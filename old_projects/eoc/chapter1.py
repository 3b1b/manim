from manimlib.imports import *
from old_projects.eoc.chapter2 import Car, MoveCar

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
        nudge_label.set_color(self.dR_color)
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
        self.wait(run_time/2.)
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
        n_anchors = ring.get_num_curves()
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
        this_video.set_color(YELLOW)
        this_video.save_state()
        this_video.set_fill(opacity = 0)
        this_video.center()
        this_video.set_height(FRAME_HEIGHT)
        self.this_video = this_video


        words = TextMobject(
            "Welcome to \\\\",
            "Essence of calculus"
        )
        words.set_color_by_tex("Essence of calculus", YELLOW)

        self.teacher.change_mode("happy")
        self.play(
            FadeIn(
                series,
                lag_ratio = 0.5,
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
        self.play(*[
            ApplyMethod(
                video.shift, 0.5*video.get_height()*DOWN,
                run_time = 3,
                rate_func = squish_rate_func(
                    there_and_back, alpha, alpha+0.3
                )
            )
            for video, alpha in zip(series, np.linspace(0, 0.7, len(series)))
        ]+[
            Animation(self.teacher.bubble),
            Animation(self.teacher.bubble.content),
        ])

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
        self.wait(3)

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
                rule.set_color_by_tex(tex, color, substring = False)
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
        self.wait(2)
        self.play(
            Write(rules[0]),
            self.teacher.change_mode, "raise_right_hand",
        )
        self.wait()
        alt_rules_list = list(rules[1:]) + [VectorizedPoint(self.teacher.eyes.get_top())]
        for last_rule, rule, video_index in zip(rules, alt_rules_list, video_indices):
            video = self.series[video_index]
            self.play(
                last_rule.replace, video,
                FadeIn(rule),
            )
            self.play(Animation(rule))
            self.wait()
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
        invent_calculus.arrange(RIGHT, buff = MED_SMALL_BUFF)
        invent_calculus.next_to(student, UP, 1.5*LARGE_BUFF)
        invent_calculus.shift(RIGHT)
        arrow = Arrow(invent_calculus, student)

        fader = Rectangle(
            width = FRAME_WIDTH,
            height = FRAME_HEIGHT,
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
        self.wait(2)

class PreviewFrame(Scene):
    def construct(self):
        frame = Rectangle(height = 9, width = 16, color = WHITE)
        frame.set_height(1.5*FRAME_Y_RADIUS)

        colors = iter(color_gradient([BLUE, YELLOW], 3))
        titles = [
            TextMobject("Chapter %d:"%d, s).to_edge(UP).set_color(next(colors))
            for d, s in [
                (3, "Derivative formulas through geometry"),
                (4, "Chain rule, product rule, etc."),
                (7, "Limits"),
            ]
        ]
        title = titles[0]

        frame.next_to(title, DOWN)

        self.add(frame, title)
        self.wait(3)
        for next_title in titles[1:]:
            self.play(Transform(title, next_title))
            self.wait(3)

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
            d_rect.line.set_color(d_rect.get_color())

        f_brace = Brace(rect, UP)
        g_brace = Brace(rect, LEFT)
        df_brace = Brace(df_rect, UP)
        dg_brace = Brace(dg_rect, LEFT)

        f_label = f_brace.get_text("$f$")
        g_label = g_brace.get_text("$g$")
        df_label = df_brace.get_text("$df$")
        dg_label = dg_brace.get_text("$dg$")

        VGroup(f_label, df_label).set_color(GREEN)
        VGroup(g_label, dg_label).set_color(RED)

        f_label.generate_target()
        g_label.generate_target()
        fg_group = VGroup(f_label.target, g_label.target)
        fg_group.generate_target()
        fg_group.target.arrange(RIGHT, buff = SMALL_BUFF)
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
            for mob in (df_brace, df_label, dg_brace, dg_label)
        ] + [
            ReplacementTransform(d_rect.line, d_rect)
            for d_rect in d_rects
        ])
        self.wait()
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
        self.wait()

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
            for alpha in [next(alpha_iter)]
        ]+[
            Write(VGroup(*it.chain(*[
                deriv.get_parts_by_tex(tex, substring = False)
                for tex in ("d(", ")", "=", "\\cdot", "+")
            ])))
        ], run_time = 3)
        self.wait()

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
        self.wait()
        R_copy = self.radius_label.copy()
        self.play(
            self.pi_creature.change_mode, "raise_right_hand",
            self.pi_creature.look_at, area,
            Transform(R_copy, area.get_part_by_tex("R"))
        )
        self.play(Write(area))
        self.remove(R_copy)
        self.wait()

        self.area = area

    def question_area(self):
        q_marks = TexMobject("???")
        q_marks.next_to(self.pi_creature, UP)
        rings = VGroup(*reversed(self.get_rings()))
        unwrapped_rings = VGroup(*[
            self.get_unwrapped(ring, to_edge = None)
            for ring in rings
        ])
        unwrapped_rings.arrange(UP, buff = SMALL_BUFF)
        unwrapped_rings.move_to(self.unwrapped_tip, UP)
        ring_anim_kwargs = {
            "run_time" : 3,
            "lag_ratio" : 0.5
        }

        self.play(
            Animation(self.area),
            Write(q_marks),
            self.pi_creature.change_mode, "confused",
            self.pi_creature.look_at, self.area,
        )
        self.wait()
        self.play(
            FadeIn(rings, **ring_anim_kwargs),
            Animation(self.radius_group),
            FadeOut(q_marks),
            self.pi_creature.change_mode, "thinking"
        )
        self.wait()
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
        self.wait()

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
        self.wait()
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
        self.wait()
        self.play(Write(VGroup(*ftc[-2:])))
        self.wait(2)

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
        self.force_skipping()

        self.write_radius_three()
        self.try_to_understand_area()
        self.slice_into_rings()
        self.isolate_one_ring()

        self.revert_to_original_skipping_status()
        self.straighten_ring_out()
        self.force_skipping()

        self.approximate_as_rectangle()

    def write_radius_three(self):
        three = TexMobject("3")
        three.move_to(self.radius_label)

        self.look_at(self.circle)
        self.play(Transform(
            self.radius_label, three,
            path_arc = np.pi
        ))
        self.wait()

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
                lag_ratio = 0.5
            ),
            Animation(self.radius_group),
            self.pi_creature.change_mode, "maybe"
        )
        self.wait(2)
        for new_lines in line_sets[1:]:
            self.play(
                Transform(lines, new_lines),
                Animation(self.radius_group)
            )
            self.wait()
        self.wait()
        self.play(FadeOut(lines), Animation(self.radius_group))

    def slice_into_rings(self):
        rings = self.get_rings()
        rings.set_stroke(BLACK, 1)

        self.play(
            FadeIn(
                rings,
                lag_ratio = 0.5,
                run_time = 3
            ),
            Animation(self.radius_group),
            self.pi_creature.change_mode, "pondering",
            self.pi_creature.look_at, self.circle
        )
        self.wait(2)
        for x in range(2):
            self.play(
                Rotate(rings, np.pi, in_place = True, run_time = 2),
                Animation(self.radius_group),
                self.pi_creature.change_mode, "happy"
            )
        self.wait(2)

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
        area_q.set_color(YELLOW)


        self.play(
            ring.shift, self.ring_shift_val,
            original_ring.set_fill, None, 0.25,
            Animation(self.radius_group),
        )

        VGroup(radius, r_label).shift(ring.get_center())
        area_q.next_to(ring, RIGHT)

        self.play(ShowCreation(radius))
        self.play(Write(r_label))
        self.wait()
        self.play(Write(area_q))
        self.wait()
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
        self.wait()
        self.change_mode("thinking")
        self.wait()

        self.original_ring = original_ring
        self.ring = ring
        self.ring_radius_group = VGroup(radius, r_label)
        self.area_q = area_q

    def straighten_ring_out(self):
        ring = self.ring.copy()
        trapezoid = TextMobject("Trapezoid?")
        rectangle_ish = TextMobject("Rectangle-ish")
        for text in trapezoid, rectangle_ish:
            text.next_to(
                self.pi_creature.get_corner(UP+RIGHT), 
                DOWN+RIGHT, buff = MED_LARGE_BUFF
            )

        self.unwrap_ring(ring, to_edge = RIGHT)
        self.change_mode("pondering")
        self.wait()
        self.play(Write(trapezoid))
        self.wait()
        self.play(trapezoid.shift, DOWN)
        strike = Line(
            trapezoid.get_left(), trapezoid.get_right(),
            stroke_color = RED,
            stroke_width = 8
        )
        self.play(
            Write(rectangle_ish),
            ShowCreation(strike),
            self.pi_creature.change_mode, "happy"
        )
        self.wait()
        self.play(*list(map(FadeOut, [trapezoid, strike])))

        self.unwrapped_ring = ring

    def approximate_as_rectangle(self):
        top_brace, side_brace = [
            Brace(
                self.unwrapped_ring, vect, buff = SMALL_BUFF,
                min_num_quads = 2,
            )
            for vect in (UP, LEFT)
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
        two_pi_r_dr.target.arrange(
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
        self.wait()
        self.play(
            GrowFromCenter(side_brace),
            Write(q_marks)
        )
        self.change_mode("confused")
        self.wait()
        for num_rings in 20, 7:
            self.show_alternate_width(num_rings)
        self.play(ReplacementTransform(q_marks, dr_label))
        self.play(
            ReplacementTransform(side_brace.copy(), alt_side_brace),
            ReplacementTransform(dr_label.copy(), alt_dr_label),
            run_time = 2
        )
        self.wait()
        self.play(
            dr_label.next_to, concrete_dr.copy(), LEFT, SMALL_BUFF, DOWN,
            Write(concrete_dr, run_time = 2),
            self.pi_creature.change_mode, "pondering"
        )
        self.wait(2)
        self.play(
            MoveToTarget(two_pi_r_dr),
            FadeIn(approx),
            self.area_q.get_part_by_tex("?").fade, 1,
        )
        self.wait()
        self.play(
            FadeOut(concrete_dr),
            dr_label.restore
        )
        self.show_alternate_width(
            40, 
            transformation_kwargs = {"run_time" : 4},
            return_to_original_configuration = False,
        )
        self.wait(2)
        self.look_at(self.circle)
        self.play(
            ApplyWave(self.rings, amplitude = 0.1),
            Animation(self.radius_group),
            Animation(alt_side_brace),
            Animation(alt_dr_label),
            run_time = 3,
            lag_ratio = 0.5
        )
        self.wait(2)

    def show_alternate_width(self, num_rings, **kwargs):
        self.transition_to_alt_config(
            dR = self.radius/num_rings, **kwargs
        )

class MoveForwardWithApproximation(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Move forward with \\\\",
            "the", "approximation"
        )
        self.change_student_modes("hesitant", "erm", "sassy")
        self.wait()
        words = TextMobject(
            "It gets better", 
            "\\\\ for smaller ",
            "$dr$"
        )
        words.set_color_by_tex("dr", BLUE)
        self.teacher_says(words, target_mode = "shruggie")
        self.wait(3)

class GraphRectangles(CircleScene, GraphScene):
    CONFIG = {
        "graph_origin" : 3.25*LEFT+2.5*DOWN,
        "x_min" : 0,
        "x_max" : 4,
        "x_axis_width" : 7,
        "x_labeled_nums" : list(range(5)),
        "x_axis_label" : "$r$",
        "y_min" : 0,
        "y_max" : 20,
        "y_tick_frequency" : 2.5,
        "y_labeled_nums" : list(range(5, 25, 5)),
        "y_axis_label" : "",
        "exclude_zero_label" : False,
        "num_rings_in_ring_sum_start" : 3,
        "tick_height" : 0.2,
    }
    def setup(self):
        CircleScene.setup(self)
        GraphScene.setup(self)
        self.setup_axes()
        self.remove(self.axes)

        # self.pi_creature.change_mode("pondering")
        # self.pi_creature.look_at(self.circle)
        # self.add(self.pi_creature)

        three = TexMobject("3")
        three.move_to(self.radius_label)
        self.radius_label.save_state()
        Transform(self.radius_label, three).update(1)

    def construct(self):
        self.draw_ring_sum()
        self.draw_r_values()
        self.unwrap_rings_onto_graph()
        self.draw_graph()
        self.point_out_approximation()
        self.let_dr_approah_zero()
        self.compute_area_under_graph()
        self.show_circle_unwrapping()

    def draw_ring_sum(self):
        rings = self.get_rings()
        rings.set_stroke(BLACK, 1)
        ring_sum, draw_ring_sum_anims = self.get_ring_sum(rings)
        area_label = TexMobject(
            "\\text{Area}", "\\approx", 
            "2\\pi", "r", "\\,dr"
        )
        area_label.set_color_by_tex("r", YELLOW, substring = False)
        area_label.next_to(ring_sum, RIGHT, aligned_edge = UP)
        area = area_label.get_part_by_tex("Area")
        arrow_start = area.get_corner(DOWN+LEFT)
        arrows = VGroup(*[
            Arrow(
                arrow_start,
                ring.target.get_boundary_point(
                    arrow_start - ring.target.get_center()
                ),
                color = ring.get_color()
            )
            for ring in rings
            if ring.target.get_fill_opacity() > 0
        ])
        
        self.add(rings, self.radius_group)
        self.remove(self.circle)
        self.wait()
        self.play(*draw_ring_sum_anims)
        self.play(Write(area_label, run_time = 2))
        self.play(ShowCreation(arrows))
        self.wait()

        self.ring_sum = ring_sum
        area_label.add(arrows)
        self.area_label = area_label
        self.rings = rings

    def draw_r_values(self):
        values_of_r = TextMobject("Values of ", "$r$")
        values_of_r.set_color_by_tex("r", YELLOW)
        values_of_r.next_to(
            self.x_axis, UP, 
            buff = 2*LARGE_BUFF,
            aligned_edge = LEFT
        )

        r_ticks = VGroup(*[
            Line(
                self.coords_to_point(r, -self.tick_height),
                self.coords_to_point(r, self.tick_height),
                color = YELLOW
            )
            for r in np.arange(0, 3, 0.1)
        ])
        arrows = VGroup(*[
            Arrow(
                values_of_r.get_part_by_tex("r").get_bottom(),
                tick.get_top(),
                buff = SMALL_BUFF,
                color = YELLOW,
                tip_length = 0.15
            )
            for tick in (r_ticks[0], r_ticks[-1])
        ])
        first_tick = r_ticks[0].copy()
        moving_arrow = arrows[0].copy()

        index = 2
        dr_brace = Brace(
            VGroup(*r_ticks[index:index+2]), 
            DOWN, buff = SMALL_BUFF
        )
        dr_label = TexMobject("dr")
        dr_label.next_to(
            dr_brace, DOWN, 
            buff = SMALL_BUFF, 
            aligned_edge = LEFT
        )
        dr_group = VGroup(dr_brace, dr_label)

        self.play(
            FadeIn(values_of_r),
            FadeIn(self.x_axis),
        )
        self.play(
            ShowCreation(moving_arrow),
            ShowCreation(first_tick),
        )
        self.play(Indicate(self.rings[0]))
        self.wait()
        self.play(
            Transform(moving_arrow, arrows[-1]),
            ShowCreation(r_ticks, lag_ratio = 0.5),
            run_time = 2
        )
        self.play(Indicate(self.rings[-1]))
        self.wait()
        self.play(FadeIn(dr_group))
        self.wait()
        self.play(*list(map(FadeOut, [moving_arrow, values_of_r])))

        self.x_axis.add(r_ticks)
        self.r_ticks = r_ticks
        self.dr_group = dr_group
        
    def unwrap_rings_onto_graph(self):
        rings = self.rings
        graph = self.get_graph(lambda r : 2*np.pi*r)
        flat_graph = self.get_graph(lambda r : 0)
        rects, flat_rects = [
            self.get_riemann_rectangles(
                g, x_min = 0, x_max = 3, dx = self.dR,
                start_color = self.rings[0].get_fill_color(),
                end_color = self.rings[-1].get_fill_color(),
            )
            for g in (graph, flat_graph)
        ]
        self.graph, self.flat_rects = graph, flat_rects

        transformed_rings = VGroup()
        self.ghost_rings = VGroup()        
        for index, rect, r in zip(it.count(), rects, np.arange(0, 3, 0.1)):
            proportion = float(index)/len(rects)
            ring_index = int(len(rings)*proportion**0.6)
            ring = rings[ring_index]
            if ring in transformed_rings:
                ring = ring.copy()
            transformed_rings.add(ring)
            if ring.get_fill_opacity() > 0:
                ghost_ring = ring.copy()
                ghost_ring.set_fill(opacity = 0.25)
                self.add(ghost_ring, ring)
                self.ghost_rings.add(ghost_ring)

            ring.rect = rect

            n_anchors = ring.get_num_curves()            
            target = VMobject()
            target.set_points_as_corners([
                interpolate(ORIGIN,  DOWN, a)
                for a in np.linspace(0, 1, n_anchors/2)
            ]+[
                interpolate(DOWN+RIGHT, RIGHT, a)
                for a in np.linspace(0, 1, n_anchors/2)
            ])
            target.replace(rect, stretch = True)
            target.stretch_to_fit_height(2*np.pi*r)
            target.move_to(rect, DOWN)
            target.set_stroke(BLACK, 1)
            target.set_fill(ring.get_fill_color(), 1)
            ring.target = target
            ring.original_ring = ring.copy()

        foreground_animations = list(map(Animation, [self.x_axis, self.area_label]))
        example_ring = transformed_rings[2]

        self.play(
            MoveToTarget(
                example_ring,
                path_arc = -np.pi/2,
                run_time = 2
            ),
            Animation(self.x_axis),
        )
        self.wait(2)
        self.play(*[
            MoveToTarget(
                ring,
                path_arc = -np.pi/2,
                run_time = 4,
                rate_func = squish_rate_func(smooth, alpha, alpha+0.25)
            )
            for ring, alpha in zip(
                transformed_rings, 
                np.linspace(0, 0.75, len(transformed_rings))
            )
        ] + foreground_animations)
        self.wait()

        ##Demonstrate height of one rect
        highlighted_ring = transformed_rings[6].copy()
        original_ring = transformed_rings[6].original_ring
        original_ring.move_to(highlighted_ring, RIGHT)
        original_ring.set_fill(opacity = 1)
        highlighted_ring.save_state()

        side_brace = Brace(highlighted_ring, RIGHT)
        height_label = side_brace.get_text("2\\pi", "r")
        height_label.set_color_by_tex("r", YELLOW)

        self.play(
            transformed_rings.set_fill, None, 0.2,
            Animation(highlighted_ring),
            *foreground_animations
        )
        self.play(
            self.dr_group.arrange, DOWN,
            self.dr_group.next_to, highlighted_ring, 
            DOWN, SMALL_BUFF
        )
        self.wait()
        self.play(
            GrowFromCenter(side_brace),
            Write(height_label)
        )
        self.wait()
        self.play(Transform(highlighted_ring, original_ring))
        self.wait()
        self.play(highlighted_ring.restore)
        self.wait()
        self.play(
            transformed_rings.set_fill, None, 1,
            FadeOut(side_brace),
            FadeOut(height_label),
            *foreground_animations
        )
        self.remove(highlighted_ring)
        self.wait()

        ##Rescale
        self.play(*[
            ApplyMethod(
                ring.replace, ring.rect, 
                method_kwargs = {"stretch" : True}
            )
            for ring in transformed_rings
        ] + [
            Write(self.y_axis),
            FadeOut(self.area_label),
        ] + foreground_animations)
        self.remove(transformed_rings)
        self.add(rects)
        self.wait()

        self.rects = rects

    def draw_graph(self):
        graph_label = self.get_graph_label(
            self.graph, "2\\pi r", 
            direction = UP+LEFT,
            x_val = 2.5,
            buff = SMALL_BUFF
        )

        self.play(ShowCreation(self.graph))
        self.play(Write(graph_label))
        self.wait()
        self.play(*[
            Transform(
                rect, flat_rect,
                run_time = 2,
                rate_func = squish_rate_func(
                    lambda t : 0.1*there_and_back(t), 
                    alpha, alpha+0.5
                ),
                lag_ratio = 0.5
            )
            for rect, flat_rect, alpha in zip(
                self.rects, self.flat_rects,
                np.linspace(0, 0.5, len(self.rects))
            )
        ] + list(map(Animation, [self.x_axis, self.graph]))
        )
        self.wait(2)

    def point_out_approximation(self):
        rect = self.rects[10]
        rect.generate_target()
        rect.save_state()
        approximation = TextMobject("= Approximation")
        approximation.scale(0.8)
        group = VGroup(rect.target, approximation)
        group.arrange(RIGHT)
        group.to_edge(RIGHT)

        self.play(
            MoveToTarget(rect),
            Write(approximation),
        )
        self.wait(2)
        self.play(
            rect.restore,
            FadeOut(approximation)
        )
        self.wait()

    def let_dr_approah_zero(self):
        thinner_rects_list = [
            self.get_riemann_rectangles(
                self.graph,
                x_min = 0, 
                x_max = 3,
                dx = 1./(10*2**n),
                stroke_width = 1./(2**n),
                start_color = self.rects[0].get_fill_color(),
                end_color = self.rects[-1].get_fill_color(),
            )
            for n in range(1, 5)
        ]

        self.play(*list(map(FadeOut, [self.r_ticks, self.dr_group])))
        self.x_axis.remove(self.r_ticks, *self.r_ticks)
        for new_rects in thinner_rects_list:
            self.play(
                Transform(
                    self.rects, new_rects, 
                    lag_ratio = 0.5,
                    run_time = 2
                ),
                Animation(self.axes),
                Animation(self.graph),
            )
            self.wait()
        self.play(ApplyWave(
            self.rects,
            direction = RIGHT,
            run_time = 2,
            lag_ratio = 0.5,
        ))
        self.wait()

    def compute_area_under_graph(self):
        formula, formula_with_R = formulas = [
            self.get_area_formula(R)
            for R in ("3", "R")
        ]
        for mob in formulas:
            mob.to_corner(UP+RIGHT, buff = MED_SMALL_BUFF)

        brace = Brace(self.rects, RIGHT)
        height_label = brace.get_text("$2\\pi \\cdot 3$")
        height_label_with_R = brace.get_text("$2\\pi \\cdot R$")
        base_line = Line(
            self.coords_to_point(0, 0),
            self.coords_to_point(3, 0),
            color = YELLOW
        )

        fresh_rings = self.get_rings(dR = 0.025)
        fresh_rings.set_stroke(width = 0)
        self.radius_label.restore()
        VGroup(
            fresh_rings, self.radius_group
        ).to_corner(UP+LEFT, buff = SMALL_BUFF)

        self.play(Write(formula.top_line, run_time = 2))
        self.play(FocusOn(base_line))
        self.play(ShowCreation(base_line))
        self.wait()
        self.play(
            GrowFromCenter(brace),
            Write(height_label)
        )
        self.wait()
        self.play(FocusOn(formula))
        self.play(Write(formula.mid_line))
        self.wait()
        self.play(Write(formula.bottom_line))
        self.wait(2)

        self.play(*list(map(FadeOut, [
            self.ghost_rings,
            self.ring_sum.tex_mobs
        ])))
        self.play(*list(map(FadeIn, [fresh_rings, self.radius_group])))
        self.wait()
        self.play(
            Transform(formula, formula_with_R),
            Transform(height_label, height_label_with_R),
        )
        self.wait(2)

        self.fresh_rings = fresh_rings

    def show_circle_unwrapping(self):
        rings = self.fresh_rings
        rings.rotate_in_place(np.pi)
        rings.submobjects.reverse()
        ghost_rings = rings.copy()
        ghost_rings.set_fill(opacity = 0.25)
        self.add(ghost_rings, rings, self.radius_group)

        unwrapped = VGroup(*[
            self.get_unwrapped(ring, to_edge = None)
            for ring in rings
        ])
        unwrapped.stretch_to_fit_height(1)
        unwrapped.stretch_to_fit_width(2)
        unwrapped.move_to(ORIGIN, DOWN)
        unwrapped.apply_function(
            lambda p : np.dot(p, 
                np.array([[1, 0, 0], [-1, 1, 0], [0, 0, 1]])
            ),
            maintain_smoothness = False
        )
        unwrapped.rotate(np.pi/2)
        unwrapped.replace(self.rects, stretch = True)

        self.play(self.rects.fade, 0.8)
        self.play(
            Transform(
                rings, unwrapped,
                run_time = 5,
                lag_ratio = 0.5,
            ),
            Animation(self.radius_group)
        )
        self.wait()

    #####

    def get_ring_sum(self, rings):
        arranged_group = VGroup()
        tex_mobs = VGroup()
        for ring in rings:
            ring.generate_target()
            ring.target.set_stroke(width = 0)

        for ring in rings[:self.num_rings_in_ring_sum_start]:
            plus = TexMobject("+")
            arranged_group.add(ring.target)
            arranged_group.add(plus)
            tex_mobs.add(plus)
        dots = TexMobject("\\vdots")
        plus = TexMobject("+")
        arranged_group.add(dots, plus)
        tex_mobs.add(dots, plus)
        last_ring = rings[-1]

        arranged_group.add(last_ring.target)
        arranged_group.arrange(DOWN, buff = SMALL_BUFF)
        arranged_group.set_height(FRAME_HEIGHT-1)
        arranged_group.to_corner(DOWN+LEFT, buff = MED_SMALL_BUFF)
        for mob in tex_mobs:
            mob.scale_in_place(0.7)

        middle_rings = rings[self.num_rings_in_ring_sum_start:-1]
        alphas = np.linspace(0, 1, len(middle_rings))
        for ring, alpha in zip(middle_rings, alphas):
            ring.target.set_fill(opacity = 0)
            ring.target.move_to(interpolate(
                dots.get_left(), last_ring.target.get_center(), alpha
            ))

        draw_ring_sum_anims = [Write(tex_mobs)]
        draw_ring_sum_anims += [
            MoveToTarget(
                ring,
                run_time = 3,
                path_arc = -np.pi/3,
                rate_func = squish_rate_func(smooth, alpha, alpha+0.8)
            )
            for ring, alpha in zip(rings, np.linspace(0, 0.2, len(rings)))
        ]
        draw_ring_sum_anims.append(FadeOut(self.radius_group))
        
        ring_sum = VGroup(rings, tex_mobs)
        ring_sum.rings = VGroup(*[r.target for r in rings])
        ring_sum.tex_mobs = tex_mobs
        
        return ring_sum, draw_ring_sum_anims

    def get_area_formula(self, R):
        formula = TexMobject(
            "\\text{Area}", "&= \\frac{1}{2}", "b", "h",
            "\\\\ &=", "\\frac{1}{2}", "(%s)"%R, "(2\\pi \\cdot %s)"%R,
            "\\\\ &=", "\\pi ", "%s"%R, "^2"
            
        )
        formula.set_color_by_tex("b", GREEN, substring = False)
        formula.set_color_by_tex("h", RED, substring = False)
        formula.set_color_by_tex("%s"%R, GREEN)
        formula.set_color_by_tex("(2\\pi ", RED)
        formula.set_color_by_tex("(2\\pi ", RED)
        formula.scale(0.8)

        formula.top_line = VGroup(*formula[:4])
        formula.mid_line = VGroup(*formula[4:8])
        formula.bottom_line = VGroup(*formula[8:])
        return formula

class ThinkLikeAMathematician(TeacherStudentsScene):
    def construct(self):
        pi_R_squraed = TexMobject("\\pi", "R", "^2")
        pi_R_squraed.set_color_by_tex("R", YELLOW)
        pi_R_squraed.move_to(self.get_students(), UP)
        pi_R_squraed.set_fill(opacity = 0)

        self.play(
            pi_R_squraed.shift, 2*UP,
            pi_R_squraed.set_fill, None, 1
        )
        self.change_student_modes(*["hooray"]*3)
        self.wait(2)
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = self.teacher.eyes,
            added_anims = [PiCreatureSays(
                self.teacher, "But why did \\\\ that work?"
            )]
        )
        self.play(FadeOut(pi_R_squraed))
        self.look_at(2*UP+4*LEFT)
        self.wait(5)

class TwoThingsToNotice(TeacherStudentsScene):
    def construct(self):
        words = TextMobject(
            "Two things to \\\\ note about",
            "$dr$",
        )
        words.set_color_by_tex("dr", GREEN)
        self.teacher_says(words, run_time = 1)
        self.wait(3)

class RecapCircleSolution(GraphRectangles, ReconfigurableScene):
    def setup(self):
        GraphRectangles.setup(self)
        ReconfigurableScene.setup(self)

    def construct(self):
        self.break_up_circle()
        self.show_sum()
        self.dr_indicates_spacing()
        self.smaller_dr()
        self.show_riemann_sum()
        self.limiting_riemann_sum()
        self.full_precision()

    def break_up_circle(self):
        self.remove(self.circle)
        rings = self.get_rings()
        rings.set_stroke(BLACK, 1)
        ring_sum, draw_ring_sum_anims = self.get_ring_sum(rings)

        hard_problem = TextMobject("Hard problem")
        down_arrow = TexMobject("\\Downarrow")
        sum_words = TextMobject("Sum of many \\\\ small values")
        integral_condition = VGroup(hard_problem, down_arrow, sum_words)
        integral_condition.arrange(DOWN)
        integral_condition.scale(0.8)
        integral_condition.to_corner(UP+RIGHT)
        
        self.add(rings, self.radius_group)
        self.play(FadeIn(
            integral_condition, 
            lag_ratio = 0.5
        ))
        self.wait()
        self.play(*draw_ring_sum_anims)

        self.rings = rings
        self.integral_condition = integral_condition

    def show_sum(self):
        visible_rings = [ring for ring in self.rings if ring.get_fill_opacity() > 0]
        radii = self.dR*np.arange(len(visible_rings))
        radii[-1] = 3-self.dR

        radial_lines = VGroup()
        for ring in visible_rings:
            radius_line = Line(ORIGIN, ring.R*RIGHT, color = YELLOW)
            radius_line.rotate(np.pi/4)
            radius_line.shift(ring.get_center())
            radial_lines.add(radius_line)

        approximations = VGroup()
        for ring, radius in zip(visible_rings, radii):
            label = TexMobject(
                "\\approx", "2\\pi", 
                "(%s)"%str(radius), "(%s)"%str(self.dR)
            )
            label[2].set_color(YELLOW)
            label[3].set_color(GREEN)
            label.scale(0.75)
            label.next_to(ring, RIGHT)
            approximations.add(label)
        approximations[-1].shift(UP+0.5*LEFT)
        area_label = TexMobject("2\\pi", "r", "\\, dr")
        area_label.set_color_by_tex("r", YELLOW)
        area_label.set_color_by_tex("dr", GREEN)
        area_label.next_to(approximations, RIGHT, buff = 2*LARGE_BUFF)
        arrows = VGroup(*[
            Arrow(
                area_label.get_left(),
                approximation.get_right(),
                color = WHITE
            )
            for approximation in approximations
        ])

        self.play(Write(area_label))
        self.play(
            ShowCreation(arrows, lag_ratio = 0),
            FadeIn(radial_lines),
            *[
                ReplacementTransform(
                    area_label.copy(),
                    VGroup(*approximation[1:])
                )
                for approximation in approximations
            ]
        )
        self.wait()
        self.play(Write(VGroup(*[
            approximation[0]
            for approximation in approximations
        ])))
        self.wait()

        self.area_label = area_label
        self.area_arrows = arrows
        self.approximations = approximations

    def dr_indicates_spacing(self):
        r_ticks = VGroup(*[
            Line(
                self.coords_to_point(r, -self.tick_height),
                self.coords_to_point(r, self.tick_height),
                color = YELLOW
            )
            for r in np.arange(0, 3, self.dR)
        ])

        index = int(0.75*len(r_ticks))
        brace_ticks = VGroup(*r_ticks[index:index+2])
        dr_brace = Brace(brace_ticks, UP, buff = SMALL_BUFF)

        dr = self.area_label.get_part_by_tex("dr")
        dr_copy = dr.copy()
        circle = Circle().replace(dr)
        circle.scale_in_place(1.3)

        dr_num = self.approximations[0][-1]

        self.play(ShowCreation(circle))
        self.play(FadeOut(circle))
        self.play(ReplacementTransform(
            dr.copy(), dr_num,
            run_time = 2,
            path_arc = np.pi/2,
        ))
        self.wait()
        self.play(FadeIn(self.x_axis))
        self.play(Write(r_ticks, run_time = 1))
        self.wait()
        self.play(
            GrowFromCenter(dr_brace),
            dr_copy.next_to, dr_brace.copy(), UP
        )
        self.wait()

        self.r_ticks = r_ticks
        self.dr_brace_group = VGroup(dr_brace, dr_copy)

    def smaller_dr(self):
        self.transition_to_alt_config(dR = 0.05)

    def show_riemann_sum(self):
        graph = self.get_graph(lambda r : 2*np.pi*r)
        graph_label = self.get_graph_label(
            graph, "2\\pi r",
            x_val = 2.5,
            direction = UP+LEFT
        )
        rects = self.get_riemann_rectangles(
            graph,
            x_min = 0, 
            x_max = 3,
            dx = self.dR
        )

        self.play(
            Write(self.y_axis, run_time = 2),
            *list(map(FadeOut, [
                self.approximations,
                self.area_label,
                self.area_arrows,
                self.dr_brace_group,
                self.r_ticks,
            ]))
        )
        self.play(
            ReplacementTransform(
                self.rings.copy(), rects,
                run_time = 2,
                lag_ratio = 0.5
            ),
            Animation(self.x_axis),
        )
        self.play(ShowCreation(graph))
        self.play(Write(graph_label))
        self.wait()

        self.graph = graph
        self.graph_label = graph_label
        self.rects = rects

    def limiting_riemann_sum(self):
        thinner_rects_list = [
            self.get_riemann_rectangles(
                self.graph,
                x_min = 0, 
                x_max = 3,
                dx = 1./(10*2**n),
                stroke_width = 1./(2**n),
                start_color = self.rects[0].get_fill_color(),
                end_color = self.rects[-1].get_fill_color(),
            )
            for n in range(1, 4)
        ]

        for new_rects in thinner_rects_list:
            self.play(
                Transform(
                    self.rects, new_rects, 
                    lag_ratio = 0.5,
                    run_time = 2
                ),
                Animation(self.axes),
                Animation(self.graph),
            )
            self.wait()

    def full_precision(self):
        words = TextMobject("Area under \\\\ a graph")
        group = VGroup(TexMobject("\\Downarrow"), words)
        group.arrange(DOWN)
        group.set_color(YELLOW)
        group.scale(0.8)
        group.next_to(self.integral_condition, DOWN)

        arc = Arc(start_angle = 2*np.pi/3, angle = 2*np.pi/3)
        arc.scale(2)
        arc.add_tip()
        arc.add(arc[1].copy().rotate(np.pi, RIGHT))
        arc_next_to_group = VGroup(
            self.integral_condition[0][0],
            words[0]
        )
        arc.set_height(
            arc_next_to_group.get_height()-MED_LARGE_BUFF
        )
        arc.next_to(arc_next_to_group, LEFT, SMALL_BUFF)

        self.play(Write(group))
        self.wait()
        self.play(ShowCreation(arc))
        self.wait()

class ExampleIntegralProblems(PiCreatureScene, GraphScene):
    CONFIG = {
        "dt" : 0.2,
        "t_max" : 7,
        "x_max" : 8,
        "y_axis_height" : 5.5,
        "x_axis_label" : "$t$",
        "y_axis_label" : "",
        "graph_origin" : 3*DOWN + 4.5*LEFT
    }
    def construct(self):
        self.write_integral_condition()
        self.show_car()
        self.show_graph()
        self.let_dt_approach_zero()
        self.show_confusion()

    def write_integral_condition(self):
        words = TextMobject(
            "Hard problem $\\Rightarrow$ Sum of many small values"
        )
        words.to_edge(UP)

        self.play(
            Write(words),
            self.pi_creature.change_mode, "raise_right_hand"
        )
        self.wait()

        self.words = words

    def show_car(self):
        car = Car()
        start, end = 3*LEFT+UP, 5*RIGHT+UP
        car.move_to(start)

        line = Line(start, end)
        tick_height = MED_SMALL_BUFF
        ticks = VGroup(*[
            Line(
                p+tick_height*UP/2,
                p+tick_height*DOWN/2,
                color = YELLOW,
                stroke_width = 2
            )
            for t in np.arange(0, self.t_max, self.dt)
            for p in [
                line.point_from_proportion(smooth(t/self.t_max))
            ]
        ])

        index = int(len(ticks)/2)
        brace_ticks = VGroup(*ticks[index:index+2])
        brace = Brace(brace_ticks, UP)
        v_dt = TexMobject("v(t)", "dt")
        v_dt.next_to(brace, UP, SMALL_BUFF)
        v_dt.set_color(YELLOW)
        v_dt_brace_group = VGroup(brace, v_dt)

        self.play(
            FadeIn(car),
            self.pi_creature.change_mode, "plain"
        )
        self.play(
            MoveCar(car, end),
            FadeIn(
                ticks, 
                lag_ratio=1,
                rate_func=linear,
            ),
            ShowCreation(line),
            FadeIn(
                v_dt_brace_group,
                rate_func = squish_rate_func(smooth, 0.6, 0.8)
            ),
            run_time = self.t_max
        )
        self.wait()
        for mob in v_dt:
            self.play(Indicate(mob))
            self.wait(2)

        self.v_dt_brace_group = v_dt_brace_group
        self.line = line
        self.ticks = ticks
        self.car = car

    def show_graph(self):
        self.setup_axes()
        self.remove(self.axes)
        s_graph = self.get_graph(
            lambda t : 1.8*self.y_max*smooth(t/self.t_max)
        )
        v_graph = self.get_derivative_graph(s_graph)
        rects = self.get_riemann_rectangles(
            v_graph,
            x_min = 0, 
            x_max = self.t_max,
            dx = self.dt
        )
        rects.set_fill(opacity = 0.5)
        pre_rects = rects.copy()
        pre_rects.rotate(-np.pi/2)
        for index, pre_rect in enumerate(pre_rects):
            ti1 = len(self.ticks)*index/len(pre_rects)
            ti2 = min(ti1+1, len(self.ticks)-1)
            tick_pair = VGroup(self.ticks[ti1], self.ticks[ti2])
            pre_rect.stretch_to_fit_width(tick_pair.get_width())
            pre_rect.move_to(tick_pair)

        special_rect = rects[int(0.6*len(rects))]
        brace = Brace(special_rect, LEFT, buff = 0)

        v_dt_brace_group_copy = self.v_dt_brace_group.copy()
        start_brace, (v_t, dt) = v_dt_brace_group_copy

        self.play(
            FadeIn(
                pre_rects, 
                run_time = 2,
                lag_ratio = 0.5
            ),
            Animation(self.ticks)
        )
        self.play(
            ReplacementTransform(
                pre_rects, rects,
                run_time = 3,
                lag_ratio = 0.5
            ),
            Animation(self.ticks),
            Write(self.axes, run_time = 1)
        )
        self.play(ShowCreation(v_graph))
        self.change_mode("pondering")
        self.wait()
        self.play(
            v_t.next_to, brace, LEFT, SMALL_BUFF,
            dt.next_to, special_rect, DOWN,
            special_rect.set_fill, None, 1,
            ReplacementTransform(start_brace, brace),
        )
        self.wait(3)

        self.v_graph = v_graph
        self.rects = rects
        self.v_dt_brace_group_copy = v_dt_brace_group_copy

    def let_dt_approach_zero(self):
        thinner_rects_list = [
            self.get_riemann_rectangles(
                self.v_graph,
                x_min = 0,
                x_max = self.t_max,
                dx = self.dt/(2**n),
                stroke_width = 1./(2**n)
            )
            for n in range(1, 4)
        ]

        self.play(
            self.rects.set_fill, None, 1,
            Animation(self.x_axis),
            FadeOut(self.v_dt_brace_group_copy),
        )
        self.change_mode("thinking")
        self.wait()
        for thinner_rects in thinner_rects_list:
            self.play(
                Transform(
                    self.rects, thinner_rects,
                    run_time = 2,
                    lag_ratio = 0.5
                )
            )
            self.wait()

    def show_confusion(self):
        randy = Randolph(color = BLUE_C)
        randy.to_corner(DOWN+LEFT)
        randy.to_edge(LEFT, buff = MED_SMALL_BUFF)

        self.play(FadeIn(randy))
        self.play(
            randy.change_mode, "confused",
            randy.look_at, self.rects
        )
        self.play(
            self.pi_creature.change_mode, "confused",
            self.pi_creature.look_at, randy.eyes
        )
        self.play(Blink(randy))
        self.wait()

class MathematicianPonderingAreaUnderDifferentCurves(PiCreatureScene):
    def construct(self):
        self.play(
            self.pi_creature.change_mode, "raise_left_hand",
            self.pi_creature.look, UP+LEFT
        )
        self.wait(4)
        self.play(
            self.pi_creature.change_mode, "raise_right_hand",
            self.pi_creature.look, UP+RIGHT
        )
        self.wait(4)
        self.play(
            self.pi_creature.change_mode, "pondering",
            self.pi_creature.look, UP+LEFT
        )
        self.wait(2)

    def create_pi_creature(self):
        self.pi_creature = Randolph(color = BLUE_C)
        self.pi_creature.to_edge(DOWN)
        return self.pi_creature

class AreaUnderParabola(GraphScene):
    CONFIG = {
        "x_max" : 4,
        "x_labeled_nums" : list(range(-1, 5)),
        "y_min" : 0,
        "y_max" : 15,
        "y_tick_frequency" : 2.5,
        "y_labeled_nums" : list(range(5, 20, 5)),
        "n_rect_iterations" : 6,
        "default_right_x" : 3,
        "func" : lambda x : x**2,
        "graph_label_tex" : "x^2",
        "graph_label_x_val" : 3.8,
    }
    def construct(self):
        self.setup_axes()
        self.show_graph()
        self.show_area()
        self.ask_about_area()
        self.show_confusion()
        self.show_variable_endpoint()
        self.name_integral()

    def show_graph(self):
        graph = self.get_graph(self.func)
        graph_label = self.get_graph_label(
            graph, self.graph_label_tex, 
            direction = LEFT,
            x_val = self.graph_label_x_val,
        )

        self.play(ShowCreation(graph))
        self.play(Write(graph_label))
        self.wait()

        self.graph = graph
        self.graph_label = graph_label

    def show_area(self):
        dx_list = [0.25/(2**n) for n in range(self.n_rect_iterations)]
        rect_lists = [
            self.get_riemann_rectangles(
                self.graph,
                x_min = 0,
                x_max = self.default_right_x,
                dx = dx,
                stroke_width = 4*dx,
            )
            for dx in dx_list
        ]
        rects = rect_lists[0]
        foreground_mobjects = [self.axes, self.graph]

        self.play(
            DrawBorderThenFill(
                rects,
                run_time = 2,
                rate_func = smooth,
                lag_ratio = 0.5,
            ),
            *list(map(Animation, foreground_mobjects))
        )
        self.wait()
        for new_rects in rect_lists[1:]:
            self.play(
                Transform(
                    rects, new_rects,
                    lag_ratio = 0.5,
                ), 
                *list(map(Animation, foreground_mobjects))
            )
        self.wait()

        self.rects = rects
        self.dx = dx_list[-1]
        self.foreground_mobjects = foreground_mobjects

    def ask_about_area(self):
        rects = self.rects
        question = TextMobject("Area?")
        question.move_to(rects.get_top(), DOWN)
        mid_rect = rects[2*len(rects)/3]
        arrow = Arrow(question.get_bottom(), mid_rect.get_center())

        v_lines = VGroup(*[
            DashedLine(
                FRAME_HEIGHT*UP, ORIGIN,
                color = RED
            ).move_to(self.coords_to_point(x, 0), DOWN)
            for x in (0, self.default_right_x)
        ])

        self.play(
            Write(question),
            ShowCreation(arrow)
        )
        self.wait()
        self.play(ShowCreation(v_lines, run_time = 2))
        self.wait()

        self.foreground_mobjects += [question, arrow]
        self.question = question
        self.question_arrow = arrow
        self.v_lines = v_lines

    def show_confusion(self):
        morty = Mortimer()
        morty.to_corner(DOWN+RIGHT)

        self.play(FadeIn(morty))
        self.play(
            morty.change_mode, "confused",
            morty.look_at, self.question,
        )
        self.play(morty.look_at, self.rects.get_bottom())
        self.play(Blink(morty))
        self.play(morty.look_at, self.question)
        self.wait()
        self.play(Blink(morty))
        self.play(FadeOut(morty))

    def show_variable_endpoint(self):
        triangle = RegularPolygon(
            n = 3,
            start_angle = np.pi/2,
            stroke_width = 0,
            fill_color = WHITE,
            fill_opacity = 1,
        )
        triangle.set_height(0.25)
        triangle.move_to(self.v_lines[1].get_bottom(), UP)
        x_label = TexMobject("x")
        x_label.next_to(triangle, DOWN)
        self.right_point_slider = VGroup(triangle, x_label)

        A_func = TexMobject("A(x)")
        A_func.move_to(self.question, DOWN)

        self.play(FadeOut(self.x_axis.numbers))
        self.x_axis.remove(*self.x_axis.numbers)
        self.foreground_mobjects.remove(self.axes)
        self.play(DrawBorderThenFill(self.right_point_slider))
        self.move_right_point_to(2)
        self.wait()
        self.move_right_point_to(self.default_right_x)
        self.wait()
        self.play(ReplacementTransform(self.question, A_func))
        self.wait()

        self.A_func = A_func

    def name_integral(self):
        f_tex = "$%s$"%self.graph_label_tex
        words = TextMobject("``Integral'' of ", f_tex)
        words.set_color_by_tex(f_tex, self.graph_label.get_color())
        brace = Brace(self.A_func, UP)
        words.next_to(brace, UP)

        self.play(
            Write(words),
            GrowFromCenter(brace)
        )
        self.wait()
        for x in 4, 2, self.default_right_x:
            self.move_right_point_to(x, run_time = 2)

        self.integral_words_group = VGroup(brace, words)

    ####

    def move_right_point_to(self, target_x, **kwargs):
        v_line = self.v_lines[1]
        slider = self.right_point_slider
        rects = self.rects
        curr_x = self.x_axis.point_to_number(v_line.get_bottom())

        group = VGroup(rects, v_line, slider)
        def update_group(group, alpha):
            rects, v_line, slider = group
            new_x = interpolate(curr_x, target_x, alpha)
            new_rects = self.get_riemann_rectangles(
                self.graph,
                x_min = 0,
                x_max = new_x,
                dx = self.dx*new_x/3.0,
                stroke_width = rects[0].get_stroke_width(),
            )
            point = self.coords_to_point(new_x, 0)
            v_line.move_to(point, DOWN)
            slider.move_to(point, UP)
            Transform(rects, new_rects).update(1)
            return VGroup(rects, v_line, slider)

        self.play(
            UpdateFromAlphaFunc(
                group, update_group,
                **kwargs
            ),
            *list(map(Animation, self.foreground_mobjects))
        )

class WhoCaresAboutArea(TeacherStudentsScene):
    def construct(self):
        point = 2*RIGHT+3*UP

        self.student_says(
            "Who cares!?!", target_mode = "angry",
        )
        self.play(self.teacher.change_mode, "guilty")
        self.wait()
        self.play(
            RemovePiCreatureBubble(self.students[1]),
            self.teacher.change_mode, "raise_right_hand",
            self.teacher.look_at, point
        )
        self.change_student_modes(
            *["pondering"]*3, 
            look_at_arg = point,
            added_anims = [self.teacher.look_at, point]

        )
        self.wait(3)

class PlayWithThisIdea(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Play with", "the", "thought!",
            target_mode = "hooray"
        )
        self.change_student_modes(*["happy"]*3)
        self.wait()
        equation = TexMobject("A(x)", "\\leftrightarrow", "x^2")
        equation.set_color_by_tex("x^2", BLUE)
        self.teacher_says(equation, target_mode = "sassy")
        self.change_student_modes(*["thinking"]*3)
        self.wait(2)

class PlayingTowardsDADX(AreaUnderParabola, ReconfigurableScene):
    CONFIG = {
        "n_rect_iterations" : 6,
        "deriv_dx" : 0.2,
        "graph_origin" : 2.5*DOWN + 6*LEFT,
    }
    def setup(self):
        AreaUnderParabola.setup(self)
        ReconfigurableScene.setup(self)

    def construct(self):
        self.fast_forward_to_end_of_previous_scene()

        self.nudge_x()
        self.describe_sliver()
        self.shrink_dx()
        self.write_dA_dx()
        self.dA_remains_a_mystery()
        self.write_example_inputs()
        self.show_dA_dx_in_detail()
        self.show_smaller_x()

    def fast_forward_to_end_of_previous_scene(self):
        self.force_skipping()
        AreaUnderParabola.construct(self)
        self.revert_to_original_skipping_status()

    def nudge_x(self):
        shadow_rects = self.rects.copy()
        shadow_rects.set_fill(BLACK, opacity = 0.5)

        original_v_line = self.v_lines[1].copy()
        right_v_lines = VGroup(original_v_line, self.v_lines[1])
        curr_x = self.x_axis.point_to_number(original_v_line.get_bottom())

        self.add(original_v_line)
        self.foreground_mobjects.append(original_v_line)
        self.move_right_point_to(curr_x + self.deriv_dx)
        self.play(
            FadeIn(shadow_rects), 
            *list(map(Animation, self.foreground_mobjects))
        )

        self.shadow_rects = shadow_rects
        self.right_v_lines = right_v_lines

    def describe_sliver(self):
        dx_brace = Brace(self.right_v_lines, DOWN, buff = 0)
        dx_label = dx_brace.get_text("$dx$")
        dx_group = VGroup(dx_brace, dx_label)

        dA_rect = Rectangle(
            width = self.right_v_lines.get_width(),
            height = self.shadow_rects[-1].get_height(),
            stroke_width = 0,
            fill_color = YELLOW,
            fill_opacity = 0.5,
        ).move_to(self.right_v_lines, DOWN)
        dA_label = TexMobject("d", "A")
        dA_label.next_to(dA_rect, RIGHT, MED_LARGE_BUFF, UP)
        dA_label.set_color(GREEN)
        dA_arrow = Arrow(
            dA_label.get_bottom()+MED_SMALL_BUFF*DOWN, 
            dA_rect.get_center(),
            buff = 0,
            color = WHITE
        )

        difference_in_area = TextMobject(
            "d", "ifference in ", "A", "rea",
            arg_separator = ""
        )
        difference_in_area.set_color_by_tex("d", GREEN)
        difference_in_area.set_color_by_tex("A", GREEN)
        difference_in_area.scale(0.7)
        difference_in_area.next_to(dA_label, UP, MED_SMALL_BUFF, LEFT)

        side_brace = Brace(dA_rect, LEFT, buff = 0)
        graph_label_copy = self.graph_label.copy()

        self.play(
            FadeOut(self.right_point_slider),
            FadeIn(dx_group)
        )
        self.play(Indicate(dx_label))
        self.wait()
        self.play(ShowCreation(dA_arrow))
        self.wait()
        self.play(Write(dA_label, run_time = 2))
        self.wait()
        self.play(
            ReplacementTransform(dA_label[0].copy(), difference_in_area[0]),
            ReplacementTransform(dA_label[1].copy(), difference_in_area[2]),
            *list(map(FadeIn, [difference_in_area[1], difference_in_area[3]]))
        )
        self.wait(2)
        self.play(FadeIn(dA_rect), Animation(dA_arrow))
        self.play(GrowFromCenter(side_brace))
        self.play(
            graph_label_copy.set_color, WHITE,
            graph_label_copy.next_to, side_brace, LEFT, SMALL_BUFF
        )
        self.wait()
        self.play(Indicate(dx_group))
        self.wait()
        self.play(FadeOut(difference_in_area))

        self.dx_group = dx_group
        self.dA_rect = dA_rect
        self.dA_label = dA_label
        self.graph_label_copy = graph_label_copy

    def shrink_dx(self, **kwargs):
        self.transition_to_alt_config(
            deriv_dx = 0.05,
            transformation_kwargs = {"run_time" : 2},
            **kwargs
        )

    def write_dA_dx(self):
        f_tex = self.graph_label_tex
        equation = TexMobject("dA", "\\approx", f_tex, "dx")
        equation.to_edge(RIGHT).shift(3*UP)
        deriv_equation = TexMobject(
            "{dA", "\\over \\,", "dx}", "\\approx", f_tex
        )
        deriv_equation.move_to(equation, UP+LEFT)

        for tex_mob in equation, deriv_equation:
            tex_mob.set_color_by_tex(
                "dA", self.dA_label.get_color()
            )

        dA = VGroup(self.dA_label[0][0], self.dA_label[1][0])
        x_squared = self.graph_label_copy
        dx = self.dx_group[1]

        self.play(*[
            ReplacementTransform(
                mob.copy(),
                equation.get_part_by_tex(tex),
                run_time = 2
            )
            for mob, tex in [(x_squared, f_tex), (dx, "dx"), (dA, "dA")]
        ])
        self.play(Write(equation.get_part_by_tex("approx")))
        self.wait()
        for tex, mob in (f_tex, x_squared), ("dx", dx):
            self.play(*list(map(Indicate, [
                equation.get_part_by_tex(tex),
                mob
            ])))
            self.wait(2)
        self.play(*[
            ReplacementTransform(
                equation.get_part_by_tex(tex),
                deriv_equation.get_part_by_tex(tex),
                run_time = 2,
            )
            for tex in ("dA", "approx", f_tex, "dx")
        ] + [
            Write(deriv_equation.get_part_by_tex("over"))
        ])
        self.wait(2)
        self.shrink_dx(return_to_original_configuration = False)
        self.wait()

        self.deriv_equation = deriv_equation

    def dA_remains_a_mystery(self):
        randy = Randolph(color = BLUE_C)
        randy.to_corner(DOWN+LEFT)
        randy.look_at(self.A_func)

        A_circle, dA_circle = [
            Circle(color = color).replace(
                mob, stretch = True
            ).scale_in_place(1.5)
            for mob, color in [(self.A_func, RED), (self.deriv_equation, GREEN)]
        ]
        q_marks = TexMobject("???")
        q_marks.next_to(A_circle, UP)

        self.play(
            FadeOut(self.integral_words_group),
            FadeIn(randy)
        )
        self.play(
            ShowCreation(A_circle),
            randy.change_mode, "confused"
        )
        self.play(Write(q_marks, run_time = 2))
        self.play(Blink(randy))
        self.wait()
        self.play(
            randy.change_mode, "surprised",
            randy.look_at, dA_circle,
            ReplacementTransform(A_circle, dA_circle)
        )
        self.play(Blink(randy))
        self.wait()
        self.play(*list(map(FadeOut, [randy, q_marks, dA_circle])))

    def write_example_inputs(self):
        d = self.default_right_x
        three = TexMobject("x =", "%d"%d)
        three_plus_dx = TexMobject("x = ", "%d.001"%d)
        labels_lines_vects = list(zip(
            [three, three_plus_dx],
            self.right_v_lines,
            [LEFT, RIGHT]
        ))

        for label, line, vect in labels_lines_vects:
            point = line.get_bottom()
            label.next_to(point, DOWN+vect, MED_SMALL_BUFF)
            label.shift(LARGE_BUFF*vect)
            label.arrow = Arrow(
                label, point,
                buff = SMALL_BUFF,
                color = WHITE,
                tip_length = 0.15
            )
            line_copy = line.copy()
            line_copy.set_color(YELLOW)

            self.play(
                FadeIn(label),
                FadeIn(label.arrow),
                ShowCreation(line_copy)
            )
            self.play(FadeOut(line_copy))
        self.wait()

        self.three = three 
        self.three_plus_dx = three_plus_dx

    def show_dA_dx_in_detail(self):
        d = self.default_right_x
        expression = TexMobject(
            "{A(", "%d.001"%d, ") ", "-A(", "%d"%d, ")", 
            "\\over \\,", "0.001}", 
            "\\approx", "%d"%d, "^2"
        )
        expression.scale(0.9)
        expression.next_to(
            self.deriv_equation, DOWN, MED_LARGE_BUFF
        )
        expression.to_edge(RIGHT)

        self.play(
            ReplacementTransform(
                self.three_plus_dx.get_part_by_tex("%d.001"%d).copy(),
                expression.get_part_by_tex("%d.001"%d)
            ),
            Write(VGroup(
                expression.get_part_by_tex("A("),
                expression.get_part_by_tex(")"),
            )),
        )
        self.wait()
        self.play(
            ReplacementTransform(
                self.three.get_part_by_tex("%d"%d).copy(),
                expression.get_part_by_tex("%d"%d, substring = False)
            ),
            Write(VGroup(
                expression.get_part_by_tex("-A("),
                expression.get_parts_by_tex(")")[1],
            )),
        )
        self.wait(2)
        self.play(
            Write(expression.get_part_by_tex("over")),
            ReplacementTransform(
                expression.get_part_by_tex("%d.001"%d).copy(),
                expression.get_part_by_tex("0.001"),
            )
            
        )
        self.wait()
        self.play(
            Write(expression.get_part_by_tex("approx")),
            ReplacementTransform(
                self.graph_label_copy.copy(),
                VGroup(*expression[-2:]),
                run_time = 2
            )
        )
        self.wait()

    def show_smaller_x(self):
        self.transition_to_alt_config(
            default_right_x = 2,
            deriv_dx = 0.04,
            transformation_kwargs = {"run_time" : 2}
        )

class AlternateAreaUnderCurve(PlayingTowardsDADX):
    CONFIG = {
        "func" : lambda x : (x-2)**3 - 3*(x-2) + 6,
        "graph_label_tex" : "f(x)",
        "deriv_dx" : 0.1,
        "x_max" : 5,
        "x_axis_width" : 11,
        "graph_label_x_val" : 4.5,
    }
    def construct(self):
        #Superclass parts to skip
        self.force_skipping()
        self.setup_axes()
        self.show_graph()
        self.show_area()
        self.ask_about_area()
        self.show_confusion()

        #Superclass parts to show
        self.revert_to_original_skipping_status()
        self.show_variable_endpoint()
        self.name_integral()
        self.nudge_x()
        self.describe_sliver()
        self.write_dA_dx()

        #New animations
        self.approximation_improves_for_smaller_dx()
        self.name_derivative()

    def approximation_improves_for_smaller_dx(self):
        color = YELLOW
        approx = self.deriv_equation.get_part_by_tex("approx")
        dx_to_zero_words = TextMobject(
            "Gets better \\\\ as", 
            "$dx \\to 0$"
        )
        dx_to_zero_words.set_color_by_tex("dx", color)
        dx_to_zero_words.next_to(approx, DOWN, 1.5*LARGE_BUFF)
        arrow = Arrow(dx_to_zero_words, approx, color = color)

        self.play(
            approx.set_color, color,
            ShowCreation(arrow),
            FadeIn(dx_to_zero_words),
        )
        self.wait()
        self.transition_to_alt_config(
            deriv_dx = self.deriv_dx/4.0,
            transformation_kwargs = {"run_time" : 2}
        )

        self.dx_to_zero_words = dx_to_zero_words
        self.dx_to_zero_words_arrow = arrow

    def name_derivative(self):
        deriv_words = TextMobject("``Derivative'' of $A$")
        deriv_words.scale(0.9)
        deriv_words.to_edge(UP+RIGHT)
        moving_group = VGroup(
            self.deriv_equation, 
            self.dx_to_zero_words,
            self.dx_to_zero_words_arrow,
        )
        moving_group.generate_target()
        moving_group.target.next_to(deriv_words, DOWN, LARGE_BUFF)
        moving_group.target.to_edge(RIGHT)

        self.play(
            FadeIn(deriv_words),
            MoveToTarget(moving_group)
        )

        dA_dx = VGroup(*self.deriv_equation[:3])
        box = Rectangle(color = GREEN)
        box.replace(dA_dx, stretch = True)
        box.scale_in_place(1.3)
        brace = Brace(box, UP)
        faders = VGroup(
            self.dx_to_zero_words[0],
            self.dx_to_zero_words_arrow
        )
        dx_to_zero = self.dx_to_zero_words[1]

        self.play(*list(map(FadeIn, [box, brace])))
        self.wait()
        self.play(
            FadeOut(faders),
            dx_to_zero.next_to, box, DOWN
        )
        self.wait()


    ########
    def show_smaller_x(self):
        return

    def shrink_dx(self, **kwargs):
        return

class NextVideoWrapper(Scene):
    def construct(self):
        rect = Rectangle(height = 9, width = 16)
        rect.set_height(1.5*FRAME_Y_RADIUS)
        titles = [
            TextMobject("Chapter %d:"%d, s)
            for d, s in [
                (2, "The paradox of the derivative"),
                (3, "Derivative formulas through geometry"),
            ]
        ]
        for title in titles:
            title.to_edge(UP)
        rect.next_to(VGroup(*titles), DOWN)

        self.add(titles[0])
        self.play(ShowCreation(rect))
        self.wait(3)
        self.play(Transform(*titles))
        self.wait(3)

class ProblemSolvingTool(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            The derivative is a
            problem-solving tool
        """)
        self.wait(3)

class FundamentalTheorem(Scene):
    def construct(self):
        words = TextMobject("""
            Fundamental theorem of calculus
        """)
        words.to_edge(UP)
        arrow = DoubleArrow(LEFT, RIGHT).shift(2*RIGHT)
        deriv = TexMobject(
            "{dA", "\\over \\,", "dx}", "=", "x^2"
        )
        deriv.set_color_by_tex("dA", GREEN)
        deriv.next_to(arrow, RIGHT)

        self.play(ShowCreation(arrow))
        self.wait()
        self.play(Write(deriv))
        self.wait()
        self.play(Write(words))
        self.wait()

class NextVideos(TeacherStudentsScene):
    def construct(self):
        series = VideoSeries()
        series.to_edge(UP)
        this_video = series[0]
        this_video.set_color(YELLOW)

        self.add(series)
        self.teacher_says(
            "That's a high-level view"
        )
        self.wait()
        self.play(
            RemovePiCreatureBubble(
                self.teacher,
                target_mode = "raise_right_hand",
                look_at_arg = this_video,
            ),
            *it.chain(*[
                [pi.change_mode, "pondering", pi.look_at, this_video]
                for pi in self.get_students()
            ])
        )
        self.play(*[
            ApplyMethod(pi.look_at, series)
            for pi in self.get_pi_creatures()
        ])
        self.play(*[
            ApplyMethod(
                video.shift, 0.5*video.get_height()*DOWN,
                run_time = 3,
                rate_func = squish_rate_func(
                    there_and_back, alpha, alpha+0.3
                )
            )
            for video, alpha in zip(series, np.linspace(0, 0.7, len(series)))
        ])
        self.wait()

        student = self.get_students()[1]
        self.remove(student)
        everything = VGroup(*self.get_top_level_mobjects())
        self.add(student)
        words = TextMobject("""
            You could have
            invented this.
        """)
        words.next_to(student, UP, LARGE_BUFF)

        self.play(self.teacher.change_mode, "plain")
        self.play(
            everything.fade, 0.75,
            student.change_mode, "plain"
        )
        self.play(
            Write(words),
            student.look_at, words,
        )
        self.play(
            student.change_mode, "confused",
            student.look_at, words
        )
        self.wait(3)
        self.play(student.change_mode, "thinking")
        self.wait(4)

class Chapter1PatreonThanks(PatreonThanks):
    CONFIG = {
        "specific_patrons" : [
            "Ali Yahya",
            "CrypticSwarm",
            "Juan    Benet",
            "Yu  Jun",
            "Othman  Alikhan",
            "Markus  Persson",
            "Joseph  John Cox",
            "Luc Ritchie",
            "Einar Johansen",
            "Rish    Kundalia",
            "Achille Brighton",
            "Kirk Werklund",
            "Ripta   Pasay",
            "Felipe  Diniz",
        ],
        "patron_scale_val" : 0.9
    }

class EndScreen(PiCreatureScene):
    CONFIG = {
        "seconds_to_blink" : 3,
    }
    def construct(self):
        words = TextMobject("Clicky stuffs")
        words.scale(1.5)
        words.next_to(self.pi_creature, UP)
        words.to_edge(UP)

        self.play(
            FadeIn(
                words, 
                run_time = 2, 
                lag_ratio = 0.5
            ),
            self.pi_creature.change_mode, "hooray"
        )
        self.wait()
        mode_point_pairs = [
            ("raise_left_hand", 5*LEFT+3*UP),
            ("raise_right_hand", 5*RIGHT+3*UP),
            ("thinking", 5*LEFT+2*DOWN),
            ("thinking", 5*RIGHT+2*DOWN),
            ("thinking", 5*RIGHT+2*DOWN),
            ("happy", 5*LEFT+3*UP),
            ("raise_right_hand", 5*RIGHT+3*UP),
        ]
        for mode, point in mode_point_pairs:
            self.play(self.pi_creature.change, mode, point)
            self.wait()
        self.wait(3)


    def create_pi_creature(self):
        self.pi_creature = Randolph()
        self.pi_creature.shift(2*DOWN + 1.5*LEFT)
        return self.pi_creature

class Thumbnail(AlternateAreaUnderCurve):
    CONFIG = {
        "x_axis_label" : "",
        "y_axis_label" : "",
        "graph_origin" : 2.4*DOWN + 3*LEFT,
    }
    def construct(self):
        self.setup_axes()
        self.remove(*self.x_axis.numbers)
        self.remove(*self.y_axis.numbers)
        graph = self.get_graph(self.func)
        rects = self.get_riemann_rectangles(
            graph,
            x_min = 0,
            x_max = 4,
            dx = 0.25,
            start_color = BLUE_E,
        )
        words = TextMobject("""
            Essence of
            calculus
        """)
        words.set_width(9)
        words.to_edge(UP)

        self.add(graph, rects, words)




















