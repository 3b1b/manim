from __future__ import annotations

import numpy as np

from manimlib.constants import FRAME_HEIGHT, FRAME_WIDTH


def vmobject_to_svg(
    vmobject,
    filename: str | None = None,
    pixel_width: int = 1920,
    pixel_height: int = 1080,
) -> str:
    """
    Convert a VMobject (and its family) to an SVG string.

    Iterates family_members_with_points() in order, emitting one <path>
    element per member. Manim's y-up coordinate system is flipped to SVG's
    y-down system by negating y values. The viewBox uses Manim frame units
    so that relative positions are preserved; pixel_width/pixel_height set
    the rendered resolution.

    If filename is provided, the SVG is also written to that path.
    """
    fw = FRAME_WIDTH
    fh = FRAME_HEIGHT
    stroke_scale = pixel_width / fw

    vb_x = -fw / 2
    vb_y = -fh / 2

    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg"',
        f'     viewBox="{vb_x} {vb_y} {fw} {fh}"',
        f'     width="{pixel_width}" height="{pixel_height}">',
    ]

    for mob in vmobject.family_members_with_points():
        path_data = _get_path_data(mob)
        if not path_data:
            continue

        fill_color = mob.get_fill_color()
        fill_opacity = mob.get_fill_opacity()
        stroke_color = mob.get_stroke_color()
        stroke_opacity = mob.get_stroke_opacity()
        stroke_width = mob.get_stroke_width() / stroke_scale

        fill_str = fill_color if fill_opacity > 0 else "none"
        stroke_str = stroke_color if (stroke_opacity > 0 and stroke_width > 0) else "none"

        attrs = [f'd="{path_data}"', f'fill="{fill_str}"']
        if fill_str != "none" and fill_opacity < 1:
            attrs.append(f'fill-opacity="{fill_opacity:.6g}"')
        attrs.append(f'stroke="{stroke_str}"')
        if stroke_str != "none":
            attrs.append(f'stroke-width="{stroke_width:.6g}"')
            if stroke_opacity < 1:
                attrs.append(f'stroke-opacity="{stroke_opacity:.6g}"')

        lines.append(f'  <path {" ".join(attrs)}/>')

    lines.append('</svg>')
    svg_str = '\n'.join(lines)

    if filename is not None:
        with open(filename, 'w') as f:
            f.write(svg_str)

    return svg_str


def _get_path_data(mob) -> str:
    """Build SVG path data string from a single VMobject's subpaths."""
    subpaths = mob.get_subpaths()
    if not subpaths:
        return ""

    parts = []
    for subpath in subpaths:
        # subpath is [a0, h0, a1, h1, ..., an], length = 2n+1
        a0 = subpath[0]
        parts.append(f"M {a0[0]:.6g},{-a0[1]:.6g}")

        for i in range(0, len(subpath) - 2, 2):
            a_cur = subpath[i]
            h = subpath[i + 1]
            a_next = subpath[i + 2]
            # Linear segment when handle sits on the start anchor or at the
            # midpoint between the two anchors (both are common in Manim)
            midpoint = 0.5 * (a_cur + a_next)
            if np.allclose(h, a_cur, atol=1e-4) or np.allclose(h, midpoint, atol=1e-4):
                parts.append(f"L {a_next[0]:.6g},{-a_next[1]:.6g}")
            else:
                parts.append(
                    f"Q {h[0]:.6g},{-h[1]:.6g} {a_next[0]:.6g},{-a_next[1]:.6g}"
                )

        if np.allclose(subpath[-1], subpath[0], atol=1e-4):
            parts.append("Z")

    return " ".join(parts)
