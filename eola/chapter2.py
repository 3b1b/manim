from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import VMobject

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.number_line import *
from topics.combinatorics import *
from scene import Scene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *
from mobject.vectorized_mobject import *

from eola.matrix import *
from eola.two_d_space import *

class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject("""
            Mathematics requires a small dose, not of genius, \\\\
            but of an imaginative freedom which, in a larger \\\\
            dose, would be insanity.
        """)
        words.to_edge(UP)    
        for mob in words.submobjects[49:49+18]:
            mob.highlight(GREEN)
        words.show()
        author = TextMobject("-Angus K. Rodgers")
        author.highlight(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(FadeIn(words))
        self.dither(3)
        self.play(Write(author, run_time = 3))
        self.dither()


class CoordinatesWereFamiliar(TeacherStudentsScene):
    def construct(self):
        self.setup()
        self.student_says("I know this already")
        self.random_blink()
        self.teacher_says("Ah, but there is a subtlety")
        self.random_blink()
        self.dither()


class CoordinatesAsScalars(VectorScene):
    def construct(self):
        self.add_axes()
        vector = self.add_vector([3, -2])
        array, x_line, y_line = self.vector_to_coords(vector)
        self.add(array)
        self.dither()
        self.general_idea_of_scalars(array)

    def general_idea_of_scalars(self, array):
        starting_mobjects = self.get_mobjects()
        starting_mobjects.remove(array)

        title = TextMobject("Think of each coordinate as a scalar")
        title.to_edge(UP)

        x, y = array.get_mob_matrix().flatten()
        new_x = x.copy().scale(2).highlight(X_COLOR)
        new_x.move_to(3*LEFT+2*UP)
        new_y = y.copy().scale(2).highlight(Y_COLOR)
        new_y.move_to(3*RIGHT+2*UP)

        self.play(
            FadeOut(*starting_mobjects)
            Transform(x, new_x),
            Transform(y, new_y),
            Write(title),
        )

















