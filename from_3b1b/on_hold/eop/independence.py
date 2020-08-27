from manimlib.imports import *

from scene.scene import ProgressDisplay
import scipy

#revert_to_original_skipping_status

def get_binomial_distribution(n, p):
    return lambda k : choose(n, k)*(p**(k))*((1-p)**(n-k))

def get_quiz(*questions):
    q_mobs = VGroup(*list(map(TextMobject, [
        "%d. %s"%(i+1, question)
        for i, question in enumerate(questions)
    ])))
    q_mobs.arrange(
        DOWN, 
        buff = MED_LARGE_BUFF,
        aligned_edge = LEFT, 
    )
    content = VGroup(
        TextMobject("Quiz").scale(1.5),
        Line(q_mobs.get_left(), q_mobs.get_right()),
        q_mobs
    )
    content.arrange(DOWN, buff = MED_SMALL_BUFF)
    rect = SurroundingRectangle(content, buff = MED_LARGE_BUFF)
    rect.shift(MED_SMALL_BUFF*DOWN)
    rect.set_color(WHITE)
    quiz = VGroup(rect, content)
    quiz.questions = q_mobs
    quiz.scale(0.7)
    return quiz

class Checkmark(TexMobjectFromPresetString):
    CONFIG = {
        "tex" : "\\checkmark",
        "color" : GREEN
    }

class Xmark(TexMobjectFromPresetString):
    CONFIG = {
        "tex" : "\\times",
        "color" : RED
    }



def get_slot_group(
    bool_list, 
    buff = MED_LARGE_BUFF, 
    include_qs = True,
    min_bool_list_len = 3,
    ):
    if len(bool_list) < min_bool_list_len:
        bool_list += [None]*(min_bool_list_len - len(bool_list))
    n = len(bool_list)

    lines = VGroup(*[
        Line(ORIGIN, MED_LARGE_BUFF*RIGHT)
        for x in range(n)
    ])
    lines.arrange(RIGHT, buff = buff)
    if include_qs:
        labels = VGroup(*[
            TextMobject("Q%d"%d) for d in range(1, n+1)
        ])
    else:
        labels = VGroup(*[VectorizedPoint() for d in range(n)])
    for label, line in zip(labels, lines):
        label.scale(0.7)
        label.next_to(line, DOWN, SMALL_BUFF)
    slot_group = VGroup()
    slot_group.lines = lines
    slot_group.labels = labels
    slot_group.content = VGroup()
    slot_group.digest_mobject_attrs()
    slot_group.to_edge(RIGHT)
    slot_group.bool_list = bool_list

    total_height = FRAME_Y_RADIUS
    base = 2.3

    for i, line in enumerate(lines):
        if i >= len(bool_list) or bool_list[i] is None:
            mob = VectorizedPoint()
        elif bool_list[i]:
            mob = TexMobject("\\checkmark")
            mob.set_color(GREEN)
            slot_group.shift(total_height*DOWN / (base**(i+1)))
        else:
            mob = TexMobject("\\times")
            mob.set_color(RED)
            slot_group.shift(total_height*UP / (base**(i+1)))
        mob.next_to(line, UP, SMALL_BUFF)
        slot_group.content.add(mob)
    return slot_group

def get_probability_of_slot_group(bool_list, conditioned_list = None):
    filler_tex = "Fi"*max(len(bool_list), 3)
    if conditioned_list is None:
        result = TexMobject("P(", filler_tex, ")")
    else:
        result = TexMobject("P(", filler_tex, "|", filler_tex, ")")
    fillers = result.get_parts_by_tex(filler_tex)
    for filler, bl in zip(fillers, [bool_list, conditioned_list]):
        slot_group = get_slot_group(
            bl, buff = SMALL_BUFF, include_qs = False,
        )
        slot_group.replace(filler, dim_to_match = 0)
        slot_group.shift(0.5*SMALL_BUFF*DOWN)
        index = result.index_of_part(filler)
        result.submobjects[index] = slot_group
    return result


#########

class IndependenceOpeningQuote(OpeningQuote):
    CONFIG = {
        "quote" : [
            "Far better an ", "approximate", 
            " answer to the ", " right question",
            ", which is often vague, than an ", "exact",
            " answer to the ", "wrong question", "."
        ],
        "highlighted_quote_terms" : {
            "approximate" : GREEN,
            "right" : GREEN,
            "exact" : RED,
            "wrong" : RED,
        },
        "author" : "John Tukey",
        "quote_arg_separator" : "",
    }

class DangerInProbability(Scene):
    def construct(self):
        warning = self.get_warning_sign()
        probability = TextMobject("Probability")
        probability.scale(2)

        self.play(Write(warning, run_time = 1))
        self.play(
            warning.next_to, probability, UP, LARGE_BUFF,
            LaggedStartMap(FadeIn, probability)
        )
        self.wait()


    #####

    def get_warning_sign(self):
        triangle = RegularPolygon(n = 3, start_angle = np.pi/2)
        triangle.set_stroke(RED, 12)
        triangle.set_height(2)
        bang = TextMobject("!")
        bang.set_height(0.6*triangle.get_height())
        bang.move_to(interpolate(
            triangle.get_bottom(),
            triangle.get_top(),
            0.4,
        ))
        triangle.add(bang)
        return triangle

class MeaningOfIndependence(SampleSpaceScene):
    CONFIG = {
        "sample_space_config" : {
            "height" : 4,
            "width" : 4,
        }
    }
    def construct(self):
        self.add_labeled_space()
        self.align_conditionals()
        self.relabel()
        self.assume_independence()
        self.no_independence()    

    def add_labeled_space(self):
        self.add_sample_space(**self.sample_space_config)
        self.sample_space.shift(2*LEFT)
        self.sample_space.divide_horizontally(0.3)
        self.sample_space[0].divide_vertically(
            0.9, colors = [BLUE_D, GREEN_C]
        )
        self.sample_space[1].divide_vertically(
            0.5, colors = [BLUE_E, GREEN_E]
        )
        side_braces_and_labels = self.sample_space.get_side_braces_and_labels(
            ["P(A)", "P(\\overline A)"]
        )
        top_braces_and_labels, bottom_braces_and_labels = [
            part.get_subdivision_braces_and_labels(
                part.vertical_parts,
                labels = ["P(B | %s)"%s, "P(\\overline B | %s)"%s],
                direction = vect
            )
            for part, s, vect in zip(
                self.sample_space.horizontal_parts, 
                ["A", "\\overline A"], 
                [UP, DOWN],
            )
        ]
        braces_and_labels_groups = VGroup(
            side_braces_and_labels,
            top_braces_and_labels,
            bottom_braces_and_labels,
        )

        self.add(self.sample_space)
        self.play(Write(braces_and_labels_groups, run_time = 4))

    def align_conditionals(self):
        line = Line(*[
            interpolate(
                self.sample_space.get_corner(vect+LEFT),
                self.sample_space.get_corner(vect+RIGHT),
                0.7
            )
            for vect in (UP, DOWN)
        ])
        line.set_stroke(RED, 8)
        word = TextMobject("Independence")
        word.scale(1.5)
        word.next_to(self.sample_space, RIGHT, buff = LARGE_BUFF)
        word.set_color(RED)

        self.play(*it.chain(
            self.get_top_conditional_change_anims(0.7),
            self.get_bottom_conditional_change_anims(0.7)
        ))
        self.play(
            ShowCreation(line),
            Write(word, run_time = 1)
        )
        self.wait()

        self.independence_word = word
        self.independence_line = line

    def relabel(self):
        old_labels = self.sample_space[0].vertical_parts.labels
        ignored_braces, new_top_labels = self.sample_space[0].get_top_braces_and_labels(
            ["P(B)", "P(\\overline B)"]
        )
        equation = TexMobject(
            "P(B | A) = P(B)"
        )
        equation.scale(1.5)
        equation.move_to(self.independence_word)

        self.play(
            Transform(old_labels, new_top_labels),
            FadeOut(self.sample_space[1].vertical_parts.labels),
            FadeOut(self.sample_space[1].vertical_parts.braces),
        )
        self.play(
            self.independence_word.next_to, equation, UP, MED_LARGE_BUFF,
            Write(equation)
        )
        self.wait()

        self.equation = equation

    def assume_independence(self):
        everything = VGroup(*self.get_top_level_mobjects())
        morty = Mortimer()
        morty.scale(0.7)
        morty.to_corner(DOWN+RIGHT)
        bubble = ThoughtBubble(direction = RIGHT)
        bubble.pin_to(morty)
        bubble.set_fill(opacity = 0)

        self.play(
            FadeIn(morty),
            everything.scale, 0.5,
            everything.move_to, bubble.get_bubble_center(),
        )
        self.play(
            morty.change, "hooray", everything,
            ShowCreation(bubble)
        )
        self.wait()
        self.play(Blink(morty))
        self.wait()

        self.morty = morty

    def no_independence(self):
        for part in self.sample_space.horizontal_parts:
            part.vertical_parts.labels = None
        self.play(*it.chain(
            self.get_top_conditional_change_anims(0.9),
            self.get_bottom_conditional_change_anims(0.5),
            [
                self.independence_word.fade, 0.7,
                self.equation.fade, 0.7,
                self.morty.change, "confused", self.sample_space,
                FadeOut(self.independence_line)
            ]
        ))
        self.wait()

class IntroduceBinomial(Scene):
    CONFIG = {
        "n" : 8,
        "p" : 0.7,
    }
    def construct(self):
        self.add_title()
        self.add_bar_chart()
        self.add_p_slider()
        self.write_independence_assumption()
        self.play_with_p_value(0.2, 0.5)
        self.cross_out_assumption()
        self.play_with_p_value(0.8, 0.4)
        self.shift_weight_to_tails()


    def add_title(self):
        title = TextMobject("Binomial distribution")
        title.scale(1.3)
        title.to_edge(RIGHT)
        title.shift(2*UP)

        formula = TexMobject(
            "P(X=", "k", ")=", 
            "{n \\choose k}", 
            "p", "^k",
            "(1-", "p", ")", "^{n-", "k}",
            arg_separator = ""
        )
        formula.set_color_by_tex("k", BLUE)
        formula.set_color_by_tex("p", YELLOW)
        choose_part = formula.get_part_by_tex("choose")
        choose_part.set_color(WHITE)
        choose_part[-2].set_color(BLUE)
        formula.next_to(title, DOWN, MED_LARGE_BUFF)

        self.formula = formula
        self.title = title
        self.add(title, formula)

    def add_bar_chart(self):
        n, p = self.n, self.p
        dist = get_binomial_distribution(n, p)
        chart = BarChart(
            [dist(k) for k in range(n+1)],
            bar_names = list(range(n+1)),
        )
        chart.to_edge(LEFT)
        self.bar_chart = chart

        self.play(LaggedStartMap(
            FadeIn, VGroup(*it.chain(*chart)), 
            run_time = 2
        ))

    def add_p_slider(self):
        interval = UnitInterval(color = LIGHT_GREY)
        interval.set_width(4)
        interval.next_to(
            VGroup(self.bar_chart.x_axis, self.bar_chart.y_axis), 
            UP, MED_LARGE_BUFF
        )
        interval.add_numbers(0, 1)
        triangle = RegularPolygon(
            n=3, start_angle = -np.pi/2,
            stroke_width = 0,
            fill_color = YELLOW,
            fill_opacity = 1,
        )
        triangle.set_height(0.25)
        triangle.move_to(interval.number_to_point(self.p), DOWN)
        label = TexMobject("p")
        label.next_to(triangle, UP, SMALL_BUFF)
        label.set_color(triangle.get_color())

        self.p_slider = VGroup(interval, triangle, label)
        self.play(Write(self.p_slider, run_time = 1))

    def play_with_p_value(self, *values):
        for value in values:
            self.change_p(value)
            self.wait()

    def write_independence_assumption(self):
        assumption = TextMobject("Independence assumption")
        assumption.scale(1.2)
        assumption.next_to(self.formula, DOWN, MED_LARGE_BUFF, LEFT)
        assumption.set_color(GREEN_C)

        self.play(Write(assumption, run_time = 2))
        self.wait()

        self.assumption = assumption

    def cross_out_assumption(self):
        cross = Cross(self.assumption)
        cross.set_color(GREY)
        self.bar_chart.save_state()

        self.play(ShowCreation(cross))
        self.play(self.bar_chart.fade, 0.7)
        self.wait(2)
        self.play(self.bar_chart.restore)

    def shift_weight_to_tails(self):
        chart = self.bar_chart
        chart_copy = chart.copy()
        dist = get_binomial_distribution(self.n, self.p)
        values = np.array(list(map(dist, list(range(self.n+1)))))
        values += 0.1
        values /= sum(values)

        old_bars = chart.bars
        old_bars.generate_target()
        new_bars = chart_copy.bars
        for bars, vect in (old_bars.target, LEFT), (new_bars, RIGHT):
            for bar in bars:
                corner = bar.get_corner(DOWN+vect)
                bar.stretch(0.5, 0)
                bar.move_to(corner, DOWN+vect)
        old_bars.target.set_color(RED)
        old_bars.target.fade()

        self.play(
            MoveToTarget(old_bars),
            ReplacementTransform(
                old_bars.copy().set_fill(opacity = 0),
                new_bars
            )
        )
        self.play(
            chart_copy.change_bar_values, values
        )
        self.wait(2)



    #####

    def change_p(self, p):
        interval, triangle, p_label = self.p_slider
        alt_dist = get_binomial_distribution(self.n, p)
        self.play(
            ApplyMethod(
                self.bar_chart.change_bar_values,
                [alt_dist(k) for k in range(self.n+1)],
            ),
            triangle.move_to, interval.number_to_point(p), DOWN,
            MaintainPositionRelativeTo(p_label, triangle)
        )
        self.p = p

class IntroduceQuiz(PiCreatureScene):
    def construct(self):
        self.add_quiz()
        self.ask_about_probabilities()
        self.show_distribution()
        self.show_single_question_probability()

    def add_quiz(self):
        quiz = self.get_example_quiz()
        quiz.next_to(self.randy, UP+RIGHT)

        self.play(
            Write(quiz),
            self.randy.change, "pondering", quiz
        )
        self.wait()

        self.quiz = quiz

    def ask_about_probabilities(self):
        probabilities, abbreviated_probabilities = [
            VGroup(*[
                TexMobject(
                    "P(", s_tex, "=", str(score), ")", rhs
                ).set_color_by_tex_to_color_map({
                    str(score) : YELLOW,
                    "text" : GREEN,
                })
                for score in range(4)
            ])
            for s_tex, rhs in [
                ("\\text{Score}", "= \\, ???"),
                ("\\text{S}", "")
            ]
        ]
        for group in probabilities, abbreviated_probabilities:
            group.arrange(
                DOWN, 
                buff = MED_LARGE_BUFF,
                aligned_edge = LEFT
            )
            group.to_corner(UP+LEFT)

        self.play(
            LaggedStartMap(FadeIn, probabilities, run_time = 3),
            self.quiz.set_height, 0.7*self.randy.get_height(),
            self.quiz.next_to, self.randy, RIGHT,
            self.randy.change, "confused", probabilities
        )
        self.wait()

        self.probabilities = probabilities
        self.abbreviated_probabilities = abbreviated_probabilities

    def show_distribution(self):
        dist = get_binomial_distribution(3, 0.7)
        values = list(map(dist, list(range(4))))
        chart = BarChart(
            values, 
            width = 7,
            bar_names = list(range(4))
        )
        chart.to_edge(RIGHT)
        for short_p, bar in zip(self.abbreviated_probabilities, chart.bars):
            short_p.set_width(1.75*bar.get_width())
            short_p.next_to(bar, UP)

        self.play(
            LaggedStartMap(Write, VGroup(
                *[m for m in chart if m is not chart.bars]
            )),
        )
        self.play(*[
            ReplacementTransform(
                bar.copy().stretch_to_fit_height(0).move_to(bar.get_bottom()),
                bar
            )
            for bar in chart.bars
        ])
        self.play(*[
            ReplacementTransform(p.copy(), short_p)
            for p, short_p in zip(
                self.probabilities,
                self.abbreviated_probabilities,
            )
        ])
        self.wait()

        self.bar_chart = chart

    def show_single_question_probability(self):
        prob = TexMobject(
            "P(", "\\text{Can answer a given question}", ")",
            "= 0.8"
        )
        prob.to_corner(UP+RIGHT)
        prob.set_color_by_tex("text", GREEN)
        rect = SurroundingRectangle(prob, buff = MED_SMALL_BUFF)

        self.play(
            Write(prob),
            self.randy.change, "happy", prob
        )
        self.play(ShowCreation(rect))
        self.wait()

        self.single_question_probability = VGroup(
            prob, rect
        )


    ######

    def create_pi_creature(self):
        randy = Randolph()
        randy.scale(0.7)
        randy.to_corner(DOWN+LEFT)
        self.randy = randy
        return randy

    def get_example_quiz(self):
        return get_quiz(
            "Define ``Brachistochrone'' ",
            "Define ``Tautochrone'' ",
            "Define ``Cycloid'' ",
        )

class BreakDownQuestionPatterns(IntroduceQuiz):
    def construct(self):
        self.add_parts_from_last_scene()
        self.break_down_possibilities()
        self.count_patterns()

    def add_parts_from_last_scene(self):
        self.force_skipping()
        IntroduceQuiz.construct(self)
        self.revert_to_original_skipping_status()

        chart_group = VGroup(
            self.bar_chart,
            self.abbreviated_probabilities
        )
        self.play(
            self.single_question_probability.scale, 0.8,
            self.single_question_probability.to_corner, UP+LEFT,
            chart_group.scale, 0.7, chart_group.get_top(),
            chart_group.to_edge, LEFT,
            FadeOut(self.probabilities)
        )

    def break_down_possibilities(self):
        slot_group_groups = VGroup(*[VGroup() for x in range(4)])
        bool_lists = [[]]
        while bool_lists:
            bool_list = bool_lists.pop()
            slot_group = self.get_slot_group(bool_list)
            slot_group_groups[len(bool_list)].add(slot_group)
            if len(bool_list) < 3:
                bool_lists += [
                    list(bool_list) + [True],
                    list(bool_list) + [False],
                ]

        group_group = slot_group_groups[0]
        self.revert_to_original_skipping_status()
        self.play(Write(group_group, run_time = 1))
        self.wait()
        for new_group_group in slot_group_groups[1:]:
            self.play(Transform(group_group, new_group_group))
            self.wait(2)

        self.slot_groups = slot_group_groups[-1]

    def count_patterns(self):
        brace = Brace(self.slot_groups, LEFT)
        count = TexMobject("2^3 = 8")
        count.next_to(brace, LEFT)

        self.play(
            GrowFromCenter(brace),
            Write(count)
        )
        self.wait()

    #######

    def get_slot_group(self, bool_list):
        return get_slot_group(bool_list, include_qs = len(bool_list) < 3)

class AssociatePatternsWithScores(BreakDownQuestionPatterns):
    CONFIG = {
        "score_group_scale_val" : 0.8,
    }
    def construct(self):
        self.add_slot_groups()
        self.show_score_groups()
        self.think_about_binomial_patterns()

    def add_slot_groups(self):
        self.slot_groups = VGroup(*list(map(
            self.get_slot_group,
            it.product(*[[True, False]]*3)
        )))
        self.add(self.slot_groups)
        self.remove(self.randy)

    def show_score_groups(self):
        score_groups = [VGroup() for x in range(4)]
        scores = VGroup()
        full_score_groups = VGroup()

        for slot_group in self.slot_groups:
            score_groups[sum(slot_group.bool_list)].add(slot_group)
        for i, score_group in enumerate(score_groups):
            score = TextMobject("Score", "=", str(i))
            score.set_color_by_tex("Score", GREEN)
            scores.add(score)
            score_group.organized = score_group.deepcopy()
            score_group.organized.arrange(UP, buff = SMALL_BUFF)
            score_group.organized.scale(self.score_group_scale_val)
            brace = Brace(score_group.organized, LEFT)
            score.next_to(brace, LEFT)
            score.add(brace)
            full_score_groups.add(VGroup(score, score_group.organized))
        full_score_groups.arrange(
            DOWN, buff = MED_LARGE_BUFF,
            aligned_edge = RIGHT
        )
        full_score_groups.to_edge(LEFT)

        for score, score_group in zip(scores, score_groups):
            score_group.save_state()
            self.play(score_group.next_to, score_group, LEFT, MED_LARGE_BUFF)
            self.wait()
            self.play(
                ReplacementTransform(
                    score_group.copy(), score_group.organized
                ),
                LaggedStartMap(FadeIn, score, run_time = 1)
            )
            self.play(score_group.restore)
        self.wait()

    def think_about_binomial_patterns(self):
        triangle = PascalsTriangle(
            nrows = 5,
            height = 3,
            width = 3,
        )
        triangle.to_edge(UP+RIGHT)
        row = VGroup(*[
            triangle.coords_to_mobs[3][k]
            for k in range(4)
        ])
        self.randy.center().to_edge(DOWN)
        bubble = ThoughtBubble()
        bubble.add_content(triangle)
        bubble.resize_to_content()
        triangle.shift(SMALL_BUFF*(3*UP + RIGHT))
        bubble.add(triangle)
        bubble.next_to(self.randy, UP+RIGHT, SMALL_BUFF)
        bubble.remove(triangle)

        self.play(
            FadeOut(self.slot_groups),
            FadeIn(self.randy),
            FadeIn(bubble)
        )
        self.play(
            self.randy.change, "pondering",
            LaggedStartMap(FadeIn, triangle, run_time = 4),
        )
        self.play(row.set_color, YELLOW)
        self.wait(4)

class BeforeCounting(TeacherStudentsScene):
    def construct(self):
        triangle = PascalsTriangle(nrows = 7)
        triangle.set_height(4)
        triangle.next_to(self.teacher, UP+LEFT)

        prob = get_probability_of_slot_group([True, True, False])
        prob.to_edge(UP)
        brace = Brace(prob, DOWN)
        q_marks = brace.get_text("???")

        self.teacher.change_mode("raise_right_hand")
        self.add(triangle)
        self.change_student_modes(*["hooray"]*3)
        self.play(
            triangle.scale, 0.5,
            triangle.to_corner, UP+RIGHT,
            self.teacher.change_mode, "sassy"
        )
        self.change_student_modes(*["confused"]*3)
        self.play(Write(prob))
        self.play(
            GrowFromCenter(brace),
            LaggedStartMap(FadeIn, q_marks)
        )
        self.wait(2)

class TemptingButWrongCalculation(BreakDownQuestionPatterns):
    def construct(self):
        self.add_title()
        self.write_simple_product()

    def add_title(self):
        title = TextMobject("Tempting$\\dots$")
        title.scale(1.5)
        title.to_edge(UP)
        self.add(title)
        self.title = title

    def write_simple_product(self):
        lhs = TexMobject("P\\big(", "Filler Blah", "\\big)", "= ")
        lhs.next_to(ORIGIN, UP+LEFT)
        p_of = lhs.get_part_by_tex("P\\big(")
        filler = lhs.get_part_by_tex("Filler")
        rp = lhs.get_part_by_tex("\\big)")
        slot_group = self.get_slot_group([True, True, False])
        slot_group.replace(filler, dim_to_match = 0)
        lhs.submobjects.remove(filler)

        rhs = VGroup(*[
            TexMobject("P(", "\\checkmark" if b else "\\times", ")")
            for b in slot_group.bool_list
        ])
        rhs.arrange(RIGHT, SMALL_BUFF)
        rhs.next_to(lhs, RIGHT, SMALL_BUFF)
        for part, b in zip(rhs, slot_group.bool_list):
            part.set_color_by_tex_to_color_map({
                "checkmark" : GREEN,
                "times" : RED,
            })
            brace = Brace(part, UP)
            if b:
                value = TexMobject("(0.8)")
            else:
                value = TexMobject("(0.2)")
            value.set_color(part[1].get_color())
            value.next_to(brace, UP)
            part.brace = brace
            part.value = value

        question = TextMobject("What about correlations?")
        question.next_to(rhs, DOWN, LARGE_BUFF)

        self.play(
            Write(lhs),
            ShowCreation(slot_group.lines),
            LaggedStartMap(FadeIn, slot_group.content, run_time = 3),
            self.randy.change, "pondering"
        )
        self.wait(2)
        for part, mob in zip(rhs, slot_group.content):
            self.play(*[
                ReplacementTransform(
                    mob.copy(), subpart,
                    path_arc = np.pi/6
                )
                for subpart, mob in zip(part, [
                    p_of, mob, rp
                ])
            ])
            self.play(GrowFromCenter(part.brace))
            self.play(FadeIn(part.value))
            self.wait()
        self.wait()
        self.play(
            Write(question),
            self.randy.change, "confused"
        )
        self.wait(3)

        self.question = question
        self.rhs = rhs

class ThousandPossibleQuizzes(Scene):
    CONFIG = {
        "n_quiz_rows" : 25,
        "n_quiz_cols" : 40,
        "n_movers" : 100,
        # "n_quiz_rows" : 5,
        # "n_quiz_cols" : 8,
        # "n_movers" : 4,
        "quizzes_height" : 4,
    }
    def construct(self):
        self.draw_all_quizzes()
        self.show_division_by_first_question()
        self.ask_about_second_question()
        self.show_uncorrelated_division_by_second()
        self.increase_second_correct_slice()
        self.second_division_among_first_wrong()
        self.show_that_second_is_still_80()
        self.emphasize_disproportionate_divide()
        self.show_third_question_results()

    def draw_all_quizzes(self):
        quizzes = self.get_thousand_quizzes()
        title = TextMobject("$1{,}000$ possible quizzes")
        title.scale(1.5)
        title.next_to(quizzes, UP)
        full_quizzes = VGroup(
            get_quiz(
                "Define ``Brachistochrone''",
                "Define ``Tautochrone''",
                "Define ``Cycloid''",
            ),
            get_quiz(
                "Define $\\dfrac{df}{dx}$",
                "Define $\\displaystyle \\lim_{h \\to 0} f(h)$",
                "Prove $\\dfrac{d(x^2)}{dx} = 2x$ ",
            ),
            get_quiz(
                "Find all primes $p$ \\\\ where $p+2$ is prime.",
                "Find all primes $p$ \\\\ where $2^{p}-1$ is prime.",
                "Solve $\\zeta(s) = 0$",
            ),
        )
        full_quizzes.arrange(RIGHT)
        target_quizzes = VGroup(*quizzes[:len(full_quizzes)])

        for quiz in full_quizzes:
            self.play(FadeIn(quiz, run_time = 3, lag_ratio = 0.5))
        self.play(
            Transform(full_quizzes, target_quizzes),
            FadeIn(title)
        )
        self.play(
            LaggedStartMap(
                FadeIn, quizzes, 
                run_time = 3,
                lag_ratio = 0.2,
            ),
            Animation(full_quizzes, remover = True)
        )
        self.wait()

        self.quizzes = quizzes
        self.title = title

    def show_division_by_first_question(self):
        n = int(0.8*len(self.quizzes))
        top_split = VGroup(*self.quizzes[:n])
        bottom_split = VGroup(*self.quizzes[n:])
        for split, color, vect in (top_split, GREEN, UP), (bottom_split, RED, DOWN):
            split.sort(lambda p : p[0])
            split.generate_target()
            split.target.shift(MED_LARGE_BUFF*vect)
            for quiz in split.target:
                quiz[0].set_color(color)

        labels = VGroup()
        for num, b, split in (800, True, top_split), (200, False, bottom_split):
            label = VGroup(
                TexMobject(str(num)),
                get_slot_group([b], buff = SMALL_BUFF, include_qs = False)
            )
            label.arrange(DOWN)
            label.next_to(split.target, LEFT, buff = LARGE_BUFF)
            labels.add(label)

        self.play(
            FadeOut(self.title),
            MoveToTarget(top_split),
            MoveToTarget(bottom_split),
        )
        for label in labels:
            self.play(FadeIn(label))
            self.wait()

        self.splits = VGroup(top_split, bottom_split)
        self.q1_split_labels = labels

    def ask_about_second_question(self):
        top_split = self.splits[0]
        sg1, sg2 = slot_groups = VGroup(*[
            get_slot_group(
                [True, b], 
                include_qs = False,
                buff = SMALL_BUFF
            )
            for b in (True, False)
        ])
        question = VGroup(
            TextMobject("Where are"), sg1,
            TextMobject("and"), sg2, TextMobject("?"),
        )
        question.arrange(RIGHT, aligned_edge = DOWN)
        question[-1].next_to(question[-2], RIGHT, SMALL_BUFF)
        question.next_to(top_split, UP, MED_LARGE_BUFF)
        slot_groups.shift(SMALL_BUFF*DOWN)
        little_rects = VGroup(*[
            SurroundingRectangle(
                VGroup(sg.lines[1], sg.content[1])
            )
            for sg in slot_groups
        ])
        big_rect = SurroundingRectangle(top_split)

        self.play(Write(question))
        self.play(ShowCreation(little_rects))
        self.wait()
        self.play(FadeOut(little_rects))
        self.play(ShowCreation(big_rect))
        self.play(
            FadeOut(big_rect),
            FadeOut(question),
        )
        self.wait()

    def show_uncorrelated_division_by_second(self):
        top_split = self.splits[0]
        top_label = self.q1_split_labels[0]
        n = int(0.8*len(top_split))
        left_split = VGroup(*top_split[:n])
        right_split = VGroup(*top_split[n:])
        for split, color in (left_split, GREEN_E), (right_split, RED_E):
            split.generate_target()
            for quiz in split.target:
                quiz[1].set_color(color)
        left_split.target.shift(LEFT)

        left_label = VGroup(
            TexMobject("(0.8)", "800 =", "640"),
            get_slot_group([True, True], buff = SMALL_BUFF, include_qs = False)
        )
        left_label.arrange(RIGHT, buff = MED_LARGE_BUFF)
        left_label.next_to(left_split.target, UP)

        self.play(
            MoveToTarget(left_split),
            MaintainPositionRelativeTo(top_label, left_split),
            MoveToTarget(right_split),
        )
        self.play(FadeIn(left_label))
        self.play(LaggedStartMap(
            ApplyMethod, left_split,
            lambda m : (m.set_color, YELLOW),
            rate_func = there_and_back,
            lag_ratio = 0.2,
        ))
        self.wait()

        self.top_left_label = left_label
        self.top_splits = VGroup(left_split, right_split)

    def increase_second_correct_slice(self):
        left_split, right_split = self.top_splits
        left_label = self.top_left_label
        left_label_equation = left_label[0]
        movers = VGroup(*right_split[:self.n_movers])
        movers.generate_target()
        for quiz in movers.target:
            quiz[1].set_color(left_split[0][1].get_color())
        movers.target.shift(LEFT)

        new_equation = TexMobject("(0.925)", "800 =", "740")
        for i in 0, 2:
            new_equation[i].set_color(YELLOW)
        new_equation.move_to(left_label_equation)

        self.play(
            MoveToTarget(
                movers, 
                lag_ratio = 0.5,
                run_time = 3,
            ),
            Transform(left_label_equation, new_equation)
        )
        self.wait(2)
        self.play(Indicate(left_label_equation[0]))
        self.wait()

        left_split.add(*movers)
        right_split.remove(*movers)
        self.top_left_split = left_split
        self.top_right_split = right_split
        self.top_movers = movers
        self.top_equation = left_label_equation

    def second_division_among_first_wrong(self):
        top_label, bottom_label = self.q1_split_labels
        top_split, bottom_split = self.splits
        top_left_label = self.top_left_label
        top_group = VGroup(top_split, top_left_label, top_label)

        n = int(0.8*len(bottom_split))
        left_split = VGroup(*bottom_split[:n])
        right_split = VGroup(*bottom_split[n:])
        for split, color in (left_split, GREEN_E), (right_split, RED_E):
            split.generate_target()
            for quiz in split.target:
                quiz[1].set_color(color)
        left_split.target.shift(LEFT)

        movers = VGroup(*left_split[-self.n_movers:])
        movers.generate_target()
        for quiz in movers.target:
            quiz[1].set_color(right_split.target[0][1].get_color())

        equation = TexMobject("(0.8)", "200 = ", "160")
        slot_group = get_slot_group([False, True], buff = SMALL_BUFF, include_qs = False)
        label = VGroup(equation, slot_group)
        label.arrange(DOWN, buff = SMALL_BUFF)
        label.next_to(left_split.target, UP, SMALL_BUFF, LEFT)
        alt_equation = TexMobject("(0.3)", "200 = ", "60")
        for i in 0, 2:
            alt_equation[i].set_color(YELLOW)
        alt_equation.move_to(equation)

        self.play(top_group.to_edge, UP, SMALL_BUFF)
        self.play(
            bottom_label.shift, LEFT,
            *list(map(MoveToTarget, [left_split, right_split]))
        )
        self.play(FadeIn(label))
        self.wait()
        self.play(
            MoveToTarget(
                movers, 
                lag_ratio = 0.5,
                run_time = 3,
            ),
            Transform(equation, alt_equation)
        )
        self.wait()

        left_split.remove(*movers)
        right_split.add(*movers)
        self.bottom_left_split = left_split
        self.bottom_right_split = right_split
        self.bottom_movers = movers
        self.bottom_equation = equation
        self.bottom_left_label = label

    def show_that_second_is_still_80(self):
        second_right = VGroup(
            self.bottom_left_split, self.top_left_split
        )
        second_wrong = VGroup(
            self.bottom_right_split, self.top_right_split
        )
        rects = VGroup(*[
            SurroundingRectangle(mob, buff = SMALL_BUFF)
            for mob in second_right
        ])

        num1 = self.top_equation[-1].copy()
        num2 = self.bottom_equation[-1].copy()

        equation = TexMobject("740", "+", "60", "=", "800")
        for tex in "740", "60":
            equation.set_color_by_tex(tex, YELLOW)
        slot_group = get_slot_group([True, True])
        slot_group.content[0].set_fill(BLACK, 0)
        label = VGroup(equation, slot_group)
        label.arrange(DOWN)
        label.next_to(self.quizzes, LEFT, LARGE_BUFF)

        self.play(
            FadeOut(self.q1_split_labels),
            ShowCreation(rects)
        )
        self.play(
            FadeIn(slot_group),
            Transform(
                num1, equation[0],
                rate_func = squish_rate_func(smooth, 0, 0.7),
            ),
            Transform(
                num2, equation[2],
                rate_func = squish_rate_func(smooth, 0.3, 1),
            ),
            run_time = 2
        )
        self.play(
            Write(equation),
            *list(map(Animation, [num1, num2]))
        )
        self.remove(num1, num2)
        self.wait()
        self.play(FadeOut(rects))

    def emphasize_disproportionate_divide(self):
        top_movers = self.top_movers
        bottom_movers = self.bottom_movers
        both_movers = VGroup(top_movers, bottom_movers)
        both_movers.save_state()

        top_movers.target = bottom_movers.copy().shift(LEFT)
        bottom_movers.target = top_movers.copy().shift(RIGHT)
        for quiz in top_movers.target:
            quiz[0].set_color(RED)
        for quiz in bottom_movers.target:
            quiz[0].set_color(GREEN)

        line = Line(UP, DOWN, color = YELLOW)
        line.set_height(self.quizzes.get_height())
        line.next_to(bottom_movers.target, LEFT, MED_LARGE_BUFF, UP)

        self.revert_to_original_skipping_status()
        self.play(*list(map(MoveToTarget, both_movers)))
        self.play(ShowCreation(line))
        self.play(FadeOut(line))
        self.wait()
        self.play(both_movers.restore)
        self.wait()

    def show_third_question_results(self):
        all_splits = VGroup(
            self.top_left_split, self.top_right_split,
            self.bottom_left_split, self.bottom_right_split
        )
        proportions = [0.9, 0.8, 0.8, 0.4]
        for split, prop in zip(all_splits, proportions):
            n = int(prop*len(split))
            split.sort(lambda p : -p[1])
            split.generate_target()
            top_part = VGroup(*split.target[:n])
            top_part.shift(MED_SMALL_BUFF*UP)
            bottom_part = VGroup(*split.target[n:])
            bottom_part.shift(MED_SMALL_BUFF*DOWN)
            for quiz in top_part:
                quiz[-1].set_color(GREEN)
            for quiz in bottom_part:
                quiz[-1].set_color(RED)

        split = self.top_left_split
        n_all_right = int(proportions[0]*len(split))
        all_right = VGroup(*split[:n_all_right])

        self.play(
            FadeOut(self.top_left_label),
            FadeOut(self.bottom_left_label),
        )
        for split in all_splits:
            self.play(MoveToTarget(split))
        self.wait()
        self.play(LaggedStartMap(
            ApplyMethod, all_right,
            lambda m : (m.set_color, YELLOW),
            rate_func = there_and_back,
            lag_ratio = 0.2,
            run_time = 2
        ))
        self.wait(2)

    #####

    def get_thousand_quizzes(self):
        rows = VGroup()
        for x in range(self.n_quiz_rows):
            quiz = VGroup(*[
                Rectangle(
                    height = SMALL_BUFF,
                    width = 0.5*SMALL_BUFF
                )
                for x in range(3)
            ])
            quiz.arrange(RIGHT, buff = 0)
            quiz.set_stroke(width = 0)
            quiz.set_fill(LIGHT_GREY, 1)
            row = VGroup(*[quiz.copy() for y in range(self.n_quiz_cols)])
            row.arrange(RIGHT, buff = SMALL_BUFF)
            rows.add(row)

        rows.arrange(DOWN, buff = SMALL_BUFF)
        quizzes = VGroup(*it.chain(*rows))
        quizzes.set_height(self.quizzes_height)
        quizzes.to_edge(RIGHT)
        quizzes.shift(MED_LARGE_BUFF*DOWN)
        return quizzes

class ExampleConditional(Scene):
    def construct(self):
        prob = get_probability_of_slot_group(
            [True, True], [True]
        )
        rhs = TexMobject("=", "0.925", ">", "0.8")
        rhs.set_color_by_tex("0.925", YELLOW)
        rhs.next_to(prob, RIGHT)
        expression = VGroup(prob, rhs)
        expression.set_width(FRAME_WIDTH - 1)
        expression.center().to_edge(DOWN)

        self.play(Write(expression))
        self.wait()

class HarderQuizzes(Scene):
    def construct(self):
        quizzes = VGroup(
            get_quiz(
                "Find all primes $p$ \\\\ where $p+2$ is prime.",
                "Find all primes $p$ \\\\ where $2^{p}-1$ is prime.",
                "Solve $\\zeta(s) = 0$",
            ),
            get_quiz(
                "Find $S$ such that \\\\ $\\#\\mathds{N} < \\#S < \\#\\mathcal{P}(\\mathds{N})$",
                "Describe ``forcing''",
                "Prove from ZFC that $S \\notin S$.",
            ),
        )
        quizzes.arrange(RIGHT)
        quizzes.to_edge(DOWN)
        crosses = VGroup(*[
            Cross(quiz.questions[0])
            for quiz in quizzes
        ])

        for quiz in quizzes:
            self.play(FadeIn(quiz))
        self.wait()
        for cross in crosses:
            self.play(ShowCreation(cross))
        self.wait()

class WritePSecond(Scene):
    def construct(self):
        prob = get_probability_of_slot_group([None, True, None])
        rhs = TexMobject("= 0.8")
        rhs.next_to(prob, RIGHT)
        prob.add(rhs)
        prob.set_width(FRAME_WIDTH - 1)
        prob.center().to_edge(DOWN)
        self.play(Write(prob))

class SubmitToTemptation(TemptingButWrongCalculation):
    def construct(self):
        self.force_skipping()
        TemptingButWrongCalculation.construct(self)
        self.revert_to_original_skipping_status()

        title = self.title
        question = self.question
        title.generate_target()
        title.target.scale_in_place(1./1.5)
        new_words = TextMobject("and", "okay", "assuming independence.")
        new_words.set_color_by_tex("okay", GREEN)
        new_words.next_to(title.target, RIGHT)
        VGroup(title.target, new_words).center().to_edge(UP)

        self.play(
            MoveToTarget(title),
            FadeOut(question)
        )
        self.play(
            Write(new_words, run_time = 2),
            self.randy.change, "hooray"
        )
        for part in self.rhs:
            self.play(Indicate(part.value))
        self.wait()

class AccurateProductRule(SampleSpaceScene, ThreeDScene):
    def construct(self):
        self.setup_terms()
        self.add_sample_space()
        self.wait()
        self.show_first_division()
        self.show_second_division()
        self.move_to_third_dimension()
        self.show_final_probability()
        self.show_confusion()

    def setup_terms(self):
        filler_tex = "Filler"
        lhs = TexMobject("P(", filler_tex, ")", "=")
        p1 = TexMobject("P(", filler_tex, ")")
        p2 = TexMobject("P(", filler_tex, "|", filler_tex, ")")
        p3 = TexMobject("P(", filler_tex, "|", filler_tex, ")")
        terms = VGroup(lhs, p1, p2, p3)
        terms.arrange(RIGHT, buff = SMALL_BUFF)
        terms.to_edge(UP, buff = LARGE_BUFF)

        kwargs = {"buff" : SMALL_BUFF, "include_qs" : False}
        slot_group_lists = [
            [get_slot_group([True, True, False], **kwargs)],
            [get_slot_group([True], **kwargs)],
            [
                get_slot_group([True, True], **kwargs),
                get_slot_group([True], **kwargs),
            ],
            [
                get_slot_group([True, True, False], **kwargs),
                get_slot_group([True, True], **kwargs),
            ],
        ]
        for term, slot_group_list in zip(terms, slot_group_lists):
            parts = term.get_parts_by_tex(filler_tex)
            for part, slot_group in zip(parts, slot_group_list):
                slot_group.replace(part, dim_to_match = 0)
                term.submobjects[term.index_of_part(part)] = slot_group
        # terms[2][1].content[0].set_fill(BLACK, 0)
        # VGroup(*terms[3][1].content[:2]).set_fill(BLACK, 0)

        value_texs = ["0.8", ">0.8", "<0.2"]
        for term, tex in zip(terms[1:], value_texs):
            term.value = TexMobject(tex)
            term.value.next_to(term, UP)

        self.terms = terms
        self.add(terms[0])

    def add_sample_space(self):
        SampleSpaceScene.add_sample_space(self, height = 4, width = 5)
        self.sample_space.to_edge(DOWN)

    def show_first_division(self):
        space = self.sample_space
        space.divide_horizontally(
            [0.8], colors = [GREEN_E, RED_E]
        )
        space.horizontal_parts.fade(0.1)
        top_label = self.terms[1].copy()
        bottom_label = top_label.copy()
        slot_group = get_slot_group([False], buff = SMALL_BUFF, include_qs = False)
        slot_group.replace(bottom_label[1])
        Transform(bottom_label[1], slot_group).update(1)
        braces_and_labels = space.get_side_braces_and_labels(
            [top_label, bottom_label]
        )

        self.play(
            FadeIn(space.horizontal_parts),
            FadeIn(braces_and_labels)
        )
        self.play(ReplacementTransform(
            top_label.copy(), self.terms[1]
        ))
        self.wait()
        self.play(Write(self.terms[1].value))
        self.wait()

        space.add(braces_and_labels)
        self.top_part = space.horizontal_parts[0]

    def show_second_division(self):
        space = self.sample_space
        top_part = self.top_part
        green_red_mix = average_color(GREEN_E, RED_E)
        top_part.divide_vertically(
            [0.9], colors = [GREEN_E, green_red_mix]
        )
        label = self.terms[2].deepcopy()
        braces_and_labels = top_part.get_top_braces_and_labels(
            labels = [label]
        )

        self.play(
            FadeIn(top_part.vertical_parts),
            FadeIn(braces_and_labels)
        )
        self.play(ReplacementTransform(
            label.copy(), self.terms[2]
        ))
        self.wait()
        self.play(Write(self.terms[2].value))
        self.wait()

        space.add(braces_and_labels)
        self.top_left_part = top_part.vertical_parts[0]

    def move_to_third_dimension(self):
        space = self.sample_space
        part = self.top_left_part
        cubes = VGroup(
            Cube(fill_color = RED_E),
            Cube(fill_color = GREEN_E),
        )
        cubes.set_fill(opacity = 0)
        cubes.stretch_to_fit_width(part.get_width())
        cubes.stretch_to_fit_height(part.get_height())
        cubes[1].move_to(part, IN)
        cubes[0].stretch(0.2, 2)
        cubes[0].move_to(cubes[1].get_edge_center(OUT), IN)
        space.add(cubes)

        self.play(
            space.rotate, 0.9*np.pi/2, LEFT,
            space.rotate, np.pi/12, UP,
            space.to_corner, DOWN+RIGHT, LARGE_BUFF
        )
        space.remove(cubes)
        self.play(
            cubes[0].set_fill, None, 1,
            cubes[0].set_stroke, WHITE, 1,
            cubes[1].set_fill, None, 0.5,
            cubes[1].set_stroke, WHITE, 1,
        )
        self.wait()

        self.cubes = cubes

    def show_final_probability(self):
        cube = self.cubes[0]
        face = cube[2]
        points = face.get_anchors()
        line = Line(points[2], points[3])
        line.set_stroke(YELLOW, 8)
        brace = Brace(line, LEFT)
        label = self.terms[3].copy()
        label.next_to(brace, LEFT)

        self.play(
            GrowFromCenter(brace),
            FadeIn(label),
        )
        self.wait()
        self.play(ReplacementTransform(
            label.copy(), self.terms[3]
        ))
        self.wait()

    def show_confusion(self):
        randy = Randolph()
        randy.to_corner(DOWN+LEFT)

        self.play(FadeIn(randy))
        self.play(randy.change, "confused", self.terms)
        self.play(randy.look_at, self.cubes)
        self.play(Blink(randy))
        self.play(randy.look_at, self.terms)
        self.wait()

class ShowAllEightConditionals(Scene):
    def construct(self):
        self.show_all_conditionals()
        self.suggest_independence()

    def show_all_conditionals(self):
        equations = VGroup()
        filler_tex = "Filler"
        for bool_list in it.product(*[[True, False]]*3):
            equation = TexMobject(
                "P(", filler_tex, ")", "=",
                "P(", filler_tex, ")",
                "P(", filler_tex, "|", filler_tex, ")",
                "P(", filler_tex, "|", filler_tex, ")",
            )
            sub_bool_lists = [
                bool_list[:n] for n in (3, 1, 2, 1, 3, 2)
            ]
            parts = equation.get_parts_by_tex(filler_tex)
            for part, sub_list in zip(parts, sub_bool_lists):
                slot_group = get_slot_group(
                    sub_list, 
                    buff = SMALL_BUFF,
                    include_qs = False
                )
                slot_group.replace(part, dim_to_match = 0)
                index = equation.index_of_part(part)
                equation.submobjects[index] = slot_group
            equations.add(equation)
        equations.arrange(DOWN)

        rect = SurroundingRectangle(
            VGroup(*equations[0][7:], *equations[-1][7:]),
            buff = SMALL_BUFF
        )
        rect.shift(0.5*SMALL_BUFF*RIGHT)

        self.play(LaggedStartMap(
            FadeIn, equations,
            run_time = 5,
            lag_ratio = 0.3
        ))
        self.wait()
        self.play(ShowCreation(rect, run_time = 2))
        self.play(FadeOut(rect))
        self.wait()

    def suggest_independence(self):
        full_screen_rect = FullScreenFadeRectangle()
        randy = Randolph()
        randy.to_corner(DOWN+LEFT)


        self.play(
            FadeIn(full_screen_rect),
            FadeIn(randy)
        )
        self.play(PiCreatureSays(
            randy, "Let's just assume \\\\ independence.",
            target_mode = "shruggie"
        ))
        self.play(Blink(randy))
        self.wait()

class ShowIndependenceSymbolically(Scene):
    def construct(self):
        filler_tex = "Filler"
        rhs = TexMobject("=", "0.8")
        rhs.set_color_by_tex("0.8", YELLOW)
        rhs.next_to(ORIGIN, RIGHT, LARGE_BUFF)
        lhs = TexMobject("P(", filler_tex, "|", filler_tex, ")")
        lhs.next_to(rhs, LEFT)
        VGroup(lhs, rhs).scale(1.5)
        for part in lhs.get_parts_by_tex(filler_tex):
            slot_group = get_slot_group(
                [True, True, True],
                buff = SMALL_BUFF,
                include_qs = False,
            )
            slot_group.replace(part, dim_to_match = 0)
            lhs.submobjects[lhs.index_of_part(part)] = slot_group
        VGroup(*lhs[1].content[:2]).set_fill(BLACK, 0)
        condition = lhs[3]
        condition.content[2].set_fill(BLACK, 0)
        bool_lists = [
            [False], [True, False], [False, True], [True],
        ]
        arrow = Arrow(UP, DOWN)
        arrow.next_to(condition, UP)
        arrow.set_color(RED)
        words = TextMobject("Doesn't matter")
        words.set_color(RED)
        words.next_to(arrow, UP)

        self.add(rhs, lhs, arrow, words)
        self.wait()
        for bool_list in bool_lists:
            slot_group = get_slot_group(bool_list, SMALL_BUFF, False)
            slot_group.replace(condition)
            slot_group.move_to(condition, DOWN)
            self.play(Transform(condition, slot_group))
            self.wait()
            
class ComputeProbabilityOfOneWrong(Scene):
    CONFIG = {
        "score" : 2,
        "final_result_rhs_tex" : [
            "3", "(0.8)", "^2", "(0.2)", "=", "0.384",
        ],
        "default_bool" : True,
        "default_p" : "0.8",
        "default_q" : "0.2",
    }
    def construct(self):
        self.show_all_three_patterns()
        self.show_final_result()

    def show_all_three_patterns(self):
        probabilities = VGroup()
        point_8s = VGroup()
        point_2s = VGroup()
        for i in reversed(list(range(3))):
            bool_list = [self.default_bool]*3
            bool_list[i] = not self.default_bool
            probs = ["(%s)"%self.default_p]*3
            probs[i] = "(%s)"%self.default_q
            lhs = get_probability_of_slot_group(bool_list)
            rhs = TexMobject("=", *probs)
            rhs.set_color_by_tex("0.8", GREEN)
            rhs.set_color_by_tex("0.2", RED)
            point_8s.add(*rhs.get_parts_by_tex("0.8"))
            point_2s.add(*rhs.get_parts_by_tex("0.2"))
            rhs.next_to(lhs, RIGHT)
            probabilities.add(VGroup(lhs, rhs))
        probabilities.arrange(DOWN, buff = LARGE_BUFF)
        probabilities.center()

        self.play(Write(probabilities[0]))
        self.wait(2)
        for i in range(2):
            self.play(ReplacementTransform(
                probabilities[i].copy(),
                probabilities[i+1]
            ))
        self.wait()
        for group in point_8s, point_2s:
            self.play(LaggedStartMap(
                Indicate, group,
                rate_func = there_and_back,
                lag_ratio = 0.7
            ))
            self.wait()

    def show_final_result(self):
        result = TexMobject(
            "P(", "\\text{Score} = %s"%self.score, ")", "=",
            *self.final_result_rhs_tex
        )
        result.set_color_by_tex_to_color_map({
            "0.8" : GREEN,
            "0.2" : RED,
            "Score" : YELLOW,
        })
        result[-1].set_color(YELLOW)
        result.set_color_by_tex("0.8", GREEN)
        result.set_color_by_tex("0.2", RED)
        result.to_edge(UP)

        self.play(Write(result))
        self.wait()

class ComputeProbabilityOfOneRight(ComputeProbabilityOfOneWrong):
    CONFIG = {
        "score" : 1,
        "final_result_rhs_tex" : [
            "3", "(0.8)", "(0.2)", "^2", "=", "0.096",
        ],
        "default_bool" : False,
        "default_p" : "0.2",
        "default_q" : "0.8",
    }

class ShowFullDistribution(Scene):
    def construct(self):
        self.add_scores_one_and_two()
        self.add_scores_zero_and_three()
        self.show_bar_chart()
        self.compare_to_binomial_pattern()
        self.show_alternate_values_of_p()

    def add_scores_one_and_two(self):
        scores = VGroup(
            TexMobject(
                "P(", "\\text{Score} = 0", ")",
                "=", "(0.2)", "^3",
                "=", "0.008",
            ),
            TexMobject(
                "P(", "\\text{Score} = 1", ")",
                "=", "3", "(0.8)", "(0.2)", "^2", 
                "=", "0.096",
            ),
            TexMobject(
                "P(", "\\text{Score} = 2", ")",
                "=", "3", "(0.8)", "^2", "(0.2)",
                "=", "0.384",
            ),
            TexMobject(
                "P(", "\\text{Score} = 3", ")",
                "=", "(0.8)", "^3",
                "=", "0.512",
            ),
        )
        scores.arrange(
            DOWN, 
            buff = MED_LARGE_BUFF,
            aligned_edge = LEFT
        )
        scores.shift(MED_LARGE_BUFF*UP)
        scores.to_edge(LEFT)
        for score in scores:
            score.set_color_by_tex_to_color_map({
                "0.8" : GREEN,
                "0.2" : RED,
            })
            score[-1].set_color(YELLOW)

        self.add(*scores[1:3])
        self.scores = scores

    def add_scores_zero_and_three(self):
        self.p_slot_groups = VGroup()

        self.wait()
        self.add_edge_score(0, UP, False)
        self.add_edge_score(3, DOWN, True)

    def add_edge_score(self, index, vect, q_bool):
        score = self.scores[index]
        prob = VGroup(*score[:3])
        brace = Brace(prob, vect)
        p_slot_group = get_probability_of_slot_group([q_bool]*3)
        p_slot_group.next_to(brace, vect)
        group = VGroup(*it.chain(p_slot_group, brace, score))

        self.play(LaggedStartMap(
            FadeIn, group,
            run_time = 2,
            lag_ratio = 0.7,
        ))
        self.wait(2)
        self.p_slot_groups.add(brace, p_slot_group)

    def show_bar_chart(self):
        p_terms = VGroup()
        to_fade = VGroup(self.p_slot_groups)
        value_mobs = VGroup()
        for score in self.scores:
            p_terms.add(VGroup(*score[:3]))
            to_fade.add(VGroup(*score[3:-1]))
            value_mobs.add(score[-1])
        dist = get_binomial_distribution(3, 0.8)
        values = list(map(dist, list(range(4))))
        chart = BarChart(
            values, bar_names = list(range(4)),
        )
        chart.shift(DOWN)

        new_p_terms = VGroup(*[
            TexMobject("P(", "S=%d"%k, ")")
            for k in range(4)
        ])
        for term, bar in zip(new_p_terms, chart.bars):
            term[1].set_color(YELLOW)
            term.set_width(1.5*bar.get_width())
            term.next_to(bar, UP)

        self.play(
            ReplacementTransform(
                value_mobs, chart.bars,
                lag_ratio = 0.5,
                run_time = 2
            )
        )
        self.play(
            LaggedStartMap(FadeIn, VGroup(*it.chain(*[
                submob 
                for submob in chart
                if submob is not chart.bars
            ]))),
            Transform(p_terms, new_p_terms),
            FadeOut(to_fade),
        )
        self.wait(2)

        chart.bar_top_labels = p_terms
        chart.add(p_terms)
        self.bar_chart = chart

    def compare_to_binomial_pattern(self):
        dist = get_binomial_distribution(3, 0.5)
        values = list(map(dist, list(range(4))))
        alt_chart = BarChart(values)
        alt_chart.move_to(self.bar_chart)
        bars = alt_chart.bars
        bars.set_fill(GREY, opacity = 0.5)
        vect = 4*UP
        bars.shift(vect)
        nums = VGroup(*list(map(TexMobject, list(map(str, [1, 3, 3, 1])))))
        for num, bar in zip(nums, bars):
            num.next_to(bar, UP)
        bars_copy = bars.copy()

        self.play(
            LaggedStartMap(FadeIn, bars),
            LaggedStartMap(FadeIn, nums),
        )
        self.wait(2)
        self.play(bars_copy.shift, -vect)
        self.play(ReplacementTransform(
            bars_copy, self.bar_chart.bars
        ))
        self.wait(2)
        self.play(
            VGroup(self.bar_chart, bars, nums).to_edge, LEFT
        )

        self.alt_bars = bars
        self.alt_bars_labels = nums

    def show_alternate_values_of_p(self):
        new_prob = TexMobject(
            "P(", "\\text{Correct}", ")", "=", "0.8"
        )
        new_prob.set_color_by_tex("Correct", GREEN)
        new_prob.shift(FRAME_X_RADIUS*RIGHT/2)
        new_prob.to_edge(UP)

        alt_ps = 0.5, 0.65, 0.25
        alt_rhss = VGroup()
        alt_charts = VGroup()
        for p in alt_ps:
            rhs = TexMobject(str(p))
            rhs.set_color(YELLOW)
            rhs.move_to(new_prob[-1])
            alt_rhss.add(rhs)

            dist = get_binomial_distribution(3, p)
            values = list(map(dist, list(range(4))))
            chart = self.bar_chart.copy()
            chart.change_bar_values(values)
            for label, bar in zip(chart.bar_top_labels, chart.bars):
                label.next_to(bar, UP)
            alt_charts.add(chart)

        self.play(FadeIn(new_prob))
        self.play(Transform(new_prob[-1], alt_rhss[0]))
        point_5_probs = self.show_point_5_probs(new_prob)
        self.wait()
        self.play(Transform(self.bar_chart, alt_charts[0]))
        self.wait()
        self.play(FadeOut(point_5_probs))
        for rhs, chart in list(zip(alt_rhss, alt_charts))[1:]:
            self.play(Transform(new_prob[-1], rhs))
            self.play(Transform(self.bar_chart, chart))
            self.wait(2)

    def show_point_5_probs(self, mob):
        probs = VGroup()
        last = mob
        for k in range(4):
            buff = MED_LARGE_BUFF
            for indices in it.combinations(list(range(3)), k):
                bool_list = np.array([False]*3)
                bool_list[list(indices)] = True
                prob = get_probability_of_slot_group(bool_list)
                rhs = TexMobject("= (0.5)^3")
                rhs.next_to(prob, RIGHT)
                prob.add(rhs)
                prob.scale(0.9)
                prob.next_to(last, DOWN, buff)
                probs.add(prob)
                last = prob
                buff = SMALL_BUFF

        self.play(LaggedStartMap(FadeIn, probs))
        self.wait()
        return probs

class ProbablyWrong(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Probably wrong!",
            run_time = 1,
        )
        self.change_student_modes(
            *["angry"]*3,
            run_time = 1
        )
        self.wait()

class ShowTrueDistribution(PiCreatureScene):
    def construct(self):
        self.force_skipping()

        self.remove(self.randy)
        self.add_title()
        self.show_distributions()
        self.show_emotion()
        self.imagine_score_0()

        self.revert_to_original_skipping_status()
        self.get_angry()

    def add_title(self):
        title = TexMobject("P(", "\\text{Correct}", ")", "=", "0.65")
        title.to_edge(UP)
        title.set_color_by_tex("Correct", GREEN)

        self.add(title)
        self.title = title

    def show_distributions(self):
        dist = get_binomial_distribution(3, 0.65)
        values = np.array(list(map(dist, list(range(4)))))
        alt_values = values + [0.2, 0, 0, 0.2]
        alt_values /= sum(alt_values)
        chart = BarChart(values, bar_names = list(range(4)))
        bars = chart.bars
        old_bars = bars.copy()
        arrows = VGroup()
        for bar, old_bar in zip(bars, old_bars):
            for mob, vect in (bar, RIGHT), (old_bar, LEFT):
                mob.generate_target()
                mob.target.do_about_point(
                    mob.get_corner(DOWN+vect),
                    mob.target.stretch, 0.5, 0
                )
            old_bar.target.set_color(average_color(RED_E, BLACK))
            old_bar.target.set_stroke(width = 0)
            arrow = Arrow(ORIGIN, UP, buff = 0, color = GREEN)
            arrow.move_to(bar.get_bottom())
            arrow.shift(3*UP)
            arrows.add(arrow)
        for arrow in arrows[1:3]:
            arrow.rotate_in_place(np.pi)
            arrow.set_color(RED)
        arrows.set_color_by_gradient(BLUE, YELLOW)

        self.add(chart)
        self.play(*list(map(MoveToTarget, it.chain(bars, old_bars))))
        self.play(
            chart.change_bar_values, alt_values,
            *list(map(ShowCreation, arrows))
        )
        self.wait(2)

        self.bar_chart = chart
        self.old_bars = old_bars

    def show_emotion(self):
        randy = self.randy

        self.play(FadeIn(randy))
        self.play(randy.change, "sad")
        self.play(Blink(randy))

    def imagine_score_0(self):
        prob_rect = SurroundingRectangle(self.title[-1])
        bar_rect = SurroundingRectangle(VGroup(
            self.bar_chart.bars[0], self.old_bars[0],
            self.bar_chart.bar_labels[0],
        ))

        self.play(ShowCreation(prob_rect))
        self.wait()
        self.play(ReplacementTransform(
            prob_rect, bar_rect
        ))
        self.wait()
        self.play(FadeOut(bar_rect))

    def get_angry(self):
        randy = self.randy

        self.play(randy.change, "angry")
        self.wait(2)
        self.play(PiCreatureSays(
            randy, "It's not representative!",
            target_mode = "pleading",
            bubble_kwargs = {"fill_opacity" : 1}
        ))
        self.wait(2)

    #####

    def create_pi_creature(self):
        self.randy = Randolph()
        self.randy.to_corner(DOWN+LEFT)
        return self.randy

class TeacherAssessingLiklihoodOfZero(TeacherStudentsScene):
    def construct(self):
        self.add_title()
        self.fade_other_students()
        self.show_independence_probability()
        self.teacher_reacts()

    def add_title(self):
        title = TexMobject("P(", "\\text{Correct}", ")", "=", "0.65")
        title.to_edge(UP)
        title.set_color_by_tex("Correct", GREEN)
        q_mark = TexMobject("?")
        q_mark.next_to(title[-2], UP, SMALL_BUFF)
        title.add(q_mark)

        self.add(title)
        self.title = title

    def fade_other_students(self):
        for student in self.students[0::2]:
            student.fade(0.7)
            self.pi_creatures.remove(student)

    def show_independence_probability(self):
        prob = get_probability_of_slot_group(3*[False])
        rhs = TexMobject("=", "(0.35)", "^3", "\\approx 4.3\\%")
        rhs.set_color_by_tex("0.35", RED)
        rhs.next_to(prob, RIGHT)
        prob.add(rhs)
        prob.next_to(self.teacher, UP+LEFT)
        words = TextMobject("Assuming independence")
        words.next_to(prob, UP)

        self.play(
            self.teacher.change, "raise_right_hand",
            FadeIn(words),
            Write(prob)
        )
        self.wait()

        self.ind_group = VGroup(prob, words)

    def teacher_reacts(self):
        ind_group = self.ind_group
        box = SurroundingRectangle(ind_group)
        box.set_stroke(WHITE, 0)
        ind_group.add(box)
        ind_group.generate_target()
        ind_group.target.scale(0.7)
        ind_group.target.to_corner(UP+RIGHT, MED_SMALL_BUFF)
        ind_group.target[-1].set_stroke(WHITE, 2)

        randy = self.students[1]

        self.teacher_says(
            "Highly unlikely",
            target_mode = "sassy",
            added_anims = [MoveToTarget(ind_group)],
            run_time = 2,
        )
        self.play(randy.change, "sad")
        self.wait(2)
        self.play(
            RemovePiCreatureBubble(
                self.teacher, target_mode = "guilty",
            ),
            PiCreatureSays(randy, "Wait!", target_mode = "surprised"),
            run_time = 1
        )
        self.wait(1)

class CorrelationsWith35Percent(ThousandPossibleQuizzes):
    def construct(self):
        self.add_top_calculation()
        self.show_first_split()
        self.show_second_split()
        self.show_third_split()
        self.comment_on_final_size()

    def add_top_calculation(self):
        equation = VGroup(
            get_probability_of_slot_group(3*[False]),
            TexMobject("="),
            get_probability_of_slot_group([False]),
            get_probability_of_slot_group(2*[False], [False]),
            get_probability_of_slot_group(3*[False], 2*[False]),
        )
        equation.arrange(RIGHT, buff = SMALL_BUFF)
        equation.to_edge(UP)

        self.add(equation)
        self.equation = equation

    def show_first_split(self):
        quizzes = self.get_thousand_quizzes()
        n = int(0.65*len(quizzes))
        top_part = VGroup(*quizzes[:n])
        bottom_part = VGroup(*quizzes[n:])
        parts = [top_part, bottom_part]
        for part, color in zip(parts, [GREEN, RED]):
            part.generate_target()
            for quiz in part.target:
                quiz[0].set_color(color)
        top_part.target.shift(UP)
        brace = Brace(bottom_part, LEFT)
        prop = TexMobject("0.35")
        prop.next_to(brace, LEFT)

        term = self.equation[2]
        term_brace = Brace(term, DOWN)

        self.add(quizzes)
        self.wait()
        self.play(
            GrowFromCenter(brace), 
            FadeIn(prop),
            *list(map(MoveToTarget, parts))
        )
        self.wait()
        self.play(
            top_part.fade, 0.8,
            Transform(brace, term_brace),
            prop.next_to, term_brace, DOWN,
        )
        self.wait()

        self.quizzes = bottom_part
        self.quizzes.sort(lambda p : p[0])

    def show_second_split(self):
        n = int(0.45*len(self.quizzes))
        left_part = VGroup(*self.quizzes[:n])
        right_part = VGroup(*self.quizzes[n:])
        parts = [left_part, right_part]
        for part, color in zip(parts, [GREEN, RED_E]):
            part.generate_target()
            for quiz in part.target:
                quiz[1].set_color(color)
        left_part.target.shift(LEFT)
        brace = Brace(right_part, UP)
        prop = TexMobject(">0.35")
        prop.next_to(brace, UP)

        term = self.equation[3]
        term_brace = Brace(term, DOWN)

        self.play(
            GrowFromCenter(brace),
            FadeIn(prop),
            *list(map(MoveToTarget, parts))
        )
        self.wait()
        self.play(
            Transform(brace, term_brace),
            prop.next_to, term_brace, DOWN
        )
        self.play(left_part.fade, 0.8)

        self.quizzes = right_part
        self.quizzes.sort(lambda p : -p[1])

    def show_third_split(self):
        quizzes = self.quizzes
        n = int(0.22*len(quizzes))
        top_part = VGroup(*quizzes[:n])
        bottom_part = VGroup(*quizzes[n:])
        parts = [top_part, bottom_part]
        for part, color in zip(parts, [GREEN, RED_B]):
            part.generate_target()
            for quiz in part.target:
                quiz[2].set_color(color)
        top_part.target.shift(0.5*UP)
        brace = Brace(bottom_part, LEFT)
        prop = TexMobject("\\gg 0.35")
        prop.next_to(brace, LEFT)

        term = self.equation[4]
        term_brace = Brace(term, DOWN)

        self.play(
            GrowFromCenter(brace), 
            FadeIn(prop),
            *list(map(MoveToTarget, parts))
        )
        self.wait()
        self.play(
            Transform(brace, term_brace),
            prop.next_to, term_brace, DOWN,
        )
        self.play(top_part.fade, 0.8)
        self.wait()

        self.quizzes = bottom_part

    def comment_on_final_size(self):
        rect = SurroundingRectangle(self.quizzes)
        words = TextMobject(
            "Much more than ", "$(0.35)^3 \\approx 4.3\\%$"
        )
        words.next_to(rect, LEFT)

        self.play(
            ShowCreation(rect),
            FadeIn(words)
        )
        self.wait()

class WeighingIndependenceAssumption(PiCreatureScene):
    def construct(self):
        randy = self.randy

        title = TextMobject("Independence")
        title.scale(1.5)
        title.to_edge(UP)
        self.add(title)
        formula = TexMobject(
            "P(", "A", "B", ")", "="
            "P(", "A", ")", "P(", "B", ")"
        )
        formula.set_color_by_tex("A", BLUE)
        formula.set_color_by_tex("B", GREEN)

        clean = TextMobject("Clean")
        clean.next_to(formula, UP)
        VGroup(clean, formula).next_to(randy, UP+LEFT)
        clean.save_state()
        clean.shift(2*(DOWN+RIGHT))
        clean.set_fill(opacity = 0)

        self.play(
            randy.change, "raise_left_hand", clean,
            clean.restore
        )
        self.play(Write(formula))
        self.play(
            randy.change, "raise_right_hand",
            randy.look, UP+RIGHT,
        )
        self.wait(2)

    ####

    def create_pi_creature(self):
        self.randy = Randolph().to_edge(DOWN)
        return self.randy

class NameBinomial(Scene):
    CONFIG = {
        "flip_indices" : [0, 2, 4, 5, 6, 7],
    }
    def construct(self):
        self.name_distribution()
        self.add_quiz_questions()
        self.change_to_gender()
        self.change_bar_chart_for_gender_example()
        self.point_out_example_input()
        self.write_probability_of_girl()
        self.think_through_probabilities()

    def name_distribution(self):
        ns = [3, 10]
        p = 0.65
        charts = VGroup()
        for n in ns:
            dist = get_binomial_distribution(n, p)
            values = list(map(dist, list(range(n+1))))
            chart = BarChart(values, bar_names = list(range(n+1)))
            chart.to_edge(LEFT)
            charts.add(chart)

        probability = TexMobject(
            "P(", "\\checkmark", ")", "=", str(p)
        )
        probability.set_color_by_tex("checkmark", GREEN)
        probability.move_to(charts, UP)

        title = TextMobject("``Binomial distribution''")
        title.next_to(charts, UP)
        title.to_edge(UP)
        formula = TexMobject(
            "P(X=", "k", ")=", 
            "{n \\choose k}", 
            "p", "^k",
            "(1-", "p", ")", "^{n-", "k}",
            arg_separator = ""
        )
        formula.set_color_by_tex("p", YELLOW)
        formula.set_color_by_tex("k", GREEN)
        choose_part = formula.get_part_by_tex("choose")
        choose_part.set_color(WHITE)
        choose_part[-2].set_color(GREEN)
        formula.to_corner(UP+RIGHT)

        self.add(charts[0], probability)
        self.wait()
        self.play(Write(title))
        self.wait()
        self.play(ReplacementTransform(*charts))
        self.play(Write(formula))
        self.wait()
        self.play(
            formula.scale, 0.7,
            formula.next_to, charts, DOWN,
        )

        self.chart = charts[1]
        self.probability = probability
        self.title = title
        self.formula = formula

    def add_quiz_questions(self):
        n = 10
        checkmarks = VGroup(*[
            TexMobject("\\checkmark").set_color(GREEN)
            for x in range(n)
        ])
        checkmarks.arrange(DOWN, buff = 0.3)
        crosses = VGroup()
        arrows = VGroup()
        for checkmark in checkmarks:
            cross = TexMobject("\\times")
            cross.set_color(RED)
            cross.next_to(checkmark, RIGHT, LARGE_BUFF)
            crosses.add(cross)
            arrow = Arrow(
                checkmark, cross,
                tip_length = 0.15,
                color = WHITE
            )
            arrows.add(arrow)
        full_group = VGroup(checkmarks, crosses, arrows)
        full_group.center().to_corner(UP + RIGHT, buff = MED_LARGE_BUFF)
        flip_indices = self.flip_indices
        flipped_arrows, faded_crosses, full_checks = [
            VGroup(*[group[i] for i in flip_indices])
            for group in (arrows, crosses, checkmarks)
        ]
        faded_checkmarks = VGroup(*[m for m in checkmarks if m not in full_checks])

        self.play(*[
            LaggedStartMap(
                Write, mob,
                run_time = 3,
                lag_ratio = 0.3
            )
            for mob in full_group
        ])
        self.wait()
        self.play(
            LaggedStartMap(
                Rotate, flipped_arrows,
                angle = np.pi,
                in_place = True,
                run_time = 2,
                lag_ratio = 0.5
            ),
            faded_crosses.set_fill, None, 0.5,
            faded_checkmarks.set_fill, None, 0.5,
        )
        self.wait()

        self.checkmarks = checkmarks
        self.crosses = crosses
        self.arrows = arrows

    def change_to_gender(self):
        flip_indices = self.flip_indices
        male = self.get_male()
        female = self.get_female()

        girls, boys = [
            VGroup(*[
                template.copy().move_to(mob)
                for mob in group
            ])
            for template, group in [
                (female, self.checkmarks), (male, self.crosses)
            ]
        ]
        for i in range(len(boys)):
            mob = boys[i] if i in flip_indices else girls[i]
            mob.set_fill(opacity = 0.5)

        brace = Brace(girls, LEFT)
        words = brace.get_text("$n$ children")

        self.play(
            GrowFromCenter(brace),
            FadeIn(words)
        )
        for m1, m2 in (self.crosses, boys), (self.checkmarks, girls):
            self.play(ReplacementTransform(
                m1, m2,
                lag_ratio = 0.5,
                run_time = 3
            ))
        self.wait()

        self.boys = boys
        self.girls = girls
        self.children_brace = brace
        self.n_children_words = words

    def change_bar_chart_for_gender_example(self):
        checkmark = self.probability.get_part_by_tex("checkmark")
        p_mob = self.probability[-1]

        female = self.get_female()
        female.move_to(checkmark)
        new_p_mob = TexMobject("0.49")
        new_p_mob.move_to(p_mob, LEFT)

        dist = get_binomial_distribution(10, 0.49)
        values = list(map(dist, list(range(11))))

        self.play(
            Transform(checkmark, female),
            Transform(p_mob, new_p_mob),
        )
        self.play(self.chart.change_bar_values, values)
        self.wait()

    def point_out_example_input(self):
        boy_girl_groups = VGroup(*[
            VGroup(boy, girl)
            for boy, girl in zip(self.boys, self.girls)
        ])
        girl_rects = VGroup(*[
            SurroundingRectangle(
                boy_girl_groups[i], 
                color = MAROON_B,
                buff = SMALL_BUFF,
            )
            for i in sorted(self.flip_indices)
        ])

        chart = self.chart
        n_girls = len(girl_rects)
        chart_rect = SurroundingRectangle(
            VGroup(chart.bars[n_girls], chart.bar_labels[n_girls]),
            buff = SMALL_BUFF
        )

        prob = TexMobject(
            "P(", "\\# \\text{Girls}", "=", "6", ")"
        )
        prob.set_color_by_tex("Girls", MAROON_B)
        arrow = Arrow(UP, ORIGIN, tip_length = 0.15)
        arrow.set_color(MAROON_B)
        arrow.next_to(prob, DOWN)
        prob.add(arrow)
        prob.next_to(chart_rect, UP)
        girls = VGroup(*[self.girls[i] for i in self.flip_indices])


        self.play(ShowCreation(chart_rect))
        self.play(LaggedStartMap(
            ShowCreation, girl_rects,
            run_time = 2,
            lag_ratio = 0.5,
        ))
        self.wait()

        self.play(Write(prob))
        self.play(LaggedStartMap(
            Indicate, girls,
            run_time = 3,
            lag_ratio = 0.3,
            rate_func = there_and_back
        ))
        self.play(FadeOut(prob))
        self.wait()

        self.chart_rect = chart_rect
        self.girl_rects = girl_rects

    def write_probability_of_girl(self):
        probability = self.probability
        probability_copies = VGroup(*[
            probability.copy().scale(0.7).next_to(
                girl, LEFT, MED_LARGE_BUFF
            )
            for girl in self.girls
        ])

        self.play(FocusOn(probability))
        self.play(Indicate(probability[-1]))
        self.wait()
        self.play(
            ReplacementTransform(
                VGroup(probability.copy()), probability_copies
            ),
            FadeOut(self.children_brace),
            FadeOut(self.n_children_words),
        )
        self.wait()

        self.probability_copies = probability_copies

    def think_through_probabilities(self):
        randy = Randolph().scale(0.5)
        randy.next_to(self.probability_copies, LEFT, LARGE_BUFF)

        self.play(FadeIn(randy))
        self.play(randy.change, "pondering")
        self.play(Blink(randy))
        self.wait()

    ##

    def get_male(self):
        return TexMobject("\\male").scale(1.3).set_color(BLUE)

    def get_female(self):
        return TexMobject("\\female").scale(1.3).set_color(MAROON_B)

class CycleThroughPatterns(NameBinomial):
    CONFIG = {
        "n_patterns_shown" : 100,
        "pattern_scale_value" : 2.7,
        "n" : 10,
        "k" : 6,
    }
    def construct(self):
        n = self.n
        k = self.k
        question = TextMobject(
            "How many patterns have \\\\ %d "%k, 
            "$\\female$",
            " and %d "%(n-k),
            "$\\male$",
            "?",
            arg_separator = ""
        )
        question.set_color_by_tex("male", BLUE)
        question.set_color_by_tex("female", MAROON_B)
        question.set_width(FRAME_WIDTH - 1)
        question.to_edge(UP, buff = LARGE_BUFF)
        self.add(question)

        all_combinations = list(it.combinations(list(range(n)), k))
        shown_combinations = all_combinations[:self.n_patterns_shown]
        patterns = VGroup(*[
            self.get_pattern(indicies)
            for indicies in shown_combinations
        ])
        patterns.to_edge(DOWN, buff = LARGE_BUFF)
        pattern = patterns[0]
        self.add(pattern)
        for new_pattern in ProgressDisplay(patterns[1:]):
            self.play(*[
                Transform(
                    getattr(pattern, attr),
                    getattr(new_pattern, attr),
                    path_arc = np.pi
                )
                for attr in ("boys", "girls")
            ])

    ####

    def get_pattern(self, indices):
        pattern = VGroup()
        pattern.boys = VGroup()
        pattern.girls = VGroup()
        for i in range(self.n):
            if i in indices:
                mob = self.get_female()  
                pattern.girls.add(mob)
            else:
                mob = self.get_male()
                pattern.boys.add(mob)
            mob.shift(i*MED_LARGE_BUFF*RIGHT)
            pattern.add(mob)
        pattern.scale(self.pattern_scale_value)
        pattern.to_edge(LEFT)
        return pattern

class Compute6of10GirlsProbability(CycleThroughPatterns):
    def construct(self):
        self.show_combinations()
        self.write_n_choose_k()

    def show_combinations(self):
        pattern_rect = ScreenRectangle(height = 4)
        pattern_rect.center()
        pattern_rect.to_edge(UP, buff = MED_SMALL_BUFF)

        self.add(pattern_rect)
        self.wait(5)

        self.pattern_rect = pattern_rect

    def write_n_choose_k(self):
        brace = Brace(self.pattern_rect, DOWN)
        ten_choose_six = brace.get_tex("{10 \\choose 6}")
        see_chapter_one = TextMobject("(See chapter 1)")
        see_chapter_one.next_to(ten_choose_six, DOWN)
        see_chapter_one.set_color(GREEN)
        computation = TexMobject(
            "=\\frac{%s}{%s}"%(
                 "\\cdot ".join(map(str, list(range(10, 4, -1)))),
                 "\\cdot ".join(map(str, list(range(1, 7)))),
            )
        )
        computation.move_to(ten_choose_six, UP)
        rhs = TexMobject("=", "210")
        rhs.next_to(computation, RIGHT)

        self.play(
            FadeIn(see_chapter_one),
            GrowFromCenter(brace)
        )
        self.play(Write(ten_choose_six))
        self.wait(2)
        self.play(
            ten_choose_six.next_to, computation.copy(), LEFT,
            Write(VGroup(computation, rhs))
        )
        self.wait()

        self.ten_choose_six = ten_choose_six
        self.rhs = rhs

class ProbabilityOfAGivenBoyGirlPattern(CycleThroughPatterns):
    def construct(self):
        self.write_total_count()
        self.write_example_probability()
        self.write_total_probability()

    def write_total_count(self):
        count = TextMobject(
            "${10 \\choose 6}$", " $= 210$",
            "total patterns."
        )
        count.to_edge(UP)
        self.add(count)

        self.count = count

    def write_example_probability(self):
        prob = TexMobject("P\\big(", "O "*15, "\\big)", "=")
        indices = [1, 2, 4, 6, 8, 9]
        pattern = self.get_pattern(indices)
        pattern.replace(prob[1], dim_to_match = 0)
        prob.submobjects[1] = pattern
        prob.next_to(self.count, DOWN, LARGE_BUFF)

        gp = TexMobject("P(\\female)")
        gp[2].set_color(MAROON_B)
        bp = TexMobject("P(\\male)")
        bp[2].set_color(BLUE)
        gp_num = TexMobject("(0.49)").set_color(MAROON_B)
        bp_num = TexMobject("(0.51)").set_color(BLUE)
        gp_nums = VGroup()
        bp_nums = VGroup()
        factored = VGroup()
        factored_in_nums = VGroup()
        for i in range(10):
            if i in indices:
                num_mob = gp_num.copy()
                gp_nums.add(num_mob)
                p_mob = gp.copy()
            else:
                num_mob = bp_num.copy()
                bp_nums.add(num_mob)
                p_mob = bp.copy()
            factored_in_nums.add(num_mob)
            factored.add(p_mob)
        for group in factored, factored_in_nums:
            group.arrange(RIGHT, buff = SMALL_BUFF)
            group.next_to(prob, DOWN, MED_LARGE_BUFF)
        gp_nums.save_state()
        bp_nums.save_state()

        final_probability = TexMobject(
            "(0.49)^6", "(0.51)^4"
        )
        final_probability.set_color_by_tex("0.49", MAROON_B)
        final_probability.set_color_by_tex("0.51", BLUE)
        final_probability.next_to(factored_in_nums, DOWN, LARGE_BUFF)

        self.play(FadeIn(prob))
        self.wait()
        self.play(ReplacementTransform(
            pattern.copy(), factored,
            run_time = 1.5,
        ))
        self.wait(2)
        self.play(ReplacementTransform(
            factored, factored_in_nums,
            run_time = 2,
            lag_ratio = 0.5
        ))
        self.wait(2)
        for group, tex in (gp_nums, "0.49"), (bp_nums, "0.51"):
            part = final_probability.get_part_by_tex(tex)
            self.play(group.shift, MED_LARGE_BUFF*DOWN)
            self.play(
                ReplacementTransform(
                    group.copy(), VGroup(VGroup(*part[:-1]))
                ),
                Write(part[-1])
            )
            self.wait()
            self.play(group.restore)
        self.wait()

        self.final_probability = final_probability

    def write_total_probability(self):
        ten_choose_six = self.count[0].copy()
        ten_choose_six.generate_target()
        ten_choose_six.target.move_to(self.final_probability)
        p_tex = TexMobject("P(", "\\text{6 Girls}", ")", "=")
        p_tex.set_color_by_tex("Girls", MAROON_B)
        p_tex.next_to(ten_choose_six.target, LEFT)

        self.play(
            Write(p_tex, run_time = 2),
            self.final_probability.next_to, 
            ten_choose_six.target, RIGHT
        )
        self.play(MoveToTarget(ten_choose_six))
        self.wait()

class CycleThroughPatternsForThree(CycleThroughPatterns):
    CONFIG = {
        "k" : 3,
        "n_patterns_shown" : 20,
    }

class GeneralBinomialDistributionValues(Scene):
    CONFIG = {
        "n" : 10,
        "alt_n" : 8,
        "p" : 0.49,
    }
    def construct(self):
        self.add_chart()
        self.show_a_few_values()
        self.compare_to_pascal_row()
        self.mention_center_concentration()
        self.generalize()
        self.play_with_p_value()

    def add_chart(self):
        dist = get_binomial_distribution(self.n, self.p)
        values = list(map(dist, list(range(self.n+1))))
        chart = BarChart(
            values,
            bar_names = list(range(self.n+1))
        )
        chart.to_edge(LEFT)

        full_probability = self.get_probability_expression(
            "10", "k", "(0.49)", "(0.51)"
        )
        full_probability.next_to(chart, UP, aligned_edge = LEFT)

        self.add(chart)

        self.chart = chart
        self.full_probability = full_probability

    def show_a_few_values(self):
        chart = self.chart
        probabilities = VGroup()
        for i, bar in enumerate(chart.bars):
            prob = self.get_probability_expression(
                "10", str(i), "(0.49)", "(0.51)",
                full = False
            )
            arrow = Arrow(
                UP, DOWN, 
                color = WHITE,
                tip_length = 0.15
            )
            arrow.next_to(bar, UP, SMALL_BUFF)
            prob.next_to(arrow, UP, SMALL_BUFF)
            ##
            prob.shift(LEFT)
            prob.shift_onto_screen()
            prob.shift(RIGHT)
            ##
            prob.add(arrow)            
            probabilities.add(prob)
        shown_prob = probabilities[6].copy()

        self.play(FadeIn(shown_prob))
        self.wait()
        self.play(LaggedStartMap(
            FadeIn, self.full_probability,
            run_time = 4,
            lag_ratio = 0.5,
        ))
        self.wait()
        last_k = 6
        for k in 3, 8, 5, 9, 6:
            self.play(Transform(
                shown_prob, probabilities[k],
                path_arc = -np.pi/6 if k > last_k else np.pi/6
            ))
            self.wait(2)
            last_k = k

        self.shown_prob = shown_prob

    def compare_to_pascal_row(self):
        triangle = PascalsTriangle(nrows = 11)
        triangle.set_width(6)
        triangle.to_corner(UP+RIGHT)
        last_row = VGroup(*[
            triangle.coords_to_mobs[10][k]
            for k in range(11)
        ])
        ten_choose_ks = VGroup()
        for k, mob in enumerate(last_row):
            ten_choose_k = TexMobject("10 \\choose %s"%k)
            ten_choose_k.scale(0.5)
            ten_choose_k.stretch(0.8, 0)
            ten_choose_k.next_to(mob, DOWN)
            ten_choose_ks.add(ten_choose_k)
        ten_choose_ks.set_color_by_gradient(BLUE, YELLOW)

        self.play(
            LaggedStartMap(FadeIn, triangle),
            FadeOut(self.shown_prob)
        )
        self.play(
            last_row.set_color_by_gradient, BLUE, YELLOW,
            Write(ten_choose_ks, run_time = 2)
        )
        self.wait()
        self.play(ApplyWave(self.chart.bars, direction = UP))
        self.play(FocusOn(last_row))
        self.play(LaggedStartMap(
            ApplyMethod, last_row,
            lambda m : (m.scale_in_place, 1.2),
            rate_func = there_and_back,
        ))
        self.wait()

        self.pascals_triangle = triangle
        self.ten_choose_ks = ten_choose_ks

    def mention_center_concentration(self):
        bars = self.chart.bars
        bars.generate_target()
        bars.save_state()
        bars.target.arrange(UP, buff = 0)
        bars.target.stretch_to_fit_height(self.chart.height)
        bars.target.move_to(
            self.chart.x_axis.point_from_proportion(0.05),
            DOWN
        )
        brace = Brace(VGroup(*bars.target[4:7]), RIGHT)
        words = brace.get_text("Most probability \\\\ in middle values")

        self.play(MoveToTarget(bars))
        self.play(
            GrowFromCenter(brace),
            FadeIn(words)
        )
        self.wait(2)
        self.play(
            bars.restore,
            *list(map(FadeOut, [
                brace, words, 
                self.pascals_triangle,
                self.ten_choose_ks
            ]))
        )

    def generalize(self):
        alt_n = self.alt_n
        dist = get_binomial_distribution(alt_n, self.p)
        values = list(map(dist, list(range(alt_n + 1))))
        alt_chart = BarChart(
            values, bar_names = list(range(alt_n + 1))
        )
        alt_chart.move_to(self.chart)

        alt_probs = [
            self.get_probability_expression("n", "k", "(0.49)", "(0.51)"),
            self.get_probability_expression("n", "k", "p", "(1-p)"),
        ]
        for prob in alt_probs:
            prob.move_to(self.full_probability)

        self.play(FocusOn(
            self.full_probability.get_part_by_tex("choose")
        ))
        self.play(
            ReplacementTransform(self.chart, alt_chart),
            Transform(self.full_probability, alt_probs[0])
        )
        self.chart = alt_chart
        self.wait(2)
        self.play(Transform(self.full_probability, alt_probs[1]))
        self.wait()

    def play_with_p_value(self):
        p = self.p
        interval = UnitInterval(color = WHITE)
        interval.set_width(5)
        interval.next_to(self.full_probability, DOWN, LARGE_BUFF)
        interval.add_numbers(0, 0.5, 1)
        triangle = RegularPolygon(
            n=3, start_angle = -np.pi/2,
            fill_color = MAROON_B,
            fill_opacity = 1,
            stroke_width = 0,
        )
        triangle.set_height(0.25)
        triangle.move_to(interval.number_to_point(p), DOWN)
        p_mob = TexMobject("p")
        p_mob.set_color(MAROON_B)
        p_mob.next_to(triangle, UP, SMALL_BUFF)
        triangle.add(p_mob)

        new_p_values = [0.8, 0.4, 0.2, 0.9, 0.97, 0.6]

        self.play(
            ShowCreation(interval),
            Write(triangle, run_time = 1)
        )
        self.wait()
        for new_p in new_p_values:
            p = new_p
            dist = get_binomial_distribution(self.alt_n, p)
            values = list(map(dist, list(range(self.alt_n + 1))))
            self.play(
                self.chart.change_bar_values, values,
                triangle.move_to, interval.number_to_point(p), DOWN
            )
            self.wait()

    #######

    def get_probability_expression(
        self, n = "n", k = "k", p = "p", q = "(1-p)",
        full = True
        ):
        args = []
        if full:
            args += ["P(", "\\# \\text{Girls}", "=", k, ")", "="]
        args += [
            "{%s \\choose %s}"%(n, k),
            p, "^%s"%k,
            q, "^{%s"%n, "-", "%s}"%k,
        ]
        result = TexMobject(*args, arg_separator = "")
        color_map = {
            "Girls" : MAROON_B,
            n : WHITE,
            k : YELLOW,
            p : MAROON_B,
            q : BLUE,
        }
        result.set_color_by_tex_to_color_map(color_map)
        choose_part = result.get_part_by_tex("choose")
        choose_part.set_color(WHITE)
        VGroup(*choose_part[1:1+len(n)]).set_color(color_map[n])
        VGroup(*choose_part[-1-len(k):-1]).set_color(color_map[k])
        return result

class PointOutSimplicityOfFormula(TeacherStudentsScene, GeneralBinomialDistributionValues):
    def construct(self):
        prob = self.get_probability_expression(full = False)
        corner = self.teacher.get_corner(UP+LEFT)
        prob.next_to(corner, UP, MED_LARGE_BUFF)
        prob.save_state()
        prob.move_to(corner)
        prob.set_fill(opacity = 0)

        self.play(
            prob.restore,
            self.teacher.change_mode, "raise_right_hand"
        )
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = prob
        )
        self.wait()
        self.student_says(
            "Simpler than I feared",
            target_mode = "hooray",
            student_index = 0,
            added_anims = [prob.to_corner, UP+RIGHT]
        )
        self.wait()
        self.teacher_says("Due to \\\\ independence")
        self.wait(2)

class CorrectForDependence(NameBinomial):
    CONFIG = {
        "flip_indices" : [3, 6, 8],
    }
    def setup(self):
        self.force_skipping()
        self.name_distribution()
        self.add_quiz_questions()
        self.revert_to_original_skipping_status()

    def construct(self):
        self.mention_dependence()
        self.show_tendency_to_align()
        self.adjust_chart()

    def mention_dependence(self):
        brace = Brace(self.checkmarks, LEFT)
        words = brace.get_text("What if there's \\\\ correlation?")
        formula = self.formula
        cross = Cross(formula)

        self.play(
            GrowFromCenter(brace),
            Write(words)
        )
        self.wait()
        self.play(ShowCreation(cross))
        self.wait()

    def show_tendency_to_align(self):
        checkmarks = self.checkmarks
        arrows = self.arrows
        crosses = self.crosses
        groups = [
            VGroup(*trip)
            for trip in zip(checkmarks, arrows, crosses)
        ]
        top_rect = SurroundingRectangle(groups[0])
        top_rect.set_color(GREEN)
        indices_to_follow = [1, 4, 5, 7]

        self.play(ShowCreation(top_rect))
        self.play(*self.get_arrow_flip_anims([0]))
        self.wait()
        self.play(*self.get_arrow_flip_anims(indices_to_follow))
        self.play(FocusOn(self.chart.bars))

    def adjust_chart(self):
        chart = self.chart
        bars = chart.bars
        old_bars = bars.copy()
        old_bars.generate_target()
        bars.generate_target()
        for group, vect in (old_bars, LEFT), (bars, RIGHT):
            for bar in group.target:
                side = bar.get_edge_center(vect)
                bar.stretch(0.5, 0)
                bar.move_to(side, vect)
        for bar in old_bars.target:
            bar.set_color(average_color(RED_E, BLACK))

        dist = get_binomial_distribution(10, 0.65)
        values = np.array(list(map(dist, list(range(11)))))
        alt_values = values + 0.1
        alt_values[0] -= 0.06
        alt_values[1] -= 0.03
        alt_values /= sum(alt_values)
        arrows = VGroup()
        arrow_template = Arrow(
            0.5*UP, ORIGIN, buff = 0, 
            tip_length = 0.15,
            color = WHITE
        )
        for value, alt_value, bar in zip(values, alt_values, bars):
            arrow = arrow_template.copy()
            if value < alt_value:
                arrow.rotate(np.pi, about_point = ORIGIN)
            arrow.next_to(bar, UP)
            arrows.add(arrow)

        self.play(
            MoveToTarget(old_bars),
            MoveToTarget(bars),
        )
        self.wait()
        self.play(*list(map(ShowCreation, arrows)))
        self.play(chart.change_bar_values, alt_values)

    ######

    def get_arrow_flip_anims(self, indices):
        checkmarks, arrows, crosses = movers = [
            VGroup(*[
                group[i]
                for i in range(len(group))
                if i in indices
            ])
            for group in (self.checkmarks, self.arrows, self.crosses)
        ]
        for arrow in arrows:
            arrow.target = arrow.deepcopy()
            arrow.target.rotate_in_place(np.pi)
        for group in checkmarks, crosses:
            for mob, arrow in zip(group, arrows):
                mob.generate_target()
                c = mob.get_center()
                start, end = arrow.target.get_start_and_end()
                to_end = get_norm(c - end)
                to_start = get_norm(c - start)
                if to_end < to_start:
                    mob.target.set_fill(opacity = 1)
                else:
                    mob.target.set_fill(opacity = 0.5)
        for checkmark in checkmarks:
            checkmark.target.scale_in_place(1.2)

        kwargs = {"path_arc" : np.pi}
        if len(indices) > 1:
            kwargs.update({"run_time" : 2})
        return [
            LaggedStartMap(
                MoveToTarget, mover,
                **kwargs
            )
            for mover in movers
        ]

class ButWhatsTheAnswer(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "But what's the \\\\ actual answer?",
            target_mode = "confused"
        )
        self.change_student_modes(*["confused"]*3)
        self.wait()
        self.play(self.teacher.change, "pondering")
        self.wait(3)

class PermuteQuizQuestions(Scene):
    def construct(self):
        quiz = get_quiz(
            "Define ``Brachistochrone''",
            "Define ``Tautochrone''",
            "Define ``Cycloid''",
        )
        questions = [
            VGroup(*q[2:])
            for q in quiz.questions
        ]
        colors = [BLUE, GREEN, RED]
        for color, question in zip(colors, questions):
            question.set_color(color)
        quiz.scale(2)

        self.add(quiz)
        self.wait()
        for m1, m2 in it.combinations(questions, 2):
            self.play(
                m1.move_to, m2, LEFT,
                m2.move_to, m1, LEFT,
                path_arc = np.pi
            )
            self.wait()

class AssumeOrderDoesntMatter(Scene):
    def construct(self):
        self.force_skipping()

        self.add_title()
        self.show_equality()
        self.mention_correlation()

        self.revert_to_original_skipping_status()
        self.coming_soon()

    def add_title(self):
        title = TextMobject(
            "Softer simplifying assumption: " +\
            "Order doesn't matter"
        )
        title.to_edge(UP)

        self.add(title)
        self.title = title

    def show_equality(self):
        n = 3
        prob_groups = VGroup(*[
            VGroup(*list(map(
                get_probability_of_slot_group,
                [t for t in it.product(*[[True, False]]*n) if sum(t) == k]
            )))
            for k in range(n+1)
        ])
        for prob_group in prob_groups:
            for prob in prob_group[:-1]:
                equals = TexMobject("=")
                equals.next_to(prob, RIGHT)
                prob.add(equals)
            prob_group.arrange(RIGHT)
            max_width = FRAME_WIDTH - 1
            if prob_group.get_width() > max_width:
                prob_group.set_width(max_width)
        prob_groups.arrange(DOWN, buff = 0.7)
        prob_groups.next_to(self.title, DOWN, MED_LARGE_BUFF)

        self.play(FadeIn(
            prob_groups[1],
            run_time = 2,
            lag_ratio = 0.5
        ))
        self.wait(2)
        self.play(FadeIn(
            VGroup(prob_groups[0], *prob_groups[2:]),
            run_time = 3,
            lag_ratio = 0.5
        ))
        self.wait()

        self.prob_groups = prob_groups

    def mention_correlation(self):
        assumption_group = VGroup(*self.get_top_level_mobjects())
        question = TextMobject(
            "But what is ", "``correlation''", "?",
            arg_separator = ""
        )
        question.set_color(BLUE)
        question.to_edge(UP)
        bottom = question.get_bottom()

        self.play(
            Write(question),
            assumption_group.next_to, bottom, DOWN, LARGE_BUFF
        )
        self.wait()

        self.assumption_group = assumption_group
        self.question = question

    def coming_soon(self):
        self.play(
            LaggedStartMap(
                ApplyMethod, self.assumption_group,
                lambda m : (m.shift, FRAME_HEIGHT*DOWN),
                remover = True,
            ),
            ApplyMethod(
                self.question.center,
                rate_func = squish_rate_func(smooth, 0.5, 1),
                run_time = 2
            )
        )

        part = self.question.get_part_by_tex("correlation")
        brace = Brace(part, UP)
        words = brace.get_text("Coming soon!")
        self.play(
            GrowFromCenter(brace),
            part.set_color, YELLOW
        )
        self.play(Write(words))
        self.wait()



class FormulaCanBeRediscovered(PointOutSimplicityOfFormula):
    def construct(self):
        prob = self.get_probability_expression(full = False)
        corner = self.teacher.get_corner(UP+LEFT)
        prob.next_to(corner, UP, MED_LARGE_BUFF)
        brace = Brace(prob, UP)
        rediscover = brace.get_text("Rediscover")

        self.play(
            Write(prob),
            self.teacher.change, "hesitant", prob
        )
        self.wait()
        self.play(
            GrowFromCenter(brace),
            Write(rediscover, run_time = 1)
        )
        self.change_student_modes(*["happy"]*3)
        self.wait(2)

class CompareTwoSituations(PiCreatureScene):
    def construct(self):
        randy = self.randy
        top_left, top_right = screens = [
            ScreenRectangle(height = 3).to_corner(vect)
            for vect in (UP+LEFT, UP+RIGHT)
        ]
        arrow = DoubleArrow(*screens, buff = SMALL_BUFF)
        arrow.set_color(BLUE)

        for screen, s in zip(screens, ["left", "right"]):
            self.play(
                randy.change, "raise_%s_hand"%s, screen,
                ShowCreation(screen)
            )
            self.wait(3)
        self.play(
            randy.change, "pondering", arrow,
            ShowCreation(arrow)
        )
        self.wait(2)

    ####

    def create_pi_creature(self):
        self.randy = Randolph().to_edge(DOWN)
        return self.randy

class SkepticalOfDistributions(TeacherStudentsScene):
    CONFIG = {
        "chart_height" : 3,
    }
    def construct(self):
        self.show_binomial()
        self.show_alternate_distributions()
        self.emphasize_underweighted_tails()

    def show_binomial(self):
        binomial = self.get_binomial()
        binomial.next_to(self.teacher.get_corner(UP+LEFT), UP)
        title = TextMobject("Probable scores")
        title.scale(0.85)
        title.next_to(binomial.bars, UP, 1.5*LARGE_BUFF)

        self.play(
            Write(title, run_time = 1),
            FadeIn(binomial, run_time = 1, lag_ratio = 0.5),
            self.teacher.change, "raise_right_hand"
        )
        for values in binomial.values_list:
            self.play(binomial.change_bar_values, values)
            self.wait()
        self.student_says(
            "Is that valid?", target_mode = "sassy",
            student_index = 0,
            run_time = 1
        )
        self.play(self.teacher.change, "guilty")
        self.wait()

        binomial.add(title)
        self.binomial = binomial

    def show_alternate_distributions(self):
        poisson = self.get_poisson()
        VGroup(poisson, poisson.title).next_to(
            self.students, UP, LARGE_BUFF
        ).shift(RIGHT)
        gaussian = self.get_gaussian()
        VGroup(gaussian, gaussian.title).next_to(
            poisson, RIGHT, LARGE_BUFF
        )


        self.play(
            FadeIn(poisson, lag_ratio = 0.5),
            RemovePiCreatureBubble(self.students[0]),
            self.teacher.change, "raise_right_hand",
            self.binomial.scale, 0.5,
            self.binomial.to_corner, UP+LEFT,
        )
        self.play(Write(poisson.title, run_time = 1))
        self.play(FadeIn(gaussian, lag_ratio = 0.5))
        self.play(Write(gaussian.title, run_time = 1))
        self.wait(2)
        self.change_student_modes(
            *["sassy"]*3,
            added_anims = [self.teacher.change, "plain"]
        )
        self.wait(2)

        self.poisson = poisson
        self.gaussian = gaussian

    def emphasize_underweighted_tails(self):
        poisson_arrows = VGroup()
        arrow_template = Arrow(
            ORIGIN, UP, color = GREEN,
            tip_length = 0.15
        )
        for bar in self.poisson.bars[-4:]:
            arrow = arrow_template.copy()
            arrow.next_to(bar, UP, SMALL_BUFF)
            poisson_arrows.add(arrow)

        gaussian_arrows = VGroup()
        for prop in 0.2, 0.8:
            point = self.gaussian[0][0].point_from_proportion(prop)
            arrow = arrow_template.copy()
            arrow.next_to(point, UP, SMALL_BUFF)
            gaussian_arrows.add(arrow)

        for arrows in poisson_arrows, gaussian_arrows:
            self.play(
                ShowCreation(
                    arrows, 
                    lag_ratio = 0.5,
                    run_time = 2
                ),
                *[
                    ApplyMethod(pi.change, "thinking", arrows)
                    for pi in self.pi_creatures
                ]
            )
            self.wait()
        self.wait(2)

    ####

    def get_binomial(self):
        k_range = list(range(11))
        dists = [
            get_binomial_distribution(10, p)
            for p in (0.2, 0.8, 0.5)
        ]
        values_list = [
            list(map(dist, k_range))
            for dist in dists
        ]
        chart = BarChart(
            values = values_list[-1],
            bar_names = k_range
        )
        chart.set_height(self.chart_height)
        chart.values_list = values_list
        return chart

    def get_poisson(self):
        k_range = list(range(11))
        L = 2
        values = [
            np.exp(-L) * (L**k) / (scipy.special.gamma(k+1))
            for k in k_range
        ]
        chart = BarChart(
            values = values,
            bar_names = k_range,
            bar_colors = [RED, YELLOW]
        )
        chart.set_height(self.chart_height)
        title = TextMobject(
            "Poisson distribution \\\\",
            "$e^{-\\lambda}\\frac{\\lambda^k}{k!}$"
        )
        title.scale(0.75)
        title.move_to(chart, UP)
        title.shift(MED_SMALL_BUFF*RIGHT)
        title[0].shift(SMALL_BUFF*UP)
        chart.title = title

        return chart

    def get_gaussian(self):
        axes = VGroup(self.binomial.x_axis, self.binomial.y_axis).copy()
        graph = FunctionGraph(
            lambda x : 5*np.exp(-x**2),
            mark_paths_closed = True,
            fill_color = BLUE_E,
            fill_opacity = 1,
            stroke_color = BLUE,
        )
        graph.set_width(axes.get_width())
        graph.move_to(axes[0], DOWN)

        title = TextMobject(
            "Gaussian distribution \\\\ ",
            "$\\frac{1}{\\sqrt{2\\pi \\sigma^2}} e^{-\\frac{(x-\\mu)^2}{2\\sigma^2}}$"
        )
        title.scale(0.75)
        title.move_to(axes, UP)
        title.shift(MED_SMALL_BUFF*RIGHT)
        title[0].shift(SMALL_BUFF*UP)
        result = VGroup(axes, graph)
        result.title = title

        return result

class IndependencePatreonThanks(PatreonThanks):
    CONFIG = {
        "specific_patrons" : [
            "Ali Yahya",
            "Desmos",
            "Burt Humburg",
            "CrypticSwarm",
            "Juan Benet",
            "Mayank M. Mehrotra",
            "Lukas Biewald",
            "Samantha D. Suplee",
            "James Park",
            "Erik Sundell",
            "Yana Chernobilsky",
            "Kaustuv DeBiswas",
            "Kathryn Schmiedicke",
            "Karan Bhargava",
            "Yu Jun",
            "Dave Nicponski",
            "Damion Kistler",
            "Markus Persson",
            "Yoni Nazarathy",
            "Corey Ogburn",
            "Ed Kellett",
            "Joseph John Cox",
            "Dan Buchoff",
            "Luc Ritchie",
            "Tianyu Ge",
            "Ted Suzman",
            "Amir Fayazi",
            "Linh Tran",
            "Andrew Busey",
            "Michael McGuffin",
            "John Haley",
            "Mourits de Beer",
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
        ],
    }

class Thumbnail(DangerInProbability):
    def construct(self):
        n, p = 15, 0.5
        dist = get_binomial_distribution(n, p)
        values = np.array(list(map(dist, list(range(n+1)))))
        values *= 2
        chart = BarChart(
            values = values,
            label_y_axis = False,
            width = FRAME_WIDTH - 3,
            height = 1.5*FRAME_Y_RADIUS
        )
        chart.to_edge(DOWN)
        self.add(chart)


        warning = self.get_warning_sign()
        warning.set_height(2)
        warning.to_edge(UP)
        self.add(warning)


        words = TextMobject("Independence")
        words.scale(2.5)
        words.next_to(warning, DOWN)
        self.add(words)

























