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
from topics.probability import *
from topics.complex_numbers import *
from scene import Scene
from scene.reconfigurable_scene import ReconfigurableScene
from scene.zoomed_scene import *
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

from waves import *

#force_skipping
#revert_to_original_skipping_status

class FilterScene(ThreeDScene):
    CONFIG = {
        "filter_x_coordinates" : [0],
        "pol_filter_configs" : [{}],
        "EMWave_config" : {
            "start_point" : SPACE_WIDTH*LEFT + DOWN+OUT
        },
        "start_phi" : 0.8*np.pi/2,
        "start_theta" : -0.6*np.pi,
        "ambient_rotation_rate" : 0.01,
    }
    def setup(self):
        self.axes = ThreeDAxes()
        self.add(self.axes)
        for x in range(len(self.filter_x_coordinates) - len(self.pol_filter_configs)):
            self.pol_filter_configs.append({})
        self.pol_filters = VGroup(*[
            PolarizingFilter(**config)
            for config in self.pol_filter_configs
        ])
        self.pol_filters.rotate(np.pi/2, RIGHT)
        self.pol_filters.rotate(-np.pi/2, OUT)
        self.pol_filters.shift(DOWN+OUT)
        for x, pf in zip(self.filter_x_coordinates, self.pol_filters):
            pf.shift(x*RIGHT)
        self.add(self.pol_filters)
        self.pol_filter = self.pol_filters[0]

        self.set_camera_position(self.start_phi, self.start_theta)
        if self.ambient_rotation_rate > 0:
            self.begin_ambient_camera_rotation(self.ambient_rotation_rate)

    def get_filter_absorbtion_animation(self, pol_filter, photon):
        x = pol_filter.get_center()[0]
        alpha = (x + SPACE_WIDTH) / (2*SPACE_WIDTH)
        return ApplyMethod(
            pol_filter.set_fill, RED,
            run_time = photon.run_time,
            rate_func = squish_rate_func(there_and_back, alpha - 0.1, alpha + 0.1)
        )

class PhotonPassesCompletelyOrNotAtAll(FilterScene):
    CONFIG = {
        "pol_filter_configs" : [{
            "include_arrow_label" : False,
            "label_tex" : "\\text{Filter}",
        }],
        "start_theta" : -0.9*np.pi,
        "target_theta" : -0.6*np.pi,
    }
    def construct(self):
        pol_filter = self.pol_filter
        label = pol_filter.label
        pol_filter.remove(label)
        label.shift(SMALL_BUFF*IN)

        passing_words = TextMobject("Photon", "passes through")
        passing_words.highlight(GREEN)
        filtered_words = TextMobject("Photon", "is blocked")
        filtered_words.highlight(RED)
        for words in passing_words, filtered_words:
            words.next_to(ORIGIN, UP+LEFT)
            words.shift(2*UP)
            words.add_background_rectangle()
            words.rotate(np.pi/2, RIGHT)

        passing_photon = WavePacket(
            run_time = 3,
            get_filtered = False,
            EMWave_config = self.EMWave_config
        )
        new_em_wave_config = dict(self.EMWave_config)
        new_em_wave_config["A_x"] = 0
        new_em_wave_config["A_y"] = 1
        filtered_photon = WavePacket(
            run_time = 3,
            get_filtered = True,
            EMWave_config = new_em_wave_config
        )


        self.play(
            DrawBorderThenFill(pol_filter),
            Write(label, run_time = 2)
        )
        self.move_camera(theta = self.target_theta)
        self.play(Write(passing_words, run_time = 1))
        self.play(passing_photon)
        self.play(Transform(passing_words, filtered_words))
        self.play(
            filtered_photon,
            ApplyMethod(
                pol_filter.set_fill, RED,
                rate_func = squish_rate_func(there_and_back, 0.4, 0.6),
                run_time = filtered_photon.run_time
            )
        )
        self.dither(3)

class DirectionOfPolarization(FilterScene):
    CONFIG = {
        "pol_filter_configs" : [{
            "include_arrow_label" : False,
        }],
        "target_theta" : -0.97*np.pi,
        "target_phi" : 0.9*np.pi/2,
        "ambient_rotation_rate" : 0.005,
        "apply_filter" : True,
    }
    def setup(self):
        self.reference_line = Line(ORIGIN, RIGHT)
        self.reference_line.set_stroke(width = 0)
        self.em_wave = EMWave(**self.EMWave_config)
        self.add(self.em_wave)

        FilterScene.setup(self)

    def construct(self):
        self.remove(self.pol_filter)
        words = TextMobject("Polarization direction")
        words.next_to(ORIGIN, UP+RIGHT, LARGE_BUFF)
        words.shift(2*UP)
        words.rotate(np.pi/2, RIGHT)
        words.rotate(-np.pi/2, OUT)

        em_wave = self.em_wave

        self.add(em_wave)
        self.dither(2)
        self.move_camera(
            phi = self.target_phi,
            theta = self.target_theta
        )
        self.play(Write(words, run_time = 1))
        self.change_polarization_direction(
            2*np.pi/3,
            run_time = 6,
            rate_func = there_and_back
        )
        self.dither(2)

    def change_polarization_direction(self, angle, **kwargs):
        added_anims = kwargs.get("added_anims", [])
        self.play(
            ApplyMethod(
                self.reference_line.rotate, angle,
                **kwargs
            ),
            *added_anims
        )

    def continual_update(self):
        FilterScene.continual_update(self)
        wave = self.em_wave.mobject
        angle = self.reference_line.get_angle()
        wave.rotate(
            angle, self.em_wave.propogation_direction,
            about_point = self.em_wave.start_point,
        )
        if self.apply_filter:
            filter_x = self.pol_filter.get_center()[0]
            for vect_group, angle in (self.em_wave.E_vects, 0), (self.em_wave.M_vects, np.pi/2):
                proj_vect = rotate_vector(
                    OUT, self.pol_filter.filter_angle + angle, RIGHT,
                )
                proj_matrix = np.array([RIGHT] + [
                    proj_vect*np.dot(proj_vect, basis)
                    for basis in UP, OUT
                ]).T
                for vect in vect_group:
                    start, end = vect.get_start_and_end()
                    if start[0] > filter_x:
                        vect.apply_matrix(proj_matrix)
                        vect.shift(start - vect.get_start())


class PhotonsThroughPerpendicularFilters(DirectionOfPolarization):
    CONFIG = {
        "filter_x_coordinates" : [-2, 2],
        "pol_filter_configs" : [
            {"filter_angle" : 0},
            {"filter_angle" : np.pi/2},
        ],
        "start_theta" : -0.9*np.pi,
        "target_theta" : -0.6*np.pi,
        "EMWave_config" : {
            "wave_number" : 0,
        }
    }
    def setup(self):
        DirectionOfPolarization.setup(self)
        self.remove(self.em_wave)

    def construct(self):
        photons = self.get_photons()[:2]
        prob_text = self.get_probability_text()
        self.pol_filters = VGroup(*reversed(self.pol_filters))

        self.play(LaggedStart(DrawBorderThenFill, self.pol_filters))
        self.move_camera(
            theta = self.target_theta,
            added_anims = [
                FadeIn(prob_text)
            ]
        )
        for x in range(4):
            pairs = zip(photons, self.pol_filters)
            random.shuffle(pairs)
            for photon, pol_filter in pairs:
                self.play(
                    photon,
                    self.get_filter_absorbtion_animation(
                        pol_filter, photon
                    )
                )

    def get_photons(self):
        self.reference_line.rotate(np.pi/4)
        self.continual_update()
        return [
            WavePacket(
                filter_distance = SPACE_WIDTH + x,
                get_filtered = True,
                em_wave = self.em_wave.copy(),
                run_time = 1.5,
            )
            for x in 2, -2, 10
        ]

    def get_probability_text(self, prob = 0):
        prob_text = TexMobject(
            "P(", "\\substack", "{\\text{photons that make it} \\\\ ", 
            " \\text{here } ", "\\text{make it}", 
            " \\text{ here} }", ")", "=", str(int(prob*100)), "\\%",
            arg_separator = ""
        )
        here1, here2 = prob_text.get_parts_by_tex("here")
        here1.highlight(GREEN)
        here2.highlight(RED)
        prob_text.add_background_rectangle()
        prob_text.next_to(ORIGIN, UP+RIGHT)
        prob_text.shift(2.5*UP+LEFT)
        prob_text.rotate(np.pi/2, RIGHT)
        arrows = [
            Arrow(
                here.get_edge_center(IN),
                DOWN+OUT + x*RIGHT,
                color = here.get_color(),
                normal_vector = DOWN+OUT,
            )
            for here, x in (here1, 0), (here2, 4)
        ]
        prob_text.add(*arrows)

        return prob_text

class AngryPiCreature(PiCreatureScene):
    def construct(self):
        self.pi_creature_says(
            "No, \\emph{locality} \\\\ must be wrong!",
            target_mode = "angry",
            look_at_arg = 2*RIGHT,
            run_time = 1
        )
        self.dither(3)

    def create_pi_creature(self):
        return Randolph().shift(DOWN+3*LEFT)

class ShowALittleMath(TeacherStudentsScene):
    def construct(self):
        expression = TexMobject(
            "\\alpha", "| \\! \\uparrow \\rangle", "+",
            "\\beta", "| \\! \\rightarrow \\rangle",
        )
        expression.highlight_by_tex("uparrow", GREEN)
        expression.highlight_by_tex("rightarrow", RED)
        expression.next_to(self.teacher, UP+LEFT, LARGE_BUFF)

        prob = TexMobject("\\text{Probability}", "=", "|", "\\alpha", "|^2")
        prob.next_to(expression, UP, LARGE_BUFF)

        self.play(
            Write(expression),
            self.teacher.change, "raise_right_hand"
        )
        target_alpha = prob.get_part_by_tex("alpha")
        prob.remove(target_alpha)
        self.play(
            ReplacementTransform(
                expression.get_part_by_tex("alpha").copy(),
                target_alpha,
            ),
            Write(prob)
        )
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = prob
        )
        self.dither(2)

class SecondVideoWrapper(Scene):
    def construct(self):
        title = TextMobject("Some light quantum mechanics")
        title.to_edge(UP)
        self.add(title)

        screen_rect = ScreenRectangle(height = 6)
        screen_rect.next_to(title, DOWN)
        self.play(ShowCreation(screen_rect))
        self.dither(3)

class BasicsOfPolarization(DirectionOfPolarization):
    def construct(self):
        self.show_continual_wave()
        self.show_photons()

    def show_continual_wave(self):
        em_wave = self.em_wave
        em_wave.M_vects.set_fill(opacity = 0.5)

        title = TextMobject("Waves in the ``electromagnetic field''")
        title.to_edge(UP)
        subtitle = TextMobject("Polarization = Direction of", "wiggling")
        subtitle.highlight_by_tex("wiggling", YELLOW)
        subtitle.next_to(title, DOWN)
        for words in title, subtitle:
            words.add_background_rectangle()
            words.rotate(np.pi/2, RIGHT)

        self.play(Write(title))
        self.dither(2)
        self.play(Write(subtitle, run_time = 2))
        self.change_polarization_direction(np.pi/2, run_time = 3)
        self.dither(2)
        self.change_polarization_direction(-np.pi/12, run_time = 2)
        self.dither()
        self.move_camera(theta = -0.95*np.pi)
        self.dither()
        self.change_polarization_direction(-np.pi/6, run_time = 2)
        self.dither()
        self.move_camera(theta = -0.6*np.pi)
        self.dither()
        self.play(FadeOut(em_wave.mobject))
        self.remove(em_wave)
        self.reference_line.put_start_and_end_on(ORIGIN, RIGHT)

    def show_photons(self):
        quantum_left_words = TextMobject(
            "Quantum", "$\\Rightarrow$",
        )
        quantum_left_words.next_to(ORIGIN, UP+RIGHT)
        quantum_left_words.shift(UP)
        quantum_right_words = TextMobject(
            "Completely through", "or \\\\",
            "Completely blocked",
        )
        quantum_right_words.scale(0.8)
        quantum_right_words.next_to(quantum_left_words, buff = 0)
        quantum_right_words.highlight_by_tex("through", GREEN)
        quantum_right_words.highlight_by_tex("blocked", RED)
        quantum_words = VGroup(quantum_left_words, quantum_right_words)
        quantum_words.rotate(np.pi/2, RIGHT)

        config = dict(self.EMWave_config)
        config.update({
            "wave_number" : 0,
            "A_x" : -1,
            "A_y" : 1,
        })
        self.em_wave = EMWave(**config)
        self.continual_update()
        passing_photon = WavePacket(
            em_wave = self.em_wave.copy(),
            run_time = 2,
        )
        filtered_photon = WavePacket(
            em_wave = self.em_wave.copy(),
            get_filtered = True,
            run_time = 2,
        )

        self.play(FadeIn(
            quantum_words,
            run_time = 2,
            submobject_mode = "lagged_start"
        ))
        anim_sets = [
            [passing_photon],
            [
                filtered_photon,
                self.get_filter_absorbtion_animation(
                    self.pol_filter,
                    filtered_photon
                )
            ],
        ]
        for index in 0, 1, 0, 0, 1:
            self.play(*anim_sets[index])

class AngleToProbabilityChart(Scene):
    def construct(self):
        TextMobject("Angle between filters")
        TextMobject(
            "Probability that one"
        )

class ShowVariousFilterPairs(PhotonsThroughPerpendicularFilters):
    CONFIG = {
        "filter_x_coordinates" : [-2, 2, 2, 2, 2],
        "pol_filter_configs" : [
            {"filter_angle" : angle}
            for angle in 0, 0, np.pi/2, np.pi/4, np.pi/8
        ],
    }
    def construct(self):
        self.photons = self.get_photons()

        self.add_filters()
        self.add_probability_text()
        self.show_photons()
        self.revert_to_original_skipping_status()
        for pol_filter in self.pol_filters[2:]:
            self.change_to_new_filter(pol_filter)
            self.show_photons()

    def add_filters(self):
        self.remove(*self.pol_filters[1:])
        self.dither()
        self.play(ReplacementTransform(
            self.pol_filters[0].copy().set_fill(BLACK, 1),
            self.pol_filters[1]
        ))
        self.move_camera(
            theta = -0.6*np.pi,
            added_anims = list(it.chain(*[
                 [
                    pf.arrow_label.rotate_in_place, np.pi/2, OUT,
                    pf.arrow_label.next_to, pf.arrow, RIGHT
                 ]
                for pf in self.pol_filters[:2]
            ]))
        )
        for pf in self.pol_filters[2:]:
            pf.arrow_label.rotate_in_place(np.pi/2, OUT)
            pf.arrow_label.next_to(pf.arrow, RIGHT)

        self.second_filter = self.pol_filters[1]
        self.add_foreground_mobject(self.second_filter)

    def add_probability_text(self):
        prob_text = self.get_probability_text(self.get_prob())
        self.play(FadeIn(prob_text))
        self.prob_text = prob_text

    def show_photons(self, n_photons = 5):
        p = self.get_prob()
        photons = [
            copy.deepcopy(self.photons[2 if random.random() < p else 0])
            for x in range(n_photons)
        ]
        for photon in photons:
            added_anims = []
            if photon.filter_distance == 2:
                added_anims.append(self.get_filter_absorbtion_animation(
                    self.second_filter, photon
                ))
            self.play(photon, *added_anims, run_time = 1.5)
        self.dither()
        
    def change_to_new_filter(self, pol_filter):
        self.play(Transform(self.second_filter, pol_filter))
        self.second_filter.filter_angle = pol_filter.filter_angle
        new_prob_text = self.get_probability_text(self.get_prob())
        new_prob_text[1][-2].highlight(YELLOW)
        self.play(Transform(self.prob_text, new_prob_text))

    ####

    def get_prob(self):
        return np.cos(self.second_filter.filter_angle)**2


class ForgetPreviousActions(PhotonsThroughPerpendicularFilters):
    CONFIG = {
        "filter_x_coordinates" : [-6, -2, 2],
        "pol_filter_configs" : [
            {"filter_angle" : angle}
            for angle in np.pi/4, 0, np.pi/4
        ],
        "start_theta" : -0.6*np.pi
    }
    def construct(self):
        for pf in self.pol_filters:
            pf.arrow_label.rotate_in_place(np.pi/2, OUT)
            pf.arrow_label.next_to(pf.arrow, RIGHT)

        rect = SurroundingRectangle(VGroup(*self.pol_filters[1:]))
        rect.rotate_in_place(np.pi/2, RIGHT)
        rect.stretch_
        words = TextMobject(
            "Probabilities depend only\\\\",
            "on this angle difference"
        )
        words.rotate(np.pi/2, RIGHT)
        words.next_to(rect, OUT)
        self.add(rect, words)





















