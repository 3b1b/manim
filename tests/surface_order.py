"""
That a see through surface is drawn in an order which does not depend on how it is wound.

Blending is not commutative, so a surface which can be seen through has to be drawn back to
front. Whether it is can be checked without any reference picture: the same shape parametrized
from a different starting angle is made of the same triangles in a different order, so if the
two do not come out looking the same, the order is deciding what the picture is, and it should
not be.

The harness misses this, every see through surface among its cases being simple enough to
come out right either way.

    python tests/surface_order.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image


WORK = Path("/tmp/manimgl-surface-order")
# What antialiasing along a silhouette is allowed to differ by, two renders never agreeing
# exactly about a pixel a triangle only partly covers
TOLERANCE = 4

SCENE = '''
from manimlib import *
import numpy as np


class WoundTwoWays(ThreeDScene):
    """The same torus, wound from two different starting angles, and a mesh of loose triangles"""
    start = 0.0

    def construct(self):
        self.frame.reorient(30, 70)
        torus = Torus(
            u_range=(self.start, self.start + TAU),
            v_range=(self.start, self.start + TAU),
            r1=2.0, r2=0.8, resolution=(51, 51),
        )
        torus.set_color(BLUE_D, opacity=0.4)
        torus.set_shading(0.2, 0.2, 0.2)
        self.add(torus)


class WoundHalfwayRound(WoundTwoWays):
    start = PI


class LooseTriangles(ThreeDScene):
    """
    Records three to a triangle rather than a grid, which is what an imported mesh gives.
    Ordering these needs no grid, and it used to be given up on.
    """

    def construct(self):
        self.frame.reorient(25, 70)
        mesh = Surface()
        mesh.set_resolution((0, 0))
        corners = []
        for n in range(24):
            angle = TAU * n / 24
            step = TAU / 24
            corners += [
                np.array([2 * np.cos(angle), 2 * np.sin(angle), -1.0]),
                np.array([2 * np.cos(angle + step), 2 * np.sin(angle + step), 1.0]),
                np.array([0.4 * np.cos(angle), 0.4 * np.sin(angle), 1.0]),
            ]
        mesh.set_points(np.array(corners))
        mesh.set_color(TEAL, opacity=0.45)
        self.add(mesh)
        self.update_frame(force_draw=True)
        drawing = self.camera.renderer.drawings[mesh]
        print(f"ORDERED|{drawing.ordered}|{drawing.order_count}|{len(mesh.data) // 3}")
'''


def render(scene: str) -> tuple[np.ndarray, str]:
    result = subprocess.run(
        ["manimgl", str(WORK / "scenes.py"), scene, "-w", "-s", "-l",
         "--config_file", str(WORK / "empty.yml"), "--video_dir", str(WORK)],
        check=True, capture_output=True, text=True,
    )
    image = Image.open(WORK / f"{scene}.png").convert("RGB")
    return np.asarray(image, dtype=int), result.stdout


def main() -> int:
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "scenes.py").write_text(SCENE)
    (WORK / "empty.yml").write_text("")

    failures = []

    one, _ = render("WoundTwoWays")
    other, _ = render("WoundHalfwayRound")
    difference = np.abs(one - other).max(axis=2)
    # Inside the surface, away from where its own color is changing quickly, which is where
    # antialiasing lives
    drawn = (one.mean(axis=2) > 14) & (other.mean(axis=2) > 14)
    steady = np.abs(np.diff(one.mean(axis=2), axis=1, prepend=0)) < 6
    inside = drawn & steady
    worst = int(difference[inside].max()) if inside.any() else 0
    differing = int((difference[inside] > TOLERANCE).sum())
    print(f"  a torus wound two ways: {differing} interior pixels differ, worst {worst}")
    if differing:
        failures.append(
            f"a see through torus looks different wound another way, on {differing} pixels "
            f"by up to {worst}: its triangles are not being drawn back to front"
        )

    _, output = render("LooseTriangles")
    line = next((l for l in output.splitlines() if l.startswith("ORDERED|")), None)
    if line is None:
        failures.append("the loose triangle mesh reported nothing")
    else:
        _, ordered, count, triangles = line.split("|")
        print(f"  a mesh of {triangles} loose triangles: ordered={ordered}, "
              f"{count} indices")
        if ordered != "True":
            failures.append("a see through mesh of loose triangles was not ordered at all")
        elif int(count) != 3 * int(triangles):
            failures.append(
                f"{count} indices for {triangles} triangles, wanted {3 * int(triangles)}"
            )

    for failure in failures:
        print(f"  FAIL: {failure}")
    if not failures:
        print("  see through surfaces are drawn back to front, however they are made")
    return 1 if failures else 0


sys.exit(main())
