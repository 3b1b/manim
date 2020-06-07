from manimlib.imports import *

T_COLOR = LIGHT_GREY
VELOCITY_COLOR = GREEN
POSITION_COLOR = BLUE
CONST_COLOR = YELLOW

tex_config = {
    "tex_to_color_map": {
        "{t}": T_COLOR,
        "{0}": T_COLOR,
        "e^": WHITE,
        "=": WHITE,
    }
}


class IntroductionOfExp(Scene):
    def construct(self):
        questions = VGroup(
            TextMobject("What", "is", "$e^{t}$", "?"),
            TextMobject("What", "properties", "does", "$e^{t}$", "have?"),
            TextMobject(
                "What", "property", "defines", "$e^{t}$", "?",
                tex_to_color_map={"defines": BLUE}
            ),
        )
        questions.scale(2)
        questions[0].next_to(questions[1], UP, LARGE_BUFF)
        questions[2][-1].next_to(questions[2][-2], RIGHT, SMALL_BUFF)
        questions.to_edge(UP)
        for question in questions:
            part = question.get_part_by_tex("e^{t}")
            part[1].set_color(T_COLOR)

        top_cross = Cross(questions[0])

        deriv_ic = self.get_deriv_and_ic()
        deriv_ic.save_state()
        deriv_ic.scale(2 / 1.5)
        deriv_ic.to_edge(DOWN, buff=LARGE_BUFF)
        derivative, ic = deriv_ic
        derivative.save_state()
        derivative.set_x(0)

        self.play(FadeInFromDown(questions[0]))
        self.wait()
        self.play(
            ShowCreation(top_cross),
            LaggedStart(
                *[
                    TransformFromCopy(
                        questions[0].get_part_by_tex(tex),
                        questions[1].get_part_by_tex(tex),
                    )
                    for tex in ("What", "e^{t}")
                ],
                *[
                    FadeIn(questions[1][i])
                    for i in [1, 2, 4]
                ]
            )
        )
        self.wait()
        self.play(
            TransformFromCopy(
                questions[1].get_part_by_tex("$e^{t}$"),
                derivative[3:7],
            ),
            FadeIn(derivative[:2]),
            FadeIn(derivative.get_part_by_tex("=")),
        )
        self.play(
            ReplacementTransform(
                questions[1][0],
                questions[2][0],
            ),
            FadeOut(questions[1][1]),
            FadeIn(questions[2][1]),
            FadeOut(questions[1][2]),
            FadeIn(questions[2][2]),
            ReplacementTransform(
                questions[1][3],
                questions[2][3],
            ),
            FadeOut(questions[1][4]),
            FadeIn(questions[2][4]),
        )
        self.wait()
        self.play(
            TransformFromCopy(
                derivative[3:7:3],
                derivative[-5:],
                path_arc=-60 * DEGREES,
            ),
        )
        self.wait()
        self.play(
            Restore(derivative),
            FadeIn(ic, LEFT)
        )
        self.wait()
        self.play(
            FadeOut(questions[0]),
            FadeOut(top_cross),
            FadeOut(questions[2]),
            Restore(deriv_ic),
        )
        self.wait()

    def get_deriv_and_ic(self, const=None):
        if const:
            const_str = "{" + str(const) + "}"
            mult_str = "\\cdot"
        else:
            const_str = "{}"
            mult_str = "{}"
        args = [
            "{d \\over d{t}}",
            "e^{",
            const_str,
            "{t}}",
            "=",
            const_str,
            mult_str,
            "e^{",
            const_str,
            "{t}}"
        ]
        derivative = TexMobject(
            *args,
            **tex_config
        )
        if const:
            derivative.set_color_by_tex(const_str, CONST_COLOR)

        ic = TexMobject("e^{0} = 1", **tex_config)
        group = VGroup(derivative, ic)
        group.arrange(RIGHT, buff=LARGE_BUFF)
        ic.align_to(derivative.get_part_by_tex("e^"), DOWN)
        group.scale(1.5)
        group.to_edge(UP)
        return group


class IntroducePhysicalModel(IntroductionOfExp):
    CONFIG = {
        "number_line_config": {
            "x_min": 0,
            "x_max": 100,
            "unit_size": 1.5,
            "numbers_with_elongated_ticks": [0],
            "numbers_to_show": list(range(0, 15)),
            "label_direction": UP,
        },
        "number_line_y": -2,
        "const": 1,
        "const_str": "",
        "num_decimal_places": 2,
        "output_label_config": {
            "show_ellipsis": True,
        },
    }

    def construct(self):
        self.setup_number_line()
        self.setup_movers()
        self.show_number_line()
        self.show_formulas()
        self.let_time_pass()

    def setup_number_line(self):
        nl = self.number_line = NumberLine(
            **self.number_line_config,
        )
        nl.to_edge(LEFT)
        nl.set_y(self.number_line_y)
        nl.add_numbers()

    def setup_movers(self):
        self.setup_value_trackers()
        self.setup_vectors()
        self.setup_vector_labels()
        self.setup_tip()
        self.setup_tip_label()
        self.setup_output_label()

    def setup_value_trackers(self):
        number_line = self.number_line

        input_tracker = ValueTracker(0)
        get_input = input_tracker.get_value

        def complex_number_to_point(z):
            zero = number_line.n2p(0)
            unit = number_line.n2p(1) - zero
            perp = rotate_vector(unit, TAU / 4)
            z = complex(z)
            return zero + unit * z.real + perp * z.imag

        number_line.cn2p = complex_number_to_point

        def get_output():
            return np.exp(self.const * get_input())

        def get_output_point():
            return number_line.n2p(get_output())

        output_tracker = ValueTracker(1)
        output_tracker.add_updater(
            lambda m: m.set_value(get_output())
        )

        self.get_input = get_input
        self.get_output = get_output
        self.get_output_point = get_output_point

        self.add(
            input_tracker,
            output_tracker,
        )
        self.input_tracker = input_tracker
        self.output_tracker = output_tracker

    def setup_tip(self):
        tip = ArrowTip(start_angle=-PI / 2)
        tip.set_height(0.6)
        tip.set_width(0.1, stretch=True)
        tip.add_updater(lambda m: m.move_to(
            self.get_output_point(), DOWN
        ))
        # tip.set_color(WHITE)
        tip.set_fill(GREY, 1)

        self.tip = tip

    def setup_tip_label(self):
        tip = self.tip
        const_str = self.const_str
        ndp = self.num_decimal_places

        args = ["e^{"]
        if const_str:
            args += [const_str, "\\cdot"]
        args += ["0." + ndp * "0"]

        tip_label = TexMobject(*args, arg_separator="")
        if const_str:
            tip_label[1].set_color(CONST_COLOR)

        template_decimal = tip_label[-1]
        # parens = tip_label[-3::2]
        template_decimal.set_opacity(0)
        tip_label.add_updater(lambda m: m.next_to(
            tip, UP,
            buff=2 * SMALL_BUFF,
            index_of_submobject_to_align=0
        ))
        decimal = DecimalNumber(num_decimal_places=ndp)
        decimal.set_color(T_COLOR)
        decimal.match_height(template_decimal)
        decimal.add_updater(lambda m: m.set_value(self.get_input()))
        decimal.add_updater(
            lambda m: m.move_to(template_decimal, LEFT)
        )
        tip_label.add(decimal)

        self.tip_label = tip_label

    def setup_output_label(self):
        label = VGroup(
            TexMobject("="),
            DecimalNumber(1, **self.output_label_config)
        )
        label.set_color(POSITION_COLOR)
        label.add_updater(
            lambda m: m[1].set_value(
                self.get_output()
            )
        )
        label.add_updater(
            lambda m: m.arrange(RIGHT, buff=SMALL_BUFF)
        )
        label.add_updater(
            lambda m: m.next_to(
                self.tip_label, RIGHT,
                buff=SMALL_BUFF,
                aligned_edge=DOWN,
            )
        )

        self.output_label = label

    def setup_vectors(self):
        number_line = self.number_line

        position_vect = Vector(color=POSITION_COLOR)
        velocity_vect = Vector(color=VELOCITY_COLOR)

        position_vect.add_updater(
            lambda m: m.put_start_and_end_on(
                number_line.cn2p(0),
                number_line.cn2p(self.get_output()),
            )
        )

        def update_velocity_vect(vect):
            vect.put_start_and_end_on(
                number_line.cn2p(0),
                number_line.cn2p(self.const * self.get_output())
            )
            vect.shift(
                number_line.cn2p(self.get_output()) - number_line.n2p(0)
            )
            return vect

        velocity_vect.add_updater(update_velocity_vect)

        self.position_vect = position_vect
        self.velocity_vect = velocity_vect

    def setup_vector_labels(self):
        position_vect = self.position_vect
        velocity_vect = self.velocity_vect

        max_width = 1.5
        p_label = TextMobject("Position")
        p_label.set_color(POSITION_COLOR)
        p_label.vect = position_vect
        v_label = TextMobject("Velocity")
        v_label.set_color(VELOCITY_COLOR)
        v_label.vect = velocity_vect

        # for label in [p_label, v_label]:
        #     label.add_background_rectangle()

        def update_label(label):
            label.set_width(min(
                max_width,
                0.8 * label.vect.get_length(),
            ))
            direction = normalize(label.vect.get_vector())
            perp_direction = rotate_vector(direction, -TAU / 4)
            label.next_to(
                label.vect.get_center(),
                np.round(perp_direction),
                buff=MED_SMALL_BUFF,
            )
        p_label.add_updater(update_label)
        v_label.add_updater(update_label)

        self.position_label = p_label
        self.velocity_label = v_label

    def show_number_line(self):
        number_line = self.number_line
        self.play(
            LaggedStartMap(
                FadeIn,
                number_line.numbers.copy(),
                remover=True,
            ),
            Write(number_line),
            run_time=2
        )
        self.wait()

    def show_formulas(self):
        deriv, ic = self.get_deriv_and_ic()
        eq_index = deriv.index_of_part_by_tex("=")
        lhs = deriv[:eq_index - 1]
        rhs = deriv[eq_index + 1:]

        rhs_rect = SurroundingRectangle(rhs)
        lhs_rect = SurroundingRectangle(lhs)
        rects = VGroup(rhs_rect, lhs_rect)
        rhs_rect.set_stroke(POSITION_COLOR, 2)
        lhs_rect.set_stroke(VELOCITY_COLOR, 2)

        rhs_word = TextMobject("Position")
        lhs_word = TextMobject("Velocity")
        words = VGroup(rhs_word, lhs_word)
        for word, rect in zip(words, rects):
            word.match_color(rect)
            word.next_to(rect, DOWN)

        self.add(deriv, ic)

        self.play(
            ShowCreation(rhs_rect),
            FadeIn(rhs_word, UP),
            ShowCreation(self.position_vect)
        )
        self.add(
            self.tip,
            self.number_line,
            self.position_vect,
        )
        self.number_line.numbers.set_stroke(BLACK, 3, background=True)
        self.play(
            Transform(
                rhs.copy(),
                self.tip_label.copy().clear_updaters(),
                remover=True,
            ),
            GrowFromPoint(self.tip, rhs.get_bottom()),
            TransformFromCopy(rhs_word, self.position_label),
        )
        self.add(self.tip_label)
        self.wait()
        self.play(
            ShowCreation(lhs_rect),
            FadeIn(lhs_word, UP),
        )
        self.wait()
        self.play(
            TransformFromCopy(
                self.position_vect,
                self.velocity_vect,
                path_arc=PI,
            )
        )
        self.play(
            TransformFromCopy(
                lhs_word,
                self.velocity_label,
            )
        )
        self.wait()

    def let_time_pass(self):
        # Sort of a quick and dirty implementation,
        # not the best for reusability

        rate = 0.25
        t_tracker = self.input_tracker
        t_tracker.add_updater(
            lambda m, dt: m.increment_value(rate * dt)
        )

        nl = self.number_line
        zero_point = nl.n2p(0)

        nl_copy = nl.copy()
        nl_copy.submobjects = []
        nl_copy.stretch(100, 0, about_point=zero_point)
        nl.add(nl_copy)

        # For first zoom
        xs1 = range(25, 100, 25)
        nl.add(*[
            nl.get_tick(x, size=1.5)
            for x in xs1
        ])
        nl.add_numbers(
            *xs1,
            number_config={"height": 5},
            buff=2,
        )

        # For second zoom
        xs2 = range(200, 1000, 200)
        nl.add(*[
            nl.get_tick(x, size=15)
            for x in xs2
        ])
        nl.add_numbers(
            *xs2,
            number_config={"height": 50},
            buff=20,
        )

        # For third zoom
        xs3 = range(2000, 10000, 2000)
        nl.add(*[
            nl.get_tick(x, size=150)
            for x in xs3
        ])
        nl.add_numbers(
            *xs3,
            number_config={
                "height": 300,
            },
            buff=200,
        )
        for n in nl.numbers:
            n[1].scale(0.5)

        self.add(self.tip)

        self.add(self.output_label)
        self.play(VFadeIn(self.output_label))
        self.wait(5)
        self.play(
            nl.scale, 0.1, {"about_point": zero_point},
            run_time=1,
        )
        self.wait(6)
        self.play(
            nl.scale, 0.1, {"about_point": zero_point},
            run_time=1,
        )
        self.wait(8)
        self.play(
            nl.scale, 0.1, {"about_point": zero_point},
            run_time=1,
        )
        self.wait(12)


class ConstantEquals2(IntroducePhysicalModel):
    CONFIG = {
        "const": 2,
        "const_str": "2",
        "const_text": "Double",
    }

    def construct(self):
        self.setup_number_line()
        self.setup_movers()

        self.add_initial_objects()
        self.point_out_chain_rule()
        self.show_double_vector()
        self.let_time_pass()

    def add_initial_objects(self):
        deriv, ic = self.get_deriv_and_ic(
            const=self.const
        )
        self.deriv = deriv
        self.ic = ic
        self.add(ic)

        self.add(self.tip)
        self.add(self.number_line)
        self.add(self.position_vect)
        self.add(self.position_label)
        self.add(self.tip_label)

    def point_out_chain_rule(self):
        deriv = self.deriv

        eq = deriv.get_part_by_tex("=")
        dot = deriv.get_part_by_tex("\\cdot")
        eq_index = deriv.index_of_part(eq)
        dot_index = deriv.index_of_part(dot)
        v_part = deriv[:eq_index - 1]
        c_part = deriv[eq_index + 1: dot_index]
        p_part = deriv[dot_index + 1:]
        parts = VGroup(v_part, c_part, p_part)

        rects = VGroup(*map(SurroundingRectangle, parts))
        words = VGroup(*map(TextMobject, [
            "Velocity", self.const_text, "Position"
        ]))
        colors = [VELOCITY_COLOR, CONST_COLOR, POSITION_COLOR]
        for rect, word, color in zip(rects, words, colors):
            rect.set_stroke(color, 2)
            word.set_color(color)
            word.next_to(rect, DOWN)

        v_rect, c_rect, p_rect = rects
        v_word, c_word, p_word = words
        self.readjust_const_label(c_word, c_rect)

        self.add(v_part, eq)
        self.add(v_rect, v_word)

        p_part.save_state()
        p_part.replace(v_part[-4:])
        c_part.save_state()
        c_part.replace(p_part.saved_state[2])

        self.play(ShowCreationThenFadeAround(
            v_part[-2],
            surrounding_rectangle_config={
                "color": CONST_COLOR
            },
        ))
        self.wait()
        self.play(
            Restore(p_part, path_arc=-TAU / 6),
            FadeIn(p_rect),
            FadeIn(p_word),
        )
        self.play(
            Restore(c_part, path_arc=TAU / 6),
            FadeIn(dot)
        )
        self.play(
            FadeIn(c_rect),
            FadeIn(c_word),
        )
        self.wait()

        self.v_word = v_word

    def show_double_vector(self):
        v_vect = self.velocity_vect
        p_vect = self.position_vect
        p_copy = p_vect.copy()
        p_copy.clear_updaters()
        p_copy.generate_target()
        p_copy.target.shift(2 * UR)

        times_2 = TexMobject("\\times", "2")
        times_2.set_color_by_tex("2", CONST_COLOR)
        times_2.next_to(p_copy.target.get_end(), UP, MED_SMALL_BUFF)

        self.play(
            MoveToTarget(p_copy),
            FadeIn(times_2),
        )
        self.play(
            p_copy.scale, 2, {"about_edge": LEFT},
            p_copy.match_color, v_vect,
        )
        self.play(FadeOut(times_2))
        self.play(
            ReplacementTransform(p_copy, v_vect),
            TransformFromCopy(
                self.v_word,
                self.velocity_label,
            )
        )
        self.wait()

    def let_time_pass(self):
        # Largely copying from the above scene.
        # Note to self: If these are reused anymore,
        # factor this out properly
        rate = 0.25
        t_tracker = self.input_tracker
        t_tracker.add_updater(
            lambda m, dt: m.increment_value(rate * dt)
        )

        nl = self.number_line
        zero_point = nl.n2p(0)

        nl_copy = nl.copy()
        nl_copy.submobjects = []
        nl_copy.stretch(1000, 0, about_point=zero_point)
        nl.add(nl_copy)

        # For first zoom
        xs1 = range(25, 100, 25)
        nl.add(*[
            nl.get_tick(x, size=1.5)
            for x in xs1
        ])
        nl.add_numbers(
            *xs1,
            number_config={"height": 5},
            buff=2,
        )

        # For second zoom
        xs2 = range(200, 1000, 200)
        nl.add(*[
            nl.get_tick(x, size=15)
            for x in xs2
        ])
        nl.add_numbers(
            *xs2,
            number_config={"height": 50},
            buff=20,
        )

        # For third zoom
        xs3 = range(2000, 10000, 2000)
        nl.add(*[
            nl.get_tick(x, size=150)
            for x in xs3
        ])
        nl.add_numbers(
            *xs3,
            number_config={
                "height": 300,
            },
            buff=200,
        )
        for n in nl.numbers:
            n[1].scale(0.5)

        # For fourth zoom
        xs3 = range(20000, 100000, 20000)
        nl.add(*[
            nl.get_tick(x, size=1500)
            for x in xs3
        ])
        nl.add_numbers(
            *xs3,
            number_config={
                "height": 3000,
            },
            buff=2000,
        )
        for n in nl.numbers:
            n[2].scale(0.5)

        self.add(self.tip)
        self.add(self.output_label)
        self.play(VFadeIn(self.output_label))
        for x in range(4):
            self.wait_until(
                lambda: self.position_vect.get_end()[0] > 0
            )
            self.play(
                nl.scale, 0.1, {"about_point": zero_point},
                run_time=1,
            )
        self.wait(5)

    #
    def readjust_const_label(self, c_word, c_rect):
        c_rect.stretch(1.2, 1, about_edge=DOWN)
        c_word.next_to(c_rect, UP)


class NegativeConstant(ConstantEquals2):
    CONFIG = {
        "const": -0.5,
        "const_str": "-0.5",
        "const_text": "Flip and squish",
        "number_line_config": {
            "unit_size": 2.5,
        }
    }

    def construct(self):
        self.setup_number_line()
        self.setup_movers()

        self.add_initial_objects()
        self.point_out_chain_rule()
        self.show_vector_manipulation()
        self.let_time_pass()

    def show_vector_manipulation(self):
        p_vect = self.position_vect
        v_vect = self.velocity_vect

        p_copy = p_vect.copy()
        p_copy.clear_updaters()
        p_copy.generate_target()
        p_copy.target.shift(5 * RIGHT + 2 * UP)

        times_neg1 = TexMobject("\\times", "(\\cdot 1)")
        temp_neg = times_neg1[1][-3]
        neg = TexMobject("-")
        neg.set_width(0.2, stretch=True)
        neg.move_to(temp_neg)
        temp_neg.become(neg)

        times_point5 = TexMobject("\\times", "0.5")
        terms = VGroup(times_neg1, times_point5)
        for term in terms:
            term[1].set_color(CONST_COLOR)
        terms.arrange(LEFT, buff=SMALL_BUFF)

        terms.next_to(p_copy.target.get_start(), UP)

        v_vect.add_updater(
            lambda m: m.shift(SMALL_BUFF * UP)
        )
        self.velocity_label.add_updater(
            lambda m: m.next_to(
                self.velocity_vect,
                UP, buff=SMALL_BUFF,
            )
        )

        v_vect_back = v_vect.copy()
        v_vect_back.set_stroke(BLACK, 3)

        self.play(
            MoveToTarget(p_copy),
            FadeIn(times_neg1),
        )
        self.play(
            Rotate(
                p_copy,
                angle=PI,
                about_point=p_copy.get_start(),
            )
        )
        self.wait()
        self.play(
            p_copy.scale, 0.5,
            {"about_point": p_copy.get_start()},
            p_copy.match_color, v_vect,
            FadeIn(times_point5)
        )
        self.wait()
        self.play(
            ReplacementTransform(p_copy, v_vect),
            FadeOut(terms),
            TransformFromCopy(
                self.v_word,
                self.velocity_label,
            ),
        )
        self.add(v_vect_back, v_vect)
        self.add(self.velocity_label)

    def let_time_pass(self):
        nl = self.number_line
        t_tracker = self.input_tracker
        zero_point = nl.n2p(0)

        scale_factor = 4.5
        nl.generate_target(use_deepcopy=True)
        nl.target.scale(scale_factor, about_point=zero_point)
        for tick in [*nl.target.tick_marks, *nl.target.big_tick_marks]:
            tick.scale(1 / scale_factor)
        nl.target.tick_marks[1].scale(2)

        for number in nl.target.numbers:
            number.scale(1.5 / scale_factor, about_edge=DOWN)
            number.align_to(zero_point + 0.3 * UP, DOWN)

        new_ticks = VGroup(*[
            nl.get_tick(x)
            for x in np.arange(0.1, 1.5, 0.1)
        ])

        self.play(
            MoveToTarget(nl),
            new_ticks.stretch, scale_factor, 0,
            {"about_point": zero_point},
            VFadeIn(new_ticks),
        )
        self.wait()

        rate = 0.25
        t_tracker.add_updater(
            lambda m, dt: m.increment_value(rate * dt)
        )
        self.play(VFadeIn(self.output_label))
        self.wait(20)

    #
    def readjust_const_label(self, c_word, c_rect):
        super().readjust_const_label(c_word, c_rect)
        c_word.shift(SMALL_BUFF * DOWN)
        c_word.shift(MED_SMALL_BUFF * RIGHT)


class ImaginaryConstant(ConstantEquals2):
    CONFIG = {
        "const": complex(0, 1),
        "const_str": "i",
        "const_text": "Rotate $90^\\circ$",
        "number_line_config": {
            "x_min": -5,
            "unit_size": 2.5,
        },
        "output_label_config": {
            "show_ellipsis": False,
        },
        "plane_unit_size": 2.5,
    }

    def construct(self):
        self.setup_number_line()
        self.setup_movers()
        self.add_initial_objects()
        self.show_vector_manipulation()
        self.transition_to_complex_plane()
        self.show_vector_field()
        self.show_circle()

    def setup_number_line(self):
        super().setup_number_line()
        nl = self.number_line
        nl.shift(nl.n2p(-5) - nl.n2p(0))
        nl.shift(0.5 * DOWN)
        shift_distance = (4 * nl.tick_size + nl.numbers.get_height() + SMALL_BUFF)
        nl.numbers.shift(shift_distance * DOWN)

    def add_initial_objects(self):
        deriv, ic = self.get_deriv_and_ic("i")
        VGroup(deriv, ic).shift(0.5 * DOWN)
        ic.shift(RIGHT)
        self.deriv = deriv
        self.ic = ic

        self.add(self.number_line)
        self.add(self.position_vect)
        self.add(self.position_label)

        # self.tip_label.clear_updaters()
        self.tip_label.shift_vect = VectorizedPoint(0.2 * UP)
        self.tip_label.add_updater(
            lambda m: m.next_to(
                self.position_vect.get_end(), UP,
                buff=0,
                index_of_submobject_to_align=0,
            ).shift(m.shift_vect.get_location())
        )

        eq = deriv.get_part_by_tex("=")
        dot = deriv.get_part_by_tex("\\cdot")
        eq_index = deriv.index_of_part(eq)
        dot_index = deriv.index_of_part(dot)
        v_term = deriv[:eq_index - 1]
        c_term = deriv[eq_index + 1: dot_index]
        p_term = deriv[dot_index + 1:]

        terms = VGroup(v_term, c_term, p_term)
        rects = VGroup(*map(SurroundingRectangle, terms))
        colors = [VELOCITY_COLOR, CONST_COLOR, POSITION_COLOR]
        labels = VGroup(*map(
            TextMobject,
            ["Velocity", self.const_text, "Position"]
        ))
        for rect, color, label in zip(rects, colors, labels):
            rect.set_stroke(color, 2)
            label.set_color(color)
            label.next_to(rect, DOWN)

        v_label, c_label, p_label = labels
        v_rect, c_rect, p_rect = rects
        self.term_rects = rects
        self.term_labels = labels

        randy = Randolph()
        randy.next_to(deriv, DOWN, LARGE_BUFF)
        point = VectorizedPoint(p_term.get_center())
        randy.add_updater(lambda r: r.look_at(point))

        self.play(
            FadeInFromDown(p_term),
            VFadeIn(randy),
        )
        self.play(randy.change, "confused")
        self.play(
            ShowCreation(p_rect),
            FadeIn(p_label, UP)
        )
        self.add(self.number_line, self.position_vect)
        self.play(
            Transform(
                p_label.copy(),
                self.tip_label.copy().clear_updaters(),
                remover=True,
            ),
            point.move_to, self.position_vect.get_end(),
            FadeIn(ic),
        )
        self.add(self.tip_label)
        self.play(Blink(randy))
        self.play(FadeOut(randy))

        # Velocity
        self.play(
            LaggedStartMap(FadeIn, [
                v_term, eq, v_rect, v_label,
            ]),
            run_time=1
        )
        c_term.save_state()
        c_term.replace(p_term[2])
        self.play(
            Restore(c_term, path_arc=TAU / 4),
            FadeIn(dot),
        )

        c_rect.stretch(1.2, 1, about_edge=DOWN)
        c_label.next_to(c_rect, UP)
        c_label.shift(0.5 * RIGHT)
        self.c_rect = c_rect
        self.c_label = c_label
        self.v_label = v_label

    def show_vector_manipulation(self):
        p_vect = self.position_vect
        v_vect = self.velocity_vect

        p_copy = p_vect.copy()
        p_copy.clear_updaters()
        p_copy.generate_target()
        p_copy.target.center()
        p_copy.target.shift(1.5 * DOWN)

        rot_p = p_copy.target.copy()
        rot_p.rotate(TAU / 4, about_point=rot_p.get_start())
        rot_p.match_style(v_vect)

        arc = Arc(
            angle=TAU / 4,
            radius=0.5,
            arc_center=p_copy.target.get_start(),
        )
        arc.add_tip(tip_length=0.1)
        angle_label = TexMobject("90^\\circ")
        angle_label.scale(0.5)
        angle_label.next_to(arc.point_from_proportion(0.5), UR, SMALL_BUFF)

        times_i = TexMobject("\\times", "i")
        times_i.set_color_by_tex("i", CONST_COLOR)
        times_i.next_to(p_copy.target, UP, buff=0)

        rot_v_label = TextMobject("Velocity")
        rot_v_label.set_color(VELOCITY_COLOR)
        rot_v_label.add_background_rectangle()
        rot_v_label.scale(0.8)
        rot_v_label.curr_angle = 0

        def update_rot_v_label(label):
            label.rotate(-label.curr_angle)
            label.next_to(ORIGIN, DOWN, 2 * SMALL_BUFF)
            # angle = PI + self.velocity_vect.get_angle()
            angle = 0
            label.rotate(angle, about_point=ORIGIN)
            label.curr_angle = angle
            # label.shift(self.velocity_vect.get_center())
            label.next_to(
                self.velocity_vect.get_end(),
                RIGHT,
                buff=SMALL_BUFF
            )

        rot_v_label.add_updater(update_rot_v_label)

        self.play(
            MoveToTarget(p_copy),
            FadeIn(times_i),
        )
        self.play(
            FadeIn(self.c_rect),
            FadeInFromDown(self.c_label),
        )
        self.play(
            ShowCreation(arc),
            FadeIn(angle_label),
            ApplyMethod(
                times_i.next_to, rot_p, RIGHT, {"buff": 0},
                path_arc=TAU / 4,
            ),
            TransformFromCopy(
                p_copy, rot_p,
                path_arc=-TAU / 4,
            ),
        )
        self.wait()

        temp_rot_v_label = rot_v_label.copy()
        temp_rot_v_label.clear_updaters()
        temp_rot_v_label.replace(self.v_label, dim_to_match=0)
        self.play(
            TransformFromCopy(rot_p, v_vect),
            TransformFromCopy(temp_rot_v_label, rot_v_label),
            self.tip_label.shift_vect.move_to, 0.1 * UP + 0.2 * RIGHT,
        )
        self.play(FadeOut(VGroup(
            p_copy, arc, angle_label,
            times_i, rot_p,
        )))

        self.velocity_label = rot_v_label

    def transition_to_complex_plane(self):
        nl = self.number_line
        background_rects = VGroup(*[
            BackgroundRectangle(rect)
            for rect in self.term_rects
        ])
        self.ic.add_background_rectangle()
        for label in self.term_labels:
            label.add_background_rectangle()

        corner_group = VGroup(
            background_rects,
            self.deriv,
            self.term_rects,
            self.term_labels,
            self.ic,
        )
        corner_group.generate_target()
        corner_group.target.to_corner(UL)
        corner_group.target[-1].next_to(
            corner_group.target, DOWN,
            buff=0.75,
            aligned_edge=LEFT
        )

        plane = ComplexPlane()
        plane.unit_size = self.plane_unit_size
        plane.scale(plane.unit_size)
        plane.add_coordinates()
        plane.shift(DOWN + 0.25 * RIGHT)

        nl.generate_target(use_deepcopy=True)
        nl.target.numbers.set_opacity(0)
        nl.target.scale(
            plane.unit_size / nl.unit_size
        )
        nl.target.shift(plane.n2p(0) - nl.target.n2p(0))

        plane_title = TextMobject("Complex plane")
        plane_title.set_stroke(BLACK, 3, background=True)
        plane_title.scale(2)
        plane_title.to_corner(UR)

        self.add(
            plane,
            corner_group,
            self.position_vect,
            self.velocity_vect,
            self.position_label,
            self.velocity_label,
            self.tip_label,
        )
        plane.save_state()
        plane.set_opacity(0)
        self.play(
            VFadeIn(background_rects),
            MoveToTarget(corner_group),
            MoveToTarget(nl),
        )
        self.play(
            Restore(plane, lag_ratio=0.01),
            FadeInFromDown(plane_title)
        )
        self.play(FadeOut(nl))
        self.play(FadeOut(plane_title))
        self.wait()

        self.plane = plane
        self.corner_group = corner_group

    def show_vector_field(self):
        plane = self.plane
        temp_faders = VGroup(
            self.position_vect,
            self.position_label,
            self.velocity_vect,
            self.velocity_label,
            self.tip_label,
        )
        foreground = VGroup(
            self.corner_group,
        )

        # Initial examples
        n = 12
        zs = [
            np.exp(complex(0, k * TAU / n))
            for k in range(n)
        ]
        points = map(plane.n2p, zs)
        vects = VGroup(*[
            Arrow(
                plane.n2p(0), point,
                buff=0,
                color=POSITION_COLOR,
            )
            for point in points
        ])
        vects.set_opacity(0.75)
        attached_vects = VGroup(*[
            vect.copy().shift(vect.get_vector())
            for vect in vects
        ])
        attached_vects.set_color(VELOCITY_COLOR)
        v_vects = VGroup(*[
            av.copy().rotate(
                90 * DEGREES,
                about_point=av.get_start()
            )
            for av in attached_vects
        ])

        self.play(
            LaggedStartMap(GrowArrow, vects),
            FadeOut(temp_faders),
        )
        self.wait()
        self.play(
            TransformFromCopy(
                vects, attached_vects,
                path_arc=20 * DEGREES,
            )
        )
        self.play(
            ReplacementTransform(
                attached_vects,
                v_vects,
                path_arc=90 * DEGREES,
            )
        )
        self.wait()

        # Vector fields
        zero_point = plane.n2p(0)

        def func(p):
            vect = p - zero_point
            return rotate_vector(vect, 90 * DEGREES)

        vf_config = {
            # "x_min": plane.n2p(-3)[0],
            # "x_max": plane.n2p(3)[0],
            # "y_min": plane.c2p(0, -2)[1],
            # "y_max": plane.c2p(0, 2)[1],
            "max_magnitude": 8,
            "opacity": 0.5,
        }
        vf0 = VectorField(
            lambda p: np.array(p) - zero_point,
            length_func=lambda x: x,
            # opacity=0.5,
            **vf_config,
        )
        vf1 = VectorField(
            func,
            length_func=lambda x: x,
            # opacity=0.5,
            **vf_config,
        )
        vf2 = VectorField(
            func,
            **vf_config,
        )
        for vf in [vf0, vf1, vf2]:
            vf.submobjects.sort(
                key=lambda m: get_norm(m.get_start())
            )

        self.play(
            FadeIn(vf0, lag_ratio=0.01, run_time=3),
            FadeOut(vects),
            FadeOut(v_vects),
            FadeOut(foreground),
        )
        self.play(
            Transform(vf0, vf1, path_arc=90 * DEGREES)
        )
        self.play(
            Transform(
                vf0, vf2,
                lag_ratio=0.001,
                run_time=2,
            ),
        )
        self.play(
            FadeIn(foreground)
        )
        self.play(FadeIn(temp_faders))

        self.vector_field = vf0
        self.foreground = foreground

    def show_circle(self):
        t_tracker = self.input_tracker
        ic = self.ic
        output_label = self.output_label
        plane = self.plane
        tip_label = self.tip_label

        output_label.update(0)
        # output_rect = BackgroundRectangle(output_label)
        # output_rect.add_updater(
        #     lambda m: m.move_to(output_label)
        # )
        # output_rect.set_opacity(0)
        output_label.set_stroke(BLACK, 5, background=True)

        ic_rect = SurroundingRectangle(ic)
        ic_rect.set_color(BLUE)

        circle = Circle(
            radius=get_norm(plane.n2p(1) - plane.n2p(0)),
            stroke_color=TEAL,
        )
        circle.move_to(plane.n2p(0))

        epii, eti = results = [
            TexMobject(
                "e^{{i}" + s1 + "} = " + s2,
                tex_to_color_map={
                    "{i}": CONST_COLOR,
                    "\\pi": T_COLOR,
                    "\\tau": T_COLOR,
                    "-1": POSITION_COLOR,
                    "1": POSITION_COLOR,
                }
            )
            for s1, s2 in [("\\pi", "-1"), ("\\tau", "1")]
        ]
        for result in results:
            rect = SurroundingRectangle(result)
            rect.set_stroke(WHITE, 1)
            rect.set_fill(BLACK, 0.75)
            result.add_to_back(rect)
            # result.set_stroke(BLACK, 5, background=True)
            result.scale(2)
            result.to_corner(UR)
            result.save_state()
            result.fade(1)
        eti.saved_state.next_to(epii, DOWN, buff=MED_LARGE_BUFF)

        epii.move_to(plane.n2p(-1), LEFT)
        eti.move_to(plane.n2p(1), LEFT)

        self.play(ShowCreation(ic_rect))
        self.play(FadeOut(ic_rect))
        self.play(
            Transform(
                ic[-1].copy(),
                output_label.deepcopy().clear_updaters(),
                remover=True
            ),
            FadeOut(self.position_label),
            FadeOut(self.velocity_label),
        )
        self.add(output_label)
        self.wait()

        circle_copy = circle.copy()
        circle_copy.save_state()
        self.play(
            ShowCreation(circle),
            t_tracker.set_value, TAU,
            run_time=TAU,
            rate_func=linear,
        )
        self.wait()
        self.play(
            t_tracker.set_value, 0,
            circle.set_stroke, {"width": 1},
        )
        self.wait()
        self.add(circle_copy, self.tip_label, self.output_label)
        self.play(
            ApplyMethod(
                t_tracker.set_value, PI,
                rate_func=linear,
            ),
            tip_label.shift_vect.move_to, 0.25 * UR,
            ShowCreation(
                circle_copy,
                rate_func=lambda t: 0.5 * t,
            ),
            run_time=PI,
        )
        self.wait()
        self.play(Restore(epii, run_time=2))
        self.wait()
        circle_copy.restore()
        self.play(
            ApplyMethod(
                t_tracker.set_value, TAU,
                rate_func=linear,
            ),
            tip_label.shift_vect.move_to, 0.1 * UR,
            ShowCreation(
                circle_copy,
                rate_func=lambda t: 0.5 + 0.5 * t,
            ),
            run_time=PI,
        )
        self.wait()
        self.play(Restore(eti, run_time=2))
        self.wait()

        rate = 1
        t_tracker.add_updater(
            lambda m, dt: m.increment_value(rate * dt)
        )
        # self.play(VFadeOut(output_label))
        self.wait(16)


class PiMinuteMark(Scene):
    def construct(self):
        text = TexMobject(
            "\\pi \\text{ minutes} \\approx \\text{3:08}"
        )
        rect = SurroundingRectangle(text)
        rect.set_fill(BLACK, 1)
        rect.set_stroke(WHITE, 2)

        self.play(
            FadeInFromDown(rect),
            FadeInFromDown(text),
        )
        self.wait()


class ReferenceWhatItMeans(PiCreatureScene):
    def construct(self):
        randy = self.pi_creature

        tex_config = {
            "tex_to_color_map": {
                "{i}": CONST_COLOR,
                "\\pi": T_COLOR,
                "-1": POSITION_COLOR,
            },
        }
        epii = TexMobject(
            "e^{{i} \\pi} = -1",
            **tex_config
        )
        epii.scale(2)

        many_es = TexMobject("e \\cdot e \\cdots e", "= -1", **tex_config)
        many_es.scale(2)
        brace = Brace(many_es[0], DOWN)
        pi_i = TexMobject("{i} \\pi \\text{ times}", **tex_config)
        pi_i.next_to(brace, DOWN, SMALL_BUFF)
        repeated_mult = VGroup(many_es, brace, pi_i)

        # arrow = Vector(2 * RIGHT)
        arrow = TexMobject("\\Rightarrow")
        arrow.scale(2)

        group = VGroup(epii, arrow, repeated_mult)
        group.arrange(
            RIGHT, buff=LARGE_BUFF,
        )
        for mob in group[1:]:
            mob.shift(
                (epii[0].get_bottom() - mob[0].get_bottom())[1] * UP
            )
        group.to_edge(UP)

        does_not_mean = TextMobject("Does \\emph{not}\\\\mean")
        does_not_mean.set_color(RED)
        does_not_mean.move_to(arrow)
        # cross = Cross(repeated_mult)

        nonsense = TextMobject(
            "\\dots because that's "
            "literal nonsense!"
        )
        nonsense.next_to(repeated_mult, DOWN)
        nonsense.to_edge(RIGHT, buff=MED_SMALL_BUFF)
        nonsense.set_color(RED)

        down_arrow = TexMobject("\\Downarrow")
        down_arrow.scale(2)
        down_arrow.stretch(1.5, 1)
        down_arrow.set_color(GREEN)
        down_arrow.next_to(epii, DOWN, LARGE_BUFF)
        actually_means = TextMobject("It actually\\\\means")
        actually_means.next_to(down_arrow, RIGHT)
        actually_means.set_color(GREEN)

        series = TexMobject(
            "{({i} \\pi )^0 \\over 0!} + ",
            "{({i} \\pi )^1 \\over 1!} + ",
            "{({i} \\pi )^2 \\over 2!} + ",
            "{({i} \\pi )^3 \\over 3!} + ",
            "{({i} \\pi )^4 \\over 4!} + ",
            "\\cdots = -1",
            **tex_config
        )
        series.set_width(FRAME_WIDTH - 1)
        series.next_to(down_arrow, DOWN, LARGE_BUFF)
        series.set_x(0)

        self.add(epii)
        self.play(
            FadeIn(arrow, LEFT),
            FadeIn(repeated_mult, 2 * LEFT),
            randy.change, "maybe",
        )
        self.wait()
        self.play(randy.change, "confused")
        self.play(
            FadeOut(arrow, DOWN),
            FadeIn(does_not_mean, UP),
        )
        self.play(Write(nonsense))
        self.play(randy.change, "angry")
        # self.play(ShowCreation(cross))
        self.wait()
        self.play(
            FadeOut(randy, DOWN),
            FadeIn(down_arrow, UP),
            FadeIn(actually_means, LEFT),
            FadeIn(series, lag_ratio=0.1, run_time=2)
        )
        self.wait()


class VideoWrapper(Scene):
    def construct(self):
        fade_rect = FullScreenFadeRectangle()
        fade_rect.set_fill(DARK_GREY, 1)
        screen_rects = VGroup(
            ScreenRectangle(),
            ScreenRectangle(),
        )
        screen_rects.set_height(3)
        screen_rects.set_fill(BLACK, 1)
        screen_rects.set_stroke(width=0)
        screen_rects.arrange(RIGHT, buff=LARGE_BUFF)
        screen_rects.shift(1.25 * UP)

        boundary = VGroup(*map(AnimatedBoundary, screen_rects))

        titles = VGroup(
            TextMobject("Want more?"),
            TextMobject("Learn calculus"),
        )
        titles.scale(1.5)
        for rect, title, in zip(screen_rects, titles):
            title.next_to(rect, UP)

        self.add(fade_rect)
        self.add(screen_rects)

        self.add(boundary[0])
        self.play(FadeInFromDown(titles[0]))
        self.add(boundary[1])
        self.play(FadeInFromDown(titles[1]))
        self.wait(18)


class Thumbnail(Scene):
    def construct(self):
        epii = TexMobject(
            "e^{{i} \\pi} = -1",
            tex_to_color_map={
                "{i}": CONST_COLOR,
                "\\pi": T_COLOR,
                "-1": POSITION_COLOR,
            }
        )
        epii.set_width(8)
        epii.to_edge(UP)

        words = VGroup(
            TextMobject("in"),
            TextMobject(
                "in", 
                "3.14", " minutes"
            ),
        )
        # words.set_width(FRAME_WIDTH - 4)
        words.set_stroke(BLACK, 6, background=True)
        words.set_width(FRAME_WIDTH - 2)
        words.arrange(DOWN, buff=LARGE_BUFF)
        words.next_to(epii, DOWN, LARGE_BUFF)
        words[1].set_color_by_tex("3.14", YELLOW)
        words.shift(-words[0].get_center())
        words[0].set_opacity(0)

        unit_size = 1.5
        plane = ComplexPlane()
        plane.scale(unit_size)
        plane.add_coordinates()

        circle = Circle(
            radius=unit_size,
            color=YELLOW,
        )
        # half_circle = VMobject()
        # half_circle.pointwise_become_partial(circle, 0, 0.5)
        # half_circle.set_stroke(RED, 6)
        p_vect = Arrow(
            plane.n2p(0),
            plane.n2p(1),
            buff=0,
            color=POSITION_COLOR,
        )
        v_vect = Arrow(
            plane.n2p(1),
            plane.n2p(complex(1, 1)),
            buff=0,
            color=VELOCITY_COLOR,
        )
        vects = VGroup(p_vect, v_vect)
        vects.set_stroke(width=10)

        self.add(plane)
        self.add(circle)
        self.add(vects)
        self.add(epii)
        self.add(words)
