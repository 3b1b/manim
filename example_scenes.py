from manimlib.imports import *

# To watch one of these scenes, run the following:
# python -m manim example_scenes.py SquareToCircle
# Use -s to skip to the end and just save the final frame
# Use -w to write the animation to a file
# Use -o to write it to a file and open it once done
# Use -n <number> to skip ahead to the n'th animation of a scene.


class OpeningManimExample(Scene):
    def construct(self):
        title = TexText("This is some \\LaTeX")
        basel = Tex(
            "\\sum_{n=1}^\\infty "
            "\\frac{1}{n^2} = \\frac{\\pi^2}{6}"
        )
        VGroup(title, basel).arrange(DOWN)
        self.play(
            Write(title),
            FadeIn(basel, UP),
        )
        self.wait()

        transform_title = Text("That was a transform")
        transform_title.to_corner(UL)
        self.play(
            Transform(title, transform_title),
            LaggedStartMap(FadeOut, basel, shift=DOWN),
        )
        self.wait()

        fade_comment = Text(
            """
            You probably don't want to overuse
            Transforms, though, a simple fade often
            looks nicer.
            """,
            font_size=36,
            color=GREY_B,
        )
        fade_comment.next_to(
            transform_title, DOWN,
            buff=LARGE_BUFF,
            aligned_edge=LEFT
        )
        self.play(FadeIn(fade_comment, shift=DOWN))
        self.wait(3)

        grid = NumberPlane((-10, 10), (-5, 5))
        grid_title = Text(
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

        matrix = [[1, 1], [0, 1]]
        linear_transform_title = VGroup(
            Text("This is what the matrix"),
            IntegerMatrix(matrix, include_background_rectangle=True),
            Text("looks like")
        )
        linear_transform_title.arrange(RIGHT)
        linear_transform_title.to_edge(UP)

        self.play(
            FadeOut(grid_title),
            FadeIn(linear_transform_title),
        )
        self.play(grid.apply_matrix, matrix, run_time=3)
        self.wait()

        grid_transform_title = Text(
            "And this is a nonlinear transformation"
        )
        grid_transform_title.set_stroke(BLACK, 5, background=True)
        grid_transform_title.to_edge(UP)
        grid.prepare_for_nonlinear_transform(100)
        self.play(
            ApplyPointwiseFunction(
                lambda p: p + np.array([np.sin(p[1]), np.sin(p[0]), 0]),
                grid,
                run_time=5,
            ),
            FadeOut(linear_transform_title),
            FadeIn(grid_transform_title),
        )
        self.wait()


class WarpSquare(Scene):
    def construct(self):
        square = Square()
        self.play(square.apply_complex_function, np.exp)
        self.wait()


class TextExample(Scene):
    def construct(self):
        # To run this scene properly, you should have "Consolas" font in your computer
        # for full usage, you can see https://github.com/3b1b/manim/pull/680
        text = Text("Here is a text", font="Consolas", font_size=90)
        difference = Text(
            """
            The most important difference between Text and TexText is that\n
            you can change the font more easily, but can't use the LaTeX grammar
            """,
            font="Arial", font_size=24,
            # t2c is a dict that you can choose color for different text
            t2c={"Text": BLUE, "TexText": BLUE, "LaTeX": ORANGE}
        )
        VGroup(text, difference).arrange(DOWN, buff=1)
        self.play(Write(text))
        self.play(FadeIn(difference, UP))
        self.wait(3)

        fonts = Text(
            "And you can also set the font according to different words",
            font="Arial",
            t2f={"font": "Consolas", "words": "Consolas"},
            t2c={"font": BLUE, "words": GREEN}
        )
        slant = Text(
            "And the same as slant and weight",
            font="Consolas",
            t2s={"slant": ITALIC},
            t2w={"weight": BOLD},
            t2c={"slant": ORANGE, "weight": RED}
        )
        VGroup(fonts, slant).arrange(DOWN, buff=0.8)
        self.play(FadeOut(text), FadeOut(difference, shift=DOWN))
        self.play(Write(fonts))
        self.wait()
        self.play(Write(slant))
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
        kw = {
            "isolate": ["B", "C", "=", "(", ")"]
        }
        lines = VGroup(
            # Surrounding substrings with double braces
            # will ensure that those parts are separated
            # out in the Tex.  For example, here the
            # Tex will have 5 submobjects, corresponding
            # to the strings [A^2, +, B^2, =, C^2]
            Tex("{{A^2}} + {{B^2}} = {{C^2}}"),
            Tex("{{A^2}} = {{C^2}} - {{B^2}}"),
            # Alternatively, you can pass in the keyword argument
            # isolate with a list of strings that should be out as
            # their own submobject.  So both lines below are equivalent
            # to what you'd get by wrapping every instance of "B", "C"
            # "=", "(" and ")" with double braces
            Tex("{{A^2}} = (C + B)(C - B)", **kw),
            Tex("A = \\sqrt{(C + B)(C - B)}", **kw)
        )
        lines.arrange(DOWN, buff=LARGE_BUFF)
        for line in lines:
            line.set_color_by_tex_to_color_map({
                "A": BLUE,
                "B": TEAL,
                "C": GREEN,
            })

        play_kw = {"run_time": 2}
        self.add(lines[0])
        # The animation TransformMatchingTex will line up parts
        # of the source and target which have matching tex strings.
        # Here, giving it a little path_arc makes each part sort of
        # rotate into their final positions, which feels appropriate
        # for the idea of rearranging an equation
        self.play(
            TransformMatchingTex(
                lines[0].copy(), lines[1],
                path_arc=90 * DEGREES,
            ),
            **play_kw
        )
        self.wait()

        # Now, we could try this again on the next line...
        self.play(
            TransformMatchingTex(lines[1].copy(), lines[2]),
            **play_kw
        )
        self.wait()
        # ...and this looks nice enough, but since there's no tex
        # in lines[2] which matches "C^2" or "B^2", those terms fade
        # out to nothing while the C and B terms fade in from nothing.
        # If, however, we want the C^2 to go to C, and B^2 to go to B,
        # we can specify that with a key map.
        self.play(FadeOut(lines[2]))
        self.play(
            TransformMatchingTex(
                lines[1].copy(), lines[2],
                key_map={
                    "C^2": "C",
                    "B^2": "B",
                }
            ),
            **play_kw
        )
        self.wait()

        # And to finish off, a simple TransformMatchingShapes will do,
        # though maybe we really want that exponent from A^2 to turn
        # into the square root, we could use a key_map again.  Or,
        # if we set fade_transform_mismatches to True, then it will
        # line up mismatching submobjects and have them transform
        # into each other
        self.play(
            TransformMatchingTex(
                lines[2].copy(), lines[3],
                fade_transform_mismatches=True,
            ),
            **play_kw
        )
        self.wait(3)
        self.play(FadeOut(lines, RIGHT))

        # Alternatively, if you don't want to think about breaking up
        # the tex strings deliberately, you can TransformMatchingShapes,
        # which will try to line up all pieces of a source mobject with
        # those of a target, regardless of the submobject hierarchy in
        # each one, according to whether those pieces have the same
        # shape (as best it can).
        source = TexText("the morse code")
        target = TexText("here come dots")

        self.play(Write(source))
        self.wait()
        kw = {"run_time": 3, "path_arc": PI / 2}
        self.play(TransformMatchingShapes(source, target, **kw))
        self.wait()
        self.play(TransformMatchingShapes(target, source, **kw))
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
        surface_text = Text("For 3d scenes, try using surfaces")
        surface_text.fix_in_frame()
        surface_text.to_edge(UP)
        self.add(surface_text)
        self.wait(0.1)

        torus1 = Torus(r1=1, r2=1)
        torus2 = Torus(r1=3, r2=1)
        sphere = Sphere(radius=3, resolution=torus1.resolution)
        # You can texture a surface with up to two images, which will
        # be interpreted as the side towards the light, and away from
        # the light.  These can be either urls, or paths to a local file
        # in whatever you've set as the image directory in
        # the custom_defaults.yml file

        # day_texture = "EarthTextureMap"
        # night_texture = "NightEarthTextureMap"
        day_texture = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Whole_world_-_land_and_oceans.jpg/1280px-Whole_world_-_land_and_oceans.jpg"
        night_texture = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/The_earth_at_night.jpg/1280px-The_earth_at_night.jpg"

        surfaces = [
            TexturedSurface(surface, day_texture, night_texture)
            for surface in [sphere, torus1, torus2]
        ]

        for mob in surfaces:
            mob.shift(IN)
            mob.mesh = SurfaceMesh(mob)
            mob.mesh.set_stroke(BLUE, 1, opacity=0.5)

        # Set perspective
        frame = self.camera.frame
        frame.set_euler_angles(
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
        light_text = Text("You can move around the light source")
        light_text.move_to(surface_text)
        light_text.fix_in_frame()

        self.play(FadeTransform(surface_text, light_text))
        light = self.camera.light_source
        self.add(light)
        light.save_state()
        self.play(light.move_to, 3 * IN, run_time=5)
        self.play(light.shift, 10 * OUT, run_time=5)

        drag_text = Text("Try moving the mouse while pressing d or s")
        drag_text.move_to(light_text)
        drag_text.fix_in_frame()

        self.play(FadeTransform(light_text, drag_text))
        self.wait()


# See https://github.com/3b1b/videos for many, many more
