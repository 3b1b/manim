from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from animation.continual_animation import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from topics.objects import *
from topics.probability import *
from topics.complex_numbers import *
from scene import Scene
from scene.reconfigurable_scene import ReconfigurableScene
from scene.zoomed_scene import *
from camera import *
from mobject.svg_mobject import *
from mobject.tex_mobject import *
from topics.graph_scene import *

from active_projects.WindingNumber import *

class AltTeacherStudentScene(TeacherStudentsScene):
    def setup(self):
        TeacherStudentsScene.setup(self)
        self.teacher.set_color(YELLOW_E)

###############


class TestColorMap(ColorMappedObjectsScene):
    CONFIG = {
        "func" : example_plane_func,
    }
    def construct(self):
        ColorMappedObjectsScene.construct(self)
        circle = Circle(color = WHITE)
        circle.color_using_background_image(self.background_image_file)

        self.play(ShowCreation(circle))
        self.play(circle.scale, 2)
        self.wait()
        self.play(circle.set_fill, {"opacity" : 0.2})
        for corner in standard_rect:
            self.play(circle.to_corner, corner, run_time = 2)


class PiCreaturesAreIntrigued(AltTeacherStudentScene):
    def construct(self):
        self.teacher_says(
            "You can extend \\\\ this to 2d",
            bubble_kwargs = {"width" : 4, "height" : 3}
        )
        self.change_student_modes("pondering", "confused", "erm")
        self.look_at(self.screen)
        self.wait(3)

class RewriteEquationWithTeacher(AltTeacherStudentScene):
    def construct(self):
        equations = VGroup(
            TexMobject(
                "f(\\text{2d input})", "", "=", 
                "g(\\text{2d input})", ""
            ),
            TexMobject(
                "f(\\text{2d input})", "-", 
                "g(\\text{2d input})", "=", "0"
            ),
        )
        specific_equations = VGroup(
            TexMobject("x^2", "", "=", "2", ""),
            TexMobject("x^2", "-", "2", "=", "0"),
        )
        for equation in it.chain(equations, specific_equations):
            equation.sort_submobjects_alphabetically()
            for part in equation.get_parts_by_tex("text"):
                part[2:-1].highlight(YELLOW)
                part[2:-1].scale(0.9)
            equation.move_to(self.hold_up_spot, DOWN)

        self.teacher_holds_up(specific_equations[0])
        self.play(Transform(*specific_equations, path_arc = TAU/4))
        self.play(self.get_student_changes(*["pondering"]*3))
        self.play(FadeOut(specific_equations[0]), FadeIn(equations[0]))
        self.wait()
        self.play(Transform(*equations, path_arc = TAU/4))
        self.change_student_modes(*["happy"]*3)

        # 2d plane
        plane = NumberPlane(x_radius = 2.5, y_radius = 2.5)
        plane.scale(0.8)
        plane.to_corner(UP+LEFT)
        plane.add_coordinates()

        dot = Dot(color = YELLOW)
        label = TextMobject("Sign?")
        label.add_background_rectangle()
        label.scale(0.5)
        label.next_to(dot, UP, SMALL_BUFF)
        dot.add(label)
        dot.move_to(plane.coords_to_point(1, 1))
        dot.save_state()
        dot.fade(1)
        dot.center()

        self.student_says(
            "Wait...what would \\\\ + and \\textminus \\, be in 2d?",
            target_mode = "sassy",
            student_index = 2,
            added_anims = [
                equations[0].to_corner, UP+RIGHT,
                self.teacher.change, "plain",
            ],
            bubble_kwargs = {"direction" : LEFT},
        )
        self.play(
            Write(plane, run_time = 1),
            self.students[0].change, "confused",
            self.students[1].change, "confused",
        )
        self.play(dot.restore)
        for coords in (-1, 1), (1, -1), (0, -2), (-2, 1):
            self.wait(0.5)
            self.play(dot.move_to, plane.coords_to_point(*coords))
        self.wait()



















































