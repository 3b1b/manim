from mobject import Mobject, Point
from mobject.tex_mobject import TexMobject, TextMobject
from mobject.image_mobject import ImageMobject

from scene import Scene

from animation import Animation
from animation.transform import Transform, CounterclockwiseTransform, ApplyMethod
from animation.simple_animations import ShowCreation, ShimmerIn
from animation.meta_animations import DelayByOrder, TransformAnimations
from animation.playground import VibratingString

from topics.geometry import Line
from topics.characters import ThoughtBubble


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
        picture.scale(0.5)
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




