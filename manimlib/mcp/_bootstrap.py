"""Load-order shim for running an MCP server inside a ManimGL checkout.

Importing :mod:`manimlib` has side effects that are actively hostile to
a stdio-based MCP server:

1. It parses ``sys.argv`` at import time. ``manimlib/config.py`` runs
   ``initialize_manim_config()`` at module scope, which calls a bare
   ``argparse.ArgumentParser.parse_args()``; any argv element ManimGL's
   parser doesn't recognize raises ``SystemExit`` (uncaught by ManimGL's
   own ``except argparse.ArgumentError``, since ``SystemExit`` is not an
   ``ArgumentError``).
2. It configures the **root** logger to write to stdout.
   ``manimlib/logger.py`` calls ``logging.basicConfig(handlers=[
   RichHandler()])``, and ``rich``'s ``Console`` resolves its output
   stream to ``sys.stdout`` on each write. On a stdio MCP server, any
   log record -- including from the ``mcp`` package itself, since this
   is the *root* logger -- would corrupt the JSON-RPC message stream.
3. Various manimlib internals call bare ``print()`` during normal
   operation (LaTeX compilation progress, in particular), which bypass
   the logging system entirely.

The functions in this module address all three -- with one structural
caveat worth being explicit about: because this package lives *inside*
``manimlib`` (``manimlib/mcp/``), Python always imports a package's
``__init__.py`` before any of its submodules, so simply doing
``python -m manimlib.mcp`` (or even ``import manimlib.mcp._bootstrap``
on its own) has *already* triggered manimlib's own argv parsing and
logging configuration before a single line of this module's code runs.
That is unavoidable given this layout -- it is what
``manimlib/config.py:399``'s module-scope ``initialize_manim_config()``
call means in practice -- and is why ``python -m manimlib.mcp`` must be
invoked with no extra arguments (verified empirically: running any
``python -m pkg.submodule`` with extra CLI args leaks those args into
the parent package's own import-time ``sys.argv``, while zero extra
args leaves it as just ``['-m']``, which ManimGL's parser accepts).
``repair_logging()`` must therefore run unconditionally at server
startup (see ``manimlib/mcp/__main__.py``) rather than being left to
fire lazily as a side effect of some tool eventually calling
:func:`import_manimlib` -- if no tool happens to need manimlib during a
session, the stdout-polluting logging config would otherwise never get
repaired.
"""
from __future__ import annotations

import functools
import io
import logging
import sys
from types import ModuleType


class ManimlibUnavailable(RuntimeError):
    """Raised when ``import manimlib`` fails.

    Most of this package's tools (introspection, example search,
    validation) do not actually require manimlib's own runtime
    dependencies (``glfw``, ``wgpu``, ...) to be installed and working --
    only rendering does. Callers should treat this as "rendering, and
    reflection-based tools, are unavailable" rather than a fatal error
    for the whole server.
    """


def repair_logging() -> None:
    """Redirect ManimGL's logging away from stdout.

    ``manimlib/logger.py`` runs ``logging.basicConfig`` on the root
    logger with a ``RichHandler`` that writes to ``sys.stdout``, and that
    has already happened by the time this is called (it fires at
    ``import manimlib`` time). This replaces the handlers on both the
    root logger and the ``manimgl`` logger with a single
    ``StreamHandler`` bound to ``sys.stderr``.

    Binding the stream *object* (not going through ``sys.stderr`` by
    name each time) means this handler keeps writing to the real stderr
    even if :func:`guard_stdout` later reassigns ``sys.stdout``.

    Idempotent; safe to call more than once.
    """
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(message)s"))

    root = logging.getLogger()
    root.handlers[:] = [handler]

    manimgl_logger = logging.getLogger("manimgl")
    manimgl_logger.handlers[:] = [handler]
    manimgl_logger.propagate = False


def guard_stdout() -> None:
    """Redirect the real stdout file descriptor (fd 1) to stderr.

    Some manimlib internals call bare ``print()`` during normal
    operation -- LaTeX compilation progress in
    ``manimlib/utils/tex_file_writing.py``, for instance -- and
    ``manimlib/scene/scene_file_writer.py`` even reassigns
    ``sys.stdout`` outright along some code paths. A Python-level
    ``contextlib.redirect_stdout`` cannot catch writes to file
    descriptor 1 made below the Python layer, and cannot survive
    manimlib code replacing ``sys.stdout`` with a new object.

    This duplicates fd 1 aside, points fd 1 itself at fd 2 (stderr), and
    rebinds ``sys.stdout`` to a text wrapper over the duplicated
    (originally-real) descriptor. The MCP SDK's stdio transport reads
    ``sys.stdout.buffer`` when it starts, so as long as this runs
    *before* that happens, the protocol stream is unaffected while every
    other writer of fd 1 -- Python-level or not -- lands on stderr.

    In this server's actual tool design, ``mcp>=2.0``'s own
    ``stdio_server()`` transport already performs the equivalent fd-1
    diversion for the entire duration it serves, and
    :mod:`manimlib.mcp.render`'s subprocess renders capture the child's
    stdout/stderr as independent OS pipes regardless of what the
    parent's fd 1 points to -- so the concrete manimlib print()/stdout-
    reassignment hazards described above never actually fire in-process
    today. This function's value is covering the (currently print-free,
    but not permanently guaranteed to stay that way) window between
    process start and the SDK's own protection taking over, and cheap
    defense-in-depth against any future in-process manimlib usage.

    Idempotent (each call duplicates the *current* fd 1 aside, which is
    a no-op the second time since fd 1 already points at stderr's
    target); should be called once, early in ``main()``.

    No-op on platforms without ``os.dup``/``os.dup2`` (none of this
    package's supported platforms lack them; this is defensive only).
    """
    import os  # noqa: PLC0415 - only needed here, and only for dup/dup2

    if not hasattr(os, "dup") or not hasattr(os, "dup2"):
        return  # pragma: no cover - not expected on any supported platform

    real_stdout_fd = os.dup(1)
    os.dup2(2, 1)
    sys.stdout = io.TextIOWrapper(
        os.fdopen(real_stdout_fd, "wb"),
        encoding="utf-8",
        line_buffering=True,
    )


@functools.lru_cache(maxsize=1)
def import_manimlib() -> ModuleType:
    """Return the ``manimlib`` module, wrapping any import failure in a clear error.

    In this server's package layout, ``manimlib`` has necessarily
    already been imported (successfully) by the time any code in
    ``manimlib.mcp`` can run at all -- reaching this function's body
    requires having already imported ``manimlib.mcp._bootstrap``, which
    requires Python to have already imported the parent ``manimlib``
    package. So the ``sys.argv`` stubbing below is not what makes
    ``python -m manimlib.mcp`` safe (that's Python's own ``-m`` argv
    handling with zero extra arguments -- see the module docstring); it
    is defensive practice for the (in this layout, unreachable via
    manimlib.mcp's own import chain, but cheap to guard regardless)
    case of a second, independent re-import attempt.

    Memoized, so the (typically instant, cache-hit) import only happens
    once per process, and every caller gets the same clear
    :class:`ManimlibUnavailable` if it is ever actually reached.

    Returns:
        The ``manimlib`` module.

    Raises:
        ManimlibUnavailable: if ``import manimlib`` fails.
    """
    saved_argv = sys.argv[:]
    try:
        sys.argv = ["manimgl"]
        import manimlib  # noqa: PLC0415 - deliberately deferred, see module docstring
    except BaseException as exc:  # noqa: BLE001 - re-raised below with context
        raise ManimlibUnavailable(
            "Could not import manimlib. Introspection, example search, "
            "and validation tools do not require manimlib's runtime "
            "dependencies and should still work; rendering does. If you "
            "expected manimlib to be available, install it and its "
            "extras with `pip install -e \".[mcp]\"` from the repository "
            "root, and confirm its GPU dependencies (glfw, wgpu) can "
            "load in this environment. "
            f"Original error: {type(exc).__name__}: {exc}"
        ) from exc
    else:
        repair_logging()
        return manimlib
    finally:
        sys.argv = saved_argv
