from helpers import *
from mobject import Mobject
from mobject.vectorized_mobject import *
from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from topics.geometry import *
from scene import Scene
from camera import *
from topics.number_line import *
from topics.three_dimensions import *
from topics.light import *
from topics.characters import *
from topics.numerals import *



class Birthday(Scene):

    def construct(self):

        sidelength = 6.0
        corner = np.array([-sidelength/2,-sidelength/2,0])
        nb_days_left = 365.0
        toggle = False

        def probability():
            width = rect.get_width()
            height = rect.get_height()
            return width * height / sidelength**2

        rect = Square().scale(sidelength/2)

        while probability() > 0.5:

            self.add(rect.copy())
            nb_days_left -= 1

            if toggle:
                dim = 0
            else:
                dim = 1
            
            rect.stretch_about_point(nb_days_left / 365, dim, corner)

            toggle = not toggle

