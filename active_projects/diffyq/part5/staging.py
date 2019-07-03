from manimlib.imports import *

tex_config = {
    "tex_to_color_map": {
        "{t}": YELLOW,
        "{0}": YELLOW,
        "e^": WHITE,
        "=": WHITE,
    }
}

VELOCITY_COLOR = RED
POSITION_COLOR = GREEN


class IntroductionOfExp(Scene):
    def construct(self):
        questions = VGroup(
            TextMobject("What", "is", "$e^{t}$"),
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
            part[1].set_color(YELLOW)

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
                derivative[3:5],
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
                derivative[3:5],
                derivative[-2:],
                path_arc=-PI
            ),
        )
        self.wait()
        self.play(
            Restore(derivative),
            FadeInFrom(ic, LEFT)
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
        # TODO, use const
        derivative = TexMobject(
            "{d \\over d{t}} e^{t} = e^{t}",
            **tex_config
        )
        ic = TexMobject("e^{0} = 1", **tex_config)
        group = VGroup(derivative, ic)
        group.arrange(RIGHT, buff=LARGE_BUFF)
        ic.align_to(derivative[-2], DOWN)
        group.scale(1.5)
        group.to_edge(UP)
        return group


class IntroducePhysicalModel(IntroductionOfExp):
    CONFIG = {
        "number_line_config": {
            "x_min": 0,
            "x_max": 100,
            "unit_size": 1,
            "numbers_with_elongated_ticks": [0],
            "numbers_to_show": list(range(0, 15))
        },
        "number_line_y": -2,
        "const": 1,
        "const_str": "",
        "num_decimal_places": 2,
    }

    def construct(self):
        self.setup_number_line()
        self.setup_movers()
        self.show_number_line()
        self.show_formulas()

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

    def setup_value_trackers(self):
        number_line = self.number_line

        input_tracker = ValueTracker(0)
        get_input = input_tracker.get_value

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
        tip.set_height(0.4)
        tip.stretch(0.25, 0)
        tip.add_updater(lambda m: m.move_to(
            self.get_output_point(), DOWN
        ))
        tip.set_color(WHITE)

        self.tip = tip

    def setup_vectors(self):
        number_line = self.number_line

        position_vect = Vector(color=POSITION_COLOR)
        velocity_vect = Vector(color=VELOCITY_COLOR)

        position_vect.add_updater(
            lambda m: m.put_start_and_end_on(
                number_line.n2p(0),
                number_line.n2p(self.get_output()),
            )
        )

        def update_velocity_vect(vect):
            vect.put_start_and_end_on(
                *position_vect.get_start_and_end()
            )
            vect.scale(abs(self.const))
            vect.rotate(np.log(self.const).imag)
            vect.shift(self.get_output_point() - vect.get_start())
            return vect

        velocity_vect.add_updater(update_velocity_vect)

        self.position_vect = position_vect
        self.velocity_vect = velocity_vect

    def setup_vector_labels(self):
        position_vect = self.position_vect
        velocity_vect = self.velocity_vect

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
            tip_label[1].set_color(BLUE)

        template_decimal = tip_label[-1]
        # parens = tip_label[-3::2]
        template_decimal.set_opacity(0)
        tip_label.add_updater(lambda m: m.next_to(
            tip, UP,
            index_of_submobject_to_align=0
        ))
        decimal = DecimalNumber(num_decimal_places=ndp)
        decimal.set_color(YELLOW)
        decimal.match_height(template_decimal)
        decimal.add_updater(lambda m: m.set_value(self.get_input()))
        decimal.add_updater(
            lambda m: m.move_to(template_decimal, LEFT)
        )
        tip_label.add(decimal)

        self.tip_label = tip_label

    def show_number_line(self):
        number_line = self.number_line
        self.add(number_line)

        self.add(self.tip)
        self.add(self.position_vect)
        self.add(self.velocity_vect)
        self.add(self.tip_label)

        self.play(
            self.input_tracker.set_value, 0.56,
            run_time=3,
        )

    def show_formulas(self):
        deriv, ic = self.get_deriv_and_ic()

        self.add(deriv, ic)
