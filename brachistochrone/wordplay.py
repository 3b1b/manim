import numpy as np
import itertools as it
import os

from helpers import *

from mobject.tex_mobject import TexMobject, TextMobject, Brace
from mobject import Mobject
from mobject.image_mobject import \
    MobjectFromRegion, ImageMobject, MobjectFromPixelArray
from topics.three_dimensions import Stars

from animation import Animation
from animation.transform import \
    Transform, CounterclockwiseTransform, ApplyPointwiseFunction,\
    FadeIn, FadeOut, GrowFromCenter, ApplyFunction, ApplyMethod, \
    ShimmerIn
from animation.simple_animations import \
    ShowCreation, Homotopy, PhaseFlow, ApplyToCenters, DelayByOrder, \
    ShowPassingFlash
from animation.playground import TurnInsideOut, Vibrate
from topics.geometry import \
    Line, Circle, Square, Grid, Rectangle, Arrow, Dot, Point, \
    Arc, FilledRectangle
from topics.characters import Randolph, Mathematician
from topics.functions import ParametricFunction, FunctionGraph
from topics.number_line import NumberPlane
from mobject.region import  Region, region_from_polygon_vertices
from scene import Scene
from generate_logo import LogoGeneration
from brachistochrone.drawing_images import sort_by_color

class Intro(Scene):
    def construct(self):
        logo = ImageMobject("LogoGeneration", invert = False)
        name_mob = TextMobject("3Blue1Brown").center()
        name_mob.highlight("grey")
        name_mob.shift(2*DOWN)
        self.add(name_mob, logo)

        new_text = TextMobject(["with ", "Steven Strogatz"])
        new_text.next_to(name_mob, DOWN)
        self.play(*[
            ShimmerIn(part)
            for part in new_text.split()
        ])
        self.dither()
        with_word, steve = new_text.split()
        steve_copy = steve.copy().center().to_edge(UP)
        # logo.sort_points(lambda p : -np.linalg.norm(p))
        sort_by_color(logo)
        self.play(
            Transform(steve, steve_copy),
            DelayByOrder(Transform(logo, Point())),
            FadeOut(with_word),
            FadeOut(name_mob),
            run_time = 3
        )


class IntroduceSteve(Scene):
    def construct(self):
        name = TextMobject("Steven Strogatz")
        name.to_edge(UP)
        contributions = TextMobject("Frequent Contributions")
        contributions.scale(0.5).to_edge(RIGHT).shift(2*UP)
        books_word = TextMobject("Books")
        books_word.scale(0.5).to_edge(LEFT).shift(2*UP)
        radio_lab, sci_fri, cornell, book2, book3, book4 = [
            ImageMobject(filename, invert = False, filter_color = WHITE)
            for filename in [
                "radio_lab",
                "science_friday",
                "cornell",
                "strogatz_book2",
                "strogatz_book3",
                "strogatz_book4",
            ]
        ]
        book1 = ImageMobject("strogatz_book1", invert = False)
        nyt = ImageMobject("new_york_times")
        logos = [radio_lab, nyt, sci_fri]
        books = [book1, book2, book3, book4]

        sample_size = Square(side_length = 2)
        last = contributions        
        for image in logos:
            image.replace(sample_size)
            image.next_to(last, DOWN)
            last = image
        sci_fri.scale_in_place(0.9)
        shift_val = 0
        sample_size.scale(0.75)
        for book in books:
            book.replace(sample_size)
            book.next_to(books_word, DOWN)
            book.shift(shift_val*(RIGHT+DOWN))
            shift_val += 0.5
        sample_size.scale(2)
        cornell.replace(sample_size)
        cornell.next_to(name, DOWN)

        Mobject(*logos+books+[cornell]).show()

        self.add(name)
        self.play(FadeIn(cornell))
        self.play(ShimmerIn(contributions))
        for logo in logos:
            self.play(FadeIn(logo))
        self.play(ShimmerIn(books_word))
        for book in books:
            book.shift(5*LEFT)
            self.play(ApplyMethod(book.shift, 5*RIGHT))
        self.dither()


class DisectBrachistochroneWord(Scene):
    def construct(self):
        word = TextMobject(["Bra", "chis", "to", "chrone"])
        original_word = word.copy()
        dots = []
        for part in word.split():
            if dots:
                part.next_to(dots[-1], buff = 0.06)
            dot = TexMobject("\\cdot")
            dot.next_to(part, buff = 0.06)
            dots.append(dot)
        dots = Mobject(*dots[:-1])
        dots.shift(0.1*DOWN)
        Mobject(word, dots).center()
        overbrace1 = Brace(Mobject(*word.split()[:-1]), UP)
        overbrace2 = Brace(word.split()[-1], UP)
        shortest = TextMobject("Shortest")
        shortest.next_to(overbrace1, UP)
        shortest.highlight(YELLOW)
        time = TextMobject("Time")
        time.next_to(overbrace2, UP)
        time.highlight(YELLOW)
        chrono_example = TextMobject("""
            As in ``Chronological'' \\\\
            or ``Synchronize''
        """)
        chrono_example.scale(0.5)
        chrono_example.to_edge(RIGHT)
        chrono_example.shift(2*UP)
        chrono_example.highlight(BLUE_D)
        chrono_arrow = Arrow(
            word.get_right(), 
            chrono_example.get_bottom(), 
            color = BLUE_D
        )
        brachy_example = TextMobject("As in . . . brachydactyly?")
        brachy_example.scale(0.5)
        brachy_example.to_edge(LEFT)
        brachy_example.shift(2*DOWN)
        brachy_example.highlight(GREEN)
        brachy_arrow = Arrow(
            word.get_left(),
            brachy_example.get_top(), 
            color = GREEN
        )

        pronunciation = TextMobject(["/br", "e", "kist","e","kr$\\bar{o}$n/"])
        pronunciation.split()[1].rotate_in_place(np.pi)
        pronunciation.split()[3].rotate_in_place(np.pi) 
        pronunciation.scale(0.7)
        pronunciation.shift(DOWN)

        latin = TextMobject(list("Latin"))
        greek = TextMobject(list("Greek"))
        for mob in latin, greek:
            mob.to_edge(LEFT)
        question_mark = TextMobject("?").next_to(greek, buff = 0.1)
        stars = Stars().highlight(BLACK)
        stars.scale(0.5).shift(question_mark.get_center())

        self.play(Transform(original_word, word), ShowCreation(dots))
        self.play(ShimmerIn(pronunciation))
        self.dither()
        self.play(
            GrowFromCenter(overbrace1),
            GrowFromCenter(overbrace2)
        )
        self.dither()
        self.play(ShimmerIn(latin))
        self.play(FadeIn(question_mark))
        self.play(Transform(
            latin, greek,
            path_func = counterclockwise_path()
        ))
        self.dither()
        self.play(Transform(question_mark, stars))
        self.remove(stars)
        self.dither()
        self.play(ShimmerIn(shortest))
        self.play(ShimmerIn(time))
        for ex, ar in [(chrono_example, chrono_arrow), (brachy_example, brachy_arrow)]:
            self.play(
                ShowCreation(ar),
                ShimmerIn(ex)
            )
        self.dither()


class FermatsPrincipleStatement(Scene):
    def construct(self):
        words = TextMobject([
            "Fermat's principle:",
            """
            If a beam of light travels
            from point $A$ to $B$, it does so along the 
            fastest path possible.
            """
        ])
        words.split()[0].highlight(BLUE)
        everything = MobjectFromRegion(Region())
        everything.scale(0.9)
        angles = np.apply_along_axis(
            angle_of_vector, 1, everything.points
        )
        norms = np.apply_along_axis(
            np.linalg.norm, 1, everything.points
        )
        norms -= np.min(norms)
        norms /= np.max(norms)
        alphas = 0.25 + 0.75 * norms * (1 + np.sin(12*angles))/2
        everything.rgbs = alphas.repeat(3).reshape((len(alphas), 3))

        Mobject(everything, words).show()

        everything.sort_points(np.linalg.norm)        
        self.add(words)
        self.play(
            DelayByOrder(FadeIn(everything, run_time = 3)),
            Animation(words)
        )
        self.play(
            ApplyMethod(everything.highlight, WHITE),
        )
        self.dither()

class VideoProgression(Scene):
    def construct(self):
        all_topics = [
            TextMobject(word, size = "\\Huge")
            for word in [
                "Brachistochrone",
                "Light through \\\\ multilayered glass",
                "Light from \\\\ air into glass",
                "Lifeguard problem",
                "Springs and rod",
                "Snell's Law",
                "Cycloid",
                "Mark Levi's cleverness",
            ]
        ]
        brachy, multi_glass, bi_glass, lifeguard, springs, \
        snell, cycloid, levi = all_topics
        positions = [
            (multi_glass, brachy, DOWN, "both"),
            (bi_glass, multi_glass, LEFT, "to"),
            (lifeguard, bi_glass, UP, "both"),
            (springs, bi_glass, DOWN, "both"),
            (snell, springs, RIGHT, "from"),
            (cycloid, multi_glass, RIGHT, "from"),
            (cycloid, snell, UP+RIGHT, "from"),
            (levi, cycloid, UP, "to"),
        ]
        arrows = []
        for mob1, mob2, direction, arrow_type in positions:
            hasarrow = hasattr(mob1, "arrow")
            if not hasarrow:
                mob1.next_to(mob2, direction, buff = 3)
            arrow = Arrow(mob1, mob2)
            if arrow_type in ["to", "from"]:
                arrow.highlight(GREEN)
            if arrow_type == "from":
                arrow.rotate_in_place(np.pi)
            elif arrow_type == "both":
                arrow.highlight(BLUE_D)
                arrow.add(arrow.copy().rotate_in_place(np.pi))
            arrows.append(arrow)
            if hasarrow:
                mob1.arrow.add(arrow)
            else:
                mob1.arrow = arrow
        everything = Mobject(*all_topics+arrows)
        everything.scale(0.7)
        everything.center()
        everything.to_edge(UP)
        everything.show()

        self.add(brachy)
        for mob in all_topics[1:]:
            self.play(ApplyMethod(mob.highlight, YELLOW))
            self.play(ShowCreation(mob.arrow))
            self.dither()
            mob.highlight(WHITE)














