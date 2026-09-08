"""Model Context Protocol (MCP) server for ManimGL.

Exposes ManimGL's real, installed API to MCP-capable LLM clients, so
that they stop guessing at ManimCommunity syntax (``Create``, ``MathTex``,
``manim -ql``, ...) which does not exist in this library. Provides
reflection over the installed classes, search over known-good example
scenes, fast static validation of submitted code, and (opt-in) sandboxed
rendering to a PNG a visual model can inspect.

Run as::

    python -m manimlib.mcp

This subpackage's ``__init__`` deliberately performs no imports of
``manimlib`` internals or the ``mcp`` package at module scope -- see
``manimlib/mcp/_bootstrap.py`` for why the import order matters when
embedding an MCP server inside ManimGL.
"""
from __future__ import annotations

__all__: list[str] = []
