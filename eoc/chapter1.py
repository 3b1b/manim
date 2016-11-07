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

class CircleScene(Scene):
    CONFIG = {
        "radius" : 1.5,
        "stroke_color" : WHITE,
        "fill_color" : BLUE_E,
        "fill_opacity" : 0.5,
        "radial_line_color" : MAROON_B,
        "outer_ring_color" : GREEN_E,
        "dR" : 0.1,
        "unwrapped_tip" : ORIGIN,
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
        self.radius_label = self.radius_brace.get_text("R", buff = SMALL_BUFF)

        self.add(
            self.circle, self.radius_line, 
            self.radius_brace, self.radius_label
        )

    def introduce_circle(self):
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
            buff = 0.025,
            tip_length = 0.2,
        )
        nudge_label = TexMobject("%.01f"%self.dR)
        nudge_label.scale(0.75)
        nudge_label.next_to(nudge_arrow.get_start(), DOWN)

        radius_mobs.add(nudge_line, nudge_arrow, nudge_label)

        outer_ring = self.get_outer_ring()

        self.play(ShowCreation(nudge_line))
        self.play(
            ShowCreation(nudge_arrow),
            Write(nudge_label)
        )
        self.dither()
        self.play(
            FadeIn(outer_ring),
            *map(Animation, radius_mobs)
        )
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

    def unwrap_ring(self, ring):
        self.unwrap_rings(ring)

    def unwrap_rings(self, *rings):
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
        self.play(Transform(
            rings, unwrapped, 
            run_time = 3,
        ))

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

class IntroduceTinyChangeInArea(CircleScene):
    def construct(self):
        new_area_form, minus area_form = expression = TexMobject(
            "\\pi (R + 0.1)^2", "-", "\\pi R^2"
        )
        expression.to_corner(UP+RIGHT, buff = 2*MED_BUFF)

        self.introduce_circle()
        self.dither()
        outer_ring = self.increase_radius()
        self.dither()
        # ring = self.get_outer_ring()






























