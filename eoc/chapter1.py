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
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

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
    }
    def setup(self):
        self.circle = Circle(
            radius = self.radius,
            stroke_color = self.stroke_color,
            fill_color = self.fill_color,
            fill_opacity = self.fill_opacity,
        )
        self.circle.to_corner(UP+LEFT, buff = 2*MED_BUFF)
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

        self.pi_creature = self.get_pi_creature()
        if self.include_pi_creature:
            self.add(self.pi_creature)

    def get_pi_creature(self):
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

    def increase_radius(self):
        radius_mobs = VGroup(
            self.radius_line, self.radius_brace, self.radius_label
        )
        nudge_line = Line(
            self.radius_line.get_right(),
            self.radius_line.get_right() + self.dR*RIGHT,
            color = self.radius_line.get_color()
        )
        nudge_arrow = Arrow(
            nudge_line.get_center() + 0.5*RIGHT+DOWN,
            nudge_line.get_center(),
            color = YELLOW,
            buff = SMALL_BUFF,
            tip_length = 0.2,
        )
        nudge_label = TexMobject("%.01f"%self.dR)
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
        )
        self.dither()
        self.nudge_line = nudge_line
        self.nudge_arrow = nudge_arrow
        self.nudge_label = nudge_label
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
            self.get_unwrapped(ring)
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

    def get_unwrapped(self, ring):
        R = ring.R
        R_plus_dr = ring.R + ring.dR
        n_anchors = ring.get_num_anchor_points()
        result = VMobject()
        result.set_points_as_corners([
            interpolate(np.pi*R_plus_dr*LEFT,  np.pi*R_plus_dr*RIGHT, a)
            for a in np.linspace(0, 1, n_anchors/2)
        ]+[
            interpolate(np.pi*R*RIGHT+self.dR*UP,  np.pi*R*LEFT+self.dR*UP, a)
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
        result.to_edge(LEFT)

        return result

######################

class OpeningQuote(Scene):
    CONFIG = {
        "quote" : """
            The art of doing mathematics is finding 
            that special case that contains all the 
            germs of generality.
        """,
        "author" : "David Hilbert"
    }
    def construct(self):
        quote = self.get_quote()
        author = self.get_author(quote)

        self.play(FadeIn(
            quote,
            submobject_mode = "lagged_start",
            run_time = 2
        ))
        self.dither(2)
        self.play(Write(author, run_time = 4))
        self.dither()

    def get_quote(self):
        quote = TextMobject(
            "``%s''"%self.quote.strip(),
            alignment = "",
        )
        quote.to_edge(UP)
        return quote

    def get_author(self, quote):
        author = TextMobject("-" + self.author)
        author.next_to(quote, DOWN)
        author.highlight(YELLOW)
        return author

class Introduction(TeacherStudentsScene):
    def construct(self):
        self.show_series()
        self.go_through_students()
        self.zoom_in_on_first()

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
        self.remove(self.teacher)
        self.teacher.change_mode("happy")
        self.add(self.teacher)
        self.play(
            FadeIn(
                series,
                submobject_mode = "lagged_start",
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
                for pi in self.get_everyone()
            ]
        )
        def homotopy(x, y, z, t):
            alpha = (0.7*x + SPACE_WIDTH)/(2*SPACE_WIDTH)
            beta = squish_rate_func(smooth, alpha-0.15, alpha+0.15)(t)
            return (x, y - 0.3*np.sin(np.pi*beta), z)
        self.play(
            Homotopy(
                homotopy, series, 
                apply_function_kwargs = {"maintain_smoothness" : False},
            ),
            *[
                ApplyMethod(pi.look_at, series[-1])
                for pi in self.get_everyone()
            ],
            run_time = 5
        )
        self.play(
            FadeOut(self.teacher.bubble),
            FadeOut(self.teacher.bubble.content),
            *[
                ApplyMethod(pi.change_mode, "happy")
                for pi in self.get_everyone()
            ]
        )

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
        cant_wait = TextMobject("I litterally \\\\ can't wait")
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
            submobject_mode = "lagged_start",
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
        self.dither()

    def zoom_in_on_first(self):
        this_video = self.this_video
        self.remove(this_video)
        this_video.generate_target()
        this_video.target.scale_to_fit_height(2*SPACE_HEIGHT)
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
        radius.highlight(MAROON_B)
        R = TexMobject("R").next_to(radius, UP)

        area, circumference = words = VGroup(*map(TextMobject, [
            "Area =", "Circumference ="
        ]))
        area.highlight(BLUE)
        circumference.highlight(YELLOW)

        words.arrange_submobjects(DOWN, aligned_edge = LEFT)
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
        calc_stuffs.arrange_submobjects(DOWN)
        calc_stuffs.next_to(words, DOWN, buff = LARGE_BUFF, aligned_edge = LEFT)

        brace = Brace(calc_stuffs, RIGHT)
        to_be_explained = brace.get_text("To be \\\\ explained")
        VGroup(brace, to_be_explained).highlight(GREEN)

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
        self.dither()
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
        self.dither()
        self.play(
            area_form.copy().replace, derivative[1],
            circum_form.copy().replace, derivative[3],
            Write(derivative[0]),
            Write(derivative[2]),
            run_time = 1
        )
        self.dither()
        self.play(
            area_form.copy().replace, integral[3],
            Transform(circum_form.copy(), integral[1]),
            Write(integral[0]),
            Write(integral[2]),
            run_time = 1
        )
        self.dither()
        self.play(Write(up_down_arrow))
        self.dither()
        self.play(
            GrowFromCenter(brace),
            Write(to_be_explained)
        )
        self.dither()

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
        circle_group.arrange_submobjects()
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
        VGroup(*new_area_form[4:7]).highlight(self.dR_color)
        expression_brace = Brace(expression, UP)
        change_in_area = expression_brace.get_text("Change in area")
        change_in_area.highlight(self.outer_ring_color)
        area_brace = Brace(area_form)
        area_word = area_brace.get_text("Area")
        area_word.highlight(BLUE)
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
        self.dither()
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
        self.dither(2)
        self.play(
            group.fade, 0.7,
            self.pi_creature.change_mode, "happy"
        )
        self.dither()
        self.play(
            outer_ring.highlight, YELLOW,
            Animation(self.nudge_arrow),
            Animation(self.nudge_line),
            rate_func = there_and_back
        )
        self.show_unwrapping(outer_ring)
        self.play(group.restore)
        self.work_out_expression(group)
        self.second_unwrapping(outer_ring)
        insignificant = TextMobject("Insignificant")
        insignificant.highlight(self.dR_color)
        insignificant.move_to(self.error_words)
        self.play(Transform(self.error_words, insignificant))
        self.dither()

        big_rect = Rectangle(
            width = 2*SPACE_WIDTH,
            height = 2*SPACE_HEIGHT,
            fill_color = BLACK, 
            fill_opacity = 0.85,
            stroke_width = 0,
        )
        self.play(
            FadeIn(big_rect),
            area_form.highlight, BLUE,
            self.two_pi_R.highlight, GREEN,
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
        dR.highlight(self.dR_color)

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
        final_area.arrange_submobjects(RIGHT, buff = SMALL_BUFF)
        final_area.next_to(almost_rect, DOWN, buff = 2*MED_BUFF)
        final_area.highlight(GREEN_A)
        final_area[3].highlight(self.dR_color)
        change_in_area.shift(0.1*LEFT)

        self.play(
            GrowFromCenter(circum_brace),
            Write(two_pi_R)
        )
        self.dither()
        self.play(
            GrowFromCenter(dR_brace),
            Write(dR)
        )
        self.dither()
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
        self.dither()
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
            VGroup(*subset).highlight(self.dR_color)
        expanded.next_to(new_area_form, DOWN, aligned_edge = LEFT, buff = MED_BUFF)
        expanded.shift(LEFT/2.)

        faders = [area_brace, area_word, new_area_brace, new_area_word]
        self.play(*map(FadeOut, faders))
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
            self.dither()
        self.play(
            Transform(minus.copy(), minus2),
            Transform(area_form.copy(), pi_R_squared2),
        )
        to_remove += self.get_mobjects_from_last_animation()
        self.remove(*to_remove)
        self.add(self.pi_creature, *expanded)
        self.dither(2)
        self.play(*[
            ApplyMethod(mob.highlight, RED)
            for mob in pi_R_squared, pi_R_squared2
        ])
        self.dither()
        self.play(*[
            ApplyMethod(mob.fade, 0.7)
            for mob in plus, pi_R_squared, pi_R_squared2, minus2
        ]) 
        self.dither()

        approx_brace = Brace(two_pi_R_dR)
        error_brace = Brace(pi_dR_squared, buff = SMALL_BUFF)
        error_words = error_brace.get_text("Error", buff = SMALL_BUFF)
        error_words.highlight(RED)
        self.error_words = error_words

        self.play(
            GrowFromCenter(approx_brace),
            self.pi_creature.change_mode, "hooray"
        )
        self.dither()
        self.play(
            GrowFromCenter(error_brace),
            Write(error_words),
            self.pi_creature.change_mode, "confused"
        )
        self.dither()
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
            almost_rect.highlight, YELLOW,
            self.pi_creature.change_mode, "pondering"
        )
        self.unwrap_ring(almost_rect)
        self.dither()
        rect.move_to(almost_rect)
        self.play(FadeIn(rect))
        self.dither()

    def get_pi_creature(self):
        morty = Mortimer()
        morty.scale(0.7)
        morty.to_corner(DOWN+RIGHT)
        return morty

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

    def get_pi_creature(self):
        morty = Mortimer()
        morty.flip()
        morty.to_corner(DOWN+LEFT)
        return morty

    def write_initial_terms(self):
        change = TextMobject("Change in area")
        change.highlight(GREEN_B)
        equals, two_pi_R, dR, plus, pi, dR2, squared = rhs = TexMobject(
            "=", "2 \\pi R", "(0.1)", "+", "\\pi", "(0.1)", "^2"
        )
        VGroup(dR, dR2).highlight(self.dR_color)
        change.next_to(self.circle, buff = LARGE_BUFF)
        rhs.next_to(change)

        circum_brace = Brace(two_pi_R, UP)
        circum_text = circum_brace.get_text("Circumference")
        error_brace = Brace(VGroup(pi, squared), UP)
        error_text = error_brace.get_text("Error")
        error_text.highlight(RED)

        self.play(
            Write(change, run_time = 1),
            self.pi_creature.change_mode, "pondering",
        )
        self.dither()
        self.play(*it.chain(
            map(Write, [equals, two_pi_R, dR]),
            map(FadeIn, [circum_text, circum_brace])
        ))
        self.dither()
        self.play(*it.chain(
            map(Write, [plus, pi, dR2, squared]),
            map(FadeIn, [error_brace, error_text])
        ))
        self.dither(2)
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
            term.denom.highlight(self.dR_color)
            term.denom.save_state()
            term.denom.replace(self.nudge_label)

        self.equals.generate_target()
        self.equals.target.next_to(self.change.frac_line, RIGHT)
        self.plus.generate_target()
        self.plus.target.next_to(self.circum_term.frac_line, RIGHT)

        self.play(*it.chain(
            [Write(term.frac_line) for term in terms],
            map(MoveToTarget, [self.equals, self.plus])
        ))
        self.play(*[term.denom.restore for term in terms])
        self.dither(2)
        canceleres = VGroup(self.circum_term[1], self.circum_term.denom)
        self.play(canceleres.highlight, RED)
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
        self.dither(2)
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
        self.dither()

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
            new_dRs.highlight(self.dR_color)
            new_outer_ring = self.get_ring(self.radius, width)
            new_nudge_line = self.nudge_line.copy()
            new_nudge_line.scale_to_fit_width(width)
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
            self.dither()
            if s == "(0.001)":
                self.plus.generate_target()
                self.plus.target.next_to(self.circum_term)
                self.error_term.generate_target()
                self.error_term.target.next_to(self.plus.target)
                error_brace.target = Brace(self.error_term.target)
                error_text.target = error_brace.target.get_text("Truly tiny")
                error_text.target.highlight(error_text.get_color())
                self.play(*map(MoveToTarget, [
                    error_brace, error_text, self.plus, self.error_term
                ]))
                self.dither()

        difference_text = TextMobject(
            "``Tiny " , "d", "ifference in ", "$R$", "''",
            arg_separator = ""

        )
        difference_text.highlight_by_tex("d", self.dR_color)
        difference_text.next_to(self.pi_creature, UP+RIGHT)
        difference_arrow = Arrow(difference_text, self.change.denom)
        self.play(
            Write(difference_text, run_time = 2),
            ShowCreation(difference_arrow),
            self.pi_creature.change_mode, "speaking"
        )
        self.dither()

        dA = TexMobject("dA")
        dA.highlight(self.change.get_color())
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
            difference_text[1].highlight, dA.get_color(),
            MoveToTarget(difference_arrow),
        )
        self.dither(2)
        self.play(*map(FadeOut, [difference_text, difference_arrow]))

    def elaborate_on_d(self):
        arc = Arc(-np.pi, start_angle = -np.pi/2)
        arc.scale_to_fit_height(
            self.change.get_center()[1]-self.change.denom.get_center()[1]
        )
        arc.next_to(self.change.frac_line, LEFT)
        arc.add_tip()

        self.play(
            ShowCreation(arc),
            self.pi_creature.change_mode, "sassy"
        )
        self.dither()
        self.play(self.pi_creature.shrug)
        self.play(FadeOut(arc))
        self.dither()

        d = TextMobject("``$d$''")
        arrow = TexMobject("\\Rightarrow")
        arrow.next_to(d)
        ignore_error = TextMobject("Ignore error")
        d_group = VGroup(d, arrow, ignore_error)
        d_group.arrange_submobjects()
        d_group.next_to(
            self.pi_creature.get_corner(UP+RIGHT), 
            buff = LARGE_BUFF
        )
        error_group = VGroup(
            self.error_term, self.error_term.label
        )

        self.play(
            Write(d),
            self.pi_creature.change_mode, "speaking"
        )
        self.play(*map(Write, [arrow, ignore_error]))
        self.play(error_group.fade, 0.8)
        self.dither(2)

        less_wrong_philosophy = TextMobject("``Less wrong'' philosophy")
        less_wrong_philosophy.move_to(ignore_error, LEFT)
        self.play(Transform(ignore_error, less_wrong_philosophy))
        self.dither()

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
            rate_func = None,
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
        self.dither()

        to_infs = [self.change, self.change.denom, self.nudge_label]
        for mob in to_infs:
            mob.save_state()
            mob.inf = TexMobject("1/\\infty")
            mob.inf.highlight(mob.get_color())
            mob.inf.move_to(mob)
        self.play(*[
            Transform(mob, mob.inf)
            for mob in to_infs
        ])
        self.dither()
        self.play(self.pi_creature.change_mode, "pleading")
        self.dither()


























