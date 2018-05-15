from big_ol_pile_of_manim_imports import *


def apply_function_to_center(point_func, mobject):
    mobject.apply_function_to_position(point_func)


def apply_function_to_submobjects(point_func, mobject):
    mobject.apply_function_to_submobject_positions(point_func)


def apply_function_to_points(point_func, mobject):
    mobject.apply_function(point_func)


class NumberlineTransformationScene(ZoomedScene):
    CONFIG = {
        "input_line_zero_point": 0.5 * UP + (FRAME_X_RADIUS - 1) * LEFT,
        "output_line_zero_point": 2 * DOWN + (FRAME_X_RADIUS - 1) * LEFT,
        "number_line_config": {
            "include_numbers": True,
            "x_min": -3.5,
            "x_max": 3.5,
            "unit_size": 2,
        },
        # These would override number_line_config
        "input_line_config": {
            "color": BLUE,
        },
        "output_line_config": {},
        "num_inserted_number_line_anchors": 20,
        "default_delta_x": 0.1,
        "default_sample_dot_radius": 0.07,
        "default_sample_dot_colors": [RED, YELLOW],
        "default_mapping_animation_config": {
            "run_time": 3,
            # "path_arc": 30 * DEGREES,
        },
        "zoom_factor": 0.1,
        "zoomed_display_height": 2.5,
        "zoomed_display_corner_buff": MED_SMALL_BUFF,
        "mini_line_scale_factor": 2,
        "default_coordinate_value_dx": 0.05,
    }

    def setup(self):
        ZoomedScene.setup(self)
        self.setup_number_lines()
        self.setup_titles()
        self.setup_zoomed_camera_background_rectangle()

    def setup_number_lines(self):
        number_lines = self.number_lines = VGroup()
        added_configs = (self.input_line_config, self.output_line_config)
        zero_opints = (self.input_line_zero_point, self.output_line_zero_point)
        for added_config, zero_point in zip(added_configs, zero_opints):
            full_config = dict(self.number_line_config)
            full_config.update(added_config)
            number_line = NumberLine(**full_config)
            number_line.main_line.insert_n_anchor_points(
                self.num_inserted_number_line_anchors
            )
            number_line.shift(zero_point - number_line.number_to_point(0))
            number_lines.add(number_line)
        self.input_line, self.output_line = number_lines

        self.add(number_lines)

    def setup_titles(self):
        input_title, output_title = self.titles = VGroup(*[
            TextMobject(word)
            for word in "Inputs", "Outputs"
        ])
        vects = [UP, DOWN]
        for title, line, vect in zip(self.titles, self.number_lines, vects):
            title.next_to(line, vect, aligned_edge=LEFT)
            title.shift_onto_screen()

        self.add(self.titles)

    def setup_zoomed_camera_background_rectangle(self):
        frame = self.zoomed_camera.frame
        frame.next_to(self.camera.frame, UL)
        self.zoomed_camera_background_rectangle = BackgroundRectangle(
            frame, fill_opacity=1
        )
        self.zoomed_camera_background_rectangle_anim = UpdateFromFunc(
            self.zoomed_camera_background_rectangle,
            lambda m: m.replace(frame, stretch=True)
        )
        self.zoomed_camera_background_rectangle_group = VGroup(
            self.zoomed_camera_background_rectangle,
        )

    def get_sample_input_points(self, x_min=None, x_max=None, delta_x=None):
        x_min = x_min or self.input_line.x_min
        x_max = x_max or self.input_line.x_max
        delta_x = delta_x or self.default_delta_x
        return [
            self.get_input_point(x)
            for x in np.arange(x_min, x_max + delta_x, delta_x)
        ]

    def get_sample_dots(self, x_min=None, x_max=None,
                        delta_x=None, dot_radius=None, colors=None):
        dot_radius = dot_radius or self.default_sample_dot_radius
        colors = colors or self.default_sample_dot_colors

        dots = VGroup(*[
            Dot(point, radius=dot_radius)
            for point in self.get_sample_input_points(x_min, x_max, delta_x)
        ])
        dots.set_color_by_gradient(*colors)
        return dots

    def get_local_sample_dots(self, x, sample_radius=None, **kwargs):
        if sample_radius is None:
            sample_radius = self.zoomed_camera.frame.get_width() / 2
        zoom_factor = self.get_zoom_factor()
        config = {
            "x_min": x - sample_radius,
            "x_max": x + sample_radius,
            "delta_x": self.default_delta_x * zoom_factor,
            "dot_radius": self.default_sample_dot_radius * zoom_factor,
        }
        config.update(kwargs)
        return self.get_sample_dots(**config)

    def get_local_coordinate_values(self, x, dx=None, n_neighbors=1):
        dx = dx or self.default_coordinate_value_dx
        return [
            x + n * dx
            for n in range(-n_neighbors, n_neighbors + 1)
        ]

    # Mapping animations
    def get_mapping_animation(self, func, mobject,
                              how_to_apply_func=apply_function_to_center,
                              **kwargs):
        anim_config = dict(self.default_mapping_animation_config)
        anim_config.update(kwargs)

        point_func = self.number_func_to_point_func(func)

        mobject.generate_target(use_deepcopy=True)
        how_to_apply_func(point_func, mobject.target)
        return MoveToTarget(mobject, **anim_config)

    def get_line_mapping_animation(self, func, **kwargs):
        input_line_copy = self.input_line.deepcopy()
        self.moving_input_line = input_line_copy
        input_line_copy.remove(input_line_copy.numbers)
        # input_line_copy.set_stroke(width=2)
        input_line_copy.main_line.insert_n_anchor_points(
            self.num_inserted_number_line_anchors
        )
        return AnimationGroup(
            self.get_mapping_animation(
                func, input_line_copy.main_line,
                apply_function_to_points
            ),
            self.get_mapping_animation(
                func, input_line_copy.tick_marks,
                apply_function_to_submobjects
            ),
        )

    def get_sample_dots_mapping_animation(self, func, dots, **kwargs):
        return self.get_mapping_animation(
            func, dots, how_to_apply_func=apply_function_to_submobjects
        )

    def get_zoomed_camera_frame_mapping_animation(self, func, x=None, **kwargs):
        frame = self.zoomed_camera.frame
        if x is None:
            point = frame.get_center()
        else:
            point = self.get_input_point(x)
        point_mob = VectorizedPoint(point)
        return AnimationGroup(
            self.get_mapping_animation(func, point_mob),
            UpdateFromFunc(frame, lambda m: m.move_to(point_mob)),
        )

    def apply_function(self, func,
                       sample_dots=None,
                       local_sample_dots=None,
                       target_coordinate_values=None):
        zcbr_group = self.zoomed_camera_background_rectangle_group
        zcbr_anim = self.zoomed_camera_background_rectangle_anim
        frame = self.zoomed_camera.frame

        anims = [self.get_line_mapping_animation(func)]
        if hasattr(self, "mini_line"):  # Test for if mini_line is in self?
            anims.append(self.get_mapping_animation(
                func, self.mini_line,
                how_to_apply_func=apply_function_to_center
            ))
        if sample_dots:
            anims.append(
                self.get_sample_dots_mapping_animation(func, sample_dots)
            )
        if self.zoom_activated:
            zoom_anim = self.get_zoomed_camera_frame_mapping_animation(func)
            anims.append(zoom_anim)
            anims.append(zcbr_anim)

            zoom_anim.update(1)
            target_mini_line = Line(frame.get_left(), frame.get_right())
            target_mini_line.scale(self.mini_line_scale_factor)
            target_mini_line.match_style(self.output_line.main_line)
            zoom_anim.update(0)
            zcbr_group.submobjects.insert(1, target_mini_line)
        if target_coordinate_values:
            coordinates = self.get_local_coordinates(
                self.output_line,
                *target_coordinate_values
            )
            anims.append(FadeIn(coordinates))
            zcbr_group.add(coordinates)
        if local_sample_dots:
            anims.append(
                self.get_sample_dots_mapping_animation(func, local_sample_dots)
            )
            zcbr_group.add(local_sample_dots)
        anims.append(Animation(zcbr_group))

        self.play(*anims)

    # Zooming
    def zoom_in_on_input(self, x,
                         local_sample_dots=None,
                         local_coordinate_values=None,
                         ):
        input_point = self.get_input_point(x)

        # Decide how to move camera frame into place
        frame = self.zoomed_camera.frame
        movement = ApplyMethod(frame.move_to, input_point)
        zcbr = self.zoomed_camera_background_rectangle
        zcbr_group = self.zoomed_camera_background_rectangle_group
        zcbr_anim = self.zoomed_camera_background_rectangle_anim
        anims = []
        if self.zoom_activated:
            anims.append(movement)
            anims.append(zcbr_anim)
        else:
            movement.update(1)
            zcbr_anim.update(1)
            anims.append(self.get_zoom_in_animation())
            anims.append(FadeIn(zcbr))

        # Make sure frame is in final place
        for anim in anims:
            anim.update(1)

        # Add miniature number_line
        mini_line = self.mini_line = Line(frame.get_left(), frame.get_right())
        mini_line.scale(self.mini_line_scale_factor)
        mini_line.insert_n_anchor_points(self.num_inserted_number_line_anchors)
        mini_line.match_style(self.input_line.main_line)
        mini_line_copy = mini_line.copy()
        zcbr_group.add(mini_line_copy, mini_line)
        anims += [FadeIn(mini_line), FadeIn(mini_line_copy)]

        # Add tiny coordiantes
        if local_coordinate_values is None:
            local_coordinate_values = [x]
        local_coordinates = self.get_local_coordinates(
            self.input_line,
            *local_coordinate_values
        )
        anims.append(FadeIn(local_coordinates))
        zcbr_group.add(local_coordinates)

        # Add tiny dots
        if local_sample_dots is not None:
            anims.append(LaggedStart(GrowFromCenter, local_sample_dots))
            zcbr_group.add(local_sample_dots)

        anims.append(Animation(zcbr_group))
        self.play(*anims)

        if not self.zoom_activated:
            self.activate_zooming(animate=False)
            self.play(self.get_zoomed_display_pop_out_animation())

    def get_local_coordinates(self, line, *x_values, **kwargs):
        num_decimal_places = kwargs.get("num_decimal_places", 2)
        result = VGroup()
        result.tick_marks = VGroup()
        result.numbers = VGroup()
        result.add(result.tick_marks, result.numbers)
        for x in x_values:
            tick_mark = Line(UP, DOWN)
            tick_mark.scale_to_fit_height(
                0.15 * self.zoomed_camera.frame.get_height()
            )
            tick_mark.move_to(line.number_to_point(x))
            result.tick_marks.add(tick_mark)

            number = DecimalNumber(x, num_decimal_places=num_decimal_places)
            number.scale(self.get_zoom_factor())
            number.scale(0.5)  # To make it seem small
            number.next_to(tick_mark, DOWN, buff=0.5 * number.get_height())
            result.numbers.add(number)
        return result

    def get_mobjects_in_zoomed_camera(self, mobjects):
        frame = self.zoomed_camera.frame
        x_min = frame.get_left()[0]
        x_max = frame.get_right()[0]
        y_min = frame.get_bottom()[1]
        y_max = frame.get_top()[1]
        result = VGroup()
        for mob in mobjects:
            for point in mob.get_all_points():
                if (x_min < point[0] < x_max) and (y_min < point[1] < y_max):
                    result.add(mob)
                    break
        return result

    # Helpers
    def get_input_point(self, x):
        return self.input_line.number_to_point(x)

    def get_output_point(self, fx):
        return self.output_line.number_to_point(fx)

    def number_func_to_point_func(self, number_func):
        input_line, output_line = self.number_lines

        def point_func(point):
            input_number = input_line.point_to_number(point)
            output_number = number_func(input_number)
            return output_line.number_to_point(output_number)
        return point_func


class ExampleNumberlineTransformationScene(NumberlineTransformationScene):
    CONFIG = {
        "number_line_config": {
            "x_min": 0,
            "x_max": 5,
            "unit_size": 2.0
        },
        "output_line_config": {
            "x_max": 20,
        },
    }

    def construct(self):
        func = lambda x: x**2
        x = 3
        dx = 0.05

        sample_dots = self.get_sample_dots()
        local_sample_dots = self.get_local_sample_dots(x)

        self.play(LaggedStart(GrowFromCenter, sample_dots))
        self.zoom_in_on_input(
            x,
            local_sample_dots=local_sample_dots,
            local_coordinate_values=[x - dx, x, x + dx],
        )
        self.wait()
        self.apply_function(
            func,
            sample_dots=sample_dots,
            local_sample_dots=local_sample_dots,
            target_coordinate_values=[func(x) - dx, func(x), func(x) + dx],
        )
        self.wait()


# Scenes


class WriteOpeningWords(Scene):
    def construct(self):
        raw_string1 = "Dear calculus student,"
        raw_string2 = "You're about to go through your first course. Like " + \
                      "any new topic, it will take some hard work to understand,"
        words1, words2 = [
            TextMobject("\\Large", *rs.split(" "))
            for rs in raw_string1, raw_string2
        ]
        words1.next_to(words2, UP, aligned_edge=LEFT, buff=LARGE_BUFF)
        words = VGroup(*it.chain(words1, words2))
        words.scale_to_fit_width(FRAME_WIDTH - 2 * LARGE_BUFF)
        words.to_edge(UP)

        letter_wait = 0.05
        word_wait = 2 * letter_wait
        comma_wait = 5 * letter_wait
        for word in words:
            self.play(LaggedStart(
                FadeIn, word,
                run_time=len(word) * letter_wait,
                lag_ratio=1.5 / len(word)
            ))
            self.wait(word_wait)
            if word.get_tex_string()[-1] == ",":
                self.wait(comma_wait)


class StartingCalc101(PiCreatureScene):
    CONFIG = {
    }

    def construct(self):
        randy = self.pi_creature
        deriv_equation = TexMobject(
            "\\frac{df}{dx}(x) = \\lim_{\\Delta x \\to \\infty}" +
            "{f(x + \\Delta x) - f(x) \\over \\Delta x}",
            tex_to_color_map={"\\Delta x": BLUE}
        )
        title = TextMobject("Calculus 101")
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT)
        h_line.scale_to_fit_width(FRAME_WIDTH - LARGE_BUFF)
        h_line.next_to(title, DOWN)

        self.add(title, h_line)
        self.play(randy.change, "erm", title)
        self.wait()


class StandardDerivativeVisual(GraphScene):
    CONFIG = {
        "y_max": 8,
        "y_axis_height": 5,
    }

    def construct(self):
        self.add_title()
        self.show_function_graph()
        self.show_slope_of_graph()
        self.encourage_not_to_think_of_slope_as_definition()
        self.show_sensitivity()

    def add_title(self):
        title = self.title = TextMobject("Standard derivative visual")
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT)
        h_line.scale_to_fit_width(FRAME_WIDTH - 2 * LARGE_BUFF)
        h_line.next_to(title, DOWN)

        self.add(title, h_line)

    def show_function_graph(self):
        self.setup_axes()

        def func(x):
            x -= 5
            return 0.1 * (x + 3) * (x - 3) * x + 3
        graph = self.get_graph(func)
        graph_label = self.get_graph_label(graph, x_val=9.5)

        input_tracker = ValueTracker(4)

        def get_x_value():
            return input_tracker.get_value()

        def get_y_value():
            return graph.underlying_function(get_x_value())

        def get_x_point():
            return self.coords_to_point(get_x_value(), 0)

        def get_y_point():
            return self.coords_to_point(0, get_y_value())

        def get_graph_point():
            return self.coords_to_point(get_x_value(), get_y_value())

        def get_v_line():
            return DashedLine(get_x_point(), get_graph_point(), stroke_width=2)

        def get_h_line():
            return DashedLine(get_graph_point(), get_y_point(), stroke_width=2)

        input_triangle = RegularPolygon(n=3, start_angle=TAU / 4)
        output_triangle = RegularPolygon(n=3, start_angle=0)
        for triangle in input_triangle, output_triangle:
            triangle.set_fill(WHITE, 1)
            triangle.set_stroke(width=0)
            triangle.scale(0.1)

        input_triangle_update = ContinualUpdateFromFunc(
            input_triangle, lambda m: m.move_to(get_x_point(), UP)
        )
        output_triangle_update = ContinualUpdateFromFunc(
            output_triangle, lambda m: m.move_to(get_y_point(), RIGHT)
        )

        x_label = TexMobject("x")
        x_label_update = ContinualUpdateFromFunc(
            x_label, lambda m: m.next_to(input_triangle, DOWN, SMALL_BUFF)
        )

        output_label = TexMobject("f(x)")
        output_label_update = ContinualUpdateFromFunc(
            output_label, lambda m: m.next_to(
                output_triangle, LEFT, SMALL_BUFF)
        )

        v_line = get_v_line()
        v_line_update = ContinualUpdateFromFunc(
            v_line, lambda vl: Transform(vl, get_v_line()).update(1)
        )

        h_line = get_h_line()
        h_line_update = ContinualUpdateFromFunc(
            h_line, lambda hl: Transform(hl, get_h_line()).update(1)
        )

        graph_dot = Dot(color=YELLOW)
        graph_dot_update = ContinualUpdateFromFunc(
            graph_dot, lambda m: m.move_to(get_graph_point())
        )

        self.play(
            ShowCreation(graph),
            Write(graph_label),
        )
        self.play(
            DrawBorderThenFill(input_triangle, run_time=1),
            Write(x_label),
            ShowCreation(v_line),
            GrowFromCenter(graph_dot),
        )
        self.add_foreground_mobject(graph_dot)
        self.play(
            ShowCreation(h_line),
            Write(output_label),
            DrawBorderThenFill(output_triangle, run_time=1)
        )
        self.add(
            input_triangle_update,
            x_label_update,
            graph_dot_update,
            v_line_update,
            h_line_update,
            output_triangle_update,
            output_label_update,
        )
        self.play(
            input_tracker.set_value, 8,
            run_time=6,
            rate_func=there_and_back
        )

        self.input_tracker = input_tracker
        self.graph = graph

    def show_slope_of_graph(self):
        input_tracker = self.input_tracker
        deriv_input_tracker = ValueTracker(input_tracker.get_value())

        # Slope line
        def get_slope_line():
            return self.get_secant_slope_group(
                x=deriv_input_tracker.get_value(),
                graph=self.graph,
                dx=0.01,
                secant_line_length=4
            ).secant_line

        slope_line = get_slope_line()
        slope_line_update = ContinualUpdateFromFunc(
            slope_line, lambda sg: Transform(sg, get_slope_line()).update(1)
        )

        def position_deriv_label(deriv_label):
            deriv_label.next_to(slope_line, UP)
            return deriv_label
        deriv_label = TexMobject(
            "\\frac{df}{dx}(x) =", "\\text{Slope}", "="
        )
        deriv_label.get_part_by_tex("Slope").match_color(slope_line)
        deriv_label_update = ContinualUpdateFromFunc(
            deriv_label, position_deriv_label
        )

        slope_decimal = DecimalNumber(slope_line.get_slope())
        slope_decimal.match_color(slope_line)
        slope_decimal_update = ContinualChangingDecimal(
            slope_decimal, lambda dt: slope_line.get_slope(),
            position_update_func=lambda m: m.next_to(
                deriv_label, RIGHT, SMALL_BUFF
            ).shift(0.2 * SMALL_BUFF * DOWN)
        )

        self.play(
            ShowCreation(slope_line),
            Write(deriv_label),
            Write(slope_decimal),
            run_time=1
        )
        self.wait()
        self.add(
            slope_line_update,
            # deriv_label_update,
            slope_decimal_update,
        )
        for x in 9, 2, 4:
            self.play(
                input_tracker.set_value, x,
                deriv_input_tracker.set_value, x,
                run_time=3
            )
            self.wait()

        self.deriv_input_tracker = deriv_input_tracker

    def encourage_not_to_think_of_slope_as_definition(self):
        morty = Mortimer(height=2)
        morty.to_corner(DR)

        self.play(FadeIn(morty))
        self.play(PiCreatureSays(
            morty, "Don't think of \\\\ this as the definition",
            bubble_kwargs={"height": 2, "width": 4}
        ))
        self.play(Blink(morty))
        self.wait()
        self.play(
            RemovePiCreatureBubble(morty),
            UpdateFromAlphaFunc(
                morty, lambda m, a: m.set_fill(opacity=1 - a),
                remover=True
            )
        )

    def show_sensitivity(self):
        input_tracker = self.input_tracker
        deriv_input_tracker = self.deriv_input_tracker

        self.wiggle_input()
        for x in 9, 7, 2:
            self.play(
                input_tracker.set_value, x,
                deriv_input_tracker.set_value, x,
                run_time=3
            )
            self.wiggle_input()

    ###
    def wiggle_input(self, dx=0.5, run_time=3):
        input_tracker = self.input_tracker

        x = input_tracker.get_value()
        x_min = x - dx
        x_max = x + dx
        y, y_min, y_max = map(
            self.graph.underlying_function,
            [x, x_min, x_max]
        )
        x_line = Line(
            self.coords_to_point(x_min, 0),
            self.coords_to_point(x_max, 0),
        )
        y_line = Line(
            self.coords_to_point(0, y_min),
            self.coords_to_point(0, y_max),
        )

        x_rect, y_rect = rects = VGroup(Rectangle(), Rectangle())
        rects.set_stroke(width=0)
        rects.set_fill(YELLOW, 0.5)
        x_rect.match_width(x_line)
        x_rect.stretch_to_fit_height(0.25)
        x_rect.move_to(x_line)
        y_rect.match_height(y_line)
        y_rect.stretch_to_fit_width(0.25)
        y_rect.move_to(y_line)

        self.play(
            ApplyMethod(
                input_tracker.set_value, input_tracker.get_value() + dx,
                rate_func=lambda t: wiggle(t, 6)
            ),
            FadeIn(
                rects,
                rate_func=squish_rate_func(smooth, 0, 0.33),
                remover=True,
            ),
            run_time=run_time,
        )
        self.play(FadeOut(rects))


class EoCWrapper(Scene):
    def construct(self):
        title = Title("Essence of calculus")
        self.play(Write(title))
        self.wait()


class IntroduceTransformationView(NumberlineTransformationScene):
    CONFIG = {
        "func": lambda x: 0.5 * np.sin(2 * x) + x,
        "number_line_config": {
            "x_min": 0,
            "x_max": 6,
            "unit_size": 2.0
        },
    }

    def construct(self):
        self.add_title()
        self.show_animation_preview()
        self.indicate_indicate_point_densities()
        self.show_zoomed_transformation()

    def add_title(self):
        title = self.title = TextMobject("$f(x)$ as a transformation")
        title.to_edge(UP)
        self.add(title)

    def show_animation_preview(self):
        input_points = self.get_sample_input_points()
        output_points = map(
            self.number_func_to_point_func(self.func),
            input_points
        )
        sample_dots = self.get_sample_dots()
        sample_dot_ghosts = sample_dots.copy().fade(0.5)
        arrows = VGroup(*[
            Arrow(ip, op, buff=MED_SMALL_BUFF)
            for ip, op in zip(input_points, output_points)
        ])
        arrows = arrows[1::3]
        arrows.set_stroke(BLACK, 1)

        self.play(
            LaggedStart(GrowFromCenter, sample_dots, run_time=1),
            LaggedStart(GrowArrow, arrows)
        )
        self.add(sample_dot_ghosts)
        self.apply_function(
            self.func, sample_dots=sample_dots
        )
        self.wait()
        self.play(LaggedStart(FadeOut, arrows, run_time=1))

        self.sample_dots = sample_dots
        self.sample_dot_ghosts = sample_dot_ghosts

    def indicate_indicate_point_densities(self):
        lower_brace = Brace(Line(LEFT, RIGHT), UP)
        upper_brace = lower_brace.copy()
        input_tracker = ValueTracker(0.5)
        dx = 0.5

        def update_upper_brace(brace):
            x = input_tracker.get_value()
            line = Line(
                self.get_input_point(x),
                self.get_input_point(x + dx),
            )
            brace.match_width(line, stretch=True)
            brace.next_to(line, UP, buff=SMALL_BUFF)
            return brace

        def update_lower_brace(brace):
            x = input_tracker.get_value()
            line = Line(
                self.get_output_point(self.func(x)),
                self.get_output_point(self.func(x + dx)),
            )
            brace.match_width(line, stretch=True)
            brace.next_to(line, UP, buff=SMALL_BUFF)
            return brace

        lower_brace_anim = UpdateFromFunc(lower_brace, update_lower_brace)
        upper_brace_anim = UpdateFromFunc(upper_brace, update_upper_brace)

        new_title = TextMobject(
            "$\\frac{df}{dx}(x)$ measures stretch/squishing"
        )
        new_title.move_to(self.title, UP)

        stretch_factor = DecimalNumber(0, color=YELLOW)
        stretch_factor_anim = ChangingDecimal(
            stretch_factor, lambda a: lower_brace.get_width() / upper_brace.get_width(),
            position_update_func=lambda m: m.next_to(lower_brace, UP, SMALL_BUFF)
        )

        self.play(
            GrowFromCenter(upper_brace),
            FadeOut(self.title),
            # FadeIn(new_title)
            Write(new_title, run_time=2)
        )
        self.title = new_title
        self.play(
            ReplacementTransform(upper_brace.copy(), lower_brace),
            GrowFromPoint(stretch_factor, upper_brace.get_center())
        )
        self.play(
            input_tracker.set_value, self.input_line.x_max - dx,
            lower_brace_anim,
            upper_brace_anim,
            stretch_factor_anim,
            run_time=8,
            rate_func=bezier([0, 0, 1, 1])
        )
        self.wait()

        new_sample_dots = self.get_sample_dots()
        self.play(
            FadeOut(VGroup(
                upper_brace, lower_brace, stretch_factor,
                self.sample_dots, self.moving_input_line,
            )),
            FadeIn(new_sample_dots),
        )
        self.sample_dots = new_sample_dots

    def show_zoomed_transformation(self):
        x = 2.75
        local_sample_dots = self.get_local_sample_dots(x)

        self.zoom_in_on_input(
            x,
            local_sample_dots=local_sample_dots,
            local_coordinate_values=self.get_local_coordinate_values(x),
        )
        self.wait()
        self.apply_function(
            self.func,
            sample_dots=self.sample_dots,
            local_sample_dots=local_sample_dots,
            target_coordinate_values=self.get_local_coordinate_values(self.func(x))
        )
        self.wait()


class TalkThroughXSquaredExample(IntroduceTransformationView):
    def construct(self):
        pass
