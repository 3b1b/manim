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

SPACE_UNIT_TO_PLANE_UNIT = 0.75

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
        "circle_radius" : 5,
        "circle_color" : YELLOW,
        "example_color" : MAROON_B,
        "zoom_factor" : 20,
        "zoomed_canvas_corner" : UP+LEFT,
        "zoomed_canvas_corner_buff" : MED_SMALL_BUFF,
    }
    def construct(self):
        should_skip_animations = self.skip_animations
        self.skip_animations = True

        self.setup_plane()
        self.introduce_circle()
        self.talk_through_pythagorean_theorem()
        self.draw_example_slope()
        # self.show_perpendicular_radius()
        self.show_dx_and_dy()
        self.write_slope_as_dy_dx()
        # self.point_out_this_is_not_a_graph()
        self.skip_animations = should_skip_animations
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
        circle = Circle(
            radius = self.circle_radius*SPACE_UNIT_TO_PLANE_UNIT,
            color = self.circle_color,
        )
        equation = TexMobject("x^2 + y^2 = 5^2")
        equation.add_background_rectangle()
        equation.next_to(
            circle.point_from_proportion(1./8), 
            UP+RIGHT
        )

        self.play(ShowCreation(circle, run_time = 2))
        self.play(Write(equation))
        self.dither()

        self.circle = circle
        self.circle_equation = equation

    def talk_through_pythagorean_theorem(self):
        point = self.plane.num_pair_to_point(self.example_point)
        x_axis_point = point[0]*RIGHT
        dot = Dot(point, color = self.example_color)

        x_line = Line(ORIGIN, x_axis_point, color = GREEN)
        y_line = Line(x_axis_point, point, color = RED)
        radial_line = Line(ORIGIN, point, color = self.example_color)
        lines = VGroup(radial_line, x_line, y_line)
        labels = VGroup()

        self.play(ShowCreation(dot))
        for line, tex in zip(lines, "5xy"):
            label = TexMobject(tex)
            label.highlight(line.get_color())
            label.add_background_rectangle()
            label.next_to(
                line.get_center(), 
                rotate_vector(UP, line.get_angle()),
                buff = SMALL_BUFF
            )
            self.play(
                ShowCreation(line),
                Write(label)
            )
            labels.add(label)

        full_group = VGroup(dot, lines, labels)
        start_angle = angle_of_vector(point)
        end_angle = np.pi/12
        spatial_radius = np.linalg.norm(point)
        def update_full_group(group, alpha):
            dot, lines, labels = group
            angle = interpolate(start_angle, end_angle, alpha)
            new_point = spatial_radius*rotate_vector(RIGHT, angle)
            new_x_axis_point = new_point[0]*RIGHT
            dot.move_to(new_point)

            radial_line, x_line, y_line = lines
            x_line.put_start_and_end_on(ORIGIN, new_x_axis_point)
            y_line.put_start_and_end_on(new_x_axis_point, new_point)
            radial_line.put_start_and_end_on(ORIGIN, new_point)
            for line, label in zip(lines, labels):
                label.next_to(
                    line.get_center(), 
                    rotate_vector(UP, line.get_angle()),
                    buff = SMALL_BUFF
                )
            return group

        self.play(UpdateFromAlphaFunc(
            full_group, update_full_group,
            rate_func = there_and_back,
            run_time = 5,
        ))
        self.dither(2)
        self.play(*map(FadeOut, [lines, labels]))
        self.remove(full_group)
        self.add(dot)
        self.dither()

        self.example_point_dot = dot

    def draw_example_slope(self):
        point = self.example_point_dot.get_center()
        line = Line(ORIGIN, point)
        line.highlight(self.example_color)
        line.rotate(np.pi/2)
        line.scale(2)
        line.move_to(point)

        word = TextMobject("Slope?")
        word.next_to(line.get_start(), UP, aligned_edge = LEFT)
        word.add_background_rectangle()

        coords = TexMobject("(%d, %d)"%self.example_point)
        coords.add_background_rectangle()
        coords.scale(0.7)
        coords.next_to(point, LEFT)
        coords.shift(SMALL_BUFF*DOWN)
        coords.highlight(self.example_color)

        self.play(GrowFromCenter(line))
        self.play(Write(word))
        self.dither()
        self.play(Write(coords))
        self.dither()

        self.tangent_line = line
        self.slope_word = word
        self.example_point_coords_mob = coords

    def show_perpendicular_radius(self):
        point = self.example_point_dot.get_center()
        radial_line = Line(ORIGIN, point, color = RED)

        perp_mark = VGroup(
            Line(UP, UP+RIGHT),
            Line(UP+RIGHT, RIGHT),
        )
        perp_mark.scale(0.2)
        perp_mark.set_stroke(width = 2)
        perp_mark.rotate(radial_line.get_angle()+np.pi)
        perp_mark.shift(point)

        self.play(ShowCreation(radial_line))
        self.play(ShowCreation(perp_mark))
        self.dither()
        self.play(Indicate(perp_mark))
        self.dither()
        
        morty =  Mortimer().flip().to_corner(DOWN+LEFT)
        self.play(FadeIn(morty))
        self.play(PiCreatureBubbleIntroduction(
            morty, "Suppose you \\\\ don't know this.",
        ))
        self.play(Blink(morty))
        self.dither()

        self.play(*map(
            FadeOut, [morty, morty.bubble, morty.bubble.content]
        ))
        self.play(*map(FadeOut, [radial_line, perp_mark]))
        self.dither()

    def show_dx_and_dy(self):
        dot = self.example_point_dot
        point = dot.get_center()
        step_vect = rotate_vector(point, np.pi/2)
        step_length = 1./self.zoom_factor
        step_vect *= step_length/np.linalg.norm(step_vect)

        step_line = Line(ORIGIN, LEFT)
        step_line.highlight(WHITE)
        brace = Brace(step_line, DOWN)
        step_text = brace.get_text("Step", buff = SMALL_BUFF)
        step_group = VGroup(step_line, brace, step_text)
        step_group.rotate(angle_of_vector(point) - np.pi/2)
        step_group.scale(1./self.zoom_factor)
        step_group.shift(point)

        interim_point = step_line.get_corner(UP+RIGHT)
        dy_line = Line(point, interim_point)
        dx_line = Line(interim_point, point+step_vect)
        dy_line.highlight(RED)
        dx_line.highlight(GREEN)
        for line, tex in (dx_line, "dx"), (dy_line, "dy"):
            label = TexMobject(tex)
            label.scale(1./self.zoom_factor)
            next_to_vect = np.round(
                rotate_vector(DOWN, line.get_angle())
            )
            label.next_to(
                line, next_to_vect,
                buff = MED_SMALL_BUFF/self.zoom_factor
            )
            label.highlight(line.get_color())
            line.label = label

        self.activate_zooming()
        self.little_rectangle.move_to(step_line.get_center())
        self.little_rectangle.save_state()
        self.little_rectangle.scale_in_place(self.zoom_factor)
        self.dither()        
        self.play(
            self.little_rectangle.restore,
            dot.scale_in_place, 1./self.zoom_factor,
            run_time = 2
        )
        self.dither()
        self.play(ShowCreation(step_line))
        self.play(GrowFromCenter(brace))
        self.play(Write(step_text))
        self.dither()
        for line in dy_line, dx_line:
            self.play(ShowCreation(line))
            self.play(Write(line.label))
            self.dither()
        self.dither()

        self.step_group = step_group
        self.dx_line = dx_line
        self.dy_line = dy_line

    def write_slope_as_dy_dx(self):
        slope_word = self.slope_word
        new_slope_word = TextMobject("Slope =")
        new_slope_word.add_background_rectangle()
        new_slope_word.next_to(ORIGIN, RIGHT)
        new_slope_word.shift(slope_word.get_center()[1]*UP)

        dy_dx = TexMobject("\\frac{dy}{dx}")
        VGroup(*dy_dx[:2]).highlight(RED)
        VGroup(*dy_dx[-2:]).highlight(GREEN)
        dy_dx.next_to(new_slope_word, RIGHT, buff = SMALL_BUFF)
        dy_dx.add_background_rectangle()

        self.play(Transform(slope_word, new_slope_word))
        self.play(Write(dy_dx))
        self.dither()

    def point_out_this_is_not_a_graph(self):
        equation = self.circle_equation
        x = equation[1][0]
        y = equation[1][3]
        brace = Brace(equation, DOWN)
        brace_text = brace.get_text(
            "Not $y = f(x)$",
            buff = SMALL_BUFF
        )
        brace_text.highlight(RED)
        alt_brace_text = brace.get_text("Implicit curve")
        for text in brace_text, alt_brace_text:
            text.add_background_rectangle()
            text.to_edge(RIGHT, buff = MED_SMALL_BUFF)

        new_circle = self.circle.copy()
        new_circle.highlight(BLUE)

        self.play(
            GrowFromCenter(brace),
            Write(brace_text)
        )
        self.dither()
        self.play(Indicate(x))
        self.dither()
        self.play(Indicate(y))
        self.dither()
        self.play(Transform(brace_text, alt_brace_text))
        self.dither()
        self.play(
            ShowCreation(new_circle, run_time = 2),
            Animation(brace_text)
        )
        self.play(new_circle.set_stroke, None, 0)
        self.dither()
        self.play(*map(FadeOut, [brace, brace_text]))
        self.dither()

    def perform_implicit_derivative(self):
        equation = self.circle_equation

    def show_rearrangement(self):
        pass

    def show_final_slope(self):
        pass


















