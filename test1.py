from big_ol_pile_of_manim_imports import *
from manim import Manim

class Shapes(Scene):
    #A few simple shapes
    def construct(self):
        circle = Circle()
        square = Square()
        line=Line(np.array([3,0,0]),np.array([5,0,0]))
        triangle=Polygon(np.array([0,0,0]),np.array([1,1,0]),np.array([1,-1,0]))

        self.add(line)
        self.play(ShowCreation(circle))
        self.play(FadeOut(circle))
        self.play(GrowFromCenter(square))
        self.play(Transform(square,triangle))

#python3 extract_scene.py test1.py Shapes -r 1080


if __name__ == '__main__':
    manim = Manim()
    Shapes(**manim.config)
