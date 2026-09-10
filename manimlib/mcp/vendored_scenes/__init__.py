"""Vendored, curated ManimGL example scenes.

These files are never imported as Python modules -- ``manimlib.mcp.examples``
reads their source as text via ``ast`` so that example search works
without manimlib's runtime dependencies installed. They live in a real
package (rather than loose data files) so that ``setuptools``' normal
package-discovery ships them with the ``manimlib`` distribution
automatically, with no extra ``MANIFEST.in`` or ``package_data`` entry
required. Named distinctly from ``manimlib.mcp.examples`` (the search
module) rather than ``examples`` -- a package directory and a module of
the same name side by side in the same parent is a silent collision:
Python resolves the package and the module is simply never reachable.

Each scene here is adapted, in miniature, from scenes that ship
alongside this repository (the root ``example_scenes.py``,
``docs/example.py``, and ``docs/source/getting_started/example_scenes.rst``)
and is written to run headless (no ``self.embed()``, no network
fetches) and quickly. They should be spot-checked with a working
manimgl + GPU before being relied on as ground truth for a release --
this vendored copy was authored without one available.
"""
from __future__ import annotations
