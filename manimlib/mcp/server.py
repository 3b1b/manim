"""The MCP tool surface for ManimGL.

Assembles the tools defined across :mod:`manimlib.mcp.introspect`,
:mod:`manimlib.mcp.examples`, :mod:`manimlib.mcp.validate`, and
:mod:`manimlib.mcp.render` into one ``MCPServer``. See
``manimlib/mcp/__main__.py`` for how this gets run over stdio.
"""
from __future__ import annotations

import os
import shutil
import sys
from typing import Any

from mcp.server.mcpserver import Image, MCPServer

from manimlib.mcp import examples as _examples
from manimlib.mcp import render as _render
from manimlib.mcp import validate as _validate
from manimlib.mcp._bootstrap import ManimlibUnavailable, import_manimlib

_INSTRUCTIONS = """\
This server describes ManimGL (github.com/3b1b/manim), NOT ManimCommunity
(the "manim" PyPI package most Manim tutorials and training data describe).
The two libraries share a name and a common ancestor but have diverged:
ManimCommunity's `Create`, `MathTex`, `config`, `MovingCameraScene`, and
the `-ql`/`-qh` CLI flags do not exist here. Scene files start with
`from manimlib import *`, not `from manim import *`.

Before writing ManimGL code, prefer `search_examples` for a known-good
scene to adapt, and `get_class_signature` over guessing a constructor's
keyword arguments -- most ManimGL mobjects take almost all of their real
configuration through kwargs forwarded up their base classes, which
guessing gets wrong more often than not. Run `validate_scene` on a draft
before rendering it: it is instant, needs no GPU, and catches
ManimCommunity-flavored mistakes by name. `render_scene` (when enabled)
renders a last-frame PNG you can inspect directly for layout problems --
prefer it whenever you're unsure whether a scene actually looks right.
"""

_render_semaphore: Any = None  # created lazily, needs a running event loop


def _get_render_semaphore():
    global _render_semaphore
    if _render_semaphore is None:
        import anyio

        max_concurrent = int(os.environ.get("MANIMGL_MCP_MAX_CONCURRENT", "1"))
        _render_semaphore = anyio.Semaphore(max_concurrent)
    return _render_semaphore


def _known_names_or_none() -> set[str] | None:
    try:
        from manimlib.mcp.introspect import public_names

        return public_names()
    except ManimlibUnavailable:
        return None


def build_server() -> MCPServer:
    mcp: MCPServer = MCPServer(name="manimgl", instructions=_INSTRUCTIONS)

    @mcp.tool()
    def list_manim_classes(kind: str = "all", query: str = "") -> dict[str, Any]:
        """List ManimGL classes, optionally filtered by kind ('mobject'/'animation'/'scene') and a name substring."""
        try:
            from manimlib.mcp.introspect import list_classes

            return {"classes": list_classes(kind=kind, query=query)}
        except ManimlibUnavailable as exc:
            return {"error": str(exc)}

    @mcp.tool()
    def get_class_signature(name: str) -> dict[str, Any]:
        """Get a ManimGL class's real constructor signature (MRO-flattened), docstring, and inline parameter comments."""
        try:
            from manimlib.mcp.introspect import describe_class

            return describe_class(name)
        except ManimlibUnavailable as exc:
            return {"error": str(exc)}

    @mcp.tool()
    def list_scene_methods(name: str = "Scene") -> dict[str, Any]:
        """List the public methods available on a ManimGL class (e.g. the verbs on Scene or Mobject) with signatures."""
        try:
            from manimlib.mcp.introspect import list_methods

            return list_methods(name)
        except ManimlibUnavailable as exc:
            return {"error": str(exc)}

    @mcp.tool()
    def get_manim_constants(category: str = "all") -> dict[str, Any]:
        """Get ManimGL's real configured constants (colors, vectors, angles, sizes), grouped by category."""
        try:
            from manimlib.mcp.introspect import get_constants

            return {"constants": get_constants(category=category)}
        except ManimlibUnavailable as exc:
            return {"error": str(exc)}

    @mcp.tool()
    def search_examples(query: str = "", limit: int = 10) -> dict[str, Any]:
        """Search known-good ManimGL example scenes by name and source substring; empty query lists the corpus."""
        return {"examples": _examples.search_examples(query=query, limit=limit)}

    @mcp.tool()
    def validate_scene(code: str) -> dict[str, Any]:
        """Statically check submitted ManimGL scene code for syntax errors and unknown/ManimCommunity-only names, with no GPU required."""
        return _validate.validate_scene(code, known_names=_known_names_or_none())

    @mcp.tool()
    def check_environment() -> dict[str, Any]:
        """Report whether rendering will actually work here: manimgl version, ffmpeg/latex/dvisvgm availability, and a GPU probe."""
        info: dict[str, Any] = {
            "render_enabled": os.environ.get("MANIMGL_MCP_ENABLE_RENDER") == "1",
            "ffmpeg": shutil.which("ffmpeg"),
            "latex": shutil.which("latex"),
            "dvisvgm": shutil.which("dvisvgm"),
            "platform": sys.platform,
        }
        try:
            manimlib = import_manimlib()
            info["manimlib_version"] = getattr(manimlib, "__version__", "unknown")
            info["configured_font"] = manimlib.manim_config.text.font
            info["configured_resolution"] = manimlib.manim_config.camera.resolution
            info["output_directory"] = manimlib.manim_config.directories.output
        except ManimlibUnavailable as exc:
            info["manimlib_error"] = str(exc)
        return info

    @mcp.tool()
    async def probe_gpu() -> dict[str, Any]:
        """Check whether a wgpu graphics adapter can be created, without risking this server (runs in a subprocess)."""
        return await _render.probe_gpu()

    @mcp.tool()
    async def render_scene(
        code: str,
        scene_name: str,
        output: str = "png",
        timeout: float = 120.0,
    ) -> Image | dict[str, Any]:
        """Render submitted ManimGL scene code to a PNG (default, inline) or MP4 (path) in a sandboxed subprocess.

        Disabled by default: set the MANIMGL_MCP_ENABLE_RENDER=1
        environment variable to enable it. This executes arbitrary
        submitted Python (via a subprocess with no stdin, a fresh
        working directory, and a timeout, but with the server's own
        filesystem and network privileges otherwise) -- do not enable
        it for a server any untrusted client can reach.
        """
        if os.environ.get("MANIMGL_MCP_ENABLE_RENDER") != "1":
            return {
                "error": "Rendering is disabled. Set MANIMGL_MCP_ENABLE_RENDER=1 to "
                "enable it. It executes submitted code in a subprocess with the "
                "server's own filesystem and network privileges; only enable this "
                "for a trusted, local client."
            }
        async with _get_render_semaphore():
            try:
                result = await _render.render_scene(
                    code, scene_name, output=output, timeout=timeout
                )
            except (_render.RenderTimeout, _render.RenderFailed) as exc:
                payload: dict[str, Any] = {"error": str(exc)}
                if isinstance(exc, _render.RenderFailed):
                    # manimlib doesn't consistently pick a stream: a
                    # LatexError goes to stderr, but the "no scene named
                    # X found, did you mean: ..." message goes to
                    # stdout (verified empirically) -- surface both.
                    payload["stdout"] = exc.stdout
                    payload["stderr"] = exc.stderr
                    payload["returncode"] = exc.returncode
                return payload
            except ValueError as exc:
                return {"error": str(exc)}

        if result["kind"] == "png":
            return Image(data=result["data"], format="png")
        return {"kind": "video", "path": result["path"], "stderr_tail": result["stderr_tail"]}

    return mcp
