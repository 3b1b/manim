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

AnimatingMethods
----------------

.. manim-example:: AnimatingMethods
    :media: ../_static/example_scenes/AnimatingMethods.mp4

    class AnimatingMethods(Scene):
        def construct(self):
            grid = Tex(r"\pi").get_grid(10, 10, height=4)
            self.add(grid)

            # If you pass in a mobject method to the scene's "play" function,
            # it will apply an animation interpolating between the mobject's
            # initial state and whatever happens when you apply that method.
            # For example, calling grid.shift(2 * LEFT) would shift it two units
            # to the left, but the following line animates that motion.
            self.play(grid.shift, 2 * LEFT)
            # The same applies for any method, including those setting colors.
            self.play(grid.set_submobject_colors_by_gradient, BLUE, GREEN)
            self.play(grid.set_height, TAU - MED_SMALL_BUFF)
            self.wait()

            # The method Mobject.apply_complex_function lets you apply arbitrary
            # complex functions, treating the points defining the mobject as
            # complex numbers.
            self.play(grid.apply_complex_function, np.exp, run_time=5)
            self.wait()

            # Even more generally, you could apply Mobject.apply_function,
            # which takes in functions form R^3 to R^3
            self.play(
                grid.apply_function,
                lambda p: [
                    p[0] + 0.5 * math.sin(p[1]),
                    p[1] + 0.5 * math.sin(p[0]),
                    p[2]
                ],
                run_time=5,
            )
            self.wait()

The new usage in this scene is ``.get_grid()`` and ``self.play(mob.method, args)``.

- ``.get_grid()`` method will return a new mobject containing multiple copies of this one arranged in a grid.
- ``self.play(mob.method, args)`` animate the method, and the details are in the comments above.

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
            to_isolate = ["B", "C", "=", "(", ")"]
            lines = VGroup(
                # Surrounding substrings with double braces
                # will ensure that those parts are separated
                # out in the Tex.  For example, here the
                # Tex will have 5 submobjects, corresponding
                # to the strings [A^2, +, B^2, =, C^2]
                Tex("{{A^2}} + {{B^2}} = {{C^2}}"),
                Tex("{{A^2}} = {{C^2}} - {{B^2}}"),
                # Alternatively, you can pass in the keyword argument
                # "isolate" with a list of strings that should be out as
                # their own submobject.  So both lines below are equivalent
                # to what you'd get by wrapping every instance of "B", "C"
                # "=", "(" and ")" with double braces
                Tex("{{A^2}} = (C + B)(C - B)", isolate=to_isolate),
                Tex("A = \\sqrt{(C + B)(C - B)}", isolate=to_isolate)
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

            # And to finish off, a simple TransformMatchingShapes would work
            # just fine.  But perhaps we want that exponent on A^2 to transform into
            # the square root symbol.  At the moment, lines[2] treats the expression
            # A^2 as a unit, so we might create a new version of the same line which
            # separates out just the A.  This way, when TransformMatchingTex lines up
            # all matching parts, the only mismatch will be between the "^2" from
            # new_line2 and the "\sqrt" from the final line.  By passing in,
            # transform_mismatches=True, it will transform this "^2" part into
            # the "\sqrt" part.
            new_line2 = Tex("{{A}}^2 = (C + B)(C - B)", isolate=to_isolate)
            new_line2.replace(lines[2])
            new_line2.match_style(lines[2])

            self.play(
                TransformMatchingTex(
                    new_line2, lines[3],
                    transform_mismatches=True,
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
            source = Text("the morse code", height=1)
            target = Text("here come dots", height=1)

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
            square = Square()
            square.set_fill(BLUE_E, 1)

            # On all all frames, the constructor Brace(square, UP) will
            # be called, and the mobject brace will set its data to match
            # that of the newly constructed object
            brace = always_redraw(Brace, square, UP)

            text, number = label = VGroup(
                Text("Width = "),
                DecimalNumber(
                    0,
                    show_ellipsis=True,
                    num_decimal_places=2,
                    include_sign=True,
                )
            )
            label.arrange(RIGHT)

            # This ensures that the method deicmal.next_to(square)
            # is called on every frame
            always(label.next_to, brace, UP)
            # You could also write the following equivalent line
            # label.add_updater(lambda m: m.next_to(brace, UP))

            # If the argument itself might change, you can use f_always,
            # for which the arguments following the initial Mobject method
            # should be functions returning arguments to that method.
            # The following line ensures thst decimal.set_value(square.get_y())
            # is called every frame
            f_always(number.set_value, square.get_width)
            # You could also write the following equivalent line
            # number.add_updater(lambda m: m.set_value(square.get_width()))

            self.add(square, brace, label)

            # Notice that the brace and label track with the square
            self.play(
                square.scale, 2,
                rate_func=there_and_back,
                run_time=2,
            )
            self.wait()
            self.play(
                square.set_width, 5, {"stretch": True},
                run_time=3,
            )
            self.wait()
            self.play(
                square.set_width, 2,
                run_time=3
            )
            self.wait()

            # In general, you can alway call Mobject.add_updater, and pass in
            # a function that you want to be called on every frame.  The function
            # should take in either one argument, the mobject, or two arguments,
            # the mobject and the amount of time since the last frame.
            now = self.time
            w0 = square.get_width()
            square.add_updater(
                lambda m: m.set_width(w0 * math.cos(self.time - now))
            )
            self.wait(4 * PI)

The new classes and usage in this scene are ``always_redraw()``, ``DecimalNumber``, ``.to_edge()``, 
``.center()``, ``always()``, ``f_always()``, ``.set_y()`` and ``.add_updater()``.

- ``always_redraw()`` function create a new mobject every frame.
- ``DecimalNumber`` is a variable number, speed it up by breaking it into ``Text`` characters.
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
            intro_words = Text("""
                The original motivation for manim was to
                better illustrate mathematical functions
                as transformations.
            """)
            intro_words.to_edge(UP)

            self.play(Write(intro_words))
            self.wait(2)

            # Linear transform
            grid = NumberPlane((-10, 10), (-5, 5))
            matrix = [[1, 1], [0, 1]]
            linear_transform_words = VGroup(
                Text("This is what the matrix"),
                IntegerMatrix(matrix, include_background_rectangle=True),
                Text("looks like")
            )
            linear_transform_words.arrange(RIGHT)
            linear_transform_words.to_edge(UP)
            linear_transform_words.set_stroke(BLACK, 10, background=True)

            self.play(
                ShowCreation(grid),
                FadeTransform(intro_words, linear_transform_words)
            )
            self.wait()
            self.play(grid.apply_matrix, matrix, run_time=3)
            self.wait()

            # Complex map
            c_grid = ComplexPlane()
            moving_c_grid = c_grid.copy()
            moving_c_grid.prepare_for_nonlinear_transform()
            c_grid.set_stroke(BLUE_E, 1)
            c_grid.add_coordinate_labels(number_config={"font_size": 36})
            complex_map_words = TexText("""
                Or thinking of the plane as $\\mathds{C}$,\\\\
                this is the map $z \\rightarrow z^2$
            """)
            complex_map_words.to_corner(UR)
            complex_map_words.set_stroke(BLACK, 5, background=True)

            self.play(
                FadeOut(grid),
                Write(c_grid, run_time=3),
                FadeIn(moving_c_grid),
                FadeTransform(linear_transform_words, complex_map_words),
            )
            self.wait()
            self.play(
                moving_c_grid.apply_complex_function, lambda z: z**2,
                run_time=6,
            )
            self.wait(2)

This scene is a comprehensive application of a two-dimensional scene.

After seeing these scenes, you have already understood part of the 
usage of manim. For more examples, see `the video code of 3b1b <https://github.com/3b1b/videos>`_.
