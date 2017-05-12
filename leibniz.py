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
        "radial_line_color" : RED,
    }
    def setup(self):
        if self.x_radius is None:
            self.x_radius = self.y_radius*SPACE_WIDTH/SPACE_HEIGHT
        plane = ComplexPlane(
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
        self.lattice_points.sort_submobjects(
            lambda p : np.linalg.norm(p - self.plane_center)
        )

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

    def get_radial_line_with_label(self, radius = None, color = None):
        if radius is None:
            radius = self.max_lattice_point_radius
        if color is None:
            color = self.radial_line_color
        radial_line = Line(
            self.plane_center,
            self.plane.coords_to_point(radius, 0),
            color = color
        )
        r_squared = int(np.round(radius**2))
        root_label = TexMobject("\\sqrt{%d}"%r_squared)
        root_label.add_background_rectangle()
        root_label.next_to(radial_line, UP, SMALL_BUFF)

        return radial_line, root_label

    def get_lattice_points_on_r_squared_circle(self, r_squared):
        points = VGroup(*filter(
            lambda dot : dot.r_squared == r_squared,
            self.lattice_points
        ))
        points.sort_submobjects(
            lambda p : angle_of_vector(p-self.plane_center)%(2*np.pi)
        )
        return points

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

    def add_axis_labels(self, spacing = 2):
        x_max = int(self.plane.point_to_coords(SPACE_WIDTH*RIGHT)[0])
        y_max = int(self.plane.point_to_coords(SPACE_HEIGHT*UP)[1])
        x_range = range(spacing, x_max, spacing)
        y_range = range(spacing, y_max, spacing)
        for r in x_range, y_range:
            r += [-n for n in r]
        tick = Line(ORIGIN, MED_SMALL_BUFF*UP)
        x_ticks = VGroup(*[
            tick.copy().move_to(self.plane.coords_to_point(x, 0))
            for x in x_range
        ])
        tick.rotate(-np.pi/2)
        y_ticks = VGroup(*[
            tick.copy().move_to(self.plane.coords_to_point(0, y))
            for y in y_range
        ])
        x_labels = VGroup(*[
            TexMobject(str(x))
            for x in x_range
        ])
        y_labels = VGroup(*[
            TexMobject(str(y) + "i")
            for y in y_range
        ])

        for labels, ticks in (x_labels, x_ticks), (y_labels, y_ticks):
            labels.scale(0.6)
            for tex_mob, tick in zip(labels, ticks):
                tex_mob.add_background_rectangle()
                tex_mob.next_to(
                    tick,
                    tick.get_start() - tick.get_end(),
                    SMALL_BUFF
                )
        self.add(x_ticks, y_ticks, x_labels, y_labels)
        digest_locals(self, [
            "x_ticks", "y_ticks",
            "x_labels", "y_labels",
        ])

    def point_to_int_coords(self, point):
        x, y = self.plane.point_to_coords(point)[:2]
        return (int(np.round(x)), int(np.round(y)))

    def dot_to_int_coords(self, dot):
        return self.point_to_int_coords(dot.get_center())


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
        # line.shift(UP)
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
            "1", "-\\frac{1}{3}", 
            "+\\frac{1}{5}", "-\\frac{1}{7}",
            "+\\frac{1}{9}", "-\\frac{1}{11}",
            "+\\cdots"
        )
        sum_mob.to_corner(UP+RIGHT)
        lhs = TexMobject(
            "\\frac{\\pi}{4}", "=", 
        )
        lhs.next_to(sum_mob, LEFT)
        lhs.highlight_by_tex("pi", YELLOW)
        sum_arrow = Arrow(
            lhs.get_part_by_tex("pi").get_bottom(),
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
                FadeIn(lhs),
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
        self.play(ShowCreation(sum_arrow))
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

class CertainRegularityInPrimes(LatticePointScene):
    CONFIG = {
        "y_radius" : 8,
        "x_radius" : 20,
        "max_lattice_point_radius" : 8,
        "plane_center" : 2.5*RIGHT,
        "primes" : [5, 13, 17, 29, 37, 41, 53],
        "include_pi_formula" : True,
    }
    def construct(self):
        if self.include_pi_formula:
            self.add_pi_formula()
        self.walk_through_primes()

    def add_pi_formula(self):
        formula = TexMobject(
            "\\frac{\\pi}{4}", "=",
            "1", "-", "\\frac{1}{3}",
            "+", "\\frac{1}{5}", "-", "\\frac{1}{7}",
            "+\\cdots"
        )
        formula.highlight_by_tex("pi", YELLOW)
        formula.add_background_rectangle()
        formula.to_corner(UP+LEFT, buff = MED_SMALL_BUFF)
        self.add_foreground_mobject(formula)

    def walk_through_primes(self):
        primes = self.primes
        lines_and_labels = [
            self.get_radial_line_with_label(np.sqrt(p))
            for p in primes
        ]
        lines, labels = zip(*lines_and_labels)
        circles = [
            self.get_circle(np.sqrt(p))
            for p in primes
        ]
        dots_list = [
            self.get_lattice_points_on_r_squared_circle(p)
            for p in primes
        ]
        groups = [
            VGroup(*mobs)
            for mobs in zip(lines, labels, circles, dots_list)
        ]

        curr_group = groups[0]
        self.play(Write(curr_group, run_time = 2))
        self.dither()
        for group in groups[1:]:
            self.play(Transform(curr_group, group))
            self.dither(2)

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
        "example_coords" : (3, 2),
        "num_rings_to_show_explicitly" : 7,
        "x_radius" : 15,

        "plane_center" : 2*RIGHT,
        "max_lattice_point_radius" : 5,
    }
    def construct(self):
        self.add_lattice_points()
        self.preview_rings()
        self.isolate_single_ring()
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

        digest_locals(self, ["circles", "radii"])

    def isolate_single_ring(self):
        x, y = self.example_coords
        example_circle = self.circles[
            self.radii.index(np.sqrt(x**2 + y**2))
        ]
        self.circles.remove(example_circle)
        points_on_example_circle = self.get_lattice_points_on_r_squared_circle(
            x**2 + y**2
        ).copy()

        self.play(
            FadeOut(self.circles),
            self.lattice_points.set_fill, GREY, 0.5,
            Animation(points_on_example_circle)
        )
        self.dither()

        digest_locals(self, ["points_on_example_circle", "example_circle"])

    def show_specific_lattice_point_distance(self):
        x, y = self.example_coords
        dot = Dot(
            self.plane.coords_to_point(x, y),
            color = self.dot_color,
            radius = self.dot_radius
        )
        label = TexMobject("(a, b)")
        num_label = TexMobject(str(self.example_coords))
        for mob in label, num_label:
            mob.add_background_rectangle()
            mob.next_to(dot, UP + RIGHT, SMALL_BUFF)
        a, b = label[1][1].copy(), label[1][3].copy()

        x_spot = self.plane.coords_to_point(x, 0)
        radial_line = Line(self.plane_center, dot)
        h_line = Line(self.plane_center, x_spot)
        h_line.highlight(GREEN)
        v_line = Line(x_spot, dot)
        v_line.highlight(RED)

        distance = TexMobject("\\sqrt{a^2 + b^2}")
        distance_num = TexMobject("\\sqrt{%d}"%(x**2 + y**2))
        for mob in distance, distance_num:
            mob.scale(0.75)
            mob.add_background_rectangle()
            mob.next_to(radial_line.get_center(), UP, SMALL_BUFF)
            mob.rotate(
                radial_line.get_angle(),
                about_point = mob.get_bottom()
            )

        self.play(Write(label))
        self.play(
            ApplyMethod(a.next_to, h_line, DOWN, SMALL_BUFF),
            ApplyMethod(b.next_to, v_line, RIGHT, SMALL_BUFF),
            ShowCreation(h_line),
            ShowCreation(v_line),
        )
        self.play(ShowCreation(radial_line))
        self.play(Write(distance))
        self.dither(2)

        a_num, b_num = [
            TexMobject(str(coord))[0]
            for coord in self.example_coords
        ]
        a_num.move_to(a, UP)
        b_num.move_to(b, LEFT)
        self.play(
            Transform(label, num_label),
            Transform(a, a_num),
            Transform(b, b_num),
        )
        self.dither()
        self.play(Transform(distance, distance_num))
        self.dither(3)
        self.play(*map(FadeOut, [
            self.example_circle, self.points_on_example_circle,
            distance, a, b,
            radial_line, h_line, v_line,
            label
        ]))

    def count_through_rings(self):
        counts = [
            len(self.get_lattice_points_on_r_squared_circle(N))
            for N in range(self.max_lattice_point_radius**2 + 1)
        ]
        left_list = VGroup(*[
            TexMobject(
                "\\sqrt{%d} \\Rightarrow"%n, str(count)
            )
            for n, count in zip(
                range(self.num_rings_to_show_explicitly),
                counts
            )
        ])
        left_counts = VGroup()
        left_roots = VGroup()
        for mob in left_list:
            mob[1].highlight(YELLOW)
            left_counts.add(VGroup(mob[1]))
            mob.add_background_rectangle()
            left_roots.add(VGroup(mob[0], mob[1][0]))

        left_list.arrange_submobjects(
            DOWN,
            buff = MED_LARGE_BUFF,
            aligned_edge = LEFT,
        )
        left_list.to_corner(UP + LEFT)

        top_list = VGroup(*[
            TexMobject("%d, "%count)
            for count in counts
        ])
        top_list.highlight(YELLOW)
        top_list.arrange_submobjects(RIGHT, aligned_edge = DOWN)
        top_list.scale_to_fit_width(2*SPACE_WIDTH - MED_LARGE_BUFF)
        top_list.to_edge(UP, buff = SMALL_BUFF)
        top_rect = BackgroundRectangle(top_list)

        for r_squared, count_mob, root in zip(it.count(), left_counts, left_roots):
            self.show_ring_count(
                r_squared,
                count_mob,
                added_anims = [FadeIn(root)]
            )
            self.dither(2)
        self.play(
            FadeOut(left_roots),
            FadeIn(top_rect),
            *[
                ReplacementTransform(
                    lc, VGroup(tc),
                    path_arc = np.pi/2
                )
                for lc, tc in zip(left_counts, top_list)
            ]
        )
        for r_squared in range(len(left_counts), self.max_lattice_point_radius**2 + 1):
            self.show_ring_count(
                r_squared, top_list[r_squared],
            )
        self.dither(3)


    def show_ring_count(
        self, radius_squared, target,
        added_anims = None,        
        run_time = 1
        ):
        added_anims = added_anims or []
        radius = np.sqrt(radius_squared)
        points = self.get_lattice_points_on_r_squared_circle(radius_squared)
        points.save_state()
        circle = self.get_circle(radius)
        radial_line = Line(
            self.plane_center, self.plane.coords_to_point(radius, 0),
            color = RED
        )
        root = TexMobject("\\sqrt{%d}"%radius_squared)
        root.add_background_rectangle()
        root.scale_to_fit_width(
            min(0.7*radial_line.get_width(), root.get_width())
        )
        root.next_to(radial_line, DOWN, SMALL_BUFF)
        if not hasattr(self, "little_circle"):
            self.little_circle = circle
        if not hasattr(self, "radial_line"):
            self.radial_line = radial_line
        if not hasattr(self, "root"):
            self.root = root
        if hasattr(self, "last_points"):
            added_anims += [self.last_points.restore]
        self.last_points = points

        if radius_squared == 0:
            points.set_fill(YELLOW, 1)
            self.play(
                DrawBorderThenFill(points, stroke_color = PINK),
                *added_anims,
                run_time = run_time
            )
            self.play(ReplacementTransform(
                points.copy(), target
            ))
            return
        points.set_fill(YELLOW, 1)
        self.play(
            Transform(self.little_circle, circle),
            Transform(self.radial_line, radial_line),
            Transform(self.root, root),
            DrawBorderThenFill(
                points, 
                stroke_width = 4,
                stroke_color = PINK,
            ),
            *added_anims,
            run_time = run_time
        )
        self.dither(run_time)
        if len(points) > 0:
            mover = points.copy()  
        else:
            mover = VectorizedPoint(self.plane_center)
        self.play(ReplacementTransform(mover, target, run_time = run_time))

class LookAtExampleRing(LatticePointScene):
    CONFIG = {
        "dot_radius" : 0.1,
        "plane_center" : 2*LEFT,
        "x_radius" : 17,
        "y_radius" : 7,
    }
    def construct(self):
        self.analyze_25()
        self.analyze_11()

    def analyze_25(self):
        x_color = GREEN
        y_color = RED
        circle = self.get_circle(radius = 5)
        points = self.get_lattice_points_on_r_squared_circle(25)
        radius, root_label = self.get_radial_line_with_label(5)
        coords_list = [(5, 0), (4, 3), (3, 4), (0, 5), (-3, 4), (-4, 3)]
        labels = [
            TexMobject("(", str(x), ",", str(y), ")")
            for x, y in coords_list
        ]
        for label in labels:
            label.x = label[1]
            label.y = label[3]
            label.x.highlight(x_color)
            label.y.highlight(y_color)
            label.add_background_rectangle()

        for label, point in zip(labels, points):
            x_coord = (point.get_center() - self.plane_center)[0]
            vect = UP+RIGHT if x_coord >= 0 else UP+LEFT
            label.next_to(point, vect, SMALL_BUFF)
            label.point = point

        def special_str(n):
            return "(%d)"%n if n < 0 else str(n)

        sums_of_squares = [
            TexMobject(
                special_str(x), "^2", "+", 
                special_str(y), "^2", "= 25"
            )
            for x, y in coords_list
        ]
        for tex_mob in sums_of_squares:
            tex_mob.x = tex_mob[0]
            tex_mob.y = tex_mob[3]
            tex_mob.x.highlight(x_color)
            tex_mob.y.highlight(y_color)
            tex_mob.add_background_rectangle()
            tex_mob.to_corner(UP+RIGHT)

        self.play(
            ShowCreation(radius),
            Write(root_label)
        )
        self.play(
            ShowCreation(circle),
            Rotating(
                radius, 
                about_point = self.plane_center,
                rate_func = smooth, 
            ),
            FadeIn(points, submobject_mode = "lagged_start"),
            run_time = 2,
        )
        self.dither()

        curr_label = labels[0]
        curr_sum_of_squares = sums_of_squares[0]
        self.play(
            Write(curr_label),
            curr_label.point.highlight, PINK
        )
        x, y = curr_label.x.copy(), curr_label.y.copy()
        self.play(
            Transform(x, curr_sum_of_squares.x),
            Transform(y, curr_sum_of_squares.y),
        )
        self.play(
            Write(curr_sum_of_squares),
            Animation(VGroup(x, y))
        )
        self.remove(x, y)
        self.dither()

        for label, sum_of_squares in zip(labels, sums_of_squares)[1:]:
            self.play(
                ReplacementTransform(curr_label, label),
                label.point.highlight, PINK,
                curr_label.point.highlight, self.dot_color
            )
            curr_label = label
            self.play(
                ReplacementTransform(
                    curr_sum_of_squares, sum_of_squares
                )
            )
            curr_sum_of_squares = sum_of_squares
            self.dither()

        points.save_state()
        points.generate_target()
        for i, point in enumerate(points.target):
            point.move_to(
                self.plane.coords_to_point(i%3, i//3)
            )
        points.target.next_to(circle, RIGHT)

        self.play(MoveToTarget(
            points, 
            run_time = 2,
        ))
        self.dither()
        self.play(points.restore, run_time = 2)
        self.dither()
        self.play(*map(FadeOut, [
            curr_label, curr_sum_of_squares, 
            circle, points,
            radius, root_label
        ]))

    def analyze_11(self):
        R = np.sqrt(11)
        circle = self.get_circle(radius = R)
        radius, root_label = self.get_radial_line_with_label(R)
        equation = TexMobject("11 \\ne ", "a", "^2", "+", "b", "^2")
        equation.highlight_by_tex("a", GREEN)
        equation.highlight_by_tex("b", RED)
        equation.add_background_rectangle()
        equation.to_corner(UP+RIGHT)

        self.play(
            Write(root_label),
            ShowCreation(radius),
            run_time = 1
        )
        self.play(
            ShowCreation(circle),
            Rotating(
                radius, 
                about_point = self.plane_center,
                rate_func = smooth, 
            ),
            run_time = 2,
        )
        self.dither()
        self.play(Write(equation))
        self.dither(3)

class Given2DThinkComplex(TeacherStudentsScene):
    def construct(self):
        tex = TextMobject("2D $\\Leftrightarrow$ Complex numbers")
        plane = ComplexPlane(
            x_radius = 0.6*SPACE_WIDTH,
            y_radius = 0.6*SPACE_HEIGHT,
        )
        plane.add_coordinates()
        plane.scale_to_fit_height(SPACE_HEIGHT)
        plane.to_corner(UP+LEFT)

        self.teacher_says(tex)
        self.change_student_modes("pondering", "confused", "erm")
        self.dither()
        self.play(
            Write(plane),
            RemovePiCreatureBubble(
                self.teacher,
                target_mode = "raise_right_hand"
            )
        )
        self.change_student_modes(
            *["thinking"]*3,
            look_at_arg = plane
        )
        self.dither(3)

class IntroduceComplexConjugate(LatticePointScene):
    CONFIG = {
        "y_radius" : 20,
        "x_radius" : 30,
        "plane_scale_factor" : 1.7,
        "plane_center" : 2*LEFT,
        "example_coords" : (3, 4),
        "x_color" : GREEN,
        "y_color" : RED,
    }
    def construct(self):
        self.resize_plane()
        self.write_points_with_complex_coords()
        self.introduce_complex_conjugate()
        self.show_confusion()
        self.expand_algebraically()
        self.show_geometrically()

    def resize_plane(self):
        self.plane.scale(
            self.plane_scale_factor,
            about_point = self.plane_center
        )
        self.plane.set_stroke(width = 3)

    def write_points_with_complex_coords(self):
        x, y = self.example_coords
        x_color = self.x_color
        y_color = self.y_color

        point = self.plane.coords_to_point(x, y)
        dot = Dot(point, color = self.dot_color)
        x_point = self.plane.coords_to_point(x, 0)
        h_arrow = Arrow(self.plane_center, x_point, buff = 0)
        v_arrow = Arrow(x_point, point, buff = 0)
        h_arrow.highlight(x_color)
        v_arrow.highlight(y_color)
        x_coord = TexMobject(str(x))
        x_coord.next_to(h_arrow, DOWN, SMALL_BUFF)
        x_coord.highlight(x_color)
        x_coord.add_background_rectangle()
        y_coord = TexMobject(str(y))
        imag_y_coord = TexMobject(str(y) + "i")
        for coord in y_coord, imag_y_coord:
            coord.next_to(v_arrow, RIGHT, SMALL_BUFF)
            coord.highlight(y_color)
            coord.add_background_rectangle()

        tuple_label = TexMobject(str((x, y)))
        tuple_label[1].highlight(x_color)
        tuple_label[3].highlight(y_color)
        complex_label = TexMobject("%d+%di"%(x, y))
        complex_label[0].highlight(x_color)
        complex_label[2].highlight(y_color)
        for label in tuple_label, complex_label:
            label.add_background_rectangle()
            label.next_to(dot, UP+RIGHT, buff = 0)

        y_range = range(-9, 10, 3)
        ticks = VGroup(*[
            Line(
                ORIGIN, MED_SMALL_BUFF*RIGHT
            ).move_to(self.plane.coords_to_point(0, y))
            for y in y_range
        ])
        imag_coords = VGroup()
        for y, tick in zip(y_range, ticks):
            if y == 0:
                continue
            if y == 1:
                tex = "i"
            elif y == -1:
                tex = "-i"
            else:
                tex = "%di"%y
            imag_coord = TexMobject(tex)
            imag_coord.scale(0.75)
            imag_coord.add_background_rectangle()
            imag_coord.next_to(tick, LEFT, SMALL_BUFF)
            imag_coords.add(imag_coord)

        self.add(dot)
        self.play(
            ShowCreation(h_arrow),
            Write(x_coord)
        )
        self.play(
            ShowCreation(v_arrow),
            Write(y_coord)
        )
        self.play(FadeIn(tuple_label))
        self.dither()
        self.play(*map(FadeOut, [tuple_label, y_coord]))
        self.play(*map(FadeIn, [complex_label, imag_y_coord]))
        self.play(*map(Write, [imag_coords, ticks]))
        self.dither()
        self.play(*map(FadeOut, [
            v_arrow, h_arrow, 
            x_coord, imag_y_coord,
        ]))

        self.complex_label = complex_label
        self.example_dot = dot

    def introduce_complex_conjugate(self):
        x, y = self.example_coords
        equation = VGroup(
            TexMobject("25 = ", str(x), "^2", "+", str(y), "^2", "="),
            TexMobject("(", str(x), "+", str(y), "i", ")"),
            TexMobject("(", str(x), "-", str(y), "i", ")"),
        )
        equation.arrange_submobjects(
            RIGHT, buff = SMALL_BUFF,
        )
        VGroup(*equation[-2:]).shift(0.5*SMALL_BUFF*DOWN)
        equation.scale(0.9)
        equation.to_corner(UP+RIGHT, buff = MED_SMALL_BUFF)
        for tex_mob in equation:
            tex_mob.highlight_by_tex(str(x), self.x_color)
            tex_mob.highlight_by_tex(str(y), self.y_color)
            tex_mob.add_background_rectangle()

        dot = Dot(
            self.plane.coords_to_point(x, -y),
            color = self.dot_color
        )
        label = TexMobject("%d-%di"%(x, y))
        label[0].highlight(self.x_color)
        label[2].highlight(self.y_color)
        label.add_background_rectangle()
        label.next_to(dot, DOWN+RIGHT, buff = 0)

        brace = Brace(equation[-1], DOWN)
        conjugate_words = TextMobject("Complex \\\\ conjugate")
        conjugate_words.scale(0.8)
        conjugate_words.add_background_rectangle()
        conjugate_words.next_to(brace, DOWN)

        self.play(FadeIn(
            equation,
            run_time = 3,
            submobject_mode = "lagged_start"
        ))
        self.dither(2)
        self.play(
            GrowFromCenter(brace),
            Write(conjugate_words, run_time = 2)
        )
        self.dither()
        self.play(*[
            ReplacementTransform(m1.copy(), m2)
            for m1, m2 in [
                (self.example_dot, dot),
                (self.complex_label, label),
            ]
        ])
        self.dither(2)

        self.conjugate_label = VGroup(brace, conjugate_words)
        self.equation = equation
        self.conjugate_dot = dot

    def show_confusion(self):
        randy = Randolph(color = BLUE_C).to_corner(DOWN+LEFT)
        morty = Mortimer().to_edge(DOWN)
        randy.make_eye_contact(morty)

        self.play(*map(FadeIn, [randy, morty]))
        self.play(PiCreatureSays(
            randy, "Wait \\dots why?",
            target_mode = "confused",
        ))
        self.play(Blink(randy))
        self.dither(2)
        self.play(
            RemovePiCreatureBubble(
                randy, target_mode = "erm",
            ),
            PiCreatureSays(
                morty, "Now it's a \\\\ factoring problem!",
                target_mode = "hooray",
                bubble_kwargs = {"width" : 5, "height" : 3}
            )
        )
        self.play(
            morty.look_at, self.equation,
            randy.look_at, self.equation,
        )
        self.play(Blink(morty))
        self.play(randy.change_mode, "pondering")
        self.play(RemovePiCreatureBubble(morty))
        self.play(*map(FadeOut, [randy, morty]))

    def expand_algebraically(self):
        x, y = self.example_coords
        expansion = VGroup(
            TexMobject(str(x), "^2"),
            TexMobject("-", "(", str(y), "i", ")^2")
        )
        expansion.arrange_submobjects(RIGHT, buff = SMALL_BUFF)
        expansion.next_to(
            VGroup(*self.equation[-2:]), 
            DOWN, LARGE_BUFF
        )
        alt_y_term = TexMobject("+", str(y), "^2")
        alt_y_term.move_to(expansion[1], LEFT)
        for tex_mob in list(expansion) + [alt_y_term]:
            tex_mob.highlight_by_tex(str(x), self.x_color)
            tex_mob.highlight_by_tex(str(y), self.y_color)
            tex_mob.rect = BackgroundRectangle(tex_mob)

        x1 = self.equation[-2][1][1]
        x2 = self.equation[-1][1][1]
        y1 = VGroup(*self.equation[-2][1][3:5])
        y2 = VGroup(*self.equation[-1][1][2:5])
        vect = MED_LARGE_BUFF*UP

        self.play(FadeOut(self.conjugate_label))
        group = VGroup(x1, x2)
        self.play(group.shift, -vect)
        self.play(
            FadeIn(expansion[0].rect),
            ReplacementTransform(group.copy(), expansion[0]),
        )
        self.play(group.shift, vect)
        group = VGroup(x1, y2)
        self.play(group.shift, -vect)
        self.dither()
        self.play(group.shift, vect)
        group = VGroup(x2, y1)
        self.play(group.shift, -vect)
        self.dither()
        self.play(group.shift, vect)
        group = VGroup(*it.chain(y1, y2))
        self.play(group.shift, -vect)
        self.dither()
        self.play(
            FadeIn(expansion[1].rect),
            ReplacementTransform(group.copy(), expansion[1]),
        )
        self.play(group.shift, vect)
        self.dither(2)
        self.play(
            Transform(expansion[1].rect, alt_y_term.rect),
            Transform(expansion[1], alt_y_term),
        )
        self.dither()
        self.play(*map(FadeOut, [
            expansion[0].rect,
            expansion[1].rect,
            expansion
        ]))

    def show_geometrically(self):
        dots = [self.example_dot, self.conjugate_dot]
        top_dot, low_dot = dots
        for dot in dots:
            dot.line = Line(
                self.plane_center, dot.get_center(), 
                color = BLUE
            )
            dot.angle = dot.line.get_angle()
            dot.arc = Arc(
                dot.angle,
                radius = 0.75, 
                color = YELLOW
            )
            dot.arc.shift(self.plane_center)
            dot.arc.add_tip(tip_length = 0.2)
            dot.rotate_word = TextMobject("Rotate")
            dot.rotate_word.scale(0.5)
            dot.rotate_word.next_to(dot.arc, RIGHT, SMALL_BUFF)
            dot.magnitude_word = TextMobject("Length 5")
            dot.magnitude_word.scale(0.6)
            dot.magnitude_word.next_to(
                ORIGIN,
                np.sign(dot.get_center()[1])*UP,
                buff = SMALL_BUFF
            )
            dot.magnitude_word.add_background_rectangle()
            dot.magnitude_word.rotate(dot.angle)
            dot.magnitude_word.shift(dot.line.get_center())
        twenty_five_label = TexMobject("25")
        twenty_five_label.add_background_rectangle()
        twenty_five_label.next_to(
            self.plane.coords_to_point(25, 0),
            DOWN
        )

        self.play(ShowCreation(top_dot.line))
        mover = VGroup(
            top_dot.line.copy().highlight(PINK), 
            top_dot.copy()
        )
        self.play(FadeIn(
            top_dot.magnitude_word,
            submobject_mode = "lagged_start"
        ))
        self.dither()
        self.play(ShowCreation(top_dot.arc))
        self.dither(2)
        self.play(ShowCreation(low_dot.line))
        self.play(
            ReplacementTransform(
                top_dot.arc,
                low_dot.arc
            ),
            FadeIn(low_dot.rotate_word)
        )
        self.play(
            Rotate(
                mover, low_dot.angle, 
                about_point = self.plane_center
            ),
            run_time = 2
        )
        self.play(
            FadeOut(low_dot.arc),
            FadeOut(low_dot.rotate_word),
            FadeIn(low_dot.magnitude_word),
        )
        self.play(
            mover[0].scale_about_point, 5, self.plane_center,
            mover[1].move_to, self.plane.coords_to_point(25, 0),
            run_time = 2
        )
        self.dither()
        self.play(Write(twenty_five_label))
        self.dither(3)

class NameGaussianIntegers(LatticePointScene):
    CONFIG = {
        "max_lattice_point_radius" : 15,
        "dot_radius" : 0.05,
        "plane_center" : 2*LEFT,
        "x_radius" : 15,
    }
    def construct(self):
        self.add_axis_labels()
        self.add_a_plus_bi()
        self.draw_lattice_points()
        self.add_name()
        self.restrict_to_one_circle()
        self.show_question_algebraically()

    def add_a_plus_bi(self):
        label = TexMobject(
            "a", "+", "b", "i"
        )
        a = label.get_part_by_tex("a")
        b = label.get_part_by_tex("b")
        a.highlight(GREEN)
        b.highlight(RED)
        label.add_background_rectangle()
        label.to_corner(UP+RIGHT)
        integers = TextMobject("Integers")
        integers.next_to(label, DOWN, LARGE_BUFF)
        integers.add_background_rectangle()
        arrows = VGroup(*[
            Arrow(integers.get_top(), mob, tip_length = 0.15)
            for mob in a, b
        ])
        self.add_foreground_mobjects(label, integers, arrows)

        self.a_plus_bi = label
        self.integers_label = VGroup(integers, arrows)

    def add_name(self):
        gauss_name = TextMobject(
            "Carl Friedrich Gauss"
        )
        gauss_name.add_background_rectangle()
        gauss_name.next_to(ORIGIN, UP, MED_LARGE_BUFF)
        gauss_name.to_edge(LEFT)

        gaussian_integers = TextMobject("``Gaussian integers'': ")
        gaussian_integers.scale(0.9)
        gaussian_integers.next_to(self.a_plus_bi, LEFT)
        gaussian_integers.add_background_rectangle()

        self.play(FadeIn(gaussian_integers))
        self.add_foreground_mobject(gaussian_integers)
        self.play(FadeIn(
            gauss_name,
            run_time = 2,
            submobject_mode = "lagged_start"
        ))
        self.dither(3)
        self.play(FadeOut(gauss_name))

        self.gaussian_integers = gaussian_integers

    def restrict_to_one_circle(self):
        dots = self.get_lattice_points_on_r_squared_circle(25).copy()
        for dot in dots:
            dot.scale_in_place(2)
        circle = self.get_circle(5)
        radius, root_label = self.get_radial_line_with_label(5)

        self.play(
            FadeOut(self.lattice_points),
            ShowCreation(circle),
            Rotating(
                radius, 
                run_time = 1, rate_func = smooth,
                about_point = self.plane_center
            ),
            *map(GrowFromCenter, dots)
        )
        self.play(Write(root_label))
        self.dither()

        self.circle_dots = dots

    def show_question_algebraically(self):
        for i, dot in enumerate(self.circle_dots):
            x, y = self.dot_to_int_coords(dot)
            x_str = str(x)
            y_str = str(y) if y >= 0 else "(%d)"%y
            label = TexMobject(x_str, "+", y_str, "i")
            label.scale(0.8)
            label.next_to(
                dot, 
                dot.get_center()-self.plane_center + SMALL_BUFF*(UP+RIGHT),
                buff = 0,
            )
            label.add_background_rectangle()
            dot.label = label

            equation = TexMobject(
                "25 = "
                "(", x_str, "+", y_str, "i", ")",
                "(", x_str, "-", y_str, "i", ")",
            )
            equation.scale(0.9)
            equation.add_background_rectangle()
            equation.to_corner(UP + RIGHT)
            dot.equation = equation

            for mob in label, equation:
                mob.highlight_by_tex(x_str, GREEN, substring = False)
                mob.highlight_by_tex(y_str, RED, substring = False)

            dot.line_pair = VGroup(*[
                Line(
                    self.plane_center,
                    self.plane.coords_to_point(x, u*y),
                    color = PINK,
                )
                for u in 1, -1
            ])
            dot.conjugate_dot = self.circle_dots[-i]

        self.play(*map(FadeOut, [
            self.a_plus_bi, self.integers_label,
            self.gaussian_integers,
        ]))

        last_dot = None
        for dot in self.circle_dots:
            anims = [
                dot.highlight, PINK,
                dot.conjugate_dot.highlight, PINK,
            ]
            if last_dot is None:
                anims += [
                    FadeIn(dot.equation),
                    FadeIn(dot.label),
                ]
                anims += map(ShowCreation, dot.line_pair)
            else:
                anims += [
                    last_dot.highlight, self.dot_color,
                    last_dot.conjugate_dot.highlight, self.dot_color,
                    ReplacementTransform(last_dot.equation, dot.equation),
                    ReplacementTransform(last_dot.label, dot.label),
                    ReplacementTransform(last_dot.line_pair, dot.line_pair),
                ]
            self.play(*anims)
            self.dither()
            last_dot = dot

class FactorOrdinaryNumber(TeacherStudentsScene):
    def construct(self):
        equation = TexMobject(
            "2{,}250", "=", "2 \\cdot 3^2 \\cdot 5^3"
        )
        equation.next_to(self.get_pi_creatures(), UP, LARGE_BUFF)
        number = equation[0]
        alt_rhs_list = list(it.starmap(TexMobject, [
            ("\\ne", "2^2 \\cdot 563"),
            ("\\ne", "2^2 \\cdot 3 \\cdot 11 \\cdot 17"),
            ("\\ne", "2 \\cdot 7^2 \\cdot 23"),
            ("=", "(-2) \\cdot (-3) \\cdot (3) \\cdot 5^3"),
        ]))
        for alt_rhs in alt_rhs_list:
            if "\\ne" in alt_rhs.get_tex_string():
                alt_rhs.highlight(RED)
            else:
                alt_rhs.highlight(GREEN)
            alt_rhs.move_to(equation.get_right())
        number.save_state()
        number.next_to(self.teacher, UP+LEFT)

        self.play(
            self.teacher.change_mode, "raise_right_hand",
            Write(number)
        )
        self.dither(2)
        self.play(
            number.restore,
            Write(VGroup(*equation[1:]))
        )
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = equation,
            added_anims = [self.teacher.change_mode, "happy"]
        )
        self.dither()
        last_alt_rhs = None
        for alt_rhs in alt_rhs_list:
            equation.generate_target()
            equation.target.next_to(alt_rhs, LEFT)
            anims = [MoveToTarget(equation)]
            if last_alt_rhs:
                anims += [ReplacementTransform(last_alt_rhs, alt_rhs)]
            else:
                anims += [FadeIn(alt_rhs)]
            self.play(*anims)
            if alt_rhs is alt_rhs_list[-1]:
                self.change_student_modes(
                    *["sassy"]*3,
                    look_at_arg = alt_rhs
                )
            self.dither(2)
            last_alt_rhs = alt_rhs

        self.play(
            FadeOut(VGroup(equation, alt_rhs)),
            PiCreatureSays(
                self.teacher,
                "It's similar for \\\\ Gaussian integers"
            )
        )
        self.change_student_modes(*["happy"]*3)
        self.dither(3)

class IntroduceGaussianPrimes(LatticePointScene):
    CONFIG = {
        "plane_center" : LEFT,
        "x_radius" : 13,
    }
    def construct(self):
        five_dot, p1_dot, p2_dot, p3_dot, p4_dot = dots = [
            Dot(self.plane.coords_to_point(*coords))
            for coords in [
                (5, 0), 
                (2, 1), (2, -1), 
                (-1, 2), (-1, -2),
            ]
        ]
        five_dot.highlight(YELLOW)
        p_dots = VGroup(*dots[1:])
        p_dots.highlight(PINK)

        five_label, p1_label, p2_label, p3_label, p4_label = labels = [
            TexMobject(tex).add_background_rectangle()
            for tex in "5", "2+i", "2-i", "-1+2i", "-1-2i",
        ]
        vects = [DOWN, UP+RIGHT, DOWN+RIGHT, UP+LEFT, DOWN+LEFT]
        for dot, label, vect in zip(dots, labels, vects):
            label.next_to(dot, vect, SMALL_BUFF)

        arc_angle = 0.8*np.pi
        times_i_arc = Arrow(
            p1_dot.get_top(), p3_dot.get_top(), 
            path_arc = arc_angle
        )
        times_neg_i_arc = Arrow(
            p2_dot.get_bottom(), p4_dot.get_bottom(), 
            path_arc = -arc_angle
        )
        times_i = TexMobject("\\times i")
        times_i.add_background_rectangle()
        times_i.next_to(
            times_i_arc.point_from_proportion(0.5),
            UP
        )
        times_neg_i = TexMobject("\\times (-i)")
        times_neg_i.add_background_rectangle()
        times_neg_i.next_to(
            times_neg_i_arc.point_from_proportion(0.5),
            DOWN
        )
        VGroup(
            times_i, times_neg_i, times_i_arc, times_neg_i_arc
        ).highlight(MAROON_B)

        gaussian_prime = TextMobject("$\\Rightarrow$ ``Gaussian prime''")
        gaussian_prime.add_background_rectangle()
        gaussian_prime.scale(0.9)
        gaussian_prime.next_to(p1_label, RIGHT)

        factorization = TexMobject(
            "5", "= (2+i)(2-i)"
        )
        factorization.to_corner(UP+RIGHT)
        factorization.shift(1.5*LEFT)
        factorization.add_background_rectangle()
        alt_factorization = TexMobject("=(-1+2i)(-1-2i)")
        alt_factorization.next_to(
            factorization.get_part_by_tex("="), DOWN,
            aligned_edge = LEFT
        )
        alt_factorization.add_background_rectangle()

        for dot in dots:
            dot.add(Line(
                self.plane_center,
                dot.get_center(),
                color = dot.get_color()
            ))

        self.add(factorization)
        self.play(
            DrawBorderThenFill(five_dot), 
            FadeIn(five_label)
        )
        self.dither()
        self.play(
            ReplacementTransform(
                VGroup(five_dot).copy(),
                VGroup(p1_dot, p2_dot)
            )
        )
        self.play(*map(Write, [p1_label, p2_label]))
        self.dither()
        self.play(Write(gaussian_prime))
        self.dither(2)
        self.play(
            ShowCreation(times_i_arc),
            FadeIn(times_i),
            *[
                ReplacementTransform(
                    mob1.copy(), mob2,
                    path_arc = np.pi/2
                )
                for mob1, mob2 in [
                    (p1_dot, p3_dot),
                    (p1_label, p3_label),
                ]
            ]
        )
        self.dither()
        self.play(
            ShowCreation(times_neg_i_arc),
            FadeIn(times_neg_i),
            *[
                ReplacementTransform(
                    mob1.copy(), mob2,
                    path_arc = -np.pi/2
                )
                for mob1, mob2 in [
                    (p2_dot, p4_dot),
                    (p2_label, p4_label),
                ]
            ]
        )
        self.dither()
        self.play(Write(alt_factorization))
        self.dither(3)

class FromIntegerFactorsToGaussianFactors(TeacherStudentsScene):
    def construct(self):
        expression = TexMobject(
            "30", "=", "2", "\\cdot", "3", "\\cdot", "5"
        )
        expression.shift(2*UP)
        two = expression.get_part_by_tex("2")
        five = expression.get_part_by_tex("5")
        two.highlight(BLUE)
        five.highlight(GREEN)
        two.factors = TexMobject("(1+i)", "(1-i)")
        five.factors = TexMobject("(2+i)", "(2-i)")
        for mob, vect in (two, DOWN), (five, UP):
            mob.factors.next_to(mob, vect, LARGE_BUFF)
            mob.factors.highlight(mob.get_color())
            mob.arrows = VGroup(*[
                Arrow(
                    mob.get_edge_center(vect),
                    factor.get_edge_center(-vect),
                    color = mob.get_color(),
                    tip_length = 0.15
                )
                for factor in mob.factors
            ])

        self.add(expression)
        for mob in two, five:
            self.play(
                ReplacementTransform(
                    mob.copy(),
                    mob.factors
                ),
                *map(ShowCreation, mob.arrows)
            )
            self.dither()
        self.play(*[
            ApplyMethod(pi.change, "pondering", expression)
            for pi in self.get_pi_creatures()
        ])
        self.dither(3)

class FactorizationPattern(Scene):
    def construct(self):
        self.add_number_line()
        self.show_one_mod_four_primes()
        self.show_three_mod_four_primes()
        self.ask_why_this_is_true()
        self.show_two()

    def add_number_line(self):
        line = NumberLine(
            x_min = 0,
            x_max = 36,
            space_unit_to_num = 0.4,
            numbers_to_show = range(0, 33, 4),
            numbers_with_elongated_ticks = range(0, 33, 4),
        )
        line.shift(2*DOWN)
        line.to_edge(LEFT)
        line.add_numbers()

        self.add(line)
        self.number_line = line

    def show_one_mod_four_primes(self):
        primes = [5, 13, 17, 29]
        dots = VGroup(*[
            Dot(self.number_line.number_to_point(prime))
            for prime in primes
        ])
        dots.highlight(GREEN)
        prime_mobs = VGroup(*map(TexMobject, map(str, primes)))
        arrows = VGroup()
        for prime_mob, dot in zip(prime_mobs, dots):
            prime_mob.next_to(dot, UP, LARGE_BUFF)
            prime_mob.highlight(dot.get_color())
            arrow = Arrow(prime_mob, dot, buff = SMALL_BUFF)
            arrow.highlight(dot.get_color())
            arrows.add(arrow)

        factorizations = VGroup(*[
            TexMobject("=(%d+%si)(%d-%si)"%(x, y_str, x, y_str))
            for x, y in [(2, 1), (3, 2), (4, 1), (5, 2)]
            for y_str in [str(y) if y is not 1 else ""]
        ])
        factorizations.arrange_submobjects(DOWN, aligned_edge = LEFT)
        factorizations.to_corner(UP+LEFT)
        factorizations.shift(RIGHT)
        movers = VGroup()
        for p_mob, factorization in zip(prime_mobs, factorizations):
            mover = p_mob.copy()
            mover.generate_target()
            mover.target.next_to(factorization, LEFT)
            movers.add(mover)
        v_dots = TexMobject("\\vdots")
        v_dots.next_to(factorizations[-1][0], DOWN)
        factorization.add(v_dots)

        self.play(*it.chain(
            map(Write, prime_mobs),
            map(ShowCreation, arrows),
            map(DrawBorderThenFill, dots),
        ))
        self.dither()
        self.play(*[
            MoveToTarget(
                mover,
                run_time = 2,
                path_arc = np.pi/2,
            )
            for mover in movers
        ])
        self.play(FadeIn(
            factorizations, 
            run_time = 2,
            submobject_mode = "lagged_start"
        ))
        self.dither(4)
        self.play(*map(FadeOut, [movers, factorizations]))

    def show_three_mod_four_primes(self):
        primes = [3, 7, 11, 19, 23, 31]
        dots = VGroup(*[
            Dot(self.number_line.number_to_point(prime))
            for prime in primes
        ])
        dots.highlight(RED)
        prime_mobs = VGroup(*map(TexMobject, map(str, primes)))
        arrows = VGroup()
        for prime_mob, dot in zip(prime_mobs, dots):
            prime_mob.next_to(dot, UP, LARGE_BUFF)
            prime_mob.highlight(dot.get_color())
            arrow = Arrow(prime_mob, dot, buff = SMALL_BUFF)
            arrow.highlight(dot.get_color())
            arrows.add(arrow)

        words = TextMobject("Already Gaussian primes")
        words.to_corner(UP+LEFT)
        word_arrows = VGroup(*[
            Line(
                words.get_bottom(), p_mob.get_top(),
                color = p_mob.get_color(),
                buff = MED_SMALL_BUFF
            )
            for p_mob in prime_mobs
        ])

        self.play(*it.chain(
            map(Write, prime_mobs),
            map(ShowCreation, arrows),
            map(DrawBorderThenFill, dots),
        ))
        self.dither()
        self.play(
            Write(words),
            *map(ShowCreation, word_arrows)
        )
        self.dither(4)
        self.play(*map(FadeOut, [words, word_arrows]))

    def ask_why_this_is_true(self):
        randy = Randolph(color = BLUE_C)
        randy.scale(0.7)
        randy.to_edge(LEFT)
        randy.shift(0.8*UP)

        links_text = TextMobject("(See links in description)")
        links_text.scale(0.7)
        links_text.to_corner(UP+RIGHT)
        links_text.shift(DOWN)

        self.play(FadeIn(randy))
        self.play(PiCreatureBubbleIntroduction(
            randy, "Wait...why?",
            bubble_class = ThoughtBubble,
            bubble_kwargs = {"height" : 2, "width" : 3},
            target_mode = "confused",
            look_at_arg = self.number_line,
        ))
        self.play(Blink(randy))
        self.dither()
        self.play(FadeIn(links_text))
        self.dither(2)
        self.play(*map(FadeOut, [
            randy, randy.bubble, randy.bubble.content,
            links_text
        ]))

    def show_two(self):
        two_dot = Dot(self.number_line.number_to_point(2))
        two = TexMobject("2")
        two.next_to(two_dot, UP, LARGE_BUFF)
        arrow = Arrow(two, two_dot, buff = SMALL_BUFF)
        VGroup(two_dot, two, arrow).highlight(YELLOW)

        mover = two.copy()
        mover.generate_target()
        mover.target.to_corner(UP+LEFT)
        factorization = TexMobject("=", "(1+i)", "(1-i)")
        factorization.next_to(mover.target, RIGHT)
        factors = VGroup(*factorization[1:])

        words = TextMobject("Really the \\\\ same prime")
        words.scale(0.8)
        words.next_to(factors, DOWN, 0.8*LARGE_BUFF)
        words_arrows = VGroup(*[
            Arrow(
                words.get_top(), factor.get_bottom(),
                buff = SMALL_BUFF
            )
            for factor in factors
        ])
        analogy = TextMobject("Like $3$ and $-3$")
        analogy.scale(0.8)
        analogy.next_to(words, DOWN)
        analogy.highlight(RED)

        self.play(
            Write(two),
            ShowCreation(arrow),
            DrawBorderThenFill(two_dot)
        )
        self.dither()
        self.play(
            MoveToTarget(mover),
            Write(factorization)
        )
        self.dither(2)
        self.play(
            FadeIn(words),
            *map(ShowCreation, words_arrows)
        )
        self.dither(3)
        self.play(Write(analogy))
        self.dither()

class RingsWithOneModFourPrimes(CertainRegularityInPrimes):
    CONFIG = {
        "plane_center" : ORIGIN,
        "primes" : [5, 13, 17, 29, 37, 41, 53],
        "include_pi_formula" : False,
    }

class RingsWithThreeModFourPrimes(CertainRegularityInPrimes):
    CONFIG = {
        "plane_center" : ORIGIN,
        "primes" : [3, 7, 11, 19, 23, 31, 43],
        "include_pi_formula" : False,
    }

class FactorTwo(LatticePointScene):
    CONFIG = {
        "y_radius" : 3,
    }
    def construct(self):
        two_dot = Dot(self.plane.coords_to_point(2, 0))
        two_dot.highlight(YELLOW)
        factor_dots = VGroup(*[
            Dot(self.plane.coords_to_point(1, u))
            for u in 1, -1
        ])
        two_label = TexMobject("2").next_to(two_dot, DOWN)
        two_label.highlight(YELLOW)
        two_label.add_background_rectangle()
        factor_labels = VGroup(*[
            TexMobject(tex).add_background_rectangle().next_to(dot, vect)
            for tex, dot, vect in zip(
                ["1+i", "1-i"], factor_dots, [UP, DOWN]
            )
        ])
        VGroup(factor_labels, factor_dots).highlight(MAROON_B)

        for dot in it.chain(factor_dots, [two_dot]):
            line = Line(self.plane_center, dot.get_center())
            line.highlight(dot.get_color())
            dot.add(line)

        self.play(
            ShowCreation(two_dot),
            Write(two_label),
        )
        self.play(*[
            ReplacementTransform(
                VGroup(mob1.copy()), mob2
            )
            for mob1, mob2 in [
                (two_label, factor_labels),
                (two_dot, factor_dots),
            ]
        ])
        self.dither(3)

class CountThroughRingsCopy(CountThroughRings):
    pass

class NameGaussianIntegersCopy(NameGaussianIntegers):
    pass

class IntroduceRecipe(Scene):
    CONFIG = {
        "N_string" : "25",
        "integer_factors" : [5, 5],
        "gaussian_factors" : [
            complex(2, 1), complex(2, -1),
            complex(2, 1), complex(2, -1),
        ],
        "x_color" : GREEN,
        "y_color" : RED,
        "N_color" : WHITE,
        "i_positive_color" : BLUE,
        "i_negative_color" : YELLOW,
        "T_chart_width" : 8,
        "T_chart_height" : 6,
    }
    def construct(self):
        self.force_skipping()

        self.add_title()
        self.show_ordinary_factorization()
        self.subfactor_ordinary_factorization()
        self.organize_factors_into_columns()
        self.mention_conjugate_rule()
        self.take_product_of_columns()
        self.mark_left_product_as_result()

    def add_title(self):
        title = TexMobject(
            "\\text{Recipe for }",
            "a", "+", "b", "i",
            "\\text{ satisfying }",
            "(", "a", "+", "b", "i", ")",
            "(", "a", "-", "b", "i", ")",
            "=", self.N_string
        )
        strings = ("a", "b", self.N_string)
        colors = (self.x_color, self.y_color, self.N_color)
        for tex, color in zip(strings, colors):
            title.highlight_by_tex(tex, color, substring = False)
        title.to_edge(UP, buff = MED_SMALL_BUFF)
        h_line = Line(LEFT, RIGHT).scale(SPACE_WIDTH)
        h_line.next_to(title, DOWN)
        self.add(title, h_line)
        N_mob = title.get_part_by_tex(self.N_string)
        digest_locals(self, ["title", "h_line", "N_mob"])

    def show_ordinary_factorization(self):
        N_mob = self.N_mob.copy()
        N_mob.generate_target()
        N_mob.target.next_to(self.h_line, DOWN)
        N_mob.target.to_edge(LEFT)

        factors = self.integer_factors
        symbols = ["="] + ["\\cdot"]*(len(factors)-1)
        factorization = TexMobject(*it.chain(*zip(
            symbols, map(str, factors)
        )))
        factorization.next_to(N_mob.target, RIGHT)

        self.play(MoveToTarget(
            N_mob,
            run_time = 2,
            path_arc = -np.pi/6
        ))
        self.play(Write(factorization))
        self.dither()

        self.factored_N_mob = N_mob
        self.integer_factorization = factorization

    def subfactor_ordinary_factorization(self):
        factors = self.gaussian_factors
        factorization = TexMobject(
            "=", *map(self.complex_number_to_tex, factors)
        )
        max_width = 2*SPACE_WIDTH - 2
        if factorization.get_width() > max_width:
            factorization.scale_to_fit_width(max_width)
        factorization.next_to(
            self.integer_factorization, DOWN,
            aligned_edge = LEFT
        )
        for factor, mob in zip(factors, factorization[1::]):
            mob.underlying_number = factor
            y = complex(factor).imag
            if y > 0:
                mob.highlight(self.i_positive_color)
            if y < 0:
                mob.highlight(self.i_negative_color)
        movers = VGroup()
        mover = self.integer_factorization[0].copy()
        mover.target = factorization[0]
        movers.add(mover)
        index = 0
        for prime_mob in self.integer_factorization[1::2]:
            gauss_prime = factors[index]
            gauss_prime_mob = factorization[index+1]
            mover = prime_mob.copy()
            mover.target = gauss_prime_mob
            movers.add(mover)
            if complex(gauss_prime).imag > 0:
                index += 1
                mover = prime_mob.copy()
                mover.target = factorization[index+1]
                movers.add(mover)
            index += 1

        self.play(LaggedStart(
            MoveToTarget,
            movers,
            replace_mobject_with_target_in_scene = True
        ))
        self.dither()

        self.gaussian_factorization = factorization

    def organize_factors_into_columns(self):
        T_chart = self.get_T_chart()
        factors = self.gaussian_factorization.copy()[1:]
        left_factors = VGroup(factors[0], factors[2])
        right_factors = VGroup(factors[1], factors[3])
        for group in left_factors, right_factors:
            group.generate_target()
            group.target.arrange_submobjects(DOWN)
        left_factors.target.next_to(T_chart.left_h_line, DOWN)
        right_factors.target.next_to(T_chart.right_h_line, DOWN)

        self.play(ShowCreation(T_chart))
        self.dither()
        self.play(MoveToTarget(left_factors))
        self.play(MoveToTarget(right_factors))
        self.dither()

        digest_locals(self, ["left_factors", "right_factors"])

    def mention_conjugate_rule(self):
        left_factors = self.left_factors
        right_factors = self.right_factors
        double_arrows = VGroup()
        for lf, rf in zip(left_factors.target, right_factors.target):
            arrow = DoubleArrow(
                lf, rf, 
                buff = SMALL_BUFF,
                tip_length = SMALL_BUFF,
                color = GREEN
            )
            word = TextMobject("Conjugates")
            word.scale(0.75)
            word.add_background_rectangle()
            word.next_to(arrow, DOWN, SMALL_BUFF)
            arrow.add(word)
            double_arrows.add(arrow)
        main_arrow = double_arrows[0]

        self.play(Write(main_arrow, run_time = 1))
        self.dither()
        for new_arrow in double_arrows[1:]:
            self.play(Transform(main_arrow, new_arrow))
            self.dither()
        self.dither()
        self.play(FadeOut(main_arrow))

    def take_product_of_columns(self):
        arrows = self.get_product_multiplication_lines()
        products = self.get_product_mobjects()
        factor_groups = [self.left_factors, self.right_factors]

        for arrow, product, group in zip(arrows, products, factor_groups):
            self.play(ShowCreation(arrow))
            self.play(ReplacementTransform(
                group.copy(), VGroup(product)
            ))
            self.dither()
        self.dither(3)

    def mark_left_product_as_result(self):
        self.revert_to_original_skipping_status()


    #########

    def get_T_chart(self):
        T_chart = VGroup()
        h_lines = VGroup(*[
            Line(ORIGIN, self.T_chart_width*RIGHT/2.0) 
            for x in range(2)
        ])
        h_lines.arrange_submobjects(RIGHT, buff = 0)
        h_lines.shift(UP)
        v_line = Line(self.T_chart_height*UP, ORIGIN)
        v_line.move_to(h_lines.get_center(), UP)

        T_chart.left_h_line, T_chart.right_h_line = h_lines
        T_chart.v_line = v_line
        T_chart.digest_mobject_attrs()

        return T_chart

    def complex_number_to_tex(self, z):
        z = complex(z)
        x, y = z.real, z.imag
        if y == 0:
            return "(%d)"%x
        y_sign_tex = "+" if y >= 0 else "-"
        if abs(y) == 1:
            y_str = y_sign_tex + "i"
        else:
            y_str = y_sign_tex + "%di"%abs(y)
        return "(%d%s)"%(x, y_str)

    def get_product_multiplication_lines(self):
        lines = VGroup()
        for factors in self.left_factors, self.right_factors:
            line = Line(*map(factors.get_corner, [DOWN+LEFT, DOWN+RIGHT]))
            line.shift(SMALL_BUFF*DOWN)
            line.scale_about_point(1.5, line.get_right())
            times = TexMobject("\\times")
            times.next_to(line.get_left(), UP+RIGHT, SMALL_BUFF)
            line.add(times)
            lines.add(line)
        self.multiplication_lines = lines
        return lines

    def get_product_mobjects(self):
        factor_groups = [self.left_factors, self.right_factors]
        product_mobjects = VGroup()
        for factors, line in zip(factor_groups, self.multiplication_lines):
            product = reduce(op.mul, [
                factor.underlying_number
                for factor in factors
            ])
            color = average_color(*[
                factor.get_color()
                for factor in factors
            ])
            product_mob = TexMobject(
                self.complex_number_to_tex(product)
            )
            product_mob.highlight(color)
            product_mob.next_to(line, DOWN, aligned_edge = RIGHT)
            product_mobjects.add(product_mob)
        self.product_mobjects = product_mobjects
        return product_mobjects





































