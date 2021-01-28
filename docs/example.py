from manimlib.imports import *

class SquareToCircle(Scene):
    def construct(self):
        circle = Circle()
        circle.set_fill(BLUE, opacity=0.5)
        circle.set_stroke(BLUE_E, width=4)
        square = Square()

        self.play(ShowCreation(square))
        self.wait()
        self.play(ReplacementTransform(square, circle))
        self.wait()
        # Try typing the following lines
        # self.play(circle.stretch, 4, {"dim": 0})
        # self.play(Rotate(circle, TAU / 4))
        # self.play(circle.shift, 2 * RIGHT, circle.scale, 0.25)
        # circle.insert_n_curves(10)
        # self.play(circle.apply_complex_function, lambda z: z**2)

class SquareToCircleEmbed(Scene):
    def construct(self):
        circle = Circle()
        circle.set_fill(BLUE, opacity=0.5)
        circle.set_stroke(BLUE_E, width=4)

        self.add(circle)
        self.wait()
        self.play(circle.stretch, 4, {"dim": 0})
        self.wait(1.5)
        self.play(Rotate(circle, TAU / 4))
        self.wait(1.5)
        self.play(circle.shift, 2 * RIGHT, circle.scale, 0.25)
        self.wait(1.5)
        circle.insert_n_curves(10)
        self.play(circle.apply_complex_function, lambda z: z**2)
        self.wait(2)
