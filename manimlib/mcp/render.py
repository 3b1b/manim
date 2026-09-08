"""Sandboxed rendering of submitted ManimGL scene code.

Runs as a **subprocess**, deliberately, for reasons that are not close
calls:

- ManimGL's renderer is wgpu-native (Rust behind cffi). A device-lost
  event or driver fault aborts the *process*, not a Python exception --
  in-process, that would take the MCP server down with it.
- Submitted ``construct()`` code is arbitrary: ``while True:`` is
  unkillable in-process, and there is no reliable cross-platform way to
  interrupt a running Python thread.
- ``manimlib.extract_scene.get_scenes_to_render`` calls
  ``prompt_user_for_choice``, which blocks on ``input()``, when the
  requested scene name doesn't match anything in the file. In-process,
  ``sys.stdin`` *is* the MCP server's own protocol pipe.
- ``manim_config`` is a module-level singleton that every ``Scene``
  merges its configuration from, so concurrent in-process renders at
  different settings would race on shared state.

The functions here are ``async`` because they drive subprocesses with
``anyio``, which is naturally asynchronous -- not because it would
otherwise block the server. (Verified against the installed ``mcp``
2.2.0: its tool dispatcher runs a synchronous tool function via
``anyio.to_thread.run_sync``, so a blocking call would only cost a
worker thread, not freeze the server -- but subprocess control is a
better fit for ``async`` regardless, and it composes with
``anyio.move_on_after`` for the timeout below.)
"""
from __future__ import annotations

import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import anyio

_STEM_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

# Flags that must never be passed to the child process, and why.
#   -o / --finder  force write_file=True *and* open a viewer/file browser
#   -e             drops into an interactive IPython shell
#   -p             pauses on every Scene.wait() for a live audience
#   -a             renders every scene in the file, not just the one asked for
#   -f             forces full-screen window mode
#   --prerun       does a full extra render pass first, to count frames
#   --uhd          4K: far more than we ever want to return to a model
_FORBIDDEN_FLAGS = {"-o", "--finder", "-e", "--embed", "-p", "--presenter_mode",
                     "-a", "--write_all", "-f", "--full_screen", "--prerun", "--uhd"}


class RenderTimeout(RuntimeError):
    """Raised when the render subprocess exceeds its timeout and is killed."""


class RenderFailed(RuntimeError):
    """Raised when the render subprocess exits non-zero.

    Carries both of the child's streams. This matters because manimlib
    doesn't consistently pick one: a ``LatexError`` (the LaTeX log,
    normally the most actionable single thing to hand back) goes to
    stderr, but the version banner and, notably, the "no scene named X
    found, did you mean: ..." prompt printed when ``scene_name`` doesn't
    match anything in the file (confirmed empirically -- this is also
    where ``prompt_user_for_choice``'s ``input()`` prompt would appear,
    which is why the subprocess is spawned with ``stdin=DEVNULL``: it
    turns what would hang into a fast ``EOFError`` instead) both go to
    stdout.
    """

    def __init__(self, message: str, stderr: str, returncode: int, stdout: str = "") -> None:
        super().__init__(message)
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


@dataclass(frozen=True)
class RenderRequest:
    code: str
    scene_name: str
    output: str = "png"  # "png" or "video"
    stem: str = "render"


def build_argv(request: RenderRequest, scene_path: Path, out_dir: Path) -> list[str]:
    """Build the ``python -m manimlib`` argv for a render request.

    A pure function -- no filesystem or process access -- so it (and
    :func:`expected_output_path`) can be tested byte-for-byte without a
    GPU or manimlib installed.

    Uses ``[sys.executable, "-m", "manimlib", ...]`` rather than the
    ``manimgl`` console script: guarantees the same interpreter and
    virtualenv, needs no ``PATH`` entry, works from an uninstalled
    checkout, and avoids the Windows ``.exe`` shim. ``manimlib/__main__.py``
    has the ``if __name__ == "__main__":`` guard this relies on.
    """
    if not _STEM_RE.match(request.stem):
        raise ValueError(
            f"Invalid render stem {request.stem!r}: must match {_STEM_RE.pattern}. "
            "In particular, no dots -- manimlib builds the output path with "
            "Path.with_suffix(), which replaces everything after the last dot."
        )

    argv = [sys.executable, "-m", "manimlib", str(scene_path), request.scene_name]
    if request.output == "video":
        # -w alone -> MP4 of the full animation.
        argv += ["-w", "-l"]
    else:
        # -s -w together -> PNG of just the last frame (no ffmpeg needed).
        # -s must never be passed without -w: show_in_window = not
        # write_file, so -s alone would try to open a window.
        argv += ["-s", "-w", "-l"]
    argv += ["--file_name", request.stem, "--video_dir", str(out_dir)]

    if _FORBIDDEN_FLAGS & set(argv):
        raise AssertionError("a forbidden flag leaked into the render argv")  # pragma: no cover
    return argv


def expected_output_path(request: RenderRequest, out_dir: Path) -> Path:
    """The path manimlib will write to, given the same request and out_dir.

    Mirrors ``manimlib/scene/scene_file_writer.py``: the file name is the
    given ``--file_name`` with the extension replaced (``with_suffix``,
    which is why dotted stems are rejected in :func:`build_argv`) by
    ``.png`` for a still or ``.mp4`` for a movie.
    """
    ext = ".mp4" if request.output == "video" else ".png"
    return out_dir / (request.stem + ext)


def _kill_tree(pid: int) -> None:
    """Kill a process and its children.

    Necessary, not defensive: the render child spawns ``ffmpeg`` (for
    video output) and potentially ``latex``/``dvisvgm`` (for Tex/TexText
    mobjects). Killing only the top process on timeout can leave ffmpeg
    holding the output file open, which then makes cleanup of the
    sandbox directory raise ``PermissionError`` on Windows.
    """
    if sys.platform == "win32":
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(pid)],
            capture_output=True,
            check=False,
        )
    else:
        try:
            pgid = os.getpgid(pid)
            os.killpg(pgid, signal.SIGKILL)
        except ProcessLookupError:
            pass  # pragma: no cover - process already gone


@dataclass
class _SubprocessResult:
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool


async def _run_subprocess(
    argv: list[str],
    timeout: float,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
) -> _SubprocessResult:
    """Run ``argv`` to completion (or until ``timeout``), capturing both streams.

    Shared by :func:`render_scene` and :func:`probe_gpu` -- both need
    the same tree-kill-on-timeout handling, since both may spawn a
    process that itself spawns children (ffmpeg/latex for a render; the
    wgpu/graphics driver stack for a GPU probe).
    """
    spawn_kwargs: dict[str, object] = {}
    if sys.platform == "win32":
        spawn_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        spawn_kwargs["start_new_session"] = True

    proc = await anyio.open_process(
        argv,
        cwd=cwd,
        stdin=subprocess.DEVNULL,
        env=env,
        **spawn_kwargs,
    )

    stdout_chunks: list[bytes] = []
    stderr_chunks: list[bytes] = []

    async def _drain(stream, sink: list[bytes]) -> None:
        if stream is None:
            return
        async for chunk in stream:
            sink.append(chunk)

    timed_out = False
    with anyio.move_on_after(timeout) as scope:
        async with anyio.create_task_group() as tg:
            tg.start_soon(_drain, proc.stdout, stdout_chunks)
            tg.start_soon(_drain, proc.stderr, stderr_chunks)
            await proc.wait()
    if scope.cancel_called:
        timed_out = True
        _kill_tree(proc.pid)
        await proc.wait()

    return _SubprocessResult(
        returncode=proc.returncode if proc.returncode is not None else -1,
        stdout=b"".join(stdout_chunks).decode("utf-8", errors="replace"),
        stderr=b"".join(stderr_chunks).decode("utf-8", errors="replace"),
        timed_out=timed_out,
    )


async def probe_gpu(timeout: float = 20.0) -> dict[str, object]:
    """Check whether a wgpu adapter can be created, without risking the server.

    Run in a subprocess for the same reason :func:`render_scene` does:
    a driver fault during adapter/device creation aborts the *process*,
    not just the call, so ``check_environment`` diagnosing a broken GPU
    setup must not itself be able to take the MCP server down.
    """
    script = (
        "import sys\n"
        "try:\n"
        "    import wgpu\n"
        "    adapter = wgpu.gpu.request_adapter_sync(power_preference='high-performance')\n"
        "    print(getattr(adapter, 'summary', str(adapter)))\n"
        "except Exception as exc:\n"
        "    print(f'{type(exc).__name__}: {exc}', file=sys.stderr)\n"
        "    sys.exit(1)\n"
    )
    try:
        result = await _run_subprocess([sys.executable, "-c", script], timeout=timeout)
    except OSError as exc:
        return {"available": False, "detail": f"{type(exc).__name__}: {exc}"}

    if result.timed_out:
        return {"available": False, "detail": f"GPU probe exceeded {timeout}s and was killed."}
    if result.returncode == 0:
        return {"available": True, "detail": result.stdout.strip()}
    return {"available": False, "detail": result.stderr.strip()}


async def render_scene(
    code: str,
    scene_name: str,
    output: str = "png",
    timeout: float = 120.0,
    config_file: str | None = None,
) -> dict[str, object]:
    """Render submitted ManimGL scene code in a sandboxed subprocess.

    The sandbox directory is also the child's working directory. This
    is load-bearing, not incidental: ``manimlib.config`` reads
    ``custom_config.yml`` from the current working directory, and a
    user's own project config (``mirror_module_path: True``, a
    different ``resolution``, ``text.font``, ``tex.template``, ...)
    would otherwise silently change how the render behaves and where
    its output actually lands, relative to what ``--video_dir`` alone
    would predict. Pass ``config_file`` to opt back in to a specific
    config (e.g. one with a needed Tex template) without inheriting the
    rest of the ambient CWD's configuration.

    Returns:
        A dict with either ``{"kind": "png", "data": bytes, ...}`` (read
        into memory -- the sandbox is deleted before returning) or
        ``{"kind": "video", "path": str, ...}`` (moved to a persistent
        cache directory first, for the same reason), plus ``stderr_tail``
        for diagnostics either way.

    Raises:
        ValueError: for a malformed ``output`` or render stem.
        RenderTimeout: if the child is still running after ``timeout``
            seconds; it and its children are killed first.
        RenderFailed: if the child exits non-zero.
    """
    if output not in ("png", "video"):
        raise ValueError(f"output must be 'png' or 'video', got {output!r}")

    sandbox = Path(tempfile.mkdtemp(prefix="manimgl-mcp-"))
    try:
        scene_path = sandbox / "scene.py"
        scene_path.write_text(code, encoding="utf-8")
        out_dir = sandbox / "out"

        request = RenderRequest(code=code, scene_name=scene_name, output=output)
        argv = build_argv(request, scene_path, out_dir)
        if config_file:
            argv += ["--config_file", config_file]

        env = dict(os.environ)
        env["PYTHONUNBUFFERED"] = "1"
        env.setdefault("MPLBACKEND", "Agg")

        result = await _run_subprocess(argv, timeout=timeout, cwd=str(sandbox), env=env)
        stderr = result.stderr
        stdout = result.stdout

        if result.timed_out:
            raise RenderTimeout(
                f"Render of {scene_name!r} exceeded {timeout}s and was killed. "
                f"stderr so far: {stderr[-2000:]}"
            )

        if result.returncode != 0:
            raise RenderFailed(
                f"Render of {scene_name!r} exited with code {result.returncode}.",
                stderr=stderr,
                stdout=stdout,
                returncode=result.returncode,
            )

        output_path = expected_output_path(request, out_dir)
        if not output_path.is_file():
            raise RenderFailed(
                f"Render exited 0 but expected output was not found at "
                f"{output_path}. This usually means the scene name "
                f"{scene_name!r} did not match any Scene subclass in the "
                "submitted code.",
                stderr=stderr,
                stdout=stdout,
                returncode=0,
            )

        if output == "png":
            data = output_path.read_bytes()
            return {"kind": "png", "data": data, "stderr_tail": stderr[-500:]}

        cache_dir = _persistent_cache_dir()
        dest_dir = cache_dir / os.urandom(4).hex()
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / output_path.name
        shutil.move(str(output_path), str(dest_path))
        _prune_cache(cache_dir)
        return {"kind": "video", "path": str(dest_path), "stderr_tail": stderr[-500:]}
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)


def _persistent_cache_dir() -> Path:
    try:
        import appdirs

        base = Path(appdirs.user_cache_dir("manimgl-mcp"))
    except ImportError:  # pragma: no cover - appdirs ships with the mcp extra
        base = Path(tempfile.gettempdir()) / "manimgl-mcp-cache"
    renders = base / "renders"
    renders.mkdir(parents=True, exist_ok=True)
    return renders


def _prune_cache(cache_dir: Path, max_entries: int = 50) -> None:
    """Delete the oldest render directories past ``max_entries``.

    Rendered videos are moved here (never deleted immediately, unlike
    PNGs which are read into memory and returned inline) since a video
    can't be returned inline -- but nothing else ever cleans this
    directory up, so it needs its own bound.
    """
    entries = sorted(cache_dir.iterdir(), key=lambda p: p.stat().st_mtime)
    for stale in entries[:-max_entries] if len(entries) > max_entries else []:
        shutil.rmtree(stale, ignore_errors=True)
