from mobject import Mobject, Point
from mobject.tex_mobject import TexMobject, TextMobject, Brace
from mobject.image_mobject import ImageMobject

from scene import Scene

from animation import Animation
from animation.transform import Transform, CounterclockwiseTransform, \
                                ApplyMethod, GrowFromCenter
from animation.simple_animations import ShowCreation, ShimmerIn
from animation.meta_animations import DelayByOrder, TransformAnimations
from animation.playground import VibratingString

from topics.geometry import Line, Dot, Arrow
from topics.characters import ThoughtBubble
from topics.number_line import UnitInterval


from helpers import *
from hilbert.curves import TransformOverIncreasingOrders, FlowSnake



class AboutSpaceFillingCurves(TransformOverIncreasingOrders):
    @staticmethod
    def args_to_string():
        return ""

    @staticmethod
    def string_to_args(arg_str):
        return ()

    def construct(self):
        self.bubble = ThoughtBubble().ingest_sub_mobjects()
        self.bubble.scale(1.5)

        TransformOverIncreasingOrders.construct(self, FlowSnake, 7)
        self.play(Transform(self.curve, self.bubble))
        self.show_infinite_objects()
        self.pose_question()
        self.dither()

    def show_infinite_objects(self):
        sigma, summand, equals, result = TexMobject([
            "\\sum_{n = 1}^{\\infty}",
            "\\dfrac{1}{n^2}",
            "=",
            "\\dfrac{\pi^2}{6}"
        ]).split()
        alt_summand = TexMobject("n").replace(summand)
        alt_result = TexMobject("-\\dfrac{1}{12}").replace(result)

        rationals, other_equals, naturals = TexMobject([
            "|\\mathds{Q}|",
            "=",
            "|\\mathds{N}|"
        ]).scale(2).split()
        infinity = TexMobject("\\infty").scale(2)
        local_mobjects = filter(
            lambda m : isinstance(m, Mobject),
            locals().values(),
        )
        for mob in local_mobjects:    
            mob.sort_points(np.linalg.norm)

        self.play(ShimmerIn(infinity))
        self.dither()
        self.play(
            ShimmerIn(summand),
            ShimmerIn(equals),
            ShimmerIn(result),
            DelayByOrder(Transform(infinity, sigma))
        )
        self.dither()
        self.play(
            Transform(summand, alt_summand),
            Transform(result, alt_result),
        )
        self.dither()
        self.remove(infinity)
        self.play(*[
            CounterclockwiseTransform(
                Mobject(summand, equals, result, sigma),
                Mobject(rationals, other_equals, naturals)
            )
        ])
        self.dither()
        self.clear()
        self.add(self.bubble)

    def pose_question(self):
        infinity, rightarrow, N = TexMobject([
            "\\infty", "\\rightarrow", "N"
        ]).scale(2).split()
        question_mark = TextMobject("?").scale(2)

        self.add(question_mark)
        self.dither()
        self.play(*[
            ShimmerIn(mob)
            for mob in infinity, rightarrow, N
        ] + [
            ApplyMethod(question_mark.next_to, rightarrow, UP),
        ])
        self.dither()




class PostponePhilosophizing(Scene):
    def construct(self):
        abstract, arrow, concrete = TextMobject([
            "Abstract", " $\\rightarrow$ ", "Concrete"
        ]).scale(2).split()

        self.add(abstract, arrow, concrete)
        self.dither()
        self.play(*[
            ApplyMethod(
                word1.replace, word2,
                interpolation_function = path_along_arc(np.pi/2)
            )
            for word1, word2 in it.permutations([abstract, concrete])
        ])
        self.dither()

class WriteSomeSoftware(Scene):
    pass #Done viea screen capture, written here for organization



class ImageToSound(Scene):
    def construct(self):
        string = VibratingString(color = BLUE_D, run_time = 5)
        picture = ImageMobject("lion", invert = False)
        picture.scale(0.8)
        picture_copy = picture.copy()
        picture.sort_points(np.linalg.norm)
        string.mobject.sort_points(lambda p : -np.linalg.norm(p))

        self.add(picture)
        self.dither()
        self.play(Transform(
            picture, string.mobject,
            run_time = 3,
            alpha_func = rush_into
        ))
        self.remove(picture)
        self.play(string)

        for mob in picture_copy, string.mobject:
            mob.sort_points(lambda p : np.linalg.norm(p)%1)

        self.play(Transform(
            string.mobject, picture_copy,
            run_time = 5,
            alpha_func = rush_from
        ))


class ImageDataIsTwoDimensional(Scene):
    def construct(self):
        image = ImageMobject("lion", invert = False)
        image.scale(0.5)
        image.shift(2*LEFT)

        self.add(image)
        for vect, num in zip([DOWN, RIGHT], [1, 2]):
            brace = Brace(image, vect)
            words_mob = TextMobject("Dimension %d"%num)
            words_mob.next_to(image, vect, buff = 1)
            self.play(
                Transform(Point(brace.get_center()), brace),
                ShimmerIn(words_mob), 
                run_time = 2
            )
        self.dither()


class SoundDataIsOneDimensional(Scene):
    def construct(self):
        overtones = 5
        floor = 2*DOWN
        main_string = VibratingString(color = BLUE_D)
        component_strings = [
            VibratingString(
                num_periods = k+1,
                overtones = 2,
                color = color,
                center = 2*DOWN + UP*k
            )
            for k, color in zip(
                range(overtones),
                Color(BLUE_E).range_to(WHITE, overtones)
            )
        ]
        dots = [
            Dot(
                string.mobject.get_center(),
                color = string.mobject.get_color()
            )
            for string in component_strings
        ]

        freq_line = UnitInterval()
        freq_line.shift(floor)
        freq_line.sort_points(np.linalg.norm)
        brace = Brace(freq_line, UP)
        words = TextMobject("Range of frequency values")
        words.next_to(brace, UP)


        self.play(*[
            TransformAnimations(
                main_string.copy(),
                string,
                run_time = 5
            )
            for string in component_strings
        ])
        self.clear()
        self.play(*[
            TransformAnimations(
                string,
                Animation(dot)
            )
            for string, dot in zip(component_strings, dots)
        ])
        self.clear()
        self.play(
            ShowCreation(freq_line),
            GrowFromCenter(brace),
            ShimmerIn(words),
            *[
                Transform(
                    dot,
                    dot.copy().scale(2).rotate(-np.pi/2).shift(floor),
                    interpolation_function = path_along_arc(np.pi/3)
                )
                for dot in dots
            ]
        )
        self.dither(0.5)



















