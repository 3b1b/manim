from manimlib.imports import *
from active_projects.ode.part1.shared_constructs import *


class SmallAngleApproximationTex(Scene):
    def construct(self):
        approx = TexMobject(
            "\\sin", "(", "\\theta", ") \\approx \\theta",
            tex_to_color_map={"\\theta": RED},
            arg_separator="",
        )

        implies = TexMobject("\\Downarrow")
        period = TexMobject(
            "\\text{Period}", "\\approx",
            "2\\pi \\sqrt{\\,{L} / {g}}",
            **Lg_formula_config,
        )
        group = VGroup(approx, implies, period)
        group.arrange(DOWN)

        approx_brace = Brace(approx, UP, buff=SMALL_BUFF)
        approx_words = TextMobject(
            "For small $\\theta$",
            tex_to_color_map={"$\\theta$": RED},
        )
        approx_words.scale(0.75)
        approx_words.next_to(approx_brace, UP, SMALL_BUFF)

        self.add(approx, approx_brace, approx_words)
        self.play(
            Write(implies),
            FadeInFrom(period, LEFT)
        )
        self.wait()


class StrogatzQuote(Scene):
    def construct(self):
        quote = self.get_quote()
        movers = VGroup(*quote[:-1].family_members_with_points())
        for mover in movers:
            mover.save_state()
            disc = Circle(radius=0.05)
            disc.set_stroke(width=0)
            disc.set_fill(BLACK, 0)
            disc.move_to(mover)
            mover.become(disc)
        self.play(
            FadeInFrom(quote.author_part, LEFT),
            LaggedStartMap(
                # FadeInFromLarge,
                # quote[:-1].family_members_with_points(),
                Restore, movers,
                lag_ratio=0.005,
                run_time=2,
            )
            # FadeInFromDown(quote[:-1]),
            # lag_ratio=0.01,
        )
        self.wait()
        self.play(
            Write(quote.law_part.copy().set_color(YELLOW)),
            run_time=1,
        )
        self.wait()
        self.play(
            Write(quote.language_part.copy().set_color(BLUE)),
            run_time=1.5,
        )
        self.wait(2)

    def get_quote(self):
        law_words = "laws of physics"
        language_words = "language of differential equations"
        author = "-Steven Strogatz"
        quote = TextMobject(
            """
            \\Large
            ``Since Newton, mankind has come to realize
            that the laws of physics are always expressed
            in the language of differential equations.''\\\\
            """ + author,
            alignment="",
            arg_separator=" ",
            substrings_to_isolate=[law_words, language_words, author]
        )
        quote.law_part = quote.get_part_by_tex(law_words)
        quote.language_part = quote.get_part_by_tex(language_words)
        quote.author_part = quote.get_part_by_tex(author)
        quote.set_width(12)
        quote.to_edge(UP)
        quote[-2].shift(SMALL_BUFF * LEFT)
        quote.author_part.shift(RIGHT + 0.5 * DOWN)
        quote.author_part.scale(1.2, about_edge=UL)

        return quote


class WriteInRadians(Scene):
    def construct(self):
        words = TextMobject("In radians")
        words.set_color(YELLOW)
        square = SurroundingRectangle(TexMobject("\\theta"))
        square.next_to(words, UP)
        self.play(ShowCreation(square))
        self.play(Write(words), FadeOut(square))
        self.wait()


class XEqLThetaToCorner(Scene):
    def construct(self):
        equation = TexMobject(
            "x = L\\theta",
            tex_to_color_map={
                "x": GREEN,
                "\\theta": BLUE,
            }
        )
        equation.move_to(DOWN + 3 * RIGHT)
        self.add(equation)
        self.play(equation.to_corner, DL, {"buff": LARGE_BUFF})
        self.wait()


class ComingUp(Scene):
    CONFIG = {
        "camera_config": {"background_color": DARKER_GREY}
    }

    def construct(self):
        frame = ScreenRectangle(
            stroke_width=0,
            fill_color=BLACK,
            fill_opacity=1,
            height=6
        )
        title = TextMobject("Coming up")
        title.scale(1.5)
        title.to_edge(UP)
        frame.next_to(title, DOWN)
        animated_frame = AnimatedBoundary(frame)
        self.add(frame, title, animated_frame)
        self.wait(10)


class InputLabel(Scene):
    def construct(self):
        label = TextMobject("Input")
        label.scale(1.25)
        arrow = Vector(UP)
        arrow.next_to(label, UP)
        self.play(
            FadeInFrom(label, UP),
            GrowArrow(arrow)
        )
        self.wait()


class ReallyHardToSolve(Scene):
    def construct(self):
        words = TextMobject(
            "They're", "really\\\\",
            "freaking", "hard\\\\",
            "to", "solve\\\\",
        )
        words.set_height(6)

        self.wait()
        for word in words:
            wait_time = 0.05 * len(word)
            self.add(word)
            self.wait(wait_time)
        self.wait()


class ReasonForSolution(Scene):
    def construct(self):
        # Words
        eq_word = TextMobject("Differential\\\\Equation")
        s_word = TextMobject("Solution")
        u_word = TextMobject("Understanding")
        c_word = TextMobject("Computation")
        cu_group = VGroup(u_word, c_word)
        cu_group.arrange(DOWN, buff=2)
        group = VGroup(eq_word, s_word, cu_group)
        group.arrange(RIGHT, buff=2)
        # words = VGroup(eq_word, s_word, u_word, c_word)

        # Arrows
        arrows = VGroup(
            Arrow(eq_word.get_right(), s_word.get_left()),
            Arrow(s_word.get_right(), u_word.get_left()),
            Arrow(s_word.get_right(), c_word.get_left()),
        )
        arrows.set_color(LIGHT_GREY)
        new_arrows = VGroup(
            Arrow(
                eq_word.get_corner(UR),
                u_word.get_left(),
                path_arc=-60 * DEGREES,
            ),
            Arrow(
                eq_word.get_corner(DR),
                c_word.get_left(),
                path_arc=60 * DEGREES,
            ),
        )
        new_arrows.set_color(BLUE)

        # Define first examples
        t2c = {
            "{x}": BLUE,
            "{\\dot x}": RED,
        }
        equation = TexMobject(
            "{\\dot x}(t) = k {x}(t)",
            tex_to_color_map=t2c,
        )
        equation.next_to(eq_word, DOWN)
        solution = TexMobject(
            "{x}(t) = x_0 e^{kt}",
            tex_to_color_map=t2c,
        )
        solution.next_to(s_word, DOWN, MED_LARGE_BUFF)
        equation.align_to(solution, DOWN)

        axes = Axes(
            x_min=-1,
            x_max=5.5,
            y_min=-1,
            y_max=4.5,
            y_axis_config={"unit_size": 0.5}
        )
        axes.set_stroke(width=2)
        graph_line = axes.get_graph(
            lambda x: np.exp(0.4 * x)
        )
        graph_line.set_stroke(width=2)
        graph = VGroup(axes, graph_line)
        graph.scale(0.5)
        graph.next_to(u_word, UP)

        computation = TexMobject(
            # "\\displaystyle "
            "e^x = \\sum_{n=0}^\\infty "
            "\\frac{x^n}{n!}"
        )
        computation.next_to(c_word, DOWN)

        first_examples = VGroup(
            equation, solution, graph, computation
        )

        # Second example
        ode = get_ode()
        ode.scale(0.75)
        second_examples = VGroup(
            ode,
            TexMobject("???").set_color(LIGHT_GREY),
            ScreenRectangle(
                height=2,
                stroke_width=1,
            ),
        )
        for fe, se in zip(first_examples, second_examples):
            se.move_to(fe, DOWN)

        ode.shift(2 * SMALL_BUFF * DOWN)
        ode.add_to_back(BackgroundRectangle(ode[-4:]))

        self.add(eq_word)
        self.add(equation)
        self.play(
            FadeInFrom(s_word, LEFT),
            GrowArrow(arrows[0]),
            TransformFromCopy(equation, solution)
        )
        self.wait()
        self.play(
            FadeInFrom(c_word, UL),
            GrowArrow(arrows[2]),
            FadeInFrom(computation, UP)
        )
        self.wait()
        self.play(
            FadeInFrom(u_word, DL),
            GrowArrow(arrows[1]),
            FadeInFromDown(graph)
        )
        self.wait(2)

        self.play(
            FadeOut(first_examples),
            FadeIn(second_examples[:2])
        )
        self.wait()
        self.play(
            arrows.fade, 0.75,
            s_word.fade, 0.75,
            second_examples[1].fade, 0.75,
            ShowCreation(new_arrows[0]),
            FadeIn(second_examples[2])
        )
        self.play(
            ShowCreation(new_arrows[1]),
            Animation(second_examples),
        )
        self.wait()


class WritePhaseSpace(Scene):
    def construct(self):
        word = TextMobject("Phase space")
        word.scale(2)
        word.shift(FRAME_WIDTH * LEFT / 4)
        word.to_edge(UP)
        word.add_background_rectangle()

        lines = VGroup(*[
            Line(v, 1.3 * v)
            for v in compass_directions(50)
        ])
        lines.replace(word, stretch=True)
        lines.scale(1.5)
        lines.set_stroke(YELLOW)
        lines.shuffle()

        self.add(word)
        self.play(
            ShowPassingFlashWithThinningStrokeWidth(
                lines,
                lag_ratio=0.002,
                run_time=1.5,
                time_width=0.9,
                n_segments=5,
            )
        )
        self.wait()


class GleickQuote(Scene):
    def construct(self):
        quote = TextMobject(
            "``[Phase space is] one of the most\\\\",
            "powerful inventions", "of modern science.''\\\\",
        )
        quote.power_part = quote.get_part_by_tex("power")
        book = ImageMobject("ChaosBookCover")
        book.set_height(5)
        book.next_to(ORIGIN, LEFT)
        book.to_edge(DOWN)
        gleick = ImageMobject("JamesGleick")
        gleick.set_height(5)
        gleick.next_to(ORIGIN, RIGHT)
        gleick.to_edge(DOWN)
        quote.to_edge(UP)

        self.play(
            FadeInFrom(book, RIGHT),
            FadeInFrom(gleick, LEFT),
        )
        self.wait()
        self.play(Write(quote))
        self.play(Write(
            quote.power_part.copy().set_color(BLUE),
            run_time=1
        ))
        self.wait()


class WritePhaseFlow(Scene):
    def construct(self):
        words = TextMobject("Phase flow")
        words.scale(2)
        words.shift(FRAME_WIDTH * LEFT / 4)
        words.to_edge(UP)
        words.add_background_rectangle()
        self.play(Write(words))
        self.wait()


class ShowSineValues(Scene):
    def construct(self):
        angle_tracker = ValueTracker(60 * DEGREES)
        get_angle = angle_tracker.get_value
        formula = always_redraw(
            lambda: self.get_sine_formula(get_angle())
        )
        self.add(formula)

        self.play(
            angle_tracker.set_value, 0,
            run_time=3,
        )
        self.wait()
        self.play(
            angle_tracker.set_value, 90 * DEGREES,
            run_time=3,
        )
        self.wait()

    def get_sine_formula(self, angle):
        sin, lp, rp = TexMobject(
            "\\sin", "(", ") = "
        )
        input_part = Integer(
            angle / DEGREES,
            unit="^\\circ",
        )
        input_part.set_color(YELLOW)
        output_part = DecimalNumber(
            np.sin(input_part.get_value() * DEGREES),
            num_decimal_places=3,
        )
        result = VGroup(
            sin, lp, input_part, rp, output_part
        )
        result.arrange(RIGHT, buff=SMALL_BUFF)
        sin.scale(1.1, about_edge=DOWN)
        lp.align_to(rp, UP)
        return result


class SetAsideSeekingSolution(Scene):
    def construct(self):
        ode = get_ode()
        ode.to_edge(UP)
        q1 = TextMobject("Find an exact solution")
        q1.set_color(YELLOW)
        q2 = TexMobject(
            "\\text{What is }", "\\theta", "(t)",
            "\\text{'s personality?}",
            tex_to_color_map={"\\theta": BLUE},
            arg_separator="",
        )
        theta = q2.get_part_by_tex("\\theta")

        for q in q1, q2:
            q.scale(1.5)
            q.next_to(ode, DOWN, MED_LARGE_BUFF)
        eyes = Eyes(theta, height=0.1)

        self.add(ode)
        self.add(q1)
        self.wait()
        self.play(
            q1.scale, 0.3,
            q1.to_corner, UR, MED_SMALL_BUFF,
        )
        self.play(FadeInFrom(q2, DOWN))
        self.play(
            eyes.blink,
            rate_func=lambda t: smooth(1 - t),
        )
        self.play(eyes.look_at, q2.get_left())
        self.play(eyes.look_at, q2.get_right())
        self.play(
            eyes.blink,
            rate_func=squish_rate_func(there_and_back)
        )
        self.wait()
        self.play(
            eyes.change_mode, "confused",
            eyes.look_at, ode.get_left(),
        )
        self.play(
            eyes.blink,
            rate_func=squish_rate_func(there_and_back)
        )


class ThreeBodyTitle(Scene):
    def construct(self):
        title = TextMobject("Three body problem")
        title.scale(1.5)
        title.to_edge(UP)
        self.add(title)


class ThreeBodySymbols(Scene):
    def construct(self):
        self.init_coord_groups()
        self.introduce_coord_groups()
        self.count_coords()

    def init_coord_groups(self):
        kwargs = {
            "bracket_v_buff": 2 * SMALL_BUFF
        }
        positions = VGroup(*[
            get_vector_symbol(*[
                "{}_{}".format(s, i)
                for s in "xyz"
            ], **kwargs)
            for i in range(1, 4)
        ])
        velocities = VGroup(*[
            get_vector_symbol(*[
                "p^{}_{}".format(s, i)
                for s in "xyz"
            ], **kwargs)
            for i in range(1, 4)
        ])
        groups = VGroup(positions, velocities)
        colors = [GREEN, RED, BLUE]
        for group in groups:
            for matrix in group:
                matrix.coords = matrix.get_entries()
                for coord, color in zip(matrix.coords, colors):
                    coord.set_color(color)
            group.arrange(RIGHT)
        groups.arrange(DOWN, buff=LARGE_BUFF)
        groups.to_edge(LEFT)

        self.coord_groups = groups

    def introduce_coord_groups(self):
        groups = self.coord_groups
        x_group, p_group = groups
        x_word = TextMobject("Positions")
        p_word = TextMobject("Momenta")
        words = VGroup(x_word, p_word)
        for word, group in zip(words, groups):
            word.next_to(group, UP)

        rect_groups = VGroup()
        for group in groups:
            rect_group = VGroup(*[
                SurroundingRectangle(
                    VGroup(*[
                        tm.coords[i]
                        for tm in group
                    ]),
                    color=WHITE,
                    stroke_width=2,
                )
                for i in range(3)
            ])
            rect_groups.add(rect_group)

        self.play(
            *[
                LaggedStartMap(
                    FadeInFrom, group,
                    lambda m: (m, UP),
                    run_time=1,
                )
                for group in groups
            ],
            *map(FadeInFromDown, words),
        )
        for rect_group in rect_groups:
            self.play(
                ShowCreationThenFadeOut(
                    rect_group,
                    lag_ratio=0.5,
                )
            )
        self.wait()

    def count_coords(self):
        coord_copies = VGroup()
        for group in self.coord_groups:
            for tex_mob in group:
                for coord in tex_mob.coords:
                    coord_copy = coord.copy()
                    coord_copy.set_stroke(
                        WHITE, 2, background=True
                    )
                    coord_copies.add(coord_copy)

        count = Integer()
        count_word = TextMobject("18", "degrees \\\\ of freedom")[1]
        count_group = VGroup(count, count_word)
        count_group.arrange(
            RIGHT,
            aligned_edge=DOWN,
        )
        count_group.scale(1.5)
        count_group.next_to(
            self.coord_groups, RIGHT,
            aligned_edge=DOWN,
        )
        count.add_updater(
            lambda m: m.set_value(len(coord_copies))
        )
        count.add_updater(
            lambda m: m.next_to(count_word[0][0], LEFT, aligned_edge=DOWN)
        )

        self.add(count_group)
        self.play(
            # ChangeDecimalToValue(count, len(coord_copies)),
            ShowIncreasingSubsets(coord_copies),
            run_time=1.5,
            rate_func=linear,
        )
        self.play(FadeOut(coord_copies))


class ThreeBodyEquation(Scene):
    def construct(self):
        x1 = "\\vec{\\textbf{x}}_1"
        x2 = "\\vec{\\textbf{x}}_2"
        x3 = "\\vec{\\textbf{x}}_3"
        kw = {
            "tex_to_color_map": {
                x1: RED,
                x2: GREEN,
                x3: BLUE,
            }
        }
        equations = VGroup(*[
            TexMobject(
                "{d^2", t1, "\\over dt^2}", "=",
                "G", "\\left("
                "{" + m2, "(", t2, "-", t1, ")"
                "\\over"
                "||", t2, "-", t1, "||^3}",
                "+",
                "{" + m3, "(", t3, "-", t1, ")"
                "\\over"
                "||", t3, "-", t1, "||^3}",
                "\\right)",
                **kw
            )
            for t1, t2, t3, m1, m2, m3 in [
                (x1, x2, x3, "m_1", "m_2", "m_3"),
                (x2, x3, x1, "m_2", "m_3", "m_1"),
                (x3, x1, x2, "m_3", "m_1", "m_2"),
            ]
        ])
        equations.arrange(DOWN, buff=LARGE_BUFF)

        self.play(LaggedStartMap(
            FadeInFrom, equations,
            lambda m: (m, UP),
            lag_ratio=0.2,
        ))
        self.wait()


class JumpToThisPoint(Scene):
    def construct(self):
        dot = Dot(color=YELLOW)
        dot.scale(0.5)

        arrow = Vector(DR, color=WHITE)
        arrow.next_to(dot, UL, SMALL_BUFF)
        words = TextMobject(
            "Jump directly to\\\\",
            "this point?",
        )
        words.add_background_rectangle_to_submobjects()
        words.next_to(arrow.get_start(), UP, SMALL_BUFF)

        self.play(
            FadeInFromLarge(dot, 20),
            rate_func=rush_into,
        )
        self.play(
            GrowArrow(arrow),
            FadeInFromDown(words),
        )


class ChaosTitle(Scene):
    def construct(self):
        title = TextMobject("Chaos theory")
        title.scale(1.5)
        title.to_edge(UP)
        line = Line(LEFT, RIGHT)
        line.set_width(FRAME_WIDTH - 1)
        line.next_to(title, DOWN)

        self.play(
            Write(title),
            ShowCreation(line),
        )
        self.wait()


class RevisitQuote(StrogatzQuote, PiCreatureScene):
    def construct(self):
        quote = self.get_quote()
        quote.law_part.set_color(YELLOW)
        quote.language_part.set_color(BLUE)
        quote.set_stroke(BLACK, 6, background=True)
        quote.scale(0.8, about_edge=UL)

        new_langauge_part = TextMobject(
            "\\Large Language of differential equations"
        )
        new_langauge_part.to_edge(UP)
        new_langauge_part.match_style(quote.language_part)

        randy = self.pi_creature

        self.play(
            FadeInFrom(quote[:-1], DOWN),
            FadeInFrom(quote[-1:], LEFT),
            randy.change, "raise_right_hand",
        )
        self.play(Blink(randy))
        self.play(randy.change, "angry")
        self.play(
            Blink(randy),
            VFadeOut(randy, run_time=3)
        )
        mover = VGroup(quote.language_part)
        self.add(quote, mover)
        self.play(
            ReplacementTransform(
                mover, new_langauge_part,
            ),
            *[
                FadeOut(part)
                for part in quote
                if part is not quote.language_part
            ],
            run_time=2,
        )
        self.wait()


class EndScreen(PatreonEndScreen):
    CONFIG = {
        "specific_patrons": [
            "Juan Benet",
            "Vassili Philippov",
            "Burt Humburg",
            "Carlos Vergara Del Rio",
            "Matt Russell",
            "Scott Gray",
            "soekul",
            "Tihan Seale",
            "Ali Yahya",
            "dave nicponski",
            "Evan Phillips",
            "Graham",
            "Joseph Kelly",
            "Kaustuv DeBiswas",
            "LambdaLabs",
            "Lukas Biewald",
            "Mike Coleman",
            "Peter Mcinerney",
            "Quantopian",
            "Roy Larson",
            "Scott Walter, Ph.D.",
            "Yana Chernobilsky",
            "Yu Jun",
            "Jordan Scales",
            "Lukas -krtek.net- Novy",
            "John Shaughnessy",
            "Britt Selvitelle",
            "David Gow",
            "J",
            "Jonathan Wilson",
            "Joseph John Cox",
            "Magnus Dahlström",
            "Randy C. Will",
            "Ryan Atallah",
            "Luc Ritchie",
            "1stViewMaths",
            "Adrian Robinson",
            "Alexis Olson",
            "Andreas Benjamin Brössel",
            "Andrew Busey",
            "Ankalagon",
            "Antonio Juarez",
            "Arjun Chakroborty",
            "Art Ianuzzi",
            "Awoo",
            "Bernd Sing",
            "Boris Veselinovich",
            "Brian Staroselsky",
            "Chad Hurst",
            "Charles Southerland",
            "Chris Connett",
            "Christian Kaiser",
            "Clark Gaebel",
            "Cooper Jones",
            "Danger Dai",
            "Dave B",
            "Dave Kester",
            "David Clark",
            "DeathByShrimp",
            "Delton Ding",
            "eaglle",
            "emptymachine",
            "Eric Younge",
            "Eryq Ouithaqueue",
            "Federico Lebron",
            "Giovanni Filippi",
            "Hal Hildebrand",
            "Herman Dieset",
            "Hitoshi Yamauchi",
            "Isaac Jeffrey Lee",
            "j eduardo perez",
            "Jacob Magnuson",
            "Jameel Syed",
            "Jason Hise",
            "Jeff Linse",
            "Jeff Straathof",
            "John Griffith",
            "John Haley",
            "John V Wertheim",
            "Jonathan Eppele",
            "Kai-Siang Ang",
            "Kanan Gill",
            "L0j1k",
            "Lee Redden",
            "Linh Tran",
            "Ludwig Schubert",
            "Magister Mugit",
            "Mark B Bahu",
            "Mark Heising",
            "Martin Price",
            "Mathias Jansson",
            "Matt Langford",
            "Matt Roveto",
            "Matthew Cocke",
            "Michael Faust",
            "Michael Hardel",
            "Mirik Gogri",
            "Mustafa Mahdi",
            "Márton Vaitkus",
            "Nero Li",
            "Nikita Lesnikov",
            "Omar Zrien",
            "Owen Campbell-Moore",
            "Peter Ehrnstrom",
            "RedAgent14",
            "rehmi post",
            "Richard Burgmann",
            "Richard Comish",
            "Ripta Pasay",
            "Rish Kundalia",
            "Robert Teed",
            "Roobie",
            "Ryan Williams",
            "Samuel D. Judge",
            "Solara570",
            "Stevie Metke",
            "Tal Einav",
            "Ted Suzman",
            "Valeriy Skobelev",
            "Xavier Bernard",
            "Yavor Ivanov",
            "Yaw Etse",
            "YinYangBalance.Asia",
            "Zach Cardwell",
        ]
    }
