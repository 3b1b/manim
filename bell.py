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
        reference_angle = self.reference_line.get_angle()
        self.em_wave.rotation = reference_angle
        FilterScene.continual_update(self)
        vect_groups = [self.em_wave.E_vects, self.em_wave.M_vects]
        if self.apply_filter:
            filters = sorted(
                self.pol_filters,
                lambda pf1, pf2 : cmp(
                    pf1.get_center()[0], 
                    pf2.get_center()[0],
                )
            )
            for pol_filter in filters:
                filter_x = pol_filter.get_center()[0]
                for vect_group, angle in zip(vect_groups, [0, -np.pi/2]):
                    proj_vect = rotate_vector(
                        OUT, pol_filter.filter_angle + angle, RIGHT,
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
                            vect.set_tip_points(vect.tip)
                            vect.set_rectangular_stem_points()

class PhotonPassesCompletelyOrNotAtAll(DirectionOfPolarization):
    CONFIG = {
        "pol_filter_configs" : [{
            "include_arrow_label" : False,
            "label_tex" : "\\text{Filter}",
        }],
        "EMWave_config" : {
            "wave_number" : 0,
            "A_vect" : [0, 1, 1],
        },
        "start_theta" : -0.9*np.pi,
        "target_theta" : -0.6*np.pi,
    }
    def setup(self):
        DirectionOfPolarization.setup(self)
        self.continual_update()
        for vect in it.chain(self.em_wave.E_vects, self.em_wave.M_vects):
            vect.reset_normal_vector()
        self.remove(self.em_wave)

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
        self.continual_update()

        passing_photon = WavePacket(
            run_time = 2,
            get_filtered = False,
            em_wave = self.em_wave.copy()
        )
        filtered_photon = WavePacket(
            run_time = 2,
            get_filtered = True,
            em_wave = self.em_wave.copy()
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

class PhotonsThroughPerpendicularFilters(PhotonPassesCompletelyOrNotAtAll):
    CONFIG = {
        "filter_x_coordinates" : [-2, 2],
        "pol_filter_configs" : [
            {"filter_angle" : 0},
            {"filter_angle" : np.pi/2},
        ],
        "start_theta" : -0.9*np.pi,
        "target_theta" : -0.6*np.pi,
        "EMWave_config" : {
            "A_vect" : [0, 0, 1],
        }
    }
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
            pairs = zip(photons, reversed(self.pol_filters))
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
                run_time = 1,
            )
            for x in -2, 2, 10
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

class MoreFiltersMoreLight(FilterScene):
    CONFIG = {
        "filter_x_coordinates" : range(-2, 3),
        "pol_filter_configs" : [
            {
                "include_arrow_label" : False,
                "filter_angle" : angle
            }
            for angle in np.linspace(0, np.pi/2, 5)
        ],
        "ambient_rotation_rate" : 0,
    }
    def construct(self):
        self.remove(self.axes)
        pfs = self.pol_filters
        for pf in pfs:
            pf.set_fill(WHITE, opacity = 0.25)
            pf.arrow.set_fill(opacity = 1)
        turn_off_3d_shading(pfs)
        self.remove(pfs)
        self.add(pfs[4], pfs[2], pfs[0])

        self.move_camera(
            phi = 0.9*np.pi/2,
            theta = -0.95*np.pi,
        )
        self.dither()
        for i in 1, 3:
            pf = pfs[i]
            foreground = VGroup(*reversed(pfs[:i]))
            pf.save_state()
            pf.shift(6*OUT)
            self.remove(foreground)
            self.play(
                pf.restore,
                Animation(foreground),
                run_time = 2
            )
            self.dither()

class ConfusedPiCreature(Scene):
    def construct(self):
        randy = Randolph()
        self.play(
            randy.change, "confused", 3*(UP+RIGHT),
        )
        self.play(Blink(randy))
        self.dither(2)
        self.play(Blink(randy))
        self.dither(2)

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
            "A_vect" : [0, 1, -1],
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
        left_title = TextMobject("Angle between \\\\ filters")
        left_title.to_corner(UP+LEFT)
        right_title = TextMobject(
            "Probability that photons passing \\\\",
            "through the first pass through the second"
        )
        right_title.next_to(left_title, RIGHT, LARGE_BUFF)

        h_line = Line(LEFT, RIGHT).scale(SPACE_WIDTH)
        h_line.to_edge(UP, buff = 2)
        v_line = Line(UP, DOWN).scale(SPACE_HEIGHT)
        v_line.next_to(left_title, RIGHT, MED_LARGE_BUFF)
        v_line.to_edge(UP, buff = 0)
        VGroup(h_line, v_line).highlight(BLUE)
        self.add(left_title, right_title, h_line, v_line)

        angles = [0, 22.5, 30, 45, 60, 67.5, 90]
        angle_mobs = VGroup(*[
            TexMobject(str(angle) + "^\\circ")
            for angle in angles
        ])
        angle_mobs.arrange_submobjects(DOWN, buff = MED_LARGE_BUFF)
        angle_mobs.scale(0.8)
        angle_mobs.next_to(left_title, DOWN, LARGE_BUFF)

        probs = [
            np.cos(angle*np.pi/180.0)**2
            for angle in angles
        ]
        prob_mobs = VGroup(*[
            TexMobject("%.1f"%(100*prob) + "\\%")
            for prob in probs
        ])
        prob_mobs.highlight(YELLOW)
        prob_mobs.scale(0.8)

        angle_prob_pairs = zip(angle_mobs, prob_mobs)
        for angle_mob, prob_mob in angle_prob_pairs:
            prob_mob.next_to(angle_mob, RIGHT, buff = 3)
        for prob_mob in prob_mobs[1:]:
            prob_mob.align_to(prob_mobs[0], LEFT)


        for i in [0, 6, 3, 1, 2, 4, 5]:
            self.play(FadeIn(angle_mobs[i]))
            self.play(ReplacementTransform(
                angle_mobs[i].copy(), prob_mobs[i]
            ))

        explanation = TextMobject("Based on $\\cos(\\theta)^2$")
        explanation.next_to(prob_mobs, RIGHT, LARGE_BUFF)
        self.play(Write(explanation, run_time = 2))
        self.dither()

class ShowVariousFilterPairs(PhotonsThroughPerpendicularFilters):
    CONFIG = {
        "filter_x_coordinates" : [-2, 2, 2, 2, 2],
        "pol_filter_configs" : [
            {"filter_angle" : angle}
            for angle in 0, 0, np.pi/2, np.pi/4, np.pi/8
        ],
        "apply_filter" : False,
    }
    def construct(self):
        self.photons = self.get_photons()
        new_filters = self.new_filters = self.pol_filters[2:]
        self.remove(*new_filters)
        self.pol_filters = self.pol_filters[:2]

        self.add_filters()
        self.add_probability_text()
        self.show_photons()
        self.revert_to_original_skipping_status()
        for pol_filter in new_filters:
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
        for pf in self.new_filters:
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
        blocked_photon = copy.deepcopy(self.photons[0])
        blocked_photon.rate_func = squish_rate_func(
            lambda x : x, 0, 0.5,
        )
        first_absorbtion = self.get_filter_absorbtion_animation(
            self.pol_filters[0], blocked_photon
        )
        first_absorbtion.rate_func = squish_rate_func(
            first_absorbtion.rate_func, 0, 0.5,
        )

        photons = [
            copy.deepcopy(self.photons[2 if q <= p else 1])
            for q in np.arange(0, 1, 1./n_photons)
        ]
        random.shuffle(photons)
        for photon in photons:
            photon.rate_func = squish_rate_func(
                lambda x : x, 0.5, 1
            )
            added_anims = []
            if photon.filter_distance == SPACE_WIDTH + 2:
                absorbtion = self.get_filter_absorbtion_animation(
                    self.second_filter, photon
                )
                absorbtion.rate_func = squish_rate_func(
                    absorbtion.rate_func, 0.5, 1
                )
                added_anims.append(absorbtion)
            self.play(
                blocked_photon,
                first_absorbtion,
                photon, 
                *added_anims
            )
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
        self.photons = self.get_photons()[1:]

        for pf in self.pol_filters:
            pf.arrow_label.rotate_in_place(np.pi/2, OUT)
            pf.arrow_label.next_to(pf.arrow, RIGHT)

        group = VGroup(*self.pol_filters[1:])
        rect1 = SurroundingRectangle(group)
        rect1.rotate_in_place(np.pi/2, RIGHT)
        rect1.rescale_to_fit(group.get_depth()+MED_SMALL_BUFF, 2, True)
        rect1.stretch_in_place(1.2, 0)
        prob_words = TextMobject(
            "Probabilities depend only\\\\",
            "on this angle difference"
        )
        prob_words.add_background_rectangle()
        prob_words.rotate(np.pi/2, RIGHT)
        prob_words.next_to(rect1, OUT)

        self.add(rect1)
        self.play(Write(prob_words))
        # for x in range(2):
        #     self.shoot_photon()

        rect2 = SurroundingRectangle(self.pol_filter, color = RED)
        rect2.rotate_in_place(np.pi/2, RIGHT)
        rect2.rescale_to_fit(self.pol_filter.get_depth()+MED_SMALL_BUFF, 2, True)
        rect2.stretch_in_place(1.5, 0)
        ignore_words = TextMobject("Photon \\\\", "``forgets'' this")
        ignore_words.add_background_rectangle()
        ignore_words.rotate(np.pi/2, RIGHT)
        ignore_words.next_to(rect2, OUT)

        self.play(
            ShowCreation(rect2), 
            Write(ignore_words, run_time = 1)
        )
        self.shoot_photon()
        self.dither(2)
        # for x in range(4):
        #     self.shoot_photon()


    def shoot_photon(self):
        photon = random.choice(self.photons)
        added_anims = []
        if photon.filter_distance == SPACE_WIDTH + 2:
            added_anims.append(self.get_filter_absorbtion_animation(
                self.pol_filters[2], photon
            ))
        self.play(photon, *added_anims, run_time = 1.5)

class IntroduceLabeledFilters(PhotonsThroughPerpendicularFilters):
    CONFIG = {
        "filter_x_coordinates" : [-3, 0, 3],
        "pol_filter_configs" : [
            {"filter_angle" : angle}
            for angle in [0, np.pi/8, np.pi/4]
        ],
        "start_phi" : 0.9*np.pi/2,
        "start_theta" : -0.85*np.pi,
    }
    def setup(self):
        PhotonsThroughPerpendicularFilters.setup(self)
        self.remove(self.axes)

    def construct(self):
        self.add_letters_to_labels()
        self.introduce_filters()
        self.reposition_camera()
        self.separate_cases()
        self.half_blocked_by_C()
        self.show_those_blocked_with_B()

    def add_letters_to_labels(self):
        for char, pf, color in zip("ABC", self.pol_filters, [RED, GREEN, BLUE]):
            label = TextMobject(char)
            label.scale(0.9)
            label.add_background_rectangle()
            label.highlight(color)
            label.rotate(np.pi/2, RIGHT)
            label.rotate(np.pi/2, IN)
            label.next_to(pf.arrow_label, UP)
            pf.arrow_label.add(label)
            pf.arrow_label.next_to(pf.arrow, OUT, SMALL_BUFF)
        self.remove(*self.pol_filters)

    def introduce_filters(self):
        self.A_filter, self.B_filter, self.C_filter = self.pol_filters
        for pf in self.pol_filters:
            pf.save_state()
            pf.shift(4*OUT)
            pf.fade(1)
            self.play(pf.restore)
            self.dither(2)

    def reposition_camera(self):
        self.move_camera(
            theta = -0.6*np.pi, 
            added_anims = list(it.chain(*[
                [
                    pf.arrow_label.rotate, np.pi/2, OUT,
                    pf.arrow_label.next_to, pf.arrow, RIGHT
                ]
                for pf in self.pol_filters
            ]))
        )
        self.dither()

    def separate_cases(self):
        self.lower_pol_filters = VGroup(
            self.A_filter.copy(),
            self.C_filter.copy(),
        )
        self.play(
            self.lower_pol_filters.shift, 3*IN,
            self.pol_filters.shift, OUT,
        )
        self.dither()

    def half_blocked_by_C(self):
        pass

    def show_those_blocked_with_B(self):
        pass

class NumbersSuggestHiddenVariablesAreImpossible(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "These numbers suggest\\\\",
            "no hidden variables"
        )
        self.change_student_modes("erm", "sassy", "confused")
        self.dither(3)

class VennDiagramProofByContradiction(Scene):
    CONFIG = {
        "circle_colors" : [RED, GREEN, BLUE]
    }
    def construct(self):
        self.draw_venn_diagram()
        self.show_100_photons()
        self.show_one_photon_answering_questions()
        self.put_all_photons_in_A()
        self.separate_by_B()
        self.separate_by_C()
        self.show_two_relevant_subsets()

    def draw_venn_diagram(self):
        venn_diagrom = VGroup(*[
            Circle(
                radius = 3,
                stroke_width = 3,
                stroke_color = c,
                fill_opacity = 0.2,
                fill_color = c,
            ).shift(vect)
            for c, vect in zip(
                self.circle_colors,
                compass_directions(3, UP)
            )
        ])
        venn_diagrom.center()
        props = [1./12, 0.5, 0]
        for circle, char, prop in zip(venn_diagrom, "ABC", props):
            label = TextMobject("Would pass \\\\ through", char)
            label.highlight_by_tex(char, circle.get_color())
            center = circle.get_center()
            label.move_to(center)
            label.generate_target()
            point = circle.point_from_proportion(prop)
            label.target.next_to(point, point-center, SMALL_BUFF)

            circle.label = label

        last_circle = None
        for circle in venn_diagrom:
            added_anims = []
            if last_circle:
                added_anims.append(MoveToTarget(last_circle.label))
            self.play(
                DrawBorderThenFill(circle, run_time = 2),
                Write(circle.label, run_time = 2),
                *added_anims
            )
            last_circle = circle
        self.play(MoveToTarget(last_circle.label))
        self.dither()

        venn_diagrom.add(*[c.label for c in venn_diagrom])
        self.venn_diagrom = venn_diagrom
        for part in self.venn_diagrom:
            part.save_state()

        self.play(
            self.venn_diagrom.scale, 0.25,
            self.venn_diagrom.to_corner, UP+RIGHT
        )        

    def show_100_photons(self):
        photon = FunctionGraph(
            lambda x : -np.cos(3*np.pi*x)*np.exp(-x*x),
            x_min = -2, 
            x_max = 2,
            color = YELLOW,
            stroke_width = 2,
        )
        photon.shift(LEFT + 2*UP)
        eyes = Eyes(photon)
        photon.eyes = eyes

        hundred, photon_word, s = words = TextMobject(
            "100 ", "Photon", "s",
            arg_separator = ""
        )
        words.next_to(eyes, UP)

        self.play(
            ShowCreation(photon),
            FadeIn(photon.eyes),
            Write(photon_word, run_time = 1.5)
        )
        photon.add(photon.eyes)

        #Split to hundred
        photons = VGroup(*[photon.deepcopy() for x in range(100)])
        self.arrange_photons_in_circle(photons)
        photons.scale_to_fit_height(6)
        photons.next_to(words, DOWN)
        photons.to_edge(LEFT)

        self.play(
            Write(hundred), Write(s),
            ReplacementTransform(
                VGroup(photon), photons,
                submobject_mode = "lagged_start"
            )
        )

        self.photons = photons
        self.photon_words = words

    def show_one_photon_answering_questions(self):
        photon = self.photons[-1]
        photon.save_state()
        photon.generate_target()
        photon.target.scale(4)
        photon.target.next_to(self.photons, RIGHT)

        answers = TextMobject(
            "Pass through A?", "Yes\\\\",
            "Pass through B?", "No\\\\",
            "Pass through C?", "No\\\\",
        )
        answers.highlight_by_tex_to_color_map({
            "Yes" : GREEN,
            "No" : RED,
        })
        answers.next_to(photon.target, RIGHT)

        self.play(
            MoveToTarget(photon),
            FadeIn(answers)
        )
        self.dither(2)
        self.play(
            FadeOut(answers),
            photon.restore,
        )

    def put_all_photons_in_A(self):
        A_circle, B_circle, C_circle = circles = self.venn_diagrom[:3]
        A_group, B_group, C_group = [
            VGroup(circle, circle.label)
            for circle in circles
        ]
        B_group.save_state()
        C_group.save_state()

        A_group.generate_target()
        A_group.target.scale(4)
        A_group.target.shift(
            (SPACE_HEIGHT-MED_LARGE_BUFF)*UP - \
            A_group.target[0].get_top()
        )
        A_group.target[1].scale_in_place(0.8)

        self.play(
            B_group.fade, 1,
            C_group.fade, 1,
            MoveToTarget(A_group),
            FadeOut(self.photon_words),
            self.photons.scale_to_fit_height, 
                0.85*A_group.target.get_height(),
            self.photons.move_to, A_group.target[0].get_center(),
        )
        self.dither()

        self.A_group = A_group
        self.B_group = B_group
        self.C_group = C_group

    def separate_by_B(self):
        A_group = self.A_group
        B_group = self.B_group
        photons = self.photons
        B_circle = B_group[0]

        B_group.target = B_group.saved_state
        B_group.target.scale(4)
        B_group.target.move_to(A_group)
        B_group.target.shift(1.25*DOWN+3.25*LEFT)
        B_group.target[1].shift(DOWN)
        B_group.target[1].scale_in_place(0.8)
        B_center = B_group.target[0].get_center()
        photons.sort_submobjects(
            lambda p : np.linalg.norm(p-B_center)
        )
        in_B = VGroup(*photons[:85])
        out_of_B = VGroup(*photons[85:])
        out_of_B.sort_submobjects(lambda p : np.dot(p, 2*UP+LEFT))

        words = TextMobject("15 blocked \\\\ by ", "B")
        words.highlight_by_tex("B", GREEN)
        words.scale(0.8)
        words.next_to(A_group, LEFT, LARGE_BUFF, UP)
        arrow = Arrow(words.get_right(), out_of_B[-1])
        arrow.highlight(RED)

        self.play(
            MoveToTarget(B_group),
            in_B.space_out_submobjects, 0.8,
            in_B.shift, MED_SMALL_BUFF*(DOWN+LEFT),
        )
        self.play(
            Write(words, run_time = 1),
            ShowCreation(arrow)
        )
        self.play(LaggedStart(
            Indicate, out_of_B, 
            rate_func = there_and_back,
            color = RED,
            scale_factor = 2,
        ))
        self.dither()

        self.in_B = in_B
        self.out_of_B = out_of_B
        self.out_of_B_words = words
        self.out_of_B_arrow = arrow

    def separate_by_C(self):
        B_group = self.B_group
        C_group = self.C_group
        in_B = self.in_B

        C_group.target = C_group.saved_state
        C_group.target.scale(4)
        C_group.target.move_to(B_group, DOWN)
        C_group.target.shift(4.5*RIGHT)
        C_center = C_group.target[0].get_center()
        C_group.target[1].scale_in_place(0.8)

        in_B.sort_submobjects(
            lambda p : np.linalg.norm(p - C_center)
        )
        in_C = VGroup(*in_B[:-11])
        out_of_C = VGroup(*in_B[-11:])

        words = TextMobject(
            "$<$ 15 passing", "B \\\\",
            "get blocked by ", "C",
        )
        words.scale(0.8)
        words.highlight_by_tex_to_color_map({
            "B" : GREEN,
            "C" : BLUE,
        })
        words.next_to(self.out_of_B_words, DOWN, LARGE_BUFF)
        words.to_edge(LEFT)
        arrow = Arrow(words.get_right(), out_of_C)
        arrow.highlight(GREEN)

        self.play(
            MoveToTarget(C_group),
            in_C.shift, MED_SMALL_BUFF*(DOWN+RIGHT),
            out_of_C.shift, SMALL_BUFF*(UP+LEFT),
        )
        self.play(
            Write(words, run_time = 1),
            ShowCreation(arrow)
        )
        self.dither()
        self.play(LaggedStart(
            Indicate, out_of_C, 
            rate_func = there_and_back,
            color = GREEN,
            scale_factor = 2,
        ))
        self.dither()

        self.in_C = in_C
        self.out_of_C = out_of_C
        self.out_of_C_words = words
        self.out_of_C_arrow = arrow

    def show_two_relevant_subsets(self):
        terms = VGroup(
            TexMobject("N(", "A+", ",", "B-", ")"),
            TexMobject("+ N(", "A+", ",", "B+", ",", "C-", ")"),
            TexMobject("\\ge", "N(", "A+", ",", "C-", ")"),
        )
        terms.arrange_submobjects(RIGHT)
        terms.to_edge(UP)
        for term in terms:
            term.highlight_by_tex_to_color_map({
                "A" : RED,    
                "B" : GREEN,
                "C" : BLUE,
            })

        all_out_of_C = VGroup(*it.chain(
            self.out_of_B[6:],
            self.out_of_C,
        ))

        self.play(*[
            ApplyMethod(
                m.scale, 0.8, 
                method_kwargs = {
                    "about_point" : SPACE_HEIGHT*DOWN
                }
            )
            for m in self.get_top_level_mobjects()
        ])
        self.dither()
        for term, group in zip(terms[:2], [self.out_of_B, self.out_of_C]):
            self.play(LaggedStart(
                Indicate, group,
                color = WHITE,
                scale_factor = 1.5,
                run_time = 1,
            ))
            self.play(Write(term, run_time = 1))
            self.play(
                LaggedStart(
                    ApplyMethod, group,
                    lambda m : (m.scale_in_place, 1/1.5)
                ),
                self.in_C.fade,
            )
        self.dither()
        self.play(Write(terms[2], run_time = 1))
        self.play(LaggedStart(
            Indicate, all_out_of_C,
            color = TEAL,
            run_time = 2,
            rate_func = smooth,
        ))
        self.dither()

        words = [self.out_of_B_words, self.out_of_C_words]
        arrows = [self.out_of_B_arrow, self.out_of_C_arrow]
        indices = [2, 3]
        for word, arrow, index, term in zip(words, arrows, indices, terms):
            num = VGroup(*word[0][:index])
            word[0].remove(*num)

            self.play(
                FadeOut(word),
                FadeOut(arrow),
                num.scale, 2,
                num.next_to, term, DOWN
            )
        self.dither()

        rect = SurroundingRectangle(VGroup(*terms[2][1:]))
        should_be_50 = TextMobject("Should be 50...somehow")
        should_be_50.scale(0.8)
        should_be_50.next_to(rect, DOWN, MED_SMALL_BUFF, LEFT)

        self.play(
            ShowCreation(rect),
            Write(should_be_50, run_time = 1)
        )
        self.dither()

        morty = Mortimer()
        morty.to_corner(DOWN+RIGHT)
        contradiction = TextMobject("Contradiction!")
        contradiction.next_to(morty, UP, aligned_edge = RIGHT)
        contradiction.highlight(RED)
        self.play(FadeIn(morty))
        self.play(
            morty.change, "hooray",
            Write(contradiction, run_time = 1)
        )
        self.play(Blink(morty))
        self.dither()


    #######

    def arrange_photons_in_circle(self, photons):
        R = np.sqrt(len(photons) / np.pi)
        pairs = []
        rejected = []
        for x, y in it.product(*[range(-int(R)-1, int(R)+2)]*2):
            if x**2 + y**2 < R**2:
                pairs.append((x, y))
            else:
                rejected.append((x, y))
        rejected.sort(
            lambda (x1, y1), (x2, y2) : (x2**2 + y2**2) - (x1**2 + y1**2)
        )
        for i in range(len(photons) - len(pairs)):
            pairs.append(rejected.pop())
        for photon, (x, y) in zip(photons, pairs):
            photon.scale_to_fit_width(0.7)
            photon.move_to(x*RIGHT + y*UP)
        return photons
































