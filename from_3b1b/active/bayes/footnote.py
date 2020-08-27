from manimlib.imports import *
from from_3b1b.active.bayes.part1 import BayesDiagram
from from_3b1b.active.bayes.part1 import LibrarianIcon
from from_3b1b.active.bayes.part1 import Person
from from_3b1b.active.bayes.part1 import RandomnessVsProportions

OUTPUT_DIRECTORY = "bayes/footnote"
TEX_TO_COLOR_MAP = {
    "A": YELLOW,
    "B": BLUE,
}
MID_COLOR = interpolate_color(BLUE_D, YELLOW, 0.5)
SICKLY_GREEN = "#9BBD37"


def get_bayes_formula():
    return TexMobject(
        "P(A|B) = {P(A)P(B|A) \\over P(B)}",
        tex_to_color_map={
            "A": YELLOW,
            "B": BLUE,
        },
        substrings_to_isolate=list("P(|)")
    )


# Scenes

class ThisIsAFootnote(TeacherStudentsScene):
    def construct(self):
        image = ImageMobject("bayes_thumbnail")
        image.set_height(2.5)
        rect = SurroundingRectangle(image, buff=0)
        rect.set_stroke(WHITE, 3)
        title = TextMobject("Bayes' theorem")
        title.match_width(image)
        title.next_to(image, UP)

        image_group = Group(rect, image, title)
        image_group.to_corner(UL)

        asterisk = TextMobject("*")
        asterisk.set_height(0.5)
        asterisk.set_stroke(BLACK, 3, background=True)
        asterisk.move_to(image.get_corner(UR), LEFT)

        formula = get_bayes_formula()
        formula.move_to(self.hold_up_spot, DOWN)

        pab = formula[:6]
        eq = formula[6]
        pa = formula[7:11]
        pba = formula[11:17]
        over = formula[17]
        pb = formula[18:23]

        # Show main video
        self.play(
            FadeInFromDown(image_group),
            self.get_student_changes(
                "pondering", "hooray", "tease",
                look_at_arg=image
            )
        )
        self.play(
            Write(asterisk),
            self.teacher.change, "speaking",
        )
        self.play(
            self.get_student_changes(
                "thinking", "erm", "thinking"
            )
        )
        self.wait(3)
        self.play(
            self.teacher.change, "raise_right_hand",
            FadeInFromDown(formula),
            self.get_student_changes(*3 * ["pondering"])
        )
        self.wait()

        # Rearrange
        parts = VGroup(
            pb, pab, eq, pa, pba,
        )
        parts.generate_target()
        parts.target.arrange(RIGHT, buff=SMALL_BUFF)
        parts.target.move_to(self.hold_up_spot)

        self.play(
            MoveToTarget(parts, path_arc=-30 * DEGREES),
            FadeOut(over),
            self.teacher.change, "pondering",
        )
        self.wait()

        # Move to top
        p_both = TexMobject(
            "P(A \\text{ and } B)",
            tex_to_color_map={"A": YELLOW, "B": BLUE},
        )
        eq2 = TexMobject("=")
        full_equation = VGroup(
            pb, pab, eq, p_both, eq2, pa, pba
        )
        full_equation.generate_target()
        full_equation.target.arrange(RIGHT, buff=SMALL_BUFF)
        full_equation.target.set_width(FRAME_WIDTH - 1)
        full_equation.target.center()
        full_equation.target.to_edge(UP)

        p_both.set_opacity(0)
        p_both.scale(0.2)
        p_both.move_to(eq)
        eq2.move_to(eq)

        self.play(
            MoveToTarget(full_equation),
            FadeOutAndShift(image_group, 2 * LEFT),
            FadeOutAndShift(asterisk, 2 * LEFT),
            self.teacher.look_at, 4 * UP,
            self.get_student_changes(
                "thinking", "erm", "confused",
                look_at_arg=4 * UP
            )
        )
        self.wait(2)


class ShowTwoPerspectives(Scene):
    CONFIG = {
        "pa": 1 / 3,
        "pb": 1 / 4,
        "p_both": 1 / 6,
        "diagram_height": 4,
    }

    def construct(self):
        # Ask about intersection
        formula = self.get_formula()

        venn_diagram = self.get_venn_diagram()
        venn_diagram.next_to(formula, DOWN, LARGE_BUFF)

        arrow = Arrow(
            formula[3].get_bottom(),
            venn_diagram.get_center(),
        )

        self.add(formula)
        self.play(
            formula[:3].set_opacity, 0.2,
            formula[-3:].set_opacity, 0.2,
        )
        for i in (0, 1):
            self.play(
                FadeIn(venn_diagram[0][i]),
                Write(venn_diagram[1][i]),
                run_time=1,
            )
        self.play(ShowCreation(arrow))
        self.wait()

        # Think with respect to A
        diagram1 = self.get_diagram1()
        diagram1.evidence_split.set_opacity(0)
        diagram1.hypothesis_split.set_opacity(1)
        diagram1.to_edge(RIGHT, LARGE_BUFF)
        diagram1.refresh_braces()

        d1_line = DashedLine(
            diagram1.h_rect.get_corner(UR),
            diagram1.h_rect.get_corner(DR),
        )
        d1_line.set_stroke(BLACK, 2)

        space_words = TextMobject(
            "Space of all\\\\possibilities"
        )
        space_words.match_width(diagram1.square)
        space_words.scale(0.9)
        space_words.move_to(diagram1.square)
        space_words.set_fill(BLACK)
        space_outline = SurroundingRectangle(diagram1.square, buff=0)
        space_outline.set_stroke(WHITE, 10)

        self.play(
            FadeOut(venn_diagram[0][1]),
            FadeOut(venn_diagram[1][1]),
            FadeOut(arrow),
            formula[4:6].set_opacity, 1,
        )
        diagram1.pa_label.update()
        self.play(
            FadeIn(diagram1.nh_rect),
            ReplacementTransform(
                venn_diagram[0][0],
                diagram1.h_rect,
            ),
            ReplacementTransform(
                venn_diagram[1][0],
                diagram1.pa_label.get_part_by_tex("A"),
            ),
            FadeIn(diagram1.h_brace),
            FadeIn(diagram1.pa_label[0]),
            FadeIn(diagram1.pa_label[2]),
            ShowCreation(d1_line),
        )
        self.add(diagram1.pa_label)
        self.wait()
        self.play(
            FadeIn(space_words),
            ShowCreation(space_outline),
        )
        self.play(
            FadeOut(space_words),
            FadeOut(space_outline),
        )
        self.wait()

        # Show B part
        B_rects = VGroup(diagram1.he_rect, diagram1.nhe_rect)
        B_rects.set_opacity(1)
        B_rects.set_sheen(0.2, UL)
        diagram1.nhe_rect.set_fill(BLUE_D)
        diagram1.he_rect.set_fill(MID_COLOR)
        diagram1.save_state()
        B_rects.stretch(0.001, 1, about_edge=DOWN)

        diagram1.he_brace.save_state()
        diagram1.he_brace.stretch(0.001, 1, about_edge=DOWN)

        self.add(diagram1.he_brace, diagram1.pba_label)
        self.add(diagram1, d1_line)
        self.play(
            Restore(diagram1),
            Restore(diagram1.he_brace),
            VFadeIn(diagram1.he_brace),
            VFadeIn(diagram1.pba_label),
            formula.pba.set_opacity, 1,
        )
        self.wait()

        # Show symmetric perspective
        diagram1_copy = diagram1.deepcopy()
        diagram2 = self.get_diagram2()
        d2_line = DashedLine(
            diagram2.b_rect.get_corner(UL),
            diagram2.b_rect.get_corner(UR),
        )
        d2_line.set_stroke(BLACK, 2)

        for rect in [diagram2.ba_rect, diagram2.nba_rect]:
            rect.save_state()
            rect.stretch(0.001, 0, about_edge=LEFT)

        self.play(
            diagram1_copy.move_to, diagram2,
            formula.pb.set_opacity, 1,
        )
        self.play(
            diagram1_copy.set_likelihood, self.pb,
            diagram1_copy.set_antilikelihood, self.pb,
            VFadeOut(diagram1_copy),
            FadeIn(diagram2),
            TransformFromCopy(formula.pb, diagram2.pb_label),
            FadeIn(diagram2.pb_brace),
            ShowCreation(d2_line),
        )
        self.wait()
        self.play(
            formula.pab.set_opacity, 1,
            formula.eq1.set_opacity, 1,
        )
        self.play(
            TransformFromCopy(formula.pab, diagram2.pab_label),
            FadeIn(diagram2.pab_brace),
            Restore(diagram2.ba_rect),
            Restore(diagram2.nba_rect),
        )
        self.wait()

    def get_formula(self):
        kw = {
            "tex_to_color_map": {
                "A": YELLOW,
                "B": BLUE,
            }
        }
        parts = VGroup(*[
            TexMobject(tex, **kw)
            for tex in [
                "P(B)", "P(A|B)", "=",
                "P(A \\text{ and } B)",
                "=", "P(A)", "P(B|A)",
            ]
        ])
        attrs = [
            "pb", "pab", "eq1", "p_both", "eq2", "pa", "pba"
        ]
        for attr, part in zip(attrs, parts):
            setattr(parts, attr, part)

        parts.arrange(RIGHT, buff=SMALL_BUFF),
        parts.set_width(FRAME_WIDTH - 1)
        parts.center().to_edge(UP)
        return parts

    def get_venn_diagram(self):
        c1 = Circle(
            radius=2.5,
            stroke_width=2,
            stroke_color=YELLOW,
            fill_opacity=0.5,
            fill_color=YELLOW,
        )
        c1.flip(RIGHT)
        c1.rotate(3 * TAU / 8)
        c2 = c1.copy()
        c2.set_color(BLUE)
        c1.shift(LEFT)
        c2.shift(RIGHT)
        circles = VGroup(c1, c2)

        titles = VGroup(
            TexMobject("A"),
            TexMobject("B"),
        )
        for title, circle, vect in zip(titles, circles, [UL, UR]):
            title.match_color(circle)
            title.scale(2)
            title.next_to(
                circle.get_boundary_point(vect),
                vect,
                buff=SMALL_BUFF
            )

        return VGroup(circles, titles)

    def get_diagram1(self):
        likelihood = (self.p_both / self.pa)
        antilikelihood = (self.pb - self.p_both) / (1 - self.pa)
        diagram = BayesDiagram(self.pa, likelihood, antilikelihood)
        diagram.set_height(self.diagram_height)

        diagram.add_brace_attrs()
        kw = {"tex_to_color_map": TEX_TO_COLOR_MAP}
        diagram.pa_label = TexMobject("P(A)", **kw)
        diagram.pba_label = TexMobject("P(B|A)", **kw)
        diagram.pa_label.add_updater(
            lambda m: m.next_to(diagram.h_brace, DOWN, SMALL_BUFF),
        )
        diagram.pba_label.add_updater(
            lambda m: m.next_to(diagram.he_brace, LEFT, SMALL_BUFF),
        )

        return diagram

    def get_diagram2(self):
        pa = self.pa
        pb = self.pb
        p_both = self.p_both
        square = Square()
        square.set_stroke(WHITE, 1)
        square.set_fill(LIGHT_GREY, 1)
        square.set_height(self.diagram_height)

        b_rect = square.copy()
        b_rect.stretch(pb, 1, about_edge=DOWN)
        b_rect.set_fill(BLUE)
        b_rect.set_sheen(0.2, UL)

        nb_rect = square.copy()
        nb_rect.stretch(1 - pb, 1, about_edge=UP)

        ba_rect = b_rect.copy()
        ba_rect.stretch((p_both / pb), 0, about_edge=LEFT)
        ba_rect.set_fill(MID_COLOR)

        nba_rect = nb_rect.copy()
        nba_rect.stretch((pa - p_both) / (1 - pb), 0, about_edge=LEFT)
        nba_rect.set_fill(YELLOW)

        result = VGroup(
            square.set_opacity(0),
            b_rect, nb_rect,
            ba_rect, nba_rect,
        )
        result.b_rect = b_rect
        result.nb_rect = nb_rect
        result.ba_rect = ba_rect
        result.nba_rect = nba_rect

        pb_brace = Brace(b_rect, LEFT, buff=SMALL_BUFF)
        pab_brace = Brace(ba_rect, DOWN, buff=SMALL_BUFF)
        kw = {"tex_to_color_map": TEX_TO_COLOR_MAP}
        pb_label = TexMobject("P(B)", **kw)
        pab_label = TexMobject("P(A|B)", **kw)
        pb_label.next_to(pb_brace, LEFT, SMALL_BUFF)
        pab_label.next_to(pab_brace, DOWN, SMALL_BUFF)

        result.pb_brace = pb_brace
        result.pab_brace = pab_brace
        result.pb_label = pb_label
        result.pab_label = pab_label

        VGroup(
            result,
            pb_brace, pab_brace,
            pb_label, pab_label,
        ).to_edge(LEFT)

        return result


class Rearrange(ShowTwoPerspectives):
    def construct(self):
        formula = self.get_formula()
        pb, pab, eq1, p_both, eq2, pa, pba = formula
        over = TexMobject("{\\qquad\\qquad \\over \\quad}")
        over.match_width(formula[:2])
        eq3 = eq1.copy()

        new_line = VGroup(
            formula.pb,
            formula.pab,
            eq3,
            formula.pa,
            formula.pba,
        )
        new_line.generate_target()
        new_line.target.arrange(RIGHT, buff=MED_SMALL_BUFF)
        new_line.target[0].shift(SMALL_BUFF * RIGHT)
        new_line.target[-1].shift(SMALL_BUFF * LEFT)
        new_line.target.center()
        eq3.set_opacity(0)

        eq1.generate_target()
        eq1.target.rotate(PI / 3)
        eq1.target.move_to(midpoint(
            p_both.get_corner(DL),
            new_line.target[0].get_corner(UR)
        ))
        eq2.generate_target()
        eq2.target.rotate(-PI / 3)
        eq2.target.move_to(midpoint(
            p_both.get_corner(DR),
            new_line.target[4].get_corner(UL)
        ))

        self.add(formula)
        self.play(
            MoveToTarget(new_line),
            MoveToTarget(eq1),
            MoveToTarget(eq2),
        )
        self.wait()

        over.move_to(VGroup(pa, pba))
        self.play(
            ApplyMethod(
                pb.next_to, over, DOWN,
                path_arc=30 * DEGREES,
            ),
            VGroup(pa, pba).next_to, over, UP,
            ShowCreation(over),
            FadeOut(VGroup(eq1, eq2))
        )
        self.wait(2)
        over.generate_target()
        over.target.next_to(eq3, LEFT)
        numer = VGroup(pb, pab)
        numer.generate_target()
        numer.target.arrange(RIGHT, buff=SMALL_BUFF)
        numer.target.next_to(over.target, UP)
        self.play(LaggedStart(
            MoveToTarget(over, path_arc=-30 * DEGREES),
            MoveToTarget(numer, path_arc=-30 * DEGREES),
            ApplyMethod(pa.next_to, over.target, DOWN),
            ApplyMethod(pba.next_to, eq3, RIGHT),
            lag_ratio=0.3,
        ))
        self.wait(2)

        # Numbers
        pb_brace = Brace(pb, UP, buff=SMALL_BUFF)
        pab_brace = Brace(pab, UP, buff=SMALL_BUFF)
        pa_brace = Brace(pa, DOWN, buff=SMALL_BUFF)

        pb_value = pb_brace.get_tex("(1/21)")
        pab_value = pab_brace.get_tex("(4/10)")
        pa_value = pa_brace.get_tex("(24/210)")

        braces = VGroup(pb_brace, pab_brace, pa_brace)
        values = VGroup(pb_value, pab_value, pa_value)

        self.play(
            LaggedStartMap(GrowFromCenter, braces, lag_ratio=0.3),
            LaggedStartMap(GrowFromCenter, values, lag_ratio=0.3),
            FadeOut(p_both),
        )
        self.wait()

        # Replace symbols
        mag = SVGMobject(file_name="magnifying_glass")
        mag.set_stroke(width=0)
        mag.set_fill(GREY, 1)
        mag.set_sheen(1, UL)

        Bs = VGroup(*[
            mob.get_part_by_tex("B")
            for mob in [pb, pab, pba]
        ])
        As = VGroup(*[
            mob.get_part_by_tex("A")
            for mob in [pab, pa, pba]
        ])
        books = VGroup(*[
            LibrarianIcon().replace(B, dim_to_match=0)
            for B in Bs
        ])
        books.set_color(YELLOW)

        mags = VGroup(*[
            mag.copy().replace(A)
            for A in As
        ])

        self.play(LaggedStart(*[
            ReplacementTransform(A, mag, path_arc=PI)
            for A, mag in zip(As, mags)
        ]))
        self.play(LaggedStart(*[
            ReplacementTransform(B, book, path_arc=PI)
            for B, book in zip(Bs, books)
        ]))
        self.wait()


class ClassLooking(TeacherStudentsScene):
    def construct(self):
        self.play(
            self.teacher.change, "pondering",
            self.get_student_changes(
                "pondering", "confused", "sassy",
                look_at_arg=self.screen,
            ),
        )
        self.wait(5)
        self.play(
            self.teacher.change, "raise_right_hand",
        )
        self.play(
            self.get_student_changes(
                "thinking", "pondering", "pondering",
                look_at_arg=self.hold_up_spot + 2 * UP,
            )
        )
        self.wait(3)


class LandscapeOfTools(TeacherStudentsScene):
    def construct(self):
        group = self.get_formulas()
        bayes = group[0].copy()

        self.play(
            self.teacher.change, "raise_right_hand",
            self.get_student_changes(
                *3 * ["confused"],
                look_at_arg=group,
            ),
            FadeInFromDown(bayes),
        )
        self.remove(bayes)
        self.play(
            ShowSubmobjectsOneByOne(group, remover=True),
            run_time=5
        )
        self.add(bayes)
        self.wait(2)

        bubble = self.students[0].get_bubble()
        self.add(bubble, bayes)
        self.play(
            bayes.move_to, bubble.get_bubble_center(),
            DrawBorderThenFill(bubble),
            self.teacher.change, "happy",
            self.get_student_changes(
                "pondering", "erm", "erm",
                look_at_arg=bubble,
            )
        )
        self.change_all_student_modes(
            "thinking", look_at_arg=bayes,
        )
        self.wait()
        self.play(
            FadeOut(bayes),
            bubble.set_fill, BLACK, 0.2,
            bubble.set_stroke, WHITE, 1,
            self.get_student_changes(
                "pleading", "guilty", "guilty",
            ),
            self.teacher.change, "hesitant"
        )
        self.wait(2)

    def get_formulas(self):
        group = VGroup(
            get_bayes_formula(),
            TexMobject(
                "P(X = k) = {\\lambda^k \\over k!}", "e^{-\\lambda}",
                tex_to_color_map={
                    "k": YELLOW,
                    "\\lambda": GREEN,
                }
            ),
            TexMobject(
                "{1 \\over \\sigma\\sqrt{2\\pi}}",
                "e^{\\frac{1}{2}\\left({(x - \\mu) \\over \\sigma}\\right)^2}",
                tex_to_color_map={
                    "\\sigma": GREEN,
                    "\\mu": BLUE,
                }
            ),
            TexMobject(
                "P(X = k) =", "\\left({n \\over k}\\right)", "p^k(1-p)^{n-k}",
                tex_to_color_map={
                    "\\over": BLACK,
                    "p": WHITE,
                    "k": YELLOW,
                    "n": BLUE,
                    "k": GREEN
                }
            ),
            TexMobject(
                "E[X + Y] = E[x] + E[y]"
            ),
            TexMobject(
                "\\text{Var}(X + Y) = \\text{Var}(x) + \\text{Var}(y) + 2\\text{Cov}(X, Y)"
            ),
            TexMobject(
                "H = \\sum_{i} -p_i \\log", "(p_i)",
                tex_to_color_map={
                    "p_i": YELLOW,
                }
            ),
            TexMobject(
                "{n \\choose k}",
                "{B(k + \\alpha, n -k + \\beta) \\over B(\\alpha, \\beta)}",
                tex_to_color_map={
                    "\\alpha": BLUE,
                    "\\beta": YELLOW,
                }
            ),
            TexMobject(
                "P(d) = \\log_{10}\\left(1 + {1 \\over d}\\right)",
                tex_to_color_map={"d": BLUE},
            ),
            TexMobject(
                "\\text{Cov}(X, Y) = \\sum_{i, j} p({x}_i, {y}_j)({x}_i - \\mu_{x})({y}_j - \\mu_{y})",
                tex_to_color_map={
                    "{x}": BLUE,
                    "{y}": RED,
                }
            ),
        )

        group.move_to(self.hold_up_spot, DOWN)
        group.shift_onto_screen()
        return group


class TemptingFormula(ShowTwoPerspectives, RandomnessVsProportions):
    def construct(self):
        # Show venn diagram
        kw = {
            "tex_to_color_map": TEX_TO_COLOR_MAP,
            "substrings_to_isolate": list("P()"),
        }
        formula = VGroup(
            TexMobject("P(A \\text{ and } B)", **kw),
            TexMobject("="),
            TexMobject("P(A)P(B)", "\\,", "\\,", **kw),
        )
        formula.arrange(RIGHT)
        formula.scale(1.5)
        formula.to_edge(UP)

        q_marks = TexMobject("???")[0]
        q_marks.scale(1.25)
        q_marks.next_to(formula[1], UP, SMALL_BUFF)

        formula.save_state()
        for part in formula:
            part.set_x(0)
        formula[1:].set_opacity(0)
        and_part = formula[0][2:5].copy()

        venn = self.get_venn_diagram()
        venn.next_to(formula, DOWN, LARGE_BUFF)

        self.add(formula)

        for i in 0, 1:
            self.play(
                DrawBorderThenFill(venn[0][i]),
                FadeIn(venn[1][i]),
            )
        self.play(
            and_part.scale, 0.5,
            and_part.move_to, venn,
        )
        self.remove(and_part)
        venn.add(and_part)
        self.add(venn)
        self.wait()
        self.play(Restore(formula))
        self.play(LaggedStartMap(FadeInFromDown, q_marks))

        # 1 in 4 heart disease related deaths
        people = VGroup(*[Person() for x in range(4)])
        people.arrange(RIGHT)
        people.set_height(2)
        people[0].set_color(RED)
        heart = SuitSymbol("hearts")
        heart.set_fill(BLACK)
        heart.set_height(0.25)
        heart.move_to(people[0])
        heart.shift(0.2 * UR)
        people[0].add(heart)

        grid = self.get_grid(4, 4, height=4)
        grid.to_corner(DL, buff=LARGE_BUFF)
        both_square = grid[0][0].copy()

        people.generate_target()
        people.target.set_height(both_square.get_height() - SMALL_BUFF)
        left_people = people.target.copy()
        self.label_grid(grid, left_people, people.target)
        pairs = self.get_grid_entries(grid, left_people, people.target)
        for pair in pairs:
            pair.generate_target()
            pair.restore()

        pair = pairs[0].target.copy()
        prob = TexMobject(
            "P(", "OO", ")", "= \\frac{1}{4} \\cdot \\frac{1}{4} = \\frac{1}{16}",
        )
        pair.move_to(prob[1])
        prob.submobjects[1] = pair
        prob.scale(1.5)
        prob.next_to(grid, RIGHT, LARGE_BUFF)

        self.play(
            FadeOut(venn),
            LaggedStartMap(FadeInFromDown, people),
        )
        self.play(WiggleOutThenIn(heart))
        self.wait()
        self.play(
            MoveToTarget(people),
            TransformFromCopy(people, left_people),
            Write(grid),
            FadeIn(prob[:3]),
            run_time=1,
        )
        self.add(both_square, pairs)
        self.play(
            LaggedStartMap(MoveToTarget, pairs, path_arc=30 * DEGREES),
            both_square.set_stroke, YELLOW, 5,
            both_square.set_fill, YELLOW, 0.25,
        )
        self.play(FadeIn(prob[3:]))
        self.wait()

        grid_group = VGroup(grid, people, left_people, both_square, pairs)

        # Coin flips
        ht_grid = self.get_grid(2, 2, height=3)
        ht_grid.move_to(grid)
        ht_labels = VGroup(TextMobject("H"), TextMobject("T"))
        ht_labels.set_submobject_colors_by_gradient(BLUE, RED)
        ht_labels.scale(2)
        left_ht_labels = ht_labels.copy()
        self.label_grid(ht_grid, left_ht_labels, ht_labels)
        ht_pairs = self.get_grid_entries(ht_grid, left_ht_labels, ht_labels)

        ht_both_square = ht_grid[1][1].copy()
        ht_both_square.set_stroke(YELLOW, 5)
        ht_both_square.set_fill(YELLOW, 0.25)

        ht_prob = TexMobject(
            "P(\\text{TT}) = \\frac{1}{2} \\cdot \\frac{1}{2} = \\frac{1}{4}",
            tex_to_color_map={"\\text{TT}": RED}
        )
        ht_prob.scale(1.5)
        ht_prob.next_to(ht_grid, RIGHT, LARGE_BUFF)

        ht_grid_group = VGroup(
            ht_grid, ht_labels, left_ht_labels,
            ht_both_square, ht_pairs,
        )

        self.play(
            FadeOut(grid_group),
            FadeOut(prob),
            FadeIn(ht_grid_group),
            FadeIn(ht_prob),
        )
        self.wait()

        # Dice throws
        dice_grid = self.get_grid(6, 6, height=4)
        dice_grid.set_stroke(WHITE, 1)
        dice_grid.move_to(grid)
        dice_labels = self.get_die_faces()
        dice_labels.set_height(0.5)
        left_dice_labels = dice_labels.copy()
        self.label_grid(dice_grid, left_dice_labels, dice_labels)
        dice_pairs = self.get_grid_entries(dice_grid, left_dice_labels, dice_labels)
        for pair in dice_pairs:
            pair.space_out_submobjects(0.9)
            pair.scale(0.75)

        dice_both_square = dice_grid[0][0].copy()
        dice_both_square.set_stroke(YELLOW, 5)
        dice_both_square.set_fill(YELLOW, 0.25)

        dice_prob = TexMobject(
            "P(", "OO", ") = \\frac{1}{6} \\cdot \\frac{1}{6} = \\frac{1}{36}",
        )
        pair = dice_pairs[0].copy()
        pair.scale(1.5)
        pair.move_to(dice_prob[1])
        dice_prob.submobjects[1] = pair
        dice_prob.scale(1.5)
        dice_prob.next_to(dice_grid, RIGHT, LARGE_BUFF)

        dice_grid_group = VGroup(
            dice_grid, dice_labels, left_dice_labels,
            dice_both_square, dice_pairs,
        )

        self.play(
            FadeOut(ht_grid_group),
            FadeOut(ht_prob),
            FadeIn(dice_grid_group),
            FadeIn(dice_prob),
        )
        self.wait()

        # Show correlation
        self.play(
            FadeOut(dice_grid_group),
            FadeOut(dice_prob),
            FadeIn(prob),
            FadeIn(grid_group),
        )
        self.wait()

        cross = Cross(prob[3])

        for pair in pairs:
            pair.add_updater(lambda m: m.move_to(m.square))
        for person, square in zip(people, grid[0]):
            person.square = square
            person.add_updater(lambda m: m.next_to(m.square, UP))

        row_rect = SurroundingRectangle(
            VGroup(grid[0], left_people[0]),
            buff=SMALL_BUFF
        )
        row_rect.set_stroke(RED, 3)

        self.play(ShowCreation(cross))
        self.play(
            FadeOut(prob),
            FadeOut(cross),
        )
        self.play(
            ShowCreation(row_rect)
        )
        self.wait()
        self.play(
            grid[0][0].stretch, 2, 0, {"about_edge": LEFT},
            grid[0][1:].stretch, 2 / 3, 0, {"about_edge": RIGHT},
            both_square.stretch, 2, 0, {"about_edge": LEFT},
            *[
                ApplyMethod(grid[i][0].stretch, 2 / 3, 0, {"about_edge": LEFT})
                for i in range(1, 4)
            ],
            *[
                ApplyMethod(grid[i][1:].stretch, 10 / 9, 0, {"about_edge": RIGHT})
                for i in range(1, 4)
            ],
        )
        self.wait()
        grid_group.add(row_rect)

        # Show correct formula
        cross = Cross(formula)
        cross.set_stroke(RED, 6)

        real_rhs = TexMobject("P(A)P(B|A)", **kw)
        real_rhs.scale(1.5)
        real_formula = VGroup(*formula[:2].copy(), real_rhs)
        real_formula.shift(1.5 * DOWN)
        real_rhs.next_to(real_formula[:2], RIGHT)

        real_rect = SurroundingRectangle(real_formula, buff=SMALL_BUFF)
        real_rect.set_stroke(GREEN)
        check = TexMobject("\\checkmark")
        check.set_color(GREEN)
        check.match_height(real_formula)
        check.next_to(real_rect, LEFT)

        small_cross = Cross(check)
        small_cross.match_style(cross)
        small_cross.next_to(formula, LEFT)

        self.play(
            ShowCreationThenFadeAround(formula),
            FadeOut(q_marks),
        )
        self.play(ShowCreation(cross))
        self.wait()
        self.play(
            TransformFromCopy(formula, real_formula),
            grid_group.scale, 0.7,
            grid_group.to_corner, DL,
        )
        self.play(
            FadeIn(real_rect),
            FadeInFrom(check, RIGHT),
        )
        self.wait()

        # Show other grid
        ht_grid_group.scale(0.7)
        ht_grid_group.next_to(grid_group, RIGHT, buff=1.5)
        dice_grid_group.scale(0.7)
        dice_grid_group.next_to(ht_grid_group, RIGHT, buff=1.5)

        Bs = VGroup(formula[2][4:], real_formula[2][4:])
        B_rect = SurroundingRectangle(
            Bs,
            stroke_color=BLUE,
            # buff=SMALL_BUFF,
            buff=0,
        )
        B_rect.scale(1.1, about_edge=LEFT)
        B_rect.set_fill(BLUE, 0.5)
        B_rect.set_stroke(width=0)

        big_rect = SurroundingRectangle(
            VGroup(ht_grid_group, dice_grid_group),
            buff=MED_LARGE_BUFF,
            color=BLUE,
        )
        # B_rect.points[0] += 0.2 * RIGHT
        # B_rect.points[-1] += 0.2 * RIGHT
        # B_rect.points[3] += 0.2 * LEFT
        # B_rect.points[4] += 0.2 * LEFT
        # B_rect.make_jagged()

        self.play(FadeIn(ht_grid_group))
        self.play(FadeIn(dice_grid_group))
        self.wait()
        self.add(B_rect, Bs.copy())
        self.play(
            FadeIn(B_rect),
            FadeIn(big_rect),
            Transform(cross, small_cross),
            FadeOut(real_rect),
        )
        self.wait()

    def get_grid(self, n, m, height=4):
        grid = VGroup(*[
            VGroup(
                *[Square() for x in range(m)]
            ).arrange(RIGHT, buff=0)
            for y in range(n)
        ]).arrange(DOWN, buff=0)
        grid.set_height(height)
        grid.set_stroke(WHITE, 2)
        return grid

    def label_grid(self, grid, row_labels, col_labels):
        for label, row in zip(row_labels, grid):
            label.next_to(row, LEFT)

        for label, square in zip(col_labels, grid[0]):
            label.next_to(square, UP)

    def get_grid_entries(self, grid, row_labels, col_labels):
        pairs = VGroup()
        for i, p1 in enumerate(row_labels):
            for j, p2 in enumerate(col_labels):
                pair = VGroup(p1, p2).copy()
                pair.save_state()
                pair.scale(0.6)
                pair.arrange(RIGHT, buff=0.05)
                pair.square = grid[i][j]
                pair.move_to(grid[i][j])
                pairs.add(pair)
        return pairs


class DiseaseBayes(Scene):
    def construct(self):
        formula = TexMobject(
            "P(D | +) = {P(D) P(+ | D) \\over P(+)}",
            tex_to_color_map={
                "D": YELLOW,
                "+": BLUE,
            },
            substrings_to_isolate=list("P(|)=")
        )
        formula.scale(2.5)

        Ds = formula.get_parts_by_tex("D")
        for D in Ds:
            index = formula.index_of_part(D)
            pi = Randolph()
            pi.change("sick")
            pi.set_color(SICKLY_GREEN)
            pi.replace(D)
            formula.submobjects[index] = pi
            pi.get_tex_string = lambda: ""

        lhs = formula[:6]
        lhs.save_state()
        lhs.center()

        sicky = lhs[2]

        sick_words = TextMobject(
            "You are sick",
            tex_to_color_map={
                "sick": SICKLY_GREEN,
            },
        )
        sick_words.scale(1.5)
        sick_words.next_to(sicky, UP, 2 * LARGE_BUFF)
        positive_words = TextMobject("Positive test result")
        positive_words.scale(1.5)
        positive_words.set_color(BLUE)
        positive_words.next_to(lhs[4], DOWN, 2 * LARGE_BUFF)

        sick_arrow = Arrow(sicky.get_top(), sick_words.get_bottom())
        positive_arrow = Arrow(lhs[4].get_bottom(), positive_words.get_top())

        arrow_groups = VGroup(
            sick_words, sick_arrow,
            positive_words, positive_arrow,
        )

        sicky.save_state()
        sicky.change("happy")
        sicky.set_color(BLUE)

        self.play(FadeInFromDown(lhs))
        self.play(
            Restore(sicky),
            GrowArrow(sick_arrow),
            FadeInFromDown(sick_words),
        )
        self.play(
            GrowArrow(positive_arrow),
            FadeInFrom(positive_words, UP),
        )
        self.wait(2)
        self.play(
            Restore(lhs),
            MaintainPositionRelativeTo(arrow_groups, lhs),
            FadeIn(formula[6]),
        )

        # Prior
        def get_formula_slice(*indices):
            return VGroup(*[formula[i] for i in indices])

        self.play(
            TransformFromCopy(
                get_formula_slice(0, 1, 2, 5),
                get_formula_slice(8, 9, 10, 11),
            ),
        )

        # Likelihood
        lhs_copy = formula[:6].copy()
        likelihood = formula[12:18]
        run_time = 1
        self.play(
            lhs_copy.next_to, likelihood, UP,
            run_time=run_time,
        )
        self.play(
            Swap(lhs_copy[2], lhs_copy[4]),
            run_time=run_time,
        )
        self.play(
            lhs_copy.move_to, likelihood,
            run_time=run_time,
        )

        # Evidence
        self.play(
            ShowCreation(formula.get_part_by_tex("\\over")),
            TransformFromCopy(
                get_formula_slice(12, 13, 14, 17),
                get_formula_slice(19, 20, 21, 22),
            ),
        )
        self.wait()


class EndScreen(Scene):
    CONFIG = {
        "camera_config": {
            "background_color": DARKER_GREY
        }
    }

    def construct(self):
        width = (475 / 1280) * FRAME_WIDTH
        height = width * (323 / 575)
        video_rect = Rectangle(
            width=width,
            height=height,
            fill_color=BLACK,
            fill_opacity=1,
        )
        video_rect.shift(UP)

        date = TextMobject(
            "Solution will be\\\\"
            "posted", "1/20/19",
        )
        date[1].set_color(YELLOW)
        date.set_width(video_rect.get_width() - 2 * MED_SMALL_BUFF)
        date.move_to(video_rect)

        handle = TextMobject("@3blue1brown")
        handle.next_to(video_rect, DOWN, MED_LARGE_BUFF)

        self.add(video_rect, handle)
        self.add(AnimatedBoundary(video_rect))
        self.wait(20)
