from manimlib.imports import *


SICKLY_GREEN = "#9BBD37"


class WomanIcon(SVGMobject):
    CONFIG = {
        "fill_color": GREY_B,
        "stroke_width": 0,
    }

    def __init__(self, **kwargs):
        super().__init__("woman_icon", **kwargs)
        self.remove(self[0])


class PersonIcon(SVGMobject):
    CONFIG = {
        "fill_color": GREY_B,
        "stroke_width": 0,
    }

    def __init__(self, **kwargs):
        super().__init__("person", **kwargs)


class Population(VGroup):
    def __init__(self, count, **kwargs):
        super().__init__(**kwargs)
        icon = PersonIcon()
        self.add(*(icon.copy() for x in range(count)))
        self.arrange_in_grid()


def get_covid_clipboard(disease_name="SARS\\\\CoV-2", color=GREEN):
    clipboard = SVGMobject("clipboard")
    clipboard.set_stroke(width=0)
    clipboard.set_fill(interpolate_color(GREY_BROWN, WHITE, 0.5), 1)
    clipboard.set_width(2.5)

    result = TextMobject(
        "+\\\\",
        disease_name + "\\\\",
        "Detected"
    )
    result[0].scale(1.5, about_edge=DOWN)
    result[0].set_fill(color)
    result[0].set_stroke(color, 2)
    result[-1].set_fill(color)
    result.set_width(clipboard.get_width() * 0.7)
    result.move_to(clipboard)
    result.shift(0.2 * DOWN)
    clipboard.add(result)
    return clipboard


# Scenes
class MathAsDesign(Scene):
    def construct(self):
        # Setup
        design_word = TextMobject("Designed?", font_size=72)
        design_word.to_edge(UP)

        e_formula = TexMobject(
            "e", "^{\\pi", "i}", "=", "-1",
            font_size=96,
        )
        e_formula[1].set_color(GREY_B)
        e_formula[2].set_color(YELLOW)
        e_formula[4].set_color(BLUE)

        l_formula = TexMobject(
            "\\sum_{n = 0}^{\\infty} \\frac{(-1)^n}{2n + 1} = \\frac{\\pi}{4}",
            font_size=72,
        )

        buff = 1.5
        formulas = VGroup(e_formula, l_formula)
        formulas.arrange(DOWN, buff=buff)
        formulas.next_to(design_word, DOWN, buff=buff)

        original_ly = l_formula.get_y()
        l_formula.center()

        self.play(Write(l_formula, run_time=1))
        self.wait()
        self.play(FadeIn(design_word, 0.2 * UP, scale=1.1))
        self.wait()

        alt_l_formula = VGroup(
            VGroup(
                TexMobject("\\pm").set_height(0.8),
                TexMobject("k \\text{ odd}", font_size=36)
            ).arrange(DOWN, SMALL_BUFF),
            TexMobject("\\frac{1}{k}"),
            TexMobject("="),
            VGroup(
                Sector(
                    angle=PI / 2,
                    fill_color=BLUE,
                    fill_opacity=1,
                    stroke_color=WHITE,
                    stroke_width=2,
                ),
                Sector(
                    start_angle=PI / 2, angle=3 * PI / 2,
                    fill_color=GREY_E,
                    fill_opacity=1,
                    stroke_color=WHITE,
                    stroke_width=2,
                ),
            ).set_height(1)
        )
        alt_l_formula.arrange(RIGHT)
        alt_l_formula.match_height(l_formula)
        alt_l_formula.next_to(l_formula.get_center(), RIGHT, LARGE_BUFF)

        self.play(
            l_formula.next_to, l_formula.get_center(), LEFT, LARGE_BUFF,
            FadeIn(alt_l_formula, shift=2 * RIGHT)
        )
        self.wait(2)

        # Euler's formula
        e_formula.next_to(e_formula.get_y() * UP, LEFT, buff=1.5)
        self.play(
            l_formula.scale, 0.7,
            l_formula.set_y, original_ly,
            alt_l_formula.scale, 0.7,
            alt_l_formula.set_y, original_ly,
            FadeIn(e_formula, scale=1.1)
        )

        alt_e_formula = VGroup(
            TextMobject("exp", font_size=96),
            TexMobject("(", font_size=96),
            Arrow(0.5 * RIGHT, 0.5 * LEFT, path_arc=PI, buff=0, color=GREY_B),
            Dot(radius=0.05, color=WHITE),
            Vector(0.75 * UP, fill_color=YELLOW),
            TexMobject(")", font_size=96),
            TexMobject("=", font_size=96),
            Vector(LEFT, fill_color=BLUE),
        )
        alt_e_formula.arrange(RIGHT, buff=MED_SMALL_BUFF)
        alt_e_formula[0].shift(0.15 * RIGHT)
        alt_e_formula[4:].shift(0.15 * LEFT)
        alt_e_formula.scale(0.8)
        alt_e_formula.next_to(e_formula.get_y() * UP, RIGHT, buff=1.0)
        alt_e_formula.shift(0.2 * DOWN)

        anims = []
        for i, j in enumerate([0, 2, 4, 6, 7]):
            src = e_formula[i].copy()
            dst = alt_e_formula[j]
            src.generate_target()
            src.target.replace(dst, stretch=True)
            src.target.set_opacity(0)
            dst.save_state()
            dst.replace(src, stretch=True)
            dst.set_opacity(0)
            anims.append(MoveToTarget(src, remover=True))
            anims.append(Restore(dst))
        anims.extend([
            FadeIn(alt_e_formula[1], shift=0.5 * UP, scale=3),
            FadeIn(alt_e_formula[5], shift=0.5 * UP, scale=3),
            GrowFromPoint(alt_e_formula[3], e_formula[1:3].get_center()),
        ])

        self.play(*anims)
        self.wait()


class BayesRuleAndMedicalTests(Scene):
    def construct(self):
        # Add title
        title = TextMobject("Bayes' rule", font_size=72)
        title.to_edge(UP)
        h_line = Underline(title)
        h_line.scale(1.5)
        h_line.set_stroke(GREY_B, 2)

        self.add(title)
        self.wait()

        # Show rule
        formula = TexMobject(
            "P(H|E) = {P(H)P(E|H) \\over P(E)}",
            tex_to_color_map={
                "H": YELLOW,
                "E": BLUE,
            },
            font_size=60
        )

        h_part = formula.get_part_by_tex("H")
        hyp_word = TextMobject("Hypothesis", color=YELLOW)
        hyp_word.next_to(h_part, UP, LARGE_BUFF)
        hyp_arrow = Arrow(hyp_word.get_bottom(), h_part.get_top(), buff=0.1)

        e_part = formula.get_part_by_tex("E")
        ev_word = TextMobject("Evidence", color=BLUE)
        ev_word.next_to(e_part, DOWN, LARGE_BUFF)
        ev_arrow = Arrow(ev_word.get_top(), e_part.get_bottom(), buff=0.1)

        self.play(
            ShowCreation(h_line),
            FadeIn(formula, scale=1.1),
        )
        self.play(
            LaggedStart(
                FadeIn(hyp_word, shift=0.25 * UP, scale=1.1),
                FadeIn(ev_word, shift=0.25 * DOWN, scale=1.1),
            ),
            LaggedStart(
                GrowArrow(hyp_arrow),
                GrowArrow(ev_arrow),
            ),
        )
        self.wait()
        formula_annoations = VGroup(hyp_word, hyp_arrow, ev_word, ev_arrow)

        # Randys
        pis = VGroup(Randolph(), Randolph())
        pis.set_height(2)
        pis[1].flip()
        pis[1].set_color(TEAL_E)
        pis.arrange(RIGHT, buff=5)
        pis.to_corner(DL)

        self.play(
            VFadeIn(pis[0]),
            pis[0].change, "hooray", formula
        )
        self.play(Blink(pis[0]))
        self.play(
            VFadeIn(pis[1]),
            pis[1].change, "maybe", formula
        )
        self.play(Blink(pis[1]))
        self.wait()

        # Sweep aside
        title.add(h_line)
        formula.generate_target()
        formula.target.scale(0.6)
        formula.target.to_corner(DR)

        self.play(
            VFadeOut(formula_annoations),
            MaintainPositionRelativeTo(formula_annoations, formula),
            MoveToTarget(formula),
            title.scale, 0.7,
            title.next_to, formula.target, UP,
            FadeOut(pis, DOWN),
        )

        # Mention paradox
        paradox_name = TextMobject("Medical Test Paradox")
        paradox_name.to_corner(UL)
        paradox_name.shift(MED_SMALL_BUFF * DOWN)
        paradox_line = Underline(paradox_name)
        paradox_line.set_stroke(GREY_B, 2)

        self.play(
            FadeIn(paradox_name, lag_ratio=0.1),
            ShowCreation(paradox_line),
        )
        self.wait()

        # Show high accuracy
        accuracy_words = TextMobject("High accuracy")
        accuracy_words.next_to(paradox_line, DOWN, MED_LARGE_BUFF)
        accuracy_words.set_color(GREEN)

        population = Population(100)
        population.arrange_in_grid(buff=LARGE_BUFF)
        population.set_height(5)
        population.next_to(accuracy_words, DOWN)

        marks = VGroup()
        for icon in population:
            icon.generate_target()
            if random.random() < 0.05:
                mark = Exmark()
                icon.target.set_opacity(0.5)
            else:
                mark = Checkmark()
            mark.set_height(icon.get_height() / 2)
            mark.move_to(icon.get_corner(UL))
            marks.add(mark)

        self.play(
            FadeIn(accuracy_words),
            FadeIn(population, lag_ratio=0.01)
        )
        self.play(
            ShowIncreasingSubsets(marks, run_time=2),
            LaggedStartMap(MoveToTarget, population, run_time=2),
        )
        self.wait()

        # Show test result
        randy = Randolph(height=2)
        randy.move_to(DOWN)
        clipboard = get_covid_clipboard("Virus", color=YELLOW)
        clipboard.set_height(2)
        clipboard.next_to(randy.get_corner(UR), RIGHT)

        self.play(
            VFadeIn(randy),
            randy.change, "guilty", clipboard,
            FadeIn(clipboard, shift=0.25 * UL, scale=1.5)
        )
        self.play(randy.change, "horrified", clipboard)
        self.play(Blink(randy))
        self.wait()

        # Show low predictive value
        prob_expression = TexMobject(
            "P(\\text{Sick} | +) = ",
            tex_to_color_map={
                "+": YELLOW,
                "\\text{Sick}": GREY_A,
            }
        )
        prob = DecimalNumber(0.9, font_size=60)
        prob.next_to(prob_expression, RIGHT)
        prob.set_color(WHITE)
        prob.set_opacity(0)
        prob_expression.add(prob)
        p_line = Underline(prob)
        p_line.shift(0.1 * DOWN)
        p_line.scale(1.5)
        p_line.set_stroke(WHITE, 2)
        prob_expression.add(p_line)
        prob_expression.next_to(VGroup(randy, clipboard), UP)

        self.play(
            FadeIn(prob_expression),
            randy.change, "pondering", prob_expression
        )
        self.play(
            ChangeDecimalToValue(prob, 0.09),
            UpdateFromAlphaFunc(prob, lambda m, a: m.set_opacity(a)),
            run_time=2
        )
        self.play(Blink(randy))
        self.play(
            randy.change, "confused", prob,
            ChangeDecimalToValue(prob, 0.01),
        )
        self.play(Blink(randy))
        self.wait()

        # Get rid of medical test stuff

        # Mention Bayes factors

        self.embed()


class SamplePopulationBreastCancer(Scene):
    def construct(self):
        # Introduce population
        title = TextMobject(
            "Sample of ", "$1{,}000$", " women",
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
            run_time=5
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

        negative_words = TextMobject(r"99\% ", "Do not have cancer", font_size=36)
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

        # Show screening
        scan_lines = VGroup(*(
            Line(
                # FRAME_WIDTH * LEFT / 2,
                FRAME_HEIGHT * DOWN / 2,
                icon.get_center(),
                stroke_width=1,
                stroke_color=interpolate_color(BLUE, GREEN, random.random())
            )
            for icon in population
        ))
        self.play(
            LaggedStartMap(
                ShowCreationThenFadeOut, scan_lines,
                lag_ratio=1 / len(scan_lines),
                run_time=3,
            )
        )
        self.wait()

        # Test results on cancer population
        tpr_words = TextMobject("9 True positives", font_size=36)
        fnr_words = TextMobject("1 False negative", font_size=36)
        tnr_words = TextMobject("901 True negatives", font_size=36)
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

        # Test results on cancer-free population
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

        fpr_words.next_to(fp_cases, UP, buff=SMALL_BUFF)
        tnr_words.next_to(tn_cases, DOWN, buff=0.2)

        self.play(
            FadeIn(fpr_words, shift=0.2 * UP),
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

        # Limit view to positive cases
        for cases, nr, rect in zip([tp_cases, fp_cases], [3, 7], rects):
            cases.save_state()
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
        positive_words.save_state()
        negative_words.save_state()
        tpr_words.save_state()
        fpr_words.save_state()

        self.play(
            MoveToTarget(tp_cases),
            MoveToTarget(fp_cases),
            tpr_words.next_to, tp_cases.target, UP,
            fpr_words.next_to, fp_cases.target, UP,
            FadeOut(signs),
            positive_words[0].set_opacity, 0,
            negative_words[0].set_opacity, 0,
            positive_words[1].match_x, rects[0],
            negative_words[1].match_x, rects[1],
            LaggedStart(
                FadeOut(fn_cases, shift=DOWN),
                FadeOut(fnr_words, shift=DOWN),
                FadeOut(tn_cases, shift=DOWN),
                FadeOut(tnr_words, shift=DOWN),
            ),
        )
        self.wait()

        # Emphasize groups counts
        self.play(
            ShowCreationThenFadeOut(SurroundingRectangle(
                tpr_words[0][:1],
                stroke_width=2,
                stroke_color=WHITE,
                buff=0.05,
            )),
            LaggedStartMap(Indicate, tp_cases, color=YELLOW, lag_ratio=0.3, run_time=1),
        )
        self.wait()
        self.play(
            ShowCreationThenFadeOut(SurroundingRectangle(
                fpr_words[0][:2],
                stroke_width=2,
                stroke_color=WHITE,
                buff=0.05,
            )),
            LaggedStartMap(
                Indicate, fp_cases,
                color=GREEN_A,
                lag_ratio=0.05,
                run_time=3
            )
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

        # Label PPV
        frame = self.camera.frame
        frame.save_state()

        ppv_words = TextMobject(
            "Positive\\\\",
            "Predictive\\\\",
            "Value\\\\",
            alignment="",
        )
        ppv_words.next_to(equation, RIGHT, LARGE_BUFF, DOWN)
        for word in ppv_words:
            word[0].set_color(BLUE)

        ppv_rhs = TexMobject(
            "={\\text{TP} \\over \\text{TP} + \\text{FP}}",
            tex_to_color_map={
                "\\text{TP}": GREEN_B,
                "\\text{FP}": GREEN_C,
            }
        )
        ppv_rhs.next_to(ppv_words, RIGHT)
        ppv_rhs.shift(1.5 * LEFT)

        self.play(frame.scale, 1.1, {"about_edge": DL})
        self.play(ShowIncreasingSubsets(ppv_words))
        self.wait()

        self.play(
            equation.shift, 1.5 * LEFT + 0.5 * UP,
            ppv_words.shift, 1.5 * LEFT,
            FadeIn(ppv_rhs, lag_ratio=0.1),
            frame.scale, 1.1, {"about_edge": DL},
        )
        self.wait()

        # Go back to earlier state
        self.play(
            frame.restore,
            frame.shift, 0.5 * DOWN,
            LaggedStartMap(FadeOut, VGroup(equation, ppv_words, ppv_rhs)),
            LaggedStartMap(Restore, VGroup(
                tpr_words, tp_cases,
                fpr_words, fp_cases,
            )),
            run_time=3,
        )
        self.play(
            LaggedStartMap(FadeIn, VGroup(
                fnr_words, fn_cases,
                tnr_words, tn_cases,
            )),
        )
        self.wait()

        # Fade rects
        fade_rects = VGroup(*(
            BackgroundRectangle(
                VGroup(rect, words),
                fill_opacity=0.9,
                fill_color=BLACK,
                buff=SMALL_BUFF,
            )
            for rect, words in zip(rects, [positive_words, negative_words])
        ))

        # Sensitivity
        sens_eq = TexMobject(
            "\\text{Sensitivity}",
            "= {9 \\over 10}",
            "= 90\\%"
        )
        sens_eq.next_to(rects[0], LEFT, MED_LARGE_BUFF, aligned_edge=UP)
        sens_eq.shift(DOWN)

        fnr_eq = TexMobject(
            "\\text{False Negative Rate}", "= 10\\%"
        )
        fnr_eq.set_color(RED)
        fnr_eq.scale(0.9)
        equiv = TexMobject("\\Leftrightarrow")
        equiv.scale(1.5)
        equiv.rotate(90 * DEGREES)
        equiv.next_to(sens_eq, DOWN, MED_LARGE_BUFF)
        fnr_eq.next_to(equiv, DOWN, MED_LARGE_BUFF)

        self.play(
            frame.shift, 5 * LEFT,
            FadeIn(fade_rects[1]),
            Write(sens_eq[0]),
        )
        self.wait()
        self.play(
            TransformFromCopy(tpr_words[0][0], sens_eq[1][1]),
            Write(sens_eq[1][0]),
            Write(sens_eq[1][2:]),
        )
        self.play(Write(sens_eq[2]))
        self.wait()

        self.play(
            FadeIn(equiv, shift=0.5 * DOWN),
            FadeIn(fnr_eq, shift=1.0 * DOWN),
        )
        self.wait()

        # Transition to right side
        fade_rects[0].stretch(5, 0, about_edge=RIGHT)
        self.play(
            ApplyMethod(frame.shift, 10 * RIGHT, run_time=4),
            FadeIn(fade_rects[0], run_time=2),
            FadeOut(fade_rects[1], run_time=2),
        )

        # Specificity
        spec_eq = TexMobject(
            "\\text{Specificity}",
            "= {901 \\over 990}",
            "\\approx 91\\%"
        )
        spec_eq.next_to(rects[1], RIGHT, MED_LARGE_BUFF, aligned_edge=DOWN)
        spec_eq.shift(UP)

        fpr_eq = TexMobject(
            "\\text{False Positive Rate}", "= 9\\%"
        )
        fpr_eq.set_color(GREEN)
        fpr_eq.scale(0.9)
        equiv2 = TexMobject("\\Leftrightarrow")
        equiv2.scale(1.5)
        equiv2.rotate(90 * DEGREES)
        equiv2.next_to(spec_eq, UP, MED_LARGE_BUFF)
        fpr_eq.next_to(equiv2, UP, MED_LARGE_BUFF)

        self.play(Write(spec_eq[0]))
        self.wait()
        self.play(
            Write(spec_eq[1][0]),
            TransformFromCopy(
                tnr_words[0][:3],
                spec_eq[1][1:4],
                run_time=2,
                path_arc=30 * DEGREES,
            ),
            Write(spec_eq[1][4:]),
        )
        self.wait()
        self.play(Write(spec_eq[2]))
        self.wait()

        self.play(
            FadeIn(equiv2, shift=0.5 * UP),
            FadeIn(fpr_eq, shift=1.0 * UP),
        )
        self.wait()

        # Reset to show both kinds of accuracy
        eqs = [sens_eq, spec_eq]
        for eq, word in zip(eqs, [positive_words, negative_words]):
            eq.generate_target()
            eq.target[1].set_opacity(0)
            eq.target[2].move_to(eq.target[1], LEFT),
            eq.target.next_to(word, UP, buff=0.3)

        self.play(
            FadeOut(fade_rects[0]),
            frame.shift, 5 * LEFT,
            frame.scale, 1.1, {"about_edge": DOWN},
            MoveToTarget(sens_eq),
            MoveToTarget(spec_eq),
            *map(FadeOut, (fnr_eq, fpr_eq, equiv, equiv2)),
            run_time=2,
        )
        self.wait()

        self.play(
            VGroup(
                fn_cases, fnr_words,
                fp_cases, fpr_words,
            ).set_opacity, 0.2,
            rate_func=there_and_back_with_pause,
            run_time=3
        )


class AskWhatTheParadoxIs(TeacherStudentsScene):
    def construct(self):
        # Image
        image = ImageMobject("ppv_image")
        image.replace(self.screen)
        image.set_opacity(0)
        outline = SurroundingRectangle(image, buff=0)
        outline.set_stroke(WHITE, 2)
        outline.set_fill(BLACK, 1)
        image = Group(outline, image)
        image.set_height(3.5, about_edge=UL)

        # What's the paradox?
        self.add(image)
        self.student_says(
            "How's that\\\\a paradox?",
            target_mode="sassy",
            look_at_arg=self.teacher.eyes,
            student_index=2,
            added_anims=[
                self.students[0].change, "pondering", image,
                self.students[1].change, "pondering", image,
            ]
        )
        self.play(self.teacher.change, 'guilty')
        self.wait(3)

        # Consider test accuracy
        self.teacher_says(
            "Consider the\\\\", "test accuracy"
        )
        self.wait(3)

        # Test accuracy split
        lower_words = self.teacher.bubble.content[1].copy()
        lower_words.unlock_triangulation()

        top_words = TextMobject("Test Accuracy", font_size=72)
        top_words.to_corner(UR)
        top_words.shift(LEFT)

        sens_spec = VGroup(
            TextMobject("Sensitivity", color=YELLOW),
            TextMobject("Specificity", color=BLUE_D),
        )
        sens_spec.scale(1)
        sens_spec.arrange(RIGHT, buff=1.0)
        sens_spec.next_to(top_words, DOWN, LARGE_BUFF)
        lines = VGroup(*(
            Line(top_words.get_bottom(), word.get_top(), buff=0.1, color=word.get_color())
            for word in sens_spec
        ))

        globals()['top_words'] = top_words
        self.play(
            TransformFromCopy(lower_words, top_words[0]),
            RemovePiCreatureBubble(
                self.teacher, target_mode="raise_right_hand",
                look_at_arg=top_words,
            ),
            *(ApplyMethod(pi.look_at, top_words) for pi in self.students)
        )
        self.play(
            LaggedStartMap(ShowCreation, lines),
            LaggedStart(*(
                FadeIn(word, shift=word.get_center() - top_words.get_center())
                for word in sens_spec
            )),
            run_time=1,
        )
        self.wait(4)


class MedicalTestsMatter(Scene):
    def construct(self):
        randy = Randolph(height=3)
        randy.to_corner(DL)
        randy.shift(2 * RIGHT)

        clipboard = get_covid_clipboard()
        clipboard.next_to(randy, RIGHT)
        clipboard.set_y(0)

        clipboard_words = VGroup(
            TexMobject("-", color=RED),
            TextMobject("SARS\\\\CoV-2"),
            TextMobject("Not Detected", color=RED),
        )
        for m1, m2 in zip(clipboard_words, clipboard[2]):
            m1.replace(m2, 0)

        clipboard.remove(clipboard[2])

        self.add(randy)
        self.play(
            FadeIn(clipboard, shift=LEFT),
            randy.change, 'guilty'
        )
        self.play(
            Write(clipboard_words),
            randy.change, "hooray", clipboard,
        )
        self.play(Blink(randy))

        question = TextMobject("What does\\\\really this mean?")
        question.next_to(clipboard, RIGHT, buff=1.5)
        question.shift(1.5 * UP)
        q_arrow = Arrow(
            question.get_bottom(), clipboard.get_right(),
            path_arc=-30 * DEGREES,
            buff=0.3,
        )

        self.play(
            FadeIn(question, shift=0.25 * UP),
            DrawBorderThenFill(q_arrow),
            randy.change, "confused",
        )
        self.play(randy.look_at, clipboard.get_top())
        self.play(Blink(randy))
        self.play(randy.look_at, clipboard.get_center())
        self.wait(3)


class GigerenzerSession(Scene):
    def construct(self):
        # Gigerenzer intro
        years = TextMobject("2006-2007", font_size=72)
        years.to_edge(UP)

        image = ImageMobject("Gerd_Gigerenzer")
        image.set_height(4)
        image.flip()
        name = TextMobject("Gerd Gigerenzer", font_size=72)
        name.next_to(image, DOWN)
        image_group = Group(image, name)

        self.play(FadeIn(years, shift=0.5 * UP))
        self.wait()
        self.play(
            FadeIn(image),
            Write(name)
        )
        self.wait()

        # Seminar words
        title = TextMobject("Statistics Seminar", font_size=72)
        title.to_edge(UP)

        title_underline = Underline(title, buff=SMALL_BUFF)
        title_underline.scale(1.1)
        title_underline.set_stroke(LIGHT_GREY)

        self.play(
            FadeIn(title, shift=0.5 * UP),
            FadeOut(years, shift=0.5 * UP),
        )
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
            image_group.scale, 0.75,
            image_group.to_corner, DR,
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
        self.wait()
        self.play(ShowCreationThenFadeOut(no_symptoms_underline))
        self.wait()
        self.play(
            FadeIn(prompt[1], lag_ratio=0.01),
            prompt[0].set_opacity, 0.5,
        )
        self.play(
            FadeIn(clipboard, shift=0.5 * UP, scale=1.1),
            image_group.scale, 0.75, {"about_edge": DR},
        )
        self.wait()

        self.play(
            FadeIn(prompt[2], lag_ratio=0.01),
            prompt[1].set_opacity, 0.5,
            clipboard.scale, 0.7, {"about_edge": DOWN},
        )
        self.wait()

        # Push prompt lower
        prompt.generate_target()
        prompt.target.set_opacity(0.8)
        prompt.target.replace(image_group, 0)
        prompt.target.scale(1.5, about_edge=RIGHT)

        h_line = DashedLine(FRAME_WIDTH * LEFT / 2, FRAME_WIDTH * RIGHT / 2)
        h_line.set_stroke(GREY_C)
        h_line.next_to(clipboard, UP)
        h_line.set_x(0)

        self.play(
            FadeOut(title, shift=UP),
            MoveToTarget(prompt),
            ShowCreation(h_line),
            FadeOut(image_group, shift=DR),
            clipboard.shift, 0.5 * LEFT,
        )

        # Test statistics
        stats = VGroup(
            TextMobject("Prevalence: ", "1\\%"),
            TextMobject("Sensitivity: ", "90\\%"),
            TextMobject("Specificity: ", "91\\%"),
        )
        stats.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        stats.to_corner(UL, buff=LARGE_BUFF)
        colors = [YELLOW, GREEN_B, GREY_B]
        for stat, color in zip(stats, colors):
            stat[0].set_color(color)
            stat[1].align_to(stats[0][1], LEFT)

        for stat in stats:
            self.play(FadeIn(stat[0], shift=0.25 * UP))
            self.play(Write(stat[1]))
            self.wait()
        self.wait()

        # Show randy knowing the answer
        randy = Randolph(height=2)
        randy.flip()
        randy.next_to(h_line, UP)
        randy.to_edge(RIGHT)

        bubble = randy.get_bubble(
            height=2,
            width=2,
        )
        bubble.shift(0.2 * LEFT)
        bubble.write("$\\frac{1}{11}$")

        self.play(FadeIn(randy))
        self.play(
            randy.change, "thinking",
            ShowCreation(bubble),
            Write(bubble.content),
        )
        self.play(Blink(randy))
        self.wait()

        # Show population
        dot = Dot()
        globals()['dot'] = dot
        dots = VGroup(*(dot.copy() for x in range(1000)))
        dots.arrange_in_grid(25, 40, buff=SMALL_BUFF)
        dots.set_height(4)
        dots.to_corner(UR)
        dots.set_fill(GREY_D)
        VGroup(*random.sample(list(dots), 10)).set_fill(YELLOW)

        cross = Cross(dots)
        cross.set_stroke(RED, 30)

        self.play(
            LaggedStartMap(FadeOut, VGroup(randy, bubble, bubble.content)),
            ShowIncreasingSubsets(dots, run_time=2)
        )
        self.wait()
        self.play(ShowCreation(cross))
        self.play(FadeOut(dots), FadeOut(cross))
        self.wait()
        self.play(LaggedStart(*(
            ShowCreationThenFadeOut(SurroundingRectangle(
                stat[1], color=stat[0].get_color()
            ))
            for stat in stats
        )))

        # Ask question
        question = TextMobject(
            "How many women who test positive\\\\actually have breast cancer?",
            font_size=36
        )
        question.to_corner(UR)
        question.shift(LEFT)

        self.play(FadeIn(question, lag_ratio=0.1))

        choices = VGroup(
            TextMobject("A) 9 in 10"),
            TextMobject("B) 8 in 10"),
            TextMobject("C) 1 in 10"),
            TextMobject("D) 1 in 100"),
        )
        choices.arrange_in_grid(2, 2, h_buff=1.0, v_buff=0.5, aligned_edge=LEFT)
        choices.next_to(question, DOWN, buff=0.75)
        choices.set_fill(GREY_A)

        self.play(LaggedStart(*(
            FadeIn(choice, scale=1.2)
            for choice in choices
        ), lag_ratio=0.3))
        self.wait()

        # Comment on choices
        a_rect = SurroundingRectangle(choices[0])
        a_rect.set_color(BLUE)
        q_mark = TexMobject("?")
        q_mark.match_height(a_rect)
        q_mark.next_to(a_rect, LEFT)
        q_mark.match_color(a_rect)
        q_mark2 = q_mark.copy()
        q_mark2.move_to(doctors, UR)

        c_rect = SurroundingRectangle(choices[2])
        c_rect.set_color(GREEN)
        checkmark = Checkmark().next_to(c_rect, LEFT)

        self.play(
            ShowCreation(a_rect),
            Write(q_mark2)
        )
        self.play(TransformFromCopy(q_mark2, q_mark))
        self.wait()

        # One fifth of doctors
        curr_doc_group = Group(
            doctors,
            clipboard,
            doctors_label,
            q_mark2,
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
        new_doctors.set_height(2.75)
        new_doctors.move_to(doctors, UP)

        marks = VGroup()
        for n, doc in enumerate(new_doctors):
            mark = Checkmark() if n == 0 else Exmark()
            mark.move_to(doc.get_corner(UL))
            mark.shift(SMALL_BUFF * DR)
            marks.add(mark)

        new_doctors[0].set_color(GREEN)

        self.play(
            LaggedStartMap(FadeOut, curr_doc_group, scale=0.5, run_time=1),
            FadeIn(new_doctors, lag_ratio=0.1)
        )
        self.play(
            ReplacementTransform(a_rect, c_rect),
            FadeOut(q_mark),
            Write(checkmark)
        )
        self.wait()


class OldGigerenzerMaterial(Scene):
    def construct(self):
        # Test sensitivity
        prompt.generate_target()
        prompt.target.set_opacity(0.8)
        prompt.target.match_height(clipboard)
        prompt.target.scale(0.65)
        prompt.target.next_to(clipboard, RIGHT, MED_LARGE_BUFF)

        sensitivity_words = TexMobject("90", "\\%", "\\text{ Sensitivity}")
        sensitivity_words.to_edge(UP)

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


class AskIfItsAParadox(TeacherStudentsScene):
    def construct(self):
        # Add fact
        stats = VGroup(
            TextMobject("Sensitivity: ", "90\\%"),
            TextMobject("Specificity: ", "91\\%"),
            TextMobject("Prevalence: ", "1\\%"),
        )
        stats.arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        for stat, color in zip(stats, [GREEN_B, GREY_B, YELLOW]):
            stat[0].set_color(color)
            stat[1].align_to(stats[0][1], LEFT)

        brace = Brace(stats, UP)
        prob = TexMobject(
            "P(\\text{Cancer} \\,|\\, +) \\approx \\frac{1}{11}",
            tex_to_color_map={
                "\\text{Cancer}": YELLOW,
                "+": GREEN,
            }
        )
        prob.next_to(brace, UP, buff=SMALL_BUFF)

        fact = VGroup(stats, brace, prob)
        fact.to_corner(UL)

        box = SurroundingRectangle(fact, buff=MED_SMALL_BUFF)
        box.set_fill(BLACK, 0.5)
        box.set_stroke(WHITE, 2)
        fact.add_to_back(box)
        fact.to_edge(UP, buff=SMALL_BUFF)

        self.add(fact)

        # Commentary
        self.student_says(
            "I'm sorry, is that\\\\a paradox?",
            target_mode="sassy",
            student_index=1
        )
        self.change_student_modes(
            "angry", "sassy", "angry",
            added_anims=[self.teacher.change, "guilty"]
        )
        self.wait(2)

        p_triangle = SVGMobject("PenroseTriangle")
        p_triangle.remove(p_triangle[0])
        p_triangle.set_fill(opacity=0)
        p_triangle.set_stroke(GREY_B, 3)
        p_triangle.set_gloss(1)
        p_triangle.set_height(3)
        p_triangle.next_to(self.students[2].get_corner(UR), UP)
        p_triangle = CurvesAsSubmobjects(p_triangle[0])

        self.play(
            self.students[0].change, "thinking", p_triangle,
            RemovePiCreatureBubble(
                self.students[1], target_mode="tease", look_at_arg=p_triangle,
            ),
            self.students[2].change, "raise_right_hand", p_triangle,
            self.teacher.change, "tease", p_triangle,
            ShowCreation(p_triangle, run_time=2, lag_ratio=0.01),
        )
        self.wait(3)

        # Veridical paradox
        v_paradox = TextMobject("``Veridical paradox''", font_size=72)
        v_paradox.move_to(self.hold_up_spot, DOWN)
        v_paradox.to_edge(UP)
        v_paradox.shift(0.5 * LEFT)
        vp_line = Underline(v_paradox)

        self.play(
            FadeIn(v_paradox, shift=UP),
            self.get_student_changes(*3 * ["pondering"], look_at_arg=v_paradox),
            FadeOut(p_triangle, shift=UP),
            self.teacher.change, "raise_right_hand", v_paradox
        )
        self.play(ShowCreation(vp_line))
        self.wait()

        definition = TextMobject(
            "- Provably true\\\\",
            "- Seems false",
            alignment="",
        )
        definition.next_to(v_paradox, DOWN, MED_LARGE_BUFF, aligned_edge=LEFT)

        for part in definition:
            self.play(FadeIn(part, shift=0.25 * RIGHT))
            self.wait()
        self.wait(5)


class GoalsOfEstimation(TeacherStudentsScene):
    def construct(self):
        # Goal
        goal = TextMobject("Goal: Quick estimations")
        goal.to_edge(UP)
        goal_line = Underline(goal)

        self.look_at(goal, added_anims=[FadeIn(goal, shift=0.5 * UP)])
        self.play(
            ShowCreation(goal_line),
            self.get_student_changes(
                *3 * ["pondering"],
                look_at_arg=goal_line,
            )
        )
        self.wait()

        # Generators
        def generate_stats(prev, sens, spec, bottom=self.hold_up_spot):
            stats = VGroup(
                TextMobject("Prevalence: ", f"{prev}\\%"),
                TextMobject("Sensitivity: ", f"{sens}\\%"),
                TextMobject("Specificity: ", f"{spec}\\%"),
            )
            stats.arrange(DOWN, buff=0.25, aligned_edge=LEFT)
            for stat, color in zip(stats, [YELLOW, GREEN_B, GREY_B]):
                stat[0].set_color(color)
                stat[1].align_to(stats[0][1], LEFT)

            rect = SurroundingRectangle(stats, buff=0.2)
            rect.set_fill(BLACK, 1)
            rect.set_stroke(GREY_B, 2)
            stats.add_to_back(rect)
            stats.move_to(bottom, DOWN)
            return stats

        def generate_answer(ans_tex):
            return TexMobject(
                "P(\\text{Cancer} \\,|\\, {+})", ans_tex,
                tex_to_color_map={
                    "\\text{Cancer}": YELLOW,
                    "{+}": GREEN,
                }
            )

        stats = [
            generate_stats(1, 90, 91),
            generate_stats(10, 90, 91),
            generate_stats(0.1, 90, 91),
            generate_stats(1, 90, 99),
        ]

        # Question and answer
        self.teacher_holds_up(stats[0])
        self.wait()
        self.student_says(
            generate_answer("\\approx \\frac{1}{11}"),
            target_mode="hooray",
            student_index=0,
            run_time=1,
        )
        self.wait(3)

        stats[1].to_edge(RIGHT)
        self.play(
            FadeOut(stats[0]),
            self.teacher.change, "raise_left_hand", stats[1],
            FadeIn(stats[1], shift=0.5 * UP),
            RemovePiCreatureBubble(self.students[0]),
        )
        self.play(ShowCreationThenFadeAround(stats[1][1][1]))
        self.change_student_modes(
            "pondering", "thinking", "confused",
            look_at_arg=stats[1]
        )
        self.wait()

        self.student_says(
            generate_answer("\\text{ is} \\\\ \\text{a little over } 50\\%"),
            bubble_kwargs={"width": 4, "height": 3},
            student_index=1,
            target_mode="speaking",
            run_time=1,
            added_anims=[
                self.students[2].change, "erm", goal,
                self.teacher.change, "happy", self.students[1].eyes,
            ]
        )
        self.wait(2)

        self.play(
            FadeOut(stats[1], 0.5 * UP),
            FadeIn(stats[2], 0.5 * UP),
            RemovePiCreatureBubble(self.students[1]),
            self.teacher.change, "raise_right_hand", stats[2],
            self.get_student_changes(*3 * ["pondering"], look_at_arg=stats[2])
        )
        self.play(ShowCreationThenFadeAround(stats[2][1][1]))
        self.wait(2)

        self.student_says(
            generate_answer("\\approx \\frac{1}{100}"),
            bubble_kwargs={"width": 4, "height": 3},
            student_index=0,
            target_mode="tease",
            run_time=1,
        )
        self.look_at(self.students[0].bubble.content)
        self.wait(2)

        stats[3].to_edge(RIGHT)
        self.play(
            FadeOut(stats[2], 0.5 * UP),
            FadeIn(stats[3], 0.5 * UP),
            self.teacher.change, "raise_left_hand",
            RemovePiCreatureBubble(self.students[0]),
            *(ApplyMethod(pi.look_at, stats[3]) for pi in self.pi_creatures)
        )
        self.play(ShowCreationThenFadeAround(stats[3][1][1]))
        self.play(
            ShowCreationThenFadeAround(
                stats[3][3][1],
                surrounding_rectangle_config={"color": TEAL},
            ),
            self.teacher.change, "tease", stats[3]
        )
        self.change_student_modes(
            "pondering", "thinking", "confused",
            look_at_arg=self.teacher.get_bottom(),
        )
        self.wait(2)
        self.student_says(
            generate_answer("\\text{ is} \\\\ \\text{a little below } 50\\%"),
            bubble_kwargs={"width": 4, "height": 3},
            student_index=1,
            target_mode="speaking",
            run_time=1,
            added_anims=[
                self.students[0].change, "erm", goal,
                self.students[2].change, "confused", goal,
                self.teacher.change, "happy", self.students[1].eyes,
            ]
        )
        self.wait(2)
        self.change_student_modes(
            "thinking", "hooray", "thinking",
            look_at_arg=self.students[1].bubble.content,
        )
        self.wait(3)


class QuickEstimatesAndMisconceptions(Scene):
    def construct(self):
        titles = VGroup(
            TextMobject("Quick\\\\estimations"),
            TextMobject("Combating\\\\misconceptions"),
        )
        for title, u in zip(titles, [-1, 1]):
            title.set_x(u * FRAME_WIDTH / 4)
        titles.to_edge(UP, buff=MED_SMALL_BUFF)

        circles = VGroup(
            Circle(color=BLUE),
            Circle(color=RED),
        )
        circles[1].flip()
        circles.set_height(4)
        circles.set_stroke(width=3)
        circles.set_fill(opacity=0.5)

        for circle, title, u in zip(circles, titles, [-1, 1]):
            circle.set_x(u)
            title.set_color(
                interpolate_color(circle.get_color(), WHITE, 0.5)
            )
            title.next_to(circle, UP)
            title.shift(u * RIGHT)

        self.play(
            LaggedStartMap(FadeIn, titles, shift=0.2 * UP),
            LaggedStartMap(DrawBorderThenFill, circles),
            run_time=1.5,
        )
        self.wait()

        arrow = TexMobject("\\leftrightarrow", font_size=72)
        arrow.move_to(circles)
        self.play(
            circles[0].next_to, arrow, LEFT,
            circles[1].next_to, arrow, RIGHT,
            titles[0].shift, 0.7 * LEFT,
            titles[1].shift, 0.7 * RIGHT,
            GrowFromCenter(arrow),
        )
        self.wait(2)
        self.play(
            FadeOut(arrow, DOWN),
            circles[0].shift, 2.0 * RIGHT,
            circles[1].shift, 2.0 * LEFT,
            titles[0].shift, 1.0 * RIGHT,
            titles[1].shift, 1.0 * LEFT,
        )
        self.wait()

        titles[1].save_state()
        self.play(
            FadeOut(titles[0]),
            FadeOut(circles[0]),
            titles[1].match_x, circles[1]
        )
        self.wait()

        circles[0].save_state()
        titles[0].save_state()
        circles[0].next_to(circles[1], LEFT, MED_LARGE_BUFF)
        titles[0].next_to(circles[0], UP)

        self.play(
            FadeIn(titles[0]),
            FadeIn(circles[0]),
        )
        self.wait()

        bayes_factor = TextMobject("Bayes\\\\factor", font_size=72)
        bayes_factor.move_to(circles[0])

        self.play(Write(bayes_factor))
        self.wait()
        restoration_group = VGroup(circles[0], titles[0], titles[1])
        self.add(restoration_group, bayes_factor)
        self.play(
            bayes_factor.move_to, VGroup(circles[0].saved_state, circles[1]),
            LaggedStartMap(Restore, restoration_group)
        )
        self.wait()


class WhatDoYouTellThem(Scene):
    def construct(self):
        text = TextMobject("What do you tell them?", font_size=72)
        text.set_color(BLUE)
        self.play(Write(text))
        self.wait(5)


class AccuracyImage(Scene):
    def construct(self):
        sens = 90
        spec = 91
        stats = VGroup(
            TextMobject("Sensitivity: ", f"{sens}\\%"),
            TextMobject("Specificity: ", f"{spec}\\%"),
        )
        stats.arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        for stat, color in zip(stats, [GREEN_B, GREY_B]):
            stat[0].set_color(color)
            stat[1].align_to(stats[0][1], LEFT)

        rect = SurroundingRectangle(stats, buff=0.2)
        rect.set_fill(GREY_E, 1)
        rect.set_stroke(GREY_B, 2)
        stats.add_to_back(rect)
        self.add(stats)


class SamplePopulation10PercentPrevalence(Scene):
    def construct(self):
        # Setup test accuracy figures
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

        # Show population
        population = VGroup(*[WomanIcon() for x in range(100)])
        population.arrange_in_grid(fill_rows_first=False)
        population.set_height(5)
        population.next_to(accuracy_figures, DOWN, LARGE_BUFF)
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

        title = TextMobject("Picture a concrete population", font_size=72)
        title.to_edge(UP)
        self.add(title)

        self.play(
            FadeIn(population, lag_ratio=0.05, run_time=3),
            FadeIn(pop_words),
        )
        self.wait()
        self.play(
            MoveToTarget(population, run_time=2),
            Restore(wc_words),
            Restore(wo_words),
            FadeOut(pop_words),
            title.shift, 0.25 * UP,
        )
        self.wait()

        # Show test stats
        self.play(
            FadeOut(title, shift=UP),
            FadeIn(accuracy_figures[0], 0.5 * UP)
        )

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
            if i == 1:
                self.play(FadeIn(accuracy_figures[1]))
            self.play(ShowCreationThenFadeOut(SurroundingRectangle(
                accuracy_figures[i][i],
                buff=SMALL_BUFF,
                stroke_color=GREEN,
            )))
            self.wait()
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


class NinePercentOfNinety(Scene):
    def construct(self):
        mob = TexMobject("(0.09)(90) = 8.1", tex_to_color_map={"8.1": GREEN})
        mob.scale(2)
        self.add(mob)


class MoreExamples(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "More examples!", target_mode="hooray",
            added_anims=[self.get_student_changes("tired", "erm", "happy", run_time=2)]
        )
        self.wait(3)


class SamplePopulationOneInThousandPrevalence(Scene):
    def construct(self):
        # Add prevalence title
        titles = VGroup(*(
            TextMobject(
                f"What if prevalence is {n} in {k}?",
                tex_to_color_map={
                    n: YELLOW,
                    k: GREY_B,
                }
            )
            for n, k in [("{1}", "{1,000}"), ("{10}", "{10,000}")]
        ))
        titles.to_edge(UP)

        self.add(titles[0])

        # Show population
        dots1k, dots10k = [
            VGroup(*(Dot() for x in range(n))).set_fill(GREY_D)
            for n in [1000, 10000]
        ]
        dots1k[:1].set_fill(YELLOW)
        dots10k[:10].set_fill(YELLOW)

        for dots, n, m in [(dots1k, 20, 50), (dots10k, 100, 100)]:
            sorter = VGroup(*dots)
            sorter.shuffle()
            sorter.arrange_in_grid(n, m, buff=SMALL_BUFF)
            sorter.set_width(FRAME_WIDTH - 1)
            if sorter.get_height() > 6:
                sorter.set_height(6)
            sorter.to_edge(DOWN)

        self.play(FadeIn(dots1k, lag_ratio=0.05, run_time=2))
        self.wait()
        self.play(
            Transform(dots1k, dots10k[0::10]),
        )
        self.play(
            FadeIn(dots10k),
            ReplacementTransform(titles[0][0::2], titles[1][0::2]),
            FadeOut(titles[0][1::2], 0.5 * UP),
            FadeIn(titles[1][1::2], 0.5 * UP),
        )
        self.remove(dots1k)

        # Split the group
        cancer_cases = dots10k[:10]
        cancer_cases.generate_target()
        cancer_cases.target.arrange_in_grid(
            buff=cancer_cases[0].get_width() / 2,
        )
        cancer_cases.target.set_height(2)
        cancer_cases.target.set_y(0)
        cancer_cases.target.to_edge(LEFT, buff=LARGE_BUFF)

        non_cancer_cases = dots10k[10:]
        non_cancer_cases.generate_target()
        non_cancer_cases.target.to_edge(RIGHT)

        c_count = titles[1][1].copy()
        c_count.generate_target()
        c_count.target.next_to(cancer_cases.target, UP, MED_LARGE_BUFF)
        nc_count = Integer(9990)
        nc_count.set_color(GREY_B)
        nc_count.set_opacity(0)
        nc_count.move_to(titles[1][3])

        self.play(
            MoveToTarget(cancer_cases),
            MoveToTarget(non_cancer_cases),
            MoveToTarget(c_count),
            nc_count.set_opacity, 1,
            nc_count.next_to, non_cancer_cases.target, UP,
            FadeOut(titles[1]),
        )
        self.wait()

        # Show test results
        tp_cases = cancer_cases[:9]
        fp_cases = VGroup(*random.sample(list(non_cancer_cases), 900))
        for case in it.chain(tp_cases, fp_cases):
            box = SurroundingRectangle(
                case, buff=0.1 * case.get_width()
            )
            box.set_stroke(GREEN, 3)
            case.box = box

        tn_cases = VGroup(*(
            case for case in non_cancer_cases if case not in fp_cases
        ))

        tp_label = TextMobject("$9$ True Positives")
        tp_label.set_color(GREEN)
        tp_label.move_to(c_count)
        tp_label.shift_onto_screen()

        fp_label = TextMobject("$\\sim 900$ False Positives")
        fp_label.set_color(GREEN_D)
        fp_label.move_to(nc_count)

        self.play(
            FadeOut(c_count),
            FadeIn(tp_label),
            LaggedStart(*(
                ShowCreation(case.box)
                for case in tp_cases
            )),
            cancer_cases[9].set_opacity, 0.25
        )
        self.wait()
        self.play(
            FadeOut(nc_count),
            FadeIn(fp_label),
            LaggedStart(*(
                ShowCreation(case.box)
                for case in fp_cases
            ), lag_ratio=0.001),
            tn_cases.set_opacity, 0.25,
            run_time=2,
        )
        self.wait()

        for case in it.chain(tp_cases, fp_cases):
            case.add(case.box)

        # Organize false positives
        center = fp_cases.get_center()
        fp_cases.sort(lambda p: get_norm(p - center))
        fp_cases.generate_target()
        fp_cases.target.arrange_in_grid(
            buff=fp_cases[0].get_width() / 4,
        )
        fp_cases.target.set_height(6)
        fp_cases.target.to_corner(DR)
        new_center = fp_cases.target.get_center()
        fp_cases.target.sort(lambda p: get_norm(p - new_center))

        self.play(
            MoveToTarget(fp_cases, run_time=4),
            FadeOut(tn_cases, run_time=1),
            FadeOut(cancer_cases[9]),
        )
        self.wait()

        # Final fraction
        final_frac = TexMobject(
            "{{9} \\over {9} + {900}} \\approx 0.01",
            tex_to_color_map={
                "{9}": GREEN,
                "{900}": GREEN_D,
            }
        )
        final_frac.scale(1.5)
        final_frac.next_to(tp_cases, DOWN, LARGE_BUFF)
        final_frac.to_edge(LEFT, LARGE_BUFF)

        self.play(FadeIn(final_frac, lag_ratio=0.2))
        self.wait()


class AltShowUpdatingPrior(Scene):
    def construct(self):
        N = 100
        post_denom = 11
        N_str = "{:,}".format(N)

        # Show prior
        woman = WomanIcon()
        population = VGroup(*[woman.copy() for x in range(N)])
        population.arrange_in_grid()
        population.set_fill(GREY)
        population[0].set_fill(YELLOW)
        population.set_height(5)

        prior_prob = TextMobject("1", " in ", N_str)
        prior_prob.set_color_by_tex("1", YELLOW)
        prior_prob.set_color_by_tex(N_str, GREY_B)
        prior_prob.next_to(population, UP, MED_LARGE_BUFF)
        prior_brace = Brace(prior_prob, UP, buff=SMALL_BUFF)
        prior_words = prior_brace.get_text("Prior")
        prior_words.add_updater(lambda m: m.next_to(prior_brace, UP, SMALL_BUFF))

        thousand_part = prior_prob.get_part_by_tex(N_str)
        pop_count = Integer(N, edge_to_fix=UL)
        pop_count.replace(thousand_part)
        pop_count.match_color(thousand_part)
        pop_count.set_value(0)
        prior_prob.replace_submobject(2, pop_count)

        VGroup(population, prior_prob, prior_brace, prior_words).to_corner(UL)

        self.add(prior_prob)

        # Before word
        before_words = TextMobject(
            "Probability of having the disease\\\\ ",
            "\\emph{before} taking a test"
        )
        before_words.set_color(BLUE_B)
        before_words.next_to(prior_words, RIGHT, buff=3, aligned_edge=UP)
        before_arrow1 = Arrow(before_words[0][0].get_left(), prior_prob.get_right() + MED_SMALL_BUFF * RIGHT)
        before_arrow2 = Arrow(before_words[0][0].get_left(), prior_words.get_right())
        before_arrow1.match_color(before_words)
        before_arrow2.match_color(before_words)

        self.play(
            FadeIn(before_words, lag_ratio=0.1),
            GrowArrow(before_arrow1),
            ShowIncreasingSubsets(population, run_time=2),
            ChangeDecimalToValue(pop_count, len(population), run_time=2),
        )
        self.wait()
        self.play(
            GrowFromCenter(prior_brace),
            FadeIn(prior_words, shift=0.5 * UP),
            ReplacementTransform(before_arrow1, before_arrow2)
        )
        self.wait()

        # Update arrow
        update_arrow = Arrow(2 * LEFT, 2 * RIGHT)
        update_arrow.set_thickness(0.1)
        update_arrow.center()
        update_arrow.match_y(pop_count)
        update_words = TextMobject("See positive test", tex_to_color_map={"positive": GREEN})
        update_words.next_to(update_arrow, UP, SMALL_BUFF)
        low_update_words = TextMobject("Update probability", font_size=36)
        low_update_words.next_to(update_arrow, DOWN, MED_SMALL_BUFF)

        # Posterior
        post_pop = population[:post_denom].copy()
        post_pop.arrange_in_grid(
            buff=get_norm(population[1].get_left() - population[0].get_right())
        )
        post_pop.match_height(population)
        post_pop.next_to(
            update_arrow, RIGHT,
            buff=abs(population.get_right()[0] - update_arrow.get_left()[0])
        )
        post_pop.align_to(population, UP)

        def give_pop_plusses(pop):
            for icon in pop:
                plus = TexMobject("+")
                plus.set_color(GREEN)
                plus.set_width(icon.get_width() / 2)
                plus.move_to(icon.get_corner(UR))
                icon.add(plus)

        give_pop_plusses(post_pop)

        post_prob = prior_prob.copy()
        post_prob[2].set_value(post_denom)
        post_prob.next_to(post_pop, UP, buff=MED_LARGE_BUFF)

        roughly = TextMobject("(roughly)", font_size=24)
        roughly.next_to(post_prob, RIGHT, buff=0.2)

        post_prob[2].set_value(0)
        self.play(
            FadeIn(update_words, lag_ratio=0.2),
            FadeOut(before_words),
            ReplacementTransform(before_arrow2, update_arrow, path_arc=30 * DEGREES),
            FadeIn(low_update_words, lag_ratio=0.2),
        )
        self.add(post_prob)
        self.play(
            ShowIncreasingSubsets(post_pop, run_time=1),
            ChangeDecimalToValue(post_prob[2], post_denom, run_time=1),
            FadeIn(roughly),
        )
        self.wait()

        post_brace = Brace(post_prob, UP, buff=SMALL_BUFF)
        post_words = post_brace.get_text("Posterior")
        post_words.add_updater(lambda m: m.next_to(post_brace, UP, SMALL_BUFF))
        post_words.update(0)

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

        return
        # Change prior and posterior
        pop100, pop11, pop10, pop2 = pops = [
            VGroup(*[woman.copy() for x in range(n)])
            for n in [100, 11, 10, 2]
        ]
        for pop in pops:
            pop.arrange_in_grid()
            pop.set_fill(GREY)
            pop[0].set_fill(YELLOW)
            pop.scale(
                post_pop[0].get_height() / pop[0].get_height()
            )

        pop100.replace(population)
        pop11.move_to(post_pop, UP)
        pop11.shift(0.2 * LEFT)
        pop10.move_to(population, UP)
        pop10.shift(0.4 * LEFT)
        pop2.move_to(post_pop, UP)
        pop2.shift(0.3 * LEFT)

        give_pop_plusses(pop11)
        give_pop_plusses(pop2)

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
            *replace_population_anims(population, pop100, prior_prob[2], prior_brace)
        )
        self.play(
            *replace_population_anims(post_pop, pop11, post_prob[2], post_brace),
        )
        self.wait(2)
        self.play(
            *replace_population_anims(pop100, pop10, prior_prob[2], prior_brace),
            prior_words.shift, 0.1 * LEFT
        )
        self.play(
            *replace_population_anims(pop11, pop2, post_prob[2], post_brace)
        )
        self.wait(2)


class ContrastThreeContexts(Scene):
    def construct(self):
        # Background
        bg_rect = FullScreenFadeRectangle()
        bg_rect.set_fill(GREY_E, 1)
        self.add(bg_rect)

        # Scene templates
        screens = VGroup(*(
            ScreenRectangle() for x in range(3)
        ))
        screens.set_stroke(WHITE, 2)
        screens.set_fill(BLACK, 1)
        screens.arrange(DOWN, buff=LARGE_BUFF)
        screens.set_height(FRAME_HEIGHT - 1)
        screens.next_to(ORIGIN, RIGHT)

        self.add(screens)

        # Prevalence values
        dots_template = VGroup(*(Dot() for x in range(1000)))
        dots_template.arrange_in_grid(20, 50, buff=SMALL_BUFF)
        dots_template.set_fill(GREY_B)
        dot_groups = VGroup()
        for screen, n in zip(screens, [1, 10, 100]):
            dots = dots_template.copy()
            dots.match_width(screen)
            dots.scale(0.9)
            dots.move_to(screen, DOWN)
            dots.shift(0.1 * UP)
            for dot in random.sample(list(dots), n):
                dot.set_fill(YELLOW)
            dot_groups.add(dots)

        prevalence_labels = VGroup(
            TextMobject("Prevalence: ", "0.1\\%"),
            TextMobject("Prevalence: ", "1\\%"),
            TextMobject("Prevalence: ", "10\\%"),
        )
        for label, dots in zip(prevalence_labels, dot_groups):
            label.scale(0.75)
            label[1].set_color(YELLOW)
            label.next_to(dots, UP, buff=0.15)

        self.add(prevalence_labels)
        self.add(dot_groups)

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
            get_positive_result() for screen in screens
        ))
        positive_results.generate_target()
        positive_results.set_opacity(0)
        for screen, result in zip(screens, positive_results.target):
            result.set_height(screen.get_height() * 0.5)
            result.next_to(screen, RIGHT, aligned_edge=DOWN)
            result.shift(0.25 * UP)

        self.add(words[2])
        self.play(MoveToTarget(positive_results))
        self.wait()

        # Different results
        probs = VGroup(*(
            Integer(0, unit="\\%").next_to(result, UP)
            for result in positive_results
        ))
        probs.set_fill(GREEN)

        self.play(
            ChangeDecimalToValue(probs[0], 1),
            ChangeDecimalToValue(probs[1], 9),
            ChangeDecimalToValue(probs[2], 53),
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
            TextMobject("\\,", "your chances"),
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
            FadeIn(up_words[2][0], scale=2),
            ReplacementTransform(ta_words[3][1], up_words[2][1]),
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

        # Show updates
        arrows = VGroup(*(
            Arrow(
                pl.get_corner(UR), prob.get_corner(UL),
                buff=0.1,
                path_arc=-45 * DEGREES,
            )
            for pl, prob in zip(prevalence_labels, probs)
        ))
        arrows.set_color(RED)

        self.play(LaggedStartMap(
            GrowArrow, arrows,
            lag_ratio=0.5,
            path_arc=-45 * DEGREES,
        ))
        self.wait()


class BayesFactor(Scene):
    def construct(self):
        # Test sensitivity
        woman = WomanIcon()
        bc_pop = VGroup(*[woman.copy() for x in range(100)])
        bc_pop.arrange_in_grid(h_buff=1.5, v_buff=1)
        bc_pop.set_height(4)
        bc_pop.next_to(ORIGIN, LEFT, MED_LARGE_BUFF)
        bc_rect = SurroundingRectangle(bc_pop, buff=0.15)
        bc_rect.set_stroke(YELLOW, 2)

        with_bc_label = TextMobject(
            "Patients with\\\\breast cancer",
            font_size=36,
            color=bc_rect.get_color()
        )
        with_bc_label.next_to(bc_rect, UP)

        bc_pop.generate_target()
        bc_signs = VGroup()
        for n, icon in enumerate(bc_pop.target):
            if n < 90:
                sign = TexMobject("+", color=GREEN)
                icon.set_color(GREEN)
            else:
                sign = TexMobject("-", color=RED)
                icon.set_color(RED)
            sign.match_width(icon)
            sign.move_to(icon.get_corner(UR), LEFT)
            bc_signs.add(sign)

        sens_brace = Brace(bc_pop[:90], LEFT, buff=MED_SMALL_BUFF)
        sens_word = sens_brace.get_text("90\\% Sens.")
        sens_word.set_color(GREEN)
        fnr_brace = Brace(bc_pop[90:], LEFT, buff=MED_SMALL_BUFF)
        fnr_word = fnr_brace.get_text("10\\% FNR")
        fnr_word.set_color(RED_E)

        bc_group = VGroup(
            with_bc_label,
            bc_rect,
            bc_pop,
            bc_signs,
            sens_brace,
            sens_word,
            fnr_brace,
            fnr_word,
        )

        # Specificity (too much copy paste)
        nc_pop = bc_pop.copy()
        nc_pop.next_to(ORIGIN, RIGHT, MED_LARGE_BUFF)
        nc_rect = SurroundingRectangle(nc_pop, buff=0.15)
        nc_rect.set_stroke(GREY_B, 2)

        without_bc_label = TextMobject(
            "Patients without\\\\breast cancer",
            font_size=36,
            color=nc_rect.get_color()
        )
        without_bc_label.next_to(nc_rect, UP)

        nc_pop.generate_target()
        nc_signs = VGroup()
        for n, icon in enumerate(nc_pop.target):
            if 0 < n < 10:
                sign = TexMobject("+", color=GREEN)
                icon.set_color(GREEN)
            else:
                sign = TexMobject("-", color=RED)
                icon.set_color(RED)
            sign.match_width(icon)
            sign.move_to(icon.get_corner(UR), LEFT)
            nc_signs.add(sign)

        spec_brace = Brace(nc_pop[10:], RIGHT, buff=MED_SMALL_BUFF)
        spec_word = spec_brace.get_text("91\\% Spec.")
        spec_word.set_color(RED)
        fpr_brace = Brace(nc_pop[:10], RIGHT, buff=MED_SMALL_BUFF)
        fpr_word = fpr_brace.get_text("9\\% FPR")
        fpr_word.set_color(GREEN_D)

        nc_group = VGroup(
            without_bc_label,
            nc_rect,
            nc_pop,
            nc_signs,
            spec_brace,
            spec_word,
            fpr_brace,
            fpr_word,
        )

        # Draw groups
        self.play(LaggedStart(
            FadeIn(with_bc_label),
            ShowCreation(bc_rect),
            ShowIncreasingSubsets(bc_pop),
            FadeIn(without_bc_label),
            ShowCreation(nc_rect),
            ShowIncreasingSubsets(nc_pop),
        ))
        self.play(LaggedStart(
            MoveToTarget(bc_pop),
            FadeIn(bc_signs, lag_ratio=0.02),
            GrowFromCenter(sens_brace),
            FadeIn(sens_word, shift=0.2 * LEFT),
            GrowFromCenter(fnr_brace),
            FadeIn(fnr_word, shift=0.2 * LEFT),
        ))
        self.play(LaggedStart(
            MoveToTarget(nc_pop),
            FadeIn(nc_signs, lag_ratio=0.02),
            GrowFromCenter(spec_brace),
            FadeIn(spec_word, shift=0.2 * RIGHT),
            GrowFromCenter(fpr_brace),
            FadeIn(fpr_word, shift=0.2 * RIGHT),
        ))
        self.wait()

        groups = VGroup(bc_group, nc_group)

        # Highlight relevant parts
        fade_rects = VGroup(*(BackgroundRectangle(group) for group in groups))
        fade_rects.set_fill(BLACK, 0.8)

        self.play(FadeIn(fade_rects[1]))
        self.play(LaggedStart(*(
            ShowCreationThenFadeOut(Underline(word))
            for word in [sens_word, fnr_word]
        ), lag_ratio=0.4))
        self.play(
            FadeIn(fade_rects[0]),
            FadeOut(fade_rects[1]),
        )
        self.play(LaggedStart(*(
            ShowCreationThenFadeOut(Underline(word))
            for word in [spec_word, fpr_word]
        ), lag_ratio=0.4))
        self.wait()
        self.play(FadeOut(fade_rects[0]))

        # None of these are your answer
        title = TexMobject(
            "\\text{None of these tell you }",
            "P(\\text{Cancer} \\,|\\, +)",
            tex_to_color_map={
                "\\text{Cancer}": YELLOW,
                "+": GREEN,
            },
            font_size=72,
        )
        title.to_edge(UP)
        title_underline = Underline(title)

        self.play(
            FadeIn(title, lag_ratio=0.1),
            groups.to_edge, DOWN,
        )
        self.play(ShowCreation(title_underline))
        self.wait()
        title.add(title_underline)

        # Ask about update strength
        question = TextMobject("How strongly\\\\does it update?")
        question.set_height(1)
        question.to_corner(UL)
        question.save_state()
        question.replace(title, 1)
        question.set_opacity(0)

        self.play(
            Restore(question),
            title.replace, question.saved_state, 0,
            title.set_opacity, 0,
        )
        self.remove(title)
        self.wait()

        # Write Bayes factor
        frac = VGroup(
            sens_word.copy(),
            TexMobject("\\qquad \\over \\qquad"),
            fpr_word.copy(),
        )
        frac[1].match_width(frac[0], stretch=True)
        frac.arrange(DOWN, SMALL_BUFF)
        frac.next_to(question, RIGHT, LARGE_BUFF)

        mid_rhs = TexMobject(
            "= {P(+ \\,|\\, \\text{Cancer}) \\over P(+ \\,|\\, \\text{No cancer})}",
            tex_to_color_map={
                "+": GREEN,
                "\\text{Cancer}": YELLOW,
                "\\text{No cancer}": GREY_B,
            }
        )
        mid_rhs.next_to(frac, RIGHT)

        rhs = TexMobject("= 10", font_size=72)
        rhs.next_to(mid_rhs, RIGHT)

        for part in frac[0::2]:
            part.save_state()
        frac[0].replace(sens_word)
        frac[2].replace(fpr_word)

        s_rect = SurroundingRectangle(frac[0])
        self.play(ShowCreation(s_rect))
        self.play(
            Restore(frac[0]),
            s_rect.move_to, frac[0].saved_state,
            s_rect.set_opacity, 0,
            Write(frac[1]),
            Restore(frac[2]),
        )
        self.wait(2)
        self.play(Write(mid_rhs))
        self.wait()
        self.play(Write(rhs))
        self.wait()

        # Name the Bayes factor
        bf_name = TextMobject("Bayes\\\\Factor ", font_size=72)
        equals = TexMobject("=", font_size=72).next_to(frac, LEFT)
        bf_name.next_to(equals, LEFT)
        lr_name = TextMobject("Likelihood\\\\ratio")
        lr_name.next_to(equals, LEFT)

        self.play(
            FadeOut(question, UP),
            FadeIn(bf_name, UP),
            FadeIn(equals, UP),
        )
        self.wait()
        self.play(
            FadeOut(bf_name, UP),
            FadeIn(lr_name, UP),
        )
        self.wait()
        self.play(
            FadeIn(bf_name, DOWN),
            FadeOut(lr_name, DOWN),
        )
        self.wait(5)


class RuleOfThumb(Scene):
    def construct(self):
        tex_to_color_map = {
            "+": GREEN,
            "\\text{Cancer}": YELLOW,
            "\\text{No cancer}": GREY_B,
            "=": WHITE,
            "\\over": WHITE,
            "{90\\%": GREEN,
            "9\\%}": GREEN,
            "1\\%}": TEAL,
            "10": WHITE,
        }
        bf_computation = TexMobject(
            """
            {
            P(+ \\, | \\, \\text{Cancer}) \\over
            P(+ \\, | \\, \\text{No cancer})
            } =
            {90\\% \\over 9\\%} = 10
            """,
            tex_to_color_map=tex_to_color_map
        )

        bf_computation.to_edge(LEFT)

        self.add(bf_computation)


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


class OddsComments(Scene):
    def construct(self):
        morty = Mortimer()
        morty.to_corner(DR)
        randy = Randolph()
        randy.next_to(morty, LEFT, buff=2)

        self.play(FadeIn(morty))
        self.play(
            PiCreatureSays(
                morty,
                "The chances are\\\\1 to 1",
                run_time=1
            ),
            FadeIn(randy)
        )
        self.play(Blink(morty))
        self.play(
            PiCreatureSays(randy, "The chances are\\\\2 to 1", run_time=1),
            RemovePiCreatureBubble(morty, target_mode="happy")
        )
        self.play(Blink(morty))
        self.play(Blink(randy))
        self.wait()


class NewSnazzyBayesRuleSteps(Scene):
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

        # Completely accurate
        accurate_words = TextMobject(
            *"Completely accurate\\\\ Not even approximating things".split(" "),
            font_size=72,
            arg_separator=" "
        )
        accurate_words.set_color(BLUE)
        for word in accurate_words:
            self.add(word)
            self.wait(0.05 * len(word))

        # Population
        population = VGroup(*(
            WomanIcon()
            for x in range(100)
        ))
        population.arrange_in_grid(h_buff=1, v_buff=0.5, fill_rows_first=False)
        population.set_height(5)
        population.to_corner(DR)
        population[0].set_color(YELLOW)

        # Step labels
        step_labels = VGroup(
            TextMobject("Step 1)"),
            TextMobject("Step 2)"),
            TextMobject("Step 3)"),
        )
        step_labels.arrange(DOWN, buff=1.5, aligned_edge=LEFT)
        step_labels.next_to(title, DOWN, MED_LARGE_BUFF)
        step_labels.to_edge(LEFT)

        step1, step2, step3 = steps = VGroup(
            TextMobject("Express the prior with odds"),
            TextMobject("Compute Bayes' factor"),
            TextMobject("Multiply"),
        )

        colors = [YELLOW, GREEN, BLUE]
        for step, label, color in zip(steps, step_labels, colors):
            step.set_color(color)
            step.next_to(label, RIGHT)

        self.play(
            LaggedStartMap(FadeIn, step_labels, shift=0.5 * RIGHT),
            LaggedStartMap(FadeIn, steps, shift=RIGHT),
            FadeOut(accurate_words),
        )
        self.wait()

        # Step 2 details
        tex_to_color_map = {
            "+": GREEN,
            "\\text{Cancer}": YELLOW,
            "\\text{No cancer}": GREY_B,
            "=": WHITE,
            "\\over": WHITE,
            "{90\\%": GREEN,
            "9\\%}": GREEN,
            "1\\%}": TEAL,
            "10": WHITE,
        }
        bf_computation = TexMobject(
            """
            {
            P(+ \\, | \\, \\text{Cancer}) \\over
            P(+ \\, | \\, \\text{No cancer})
            } =
            {90\\% \\over 9\\%} = 10
            """,
            tex_to_color_map=tex_to_color_map
        )
        bf_computation[-1].scale(1.2)
        bf_computation.scale(0.6)
        bf_computation.next_to(step2, DOWN, aligned_edge=LEFT)
        bf_computation.save_state()
        bf_computation.scale(1.5)
        bf_computation.next_to(steps[1], RIGHT, LARGE_BUFF)

        lr_words = TextMobject("``Likelihood ratio''", font_size=30)
        lr_words.next_to(bf_computation[-1], RIGHT, MED_LARGE_BUFF, DOWN)
        lr_words.set_color(GREY_A)

        sens_part = bf_computation.get_part_by_tex("90\\%")
        sens_word = TextMobject("Sensitivity")
        sens_word.next_to(sens_part, UP, buff=1)
        sens_arrow = Arrow(sens_word.get_bottom(), sens_part.get_top(), buff=0.1)

        fpr_part = bf_computation.get_part_by_tex("9\\%")
        fpr_word = TextMobject("FPR")
        fpr_word.next_to(fpr_part, DOWN, buff=1)
        fpr_arrow = Arrow(fpr_word.get_top(), fpr_part.get_bottom(), buff=0.1)

        self.play(FadeIn(bf_computation, lag_ratio=0.1))
        self.wait()
        self.play(
            Indicate(sens_part),
            FadeIn(sens_word),
            GrowArrow(sens_arrow)
        )
        self.wait()
        self.play(
            Indicate(fpr_part),
            FadeIn(fpr_word),
            GrowArrow(fpr_arrow),
        )
        self.wait(2)
        self.play(
            Restore(bf_computation),
            FadeOut(VGroup(sens_word, sens_arrow, fpr_word, fpr_arrow))
        )

        # Step 1 details
        step1_subtext = TextMobject("E.g.", " 1\\% ", " $\\rightarrow$ ", "1:99")
        step1_subtext.set_color(GREY_A)
        step1_subtext.scale(0.9)
        step1_subtext.next_to(step1, DOWN, aligned_edge=LEFT)

        step1_subtext.unlock_triangulation()
        self.play(
            FadeIn(step1_subtext[:2]),
            ShowIncreasingSubsets(population),
        )
        self.wait()
        self.play(
            TransformFromCopy(step1_subtext[1], step1_subtext[3]),
            Write(step1_subtext[2]),
        )
        self.play(ShowCreationThenFadeAround(step1_subtext[3]))
        self.wait()

        # Step 3
        multiplication = TexMobject(
            "(", "1:99", ")", "\\times", "10",
            "=", "10:99",
            "\\rightarrow", "{10 \\over 109}",
            "\\approx", "{1 \\over 11}",
            font_size=36,
        )
        multiplication.next_to(step3, DOWN, aligned_edge=LEFT)
        multiplication.unlock_triangulation()

        odds_rect = SurroundingRectangle(step1_subtext[-1], color=YELLOW)
        bf_rect = SurroundingRectangle(bf_computation[-1], color=GREEN)
        self.play(
            ShowCreation(odds_rect),
            ShowCreation(bf_rect),
        )
        self.play(
            Write(VGroup(*(multiplication[i] for i in [0, 2, 3]))),
            TransformFromCopy(step1_subtext[-1], multiplication[1]),
            odds_rect.move_to, multiplication[1],
            odds_rect.set_opacity, 0,
            TransformFromCopy(bf_computation[-1], multiplication[4]),
            bf_rect.move_to, multiplication[4],
            bf_rect.set_opacity, 0,
        )
        self.remove(odds_rect, bf_rect)
        self.wait()

        self.play(
            FadeIn(multiplication.get_part_by_tex("=")),
            TransformFromCopy(
                multiplication.get_part_by_tex("1:99"),
                multiplication.get_part_by_tex("10:99"),
                path_arc=30 * DEGREES,
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

        # 10% prior example
        prior_odds = step1_subtext[1:]
        alt_prior_odds = TexMobject(
            "10\\%", "\\rightarrow", "\\text{1:9}"
        )
        alt_prior_odds.match_height(prior_odds)
        alt_prior_odds.move_to(prior_odds, LEFT)
        alt_prior_odds.match_style(prior_odds)

        self.play(
            FadeOut(multiplication, shift=DOWN),
            FadeOut(prior_odds, shift=DOWN),
        )
        self.play(
            FadeIn(alt_prior_odds[0], scale=2),
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
        self.play(
            Write(alt_prior_odds[1]),
            FadeIn(alt_prior_odds[2], shift=0.5 * RIGHT)
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
            SurroundingRectangle(alt_prior_odds.get_part_by_tex("1:9"), color=YELLOW),
            SurroundingRectangle(bf_computation.get_part_by_tex("10"), color=GREEN),
            SurroundingRectangle(new_multiplication.get_part_by_tex("10:9"), color=RED),
        )

        self.play(
            FadeIn(rects[:2], lag_ratio=0.6, run_time=1.5)
        )
        self.play(
            ReplacementTransform(rects[0], rects[2]),
            ReplacementTransform(rects[1], rects[2]),
            FadeIn(new_multiplication[:5]),
        )
        self.wait()

        alt_rhs = TexMobject("> 1:1", font_size=36)
        alt_rhs.next_to(new_multiplication[4], RIGHT)
        self.play(
            FadeOut(rects[2]),
            Write(alt_rhs)
        )
        self.wait()

        self.play(
            FadeOut(alt_rhs, shift=0.5 * UP),
            FadeIn(new_multiplication[5:7], shift=0.5 * UP),
        )
        self.wait()
        self.play(Write(new_multiplication[7:]))
        self.wait()

        # Return to original prior
        self.play(
            FadeOut(new_multiplication, shift=DOWN),
            FadeOut(alt_prior_odds, shift=DOWN),
            FadeIn(prior_odds, shift=DOWN)
        )
        self.play(population[1:].set_color, GREY_B)
        self.play(Indicate(population[0], color=RED))
        self.play(LaggedStartMap(
            Indicate, population[1:], color=GREY_A,
            lag_ratio=0.01
        ))
        self.wait()

        # Change test accuracy
        new_bf_computation = TexMobject(
            """
            {
            P(+ \\, | \\, \\text{Cancer}) \\over
            P(+ \\, | \\, \\text{No cancer})
            } =
            {90\\% \\over 1\\%} = 90
            """,
            tex_to_color_map=tex_to_color_map
        )
        new_bf_computation.replace(bf_computation)
        new_bf_computation[-2:].scale(1.5, about_edge=LEFT)

        rects = VGroup(*(
            SurroundingRectangle(bf_computation[i:j], buff=0.05)
            for (i, j) in [(5, 8), (14, 15)]
        ))
        rects.set_color(RED)

        self.play(ShowCreation(rects))
        self.wait()
        self.play(
            FadeOut(bf_computation),
            FadeIn(new_bf_computation[:-2])
        )
        self.play(FadeOut(rects))
        self.wait()
        self.play(Write(new_bf_computation[-2:]))
        self.wait()

        # New posterior (largely copy-pasted)
        final_multiplication = TexMobject(
            "(1:99)", "\\times", "90",
            "=", "90:99",
            "\\rightarrow", "{90 \\over 189}",
            "\\approx", "0.48",
            font_size=36,
        )
        final_multiplication.move_to(multiplication, LEFT)
        rects = VGroup(
            SurroundingRectangle(step1_subtext.get_part_by_tex("1:99"), color=YELLOW),
            SurroundingRectangle(new_bf_computation.get_parts_by_tex("90")[1], color=GREEN),
            SurroundingRectangle(final_multiplication.get_part_by_tex("90:99"), color=RED),
        )

        self.play(
            FadeIn(rects[:2], lag_ratio=0.6, run_time=1.5)
        )
        self.play(
            ReplacementTransform(rects[0], rects[2]),
            ReplacementTransform(rects[1], rects[2]),
            FadeIn(final_multiplication[:5]),
        )
        self.wait()

        alt_rhs = TexMobject("< 1:1", font_size=36)
        alt_rhs.next_to(final_multiplication[4], RIGHT)
        self.play(
            FadeOut(rects[2]),
            Write(alt_rhs)
        )
        self.wait()

        self.play(
            FadeOut(alt_rhs, shift=0.5 * UP),
            FadeIn(final_multiplication[5:7], shift=0.5 * UP),
        )
        self.wait()
        self.play(Write(final_multiplication[7:]))
        self.wait()


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


class ReframeWhatTestsDo(TeacherStudentsScene):
    def construct(self):
        # Question
        question = TextMobject("What do tests tell you?")
        self.teacher_holds_up(question)
        self.wait()

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
            students[0].set_opacity, 0.5,
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
            *(
                TransformFromCopy(
                    answers[1][i],
                    answers[2][i],
                )
                for i in [0, 2, 3]
            ),
            Restore(answers[2][1]),
            students[0].change, "pondering", answers[1],
            students[1].set_opacity, 0.5,
            students[1].change, "pondering", answers[1],
            students[2].change, "raise_left_hand", answers[1],
        )
        self.play(
            self.teacher.change, "happy", students[2].eyes,
        )
        self.wait()

        # The fundamental reframing
        new_title = TextMobject(
            "The Fundamental Reframing",
            font_size=72,
        )
        new_title.add(Underline(new_title))
        new_title.to_edge(UP)

        self.play(
            Write(new_title),
            FadeOut(question),
            self.students[2].change, "hooray", new_title,
            answers.shift, 0.5 * DOWN,
        )
        self.wait(3)


class PrevalenceVsPrior(Scene):
    def construct(self):
        # Prior and prevalence
        eq = TextMobject(
            "Prevalence = Prior",
            tex_to_color_map={
                "Prevalence": WHITE,
                "Prior": YELLOW,
            }
        )
        eq.shift(UP)
        prior = eq[2]
        prev = eq[0]

        strike = Line(eq.get_left(), eq.get_right())
        strike.set_stroke(RED, 4)
        not_words = TextMobject("Not necessarily!")
        not_words.set_color(RED)
        not_words.match_width(eq)
        not_words.next_to(eq, DOWN, MED_LARGE_BUFF)

        factors = VGroup(
            TextMobject("Prevalence"),
            TextMobject("Symptoms"),
            TextMobject("Contacts\\\\", "(if contagious)"),
        )
        factors.arrange(DOWN, buff=MED_LARGE_BUFF, aligned_edge=LEFT)
        factors.shift(prev.get_center() - factors[0].get_center())

        prior.generate_target()
        prior.target.match_y(factors[1])
        prior.target.shift(0.5 * RIGHT)
        arrows = VGroup(*(
            Arrow(
                factor.get_right(), prior.target.get_corner(LEFT + u * UP),
                buff=0.1,
                max_tip_length_to_length_ratio=0.25,
            )
            for u, factor in zip([1, 0, -1], factors)
        ))

        population = Population(100)
        population.set_height(7)
        population.to_edge(LEFT)
        population.set_fill(GREY_C)
        random.choice(population).set_color(YELLOW)

        self.play(Write(prev))
        self.play(ShowIncreasingSubsets(population, run_time=3))
        self.wait()
        self.play(Write(eq[1:]))
        self.wait()

        self.play(
            ShowCreation(strike),
            FadeIn(not_words, shift=0.2 * DOWN, rate_func=squish_rate_func(smooth, 0.3, 1))
        )
        self.wait()

        eq[1].unlock_triangulation()
        self.play(
            Uncreate(strike),
            MoveToTarget(prior),
            ReplacementTransform(eq[1], arrows),
            LaggedStartMap(FadeIn, factors[1:], shift=0.25 * DOWN),
            FadeOut(not_words, shift=DOWN)
        )
        self.remove(prev)
        self.add(factors)
        self.wait()

        # Symptoms
        randy = Randolph(height=1.5)
        randy.to_corner(UR)
        randy.shift(LEFT)

        self.play(FadeIn(randy))
        self.play(
            ShowCreationThenFadeOut(Underline(factors[1], color=RED)),
            randy.change, "sick",
            randy.set_color, SICKLY_GREEN,
        )
        self.wait()

        # Contagion (implicit)
        self.play(
            ShowCreationThenFadeOut(Underline(factors[2][0], color=RED)),
            ShowCreationThenFadeOut(Underline(factors[2][1], color=RED)),
        )
        self.wait()

        self.play(
            LaggedStartMap(
                FadeOut, VGroup(
                    randy, prior, *arrows, *factors,
                ),
                shift=DOWN,
            )
        )


# Everything above has been combed through after the rewrite

class OldBayesFactorCode(Scene):
    def construct(self):
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


class LookOverTweet(Scene):
    def construct(self):
        # Tweet
        bg_rect = FullScreenFadeRectangle()
        bg_rect.set_fill(GREY_E, 1)
        self.add(bg_rect)

        tweet = ImageMobject("twitter_covid_test_poll")
        tweet.set_height(6)
        tweet.to_edge(LEFT)
        self.play(FadeIn(tweet, shift=UP, scale=1.2))
        self.wait()

        # Tweet highlights
        lines = VGroup(
            Line((-3.9, 1.7), (0.3, 1.7)),
            Line((-3.4, 0.1), (-0.7, 0.1)),
            VGroup(
                Line((0.2, 0.1), (0.8, 0.1)),
                Line((-6.4, -0.3), (-4, -0.3)),
            ),
        )
        lines.set_color(RED)

        rects = VGroup(*(Rectangle(3.2, 0.37) for x in range(4)))
        rects.arrange(DOWN, buff=0.08)
        rects.set_stroke(BLUE, 3)
        rects.set_fill(BLUE, 0.25)
        rects.move_to((-4.8, -1.66, 0.))

        # Population
        icon = SVGMobject("person")
        icon.set_stroke(width=0)
        globals()['icon'] = icon
        population = VGroup(*(icon.copy() for x in range(1000)))

        population.scale(1 / population[0].get_height())
        population.arrange_in_grid(
            30, 33,
            buff=MED_LARGE_BUFF,
        )
        population.set_width(4)
        population.to_edge(RIGHT)
        population.set_fill(GREY_B)
        population[random.randint(0, 1000)].set_fill(YELLOW)

        pop_title = TextMobject("1", " in ", "1,000")
        pop_title[0].set_color(YELLOW)
        pop_title.next_to(population, UP)

        self.play(
            FadeIn(pop_title, shift=0.25 * UP),
            ShowIncreasingSubsets(population),
            ShowCreation(lines[0])
        )
        self.wait()

        pop_group = VGroup(population, pop_title)

        # Positive result
        clipboard = SVGMobject("clipboard")
        clipboard.set_stroke(width=0)
        clipboard.set_fill(interpolate_color(GREY_BROWN, WHITE, 0.5), 1)
        clipboard.set_width(2.5)
        clipboard.move_to(population)
        clipboard.to_edge(UP)

        result = TextMobject(
            "+\\\\",
            "SARS\\\\CoV-2\\\\",
            "Detected"
        )
        result[0].scale(1.5, about_edge=DOWN)
        result[0].set_fill(GREEN)
        result[0].set_stroke(GREEN, 2)
        result[-1].set_fill(GREEN)
        result.set_width(clipboard.get_width() * 0.7)
        result.move_to(clipboard)
        result.shift(0.2 * DOWN)
        clipboard.add(result)

        self.play(
            pop_group.scale, 0.4,
            pop_group.to_edge, DOWN,
            FadeIn(clipboard, DOWN),
        )
        self.wait()

        # FPR, FRN
        self.play(ShowCreation(lines[1]))
        self.wait()
        self.play(ShowCreation(lines[2]))
        self.wait()

        # Answer choices
        rect = rects[0].copy()
        self.play(DrawBorderThenFill(rect))
        self.wait()
        for r2 in rects[1:]:
            self.play(Transform(rect, r2))
            self.wait()
        self.play(FadeOut(rect))

        # Focus on FPR
        rect = Rectangle()
        rect.match_width(lines[1])
        rect.scale(1.02)
        rect.set_height(0.4, stretch=True)
        rect.match_style(lines[1])
        rect.move_to(lines[1], DOWN)
        rect.set_fill(RED, 0.2)

        self.play(
            FadeOut(lines[0]),
            FadeOut(lines[2]),
            DrawBorderThenFill(rect)
        )

        # Randy
        randy = Randolph(height=2)
        randy.flip()
        randy.next_to(tweet, RIGHT, LARGE_BUFF, DOWN)

        bubble = randy.get_bubble(height=3, width=3, direction=RIGHT)
        bubble.flip()
        bubble.write("99\\%\\\\right?")

        self.play(
            FadeIn(randy),
            FadeOut(clipboard, RIGHT),
            FadeOut(pop_group, 0.5 * RIGHT),
        )
        self.play(
            randy.change, "maybe",
            DrawBorderThenFill(bubble),
            Write(bubble.content),
        )
        self.play(Blink(randy))
        self.wait()


class DisambiguateFPR(Scene):
    def construct(self):
        # Add title
        title = TextMobject(
            "1\\% False Positive Rate",
            substrings_to_isolate=["F", "P", "R"],
            font_size=72
        )
        title.to_edge(UP)
        title.set_color(GREY_A)
        underline = Underline(title)
        underline.match_color(title)

        morty = Mortimer()
        morty.to_corner(DR)
        morty.look_at(title)

        self.add(title)
        self.play(
            PiCreatureSays(
                morty,
                "It's a confusing term!",
                target_mode="surprised",
                run_time=1,
            )
        )
        self.play(
            Blink(morty),
            ShowCreation(underline),
        )
        self.play(morty.change, "angry")
        self.play(Blink(morty))

        # Draw out grid
        word_grid = VGroup(
            TextMobject("True positives", color=GREEN),
            TextMobject("False negatives", color=RED_E),
            TextMobject("False positives", color=GREEN_D),
            TextMobject("True negatives", color=RED),
        )
        word_box = SurroundingRectangle(word_grid)
        word_box.set_stroke(WHITE, 2)
        word_box.stretch(2, 1)

        word_grid.arrange_in_grid(
            v_buff=1.0,
            h_buff=0.5,
            fill_rows_first=False
        )
        word_grid.move_to(2 * DOWN)

        globals()['word_box'] = word_box
        word_boxes = VGroup(*(
            word_box.copy().move_to(word).match_color(word)
            for word in word_grid
        ))

        group_boxes = VGroup(
            SurroundingRectangle(word_boxes[:2], color=YELLOW),
            SurroundingRectangle(word_boxes[2:], color=GREY_B),
        )
        group_titles = VGroup(
            TextMobject("Have COVID-19", font_size=36),
            TextMobject("Don't have COVID-19", font_size=36),
        )
        for box, gt in zip(group_boxes, group_titles):
            gt.next_to(box, UP)
            gt.match_color(box)

        icon = SVGMobject("person", stroke_width=0, fill_color=GREY_B)
        globals()['icon'] = icon
        with_pop = VGroup(*(icon.copy() for x in range(1)))
        with_pop.set_color(YELLOW)
        without_pop = VGroup(*(icon.copy() for x in range(999)))

        with_pop.set_height(0.5)
        with_pop.move_to(group_boxes[0])
        without_pop.arrange_in_grid(n_rows=20)
        without_pop.replace(group_boxes[1], dim_to_match=1)
        without_pop.scale(0.9)

        self.play(
            ShowCreation(group_boxes, lag_ratio=0.3),
            DrawBorderThenFill(with_pop),
            ShowIncreasingSubsets(without_pop),
            FadeIn(group_titles, lag_ratio=0.3),
            FadeOut(morty),
            FadeOut(morty.bubble),
            FadeOut(morty.bubble.content),
        )
        self.wait()

        arrow = Vector(DOWN)
        arrow.next_to(group_titles[1], UP)
        self.play(GrowArrow(arrow))
        self.wait()
        self.play(
            LaggedStartMap(Write, word_grid[2:], lag_ratio=0.9),
            LaggedStartMap(ShowCreation, word_boxes[2:], lag_ratio=0.9),
            without_pop.set_opacity, 0.3,
            run_time=1,
        )
        self.wait()

        # Two reasonable fractions
        tp, fn, fp, tn = (
            word
            for word, box in zip(word_grid, word_boxes)
        )

        def create_fraction(m1, m2, scale_factor=0.75):
            result = VGroup(
                m1.copy(),
                TexMobject("\\quad \\over \\quad"),
                m1.copy(),
                TexMobject("+"),
                m2.copy()
            )
            result[0::2].scale(scale_factor)
            result[2:].arrange(RIGHT, buff=SMALL_BUFF)
            result[1].match_width(result[2:], stretch=True)
            result[1].next_to(result[2:], UP, SMALL_BUFF)
            result[0].next_to(result[1], UP, SMALL_BUFF)
            return result

        def fraction_anims(m1, m2, fraction):
            return [
                TransformFromCopy(m1, fraction[0]),
                TransformFromCopy(m1, fraction[2]),
                TransformFromCopy(m2, fraction[4]),
                GrowFromPoint(
                    fraction[1],
                    VGroup(m1, m2).get_center(),
                ),
                GrowFromPoint(
                    fraction[3],
                    VGroup(m1, m2).get_center(),
                ),
            ]

        frac1 = create_fraction(fp, tp)
        frac2 = create_fraction(fp, tn)
        fracs = VGroup(frac1, frac2)
        fracs.arrange(RIGHT, buff=3)
        fracs.to_edge(UP, buff=1.5)

        title.add(underline)
        fpr = TextMobject(
            "1\\% ", "F", "", "P", "", "R", "",
            font_size=72
        )
        fpr.add(Underline(fpr))
        fpr[-1].set_width(0)
        fpr.match_style(title)
        fpr.next_to(frac2, UP, MED_LARGE_BUFF)

        frac2.save_state()
        frac2.set_x(0)

        title.unlock_triangulation()
        self.play(
            FadeOut(arrow),
            LaggedStart(*fraction_anims(fp, tn, frac2))
        )
        self.wait(2)

        self.play(
            ReplacementTransform(title, fpr),
            Restore(frac2)
        )
        self.play(
            LaggedStartMap(Write, word_grid[:2], lag_ratio=0),
            LaggedStartMap(ShowCreation, word_boxes[:2], lag_ratio=0),
            with_pop.set_opacity, 0.2,
            run_time=1,
        )
        self.play(
            LaggedStart(*fraction_anims(fp, tp, frac1)),
            fn.set_opacity, 0.5,
            tn.set_opacity, 0.5,
        )
        self.wait()

        comment = TextMobject("What we actually want")
        comment.next_to(frac1, UP, buff=0.75)

        self.play(FadeIn(comment, 0.5 * UP))
        self.wait()

        # Prep for Bayes calculation
        right_brace = Brace(word_boxes[2], RIGHT, buff=SMALL_BUFF)
        left_brace = Brace(word_boxes[1], LEFT, buff=SMALL_BUFF)
        fpr.generate_target()
        fpr.target.scale(48 / 72)
        fpr.target.next_to(right_brace, RIGHT)
        fnr = TextMobject("10\\% FNR")
        fnr.next_to(left_brace, LEFT)
        VGroup(left_brace, right_brace, fnr).set_color(GREY_A)

        self.play(
            MoveToTarget(fpr),
            GrowFromCenter(left_brace),
            GrowFromCenter(right_brace),
            FadeIn(fnr),
            FadeOut(comment),
            FadeOut(fracs),
            fn.set_opacity, 1.0,
            tn.set_opacity, 1.0,
        )

        prior_title = TextMobject("Prior: 1 in 1,000", font_size=72)
        prior_title.to_edge(UP)
        self.play(FadeIn(prior_title, UP))
        self.wait()

        # Show population counts
        full_pop = VGroup(
            TextMobject("Imagine"),
            Integer(10000),
            TextMobject("People")
        )
        full_pop.arrange(RIGHT, aligned_edge=DOWN)
        full_pop.set_color(GREY_A)
        full_pop.next_to(prior_title, DOWN, MED_LARGE_BUFF)

        self.play(
            FadeIn(full_pop[0::2]),
            CountInFrom(full_pop[1], 0),
            FadeOut(with_pop),
            FadeOut(without_pop),
        )
        self.wait()

        def move_number_above_word(number, word, target_count, buff=MED_SMALL_BUFF, scene=self):
            mover = number.copy()
            mover.original_bottom = mover.get_bottom()
            start_count = number.get_value()
            scene.play(
                UpdateFromAlphaFunc(
                    mover,
                    lambda m, a, word=word, sc=start_count, tc=target_count, buff=buff: m.set_color(
                        interpolate_color(GREY_A, word.get_color(), a)
                    ).set_value(
                        interpolate(sc, tc, a),
                    ).move_to(
                        interpolate(
                            m.original_bottom,
                            word.get_top() + buff * UP,
                            a
                        ),
                        DOWN,
                    )
                )
            )
            return mover

        with_count = move_number_above_word(full_pop[1], group_titles[0], 10, buff=0.3)
        self.wait()
        without_count = move_number_above_word(full_pop[1], group_titles[1], 9990)
        self.wait()

        self.play(word_grid.shift, 0.25 * DOWN)
        tp_count = move_number_above_word(with_count, word_grid[0], 9, SMALL_BUFF)
        fn_count = move_number_above_word(with_count, word_grid[1], 1, SMALL_BUFF)
        self.wait()
        fp_count = move_number_above_word(without_count, word_grid[2], 100, SMALL_BUFF)
        tn_count = move_number_above_word(without_count, word_grid[3], 9890, buff=0.05)
        self.wait()

        faders = VGroup(
            with_count, without_count,
            group_titles,
            fpr, fnr,
            fn, tn, fn_count, tn_count,
        )
        braces = VGroup(left_brace, right_brace)
        self.play(faders.set_opacity, 0.3, FadeOut(braces))
        self.wait()

        # Show posterior
        prior_group = VGroup(prior_title, full_pop)
        prior_group.generate_target()
        prior_group.target.to_edge(LEFT)
        prior_group.target.shift(0.5 * DOWN)

        arrow = Vector(0.8 * RIGHT)
        arrow.next_to(prior_group.target[0], RIGHT)

        post_word = TextMobject("Posterior:", font_size=72)
        post_word.set_color(BLUE)
        post_word.next_to(arrow, RIGHT)
        post_word.align_to(prior_group.target[0][0][0], DOWN)
        post_frac = create_fraction(tp_count, fp_count, scale_factor=1)
        post_frac.next_to(post_word, RIGHT, MED_LARGE_BUFF)

        rhs = TexMobject("\\approx", "8.3\\%")
        rhs.next_to(post_frac, RIGHT)

        self.play(
            MoveToTarget(prior_group),
            GrowArrow(arrow),
            Write(post_word, run_time=1),
        )
        self.play(*fraction_anims(tp_count, fp_count, post_frac))
        self.wait()
        self.play(Write(rhs))
        self.wait()


class BayesFactorForCovidExample(Scene):
    def construct(self):
        # Titles
        titles = VGroup(
            TextMobject("Prior odds", color=YELLOW),
            TextMobject("Bayes factor", color=GREEN),
            TextMobject("Posterior odds", color=BLUE),
        )
        titles.scale(1.25)
        titles[0].shift(FRAME_WIDTH * LEFT / 3)
        titles[2].shift(FRAME_WIDTH * RIGHT / 3)
        titles.to_edge(UP)

        v_lines = VGroup(*(
            Line(UP, DOWN).set_height(FRAME_HEIGHT).move_to(
                FRAME_WIDTH * x * RIGHT / 6,
            )
            for x in (-1, 1)
        ))
        self.add(titles, v_lines)

        # Prior odds
        prior_odds = TextMobject(
            "1", "\\,:\\,", "999",
            tex_to_color_map={"1": YELLOW}
        )
        prior_odds.next_to(titles[0], DOWN, buff=1)

        population = Population(1000)
        population.set_width(FRAME_WIDTH / 5)
        population[0].set_color(YELLOW)
        population[0].next_to(population[1:], LEFT, MED_LARGE_BUFF)
        colon = TexMobject(":")
        colon.move_to(midpoint(population[0].get_right(), population[1:].get_left()))
        pop_ratio = VGroup(population[0], colon, population[1:])
        pop_ratio.next_to(prior_odds, DOWN, MED_LARGE_BUFF)

        self.play(
            FadeIn(prior_odds, shift=0.2 * DOWN, scale=1.2),
            FadeIn(pop_ratio, lag_ratio=0.01),
        )
        self.wait()

        # Bayes factor
        bf_lhs = TexMobject(
            """
            {
                P(+ \\,|\\, \\text{COVID})
                \\over
                P(+ \\,|\\, \\text{No COVID})
            }
            """,
            tex_to_color_map={
                "+": GREEN,
                "\\text{COVID}": YELLOW,
                "\\text{No COVID}": GREY_A,
            }
        )
        bf_lhs.next_to(titles[1], DOWN)
        bf_rhs = TexMobject(
            "= {90\\%", "\\over", "1\\%}",
            tex_to_color_map={
                "90\\%": GREEN_D,
                "1\\%": GREEN,
            }
        )
        bf = VGroup(bf_lhs, bf_rhs)
        bf.arrange(RIGHT)
        bf.set_width(0.9 * FRAME_WIDTH / 3)
        bf.next_to(titles[1], DOWN, MED_LARGE_BUFF)

        eq_90 = TexMobject("=", "90")
        eq_90.next_to(bf, DOWN, MED_LARGE_BUFF)
        eq_90[1].save_state()
        eq_90[1].replace(bf_rhs[1:], stretch=True)
        eq_90[1].set_opacity(0)
        eq_90[1].set_color(GREEN)

        self.play(
            FadeIn(bf_lhs, lag_ratio=0.1),
            FadeIn(bf_rhs[0::2], lag_ratio=0.1),
        )
        self.wait()
        self.play(Write(bf_rhs[1]))
        self.wait()
        self.play(Write(bf_rhs[3]))
        self.wait()
        self.play(
            TransformFromCopy(bf_rhs[0], eq_90[0]),
            Restore(eq_90[1])
        )
        self.wait()

        # Posterior
        post_odds = TexMobject("90", ":", "999")
        post_odds.match_x(titles[2])
        post_odds.match_y(prior_odds)

        arrow = Vector(DOWN)
        arrow.next_to(post_odds, DOWN)

        fraction = TexMobject(
            "{90", "\\over", "90", "+", "999}",
            "\\approx", "8.3\\%"
        )
        fraction.next_to(arrow, DOWN)

        prior_odds.unlock_triangulation()
        self.play(LaggedStart(
            TransformFromCopy(eq_90[1], post_odds[0]),
            TransformFromCopy(prior_odds[1:], post_odds[1:]),
            lag_ratio=0.4
        ))
        self.wait()
        self.play(
            GrowArrow(arrow),
            FadeIn(fraction, DOWN)
        )

        # Approximate
        approx1 = TexMobject("\\approx", "90", ":", "1,000")
        approx2 = TexMobject("\\approx", "9", ":", "100")
        approx3 = TexMobject("\\approx 9\\%")

        approx1.next_to(arrow, DOWN)
        approx2.move_to(approx1)
        arrow2 = arrow.copy()
        arrow2.next_to(approx2, DOWN)
        approx3.next_to(arrow2, DOWN)

        self.play(
            FadeOut(fraction, 0.5 * DOWN),
            FadeIn(approx1, 0.5 * DOWN),
        )
        self.wait()
        approx1.unlock_triangulation()
        self.play(
            ReplacementTransform(approx1, approx2)
        )
        self.wait()
        self.play(
            GrowArrow(arrow2),
            FadeIn(approx3, DOWN)
        )
        self.wait()


class WhyIsThisWrong(TeacherStudentsScene):
    def construct(self):
        # Ask question
        tweet = ImageMobject("twitter_covid_test_poll")
        tweet.replace(self.screen, dim_to_match=0)
        tweet.to_edge(UP)
        tweet.scale(0.9, about_edge=UP)

        self.add(tweet)
        self.student_says(
            "Bayes' rule says\\\\ 8.5\\%, right?",
            target_mode="hooray",
            student_index=1,
        )
        self.wait()
        self.play(
            PiCreatureSays(
                self.teacher,
                "Well...",
                bubble_kwargs={"height": 2, "width": 2},
                target_mode="hesitant",
            ),
            self.get_student_changes("confused", "erm", "pondering")
        )
        self.wait(3)

        # Highlight symptoms
        self.play(
            RemovePiCreatureBubble(self.students[1]),
            RemovePiCreatureBubble(self.teacher, target_mode="raise_right_hand"),
            tweet.move_to, self.hold_up_spot, DR,
            tweet.shift, RIGHT,
        )

        underline = Line((-1.3, 2.65), (2.1, 2.65))
        underline.shift(RIGHT)
        underline.set_stroke(RED, 3)

        self.play(
            ShowCreation(underline),
            self.teacher.look_at, underline,
            *(ApplyMethod(pi.change, "pondering", underline) for pi in self.students),
        )
        self.wait()

        # Change prior
        ineq = TextMobject("Prior > $\\frac{1}{1,000}$", font_size=72)
        ineq.next_to(tweet, LEFT, LARGE_BUFF)

        self.play(Write(ineq))
        self.look_at(ineq)
        self.wait()

        # More severe symptoms
        for pi in self.students:
            pi.generate_target()
            pi.target.change("sick")
            pi.target.set_color(SICKLY_GREEN)
            pi.target.look(DR)

        self.play(
            LaggedStartMap(MoveToTarget, self.students, lag_ratio=0.3),
            self.teacher.change, "erm"
        )

        clipboard = get_covid_clipboard()
        clipboard.to_corner(UL)

        self.play(
            FadeIn(clipboard, UP),
            FadeOut(ineq, UP),
            *(ApplyMethod(pi.look_at, clipboard) for pi in self.pi_creatures),
        )
        self.wait()

        percent = TexMobject("8.3 \\%", font_size=72)
        percent.next_to(clipboard, RIGHT, buff=0.6)
        percent_cross = Cross(percent, stroke_width=8)

        self.play(
            FadeIn(percent),
            self.teacher.change, "tease"
        )
        self.play(ShowCreation(percent_cross))
        self.wait()

        self.student_says(
            "What's the appropriate\\\\math here?",
            student_index=1,
            added_anims=[
                FadeOut(tweet),
                FadeOut(underline),
                self.teacher.change, "happy"
            ]
        )
        self.wait(2)


class TotalPopulationVsSymptomatic(Scene):
    def construct(self):
        # Titles
        v_line = Line(UP, DOWN).set_height(2 * FRAME_HEIGHT)
        v_line.to_edge(UP)
        self.add(v_line)

        titles = VGroup(
            TextMobject("Population"),
            TextMobject("Population", " \\emph{with symptoms}"),
        )
        titles[1][1].set_color(BLUE)
        for title, u in zip(titles, [-1, 1]):
            title.move_to(u * RIGHT * FRAME_WIDTH / 4)
        titles.to_edge(UP)

        self.add(titles[0])

        # Actual populations
        full_pop = VGroup(*(Dot() for x in range(10000)))
        full_pop.arrange_in_grid(
            buff=full_pop[0].get_width()
        )
        full_pop.set_width(FRAME_WIDTH / 2 - 1)
        full_pop.next_to(titles[0], DOWN)
        full_pop.to_edge(DOWN, buff=SMALL_BUFF)
        covid_pop = full_pop[:10]
        covid_pop.set_fill(YELLOW)
        covid_pop.save_state()
        covid_pop.scale(8, about_edge=UL)
        covid_pop.shift(DOWN)

        full_pop_words = VGroup(
            TextMobject("10 ", "with COVID", color=YELLOW),
            TextMobject("9990 ", "without COVID", color=GREY_B),
        )
        full_pop_words.arrange(RIGHT, buff=LARGE_BUFF)
        full_pop_words.scale(0.7)
        full_pop_words.next_to(full_pop, UP, SMALL_BUFF, LEFT)

        self.play(
            FadeIn(full_pop_words[0]),
            Write(covid_pop),
            run_time=1
        )
        self.play(
            FadeIn(full_pop_words[1]),
            ShowIncreasingSubsets(full_pop[10:]),
            Restore(covid_pop),
        )
        self.wait()

        # Mention symptoms
        self.play(
            TransformFromCopy(titles[0][0], titles[1][0]),
            FadeInFromPoint(titles[1][1], titles[0].get_center()),
        )
        self.wait()

        arrow = Vector(DOWN).next_to(titles[1][1], DOWN)
        arrow.set_color(BLUE)
        prop_ex = TexMobject("\\sim \\frac{1}{50}", "\\text{, say}")
        prop_ex[0].set_color(BLUE)
        prop_ex.next_to(arrow, DOWN)

        self.play(
            GrowArrow(arrow),
            FadeIn(prop_ex, DOWN)
        )
        self.wait()

        # Symptomatic population
        left_sym_pop = VGroup(*random.sample(list(full_pop[10:]), 200))
        sym_pop = left_sym_pop.copy()
        sym_pop.generate_target()
        buff = get_norm(full_pop[1].get_left() - full_pop[0].get_right())
        sym_pop.target.arrange_in_grid(buff=buff)
        sym_pop.target.set_width(3.5)
        sym_pop.target.match_x(titles[1])
        sym_pop.target.align_to(full_pop, UP)
        sym_pop.target.shift(DOWN)
        sym_pop.target.set_color(BLUE)

        sym_pop_label = TextMobject("$\\sim 200$", " without COVID")
        sym_pop_label.set_color(GREY_B)
        sym_pop_label.scale(0.7)
        sym_pop_label.next_to(sym_pop.target, UP, buff=0.2)

        self.play(
            sym_pop.set_color, BLUE,
            MoveToTarget(sym_pop, lag_ratio=0.01, run_time=2),
            prop_ex.to_edge, DOWN,
            FadeOut(arrow),
            Write(sym_pop_label),
        )
        self.wait()

        sym_covid_pop = covid_pop[:5].copy()
        sym_covid_pop.generate_target()
        sym_covid_pop.target.arrange(DOWN, buff=buff)
        sym_covid_pop.target.scale(
            sym_pop[0].get_height() / sym_covid_pop[0].get_height()
        )
        sym_covid_pop.target.next_to(sym_pop, LEFT, aligned_edge=UP)

        sym_covid_pop_label = TextMobject("5", " with COVID")
        sym_covid_pop_label.scale(0.7)
        sym_covid_pop_label.next_to(sym_covid_pop.target, UP, buff=0.2)
        sym_covid_pop_label.set_color(YELLOW)

        self.play(ShowCreationThenFadeAround(sym_pop_label))
        self.play(
            VGroup(sym_pop, sym_pop_label).to_edge, RIGHT,
            MoveToTarget(sym_covid_pop),
            FadeIn(sym_covid_pop_label),
        )
        self.wait()

        # Apply test
        left_movers = VGroup(
            full_pop, full_pop_words,
            titles[0], v_line,
        )
        right_movers = VGroup(
            titles[1],
            sym_covid_pop, sym_covid_pop_label,
            sym_pop, sym_pop_label,
        )
        v_line_copy = v_line.copy()

        left_vect = (FRAME_WIDTH + SMALL_BUFF) * LEFT / 2
        self.play(
            LaggedStartMap(
                ApplyMethod, left_movers,
                lambda m: (m.shift, left_vect),
                lag_ratio=0.05,
            ),
            ApplyMethod(
                right_movers.shift, left_vect,
                rate_func=squish_rate_func(smooth, 0.3, 1),
            ),
            FadeOut(prop_ex),
            run_time=2,
        )
        self.wait()

        # With test result
        right_title = TextMobject(
            "Population ", "\\emph{with symptoms}\\\\",
            "and a positive test result"
        )
        right_title.set_color_by_tex("symptoms", BLUE)
        right_title.set_color_by_tex("positive", GREEN)
        right_title.set_x(FRAME_WIDTH / 4)
        right_title.to_edge(UP)
        titles.add(right_title)

        self.play(
            ShowCreation(v_line_copy),
            FadeIn(right_title),
        )
        self.wait()

        right_vect = FRAME_WIDTH * RIGHT / 2

        pc_pop = sym_covid_pop.copy()
        pn_pop = VGroup(*random.sample(list(sym_pop), 2)).copy()

        pn_pop.generate_target()
        buff = get_norm(sym_pop[1].get_left() - sym_pop[0].get_right())
        pn_pop.target.arrange(DOWN, buff=buff)
        pn_pop.target.next_to(sym_pop_label, DOWN)
        pn_pop.target.shift(right_vect)
        pn_pop.target.scale(1.5, about_edge=UP)

        black_rect = BackgroundRectangle(pc_pop[-1], fill_opacity=1)
        black_rect.stretch(0.5, 1, about_edge=DOWN)
        pc_pop.add(black_rect)
        pc_pop.set_opacity(0)

        pc_pop_label = TextMobject("4.5 with COVID", color=YELLOW)
        pn_pop_label = TextMobject("~2 without COVID", color=GREY_B)
        labels = VGroup(pc_pop_label, pn_pop_label)
        labels.scale(0.7)
        labels.set_opacity(0)

        pc_pop_label.move_to(sym_covid_pop_label)
        pn_pop_label.move_to(sym_pop_label)

        def get_test_rects(mob):
            return VGroup(*(
                SurroundingRectangle(
                    part,
                    color=GREEN,
                    buff=buff / 2,
                    stroke_width=2,
                )
                for part in mob
            ))

        self.play(
            pc_pop_label.shift, right_vect,
            pc_pop_label.set_opacity, 1,
            pc_pop.shift, right_vect,
            pc_pop.set_opacity, 1,
            pc_pop.scale, 1.5, {"about_edge": UP}
        )
        pc_pop_rects = get_test_rects(pc_pop[:5])
        self.play(FadeIn(pc_pop_rects, lag_ratio=0.3))
        self.wait()
        self.play(
            pn_pop_label.shift, right_vect,
            pn_pop_label.set_opacity, 1,
            MoveToTarget(pn_pop),
        )
        pn_pop_rects = get_test_rects(pn_pop)
        self.play(FadeIn(pn_pop_rects, lag_ratio=0.3))
        self.wait()

        # Final fraction
        equation = TexMobject(
            "{4.5 \\over 4.5 + {2}} \\approx 69.2\\%",
            tex_to_color_map={
                "4.5": YELLOW,
                "{2}": GREY_B,
            }
        )
        equation.move_to(FRAME_WIDTH * RIGHT / 4)
        equation.to_edge(DOWN, buff=LARGE_BUFF)

        self.play(FadeIn(equation, lag_ratio=0.1))
        self.wait()

        # Zoom out
        frame = self.camera.frame

        self.play(
            frame.scale, 1.5, {"about_edge": UR},
            run_time=3,
        )
        self.wait()

        # Prepare population groups to move
        pop_groups = VGroup(
            VGroup(
                full_pop, full_pop_words,
            ),
            VGroup(
                sym_covid_pop, sym_covid_pop_label,
                sym_pop, sym_pop_label,
            ),
            VGroup(
                pc_pop, pc_pop_label, pc_pop_rects,
                pn_pop, pn_pop_label, pn_pop_rects,
                equation
            ),
        )
        pop_groups.generate_target()
        for group in pop_groups.target:
            group.scale(0.5, about_edge=DOWN)
            group.shift(4.5 * DOWN)

        pop_groups.target[0][0].set_opacity(0.5)

        h_line = Line(pop_groups.get_left(), pop_groups.get_right())
        h_line.next_to(pop_groups.target, UP)
        h_line.set_stroke(WHITE, 1)

        # Relevant odds labels
        def get_odds_label(n, k, n_color=YELLOW, k_color=GREY_B):
            result = VGroup(
                TextMobject("Odds = "),
                Integer(n, color=n_color, edge_to_fix=UR),
                TextMobject(":"),
                Integer(k, color=k_color, edge_to_fix=UL),
            )
            result.scale(1.5)
            result.arrange(RIGHT, buff=0.25)
            result[3].align_to(result[1], UP)
            return result

        odds_labels = VGroup(
            get_odds_label(1, 999),
            get_odds_label(25, 1000),
            get_odds_label(40, 90),
        )
        for label, title in zip(odds_labels, titles):
            label.move_to(title, UP)
            label.shift(2 * DOWN)

        odds_underlines = VGroup(*(
            Underline(label[1:])
            for label in odds_labels
        ))
        odds_arrows = VGroup(*(
            Arrow(o1.get_right(), o2.get_left())
            for o1, o2 in zip(odds_labels, odds_labels[1:])
        ))
        odds_arrows.set_fill(GREY_B)
        for arrow in odds_arrows:
            arrow.set_angle(0)

        self.play(
            MoveToTarget(pop_groups),
            FadeIn(odds_labels[0]),
            ShowCreation(h_line),
        )
        for i in (1, 2):
            self.play(
                FadeIn(odds_labels[i][0], RIGHT),
                FadeIn(odds_underlines[i], RIGHT),
                GrowArrow(odds_arrows[i - 1]),
            )
        self.wait()

        # Bayes factors
        bf_labels = VGroup(
            TextMobject(
                "Bayes factor for symptoms",
                tex_to_color_map={"for symptoms": BLUE}
            ),
            TextMobject(
                "Bayes factor positive test",
                tex_to_color_map={"positive test": GREEN}
            ),
        )
        for label, title in zip(bf_labels, titles[1:]):
            label.move_to(title, UP)
            label.shift(4.5 * DOWN)

        t2c = {
            "\\text{COVID}": YELLOW,
            "\\text{No COVID}": GREY_B,
            "\\text{Symp}": BLUE,
            "+": GREEN,
            "=": WHITE,
        }
        bf_equations = VGroup(
            TexMobject(
                """
                {P(\\text{Symp} \\,|\\, \\text{COVID})
                \\over
                P(\\text{Symp} \\,|\\, \\text{No COVID})}
                = {50\\% \\over 2\\%} = 25
                """,
                tex_to_color_map=t2c,
            ),
            TexMobject(
                """
                {P(+ \\,|\\, \\text{COVID}) \\over P(+ \\,|\\, \\text{No COVID})}
                = {90\\% \\over 1\\%} = 90
                """,
                tex_to_color_map=t2c,
            ),
        )
        for label, eq in zip(bf_labels, bf_equations):
            eq.scale(0.75)
            eq[-1].scale(2, about_edge=LEFT)
            eq.next_to(label, DOWN, buff=0.75)

        assumption_brace = Brace(bf_equations[0][-3:], DOWN)
        assumption_word = TextMobject("Assumption")
        assumption_word.next_to(assumption_brace, DOWN)

        self.play(
            Write(bf_labels[0]),
            FadeIn(bf_equations[0][:-3]),
        )
        self.wait()
        self.play(
            GrowFromCenter(assumption_brace),
            FadeIn(assumption_word, shift=0.2 * DOWN),
            FadeIn(bf_equations[0][-3:]),
        )
        self.wait()

        self.play(ShowCreationThenFadeOut(odds_underlines[0]))
        new_left_odds = get_odds_label(1, 1000)[1:]
        new_left_odds.move_to(odds_labels[0][1:], UL)
        approx = TexMobject("\\approx", font_size=72)
        approx.rotate(90 * DEGREES)
        approx.next_to(odds_labels[0][1:], DOWN, buff=0.5)
        self.play(
            FadeIn(approx, 0.25 * DOWN),
            odds_labels[0][1:].next_to, approx, DOWN, {"buff": 0.5},
            FadeIn(new_left_odds, 0.5 * DOWN),
            odds_arrows[0].scale, 0.7, {"about_edge": RIGHT},
        )
        self.wait()

        curr_odds = new_left_odds.copy()
        self.play(
            curr_odds.move_to, odds_labels[1][1:], UR,
            path_arc=-30 * DEGREES
        )
        self.play(ChangeDecimalToValue(curr_odds[0], 25))
        self.wait()

        new_odds = curr_odds.copy()
        new_odds[0].set_value(1)
        new_odds[2].set_value(40)
        self.play(
            FadeOut(curr_odds, 0.5 * UP),
            FadeIn(new_odds, 0.5 * UP),
        )
        curr_odds = new_odds
        self.wait()

        self.play(
            Write(bf_labels[1]),
            FadeIn(bf_equations[1]),
        )
        self.wait()

        mid_odds = curr_odds.copy()
        self.add(mid_odds)

        self.play(
            curr_odds.move_to, odds_labels[2][1:], UR,
            path_arc=-30 * DEGREES
        )
        self.play(
            ChangeDecimalToValue(curr_odds[0], 90)
        )
        self.wait()
        new_odds = curr_odds.copy()
        new_odds[0].set_value(9)
        new_odds[2].set_value(4)
        self.play(
            FadeOut(curr_odds, 0.5 * UP),
            FadeIn(new_odds, 0.5 * UP),
        )
        curr_odds = new_odds
        self.wait()

        # Posterior as a probability
        final_frac = TexMobject(
            "{{9} \\over {9} + {4}} \\approx 69.2\\%",
            tex_to_color_map={
                "{9}": YELLOW,
                "{4}": GREY_B,
            }
        )

        final_frac.next_to(odds_labels[2], DOWN, buff=0.4)
        self.play(FadeIn(final_frac, lag_ratio=0.2))
        self.wait()

        # Get rid of population
        self.play(
            LaggedStartMap(FadeOut, pop_groups, shift=DOWN, lag_ratio=0.3),
            FadeOut(h_line),
        )

        # Change symptom Bayes factor
        old_assumption = bf_equations[0][-3:]
        new_assumption = TexMobject("2")
        new_assumption.replace(old_assumption, 1)
        new_assumption.scale(0.8)
        new_assumption.set_color(BLUE)

        change_word = TextMobject("Change this", font_size=72)
        change_word.next_to(assumption_word, DOWN, buff=1.5)
        change_word.shift(LEFT)
        change_word.set_color(RED)
        change_arrow = Arrow(change_word.get_top(), assumption_word.get_bottom())
        change_arrow.match_color(change_word)

        self.play(
            Write(change_word, run_time=1),
            GrowArrow(change_arrow),
        )
        self.wait()
        self.play(
            FadeOut(old_assumption, shift=0.5 * UP),
            FadeIn(new_assumption, shift=0.5 * UP),
            assumption_brace.set_width,
            1.5 * new_assumption.get_width(), {"stretch": True},
            FadeOut(mid_odds),
            FadeOut(curr_odds),
            FadeOut(final_frac),
        )
        self.wait()

        # New odds calculation
        curr_odds = new_left_odds.copy()

        self.play(
            curr_odds.move_to, mid_odds, UP,
            curr_odds.shift, SMALL_BUFF * RIGHT,
            FadeOut(odds_underlines[1]),
            path_arc=-30 * DEGREES,
        )
        self.play(ChangeDecimalToValue(curr_odds[2], 500))
        self.wait()

        mid_odds = curr_odds.copy()
        self.add(mid_odds)

        self.play(
            curr_odds.move_to, odds_labels[2][1:], UR,
            curr_odds.shift, 0.35 * RIGHT,
            FadeOut(odds_underlines[2]),
            path_arc=-30 * DEGREES,
        )
        self.play(ChangeDecimalToValue(curr_odds[0], 90))
        self.wait()

        new_odds = curr_odds.copy()
        new_odds[0].set_value(9)
        new_odds[2].set_value(50)
        new_odds.move_to(curr_odds, LEFT)
        self.play(
            FadeIn(new_odds, shift=0.5 * UP),
            FadeOut(curr_odds, shift=0.5 * UP),
        )
        curr_odds = new_odds
        self.wait()

        # Prob calculation
        new_final_frac = TexMobject(
            "{{9} \\over {9} + {50}} \\approx 15.3\\%",
            tex_to_color_map={
                "{9}": YELLOW,
                "{50}": GREY_B,
            }
        )
        new_final_frac.replace(final_frac, 1)

        self.play(FadeIn(new_final_frac, lag_ratio=0.3))
        self.wait()


class ContrastTextbookAndRealWorld(Scene):
    def construct(self):
        pass


class TwoMissteps(Scene):
    def construct(self):
        words = VGroup(
            TextMobject(
                "Misstep 1: ",
                "Fail to consider the prevalence."
            ),
            TextMobject(
                "Misstep 2: ",
                "Assume prior = prevalence"
            ),
        )
        words[0][0].set_color(YELLOW)
        words[1][0].set_color(BLUE)
        words.scale(1.5)
        words.arrange(DOWN, buff=1, aligned_edge=LEFT)
        words.to_edge(LEFT)

        self.add(words)

        # Embed
        self.embed()
