Example Scenes
==============

After understanding the previous knowledge, we can understand more scenes. 
Many example scenes are given in ``example_scenes.py``, let's start with 
the simplest and one by one.

SquareToCircle
--------------

.. manim-example:: SquareToCircle
    :media: ../_static/example_scenes/SquareToCircle.mp4

    from manimlib.imports import *

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

This scene is what we wrote in :doc:`quickstart`.
No more explanation here

WarpSquare
----------

.. manim-example:: WarpSquare
   :media: ../_static/example_scenes/WarpSquare.mp4

   class WarpSquare(Scene):
       def construct(self):
           square = Square()
           self.play(square.apply_complex_function, np.exp)
           self.wait()

The new usage in this scene is ``self.play(square.apply_complex_function, np.exp)``, 
which shows an animation of applying a complex function :math:`f(z)=e^z` to a square. 
It is equivalent to transforming the original square into the result after 
applying a function.

TextExample
-----------

.. manim-example:: TextExample
   :media: ../_static/example_scenes/TextExample.mp4

    class TextExample(Scene):
        def construct(self):
            text = Text("Here is a text", font="Consolas", font_size=90)
            difference = Text(
                """
                The most important difference between Text and TexText is that\n
                you can change the font more easily, but can't use the LaTeX grammar
                """,
                font="Arial", font_size=24,
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

The new classes in this scene are ``Text``, ``VGroup``, ``Write``, ``FadeIn`` and ``FadeOut``.

- ``Text`` can create text, define fonts, etc. The usage ais clearly reflected in the above examples.
- ``VGroup`` can put multiple ``VMobject`` together as a whole. In the example, the ``.arrange()`` method is called to arrange the sub-mobjects in sequence downward (``DOWN``), and the spacing is ``buff``.
- ``Write`` is an animation that shows similar writing effects.
- ``FadeIn`` fades the object in, the second parameter indicates the direction of the fade in.
- ``FadeOut`` fades out the object, the second parameter indicates the direction of the fade out.

TexTransformExample
-------------------

.. manim-example:: TexTransformExample
   :media: ../_static/example_scenes/TexTransformExample.mp4

    class TexTransformExample(Scene):
        def construct(self):
            kw = {
                "isolate": ["B", "C", "=", "(", ")"]
            }
            lines = VGroup(
                Tex("{{A^2}} + {{B^2}} = {{C^2}}"),
                Tex("{{A^2}} = {{C^2}} - {{B^2}}"),
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
            self.play(
                TransformMatchingTex(
                    lines[0].copy(), lines[1],
                    path_arc=90 * DEGREES,
                ),
                **play_kw
            )
            self.wait()

            self.play(
                TransformMatchingTex(lines[1].copy(), lines[2]),
                **play_kw
            )
            self.wait()
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

            self.play(
                TransformMatchingTex(
                    lines[2].copy(), lines[3],
                    fade_transform_mismatches=True,
                ),
                **play_kw
            )
            self.wait(3)
            self.play(FadeOut(lines, RIGHT))

            source = TexText("the morse code")
            target = TexText("here come dots")

            self.play(Write(source))
            self.wait()
            kw = {"run_time": 3, "path_arc": PI / 2}
            self.play(TransformMatchingShapes(source, target, **kw))
            self.wait()
            self.play(TransformMatchingShapes(target, source, **kw))
            self.wait()

The new classes in this scene are ``Tex``, ``TexText``, ``TransformMatchingTex``
and ``TransformMatchingShapes``.

- ``Tex`` uses LaTeX to create mathematical formulas.
- ``TexText`` uses LaTeX to create text.
- ``TransformMatchingTeX`` automatically transforms sub-objects according to the similarities and differences of tex in ``Tex``.
- ``TransformMatchingShapes`` automatically transform sub-objects directly based on the similarities and differences of the object point sets.

UpdatersExample
---------------

.. manim-example:: UpdatersExample
   :media: ../_static/example_scenes/UpdatersExample.mp4

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

            always(decimal.next_to, square)
            f_always(decimal.set_value, square.get_y)

            self.add(square, decimal)
            self.play(
                square.to_edge, DOWN,
                run_time=3,
            )
            self.play(square.center)
            self.wait()

            now = self.time
            square.add_updater(
                lambda m: m.set_y(math.sin(self.time - now))
            )
            self.wait(10)

The new classes and usage in this scene are ``DecimalNumber``, ``.to_edge()``, 
``.center()``, ``always()``, ``f_always()``, ``.set_y()`` and ``.add_updater()``.

- ``DecimalNumber`` is a variable number, speed it up by breaking it into ``Tex`` characters.
- ``.to_edge()`` means to place the object on the edge of the screen.
- ``.center()`` means to place the object in the center of the screen.
- ``always(f, x)`` means that a certain function (``f(x)``) is executed every frame.
- ``f_always(f, g)`` is similar to ``always``, executed ``f(g())`` every frame.
- ``.set_y()`` means to set the ordinate of the object on the screen.
- ``.add_updater()`` sets an update function for the object. For example: ``mob1.add_updater(lambda mob: mob.next_to(mob2))`` means ``mob1.next_to(mob2)`` is executed every frame.

SurfaceExample
--------------

.. manim-example:: SurfaceExample
   :media: ../_static/example_scenes/SurfaceExample.mp4

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

This scene shows an example of using a three-dimensional surface, and 
the related usage has been briefly described in the notes.

- ``.fix_in_frame()`` makes the object not change with the view angle of the screen, and is always displayed at a fixed position on the screen.

OpeningManimExample
-------------------

.. manim-example:: OpeningManimExample
   :media: ../_static/example_scenes/OpeningManimExample.mp4

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

This scene is a comprehensive application of a two-dimensional scene.

After seeing these scenes, you have already understood part of the 
usage of manim. For more examples, see `the video code of 3b1b <https://github.com/3b1b/videos>`_.
