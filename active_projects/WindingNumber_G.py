from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.compositions import *
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

class AltTeacherStudentsScene(TeacherStudentsScene):
    def setup(self):
        TeacherStudentsScene.setup(self)
        self.teacher.set_color(YELLOW_E)

###############


class IntroSceneWrapper(PiCreatureScene):
    CONFIG = {
        "default_pi_creature_kwargs" : {
            "color" : YELLOW_E,
            "flip_at_start" : False,
            "height" : 2,
        },
        "default_pi_creature_start_corner" : DOWN+LEFT,
        # "default_pi_creature_height" : 1,
    }
    def construct(self):
        morty = self.pi_creature
        rect = ScreenRectangle(height = 5)
        rect.to_corner(UP+RIGHT)
        self.add(rect)

        main_topic, meta_topic = toipcs = VGroup(
            TextMobject("Main topic"),
            TextMobject("Meta topic"),
        )
        topics.arrange_submobjects(DOWN, aligned_edge = LEFT)






class PiCreaturesAreIntrigued(AltTeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "You can extend \\\\ this to 2d",
            bubble_kwargs = {"width" : 4, "height" : 3}
        )
        self.change_student_modes("pondering", "confused", "erm")
        self.look_at(self.screen)
        self.wait(3)

class RewriteEquationWithTeacher(AltTeacherStudentsScene):
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

        question = TextMobject(
            "Wait...what would \\\\", "+", "and", "\\textminus", " \\, be in 2d?",
        )
        question.highlight_by_tex_to_color_map({
            "+" : "green", 
            "textminus" : "red"
        })

        self.student_says(
            question,
            target_mode = "sassy",
            student_index = 2,
            added_anims = [
                equations[0].to_corner, UP+RIGHT,
                self.teacher.change, "plain",
            ],
            bubble_kwargs = {"direction" : LEFT},
            run_time = 1,
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

class DotsHoppingToColor(Scene):
    CONFIG = {
        "dot_radius" : 0.05,
        "plane_width" : 6,
        "plane_height" : 6,
        "x_shift" : SPACE_WIDTH/2,
        "y_shift" : MED_LARGE_BUFF,
        "output_scalar" : 10,
        "non_renormalized_func" : plane_func_by_wind_spec(
            (-2, -1, 2), 
            (1, 2, 1), 
            (2, -2, 1),
        ),
        "dot_density" : 0.25,
    }
    def construct(self):
        input_coloring, output_coloring = self.get_colorings()
        input_plane, output_plane = self.get_planes()

        v_line = Line(UP, DOWN).scale(SPACE_HEIGHT)
        v_line.set_stroke(WHITE, 5)

        dots = self.get_dots(input_plane, output_plane)

        right_half_block = Rectangle(
            height = 2*SPACE_HEIGHT,
            width = SPACE_WIDTH - SMALL_BUFF,
            stroke_width = 0,
            fill_color = BLACK,
            fill_opacity = 0.8,
        )
        right_half_block.to_edge(RIGHT, buff = 0)

        #Introduce parts
        self.add(input_plane, output_plane, v_line)
        self.play(
            FadeIn(output_coloring), 
            Animation(output_plane),
            output_plane.white_parts.highlight, BLACK,
            output_plane.lines_to_fade.set_stroke, {"width" : 0},
        )
        self.wait()
        self.play(LaggedStart(GrowFromCenter, dots, run_time = 3))
        self.wait()

        #Hop over and back
        self.play(LaggedStart(
            MoveToTarget, dots, 
            path_arc = -TAU/4,
            run_time = 3,
        ))
        self.wait()
        self.play(LaggedStart(
            ApplyMethod, dots,
            lambda d : (d.set_fill, d.target_color),
        ))
        self.wait()
        self.play(LaggedStart(
            ApplyMethod, dots,
            lambda d : (d.move_to, d.original_position),
            path_arc = TAU/4,
            run_time = 3,
        ))
        self.wait()
        self.play(
            FadeIn(input_coloring),
            Animation(input_plane),
            input_plane.white_parts.highlight, BLACK,
            input_plane.lines_to_fade.set_stroke, {"width" : 0},
            FadeOut(dots),
        )
        self.wait()

        #Cover output half
        right_half_block.save_state()
        right_half_block.next_to(SPACE_WIDTH*RIGHT, RIGHT)
        self.play(right_half_block.restore)
        self.wait()

        # Show yellow points
        inspector = DashedLine(
            ORIGIN, TAU*UP,
            dashed_segment_length = TAU/24,
            fill_opacity = 0,
            stroke_width = 3,
            stroke_color = WHITE,
        )
        inspector.add(*inspector.copy().highlight(BLACK).shift((TAU/24)*UP))
        inspector.apply_complex_function(np.exp)
        inspector.scale(0.15)

        inspector_image = inspector.copy()
        def point_function(point):
            in_coords = input_plane.point_to_coords(point)
            out_coords = self.func(in_coords)
            return output_plane.coords_to_point(*out_coords)

        def update_inspector_image(inspector_image):
            inspector_image.move_to(point_function(inspector.get_center()))

        inspector_image_update_anim = UpdateFromFunc(
            inspector_image, update_inspector_image
        )
        yellow_points_label = TextMobject("Yellow points")
        yellow_points_label.scale(0.7)
        yellow_points_label.highlight(BLACK)

        self.play(
            inspector.move_to, input_plane.coords_to_point(1.5, 0),
            inspector.set_stroke, {"width" : 2},
        )
        yellow_points_label.next_to(inspector, UP)
        self.play(
            Rotating(
                inspector, about_point = inspector.get_corner(UP+LEFT),
                rate_func = smooth,
                run_time = 2,
            ),
            Write(yellow_points_label)
        )
        self.wait()
        self.play(right_half_block.next_to, SPACE_WIDTH*RIGHT, RIGHT)
        inspector_image_update_anim.update(0)
        self.play(ReplacementTransform(
            inspector.copy(), inspector_image,
            path_arc = -TAU/4,
        ))
        self.play(
            ApplyMethod(
                inspector.move_to, 
                input_plane.coords_to_point(0, 2),
                path_arc = -TAU/8,
                run_time = 3,
            ),
            inspector_image_update_anim
        )
        self.play(
            ApplyMethod(
                inspector.move_to, 
                input_plane.coords_to_point(2, 0),
                path_arc = TAU/4,
                run_time = 3,
            ),
            inspector_image_update_anim
        )
        self.play(FadeOut(yellow_points_label))

        # Show black zero
        zeros = tuple(it.starmap(input_plane.coords_to_point, [
            (-2, -1), (1, 2), (2, -2),
        ]))
        for x in range(2):
            for zero in zeros:
                self.play(
                    ApplyMethod(
                        inspector.move_to, zero,
                        path_arc = -TAU/8,
                        run_time = 2,
                    ),
                    inspector_image_update_anim,
                )
                self.wait()
        self.play(FadeOut(VGroup(inspector, inspector_image)))

        # Show all dots and slowly fade them out
        for dot in dots:
            dot.scale(1.5)
        self.play(
            FadeOut(input_coloring),
            input_plane.white_parts.highlight, WHITE,
            LaggedStart(GrowFromCenter, dots)
        )
        self.wait()
        random.shuffle(dots.submobjects)
        self.play(LaggedStart(
            FadeOut, dots,
            lag_ratio = 0.05,
            run_time = 10,
        ))

        # Ask about whether a region contains a zero
        question = TextMobject("Does this region \\\\ contain a zero?")
        question.add_background_rectangle(opacity = 1)
        question.next_to(input_plane.label, DOWN)
        square = Square()
        square.match_background_image_file(input_coloring)
        square.move_to(input_plane)

        self.play(ShowCreation(square), Write(question))
        self.wait()
        quads = [
            (0, 0.5, 6, 6.25),
            (1, 1, 0.5, 2),
            (-1, -1, 3, 4.5),
            (0, 1.25, 5, 1.7),
            (-2, -1, 1, 1),
        ]
        for x, y, width, height in quads:
            self.play(
                square.stretch_to_fit_width, width,
                square.stretch_to_fit_height, height,
                square.move_to, input_plane.coords_to_point(x, y)
            )
            self.wait()



    ###

    def func(self, coord_pair):
        out_coords = np.array(self.non_renormalized_func(coord_pair))
        out_norm = np.linalg.norm(out_coords)
        if out_norm > 0.5:
            angle = angle_of_vector(out_coords)
            factor = 0.5-0.1*np.cos(4*angle)
            target_norm = factor*np.log(out_norm)
            out_coords *= target_norm / out_norm
        return tuple(out_coords)

    def get_colorings(self):
        in_cmos = ColorMappedObjectsScene(
            func = lambda p : self.non_renormalized_func(
                (p[0]+self.x_shift, p[1]+self.y_shift)
            )
        )
        scalar = self.output_scalar
        out_cmos = ColorMappedObjectsScene(
            func = lambda p : (
                scalar*(p[0]-self.x_shift), scalar*(p[1]+self.y_shift)
            )
        )

        input_coloring = Rectangle(
            height = self.plane_height,
            width = self.plane_width,
            stroke_width = 0,
            fill_color = WHITE,
            fill_opacity = 1,
        )
        output_coloring = input_coloring.copy()
        colorings = [input_coloring, output_coloring]
        vects = [LEFT, RIGHT]
        cmos_pair = [in_cmos, out_cmos]
        for coloring, vect, cmos in zip(colorings, vects, cmos_pair):
            coloring.move_to(self.x_shift*vect + self.y_shift*DOWN)
            coloring.color_using_background_image(cmos.background_image_file)
        return colorings

    def get_planes(self):
        input_plane = NumberPlane(
            x_radius = self.plane_width/2.0,
            y_radius = self.plane_height/2.0,
        )
        output_plane = input_plane.copy()
        planes = [input_plane, output_plane]
        vects = [LEFT, RIGHT]
        label_texts = ["Input", "Output"]
        label_colors = [GREEN, RED]
        for plane, vect, text, color in zip(planes, vects, label_texts, label_colors):
            plane.stretch_to_fit_width(self.plane_width)
            plane.add_coordinates(x_vals = range(-2, 3), y_vals = range(-2, 3))
            plane.white_parts = VGroup(plane.axes, plane.coordinate_labels)
            plane.lines_to_fade = VGroup(plane.main_lines, plane.secondary_lines)
            plane.move_to(vect*SPACE_WIDTH/2 + self.y_shift*DOWN)
            label = TextMobject(text)
            label.scale(1.5)
            label.add_background_rectangle()
            label.move_to(plane)
            label.to_edge(UP, buff = MED_SMALL_BUFF)
            plane.add(label)
            plane.label = label
            for submob in plane.submobject_family():
                if isinstance(submob, TexMobject) and hasattr(submob, "background_rectangle"):
                    submob.remove(submob.background_rectangle)


        return planes

    def get_dots(self, input_plane, output_plane):
        step = self.dot_density
        x_min = -3.0
        x_max = 3.0
        y_min = -3.0
        y_max = 3.0
        dots = VGroup()
        for x in np.arange(x_min, x_max + step, step):
            for y in np.arange(y_max, y_min - step, -step):
                out_coords = self.func((x, y))
                dot = Dot(radius = self.dot_radius)
                dot.set_stroke(BLACK, 1)
                dot.move_to(input_plane.coords_to_point(x, y))
                dot.original_position = dot.get_center()
                dot.generate_target()
                dot.target.move_to(output_plane.coords_to_point(*out_coords))
                dot.target_color = rgba_to_color(point_to_rgba(
                    tuple(self.output_scalar*np.array(out_coords))
                ))
                dots.add(dot)
        return dots

class SoWeFoundTheZeros(AltTeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Aha! So we \\\\ found the solutions!",
            target_mode = "hooray",
            student_index = 2,
            bubble_kwargs = {"direction" : LEFT},
        )
        self.wait()
        self.teacher_says(
            "Er...only \\\\ kind of",
            target_mode = "hesitant"
        )
        self.wait(3)

class PiCreatureAsksWhatWentWrong(PiCreatureScene):
    def construct(self):
        randy = self.pi_creature
        randy.set_color(YELLOW_E)
        randy.flip()
        randy.to_corner(DOWN+LEFT)
        question = TextMobject("What went wrong?")
        question.next_to(randy, UP)
        question.shift_onto_screen()
        question.save_state()
        question.shift(DOWN).fade(1)

        self.play(randy.change, "erm")
        self.wait(2)
        self.play(
            Animation(VectorizedPoint(ORIGIN)),
            question.restore,
            randy.change, "confused",
        )
        self.wait(5)












































