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
        "n_rungs" : 7,
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
            for a in np.linspace(0, 1, 2*self.n_rungs+1)[1:-1:2]
        ]
        self.add(left_line, right_line, *rungs)
        self.center()

class RelatedRatesExample(ThreeDScene):
    CONFIG = {
        "start_x" : 3.0,
        "start_y" : 4.0,
        "wall_dimensions" : [0.3, 5, 5],
        "wall_color" : color_gradient([GREY_BROWN, BLACK], 4)[1],
        "wall_center" : 1.5*LEFT+0.5*UP,
    }
    def construct(self):
        self.introduce_ladder()
        self.write_related_rates()
        self.measure_ladder()
        self.slide_ladder()
        self.write_equation()
        self.isolate_x_of_t()
        self.discuss_lhs_as_function()
        self.let_dt_pass()
        self.take_derivative_of_rhs()
        self.take_derivative_of_lhs()
        self.bring_back_velocity_arrows()
        self.replace_terms_in_final_form()
        self.write_final_solution()

    def introduce_ladder(self):
        ladder = Ladder(height = self.get_ladder_length())

        wall = Prism(
            dimensions = self.wall_dimensions,
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
            ladder_copy.shift(0.8*RIGHT) ##BAD!


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

        self.related_rates_words = words

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

        self.play(Write(ladder_brace))
        self.dither()
        self.play(ShowCreation(y_line), Write(y_label))
        self.dither()
        self.play(ShowCreation(x_line), Write(x_label))
        self.dither(2)
        self.play(*map(FadeOut, [x_label, y_label]))

        self.ladder_brace = ladder_brace
        self.x_and_y_lines = x_and_y_lines
        self.numerical_x_and_y_labels = VGroup(x_label, y_label)

    def slide_ladder(self):
        ladder = self.ladder
        brace = self.ladder_brace
        x_and_y_lines = self.x_and_y_lines
        x_line, y_line = x_and_y_lines

        down_arrow, left_arrow = [
            Arrow(ORIGIN, vect, color = YELLOW, buff = 0)
            for vect in DOWN, LEFT
        ]
        down_arrow.shift(y_line.get_start()+MED_SMALL_BUFF*RIGHT)
        left_arrow.shift(x_line.get_start()+SMALL_BUFF*DOWN)

        # speed_label = TexMobject("1 \\text{m}/\\text{s}")
        speed_label = TexMobject("1 \\frac{\\text{m}}{\\text{s}}")
        speed_label.next_to(down_arrow, RIGHT, buff = SMALL_BUFF)

        q_marks = TexMobject("???")
        q_marks.next_to(left_arrow, DOWN, buff = SMALL_BUFF)


        added_anims = [
            UpdateFromFunc(brace, self.update_brace),
            UpdateFromFunc(x_and_y_lines, self.update_x_and_y_lines),
            Animation(down_arrow),
        ]
        self.play(ShowCreation(down_arrow))
        self.play(Write(speed_label))
        self.let_ladder_fall(ladder, *added_anims)
        self.dither()
        self.reset_ladder(ladder, *added_anims)
        self.play(ShowCreation(left_arrow))
        self.play(Write(q_marks))
        self.dither()
        self.let_ladder_fall(ladder, *added_anims)
        self.dither()
        self.reset_ladder(ladder, *added_anims)
        self.dither()

        self.dy_arrow = down_arrow
        self.dy_label = speed_label
        self.dx_arrow = left_arrow
        self.dx_label = q_marks

    def write_equation(self):
        self.x_and_y_labels = self.get_x_and_y_labels()
        x_label, y_label = self.x_and_y_labels

        equation = TexMobject(
            "x(t)", "^2", "+", "y(t)", "^2", "=", "5^2"
        )
        equation[0].highlight(GREEN)
        equation[3].highlight(RED)
        equation.next_to(self.related_rates_words, DOWN, buff = MED_LARGE_BUFF)
        equation.to_edge(RIGHT, buff = LARGE_BUFF)

        self.play(Write(y_label))
        self.dither()
        self.let_ladder_fall(
            self.ladder,
            y_label.shift, self.start_y*DOWN/2,
            *self.get_added_anims_for_ladder_fall()[:-1],
            rate_func = lambda t : 0.2*there_and_back(t),
            run_time = 3
        )
        self.play(FocusOn(x_label))
        self.play(Write(x_label))
        self.dither(2)
        self.play(
            ReplacementTransform(x_label.copy(), equation[0]),
            ReplacementTransform(y_label.copy(), equation[3]),
            Write(VGroup(*np.array(equation)[[1, 2, 4, 5, 6]]))
        )
        self.dither(2)
        self.let_ladder_fall(
            self.ladder,
            *self.get_added_anims_for_ladder_fall(),
            rate_func = there_and_back,
            run_time = 6
        )
        self.dither()

        self.equation = equation

    def isolate_x_of_t(self):
        alt_equation = TexMobject(
            "x(t)", "=", "\\big(5^2", "-", "y(t)", "^2 \\big)", "^{1/2}",
        )
        alt_equation[0].highlight(GREEN)
        alt_equation[4].highlight(RED)
        alt_equation.next_to(self.equation, DOWN, buff = MED_LARGE_BUFF)
        alt_equation.to_edge(RIGHT)

        randy = Randolph()
        randy.next_to(
            alt_equation, DOWN, 
            buff = MED_LARGE_BUFF,
            aligned_edge = LEFT,
        )
        randy.look_at(alt_equation)

        find_dx_dt = TexMobject("\\text{Find } \\,", "\\frac{dx}{dt}")
        find_dx_dt.next_to(randy, RIGHT, aligned_edge = UP)
        find_dx_dt[1].highlight(GREEN)

        self.play(FadeIn(randy))
        self.play(
            randy.change_mode, "raise_right_hand", 
            randy.look_at, alt_equation,
            *[
                ReplacementTransform(
                    self.equation[i].copy(), 
                    alt_equation[j],
                    path_arc = np.pi/2,
                    run_time = 3,
                    rate_func = squish_rate_func(
                        smooth, j/12.0, (j+6)/12.0
                    )
                )
                for i, j in enumerate([0, 6, 3, 4, 5, 1, 2])
            ]
        )
        self.play(Blink(randy))
        self.dither()
        self.play(
            Write(find_dx_dt),
            randy.change_mode, "pondering",
            randy.look_at, find_dx_dt,
        )
        self.let_ladder_fall(
            self.ladder, *self.get_added_anims_for_ladder_fall(),
            run_time = 8,
            rate_func = there_and_back
        )
        self.play(*map(FadeOut, [
            randy, find_dx_dt, alt_equation
        ]))
        self.dither()

    def discuss_lhs_as_function(self):
        equation = self.equation
        lhs = VGroup(*equation[:5])
        brace = Brace(lhs, DOWN)
        function_of_time = brace.get_text(
            "Function of time"
        )
        constant_words = TextMobject(
            """that happens to
            be constant"""
        )
        constant_words.highlight(YELLOW)
        constant_words.next_to(function_of_time, DOWN)

        derivative = TexMobject(
            "\\frac{d\\left(x(t)^2 + y(t)^2 \\right)}{dt}"
        )
        derivative.next_to(equation, DOWN, buff = MED_LARGE_BUFF)
        derivative.shift( ##Align x terms
            equation[0][0].get_center()[0]*RIGHT-\
            derivative[2].get_center()[0]*RIGHT
        )
        derivative_interior = lhs.copy()
        derivative_interior.move_to(VGroup(*derivative[2:13]))
        derivative_scaffold = VGroup(
            *list(derivative[:2])+list(derivative[13:])
        )

        self.play(
            GrowFromCenter(brace),
            Write(function_of_time)
        )
        self.dither()
        self.play(Write(constant_words))
        self.let_ladder_fall(
            self.ladder, *self.get_added_anims_for_ladder_fall(),
            run_time = 6,
            rate_func = lambda t : 0.5*there_and_back(t)
        )
        self.dither()
        self.play(*map(FadeOut, [
            brace, constant_words, function_of_time
        ]))
        self.play(
            ReplacementTransform(lhs.copy(), derivative_interior),
            Write(derivative_scaffold),
        )
        self.dither()

        self.derivative = VGroup(
            derivative_scaffold, derivative_interior
        )

    def let_dt_pass(self):
        dt_words = TextMobject("After", "$dt$", "seconds...")
        dt_words.to_corner(UP+LEFT)
        dt = dt_words[1]
        dt.highlight(YELLOW)
        dt_brace = Brace(dt, buff = SMALL_BUFF)
        dt_brace_text = dt_brace.get_text("Think 0.01", buff = SMALL_BUFF)
        dt_brace_text.highlight(dt.get_color())

        shadow_ladder = self.ladder.copy()
        shadow_ladder.fade(0.5)

        x_line, y_line = self.x_and_y_lines
        y_top = y_line.get_start()
        x_left = x_line.get_start()

        self.play(Write(dt_words, run_time = 2))
        self.play(
            GrowFromCenter(dt_brace),
            Write(dt_brace_text, run_time = 2)
        )
        self.play(*map(FadeOut, [
            self.dy_arrow, self.dy_label, 
            self.dx_arrow, self.dx_label, 
        ]))
        self.add(shadow_ladder)
        self.let_ladder_fall(
            self.ladder, *self.get_added_anims_for_ladder_fall(),
            rate_func = lambda t : 0.1*smooth(t),
            run_time = 1
        )

        new_y_top = y_line.get_start()
        new_x_left = x_line.get_start()

        dy_line = Line(y_top, new_y_top)
        dy_brace = Brace(dy_line, RIGHT, buff = SMALL_BUFF)
        dy_label = dy_brace.get_text("$dy$", buff = SMALL_BUFF)
        dy_label.highlight(RED)

        dx_line = Line(x_left, new_x_left)
        dx_brace = Brace(dx_line, DOWN, buff = SMALL_BUFF)
        dx_label = dx_brace.get_text("$dx$")
        dx_label.highlight(GREEN)

        VGroup(dy_line, dx_line).highlight(YELLOW)

        for line, brace, label in (dy_line, dy_brace, dy_label), (dx_line, dx_brace, dx_label):
            self.play(
                ShowCreation(line),
                GrowFromCenter(brace),
                Write(label),
                run_time = 1
            )
        self.dither()
        self.play(Indicate(self.derivative[1]))
        self.dither()

        self.dy_group = VGroup(dy_line, dy_brace, dy_label)
        self.dx_group = VGroup(dx_line, dx_brace, dx_label)
        self.shadow_ladder = shadow_ladder

    def take_derivative_of_rhs(self):
        derivative = self.derivative
        equals_zero = TexMobject("= 0")
        equals_zero.next_to(derivative)

        rhs = self.equation[-1]

        self.play(Write(equals_zero))
        self.dither()
        self.play(FocusOn(rhs))
        self.play(Indicate(rhs))
        self.dither()
        self.reset_ladder(
            self.ladder, 
            *self.get_added_anims_for_ladder_fall()+[
                Animation(self.dy_group),
                Animation(self.dx_group),
            ],
            rate_func = there_and_back,
            run_time = 3
        )
        self.dither()

        self.equals_zero = equals_zero

    def take_derivative_of_lhs(self):
        derivative_scaffold, equation = self.derivative
        equals_zero_copy = self.equals_zero.copy()

        lhs_derivative = TexMobject(
            "2", "x(t)", "\\frac{dx}{dt}", "+",
            "2", "y(t)", "\\frac{dy}{dt}",
        )
        lhs_derivative[1].highlight(GREEN)
        VGroup(*lhs_derivative[2][:2]).highlight(GREEN)
        lhs_derivative[5].highlight(RED)
        VGroup(*lhs_derivative[6][:2]).highlight(RED)
        lhs_derivative.next_to(
            derivative_scaffold, DOWN,
            aligned_edge = RIGHT,
            buff = MED_LARGE_BUFF
        )
        equals_zero_copy.next_to(lhs_derivative, RIGHT)

        pairs = [
            (0, 1), (1, 0), #x^2 -> 2x
            (2, 3), (3, 5), (4, 4), #+y^2 -> +2y
        ]
        def perform_replacement(index_pairs):
            self.play(*[
                ReplacementTransform(
                    equation[i].copy(), lhs_derivative[j],
                    path_arc = np.pi/2,
                    run_time = 2
                )
                for i, j in index_pairs
            ])

        perform_replacement(pairs[:2])
        self.play(Write(lhs_derivative[2]))
        self.dither()
        self.play(Indicate(
            VGroup(
                *list(lhs_derivative[:2])+\
                list(lhs_derivative[2][:2])
            ),
            run_time = 2
        ))
        self.play(Indicate(VGroup(*lhs_derivative[2][3:])))
        self.dither(2)
        perform_replacement(pairs[2:])
        self.play(Write(lhs_derivative[6]))
        self.dither()

        self.play(FocusOn(self.equals_zero))
        self.play(ReplacementTransform(
            self.equals_zero.copy(),
            equals_zero_copy
        ))
        self.dither(2)

        lhs_derivative.add(equals_zero_copy)
        self.lhs_derivative = lhs_derivative

    def bring_back_velocity_arrows(self):
        dx_dy_group = VGroup(self.dx_group, self.dy_group)
        arrow_group = VGroup(
            self.dy_arrow, self.dy_label,
            self.dx_arrow, self.dx_label,
        )
        ladder_fall_args = [self.ladder] + self.get_added_anims_for_ladder_fall()


        self.reset_ladder(*ladder_fall_args + [
            FadeOut(dx_dy_group),
            FadeOut(self.derivative),
            FadeOut(self.equals_zero),
            self.lhs_derivative.shift, 2*UP,
        ])
        self.remove(self.shadow_ladder)
        self.play(FadeIn(arrow_group))
        self.let_ladder_fall(*ladder_fall_args)
        self.dither()
        self.reset_ladder(*ladder_fall_args)
        self.dither()

    def replace_terms_in_final_form(self):
        x_label, y_label = self.x_and_y_labels
        num_x_label, num_y_label = self.numerical_x_and_y_labels

        new_lhs_derivative = TexMobject(
            "2", "(%d)"%int(self.start_x), "\\frac{dx}{dt}", "+",
            "2", "(%d)"%int(self.start_y), "(1)",
            "= 0"
        )
        new_lhs_derivative[1].highlight(GREEN)
        VGroup(*new_lhs_derivative[2][:2]).highlight(GREEN)
        new_lhs_derivative[5].highlight(RED)
        new_lhs_derivative.next_to(
            self.lhs_derivative, DOWN,
            buff = MED_LARGE_BUFF,
            aligned_edge = RIGHT
        )
        def fill_in_equation_part(*indices):
            self.play(*[
                ReplacementTransform(
                    self.lhs_derivative[i].copy(),
                    new_lhs_derivative[i],
                    run_time = 2
                )
                for i in indices
            ])

        self.play(FadeOut(y_label), FadeIn(num_y_label))
        fill_in_equation_part(3, 4, 5)
        self.play(FadeOut(x_label), FadeIn(num_x_label))
        for indices in [(0, 1), (6,), (2, 7)]:
            fill_in_equation_part(*indices)
            self.dither()
        self.dither()

        self.new_lhs_derivative = new_lhs_derivative

    def write_final_solution(self):
        solution = TexMobject(
            "\\frac{dx}{dt} = \\frac{-4}{3}"
        )
        for i in 0, 1, -1:
            solution[i].highlight(GREEN)
        solution[-3].highlight(RED)
        solution.next_to(
            self.new_lhs_derivative, DOWN,
            buff = MED_LARGE_BUFF,
            aligned_edge = RIGHT
        )

        box = Rectangle(color = YELLOW)
        box.replace(solution)
        box.scale_in_place(1.3)

        self.play(Write(solution))
        self.dither()
        self.play(ShowCreation(box))
        self.dither()

    #########

    def get_added_anims_for_ladder_fall(self):
        return [
            UpdateFromFunc(self.ladder_brace, self.update_brace),
            UpdateFromFunc(self.x_and_y_lines, self.update_x_and_y_lines),
            UpdateFromFunc(self.x_and_y_labels, self.update_x_and_y_labels),
        ]

    def let_ladder_fall(self, ladder, *added_anims, **kwargs):
        kwargs["run_time"] = kwargs.get("run_time", self.start_y)
        kwargs["rate_func"] = kwargs.get("rate_func", None)
        self.play(
            Transform(ladder, ladder.fallen),
            *added_anims,
            **kwargs
        )

    def reset_ladder(self, ladder, *added_anims, **kwargs):
        kwargs["run_time"] = kwargs.get("run_time", 2)
        self.play(
            Transform(ladder, ladder.target),
            *added_anims,
            **kwargs
        )

    def update_brace(self, brace):
        Transform(
            brace, self.get_ladder_brace(self.ladder)
        ).update(1)
        return brace

    def update_x_and_y_lines(self, x_and_y_lines):
        Transform(
            x_and_y_lines,
            self.get_x_and_y_lines(self.ladder)
        ).update(1)
        return x_and_y_lines

    def update_x_and_y_labels(self, x_and_y_labels):
        Transform(
            x_and_y_labels,
            self.get_x_and_y_labels()
        ).update(1)
        return x_and_y_labels

    def get_ladder_brace(self, ladder):
        vect = rotate_vector(LEFT, -self.get_ladder_angle())
        brace = Brace(ladder, vect)        
        length_string = "%dm"%int(self.get_ladder_length())
        length_label = brace.get_text(
            length_string, use_next_to = False
        )
        brace.add(length_label)
        brace.length_label = length_label
        return brace

    def get_x_and_y_labels(self):
        x_line, y_line = self.x_and_y_lines

        x_label = TexMobject("x(t)")
        x_label.highlight(x_line.get_color())
        x_label.next_to(x_line, DOWN, buff = SMALL_BUFF)

        y_label = TexMobject("y(t)")
        y_label.highlight(y_line.get_color())
        y_label.next_to(y_line, LEFT, buff = SMALL_BUFF)

        return VGroup(x_label, y_label)

    def get_x_and_y_lines(self, ladder):
        bottom_point, top_point = np.array(ladder[1].get_start_and_end())
        interim_point = top_point[0]*RIGHT + bottom_point[1]*UP
        interim_point += SMALL_BUFF*DOWN
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

















