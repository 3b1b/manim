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
            "Why are you \\\\ talking so fast?",
            student_index = 0,
            target_mode = "sassy",
        )
        self.change_student_modes(*["sassy"]*3)
        self.play(self.get_teacher().change_mode, "guilty")
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

























































