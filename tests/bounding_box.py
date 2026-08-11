"""
That a cached bounding box still says which corner is which after a transform.

Most transforms leave the box to be worked out again from the points, but shift, scale and
stretch move the cached corners instead, there being no need to look at every point to know
where a box went. That shortcut assumes the corner which was smallest stays smallest, which a
negative factor does not: stretch(-1, dim) sends the low corner high and the high corner low,
and the box comes out inside out, get_width() of it negative and get_left() to the right of
get_right().

Nothing in the harness reads a box that closely. Dodecahedron builds a face with
stretch(-1, 2, about_point=ORIGIN) and looks right anyway, a group working its own box out
from the corners of its children with min and max, which puts an inside out one back the
right way round.

    python tests/bounding_box.py
"""
from __future__ import annotations

import sys

import numpy as np

from manimlib import ORIGIN, PI, RIGHT, Square


def box_disagrees_with_points(mobject) -> str:
    """What a box says against what the points it is meant to cover come to, or empty"""
    box = mobject.get_bounding_box()
    points = mobject.get_all_points()
    problems = []
    if not np.allclose(box[0], points.min(0), atol=1e-5):
        problems.append(f"mins {np.round(box[0], 3).tolist()} for {np.round(points.min(0), 3).tolist()}")
    if not np.allclose(box[2], points.max(0), atol=1e-5):
        problems.append(f"maxs {np.round(box[2], 3).tolist()} for {np.round(points.max(0), 3).tolist()}")
    if not np.allclose(box[1], (box[0] + box[2]) / 2, atol=1e-5):
        problems.append(f"mid {np.round(box[1], 3).tolist()} between them")
    return ", ".join(problems)


CASES = [
    ("stretch(-1, 0)", lambda: Square().stretch(-1, 0)),
    ("stretch(-2, 1) off center", lambda: Square().shift(RIGHT).stretch(-2, 1, about_point=ORIGIN)),
    # The transforms which took the shortcut already, and have to go on working
    ("shift", lambda: Square().shift(2 * RIGHT)),
    ("scale", lambda: Square().scale(3)),
    ("stretch(2, 1)", lambda: Square().stretch(2, 1)),
    # And one which does not, the box behind a rotation being worked out afresh
    ("rotate", lambda: Square().shift(2 * RIGHT).rotate(PI / 4, about_point=ORIGIN)),
]


def main() -> int:
    failures = []
    for name, build in CASES:
        problem = box_disagrees_with_points(build())
        print(f"  {name}: {problem or 'box covers its points'}")
        if problem:
            failures.append(f"{name} left the box saying {problem}")

    for failure in failures:
        print(f"  FAIL: {failure}")
    if not failures:
        print("  a moved box keeps its corners the right way round")
    return 1 if failures else 0


sys.exit(main())
