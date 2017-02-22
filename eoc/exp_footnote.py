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

from eoc.chapter1 import OpeningQuote, PatreonThanks
from eoc.graph_scene import *

class LastVideo(TeacherStudentsScene):
    def construct(self):
        series = VideoSeries()
        series.to_edge(UP)
        last_video = series[2]
        next_video = series[3]
        last_video_color = last_video[0].get_fill_color()
        early_videos = VGroup(*series[:3])
        later_videos = VGroup(*series[3:])
        this_video = VideoIcon().scale(0.5)
        this_video.move_to(VGroup(last_video, next_video), DOWN)

        known_formulas = VGroup(*map(TexMobject, [
            "\\frac{d(x^n)}{dx} = nx^{n-1}",
            "\\frac{d(\\sin(x))}{dx} = \\cos(x)",
        ]))
        known_formulas.arrange_submobjects(
            DOWN, buff = MED_LARGE_BUFF,
        )
        known_formulas.scale_to_fit_height(2.5)
        exp_question = TexMobject("2^x, 7^x, e^x ???")

        last_video_brace = Brace(last_video)
        known_formulas.next_to(last_video_brace, DOWN)
        last_video_brace.save_state()
        last_video_brace.shift(3*LEFT)
        last_video_brace.set_fill(opacity = 0)

        self.add(series)
        self.play(
            last_video_brace.restore,
            last_video.highlight, YELLOW,
            self.get_teacher().change_mode, "raise_right_hand",
        )
        self.play(Write(known_formulas))
        self.dither()
        self.student_says(
            exp_question, student_index = -1,
            added_anims = [self.get_teacher().change_mode, "pondering"]
        )
        self.dither(2)
        self.play(known_formulas.replace, last_video)
        last_video.add(known_formulas)
        this_video_copy = this_video.copy()
        self.play(
            early_videos.stretch_to_fit_width,
            early_videos.get_width() - this_video_copy.get_width(),
            early_videos.next_to, this_video_copy, LEFT, SMALL_BUFF, DOWN,
            later_videos.stretch_to_fit_width,
            later_videos.get_width() - this_video_copy.get_width(),
            later_videos.next_to, this_video_copy, RIGHT, SMALL_BUFF, DOWN,
            last_video_brace.stretch_to_fit_width, 
            this_video_copy.get_width(),
            last_video_brace.next_to, this_video_copy, DOWN, SMALL_BUFF,
            GrowFromCenter(this_video)
        )
        self.play(
            last_video.highlight, last_video_color,
            this_video.highlight, YELLOW
        )
        self.play(
            FadeOut(self.get_students()[-1].bubble),            
            exp_question.next_to, last_video_brace, DOWN,
            *[
                ApplyMethod(pi.change_mode, "pondering")
                for pi in self.get_students()
            ]
        )
        self.dither(3)





































