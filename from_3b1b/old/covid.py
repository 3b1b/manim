from manimlib.imports import *
import scipy.stats


CASE_DATA = [
    9,
    15,
    30,
    40,
    56,
    66,
    84,
    102,
    131,
    159,
    173,
    186,
    190,
    221,
    248,
    278,
    330,
    354,
    382,
    461,
    481,
    526,
    587,
    608,
    697,
    781,
    896,
    999,
    1124,
    1212,
    1385,
    1715,
    2055,
    2429,
    2764,
    3323,
    4288,
    5364,
    6780,
    8555,
    10288,
    12742,
    14901,
    17865,
    21395,
    # 25404,
    # 29256,
    # 33627,
    # 38170,
    # 45421,
    # 53873,
]
SICKLY_GREEN = "#9BBD37"


class IntroducePlot(Scene):
    def construct(self):
        axes = self.get_axes()
        self.add(axes)

        # Dots
        dots = VGroup()
        for day, nc in zip(it.count(1), CASE_DATA):
            dot = Dot()
            dot.set_height(0.075)
            dot.x = day
            dot.y = nc
            dot.axes = axes
            dot.add_updater(lambda d: d.move_to(d.axes.c2p(d.x, d.y)))
            dots.add(dot)
        dots.set_color(YELLOW)

        # Rescale y axis
        origin = axes.c2p(0, 0)
        axes.y_axis.tick_marks.save_state()
        for tick in axes.y_axis.tick_marks:
            tick.match_width(axes.y_axis.tick_marks[0])
        axes.y_axis.add(
            axes.h_lines,
            axes.small_h_lines,
            axes.tiny_h_lines,
            axes.tiny_ticks,
        )
        axes.y_axis.stretch(25, 1, about_point=origin)
        dots.update()

        self.add(axes.small_y_labels)
        self.add(axes.tiny_y_labels)

        # Add title
        title = self.get_title(axes)
        self.add(title)

        # Introduce the data
        day = 10
        self.add(*dots[:day + 1])

        dot = Dot()
        dot.match_style(dots[day])
        dot.replace(dots[day])
        count = Integer(CASE_DATA[day])
        count.add_updater(lambda m: m.next_to(dot, UP))
        count.add_updater(lambda m: m.set_stroke(BLACK, 5, background=True))

        v_line = Line(DOWN, UP)
        v_line.set_stroke(YELLOW, 1)
        v_line.add_updater(
            lambda m: m.put_start_and_end_on(
                axes.c2p(
                    axes.x_axis.p2n(dot.get_center()),
                    0,
                ),
                dot.get_bottom(),
            )
        )

        self.add(dot)
        self.add(count)
        self.add(v_line)

        for new_day in range(day + 1, len(dots)):
            new_dot = dots[new_day]
            new_dot.update()
            line = Line(dot.get_center(), new_dot.get_center())
            line.set_stroke(PINK, 3)

            self.add(line, dot)
            self.play(
                dot.move_to, new_dot.get_center(),
                dot.set_color, RED,
                ChangeDecimalToValue(count, CASE_DATA[new_day]),
                ShowCreation(line),
            )
            line.rotate(PI)
            self.play(
                dot.set_color, YELLOW,
                Uncreate(line),
                run_time=0.5
            )
            self.add(dots[new_day])

            day = new_day

            if day == 27:
                self.add(
                    axes.y_axis, axes.tiny_y_labels, axes.tiny_h_lines, axes.tiny_ticks,
                    title
                )
                self.play(
                    axes.y_axis.stretch, 0.2, 1, {"about_point": origin},
                    VFadeOut(axes.tiny_y_labels),
                    VFadeOut(axes.tiny_h_lines),
                    VFadeOut(axes.tiny_ticks),
                    MaintainPositionRelativeTo(dot, dots[new_day]),
                    run_time=2,
                )
                self.add(axes, title, *dots[:new_day])
            if day == 36:
                self.add(axes.y_axis, axes.small_y_labels, axes.small_h_lines, title)
                self.play(
                    axes.y_axis.stretch, 0.2, 1, {"about_point": origin},
                    VFadeOut(axes.small_y_labels),
                    VFadeOut(axes.small_h_lines),
                    MaintainPositionRelativeTo(dot, dots[new_day]),
                    run_time=2,
                )
                self.add(axes, title, *dots[:new_day])

        count.add_background_rectangle()
        count.background_rectangle.stretch(1.1, 0)
        self.add(count)

        # Show multiplications
        last_label = VectorizedPoint(dots[25].get_center())
        last_line = VMobject()
        for d1, d2 in zip(dots[25:], dots[26:]):
            line = Line(
                d1.get_top(),
                d2.get_corner(UL),
                path_arc=-90 * DEGREES,
            )
            line.set_stroke(PINK, 2)

            label = VGroup(
                TexMobject("\\times"),
                DecimalNumber(
                    axes.y_axis.p2n(d2.get_center()) /
                    axes.y_axis.p2n(d1.get_center()),
                )
            )
            label.arrange(RIGHT, buff=SMALL_BUFF)
            label.set_height(0.25)
            label.next_to(line.point_from_proportion(0.5), UL, SMALL_BUFF)
            label.match_color(line)
            label.add_background_rectangle()
            label.save_state()
            label.move_to(last_label)
            label.set_opacity(0)

            self.play(
                ShowCreation(line),
                Restore(label),
                last_label.move_to, label.saved_state,
                VFadeOut(last_label),
                FadeOut(last_line),
            )
            last_line = line
            last_label = label
        self.wait()
        self.play(
            FadeOut(last_label),
            FadeOut(last_line),
        )

    #
    def get_title(self, axes):
        title = TextMobject(
            "Recorded COVID-19 cases\\\\outside mainland China",
            tex_to_color_map={"COVID-19": RED}
        )
        title.next_to(axes.c2p(0, 1e3), RIGHT, LARGE_BUFF)
        title.to_edge(UP)
        title.add_background_rectangle()
        return title

    def get_axes(self, width=12, height=6):
        n_cases = len(CASE_DATA)
        axes = Axes(
            x_min=0,
            x_max=n_cases,
            x_axis_config={
                "tick_frequency": 1,
                "include_tip": False,
            },
            y_min=0,
            y_max=25000,
            y_axis_config={
                "unit_size": 1 / 2500,
                "tick_frequency": 1000,
                "include_tip": False,
            }
        )
        axes.x_axis.set_width(
            width,
            stretch=True,
            about_point=axes.c2p(0, 0),
        )
        axes.y_axis.set_height(
            height,
            stretch=True,
            about_point=axes.c2p(0, 0),
        )
        axes.center()
        axes.to_edge(DOWN, buff=LARGE_BUFF)

        # Add dates
        text_pos_pairs = [
            ("Mar 6", 0),
            ("Feb 23", -12),
            ("Feb 12", -23),
            ("Feb 1", -34),
            ("Jan 22", -44),
        ]
        labels = VGroup()
        extra_ticks = VGroup()
        for text, pos in text_pos_pairs:
            label = TextMobject(text)
            label.set_height(0.2)
            label.rotate(45 * DEGREES)
            axis_point = axes.c2p(n_cases + pos, 0)
            label.move_to(axis_point, UR)
            label.shift(MED_SMALL_BUFF * DOWN)
            label.shift(SMALL_BUFF * RIGHT)
            labels.add(label)

            tick = Line(UP, DOWN)
            tick.set_stroke(GREEN, 3)
            tick.set_height(0.25)
            tick.move_to(axis_point)
            extra_ticks.add(tick)

        axes.x_labels = labels
        axes.extra_x_ticks = extra_ticks
        axes.add(labels, extra_ticks)

        # Adjust y ticks
        axes.y_axis.tick_marks.stretch(0.5, 0)
        axes.y_axis.tick_marks[0::5].stretch(2, 0)

        # Add y_axis_labels
        def get_y_labels(axes, y_values):
            labels = VGroup()
            for y in y_values:
                label = TextMobject(f"{y}k")
                label.set_height(0.25)
                tick = axes.y_axis.tick_marks[y]
                always(label.next_to, tick, LEFT, SMALL_BUFF)
                labels.add(label)
            return labels

        main_labels = get_y_labels(axes, range(5, 30, 5))
        axes.y_labels = main_labels
        axes.add(main_labels)
        axes.small_y_labels = get_y_labels(axes, range(1, 6))

        tiny_labels = VGroup()
        tiny_ticks = VGroup()
        for y in range(200, 1000, 200):
            tick = axes.y_axis.tick_marks[0].copy()
            point = axes.c2p(0, y)
            tick.move_to(point)
            label = Integer(y)
            label.set_height(0.25)
            always(label.next_to, tick, LEFT, SMALL_BUFF)
            tiny_labels.add(label)
            tiny_ticks.add(tick)

        axes.tiny_y_labels = tiny_labels
        axes.tiny_ticks = tiny_ticks

        # Horizontal lines
        axes.h_lines = VGroup()
        axes.small_h_lines = VGroup()
        axes.tiny_h_lines = VGroup()
        group_range_pairs = [
            (axes.h_lines, 5e3 * np.arange(1, 6)),
            (axes.small_h_lines, 1e3 * np.arange(1, 5)),
            (axes.tiny_h_lines, 200 * np.arange(1, 5)),
        ]
        for group, _range in group_range_pairs:
            for y in _range:
                group.add(
                    Line(
                        axes.c2p(0, y),
                        axes.c2p(n_cases, y),
                    )
                )
            group.set_stroke(WHITE, 1, opacity=0.5)

        return axes


class Thumbnail(IntroducePlot):
    def construct(self):
        axes = self.get_axes()
        self.add(axes)

        dots = VGroup()
        data = CASE_DATA
        data.append(25398)
        for day, nc in zip(it.count(1), CASE_DATA):
            dot = Dot()
            dot.set_height(0.2)
            dot.x = day
            dot.y = nc
            dot.axes = axes
            dot.add_updater(lambda d: d.move_to(d.axes.c2p(d.x, d.y)))
            dots.add(dot)
        dots.set_color(YELLOW)
        dots.set_submobject_colors_by_gradient(BLUE, GREEN, RED)

        self.add(dots)

        title = TextMobject("COVID-19")
        title.set_height(1)
        title.set_color(RED)
        title.to_edge(UP, buff=LARGE_BUFF)

        subtitle = TextMobject("and exponential growth")
        subtitle.match_width(title)
        subtitle.next_to(title, DOWN)

        # self.add(title)
        # self.add(subtitle)

        title = TextMobject("How is ", "COVID-19\\\\", "currently growing?")
        title[1].set_color(RED)
        title.set_height(2.5)
        title.to_edge(UP, buff=LARGE_BUFF)
        self.add(title)

        # self.remove(words)
        # words = TextMobject("Exponential growth")
        # words.move_to(ORIGIN, DL)
        # words.apply_function(
        #     lambda p: [
        #         p[0], p[1] + np.exp(0.2 * p[0]), p[2]
        #     ]
        # )
        # self.add(words)

        self.embed()


class IntroQuestion(Scene):
    def construct(self):
        questions = VGroup(
            TextMobject("What is exponential growth?"),
            TextMobject("Where does it come from?"),
            TextMobject("What does it imply?"),
            TextMobject("When does it stop?"),
        )
        questions.arrange(DOWN, buff=MED_LARGE_BUFF, aligned_edge=LEFT)

        for question in questions:
            self.play(FadeIn(question, RIGHT))
            self.wait()
        self.play(LaggedStartMap(
            FadeOutAndShift, questions,
            lambda m: (m, DOWN),
        ))


class ViralSpreadModel(Scene):
    CONFIG = {
        "num_neighbors": 5,
        "infection_probability": 0.3,
        "random_seed": 1,
    }

    def construct(self):
        # Init population
        randys = self.get_randys()
        self.add(*randys)

        # Show the sicko
        self.show_patient0(randys)

        # Repeatedly spread
        for x in range(20):
            self.spread_infection(randys)

    def get_randys(self):
        randys = VGroup(*[
            Randolph()
            for x in range(150)
        ])
        for randy in randys:
            randy.set_height(0.5)
        randys.arrange_in_grid(10, 15, buff=0.5)
        randys.set_height(FRAME_HEIGHT - 1)

        for i in range(0, 10, 2):
            randys[i * 15:(i + 1) * 15].shift(0.25 * RIGHT)
        for randy in randys:
            randy.shift(0.2 * random.random() * RIGHT)
            randy.shift(0.2 * random.random() * UP)
            randy.infected = False
        randys.center()
        return randys

    def show_patient0(self, randys):
        patient0 = random.choice(randys)
        patient0.infected = True

        circle = Circle()
        circle.set_stroke(SICKLY_GREEN)
        circle.replace(patient0)
        circle.scale(1.5)
        self.play(
            patient0.change, "sick",
            patient0.set_color, SICKLY_GREEN,
            ShowCreationThenFadeOut(circle),
        )

    def spread_infection(self, randys):
        E = self.num_neighbors
        inf_p = self.infection_probability

        cough_anims = []
        new_infection_anims = []

        for randy in randys:
            if randy.infected:
                cough_anims.append(Flash(
                    randy,
                    color=SICKLY_GREEN,
                    num_lines=16,
                    line_stroke_width=1,
                    flash_radius=0.5,
                    line_length=0.1,
                ))
        random.shuffle(cough_anims)
        self.play(LaggedStart(
            *cough_anims,
            run_time=1,
            lag_ratio=1 / len(cough_anims),
        ))

        newly_infected = []
        for randy in randys:
            if randy.infected:
                distances = [
                    get_norm(r2.get_center() - randy.get_center())
                    for r2 in randys
                ]
                for i in np.argsort(distances)[1:E + 1]:
                    r2 = randys[i]
                    if random.random() < inf_p and not r2.infected and r2 not in newly_infected:
                        newly_infected.append(r2)
                        r2.generate_target()
                        r2.target.change("sick")
                        r2.target.set_color(SICKLY_GREEN)
                        new_infection_anims.append(MoveToTarget(r2))
        random.shuffle(new_infection_anims)
        self.play(LaggedStart(*new_infection_anims, run_time=1))

        for randy in newly_infected:
            randy.infected = True


class GrowthEquation(Scene):
    def construct(self):
        # Add labels
        N_label = TextMobject("$N_d$", " = Number of cases on a given day", )
        E_label = TextMobject("$E$", " = Average number of people someone infected is exposed to each day")
        p_label = TextMobject("$p$", " = Probability of each exposure becoming an infection")

        N_label[0].set_color(YELLOW)
        E_label[0].set_color(BLUE)
        p_label[0].set_color(TEAL)

        labels = VGroup(
            N_label,
            E_label,
            p_label
        )
        labels.arrange(DOWN, buff=MED_LARGE_BUFF, aligned_edge=LEFT)
        labels.set_width(FRAME_WIDTH - 1)
        labels.to_edge(UP)

        for label in labels:
            self.play(FadeInFromDown(label))
            self.wait()

        delta_N = TexMobject("\\Delta", "N_d")
        delta_N.set_color(YELLOW)
        eq = TexMobject("=")
        eq.center()
        delta_N.next_to(eq, LEFT)

        delta_N_brace = Brace(delta_N, DOWN)
        delta_N_text = delta_N_brace.get_text("Change over a day")

        nep = TexMobject("E", "\\cdot", "p", "\\cdot", "N_d")
        nep[4].match_color(N_label[0])
        nep[0].match_color(E_label[0])
        nep[2].match_color(p_label[0])
        nep.next_to(eq, RIGHT)

        self.play(FadeIn(delta_N), FadeIn(eq))
        self.play(
            GrowFromCenter(delta_N_brace),
            FadeIn(delta_N_text, 0.5 * UP),
        )
        self.wait()
        self.play(LaggedStart(
            TransformFromCopy(N_label[0], nep[4]),
            TransformFromCopy(E_label[0], nep[0]),
            TransformFromCopy(p_label[0], nep[2]),
            FadeIn(nep[1]),
            FadeIn(nep[3]),
            lag_ratio=0.2,
            run_time=2,
        ))
        self.wait()
        self.play(ShowCreationThenFadeAround(
            nep[-1],
            surrounding_rectangle_config={"color": RED},
        ))

        # Recursive equation
        lhs = TexMobject("N_{d + 1}", "=")
        lhs[0].set_color(YELLOW)
        lhs.move_to(eq, RIGHT)
        lhs.shift(DOWN)

        rhs = VGroup(
            nep[-1].copy(),
            TexMobject("+"),
            nep.copy(),
        )
        rhs.arrange(RIGHT)
        rhs.next_to(lhs, RIGHT)

        self.play(
            FadeOut(delta_N_brace),
            FadeOut(delta_N_text),
            FadeIn(lhs, UP),
        )
        self.play(FadeIn(rhs[:2]))
        self.play(TransformFromCopy(nep, rhs[2]))
        self.wait()

        alt_rhs = TexMobject(
            "(", "1", "+", "E", "\\cdot", "p", ")", "N_d",
            tex_to_color_map={
                "E": BLUE,
                "p": TEAL,
                "N_d": YELLOW,
            }
        )
        new_lhs = lhs.copy()
        new_lhs.shift(DOWN)
        alt_rhs.next_to(new_lhs, RIGHT)
        self.play(TransformFromCopy(lhs, new_lhs))

        rhs.unlock_triangulation()
        self.play(
            TransformFromCopy(rhs[0], alt_rhs[7].copy()),
            TransformFromCopy(rhs[2][4], alt_rhs[7]),
        )
        self.play(
            TransformFromCopy(rhs[1][0], alt_rhs[2]),
            TransformFromCopy(rhs[2][0], alt_rhs[3]),
            TransformFromCopy(rhs[2][1], alt_rhs[4]),
            TransformFromCopy(rhs[2][2], alt_rhs[5]),
            TransformFromCopy(rhs[2][3], alt_rhs[6]),
            FadeIn(alt_rhs[0]),
            FadeIn(alt_rhs[1]),
        )
        self.wait()

        # Comment on factor
        brace = Brace(alt_rhs[:7], DOWN)
        text = TextMobject("For example, ", "1.15")
        text.next_to(brace, DOWN)
        self.play(
            GrowFromCenter(brace),
            FadeIn(text, 0.5 * UP)
        )
        self.wait()

        # Show exponential
        eq_group = VGroup(
            delta_N, eq, nep,
            lhs, rhs,
            new_lhs, alt_rhs,
            brace,
            text,
        )
        self.clear()
        self.add(labels, eq_group)

        self.play(ShowCreationThenFadeAround(
            VGroup(delta_N, eq, nep),
            surrounding_rectangle_config={"color": RED},
        ))
        self.play(ShowCreationThenFadeAround(
            VGroup(new_lhs, alt_rhs, brace, text),
            surrounding_rectangle_config={"color": RED},
        ))
        self.wait()
        self.play(eq_group.to_edge, LEFT, LARGE_BUFF)

        exp_eq = TexMobject(
            "N_d = (1 + E \\cdot p)^{d} \\cdot N_0",
            tex_to_color_map={
                "N_d": YELLOW,
                "E": BLUE,
                "p": TEAL,
                "{d}": YELLOW,
                "N_0": YELLOW,
            }
        )
        exp_eq.next_to(alt_rhs, RIGHT, buff=3)
        arrow = Arrow(alt_rhs.get_right(), exp_eq.get_left())

        self.play(
            GrowArrow(arrow),
            FadeIn(exp_eq, 2 * LEFT)
        )
        self.wait()

        # Discuss factor in front of N
        ep = nep[:3]
        ep_rect = SurroundingRectangle(ep)
        ep_rect.set_stroke(RED, 2)

        ep_label = TextMobject("This factor will decrease")
        ep_label.next_to(ep_rect, UP, aligned_edge=LEFT)
        ep_label.set_color(RED)

        self.play(
            ShowCreation(ep_rect),
            FadeIn(ep_label, lag_ratio=0.1),
        )
        self.wait()
        self.play(
            FadeOut(ep_rect),
            FadeOut(ep_label),
        )

        # Add carrying capacity factor to p
        p_factors = TexMobject(
            "\\left(1 - {N_d \\over \\text{pop. size}} \\right)",
            tex_to_color_map={"N_d": YELLOW},
        )
        p_factors.next_to(nep, RIGHT, buff=3)
        p_factors_rect = SurroundingRectangle(p_factors)
        p_factors_rect.set_stroke(TEAL, 2)
        p_arrow = Arrow(
            p_factors_rect.get_corner(UL),
            nep[2].get_top(),
            path_arc=75 * DEGREES,
            color=TEAL,
        )

        self.play(
            ShowCreation(p_factors_rect),
            ShowCreation(p_arrow)
        )
        self.wait()
        self.play(Write(p_factors))
        self.wait()
        self.play(
            FadeOut(p_factors),
            FadeOut(p_arrow),
            FadeOut(p_factors_rect),
        )

        # Ask about ep shrinking
        ep_question = TextMobject("What makes this shrink?")
        ep_question.set_color(RED)
        ep_question.next_to(ep_rect, UP, aligned_edge=LEFT)

        E_line = Underline(E_label)
        E_line.set_color(BLUE)
        p_line = Underline(p_label)
        p_line.set_color(TEAL)

        self.play(
            ShowCreation(ep_rect),
            FadeIn(ep_question, LEFT)
        )
        self.wait()
        for line in E_line, p_line:
            self.play(ShowCreation(line))
            self.wait()
            self.play(FadeOut(line))
        self.wait()

        # Show alternate projections
        ep_value = DecimalNumber(0.15)
        ep_value.next_to(ep_rect, UP)

        self.play(
            FadeOut(ep_question),
            FadeIn(ep_value),
            FadeOut(text[0]),
            text[1].next_to, brace, DOWN,
        )

        eq1 = TexMobject("(", "1.15", ")", "^{61}", "\\cdot", "21{,}000", "=")
        eq2 = TexMobject("(", "1.05", ")", "^{61}", "\\cdot", "21{,}000", "=")
        eq1_rhs = Integer((1.15**61) * (21000))
        eq2_rhs = Integer((1.05**61) * (21000))

        for eq, rhs in (eq1, eq1_rhs), (eq2, eq2_rhs):
            eq[1].set_color(RED)
            eq.move_to(nep)
            eq.to_edge(RIGHT, buff=3)
            rhs.next_to(eq, RIGHT)
            rhs.align_to(eq[-2], UP)

        self.play(FadeIn(eq1))
        for tex in ["21{,}000", "61"]:
            self.play(ShowCreationThenFadeOut(
                Underline(
                    eq1.get_part_by_tex(tex),
                    stroke_color=YELLOW,
                    stroke_width=2,
                    buff=SMALL_BUFF,
                ),
                run_time=2,
            ))
        value = eq1_rhs.get_value()
        eq1_rhs.set_value(0)
        self.play(ChangeDecimalToValue(eq1_rhs, value))
        self.wait()
        eq1.add(eq1_rhs)
        self.play(
            eq1.shift, DOWN,
            FadeIn(eq2),
        )

        new_text = TextMobject("1.05")
        new_text.move_to(text[1])
        self.play(
            ChangeDecimalToValue(ep_value, 0.05),
            FadeOut(text[1]),
            FadeIn(new_text),
        )

        self.wait()

        eq2_rhs.align_to(eq1_rhs, RIGHT)
        value = eq2_rhs.get_value()
        eq2_rhs.set_value(0)
        self.play(ChangeDecimalToValue(eq2_rhs, value))
        self.wait()

        # Pi creature quote
        morty = Mortimer()
        morty.set_height(1)
        morty.next_to(eq2_rhs, UP)
        bubble = SpeechBubble(
            direction=RIGHT,
            height=2.5,
            width=5,
        )
        bubble.next_to(morty, UL, buff=0)
        bubble.write("The only thing to fear\\\\is the lack of fear itself.")

        self.add(morty)
        self.add(bubble)
        self.add(bubble.content)

        self.play(
            labels.set_opacity, 0.5,
            VFadeIn(morty),
            morty.change, "speaking",
            FadeIn(bubble),
            Write(bubble.content),
        )
        self.play(Blink(morty))
        self.wait()


class RescaleToLogarithmic(IntroducePlot):
    def construct(self):
        # Setup axes
        axes = self.get_axes(width=10)
        title = self.get_title(axes)

        dots = VGroup()
        for day, nc in zip(it.count(1), CASE_DATA):
            dot = Dot()
            dot.set_height(0.075)
            dot.move_to(axes.c2p(day, nc))
            dots.add(dot)
        dots.set_color(YELLOW)

        self.add(axes, axes.h_lines, dots, title)

        # Create logarithmic y axis
        log_y_axis = NumberLine(
            x_min=0,
            x_max=9,
        )
        log_y_axis.rotate(90 * DEGREES)
        log_y_axis.move_to(axes.c2p(0, 0), DOWN)

        labels_text = [
            "10", "100",
            "1k", "10k", "100k",
            "1M", "10M", "100M",
            "1B",
        ]
        log_y_labels = VGroup()
        for text, tick in zip(labels_text, log_y_axis.tick_marks[1:]):
            label = TextMobject(text)
            label.set_height(0.25)
            always(label.next_to, tick, LEFT, SMALL_BUFF)
            log_y_labels.add(label)

        # Animate the rescaling to a logarithmic plot
        logarithm_title = TextMobject("(Logarithmic scale)")
        logarithm_title.set_color(TEAL)
        logarithm_title.next_to(title, DOWN)
        logarithm_title.add_background_rectangle()

        def scale_logarithmically(p):
            result = np.array(p)
            y = axes.y_axis.p2n(p)
            result[1] = log_y_axis.n2p(np.log10(y))[1]
            return result

        log_h_lines = VGroup()
        for exponent in range(0, 9):
            for mult in range(2, 12, 2):
                y = mult * 10**exponent
                line = Line(
                    axes.c2p(0, y),
                    axes.c2p(axes.x_max, y),
                )
                log_h_lines.add(line)
        log_h_lines.set_stroke(WHITE, 0.5, opacity=0.5)
        log_h_lines[4::5].set_stroke(WHITE, 1, opacity=1)

        movers = [dots, axes.y_axis.tick_marks, axes.h_lines, log_h_lines]
        for group in movers:
            group.generate_target()
            for mob in group.target:
                mob.move_to(scale_logarithmically(mob.get_center()))

        log_y_labels.suspend_updating()
        log_y_labels.save_state()
        for exponent, label in zip(it.count(1), log_y_labels):
            label.set_y(axes.y_axis.n2p(10**exponent)[1])
            label.set_opacity(0)

        self.add(log_y_axis)
        log_y_axis.save_state()
        log_y_axis.tick_marks.set_opacity(0)
        log_h_lines.set_opacity(0)
        self.wait()
        self.add(log_h_lines, title, logarithm_title)
        self.play(
            MoveToTarget(dots),
            MoveToTarget(axes.y_axis.tick_marks),
            MoveToTarget(axes.h_lines),
            MoveToTarget(log_h_lines),
            VFadeOut(axes.y_labels),
            VFadeOut(axes.y_axis.tick_marks),
            VFadeOut(axes.h_lines),
            Restore(log_y_labels),
            FadeIn(logarithm_title),
            run_time=2,
        )
        self.play(Restore(log_y_axis))
        self.wait()

        # Walk up y axis
        brace = Brace(
            log_y_axis.tick_marks[1:3],
            RIGHT,
            buff=SMALL_BUFF,
        )
        brace_label = brace.get_tex(
            "\\times 10",
            buff=SMALL_BUFF
        )
        VGroup(brace, brace_label).set_color(TEAL)
        brace_label.set_stroke(BLACK, 8, background=True)

        self.play(
            GrowFromCenter(brace),
            FadeIn(brace_label)
        )
        brace.add(brace_label)
        for i in range(2, 5):
            self.play(
                brace.next_to,
                log_y_axis.tick_marks[i:i + 2],
                {"buff": SMALL_BUFF}
            )
            self.wait(0.5)
        self.play(FadeOut(brace))
        self.wait()

        # Show order of magnitude jumps
        remove_anims = []
        for i, j in [(7, 27), (27, 40)]:
            line = Line(dots[i].get_center(), dots[j].get_center())
            rect = Rectangle()
            rect.set_fill(TEAL, 0.5)
            rect.set_stroke(width=0)
            rect.replace(line, stretch=True)
            label = TextMobject(f"{j - i} days")
            label.next_to(rect, UP, SMALL_BUFF)
            label.set_color(TEAL)

            rect.save_state()
            rect.stretch(0, 0, about_edge=LEFT)
            self.play(
                Restore(rect),
                FadeIn(label, LEFT)
            )
            self.wait()

            remove_anims += [
                ApplyMethod(
                    rect.stretch, 0, 0, {"about_edge": RIGHT},
                    remover=True,
                ),
                FadeOut(label, RIGHT),
            ]
        self.wait()

        # Linear regression
        def c2p(x, y):
            xp = axes.x_axis.n2p(x)
            yp = log_y_axis.n2p(np.log10(y))
            return np.array([xp[0], yp[1], 0])

        reg = scipy.stats.linregress(
            range(7, len(CASE_DATA)),
            np.log10(CASE_DATA[7:])
        )
        x_max = axes.x_max
        axes.y_axis = log_y_axis
        reg_line = Line(
            c2p(0, 10**reg.intercept),
            c2p(x_max, 10**(reg.intercept + reg.slope * x_max)),
        )
        reg_line.set_stroke(TEAL, 3)

        self.add(reg_line, dots)
        dots.set_stroke(BLACK, 3, background=True)
        self.play(
            LaggedStart(*remove_anims),
            ShowCreation(reg_line)
        )

        # Describe linear regression
        reg_label = TextMobject("Linear regression")
        reg_label.move_to(c2p(25, 10), DOWN)
        reg_arrows = VGroup()
        for prop in [0.4, 0.6, 0.5]:
            reg_arrows.add(
                Arrow(
                    reg_label.get_top(),
                    reg_line.point_from_proportion(prop),
                    buff=SMALL_BUFF,
                )
            )

        reg_arrow = reg_arrows[0].copy()
        self.play(
            Write(reg_label, run_time=1),
            Transform(reg_arrow, reg_arrows[1], run_time=2),
            VFadeIn(reg_arrow),
        )
        self.play(Transform(reg_arrow, reg_arrows[2]))
        self.wait()

        # Label slope
        slope_label = TextMobject("$\\times 10$ every $16$ days (on average)")
        slope_label.set_color(BLUE)
        slope_label.set_stroke(BLACK, 8, background=True)
        slope_label.rotate(reg_line.get_angle())
        slope_label.move_to(reg_line.get_center())
        slope_label.shift(MED_LARGE_BUFF * UP)

        self.play(FadeIn(slope_label, lag_ratio=0.1))
        self.wait()

        # R^2 label
        R2_label = VGroup(
            TexMobject("R^2 = "),
            DecimalNumber(0, num_decimal_places=3)
        )
        R2_label.arrange(RIGHT, aligned_edge=DOWN)
        R2_label.next_to(reg_label[0][-1], RIGHT, LARGE_BUFF, aligned_edge=DOWN)

        self.play(
            ChangeDecimalToValue(R2_label[1], reg.rvalue**2, run_time=2),
            UpdateFromAlphaFunc(
                R2_label,
                lambda m, a: m.set_opacity(a),
            )
        )
        self.wait()

        rect = SurroundingRectangle(R2_label, buff=0.15)
        rect.set_stroke(YELLOW, 3)
        rect.set_fill(BLACK, 0)
        self.add(rect, R2_label)
        self.play(ShowCreation(rect))
        self.play(
            rect.set_stroke, WHITE, 2,
            rect.set_fill, GREY_E, 1,
        )
        self.wait()
        self.play(
            FadeOut(rect),
            FadeOut(R2_label),
            FadeOut(reg_label),
            FadeOut(reg_arrow),
        )

        # Zoom out
        extended_x_axis = NumberLine(
            x_min=axes.x_axis.x_max,
            x_max=axes.x_axis.x_max + 90,
            unit_size=get_norm(
                axes.x_axis.n2p(1) -
                axes.x_axis.n2p(0)
            ),
            numbers_with_elongated_ticks=[],
        )
        extended_x_axis.move_to(axes.x_axis.get_right(), LEFT)
        self.play(
            self.camera.frame.scale, 2, {"about_edge": DL},
            self.camera.frame.shift, 2.5 * DOWN + RIGHT,
            log_h_lines.stretch, 3, 0, {"about_edge": LEFT},
            ShowCreation(extended_x_axis, rate_func=squish_rate_func(smooth, 0.5, 1)),
            run_time=3,
        )
        self.play(
            reg_line.scale, 3, {"about_point": reg_line.get_start()}
        )
        self.wait()

        # Show future projections
        target_ys = [1e6, 1e7, 1e8, 1e9]
        last_point = dots[-1].get_center()
        last_label = None
        last_rect = None

        date_labels_text = [
            "Apr 5",
            "Apr 22",
            "May 9",
            "May 26",
        ]

        for target_y, date_label_text in zip(target_ys, date_labels_text):
            log_y = np.log10(target_y)
            x = (log_y - reg.intercept) / reg.slope
            line = Line(last_point, c2p(x, target_y))
            rect = Rectangle().replace(line, stretch=True)
            rect.set_stroke(width=0)
            rect.set_fill(TEAL, 0.5)
            label = TextMobject(f"{int(x) - axes.x_max} days")
            label.scale(1.5)
            label.next_to(rect, UP, SMALL_BUFF)

            date_label = TextMobject(date_label_text)
            date_label.set_height(0.25)
            date_label.rotate(45 * DEGREES)
            axis_point = axes.c2p(int(x), 0)
            date_label.move_to(axis_point, UR)
            date_label.shift(MED_SMALL_BUFF * DOWN)
            date_label.shift(SMALL_BUFF * RIGHT)

            v_line = DashedLine(
                axes.c2p(x, 0),
                c2p(x, target_y),
            )
            v_line.set_stroke(WHITE, 2)

            if target_y is target_ys[-1]:
                self.play(self.camera.frame.scale, 1.1, {"about_edge": LEFT})

            if last_label:
                last_label.unlock_triangulation()
                self.play(
                    ReplacementTransform(last_label, label),
                    ReplacementTransform(last_rect, rect),
                )
            else:
                rect.save_state()
                rect.stretch(0, 0, about_edge=LEFT)
                self.play(Restore(rect), FadeIn(label, LEFT))
            self.wait()

            self.play(
                ShowCreation(v_line),
                FadeIn(date_label),
            )

            last_label = label
            last_rect = rect

        self.wait()
        self.play(
            FadeOut(last_label, RIGHT),
            ApplyMethod(
                last_rect.stretch, 0, 0, {"about_edge": RIGHT},
                remover=True
            ),
        )

        # Show alternate petering out possibilities
        def get_dots_along_curve(curve):
            x_min = int(axes.x_axis.p2n(curve.get_start()))
            x_max = int(axes.x_axis.p2n(curve.get_end()))
            result = VGroup()
            for x in range(x_min, x_max):
                prop = binary_search(
                    lambda p: axes.x_axis.p2n(
                        curve.point_from_proportion(p),
                    ),
                    x, 0, 1,
                )
                prop = prop or 0
                point = curve.point_from_proportion(prop)
                dot = Dot(point)
                dot.shift(0.02 * (random.random() - 0.5))
                dot.set_height(0.075)
                dot.set_color(RED)
                result.add(dot)
            dots.remove(dots[0])
            return result

        def get_point_from_y(y):
            log_y = np.log10(y)
            x = (log_y - reg.intercept) / reg.slope
            return c2p(x, 10**log_y)

        p100k = get_point_from_y(1e5)
        p100M = get_point_from_y(1e8)
        curve1 = VMobject()
        curve1.append_points([
            dots[-1].get_center(),
            p100k,
            p100k + 5 * RIGHT,
        ])
        curve2 = VMobject()
        curve2.append_points([
            dots[-1].get_center(),
            p100M,
            p100M + 5 * RIGHT + 0.25 * UP,
        ])

        proj_dots1 = get_dots_along_curve(curve1)
        proj_dots2 = get_dots_along_curve(curve2)

        for proj_dots in [proj_dots1, proj_dots2]:
            self.play(FadeIn(proj_dots, lag_ratio=0.1))
            self.wait()
            self.play(FadeOut(proj_dots, lag_ratio=0.1))


class LinRegNote(Scene):
    def construct(self):
        text = TextMobject("(Starting from when\\\\there were 100 cases)")
        text.set_stroke(BLACK, 8, background=True)
        self.add(text)


class CompareCountries(Scene):
    def construct(self):
        # Introduce
        sk_flag = ImageMobject(os.path.join("flags", "kr"))
        au_flag = ImageMobject(os.path.join("flags", "au"))
        flags = Group(sk_flag, au_flag)
        flags.set_height(3)
        flags.arrange(RIGHT, buff=LARGE_BUFF)
        flags.next_to(ORIGIN, UP)

        labels = VGroup()
        case_numbers = [6593, 64]
        for flag, cn in zip(flags, case_numbers):
            label = VGroup(Integer(cn), TextMobject("cases"))
            label.arrange(RIGHT, buff=MED_SMALL_BUFF)
            label[1].align_to(label[0][-1], DOWN)
            label.scale(1.5)
            label.next_to(flag, DOWN, MED_LARGE_BUFF)
            label[0].set_value(0)
            labels.add(label)

        self.play(LaggedStartMap(FadeInFromDown, flags, lag_ratio=0.25))
        self.play(
            ChangeDecimalToValue(labels[0][0], case_numbers[0]),
            ChangeDecimalToValue(labels[1][0], case_numbers[1]),
            UpdateFromAlphaFunc(
                labels,
                lambda m, a: m.set_opacity(a),
            )
        )
        self.wait()

        # Compare
        arrow = Arrow(
            labels[1][0].get_bottom(),
            labels[0][0].get_bottom(),
            path_arc=-90 * DEGREES,
        )
        arrow_label = TextMobject("100x better")
        arrow_label.set_color(YELLOW)
        arrow_label.next_to(arrow, DOWN)

        alt_arrow_label = TextMobject("1 month behind")
        alt_arrow_label.set_color(RED)
        alt_arrow_label.next_to(arrow, DOWN)

        self.play(ShowCreation(arrow))
        self.play(FadeIn(arrow_label, 0.5 * UP))
        self.wait(2)
        self.play(
            FadeIn(alt_arrow_label, 0.5 * UP),
            FadeOut(arrow_label, 0.5 * DOWN),
        )
        self.wait(2)


class SARSvs1918(Scene):
    def construct(self):
        titles = VGroup(
            TextMobject("2002 SARS outbreak"),
            TextMobject("1918 Spanish flu"),
        )
        images = Group(
            ImageMobject("sars_icon"),
            ImageMobject("spanish_flu"),
        )
        for title, vect, color, image in zip(titles, [LEFT, RIGHT], [YELLOW, RED], images):
            image.set_height(4)
            image.move_to(vect * FRAME_WIDTH / 4)
            image.to_edge(UP)
            title.scale(1.25)
            title.next_to(image, DOWN, MED_LARGE_BUFF)
            title.set_color(color)
            title.underline = Underline(title)
            title.underline.set_stroke(WHITE, 1)
            title.add_to_back(title.underline)

        titles[1].underline.match_y(titles[0].underline)

        n_cases_labels = VGroup(
            TextMobject("8,096 cases"),
            TextMobject("$\\sim$513{,}000{,}000 cases"),
        )

        for n_cases_label, title in zip(n_cases_labels, titles):
            n_cases_label.scale(1.25)
            n_cases_label.next_to(title, DOWN, MED_LARGE_BUFF)

        for image, title, label in zip(images, titles, n_cases_labels):
            self.play(
                FadeIn(image, DOWN),
                Write(title),
                run_time=1,
            )
            self.play(FadeIn(label, UP))
            self.wait()


class ViralSpreadModelWithShuffling(ViralSpreadModel):
    def construct(self):
        # Init population
        randys = self.get_randys()
        self.add(*randys)

        # Show the sicko
        self.show_patient0(randys)

        # Repeatedly spread
        for x in range(15):
            self.spread_infection(randys)
            self.shuffle_randys(randys)

    def shuffle_randys(self, randys):
        indices = list(range(len(randys)))
        np.random.shuffle(indices)

        anims = []
        for i, randy in zip(indices, randys):
            randy.generate_target()
            randy.target.move_to(randys[i])
            anims.append(MoveToTarget(
                randy, path_arc=30 * DEGREES,
            ))

        self.play(LaggedStart(
            *anims,
            lag_ratio=1 / len(randys),
            run_time=3
        ))


class SneezingOnNeighbors(Scene):
    def construct(self):
        randys = VGroup(*[PiCreature() for x in range(3)])
        randys.set_height(1)
        randys.arrange(RIGHT)

        self.add(randys)
        self.play(
            randys[1].change, "sick",
            randys[1].set_color, SICKLY_GREEN,
        )
        self.play(
            Flash(
                randys[1],
                color=SICKLY_GREEN,
                flash_radius=0.8,
            ),
            randys[0].change, "sassy", randys[1],
            randys[2].change, "angry", randys[1],
        )
        self.play(
            randys[0].change, "sick",
            randys[0].set_color, SICKLY_GREEN,
            randys[2].change, "sick",
            randys[2].set_color, SICKLY_GREEN,
        )
        self.play(
            Flash(
                randys[1],
                color=SICKLY_GREEN,
                flash_radius=0.8,
            )
        )
        self.play(
            randys[0].change, "sad", randys[1],
            randys[2].change, "tired", randys[1],
        )
        self.play(
            Flash(
                randys[1],
                color=SICKLY_GREEN,
                flash_radius=0.8,
            )
        )
        self.play(
            randys[0].change, "angry", randys[1],
            randys[2].change, "angry", randys[1],
        )
        self.wait()


class ViralSpreadModelWithClusters(ViralSpreadModel):
    def construct(self):
        randys = self.get_randys()
        self.add(*randys)
        self.show_patient0(randys)

        for x in range(6):
            self.spread_infection(randys)

    def get_randys(self):
        cluster = VGroup(*[Randolph() for x in range(16)])
        cluster.arrange_in_grid(4, 4)
        cluster.set_height(1)
        cluster.space_out_submobjects(1.3)

        clusters = VGroup(*[cluster.copy() for x in range(12)])
        clusters.arrange_in_grid(3, 4, buff=LARGE_BUFF)
        clusters.set_height(FRAME_HEIGHT - 1)

        for cluster in clusters:
            for randy in cluster:
                randy.infected = False

        self.add(clusters)

        self.clusters = clusters
        return VGroup(*it.chain(*clusters))


class ViralSpreadModelWithClustersAndTravel(ViralSpreadModelWithClusters):
    CONFIG = {
        "random_seed": 2,
    }

    def construct(self):
        randys = self.get_randys()
        self.add(*randys)
        self.show_patient0(randys)

        for x in range(20):
            self.spread_infection(randys)
            self.travel_between_clusters()
            self.update_frame(ignore_skipping=True)

    def travel_between_clusters(self):
        reps = VGroup(*[
            random.choice(cluster)
            for cluster in self.clusters
        ])
        targets = list(reps)
        random.shuffle(targets)

        anims = []
        for rep, target in zip(reps, targets):
            rep.generate_target()
            rep.target.move_to(target)
            anims.append(MoveToTarget(
                rep,
                path_arc=30 * DEGREES,
            ))
        self.play(LaggedStart(*anims, run_time=3))


class ShowLogisticCurve(Scene):
    def construct(self):
        # Init axes
        axes = self.get_axes()
        self.add(axes)

        # Add ODE
        ode = TexMobject(
            "{dN \\over dt} =",
            "c",
            "\\left(1 - {N \\over \\text{pop.}}\\right)",
            "N",
            tex_to_color_map={"N": YELLOW}
        )
        ode.set_height(0.75)
        ode.center()
        ode.to_edge(RIGHT)
        ode.shift(1.5 * UP)
        self.add(ode)

        # Show curve
        curve = axes.get_graph(
            lambda x: 8 * smooth(x / 10) + 0.2,
        )
        curve.set_stroke(YELLOW, 3)

        curve_title = TextMobject("Logistic curve")
        curve_title.set_height(0.75)
        curve_title.next_to(curve.get_end(), UL)

        self.play(ShowCreation(curve, run_time=3))
        self.play(FadeIn(curve_title, lag_ratio=0.1))
        self.wait()

        # Early part
        line = Line(
            curve.point_from_proportion(0),
            curve.point_from_proportion(0.25),
        )
        rect = Rectangle()
        rect.set_stroke(width=0)
        rect.set_fill(TEAL, 0.5)
        rect.replace(line, stretch=True)

        exp_curve = axes.get_graph(
            lambda x: 0.15 * np.exp(0.68 * x)
        )
        exp_curve.set_stroke(RED, 3)

        rect.save_state()
        rect.stretch(0, 0, about_edge=LEFT)
        self.play(Restore(rect))
        self.play(ShowCreation(exp_curve, run_time=4))

        # Show capacity
        line = DashedLine(
            axes.c2p(0, 8.2),
            axes.c2p(axes.x_max, 8.2),
        )
        line.set_stroke(BLUE, 2)

        self.play(ShowCreation(line))
        self.wait()
        self.play(FadeOut(rect), FadeOut(exp_curve))

        # Show inflection point
        infl_point = axes.input_to_graph_point(5, curve)
        infl_dot = Dot(infl_point)
        infl_dot.set_stroke(WHITE, 3)

        curve_up_part = curve.copy()
        curve_up_part.pointwise_become_partial(curve, 0, 0.4)
        curve_up_part.set_stroke(GREEN)
        curve_down_part = curve.copy()
        curve_down_part.pointwise_become_partial(curve, 0.4, 1)
        curve_down_part.set_stroke(RED)
        for part in curve_up_part, curve_down_part:
            part.save_state()
            part.stretch(0, 1)
            part.set_y(axes.c2p(0, 0)[1])

        pre_dot = curve.copy()
        pre_dot.pointwise_become_partial(curve, 0.375, 0.425)
        pre_dot.unlock_triangulation()

        infl_name = TextMobject("Inflection point")
        infl_name.next_to(infl_dot, LEFT)

        self.play(ReplacementTransform(pre_dot, infl_dot, path_arc=90 * DEGREES))
        self.add(curve_up_part, infl_dot)
        self.play(Restore(curve_up_part))
        self.add(curve_down_part, infl_dot)
        self.play(Restore(curve_down_part))
        self.wait()
        self.play(Write(infl_name, run_time=1))
        self.wait()

        # Show tangent line
        x_tracker = ValueTracker(0)
        tan_line = Line(LEFT, RIGHT)
        tan_line.set_width(5)
        tan_line.set_stroke(YELLOW, 2)

        def update_tan_line(line):
            x1 = x_tracker.get_value()
            x2 = x1 + 0.001
            p1 = axes.input_to_graph_point(x1, curve)
            p2 = axes.input_to_graph_point(x2, curve)
            angle = angle_of_vector(p2 - p1)
            line.rotate(angle - line.get_angle())
            line.move_to(p1)

        tan_line.add_updater(update_tan_line)

        dot = Dot()
        dot.scale(0.75)
        dot.set_fill(BLUE, 0.75)
        dot.add_updater(
            lambda m: m.move_to(axes.input_to_graph_point(
                x_tracker.get_value(), curve
            ))
        )

        self.play(
            ShowCreation(tan_line),
            FadeInFromLarge(dot),
        )
        self.play(
            x_tracker.set_value, 5,
            run_time=6,
        )
        self.wait()
        self.play(
            x_tracker.set_value, 9.9,
            run_time=6,
        )
        self.wait()

        # Define growth factor
        gf_label = TexMobject(
            "\\text{Growth factor} =",
            "{\\Delta N_d \\over \\Delta N_{d - 1}}",
            tex_to_color_map={
                "\\Delta": WHITE,
                "N_d": YELLOW,
                "N_{d - 1}": BLUE,
            }
        )
        gf_label.next_to(infl_dot, RIGHT, LARGE_BUFF)

        numer_label = TextMobject("New cases one day")
        denom_label = TextMobject("New cases the\\\\previous day")

        for label, tex, vect in (numer_label, "N_d", UL), (denom_label, "N_{d - 1}", DL):
            part = gf_label.get_part_by_tex(tex)
            label.match_color(part)
            label.next_to(part, vect, LARGE_BUFF)
            label.shift(2 * RIGHT)
            arrow = Arrow(
                label.get_corner(vect[1] * DOWN),
                part.get_corner(vect[1] * UP) + 0.25 * LEFT,
                buff=0.1,
            )
            arrow.match_color(part)
            label.add_to_back(arrow)

        self.play(
            FadeIn(gf_label[0], RIGHT),
            FadeIn(gf_label[1:], LEFT),
            FadeOut(ode)
        )
        self.wait()
        for label in numer_label, denom_label:
            self.play(FadeIn(label, lag_ratio=0.1))
            self.wait()

        # Show example growth factors
        self.play(x_tracker.set_value, 1)

        eq = TexMobject("=")
        eq.next_to(gf_label, RIGHT)
        gf = DecimalNumber(1.15)
        gf.set_height(0.4)
        gf.next_to(eq, RIGHT)

        def get_growth_factor():
            x1 = x_tracker.get_value()
            x0 = x1 - 0.2
            x2 = x1 + 0.2
            p0, p1, p2 = [
                axes.input_to_graph_point(x, curve)
                for x in [x0, x1, x2]
            ]
            return (p2[1] - p1[1]) / (p1[1] - p0[1])

        gf.add_updater(lambda m: m.set_value(get_growth_factor()))

        self.add(eq, gf)
        self.play(
            x_tracker.set_value, 5,
            run_time=6,
            rate_func=linear,
        )
        self.wait()
        self.play(
            x_tracker.set_value, 9,
            run_time=6,
            rate_func=linear,
        )

    def get_axes(self):
        axes = Axes(
            x_min=0,
            x_max=13,
            y_min=0,
            y_max=10,
            y_axis_config={
                "unit_size": 0.7,
                "include_tip": False,
            }
        )
        axes.center()
        axes.to_edge(DOWN)

        x_label = TextMobject("Time")
        x_label.next_to(axes.x_axis, UP, aligned_edge=RIGHT)
        y_label = TextMobject("N cases")
        y_label.next_to(axes.y_axis, RIGHT, aligned_edge=UP)
        axes.add(x_label, y_label)
        return axes


class SubtltyOfGrowthFactorShift(Scene):
    def construct(self):
        # Set up totals
        total_title = TextMobject("Totals")
        total_title.add(Underline(total_title))
        total_title.to_edge(UP)
        total_title.scale(1.25)
        total_title.shift(LEFT)
        total_title.set_color(YELLOW)
        total_title.shift(LEFT)

        data = CASE_DATA[-4:]
        data.append(int(data[-1] + 1.15 * (data[-1] - data[-2])))
        totals = VGroup(*[Integer(value) for value in data])
        totals.scale(1.25)
        totals.arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        totals.next_to(total_title, DOWN, buff=0.6)
        totals[-1].set_color(BLUE)

        # Set up dates
        dates = VGroup(
            TextMobject("March 3, 2020"),
            TextMobject("March 4, 2020"),
            TextMobject("March 5, 2020"),
            TextMobject("March 6, 2020"),
        )
        for date, total in zip(dates, totals):
            date.scale(0.75)
            date.set_color(LIGHT_GREY)
            date.next_to(total, LEFT, buff=0.75, aligned_edge=DOWN)

        # Set up changes
        change_arrows = VGroup()
        change_labels = VGroup()
        for t1, t2 in zip(totals, totals[1:]):
            arrow = Arrow(
                t1.get_right(),
                t2.get_right(),
                path_arc=-150 * DEGREES,
                buff=0.1,
                max_tip_length_to_length_ratio=0.15,
            )
            arrow.shift(MED_SMALL_BUFF * RIGHT)
            arrow.set_stroke(width=3)
            change_arrows.add(arrow)

            diff = t2.get_value() - t1.get_value()
            label = Integer(diff, include_sign=True)
            label.set_color(GREEN)
            label.next_to(arrow, RIGHT)
            change_labels.add(label)

        change_labels[-1].set_color(BLUE)

        change_title = TextMobject("Changes")
        change_title.add(Underline(change_title).shift(0.128 * UP))
        change_title.scale(1.25)
        change_title.set_color(GREEN)
        change_title.move_to(change_labels)
        change_title.align_to(total_title, UP)

        # Set up growth factors
        gf_labels = VGroup()
        gf_arrows = VGroup()
        for c1, c2 in zip(change_labels, change_labels[1:]):
            arrow = Arrow(
                c1.get_right(),
                c2.get_right(),
                path_arc=-150 * DEGREES,
                buff=0.1,
                max_tip_length_to_length_ratio=0.15,
            )
            arrow.set_stroke(width=1)
            gf_arrows.add(arrow)

            line = Line(LEFT, RIGHT)
            line.match_width(c2)
            line.set_stroke(WHITE, 2)
            numer = c2.deepcopy()
            denom = c1.deepcopy()
            frac = VGroup(numer, line, denom)
            frac.arrange(DOWN, buff=SMALL_BUFF)
            frac.scale(0.7)
            frac.next_to(arrow, RIGHT)
            eq = TexMobject("=")
            eq.next_to(frac, RIGHT)
            gf = DecimalNumber(c2.get_value() / c1.get_value())
            gf.next_to(eq, RIGHT)
            gf_labels.add(VGroup(frac, eq, gf))

        gf_title = TextMobject("Growth factors")
        gf_title.add(Underline(gf_title))
        gf_title.scale(1.25)
        gf_title.move_to(gf_labels[0][-1])
        gf_title.align_to(total_title, DOWN)

        # Add things
        self.add(dates, total_title)
        self.play(
            LaggedStartMap(
                FadeInFrom, totals[:-1],
                lambda m: (m, UP),
            )
        )
        self.wait()
        self.play(
            ShowCreation(change_arrows[:-1]),
            LaggedStartMap(
                FadeInFrom, change_labels[:-1],
                lambda m: (m, LEFT),
            ),
            FadeIn(change_title),
        )
        self.wait()
        self.play(
            ShowCreation(gf_arrows[:-1]),
            LaggedStartMap(FadeIn, gf_labels[:-1]),
            FadeIn(gf_title),
        )
        self.wait()

        # Show hypothetical new value
        self.play(LaggedStart(
            FadeIn(gf_labels[-1]),
            FadeIn(gf_arrows[-1]),
            FadeIn(change_labels[-1]),
            FadeIn(change_arrows[-1]),
            FadeIn(totals[-1]),
        ))
        self.wait()

        # Change it
        alt_change = data[-2] - data[-3]
        alt_total = data[-2] + alt_change
        alt_gf = 1

        self.play(
            ChangeDecimalToValue(gf_labels[-1][-1], alt_gf),
            ChangeDecimalToValue(gf_labels[-1][0][0], alt_change),
            ChangeDecimalToValue(change_labels[-1], alt_change),
            ChangeDecimalToValue(totals[-1], alt_total),
        )
        self.wait()


class ContrastRandomShufflingWithClustersAndTravel(Scene):
    def construct(self):
        background = FullScreenFadeRectangle()
        background.set_fill(GREY_E)
        self.add(background)

        squares = VGroup(*[Square() for x in range(2)])
        squares.set_width(FRAME_WIDTH / 2 - 1)
        squares.arrange(RIGHT, buff=0.75)
        squares.to_edge(DOWN)
        squares.set_fill(BLACK, 1)
        squares.stretch(0.8, 1)
        self.add(squares)

        titles = VGroup(
            TextMobject("Random shuffling"),
            TextMobject("Clusters with travel"),
        )
        for title, square in zip(titles, squares):
            title.scale(1.4)
            title.next_to(square, UP)
        titles[1].align_to(titles[0], UP)

        self.play(LaggedStartMap(
            FadeInFrom, titles,
            lambda m: (m, 0.25 * DOWN),
        ))
        self.wait()


class ShowVaryingExpFactor(Scene):
    def construct(self):
        factor = DecimalNumber(0.15)
        rect = BackgroundRectangle(factor, buff=SMALL_BUFF)
        rect.set_fill(BLACK, 1)
        arrow = Arrow(
            factor.get_right(),
            factor.get_right() + 4 * RIGHT + 0.5 * DOWN,
        )

        self.add(rect, factor, arrow)
        for value in [0.05, 0.25, 0.15]:
            self.play(
                ChangeDecimalToValue(factor, value),
                run_time=3,
            )
        self.wait()


class ShowVaryingBaseFactor(ShowLogisticCurve):
    def construct(self):
        factor = DecimalNumber(1.15)
        rect = BackgroundRectangle(factor, buff=SMALL_BUFF)
        rect.set_fill(BLACK, 1)

        self.add(rect, factor)
        for value in [1.05, 1.25, 1.15]:
            self.play(
                ChangeDecimalToValue(factor, value),
                run_time=3,
            )
        self.wait()


class ShowVaryingExpCurve(ShowLogisticCurve):
    def construct(self):
        axes = self.get_axes()
        self.add(axes)

        curve = axes.get_graph(lambda x: np.exp(0.15 * x))
        curve.set_stroke([BLUE, YELLOW, RED])
        curve.make_jagged()
        self.add(curve)

        self.camera.frame.scale(2, about_edge=DOWN)
        self.camera.frame.shift(DOWN)
        rect = FullScreenFadeRectangle()
        rect.set_stroke(WHITE, 3)
        rect.set_fill(opacity=0)
        self.add(rect)

        for value in [0.05, 0.25, 0.15]:
            new_curve = axes.get_graph(lambda x: np.exp(value * x))
            new_curve.set_stroke([BLUE, YELLOW, RED])
            new_curve.make_jagged()
            self.play(
                Transform(curve, new_curve),
                run_time=3,
            )


class EndScreen(PatreonEndScreen):
    CONFIG = {
        "specific_patrons": [
            "1stViewMaths",
            "Adam Dřínek",
            "Aidan Shenkman",
            "Alan Stein",
            "Alex Mijalis",
            "Alexis Olson",
            "Ali Yahya",
            "Andrew Busey",
            "Andrew Cary",
            "Andrew R. Whalley",
            "Aravind C V",
            "Arjun Chakroborty",
            "Arthur Zey",
            "Austin Goodman",
            "Avi Finkel",
            "Awoo",
            "AZsorcerer",
            "Barry Fam",
            "Bernd Sing",
            "Boris Veselinovich",
            "Bradley Pirtle",
            "Brian Staroselsky",
            "Britt Selvitelle",
            "Britton Finley",
            "Burt Humburg",
            "Calvin Lin",
            "Charles Southerland",
            "Charlie N",
            "Chenna Kautilya",
            "Chris Connett",
            "Christian Kaiser",
            "cinterloper",
            "Clark Gaebel",
            "Colwyn Fritze-Moor",
            "Cooper Jones",
            "Corey Ogburn",
            "D. Sivakumar",
            "Daniel Herrera C",
            "Dave B",
            "Dave Kester",
            "dave nicponski",
            "David B. Hill",
            "David Clark",
            "David Gow",
            "Delton Ding",
            "Dominik Wagner",
            "Douglas Cantrell",
            "emptymachine",
            "Eric Younge",
            "Eryq Ouithaqueue",
            "Federico Lebron",
            "Frank R. Brown, Jr.",
            "Giovanni Filippi",
            "Hal Hildebrand",
            "Hitoshi Yamauchi",
            "Ivan Sorokin",
            "Jacob Baxter",
            "Jacob Harmon",
            "Jacob Hartmann",
            "Jacob Magnuson",
            "Jake Vartuli - Schonberg",
            "Jameel Syed",
            "Jason Hise",
            "Jayne Gabriele",
            "Jean-Manuel Izaret",
            "Jeff Linse",
            "Jeff Straathof",
            "John C. Vesey",
            "John Haley",
            "John Le",
            "John V Wertheim",
            "Jonathan Heckerman",
            "Jonathan Wilson",
            "Joseph John Cox",
            "Joseph Kelly",
            "Josh Kinnear",
            "Joshua Claeys",
            "Juan Benet",
            "Kai-Siang Ang",
            "Kanan Gill",
            "Karl Niu",
            "Kartik Cating-Subramanian",
            "Kaustuv DeBiswas",
            "Killian McGuinness",
            "Kros Dai",
            "L0j1k",
            "Lambda GPU Workstations",
            "Lee Redden",
            "Linh Tran",
            "Luc Ritchie",
            "Ludwig Schubert",
            "Lukas Biewald",
            "Magister Mugit",
            "Magnus Dahlström",
            "Manoj Rewatkar - RITEK SOLUTIONS",
            "Mark Heising",
            "Mark Mann",
            "Martin Price",
            "Mathias Jansson",
            "Matt Godbolt",
            "Matt Langford",
            "Matt Roveto",
            "Matt Russell",
            "Matteo Delabre",
            "Matthew Bouchard",
            "Matthew Cocke",
            "Mia Parent",
            "Michael Hardel",
            "Michael W White",
            "Mirik Gogri",
            "Mustafa Mahdi",
            "Márton Vaitkus",
            "Nicholas Cahill",
            "Nikita Lesnikov",
            "Oleg Leonov",
            "Oliver Steele",
            "Omar Zrien",
            "Owen Campbell-Moore",
            "Patrick Lucas",
            "Peter Ehrnstrom",
            "Peter Mcinerney",
            "Pierre Lancien",
            "Quantopian",
            "Randy C. Will",
            "rehmi post",
            "Rex Godby",
            "Ripta Pasay",
            "Rish Kundalia",
            "Roman Sergeychik",
            "Roobie",
            "Ryan Atallah",
            "Samuel Judge",
            "SansWord Huang",
            "Scott Gray",
            "Scott Walter, Ph.D.",
            "Sebastian Garcia",
            "soekul",
            "Solara570",
            "Steve Huynh",
            "Steve Sperandeo",
            "Steven Braun",
            "Steven Siddals",
            "Stevie Metke",
            "supershabam",
            "Suteerth Vishnu",
            "Suthen Thomas",
            "Tal Einav",
            "Tauba Auerbach",
            "Ted Suzman",
            "Thomas J Sargent",
            "Thomas Tarler",
            "Tianyu Ge",
            "Tihan Seale",
            "Tyler VanValkenburg",
            "Vassili Philippov",
            "Veritasium",
            "Vinicius Reis",
            "Xuanji Li",
            "Yana Chernobilsky",
            "Yavor Ivanov",
            "YinYangBalance.Asia",
            "Yu Jun",
            "Yurii Monastyrshyn",
        ]
    }
