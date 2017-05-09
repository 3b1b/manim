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

class ShowSum(TeacherStudentsScene):
    CONFIG = {
        "num_terms_to_add" : 40,
    }
    def construct(self):
        self.say_words()
        self.show_sum()

    def say_words(self):
        self.teacher_says("This won't be easy")
        self.change_student_modes(
            "hooray", "sassy", "angry"
        )
        self.dither(2)

    def show_sum(self):
        line = UnitInterval()
        line.add_numbers(0, 1)
        line.shift(UP)
        sum_point = line.number_to_point(np.pi/4)

        numbers = [0] + [
            ((-1)**n)/(2.0*n + 1) 
            for n in range(self.num_terms_to_add)
        ]
        partial_sums = np.cumsum(numbers)
        points = map(line.number_to_point, partial_sums)
        arrows = [
            Arrow(
                p1, p2, 
                tip_length = 0.2*min(1, np.linalg.norm(p1-p2)),
                buff = 0
            )
            for p1, p2 in zip(points, points[1:])
        ]
        dot = Dot(points[0])

        sum_mob = TexMobject(
            "1", "-\\frac{1}{3}", "+\\frac{1}{5}", 
            "-\\frac{1}{7}", "+\\cdots"
        )
        sum_mob.to_edge(UP)
        sum_mob.shift(LEFT)
        rhs = TexMobject(
            "=", "\\frac{\\pi}{4}",
            "\\approx %.5f\\dots"%(np.pi/4)
        )
        rhs.next_to(sum_mob, RIGHT)
        rhs.highlight_by_tex("pi", YELLOW)
        sum_arrow = Arrow(
            rhs.get_part_by_tex("pi"),
            sum_point
        )
        fading_terms = [
            TexMobject(sign + "\\frac{1}{%d}"%(2*n + 1))
            for n, sign in zip(
                range(self.num_terms_to_add),
                it.cycle("+-")
            )
        ]
        for fading_term, arrow in zip(fading_terms, arrows):
            fading_term.next_to(arrow, UP)

        terms = it.chain(sum_mob, it.repeat(None))
        last_arrows = it.chain([None], arrows)
        last_fading_terms = it.chain([None], fading_terms)

        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = line,
            added_anims = [
                FadeIn(VGroup(line, dot)),
                RemovePiCreatureBubble(
                    self.teacher,
                    target_mode = "raise_right_hand"
                )
            ]
            
        )
        run_time = 1
        for term, arrow, last_arrow, fading_term, last_fading_term in zip(
            terms, arrows, last_arrows, fading_terms, last_fading_terms
            ):
            anims = []
            if term:
                anims.append(Write(term))
            if last_arrow:
                anims.append(FadeOut(last_arrow))
            if last_fading_term:
                anims.append(FadeOut(last_fading_term))
            dot_movement = ApplyMethod(dot.move_to, arrow.get_end())
            anims.append(ShowCreation(arrow))
            anims.append(dot_movement)
            anims.append(FadeIn(fading_term))
            self.play(*anims, run_time = run_time)
            if term:
                self.dither()
            else:
                run_time *= 0.8
        self.play(
            FadeOut(arrow),
            FadeOut(fading_term),
            dot.move_to, sum_point
        )
        self.play(
            Write(rhs),
            ShowCreation(sum_arrow)
        )
        self.dither()
        self.change_student_modes("erm", "confused", "maybe")
        self.play(self.teacher.change_mode, "happy")
        self.dither(2)

class FermatsDreamExcerptWrapper(Scene):
    def construct(self):
        words = TextMobject(
            "From ``Fermat's dream'' by Kato, Kurokawa and Saito"
        )
        words.scale(0.8)
        words.to_edge(UP)
        self.add(words)
        self.dither()













































