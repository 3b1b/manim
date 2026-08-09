"""
Scenes for the frame comparison harness, see render_compare.py.

Each one is meant to be quick to render, to come out the same every time it is rendered, and
to put on screen something whose look depends on a part of the renderer which is easy to
break without noticing. Between them they cover every kind of mobject, every pass the
renderer makes, and every uniform a shader reads.
"""
from __future__ import annotations

import itertools as it
import numpy as np
from pathlib import Path
from PIL import Image

from manimlib import *


ASSETS = Path(__file__).parent / "assets"


def checker_image(name: str = "checker.png", size: int = 64) -> str:
    """
    An image to hang on things which take a texture, made here rather than committed, so
    that it is the same every time without a binary living in the repository.
    """
    ASSETS.mkdir(exist_ok=True)
    path = ASSETS / name
    if not path.exists():
        rows, cols = np.indices((size, size))
        squares = ((rows // 8 + cols // 8) % 2).astype(np.uint8)
        Image.fromarray(np.stack([
            255 * squares,
            (255 * rows / size).astype(np.uint8),
            (255 * cols / size).astype(np.uint8),
        ], axis=2)).save(path)
    return str(path)


def star_points(n: int = 5, turns: int = 2, radius: float = 1.0) -> np.ndarray:
    """A self crossing outline, so that a fill has to count windings above one"""
    angles = TAU * turns * np.arange(n + 1) / n + PI / 2
    return radius * np.array([[np.cos(a), np.sin(a), 0] for a in angles])


def corners(*points) -> VMobject:
    return VMobject().set_points_as_corners([np.array(p, dtype=float) for p in points])


def fit(mob: Mobject) -> Mobject:
    """As large as fits in the frame, so that a case cannot quietly grow off the edge"""
    mob.set_height(FRAME_HEIGHT - 1)
    if mob.get_width() > FRAME_WIDTH - 1:
        mob.set_width(FRAME_WIDTH - 1)
    return mob.center()


def half_plane(mob: Mobject, direction: Vect3, offset: float = 0.0):
    """
    A plane through the mobject, keeping the side of it the direction points towards,
    cutting that far along the direction from its center.

    Clip planes are in the scene's coordinates rather than in a mobject's own, so where
    one cuts depends on where the mobject has ended up, and these have to be worked out
    after everything has been arranged rather than before.
    """
    unit = normalize(np.array(direction, dtype=float))
    return (unit, -float(np.dot(mob.get_center(), unit)) - offset)


# Stills


class Fills(Scene):
    """Winding counts: overlaps, holes, self crossing, gradients, transparency"""

    def construct(self):
        opaque = Circle(radius=1.1).set_fill(BLUE_D, 1).set_stroke(width=0)
        over = Square(side_length=1.8).set_fill(RED_D, 1).set_stroke(width=0)
        over.shift(0.6 * RIGHT + 0.4 * DOWN)
        see_through = Circle(radius=0.9).set_fill(YELLOW, 0.5).set_stroke(width=0)
        see_through.shift(0.5 * RIGHT + 0.5 * UP)
        overlaps = Group(opaque, over, see_through)

        holes = Annulus(inner_radius=0.4, outer_radius=1.0).set_fill(TEAL, 1)
        star = corners(*star_points(radius=1.0)).set_fill(GREEN, 1).set_stroke(width=0)
        gradient = Square(side_length=1.8).set_stroke(width=0)
        gradient.set_fill([PINK, BLUE], 1, gradient_direction=UR)
        fading = Circle(radius=0.9).set_stroke(width=0)
        fading.set_fill([WHITE, WHITE], [0.9, 0.1], gradient_direction=RIGHT)

        group = Group(overlaps, holes, star, gradient, fading)
        group.arrange(RIGHT, buff=0.4)
        self.add(fit(group))


class Strokes(Scene):
    """Joints of every angle, closed and open paths, widths along a path"""

    def construct(self):
        angles = VGroup(*(
            corners(LEFT, ORIGIN, rotate_vector(RIGHT, angle))
            for angle in np.linspace(0.05 * PI, 0.95 * PI, 6)
        ))
        angles.set_stroke(WHITE, 8)
        angles.arrange_in_grid(2, 3, buff=0.4)

        closed = Circle(radius=0.8).set_stroke(YELLOW, 10)
        reversal = corners(LEFT, ORIGIN, LEFT + 0.08 * UP).set_stroke(RED, 10)
        rounded = corners(*star_points(radius=0.8))
        rounded.set_stroke(BLUE, 10).set_joint_roundness(1.0)
        tapered = Line(LEFT, RIGHT).insert_n_curves(20).set_stroke(GREEN, [1, 12, 1])
        behind = Circle(radius=0.7).set_fill(GREY_D, 1).set_stroke(ORANGE, 14, behind=True)

        top = Group(angles, closed).arrange(RIGHT, buff=0.5)
        bottom = Group(reversal, rounded, tapered, behind).arrange(RIGHT, buff=0.4)
        both = Group(top, bottom).arrange(DOWN, buff=0.5)
        self.add(fit(both))


class PartialDraws(Scene):
    """
    Shapes part way through being drawn, which is where an open subpath's fill and the
    joints at a subpath's ends are on show. Held still rather than animated, so that what
    is compared is one frame and not a rate function.
    """

    def construct(self):
        def partway(mob, alpha):
            result = mob.copy()
            result.pointwise_become_partial(mob, 0, alpha)
            return result

        sources = [
            Circle(radius=0.7).set_fill(BLUE, 1).set_stroke(WHITE, 4),
            Annulus(inner_radius=0.3, outer_radius=0.7).set_fill(TEAL, 1),
            Tex(R"e^{i\pi}", font_size=72).set_fill(WHITE, 1).set_stroke(YELLOW, 2),
            Square(side_length=1.2).set_fill(RED, 0.5).set_stroke(width=0),
        ]
        rows = Group(*(
            Group(*(partway(source, alpha) for alpha in [0.2, 0.5, 0.8, 1.0]))
            for source in sources
        ))
        for row in rows:
            row.arrange(RIGHT, buff=0.4)
        rows.arrange(DOWN, buff=0.4)
        self.add(fit(rows))


class TextAndTex(Scene):
    """Glyph fills, kerning, colored substrings, and a stroke around text"""

    def construct(self):
        group = VGroup(
            Text("The quick brown fox", font_size=42),
            Text("jumps over the lazy dog", font_size=42,
                 t2c={"jumps": BLUE, "lazy": YELLOW}),
            Tex(R"\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}", font_size=60),
            TexText(R"Text and $\int_0^1 x^2\,dx$ together", font_size=42),
            Text("outlined", font_size=60).set_fill(BLACK, 1).set_stroke(WHITE, 2),
        )
        group.arrange(DOWN, buff=0.3)
        self.add(fit(group))


class ClipPlanes(Scene):
    """
    Every kind of mobject cut by clip planes, one to four at a time, and by clip_to_box.
    Heavily used in the videos repository, and the one place where a change of technique
    could look almost right, see phase 0c of the port plan.
    """

    def construct(self):
        filled = Circle(radius=0.8).set_fill(BLUE, 1).set_stroke(WHITE, 3)
        two = Square(side_length=1.4).set_fill(RED, 1).set_stroke(width=0)
        four = Circle(radius=0.9).set_fill(TEAL, 1).set_stroke(width=0)
        diagonal = Text("clipped", font_size=48)
        see_through = Square(side_length=1.4).set_fill(YELLOW, 0.5).set_stroke(width=0)
        stroked = corners(*star_points(radius=0.8)).set_stroke(GREEN, 8)
        boxed = Group(
            Tex(R"\pi r^2", font_size=48),
            Circle(radius=0.5).set_fill(PURPLE, 1).set_stroke(width=0),
        ).arrange(RIGHT, buff=0.1)
        box = Square(side_length=1.1).move_to(boxed).set_stroke(GREY_B, 1)

        group = Group(filled, two, four, diagonal, see_through, stroked, Group(boxed, box))
        group.arrange_in_grid(2, 4, buff=0.4)
        self.add(fit(group))

        filled.set_clip_plane(*half_plane(filled, RIGHT, -0.2))
        two.set_clip_planes(half_plane(two, RIGHT), half_plane(two, UP))
        four.set_clip_planes(*(
            half_plane(four, direction, -0.25)
            for direction in [RIGHT, LEFT, UP, DOWN]
        ))
        diagonal.set_clip_plane(*half_plane(diagonal, UR))
        see_through.set_clip_plane(*half_plane(see_through, UP, -0.2))
        stroked.set_clip_plane(*half_plane(stroked, LEFT, -0.2))
        boxed.clip_to_box(box)


class ClippedInThree(ThreeDScene):
    """A clip plane cutting things which are depth tested and shaded"""

    def construct(self):
        sphere = Sphere(radius=1.3).set_color(BLUE_E)
        cube = VCube(side_length=1.3).set_fill(TEAL, 1)
        group = Group(sphere, cube).arrange(RIGHT, buff=1.0)
        self.add(group)
        sphere.set_clip_plane(*half_plane(sphere, RIGHT, -0.3))
        cube.set_clip_plane(*half_plane(cube, UP))
        self.frame.reorient(20, 70)


class Surfaces(ThreeDScene):
    """Shading, depth testing, culling, and a mesh over a surface"""

    def construct(self):
        sphere = Sphere(radius=1.0, resolution=(51, 26)).set_color(BLUE_D)
        torus = Torus(r1=0.8, r2=0.3).set_color(GREEN_D)
        graph = ParametricSurface(
            lambda u, v: [u, v, 0.4 * np.sin(2 * u) * np.cos(2 * v)],
            u_range=(-1, 1), v_range=(-1, 1), resolution=(31, 31),
        ).set_color(TEAL_D)
        mesh = SurfaceMesh(Sphere(radius=0.9, resolution=(21, 11)))
        group = Group(sphere, torus, graph, mesh)
        group.arrange_in_grid(2, 2, buff=0.5)
        self.add(fit(group))
        self.frame.reorient(15, 65)


class TransparentSurfaces(ThreeDScene):
    """Two see through surfaces overlapping, one of them sorted to the camera"""

    def construct(self):
        plain = Sphere(radius=1.0).set_color(BLUE, 0.5)
        folded = ParametricSurface(
            lambda u, v: [u, v, 0.7 * np.sin(3 * u)],
            u_range=(-1, 1), v_range=(-1, 1), resolution=(41, 41),
        ).set_color(YELLOW, 0.5)
        folded.set_sort_to_camera(True)
        group = Group(plain, folded).arrange(RIGHT, buff=0.7)
        group.set_height(FRAME_HEIGHT - 2)
        self.add(group)
        self.frame.reorient(25, 70)


class TexturedAndImages(ThreeDScene):
    """A texture on a surface and an image in the plane, both being sampled"""

    def construct(self):
        path = checker_image()
        surface = TexturedSurface(Sphere(radius=1.1, resolution=(51, 26)), path)
        image = ImageMobject(path, height=2.2)
        group = Group(surface, image).arrange(RIGHT, buff=0.8)
        self.add(group)
        self.frame.reorient(10, 70)


class DotsAndVectors(Scene):
    """Many small mobjects: dot clouds, glow, and a field of arrows"""

    def construct(self):
        dots = DotCloud([
            [x, y, 0] for x in np.linspace(-1, 1, 7) for y in np.linspace(-1, 1, 7)
        ], radius=0.06)
        dots.set_color_by_gradient(BLUE, RED)
        glow = GlowDots([[x, 0, 0] for x in np.linspace(-1, 1, 5)], radius=0.4)

        plane = NumberPlane(x_range=(-2, 2), y_range=(-2, 2))
        field = VectorField(
            lambda coords: 0.3 * np.stack([
                -coords[:, 1], coords[:, 0], np.zeros(len(coords)),
            ], axis=1),
            plane,
        )

        group = Group(dots, glow, Group(plane, field))
        group.arrange(RIGHT, buff=0.4)
        self.add(fit(group))


class FixedInFrame(ThreeDScene):
    """Things pinned to the frame while the camera is turned, over things which are not"""

    def construct(self):
        label = Text("fixed in frame", font_size=36).to_corner(UL)
        formula = Tex(R"\vec{v} \cdot \hat{n}", font_size=48).to_corner(DR)
        for mob in [label, formula]:
            mob.fix_in_frame()
        self.add(ThreeDAxes(), Sphere(radius=1.3).set_color(BLUE_E), label, formula)
        self.frame.reorient(35, 60)


class Zoomed(Scene):
    """
    Shapes far smaller and far larger than the frame, which is what decides whether a
    stroke width holds its look, see frame_rescale_factors
    """

    def construct(self):
        shapes = Group(
            Circle(radius=1).set_stroke(WHITE, 4),
            Square(side_length=1.5).set_stroke(YELLOW, 4).set_fill(BLUE, 0.4),
            Tex(R"\alpha", font_size=60),
        ).arrange(RIGHT, buff=0.5)
        self.add(
            shapes.copy().scale(0.1).to_edge(LEFT),
            shapes.copy().scale(2.5).to_edge(RIGHT),
        )
        self.frame.set_height(6)


class ByCode(Scene):
    """A mobject whose color comes from a snippet of shader code"""

    def construct(self):
        square = Square(side_length=3).set_fill(WHITE, 1).set_stroke(width=0)
        # WGSL, which the shaders are written in, and which has no assigning to a swizzle
        square.set_color_by_code(
            "color = vec4f(color.rgb * vec3f(0.5 + 0.5 * sin(3.0 * point.x), 0.4, 1.0), color.a);"
        )
        self.add(square)


# Videos, kept short. These are what catch anything to do with a mobject changing between
# frames, rather than with how one frame is drawn.


class AnimWrite(Scene):
    def construct(self):
        self.play(Write(Tex(R"x^2 + y^2 = r^2", font_size=60)), run_time=0.4)
        self.wait(0.1)


class AnimTransform(Scene):
    def construct(self):
        source = Tex("A^2 + B^2", font_size=60)
        target = Tex("A^2 = B^2", font_size=60)
        self.add(source)
        self.play(TransformMatchingStrings(source, target), run_time=0.4)
        self.wait(0.1)


class AnimShapes(Scene):
    def construct(self):
        circle = Circle(radius=1.2).set_fill(BLUE, 0.5).set_stroke(WHITE, 4)
        square = Square(side_length=2).set_fill(RED, 0.5).set_stroke(YELLOW, 4)
        self.add(circle)
        self.play(ReplacementTransform(circle, square), run_time=0.3)
        self.play(FadeOut(square), run_time=0.2)


class AnimUpdaters(Scene):
    def construct(self):
        tracker = ValueTracker(0.5)
        line = always_redraw(lambda: Line(
            2 * LEFT, 2 * LEFT + 4 * tracker.get_value() * RIGHT,
        ).set_stroke(BLUE, 6))
        dot = GlowDot(color=YELLOW)
        dot.add_updater(lambda m: m.move_to(line.get_end()))
        number = DecimalNumber(0).to_edge(UP)
        number.add_updater(lambda m: m.set_value(tracker.get_value()))
        self.add(line, dot, number)
        self.play(tracker.animate.set_value(1.0), run_time=0.3)


class AnimCamera(ThreeDScene):
    def construct(self):
        label = Text("turning", font_size=36).to_corner(UL)
        label.fix_in_frame()
        self.add(ThreeDAxes(), Sphere(radius=1.2).set_color(BLUE_E), label)
        self.play(self.frame.animate.reorient(40, 60), run_time=0.3)


class AnimTextTransform(Scene):
    """
    Text transformed into other text, whose middle is where a subpath range is a blend of two
    which disagree. The glyphs are what to watch: a fill anchors its fan at the start of its
    own subpath, so a range which came out meaning nothing would eat pieces out of them.
    """

    def construct(self):
        first = Tex(r"\frac{1}{2} + \frac{1}{3}").scale(2)
        second = TexText("one half plus one third").scale(1.2)
        self.add(first)
        self.play(FadeTransform(first, second), run_time=0.3)


class DrawnTogether(Scene):
    """
    Many small stroked mobjects, which the renderer gathers into runs and draws a run at a
    time, see Renderer.group. The joints are what to watch: a run's members sit in one buffer
    with a null curve between them, so a joint reaching into its neighbour would show here.

    Stroke color and width are held per point rather than per mobject, so they are no reason
    to cut a run. What is: a fill, which counts its winding across the whole of a draw, and a
    uniform such as the anti alias width.
    """

    def construct(self):
        def zigzag(color, width):
            mob = VMobject().set_points_as_corners([DL, UP * 0.6, DR, RIGHT * 0.3 + UP * 0.4])
            return mob.set_stroke(color, width).set_height(0.5)

        rows = VGroup(*(
            zigzag(color, width)
            for color, width in zip(color_gradient([YELLOW, TEAL], 40), it.cycle([6, 2]))
        ))
        # Cut in three: a fill in the middle of them, and a wider edge on the last dozen
        rows[20].set_fill(BLUE, 0.6)
        rows[28:].set_anti_alias_width(6.0)
        rows.arrange_in_grid(5, 8, buff=0.25).set_height(FRAME_HEIGHT - 2)
        self.add(rows)
        closed = VGroup(*(
            RegularPolygon(5).set_stroke(RED, 3).set_fill(opacity=0).scale(0.3)
            for _ in range(8)
        )).arrange(RIGHT, buff=0.15).to_edge(DOWN, buff=0.1)
        self.add(closed)
        # Filled shapes, which are drawn on their own however they are laid out, see
        # Drawing.can_follow
        apart = VGroup(*(
            Square().set_fill(BLUE, 0.5).set_stroke(WHITE, 2).scale(0.22)
            for _ in range(6)
        )).arrange(RIGHT, buff=0.12)
        over = VGroup(*(
            Circle().set_fill(YELLOW, 0.5).set_stroke(width=0).scale(0.3)
            for _ in range(2)
        )).arrange(RIGHT, buff=-0.35)
        VGroup(apart, over).arrange(RIGHT, buff=0.4).to_edge(UP, buff=0.1)
        self.add(apart, over)


class AnimSorted(ThreeDScene):
    """
    A see through surface turned past the camera, whose triangles are put in a new order every
    frame. The order is a buffer of its own, so this is the one case where what a frame draws
    is settled by something a bundled draw reads rather than bakes in, see Renderer.
    """

    def construct(self):
        torus = Torus(r1=1.6, r2=0.6, resolution=(51, 25)).set_color(TEAL, 0.4)
        self.add(torus)
        self.frame.reorient(20, 70)
        self.play(self.frame.animate.reorient(70, 55), run_time=0.3)
