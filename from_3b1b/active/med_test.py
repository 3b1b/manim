from manimlib.imports import *


class WomanIcon(SVGMobject):
    CONFIG = {
        "fill_color": GREY_B,
        "stroke_width": 0,
    }

    def __init__(self, **kwargs):
        super().__init__("woman_icon", **kwargs)
        self.remove(self[0])


# Scenes
class BreastCancerExampleSetup(Scene):
    def construct(self):
        # Title
        title = TextMobject("Statistics Seminar", font_size=72)
        title.to_edge(UP)

        title_underline = Underline(title, buff=SMALL_BUFF)
        title_underline.scale(1.1)
        title_underline.set_stroke(LIGHT_GREY)

        self.play(FadeIn(title, shift=0.5 * UP))
        self.play(ShowCreation(title_underline))
        title.add(title_underline)

        # Docs
        doctors = ImageMobject("doctor_pair", height=2)
        doctors.to_corner(DL, buff=1)
        doctors_label = TextMobject("Practicing Gynecologists")
        doctors_label.match_width(doctors)
        doctors_label.next_to(doctors, DOWN)
        doctors_label.set_fill(GREY_A)

        self.play(
            FadeIn(doctors, scale=1.1),
            Write(doctors_label, run_time=1),
        )
        self.wait()

        # Description of patient
        prompt = TextMobject(
            """
            A 50-year-old woman, no symptoms, participates\\\\
            in routine mammography screening.
            """,
            """She tests positive,\\\\
            is alarmed, and wants to know from you whether she\\\\
            has breast cancer for certain or what the chances are.\\\\
            \\quad \\\\
            """,
            """
            Apart from the screening results, you know nothing\\\\
            else about this woman.\\\\
            """,
            alignment="",
            font_size=36,
        )
        prompt.next_to(title_underline, DOWN, MED_LARGE_BUFF)
        prompt[2].shift(0.5 * UP)
        no_symptoms_part = prompt[0][18:28]
        no_symptoms_underline = Underline(
            no_symptoms_part,
            buff=0,
            stroke_width=3,
            stroke_color=YELLOW,
        )

        clipboard = SVGMobject(
            "clipboard",
            stroke_width=0,
            fill_color=interpolate_color(GREY_BROWN, WHITE, 0.2)
        )
        clipboard.next_to(prompt, DOWN)
        clipboard.set_width(2.5)

        clipboard_contents = VGroup(
            TextMobject("+", color=GREEN, font_size=96, stroke_width=3),
            TextMobject("Cancer\\\\detected", color=GREY_A),
        )
        clipboard_contents.arrange(DOWN)
        clipboard_contents.set_width(0.7 * clipboard.get_width())
        clipboard_contents.move_to(clipboard)
        clipboard_contents.shift(0.1 * DOWN)
        clipboard.add(clipboard_contents)

        self.play(FadeIn(prompt[0], lag_ratio=0.01))
        self.play(ShowCreationThenFadeOut(no_symptoms_underline))
        self.wait()
        self.play(
            FadeIn(prompt[1], lag_ratio=0.01),
            prompt[0].set_opacity, 0.5,
        )
        self.play(
            FadeIn(clipboard, shift=0.5 * UP, scale=1.1)
        )
        self.wait()

        self.play(
            FadeIn(prompt[2], lag_ratio=0.01),
            prompt[1].set_opacity, 0.5,
            clipboard.scale, 0.7, {"about_edge": DOWN},
        )
        self.wait()

        # Test sensitivity
        prompt.generate_target()
        prompt.target.set_opacity(0.8)
        prompt.target.match_height(clipboard)
        prompt.target.scale(0.65)
        prompt.target.next_to(clipboard, RIGHT, MED_LARGE_BUFF)

        sensitivity_words = TexMobject("90", "\\%", "\\text{ Sensitivity}")
        sensitivity_words.to_edge(UP)

        h_line = DashedLine(FRAME_WIDTH * LEFT / 2, FRAME_WIDTH * RIGHT / 2)
        h_line.set_stroke(GREY_C)
        h_line.next_to(clipboard, UP)
        h_line.set_x(0)

        self.play(
            FadeIn(sensitivity_words),
            FadeOut(title, shift=UP),
            MoveToTarget(prompt),
            ShowCreation(h_line)
        )

        woman = WomanIcon()
        women = VGroup(*[woman.copy() for x in range(100)])
        women.arrange_in_grid(h_buff=2, v_buff=1)
        women.set_height(3)
        women.next_to(sensitivity_words, DOWN)
        women_rect = SurroundingRectangle(women, buff=0.15)
        women_rect.set_stroke(YELLOW, 2)

        with_bc_label = TextMobject(
            "Women\\\\with\\\\breast\\\\cancer",
            font_size=36,
            color=women_rect.get_color()
        )
        with_bc_label.next_to(women_rect, LEFT)

        women.generate_target()
        signs = VGroup()
        for n, woman in enumerate(women.target):
            if n < 90:
                sign = TexMobject("+", color=GREEN)
                woman.set_color(GREEN)
            else:
                sign = TexMobject("-", color=RED)
                woman.set_color(RED)
            sign.match_width(woman)
            sign.move_to(woman.get_corner(UR), LEFT)
            signs.add(sign)

        self.play(
            FadeIn(women_rect),
            FadeIn(with_bc_label),
            FadeIn(women, lag_ratio=0.01),
        )
        self.wait()
        self.play(
            MoveToTarget(women),
            FadeIn(signs, lag_ratio=0.01)
        )
        self.wait()

        sens_group = VGroup(
            sensitivity_words,
            with_bc_label,
            women_rect,
            women,
            signs
        )

        # Specificity
        specificity_words = TexMobject("91", "\\%", "\\text{ Specificity}")
        specificity_words.move_to(sensitivity_words)
        spec_women = women.copy()
        spec_women.set_fill(GREY_C)
        spec_rect = women_rect.copy()
        spec_rect.set_color(interpolate_color(GREY_BROWN, WHITE, 0.5))
        wo_bc_label = TextMobject(
            "Women\\\\ \\emph{without} \\\\breast\\\\cancer",
            font_size=36,
        )
        wo_bc_label.next_to(spec_rect, LEFT)
        wo_bc_label.match_color(spec_rect)

        spec_group = VGroup(
            specificity_words,
            wo_bc_label,
            spec_rect,
            spec_women,
        )
        spec_group.next_to(ORIGIN, RIGHT, buff=1)
        spec_group.to_edge(UP)

        self.play(
            sens_group.next_to, ORIGIN, LEFT, {"buff": 2},
            sens_group.to_edge, UP,
            FadeIn(spec_group, shift=RIGHT),
        )
        self.wait()

        spec_women.generate_target()
        spec_signs = VGroup()
        for n, woman in enumerate(spec_women.target):
            if n < 9:
                sign = TexMobject("+", color=GREEN)
                woman.set_color(GREEN)
            else:
                sign = TexMobject("-", color=RED)
                woman.set_color(RED)
            sign.match_width(woman)
            sign.move_to(woman.get_corner(UR), LEFT)
            spec_signs.add(sign)

        self.play(
            MoveToTarget(spec_women),
            FadeIn(spec_signs, lag_ratio=0.01)
        )
        self.wait()
        spec_group.add(spec_signs)

        # False negatives/False positives
        fnr = TexMobject(
            "\\leftarrow", "10", "\\%", " \\text{ false negative}",
            font_size=36,
        )
        fnr.next_to(women[-1], RIGHT, buff=0.3)

        fpr = TexMobject(
            "9", "\\%", "\\text{ false positive}", "\\rightarrow",
            font_size=36,
        )
        fpr.next_to(spec_women[0], LEFT, buff=0.3)

        self.play(FadeIn(fnr, shift=0.2 * RIGHT, scale=2))
        self.play(FadeIn(fpr, shift=0.2 * LEFT, scale=2))

        # Ask question
        question = TextMobject(
            "Assume 1\\% of women have breast cancer.  ",
            "How many\\\\ women who test positive actually have breast cancer?",
            font_size=36
        )
        question[0].replace_submobject(
            7, TexMobject("\\%").replace(question[0][7])
        )

        question.next_to(h_line, DOWN)
        question.to_edge(RIGHT)

        clipboard.add_to_back(BackgroundRectangle(clipboard))
        self.play(
            FadeOut(prompt, shift=DOWN),
            clipboard.set_height, 1,
            clipboard.move_to, doctors.get_corner(DR), DOWN,
            FadeIn(question[0], lag_ratio=0.1, run_time=2)
        )
        self.wait()
        self.play(FadeIn(question[1], lag_ratio=0.1, run_time=2))
        self.wait()

        choices = VGroup(
            TextMobject("A) 9 in 10"),
            TextMobject("B) 8 in 10"),
            TextMobject("C) 1 in 10"),
            TextMobject("D) 1 in 100"),
        )
        choices.arrange_in_grid(2, 2, h_buff=1.0, v_buff=0.25, aligned_edge=LEFT)
        choices.next_to(question, DOWN, buff=0.5)
        choices.set_fill(GREY_A)

        for choice in choices:
            self.play(FadeIn(choice, scale=1.2))
            self.wait(0.5)

        # Comment on choices
        a_rect = SurroundingRectangle(choices[0])
        a_rect.set_color(BLUE)
        q_mark = TexMobject("?")
        q_mark.match_height(a_rect)
        q_mark.next_to(a_rect, LEFT)
        q_mark.match_color(a_rect)

        c_rect = SurroundingRectangle(choices[2])
        c_rect.set_color(GREEN)
        checkmark = Checkmark().next_to(c_rect, LEFT)

        self.play(
            ShowCreation(a_rect),
            Write(q_mark)
        )
        self.wait()
        self.play(
            q_mark.move_to, doctors, UR,
            a_rect.set_stroke, {"width": 1},
        )
        self.wait()

        self.play(
            question[0].set_color, YELLOW,
            question[1].set_opacity, 0.5,
        )
        self.wait()

        self.play(
            ReplacementTransform(a_rect, c_rect),
            Write(checkmark)
        )
        self.wait()

        # One fifth of doctors
        curr_doc_group = Group(
            doctors,
            clipboard,
            doctors_label,
            q_mark,
        )

        new_doctors = VGroup(
            SVGMobject("female_doctor"),
            SVGMobject("female_doctor"),
            SVGMobject("female_doctor"),
            SVGMobject("male_doctor"),
            SVGMobject("male_doctor"),
        )
        for doc in new_doctors:
            doc.remove(doc[0])
            doc.set_stroke(width=0)
            doc.set_fill(GREY_B)
        new_doctors.arrange_in_grid(2, 2, buff=MED_LARGE_BUFF)
        new_doctors[4].move_to(new_doctors[:4])
        new_doctors.replace(curr_doc_group, dim_to_match=1)

        marks = VGroup()
        for n, doc in enumerate(new_doctors):
            mark = Checkmark() if n == 0 else Exmark()
            mark.move_to(doc.get_corner(UL))
            mark.shift(SMALL_BUFF * DR)
            marks.add(mark)

        self.play(
            LaggedStartMap(FadeOut, curr_doc_group, scale=0.5, run_time=1),
            FadeIn(new_doctors, lag_ratio=0.1)
        )
        self.play(ShowIncreasingSubsets(marks))
        self.wait()


class SamplePopulationBreastCancer(Scene):
    def construct(self):
        # Introduce population
        title = TextMobject(
            "Sample population of", " $1{,}000$",
            font_size=72,

        )
        title.add(Underline(title, color=LIGHT_GREY))
        title.to_edge(UP, buff=MED_SMALL_BUFF)
        self.add(title)

        woman = WomanIcon()
        globals()['woman'] = woman
        population = VGroup(*[woman.copy() for x in range(1000)])
        population.arrange_in_grid(
            25, 40,
            buff=LARGE_BUFF,
            fill_rows_first=False,
        )
        population.set_height(6)
        population.next_to(title, DOWN)

        counter = Integer(1000, edge_to_fix=UL)
        counter.replace(title[1])
        counter.set_value(0)

        title[1].set_opacity(0)
        self.play(
            ShowIncreasingSubsets(population),
            ChangeDecimalToValue(counter, 1000),
            run_time=2
        )
        self.remove(counter)
        title[1].set_opacity(1)
        self.wait()

        # Show true positives
        rects = VGroup(Rectangle(), Rectangle())
        rects.set_height(6)
        rects[0].set_width(4, stretch=True)
        rects[1].set_width(8, stretch=True)
        rects[0].set_stroke(YELLOW, 3)
        rects[1].set_stroke(GREY, 3)
        rects.arrange(RIGHT)
        rects.center().to_edge(DOWN, buff=MED_SMALL_BUFF)

        positive_cases = population[:10]
        negative_cases = population[10:]

        positive_cases.generate_target()
        positive_cases.target.move_to(rects[0])
        positive_cases.target.set_color(YELLOW)

        negative_cases.generate_target()
        negative_cases.target.set_height(rects[1].get_height() * 0.8)
        negative_cases.target.move_to(rects[1])

        positive_words = TextMobject(r"1\% ", "Have breast cancer", font_size=36)
        positive_words.set_color(YELLOW)
        positive_words.next_to(rects[0], UP, SMALL_BUFF)

        negative_words = TextMobject(r"99\% ", "Do not", font_size=36)
        negative_words.set_color(GREY_B)
        negative_words.next_to(rects[1], UP, SMALL_BUFF)

        self.play(
            MoveToTarget(positive_cases),
            MoveToTarget(negative_cases),
            Write(positive_words, run_time=1),
            Write(negative_words, run_time=1),
            FadeIn(rects),
        )
        self.wait()

        # Sensitivity
        tpr_words = TextMobject("9 True positives", font_size=36)
        fnr_words = TextMobject("1 False negative", font_size=36)
        tnr_words = TextMobject("900 True negatives", font_size=36)
        fpr_words = TextMobject("89 False positives", font_size=36)

        tpr_words.set_color(GREEN_B)
        fnr_words.set_color(RED_D)
        tnr_words.set_color(RED_B)
        fpr_words.set_color(GREEN_D)

        tp_cases = positive_cases[:9]
        fn_cases = positive_cases[9:]

        tpr_words.next_to(tp_cases, UP)
        fnr_words.next_to(fn_cases, DOWN)

        signs = VGroup()
        for woman in tp_cases:
            sign = TexMobject("+")
            sign.set_color(GREEN_B)
            sign.match_height(woman)
            sign.next_to(woman, RIGHT, SMALL_BUFF)
            woman.sign = sign
            signs.add(sign)
        for woman in fn_cases:
            sign = TexMobject("-")
            sign.set_color(RED)
            sign.match_width(signs[0])
            sign.next_to(woman, RIGHT, SMALL_BUFF)
            woman.sign = sign
            signs.add(sign)

        boxes = VGroup()
        for n, woman in enumerate(positive_cases):
            box = SurroundingRectangle(woman, buff=0)
            box.set_stroke(width=2)
            if woman in tp_cases:
                box.set_color(GREEN)
            else:
                box.set_color(RED)
            woman.box = box
            boxes.add(box)

        self.play(
            FadeIn(tpr_words, shift=0.2 * UP),
            ShowIncreasingSubsets(signs[:9]),
            ShowIncreasingSubsets(boxes[:9]),
        )
        self.wait()
        self.play(
            FadeIn(fnr_words, shift=0.2 * DOWN),
            Write(signs[9:]),
            ShowCreation(boxes[9:]),
        )
        self.wait()

        # Specificity
        negative_cases.sort(lambda p: -p[1])

        num_fp = int(len(negative_cases) * 0.09)
        fp_cases = negative_cases[:num_fp]
        tn_cases = negative_cases[num_fp:]

        new_boxes = VGroup()
        for n, woman in enumerate(negative_cases):
            box = SurroundingRectangle(woman, buff=0)
            box.set_stroke(width=2)
            if woman in fp_cases:
                box.set_color(GREEN)
            else:
                box.set_color(RED)
            woman.box = box
            new_boxes.add(box)

        fpr_lhs = TexMobject("(0.09)(990) \\approx", font_size=36)
        fpr_lhs.next_to(fpr_words, LEFT)
        fpr_lhs.set_color(GREY_A)

        VGroup(fpr_words, fpr_lhs).next_to(fp_cases, UP, buff=SMALL_BUFF)
        tnr_words.next_to(tn_cases, DOWN, buff=0.2)

        self.play(
            FadeIn(fpr_words, shift=0.2 * UP),
            FadeIn(fpr_lhs, shift=0.2 * UP),
            ShowIncreasingSubsets(new_boxes[:num_fp])
        )
        self.wait()
        self.play(
            FadeIn(tnr_words, shift=0.2 * DOWN),
            ShowIncreasingSubsets(new_boxes[num_fp:])
        )
        self.wait()

        # Consolidate boxes
        self.remove(boxes, new_boxes, population)
        for woman in population:
            woman.add(woman.box)
        self.add(population)

        # Emphasize true positives
        self.play(
            LaggedStartMap(Indicate, tp_cases),
            ShowCreationThenDestruction(
                Underline(tpr_words, buff=0, color=GREEN)
            ),
        )
        self.wait()

        # Limit view to positive cases
        for cases, nr, rect in zip([tp_cases, fp_cases], [3, 7], rects):
            cases.generate_target()
            for case in cases.target:
                case[-1].set_stroke(width=3)
                case[-1].scale(1.1)
            cases.target.arrange_in_grid(
                n_rows=nr,
                buff=0.5 * cases[0].get_width()
            )
            cases.target.scale(0.5 / cases.target[0].get_height())
            cases.target.move_to(rect)

        fp_cases.target.shift(0.4 * DOWN)

        self.play(
            MoveToTarget(tp_cases),
            MoveToTarget(fp_cases),
            tpr_words.next_to, tp_cases.target, UP,
            fpr_words.next_to, fp_cases.target, UP,
            FadeOut(signs),
            FadeOut(positive_words[0]),
            FadeOut(negative_words[0]),
            positive_words[1].match_x, rects[0],
            negative_words[1].match_x, rects[1],
            LaggedStart(
                FadeOut(fn_cases, shift=DOWN),
                FadeOut(fnr_words, shift=DOWN),
                FadeOut(tn_cases, shift=DOWN),
                FadeOut(tnr_words, shift=DOWN),
                FadeOut(fpr_lhs),
            ),
        )
        self.wait()

        # Final equation
        equation = TexMobject(
            "P(",
            "\\text{Have cancer }",
            "|",
            "\\text{ positive test})",
            "\\approx",
            "\\frac{9}{9 + 89}",
            "\\approx \\frac{1}{11}"
        )
        equation.set_color_by_tex("cancer", YELLOW)
        equation.set_color_by_tex("positive", GREEN)
        equation.to_edge(UP, buff=SMALL_BUFF)

        self.play(
            FadeIn(equation[:-1], shift=UP),
            FadeOut(title, shift=UP),
        )
        self.wait()
        self.play(Write(equation[-1]))
        self.wait()


class ReframeWhatTestsDo(TeacherStudentsScene):
    def construct(self):
        # Question
        question = TextMobject("What do tests tell you?")
        self.teacher_holds_up(question)

        question.generate_target()
        question.target.set_height(0.6)
        question.target.center()
        question.target.to_edge(UP)
        self.play(
            MoveToTarget(question),
            *[
                ApplyMethod(pi.change, "pondering", question.target)
                for pi in self.pi_creatures
            ]
        )
        self.wait(2)

        # Possible answers
        answers = VGroup(
            TextMobject("Tests", " determine", " if you have", " a disease."),
            TextMobject("Tests", " determine", " your chances of having", " a disease."),
            TextMobject("Tests", " update", " your chances of having", " a disease."),
        )
        students = self.students
        answers.set_color(BLUE_C)
        answers.arrange(DOWN)
        answers.next_to(question, DOWN, MED_LARGE_BUFF)

        answers[1][2].set_fill(GREY_A)
        answers[2][2].set_fill(GREY_A)
        answers[2][1].set_fill(YELLOW)

        def add_strike_anim(words):
            strike = Line()
            strike.replace(words, dim_to_match=0)
            strike.set_stroke(RED, 5)
            anim = ShowCreation(strike)
            words.add(strike)
            return anim

        self.play(
            GrowFromPoint(answers[0], students[0].get_corner(UR)),
            students[0].change, "raise_right_hand", answers[0],
            students[1].change, "sassy", students[0].eyes,
            students[2].change, "sassy", students[0].eyes,
        )
        self.wait()
        self.play(
            add_strike_anim(answers[0]),
            students[0].change, "guilty",
        )
        self.wait()

        answers[1][2].save_state()
        answers[1][2].replace(answers[0][2], stretch=True)
        answers[1][2].set_opacity(0)
        self.play(
            TransformFromCopy(
                answers[0][:2],
                answers[1][:2],
            ),
            TransformFromCopy(
                answers[0][3],
                answers[1][3],
            ),
            Restore(answers[1][2]),
            students[0].change, "pondering", answers[1],
            students[1].change, "raise_right_hand", answers[1],
            students[2].change, "pondering", answers[1],
        )
        self.wait(2)
        self.play(
            add_strike_anim(answers[1]),
            students[1].change, "guilty",
        )
        self.wait(2)

        answers[2][1].save_state()
        answers[2][1].replace(answers[1][1], stretch=True)
        answers[2][1].set_opacity(0)
        self.play(
            TransformFromCopy(
                answers[1][:1],
                answers[2][:1],
            ),
            TransformFromCopy(
                answers[1][2:],
                answers[2][2:],
            ),
            Restore(answers[2][1]),
            students[0].change, "pondering", answers[1],
            students[1].change, "pondering", answers[1],
            students[2].change, "raise_left_hand", answers[1],
        )
        self.play(
            self.teacher.change, "happy", students[2].eyes,
        )
        self.wait()


class ShowUpdatingPrior(Scene):
    def construct(self):
        # Show prior
        woman = WomanIcon()
        population = VGroup(*[woman.copy() for x in range(100)])
        population.arrange_in_grid()
        population.set_fill(GREY)
        population[0].set_fill(YELLOW)
        population.set_height(5)

        prior_prob = TextMobject("1", " in ", "100")
        prior_prob.set_color_by_tex("1", YELLOW)
        prior_prob.set_color_by_tex("100", GREY_B)
        prior_prob.next_to(population, UP, MED_LARGE_BUFF)
        prior_brace = Brace(prior_prob, UP, buff=SMALL_BUFF)
        prior_words = prior_brace.get_text("Prior")

        hundred_part = prior_prob.get_part_by_tex("100")
        pop_count = Integer(100)
        pop_count.replace(hundred_part)
        pop_count.match_color(hundred_part)
        pop_count.set_value(0)
        prior_prob.replace_submobject(2, pop_count)

        VGroup(population, prior_prob, prior_brace, prior_words).to_corner(UL)

        self.add(prior_prob)
        self.add(prior_brace)
        self.add(prior_words)

        self.play(
            ShowIncreasingSubsets(population),
            ChangeDecimalToValue(pop_count, len(population)),
        )
        self.wait()

        # Update arrow
        update_arrow = Arrow(2 * LEFT, 2 * RIGHT)
        update_arrow.set_thickness(0.1)
        update_arrow.center()
        update_arrow.match_y(pop_count)
        update_words = TextMobject("Gets updated")
        update_words.next_to(update_arrow, UP, SMALL_BUFF)

        self.play(
            GrowArrow(update_arrow),
            FadeIn(update_words, lag_ratio=0.2),
        )

        # Posterior
        post_pop = population[:11].copy()
        post_pop.arrange_in_grid(
            n_rows=2,
            buff=get_norm(population[1].get_left() - population[0].get_right())
        )
        post_pop.next_to(
            update_arrow, RIGHT,
            buff=abs(population.get_right()[0] - update_arrow.get_left()[0])
        )
        post_pop.align_to(population, UP)

        post_prob = prior_prob.copy()
        post_prob[2].set_value(11)
        post_prob.next_to(post_pop, UP, buff=MED_LARGE_BUFF)
        post_prob[2].set_value(0)

        roughly = TextMobject("(roughly)", font_size=24)
        roughly.next_to(post_prob, RIGHT, buff=MED_LARGE_BUFF)

        self.add(post_prob)
        self.play(
            ShowIncreasingSubsets(post_pop),
            ChangeDecimalToValue(post_prob[2], 11),
        )
        self.play(FadeIn(roughly))
        self.wait()

        post_brace = Brace(post_prob, UP, buff=SMALL_BUFF)
        post_words = post_brace.get_text("Posterior")

        self.play(
            GrowFromCenter(post_brace),
            FadeIn(post_words, shift=0.5 * UP)
        )
        self.wait()

        post_group = VGroup(
            update_arrow, update_words,
            post_pop, post_prob, post_brace, post_words,
        )
        post_group.save_state()

        # Show test statistics
        def get_prob_bars(p_positive):
            rects = VGroup(Square(), Square())
            rects.set_width(0.2, stretch=True)
            rects.set_stroke(WHITE, 2)
            rects[0].stretch(p_positive, 1, about_edge=UP)
            rects[1].stretch(1 - p_positive, 1, about_edge=DOWN)
            rects[0].set_fill(GREEN, 1)
            rects[1].set_fill(RED_E, 1)

            braces = VGroup(*[
                Brace(rect, LEFT, buff=SMALL_BUFF)
                for rect in rects
            ])
            positive_percent = int(p_positive * 100)
            percentages = VGroup(
                TextMobject(f"{positive_percent}\\% +", color=GREEN),
                TextMobject(f"{100 - positive_percent}\\% $-$", color=RED),
            )
            percentages.scale(0.7)
            for percentage, brace in zip(percentages, braces):
                percentage.next_to(brace, LEFT, SMALL_BUFF)

            result = VGroup(
                rects,
                braces,
                percentages,
            )

            return result

        boxes = VGroup(
            Square(color=YELLOW),
            Square(color=GREY_B)
        )
        boxes.set_height(3)
        labels = VGroup(
            TextMobject("With cancer"),
            TextMobject("Without cancer"),
        )
        for box, label in zip(boxes, labels):
            label.next_to(box, UP)
            label.match_color(box)
            box.push_self_into_submobjects()
            box.add(label)

        boxes.arrange(DOWN, buff=0.5)
        boxes.to_edge(RIGHT)

        sens_bars = get_prob_bars(0.9)
        spec_bars = get_prob_bars(0.09)
        bar_groups = VGroup(sens_bars, spec_bars)
        for bars, box in zip(bar_groups, boxes):
            bars.shift(box[0].get_right() - bars[0].get_center())
            bars.shift(0.75 * LEFT)
            box.add(bars)

        self.play(
            FadeIn(boxes[0], lag_ratio=0.1),
            post_group.scale, 0.1, {"about_point": FRAME_HEIGHT * DOWN / 2}
        )
        self.wait()
        self.play(
            FadeIn(boxes[1], lag_ratio=0.1)
        )
        self.wait()

        # Pull out Bayes factor
        ratio = VGroup(
            sens_bars[2][0].copy(),
            TexMobject("\\phantom{90\\%+} \\over \\phantom{9\\%+}"),
            spec_bars[2][0].copy(),
            *TexMobject("=", "10"),
        )
        ratio.generate_target()
        ratio.target[:3].arrange(DOWN, buff=0.2)
        ratio.target[3:].arrange(RIGHT, buff=0.2)
        ratio.target[3:].next_to(ratio.target[:3], RIGHT, buff=0.2)
        ratio.target.center()

        ratio[1].scale(0)
        ratio[3:].scale(0)

        new_boxes = VGroup(boxes[0][0], boxes[1][0]).copy()
        new_boxes.generate_target()
        for box, part in zip(new_boxes.target, ratio.target[::2]):
            box.replace(part, stretch=True)
            box.scale(1.2)
            box.set_stroke(width=2)

        self.play(
            MoveToTarget(ratio),
            MoveToTarget(new_boxes),
        )
        self.wait()

        for part, box in zip(ratio[0:3:2], new_boxes):
            part.add(box)

        self.remove(new_boxes)
        self.add(ratio)

        bayes_factor_label = TextMobject("``Bayes factor''")
        bayes_factor_label.next_to(ratio, UP, LARGE_BUFF)
        self.play(Write(bayes_factor_label))
        self.wait()

        # Show updated result
        bayes_factor_label.generate_target()
        bayes_factor_label.target.scale(0.8)
        bayes_factor_label.target.next_to(
            post_group.saved_state[0], DOWN,
            buff=LARGE_BUFF,
        )

        self.play(
            MoveToTarget(bayes_factor_label),
            ratio.scale, 0.8,
            ratio.next_to, bayes_factor_label.target, DOWN,
            Restore(post_group),
            FadeOut(boxes, shift=2 * RIGHT),
        )
        self.wait()

        # Change prior and posterior
        pop1000, pop100, pop10, pop2 = pops = [
            VGroup(*[woman.copy() for x in range(n)])
            for n in [1000, 100, 10, 2]
        ]
        for pop in pops:
            pop.arrange_in_grid()
            pop.set_fill(GREY)
            pop[0].set_fill(YELLOW)
            pop.scale(
                population[0].get_height() / pop[0].get_height()
            )

        pop1000.replace(population)
        pop100.move_to(post_pop, UP)
        pop10.move_to(population, UP)
        pop10.shift(0.2 * LEFT)
        pop2.move_to(post_pop, UP)
        pop2.shift(0.2 * LEFT)

        def replace_population_anims(old_pop, new_pop, count, brace):
            count.set_value(len(new_pop))
            brace.generate_target()
            brace.target.match_width(
                Line(brace.get_left(), count.get_right()),
                about_edge=LEFT,
                stretch=True,
            )
            count.set_value(len(old_pop))

            return [
                FadeOut(old_pop, lag_ratio=0.1),
                ShowIncreasingSubsets(new_pop),
                ChangeDecimalToValue(count, len(new_pop)),
                MoveToTarget(brace)
            ]

        self.play(
            *replace_population_anims(population, pop1000, prior_prob[2], prior_brace)
        )
        self.play(
            *replace_population_anims(post_pop, pop100, post_prob[2], post_brace),
            roughly.shift, 0.25 * RIGHT
        )
        self.wait(2)
        self.play(
            *replace_population_anims(pop1000, pop10, prior_prob[2], prior_brace),
            prior_words.shift, 0.1 * LEFT
        )
        self.play(
            *replace_population_anims(pop100, pop2, post_prob[2], post_brace)
        )
        self.wait(2)


class AskAboutHowItsSoLow(TeacherStudentsScene):
    def construct(self):
        question = TextMobject(
            "How can it be 1 in 11\\\\"
            "if the test is accurate more\\\\"
            "than 90\\% of the time?",
            tex_to_color_map={
                "1 in 11": BLUE,
                "90\\%": YELLOW,
            }
        )
        self.student_says(
            question,
            student_index=1,
            target_mode="maybe",
        )
        self.change_student_modes(
            "confused", "maybe", "confused",
            look_at_arg=question,
        )
        self.wait()
        self.play(self.teacher.change, "tease", question)
        self.wait(2)


class HowDoesUpdatingWork(TeacherStudentsScene):
    def construct(self):
        students = self.students
        teacher = self.teacher

        self.student_says(
            "Where are these\\\\numbers coming\\\\from?",
            target_mode="raise_right_hand"
        )
        self.play(
            teacher.change, "happy",
            self.get_student_changes("confused", "erm", "raise_right_hand"),
        )
        self.look_at(self.screen)
        self.wait(3)

        sample_pop = TextMobject("Sample populations (most intuitive)")
        bayes_factor = TextMobject("Bayes' factor (most fun)")
        for words in sample_pop, bayes_factor:
            words.move_to(self.hold_up_spot, DOWN)
            words.shift_onto_screen()

        bayes_factor.set_fill(YELLOW)

        self.play(
            RemovePiCreatureBubble(students[2]),
            teacher.change, "raise_right_hand",
            FadeIn(sample_pop, shift=UP, scale=1.5),
            self.get_student_changes(
                "pondering", "thinking", "pondering",
                look_at_arg=sample_pop,
            )
        )
        self.wait(2)
        self.play(
            FadeIn(bayes_factor, shift=UP, scale=1.5),
            sample_pop.shift, UP,
            teacher.change, "hooray",
            self.get_student_changes(
                "thinking", "confused", "erm",
            )
        )
        self.look_at(bayes_factor)
        self.wait(3)


class SamplePopulation10PercentPrevalence(Scene):
    def construct(self):
        # Add test accuracy figures
        accuracy_figures = VGroup(
            TextMobject(
                "90\\% Sensitivity,", " 10\\% False negative rate",
                font_size=36
            ),
            TextMobject(
                "91\\% Specificity,", " 9\\% False positive rate",
                font_size=36
            ),
        )
        accuracy_figures.arrange(RIGHT, buff=LARGE_BUFF)
        accuracy_figures.to_edge(UP)

        for color, text in zip([YELLOW, GREY], accuracy_figures):
            text.add(Underline(text, color=color, stroke_width=2))

        self.add(accuracy_figures)

        # Show population
        population = VGroup(*[WomanIcon() for x in range(100)])
        population.arrange_in_grid(fill_rows_first=False)
        population.set_height(5)
        population.next_to(accuracy_figures, DOWN, MED_LARGE_BUFF)
        cancer_cases = population[:10]
        healthy_cases = population[10:]
        cancer_cases.set_fill(YELLOW)
        healthy_cases.set_fill(GREY)

        population.generate_target()
        reordered_pop = VGroup(*population)
        reordered_pop.shuffle()
        for m1, m2 in zip(reordered_pop, population.target):
            m1.move_to(m2)
        population.target[:10].next_to(accuracy_figures[0], DOWN, MED_LARGE_BUFF)
        population.target[10:].next_to(accuracy_figures[1], DOWN, MED_LARGE_BUFF)

        pop_words = TextMobject("100", " patients")
        wc_words = TextMobject("10", " with cancer")
        wo_words = TextMobject("90", " without cancer")

        pop_words.next_to(population, DOWN)
        wc_words.next_to(population.target[:10], DOWN)
        wo_words.next_to(population.target[10:], DOWN)
        for words in wc_words, wo_words:
            words.save_state()
            words[0].replace(pop_words[0], stretch=True)
            words[1].replace(pop_words[1], stretch=True)
            words.set_opacity(0)

        self.play(
            FadeIn(pop_words),
            FadeIn(population, lag_ratio=0.1),
        )
        self.wait()
        self.play(
            MoveToTarget(population, run_time=2),
            Restore(wc_words),
            Restore(wo_words),
            FadeOut(pop_words),
        )
        self.wait()

        # Show test results
        c_boxes = VGroup(*(
            SurroundingRectangle(icon, buff=0)
            for icon in cancer_cases
        ))
        h_boxes = VGroup(*(
            SurroundingRectangle(icon, buff=0)
            for icon in healthy_cases
        ))
        all_boxes = VGroup(c_boxes, h_boxes)
        all_boxes.set_stroke(width=3)

        c_boxes[:9].set_stroke(GREEN)
        c_boxes[9:].set_stroke(RED)
        h_boxes.set_stroke(RED)

        false_positives = healthy_cases[0:80:10]
        false_positive_boxes = h_boxes[0:80:10]
        false_positive_boxes.set_stroke(GREEN)

        for n, box in enumerate(c_boxes):
            tex = "+" if n < 9 else "-"
            sign = TexMobject(tex, font_size=36)
            sign.next_to(box, RIGHT, SMALL_BUFF)
            sign.match_color(box)
            box.add(sign)

        for box in false_positive_boxes:
            sign = TexMobject("+", font_size=36)
            sign.next_to(box, UP, SMALL_BUFF)
            sign.match_color(box)
            box.add(sign)

        for i, boxes in (0, c_boxes), (1, h_boxes):
            self.play(ShowCreationThenFadeOut(SurroundingRectangle(
                accuracy_figures[i][i],
                buff=SMALL_BUFF,
                stroke_color=GREEN,
            )))
            self.play(ShowIncreasingSubsets(boxes))
            self.wait()

        for icon, box in zip(cancer_cases, c_boxes):
            icon.add(box)
        for icon, box in zip(healthy_cases, h_boxes):
            icon.add(box)

        self.remove(all_boxes)
        self.add(population)

        # Filter down to positive cases
        new_wc_words = TextMobject("9 ", "with cancer")
        new_wo_words = TextMobject("8 ", "without cancer")
        for nw, w in (new_wc_words, wc_words), (new_wo_words, wo_words):
            nw[0].set_color(GREEN)
            nw.move_to(w)

        wc_words.unlock_triangulation()
        self.play(
            cancer_cases[:9].move_to, cancer_cases,
            FadeOut(cancer_cases[9:]),
            ReplacementTransform(wc_words, new_wc_words),
        )
        self.wait()
        wo_words.unlock_triangulation()
        self.play(
            false_positives.move_to, healthy_cases,
            FadeOut(VGroup(*(
                case for case in healthy_cases
                if case not in false_positives
            ))),
            ReplacementTransform(wo_words, new_wo_words),
        )
        self.wait()

        # Rearrange true positives
        false_positives.generate_target()
        false_positives.target.shift(DOWN)
        true_positives = cancer_cases[:9]
        true_positives.generate_target()
        for case in true_positives.target:
            box = case[-1]
            sign = box[-1]
            sign.next_to(case[:-1], UP, SMALL_BUFF)
        true_positives.target.arrange(
            RIGHT,
            buff=get_norm(false_positives[0].get_right() - false_positives[1].get_left()),
        )
        true_positives.target.match_y(false_positives.target)
        true_positives.target.match_x(new_wc_words)

        self.play(
            MoveToTarget(true_positives),
            MoveToTarget(false_positives),
            new_wc_words.next_to, true_positives.target, DOWN,
            new_wo_words.next_to, false_positives.target, DOWN,
        )
        self.wait()

        # Show final fraction
        answer = TexMobject(
            "{9 \\over 9 + 8} \\approx 0.53",
            font_size=72,
        )[0]
        answer.next_to(accuracy_figures, DOWN, LARGE_BUFF)
        nine1 = new_wc_words[0].copy()
        nine2 = new_wc_words[0].copy()
        eight = new_wo_words[0].copy()

        self.play(
            nine1.replace, answer[0],
            nine2.replace, answer[2],
            eight.replace, answer[4],
            Write(answer[1:5:2]),
        )
        self.wait()
        self.play(Write(answer[5:]))
        self.wait()


class HighlightBayesFactorOverlay(Scene):
    def construct(self):
        rect = Rectangle(height=2, width=3)
        rect.set_stroke(BLUE, 3)
        words = TextMobject("How to\\\\use this")
        words.next_to(rect, DOWN, buff=1.5)
        words.shift(2 * RIGHT)
        words.match_color(rect)
        arrow = Arrow(
            words.get_left(),
            rect.get_bottom(),
            path_arc=-60 * DEGREES
        )
        arrow.match_color(words)

        self.play(
            FadeIn(words, scale=1.1),
            DrawBorderThenFill(arrow),
        )
        self.play(
            ShowCreation(rect),
        )
        self.wait()


class ContrastTwoContexts(Scene):
    def construct(self):
        # Background
        bg_rect = FullScreenFadeRectangle()
        bg_rect.set_fill(GREY_E, 1)
        self.add(bg_rect)

        # Scene templates
        screens = VGroup(*(
            ScreenRectangle() for x in range(2)
        ))
        screens.set_stroke(WHITE, 2)
        screens.set_fill(BLACK, 1)
        screens.arrange(DOWN, buff=LARGE_BUFF)
        screens.set_height(FRAME_HEIGHT - 1)
        screens.to_edge(RIGHT)

        self.add(screens)

        # Words
        words = VGroup(
            TextMobject("Same", " test"),
            TextMobject("Same", " accuracy"),
            TextMobject("Same", " result"),
        )
        words.scale(1.5)
        words.arrange(DOWN, aligned_edge=LEFT, buff=MED_LARGE_BUFF)
        words.to_edge(LEFT)
        words.set_stroke(BLACK, 3, background=True)

        for word in words[:2]:
            self.add(word)
            self.wait()

        # Show receiving results
        def get_positive_result():
            woman = WomanIcon()
            clipboard = SVGMobject(
                "clipboard",
                stroke_width=0,
                fill_color=interpolate_color(GREY_BROWN, WHITE, 0.2)
            )
            clipboard.set_width(1)
            clipboard.next_to(woman, LEFT)
            content = TextMobject("+\\\\", "Cancer\\\\detected")
            content[0].scale(2, about_edge=DOWN)
            content[0].set_color(GREEN)
            content[0].set_stroke(GREEN, 3)
            content[0].shift(SMALL_BUFF * UP)
            content.set_width(0.7 * clipboard.get_width())
            content.move_to(clipboard)
            content.shift(SMALL_BUFF * DOWN)
            clipboard.add(content)
            result = VGroup(woman, clipboard)
            result.scale(0.7)
            return result

        globals()['get_positive_result'] = get_positive_result

        positive_results = VGroup(*(
            get_positive_result() for x in range(2)
        ))
        positive_results.generate_target()
        positive_results.set_opacity(0)
        for screen, result in zip(screens, positive_results.target):
            result.next_to(screen, LEFT, aligned_edge=DOWN)

        self.add(words[2])
        self.play(MoveToTarget(positive_results))
        self.wait()

        # Different results
        probs = VGroup(
            DecimalNumber(0.0),
            DecimalNumber(0.0),
        )
        probs.set_fill(YELLOW)
        for prob, result in zip(probs, positive_results):
            prob.next_to(result, UP)

        self.play(
            ChangeDecimalToValue(probs[0], 0.09),
            ChangeDecimalToValue(probs[1], 0.53),
            UpdateFromAlphaFunc(
                Mobject(),
                lambda m, a, probs=probs: probs.set_opacity(a),
                remover=True,
            )
        )
        self.wait()

        # What test accuracy does
        ta_words = VGroup(
            TextMobject("Test", " accuracy"),
            TextMobject("\\emph{alone} ", "does not"),
            TextMobject("determine", "."),
            TextMobject("", "your chances"),
        )
        ta_words[2][1].set_opacity(0)
        ta_words[1].set_color_by_tex("not", RED)

        up_words = VGroup(
            TextMobject("Test", " accuracy"),
            TextMobject("determine", "s"),
            TextMobject("how", " your chances"),
            TextMobject("are", " \\emph{updated}"),
        )
        up_words[3][1].set_color(BLUE)
        up_words[3].shift(SMALL_BUFF * UP)
        up_words[0].shift(SMALL_BUFF * DOWN)

        for group in ta_words, up_words:
            group.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
            group.scale(1.5)
            group.to_edge(LEFT)
            group.set_stroke(BLACK, 3, background=True)

        words[0][1].unlock_triangulation()
        self.play(
            FadeOut(words[0][0]),
            FadeOut(words[1][0]),
            FadeOut(words[2]),
            ReplacementTransform(words[0][1], ta_words[0][0]),
            ReplacementTransform(words[1][1], ta_words[0][1]),
            LaggedStartMap(FadeIn, ta_words[1:]),
        )
        self.add(ta_words)
        self.wait()
        ta_words.unlock_triangulation()
        self.play(
            ReplacementTransform(ta_words[0], up_words[0]),
            ReplacementTransform(ta_words[2], up_words[1]),
            FadeIn(up_words[2], scale=2),
            ReplacementTransform(ta_words[3], up_words[2]),
            FadeOut(ta_words[1], scale=0.5),
        )
        self.play(Write(up_words[3]))
        self.wait()

        underlines = VGroup()
        for word in up_words:
            line = Underline(word)
            line.set_y(word[0][0].get_bottom()[1])
            line.shift(SMALL_BUFF * DOWN)
            underlines.add(line)
        underlines.set_stroke(BLUE, 3)
        shifted_underlines = underlines.copy().shift(SMALL_BUFF * DOWN)
        shifted_underlines.set_stroke(BLUE_E, 3)
        underlines.add(*shifted_underlines)

        self.add(underlines, up_words)
        self.play(ShowCreation(
            underlines,
            run_time=2,
            rate_func=double_smooth,
        ))
        self.wait()


class BayesTheorem(Scene):
    def construct(self):
        # Add title
        title = TextMobject("Bayes' theorem", font_size=72)
        title.to_edge(UP, buff=MED_SMALL_BUFF)
        title.add(Underline(title))
        self.add(title)

        # Draw rectangle
        prior = 1 / 12
        sensitivity = 0.8
        specificity = 0.9

        rects = VGroup(*[Square() for x in range(4)])
        # rects[0::2].set_stroke(GREEN, 3)
        # rects[1::2].set_stroke(RED, 3)
        rects.set_stroke(WHITE, 2)
        rects[:2].set_stroke(YELLOW)
        rects.set_fill(GREY_D, 1)
        rects.set_height(3)
        rects.set_width(3, stretch=True)
        rects.move_to(3.5 * LEFT)

        rects[:2].stretch(prior, 0, about_edge=LEFT)
        rects[2:].stretch(1 - prior, 0, about_edge=RIGHT)
        rects[0].stretch(sensitivity, 1, about_edge=UP)
        rects[1].stretch(1 - sensitivity, 1, about_edge=DOWN)
        rects[2].stretch(1 - specificity, 1, about_edge=UP)
        rects[3].stretch(specificity, 1, about_edge=DOWN)

        rects[0].set_fill(GREEN_D)
        rects[1].set_fill(interpolate_color(RED_E, BLACK, 0.5))
        rects[2].set_fill(GREEN_E)
        rects[3].set_fill(interpolate_color(RED_E, BLACK, 0.75))

        icons = VGroup(*(WomanIcon() for x in range(120)))
        icons.arrange_in_grid(
            10, 12,
            h_buff=1, v_buff=0.5,
            fill_rows_first=False,
        )
        icons.replace(rects, dim_to_match=1)
        icons.scale(0.98)
        icons[:10].set_fill(YELLOW)

        # Add terminology
        braces = VGroup(
            Brace(rects[1], DOWN, buff=SMALL_BUFF),
            *(
                Brace(rect, u * RIGHT, buff=SMALL_BUFF)
                for rect, u in zip(rects, [-1, -1, 1, 1])
            )
        )
        braces.set_fill(GREY_B)
        terms = VGroup(
            TextMobject("Prior"),
            TextMobject("Sensitivity"),
            TextMobject("False\\\\negative\\\\rate"),
            TextMobject("False\\\\positive\\\\rate"),
            TextMobject("Specificity"),
        )
        terms[0].set_color(YELLOW)
        for term, brace in zip(terms, braces):
            term.scale(0.5)
            term.next_to(brace, brace.direction, buff=SMALL_BUFF)

        # Formula with jargon
        lhs = TexMobject(
            "P(",
            "\\text{Sick}",
            "\\text{ given }",
            "\\text{+}",
            ")"
        )
        lhs.set_color_by_tex("Sick", YELLOW)
        lhs.set_color_by_tex("+", GREEN)
        lhs.set_x(3.5)
        lhs.set_y(2)

        equals = TexMobject("=")
        equals.rotate(PI / 2)
        equals.scale(1.5)

        term_formula = TexMobject(
            """
            {(\\text{Prior})(\\text{Sensitivity})
            \\over
            (\\text{Prior})(\\text{Sensitivity})
            +
            (1 - \\text{Prior})(\\text{FPR})
            """,
            font_size=30,
            tex_to_color_map={
                "\\text{Prior}": YELLOW,
                "\\text{Sensitivity}": GREEN,
                "\\text{FPR}": GREEN_D,
            }
        )

        eq2 = equals.copy()

        prob_formula = TexMobject(
            """
            P(\\text{Sick}) P(\\text{+} \\text{ given } \\text{Sick})
            \\over
            P(\\text{+})
            """,
            tex_to_color_map={
                "\\text{Sick}": YELLOW,
                "\\text{+}": GREEN,
            },
            font_size=30
        )

        formula = VGroup(lhs, equals, term_formula, eq2, prob_formula)
        formula.arrange(DOWN, buff=0.35)
        formula.to_edge(RIGHT)

        # Animations
        rects.set_opacity(0)
        rects.submobjects.reverse()
        icons.save_state()
        icons.set_height(6)
        icons.center().to_edge(DOWN)

        self.add(icons)
        self.wait()
        self.play(Restore(icons))
        self.add(rects, icons)
        self.play(
            rects.set_opacity, 1,
            icons.set_opacity, 0.1,
            LaggedStartMap(GrowFromCenter, braces),
            LaggedStartMap(FadeIn, terms),
        )
        self.wait()
        self.play(LaggedStartMap(FadeIn, formula, scale=1.2, run_time=2))
        self.wait()

        # Show confused
        randy = Randolph(height=1.5)
        randy.to_edge(DOWN)

        self.play(FadeIn(randy))
        self.play(randy.change, 'maybe', formula)
        self.play(Blink(randy))
        self.play(randy.change, 'confused', formula)
        self.wait()
        self.play(Blink(randy))
        self.wait()

        # Back to population
        self.add(rects, icons)
        self.play(
            icons.set_opacity, 1,
            rects.set_opacity, 0.5,
            randy.change, "pondering", icons,
        )
        self.play(Blink(randy))
        self.wait()


class ProbabilityVsOdds(Scene):
    def construct(self):
        # Show titles and division
        titles = VGroup(
            TextMobject("Probability"),
            TextMobject("Odds"),
        )
        for title, u in zip(titles, [-1, 1]):
            title.scale(1.5)
            title.to_edge(UP)
            title.set_x(FRAME_WIDTH * u / 4)

        h_line = Line(LEFT, RIGHT)
        h_line.set_width(FRAME_WIDTH)
        h_line.next_to(titles, DOWN, SMALL_BUFF)
        h_line.set_x(0)

        v_line = Line(UP, DOWN)
        v_line.set_height(FRAME_HEIGHT)
        v_line.center()

        VGroup(h_line, v_line).set_stroke(GREY, 2)

        titles.save_state()
        for title in titles:
            title.set_x(0)
        titles[1].set_opacity(0)

        self.add(titles)
        self.wait()
        self.play(
            Restore(titles),
            ShowCreation(v_line),
        )
        self.play(ShowCreation(h_line))
        self.wait()

        # Function definitions
        def get_people_row(n_all, n_pos=1):
            icon = SVGMobject("person")
            icon.set_fill(GREY)
            icon.set_stroke(WHITE, 1)
            icon.set_height(1)

            people = VGroup(*(icon.copy() for x in range(n_all)))
            people.arrange(RIGHT, buff=SMALL_BUFF)
            people[:n_pos].set_fill(YELLOW)
            return people

        def get_prob_counts(people, n_pos, n_all):
            pos_brace = Brace(people[:n_pos], UP, buff=SMALL_BUFF)
            all_brace = Brace(people, DOWN, buff=SMALL_BUFF)

            pos_label = Integer(n_pos, color=YELLOW)
            all_label = Integer(n_all)

            pos_label.next_to(pos_brace, UP)
            all_label.next_to(all_brace, DOWN)

            return VGroup(
                VGroup(pos_brace, pos_label),
                VGroup(all_brace, all_label),
            )

        def get_odds_counts(people, n_pos, n_neg):
            pos_brace = Brace(people[:n_pos], UP, buff=SMALL_BUFF)
            neg_brace = Brace(people[n_pos:], UP, buff=SMALL_BUFF)

            pos_label = Integer(n_pos, color=YELLOW)
            neg_label = Integer(n_neg, color=GREY_B)

            pos_label.next_to(pos_brace, UP)
            neg_label.next_to(neg_brace, UP)

            return VGroup(
                VGroup(pos_brace, pos_label),
                VGroup(neg_brace, neg_label),
            )

        def get_prob_label(n_pos, n_all):
            result = VGroup(
                Integer(n_pos, color=YELLOW),
                TexMobject("/"),
                Integer(n_all),
            )
            result.scale(1.5)
            result.arrange(RIGHT, buff=0.1)
            return result

        def get_odds_label(n_pos, n_neg):
            result = VGroup(
                Integer(n_pos, color=YELLOW),
                TexMobject(":"),
                Integer(n_neg, color=GREY_B),
            )
            result.scale(1.5)
            result.arrange(RIGHT, buff=0.2)
            return result

        # Show probability
        people = get_people_row(5)
        people.match_x(titles[0])
        people.shift(DOWN)
        prob_counts = get_prob_counts(people, 1, 5)

        prob = get_prob_label(1, 5)
        prob.next_to(people, UP, MED_LARGE_BUFF)

        self.play(
            FadeIn(people, lag_ratio=0.3),
            Write(prob)
        )
        self.wait()

        self.play(
            prob.shift, 1.5 * UP,
            TransformFromCopy(prob[0], prob_counts[0][1]),
            GrowFromCenter(prob_counts[0][0]),
        )
        self.play(
            TransformFromCopy(prob[2], prob_counts[1][1]),
            GrowFromCenter(prob_counts[1][0]),
        )
        self.wait()

        # Transition to odds
        right_people = people.copy()
        right_people.match_x(titles[1])

        odds = get_odds_label(1, 4)
        odds.match_x(right_people)
        odds.match_y(prob)

        arrow = Arrow(prob.get_right(), odds.get_left(), buff=1)
        arrow.set_thickness(0.1)

        odds_count = get_odds_counts(right_people, 1, 4)

        self.play(
            TransformFromCopy(people, right_people),
            TransformFromCopy(
                odds.copy().replace(prob).set_opacity(0),
                odds
            ),
            GrowArrow(arrow),
        )
        self.wait()
        self.play(
            TransformFromCopy(odds[0], odds_count[0][1]),
            GrowFromCenter(odds_count[0][0]),
        )
        self.play(
            TransformFromCopy(odds[2], odds_count[1][1]),
            GrowFromCenter(odds_count[1][0]),
        )
        self.wait()
        self.play(ShowCreationThenFadeAround(odds[1]))
        self.wait()

        # Other examples
        people.add(prob_counts)
        right_people.add(odds_count)

        def get_example(n_pos, n_all):
            new_prob = TexMobject(
                f"{int(100 * n_pos / n_all)}\\%",
                font_size=72
            )
            new_odds = get_odds_label(n_pos, n_all - n_pos)
            new_odds.next_to(new_prob, RIGHT, buff=1.5)
            arrow = Arrow(
                new_prob.get_right(),
                new_odds.get_left(),
                thickness=0.05
            )
            arrow.set_fill(GREY_A)
            example = VGroup(new_prob, arrow, new_odds)
            example.scale(0.5)
            return example

        def generate_example_movement(prob, arrow, odds, example):
            prob.unlock_triangulation()
            mover = VGroup(prob, arrow.copy(), odds)
            return ReplacementTransform(mover, example)

        def transition_to_new_example(n_pos, n_all, example,
                                      scene=self,
                                      people=people,
                                      right_people=right_people,
                                      prob=prob,
                                      odds=odds,
                                      arrow=arrow
                                      ):

            new_people = get_people_row(n_all, n_pos)
            new_people.set_x(-FRAME_WIDTH / 4)
            new_right_people = new_people.copy()
            new_right_people.set_x(FRAME_WIDTH / 4)

            new_prob = TexMobject(
                f"{int(100 * n_pos / n_all)}\\%",
                font_size=72
            )
            new_odds = get_odds_label(n_pos, n_all - n_pos)
            new_prob.move_to(prob)
            new_odds.move_to(odds)

            scene.play(
                generate_example_movement(prob, arrow, odds, example),
                FadeOut(people),
                FadeOut(right_people),
                FadeIn(new_prob),
                FadeIn(new_odds),
                FadeIn(new_people),
                FadeIn(new_right_people),
            )
            return {
                "people": new_people,
                "right_people": new_right_people,
                "prob": new_prob,
                "odds": new_odds,
            }

        examples = VGroup(*(
            get_example(n, k)
            for n, k in [(1, 10), (1, 5), (1, 2), (4, 5), (9, 10)]
        ))
        examples.arrange(UP)
        examples.to_edge(DOWN)

        kw = {}
        for n, k, ei in (1, 2, 1), (1, 10, 2), (4, 5, 0), (9, 10, 3):
            kw = transition_to_new_example(
                n, k, examples[ei], **kw
            )
            self.wait(2)

        self.remove(arrow)
        self.play(
            generate_example_movement(
                kw["prob"], arrow, kw["odds"], examples[4],
            ),
            FadeOut(kw["people"]),
            FadeOut(kw["right_people"]),
        )

        # Show ranges
        left_range = UnitInterval((0, 1, 0.1), width=5)
        left_range.set_y(1.5)
        left_range.match_x(titles[0])

        right_range = NumberLine((0, 5), width=5, include_tip=True)
        right_range.match_y(left_range)
        right_range.match_x(titles[1])
        dots = TexMobject("\\dots")
        dots.next_to(right_range, RIGHT)
        right_range.add(dots)
        right_range.add(*(
            right_range.get_tick(
                1 / n,
                right_range.tick_size * (1 / n)**0.5,
            ).set_opacity((1 / n)**0.5)
            for n in range(2, 100)
        ))

        left_range.add_numbers([0, 0.2, 0.5, 0.8, 1])
        right_range.add_numbers()

        left_ticker = ArrowTip(angle=-90 * DEGREES)
        left_ticker.set_fill(BLUE)
        left_ticker.move_to(left_range.n2p(0.5), DOWN)
        right_ticker = left_ticker.copy()
        right_ticker.set_color(RED)
        right_ticker.move_to(right_range.n2p(1), DOWN)

        self.play(
            Write(left_range),
            Write(right_range),
            run_time=1
        )
        self.play(
            FadeIn(left_ticker, shift=DOWN),
            FadeIn(right_ticker, shift=DOWN),
        )

        rect = SurroundingRectangle(examples[0])
        rect.set_opacity(0)

        prob = ValueTracker(0.5)
        left_ticker.add_updater(
            lambda m: m.move_to(left_range.n2p(prob.get_value()), DOWN)
        )
        right_ticker.add_updater(
            lambda m: m.move_to(right_range.n2p(
                prob.get_value() / (1 - prob.get_value())
            ), DOWN)
        )

        for i, p in enumerate([0.1, 0.2, 0.5, 0.8, 0.9]):
            self.play(
                prob.set_value, p,
                rect.become,
                SurroundingRectangle(examples[i]),
            )
            self.wait()
        self.play(
            FadeOut(rect),
            ApplyMethod(prob.set_value, 0.5, run_time=4),
        )
        self.wait()


class SnazzyBayesRuleSteps(Scene):
    def construct(self):
        # Add title
        title = TextMobject(
            "Bayes' rule, the snazzy way",
            font_size=72
        )
        title.to_edge(UP)
        title.set_stroke(BLACK, 2, background=True)
        underline = Underline(title)
        underline.scale(1.2)
        underline.shift(0.2 * UP)
        underline.set_stroke(GREY, 3)
        self.add(underline, title)
        self.play(ShowCreation(underline))

        # Step labels
        step_labels = VGroup(
            TextMobject("Step 1)"),
            TextMobject("Step 2)"),
            TextMobject("Step 3)"),
        )
        step_labels.arrange(DOWN, buff=1.5, aligned_edge=LEFT)
        step_labels.next_to(title, DOWN, MED_LARGE_BUFF)
        step_labels.to_edge(LEFT)

        self.play(
            LaggedStartMap(FadeIn, step_labels, scale=1.2)
        )

        # Step 1
        step1 = TextMobject("Express the prior with odds")
        step1.set_color(YELLOW)
        step1_subtext = TextMobject("E.g.", " 1\\% ", " $\\rightarrow$ ", "1:99")
        step1_subtext.set_color(GREY_A)
        step1_subtext.scale(0.9)
        step1.next_to(step_labels[0], RIGHT)
        step1_subtext.next_to(step1, DOWN, aligned_edge=LEFT)

        population = VGroup(*(
            WomanIcon()
            for x in range(100)
        ))
        population.arrange_in_grid(h_buff=1, v_buff=0.5, fill_rows_first=False)
        population.set_height(5)
        population.to_corner(DR)
        population[0].set_color(YELLOW)

        self.play(
            ShowIncreasingSubsets(population),
            Write(step1)
        )
        self.wait()
        step1_subtext.unlock_triangulation()
        self.play(FadeIn(step1_subtext[:2]))
        self.play(
            TransformFromCopy(step1_subtext[1], step1_subtext[3]),
            Write(step1_subtext[2]),
        )
        self.wait()

        # Step 2
        step2 = TextMobject("Compute Bayes' factor")
        step2.set_color(GREEN)
        step2.next_to(step_labels[1], RIGHT)

        bf_computation = TexMobject(
            """
            {
            P(+ \\, | \\, \\text{Cancer}) \\over
            P(+ \\, | \\, \\text{No cancer})
            } =
            {90\\% \\over 9\\%} = 10
            """,
            tex_to_color_map={
                "+": GREEN,
                "\\text{Cancer}": YELLOW,
                "\\text{No cancer}": GREY_B,
                "{90\\%": GREEN,
                "9\\%}": GREEN,
                "10": WHITE,
            }
        )
        bf_computation[-1].scale(1.2)
        bf_computation.scale(0.6)
        bf_computation.next_to(step2, DOWN, aligned_edge=LEFT)

        lr_words = TextMobject("``Likelihood ratio''", font_size=30)
        lr_words.next_to(bf_computation[-1], RIGHT, MED_LARGE_BUFF, DOWN)
        lr_words.set_color(GREY_A)

        self.play(Write(step2, run_time=1))
        self.play(FadeIn(bf_computation, lag_ratio=0.1))
        self.wait()
        self.play(Write(lr_words, run_time=1))
        self.wait()

        # Step 3
        step3 = TextMobject("Multiply")
        step3.set_color(BLUE)
        step3.next_to(step_labels[2], RIGHT)

        multiplication = TexMobject(
            "(1:99)", "\\times", "10",
            "=", "10:99",
            "\\rightarrow", "{10 \\over 109}",
            "\\approx", "{1 \\over 11}",
            font_size=36,
        )
        multiplication.next_to(step3, DOWN, aligned_edge=LEFT)
        multiplication.unlock_triangulation()

        self.play(
            Write(step3, run_time=1),
            FadeIn(multiplication[:3])
        )
        self.wait()
        self.play(
            FadeIn(multiplication.get_part_by_tex("=")),
            TransformFromCopy(
                multiplication.get_part_by_tex("1:99"),
                multiplication.get_part_by_tex("10:99"),
            ),
        )
        self.wait()
        self.play(
            FadeIn(multiplication.get_part_by_tex("\\rightarrow")),
            FadeIn(multiplication.get_part_by_tex("10 \\over 109")),
        )
        self.play(
            FadeIn(multiplication.get_part_by_tex("\\approx")),
            FadeIn(multiplication.get_part_by_tex("1 \\over 11")),
        )
        self.wait()

        # Alt example
        prior_odds = step1_subtext[1:]
        alt_prior_odds = TexMobject(
            "10\\%", "\\rightarrow", "\\text{1:9}"
        )
        alt_prior_odds.match_height(prior_odds)
        alt_prior_odds.move_to(prior_odds, LEFT)
        alt_prior_odds.match_style(prior_odds)

        self.play(
            FadeOut(multiplication),
            FadeOut(prior_odds, shift=UP),
            FadeIn(alt_prior_odds, shift=UP),
        )
        self.play(
            population[:10].set_color, YELLOW,
            LaggedStartMap(
                ShowCreationThenFadeOut,
                VGroup(*(
                    SurroundingRectangle(person, buff=0.05)
                    for person in population[:10]
                ))
            )
        )
        self.wait()

        new_multiplication = TexMobject(
            "(1:9)", "\\times", "10",
            "=", "10:9",
            "\\rightarrow", "{10 \\over 19}",
            "\\approx", "0.53",
            font_size=36,
        )
        new_multiplication.move_to(multiplication, LEFT)
        rects = VGroup(
            SurroundingRectangle(alt_prior_odds.get_part_by_tex("1:9")),
            SurroundingRectangle(bf_computation.get_part_by_tex("10")),
            SurroundingRectangle(new_multiplication.get_part_by_tex("10:9")),
        )
        rects.set_color(RED)

        self.play(
            FadeIn(rects[:2], lag_ratio=0.6, run_time=1.5)
        )
        self.wait()
        self.play(
            ReplacementTransform(rects[0], rects[2]),
            ReplacementTransform(rects[1], rects[2]),
            FadeIn(new_multiplication[:5]),
        )
        self.wait()
        self.play(
            FadeOut(rects[2]),
            FadeIn(new_multiplication[5:7]),
        )
        self.wait()
        self.play(Write(new_multiplication[7:]))
        self.wait()


class CompressedBayesFactorSteps(Scene):
    def construct(self):
        steps = TextMobject(
            "Step 1) ", "Express the prior with odds\\\\",
            "Step 2) ", "Compute the Bayes factor\\\\",
            "Step 3) ", "Multiply\\\\",
            alignment="",
        )
        steps[1].set_color(YELLOW)
        steps[3].set_color(GREEN)
        steps[5].set_color(BLUE)
        steps.set_width(FRAME_WIDTH - 2)

        self.add(steps)


class AskWhyItWorks(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Huh?  Why does\\\\that work?",
            target_mode="confused",
        )
        self.change_student_modes(
            "pondering", "erm", "confused",
            look_at_arg=self.screen,
        )
        self.play(self.teacher.change, "happy")
        self.wait(3)


class WhyTheBayesFactorTrickWorks(Scene):
    def construct(self):
        # Setup before and after
        titles = VGroup(
            TextMobject("Before test"),
            TextMobject("After test"),
        )
        titles.scale(1.25)
        for title, u in zip(titles, [-1, 1]):
            title.set_x(u * FRAME_WIDTH / 4)
            title.to_edge(UP, buff=MED_SMALL_BUFF)
        h_line = Line(LEFT, RIGHT)
        h_line.set_width(FRAME_WIDTH)
        h_line.next_to(titles, DOWN)
        h_line.set_x(0)
        v_line = Line(UP, DOWN).set_height(FRAME_HEIGHT)
        lines = VGroup(h_line, v_line)
        lines.set_stroke(GREY, 2)

        self.add(titles)
        self.add(lines)

        # Show population before
        population = VGroup(*(WomanIcon() for x in range(100)))
        population.arrange_in_grid(h_buff=0.7, fill_rows_first=False)
        population.set_height(5)
        population[:10].set_fill(YELLOW)
        population[:10].shift(MED_SMALL_BUFF * LEFT)
        population.match_x(titles[0])
        population.to_edge(DOWN, buff=MED_LARGE_BUFF)

        w_tex = "(\\text{\\# With})"
        wo_tex = "(\\text{\\# Without})"
        t2c = {
            w_tex: YELLOW,
            wo_tex: GREY_B,
        }
        odds = TexMobject(w_tex, ":", wo_tex, tex_to_color_map=t2c)
        odds.next_to(population, UP, buff=MED_LARGE_BUFF)
        odds.match_x(titles[0])

        self.add(population)
        self.add(odds)
        self.play(
            ShowCreationThenDestruction(Underline(odds[0])),
            LaggedStartMap(
                ShowCreationThenFadeOut,
                VGroup(*(
                    SurroundingRectangle(icon, stroke_width=1, buff=0.05)
                    for icon in population[:10]
                ))
            ),
        )
        self.play(
            ShowCreationThenDestruction(Underline(odds[2])),
            LaggedStartMap(
                ShowCreationThenFadeOut,
                VGroup(*(
                    SurroundingRectangle(icon, color=GREY, stroke_width=1, buff=0.05)
                    for icon in population[10:]
                )),
                lag_ratio=0.01
            ),
        )
        self.wait()

        # Turn odds into fraction
        frac = TexMobject(
            w_tex, "\\over", wo_tex, tex_to_color_map=t2c,
            font_size=36
        )
        frac.next_to(h_line, DOWN, MED_LARGE_BUFF)
        frac.match_x(titles[0])

        self.play(
            ReplacementTransform(odds, frac),
            population.set_height, 4.5,
            population.next_to, frac, DOWN, MED_LARGE_BUFF,
        )
        self.wait()

        # Show filtration
        pop_copy = population.copy()
        pop_copy.match_x(titles[1])

        tp_cases = pop_copy[:9]
        fn_cases = pop_copy[9:10]
        fp_cases = pop_copy[10::10]
        tn_cases = VGroup(*(
            case
            for case in pop_copy[10:]
            if case not in fp_cases
        ))

        VGroup(fn_cases, tn_cases).set_opacity(0.1)
        VGroup(tp_cases, tp_cases).set_stroke(GREEN, 3, background=True)

        pos_boxes = VGroup()
        for case in it.chain(tp_cases, fp_cases):
            box = SurroundingRectangle(case, buff=0.025)
            box.set_stroke(GREEN, 0)
            plus = TexMobject("+", font_size=24)
            plus.move_to(box.get_corner(UR))
            plus.shift(DR * plus.get_height() / 4)
            plus.set_color(GREEN)
            box.add(plus)
            pos_boxes.add(box)

        self.play(
            TransformFromCopy(population, pop_copy),
            path_arc=30 * DEGREES
        )
        self.play(LaggedStartMap(DrawBorderThenFill, pos_boxes))
        self.wait()

        # Final fraction
        t2c.update({
            "\\text{Cancer}": YELLOW,
            "\\text{No cancer}": GREY,
            "+": GREEN,
            "\\cdot": WHITE,
        })
        final_frac = TexMobject(
            w_tex, "\\cdot P(+ \\,|\\, \\text{Cancer})",
            "\\over",
            wo_tex, "\\cdot P(+ \\,|\\, \\text{No cancer})",
            tex_to_color_map=t2c,
            font_size=36,
        )
        final_frac.match_x(pop_copy)
        final_frac.match_y(frac)

        left_brace = Brace(tp_cases, LEFT)
        right_brace = Brace(fp_cases, RIGHT, min_num_quads=1)
        big_left_brace = Brace(VGroup(tp_cases, fn_cases), LEFT)
        big_right_brace = Brace(VGroup(fp_cases, tn_cases), RIGHT)
        big_left_brace.set_opacity(0)
        big_right_brace.set_opacity(0)

        self.play(*(
            TransformFromCopy(
                frac.get_part_by_tex(tex),
                final_frac.get_part_by_tex(tex)
            )
            for tex in (w_tex, "\\over")
        ))
        self.wait()
        self.play(
            TransformFromCopy(big_left_brace, left_brace),
            Write(final_frac[1:7])
        )
        self.wait()
        self.play(*(
            TransformFromCopy(
                frac.get_part_by_tex(tex),
                final_frac.get_part_by_tex(tex)
            )
            for tex in (wo_tex,)
        ))
        self.play(
            TransformFromCopy(big_right_brace, right_brace),
            Write(final_frac[9:])
        )
        self.wait()
        self.add(final_frac)

        # Circle likelihood ratio
        likelihood_ratio = VGroup(
            final_frac[2:7],
            final_frac[10:]
        )
        lr_rect = SurroundingRectangle(likelihood_ratio)
        lr_rect.set_stroke(BLUE, 3)

        self.play(ShowCreation(lr_rect))
        self.wait()


# Likely remove
class LanguageIssues(Scene):
    def construct(self):
        # Diagram
        prior = 0.05
        sensitivity = 0.9
        specificity = 0.91

        rects = VGroup(*[Square() for x in range(4)])
        rects[0::2].set_stroke(GREEN, 3)
        rects[1::2].set_stroke(RED, 3)
        rects.set_fill(GREY_D, 1)
        rects.set_height(6)
        rects.set_width(8, stretch=True)
        rects.center()

        rects[:2].stretch(prior, 0, about_edge=LEFT)
        rects[2:].stretch(1 - prior, 0, about_edge=RIGHT)
        rects[0].stretch(sensitivity, 1, about_edge=UP)
        rects[1].stretch(1 - sensitivity, 1, about_edge=DOWN)
        rects[2].stretch(1 - specificity, 1, about_edge=UP)
        rects[3].stretch(specificity, 1, about_edge=DOWN)

        icon = VGroup(WomanIcon())
        icon.add(SurroundingRectangle(icon, buff=0, stroke_width=3))
        icon_scale_factor = 0.1

        tp_icons = VGroup(*[icon.copy() for x in range(9)])
        tp_icons.set_fill(YELLOW)
        tp_icons.set_stroke(GREEN)
        tp_icons.arrange_in_grid()
        tp_icons.scale(icon_scale_factor)
        tp_icons.move_to(rects[0])

        fn_icons = VGroup(*[icon.copy() for x in range(1)])
        fn_icons.set_fill(YELLOW)
        fn_icons.set_stroke(RED)
        fn_icons.scale(icon_scale_factor)
        fn_icons.move_to(rects[1])

        fp_icons = VGroup(*[icon.copy() for x in range(89)])
        fp_icons.set_fill(GREY)
        fp_icons.set_stroke(GREEN)
        fp_icons.arrange_in_grid(2, 45)
        fp_icons.scale(icon_scale_factor)
        fp_icons.move_to(rects[2])

        tn_icons = VGroup(*[icon.copy() for x in range(900)])
        tn_icons.set_fill(GREY)
        tn_icons.set_stroke(RED)
        tn_icons.arrange_in_grid(n_cols=45)
        tn_icons.scale(icon_scale_factor)
        tn_icons.move_to(rects[3])

        tp_icons.align_to(fp_icons, UP)
        fn_icons.match_y(tn_icons)

        icon_groups = VGroup(tp_icons, fn_icons, fp_icons, tn_icons)

        labels = VGroup(
            TextMobject("9", " True\\\\positives", color=GREEN_B),
            TextMobject("1", " False\\\\negative", color=RED_D),
            TextMobject("89", " False\\\\positives", color=GREEN_D),
            TextMobject("900", " True\\\\negatives", color=RED_B),
        )
        for label, icons, u, v in zip(labels, icon_groups, [-1, -1, 1, 1], [1, -1, 1, -1]):
            label.next_to(icons, u * RIGHT, MED_SMALL_BUFF)

        diagram = VGroup(icon_groups, labels)
        diagram.center()

        for label, icons in zip(labels, icon_groups):
            self.play(
                ShowIncreasingSubsets(icons),
                FadeIn(label)
            )
            self.wait()

        # Question
        question = TextMobject("Is it an issue with language?", font_size=72)
        fpr_words = TextMobject("False positive rate", font_size=72)
        question.to_edge(UP)
        fpr_words.to_edge(UP)

        self.play(
            Write(question),
            diagram.set_height, 5,
            diagram.next_to, question, DOWN, LARGE_BUFF,
        )
        self.wait()

        fpr_words.save_state()
        fpr_words.replace(question, stretch=True)
        fpr_words.set_opacity(0)
        self.play(
            Restore(fpr_words),
            question.replace, fpr_words.saved_state, {"stretch": True},
            question.set_opacity, 0,
        )

        # Show fraction
        fraction = TexMobject(
            "=",
            "{\\text{False positives}",
            "\\over", "\\text{???}}"
        )
        fraction.set_color_by_tex("False positives", GREEN_D)

        fraction.next_to(fpr_words, RIGHT)
        fpr_words.generate_target()
        VGroup(fpr_words.target, fraction).center().to_edge(UP)
