"""Protocol-level tests for the MCP server entry point.

These drive the *real* ``python -m manimlib.mcp`` subprocess over its
actual stdio transport -- the only way to genuinely prove the stdout-
cleanliness fix in ``manimlib/mcp/_bootstrap.py``, since an in-process
test would bypass the exact code path (module-level side effects from
the forced ``manimlib`` import, then ``repair_logging()``,
``guard_stdout()``, then the SDK's own stdio transport) that the fix
targets.

(The plan sketched an additional in-process protocol test using
``mcp.shared.memory.create_connected_server_and_client_session``; that
helper does not exist in the installed ``mcp`` 2.2.0 -- it was renamed/
restructured to ``create_client_server_memory_streams``, a lower-level
primitive. The subprocess-based tests here cover the same ground
end-to-end and are what actually exercises the stdio guard, so that
in-process variant was dropped rather than reimplemented against the
new, lower-level API under a fixed time budget.)

Requires manimlib to be importable (the server can't even start
otherwise, given its package layout -- see ``_bootstrap.py``'s module
docstring), so every test here skips cleanly without it.
"""
from __future__ import annotations

import json
import queue
import subprocess
import sys
import threading

import pytest

pytest.importorskip("manimlib")

_STARTUP_TIMEOUT = 15.0
_CALL_TIMEOUT = 15.0


class _StdioSession:
    """Minimal JSON-RPC-over-stdio client for driving the real subprocess.

    Reads stdout on a background thread into a queue: on Windows,
    pipe file objects support neither ``select`` nor a non-blocking
    ``readline``, so a genuinely enforced timeout (a hung server must
    fail *this test*, not freeze the whole suite) needs a thread you
    can abandon rather than a blocking call you can't interrupt.
    """

    def __init__(self) -> None:
        self.proc = subprocess.Popen(
            [sys.executable, "-m", "manimlib.mcp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self._lines: queue.Queue[str] = queue.Queue()
        self._reader = threading.Thread(target=self._pump_stdout, daemon=True)
        self._reader.start()

    def _pump_stdout(self) -> None:
        assert self.proc.stdout is not None
        for line in self.proc.stdout:
            self._lines.put(line)

    def send(self, message: dict) -> None:
        assert self.proc.stdin is not None
        self.proc.stdin.write(json.dumps(message) + "\n")
        self.proc.stdin.flush()

    def read_line(self, timeout: float = _CALL_TIMEOUT) -> str:
        try:
            return self._lines.get(timeout=timeout)
        except queue.Empty:
            raise TimeoutError(
                f"no response from manimlib.mcp subprocess within {timeout}s"
            ) from None

    def initialize(self) -> dict:
        self.send({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "pytest", "version": "1"},
            },
        })
        response = json.loads(self.read_line(timeout=_STARTUP_TIMEOUT))
        self.send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return response

    def call_tool(self, name: str, arguments: dict) -> dict:
        self.send({
            "jsonrpc": "2.0",
            "id": id(arguments) % 100000 + 2,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        })
        return json.loads(self.read_line())

    def list_tools(self) -> list[str]:
        self.send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        response = json.loads(self.read_line())
        return sorted(t["name"] for t in response["result"]["tools"])

    def close(self) -> tuple[str, str]:
        """Terminate the subprocess and return any output nobody has read yet.

        Only stderr is read here via ``communicate()`` -- stdout is
        exclusively owned by the background reader thread for this
        session's whole lifetime, so reading it again here would race
        that thread for the same pipe.
        """
        self.proc.terminate()
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait(timeout=5)
        self._reader.join(timeout=2)

        leftover_stdout = []
        while True:
            try:
                leftover_stdout.append(self._lines.get_nowait())
            except queue.Empty:
                break

        stderr = self.proc.stderr.read() if self.proc.stderr else ""
        return "".join(leftover_stdout), stderr


@pytest.fixture
def session():
    s = _StdioSession()
    yield s
    s.close()


def test_initialize_response_is_the_only_stdout_output_so_far(session):
    """The core stdout-cleanliness assertion: the very first bytes on stdout
    must be the JSON-RPC response, not a `ManimGL vX.Y.Z` banner or a rich-
    formatted log line -- both of which manimlib prints/logs at import time
    absent the repair_logging()/guard_stdout() fix."""
    response = session.initialize()
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 1
    assert "result" in response
    assert response["result"]["serverInfo"]["name"] == "manimgl"


def test_all_expected_tools_are_registered(session):
    session.initialize()
    tools = session.list_tools()
    assert tools == sorted([
        "check_environment",
        "get_class_signature",
        "get_manim_constants",
        "list_manim_classes",
        "list_scene_methods",
        "probe_gpu",
        "render_scene",
        "search_examples",
        "validate_scene",
    ])


def test_validate_scene_over_real_stdio_flags_community_syntax(session):
    session.initialize()
    response = session.call_tool("validate_scene", {
        "code": "from manimlib import *\nclass D(Scene):\n def construct(self):\n  self.play(Create(Square()))\n"
    })
    text = response["result"]["content"][0]["text"]
    payload = json.loads(text)
    assert any(n["name"] == "Create" for n in payload["unknown_names"])


def test_search_examples_over_real_stdio_returns_results(session):
    session.initialize()
    response = session.call_tool("search_examples", {"query": "square"})
    text = response["result"]["content"][0]["text"]
    payload = json.loads(text)
    assert payload["examples"]


def test_render_scene_is_disabled_by_default(session):
    """MANIMGL_MCP_ENABLE_RENDER is unset for this subprocess -- render_scene
    must refuse rather than execute submitted code."""
    session.initialize()
    response = session.call_tool("render_scene", {
        "code": "from manimlib import *\nclass D(Scene):\n def construct(self):\n  pass\n",
        "scene_name": "D",
    })
    text = response["result"]["content"][0]["text"]
    payload = json.loads(text)
    assert "error" in payload
    assert "MANIMGL_MCP_ENABLE_RENDER" in payload["error"]


def test_session_ends_with_no_leftover_stdout_or_stderr_pollution(session):
    session.initialize()
    session.call_tool("check_environment", {})  # already reads its one response line
    out, err = session.close()
    assert out == ""
    assert err == ""
