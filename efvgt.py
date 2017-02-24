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

class ConfettiSpiril(Animation):
    CONFIG = {
        "x_start" : 0,
        "spiril_radius" : 1,
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
    }
    def construct(self):
        ##REMOVE##
        should_skip_animations = self.skip_animations
        self.skip_animations = True
        ##

        self.add_title()
        self.ask_about_square_symmetry()
        self.talk_through_90_degree_rotation()
        self.talk_through_vertical_flip()
        self.skip_animations = should_skip_animations
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
        square_radius = np.linalg.norm(self.square.get_corner(UP+RIGHT))
        arc = Arc(
            radius = square_radius + SMALL_BUFF,
            start_angle = np.pi/4 + SMALL_BUFF,
            angle = np.pi/2 - 2*SMALL_BUFF,
            color = YELLOW
        )
        arc.add_tip()
        arcs = VGroup(arc, *[
            arc.copy().rotate(i*np.pi/2)
            for i in range(1, 4)
        ])

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
        randy.next_to(self.square, DOWN+LEFT)
        randy.shift_onto_screen()
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
        pass

    def show_full_group(self):
        pass

    def show_top_actions(self):
        pass

    def show_bottom_actions(self):
        pass

    def name_dihedral_group(self):
        pass

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
        rotation = Rotate(square, angle = angle, axis = axis, **kwargs)
        if hasattr(square, "labels"):
            for label in rotation.target_mobject.labels:
                label.rotate_in_place(-angle, axis)

        if show_axis:
            axis_line = DashedLine(2*axis, -2*axis)
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


















































