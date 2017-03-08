from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from topics.objects import *
from scene import Scene
from scene.zoomed_scene import ZoomedScene
from scene.reconfigurable_scene import ReconfigurableScene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

from topics.common_scenes import *
from eoc.graph_scene import *

SPACE_UNIT_TO_PLANE_UNIT = 0.7

class Chapter5OpeningQuote(OpeningQuote):
    CONFIG = {
        "quote" : [
            "Do not ask whether a ",
            "statement is true until",
            "you know what it means."
        ],
        "author" : "Errett Bishop"
    }

class ThisWasConfusing(TeacherStudentsScene):
    def construct(self):
        words = TextMobject("Implicit differentiation")
        words.move_to(self.get_teacher().get_corner(UP+LEFT), DOWN+RIGHT)
        words.set_fill(opacity = 0)

        self.play(
            self.get_teacher().change_mode, "raise_right_hand",
            words.set_fill, None, 1,
            words.shift, 0.5*UP
        )
        self.change_student_modes(
            *["confused"]*3,
            look_at_arg = words,
            added_anims = [Animation(self.get_teacher())]
        )
        self.dither()
        self.play(
            self.get_teacher().change_mode, "confused",
            self.get_teacher().look_at, words,
        )
        self.dither(3)

class SlopeOfCircleExample(ZoomedScene):
    CONFIG = {
        "plane_kwargs" : {
            "x_radius" : SPACE_WIDTH/SPACE_UNIT_TO_PLANE_UNIT,
            "y_radius" : SPACE_HEIGHT/SPACE_UNIT_TO_PLANE_UNIT,
            "space_unit_to_x_unit" : SPACE_UNIT_TO_PLANE_UNIT,
            "space_unit_to_y_unit" : SPACE_UNIT_TO_PLANE_UNIT,
        },
        "example_point" : (3, 4),
    }
    def construct(self):
        should_skip_animations = self.skip_animations
        self.skip_animations = True


        self.skip_animations = should_skip_animations
        self.setup_plane()
        self.introduce_circle()
        self.talk_through_pythagorean_theorem()
        self.draw_example_slope()
        self.show_perpendicular_radius()
        self.show_dx_and_dy()
        self.point_out_this_is_not_a_graph()
        self.perform_implicit_derivative()
        self.show_rearrangement()
        self.show_final_slope()

    def setup_plane(self):
        self.plane = NumberPlane(**self.plane_kwargs)
        self.plane.main_lines.fade()

        self.plane.add(self.plane.get_axis_labels())
        self.plane.add_coordinates()

        self.add(self.plane)

    def introduce_circle(self):
        pass

    def talk_through_pythagorean_theorem(self):
        pass

    def draw_example_slope(self):
        pass

    def show_perpendicular_radius(self):
        pass

    def show_dx_and_dy(self):
        pass

    def point_out_this_is_not_a_graph(self):
        pass

    def perform_implicit_derivative(self):
        pass

    def show_rearrangement(self):
        pass

    def show_final_slope(self):
        pass


















