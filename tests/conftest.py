"""Pytest configuration for the ManimGL test suite.

Importing :mod:`manimlib` parses ``sys.argv`` at import time (see
``manimlib/config.py``): ``initialize_manim_config()`` runs a bare
``argparse.ArgumentParser.parse_args()`` at module scope, and any argv
element ManimGL's parser doesn't recognize (``-k``, ``--cov``, pytest's
own node ids, ...) raises ``SystemExit`` during test *collection*, before
any test body runs.

conftest.py is imported before any test module, so truncating argv here
-- to just the program name, which ManimGL's parser always accepts --
makes the rest of pytest's own arguments invisible to it.
"""
from __future__ import annotations

import sys

sys.argv[:] = sys.argv[:1]
