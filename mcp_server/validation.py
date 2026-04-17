"""
Scene code validation without rendering.

Catches syntax errors and basic import/name errors by compiling
and executing the code in a namespace with manimlib pre-imported.
"""
from __future__ import annotations

import traceback


def validate_scene_code(code: str) -> dict:
    """
    Validate scene code without rendering.

    Returns {"valid": True} or {"valid": False, "error": "...", "line": N}.
    """
    full_code = "from manimlib import *\n\n" + code

    # Phase 1: Syntax check via compile()
    try:
        compiled = compile(full_code, "<scene>", "exec")
    except SyntaxError as e:
        # Adjust line number to account for the import we prepended
        line = (e.lineno or 0) - 2
        return {
            "valid": False,
            "error": f"SyntaxError: {e.msg}",
            "line": max(line, 1),
        }

    # Phase 2: Execute to catch NameError, ImportError, etc.
    # This defines the classes but does NOT call construct() or run().
    namespace: dict = {}
    try:
        exec(compiled, namespace)
    except Exception as e:
        # Try to extract line number from traceback
        tb = traceback.extract_tb(e.__traceback__)
        line = None
        for frame in reversed(tb):
            if frame.filename == "<scene>":
                line = max((frame.lineno or 0) - 2, 1)
                break

        return {
            "valid": False,
            "error": f"{type(e).__name__}: {e}",
            "line": line,
        }

    return {"valid": True}
