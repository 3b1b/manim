from manimlib.imports import *
from old_projects.hilbert.curves import *

class Intro(TransformOverIncreasingOrders):
    @staticmethod
    def args_to_string(*args):
        return ""
        
    @staticmethod
    def string_to_args(string):
        raise Exception("string_to_args Not Implemented!")

    def construct(self):
        words1 = TextMobject(
            "If you watched my video about Hilbert's space-filling curve\\dots"
        )
        words2 = TextMobject(
            "\\dots you might be curious to see what a few other space-filling curves look like."
        )
        words2.scale(0.8)
        for words in words1, words2:
            words.to_edge(UP, buff = 0.2)

        self.setup(HilbertCurve)
        self.play(ShimmerIn(words1))
        for x in range(4):
            self.increase_order()
        self.remove(words1)
        self.increase_order(
            ShimmerIn(words2)
        )
        for x in range(4):
            self.increase_order()



class BringInPeano(Intro):
    def construct(self):
        words1 = TextMobject("""
            For each one, see if you can figure out what
            the pattern of construction is.
        """)
        words2 = TextMobject("""
            This one is the Peano curve.
        """)
        words3 = TextMobject("""
            It is the original space-filling curve.
        """)
        self.setup(PeanoCurve)
        self.play(ShimmerIn(words1))
        self.wait(5)
        self.remove(words1)
        self.add(words2.to_edge(UP))
        for x in range(3):
            self.increase_order()
        self.remove(words2)
        self.increase_order(ShimmerIn(words3.to_edge(UP)))
        for x in range(2):
            self.increase_order()


class FillOtherShapes(Intro):
    def construct(self):
        words1 = TextMobject("""
            But of course, there's no reason we should limit 
            ourselves to filling in squares.
        """)
        words2 = TextMobject("""
            Here's a simple triangle-filling curve I defined
            in a style reflective of a Hilbert curve.
        """)
        words1.to_edge(UP)
        words2.scale(0.8).to_edge(UP, buff = 0.2)

        self.setup(TriangleFillingCurve)
        self.play(ShimmerIn(words1))
        for x in range(3):
            self.increase_order()
        self.remove(words1)
        self.add(words2)
        for x in range(5):
            self.increase_order()

class SmallerFlowSnake(FlowSnake):
    CONFIG = {
        "radius" : 4
    }

class MostDelightfulName(Intro):
    def construct(self):
        words1 = TextMobject("""
            This one has the most delightful name, 
            thanks to mathematician/programmer Bill Gosper:
        """)
        words2 = TextMobject("``Flow Snake''")
        words3 = TextMobject("""
            What makes this one particularly interesting
            is that the boundary itself is a fractal.
        """)
        for words in words1, words2, words3:
            words.to_edge(UP)

        self.setup(SmallerFlowSnake)
        self.play(ShimmerIn(words1))
        for x in range(3):
            self.increase_order()
        self.remove(words1)
        self.add(words2)
        for x in range(3):
            self.increase_order()
        self.remove(words2)
        self.play(ShimmerIn(words3))



class SurpriseFractal(Intro):
    def construct(self):
        words = TextMobject("""
            It might come as a surprise how some well-known
            fractals can be described with curves.
        """)
        words.to_edge(UP)

        self.setup(Sierpinski)
        self.add(TextMobject("Speaking of other fractals\\dots"))
        self.wait(3)
        self.clear()
        self.play(ShimmerIn(words))
        for x in range(9):
            self.increase_order()


class IntroduceKoch(Intro):
    def construct(self):
        words = list(map(TextMobject, [
            "This is another famous fractal.",
            "The ``Koch Snowflake''",
            "Let's finish things off by seeing how to turn \
            this into a space-filling curve"
        ]))
        for text in words:
            text.to_edge(UP)

        self.setup(KochCurve)
        self.add(words[0])
        for x in range(3):
            self.increase_order()
        self.remove(words[0])
        self.add(words[1])
        for x in range(4):
            self.increase_order()
        self.remove(words[1])
        self.add(words[2])
        self.wait(6)

class StraightKoch(KochCurve):
    CONFIG = {
        "axiom" : "A"
    }

class SharperKoch(StraightKoch):
    CONFIG = {
        "angle" : 0.9*np.pi/2,
    }

class DullerKoch(StraightKoch):
    CONFIG = {
        "angle" : np.pi/6,
    }

class SpaceFillingKoch(StraightKoch):
    CONFIG = {
        "angle" : np.pi/2,
    }



class FromKochToSpaceFilling(Scene):
    def construct(self):
        self.max_order = 7

        self.revisit_koch()
        self.show_angles()
        self.show_change_side_by_side()


    def revisit_koch(self):
        words = list(map(TextMobject, [
            "First, look at how one section of this curve is made.",
            "This pattern of four lines is the ``seed''",
            "With each iteration, every straight line is \
            replaced with an appropriately small copy of the seed",
        ]))
        for text in words:
            text.to_edge(UP)

        self.add(words[0])
        curve = StraightKoch(order = self.max_order)
        self.play(Transform(
            curve,
            StraightKoch(order = 1),
            run_time = 5
        ))
        self.remove(words[0])
        self.add(words[1])
        self.wait(4)
        self.remove(words[1])
        self.add(words[2])
        self.wait(3)
        for order in range(2, self.max_order):
            self.play(Transform(
                curve,
                StraightKoch(order = order)
            ))
            if order == 2:
                self.wait(2)
            elif order == 3:
                self.wait()
        self.clear()



    def show_angles(self):
        words = TextMobject("""
            Let's see what happens as we change
            the angle in this seed
        """)
        words.to_edge(UP)
        koch, sharper_koch, duller_koch = curves = [
            CurveClass(order = 1)
            for CurveClass in (StraightKoch, SharperKoch, DullerKoch)
        ]
        arcs = [
            Arc(
                2*(np.pi/2 - curve.angle),
                radius = r,
                start_angle = np.pi+curve.angle
            ).shift(curve.points[curve.get_num_points()/2])
            for curve, r in zip(curves, [0.6, 0.7, 0.4])
        ]
        theta = TexMobject("\\theta")
        theta.shift(arcs[0].get_center()+2.5*DOWN)
        arrow = Arrow(theta, arcs[0])

        self.add(words, koch)
        self.play(ShowCreation(arcs[0]))
        self.play(
            ShowCreation(arrow),
            ShimmerIn(theta)
        )
        self.wait(2)
        self.remove(theta, arrow)
        self.play(
            Transform(koch, duller_koch),
            Transform(arcs[0], arcs[2]),
        )
        self.play(
            Transform(koch, sharper_koch),
            Transform(arcs[0], arcs[1]),
        )
        self.clear()        

    def show_change_side_by_side(self):

        seed = TextMobject("Seed")
        seed.shift(3*LEFT+2*DOWN)
        fractal = TextMobject("Fractal")
        fractal.shift(3*RIGHT+2*DOWN)
        words = list(map(TextMobject, [
            "A sharper angle results in a richer curve",
            "A more obtuse angle gives a sparser curve",
            "And as the angle approaches 0\\dots",
            "We have a new space-filling curve."
        ]))
        for text in words:
            text.to_edge(UP)
        sharper, duller, space_filling = [
            CurveClass(order = 1).shift(3*LEFT)
            for CurveClass in (SharperKoch, DullerKoch, SpaceFillingKoch)
        ]
        shaper_f, duller_f, space_filling_f = [
            CurveClass(order = self.max_order).shift(3*RIGHT)
            for CurveClass in (SharperKoch, DullerKoch, SpaceFillingKoch)
        ]

        self.add(words[0])
        left_curve = SharperKoch(order = 1)
        right_curve = SharperKoch(order = 1)
        self.play(
            Transform(left_curve, sharper),
            ApplyMethod(right_curve.shift, 3*RIGHT),
        )
        self.play(
            Transform(
                right_curve,
                SharperKoch(order = 2).shift(3*RIGHT)
            ),
            ShimmerIn(seed),
            ShimmerIn(fractal)
        )
        for order in range(3, self.max_order):
            self.play(Transform(
                right_curve,
                SharperKoch(order = order).shift(3*RIGHT)
            ))
        self.remove(words[0])
        self.add(words[1])
        kwargs = {
            "run_time" : 4,
        }
        self.play(
            Transform(left_curve, duller, **kwargs),
            Transform(right_curve, duller_f, **kwargs)
        )
        self.wait()
        kwargs["run_time"] = 7
        kwargs["rate_func"] = None
        self.remove(words[1])
        self.add(words[2])
        self.play(
            Transform(left_curve, space_filling, **kwargs),
            Transform(right_curve, space_filling_f, **kwargs)
        )
        self.remove(words[2])
        self.add(words[3])
        self.wait()












