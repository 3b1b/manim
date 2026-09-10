"""Entry point: ``python -m manimlib.mcp``.

Must be invoked with **no additional command-line arguments**. By the
time this module's code runs, Python has already imported the parent
``manimlib`` package (``__init__.py`` runs before any submodule, always)
-- which means ``manimlib/config.py``'s import-time
``argparse.ArgumentParser.parse_args()`` has already seen this
process's ``sys.argv``. Verified empirically: running
``python -m manimlib.mcp`` with zero extra arguments leaves
``sys.argv == ["-m"]`` during that parse, which ManimGL's parser
accepts (its positional arguments are optional); any additional
argument leaks into that same parse and raises ``SystemExit`` before
this file is even reached. See ``manimlib/mcp/_bootstrap.py`` for the
full explanation, and configure this server via the ``MANIMGL_MCP_*``
environment variables documented in
``docs/source/documentation/mcp.rst`` instead of flags.
"""
from __future__ import annotations

import sys

from manimlib.mcp._bootstrap import guard_stdout, repair_logging


def main() -> int:
    # manimlib's own logging/stdout side effects have already happened
    # (see the module docstring) -- repair them unconditionally, here,
    # rather than relying on some tool call to trigger it later; a
    # session that never happens to call a manimlib-touching tool would
    # otherwise never get the logging fix.
    repair_logging()
    guard_stdout()

    from manimlib.mcp.server import build_server

    build_server().run()  # no transport argument => stdio
    return 0


if __name__ == "__main__":
    sys.exit(main())
