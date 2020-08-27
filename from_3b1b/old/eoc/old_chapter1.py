from manimlib.imports import *


#### Warning, scenes here not updated based on most recent GraphScene changes #######

class CircleScene(PiCreatureScene):
    CONFIG = {
        "radius" : 1.5,
        "stroke_color" : WHITE,
        "fill_color" : BLUE_E,
        "fill_opacity" : 0.5,
        "radial_line_color" : MAROON_B,
        "outer_ring_color" : GREEN_E,
        "dR" : 0.1,
        "dR_color" : YELLOW,
        "unwrapped_tip" : ORIGIN,
        "include_pi_creature" : False,
        "circle_corner" : UP+LEFT
    }
    def setup(self):
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

        self.add(
            self.circle, self.radius_line, 
            self.radius_brace, self.radius_label
        )

        self.pi_creature = self.create_pi_creature()
        if self.include_pi_creature:
            self.add(self.pi_creature)
        else:
            self.pi_creature.set_fill(opacity = 0)

    def create_pi_creature(self):
        return Mortimer().to_corner(DOWN+RIGHT)

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
            path_arc = np.pi/2
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
        result.to_edge(to_edge)

        return result

######################

class PatronsOnly(Scene):
    def construct(self):
        morty = Mortimer()
        morty.shift(2*DOWN)
        title = TextMobject("""
            This is a draft
            for patrons only
        """)
        title.set_color(RED)
        title.scale(2)
        title.to_edge(UP)

        self.add(morty)
        self.play(
            Write(title),
            morty.change_mode, "wave_1"
        )
        self.play(Blink(morty))
        self.play(
            morty.change_mode, "pondering",
            morty.look_at, title
        )
        self.play(Blink(morty))
        self.wait()

class Introduction(TeacherStudentsScene):
    def construct(self):
        self.show_series()
        self.look_to_center()        
        self.go_through_students()
        self.zoom_in_on_first()

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
        self.remove(self.teacher)
        self.teacher.change_mode("happy")
        self.add(self.teacher)
        self.play(
            FadeIn(
                series,
                lag_ratio = 0.5,
                run_time = 2
            ),
            Blink(self.get_teacher())
        )
        self.teacher_says(words, target_mode = "hooray")
        self.play(
            ApplyMethod(this_video.restore, run_time = 3),
            *[
                ApplyFunction(
                    lambda p : p.change_mode("hooray").look_at(series[1]),
                    pi
                )
                for pi in self.get_pi_creatures()
            ]
        )
        def homotopy(x, y, z, t):
            alpha = (0.7*x + FRAME_X_RADIUS)/(FRAME_WIDTH)
            beta = squish_rate_func(smooth, alpha-0.15, alpha+0.15)(t)
            return (x, y - 0.3*np.sin(np.pi*beta), z)
        self.play(
            Homotopy(
                homotopy, series, 
                apply_function_kwargs = {"maintain_smoothness" : False},
            ),
            *[
                ApplyMethod(pi.look_at, series[-1])
                for pi in self.get_pi_creatures()
            ],
            run_time = 5
        )
        self.play(
            FadeOut(self.teacher.bubble),
            FadeOut(self.teacher.bubble.content),
            *[
                ApplyMethod(pi.change_mode, "happy")
                for pi in self.get_pi_creatures()
            ]
        )

    def look_to_center(self):
        anims = []
        for pi in self.get_pi_creatures():
            anims += [
                pi.change_mode, "pondering",
                pi.look_at, 2*UP
            ]
        self.play(*anims)
        self.random_blink(6)
        self.play(*[
            ApplyMethod(pi.change_mode, "happy")
            for pi in self.get_pi_creatures()
        ])

    def go_through_students(self):
        pi1, pi2, pi3 = self.get_students()
        for pi in pi1, pi2, pi3:
            pi.save_state()
        bubble = pi1.get_bubble(width = 5)
        bubble.set_fill(BLACK, opacity = 1)
        remembered_symbols = VGroup(
            TexMobject("\\int_0^1 \\frac{1}{1-x^2}\\,dx").shift(UP+LEFT),
            TexMobject("\\frac{d}{dx} e^x = e^x").shift(DOWN+RIGHT),
        )
        cant_wait = TextMobject("I literally \\\\ can't wait")
        big_derivative = TexMobject("""
            \\frac{d}{dx} \\left( \\sin(x^2)2^{\\sqrt{x}} \\right)
        """)

        self.play(
            pi1.change_mode, "confused",
            pi1.look_at, bubble.get_right(),
            ShowCreation(bubble),
            pi2.fade,
            pi3.fade,
        )
        bubble.add_content(remembered_symbols)
        self.play(Write(remembered_symbols))
        self.play(ApplyMethod(
            remembered_symbols.fade, 0.7,
            lag_ratio = 0.5,
            run_time = 3
        ))
        self.play(
            pi1.restore,
            pi1.fade,
            pi2.restore,
            pi2.change_mode, "hooray",
            pi2.look_at, bubble.get_right(),
            bubble.pin_to, pi2,
            FadeOut(remembered_symbols),
        )
        bubble.add_content(cant_wait)
        self.play(Write(cant_wait, run_time = 2))
        self.play(Blink(pi2))
        self.play(
            pi2.restore,
            pi2.fade,
            pi3.restore,
            pi3.change_mode, "pleading",
            pi3.look_at, bubble.get_right(),
            bubble.pin_to, pi3,
            FadeOut(cant_wait)
        )
        bubble.add_content(big_derivative)
        self.play(Write(big_derivative))
        self.play(Blink(pi3))
        self.wait()

    def zoom_in_on_first(self):
        this_video = self.this_video
        self.remove(this_video)
        this_video.generate_target()
        this_video.target.set_height(FRAME_HEIGHT)
        this_video.target.center()        
        this_video.target.set_fill(opacity = 0)

        everything = VGroup(*self.get_mobjects())
        self.play(
            FadeOut(everything),
            MoveToTarget(this_video, run_time = 2)
        )

class IntroduceCircle(Scene):
    def construct(self):
        circle = Circle(radius = 3, color = WHITE)
        circle.to_edge(LEFT)
        radius = Line(circle.get_center(), circle.get_right())
        radius.set_color(MAROON_B)
        R = TexMobject("R").next_to(radius, UP)

        area, circumference = words = VGroup(*list(map(TextMobject, [
            "Area =", "Circumference ="
        ])))
        area.set_color(BLUE)
        circumference.set_color(YELLOW)

        words.arrange(DOWN, aligned_edge = LEFT)
        words.next_to(circle, RIGHT)
        words.to_edge(UP)
        pi_R, pre_squared = TexMobject("\\pi R", "{}^2")
        squared = TexMobject("2").replace(pre_squared)
        area_form = VGroup(pi_R, squared)
        area_form.next_to(area, RIGHT)
        two, pi_R = TexMobject("2", "\\pi R")
        circum_form = VGroup(pi_R, two)
        circum_form.next_to(circumference, RIGHT)

        derivative = TexMobject(
            "\\frac{d}{dR}", "\\pi R^2", "=", "2\\pi R"
        )
        integral = TexMobject(
            "\\int_0^R", "2\\pi r", "\\, dR = ", "\\pi R^2"
        )
        up_down_arrow = TexMobject("\\Updownarrow")
        calc_stuffs = VGroup(derivative, up_down_arrow, integral)
        calc_stuffs.arrange(DOWN)
        calc_stuffs.next_to(words, DOWN, buff = LARGE_BUFF, aligned_edge = LEFT)

        brace = Brace(calc_stuffs, RIGHT)
        to_be_explained = brace.get_text("To be \\\\ explained")
        VGroup(brace, to_be_explained).set_color(GREEN)

        self.play(ShowCreation(radius), Write(R))
        self.play(
            Rotate(radius, 2*np.pi, about_point = circle.get_center()),
            ShowCreation(circle)
        )
        self.play(
            FadeIn(area),
            Write(area_form),
            circle.set_fill, area.get_color(), 0.5,
            Animation(radius),
            Animation(R),
        )
        self.wait()
        self.play(
            circle.set_stroke, circumference.get_color(),
            FadeIn(circumference),
            Animation(radius),
            Animation(R),
        )
        self.play(Transform(
            area_form.copy(),
            circum_form,
            path_arc = -np.pi/2,
            run_time = 3
        ))
        self.wait()
        self.play(
            area_form.copy().replace, derivative[1],
            circum_form.copy().replace, derivative[3],
            Write(derivative[0]),
            Write(derivative[2]),
            run_time = 1
        )
        self.wait()
        self.play(
            area_form.copy().replace, integral[3],
            Transform(circum_form.copy(), integral[1]),
            Write(integral[0]),
            Write(integral[2]),
            run_time = 1
        )
        self.wait()
        self.play(Write(up_down_arrow))
        self.wait()
        self.play(
            GrowFromCenter(brace),
            Write(to_be_explained)
        )
        self.wait()

class HeartOfCalculus(GraphScene):
    CONFIG = {
        "x_labeled_nums" : [],
        "y_labeled_nums" : [],
    }
    def construct(self):
        self.setup_axes()
        self.graph_function(lambda x : 3*np.sin(x/2) + x)
        rect_sets = [
            self.get_riemann_rectangles(
                0, self.x_max, 1./(2**n), stroke_width = 1./(n+1)
            )
            for n in range(6)
        ]

        rects = rect_sets.pop(0)
        rects.save_state()
        rects.stretch_to_fit_height(0)
        rects.shift(
            (self.graph_origin[1] - rects.get_center()[1])*UP
        )
        self.play(
            rects.restore,
            lag_ratio = 0.5,
            run_time = 3
        )
        while rect_sets:
            self.play(
                Transform(rects, rect_sets.pop(0)),
                run_time = 2
            )

class PragmatismToArt(Scene):
    def construct(self):
        morty = Mortimer()
        morty.to_corner(DOWN+RIGHT)
        morty.shift(LEFT)
        pragmatism = TextMobject("Pragmatism")
        art = TextMobject("Art")
        pragmatism.move_to(morty.get_corner(UP+LEFT), aligned_edge = DOWN)
        art.move_to(morty.get_corner(UP+RIGHT), aligned_edge = DOWN)
        art.shift(0.2*(LEFT+UP))

        circle1 = Circle(
            radius = 2,
            fill_opacity = 1,
            fill_color = BLUE_E,            
            stroke_width = 0,
        )
        circle2 = Circle(
            radius = 2,
            stroke_color = YELLOW
        )
        arrow = DoubleArrow(LEFT, RIGHT, color = WHITE)
        circle_group = VGroup(circle1, arrow, circle2)
        circle_group.arrange()
        circle_group.to_corner(UP+LEFT)
        circle2.save_state()
        circle2.move_to(circle1)
        q_marks = TextMobject("???").next_to(arrow, UP)


        self.play(
            morty.change_mode, "raise_right_hand",
            morty.look_at, pragmatism,
            Write(pragmatism, run_time = 1),
        )
        self.play(Blink(morty))
        self.play(
            morty.change_mode, "raise_left_hand",
            morty.look_at, art,
            Transform(
                VectorizedPoint(morty.get_corner(UP+RIGHT)),
                art
            ),
            pragmatism.fade, 0.7,
            pragmatism.rotate_in_place, np.pi/4,
            pragmatism.shift, DOWN+LEFT
        )
        self.play(Blink(morty))
        self.play(
            GrowFromCenter(circle1),
            morty.look_at, circle1
        )
        self.play(ShowCreation(circle2))
        self.play(
            ShowCreation(arrow),
            Write(q_marks),
            circle2.restore
        )
        self.play(Blink(morty))

class IntroduceTinyChangeInArea(CircleScene):
    CONFIG = {
        "include_pi_creature" : True,
    }
    def construct(self):
        new_area_form, minus, area_form = expression = TexMobject(
            "\\pi (R + 0.1)^2", "-", "\\pi R^2"
        )
        VGroup(*new_area_form[4:7]).set_color(self.dR_color)
        expression_brace = Brace(expression, UP)
        change_in_area = expression_brace.get_text("Change in area")
        change_in_area.set_color(self.outer_ring_color)
        area_brace = Brace(area_form)
        area_word = area_brace.get_text("Area")
        area_word.set_color(BLUE)
        new_area_brace = Brace(new_area_form)
        new_area_word = new_area_brace.get_text("New area")
        group = VGroup(
            expression, expression_brace, change_in_area,
            area_brace, area_word, new_area_brace, new_area_word
        )
        group.to_edge(UP).shift(RIGHT)
        group.save_state()
        area_group = VGroup(area_form, area_brace, area_word)
        area_group.save_state()
        area_group.next_to(self.circle, RIGHT, buff = LARGE_BUFF)

        self.introduce_circle(
            added_anims = [self.pi_creature.change_mode, "speaking"]
        )
        self.play(Write(area_group))
        self.change_mode("happy")
        outer_ring = self.increase_radius()
        self.wait()
        self.play(
            area_group.restore,            
            GrowFromCenter(expression_brace),
            Write(new_area_form), 
            Write(minus), 
            Write(change_in_area),
            self.pi_creature.change_mode, "confused",
        )
        self.play(
            Write(new_area_word),
            GrowFromCenter(new_area_brace)
        )
        self.wait(2)
        self.play(
            group.fade, 0.7,
            self.pi_creature.change_mode, "happy"
        )
        self.wait()
        self.play(
            outer_ring.set_color, YELLOW,
            Animation(self.nudge_arrow),
            Animation(self.nudge_line),
            rate_func = there_and_back
        )
        self.show_unwrapping(outer_ring)
        self.play(group.restore)
        self.work_out_expression(group)
        self.second_unwrapping(outer_ring)
        insignificant = TextMobject("Insignificant")
        insignificant.set_color(self.dR_color)
        insignificant.move_to(self.error_words)
        self.play(Transform(self.error_words, insignificant))
        self.wait()

        big_rect = Rectangle(
            width = FRAME_WIDTH,
            height = FRAME_HEIGHT,
            fill_color = BLACK, 
            fill_opacity = 0.85,
            stroke_width = 0,
        )
        self.play(
            FadeIn(big_rect),
            area_form.set_color, BLUE,
            self.two_pi_R.set_color, GREEN,
            self.pi_creature.change_mode, "happy"
        )

    def show_unwrapping(self, outer_ring):
        almost_rect = outer_ring.copy()        
        self.unwrap_ring(
            almost_rect,
            added_anims = [self.pi_creature.change_mode, "pondering"]
        )

        circum_brace = Brace(almost_rect, UP).scale_in_place(0.95)
        dR_brace = TexMobject("\\}")
        dR_brace.stretch(0.5, 1)
        dR_brace.next_to(almost_rect, RIGHT)
        two_pi_R = circum_brace.get_text("$2\\pi R$")
        dR = TexMobject("$0.1$").scale(0.7).next_to(dR_brace, RIGHT)
        dR.set_color(self.dR_color)

        two_pi_R.generate_target()
        dR.generate_target()
        lp, rp = TexMobject("()")
        change_in_area = TextMobject(
            "Change in area $\\approx$"
        )
        final_area = VGroup(
            change_in_area,
            two_pi_R.target, lp, dR.target.scale(1./0.7), rp
        )
        final_area.arrange(RIGHT, buff = SMALL_BUFF)
        final_area.next_to(almost_rect, DOWN, buff = MED_LARGE_BUFF)
        final_area.set_color(GREEN_A)
        final_area[3].set_color(self.dR_color)
        change_in_area.shift(0.1*LEFT)

        self.play(
            GrowFromCenter(circum_brace),
            Write(two_pi_R)
        )
        self.wait()
        self.play(
            GrowFromCenter(dR_brace),
            Write(dR)
        )
        self.wait()
        self.play(
            MoveToTarget(two_pi_R.copy()),
            MoveToTarget(dR.copy()),
            Write(change_in_area, run_time = 1),
            Write(lp),
            Write(rp),
        )
        self.remove(*self.get_mobjects_from_last_animation())
        self.add(final_area)
        self.play(
            self.pi_creature.change_mode, "happy",
            self.pi_creature.look_at, final_area
        )
        self.wait()
        group = VGroup(
            almost_rect, final_area, two_pi_R, dR,
            circum_brace, dR_brace
        )
        self.play(group.fade)

    def work_out_expression(self, expression_group):
        exp, exp_brace, title, area_brace, area_word, new_area_brace, new_area_word = expression_group
        new_area_form, minus, area_form = exp

        expanded = TexMobject(
            "\\pi R^2", "+", "2\\pi R (0.1)", 
            "+", "\\pi (0.1)^2", "-", "\\pi R^2",
        )
        pi_R_squared, plus, two_pi_R_dR, plus2, pi_dR_squared, minus2, pi_R_squared2 = expanded
        for subset in two_pi_R_dR[4:7], pi_dR_squared[2:5]:
            VGroup(*subset).set_color(self.dR_color)
        expanded.next_to(new_area_form, DOWN, aligned_edge = LEFT, buff = MED_SMALL_BUFF)
        expanded.shift(LEFT/2.)

        faders = [area_brace, area_word, new_area_brace, new_area_word]
        self.play(*list(map(FadeOut, faders)))
        trips = [
            ([0, 2, 8], pi_R_squared, plus),
            ([8, 0, 2, 1, 4, 5, 6, 7], two_pi_R_dR, plus2),
            ([0, 1, 4, 5, 6, 7, 8], pi_dR_squared, VGroup()),
        ]
        to_remove = []
        for subset, target, writer in trips:
            starter = VGroup(
                *np.array(list(new_area_form.copy()))[subset]
            )
            self.play(
                Transform(starter, target, run_time = 2),
                Write(writer)
            )
            to_remove += self.get_mobjects_from_last_animation()
            self.wait()
        self.play(
            Transform(minus.copy(), minus2),
            Transform(area_form.copy(), pi_R_squared2),
        )
        to_remove += self.get_mobjects_from_last_animation()
        self.remove(*to_remove)
        self.add(self.pi_creature, *expanded)
        self.wait(2)
        self.play(*[
            ApplyMethod(mob.set_color, RED)
            for mob in (pi_R_squared, pi_R_squared2)
        ])
        self.wait()
        self.play(*[
            ApplyMethod(mob.fade, 0.7)
            for mob in (plus, pi_R_squared, pi_R_squared2, minus2)
        ]) 
        self.wait()

        approx_brace = Brace(two_pi_R_dR)
        error_brace = Brace(pi_dR_squared, buff = SMALL_BUFF)
        error_words = error_brace.get_text("Error", buff = SMALL_BUFF)
        error_words.set_color(RED)
        self.error_words = error_words

        self.play(
            GrowFromCenter(approx_brace),
            self.pi_creature.change_mode, "hooray"
        )
        self.wait()
        self.play(
            GrowFromCenter(error_brace),
            Write(error_words),
            self.pi_creature.change_mode, "confused"
        )
        self.wait()
        self.two_pi_R = VGroup(*two_pi_R_dR[:3])

    def second_unwrapping(self, outer_ring):
        almost_rect = outer_ring.copy()
        rect = Rectangle(
            width = 2*np.pi*self.radius,
            height = self.dR,
            fill_color = self.outer_ring_color,
            fill_opacity = 1,
            stroke_width = 0,
        )
        self.play(
            almost_rect.set_color, YELLOW,
            self.pi_creature.change_mode, "pondering"
        )
        self.unwrap_ring(almost_rect)
        self.wait()
        rect.move_to(almost_rect)
        self.play(FadeIn(rect))
        self.wait()

    def create_pi_creature(self):
        morty = Mortimer()
        morty.scale(0.7)
        morty.to_corner(DOWN+RIGHT)
        return morty

class CleanUpABit(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            Let's clean that
            up a bit
        """)
        self.random_blink(2)

class BuildToDADR(CircleScene):
    CONFIG = {
        "include_pi_creature" : True,
    }
    def construct(self):
        self.outer_ring = self.increase_radius()
        self.write_initial_terms()
        self.show_fractions()
        self.transition_to_dR()
        self.elaborate_on_d()
        self.not_infinitely_small()

    def create_pi_creature(self):
        morty = Mortimer()
        morty.flip()
        morty.to_corner(DOWN+LEFT)
        return morty

    def write_initial_terms(self):
        change = TextMobject("Change in area")
        change.set_color(GREEN_B)
        equals, two_pi_R, dR, plus, pi, dR2, squared = rhs = TexMobject(
            "=", "2 \\pi R", "(0.1)", "+", "\\pi", "(0.1)", "^2"
        )
        VGroup(dR, dR2).set_color(self.dR_color)
        change.next_to(self.circle, buff = LARGE_BUFF)
        rhs.next_to(change)

        circum_brace = Brace(two_pi_R, UP)
        circum_text = circum_brace.get_text("Circumference")
        error_brace = Brace(VGroup(pi, squared), UP)
        error_text = error_brace.get_text("Error")
        error_text.set_color(RED)

        self.play(
            Write(change, run_time = 1),
            self.pi_creature.change_mode, "pondering",
        )
        self.wait()
        self.play(*it.chain(
            list(map(Write, [equals, two_pi_R, dR])),
            list(map(FadeIn, [circum_text, circum_brace]))
        ))
        self.wait()
        self.play(*it.chain(
            list(map(Write, [plus, pi, dR2, squared])),
            list(map(FadeIn, [error_brace, error_text]))
        ))
        self.wait(2)
        self.change = change
        self.circum_term = VGroup(two_pi_R, dR)
        self.circum_term.label = VGroup(circum_brace, circum_text)
        self.error_term = VGroup(pi, dR2, squared)
        self.error_term.label = VGroup(error_brace, error_text)        
        self.equals = equals
        self.plus = plus

    def show_fractions(self):
        terms = [self.change, self.circum_term, self.error_term]
        for term in terms:
            term.frac_line = TexMobject("\\frac{\\quad}{\\quad}")
            term.frac_line.stretch_to_fit_width(term.get_width())
            term.frac_line.next_to(term, DOWN, buff = SMALL_BUFF)
            term.denom = TexMobject("(0.1)")
            term.denom.next_to(term.frac_line, DOWN, buff = SMALL_BUFF)
            term.denom.set_color(self.dR_color)
            term.denom.save_state()
            term.denom.replace(self.nudge_label)

        self.equals.generate_target()
        self.equals.target.next_to(self.change.frac_line, RIGHT)
        self.plus.generate_target()
        self.plus.target.next_to(self.circum_term.frac_line, RIGHT)

        self.play(*it.chain(
            [Write(term.frac_line) for term in terms],
            list(map(MoveToTarget, [self.equals, self.plus]))
        ))
        self.play(*[term.denom.restore for term in terms])
        self.wait(2)
        self.play(
            self.outer_ring.set_color, YELLOW,
            rate_func = there_and_back
        )
        self.play(
            self.nudge_label.scale_in_place, 2,
            rate_func = there_and_back
        )
        self.wait(2)
        canceleres = VGroup(self.circum_term[1], self.circum_term.denom)
        self.play(canceleres.set_color, RED)
        self.play(FadeOut(canceleres))
        self.remove(self.circum_term)
        self.play(
            self.circum_term[0].move_to, self.circum_term.frac_line, LEFT,
            self.circum_term[0].shift, 0.1*UP,
            FadeOut(self.circum_term.frac_line),
            MaintainPositionRelativeTo(
                self.circum_term.label,
                self.circum_term[0]
            )
        )
        self.circum_term = self.circum_term[0]
        self.wait(2)
        self.play(
            FadeOut(self.error_term[-1]),
            FadeOut(self.error_term.denom)
        )
        self.error_term.remove(self.error_term[-1])
        self.play(
            self.error_term.move_to, self.error_term.frac_line,
            self.error_term.shift, 0.3*LEFT + 0.15*UP,
            FadeOut(self.error_term.frac_line),
            self.plus.shift, 0.7*LEFT + 0.1*UP,
            MaintainPositionRelativeTo(
                self.error_term.label,
                self.error_term
            )
        )
        self.wait()

    def transition_to_dR(self):
        dRs = VGroup(
            self.nudge_label, 
            self.change.denom,
            self.error_term[1],
        )
        error_brace, error_text = self.error_term.label
        for s, width in ("(0.01)", 0.05), ("(0.001)", 0.03), ("dR", 0.03):
            new_dRs = VGroup(*[
                TexMobject(s).move_to(mob, LEFT)
                for mob in dRs
            ])
            new_dRs.set_color(self.dR_color)
            new_outer_ring = self.get_ring(self.radius, width)
            new_nudge_line = self.nudge_line.copy()
            new_nudge_line.set_width(width)
            new_nudge_line.move_to(self.nudge_line, LEFT)
            error_brace.target = error_brace.copy()
            error_brace.target.stretch_to_fit_width(
                VGroup(self.error_term[0], new_dRs[-1]).get_width()
            )
            error_brace.target.move_to(error_brace, LEFT)
            self.play(
                MoveToTarget(error_brace),
                Transform(self.outer_ring, new_outer_ring),
                Transform(self.nudge_line, new_nudge_line),
                *[
                    Transform(*pair)
                    for pair in zip(dRs, new_dRs)
                ]
            )
            self.wait()
            if s == "(0.001)":
                self.plus.generate_target()
                self.plus.target.next_to(self.circum_term)
                self.error_term.generate_target()
                self.error_term.target.next_to(self.plus.target)
                error_brace.target = Brace(self.error_term.target)
                error_text.target = error_brace.target.get_text("Truly tiny")
                error_text.target.set_color(error_text.get_color())
                self.play(*list(map(MoveToTarget, [
                    error_brace, error_text, self.plus, self.error_term
                ])))
                self.wait()

        difference_text = TextMobject(
            "``Tiny " , "d", "ifference in ", "$R$", "''",
            arg_separator = ""

        )
        difference_text.set_color_by_tex("d", self.dR_color)
        difference_text.next_to(self.pi_creature, UP+RIGHT)
        difference_arrow = Arrow(difference_text, self.change.denom)
        self.play(
            Write(difference_text, run_time = 2),
            ShowCreation(difference_arrow),
            self.pi_creature.change_mode, "speaking"
        )
        self.wait()

        dA = TexMobject("dA")
        dA.set_color(self.change.get_color())
        frac_line = self.change.frac_line
        frac_line.generate_target()
        frac_line.target.stretch_to_fit_width(dA.get_width())
        frac_line.target.next_to(self.equals, LEFT)
        dA.next_to(frac_line.target, UP, 2*SMALL_BUFF)
        self.change.denom.generate_target()
        self.change.denom.target.next_to(frac_line.target, DOWN, 2*SMALL_BUFF)
        A = TexMobject("A").replace(difference_text[3])
        difference_arrow.target = Arrow(difference_text, dA.get_left())
        self.play(
            Transform(self.change, dA),
            MoveToTarget(frac_line),
            MoveToTarget(self.change.denom),
            Transform(difference_text[3], A),
            difference_text[1].set_color, dA.get_color(),
            MoveToTarget(difference_arrow),
        )
        self.wait(2)
        self.play(*list(map(FadeOut, [difference_text, difference_arrow])))

    def elaborate_on_d(self):
        arc = Arc(-np.pi, start_angle = -np.pi/2)
        arc.set_height(
            self.change.get_center()[1]-self.change.denom.get_center()[1]
        )
        arc.next_to(self.change.frac_line, LEFT)
        arc.add_tip()

        self.play(
            ShowCreation(arc),
            self.pi_creature.change_mode, "sassy"
        )
        self.wait()
        self.play(self.pi_creature.shrug)
        self.play(FadeOut(arc))
        self.wait()

        d = TextMobject("``$d$''")
        arrow = TexMobject("\\Rightarrow")
        arrow.next_to(d)
        ignore_error = TextMobject("Ignore error")
        d_group = VGroup(d, arrow, ignore_error)
        d_group.arrange()
        d_group.next_to(
            self.pi_creature.get_corner(UP+RIGHT), 
            buff = LARGE_BUFF
        )
        error_group = VGroup(
            self.plus, self.error_term, self.error_term.label
        )

        self.play(
            Write(d),
            self.pi_creature.change_mode, "speaking"
        )
        self.play(*list(map(Write, [arrow, ignore_error])))
        self.play(error_group.fade, 0.8)
        self.wait(2)
        equality_brace = Brace(VGroup(self.change.denom, self.circum_term))
        equal_word = equality_brace.get_text("Equality")
        VGroup(equality_brace, equal_word).set_color(BLUE)
        self.play(
            GrowFromCenter(equality_brace),
            Write(equal_word, run_time = 1)
        )
        self.wait(2)
        self.play(*list(map(FadeOut, [equality_brace, equal_word])))

        less_wrong_philosophy = TextMobject("``Less wrong'' philosophy")
        less_wrong_philosophy.move_to(ignore_error, LEFT)
        self.play(Transform(ignore_error, less_wrong_philosophy))
        self.wait()

        big_dR = 0.3
        big_outer_ring = self.get_ring(self.radius, big_dR)
        big_nudge_line = self.nudge_line.copy()
        big_nudge_line.stretch_to_fit_width(big_dR)
        big_nudge_line.move_to(self.nudge_line, LEFT)
        new_nudge_arrow = Arrow(self.nudge_label, big_nudge_line, buff = SMALL_BUFF)
        self.outer_ring.save_state()
        self.nudge_line.save_state()
        self.nudge_arrow.save_state()
        self.play(
            Transform(self.outer_ring, big_outer_ring),
            Transform(self.nudge_line, big_nudge_line),
            Transform(self.nudge_arrow, new_nudge_arrow),
        )
        self.play(
            *[
                mob.restore 
                for mob in [
                    self.outer_ring,
                    self.nudge_line,
                    self.nudge_arrow,
                ]
            ],
            rate_func=linear,
            run_time = 7
        )
        self.play(self.pi_creature.change_mode, "hooray")
        self.less_wrong_philosophy = VGroup(
            d, arrow, ignore_error
        )

    def not_infinitely_small(self):
        randy = Randolph().flip()
        randy.scale(0.7)
        randy.to_corner(DOWN+RIGHT)
        bubble = SpeechBubble()
        bubble.write("$dR$ is infinitely small")
        bubble.resize_to_content()
        bubble.stretch(0.7, 1)
        bubble.pin_to(randy)
        bubble.set_fill(BLACK, opacity = 1)
        bubble.add_content(bubble.content)
        self.play(FadeIn(randy))
        self.play(
            randy.change_mode, "speaking",
            ShowCreation(bubble),
            Write(bubble.content),
            self.pi_creature.change_mode, "confused"
        )
        self.wait()

        to_infs = [self.change, self.change.denom, self.nudge_label]
        for mob in to_infs:
            mob.save_state()
            mob.inf = TexMobject("1/\\infty")
            mob.inf.set_color(mob.get_color())
            mob.inf.move_to(mob)
        self.play(*[
            Transform(mob, mob.inf)
            for mob in to_infs
        ])
        self.wait()
        self.play(self.pi_creature.change_mode, "pleading")
        self.wait()
        self.play(*it.chain(
            [mob.restore for mob in to_infs],
            list(map(FadeOut, [bubble, bubble.content])),
            [randy.change_mode, "erm"],
            [self.pi_creature.change_mode, "happy"],
        ))
        for n in range(7):
            target = TexMobject("0.%s1"%("0"*n))
            target.set_color(self.nudge_label.get_color())
            target.move_to(self.nudge_label, LEFT)
            self.outer_ring.target = self.get_ring(self.radius, 0.1/(n+1))
            self.nudge_line.get_center = self.nudge_line.get_left
            self.play(
                Transform(self.nudge_label, target),
                MoveToTarget(self.outer_ring),
                self.nudge_line.stretch_to_fit_width, 0.1/(n+1)
            )
        self.wait()
        bubble.write("Wrong!")
        bubble.resize_to_content()
        bubble.stretch(0.7, 1)
        bubble.pin_to(randy)
        bubble.add_content(bubble.content)
        self.play(
            FadeIn(bubble),
            Write(bubble.content, run_time = 1),
            randy.change_mode, "angry",
        )
        self.play(randy.set_color, RED)
        self.play(self.pi_creature.change_mode, "guilty")
        self.wait()

        new_bubble = self.pi_creature.get_bubble(SpeechBubble)
        new_bubble.set_fill(BLACK, opacity = 0.8)
        new_bubble.write("But it gets \\\\ less wrong!")
        new_bubble.resize_to_content()
        new_bubble.pin_to(self.pi_creature)

        self.play(
            FadeOut(bubble),
            FadeOut(bubble.content),
            ShowCreation(new_bubble),
            Write(new_bubble.content),
            randy.change_mode, "erm",
            randy.set_color, BLUE_E,
            self.pi_creature.change_mode, "shruggie"
        )
        self.wait(2)

class NameDerivative(IntroduceTinyChangeInArea):
    def construct(self):
        self.increase_radius(run_time = 0)
        self.change_nudge_label()
        self.name_derivative_for_cricle()
        self.interpret_geometrically()
        self.show_limiting_process()
        self.reference_approximation()
        self.emphasize_equality()

    def change_nudge_label(self):
        new_label = TexMobject("dR")
        new_label.move_to(self.nudge_label)
        new_label.to_edge(UP)        
        new_label.set_color(self.nudge_label.get_color())
        new_arrow = Arrow(new_label, self.nudge_line)

        self.remove(self.nudge_label, self.nudge_arrow)
        self.nudge_label = new_label
        self.nudge_arrow = new_arrow
        self.add(self.nudge_label, self.nudge_arrow)
        self.wait()

    def name_derivative_for_cricle(self):
        dA_dR, equals, d_formula_dR, equals2, two_pi_R = dArea_fom = TexMobject(
            "\\frac{dA}{dR}", 
            "=", "\\frac{d(\\pi R^2)}{dR}",
            "=", "2\\pi R"
        )
        dArea_fom.to_edge(UP, buff = MED_LARGE_BUFF).shift(RIGHT)
        dA, frac_line, dR = VGroup(*dA_dR[:2]), dA_dR[2], VGroup(*dA_dR[3:])
        dA.set_color(GREEN_B)
        dR.set_color(self.dR_color)
        VGroup(*d_formula_dR[7:]).set_color(self.dR_color)


        dA_dR_circle = Circle()
        dA_dR_circle.replace(dA_dR, stretch = True)
        dA_dR_circle.scale_in_place(1.5)
        dA_dR_circle.set_color(BLUE)

        words = TextMobject(
            "``Derivative'' of $A$\\\\",
            "with respect to $R$"
        )
        words.next_to(dA_dR_circle, DOWN, buff = 1.5*LARGE_BUFF)
        words.shift(0.5*LEFT)
        arrow = Arrow(words, dA_dR_circle)
        arrow.set_color(dA_dR_circle.get_color())

        self.play(Transform(self.outer_ring.copy(), dA, run_time = 2))
        self.play(
            Transform(self.nudge_line.copy(), dR, run_time = 2),
            Write(frac_line)
        )
        self.wait()
        self.play(
            ShowCreation(dA_dR_circle),
            ShowCreation(arrow),
            Write(words)
        )
        self.wait()
        self.play(Write(VGroup(equals, d_formula_dR)))
        self.wait()
        self.play(Write(VGroup(equals2, two_pi_R)))
        self.wait()
        self.dArea_fom = dArea_fom
        self.words = words
        self.two_pi_R = two_pi_R

    def interpret_geometrically(self):
        target_formula = TexMobject(
            "\\frac{d \\quad}{dR} = "
        )
        VGroup(*target_formula[2:4]).set_color(self.dR_color)
        target_formula.scale(1.3)
        target_formula.next_to(self.dArea_fom, DOWN)
        target_formula.shift(2*RIGHT + 0.5*DOWN)

        area_form = VGroup(*self.dArea_fom[2][2:5]).copy()
        area_form.set_color(BLUE_D)
        circum_form = self.dArea_fom[-1]

        circle_width = 1
        area_circle = self.circle.copy()
        area_circle.set_stroke(width = 0)
        area_circle.generate_target()
        area_circle.target.set_width(circle_width)
        area_circle.target.next_to(target_formula[0], RIGHT, buff = 0)
        area_circle.target.set_color(BLUE_D)
        circum_circle = self.circle.copy()
        circum_circle.set_fill(opacity = 0)
        circum_circle.generate_target()
        circum_circle.target.set_width(circle_width)
        circum_circle.target.next_to(target_formula)

        self.play(
            Write(target_formula),
            MoveToTarget(area_circle),
            MoveToTarget(
                circum_circle,
                run_time = 2,
                rate_func = squish_rate_func(smooth, 0.5, 1)
            ),
            self.pi_creature.change_mode, "hooray"
        )
        self.wait()
        self.play(Transform(area_circle.copy(), area_form))
        self.remove(area_form)
        self.play(Transform(circum_circle.copy(), circum_form))
        self.change_mode("happy")

    def show_limiting_process(self):
        big_dR = 0.3
        small_dR = 0.01
        big_ring = self.get_ring(self.radius, big_dR)
        small_ring = self.get_ring(self.radius, small_dR)
        big_nudge_line = self.nudge_line.copy().set_width(big_dR)
        small_nudge_line = self.nudge_line.copy().set_width(small_dR)
        for line in big_nudge_line, small_nudge_line:
            line.move_to(self.nudge_line, LEFT)
        new_nudge_arrow = Arrow(self.nudge_label, big_nudge_line)
        small_nudge_arrow = Arrow(self.nudge_label, small_nudge_line)

        ring_group = VGroup(self.outer_ring, self.nudge_line, self.nudge_arrow)
        ring_group.save_state()
        big_group = VGroup(big_ring, big_nudge_line, new_nudge_arrow)
        small_group = VGroup(small_ring, small_nudge_line, small_nudge_arrow)

        fracs = VGroup()
        sample_dRs = [0.3, 0.1, 0.01]
        for dR in sample_dRs:
            dA = 2*np.pi*dR + np.pi*(dR**2)
            frac = TexMobject("\\frac{%.3f}{%.2f}"%(dA, dR))
            VGroup(*frac[:5]).set_color(self.outer_ring.get_color())
            VGroup(*frac[6:]).set_color(self.dR_color)
            fracs.add(frac)
        fracs.add(TexMobject("\\cdots \\rightarrow"))
        fracs.add(TexMobject("???"))
        fracs[-1].set_color_by_gradient(self.dR_color, self.outer_ring.get_color())
        fracs.arrange(RIGHT, buff = MED_LARGE_BUFF)
        fracs.to_corner(DOWN+LEFT)

        arrows = VGroup()
        for frac in fracs[:len(sample_dRs)] + [fracs[-1]]:
            arrow = Arrow(self.words.get_bottom(), frac.get_top())
            arrow.set_color(WHITE)
            if frac is fracs[-1]:
                check = TexMobject("\\checkmark")
                check.set_color(GREEN)
                check.next_to(arrow.get_center(), UP+RIGHT, SMALL_BUFF)
                arrow.add(check)
            else:
                cross = TexMobject("\\times")
                cross.set_color(RED)
                cross.move_to(arrow.get_center())
                cross.set_stroke(RED, width = 5)
                arrow.add(cross)
            arrows.add(arrow)


        self.play(
            Transform(ring_group, big_group),
            self.pi_creature.change_mode, "sassy"
        )
        for n, frac in enumerate(fracs):
            anims = [FadeIn(frac)]
            num_fracs = len(sample_dRs)
            if n < num_fracs:
                anims.append(ShowCreation(arrows[n]))
                anims.append(Transform(
                    ring_group, small_group,
                    rate_func = lambda t : t*(1./(num_fracs-n)),
                    run_time = 2
                ))
            elif n > num_fracs:
                anims.append(ShowCreation(arrows[-1]))
            self.play(*anims)
        self.wait(2)
        self.play(
            FadeOut(arrows),
            ring_group.restore,
            self.pi_creature.change_mode, "happy",
        )
        self.wait()

    def reference_approximation(self):
        ring_copy = self.outer_ring.copy()
        self.unwrap_ring(ring_copy)
        self.wait()
        self.last_mover = ring_copy

    def emphasize_equality(self):
        equals = self.dArea_fom[-2]

        self.play(Transform(self.last_mover, equals))
        self.remove(self.last_mover)
        self.play(
            equals.scale_in_place, 1.5,
            equals.set_color, GREEN,
            rate_func = there_and_back,
            run_time = 2
        )
        self.play(
            self.two_pi_R.set_stroke, YELLOW, 3,
            rate_func = there_and_back,
            run_time = 2
        )
        self.wait()

        new_words = TextMobject(
            "Systematically\\\\",
            "ignore error"
        )
        new_words.move_to(self.words)
        self.play(Transform(self.words, new_words))
        self.wait()

class DerivativeAsTangentLine(ZoomedScene):
    CONFIG = {
        "zoomed_canvas_frame_shape" : (4, 4),
        "zoom_factor" : 10,
        "R_min" : 0,
        "R_max" : 2.5,
        "R_to_zoom_in_on" : 2,
        "little_rect_nudge" : 0.075*(UP+RIGHT),
    }
    def construct(self):
        self.setup_axes()
        self.show_zoomed_in_steps()
        self.show_tangent_lines()
        self.state_commonality()

    def setup_axes(self):
        x_axis = NumberLine(
            x_min = -0.25, 
            x_max = 4,
            unit_size = 2,
            tick_frequency = 0.25,
            leftmost_tick = -0.25,
            numbers_with_elongated_ticks = [0, 1, 2, 3, 4],
            color = GREY
        )
        x_axis.shift(2.5*DOWN)
        x_axis.shift(4*LEFT)
        x_axis.add_numbers(1, 2, 3, 4)
        x_label = TexMobject("R")
        x_label.next_to(x_axis, RIGHT+UP, buff = SMALL_BUFF)
        self.x_axis_label = x_label

        y_axis = NumberLine(
            x_min = -2,
            x_max = 20,
            unit_size = 0.3,
            tick_frequency = 2.5,
            leftmost_tick = 0,
            longer_tick_multiple = -2,
            numbers_with_elongated_ticks = [0, 5, 10, 15, 20],
            color = GREY
        )
        y_axis.shift(x_axis.number_to_point(0)-y_axis.number_to_point(0))
        y_axis.rotate(np.pi/2, about_point = y_axis.number_to_point(0))
        y_axis.add_numbers(5, 10, 15, 20)
        y_axis.numbers.shift(0.4*UP+0.5*LEFT)
        y_label = TexMobject("A")
        y_label.next_to(y_axis.get_top(), RIGHT, buff = MED_LARGE_BUFF)

        def func(alpha):
            R = interpolate(self.R_min, self.R_max, alpha)
            x = x_axis.number_to_point(R)[0]
            output = np.pi*(R**2)
            y = y_axis.number_to_point(output)[1]
            return x*RIGHT + y*UP

        graph = ParametricFunction(func, color = BLUE)
        graph_label = TexMobject("A(R) = \\pi R^2")
        graph_label.set_color(BLUE)
        graph_label.next_to(
            graph.point_from_proportion(2), LEFT
        )

        self.play(Write(VGroup(x_axis, y_axis)))
        self.play(ShowCreation(graph))
        self.play(Write(graph_label))
        self.play(Write(VGroup(x_label, y_label)))
        self.wait()

        self.x_axis, self.y_axis = x_axis, y_axis
        self.graph = graph
        self.graph_label = graph_label

    def graph_point(self, R):
        alpha = (R - self.R_min)/(self.R_max - self.R_min)
        return self.graph.point_from_proportion(alpha)

    def angle_of_tangent(self, R, dR = 0.01):
        vect = self.graph_point(R + dR) - self.graph_point(R)
        return angle_of_vector(vect)

    def show_zoomed_in_steps(self):
        R = self.R_to_zoom_in_on
        dR = 0.05
        graph_point = self.graph_point(R)
        nudged_point = self.graph_point(R+dR)
        interim_point = nudged_point[0]*RIGHT + graph_point[1]*UP


        self.activate_zooming()        
        dot = Dot(color = YELLOW)
        dot.scale(0.1)
        dot.move_to(graph_point)

        self.play(*list(map(FadeIn, [
            self.little_rectangle,
            self.big_rectangle
        ])))
        self.play(
            self.little_rectangle.move_to, 
            graph_point+self.little_rect_nudge
        )
        self.play(FadeIn(dot))

        dR_line = Line(graph_point, interim_point)
        dR_line.set_color(YELLOW)
        dA_line = Line(interim_point, nudged_point)
        dA_line.set_color(GREEN)
        tiny_buff = SMALL_BUFF/self.zoom_factor
        for line, vect, char in (dR_line, DOWN, "R"), (dA_line, RIGHT, "A"):
            line.brace = Brace(Line(LEFT, RIGHT))
            line.brace.scale(1./self.zoom_factor)
            line.brace.stretch_to_fit_width(line.get_length())
            line.brace.rotate(line.get_angle())
            line.brace.next_to(line, vect, buff = tiny_buff)
            line.text = TexMobject("d%s"%char)
            line.text.scale(1./self.zoom_factor)
            line.text.set_color(line.get_color())
            line.text.next_to(line.brace, vect, buff = tiny_buff)
            self.play(ShowCreation(line))
            self.play(Write(VGroup(line.brace, line.text)))
            self.wait()

        deriv_is_slope = TexMobject(
            "\\frac{dA}{dR} =", "\\text{Slope}"
        )
        self.slope_word = deriv_is_slope[1]
        VGroup(*deriv_is_slope[0][:2]).set_color(GREEN)
        VGroup(*deriv_is_slope[0][3:5]).set_color(YELLOW)
        deriv_is_slope.next_to(self.y_axis, RIGHT)
        deriv_is_slope.shift(UP)

        self.play(Write(deriv_is_slope))
        self.wait()

        ### Whoa boy, this aint' gonna be pretty
        self.dot = dot
        self.small_step_group = VGroup(
            dR_line, dR_line.brace, dR_line.text,
            dA_line, dA_line.brace, dA_line.text,
        )
        def update_small_step_group(group):
            R = self.x_axis.point_to_number(dot.get_center())
            graph_point = self.graph_point(R)
            nudged_point = self.graph_point(R+dR)
            interim_point = nudged_point[0]*RIGHT + graph_point[1]*UP

            dR_line.put_start_and_end_on(graph_point, interim_point)
            dA_line.put_start_and_end_on(interim_point, nudged_point)

            dR_line.brace.stretch_to_fit_width(dR_line.get_width())
            dR_line.brace.next_to(dR_line, DOWN, buff = tiny_buff)
            dR_line.text.next_to(dR_line.brace, DOWN, buff = tiny_buff)

            dA_line.brace.stretch_to_fit_height(dA_line.get_height())
            dA_line.brace.next_to(dA_line, RIGHT, buff = tiny_buff)
            dA_line.text.next_to(dA_line.brace, RIGHT, buff = tiny_buff)
        self.update_small_step_group = update_small_step_group

    def show_tangent_lines(self):
        R = self.R_to_zoom_in_on
        line = Line(LEFT, RIGHT).scale(FRAME_Y_RADIUS)
        line.set_color(MAROON_B)
        line.rotate(self.angle_of_tangent(R))
        line.move_to(self.graph_point(R))
        x_axis_y = self.x_axis.number_to_point(0)[1]
        two_pi_R = TexMobject("= 2\\pi R")
        two_pi_R.next_to(self.slope_word, DOWN, aligned_edge = RIGHT)
        two_pi_R.shift(0.5*LEFT)

        def line_update_func(line):
            R = self.x_axis.point_to_number(self.dot.get_center())
            line.rotate(
                self.angle_of_tangent(R) - line.get_angle()
            )
            line.move_to(self.dot)
        def update_little_rect(rect):
            R = self.x_axis.point_to_number(self.dot.get_center())
            rect.move_to(self.graph_point(R) + self.little_rect_nudge)

        self.play(ShowCreation(line))
        self.wait()
        self.note_R_value_of_point()

        alphas = np.arange(0, 1, 0.01)
        graph_points = list(map(self.graph.point_from_proportion, alphas))
        curr_graph_point = self.graph_point(R)
        self.last_alpha = alphas[np.argmin([
            get_norm(point - curr_graph_point)
            for point in graph_points
        ])]
        def shift_everything_to_alpha(alpha, run_time = 3):
            self.play(
                MoveAlongPath(
                    self.dot, self.graph,
                    rate_func = lambda t : interpolate(self.last_alpha, alpha, smooth(t))
                ),
                UpdateFromFunc(line, line_update_func),
                UpdateFromFunc(self.small_step_group, self.update_small_step_group),
                UpdateFromFunc(self.little_rectangle, update_little_rect),
                run_time = run_time
            )
            self.last_alpha = alpha

        for alpha in 0.95, 0.2:
            shift_everything_to_alpha(alpha)
        self.wait()
        self.play(Write(two_pi_R))
        self.wait()
        shift_everything_to_alpha(0.8, 4)
        self.wait()

    def note_R_value_of_point(self):
        R = self.R_to_zoom_in_on
        point = self.graph_point(R)
        R_axis_point = point[0]*RIGHT + 2.5*DOWN

        dashed_line = DashedLine(point, R_axis_point, color = RED)
        dot = Dot(R_axis_point, color = RED)
        arrow = Arrow(
            self.x_axis_label.get_left(),
            dot,
            buff = SMALL_BUFF
        )
        self.play(ShowCreation(dashed_line))
        self.play(ShowCreation(dot))
        self.play(ShowCreation(arrow))
        self.play(dot.scale_in_place, 2, rate_func = there_and_back)
        self.wait()
        self.play(*list(map(FadeOut, [dashed_line, dot, arrow])))

    def state_commonality(self):
        morty = Mortimer()
        morty.scale(0.7)
        morty.to_edge(DOWN).shift(2*RIGHT)
        bubble = morty.get_bubble(SpeechBubble, height = 2)
        bubble.set_fill(BLACK, opacity = 0.8)
        bubble.shift(0.5*DOWN)        
        bubble.write("This is the standard view")

        self.play(FadeIn(morty))
        self.play(
            ShowCreation(bubble),
            Write(bubble.content),
            morty.change_mode, "surprised"
        )
        self.play(Blink(morty))
        self.wait()
        new_words = TextMobject("Which is...fine...")
        new_words.move_to(bubble.content, RIGHT)
        self.play(
            bubble.stretch_to_fit_width, 5,
            bubble.shift, RIGHT,
            Transform(bubble.content, new_words),            
            morty.change_mode, "hesitant"
        )
        self.play(Blink(morty))
        self.wait()

class SimpleConfusedPi(Scene):
    def construct(self):
        randy = Randolph()
        confused = Randolph(mode = "confused")
        for pi in randy, confused:
            pi.flip()
            pi.look(UP+LEFT)
            pi.scale(2)
            pi.rotate(np.pi/2)
        self.play(Transform(randy, confused))
        self.wait()

class TangentLinesAreNotEverything(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            Tangent lines are just
            one way to visualize 
            derivatives
        """)
        self.change_student_modes("raise_left_hand", "pondering", "erm")
        self.random_blink(3)

class OnToIntegrals(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("On to integrals!", target_mode = "hooray")
        self.change_student_modes(*["happy"]*3)
        self.random_blink(3)

class IntroduceConcentricRings(CircleScene):
    CONFIG = {
        "radius" : 2.5,
        "special_ring_index" : 10,
        "include_pi_creature" : True,
    }
    def construct(self):
        self.build_up_rings()
        self.add_up_areas()
        self.unwrap_special_ring()
        self.write_integral()
        self.ask_about_approx()

    def create_pi_creature(self):
        morty = Mortimer()
        morty.scale(0.7)
        morty.to_corner(DOWN+RIGHT)
        return morty

    def build_up_rings(self):
        self.circle.set_fill(opacity = 0)
        rings = VGroup(*[
            self.get_ring(r, self.dR)
            for r in np.arange(0, self.radius, self.dR)
        ])
        rings.set_color_by_gradient(BLUE_E, GREEN_E)
        rings.set_stroke(BLACK, width = 1)
        outermost_ring = rings[-1]
        dr_line = Line(
            rings[-2].get_top(), 
            rings[-1].get_top(),
            color = YELLOW
        )
        dr_text = TexMobject("dr")
        dr_text.move_to(self.circle.get_corner(UP+RIGHT))
        dr_text.shift(LEFT)
        dr_text.set_color(YELLOW)
        dr_arrow = Arrow(dr_text, dr_line, buff = SMALL_BUFF)
        self.dr_group = VGroup(dr_text, dr_arrow, dr_line)


        foreground_group = VGroup(self.radius_brace, self.radius_label, self.radius_line)
        self.play(
            FadeIn(outermost_ring), 
            Animation(foreground_group)
        )
        self.play(
            Write(dr_text),
            ShowCreation(dr_arrow),
            ShowCreation(dr_line)
        )
        foreground_group.add(dr_line, dr_arrow, dr_text)        
        self.change_mode("pondering")
        self.wait()
        self.play(
            FadeIn(
                VGroup(*rings[:-1]),
                lag_ratio=1,
                run_time = 5
            ),
            Animation(foreground_group)
        )
        self.wait()

        self.foreground_group = foreground_group
        self.rings = rings

    def add_up_areas(self):
        start_rings = VGroup(*self.rings[:4])
        moving_rings = start_rings.copy()
        moving_rings.generate_target()
        moving_rings.target.set_stroke(width = 0)
        plusses = VGroup(*[TexMobject("+") for ring in moving_rings])
        area_sum = VGroup(*it.chain(*list(zip(
            [ring for ring in moving_rings.target],
            plusses
        ))))
        dots_equals_area = TexMobject("\\dots", "=", "\\pi R^2")
        area_sum.add(*dots_equals_area)
        area_sum.arrange()
        area_sum.to_edge(RIGHT)
        area_sum.to_edge(UP, buff = MED_SMALL_BUFF)
        dots_equals_area[-1].shift(0.1*UP)
        self.area_sum_rhs = dots_equals_area[-1]

        # start_rings.set_fill(opacity = 0.3)
        self.play(
            MoveToTarget(
                moving_rings,
                lag_ratio = 0.5,
            ),
            Write(
                VGroup(plusses, dots_equals_area),
                rate_func = squish_rate_func(smooth, 0.5, 1)
            ),
            Animation(self.foreground_group),
            run_time = 5,
        )
        self.wait()
        self.area_sum = area_sum

    def unwrap_special_ring(self):
        rings = self.rings
        foreground_group = self.foreground_group
        special_ring = rings[self.special_ring_index]
        special_ring.save_state()

        radius = (special_ring.get_width()-2*self.dR)/2.
        radial_line = Line(ORIGIN, radius*RIGHT)
        radial_line.rotate(np.pi/4)
        radial_line.shift(self.circle.get_center())
        radial_line.set_color(YELLOW)
        r_label = TexMobject("r")
        r_label.next_to(radial_line.get_center(), UP+LEFT, buff = SMALL_BUFF)

        rings.generate_target()
        rings.save_state()
        rings.target.set_fill(opacity = 0.3)
        rings.target.set_stroke(BLACK)
        rings.target[self.special_ring_index].set_fill(opacity = 1)
        self.play(
            MoveToTarget(rings),
            Animation(foreground_group)
        )
        self.play(ShowCreation(radial_line))
        self.play(Write(r_label))
        self.foreground_group.add(radial_line, r_label)
        self.wait()
        self.unwrap_ring(special_ring, to_edge = RIGHT)

        brace = Brace(special_ring, UP)
        brace.stretch_in_place(0.9, 0)
        two_pi_r = brace.get_text("$2\\pi r$")
        left_brace = TexMobject("\\{")
        left_brace.stretch_to_fit_height(1.5*self.dR)
        left_brace.next_to(special_ring, LEFT, buff = SMALL_BUFF)
        dr = TexMobject("dr")
        dr.next_to(left_brace, LEFT, buff = SMALL_BUFF)
        self.play(
            GrowFromCenter(brace),
            Write(two_pi_r)
        )
        self.play(GrowFromCenter(left_brace), Write(dr))
        self.wait()

        think_concrete = TextMobject("Think $dr = 0.1$")
        think_concrete.next_to(dr, DOWN+LEFT, buff = LARGE_BUFF)
        arrow = Arrow(think_concrete.get_top(), dr)
        self.play(
            Write(think_concrete),
            ShowCreation(arrow),
            self.pi_creature.change_mode, "speaking"
        )
        self.wait()

        less_wrong = TextMobject("""
            Approximations get
            less wrong
        """)
        less_wrong.next_to(self.pi_creature, LEFT, aligned_edge = UP)
        self.play(Write(less_wrong))
        self.wait()

        self.special_ring = special_ring
        self.radial_line = radial_line
        self.r_label = r_label
        self.to_fade = VGroup(
            brace, left_brace, two_pi_r, dr, 
            think_concrete, arrow, less_wrong
        )
        self.two_pi_r = two_pi_r.copy()
        self.dr = dr.copy()

    def write_integral(self):
        brace = Brace(self.area_sum)
        formula_q = brace.get_text("Nice formula?")
        int_sym, R, zero = def_int = TexMobject("\\int", "_0", "^R")
        self.two_pi_r.generate_target()
        self.dr.generate_target()
        equals_pi_R_squared = TexMobject("= \\pi R^2")
        integral_expression = VGroup(
            def_int, self.two_pi_r.target,
            self.dr.target, equals_pi_R_squared
        )
        integral_expression.arrange()
        integral_expression.next_to(brace, DOWN)
        self.integral_expression = VGroup(*integral_expression[:-1])

        self.play(
            GrowFromCenter(brace),
            Write(formula_q),
            self.pi_creature.change_mode, "pondering"
        )
        self.wait(2)

        last = VMobject()
        last.save_state()
        for ring in self.rings:
            ring.save_state()
            target = ring.copy()
            target.set_fill(opacity = 1)
            self.play(
                last.restore,
                Transform(ring, target),
                Animation(self.foreground_group),
                run_time = 0.5
            )
            last = ring
        self.play(last.restore)
        self.wait()

        ghost = self.rings.copy()
        for mob in self.area_sum_rhs, self.two_pi_r:
            ghost.set_fill(opacity = 0.1)
            self.play(Transform(ghost, mob))
            self.wait()
        self.remove(ghost)

        self.wait()
        self.play(FadeOut(formula_q))
        self.play(Write(int_sym))
        self.wait()
        self.rings.generate_target()
        self.rings.target.set_fill(opacity = 1)
        self.play(
            MoveToTarget(self.rings, rate_func = there_and_back),
            Animation(self.foreground_group)
        )
        self.wait()
        self.grow_and_shrink_r_line(zero, R)
        self.wait()
        self.play(
            MoveToTarget(self.two_pi_r),
            MoveToTarget(self.dr),
            run_time = 2
        )
        self.wait()
        self.play(
            FadeOut(self.to_fade),
            ApplyMethod(self.rings.restore, run_time = 2),
            Animation(self.foreground_group)
        )
        self.wait()
        self.play(Write(equals_pi_R_squared))
        self.wait()
        self.equals = equals_pi_R_squared[0]
        self.integral_terms = VGroup(
            self.integral_expression[1], 
            self.integral_expression[2], 
            self.int_lower_bound, 
            self.int_upper_bound,
            VGroup(*equals_pi_R_squared[1:])
        )

    def grow_and_shrink_r_line(self, zero_target, R_target):
        self.radial_line.get_center = self.circle.get_center
        self.radial_line.save_state()
        self.radial_line.generate_target()
        self.radial_line.target.scale_in_place(
            0.1 / self.radial_line.get_length()
        )
        self.r_label.generate_target()
        self.r_label.save_state()
        equals_0 = TexMobject("=0")
        r_equals_0 = VGroup(self.r_label.target, equals_0)
        r_equals_0.arrange(buff = SMALL_BUFF)
        r_equals_0.next_to(self.radial_line.target, UP+LEFT, buff = SMALL_BUFF)
        self.play(
            MoveToTarget(self.radial_line),
            MoveToTarget(self.r_label),
            GrowFromCenter(equals_0)
        )
        self.play(equals_0[-1].copy().replace, zero_target)
        self.remove(self.get_mobjects_from_last_animation()[0])
        self.add(zero_target)
        self.wait()
        self.radial_line.target.scale_in_place(
            self.radius/self.radial_line.get_length()
        )
        equals_0.target = TexMobject("=R")
        equals_0.target.next_to(
            self.radial_line.target.get_center_of_mass(),
            UP+LEFT, buff = SMALL_BUFF
        )
        self.r_label.target.next_to(equals_0.target, LEFT, buff = SMALL_BUFF)
        self.play(
            MoveToTarget(self.radial_line),
            MoveToTarget(self.r_label),
            MoveToTarget(equals_0)
        )
        self.play(equals_0[-1].copy().replace, R_target)
        self.remove(self.get_mobjects_from_last_animation()[0])
        self.add(R_target)
        self.wait()
        self.play(
            self.radial_line.restore,
            self.r_label.restore,
            FadeOut(equals_0)
        )
        self.int_lower_bound, self.int_upper_bound = zero_target, R_target

    def ask_about_approx(self):
        approx = TexMobject("\\approx").replace(self.equals)
        self.equals.save_state()
        question = TextMobject(
            "Should this be\\\\",
            "an approximation?"
        )
        question.next_to(approx, DOWN, buff = 1.3*LARGE_BUFF)
        arrow = Arrow(question, approx, buff = MED_SMALL_BUFF)
        approach_words = TextMobject("Consider\\\\", "$dr \\to 0$")
        approach_words.move_to(question, RIGHT)
        int_brace = Brace(self.integral_expression)
        integral_word = int_brace.get_text("``Integral''")

        self.play(
            Transform(self.equals, approx),
            Write(question),
            ShowCreation(arrow),
            self.pi_creature.change_mode, "confused"
        )
        self.wait(2)
        self.play(*[
            ApplyMethod(ring.set_stroke, ring.get_color(), width = 1)
            for ring in self.rings
        ] + [
            FadeOut(self.dr_group),
            Animation(self.foreground_group)
        ])
        self.wait()
        self.play(
            Transform(question, approach_words),
            Transform(arrow, Arrow(approach_words, approx)),
            self.equals.restore,
            self.pi_creature.change_mode, "happy"
        )
        self.wait(2)
        self.play(
            self.integral_expression.set_color_by_gradient, BLUE, GREEN,
            GrowFromCenter(int_brace),
            Write(integral_word)
        )
        self.wait()
        for term in self.integral_terms:
            term.save_state()
            self.play(term.set_color, YELLOW)
            self.play(term.restore)
        self.wait(3)

class AskAboutGeneralCircles(TeacherStudentsScene):
    def construct(self):
        self.student_says("""
            What about integrals
            beyond this circle
            example?
        """)
        self.change_student_modes("confused")
        self.random_blink(2)
        self.teacher_says(
            "All in due time",
        )
        self.change_student_modes(*["happy"]*3)
        self.random_blink(2)

class GraphIntegral(GraphScene):
    CONFIG = {
        "x_min" : -0.25,
        "x_max" : 4,
        "x_tick_frequency" : 0.25,
        "x_leftmost_tick" : -0.25,
        "x_labeled_nums" : list(range(1, 5)),
        "x_axis_label" : "r",
        "y_min" : -2,
        "y_max" : 25,
        "y_tick_frequency" : 2.5,
        "y_bottom_tick" : 0,
        "y_labeled_nums" : list(range(5, 30, 5)),
        "y_axis_label" : "",
        "dr" : 0.125,
        "R" : 3.5,
    }
    def construct(self):
        self.func = lambda r : 2*np.pi*r
        integral = TexMobject("\\int_0^R 2\\pi r \\, dr")
        integral.to_edge(UP).shift(LEFT)
        self.little_r = integral[5]

        self.play(Write(integral))
        self.wait()
        self.setup_axes()
        self.show_horizontal_axis()
        self.add_rectangles()
        self.thinner_rectangles()
        self.ask_about_area()

    def show_horizontal_axis(self):
        arrows = [
            Arrow(self.little_r, self.coords_to_point(*coords))
            for coords in ((0, 0), (self.x_max, 0))
        ]
        moving_arrow = arrows[0].copy()
        self.play(
            ShowCreation(moving_arrow),
            self.little_r.set_color, YELLOW
        )
        for arrow in reversed(arrows):
            self.play(Transform(moving_arrow, arrow, run_time = 4))
        self.play(
            FadeOut(moving_arrow),
            self.little_r.set_color, WHITE
        )
        
    def add_rectangles(self):
        tick_height = 0.2
        special_tick_index = 12
        ticks = VGroup(*[
            Line(UP, DOWN).move_to(self.coords_to_point(x, 0))
            for x in np.arange(0, self.R+self.dr, self.dr)
        ])
        ticks.stretch_to_fit_height(tick_height)
        ticks.set_color(YELLOW)
        R_label = TexMobject("R")
        R_label.next_to(self.coords_to_point(self.R, 0), DOWN)

        values_words = TextMobject("Values of $r$")
        values_words.shift(UP)
        arrows = VGroup(*[
            Arrow(
                values_words.get_bottom(), 
                tick.get_center(), 
                tip_length = 0.15
            )
            for tick in ticks
        ])

        dr_brace = Brace(
            VGroup(*ticks[special_tick_index:special_tick_index+2]), 
            buff = SMALL_BUFF
        )
        dr_text = dr_brace.get_text("$dr$", buff = SMALL_BUFF)
        # dr_text.set_color(YELLOW)

        rectangles = self.get_rectangles(self.dr)
        special_rect = rectangles[special_tick_index]
        left_brace = Brace(special_rect, LEFT)
        height_label = left_brace.get_text("$2\\pi r$")

        self.play(
            ShowCreation(ticks, lag_ratio = 0.5),
            Write(R_label)
        )
        self.play(
            Write(values_words),
            ShowCreation(arrows)
        )
        self.wait()
        self.play(
            GrowFromCenter(dr_brace),
            Write(dr_text)
        )
        self.wait()
        rectangles.save_state()
        rectangles.stretch_to_fit_height(0)
        rectangles.move_to(self.graph_origin, DOWN+LEFT)
        self.play(*list(map(FadeOut, [arrows, values_words])))
        self.play(
            rectangles.restore, 
            Animation(ticks),
            run_time = 2
        )
        self.wait()
        self.play(*[
            ApplyMethod(rect.fade, 0.7)
            for rect in rectangles
            if rect is not special_rect
        ] + [Animation(ticks)])
        self.play(
            GrowFromCenter(left_brace),
            Write(height_label)
        )
        self.wait()

        graph = self.graph_function(
            lambda r : 2*np.pi*r, 
            animate = False
        )
        graph_label = self.label_graph(
            self.graph, "f(r) = 2\\pi r", 
            proportion = 0.5,
            direction = LEFT,
            animate = False
        )
        self.play(
            rectangles.restore,
            Animation(ticks),
            FadeOut(left_brace),
            Transform(height_label, graph_label),
            ShowCreation(graph)
        )
        self.wait(3)
        self.play(*list(map(FadeOut, [ticks, dr_brace, dr_text])))
        self.rectangles = rectangles

    def thinner_rectangles(self):
        for x in range(2, 8):
            new_rects = self.get_rectangles(
                dr = self.dr/x, stroke_width = 1./x
            )
            self.play(Transform(self.rectangles, new_rects))
        self.wait()

    def ask_about_area(self):
        question = TextMobject("What's this \\\\ area")
        question.to_edge(RIGHT).shift(2*UP)
        arrow = Arrow(
            question.get_bottom(), 
            self.rectangles, 
            buff = SMALL_BUFF
        )
        self.play(
            Write(question),
            ShowCreation(arrow)
        )
        self.wait()

    def get_rectangles(self, dr, stroke_width = 1):
        return self.get_riemann_rectangles(
            0, self.R, dr, stroke_width = stroke_width
        )

class MoreOnThisLater(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            More details on
            integrals later
        """)
        self.change_student_modes(
            "raise_right_hand", 
            "raise_left_hand",
            "raise_left_hand",
        )
        self.random_blink(2)
        self.teacher_says("""
            This is just
            a preview
        """)
        self.random_blink(2)

class FundamentalTheorem(CircleScene):
    CONFIG = {
        "circle_corner" : ORIGIN,
        "radius" : 1.5,
        "area_color" : BLUE,
        "circum_color" : WHITE,
        "unwrapped_tip" : 2.5*UP,
        "include_pi_creature" : False
    }
    def setup(self):
        CircleScene.setup(self)
        group = VGroup(
            self.circle, self.radius_line,
            self.radius_brace, self.radius_label
        )
        self.remove(*group)
        group.shift(DOWN)

        self.foreground_group = VGroup(
            self.radius_line,
            self.radius_brace,
            self.radius_label,
        )

    def create_pi_creature(self):
        morty = Mortimer()
        morty.scale(0.7)
        morty.to_corner(DOWN+RIGHT)
        return morty

    def construct(self):
        self.add_derivative_terms()
        self.add_integral_terms()
        self.think_about_it()
        self.bring_in_circle()
        self.show_outer_ring()
        self.show_all_rings()
        self.emphasize_oposites()

    def add_derivative_terms(self):
        symbolic = TexMobject(
            "\\frac{d(\\pi R^2)}{dR} =", "2\\pi R"
        )
        VGroup(*symbolic[0][2:5]).set_color(self.area_color)
        VGroup(*symbolic[0][7:9]).set_color(self.dR_color)
        symbolic[1].set_color(self.circum_color)

        geometric = TexMobject("\\frac{d \\quad}{dR}=")
        VGroup(*geometric[2:4]).set_color(self.dR_color)
        radius = geometric[0].get_height()
        area_circle = Circle(
            stroke_width = 0,
            fill_color = self.area_color,
            fill_opacity = 0.5,
            radius = radius
        )
        area_circle.next_to(geometric[0], buff = SMALL_BUFF)
        circum_circle = Circle(
            color = self.circum_color,
            radius = radius
        )
        circum_circle.next_to(geometric, RIGHT)
        geometric.add(area_circle, circum_circle)
        self.derivative_terms = VGroup(symbolic, geometric)
        self.derivative_terms.arrange(
            DOWN, buff = LARGE_BUFF, aligned_edge = LEFT
        )
        self.derivative_terms.next_to(ORIGIN, LEFT, buff = LARGE_BUFF)

        self.play(
            Write(self.derivative_terms),
            self.pi_creature.change_mode, "hooray"
        )
        self.wait()

    def add_integral_terms(self):
        symbolic = TexMobject(
            "\\int_0^R", "2\\pi r", "\\cdot", "dr", "=", "\\pi R^2"
        )
        symbolic.set_color_by_tex("2\\pi r", self.circum_color)
        symbolic.set_color_by_tex("dr", self.dR_color)
        symbolic.set_color_by_tex("\\pi R^2", self.area_color)

        geometric = symbolic.copy()
        area_circle = Circle(
            radius = geometric[-1].get_width()/2,
            stroke_width = 0,
            fill_color = self.area_color,
            fill_opacity = 0.5
        )
        area_circle.move_to(geometric[-1])
        circum_circle = Circle(
            radius = geometric[1].get_width()/2,
            color = self.circum_color
        )
        circum_circle.move_to(geometric[1])
        geometric.submobjects[1] = circum_circle
        geometric.submobjects[-1] = area_circle

        self.integral_terms = VGroup(symbolic, geometric)
        self.integral_terms.arrange(
            DOWN, 
            buff = LARGE_BUFF, 
            aligned_edge = LEFT
        )
        self.integral_terms.next_to(ORIGIN, RIGHT, buff = LARGE_BUFF)

        self.play(Write(self.integral_terms))
        self.wait()

    def think_about_it(self):
        for mode in "confused", "pondering", "surprised":
            self.change_mode(mode)
            self.wait()

    def bring_in_circle(self):
        self.play(
            FadeOut(self.derivative_terms[0]),
            FadeOut(self.integral_terms[0]),
            self.derivative_terms[1].to_corner, UP+LEFT, MED_LARGE_BUFF,
            self.integral_terms[1].to_corner, UP+RIGHT, MED_LARGE_BUFF,
            self.pi_creature.change_mode, "speaking"
        )
        self.introduce_circle()

    def show_outer_ring(self):
        self.increase_radius(numerical_dr = False)
        self.foreground_group.add(self.nudge_line, self.nudge_arrow)
        self.wait()
        ring_copy = self.outer_ring.copy()
        ring_copy.save_state()
        self.unwrap_ring(ring_copy, to_edge = LEFT)
        brace = Brace(ring_copy, UP)
        brace.stretch_in_place(0.95, 0)
        deriv = brace.get_text("$\\dfrac{dA}{dR}$")
        VGroup(*deriv[:2]).set_color(self.outer_ring.get_color())
        VGroup(*deriv[-2:]).set_color(self.dR_color)
        self.play(
            GrowFromCenter(brace),
            Write(deriv),
            self.pi_creature.change_mode, "happy"
        )
        self.to_fade = VGroup(deriv, brace)
        self.to_restore = ring_copy        

    def show_all_rings(self):
        rings = VGroup(*[
            self.get_ring(radius = r, dR = self.dR)
            for r in np.arange(0, self.radius, self.dR)
        ])
        rings.set_color_by_gradient(BLUE_E, GREEN_E)
        rings.save_state()
        integrand = self.integral_terms[1][1]
        for ring in rings:
            Transform(ring, integrand).update(1)

        self.play(
            ApplyMethod(
                rings.restore,
                lag_ratio = 0.5,
                run_time = 5
            ),
            Animation(self.foreground_group),
        )

    def emphasize_oposites(self):
        self.play(
            FadeOut(self.to_fade),
            self.to_restore.restore,
            Animation(self.foreground_group),
            run_time = 2
        )
        arrow = DoubleArrow(
            self.derivative_terms[1],
            self.integral_terms[1],
        )
        opposites = TextMobject("Opposites")
        opposites.next_to(arrow, DOWN)

        self.play(
            ShowCreation(arrow),
            Write(opposites)
        )
        self.wait()

class NameTheFundamentalTheorem(TeacherStudentsScene):
    def construct(self):
        symbols = TexMobject(
            "\\frac{d}{dx} \\int_0^x f(t)dt = f(x)",
        )
        symbols.to_corner(UP+LEFT)
        brace = Brace(symbols)
        abstract = brace.get_text("Abstract version")
        self.add(symbols)
        self.play(
            GrowFromCenter(brace),
            Write(abstract),
            *[
                ApplyMethod(pi.look_at, symbols)
                for pi in self.get_pi_creatures()
            ]
        )
        self.change_student_modes("pondering", "confused", "erm")
        self.random_blink()
        self.teacher_says("""
            This is known as
            the ``fundamental 
            theorem of calculus''
        """, width = 5, height = 5, target_mode = "hooray")
        self.random_blink(3)
        self.teacher_says("""
            We'll get here
            in due time.
        """)
        self.change_student_modes(*["happy"]*3)
        self.wait(2)

class CalculusInANutshell(CircleScene):
    CONFIG = {
        "circle_corner" : ORIGIN,
        "radius" : 3,
    }
    def construct(self):
        self.clear()
        self.morph_word()
        self.show_remainder_of_series()

    def morph_word(self):
        calculus = TextMobject("Calculus")
        calculus.scale(1.5)
        calculus.to_edge(UP)
        dR = self.radius/float(len(calculus.split()))
        rings = VGroup(*[
            self.get_ring(rad, 0.95*dR)
            for rad in np.arange(0, self.radius, dR)
        ])
        for ring in rings:
            ring.add(ring.copy().rotate(np.pi))
        for mob in calculus, rings:
            mob.set_color_by_gradient(BLUE, GREEN)
        rings.set_stroke(width = 0) 

        self.play(Write(calculus))
        self.wait()
        self.play(Transform(
            calculus, rings,
            lag_ratio = 0.5,
            run_time = 5
        ))
        self.wait()

    def show_remainder_of_series(self):
        series = VideoSeries()
        first = series[0]
        first.set_fill(YELLOW)
        first.save_state()
        first.center()
        first.set_height(FRAME_Y_RADIUS*2)
        first.set_fill(opacity = 0)
        everything = VGroup(*self.get_mobjects())
        everything.generate_target()
        everything.target.scale(series[1].get_height()/first.get_height())
        everything.target.shift(first.saved_state.get_center())
        everything.target.set_fill(opacity = 0.1)

        second = series[1]
        brace = Brace(second)
        derivatives = brace.get_text("Derivatives")

        self.play(
            MoveToTarget(everything),
            first.restore,
            run_time = 2
        )
        self.play(FadeIn(
            VGroup(*series[1:]),
            lag_ratio = 0.5,
            run_time = 2,
        ))
        self.wait()
        self.play(
            GrowFromCenter(brace),
            Write(derivatives)
        )
        self.wait()

class Thumbnail(CircleScene):
    CONFIG = {
        "radius" : 2,
        "circle_corner" : ORIGIN
    }
    def construct(self):
        self.clear()
        title = TextMobject("Essence of \\\\ calculus")
        title.scale(2)
        title.to_edge(UP)

        area_circle = Circle(
            fill_color = BLUE,
            fill_opacity = 0.5,
            stroke_width = 0,
        )
        circum_circle = Circle(
            color = YELLOW
        )

        deriv_eq = TexMobject("\\frac{d \\quad}{dR} = ")
        int_eq = TexMobject("\\int_0^R \\quad = ") 
        target_height = deriv_eq[0].get_height()*2
        area_circle.set_height(target_height)
        circum_circle.set_height(target_height)

        area_circle.next_to(deriv_eq[0], buff = SMALL_BUFF)
        circum_circle.next_to(deriv_eq)
        deriv_eq.add(area_circle.copy(), circum_circle.copy())

        area_circle.next_to(int_eq)
        circum_circle.next_to(int_eq[-1], LEFT)
        int_eq.add(area_circle, circum_circle)

        for mob in deriv_eq, int_eq:
            mob.scale(1.5)

        arrow = TexMobject("\\Leftrightarrow").scale(2)
        arrow.shift(DOWN)
        deriv_eq.next_to(arrow, LEFT)
        int_eq.next_to(arrow, RIGHT)

        self.add(title, arrow, deriv_eq, int_eq)














