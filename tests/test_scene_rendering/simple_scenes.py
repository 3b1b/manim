from manim import *


class SquareToCircle(Scene):
    def construct(self):
        square = Square()
        circle = Circle()
        self.play(Transform(square, circle))


class SceneWithMultipleCalls(Scene):
    def construct(self):
        number = Integer(0)
        self.add(number)
        for i in range(10):
            number.become(Integer(i))
            self.play(Animation(number))


class SceneWithMultipleWaitCalls(Scene):
    def construct(self):
        self.play(ShowCreation(Square()))
        self.wait(1)
        self.play(ShowCreation(Square().shift(DOWN)))
        self.wait(1)
        self.play(ShowCreation(Square().shift(2 * DOWN)))
        self.wait(1)
        self.play(ShowCreation(Square().shift(3 * DOWN)))
        self.wait(1)


class NoAnimations(Scene):
    def construct(self):
        dot = Dot().set_color(GREEN)
        self.add(dot)
        self.wait(1)
