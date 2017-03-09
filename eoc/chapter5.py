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
        self.setup_plane()
        self.introduce_circle()
        self.talk_through_pythagorean_theorem()
        self.draw_example_slope()
        self.show_perpendicular_radius()
        self.show_dx_and_dy()
        self.write_slope_as_dy_dx()
        self.point_out_this_is_not_a_graph()
        self.perform_implicit_derivative()
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
        equation.to_edge(RIGHT)

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
        to_fade =self.get_mobjects_from_last_animation()
        self.play(Blink(morty))
        self.dither()

        self.play(*map(FadeOut, to_fade))
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
        dy_dx.next_to(new_slope_word, RIGHT)
        dy_dx.add_background_rectangle()

        self.play(Transform(slope_word, new_slope_word))
        self.play(Write(dy_dx))
        self.dither()

        self.dy_dx = dy_dx

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
        morty = Mortimer()
        morty.flip()
        morty.next_to(ORIGIN, LEFT)
        morty.to_edge(DOWN, buff = SMALL_BUFF)
        q_marks = TexMobject("???")
        q_marks.next_to(morty, UP)

        rect = Rectangle(
            width = SPACE_WIDTH - SMALL_BUFF, 
            height = SPACE_HEIGHT - SMALL_BUFF,
            stroke_width = 0,
            fill_color = BLACK,
            fill_opacity = 0.8,
        )
        rect.to_corner(DOWN+RIGHT, buff = 0)

        derivative = TexMobject("2x\\,dx + 2y\\,dy = 0")
        dx = VGroup(*derivative[2:4])
        dy = VGroup(*derivative[7:9])
        dx.highlight(GREEN)
        dy.highlight(RED)



        self.play(
            FadeIn(rect),
            FadeIn(morty),            
            equation.next_to, ORIGIN, DOWN, MED_LARGE_BUFF,
            equation.shift, SPACE_WIDTH*RIGHT/2,
        )
        self.play(
            morty.change_mode, "confused",
            morty.look_at, equation
        )
        self.play(Blink(morty))
        derivative.next_to(equation, DOWN)
        derivative.shift(
            equation[1][-3].get_center()[0]*RIGHT - \
            derivative[-2].get_center()[0]*RIGHT
        )


        #Differentiate
        self.play(
            morty.look_at, derivative[0],
            *[
                ReplacementTransform(
                    equation[1][i].copy(),
                    derivative[j],
                )
                for i, j in (1, 0), (0, 1)
            ]
        )
        self.play(Write(dx, run_time = 1))
        self.dither()
        self.play(*[
            ReplacementTransform(
                equation[1][i].copy(),
                derivative[j],
            )
            for i, j in (2, 4), (3, 6), (4, 5)
        ])
        self.play(Write(dy, run_time = 1))
        self.play(Blink(morty)) 
        self.play(*[
            ReplacementTransform(
                equation[1][i].copy(),
                derivative[j],
            )
            for i, j in (-3, -2), (-2, -1), (-1, -1)
        ])
        self.dither()

        #React
        self.play(morty.change_mode, "erm")
        self.play(Blink(morty))
        self.play(Write(q_marks))
        self.dither()
        self.play(Indicate(dx), morty.look_at, dx)
        self.play(Indicate(dy), morty.look_at, dy)
        self.dither()
        self.play(
            morty.change_mode, "shruggie",
            FadeOut(q_marks)
        )
        self.play(Blink(morty))
        self.play(
            morty.change_mode, "pondering",
            morty.look_at, derivative,
        )

        #Rearrange
        x, y, eq = np.array(derivative)[[1, 6, 9]]
        final_form = TexMobject(
            "\\frac{dy}{dx} = \\frac{-x}{y}"
        )
        new_dy = VGroup(*final_form[:2])
        new_dx = VGroup(*final_form[3:5])
        new_dy.highlight(dy.get_color())
        new_dx.highlight(dx.get_color())
        new_dy.add(final_form[2])
        new_x = VGroup(*final_form[6:8])
        new_y = VGroup(*final_form[8:10])
        new_eq = final_form[5]

        final_form.next_to(derivative, DOWN)
        final_form.shift((eq.get_center()[0]-new_eq.get_center()[0])*RIGHT)


        self.play(*[
            ReplacementTransform(
                mover.copy(), target,
                run_time = 2,
                path_arc = np.pi/2,
            )
            for mover, target in [
                (dy, new_dy), 
                (dx, new_dx), 
                (eq, new_eq), 
                (x, new_x), 
                (y, new_y)
            ]
        ] + [
            morty.look_at, final_form
        ])
        self.dither(2)

        self.morty = morty
        self.neg_x_over_y = VGroup(*final_form[6:])

    def show_final_slope(self):
        morty = self.morty
        dy_dx = self.dy_dx
        coords = self.example_point_coords_mob
        x, y = coords[1][1].copy(), coords[1][3].copy()        

        frac = self.neg_x_over_y.copy()
        frac.generate_target()
        eq = TexMobject("=")
        eq.add_background_rectangle()
        eq.next_to(dy_dx, RIGHT)
        frac.target.next_to(eq, RIGHT)
        frac.target.shift(SMALL_BUFF*DOWN)
        rect = BackgroundRectangle(frac.target)

        self.play(
            FadeIn(rect),
            MoveToTarget(frac),
            Write(eq),
            morty.look_at, rect,
            run_time = 2,
        )
        self.dither()
        self.play(FocusOn(coords), morty.look_at, coords)
        self.play(Indicate(coords))
        scale_factor = 1.4
        self.play(
            x.scale, scale_factor,
            x.highlight, GREEN,
            x.move_to, frac[1],
            FadeOut(frac[1]),
            y.scale, scale_factor,
            y.highlight, RED,
            y.move_to, frac[3], DOWN,
            y.shift, SMALL_BUFF*UP,
            FadeOut(frac[3]),
            morty.look_at, frac,
            run_time = 2
        )
        self.dither()
        self.play(Blink(morty))

class NameImplicitDifferentation(TeacherStudentsScene):
    def construct(self):
        title = TextMobject("``Implicit differentiation''")

        equation = TexMobject("x^2", "+", "y^2", "=", "5^2")
        derivative = TexMobject(
            "2x\\,dx", "+", "2y\\,dy", "=", "0"
        )
        VGroup(*derivative[0][2:]).highlight(GREEN)
        VGroup(*derivative[2][2:]).highlight(RED)
        arrow = Arrow(ORIGIN, DOWN, buff = SMALL_BUFF)
        group = VGroup(title, equation, arrow, derivative)
        group.arrange_submobjects(DOWN)
        group.to_edge(UP)

        self.add(title, equation)
        self.play(
            self.get_teacher().change_mode, "raise_right_hand",
            ShowCreation(arrow)
        )
        self.change_student_modes(
            *["confused"]*3,
            look_at_arg = derivative,
            added_anims = [ReplacementTransform(equation.copy(), derivative)]
        )
        self.dither(2)
        self.teacher_says(
            "Don't worry...",
            added_anims = [
                group.scale, 0.7,
                group.to_corner, UP+LEFT,
            ]
        )
        self.change_student_modes(*["happy"]*3)
        self.dither(3)

class Ladder(VMobject):
    CONFIG = {
        "height" : 4,
        "width" : 1,
        "n_rungs" : 6,
    }
    def generate_points(self):
        left_line, right_line = [
            Line(ORIGIN, self.height*UP).shift(self.width*vect/2.0)
            for vect in LEFT, RIGHT
        ]
        rungs = [
            Line(
                left_line.point_from_proportion(a),
                right_line.point_from_proportion(a),
            )
            for a in np.linspace(0, 1, self.n_rungs+2)[1:-1]
        ]
        self.add(left_line, right_line, *rungs)
        self.center()


class RelatedRatesExample(ThreeDScene):
    CONFIG = {
        "start_x" : 3.0,
        "start_y" : 4.0,
        "wall_color" : color_gradient([GREY_BROWN, BLACK], 4)[1],
        "wall_center" : LEFT,
    }
    def construct(self):
        should_skip_animations = self.skip_animations
        self.skip_animations = True

        self.introduce_ladder()
        self.write_related_rates()
        self.measure_ladder()
        self.skip_animations = should_skip_animations
        self.slide_ladder()

    def introduce_ladder(self):
        ladder = Ladder(height = self.get_ladder_length())

        wall = Prism(
            dimensions = [0.5, 6, 5],
            fill_color = self.wall_color,
            fill_opacity = 1,
        )
        wall.rotate(np.pi/12, UP)
        wall.shift(self.wall_center)

        ladder.generate_target()
        ladder.fallen = ladder.copy()
        ladder.target.rotate(self.get_ladder_angle(), LEFT)
        ladder.fallen.rotate(np.pi/2, LEFT)
        for ladder_copy in ladder.target, ladder.fallen:
            ladder_copy.rotate(-5*np.pi/12, UP)
            ladder_copy.next_to(wall, LEFT, 0, DOWN)
            ladder_copy.shift(LARGE_BUFF*RIGHT)


        self.play(
            ShowCreation(ladder, run_time = 2)
        )
        self.dither()

        self.play(
            DrawBorderThenFill(wall),
            MoveToTarget(ladder),
            run_time = 2
        )
        self.dither()

        self.ladder = ladder

    def write_related_rates(self):
        words = TextMobject("Related rates")
        words.to_corner(UP+RIGHT)
        self.play(Write(words))
        self.dither()

    def measure_ladder(self):
        ladder = self.ladder
        ladder_brace = self.get_ladder_brace(ladder)

        x_and_y_lines = self.get_x_and_y_lines(ladder)
        x_line, y_line = x_and_y_lines

        y_label = TexMobject("%dm"%int(self.start_y))
        y_label.next_to(y_line, LEFT, buff = SMALL_BUFF)
        y_label.highlight(y_line.get_color())

        x_label = TexMobject("%dm"%int(self.start_x))
        x_label.next_to(x_line, UP)
        x_label.highlight(x_line.get_color())

        self.play(
            GrowFromCenter(ladder_brace),
            Write(ladder_brace.length_label),
        )
        self.dither()
        self.play(ShowCreation(y_line), Write(y_label))
        self.dither()
        self.play(ShowCreation(x_line), Write(x_label))
        self.dither(2)
        self.play(*map(FadeOut, [x_label, y_label]))

        self.ladder_brace = ladder_brace
        self.x_and_y_lines = x_and_y_lines

    def slide_ladder(self):
        ladder = self.ladder
        brace = self.ladder_brace
        x_and_y_lines = self.x_and_y_lines

        self.play(
            Transform(
                ladder, ladder.fallen,
                rate_func = None,
                run_time = self.start_y,
            ),
        )
        self.dither()


    #########

    def get_ladder_brace(self, ladder):
        vect = rotate_vector(LEFT, -self.get_ladder_angle())
        brace = Brace(ladder, vect)        
        length_string = "%dm"%int(self.get_ladder_length())
        length_label = brace.get_text(length_string)
        brace.length_label = length_label
        return brace

    def get_x_and_y_lines(self, ladder):
        top_point = ladder.get_corner(UP+RIGHT)
        bottom_point = ladder.get_corner(DOWN+LEFT)
        interim_point = top_point[0]*RIGHT + bottom_point[1]*UP
        y_line = Line(top_point, interim_point)
        y_line.highlight(RED)
        x_line = Line(bottom_point, interim_point)
        x_line.highlight(GREEN)

        return VGroup(x_line, y_line)

    def get_ladder_angle(self):
        if hasattr(self, "ladder"):
            c1 = self.ladder.get_corner(UP+RIGHT)
            c2 = self.ladder.get_corner(DOWN+LEFT)
            vect = c1-c2
            return np.pi/2 - angle_of_vector(vect)
        else:
            return np.arctan(self.start_x/self.start_y)

    def get_ladder_length(self):
        return np.linalg.norm([self.start_x, self.start_y])

















