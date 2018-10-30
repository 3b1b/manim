from big_ol_pile_of_manim_imports import *
from manim import Manim

class Shapes(Scene):
    #A few simple shapes
    def construct(self):
        circle = Circle()
        square = Square()
        line = Line(np.array([3,0,0]),np.array([5,0,0]))
        triangle = Polygon(np.array([0,0,0]),np.array([1,1,0]),np.array([1,-1,0]))

        self.add(line)
        self.play(ShowCreation(circle))
        self.play(FadeOut(circle))
        self.play(GrowFromCenter(square))
        self.play(Transform(square,triangle))

#python3 extract_scene.py test1.py Shapes -r 1080


manim = Manim()

circle = Circle()
square = Square()
line = Line(np.array([3,0,0]),np.array([5,0,0]))
triangle = Polygon(np.array([0,0,0]),np.array([1,1,0]),np.array([1,-1,0]))

manim.add(line)
manim.play(ShowCreation(circle))
manim.play(FadeOut(circle))
manim.play(GrowFromCenter(square))
manim.play(Transform(square,triangle))

manim.close_movie_pipe()
