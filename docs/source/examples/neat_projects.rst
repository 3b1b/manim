NeatProjects
=================================


.. manim:: OpeningManimExample
    :quality: low

    class OpeningManimExample(Scene):
        def construct(self):
            title = Tex("This is some \\LaTeX")
            basel = MathTex("\\sum_{n=1}^\\infty " "\\frac{1}{n^2} = \\frac{\\pi^2}{6}")
            VGroup(title, basel).arrange(DOWN)
            self.play(
                Write(title),
                FadeInFrom(basel, UP),
            )
            self.wait()
    
            transform_title = Tex("That was a transform")
            transform_title.to_corner(UP + LEFT)
            self.play(
                Transform(title, transform_title),
                LaggedStart(*map(FadeOutAndShiftDown, basel)),
            )
            self.wait()
    
            grid = NumberPlane()
            grid_title = Tex("This is a grid")
            grid_title.scale(1.5)
            grid_title.move_to(transform_title)
    
            self.add(grid, grid_title)  # Make sure title is on top of grid
            self.play(
                FadeOut(title),
                FadeInFromDown(grid_title),
                ShowCreation(grid, run_time=3, lag_ratio=0.1),
            )
            self.wait()
    
            grid_transform_title = Tex(
                "That was a non-linear function \\\\" "applied to the grid"
            )
            grid_transform_title.move_to(grid_title, UL)
            grid.prepare_for_nonlinear_transform()
            self.play(
                grid.apply_function,
                lambda p: p
                          + np.array(
                    [
                        np.sin(p[1]),
                        np.sin(p[0]),
                        0,
                    ]
                ),
                run_time=3,
            )
            self.wait()
            self.play(Transform(grid_title, grid_transform_title))
            self.wait()


.. manim:: SquareToCircle
    :quality: low

    class SquareToCircle(Scene):
        def construct(self):
            circle = Circle()
            square = Square()
            square.flip(RIGHT)
            square.rotate(-3 * TAU / 8)
            circle.set_fill(PINK, opacity=0.5)
    
            self.play(ShowCreation(square))
            self.play(Transform(square, circle))
            self.play(FadeOut(square))


.. manim:: WarpSquare
    :quality: low

    class WarpSquare(Scene):
        def construct(self):
            square = Square()
            self.play(
                ApplyPointwiseFunction(
                    lambda point: complex_to_R3(np.exp(R3_to_complex(point))), square
                )
            )
            self.wait()

.. manim:: WriteStuff
    :quality: low

    class WriteStuff(Scene):
        def construct(self):
            example_text = Tex("This is a some text", tex_to_color_map={"text": YELLOW})
            example_tex = MathTex(
                "\\sum_{k=1}^\\infty {1 \\over k^2} = {\\pi^2 \\over 6}",
            )
            group = VGroup(example_text, example_tex)
            group.arrange(DOWN)
            group.set_width(config["frame_width"] - 2 * LARGE_BUFF)
    
            self.play(Write(example_text))
            self.play(Write(example_tex))
            self.wait()

.. manim:: UpdatersExample
    :quality: low

    class UpdatersExample(Scene):
        def construct(self):
            decimal = DecimalNumber(
                0,
                show_ellipsis=True,
                num_decimal_places=3,
                include_sign=True,
            )
            square = Square().to_edge(UP)
    
            decimal.add_updater(lambda d: d.next_to(square, RIGHT))
            decimal.add_updater(lambda d: d.set_value(square.get_center()[1]))
            self.add(square, decimal)
            self.play(
                square.to_edge,
                DOWN,
                rate_func=there_and_back,
                run_time=5,
            )
            self.wait()


.. manim:: VDictExample
    :quality: low

    class VDictExample(Scene):
        def construct(self):
            square = Square().set_color(RED)
            circle = Circle().set_color(YELLOW).next_to(square, UP)
    
            # create dict from list of tuples each having key-mobject pair
            pairs = [("s", square), ("c", circle)]
            my_dict = VDict(pairs, show_keys=True)
    
            # display it just like a VGroup
            self.play(ShowCreation(my_dict))
            self.wait()
    
            text = Tex("Some text").set_color(GREEN).next_to(square, DOWN)
    
            # add a key-value pair by wrapping it in a single-element list of tuple
            # after attrs branch is merged, it will be easier like `.add(t=text)`
            my_dict.add([("t", text)])
            self.wait()
    
            rect = Rectangle().next_to(text, DOWN)
            # can also do key assignment like a python dict
            my_dict["r"] = rect
    
            # access submobjects like a python dict
            my_dict["t"].set_color(PURPLE)
            self.play(my_dict["t"].scale, 3)
            self.wait()
    
            # also supports python dict styled reassignment
            my_dict["t"] = Tex("Some other text").set_color(BLUE)
            self.wait()
    
            # remove submoject by key
            my_dict.remove("t")
            self.wait()
    
            self.play(Uncreate(my_dict["s"]))
            self.wait()
    
            self.play(FadeOut(my_dict["c"]))
            self.wait()
    
            self.play(FadeOutAndShift(my_dict["r"], DOWN))
            self.wait()
    
            # you can also make a VDict from an existing dict of mobjects
            plain_dict = {
                1: Integer(1).shift(DOWN),
                2: Integer(2).shift(2 * DOWN),
                3: Integer(3).shift(3 * DOWN),
            }
    
            vdict_from_plain_dict = VDict(plain_dict)
            vdict_from_plain_dict.shift(1.5 * (UP + LEFT))
            self.play(ShowCreation(vdict_from_plain_dict))
    
            # you can even use zip
            vdict_using_zip = VDict(zip(["s", "c", "r"], [Square(), Circle(), Rectangle()]))
            vdict_using_zip.shift(1.5 * RIGHT)
            self.play(ShowCreation(vdict_using_zip))
            self.wait()


.. manim:: VariableExample
    :quality: low

    class VariableExample(Scene):
        def construct(self):
            var = 0.5
            on_screen_var = Variable(var, Text("var"), num_decimal_places=3)
    
            # You can also change the colours for the label and value
            on_screen_var.label.set_color(RED)
            on_screen_var.value.set_color(GREEN)
    
            self.play(Write(on_screen_var))
            # The above line will just display the variable with
            # its initial value on the screen. If you also wish to
            # update it, you can do so by accessing the `tracker` attribute
            self.wait()
            var_tracker = on_screen_var.tracker
            var = 10.5
            self.play(var_tracker.set_value, var)
            self.wait()
    
            int_var = 0
            on_screen_int_var = Variable(
                int_var, Text("int_var"), var_type=Integer
            ).next_to(on_screen_var, DOWN)
            on_screen_int_var.label.set_color(RED)
            on_screen_int_var.value.set_color(GREEN)
    
            self.play(Write(on_screen_int_var))
            self.wait()
            var_tracker = on_screen_int_var.tracker
            var = 10.5
            self.play(var_tracker.set_value, var)
            self.wait()
    
            # If you wish to have a somewhat more complicated label for your
            # variable with subscripts, superscripts, etc. the default class
            # for the label is MathTex
            subscript_label_var = 10
            on_screen_subscript_var = Variable(subscript_label_var, "{a}_{i}").next_to(
                on_screen_int_var, DOWN
            )
            self.play(Write(on_screen_subscript_var))
            self.wait()