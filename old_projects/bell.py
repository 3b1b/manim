from manimlib.imports import *

from tqdm import tqdm as ProgressDisplay

from .waves import *
from functools import reduce

#force_skipping
#revert_to_original_skipping_status

class PhotonPassesCompletelyOrNotAtAll(DirectionOfPolarizationScene):
    CONFIG = {
        "pol_filter_configs" : [{
            "include_arrow_label" : False,
            "label_tex" : "\\text{Filter}",
        }],
        "EMWave_config" : {
            "wave_number" : 0,
            "A_vect" : [0, 1, 1],
            "start_point" : FRAME_X_RADIUS*LEFT + DOWN + 1.5*OUT,
        },
        "start_theta" : -0.9*np.pi,
        "target_theta" : -0.6*np.pi,
        "apply_filter" : True,
        "lower_portion_shift" : 3*IN,
        "show_M_vects" : True,
    }
    def setup(self):
        DirectionOfPolarizationScene.setup(self)
        if not self.show_M_vects:
            for M_vect in self.em_wave.M_vects:
                M_vect.set_fill(opacity = 0)
        self.update_mobjects()
        for vect in it.chain(self.em_wave.E_vects, self.em_wave.M_vects):
            vect.reset_normal_vector()
        self.remove(self.em_wave)

    def construct(self):
        pol_filter = self.pol_filter
        pol_filter.shift(0.5*OUT)
        lower_filter = pol_filter.copy()
        lower_filter.save_state()
        pol_filter.remove(pol_filter.label)

        passing_words = TextMobject("Photon", "passes through\\\\", "entirely")
        passing_words.set_color(GREEN)
        filtered_words = TextMobject("Photon", "is blocked\\\\", "entirely")
        filtered_words.set_color(RED)
        for words in passing_words, filtered_words:
            words.next_to(ORIGIN, UP+LEFT)
            words.shift(2*UP)
            words.add_background_rectangle()
            words.rotate(np.pi/2, RIGHT)
        filtered_words.shift(self.lower_portion_shift)

        passing_photon = WavePacket(
            run_time = 2,
            get_filtered = False,
            em_wave = self.em_wave.copy()
        )
        lower_em_wave = self.em_wave.copy()
        lower_em_wave.mobject.shift(self.lower_portion_shift)
        lower_em_wave.start_point += self.lower_portion_shift
        filtered_photon = WavePacket(
            run_time = 2,
            get_filtered = True,
            em_wave = lower_em_wave.copy()
        )
        green_flash = ApplyMethod(
            pol_filter.set_fill, GREEN,
            rate_func = squish_rate_func(there_and_back, 0.4, 0.6),
            run_time = passing_photon.run_time
        )

        self.play(
            DrawBorderThenFill(pol_filter),
            Write(pol_filter.label, run_time = 2),
        )
        self.move_camera(theta = self.target_theta)
        self.play(
            FadeIn(passing_words),
            passing_photon,
            green_flash,
        )
        self.play(
            lower_filter.restore,
            lower_filter.shift, self.lower_portion_shift,
            FadeIn(filtered_words)
        )
        red_flash = ApplyMethod(
            lower_filter.set_fill, RED,
            rate_func = squish_rate_func(there_and_back, 0.4, 0.6),
            run_time = filtered_photon.run_time
        )
        for x in range(4):
            self.play(
                passing_photon,
                filtered_photon,
                green_flash,
                red_flash,
            )
            self.wait()

class PhotonPassesCompletelyOrNotAtAllForWavesVideo(PhotonPassesCompletelyOrNotAtAll):
    CONFIG = {
        "show_M_vects" : False,
    }    

class DirectionOfPolarization(DirectionOfPolarizationScene):
    def construct(self):
        self.remove(self.pol_filter)
        self.axes.z_axis.rotate(np.pi/2, OUT)
        words = TextMobject("Polarization direction")
        words.next_to(ORIGIN, UP+RIGHT, LARGE_BUFF)
        words.shift(2*UP)
        words.rotate(np.pi/2, RIGHT)
        words.rotate(-np.pi/2, OUT)

        em_wave = self.em_wave

        self.add(em_wave)
        self.wait(2)
        self.move_camera(
            phi = self.target_phi,
            theta = self.target_theta
        )
        self.play(Write(words, run_time = 1))
        for angle in 2*np.pi/3, -np.pi/3, np.pi/4:
            self.change_polarization_direction(angle)
            self.wait()
        self.wait(2)

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
            "start_point" : FRAME_X_RADIUS*LEFT + DOWN + OUT,
        },
        "apply_filter" : False,
    }
    def construct(self):
        photons = self.get_photons()
        prob_text = self.get_probability_text()
        self.pol_filters = VGroup(*reversed(self.pol_filters))
        ninety_filter, zero_filter = self.pol_filters
        self.remove(*self.pol_filters)

        self.play(DrawBorderThenFill(zero_filter), run_time = 1)
        self.add_foreground_mobject(zero_filter)
        self.move_camera(
            theta = self.target_theta,
            added_anims = [ApplyFunction(
                self.reposition_filter_label,
                zero_filter
            )]
        )
        self.reposition_filter_label(ninety_filter)
        self.play(self.get_photons()[2])
        self.play(FadeIn(ninety_filter))
        self.add_foreground_mobject(ninety_filter)
        self.shoot_photon()
        self.shoot_photon()
        self.play(FadeIn(prob_text))
        for x in range(6):
            self.shoot_photon()

    def reposition_filter_label(self, pf):
        pf.arrow_label.rotate_in_place(np.pi/2, OUT)
        pf.arrow_label.next_to(pf.arrow, RIGHT)
        return pf


    def shoot_photon(self, *added_anims):
        photon = self.get_photons()[1]
        pol_filter = self.pol_filters[0]
        absorption = self.get_filter_absorption_animation(pol_filter, photon)
        self.play(photon, absorption)


    def get_photons(self):
        self.reference_line.rotate(np.pi/4)
        self.update_mobjects()
        return [
            WavePacket(
                filter_distance = FRAME_X_RADIUS + x,
                get_filtered = True,
                em_wave = self.em_wave.copy(),
                run_time = 1,
            )
            for x in (-2, 2, 10)
        ]

    def get_probability_text(self, prob = 0):
        prob_text = TexMobject(
            "P(", "\\substack", "{\\text{photons that make it} \\\\ ", 
            " \\text{here } ", "\\text{make it}", 
            " \\text{ here} }", ")", "=", str(int(prob*100)), "\\%",
            arg_separator = ""
        )
        here1, here2 = prob_text.get_parts_by_tex("here")
        here1.set_color(GREEN)
        here2.set_color(RED)
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
            for here, x in ((here1, 0), (here2, 4))
        ]
        prob_text.add(*arrows)

        return prob_text

class MoreFiltersMoreLight(FilterScene):
    CONFIG = {
        "filter_x_coordinates" : list(range(-2, 3)),
        "pol_filter_configs" : [
            {
                "include_arrow_label" : False,
                "filter_angle" : angle
            }
            for angle in np.linspace(0, np.pi/2, 5)
        ],
        "ambient_rotation_rate" : 0,
        "arrow_rgb" : (0, 0, 0),
        "background_rgb" : (245, 245, 245), 
    }
    def construct(self):
        self.remove(self.axes)
        pfs = VGroup(*reversed(self.pol_filters))
        self.color_filters(pfs)
        self.remove(pfs)
        self.build_color_map(pfs)
        self.add(pfs[0], pfs[2], pfs[4])
        pfs.center().scale(1.5)

        self.move_camera(
            phi = 0.9*np.pi/2,
            theta = -0.95*np.pi,
        )
        self.play(
            Animation(pfs[0]),
            pfs[2].shift, 3*OUT,
            Animation(pfs[4]),
        )
        self.wait()
        self.play(
            Animation(pfs[0]),
            pfs[2].shift, 3*IN,
            Animation(pfs[4]),
        )

        pfs[1].shift(8*OUT)
        self.play(
            Animation(pfs[0]),
            pfs[1].shift, 8*IN,
            Animation(VGroup(pfs[2], pfs[4])),
            run_time = 2
        )
        self.wait()

        pfs[3].shift(8*OUT)
        self.play(
            Animation(VGroup(*pfs[:3])),
            pfs[3].shift, 8*IN,
            Animation(VGroup(*pfs[4:])),
            run_time = 2
        )
        self.wait()

    def color_filters(self, pfs):
        colors = [RED, GREEN, BLUE, MAROON_B, PURPLE_C]
        for pf, color in zip(pfs, colors):
            pf.set_fill(color, 0.5)
            pf.arrow.set_fill(WHITE, 1)
        turn_off_3d_shading(pfs)

    def build_color_map(self, pfs):
        phi, theta = self.camera.get_phi(), self.camera.get_theta()
        self.set_camera_orientation(np.pi/2, -np.pi)

        self.original_rgbas = [(255, 255, 255)]
        self.new_rgbas = [self.arrow_rgb]
        for bool_array in it.product(*5*[[True, False]]):
            pfs_to_use = VGroup(*[
                pf
                for pf, b in zip(pfs, bool_array)
                if b
            ])
            self.camera.capture_mobject(pfs_to_use)
            frame = self.camera.get_image()
            h, w, three = frame.shape
            rgb = frame[3*h/8, 7*w/12]
            self.original_rgbas.append(rgb)

            angles = [pf.filter_angle for pf in pfs_to_use]
            p = 0.5
            for a1, a2 in zip(angles, angles[1:]):
                p *= np.cos(a2 - a1)**2
            new_rgb = (255*p*np.ones(3)).astype(int)
            if not any(bool_array):
                new_rgb = self.background_rgb

            self.new_rgbas.append(new_rgb)
            self.camera.reset()
        self.set_camera_orientation(phi, theta)

    def update_frame(self, mobjects = None, image = None):
        FilterScene.update_frame(self, mobjects)

    def get_frame(self):
        frame = FilterScene.get_frame(self)
        bool_arrays = [
            (frame[:,:,0] == r) & (frame[:,:,1] == g) & (frame[:,:,2] == b)
            for (r, g, b) in self.original_rgbas
        ]
        for ba, new_rgb in zip(bool_arrays, self.new_rgbas):
            frame[ba] = new_rgb
        covered = reduce(
            lambda b1, b2 : b1 | b2,
            bool_arrays
        )
        frame[~covered] = [65, 65, 65]
        return frame

class MoreFiltersMoreLightBlackBackground(MoreFiltersMoreLight):
    CONFIG = {
        "arrow_rgb" : (255, 255, 255),
        "background_rgb" : (0, 0, 0),    
    }

class ConfusedPiCreature(Scene):
    def construct(self):
        randy = Randolph()
        self.play(
            randy.change, "confused", 3*(UP+RIGHT),
        )
        self.play(Blink(randy))
        self.wait(2)
        self.play(Blink(randy))
        self.wait(2)

class AngryPiCreature(PiCreatureScene):
    def construct(self):
        self.pi_creature_says(
            "No, \\emph{locality} \\\\ must be wrong!",
            target_mode = "angry",
            look_at_arg = 2*RIGHT,
            run_time = 1
        )
        self.wait(3)

    def create_pi_creature(self):
        return Randolph().shift(DOWN+3*LEFT)

class ShowALittleMath(TeacherStudentsScene):
    def construct(self):
        exp1 = TexMobject(
            "|", "\\psi", "\\rangle = ",
            "\\alpha", "|\\uparrow\\rangle", 
            "+", "\\beta", "|\\rightarrow\\rangle"
        )
        exp2 = TexMobject(
            "|| \\langle", "\\psi", "|", "\\psi", "\\rangle ||^2",
            "= ", "\\alpha", "^2", "+", "\\beta", "^2"
        )
        color_map = {
            "alpha" : GREEN,
            "beta" : RED,
            "psi" : BLUE
        }
        for exp in exp1, exp2:
            exp.set_color_by_tex_to_color_map(color_map)
        exp1.next_to(self.teacher.get_corner(UP+LEFT), UP, LARGE_BUFF)

        exp2.move_to(exp1)

        self.play(
            Write(exp1, run_time = 2),
            self.teacher.change, "raise_right_hand"
        )
        self.play(exp1.shift, UP)
        self.play(*[
                ReplacementTransform(
                    exp1.get_parts_by_tex(tex).copy(),
                    exp2.get_parts_by_tex(tex).copy(),
                )
                for tex in list(color_map.keys())
        ] + [Write(exp2, run_time = 2)])
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = exp2
        )
        self.wait(2)

class SecondVideoWrapper(Scene):
    def construct(self):
        title = TextMobject("Some light quantum mechanics")
        title.to_edge(UP)
        self.add(title)

        screen_rect = ScreenRectangle(height = 6)
        screen_rect.next_to(title, DOWN)
        self.play(ShowCreation(screen_rect))
        self.wait(3)

class BasicsOfPolarization(DirectionOfPolarizationScene):
    CONFIG = {
        "apply_filter" : True,
    }
    def construct(self):
        self.setup_rectangles()
        self.show_continual_wave()
        self.show_photons()

    def show_continual_wave(self):
        em_wave = self.em_wave

        title = TextMobject("Waves in the ``electromagnetic field''")
        title.to_edge(UP)
        subtitle = TextMobject("Polarization = Direction of", "wiggling")
        subtitle.set_color_by_tex("wiggling", BLUE)
        subtitle.next_to(title, DOWN)
        for words in title, subtitle:
            words.add_background_rectangle()
            words.rotate(np.pi/2, RIGHT)

        self.play(Write(title))
        self.wait(2)
        self.play(
            Write(subtitle, run_time = 2),
            FadeIn(self.rectangles)
        )
        self.change_polarization_direction(np.pi/2, run_time = 3)
        self.wait()
        self.change_polarization_direction(-np.pi/12, run_time = 2)
        self.move_camera(theta = -0.95*np.pi)
        self.change_polarization_direction(-np.pi/6, run_time = 2)
        self.change_polarization_direction(np.pi/6, run_time = 2)
        self.move_camera(theta = -0.6*np.pi)
        self.change_polarization_direction(-np.pi/6, run_time = 2)
        self.change_polarization_direction(np.pi/6, run_time = 2)
        self.change_polarization_direction(-5*np.pi/12, run_time = 2)
        self.play(
            FadeOut(em_wave.mobject),
            FadeOut(self.rectangles),
        )
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
        quantum_right_words.set_color_by_tex("through", GREEN)
        quantum_right_words.set_color_by_tex("blocked", RED)
        quantum_words = VGroup(quantum_left_words, quantum_right_words)
        quantum_words.rotate(np.pi/2, RIGHT)

        prob_eq = TexMobject(
            "&P(", "\\text{Pass}", ")", "=", "p\\\\",
            "&P(", "\\text{Blocked}", ")", "=", "1-p",
        )
        prob_eq.set_color_by_tex_to_color_map({
            "Pass" : GREEN,
            "Blocked" : RED,
        })
        prob_eq.next_to(ORIGIN, DOWN+RIGHT)
        prob_eq.shift(RIGHT)
        prob_eq.rotate(np.pi/2, RIGHT)

        config = dict(self.EMWave_config)
        config.update({
            "wave_number" : 0,
            "A_vect" : [0, 1, -1],
        })
        self.em_wave = EMWave(**config)
        self.update_mobjects()
        passing_photon = WavePacket(
            em_wave = self.em_wave.copy(),
            run_time = 1.5,
        )
        filtered_photon = WavePacket(
            em_wave = self.em_wave.copy(),
            get_filtered = True,
            run_time = 1.5,
        )

        self.play(FadeIn(
            quantum_words,
            run_time = 2,
            lag_ratio = 0.5
        ))
        anim_sets = [
            [passing_photon],
            [
                filtered_photon,
                self.get_filter_absorption_animation(
                    self.pol_filter,
                    filtered_photon
                )
            ],
        ]

        for index in 0, 1:
            self.play(*anim_sets[index])
        self.play(
            # FadeIn(prob_eq, lag_ratio = 0.5),
            passing_photon
        )
        for index in 1, 0, 0, 1:
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

        h_line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS)
        h_line.to_edge(UP, buff = 2)
        v_line = Line(UP, DOWN).scale(FRAME_Y_RADIUS)
        v_line.next_to(left_title, RIGHT, MED_LARGE_BUFF)
        v_line.to_edge(UP, buff = 0)
        VGroup(h_line, v_line).set_color(BLUE)
        self.add(left_title, right_title, h_line, v_line)

        angles = [0, 22.5, 45, 67.5, 90]
        angle_mobs = VGroup(*[
            TexMobject(str(angle) + "^\\circ")
            for angle in angles
        ])
        angle_mobs.arrange(DOWN, buff = MED_LARGE_BUFF)
        angle_mobs.next_to(left_title, DOWN, LARGE_BUFF)

        probs = [
            np.cos(angle*np.pi/180.0)**2
            for angle in angles
        ]
        prob_mobs = VGroup(*[
            TexMobject("%.1f"%(100*prob) + "\\%")
            for prob in probs
        ])
        prob_mobs.set_color(YELLOW)

        angle_prob_pairs = list(zip(angle_mobs, prob_mobs))
        for angle_mob, prob_mob in angle_prob_pairs:
            prob_mob.next_to(angle_mob, RIGHT, buff = 3)
        for prob_mob in prob_mobs[1:]:
            prob_mob.align_to(prob_mobs[0], LEFT)


        for i in [0, 4, 2, 1, 3]:
            self.play(FadeIn(angle_mobs[i]))
            self.play(ReplacementTransform(
                angle_mobs[i].copy(), prob_mobs[i]
            ))

        explanation = TextMobject("Based on $\\cos(\\theta)^2$")
        explanation.next_to(prob_mobs, RIGHT, LARGE_BUFF)
        self.play(Write(explanation, run_time = 2))
        self.wait()

class ShowVariousFilterPairsWithPhotonsOverTime(PhotonsThroughPerpendicularFilters):
    CONFIG = {
        "filter_x_coordinates" : [-2, 2, 2, 2, 2],
        "pol_filter_configs" : [
            {"filter_angle" : angle}
            for angle in (0, 0, np.pi/2, np.pi/4, np.pi/8)
        ],
        "apply_filter" : False,
    }
    def setup(self):
        PhotonsThroughPerpendicularFilters.setup(self)
        self.new_filters = self.pol_filters[2:]
        self.remove(*self.new_filters)
        self.pol_filters = self.pol_filters[:2]

    def construct(self):
        self.photons = self.get_photons()

        self.add_filters()
        self.add_probability_text()
        self.show_photons()
        for pol_filter in self.new_filters:
            self.change_to_new_filter(pol_filter)
            self.show_photons()

    def add_filters(self):
        self.remove(*self.pol_filters[1:])
        self.wait()
        self.play(ReplacementTransform(
            self.pol_filters[0].copy().set_fill(BLACK, 1),
            self.pol_filters[1]
        ))
        self.move_camera(
            theta = -0.65*np.pi,
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
        first_absorption = self.get_filter_absorption_animation(
            self.pol_filters[0], blocked_photon
        )
        first_absorption.rate_func = squish_rate_func(
            first_absorption.rate_func, 0, 0.5,
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
            if photon.filter_distance == FRAME_X_RADIUS + 2:
                absorption = self.get_filter_absorption_animation(
                    self.second_filter, photon
                )
                absorption.rate_func = squish_rate_func(
                    absorption.rate_func, 0.5, 1
                )
                added_anims.append(absorption)
            self.play(
                blocked_photon,
                first_absorption,
                photon, 
                *added_anims
            )
        self.wait()
        
    def change_to_new_filter(self, pol_filter, added_anims = None):
        if added_anims is None:
            added_anims = []
        self.play(
            Transform(self.second_filter, pol_filter),
            *added_anims
        )
        self.second_filter.filter_angle = pol_filter.filter_angle
        new_prob_text = self.get_probability_text(self.get_prob())
        new_prob_text[1][-2].set_color(YELLOW)
        self.play(Transform(self.prob_text, new_prob_text))

    ####

    def get_prob(self, pol_filter = None):
        if pol_filter is None:
            pol_filter = self.second_filter
        return np.cos(pol_filter.filter_angle)**2

class ShowVariousFilterPairs(ShowVariousFilterPairsWithPhotonsOverTime):
    CONFIG = {
        "filter_x_coordinates" : [],
        "filter_z_coordinates" : [2.5, 0, -2.5],
        "angles" : [0, np.pi/4, np.pi/2],
        "n_lines" : 20,
        "new_group_shift_val" : 2.5*IN,
        "prev_group_shift_val" : 1.75*IN,
        "ambient_rotation_rate" : 0.015,
        "line_start_length" : 16,
        "line_end_length" : 16,
        "lines_depth" : 1.2,
        "lines_shift_vect" : SMALL_BUFF*OUT,
    }
    def setup(self):
        ShowVariousFilterPairsWithPhotonsOverTime.setup(self)
        self.remove(*self.pol_filters)
        self.prev_groups = VGroup()
        self.remove(self.axes)
        self.setup_filters()
        self.stop_ambient_camera_rotation()
        self.prob_texts = VGroup()

    def setup_filters(self):
        self.filter_pairs = []
        zs = self.filter_z_coordinates
        for non_zero_angle, z in zip(self.angles, zs):
            filter_pair = VGroup()
            for angle, x in (0, -3), (non_zero_angle, 3):
                pf = PolarizingFilter(filter_angle = angle)
                pf.scale(0.7)
                pf.rotate(np.pi/2, RIGHT)
                pf.rotate(np.pi/2, IN)
                pf.shift(x*RIGHT + z*OUT)
                pf.arrow_label.rotate(np.pi/2, OUT)
                pf.arrow_label.next_to(pf.arrow, RIGHT, SMALL_BUFF)

                filter_pair.add(pf)
            self.filter_pairs.append(filter_pair)

    def construct(self):
        self.add_top_filters()
        self.show_light(self.filter_pairs[0])
        self.turn_one_filter_pair_into_another(0, 2)
        self.show_light(self.filter_pairs[2])
        self.turn_one_filter_pair_into_another(2, 1)
        self.show_light(self.filter_pairs[1])

    def add_top_filters(self):
        pf1, pf2 = pair = self.filter_pairs[0]
        for pf in pair:
            pf.save_state()
            pf.arrow_label.rotate(np.pi/2, IN)
            pf.arrow_label.next_to(pf.arrow, UP, SMALL_BUFF)
            pf.shift(2*IN)

        self.add(pf1)
        self.play(
            ReplacementTransform(pf1.copy().fade(1), pf2),
            Animation(pf1)
        )
        self.move_camera(
            0.9*np.pi/2, -0.6*np.pi,
            added_anims = [
                pf.restore 
                for pf in pair
            ]
        )

    def show_light(self, filter_pair):
        pf1, pf2 = filter_pair
        lines_to_pf1 = self.get_lines(None, pf1)
        vect = lines_to_pf1[1].get_center() - lines_to_pf1[0].get_center()
        lines_to_pf1.add(*lines_to_pf1.copy().shift(vect/2))
        lines_to_pf2 = self.get_lines(pf1, pf2)
        lines_from_pf2 = self.get_lines(pf2)

        prob = self.get_prob(pf2)
        n_black = int(prob*len(lines_from_pf2))
        VGroup(*lines_from_pf2[n_black:]).set_stroke(BLACK, 0)

        kwargs = {
            "rate_func" : None,
            "lag_ratio" : 0,
        }

        self.play(ShowCreation(lines_to_pf1, run_time = 2./3, **kwargs))
        self.play(
            ShowCreation(lines_to_pf2, **kwargs),
            Animation(VGroup(pf1, lines_to_pf1)),
            run_time = 1./6,
        )
        self.play(
            ShowCreation(lines_from_pf2, **kwargs),
            Animation(VGroup(pf2, lines_to_pf2, pf1, lines_to_pf1)),
            run_time = 2./3,
        )

        group = VGroup(
            lines_from_pf2, pf2, lines_to_pf2, pf1, lines_to_pf2
        )

        #Write probability
        prob_text = self.get_probability_text(pf2)
        self.play(Write(prob_text, run_time = 1))
        self.wait()

        self.prob_texts.add(prob_text)

    def turn_one_filter_pair_into_another(self, i1, i2):
        mover = self.filter_pairs[i1].copy()
        mover.set_stroke(width = 0)
        mover.set_fill(opacity = 0)
        target = self.filter_pairs[i2]
        self.play(ReplacementTransform(mover, target))

    def get_probability_text(self, pol_filter = None):
        if pol_filter is None:
            pol_filter = self.second_filter
        prob = self.get_prob(pol_filter)
        prob_mob = TextMobject(str(int(prob*100)) + "\\%", " pass")
        prob_mob.scale(0.7)
        prob_mob.rotate(np.pi/2, RIGHT)
        prob_mob.next_to(pol_filter.arrow_label, RIGHT)
        prob_mob.set_color(
            list(Color(RED).range_to(GREEN, 11))[int(prob*10)]
        )
        return prob_mob


    #####

    def get_lines(
        self, filter1 = None, filter2 = None, 
        ratio = 1.0,
        remove_from_bottom = False,
        ):
        # n = int(ratio*self.n_lines)
        n = self.n_lines
        start, end = [
            (f.point_from_proportion(0.75) if f is not None else None)
            for f in (filter1, filter2)
        ]
        if start is None:
            start = end + self.line_start_length*LEFT
        if end is None:
            end = start + self.line_end_length*RIGHT
        nudge = (float(self.lines_depth)/self.n_lines)*OUT
        lines = VGroup(*[
            Line(start, end).shift(z*nudge)
            for z in range(n)
        ])
        lines.set_stroke(YELLOW, 2)
        lines.move_to(start, IN+LEFT)
        lines.shift(self.lines_shift_vect)
        n_to_block = int((1-ratio)*self.n_lines)
        if remove_from_bottom:
            to_block = lines[:n_to_block]
        else:
            to_block = lines[len(lines)-n_to_block:]
        VGroup(*to_block).set_stroke(width = 0)
        return lines

class ShowVariousFilterPairsFrom0To45(ShowVariousFilterPairs):
    CONFIG = {
        "angles" : [0, np.pi/8, np.pi/4]
    }
    def construct(self):
        ShowVariousFilterPairs.construct(self)
        self.mention_probabilities()

    def mention_probabilities(self):
        rects = VGroup()
        for prob_text in self.prob_texts:
            prob_text.rotate(np.pi/2, LEFT)
            rect = SurroundingRectangle(prob_text, color = BLUE)
            VGroup(prob_text, rect).rotate(np.pi/2, RIGHT)
            rects.add(rect)

        cosines = VGroup(*[
            TexMobject("\\cos^2(%s^\\circ)"%str(x))
            for x in (45, 22.5)
        ])
        cosines.scale(0.8)
        # cosines.set_color(BLUE)
        cosines.rotate(np.pi/2, RIGHT)
        for cos, rect in zip(cosines, rects[1:]):
            cos.next_to(rect, OUT, SMALL_BUFF)

        self.play(LaggedStartMap(ShowCreation, rects))
        self.wait()
        self.play(*list(map(Write, cosines)), run_time = 2)
        self.wait()

class ForgetPreviousActions(ShowVariousFilterPairs):
    CONFIG = {
        "filter_x_coordinates" : [-6, -2, 2, 2, 2],
        "pol_filter_configs" : [
            {"filter_angle" : angle}
            for angle in (np.pi/4, 0, np.pi/4, np.pi/3, np.pi/6)
        ],
        "start_theta" : -0.6*np.pi,
        "EMWave_config" : {
            "wave_number" : 0,
            "start_point" : FRAME_X_RADIUS*LEFT + DOWN,
        },
        "apply_filter" : False,
    }
    def setup(self):
        PhotonsThroughPerpendicularFilters.setup(self)
        self.remove(self.axes)

        VGroup(*self.pol_filters).shift(IN)

        for pf in self.pol_filters:
            pf.arrow_label.rotate_in_place(np.pi/2, OUT)
            pf.arrow_label.next_to(pf.arrow, RIGHT)

        self.stop_ambient_camera_rotation()

    def construct(self):
        front_filter = self.pol_filters[0]
        first_filter = self.pol_filters[1]
        possible_second_filters = self.pol_filters[2:]
        for pf in possible_second_filters:
            prob_text = self.get_probability_text(pf)
            prob_text.scale(1.3, about_point = prob_text.get_left())
            pf.add(prob_text)

        second_filter = possible_second_filters[0].copy()
        self.second_filter = second_filter
        self.pol_filters = VGroup(
            first_filter, second_filter
        )
        self.remove(front_filter)
        self.remove(*possible_second_filters)
        self.add(second_filter)
        self.apply_filter = True
        self.update_mobjects()
        self.photons = self.get_photons()[1:]

        group = VGroup(*self.pol_filters)
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
        self.play(FadeIn(prob_words))
        for index in 1, 2:
            self.shoot_photon()
            self.play(Transform(
                second_filter, possible_second_filters[index]
            ))

        rect2 = SurroundingRectangle(front_filter, color = RED)
        rect2.rotate_in_place(np.pi/2, RIGHT)
        rect2.rescale_to_fit(front_filter.get_depth()+MED_SMALL_BUFF, 2, True)
        rect2.stretch_in_place(1.5, 0)
        ignore_words = TextMobject("Photon \\\\", "``forgets'' this")
        ignore_words.add_background_rectangle()
        ignore_words.rotate(np.pi/2, RIGHT)
        ignore_words.next_to(rect2, OUT)

        self.play(
            ShowCreation(rect2), 
            Write(ignore_words, run_time = 1),
            FadeIn(front_filter),
            run_time = 1.5,
        )
        self.shoot_photon()
        for index in 0, 1, 2:
            self.play(Transform(
                second_filter, possible_second_filters[index]
            ))
            self.shoot_photon()

    def shoot_photon(self):
        photon = random.choice(self.photons)
        added_anims = []
        if photon.filter_distance == FRAME_X_RADIUS + 2:
            added_anims.append(
                ApplyMethod(
                    self.second_filter.set_color, RED,
                    rate_func = squish_rate_func(there_and_back, 0.5, 0.7)
                )
            )
        self.play(photon, *added_anims, run_time = 1.5)

class IntroduceLabeledFilters(ShowVariousFilterPairs):
    CONFIG = {
        "filter_x_coordinates" : [-5, -2, 1],
        "pol_filter_configs" : [
            {"filter_angle" : angle}
            for angle in [0, np.pi/8, np.pi/4]
        ],
        "start_phi" : 0.9*np.pi/2,
        "start_theta" : -0.85*np.pi,
        "target_theta" : -0.65*np.pi,
        "lines_depth" : 1.7,
        "lines_shift_vect" : MED_SMALL_BUFF*OUT,
        "line_start_length" : 3,
        "line_end_length" : 9,
        "ambient_rotation_rate" : 0.005,
    }
    def setup(self):
        PhotonsThroughPerpendicularFilters.setup(self)
        self.remove(self.axes)

    def construct(self):
        self.add_letters_to_labels()
        self.introduce_filters()
        self.reposition_camera()
        self.separate_cases()
        self.show_bottom_lines()
        self.comment_on_half_blocked_by_C()
        self.show_top_lines()
        self.comment_on_those_blocked_by_B()
        self.show_sum()

    def add_letters_to_labels(self):
        for char, pf, color in zip("ABC", self.pol_filters, [RED, GREEN, BLUE]):
            label = TextMobject(char)
            label.scale(0.9)
            label.add_background_rectangle()
            label.set_color(color)
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
            self.wait()

    def reposition_camera(self):
        self.move_camera(
            theta = self.target_theta, 
            added_anims = list(it.chain(*[
                [
                    pf.arrow_label.rotate, np.pi/2, OUT,
                    pf.arrow_label.next_to, pf.arrow, RIGHT
                ]
                for pf in self.pol_filters
            ]))
        )

    def separate_cases(self):
        self.lower_pol_filters = VGroup(
            self.A_filter.deepcopy(),
            self.C_filter.deepcopy(),
        )
        self.lower_pol_filters.save_state()
        self.lower_pol_filters.fade(1)

        self.play(
            self.lower_pol_filters.restore,
            self.lower_pol_filters.shift, 3*IN,
            self.pol_filters.shift, 1.5*OUT,
        )
        self.wait()

    def show_bottom_lines(self):
        A, C = self.lower_pol_filters
        lines_to_A = self.get_lines(None, A)
        vect = lines_to_A[1].get_center() - lines_to_A[0].get_center()
        lines_to_A.add(*lines_to_A.copy().shift(vect/2))
        lines_to_C = self.get_lines(A, C)
        lines_from_C = self.get_lines(C, ratio = 0.5)
        kwargs = {
            "rate_func" : None,
            "lag_ratio" : 0,
            "run_time" : 1./3,
        }
        self.play(
            ShowCreation(lines_to_A),
            **kwargs
        )
        self.play(
            ShowCreation(lines_to_C),
            Animation(VGroup(A, lines_to_A)),
            **kwargs
        )
        kwargs["run_time"] = 3*kwargs["run_time"]
        self.play(
            ShowCreation(lines_from_C),
            Animation(VGroup(C, lines_to_C, A, lines_to_A)),
            **kwargs
        )

        line_group = VGroup(lines_from_C, C, lines_to_C, A, lines_to_A)
        self.remove(*line_group)
        self.add_foreground_mobject(line_group)

        self.bottom_lines_group = line_group

    def comment_on_half_blocked_by_C(self):
        arrow = Arrow(
            ORIGIN, 3.5*RIGHT,
            path_arc = -0.9*np.pi,
            color = BLUE,
            stroke_width = 5,
        )
        words = TextMobject("50\\% blocked")
        words.set_color(BLUE)
        words.next_to(arrow, RIGHT, buff = 0)
        group = VGroup(arrow, words)
        group.rotate(np.pi/2, RIGHT)
        group.shift(1.7*IN + 0.5*RIGHT)

        self.play(
            Write(words, run_time = 2),
            ShowCreation(arrow)
        )
        self.wait(2)

        self.blocked_at_C_words = words
        self.blocked_at_C_label_group = VGroup(arrow, words)

    def show_top_lines(self):
        A, B, C = self.pol_filters
        lines_to_A = self.get_lines(None, A)
        vect = lines_to_A[1].get_center() - lines_to_A[0].get_center()
        lines_to_A.add(*lines_to_A.copy().shift(vect/2))
        lines_to_B = self.get_lines(A, B)
        lines_to_C = self.get_lines(B, C, ratio = 0.85, remove_from_bottom = True)
        lines_from_C = self.get_lines(C, ratio = 0.85**2, remove_from_bottom = True)

        kwargs = {
            "rate_func" : None,
            "lag_ratio" : 0,
            "run_time" : 1./5,
        }
        self.play(
            ShowCreation(lines_to_A),
            **kwargs
        )
        self.play(
            ShowCreation(lines_to_B),
            Animation(VGroup(A, lines_to_A)),
            **kwargs
        )
        self.play(
            ShowCreation(lines_to_C),
            Animation(VGroup(B, lines_to_B, A, lines_to_A)),
            **kwargs
        )
        kwargs["run_time"] = 3*kwargs["run_time"]
        self.play(
            ShowCreation(lines_from_C),
            Animation(VGroup(C, lines_to_C, B, lines_to_B, A, lines_to_A)),
            **kwargs
        )

        line_group = VGroup(
            lines_from_C, C, lines_to_C, B, lines_to_B, A, lines_to_A
        )
        self.remove(*line_group)
        self.add_foreground_mobject(line_group)

        self.top_lines_group = line_group

    def comment_on_those_blocked_by_B(self):
        arrow0 = Arrow(
            2*LEFT, 0.5*(UP+RIGHT),
            path_arc = 0.8*np.pi,
            color = WHITE,
            stroke_width = 5,
            buff = 0
        )
        arrow1 = Arrow(
            2*LEFT, ORIGIN,
            path_arc = 0.8*np.pi,
            color = GREEN,
            stroke_width = 5,
            buff = 0
        )
        arrow2 = arrow1.copy()
        arrow2.next_to(arrow1, RIGHT, buff = LARGE_BUFF)
        words1 = TextMobject("15\\%", "blocked")
        words1.set_color(GREEN)
        words2 = words1.copy()
        words1.next_to(arrow1, DOWN, buff = SMALL_BUFF)
        words2.next_to(arrow2, DOWN, buff = SMALL_BUFF)
        words2.shift(MED_LARGE_BUFF*RIGHT)

        words0 = TextMobject("85\\%", "pass")
        words0.move_to(words1)

        group = VGroup(arrow0, arrow1, arrow2, words0, words1, words2)
        group.rotate(np.pi/2, RIGHT)
        group.shift(0.8*LEFT+1.5*OUT)

        self.play(
            ShowCreation(arrow0),
            Write(words0, run_time = 1)
        )
        self.wait()
        self.play(
            ReplacementTransform(words0, words1),
            ReplacementTransform(arrow0, arrow1),
        )
        self.wait()
        self.play(
            ShowCreation(arrow2),
            Write(words2)
        )
        self.wait(2)

        self.fifteens = VGroup(words1, words2)
        self.blocked_at_B_label_group = VGroup(
            words1, words2, arrow1, arrow2
        )

    def show_sum(self):
        fifteen1, fifteen2 = self.fifteens
        fifty = self.blocked_at_C_words
        plus = TexMobject("+").rotate(np.pi/2, RIGHT)
        plus.move_to(Line(fifteen1.get_right(), fifteen2.get_left()))
        equals = TexMobject("=").rotate(np.pi/2, RIGHT)
        equals.next_to(fifteen2, RIGHT, 2*SMALL_BUFF)
        q_mark = TexMobject("?").rotate(np.pi/2, RIGHT)
        q_mark.next_to(equals, OUT, SMALL_BUFF)
        q_mark.set_color(RED)
        randy = Randolph(mode = "confused").flip()
        randy.scale(0.7)
        randy.rotate(np.pi/2, RIGHT)
        randy.move_to(fifty)
        randy.shift(0.5*RIGHT)
        randy.look_at(equals)
        blinked = randy.copy()
        blinked.rotate(np.pi/2, LEFT)
        blinked.blink()
        blinked.rotate(np.pi/2, RIGHT)

        self.play(
            fifteen1.set_color, YELLOW,
            Write(plus)
        )
        self.play(
            fifteen2.set_color, YELLOW,
            Write(equals)
        )
        self.play(
            fifty.next_to, equals, RIGHT, 2*SMALL_BUFF,
            Write(q_mark),
            FadeIn(randy)
        )
        self.play(Transform(
            randy, blinked, 
            rate_func = squish_rate_func(there_and_back)
        ))
        self.wait(3)

class IntroduceLabeledFiltersNoRotation(IntroduceLabeledFilters):
    CONFIG = {
        "ambient_rotation_rate" : 0,
        "target_theta" : -0.55*np.pi,
    }

class RemoveBFromLabeledFilters(IntroduceLabeledFiltersNoRotation):
    def construct(self):
        self.force_skipping()
        IntroduceLabeledFiltersNoRotation.construct(self)
        self.revert_to_original_skipping_status()

        self.setup_start()
        self.show_filter_B_removal()
        self.fade_in_labels()

    def show_sum(self):
        pass


    def setup_start(self):
        self.remove(self.blocked_at_C_label_group)
        self.remove(self.blocked_at_B_label_group)
        self.remove(self.bottom_lines_group)
        self.top_lines_group.save_state()
        self.top_lines_group.shift(2*IN)

    def show_filter_B_removal(self):
        top_lines_group = self.top_lines_group
        bottom_lines_group = self.bottom_lines_group


        mover = top_lines_group.copy()
        mover.save_state()
        mover.fade(1)

        sl1, sC, sl2, sB, sl3, sA, sl4 = mover
        tl1, tC, tl2, tA, tl3 = bottom_lines_group

        for line in tl2:
            line.scale(0.5, about_point = line.get_end())

        kwargs = {
            "lag_ratio" : 0,
            "rate_func" : None,
        }

        self.play(
            top_lines_group.shift, 2*OUT,
            mover.restore,
            mover.shift, 2.5*IN,
        )
        self.wait()
        self.play(
            ApplyMethod(sB.shift, 4*IN, rate_func = running_start),
            FadeOut(sl1),
            Animation(sC),
            FadeOut(sl2),
        )
        self.play(ShowCreation(tl2, run_time = 0.25, **kwargs))
        self.play(
            ShowCreation(tl1, run_time = 0.5, **kwargs),
            Animation(sC),
            Animation(tl2),
        )
        self.wait()

    def fade_in_labels(self):
        self.play(*list(map(FadeIn, [
            self.blocked_at_B_label_group,
            self.blocked_at_C_label_group,
        ])))
        self.wait()

class NumbersSuggestHiddenVariablesAreImpossible(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "These numbers suggest\\\\",
            "no hidden variables"
        )
        self.change_student_modes("erm", "sassy", "confused")
        self.wait(3)

class VennDiagramProofByContradiction(Scene):
    CONFIG = {
        "circle_colors" : [RED, GREEN, BLUE]
    }
    def construct(self):
        self.setup_venn_diagram_sections()
        self.draw_venn_diagram()
        self.show_100_photons()
        self.show_one_photon_answering_questions()
        self.put_all_photons_in_A()
        self.separate_by_B()
        self.separate_by_C()
        self.show_two_relevant_subsets()

    def draw_venn_diagram(self, send_to_corner = True):
        A, B, C = venn_diagram = VGroup(*[
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
        self.A_to_B_vect = B.get_center() - A.get_center()
        self.A_to_C_vect = C.get_center() - A.get_center()

        venn_diagram.center()
        labels = VGroup()
        alt_labels = VGroup()
        props = [1./12, 0.5, 0]
        angles = [0, np.pi/8, np.pi/4]
        for circle, char, prop, angle in zip(venn_diagram, "ABC", props, angles):
            label, alt_label = [
                TextMobject(
                    "%s \\\\"%start,
                    "through", char + "$\\! \\uparrow$"
                ).set_color_by_tex(char, circle.get_color())
                for start in ("Would pass", "Pass")
            ]
            for mob in label, alt_label:
                mob[-1][-1].rotate_in_place(-angle)
                mob[-1][-1].shift(0.5*SMALL_BUFF*UP)
            center = circle.get_center()
            label.move_to(center)
            label.generate_target()
            point = circle.point_from_proportion(prop)
            alt_label.scale(2)
            for mob in label.target, alt_label:
                mob.next_to(point, point-center, SMALL_BUFF)

            circle.label = label
            circle.alt_label = alt_label
            labels.add(label)
            alt_labels.add(alt_label)

        last_circle = None
        for circle in venn_diagram:
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
        self.wait()

        if hasattr(self, "A_segments"):
            A.add(self.A_segments)

        if send_to_corner:
            group = VGroup(venn_diagram, labels)
            target = VGroup(venn_diagram.copy(), alt_labels)
            target.scale(0.25)
            target.to_corner(UP+RIGHT)
            self.play(Transform(group, target))
            self.remove(group)
            for circle in venn_diagram:
                circle.label = circle.alt_label
                self.add(circle)
        for circle in venn_diagram:
            self.add(circle.label)

        self.venn_diagram = venn_diagram

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
        photons.set_height(6)
        photons.next_to(words, DOWN)
        photons.to_edge(LEFT)

        self.play(
            Write(hundred), Write(s),
            ReplacementTransform(
                VGroup(photon), photons,
                lag_ratio = 0.5
            )
        )

        self.photons = photons
        self.photon_words = words

    def show_one_photon_answering_questions(self):
        photon = self.photons[89]
        photon.save_state()
        photon.generate_target()

        answers = TextMobject(
            "Pass through A?", "Yes\\\\",
            "Pass through B?", "No\\\\",
            "Pass through C?", "No\\\\",
        )
        answers.set_color_by_tex_to_color_map({
            "Yes" : GREEN,
            "No" : RED,
        })
        bubble = ThoughtBubble()
        bubble.add_content(answers)
        bubble.resize_to_content() 
        answers.shift(SMALL_BUFF*(RIGHT+UP))
        bubble_group = VGroup(bubble, answers)
        bubble_group.scale(0.25)
        bubble_group.next_to(photon, UP+RIGHT, buff = 0)

        group = VGroup(photon, bubble_group)
        group.save_state()
        bubble_group.set_fill(opacity = 0)
        bubble_group.set_stroke(width = 0)

        self.play(
            group.restore,
            group.scale, 4,
            group.to_corner, DOWN + RIGHT,
        )
        self.play(photon.eyes.blink_anim())
        self.wait()
        self.play(
            FadeOut(bubble_group),
            photon.restore,
        )

    def put_all_photons_in_A(self):
        A, B, C = circles = self.venn_diagram[:3]
        A_group, B_group, C_group = [
            VGroup(circle, circle.label)
            for circle in circles
        ]
        B_group.save_state()
        C_group.save_state()

        A.generate_target()
        A.target.scale(4)
        A.target.shift(
            (FRAME_Y_RADIUS-MED_LARGE_BUFF)*UP - \
            A.target.get_top()
        )
        A.label.generate_target()
        A.label.target.scale(2)
        A.label.target.next_to(
            A.target.point_from_proportion(0.1),
            UP+RIGHT, SMALL_BUFF
        )

        self.play(
            B_group.fade, 1,
            C_group.fade, 1,
            MoveToTarget(A),
            MoveToTarget(A.label),
            FadeOut(self.photon_words),
            self.photons.set_height,
                0.85*A.target.get_height(),
            self.photons.space_out_submobjects, 0.8,
            self.photons.move_to, A.target,
        )
        self.wait()

        self.A_group = A_group
        self.B_group = B_group
        self.C_group = C_group

    def separate_by_B(self):
        A_group = self.A_group
        B_group = self.B_group
        photons = self.photons
        B = B_group[0]

        B.target, B.label.target = B_group.saved_state
        B.target.scale(4)
        B.target.move_to(A_group[0])
        B.target.shift(self.A_to_B_vect)
        B.label.target.scale(2)
        B.label.target.next_to(
            B.target.point_from_proportion(0.55),
            LEFT, SMALL_BUFF
        )

        B_center = B.target.get_center()
        photons.sort(
            lambda p : get_norm(p-B_center)
        )
        in_B = VGroup(*photons[:85])
        out_of_B = VGroup(*photons[85:])
        out_of_B.sort(lambda p : np.dot(p, 2*UP+LEFT))

        self.play(
            MoveToTarget(B),
            MoveToTarget(B.label),
            in_B.shift, 0.5*DOWN+0.2*LEFT,
            out_of_B.scale_in_place, 1./0.8,
            out_of_B.shift, 0.15*(UP+RIGHT),
        )

        words1 = TextMobject("85 also \\\\", "pass ", "B")
        words1.set_color_by_tex("B", GREEN)
        words1.scale(0.8)
        words1.next_to(A_group, LEFT, LARGE_BUFF).shift(UP)
        arrow1 = Arrow(
            words1.get_right(), 
            in_B.get_corner(UP+LEFT) + MED_LARGE_BUFF*(DOWN+RIGHT)
        )
        arrow1.set_color(GREEN)

        words2 = TextMobject("15 blocked \\\\", "by ", "B")
        words2.set_color_by_tex("B", GREEN)
        words2.scale(0.8)
        words2.next_to(A_group, LEFT, MED_LARGE_BUFF, UP)
        arrow2 = Arrow(words2.get_right(), out_of_B[-1])
        arrow2.set_color(RED)

        self.play(
            Write(words1, run_time = 1),
            ShowCreation(arrow1),
            self.in_A_in_B.set_fill, GREEN, 0.5,
            Animation(in_B),
        )
        self.wait()
        self.play(
            ReplacementTransform(words1, words2),
            ReplacementTransform(arrow1, arrow2),
            self.in_A_in_B.set_fill, None, 0,
            Animation(in_B),
            self.in_A_out_B.set_fill, RED, 0.5,
            Animation(out_of_B)
        )
        self.wait()
        self.play(ApplyMethod(
            VGroup(self.in_A_out_B, out_of_B).shift,
            MED_LARGE_BUFF*UP, 
            rate_func = wiggle,
            run_time = 1.5,
        ))
        self.wait(0.5)

        self.in_B = in_B
        self.out_of_B = out_of_B
        self.out_of_B_words = words2
        self.out_of_B_arrow = arrow2

    def separate_by_C(self):
        A_group = self.A_group
        B_group = self.B_group
        C_group = self.C_group
        in_B = self.in_B
        A, B, C = self.venn_diagram

        C.target, C.label.target = C_group.saved_state
        C.target.scale(4)
        C.target.move_to(A)
        C.target.shift(self.A_to_C_vect)
        C_center = C.target.get_center()
        C.label.target.scale(2)
        C.label.target.next_to(
            C.target.point_from_proportion(0),
            DOWN+RIGHT, buff = SMALL_BUFF
        )

        in_B.sort(
            lambda p : get_norm(p - C_center)
        )
        in_C = VGroup(*in_B[:-11])
        out_of_C = VGroup(*in_B[-11:])
        in_C_out_B = VGroup(*self.out_of_B[:6])

        words = TextMobject(
            "$15\\%$", "passing", "B \\\\",
            "get blocked by ", "C",
        )
        words.scale(0.8)
        words.set_color_by_tex_to_color_map({
            "B" : GREEN,
            "C" : BLUE,
        })
        words.next_to(self.out_of_B_words, DOWN, LARGE_BUFF)
        words.to_edge(LEFT)
        percent = words[0]
        pound = TexMobject("\\#")
        pound.move_to(percent, RIGHT)
        less_than_15 = TexMobject("<15")
        less_than_15.next_to(words, DOWN)


        arrow = Arrow(words.get_right(), out_of_C)
        arrow.set_color(GREEN)

        C_copy = C.copy()
        C_copy.set_fill(BLACK, opacity = 1)

        self.play(
            self.in_A_in_B.set_fill, GREEN, 0.5,
            rate_func = there_and_back,
        )
        self.play(
            MoveToTarget(C),
            MoveToTarget(C.label),
            in_C.shift, 0.2*DOWN+0.15*RIGHT,
            out_of_C.shift, SMALL_BUFF*(UP+LEFT),
            in_C_out_B.shift, 0.3*DOWN
        )
        self.play(
            self.in_A_in_B_out_C.set_fill, GREEN, 0.5,
            Write(words, run_time = 1),
            ShowCreation(arrow),
            Animation(out_of_C),
        )
        self.play(ApplyMethod(
            VGroup(self.in_A_in_B_out_C, out_of_C).shift,
            MED_LARGE_BUFF*UP,
            rate_func = wiggle
        ))
        self.wait()
        C.save_state()
        self.play(C.set_fill, BLACK, 1)
        self.wait()
        self.play(C.restore)
        self.wait(2)
        self.play(Transform(percent, pound))
        self.play(Write(less_than_15, run_time = 1))
        self.wait()

        self.in_C = in_C
        self.out_of_C = out_of_C
        words.add(less_than_15)
        self.out_of_C_words = words
        self.out_of_C_arrow = arrow

    def show_two_relevant_subsets(self):
        A, B, C = self.venn_diagram

        all_out_of_C = VGroup(*it.chain(
            self.out_of_B[6:],
            self.out_of_C,
        ))
        everything = VGroup(*self.get_top_level_mobjects())
        photon_groups = [all_out_of_C, self.out_of_C, self.out_of_B]
        regions = [self.in_A_out_C, self.in_A_in_B_out_C, self.in_A_out_B]
        self.play(*[
            ApplyMethod(
                m.scale, 0.7, 
                method_kwargs = {
                    "about_point" : FRAME_Y_RADIUS*DOWN
                }
            )
            for m in everything
        ])

        terms = VGroup(
            TexMobject("N(", "A", "\\checkmark", ",", "C", ")", "\\le"),
            TexMobject(
                "N(", "A", "\\checkmark", ",", 
                "B", "\\checkmark", ",", "C", ")"
            ),
            TexMobject("+\\, N(", "A", "\\checkmark", ",", "B", ")"),
        )
        terms.arrange(RIGHT)
        terms.to_edge(UP)
        for term, index, group in zip(terms, [-3, -2, -2], photon_groups):
            term.set_color_by_tex("checkmark", "#00ff00")
            cross = Cross(term[index])
            cross.set_color("#ff0000")
            cross.set_stroke(width = 8)
            term[index].add(cross)

        less_than = terms[0][-1]
        terms[0].remove(less_than)
        plus = terms[2][0][0]
        terms[2][0].remove(plus)
        rects = list(map(SurroundingRectangle, terms))
        terms[2][0].add_to_back(plus)
        last_rects = VGroup(*rects[1:])

        should_be_50 = TextMobject("Should be 50 \\\\", "...somehow")
        should_be_50.scale(0.8)
        should_be_50.next_to(rects[0], DOWN)

        lt_fifteen = VGroup(self.out_of_C_words[-1]).copy()
        something_lt_15 = TextMobject("(Something", "$<15$", ")")
        something_lt_15.scale(0.8)
        something_lt_15.next_to(rects[1], DOWN)
        lt_fifteen.target = something_lt_15

        fifteen = VGroup(*self.out_of_B_words[0][:2]).copy()
        fifteen.generate_target()
        fifteen.target.scale(1.5)
        fifteen.target.next_to(rects[2], DOWN)

        nums = [should_be_50, lt_fifteen, fifteen]

        cross = Cross(less_than)
        cross.set_color("#ff0000")
        cross.set_stroke(width = 8)

        tweaser_group = VGroup(
            self.in_A_in_B_out_C.copy(),
            self.in_A_out_B.copy(),
        )
        tweaser_group.set_fill(TEAL, 1)
        tweaser_group.set_stroke(TEAL, 5)

        #Fade out B circle
        faders = VGroup(
            B, B.label,
            self.out_of_B_words, self.out_of_C_words,
            self.out_of_B_arrow, self.out_of_C_arrow,
            *regions[1:]
        )
        faders.save_state()

        self.play(faders.fade, 1)
        self.play(Write(terms[0]), run_time = 1)
        self.wait()
        self.photon_thinks_in_A_out_C()
        regions[0].set_stroke(YELLOW, width = 8)
        regions[0].set_fill(YELLOW, opacity = 0.25)
        self.play(
            VGroup(regions[0], all_out_of_C).shift, 0.5*UP,
            run_time = 1.5,
            rate_func = wiggle,
        )
        self.wait(2)

        #Photons jump
        self.photons.save_state()
        self.play(Write(should_be_50[0], run_time = 1))
        self.photons_jump_to_A_not_C_region()
        self.wait()
        self.play(
            faders.restore,
            self.photons.restore,
        )

        self.play(
            faders.restore,
            regions[0].set_fill, None, 0,
            Animation(self.photons)
        )

        #Funny business
        everything_copy = everything.copy().scale(1./3)
        braces = VGroup(
            Brace(everything_copy, LEFT),
            Brace(everything_copy, RIGHT),
        ).scale(3)
        funny_business = TextMobject("Funny business")
        funny_business.scale(1.5)
        funny_business.to_edge(UP)
        funny_business.shift(RIGHT)

        self.play(
            FadeIn(funny_business),
            *list(map(Write, braces)),
            run_time = 1
        )
        self.wait()
        self.play(
            FadeIn(less_than),
            *list(map(FadeOut, [funny_business, braces]))
        )

        for term, group, region, num in zip(terms, photon_groups, regions, nums)[1:]:
            group.set_stroke(WHITE)
            self.play(Write(term, run_time = 1))
            self.wait()
            self.play(
                ApplyMethod(
                    VGroup(region, group).shift, 0.5*UP,
                    rate_func = wiggle,
                    run_time = 1.5,
                ),
            )
            self.play(MoveToTarget(num))
            self.wait()
        self.wait()

        self.play(ShowCreation(rects[0]))
        self.play(
            VGroup(regions[0], all_out_of_C).shift, 0.5*UP,
            run_time = 1.5,
            rate_func = wiggle,
        )
        self.wait()
        self.play(Transform(rects[0], last_rects))
        self.in_A_out_B.save_state()
        self.in_A_in_B_out_C.save_state()
        self.play(
            self.in_A_out_B.set_fill, YELLOW, 0.5,
            self.in_A_in_B_out_C.set_fill, YELLOW, 0.5,
            Animation(self.photons)
        )
        self.wait()
        self.play(
            FadeOut(rects[0]),
            self.in_A_out_B.restore,
            self.in_A_in_B_out_C.restore,
            Animation(self.in_A_out_C),
            Animation(self.photons)
        )
        self.wait()
        self.play(
            FadeIn(should_be_50[1]),
            ShowCreation(cross)
        )

        morty = Mortimer()
        morty.to_corner(DOWN+RIGHT)
        contradiction = TextMobject("Contradiction!")
        contradiction.next_to(morty, UP, aligned_edge = RIGHT)
        contradiction.set_color(RED)

        self.play(FadeIn(morty))
        self.play(
            morty.change, "confused", should_be_50,
            Write(contradiction, run_time = 1)
        )
        self.play(Blink(morty))
        self.wait()

    def photons_jump_to_A_not_C_region(self):
        in_C = self.in_C
        in_C.sort(lambda p : np.dot(p, DOWN+RIGHT))
        movers = VGroup(*self.in_C[:30])
        for mover in movers:
            mover.generate_target()
            mover.target.shift(1.2*UP + 0.6*LEFT)
            mover.target.set_stroke(WHITE)
        self.play(LaggedStartMap(
            MoveToTarget, movers,
            path_arc = np.pi,
            lag_ratio = 0.3
        ))

    def photon_thinks_in_A_out_C(self):
        photon = self.photons[-1]
        photon.save_state()
        photon.generate_target()
        photon.target.scale(4)
        photon.target.center().to_edge(LEFT).shift(DOWN)
        bubble = ThoughtBubble()
        content = TexMobject("A", "\\checkmark", ",", "C")
        content.set_color_by_tex("checkmark", "#00ff00")
        cross = Cross(content[-1])
        cross.set_color("#ff0000")
        content.add(cross)
        bubble.add_content(content)
        bubble.resize_to_content()
        bubble.add(bubble.content)
        bubble.pin_to(photon.target).shift(SMALL_BUFF*RIGHT)
        bubble.save_state()
        bubble.scale(0.25)
        bubble.move_to(photon.get_corner(UP+RIGHT), DOWN+LEFT)
        bubble.fade()

        self.play(
            MoveToTarget(photon),
            bubble.restore,
        )
        self.play(photon.eyes.blink_anim())
        self.play(
            photon.restore, 
            FadeOut(bubble)
        )


    #######

    def setup_venn_diagram_sections(self):
        in_A_out_B, in_A_in_B_out_C, in_A_out_C, in_A_in_B = segments = VGroup(*[
            SVGMobject(
                file_name = "VennDiagram_" + s,
                stroke_width = 0,
                fill_opacity = 0.5,
                fill_color = YELLOW,
            )
            for s in ("in_A_out_B", "in_A_in_B_out_C", "in_A_out_C", "in_A_in_B")
        ])

        in_A_out_B.scale(2.59)
        in_A_out_B.move_to(3.74*UP + 2.97*RIGHT, UP+RIGHT)

        in_A_in_B_out_C.scale(1.84)
        in_A_in_B_out_C.move_to(2.23*UP, UP+RIGHT)

        in_A_out_C.scale(2.56)
        in_A_out_C.move_to(3*LEFT + (3.69)*UP, UP+LEFT)

        in_A_in_B.scale(2.24)
        in_A_in_B.move_to(2.23*UP + 3*LEFT, UP+LEFT)

        segments.set_fill(BLACK, opacity = 0)

        self.in_A_out_B = in_A_out_B
        self.in_A_in_B_out_C = in_A_in_B_out_C
        self.in_A_out_C = in_A_out_C
        self.in_A_in_B = in_A_in_B
        self.A_segments = segments

    def arrange_photons_in_circle(self, photons):
        R = np.sqrt(len(photons) / np.pi)
        pairs = []
        rejected = []
        for x, y in it.product(*[list(range(-int(R)-1, int(R)+2))]*2):
            if x**2 + y**2 < R**2:
                pairs.append((x, y))
            else:
                rejected.append((x, y))
        rejected.sort(
            kay=lambda x, y: (x**2 + y**2)
        )
        for i in range(len(photons) - len(pairs)):
            pairs.append(rejected.pop())
        for photon, (x, y) in zip(photons, pairs):
            photon.set_width(0.7)
            photon.move_to(x*RIGHT + y*UP)
        return photons

class PonderingPiCreature(Scene):
    def construct(self):
        randy = Randolph()
        randy.to_edge(DOWN).shift(3*LEFT)
        self.play(randy.change, "pondering", UP+RIGHT)
        self.play(Blink(randy))
        self.wait(2)
        self.play(Blink(randy))
        self.wait(2)

class ReEmphasizeVennDiagram(VennDiagramProofByContradiction):
    def construct(self):
        self.draw_venn_diagram(send_to_corner = False)
        self.rescale_diagram()
        self.setup_faded_circles()
        self.shift_B_circle()
        self.shift_C_circle()
        self.show_A_not_C_region()
        self.shorten_labels()
        self.show_inequality_with_circle()
        # self.emphasize_containment()
        self.write_50_percent()
        self.write_assumption()
        self.adjust_circles()

    def rescale_diagram(self):
        group = VGroup(self.venn_diagram, *[
            c.label for c in self.venn_diagram
        ])
        self.play(
            group.scale, 0.7,
            group.to_edge, DOWN, MED_SMALL_BUFF,
        )
        self.clear()
        self.add_foreground_mobjects(*group)

    def setup_faded_circles(self):
        self.circles = self.venn_diagram[:3]
        self.black_circles = VGroup(*[
            circ.copy().set_stroke(width = 0).set_fill(BLACK, 1)
            for circ in self.circles
        ])
        self.filled_circles = VGroup(*[
            circ.copy().set_stroke(width = 0).set_fill(circ.get_color(), 1)
            for circ in self.circles
        ])

    def shift_B_circle(self):
        A, B, C = self.circles
        A0, B0, C0 = self.black_circles
        A1, B1, C1 = self.filled_circles

        words = TextMobject("Should be 15\\% \\\\ of circle ", "A")
        words.scale(0.7)
        words.set_color_by_tex("A", RED)
        words.next_to(A, UP, LARGE_BUFF)
        words.shift(RIGHT)
        arrow = Arrow(
            words.get_bottom(),
            A.get_top() + MED_SMALL_BUFF*RIGHT,
            color = RED
        )

        self.play(FadeIn(A1))
        self.play(FadeIn(B0))
        self.play(
            FadeIn(words, lag_ratio = 0.5),
            ShowCreation(arrow)
        )
        self.wait()
        vect = 0.6*(A.get_center() - B.get_center())
        self.play(
            B0.shift, vect,
            B.shift, vect,
            B.label.shift, vect,
            run_time = 2,
            rate_func = running_start,
        )
        B1.shift(vect)
        self.wait()

        self.in_A_out_B_words = words
        self.in_A_out_B_arrow = arrow
        for mob in words, arrow:
            mob.save_state()

    def shift_C_circle(self):
        A, B, C = self.circles
        A0, B0, C0 = self.black_circles
        A1, B1, C1 = self.filled_circles

        words = TextMobject("Should be 15\\% \\\\ of circle ", "B")
        words.scale(0.7)
        words.set_color_by_tex("B", GREEN)
        words.next_to(B, LEFT)
        words.shift(2.5*UP)
        arrow = Arrow(
            words.get_bottom(),
            B.point_from_proportion(0.4),
            color = GREEN
        )

        self.play(
            FadeOut(A1),
            FadeOut(B0),
            self.in_A_out_B_words.fade, 1,
            self.in_A_out_B_arrow.fade, 1,
            FadeIn(B1),
            FadeIn(words, lag_ratio = 0.5),
            ShowCreation(arrow)
        )
        self.play(FadeIn(C0))
        self.wait(2)
        vect = 0.5*(B.get_center() - C.get_center())
        self.play(
            C0.shift, vect,
            C.shift, vect,
            C.label.shift, vect,
            run_time = 2,
            rate_func = running_start,
        )
        C1.shift(vect)
        self.wait()

        for mob in words, arrow:
            mob.save_state()
        self.in_B_out_C_words = words
        self.in_B_out_C_arrow = arrow

    def show_A_not_C_region(self):
        A, B, C = self.circles
        A0, B0, C0 = self.black_circles
        A1, B1, C1 = self.filled_circles
        A1_yellow_copy = A1.copy().set_fill(YELLOW)

        self.play(
            FadeOut(B1),
            FadeOut(C0),
            self.in_B_out_C_words.fade, 1,
            self.in_B_out_C_arrow.fade, 1,
            FadeIn(A1_yellow_copy)
        )
        self.play(FadeIn(C0))
        self.wait()
        self.A1_yellow_copy = A1_yellow_copy

    def shorten_labels(self):
        A, B, C = self.circles
        A0, B0, C0 = self.black_circles
        A1, B1, C1 = self.filled_circles
        for circle in A, B, C:
            circle.pre_label = VGroup(*circle.label[:-1])
            circle.letter = circle.label[-1]

        self.play(
            A.pre_label.fade, 1,
            A.letter.scale, 2,
            A.letter.move_to, A.pre_label, LEFT,
            B.pre_label.fade, 1,
            B.letter.scale, 2, B.letter.get_right(),
            C.pre_label.fade, 1,
            C.letter.scale, 2,
            C.letter.move_to, C.pre_label, LEFT,
            C.letter.shift, DOWN+0.5*LEFT,
        )
        for circle in A, B, C:
            circle.remove(circle.label)
            self.remove(circle.label)
            circle.add(circle.letter)
            self.add(circle.letter)

    def show_inequality_with_circle(self):
        A, B, C = self.circles
        A0, B0, C0 = self.black_circles
        A1, B1, C1 = self.filled_circles
        A1_yellow_copy = self.A1_yellow_copy

        inequality = VGroup(
            TexMobject("N(", "A", "\\checkmark", ",", "C", ")"),
            TexMobject("N(", "B", "\\checkmark", ",", "C", ")"),
            TexMobject("N(", "A", "\\checkmark", ",", "B", ")"),
        )
        inequality.arrange(RIGHT)
        for tex in inequality:
            tex.set_color_by_tex("checkmark", "#00ff00")
            if len(tex) > 1:
                cross = Cross(tex[-2], color = "#ff0000")
                cross.set_stroke(width = 8)
                tex[-2].add(cross)
        inequality.space_out_submobjects(2.1)
        big_le = TexMobject("\\le").scale(2)
        big_plus = TexMobject("+").scale(2)
        big_le.move_to(2.75*LEFT)
        big_plus.move_to(2.25*RIGHT)

        groups = VGroup(*[
            VGroup(
                m2.copy(), m1.copy(),
                VGroup(*self.circles).copy()
            )
            for m1, m2 in [(C0, A1_yellow_copy), (C0, B1), (B0, A1)]
        ])
        for group, vect in zip(groups[1:], [UP, 5*RIGHT+UP]):
            group.scale_in_place(0.5)
            group.shift(vect)
            group.save_state()
            group.shift(-vect[0]*RIGHT + 5*LEFT)
        inequality.shift(2.25*DOWN + 0.25*LEFT)

        self.in_B_out_C_words.restore()
        self.in_B_out_C_words.move_to(2*UP)
        self.in_A_out_B_words.restore()
        self.in_A_out_B_words.move_to(5*RIGHT+2*UP)

        self.clear()
        self.play(
            groups[0].scale_in_place, 0.5,
            groups[0].shift, 5*LEFT + UP,
            Write(inequality[0], run_time = 1),
            FadeIn(big_le),
        )
        self.wait()
        self.play(FadeIn(groups[1]))
        self.play(
            groups[1].restore, 
            FadeIn(inequality[1]),
            FadeIn(self.in_B_out_C_words),
            FadeIn(big_plus),
        )
        self.play(FadeIn(groups[2]))
        self.play(
            groups[2].restore,
            FadeIn(inequality[2]),
            FadeIn(self.in_A_out_B_words),
        )
        self.wait(2)

        self.groups = groups
        self.inequality = inequality

    def emphasize_containment(self):
        groups = self.groups
        c1, c2 = [VGroup(*group[:2]).copy() for group in groups[1:]]
        foreground = VGroup(groups[0][-1], *groups[1:])

        rect = SurroundingRectangle(groups[0])

        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))
        self.play(
            ApplyMethod(
                c1.shift, 4*LEFT,
                path_arc = -np.pi/2,
            ),
            Animation(foreground)
        )
        self.play(
            ApplyMethod(
                c2.shift, 8*LEFT,
                path_arc = -np.pi/2,
            ),
            Animation(c1),
            Animation(foreground),
            run_time = 1.5
        )
        self.play(
            FadeOut(c2),
            FadeOut(c1),
            Animation(foreground),
            run_time = 2
        )
        self.wait()

    def write_50_percent(self):
        words = TextMobject(
            "Should be 50\\% \\\\ of circle ", "A",
            "...somehow"
        )
        words.scale(0.7)
        words.set_color_by_tex("A", RED)
        words.move_to(5*LEFT + 2*UP)

        self.play(Write(words))
        self.wait()

    def write_assumption(self):
        words = TextMobject("Assume circles have the same size$^*$")
        words.scale(0.8)
        words.to_edge(UP)

        footnote = TextMobject("""
            *If you prefer, you can avoid the need for that 
            assumption by swapping the roles of A and C here 
            and writing a second inequality for added constraint.
        """)
        footnote.scale(0.5)
        footnote.to_corner(DOWN+RIGHT)
        footnote.add(words[-1])
        words.remove(words[-1])

        self.footnote = footnote

        self.play(FadeIn(words))

    def adjust_circles(self):
        groups = self.groups
        A_group = VGroup(
            groups[0][0],
            groups[2][0],
            groups[0][2][0],
            groups[1][2][0],
            groups[2][2][0],
        )
        B_group = VGroup(
            groups[1][0],
            groups[2][1],
            groups[0][2][1],
            groups[1][2][1],
            groups[2][2][1],
        )
        C_group = VGroup(
            groups[0][1],
            groups[1][1],
            groups[0][2][2],
            groups[1][2][2],
            groups[2][2][2],
        )

        def center_of_mass(mob):
            return np.apply_along_axis(np.mean, 0, mob.points)

        movers = [A_group, B_group, C_group]
        A_ref, B_ref, C_ref = [g[4] for g in movers]
        B_center = center_of_mass(B_ref)
        B_to_A = center_of_mass(A_ref) - B_center
        B_to_C = center_of_mass(C_ref) - B_center

        A_freq = 1
        C_freq = -0.7

        self.time = 0
        dt = 1 / self.camera.frame_rate

        def move_around(total_time):
            self.time
            t_range = list(range(int(total_time/dt)))
            for x in ProgressDisplay(t_range):
                self.time += dt
                new_B_to_A = rotate_vector(B_to_A, self.time*A_freq)
                new_B_to_C = rotate_vector(B_to_C, self.time*C_freq)
                A_group.shift(B_center + new_B_to_A - center_of_mass(A_ref))
                C_group.shift(B_center + new_B_to_C - center_of_mass(C_ref))
                self.wait(dt)

        move_around(3)
        self.add(self.footnote)
        move_around(1)
        self.remove(self.footnote)
        move_around(15)

class NoFirstMeasurementPreferenceBasedOnDirection(ShowVariousFilterPairs):
    CONFIG = {
        "filter_x_coordinates" : [0, 0, 0],
        "pol_filter_configs" : [
            {"filter_angle" : angle}
            for angle in (0, np.pi/8, np.pi/4)
        ],
        "lines_depth" : 1.2,
        "lines_shift_vect" : SMALL_BUFF*OUT,
        "n_lines" : 30,
    }
    def setup(self):
        DirectionOfPolarization.setup(self)
        self.remove(self.axes, self.em_wave)
        zs = [2.5, 0, -2.5]
        chars = "ABC"
        colors = [RED, GREEN, BLUE]
        for z, char, color, pf in zip(zs, chars, colors, self.pol_filters):
            pf.scale_in_place(0.7)
            pf.move_to(z*OUT)
            label = TextMobject(char)
            label.add_background_rectangle()
            label.set_color(color)
            label.scale(0.7)
            label.rotate(np.pi/2, RIGHT)
            label.rotate(-np.pi/2, OUT)
            label.next_to(pf.arrow_label, UP, SMALL_BUFF)
            pf.arrow_label.add(label)

            self.add_foreground_mobject(pf)

    def construct(self):
        self.reposition_camera()
        self.show_lines()

    def reposition_camera(self):
        words = TextMobject("No statistical preference")
        words.to_corner(UP+LEFT)
        words.rotate(np.pi/2, RIGHT)
        self.move_camera(
            theta = -0.6*np.pi,
            added_anims = list(it.chain(*[
                [
                    pf.arrow_label.rotate, np.pi/2, OUT,
                    pf.arrow_label.next_to, pf.arrow, OUT+RIGHT, SMALL_BUFF
                ]
                for pf in self.pol_filters
            ] + [[FadeIn(words)]]))
        )

    def show_lines(self):
        all_pre_lines = VGroup()
        all_post_lines = VGroup()
        for pf in self.pol_filters:
            pre_lines = self.get_lines(None, pf)
            post_lines = self.get_lines(pf, None)
            VGroup(
                *random.sample(post_lines, self.n_lines/2)
            ).set_stroke(BLACK, 0)
            all_pre_lines.add(*pre_lines)
            all_post_lines.add(*post_lines)

        kwargs = {
            "rate_func" : None,
            "lag_ratio" : 0
        }
        self.play(ShowCreation(all_pre_lines, **kwargs))
        self.play(
            ShowCreation(all_post_lines, **kwargs),
            Animation(self.pol_filters),
            Animation(all_pre_lines),
        )
        self.add_foreground_mobject(all_pre_lines)
        self.wait(7)
