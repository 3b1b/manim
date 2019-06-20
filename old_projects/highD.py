from manimlib.imports import *

##########
#force_skipping
#revert_to_original_skipping_status

##########

class Slider(NumberLine):
    CONFIG = {
        "color" : WHITE,
        "x_min" : -1,
        "x_max" : 1,
        "unit_size" : 2,
        "center_value" : 0,
        "number_scale_val" : 0.75,
        "label_scale_val" : 1,
        "numbers_with_elongated_ticks" : [],
        "line_to_number_vect" : LEFT,
        "line_to_number_buff" : MED_LARGE_BUFF,
        "dial_radius" : 0.1,
        "dial_color" : YELLOW,
        "include_real_estate_ticks" : True,
    }
    def __init__(self, **kwargs):
        NumberLine.__init__(self, **kwargs)
        self.rotate(np.pi/2)
        self.init_dial()
        if self.include_real_estate_ticks:
            self.add_real_estate_ticks()

    def init_dial(self):
        dial = Dot(
            radius = self.dial_radius,
            color = self.dial_color,
        )
        dial.move_to(self.number_to_point(self.center_value))
        re_dial = dial.copy()
        re_dial.set_fill(opacity = 0)
        self.add(dial, re_dial)

        self.dial = dial
        self.re_dial = re_dial
        self.last_sign = -1

    def add_label(self, tex):
        label = TexMobject(tex)
        label.scale(self.label_scale_val)
        label.move_to(self.get_top())
        label.shift(MED_LARGE_BUFF*UP)
        self.add(label)
        self.label = label

    def add_real_estate_ticks(
        self, 
        re_per_tick = 0.05,
        colors = [BLUE, RED],
        max_real_estate = 1,
        ):
        self.real_estate_ticks = VGroup(*[   
            self.get_tick(self.center_value + u*np.sqrt(x + re_per_tick))
            for x in np.arange(0, max_real_estate, re_per_tick)
            for u in [-1, 1]
        ])
        self.real_estate_ticks.set_stroke(width = 3)
        self.real_estate_ticks.set_color_by_gradient(*colors)
        self.add(self.real_estate_ticks)
        self.add(self.dial)
        return self.real_estate_ticks

    def set_value(self, x):
        re = (x - self.center_value)**2
        for dial, val in (self.dial, x), (self.re_dial, re):
            dial.move_to(self.number_to_point(val))
        return self

    def set_center_value(self, x):
        self.center_value = x
        return self

    def change_real_estate(self, d_re):
        left_over = 0
        curr_re = self.get_real_estate()
        if d_re < -curr_re:
            left_over = d_re + curr_re
            d_re = -curr_re
        self.set_real_estate(curr_re + d_re)
        return left_over

    def set_real_estate(self, target_re):
        if target_re < 0:
            raise Exception("Cannot set real estate below 0")
        self.re_dial.move_to(self.number_to_point(target_re))
        self.update_dial_by_re_dial()
        return self

    def get_dial_supplement_animation(self):
        return UpdateFromFunc(self.dial, self.update_dial_by_re_dial)

    def update_dial_by_re_dial(self, dial = None):
        dial = dial or self.dial
        re = self.get_real_estate()
        sign = np.sign(self.get_value() - self.center_value)
        if sign == 0:
            sign = -self.last_sign
            self.last_sign *= -1
        dial.move_to(self.number_to_point(
            self.center_value + sign*np.sqrt(abs(re))
        ))
        return dial

    def get_value(self):
        return self.point_to_number(self.dial.get_center())

    def get_real_estate(self):
        return self.point_to_number(self.re_dial.get_center())

    def copy(self):
        return self.deepcopy()

class SliderScene(Scene):
    CONFIG = {
        "n_sliders" : 4,
        "slider_spacing" : MED_LARGE_BUFF,
        "slider_config" : {},
        "center_point" : None,
        "total_real_estate" : 1,
        "ambiently_change_sliders" : False,
        "ambient_velocity_magnitude" : 1.0,
        "ambient_acceleration_magnitude" : 1.0,
        "ambient_jerk_magnitude" : 1.0/2,
    }
    def setup(self):
        if self.center_point is None:
            self.center_point = np.zeros(self.n_sliders)
        sliders = VGroup(*[
            Slider(center_value = cv, **self.slider_config)
            for cv in self.center_point
        ])
        sliders.arrange(RIGHT, buff = self.slider_spacing)
        sliders[0].add_numbers()
        sliders[0].set_value(
            self.center_point[0] + np.sqrt(self.total_real_estate)
        )
        self.sliders = sliders
        
        self.add_labels_to_sliders()
        self.add(sliders)

    def add_labels_to_sliders(self):
        if len(self.sliders) <= 4:
            for slider, char in zip(self.sliders, "xyzw"):
                slider.add_label(char)
            for slider in self.sliders[1:]:
                slider.label.align_to(self.sliders[0].label, UP)
        else:
            for i, slider in enumerate(self.sliders):
                slider.add_label("x_{%d}"%(i+1))
        return self

    def reset_dials(self, values, run_time = 1, **kwargs):
        target_vector = self.get_target_vect_from_subset_of_values(values, **kwargs)

        radius = np.sqrt(self.total_real_estate)
        def update_sliders(sliders):
            curr_vect = self.get_vector()
            curr_vect -= self.center_point
            curr_vect *= radius/get_norm(curr_vect)
            curr_vect += self.center_point
            self.set_to_vector(curr_vect)
            return sliders

        self.play(*[
            ApplyMethod(slider.set_value, value)
            for value, slider in zip(target_vector, self.sliders)
        ] + [
            UpdateFromFunc(self.sliders, update_sliders)
        ], run_time = run_time)

    def get_target_vect_from_subset_of_values(self, values, fixed_indices = None):
        if fixed_indices is None: 
            fixed_indices = []
        curr_vector = self.get_vector()
        target_vector = np.array(self.center_point, dtype = 'float')
        unspecified_vector = np.array(self.center_point, dtype = 'float')
        unspecified_indices = []
        for i in range(len(curr_vector)):
            if i < len(values) and values[i] is not None:
                target_vector[i] = values[i]
            else:
                unspecified_indices.append(i)
                unspecified_vector[i] = curr_vector[i]
        used_re = get_norm(target_vector - self.center_point)**2
        left_over_re = self.total_real_estate - used_re
        if left_over_re < -0.001:
            raise Exception("Overspecified reset")
        uv_norm = get_norm(unspecified_vector - self.center_point)
        if uv_norm == 0 and left_over_re > 0:
            unspecified_vector[unspecified_indices] = 1
            uv_norm = get_norm(unspecified_vector - self.center_point)
        if uv_norm > 0:
            unspecified_vector -= self.center_point
            unspecified_vector *= np.sqrt(left_over_re)/uv_norm
            unspecified_vector += self.center_point
        return target_vector + unspecified_vector - self.center_point

    def set_to_vector(self, vect):
        assert len(vect) == len(self.sliders)
        for slider, value in zip(self.sliders, vect):
            slider.set_value(value)

    def get_vector(self):
        return np.array([slider.get_value() for slider in self.sliders])

    def get_center_point(self):
        return np.array([slider.center_value for slider in self.sliders])

    def set_center_point(self, new_center_point):
        self.center_point = np.array(new_center_point)
        for x, slider in zip(new_center_point, self.sliders):
            slider.set_center_value(x)
        return self

    def get_current_total_real_estate(self):
        return sum([
            slider.get_real_estate()
            for slider in self.sliders
        ])

    def get_all_dial_supplement_animations(self):
        return [
            slider.get_dial_supplement_animation()
            for slider in self.sliders
        ]

    def initialize_ambiant_slider_movement(self):
        self.ambiently_change_sliders = True
        self.ambient_change_end_time = np.inf
        self.ambient_change_time = 0
        self.ambient_velocity, self.ambient_acceleration, self.ambient_jerk = [
            self.get_random_vector(magnitude)
            for magnitude in [
                self.ambient_velocity_magnitude,
                self.ambient_acceleration_magnitude,
                self.ambient_jerk_magnitude,
            ]
        ]
        ##Ensure counterclockwise rotations in 2D
        if len(self.ambient_velocity) == 2:
            cross = np.cross(self.get_vector(), self.ambient_velocity)
            if cross < 0:
                self.ambient_velocity *= -1
        self.add_foreground_mobjects(self.sliders)

    def wind_down_ambient_movement(self, time = 1, wait = True):
        self.ambient_change_end_time = self.ambient_change_time + time
        if wait:
            self.wait(time)
            if self.skip_animations:
                self.ambient_change_time += time

    def ambient_slider_movement_update(self):
        #Set velocity_magnitude based on start up or wind down
        velocity_magnitude = float(self.ambient_velocity_magnitude)
        if self.ambient_change_time <= 1:
            velocity_magnitude *= smooth(self.ambient_change_time)
        time_until_end = self.ambient_change_end_time - self.ambient_change_time
        if time_until_end <= 1:
            velocity_magnitude *= smooth(time_until_end)
        if time_until_end < 0:
            self.ambiently_change_sliders = False
            return

        center_point = self.get_center_point()
        target_vector = self.get_vector() - center_point
        if get_norm(target_vector) == 0:
            return
        vectors_and_magnitudes = [
            (self.ambient_acceleration, self.ambient_acceleration_magnitude),
            (self.ambient_velocity, velocity_magnitude),
            (target_vector, np.sqrt(self.total_real_estate)),
        ]
        jerk = self.get_random_vector(self.ambient_jerk_magnitude)
        deriv = jerk
        for vect, mag in vectors_and_magnitudes:
            vect += self.frame_duration*deriv
            if vect is self.ambient_velocity:
                unit_r_vect = target_vector / get_norm(target_vector)
                vect -= np.dot(vect, unit_r_vect)*unit_r_vect
            vect *= mag/get_norm(vect)
            deriv = vect

        self.set_to_vector(target_vector + center_point)
        self.ambient_change_time += self.frame_duration

    def get_random_vector(self, magnitude):
        result = 2*np.random.random(len(self.sliders)) - 1
        result *= magnitude / get_norm(result)
        return result

    def update_frame(self, *args, **kwargs):
        if self.ambiently_change_sliders:
            self.ambient_slider_movement_update()
        Scene.update_frame(self, *args, **kwargs)

    def wait(self, time = 1):
        if self.ambiently_change_sliders:
            self.play(Animation(self.sliders, run_time = time))
        else:
            Scene.wait(self,time)

##########

class MathIsATease(Scene):
    def construct(self):
        randy = Randolph()
        lashes = VGroup()
        for eye in randy.eyes:
            for angle in np.linspace(-np.pi/3, np.pi/3, 12):
                lash = Line(ORIGIN, RIGHT)
                lash.set_stroke(DARK_GREY, 2)
                lash.set_width(0.27)
                lash.next_to(ORIGIN, RIGHT, buff = 0)
                lash.rotate(angle + np.pi/2)
                lash.shift(eye.get_center())
                lashes.add(lash)
        lashes.do_in_place(lashes.stretch, 0.8, 1)
        lashes.shift(0.04*DOWN)


        fan = SVGMobject(
            file_name = "fan",
            fill_opacity = 1,
            fill_color = YELLOW,
            stroke_width = 2,
            stroke_color = YELLOW,
            height = 0.7,
        )
        VGroup(*fan[-12:]).set_fill(YELLOW_E)
        fan.rotate(-np.pi/4)
        fan.move_to(randy)
        fan.shift(0.85*UP+0.25*LEFT)

        self.add(randy)
        self.play(
            ShowCreation(lashes, lag_ratio = 0),
            randy.change, "tease",
            randy.look, OUT,
        )
        self.add_foreground_mobjects(fan)
        eye_bottom_y = randy.eyes.get_bottom()[1]
        self.play(
            ApplyMethod(
                lashes.apply_function, 
                lambda p : [p[0], eye_bottom_y, p[2]],
                rate_func = Blink.CONFIG["rate_func"],
            ),
            Blink(randy),
            DrawBorderThenFill(fan),
        )
        self.play(
            ApplyMethod(
                lashes.apply_function, 
                lambda p : [p[0], eye_bottom_y, p[2]],
                rate_func = Blink.CONFIG["rate_func"],
            ),
            Blink(randy),
        )
        self.wait()

class TODODeterminants(TODOStub):
    CONFIG = {
        "message" : "Determinants clip"
    }

class CircleToPairsOfPoints(Scene):
    def construct(self):
        plane = NumberPlane(written_coordinate_height = 0.3)
        plane.scale(2)
        plane.add_coordinates(y_vals = [-1, 1])
        background_plane = plane.copy()
        background_plane.set_color(GREY)
        background_plane.fade()
        circle = Circle(radius = 2, color = YELLOW)

        x, y = [np.sqrt(2)/2]*2
        dot = Dot(2*x*RIGHT + 2*y*UP, color = LIGHT_GREY)

        equation = TexMobject("x", "^2", "+", "y", "^2", "=", "1")
        equation.set_color_by_tex("x", GREEN)
        equation.set_color_by_tex("y", RED)
        equation.to_corner(UP+LEFT)
        equation.add_background_rectangle()

        coord_pair = TexMobject("(", "-%.02f"%x, ",", "-%.02f"%y, ")") 
        fixed_numbers = coord_pair.get_parts_by_tex("-")
        fixed_numbers.set_fill(opacity = 0)
        coord_pair.add_background_rectangle()
        coord_pair.next_to(dot, UP+RIGHT, SMALL_BUFF)
        numbers = VGroup(*[
            DecimalNumber(val).replace(num, dim_to_match = 1)
            for val, num in zip([x, y], fixed_numbers)
        ])
        numbers[0].set_color(GREEN)
        numbers[1].set_color(RED)

        def get_update_func(i):
            return lambda t : dot.get_center()[i]/2.0


        self.add(background_plane, plane)
        self.play(ShowCreation(circle))
        self.play(
            FadeIn(coord_pair),
            Write(numbers, run_time = 1),
            ShowCreation(dot),
        )
        self.play(
            Write(equation),
            *[
                Transform(
                    number.copy(),
                    equation.get_parts_by_tex(tex),
                    remover = True
                )
                for tex, number in zip("xy", numbers)
            ]
        )
        self.play(FocusOn(dot, run_time = 1))
        self.play(
            Rotating(
                dot, run_time = 7, in_place = False,
                rate_func = smooth,
            ),
            MaintainPositionRelativeTo(coord_pair, dot),
            *[
                ChangingDecimal(
                    num, get_update_func(i),
                    tracked_mobject = fixed_num
                )
                for num, i, fixed_num in zip(
                    numbers, (0, 1), fixed_numbers
                )
            ]
        )
        self.wait()

        ######### Rotation equations ##########

        rot_equation = TexMobject(
            "\\Rightarrow"
            "\\big(\\cos(\\theta)x - \\sin(\\theta)y\\big)^2 + ",
            "\\big(\\sin(\\theta)x + \\cos(\\theta)y\\big)^2 = 1",
        )
        rot_equation.scale(0.9)
        rot_equation.next_to(equation, RIGHT)
        rot_equation.add_background_rectangle()

        words = TextMobject("Rotational \\\\ symmetry")
        words.next_to(ORIGIN, UP)
        words.to_edge(RIGHT)
        words.add_background_rectangle()

        arrow = Arrow(
            words.get_left(), rot_equation.get_bottom(),
            path_arc = -np.pi/6
        )
        randy = Randolph(color = GREY_BROWN)
        randy.to_corner(DOWN+LEFT)

        self.play(
            Write(rot_equation, run_time = 2),
            FadeOut(coord_pair),
            FadeOut(numbers),
            FadeOut(dot),
            FadeIn(randy)
        )
        self.play(randy.change, "confused", rot_equation)
        self.play(Blink(randy))
        self.play(
            Write(words, run_time = 1),
            ShowCreation(arrow),
            randy.look_at, words
        )
        plane.remove(*plane.coordinate_labels)
        self.play(
            Rotate(
                plane, np.pi/3, 
                run_time = 4,
                rate_func = there_and_back
            ),
            Animation(equation),
            Animation(rot_equation),
            Animation(words),
            Animation(arrow),
            Animation(circle),
            randy.change, "hooray"
        )
        self.wait()

class GreatSourceOfMaterial(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "It's a great source \\\\ of material.",
            target_mode = "hooray"
        )
        self.change_student_modes(*["happy"]*3)
        self.wait(3)

class CirclesSpheresSumsSquares(ExternallyAnimatedScene):
    pass

class BackAndForth(Scene):
    def construct(self):
        analytic = TextMobject("Analytic")
        analytic.shift(FRAME_X_RADIUS*LEFT/2)
        analytic.to_edge(UP, buff = MED_SMALL_BUFF)
        geometric = TextMobject("Geometric")
        geometric.shift(FRAME_X_RADIUS*RIGHT/2)
        geometric.to_edge(UP, buff = MED_SMALL_BUFF)
        h_line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS)
        h_line.to_edge(UP, LARGE_BUFF)
        v_line = Line(UP, DOWN).scale(FRAME_Y_RADIUS)
        self.add(analytic, geometric, h_line, v_line)

        pair = TexMobject("(", "x", ",", "y", ")")
        pair.shift(FRAME_X_RADIUS*LEFT/2 + FRAME_Y_RADIUS*UP/3)
        triplet = TexMobject("(", "x", ",", "y", ",", "z", ")")
        triplet.shift(FRAME_X_RADIUS*LEFT/2 + FRAME_Y_RADIUS*DOWN/2)
        for mob in pair, triplet:
            arrow = DoubleArrow(LEFT, RIGHT)
            arrow.move_to(mob)
            arrow.shift(2*RIGHT)
            mob.arrow = arrow
        circle_eq = TexMobject("x", "^2", "+", "y", "^2", "=", "1")
        circle_eq.move_to(pair)
        sphere_eq = TexMobject("x", "^2", "+", "y", "^2", "+", "z", "^2", "=", "1")
        sphere_eq.move_to(triplet)

        plane = NumberPlane(x_unit_size = 2, y_unit_size = 2)
        circle = Circle(radius = 2, color = YELLOW)
        plane_group = VGroup(plane, circle)
        plane_group.scale(0.4)
        plane_group.next_to(h_line, DOWN, SMALL_BUFF)
        plane_group.shift(FRAME_X_RADIUS*RIGHT/2)


        self.play(Write(pair))
        # self.play(ShowCreation(pair.arrow))
        self.play(ShowCreation(plane, run_time = 3))
        self.play(Write(triplet))
        # self.play(ShowCreation(triplet.arrow))
        self.wait(3)
        for tup, eq, to_draw in (pair, circle_eq, circle), (triplet, sphere_eq, VMobject()):
            for mob in tup, eq:
                mob.xyz = VGroup(*[sm for sm in map(mob.get_part_by_tex, "xyz") if sm is not None])
            self.play(
                ReplacementTransform(tup.xyz, eq.xyz),
                FadeOut(VGroup(*[sm for sm in tup if sm not in tup.xyz])),
            )
            self.play(
                Write(VGroup(*[sm for sm in eq if sm not in eq.xyz])),
                ShowCreation(to_draw)
            )
        self.wait(3)

class SphereForming(ExternallyAnimatedScene):
    pass

class PreviousVideos(Scene):
    def construct(self):
        titles = VGroup(*list(map(TextMobject, [
            "Pi hiding in prime regularities",
            "Visualizing all possible pythagorean triples",
            "Borsuk-Ulam theorem",
        ])))
        titles.to_edge(UP, buff = MED_SMALL_BUFF)
        screen = ScreenRectangle(height = 6)
        screen.next_to(titles, DOWN)

        title = titles[0]
        self.add(title, screen)
        self.wait(2)
        for new_title in titles[1:]:
            self.play(Transform(title, new_title))
            self.wait(2)

class TODOTease(TODOStub):
    CONFIG = {
        "message" : "Tease"
    }

class AskAboutLongerLists(TeacherStudentsScene):
    def construct(self):
        question = TextMobject(
            "What about \\\\", 
            "$(x_1, x_2, x_3, x_4)?$"
        )
        tup = question[1]
        alt_tups = list(map(TextMobject, [
            "$(x_1, x_2, x_3, x_4, x_5)?$",
            "$(x_1, x_2, \\dots, x_{99}, x_{100})?$"
        ]))

        self.student_says(question, run_time = 1)
        self.wait()
        for alt_tup in alt_tups:
            alt_tup.move_to(tup)
            self.play(Transform(tup, alt_tup))
            self.wait()
        self.wait()
        self.play(
            RemovePiCreatureBubble(self.students[1]),
            self.teacher.change, "raise_right_hand"
        )
        self.change_student_modes(
            *["confused"]*3,
            look_at_arg = self.teacher.get_top() + 2*UP
        )
        self.play(self.teacher.look, UP)
        self.wait(5)
        self.student_says(
            "I...don't see it.",
            target_mode = "maybe",
            student_index = 0
        )
        self.wait(3)

class FourDCubeRotation(ExternallyAnimatedScene):
    pass

class HypersphereRotation(ExternallyAnimatedScene):
    pass

class FourDSurfaceRotating(ExternallyAnimatedScene):
    pass

class Professionals(PiCreatureScene):
    def construct(self):
        self.introduce_characters()
        self.add_equation()
        self.analogies()

    def introduce_characters(self):
        titles = VGroup(*list(map(TextMobject, [
            "Mathematician",
            "Computer scientist",
            "Physicist",
        ])))
        self.remove(*self.pi_creatures)
        for title, pi in zip(titles, self.pi_creatures):
            title.next_to(pi, DOWN)
            self.play(
                Animation(VectorizedPoint(pi.eyes.get_center())),
                FadeIn(pi),
                Write(title, run_time = 1),
            )
        self.wait()

    def add_equation(self):
        quaternion = TexMobject(
            "\\frac{1}{2}", "+", 
            "0", "\\textbf{i}", "+",
            "\\frac{\\sqrt{6}}{4}", "\\textbf{j}", "+",
            "\\frac{\\sqrt{6}}{4}", "\\textbf{k}",
        )
        quaternion.scale(0.7)
        quaternion.next_to(self.mathy, UP)
        quaternion.set_color_by_tex_to_color_map({
            "i" : RED,
            "j" : GREEN,
            "k" : BLUE,
        })

        array = TexMobject("[a_1, a_2, \\dots, a_{100}]")
        array.next_to(self.compy, UP)

        kets = TexMobject(
            "\\alpha",
            "|\\!\\uparrow\\rangle + ",
            "\\beta",
            "|\\!\\downarrow\\rangle"
        )
        kets.set_color_by_tex_to_color_map({
            "\\alpha" : GREEN,
            "\\beta" : RED,
        })
        kets.next_to(self.physy, UP)


        terms = VGroup(quaternion, array, kets)
        for term, pi in zip(terms, self.pi_creatures):
            self.play(
                Write(term, run_time = 1),
                pi.change, "pondering", term
            )
        self.wait(2)

        self.terms = terms

    def analogies(self):
        examples = VGroup()
        plane = ComplexPlane(
            x_radius = 2.5,
            y_radius = 1.5,
        )
        plane.add_coordinates()
        plane.add(Circle(color = YELLOW))
        plane.scale(0.75)
        examples.add(plane)
        examples.add(Circle())
        examples.arrange(RIGHT, buff = 2)
        examples.to_edge(UP, buff = LARGE_BUFF)
        labels = VGroup(*list(map(TextMobject, ["2D", "3D"])))

        title = TextMobject("Fly by instruments")
        title.scale(1.5)
        title.to_edge(UP)

        for label, example in zip(labels, examples):
            label.next_to(example, DOWN)
            self.play(
                ShowCreation(example),
                Write(label, run_time = 1)
            )
            example.add(label)
            self.wait()
        self.wait()
        self.play(
            FadeOut(examples),
            self.terms.shift, UP,
            Write(title, run_time = 2)
        )
        self.play(*[
            ApplyMethod(
                pi.change, mode, self.terms.get_left(),
                run_time = 2,
                rate_func = squish_rate_func(smooth, a, a+0.5)
            )
            for pi, mode, a in zip(
                self.pi_creatures, 
                ["confused", "sassy", "erm"],
                np.linspace(0, 0.5, len(self.pi_creatures))
            )
        ])
        self.wait()
        self.play(Animation(self.terms[-1]))
        self.wait(2)

    ######

    def create_pi_creatures(self):
        self.mathy = Mathematician()
        self.physy = PiCreature(color = PINK)
        self.compy = PiCreature(color = PURPLE)
        pi_creatures = VGroup(self.mathy, self.compy, self.physy)
        for pi in pi_creatures:
            pi.scale(0.7)
        pi_creatures.arrange(RIGHT, buff = 3)
        pi_creatures.to_edge(DOWN, buff = LARGE_BUFF)
        return pi_creatures

class OfferAHybrid(SliderScene):
    CONFIG = {
        "n_sliders" : 3,
    }
    def construct(self):
        self.remove(self.sliders)
        titles = self.get_titles()
        h_line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS)
        h_line.next_to(titles, DOWN)
        v_lines = VGroup(*[
            Line(UP, DOWN).scale(FRAME_Y_RADIUS)
            for x in range(2)
        ])
        v_lines.generate_target()
        for line, vect in zip(v_lines.target, [LEFT, RIGHT]):
            line.shift(vect*FRAME_X_RADIUS/3)

        equation = TexMobject("x^2 + y^2 + z^2 = 1")
        equation.generate_target()
        equation.shift(FRAME_X_RADIUS*LEFT/2)
        equation.target.shift(FRAME_WIDTH*LEFT/3)

        self.add(titles, h_line, v_lines, equation)
        self.wait()
        self.play(*list(map(MoveToTarget, [titles, v_lines, equation])))
        self.play(Write(self.sliders, run_time = 1))
        self.initialize_ambiant_slider_movement()
        self.wait(10)
        self.wind_down_ambient_movement()
        self.wait()

    def get_titles(self):
        titles = VGroup(*list(map(TextMobject, [
            "Analytic", "Hybrid", "Geometric"
        ])))
        titles.to_edge(UP)
        titles[1].set_color(BLUE)
        titles.generate_target()
        titles[1].scale_in_place(0.001)
        titles[0].shift(FRAME_X_RADIUS*LEFT/2)
        titles.target[0].shift(FRAME_WIDTH*LEFT/3)
        titles[2].shift(FRAME_X_RADIUS*RIGHT/2)
        titles.target[2].shift(FRAME_WIDTH*RIGHT/3)
        return titles

class TODOBoxExample(TODOStub):
    CONFIG = {
        "message" : "Box Example"
    }

class RotatingSphereWithWanderingPoint(ExternallyAnimatedScene):
    pass

class DismissProjection(PiCreatureScene):
    CONFIG = { 
        "screen_rect_color" : WHITE,
        "example_vect" : np.array([0.52, 0.26, 0.53, 0.60]),
    }
    def construct(self):
        self.remove(self.pi_creature)
        self.show_all_spheres()
        self.discuss_4d_sphere_definition()
        self.talk_through_animation()
        self.transition_to_next_scene()
        
    def show_all_spheres(self):
        equations = VGroup(*list(map(TexMobject, [
            "x^2 + y^2 = 1",
            "x^2 + y^2 + z^2 = 1",
            "x^2 + y^2 + z^2 + w^2 = 1",
        ])))
        colors = [YELLOW, GREEN, BLUE]
        for equation, edge, color in zip(equations, [LEFT, ORIGIN, RIGHT], colors):
            equation.set_color(color)
            equation.shift(3*UP)
            equation.to_edge(edge)
        equations[1].shift(LEFT)

        spheres = VGroup(
            self.get_circle(equations[0]),
            self.get_sphere_screen(equations[1], DOWN),
            self.get_sphere_screen(equations[2], DOWN),
        )
        
        for equation, sphere in zip(equations, spheres):
            self.play(
                Write(equation),
                LaggedStartMap(ShowCreation, sphere),
            )
        self.wait()

        self.equations = equations
        self.spheres = spheres

    def get_circle(self, equation):
        result = VGroup(
            NumberPlane(
                x_radius = 2.5,
                y_radius = 2,
            ).fade(0.4),
            Circle(color = YELLOW, radius = 1),
        )
        result.scale(0.7)
        result.next_to(equation, DOWN)
        return result

    def get_sphere_screen(self, equation, vect):
        square = Rectangle()
        square.set_width(equation.get_width())
        square.stretch_to_fit_height(3)
        square.next_to(equation, vect)
        square.set_color(self.screen_rect_color)
        return square

    def discuss_4d_sphere_definition(self):
        sphere = self.spheres[-1]
        equation = self.equations[-1]

        sphere_words = TextMobject("``4-dimensional sphere''")
        sphere_words.next_to(sphere, DOWN+LEFT, buff = LARGE_BUFF)
        arrow = Arrow(
            sphere_words.get_right(), sphere.get_bottom(), 
            path_arc = np.pi/3, 
            color = BLUE
        )
        descriptor = TexMobject(
            "\\text{Just lists of numbers like }", 
            "(%.02f \\,, %.02f \\,, %.02f \\,, %.02f \\,)"%tuple(self.example_vect)
        )
        descriptor[1].set_color(BLUE)
        descriptor.next_to(sphere_words, DOWN)
        dot = Dot(descriptor[1].get_top())
        dot.set_fill(WHITE, opacity = 0.75)

        self.play(
            Write(sphere_words),
            ShowCreation(
                arrow,
                rate_func = squish_rate_func(smooth, 0.5, 1)
            ),
            run_time = 3,
        )
        self.wait()
        self.play(Write(descriptor, run_time = 2))
        self.wait()
        self.play(
            dot.move_to, equation.get_left(),
            dot.set_fill, None, 0,
            path_arc = -np.pi/12
        )
        self.wait(2)

        self.sphere_words = sphere_words
        self.sphere_arrow = arrow
        self.descriptor = descriptor

    def talk_through_animation(self):
        sphere = self.spheres[-1]

        morty = self.pi_creature
        alt_dims = VGroup(*list(map(TextMobject, ["5D", "6D", "7D"])))
        alt_dims.next_to(morty.eyes, UP, SMALL_BUFF)
        alt_dim = alt_dims[0]

        self.play(FadeIn(morty))
        self.play(morty.change, "raise_right_hand", sphere)
        self.wait(3)
        self.play(morty.change, "confused", sphere)
        self.wait(3)
        self.play(
            morty.change, "erm", alt_dims,
            FadeIn(alt_dim)
        )
        for new_alt_dim in alt_dims[1:]:
            self.wait()
            self.play(Transform(alt_dim, new_alt_dim))
        self.wait()
        self.play(morty.change, "concerned_musician")
        self.play(FadeOut(alt_dim))
        self.wait()
        self.play(morty.change, "angry", sphere)
        self.wait(2)

    def transition_to_next_scene(self):
        equation = self.equations[-1]
        self.equations.remove(equation)
        tup = self.descriptor[1]
        self.descriptor.remove(tup)

        equation.generate_target()
        equation.target.center().to_edge(UP)
        tup.generate_target()
        tup.target.next_to(equation.target, DOWN)
        tup.target.set_color(WHITE)

        self.play(LaggedStartMap(FadeOut, VGroup(*[
            self.equations, self.spheres,
            self.sphere_words, self.sphere_arrow,
            self.descriptor,
            self.pi_creature
        ])))
        self.play(*list(map(MoveToTarget, [equation, tup])))
        self.wait()

    ###

    def create_pi_creature(self):
        return Mortimer().scale(0.8).to_corner(DOWN+RIGHT)

class RotatingSphere(ExternallyAnimatedScene):
    pass

class Introduce4DSliders(SliderScene):
    CONFIG = {
        "slider_config" : {
            "include_real_estate_ticks" : False,
            "numbers_with_elongated_ticks" : [-1, 0, 1],
            "tick_frequency" : 0.25,
            "tick_size" : 0.05,
            "dial_color" : YELLOW,
        },
        "slider_spacing" : LARGE_BUFF,
    }
    def construct(self):
        self.match_last_scene()
        self.introduce_sliders()
        self.ask_about_constraint()

    def match_last_scene(self):
        self.start_vect = DismissProjection.CONFIG["example_vect"]
        self.remove(self.sliders)

        equation = TexMobject("x^2 + y^2 + z^2 + w^2 = 1")
        x, y, z, w = self.start_vect
        tup = TexMobject(
            "(", "%.02f \\,"%x, 
            ",", "%.02f \\,"%y, 
            ",", "%.02f \\,"%z, 
            ",", "%.02f \\,"%w, ")"
        )
        equation.center().to_edge(UP)
        equation.set_color(BLUE)
        tup.next_to(equation, DOWN)

        self.sliders.next_to(tup, DOWN)
        self.sliders.shift(0.8*LEFT)

        self.add(equation, tup)
        self.wait()
        self.equation = equation
        self.tup = tup

    def introduce_sliders(self):
        self.set_to_vector(self.start_vect)

        numbers = self.tup.get_parts_by_tex(".")
        self.tup.remove(*numbers)
        dials = VGroup(*[slider.dial for slider in self.sliders])
        dial_copies = dials.copy()
        dials.set_fill(opacity = 0)

        self.play(LaggedStartMap(FadeIn, self.sliders))
        self.play(*[
            Transform(
                num, dial,
                run_time = 3,
                rate_func = squish_rate_func(smooth, a, a+0.5),
                remover = True
            )
            for num, dial, a in zip(
                numbers, dial_copies, 
                np.linspace(0, 0.5, len(numbers))
            )
        ])
        dials.set_fill(opacity = 1)
        self.initialize_ambiant_slider_movement()
        self.play(FadeOut(self.tup))
        self.wait(10)

    def ask_about_constraint(self):
        equation = self.equation
        rect = SurroundingRectangle(equation, color = GREEN)
        randy = Randolph().scale(0.5)
        randy.next_to(rect, DOWN+LEFT, LARGE_BUFF)

        self.play(ShowCreation(rect))
        self.play(FadeIn(randy))
        self.play(randy.change, "pondering", rect)
        self.wait()
        for mob in self.sliders, rect:
            self.play(randy.look_at, mob)
            self.play(Blink(randy))
            self.wait()
        self.wait()

class TwoDimensionalCase(Introduce4DSliders):
    CONFIG = {
        "n_sliders" : 2,
    }
    def setup(self):
        SliderScene.setup(self)
        self.sliders.shift(RIGHT)
        for number in self.sliders[0].numbers:
            value = int(number.get_tex_string())
            number.move_to(center_of_mass([
                slider.number_to_point(value)
                for slider in self.sliders
            ]))

        plane = NumberPlane(
            x_radius = 2.5,
            y_radius = 2.5,
        )
        plane.fade(0.25)
        plane.axes.set_color(GREY)
        plane.add_coordinates()
        plane.to_edge(LEFT)
        origin = plane.coords_to_point(0, 0)

        circle = Circle(radius = 1, color = WHITE)
        circle.move_to(plane.coords_to_point(*self.center_point))

        dot = Dot(color = YELLOW)
        dot.move_to(plane.coords_to_point(1, 0))

        equation = TexMobject("x^2 + y^2 = 1")
        equation.to_corner(UP + RIGHT)

        self.add(plane, circle, dot, equation)
        self.add_foreground_mobjects(dot)

        self.plane = plane
        self.circle = circle
        self.dot = dot
        self.equation = equation

    def construct(self):
        self.let_values_wander()
        self.introduce_real_estate()
        self.let_values_wander(6)
        self.comment_on_cheap_vs_expensive_real_estate()
        self.nudge_x_from_one_example()
        self.note_circle_steepness()
        self.add_tick_marks()
        self.write_distance_squared()

    def let_values_wander(self, total_time = 5):
        self.initialize_ambiant_slider_movement()
        self.wait(total_time - 1)
        self.wind_down_ambient_movement()

    def introduce_real_estate(self):
        x_squared_mob = VGroup(*self.equation[:2])
        y_squared_mob = VGroup(*self.equation[3:5])
        x_rect = SurroundingRectangle(x_squared_mob)
        y_rect = SurroundingRectangle(y_squared_mob)
        rects = VGroup(x_rect, y_rect)

        decimals = VGroup(*[
            DecimalNumber(num**2) 
            for num in self.get_vector()
        ])
        decimals.arrange(RIGHT, buff = LARGE_BUFF)
        decimals.next_to(rects, DOWN, LARGE_BUFF)

        real_estate_word = TextMobject("``Real estate''")
        real_estate_word.next_to(decimals, DOWN, MED_LARGE_BUFF)
        self.play(FadeIn(real_estate_word))

        colors = GREEN, RED
        arrows = VGroup()
        for rect, decimal, color in zip(rects, decimals, colors):
            rect.set_color(color)
            decimal.set_color(color)
            arrow = Arrow(
                rect.get_bottom()+SMALL_BUFF*UP, decimal.get_top(),
                tip_length = 0.2,
            )
            arrow.set_color(color)
            arrows.add(arrow)

            self.play(ShowCreation(rect))
            self.play(
                ShowCreation(arrow),
                Write(decimal)
            )
            self.wait()

        sliders = self.sliders
        def create_update_func(i):
            return lambda alpha : sliders[i].get_real_estate()

        self.add_foreground_mobjects(decimals)
        self.decimals = decimals
        self.decimal_update_anims = [
            ChangingDecimal(decimal, create_update_func(i))
            for i, decimal in enumerate(decimals)
        ]
        self.real_estate_word = real_estate_word

    def comment_on_cheap_vs_expensive_real_estate(self):
        blue_rects = VGroup()
        red_rects = VGroup()
        for slider in self.sliders:
            for x1, x2 in (-0.5, 0.5), (0.75, 1.0), (-1.0, -0.75):
                p1, p2 = list(map(slider.number_to_point, [x1, x2]))
                rect = Rectangle(
                    stroke_width = 0,
                    fill_opacity = 0.5,
                    width = 0.25,
                    height = (p2-p1)[1]
                )
                rect.move_to((p1+p2)/2)
                if np.mean([x1, x2]) == 0:
                    rect.set_color(BLUE)
                    blue_rects.add(rect)
                else:
                    rect.set_color(RED)
                    red_rects.add(rect)

        blue_rects.save_state()
        self.play(DrawBorderThenFill(blue_rects))
        self.wait()
        self.play(ReplacementTransform(blue_rects, red_rects))
        self.wait()
        self.play(FadeOut(red_rects))

        blue_rects.restore()
        self.real_estate_rects = VGroup(blue_rects, red_rects)

    def nudge_x_from_one_example(self):
        x_re = self.decimals[0]
        rect = SurroundingRectangle(x_re)

        self.reset_dials([1, 0])
        self.wait()
        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))
        self.play(FocusOn(self.dot))
        self.wait()
        self.reset_dials([0.9, -np.sqrt(0.19)])

        x_brace, y_brace = [
            Brace(
                VGroup(slider.dial, Dot(slider.number_to_point(0))),
                vect
            )
            for slider, vect in zip(self.sliders, [LEFT, RIGHT])
        ]
        x_text = x_brace.get_tex("0.9")
        y_text = y_brace.get_tex("%.02f"%self.sliders[1].get_value())

        self.play(
            GrowFromCenter(x_brace),
            Write(x_text)
        )
        self.play(ReplacementTransform(
            VGroup(x_text.copy()), x_re
        ))
        self.wait(2)
        self.play(
            GrowFromCenter(y_brace),
            Write(y_text),
        )
        self.wait(2)
        self.play(FadeIn(self.real_estate_rects))
        self.reset_dials([1, 0], run_time = 1)
        self.reset_dials([0.9, -np.sqrt(0.19)], run_time = 2)
        self.play(FadeOut(self.real_estate_rects))
        self.play(*list(map(FadeOut, [x_brace, y_brace, x_text, y_text])))
        self.wait()

    def note_circle_steepness(self):
        line = Line(
            self.plane.coords_to_point(0.5, 1),
            self.plane.coords_to_point(1.5, -1),
        )
        rect = Rectangle(
            stroke_width = 0,
            fill_color = BLUE,
            fill_opacity = 0.5,
        )
        rect.replace(line, stretch = True)

        self.play(DrawBorderThenFill(rect, stroke_color = YELLOW))
        for x, u in (1, 1), (0.8, 1), (1, 1), (0.8, -1), (1, 1):
            self.reset_dials([x, u*np.sqrt(1 - x**2)])
        self.play(FadeOut(rect))

    def add_tick_marks(self):
        self.remove_foreground_mobjects(self.sliders)
        self.add(self.sliders)
        old_ticks = VGroup()
        all_ticks = VGroup()
        for slider in self.sliders:
            slider.tick_size = 0.1
            slider.add_real_estate_ticks()
            slider.remove(slider.get_tick_marks())
            all_ticks.add(*slider.real_estate_ticks)
            old_ticks.add(*slider.get_tick_marks()[:-3])

        self.play(
            FadeOut(old_ticks),
            ShowCreation(all_ticks, run_time = 3),
            Animation(VGroup(*[slider.dial for slider in self.sliders])),
        )
        self.add_foreground_mobjects(self.sliders)
        self.wait()
        for x in np.arange(0.95, 0.05, -0.05):
            self.reset_dials(
                [np.sqrt(x), np.sqrt(1-x)],
                run_time = 0.5
            )
            self.wait(0.5)
        self.initialize_ambiant_slider_movement()
        self.wait(10)

    def write_distance_squared(self):
        d_squared = TexMobject("(\\text{Distance})^2")
        d_squared.next_to(self.real_estate_word, DOWN)
        d_squared.set_color(YELLOW)

        self.play(Write(d_squared))
        self.wait(3)

    #####

    def update_frame(self, *args, **kwargs):
        if hasattr(self, "dot"):
            x, y = self.get_vector()
            self.dot.move_to(self.plane.coords_to_point(x, y))
        if hasattr(self, "decimals"):
            for anim in self.decimal_update_anims:
                anim.update(0)
        SliderScene.update_frame(self, *args, **kwargs)

class TwoDimensionalCaseIntro(TwoDimensionalCase):
    def construct(self):
        self.initialize_ambiant_slider_movement()
        self.wait(10)

class ThreeDCase(TwoDimensionalCase):
    CONFIG = { 
        "n_sliders" : 3,
        "slider_config" : {
            "include_real_estate_ticks" : True,
            "numbers_with_elongated_ticks" : [],
            "tick_frequency" : 1,
            "tick_size" : 0.1,
        },
    }
    def setup(self):
        SliderScene.setup(self)
        self.equation = TexMobject(
            "x^2", "+", "y^2", "+", "z^2", "=", "1"
        )
        self.equation.to_corner(UP+RIGHT)
        self.add(self.equation)

    def construct(self):
        self.force_skipping()

        self.add_real_estate_decimals()
        self.initialize_ambiant_slider_movement()
        self.point_out_third_slider()
        self.wait(3)
        self.hold_x_at(0.5, 12)
        self.revert_to_original_skipping_status()
        self.hold_x_at(0.85, 12)
        return
        self.hold_x_at(1, 5)

    def add_real_estate_decimals(self):
        rects = VGroup(*[
            SurroundingRectangle(self.equation.get_part_by_tex(char))
            for char in "xyz"
        ])

        decimals = VGroup(*[
            DecimalNumber(num**2)
            for num in self.get_vector()
        ])
        decimals.arrange(RIGHT, buff = LARGE_BUFF)
        decimals.next_to(rects, DOWN, LARGE_BUFF)

        colors = [GREEN, RED, BLUE]
        arrows = VGroup()
        for rect, decimal, color in zip(rects, decimals, colors):
            rect.set_color(color)
            decimal.set_color(color)
            arrow = Arrow(
                rect.get_bottom()+SMALL_BUFF*UP, decimal.get_top(),
                tip_length = 0.2,
                color = color
            )
            arrows.add(arrow)
        real_estate_word = TextMobject("``Real estate''")
        real_estate_word.next_to(decimals, DOWN, MED_LARGE_BUFF)

        sliders = self.sliders
        def create_update_func(i):
            return lambda alpha : sliders[i].get_real_estate()
        self.add_foreground_mobjects(decimals)
        self.decimals = decimals
        self.decimal_update_anims = [
            ChangingDecimal(decimal, create_update_func(i))
            for i, decimal in enumerate(decimals)
        ]
        self.add(rects, arrows, real_estate_word)
        self.rects = rects
        self.arrows = arrows
        self.real_estate_word = real_estate_word

    def point_out_third_slider(self):
        rect = SurroundingRectangle(self.sliders[-1])
        self.wait(4)
        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))
        self.wait(8)

    def hold_x_at(self, x_val, wait_time):
        #Save these
        all_sliders = self.sliders
        original_total_real_estate = self.total_real_estate

        self.reset_dials([x_val], run_time = 3)
        self.sliders = VGroup(*self.sliders[1:])
        self.total_real_estate = self.total_real_estate-x_val**2
        self.initialize_ambiant_slider_movement()
        self.wait(wait_time-2)
        self.wind_down_ambient_movement()
        self.sliders = all_sliders
        self.total_real_estate = original_total_real_estate
        self.initialize_ambiant_slider_movement()

    ####

class ThreeDCaseInsert(ThreeDCase):
    def construct(self):
        self.add_real_estate_decimals()
        self.reset_dials([0.85, np.sqrt(1-0.85**2)], run_time = 0)
        self.reset_dials([1], run_time = 3)
        self.wait()

class SphereAtRest(ExternallyAnimatedScene):
    pass

class BugOnASurface(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("You're a bug \\\\ on a surface")
        self.wait(3)

class SphereWithWanderingDotAtX0point5(ExternallyAnimatedScene):
    pass

class MoveSphereSliceFromPoint5ToPoint85(ExternallyAnimatedScene):
    pass

class SphereWithWanderingDotAtX0point85(ExternallyAnimatedScene):
    pass

class MoveSphereSliceFromPoint85To1(ExternallyAnimatedScene):
    pass

class BugOnTheSurfaceSlidersPart(ThreeDCase):
    CONFIG = {
        "run_time" : 30
    }
    def construct(self):
        self.add_real_estate_decimals()
        self.reset_dials([0.9], run_time = 0)
        time_range = np.arange(0, self.run_time, self.frame_duration)
        for time in ProgressDisplay(time_range):
            t = 0.3*np.sin(2*np.pi*time/7.0) + 1
            u = 0.3*np.sin(4*np.pi*time/7.0) + 1.5
            self.set_to_vector([
                np.cos(u),
                np.sin(u)*np.cos(t),
                np.sin(u)*np.sin(t),
            ])
            self.wait(self.frame_duration)

class BugOnTheSurfaceSpherePart(ExternallyAnimatedScene):
    pass

class FourDCase(SliderScene, TeacherStudentsScene):
    def setup(self):
        TeacherStudentsScene.setup(self)
        SliderScene.setup(self)
        self.sliders.scale(0.9)
        self.sliders.to_edge(UP)
        self.sliders.shift(2*RIGHT)
        self.initialize_ambiant_slider_movement()

    def construct(self):
        self.show_initial_exchange()
        self.fix_one_slider()
        self.ask_now_what()
        self.set_aside_sliders()

    def show_initial_exchange(self):
        dot = Dot(fill_opacity = 0)
        dot.to_corner(UP+LEFT, buff = 2)
        self.play(Animation(dot))
        self.wait()
        self.play(
            Animation(self.sliders),
            self.teacher.change, "raise_right_hand",
        )
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = self.sliders
        )
        self.wait(4)

    def fix_one_slider(self):
        x_slider = self.sliders[0]
        dial = x_slider.dial
        self.wind_down_ambient_movement(wait = False)
        self.play(self.teacher.change, "speaking")
        self.sliders.remove(x_slider)
        self.total_real_estate = get_norm(self.get_vector())**2
        self.initialize_ambiant_slider_movement()
        arrow = Arrow(LEFT, RIGHT, color = GREEN)
        arrow.next_to(dial, LEFT)
        self.play(
            ShowCreation(arrow),
            dial.set_color, arrow.get_color()
        )
        self.change_student_modes(
            "erm", "confused", "hooray",
            look_at_arg = self.sliders,
            added_anims = [self.teacher.change, "plain"]
        )
        self.wait(5)

        self.x_slider = x_slider
        self.x_arrow = arrow

    def ask_now_what(self):
        self.student_says(
            "Okay...now what?",
            target_mode = "raise_left_hand",
            student_index = 0,
            added_anims = [self.teacher.change, "plain"]
        )
        self.change_student_modes(
            None, "pondering", "pondering",
            look_at_arg = self.students[0].bubble,
        )
        self.wait(4)
        self.play(RemovePiCreatureBubble(self.students[0]))

    def set_aside_sliders(self):
        self.sliders.add(self.x_slider)
        self.total_real_estate = 1
        self.initialize_ambiant_slider_movement()
        self.play(
            self.sliders.scale, 0.5,
            self.sliders.to_corner, UP+RIGHT,
            FadeOut(self.x_arrow)
        )
        self.teacher_says(
            "Time for some \\\\ high-dimensional \\\\ strangeness!",
            target_mode = "hooray",
        )
        self.wait(7)

    #####
    def non_blink_wait(self, time = 1):
        SliderScene.wait(self, time)

class TwoDBoxExample(Scene):
    def setup(self):
        scale_factor = 1.7
        self.plane = NumberPlane()
        self.plane.scale(scale_factor)
        self.plane.add_coordinates()
        self.plane.axes.set_color(GREY)
        self.add(self.plane)

    def construct(self):
        self.add_box()
        self.label_corner_coordinates()
        self.add_corner_circles()
        self.add_center_circle()
        self.compute_radius()

    def add_box(self):
        box = Square(color = RED, stroke_width = 6)
        line = Line(
            self.plane.coords_to_point(-1, -1),
            self.plane.coords_to_point(1, 1),
        )
        box.replace(line, stretch = True)
        self.play(ShowCreation(box))
        self.wait()

    def label_corner_coordinates(self):
        corner_dots = VGroup()
        coords_group = VGroup()
        for x, y in it.product(*[[1, -1]]*2):
            point = self.plane.coords_to_point(x, y)
            dot = Dot(point, color = WHITE)
            coords = TexMobject("(%d, %d)"%(x, y))
            coords.add_background_rectangle()
            coords.next_to(point, point, SMALL_BUFF)
            corner_dots.add(dot)
            coords_group.add(coords)

            self.play(
                ShowCreation(dot),
                Write(coords, run_time = 1)
            )

        self.add_foreground_mobjects(coords_group)
        self.corner_dots = corner_dots
        self.coords_group = coords_group

    def add_corner_circles(self):
        line = Line(
            self.plane.coords_to_point(-1, 0),
            self.plane.coords_to_point(1, 0),
        )
        circle = Circle(color = YELLOW)
        circle.replace(line, dim_to_match = 0)
        circles = VGroup(*[
            circle.copy().move_to(dot)
            for dot in self.corner_dots
        ])

        radius = Line(ORIGIN, self.plane.coords_to_point(1, 0))
        radius.set_stroke(GREY, 6)
        radius.rotate(-np.pi/4)
        c0_center = circles[0].get_center()
        radius.shift(c0_center)
        r_equals_1 = TexMobject("r = 1")
        r_equals_1.add_background_rectangle()
        r_equals_1.next_to(
            radius.point_from_proportion(0.75),
            UP+RIGHT, SMALL_BUFF
        )

        self.play(LaggedStartMap(ShowCreation, circles))
        self.play(
            ShowCreation(radius),
            Write(r_equals_1)
        )
        for angle in -np.pi/4, -np.pi/2, 3*np.pi/4:
            self.play(Rotating(
                radius, about_point = c0_center,
                radians = angle,
                run_time = 1,
                rate_func = smooth,
            ))
            self.wait(0.5)
        self.play(*list(map(FadeOut, [radius, r_equals_1])))
        self.wait()

        self.corner_radius = radius
        self.corner_circles = circles

    def add_center_circle(self):
        r = np.sqrt(2) - 1
        radius = Line(ORIGIN, self.plane.coords_to_point(r, 0))
        radius.set_stroke(WHITE)
        circle = Circle(color = GREEN)
        circle.replace(
            VGroup(radius, radius.copy().rotate(np.pi)),
            dim_to_match = 0
        )
        radius.rotate(np.pi/4)
        r_equals_q = TexMobject("r", "= ???")
        r_equals_q[1].add_background_rectangle()
        r_equals_q.next_to(radius, RIGHT, buff = -SMALL_BUFF)

        self.play(GrowFromCenter(circle, run_time = 2))
        self.play(circle.scale, 1.2, rate_func = wiggle)
        self.play(ShowCreation(radius))
        self.play(Write(r_equals_q))
        self.wait(2)
        self.play(FadeOut(r_equals_q[1]))

        self.inner_radius = radius
        self.inner_circle = circle
        self.inner_r = r_equals_q[0]

    def compute_radius(self):
        triangle = Polygon(
            ORIGIN, 
            self.plane.coords_to_point(1, 0),
            self.plane.coords_to_point(1, 1),
            fill_color = BLUE,
            fill_opacity = 0.5,
            stroke_width = 6,
            stroke_color = WHITE,
        )
        bottom_one = TexMobject("1")
        bottom_one.next_to(triangle.get_bottom(), UP, SMALL_BUFF)
        bottom_one.shift(MED_SMALL_BUFF*RIGHT)
        side_one = TexMobject("1")
        side_one.next_to(triangle, RIGHT)
        sqrt_1_plus_1 = TexMobject("\\sqrt", "{1^2 + 1^2}")
        sqrt_2 = TexMobject("\\sqrt", "{2}")
        for sqrt in sqrt_1_plus_1, sqrt_2:
            sqrt.add_background_rectangle()
            sqrt.next_to(ORIGIN, UP, SMALL_BUFF)
            sqrt.rotate(np.pi/4)
            sqrt.shift(triangle.get_center())

        root_2_value = TexMobject("\\sqrt{2} \\approx 1.414")
        root_2_value.to_corner(UP+RIGHT)
        root_2_value.add_background_rectangle()
        root_2_minus_1_value = TexMobject(
            "\\sqrt{2} - 1 \\approx 0.414"
        )
        root_2_minus_1_value.next_to(root_2_value, DOWN)
        root_2_minus_1_value.to_edge(RIGHT)
        root_2_minus_1_value.add_background_rectangle()

        corner_radius = self.corner_radius
        c0_center = self.corner_circles[0].get_center()
        corner_radius.rotate(-np.pi/2, about_point = c0_center)

        rhs = TexMobject("=", "\\sqrt", "{2}", "-1")
        rhs.next_to(self.inner_r, RIGHT, SMALL_BUFF, DOWN)
        rhs.shift(0.5*SMALL_BUFF*DOWN)
        sqrt_2_target = VGroup(*rhs[1:3])
        rhs.add_background_rectangle()

        self.play(
            FadeIn(triangle),
            Write(VGroup(bottom_one, side_one, sqrt_1_plus_1))
        )
        self.wait(2)
        self.play(ReplacementTransform(sqrt_1_plus_1, sqrt_2))
        self.play(
            Write(root_2_value, run_time = 1),
            *list(map(FadeOut, [bottom_one, side_one]))
        )
        self.wait()
        self.play(ShowCreation(corner_radius))
        self.play(Rotating(
            corner_radius, about_point = c0_center,
            run_time = 2,
            rate_func = smooth
        ))
        self.play(FadeOut(triangle), Animation(corner_radius))
        self.wait()
        self.play(
            Write(rhs),
            Transform(sqrt_2, sqrt_2_target),
        )
        self.play(Write(root_2_minus_1_value))
        self.wait(2)

class ThreeDBoxExample(ExternallyAnimatedScene):
    pass

class ThreeDCubeCorners(Scene):
    def construct(self):
        coordinates = VGroup(*[
            TexMobject("(%d,\\, %d,\\, %d)"%(x, y, z))
            for x, y, z in it.product(*3*[[1, -1]])
        ])
        coordinates.arrange(DOWN, aligned_edge = LEFT)
        name = TextMobject("Corners: ")
        name.next_to(coordinates[0], LEFT)
        group = VGroup(name, coordinates)
        group.set_height(FRAME_HEIGHT - 1)
        group.to_edge(LEFT)

        self.play(Write(name, run_time = 2))
        self.play(LaggedStartMap(FadeIn, coordinates, run_time = 3))
        self.wait()

class ShowDistanceFormula(TeacherStudentsScene):
    def construct(self):
        rule = TexMobject(
            "||(", "x_1", ", ", "x_2", "\\dots, ", "x_n", ")||", 
            "=", 
            "\\sqrt", "{x_1^2", " + ", "x_2^2", " +\\cdots", "x_n^2", "}"
        )
        rule.set_color_by_tex_to_color_map({
            "x_1" : GREEN,
            "x_2" : RED,
            "x_n" : BLUE,
        })
        for part in rule.get_parts_by_tex("x_"):
            if len(part) > 2:
                part[1].set_color(WHITE)
        rule.next_to(self.teacher, UP, LARGE_BUFF)
        rule.to_edge(RIGHT)
        rule.shift(UP)

        rule.save_state()
        rule.shift(2*DOWN)
        rule.set_fill(opacity = 0)

        self.play(
            rule.restore,
            self.teacher.change, "raise_right_hand",
        )
        self.wait(3)
        self.student_says("Why?", student_index = 0)
        self.play(self.teacher.change, "thinking")
        self.wait(3)

class GeneralizePythagoreanTheoremBeyondTwoD(ThreeDScene):
    def construct(self):
        tex_to_color_map = {
            "x" : GREEN,
            "y" : RED,
            "z" : BLUE,
        }
        rect = Rectangle(
            height = 4, width = 5,
            fill_color = WHITE,
            fill_opacity = 0.2,
        )
        diag = Line(
            rect.get_corner(DOWN+LEFT),
            rect.get_corner(UP+RIGHT),
            color = YELLOW
        )
        bottom = Line(rect.get_left(), rect.get_right())
        bottom.move_to(rect.get_bottom())
        bottom.set_color(tex_to_color_map["x"])
        side = Line(rect.get_bottom(), rect.get_top())
        side.move_to(rect.get_right())
        side.set_color(tex_to_color_map["y"])

        x = TexMobject("x")
        x.next_to(rect.get_bottom(), UP, SMALL_BUFF)
        y = TexMobject("y")
        y.next_to(rect.get_right(), LEFT, SMALL_BUFF)
        hyp = TexMobject("\\sqrt", "{x", "^2 + ", "y", "^2}")
        hyp.set_color_by_tex_to_color_map(tex_to_color_map)
        hyp.next_to(ORIGIN, UP)
        hyp.rotate(diag.get_angle())
        hyp.shift(diag.get_center())
        group = VGroup(rect, bottom, side, diag, x, y, hyp)

        self.add(rect)
        for line, tex in (bottom, x), (side, y), (diag, hyp):
            self.play(
                ShowCreation(line),
                Write(tex, run_time = 1)
            )
        self.wait()
        self.play(
            group.rotate, 0.45*np.pi, LEFT,
            group.shift, 2*DOWN
        )

        corner = diag.get_end()
        z_line = Line(corner, corner + 3*UP)
        z_line.set_color(tex_to_color_map["z"])
        z = TexMobject("z")
        z.set_color(tex_to_color_map["z"])
        z.next_to(z_line, RIGHT)
        dot = Dot(z_line.get_end())
        three_d_diag = Line(diag.get_start(), z_line.get_end())
        three_d_diag.set_color(MAROON_B)

        self.play(
            ShowCreation(z_line),
            ShowCreation(dot),
            Write(z, run_time = 1)
        )
        self.play(ShowCreation(three_d_diag))
        self.wait()

        full_group = VGroup(group, z_line, z, three_d_diag, dot)
        self.play(Rotating(
            full_group, radians = -np.pi/6,
            axis = UP, 
            run_time = 10,
        ))
        self.wait()

class ThreeDBoxFormulas(Scene):
    def construct(self):
        question = TexMobject(
            "||(1, 1, 1)||", "=", "???"
        )
        answer = TexMobject(
            "||(1, 1, 1)||", "&=", "\\sqrt{1^2 + 1^2 + 1^2}\\\\",
            "&= \\sqrt{3}\\\\", "&\\approx", "1.73",
        )
        for mob in question, answer:
            mob.to_corner(UP+LEFT)
        inner_r = TexMobject(
            "\\text{Inner radius}", "&=", "\\sqrt{3} - 1\\\\",
            "&\\approx", "0.73"
        )
        inner_r.next_to(answer, DOWN, LARGE_BUFF, LEFT)
        inner_r.set_color(GREEN_C)
        VGroup(question, answer).shift(0.55*RIGHT)

        self.play(Write(question))
        self.wait(2)
        self.play(ReplacementTransform(question, answer))
        self.wait(2)
        self.play(Write(inner_r))
        self.wait(2)

class AskAboutHigherDimensions(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "What happens for \\\\ higher dimensions?"
        )
        self.change_student_modes(*["pondering"]*3)
        self.wait(2)
        self.student_thinks(
            "$\\sqrt{N} - 1$",
            target_mode = "happy",
            student_index = 1
        )
        self.wait()
        pi = self.students[1]
        self.play(pi.change, "confused", pi.bubble)
        self.wait(3)

class TenSliders(SliderScene):
    CONFIG = {
        "n_sliders" : 10,
        "run_time": 30,
        "slider_spacing" : 0.75,
        "ambient_acceleration_magnitude" : 2.0,
    }
    def construct(self):
        self.initialize_ambiant_slider_movement()
        self.wait(self.run_time)
        self.wind_down_ambient_movement()

class TwoDBoxWithSliders(TwoDimensionalCase):
    CONFIG = {
        "slider_config" : {
            "include_real_estate_ticks" : True,
            "tick_frequency" : 1,
            "numbers_with_elongated_ticks" : [],
            "tick_size" : 0.1,
            "dial_color" : YELLOW,
            "x_min" : -2,
            "x_max" : 2,
            "unit_size" : 1.5,
        },
        "center_point" : [1, -1],
    }
    def setup(self):
        TwoDimensionalCase.setup(self)
        ##Correct from previous setup
        self.remove(self.equation)
        self.sliders.shift(RIGHT)
        VGroup(*self.get_top_level_mobjects()).shift(RIGHT)
        x_slider = self.sliders[0]
        for number in x_slider.numbers:
            value = int(number.get_tex_string())
            number.next_to(
                x_slider.number_to_point(value), 
                LEFT, MED_SMALL_BUFF
            )
        self.plane.axes.set_color(BLUE)

        ##Add box material
        corner_circles = VGroup(*[
            self.circle.copy().move_to(
                self.plane.coords_to_point(*coords)
            ).set_color(GREY)
            for coords in ((1, 1), (-1, 1), (-1, -1))
        ])
        line = Line(
            self.plane.coords_to_point(-1, -1),
            self.plane.coords_to_point(1, 1),
        )
        box = Square(color = RED)
        box.replace(line, stretch = True)

        self.add(box, corner_circles)
        self.box = box
        self.corner_circles = corner_circles

    def construct(self):
        self.ask_about_off_center_circle()
        self.recenter_circle()
        self.write_x_and_y_real_estate()
        self.swap_with_top_right_circle()
        self.show_center_circle()
        self.describe_tangent_point()
        self.perterb_point()
        self.wander_on_inner_circle()
        self.ask_about_inner_real_estate()

    def ask_about_off_center_circle(self):
        question = TextMobject("Off-center circles?")
        question.next_to(self.plane, UP)

        self.initialize_ambiant_slider_movement()
        self.play(Write(question))
        self.wait(4)
        self.wind_down_ambient_movement()

        self.question = question

    def recenter_circle(self):
        original_center_point = self.center_point

        self.play(
            self.circle.move_to, self.plane.coords_to_point(0, 0),
            Animation(self.sliders),
            *[
                ApplyMethod(
                    mob.shift,
                    slider.number_to_point(0)-slider.number_to_point(slider.center_value)
                )
                for slider in self.sliders
                for mob in [slider.real_estate_ticks, slider.dial]
            ]
        )
        self.center_point = [0, 0]
        for x, slider in zip(self.center_point, self.sliders):
            slider.center_value = x
        self.initialize_ambiant_slider_movement()
        self.wait(7)
        self.wind_down_ambient_movement()
        self.play(
            self.circle.move_to, 
                self.plane.coords_to_point(*original_center_point),
            Animation(self.sliders),
            *[
                ApplyMethod(
                    mob.shift,
                    slider.number_to_point(x)-slider.number_to_point(0)
                )
                for x, slider in zip(original_center_point, self.sliders)
                for mob in [slider.real_estate_ticks, slider.dial]
            ]
        )
        self.center_point = original_center_point
        for x, slider in zip(self.center_point, self.sliders):
            slider.center_value = x

        self.initialize_ambiant_slider_movement()
        self.wait(5)

    def write_x_and_y_real_estate(self):
        phrases = VGroup(
            TextMobject("$x$", "real estate:", "$(x-1)^2$"),
            TextMobject("$y$", "real estate:", "$(y+1)^2$"),
        )
        phrases.next_to(self.plane, UP)
        phrases[0].set_color_by_tex("x", GREEN)
        phrases[1].set_color_by_tex("y", RED)
        x_brace, y_brace = [
            Brace(slider.real_estate_ticks, RIGHT)
            for slider in self.sliders
        ]
        x_brace.set_color(GREEN)
        y_brace.set_color(RED)

        self.play(FadeOut(self.question))
        self.play(
            Write(phrases[0]),
            GrowFromCenter(x_brace)
        )
        self.wait(3)
        self.play(
            Transform(*phrases),
            Transform(x_brace, y_brace)
        )
        self.wait(5)
        self.wind_down_ambient_movement(wait = False)
        self.play(*list(map(FadeOut, [x_brace, phrases[0]])))

    def swap_with_top_right_circle(self):
        alt_circle = self.corner_circles[0]
        slider = self.sliders[1]

        self.play(
            self.circle.move_to, alt_circle,
            alt_circle.move_to, self.circle,
            Animation(slider),
            *[
                ApplyMethod(
                    mob.shift,
                    slider.number_to_point(1) - slider.number_to_point(-1)
                )
                for mob in (slider.real_estate_ticks, slider.dial)
            ]
        )
        slider.center_value = 1
        self.center_point[1] = 1
        self.initialize_ambiant_slider_movement()
        self.wait(3)

    def show_center_circle(self):
        origin = self.plane.coords_to_point(0, 0)
        radius = get_norm(
            self.plane.coords_to_point(np.sqrt(2)-1, 0) - origin
        )
        circle = Circle(radius = radius, color = GREEN)
        circle.move_to(origin)

        self.play(FocusOn(circle))
        self.play(GrowFromCenter(circle, run_time = 2))
        self.wait(3)

    def describe_tangent_point(self):
        target_vector = np.array([
            1-np.sqrt(2)/2, 1-np.sqrt(2)/2
        ])
        point = self.plane.coords_to_point(*target_vector)
        origin = self.plane.coords_to_point(0, 0)
        h_line = Line(point[1]*UP + origin[0]*RIGHT, point)
        v_line = Line(point[0]*RIGHT+origin[1]*UP, point)

        while get_norm(self.get_vector()-target_vector) > 0.5:
            self.wait()
        self.wind_down_ambient_movement(0)
        self.reset_dials(target_vector)
        self.play(*list(map(ShowCreation, [h_line, v_line])))
        self.wait()

        re_line = DashedLine(
            self.sliders[0].dial.get_left() + MED_SMALL_BUFF*LEFT,
            self.sliders[1].dial.get_right() + MED_SMALL_BUFF*RIGHT,
        )
        words = TextMobject("Evenly shared \\\\ real estate")
        words.scale(0.8)
        words.next_to(re_line, RIGHT)
        self.play(ShowCreation(re_line))
        self.play(Write(words))
        self.wait()

        self.evenly_shared_words = words
        self.re_line = re_line

    def perterb_point(self):
        #Perturb dials
        target_vector = np.array([
            1 - np.sqrt(0.7),
            1 - np.sqrt(0.3),
        ])
        ghost_dials = VGroup(*[
            slider.dial.copy()
            for slider in self.sliders
        ])
        ghost_dials.set_fill(WHITE, opacity = 0.75)

        self.add_foreground_mobjects(ghost_dials)
        self.reset_dials(target_vector)
        self.wait()

        #Comment on real estate exchange
        x_words = TextMobject("Gain expensive \\\\", "real estate")
        y_words = TextMobject("Give up cheap \\\\", "real estate")
        VGroup(x_words, y_words).scale(0.8)
        x_words.next_to(self.re_line, UP+LEFT)
        x_words.shift(SMALL_BUFF*(DOWN+LEFT))
        y_words.next_to(self.re_line, UP+RIGHT)
        y_words.shift(MED_LARGE_BUFF*UP)

        x_arrow, y_arrow = [
            Arrow(
                words[1].get_edge_center(vect), self.sliders[i].dial,
                tip_length = 0.15,
            )
            for i, words, vect in zip(
                (0, 1), [x_words, y_words], [RIGHT, LEFT]
            )
        ]

        self.play(
            Write(x_words, run_time = 2),
            ShowCreation(x_arrow)
        )
        self.wait()
        self.play(FadeOut(self.evenly_shared_words))
        self.play(
            Write(y_words, run_time = 2),
            ShowCreation(y_arrow)
        )
        self.wait(2)

        #Swap perspective
        word_starts = VGroup(y_words[0], x_words[0])
        crosses = VGroup()
        new_words = VGroup()
        for w1, w2 in zip(word_starts, reversed(word_starts)):
            crosses.add(Cross(w1))
            w1_copy = w1.copy()
            w1_copy.generate_target()
            w1_copy.target.next_to(w2, UP, SMALL_BUFF)
            new_words.add(w1_copy)

        self.play(*[
            ApplyMethod(
                slider.real_estate_ticks.shift,
                slider.number_to_point(0)-slider.number_to_point(1)
            )
            for slider in self.sliders
        ])
        self.wait()
        self.play(ShowCreation(crosses))
        self.play(
            LaggedStartMap(MoveToTarget, new_words),
            Animation(crosses)
        )
        self.wait(3)

        #Return to original position
        target_vector = np.array(2*[1-np.sqrt(0.5)])
        self.play(LaggedStartMap(FadeOut, VGroup(*[
            ghost_dials, 
            x_words, y_words, 
            x_arrow, y_arrow, 
            crosses, new_words, 
        ])))
        self.remove_foreground_mobjects(ghost_dials)
        self.reset_dials(target_vector)
        self.center_point = np.zeros(2)
        for x, slider in zip(self.center_point, self.sliders):
            slider.center_value = x
        self.set_to_vector(target_vector)
        self.total_real_estate = self.get_current_total_real_estate()
        self.wait(2)

    def wander_on_inner_circle(self):
        self.initialize_ambiant_slider_movement()
        self.wait(9)

    def ask_about_inner_real_estate(self):
        question = TextMobject("What is \\\\ $x^2 + y^2$?")
        question.next_to(self.re_line, RIGHT)

        rhs = TexMobject("<0.5^2 + 0.5^2")
        rhs.scale(0.8)
        rhs.next_to(question, DOWN)
        rhs.to_edge(RIGHT)

        half_line = Line(*[
            slider.number_to_point(0.5) + MED_LARGE_BUFF*vect
            for slider, vect in zip(self.sliders, [LEFT, RIGHT])
        ])
        half = TexMobject("0.5")
        half.scale(self.sliders[0].number_scale_val)
        half.next_to(half_line, LEFT, SMALL_BUFF)

        target_vector = np.array(2*[1-np.sqrt(0.5)])
        while get_norm(target_vector - self.get_vector()) > 0.5:
            self.wait()
        self.wind_down_ambient_movement(0)
        self.reset_dials(target_vector)
        self.play(Write(question))
        self.wait(3)
        self.play(
            ShowCreation(half_line),
            Write(half)
        )
        self.wait()
        self.play(Write(rhs))
        self.wait(3)

class AskWhy(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Wait, why?",
            target_mode = "confused"
        )
        self.wait(3)

class MentionComparisonToZeroPointFive(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Comparing to $0.5$ will \\\\"+\
            "be surprisingly useful!",
            target_mode = "hooray"
        )
        self.change_student_modes(*["happy"]*3)
        self.wait(3)

class ThreeDBoxExampleWithSliders(SliderScene):
    CONFIG = {
        "n_sliders" : 3,
        "slider_config" : {
            "x_min" : -2,
            "x_max" : 2,
            "unit_size" : 1.5,
        },
        "center_point" : np.ones(3),
    }
    def setup(self):
        SliderScene.setup(self)
        self.sliders.shift(2*RIGHT)

    def construct(self):
        self.initialize_ambiant_slider_movement()
        self.name_corner_sphere()
        self.point_out_closest_point()
        self.compare_to_halfway_point()
        self.reframe_as_inner_sphere_point()
        self.place_bound_on_inner_real_estate()
        self.comment_on_inner_sphere_smallness()

    def name_corner_sphere(self):
        sphere_name = TextMobject(
            """Sphere with radius 1\\\\
            centered at (1, 1, 1)"""
        )
        sphere_name.to_corner(UP+LEFT)
        arrow = Arrow(
            sphere_name, VGroup(*self.sliders[0].numbers[-2:]),
            color = BLUE
        )

        self.play(
            LaggedStartMap(FadeIn, sphere_name,),
            ShowCreation(arrow, rate_func = squish_rate_func(smooth, 0.7, 1)),
            run_time = 3
        )
        self.wait(5)

        self.sphere_name = sphere_name
        self.arrow = arrow

    def point_out_closest_point(self):
        target_x = 1-np.sqrt(1./3)
        target_vector = np.array(3*[target_x])
        re_words = TextMobject(
            "$x$, $y$ and $z$ each have \\\\",
            "$\\frac{1}{3}$", "units of real estate"
        )
        re_words.to_corner(UP+LEFT)
        re_line = DashedLine(*[
            self.sliders[i].number_to_point(target_x) + MED_SMALL_BUFF*vect
            for i, vect in [(0, LEFT), (2, RIGHT)]
        ])
        new_arrow = Arrow(
            re_words.get_corner(DOWN+RIGHT), re_line.get_left(),
            color = BLUE
        )

        self.wind_down_ambient_movement()
        self.play(*[
            ApplyMethod(slider.set_value, x)
            for x, slider in zip(target_vector, self.sliders)
        ])
        self.play(ShowCreation(re_line))
        self.play(
            FadeOut(self.sphere_name),
            Transform(self.arrow, new_arrow),
        )
        self.play(LaggedStartMap(FadeIn, re_words))
        self.wait(2)

        self.re_words = re_words
        self.re_line = re_line

    def compare_to_halfway_point(self):
        half_line = Line(*[
            self.sliders[i].number_to_point(0.5)+MED_SMALL_BUFF*vect
            for i, vect in [(0, LEFT), (2, RIGHT)]
        ])
        half_line.set_stroke(MAROON_B, 6)
        half_label = TexMobject("0.5")
        half_label.scale(self.sliders[0].number_scale_val)
        half_label.next_to(half_line, LEFT, MED_SMALL_BUFF)
        half_label.set_color(half_line.get_color())

        curr_vector = self.get_vector()
        target_vector = 0.5*np.ones(3)
        ghost_dials = VGroup(*[
            slider.dial.copy().set_fill(WHITE, 0.5)
            for slider in self.sliders
        ])

        cross = Cross(self.re_words.get_parts_by_tex("frac"))
        new_re = TexMobject("(0.5)^2 = 0.25")
        new_re.next_to(cross, DOWN, MED_SMALL_BUFF, LEFT)
        new_re.set_color(MAROON_B)

        self.play(
            FadeOut(self.arrow),
            Write(half_label, run_time = 1),
            ShowCreation(half_line)
        )
        self.wait()
        self.add(ghost_dials)
        self.play(*[
            ApplyMethod(slider.set_value, 0.5)
            for slider in self.sliders
        ])
        self.play(ShowCreation(cross))
        self.play(Write(new_re))
        self.wait(3)
        self.play(
            FadeOut(new_re),
            FadeOut(cross),
            *[
                ApplyMethod(slider.set_value, x)
                for x, slider in zip(curr_vector, self.sliders)
            ]
        )

    def reframe_as_inner_sphere_point(self):
        s = self.sliders[0]
        shift_vect = s.number_to_point(0)-s.number_to_point(1)
        curr_vector = self.get_vector()
        self.set_center_point(np.zeros(3))
        self.set_to_vector(curr_vector)
        self.total_real_estate = self.get_current_total_real_estate()

        all_re_ticks = VGroup(*[
            slider.real_estate_ticks
            for slider in self.sliders
        ])
        inner_sphere_words = TextMobject(
            "Also a point on \\\\", "the inner sphere"
        )
        inner_sphere_words.next_to(self.re_line, RIGHT)
        question = TextMobject("How much \\\\", "real estate?")
        question.next_to(self.re_line, RIGHT, MED_LARGE_BUFF)

        self.play(
            Animation(self.sliders),
            FadeOut(self.re_words),
            LaggedStartMap(
                ApplyMethod, all_re_ticks,
                lambda m : (m.shift, shift_vect)
            )
        )
        self.initialize_ambiant_slider_movement()
        self.play(Write(inner_sphere_words))
        self.wait(5)
        self.wind_down_ambient_movement(0)
        self.play(*[
            ApplyMethod(slider.set_value, x)
            for slider, x in zip(self.sliders, curr_vector)
        ])
        self.play(ReplacementTransform(
            inner_sphere_words, question
        ))
        self.wait(2)

        self.re_question = question

    def place_bound_on_inner_real_estate(self):
        bound = TexMobject(
            "&< 3(0.5)^2 ",
            "= 0.75"
        )
        bound.next_to(self.re_question, DOWN)
        bound.to_edge(RIGHT)

        self.play(Write(bound))
        self.wait(2)

    def comment_on_inner_sphere_smallness(self):
        self.initialize_ambiant_slider_movement()
        self.wait(15)

class Rotating3DCornerSphere(ExternallyAnimatedScene):
    pass

class FourDBoxExampleWithSliders(ThreeDBoxExampleWithSliders):
    CONFIG = {
        "n_sliders" : 4,
        "center_point" : np.ones(4),
    }
    def construct(self):
        self.list_corner_coordinates()
        self.show_16_corner_spheres()
        self.show_closest_point()
        self.show_real_estate_at_closest_point()
        self.reframe_as_inner_sphere_point()
        self.compute_inner_radius_numerically()
        self.inner_sphere_touches_box()

    def list_corner_coordinates(self):
        title = TextMobject(
            "$2 \\!\\times\\! 2 \\!\\times\\! 2 \\!\\times\\! 2$ box vertices:"
        )
        title.shift(FRAME_X_RADIUS*LEFT/2)
        title.to_edge(UP)

        coordinates = list(it.product(*4*[[1, -1]]))
        coordinate_mobs = VGroup(*[
            TexMobject("(%d, %d, %d, %d)"%tup)
            for tup in coordinates
        ])
        coordinate_mobs.arrange(DOWN, aligned_edge = LEFT)
        coordinate_mobs.scale(0.8)
        left_column = VGroup(*coordinate_mobs[:8])
        right_column = VGroup(*coordinate_mobs[8:])
        right_column.next_to(left_column, RIGHT)
        coordinate_mobs.next_to(title, DOWN)

        self.play(Write(title))
        self.play(LaggedStartMap(FadeIn, coordinate_mobs))
        self.wait()

        self.coordinate_mobs = coordinate_mobs
        self.coordinates = coordinates
        self.box_vertices_title = title

    def show_16_corner_spheres(self):
        sphere_words = VGroup(TextMobject("Sphere centered at"))
        sphere_words.scale(0.8)
        sphere_words.next_to(self.sliders, RIGHT)
        sphere_words.shift(2*UP)

        self.add(sphere_words)
        pairs = list(zip(self.coordinate_mobs, self.coordinates))
        for coord_mob, coords in pairs[1:] + [pairs[0]]:
            coord_mob.set_color(GREEN)
            coord_mob_copy = coord_mob.copy()
            coord_mob_copy.next_to(sphere_words, DOWN)
            for slider, x in zip(self.sliders, coords):
                point = slider.number_to_point(x)
                slider.real_estate_ticks.move_to(point)
                slider.dial.move_to(point)
            self.sliders[0].dial.move_to(
                self.sliders[0].number_to_point(coords[0]+1)
            )
            self.add(coord_mob_copy)
            self.wait()
            self.remove(coord_mob_copy)
            coord_mob.set_color(WHITE)
        self.add(coord_mob_copy)
        sphere_words.add(coord_mob_copy)
        self.sphere_words = sphere_words

        self.play(
            self.sliders.center,
            sphere_words.shift, LEFT,
            *list(map(FadeOut, [
                self.coordinate_mobs, self.box_vertices_title
            ]))
        )
        self.initialize_ambiant_slider_movement()
        self.wait(4)

    def show_closest_point(self):
        target_vector = 0.5*np.ones(4)
        re_line = DashedLine(*[
            self.sliders[i].number_to_point(0.5)+MED_SMALL_BUFF*vect
            for i, vect in [(0, LEFT), (-1, RIGHT)]
        ])
        half_label = TexMobject("0.5")
        half_label.scale(self.sliders[0].number_scale_val)
        half_label.next_to(re_line, LEFT, MED_SMALL_BUFF)
        half_label.set_color(MAROON_B)

        self.wind_down_ambient_movement()
        self.play(*[
            ApplyMethod(slider.set_value, x)
            for x, slider in zip(target_vector, self.sliders)
        ])
        self.play(ShowCreation(re_line))
        self.play(Write(half_label))
        self.wait(2)

        self.re_line = re_line
        self.half_label = half_label

    def show_real_estate_at_closest_point(self):
        words = TextMobject("Total real estate:")
        value = TexMobject("4(0.5)^2 = 4(0.25) = 1")
        value.next_to(words, DOWN)
        re_words = VGroup(words, value)
        re_words.scale(0.8)
        re_words.next_to(self.sphere_words, DOWN, MED_LARGE_BUFF)

        re_rects = VGroup()
        for slider in self.sliders:
            rect = Rectangle(
                width = 2*slider.tick_size,
                height = 0.5*slider.unit_size,
                stroke_width = 0,
                fill_color = MAROON_B,
                fill_opacity = 0.75,
            )
            rect.move_to(slider.number_to_point(0.75))
            re_rects.add(rect)

        self.play(FadeIn(re_words))
        self.play(LaggedStartMap(DrawBorderThenFill, re_rects, run_time = 3))
        self.wait(2)

        self.re_words = re_words
        self.re_rects = re_rects

    def reframe_as_inner_sphere_point(self):
        sphere_words = self.sphere_words
        sphere_words.generate_target()
        sphere_words.target.shift(2*DOWN)
        old_coords = sphere_words.target[1]
        new_coords = TexMobject("(0, 0, 0, 0)")
        new_coords.replace(old_coords, dim_to_match = 1)
        new_coords.set_color(old_coords.get_color())
        Transform(old_coords, new_coords).update(1)

        self.play(Animation(self.sliders), *[
            ApplyMethod(
                s.real_estate_ticks.move_to, s.number_to_point(0),
                run_time = 2,
                rate_func = squish_rate_func(smooth, a, a+0.5)
            )
            for s, a in zip(self.sliders, np.linspace(0, 0.5, 4))
        ])
        self.play(
            MoveToTarget(sphere_words),
            self.re_words.next_to, sphere_words.target, UP, MED_LARGE_BUFF,
            path_arc = np.pi
        )
        self.wait(2)
        re_shift_vect = 0.5*self.sliders[0].unit_size*DOWN
        self.play(LaggedStartMap(
            ApplyMethod, self.re_rects,
            lambda m : (m.shift, re_shift_vect),
            path_arc = np.pi
        ))
        self.wait()
        re_words_rect = SurroundingRectangle(self.re_words)
        self.play(ShowCreation(re_words_rect))
        self.wait()
        self.play(FadeOut(re_words_rect))
        self.wait()

        self.set_center_point(np.zeros(4))
        self.initialize_ambiant_slider_movement()
        self.wait(4)

    def compute_inner_radius_numerically(self):
        computation = TexMobject(
            "R_\\text{Inner}", 
            "&= ||(1, 1, 1, 1)|| - 1 \\\\",
            # "&= \\sqrt{1^2 + 1^2 + 1^2 + 1^2} - 1 \\\\",
            "&= \\sqrt{4} - 1 \\\\",
            "&= 1"
        )
        computation.scale(0.8)
        computation.to_corner(UP+LEFT)
        computation.shift(DOWN)
        brace = Brace(VGroup(*computation[1][1:-2]), UP)
        brace_text = brace.get_text("Distance to corner")
        brace_text.scale(0.8, about_point = brace_text.get_bottom())
        VGroup(brace, brace_text).set_color(RED)

        self.play(LaggedStartMap(FadeIn, computation, run_time = 3))
        self.play(GrowFromCenter(brace))
        self.play(Write(brace_text, run_time = 2))
        self.wait(16)

        computation.add(brace, brace_text)
        self.computation = computation

    def inner_sphere_touches_box(self):
        touching_words = TextMobject(
            "This point touches\\\\",
            "the $2 \\!\\times\\! 2 \\!\\times\\! 2 \\!\\times\\! 2$ box!"
        )
        touching_words.to_corner(UP+LEFT)
        arrow = Arrow(MED_SMALL_BUFF*DOWN, 3*RIGHT+DOWN)
        arrow.set_color(BLUE)
        arrow.shift(touching_words.get_bottom())

        self.wind_down_ambient_movement(wait = False)
        self.play(FadeOut(self.computation))
        self.reset_dials([1])
        self.play(Write(touching_words))
        self.play(ShowCreation(arrow))
        self.wait(2)

class TwoDInnerSphereTouchingBox(TwoDBoxWithSliders, PiCreatureScene):
    def setup(self):
        TwoDBoxWithSliders.setup(self)
        PiCreatureScene.setup(self)
        self.remove(self.sliders)
        self.remove(self.dot)
        self.circle.set_color(GREY)
        self.randy.next_to(self.plane, RIGHT, LARGE_BUFF, DOWN)

    def construct(self):
        little_inner_circle, big_inner_circle = [
            Circle(
                radius = radius*self.plane.x_unit_size,
                color = GREEN
            ).move_to(self.plane.coords_to_point(0, 0))
            for radius in (np.sqrt(2)-1, 1)
        ]
        randy = self.randy
        tangency_points = VGroup(*[
            Dot(self.plane.coords_to_point(x, y))
            for x, y in [(1, 0), (0, 1), (-1, 0), (0, -1)]
        ])
        tangency_points.set_fill(YELLOW, 0.5)

        self.play(
            ShowCreation(little_inner_circle),
            randy.change, "pondering", little_inner_circle
        )
        self.wait()
        self.play(
            ReplacementTransform(
                little_inner_circle.copy(), big_inner_circle
            ),
            little_inner_circle.fade,
            randy.change, "confused"
        )
        big_inner_circle.save_state()
        self.play(big_inner_circle.move_to, self.circle)
        self.play(big_inner_circle.restore)
        self.wait()
        self.play(LaggedStartMap(
            DrawBorderThenFill, tangency_points,
            rate_func = double_smooth
        ))
        self.play(randy.change, "maybe")
        self.play(randy.look_at, self.circle)
        self.wait()
        self.play(randy.look_at, little_inner_circle)
        self.wait()

    ####

    def create_pi_creature(self):
        self.randy = Randolph().flip()
        return self.randy

class FiveDBoxExampleWithSliders(FourDBoxExampleWithSliders):
    CONFIG = {
        "n_sliders" : 5,
        "center_point" : np.ones(5),
    }
    def setup(self):
        FourDBoxExampleWithSliders.setup(self)
        self.sliders.center()

    def construct(self):
        self.show_32_corner_spheres()
        self.show_closest_point()
        self.show_halfway_point()
        self.reframe_as_inner_sphere_point()
        self.compute_radius()
        self.poke_out_of_box()

    def show_32_corner_spheres(self):
        sphere_words = VGroup(TextMobject("Sphere centered at"))
        sphere_words.next_to(self.sliders, RIGHT, MED_LARGE_BUFF)
        sphere_words.shift(2.5*UP)
        self.add(sphere_words)

        n_sphere_words = TextMobject("32 corner spheres")
        n_sphere_words.to_edge(LEFT)
        n_sphere_words.shift(2*UP)
        self.add(n_sphere_words)

        for coords in it.product(*5*[[-1, 1]]):
            s = str(tuple(coords))
            s = s.replace("1", "+1")
            s = s.replace("-+1", "-1")
            coords_mob = TexMobject(s)
            coords_mob.set_color(GREEN)
            coords_mob.next_to(sphere_words, DOWN)
            for slider, x in zip(self.sliders, coords):
                for mob in slider.real_estate_ticks, slider.dial:
                    mob.move_to(slider.number_to_point(x))
            self.sliders[0].dial.move_to(
                self.sliders[0].number_to_point(coords[0]+1)
            )
            self.add(coords_mob)
            self.wait(0.25)
            self.remove(coords_mob)
        self.add(coords_mob)
        sphere_words.add(coords_mob)
        self.sphere_words = sphere_words

        self.initialize_ambiant_slider_movement()
        self.play(FadeOut(n_sphere_words))
        self.wait(3)

    def show_closest_point(self):
        target_x = 1-np.sqrt(0.2)
        re_line = DashedLine(*[
            self.sliders[i].number_to_point(target_x)+MED_SMALL_BUFF*vect
            for i, vect in [(0, LEFT), (-1, RIGHT)]
        ])
        re_words = TextMobject(
            "$0.2$", "units of real \\\\ estate each"
        )
        re_words.next_to(self.sphere_words, DOWN, MED_LARGE_BUFF)

        re_rects = VGroup()
        for slider in self.sliders:
            rect = Rectangle(
                width = 2*slider.tick_size,
                height = (1-target_x)*slider.unit_size,
                stroke_width = 0,
                fill_color = GREEN,
                fill_opacity = 0.75,
            )
            rect.move_to(slider.number_to_point(1), UP)
            re_rects.add(rect)
        
        self.wind_down_ambient_movement()
        self.reset_dials(5*[target_x])
        self.play(
            ShowCreation(re_line),
            Write(re_words, run_time = 2)
        )
        self.play(LaggedStartMap(
            DrawBorderThenFill, re_rects,
            rate_func = double_smooth
        ))
        self.wait()

        self.re_rects = re_rects
        self.re_words = re_words
        self.re_line = re_line

    def show_halfway_point(self):
        half_line = Line(*[
            self.sliders[i].number_to_point(0.5)+MED_SMALL_BUFF*vect
            for i, vect in [(0, LEFT), (-1, RIGHT)]
        ])
        half_line.set_color(MAROON_B)
        half_label = TexMobject("0.5")
        half_label.scale(self.sliders[0].number_scale_val)
        half_label.next_to(half_line, LEFT, MED_SMALL_BUFF)
        half_label.set_color(half_line.get_color())

        curr_vector = self.get_vector()
        ghost_dials = VGroup(*[
            slider.dial.copy().set_fill(WHITE, 0.75)
            for slider in self.sliders
        ])
        point_25 = TexMobject("0.25")
        point_25.set_color(half_label.get_color())
        point_25.move_to(self.re_words[0], RIGHT)
        self.re_words.save_state()

        self.play(
            Write(half_label),
            ShowCreation(half_line)
        )
        self.wait(2)
        self.add(ghost_dials)
        self.play(*[
            ApplyMethod(slider.set_value, 0.5)
            for slider in self.sliders
        ])
        self.play(Transform(self.re_words[0], point_25))
        self.wait(2)
        self.play(*[
            ApplyMethod(slider.set_value, x)
            for x, slider in zip(curr_vector, self.sliders)
        ])
        self.play(self.re_words.restore)

    def reframe_as_inner_sphere_point(self):
        s = self.sliders[0]
        shift_vect = s.number_to_point(0)-s.number_to_point(1)
        re_ticks = VGroup(*[
            slider.real_estate_ticks
            for slider in self.sliders
        ])

        re_rects = self.re_rects
        re_rects.generate_target()
        for rect, slider in zip(re_rects.target, self.sliders):
            height = slider.unit_size*(1-np.sqrt(0.2))
            rect.set_height(height)
            rect.move_to(slider.number_to_point(0), DOWN)

        self.sphere_words.generate_target()
        old_coords = self.sphere_words.target[1]
        new_coords = TexMobject(str(tuple(5*[0])))
        new_coords.replace(old_coords, dim_to_match = 1)
        new_coords.set_color(old_coords.get_color())
        Transform(old_coords, new_coords).update(1)

        self.re_words.generate_target()
        new_re = TexMobject("0.31")
        new_re.set_color(GREEN)
        old_re = self.re_words.target[0]
        new_re.move_to(old_re, RIGHT)
        Transform(old_re, new_re).update(1)

        self.play(
            Animation(self.sliders),
            LaggedStartMap(
                ApplyMethod, re_ticks,
                lambda m : (m.shift, shift_vect),
                path_arc = np.pi
            ),
            MoveToTarget(self.sphere_words),
        )
        self.play(
            MoveToTarget(
                re_rects, 
                run_time = 2,
                lag_ratio = 0.5,
                path_arc = np.pi
            ),
            MoveToTarget(self.re_words),
        )
        self.wait(2)

        self.set_center_point(np.zeros(5))
        self.total_real_estate = (np.sqrt(5)-1)**2
        self.initialize_ambiant_slider_movement()
        self.wait(12)

    def compute_radius(self):
        computation = TexMobject(
            "R_{\\text{inner}} &= \\sqrt{5}-1 \\\\",
            "&\\approx 1.24"
        )
        computation.to_corner(UP+LEFT)

        self.play(Write(computation, run_time = 2))
        self.wait(12)

    def poke_out_of_box(self):
        self.wind_down_ambient_movement(0)
        self.reset_dials([np.sqrt(5)-1])

        words = TextMobject("Poking outside \\\\ the box!")
        words.to_edge(LEFT)
        words.set_color(RED)
        arrow = Arrow(
            words.get_top(),
            self.sliders[0].dial,
            path_arc = -np.pi/3,
            color = words.get_color()
        )

        self.play(
            ShowCreation(arrow),
            Write(words)
        )
        self.wait(2)

class SkipAheadTo10(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Let's skip ahead \\\\ to 10 dimensions",
            target_mode = "hooray"
        )
        self.change_student_modes(
            "pleading", "confused", "horrified"
        )
        self.wait(3)

class TenDBoxExampleWithSliders(FiveDBoxExampleWithSliders):
    CONFIG = {
        "n_sliders" : 10,
        "center_point" : np.ones(10),
        "ambient_velocity_magnitude" : 2.0,
        "ambient_acceleration_magnitude" : 3.0,
    }
    def setup(self):
        FourDBoxExampleWithSliders.setup(self)
        self.sliders.to_edge(RIGHT)

    def construct(self):
        self.initial_wandering()
        self.show_closest_point()
        self.reframe_as_inner_sphere_point()
        self.compute_inner_radius_numerically()
        self.wander_on_inner_sphere()
        self.poke_outside_outer_box()

    def initial_wandering(self):
        self.initialize_ambiant_slider_movement()
        self.wait(9)

    def show_closest_point(self):
        target_x = 1-np.sqrt(1./self.n_sliders)
        re_line = DashedLine(*[
            self.sliders[i].number_to_point(target_x)+MED_SMALL_BUFF*vect
            for i, vect in [(0, LEFT), (-1, RIGHT)]
        ])

        re_rects = VGroup()
        for slider in self.sliders:
            rect = Rectangle(
                width = 2*slider.tick_size,
                height = (1-target_x)*slider.unit_size,
                stroke_width = 0,
                fill_color = GREEN,
                fill_opacity = 0.75,
            )
            rect.move_to(slider.number_to_point(1), UP)
            re_rects.add(rect)
        
        self.wind_down_ambient_movement()
        self.reset_dials(self.n_sliders*[target_x])
        self.play(ShowCreation(re_line))
        self.play(LaggedStartMap(
            DrawBorderThenFill, re_rects,
            rate_func = double_smooth
        ))
        self.wait(2)

        self.re_line = re_line
        self.re_rects = re_rects

    def reframe_as_inner_sphere_point(self):
        s = self.sliders[0]
        shift_vect = s.number_to_point(0)-s.number_to_point(1)
        re_ticks = VGroup(*[
            slider.real_estate_ticks
            for slider in self.sliders
        ])

        re_rects = self.re_rects
        re_rects.generate_target()
        for rect, slider in zip(re_rects.target, self.sliders):
            height = slider.unit_size*(1-np.sqrt(1./self.n_sliders))
            rect.stretch_to_fit_height(height)
            rect.move_to(slider.number_to_point(0), DOWN)

        self.play(
            Animation(self.sliders),
            LaggedStartMap(
                ApplyMethod, re_ticks,
                lambda m : (m.shift, shift_vect),
                path_arc = np.pi
            ),
        )
        self.play(
            MoveToTarget(
                re_rects, 
                run_time = 2,
                lag_ratio = 0.5,
                path_arc = np.pi
            ),
        )
        self.wait(2)

        self.set_center_point(np.zeros(self.n_sliders))
        self.total_real_estate = (np.sqrt(self.n_sliders)-1)**2
        self.initialize_ambiant_slider_movement()
        self.wait(5)

    def compute_inner_radius_numerically(self):
        computation = TexMobject(
            "R_{\\text{inner}} &= \\sqrt{10}-1 \\\\",
            "&\\approx 2.16"
        )
        computation.to_corner(UP+LEFT)

        self.play(Write(computation, run_time = 2))

    def wander_on_inner_sphere(self):
        self.wait(10)

    def poke_outside_outer_box(self):
        self.wind_down_ambient_movement()
        self.reset_dials([np.sqrt(10)-1])

        words = TextMobject(
            "Outside the \\emph{outer} \\\\",
            "bounding box!"
        )
        words.to_edge(LEFT)
        words.set_color(RED)
        arrow = Arrow(
            words.get_top(), 
            self.sliders[0].dial,
            path_arc = -np.pi/3,
            color = words.get_color()
        )
        self.play(
            Write(words, run_time = 2),
            ShowCreation(arrow)
        )
        self.wait(3)

class TwoDOuterBox(TwoDInnerSphereTouchingBox):
    def construct(self):
        words = TextMobject("$4 \\!\\times\\! 4$ outer bounding box")
        words.next_to(self.plane, UP)
        words.set_color(MAROON_B)
        line = Line(
            self.plane.coords_to_point(-2, -2),
            self.plane.coords_to_point(2, 2),
        )
        box = Square(color = words.get_color())
        box.replace(line, stretch = True)
        box.set_stroke(width = 8)

        self.play(
            Write(words),
            ShowCreation(box),
            self.randy.change, "pondering",
        )
        self.wait(3)

        self.outer_box = box

class ThreeDOuterBoundingBox(ExternallyAnimatedScene):
    pass

class ThreeDOuterBoundingBoxWords(Scene):
    def construct(self):
        words = TextMobject(
            "$4 \\!\\times\\! 4\\!\\times\\! 4$ outer\\\\",
            "bounding box"
        )
        words.set_width(FRAME_WIDTH-1)
        words.to_edge(DOWN)
        words.set_color(MAROON_B)

        self.play(Write(words))
        self.wait(4)

class FaceDistanceDoesntDependOnDimension(TwoDOuterBox):
    def construct(self):
        self.force_skipping()
        TwoDOuterBox.construct(self)
        self.randy.change("confused")
        self.revert_to_original_skipping_status()

        line = Line(
            self.plane.coords_to_point(0, 0),
            self.outer_box.get_right(),
            buff = 0,
            stroke_width = 6,
            color = YELLOW
        )
        length_words = TextMobject("Always 2, in all dimensions")
        length_words.next_to(self.plane, RIGHT, MED_LARGE_BUFF, UP)
        arrow = Arrow(length_words[4].get_bottom(), line.get_center())

        self.play(ShowCreation(line))
        self.play(
            Write(length_words),
            ShowCreation(arrow)
        )
        self.play(self.randy.change, "thinking")
        self.wait(3)

class TenDCornerIsVeryFarAway(TenDBoxExampleWithSliders):
    CONFIG = {
        "center_point" : np.zeros(10)
    }
    def construct(self):
        self.show_re_rects()

    def show_re_rects(self):
        re_rects = VGroup()
        for slider in self.sliders:
            rect = Rectangle(
                width = 2*slider.tick_size,
                height = slider.unit_size,
                stroke_width = 0,
                fill_color = GREEN,
                fill_opacity = 0.75,
            )
            rect.move_to(slider.number_to_point(0), DOWN)
            re_rects.add(rect)
            rect.save_state()
            rect.stretch_to_fit_height(0)
            rect.move_to(rect.saved_state, DOWN)

        self.set_to_vector(np.zeros(10))
        self.play(
            LaggedStartMap(
                ApplyMethod, re_rects,
                lambda m : (m.restore,),
                lag_ratio = 0.3,
            ),
            LaggedStartMap(
                ApplyMethod, self.sliders,
                lambda m : (m.set_value, 1),
                lag_ratio = 0.3,
            ),
            run_time = 10,
        )
        self.wait()

class InnerRadiusIsUnbounded(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("Inner radius \\\\ is unbounded")
        self.change_student_modes(*["erm"]*3)
        self.wait(3)

class ProportionOfSphereInBox(GraphScene):
    CONFIG = {
        "x_axis_label" : "Dimension",
        "y_axis_label" : "",
        "y_max" : 1.5,
        "y_min" : 0,
        "y_tick_frequency" : 0.25,
        "y_labeled_nums" : np.linspace(0.25, 1, 4),
        "x_min" : 0,
        "x_max" : 50,
        "x_tick_frequency" : 5,
        "x_labeled_nums" : list(range(10, 50, 10)),
        "num_graph_anchor_points" : 100,
    }
    def construct(self):
        self.setup_axes()
        title = TextMobject(
            "Proportion of inner sphere \\\\ inside box"
        )
        title.next_to(self.y_axis, RIGHT, MED_SMALL_BUFF, UP)
        self.add(title)

        graph = self.get_graph(lambda x : np.exp(0.1*(9-x)))
        max_y = self.coords_to_point(0, 1)[1]
        too_high = graph.points[:,1] > max_y
        graph.points[too_high, 1] = max_y

        footnote = TextMobject("""
            \\begin{flushleft}
            *I may or may not have used an easy-to-compute \\\\
            but not-totally-accurate curve here, due to \\\\
            the surprising difficulty in computing the real \\\\
            proportion :)
            \\end{flushleft}
        """,)
        footnote.scale(0.75)
        footnote.next_to(
            graph.point_from_proportion(0.3),
            UP+RIGHT, SMALL_BUFF
        )
        footnote.set_color(YELLOW)

        self.play(ShowCreation(graph, run_time = 5, rate_func=linear))
        self.wait()
        self.add(footnote)
        self.wait(0.25)

class ShowingToFriend(PiCreatureScene, SliderScene):
    CONFIG = {
        "n_sliders" : 10,
        "ambient_acceleration_magnitude" : 3.0,
        "seconds_to_blink" : 4,
    }
    def setup(self):
        PiCreatureScene.setup(self)
        SliderScene.setup(self)
        self.sliders.scale(0.75)
        self.sliders.next_to(
            self.morty.get_corner(UP+LEFT), UP, MED_LARGE_BUFF
        )
        self.initialize_ambiant_slider_movement()

    def construct(self):
        morty, randy = self.morty, self.randy
        self.play(morty.change, "raise_right_hand", self.sliders)
        self.play(randy.change, "happy", self.sliders)
        self.wait(7)
        self.play(randy.change, "skeptical", morty.eyes)
        self.wait(3)
        self.play(randy.change, "thinking", self.sliders)
        self.wait(6)

    ###

    def create_pi_creatures(self):
        self.morty = Mortimer()
        self.morty.to_edge(DOWN).shift(4*RIGHT)
        self.randy = Randolph()
        self.randy.to_edge(DOWN).shift(4*LEFT)
        return VGroup(self.morty, self.randy)

    def non_blink_wait(self, time = 1):
        SliderScene.wait(self, time)

class QuestionsFromStudents(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Is 10-dimensional \\\\ space real?",
            target_mode = "sassy",
            run_time = 2,
        )
        self.wait()
        self.teacher_says(
            "No less real \\\\ than reals",
            target_mode = "shruggie",
            content_introduction_class = FadeIn,
        )
        self.wait(2)
        self.student_says(
            "How do you think \\\\ about volume?",
            student_index = 0,
            content_introduction_class = FadeIn,
        )
        self.wait()
        self.student_says(
            "How do cubes work?",
            student_index = 2,
            run_time = 2,
        )
        self.wait(2)

class FunHighDSpherePhenomena(Scene):
    def construct(self):
        title = TextMobject(
            "Fun high-D sphere phenomena"
        )
        title.to_edge(UP)
        title.set_color(BLUE)
        h_line = Line(LEFT, RIGHT).scale(5)
        h_line.next_to(title, DOWN)
        self.add(title, h_line)

        items = VGroup(*list(map(TextMobject, [
            "$\\cdot$ Most volume is near the equator",
            "$\\cdot$ Most volume is near the surface",
            "$\\cdot$ Sphere packing in 8 dimensions",
            "$\\cdot$ Sphere packing in 24 dimensions",
        ])))
        items.arrange(
            DOWN, buff = MED_LARGE_BUFF, aligned_edge = LEFT
        )
        items.next_to(h_line, DOWN)

        for item in items:
            self.play(LaggedStartMap(FadeIn, item, run_time = 2))
        self.wait()

class TODOBugOnSurface(TODOStub):
    CONFIG = {
        "message" : "Bug on surface"
    }

class CoordinateFree(PiCreatureScene):
    def construct(self):
        plane = NumberPlane(x_radius = 2.5, y_radius = 2.5)
        plane.add_coordinates()
        plane.to_corner(UP+LEFT)
        self.add(plane)

        circles = VGroup(*[
            Circle(color = YELLOW).move_to(
                plane.coords_to_point(*coords)
            )
            for coords in it.product(*2*[[-1, 1]])
        ])
        inner_circle = Circle(
            radius = np.sqrt(2)-1,
            color = GREEN
        ).move_to(plane.coords_to_point(0, 0))

        self.add_foreground_mobjects(circles, inner_circle)

        self.play(PiCreatureSays(
            self.pi_creature, "Lose the \\\\ coordinates!",
            target_mode = "hooray"
        ))
        self.play(FadeOut(plane, run_time = 2))
        self.wait(3)

class Skeptic(TeacherStudentsScene, SliderScene):
    def setup(self):
        SliderScene.setup(self)
        TeacherStudentsScene.setup(self)

        self.sliders.scale(0.7)
        self.sliders.next_to(self.teacher, UP, aligned_edge = LEFT)
        self.sliders.to_edge(UP)
        self.initialize_ambiant_slider_movement()

    def construct(self):
        analytic_thought = VGroup(TextMobject("No different from"))
        equation = TexMobject(
            "x", "^2 + ", "y", "^2 + ", "z", "^2 + ", "w", "^2 = 1"
        )
        variables = VGroup(*[
            equation.get_part_by_tex(tex)
            for tex in "xyzw"
        ])
        slider_labels = VGroup(*[
            slider.label for slider in self.sliders
        ])
        equation.next_to(analytic_thought, DOWN)
        analytic_thought.add(equation)

        all_real_estate_ticks = VGroup(*it.chain(*[
            slider.real_estate_ticks
            for slider in self.sliders
        ]))

        box = Square(color = RED)
        box.next_to(self.sliders, LEFT)
        line = Line(box.get_center(), box.get_corner(UP+RIGHT))
        line.set_color(YELLOW)

        self.student_says(
            analytic_thought,
            student_index = 0,
            target_mode = "sassy",
            added_anims = [self.teacher.change, "guilty"]
        )
        self.wait(2)
        equation.remove(*variables)
        self.play(ReplacementTransform(variables, slider_labels))
        self.play(
            self.teacher.change, "pondering", slider_labels,
            RemovePiCreatureBubble(
                self.students[0], target_mode = "hesitant"
            ),
        )
        self.wait(4)
        bubble = self.teacher.get_bubble(
            "It's much \\\\ more playful!",
            bubble_class = SpeechBubble
        )
        bubble.resize_to_content()
        VGroup(bubble, bubble.content).next_to(self.teacher, UP+LEFT)
        self.play(
            self.teacher.change, "hooray",
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.wait(3)
        self.play(
            RemovePiCreatureBubble(
                self.teacher, target_mode = "raise_right_hand",
                look_at_arg = self.sliders
            ),
            *[
                ApplyMethod(pi.change, "pondering")
                for pi in self.students
            ]
        )
        self.play(Animation(self.sliders), LaggedStartMap(
            ApplyMethod, all_real_estate_ticks,
            lambda m : (m.shift, SMALL_BUFF*LEFT),
            rate_func = wiggle,
            lag_ratio = 0.3,
            run_time = 4,
        ))
        self.play(
            ShowCreation(box),
            self.teacher.change, "happy"
        )
        self.play(ShowCreation(line))
        self.wait(3)

    #####
    def non_blink_wait(self, time = 1):
        SliderScene.wait(self, time)

class ClipFrom4DBoxExampleTODO(TODOStub):
    CONFIG = {
        "message" : "Clip from 4d box example"
    }

class JustBecauseYouCantVisualize(Scene):
    def construct(self):
        phrase = "\\raggedright "
        phrase += "Just because you can't visualize\\\\ "
        phrase += "something   doesn't mean you can't\\\\ "
        phrase += "still think about it visually."
        phrase_mob = TextMobject(*phrase.split(" "))
        phrase_mob.set_color_by_tex("visual", YELLOW)
        phrase_mob.next_to(ORIGIN, UP)

        for part in phrase_mob:
            self.play(LaggedStartMap(
                FadeIn, part,
                run_time = 0.05*len(part)
            ))
        self.wait(2)

class Announcements(TeacherStudentsScene):
    def construct(self):
        title = TextMobject("Announcements")
        title.scale(1.5)
        title.to_edge(UP, buff = MED_SMALL_BUFF)
        h_line = Line(LEFT, RIGHT).scale(3)
        h_line.next_to(title, DOWN)
        self.add(title, h_line)

        items = VGroup(*list(map(TextMobject, [
            "$\\cdot$ Where to learn more",
            "$\\cdot$ Q\\&A Followup (podcast!)",
        ])))
        items.arrange(DOWN, aligned_edge = LEFT)
        items.next_to(h_line, DOWN)

        self.play(
            Write(items[0], run_time = 2),
        )
        self.play(*[
            ApplyMethod(pi.change, "hooray", items)
            for pi in self.pi_creatures
        ])
        self.play(Write(items[1], run_time = 2))
        self.wait(2)

class Promotion(PiCreatureScene):
    CONFIG = {
        "seconds_to_blink" : 5,
    }
    def construct(self):
        url = TextMobject("https://brilliant.org/3b1b/")
        url.to_corner(UP+LEFT)

        rect = Rectangle(height = 9, width = 16)
        rect.set_height(5.5)
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

        self.remove(rect)
        self.play(
            url.next_to, self.pi_creature, UP+LEFT
        )
        url_rect = SurroundingRectangle(url)
        self.play(ShowCreation(url_rect))
        self.play(FadeOut(url_rect))
        self.wait(3)

class BrilliantGeometryQuiz(ExternallyAnimatedScene):
    pass

class BrilliantScrollThroughCourses(ExternallyAnimatedScene):
    pass

class Podcast(TeacherStudentsScene):
    def construct(self):
        title = TextMobject("Podcast!")
        title.scale(1.5)
        title.to_edge(UP)
        title.shift(FRAME_X_RADIUS*LEFT/2)
        self.add(title)

        q_and_a = TextMobject("Q\\&A Followup")
        q_and_a.next_to(self.teacher.get_corner(UP+LEFT), UP, LARGE_BUFF)

        self.play(
            LaggedStartMap(
                ApplyMethod, self.pi_creatures,
                lambda pi : (pi.change, "hooray", title)
            ), 
            Write(title)
        )
        self.wait(5)
        self.play(
            Write(q_and_a),
            self.teacher.change, "raise_right_hand",
        )
        self.wait(4)

class HighDPatreonThanks(PatreonThanks):
    CONFIG = {
        "specific_patrons" : [
            "Desmos",
            "Burt Humburg",
            "CrypticSwarm",
            "Juan Benet",
            "Ali Yahya",
            "William",
            "Mayank M. Mehrotra",
            "Lukas Biewald",
            "Samantha D. Suplee",
            "James Park",
            "Yana Chernobilsky",
            "Kaustuv DeBiswas",
            "Kathryn Schmiedicke",
            "Yu Jun",
            "dave nicponski",
            "Damion Kistler",
            "Markus Persson",
            "Yoni Nazarathy",
            "Corey Ogburn",
            "Ed Kellett",
            "Joseph John Cox",
            "Dan Buchoff",
            "Luc Ritchie",
            "Erik Sundell",
            "Xueqi Li",
            "David Stork",
            "Tianyu Ge",
            "Ted Suzman",
            "Amir Fayazi",
            "Linh Tran",
            "Andrew Busey",
            "Michael McGuffin",
            "John Haley",
            "Ankalagon",
            "Eric Lavault",
            "Tomohiro Furusawa",
            "Boris Veselinovich",
            "Julian Pulgarin",
            "Jeff Linse",
            "Cooper Jones",
            "Ryan Dahl",
            "Mark Govea",
            "Robert Teed",
            "Jason Hise",
            "Meshal Alshammari",
            "Bernd Sing",
            "Nils Schneider",
            "James Thornton",
            "Mustafa Mahdi",
            "Mathew Bramson",
            "Jerry Ling",
            "Vecht",
            "Shimin Kuang",
            "Rish Kundalia",
            "Achille Brighton",
            "Ripta Pasay",
        ]
    }

class Thumbnail(SliderScene):
    CONFIG = {
        "n_sliders" : 10,
    }
    def construct(self):
        for slider in self.sliders:
            self.remove(slider.label)
            slider.remove(slider.label)
        vect = np.random.random(10) - 0.5
        vect /= get_norm(vect)
        self.set_to_vector(vect)

        title = TextMobject("10D Sphere?")
        title.scale(2)
        title.to_edge(UP)
        self.add(title)





















