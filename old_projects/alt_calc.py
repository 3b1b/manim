 # -*- coding: utf-8 -*-
from manimlib.imports import *


def apply_function_to_center(point_func, mobject):
    mobject.apply_function_to_position(point_func)


def apply_function_to_submobjects(point_func, mobject):
    mobject.apply_function_to_submobject_positions(point_func)


def apply_function_to_points(point_func, mobject):
    mobject.apply_function(point_func)


def get_nested_one_plus_one_over_x(n_terms, bottom_term="x"):
    tex = "1+ {1 \\over" * n_terms + bottom_term + "}" * n_terms
    return TexMobject(tex, substrings_to_isolate=["1", "\\over", bottom_term])


def get_phi_continued_fraction(n_terms):
    return get_nested_one_plus_one_over_x(n_terms, bottom_term="1+\\cdots")


def get_nested_f(n_terms, arg="x"):
    terms = ["f("] * n_terms + [arg] + [")"] * n_terms
    return TexMobject(*terms)


# Scene types

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
        "num_inserted_number_line_curves": 20,
        "default_delta_x": 0.1,
        "default_sample_dot_radius": 0.07,
        "default_sample_dot_colors": [RED, YELLOW],
        "default_mapping_animation_config": {
            "run_time": 3,
            # "path_arc": 30 * DEGREES,
        },
        "local_coordinate_num_decimal_places": 2,
        "zoom_factor": 0.1,
        "zoomed_display_height": 2.5,
        "zoomed_display_corner_buff": MED_SMALL_BUFF,
        "mini_line_scale_factor": 2,
        "default_coordinate_value_dx": 0.05,
        "zoomed_camera_background_rectangle_fill_opacity": 1.0,
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
            number_line.insert_n_curves(
                self.num_inserted_number_line_curves
            )
            number_line.shift(zero_point - number_line.number_to_point(0))
            number_lines.add(number_line)
        self.input_line, self.output_line = number_lines

        self.add(number_lines)

    def setup_titles(self):
        input_title, output_title = self.titles = VGroup(*[
            TextMobject(word)
            for word in ("Inputs", "Outputs")
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
            frame, fill_opacity=self.zoomed_camera_background_rectangle_fill_opacity
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
        zoom_factor = self.get_zoom_factor()
        delta_x = kwargs.get("delta_x", self.default_delta_x * zoom_factor)
        dot_radius = kwargs.get("dot_radius", self.default_sample_dot_radius * zoom_factor)

        if sample_radius is None:
            unrounded_radius = self.zoomed_camera.frame.get_width() / 2
            sample_radius = int(unrounded_radius / delta_x) * delta_x
        config = {
            "x_min": x - sample_radius,
            "x_max": x + sample_radius,
            "delta_x": delta_x,
            "dot_radius": dot_radius,
        }
        config.update(kwargs)
        return self.get_sample_dots(**config)

    def add_sample_dot_ghosts(self, sample_dots, fade_factor=0.5):
        self.sample_dot_ghosts = sample_dots.copy()
        self.sample_dot_ghosts.fade(fade_factor)
        self.add(self.sample_dot_ghosts, sample_dots)

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
        input_line_copy.insert_n_curves(
            self.num_inserted_number_line_curves
        )
        return AnimationGroup(
            self.get_mapping_animation(
                func, input_line_copy,
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
                       apply_function_to_number_line=True,
                       sample_dots=None,
                       local_sample_dots=None,
                       target_coordinate_values=None,
                       added_anims=None,
                       **kwargs
                       ):
        zcbr_group = self.zoomed_camera_background_rectangle_group
        zcbr_anim = self.zoomed_camera_background_rectangle_anim
        frame = self.zoomed_camera.frame

        anims = []
        if apply_function_to_number_line:
            anims.append(self.get_line_mapping_animation(func))
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
            target_mini_line.match_style(self.output_line)
            zoom_anim.update(0)
            zcbr_group.submobjects.insert(1, target_mini_line)
        if target_coordinate_values:
            coordinates = self.get_local_coordinates(
                self.output_line,
                *target_coordinate_values
            )
            anims.append(FadeIn(coordinates))
            zcbr_group.add(coordinates)
            self.local_target_coordinates = coordinates
        if local_sample_dots:
            anims.append(
                self.get_sample_dots_mapping_animation(func, local_sample_dots)
            )
            zcbr_group.add(local_sample_dots)
        if added_anims:
            anims += added_anims
        anims.append(Animation(zcbr_group))

        self.play(*anims, **kwargs)

    # Zooming
    def zoom_in_on_input(self, x,
                         local_sample_dots=None,
                         local_coordinate_values=None,
                         pop_out=True,
                         first_added_anims=None,
                         first_anim_kwargs=None,
                         second_added_anims=None,
                         second_anim_kwargs=None,
                         zoom_factor=None,
                         ):

        first_added_anims = first_added_anims or []
        first_anim_kwargs = first_anim_kwargs or {}
        second_added_anims = second_added_anims or []
        second_anim_kwargs = second_anim_kwargs or {}
        input_point = self.get_input_point(x)

        # Decide how to move camera frame into place
        frame = self.zoomed_camera.frame
        frame.generate_target()
        frame.target.move_to(input_point)
        if zoom_factor:
            frame.target.set_height(
                self.zoomed_display.get_height() * zoom_factor
            )
        movement = MoveToTarget(frame)
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
        mini_line.insert_n_curves(self.num_inserted_number_line_curves)
        mini_line.match_style(self.input_line)
        mini_line_copy = mini_line.copy()
        zcbr_group.add(mini_line_copy, mini_line)
        anims += [FadeIn(mini_line), FadeIn(mini_line_copy)]

        # Add tiny coordinates
        if local_coordinate_values is None:
            local_coordinate_values = [x]
        local_coordinates = self.get_local_coordinates(
            self.input_line,
            *local_coordinate_values
        )
        anims.append(FadeIn(local_coordinates))
        zcbr_group.add(local_coordinates)
        self.local_coordinates = local_coordinates

        # Add tiny dots
        if local_sample_dots is not None:
            anims.append(LaggedStartMap(GrowFromCenter, local_sample_dots))
            zcbr_group.add(local_sample_dots)

        if first_added_anims:
            anims += first_added_anims

        anims.append(Animation(zcbr_group))
        if not pop_out:
            self.activate_zooming(animate=False)
        self.play(*anims, **first_anim_kwargs)

        if not self.zoom_activated and pop_out:
            self.activate_zooming(animate=False)
            added_anims = second_added_anims or []
            self.play(
                self.get_zoomed_display_pop_out_animation(),
                *added_anims,
                **second_anim_kwargs
            )

    def get_local_coordinates(self, line, *x_values, **kwargs):
        num_decimal_places = kwargs.get(
            "num_decimal_places", self.local_coordinate_num_decimal_places
        )
        result = VGroup()
        result.tick_marks = VGroup()
        result.numbers = VGroup()
        result.add(result.tick_marks, result.numbers)
        for x in x_values:
            tick_mark = Line(UP, DOWN)
            tick_mark.set_height(
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

        self.play(LaggedStartMap(GrowFromCenter, sample_dots))
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
            for rs in (raw_string1, raw_string2)
        ]
        words1.next_to(words2, UP, aligned_edge=LEFT, buff=LARGE_BUFF)
        words = VGroup(*it.chain(words1, words2))
        words.set_width(FRAME_WIDTH - 2 * LARGE_BUFF)
        words.to_edge(UP)

        letter_wait = 0.05
        word_wait = 2 * letter_wait
        comma_wait = 5 * letter_wait
        for word in words:
            self.play(LaggedStartMap(
                FadeIn, word,
                run_time=len(word) * letter_wait,
                lag_ratio=1.5 / len(word)
            ))
            self.wait(word_wait)
            if word.get_tex_string()[-1] == ",":
                self.wait(comma_wait)


class StartingCalc101(PiCreatureScene):
    CONFIG = {
        "camera_config": {"background_opacity": 1},
        "image_frame_width": 3.5,
        "image_frame_height": 2.5,
    }

    def construct(self):
        self.show_you()
        self.show_images()
        self.show_mystery_topic()

    def show_you(self):
        randy = self.pi_creature
        title = self.title = Title("Calculus 101")
        you = TextMobject("You")
        arrow = Vector(DL, color=WHITE)
        arrow.next_to(randy, UR)
        you.next_to(arrow.get_start(), UP)

        self.play(
            Write(you),
            GrowArrow(arrow),
            randy.change, "erm", title
        )
        self.wait()
        self.play(Write(title, run_time=1))
        self.play(FadeOut(VGroup(arrow, you)))

    def show_images(self):
        randy = self.pi_creature
        images = self.get_all_images()
        modes = [
            "pondering",  # hard_work_image
            "pondering",  # neat_example_image
            "hesitant",  # not_so_neat_example_image
            "hesitant",  # physics_image
            "horrified",  # piles_of_formulas_image
            "horrified",  # getting_stuck_image
            "thinking",  # aha_image
            "thinking",  # graphical_intuition_image
        ]

        for i, image, mode in zip(it.count(), images, modes):
            anims = []
            if hasattr(image, "fade_in_anim"):
                anims.append(image.fade_in_anim)
                anims.append(FadeIn(image.frame))
            else:
                anims.append(FadeIn(image))

            if i >= 3:
                image_to_fade_out = images[i - 3]
                if hasattr(image_to_fade_out, "fade_out_anim"):
                    anims.append(image_to_fade_out.fade_out_anim)
                else:
                    anims.append(FadeOut(image_to_fade_out))

            if hasattr(image, "continual_animations"):
                self.add(*image.continual_animations)

            anims.append(ApplyMethod(randy.change, mode))
            self.play(*anims)
            self.wait()
            if i >= 3:
                if hasattr(image_to_fade_out, "continual_animations"):
                    self.remove(*image_to_fade_out.continual_animations)
                self.remove(image_to_fade_out.frame)
        self.wait(3)

        self.remaining_images = images[-3:]

    def show_mystery_topic(self):
        images = self.remaining_images
        randy = self.pi_creature

        mystery_box = Rectangle(
            width=self.image_frame_width,
            height=self.image_frame_height,
            stroke_color=YELLOW,
            fill_color=DARK_GREY,
            fill_opacity=0.5,
        )
        mystery_box.scale(1.5)
        mystery_box.next_to(self.title, DOWN, MED_LARGE_BUFF)

        rects = images[-1].rects.copy()
        rects.center()
        rects.set_height(FRAME_HEIGHT - 1)
        # image = rects.get_image()
        open_cv_image = cv2.imread(get_full_raster_image_path("alt_calc_hidden_image"))
        blurry_iamge = cv2.blur(open_cv_image, (50, 50))
        array = np.array(blurry_iamge)[:, :, ::-1]
        im_mob = ImageMobject(array)
        im_mob.replace(mystery_box, stretch=True)
        mystery_box.add(im_mob)

        q_marks = TexMobject("???").scale(3)
        q_marks.space_out_submobjects(1.5)
        q_marks.set_stroke(BLACK, 1)
        q_marks.move_to(mystery_box)
        mystery_box.add(q_marks)

        for image in images:
            if hasattr(image, "continual_animations"):
                self.remove(*image.continual_animations)
            self.play(
                image.shift, DOWN,
                image.fade, 1,
                randy.change, "erm",
                run_time=1.5
            )
            self.remove(image)
        self.wait()
        self.play(
            FadeInFromDown(mystery_box),
            randy.change, "confused"
        )
        self.wait(5)

    # Helpers

    def get_all_images(self):
        # Images matched to narration's introductory list
        images = VGroup(
            self.get_hard_work_image(),
            self.get_neat_example_image(),
            self.get_not_so_neat_example_image(),
            self.get_physics_image(),
            self.get_piles_of_formulas_image(),
            self.get_getting_stuck_image(),
            self.get_aha_image(),
            self.get_graphical_intuition_image(),
        )
        colors = color_gradient([BLUE, YELLOW], len(images))
        for i, image, color in zip(it.count(), images, colors):
            self.adjust_size(image)
            frame = Rectangle(
                width=self.image_frame_width,
                height=self.image_frame_height,
                color=color,
                stroke_width=2,
            )
            frame.move_to(image)
            image.frame = frame
            image.add(frame)
            image.next_to(self.title, DOWN)
            alt_i = (i % 3) - 1
            vect = (self.image_frame_width + LARGE_BUFF) * RIGHT
            image.shift(alt_i * vect)
        return images

    def adjust_size(self, group):
        group.set_width(min(
            group.get_width(),
            self.image_frame_width - 2 * MED_SMALL_BUFF
        ))
        group.set_height(min(
            group.get_height(),
            self.image_frame_height - 2 * MED_SMALL_BUFF
        ))
        return group

    def get_hard_work_image(self):
        new_randy = self.pi_creature.copy()
        new_randy.change_mode("telepath")
        bubble = new_randy.get_bubble(height=3.5, width=4)
        bubble.add_content(TexMobject("\\frac{d}{dx}(\\sin(\\sqrt{x}))"))
        bubble.add(bubble.content)  # Remove?

        return VGroup(new_randy, bubble)

    def get_neat_example_image(self):
        filled_circle = Circle(
            stroke_width=0,
            fill_color=BLUE_E,
            fill_opacity=1
        )
        area = TexMobject("\\pi r^2")
        area.move_to(filled_circle)
        unfilled_circle = Circle(
            stroke_width=3,
            stroke_color=YELLOW,
            fill_opacity=0,
        )
        unfilled_circle.next_to(filled_circle, RIGHT)
        circles = VGroup(filled_circle, unfilled_circle)
        circumference = TexMobject("2\\pi r")
        circumference.move_to(unfilled_circle)
        equation = TexMobject(
            "{d (\\pi r^2) \\over dr}  = 2\\pi r",
            tex_to_color_map={
                "\\pi r^2": BLUE_D,
                "2\\pi r": YELLOW,
            }
        )
        equation.next_to(circles, UP)

        return VGroup(
            filled_circle, area,
            unfilled_circle, circumference,
            equation
        )

    def get_not_so_neat_example_image(self):
        return TexMobject("\\int x \\cos(x) \\, dx")

    def get_physics_image(self):
        t_max = 6.5
        r = 0.2
        spring = ParametricFunction(
            lambda t: op.add(
                r * (np.sin(TAU * t) * RIGHT + np.cos(TAU * t) * UP),
                t * DOWN,
            ),
            t_min=0, t_max=t_max,
            color=WHITE,
            stroke_width=2,
        )
        spring.color_using_background_image("grey_gradient")

        weight = Square()
        weight.set_stroke(width=0)
        weight.set_fill(opacity=1)
        weight.color_using_background_image("grey_gradient")
        weight.set_height(0.4)

        t_tracker = ValueTracker(0)
        group = VGroup(spring, weight)
        group.continual_animations = [
            t_tracker.add_udpater(
                lambda tracker, dt: tracker.set_value(
                    tracker.get_value() + dt
                )
            ),
            spring.add_updater(
                lambda s: s.stretch_to_fit_height(
                    1.5 + 0.5 * np.cos(3 * t_tracker.get_value()),
                    about_edge=UP
                )
            ),
            weight.add_updater(
                lambda w: w.move_to(spring.points[-1])
            )
        ]

        def update_group_style(alpha):
            spring.set_stroke(width=2 * alpha)
            weight.set_fill(opacity=alpha)

        group.fade_in_anim = UpdateFromAlphaFunc(
            group,
            lambda g, a: update_group_style(a)
        )
        group.fade_out_anim = UpdateFromAlphaFunc(
            group,
            lambda g, a: update_group_style(1 - a)
        )
        return group

    def get_piles_of_formulas_image(self):
        return TexMobject("(f/g)' = \\frac{gf' - fg'}{g^2}")

    def get_getting_stuck_image(self):
        creature = self.pi_creature.copy()
        creature.change_mode("angry")
        equation = TexMobject("\\frac{d}{dx}(x^x)")
        equation.set_height(creature.get_height() / 2)
        equation.next_to(creature, RIGHT, aligned_edge=UP)
        creature.look_at(equation)
        return VGroup(creature, equation)

    def get_aha_image(self):
        creature = self.pi_creature.copy()
        creature.change_mode("hooray")
        from old_projects.eoc.chapter3 import NudgeSideLengthOfCube
        scene = NudgeSideLengthOfCube(
            end_at_animation_number=7,
            skip_animations=True
        )
        group = VGroup(
            scene.cube, scene.faces,
            scene.bars, scene.corner_cube,
        )
        group.set_height(0.75 * creature.get_height())
        group.next_to(creature, RIGHT)
        creature.look_at(group)
        return VGroup(creature, group)

    def get_graphical_intuition_image(self):
        gs = GraphScene()
        gs.setup_axes()
        graph = gs.get_graph(
            lambda x: 0.2 * (x - 3) * (x - 5) * (x - 6) + 4,
            x_min=2, x_max=8,
        )
        rects = gs.get_riemann_rectangles(
            graph, x_min=2, x_max=8,
            stroke_width=0.5,
            dx=0.25
        )
        gs.add(graph, rects, gs.axes)
        group = VGroup(*gs.mobjects)
        self.adjust_size(group)
        group.next_to(self.title, DOWN, MED_LARGE_BUFF)
        group.rects = rects
        group.continual_animations = [
            turn_animation_into_updater(Write(rects)),
            turn_animation_into_updater(ShowCreation(graph)),
            turn_animation_into_updater(FadeIn(gs.axes)),
        ]
        self.adjust_size(group)
        return group


class GraphicalIntuitions(GraphScene):
    CONFIG = {
        "func": lambda x: 0.1 * (x - 2) * (x - 5) * (x - 7) + 4,
        "x_labeled_nums": list(range(1, 10)),
    }

    def construct(self):
        self.setup_axes()
        axes = self.axes
        graph = self.get_graph(self.func)

        ss_group = self.get_secant_slope_group(
            x=8, graph=graph, dx=0.01,
            secant_line_length=6,
            secant_line_color=RED,
        )
        rects = self.get_riemann_rectangles(
            graph, x_min=2, x_max=8, dx=0.01, stroke_width=0
        )

        deriv_text = TextMobject(
            "Derivative $\\rightarrow$ slope",
            tex_to_color_map={"slope": ss_group.secant_line.get_color()}
        )
        deriv_text.to_edge(UP)
        integral_text = TextMobject(
            "Integral $\\rightarrow$ area",
            tex_to_color_map={"area": rects[0].get_color()}
        )
        integral_text.next_to(deriv_text, DOWN)

        self.play(
            Succession(Write(axes), ShowCreation(graph, run_time=2)),
            self.get_graph_words_anim(),
        )
        self.animate_secant_slope_group_change(
            ss_group,
            target_x=2,
            rate_func=smooth,
            run_time=2.5,
            added_anims=[
                Write(deriv_text),
                VFadeIn(ss_group, run_time=2),
            ]
        )
        self.play(FadeIn(integral_text))
        self.play(
            LaggedStartMap(
                GrowFromEdge, rects,
                lambda r: (r, DOWN)
            ),
            Animation(axes),
            Animation(graph),
        )
        self.wait()

    def get_graph_words_anim(self):
        words = VGroup(
            TextMobject("Graphs,"),
            TextMobject("graphs,"),
            TextMobject("non-stop graphs"),
            TextMobject("all day"),
            TextMobject("every day"),
            TextMobject("as if to visualize is to graph"),
        )
        for word in words:
            word.add_background_rectangle()
        words.arrange(DOWN)
        words.to_edge(UP)
        return LaggedStartMap(
            FadeIn, words,
            rate_func=there_and_back,
            run_time=len(words) - 1,
            lag_ratio=0.6,
            remover=True
        )


class Wrapper(Scene):
    CONFIG = {
        "title": "",
        "title_kwargs": {},
        "screen_height": 6,
        "wait_time": 2,
    }

    def construct(self):
        rect = self.rect = ScreenRectangle(height=self.screen_height)
        title = self.title = TextMobject(self.title, **self.title_kwargs)
        title.to_edge(UP)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait(self.wait_time)


class DomainColoringWrapper(Wrapper):
    CONFIG = {
        "title": "Complex $\\rightarrow$ Complex",
    }


class R2ToR2Wrapper(Wrapper):
    CONFIG = {"title": "$\\mathds{R}^2 \\rightarrow \\mathds{R}^2$"}


class ExampleMultivariableFunction(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors": False,
        "show_coordinates": True,
    }

    def construct(self):
        def example_function(point):
            x, y, z = point
            return np.array([
                x + np.sin(y),
                y + np.sin(x),
                0
            ])
        self.wait()
        self.apply_nonlinear_transformation(example_function, run_time=5)
        self.wait()


class ChangingVectorFieldWrapper(Wrapper):
    CONFIG = {"title": "$(x, y, t) \\rightarrow (x', y')$"}


class ChangingVectorField(Scene):
    CONFIG = {
        "wait_time": 30,
    }

    def construct(self):
        plane = self.plane = NumberPlane()
        plane.set_stroke(width=2)
        plane.add_coordinates()
        self.add(plane)

        # Obviously a silly thing to do, but I'm sweeping
        # through trying to make sure old scenes don't
        # completely break in spots which used to have
        # Continual animations
        time_tracker = self.time_tracker = ValueTracker(0)
        time_tracker.add_updater(
            lambda t: t.set_value(self.get_time())
        )

        vectors = self.get_vectors()
        vectors.add_updater(self.update_vectors)
        self.add(vectors)
        self.wait(self.wait_time)

    def get_vectors(self):
        vectors = VGroup()
        x_max = int(np.ceil(FRAME_WIDTH))
        y_max = int(np.ceil(FRAME_HEIGHT))
        step = 0.5
        for x in np.arange(-x_max, x_max + 1, step):
            for y in np.arange(-y_max, y_max + 1, step):
                point = x * RIGHT + y * UP
                vectors.add(Vector(RIGHT).shift(point))
        vectors.set_color_by_gradient(YELLOW, RED)
        return vectors

    def update_vectors(self, vectors):
        time = self.time_tracker.get_value()
        for vector in vectors:
            point = vector.get_start()
            out_point = self.func(point, time)
            norm = get_norm(out_point)
            if norm == 0:
                out_point = RIGHT  # Fake it
                vector.set_fill(opacity=0)
            else:
                out_point *= 0.5
                color = interpolate_color(BLUE, RED, norm / np.sqrt(8))
                vector.set_fill(color, opacity=1)
                vector.set_stroke(BLACK, width=1)
            new_x, new_y = out_point[:2]
            vector.put_start_and_end_on(
                point, point + new_x * RIGHT + new_y * UP
            )

    def func(self, point, time):
        x, y, z = point
        return np.array([
            np.sin(time + 0.5 * x + y),
            np.cos(time + 0.2 * x * y + 0.7),
            0
        ])


class MoreTopics(Scene):
    def construct(self):
        calculus = TextMobject("Calculus")
        calculus.next_to(LEFT, LEFT)
        calculus.set_color(YELLOW)
        calculus.add_background_rectangle()
        others = VGroup(
            TextMobject("Multivariable calculus"),
            TextMobject("Complex analysis"),
            TextMobject("Differential geometry"),
            TextMobject("$\\vdots$")
        )
        for word in others:
            word.add_background_rectangle()
        others.arrange(
            DOWN, buff=MED_LARGE_BUFF, aligned_edge=LEFT,
        )
        others.next_to(RIGHT, RIGHT)
        lines = VGroup(*[
            Line(calculus.get_right(), word.get_left(), buff=MED_SMALL_BUFF)
            for word in others
        ])

        rect = FullScreenFadeRectangle(fill_opacity=0.7)
        self.add(rect)

        self.add(calculus)
        self.play(
            LaggedStartMap(ShowCreation, lines),
            LaggedStartMap(Write, others),
        )
        self.wait()

        self.calculus = calculus
        self.lines = lines
        self.full_screen_rect = rect
        self.other_topics = others


class TransformationalViewWrapper(Wrapper):
    CONFIG = {
        "title": "Transformational view"
    }


class SetTheStage(TeacherStudentsScene):
    def construct(self):
        ordinary = TextMobject("Ordinary visual")
        transformational = TextMobject("Transformational visual")
        for word in ordinary, transformational:
            word.move_to(self.hold_up_spot, DOWN)
            word.shift_onto_screen()

        self.screen.scale(1.25, about_edge=UL)
        self.add(self.screen)
        self.teacher_holds_up(
            ordinary,
            added_anims=[self.get_student_changes(*3 * ["sassy"])]
        )
        self.wait()
        self.play(
            ordinary.shift, UP,
            FadeInFromDown(transformational),
            self.teacher.change, "hooray",
            self.get_student_changes(*3 * ["erm"])
        )
        self.wait(3)
        self.change_all_student_modes("pondering", look_at_arg=self.screen)


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
        h_line.set_width(FRAME_WIDTH - 2 * LARGE_BUFF)
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

        input_triangle_update = input_tracker.add_updater(
            lambda m: m.move_to(get_x_point(), UP)
        )
        output_triangle_update = output_triangle.add_updater(
            lambda m: m.move_to(get_y_point(), RIGHT)
        )

        x_label = TexMobject("x")
        x_label_update = Mobject.add_updater(
            x_label, lambda m: m.next_to(input_triangle, DOWN, SMALL_BUFF)
        )

        output_label = TexMobject("f(x)")
        output_label_update = Mobject.add_updater(
            output_label, lambda m: m.next_to(
                output_triangle, LEFT, SMALL_BUFF)
        )

        v_line = get_v_line()
        v_line_update = Mobject.add_updater(
            v_line, lambda vl: Transform(vl, get_v_line()).update(1)
        )

        h_line = get_h_line()
        h_line_update = Mobject.add_updater(
            h_line, lambda hl: Transform(hl, get_h_line()).update(1)
        )

        graph_dot = Dot(color=YELLOW)
        graph_dot_update = Mobject.add_updater(
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
        slope_line_update = Mobject.add_updater(
            slope_line, lambda sg: Transform(sg, get_slope_line()).update(1)
        )

        def position_deriv_label(deriv_label):
            deriv_label.next_to(slope_line, UP)
            return deriv_label
        deriv_label = TexMobject(
            "\\frac{df}{dx}(x) =", "\\text{Slope}", "="
        )
        deriv_label.get_part_by_tex("Slope").match_color(slope_line)
        deriv_label_update = Mobject.add_updater(
            deriv_label, position_deriv_label
        )

        slope_decimal = DecimalNumber(slope_line.get_slope())
        slope_decimal.match_color(slope_line)
        slope_decimal.add_updater(
            lambda d: d.set_value(slope_line.get_slope())
        )
        slope_decimal.add_upater(
            lambda d: d.next_to(
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
        y, y_min, y_max = list(map(
            self.graph.underlying_function,
            [x, x_min, x_max]
        ))
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
        output_points = list(map(
            self.number_func_to_point_func(self.func),
            input_points
        ))
        sample_dots = self.get_sample_dots()
        sample_dot_ghosts = sample_dots.copy().fade(0.5)
        arrows = VGroup(*[
            Arrow(ip, op, buff=MED_SMALL_BUFF)
            for ip, op in zip(input_points, output_points)
        ])
        arrows = arrows[1::3]
        arrows.set_stroke(BLACK, 1)

        for sd in sample_dots:
            sd.save_state()
            sd.scale(2)
            sd.fade(1)
        self.play(LaggedStartMap(
            ApplyMethod, sample_dots,
            lambda sd: (sd.restore,),
            run_time=2
        ))
        self.play(LaggedStartMap(
            GrowArrow, arrows,
            run_time=6,
            lag_ratio=0.3,
        ))
        self.add(sample_dot_ghosts)
        self.apply_function(
            self.func, sample_dots=sample_dots,
            run_time=3
        )
        self.wait()
        self.play(LaggedStartMap(FadeOut, arrows, run_time=1))

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


class ExamplePlease(TeacherStudentsScene):
    def construct(self):
        self.student_says("Example?", student_index=0)
        self.teacher_holds_up(TexMobject("f(x) = x^2").scale(1.5))
        self.wait(2)


class TalkThroughXSquaredExample(IntroduceTransformationView):
    CONFIG = {
        "func": lambda x: x**2,
        "number_line_config": {
            "x_min": 0,
            "x_max": 5,
            "unit_size": 1.25,
        },
        "output_line_config": {
            "x_max": 25,
        },
        "default_delta_x": 0.2
    }

    def construct(self):
        self.add_title()
        self.show_specific_points_mapping()

    def add_title(self):
        title = self.title = TextMobject("$f(x) = x^2$")
        title.to_edge(UP, buff=MED_SMALL_BUFF)
        self.add(title)

    def show_specific_points_mapping(self):
        # First, just show integers as examples
        int_dots = self.get_sample_dots(1, 6, 1)
        int_dot_ghosts = int_dots.copy().fade(0.5)
        int_arrows = VGroup(*[
            Arrow(
                # num.get_bottom(),
                self.get_input_point(x),
                self.get_output_point(self.func(x)),
                buff=MED_SMALL_BUFF
            )
            for x, num in zip(list(range(1, 6)), self.input_line.numbers[1:])
        ])
        point_func = self.number_func_to_point_func(self.func)

        numbers = self.input_line.numbers
        numbers.next_to(self.input_line, UP, SMALL_BUFF)
        self.titles[0].next_to(numbers, UP, MED_SMALL_BUFF, LEFT)
        # map(TexMobject.add_background_rectangle, numbers)
        # self.add_foreground_mobject(numbers)

        for dot, dot_ghost, arrow in zip(int_dots, int_dot_ghosts, int_arrows):
            arrow.match_color(dot)
            self.play(DrawBorderThenFill(dot, run_time=1))
            self.add(dot_ghost)
            self.play(
                GrowArrow(arrow),
                dot.apply_function_to_position, point_func
            )
        self.wait()

        # Show more sample_dots
        sample_dots = self.get_sample_dots()
        sample_dot_ghosts = sample_dots.copy().fade(0.5)

        self.play(
            LaggedStartMap(DrawBorderThenFill, sample_dots),
            LaggedStartMap(FadeOut, int_arrows),
        )
        self.remove(int_dot_ghosts)
        self.add(sample_dot_ghosts)
        self.apply_function(self.func, sample_dots=sample_dots)
        self.remove(int_dots)
        self.wait()

        self.sample_dots = sample_dots
        self.sample_dot_ghosts = sample_dot_ghosts

    def get_stretch_words(self, factor, color=RED, less_than_one=False):
        factor_str = "$%s$" % str(factor)
        result = TextMobject(
            "Scale \\\\ by", factor_str,
            tex_to_color_map={factor_str: color}
        )
        result.scale(0.7)
        la, ra = TexMobject("\\leftarrow \\rightarrow")
        if less_than_one:
            la, ra = ra, la
        if factor < 0:
            kwargs = {
                "path_arc": np.pi,
            }
            la = Arrow(UP, DOWN, **kwargs)
            ra = Arrow(DOWN, UP, **kwargs)
            for arrow in la, ra:
                arrow.pointwise_become_partial(arrow, 0, 0.9)
                arrow.tip.scale(2)
            VGroup(la, ra).match_height(result)
        la.next_to(result, LEFT)
        ra.next_to(result, RIGHT)
        result.add(la, ra)
        result.next_to(
            self.zoomed_display.get_top(), DOWN, SMALL_BUFF
        )
        return result

    def get_deriv_equation(self, x, rhs, color=RED):
        deriv_equation = self.deriv_equation = TexMobject(
            "\\frac{df}{dx}(", str(x), ")", "=", str(rhs),
            tex_to_color_map={str(x): color, str(rhs): color}
        )
        deriv_equation.next_to(self.title, DOWN, MED_LARGE_BUFF)
        return deriv_equation


class ZoomInOnXSquaredNearOne(TalkThroughXSquaredExample):
    def setup(self):
        TalkThroughXSquaredExample.setup(self)
        self.force_skipping()
        self.add_title()
        self.show_specific_points_mapping()
        self.revert_to_original_skipping_status()

    def construct(self):
        zoom_words = TextMobject("Zoomed view \\\\ near 1")
        zoom_words.next_to(self.zoomed_display, DOWN)
        # zoom_words.shift_onto_screen()

        x = 1
        local_sample_dots = self.get_local_sample_dots(x)
        local_coords = self.get_local_coordinate_values(x, dx=0.1)

        zcbr_anim = self.zoomed_camera_background_rectangle_anim
        zcbr_group = self.zoomed_camera_background_rectangle_group
        frame = self.zoomed_camera.frame
        sample_dot_ghost_copies = self.sample_dot_ghosts.copy()

        self.zoom_in_on_input(x, local_sample_dots, local_coords)
        self.play(FadeIn(zoom_words))
        self.wait()
        local_sample_dots.save_state()
        frame.save_state()
        self.mini_line.save_state()
        self.apply_function(
            self.func,
            apply_function_to_number_line=False,
            sample_dots=sample_dot_ghost_copies,
            local_sample_dots=local_sample_dots,
            target_coordinate_values=local_coords
        )
        self.remove(sample_dot_ghost_copies)
        self.wait()

        # Go back
        self.play(
            frame.restore,
            self.mini_line.restore,
            local_sample_dots.restore,
            zcbr_anim,
            Animation(zcbr_group)
        )
        self.wait()

        # Zoom in even more
        extra_zoom_factor = 0.3
        one_group = VGroup(
            self.local_coordinates.tick_marks[1],
            self.local_coordinates.numbers[1],
        )
        all_other_coordinates = VGroup(
            self.local_coordinates.tick_marks[::2],
            self.local_coordinates.numbers[::2],
            self.local_target_coordinates,
        )
        self.play(frame.scale, extra_zoom_factor)
        new_local_sample_dots = self.get_local_sample_dots(x, delta_x=0.005)
        new_coordinate_values = self.get_local_coordinate_values(x, dx=0.02)
        new_local_coordinates = self.get_local_coordinates(
            self.input_line, *new_coordinate_values
        )

        self.play(
            Write(new_local_coordinates),
            Write(new_local_sample_dots),
            one_group.scale, extra_zoom_factor, {"about_point": self.get_input_point(1)},
            FadeOut(all_other_coordinates),
            *[
                ApplyMethod(dot.scale, extra_zoom_factor)
                for dot in local_sample_dots
            ]
        )
        self.remove(one_group, local_sample_dots)
        zcbr_group.remove(
            self.local_coordinates, self.local_target_coordinates,
            local_sample_dots
        )

        # Transform new zoomed view
        stretch_by_two_words = self.get_stretch_words(2)
        self.add_foreground_mobject(stretch_by_two_words)
        sample_dot_ghost_copies = self.sample_dot_ghosts.copy()
        self.apply_function(
            self.func,
            apply_function_to_number_line=False,
            sample_dots=sample_dot_ghost_copies,
            local_sample_dots=new_local_sample_dots,
            target_coordinate_values=new_coordinate_values,
            added_anims=[FadeIn(stretch_by_two_words)]
        )
        self.remove(sample_dot_ghost_copies)
        self.wait()

        # Write derivative
        deriv_equation = self.get_deriv_equation(1, 2, color=RED)
        self.play(Write(deriv_equation))
        self.wait()


class ZoomInOnXSquaredNearThree(ZoomInOnXSquaredNearOne):
    CONFIG = {
        "zoomed_display_width": 4,
    }

    def construct(self):
        zoom_words = TextMobject("Zoomed view \\\\ near 3")
        zoom_words.next_to(self.zoomed_display, DOWN)

        x = 3
        local_sample_dots = self.get_local_sample_dots(x)
        local_coordinate_values = self.get_local_coordinate_values(x, dx=0.1)
        target_coordinate_values = self.get_local_coordinate_values(self.func(x), dx=0.1)

        color = self.sample_dots[len(self.sample_dots) / 2].get_color()
        sample_dot_ghost_copies = self.sample_dot_ghosts.copy()
        stretch_words = self.get_stretch_words(2 * x, color)
        deriv_equation = self.get_deriv_equation(x, 2 * x, color)

        self.add(deriv_equation)
        self.zoom_in_on_input(
            x,
            pop_out=False,
            local_sample_dots=local_sample_dots,
            local_coordinate_values=local_coordinate_values
        )
        self.play(Write(zoom_words, run_time=1))
        self.wait()
        self.add_foreground_mobject(stretch_words)
        self.apply_function(
            self.func,
            apply_function_to_number_line=False,
            sample_dots=sample_dot_ghost_copies,
            local_sample_dots=local_sample_dots,
            target_coordinate_values=target_coordinate_values,
            added_anims=[Write(stretch_words)]
        )
        self.wait(2)


class ZoomInOnXSquaredNearOneFourth(ZoomInOnXSquaredNearOne):
    CONFIG = {
        "zoom_factor": 0.01,
        "local_coordinate_num_decimal_places": 4,
        "zoomed_display_width": 4,
        "default_delta_x": 0.25,
    }

    def construct(self):
        # Much copy-pasting from previous scenes.  Not great, but
        # the fastest way to get the ease-of-tweaking I'd like.
        zoom_words = TextMobject("Zoomed view \\\\ near $1/4$")
        zoom_words.next_to(self.zoomed_display, DOWN)

        x = 0.25
        local_sample_dots = self.get_local_sample_dots(
            x, sample_radius=2.5 * self.zoomed_camera.frame.get_width(),
        )
        local_coordinate_values = self.get_local_coordinate_values(
            x, dx=0.01,
        )
        target_coordinate_values = self.get_local_coordinate_values(
            self.func(x), dx=0.01,
        )

        color = RED
        sample_dot_ghost_copies = self.sample_dot_ghosts.copy()
        stretch_words = self.get_stretch_words("1/2", color, less_than_one=True)
        deriv_equation = self.get_deriv_equation("1/4", "1/2", color)

        one_fourth_point = self.get_input_point(x)
        one_fourth_arrow = Vector(0.5 * UP, color=WHITE)
        one_fourth_arrow.stem.stretch(0.75, 0)
        one_fourth_arrow.tip.scale(0.75, about_edge=DOWN)
        one_fourth_arrow.next_to(one_fourth_point, DOWN, SMALL_BUFF)
        one_fourth_label = TexMobject("0.25")
        one_fourth_label.match_height(self.input_line.numbers)
        one_fourth_label.next_to(one_fourth_arrow, DOWN, SMALL_BUFF)

        self.add(deriv_equation)
        self.zoom_in_on_input(
            x,
            local_sample_dots=local_sample_dots,
            local_coordinate_values=local_coordinate_values,
            pop_out=False,
            first_added_anims=[
                FadeIn(one_fourth_label),
                GrowArrow(one_fourth_arrow),
            ]
        )
        self.play(Write(zoom_words, run_time=1))
        self.wait()
        self.add_foreground_mobject(stretch_words)
        self.apply_function(
            self.func,
            apply_function_to_number_line=False,
            sample_dots=sample_dot_ghost_copies,
            local_sample_dots=local_sample_dots,
            target_coordinate_values=target_coordinate_values,
            added_anims=[Write(stretch_words)]
        )
        self.wait(2)


class ZoomInOnXSquaredNearZero(ZoomInOnXSquaredNearOne):
    CONFIG = {
        "zoom_factor": 0.1,
        "zoomed_display_width": 4,
        "scale_by_term": "???",
    }

    def construct(self):
        zoom_words = TextMobject(
            "Zoomed %sx \\\\ near 0" % "{:,}".format(int(1.0 / self.zoom_factor))
        )
        zoom_words.next_to(self.zoomed_display, DOWN)

        x = 0
        local_sample_dots = self.get_local_sample_dots(
            x, sample_radius=2 * self.zoomed_camera.frame.get_width()
        )
        local_coordinate_values = self.get_local_coordinate_values(
            x, dx=self.zoom_factor
        )
        # target_coordinate_values = self.get_local_coordinate_values(
        #     self.func(x), dx=self.zoom_factor
        # )

        color = self.sample_dots[len(self.sample_dots) / 2].get_color()
        sample_dot_ghost_copies = self.sample_dot_ghosts.copy()
        stretch_words = self.get_stretch_words(
            self.scale_by_term, color, less_than_one=True
        )
        deriv_equation = self.get_deriv_equation(x, 2 * x, color)

        self.add(deriv_equation)
        self.zoom_in_on_input(
            x,
            pop_out=False,
            local_sample_dots=local_sample_dots,
            local_coordinate_values=local_coordinate_values
        )
        self.play(Write(zoom_words, run_time=1))
        self.wait()
        self.add_foreground_mobject(stretch_words)
        self.apply_function(
            self.func,
            apply_function_to_number_line=False,
            sample_dots=sample_dot_ghost_copies,
            local_sample_dots=local_sample_dots,
            # target_coordinate_values=target_coordinate_values,
            added_anims=[
                Write(stretch_words),
                MaintainPositionRelativeTo(
                    self.local_coordinates,
                    self.zoomed_camera.frame
                )
            ]
        )
        self.wait(2)


class ZoomInMoreAndMoreToZero(ZoomInOnXSquaredNearZero):
    def construct(self):
        x = 0
        color = self.sample_dots[len(self.sample_dots) / 2].get_color()
        deriv_equation = self.get_deriv_equation(x, 2 * x, color)
        self.add(deriv_equation)

        frame = self.zoomed_camera.frame
        zoomed_display_height = self.zoomed_display.get_height()

        last_sample_dots = VGroup()
        last_coords = VGroup()
        last_zoom_words = None
        for factor in 0.1, 0.01, 0.001, 0.0001:
            frame.save_state()
            frame.set_height(factor * zoomed_display_height)
            self.local_coordinate_num_decimal_places = int(-np.log10(factor))
            zoom_words = TextMobject(
                "Zoomed", "{:,}x \\\\".format(int(1.0 / factor)),
                "near 0",
            )
            zoom_words.next_to(self.zoomed_display, DOWN)

            sample_dots = self.get_local_sample_dots(x)
            coords = self.get_local_coordinate_values(x, dx=factor)
            frame.restore()

            added_anims = [
                ApplyMethod(last_sample_dots.fade, 1),
                ApplyMethod(last_coords.fade, 1),
            ]
            if last_zoom_words is not None:
                added_anims.append(ReplacementTransform(
                    last_zoom_words, zoom_words
                ))
            else:
                added_anims.append(FadeIn(zoom_words))
            self.zoom_in_on_input(
                x,
                local_sample_dots=sample_dots,
                local_coordinate_values=coords,
                pop_out=False,
                zoom_factor=factor,
                first_added_anims=added_anims
            )
            self.wait()
            last_sample_dots = sample_dots
            last_coords = self.local_coordinates
            last_zoom_words = zoom_words


class ZoomInOnXSquared100xZero(ZoomInOnXSquaredNearZero):
    CONFIG = {
        "zoom_factor": 0.01
    }


class ZoomInOnXSquared1000xZero(ZoomInOnXSquaredNearZero):
    CONFIG = {
        "zoom_factor": 0.001,
        "local_coordinate_num_decimal_places": 3,
    }


class ZoomInOnXSquared10000xZero(ZoomInOnXSquaredNearZero):
    CONFIG = {
        "zoom_factor": 0.0001,
        "local_coordinate_num_decimal_places": 4,
        "scale_by_term": "0",
    }


class XSquaredForNegativeInput(TalkThroughXSquaredExample):
    CONFIG = {
        "input_line_config": {
            "x_min": -4,
            "x_max": 4,
        },
        "input_line_zero_point": 0.5 * UP + 0 * LEFT,
        "output_line_config": {},
        "default_mapping_animation_config": {
            "path_arc": 30 * DEGREES
        },
        "zoomed_display_width": 4,
    }

    def construct(self):
        self.add_title()
        self.show_full_transformation()
        self.zoom_in_on_example()

    def show_full_transformation(self):
        sample_dots = self.get_sample_dots(
            x_min=-4.005,
            delta_x=0.05,
            dot_radius=0.05
        )
        sample_dots.set_fill(opacity=0.8)

        self.play(LaggedStartMap(DrawBorderThenFill, sample_dots))
        self.play(LaggedStartMap(
            ApplyFunction, sample_dots[len(sample_dots) / 2:0:-1],
            lambda mob: (
                lambda m: m.scale(2).shift(SMALL_BUFF * UP).set_color(PINK),
                mob,
            ),
            rate_func=there_and_back,
        ))
        self.add_sample_dot_ghosts(sample_dots)
        self.apply_function(self.func, sample_dots=sample_dots)
        self.wait()

    def zoom_in_on_example(self):
        x = -2

        local_sample_dots = self.get_local_sample_dots(x)
        local_coordinate_values = self.get_local_coordinate_values(
            x, dx=0.1
        )
        target_coordinate_values = self.get_local_coordinate_values(
            self.func(x), dx=0.1
        )
        deriv_equation = self.get_deriv_equation(x, 2 * x, color=BLUE)
        sample_dot_ghost_copies = self.sample_dot_ghosts.copy()
        scale_words = self.get_stretch_words(-4, color=BLUE)

        self.zoom_in_on_input(
            x,
            local_sample_dots=local_sample_dots,
            local_coordinate_values=local_coordinate_values,
        )
        self.wait()
        self.play(Write(deriv_equation))
        self.add_foreground_mobject(scale_words)
        self.play(Write(scale_words))
        self.apply_function(
            self.func,
            sample_dots=sample_dot_ghost_copies,
            local_sample_dots=local_sample_dots,
            target_coordinate_values=target_coordinate_values
        )
        self.wait()


class FeelsALittleCramped(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Kind of cramped,\\\\ isn't it?",
            target_mode="sassy"
        )
        self.wait()
        self.teacher_says(
            "Sure, but think \\\\ locally"
        )
        self.change_all_student_modes("pondering", look_at_arg=self.screen)
        self.wait(3)


class HowDoesThisSolveProblems(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Is this...useful?",
            target_mode="confused"
        )
        self.change_student_modes("maybe", "confused", "sassy")
        self.play(self.teacher.change, "happy")
        self.wait(3)


class IntroduceContinuedFractionPuzzle(PiCreatureScene):
    CONFIG = {
        "remove_initial_rhs": True,
    }

    def construct(self):
        self.ask_question()
        self.set_equal_to_x()

    def create_pi_creatures(self):
        morty = Mortimer(height=2)
        morty.to_corner(DR)

        friend = PiCreature(color=GREEN, height=2)
        friend.to_edge(DOWN)
        friend.shift(LEFT)

        group = VGroup(morty, friend)
        group.shift(2 * LEFT)

        return morty, friend

    def ask_question(self):
        morty, friend = self.pi_creatures
        frac = get_phi_continued_fraction(9)
        frac.scale(0.8)
        rhs = DecimalNumber(
            (1 - np.sqrt(5)) / 2.0,
            num_decimal_places=5,
            show_ellipsis=True,
        )
        rhs.set_color(YELLOW)
        equals = TexMobject("=")
        equals.next_to(frac.get_part_by_tex("\\over"), RIGHT)
        rhs.next_to(equals, RIGHT)
        group = VGroup(frac, equals, rhs)
        group.scale(1.5)
        group.to_corner(UR)

        self.play(
            LaggedStartMap(
                Write, frac,
                run_time=15,
                lag_ratio=0.15,
            ),
            FadeInFromDown(equals),
            FadeInFromDown(rhs),
            PiCreatureSays(
                friend, "Would this be valid? \\\\ If not, why not?",
                target_mode="confused",
                look_at_arg=frac,
                bubble_kwargs={
                    "direction": RIGHT,
                    "width": 4,
                    "height": 3,
                }
            ),
            morty.change, "pondering",
        )
        self.wait()

        anims = [
            RemovePiCreatureBubble(
                friend, target_mode="pondering",
                look_at_arg=frac
            ),
        ]
        if self.remove_initial_rhs:
            anims += [
                Animation(frac),
                FadeOut(equals),
                rhs.scale, 0.5,
                rhs.to_corner, DL,
            ]
        self.play(*anims)

        self.neg_one_over_phi = rhs
        self.equals = equals
        self.frac = frac

    def set_equal_to_x(self):
        frac = self.frac
        morty, friend = self.get_pi_creatures()

        inner_frac = frac[4:]
        inner_frac_rect = SurroundingRectangle(
            inner_frac, stroke_width=2, buff=0.5 * SMALL_BUFF
        )
        inner_frac_group = VGroup(inner_frac, inner_frac_rect)

        equals = TexMobject("=")
        equals.next_to(frac[3], RIGHT)
        x, new_x = [TexMobject("x") for i in range(2)]
        xs = VGroup(x, new_x)
        xs.set_color(YELLOW)
        xs.scale(1.3)
        x.next_to(equals, RIGHT)
        new_x.next_to(frac[3], DOWN, 2 * SMALL_BUFF)

        fixed_point_words = VGroup(
            TextMobject("Fixed point of"),
            TexMobject(
                "f(x) = 1 + \\frac{1}{x}",
                tex_to_color_map={"x": YELLOW}
            )
        )
        fixed_point_words.arrange(DOWN)

        self.play(Write(x), Write(equals))
        self.wait()
        self.play(ShowCreation(inner_frac_rect))
        self.wait()
        self.play(
            inner_frac_group.scale, 0.75,
            inner_frac_group.center,
            inner_frac_group.to_edge, LEFT,
            ReplacementTransform(
                x.copy(), new_x,
                path_arc=-90 * DEGREES
            )
        )
        self.wait()
        self.play(
            frac[3].stretch, 0.1, 0, {"about_edge": RIGHT},
            MaintainPositionRelativeTo(
                VGroup(frac[2], new_x), frac[3]
            ),
            UpdateFromFunc(
                frac[:2], lambda m: m.next_to(frac[3], LEFT)
            )
        )
        self.wait()
        fixed_point_words.next_to(VGroup(frac[0], xs), DOWN, LARGE_BUFF)
        self.play(
            Write(fixed_point_words),
            morty.change, "hooray",
            friend.change, "happy"
        )
        self.wait(3)


class GraphOnePlusOneOverX(GraphScene):
    CONFIG = {
        "x_min": -6,
        "x_max": 6,
        "x_axis_width": 12,
        "y_min": -4,
        "y_max": 5,
        "y_axis_height": 8,
        "y_axis_label": None,
        "graph_origin": 0.5 * DOWN,
        "num_graph_anchor_points": 100,
        "func_graph_color": GREEN,
        "identity_graph_color": BLUE,
    }

    def construct(self):
        self.add_title()
        self.setup_axes()
        self.draw_graphs()
        self.show_solutions()

    def add_title(self):
        title = self.title = TexMobject(
            "\\text{Solve: }", "1 + \\frac{1}{x}", "=", "x",
        )
        title.set_color_by_tex("x", self.identity_graph_color, substring=False)
        title.set_color_by_tex("frac", self.func_graph_color)
        title.to_corner(UL)
        self.add(title)

    def setup_axes(self):
        GraphScene.setup_axes(self)
        step = 2
        self.x_axis.add_numbers(*list(range(-6, 0, step)) + list(range(step, 7, step)))
        self.y_axis.label_direction = RIGHT
        self.y_axis.add_numbers(*list(range(-2, 0, step)) + list(range(step, 4, step)))

    def draw_graphs(self, animate=True):
        lower_func_graph, upper_func_graph = func_graph = VGroup(*[
            self.get_graph(
                lambda x: 1.0 + 1.0 / x,
                x_min=x_min,
                x_max=x_max,
                color=self.func_graph_color,
            )
            for x_min, x_max in [(-10, -0.1), (0.1, 10)]
        ])
        func_graph.label = self.get_graph_label(
            upper_func_graph, "y = 1 + \\frac{1}{x}",
            x_val=6, direction=UP,
        )

        identity_graph = self.get_graph(
            lambda x: x, color=self.identity_graph_color
        )
        identity_graph.label = self.get_graph_label(
            identity_graph, "y = x",
            x_val=3, direction=UL, buff=SMALL_BUFF
        )

        if animate:
            for graph in func_graph, identity_graph:
                self.play(
                    ShowCreation(graph),
                    Write(graph.label),
                    run_time=2
                )
            self.wait()
        else:
            self.add(
                func_graph, func_graph.label,
                identity_graph, identity_graph.label,
            )

        self.func_graph = func_graph
        self.identity_graph = identity_graph

    def show_solutions(self):
        phi = 0.5 * (1 + np.sqrt(5))
        phi_bro = 0.5 * (1 - np.sqrt(5))

        lines = VGroup()
        for num in phi, phi_bro:
            line = DashedLine(
                self.coords_to_point(num, 0),
                self.coords_to_point(num, num),
                color=WHITE
            )
            line_copy = line.copy()
            line_copy.set_color(YELLOW)
            line.fade(0.5)
            line_anim = ShowCreationThenDestruction(
                line_copy,
                lag_ratio=0.5,
                run_time=2
            )
            cycle_animation(line_anim)
            lines.add(line)

        phi_line, phi_bro_line = lines

        decimal_kwargs = {
            "num_decimal_places": 3,
            "show_ellipsis": True,
            "color": YELLOW,
        }
        arrow_kwargs = {
            "buff": SMALL_BUFF,
            "color": WHITE,
            "tip_length": 0.15,
            "rectangular_stem_width": 0.025,
        }

        phi_decimal = DecimalNumber(phi, **decimal_kwargs)
        phi_decimal.next_to(phi_line, DOWN, LARGE_BUFF)
        phi_arrow = Arrow(
            phi_decimal[:4].get_top(), phi_line.get_bottom(),
            **arrow_kwargs
        )
        phi_label = TexMobject("=", "\\varphi")
        phi_label.next_to(phi_decimal, RIGHT)
        phi_label.set_color_by_tex("\\varphi", YELLOW)

        phi_bro_decimal = DecimalNumber(phi_bro, **decimal_kwargs)
        phi_bro_decimal.next_to(phi_bro_line, UP, LARGE_BUFF)
        phi_bro_decimal.shift(0.5 * LEFT)
        phi_bro_arrow = Arrow(
            phi_bro_decimal[:6].get_bottom(), phi_bro_line.get_top(),
            **arrow_kwargs
        )

        brother_words = TextMobject(
            "$\\varphi$'s little brother",
            tex_to_color_map={"$\\varphi$": YELLOW},
            arg_separator=""
        )
        brother_words.next_to(
            phi_bro_decimal[-2], UP, buff=MED_SMALL_BUFF,
            aligned_edge=RIGHT
        )

        self.add(phi_line.continual_anim)
        self.play(ShowCreation(phi_line))
        self.play(
            Write(phi_decimal),
            GrowArrow(phi_arrow),
        )
        self.play(Write(phi_label))
        self.wait(3)
        self.add(phi_bro_line.continual_anim)
        self.play(ShowCreation(phi_bro_line))
        self.play(
            Write(phi_bro_decimal),
            GrowArrow(phi_bro_arrow),
        )
        self.wait(4)
        self.play(Write(brother_words))
        self.wait(8)


class ThinkAboutWithRepeatedApplication(IntroduceContinuedFractionPuzzle):
    CONFIG = {
        "remove_initial_rhs": False,
    }

    def construct(self):
        self.force_skipping()
        self.ask_question()
        self.revert_to_original_skipping_status()

        self.obviously_not()
        self.ask_about_fraction()
        self.plug_func_into_self()

    def obviously_not(self):
        morty, friend = self.get_pi_creatures()
        friend.change_mode("confused")
        randy = Randolph()
        randy.match_height(morty)
        randy.to_corner(DL)

        frac = self.frac
        rhs = self.neg_one_over_phi
        plusses = frac[1::4]
        plus_rects = VGroup(*[
            SurroundingRectangle(plus, buff=0) for plus in plusses
        ])
        plus_rects.set_color(PINK)

        self.play(FadeIn(randy))
        self.play(
            PiCreatureSays(
                randy, "Obviously not!",
                bubble_kwargs={"width": 3, "height": 2},
                target_mode="angry",
                run_time=1,
            ),
            morty.change, "guilty",
            friend.change, "hesitant"
        )
        self.wait()
        self.play(
            Animation(frac),
            RemovePiCreatureBubble(randy, target_mode="sassy"),
            morty.change, "confused",
            friend.change, "confused",
        )
        self.play(LaggedStartMap(
            ShowCreationThenDestruction, plus_rects,
            run_time=2,
            lag_ratio=0.35,
        ))
        self.play(WiggleOutThenIn(rhs))
        self.wait(2)
        self.play(
            frac.scale, 0.7,
            frac.to_corner, UL,
            FadeOut(self.equals),
            rhs.scale, 0.5,
            rhs.center,
            rhs.to_edge, LEFT,
            FadeOut(randy),
            morty.change, "pondering",
            friend.change, "pondering",
        )

    def ask_about_fraction(self):
        frac = self.frac
        arrow = Vector(LEFT, color=RED)
        arrow.next_to(frac, RIGHT)
        question = TextMobject("What does this \\\\ actually mean?")
        question.set_color(RED)
        question.next_to(arrow, RIGHT)

        self.play(
            LaggedStartMap(FadeIn, question, run_time=1),
            GrowArrow(arrow),
            LaggedStartMap(
                ApplyMethod, frac,
                lambda m: (m.set_color, RED),
                rate_func=there_and_back,
                lag_ratio=0.2,
                run_time=2
            )
        )
        self.wait()
        self.play(FadeOut(question), FadeOut(arrow))

    def plug_func_into_self(self, value=1, value_str="1"):
        morty, friend = self.pi_creatures

        def func(x):
            return 1 + 1.0 / x

        lines = VGroup()
        value_labels = VGroup()
        for n_terms in range(5):
            lhs = get_nested_f(n_terms, arg="c")
            equals = TexMobject("=")
            rhs = get_nested_one_plus_one_over_x(n_terms, bottom_term=value_str)
            equals.next_to(rhs[0], LEFT)
            lhs.next_to(equals, LEFT)
            lines.add(VGroup(lhs, equals, rhs))

            value_label = TexMobject("= %.3f\\dots" % value)
            value = func(value)
            value_labels.add(value_label)

        lines.arrange(
            DOWN, buff=MED_LARGE_BUFF,
        )
        VGroup(lines, value_labels).scale(0.8)
        lines.to_corner(UR)
        buff = MED_LARGE_BUFF + MED_SMALL_BUFF + value_labels.get_width()
        lines.to_edge(RIGHT, buff=buff)
        for line, value_label in zip(lines, value_labels):
            value_label.move_to(line[1]).to_edge(RIGHT)

        top_line = lines[0]
        colors = [WHITE] + color_gradient([YELLOW, RED, PINK], len(lines) - 1)
        for n in range(1, len(lines)):
            color = colors[n]
            lines[n][0].set_color(color)
            lines[n][0][1:-1].match_style(lines[n - 1][0])
            lines[n][2].set_color(color)
            lines[n][2][4:].match_style(lines[n - 1][2])

        arrow = Vector(0.5 * DOWN, color=WHITE)
        arrow.next_to(value_labels[-1], DOWN)
        q_marks = TexMobject("???")
        q_marks.next_to(arrow, DOWN)

        self.play(
            FadeInFromDown(top_line),
            FadeInFromDown(value_labels[0])
        )
        for n in range(1, len(lines)):
            new_line = lines[n]
            last_line = lines[n - 1]
            value_label = value_labels[n]
            mover, target = [
                VGroup(
                    line[0][0],
                    line[0][-1],
                    line[1],
                    line[2][:4],
                )
                for line in (lines[1], new_line)
            ]
            anims = [ReplacementTransform(
                mover.copy().fade(1), target, path_arc=30 * DEGREES
            )]
            if n == 4:
                morty.generate_target()
                morty.target.change("horrified")
                morty.target.shift(2.5 * DOWN)
                anims.append(MoveToTarget(morty, remover=True))
            self.play(*anims)
            self.wait()
            self.play(
                ReplacementTransform(
                    last_line[0].copy(), new_line[0][1:-1]
                ),
                ReplacementTransform(
                    last_line[2].copy(), new_line[2][4:]
                ),
            )
            self.play(FadeIn(value_label))
            self.wait()
        self.play(
            GrowArrow(arrow),
            Write(q_marks),
            friend.change, "confused"
        )
        self.wait(3)

        self.top_line = VGroup(lines[0], value_labels[0])


class RepeatedApplicationWithPhiBro(ThinkAboutWithRepeatedApplication):
    CONFIG = {
        "value": (1 - np.sqrt(5)) / 2,
        "value_str": "-1/\\varphi",
    }

    def construct(self):
        self.force_skipping()
        self.ask_question()
        self.obviously_not()
        self.revert_to_original_skipping_status()

        self.plug_func_into_self(
            value=self.value,
            value_str=self.value_str
        )


class RepeatedApplicationWithNegativeSeed(RepeatedApplicationWithPhiBro, MovingCameraScene):
    CONFIG = {
        "value": -0.65,
        "value_str": "-0.65"
    }

    def setup(self):
        MovingCameraScene.setup(self)
        RepeatedApplicationWithPhiBro.setup(self)

    def construct(self):
        RepeatedApplicationWithPhiBro.construct(self)

        rect = SurroundingRectangle(self.top_line)
        question = TextMobject("What about a negative seed?")
        question.match_color(rect)
        question.next_to(rect, UP)
        self.play(ShowCreation(rect))
        self.play(
            Write(question),
            self.camera.frame.set_height, FRAME_HEIGHT + 1.5
        )
        self.wait()
        self.play(
            FadeOut(question),
            FadeOut(rect),
            self.camera.frame.set_height, FRAME_HEIGHT
        )


class ShowRepeatedApplication(Scene):
    CONFIG = {
        "title_color": YELLOW,
    }

    def construct(self):
        self.add_func_title()
        self.show_repeated_iteration()

    def add_func_title(self):
        title = self.title = VGroup(
            TexMobject("f(", "x", ")"),
            TexMobject("="),
            get_nested_one_plus_one_over_x(1)
        )
        title.arrange(RIGHT)
        title.to_corner(UL)
        title.set_color(self.title_color)

        self.add(title)

    def show_repeated_iteration(self):
        line = VGroup()
        decimal_kwargs = {
            "num_decimal_places": 3,
            "show_ellipsis": True,
        }
        phi = (1 + np.sqrt(5)) / 2

        def func(x):
            return 1.0 + 1.0 / x

        initial_term = DecimalNumber(2.71828, **decimal_kwargs)
        line.add(initial_term)
        last_term = initial_term

        def get_arrow():
            arrow = TexMobject("\\rightarrow")
            arrow.stretch(1.5, 0)
            arrow.next_to(line[-1], RIGHT)
            tex = TexMobject("f(x)")
            tex.set_color(YELLOW)
            tex.match_width(arrow)
            tex.next_to(arrow, UP, SMALL_BUFF)
            return VGroup(arrow, tex)

        for x in range(2):
            arrow = get_arrow()
            line.add(arrow)

            new_term = DecimalNumber(
                func(last_term.number),
                **decimal_kwargs
            )
            new_term.next_to(arrow[0], RIGHT)
            last_term = new_term
            line.add(new_term)

        line.add(get_arrow())
        line.add(TexMobject("\\dots\\dots").next_to(line[-1][0], RIGHT))
        num_phi_mob = DecimalNumber(phi, **decimal_kwargs)
        line.add(num_phi_mob.next_to(line[-1], RIGHT))
        line.move_to(DOWN)

        rects = VGroup(*[
            SurroundingRectangle(mob)
            for mob in (line[0], line[1:-1], line[-1])
        ])
        rects.set_stroke(BLUE, 2)

        braces = VGroup(*[
            Brace(rect, DOWN, buff=SMALL_BUFF)
            for rect in rects
        ])
        braces.set_color_by_gradient(GREEN, YELLOW)
        brace_texts = VGroup(*[
            brace.get_text(text).scale(0.75, about_edge=UP)
            for brace, text in zip(braces, [
                "Arbitrary \\\\ starting \\\\ value",
                "Repeatedly apply $f(x)$",
                "$\\varphi$ \\\\ ``Golden ratio''"
            ])
        ])
        var_phi_mob = brace_texts[2][0]
        var_phi_mob.scale(2, about_edge=UP).set_color(YELLOW)
        brace_texts[2][1:].next_to(var_phi_mob, DOWN, MED_SMALL_BUFF)

        # Animations
        self.add(line[0])
        self.play(
            GrowFromCenter(braces[0]),
            Write(brace_texts[0])
        )
        self.wait()
        self.play(
            GrowFromEdge(line[1], LEFT),
            FadeIn(braces[1]),
            FadeIn(brace_texts[1]),
        )
        self.play(ReplacementTransform(line[0].copy(), line[2]))
        self.wait()

        self.play(GrowFromEdge(line[3], LEFT))
        self.play(ReplacementTransform(line[2].copy(), line[4]))
        self.wait()

        self.play(GrowFromEdge(line[5], LEFT))
        self.play(LaggedStartMap(GrowFromCenter, line[6]))
        self.wait()

        self.play(FadeIn(line[7]))
        self.play(
            GrowFromCenter(braces[2]),
            FadeIn(brace_texts[2]),
        )
        self.wait()


class NumericalPlayFromOne(ExternallyAnimatedScene):
    pass


class NumericalPlayFromTau(ExternallyAnimatedScene):
    pass


class NumericalPlayFromNegPhi(ExternallyAnimatedScene):
    pass


class NumericalPlayOnNumberLineFromOne(Scene):
    CONFIG = {
        "starting_value": 1,
        "n_jumps": 10,
        "func": lambda x: 1 + 1.0 / x,
        "number_line_config": {
            "x_min": 0,
            "x_max": 2,
            "unit_size": 6,
            "tick_frequency": 0.25,
            "numbers_with_elongated_ticks": [0, 1, 2]
        }
    }

    def construct(self):
        self.add_number_line()
        self.add_phi_label()
        self.add_title()
        self.bounce_around()

    def add_number_line(self):
        number_line = NumberLine(**self.number_line_config)
        number_line.move_to(2 * DOWN)
        number_line.add_numbers()

        self.add(number_line)
        self.number_line = number_line

    def add_phi_label(self):
        number_line = self.number_line
        phi_point = number_line.number_to_point(
            (1 + np.sqrt(5)) / 2
        )
        phi_dot = Dot(phi_point, color=YELLOW)
        arrow = Vector(DL)
        arrow.next_to(phi_point, UR, SMALL_BUFF)
        phi_label = TexMobject("\\varphi = 1.618\\dots")
        phi_label.set_color(YELLOW)
        phi_label.next_to(arrow.get_start(), UP, SMALL_BUFF)

        self.add(phi_dot, phi_label, arrow)

    def add_title(self):
        title = TexMobject("x \\rightarrow 1 + \\frac{1}{x}")
        title.to_corner(UL)
        self.add(title)

    def bounce_around(self):
        number_line = self.number_line
        value = self.starting_value
        point = number_line.number_to_point(value)
        dot = Dot(point)
        dot.set_fill(RED, opacity=0.8)
        arrow = Vector(DR)
        arrow.next_to(point, UL, buff=SMALL_BUFF)
        arrow.match_color(dot)
        start_here = TextMobject("Start here")
        start_here.next_to(arrow.get_start(), UP, SMALL_BUFF)
        start_here.match_color(dot)

        self.play(
            FadeIn(start_here),
            GrowArrow(arrow),
            GrowFromPoint(dot, arrow.get_start())
        )
        self.play(
            FadeOut(start_here),
            FadeOut(arrow)
        )
        self.wait()
        for x in range(self.n_jumps):
            new_value = self.func(value)
            new_point = number_line.number_to_point(new_value)
            if new_value - value > 0:
                path_arc = -120 * DEGREES
            else:
                path_arc = -120 * DEGREES
            arc = Line(
                point, new_point,
                path_arc=path_arc,
                buff=SMALL_BUFF
            )
            self.play(
                ShowCreationThenDestruction(arc, run_time=1.5),
                ApplyMethod(
                    dot.move_to, new_point,
                    path_arc=path_arc
                ),
            )
            self.wait(0.5)

            value = new_value
            point = new_point


class NumericalPlayOnNumberLineFromTau(NumericalPlayOnNumberLineFromOne):
    CONFIG = {
        "starting_value": TAU,
        "number_line_config": {
            "x_min": 0,
            "x_max": 7,
            "unit_size": 2,
        }
    }


class NumericalPlayOnNumberLineFromMinusPhi(NumericalPlayOnNumberLineFromOne):
    CONFIG = {
        "starting_value": -0.61803,
        "number_line_config": {
            "x_min": -3,
            "x_max": 3,
            "unit_size": 2,
            "tick_frequency": 0.25,
        },
        "n_jumps": 25,
    }

    def add_phi_label(self):
        NumericalPlayOnNumberLineFromOne.add_phi_label(self)
        number_line = self.number_line
        new_point = number_line.number_to_point(
            (1 - np.sqrt(5)) / 2
        )
        arrow = Vector(DR)
        arrow.next_to(new_point, UL, SMALL_BUFF)
        arrow.set_color(RED)
        new_label = TexMobject("-\\frac{1}{\\varphi} = -0.618\\dots")
        new_label.set_color(RED)
        new_label.next_to(arrow.get_start(), UP, SMALL_BUFF)
        new_label.shift(RIGHT)
        self.add(new_label, arrow)


class RepeatedApplicationGraphically(GraphOnePlusOneOverX, PiCreatureScene):
    CONFIG = {
        "starting_value": 1,
        "n_jumps": 5,
        "n_times_to_show_identity_property": 2,
    }

    def setup(self):
        GraphOnePlusOneOverX.setup(self)
        PiCreatureScene.setup(self)

    def construct(self):
        self.setup_axes()
        self.draw_graphs(animate=False)
        self.draw_spider_web()

    def create_pi_creature(self):
        randy = Randolph(height=2)
        randy.flip()
        randy.to_corner(DR)
        return randy

    def get_new_randy_mode(self):
        randy = self.pi_creature
        if not hasattr(self, "n_mode_changes"):
            self.n_mode_changes = 0
        else:
            self.n_mode_changes += 1
        if self.n_mode_changes % 3 != 0:
            return randy.get_mode()
        return random.choice([
            "confused",
            "erm",
            "maybe"
        ])

    def draw_spider_web(self):
        randy = self.pi_creature
        func = self.func_graph[0].underlying_function
        x_val = self.starting_value
        curr_output = 0
        dot = Dot(color=RED, fill_opacity=0.7)
        dot.move_to(self.coords_to_point(x_val, curr_output))

        self.play(FadeInFrom(dot, 2 * UR))
        self.wait()

        for n in range(self.n_jumps):
            new_output = func(x_val)
            func_graph_point = self.coords_to_point(x_val, new_output)
            id_graph_point = self.coords_to_point(new_output, new_output)
            v_line = DashedLine(dot.get_center(), func_graph_point)
            h_line = DashedLine(func_graph_point, id_graph_point)

            curr_output = new_output
            x_val = new_output

            for line in v_line, h_line:
                line_end = line.get_end()
                self.play(
                    ShowCreation(line),
                    dot.move_to, line_end,
                    randy.change, self.get_new_randy_mode()
                )
                self.wait()

            if n < self.n_times_to_show_identity_property:
                x_point = self.coords_to_point(new_output, 0)
                y_point = self.coords_to_point(0, new_output)
                lines = VGroup(*[
                    Line(dot.get_center(), point)
                    for point in (x_point, y_point)
                ])
                lines.set_color(YELLOW)
                self.play(ShowCreationThenDestruction(
                    lines, run_time=2
                ))
                self.wait(0.25)


class RepeatedApplicationGraphicallyFromNegPhi(RepeatedApplicationGraphically):
    CONFIG = {
        "starting_value": -0.61,
        "n_jumps": 13,
        "n_times_to_show_identity_property": 0,
    }


class LetsSwitchToTheTransformationalView(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Lose the \\\\ graphs!",
            target_mode="hooray"
        )
        self.change_student_modes("hooray", "erm", "surprised")
        self.wait(5)


class AnalyzeFunctionWithTransformations(NumberlineTransformationScene):
    CONFIG = {
        "input_line_zero_point": 0.5 * UP,
        "output_line_zero_point": 2 * DOWN,
        "func": lambda x: 1 + 1.0 / x,
        "num_initial_applications": 10,
        "num_repeated_local_applications": 7,
        "zoomed_display_width": 3.5,
        "zoomed_display_height": 2,
        "default_mapping_animation_config": {},
    }

    def construct(self):
        self.add_function_title()
        self.repeatedly_apply_function()
        self.show_phi_and_phi_bro()
        self.zoom_in_on_phi()
        self.zoom_in_on_phi_bro()

    def setup_number_lines(self):
        NumberlineTransformationScene.setup_number_lines(self)
        for line in self.input_line, self.output_line:
            VGroup(line, line.tick_marks).set_stroke(width=2)

    def add_function_title(self):
        title = TexMobject("f(x)", "=", "1 +", "\\frac{1}{x}")
        title.to_edge(UP)
        self.add(title)
        self.title = title

    def repeatedly_apply_function(self):
        input_zero_point = self.input_line.number_to_point(0)
        output_zero_point = self.output_line.number_to_point(0)
        sample_dots = self.get_sample_dots(
            delta_x=0.05,
            dot_radius=0.05,
            x_min=-10,
            x_max=10,
        )
        sample_dots.set_stroke(BLACK, 0.5)
        sample_points = list(map(Mobject.get_center, sample_dots))

        self.play(LaggedStartMap(
            FadeInFrom, sample_dots,
            lambda m: (m, UP)
        ))
        self.show_arrows(sample_points)
        self.wait()
        for x in range(self.num_initial_applications):
            self.apply_function(
                self.func,
                apply_function_to_number_line=False,
                sample_dots=sample_dots
            )
            self.wait()

            shift_vect = input_zero_point - output_zero_point
            shift_vect[0] = 0
            lower_output_line = self.output_line.copy()
            upper_output_line = self.output_line.copy()
            lower_output_line.shift(-shift_vect)
            lower_output_line.fade(1)

            self.remove(self.output_line)
            self.play(
                ReplacementTransform(lower_output_line, self.output_line),
                upper_output_line.shift, shift_vect,
                upper_output_line.fade, 1,
                sample_dots.shift, shift_vect,
            )
            self.remove(upper_output_line)
            self.wait()
        self.play(FadeOut(sample_dots))

    def show_arrows(self, sample_points):
        input_zero_point = self.input_line.number_to_point(0)
        point_func = self.number_func_to_point_func(self.func)
        alt_point_func = self.number_func_to_point_func(lambda x: 1.0 / x)
        arrows, alt_arrows = [
            VGroup(*[
                Arrow(
                    point, func(point), buff=SMALL_BUFF,
                    tip_length=0.15
                )
                for point in sample_points
                if get_norm(point - input_zero_point) > 0.3
            ])
            for func in (point_func, alt_point_func)
        ]
        for group in arrows, alt_arrows:
            group.set_stroke(WHITE, 0.5)
            group.set_color_by_gradient(RED, YELLOW)
            for arrow in group:
                arrow.tip.set_stroke(BLACK, 0.5)

        one_plus = self.title.get_part_by_tex("1 +")
        one_plus_rect = BackgroundRectangle(one_plus)
        one_plus_rect.set_fill(BLACK, opacity=0.8)

        self.play(LaggedStartMap(GrowArrow, arrows))
        self.wait()
        self.play(LaggedStartMap(
            ApplyMethod, arrows,
            lambda a: (a.scale, 0.7),
            rate_func=there_and_back,
        ))
        self.wait()
        self.play(
            Transform(arrows, alt_arrows),
            FadeIn(one_plus_rect, remover=True),
            rate_func=there_and_back_with_pause,
            run_time=4,
        )
        self.wait()

        self.all_arrows = arrows

    def show_phi_and_phi_bro(self):
        phi = (1 + np.sqrt(5)) / 2
        phi_bro = (1 - np.sqrt(5)) / 2

        input_phi_point = self.input_line.number_to_point(phi)
        output_phi_point = self.output_line.number_to_point(phi)
        input_phi_bro_point = self.input_line.number_to_point(phi_bro)
        output_phi_bro_point = self.output_line.number_to_point(phi_bro)

        tick = Line(UP, DOWN)
        tick.set_stroke(YELLOW, 3)
        tick.match_height(self.input_line.tick_marks)
        phi_tick = tick.copy().move_to(input_phi_point, DOWN)
        phi_bro_tick = tick.copy().move_to(input_phi_bro_point, DOWN)
        VGroup(phi_tick, phi_bro_tick).shift(SMALL_BUFF * DOWN)

        phi_label = TexMobject("1.618\\dots")
        phi_label.next_to(phi_tick, UP)
        phi_bro_label = TexMobject("-0.618\\dots")
        phi_bro_label.next_to(phi_bro_tick, UP)
        VGroup(phi_label, phi_bro_label).set_color(YELLOW)

        arrow_kwargs = {
            "buff": SMALL_BUFF,
            "rectangular_stem_width": 0.035,
            "tip_length": 0.2,
        }
        phi_arrow = Arrow(phi_tick, output_phi_point, **arrow_kwargs)
        phi_bro_arrow = Arrow(phi_bro_tick, output_phi_bro_point, **arrow_kwargs)

        def fade_arrow(arrow):
            # arrow.set_stroke(DARK_GREY, 0.5)
            arrow.set_stroke(width=0.1)
            arrow.tip.set_fill(opacity=0)
            arrow.tip.set_stroke(width=0)
            return arrow

        self.play(
            LaggedStartMap(
                ApplyFunction, self.all_arrows,
                lambda a: (fade_arrow, a)
            ),
            FadeIn(phi_arrow),
            FadeIn(phi_bro_arrow),
        )
        self.play(
            Write(phi_label),
            GrowFromCenter(phi_tick)
        )
        self.play(
            Write(phi_bro_label),
            GrowFromCenter(phi_bro_tick)
        )

        self.set_variables_as_attrs(
            input_phi_point, output_phi_point,
            input_phi_bro_point, output_phi_bro_point,
            phi_label, phi_tick,
            phi_bro_label, phi_bro_tick,
            phi_arrow, phi_bro_arrow
        )

    def zoom_in_on_phi(self):
        phi = (1 + np.sqrt(5)) / 2
        # phi_point = self.get_input_point(phi)
        local_sample_dots = self.get_local_sample_dots(
            phi, dot_radius=0.005, sample_radius=1
        )
        local_coordinate_values = [1.55, 1.6, 1.65, 1.7]

        # zcbr = self.zoomed_camera_background_rectangle
        zcbr_group = self.zoomed_camera_background_rectangle_group
        zcbr_group.add(self.phi_tick)

        title = self.title
        deriv_text = TexMobject(
            "|", "\\frac{df}{dx}(\\varphi)", "|", "< 1",
            tex_to_color_map={"\\varphi": YELLOW}
        )
        deriv_text.get_parts_by_tex("|").match_height(
            deriv_text, stretch=True
        )
        deriv_text.move_to(title, UP)
        approx_value = TexMobject("\\approx |%.2f|" % (-1 / phi**2))
        approx_value.move_to(deriv_text)
        deriv_text_lhs = deriv_text[:-1]
        deriv_text_rhs = deriv_text[-1]

        self.zoom_in_on_input(
            phi,
            local_sample_dots=local_sample_dots,
            local_coordinate_values=local_coordinate_values
        )
        self.wait()
        self.apply_function(
            self.func,
            apply_function_to_number_line=False,
            local_sample_dots=local_sample_dots,
            target_coordinate_values=local_coordinate_values,
        )
        self.wait()
        self.play(
            FadeInFromDown(deriv_text_lhs),
            FadeInFromDown(deriv_text_rhs),
            title.to_corner, UL
        )
        self.wait()
        self.play(
            deriv_text_lhs.next_to, approx_value, LEFT,
            deriv_text_rhs.next_to, approx_value, RIGHT,
            FadeIn(approx_value)
        )
        self.wait()
        for n in range(self.num_repeated_local_applications):
            self.apply_function(
                self.func,
                apply_function_to_number_line=False,
                local_sample_dots=local_sample_dots,
                path_arc=60 * DEGREES,
                run_time=2
            )

        self.deriv_text = VGroup(
            deriv_text_lhs, deriv_text_rhs, approx_value
        )

    def zoom_in_on_phi_bro(self):
        zcbr = self.zoomed_camera_background_rectangle
        # zcbr_group = self.zoomed_camera_background_rectangle_group
        zoomed_frame = self.zoomed_camera.frame

        phi_bro = (1 - np.sqrt(5)) / 2
        # phi_bro_point = self.get_input_point(phi_bro)
        local_sample_dots = self.get_local_sample_dots(phi_bro)
        local_coordinate_values = [-0.65, -0.6, -0.55]

        deriv_text = TexMobject(
            "\\left| \\frac{df}{dx}\\left(\\frac{-1}{\\varphi}\\right) \\right|",
            "\\approx |%.2f|" % (-1 / (phi_bro**2)),
            "> 1"
        )
        deriv_text.move_to(self.deriv_text, UL)
        deriv_text[0][10:14].set_color(YELLOW)

        self.play(
            zoomed_frame.set_height, 4,
            zoomed_frame.center,
            self.deriv_text.fade, 1,
            run_time=2
        )
        self.wait()
        zcbr.set_fill(opacity=0)
        self.zoom_in_on_input(
            phi_bro,
            local_sample_dots=local_sample_dots,
            local_coordinate_values=local_coordinate_values,
            zoom_factor=self.zoom_factor,
            first_anim_kwargs={"run_time": 2},
        )
        self.wait()
        self.play(FadeInFromDown(deriv_text))
        self.wait()
        zcbr.set_fill(opacity=1)
        self.apply_function(
            self.func,
            apply_function_to_number_line=False,
            local_sample_dots=local_sample_dots,
            target_coordinate_values=local_coordinate_values,
        )
        self.wait()
        for n in range(self.num_repeated_local_applications):
            self.apply_function(
                self.func,
                apply_function_to_number_line=False,
                local_sample_dots=local_sample_dots,
                path_arc=20 * DEGREES,
                run_time=2,
            )


class StabilityAndInstability(AnalyzeFunctionWithTransformations):
    CONFIG = {
        "num_initial_applications": 0,
    }

    def construct(self):
        self.force_skipping()
        self.add_function_title()
        self.repeatedly_apply_function()
        self.show_phi_and_phi_bro()
        self.revert_to_original_skipping_status()

        self.label_stability()
        self.write_derivative_fact()

    def label_stability(self):
        self.title.to_corner(UL)

        stable_label = TextMobject("Stable fixed point")
        unstable_label = TextMobject("Unstable fixed point")
        labels = VGroup(stable_label, unstable_label)
        labels.scale(0.8)
        stable_label.next_to(self.phi_label, UP, aligned_edge=ORIGIN)
        unstable_label.next_to(self.phi_bro_label, UP, aligned_edge=ORIGIN)

        phi_point = self.input_phi_point
        phi_bro_point = self.input_phi_bro_point

        arrow_groups = VGroup()
        for point in phi_point, phi_bro_point:
            arrows = VGroup(*[a for a in self.all_arrows if get_norm(a.get_start() - point) < 0.75]).copy()
            arrows.set_fill(PINK, 1)
            arrows.set_stroke(PINK, 3)
            arrows.second_anim = LaggedStartMap(
                ApplyMethod, arrows,
                lambda m: (m.set_color, YELLOW),
                rate_func=there_and_back_with_pause,
                lag_ratio=0.7,
                run_time=2,
            )
            arrows.anim = AnimationGroup(*list(map(GrowArrow, arrows)))
            arrow_groups.add(arrows)
        phi_arrows, phi_bro_arrows = arrow_groups

        self.add_foreground_mobjects(self.phi_arrow, self.phi_bro_arrow)
        self.play(
            Write(stable_label),
            phi_arrows.anim,
        )
        self.play(phi_arrows.second_anim)
        self.play(
            Write(unstable_label),
            phi_bro_arrows.anim,
        )
        self.play(phi_bro_arrows.second_anim)
        self.wait()

        self.stable_label = stable_label
        self.unstable_label = unstable_label
        self.phi_arrows = phi_arrows
        self.phi_bro_arrows = phi_bro_arrows

    def write_derivative_fact(self):
        stable_label = self.stable_label
        unstable_label = self.unstable_label
        labels = VGroup(stable_label, unstable_label)
        phi_arrows = self.phi_arrows
        phi_bro_arrows = self.phi_bro_arrows
        arrow_groups = VGroup(phi_arrows, phi_bro_arrows)

        deriv_labels = VGroup()
        for char, label in zip("<>", labels):
            deriv_label = TexMobject(
                "\\big|", "\\frac{df}{dx}(", "x", ")", "\\big|",
                char, "1"
            )
            deriv_label.get_parts_by_tex("\\big|").match_height(
                deriv_label, stretch=True
            )
            deriv_label.set_color_by_tex("x", YELLOW, substring=False)
            deriv_label.next_to(label, UP)
            deriv_labels.add(deriv_label)

        dot_groups = VGroup()
        for arrow_group in arrow_groups:
            dot_group = VGroup()
            for arrow in arrow_group:
                start_point, end_point = [
                    line.number_to_point(line.point_to_number(p))
                    for line, p in [
                        (self.input_line, arrow.get_start()),
                        (self.output_line, arrow.get_end()),
                    ]
                ]
                dot = Dot(start_point, radius=0.05)
                dot.set_color(YELLOW)
                dot.generate_target()
                dot.target.move_to(end_point)
                dot_group.add(dot)
            dot_groups.add(dot_group)

        for deriv_label, dot_group in zip(deriv_labels, dot_groups):
            self.play(FadeInFromDown(deriv_label))
            self.play(LaggedStartMap(GrowFromCenter, dot_group))
            self.play(*list(map(MoveToTarget, dot_group)), run_time=2)
            self.wait()


class StaticAlgebraicObject(Scene):
    def construct(self):
        frac = get_phi_continued_fraction(40)
        frac.set_width(FRAME_WIDTH - 1)
        # frac.shift(2 * DOWN)
        frac.to_edge(DOWN)
        frac.set_stroke(WHITE, width=0.5)

        title = TexMobject(
            "\\infty \\ne \\lim",
            tex_to_color_map={"\\ne": RED}
        )
        title.scale(1.5)
        title.to_edge(UP)

        polynomial = TexMobject("x^2 - x - 1 = 0")
        polynomial.move_to(title)

        self.add(title)
        self.play(LaggedStartMap(
            GrowFromCenter, frac,
            lag_ratio=0.1,
            run_time=3
        ))
        self.wait()
        factor = 1.1
        self.play(frac.scale, factor, run_time=0.5)
        self.play(
            frac.scale, 1 / factor,
            frac.set_color, LIGHT_GREY,
            run_time=0.5, rate_func=lambda t: t**5,
        )
        self.wait()
        self.play(
            FadeOut(title),
            FadeIn(polynomial)
        )
        self.wait(2)


class NotBetterThanGraphs(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Um, yeah, I'll stick \\\\ with graphs thanks",
            target_mode="sassy",
        )
        self.play(
            self.teacher.change, "guilty",
            self.get_student_changes("sad", "sassy", "hesitant")
        )
        self.wait(2)
        self.play(
            RemovePiCreatureBubble(self.students[1]),
            self.teacher.change, "raise_right_hand"
        )
        self.change_all_student_modes(
            "confused", look_at_arg=self.screen
        )
        self.wait(3)
        self.teacher_says(
            "You must flex those \\\\ conceptual muscles",
            added_anims=[self.get_student_changes(
                *3 * ["thinking"],
                look_at_arg=self.teacher.eyes
            )]
        )
        self.wait(3)


class WhatComesAfterWrapper(Wrapper):
    CONFIG = {"title": "Beyond the first year"}

    def construct(self):
        Wrapper.construct(self)
        new_title = TextMobject("Next video")
        new_title.set_color(BLUE)
        new_title.move_to(self.title)

        self.play(
            FadeInFromDown(new_title),
            self.title.shift, UP,
            self.title.fade, 1,
        )
        self.wait(3)


class TopicsAfterSingleVariable(PiCreatureScene, MoreTopics):
    CONFIG = {
        "pi_creatures_start_on_screen": False,
    }

    def construct(self):
        MoreTopics.construct(self)
        self.show_horror()
        self.zero_in_on_complex_analysis()

    def create_pi_creatures(self):
        creatures = VGroup(*[
            PiCreature(color=color)
            for color in [BLUE_E, BLUE_C, BLUE_D]
        ])
        creatures.arrange(RIGHT, buff=LARGE_BUFF)
        creatures.scale(0.5)
        creatures.to_corner(DR)
        return creatures

    def show_horror(self):
        creatures = self.get_pi_creatures()
        modes = ["horrified", "tired", "horrified"]
        for creature, mode in zip(creatures, modes):
            creature.generate_target()
            creature.target.change(mode, self.other_topics)
        creatures.fade(1)

        self.play(LaggedStartMap(MoveToTarget, creatures))
        self.wait(2)

    def zero_in_on_complex_analysis(self):
        creatures = self.get_pi_creatures()
        complex_analysis = self.other_topics[1]
        self.other_topics.remove(complex_analysis)

        self.play(
            complex_analysis.scale, 1.25,
            complex_analysis.center,
            complex_analysis.to_edge, UP,
            LaggedStartMap(FadeOut, self.other_topics),
            LaggedStartMap(FadeOut, self.lines),
            FadeOut(self.calculus),
            *[
                ApplyMethod(creature.change, "pondering")
                for creature in creatures
            ]
        )
        self.wait(4)


class ShowJacobianZoomedIn(LinearTransformationScene, ZoomedScene):
    CONFIG = {
        "show_basis_vectors": False,
        "show_coordinates": True,
        "zoom_factor": 0.05,
    }

    def setup(self):
        LinearTransformationScene.setup(self)
        ZoomedScene.setup(self)

    def construct(self):
        def example_function(point):
            x, y, z = point
            return np.array([
                x + np.sin(y),
                y + np.sin(x),
                0
            ])

        zoomed_camera = self.zoomed_camera
        zoomed_display = self.zoomed_display
        frame = zoomed_camera.frame
        frame.move_to(3 * LEFT + 1 * UP)
        frame.set_color(YELLOW)
        zoomed_display.display_frame.set_color(YELLOW)
        zd_rect = BackgroundRectangle(
            zoomed_display,
            fill_opacity=1,
            buff=MED_SMALL_BUFF,
        )
        self.add_foreground_mobject(zd_rect)
        zd_rect.anim = UpdateFromFunc(
            zd_rect,
            lambda rect: rect.replace(zoomed_display).scale(1.1)
        )
        zd_rect.next_to(FRAME_HEIGHT * UP, UP)

        tiny_grid = NumberPlane(
            x_radius=2,
            y_radius=2,
            color=BLUE_E,
            secondary_color=DARK_GREY,
        )
        tiny_grid.replace(frame)

        jacobian_words = TextMobject("Jacobian")
        jacobian_words.add_background_rectangle()
        jacobian_words.scale(1.5)
        jacobian_words.move_to(zoomed_display, UP)
        zoomed_display.next_to(jacobian_words, DOWN)

        self.play(self.get_zoom_in_animation())
        self.activate_zooming()
        self.play(
            self.get_zoomed_display_pop_out_animation(),
            zd_rect.anim
        )
        self.play(
            ShowCreation(tiny_grid),
            Write(jacobian_words),
            run_time=2
        )
        self.add_transformable_mobject(tiny_grid)
        self.add_foreground_mobject(jacobian_words)
        self.wait()
        self.apply_nonlinear_transformation(
            example_function,
            added_anims=[MaintainPositionRelativeTo(
                zoomed_camera.frame, tiny_grid,
            )],
            run_time=5
        )
        self.wait()


class PrinciplesOverlay(PiCreatureScene):
    CONFIG = {
        "default_pi_creature_kwargs": {
            "color": GREY_BROWN,
            "flip_at_start": True,
        },
        "default_pi_creature_start_corner": DR,
    }

    def construct(self):
        morty = self.pi_creature
        q_marks = VGroup(*[TexMobject("?") for x in range(40)])
        q_marks.arrange_in_grid(4, 10)
        q_marks.space_out_submobjects(1.4)
        for mark in q_marks:
            mark.shift(
                random.random() * RIGHT,
                random.random() * UP,
            )
            mark.scale(1.5)
            mark.set_stroke(BLACK, 1)
        q_marks.next_to(morty, UP)
        q_marks.shift_onto_screen()
        q_marks.sort(
            lambda p: get_norm(p - morty.get_top())
        )

        self.play(morty.change, "pondering")
        self.wait(2)
        self.play(morty.change, "raise_right_hand")
        self.wait()
        self.play(morty.change, "thinking")
        self.wait(4)
        self.play(FadeInFromDown(q_marks[0]))
        self.wait(2)
        self.play(LaggedStartMap(
            FadeInFromDown, q_marks[1:],
            run_time=3
        ))
        self.wait(3)


class ManyInfiniteExpressions(Scene):
    def construct(self):
        frac = get_phi_continued_fraction(10)
        frac.set_height(2)
        frac.to_corner(UL)

        n = 9
        radical_str_parts = [
            "%d + \\sqrt{" % d
            for d in range(1, n + 1)
        ]
        radical_str_parts += ["\\cdots"]
        radical_str_parts += ["}"] * n
        radical = TexMobject("".join(radical_str_parts))
        radical.to_corner(UR)
        radical.to_edge(DOWN)
        radical.set_color_by_gradient(YELLOW, RED)

        n = 12
        power_tower = TexMobject(
            *["\\sqrt{2}^{"] * n + ["\\dots"] + ["}"] * n
        )
        power_tower.to_corner(UR)
        power_tower.set_color_by_gradient(BLUE, GREEN)

        self.play(*[
            LaggedStartMap(
                GrowFromCenter, group,
                lag_ratio=0.1,
                run_time=8,
            )
            for group in (frac, radical, power_tower)
        ])
        self.wait(2)


class HoldUpPromo(PrinciplesOverlay):
    def construct(self):
        morty = self.pi_creature

        url = TextMobject("https://brilliant.org/3b1b/")
        url.to_corner(UL)

        rect = ScreenRectangle(height=5.5)
        rect.next_to(url, DOWN)
        rect.to_edge(LEFT)

        self.play(
            Write(url),
            self.pi_creature.change, "raise_right_hand"
        )
        self.play(ShowCreation(rect))
        self.wait(2)
        self.change_mode("thinking")
        self.wait()
        self.look_at(url)
        self.wait(10)
        self.change_mode("happy")
        self.wait(10)
        self.change_mode("raise_right_hand")
        self.wait(10)

        self.play(FadeOut(rect), FadeOut(url))
        self.play(morty.change, "raise_right_hand")
        self.wait()
        self.play(morty.change, "hooray")
        self.wait(3)


class EndScreen(PatreonEndScreen):
    CONFIG = {
        "specific_patrons": [
            "Juan Benet",
            "Keith Smith",
            "Chloe Zhou",
            "Desmos",
            "Burt Humburg",
            "CrypticSwarm",
            "Andrew Sachs",
            "Ho\\`ang T\\`ung L\\^am",
            # "Hoàng Tùng Lâm",
            "Devin Scott",
            "Akash Kumar",
            "Felix Tripier",
            "Arthur Zey",
            "David Kedmey",
            "Ali Yahya",
            "Mayank M. Mehrotra",
            "Lukas Biewald",
            "Yana Chernobilsky",
            "Kaustuv DeBiswas",
            "Yu Jun",
            "dave nicponski",
            "Damion Kistler",
            "Jordan Scales",
            "Markus Persson",
            "Fela",
            "Fred Ehrsam",
            "Britt Selvitelle",
            "Jonathan Wilson",
            "Ryan Atallah",
            "Joseph John Cox",
            "Luc Ritchie",
            "Matt Roveto",
            "Jamie Warner",
            "Marek Cirkos",
            "Magister Mugit",
            "Stevie Metke",
            "Cooper Jones",
            "James Hughes",
            "John V Wertheim",
            "Chris Giddings",
            "Song Gao",
            "Alexander Feldman",
            "Matt Langford",
            "Max Mitchell",
            "Richard Burgmann",
            "John Griffith",
            "Chris Connett",
            "Steven Tomlinson",
            "Jameel Syed",
            "Bong Choung",
            "Ignacio Freiberg",
            "Zhilong Yang",
            "Giovanni Filippi",
            "Eric Younge",
            "Prasant Jagannath",
            "Cody Brocious",
            "James H. Park",
            "Norton Wang",
            "Kevin Le",
            "Tianyu Ge",
            "David MacCumber",
            "Oliver Steele",
            "Yaw Etse",
            "Dave B",
            "Waleed Hamied",
            "George Chiesa",
            "supershabam",
            "Delton Ding",
            "Thomas Tarler",
            "Isak Hietala",
            "1st ViewMaths",
            "Jacob Magnuson",
            "Mark Govea",
            "Clark Gaebel",
            "Mathias Jansson",
            "David Clark",
            "Michael Gardner",
            "Mads Elvheim",
            "Awoo",
            "Dr . David G. Stork",
            "Ted Suzman",
            "Linh Tran",
            "Andrew Busey",
            "John Haley",
            "Ankalagon",
            "Eric Lavault",
            "Boris Veselinovich",
            "Julian Pulgarin",
            "Jeff Linse",
            "Robert Teed",
            "Jason Hise",
            "Meshal Alshammari",
            "Bernd Sing",
            "James Thornton",
            "Mustafa Mahdi",
            "Mathew Bramson",
            "Jerry Ling",
            "Sh\\`im\\'in Ku\\=ang",
            "Rish Kundalia",
            "Achille Brighton",
            "Ripta Pasay",
        ]
    }


# class Thumbnail(GraphicalIntuitions):
class Thumbnail(AnalyzeFunctionWithTransformations):
    CONFIG = {
        "x_axis_width": 12,
        "graph_origin": 1.5 * DOWN + 4 * LEFT,
        "num_initial_applications": 1,
        "input_line_zero_point": 2 * UP,
    }

    def construct(self):
        self.add_function_title()
        self.title.fade(1)
        self.titles.fade(1)
        self.repeatedly_apply_function()
        self.all_arrows.set_stroke(width=1)

        full_rect = FullScreenFadeRectangle()
        cross = Cross(full_rect)
        cross.set_stroke(width=40)

        # self.add(cross)
