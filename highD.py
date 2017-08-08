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
from scene import Scene
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
        "label_scale_val" : 0.75,
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
        dial.move_to(self.number_to_point(0))
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
        ):
        self.real_estate_ticks = VGroup(*[   
            self.get_tick(u*np.sqrt(x))
            for x in np.arange(re_per_tick, 1, re_per_tick)
            for u in [-1, 1]
        ])
        self.real_estate_ticks.set_stroke(width = 3)
        self.real_estate_ticks.gradient_highlight(*colors)
        self.add(self.real_estate_ticks)
        self.add(self.dial)
        return self.real_estate_ticks

    def set_value(self, x):
        for dial, val in (self.dial, x), (self.re_dial, x**2):
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
            self.center_value + sign*np.sqrt(re)
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
        sliders[0].set_value(np.sqrt(self.total_real_estate))
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

    def reset_dials(self, values, fixed_sliders = None):
        if fixed_sliders is None: fixed_sliders = []
        unspecified_sliders = [
            self.sliders[i]
            for i in range(len(self.sliders))
            if i  >= len(values) or values[i] is None
            if self.sliders[i] not in fixed_sliders
        ]
        for value, slider in zip(values, self.sliders):
            if value is not None:
                slider.set_value(value)
        #Readjust sliers with unspecified values that are not fixed
        real_estate_diff = self.total_real_estate - self.get_current_total_real_estate()
        for i, slider in enumerate(unspecified_sliders):
            n_remaining = len(unspecified_sliders[i:])
            d_re = real_estate_diff / n_remaining
            left_over = slider.change_real_estate(d_re)
            real_estate_diff -= (d_re - left_over)
        if real_estate_diff > 0.001:
            raise Exception("Overspecified reset")

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
        self.add_foreground_mobjects(self.sliders)

    def wind_down_ambient_movement(self, time = 1):
        self.ambient_change_end_time = self.ambient_change_time + time

    def ambient_slider_movement_update(self):
        #Set velocity_magnitude based on start up or wind down
        velocity_magnitude = float(self.ambient_velocity_magnitude)
        if self.ambient_change_time <= 1:
            velocity_magnitude *= smooth(self.ambient_change_time)
        time_until_end = self.ambient_change_end_time - self.ambient_change_time
        if time_until_end <= 1:
            velocity_magnitude *= smooth(time_until_end)
        if time_until_end <= 0:
            self.ambiently_change_sliders = False
            return

        center_point = self.get_center_point()
        target_vector = self.get_vector() - center_point
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

        self.reset_dials(target_vector + center_point)
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




































