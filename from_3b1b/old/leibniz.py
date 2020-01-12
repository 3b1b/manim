from manimlib.imports import *
from functools import reduce

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
            self.x_radius = self.y_radius*FRAME_X_RADIUS/FRAME_Y_RADIUS
        plane = ComplexPlane(
            y_radius = self.y_radius,
            x_radius = self.x_radius,
            secondary_line_ratio = self.secondary_line_ratio,
            radius = self.plane_color
        )
        plane.set_height(FRAME_HEIGHT)
        plane.shift(self.plane_center)
        self.add(plane)
        self.plane = plane

        self.setup_lattice_points()

    def setup_lattice_points(self):
        M = self.max_lattice_point_radius
        int_range = list(range(-M, M+1))
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
        self.lattice_points.sort(
            lambda p : get_norm(p - self.plane_center)
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
        points = VGroup(*[dot for dot in self.lattice_points if dot.r_squared == r_squared])
        points.sort(
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
        x_max = int(self.plane.point_to_coords(FRAME_X_RADIUS*RIGHT)[0])
        y_max = int(self.plane.point_to_coords(FRAME_Y_RADIUS*UP)[1])
        x_range = list(range(spacing, x_max, spacing))
        y_range = list(range(spacing, y_max, spacing))
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
        video.set_color(TEAL)
        video.next_to(morty.get_corner(UP+LEFT), UP)

        self.play(
            morty.change_mode, "raise_right_hand",
            DrawBorderThenFill(video)
        )
        self.wait()
        self.play(
            Write(primes, run_time = 2),
            morty.change_mode, "happy",
            video.set_height, FRAME_WIDTH,
            video.center,
            video.set_fill, None, 0
        )
        self.wait()
        self.play(
            Write(plane, run_time = 2),
            morty.change, "raise_right_hand"
        )
        self.wait()
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
        self.wait(2)
        self.play(
            plane.set_width, pi_group.get_width(),
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
            title.set_color(YELLOW)
        self.play(
            ShowCreation(screen),
            FadeIn(titles[0])
        )
        self.show_frame()
        self.wait(2)
        self.play(Transform(*titles))
        self.wait(3)

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
        label.set_color(YELLOW)
        plane.label = label
        plane.add(dot, label)
        return plane

    def get_pi_group(self):
        result = TexMobject("\\pi", "=", "%.8f\\dots"%np.pi)
        pi = result.get_part_by_tex("pi")
        pi.scale(2, about_point = pi.get_right())
        pi.set_color(MAROON_B)
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
        self.wait(2)

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
        points = list(map(line.number_to_point, partial_sums))
        arrows = [
            Arrow(
                p1, p2, 
                tip_length = 0.2*min(1, get_norm(p1-p2)),
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
        lhs.set_color_by_tex("pi", YELLOW)
        sum_arrow = Arrow(
            lhs.get_part_by_tex("pi").get_bottom(),
            sum_point
        )
        fading_terms = [
            TexMobject(sign + "\\frac{1}{%d}"%(2*n + 1))
            for n, sign in zip(
                list(range(self.num_terms_to_add)),
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
                self.wait()
            else:
                run_time *= 0.8
        self.play(
            FadeOut(arrow),
            FadeOut(fading_term),
            dot.move_to, sum_point
        )
        self.play(ShowCreation(sum_arrow))
        self.wait()
        self.change_student_modes("erm", "confused", "maybe")
        self.play(self.teacher.change_mode, "happy")
        self.wait(2)

class FermatsDreamExcerptWrapper(Scene):
    def construct(self):
        words = TextMobject(
            "From ``Fermat's dream'' by Kato, Kurokawa and Saito"
        )
        words.scale(0.8)
        words.to_edge(UP)
        self.add(words)
        self.wait()

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
        rhs_group.arrange(
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
            self.wait()
        self.change_mode("maybe")
        self.wait()
        self.look_at(rhs_group[-1])
        self.wait()
        self.pi_creature_says(
            "Where's the \\\\ circle?",
            bubble_kwargs = {"width" : 4, "height" : 3},
            target_mode = "maybe"
        )
        self.look_at(rhs_group[0])
        self.wait()

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
        formula.set_color_by_tex("pi", YELLOW)
        formula.add_background_rectangle()
        formula.to_corner(UP+LEFT, buff = MED_SMALL_BUFF)
        self.add_foreground_mobject(formula)

    def walk_through_primes(self):
        primes = self.primes
        lines_and_labels = [
            self.get_radial_line_with_label(np.sqrt(p))
            for p in primes
        ]
        lines, labels = list(zip(*lines_and_labels))
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
        self.wait()
        for group in groups[1:]:
            self.play(Transform(curr_group, group))
            self.wait(2)

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
            step.set_color_by_tex("1", RED, substring = False)
            step.set_color_by_tex("i", RED, substring = False)
            step.set_color_by_tex("4", GREEN, substring = False)
        steps.arrange(
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
        pi.set_color(YELLOW)
        question.next_to(self.pi_creature.body, LEFT, aligned_edge = UP)
        self.think(
            "Who am I really?",
            look_at_arg = question,
            added_anims = [
                FadeIn(question)
            ]
        )
        self.wait(2)
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
        plane.set_height(6)
        plane.next_to(step, DOWN)
        plane.to_edge(LEFT)
        circle = Circle(
            color = YELLOW,
            radius = get_norm(
                plane.coords_to_point(10, 0) - \
                plane.coords_to_point(0, 0)
            )
        )
        plane_center = plane.coords_to_point(0, 0)
        circle.move_to(plane_center)
        lattice_points = VGroup(*[
            Dot(
                plane.coords_to_point(a, b), 
                radius = 0.05,
                color = PINK,
            )
            for a in range(-10, 11)
            for b in range(-10, 11)
            if a**2 + b**2 <= 10**2
        ])
        lattice_points.sort(
            lambda p : get_norm(p - plane_center)
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
        self.wait()
        self.play(
            lattice_group.set_height, 2.5,
            lattice_group.next_to, self.question, DOWN,
            lattice_group.to_edge, RIGHT
        )

    def write_steps_2_and_3(self):
        for step in self.steps[1:3]:
            self.play(FadeIn(step))
            self.wait(2)
        self.wait()

    def show_chi(self):
        input_range = list(range(1, 7))
        chis = VGroup(*[
            TexMobject("\\chi(%d)"%n)
            for n in input_range
        ])
        chis.arrange(RIGHT, buff = LARGE_BUFF)
        chis.set_stroke(WHITE, width = 1)
        numerators = VGroup()
        arrows = VGroup()
        for chi, n in zip(chis, input_range):
            arrow = TexMobject("\\Downarrow")
            arrow.next_to(chi, DOWN, SMALL_BUFF)
            arrows.add(arrow)
            value = TexMobject(str(chi_func(n)))
            value.set_color_by_tex("1", BLUE)
            value.set_color_by_tex("-1", GREEN)
            value.next_to(arrow, DOWN)
            numerators.add(value)
        group = VGroup(chis, arrows, numerators)
        group.set_width(1.3*FRAME_X_RADIUS)
        group.to_corner(DOWN+LEFT)

        self.play(FadeIn(self.steps[3]))
        self.play(*[
            FadeIn(
                mob, 
                run_time = 3,
                lag_ratio = 0.5
            )
            for mob in [chis, arrows, numerators]
        ])
        self.change_mode("pondering")
        self.wait()

        self.chis = chis
        self.arrows = arrows
        self.numerators = numerators

    def show_complicated_formula(self):
        rhs = TexMobject(
            " = \\lim_{N \\to \\infty}",
            " \\frac{4}{N}",
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
        self.wait(2)

        self.complicated_formula = rhs

    def show_last_step(self):
        expression = TexMobject(
            "=", "\\frac{\\quad}{1}",
            *it.chain(*[
                ["+", "\\frac{\\quad}{%d}"%d]
                for d in range(2, len(self.numerators)+1)
            ] + [["+ \\cdots"]])
        )
        over_four = TexMobject("\\quad \\over 4")
        over_four.to_corner(DOWN+LEFT)
        over_four.shift(UP)
        pi = self.pi
        pi.generate_target()
        pi.target.scale(0.75)
        pi.target.next_to(over_four, UP)
        expression.next_to(over_four, RIGHT, align_using_submobjects = True)
        self.numerators.generate_target()
        for num, denom in zip(self.numerators.target, expression[1::2]):
            num.scale(1.2)
            num.next_to(denom, UP, MED_SMALL_BUFF)

        self.play(
            MoveToTarget(self.numerators),
            MoveToTarget(pi),
            Write(over_four),
            FadeOut(self.chis),
            FadeOut(self.arrows),
            FadeOut(self.complicated_formula),
        )
        self.play(
            Write(expression),
            self.pi_creature.change_mode, "pondering"
        )
        self.wait(3)

    ########
    def create_pi_creature(self):
        return Randolph(color = BLUE_C).flip().to_corner(DOWN+RIGHT)

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
        self.wait(2)
        self.play(*list(map(FadeOut, [label, lines, example_dot])))

    def draw_lattice_points_in_circle(self):
        circle = self.get_circle()
        radius = Line(ORIGIN, circle.get_right())
        radius.set_color(RED)
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
        self.wait()
        self.play(*list(map(FadeOut, [brace, radius])))

        self.circle = circle

    def turn_points_int_units_of_area(self):
        square = Square(fill_opacity = 0.9)
        unit_line = Line(
            self.plane.coords_to_point(0, 0),
            self.plane.coords_to_point(1, 0),
        )
        square.set_width(unit_line.get_width())
        squares = VGroup(*[
            square.copy().move_to(point)
            for point in self.lattice_points
        ])
        squares.set_color_by_gradient(BLUE_E, GREEN_E)
        squares.set_stroke(WHITE, 1)
        point_copies = self.lattice_points.copy()

        self.play(
            ReplacementTransform(
                point_copies, squares,
                run_time = 3,
                lag_ratio = 0.5,
            ),
            Animation(self.lattice_points)
        )
        self.wait()
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
            ).arrange(RIGHT)
            for R in ("10", "1{,}000{,}000", "R")
        ])
        radius_10_eq, radius_million_eq, radius_R_eq = equations
        for eq in equations:
            for tex_mob in eq:
                tex_mob.set_color_by_tex("0", BLUE)
        radius_10_eq.to_corner(UP+LEFT)
        radius_million_eq.next_to(radius_10_eq, DOWN, LARGE_BUFF)
        radius_million_eq.to_edge(LEFT)
        brace = Brace(radius_million_eq, DOWN)
        brace.add(brace.get_text("More accurate"))
        brace.set_color(YELLOW)

        background = FullScreenFadeRectangle(opacity = 0.9)

        self.play(
            FadeIn(background),
            Write(radius_10_eq)
        )
        self.wait(2)
        self.play(ReplacementTransform(
            radius_10_eq.copy(),
            radius_million_eq
        ))
        self.play(FadeIn(brace))
        self.wait(3)

        self.radius_10_eq = radius_10_eq
        self.million_group = VGroup(radius_million_eq, brace)
        self.radius_R_eq = radius_R_eq

    def allude_to_alternate_counting_method(self):
        alt_count = TextMobject(
            "(...something else...)", "$R^2$", "=",
            arg_separator = ""
        )
        alt_count.to_corner(UP+LEFT)
        alt_count.set_color_by_tex("something", MAROON_B)
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
        self.wait(2)
        self.play(
            final_group.arrange, RIGHT,
            final_group.next_to, ORIGIN, UP
        )
        rect = BackgroundRectangle(final_group)
        self.play(FadeIn(rect), Animation(final_group))
        self.wait(2)

class SoYouPlay(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "So you play!",
            run_time = 2
        )
        self.change_student_modes("happy", "thinking", "hesitant")
        self.wait()
        self.look_at(Dot().to_corner(UP+LEFT))
        self.wait(3)

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
        self.play(LaggedStartMap(
            ApplyMethod,
            circles,
            arg_creator = lambda m : (m.set_stroke, PINK, 4),
            rate_func = there_and_back,
        ))
        self.wait()
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
        self.wait()

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
        h_line.set_color(GREEN)
        v_line = Line(x_spot, dot)
        v_line.set_color(RED)

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
        self.wait(2)

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
        self.wait()
        self.play(Transform(distance, distance_num))
        self.wait(3)
        self.play(*list(map(FadeOut, [
            self.example_circle, self.points_on_example_circle,
            distance, a, b,
            radial_line, h_line, v_line,
            label
        ])))

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
                list(range(self.num_rings_to_show_explicitly)),
                counts
            )
        ])
        left_counts = VGroup()
        left_roots = VGroup()
        for mob in left_list:
            mob[1].set_color(YELLOW)
            left_counts.add(VGroup(mob[1]))
            mob.add_background_rectangle()
            left_roots.add(VGroup(mob[0], mob[1][0]))

        left_list.arrange(
            DOWN,
            buff = MED_LARGE_BUFF,
            aligned_edge = LEFT,
        )
        left_list.to_corner(UP + LEFT)

        top_list = VGroup(*[
            TexMobject("%d, "%count)
            for count in counts
        ])
        top_list.set_color(YELLOW)
        top_list.arrange(RIGHT, aligned_edge = DOWN)
        top_list.set_width(FRAME_WIDTH - MED_LARGE_BUFF)
        top_list.to_edge(UP, buff = SMALL_BUFF)
        top_rect = BackgroundRectangle(top_list)

        for r_squared, count_mob, root in zip(it.count(), left_counts, left_roots):
            self.show_ring_count(
                r_squared,
                count_mob,
                added_anims = [FadeIn(root)]
            )
            self.wait(2)
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
        self.wait(3)


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
        root.set_width(
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
        self.wait(run_time)
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
            label.x.set_color(x_color)
            label.y.set_color(y_color)
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
            tex_mob.x.set_color(x_color)
            tex_mob.y.set_color(y_color)
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
            FadeIn(points, lag_ratio = 0.5),
            run_time = 2,
        )
        self.wait()

        curr_label = labels[0]
        curr_sum_of_squares = sums_of_squares[0]
        self.play(
            Write(curr_label),
            curr_label.point.set_color, PINK
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
        self.wait()

        for label, sum_of_squares in zip(labels, sums_of_squares)[1:]:
            self.play(
                ReplacementTransform(curr_label, label),
                label.point.set_color, PINK,
                curr_label.point.set_color, self.dot_color
            )
            curr_label = label
            self.play(
                ReplacementTransform(
                    curr_sum_of_squares, sum_of_squares
                )
            )
            curr_sum_of_squares = sum_of_squares
            self.wait()

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
        self.wait()
        self.play(points.restore, run_time = 2)
        self.wait()
        self.play(*list(map(FadeOut, [
            curr_label, curr_sum_of_squares, 
            circle, points,
            radius, root_label
        ])))

    def analyze_11(self):
        R = np.sqrt(11)
        circle = self.get_circle(radius = R)
        radius, root_label = self.get_radial_line_with_label(R)
        equation = TexMobject("11 \\ne ", "a", "^2", "+", "b", "^2")
        equation.set_color_by_tex("a", GREEN)
        equation.set_color_by_tex("b", RED)
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
        self.wait()
        self.play(Write(equation))
        self.wait(3)

class Given2DThinkComplex(TeacherStudentsScene):
    def construct(self):
        tex = TextMobject("2D $\\Leftrightarrow$ Complex numbers")
        plane = ComplexPlane(
            x_radius = 0.6*FRAME_X_RADIUS,
            y_radius = 0.6*FRAME_Y_RADIUS,
        )
        plane.add_coordinates()
        plane.set_height(FRAME_Y_RADIUS)
        plane.to_corner(UP+LEFT)

        self.teacher_says(tex)
        self.change_student_modes("pondering", "confused", "erm")
        self.wait()
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
        self.wait(3)

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
        self.discuss_geometry()
        self.show_geometrically()

    def resize_plane(self):
        self.plane.scale(
            self.plane_scale_factor,
            about_point = self.plane_center
        )
        self.plane.set_stroke(width = 1)
        self.plane.axes.set_stroke(width = 3)

    def write_points_with_complex_coords(self):
        x, y = self.example_coords
        x_color = self.x_color
        y_color = self.y_color

        point = self.plane.coords_to_point(x, y)
        dot = Dot(point, color = self.dot_color)
        x_point = self.plane.coords_to_point(x, 0)
        h_arrow = Arrow(self.plane_center, x_point, buff = 0)
        v_arrow = Arrow(x_point, point, buff = 0)
        h_arrow.set_color(x_color)
        v_arrow.set_color(y_color)
        x_coord = TexMobject(str(x))
        x_coord.next_to(h_arrow, DOWN, SMALL_BUFF)
        x_coord.set_color(x_color)
        x_coord.add_background_rectangle()
        y_coord = TexMobject(str(y))
        imag_y_coord = TexMobject(str(y) + "i")
        for coord in y_coord, imag_y_coord:
            coord.next_to(v_arrow, RIGHT, SMALL_BUFF)
            coord.set_color(y_color)
            coord.add_background_rectangle()

        tuple_label = TexMobject(str((x, y)))
        tuple_label[1].set_color(x_color)
        tuple_label[3].set_color(y_color)
        complex_label = TexMobject("%d+%di"%(x, y))
        complex_label[0].set_color(x_color)
        complex_label[2].set_color(y_color)
        for label in tuple_label, complex_label:
            label.add_background_rectangle()
            label.next_to(dot, UP+RIGHT, buff = 0)

        y_range = list(range(-9, 10, 3))
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
        self.wait()
        self.play(*list(map(FadeOut, [tuple_label, y_coord])))
        self.play(*list(map(FadeIn, [complex_label, imag_y_coord])))
        self.play(*list(map(Write, [imag_coords, ticks])))
        self.wait()
        self.play(*list(map(FadeOut, [
            v_arrow, h_arrow, 
            x_coord, imag_y_coord,
        ])))

        self.complex_label = complex_label
        self.example_dot = dot

    def introduce_complex_conjugate(self):
        x, y = self.example_coords
        equation = VGroup(
            TexMobject("25 = ", str(x), "^2", "+", str(y), "^2", "="),
            TexMobject("(", str(x), "+", str(y), "i", ")"),
            TexMobject("(", str(x), "-", str(y), "i", ")"),
        )
        equation.arrange(
            RIGHT, buff = SMALL_BUFF,
        )
        VGroup(*equation[-2:]).shift(0.5*SMALL_BUFF*DOWN)
        equation.scale(0.9)
        equation.to_corner(UP+RIGHT, buff = MED_SMALL_BUFF)
        equation.shift(MED_LARGE_BUFF*DOWN)
        for tex_mob in equation:
            tex_mob.set_color_by_tex(str(x), self.x_color)
            tex_mob.set_color_by_tex(str(y), self.y_color)
            tex_mob.add_background_rectangle()

        dot = Dot(
            self.plane.coords_to_point(x, -y),
            color = self.dot_color
        )
        label = TexMobject("%d-%di"%(x, y))
        label[0].set_color(self.x_color)
        label[2].set_color(self.y_color)
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
            lag_ratio = 0.5
        ))
        self.wait(2)
        self.play(
            GrowFromCenter(brace),
            Write(conjugate_words, run_time = 2)
        )
        self.wait()
        self.play(*[
            ReplacementTransform(m1.copy(), m2)
            for m1, m2 in [
                (self.example_dot, dot),
                (self.complex_label, label),
            ]
        ])
        self.wait(2)

        self.conjugate_label = VGroup(brace, conjugate_words)
        self.equation = equation
        self.conjugate_dot = dot

    def show_confusion(self):
        randy = Randolph(color = BLUE_C).to_corner(DOWN+LEFT)
        morty = Mortimer().to_edge(DOWN)
        randy.make_eye_contact(morty)

        self.play(*list(map(FadeIn, [randy, morty])))
        self.play(PiCreatureSays(
            randy, "Wait \\dots why?",
            target_mode = "confused",
        ))
        self.play(Blink(randy))
        self.wait(2)
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
        self.play(*list(map(FadeOut, [randy, morty])))

    def expand_algebraically(self):
        x, y = self.example_coords
        expansion = VGroup(
            TexMobject(str(x), "^2"),
            TexMobject("-", "(", str(y), "i", ")^2")
        )
        expansion.arrange(RIGHT, buff = SMALL_BUFF)
        expansion.next_to(
            VGroup(*self.equation[-2:]), 
            DOWN, LARGE_BUFF
        )
        alt_y_term = TexMobject("+", str(y), "^2")
        alt_y_term.move_to(expansion[1], LEFT)
        for tex_mob in list(expansion) + [alt_y_term]:
            tex_mob.set_color_by_tex(str(x), self.x_color)
            tex_mob.set_color_by_tex(str(y), self.y_color)
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
        self.wait()
        self.play(group.shift, vect)
        group = VGroup(x2, y1)
        self.play(group.shift, -vect)
        self.wait()
        self.play(group.shift, vect)
        group = VGroup(*it.chain(y1, y2))
        self.play(group.shift, -vect)
        self.wait()
        self.play(
            FadeIn(expansion[1].rect),
            ReplacementTransform(group.copy(), expansion[1]),
        )
        self.play(group.shift, vect)
        self.wait(2)
        self.play(
            Transform(expansion[1].rect, alt_y_term.rect),
            Transform(expansion[1], alt_y_term),
        )
        self.wait()
        self.play(*list(map(FadeOut, [
            expansion[0].rect,
            expansion[1].rect,
            expansion
        ])))

    def discuss_geometry(self):
        randy = Randolph(color = BLUE_C)
        randy.scale(0.8)
        randy.to_corner(DOWN+LEFT)
        morty = Mortimer()
        morty.set_height(randy.get_height())
        morty.next_to(randy, RIGHT)
        randy.make_eye_contact(morty)
        screen = ScreenRectangle(height = 3.5)
        screen.to_corner(DOWN+RIGHT, buff = MED_SMALL_BUFF)

        self.play(*list(map(FadeIn, [randy, morty])))
        self.play(PiCreatureSays(
            morty, "More geometry!",
            target_mode = "hooray",
            run_time = 2,
            bubble_kwargs = {"height" : 2, "width" : 4}
        ))
        self.play(Blink(randy))
        self.play(
            RemovePiCreatureBubble(
                morty, target_mode = "plain",
            ),
            PiCreatureSays(
                randy, "???",
                target_mode = "maybe",
                bubble_kwargs = {"width" : 3, "height" : 2}
            )
        )
        self.play(
            ShowCreation(screen),
            morty.look_at, screen,
            randy.look_at, screen,
        )
        self.play(Blink(morty))
        self.play(RemovePiCreatureBubble(randy, target_mode = "pondering"))
        self.wait()
        self.play(*list(map(FadeOut, [randy, morty, screen])))

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
            top_dot.line.copy().set_color(PINK), 
            top_dot.copy()
        )
        self.play(FadeIn(
            top_dot.magnitude_word,
            lag_ratio = 0.5
        ))
        self.wait()
        self.play(ShowCreation(top_dot.arc))
        self.wait(2)
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
        self.wait()
        self.play(Write(twenty_five_label))
        self.wait(3)

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
        a.set_color(GREEN)
        b.set_color(RED)
        label.add_background_rectangle()
        label.to_corner(UP+RIGHT)
        integers = TextMobject("Integers")
        integers.next_to(label, DOWN, LARGE_BUFF)
        integers.add_background_rectangle()
        arrows = VGroup(*[
            Arrow(integers.get_top(), mob, tip_length = 0.15)
            for mob in (a, b)
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
            lag_ratio = 0.5
        ))
        self.wait(3)
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
            *list(map(GrowFromCenter, dots))
        )
        self.play(Write(root_label))
        self.wait()

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
                mob.set_color_by_tex(x_str, GREEN, substring = False)
                mob.set_color_by_tex(y_str, RED, substring = False)

            dot.line_pair = VGroup(*[
                Line(
                    self.plane_center,
                    self.plane.coords_to_point(x, u*y),
                    color = PINK,
                )
                for u in (1, -1)
            ])
            dot.conjugate_dot = self.circle_dots[-i]

        self.play(*list(map(FadeOut, [
            self.a_plus_bi, self.integers_label,
            self.gaussian_integers,
        ])))

        last_dot = None
        for dot in self.circle_dots:
            anims = [
                dot.set_color, PINK,
                dot.conjugate_dot.set_color, PINK,
            ]
            if last_dot is None:
                anims += [
                    FadeIn(dot.equation),
                    FadeIn(dot.label),
                ]
                anims += list(map(ShowCreation, dot.line_pair))
            else:
                anims += [
                    last_dot.set_color, self.dot_color,
                    last_dot.conjugate_dot.set_color, self.dot_color,
                    ReplacementTransform(last_dot.equation, dot.equation),
                    ReplacementTransform(last_dot.label, dot.label),
                    ReplacementTransform(last_dot.line_pair, dot.line_pair),
                ]
            self.play(*anims)
            self.wait()
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
            ("=", "2 \\cdot (-3) \\cdot (3) \\cdot (-5) \\cdot 5^2"),
        ]))
        for alt_rhs in alt_rhs_list:
            if "\\ne" in alt_rhs.get_tex_string():
                alt_rhs.set_color(RED)
            else:
                alt_rhs.set_color(GREEN)
            alt_rhs.move_to(equation.get_right())
        number.save_state()
        number.next_to(self.teacher, UP+LEFT)
        title = TextMobject("Almost", "Unique factorization")
        title.set_color_by_tex("Almost", YELLOW)
        title.to_edge(UP)

        self.play(
            self.teacher.change_mode, "raise_right_hand",
            Write(number)
        )
        self.wait(2)
        self.play(
            number.restore,
            Write(VGroup(*equation[1:])),
            Write(title[1])
        )
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = equation,
            added_anims = [self.teacher.change_mode, "happy"]
        )
        self.wait()
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
            if alt_rhs is alt_rhs_list[-2]:
                self.change_student_modes(
                    *["sassy"]*3,
                    look_at_arg = alt_rhs,
                    added_anims = [Write(title[0])]
                )
            self.wait(2)
            last_alt_rhs = alt_rhs

        self.play(
            FadeOut(VGroup(equation, alt_rhs)),
            PiCreatureSays(
                self.teacher,
                "It's similar for \\\\ Gaussian integers",
                bubble_kwargs = {"height" : 3.5}
            )
        )
        self.change_student_modes(*["happy"]*3)
        self.wait(3)

class IntroduceGaussianPrimes(LatticePointScene, PiCreatureScene):
    CONFIG = {
        "plane_center" : LEFT,
        "x_radius" : 13,
    }
    def create_pi_creature(self):
        morty = Mortimer().flip()
        morty.scale(0.7)
        morty.next_to(ORIGIN, UP, buff = 0)
        morty.to_edge(LEFT)
        return morty

    def setup(self):
        LatticePointScene.setup(self)
        PiCreatureScene.setup(self)
        self.remove(self.pi_creature)

    def construct(self):
        self.plane.set_stroke(width = 2)
        morty = self.pi_creature
        dots = [
            Dot(self.plane.coords_to_point(*coords))
            for coords in [
                (5, 0), 
                (2, 1), (2, -1), 
                (-1, 2), (-1, -2),
                (-2, -1), (-2, 1),
            ]
        ]
        five_dot = dots[0]
        five_dot.set_color(YELLOW)
        p_dots = VGroup(*dots[1:])
        p1_dot, p2_dot, p3_dot, p4_dot, p5_dot, p6_dot = p_dots
        VGroup(p1_dot, p3_dot, p5_dot).set_color(PINK)
        VGroup(p2_dot, p4_dot, p6_dot).set_color(RED)

        labels = [
            TexMobject(tex).add_background_rectangle()
            for tex in ("5", "2+i", "2-i", "-1+2i", "-1-2i", "-2-i", "-2+i")
        ]
        five_label, p1_label, p2_label, p3_label, p4_label, p5_label, p6_label = labels
        vects = [
            DOWN, 
            UP+RIGHT, DOWN+RIGHT, 
            UP+LEFT, DOWN+LEFT,
            DOWN+LEFT, UP+LEFT,
        ]
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
        ).set_color(MAROON_B)

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
        neg_alt_factorization = TexMobject("=(-2-i)(-2+i)")
        i_alt_factorization = TexMobject("=(-1+2i)(-1-2i)")
        for alt_factorization in neg_alt_factorization, i_alt_factorization:
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
        self.wait()
        self.play(
            ReplacementTransform(
                VGroup(five_dot).copy(),
                VGroup(p1_dot, p2_dot)
            )
        )
        self.play(*list(map(Write, [p1_label, p2_label])))
        self.wait()
        self.play(Write(gaussian_prime))
        self.wait()

        #Show morty
        self.play(FadeIn(morty))
        self.play(PiCreatureSays(
            morty, "\\emph{Almost} unique",
            bubble_kwargs = {"height" : 2, "width" : 5},
        ))
        self.wait()
        self.play(RemovePiCreatureBubble(morty, target_mode = "pondering"))

        #Show neg_alternate expression 
        movers = [p1_dot, p2_dot, p1_label, p2_label]
        for mover in movers:
            mover.save_state()
        self.play(
            Transform(p1_dot, p5_dot),
            Transform(p1_label, p5_label),
        )
        self.play(
            Transform(p2_dot, p6_dot),
            Transform(p2_label, p6_label),
        )
        self.play(Write(neg_alt_factorization))
        self.wait()
        self.play(
            FadeOut(neg_alt_factorization),
            *[m.restore for m in movers]
        )
        self.wait()

        ##Show i_alternate expression
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
        self.wait()
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
        self.wait()
        self.play(Write(i_alt_factorization))
        self.change_mode("hesitant")
        self.wait(3)

class FromIntegerFactorsToGaussianFactors(TeacherStudentsScene):
    def construct(self):
        expression = TexMobject(
            "30", "=", "2", "\\cdot", "3", "\\cdot", "5"
        )
        expression.shift(2*UP)
        two = expression.get_part_by_tex("2")
        five = expression.get_part_by_tex("5")
        two.set_color(BLUE)
        five.set_color(GREEN)
        two.factors = TexMobject("(1+i)", "(1-i)")
        five.factors = TexMobject("(2+i)", "(2-i)")
        for mob, vect in (two, DOWN), (five, UP):
            mob.factors.next_to(mob, vect, LARGE_BUFF)
            mob.factors.set_color(mob.get_color())
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
                *list(map(ShowCreation, mob.arrows))
            )
            self.wait()
        self.play(*[
            ApplyMethod(pi.change, "pondering", expression)
            for pi in self.get_pi_creatures()
        ])
        self.wait(5)
        group = VGroup(
            expression, 
            two.arrows, two.factors,
            five.arrows, five.factors,
        )
        self.teacher_says(
            "Now for a \\\\ surprising fact...",
            added_anims = [FadeOut(group)]
        )
        self.wait(2)

class FactorizationPattern(Scene):
    def construct(self):
        self.force_skipping()

        self.add_number_line()
        self.show_one_mod_four_primes()
        self.show_three_mod_four_primes()
        self.ask_why_this_is_true()
        self.show_two()

    def add_number_line(self):
        line = NumberLine(
            x_min = 0,
            x_max = 36,
            unit_size = 0.4,
            numbers_to_show = list(range(0, 33, 4)),
            numbers_with_elongated_ticks = list(range(0, 33, 4)),
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
        dots.set_color(GREEN)
        prime_mobs = VGroup(*list(map(TexMobject, list(map(str, primes)))))
        arrows = VGroup()
        for prime_mob, dot in zip(prime_mobs, dots):
            prime_mob.next_to(dot, UP, LARGE_BUFF)
            prime_mob.set_color(dot.get_color())
            arrow = Arrow(prime_mob, dot, buff = SMALL_BUFF)
            arrow.set_color(dot.get_color())
            arrows.add(arrow)

        factorizations = VGroup(*[
            TexMobject("=(%d+%si)(%d-%si)"%(x, y_str, x, y_str))
            for x, y in [(2, 1), (3, 2), (4, 1), (5, 2)]
            for y_str in [str(y) if y is not 1 else ""]
        ])
        factorizations.arrange(DOWN, aligned_edge = LEFT)
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
            list(map(Write, prime_mobs)),
            list(map(ShowCreation, arrows)),
            list(map(DrawBorderThenFill, dots)),
        ))
        self.wait()
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
            lag_ratio = 0.5
        ))
        self.wait(4)
        self.play(*list(map(FadeOut, [movers, factorizations])))

    def show_three_mod_four_primes(self):
        primes = [3, 7, 11, 19, 23, 31]
        dots = VGroup(*[
            Dot(self.number_line.number_to_point(prime))
            for prime in primes
        ])
        dots.set_color(RED)
        prime_mobs = VGroup(*list(map(TexMobject, list(map(str, primes)))))
        arrows = VGroup()
        for prime_mob, dot in zip(prime_mobs, dots):
            prime_mob.next_to(dot, UP, LARGE_BUFF)
            prime_mob.set_color(dot.get_color())
            arrow = Arrow(prime_mob, dot, buff = SMALL_BUFF)
            arrow.set_color(dot.get_color())
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
            list(map(Write, prime_mobs)),
            list(map(ShowCreation, arrows)),
            list(map(DrawBorderThenFill, dots)),
        ))
        self.wait()
        self.play(
            Write(words),
            *list(map(ShowCreation, word_arrows))
        )
        self.wait(4)
        self.play(*list(map(FadeOut, [words, word_arrows])))

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
        self.wait()
        self.play(FadeIn(links_text))
        self.wait(2)
        self.play(*list(map(FadeOut, [
            randy, randy.bubble, randy.bubble.content,
            links_text
        ])))

    def show_two(self):
        two_dot = Dot(self.number_line.number_to_point(2))
        two = TexMobject("2")
        two.next_to(two_dot, UP, LARGE_BUFF)
        arrow = Arrow(two, two_dot, buff = SMALL_BUFF)
        VGroup(two_dot, two, arrow).set_color(YELLOW)

        mover = two.copy()
        mover.generate_target()
        mover.target.to_corner(UP+LEFT)
        factorization = TexMobject("=", "(1+i)", "(1-i)")
        factorization.next_to(mover.target, RIGHT)
        factors = VGroup(*factorization[1:])

        time_i_arrow = Arrow(
            factors[1].get_bottom(),
            factors[0].get_bottom(),
            path_arc = -np.pi
        )
        times_i = TexMobject("\\times i")
        # times_i.scale(1.5)
        times_i.next_to(time_i_arrow, DOWN)
        times_i.set_color(time_i_arrow.get_color())
        words = TextMobject("You'll see why this matters...")
        words.next_to(times_i, DOWN)
        words.shift_onto_screen()

        self.play(
            Write(two),
            ShowCreation(arrow),
            DrawBorderThenFill(two_dot)
        )
        self.wait()
        self.play(
            MoveToTarget(mover),
            Write(factorization)
        )

        self.revert_to_original_skipping_status()
        self.wait(2)
        self.play(ShowCreation(time_i_arrow))
        self.play(Write(times_i))
        self.wait(2)
        self.play(FadeIn(words))
        self.wait(2)

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
        two_dot.set_color(YELLOW)
        factor_dots = VGroup(*[
            Dot(self.plane.coords_to_point(1, u))
            for u in (1, -1)
        ])
        two_label = TexMobject("2").next_to(two_dot, DOWN)
        two_label.set_color(YELLOW)
        two_label.add_background_rectangle()
        factor_labels = VGroup(*[
            TexMobject(tex).add_background_rectangle().next_to(dot, vect)
            for tex, dot, vect in zip(
                ["1+i", "1-i"], factor_dots, [UP, DOWN]
            )
        ])
        VGroup(factor_labels, factor_dots).set_color(MAROON_B)

        for dot in it.chain(factor_dots, [two_dot]):
            line = Line(self.plane_center, dot.get_center())
            line.set_color(dot.get_color())
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
        self.wait(2)
        dot_copy = factor_dots[1].copy()
        dot_copy.set_color(RED)
        for angle in np.pi/2, -np.pi/2:
            self.play(Rotate(dot_copy, angle, run_time = 2))
            self.wait(2)

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
        "i_zero_color" : MAROON_B,
        "T_chart_width" : 8,
        "T_chart_height" : 6,
    }
    def construct(self):
        self.add_title()
        self.show_ordinary_factorization()
        self.subfactor_ordinary_factorization()
        self.organize_factors_into_columns()
        self.mention_conjugate_rule()
        self.take_product_of_columns()
        self.mark_left_product_as_result()
        self.swap_factors()

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
            title.set_color_by_tex(tex, color, substring = False)
        title.to_edge(UP, buff = MED_SMALL_BUFF)
        h_line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS)
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
        factorization = TexMobject(*it.chain(*list(zip(
            symbols, list(map(str, factors))
        ))))
        factorization.next_to(N_mob.target, RIGHT)

        self.play(MoveToTarget(
            N_mob,
            run_time = 2,
            path_arc = -np.pi/6
        ))
        self.play(Write(factorization))
        self.wait()

        self.factored_N_mob = N_mob
        self.integer_factorization = factorization

    def subfactor_ordinary_factorization(self):
        factors = self.gaussian_factors
        factorization = TexMobject(
            "=", *list(map(self.complex_number_to_tex, factors))
        )
        max_width = FRAME_WIDTH - 2
        if factorization.get_width() > max_width:
            factorization.set_width(max_width)
        factorization.next_to(
            self.integer_factorization, DOWN,
            aligned_edge = LEFT
        )
        for factor, mob in zip(factors, factorization[1:]):
            mob.underlying_number = factor
            y = complex(factor).imag
            if y == 0:
                mob.set_color(self.i_zero_color)
            elif y > 0:
                mob.set_color(self.i_positive_color)
            elif y < 0:
                mob.set_color(self.i_negative_color)
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
            if abs(complex(gauss_prime).imag) > 0:
                index += 1
                mover = prime_mob.copy()
                mover.target = factorization[index+1]
                movers.add(mover)
            index += 1

        self.play(LaggedStartMap(
            MoveToTarget,
            movers,
            replace_mobject_with_target_in_scene = True
        ))
        self.wait()

        self.gaussian_factorization = factorization

    def organize_factors_into_columns(self):
        T_chart = self.get_T_chart()
        factors = self.gaussian_factorization.copy()[1:]
        left_factors, right_factors = self.get_left_and_right_factors()
        for group in left_factors, right_factors:
            group.generate_target()
            group.target.arrange(DOWN)
        left_factors.target.next_to(T_chart.left_h_line, DOWN)
        right_factors.target.next_to(T_chart.right_h_line, DOWN)

        self.play(ShowCreation(T_chart))
        self.wait()
        self.play(MoveToTarget(left_factors))
        self.play(MoveToTarget(right_factors))
        self.wait()

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
        self.wait()
        for new_arrow in double_arrows[1:]:
            self.play(Transform(main_arrow, new_arrow))
            self.wait()
        self.wait()
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
            self.wait()
        self.wait(3)

    def mark_left_product_as_result(self):
        rect = self.get_result_surrounding_rect()
        words = TextMobject("Output", " of recipe")
        words.next_to(rect, DOWN, buff = MED_LARGE_BUFF)
        words.to_edge(LEFT)
        arrow = Arrow(words.get_top(), rect.get_left())

        self.play(ShowCreation(rect))
        self.play(
            Write(words, run_time = 2),
            ShowCreation(arrow)
        )
        self.wait(3)
        self.play(*list(map(FadeOut, [words, arrow])))

        self.output_label_group = VGroup(words, arrow)

    def swap_factors(self):
        for i in range(len(self.left_factors)):
            self.swap_factors_at_index(i)
            self.wait()

    #########

    def get_left_and_right_factors(self):
        factors = self.gaussian_factorization.copy()[1:]
        return VGroup(*factors[::2]), VGroup(*factors[1::2])

    def get_T_chart(self):
        T_chart = VGroup()
        h_lines = VGroup(*[
            Line(ORIGIN, self.T_chart_width*RIGHT/2.0) 
            for x in range(2)
        ])
        h_lines.arrange(RIGHT, buff = 0)
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
            line = Line(ORIGIN, 3*RIGHT)
            line.next_to(factors, DOWN, SMALL_BUFF)
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
            product_mob.set_color(color)
            product_mob.next_to(line, DOWN)
            product_mobjects.add(product_mob)
        self.product_mobjects = product_mobjects
        return product_mobjects

    def swap_factors_at_index(self, index):
        factor_groups = self.left_factors, self.right_factors
        factors_to_swap = [group[index] for group in factor_groups]
        self.play(*[
            ApplyMethod(
                factors_to_swap[i].move_to, factors_to_swap[1-i],
                path_arc = np.pi/2,
            )
            for i in range(2)
        ])
        for i, group in enumerate(factor_groups):
            group.submobjects[index] = factors_to_swap[1-i]
        self.play(FadeOut(self.product_mobjects))
        self.get_product_mobjects()
        rect = self.result_surrounding_rect
        new_rect = self.get_result_surrounding_rect()
        self.play(*[
            ReplacementTransform(group.copy(), VGroup(product))
            for group, product in zip(
                factor_groups, self.product_mobjects,
            )
        ]+[
            ReplacementTransform(rect, new_rect)
        ])
        self.wait()

    def get_result_surrounding_rect(self, product = None):
        if product is None:
            product = self.product_mobjects[0]
        rect = SurroundingRectangle(product)
        self.result_surrounding_rect = rect
        return rect

    def write_last_step(self):
        output_words, arrow = self.output_label_group
        final_step = TextMobject(
            "Multiply by $1$, $i$, $-1$ or $-i$"
        )
        final_step.scale(0.9)
        final_step.next_to(arrow.get_start(), DOWN, SMALL_BUFF)
        final_step.shift_onto_screen()
        
        anims = [Write(final_step)]
        if arrow not in self.get_mobjects():
            # arrow = Arrow(
            #     final_step.get_top(),
            #     self.result_surrounding_rect.get_left()
            # )
            anims += [ShowCreation(arrow)]
        self.play(*anims)
        self.wait(2)

class StateThreeChoices(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "$5^2$ gives 3 choices."
        )
        self.wait(3)

class ThreeOutputsAsLatticePoints(LatticePointScene):
    CONFIG = {
        "coords_list" : [(3, 4), (5, 0), (3, -4)],
        "dot_radius" : 0.1,
        "colors" : [YELLOW, GREEN, PINK, MAROON_B],
    }
    def construct(self):
        self.add_circle()
        self.add_dots_and_labels()

    def add_circle(self):
        radius = np.sqrt(self.radius_squared)
        circle = self.get_circle(radius)
        radial_line, root_label = self.get_radial_line_with_label(radius)
        self.add(radial_line, root_label, circle)
        self.add_foreground_mobject(root_label)

    def add_dots_and_labels(self):
        dots = VGroup(*[
            Dot(
                self.plane.coords_to_point(*coords),
                radius = self.dot_radius, 
                color = self.colors[0],
            )
            for coords in self.coords_list
        ])
        labels = VGroup()
        for x, y in self.coords_list:
            if y == 0:
                y_str = ""
                vect = DOWN+RIGHT
            elif y > 1:
                y_str = "+%di"%y
                vect = UP+RIGHT
            else:
                y_str = "%di"%y
                vect = DOWN+RIGHT
            label = TexMobject("%d%s"%(x, y_str))
            label.add_background_rectangle()
            point = self.plane.coords_to_point(x, y)
            label.next_to(point, vect)
            labels.add(label)

        for dot, label in zip(dots, labels):
            self.play(
                FadeIn(label),
                DrawBorderThenFill(
                    dot, 
                    stroke_color = PINK,
                    stroke_width = 4
                )
            )
        self.wait(2)

        self.original_dots = dots

class LooksLikeYoureMissingSome(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Looks like you're \\\\ missing a few",
            target_mode = "sassy",
            student_index = 0,
        )
        self.play(self.teacher.change, "guilty")
        self.wait(3)

class ShowAlternateFactorizationOfTwentyFive(IntroduceRecipe):
    CONFIG = {
        "gaussian_factors" : [
            complex(-1, 2), complex(-1, -2),
            complex(2, 1), complex(2, -1),
        ],
    }
    def construct(self):
        self.add_title()
        self.show_ordinary_factorization()
        self.subfactor_ordinary_factorization()
        self.organize_factors_into_columns()
        self.take_product_of_columns()
        self.mark_left_product_as_result()
        self.swap_factors()

class WriteAlternateLastStep(IntroduceRecipe):
    def construct(self):
        self.force_skipping()        
        self.add_title()
        self.show_ordinary_factorization()
        self.subfactor_ordinary_factorization()
        self.organize_factors_into_columns()
        self.take_product_of_columns()
        self.mark_left_product_as_result()
        self.revert_to_original_skipping_status()

        self.cross_out_output_words()
        self.write_last_step()

    def cross_out_output_words(self):
        output_words, arrow = self.output_label_group
        cross = TexMobject("\\times")
        cross.replace(output_words, stretch = True)
        cross.set_color(RED)
        
        self.add(output_words, arrow)
        self.play(Write(cross))
        output_words.add(cross)
        self.play(output_words.to_edge, DOWN)

class ThreeOutputsAsLatticePointsContinued(ThreeOutputsAsLatticePoints):
    def construct(self):
        self.force_skipping()
        ThreeOutputsAsLatticePoints.construct(self)
        self.revert_to_original_skipping_status()

        self.show_multiplication_by_units()

    def show_multiplication_by_units(self):
        original_dots = self.original_dots
        lines = VGroup()
        for dot in original_dots:
            line = Line(self.plane_center, dot.get_center())
            line.set_stroke(dot.get_color(), 6)
            lines.add(line)
            dot.add(line)
        words_group = VGroup(*[
            TextMobject("Multiply by $%s$"%s)
            for s in ("1", "i", "-1", "-i")
        ])
        for words, color in zip(words_group, self.colors):
            words.add_background_rectangle()
            words.set_color(color)
        words_group.arrange(DOWN, aligned_edge = LEFT)
        words_group.to_corner(UP+LEFT, buff = MED_SMALL_BUFF)
        angles = [np.pi/2, np.pi, -np.pi/2]

        self.play(
            FadeIn(words_group[0]),
            *list(map(ShowCreation, lines))
        )
        for words, angle, color in zip(words_group[1:], angles, self.colors[1:]):
            self.play(FadeIn(words))
            dots_copy = original_dots.copy()
            self.play(
                dots_copy.rotate, angle,
                dots_copy.set_color, color,
                path_arc = angle
            )
            self.wait()
        self.wait(2)

class RecipeFor125(IntroduceRecipe):
    CONFIG = {
        "N_string" : "125",
        "integer_factors" : [5, 5, 5],
        "gaussian_factors" : [
            complex(2, -1), complex(2, 1), 
            complex(2, -1), complex(2, 1), 
            complex(2, -1), complex(2, 1),
        ],
    }
    def construct(self):
        self.force_skipping()

        self.add_title()
        self.show_ordinary_factorization()
        self.subfactor_ordinary_factorization()
        
        self.revert_to_original_skipping_status()
        self.organize_factors_into_columns()
        # self.take_product_of_columns()
        # self.mark_left_product_as_result()
        # self.swap_factors()
        # self.write_last_step()

class StateFourChoices(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "$5^3$ gives 4 choices."
        )
        self.wait(3)

class Show125Circle(ThreeOutputsAsLatticePointsContinued):
    CONFIG = {
        "radius_squared" : 125,
        "coords_list" : [(2, 11), (10, 5), (10, -5), (2, -11)],
        "y_radius" : 15,
    }
    def construct(self):
        self.draw_circle()
        self.add_dots_and_labels()
        self.show_multiplication_by_units()
        self.ask_about_two()

    def draw_circle(self):
        self.plane.scale(2)
        radius = np.sqrt(self.radius_squared)
        circle = self.get_circle(radius)
        radial_line, root_label = self.get_radial_line_with_label(radius)

        self.play(
            Write(root_label),
            ShowCreation(radial_line)
        )
        self.add_foreground_mobject(root_label)
        self.play(
            Rotating(
                radial_line, 
                rate_func = smooth, 
                about_point = self.plane_center
            ),
            ShowCreation(circle),
            run_time = 2,
        )
        group = VGroup(
            self.plane, radial_line, circle, root_label
        )
        self.play(group.scale, 0.5)

class RecipeFor375(IntroduceRecipe):
    CONFIG = {
        "N_string" : "375",
        "integer_factors" : [3, 5, 5, 5],
        "gaussian_factors" : [
            3, 
            complex(2, 1), complex(2, -1),
            complex(2, 1), complex(2, -1),
            complex(2, 1), complex(2, -1),
        ],
    }
    def construct(self):
        self.add_title()
        self.show_ordinary_factorization()
        self.subfactor_ordinary_factorization()
        self.organize_factors_into_columns()
        self.express_trouble_with_three()
        self.take_product_of_columns()

    def express_trouble_with_three(self):
        morty = Mortimer().flip().to_corner(DOWN+LEFT)
        three = self.gaussian_factorization[1].copy()
        three.generate_target()
        three.target.next_to(morty, UP, MED_LARGE_BUFF)

        self.play(FadeIn(morty))
        self.play(
            MoveToTarget(three), 
            morty.change, "angry", three.target
        )
        self.play(Blink(morty))
        self.wait()
        for factors in self.left_factors, self.right_factors:
            self.play(
                three.next_to, factors, DOWN,
                morty.change, "sassy", factors.get_bottom()
            )
            self.wait()
        self.right_factors.add(three)
        self.play(morty.change_mode, "pondering")

    ####

    def get_left_and_right_factors(self):
        factors = self.gaussian_factorization.copy()[1:]
        return VGroup(*factors[1::2]), VGroup(*factors[2::2])

class Show375Circle(LatticePointScene):
    CONFIG = {
        "y_radius" : 20,
    }
    def construct(self):
        radius = np.sqrt(375)
        circle = self.get_circle(radius)
        radial_line, root_label = self.get_radial_line_with_label(radius)

        self.play(
            ShowCreation(radial_line),
            Write(root_label, run_time = 1)
        )
        self.add_foreground_mobject(root_label)
        self.play(
            Rotating(
                radial_line,
                rate_func = smooth,
                about_point = self.plane_center
            ),
            ShowCreation(circle),
            run_time = 2,
        )
        group = VGroup(
            self.plane, radial_line, root_label, circle
        )
        self.wait(2)

class RecipeFor1125(IntroduceRecipe):
    CONFIG = {
        "N_string" : "1125",
        "integer_factors" : [3, 3, 5, 5, 5],
        "gaussian_factors" : [
            3, 3,
            complex(2, 1), complex(2, -1),
            complex(2, 1), complex(2, -1),
            complex(2, 1), complex(2, -1),
        ],
    }
    def construct(self):
        self.add_title()
        self.show_ordinary_factorization()
        self.subfactor_ordinary_factorization()
        self.organize_factors_into_columns()
        self.mention_conjugate_rule()
        self.take_product_of_columns()
        self.mark_left_product_as_result()
        self.swap_factors()
        self.write_last_step()

    def write_last_step(self):
        words = TextMobject(
            "Multiply by \\\\ ", 
            "$1$, $i$, $-1$ or $-i$"
        )
        words.scale(0.7)
        words.to_corner(DOWN+LEFT)
        product = self.product_mobjects[0]

        self.play(Write(words))
        self.wait()

class Show125CircleSimple(LatticePointScene):
    CONFIG = {
        "radius_squared" : 125,
        "y_radius" : 12,
        "max_lattice_point_radius" : 12,
    }
    def construct(self):
        self.plane.set_stroke(width = 1)
        radius = np.sqrt(self.radius_squared)
        circle = self.get_circle(radius)
        radial_line, root_label = self.get_radial_line_with_label(radius)
        dots = self.get_lattice_points_on_r_squared_circle(self.radius_squared)

        self.play(
            ShowCreation(radial_line),
            Write(root_label, run_time = 1)
        )
        self.add_foreground_mobject(root_label)
        self.play(
            Rotating(
                radial_line,
                rate_func = smooth,
                about_point = self.plane_center
            ),
            ShowCreation(circle),
            LaggedStartMap(
                DrawBorderThenFill,
                dots,
                stroke_width = 4,
                stroke_color = PINK,
            ),
            run_time = 2,
        )
        self.wait(2)

class Show1125Circle(Show125CircleSimple):
    CONFIG = {
        "radius_squraed" : 1125,
        "y_radius" : 35,
        "max_lattice_point_radius" : 35,
    }

class SummarizeCountingRule(Show125Circle):
    CONFIG = {
        "dot_radius" : 0.075,
        "N_str" : "N",
        "rect_opacity" : 1,
    }
    def construct(self):
        self.add_count_words()
        self.draw_circle()
        self.add_full_screen_rect()
        self.talk_through_rules()
        self.ask_about_two()

    def add_count_words(self):
        words = TextMobject(
            "\\# Lattice points \\\\ on $\\sqrt{%s}$ circle"%self.N_str
        )
        words.to_corner(UP+LEFT)
        words.add_background_rectangle()
        self.add(words)
        self.count_words = words

    def draw_circle(self):
        radius = np.sqrt(self.radius_squared)
        circle = self.get_circle(radius)
        radial_line, num_root_label = self.get_radial_line_with_label(radius)
        root_label = TexMobject("\\sqrt{%s}"%self.N_str)
        root_label.next_to(radial_line, UP, SMALL_BUFF)
        dots = VGroup(*[
            Dot(
                self.plane.coords_to_point(*coords),
                radius = self.dot_radius,
                color = self.dot_color
            )
            for coords in self.coords_list
        ])
        for angle in np.pi/2, np.pi, -np.pi/2:
            dots.add(*dots.copy().rotate(angle))

        self.play(
            Write(root_label),
            ShowCreation(radial_line)
        )
        self.play(
            Rotating(
                radial_line, 
                rate_func = smooth, 
                about_point = self.plane_center
            ),
            ShowCreation(circle),
            run_time = 2,
        )
        self.play(LaggedStartMap(
            DrawBorderThenFill,
            dots,
            stroke_width = 4,
            stroke_color = PINK
        ))
        self.wait(2)

    def add_full_screen_rect(self):
        rect = FullScreenFadeRectangle(
            fill_opacity = self.rect_opacity
        )
        self.play(
            FadeIn(rect),
            Animation(self.count_words)
        )

    def talk_through_rules(self):
        factorization = TexMobject(
            "N =", 
            "3", "^4", "\\cdot",
            "5", "^3", "\\cdot",
            "13", "^2"
        )
        factorization.next_to(ORIGIN, RIGHT)
        factorization.to_edge(UP)

        three, five, thirteen = [
            factorization.get_part_by_tex(str(n), substring = False)
            for n in (3, 5, 13)
        ]
        three_power = factorization.get_part_by_tex("^4")
        five_power = factorization.get_part_by_tex("^3")
        thirteen_power = factorization.get_part_by_tex("^2")
        alt_three_power = five_power.copy().move_to(three_power)

        three_brace = Brace(VGroup(*factorization[1:3]), DOWN)
        five_brace = Brace(VGroup(*factorization[3:6]), DOWN)
        thirteen_brace = Brace(VGroup(*factorization[6:9]), DOWN)

        three_choices = three_brace.get_tex("(", "1", ")")
        five_choices = five_brace.get_tex(
            "(", "3", "+", "1", ")"
        )
        thirteen_choices = thirteen_brace.get_tex(
            "(", "2", "+", "1", ")"
        )
        all_choices = VGroup(three_choices, five_choices, thirteen_choices)
        for choices in all_choices:
            choices.scale(0.75, about_point = choices.get_top())
        thirteen_choices.next_to(five_choices, RIGHT)
        three_choices.next_to(five_choices, LEFT)
        alt_three_choices = TexMobject("(", "0", ")")
        alt_three_choices.scale(0.75)
        alt_three_choices.move_to(three_choices, RIGHT)


        self.play(FadeIn(factorization))
        self.wait()
        self.play(
            five.set_color, GREEN,
            thirteen.set_color, GREEN,
            FadeIn(five_brace),
            FadeIn(thirteen_brace),
        )
        self.wait()
        for choices, power in (five_choices, five_power), (thirteen_choices, thirteen_power):
            self.play(
                Write(VGroup(choices[0], *choices[2:])),
                ReplacementTransform(
                    power.copy(), choices[1]
                )
            )
        self.wait()
        self.play(
            three.set_color, RED,
            FadeIn(three_brace)
        )
        self.wait()
        self.play(
            Write(VGroup(three_choices[0], three_choices[2])),
            ReplacementTransform(
                three_power.copy(), three_choices[1]
            )
        )
        self.wait()

        movers = three_power, three_choices
        for mob in movers:
            mob.save_state()
        self.play(
            Transform(
                three_power, alt_three_power,
                path_arc = np.pi
            ),
            Transform(three_choices, alt_three_choices)
        )
        self.wait()
        self.play(
            *[mob.restore for mob in movers],
            path_arc = -np.pi
        )
        self.wait()

        equals_four = TexMobject("=", "4")
        four = equals_four.get_part_by_tex("4")
        four.set_color(YELLOW)
        final_choice_words = TextMobject(
            "Mutiply", "by $1$, $i$, $-1$ or $-i$"
        )
        final_choice_words.set_color(YELLOW)
        final_choice_words.next_to(four, DOWN, LARGE_BUFF, LEFT)
        final_choice_words.to_edge(RIGHT)
        final_choice_arrow = Arrow(
            final_choice_words[0].get_top(),
            four.get_bottom(),
            buff = SMALL_BUFF
        )

        choices_copy = all_choices.copy()
        choices_copy.generate_target()

        choices_copy.target.scale(1./0.75)
        choices_copy.target.arrange(RIGHT, buff = SMALL_BUFF)
        choices_copy.target.next_to(equals_four, RIGHT, SMALL_BUFF)
        choices_copy.target.shift(0.25*SMALL_BUFF*DOWN)
        self.play(
            self.count_words.next_to, equals_four, LEFT,
            MoveToTarget(choices_copy),
            FadeIn(equals_four)
        )
        self.play(*list(map(FadeIn, [final_choice_words, final_choice_arrow])))
        self.wait()

    def ask_about_two(self):
        randy = Randolph(color = BLUE_C)
        randy.scale(0.7)
        randy.to_edge(LEFT)

        self.play(FadeIn(randy))
        self.play(PiCreatureBubbleIntroduction(
            randy, "What about \\\\ factors of 2?",
            bubble_class = ThoughtBubble,
            bubble_kwargs = {"height" : 3, "width" : 3},
            target_mode = "confused",
            look_at_arg = self.count_words
        ))
        self.play(Blink(randy))
        self.wait()

class ThisIsTheHardestPart(TeacherStudentsScene):
    def construct(self):
        self.change_student_modes("horrified", "confused", "pleading")
        self.teacher_says("This is the \\\\ hardest part")
        self.change_student_modes("thinking", "happy", "pondering")
        self.wait(2)

class RecipeFor10(IntroduceRecipe):
    CONFIG = {
        "N_string" : "10",
        "integer_factors" : [2, 5],
        "gaussian_factors" : [
            complex(1, 1), complex(1, -1),
            complex(2, 1), complex(2, -1),
        ],
    }
    def construct(self):
        self.add_title()
        self.show_ordinary_factorization()
        self.subfactor_ordinary_factorization()
        self.organize_factors_into_columns()
        self.take_product_of_columns()
        self.mark_left_product_as_result()
        self.swap_two_factors()
        self.write_last_step()

    def swap_two_factors(self):
        left = self.left_factors[0]
        right = self.right_factors[0]
        arrow = Arrow(right, left, buff = SMALL_BUFF)
        times_i = TexMobject("\\times i")
        times_i.next_to(arrow, DOWN, 0)
        times_i.add_background_rectangle()
        curr_product = self.product_mobjects[0].copy()

        for x in range(2):
            self.swap_factors_at_index(0)
        self.play(
            ShowCreation(arrow),
            Write(times_i, run_time = 1)
        )
        self.wait()
        self.play(curr_product.to_edge, LEFT)
        self.swap_factors_at_index(0)
        new_arrow = Arrow(
            self.result_surrounding_rect, curr_product, 
            buff = SMALL_BUFF
        )
        self.play(
            Transform(arrow, new_arrow),
            MaintainPositionRelativeTo(times_i, arrow)
        )
        self.wait(2)
        self.play(*list(map(FadeOut, [arrow, times_i, curr_product])))

class FactorsOfTwoNeitherHelpNorHurt(TeacherStudentsScene):
    def construct(self):
        words = TextMobject(
            "Factors of", "$2^k$", "neither \\\\ help nor hurt"
        )
        words.set_color_by_tex("2", YELLOW)
        self.teacher_says(words)
        self.change_student_modes(*["pondering"]*3)
        self.wait(3)

class EffectOfPowersOfTwo(LatticePointScene):
    CONFIG = {
        "y_radius" : 9,
        "max_lattice_point_radius" : 9,
        "square_radii" : [5, 10, 20, 40, 80],
    }
    def construct(self):
        radii = list(map(np.sqrt, self.square_radii))
        circles = list(map(self.get_circle, radii))
        radial_lines, root_labels = list(zip(*list(map(
            self.get_radial_line_with_label, radii
        ))))
        dots_list = list(map(
            self.get_lattice_points_on_r_squared_circle,
            self.square_radii
        ))
        groups = [
            VGroup(*mobs)
            for mobs in zip(radial_lines, circles, root_labels, dots_list)
        ]
        group = groups[0]

        self.add(group)
        self.play(LaggedStartMap(
            DrawBorderThenFill, dots_list[0],
            stroke_width = 4,
            stroke_color = PINK
        ))
        self.wait()
        for new_group in groups[1:]:
            self.play(Transform(group, new_group))
            self.wait(2)

class NumberTheoryAtItsBest(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Number theory at its best!",
            target_mode = "hooray",
            run_time = 2,
        )
        self.change_student_modes(*["hooray"]*3)
        self.wait(3)

class IntroduceChi(FactorizationPattern):
    CONFIG = {
        "numbers_list" : [
            list(range(i, 36, d))
            for i, d in [(1, 4), (3, 4), (2, 2)]
        ],
        "colors" : [GREEN, RED, YELLOW]
    }
    def construct(self):
        self.add_number_line()
        self.add_define_chi_label()
        for index in range(3):
            self.describe_values(index)
        self.fade_out_labels()
        self.cyclic_pattern()
        self.write_multiplicative_label()
        self.show_multiplicative()


    def add_define_chi_label(self):
        label = TextMobject("Define $\\chi(n)$:")
        chi_expressions = VGroup(*[
            self.get_chi_expression(numbers, color)
            for numbers, color in zip(
                self.numbers_list,
                self.colors
            )
        ])
        chi_expressions.scale(0.9)
        chi_expressions.arrange(
            DOWN, buff = MED_LARGE_BUFF, aligned_edge = LEFT
        )
        chi_expressions.to_corner(UP+RIGHT)
        brace = Brace(chi_expressions, LEFT)
        label.next_to(brace, LEFT)

        self.play(
            Write(label),
            GrowFromCenter(brace)
        )
        self.define_chi_label = label
        self.chi_expressions = chi_expressions

    def describe_values(self, index):
        numbers = self.numbers_list[index]
        color = self.colors[index]
        dots, arrows, labels = self.get_dots_arrows_and_labels(
            numbers, color
        )
        chi_expression = self.chi_expressions[index]

        self.introduce_dots_arrows_and_labels(dots, arrows, labels)
        self.wait()
        self.play(
            Write(VGroup(*[
                part 
                for part in chi_expression
                if part not in chi_expression.inputs
            ])), 
        *[
            ReplacementTransform(label.copy(), num_mob)
            for label, num_mob in zip(
                labels, chi_expression.inputs
            )
        ])
        self.wait()

    def fade_out_labels(self):
        self.play(*list(map(FadeOut, [
            self.last_dots, self.last_arrows, self.last_labels,
            self.number_line
        ])))

    def cyclic_pattern(self):
        input_range = list(range(1, 9))
        chis = VGroup(*[
            TexMobject("\\chi(%d)"%n)
            for n in input_range
        ])
        chis.arrange(RIGHT, buff = LARGE_BUFF)
        chis.set_stroke(WHITE, width = 1)
        numbers = VGroup()
        arrows = VGroup()
        for chi, n in zip(chis, input_range):
            arrow = TexMobject("\\Uparrow")
            arrow.next_to(chi, UP, SMALL_BUFF)
            arrows.add(arrow)
            value = TexMobject(str(chi_func(n)))
            for tex, color in zip(["1", "-1", "0"], self.colors):
                value.set_color_by_tex(tex, color)
            value.next_to(arrow, UP)
            numbers.add(value)
        group = VGroup(chis, arrows, numbers)
        group.set_width(FRAME_WIDTH - LARGE_BUFF)
        group.to_edge(DOWN, buff = LARGE_BUFF)

        self.play(*[
            FadeIn(
                mob, 
                run_time = 3,
                lag_ratio = 0.5
            )
            for mob in [chis, arrows, numbers]
        ])

        self.play(LaggedStartMap(
            ApplyMethod,
            numbers,
            lambda m : (m.shift, MED_SMALL_BUFF*UP),
            rate_func = there_and_back,
            lag_ratio = 0.2,
            run_time = 6
        ))

        self.wait()
        self.play(*list(map(FadeOut, [chis, arrows, numbers])))

    def write_multiplicative_label(self):
        morty = Mortimer()
        morty.scale(0.7)
        morty.to_corner(DOWN+RIGHT)

        self.play(PiCreatureSays(
            morty, "$\\chi$ is ``multiplicative''",
            bubble_kwargs = {"height" : 2.5, "width" : 5}
        ))
        self.play(Blink(morty))
        self.morty = morty

    def show_multiplicative(self):
        pairs = [(3, 5), (5, 5), (2, 13), (3, 11)]
        expressions = VGroup()
        for x, y in pairs:
            expression = TexMobject(
                "\\chi(%d)"%x,
                "\\cdot",
                "\\chi(%d)"%y,
                "=", 
                "\\chi(%d)"%(x*y)
            )
            braces = [
                Brace(expression[i], UP) 
                for i in (0, 2, 4)
            ]
            for brace, n in zip(braces, [x, y, x*y]):
                output = chi_func(n)
                label = brace.get_tex(str(output))
                label.set_color(self.number_to_color(output))
                brace.add(label)
                expression.add(brace)
            expressions.add(expression)

        expressions.next_to(ORIGIN, LEFT)
        expressions.shift(DOWN)
        expression = expressions[0]

        self.play(
            FadeIn(expression),
            self.morty.change, "pondering", expression
        )
        self.wait(2)
        for new_expression in expressions[1:]:
            self.play(Transform(expression, new_expression))
            self.wait(2)




    #########

    def get_dots_arrows_and_labels(self, numbers, color):
        dots = VGroup()
        arrows = VGroup()
        labels = VGroup()
        for number in numbers:
            point = self.number_line.number_to_point(number)
            dot = Dot(point)
            label = TexMobject(str(number))
            label.scale(0.8)
            label.next_to(dot, UP, LARGE_BUFF)
            arrow = Arrow(label, dot, buff = SMALL_BUFF)
            VGroup(dot, label, arrow).set_color(color)
            dots.add(dot)
            arrows.add(arrow)
            labels.add(label)
        return dots, arrows, labels

    def introduce_dots_arrows_and_labels(self, dots, arrows, labels):
        if hasattr(self, "last_dots"):
            self.play(
                ReplacementTransform(self.last_dots, dots),
                ReplacementTransform(self.last_arrows, arrows),
                ReplacementTransform(self.last_labels, labels),
            )
        else:
            self.play(
                Write(labels),
                FadeIn(arrows, lag_ratio = 0.5),
                LaggedStartMap(
                    DrawBorderThenFill, dots,
                    stroke_width = 4,
                    stroke_color = YELLOW
                ),
                run_time = 2
            )
        self.last_dots = dots
        self.last_arrows = arrows
        self.last_labels = labels

    def get_chi_expression(self, numbers, color, num_terms = 4):
        truncated_numbers = numbers[:num_terms]
        output = str(chi_func(numbers[0]))
        result = TexMobject(*it.chain(*[
            ["\\chi(", str(n), ")", "="]
            for n in truncated_numbers
        ] + [
            ["\\cdots =", output]
        ]))
        result.inputs = VGroup()
        for n in truncated_numbers:
            num_mob = result.get_part_by_tex(str(n), substring = False)
            num_mob.set_color(color)
            result.inputs.add(num_mob)
        result.set_color_by_tex(output, color, substring = False)
        return result

    def number_to_color(self, n):
        output = chi_func(n)
        if n == 1:
            return self.colors[0]
        elif n == -1:
            return self.colors[1]
        else:
            return self.colors[2]

class WriteCountingRuleWithChi(SummarizeCountingRule):
    CONFIG = {
        "colors" : [GREEN, RED, YELLOW]
    }
    def construct(self):
        self.add_count_words()
        self.draw_circle()
        self.add_full_screen_rect()

        self.add_factorization_and_rule()
        self.write_chi_expression()
        self.walk_through_expression_terms()
        self.circle_four()

    def add_factorization_and_rule(self):
        factorization = TexMobject(
            "N", "=", 
            "2", "^2", "\\cdot",
            "3", "^4", "\\cdot",
            "5", "^3",
        )
        for tex, color in zip(["5", "3", "2"], self.colors):
            factorization.set_color_by_tex(tex, color, substring = False)
        factorization.to_edge(UP)
        factorization.shift(LEFT)

        count = VGroup(
            TexMobject("=", "4"),
            TexMobject("(", "1", ")"),
            TexMobject("(", "1", ")"),
            TexMobject("(", "3+1", ")"),
        )
        count.arrange(RIGHT, buff = SMALL_BUFF)
        for i, color in zip([3, 2, 1], self.colors):
            count[i][1].set_color(color)
        count.next_to(
            factorization.get_part_by_tex("="), DOWN,
            buff = LARGE_BUFF,
            aligned_edge = LEFT
        )

        self.play(
            FadeIn(factorization),
            self.count_words.next_to, count, LEFT
        )
        self.wait()
        self.play(*[
            ReplacementTransform(
                VGroup(factorization.get_part_by_tex(
                    tex, substring = False
                )).copy(),
                part
            )
            for tex, part in zip(["=", "2", "3", "5"], count)
        ])
        self.wait()

        self.factorization = factorization
        self.count = count

    def write_chi_expression(self):
        equals_four = TexMobject("=", "4")
        expression = VGroup(equals_four)
        for n, k, color in zip([2, 3, 5], [2, 4, 3], reversed(self.colors)):
            args = ["(", "\\chi(", "1", ")", "+"]
            for i in range(1, k+1):
                args += ["\\chi(", str(n), "^%d"%i, ")", "+"]
            args[-1] = ")"
            factor = TexMobject(*args)
            factor.set_color_by_tex(str(n), color, substring = False)
            factor.set_color_by_tex("1", color, substring = False)
            factor.scale(0.8)
            expression.add(factor)
        expression.arrange(
            DOWN, buff = MED_SMALL_BUFF, aligned_edge = LEFT
        )
        equals_four.next_to(expression[1], LEFT, SMALL_BUFF)
        expression.shift(
            self.count[0].get_center() + LARGE_BUFF*DOWN -\
            equals_four.get_center()
        )

        count_copy = self.count.copy()
        self.play(*[
            ApplyMethod(
                c_part.move_to, e_part, LEFT,
                path_arc = -np.pi/2,
                run_time = 2
            )
            for c_part, e_part in zip(count_copy, expression)
        ])
        self.wait()
        self.play(ReplacementTransform(
            count_copy, expression,
            run_time = 2
        ))
        self.wait()

        self.chi_expression = expression

    def walk_through_expression_terms(self):
        rect = FullScreenFadeRectangle()
        groups = [
            VGroup(
                self.chi_expression[index],
                self.count[index],
                self.factorization.get_part_by_tex(tex1, substring = False),
                self.factorization.get_part_by_tex(tex2, substring = False),
            )
            for index, tex1, tex2 in [
                (-1, "5", "^3"), (-2, "3", "^4"), (-3, "2", "^2")
            ]
        ]
        evaluation_strings = [
            "(1+1+1+1)",
            "(1-1+1-1+1)",
            "(1+0+0)",
        ]

        for group, tex in zip(groups, evaluation_strings):
            chi_sum, count, base, exp = group
            brace = Brace(chi_sum, DOWN)
            evaluation = brace.get_tex(*tex)
            evaluation.set_color(base.get_color())
            evaluation_rect = BackgroundRectangle(evaluation)

            self.play(FadeIn(rect), Animation(group))
            self.play(GrowFromCenter(brace))
            self.play(
                FadeIn(evaluation_rect),
                ReplacementTransform(chi_sum.copy(), evaluation),
            )
            self.wait(2)
            self.play(Indicate(count, color = PINK))
            self.wait()
            if base.get_tex_string() is "3":
                new_exp = TexMobject("3")
                new_exp.replace(exp)
                count_num = count[1]
                new_count = TexMobject("0")
                new_count.replace(count_num, dim_to_match = 1)
                new_count.set_color(count_num.get_color())
                evaluation_point = VectorizedPoint(evaluation[-4].get_right())
                chi_sum_point = VectorizedPoint(chi_sum[-7].get_right())
                new_brace = Brace(VGroup(*chi_sum[:-6]), DOWN)

                to_save = [brace, exp, evaluation, count_num, chi_sum]
                for mob in to_save:
                    mob.save_state()

                self.play(FocusOn(exp))
                self.play(Transform(exp, new_exp))
                self.play(
                    Transform(brace, new_brace),
                    Transform(
                        VGroup(*evaluation[-3:-1]),
                        evaluation_point
                    ),
                    evaluation[-1].next_to, evaluation_point, RIGHT, SMALL_BUFF,
                    Transform(
                        VGroup(*chi_sum[-6:-1]),
                        chi_sum_point
                    ),
                    chi_sum[-1].next_to, chi_sum_point, RIGHT, SMALL_BUFF
                )
                self.play(Transform(count_num, new_count))
                self.play(Indicate(count_num, color = PINK))
                self.wait()
                self.play(*[mob.restore for mob in to_save])

            self.play(
                FadeOut(VGroup(
                    rect, brace, evaluation_rect, evaluation
                )),
                Animation(group)
            )

    def circle_four(self):
        four = self.chi_expression[0][1]
        rect = SurroundingRectangle(four)

        self.revert_to_original_skipping_status()
        self.play(ShowCreation(rect))
        self.wait(3)

class WeAreGettingClose(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("We're getting close...")
        self.change_student_modes(*["hooray"]*3)
        self.wait(2)

class ExpandCountWith45(SummarizeCountingRule):
    CONFIG = {
        "N_str" : "45",
        "coords_list" : [(3, 6), (6, 3)],
        "radius_squared" : 45,
        "y_radius" : 7,
        "rect_opacity" : 0.75,
    }
    def construct(self):
        self.add_count_words()
        self.draw_circle()
        self.add_full_screen_rect()
        self.add_factorization_and_count()
        self.expand_expression()
        self.show_divisor_sum()


    def add_factorization_and_count(self):
        factorization = TexMobject(
            "45", "=", "3", "^2", "\\cdot", "5",
        )
        for tex, color in zip(["5", "3",], [GREEN, RED]):
            factorization.set_color_by_tex(tex, color, substring = False)
        factorization.to_edge(UP)
        factorization.shift(1.7*LEFT)

        equals_four = TexMobject("=", "4")
        expression = VGroup(equals_four)
        for n, k, color in zip([3, 5], [2, 1], [RED, GREEN]):
            args = ["("]
            ["\\chi(1)", "+"]
            for i in range(k+1):
                if i == 0:
                    input_str = "1"
                elif i == 1:
                    input_str = str(n)
                else:
                    input_str = "%d^%d"%(n, i)
                args += ["\\chi(%s)"%input_str, "+"]
            args[-1] = ")"
            factor = TexMobject(*args)
            for part in factor[1::2]:
                part[2].set_color(color)
            factor.scale(0.8)
            expression.add(factor)
        expression.arrange(RIGHT, buff = SMALL_BUFF)
        expression.next_to(
            factorization[1], DOWN, 
            buff = LARGE_BUFF,
            aligned_edge = LEFT,
        )
        braces = VGroup(*[
            Brace(part, UP)
            for part in expression[1:]
        ])
        for brace, num, color in zip(braces, [1, 2], [RED, GREEN]):
            num_mob = brace.get_tex(str(num), buff = SMALL_BUFF)
            num_mob.set_color(color)
            brace.add(num_mob)

        self.play(
            FadeIn(factorization),
            self.count_words.next_to, expression, LEFT
        )
        self.wait()
        self.play(*[
            ReplacementTransform(
                VGroup(factorization.get_part_by_tex(
                    tex, substring = False
                )).copy(),
                part
            )
            for tex, part in zip(["=", "3", "5"], expression)
        ])
        self.play(FadeIn(braces))
        self.wait()

        self.chi_expression = expression
        self.factorization = factorization

    def expand_expression(self):
        equals, four, lp, rp = list(map(TexMobject, [
            "=", "4", "\\big(", "\\big)"
        ]))
        expansion = VGroup(equals, four, lp)
        chi_pairs = list(it.product(*[
            factor[1::2]
            for factor in self.chi_expression[1:]
        ]))
        num_pairs = list(it.product([1, 3, 9], [1, 5]))
        products = list(it.starmap(op.mul, num_pairs))
        sorted_indices = np.argsort(products)
        mover_groups = [VGroup(), VGroup()]
        plusses = VGroup()
        prime_pairs = VGroup()
        for index in sorted_indices:
            pair = chi_pairs[index]
            prime_pair = VGroup()
            for chi, movers in zip(pair, mover_groups):
                mover = chi.copy()
                mover.generate_target()
                expansion.add(mover.target)
                movers.add(mover)
                prime_pair.add(mover.target[2])
            prime_pairs.add(prime_pair)
            if index != sorted_indices[-1]:
                plus = TexMobject("+")
                plusses.add(plus)
                expansion.add(plus)
        expansion.add(rp)
        expansion.arrange(RIGHT, buff = SMALL_BUFF)
        expansion.set_width(FRAME_WIDTH - LARGE_BUFF)
        expansion.next_to(ORIGIN, UP)
        rect = BackgroundRectangle(expansion)
        rect.stretch_in_place(1.5, 1)

        self.play(
            FadeIn(rect),
            *[
                ReplacementTransform(
                    self.chi_expression[i][j].copy(),
                    mob
                )
                for i, j, mob in [
                    (0, 0, equals),
                    (0, 1, four),
                    (1, 0, lp),
                    (2, -1, rp),
                ]
            ]
        )
        for movers in mover_groups:
            self.wait()
            self.play(movers.next_to, rect, DOWN)
            self.play(*list(map(MoveToTarget, movers)))
        self.play(Write(plusses))
        self.wait()

        self.expansion = expansion
        self.prime_pairs = prime_pairs

    def show_divisor_sum(self):
        equals, four, lp, rp = list(map(TexMobject, [
            "=", "4", "\\big(", "\\big)"
        ]))
        divisor_sum = VGroup(equals, four, lp)

        num_pairs = list(it.product([1, 3, 9], [1, 5]))
        products = list(it.starmap(op.mul, num_pairs))
        products.sort()
        color = BLACK
        product_mobs = VGroup()
        chi_mobs = VGroup()
        for product in products:
            chi_mob = TexMobject("\\chi(", str(product), ")")
            product_mob = chi_mob.get_part_by_tex(str(product))
            product_mob.set_color(color)
            product_mobs.add(product_mob)
            divisor_sum.add(chi_mob)
            chi_mobs.add(chi_mob)
            if product != products[-1]:
                divisor_sum.add(TexMobject("+"))
        divisor_sum.add(rp)
        divisor_sum.arrange(RIGHT, buff = SMALL_BUFF)
        divisor_sum.next_to(self.expansion, DOWN, MED_LARGE_BUFF)
        rect = BackgroundRectangle(divisor_sum)

        prime_pairs = self.prime_pairs.copy()
        for prime_pair, product_mob in zip(prime_pairs, product_mobs):
            prime_pair.target = product_mob.copy()
            prime_pair.target.set_color(YELLOW)

        braces = VGroup(*[Brace(m, DOWN) for m in chi_mobs])
        for brace, product in zip(braces, products):
            value = brace.get_tex(str(chi_func(product)))
            brace.add(value)

        self.play(
            FadeIn(rect),
            Write(divisor_sum, run_time = 2)
        )
        self.play(LaggedStartMap(
            MoveToTarget, prime_pairs, 
            run_time = 4,
            lag_ratio = 0.25,
        ))
        self.remove(prime_pairs)
        product_mobs.set_color(YELLOW)
        self.wait(2)
        self.play(LaggedStartMap(
            ApplyMethod,
            product_mobs,
            lambda m : (m.shift, MED_LARGE_BUFF*DOWN),
            rate_func = there_and_back
        ))
        self.play(FadeIn(
            braces, 
            run_time = 2,
            lag_ratio = 0.5,
        ))
        self.wait(2)

class CountLatticePointsInBigCircle(LatticePointScene):
    CONFIG = {
        "y_radius" : 2*11,
        "max_lattice_point_radius" : 10,
        "dot_radius" : 0.05
    }
    def construct(self):
        self.resize_plane()
        self.introduce_points()
        self.show_rings()
        self.ignore_center_dot()

    def resize_plane(self):
        self.plane.set_stroke(width = 2)
        self.plane.scale(2)
        self.lattice_points.scale(2)
        for point in self.lattice_points:
            point.scale_in_place(0.5)

    def introduce_points(self):
        circle = self.get_circle(radius = self.max_lattice_point_radius)
        radius = Line(ORIGIN, circle.get_right())
        radius.set_color(RED)
        R = TexMobject("R").next_to(radius, UP)
        R_rect = BackgroundRectangle(R)
        R_group = VGroup(R_rect, R)
        pi_R_squared = TexMobject("\\pi", "R", "^2")
        pi_R_squared.next_to(ORIGIN, UP)
        pi_R_squared.to_edge(RIGHT)
        pi_R_squared_rect = BackgroundRectangle(pi_R_squared)
        pi_R_squared_group = VGroup(pi_R_squared_rect, pi_R_squared)

        self.play(*list(map(FadeIn, [circle, radius, R_group])))
        self.add_foreground_mobject(R_group)
        self.draw_lattice_points()
        self.wait()
        self.play(
            FadeOut(R_rect),
            FadeIn(pi_R_squared_rect),
            ReplacementTransform(R, pi_R_squared.get_part_by_tex("R")),
            Write(VGroup(*[
                part for part in pi_R_squared
                if part is not pi_R_squared.get_part_by_tex("R")
            ]))
        )
        self.remove(R_group)
        self.add_foreground_mobject(pi_R_squared_group)
        self.wait()

        self.circle = circle
        self.radius = radius

    def show_rings(self):
        N_range = list(range(self.max_lattice_point_radius**2))
        rings = VGroup(*[
            self.get_circle(radius = np.sqrt(N))
            for N in N_range
        ])
        rings.set_color_by_gradient(TEAL, GREEN)
        rings.set_stroke(width = 2)
        dot_groups = VGroup(*[
            self.get_lattice_points_on_r_squared_circle(N)
            for N in N_range
        ])
        radicals = self.get_radicals()

        self.play(
            LaggedStartMap(FadeIn, rings),
            Animation(self.lattice_points),
            LaggedStartMap(FadeIn, radicals),
            run_time = 3
        )
        self.add_foreground_mobject(radicals)
        self.play(
            LaggedStartMap(
                ApplyMethod,
                dot_groups,
                lambda m : (m.set_stroke, PINK, 5),
                rate_func = there_and_back,
                run_time = 4,
                lag_ratio = 0.1,
            ),
        )
        self.wait()

        self.rings = rings

    def ignore_center_dot(self):
        center_dot = self.lattice_points[0]
        circle = Circle(color = RED)
        circle.replace(center_dot)
        circle.scale_in_place(2)
        arrow = Arrow(ORIGIN, UP+RIGHT, color = RED)
        arrow.next_to(circle, DOWN+LEFT, SMALL_BUFF)
        new_max = 2*self.max_lattice_point_radius
        new_dots = VGroup(*[
            Dot(
                self.plane.coords_to_point(x, y),
                color = self.dot_color,
                radius = self.dot_radius,
            )
            for x in range(-new_max, new_max+1)
            for y in range(-new_max, new_max+1)
            if (x**2 + y**2) > self.max_lattice_point_radius**2
            if (x**2 + y**2) < new_max**2
        ])
        new_dots.sort(get_norm)

        self.play(*list(map(ShowCreation, [circle, arrow])))
        self.play(*list(map(FadeOut, [circle, arrow])))
        self.play(FadeOut(center_dot))
        self.lattice_points.remove(center_dot)
        self.wait()
        self.play(*[
            ApplyMethod(m.scale, 0.5)
            for m in [
                self.plane,
                self.circle,
                self.radius,
                self.rings,
                self.lattice_points
            ]
        ])
        new_dots.scale(0.5)
        self.play(FadeOut(self.rings))
        self.play(
            ApplyMethod(
                VGroup(self.circle, self.radius).scale_in_place, 2,
                rate_func=linear,
            ),
            LaggedStartMap(
                DrawBorderThenFill,
                new_dots,
                stroke_width = 4,
                stroke_color = PINK,
                lag_ratio = 0.2,
            ),
            run_time = 4,
        )
        self.wait(2)

    #####

    @staticmethod
    def get_radicals():
        radicals = VGroup(*[
            TexMobject("\\sqrt{%d}"%N)
            for N in range(1, 13)
        ])
        radicals.add(
            TexMobject("\\vdots"),
            TexMobject("\\sqrt{R^2}")
        )
        radicals.arrange(DOWN, buff = MED_SMALL_BUFF)
        radicals.set_height(FRAME_HEIGHT - MED_LARGE_BUFF)
        radicals.to_edge(DOWN, buff = MED_SMALL_BUFF)
        radicals.to_edge(LEFT)
        for radical in radicals:
            radical.add_background_rectangle()
        return radicals

class AddUpGrid(Scene):
    def construct(self):
        self.add_radicals()
        self.add_row_lines()
        self.add_chi_sums()
        self.put_four_in_corner()
        self.talk_through_rows()
        self.organize_into_columns()
        self.add_count_words()
        self.collapse_columns()
        self.factor_out_R()
        self.show_chi_sum_values()
        self.compare_to_pi_R_squared()
        self.celebrate()

    def add_radicals(self):
        self.radicals = CountLatticePointsInBigCircle.get_radicals()
        self.add(self.radicals)

    def add_row_lines(self):
        h_line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS - MED_LARGE_BUFF)
        h_line.set_stroke(WHITE, 1)
        row_lines = VGroup(*[
            h_line.copy().next_to(
                radical, DOWN,
                buff = SMALL_BUFF,
                aligned_edge = LEFT
            )
            for radical in self.radicals
        ])
        row_lines[-2].shift(
            row_lines[-1].get_left()[0]*RIGHT -\
            row_lines[-2].get_left()[0]*RIGHT
        )

        self.play(LaggedStartMap(ShowCreation, row_lines))
        self.wait()

        self.row_lines = row_lines

    def add_chi_sums(self):
        chi_sums = VGroup()
        chi_mobs = VGroup()
        plusses = VGroup()
        fours = VGroup()
        parens = VGroup()
        arrows = VGroup()
        for N, radical in zip(list(range(1, 13)), self.radicals):
            arrow, four, lp, rp = list(map(TexMobject, [
                "\\Rightarrow", "4", "\\big(", "\\big)"
            ]))
            fours.add(four)
            parens.add(lp, rp)
            arrows.add(arrow)
            chi_sum = VGroup(arrow, four, lp)
            for d in range(1, N+1):
                if N%d != 0:
                    continue
                chi_mob = TexMobject("\\chi(", str(d), ")")
                chi_mob[1].set_color(YELLOW)
                chi_mob.d = d
                chi_mobs.add(chi_mob)
                chi_sum.add(chi_mob)
                if d != N:
                    plus = TexMobject("+")
                    plus.chi_mob = chi_mob
                    plusses.add(plus)
                    chi_sum.add(plus)
            chi_sum.add(rp)
            chi_sum.arrange(RIGHT, buff = SMALL_BUFF)
            chi_sum.scale(0.7)
            chi_sum.next_to(radical, RIGHT)
            chi_sums.add(chi_sum)
            radical.chi_sum = chi_sum

        self.play(LaggedStartMap(
            Write, chi_sums, 
            run_time = 5,
            rate_func = lambda t : t,
        ))
        self.wait()

        digest_locals(self, [
            "chi_sums", "chi_mobs", "plusses", 
            "fours", "parens", "arrows",
        ])

    def put_four_in_corner(self):
        corner_four = TexMobject("4")
        corner_four.to_corner(DOWN+RIGHT, buff = MED_SMALL_BUFF)
        rect = SurroundingRectangle(corner_four, color = BLUE)
        corner_four.rect = rect

        self.play(
            ReplacementTransform(
                self.fours, VGroup(corner_four),
                run_time = 2,
            ),
            FadeOut(self.parens)
        )
        self.play(ShowCreation(rect))

        self.corner_four = corner_four

    def talk_through_rows(self):
        rect = Rectangle(
            stroke_width = 0,
            fill_color = BLUE_C,
            fill_opacity = 0.3,
        )
        rect.stretch_to_fit_width(
            VGroup(self.radicals, self.chi_mobs).get_width()
        )
        rect.stretch_to_fit_height(self.radicals[0].get_height())

        composite_rects, prime_rects = [
            VGroup(*[
                rect.copy().move_to(self.radicals[N-1], LEFT)
                for N in numbers
            ])
            for numbers in ([6, 12], [2, 3, 5, 7, 11])
        ]
        prime_rects.set_color(GREEN)

        randy = Randolph().flip()
        randy.next_to(self.chi_mobs, RIGHT)

        self.play(FadeIn(randy))
        self.play(randy.change_mode, "pleading")
        self.play(
            FadeIn(composite_rects),
            randy.look_at, composite_rects.get_bottom()
        )
        self.wait(2)
        self.play(
            FadeOut(composite_rects),
            FadeIn(prime_rects),
            randy.look_at, prime_rects.get_top(),
        )
        self.play(Blink(randy))
        self.wait()
        self.play(*list(map(FadeOut, [prime_rects, randy])))

    def organize_into_columns(self):
        left_x = self.arrows.get_right()[0] + SMALL_BUFF
        spacing = self.chi_mobs[-1].get_width() + SMALL_BUFF
        for chi_mob in self.chi_mobs:
            y = chi_mob.get_left()[1]
            x = left_x + (chi_mob.d - 1)*spacing
            chi_mob.generate_target()
            chi_mob.target.move_to(x*RIGHT + y*UP, LEFT)
        for plus in self.plusses:
            plus.generate_target()
            plus.target.scale(0.5)
            plus.target.next_to(
                plus.chi_mob.target, RIGHT, SMALL_BUFF
            )

        self.play(*it.chain(
            list(map(MoveToTarget, self.chi_mobs)),
            list(map(MoveToTarget, self.plusses)),
        ), run_time = 2)
        self.wait()

    def add_count_words(self):
        rect = Rectangle(
            stroke_color = WHITE,
            stroke_width = 2,
            fill_color = average_color(BLUE_E, BLACK),
            fill_opacity = 1,
            height = 1.15,
            width = FRAME_WIDTH - 2*MED_SMALL_BUFF,
        )
        rect.move_to(3*LEFT, LEFT)
        rect.to_edge(UP, buff = SMALL_BUFF)
        words = TextMobject("Total")
        words.scale(0.8)
        words.next_to(rect.get_left(), RIGHT, SMALL_BUFF)
        approx = TexMobject("\\approx")
        approx.scale(0.7)
        approx.next_to(words, RIGHT, SMALL_BUFF)
        words.add(approx)

        self.play(*list(map(FadeIn, [rect, words])))
        self.wait()

        self.count_rect = rect
        self.count_words = words

    def collapse_columns(self):
        chi_mob_columns = [VGroup() for i in range(12)]
        for chi_mob in self.chi_mobs:
            chi_mob_columns[chi_mob.d - 1].add(chi_mob)

        full_sum = VGroup()
        for d in range(1, 7):
            R_args = ["{R^2"]
            if d != 1:
                R_args.append("\\over %d}"%d)
            term = VGroup(
                TexMobject(*R_args),
                TexMobject("\\chi(", str(d), ")"),
                TexMobject("+")
            )
            term.arrange(RIGHT, SMALL_BUFF)
            term[1][1].set_color(YELLOW)
            full_sum.add(term)
        full_sum.arrange(RIGHT, SMALL_BUFF)
        full_sum.scale(0.7)
        full_sum.next_to(self.count_words, RIGHT, SMALL_BUFF)

        for column, term in zip(chi_mob_columns, full_sum):
            rect = SurroundingRectangle(column)
            rect.stretch_to_fit_height(FRAME_HEIGHT)
            rect.move_to(column, UP)
            rect.set_stroke(width = 0)
            rect.set_fill(YELLOW, 0.3)

            self.play(FadeIn(rect))
            self.wait()
            self.play(
                ReplacementTransform(
                    column.copy(),
                    VGroup(term[1]),
                    run_time = 2
                ),
                Write(term[0]),
                Write(term[2]),
            )
            self.wait()
            if term is full_sum[2]:
                vect = sum([
                    self.count_rect.get_left()[0],
                    FRAME_X_RADIUS,
                    -MED_SMALL_BUFF,
                ])*LEFT
                self.play(*[
                    ApplyMethod(m.shift, vect)
                    for m in [
                        self.count_rect,
                        self.count_words,
                    ]+list(full_sum[:3])
                ])
                VGroup(*full_sum[3:]).shift(vect)
            self.play(FadeOut(rect))

        self.full_sum = full_sum

    def factor_out_R(self):
        self.corner_four.generate_target()
        R_squared = TexMobject("R^2")
        dots = TexMobject("\\cdots")
        lp, rp = list(map(TexMobject, ["\\big(", "\\big)"]))
        new_sum = VGroup(
            self.corner_four.target, R_squared, lp
        )

        R_fracs, chi_terms, plusses = full_sum_parts = [
            VGroup(*[term[i] for term in self.full_sum])
            for i in range(3)
        ]
        targets = []
        for part in full_sum_parts:
            part.generate_target()
            targets.append(part.target)
        for R_frac, chi_term, plus in zip(*targets):
            chi_term.scale(0.9)
            chi_term.move_to(R_frac[0], DOWN)
            if R_frac is R_fracs.target[0]:
                new_sum.add(chi_term)
            else:
                new_sum.add(VGroup(chi_term, R_frac[1]))
            new_sum.add(plus)
        new_sum.add(dots)
        new_sum.add(rp)
        new_sum.arrange(RIGHT, buff = SMALL_BUFF)
        new_sum.next_to(self.count_words, RIGHT, SMALL_BUFF)
        R_squared.shift(0.5*SMALL_BUFF*UP)
        R_movers = VGroup()
        for R_frac in R_fracs.target:
            if R_frac is R_fracs.target[0]:
                mover = R_frac
            else:
                mover = R_frac[0]
            Transform(mover, R_squared).update(1)
            R_movers.add(mover)

        self.play(*it.chain(
            list(map(Write, [lp, rp, dots])), 
            list(map(MoveToTarget, full_sum_parts)),
        ), run_time = 2)
        self.remove(R_movers)
        self.add(R_squared)
        self.wait()
        self.play(
            MoveToTarget(self.corner_four, run_time = 2),
            FadeOut(self.corner_four.rect)
        )
        self.wait(2)
        self.remove(self.full_sum, self.corner_four)
        self.add(new_sum)

        self.new_sum = new_sum

    def show_chi_sum_values(self):
        alt_rhs = TexMobject(
            "\\approx", "4", "R^2", 
            "\\left(1 - \\frac{1}{3} + \\frac{1}{5}" + \
            "-\\frac{1}{7} + \\frac{1}{9} - \\frac{1}{11}" + \
            "+ \\cdots \\right)",
        )
        alt_rhs.scale(0.9)
        alt_rhs.next_to(
            self.count_words[-1], DOWN,
            buff = LARGE_BUFF,
            aligned_edge = LEFT
        )

        self.play(
            *list(map(FadeOut, [
                self.chi_mobs, self.plusses, self.arrows,
                self.radicals, self.row_lines
            ])) + [
            FadeOut(self.count_rect),
            Animation(self.new_sum),
            Animation(self.count_words),
            ]
        )
        self.play(Write(alt_rhs))
        self.wait(2)

        self.alt_rhs = alt_rhs

    def compare_to_pi_R_squared(self):
        approx, pi, R_squared = area_rhs = TexMobject(
            "\\approx", "\\pi", "R^2"
        )
        area_rhs.next_to(self.alt_rhs, RIGHT)

        brace = Brace(
            VGroup(self.alt_rhs, area_rhs), DOWN
        )
        brace.add(brace.get_text(
            "Arbitrarily good as $R \\to \\infty$"
        ))

        pi_sum = TexMobject(
            "4", self.alt_rhs[-1].get_tex_string(),
            "=", "\\pi"
        )
        pi_sum.scale(0.9)
        pi = pi_sum.get_part_by_tex("pi")
        pi.scale(2, about_point = pi.get_left())
        pi.set_color(YELLOW)
        pi_sum.shift(
            self.alt_rhs[-1].get_bottom(),
            MED_SMALL_BUFF*DOWN,
            -pi_sum[1].get_top()
        )

        self.play(Write(area_rhs))
        self.wait()
        self.play(FadeIn(brace))
        self.wait(2)
        self.play(FadeOut(brace))
        self.play(*[
            ReplacementTransform(m.copy(), pi_sum_part)
            for pi_sum_part, m in zip(pi_sum, [
                self.alt_rhs.get_part_by_tex("4"),
                self.alt_rhs[-1],
                area_rhs[0],
                area_rhs[1],
            ])
        ])

    def celebrate(self):
        creatures = TeacherStudentsScene().get_pi_creatures()
        self.play(FadeIn(creatures))
        self.play(*[
            ApplyMethod(pi.change, "hooray", self.alt_rhs)
            for pi in creatures
        ])
        self.wait()
        for i in 0, 2, 3:
            self.play(Blink(creatures[i]))
            self.wait()

class IntersectionOfTwoFields(TeacherStudentsScene):
    def construct(self):
        circles = VGroup()
        for vect, color, adj in (LEFT, BLUE, "Algebraic"), (RIGHT, YELLOW, "Analytic"):
            circle = Circle(color = WHITE)
            circle.set_fill(color, opacity = 0.3)
            circle.stretch_to_fit_width(7)
            circle.stretch_to_fit_height(4)
            circle.shift(FRAME_X_RADIUS*vect/3.0 + LEFT)
            title = TextMobject("%s \\\\ number theory"%adj)
            title.scale(0.7)
            title.move_to(circle)
            title.to_edge(UP, buff = SMALL_BUFF)
            circle.next_to(title, DOWN, SMALL_BUFF)
            title.set_color(color)
            circle.title = title
            circles.add(circle)
        new_number_systems = TextMobject(
            "New \\\\ number systems"
        )
        gaussian_integers = TextMobject(
            "e.g. Gaussian \\\\ integers"
        )
        new_number_systems.next_to(circles[0].get_top(), DOWN, MED_SMALL_BUFF)
        new_number_systems.shift(MED_LARGE_BUFF*(DOWN+2*LEFT))
        gaussian_integers.next_to(new_number_systems, DOWN)
        gaussian_integers.set_color(BLUE)
        circles[0].words = VGroup(new_number_systems, gaussian_integers)

        zeta = TexMobject("\\zeta(s) = \\sum_{n=1}^\\infty \\frac{1}{n^s}")
        L_function = TexMobject(
            "L(s, \\chi) = \\sum_{n=1}^\\infty \\frac{\\chi(n)}{n^s}"
        )
        for mob in zeta, L_function:
            mob.scale(0.8)
        zeta.next_to(circles[1].get_top(), DOWN, MED_LARGE_BUFF)
        zeta.shift(MED_LARGE_BUFF*RIGHT)
        L_function.next_to(zeta, DOWN, MED_LARGE_BUFF)
        L_function.set_color(YELLOW)
        circles[1].words = VGroup(zeta, L_function)

        mid_words = TextMobject("Where\\\\ we \\\\ were")
        mid_words.scale(0.7)
        mid_words.move_to(circles)

        for circle in circles:
            self.play(
                Write(circle.title, run_time = 2),
                DrawBorderThenFill(circle, run_time = 2),
                self.teacher.change_mode, "raise_right_hand"
            )
        self.wait()
        for circle in circles:
            for word in circle.words:
                self.play(
                    Write(word, run_time = 2),
                    self.teacher.change, "speaking",
                    *[
                        ApplyMethod(pi.change, "pondering")
                        for pi in self.get_students()
                    ]
                )
                self.wait()
        self.play(
            Write(mid_words),
            self.teacher.change, "raise_right_hand"
        )
        self.change_student_modes(
            *["thinking"]*3,
            look_at_arg = mid_words
        )
        self.wait(3)

class LeibnizPatreonThanks(PatreonThanks):
    CONFIG = {
        "specific_patrons" : [
            "Ali Yahya",
            "Burt Humburg",
            "CrypticSwarm",
            "Erik Sundell",
            "Yana Chernobilsky",
            "Kaustuv DeBiswas",
            "Kathryn Schmiedicke",
            "Karan Bhargava",
            "Ankit Agarwal",
            "Yu Jun",
            "Dave Nicponski",
            "Damion Kistler",
            "Juan Benet",
            "Othman Alikhan",
            "Markus Persson",
            "Yoni Nazarathy",
            "Joseph John Cox",
            "Dan Buchoff",
            "Luc Ritchie",
            "Guido Gambardella",
            "Julian Pulgarin",
            "John Haley",
            "Jeff Linse",
            "Suraj Pratap",
            "Cooper Jones",
            "Ryan Dahl",
            "Ahmad Bamieh",
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
        ],
    }

class Sponsorship(PiCreatureScene):
    def construct(self):
        morty = self.pi_creature
        logo = SVGMobject(
            file_name = "remix_logo",
        )
        logo.set_height(1)
        logo.center()
        logo.set_stroke(width = 0)
        logo.set_fill(BLUE_D, 1)
        VGroup(*logo[6:]).set_color_by_gradient(BLUE_B, BLUE_E)
        logo.next_to(morty.get_corner(UP+LEFT), UP)

        url = TextMobject("www.remix.com")
        url.to_corner(UP+LEFT)
        rect = ScreenRectangle(height = 5)
        rect.next_to(url, DOWN, aligned_edge = LEFT)

        self.play(
            morty.change_mode, "raise_right_hand",
            LaggedStartMap(DrawBorderThenFill, logo, run_time = 3)
        )
        self.wait()
        self.play(
            ShowCreation(rect),
            logo.scale, 0.8,
            logo.to_corner, UP+RIGHT,
            morty.change, "happy"
        )
        self.wait()
        self.play(Write(url))
        self.wait(3)
        for mode in "confused", "pondering", "happy":
            self.play(morty.change_mode, mode)
            self.wait(3)

class Thumbnail(Scene):
    def construct(self):
        randy = Randolph()
        randy.set_height(5)
        body_copy = randy.body.copy()
        body_copy.set_stroke(YELLOW, width = 3)
        body_copy.set_fill(opacity = 0)
        self.add(randy)

        primes = [
            n for n in range(2, 1000)
            if all(n%k != 0 for k in list(range(2, n)))
        ]
        prime_mobs = VGroup()
        x_spacing = 1.7
        y_spacing = 1.5
        n_rows = 10
        n_cols = 8
        for i, prime in enumerate(primes[:n_rows*n_cols]):
            prime_mob = Integer(prime)
            prime_mob.scale(1.5)
            x = i%n_cols
            y = i//n_cols
            prime_mob.shift(x*x_spacing*RIGHT + y*y_spacing*DOWN)
            prime_mobs.add(prime_mob)
            prime_mob.set_color({
                -1 : YELLOW,
                0 : RED,
                1 : BLUE_C,
            }[chi_func(prime)])
        prime_mobs.center().to_edge(UP)
        for i in range(7):
            self.add(SurroundingRectangle(
                VGroup(*prime_mobs[n_cols*i:n_cols*(i+1)]),
                fill_opacity = 0.7,
                fill_color = BLACK,
                stroke_width = 0,
                buff = 0,
            ))
        self.add(prime_mobs)
        self.add(body_copy)












