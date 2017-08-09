from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from topics.objects import *
from topics.probability import *
from topics.complex_numbers import *
from topics.common_scenes import *
from scene.scene import Scene, ProgressDisplay
from scene.reconfigurable_scene import ReconfigurableScene
from scene.zoomed_scene import *
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

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
        label.move_to(self.main_line.get_top())
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
        self.real_estate_ticks.gradient_highlight(*colors)
        self.add(self.real_estate_ticks)
        self.add(self.dial)
        return self.real_estate_ticks

    def set_value(self, x):
        re = (x - self.center_value)**2
        for dial, val in (self.dial, x), (self.re_dial, re):
            dial.move_to(self.number_to_point(val))
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
        sliders.arrange_submobjects(RIGHT, buff = self.slider_spacing)
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
        else:
            for i, slider in enumerate(self.sliders):
                slider.add_label("x_{%d}"%(i+1))
        return self

    def reset_dials(self, values, run_time = 1, **kwargs):
        target_vector = self.get_target_vect_from_subset_of_values(values, **kwargs)
        self.play(*[
            ApplyMethod(slider.set_value, value)
            for value, slider in zip(target_vector, self.sliders)
        ] + [
            slider.get_dial_supplement_animation()
            for slider in self.sliders
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
        used_re = np.linalg.norm(target_vector - self.center_point)**2
        left_over_re = self.total_real_estate - used_re
        if left_over_re < 0:
            raise Exception("Overspecified reset")
        uv_norm = np.linalg.norm(unspecified_vector - self.center_point)
        if uv_norm == 0 and left_over_re > 0:
            unspecified_vector[unspecified_indices] = 1
            uv_norm = np.linalg.norm(unspecified_vector - self.center_point)
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

    def wind_down_ambient_movement(self, time = 1, dither = True):
        self.ambient_change_end_time = self.ambient_change_time + time
        if dither:
            self.dither(time)
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
        if np.linalg.norm(target_vector) == 0:
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
                unit_r_vect = target_vector / np.linalg.norm(target_vector)
                vect -= np.dot(vect, unit_r_vect)*unit_r_vect
            vect *= mag/np.linalg.norm(vect)
            deriv = vect

        self.set_to_vector(target_vector + center_point)
        self.ambient_change_time += self.frame_duration

    def get_random_vector(self, magnitude):
        result = 2*np.random.random(len(self.sliders)) - 1
        result *= magnitude / np.linalg.norm(result)
        return result

    def update_frame(self, *args, **kwargs):
        if self.ambiently_change_sliders:
            self.ambient_slider_movement_update()
        Scene.update_frame(self, *args, **kwargs)

    def dither(self, time = 1):
        if self.ambiently_change_sliders:
            self.play(Animation(self.sliders, run_time = time))
        else:
            Scene.dither(self,time)

##########

class MathIsATease(Scene):
    def construct(self):
        randy = Randolph()
        lashes = VGroup()
        for eye in randy.eyes:
            for angle in np.linspace(-np.pi/3, np.pi/3, 12):
                lash = Line(ORIGIN, RIGHT)
                lash.set_stroke(DARK_GREY, 2)
                lash.scale_to_fit_width(0.27)
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
            ShowCreation(lashes, submobject_mode = "all_at_once"),
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
        self.dither()

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
        background_plane.highlight(GREY)
        background_plane.fade()
        circle = Circle(radius = 2, color = YELLOW)

        x, y = [np.sqrt(2)/2]*2
        dot = Dot(2*x*RIGHT + 2*y*UP, color = LIGHT_GREY)

        equation = TexMobject("x", "^2", "+", "y", "^2", "=", "1")
        equation.highlight_by_tex("x", GREEN)
        equation.highlight_by_tex("y", RED)
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
        numbers[0].highlight(GREEN)
        numbers[1].highlight(RED)

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
        self.dither()

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
        self.dither()

class GreatSourceOfMaterial(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "It's a great source \\\\ of material.",
            target_mode = "hooray"
        )
        self.change_student_modes(*["happy"]*3)
        self.dither(3)

class CirclesSpheresSumsSquares(ExternallyAnimatedScene):
    pass

class BackAndForth(Scene):
    def construct(self):
        analytic = TextMobject("Analytic")
        analytic.shift(SPACE_WIDTH*LEFT/2)
        analytic.to_edge(UP, buff = MED_SMALL_BUFF)
        geometric = TextMobject("Geometric")
        geometric.shift(SPACE_WIDTH*RIGHT/2)
        geometric.to_edge(UP, buff = MED_SMALL_BUFF)
        h_line = Line(LEFT, RIGHT).scale(SPACE_WIDTH)
        h_line.to_edge(UP, LARGE_BUFF)
        v_line = Line(UP, DOWN).scale(SPACE_HEIGHT)
        self.add(analytic, geometric, h_line, v_line)

        pair = TexMobject("(", "x", ",", "y", ")")
        pair.shift(SPACE_WIDTH*LEFT/2 + SPACE_HEIGHT*UP/3)
        triplet = TexMobject("(", "x", ",", "y", ",", "z", ")")
        triplet.shift(SPACE_WIDTH*LEFT/2 + SPACE_HEIGHT*DOWN/2)
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
        plane_group.shift(SPACE_WIDTH*RIGHT/2)


        self.play(Write(pair))
        # self.play(ShowCreation(pair.arrow))
        self.play(ShowCreation(plane, run_time = 3))
        self.play(Write(triplet))
        # self.play(ShowCreation(triplet.arrow))
        self.dither(3)
        for tup, eq, to_draw in (pair, circle_eq, circle), (triplet, sphere_eq, VMobject()):
            for mob in tup, eq:
                mob.xyz = VGroup(*filter(
                    lambda sm : sm is not None,
                    map(mob.get_part_by_tex, "xyz")
                ))
            self.play(
                ReplacementTransform(tup.xyz, eq.xyz),
                FadeOut(VGroup(*filter(
                    lambda sm : sm not in tup.xyz, tup
                ))),
            )
            self.play(
                Write(VGroup(*filter(
                    lambda sm : sm not in eq.xyz, eq
                ))),
                ShowCreation(to_draw)
            )
        self.dither(3)

class SphereForming(ExternallyAnimatedScene):
    pass

class PreviousVideos(Scene):
    def construct(self):
        titles = VGroup(*map(TextMobject, [
            "Pi hiding in prime regularities",
            "Visualizing all possible pythagorean triples",
            "Borsuk-Ulam theorem",
        ]))
        titles.to_edge(UP, buff = MED_SMALL_BUFF)
        screen = ScreenRectangle(height = 6)
        screen.next_to(titles, DOWN)

        title = titles[0]
        self.add(title, screen)
        self.dither(2)
        for new_title in titles[1:]:
            self.play(Transform(title, new_title))
            self.dither(2)

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
        alt_tups = map(TextMobject, [
            "$(x_1, x_2, x_3, x_4, x_5)?$",
            "$(x_1, x_2, \\dots, x_{99}, x_{100})?$"
        ])

        self.student_says(question, run_time = 1)
        self.dither()
        for alt_tup in alt_tups:
            alt_tup.move_to(tup)
            self.play(Transform(tup, alt_tup))
            self.dither()
        self.dither()
        self.play(
            RemovePiCreatureBubble(self.students[1]),
            self.teacher.change, "raise_right_hand"
        )
        self.change_student_modes(
            *["confused"]*3,
            look_at_arg = self.teacher.get_top() + 2*UP
        )
        self.play(self.teacher.look, UP)
        self.dither(5)
        self.student_says(
            "I...don't see it.",
            target_mode = "maybe",
            student_index = 0
        )
        self.dither(3)

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

    def add_equation(self):
        quaternion = TexMobject(
            "\\frac{1}{2}", "+", 
            "0", "\\textbf{i}", "+",
            "\\frac{\\sqrt{6}}{4}", "\\textbf{j}", "+",
            "\\frac{\\sqrt{6}}{4}", "\\textbf{k}",
        )
        quaternion.shift(SPACE_WIDTH*LEFT/2)
        equation = TexMobject(
            "\\textbf{i}", "^2", "=",
            "\\textbf{j}", "^2", "=",
            "\\textbf{k}", "^2", "=",
            "\\textbf{i}", "\\textbf{j}", "\\textbf{k}", "=",
            "-1"
        )
        equation.shift(SPACE_WIDTH*RIGHT/2)
        VGroup(quaternion, equation).to_edge(UP)
        for mob in quaternion, equation:
            mob.highlight_by_tex_to_color_map({
                "i" : RED,
                "j" : GREEN,
                "k" : BLUE,
            })

        brace = Brace(quaternion, DOWN)
        words = brace.get_text("4 numbers")

        self.play(
            Write(quaternion),
            Write(equation),
            GrowFromCenter(brace),
            FadeIn(words),
            run_time = 2
        )
        self.play(*[
            ApplyMethod(pi.change, "pondering", quaternion)
            for pi in self.pi_creatures
        ])
        self.dither()
        self.play(FadeOut(VGroup(brace, words)))


        self.quaternion = quaternion
        self.equation = equation

    def introduce_characters(self):
        titles = VGroup(*map(TextMobject, [
            "Mathematician",
            "Computer scientist",
            "Physicist",
        ]))
        self.remove(*self.pi_creatures)
        for title, pi in zip(titles, self.pi_creatures):
            title.next_to(pi, DOWN)
            self.play(
                Animation(VectorizedPoint(pi.eyes.get_center())),
                FadeIn(pi),
                Write(title, run_time = 1),
            )
        self.dither()

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
        examples.arrange_submobjects(RIGHT, buff = 2)
        examples.next_to(self.pi_creatures, UP, MED_LARGE_BUFF)
        labels = VGroup(*map(TextMobject, ["2D", "3D"]))

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
            self.dither()
        self.dither()
        self.play(
            FadeOut(examples),
            VGroup(self.quaternion, self.equation).shift, 2*DOWN,
            Write(title, run_time = 2)
        )
        self.play(*[
            ApplyMethod(
                pi.change, mode, self.equation,
                run_time = 2,
                rate_func = squish_rate_func(smooth, a, a+0.5)
            )
            for pi, mode, a in zip(
                self.pi_creatures, 
                ["confused", "sassy", "erm"],
                np.linspace(0, 0.5, len(self.pi_creatures))
            )
        ])
        self.dither()
        self.play(Animation(self.quaternion))
        self.dither(2)



    ######

    def create_pi_creatures(self):
        mathy = Mathematician()
        physy = PiCreature(color = PINK)
        compy = PiCreature(color = PURPLE)
        pi_creatures = VGroup(mathy, compy, physy)
        for pi in pi_creatures:
            pi.scale(0.7)
        pi_creatures.arrange_submobjects(RIGHT, buff = 3)
        pi_creatures.to_edge(DOWN, buff = LARGE_BUFF)
        return pi_creatures

class OfferAHybrid(SliderScene):
    CONFIG = {
        "n_sliders" : 3,
    }
    def construct(self):
        self.remove(self.sliders)
        titles = self.get_titles()
        h_line = Line(LEFT, RIGHT).scale(SPACE_WIDTH)
        h_line.next_to(titles, DOWN)
        v_lines = VGroup(*[
            Line(UP, DOWN).scale(SPACE_HEIGHT)
            for x in range(2)
        ])
        v_lines.generate_target()
        for line, vect in zip(v_lines.target, [LEFT, RIGHT]):
            line.shift(vect*SPACE_WIDTH/3)

        equation = TexMobject("x^2 + y^2 + z^2 = 1")
        equation.generate_target()
        equation.shift(SPACE_WIDTH*LEFT/2)
        equation.target.shift(2*SPACE_WIDTH*LEFT/3)

        self.add(titles, h_line, v_lines, equation)
        self.dither()
        self.play(*map(MoveToTarget, [titles, v_lines, equation]))
        self.play(Write(self.sliders, run_time = 1))
        self.initialize_ambiant_slider_movement()
        self.dither(10)
        self.wind_down_ambient_movement()
        self.dither()

    def get_titles(self):
        titles = VGroup(*map(TextMobject, [
            "Analytic", "Hybrid", "Geometric"
        ]))
        titles.to_edge(UP)
        titles[1].highlight(BLUE)
        titles.generate_target()
        titles[1].scale_in_place(0.001)
        titles[0].shift(SPACE_WIDTH*LEFT/2)
        titles.target[0].shift(2*SPACE_WIDTH*LEFT/3)
        titles[2].shift(SPACE_WIDTH*RIGHT/2)
        titles.target[2].shift(2*SPACE_WIDTH*RIGHT/3)
        return titles

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
        equations = VGroup(*map(TexMobject, [
            "x^2 + y^2 = 1",
            "x^2 + y^2 + z^2 = 1",
            "x^2 + y^2 + z^2 + w^2 = 1",
        ]))
        colors = [YELLOW, GREEN, BLUE]
        for equation, edge, color in zip(equations, [LEFT, ORIGIN, RIGHT], colors):
            equation.highlight(color)
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
                LaggedStart(ShowCreation, sphere),
            )
        self.dither()

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
        square.scale_to_fit_width(equation.get_width())
        square.stretch_to_fit_height(3)
        square.next_to(equation, vect)
        square.highlight(self.screen_rect_color)
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
        descriptor[1].highlight(BLUE)
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
        self.dither()
        self.play(Write(descriptor, run_time = 2))
        self.dither()
        self.play(
            dot.move_to, equation.get_left(),
            dot.set_fill, None, 0,
            path_arc = -np.pi/12
        )
        self.dither(2)

        self.sphere_words = sphere_words
        self.sphere_arrow = arrow
        self.descriptor = descriptor

    def talk_through_animation(self):
        sphere = self.spheres[-1]

        morty = self.pi_creature
        alt_dims = VGroup(*map(TextMobject, ["5D", "6D", "7D"]))
        alt_dims.next_to(morty.eyes, UP, SMALL_BUFF)
        alt_dim = alt_dims[0]

        self.play(FadeIn(morty))
        self.play(morty.change, "raise_right_hand", sphere)
        self.dither(3)
        self.play(morty.change, "confused", sphere)
        self.dither(3)
        self.play(
            morty.change, "erm", alt_dims,
            FadeIn(alt_dim)
        )
        for new_alt_dim in alt_dims[1:]:
            self.dither()
            self.play(Transform(alt_dim, new_alt_dim))
        self.dither()
        self.play(morty.change, "concerned_musician")
        self.play(FadeOut(alt_dim))
        self.dither()
        self.play(morty.change, "angry", sphere)
        self.dither(2)

    def transition_to_next_scene(self):
        equation = self.equations[-1]
        self.equations.remove(equation)
        tup = self.descriptor[1]
        self.descriptor.remove(tup)

        equation.generate_target()
        equation.target.center().to_edge(UP)
        tup.generate_target()
        tup.target.next_to(equation.target, DOWN)
        tup.target.highlight(WHITE)

        self.play(LaggedStart(FadeOut, VGroup(*[
            self.equations, self.spheres,
            self.sphere_words, self.sphere_arrow,
            self.descriptor,
            self.pi_creature
        ])))
        self.play(*map(MoveToTarget, [equation, tup]))
        self.dither()

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
        equation.highlight(BLUE)
        tup.next_to(equation, DOWN)

        self.sliders.next_to(tup, DOWN)
        self.sliders.shift(0.8*LEFT)

        self.add(equation, tup)
        self.dither()
        self.equation = equation
        self.tup = tup

    def introduce_sliders(self):
        self.set_to_vector(self.start_vect)

        numbers = self.tup.get_parts_by_tex(".")
        self.tup.remove(*numbers)
        dials = VGroup(*[slider.dial for slider in self.sliders])
        dial_copies = dials.copy()
        dials.set_fill(opacity = 0)

        self.play(LaggedStart(FadeIn, self.sliders))
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
        self.dither(10)

    def ask_about_constraint(self):
        equation = self.equation
        rect = SurroundingRectangle(equation, color = GREEN)
        randy = Randolph().scale(0.5)
        randy.next_to(rect, DOWN+LEFT, LARGE_BUFF)

        self.play(ShowCreation(rect))
        self.play(FadeIn(randy))
        self.play(randy.change, "pondering", rect)
        self.dither()
        for mob in self.sliders, rect:
            self.play(randy.look_at, mob)
            self.play(Blink(randy))
            self.dither()
        self.dither()

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
        plane.axes.highlight(GREY)
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
        self.dither(total_time - 1)
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
        decimals.arrange_submobjects(RIGHT, buff = LARGE_BUFF)
        decimals.next_to(rects, DOWN, LARGE_BUFF)

        real_estate_word = TextMobject("``Real estate''")
        real_estate_word.next_to(decimals, DOWN, MED_LARGE_BUFF)
        self.play(FadeIn(real_estate_word))

        colors = GREEN, RED
        arrows = VGroup()
        for rect, decimal, color in zip(rects, decimals, colors):
            rect.highlight(color)
            decimal.highlight(color)
            arrow = Arrow(
                rect.get_bottom()+SMALL_BUFF*UP, decimal.get_top(),
                tip_length = 0.2,
            )
            arrow.highlight(color)
            arrows.add(arrow)

            self.play(ShowCreation(rect))
            self.play(
                ShowCreation(arrow),
                Write(decimal)
            )
            self.dither()

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
                p1, p2 = map(slider.number_to_point, [x1, x2])
                rect = Rectangle(
                    stroke_width = 0,
                    fill_opacity = 0.5,
                    width = 0.25,
                    height = (p2-p1)[1]
                )
                rect.move_to((p1+p2)/2)
                if np.mean([x1, x2]) == 0:
                    rect.highlight(BLUE)
                    blue_rects.add(rect)
                else:
                    rect.highlight(RED)
                    red_rects.add(rect)

        blue_rects.save_state()
        self.play(DrawBorderThenFill(blue_rects))
        self.dither()
        self.play(ReplacementTransform(blue_rects, red_rects))
        self.dither()
        self.play(FadeOut(red_rects))

        blue_rects.restore()
        self.real_estate_rects = VGroup(blue_rects, red_rects)

    def nudge_x_from_one_example(self):
        x_re = self.decimals[0]
        rect = SurroundingRectangle(x_re)

        self.reset_dials([1, 0])
        self.dither()
        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))
        self.play(FocusOn(self.dot))
        self.dither()
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
        self.dither(2)
        self.play(
            GrowFromCenter(y_brace),
            Write(y_text),
        )
        self.dither(2)
        self.play(FadeIn(self.real_estate_rects))
        self.reset_dials([1, 0], run_time = 1)
        self.reset_dials([0.9, -np.sqrt(0.19)], run_time = 2)
        self.play(FadeOut(self.real_estate_rects))
        self.play(*map(FadeOut, [x_brace, y_brace, x_text, y_text]))
        self.dither()

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
        self.dither()
        for x in np.arange(0.95, 0.05, -0.05):
            self.reset_dials(
                [np.sqrt(x), np.sqrt(1-x)],
                run_time = 0.5
            )
            self.dither(0.5)
        self.initialize_ambiant_slider_movement()
        self.dither(10)

    def write_distance_squared(self):
        d_squared = TexMobject("(\\text{Distance})^2")
        d_squared.next_to(self.real_estate_word, DOWN)
        d_squared.highlight(YELLOW)

        self.play(Write(d_squared))
        self.dither(3)

    #####

    def update_frame(self, *args, **kwargs):
        if hasattr(self, "dot"):
            x, y = self.get_vector()
            self.dot.move_to(self.plane.coords_to_point(x, y))
        if hasattr(self, "decimals"):
            for anim in self.decimal_update_anims:
                anim.update(0)
        SliderScene.update_frame(self, *args, **kwargs)

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
        self.add_real_estate_decimals()
        self.initialize_ambiant_slider_movement()
        self.point_out_third_slider()
        self.dither(3)
        self.hold_x_at(0.5, 12)
        self.hold_x_at(0.85, 5)
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
        decimals.arrange_submobjects(RIGHT, buff = LARGE_BUFF)
        decimals.next_to(rects, DOWN, LARGE_BUFF)

        colors = [GREEN, RED, BLUE]
        arrows = VGroup()
        for rect, decimal, color in zip(rects, decimals, colors):
            rect.highlight(color)
            decimal.highlight(color)
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
        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))

    def hold_x_at(self, x_val, wait_time):
        #Save these
        all_sliders = self.sliders
        original_total_real_estate = self.total_real_estate

        self.reset_dials([x_val], run_time = 3)
        self.sliders = VGroup(*self.sliders[1:])
        self.total_real_estate = self.total_real_estate-x_val**2
        self.initialize_ambiant_slider_movement()
        self.dither(wait_time-2)
        self.wind_down_ambient_movement()
        self.sliders = all_sliders
        self.total_real_estate = original_total_real_estate
        self.initialize_ambiant_slider_movement()

    ####

class SphereAtRest(ExternallyAnimatedScene):
    pass

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
            self.dither(self.frame_duration)

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
        self.dither()
        self.play(
            Animation(self.sliders),
            self.teacher.change, "raise_right_hand",
        )
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = self.sliders
        )
        self.dither(4)

    def fix_one_slider(self):
        x_slider = self.sliders[0]
        dial = x_slider.dial
        self.wind_down_ambient_movement(dither = False)
        self.play(self.teacher.change, "speaking")
        self.sliders.remove(x_slider)
        self.total_real_estate = np.linalg.norm(self.get_vector())**2
        self.initialize_ambiant_slider_movement()
        arrow = Arrow(LEFT, RIGHT, color = GREEN)
        arrow.next_to(dial, LEFT)
        self.play(
            ShowCreation(arrow),
            dial.highlight, arrow.get_color()
        )
        self.change_student_modes(
            "erm", "confused", "hooray",
            look_at_arg = self.sliders,
            added_anims = [self.teacher.change, "plain"]
        )
        self.dither(5)

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
        self.dither(4)
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
        self.dither(7)

class TwoDBoxExample(Scene):
    def setup(self):
        scale_factor = 1.7
        self.plane = NumberPlane()
        self.plane.scale(scale_factor)
        self.plane.add_coordinates()
        self.plane.axes.highlight(GREY)
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
        self.dither()

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

        self.play(LaggedStart(ShowCreation, circles))
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
            self.dither(0.5)
        self.play(*map(FadeOut, [radius, r_equals_1]))
        self.dither()

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
        self.dither(2)
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
        self.dither(2)
        self.play(ReplacementTransform(sqrt_1_plus_1, sqrt_2))
        self.play(
            Write(root_2_value, run_time = 1),
            *map(FadeOut, [bottom_one, side_one])
        )
        self.dither()
        self.play(ShowCreation(corner_radius))
        self.play(Rotating(
            corner_radius, about_point = c0_center,
            run_time = 2,
            rate_func = smooth
        ))
        self.play(FadeOut(triangle), Animation(corner_radius))
        self.dither()
        self.play(
            Write(rhs),
            Transform(sqrt_2, sqrt_2_target),
        )
        self.play(Write(root_2_minus_1_value))
        self.dither(2)

class ThreeDBoxExample(ExternallyAnimatedScene):
    pass

class ThreeDCubeCorners(Scene):
    def construct(self):
        coordinates = VGroup(*[
            TexMobject("(%d,\\, %d,\\, %d)"%(x, y, z))
            for x, y, z in it.product(*3*[[1, -1]])
        ])
        coordinates.arrange_submobjects(DOWN, aligned_edge = LEFT)
        name = TextMobject("Corners: ")
        name.next_to(coordinates[0], LEFT)
        group = VGroup(name, coordinates)
        group.scale_to_fit_height(2*SPACE_HEIGHT - 1)
        group.to_edge(LEFT)

        self.play(Write(name, run_time = 2))
        self.play(LaggedStart(FadeIn, coordinates, run_time = 3))
        self.dither()

class ShowDistanceFormula(TeacherStudentsScene):
    def construct(self):
        rule = TexMobject(
            "||(", "x_1", ", ", "x_2", "\\dots, ", "x_n", ")||", 
            "=", 
            "\\sqrt", "{x_1^2", " + ", "x_2^2", " +\\cdots", "x_n^2", "}"
        )
        rule.highlight_by_tex_to_color_map({
            "x_1" : GREEN,
            "x_2" : RED,
            "x_n" : BLUE,
        })
        for part in rule.get_parts_by_tex("x_"):
            if len(part) > 2:
                part[1].highlight(WHITE)
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
        self.dither(3)
        self.student_says("Why?", student_index = 0)
        self.play(self.teacher.change, "thinking")
        self.dither(3)

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
        bottom.highlight(tex_to_color_map["x"])
        side = Line(rect.get_bottom(), rect.get_top())
        side.move_to(rect.get_right())
        side.highlight(tex_to_color_map["y"])

        x = TexMobject("x")
        x.next_to(rect.get_bottom(), UP, SMALL_BUFF)
        y = TexMobject("y")
        y.next_to(rect.get_right(), LEFT, SMALL_BUFF)
        hyp = TexMobject("\\sqrt", "{x", "^2 + ", "y", "^2}")
        hyp.highlight_by_tex_to_color_map(tex_to_color_map)
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
        self.dither()
        self.play(
            group.rotate, 0.45*np.pi, LEFT,
            group.shift, 2*DOWN
        )

        corner = diag.get_end()
        z_line = Line(corner, corner + 3*UP)
        z_line.highlight(tex_to_color_map["z"])
        z = TexMobject("z")
        z.highlight(tex_to_color_map["z"])
        z.next_to(z_line, RIGHT)
        dot = Dot(z_line.get_end())
        three_d_diag = Line(diag.get_start(), z_line.get_end())
        three_d_diag.highlight(MAROON_B)

        self.play(
            ShowCreation(z_line),
            ShowCreation(dot),
            Write(z, run_time = 1)
        )
        self.play(ShowCreation(three_d_diag))
        self.dither()

        full_group = VGroup(group, z_line, z, three_d_diag, dot)
        self.play(Rotating(
            full_group, radians = -np.pi/6,
            axis = UP, 
            run_time = 10,
        ))
        self.dither()

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
        inner_r.highlight(GREEN_C)
        VGroup(question, answer).shift(0.55*RIGHT)

        self.play(Write(question))
        self.dither(2)
        self.play(ReplacementTransform(question, answer))
        self.dither(2)
        self.play(Write(inner_r))
        self.dither(2)

class AskAboutHigherDimensions(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "What happens for \\\\ higher dimensions?"
        )
        self.change_student_modes(*["pondering"]*3)
        self.dither(2)
        self.student_thinks(
            "$\\sqrt{N} - 1$",
            target_mode = "happy",
            student_index = 1
        )
        self.dither()
        pi = self.students[1]
        self.play(pi.change, "confused", pi.bubble)
        self.dither(3)

class TenSliders(SliderScene):
    CONFIG = {
        "n_sliders" : 10,
        "run_time": 30,
    }
    def construct(self):
        self.initialize_ambiant_slider_movement()
        self.dither(self.run_time)

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
                LEFT, MED_LARGE_BUFF
            )
        self.plane.axes.highlight(BLUE)

        ##Add box material
        corner_circles = VGroup(*[
            self.circle.copy().move_to(
                self.plane.coords_to_point(*coords)
            ).highlight(GREY)
            for coords in (1, 1), (-1, 1), (-1, -1)
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
        self.force_skipping()

        self.ask_about_off_center_circle()
        self.recenter_circle()
        self.write_x_and_y_real_estate()
        self.swap_with_top_right_circle()
        self.show_center_circle()
        self.describe_tangent_point()

    def ask_about_off_center_circle(self):
        question = TextMobject("Off-center circles?")
        question.next_to(self.plane, UP)

        self.initialize_ambiant_slider_movement()
        self.play(Write(question))
        self.dither(4)
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
                for mob in slider.real_estate_ticks, slider.dial
            ]
        )
        self.center_point = [0, 0]
        for x, slider in zip(self.center_point, self.sliders):
            slider.center_value = x
        self.initialize_ambiant_slider_movement()
        self.dither(7)
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
                for mob in slider.real_estate_ticks, slider.dial
            ]
        )
        self.center_point = original_center_point
        for x, slider in zip(self.center_point, self.sliders):
            slider.center_value = x

        self.initialize_ambiant_slider_movement()
        self.dither(5)

    def write_x_and_y_real_estate(self):
        phrases = VGroup(
            TextMobject("$x$", "real estate:", "$(x-1)^2$"),
            TextMobject("$y$", "real estate:", "$(y+1)^2$"),
        )
        phrases.next_to(self.plane, UP)
        phrases[0].highlight_by_tex("x", GREEN)
        phrases[1].highlight_by_tex("y", RED)
        x_brace, y_brace = [
            Brace(slider.real_estate_ticks, RIGHT)
            for slider in self.sliders
        ]
        x_brace.highlight(GREEN)
        y_brace.highlight(RED)

        self.play(FadeOut(self.question))
        self.play(
            Write(phrases[0]),
            GrowFromCenter(x_brace)
        )
        self.dither(3)
        self.play(
            Transform(*phrases),
            Transform(x_brace, y_brace)
        )
        self.dither(5)
        self.wind_down_ambient_movement(dither = False)
        self.play(*map(FadeOut, [x_brace, phrases[0]]))

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
                for mob in slider.real_estate_ticks, slider.dial
            ]
        )
        slider.center_value = 1
        self.center_point[1] = 1
        self.initialize_ambiant_slider_movement()
        self.dither(3)

    def show_center_circle(self):
        origin = self.plane.coords_to_point(0, 0)
        radius = np.linalg.norm(
            self.plane.coords_to_point(np.sqrt(2)-1, 0) - origin
        )
        circle = Circle(radius = radius, color = GREEN)
        circle.move_to(origin)

        self.play(FocusOn(circle))
        self.play(GrowFromCenter(circle, run_time = 2))
        self.dither(3)
        self.wind_down_ambient_movement()

    def describe_tangent_point(self):
        
        self.revert_to_original_skipping_status()
        self.reset_dials([
            1-np.sqrt(2)/2, 1-np.sqrt(2)/2
        ])
        self.dither()







































