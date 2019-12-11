from manimlib.imports import *

OUTPUT_DIRECTORY = "bayes"

HYPOTHESIS_COLOR = YELLOW
NOT_HYPOTHESIS_COLOR = GREY
EVIDENCE_COLOR1 = BLUE_C
EVIDENCE_COLOR2 = BLUE_D
NOT_EVIDENCE_COLOR1 = RED
NOT_EVIDENCE_COLOR2 = RED_E
# NOT_EVIDENCE_COLOR1 = PURPLE
# NOT_EVIDENCE_COLOR2 = PURPLE_D

#


def get_bayes_formula(expand_denominator=False):
    t2c = {
        "{H}": HYPOTHESIS_COLOR,
        "{\\neg H}": NOT_HYPOTHESIS_COLOR,
        "{E}": EVIDENCE_COLOR1,
    }
    substrings_to_isolate = ["P", "\\over", "=", "\\cdot", "+"]

    tex = "P({H} | {E}) = {P({H}) \\cdot P({E} | {H}) \\over "
    if expand_denominator:
        tex += "P({H}) \\cdot P({E} | {H}) + P({\\neg H}) \\cdot P({E} | {\\neg H})}"
    else:
        tex += "P({E})}"

    formula = TexMobject(
        tex,
        tex_to_color_map=t2c,
        substrings_to_isolate=substrings_to_isolate,
    )

    formula.posterior = formula[:6]
    formula.prior = formula[8:12]
    formula.likelihood = formula[13:19]

    if expand_denominator:
        pass
        formula.denom_prior = formula[20:24]
        formula.denom_likelihood = formula[25:31]
        formula.denom_anti_prior = formula[32:36]
        formula.denom_anti_likelihood = formula[37:42]
    else:
        formula.p_evidence = formula[20:]

    return formula


class BayesDiagram(VGroup):
    CONFIG = {
        "height": 2,
        "square_style": {
            "fill_color": DARK_GREY,
            "fill_opacity": 1,
            "stroke_color": WHITE,
            "stroke_width": 2,
        },
        "rect_style": {
            "stroke_color": WHITE,
            "stroke_width": 1,
            "fill_opacity": 1,
        },
        "hypothesis_color": HYPOTHESIS_COLOR,
        "not_hypothesis_color": NOT_HYPOTHESIS_COLOR,
        "evidence_color1": EVIDENCE_COLOR1,
        "evidence_color2": EVIDENCE_COLOR2,
        "not_evidence_color1": NOT_EVIDENCE_COLOR1,
        "not_evidence_color2": NOT_EVIDENCE_COLOR2,
        "prior_rect_direction": DOWN,
    }

    def __init__(self, prior, likelihood, antilikelihood, **kwargs):
        super().__init__(**kwargs)
        square = Square(side_length=self.height)
        square.set_style(**self.square_style)

        # Create all rectangles
        h_rect, nh_rect, he_rect, nhe_rect, hne_rect, nhne_rect = [
            square.copy().set_style(**self.rect_style)
            for x in range(6)
        ]

        # Add as attributes
        self.square = square
        self.h_rect = h_rect  # Hypothesis
        self.nh_rect = nh_rect  # Not hypothesis
        self.he_rect = he_rect  # Hypothesis and evidence
        self.hne_rect = hne_rect  # Hypothesis and not evidence
        self.nhe_rect = nhe_rect  # Not hypothesis and evidence
        self.nhne_rect = nhne_rect  # Not hypothesis and not evidence

        # Stretch the rectangles
        for rect in h_rect, he_rect, hne_rect:
            rect.stretch(prior, 0, about_edge=LEFT)
        for rect in nh_rect, nhe_rect, nhne_rect:
            rect.stretch(1 - prior, 0, about_edge=RIGHT)

        he_rect.stretch(likelihood, 1, about_edge=DOWN)
        hne_rect.stretch(1 - likelihood, 1, about_edge=UP)
        nhe_rect.stretch(antilikelihood, 1, about_edge=DOWN)
        nhne_rect.stretch(1 - antilikelihood, 1, about_edge=UP)

        # Color the rectangles
        h_rect.set_fill(self.hypothesis_color)
        nh_rect.set_fill(self.not_hypothesis_color)
        he_rect.set_fill(self.evidence_color1)
        hne_rect.set_fill(self.not_evidence_color1)
        nhe_rect.set_fill(self.evidence_color2)
        nhne_rect.set_fill(self.not_evidence_color2)

        # Add them
        self.hypothesis_split = VGroup(h_rect, nh_rect)
        self.evidence_split = VGroup(he_rect, hne_rect, nhe_rect, nhne_rect)

        # Don't add hypothesis split by default
        self.add(self.square, self.hypothesis_split, self.evidence_split)
        self.square.set_opacity(0)
        self.hypothesis_split.set_opacity(0)

    def add_brace_attrs(self, buff=SMALL_BUFF):
        braces = self.braces = self.create_braces(buff)
        self.braces_buff = buff
        attrs = [
            "h_brace",
            "nh_brace",
            "he_brace",
            "hne_brace",
            "nhe_brace",
            "nhne_brace",
        ]
        for brace, attr in zip(braces, attrs):
            setattr(self, attr, brace)
        return self

    def create_braces(self, buff=SMALL_BUFF):
        kw = {"buff": buff}
        return VGroup(
            Brace(self.h_rect, self.prior_rect_direction, **kw),
            Brace(self.nh_rect, self.prior_rect_direction, **kw),
            Brace(self.he_rect, LEFT, **kw),
            Brace(self.hne_rect, LEFT, **kw),
            Brace(self.nhe_rect, RIGHT, **kw),
            Brace(self.nhne_rect, RIGHT, **kw),
        )

    def refresh_braces(self):
        if hasattr(self, "braces"):
            self.braces.become(
                self.create_braces(self.braces_buff)
            )
        return self

    def set_prior(self, new_prior):
        p = new_prior
        q = 1 - p
        full_width = self.square.get_width()

        left_rects = [self.h_rect, self.he_rect, self.hne_rect]
        right_rects = [self.nh_rect, self.nhe_rect, self.nhne_rect]

        for group, vect, value in [(left_rects, LEFT, p), (right_rects, RIGHT, q)]:
            for rect in group:
                rect.set_width(
                    value * full_width,
                    stretch=True,
                    about_edge=vect,
                )

        self.refresh_braces()
        return self

    def general_set_likelihood(self, new_likelihood, low_rect, high_rect):
        height = self.square.get_height()

        low_rect.set_height(
            new_likelihood * height,
            stretch=True,
            about_edge=DOWN,
        )
        high_rect.set_height(
            (1 - new_likelihood) * height,
            stretch=True,
            about_edge=UP,
        )
        self.refresh_braces()
        return self

    def set_likelihood(self, new_likelihood):
        self.general_set_likelihood(
            new_likelihood,
            self.he_rect,
            self.hne_rect,
        )
        return self

    def set_antilikelihood(self, new_antilikelihood):
        self.general_set_likelihood(
            new_antilikelihood,
            self.nhe_rect,
            self.nhne_rect,
        )
        return self

    def copy(self):
        return self.deepcopy()


class ProbabilityBar(VGroup):
    CONFIG = {
        "color1": BLUE_D,
        "color2": GREY_BROWN,
        "height": 0.5,
        "width": 6,
        "rect_style": {
            "stroke_width": 1,
            "stroke_color": WHITE,
            "fill_opacity": 1,
        },
        "include_braces": True,
        "brace_direction": UP,
        "include_percentages": True,
        "percentage_background_stroke_width": 5,
    }

    def __init__(self, p=0.5, **kwargs):
        super().__init__(**kwargs)
        self.add_backbone()
        self.add_p_tracker(p)
        self.add_bars()
        if self.include_braces:
            self.braces = always_redraw(lambda: self.get_braces())
            self.add(self.braces)
        if self.include_percentages:
            self.percentages = always_redraw(lambda: self.get_percentages())
            self.add(self.percentages)

    def add_backbone(self):
        backbone = Line()
        backbone.set_opacity(0)
        backbone.set_width(self.width)
        self.backbone = backbone
        self.add(backbone)

    def add_p_tracker(self, p):
        self.p_tracker = ValueTracker(p)

    def add_bars(self):
        bars = VGroup(Rectangle(), Rectangle())
        bars.set_height(self.height)
        colors = [self.color1, self.color2]
        for bar, color in zip(bars, colors):
            bar.set_style(**self.rect_style)
            bar.set_fill(color=color)

        bars.add_updater(self.update_bars)
        self.bars = bars
        self.add(bars)

    def update_bars(self, bars):
        vects = [LEFT, RIGHT]
        p = self.p_tracker.get_value()
        values = [p, 1 - p]
        total_width = self.backbone.get_width()
        for bar, vect, value in zip(bars, vects, values):
            bar.set_width(value * total_width, stretch=True)
            bar.move_to(self.backbone, vect)
        return bars

    def get_braces(self):
        return VGroup(*[
            Brace(
                bar,
                self.brace_direction,
                min_num_quads=1,
                buff=SMALL_BUFF,
            )
            for bar in self.bars
        ])

    def get_percentages(self):
        p = self.p_tracker.get_value()
        labels = VGroup(*[
            Integer(value, unit="\\%")
            for value in [
                np.floor(p * 100),
                100 - np.floor(p * 100),
            ]
        ])
        for label, bar in zip(labels, self.bars):
            label.set_height(0.75 * bar.get_height())
            min_width = 0.75 * bar.get_width()
            if label.get_width() > min_width:
                label.set_width(min_width)
            label.move_to(bar)
            label.set_stroke(
                BLACK,
                self.percentage_background_stroke_width,
                background=True
            )
        return labels

    def add_icons(self, *icons, buff=SMALL_BUFF):
        if hasattr(self, "braces"):
            refs = self.braces
        else:
            refs = self.bars

        for icon, ref in zip(icons, refs):
            icon.ref = ref
            icon.add_updater(lambda i: i.next_to(
                i.ref,
                self.brace_direction,
                buff=buff
            ))
        self.icons = VGroup(*icons)
        self.add(self.icons)


class Steve(SVGMobject):
    CONFIG = {
        "file_name": "steve",
        "fill_color": GREY,
        "sheen_factor": 0.5,
        "sheen_direction": UL,
        "stroke_width": 0,
        "height": 3,
        "include_name": True,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.include_name:
            self.add_name()

    def add_name(self):
        self.name = TextMobject("Steve")
        self.name.match_width(self)
        self.name.next_to(self, DOWN, SMALL_BUFF)
        self.add(self.name)


class LibrarianIcon(SVGMobject):
    CONFIG = {
        "file_name": "book",
        "stroke_width": 0,
        "fill_color": LIGHT_GREY,
        "sheen_factor": 0.5,
        "sheen_direction": UL,
        "height": 0.75,
    }


class FarmerIcon(SVGMobject):
    CONFIG = {
        "file_name": "farming",
        "stroke_width": 0,
        "fill_color": GREEN_E,
        "sheen_factor": 0.5,
        "sheen_direction": UL,
        "height": 1.5,
    }


class PitchforkIcon(SVGMobject):
    CONFIG = {
        "file_name": "pitch_fork_and_roll",
        "stroke_width": 0,
        "fill_color": LIGHT_GREY,
        "sheen_factor": 0.5,
        "sheen_direction": UL,
        "height": 1.5,
    }


class Person(SVGMobject):
    CONFIG = {
        "file_name": "person",
        "height": 1.5,
        "stroke_width": 0,
        "fill_opacity": 1,
        "fill_color": LIGHT_GREY,
    }


class Librarian(Person):
    CONFIG = {
        "IconClass": LibrarianIcon,
        "icon_style": {
            "background_stroke_width": 5,
            "background_stroke_color": BLACK,
        },
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        icon = self.IconClass()
        icon.set_style(**self.icon_style)
        icon.match_width(self)
        icon.move_to(self.get_corner(DR), DOWN)
        self.add(icon)


class Farmer(Librarian):
    CONFIG = {
        "IconClass": FarmerIcon,
        "icon_style": {
            "background_stroke_width": 2,
        },
        "fill_color": GREEN,
    }


# Scenes


class Test(Scene):
    def construct(self):
        icon = FarmerIcon()
        icon.scale(2)
        self.add(icon)
        # self.add(get_submobject_index_labels(icon))


# class FullFormulaIndices(Scene):
#     def construct(self):
#         formula = get_bayes_formula(expand_denominator=True)
#         formula.set_width(FRAME_WIDTH - 1)
#         self.add(formula)
#         self.add(get_submobject_index_labels(formula))


class IntroduceFormula(Scene):
    def construct(self):
        formula = get_bayes_formula()
        formula.set_width(FRAME_WIDTH - 1)

        def get_formula_slice(*indices):
            return VGroup(*[formula[i] for i in indices])

        H_label = formula.get_part_by_tex("{H}")
        E_label = formula.get_part_by_tex("{E}")

        hyp_label = TextMobject("Hypothesis")
        hyp_label.set_color(HYPOTHESIS_COLOR)
        hyp_label.next_to(H_label, UP, LARGE_BUFF)

        evid_label = TextMobject("Evidence")
        evid_label.set_color(EVIDENCE_COLOR1)
        evid_label.next_to(E_label, DOWN, LARGE_BUFF)

        hyp_arrow = Arrow(hyp_label.get_bottom(), H_label.get_top(), buff=SMALL_BUFF)
        evid_arrow = Arrow(evid_label.get_top(), E_label.get_bottom(), buff=SMALL_BUFF)

        self.add(formula[:6])
        # self.add(get_submobject_index_labels(formula))
        # return
        self.play(
            FadeInFrom(hyp_label, DOWN),
            GrowArrow(hyp_arrow),
            FadeInFrom(evid_label, UP),
            GrowArrow(evid_arrow),
        )
        self.wait()

        # Prior
        self.play(
            ShowCreation(formula.get_part_by_tex("=")),
            TransformFromCopy(
                get_formula_slice(0, 1, 2, 5),
                get_formula_slice(8, 9, 10, 11),
            ),
        )
        self.wait()

        # Likelihood
        lhs_copy = formula[:6].copy()
        likelihood = formula[13:19]
        run_time = 1
        self.play(
            lhs_copy.next_to, likelihood, UP,
            DrawBorderThenFill(formula.get_part_by_tex("\\cdot")),
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
        self.wait()

        # Evidence
        self.play(
            ShowCreation(formula.get_part_by_tex("\\over")),
            TransformFromCopy(
                get_formula_slice(0, 1, 4, 5),
                get_formula_slice(20, 21, 22, 23),
            ),
        )
        self.wait()


class StateGoal(PiCreatureScene):
    CONFIG = {
        "default_pi_creature_kwargs": {
            "color": BLUE_B,
            "height": 2,
        },

    }

    def construct(self):
        you = self.pi_creature
        line = NumberLine(
            x_min=-2,
            x_max=12,
            include_tip=True
        )
        line.to_edge(DOWN, buff=1.5)
        line.to_edge(LEFT, buff=-0.5)

        you.next_to(line.n2p(0), UP)

        you_label = TextMobject("you")
        you_label.next_to(you, RIGHT, MED_LARGE_BUFF)
        you_arrow = Arrow(you_label.get_left(), you.get_right() + 0.5 * LEFT, buff=0.1)

        now_label = TextMobject("Now")
        later_label = TextMobject("Later")
        now_label.next_to(line.n2p(0), DOWN)
        later_label.next_to(line.n2p(10), DOWN)

        self.add(line, now_label)
        self.add(you)
        self.play(
            FadeInFrom(you_label, LEFT),
            GrowArrow(you_arrow),
            you.change, "pondering",
        )
        self.wait()
        you_label.add(you_arrow)
        self.play(
            you.change, "horrified",
            you.look, DOWN,
            you.next_to, line.n2p(10), UP,
            MaintainPositionRelativeTo(you_label, you),
            FadeInFromPoint(later_label, now_label.get_center()),
        )
        self.wait()

        bubble = you.get_bubble(
            height=4,
            width=6,
        )
        bubble.set_fill(opacity=0)
        formula = get_bayes_formula()
        bubble.position_mobject_inside(formula)

        self.play(
            you.change, "confused", bubble,
            ShowCreation(bubble),
        )
        self.play(FadeIn(formula))
        self.play(you.change, "hooray", formula)
        self.wait(2)

        # Levels of understanding
        # Turn bubble into level points
        level_points = VGroup(*[bubble.copy() for x in range(3)])
        for n, point in enumerate(level_points):
            point.set_width(0.5)
            point.set_height(0.5, stretch=True)
            point.add(*[
                point[-1].copy().scale(1.2**k)
                for k in range(1, n + 1)
            ])
            point[:3].scale(1.2**n, about_point=point[3].get_center())
            point.set_stroke(width=2)
            point.set_fill(opacity=0)
        level_points.arrange(DOWN, buff=LARGE_BUFF)

        title = TextMobject("Levels of understanding")
        title.scale(1.5)
        title.to_corner(UL)
        underline = Line()
        underline.match_width(title)
        underline.move_to(title, DOWN)
        title.add(underline)

        level_points.next_to(title, DOWN, buff=1.5)
        level_points.to_edge(LEFT)
        level_points.set_submobject_colors_by_gradient(GREEN, YELLOW, RED)

        self.remove(bubble)
        self.play(
            formula.to_corner, UR,
            Uncreate(line),
            FadeOutAndShift(now_label, DOWN),
            FadeOutAndShift(later_label, DOWN),
            FadeOut(you_label),
            FadeOut(you_arrow),
            FadeOut(you),
            *[
                ReplacementTransform(bubble.copy(), point)
                for point in level_points
            ],
        )
        self.play(Write(title, run_time=1))
        self.wait()

        # Write level 1
        level_labels = VGroup(
            TextMobject("What is it saying?"),
            TextMobject("Why is it true?"),
            TextMobject("When is it useful?"),
        )
        for lp, ll in zip(level_points, level_labels):
            ll.scale(1.25)
            ll.match_color(lp)
            ll.next_to(lp, RIGHT)

        formula_parts = VGroup(
            formula.prior,
            formula.likelihood,
            formula.p_evidence,
            formula.posterior,
        ).copy()
        formula_parts.generate_target()
        formula_parts.target.scale(1.5)
        formula_parts.target.arrange(DOWN, buff=LARGE_BUFF, aligned_edge=LEFT)
        formula_parts.target.next_to(formula, DOWN, buff=LARGE_BUFF)
        formula_parts.target.shift(3 * LEFT)

        equal_signs = VGroup(*[
            TextMobject("=").next_to(fp, RIGHT)
            for fp in formula_parts.target
        ])

        kw = {
            "tex_to_color_map": {
                "hypothesis": HYPOTHESIS_COLOR,
                "evidence": EVIDENCE_COLOR1,
            },
            "alignment": "",
        }
        meanings = VGroup(
            TextMobject("Probability a hypothesis is true\\\\(before any evidence)", **kw),
            TextMobject("Probability of seeing the evidence \\quad \\\\if the hypothesis is true", **kw),
            TextMobject("Probability of seeing the evidence", **kw),
            TextMobject("Probability a hypothesis is true\\\\given some evidence", **kw),
        )
        for meaning, equals in zip(meanings, equal_signs):
            meaning.scale(0.5)
            meaning.next_to(equals, RIGHT)

        self.play(
            FadeIn(level_labels[0], lag_ratio=0.1),
            MoveToTarget(formula_parts),
            LaggedStartMap(FadeInFrom, equal_signs, lambda m: (m, RIGHT)),
            LaggedStartMap(FadeIn, meanings),
        )
        self.wait()

        # Write level 2
        diagram = BayesDiagram(0.35, 0.5, 0.2, height=2.5)
        diagram.next_to(formula, DOWN, aligned_edge=LEFT)

        braces = VGroup(*[
            Brace(diagram.he_rect, vect, buff=SMALL_BUFF)
            for vect in [DOWN, LEFT]
        ])

        formula_parts.generate_target()
        formula_parts.target[:2].scale(0.5)
        formula_parts.target[0].next_to(braces[0], DOWN, SMALL_BUFF)
        formula_parts.target[1].next_to(braces[1], LEFT, SMALL_BUFF)

        pe_picture = VGroup(
            diagram.he_rect.copy(),
            TexMobject("+"),
            diagram.nhe_rect.copy()
        )
        pe_picture.arrange(RIGHT, buff=SMALL_BUFF)
        pe_picture.next_to(equal_signs[2], RIGHT)

        phe_picture = VGroup(
            diagram.he_rect.copy(),
            Line().match_width(pe_picture),
            pe_picture.copy(),
        )
        phe_picture.arrange(DOWN, buff=MED_SMALL_BUFF)
        phe_picture.next_to(equal_signs[3], RIGHT)

        pe_picture.scale(0.5, about_edge=LEFT)
        phe_picture.scale(0.3, about_edge=LEFT)

        self.play(
            FadeOut(meanings),
            FadeOut(equal_signs[:2]),
            MoveToTarget(formula_parts),
            FadeIn(diagram),
            LaggedStartMap(GrowFromCenter, braces),
            FadeIn(level_labels[1], lag_ratio=0.1),
            level_labels[0].set_opacity, 0.5,
        )
        self.play(
            TransformFromCopy(diagram.he_rect, pe_picture[0]),
            TransformFromCopy(diagram.nhe_rect, pe_picture[2]),
            FadeIn(pe_picture[1]),
        )
        self.play(
            TransformFromCopy(pe_picture, phe_picture[2]),
            TransformFromCopy(pe_picture[0], phe_picture[0]),
            ShowCreation(phe_picture[1])
        )
        self.wait()

        # Write level 3
        steve = Steve(height=3)
        steve.to_edge(RIGHT, buff=2)

        arrow = Arrow(level_points.get_bottom(), level_points.get_top(), buff=0)
        arrow.shift(0.25 * LEFT)

        self.play(
            LaggedStartMap(
                FadeOutAndShift,
                VGroup(
                    VGroup(diagram, braces, formula_parts[:2]),
                    VGroup(formula_parts[2], equal_signs[2], pe_picture),
                    VGroup(formula_parts[3], equal_signs[3], phe_picture),
                ),
                lambda m: (m, 3 * RIGHT),
            ),
            FadeIn(level_labels[2], lag_ratio=0.1),
            level_labels[1].set_opacity, 0.5,
        )
        self.wait()
        self.play(
            GrowArrow(arrow),
            level_points.shift, 0.5 * RIGHT,
            level_labels.shift, 0.5 * RIGHT,
            level_labels.set_opacity, 1,
        )
        self.wait()
        self.play(Write(steve, run_time=3))
        self.wait()

        # Transition to next scene
        self.play(
            steve.to_corner, UR,
            Uncreate(arrow),
            LaggedStartMap(
                FadeOutAndShift,
                VGroup(
                    title,
                    formula,
                    *level_points,
                    *level_labels,
                ),
                lambda m: (m, DOWN),
            ),
        )
        self.wait()


class DescriptionOfSteve(Scene):
    def construct(self):
        self.write_description()
        self.compare_probabilities()

    def write_description(self):
        steve = Steve(height=3)
        steve.to_corner(UR)

        description = self.get_description()
        description.to_edge(LEFT)
        description.align_to(steve, UP)

        mt_parts = VGroup(
            description.get_part_by_tex("meek"),
            description.get_part_by_tex("soul"),
        )
        mt_parts.set_color(WHITE)

        self.add(steve)
        self.play(
            FadeIn(description),
            run_time=3,
            lag_ratio=0.01,
            rate_func=linear,
        )
        self.wait(3)

        lines = VGroup(*[
            Line(mob.get_corner(DL), mob.get_corner(DR), color=YELLOW)
            for mob in mt_parts
        ])
        self.play(
            ShowCreation(lines),
            mt_parts.set_color, YELLOW,
        )
        self.play(FadeOut(lines))
        self.wait()

    def compare_probabilities(self):
        bar = ProbabilityBar(0.5, width=10)
        icons = VGroup(
            LibrarianIcon(),
            FarmerIcon(),
        )
        for icon, text, half in zip(icons, ["Librarian", "Farmer"], bar.bars):
            icon.set_height(0.7)
            label = TextMobject(text)
            label.next_to(icon, DOWN, buff=SMALL_BUFF)
            label.set_color(
                interpolate_color(half.get_color(), WHITE, 0.5)
            )
            icon.add(label)

        bar.add_icons(*icons)
        bar.move_to(1.75 * DOWN)

        bar.icons.set_opacity(0)

        q_marks = TexMobject(*"???")
        q_marks.scale(1.5)
        q_marks.space_out_submobjects(1.5)
        q_marks.next_to(bar, DOWN)

        self.play(FadeIn(bar))
        self.wait()
        self.play(
            bar.p_tracker.set_value, 0.9,
            bar.icons[0].set_opacity, 1,
        )
        self.wait()
        self.play(
            bar.p_tracker.set_value, 0.1,
            bar.icons[1].set_opacity, 1,
        )
        self.play(
            LaggedStartMap(
                FadeInFrom, q_marks,
                lambda m: (m, UP),
                run_time=2,
            ),
            ApplyMethod(
                bar.p_tracker.set_value, 0.7,
                run_time=8,
            )
        )
        for value in 0.3, 0.7:
            self.play(
                bar.p_tracker.set_value, 0.3,
                run_time=7,
            )

    def get_description(self):
        return TextMobject(
            """
            Steve is very shy and withdrawn,\\\\
            invariably helpful but with very\\\\
            little interest in people or in the\\\\
            world of reality. A meek and tidy\\\\
            soul, he has a need for order and\\\\
            structure, and a passion for detail.\\\\
            """,
            tex_to_color_map={
                "shy and withdrawn": BLUE,
                "meek and tidy": YELLOW,
                "soul": YELLOW,
            },
            alignment="",
        )


class IntroduceKahnemanAndTversky(DescriptionOfSteve, MovingCameraScene):
    def construct(self):
        # Introduce K and T
        images = Group(
            ImageMobject("kahneman"),
            ImageMobject("tversky"),
        )
        danny, amos = images
        images.set_height(3.5)
        images.arrange(DOWN, buff=0.5)
        images.to_edge(LEFT, buff=MED_LARGE_BUFF)

        names = VGroup(
            TextMobject("Daniel\\\\Kahneman", alignment=""),
            TextMobject("Amos\\\\Tversky", alignment=""),
        )
        for name, image in zip(names, images):
            name.scale(1.25)
            name.next_to(image, RIGHT)
            image.name = name

        prize = ImageMobject("nobel_prize", height=1)
        prize.move_to(danny, UR)
        prize.shift(MED_SMALL_BUFF * UR)

        books = Group(
            ImageMobject("thinking_fast_and_slow"),
            ImageMobject("undoing_project"),
        )
        books.set_height(5)
        books.arrange(RIGHT, buff=0.5)
        books.to_edge(RIGHT, buff=MED_LARGE_BUFF)

        self.play(
            FadeInFrom(danny, DOWN),
            FadeInFrom(danny.name, LEFT),
        )
        self.play(
            FadeInFrom(amos, UP),
            FadeInFrom(amos.name, LEFT),
        )
        self.wait()
        self.play(FadeInFromLarge(prize))
        self.wait()
        for book in books:
            self.play(FadeInFrom(book, LEFT))
        self.wait()

        # Show them thinking
        for image in images:
            image.generate_target()
        amos.target.to_corner(DL)
        danny.target.to_corner(DR)
        targets = Group(amos.target, danny.target)

        bubble = ThoughtBubble(
            width=7, height=4,
        )
        bubble.next_to(targets, UP)
        new_stem = bubble[:-1].copy()
        new_stem.rotate(PI, UP, about_point=targets.get_top())
        new_stem.shift(SMALL_BUFF * DR)
        bubble.add_to_back(*new_stem)
        bubble[-1].scale(1.2)
        bubble[-1].to_edge(UP, buff=0)
        bubble[:-1].shift(DOWN)
        bubble.set_fill(DARK_GREY, 1)

        randy = Randolph(color=BLUE_B)
        randy.set_height(1)
        randy.next_to(bubble[-1].get_center(), DL)
        randy.shift(LEFT)

        lil_bubble = ThoughtBubble(height=1.5, width=2)
        lil_bubble.next_to(randy, UR, buff=0)
        lil_bubble[:-1].rotate(
            PI, axis=UR, about_point=lil_bubble[:-1].get_corner(UL),
        )
        lil_bubble.move_to(randy.get_top(), DL)
        for i, part in enumerate(lil_bubble[-2::-1]):
            part.rotate(90 * DEGREES)
            part.shift(0.05 * i * UR)
        lil_bubble[-1].scale(0.8)

        librarian = TextMobject("Librarian")
        librarian.set_color(BLUE)
        librarian.scale(0.5)
        librarian.move_to(lil_bubble[-1])

        bar = ProbabilityBar(percentage_background_stroke_width=1)
        bar.add_icons(
            LibrarianIcon(height=1),
            FarmerIcon(height=1),
        )
        bar.scale(0.5)
        bar.next_to(randy, RIGHT, buff=0.75)
        bar.update()

        self.play(
            LaggedStartMap(MoveToTarget, images),
            LaggedStartMap(FadeOutAndShiftDown, books),
            LaggedStartMap(FadeOut, Group(prize, *names)),
        )
        self.play(
            DrawBorderThenFill(bubble),
            FadeInFrom(
                randy, UR,
                rate_func=squish_rate_func(smooth, 0.5, 1),
                run_time=2,
            )
        )
        self.play(
            DrawBorderThenFill(lil_bubble),
            randy.change, "pondering",
        )
        self.play(Blink(randy))
        self.play(Write(librarian))
        self.add(bar, lil_bubble, librarian)
        self.play(FadeIn(bar))
        self.play(
            bar.p_tracker.set_value, 1 / 6,
            randy.change, "thinking", bar,
        )
        self.play(Blink(randy))
        self.wait()

        # Zoom in
        description = self.get_description()
        description.scale(0.4)
        description.next_to(randy, UL)
        description.shift(1.25 * RIGHT + 0.75 * UP)
        description.set_color(WHITE)

        frame = self.camera_frame

        steve = Steve()
        steve.match_height(description)
        steve.align_to(bar, RIGHT)
        steve.align_to(description, UP)

        # cross = Cross(librarian)

        book_border = bar.icons[0].copy()
        farm_border = bar.icons[1].copy()
        for border in [book_border, farm_border]:
            border.set_fill(opacity=0)
            border.set_stroke(YELLOW, 1)

        seems_bookish = TextMobject("Seems\\\\bookish")
        seems_bookish.match_width(librarian)
        seems_bookish.scale(0.8)
        seems_bookish.move_to(librarian)

        self.play(
            frame.scale, 0.5,
            frame.move_to, bubble[-1], DOWN,
            frame.shift, 0.75 * LEFT,
            FadeOut(bubble),
            FadeOut(images),
            FadeOut(lil_bubble),
            FadeOut(librarian),
            FadeIn(description, lag_ratio=0.05),
            randy.change, "pondering", description,
            run_time=6,
        )
        self.play(randy.change, "happy", description)
        self.play(
            description.get_part_by_tex("shy").set_color, BLUE,
            lag_ratio=0.1,
        )
        self.play(
            description.get_part_by_tex("meek").set_color, YELLOW,
            description.get_part_by_tex("soul").set_color, YELLOW,
            lag_ratio=0.1,
        )
        self.play(
            bar.p_tracker.set_value, 0.9,
            FadeIn(lil_bubble),
            Write(librarian),
        )
        self.play(ShowCreationThenFadeOut(book_border))
        self.play(Blink(randy))
        self.play(
            FadeInFromDown(steve),
            randy.look_at, steve,
        )
        self.play(
            randy.change, "tease", steve,
            FadeOut(librarian),
            FadeIn(seems_bookish),
        )
        lil_bubble.add(seems_bookish)
        self.wait()
        self.play(Blink(randy))

        self.play(
            LaggedStartMap(
                FadeOutAndShift, lil_bubble,
                lambda m: (m, LEFT),
                run_time=1,
            ),
            bar.p_tracker.set_value, 1 / 6,
            randy.change, "confused", bar,
        )
        self.play(
            ShowCreationThenFadeOut(farm_border)
        )
        self.wait()

        # Transition to next scene
        fh = frame.get_height()
        fw = frame.get_width()
        center = frame.get_center()
        right = (fw / FRAME_WIDTH) * RIGHT
        up = (fh / FRAME_HEIGHT) * UP
        left = -right
        down = -up

        book, farm = bar.icons.deepcopy()
        bar.clear_updaters()
        bar.icons.set_opacity(0)

        for mob in book, farm:
            mob.clear_updaters()
            mob.generate_target(use_deepcopy=True)
            mob.target.set_height(get_norm(up))
            mob.target.move_to(center + down + 2 * left)
        farm.target.shift(4 * right)

        steve.generate_target()
        steve.target.match_width(book.target)
        steve.target.move_to(book.target, DOWN)
        steve.target.shift(3 * up)
        steve_copy = steve.target.copy()
        steve_copy.match_x(farm.target),

        self.play(
            TransformFromCopy(steve, steve_copy),
            LaggedStartMap(MoveToTarget, VGroup(steve, book, farm)),
            LaggedStartMap(
                FadeOutAndShift,
                description,
                lambda m: (m, LEFT)
            ),
            FadeOutAndShift(randy, LEFT),
            FadeOutAndShift(bar, LEFT),
        )


class CorrectViewOfFarmersAndLibrarians(Scene):
    def construct(self):
        # Match last scene
        steves = VGroup(Steve(), Steve())
        book = LibrarianIcon()
        farm = FarmerIcon()
        icons = VGroup(book, farm)

        for mob in icons:
            mob.set_height(1)
            mob.move_to(DOWN + 2 * LEFT)
        farm.shift(4 * RIGHT)

        steves.match_width(book)
        steves.move_to(book, DOWN)
        steves.shift(3 * UP)
        steve1, steve2 = steves
        steve2.match_x(farm)

        self.add(steves, book, farm)

        # Add arrows
        arrows = VGroup(*[
            Arrow(s.get_bottom(), m.get_top())
            for s, m in zip(steves, icons)
        ])
        words = VGroup(
            TextMobject("Stereotype"),
            TextMobject("Unexpected"),
        )
        for arrow, word, vect in zip(arrows, words, [LEFT, RIGHT]):
            word.scale(1.5)
            word.next_to(arrow, vect)
            self.play(
                GrowArrow(arrow),
                FadeInFrom(word, UP),
            )
        self.wait()

        # Show people proportions
        librarian = Librarian()
        farmer = Farmer()

        librarian.move_to(LEFT).to_edge(UP)
        farmer.move_to(RIGHT).to_edge(UP)
        farmer_ul = farmer.get_corner(UL)

        farmers = VGroup(farmer, *[farmer.copy() for x in range(19)])
        farmers.arrange_in_grid(n_rows=4)
        farmers.move_to(farmer_ul, UL)

        farmer_outlines = farmers.copy()
        farmer_outlines.set_fill(opacity=0)
        farmer_outlines.set_stroke(YELLOW, 1)

        farmer_count = Integer(1)
        farmer_count.scale(2)
        farmer_count.set_color(GREEN)
        farmer_count.next_to(farmers, LEFT, buff=LARGE_BUFF)
        farmer_count.add_updater(lambda m: m.set_value(len(farmer_outlines)))

        for person, icon in zip([librarian, farmer], icons):
            person.save_state()
            person[:-1].set_opacity(0)
            person.scale(
                icon.get_height() / person[-1].get_height()
            )
            person.move_to(icon, DR)

        self.remove(*icons)
        self.play(
            LaggedStartMap(FadeOut, VGroup(steves, arrows, words)),
            Restore(librarian),
            Restore(farmer),
            run_time=1,
        )
        self.play(
            LaggedStartMap(FadeIn, farmers[1:])
        )
        self.wait()
        self.add(farmer_count)
        self.play(
            ShowIncreasingSubsets(farmer_outlines),
            int_func=np.ceil,
            rate_func=linear,
            run_time=2,
        )
        self.play(FadeOut(farmer_outlines))
        self.wait()

        # Show higher number of farmers
        farmers.save_state()
        farmers.generate_target()
        farmers.target.scale(0.5, about_edge=UL)
        new_farmers = VGroup(*it.chain(*[
            farmers.target.copy().next_to(
                farmers.target, vect, buff=SMALL_BUFF,
            )
            for vect in [RIGHT, DOWN]
        ]))
        new_farmers[-10:].align_to(new_farmers, RIGHT)
        new_farmers[-10:].align_to(new_farmers[-20], UP)

        farmer_count.clear_updaters()
        self.play(
            MoveToTarget(farmers),
            ShowIncreasingSubsets(new_farmers),
            ChangeDecimalToValue(farmer_count, 60),
        )
        self.wait()
        self.play(
            FadeOut(new_farmers),
            Restore(farmers),
            ChangeDecimalToValue(farmer_count, 20),
        )
        self.wait()

        # Organize into a representative sample
        farmers.generate_target()
        librarian.generate_target()
        group = VGroup(librarian.target, *farmers.target)
        self.arrange_bottom_row(group)

        l_brace = self.get_count_brace(VGroup(librarian.target))
        f_brace = self.get_count_brace(farmers.target)

        self.play(
            MoveToTarget(librarian),
            MoveToTarget(farmers),
            ReplacementTransform(farmer_count, f_brace[-1]),
            GrowFromCenter(f_brace[:-1]),
        )
        self.play(GrowFromCenter(l_brace))
        self.wait()

    def get_count_brace(self, people):
        brace = Brace(people, UP, buff=SMALL_BUFF)
        count = Integer(len(people), edge_to_fix=DOWN)
        count.next_to(brace, UP, SMALL_BUFF)
        brace.add(count)
        brace.count = count
        return brace

    def arrange_bottom_row(self, group):
        group.arrange(RIGHT, buff=0.5)
        group.set_width(FRAME_WIDTH - 3)
        group.to_edge(DOWN)
        for person in group:
            person[-1].set_stroke(BLACK, 1, background=True)


class ComplainAboutNotKnowingTheStats(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Are people expected\\\\to know that?",
            student_index=2
        )
        self.change_student_modes(
            "sassy", "sassy",
        )
        self.play(self.teacher.change, "hesitant")
        self.look_at(self.screen)
        self.wait(3)
        self.teacher_says(
            "No, but did you\\\\think to estimate it?",
            bubble_kwargs={"width": 4.5, "height": 3.5},
        )
        self.change_all_student_modes("guilty")
        self.wait(2)
        self.change_all_student_modes("pondering")
        self.wait(3)


class SpoilerAlert(Scene):
    def construct(self):
        pass


class ReasonByRepresentativeSample(CorrectViewOfFarmersAndLibrarians):
    CONFIG = {
        "ignore_icons": False,
        # "ignore_icons": True,
    }

    def construct(self):
        # Match previous scene
        librarians = VGroup(Librarian())
        farmers = VGroup(*[Farmer() for x in range(20)])
        everyone = VGroup(*librarians, *farmers)
        self.arrange_bottom_row(everyone)
        self.add(everyone)

        if self.ignore_icons:
            for person in everyone:
                person.submobjects.pop()

        l_brace = self.get_count_brace(librarians)
        f_brace = self.get_count_brace(farmers)
        braces = VGroup(l_brace, f_brace)
        for brace in braces:
            brace.count.set_stroke(BLACK, 3, background=True)
            brace.count.brace = brace
            brace.remove(brace.count)
            brace.count_tracker = ValueTracker(brace.count.get_value())
            brace.count.add_updater(
                lambda c: c.set_value(
                    c.brace.count_tracker.get_value(),
                ).next_to(c.brace, UP, SMALL_BUFF)
            )
            self.add(brace, brace.count)

        # Multiply by 10
        new_people = VGroup()
        for group in [librarians, farmers]:
            new_rows = VGroup(*[group.copy() for x in range(9)])
            new_rows.arrange(UP, buff=SMALL_BUFF)
            new_rows.next_to(group, UP, SMALL_BUFF)
            new_people.add(new_rows)
        new_librarians, new_farmers = new_people

        self.play(
            *[
                FadeIn(new_rows, lag_ratio=0.1)
                for new_rows in new_people
            ],
            *[
                ApplyMethod(brace.next_to, new_rows, UP, {"buff": SMALL_BUFF})
                for brace, new_rows in zip(braces, new_people)
            ],
            *[
                ApplyMethod(
                    brace.count_tracker.set_value,
                    10 * brace.count_tracker.get_value(),
                )
                for brace in braces
            ],
        )

        farmers = VGroup(farmers, *new_farmers)
        librarians = VGroup(librarians, *new_librarians)
        everyone = VGroup(farmers, librarians)

        # Add background rectangles
        big_rect = SurroundingRectangle(
            everyone,
            buff=0.05,
            stroke_width=1,
            stroke_color=WHITE,
            fill_opacity=1,
            fill_color=DARKER_GREY,
        )
        left_rect = big_rect.copy()
        prior = 1 / 21
        left_rect.stretch(prior, 0, about_edge=LEFT)
        right_rect = big_rect.copy()
        right_rect.stretch(1 - prior, 0, about_edge=RIGHT)

        dl_rect = left_rect.copy()
        ul_rect = left_rect.copy()
        dl_rect.stretch(0.4, 1, about_edge=DOWN)
        ul_rect.stretch(0.6, 1, about_edge=UP)

        dr_rect = right_rect.copy()
        ur_rect = right_rect.copy()
        dr_rect.stretch(0.1, 1, about_edge=DOWN)
        ur_rect.stretch(0.9, 1, about_edge=UP)

        colors = [
            interpolate_color(color, BLACK, 0.5)
            for color in [EVIDENCE_COLOR1, EVIDENCE_COLOR2]
        ]
        for rect, color in zip([dl_rect, dr_rect], colors):
            rect.set_fill(color)

        all_rects = VGroup(
            left_rect, right_rect,
            dl_rect, ul_rect, dr_rect, ur_rect,
        )
        all_rects.set_opacity(0)

        self.add(all_rects, everyone)
        self.play(
            left_rect.set_opacity, 1,
            right_rect.set_opacity, 1,
        )
        self.wait()

        # 40% of librarians and 10% of farmers
        for rect, vect in zip([dl_rect, dr_rect], [LEFT, RIGHT]):
            rect.set_opacity(1)
            rect.save_state()
            rect.brace = Brace(rect, vect, buff=SMALL_BUFF)
            rect.brace.save_state()

            rect.number = Integer(0, unit="\\%")
            rect.number.scale(0.75)
            rect.number.next_to(rect.brace, vect, SMALL_BUFF)
            rect.number.brace = rect.brace
            rect.number.vect = vect

            rect.number.add_updater(
                lambda d: d.set_value(100 * d.brace.get_height() / big_rect.get_height())
            )
            rect.number.add_updater(lambda d: d.next_to(d.brace, d.vect, SMALL_BUFF))

            for mob in [rect, rect.brace]:
                mob.stretch(0, 1, about_edge=DOWN)

        for rect, to_fade in [(dl_rect, librarians[4:]), (dr_rect, farmers[1:])]:
            self.add(rect.brace, rect.number)
            self.play(
                Restore(rect),
                Restore(rect.brace),
                to_fade.set_opacity, 0.1,
            )
            self.wait()

        # Emphasize restricted set
        highlighted_librarians = librarians[:4].copy()
        highlighted_farmers = farmers[0].copy()
        for highlights in [highlighted_librarians, highlighted_farmers]:
            highlights.set_color(YELLOW)

        self.add(braces, *[b.count for b in braces])
        self.play(
            l_brace.next_to, librarians[:4], UP, SMALL_BUFF,
            l_brace.count_tracker.set_value, 4,
            ShowIncreasingSubsets(highlighted_librarians)
        )
        self.play(FadeOut(highlighted_librarians))
        self.play(
            f_brace.next_to, farmers[:1], UP, SMALL_BUFF,
            f_brace.count_tracker.set_value, 20,
            ShowIncreasingSubsets(highlighted_farmers),
            run_time=2,
        )
        self.play(FadeOut(highlighted_farmers))
        self.wait()

        # Write answer
        equation = TexMobject(
            "P\\left(",
            "\\text{Librarian }",
            "\\text{given }",
            "\\text{description}",
            "\\right)",
            "=",
            "{4", "\\over", " 4", "+", "20}",
            "\\approx", "16.7\\%",
        )
        equation.set_color_by_tex_to_color_map({
            "Librarian": HYPOTHESIS_COLOR,
            "description": EVIDENCE_COLOR1,
        })

        equation.set_width(FRAME_WIDTH - 2)
        equation.to_edge(UP)
        equation_rect = BackgroundRectangle(equation, buff=MED_SMALL_BUFF)
        equation_rect.set_fill(opacity=1)
        equation_rect.set_stroke(WHITE, width=1, opacity=1)

        self.play(
            FadeIn(equation_rect),
            FadeInFromDown(equation[:6])
        )
        self.wait()
        self.play(
            TransformFromCopy(
                l_brace.count,
                equation.get_parts_by_tex("4")[0],
            ),
            Write(equation.get_part_by_tex("\\over")),
        )
        self.play(
            Write(equation.get_part_by_tex("+")),
            TransformFromCopy(
                f_brace.count,
                equation.get_part_by_tex("20"),
            ),
            TransformFromCopy(
                l_brace.count,
                equation.get_parts_by_tex("4")[1],
            ),
        )

        self.wait()
        self.play(FadeIn(equation[-2:]))
        self.wait()

        # Compare raw likelihoods
        axes = Axes(
            x_min=0,
            x_max=10,
            y_min=0,
            y_max=100,
            y_axis_config={
                "unit_size": 0.07,
                "tick_frequency": 10,
            },
            number_line_config={
                "include_tip": False,
            },
        )
        axes.x_axis.tick_marks.set_opacity(0)
        axes.y_axis.add_numbers(
            *range(20, 120, 20),
            number_config={"unit": "\\%"}
        )
        axes.center().to_edge(DOWN)

        title = TextMobject("Likelihood of fitting the description")
        title.scale(1.25)
        title.to_edge(UP)
        title.shift(RIGHT)
        axes.add(title)

        lines = VGroup(
            Line(axes.c2p(3, 0), axes.c2p(3, 40)),
            Line(axes.c2p(7, 0), axes.c2p(7, 10)),
        )
        rects = VGroup(*[Rectangle() for x in range(2)])
        rects.set_fill(EVIDENCE_COLOR1, 1)
        rects[1].set_fill(GREEN)
        rects.set_stroke(WHITE, 1)
        icons = VGroup(LibrarianIcon(), FarmerIcon())

        for rect, line, icon in zip(rects, lines, icons):
            rect.replace(line, dim_to_match=1)
            rect.set_width(1, stretch=True)
            icon.set_width(1)
            icon.next_to(rect, UP)
            y = axes.y_axis.p2n(rect.get_top())
            y_point = axes.y_axis.n2p(y)
            rect.line = DashedLine(y_point, rect.get_corner(UL))

        pre_rects = VGroup()
        for r in dl_rect, dr_rect:
            r_copy = r.deepcopy()
            pre_rects.add(r_copy)

        people_copy = VGroup(librarians[:4], farmers[:1]).copy()
        everything = self.get_mobjects()

        self.play(
            *[FadeOut(mob) for mob in everything],
            FadeIn(axes),
            FadeIn(icons),
            *[
                TransformFromCopy(pr, r)
                for pr, r in zip(pre_rects, rects)
            ],
            FadeOut(people_copy),
        )
        self.play(*[
            ShowCreation(rect.line)
            for rect in rects
        ])
        self.wait()
        self.play(
            FadeOut(axes),
            FadeOut(rects[0].line),
            FadeOut(rects[1].line),
            FadeOut(icons),
            *[
                ReplacementTransform(r, pr)
                for pr, r in zip(pre_rects, rects)
            ],
            # FadeOut(fsfr),
            *[FadeIn(mob) for mob in everything],
        )
        self.remove(*pre_rects)
        self.wait()

        # Emphasize prior belief
        prior_equation = TexMobject(
            "P\\left(",
            "\\text{Librarian}",
            "\\right)",
            "=",
            "{1", "\\over", "21}",
            "\\approx", "4.8\\%",
        )
        prior_equation.set_color_by_tex_to_color_map({
            "Librarian": HYPOTHESIS_COLOR,
        })

        prior_equation.match_height(equation)

        prior_rect = BackgroundRectangle(prior_equation, buff=MED_SMALL_BUFF)
        prior_rect.match_style(equation_rect)

        group = VGroup(prior_equation, prior_rect)
        group.align_to(equation_rect, UP)
        group.shift(
            (
                equation.get_part_by_tex("\\over").get_x() -
                prior_equation.get_part_by_tex("\\over").get_x()
            ) * RIGHT
        )

        prior_label = TextMobject("Prior belief")
        prior_label.scale(1.5)
        prior_label.next_to(prior_rect, LEFT, buff=1.5)
        prior_label.to_edge(UP, buff=0.25)
        prior_label.set_stroke(BLACK, 5, background=True)
        prior_arrow = Arrow(
            prior_label.get_right(),
            prior_equation.get_left(),
            buff=SMALL_BUFF,
        )

        self.play(
            VGroup(equation_rect, equation).shift, prior_rect.get_height() * DOWN,
            FadeIn(prior_rect),
            FadeIn(prior_equation),
            FadeInFrom(prior_label, RIGHT),
            GrowArrow(prior_arrow),
        )
        self.wait()


class HeartOfBayesTheorem(Scene):
    def construct(self):
        title = TextMobject("Heart of Bayes' theorem")
        title.scale(1.5)
        title.add(Underline(title))
        title.to_edge(UP)

        # Bayes diagrams
        prior_tracker = ValueTracker(0.1)
        likelihood_tracker = ValueTracker(0.4)
        antilikelihood_tracker = ValueTracker(0.1)
        diagram = always_redraw(
            lambda: self.get_diagram(
                prior_tracker.get_value(),
                likelihood_tracker.get_value(),
                antilikelihood_tracker.get_value(),
            )
        )
        restricted_diagram = always_redraw(
            lambda: self.get_restricted_diagram(diagram)
        )

        diagrams = VGroup(diagram, restricted_diagram)

        label1 = TextMobject("All possibilities")
        label2 = TextMobject(
            "All possibilities\\\\", "fitting the evidence",
            tex_to_color_map={"evidence": EVIDENCE_COLOR1},
        )
        labels = VGroup(label1, label2)
        labels.scale(diagram.get_width() / label1.get_width())

        for l, d in zip(labels, diagrams):
            l.next_to(d, UP)

        label2.save_state()
        label2[0].move_to(label2, DOWN)
        label2[1:].shift(0.25 * UP)
        label2[1:].set_opacity(0)

        # Final fraction written geometrically
        fraction = always_redraw(
            lambda: self.get_geometric_fraction(diagram)
        )
        frac_box = always_redraw(lambda: DashedVMobject(
            SurroundingRectangle(
                fraction,
                buff=MED_SMALL_BUFF,
                stroke_width=2,
                stroke_color=WHITE,
            ),
            num_dashes=100,
        ))
        prob = TexMobject(
            "P\\left(",
            "{\\text{Librarian }",
            "\\text{given}", "\\over", "\\text{the evidence}}",
            "\\right)"
        )
        prob.set_color_by_tex("Librarian", HYPOTHESIS_COLOR)
        prob.set_color_by_tex("evidence", EVIDENCE_COLOR1)
        prob.get_part_by_tex("\\over").set_opacity(0)
        prob.match_width(frac_box)
        prob.next_to(frac_box, UP)

        updaters = VGroup(
            diagram, restricted_diagram, fraction, frac_box
        )
        updaters.suspend_updating()

        self.play(
            FadeIn(diagram),
            FadeInFromDown(label1),
        )
        self.play(
            TransformFromCopy(diagram, restricted_diagram),
            TransformFromCopy(label1[0], label2[0]),
        )
        self.play(Restore(label2))
        self.wait()

        self.play(
            TransformFromCopy(
                restricted_diagram.he_rect,
                fraction[0],
            ),
            TransformFromCopy(
                restricted_diagram.he_rect,
                fraction[2][0],
            ),
            TransformFromCopy(
                restricted_diagram.nhe_rect,
                fraction[2][2],
            ),
            ShowCreation(fraction[1]),
            Write(fraction[2][1]),
        )
        self.add(fraction)
        self.play(
            ShowCreation(frac_box),
            FadeIn(prob)
        )
        self.wait()

        self.play(Write(title, run_time=1))
        self.wait()

        # Mess with some numbers
        updaters.resume_updating()
        self.play(prior_tracker.set_value, 0.4, run_time=2)
        self.play(antilikelihood_tracker.set_value, 0.3, run_time=2)
        self.play(likelihood_tracker.set_value, 0.6, run_time=2)
        self.wait()
        updaters.suspend_updating()

        # Ask about a formula
        words = TextMobject("Write this more\\\\mathematically")
        words.scale(1.25)
        words.set_color(RED)
        words.to_corner(UR)
        arrow = Arrow(words.get_bottom(), frac_box.get_top(), buff=SMALL_BUFF)
        arrow.match_color(words)
        arrow.set_stroke(width=5)

        self.play(
            FadeInFrom(words, DOWN),
            GrowArrow(arrow),
            FadeOut(prob),
            title.to_edge, LEFT
        )
        self.wait()

    def get_diagram(self, prior, likelihood, antilikelihood):
        diagram = BayesDiagram(
            prior, likelihood, antilikelihood,
            not_evidence_color1=GREY,
            not_evidence_color2=GREEN_E,
        )
        diagram.set_height(3)
        diagram.move_to(5 * LEFT + DOWN)

        diagram.add_brace_attrs()
        braces = VGroup(diagram.h_brace, diagram.nh_brace)
        diagram.add(*braces)
        icons = VGroup(LibrarianIcon(), FarmerIcon())
        icons[0].set_color(YELLOW_D)
        for icon, brace in zip(icons, braces):
            icon.set_height(0.5)
            icon.next_to(brace, DOWN, SMALL_BUFF)
            diagram.add(icon)
        return diagram

    def get_restricted_diagram(self, diagram):
        restricted_diagram = diagram.deepcopy()
        restricted_diagram.set_x(0)
        restricted_diagram.hne_rect.set_opacity(0.1)
        restricted_diagram.nhne_rect.set_opacity(0.1)
        return restricted_diagram

    def get_geometric_fraction(self, diagram):
        fraction = VGroup(
            diagram.he_rect.copy(),
            Line(LEFT, RIGHT),
            VGroup(
                diagram.he_rect.copy(),
                TexMobject("+"),
                diagram.nhe_rect.copy(),
            ).arrange(RIGHT, buff=SMALL_BUFF)
        )
        fraction.arrange(DOWN)
        fraction[1].match_width(fraction)
        fraction.to_edge(RIGHT)
        fraction.align_to(diagram.square, UP)
        return fraction


class WhenDoesBayesApply(DescriptionOfSteve):
    def construct(self):
        title = TextMobject("When to use Bayes' rule")
        title.add(Underline(title, buff=-SMALL_BUFF))
        title.scale(1.5)
        title.to_edge(UP)
        self.add(title)

        # Words
        all_words = VGroup(
            TextMobject("You have a\\\\", "hypothesis"),
            TextMobject("You've observed\\\\some ", "evidence"),
            TexMobject(
                "\\text{You want}\\\\",
                "P", "(", "H", "|", "E", ")\\\\",
                "P", "\\left(",
                "\\substack{""\\text{Hypothesis} \\\\",
                "\\textbf{given} \\\\",
                "\\, \\text{the evidence} \\,}",
                "\\right)",
            ),
        )
        for words in all_words:
            words.set_color_by_tex_to_color_map({
                "hypothesis": HYPOTHESIS_COLOR,
                "H": HYPOTHESIS_COLOR,
                "evidence": EVIDENCE_COLOR1,
                "E": EVIDENCE_COLOR1,
            })

        goal = all_words[2]
        prob = goal[1:7]
        big_prob = goal[7:]
        for mob in [prob, big_prob]:
            mob.match_x(goal[0])
        prob.shift(0.2 * DOWN)
        big_prob.shift(0.4 * DOWN)
        VGroup(big_prob[1], big_prob[-1]).stretch(1.2, 1)

        all_words.arrange(RIGHT, buff=2, aligned_edge=UP)
        all_words.next_to(title, DOWN, buff=MED_LARGE_BUFF)

        big_prob.save_state()
        big_prob.move_to(prob, UP)

        # Icons
        hypothesis_icon = self.get_hypothesis_icon()
        evidence_icon = self.get_evidence_icon()

        hypothesis_icon.next_to(all_words[0], DOWN, LARGE_BUFF)
        evidence_icon.next_to(all_words[1], DOWN, LARGE_BUFF)

        # Show icons
        self.play(FadeInFromDown(all_words[0]))
        self.play(
            LaggedStart(
                FadeInFrom(hypothesis_icon[0], DOWN),
                Write(hypothesis_icon[1]),
                FadeInFrom(hypothesis_icon[2], UP),
                run_time=1,
            )
        )
        self.wait()

        self.play(FadeInFromDown(all_words[1]))
        self.play(
            FadeIn(evidence_icon),
            lag_ratio=0.1,
            run_time=2,
        )
        self.wait()

        # More compact probability
        self.play(FadeInFromDown(VGroup(goal[0], big_prob)))
        self.wait()
        self.play(
            Restore(big_prob),
            *[
                TransformFromCopy(big_prob[i], prob[i])
                for i in [0, 1, -1]
            ]
        )
        self.play(LaggedStart(*[
            TransformFromCopy(big_prob[i][j], prob[i])
            for i, j in [(2, 0), (3, 1), (4, 3)]
        ]))
        self.wait()

        # Highlight "given"
        rects = VGroup(*[
            SurroundingRectangle(
                goal.get_part_by_tex(tex),
                buff=0.05,
                stroke_width=2,
                stroke_color=RED,
            )
            for tex in ("|", "given")
        ])

        self.play(ShowCreation(rects))
        self.play(Transform(rects[0].copy(), rects[1], remover=True))
        self.play(FadeOut(rects))
        self.wait()

        self.remove(prob)
        everything = Group(*self.get_mobjects())
        self.play(
            LaggedStartMap(FadeOut, everything, run_time=2),
            prob.copy().to_corner, UR,
        )

    def get_hypothesis_icon(self):
        group = VGroup(
            Steve().set_height(1.5),
            TexMobject("\\updownarrow"),
            LibrarianIcon().set_color(YELLOW_D)
        )
        group.arrange(DOWN)
        return group

    def get_evidence_icon(self):
        result = self.get_description()
        result.scale(0.5)
        result.set_color_by_tex("meek", EVIDENCE_COLOR1)
        result.set_color_by_tex("soul", EVIDENCE_COLOR1)
        rect = SurroundingRectangle(result)
        rect.set_stroke(WHITE, 2)
        result.add(rect)
        return result


class CreateFormulaFromDiagram(Scene):
    def construct(self):
        t2c = {
            "P": WHITE,
            "H": HYPOTHESIS_COLOR,
            "E": EVIDENCE_COLOR1,
            "\\neg": RED,
        }

        # Add posterior
        posterior = TexMobject("P(H|E)", tex_to_color_map=t2c)
        posterior.to_corner(UR)
        posterior_words = TextMobject("Goal: ")
        posterior_words.next_to(posterior, LEFT, aligned_edge=UP)
        self.add(posterior)
        self.add(posterior_words)

        # Show prior
        diagram = self.get_diagram()

        prior_label = TexMobject("P(H)", tex_to_color_map=t2c)
        prior_label.add_updater(
            lambda m: m.next_to(diagram.h_brace, UP, SMALL_BUFF)
        )

        prior_example = TexMobject("= 1 / 21")
        prior_example.add_updater(
            lambda m: m.next_to(prior_label, RIGHT).shift(0.03 * UP)

        )
        # example_words = TextMobject("In our example")
        # example_words.next_to(prior_example[0][1:], UP, buff=SMALL_BUFF, aligned_edge=LEFT)
        # prior_example.add(example_words)

        prior_arrow = Vector(0.7 * RIGHT)
        prior_arrow.next_to(prior_label, LEFT, SMALL_BUFF)
        prior_word = TextMobject("``Prior''")
        prior_word.next_to(prior_arrow, LEFT, SMALL_BUFF)
        prior_word.align_to(prior_label[0], DOWN)
        prior_word.set_color(HYPOTHESIS_COLOR)

        self.add(diagram)
        self.play(ShowIncreasingSubsets(diagram.people, run_time=2))
        self.wait()
        self.play(
            diagram.hypothesis_split.set_opacity, 1,
            FadeIn(diagram.h_brace),
            FadeInFromDown(prior_label),
        )
        self.wait()
        self.play(FadeIn(prior_example))
        self.play(
            LaggedStartMap(
                Indicate, diagram.people[::10],
                color=BLUE,
            )
        )
        self.wait()
        self.play(
            FadeInFrom(prior_word, RIGHT),
            GrowArrow(prior_arrow)
        )
        self.wait()

        # First likelihood split
        like_label = TexMobject("P(E|H)", tex_to_color_map=t2c)
        like_label.add_updater(
            lambda m: m.next_to(diagram.he_brace, LEFT)
        )

        like_example = TexMobject("= 0.4")
        like_example.add_updater(
            lambda m: m.next_to(like_label, DOWN)
        )

        like_word = TextMobject("``Likelihood''")
        like_word.next_to(like_label, UP, LARGE_BUFF, aligned_edge=RIGHT)
        like_arrow = Arrow(
            like_word.get_bottom(),
            like_label.get_top(),
            buff=0.2,
        )

        limit_arrow = Vector(0.5 * UP)
        limit_arrow.next_to(like_label.get_part_by_tex("|"), UP, SMALL_BUFF)
        limit_arrow.set_stroke(WHITE, 4)
        limit_word = TextMobject("Limit\\\\your\\\\view")
        limit_word.next_to(limit_arrow, UP)

        self.play(
            diagram.he_rect.set_opacity, 1,
            diagram.hne_rect.set_opacity, 1,
            GrowFromCenter(diagram.he_brace),
            FadeInFrom(like_label, RIGHT),
            FadeInFrom(like_example, RIGHT),
        )
        self.wait()
        self.play(
            ShowCreationThenFadeAround(
                like_label.get_part_by_tex("E"),
                surrounding_rectangle_config={
                    "color": EVIDENCE_COLOR1
                }
            ),
        )
        self.play(WiggleOutThenIn(like_label.get_part_by_tex("|")))
        self.play(
            ShowCreationThenFadeAround(
                like_label.get_part_by_tex("H")
            ),
        )
        self.wait()
        self.play(
            diagram.people[10:].set_opacity, 0.2,
            diagram.nh_rect.set_opacity, 0.2,
            FadeInFrom(limit_word, DOWN),
            GrowArrow(limit_arrow),
            rate_func=there_and_back_with_pause,
            run_time=6,
        )
        self.wait()
        self.play(
            Write(like_word, run_time=1),
            GrowArrow(like_arrow),
        )
        self.wait()

        # Show anti-likelihood
        anti_label = TexMobject("P(E| \\neg H)", tex_to_color_map=t2c)
        anti_label.add_updater(
            lambda m: m.next_to(diagram.nhe_brace, RIGHT)
        )

        anti_example = TexMobject("= 0.1")
        anti_example.add_updater(
            lambda m: m.next_to(anti_label, RIGHT).align_to(anti_label[0], DOWN)
        )

        neg_sym = anti_label.get_part_by_tex("\\neg").copy()
        neg_sym.generate_target()
        neg_sym.target.scale(2.5)
        not_word = TextMobject("means ``not''")
        neg_group = VGroup(neg_sym.target, not_word)
        neg_group.arrange(RIGHT)
        neg_group.next_to(anti_label, UP, LARGE_BUFF)
        neg_group.to_edge(RIGHT, buff=MED_SMALL_BUFF)

        diagram.nhe_rect.set_opacity(1)
        diagram.nhe_rect.save_state()
        diagram.nhe_rect.become(diagram.nh_rect)
        self.play(
            Restore(diagram.nhe_rect),
            GrowFromCenter(diagram.nhe_brace),
            FadeInFrom(anti_label, LEFT),
            FadeInFrom(anti_example, LEFT),
        )
        diagram.nhne_rect.set_opacity(1)
        self.wait()
        self.play(
            ShowCreationThenFadeAround(
                anti_label[2],
                surrounding_rectangle_config={"color": EVIDENCE_COLOR1},
            )
        )
        self.play(
            ShowCreationThenFadeAround(
                anti_label[4:6],
                surrounding_rectangle_config={"color": RED},
            )
        )
        self.wait()
        self.play(
            MoveToTarget(neg_sym),
            FadeIn(not_word)
        )
        self.wait()
        self.play(
            FadeOut(not_word),
            Transform(neg_sym, anti_label.get_part_by_tex("\\neg"))
        )
        self.remove(neg_sym)

        # Recall final answer

        diagram.add(
            diagram.h_brace,
            diagram.he_brace,
            diagram.nhe_brace,
        )
        self.play(
            diagram.scale, 0.7, {"about_edge": DL},
            diagram.refresh_braces,
            MaintainPositionRelativeTo(
                VGroup(like_word, like_arrow),
                like_label,
            ),
            MaintainPositionRelativeTo(
                VGroup(prior_word, prior_arrow),
                prior_label,
            ),
        )

    def get_diagram(self):
        diagram = BayesDiagram(
            prior=1 / 21,
            likelihood=0.4,
            antilikelihood=0.1,
            not_evidence_color1=GREY,
            not_evidence_color2=DARK_GREY,
            prior_rect_direction=UP,
        )
        diagram.set_height(5.5)
        diagram.set_width(6, stretch=True)
        diagram.move_to(0.5 * DOWN)
        diagram.add_brace_attrs()

        diagram.evidence_split.set_opacity(0)
        diagram.hypothesis_split.set_opacity(0)
        diagram.nh_rect.set_fill(DARK_GREY)

        people = VGroup(*[Person() for x in range(210)])
        people.set_color(interpolate_color(LIGHT_GREY, WHITE, 0.5))
        people.arrange_in_grid(n_cols=21)
        people.set_width(diagram.get_width() - SMALL_BUFF)
        people.set_height(diagram.get_height() - SMALL_BUFF, stretch=True)
        people.move_to(diagram)
        people[10:].set_color(GREEN_D)
        people.set_stroke(BLACK, 2, background=True)

        diagram.add(people)
        diagram.people = people

        return diagram
