#!/usr/bin/env python

from manimlib.imports import *

# To watch one of these scenes, run the following:
# python -m manim example_scenes.py SquareToCircle
# Use -s to skip to the end and just save the final frame
# Use -w to write the animation to a file
# Use -o to write it to a file and open it once done
# Use -n <number> to skip ahead to the n'th animation of a scene.
# Use -r <number> to specify a resolution (for example, -r 1080
# for a 1920x1080 video)


class OpeningManimExample(Scene):
    def construct(self):
        title = TextMobject("This is some \\LaTeX")
        basel = TexMobject(
            "\\sum_{n=1}^\\infty "
            "\\frac{1}{n^2} = \\frac{\\pi^2}{6}"
        )
        VGroup(title, basel).arrange(DOWN)
        self.play(
            Write(title),
            FadeIn(basel, UP),
        )
        self.wait()

        transform_title = TextMobject("That was a transform")
        transform_title.to_corner(UP + LEFT)
        self.play(
            Transform(title, transform_title),
            LaggedStartMap(FadeOut, basel, shift=DOWN),
        )
        self.wait()

        fade_comment = TextMobject("""
            You probably don't want to over use\\\\
            Transforms, though, a simple fade often\\\\
            looks nicer.
        """)
        fade_comment.next_to(
            transform_title, DOWN,
            buff=LARGE_BUFF,
            aligned_edge=LEFT
        )
        self.play(FadeIn(fade_comment, shift=DOWN))
        self.wait(3)

        grid = NumberPlane()
        grid_title = TextMobject(
            "But manim is for illustrating math, not text",
        )
        grid_title.to_edge(UP)
        grid_title.add_background_rectangle()

        self.add(grid, grid_title)  # Make sure title is on top of grid
        self.play(
            FadeOut(title, shift=LEFT),
            FadeOut(fade_comment, shift=LEFT),
            FadeIn(grid_title),
            ShowCreation(grid, run_time=3, lag_ratio=0.1),
        )
        self.wait()

        grid_transform_title = TextMobject(
            "This is a non-linear function applied to the grid"
        )
        grid_transform_title.set_stroke(BLACK, 5, background=True)
        grid_transform_title.to_edge(UP)
        grid.prepare_for_nonlinear_transform()
        self.play(
            ApplyPointwiseFunction(
                lambda p: p + np.array([np.sin(p[1]), np.sin(p[0]), 0]),
                grid,
                run_time=5,
            ),
            FadeOut(grid_title),
            FadeIn(grid_transform_title),
        )
        self.wait()


class WarpSquare(Scene):
    def construct(self):
        square = Square()
        self.play(square.apply_complex_function, np.exp)
        self.wait()


class SquareToCircle(Scene):
    def construct(self):
        circle = Circle()
        circle.set_fill(BLUE, opacity=0.5)
        circle.set_stroke(BLUE_E, width=4)
        square = Square()

        self.play(ShowCreation(square))
        self.wait()
        self.play(ReplacementTransform(square, circle))
        self.wait()

        # This opens an iPython termnial where you can keep writing
        # lines as if they were part of this construct method
        self.embed()
        # Try typing the following lines
        # self.play(circle.stretch, 4, {"dim": 0})
        # self.play(Rotate(circle, TAU / 4))
        # self.play(circle.shift, 2 * RIGHT, circle.scale, 0.25)
        # circle.insert_n_curves(10)
        # self.play(circle.apply_complex_function, lambda z: z**2)


class TexTransformExample(Scene):
    def construct(self):
        lines = VGroup(
            # Surrounding substrings with double braces
            # will ensure that those parts are separated
            # out in the TexMobject.  For example, here the
            # TexMobject will have 5 submobjects, corresponding
            # to the strings [A^2, +, B^2, =, C^2]
            TexMobject("{{A^2}} + {{B^2}} = {{C^2}}"),
            TexMobject("{{A^2}} = {{C^2}} - {{B^2}}"),
            TexMobject(
                "A = \\sqrt{(C + B)(C - B)}",
                substrings_to_isolate=["A", "B", "C"]
            ),
        )
        lines.arrange(DOWN, buff=LARGE_BUFF)
        for line in lines:
            line.set_color_by_tex_to_color_map({
                "A": BLUE,
                "B": TEAL,
                "C": GREEN,
            })

        self.add(lines[0])

        # The animation TransformMatchingTex will line up parts
        # of the source and target which have matching tex strings
        self.play(TransformMatchingTex(
            lines[0].copy(), lines[1],
            run_time=2, path_arc=90 * DEGREES,
        ))
        self.wait()
        # The animation TransformMatchingShapes will line up parts
        # of the source and target which have matching shapes, regardless
        # of where they fall in the mobject family heirarchies.
        # For example, calling TransformMatchingTex below would not
        # quite look like we want, becuase lines[2] has none of its
        # substringsisolated, and even if it did it would not know to
        # match the symbol "C", say, from line[1] to the "C" from line[2],
        # since in line[1] it is tied up with the full C^2 submobject.
        # However, TransformMatchingShapes just does its best to pair
        # pieces which look the same
        self.play(TransformMatchingShapes(
            lines[1].copy(), lines[2],
            run_time=2,
        ))
        self.wait()


class UpdatersExample(Scene):
    def construct(self):
        decimal = DecimalNumber(
            0,
            show_ellipsis=True,
            num_decimal_places=3,
            include_sign=True,
        )
        square = Square()
        square.to_edge(UP)

        # This ensures that the method deicmal.next_to(square)
        # is called on every frame
        always(decimal.next_to, square)
        # This ensures thst decimal.set_value(square.get_y()) is
        # called every frame
        f_always(decimal.set_value, square.get_y)

        self.add(square, decimal)
        self.play(
            square.to_edge, DOWN,
            run_time=3,
        )
        self.play(square.center)
        self.wait()

        # You can also add any function generally to a Mobject's
        # list of 'updaters'.
        now = self.time
        square.add_updater(
            lambda m: m.set_y(math.sin(self.time - now))
        )
        self.wait(10)


class SurfaceExample(Scene):
    CONFIG = {
        "camera_class": ThreeDCamera,
    }

    def construct(self):
        torus1 = Torus(r1=1, r2=1)
        torus2 = Torus(r1=3, r2=1)
        sphere = Sphere(radius=3, resolution=torus1.resolution)
        surfaces = [sphere, torus1, torus2]
        # If you want these to be textured with pictures of, say, earth,
        # find images for the texture maps you want, perhaps
        # https://en.wikipedia.org/wiki/File:Blue_Marble_2002.png and
        # https://commons.wikimedia.org/wiki/File:The_earth_at_night.jpg
        # and make sure they are available in whatever folder manim
        # looks for images, then uncomment the lines below
        surfaces = [
            TexturedSurface(surface, "EarthTextureMap", "NightEarthTextureMap")
            for surface in [sphere, torus1, torus2]
        ]

        for mob in surfaces:
            mob.mesh = SurfaceMesh(mob)
            mob.mesh.set_stroke(BLUE, 1, opacity=0.5)

        # Set perspective
        frame = self.camera.frame
        frame.set_rotation(
            theta=-30 * DEGREES,
            phi=70 * DEGREES,
        )

        surface = surfaces[0]

        self.play(
            FadeIn(surface),
            ShowCreation(surface.mesh, lag_ratio=0.01, run_time=3),
        )
        for mob in surfaces:
            mob.add(mob.mesh)
        surface.save_state()
        self.play(Rotate(surface, PI / 2), run_time=2)
        for mob in surfaces[1:]:
            mob.rotate(PI / 2)

        self.play(
            Transform(surface, surfaces[1]),
            run_time=3
        )

        self.play(
            Transform(surface, surfaces[2]),
            # Move camera frame during the transition
            frame.increment_phi, -10 * DEGREES,
            frame.increment_theta, -20 * DEGREES,
            run_time=3
        )
        # Add ambient rotation
        frame.add_updater(lambda m, dt: m.increment_theta(-0.1 * dt))

        # Play around with where the light is
        light = self.camera.light_source
        self.add(light)
        light.save_state()
        self.play(light.move_to, 3 * IN, run_time=5)
        self.play(light.shift, 10 * OUT, run_time=5)
        self.wait(4)


# See https://github.com/3b1b/videos for many, many more
