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
from topics.complex_numbers import *
from scene import Scene
from scene.zoomed_scene import ZoomedScene
from scene.reconfigurable_scene import ReconfigurableScene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

ADDER_COLOR = GREEN
MULTIPLIER_COLOR = YELLOW

def normalize(vect):
    norm = np.linalg.norm(vect)
    if norm == 0:
        return OUT
    else:
        return vect/norm

def get_composite_rotation_angle_and_axis(angles, axes):
    angle1, axis1 = 0, OUT
    for angle2, axis2 in zip(angles, axes):
        ## Figure out what (angle3, axis3) is the same 
        ## as first applying (angle1, axis1), then (angle2, axis2)
        axis2 = normalize(axis2)
        dot = np.dot(axis2, axis1)
        cross = np.cross(axis2, axis1)
        angle3 = 2*np.arccos(
            np.cos(angle2/2)*np.cos(angle1/2) - \
            np.sin(angle2/2)*np.sin(angle1/2)*dot
        )
        axis3 = (
            np.sin(angle2/2)*np.cos(angle1/2)*axis2 + \
            np.cos(angle2/2)*np.sin(angle1/2)*axis1 + \
            np.sin(angle2/2)*np.sin(angle1/2)*cross
        )
        axis3 = normalize(axis3)
        angle1, axis1 = angle3, axis3

    if angle1 > np.pi:
        angle1 -= 2*np.pi
    return angle1, axis1

class ConfettiSpiril(Animation):
    CONFIG = {
        "x_start" : 0,
        "spiril_radius" : 0.5,
        "num_spirils" : 4,
        "run_time" : 10,
        "rate_func" : None,
    }
    def __init__(self, mobject, **kwargs):
        digest_config(self, kwargs)
        mobject.next_to(self.x_start*RIGHT + SPACE_HEIGHT*UP, UP)
        self.total_vert_shift = \
            2*SPACE_HEIGHT + mobject.get_height() + 2*MED_SMALL_BUFF
        
        Animation.__init__(self, mobject, **kwargs)

    def update_submobject(self, submobject, starting_submobject, alpha):
        submobject.points = np.array(starting_submobject.points)

    def update_mobject(self, alpha):
        Animation.update_mobject(self, alpha)
        angle = alpha*self.num_spirils*2*np.pi
        vert_shift = alpha*self.total_vert_shift

        start_center = self.mobject.get_center()
        self.mobject.shift(self.spiril_radius*OUT)
        self.mobject.rotate(angle, axis = UP, about_point = start_center)
        self.mobject.shift(vert_shift*DOWN)

class Anniversary(TeacherStudentsScene):
    CONFIG = {
        "num_confetti_squares" : 50,
    }
    def construct(self):
        self.celebrate()
        self.complain()

    def celebrate(self):
        title = TextMobject("2 year Anniversary!")
        title.scale(1.5)
        title.to_edge(UP)

        first_video = Rectangle(
            height = 2, width = 2*(16.0/9),
            stroke_color = WHITE,
            fill_color = "#111111",
            fill_opacity = 0.75,
        )
        first_video.next_to(self.get_teacher(), UP+LEFT)
        first_video.shift(RIGHT)
        formula = TexMobject("e^{\\pi i} = -1")
        formula.move_to(first_video)
        first_video.add(formula)

        hats = self.get_party_hats()
        confetti_spirils = self.get_confetti_animations()
        self.play(
            Write(title, run_time = 2),
            *[
                ApplyMethod(pi.change_mode, "hooray")
                for pi in self.get_pi_creatures()
            ]
        )
        self.play(
            DrawBorderThenFill(
                hats,
                submobject_mode = "lagged_start",
                rate_func = None,
                run_time = 2,
            ),
            *confetti_spirils + [
                Succession(
                    Animation(pi, run_time = 2),
                    ApplyMethod(pi.look, UP+LEFT),
                    ApplyMethod(pi.look, UP+RIGHT),
                    Animation(pi),
                    ApplyMethod(pi.look_at, first_video),
                    rate_func = None
                )
                for pi in self.get_students()
            ] + [
                Succession(
                    Animation(self.get_teacher(), run_time = 2),
                    Blink(self.get_teacher()),
                    Animation(self.get_teacher(), run_time = 2),
                    ApplyMethod(self.get_teacher().change_mode, "raise_right_hand"),
                    rate_func = None
                ),
                DrawBorderThenFill(
                    first_video, 
                    run_time = 10,
                    rate_func = squish_rate_func(smooth, 0.5, 0.7)
                )
            ]
        )
        self.change_student_modes(*["confused"]*3)

    def complain(self):
        self.student_says(
            "Why were you \\\\ talking so fast?",
            student_index = 0,
            target_mode = "sassy",
        )
        self.change_student_modes(*["sassy"]*3)
        self.play(self.get_teacher().change_mode, "shruggie")
        self.dither(2)

    def get_party_hats(self):
        hats = VGroup(*[
            PartyHat(
                pi_creature = pi,
                height = 0.5*pi.get_height()
            )
            for pi in self.get_pi_creatures()
        ])
        max_angle = np.pi/6
        for hat in hats:
            hat.rotate(
                random.random()*2*max_angle - max_angle,
                about_point = hat.get_bottom()
            )
        return hats

    def get_confetti_animations(self):
        colors = [RED, YELLOW, GREEN, BLUE, PURPLE, RED]
        confetti_squares = [
            Square(
                side_length = 0.2,
                stroke_width = 0,
                fill_opacity = 0.5,
                fill_color = random.choice(colors),
            )
            for x in range(self.num_confetti_squares)
        ]
        confetti_spirils = [
            ConfettiSpiril(
                square,
                x_start = 2*random.random()*SPACE_WIDTH - SPACE_WIDTH,
                rate_func = squish_rate_func(lambda t : t, a, a+0.5)
            )
            for a, square in zip(
                np.linspace(0, 0.5, self.num_confetti_squares),
                confetti_squares
            )
        ]
        return confetti_spirils

class WatchingScreen(PiCreatureScene):
    CONFIG = {
        "screen_height" : 5.5
    }
    def create_pi_creatures(self):
        randy = Randolph().to_corner(DOWN+LEFT)
        return VGroup(randy)

    def construct(self):
        screen = Rectangle(height = 9, width = 16)
        screen.scale_to_fit_height(self.screen_height)
        screen.to_corner(UP+RIGHT)

        self.add(screen)
        for mode in "erm", "pondering", "confused":
            self.dither()
            self.change_mode(mode)
            self.play(Animation(screen))
            self.dither()

class LetsStudyTheBasics(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("Let's learn some \\\\ group theory.")
        self.change_student_modes(*["happy"]*3)
        self.dither(2)

class QuickExplanation(ComplexTransformationScene):
    CONFIG = {
        "plane_config" : {
            "x_line_frequency" : 1,
            "y_line_frequency" : 1,
            "secondary_line_ratio" : 1,
            "space_unit_to_x_unit" : 1.5,
            "space_unit_to_y_unit" : 1.5,
        },
        "background_fade_factor" : 0.2,
        "background_label_scale_val" : 0.7,
        "velocity_color" : RED,
        "position_color" : YELLOW,
    }
    def construct(self):
        # self.add_transformable_plane()
        self.add_equation()
        self.add_explanation()
        self.add_vectors()

    def add_equation(self):
        equation = TexMobject(
            "\\frac{d(e^{it})}{dt}",
            "=",
            "i", "e^{it}"
        )
        equation[0].highlight(self.velocity_color)
        equation[-1].highlight(self.position_color)
        equation.add_background_rectangle()        
        brace = Brace(equation, UP)
        equation.add(brace)
        brace_text = TextMobject(
            "Velocity vector", "is a", 
            "$90^\\circ$ \\\\ rotation", 
            "of", "position vector"
        )
        brace_text[0].highlight(self.velocity_color)
        brace_text[-1].highlight(self.position_color)
        brace_text.add_background_rectangle()
        brace_text.scale(0.8)
        brace_text.to_corner(UP+LEFT, buff = MED_SMALL_BUFF)
        equation.next_to(brace_text, DOWN)

        self.add_foreground_mobjects(brace_text, equation)
        self.brace_text = brace_text

    def add_explanation(self):
        words = TextMobject("""
            Only a walk around the unit
            circle at rate 1 satisfies both
            this property and e^0 = 1.
        """)
        words.scale(0.8)
        words.add_background_rectangle()
        words.to_corner(UP+RIGHT, buff = MED_SMALL_BUFF)
        arrow = Arrow(RIGHT, 1.5*LEFT, color = WHITE)
        arrow.to_edge(UP)

        self.add(words, arrow)

    def add_vectors(self):
        right = self.z_to_point(1)
        s_vector = Arrow(
            ORIGIN, right,
            tip_length = 0.2,
            buff = 0,            
            color = self.position_color,
        )

        v_vector = s_vector.copy().rotate(np.pi/2)
        v_vector.highlight(self.velocity_color)
        circle = Circle(
            radius = self.z_to_point(1)[0],
            color = self.position_color
        )

        self.dither(2)
        self.play(ShowCreation(s_vector))
        self.play(ReplacementTransform(
            s_vector.copy(), v_vector, path_arc = np.pi/2
        ))
        self.dither()
        self.play(v_vector.shift, right)
        self.dither()
        self.vectors = VGroup(s_vector, v_vector)

        kwargs = {
            "rate_func" : None,
            "run_time" : 5,
        }
        rotation = Rotating(self.vectors, about_point = ORIGIN, **kwargs)
        self.play(
            ShowCreation(circle, **kwargs),
            rotation            
        )
        self.play(rotation)
        self.play(rotation)

class SymmetriesOfSquare(ThreeDScene):
    CONFIG = {
        "square_config" : {
            "side_length" : 2,
            "stroke_width" : 0,
            "fill_color" : BLUE,
            "fill_opacity" : 0.75,
        },
        "dashed_line_config" : {},
    }
    def construct(self):
        self.add_title()
        self.ask_about_square_symmetry()
        self.talk_through_90_degree_rotation()
        self.talk_through_vertical_flip()
        self.confused_by_lack_of_labels()
        self.add_labels()
        self.show_full_group()
        self.show_top_actions()
        self.show_bottom_actions()
        self.name_dihedral_group()

    def add_title(self):
        title = TextMobject("Groups", "$\\leftrightarrow$", "Symmetry")
        title.to_edge(UP)

        for index in 0, 2:
            self.play(Write(title[index], run_time = 1))
        self.play(GrowFromCenter(title[1]))
        self.dither()

        self.title = title

    def ask_about_square_symmetry(self):
        brace = Brace(self.title[-1])
        q_marks = brace.get_text("???")

        self.square = Square(**self.square_config)

        self.play(DrawBorderThenFill(self.square))
        self.play(GrowFromCenter(brace), Write(q_marks))
        self.rotate_square()
        self.dither()
        for axis in UP, UP+RIGHT:
            self.flip_square(axis)
            self.dither()
        self.rotate_square(-np.pi)
        self.dither()
        self.play(*map(FadeOut, [brace, q_marks]))

    def talk_through_90_degree_rotation(self):
        arcs = self.get_rotation_arcs(self.square, np.pi/2)

        self.play(*map(ShowCreation, arcs))
        self.dither()
        self.rotate_square(np.pi/2, run_time = 2)
        self.dither()
        self.play(FadeOut(arcs))
        self.dither()

    def talk_through_vertical_flip(self):
        self.flip_square(UP, run_time = 2)
        self.dither()

    def confused_by_lack_of_labels(self):
        randy = Randolph(mode = "confused")
        randy.next_to(self.square, LEFT, buff = LARGE_BUFF)
        randy.to_edge(DOWN)
        self.play(FadeIn(randy))
        for axis in OUT, RIGHT, UP:
            self.rotate_square(
                angle = np.pi, axis = axis,
                added_anims = [randy.look_at, self.square.points[0]]
            )
        self.play(Blink(randy))
        self.dither()

        self.randy = randy

    def add_labels(self):
        self.add_randy_to_square(self.square)

        self.play(
            FadeIn(self.square.randy),
            self.randy.change_mode, "happy",
            self.randy.look_at, self.square.randy.eyes
        )
        self.play(Blink(self.randy))
        self.play(FadeOut(self.randy))

        self.dither()

    def show_full_group(self):
        new_title = TextMobject("Group", "of", "symmetries")
        new_title.move_to(self.title)

        all_squares = VGroup(*[
            self.square.copy().scale(0.5)
            for x in range(8)
        ])
        all_squares.arrange_submobjects(RIGHT, buff = LARGE_BUFF)

        top_squares = VGroup(*all_squares[:4])
        bottom_squares = VGroup(*all_squares[4:])
        bottom_squares.next_to(top_squares, DOWN, buff = LARGE_BUFF)

        all_squares.scale_to_fit_width(2*SPACE_WIDTH-2*LARGE_BUFF)
        all_squares.center()
        all_squares.to_edge(DOWN, buff = LARGE_BUFF)

        self.play(ReplacementTransform(self.square, all_squares[0]))
        self.play(ReplacementTransform(self.title, new_title))
        self.title = new_title
        self.play(*[
            ApplyMethod(mob.highlight, GREY)
            for mob in self.title[1:]
        ])

        for square, angle in zip(all_squares[1:4], [np.pi/2, np.pi, -np.pi/2]):
            arcs = self.get_rotation_arcs(square, angle, MED_SMALL_BUFF)
            self.play(*map(FadeIn, [square, arcs]))
            square.rotation_kwargs = {"angle" : angle}
            self.rotate_square(square = square, **square.rotation_kwargs)
            square.add(arcs)

        for square, axis in zip(bottom_squares, [RIGHT, RIGHT+UP, UP, UP+LEFT]):
            axis_line = self.get_axis_line(square, axis)
            self.play(FadeIn(square))
            self.play(ShowCreation(axis_line))
            square.rotation_kwargs = {"angle" : np.pi, "axis" : axis}
            self.rotate_square(square = square, **square.rotation_kwargs)
            square.add(axis_line)
        self.dither()

        self.all_squares = all_squares

    def show_top_actions(self):
        all_squares = self.all_squares

        self.play(Indicate(all_squares[0]))
        self.dither()

        self.play(*[
            Rotate(
                square,
                rate_func = lambda t : -there_and_back(t),
                run_time = 3,
                about_point = square.get_center(),
                **square.rotation_kwargs
            )
            for square in all_squares[1:4]
        ])
        self.dither()

    def show_bottom_actions(self):
        for square in self.all_squares[4:]:
            self.rotate_square(
                square = square,
                rate_func = there_and_back,
                run_time = 2,
                **square.rotation_kwargs
            )
        self.dither()

    def name_dihedral_group(self):
        new_title = TextMobject(
            "``Dihedral group'' of order 8"
        )
        new_title.to_edge(UP)

        self.play(FadeOut(self.title))
        self.play(FadeIn(new_title))
        self.dither()

    ##########

    def rotate_square(
        self, 
        angle = np.pi/2, 
        axis = OUT, 
        square = None, 
        show_axis = False,
        added_anims = None,
        **kwargs
        ):
        if square is None:
            assert hasattr(self, "square")
            square = self.square
        added_anims = added_anims or []
        rotation = Rotate(
            square, 
            angle = angle, 
            axis = axis, 
            about_point = square.get_center(),
            **kwargs
        )
        if hasattr(square, "labels"):
            for label in rotation.target_mobject.labels:
                label.rotate_in_place(-angle, axis)

        if show_axis:
            axis_line = self.get_axis_line(square, axis)
            self.play(
                ShowCreation(axis_line),
                Animation(square)
            )
        self.play(rotation, *added_anims)
        if show_axis:
            self.play(
                FadeOut(axis_line),
                Animation(square)
            )

    def flip_square(self, axis = UP, **kwargs):
        self.rotate_square(
            angle = np.pi, 
            axis = axis,
            show_axis = True,
            **kwargs
        )

    def get_rotation_arcs(self, square, angle, angle_buff = SMALL_BUFF):
        square_radius = np.linalg.norm(
            square.points[0] - square.get_center()
        )
        arc = Arc(
            radius = square_radius + SMALL_BUFF,
            start_angle = np.pi/4 + np.sign(angle)*angle_buff,
            angle = angle - np.sign(angle)*2*angle_buff,
            color = YELLOW
        )
        arc.add_tip()
        if abs(angle) < 3*np.pi/4:
            angle_multiple_range = range(1, 4)
        else:
            angle_multiple_range = [2]
        arcs = VGroup(arc, *[
            arc.copy().rotate(i*np.pi/2)
            for i in angle_multiple_range
        ])
        arcs.move_to(square[0])

        return arcs

    def get_axis_line(self, square, axis):
        axis_line = DashedLine(2*axis, -2*axis, **self.dashed_line_config)
        axis_line.replace(square, dim_to_match = np.argmax(np.abs(axis)))
        axis_line.scale_in_place(1.2)
        return axis_line

    def add_labels_and_dots(self, square):
        labels = VGroup()
        dots = VGroup()
        for tex, vertex in zip("ABCD", square.get_anchors()):
            label = TexMobject(tex)
            label.add_background_rectangle()
            label.next_to(vertex, vertex-square.get_center(), SMALL_BUFF)
            labels.add(label)
            dot = Dot(vertex, color = WHITE)
            dots.add(dot)
        square.add(labels, dots)
        square.labels = labels
        square.dots = dots

    def add_randy_to_square(self, square, mode = "pondering"):
        randy = Randolph(mode = mode)
        randy.scale_to_fit_height(0.75*square.get_height())
        randy.move_to(square)
        square.add(randy)
        square.randy = randy

class ManyGroupsAreInfinite(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("Many groups are infinite")
        self.change_student_modes(*["pondering"]*3)
        self.dither(2)

class CircleSymmetries(Scene):
    CONFIG = {
        "circle_radius" : 2,
    }
    def construct(self):
        self.add_circle_and_title()        
        self.show_range_of_angles()
        self.associate_rotations_with_points()

    def add_circle_and_title(self):
        title = TextMobject("Group of rotations")
        title.to_edge(UP)

        circle = self.get_circle()

        self.play(Write(title), ShowCreation(circle, run_time = 2))
        self.dither()
        angles = [
            np.pi/2, -np.pi/3, 5*np.pi/6, 
            3*np.pi/2 + 0.1
        ]
        angles.append(-sum(angles))
        for angle in angles:
            self.play(Rotate(circle, angle = angle))
            self.dither()

        self.circle = circle

    def show_range_of_angles(self):
        self.add_radial_line()
        arc_circle = self.get_arc_circle()

        theta = TexMobject("\\theta = ")
        theta_value = DecimalNumber(0.00)
        theta_value.next_to(theta, RIGHT)
        theta_group = VGroup(theta, theta_value)
        theta_group.next_to(arc_circle, UP)
        def theta_value_update(theta_value, alpha):
            new_theta_value = DecimalNumber(alpha*2*np.pi)
            new_theta_value.scale_to_fit_height(theta.get_height())
            new_theta_value.next_to(theta, RIGHT)
            Transform(theta_value, new_theta_value).update(1)
            return new_theta_value


        self.play(FadeIn(theta_group))
        for rate_func in smooth, lambda t : smooth(1-t):
            self.play(
                Rotate(self.circle, 2*np.pi-0.001),
                ShowCreation(arc_circle),
                UpdateFromAlphaFunc(theta_value, theta_value_update),
                run_time = 7,
                rate_func = rate_func
            )
            self.dither()
        self.play(FadeOut(theta_group))
        self.dither()

    def associate_rotations_with_points(self):
        zero_dot = Dot(self.circle.point_from_proportion(0))
        zero_dot.highlight(RED)
        zero_arrow = Arrow(UP+RIGHT, ORIGIN)
        zero_arrow.highlight(zero_dot.get_color())
        zero_arrow.next_to(zero_dot, UP+RIGHT, buff = SMALL_BUFF)

        self.play(
            ShowCreation(zero_arrow),
            DrawBorderThenFill(zero_dot)
        )
        self.circle.add(zero_dot)
        self.dither()

        for alpha in 0.2, 0.6, 0.4, 0.8:
            point = self.circle.point_from_proportion(alpha)
            dot = Dot(point, color = YELLOW)
            vect = np.sign(point)
            arrow = Arrow(vect, ORIGIN)
            arrow.next_to(dot, vect, buff = SMALL_BUFF)
            arrow.highlight(dot.get_color())
            angle = alpha*2*np.pi

            self.play(
                ShowCreation(arrow),
                DrawBorderThenFill(dot)
            )
            self.play(
                Rotate(self.circle, angle, run_time = 2),
                Animation(dot)
            )
            self.dither()            
            self.play(
                Rotate(self.circle, -angle, run_time = 2),
                FadeOut(dot),
                FadeOut(arrow),
            )
            self.dither()

    ####

    def get_circle(self):
        circle = Circle(color = MAROON_B, radius = self.circle_radius)
        circle.ticks = VGroup()
        for alpha in np.arange(0, 1, 1./8):
            point = circle.point_from_proportion(alpha)
            tick = Line((1 - 0.05)*point, (1 + 0.05)*point)
            circle.ticks.add(tick)
        circle.add(circle.ticks)
        return circle

    def add_radial_line(self):
        radius = Line(
            self.circle.get_center(), 
            self.circle.point_from_proportion(0)
        )
        static_radius = radius.copy().highlight(GREY)

        self.play(ShowCreation(radius))
        self.add(static_radius, radius)
        self.circle.radius = radius
        self.circle.static_radius = static_radius
        self.circle.add(radius)

    def get_arc_circle(self):
        arc_radius = self.circle_radius/5.0
        arc_circle = Circle(
            radius = arc_radius,
            color = WHITE
        )
        return arc_circle

class GroupOfCubeSymmetries(ThreeDScene):
    CONFIG = {
        "cube_opacity" : 0.5,
        "cube_colors" : [BLUE],
        "put_randy_on_cube" : True,
    }
    def construct(self):
        title = TextMobject("Group of cube symmetries")
        title.to_edge(UP)
        self.add(title)

        cube = self.get_cube()

        face_centers = [face.get_center() for face in cube[0:7:2]]
        angle_axis_pairs = zip(3*[np.pi/2], face_centers)
        for i in range(3):
            ones = np.ones(3)
            ones[i] = -1
            axis = np.dot(ones, face_centers)
            angle_axis_pairs.append((2*np.pi/3, axis))

        for angle, axis in angle_axis_pairs:
            self.play(Rotate(
                cube, angle = angle, axis = axis,
                run_time = 2
            ))
            self.dither()

    def get_cube(self):
        cube = Cube(fill_opacity = self.cube_opacity)
        cube.gradient_highlight(*self.cube_colors)
        if self.put_randy_on_cube:
            randy = Randolph(mode = "pondering")
            randy.pupils.shift(0.01*OUT)
            randy.add(randy.pupils.copy().shift(0.02*IN))
            for submob in randy.submobject_family():
                submob.part_of_three_d_mobject = True
            randy.scale(0.5)
            face = cube[1]
            randy.move_to(face)
            face.add(randy)
        pose_matrix = self.get_pose_matrix()
        cube.apply_function(
            lambda p : np.dot(p, pose_matrix.T),
            maintain_smoothness = False
        )
        return cube

    def get_pose_matrix(self):
        return np.dot(
            rotation_matrix(np.pi/8, UP),
            rotation_matrix(np.pi/24, RIGHT)
        )

class HowDoSymmetriesPlayWithEachOther(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "How do symmetries \\\\ play with each other?",
            target_mode = "hesitant",
        )
        self.change_student_modes("pondering", "maybe", "confused")
        self.dither(2)

class AddSquareSymmetries(SymmetriesOfSquare):
    def construct(self):
        square = Square(**self.square_config)
        square.flip(RIGHT)
        square.shift(DOWN)
        self.add_randy_to_square(square, mode = "shruggie")
        alt_square = square.copy()
        equals = TexMobject("=")
        equals.move_to(square)

        equation_square = Square(**self.square_config)
        equation = VGroup(
            equation_square, TexMobject("+"), 
            equation_square.copy(), TexMobject("="),
            equation_square.copy(),
        )
        equation[0].add(self.get_rotation_arcs(
            equation[0], np.pi/2,
        ))
        equation[2].add(self.get_axis_line(equation[4], UP))
        equation[4].add(self.get_axis_line(equation[4], UP+RIGHT))
        for mob in equation[::2]:
            mob.scale(0.5)
        equation.arrange_submobjects(RIGHT)
        equation.to_edge(UP)

        arcs = self.get_rotation_arcs(square, np.pi/2)

        self.add(square)
        self.play(FadeIn(arcs))
        self.rotate_square(
            square = square, angle = np.pi/2,
            added_anims = map(FadeIn, equation[:2])
        )
        self.dither()
        self.play(FadeOut(arcs))
        self.flip_square(
            square = square, axis = UP,
            added_anims = map(FadeIn, equation[2:4])
        )
        self.dither()
        alt_square.next_to(equals, RIGHT, buff = LARGE_BUFF)
        alt_square.save_state()
        alt_square.move_to(square)
        alt_square.set_fill(opacity = 0)
        self.play(
            square.next_to, equals, LEFT, LARGE_BUFF,
            alt_square.restore,
            Write(equals)
        )
        self.flip_square(
            square = alt_square, axis = UP+RIGHT,
            added_anims = map(FadeIn, equation[4:]),
        )
        self.dither(2)

        ## Reiterate composition
        self.rotate_square(square = square, angle = np.pi/2)
        self.flip_square(square = square, axis = UP)
        self.dither()
        self.flip_square(square = alt_square, axis = UP+RIGHT)
        self.dither()

class AddCircleSymmetries(CircleSymmetries):
    def construct(self):
        circle = self.circle = self.get_circle()
        arc_circle = self.get_arc_circle()
        angles = [3*np.pi/2, 2*np.pi/3, np.pi/6]
        arcs = [
            arc_circle.copy().scale(scalar)
            for scalar in [1, 1.2, 1.4]
        ]

        equation = TexMobject(
            "270^\\circ", "+", "120^\\circ", "=", "30^\\circ",
        )
        equation.to_edge(UP)

        colors = [BLUE, YELLOW, GREEN]
        for color, arc, term in zip(colors, arcs, equation[::2]):
            arc.highlight(color)
            term.highlight(color)

        self.play(FadeIn(circle))
        self.add_radial_line()
        alt_radius = circle.radius.copy()
        alt_radius.highlight(GREY)
        alt_circle = circle.copy()
        equals = TexMobject("=")
        equals.move_to(circle)

        def rotate(circle, angle, arc, terms):
            self.play(
                Rotate(circle, angle, in_place = True),
                ShowCreation(
                    arc,
                    rate_func = lambda t : (angle/(2*np.pi))*smooth(t)
                ),
                Write(VGroup(*terms)),
                run_time = 2,
            )

        rotate(circle, angles[0], arcs[0], equation[:2])
        self.dither()
        circle.add(alt_radius)
        rotate(circle, angles[1], arcs[1], equation[2:4])
        self.play(FadeOut(alt_radius))
        circle.remove(alt_radius)
        self.dither()

        circle.add(circle.static_radius)
        circle.add(*arcs[:2])

        alt_static_radius = circle.static_radius.copy()
        alt_circle.add(alt_static_radius)
        alt_circle.next_to(equals, RIGHT, buff = LARGE_BUFF)
        alt_circle.save_state()
        alt_circle.move_to(circle)
        alt_circle.set_stroke(width = 0)
        self.play(
            circle.next_to, equals, LEFT, LARGE_BUFF,
            alt_circle.restore,
            Write(equals)
        )
        arcs[2].shift(alt_circle.get_center())
        alt_circle.remove(alt_static_radius)
        self.dither()
        rotate(alt_circle, angles[2], arcs[2], equation[4:])
        self.dither()
        self.play(
            Rotate(arcs[1], angles[0], about_point = circle.get_center())
        )
        self.dither(2)
        for term, arc in zip(equation[::2], arcs):
            self.play(*[
                ApplyMethod(mob.scale_in_place, 1.2, rate_func = there_and_back)
                for mob in term, arc
            ])
            self.dither()

class AddCubeSymmetries(GroupOfCubeSymmetries):
    CONFIG = {
        "angle_axis_pairs" : [
            (np.pi/2, RIGHT),
            (np.pi/2, UP),
        ],
        "cube_opacity" : 0.5,
        "cube_colors" : [BLUE],
    }
    def construct(self):
        angle_axis_pairs = list(self.angle_axis_pairs)
        angle_axis_pairs.append(
            self.get_composition_angle_and_axis()
        )
        self.pose_matrix = self.get_pose_matrix()
        cube = self.get_cube()

        equation = cube1, plus, cube2, equals, cube3 = VGroup(
            cube, TexMobject("+"), 
            cube.copy(), TexMobject("="),
            cube.copy()
        )
        equation.arrange_submobjects(RIGHT, buff = MED_LARGE_BUFF)
        equation.center()

        self.add(cube1)
        self.rotate_cube(cube1, *angle_axis_pairs[0])
        cube_copy = cube1.copy()
        cube_copy.set_fill(opacity = 0)
        self.play(
            cube_copy.move_to, cube2,
            cube_copy.set_fill, None, self.cube_opacity,
            Write(plus)
        )
        self.rotate_cube(cube_copy, *angle_axis_pairs[1])
        self.play(Write(equals))
        self.play(DrawBorderThenFill(cube3, run_time = 1))
        self.rotate_cube(cube3, *angle_axis_pairs[2])
        self.dither(2)

        times = TexMobject("\\times")
        times.scale(1.5)
        times.move_to(plus)
        times.highlight(RED)
        self.dither()
        self.play(ReplacementTransform(plus, times))
        self.play(Indicate(times))
        self.dither()
        for cube, (angle, axis) in zip([cube1, cube_copy, cube3], angle_axis_pairs):
            self.rotate_cube(
                cube, -angle, axis, add_arrows = False,
                rate_func = there_and_back,
                run_time = 1.5
            )
        self.dither()

    def rotate_cube(self, cube, angle, axis, add_arrows = True, **kwargs):
        axis = np.dot(axis, self.pose_matrix.T)
        anims = []
        if add_arrows:
            arrows = VGroup(*[
                Arc(
                    start_angle = np.pi/12+a, angle = 5*np.pi/6,
                    color = YELLOW
                ).add_tip()
                for a in 0, np.pi
            ])
            arrows.scale_to_fit_height(1.5*cube.get_height())
            z_to_axis = z_to_vector(axis)
            arrows.apply_function(
                lambda p : np.dot(p, z_to_axis.T),
                maintain_smoothness = False
            )
            arrows.move_to(cube)
            arrows.shift(-axis*cube.get_height()/2/np.linalg.norm(axis))
            anims += map(ShowCreation, arrows)
        anims.append(
            Rotate(
                cube, axis = axis, angle = angle, in_place = True,
                **kwargs
            )
        )
        self.play(*anims, run_time = 1.5)

    def get_composition_angle_and_axis(self):
        return get_composite_rotation_angle_and_axis(
            *zip(*self.angle_axis_pairs)
        )

class DihedralGroupStructure(SymmetriesOfSquare):
    CONFIG = {
        "dashed_line_config" : {
            "dashed_segment_length" : 0.1
        },
        "filed_sum_scale_factor" : 0.4,
        "num_rows" : 5,
    }
    def construct(self):
        angle_axis_pairs = [
            (np.pi/2, OUT),
            (np.pi, OUT),
            (-np.pi/2, OUT),
            # (np.pi, RIGHT),
            # (np.pi, UP+RIGHT),
            (np.pi, UP),
            (np.pi, UP+LEFT),
        ]
        pair_pairs = list(it.product(*[angle_axis_pairs]*2))
        random.shuffle(pair_pairs)
        for pair_pair in pair_pairs[:4]:
            sum_expression = self.demonstrate_sum(pair_pair)
            self.file_away_sum(sum_expression)
        for pair_pair in pair_pairs[4:]:
            should_skip_animations = self.skip_animations
            self.skip_animations = True
            sum_expression = self.demonstrate_sum(pair_pair)
            self.file_away_sum(sum_expression)
            self.skip_animations = should_skip_animations
            self.play(FadeIn(sum_expression))
        self.dither(3)


    def demonstrate_sum(self, angle_axis_pairs):
        angle_axis_pairs = list(angle_axis_pairs) + [
            get_composite_rotation_angle_and_axis(
                *zip(*angle_axis_pairs)
            )
        ]

        prototype_square = Square(**self.square_config)
        prototype_square.flip(RIGHT)
        self.add_randy_to_square(prototype_square)

        # self.add_labels_and_dots(prototype_square)
        prototype_square.scale(0.7)
        expression = s1, plus, s2, equals, s3 = VGroup(
            prototype_square, TexMobject("+").scale(2), 
            prototype_square.copy(), TexMobject("=").scale(2),
            prototype_square.copy()
        )

        final_expression = VGroup()
        for square, (angle, axis) in zip([s1, s2, s3], angle_axis_pairs):
            if np.cos(angle) > 0.5:
                square.action_illustration = VectorizedPoint()
            elif np.argmax(np.abs(axis)) == 2: ##Axis is in z direction
                square.action_illustration = self.get_rotation_arcs(
                    square, angle
                )
            else:
                square.action_illustration = self.get_axis_line(
                    square, axis
                )
            square.add(square.action_illustration)
            final_expression.add(square.action_illustration)
            square.rotation_kwargs = {
                "square" : square,
                "angle" : angle,
                "axis" : axis,
            }
        expression.arrange_submobjects()
        expression.scale_to_fit_width(SPACE_WIDTH+1)
        expression.to_edge(RIGHT, buff = SMALL_BUFF)
        for square in s1, s2, s3:
            square.remove(square.action_illustration)

        self.play(FadeIn(s1))
        self.play(*map(ShowCreation, s1.action_illustration))
        self.rotate_square(**s1.rotation_kwargs)

        s1_copy = s1.copy()
        self.play(
            # FadeIn(s2),
            s1_copy.move_to, s2,
            Write(plus)
        )
        Transform(s2, s1_copy).update(1)
        self.remove(s1_copy)
        self.add(s2)
        self.play(*map(ShowCreation, s2.action_illustration))
        self.rotate_square(**s2.rotation_kwargs)

        self.play(
            Write(equals),
            FadeIn(s3)
        )
        self.play(*map(ShowCreation, s3.action_illustration))
        self.rotate_square(**s3.rotation_kwargs)
        self.dither()
        final_expression.add(*expression)

        return final_expression

    def file_away_sum(self, sum_expression):
        if not hasattr(self, "num_sum_expressions"):
            self.num_sum_expressions = 0
        target = sum_expression.copy()
        target.scale(self.filed_sum_scale_factor)
        y_index = self.num_sum_expressions%self.num_rows
        y_prop = float(y_index)/(self.num_rows-1)
        y = interpolate(SPACE_HEIGHT-LARGE_BUFF, -SPACE_HEIGHT+LARGE_BUFF, y_prop)
        x_index = self.num_sum_expressions//self.num_rows
        x_spacing = 2*SPACE_WIDTH/3
        x = (x_index-1)*x_spacing

        target.move_to(x*RIGHT + y*UP)

        self.play(Transform(sum_expression, target))
        self.dither()

        self.num_sum_expressions += 1
        self.last_sum_expression = sum_expression

class ThisIsAVeryGeneralIdea(Scene):
    def construct(self):
        groups = TextMobject("Groups")
        groups.to_edge(UP)
        groups.highlight(BLUE)

        examples = VGroup(*map(TextMobject, [
            "Square matrices \\\\ \\small (Where $\\det(M) \\ne 0$)",
            "Molecular \\\\ symmetry",
            "Cryptography",
            "Numbers",
        ]))
        numbers = examples[-1]
        examples.arrange_submobjects(buff = LARGE_BUFF)
        examples.scale_to_fit_width(2*SPACE_WIDTH-1)
        examples.move_to(UP)

        lines = VGroup(*[
            Line(groups.get_bottom(), ex.get_top(), buff = MED_SMALL_BUFF)
            for ex in examples
        ])
        lines.highlight(groups.get_color())

        self.add(groups)

        for example, line in zip(examples, lines):
            self.play(
                ShowCreation(line),
                Write(example, run_time = 2)
            )
        self.dither()
        self.play(
            VGroup(*examples[:-1]).fade, 0.7,
            VGroup(*lines[:-1]).fade, 0.7,
        )

        self.play(
            numbers.scale, 1.2, numbers.get_corner(UP+RIGHT),
        )
        self.dither(2)

        sub_categories = VGroup(*map(TextMobject, [
            "Numbers \\\\ (Additive)",
            "Numbers \\\\ (Multiplicative)",
        ]))
        sub_categories.arrange_submobjects(RIGHT, buff = MED_LARGE_BUFF)
        sub_categories.next_to(numbers, DOWN, 1.5*LARGE_BUFF)
        sub_categories.to_edge(RIGHT)
        sub_categories[0].highlight(ADDER_COLOR)
        sub_categories[1].highlight(MULTIPLIER_COLOR)

        sub_lines = VGroup(*[
            Line(numbers.get_bottom(), sc.get_top(), buff = MED_SMALL_BUFF)
            for sc in sub_categories
        ])
        sub_lines.highlight(numbers.get_color())

        self.play(*it.chain(
            map(ShowCreation, sub_lines),
            map(Write, sub_categories)
        ))
        self.dither()

class NumbersAsActionsQ(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Numbers are actions?",
            target_mode = "confused",
        )
        self.change_student_modes("pondering", "confused", "erm")
        self.play(self.get_teacher().change_mode, "happy")
        self.dither(3)

class AdditiveGroupOfReals(Scene):
    CONFIG = {
        "number_line_center" : UP,
        "shadow_line_center" : DOWN,
        "zero_color" : GREEN_B,
    }
    def construct(self):
        self.add_number_line()
        self.show_example_slides(3, -7)
        self.write_group_of_slides()
        self.show_example_slides(2, 6, -1, -3)
        self.mark_zero()
        self.show_example_slides_labeled(3, -2)
        self.comment_on_zero_as_identity()
        self.show_example_slides_labeled(
            5.5, added_anims = [self.get_write_name_of_group_anim()]
        )
        self.show_example_additions((3, 2), (2, -5), (-4, 4))

    def add_number_line(self):
        number_line = NumberLine(
            x_min = -2*SPACE_WIDTH,
            x_max = 2*SPACE_WIDTH
        )

        number_line.shift(self.number_line_center)
        shadow_line = NumberLine(color = GREY, stroke_width = 2)
        shadow_line.shift(self.shadow_line_center)
        for line in number_line, shadow_line:
            line.add_numbers()
        shadow_line.numbers.fade(0.25)
        shadow_line.save_state()
        shadow_line.highlight(BLACK)
        shadow_line.move_to(number_line)


        self.play(*map(Write, number_line), run_time = 1)
        self.play(shadow_line.restore, Animation(number_line))
        self.dither()

        self.number_line = number_line
        self.shadow_line = shadow_line

    def show_example_slides(self, *nums):
        for num in nums:
            zero_point = self.number_line.number_to_point(0)            
            num_point = self.number_line.number_to_point(num)
            arrow = Arrow(zero_point, num_point, buff = 0)
            arrow.highlight(ADDER_COLOR)
            arrow.shift(MED_LARGE_BUFF*UP)

            self.play(ShowCreation(arrow))
            self.play(
                self.number_line.shift,
                num_point - zero_point,
                run_time = 2
            )
            self.play(FadeOut(arrow))

    def write_group_of_slides(self):
        title = TextMobject("Group of line symmetries")
        title.to_edge(UP)
        self.play(Write(title))
        self.title = title

    def mark_zero(self):
        dot = Dot(
            self.number_line.number_to_point(0),
            color = self.zero_color
        )
        arrow = Arrow(dot, color = self.zero_color)
        words = TextMobject("Follow zero")
        words.next_to(arrow.get_start(), UP)
        words.highlight(self.zero_color)

        self.play(
            ShowCreation(arrow),
            DrawBorderThenFill(dot),
            Write(words),
        )
        self.dither()
        self.play(*map(FadeOut, [arrow, words]))

        self.number_line.add(dot)

    def show_example_slides_labeled(self, *nums, **kwargs):
        for num in nums:
            line = DashedLine(
                self.number_line.number_to_point(num)+MED_LARGE_BUFF*UP,
                self.shadow_line.number_to_point(num)+MED_LARGE_BUFF*DOWN,
            )
            vect = self.number_line.number_to_point(num) - \
                   self.number_line.number_to_point(0)
            self.play(ShowCreation(line))
            self.dither()
            self.play(self.number_line.shift, vect, run_time = 2)
            self.dither()
            if "added_anims" in kwargs:
                self.play(*kwargs["added_anims"])
                self.dither()
            self.play(
                self.number_line.shift, -vect,
                FadeOut(line)
            )

    def comment_on_zero_as_identity(self):
        line = DashedLine(
            self.number_line.number_to_point(0)+MED_LARGE_BUFF*UP,
            self.shadow_line.number_to_point(0)+MED_LARGE_BUFF*DOWN,
        )
        words = TexMobject("0 \\leftrightarrow \\text{Do nothing}")
        words.shift(line.get_top()+MED_SMALL_BUFF*UP - words[0].get_bottom())

        self.play(
            ShowCreation(line),
            Write(words)
        )
        self.dither(2)
        self.play(*map(FadeOut, [line, words]))

    def get_write_name_of_group_anim(self):
        new_title = TextMobject("Additive group of real numbers")
        VGroup(*new_title[-len("realnumbers"):]).highlight(BLUE)
        VGroup(*new_title[:len("Additive")]).highlight(ADDER_COLOR)
        new_title.to_edge(UP)
        return Transform(self.title, new_title)

    def show_example_additions(self, *num_pairs):
        for num_pair in num_pairs:
            num_mobs = VGroup()
            arrows = VGroup()
            self.number_line.save_state()
            for num in num_pair:
                zero_point, num_point, arrow, num_mob = \
                    self.get_adder_mobs(num)
                if len(num_mobs) > 0:
                    last_num_mob = num_mobs[0]
                    x = num_mob.get_center()[0]
                    if x < last_num_mob.get_right()[0] and x > last_num_mob.get_left()[0]:
                        num_mob.next_to(last_num_mob, RIGHT)
                num_mobs.add(num_mob)
                arrows.add(arrow)

                self.play(
                    ShowCreation(arrow),
                    Write(num_mob, run_time = 1)
                )
                self.play(
                    self.number_line.shift, 
                    num_point - zero_point
                )
                self.dither()
            #Reset
            self.play(
                FadeOut(num_mobs),
                FadeOut(self.number_line)
            )
            ApplyMethod(self.number_line.restore).update(1)
            self.play(FadeIn(self.number_line))

            #Sum arrow
            num = sum(num_pair)
            zero_point, sum_point, arrow, sum_mob = \
                self.get_adder_mobs(sum(num_pair))
            VGroup(arrow, sum_mob).shift(MED_LARGE_BUFF*UP)
            arrows.add(arrow)
            self.play(
                ShowCreation(arrow),
                Write(sum_mob, run_time = 1)
            )
            self.dither()
            self.play(
                self.number_line.shift, 
                num_point - zero_point,
                run_time = 2
            )
            self.dither()
            self.play(
                self.number_line.restore,
                *map(FadeOut, [arrows, sum_mob])
            )

    def get_adder_mobs(self, num):
        zero_point = self.number_line.number_to_point(0)            
        num_point = self.number_line.number_to_point(num)
        arrow = Arrow(zero_point, num_point, buff = 0)
        arrow.highlight(ADDER_COLOR)
        arrow.shift(MED_SMALL_BUFF*UP)
        if num == 0:
            arrow = DashedLine(UP, ORIGIN)
            arrow.move_to(zero_point)
        elif num < 0:
            arrow.highlight(RED)
            arrow.shift(SMALL_BUFF*UP)
        sign = "+" if num >= 0 else ""
        num_mob = TexMobject(sign + str(num))
        num_mob.next_to(arrow, UP)
        num_mob.highlight(arrow.get_color())
        return zero_point, num_point, arrow, num_mob

class AdditiveGroupOfComplexNumbers(ComplexTransformationScene):
    CONFIG = {
        "x_min" : -2*int(SPACE_WIDTH),
        "x_max" : 2*int(SPACE_WIDTH),
        "y_min" : -2*SPACE_HEIGHT,
        "y_max" : 2*SPACE_HEIGHT,
        "example_points" : [
            complex(3, 2),
            complex(1, -3),
        ]
    }
    def construct(self):
        self.add_plane()
        self.show_vertical_slide()
        self.show_example_point()
        self.show_example_addition()
        self.write_group_name()
        self.show_some_random_slides()

    def add_plane(self):
        self.add_transformable_plane(animate = True)
        zero_dot = Dot(
            self.z_to_point(0),
            color = ADDER_COLOR
        )
        self.play(ShowCreation(zero_dot))
        self.plane.add(zero_dot)
        self.dither()

    def show_vertical_slide(self):
        dots = VGroup(*[
            Dot(self.z_to_point(complex(0, i)))
            for i in range(1, 4)
        ])
        dots.highlight(YELLOW)
        labels = VGroup(*self.imag_labels[-3:])

        arrow = Arrow(ORIGIN, dots[-1].get_center(), buff = 0)
        arrow.highlight(ADDER_COLOR)

        self.plane.save_state()
        for dot, label in zip(dots, labels):
            self.play(
                Indicate(label),
                ShowCreation(dot)
            )
        self.add_foreground_mobjects(dots)
        self.dither()
        self.play(ShowCreation(arrow))
        self.play(
            self.plane.shift, dots[-1].get_center(),
            Animation(arrow),
            run_time = 2
        )
        self.dither()
        self.play(FadeOut(arrow))
        self.play(
            self.plane.shift, 6*DOWN,
            run_time = 2,
        )
        self.play(self.plane.restore, run_time = 2)
        self.foreground_mobjects.remove(dots)
        self.play(FadeOut(dots))

    def show_example_point(self):
        z = self.example_points[0]
        point = self.z_to_point(z)
        dot = Dot(point, color = YELLOW)
        arrow = Vector(point, buff = dot.radius)
        arrow.highlight(dot.get_color())
        label = TexMobject("%d + %di"%(z.real, z.imag))
        label.next_to(point, UP)
        label.highlight(dot.get_color())
        label.add_background_rectangle()

        real_arrow = Vector(self.z_to_point(z.real))
        imag_arrow = Vector(self.z_to_point(z - z.real))
        VGroup(real_arrow, imag_arrow).highlight(ADDER_COLOR)

        self.play(
            Write(label),
            DrawBorderThenFill(dot)
        )
        self.dither()
        self.play(ShowCreation(arrow))
        self.add_foreground_mobjects(label, dot, arrow)
        self.dither()
        self.slide(z)
        self.dither()
        self.play(FadeOut(self.plane))
        self.plane.restore()
        self.plane.set_stroke(width = 0)
        self.play(self.plane.restore)
        self.play(ShowCreation(real_arrow))
        self.add_foreground_mobjects(real_arrow)
        self.slide(z.real)
        self.dither()
        self.play(ShowCreation(imag_arrow))
        self.dither()
        self.play(imag_arrow.shift, self.z_to_point(z.real))
        self.add_foreground_mobjects(imag_arrow)
        self.slide(z - z.real)
        self.dither()

        self.foreground_mobjects.remove(real_arrow)
        self.foreground_mobjects.remove(imag_arrow)
        self.play(*map(FadeOut, [real_arrow, imag_arrow, self.plane]))
        self.plane.restore()
        self.plane.set_stroke(0)
        self.play(self.plane.restore)

        self.z1 = z
        self.arrow1 = arrow
        self.dot1 = dot
        self.label1 = label

    def show_example_addition(self):
        z1 = self.z1
        arrow1 = self.arrow1
        dot1 = self.dot1
        label1 = self.label1

        z2 = self.example_points[1]
        point2 = self.z_to_point(z2)
        dot2 = Dot(point2, color = TEAL)
        arrow2 = Vector(
            point2, 
            buff = dot2.radius,
            color = dot2.get_color()
        )
        label2 = TexMobject(
            "%d %di"%(z2.real, z2.imag)
        )
        label2.next_to(point2, UP+RIGHT)
        label2.highlight(dot2.get_color())
        label2.add_background_rectangle()

        self.play(ShowCreation(arrow2))
        self.play(
            DrawBorderThenFill(dot2),
            Write(label2)
        )
        self.add_foreground_mobjects(arrow2, dot2, label2)
        self.dither()

        self.slide(z1)
        arrow2_copy = arrow2.copy()
        self.play(arrow2_copy.shift, self.z_to_point(z1))
        self.add_foreground_mobjects(arrow2_copy)
        self.slide(z2)
        self.play(FadeOut(arrow2_copy))
        self.foreground_mobjects.remove(arrow2_copy)
        self.dither()

        ##Break into components
        real_arrow, imag_arrow = component_arrows = [
            Vector(
                self.z_to_point(z),
                color = ADDER_COLOR
            )
            for z in [
                z1.real+z2.real,
                complex(0, z1.imag+z2.imag),
            ]
        ]
        imag_arrow.shift(real_arrow.get_end())
        plus = TexMobject("+").next_to(
            real_arrow.get_center(), UP+RIGHT
        )
        plus.add_background_rectangle()

        rp1, rp2, ip1, ip2 = label_parts = [
            VGroup(label1[1][0].copy()),
            VGroup(label2[1][0].copy()),
            VGroup(*label1[1][2:]).copy(),
            VGroup(*label2[1][1:]).copy(),
        ]
        for part in label_parts:
            part.generate_target()

        rp1.target.next_to(plus, LEFT)
        rp2.target.next_to(plus, RIGHT)
        ip1.target.next_to(imag_arrow.get_center(), RIGHT)
        ip1.target.shift(SMALL_BUFF*DOWN)
        ip2.target.next_to(ip1.target, RIGHT)

        real_background_rect = BackgroundRectangle(
            VGroup(rp1.target, rp2.target)
        )
        imag_background_rect = BackgroundRectangle(
            VGroup(ip1.target, ip2.target)
        )

        self.play(
            ShowCreation(real_arrow),
            ShowCreation(
                real_background_rect,
                rate_func = squish_rate_func(smooth, 0.75, 1),
            ),
            Write(plus),
            *map(MoveToTarget, [rp1, rp2])
        )
        self.dither()
        self.play(
            ShowCreation(imag_arrow),
            ShowCreation(
                imag_background_rect,
                rate_func = squish_rate_func(smooth, 0.75, 1),
            ),
            *map(MoveToTarget, [ip1, ip2])
        )
        self.dither(2)
        to_remove = [
            arrow1, dot1, label1,
            arrow2, dot2, label2,
            real_background_rect,
            imag_background_rect,
            plus,
        ] + label_parts + component_arrows
        for mob in to_remove:
            if mob in self.foreground_mobjects:
                self.foreground_mobjects.remove(mob)
        self.play(*map(FadeOut, to_remove))
        self.play(self.plane.restore, run_time = 2)
        self.dither()

    def write_group_name(self):
        title = TextMobject(
            "Additive", "group of", "complex numbers"
        )
        title[0].highlight(ADDER_COLOR)
        title[2].highlight(BLUE)
        title.add_background_rectangle()
        title.to_edge(UP, buff = MED_SMALL_BUFF)

        self.play(Write(title))
        self.add_foreground_mobjects(title)
        self.dither()

    def show_some_random_slides(self):
        example_slides = [
            complex(3),
            complex(0, 2),
            complex(-4, -1),
            complex(-2, -1),
            complex(4, 2),
        ]
        for z in example_slides:
            self.slide(z)
            self.dither()

    #########

    def slide(self, z, *added_anims, **kwargs):
        kwargs["run_time"] = kwargs.get("run_time", 2)
        self.play(
            ApplyMethod(
                self.plane.shift, self.z_to_point(z),
                **kwargs
            ),
            *added_anims
        )


























