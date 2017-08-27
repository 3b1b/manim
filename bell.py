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
            filters = sorted(
                self.pol_filters,
                lambda pf1, pf2 : cmp(
                    pf1.get_center()[0], 
                    pf2.get_center()[0],
                )
            )
            for pol_filter in filters:
                filter_x = pol_filter.get_center()[0]
                for vect_group, angle in (self.em_wave.E_vects, 0), (self.em_wave.M_vects, np.pi/2):
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
            copy.deepcopy(self.photons[2 if random.random() < p else 1])
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
        for x in range(2):
            self.shoot_photon()

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
        for x in range(4):
            self.shoot_photon()


    def shoot_photon(self):
        photon = random.choice(self.photons)
        added_anims = []
        if photon.filter_distance == SPACE_WIDTH + 2:
            added_anims.append(self.get_filter_absorbtion_animation(
                self.pol_filters[2], photon
            ))
        self.play(photon, *added_anims, run_time = 1.5)

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
        # self.force_skipping()

        self.draw_venn_diagram()
        self.show_100_photons()
        self.show_one_photon_answering_questions()
        self.put_all_photons_in_A()
        self.separate_by_B()
        self.separate_by_C()
        self.show_two_relevant_subsets()
        self.show_real_value()
        self.contradiction()

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
            color = YELLOW
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
        A_group.target.center().to_edge(UP)

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
        pass

    def separate_by_C(self):
        pass

    def show_two_relevant_subsets(self):
        pass

    def show_real_value(self):
        pass

    def contradiction(self):
        pass

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


























