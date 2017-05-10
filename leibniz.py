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
from topics.complex_numbers import *
from scene import Scene
from scene.reconfigurable_scene import ReconfigurableScene
from scene.zoomed_scene import *
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

# revert_to_original_skipping_status

def chi_func(n):
    if n%2 == 0:
        return 0
    if n%4 == 1:
        return 1
    else:
        return -1

######

class Introduction(PiCreatureScene):
    def construct(self):
        self.introduce_three_objects()
        self.show_screen()

    def introduce_three_objects(self):
        primes = self.get_primes()
        primes.to_corner(UP+RIGHT)
        primes.shift(DOWN)
        plane = self.get_complex_numbers()
        plane.shift(2*LEFT)
        pi_group = self.get_pi_group()
        pi_group.next_to(primes, DOWN, buff = MED_LARGE_BUFF)
        pi_group.shift_onto_screen()

        morty = self.get_primary_pi_creature()
        video = VideoIcon()
        video.highlight(TEAL)
        video.next_to(morty.get_corner(UP+LEFT), UP)

        self.play(
            morty.change_mode, "raise_right_hand",
            DrawBorderThenFill(video)
        )
        self.dither()
        self.play(
            Write(primes, run_time = 2),
            morty.change_mode, "happy",
            video.scale_to_fit_height, 2*SPACE_WIDTH,
            video.center,
            video.set_fill, None, 0
        )
        self.dither()
        self.play(
            Write(plane, run_time = 2),
            morty.change, "raise_right_hand"
        )
        self.dither()
        self.remove(morty)
        morty = morty.copy()
        self.add(morty)
        self.play(
            ReplacementTransform(
                morty.body,
                pi_group.get_part_by_tex("pi"),
                run_time = 1
            ),
            FadeOut(VGroup(morty.eyes, morty.mouth)),
            Write(VGroup(*pi_group[1:]))
        )
        self.dither(2)
        self.play(
            plane.scale_to_fit_width, pi_group.get_width(),
            plane.next_to, pi_group, DOWN, MED_LARGE_BUFF
        )

    def show_screen(self):
        screen = ScreenRectangle(height = 4.3)
        screen.to_edge(LEFT)
        titles = VGroup(
            TextMobject("From zeta video"),
            TextMobject("Coming up")
        )
        for title in titles:
            title.next_to(screen, UP)
            title.highlight(YELLOW)
        self.play(
            ShowCreation(screen),
            FadeIn(titles[0])
        )
        self.show_frame()
        self.dither(2)
        self.play(Transform(*titles))
        self.dither(3)

    def get_primes(self):
        return TexMobject("2, 3, 5, 7, 11, 13, \\dots")

    def get_complex_numbers(self):
        plane = ComplexPlane(
            x_radius = 3,
            y_radius = 2.5,
        )
        plane.add_coordinates()
        point = plane.number_to_point(complex(1, 2))
        dot = Dot(point, radius = YELLOW)
        label = TexMobject("1 + 2i")
        label.add_background_rectangle()
        label.next_to(dot, UP+RIGHT, buff = SMALL_BUFF)
        label.highlight(YELLOW)
        plane.label = label
        plane.add(dot, label)
        return plane

    def get_pi_group(self):
        result = TexMobject("\\pi", "=", "%.8f\\dots"%np.pi)
        pi = result.get_part_by_tex("pi")
        pi.scale(2, about_point = pi.get_right())
        pi.highlight(MAROON_B)
        return result

class ShowSum(TeacherStudentsScene):
    CONFIG = {
        "num_terms_to_add" : 40,
    }
    def construct(self):
        self.say_words()
        self.show_sum()

    def say_words(self):
        self.teacher_says("This won't be easy")
        self.change_student_modes(
            "hooray", "sassy", "angry"
        )
        self.dither(2)

    def show_sum(self):
        line = UnitInterval()
        line.add_numbers(0, 1)
        line.shift(UP)
        sum_point = line.number_to_point(np.pi/4)

        numbers = [0] + [
            ((-1)**n)/(2.0*n + 1) 
            for n in range(self.num_terms_to_add)
        ]
        partial_sums = np.cumsum(numbers)
        points = map(line.number_to_point, partial_sums)
        arrows = [
            Arrow(
                p1, p2, 
                tip_length = 0.2*min(1, np.linalg.norm(p1-p2)),
                buff = 0
            )
            for p1, p2 in zip(points, points[1:])
        ]
        dot = Dot(points[0])

        sum_mob = TexMobject(
            "1", "-\\frac{1}{3}", "+\\frac{1}{5}", 
            "-\\frac{1}{7}", "+\\cdots"
        )
        sum_mob.to_edge(UP)
        sum_mob.shift(LEFT)
        rhs = TexMobject(
            "=", "\\frac{\\pi}{4}",
            "\\approx %.5f\\dots"%(np.pi/4)
        )
        rhs.next_to(sum_mob, RIGHT)
        rhs.highlight_by_tex("pi", YELLOW)
        sum_arrow = Arrow(
            rhs.get_part_by_tex("pi"),
            sum_point
        )
        fading_terms = [
            TexMobject(sign + "\\frac{1}{%d}"%(2*n + 1))
            for n, sign in zip(
                range(self.num_terms_to_add),
                it.cycle("+-")
            )
        ]
        for fading_term, arrow in zip(fading_terms, arrows):
            fading_term.next_to(arrow, UP)

        terms = it.chain(sum_mob, it.repeat(None))
        last_arrows = it.chain([None], arrows)
        last_fading_terms = it.chain([None], fading_terms)

        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = line,
            added_anims = [
                FadeIn(VGroup(line, dot)),
                RemovePiCreatureBubble(
                    self.teacher,
                    target_mode = "raise_right_hand"
                )
            ]
            
        )
        run_time = 1
        for term, arrow, last_arrow, fading_term, last_fading_term in zip(
            terms, arrows, last_arrows, fading_terms, last_fading_terms
            ):
            anims = []
            if term:
                anims.append(Write(term))
            if last_arrow:
                anims.append(FadeOut(last_arrow))
            if last_fading_term:
                anims.append(FadeOut(last_fading_term))
            dot_movement = ApplyMethod(dot.move_to, arrow.get_end())
            anims.append(ShowCreation(arrow))
            anims.append(dot_movement)
            anims.append(FadeIn(fading_term))
            self.play(*anims, run_time = run_time)
            if term:
                self.dither()
            else:
                run_time *= 0.8
        self.play(
            FadeOut(arrow),
            FadeOut(fading_term),
            dot.move_to, sum_point
        )
        self.play(
            Write(rhs),
            ShowCreation(sum_arrow)
        )
        self.dither()
        self.change_student_modes("erm", "confused", "maybe")
        self.play(self.teacher.change_mode, "happy")
        self.dither(2)

class FermatsDreamExcerptWrapper(Scene):
    def construct(self):
        words = TextMobject(
            "From ``Fermat's dream'' by Kato, Kurokawa and Saito"
        )
        words.scale(0.8)
        words.to_edge(UP)
        self.add(words)
        self.dither()

class ShowSumMeantForFadedBackground(Scene):
    def construct(self):
        tex_mob = TexMobject(
            "1 - \\frac{1}{3} + \\frac{1}{5} - \\frac{1}{7} + \\cdots",
            "=", "\\frac{\\pi}{4}"
        )
        tex_mob.highlight_by_tex("pi", YELLOW)
        self.add(tex_mob)
        self.dither()

class ShowCalculus(PiCreatureScene):
    def construct(self):
        frac_sum = TexMobject(
            "1 - \\frac{1}{3} + \\frac{1}{5} - \\frac{1}{7} + \\cdots",
        )
        int1 = TexMobject(
            "= \\int_0^1 (1 - x^2 + x^4 - \\dots )\\,dx"
        )
        int2 = TexMobject(
            "= \\int_0^1 \\frac{1}{1+x^2}\\,dx"
        )
        arctan = TexMobject("= \\tan^{-1}(1)")
        pi_fourths = TexMobject("= \\frac{\\pi}{4}")

        frac_sum.to_corner(UP+LEFT)
        frac_sum.shift(RIGHT)
        rhs_group = VGroup(int1, int2, arctan, pi_fourths)
        rhs_group.arrange_submobjects(
            DOWN, buff = MED_LARGE_BUFF,
            aligned_edge = LEFT
        )
        rhs_group.shift(
            frac_sum.get_right() + MED_SMALL_BUFF*RIGHT \
            -int1[0].get_left()
        )
        
        self.add(frac_sum)
        modes = it.chain(["plain"], it.cycle(["confused"]))
        for rhs, mode in zip(rhs_group, modes):
            self.play(
                FadeIn(rhs),
                self.pi_creature.change, mode
            )
            self.dither()
        self.change_mode("maybe")
        self.dither()
        self.look_at(rhs_group[-1])
        self.dither()
        self.pi_creature_says(
            "Where's the \\\\ circle?",
            bubble_kwargs = {"width" : 4, "height" : 3},
            target_mode = "maybe"
        )
        self.look_at(rhs_group[0])
        self.dither()

    def create_pi_creature(self):
        return Randolph(color = BLUE_C).to_corner(DOWN+LEFT)

class Outline(PiCreatureScene):
    def construct(self):
        self.generate_list()
        self.wonder_at_pi()
        self.count_lattice_points()
        self.write_steps_2_and_3()
        self.show_chi()
        self.show_complicated_formula()
        self.show_last_step()

    def generate_list(self):
        steps = VGroup(
            TextMobject("1. Count lattice points"),
            TexMobject("2. \\text{ Things like }17 = ", "4", "^2 + ", "1", "^2"),
            TexMobject("3. \\text{ Things like }17 = (", "4", " + ", "i", ")(", "4", " - ", "i", ")"),
            TextMobject("4. Introduce $\\chi$"),
            TextMobject("5. Shift perspective"),
        )
        for step in steps[1:3]:
            step.highlight_by_tex("1", RED, substring = False)
            step.highlight_by_tex("i", RED, substring = False)
            step.highlight_by_tex("4", GREEN, substring = False)
        steps.arrange_submobjects(
            DOWN, 
            buff = MED_LARGE_BUFF,
            aligned_edge = LEFT
        )
        steps.to_corner(UP+LEFT)

        self.steps = steps

    def wonder_at_pi(self):
        question = TexMobject("\\pi", "=???")
        pi = question.get_part_by_tex("pi")
        pi.scale(2, about_point = pi.get_right())
        pi.highlight(YELLOW)
        question.next_to(self.pi_creature.body, LEFT, aligned_edge = UP)
        self.think(
            "Who am I really?",
            look_at_arg = question,
            added_anims = [
                FadeIn(question)
            ]
        )
        self.dither(2)
        self.play(
            RemovePiCreatureBubble(self.pi_creature),
            question.to_corner, UP+RIGHT
        )

        self.question = question
        self.pi = question.get_part_by_tex("pi")

    def count_lattice_points(self):
        step = self.steps[0]
        plane = NumberPlane(
            x_radius = 10, y_radius = 10,
            secondary_line_ratio = 0,
            color = BLUE_E,
        )
        plane.scale_to_fit_height(6)
        plane.next_to(step, DOWN)
        plane.to_edge(LEFT)
        circle = Circle(
            color = YELLOW,
            radius = np.linalg.norm(
                plane.coords_to_points(10, 0) - \
                plane.coords_to_points(0, 0)
            )
        )
        plane_center = plane.coords_to_points(0, 0)
        circle.move_to(plane_center)
        lattice_points = VGroup(*[
            Dot(
                plane.coords_to_points(a, b), 
                radius = 0.05,
                color = PINK,
            )
            for a in range(-10, 11)
            for b in range(-10, 11)
            if a**2 + b**2 <= 10**2
        ])
        lattice_points.sort_submobjects(
            lambda p : np.linalg.norm(p - plane_center)
        )
        lattice_group = VGroup(plane, circle, lattice_points)

        self.play(ShowCreation(circle))
        self.play(Write(plane, run_time = 2), Animation(circle))
        self.play(
            *[
                DrawBorderThenFill(
                    dot,
                    stroke_width = 4,
                    stroke_color = YELLOW,
                    run_time = 4,
                    rate_func = squish_rate_func(
                        double_smooth, a, a + 0.25
                    )
                )
                for dot, a in zip(
                    lattice_points, 
                    np.linspace(0, 0.75, len(lattice_points))
                )
            ]
        )
        self.play(
            FadeIn(step)
        )
        self.dither()
        self.play(
            lattice_group.scale_to_fit_height, 2.5,
            lattice_group.next_to, self.question, DOWN,
            lattice_group.to_edge, RIGHT
        )

    def write_steps_2_and_3(self):
        for step in self.steps[1:3]:
            self.play(FadeIn(step))
            self.dither(2)
        self.dither()

    def show_chi(self):
        input_range = range(1, 7)
        chis = VGroup(*[
            TexMobject("\\chi(%d)"%n)
            for n in input_range
        ])
        chis.arrange_submobjects(RIGHT, buff = LARGE_BUFF)
        chis.set_stroke(WHITE, width = 1)
        numerators = VGroup()
        arrows = VGroup()
        for chi, n in zip(chis, input_range):
            arrow = TexMobject("\\Downarrow")
            arrow.next_to(chi, DOWN, SMALL_BUFF)
            arrows.add(arrow)
            value = TexMobject(str(chi_func(n)))
            value.highlight_by_tex("1", BLUE)
            value.highlight_by_tex("-1", GREEN)
            value.next_to(arrow, DOWN)
            numerators.add(value)
        group = VGroup(chis, arrows, numerators)
        group.scale_to_fit_width(1.3*SPACE_WIDTH)
        group.to_corner(DOWN+LEFT)

        self.play(FadeIn(self.steps[3]))
        self.play(*[
            FadeIn(
                mob, 
                run_time = 3,
                submobject_mode = "lagged_start"
            )
            for mob in [chis, arrows, numerators]
        ])
        self.change_mode("pondering")
        self.dither()

        self.chis = chis
        self.arrows = arrows
        self.numerators = numerators

    def show_complicated_formula(self):
        rhs = TexMobject(
            " = \\lim_{N \\to \\infty}",
            " \\frac{1}{N}",
            "\\sum_{n = 1}^N",
            "\\sum_{d | n} \\chi(d)",
        )
        pi = self.pi 
        self.add(pi.copy())
        pi.generate_target()
        pi.target.next_to(self.steps[3], RIGHT, MED_LARGE_BUFF)
        pi.target.shift(MED_LARGE_BUFF*DOWN)
        rhs.next_to(pi.target, RIGHT)

        self.play(
            MoveToTarget(pi),
            Write(rhs)
        )
        self.change_mode("confused")
        self.dither(2)

        self.complicated_formula = rhs

    def show_last_step(self):
        expression = TexMobject(
            "=", "\\frac{\\quad}{1}",
            *it.chain(*[
                ["+", "\\frac{\\quad}{%d}"%d]
                for d in range(2, len(self.numerators)+1)
            ] + [["+ \\cdots"]])
        )
        pi = self.pi
        pi.generate_target()
        pi.target.to_corner(DOWN+LEFT)
        pi.target.shift(UP)
        expression.next_to(pi.target, RIGHT)
        self.numerators.generate_target()
        for num, denom in zip(self.numerators.target, expression[1::2]):
            num.scale(1.2)
            num.next_to(denom, UP, MED_SMALL_BUFF)

        self.play(
            MoveToTarget(self.numerators),
            MoveToTarget(pi),
            FadeOut(self.chis),
            FadeOut(self.arrows),
            FadeOut(self.complicated_formula),
        )
        self.play(
            Write(expression),
            self.pi_creature.change_mode, "pondering"
        )
        self.dither(3)

    ########
    def create_pi_creature(self):
        return Randolph(color = BLUE_B).flip().to_corner(DOWN+RIGHT)

class LatticePointScene(Scene):
    CONFIG = {
        "y_radius" : 6,
        "x_radius" : None,
        "plane_center" : ORIGIN,
        "max_lattice_point_radius" : 6,
        "dot_radius" : 0.075,
        "secondary_line_ratio" : 0,
        "plane_color" : BLUE_E,
        "dot_color" : YELLOW,
        "dot_drawing_stroke_color" : PINK,
        "circle_color" : MAROON_D,
    }
    def setup(self):
        if self.x_radius is None:
            self.x_radius = self.y_radius*SPACE_WIDTH/SPACE_HEIGHT
        plane = NumberPlane(
            y_radius = self.y_radius,
            x_radius = self.x_radius,
            secondary_line_ratio = self.secondary_line_ratio,
            color = self.plane_color
        )
        plane.scale_to_fit_height(2*SPACE_HEIGHT)
        plane.shift(self.plane_center)
        self.add(plane)
        self.plane = plane

        self.setup_lattice_points()

    def setup_lattice_points(self):
        M = self.max_lattice_point_radius
        int_range = range(-M, M+1)
        self.lattice_points = VGroup()
        for x, y in it.product(*[int_range]*2):
            r_squared = x**2 + y**2
            if r_squared > M**2:
                continue
            dot = Dot(
                self.plane.coords_to_point(x, y),
                color = self.dot_color,
                radius = self.dot_radius,
            )
            dot.r_squared = r_squared
            self.lattice_points.add(dot)
        self.lattice_points.sort_submobjects(np.linalg.norm)

    def get_circle(self, radius = None, color = None):
        if radius is None:
            radius = self.max_lattice_point_radius
        if color is None:
            color = self.circle_color
        radius *= self.plane.get_space_unit_to_y_unit()
        circle = Circle(
            color = color,
            radius = radius,
        )
        circle.move_to(self.plane.get_center())
        return circle

    def get_lattice_points_on_r_squared_circle(self, r_squared):
        return VGroup(*filter(
            lambda dot : dot.r_squared == r_squared,
            self.lattice_points
        ))

    def draw_lattice_points(self, points = None, run_time = 4):
        if points is None:
            points = self.lattice_points
        self.play(*[
            DrawBorderThenFill(
                dot,
                stroke_width = 4,
                stroke_color = self.dot_drawing_stroke_color,
                run_time = run_time,
                rate_func = squish_rate_func(
                    double_smooth, a, a + 0.25
                ),
            )
            for dot, a in zip(
                points, 
                np.linspace(0, 0.75, len(points))
            )
        ])

class CountLatticePoints(LatticePointScene):
    CONFIG = {
        "y_radius" : 11,
        "max_lattice_point_radius" : 10,
        "dot_radius" : 0.05,
        "example_coords" : (7, 5),
    }
    def construct(self):
        self.introduce_lattice_point()
        self.draw_lattice_points_in_circle()
        self.turn_points_int_units_of_area()
        self.write_pi_R_squared()
        self.allude_to_alternate_counting_method()


    def introduce_lattice_point(self):
        x, y = self.example_coords
        example_dot = Dot(
            self.plane.coords_to_point(x, y),
            color = self.dot_color,
            radius = 1.5*self.dot_radius,
        )
        label = TexMobject(str(self.example_coords))
        label.add_background_rectangle()
        label.next_to(example_dot, UP+RIGHT, buff = 0)
        h_line = Line(
            ORIGIN, self.plane.coords_to_point(x, 0),
            color = GREEN
        )
        v_line = Line(
            h_line.get_end(), self.plane.coords_to_point(x, y),
            color = RED
        )
        lines = VGroup(h_line, v_line)

        dots = self.lattice_points.copy()
        random.shuffle(dots.submobjects)

        self.play(*[
            ApplyMethod(
                dot.set_fill, None, 0,
                run_time = 3,
                rate_func = squish_rate_func(
                    lambda t : 1 - there_and_back(t),
                    a, a + 0.5
                ),
                remover = True
            )
            for dot, a in zip(dots, np.linspace(0, 0.5, len(dots)))
        ])
        self.play(
            Write(label),
            ShowCreation(lines),
            DrawBorderThenFill(example_dot),
            run_time = 2,
        )
        self.dither(2)
        self.play(*map(FadeOut, [label, lines, example_dot]))

    def draw_lattice_points_in_circle(self):
        circle = self.get_circle()
        radius = Line(ORIGIN, circle.get_right())
        radius.highlight(RED)
        brace = Brace(radius, DOWN, buff = SMALL_BUFF)
        radius_label = brace.get_text(
            str(self.max_lattice_point_radius),
            buff = SMALL_BUFF
        )
        radius_label.add_background_rectangle()
        brace.add(radius_label)

        self.play(
            ShowCreation(circle),
            Rotating(radius, about_point = ORIGIN),
            run_time = 2,
            rate_func = smooth,
        )
        self.play(FadeIn(brace))
        self.add_foreground_mobject(brace)
        self.draw_lattice_points()
        self.dither()
        self.play(*map(FadeOut, [brace, radius]))

        self.circle = circle

    def turn_points_int_units_of_area(self):
        square = Square(fill_opacity = 0.9)
        unit_line = Line(
            self.plane.coords_to_point(0, 0),
            self.plane.coords_to_point(1, 0),
        )
        square.scale_to_fit_width(unit_line.get_width())
        squares = VGroup(*[
            square.copy().move_to(point)
            for point in self.lattice_points
        ])
        squares.gradient_highlight(BLUE_E, GREEN_E)
        squares.set_stroke(WHITE, 1)
        point_copies = self.lattice_points.copy()

        self.play(
            ReplacementTransform(
                point_copies, squares,
                run_time = 3,
                submobject_mode = "lagged_start",
                lag_factor = 4,
            ),
            Animation(self.lattice_points)
        )
        self.dither()
        self.play(FadeOut(squares), Animation(self.lattice_points))

    def write_pi_R_squared(self):
        equations = VGroup(*[
            VGroup(
                TextMobject(
                    "\\# Lattice points\\\\",
                    "within radius ", R,
                    alignment = ""
                ),
                TexMobject(
                    "\\approx \\pi", "(", R, ")^2"
                )
            ).arrange_submobjects(RIGHT)
            for R in "10", "1{,}000{,}000", "R"
        ])
        radius_10_eq, radius_million_eq, radius_R_eq = equations
        for eq in equations:
            for tex_mob in eq:
                tex_mob.highlight_by_tex("0", BLUE)
        radius_10_eq.to_corner(UP+LEFT)
        radius_million_eq.next_to(radius_10_eq, DOWN, LARGE_BUFF)
        radius_million_eq.to_edge(LEFT)
        brace = Brace(radius_million_eq, DOWN)
        brace.add(brace.get_text("More accurate"))
        brace.highlight(YELLOW)

        background = FullScreenFadeRectangle(opacity = 0.9)

        self.play(
            FadeIn(background),
            Write(radius_10_eq)
        )
        self.dither(2)
        self.play(ReplacementTransform(
            radius_10_eq.copy(),
            radius_million_eq
        ))
        self.play(FadeIn(brace))
        self.dither(3)

        self.radius_10_eq = radius_10_eq
        self.million_group = VGroup(radius_million_eq, brace)
        self.radius_R_eq = radius_R_eq

    def allude_to_alternate_counting_method(self):
        alt_count = TextMobject(
            "(...something else...)", "$R^2$", "=",
            arg_separator = ""
        )
        alt_count.to_corner(UP+LEFT)
        alt_count.highlight_by_tex("something", MAROON_B)
        self.radius_R_eq.next_to(alt_count, RIGHT)

        final_group = VGroup(
            alt_count.get_part_by_tex("something"),
            self.radius_R_eq[1].get_part_by_tex("pi"),
        ).copy()

        self.play(
            FadeOut(self.million_group),
            Write(alt_count),
            ReplacementTransform(
                self.radius_10_eq,
                self.radius_R_eq
            )
        )
        self.dither(2)
        self.play(
            final_group.arrange_submobjects, RIGHT,
            final_group.next_to, ORIGIN, UP
        )
        rect = BackgroundRectangle(final_group)
        self.play(FadeIn(rect), Animation(final_group))
        self.dither(2)

class SoYouPlay(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "So you play!",
            run_time = 2
        )
        self.change_student_modes("happy", "thinking", "hesitant")
        self.dither()
        self.look_at(Dot().to_corner(UP+LEFT))
        self.dither(3)

class CountThroughRings(LatticePointScene):
    CONFIG = {
        "example_point_coords" : (3, 2),
        "num_rings_to_show_explicitly" : 6,
        "x_radius" : 15,
        "plane_center" : 2*RIGHT,
        "max_lattice_point_radius" : 5,
    }
    def construct(self):
        self.force_skipping()

        self.add_lattice_points()
        self.preview_rings()
        self.show_specific_lattice_point_distance()
        self.count_through_rings()

    def add_lattice_points(self):
        big_circle = self.get_circle()
        self.add(big_circle)
        self.add(self.lattice_points)
        self.big_circle = big_circle

    def preview_rings(self):
        radii = list(set([
            np.sqrt(p.r_squared) for p in self.lattice_points
        ]))
        radii.sort()
        circles = VGroup(*[
            self.get_circle(radius = r)
            for r in radii
        ])
        circles.set_stroke(width = 2)
    
        self.revert_to_original_skipping_status()        
        self.add_foreground_mobject(self.lattice_points)
        self.play(FadeIn(circles))
        self.play(LaggedStart(
            ApplyMethod,
            circles,
            arg_creator = lambda m : (m.set_stroke, PINK, 4),
            rate_func = there_and_back,
        ))
        self.dither()

        self.remove_foreground_mobject(self.lattice_points)



    def show_specific_lattice_point_distance(self):
        pass

    def count_through_rings(self):
        pass






























