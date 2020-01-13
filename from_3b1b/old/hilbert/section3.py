from manimlib.imports import *
import displayer as disp

from hilbert.curves import \
    TransformOverIncreasingOrders, FlowSnake, HilbertCurve, \
    SnakeCurve, Sierpinski
from hilbert.section1 import get_mathy_and_bubble




class SectionThree(Scene):
    def construct(self):
        self.add(TextMobject("A few words on the usefulness of infinite math"))
        self.wait()


class InfiniteResultsFiniteWorld(Scene):
    def construct(self):
        left_words = TextMobject("Infinite result")
        right_words = TextMobject("Finite world")
        for words in left_words, right_words:
            words.scale(0.8)
        left_formula = TexMobject(
            "\\sum_{n = 0}^{\\infty} 2^n = -1"
        )
        right_formula = TexMobject("111\\cdots111")
        for formula in left_formula, right_formula:
            formula.add(
                Brace(formula, UP),
            )
            formula.ingest_submobjects()
        right_overwords = TextMobject(
            "\\substack{\
                \\text{How computers} \\\\ \
                \\text{represent $-1$}\
            }"
        ).scale(1.5)

        left_mobs = [left_words, left_formula]
        right_mobs = [right_words, right_formula]
        for mob in left_mobs:
            mob.to_edge(RIGHT, buff = 1)
            mob.shift(FRAME_X_RADIUS*LEFT)
        for mob in right_mobs:
            mob.to_edge(LEFT, buff = 1)
            mob.shift(FRAME_X_RADIUS*RIGHT)
        arrow = Arrow(left_words, right_words)
        right_overwords.next_to(right_formula, UP)

        self.play(ShimmerIn(left_words))
        self.play(ShowCreation(arrow))
        self.play(ShimmerIn(right_words))
        self.wait()
        self.play(
            ShimmerIn(left_formula),
            ApplyMethod(left_words.next_to, left_formula, UP)
        )
        self.wait()
        self.play(
            ShimmerIn(right_formula),
            Transform(right_words, right_overwords)
        )
        self.wait()
        self.finite_analog(
            Mobject(left_formula, left_words),
            arrow,
            Mobject(right_formula, right_words)
        )


    def finite_analog(self, left_mob, arrow, right_mob):
        self.clear()
        self.add(left_mob, arrow, right_mob)
        ex = TextMobject("\\times")
        ex.set_color(RED)
        # ex.shift(arrow.get_center())
        middle = TexMobject(
            "\\sum_{n=0}^N 2^n \\equiv -1 \\mod 2^{N+1}"
        )
        finite_analog = TextMobject("Finite analog")
        finite_analog.scale(0.8)
        brace = Brace(middle, UP)
        finite_analog.next_to(brace, UP)
        new_left = left_mob.copy().to_edge(LEFT)
        new_right = right_mob.copy().to_edge(RIGHT)
        left_arrow, right_arrow = [
            Arrow(
                mob1.get_right()[0]*RIGHT,
                mob2.get_left()[0]*RIGHT,
                buff = 0
            )
            for mob1, mob2 in [
                (new_left, middle), 
                (middle, new_right)
            ]
        ]
        for mob in ex, middle:
            mob.sort_points(get_norm)

        self.play(GrowFromCenter(ex))
        self.wait()
        self.play(
            Transform(left_mob, new_left),
            Transform(arrow.copy(), left_arrow),
            DelayByOrder(Transform(ex, middle)),
            Transform(arrow, right_arrow),
            Transform(right_mob, new_right)
        )
        self.play(
            GrowFromCenter(brace),
            ShimmerIn(finite_analog)
        )
        self.wait()
        self.equivalence(
            left_mob,
            left_arrow, 
            Mobject(middle, brace, finite_analog)
        )

    def equivalence(self, left_mob, arrow, right_mob):
        self.clear()
        self.add(left_mob, arrow, right_mob)
        words = TextMobject("is equivalent to")
        words.shift(0.25*LEFT)
        words.set_color(BLUE)
        new_left = left_mob.copy().shift(RIGHT)
        new_right = right_mob.copy()
        new_right.shift(
            (words.get_right()[0]-\
             right_mob.get_left()[0]+\
             0.5
            )*RIGHT
        )
        for mob in arrow, words:
            mob.sort_points(get_norm)     

        self.play(
            ApplyMethod(left_mob.shift, RIGHT),
            Transform(arrow, words),
            ApplyMethod(right_mob.to_edge, RIGHT)
        )
        self.wait()


class HilbertCurvesStayStable(Scene):
    def construct(self):
        scale_factor = 0.9
        grid = Grid(4, 4, stroke_width = 1)
        curve = HilbertCurve(order = 2)
        for mob in grid, curve:
            mob.scale(scale_factor)
        words = TextMobject("""
            Sequence of curves is stable 
            $\\leftrightarrow$ existence of limit curve
        """, size = "\\normal")
        words.scale(1.25)
        words.to_edge(UP)

        self.add(curve, grid)
        self.wait()
        for n in range(3, 7):
            if n == 5:
                self.play(ShimmerIn(words))
            new_grid = Grid(2**n, 2**n, stroke_width = 1)
            new_curve = HilbertCurve(order = n)
            for mob in new_grid, new_curve:
                mob.scale(scale_factor)
            self.play(
                ShowCreation(new_grid),
                Animation(curve)
            )
            self.remove(grid)
            grid = new_grid
            self.play(Transform(curve, new_curve))
            self.wait()



class InfiniteObjectsEncapsulateFiniteObjects(Scene):
    def get_triangles(self):
        triangle = Polygon(
            LEFT/np.sqrt(3),
            UP,
            RIGHT/np.sqrt(3),
            color = GREEN
        )
        triangles = Mobject(
            triangle.copy().scale(0.5).shift(LEFT),
            triangle,
            triangle.copy().scale(0.3).shift(0.5*UP+RIGHT)
        )
        triangles.center()
        return triangles

    def construct(self):
        words =[
            TextMobject(text, size = "\\large")
            for text in [
                "Truths about infinite objects", 
                " encapsulate ", 
                "facts about finite objects"
            ]
        ]
        
        words[0].set_color(RED)
        words[1].next_to(words[0])
        words[2].set_color(GREEN).next_to(words[1])
        Mobject(*words).center().to_edge(UP)
        infinite_objects = [
            TexMobject(
                "\\sum_{n=0}^\\infty", 
                size = "\\normal"
            ).set_color(RED_E),
            Sierpinski(order = 8).scale(0.3),
            TextMobject(
                "$\\exists$ something infinite $\\dots$"
            ).set_color(RED_B)
        ]
        finite_objects = [
            TexMobject(
                "\\sum_{n=0}^N",
                size = "\\normal"
            ).set_color(GREEN_E),
            self.get_triangles(),
            TextMobject(
                "$\\forall$ finite somethings $\\dots$"
            ).set_color(GREEN_B)
        ]
        for infinite, finite, n in zip(infinite_objects, finite_objects, it.count(1, 2)):
            infinite.next_to(words[0], DOWN, buff = n)
            finite.next_to(words[2], DOWN, buff = n)

        self.play(ShimmerIn(words[0]))
        self.wait()
        self.play(ShimmerIn(infinite_objects[0]))
        self.play(ShowCreation(infinite_objects[1]))
        self.play(ShimmerIn(infinite_objects[2]))
        self.wait()
        self.play(ShimmerIn(words[1]), ShimmerIn(words[2]))
        self.play(ShimmerIn(finite_objects[0]))
        self.play(ShowCreation(finite_objects[1]))
        self.play(ShimmerIn(finite_objects[2]))
        self.wait()


class StatementRemovedFromReality(Scene):
    def construct(self):
        mathy, bubble = get_mathy_and_bubble()
        bubble.stretch_to_fit_width(4)
        mathy.to_corner(DOWN+LEFT)
        bubble.pin_to(mathy)
        bubble.shift(LEFT)
        morty = Mortimer()
        morty.to_corner(DOWN+RIGHT)
        morty_bubble = SpeechBubble()
        morty_bubble.stretch_to_fit_width(4)
        morty_bubble.pin_to(morty)
        bubble.write("""
            Did you know a curve \\\\
            can fill all space?
        """)
        morty_bubble.write("Who cares?")

        self.add(mathy, morty)
        for bub, buddy in [(bubble, mathy), (morty_bubble, morty)]:
            self.play(Transform(
                Point(bub.get_tip()),
                bub
            ))
            self.play(ShimmerIn(bub.content))
            self.play(ApplyMethod(
                buddy.blink,
                rate_func = squish_rate_func(there_and_back)
            ))








