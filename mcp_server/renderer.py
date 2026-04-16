"""
Subprocess-based ManimGL scene renderer.

All scene execution happens in an isolated subprocess to prevent
bad user code from crashing the MCP server.
"""
from __future__ import annotations

import base64
import os
import subprocess
import tempfile
from pathlib import Path

RENDER_TIMEOUT = 120  # seconds
OUTPUT_DIR = Path(tempfile.gettempdir()) / "manimgl_mcp"
# Project root — needed so `uv run` can find pyproject.toml
PROJECT_ROOT = Path(__file__).resolve().parent.parent

QUALITY_FLAGS = {
    "low": ["-l"],
    "medium": ["-m"],
    "high": ["--hd"],
    "4k": ["--uhd"],
}


def _ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def _find_output_file(output_dir: Path, fmt: str) -> Path | None:
    """Walk the output directory tree for the most recent file matching fmt."""
    extensions = {
        "mp4": {".mp4"},
        "gif": {".gif"},
        "png": {".png"},
    }
    valid_exts = extensions.get(fmt, {f".{fmt}"})
    candidates = [
        f for f in output_dir.rglob("*")
        if f.suffix.lower() in valid_exts and f.is_file()
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _image_to_base64(path: Path) -> str:
    """Read an image file and return its base64-encoded content."""
    data = path.read_bytes()
    return base64.b64encode(data).decode("ascii")


def _write_temp_scene(code: str) -> Path:
    """Write scene code to a temp .py file and return its path."""
    output_dir = _ensure_output_dir()
    fd, path = tempfile.mkstemp(suffix=".py", dir=output_dir, prefix="scene_")
    with os.fdopen(fd, "w") as f:
        # Ensure manimlib is importable
        f.write("from manimlib import *\n\n")
        f.write(code)
    return Path(path)


def _build_command(
    scene_file: Path,
    scene_name: str | None,
    quality: str,
    fmt: str,
    output_dir: Path,
) -> list[str]:
    """Build the uv run manimgl command."""
    cmd = ["uv", "run", "--extra", "mcp", "manimgl"]
    cmd.append(str(scene_file))

    if scene_name:
        cmd.append(scene_name)

    # Write to file (not window)
    cmd.append("-w")

    # Direct output to our temp directory
    cmd.extend(["--video_dir", str(output_dir)])

    # Quality
    cmd.extend(QUALITY_FLAGS.get(quality, ["-m"]))

    # For png output, skip animations and save last frame
    if fmt == "png":
        cmd.append("-s")

    return cmd


def render_scene(
    code: str,
    scene_name: str | None = None,
    quality: str = "medium",
    fmt: str = "mp4",
) -> dict:
    """
    Render a ManimGL scene from code.

    Returns a dict with file_path, format, and optionally base64_image.
    """
    output_dir = _ensure_output_dir()
    scene_file = _write_temp_scene(code)

    try:
        cmd = _build_command(scene_file, scene_name, quality, fmt, output_dir)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=RENDER_TIMEOUT,
            cwd=str(PROJECT_ROOT),
        )

        if result.returncode != 0:
            return {
                "success": False,
                "error": result.stderr.strip() or result.stdout.strip(),
            }

        # Find the output file
        search_fmt = "png" if fmt == "png" else fmt
        output_file = _find_output_file(output_dir, search_fmt)

        if output_file is None:
            return {
                "success": False,
                "error": "Render completed but no output file found.",
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
            }

        response: dict = {
            "success": True,
            "file_path": str(output_file),
            "format": fmt,
        }

        # Include base64 for images (small enough for inline transport)
        if fmt == "png":
            response["base64_image"] = _image_to_base64(output_file)

        return response

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Render timed out after {RENDER_TIMEOUT} seconds.",
        }
    finally:
        # Clean up the temp scene file
        scene_file.unlink(missing_ok=True)


def render_frame(
    code: str,
    scene_name: str | None = None,
    quality: str = "low",
) -> dict:
    """
    Render a single frame (last frame) of a scene.
    Always returns base64 PNG for quick visual feedback.
    """
    return render_scene(code, scene_name, quality, fmt="png")
