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
        pi_R, pre_squared = TexMobject("\\pi R", "{}^2")
        squared = TexMobject("2").replace(pre_squared)
        area_form = VGroup(pi_R, squared)
        area_form.next_to(area, RIGHT)
        two, pi_R = TexMobject("2", "\\pi R")
        circum_form = VGroup(pi_R, two)
        circum_form.next_to(circumference, RIGHT)

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





























