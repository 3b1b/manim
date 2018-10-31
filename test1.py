from big_ol_pile_of_manim_imports import *
from manim import Manim


manim = Manim()

circle = Circle()
square = Square()
line = Line(np.array([3,0,0]),np.array([5,0,0]))
triangle = Polygon(np.array([0,0,0]),np.array([1,1,0]),np.array([1,-1,0]))

manim.wait(3)
manim.add(line)
manim.wait(3)
manim.play(ShowCreation(circle))
manim.wait(3)
manim.play(FadeOut(circle))
manim.wait(3)
manim.play(GrowFromCenter(square))
manim.wait(3)
manim.play(Transform(square,triangle))
manim.wait(10)

manim.close_movie_pipe()

# ffplay tcp://127.0.0.1:2000?listen
# for listening the stream
# start mplayer before running this script
