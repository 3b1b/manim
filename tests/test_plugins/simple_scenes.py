from manim import *


class SquareToCircle(Scene):
    def construct(self):
        square = Square()
        circle = Circle()
        self.play(Transform(square, circle))


class FunctionLikeTest(Scene):
    def contruct(self):
        assert "FunctionLike" in globals()
        a = FunctionLike()
        self.play(FadeIn(a))


class NoAllTest(Scene):
    def construct(self):
        assert "test_plugin" in globals()
        a = test_plugin.NoAll()
        self.play(FadeIn(a))


class WithAllTest(Scene):
    def construct(self):
        assert "WithAll" in globals()
        a = WithAll()
        self.play(FadeIn(a))
