"""Tests for manimlib.mcp.render.

Tier 0 (below): pure functions (build_argv, expected_output_path) --
no filesystem, no subprocess, no manimlib, no GPU.

Tier 2 (bottom of file): actual sandboxed renders. Opt-in via
MANIMGL_MCP_GPU_TESTS=1 -- these need a working manimgl install, a
usable wgpu adapter, and take real wall-clock time.
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

import pytest

from manimlib.mcp.render import RenderRequest, _FORBIDDEN_FLAGS, build_argv, expected_output_path

SCENE_PATH = Path("/sandbox/scene.py")
OUT_DIR = Path("/sandbox/out")


def test_png_request_uses_s_and_w():
    request = RenderRequest(code="", scene_name="Demo", output="png", stem="render")
    argv = build_argv(request, SCENE_PATH, OUT_DIR)
    assert "-s" in argv
    assert "-w" in argv


def test_video_request_uses_w_without_s():
    request = RenderRequest(code="", scene_name="Demo", output="video", stem="render")
    argv = build_argv(request, SCENE_PATH, OUT_DIR)
    assert "-w" in argv
    assert "-s" not in argv, "show_in_window = not write_file; -s without -w would open a window"


def test_forbidden_flags_never_appear():
    for output in ("png", "video"):
        request = RenderRequest(code="", scene_name="Demo", output=output, stem="render")
        argv = build_argv(request, SCENE_PATH, OUT_DIR)
        assert not (_FORBIDDEN_FLAGS & set(argv)), f"forbidden flag leaked into {output} argv"


def test_scene_name_and_paths_are_passed_through():
    request = RenderRequest(code="", scene_name="MyScene", output="png", stem="render")
    argv = build_argv(request, SCENE_PATH, OUT_DIR)
    assert str(SCENE_PATH) in argv
    assert "MyScene" in argv
    assert str(OUT_DIR) in argv


def test_dotted_stem_is_rejected():
    """manimlib builds the output path with Path.with_suffix(), which replaces
    everything after the LAST dot -- 'my.scene.v1' would become 'my.scene.png'."""
    request = RenderRequest(code="", scene_name="Demo", stem="my.scene.v1")
    with pytest.raises(ValueError, match="dots"):
        build_argv(request, SCENE_PATH, OUT_DIR)


def test_invalid_stem_characters_are_rejected():
    request = RenderRequest(code="", scene_name="Demo", stem="../../etc/passwd")
    with pytest.raises(ValueError):
        build_argv(request, SCENE_PATH, OUT_DIR)


def test_expected_output_path_png():
    request = RenderRequest(code="", scene_name="Demo", output="png", stem="render")
    assert expected_output_path(request, OUT_DIR) == OUT_DIR / "render.png"


def test_expected_output_path_video():
    request = RenderRequest(code="", scene_name="Demo", output="video", stem="render")
    assert expected_output_path(request, OUT_DIR) == OUT_DIR / "render.mp4"


def test_uses_sys_executable_module_invocation():
    """[sys.executable, '-m', 'manimlib', ...] -- not the manimgl console script."""
    import sys

    request = RenderRequest(code="", scene_name="Demo")
    argv = build_argv(request, SCENE_PATH, OUT_DIR)
    assert argv[0] == sys.executable
    assert argv[1:3] == ["-m", "manimlib"]


# --- Tier 2: real sandboxed renders, opt-in ---------------------------------

pytestmark_gpu = pytest.mark.skipif(
    os.environ.get("MANIMGL_MCP_GPU_TESTS") != "1",
    reason="set MANIMGL_MCP_GPU_TESTS=1 to run real renders (needs manimgl + a GPU)",
)


@pytestmark_gpu
def test_render_scene_produces_a_png():
    pytest.importorskip("manimlib")
    from manimlib.mcp.render import render_scene

    code = (
        "from manimlib import *\n\n"
        "class Demo(Scene):\n"
        "    def construct(self):\n"
        "        self.add(Circle())\n"
    )
    result = asyncio.run(render_scene(code, "Demo", output="png", timeout=90))
    assert result["kind"] == "png"
    assert result["data"][:8] == b"\x89PNG\r\n\x1a\n"


@pytestmark_gpu
def test_render_scene_bad_syntax_fails_without_hanging():
    pytest.importorskip("manimlib")
    from manimlib.mcp.render import RenderFailed, render_scene

    with pytest.raises(RenderFailed):
        asyncio.run(render_scene("def f(:", "Demo", output="png", timeout=30))


@pytestmark_gpu
def test_render_scene_infinite_loop_is_killed_by_timeout():
    pytest.importorskip("manimlib")
    from manimlib.mcp.render import RenderTimeout, render_scene

    code = (
        "from manimlib import *\n\n"
        "class Hang(Scene):\n"
        "    def construct(self):\n"
        "        while True:\n"
        "            pass\n"
    )
    with pytest.raises(RenderTimeout):
        asyncio.run(render_scene(code, "Hang", output="png", timeout=5))


@pytestmark_gpu
def test_render_scene_wrong_name_surfaces_did_you_mean_without_hanging():
    """Exercises the extract_scene.py prompt_user_for_choice landmine: with
    stdin=DEVNULL, input() raises EOFError immediately instead of hanging."""
    pytest.importorskip("manimlib")
    from manimlib.mcp.render import RenderFailed, render_scene

    code = (
        "from manimlib import *\n\n"
        "class Demo(Scene):\n"
        "    def construct(self):\n"
        "        self.add(Circle())\n\n"
        "class Other(Scene):\n"
        "    def construct(self):\n"
        "        self.add(Square())\n"
    )
    with pytest.raises(RenderFailed) as excinfo:
        asyncio.run(render_scene(code, "DoesNotExist", output="png", timeout=30))
    # manimlib's "no scene named X found, did you mean" message goes to
    # stdout, not stderr -- both must be surfaced.
    assert "DoesNotExist" in excinfo.value.stdout or "Demo" in excinfo.value.stdout


@pytestmark_gpu
def test_probe_gpu_reports_a_result_without_crashing():
    pytest.importorskip("manimlib")
    from manimlib.mcp.render import probe_gpu

    result = asyncio.run(probe_gpu())
    assert "available" in result
    assert isinstance(result["available"], bool)
