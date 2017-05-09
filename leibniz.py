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
from scene.reconfigurable_scene import ReconfigurableScene
from scene.zoomed_scene import *
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

# revert_to_original_skipping_status


class Introduction(PiCreatureScene):
    def construct(self):
        self.introduce_three_objects()
        self.show_screen()

    def introduce_three_objects(self):
        primes = self.get_primes()
        primes.to_corner(UP+RIGHT)
        primes.shift(DOWN)
        plane = self.get_complex_numbers()
        plane.shift(2*LEFT)
        pi_group = self.get_pi_group()
        pi_group.next_to(primes, DOWN, buff = MED_LARGE_BUFF)
        pi_group.shift_onto_screen()

        morty = self.get_primary_pi_creature()
        video = VideoIcon()
        video.highlight(TEAL)
        video.next_to(morty.get_corner(UP+LEFT), UP)

        self.play(
            morty.change_mode, "raise_right_hand",
            DrawBorderThenFill(video)
        )
        self.dither()
        self.play(
            Write(primes, run_time = 2),
            morty.change_mode, "happy",
            video.scale_to_fit_height, 2*SPACE_WIDTH,
            video.center,
            video.set_fill, None, 0
        )
        self.dither()
        self.play(
            Write(plane, run_time = 2),
            morty.change, "raise_right_hand"
        )
        self.dither()
        self.remove(morty)
        morty = morty.copy()
        self.add(morty)
        self.play(
            ReplacementTransform(
                morty.body,
                pi_group.get_part_by_tex("pi"),
                run_time = 1
            ),
            FadeOut(VGroup(morty.eyes, morty.mouth)),
            Write(VGroup(*pi_group[1:]))
        )
        self.dither(2)
        self.play(
            plane.scale_to_fit_width, pi_group.get_width(),
            plane.next_to, pi_group, DOWN, MED_LARGE_BUFF
        )

    def show_screen(self):
        screen = ScreenRectangle(height = 4.3)
        screen.to_edge(LEFT)
        titles = VGroup(
            TextMobject("From zeta video"),
            TextMobject("Coming up")
        )
        for title in titles:
            title.next_to(screen, UP)
            title.highlight(YELLOW)
        self.play(
            ShowCreation(screen),
            FadeIn(titles[0])
        )
        self.show_frame()
        self.dither(2)
        self.play(Transform(*titles))
        self.dither(3)

    def get_primes(self):
        return TexMobject("2, 3, 5, 7, 11, 13, \\dots")

    def get_complex_numbers(self):
        plane = ComplexPlane(
            x_radius = 3,
            y_radius = 2.5,
        )
        plane.add_coordinates()
        point = plane.number_to_point(complex(1, 2))
        dot = Dot(point, color = YELLOW)
        label = TexMobject("1 + 2i")
        label.add_background_rectangle()
        label.next_to(dot, UP+RIGHT, buff = SMALL_BUFF)
        label.highlight(YELLOW)
        plane.label = label
        plane.add(dot, label)
        return plane

    def get_pi_group(self):
        result = TexMobject("\\pi", "=", "%.8f\\dots"%np.pi)
        pi = result.get_part_by_tex("pi")
        pi.scale(2, about_point = pi.get_right())
        pi.highlight(MAROON_B)
        return result


class ThisWontBeEasy(TeacherStudentsScene):
    def construct(self):
        self.say_words()
        self.show_sum()

    def say_words(self):
        self.teacher_says("This won't be easy")
        self.change_student_modes(
            "hooray", "sassy", "angry"
        )
        self.dither(2)
        self.play(RemovePiCreatureBubble(
            self.teacher,
            target_mode = "raise_right_hand",
        ))
        self.change_student_modes(
            *["pondering"]*3, 
            look_at_arg = 3*UP
        )

    def show_sum(self):
        line = NumberLine()
        line.add_numbers()









































