from manimlib.imports import *

import scipy.integrate

OUTPUT_DIRECTORY = "bayes/part1"

HYPOTHESIS_COLOR = YELLOW
NOT_HYPOTHESIS_COLOR = GREY
EVIDENCE_COLOR1 = BLUE_C
EVIDENCE_COLOR2 = BLUE_E
NOT_EVIDENCE_COLOR1 = GREY
NOT_EVIDENCE_COLOR2 = DARK_GREY

#


def get_bayes_formula(expand_denominator=False):
    t2c = {
        "{H}": HYPOTHESIS_COLOR,
        "{\\neg H}": NOT_HYPOTHESIS_COLOR,
        "{E}": EVIDENCE_COLOR1,
    }
    substrings_to_isolate = ["P", "\\over", "=", "\\cdot", "+"]

    tex = "P({H} | {E}) = {P({H}) P({E} | {H}) \\over "
    if expand_denominator:
        tex += "P({H}) P({E} | {H}) + P({\\neg H}) \\cdot P({E} | {\\neg H})}"
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
        kw = {
            "buff": buff,
            "min_num_quads": 1,
        }
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
        "include_braces": False,
        "brace_direction": UP,
        "include_percentages": True,
        "percentage_background_stroke_width": 2,
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
        "name": "Steve"
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.include_name:
            self.add_name()

    def add_name(self):
        self.name = TextMobject(self.name)
        self.name.match_width(self)
        self.name.next_to(self, DOWN, SMALL_BUFF)
        self.add(self.name)


class Linda(Steve):
    CONFIG = {
        "file_name": "linda",
        "name": "Linda"
    }


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
        formula.save_state()
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
                get_formula_slice(0, 1, 4, 5),
                get_formula_slice(19, 20, 21, 22),
            ),
        )
        self.wait()

        self.clear()
        self.play(
            formula.restore,
            formula.scale, 1.5,
            formula.to_edge, UP,
            FadeOut(VGroup(
                hyp_arrow, hyp_label,
                evid_arrow, evid_label,
            ))
        )


class StateGoal(PiCreatureScene, Scene):
    CONFIG = {
        "default_pi_creature_kwargs": {
            "color": BLUE_B,
            "height": 2,
        },

    }

    def construct(self):
        # Zoom to later
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

        # Add bubble
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

        # Show examples
        icons = VGroup(
            SVGMobject(file_name="science"),
            SVGMobject(file_name="robot"),
        )
        for icon in icons:
            icon.set_stroke(width=0)
            icon.set_fill(GREY)
            icon.set_sheen(1, UL)
            icon.set_height(1.5)
        icons[0].set_stroke(GREY, 3, background=True)
        gold = self.get_gold()
        icons.add(gold)

        icons.arrange(DOWN, buff=MED_LARGE_BUFF)
        icons.to_corner(UL)

        for icon in icons[:2]:
            self.play(
                Write(icon, run_time=2),
                you.change, "thinking", icon,
            )
        self.play(
            Blink(you),
            FadeOut(VGroup(
                line, now_label, later_label,
                you_label, you_arrow
            )),
        )
        self.play(
            FadeInFrom(gold, LEFT),
            you.change, "erm", gold,
        )
        self.play(Blink(you))

        # Brief Thompson description
        words = VGroup(
            TextMobject("1988").scale(1.5),
            TextMobject("Tommy Thompson\\\\and friends"),
        )
        words.arrange(DOWN, buff=0.75)

        ship = ImageMobject("ss_central_america")
        ship.set_width(4)
        ship.move_to(gold, DL)
        ship_title = TextMobject("SS Central America")
        ship_title.next_to(ship, UP)

        words.next_to(ship, RIGHT)

        self.play(
            FadeInFrom(words[0], LEFT),
            you.change, "tease", words,
            FadeOut(icons[:2]),
        )
        self.play(FadeInFrom(words[1], UP))
        self.wait()

        self.add(ship, gold)
        self.play(
            FadeIn(ship),
            gold.scale, 0.2,
            gold.move_to, ship,
        )
        self.play(FadeInFromDown(ship_title))
        self.play(you.change, "thinking", ship)

        amount = TexMobject("> \\$700{,}000{,}000")
        amount.scale(1.5)
        amount.next_to(ship, DOWN, MED_LARGE_BUFF)
        amount.to_edge(LEFT, buff=2)
        amount.set_color(YELLOW)

        gold_copy = gold.copy()
        self.play(
            gold_copy.scale, 3,
            gold_copy.next_to, amount, LEFT,
            FadeIn(amount),
        )
        self.play(Blink(you))
        self.wait()
        self.play(LaggedStartMap(
            FadeOutAndShift,
            Group(*words, ship_title, ship, gold, gold_copy, amount),
        ))

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

    def get_gold(self):
        gold = SVGMobject(file_name="gold_bars")[0]
        gold.set_stroke(width=0)
        gold.set_fill(GOLD)
        gold.set_sheen(0.5, UP)
        gold.flip(UP)
        gold_copy = gold.copy()
        gold_copy.shift(2 * OUT)

        rects = VGroup()
        for curve in CurvesAsSubmobjects(gold):
            p1 = curve.points[0]
            p2 = curve.points[-1]
            rect = Polygon(p1, p2, p2 + 2 * OUT, p1 + 2 * OUT)
            rect.match_style(gold)
            # rect.set_fill(GOLD)
            # rect.set_sheen(1, UL)
            rects.add(rect)
        rects.sort(lambda p: p[1])
        gold.add(*rects)
        gold.add(gold_copy)

        # gold = rects

        gold.rotate(2 * DEGREES, UP)
        gold.rotate(2 * DEGREES, RIGHT)
        gold.set_shade_in_3d(True)
        gold.set_height(1.5)
        gold.set_stroke(BLACK, 0.5)
        return gold


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
        bar = ProbabilityBar(
            0.5, width=10,
            include_braces=True,
            percentage_background_stroke_width=2,
        )
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
        sa_words = TextMobject("Spoiler Alert")
        sa_words.scale(2)
        sa_words.to_edge(UP)
        sa_words.set_color(RED)

        alert = Triangle(start_angle=90 * DEGREES)
        alert.set_stroke(RED, 8)
        alert.set_height(sa_words.get_height())
        alert.round_corners(0.1)
        bang = TextMobject("!")
        bang.set_color(RED)
        bang.scale(1.5)
        bang.move_to(alert)
        alert.add(bang)

        alert.next_to(sa_words, LEFT)
        sa_words.add(alert.copy())
        alert.next_to(sa_words, RIGHT)
        sa_words.add(alert)

        formula = get_bayes_formula()
        formula_words = TextMobject("This is secretly ")
        formula_words.scale(1.5)
        formula_group = VGroup(formula_words, formula)
        formula_group.arrange(DOWN, buff=MED_LARGE_BUFF)
        formula_group.next_to(sa_words, DOWN, LARGE_BUFF)

        self.add(sa_words)
        self.wait()
        self.play(FadeInFrom(formula_group, UP))
        self.wait()


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
            axis_config={
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


class NewEvidenceUpdatesPriorBeliefs(DescriptionOfSteve):
    def construct(self):
        # Determining belief in a vacuum
        description = self.get_description()
        rect = SurroundingRectangle(description)
        rect.set_stroke(WHITE, 2)
        rect.set_fill(BLACK, 0.9)
        evid = VGroup(rect, description)
        evid.set_height(2)

        librarian = Librarian()
        librarian.set_height(2)

        arrow = Arrow(LEFT, RIGHT)
        arrow.set_stroke(WHITE, 5)

        group = VGroup(evid, arrow, librarian)
        group.arrange(RIGHT, buff=LARGE_BUFF)

        cross = Cross(VGroup(group))
        cross.set_stroke(RED, 12)
        cross.scale(1.2)

        self.add(evid)
        self.play(
            GrowArrow(arrow),
            FadeInFrom(librarian, LEFT)
        )
        self.play(ShowCreation(cross))
        self.wait()

        #
        icons = VGroup(LibrarianIcon(), FarmerIcon())
        for icon in icons:
            icon.set_height(0.5)

        kw = {
            "include_braces": True,
            "width": 11,
            "height": 0.75,
        }
        top_bar = ProbabilityBar(p=1 / 21, **kw)
        low_bar = ProbabilityBar(p=1 / 21, brace_direction=DOWN, **kw)

        bars = VGroup(top_bar, low_bar)
        for bar in bars:
            bar.percentages[1].add_updater(lambda m: m.set_opacity(0))
            bar.add_icons(*icons.copy())
            bar.suspend_updating()

        new_arrow = Arrow(1.5 * UP, 1.5 * DOWN)
        new_arrow.set_stroke(WHITE, 5)

        top_bar.next_to(new_arrow, UP)
        low_bar.next_to(new_arrow, DOWN)

        self.add(arrow, evid, cross)
        self.play(
            FadeOut(cross),
            Transform(arrow, new_arrow),
            evid.scale, 0.6,
            evid.move_to, new_arrow,
            ReplacementTransform(librarian, low_bar.icons[0]),
            FadeIn(bars)
        )
        self.play(low_bar.p_tracker.set_value, 1 / 6)
        self.wait()


class HeartOfBayesTheorem(Scene):
    def construct(self):
        title = TextMobject("Heart of Bayes' theorem")
        title.scale(1.5)
        title.add(Underline(title))
        title.to_edge(UP)

        # Bayes diagrams
        # prior_tracker = ValueTracker(0.1)
        # likelihood_tracker = ValueTracker(0.4)
        # antilikelihood_tracker = ValueTracker(0.1)
        diagram = self.get_diagram(
            prior=0.1, likelihood=0.4, antilikelihood=0.1,
            # prior_tracker.get_value(),
            # likelihood_tracker.get_value(),
            # antilikelihood_tracker.get_value(),
        )
        diagram.nh_rect.set_fill(GREEN_E)
        diagram.hypothesis_split.set_opacity(1)
        diagram.evidence_split.set_opacity(0)
        restricted_diagram = self.get_restricted_diagram(diagram)
        diagram_copy = diagram.copy()
        diagram_copy.move_to(restricted_diagram)

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
            lambda: self.get_geometric_fraction(restricted_diagram)
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
            TransformFromCopy(diagram, diagram_copy),
            TransformFromCopy(label1[0], label2[0]),
        )
        self.play(
            Restore(label2),
            ReplacementTransform(diagram_copy, restricted_diagram)
        )
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
        self.play(*[
            ApplyMethod(d.set_prior, 0.4, run_time=2)
            for d in diagrams
        ])
        self.play(*[
            ApplyMethod(d.set_likelihood, 0.3, run_time=2)
            for d in diagrams
        ])
        self.play(*[
            ApplyMethod(d.set_antilikelihood, 0.6, run_time=2)
            for d in diagrams
        ])
        # self.play(prior_tracker.set_value, 0.4, run_time=2)
        # self.play(antilikelihood_tracker.set_value, 0.3, run_time=2)
        # self.play(likelihood_tracker.set_value, 0.6, run_time=2)
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
            icon.brace = brace
            icon.add_updater(lambda m: m.next_to(m.brace, DOWN, SMALL_BUFF))
            diagram.add(icon)
        return diagram

    def get_restricted_diagram(self, diagram):
        restricted_diagram = diagram.deepcopy()
        restricted_diagram.set_x(0)
        restricted_diagram.hypothesis_split.set_opacity(0)
        restricted_diagram.evidence_split.set_opacity(1)
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
    CONFIG = {
        "tex_to_color_map": {
            "P": WHITE,
            "H": HYPOTHESIS_COLOR,
            "E": EVIDENCE_COLOR1,
            "\\neg": RED,
        },
        "bayes_diagram_config": {
            "prior": 1 / 21,
            "likelihood": 0.4,
            "antilikelihood": 0.1,
            "not_evidence_color1": GREY,
            "not_evidence_color2": DARK_GREY,
            "prior_rect_direction": UP,
        },
    }

    def construct(self):
        t2c = self.tex_to_color_map

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
        prior_group = VGroup(
            prior_word, prior_arrow,
            prior_label, prior_example,
            diagram.h_brace,
        )

        # First likelihood split
        like_example = TexMobject("= 0.4")
        like_example.add_updater(
            lambda m: m.next_to(diagram.he_brace, LEFT)
        )
        like_example.update()

        like_label = TexMobject("P(E|H)", tex_to_color_map=t2c)
        like_label.add_updater(
            lambda m: m.next_to(like_example, LEFT)
        )
        like_label.update()

        like_word = TextMobject("``Likelihood''")
        like_word.next_to(like_label, UP, buff=LARGE_BUFF, aligned_edge=LEFT)
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

        hne_people = diagram.people[:6]
        he_people = diagram.people[6:10]
        nhe_people = diagram.people[19::10]
        nhne_people = diagram.people[10:]
        nhne_people.remove(*nhe_people)

        for group in [hne_people, nhne_people]:
            group.generate_target()
            group.target.set_opacity(0.25)
            group.target.set_stroke(BLACK, 0, background=True)

        self.play(
            diagram.he_rect.set_opacity, 1,
            diagram.hne_rect.set_opacity, 1,
            MoveToTarget(hne_people),
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
        not_word = TextMobject("means ", "``not''")
        not_word[1].set_color(RED)
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
            MoveToTarget(nhne_people),
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

        # Recall final answer, geometrically
        he_group = VGroup(diagram.he_rect, he_people)
        nhe_group = VGroup(diagram.nhe_rect, nhe_people)

        denom = VGroup(
            he_group.copy(),
            TexMobject("+"),
            nhe_group.copy(),
        )
        denom.arrange(RIGHT)
        answer = VGroup(
            he_group.copy(),
            Underline(denom, stroke_width=2),
            denom,
        )
        answer.arrange(DOWN)
        answer.scale(0.5)
        answer.to_edge(UP, MED_SMALL_BUFF)
        answer.shift(LEFT)

        equals = TexMobject("=")
        posterior.generate_target()

        post_group = VGroup(posterior.target, equals, answer)
        post_group.arrange(RIGHT)
        post_group.to_corner(UL)

        post_word = TextMobject("``Posterior''")
        post_word.set_color(YELLOW)
        post_word.to_corner(UL, buff=MED_SMALL_BUFF)

        post_arrow = Arrow(
            post_word.get_bottom(),
            posterior.target[1].get_top(),
            buff=0.2,
        )
        post_arrow.set_stroke(WHITE, 5)

        dividing_line = DashedLine(ORIGIN, FRAME_WIDTH * RIGHT)
        dividing_line.set_stroke(WHITE, 1)
        dividing_line.next_to(answer, DOWN)
        dividing_line.set_x(0)

        diagram.add(
            diagram.h_brace,
            diagram.he_brace,
            diagram.nhe_brace,
        )
        diagram.generate_target(use_deepcopy=True)
        diagram.target.scale(0.5, about_edge=DL)
        diagram.target.refresh_braces()

        like_group = VGroup(like_word, like_arrow)
        like_vect = like_group.get_center() - like_label.get_center()
        self.play(
            ShowCreation(dividing_line),
            MoveToTarget(diagram),
            MaintainPositionRelativeTo(like_group, like_label),
            MaintainPositionRelativeTo(
                VGroup(prior_word, prior_arrow),
                prior_label,
            ),
            MoveToTarget(posterior),
            ReplacementTransform(posterior_words, equals),
        )
        like_group.move_to(like_label.get_center() + like_vect)
        self.wait()
        self.play(TransformFromCopy(he_group, answer[0]))
        self.play(ShowCreation(answer[1]))
        self.play(LaggedStart(
            TransformFromCopy(he_group, answer[2][0]),
            GrowFromCenter(answer[2][1]),
            TransformFromCopy(nhe_group, answer[2][2]),
        ))
        self.wait()

        # Write final answer, as a formula
        formula = TexMobject(
            "=", "{P(H) P(E | H)", "\\over",
            "P(H) P(E | H) + P(\\neg H) P(E | \\neg H)}",
            tex_to_color_map=t2c
        )
        formula.scale(0.9)
        formula.next_to(answer, RIGHT)

        ph = formula[2:6]
        peh = formula[6:12]
        over = formula.get_part_by_tex("\\over")
        ph2 = formula[13:17]
        peh2 = formula[17:23]
        pnh = formula[23:28]
        penh = formula[28:]

        parts = VGroup(ph, peh, ph2, peh2, pnh, penh)
        parts.save_state()

        np1 = TexMobject("(\\# I )")[0]
        person = Person()
        person.replace(np1[2], dim_to_match=1)
        person.scale(1.5)
        np1.submobjects[2] = person

        np1.match_height(ph)
        np1.next_to(ph, LEFT, SMALL_BUFF)
        VGroup(np1, ph, peh).match_x(over)

        np2 = np1.copy()
        np2.next_to(ph2, LEFT, SMALL_BUFF)
        VGroup(np2, ph2, peh2).match_width(
            VGroup(ph2, peh2), about_edge=RIGHT
        )

        np3 = np1.copy()
        np3.next_to(pnh, LEFT, SMALL_BUFF)
        VGroup(np3, pnh, penh).match_width(
            VGroup(pnh, penh), about_edge=RIGHT
        )

        nps = VGroup(np1, np2, np3)
        crosses = VGroup(*[Cross(np)[0] for np in nps])

        top_brace = Brace(np1, UP, buff=SMALL_BUFF)
        top_count = Integer(210)
        top_count.add_updater(lambda m: m.next_to(top_brace, UP, SMALL_BUFF))

        low_brace = Brace(np3, DOWN, buff=SMALL_BUFF)
        low_count = Integer(210)
        low_count.add_updater(lambda m: m.next_to(low_brace, DOWN, SMALL_BUFF))

        h_rect = Rectangle(  # Highlighting rectangle
            stroke_color=YELLOW,
            stroke_width=3,
            fill_color=YELLOW,
            fill_opacity=0.25,
        )
        h_rect.replace(diagram.square, stretch=True)

        s_rect = SurroundingRectangle(answer[0])

        diagram.refresh_braces()
        nh_group = VGroup(
            diagram.nh_brace,
            TexMobject("P(\\neg H)", tex_to_color_map=t2c),
            TexMobject("= 20 / 21"),
        )
        nh_group[1].next_to(nh_group[0], UP, SMALL_BUFF)
        nh_group[2].next_to(nh_group[1], RIGHT, SMALL_BUFF)

        self.play(
            Write(formula.get_part_by_tex("=")),
            Write(formula.get_part_by_tex("\\over")),
            run_time=1
        )
        self.play(ShowCreation(s_rect))
        self.wait()
        self.play(
            FadeIn(np1),
            FadeIn(top_brace),
            FadeIn(top_count),
        )
        self.wait()
        self.play(h_rect.replace, diagram.h_rect, {"stretch": True})
        self.play(
            TransformFromCopy(prior_label, ph),
            top_brace.become, Brace(VGroup(np1, ph), UP, buff=SMALL_BUFF),
            ChangeDecimalToValue(top_count, 10),
        )
        self.wait()
        self.play(h_rect.replace, diagram.he_rect, {"stretch": True})
        self.play(
            TransformFromCopy(like_label, peh),
            top_brace.become, Brace(VGroup(np1, peh), UP, buff=SMALL_BUFF),
            ChangeDecimalToValue(top_count, 4)
        )
        self.wait()

        self.play(
            s_rect.move_to, answer[2][0],
            TransformFromCopy(np1, np2),
            TransformFromCopy(ph, ph2),
            TransformFromCopy(peh, peh2),
        )
        self.wait()

        self.play(
            FadeOut(h_rect),
            s_rect.become, SurroundingRectangle(answer[2][2]),
            FadeOut(prior_group),
            FadeIn(nh_group),
        )
        self.wait()
        h_rect.replace(diagram.square, stretch=True)
        self.play(
            FadeIn(np3),
            FadeIn(low_brace),
            FadeIn(low_count),
        )
        self.play(h_rect.replace, diagram.nh_rect, {"stretch": True})
        self.play(
            TransformFromCopy(nh_group[1], pnh),
            low_brace.become, Brace(VGroup(np3, pnh), DOWN, buff=SMALL_BUFF),
            ChangeDecimalToValue(low_count, 200),
        )
        self.play(h_rect.replace, diagram.nhe_rect, {"stretch": True})
        self.play(
            TransformFromCopy(anti_label, penh),
            low_brace.become, Brace(VGroup(np3, penh), DOWN, buff=SMALL_BUFF),
            ChangeDecimalToValue(low_count, 20),
        )
        self.wait()

        # Clean up
        self.play(
            FadeOut(nh_group),
            FadeOut(s_rect),
            FadeOut(h_rect),
            FadeIn(prior_group),
        )
        self.wait()

        self.play(
            ShowCreation(crosses),
            FadeOut(low_brace),
            FadeOut(top_brace),
            FadeOut(low_count),
            FadeOut(top_count),
        )
        self.wait()
        self.play(
            Restore(parts),
            FadeOut(crosses),
            FadeOut(nps),
            answer.set_opacity, 0.2
        )
        self.wait()

        # Write Bayes' theorem
        formula_rect = SurroundingRectangle(formula[1:])
        formula_rect.set_stroke(TEAL, 2)

        bayes_words = TextMobject("Bayes' theorem")
        bayes_words.scale(1.5)
        bayes_words.next_to(formula_rect, UP, SMALL_BUFF)
        bayes_words.match_color(formula_rect)

        self.play(ShowCreation(formula_rect))
        self.play(FadeInFromDown(bayes_words))
        self.wait()

        # Simplify denominator
        simpler_form = get_bayes_formula()[7:]
        simpler_form.move_to(answer)
        pe = simpler_form[-4:].copy()
        pe.save_state()

        big_denom_rect = SurroundingRectangle(VGroup(ph2, penh))
        lil_denom_rect = SurroundingRectangle(pe)
        for rect in big_denom_rect, lil_denom_rect:
            rect.set_stroke(BLUE, 0)
            rect.set_fill(BLUE, 0.25)
        pe.move_to(big_denom_rect)
        pe.set_opacity(0)

        self.play(
            FadeOut(answer),
            FadeIn(simpler_form[:-4])
        )
        self.play(TransformFromCopy(formula_rect, big_denom_rect))
        self.wait()
        self.play(
            Restore(pe),
            ReplacementTransform(big_denom_rect, lil_denom_rect),
            Transform(
                formula_rect,
                SurroundingRectangle(simpler_form, color=TEAL),
            ),
            bayes_words.match_x, simpler_form,
        )
        self.remove(pe)
        self.add(simpler_form)
        self.wait()

        # Show all evidence cases
        he_group_copy = he_group.copy()
        nhe_group_copy = nhe_group.copy()
        copies = VGroup(he_group_copy, nhe_group_copy)

        self.play(
            copies.arrange, RIGHT, {"buff": LARGE_BUFF},
            copies.move_to, DOWN,
            copies.to_edge, RIGHT, LARGE_BUFF,
        )
        self.wait()
        self.play(
            he_group_copy.next_to, VGroup(ph2, peh2), DOWN,
        )
        self.play(
            nhe_group_copy.next_to, VGroup(pnh, penh), DOWN,
        )
        self.wait()
        self.play(
            FadeOut(copies),
            FadeOut(lil_denom_rect),
        )
        self.wait()

        # Name posterior
        self.play(
            GrowArrow(post_arrow),
            FadeInFrom(post_word, RIGHT),
            FadeOut(formula_rect),
            FadeOut(bayes_words),
        )
        self.wait()

        # Show confusion
        randy = Randolph()
        randy.flip()
        randy.next_to(dividing_line, DOWN)
        randy.to_edge(RIGHT)

        prior_rect = SurroundingRectangle(prior_word)
        post_rect = SurroundingRectangle(post_word)
        VGroup(prior_rect, post_rect).set_stroke(WHITE, 2)

        self.play(FadeIn(randy))
        self.play(randy.change, "confused", formula)
        self.play(Blink(randy))
        self.play(randy.change, "horrified", formula)
        self.play(randy.look_at, diagram)
        self.play(Blink(randy))
        self.play(randy.look_at, formula)
        self.play(randy.change, "tired")
        self.wait(2)
        self.play(
            randy.change, "pondering", prior_label,
            ShowCreation(prior_rect)
        )
        self.play(Blink(randy))
        self.play(
            ReplacementTransform(prior_rect, post_rect),
            randy.look_at, post_rect,
        )
        self.play(randy.change, "thinking")
        self.play(FadeOut(post_rect))
        self.play(Blink(randy))
        self.wait()
        self.play(randy.look_at, formula)
        self.play(Blink(randy))
        self.wait()

        # Transition to next scene
        return  # Skip
        to_move = VGroup(posterior, formula)
        self.remove(to_move, *to_move, *to_move[1])
        to_move.generate_target()
        to_move.target[1].scale(1 / 0.9)
        to_move.target.arrange(RIGHT)
        to_move.target.to_corner(UL)

        everything = Group(*self.get_mobjects())

        self.play(
            LaggedStartMap(FadeOutAndShiftDown, everything),
            MoveToTarget(to_move, rate_func=squish_rate_func(smooth, 0.5, 1)),
            run_time=2,
        )

    def get_diagram(self, include_people=True):
        diagram = BayesDiagram(**self.bayes_diagram_config)
        diagram.set_height(5.5)
        diagram.set_width(5.5, stretch=True)
        diagram.move_to(0.5 * DOWN)
        diagram.add_brace_attrs()

        diagram.evidence_split.set_opacity(0)
        diagram.hypothesis_split.set_opacity(0)
        diagram.nh_rect.set_fill(DARK_GREY)

        if include_people:
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


class DiscussFormulaAndAreaModel(CreateFormulaFromDiagram):
    CONFIG = {
        "bayes_diagram_config": {
            "prior_rect_direction": DOWN,
        },
    }

    def construct(self):
        # Show smaller denominator
        t2c = self.tex_to_color_map
        formula = TexMobject(
            "P(H | E)", "=",
            "{P(H) P(E | H)", "\\over",
            "P(H) P(E | H) + P(\\neg H) P(E | \\neg H)}",
            tex_to_color_map=t2c
        )
        equals = formula.get_part_by_tex("=")
        equals_index = formula.index_of_part(equals)
        lhs = formula[:equals_index]
        rhs = formula[equals_index + 1:]
        lhs.next_to(equals, LEFT)
        formula.to_corner(UL)

        alt_rhs = TexMobject(
            "{P(H)P(E|H)", "\\over", "P(E)}",
            "=",
            tex_to_color_map=t2c,
        )
        alt_rhs.next_to(equals, RIGHT, SMALL_BUFF)

        s_rect = SurroundingRectangle(rhs[12:], color=BLUE)

        self.add(formula)
        self.wait()
        self.play(ShowCreation(s_rect))
        self.add(alt_rhs, s_rect)
        self.play(
            VGroup(rhs, s_rect).next_to, alt_rhs, RIGHT, SMALL_BUFF,
            GrowFromCenter(alt_rhs),
        )
        self.play(
            s_rect.become,
            SurroundingRectangle(alt_rhs[12:-1], color=BLUE)
        )
        self.wait()

        # Bring in diagram
        diagram = self.get_diagram(include_people=False)
        diagram.evidence_split.set_opacity(1)
        diagram.set_height(3)
        diagram.set_prior(0.1)

        diagram.refresh_braces()
        diagram.add(
            diagram.h_brace,
            diagram.he_brace,
            diagram.nhe_brace,
        )

        h_label, he_label, nhe_label = labels = [
            TexMobject(tex, tex_to_color_map=t2c)
            for tex in ["P(H)", "P(E|H)", "P(E|\\neg H)"]
        ]
        h_label.add_updater(lambda m: m.next_to(diagram.h_brace, DOWN))
        he_label.add_updater(lambda m: m.next_to(diagram.he_brace, LEFT))
        nhe_label.add_updater(lambda m: m.next_to(diagram.nhe_brace, RIGHT))
        diagram.add(*labels)

        diagram.to_corner(DL)

        he_rect_copy = diagram.he_rect.copy()
        nhe_rect_copy = diagram.nhe_rect.copy()

        self.play(
            FadeIn(diagram),
            # FadeOut(s_rect),
            ReplacementTransform(
                VGroup(s_rect, s_rect.copy()),
                VGroup(he_rect_copy, nhe_rect_copy),
            ),
        )
        self.wait()
        self.play(LaggedStart(
            ApplyMethod(he_rect_copy.next_to, rhs[12:22], DOWN),
            ApplyMethod(nhe_rect_copy.next_to, rhs[23:], DOWN),
            lag_ratio=0.7,
            run_time=1.5
        ))
        self.wait()
        self.play(FadeOut(VGroup(he_rect_copy, nhe_rect_copy)))

        # Tell what to memorize
        big_rect = SurroundingRectangle(formula)
        big_rect.set_stroke(WHITE, 2)
        big_rect.set_fill(BLACK, 0)

        words1 = TextMobject("Don't memorize\\\\this")
        words2 = TextMobject("Remember\\\\this")
        for words in words1, words2:
            words.scale(1.5)
            words.to_edge(RIGHT)

        arrow1 = Arrow(words1.get_corner(UL), big_rect.get_bottom())
        arrow2 = Arrow(words2.get_left(), diagram.square.get_right())

        self.play(
            FadeIn(words1),
            ShowCreation(arrow1),
            ShowCreation(big_rect)
        )
        self.wait()
        self.play(
            ReplacementTransform(arrow1, arrow2),
            FadeOut(words1),
            FadeIn(words2),
            big_rect.set_stroke, WHITE, 0,
            big_rect.set_fill, BLACK, 0.7,
        )
        self.wait()

        # Talk about diagram slices
        to_fade = VGroup(
            diagram.evidence_split,
            diagram.he_brace,
            diagram.nhe_brace,
            he_label, nhe_label,
        )
        to_fade.save_state()

        h_part = VGroup(
            diagram.hypothesis_split,
            diagram.h_brace,
            h_label,
        )
        people = self.get_diagram().people
        people.set_width(diagram.square.get_width() - 0.05)
        people.move_to(diagram.square)

        sides = VGroup(
            DashedLine(
                diagram.square.get_corner(UL),
                diagram.square.get_corner(UR),
            ),
            DashedLine(
                diagram.square.get_corner(UL),
                diagram.square.get_corner(DL),
            ),
        )
        sides.set_stroke(YELLOW, 4)
        ones = VGroup(
            TexMobject("1").next_to(diagram.square, UP),
            TexMobject("1").next_to(diagram.square, LEFT),
        )

        self.play(
            to_fade.set_opacity, 0,
            h_part.set_opacity, 0,
            diagram.square.set_opacity, 1,
            ShowIncreasingSubsets(people),
        )
        self.play(FadeOut(people))
        self.play(
            LaggedStartMap(ShowCreation, sides, lag_ratio=0.8),
            LaggedStartMap(FadeIn, ones, lag_ratio=0.8),
        )
        self.wait()

        self.play(
            h_part.set_opacity, 1,
        )
        diagram.square.set_opacity(0)
        self.wait()
        self.play(
            FadeOut(sides),
            FadeOut(ones),
        )
        self.wait()
        VGroup(
            to_fade[1:],
            to_fade[0][::2],
        ).stretch(0, 1, about_edge=DOWN)
        self.play(
            Restore(to_fade),
            diagram.hypothesis_split.set_opacity, 0,
            diagram.hne_rect.set_opacity, 0.2,
            diagram.nhne_rect.set_opacity, 0.2,
        )
        self.wait()

        # Add posterior bar
        post_bar = always_redraw(
            lambda: self.get_posterior_bar(
                diagram.he_rect,
                diagram.nhe_rect,
            )
        )
        post_label = TexMobject("P(H|E)", tex_to_color_map=t2c)
        post_label.add_updater(lambda m: m.next_to(post_bar.brace, DOWN))

        self.play(
            FadeOut(words2),
            FadeOut(arrow2),
            TransformFromCopy(
                diagram.he_rect, post_bar.rects[0],
            ),
            TransformFromCopy(
                diagram.nhe_rect, post_bar.rects[1],
            ),
            FadeIn(post_bar.brace),
            FadeIn(post_label),
        )
        self.add(post_bar)
        self.wait()

        self.play(
            diagram.set_likelihood, 0.8,
            rate_func=there_and_back,
            run_time=4,
        )
        self.wait()
        self.play(diagram.set_antilikelihood, 0.4)
        self.wait()
        self.play(
            diagram.set_likelihood, 0.8,
            diagram.set_antilikelihood, 0.05,
        )
        self.wait()
        self.play(
            diagram.set_likelihood, 0.4,
            diagram.set_antilikelihood, 0.1,
        )
        self.wait()

        self.play(
            big_rect.set_width, rhs.get_width() + 0.7,
            {"about_edge": RIGHT, "stretch": True},
        )
        self.wait()

        # Terms from formula to sides in diagram
        hs_rect = SurroundingRectangle(alt_rhs[:5], buff=0.05)
        hes_rect = SurroundingRectangle(alt_rhs[5:11], buff=0.05)
        hs_rect.set_stroke(YELLOW, 3)
        hes_rect.set_stroke(BLUE, 3)

        self.play(ShowCreation(hs_rect))
        self.play(ShowCreation(hes_rect))
        self.wait()
        self.play(hs_rect.move_to, h_label)
        self.play(hes_rect.move_to, he_label)
        self.wait()
        self.play(FadeOut(VGroup(hs_rect, hes_rect)))

    def get_posterior_bar(self, he_rect, nhe_rect):
        he_height = he_rect.get_height()
        he_width = he_rect.get_width()
        nhe_height = nhe_rect.get_height()
        nhe_width = nhe_rect.get_width()

        total_width = he_width + nhe_width
        he_area = he_width * he_height
        nhe_area = nhe_width * nhe_height

        posterior = he_area / (he_area + nhe_area)

        new_he_width = posterior * total_width
        new_he_height = he_area / new_he_width
        new_nhe_width = (1 - posterior) * total_width
        new_nhe_height = nhe_area / new_nhe_width

        new_he_rect = Rectangle(
            width=new_he_width,
            height=new_he_height,
        ).match_style(he_rect)
        new_nhe_rect = Rectangle(
            width=new_nhe_width,
            height=new_nhe_height,
        ).match_style(nhe_rect)

        rects = VGroup(new_he_rect, new_nhe_rect)
        rects.arrange(RIGHT, buff=0)

        brace = Brace(
            new_he_rect, DOWN,
            buff=SMALL_BUFF,
            min_num_quads=2,
        )
        result = VGroup(rects, brace)
        result.rects = rects
        result.brace = brace

        # Put positioning elsewhere?
        result.to_edge(RIGHT)
        return result


class RandomShapes(Scene):
    def construct(self):
        diagram = BayesDiagram(0.1, 0.4, 0.1)
        diagram.set_height(3)

        e_part = VGroup(diagram.he_rect, diagram.nhe_rect).copy()
        e_part.set_fill(BLUE)

        circle = Circle()
        circle.set_fill(RED, 0.5)
        circle.set_stroke(RED, 2)
        circle.move_to(diagram)

        tri = Polygon(UP, ORIGIN, RIGHT)
        tri.match_height(diagram)
        tri.set_fill(PURPLE, 0.5)
        tri.set_stroke(PURPLE, 2)
        tri.move_to(diagram)

        h_rect = diagram.h_rect
        h_rect.set_fill(YELLOW, 1)

        pi = TexMobject("\\pi")
        pi.set_height(2)
        pi.set_stroke(GREEN, 2)
        pi.set_fill(GREEN, 0.5)

        events = VGroup(
            e_part,
            h_rect,
            circle,
            pi,
            tri,
        )

        last = VMobject()
        for event in events:
            self.play(
                FadeIn(event),
                FadeOut(last)
            )
            self.wait()
            last = event


class BigArrow(Scene):
    def construct(self):
        arrow = Arrow(
            3 * DOWN + 4 * LEFT,
            3 * RIGHT + DOWN,
            path_arc=50 * DEGREES,
        )

        self.play(ShowCreation(arrow))
        self.wait()


class UsesOfBayesTheorem(Scene):
    def construct(self):
        formula = get_bayes_formula()
        formula.to_corner(UL)
        rhs = formula[7:]

        bubble = ThoughtBubble(direction=RIGHT)
        bubble.set_fill(opacity=0)
        arrow = Vector(RIGHT)
        arrow.next_to(formula, RIGHT, MED_LARGE_BUFF)
        bubble.set_height(2)
        bubble.next_to(arrow, RIGHT, MED_LARGE_BUFF)
        bubble.align_to(formula, UP)
        bar = ProbabilityBar(
            0.1,
            percentage_background_stroke_width=1,
            include_braces=False,
        )
        bar.set_width(0.8 * bubble[-1].get_width())
        bar.move_to(bubble.get_bubble_center())

        scientist = SVGMobject(file_name="scientist")
        programmer = SVGMobject(file_name="programmer")
        randy = Randolph().flip()

        people = VGroup(scientist, programmer, randy)
        people.set_stroke(width=0)
        for person in people:
            person.set_height(2.5)
            if person is not randy:
                person.set_fill(GREY)
                person.set_sheen(0.5, UL)

        people.arrange(RIGHT, buff=2.5)
        # programmer.shift(0.5 * RIGHT)
        people.to_edge(DOWN, buff=LARGE_BUFF)

        self.add(formula)
        self.wait()
        self.play(GrowArrow(arrow))
        self.play(ShowCreation(bubble), FadeIn(bar))
        self.play(bar.p_tracker.set_value, 0.8)
        self.wait()

        # Add people
        for person in [scientist, programmer]:
            self.play(FadeInFrom(person, DOWN))
            rhs_copy = rhs.copy()
            rhs_copy.add_to_back(
                SurroundingRectangle(
                    rhs_copy,
                    fill_color=BLACK,
                    fill_opacity=0.8,
                    stroke_color=WHITE,
                    stroke_width=2,
                )
            )
            rhs_copy.generate_target()
            rhs_copy[0].set_stroke(width=0)
            rhs_copy.target.scale(0.5)
            rhs_copy.target.move_to(person.get_corner(DR))
            self.add(rhs_copy, formula)
            self.play(MoveToTarget(rhs_copy))
            self.wait()
            person.add(rhs_copy)

        self.play(FadeInFromDown(randy))
        self.play(randy.change, "pondering")
        self.play(Blink(randy))
        bubble_group = VGroup(bubble, bar)
        self.play(
            bubble_group.scale, 1.4,
            bubble_group.move_to, randy.get_corner(UL), DR,
            randy.look_at, bubble,
            FadeOut(arrow),
        )
        self.wait()
        self.play(Blink(randy))
        self.play(bar.p_tracker.set_value, 0.3, run_time=3)
        self.play(randy.change, "thinking")
        self.play(Blink(randy))
        self.wait()

        self.play(LaggedStartMap(
            FadeOutAndShift,
            VGroup(*people, bubble_group),
            lambda m: (m, DOWN),
            lag_ratio=0.15,
        ))


class AskAboutWhenProbabilityIsIntuitive(TeacherStudentsScene):
    def construct(self):
        words = TextMobject("What makes probability\\\\more intuitive?")
        words.move_to(self.hold_up_spot, DOWN)
        words.shift_onto_screen()

        self.play(
            self.teacher.change, "speaking",
            self.get_student_changes(
                "pondering", "sassy", "happy",
                look_at_arg=self.screen,
            )
        )
        self.wait(2)

        self.play(
            self.teacher.change, "raise_right_hand",
            FadeInFrom(words, DOWN),
            self.get_student_changes("erm", "pondering", "confused")
        )
        self.wait(2)
        self.play(
            words.scale, 2,
            words.center,
            words.to_edge, UP,
            self.teacher.change, "pondering", 3 * UP,
            self.get_student_changes(
                "pondering", "thinking", "thinking",
                look_at_arg=3 * UP,
            )
        )
        self.wait(6)


class IntroduceLinda(DescriptionOfSteve):
    def construct(self):
        # Kahneman and Tversky
        images = self.get_images()

        self.play(
            LaggedStartMap(
                FadeInFrom, images,
                lambda m: (m, LEFT),
                lag_ratio=0.3,
                run_time=3,
            )
        )
        self.wait()

        # Add steve
        steve = Steve()
        steve.set_height(3)
        steve.move_to(2 * RIGHT)
        steve.to_edge(DOWN, buff=LARGE_BUFF)
        steve_words = self.get_description()
        steve_words.scale(0.8)
        steve_words.next_to(steve, UP, LARGE_BUFF)

        self.play(LaggedStart(
            FadeInFrom(steve, LEFT),
            FadeInFrom(steve_words, LEFT),
        ))
        self.wait()

        # Replace with Linda
        linda = Linda()
        linda_words = self.get_linda_description()
        linda_words.scale(0.8)
        linda.replace(steve)
        linda_words.move_to(steve_words)

        self.play(
            LaggedStart(
                FadeOutAndShift(steve_words, 2 * RIGHT),
                FadeOutAndShift(steve, 2 * RIGHT),
                FadeInFrom(linda, 2 * LEFT),
                lag_ratio=0.15,
            )
        )
        self.wait()

        self.play(
            FadeIn(linda_words),
            lag_ratio=0.1,
            run_time=6,
            rate_func=linear,
        )
        self.wait()

        # Ask question
        options = VGroup(
            TextMobject("1) Linda is a bank teller."),
            TextMobject(
                "2) Linda is a bank teller and is active\\\\",
                "\\phantom{2)} in the feminist movement.",
                alignment="",
            ),
        )
        options.arrange(DOWN, buff=LARGE_BUFF, aligned_edge=LEFT)
        options.to_edge(DOWN, buff=LARGE_BUFF)

        self.play(
            linda.match_height, linda_words,
            linda.next_to, linda_words, LEFT, LARGE_BUFF,
            LaggedStartMap(
                FadeOutAndShift, images,
                lambda m: (m, 2 * LEFT),
            )
        )
        for option in options:
            self.play(FadeIn(option, lag_ratio=0.1, run_time=2))
            self.wait()

        # Show result
        rect = SurroundingRectangle(options[1], color=RED)
        options.generate_target()
        rect.generate_target()
        VGroup(options.target, rect.target).to_edge(LEFT)

        result = VGroup(
            Integer(85, unit="\\%"),
            TextMobject("chose this!")
        )
        result.arrange(RIGHT)
        result.scale(1.25)
        result.set_color(RED)
        result.move_to(rect)
        result.to_edge(RIGHT)
        result.shift(2 * UP)
        arrow = Arrow(result.get_bottom(), rect.target.get_corner(UR))

        self.play(
            MoveToTarget(options),
            MoveToTarget(rect),
            VFadeIn(rect),
            FadeInFrom(result, LEFT),
            GrowArrow(arrow)
        )
        self.wait()

        # Show subsets
        fb_words = TextMobject("Active feminist\\\\bank tellers")
        fb_words.scale(0.5)
        fb_words.set_stroke(BLACK, 0, background=True)
        fb_set = Circle()
        fb_set.flip(RIGHT)
        fb_set.rotate(3 * TAU / 8)
        fb_set.set_stroke(WHITE, 1)
        fb_set.set_fill(YELLOW, 0.5)
        fb_set.replace(fb_words, stretch=True)
        fb_set.scale(1.2)
        fb_set.stretch(1.4, 1)
        fb_group = VGroup(fb_set, fb_words)
        fb_group.move_to(linda_words, RIGHT)

        b_set = fb_set.copy()
        b_set.set_fill(BLUE)
        b_set.scale(3, about_edge=RIGHT)
        b_set.stretch(1.5, 1)
        b_set.to_corner(UR)
        b_words = TextMobject("Bank\\\\tellers")
        b_words.next_to(b_set.get_left(), RIGHT, LARGE_BUFF)

        self.play(
            FadeOut(linda_words),
            TransformFromCopy(rect, fb_set),
            ReplacementTransform(
                VectorizedPoint(rect.get_center()),
                fb_words,
            ),
        )
        self.add(fb_set, fb_words)
        self.wait()
        self.add(b_set, fb_set, fb_words)
        self.play(
            DrawBorderThenFill(b_set),
            TransformFromCopy(
                options[0][0][10:], b_words[0]
            ),
        )
        sets_group = VGroup(b_set, b_words, fb_set, fb_words)
        self.add(sets_group)
        self.wait()

        # Reduce 85
        number = result[0]

        self.play(
            LaggedStart(
                FadeOut(arrow),
                FadeOut(result[1]),
                FadeOut(rect),
                FadeOut(options[0]),
                FadeOut(options[1]),
            ),
            number.scale, 1.5,
            number.move_to, DOWN,
        )
        self.play(
            ChangeDecimalToValue(number, 0),
            UpdateFromAlphaFunc(
                number,
                lambda m, a: m.set_color(interpolate_color(
                    RED, GREEN, a,
                ))
            ),
            run_time=2,
        )
        self.wait()

        self.play(
            FadeOut(number),
            FadeOut(sets_group),
            FadeIn(linda_words),
        )

        # New options
        words = TextMobject("100 people fit this description.  How many are:")
        words.set_color(BLUE_B)
        kw = {"tex_to_color_map": {"\\underline{\\qquad}": WHITE}}
        new_options = VGroup(
            TextMobject("1) Bank tellers? \\underline{\\qquad} of 100", **kw),
            TextMobject(
                "2) Bank tellers and active in the",
                " feminist movement? \\underline{\\qquad} of 100",
                **kw
            ),
        )
        new_options.scale(0.9)
        new_options.arrange(DOWN, aligned_edge=LEFT, buff=MED_LARGE_BUFF)
        new_options.to_edge(DOWN, buff=LARGE_BUFF)

        words.next_to(new_options, UP, LARGE_BUFF)

        self.play(
            FadeIn(words, lag_ratio=0.1, rate_func=linear)
        )
        self.wait()
        for option in new_options:
            self.play(FadeIn(option))
            self.wait()

        example_numbers = VGroup(Integer(8), Integer(5))
        for exn, option in zip(example_numbers, new_options):
            line = option.get_part_by_tex("underline")
            exn.scale(1.1)
            exn.next_to(line, UP, buff=0.05)
            exn.set_color(YELLOW)
            self.play(Write(exn))
        self.wait()

    def get_images(self):
        images = Group(
            ImageMobject("kahneman"),
            ImageMobject("tversky"),
        )
        images.set_height(3.5)
        images.arrange(DOWN, buff=0.5)
        images.to_edge(LEFT, buff=MED_LARGE_BUFF)

        names = VGroup(
            TextMobject("Kahneman", alignment=""),
            TextMobject("Tversky", alignment=""),
        )
        for name, image in zip(names, images):
            name.next_to(image, DOWN)
            image.name = name
            image.add(name)
        images.arrange(DOWN, buff=1, aligned_edge=LEFT)
        images.set_height(FRAME_HEIGHT - 1)
        images.to_edge(LEFT)
        return images

    def get_linda_description(self):
        result = TextMobject(
            "Linda is 31 years old, single, outspoken, and\\\\",
            "very bright. She majored in philosophy. As a \\\\",
            "student, she was deeply concerned with issues\\\\",
            "of discrimination and social justice, and also\\\\",
            "participated in anti-nuclear demonstrations.\\\\",
            alignment="",
            tex_to_color_map={
                "deeply concerned with issues": YELLOW,
                "of discrimination": YELLOW,
            }
        )
        return result


class LindaDescription(IntroduceLinda):
    def construct(self):
        words = self.get_linda_description()
        words.set_color(WHITE)

        highlighted_part = VGroup(
            *words.get_part_by_tex("deeply"),
            *words.get_part_by_tex("discrimination"),
        )

        self.add(words)
        self.play(
            FadeIn(words),
            run_time=3,
            lag_ratio=0.01,
            rate_func=linear,
        )
        self.wait(1)
        self.play(
            highlighted_part.set_color, YELLOW,
            lag_ratio=0.1,
            run_time=2
        )
        self.wait()


class AlternatePhrasings(PiCreatureScene):
    CONFIG = {
        "camera_config": {
            "background_color": DARKER_GREY,
        }
    }

    def construct(self):
        randy = self.pi_creature

        phrases = VGroup(
            TextMobject("40 out of 100"),
            TexMobject("40\\%"),
            TexMobject("0.4"),
            TextMobject("What's more likely$\\dots$"),
        )
        for phrase in phrases:
            phrase.scale(1.5)
            phrase.next_to(randy, RIGHT, buff=LARGE_BUFF)
            phrase.align_to(randy, UP)

        def push_down(phrase):
            phrase.scale(0.8, about_edge=LEFT)
            phrase.shift(1 * DOWN)
            phrase.set_opacity(0.5)
            return phrase

        bubble = randy.get_bubble()
        content_width = 4.5

        people = VGroup(*[Person() for x in range(100)])
        people.arrange_in_grid(n_cols=20)
        people.set_width(content_width)
        people.move_to(bubble.get_bubble_center())
        people.shift(SMALL_BUFF * UP)
        people[:40].set_color(YELLOW)

        bar = ProbabilityBar(0.9999)
        bar.set_width(content_width)
        bar.move_to(people)

        steve = Steve()
        steve.set_height(1)
        steve_words = TextMobject("seems bookish...")
        steve_words.next_to(steve, RIGHT, MED_LARGE_BUFF)
        steve.add(steve_words)

        linda = Linda()
        linda.set_height(1)
        linda_words = TextMobject("seems activist...")
        linda_words.next_to(linda, RIGHT, MED_LARGE_BUFF)
        linda.add(linda_words)

        stereotypes = VGroup(steve, linda)
        stereotypes.arrange(DOWN, buff=MED_SMALL_BUFF, aligned_edge=LEFT)
        stereotypes.move_to(people)

        self.play(
            FadeInFrom(phrases[0], UP),
            randy.change, "pondering",
        )
        self.play(
            DrawBorderThenFill(bubble, lag_ratio=0.1),
            FadeIn(people, lag_ratio=0.1),
            randy.change, "thinking", people,
        )
        self.wait()
        self.play(
            FadeInFrom(phrases[1], UP),
            randy.change, "confused", phrases[1],
            FadeOut(people),
            ApplyFunction(push_down, phrases[0]),
            FadeIn(bar),
        )
        self.play(bar.p_tracker.set_value, 0.4)
        bar.clear_updaters()
        self.play(
            FadeInFrom(phrases[2], UP),
            ApplyFunction(push_down, phrases[:2]),
            FadeOut(bar.percentages),
            randy.change, "guilty",
        )
        self.wait()
        bar.remove(bar.percentages)
        self.play(
            FadeInFrom(phrases[3], UP),
            ApplyFunction(push_down, phrases[:3]),
            FadeOut(bar),
            FadeIn(stereotypes),
            randy.change, "shruggie", stereotypes,
        )
        self.wait(6)


class WhenDiscreteChunksArentSoClean(Scene):
    def construct(self):
        squares = VGroup(*[Square() for x in range(100)])
        squares.arrange_in_grid(n_cols=10, buff=0)
        squares.set_stroke(WHITE, 1)
        squares.set_fill(DARKER_GREY, 1)
        squares.set_height(6)
        squares.to_edge(DOWN)

        target_p = 0.3612

        rain, sun = icon_templates = VGroup(
            SVGMobject("rain_cloud"),
            SVGMobject("sunny"),
        )
        for icon in icon_templates:
            icon.set_width(0.6 * squares[0].get_width())
            icon.set_stroke(width=0)
            icon.set_sheen(0.5, UL)
        rain.set_color(BLUE_E)
        sun.set_color(YELLOW)

        partial_rects = VGroup()
        icons = VGroup()
        q_marks = VGroup()
        for i, square in enumerate(squares):
            icon = rain.copy() if i < 40 else sun.copy()
            icon.move_to(square)
            icons.add(icon)

            partial_rect = square.copy()
            partial_rect.set_stroke(width=0)
            partial_rect.scale(0.95)
            partial_rect.stretch(
                0.4,
                0,
                about_edge=RIGHT
            )
            partial_rects.add(partial_rect)

            q_mark = TexMobject("?")
            q_mark.replace(partial_rect, dim_to_match=0)
            q_mark.scale(0.8)
            q_marks.add(q_mark)

        p_label = VGroup(
            TexMobject("P", "(", "\\text{Rain}", ")", "="),
            DecimalNumber(40, unit="\\%", num_decimal_places=2)
        )
        percentage = p_label[1]
        p_label.arrange(RIGHT)
        p_label.to_edge(UP)
        p_label[0].set_color_by_tex("Rain", BLUE)
        percentage.align_to(p_label[0][0], DOWN)

        alt_percentage = Integer(0, unit="\\%")
        alt_percentage.move_to(percentage, LEFT)

        self.add(squares)
        self.add(p_label[0])
        self.play(
            ChangeDecimalToValue(alt_percentage, 40),
            ShowIncreasingSubsets(icons[:40])
        )
        self.play(FadeIn(icons[40:]))
        self.wait()
        self.remove(alt_percentage)
        self.add(percentage)
        self.play(
            ChangeDecimalToValue(percentage, 100 * target_p),
            FadeIn(partial_rects[30:40]),
            FadeIn(q_marks[30:40], lag_ratio=0.3)
        )
        self.wait(2)

        l_rect = Rectangle(fill_color=BLUE_D)
        r_rect = Rectangle(fill_color=LIGHT_GREY)
        rects = VGroup(l_rect, r_rect)
        for rect, p in (l_rect, target_p), (r_rect, 1 - target_p):
            rect.set_height(squares.get_height())
            rect.set_width(p * squares.get_width(), stretch=True)
            rect.set_stroke(WHITE, 2)
            rect.set_fill(opacity=1)
        rects.arrange(RIGHT, buff=0)
        rects.move_to(squares)

        brace = Brace(l_rect, UP, buff=SMALL_BUFF)

        sun = icons[40].copy()
        rain = icons[0].copy()
        for mob, rect in [(rain, l_rect), (sun, r_rect)]:
            mob.generate_target()
            mob.target.set_stroke(BLACK, 3, background=True)
            mob.target.set_height(1)
            mob.target.move_to(rect)
        self.play(
            FadeIn(rects),
            MoveToTarget(rain),
            MoveToTarget(sun),
            GrowFromCenter(brace),
            p_label.shift,
            brace.get_top() + MED_SMALL_BUFF * UP -
            percentage.get_bottom(),
        )
        self.wait()

        # With updaters
        full_width = rects.get_width()
        rain.add_updater(lambda m: m.move_to(l_rect))
        sun.add_updater(lambda m: m.move_to(r_rect))
        r_rect.add_updater(lambda m: m.set_width(
            full_width - l_rect.get_width(),
            about_edge=RIGHT,
            stretch=True,
        ))
        brace.add_updater(lambda m: m.match_width(l_rect, stretch=True))
        brace.add_updater(lambda m: m.next_to(l_rect, UP, SMALL_BUFF))
        percentage.add_updater(lambda m: m.set_value(
            100 * l_rect.get_width() / full_width,
        ))
        percentage.add_updater(lambda m: m.next_to(brace, UP, MED_SMALL_BUFF))

        self.play(
            MaintainPositionRelativeTo(p_label[0], percentage),
            l_rect.stretch, 2, 0, {"about_edge": LEFT},
            run_time=8,
            rate_func=there_and_back,
        )


class RandomnessVsProportions(Scene):
    def construct(self):
        prob_word = TextMobject("Probability")
        unc_word = TextMobject("Uncertainty")
        prop_word = TextMobject("Proportions")
        words = VGroup(prop_word, prob_word, unc_word)
        words.arrange(RIGHT, buff=LARGE_BUFF)
        words.set_width(FRAME_WIDTH - 1)
        words.to_edge(UP)
        arrows = VGroup()
        for w1, w2 in zip(words, words[1:]):
            arrow = TexMobject("\\rightarrow")
            arrow.move_to(midpoint(w1.get_right(), w2.get_left()))
            arrows.add(arrow)

        random_dice = self.get_random_dice()
        random_dice.next_to(unc_word, DOWN, LARGE_BUFF)

        diagram = self.get_dice_diagram()
        diagram.next_to(prop_word, DOWN, LARGE_BUFF)
        diagram.shift_onto_screen()

        grid = diagram[0]
        border = grid[0][0].copy()
        border.set_stroke(BLACK, 3)
        border.set_fill(WHITE, opacity=0.2)
        border.scale(1.02)

        def update_border(border):
            r1, r2 = random_dice
            i = len(r1[1]) - 1
            j = len(r2[1]) - 1
            border.move_to(diagram[0][i][j])
        border.add_updater(update_border)

        example = VGroup(
            TextMobject("P(X = 5)", tex_to_color_map={"5": YELLOW}),
            Line(LEFT, RIGHT)
        )
        example.arrange(RIGHT)
        example.next_to(grid, RIGHT, LARGE_BUFF)
        example.align_to(random_dice, RIGHT)
        example.shift(0.5 * DOWN)
        grid_copy = grid.copy()
        five_part = VGroup(*[
            square
            for i, row in enumerate(grid_copy)
            for j, square in enumerate(row)
            if i + j == 3
        ])

        self.play(FadeInFromDown(prob_word))
        self.play(
            FadeInFrom(unc_word, LEFT),
            Write(arrows[1]),
        )
        self.add(random_dice)
        self.wait(9)
        self.play(
            FadeInFrom(prop_word, RIGHT),
            Write(arrows[0])
        )
        self.play(FadeIn(diagram))
        self.add(border)
        self.wait(2)

        self.play(FadeIn(example))
        self.add(grid_copy, diagram[1])
        self.play(
            grid_copy.set_width, 0.8 * example[1].get_width(),
            grid_copy.next_to, example[1], DOWN,
        )
        self.play(five_part.copy().next_to, example[1], UP)
        self.wait(6)

    def get_die_faces(self):
        dot = Dot()
        dot.set_width(0.15)
        dot.set_color(BLUE_B)

        square = Square()
        square.round_corners(0.25)
        square.set_stroke(WHITE, 2)
        square.set_fill(DARKER_GREY, 1)
        square.set_width(0.6)

        edge_groups = [
            (ORIGIN,),
            (UL, DR),
            (UL, ORIGIN, DR),
            (UL, UR, DL, DR),
            (UL, UR, ORIGIN, DL, DR),
            (UL, UR, LEFT, RIGHT, DL, DR),
        ]

        arrangements = VGroup(*[
            VGroup(*[
                dot.copy().move_to(square.get_critical_point(ec))
                for ec in edge_group
            ])
            for edge_group in edge_groups
        ])
        square.set_width(1)

        faces = VGroup(*[
            VGroup(square.copy(), arrangement)
            for arrangement in arrangements
        ])
        faces.arrange(RIGHT)

        return faces

    def get_random_dice(self):
        faces = list(self.get_die_faces())

        def get_random_pair():
            result = VGroup(*random.sample(faces, 2)).copy()
            result.arrange(RIGHT)
            for mob in result:
                mob.shift(random.random() * RIGHT * MED_SMALL_BUFF)
                mob.shift(random.random() * UP * MED_SMALL_BUFF)
            return result

        result = VGroup(*get_random_pair())
        result.time = 0
        result.iter_count = 0

        def update_result(group, dt):
            group.time += dt
            group.iter_count += 1
            if int(group.time) % 3 == 2:
                group.set_stroke(YELLOW)
                return group
            elif result.iter_count % 3 != 0:
                return group
            else:
                pair = get_random_pair()
                pair.move_to(group)
                group.submobjects = [*pair]

        result.add_updater(update_result)
        result.update()
        return result

    def get_dice_diagram(self):
        grid = VGroup(*[
            VGroup(*[
                Square() for x in range(6)
            ]).arrange(RIGHT, buff=0)
            for y in range(6)
        ]).arrange(DOWN, buff=0)
        grid.set_stroke(WHITE, 1)
        grid.set_height(5)

        colors = color_gradient([RED, YELLOW, GREEN, BLUE], 11)

        numbers = VGroup()
        for i, row in enumerate(grid):
            for j, square in enumerate(row):
                num = Integer(i + j + 2)
                num.set_height(square.get_height() - MED_LARGE_BUFF)
                num.move_to(square)
                # num.set_stroke(BLACK, 2, background=True)
                num.set_fill(DARK_GREY)
                square.set_fill(colors[i + j], 0.9)
                numbers.add(num)

        faces = VGroup()
        face_templates = self.get_die_faces()
        face_templates.scale(0.5)
        for face, row in zip(face_templates, grid):
            face.next_to(row, LEFT, MED_SMALL_BUFF)
            faces.add(face)
        for face, square in zip(faces.copy(), grid[0]):
            face.next_to(square, UP, MED_SMALL_BUFF)
            faces.add(face)

        result = VGroup(grid, numbers, faces)
        return result


class JustRandomDice(RandomnessVsProportions):
    def construct(self):
        random_dice = self.get_random_dice()
        random_dice.center()

        self.add(random_dice)
        self.wait(60)


class BayesTheoremOnProportions(Scene):
    def construct(self):
        # Place on top of visuals from "HeartOfBayes"
        formula = get_bayes_formula()
        formula.scale(1.5)

        title = TextMobject("Bayes' theorem")
        title.scale(2)
        title.next_to(formula, UP, LARGE_BUFF)
        group = VGroup(formula, title)

        equals = TexMobject("=")
        equals.next_to(formula, RIGHT)
        h_line = Line(LEFT, RIGHT)
        h_line.set_width(4)
        h_line.next_to(equals, RIGHT)
        h_line.set_stroke(WHITE, 3)

        self.add(group)
        self.wait()
        self.play(
            group.to_edge, LEFT,
            MaintainPositionRelativeTo(equals, group),
            VFadeIn(equals),
            MaintainPositionRelativeTo(h_line, group),
            VFadeIn(h_line),
        )

        # People
        people = VGroup(*[Person() for x in range(7)])
        people.arrange(RIGHT)
        people.match_width(h_line)
        people.next_to(h_line, DOWN)
        people.set_color(BLUE_E)
        people[:3].set_color(GREEN)
        num_people = people[:3].copy()

        self.play(FadeIn(people, lag_ratio=0.1))
        self.play(num_people.next_to, h_line, UP)
        self.wait(0.5)

        # Diagrams
        diagram = BayesDiagram(0.25, 0.5, 0.2)
        diagram.set_width(0.7 * h_line.get_width())
        diagram.next_to(h_line, DOWN)
        diagram.hne_rect.set_fill(opacity=0.1)
        diagram.nhne_rect.set_fill(opacity=0.1)
        num_diagram = diagram.deepcopy()
        num_diagram.next_to(h_line, UP)
        num_diagram.nhe_rect.set_fill(opacity=0.1)
        low_diagram_rects = VGroup(diagram.he_rect, diagram.nhe_rect)
        top_diagram_rects = VGroup(num_diagram.he_rect)

        self.play(
            FadeOut(people),
            FadeOut(num_people),
            FadeIn(diagram),
            FadeIn(num_diagram),
        )
        self.wait()

        # Circle each part
        E_part = VGroup(formula[4], *formula[19:]).copy()
        H_part = VGroup(formula[2], *formula[8:18]).copy()

        E_arrow = Vector(UP, color=BLUE)
        E_arrow.next_to(E_part[0], DOWN)
        E_words = TextMobject(
            "...among cases where\\\\$E$ is True",
            tex_to_color_map={"$E$": BLUE},
        )
        E_words.next_to(E_arrow, DOWN)
        H_arrow = Vector(DOWN, color=YELLOW)
        H_arrow.next_to(H_part[0], UP)
        H_words = TextMobject(
            "How often is\\\\$H$ True...",
            tex_to_color_map={"$H$": YELLOW},
        )
        H_words.next_to(H_arrow, UP)

        denom_rect = SurroundingRectangle(E_part[1:], color=BLUE)
        numer_rect = SurroundingRectangle(H_part[1:], color=YELLOW)

        self.play(
            formula.set_opacity, 0.5,
            ApplyMethod(
                E_part.set_stroke, YELLOW, 3, {"background": True},
                rate_func=there_and_back,
            ),
            FadeIn(denom_rect),
            ShowCreation(E_arrow),
            FadeInFrom(E_words, UP),
            low_diagram_rects.set_stroke, TEAL, 3,
        )
        self.wait()
        self.play(
            FadeOut(E_part),
            FadeIn(H_part),
            FadeOut(denom_rect),
            FadeIn(numer_rect),
            ShowCreation(H_arrow),
            FadeInFrom(H_words, DOWN),
            FadeOutAndShift(title, UP),
            low_diagram_rects.set_stroke, WHITE, 1,
            top_diagram_rects.set_stroke, YELLOW, 3,
        )
        self.wait()


class GlimpseOfNextVideo(GraphScene):
    CONFIG = {
        "x_axis_label": "",
        "y_axis_label": "",
        "x_min": 0,
        "x_max": 15,
        "x_axis_width": 12,
        "y_min": 0,
        "y_max": 1.0,
        "y_axis_height": 6,
        "y_tick_frequency": 0.125,
        "add_x_coords": True,
        "formula_position": ORIGIN,
        "dx": 0.2,
    }

    def setup(self):
        super().setup()
        self.setup_axes()
        self.y_axis.add_numbers(
            0.25, 0.5, 0.75, 1,
            number_config={
                "num_decimal_places": 2,
            },
            direction=LEFT,
        )
        if self.add_x_coords:
            self.x_axis.add_numbers(*range(1, 15),)

    def construct(self):
        f1 = self.prior

        def f2(x):
            return f1(x) * self.likelihood(x)

        pe = scipy.integrate.quad(f2, 0, 20)[0]

        graph1 = self.get_graph(f1)
        graph2 = self.get_graph(f2)

        rects1 = self.get_riemann_rectangles(graph1, dx=self.dx)
        rects2 = self.get_riemann_rectangles(graph2, dx=self.dx)

        rects1.set_color(YELLOW_D)
        rects2.set_color(BLUE)
        for rects in rects1, rects2:
            rects.set_stroke(WHITE, 1)

        rects1.save_state()
        rects1.stretch(0, 1, about_edge=DOWN)

        formula = self.get_formula()

        self.play(
            FadeInFromDown(formula[:4]),
            Restore(rects1, lag_ratio=0.05, run_time=2)
        )
        self.wait()
        self.add(rects1.copy().set_opacity(0.4))
        self.play(
            FadeInFromDown(formula[4:10]),
            Transform(rects1, rects2),
        )
        self.wait()
        self.play(
            rects1.stretch, 1 / pe, 1, {"about_edge": DOWN},
            Write(formula[10:], run_time=1)
        )
        self.wait()

    def get_formula(self):
        formula = TexMobject(
            "p(H) p(E|H) \\over p(E)",
            tex_to_color_map={
                "H": HYPOTHESIS_COLOR,
                "E": EVIDENCE_COLOR1,
            },
            substrings_to_isolate=list("p(|)")
        )
        formula.move_to(self.formula_position)
        return formula

    def prior(self, x):
        return (x**3 / 6) * np.exp(-x)

    def likelihood(self, x):
        return np.exp(-0.5 * x)


class ComingUp(Scene):
    CONFIG = {
        "camera_config": {"background_color": DARK_GREY}
    }

    def construct(self):
        rect = ScreenRectangle()
        rect.set_height(6)
        rect.set_fill(BLACK, 1)
        rect.set_stroke(WHITE, 2)

        words = TextMobject("Later...")
        words.scale(2)
        words.to_edge(UP)
        rect.next_to(words, DOWN)

        self.add(rect)
        self.play(FadeIn(words))
        self.wait()


class QuestionSteveConclusion(HeartOfBayesTheorem, DescriptionOfSteve):
    def construct(self):
        # Setup
        steve = Steve()
        steve.shift(UP)
        self.add(steve)

        kt = Group(
            ImageMobject("kahneman"),
            ImageMobject("tversky"),
        )
        kt.arrange(DOWN)
        kt.set_height(6)
        randy = Randolph()
        kt.next_to(randy, RIGHT, LARGE_BUFF)
        randy.align_to(kt, DOWN)

        farmers = VGroup(*[Farmer() for x in range(20)])
        farmers.arrange_in_grid(n_cols=5)
        people = VGroup(Librarian(), farmers)
        people.arrange(RIGHT, aligned_edge=UP)
        people.set_height(3)
        people.next_to(randy.get_corner(UL), UP)
        cross = Cross(people)
        cross.set_stroke(RED, 8)

        # Question K&T
        self.play(
            steve.scale, 0.5,
            steve.to_corner, DL,
            FadeIn(randy),
            FadeInFromDown(kt, lag_ratio=0.3),
        )
        self.play(randy.change, "sassy")
        self.wait()
        self.play(
            FadeInFrom(people, RIGHT, lag_ratio=0.01),
            randy.change, "raise_left_hand", people,
        )
        self.wait()
        self.play(
            ShowCreation(cross),
            randy.change, "angry"
        )
        self.wait()

        # Who is Steve?
        people.add(cross)
        self.play(
            people.scale, 0.3,
            people.to_corner, UL,
            steve.scale, 1.5,
            steve.next_to, randy.get_corner(UL), LEFT,
            randy.change, "pondering", steve,
        )
        self.play(randy.look_at, steve)
        self.play(Blink(randy))

        kt.generate_target()
        steve.generate_target()
        steve.target.set_height(0.9 * kt[0].get_height())
        group = Group(kt.target[0], steve.target, kt.target[1])
        group.arrange(RIGHT)
        group.to_edge(RIGHT)

        self.play(
            MoveToTarget(kt),
            MoveToTarget(steve),
            randy.shift, 2 * LEFT,
            randy.change, 'erm', kt.target,
            FadeOutAndShift(people, 2 * LEFT),
        )
        self.remove(people, cross)
        self.play(Blink(randy))
        self.wait()

        jessy = Randolph(color=BLUE_B)
        jessy.next_to(randy, LEFT, MED_LARGE_BUFF)
        steve.target.match_height(randy)
        steve.target.next_to(randy, RIGHT, MED_LARGE_BUFF)
        morty = Mortimer()
        morty.next_to(steve.target, RIGHT, MED_LARGE_BUFF)
        morty.look_at(steve.target),
        jessy.look_at(steve.target),
        VGroup(jessy, morty, steve.target).to_edge(DOWN)
        pis = VGroup(randy, jessy, morty)

        self.play(
            LaggedStartMap(FadeOutAndShift, kt, lambda m: (m, 3 * UR)),
            MoveToTarget(steve),
            randy.to_edge, DOWN,
            randy.change, "happy", steve.target,
            FadeIn(jessy),
            FadeIn(morty),
        )
        self.play(LaggedStart(*[
            ApplyMethod(pi.change, "hooray", steve)
            for pi in pis
        ]))
        self.play(Blink(morty))
        self.play(Blink(jessy))

        # The assumption changes the prior
        diagram = self.get_diagram(0.05, 0.4, 0.1)
        diagram.nhne_rect.set_fill(DARK_GREY)
        diagram.set_height(3.5)
        diagram.center().to_edge(UP, buff=MED_SMALL_BUFF)

        self.play(
            FadeIn(diagram),
            *[
                ApplyMethod(pi.change, "pondering", diagram)
                for pi in pis
            ],
        )
        self.play(diagram.set_prior, 0.5)
        self.play(Blink(jessy))
        self.wait()
        self.play(Blink(morty))
        self.play(
            morty.change, "raise_right_hand", diagram,
            ApplyMethod(diagram.set_prior, 0.9, run_time=2),
        )
        self.play(Blink(randy))
        self.wait()

        # Likelihood of description
        description = self.get_description()
        description.scale(0.5)
        description.to_corner(UL)

        self.play(
            FadeIn(description),
            *[ApplyMethod(pi.change, "sassy", description) for pi in pis]
        )
        self.play(
            diagram.set_likelihood, 0.2,
            run_time=2,
        )
        self.play(
            diagram.set_antilikelihood, 0.5,
            run_time=2,
        )
        self.play(Blink(jessy))
        self.play(Blink(randy))
        self.wait()

        # Focus on diagram
        diagram.generate_target()
        diagram.target.set_height(6)
        diagram.target.move_to(3 * LEFT)

        formula = get_bayes_formula()
        formula.scale(0.75)
        formula.to_corner(UR)

        self.play(
            FadeInFromDown(formula),
            LaggedStart(*[
                ApplyMethod(pi.change, "thinking", formula)
                for pi in pis
            ])
        )
        self.play(Blink(randy))
        self.play(
            LaggedStartMap(
                FadeOutAndShiftDown,
                VGroup(description, *pis, steve),
            ),
            MoveToTarget(diagram, run_time=3),
            ApplyMethod(
                formula.scale, 1.5, {"about_edge": UR},
                run_time=2.5,
            ),
        )
        self.wait()

        kw = {"run_time": 2}
        self.play(diagram.set_prior, 0.1, **kw)
        self.play(diagram.set_prior, 0.6, **kw)
        self.play(diagram.set_likelihood, 0.5, **kw),
        self.play(diagram.set_antilikelihood, 0.1, **kw),
        self.wait()


class WhoAreYou(Scene):
    def construct(self):
        words = TextMobject("Who are you?")
        self.add(words)


class FadeInHeart(Scene):
    def construct(self):
        heart = SuitSymbol("hearts")

        self.play(FadeInFromDown(heart))
        self.play(FadeOut(heart))


class ReprogrammingThought(Scene):
    CONFIG = {
        "camera_config": {
            "background_color": DARKER_GREY,
        }
    }

    def construct(self):
        brain = SVGMobject("brain")
        brain.set_fill(GREY, 1)
        brain.set_sheen(1, UL)
        brain.set_stroke(width=0)

        arrow = DoubleArrow(ORIGIN, 3 * RIGHT)

        formula = get_bayes_formula()

        group = VGroup(brain, arrow, formula)
        group.arrange(RIGHT)
        group.center()

        q_marks = TexMobject("???")
        q_marks.scale(1.5)
        q_marks.next_to(arrow, UP, SMALL_BUFF)

        kt = Group(
            ImageMobject("kahneman"),
            ImageMobject("tversky"),
        )
        kt.arrange(RIGHT)
        kt.set_height(2)
        kt.to_corner(UR)

        brain_outline = brain.copy()
        brain_outline.set_fill(opacity=0)
        brain_outline.set_stroke(TEAL, 4)

        self.play(FadeInFrom(brain, RIGHT))
        self.play(
            GrowFromCenter(arrow),
            LaggedStartMap(FadeInFromDown, q_marks[0]),
            run_time=1
        )
        self.play(FadeInFrom(formula, LEFT))
        self.wait()

        kw = {"run_time": 1, "lag_ratio": 0.3}
        self.play(LaggedStartMap(FadeInFromDown, kt, **kw))
        self.play(LaggedStartMap(FadeOut, kt, **kw))
        self.wait()

        self.add(brain)
        self.play(ShowCreationThenFadeOut(
            brain_outline,
            lag_ratio=0.01,
            run_time=2
        ))

        # Bubble
        bubble = ThoughtBubble()
        bubble.next_to(brain, UR, SMALL_BUFF)
        bubble.shift(2 * DOWN)

        diagram = BayesDiagram(0.25, 0.8, 0.5)
        diagram.set_height(2.5)
        diagram.move_to(bubble.get_bubble_center())

        group = VGroup(brain, arrow, q_marks, formula)

        self.play(
            DrawBorderThenFill(VGroup(*reversed(bubble))),
            group.shift, 2 * DOWN,
        )
        self.play(FadeIn(diagram))
        self.wait()
        self.play(
            q_marks.scale, 1.5,
            q_marks.space_out_submobjects, 1.5,
            q_marks.set_opacity, 0,
        )
        self.remove(q_marks)
        self.wait()

        # Move parts
        prior_outline = formula[7:12].copy()
        prior_outline.set_stroke(YELLOW, 5, background=True)
        like_outline = formula[12:18].copy()
        like_outline.set_stroke(BLUE, 5, background=True)

        self.play(
            FadeIn(prior_outline),
            ApplyMethod(diagram.set_prior, 0.5, run_time=2)
        )
        self.play(FadeOut(prior_outline))
        self.play(
            FadeIn(like_outline),
            ApplyMethod(diagram.set_likelihood, 0.2, run_time=2),
        )
        self.play(FadeOut(like_outline))
        self.wait()


class MassOfEarthEstimates(GlimpseOfNextVideo):
    CONFIG = {
        "add_x_coords": False,
        "formula_position": 2 * UP + 0.5 * RIGHT,
        "dx": 0.05,
    }

    def setup(self):
        super().setup()
        earth = SVGMobject(
            file_name="earth",
            height=1.5,
            fill_color=BLACK,
        )
        earth.set_stroke(width=0)
        # earth.set_stroke(BLACK, 1, background=True)
        circle = Circle(
            stroke_width=3,
            stroke_color=GREEN,
            fill_opacity=1,
            fill_color=BLUE_C,
        )
        circle.replace(earth)
        earth.add_to_back(circle)
        earth.set_height(0.75)

        words = TextMobject("Mass of ")
        words.next_to(earth, LEFT)
        group = VGroup(words, earth)

        group.to_edge(DOWN).shift(2 * RIGHT)
        self.add(group)

    def get_formula(self):
        formula = TexMobject(
            "p(M) p(\\text{data}|M) \\over p(\\text{data})",
            tex_to_color_map={
                "M": HYPOTHESIS_COLOR,
                "\\text{data}": EVIDENCE_COLOR1,
            },
            substrings_to_isolate=list("p(|)")
        )
        formula.move_to(self.formula_position)
        return formula

    def prior(self, x, mu=6, sigma=1):
        factor = (1 / sigma / np.sqrt(TAU))
        return factor * np.exp(-0.5 * ((x - mu) / sigma)**2)

    def likelihood(self, x):
        return self.prior(x, 5, 1)


class ShowProgrammer(Scene):
    CONFIG = {
        "camera_config": {
            "background_color": DARKER_GREY,
        }
    }

    def construct(self):
        programmer = SVGMobject(file_name="programmer")
        programmer.set_stroke(width=0)
        programmer.set_fill(GREY, 1)
        programmer.set_sheen(1, UL)
        programmer.set_height(3)

        programmer.to_corner(DL)
        self.play(FadeInFrom(programmer, DOWN))
        self.wait()


class BayesEndScene(PatreonEndScreen):
    CONFIG = {
        "specific_patrons": [
            "Juan Benet",
            "Vassili Philippov",
            "Burt Humburg",
            "D. Sivakumar",
            "John Le",
            "Matt Russell",
            "Scott Gray",
            "soekul",
            "Steven Braun",
            "Tihan Seale",
            "Ali Yahya",
            "Arthur Zey",
            "dave nicponski",
            "Joseph Kelly",
            "Kaustuv DeBiswas",
            "Lambda AI Hardware",
            "Lukas Biewald",
            "Mark Heising",
            "Nicholas Cahill",
            "Peter Mcinerney",
            "Quantopian",
            "Scott Walter, Ph.D.",
            "Tauba Auerbach",
            "Yana Chernobilsky",
            "Yu Jun",
            "Lukas -krtek.net- Novy",
            "Britt Selvitelle",
            "Britton Finley",
            "David Gow",
            "J",
            "Jonathan Wilson",
            "Joseph John Cox",
            "Magnus Dahlström",
            "Matteo Delabre",
            "Randy C. Will",
            "Ray Hua Wu",
            "Ryan Atallah",
            "Luc Ritchie",
            "1stViewMaths",
            "Adam Dřínek",
            "Aidan Shenkman",
            "Alan Stein",
            "Alex Mijalis",
            "Alexis Olson",
            "Andreas Benjamin Brössel",
            "Andrew Busey",
            "Andrew Cary",
            "Andrew R. Whalley",
            "Anthony Turvey",
            "Antoine Bruguier",
            "Antonio Juarez",
            "Arjun Chakroborty",
            "Austin Goodman",
            "Avi Finkel",
            "Awoo",
            "Azeem Ansar",
            "AZsorcerer",
            "Barry Fam",
            "Bernd Sing",
            "Boris Veselinovich",
            "Bradley Pirtle",
            "Brian Staroselsky",
            "Calvin Lin",
            "Chaitanya Upmanu",
            "Charles Southerland",
            "Charlie N",
            "Chenna Kautilya",
            "Chris Connett",
            "Christian Kaiser",
            "Clark Gaebel",
            "Cooper Jones",
            "Corey Ogburn",
            "Danger Dai",
            "Daniel Herrera C",
            "Dave B",
            "Dave Kester",
            "David B. Hill",
            "David Clark",
            "David Pratt",
            "DeathByShrimp",
            "Delton Ding",
            "Dominik Wagner",
            "eaglle",
            "emptymachine",
            "Eric Younge",
            "Eryq Ouithaqueue",
            "Federico Lebron",
            "Fernando Via Canel",
            "Frank R. Brown, Jr.",
            "Giovanni Filippi",
            "Hal Hildebrand",
            "Hitoshi Yamauchi",
            "Ivan Sorokin",
            "j eduardo perez",
            "Jacob Baxter",
            "Jacob Harmon",
            "Jacob Hartmann",
            "Jacob Magnuson",
            "Jameel Syed",
            "James Liao",
            "Jason Hise",
            "Jayne Gabriele",
            "Jeff Linse",
            "Jeff Straathof",
            "John C. Vesey",
            "John Griffith",
            "John Haley",
            "John V Wertheim",
            "Jonathan Heckerman",
            "Josh Kinnear",
            "Joshua Claeys",
            "Kai-Siang Ang",
            "Kanan Gill",
            "Kartik Cating-Subramanian",
            "L0j1k",
            "Lee Redden",
            "Linh Tran",
            "Ludwig Schubert",
            "Magister Mugit",
            "Mark B Bahu",
            "Mark Mann",
            "Martin Price",
            "Mathias Jansson",
            "Matt Godbolt",
            "Matt Langford",
            "Matt Roveto",
            "Matthew Bouchard",
            "Matthew Cocke",
            "Michael Hardel",
            "Michael W White",
            "Mirik Gogri",
            "Mustafa Mahdi",
            "Márton Vaitkus",
            "Nikita Lesnikov",
            "Omar Zrien",
            "Owen Campbell-Moore",
            "Patrick Lucas",
            "Pedro Igor S. Budib",
            "Peter Ehrnstrom",
            "rehmi post",
            "Rex Godby",
            "Richard Barthel",
            "Ripta Pasay",
            "Rish Kundalia",
            "Roman Sergeychik",
            "Roobie",
            "SansWord Huang",
            "Sebastian Garcia",
            "Solara570",
            "Steven Siddals",
            "Stevie Metke",
            "Suthen Thomas",
            "Tal Einav",
            "Ted Suzman",
            "The Responsible One",
            "Thomas Roets",
            "Thomas Tarler",
            "Tianyu Ge",
            "Tom Fleming",
            "Tyler VanValkenburg",
            "Valeriy Skobelev",
            "Veritasium",
            "Vinicius Reis",
            "Xuanji Li",
            "Yavor Ivanov",
            "YinYangBalance.Asia",
        ],
    }


class Thumbnail(Scene):
    def construct(self):
        diagram = BayesDiagram(0.25, 0.4, 0.1)
        diagram.set_height(3)
        diagram.add_brace_attrs()
        braces = VGroup(
            diagram.h_brace,
            diagram.he_brace,
            diagram.nhe_brace,
        )
        diagram.add(*braces)

        kw = {
            "tex_to_color_map": {
                "H": YELLOW,
                "E": BLUE,
                "\\neg": RED,
            }
        }
        labels = VGroup(
            TexMobject("P(H)", **kw),
            TexMobject("P(E|H)", **kw),
            TexMobject("P(E|\\neg H)", **kw),
        )
        labels.scale(1)

        for label, brace, vect in zip(labels, braces, [DOWN, LEFT, RIGHT]):
            label.next_to(brace, vect)

        diagram.add(*labels)

        # diagram.set_height(6)
        diagram.to_edge(DOWN, buff=MED_SMALL_BUFF)
        diagram.shift(2 * LEFT)
        self.add(diagram)

        diagram.set_height(FRAME_HEIGHT - 1)
        diagram.center().to_edge(DOWN)
        for rect in diagram.evidence_split:
            rect.set_sheen(0.2, UL)
        return

        # Formula
        formula = get_bayes_formula()
        formula.scale(1.5)
        formula.to_corner(UL)

        frac = VGroup(
            diagram.he_rect.copy(),
            Line(ORIGIN, 4 * RIGHT).set_stroke(WHITE, 3),
            VGroup(
                diagram.he_rect.copy(),
                TexMobject("+"),
                diagram.nhe_rect.copy(),
            ).arrange(RIGHT)
        )
        frac.arrange(DOWN)
        equals = TexMobject("=")
        equals.next_to(formula, RIGHT)
        frac.next_to(equals, RIGHT)

        self.add(formula)
        self.add(equals, frac)

        VGroup(formula, equals, frac).to_edge(UP, buff=SMALL_BUFF)
