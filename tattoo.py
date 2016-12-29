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
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *



class TrigRepresentationsScene(Scene):
    CONFIG = {
        "unit_length" : 1.5,
        "arc_radius" : 0.5,
        "axes_color" : WHITE,
        "circle_color" : RED,
        "theta_color" : YELLOW,
        "theta_height" : 0.3,
        "theta_value" : np.pi/5,
        "x_line_colors" : MAROON_B,
        "y_line_colors" : BLUE,
    }
    def setup(self):
        self.init_axes()
        self.init_circle()
        self.init_theta_mobs()

    def init_axes(self):
        self.axes = Axes(
            space_unit_to_num = self.unit_length,
        )
        self.axes.highlight(self.axes_color)
        self.add(self.axes)

    def init_circle(self):
        self.circle = Circle(
            radius = self.unit_length,
            color = self.circle_color
        )
        self.add(self.circle)

    def init_theta_mobs(self):
        self.theta_mobs = self.get_theta_mobs()
        self.add(self.theta_mobs)

    def add_trig_lines(self, *funcs, **kwargs):
        lines = VGroup(*[
            self.get_trig_line(func, **kwargs)
            for func in funcs
        ])
        self.add(*lines)

    def get_theta_mobs(self):
        arc = Arc(
            self.theta_value, 
            radius = self.arc_radius,
            color = self.theta_color,
        )
        theta = TexMobject("\\theta")
        theta.shift(1.5*arc.point_from_proportion(0.5))
        theta.highlight(self.theta_color)
        theta.scale_to_fit_height(self.theta_height)
        line = Line(ORIGIN, self.get_circle_point())
        dot = Dot(line.get_end(), radius = 0.05)
        return VGroup(line, arc, theta, dot)

    def get_circle_point(self):
        return rotate_vector(self.unit_length*RIGHT, self.theta_value)

    def get_trig_line(self, func_name = "sin", color = None):
        assert(func_name in ["sin", "tan", "sec", "cos", "cot", "csc"])
        is_co = func_name in ["cos", "cot", "csc"]
        if color is None:
            if is_co:
                color = self.y_line_colors 
            else:
                color = self.x_line_colors

        #Establish start point
        if func_name in ["sin", "cos", "tan", "cot"]:
            start_point = self.get_circle_point()
        else:
            start_point = ORIGIN

        #Establish end point
        if func_name is "sin":
            end_point = start_point[0]*RIGHT
        elif func_name is "cos":
            end_point = start_point[1]*UP
        elif func_name in ["tan", "sec"]:
            end_point = (1./np.cos(self.theta_value))*self.unit_length*RIGHT
        elif func_name in ["cot", "csc"]:
            end_point = (1./np.sin(self.theta_value))*self.unit_length*UP
        return Line(start_point, end_point, color = color)


class IntroduceCSC(TrigRepresentationsScene):
    def construct(self):
        self.clear()
        Cam_S_C = TextMobject("Cam", "S.", "C.")
        CSC = TextMobject("C", "S", "C", arg_separator = "")
        csc_of_theta = TextMobject("c", "s", "c", "(\\theta)", arg_separator = "")
        csc, of_theta = VGroup(*csc_of_theta[:3]), csc_of_theta[-1]
        of_theta[1].highlight(YELLOW)
        CSC.move_to(csc, DOWN)

        csc_line = self.get_trig_line("csc")
        csc_line.set_stroke(width = 8)
        cot_line = self.get_trig_line("cot")
        cot_line.highlight(WHITE)
        brace = Brace(csc_line, LEFT)

        self.play(Write(Cam_S_C))
        self.dither()
        self.play(Transform(Cam_S_C, CSC))
        self.dither()
        self.play(Transform(Cam_S_C, csc))
        self.remove(Cam_S_C)
        self.add(csc)
        self.play(Write(of_theta))
        self.dither(2)

        csc_of_theta.add_to_back(BackgroundRectangle(csc))
        self.play(
            ShowCreation(self.axes),
            ShowCreation(self.circle),
            GrowFromCenter(brace),            
            csc_of_theta.rotate, np.pi/2,
            csc_of_theta.next_to, brace, LEFT,
            path_arc = np.pi/2,
        )
        self.play(Write(self.theta_mobs, run_time = 1))
        self.play(ShowCreation(cot_line))
        self.play(
            ShowCreation(csc_line),
            csc.highlight, csc_line.get_color(),
        )
        self.dither(3)









































