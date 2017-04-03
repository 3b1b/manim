from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from topics.objects import *
from scene import Scene
from scene.zoomed_scene import ZoomedScene
from scene.reconfigurable_scene import ReconfigurableScene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

from eoc.graph_scene import GraphScene
from topics.common_scenes import OpeningQuote, PatreonThanks

class CircleScene(PiCreatureScene):
    CONFIG = {
        "radius" : 1.5,
        "stroke_color" : WHITE,
        "fill_color" : BLUE_E,
        "fill_opacity" : 0.75,
        "radial_line_color" : MAROON_B,
        "outer_ring_color" : GREEN_E,
        "ring_colors" : [BLUE, GREEN],
        "dR" : 0.1,
        "dR_color" : YELLOW,
        "unwrapped_tip" : ORIGIN,
        "include_pi_creature" : False,
        "circle_corner" : UP+LEFT,
    }
    def setup(self):
        PiCreatureScene.setup(self)
        self.circle = Circle(
            radius = self.radius,
            stroke_color = self.stroke_color,
            fill_color = self.fill_color,
            fill_opacity = self.fill_opacity,
        )
        self.circle.to_corner(self.circle_corner, buff = MED_LARGE_BUFF)
        self.radius_line = Line(
            self.circle.get_center(),
            self.circle.get_right(),
            color = self.radial_line_color
        )
        self.radius_brace = Brace(self.radius_line, buff = SMALL_BUFF)
        self.radius_label = self.radius_brace.get_text("$R$", buff = SMALL_BUFF)

        self.radius_group = VGroup(
            self.radius_line, self.radius_brace, self.radius_label
        )
        self.add(self.circle, *self.radius_group)

        if not self.include_pi_creature:
            self.remove(self.get_primary_pi_creature())

    def introduce_circle(self, added_anims = []):
        self.remove(self.circle)
        self.play(
            ShowCreation(self.radius_line),
            GrowFromCenter(self.radius_brace),
            Write(self.radius_label),
        )
        self.circle.set_fill(opacity = 0)

        self.play(
            Rotate(
                self.radius_line, 2*np.pi-0.001, 
                about_point = self.circle.get_center(),
            ),
            ShowCreation(self.circle),
            *added_anims,
            run_time = 2
        )
        self.play(
            self.circle.set_fill, self.fill_color, self.fill_opacity,
            Animation(self.radius_line),
            Animation(self.radius_brace),
            Animation(self.radius_label),
        )

    def increase_radius(self, numerical_dr = True, run_time = 2):
        radius_mobs = VGroup(
            self.radius_line, self.radius_brace, self.radius_label
        )
        nudge_line = Line(
            self.radius_line.get_right(),
            self.radius_line.get_right() + self.dR*RIGHT,
            color = self.dR_color
        )
        nudge_arrow = Arrow(
            nudge_line.get_center() + 0.5*RIGHT+DOWN,
            nudge_line.get_center(),
            color = YELLOW,
            buff = SMALL_BUFF,
            tip_length = 0.2,
        )
        if numerical_dr:
            nudge_label = TexMobject("%.01f"%self.dR)
        else:
            nudge_label = TexMobject("dr")
        nudge_label.highlight(self.dR_color)
        nudge_label.scale(0.75)
        nudge_label.next_to(nudge_arrow.get_start(), DOWN)

        radius_mobs.add(nudge_line, nudge_arrow, nudge_label)

        outer_ring = self.get_outer_ring()

        self.play(
            FadeIn(outer_ring),            
            ShowCreation(nudge_line),
            ShowCreation(nudge_arrow),
            Write(nudge_label),
            run_time = run_time/2.
        )
        self.dither(run_time/2.)
        self.nudge_line = nudge_line
        self.nudge_arrow = nudge_arrow
        self.nudge_label = nudge_label
        self.outer_ring = outer_ring
        return outer_ring

    def get_ring(self, radius, dR, color = GREEN):
        ring = Circle(radius = radius + dR).center()
        inner_ring = Circle(radius = radius)
        inner_ring.rotate(np.pi, RIGHT)
        ring.append_vectorized_mobject(inner_ring)
        ring.set_stroke(width = 0)
        ring.set_fill(color)
        ring.move_to(self.circle)
        ring.R = radius 
        ring.dR = dR
        return ring

    def get_rings(self, **kwargs):
        dR = kwargs.get("dR", self.dR)
        colors = kwargs.get("colors", self.ring_colors)
        radii = np.arange(0, self.radius, dR)
        colors = color_gradient(colors, len(radii))

        rings = VGroup(*[
            self.get_ring(radius, dR = dR, color = color)
            for radius, color in zip(radii, colors)
        ])
        return rings

    def get_outer_ring(self):
        return self.get_ring(
            radius = self.radius, dR = self.dR,
            color = self.outer_ring_color
        )

    def unwrap_ring(self, ring, **kwargs):
        self.unwrap_rings(ring, **kwargs)

    def unwrap_rings(self, *rings, **kwargs):
        added_anims = kwargs.get("added_anims", [])
        rings = VGroup(*rings)
        unwrapped = VGroup(*[
            self.get_unwrapped(ring, **kwargs)
            for ring in rings
        ])
        self.play(
            rings.rotate, np.pi/2,
            rings.next_to, unwrapped.get_bottom(), UP,
            run_time = 2,
            path_arc = np.pi/2,
        )
        self.play(
            Transform(rings, unwrapped, run_time = 3),
            *added_anims
        )

    def get_unwrapped(self, ring, to_edge = LEFT, **kwargs):
        R = ring.R
        R_plus_dr = ring.R + ring.dR
        n_anchors = ring.get_num_anchor_points()
        result = VMobject()
        result.set_points_as_corners([
            interpolate(np.pi*R_plus_dr*LEFT,  np.pi*R_plus_dr*RIGHT, a)
            for a in np.linspace(0, 1, n_anchors/2)
        ]+[
            interpolate(np.pi*R*RIGHT+ring.dR*UP,  np.pi*R*LEFT+ring.dR*UP, a)
            for a in np.linspace(0, 1, n_anchors/2)
        ])
        result.set_style_data(
            stroke_color = ring.get_stroke_color(),
            stroke_width = ring.get_stroke_width(),
            fill_color = ring.get_fill_color(),
            fill_opacity = ring.get_fill_opacity(),
        )
        result.move_to(self.unwrapped_tip, aligned_edge = DOWN)
        result.shift(R_plus_dr*DOWN)
        if to_edge is not None:
            result.to_edge(to_edge)

        return result

    def create_pi_creature(self):
        self.pi_creature = Randolph(color = BLUE_C)
        self.pi_creature.to_corner(DOWN+LEFT)
        return self.pi_creature


#############

#revert_to_original_skipping_status

class Chapter1OpeningQuote(OpeningQuote):
    CONFIG = {
        "quote" : [
            """The art of doing mathematics is finding
            that """, "special case", 
            """that contains all the 
            germs of generality."""
        ],
        "quote_arg_separator" : " ",
        "highlighted_quote_terms" : {
            "special case" : BLUE
        },
        "author" : "David Hilbert",
    }

class Introduction(TeacherStudentsScene):
    def construct(self):
        self.show_series()
        self.show_many_facts()
        self.invent_calculus()

    def show_series(self):
        series = VideoSeries()
        series.to_edge(UP)
        this_video = series[0]
        this_video.highlight(YELLOW)
        this_video.save_state()
        this_video.set_fill(opacity = 0)
        this_video.center()
        this_video.scale_to_fit_height(2*SPACE_HEIGHT)
        self.this_video = this_video


        words = TextMobject(
            "Welcome to \\\\",
            "Essence of calculus"
        )
        words.highlight_by_tex("Essence of calculus", YELLOW)

        self.teacher.change_mode("happy")
        self.play(
            FadeIn(
                series,
                submobject_mode = "lagged_start",
                run_time = 2
            ),
            Blink(self.get_teacher())
        )
        self.teacher_says(words, target_mode = "hooray")
        self.change_student_modes(
            *["hooray"]*3,
            look_at_arg = series[1].get_left(),
            added_anims = [
                ApplyMethod(this_video.restore, run_time = 3),
            ]
        )
        self.play(
            ApplyWave(series, direction = DOWN, run_time = 2),
            Animation(self.teacher.bubble),
            Animation(self.teacher.bubble.content),
        )

        essence_words = words.get_part_by_tex("Essence").copy()
        self.play(
            FadeOut(self.teacher.bubble),
            FadeOut(self.teacher.bubble.content),
            essence_words.next_to, series, DOWN,
            *[
                ApplyMethod(pi.change_mode, "pondering")
                for pi in self.get_pi_creatures()
            ]
        )
        self.dither(3)

        self.series = series
        self.essence_words = essence_words

    def show_many_facts(self):
        rules = list(it.starmap(TexMobject, [
            ("{d(", "x", "^2)", "\\over \\,", "dx}", "=", "2", "x"),
            (
                "d(", "f", "g", ")", "=", 
                "f", "dg", "+", "g", "df",
            ),
            (
                "F(x)", "=", "\\int_0^x", 
                "\\frac{dF}{dg}(t)\\,", "dt"
            ),
            (
                "f(x)", "=", "\\sum_{n = 0}^\\infty",
                "f^{(n)}(a)", "\\frac{(x-a)^n}{n!}"
            ),
        ]))
        video_indices = [2, 3, 7, 10]
        tex_to_color = [
            ("x", BLUE),
            ("f", BLUE),
            ("df", BLUE),
            ("g", YELLOW),
            ("dg", YELLOW),
            ("f(x)", BLUE),
            ( "f^{(n)}(a)", BLUE),
        ]

        for rule in rules:
            for tex, color in tex_to_color:
                rule.highlight_by_tex(tex, color, substring = False)
            rule.next_to(self.teacher.get_corner(UP+LEFT), UP)
            rule.shift_onto_screen()

        student_index = 1
        student = self.get_students()[student_index]
        self.change_student_modes(
            "pondering", "sassy", "pondering",
            look_at_arg = self.teacher.eyes,
            added_anims = [
                self.teacher.change_mode, "plain"
            ]
        )
        self.dither(2)
        self.play(
            Write(rules[0]),
            self.teacher.change_mode, "raise_right_hand",
        )
        self.dither()
        alt_rules_list = list(rules[1:]) + [VectorizedPoint(self.teacher.eyes.get_top())]
        for last_rule, rule, video_index in zip(rules, alt_rules_list, video_indices):
            video = self.series[video_index]
            self.play(
                last_rule.replace, video,
                FadeIn(rule),
            )
            self.play(Animation(rule))
            self.dither()
        self.play(
            self.teacher.change_mode, "happy",
            self.teacher.look_at, student.eyes
        )

    def invent_calculus(self):
        student = self.get_students()[1]
        creatures = self.get_pi_creatures()
        creatures.remove(student)
        creature_copies = creatures.copy()
        self.remove(creatures)
        self.add(creature_copies)

        calculus = VGroup(*self.essence_words[-len("calculus"):])
        calculus.generate_target()
        invent = TextMobject("Invent")
        invent_calculus = VGroup(invent, calculus.target)
        invent_calculus.arrange_submobjects(RIGHT, buff = MED_SMALL_BUFF)
        invent_calculus.next_to(student, UP, 1.5*LARGE_BUFF)
        invent_calculus.shift(RIGHT)
        arrow = Arrow(invent_calculus, student)

        fader = Rectangle(
            width = 2*SPACE_WIDTH,
            height = 2*SPACE_HEIGHT,
            stroke_width = 0,
            fill_color = BLACK,
            fill_opacity = 0.5,
        )

        self.play(
            FadeIn(fader),
            Animation(student),
            Animation(calculus)
        )
        self.play(
            Write(invent),
            MoveToTarget(calculus),
            student.change_mode, "erm",
            student.look_at, calculus
        )
        self.play(ShowCreation(arrow))
        self.dither(2)

class PreviewFrame(Scene):
    def construct(self):
        frame = Rectangle(height = 9, width = 16, color = WHITE)
        frame.scale_to_fit_height(1.5*SPACE_HEIGHT)

        colors = iter(color_gradient([BLUE, YELLOW], 3))
        titles = [
            TextMobject("Chapter %d:"%d, s).to_edge(UP).highlight(colors.next())
            for d, s in [
                (3, "Derivative formulas through geometry"),
                (4, "Chain rule, product rule, etc."),
                (7, "Limits"),
            ]
        ]
        title = titles[0]

        frame.next_to(title, DOWN)

        self.add(frame, title)
        self.dither(3)
        for next_title in titles[1:]:
            self.play(Transform(title, next_title))
            self.dither(3)

class ProductRuleDiagram(Scene):
    def construct(self):
        df = 0.4
        dg = 0.2
        rect_kwargs = {
            "stroke_width" : 0,
            "fill_color" : BLUE,
            "fill_opacity" : 0.6,
        }

        rect = Rectangle(width = 4, height = 3, **rect_kwargs)
        rect.shift(DOWN)
        df_rect = Rectangle(
            height = rect.get_height(),
            width = df,
            **rect_kwargs
        )
        dg_rect = Rectangle(
            height = dg,
            width = rect.get_width(),
            **rect_kwargs
        )
        corner_rect = Rectangle(
            height = dg, 
            width = df,
            **rect_kwargs
        )
        d_rects = VGroup(df_rect, dg_rect, corner_rect)
        for d_rect, direction in zip(d_rects, [RIGHT, DOWN, RIGHT+DOWN]):
            d_rect.next_to(rect, direction, buff = 0)
            d_rect.set_fill(YELLOW, 0.75)

        corner_pairs = [
            (DOWN+RIGHT, UP+RIGHT),
            (DOWN+RIGHT, DOWN+LEFT),
            (DOWN+RIGHT, DOWN+RIGHT),
        ]
        for d_rect, corner_pair in zip(d_rects, corner_pairs):
            line = Line(*[
                rect.get_corner(corner)
                for corner in corner_pair
            ])
            d_rect.line = d_rect.copy().replace(line, stretch = True)
            d_rect.line.highlight(d_rect.get_color())

        f_brace = Brace(rect, UP)
        g_brace = Brace(rect, LEFT)
        df_brace = Brace(df_rect, UP)
        dg_brace = Brace(dg_rect, LEFT)

        f_label = f_brace.get_text("$f$")
        g_label = g_brace.get_text("$g$")
        df_label = df_brace.get_text("$df$")
        dg_label = dg_brace.get_text("$dg$")

        VGroup(f_label, df_label).highlight(GREEN)
        VGroup(g_label, dg_label).highlight(RED)

        f_label.generate_target()
        g_label.generate_target()
        fg_group = VGroup(f_label.target, g_label.target)
        fg_group.generate_target()
        fg_group.target.arrange_submobjects(RIGHT, buff = SMALL_BUFF)
        fg_group.target.move_to(rect.get_center())

        for mob in df_brace, df_label, dg_brace, dg_label:
            mob.save_state()
            mob.scale(0.01, about_point = rect.get_corner(
                mob.get_center() - rect.get_center()
            ))

        self.add(rect)
        self.play(
            GrowFromCenter(f_brace),
            GrowFromCenter(g_brace),
            Write(f_label),
            Write(g_label),
        )
        self.play(MoveToTarget(fg_group))
        self.play(*[
            mob.restore
            for mob in df_brace, df_label, dg_brace, dg_label
        ] + [
            ReplacementTransform(d_rect.line, d_rect)
            for d_rect in d_rects
        ])
        self.dither()
        self.play(
            d_rects.space_out_submobjects, 1.2,
            MaintainPositionRelativeTo(
                VGroup(df_brace, df_label),
                df_rect
            ),
            MaintainPositionRelativeTo(
                VGroup(dg_brace, dg_label),
                dg_rect
            ),
        )
        self.dither()

        deriv = TexMobject(
            "d(", "fg", ")", "=", 
            "f", "\\cdot", "dg", "+", "g", "\\cdot", "df"
        )
        deriv.to_edge(UP)
        alpha_iter = iter(np.linspace(0, 0.5, 5))
        self.play(*[
            ApplyMethod(
                mob.copy().move_to,
                deriv.get_part_by_tex(tex, substring = False),
                rate_func = squish_rate_func(smooth, alpha, alpha+0.5)
            )
            for mob, tex in [
                (fg_group, "fg"),
                (f_label, "f"),
                (dg_label, "dg"),
                (g_label, "g"),
                (df_label, "df"),
            ]
            for alpha in [alpha_iter.next()]
        ]+[
            Write(VGroup(*it.chain(*[
                deriv.get_parts_by_tex(tex, substring = False)
                for tex in "d(", ")", "=", "\\cdot", "+"
            ])))
        ], run_time = 3)
        self.dither()

class IntroduceCircle(CircleScene):
    CONFIG = {
        "include_pi_creature" : True,
        "unwrapped_tip" : 2*RIGHT
    }
    def construct(self):
        self.force_skipping()

        self.introduce_area()
        self.question_area()
        self.show_calculus_symbols()

    def introduce_area(self):
        area = TexMobject("\\text{Area}", "=", "\\pi", "R", "^2")
        area.next_to(self.pi_creature.get_corner(UP+RIGHT), UP+RIGHT)

        self.remove(self.circle, self.radius_group)
        self.play(
            self.pi_creature.change_mode, "pondering",
            self.pi_creature.look_at, self.circle
        )
        self.introduce_circle()
        self.dither()
        R_copy = self.radius_label.copy()
        self.play(
            self.pi_creature.change_mode, "raise_right_hand",
            self.pi_creature.look_at, area,
            Transform(R_copy, area.get_part_by_tex("R"))
        )
        self.play(Write(area))
        self.remove(R_copy)
        self.dither()

        self.area = area

    def question_area(self):
        q_marks = TexMobject("???")
        q_marks.next_to(self.pi_creature, UP)
        rings = VGroup(*reversed(self.get_rings()))
        unwrapped_rings = VGroup(*[
            self.get_unwrapped(ring, to_edge = None)
            for ring in rings
        ])
        unwrapped_rings.arrange_submobjects(UP, buff = SMALL_BUFF)
        unwrapped_rings.move_to(self.unwrapped_tip, UP)
        ring_anim_kwargs = {
            "run_time" : 3,
            "submobject_mode" : "lagged_start"
        }

        self.play(
            Animation(self.area),
            Write(q_marks),
            self.pi_creature.change_mode, "confused",
            self.pi_creature.look_at, self.area,
        )
        self.dither()
        self.play(
            FadeIn(rings, **ring_anim_kwargs),
            Animation(self.radius_group),
            FadeOut(q_marks),
            self.pi_creature.change_mode, "thinking"
        )
        self.dither()
        self.play(
            rings.rotate, np.pi/2,
            rings.move_to, unwrapped_rings.get_top(),
            Animation(self.radius_group),
            path_arc = np.pi/2,
            **ring_anim_kwargs
        )
        self.play(
            Transform(rings, unwrapped_rings, **ring_anim_kwargs),
        )
        self.dither()

    def show_calculus_symbols(self):
        ftc = TexMobject(
            "\\int_0^R", "\\frac{dA}{dr}", "\\,dr",
            "=", "A(R)"
        )
        ftc.shift(2*UP)

        self.play(
            ReplacementTransform(
                self.area.get_part_by_tex("R").copy(),
                ftc.get_part_by_tex("int")
            ),
            self.pi_creature.change_mode, "plain"
        )
        self.dither()
        self.play(
            ReplacementTransform(
                self.area.get_part_by_tex("Area").copy(),
                ftc.get_part_by_tex("frac")
            ),
            ReplacementTransform(
                self.area.get_part_by_tex("R").copy(),
                ftc.get_part_by_tex("\\,dr")
            )
        )
        self.dither()
        self.play(Write(VGroup(*ftc[-2:])))
        self.dither(2)

class ApproximateOneRing(CircleScene, ReconfigurableScene):
    CONFIG = {
        "num_lines" : 24,
        "ring_index_proportion" : 0.6,
        "ring_shift_val" : 6*RIGHT,
        "ring_colors" : [BLUE, GREEN_E],
        "unwrapped_tip" : 2*RIGHT+0.5*UP,
    }
    def setup(self):
        CircleScene.setup(self)
        ReconfigurableScene.setup(self)

    def construct(self):
        self.write_radius_three()
        self.try_to_understand_area()
        self.slice_into_rings()
        self.isolate_one_ring()
        self.straighten_ring_out()
        self.approximate_as_rectangle()

    def write_radius_three(self):
        three = TexMobject("3")
        three.move_to(self.radius_label)

        self.look_at(self.circle)
        self.play(Transform(
            self.radius_label, three,
            path_arc = np.pi
        ))
        self.dither()

    def try_to_understand_area(self):
        line_sets = [
            VGroup(*[
                Line(
                    self.circle.point_from_proportion(alpha),
                    self.circle.point_from_proportion(func(alpha)),
                )
                for alpha in np.linspace(0, 1, self.num_lines)
            ])
            for func in [
                lambda alpha : 1-alpha,
                lambda alpha : (0.5-alpha)%1,
                lambda alpha : (alpha + 0.4)%1,
                lambda alpha : (alpha + 0.5)%1,
            ]
        ]
        for lines in line_sets:
            lines.set_stroke(BLACK, 2)
        lines = line_sets[0]

        self.play(
            ShowCreation(
                lines, 
                run_time = 2, 
                submobject_mode = "lagged_start"
            ),
            Animation(self.radius_group),
            self.pi_creature.change_mode, "maybe"
        )
        self.dither(2)
        for new_lines in line_sets[1:]:
            self.play(
                Transform(lines, new_lines),
                Animation(self.radius_group)
            )
            self.dither()
        self.dither()
        self.play(FadeOut(lines), Animation(self.radius_group))

    def slice_into_rings(self):
        rings = self.get_rings()
        rings.set_stroke(BLACK, 1)

        self.play(
            FadeIn(
                rings,
                submobject_mode = "lagged_start",
                run_time = 3
            ),
            Animation(self.radius_group),
            self.pi_creature.change_mode, "pondering",
            self.pi_creature.look_at, self.circle
        )
        self.dither(2)
        for x in range(2):
            self.play(
                Rotate(rings, np.pi, in_place = True, run_time = 2),
                Animation(self.radius_group),
                self.pi_creature.change_mode, "happy"
            )
        self.dither(2)

        self.rings = rings

    def isolate_one_ring(self):
        rings = self.rings
        index = int(self.ring_index_proportion*len(rings))
        original_ring = rings[index]
        ring = original_ring.copy()

        radius = Line(ORIGIN, ring.R*RIGHT, color = WHITE)
        radius.rotate(np.pi/4)
        r_label = TexMobject("r")
        r_label.next_to(radius.get_center(), UP+LEFT, SMALL_BUFF)
        area_q = TextMobject("Area", "?", arg_separator = "")
        area_q.highlight(YELLOW)


        self.play(
            ring.shift, self.ring_shift_val,
            original_ring.set_fill, None, 0.25,
            Animation(self.radius_group),
        )

        VGroup(radius, r_label).shift(ring.get_center())
        area_q.next_to(ring, RIGHT)

        self.play(ShowCreation(radius))
        self.play(Write(r_label))
        self.dither()
        self.play(Write(area_q))
        self.dither()
        self.play(*[
            ApplyMethod(
                r.set_fill, YELLOW, 
                rate_func = squish_rate_func(there_and_back, alpha, alpha+0.15),
                run_time = 3
            )
            for r, alpha in zip(rings, np.linspace(0, 0.85, len(rings)))
        ]+[
            Animation(self.radius_group)
        ])
        self.dither()
        self.change_mode("thinking")
        self.dither()

        self.original_ring = original_ring
        self.ring = ring
        self.ring_radius_group = VGroup(radius, r_label)
        self.area_q = area_q

    def straighten_ring_out(self):
        ring = self.ring.copy()
        trapazoid = TextMobject("Trapazoid?")
        rectangle_ish = TextMobject("Rectangle-ish")
        for text in trapazoid, rectangle_ish:
            text.next_to(
                self.pi_creature.get_corner(UP+RIGHT), 
                DOWN+RIGHT, buff = MED_LARGE_BUFF
            )

        self.unwrap_ring(ring, to_edge = RIGHT)
        self.change_mode("pondering")
        self.dither()
        self.play(Write(trapazoid))
        self.dither()
        self.play(trapazoid.shift, DOWN)
        strike = Line(
            trapazoid.get_left(), trapazoid.get_right(),
            stroke_color = RED,
            stroke_width = 8
        )
        self.play(
            Write(rectangle_ish),
            ShowCreation(strike),
            self.pi_creature.change_mode, "happy"
        )
        self.dither()
        self.play(*map(FadeOut, [trapazoid, strike]))

        self.unwrapped_ring = ring

    def approximate_as_rectangle(self):
        top_brace, side_brace = [
            Brace(
                self.unwrapped_ring, vect, buff = SMALL_BUFF,
                min_num_quads = 2,
            )
            for vect in UP, LEFT
        ]
        top_brace.scale_in_place(self.ring.R/(self.ring.R+self.dR))
        side_brace.set_stroke(WHITE, 0.5)


        width_label = TexMobject("2\\pi", "r")
        width_label.next_to(top_brace, UP, SMALL_BUFF)
        dr_label = TexMobject("dr")
        q_marks = TexMobject("???")
        concrete_dr = TexMobject("=0.1")
        concrete_dr.submobjects.reverse()
        for mob in dr_label, q_marks, concrete_dr:
            mob.next_to(side_brace, LEFT, SMALL_BUFF)
        dr_label.save_state()

        alt_side_brace = side_brace.copy()
        alt_side_brace.move_to(ORIGIN, UP+RIGHT)
        alt_side_brace.rotate(-np.pi/2)
        alt_side_brace.shift(
            self.original_ring.get_boundary_point(RIGHT)
        )
        alt_dr_label = dr_label.copy()
        alt_dr_label.next_to(alt_side_brace, UP, SMALL_BUFF)

        approx = TexMobject("\\approx")
        approx.next_to(
            self.area_q.get_part_by_tex("Area"), 
            RIGHT,
            align_using_submobjects = True,
        )
        two_pi_r_dr = VGroup(width_label, dr_label).copy()
        two_pi_r_dr.generate_target()
        two_pi_r_dr.target.arrange_submobjects(
            RIGHT, buff = SMALL_BUFF, aligned_edge = DOWN
        )
        two_pi_r_dr.target.next_to(approx, RIGHT, aligned_edge = DOWN)

        self.play(GrowFromCenter(top_brace))
        self.play(
            Write(width_label.get_part_by_tex("pi")),
            ReplacementTransform(
                self.ring_radius_group[1].copy(),
                width_label.get_part_by_tex("r")
            )
        )
        self.dither()
        self.play(
            GrowFromCenter(side_brace),
            Write(q_marks)
        )
        self.change_mode("confused")
        self.dither()
        for num_rings in 20, 7:
            self.show_alternate_width(num_rings)
        self.play(ReplacementTransform(q_marks, dr_label))
        self.play(
            ReplacementTransform(side_brace.copy(), alt_side_brace),
            ReplacementTransform(dr_label.copy(), alt_dr_label),
            run_time = 2
        )
        self.dither()
        self.play(
            dr_label.next_to, concrete_dr.copy(), LEFT, SMALL_BUFF, DOWN,
            Write(concrete_dr, run_time = 2),
            self.pi_creature.change_mode, "pondering"
        )
        self.dither(2)
        self.play(
            MoveToTarget(two_pi_r_dr),
            FadeIn(approx),
            self.area_q.get_part_by_tex("?").fade, 1,
        )
        self.dither()
        self.play(
            FadeOut(concrete_dr),
            dr_label.restore
        )
        self.show_alternate_width(
            40, 
            transformation_kwargs = {"run_time" : 4},
            return_to_original_configuration = False,
        )
        self.dither(2)
        self.look_at(self.circle)
        self.play(
            ApplyWave(self.rings, amplitude = 0.1),
            Animation(self.radius_group),
            Animation(alt_side_brace),
            Animation(alt_dr_label),
            run_time = 3,
            submobject_mode = "lagged_start"
        )
        self.dither(2)

    def show_alternate_width(self, num_rings, **kwargs):
        self.transition_to_alt_config(
            dR = self.radius/num_rings, **kwargs
        )

class GraphRectangles(CircleScene, GraphScene):
    CONFIG = {
        "x_min" : -1,
        "x_max" : 4,
        "x_axis_width" : 8,
        "x_labeled_nums" : range(1, 5),
        "x_axis_label" : "$r$",
        "y_min" : 0,
        "y_max" : 20,
        "y_tick_frequency" : 2.5,
        "y_labeled_nums" : range(5, 25, 5),
        "y+axis_label" : ""
    }
    def setup(self):
        CircleScene.setup(self)
        self.graph_origin = (self.circle.get_right()[0]+LARGE_BUFF)*RIGHT
        self.graph_origin += 3*DOWN
        GraphScene.setup(self)

    def construct(self):
        self.setup_axes()






























