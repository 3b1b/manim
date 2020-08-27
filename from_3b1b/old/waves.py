from manimlib.imports import *


import warnings
warnings.warn("""
    Warning: This file makes use of
    ContinualAnimation, which has since
    been deprecated
""")


E_COLOR = BLUE
M_COLOR = YELLOW


# Warning, much of what is below was implemented using
# ConintualAnimation, which has now been deprecated.  One
# Should use Mobject updaters instead.
# 
# That is, anything below implemented as a ContinualAnimation
# should instead be a Mobject, where the update methods
# should be added via Mobject.add_udpater.


class OscillatingVector(ContinualAnimation):
    CONFIG = {
        "tail" : ORIGIN,
        "frequency" : 1,
        "A_vect" : [1, 0, 0],
        "phi_vect" : [0, 0, 0],
        "vector_to_be_added_to" : None,
    }
    def setup(self):
        self.vector = self.mobject

    def update_mobject(self, dt):
        f = self.frequency
        t = self.internal_time
        angle = 2*np.pi*f*t
        vect = np.array([
            A*np.exp(complex(0, angle + phi))
            for A, phi in zip(self.A_vect, self.phi_vect)
        ]).real
        self.update_tail()
        self.vector.put_start_and_end_on(self.tail, self.tail+vect)

    def update_tail(self):
        if self.vector_to_be_added_to is not None:
            self.tail = self.vector_to_be_added_to.get_end()

class OscillatingVectorComponents(ContinualAnimationGroup):
    CONFIG = {
        "tip_to_tail" : False,
    }
    def __init__(self, oscillating_vector, **kwargs):
        digest_config(self, kwargs)
        vx = Vector(UP, color = GREEN).fade()
        vy = Vector(UP, color = RED).fade()
        kwargs = {
            "frequency" : oscillating_vector.frequency,
            "tail" : oscillating_vector.tail,
        }
        ovx = OscillatingVector(
            vx,
            A_x = oscillating_vector.A_x,
            phi_x = oscillating_vector.phi_x,
            A_y = 0,
            phi_y = 0,
            **kwargs
        )
        ovy = OscillatingVector(
            vy,
            A_x = 0,
            phi_x = 0,
            A_y = oscillating_vector.A_y,
            phi_y = oscillating_vector.phi_y,
            **kwargs
        )
        components = [ovx, ovy]
        self.vectors = VGroup(ovx.vector, ovy.vector)
        if self.tip_to_tail:
            ovy.vector_to_be_added_to = ovx.vector
        else:
            self.lines = VGroup()
            for ov1, ov2 in (ovx, ovy), (ovy, ovx):
                ov_line = ov1.copy()
                ov_line.mobject = ov_line.vector = DashedLine(
                    UP, DOWN, color = ov1.vector.get_color()
                )
                ov_line.vector_to_be_added_to = ov2.vector
                components.append(ov_line)
                self.lines.add(ov_line.line)

        ContinualAnimationGroup.__init__(self, *components, **kwargs)

class EMWave(ContinualAnimationGroup):
    CONFIG = {
        "wave_number" : 1,
        "frequency" : 0.25,
        "n_vectors" : 40,
        "propogation_direction" : RIGHT,
        "start_point" : FRAME_X_RADIUS*LEFT + DOWN + OUT,
        "length" : FRAME_WIDTH,
        "amplitude" : 1,
        "rotation" : 0,
        "A_vect" : [0, 0, 1],
        "phi_vect" : [0, 0, 0],
        "requires_start_up" : False,
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        if not all(self.propogation_direction == RIGHT):
            self.matrix_transform = np.dot(
                z_to_vector(self.propogation_direction),
                np.linalg.inv(z_to_vector(RIGHT)),
            )
        else:
            self.matrix_transform = None

        vector_oscillations = []
        self.E_vects = VGroup()
        self.M_vects = VGroup()

        self.A_vect = np.array(self.A_vect)/get_norm(self.A_vect)
        self.A_vect *= self.amplitude

        for alpha in np.linspace(0, 1, self.n_vectors):
            tail = interpolate(ORIGIN, self.length*RIGHT, alpha)
            phase = -alpha*self.length*self.wave_number
            kwargs = {
                "phi_vect" : np.array(self.phi_vect) + phase,
                "frequency" : self.frequency,
                "tail" : np.array(tail),
            }
            E_ov = OscillatingVector(
                Vector(
                    OUT, color = E_COLOR,
                    normal_vector = UP,
                ),
                A_vect = self.A_vect,
                **kwargs
            )
            M_ov = OscillatingVector(
                Vector(
                    UP, color = M_COLOR,
                    normal_vector = OUT,
                ),
                A_vect = rotate_vector(self.A_vect, np.pi/2, RIGHT),
                **kwargs
            )
            vector_oscillations += [E_ov, M_ov]
            self.E_vects.add(E_ov.vector)
            self.M_vects.add(M_ov.vector)
        ContinualAnimationGroup.__init__(self, *vector_oscillations)

    def update_mobject(self, dt):
        if self.requires_start_up:
            n_wave_lengths = self.length / (2*np.pi*self.wave_number)
            prop_time = n_wave_lengths/self.frequency
            middle_alpha = interpolate(
                0.4, 1.4,
                self.external_time / prop_time
            )
            new_smooth = squish_rate_func(smooth, 0.4, 0.6)

            ovs = self.continual_animations
            for ov, alpha in zip(ovs, np.linspace(0, 1, len(ovs))):
                epsilon = 0.0001
                new_amplitude = np.clip(
                    new_smooth(middle_alpha - alpha), epsilon, 1
                )
                norm = get_norm(ov.A_vect)
                if norm != 0:
                    ov.A_vect = new_amplitude * np.array(ov.A_vect) / norm

        ContinualAnimationGroup.update_mobject(self, dt)
        self.mobject.rotate(self.rotation, RIGHT)
        if self.matrix_transform:
            self.mobject.apply_matrix(self.matrix_transform)
        self.mobject.shift(self.start_point)

class WavePacket(Animation):
    CONFIG = {
        "EMWave_config" : {
            "wave_number" : 0,
            "start_point" : FRAME_X_RADIUS*LEFT,
            "phi_vect" : np.ones(3)*np.pi/4,
        },
        "em_wave" : None,
        "run_time" : 4,
        "rate_func" : None,
        "packet_width" : 6,
        "include_E_vects" : True,
        "include_M_vects" : True,
        "filter_distance" : FRAME_X_RADIUS,
        "get_filtered" : False,
        "remover" : True,
        "width" : 2*np.pi,
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        em_wave = self.em_wave
        if em_wave is None:
            em_wave = EMWave(**self.EMWave_config)
            em_wave.update(0)
            self.em_wave = em_wave

        self.vects = VGroup()
        if self.include_E_vects:
            self.vects.add(*em_wave.E_vects)
        if self.include_M_vects:
            self.vects.add(*em_wave.M_vects)
        for vect in self.vects:
            vect.save_state()

        u = em_wave.propogation_direction
        self.wave_packet_start, self.wave_packet_end = [
            em_wave.start_point - u*self.packet_width/2,
            em_wave.start_point + u*(em_wave.length + self.packet_width/2)
        ]
        Animation.__init__(self, self.vects, **kwargs)

    def interpolate_mobject(self, alpha):
        packet_center = interpolate(
            self.wave_packet_start,
            self.wave_packet_end,
            alpha
        )
        em_wave = self.em_wave
        for vect in self.vects:
            tail = vect.get_start()
            distance_from_packet = np.dot(
                tail - packet_center,
                em_wave.propogation_direction
            )
            A = em_wave.amplitude*self.E_func(distance_from_packet)
            distance_from_start = get_norm(tail - em_wave.start_point)
            if self.get_filtered and distance_from_start > self.filter_distance:
                A = 0
            epsilon = 0.05
            if abs(A) < epsilon:
                A = 0
            vect.restore()
            vect.scale(A/vect.get_length(), about_point = tail)

    def E_func(self, x):
        x0 = 2*np.pi*x/self.width
        return np.sin(x0)*np.exp(-0.25*x0*x0)

class FilterLabel(TexMobject):
    def __init__(self, tex, degrees, **kwargs):
        TexMobject.__init__(self, tex + " \\uparrow", **kwargs)
        self[-1].rotate(-degrees * np.pi / 180)

class PolarizingFilter(Circle):
    CONFIG = {
        "stroke_color" : DARK_GREY,
        "fill_color" : LIGHT_GREY,
        "fill_opacity" : 0.5,
        "label_tex" : None,
        "filter_angle" : 0,
        "include_arrow_label" : True,
        "arrow_length" : 0.7,
    }
    def __init__(self, **kwargs):
        Circle.__init__(self, **kwargs)

        if self.label_tex:
            self.label = TexMobject(self.label_tex)
            self.label.next_to(self.get_top(), DOWN, MED_SMALL_BUFF)
            self.add(self.label)

        arrow = Arrow(
            ORIGIN, self.arrow_length*UP, 
            color = WHITE,
            buff = 0,
        )
        arrow.shift(self.get_top())
        arrow.rotate(-self.filter_angle)
        self.add(arrow)
        self.arrow = arrow
        shade_in_3d(self)

        if self.include_arrow_label:
            arrow_label = TexMobject(
                "%.1f^\\circ"%(self.filter_angle*180/np.pi)
            )
            arrow_label.add_background_rectangle()
            arrow_label.next_to(arrow.get_tip(), UP)
            self.add(arrow_label)
            self.arrow_label = arrow_label

################

class FilterScene(ThreeDScene):
    CONFIG = {
        "filter_x_coordinates" : [0],
        "pol_filter_configs" : [{}],
        "EMWave_config" : {
            "start_point" : FRAME_X_RADIUS*LEFT + DOWN+OUT
        },
        "axes_config" : {},
        "start_phi" : 0.8*np.pi/2,
        "start_theta" : -0.6*np.pi,
        "ambient_rotation_rate" : 0.01,
    }
    def setup(self):
        self.axes = ThreeDAxes(**self.axes_config)
        self.add(self.axes)
        for x in range(len(self.filter_x_coordinates) - len(self.pol_filter_configs)):
            self.pol_filter_configs.append({})
        self.pol_filters = VGroup(*[
            PolarizingFilter(**config)
            for config in self.pol_filter_configs
        ])
        self.pol_filters.rotate(np.pi/2, RIGHT)
        self.pol_filters.rotate(-np.pi/2, OUT)
        pol_filter_shift = np.array(self.EMWave_config["start_point"])
        pol_filter_shift[0] = 0
        self.pol_filters.shift(pol_filter_shift)
        for x, pf in zip(self.filter_x_coordinates, self.pol_filters):
            pf.shift(x*RIGHT)
        self.add(self.pol_filters)
        self.pol_filter = self.pol_filters[0]

        self.set_camera_orientation(self.start_phi, self.start_theta)
        if self.ambient_rotation_rate > 0:
            self.begin_ambient_camera_rotation(self.ambient_rotation_rate)

    def get_filter_absorption_animation(self, pol_filter, photon):
        x = pol_filter.get_center()[0]
        alpha = (x + FRAME_X_RADIUS) / (FRAME_WIDTH)
        return ApplyMethod(
            pol_filter.set_fill, RED,
            run_time = photon.run_time,
            rate_func = squish_rate_func(there_and_back, alpha - 0.1, alpha + 0.1)
        )

class DirectionOfPolarizationScene(FilterScene):
    CONFIG = {
        "pol_filter_configs" : [{
            "include_arrow_label" : False,
        }],
        "target_theta" : -0.97*np.pi,
        "target_phi" : 0.9*np.pi/2,
        "ambient_rotation_rate" : 0.005,
        "apply_filter" : False,
        "quantum" : False,
    }
    def setup(self):
        self.reference_line = Line(ORIGIN, RIGHT)
        self.reference_line.set_stroke(width = 0)
        self.em_wave = EMWave(**self.EMWave_config)
        self.add(self.em_wave)

        FilterScene.setup(self)

    def change_polarization_direction(self, angle, **kwargs):
        added_anims = kwargs.get("added_anims", [])
        self.play(
            ApplyMethod(
                self.reference_line.rotate, angle,
                **kwargs
            ),
            *added_anims
        )

    def setup_rectangles(self):
        rect1 = Rectangle(
            height = 2*self.em_wave.amplitude,
            width = FRAME_X_RADIUS + 0.25,
            stroke_color = BLUE,
            fill_color = BLUE,
            fill_opacity = 0.2,
        )
        rect1.rotate(np.pi/2, RIGHT)
        pf_copy = self.pol_filter.deepcopy()
        pf_copy.remove(pf_copy.arrow)
        center = pf_copy.get_center()
        rect1.move_to(center, RIGHT)
        rect2 = rect1.copy()
        rect2.move_to(center, LEFT)

        self.rectangles = VGroup(rect1, rect2)

    def update_mobjects(self, *args, **kwargs):
        reference_angle = self.reference_line.get_angle()
        self.em_wave.rotation = reference_angle
        FilterScene.update_mobjects(self, *args, **kwargs)
        if self.apply_filter:
            self.apply_filters()
        self.update_rectangles()

    def apply_filters(self):
        vect_groups = [self.em_wave.E_vects, self.em_wave.M_vects]
        filters = sorted(
            self.pol_filters,
            lambda pf1, pf2 : cmp(
                pf1.get_center()[0], 
                pf2.get_center()[0],
            )
        )
        for pol_filter in filters:
            filter_x = pol_filter.arrow.get_center()[0]
            for vect_group, angle in zip(vect_groups, [0, -np.pi/2]):
                target_angle = pol_filter.filter_angle + angle
                for vect_mob in vect_group:
                    vect = vect_mob.get_vector()
                    vect_angle = angle_of_vector([
                        vect[2], -vect[1]
                    ])
                    angle_diff = target_angle - vect_angle
                    angle_diff = (angle_diff+np.pi/2)%np.pi - np.pi/2
                    start, end = vect_mob.get_start_and_end()
                    if start[0] > filter_x:
                        vect_mob.rotate(angle_diff, RIGHT)
                        if not self.quantum:
                            vect_mob.scale(
                                np.cos(angle_diff),
                                about_point = start,
                            )

    def update_rectangles(self):
        if not hasattr(self, "rectangles") or self.rectangles not in self.mobjects:
            return

        r1, r2 = self.rectangles

        target_angle = self.reference_line.get_angle()
        anchors = r1.get_anchors()
        vect = anchors[0] - anchors[3]
        curr_angle = angle_of_vector([vect[2], -vect[1]])
        r1.rotate_in_place(target_angle - curr_angle, RIGHT)

        epsilon = 0.001
        curr_depth = max(r2.get_depth(), epsilon)
        target_depth = max(
            2*self.em_wave.amplitude*abs(np.cos(target_angle)),
            epsilon
        )
        r2.stretch_in_place(target_depth/curr_depth, 2)

################

class WantToLearnQM(TeacherStudentsScene):
    def construct(self):
        question1 = TexMobject(
            "\\text{What does }\\qquad \\\\", 
            "|\\!\\psi \\rangle", "=",
            "\\frac{1}{\\sqrt{2}}", "|\\!\\uparrow \\rangle", "+",
            "\\frac{1}{\\sqrt{2}}", "|\\!\\downarrow \\rangle \\\\",
            "\\text{mean?}\\qquad\\quad"
        )
        question1.set_color_by_tex_to_color_map({
            "psi" : BLUE,
            "uparrow" : GREEN,
            "downarrow" : RED,
        })
        question2 = TextMobject(
            "Why are complex \\\\ numbers involved?"
        )
        question3 = TextMobject(
            "How do you compute \\\\ quantum probabilities?"
        )
        questions = [question1, question2, question3]
        bubbles = VGroup()

        for i, question in zip([1, 2, 0], questions):
            self.student_says(
                question, 
                content_introduction_kwargs = {"run_time" : 2},
                student_index = i,
                bubble_kwargs = {"fill_opacity" : 1},
                bubble_creation_class = FadeIn,
            )
            bubble = self.students[i].bubble
            bubble.add(bubble.content)
            bubbles.add(bubble)
            self.students
            self.students[i].bubble = None
        self.wait(2)
        self.teacher_says(
            "First, lots and lots \\\\ of linear algebra",
            added_anims = list(map(FadeOut, bubbles))
        )
        self.wait()

class Goal(PiCreatureScene):
    def construct(self):
        randy = self.pi_creature

        goal = TextMobject("Goal: ")
        goal.set_color(YELLOW)
        goal.shift(FRAME_X_RADIUS*LEFT/2 + UP)
        weirdness = TextMobject("Eye-catching quantum weirdness")
        weirdness.next_to(goal, RIGHT)
        cross = Cross(weirdness)
        foundations = TextMobject("Foundational intuitions")
        foundations.next_to(goal, RIGHT)

        goal.save_state()
        goal.scale(0.01)
        goal.move_to(randy.get_right())

        self.play(
            goal.restore,
            randy.change, "raise_right_hand"
        )
        self.play(Write(weirdness, run_time = 2))
        self.play(
            ShowCreation(cross),
            randy.change, "sassy"
        )
        self.wait()
        self.play(
            VGroup(weirdness, cross).shift, DOWN,
            Write(foundations, run_time = 2),
            randy.change, "happy"
        )
        self.wait(2)


    ####

    def create_pi_creature(self):
        return Randolph().to_corner(DOWN+LEFT)

class AskWhatsDifferentInQM(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "What's different in \\\\ quantum mechanics?"
        )
        self.play(self.teacher.change, "pondering")
        self.wait(3)

class VideoWrapper(Scene):
    CONFIG = {
        "title" : ""
    }
    def construct(self):
        title = TextMobject(self.title)
        title.to_edge(UP)
        self.add(title)
        rect = ScreenRectangle()
        rect.set_height(6)
        rect.next_to(title, DOWN)
        self.add(rect)
        self.wait()

class BellsWrapper(VideoWrapper):
    CONFIG = {
        "title" : "Bell's inequalities"
    }

class FromOtherVideoWrapper(VideoWrapper):
    CONFIG = {
        "title" : "See the other video..."
    }

class OriginOfQuantumMechanicsWrapper(VideoWrapper):
    CONFIG = {
        "title" : "The origin of quantum mechanics"
    }

class IntroduceElectricField(PiCreatureScene):
    CONFIG = {
        "vector_field_colors" : [BLUE_B, BLUE_D],
        "max_vector_length" : 0.9,
    }
    def construct(self):
        self.write_title()
        self.draw_field()
        self.add_particle()
        self.let_particle_wander()

    def write_title(self):
        morty = self.pi_creature

        title = TextMobject(
            "Electro", "magnetic", " field",
            arg_separator = ""
        )
        title.next_to(morty, UP+LEFT)
        electric = TextMobject("Electric")
        electric.next_to(title[-1], LEFT)
        electric.set_color(BLUE)

        title.save_state()
        title.shift(DOWN)
        title.fade(1)

        self.play(
            title.restore,
            morty.change, "raise_right_hand",
        )
        self.play(
            title[0].set_color, BLUE,
            title[1].set_color, YELLOW,
        )
        self.wait()
        self.play(
            ShrinkToCenter(title[1]),
            Transform(title[0], electric)
        )

        title.add_background_rectangle()
        self.title = title

    def draw_field(self):
        morty = self.pi_creature
        vector_field = self.get_vector_field()
        self.play(
            LaggedStartMap(
                ShowCreation, vector_field, 
                run_time = 3
            ),
            self.title.center,
            self.title.scale, 1.5,
            self.title.to_edge, UP,
            morty.change, "happy", ORIGIN,
        )
        self.wait()

        self.vector_field = vector_field

    def add_particle(self):
        morty = self.pi_creature
        point = UP+LEFT + SMALL_BUFF*(UP+RIGHT)
        particle = self.get_particle()
        particle.move_to(point)

        vector = self.get_vector(particle.get_center())
        vector.set_color(RED)
        vector.scale(1.5, about_point = point)
        vector.shift(SMALL_BUFF*vector.get_vector())
        force = TextMobject("Force")
        force.next_to(ORIGIN, UP+RIGHT, SMALL_BUFF)
        force.rotate(vector.get_angle())
        force.shift(vector.get_start())

        particle.save_state()
        particle.move_to(morty.get_left() + 0.5*UP + 0.2*RIGHT)
        particle.fade(1)

        self.play(
            particle.restore,
            morty.change, "raise_right_hand",
        )
        self.play(morty.change, "thinking", particle)
        self.play(
            ShowCreation(vector),
            Write(force, run_time = 1),
        )
        self.wait(2)

        self.particle = particle
        self.force_vector = VGroup(vector, force)

    def let_particle_wander(self):
        possible_points = [v.get_start() for v in self.vector_field]
        points = random.sample(possible_points, 45)
        points.append(3*UP+3*LEFT)
        particles = VGroup(self.particle, *[
            self.particle.copy().move_to(point)
            for point in points
        ])
        for particle in particles:
            particle.velocity = np.zeros(3)

        self.play(
            FadeOut(self.force_vector),
            LaggedStartMap(FadeIn, VGroup(*particles[1:]))
        )
        self.moving_particles = particles
        self.add_foreground_mobjects(self.moving_particles, self.pi_creature)
        self.always_update_mobjects = True
        self.wait(10)

    ###

    def update_mobjects(self, *args, **kwargs):
        Scene.update_mobjects(self, *args, **kwargs)
        if hasattr(self, "moving_particles"):
            dt = self.frame_duration
            for p in self.moving_particles:
                vect = self.field_function(p.get_center())
                p.velocity += vect*dt
                p.shift(p.velocity*dt)
            self.pi_creature.look_at(self.moving_particles[-1])

    def get_particle(self):
        particle = Circle(radius = 0.2)
        particle.set_stroke(RED, 3)
        particle.set_fill(RED, 0.5)
        plus = TexMobject("+")
        plus.scale(0.7)
        plus.move_to(particle)
        particle.add(plus)
        return particle

    def get_vector_field(self):
        result = VGroup(*[
            self.get_vector(point)
            for x in np.arange(-9, 9)
            for y in np.arange(-5, 5)
            for point in [x*RIGHT + y*UP]
        ])
        shading_list = list(result)
        shading_list.sort(
            key=lambda m: m1.get_length()
        )
        VGroup(*shading_list).set_color_by_gradient(*self.vector_field_colors)
        result.set_fill(opacity = 0.75)
        result.sort(get_norm)

        return result

    def get_vector(self, point):
        return Vector(self.field_function(point)).shift(point)

    def field_function(self, point):
        x, y = point[:2]
        result = y*RIGHT + np.sin(x)*UP
        return self.normalized(result)

    def normalized(self, vector):
        norm = get_norm(vector) or 1
        target_length = self.max_vector_length * sigmoid(0.1*norm)
        return target_length * vector/norm

class IntroduceMagneticField(IntroduceElectricField, ThreeDScene):
    CONFIG = {
        "vector_field_colors" : [YELLOW_C, YELLOW_D]
    }
    def setup(self):
        IntroduceElectricField.setup(self)
        self.remove(self.pi_creature)

    def construct(self):
        self.set_camera_orientation(0.1, -np.pi/2)
        self.add_title()
        self.add_vector_field()
        self.introduce_moving_charge()
        self.show_force()
        # self.many_charges()

    def add_title(self):
        title = TextMobject("Magnetic", "field")
        title[0].set_color(YELLOW)
        title.scale(1.5)
        title.to_edge(UP)
        title.add_background_rectangle()

        self.add(title)
        self.title = title

    def add_vector_field(self):
        vector_field = self.get_vector_field()

        self.play(
            LaggedStartMap(ShowCreation, vector_field, run_time = 3),
            Animation(self.title)
        )
        self.wait()

    def introduce_moving_charge(self):
        point = 3*RIGHT + UP
        particle = self.get_particle()
        particle.move_to(point)

        velocity = Vector(2*RIGHT).shift(particle.get_right())
        velocity.set_color(WHITE)
        velocity_word = TextMobject("Velocity")
        velocity_word.set_color(velocity.get_color())
        velocity_word.add_background_rectangle()
        velocity_word.next_to(velocity, UP, 0, LEFT)

        M_vect = self.get_vector(point)
        M_vect.set_color(YELLOW)
        M_vect.shift(SMALL_BUFF*M_vect.get_vector())

        particle.save_state()
        particle.shift(FRAME_WIDTH*LEFT)

        self.play(
            particle.restore,
            run_time = 2,
            rate_func=linear,
        )
        self.add(velocity)
        self.play(Write(velocity_word, run_time = 0.5))
        # self.play(ShowCreation(M_vect))
        self.wait()

        self.particle = particle

    def show_force(self):
        point = self.particle.get_center()
        F_vect = Vector(
            3*np.cross(self.field_function(point), RIGHT),
            color = GREEN
        )
        F_vect.shift(point)
        F_word = TextMobject("Force")
        F_word.rotate(np.pi/2, RIGHT)
        F_word.next_to(F_vect, OUT)
        F_word.set_color(F_vect.get_color())
        F_eq = TexMobject(
            "=","q", "\\textbf{v}", "\\times", "\\textbf{B}"
        )
        F_eq.set_color_by_tex_to_color_map({
            "q" : RED,
            "B" : YELLOW,
        })
        F_eq.rotate(np.pi/2, RIGHT)
        F_eq.next_to(F_word, RIGHT)


        self.move_camera(0.8*np.pi/2, -0.55*np.pi)
        self.begin_ambient_camera_rotation()
        self.play(ShowCreation(F_vect))
        self.play(Write(F_word))
        self.wait()
        self.play(Write(F_eq))
        self.wait(8)

    def many_charges(self):
        charges = VGroup()
        for y in range(2, 3):
            charge = self.get_particle()
            charge.move_to(3*LEFT + y*UP)
            charge.velocity = (2*RIGHT).astype('float')
            charges.add(charge)

        self.revert_to_original_skipping_status()
        self.add_foreground_mobjects(*charges)
        self.moving_particles = charges
        self.wait(5)

        
    ###

    def update_mobjects(self, *args, **kwargs):
        Scene.update_mobjects(self, *args, **kwargs)
        if hasattr(self, "moving_particles"):
            dt = self.frame_duration
            for p in self.moving_particles:
                M_vect = self.field_function(p.get_center())
                F_vect = 3*np.cross(p.velocity, M_vect)
                p.velocity += F_vect*dt
                p.shift(p.velocity*dt)

    def field_function(self, point):
        x, y = point[:2]
        y += 0.5
        gauss = lambda r : np.exp(-0.5*r**2)
        result = (y**2 - 1)*RIGHT + x*(gauss(y+2) - gauss(y-2))*UP
        return self.normalized(result)

class CurlRelationBetweenFields(ThreeDScene):
    def construct(self):
        self.add_axes()
        self.loop_in_E()
        self.loop_in_M()
        self.second_loop_in_E()

    def add_axes(self):
        self.add(ThreeDAxes(x_axis_radius = FRAME_X_RADIUS))

    def loop_in_E(self):
        E_vects = VGroup(*[
            Vector(0.5*rotate_vector(vect, np.pi/2)).shift(vect)
            for vect in compass_directions(8)
        ])
        E_vects.set_color(E_COLOR)
        point = 1.2*RIGHT + 2*UP + OUT
        E_vects.shift(point)

        M_vect = Vector(
            IN, 
            normal_vector = DOWN,
            color = M_COLOR
        )
        M_vect.shift(point)
        M_vect.save_state()
        M_vect.scale(0.01, about_point = M_vect.get_start())

        self.play(ShowCreation(E_vects, run_time = 2))
        self.wait()
        self.move_camera(0.8*np.pi/2, -0.45*np.pi)
        self.begin_ambient_camera_rotation()
        self.play(M_vect.restore, run_time = 3, rate_func=linear)
        self.wait(3)

        self.E_vects = E_vects
        self.E_circle_center = point
        self.M_vect = M_vect

    def loop_in_M(self):
        M_vects = VGroup(*[
            Vector(
                rotate_vector(vect, np.pi/2),
                normal_vector = IN,
                color = M_COLOR
            ).shift(vect)
            for vect in compass_directions(8, LEFT)[1:]
        ])
        M_vects.rotate(np.pi/2, RIGHT)
        new_point = self.E_circle_center + RIGHT
        M_vects.shift(new_point)

        E_vect = self.E_vects[0]

        self.play(
            ShowCreation(M_vects, run_time = 2),
            *list(map(FadeOut, self.E_vects[1:]))
        )
        self.wait()
        self.play(
            E_vect.rotate, np.pi, RIGHT, [], new_point,
            E_vect.scale_about_point, 3, new_point,
            run_time = 4,
            rate_func=linear,
        )
        self.wait()

        self.M_circle_center = new_point
        M_vects.add(self.M_vect)
        self.M_vects = M_vects
        self.E_vect = E_vect

    def second_loop_in_E(self):
        E_vects = VGroup(*[
            Vector(1.5*rotate_vector(vect, np.pi/2)).shift(vect)
            for vect in compass_directions(8, LEFT)[1:]
        ])
        E_vects.set_color(E_COLOR)
        point = self.M_circle_center + RIGHT
        E_vects.shift(point)

        M_vect = self.M_vects[3]
        self.M_vects.remove(M_vect)

        self.play(FadeOut(self.M_vects))
        self.play(ShowCreation(E_vects), Animation(M_vect))
        self.play(
            M_vect.rotate, np.pi, RIGHT, [], point,
            run_time = 5,
            rate_func=linear,
        )
        self.wait(3)

class WriteCurlEquations(Scene):
    def construct(self):
        eq1 = TexMobject(
            "\\nabla \\times", "\\textbf{E}", "=",
            "-\\frac{1}{c}", 
            "\\frac{\\partial \\textbf{B}}{\\partial t}"
        )
        eq2 = TexMobject(
            "\\nabla \\times", "\\textbf{B}", "=^*",
            "\\frac{1}{c}", 
            "\\frac{\\partial \\textbf{E}}{\\partial t}"
        )
        eqs = VGroup(eq1, eq2)
        eqs.arrange(DOWN, buff = LARGE_BUFF)
        eqs.set_height(FRAME_HEIGHT - 1)
        eqs.to_edge(LEFT)
        for eq in eqs:
            eq.set_color_by_tex_to_color_map({
                "E" : E_COLOR,            
                "B" : M_COLOR,
            })
        footnote = TextMobject("*Ignoring currents")
        footnote.next_to(eqs[1], RIGHT)
        footnote.to_edge(RIGHT)

        self.play(Write(eq1, run_time = 2))
        self.wait(3)
        self.play(Write(eq2, run_time = 2))
        self.play(FadeIn(footnote))
        self.wait(3)

class IntroduceEMWave(ThreeDScene):
    CONFIG = {
        "EMWave_config" : {
            "requires_start_up" : True
        }
    }
    def setup(self):
        self.axes = ThreeDAxes()
        self.add(self.axes)
        self.em_wave = EMWave(**self.EMWave_config)
        self.add(self.em_wave)
        self.set_camera_orientation(0.8*np.pi/2, -0.7*np.pi)
        self.begin_ambient_camera_rotation()

    def construct(self):
        words = TextMobject(
            "Electro", "magnetic", " radiation",
            arg_separator = ""
        )
        words.set_color_by_tex_to_color_map({
            "Electro" : E_COLOR,
            "magnetic" : M_COLOR,
        })
        words.next_to(ORIGIN, LEFT, MED_LARGE_BUFF)
        words.to_edge(UP)
        words.rotate(np.pi/2, RIGHT)

        self.wait(7)
        self.play(Write(words, run_time = 2))
        self.wait(20)

    #####

class SimpleEMWave(IntroduceEMWave):
    def construct(self):
        self.wait(30)

class ListRelevantWaveIdeas(TeacherStudentsScene):
    def construct(self):
        title = TextMobject("Wave","topics")
        title.to_corner(UP + LEFT, LARGE_BUFF)
        title.set_color(BLUE)
        h_line = Line(title.get_left(), title.get_right())
        h_line.next_to(title, DOWN, SMALL_BUFF)

        topics = VGroup(*list(map(TextMobject, [
            "- Superposition",
            "- Amplitudes",
            "- How phase influences addition",
        ])))
        topics.scale(0.8)
        topics.arrange(DOWN, aligned_edge = LEFT)
        topics.next_to(h_line, DOWN, aligned_edge = LEFT)

        quantum = TextMobject("Quantum")
        quantum.set_color(GREEN)
        quantum.move_to(title[0], LEFT)

        wave_point = self.teacher.get_corner(UP+LEFT) + 2*UP
        self.play(
            Animation(VectorizedPoint(wave_point)),
            self.teacher.change, "raise_right_hand"
        )
        self.wait(2)
        self.play(
            Write(title, run_time = 2),
            ShowCreation(h_line)
        )
        self.change_student_modes(
            *["pondering"]*3,
            added_anims = [LaggedStartMap(
                FadeIn, topics,
                run_time = 3
            )],
            look_at_arg = title
        )
        self.play(
            Animation(title),
            self.teacher.change, "happy"
        )
        self.play(
            title[0].next_to, quantum.copy(), UP, MED_SMALL_BUFF, LEFT,
            title[0].fade, 0.5,
            title[1].next_to, quantum.copy(), RIGHT, 2*SMALL_BUFF,
            Write(quantum),
        )
        self.wait(5)

class DirectWaveOutOfScreen(IntroduceEMWave):
    CONFIG = {
        "EMWave_config" : {
            "requires_start_up" : False,
            "amplitude" : 2,
            "start_point" : FRAME_X_RADIUS*LEFT,
            "A_vect" : [0, 1, 0],
            "start_up_time" : 0,
        }
    }
    def setup(self):
        IntroduceEMWave.setup(self)
        self.remove(self.axes)
        for ov in self.em_wave.continual_animations:
            ov.vector.normal_vector = RIGHT
        self.set_camera_orientation(0.9*np.pi/2, -0.3*np.pi)

    def construct(self):
        self.move_into_position()
        self.fade_M_vects()
        self.fade_all_but_last_E_vects()

    def move_into_position(self):
        self.wait(2)
        self.update_mobjects()
        faded_vectors = VGroup(*[
            ov.vector
            for ov in self.em_wave.continual_animations[:-2]
        ])
        self.move_camera(
            0.99*np.pi/2, -0.01,
            run_time = 2,
            added_anims = [faded_vectors.set_fill, None, 0.5]
        )
        self.stop_ambient_camera_rotation()
        self.move_camera(
            np.pi/2, 0,
            added_anims = [faded_vectors.set_fill, None, 0.05],
            run_time = 2,
        )
        self.faded_vectors = faded_vectors

    def fade_M_vects(self):
        self.play(
            self.em_wave.M_vects.set_fill, None, 0
        )
        self.wait(2)

    def fade_all_but_last_E_vects(self):
        self.play(self.faded_vectors.set_fill, None, 0)
        self.wait(4)

class ShowVectorEquation(Scene):
    CONFIG = {
        "f_color" : RED,
        "phi_color" : MAROON_B,
        "A_color" : GREEN,
    }
    def construct(self):
        self.add_vector()
        self.add_plane()
        self.write_horizontally_polarized()
        self.write_components()
        self.show_graph()
        self.add_phi()
        self.add_amplitude()
        self.add_kets()
        self.switch_to_vertically_polarized_light()

    def add_vector(self):
        self.vector = Vector(2*RIGHT, color = E_COLOR)
        self.oscillating_vector = OscillatingVector(
            self.vector,
            A_vect = [2, 0, 0],
            frequency = 0.25,
        )
        self.add(self.oscillating_vector)
        self.wait(3)

    def add_plane(self):
        xy_plane = NumberPlane(
            axes_color = LIGHT_GREY,
            color = DARK_GREY,
            secondary_color = DARK_GREY,
            x_unit_size = 2,
            y_unit_size = 2,
        )
        xy_plane.add_coordinates()
        xy_plane.add(xy_plane.get_axis_labels())

        self.play(
            Write(xy_plane),
            Animation(self.vector)
        )
        self.wait(2)
        self.xy_plane = xy_plane

    def write_horizontally_polarized(self):
        words = TextMobject(
            "``", "Horizontally", " polarized", "''",
            arg_separator = ""
        )
        words.next_to(ORIGIN, LEFT)
        words.to_edge(UP)
        words.add_background_rectangle()

        self.play(Write(words, run_time = 3))
        self.wait()

        self.horizontally_polarized_words = words

    def write_components(self):
        x, y = components = VGroup(
            TexMobject("\\cos(", "2\\pi", "f_x", "t", "+ ", "\\phi_x", ")"),
            TexMobject("0", "")
        )
        components.arrange(DOWN)
        lb, rb = brackets = TexMobject("[]")
        brackets.set_height(components.get_height() + SMALL_BUFF)
        lb.next_to(components, LEFT, buff = 0.3)
        rb.next_to(components, RIGHT, buff = 0.3)
        E, equals = E_equals = TexMobject(
            "\\vec{\\textbf{E}}", "="
        )
        E.set_color(E_COLOR)
        E_equals.next_to(brackets, LEFT)
        E_equals.add_background_rectangle()
        brackets.add_background_rectangle()
        group = VGroup(E_equals, brackets, components)
        group.next_to(
            self.horizontally_polarized_words, 
            DOWN, MED_LARGE_BUFF, RIGHT
        )

        x_without_phi = TexMobject("\\cos(", "2\\pi", "f_x", "t", ")")
        x_without_phi.move_to(x)
        for mob in x, x_without_phi:
            mob.set_color_by_tex_to_color_map({
                "f_x" : self.f_color,
                "phi_x" : self.phi_color,
            })

        def update_brace(brace):
            brace.stretch_to_fit_width(
                max(self.vector.get_width(), 0.001)
            )
            brace.next_to(self.vector.get_center(), DOWN, SMALL_BUFF)
            return brace
        moving_brace = Mobject.add_updater(
            Brace(Line(LEFT, RIGHT), DOWN), update_brace
        )
        moving_x_without_phi = Mobject.add_updater(
            x_without_phi.copy().add_background_rectangle(),
            lambda m : m.next_to(moving_brace.mobject, DOWN, SMALL_BUFF)
        )

        self.play(Write(E_equals), Write(brackets))
        y.save_state()
        y.move_to(self.horizontally_polarized_words)
        y.set_fill(opacity = 0)
        self.play(y.restore)
        self.wait()
        self.add(moving_brace, moving_x_without_phi)
        self.play(
            FadeIn(moving_brace.mobject),
            FadeIn(x_without_phi),
            FadeIn(moving_x_without_phi.mobject),
            lag_ratio = 0.5,
            run_time = 2,
        )
        self.wait(3)
        self.play(
            FadeOut(moving_brace.mobject),
            FadeOut(moving_x_without_phi.mobject),
        )
        self.remove(moving_brace, moving_x_without_phi)

        self.E_equals = E_equals
        self.brackets = brackets
        self.x_without_phi = x_without_phi
        self.components = components

    def show_graph(self):
        axes = Axes(
            x_min = -0.5,
            x_max = 5.2,
            y_min = -1.5,
            y_max = 1.5,
        )
        axes.x_axis.add_numbers(*list(range(1, 6)))
        t = TexMobject("t")
        t.next_to(axes.x_axis, UP, SMALL_BUFF, RIGHT)
        cos = self.x_without_phi.copy()
        cos.next_to(axes.y_axis, RIGHT, SMALL_BUFF, UP)
        cos_arg = VGroup(*cos[1:-1])
        fx_equals_1 = TexMobject("f_x", "= 1")
        fx_equals_fourth = TexMobject("f_x", "= 0.25")
        fx_group = VGroup(fx_equals_1, fx_equals_fourth)
        for fx in fx_group:
            fx[0].set_color(self.f_color)
            fx.move_to(axes, UP+RIGHT)
        high_f_graph, low_f_graph = graphs = VGroup(*[
            FunctionGraph(
                lambda x : np.cos(2*np.pi*f*x),
                color = E_COLOR,
                x_min = 0,
                x_max = 4/f,
                num_steps = 20/f,
            )
            for f in (1, 0.25,)
        ])

        group = VGroup(axes, t, cos, high_f_graph, *fx_group)
        rect = SurroundingRectangle(
            group,
            buff = MED_LARGE_BUFF,
            stroke_color = WHITE,
            stroke_width = 3,
            fill_color = BLACK,
            fill_opacity = 0.9
        )
        group.add_to_back(rect)
        group.scale(0.8)
        group.to_corner(UP+RIGHT, buff = -SMALL_BUFF)
        group.remove(*it.chain(fx_group, graphs))
        low_f_graph.scale(0.8)
        low_f_graph.move_to(high_f_graph, LEFT)

        cos_arg_rect = SurroundingRectangle(cos_arg)

        new_ov = OscillatingVector(
            Vector(RIGHT, color = E_COLOR),
            A_vect = [2, 0, 0],
            frequency = 1,
            start_up_time = 0,
        )

        self.play(FadeIn(group))
        self.play(
            ReplacementTransform(
                self.components[0].get_part_by_tex("f_x").copy(),
                fx_equals_1
            ),
        )
        self.wait(4 - (self.oscillating_vector.internal_time%4))
        self.remove(self.oscillating_vector)
        self.add(new_ov)
        self.play(ShowCreation(
            high_f_graph, run_time = 4,
            rate_func=linear,
        ))
        self.wait()
        self.play(FadeOut(new_ov.vector))
        self.remove(new_ov)
        self.add(self.oscillating_vector)
        self.play(
            ReplacementTransform(*fx_group),
            ReplacementTransform(*graphs),
            FadeOut(new_ov.vector),
            FadeIn(self.vector)
        )
        self.wait(4)
        self.play(ShowCreation(cos_arg_rect))
        self.play(FadeOut(cos_arg_rect))
        self.wait(5)

        self.corner_group = group
        self.fx_equals_fourth = fx_equals_fourth
        self.corner_cos = cos
        self.low_f_graph = low_f_graph
        self.graph_axes = axes

    def add_phi(self):
        corner_cos = self.corner_cos
        corner_phi = TexMobject("+", "\\phi_x")
        corner_phi.set_color_by_tex("phi", self.phi_color)
        corner_phi.scale(0.8)
        corner_phi.next_to(corner_cos[-2], RIGHT, SMALL_BUFF)

        x, y = self.components
        x_without_phi = self.x_without_phi

        words = TextMobject("``Phase shift''")
        words.next_to(ORIGIN, UP+LEFT)
        words.set_color(self.phi_color)
        words.add_background_rectangle()
        arrow = Arrow(words.get_top(), x[-2])
        arrow.set_color(WHITE)

        self.play(
            ReplacementTransform(
                VGroup(*x_without_phi[:-1]),
                VGroup(*x[:-3]),
            ),
            ReplacementTransform(x_without_phi[-1], x[-1]),
            Write(VGroup(*x[-3:-1])),
            corner_cos[-1].next_to, corner_phi.copy(), RIGHT, SMALL_BUFF,
            Write(corner_phi),
            FadeOut(self.fx_equals_fourth),
        )
        self.play(self.low_f_graph.shift, MED_LARGE_BUFF*LEFT)
        self.play(
            Write(words, run_time = 1),
            ShowCreation(arrow)
        )
        self.wait(3)
        self.play(*list(map(FadeOut, [words, arrow])))

        self.corner_cos.add(corner_phi)

    def add_amplitude(self):
        x, y = self.components
        corner_cos = self.corner_cos
        graph = self.low_f_graph
        graph_y_axis = self.graph_axes.y_axis

        A = TexMobject("A_x")
        A.set_color(self.A_color)
        A.move_to(x.get_left())
        corner_A = A.copy()
        corner_A.scale(0.8)
        corner_A.move_to(corner_cos, LEFT)

        h_brace = Brace(Line(ORIGIN, 2*RIGHT), UP)
        v_brace = Brace(Line(
            graph_y_axis.number_to_point(0),
            graph_y_axis.number_to_point(1),
        ), LEFT, buff = SMALL_BUFF)
        for brace in h_brace, v_brace:
            brace.A = brace.get_tex("A_x")
            brace.A.set_color(self.A_color)
        v_brace.A.scale(0.5, about_point = v_brace.get_center())
        all_As = VGroup(A, corner_A, h_brace.A, v_brace.A)

        def update_vect(vect):
            self.oscillating_vector.A_vect[0] = h_brace.get_width()
            return vect

        self.play(
            GrowFromCenter(h_brace),
            GrowFromCenter(v_brace),
        )
        self.wait(2)
        self.play(
            x.next_to, A, RIGHT, SMALL_BUFF,
            corner_cos.next_to, corner_A, RIGHT, SMALL_BUFF,
            FadeIn(all_As)
        )
        x.add(A)
        corner_cos.add(corner_A)
        self.wait()
        factor = 0.5
        self.play(
            v_brace.stretch_in_place, factor, 1,
            v_brace.move_to, v_brace.copy(), DOWN,
            MaintainPositionRelativeTo(v_brace.A, v_brace),
            h_brace.stretch_in_place, factor, 0,
            h_brace.move_to, h_brace.copy(), LEFT,
            MaintainPositionRelativeTo(h_brace.A, h_brace),
            UpdateFromFunc(self.vector, update_vect),
            graph.stretch_in_place, factor, 1,
        )
        self.wait(4)

        self.h_brace = h_brace 
        self.v_brace = v_brace

    def add_kets(self):
        x, y = self.components
        E_equals = self.E_equals
        for mob in x, y, E_equals:
            mob.add_background_rectangle()
            mob.generate_target()

        right_ket = TexMobject("|\\rightarrow\\rangle")
        up_ket = TexMobject("|\\uparrow\\rangle")
        kets = VGroup(right_ket, up_ket)
        kets.set_color(YELLOW)
        for ket in kets:
            ket.add_background_rectangle()
        plus = TextMobject("+")
        group = VGroup(
            E_equals.target, 
            x.target, right_ket, plus,
            y.target, up_ket,
        )
        group.arrange(RIGHT)
        E_equals.target.shift(SMALL_BUFF*UP)
        group.scale(0.8)
        group.move_to(self.brackets, DOWN)
        group.to_edge(LEFT, buff = MED_SMALL_BUFF)

        kets_word = TextMobject("``kets''")
        kets_word.next_to(kets, DOWN, buff = 0.8)
        arrows = VGroup(*[
            Arrow(kets_word.get_top(), ket, color = ket.get_color())
            for ket in kets
        ])
        ket_rects = VGroup(*list(map(SurroundingRectangle, kets)))
        ket_rects.set_color(WHITE)
        unit_vectors = VGroup(*[Vector(2*vect) for vect in (RIGHT, UP)])
        unit_vectors.set_fill(YELLOW)

        self.play(
            FadeOut(self.brackets),
            *list(map(MoveToTarget, [E_equals, x, y]))
        )
        self.play(*list(map(Write, [right_ket, plus, up_ket])), run_time = 1)
        self.play(
            Write(kets_word),
            LaggedStartMap(ShowCreation, arrows, lag_ratio = 0.7),
            run_time = 2,
        )
        self.wait()
        for ket, ket_rect, unit_vect in zip(kets, ket_rects, unit_vectors):
            self.play(ShowCreation(ket_rect))
            self.play(FadeOut(ket_rect))
            self.play(ReplacementTransform(ket[1][1].copy(), unit_vect))
            self.wait()
        self.play(FadeOut(unit_vectors))
        self.play(*list(map(FadeOut, [kets_word, arrows])))

        self.kets = kets
        self.plus = plus

    def switch_to_vertically_polarized_light(self):
        x, y = self.components
        x_ket, y_ket = self.kets
        plus = self.plus

        x.target = TexMobject("0", "").add_background_rectangle()
        y.target = TexMobject(
            "A_y", "\\cos(", "2\\pi", "f_y", "t", "+", "\\phi_y", ")"
        )
        y.target.set_color_by_tex_to_color_map({
            "A" : self.A_color,            
            "f" : self.f_color,
            "phi" : self.phi_color,
        })
        y.target.add_background_rectangle()
        VGroup(x.target, y.target).scale(0.8)
        for mob in [plus] + list(self.kets):
            mob.generate_target()

        movers = x, x_ket, plus, y, y_ket
        group = VGroup(*[m.target for m in movers])
        group.arrange(RIGHT)
        group.move_to(x, LEFT)

        vector_A_vect = np.array(self.oscillating_vector.A_vect)
        def update_vect(vect, alpha):
            self.oscillating_vector.A_vect = rotate_vector(
                vector_A_vect, alpha*np.pi/2
            )
            return vect

        new_h_brace = Brace(Line(ORIGIN, UP), RIGHT)

        words = TextMobject(
            "``", "Vertically", " polarized", "''",
            arg_separator = "",
        )
        words.add_background_rectangle()
        words.move_to(self.horizontally_polarized_words)

        self.play(
            UpdateFromAlphaFunc(self.vector, update_vect),
            Transform(self.h_brace, new_h_brace),
            self.h_brace.A.next_to, new_h_brace, RIGHT, SMALL_BUFF,
            Transform(self.horizontally_polarized_words, words),
            *list(map(FadeOut, [
                self.corner_group, self.v_brace, 
                self.v_brace.A, self.low_f_graph,
            ]))
        )
        self.play(*list(map(MoveToTarget, movers)))
        self.wait(5)

class ChangeFromHorizontalToVerticallyPolarized(DirectionOfPolarizationScene):
    CONFIG = {
        "filter_x_coordinates" : [],
        "EMWave_config" : {
            "start_point" : FRAME_X_RADIUS*LEFT,
            "A_vect" : [0, 2, 0],
        }
    }
    def setup(self):
        DirectionOfPolarizationScene.setup(self)
        self.axes.z_axis.rotate(np.pi/2, OUT)
        self.axes.y_axis.rotate(np.pi/2, UP)
        self.remove(self.pol_filter)
        self.em_wave.M_vects.set_fill(opacity = 0)
        for vect in self.em_wave.E_vects:
            vect.normal_vector = RIGHT
            vect.set_fill(opacity = 0.5)
        self.em_wave.E_vects[-1].set_fill(opacity = 1)

        self.set_camera_orientation(0.9*np.pi/2, -0.05*np.pi)        

    def construct(self):
        self.wait(3)
        self.change_polarization_direction(np.pi/2)
        self.wait(10)

class SumOfTwoWaves(ChangeFromHorizontalToVerticallyPolarized):
    CONFIG = {
        "axes_config" : {
            "y_max" : 1.5,
            "y_min" : -1.5,
            "z_max" : 1.5,
            "z_min" : -1.5,
        },
        "EMWave_config" : {
            "A_vect" : [0, 0, 1],
        },
        "ambient_rotation_rate" : 0,
    }
    def setup(self):
        ChangeFromHorizontalToVerticallyPolarized.setup(self)
        for vect in self.em_wave.E_vects[:-1]:
            vect.set_fill(opacity = 0.3)
        self.side_em_waves = []
        for shift_vect, A_vect in (5*DOWN, [0, 1, 0]), (5*UP, [0, 1, 1]):
            axes = self.axes.copy()
            em_wave = copy.deepcopy(self.em_wave)
            axes.shift(shift_vect)
            em_wave.mobject.shift(shift_vect)
            em_wave.start_point += shift_vect
            for ov in em_wave.continual_animations:
                ov.A_vect = np.array(A_vect)
            self.add(axes, em_wave)
            self.side_em_waves.append(em_wave)

        self.set_camera_orientation(0.95*np.pi/2, -0.03*np.pi)

    def construct(self):
        plus, equals = pe = VGroup(*list(map(TexMobject, "+=")))
        pe.scale(2)
        pe.rotate(np.pi/2, RIGHT)
        pe.rotate(np.pi/2, OUT)
        plus.shift(2.5*DOWN)
        equals.shift(2.5*UP)
        self.add(pe)

        self.wait(16)

class ShowTipToTailSum(ShowVectorEquation):
    def construct(self):
        self.force_skipping()
        self.add_vector()
        self.add_plane()
        self.add_vertial_vector()
        self.revert_to_original_skipping_status()

        self.add_kets()
        self.show_vector_sum()
        self.write_superposition()
        self.add_amplitudes()
        self.add_phase_shift()

    def add_vertial_vector(self):
        self.h_vector = self.vector
        self.h_oscillating_vector = self.oscillating_vector
        self.h_oscillating_vector.start_up_time = 0

        self.v_oscillating_vector = self.h_oscillating_vector.copy()
        self.v_vector = self.v_oscillating_vector.vector
        self.v_oscillating_vector.A_vect = [0, 2, 0]
        self.v_oscillating_vector.update(0)

        self.d_oscillating_vector = Mobject.add_updater(
            Vector(UP+RIGHT, color = E_COLOR),
            lambda v : v.put_start_and_end_on(
                ORIGIN,
                self.v_vector.get_end()+ self.h_vector.get_end(),
            )
        )
        self.d_vector = self.d_oscillating_vector.mobject
        self.d_oscillating_vector.update(0)

        self.add(self.v_oscillating_vector)
        self.add_foreground_mobject(self.v_vector)

    def add_kets(self):
        h_ket, v_ket = kets = VGroup(*[
            TexMobject(
                "\\cos(", "2\\pi", "f", "t", ")",
                "|\\!\\%sarrow\\rangle"%s
            )
            for s in ("right", "up")
        ])
        for ket in kets:
            ket.set_color_by_tex_to_color_map({
                "f" : self.f_color,    
                "rangle" : YELLOW,
            })
            ket.add_background_rectangle(opacity = 1)
            ket.scale(0.8)

        h_ket.next_to(2*RIGHT, UP, SMALL_BUFF)
        v_ket.next_to(2*UP, UP, SMALL_BUFF)
        self.add_foreground_mobject(kets)

        self.kets = kets

    def show_vector_sum(self):
        h_line = DashedLine(ORIGIN, 2*RIGHT)
        v_line = DashedLine(ORIGIN, 2*UP)

        h_line.update = self.generate_dashed_line_update(
            self.h_vector, self.v_vector
        )
        v_line.update = self.generate_dashed_line_update(
            self.v_vector, self.h_vector
        )

        h_ket, v_ket = self.kets
        for ket in self.kets:
            ket.generate_target()
        plus = TexMobject("+")
        ket_sum = VGroup(h_ket.target, plus, v_ket.target)
        ket_sum.arrange(RIGHT)
        ket_sum.next_to(3*RIGHT + 2*UP, UP, SMALL_BUFF)

        self.wait(4)
        self.remove(self.h_oscillating_vector, self.v_oscillating_vector)
        self.add(self.h_vector, self.v_vector)
        h_line.update(h_line)
        v_line.update(v_line)
        self.play(*it.chain(
            list(map(MoveToTarget, self.kets)),
            [Write(plus)],
            list(map(ShowCreation, [h_line, v_line])),
        ))
        blue_black = average_color(BLUE, BLACK)
        self.play(
            GrowFromPoint(self.d_vector, ORIGIN),
            self.h_vector.set_fill, blue_black,
            self.v_vector.set_fill, blue_black,
        )
        self.wait()
        self.add(
            self.h_oscillating_vector,
            self.v_oscillating_vector,
            self.d_oscillating_vector,
            Mobject.add_updater(h_line, h_line.update),
            Mobject.add_updater(v_line, v_line.update),
        )
        self.wait(4)

        self.ket_sum = VGroup(h_ket, plus, v_ket)

    def write_superposition(self):
        superposition_words = TextMobject(
            "``Superposition''", "of",
            "$|\\!\\rightarrow\\rangle$", "and", 
            "$|\\!\\uparrow\\rangle$",
        )
        superposition_words.scale(0.8)
        superposition_words.set_color_by_tex("rangle", YELLOW)
        superposition_words.add_background_rectangle()
        superposition_words.to_corner(UP+LEFT)
        ket_sum = self.ket_sum
        ket_sum.generate_target()
        ket_sum.target.move_to(superposition_words)
        ket_sum.target.align_to(ket_sum, UP)

        sum_word = TextMobject("", "Sum")
        weighted_sum_word = TextMobject("Weighted", "sum")
        for word in sum_word, weighted_sum_word:
            word.scale(0.8)
            word.set_color(GREEN)
            word.add_background_rectangle()
            word.move_to(superposition_words.get_part_by_tex("Super"))

        self.play(
            Write(superposition_words, run_time = 2),
            MoveToTarget(ket_sum)
        )
        self.wait(2)
        self.play(
            FadeIn(sum_word),
            superposition_words.shift, MED_LARGE_BUFF*DOWN,
            ket_sum.shift, MED_LARGE_BUFF*DOWN,
        )
        self.wait()
        self.play(ReplacementTransform(
            sum_word, weighted_sum_word
        ))
        self.wait(2)

    def add_amplitudes(self):
        h_ket, plus, r_ket = self.ket_sum
        for mob in self.ket_sum:
            mob.generate_target()
        h_A, v_A = 2, 0.5
        h_A_mob, v_A_mob = A_mobs = VGroup(*[
            TexMobject(str(A)).add_background_rectangle()
            for A in [h_A, v_A]
        ])
        A_mobs.scale(0.8)
        A_mobs.set_color(GREEN)
        h_A_mob.move_to(h_ket, LEFT)
        VGroup(h_ket.target, plus.target).next_to(
            h_A_mob, RIGHT, SMALL_BUFF
        )
        v_A_mob.next_to(plus.target, RIGHT, SMALL_BUFF)
        r_ket.target.next_to(v_A_mob, RIGHT, SMALL_BUFF)
        A_mobs.shift(0.4*SMALL_BUFF*UP)

        h_ov = self.h_oscillating_vector
        v_ov = self.v_oscillating_vector


        self.play(*it.chain(
            list(map(MoveToTarget, self.ket_sum)),
            list(map(Write, A_mobs)),
            [
                UpdateFromAlphaFunc(
                    ov.vector,
                    self.generate_A_update(
                        ov, 
                        A*np.array(ov.A_vect), 
                        np.array(ov.A_vect)
                    )
                )
                for ov, A in [(h_ov, h_A), (v_ov, v_A)]
            ]
        ))
        self.wait(4)

        self.A_mobs = A_mobs

    def add_phase_shift(self):
        h_ket, plus, v_ket = self.ket_sum

        plus_phi = TexMobject("+", "\\pi/2")
        plus_phi.set_color_by_tex("pi", self.phi_color)
        plus_phi.scale(0.8)
        plus_phi.next_to(v_ket.get_part_by_tex("t"), RIGHT, SMALL_BUFF)
        v_ket.generate_target()
        VGroup(*v_ket.target[1][-2:]).next_to(plus_phi, RIGHT, SMALL_BUFF)
        v_ket.target[0].replace(v_ket.target[1])


        h_ov = self.h_oscillating_vector
        v_ov = self.v_oscillating_vector

        ellipse = Circle()
        ellipse.stretch_to_fit_height(2)
        ellipse.stretch_to_fit_width(8)
        ellipse.set_color(self.phi_color)

        h_A_mob, v_A_mob = self.A_mobs
        new_h_A_mob = v_A_mob.copy()
        new_h_A_mob.move_to(h_A_mob, RIGHT)

        self.add_foreground_mobject(plus_phi)
        self.play(
            MoveToTarget(v_ket),
            Write(plus_phi),
            UpdateFromAlphaFunc(
                v_ov.vector,
                self.generate_phi_update(
                    v_ov, 
                    np.array([0, np.pi/2, 0]), 
                    np.array(v_ov.phi_vect)
                )
            )
        )
        self.play(FadeIn(ellipse))
        self.wait(5)
        self.play(
            UpdateFromAlphaFunc(
                h_ov.vector,
                self.generate_A_update(
                    h_ov, 
                    0.25*np.array(h_ov.A_vect), 
                    np.array(h_ov.A_vect),
                )
            ),
            ellipse.stretch, 0.25, 0,
            Transform(h_A_mob, new_h_A_mob)
        )
        self.wait(8)

    #####

    def generate_A_update(self, ov, A_vect, prev_A_vect):
        def update(vect, alpha):
            ov.A_vect = interpolate(
                np.array(prev_A_vect),
                A_vect,
                alpha
            )
            return vect
        return update

    def generate_phi_update(self, ov, phi_vect, prev_phi_vect):
        def update(vect, alpha):
            ov.phi_vect = interpolate(
                prev_phi_vect, phi_vect, alpha
            )
            return vect
        return update

    def generate_dashed_line_update(self, v1, v2):
        def update_line(line):
            line.put_start_and_end_on_with_projection(
                *v1.get_start_and_end()
            )
            line.shift(v2.get_end() - line.get_start())
        return update_line

class FromBracketFootnote(Scene):
    def construct(self):
        words = TextMobject(
            "From, ``Bra", "ket", "''",
            arg_separator = ""
        )
        words.set_color_by_tex("ket", YELLOW)
        words.set_width(FRAME_WIDTH - 1)
        self.add(words)

class Ay(Scene):
    def construct(self):
        sym = TexMobject("A_y").set_color(GREEN)
        sym.scale(5)
        self.add(sym)

class CircularlyPolarizedLight(SumOfTwoWaves):
    CONFIG = {
        "EMWave_config" : {
            "phi_vect" : [0, np.pi/2, 0],
        },
    }

class AlternateBasis(ShowTipToTailSum):
    def construct(self):
        self.force_skipping()
        self.add_vector()
        self.add_plane()
        self.add_vertial_vector()
        self.add_kets()
        self.show_vector_sum()
        self.remove(self.ket_sum, self.kets)
        self.reset_amplitude()
        self.revert_to_original_skipping_status()

        self.add_superposition_text()
        self.rotate_plane()
        self.show_vertically_polarized()

    def reset_amplitude(self):
        self.h_oscillating_vector.A_vect = np.array([1, 0, 0])

    def add_superposition_text(self):
        self.hv_superposition, self.da_superposition = superpositions = [
            TexMobject(
                "\\vec{\\textbf{E}}", "=",
                "(\\dots)",
                "|\\!\\%sarrow\\rangle"%s1,
                "+",
                "(\\dots)",
                "|\\!\\%sarrow\\rangle"%s2,
            )
            for s1, s2 in [("right", "up"), ("ne", "nw")]
        ]
        for superposition in superpositions:
            superposition.set_color_by_tex("rangle", YELLOW)
            superposition.set_color_by_tex("E", E_COLOR)
            superposition.add_background_rectangle(opacity = 1)
            superposition.to_edge(UP)
        self.add(self.hv_superposition)

    def rotate_plane(self):
        new_plane = NumberPlane(
            x_unit_size = 2,
            y_unit_size = 2,
            y_radius = FRAME_X_RADIUS,
            secondary_line_ratio = 0,
        )
        new_plane.add_coordinates()
        new_plane.save_state()
        new_plane.fade(1)

        d = (RIGHT + UP)/np.sqrt(2)
        a = (LEFT + UP)/np.sqrt(2)

        self.wait(4)
        self.play(
            self.xy_plane.fade, 0.5,
            self.xy_plane.coordinate_labels.fade, 1,
            new_plane.restore,
            new_plane.rotate, np.pi/4,
            UpdateFromAlphaFunc(
                self.h_vector,
                self.generate_A_update(
                    self.h_oscillating_vector,
                    2*d*np.dot(0.5*RIGHT + UP, d),
                    np.array(self.h_oscillating_vector.A_vect)
                )
            ),
            UpdateFromAlphaFunc(
                self.v_vector,
                self.generate_A_update(
                    self.v_oscillating_vector,
                    2*a*np.dot(0.5*RIGHT + UP, a),
                    np.array(self.v_oscillating_vector.A_vect)
                )
            ),
            Transform(self.hv_superposition, self.da_superposition),
            run_time = 2,
        )
        self.wait(4)

    def show_vertically_polarized(self):
        self.play(
            UpdateFromAlphaFunc(
                self.h_vector,
                self.generate_A_update(
                    self.h_oscillating_vector,
                    np.array([0.7, 0.7, 0]),
                    np.array(self.h_oscillating_vector.A_vect)
                )
            ),
            UpdateFromAlphaFunc(
                self.v_vector,
                self.generate_A_update(
                    self.v_oscillating_vector,
                    np.array([-0.7, 0.7, 0]),
                    np.array(self.v_oscillating_vector.A_vect)
                )
            ),
        )
        self.wait(8)

class WriteBasis(Scene):
    def construct(self):
        words = TextMobject("Choice of ``basis''")
        words.set_width(FRAME_WIDTH-1)
        self.play(Write(words))
        self.wait()

class ShowPolarizingFilter(DirectionOfPolarizationScene):
    CONFIG = {
        "EMWave_config" : {
            "start_point" : FRAME_X_RADIUS*LEFT,
        },
        "apply_filter" : True,
    }
    def construct(self):
        self.setup_rectangles()
        self.fade_M_vects()
        self.axes.fade(0.5)

        self.initial_rotation()
        self.mention_energy_absorption()
        self.write_as_superposition()
        self.diagonal_filter()

    def setup_rectangles(self):
        DirectionOfPolarizationScene.setup_rectangles(self)
        self.rectangles[-1].fade(1)

    def fade_M_vects(self):
        self.em_wave.M_vects.set_fill(opacity = 0)

    def initial_rotation(self):
        self.wait()
        self.play(FadeIn(self.rectangles))
        self.wait()
        self.change_polarization_direction(np.pi/2, run_time = 3)
        self.move_camera(phi = 0.9*np.pi/2, theta = -0.05*np.pi)

    def mention_energy_absorption(self):
        words = TextMobject("Absorbs horizontal \\\\ energy")
        words.set_color(RED)
        words.next_to(ORIGIN, UP+RIGHT, MED_LARGE_BUFF)
        words.rotate(np.pi/2, RIGHT)
        words.rotate(np.pi/2, OUT)

        lines = VGroup(*[
            Line(
                np.sin(a)*RIGHT + np.cos(a)*UP,
                np.sin(a)*LEFT + np.cos(a)*UP,
                color = RED,
                stroke_width = 2,
            )
            for a in np.linspace(0, np.pi, 15)
        ])
        lines.rotate(np.pi/2, RIGHT)
        lines.rotate(np.pi/2, OUT)

        self.play(
            Write(words, run_time = 2),
            *list(map(GrowFromCenter, lines))
        )
        self.wait(6)
        self.play(FadeOut(lines))
        self.play(FadeOut(words))

    def write_as_superposition(self):
        superposition, continual_updates = self.get_superposition_tex(0, "right", "up")
        rect = superposition.rect

        self.play(Write(superposition, run_time = 2))
        self.add(*continual_updates)
        for angle in np.pi/4, -np.pi/6:
            self.change_polarization_direction(angle)
            self.wait(3)

        self.move_camera(
            theta = -0.6*np.pi,
            added_anims = [
                Rotate(superposition, -0.6*np.pi, axis = OUT)
            ]
        )
        rect.set_stroke(YELLOW, 3)
        self.play(ShowCreation(rect))
        arrow = Arrow(
            rect.get_nadir(), 3*RIGHT + 0.5*OUT,
            normal_vector = DOWN
        )
        self.play(ShowCreation(arrow))

        for angle in np.pi/3, -np.pi/3, np.pi/6:
            self.change_polarization_direction(angle)
            self.wait(2)
        self.play(
            FadeOut(superposition),
            FadeOut(arrow),
            *[
                FadeOut(cu.mobject)
                for cu in continual_updates
            ]
        )
        self.move_camera(theta = -0.1*np.pi)

    def diagonal_filter(self):
        superposition, continual_updates = self.get_superposition_tex(-np.pi/4, "nw", "ne")

        def update_filter_angle(pf, alpha):
            pf.filter_angle = interpolate(0, -np.pi/4, alpha)

        self.play(
            Rotate(self.pol_filter, np.pi/4, axis = LEFT),
            UpdateFromAlphaFunc(self.pol_filter, update_filter_angle),
            Animation(self.em_wave.mobject)
        )
        superposition.rect.set_stroke(YELLOW, 2)
        self.play(Write(superposition, run_time = 2))
        self.add(*continual_updates)
        for angle in np.pi/4, -np.pi/3, -np.pi/6:
            self.change_polarization_direction(np.pi/4)
            self.wait(2)

    #######

    def get_superposition_tex(self, angle, s1, s2):
        superposition = TexMobject(
            "0.00", "\\cos(", "2\\pi", "f", "t", ")",
            "|\\! \\%sarrow \\rangle"%s1,
            "+",
            "1.00", "\\cos(", "2\\pi", "f", "t", ")",
            "|\\! \\%sarrow \\rangle"%s2,
        )

        A_x = DecimalNumber(0)
        A_y = DecimalNumber(1)
        A_x.move_to(superposition[0])
        A_y.move_to(superposition[8])
        superposition.submobjects[0] = A_x
        superposition.submobjects[8] = A_y
        VGroup(A_x, A_y).set_color(GREEN)
        superposition.set_color_by_tex("f", RED)
        superposition.set_color_by_tex("rangle", YELLOW)
        plus = superposition.get_part_by_tex("+")
        plus.add_to_back(BackgroundRectangle(plus))

        v_part = VGroup(*superposition[8:])
        rect = SurroundingRectangle(v_part)
        rect.fade(1)
        superposition.rect = rect
        superposition.add(rect)

        superposition.shift(3*UP + SMALL_BUFF*LEFT)
        superposition.rotate(np.pi/2, RIGHT)
        superposition.rotate(np.pi/2, OUT)

        def generate_decimal_update(trig_func):
            def update_decimal(decimal):
                new_decimal = DecimalNumber(abs(trig_func(
                    self.reference_line.get_angle() - angle
                )))
                new_decimal.rotate(np.pi/2, RIGHT)
                new_decimal.rotate(np.pi/2, OUT)
                new_decimal.rotate(self.camera.get_theta(), OUT)
                new_decimal.set_depth(decimal.get_depth())
                new_decimal.move_to(decimal, UP)
                new_decimal.set_color(decimal.get_color())
                decimal.align_data(new_decimal)
                families = [
                    mob.family_members_with_points()
                    for mob in (decimal, new_decimal)
                ]
                for sm1, sm2 in zip(*families):
                    sm1.interpolate(sm1, sm2, 1)
                return decimal
            return update_decimal

        continual_updates = [
            Mobject.add_updater(
                A_x, generate_decimal_update(np.sin),
            ),
            Mobject.add_updater(
                A_y, generate_decimal_update(np.cos),
            ),
        ]

        return superposition, continual_updates

class NamePolarizingFilter(Scene):
    def construct(self):
        words = TextMobject("Polarizing filter")
        words.set_width(FRAME_WIDTH - 1)
        self.play(Write(words))
        self.wait()

class EnergyOfWavesWavePortion(DirectWaveOutOfScreen):
    CONFIG = {
        "EMWave_config" : {
            "A_vect" : [0, 1, 1],
            "amplitude" : 4,
            "start_point" : FRAME_X_RADIUS*LEFT + 2*DOWN,
        }
    }
    def construct(self):
        self.grow_arrows()
        self.move_into_position()
        self.fade_M_vects()
        self.label_A()
        self.add_components()
        self.scale_up_and_down()

    def grow_arrows(self):
        for ov in self.em_wave.continual_animations:
            ov.vector.rectangular_stem_width = 0.1
            ov.vector.tip_length = 0.5

    def label_A(self):
        brace = Brace(Line(ORIGIN, 4*RIGHT))
        brace.rotate(np.pi/4, OUT)
        brace.A = brace.get_tex("A", buff = MED_SMALL_BUFF)
        brace.A.scale_in_place(2)
        brace.A.set_color(GREEN)
        brace_group = VGroup(brace, brace.A)
        self.position_brace_group(brace_group)
        self.play(Write(brace_group, run_time = 1))
        self.wait(12)

        self.brace = brace

    def add_components(self):
        h_wave = self.em_wave.copy()
        h_wave.A_vect = [0, 1, 0]
        v_wave = self.em_wave.copy()
        v_wave.A_vect = [0, 0, 1]
        length = 4/np.sqrt(2)
        for wave in h_wave, v_wave:
            for ov in wave.continual_animations:
                ov.A_vect = length*np.array(wave.A_vect)

        h_brace = Brace(Line(ORIGIN, length*RIGHT))
        v_brace = Brace(Line(ORIGIN, length*UP), LEFT)
        for brace, c in (h_brace, "x"), (v_brace, "y"):
            brace.A = brace.get_tex("A_%s"%c, buff = MED_LARGE_BUFF)
            brace.A.scale_in_place(2)
            brace.A.set_color(GREEN)
        brace_group = VGroup(h_brace, h_brace.A, v_brace, v_brace.A)
        self.position_brace_group(brace_group)

        rhs = TexMobject("= \\sqrt{A_x^2 + A_y^2}")
        rhs.scale(2)
        for i in 3, 5, 7, 9:
            rhs[i].set_color(GREEN)
        rhs.rotate(np.pi/2, RIGHT)
        rhs.rotate(np.pi/2, OUT)

        period = 1./self.em_wave.frequency
        self.add(h_wave, v_wave)
        self.play(
            FadeIn(h_wave.mobject),
            FadeIn(v_wave.mobject),
            self.brace.A.move_to, self.brace,
            self.brace.A.shift, SMALL_BUFF*(2*UP+IN),
            ReplacementTransform(self.brace, h_brace),
            Write(h_brace.A)
        )
        self.wait(6)

        self.play(
            ReplacementTransform(h_brace.copy(), v_brace),
            Write(v_brace.A)
        )
        self.wait(6)
        rhs.next_to(self.brace.A, UP, SMALL_BUFF)
        self.play(Write(rhs))
        self.wait(2*period)

        self.h_brace = h_brace
        self.v_brace = v_brace
        self.h_wave = h_wave
        self.v_wave = v_wave

    def scale_up_and_down(self):
        for scale_factor in 1.25, 0.4, 1.5, 0.3, 2:
            self.scale_wave(scale_factor)
            self.wait()
        self.wait(4)

    ######

    def position_brace_group(self, brace_group):
        brace_group.rotate(np.pi/2, RIGHT)
        brace_group.rotate(np.pi/2, OUT)
        brace_group.shift(2*DOWN)

    def scale_wave(self, factor):
        def generate_vect_update(ov):
            prev_A = np.array(ov.A_vect)
            new_A = factor*prev_A
            def update(vect, alpha):
                ov.A_vect = interpolate(
                    prev_A, new_A, alpha
                )
                return vect
            return update
        h_brace = self.h_brace
        v_brace = self.v_brace

        h_brace.generate_target()
        h_brace.target.stretch_about_point(
            factor, 1, h_brace.get_bottom()
        )
        v_brace.generate_target()
        v_brace.target.stretch_about_point(
            factor, 2, v_brace.get_nadir()
        )
        self.play(
            MoveToTarget(h_brace),
            MoveToTarget(v_brace),
            *[
                UpdateFromAlphaFunc(ov.vector, generate_vect_update(ov))
                for ov in it.chain(
                    self.em_wave.continual_animations,
                    self.h_wave.continual_animations,
                    self.v_wave.continual_animations,
                )
            ]
        )

class EnergyOfWavesTeacherPortion(TeacherStudentsScene):
    def construct(self):
        self.show_energy_equation()
        self.show_both_ways_of_thinking_about_it()

    def show_energy_equation(self):
        dot = Dot(self.teacher.get_top() + 2*(UP+LEFT))
        dot.fade(1)
        self.dot = dot

        energy = TexMobject(
            "\\frac{\\text{Energy}}{\\text{Volume}}",
            "=", 
            "\\epsilon_0", "A", "^2"
        )
        energy.set_color_by_tex("A", GREEN)
        energy.to_corner(UP+LEFT)

        component_energy = TexMobject(
            "=", "\\epsilon_0", "A_x", "^2", 
            "+", "\\epsilon_0", "A_y", "^2", 
        )
        for i in 2, 6:
            component_energy[i][0].set_color(GREEN)
            component_energy[i+1].set_color(GREEN)
        component_energy.next_to(energy[1], DOWN, MED_LARGE_BUFF, LEFT)

        self.play(
            Animation(dot),
            self.teacher.change, "raise_right_hand", dot,
        )
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = dot
        )
        self.wait(2)
        self.play(Write(energy))
        self.play(self.teacher.change, "happy")
        self.wait(3)
        self.play(
            ReplacementTransform(
                VGroup(*energy[-4:]).copy(),
                VGroup(*component_energy[:4])
            ),
            ReplacementTransform(
                VGroup(*energy[-4:]).copy(),
                VGroup(*component_energy[4:])
            )
        )
        self.change_student_modes(*["happy"]*3, look_at_arg = energy)
        self.wait()

    def show_both_ways_of_thinking_about_it(self):
        s1, s2 = self.get_students()[:2]
        b1, b2 = [
            ThoughtBubble(direction = v).scale(0.5)
            for v in (LEFT, RIGHT)
        ]
        b1.pin_to(s1)
        b2.pin_to(s2)

        b1.write("Add \\\\ components")
        b2.write("Pythagorean \\\\ theorem")

        for b, s in (b1, s1), (b2, s2):
            self.play(
                ShowCreation(b),
                Write(b.content, run_time = 2),
                s.change, "thinking"
            )
            self.wait(2)
        self.change_student_modes(
            *["plain"]*3,
            look_at_arg = self.dot,
            added_anims = [
                self.teacher.change, "raise_right_hand", self.dot
            ]

        )
        self.play(self.teacher.look_at, self.dot)
        self.wait(5)

class DescribePhoton(ThreeDScene):
    CONFIG = {
        "x_color" : RED,
        "y_color" : GREEN,
    }
    def setup(self):
        self.axes = ThreeDAxes()
        self.add(self.axes)

        self.set_camera_orientation(phi = 0.8*np.pi/2, theta = -np.pi/4)
        em_wave = EMWave(
            start_point = FRAME_X_RADIUS*LEFT,
            A_vect = [0, 1, 1],
            wave_number = 0,
            amplitude = 3,
        )
        for ov in em_wave.continual_animations:
            ov.vector.normal_vector = RIGHT
            ov.vector.set_fill(opacity = 0.7)
        for M_vect in em_wave.M_vects:
            M_vect.set_fill(opacity = 0)
        em_wave.update(0)
        photon = WavePacket(
            em_wave = em_wave,
            run_time = 2,
        )

        self.photon = photon
        self.em_wave = em_wave

    def construct(self):
        self.add_ket_equation()
        self.shoot_a_few_photons()
        self.freeze_photon()
        self.reposition_to_face_photon_head_on()
        self.show_components()
        self.show_amplitude_and_phase()
        self.change_basis()
        self.write_different_meaning()
        self.write_components()
        self.describe_via_energy()
        self.components_not_possible_in_isolation()
        self.ask_what_they_mean()
        self.change_camera()

    def add_ket_equation(self):
        equation = TexMobject(
            "|\\!\\psi\\rangle", 
            "=",
            "\\alpha", "|\\!\\rightarrow \\rangle", "+",
            "\\beta", "|\\!\\uparrow \\rangle",
        )
        equation.to_edge(UP)
        equation.set_color_by_tex("psi", E_COLOR)
        equation.set_color_by_tex("alpha", self.x_color)
        equation.set_color_by_tex("beta", self.y_color)
        rect = SurroundingRectangle(equation.get_part_by_tex("psi"))
        rect.set_color(E_COLOR)
        words = TextMobject("Polarization\\\\", "state")
        words.next_to(rect, DOWN)
        for part in words:
            bg_rect = BackgroundRectangle(part)
            bg_rect.stretch_in_place(2, 1)
            part.add_to_back(bg_rect)
        equation.rect = rect
        equation.words = words
        equation.add_background_rectangle()
        equation.add(rect, words)
        VGroup(rect, words).fade(1)

        equation.rotate(np.pi/2, RIGHT)
        equation.rotate(np.pi/2 + self.camera.get_theta(), OUT)

        self.add(equation)
        self.equation = equation
        self.superposition = VGroup(*equation[1][2:])

    def shoot_a_few_photons(self):
        for x in range(2):
            self.play(self.photon)

    def freeze_photon(self):
        self.play(
            self.photon,
            rate_func = lambda x : 0.55*x,
            run_time = 1
        )
        self.add(self.photon.mobject)
        self.photon.rate_func = lambda x : x
        self.photon.run_time = 2

    def reposition_to_face_photon_head_on(self):
        plane = NumberPlane(
            color = LIGHT_GREY,
            secondary_color = DARK_GREY,
            x_unit_size = 2,
            y_unit_size = 2,
            y_radius = FRAME_X_RADIUS,
        )
        plane.add_coordinates(x_vals = list(range(-3, 4)), y_vals = [])
        plane.rotate(np.pi/2, RIGHT)
        plane.rotate(np.pi/2, OUT)

        self.play(self.em_wave.M_vects.set_fill, None, 0)
        self.move_camera(
            phi = np.pi/2, theta = 0,
            added_anims = [
                Rotate(self.equation, -self.camera.get_theta())
            ]
        )
        self.play(
            Write(plane, run_time = 1), 
            Animation(self.equation)
        )

        self.xy_plane = plane

    def show_components(self):
        h_arrow, v_arrow = [
            Vector(
                1.38*direction, 
                color = color,
                normal_vector = RIGHT,
            )
            for color, direction in [(self.x_color, UP), (self.y_color, OUT)]
        ]
        v_arrow.move_to(h_arrow.get_end(), IN)
        h_part = VGroup(*self.equation[1][2:4]).copy()
        v_part = VGroup(*self.equation[1][5:7]).copy()

        self.play(
            self.equation.rect.set_stroke, BLUE, 4,
            self.equation.words.set_fill, WHITE, 1,
        )
        for part, arrow, d in (h_part, h_arrow, IN), (v_part, v_arrow, UP):
            self.play(
                part.next_to, arrow.get_center(), d,
                ShowCreation(arrow)
            )
            part.rotate(np.pi/2, DOWN)
            bg_rect = BackgroundRectangle(part)
            bg_rect.stretch_in_place(1.3, 0)
            part.add_to_back(bg_rect)
            part.rotate(np.pi/2, UP)
            self.add(part)
        self.wait()

        self.h_part_tex = h_part
        self.h_arrow = h_arrow
        self.v_part_tex = v_part
        self.v_arrow = v_arrow

    def show_amplitude_and_phase(self):
        alpha = self.h_part_tex[1]
        new_alpha = alpha.copy().shift(IN)
        rhs = TexMobject(
            "=", "A_x", "e", 
            "^{i", "(2\\pi", "f", "t", "+", "\\phi_x)}"
        )
        A_rect = SurroundingRectangle(rhs.get_part_by_tex("A_x"), buff = 0.5*SMALL_BUFF)
        A_word = TextMobject("Amplitude")
        A_word.add_background_rectangle()
        A_word.next_to(A_rect, DOWN, aligned_edge = LEFT)
        A_group = VGroup(A_rect, A_word)
        A_group.set_color(YELLOW)
        phase_rect = SurroundingRectangle(VGroup(*rhs[4:]), buff = 0.5*SMALL_BUFF)
        phase_word = TextMobject("Phase")
        phase_word.add_background_rectangle()
        phase_word.next_to(phase_rect, UP)
        phase_group = VGroup(phase_word, phase_rect)
        phase_group.set_color(MAROON_B)
        rhs.add_background_rectangle()

        group = VGroup(rhs, A_group, phase_group)
        group.rotate(np.pi/2, RIGHT)
        group.rotate(np.pi/2, OUT)
        group.next_to(new_alpha, UP, SMALL_BUFF)

        self.play(
            ReplacementTransform(alpha.copy(), new_alpha),
            FadeIn(rhs)
        )
        for word, rect in A_group, phase_group:
            self.play(
                ShowCreation(rect),
                Write(word, run_time = 1)
            )
        self.wait()
        self.play(*list(map(FadeOut, [new_alpha, group])))

    def change_basis(self):
        superposition = self.superposition
        plane = self.xy_plane
        h_arrow = self.h_arrow
        v_arrow = self.v_arrow
        h_part = self.h_part_tex
        v_part = self.v_part_tex
        axes = self.axes
        movers = [
            plane, axes,
            h_arrow, v_arrow, 
            h_part, v_part, 
            self.equation,
            superposition, 
        ]
        for mob in movers:
            mob.save_state()

        superposition.target = TexMobject(
            "\\gamma", "|\\! \\nearrow \\rangle", "+",
            "\\delta", "|\\! \\nwarrow \\rangle",
        )
        superposition.target.set_color_by_tex("gamma", TEAL_D)
        superposition.target.set_color_by_tex("delta", MAROON)
        for part in superposition.target.get_parts_by_tex("rangle"):
            part[1].rotate_in_place(-np.pi/12)
        superposition.target.rotate(np.pi/2, RIGHT)
        superposition.target.rotate(np.pi/2, OUT)
        superposition.target.move_to(superposition)

        for mob in plane, axes:
            mob.generate_target()
            mob.target.rotate(np.pi/6, RIGHT)

        A = 1.9
        h_arrow.target = Vector(
            A*np.cos(np.pi/12)*rotate_vector(UP, np.pi/6, RIGHT),
            normal_vector = RIGHT,
            color = TEAL
        )
        v_arrow.target = Vector(
            A*np.sin(np.pi/12)*rotate_vector(OUT, np.pi/6, RIGHT),
            normal_vector = RIGHT,
            color = MAROON
        )
        v_arrow.target.shift(h_arrow.target.get_vector())

        h_part.target = VGroup(*superposition.target[:2]).copy()
        v_part.target = VGroup(*superposition.target[3:]).copy()
        h_part.target.next_to(
            h_arrow.target.get_center(), IN+UP, SMALL_BUFF
        )
        v_part.target.next_to(
            v_arrow.target.get_center(), UP, SMALL_BUFF
        )
        for part in h_part.target, v_part.target:
            part.rotate(np.pi/2, DOWN)
            part.add_to_back(BackgroundRectangle(part))
            part.rotate(np.pi/2, UP)

        self.equation.generate_target()

        self.play(*list(map(MoveToTarget, movers)))
        self.wait(2)
        self.play(*[mob.restore for mob in movers])
        self.wait()

    def write_different_meaning(self):
        superposition = self.superposition
        superposition.rotate(np.pi/2, DOWN)
        rect = SurroundingRectangle(superposition)
        VGroup(superposition, rect).rotate(np.pi/2, UP)
        morty = Mortimer(mode = "confused")
        blinked = morty.copy().blink()
        words = TextMobject("Means something \\\\ different...")
        for mob in morty, blinked, words:
            mob.rotate(np.pi/2, RIGHT)
            mob.rotate(np.pi/2, OUT)
        words.next_to(rect, UP)
        VGroup(morty, blinked).next_to(words, IN)

        self.play(
            ShowCreation(rect),
            Write(words, run_time = 2)
        )
        self.play(FadeIn(morty))
        self.play(Transform(
            morty, blinked, 
            rate_func = squish_rate_func(there_and_back)
        ))
        self.wait()
        self.play(*list(map(FadeOut, [
            morty, words, rect,
            self.equation.rect,
            self.equation.words,
        ])))

    def write_components(self):
        d_brace = Brace(Line(ORIGIN, 2*RIGHT), UP, buff = SMALL_BUFF)
        h_brace = Brace(Line(ORIGIN, (2/np.sqrt(2))*RIGHT), DOWN, buff = SMALL_BUFF)
        v_brace = Brace(Line(ORIGIN, (2/np.sqrt(2))*UP), RIGHT, buff = SMALL_BUFF)
        d_brace.rotate(np.pi/4)
        v_brace.shift((2/np.sqrt(2))*RIGHT)
        braces = VGroup(d_brace, h_brace, v_brace)
        group = VGroup(braces)

        tex = ["1"] + 2*["\\sqrt{1/2}"]
        colors = BLUE, self.x_color, self.y_color
        for brace, tex, color in zip(braces, tex, colors):
            brace.label = brace.get_tex(tex, buff = SMALL_BUFF)
            brace.label.add_background_rectangle()
            brace.label.set_color(color)
            group.add(brace.label)

        group.rotate(np.pi/2, RIGHT)
        group.rotate(np.pi/2, OUT)

        self.play(
            GrowFromCenter(d_brace),
            Write(d_brace.label)
        )
        self.wait()
        self.play(
            FadeOut(self.h_part_tex),
            FadeOut(self.v_part_tex),
            GrowFromCenter(h_brace),
            GrowFromCenter(v_brace),
        )
        self.play(
            Write(h_brace.label),
            Write(v_brace.label),
        )
        self.wait()

        self.d_brace = d_brace
        self.h_brace = h_brace
        self.v_brace = v_brace

    def describe_via_energy(self):
        energy = TexMobject(
            "&\\text{Energy}", 
            "=", "(hf)", "(", "1", ")^2\\\\",
            "&=", "(hf)", "\\left(", "\\sqrt{1/2}", "\\right)^2", 
            "+", "(hf)", "\\left(", "\\sqrt{1/2}", "\\right)^2",
        )
        energy.scale(0.8)
        one = energy.get_part_by_tex("1", substring = False)
        one.set_color(BLUE)
        halves = energy.get_parts_by_tex("1/2")
        halves[0].set_color(self.x_color)
        halves[1].set_color(self.y_color)
        indices = [0, 3, 6, len(energy)]
        parts = VGroup(*[
            VGroup(*energy[i1:i2])
            for i1, i2 in zip(indices, indices[1:])    
        ])
        for part in parts:
            bg_rect = BackgroundRectangle(part)
            bg_rect.stretch_in_place(1.5, 1)
            part.add_to_back(bg_rect)

        parts.to_corner(UP+LEFT, buff = MED_SMALL_BUFF)
        parts.shift(DOWN)
        parts.rotate(np.pi/2, RIGHT)
        parts.rotate(np.pi/2, OUT)

        self.play(Write(parts[0]), run_time = 2)
        self.play(Indicate(energy.get_part_by_tex("hf")))
        self.play(
            Transform(
                self.d_brace.label.copy(),
                one.copy(),
                remover = True
            ),
            Write(parts[1], run_time = 1),
        )
        self.wait()
        self.play(
            Transform(
                self.h_brace.label[1].copy(),
                halves[0].copy(),
                remover = True,
                rate_func = squish_rate_func(smooth, 0, 0.75)
            ),
            Transform(
                self.v_brace.label[1].copy(),
                halves[1].copy(),
                remover = True,
                rate_func = squish_rate_func(smooth, 0.25, 1)
            ),
            Write(parts[2]),
            run_time = 2
        )
        self.wait()

        self.energy_equation_parts = parts

    def components_not_possible_in_isolation(self):
        half_hf = VGroup(*self.energy_equation_parts[2][1:6])
        half_hf.rotate(np.pi/2, DOWN)
        rect = SurroundingRectangle(half_hf)
        VGroup(half_hf, rect).rotate(np.pi/2, UP)

        randy = Randolph()
        randy.scale(0.7)
        randy.look(UP)
        randy.rotate(np.pi/2, RIGHT)
        randy.rotate(np.pi/2, OUT)
        randy.next_to(rect, IN)

        self.play(
            ShowCreation(rect),
            FadeIn(randy)
        )
        self.play(
            randy.rotate, np.pi/2, IN,
            randy.rotate, np.pi/2, LEFT,
            randy.change, "maybe",
            randy.rotate, np.pi/2, RIGHT,
            randy.rotate, np.pi/2, OUT,
        )
        self.wait()

    def ask_what_they_mean(self):
        morty = Mortimer(mode = "confused")
        morty.scale(0.7)
        morty.to_edge(LEFT)

        bubble = morty.get_bubble()
        bubble.write("?!?")
        bubble.resize_to_content()
        bubble.add(bubble.content)
        bubble.pin_to(morty)

        group = VGroup(morty, bubble)
        group.to_corner(DOWN+RIGHT)
        group.rotate(np.pi/2, RIGHT)
        group.rotate(np.pi/2, OUT)

        component = VGroup(self.h_arrow, self.h_brace, self.h_brace.label)

        self.play(
            FadeIn(morty),
            component.next_to, morty, DOWN, OUT,
            component.shift, MED_LARGE_BUFF*(DOWN + OUT),
        )
        component.rotate(np.pi/2, DOWN)
        cross = Cross(component)
        VGroup(component, cross).rotate(np.pi/2, UP)
        cross.set_color("#ff0000")
        self.play(ShowCreation(cross))
        bubble.remove(bubble.content)
        self.play(
            ShowCreation(bubble),
            Write(bubble.content),
            morty.look_at, component,
        )
        self.wait()

    def change_camera(self):
        everything = VGroup(*self.get_top_level_mobjects())
        everything.remove(self.photon.mobject)
        everything.remove(self.axes)

        self.play(*list(map(FadeOut, everything)))
        self.move_camera(
            phi = 0.8*np.pi/2,
            theta = -0.3*np.pi, 
            run_time = 2
        )
        self.play(
            self.photon,
            rate_func = lambda x : min(x + 0.55, 1),
            run_time = 2,
        )
        self.photon.rate_func = lambda x : x
        self.play(self.photon)
        self.wait()

class SeeCommentInDescription(Scene):
    def construct(self):
        words = TextMobject("""
            \\begin{flushleft}
            $^*$See comment in the \\\\
            description on single-headed \\\\
            vs. double-headed arrows
            \\end{flushleft}
        """)
        words.set_width(FRAME_WIDTH - 1)
        words.to_corner(DOWN+LEFT)
        self.add(words)

class SeeCommentInDescriptionAgain(Scene):
    def construct(self):
        words = TextMobject("$^*$Again, see description")
        words.set_width(FRAME_WIDTH - 1)
        words.to_corner(DOWN+LEFT)
        self.add(words)

class GetExperimental(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("Get experimental!", target_mode = "hooray")
        self.change_student_modes(*["hooray"]*3)
        self.wait(3)

class ShootPhotonThroughFilter(DirectionOfPolarizationScene):
    CONFIG = {
        "EMWave_config" : {
            "wave_number" : 0,
            "A_vect" : [0, 1, 1],
            "start_point" : FRAME_X_RADIUS*LEFT,
            "amplitude" : np.sqrt(2),
        },
        "pol_filter_configs" : [{
            "label_tex" : "\\text{Filter}",
            "include_arrow_label" : False,
        }],
        "apply_filter" : True,
        "quantum" : True,
        "pre_filter_alpha" : 0.35,
        "ambient_rotation_rate" : 0,
    }
    def setup(self):
        DirectionOfPolarizationScene.setup(self)
        self.em_wave.update(0)
        self.remove(self.em_wave)

    def construct(self):
        self.force_skipping()

        self.add_superposition_tex()
        self.ask_what_would_happen()
        self.expect_half_energy_to_be_absorbed()
        self.probabalistic_passing_and_blocking()
        # self.note_change_in_polarization()

    def add_superposition_tex(self):
        superposition_tex = TexMobject(
            "|\\!\\nearrow\\rangle", 
            "=",
            "(\\sqrt{1/2})", "|\\!\\rightarrow \\rangle", "+",
            "(\\sqrt{1/2})", "|\\!\\uparrow \\rangle",
        )
        superposition_tex.scale(0.9)
        superposition_tex[0].set_color(E_COLOR)
        halves = superposition_tex.get_parts_by_tex("1/2")
        for half, color in zip(halves, [RED, GREEN]):
            half.set_color(color)

        h_rect = SurroundingRectangle(VGroup(*superposition_tex[2:4]))
        v_rect = SurroundingRectangle(VGroup(*superposition_tex[5:7]))
        VGroup(h_rect, v_rect).fade(1)
        superposition_tex.h_rect = h_rect
        superposition_tex.v_rect = v_rect
        superposition_tex.add(h_rect, v_rect)

        superposition_tex.next_to(ORIGIN, LEFT)
        superposition_tex.to_edge(UP)
        superposition_tex.rotate(np.pi/2, RIGHT)
        self.superposition_tex = superposition_tex

    def ask_what_would_happen(self):
        photon = self.get_photon(
            rate_func = lambda t : self.pre_filter_alpha*t,
            remover = False,
            run_time = 0.6,
        )
        question = TextMobject("What's going to happen?")
        question.add_background_rectangle()
        question.set_color(YELLOW)
        question.rotate(np.pi/2, RIGHT)
        question.next_to(self.superposition_tex, IN)

        self.pol_filter.add(
            self.pol_filter.arrow.copy().rotate(np.pi/2, OUT)
        )
        self.pol_filter.save_state()
        self.pol_filter.shift(5*OUT)

        self.set_camera_orientation(theta = -0.9*np.pi)
        self.play(self.pol_filter.restore)
        self.move_camera(
            theta = -0.6*np.pi,
        )
        self.play(
            photon,
            FadeIn(self.superposition_tex)
        )
        self.play(Write(question, run_time = 1))
        self.wait()
        self.play(FadeOut(self.pol_filter.label))
        self.pol_filter.remove(self.pol_filter.label)
        self.add(self.pol_filter)

        self.question = question
        self.frozen_photon = photon

    def expect_half_energy_to_be_absorbed(self):
        words = TextMobject("Absorbs horizontal \\\\ energy")
        words.set_color(RED)
        words.next_to(ORIGIN, UP+RIGHT, MED_LARGE_BUFF)
        words.rotate(np.pi/2, RIGHT)
        words.rotate(np.pi/2, OUT)

        lines = VGroup(*[
            Line(
                np.sin(a)*RIGHT + np.cos(a)*UP,
                np.sin(a)*LEFT + np.cos(a)*UP,
                color = RED,
                stroke_width = 2,
            )
            for a in np.linspace(0, np.pi, 15)
        ])
        lines.rotate(np.pi/2, RIGHT)
        lines.rotate(np.pi/2, OUT)

        self.move_camera(
            phi = np.pi/2, theta = 0, 
            added_anims = [
                Rotate(self.superposition_tex, np.pi/2),
            ] + [
                ApplyMethod(
                    v.rotate_in_place, 
                    -np.pi/2, 
                    method_kwargs = {"axis" : v.get_vector()}
                )
                for v in self.frozen_photon.mobject
            ]
        )
        self.play(
            Write(words, run_time = 2),
            self.superposition_tex.h_rect.set_stroke, RED, 3,
            *list(map(GrowFromCenter, lines))+\
            [
                Animation(self.pol_filter), 
                Animation(self.frozen_photon.mobject)
            ]
        )
        self.wait(2)
        self.move_camera(
            phi = 0.8*np.pi/2, theta = -0.7*np.pi,
            added_anims = [
                FadeOut(words),
                Animation(lines),
                Rotate(self.superposition_tex, -np.pi/2),
            ] + [
                ApplyMethod(
                    v.rotate_in_place, 
                    np.pi/2, 
                    method_kwargs = {"axis" : v.get_vector()}
                )
                for v in self.frozen_photon.mobject
            ]
        )
        self.play(
            FadeOut(lines), 
            FadeOut(self.question),
            self.superposition_tex.h_rect.fade, 1,
            Animation(self.pol_filter)
        )
        self.wait()

        self.absorption_words = words

    def probabalistic_passing_and_blocking(self):
        absorption = self.get_filter_absorption_animation(
            self.pol_filter, self.get_blocked_photon()
        )
        prob = TexMobject("P(", "\\text{pass}", ")", "=", "1/2")
        prob.set_color_by_tex("pass", GREEN)
        prob.rotate(np.pi/2, RIGHT)
        prob.next_to(self.superposition_tex, IN, MED_SMALL_BUFF, RIGHT)

        self.remove(self.frozen_photon.mobject)
        self.play(
            self.get_photon(),
            rate_func = lambda t : min(t+self.pre_filter_alpha, 1),
        )
        self.play(
            FadeIn(prob),
            self.get_blocked_photon(),
            absorption
        )
        bools = 6*[True] + 6*[False]
        self.revert_to_original_skipping_status()
        random.shuffle(bools)
        for should_pass in bools:
            if should_pass:
                self.play(self.get_photon(), run_time = 1)
            else:
                self.play(
                    self.get_blocked_photon(), 
                    Animation(self.axes),
                    absorption,
                    run_time = 1
                )
        self.play(FadeOut(prob))

    def note_change_in_polarization(self):
        words = TextMobject(
            "``Collapses'' \\\\ from", "$|\\!\\nearrow\\rangle$",
            "to", "$|\\!\\uparrow\\rangle$"
        )
        words.set_color_by_tex("nearrow", E_COLOR)
        words.set_color_by_tex("uparrow", GREEN)
        words.next_to(ORIGIN, RIGHT, MED_LARGE_BUFF)
        words.shift(2*UP)
        words.rotate(np.pi/2, RIGHT)
        photon = self.get_photon(run_time = 4)
        for vect in photon.mobject:
            if vect.get_center()[0] > 0:
                vect.saved_state.set_fill(GREEN)

        self.play(FadeIn(words), photon)
        for x in range(3):
            self.play(photon)

    ######

    def get_photon(self, **kwargs):
        kwargs["run_time"] = kwargs.get("run_time", 1)
        kwargs["include_M_vects"] = False
        return WavePacket(em_wave = self.em_wave.copy(), **kwargs)

    def get_blocked_photon(self, **kwargs):
        kwargs["get_filtered"] = True
        return self.get_photon(self, **kwargs)

class PhotonPassesCompletelyOrNotAtAllStub(ExternallyAnimatedScene):
    pass

class YouCanSeeTheCollapse(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "You can literally \\\\ \\emph{see} the collapse",
            target_mode = "hooray"
        )
        self.change_student_modes("confused", "hooray", "erm")
        self.wait(3)

class ThreeFilters(ShootPhotonThroughFilter):
    CONFIG = {
        "filter_x_coordinates" : [-4, 0, 4],
        "pol_filter_configs" : [
            {"filter_angle" : 0},
            {"filter_angle" : np.pi/4},
            {"filter_angle" : np.pi/2},
        ],
        "EMWave_config" : {
            "A_vect" : [0, 0, 1],
            "amplitude" : 1.5,
            "n_vectors" : 60,
        },
        "line_start_length" : 8,
        "line_end_length" : 8,
        "n_lines" : 20,
        "lines_depth" : 1.8,
        "lines_shift_vect" : SMALL_BUFF*OUT,
        "random_seed" : 6,
    }
    def construct(self):
        self.remove(self.axes)
        self.setup_filters()
        self.setup_lines()
        self.setup_arrows()

        self.fifty_percent_pass_second()
        self.show_changed_to_diagonal()
        self.fifty_percent_to_pass_third()
        self.show_lines_with_middle()
        self.remove_middle_then_put_back()

    def setup_filters(self):
        for pf in self.pol_filters:
            pf.arrow_label.rotate(np.pi/2, OUT)
            pf.arrow_label.next_to(pf.arrow, RIGHT)
            pf.arrow_label.rotate(np.pi/2, LEFT)
            pf.arrow_label.add_background_rectangle()
            pf.arrow_label.rotate(np.pi/2, RIGHT)
            self.add_foreground_mobject(pf.arrow_label)

    def setup_lines(self):
        lines_group = VGroup(*[
            self.get_lines(pf1, pf2, ratio)
            for pf1, pf2, ratio in zip(
                [None] + list(self.pol_filters),
                list(self.pol_filters) + [None],
                [1, 1, 0.5, 0.25]
            )
        ])
        lines = lines_group[0]
        spacing = lines[1].get_start() - lines[0].get_start()
        lines.add(lines.copy().shift(spacing/2))
        self.lines_group = lines_group

        self.A_to_C_lines = self.get_lines(
            self.pol_filters[0], self.pol_filters[2],
        )

    def setup_arrows(self):
        for E_vect in self.em_wave.E_vects:
            E_vect.normal_vector = IN+DOWN
        self.em_wave.update(0)

    def fifty_percent_pass_second(self):
        arrow = Arrow(
            ORIGIN, 3*RIGHT,
            use_rectangular_stem = False,
            path_arc = -0.8*np.pi
        )
        label = TexMobject("50\\%")
        label.next_to(arrow, UP)
        group = VGroup(arrow, label)
        group.rotate(np.pi/2, RIGHT)
        group.next_to(self.pol_filters[1], OUT, buff = 0)
        group.set_color(BLUE)

        l1, l2, l3 = self.lines_group[:3]
        pf1, pf2, pf3 = self.pol_filters
        kwargs = {
            "lag_ratio" : 0,
            "rate_func" : None,
        }

        self.play(ShowCreation(l1, run_time = 1, **kwargs))
        self.play(
            ShowCreation(l2, **kwargs),
            Animation(VGroup(pf1, l1)),
            ShowCreation(arrow),
            run_time = 0.5,
        )
        self.play(
            ShowCreation(l3, **kwargs),
            Animation(VGroup(pf2, l2, pf1, l1)),
            FadeIn(label),
            run_time = 0.5, 
        )
        self.wait(2)
        self.play(
            FadeOut(l3),
            Animation(pf2), 
            FadeOut(l2),
            Animation(pf1),
            FadeOut(l1)
        )

        self.fifty_percent_arrow_group = group

    def show_changed_to_diagonal(self):
        photon = self.get_photon(
            run_time = 2,
            rate_func = lambda x : 0.6*x,
            remover = False,
        )
        brace = Brace(Line(1.5*LEFT, 1.5*RIGHT), DOWN)
        label = brace.get_text(
            "Changed to", 
            "$|\\!\\nearrow\\rangle$"
        )
        label.set_color_by_tex("rangle", BLUE)
        group = VGroup(brace, label)
        group.rotate(np.pi/2, RIGHT)
        group.shift(2*RIGHT + 0.5*IN)

        self.play(photon)
        self.play(
            GrowFromCenter(brace),
            Write(label, run_time = 1)
        )
        kwargs = {
            "run_time" : 3,
            "rate_func" : there_and_back_with_pause,
        }
        self.move_camera(
            phi = np.pi/2,
            theta = 0,
            added_anims = [
                Animation(VGroup(*self.pol_filters[:2]))
            ] + [
                Rotate(
                    v, np.pi/2, 
                    axis = v.get_vector(),
                    in_place = True,
                    **kwargs
                )
                for v in photon.mobject
            ] + [
                Animation(self.pol_filters[2]),
                Rotate(
                    label, np.pi/2, 
                    axis = OUT,
                    in_place = True,
                    **kwargs
                ),
            ],
            **kwargs
        )
        self.wait()

        self.photon = photon
        self.brace_group = VGroup(brace, label)

    def fifty_percent_to_pass_third(self):
        arrow_group = self.fifty_percent_arrow_group.copy()
        arrow_group.shift(4*RIGHT)
        arrow, label = arrow_group

        a = self.photon.rate_func(1)
        new_photon = self.get_photon(
            rate_func = lambda x : (1-a)*x + a,
            run_time = 1
        )

        self.revert_to_original_skipping_status()
        self.play(
            ShowCreation(arrow),
            Write(label, run_time = 1)
        )
        self.remove(self.photon.mobject)
        self.play(new_photon)

        self.second_fifty_percent_arrow_group = arrow_group

    def show_lines_with_middle(self):
        l1, l2, l3, l4 = self.lines_group
        pf1, pf2, pf3 = self.pol_filters

        self.play(
            FadeIn(l4),
            Animation(pf3),
            FadeIn(l3),
            Animation(pf2),
            FadeIn(l2),
            Animation(pf1),
            FadeIn(l1),
            FadeOut(self.brace_group)
        )
        self.wait(2)

    def remove_middle_then_put_back(self):
        l1, l2, l3, l4 = self.lines_group
        pf1, pf2, pf3 = self.pol_filters
        mid_lines = self.A_to_C_lines
        mover = VGroup(
            pf2, 
            self.fifty_percent_arrow_group,
            self.second_fifty_percent_arrow_group,
        )

        arrow = Arrow(
            ORIGIN, 7*RIGHT,
            path_arc = 0.5*np.pi,
        )
        labels = VGroup(*list(map(TexMobject, ["0\\%", "25\\%"])))
        labels.scale(1.5)
        labels.next_to(arrow, DOWN)
        group = VGroup(arrow, labels)
        group.rotate(np.pi/2, RIGHT)
        group.shift(2*LEFT + IN)
        group.set_color(GREEN)

        self.remove(l2, l3)
        self.play(
            FadeOut(l4),
            Animation(pf3),
            FadeOut(l3),
            ApplyMethod(
                mover.shift, 3*OUT,
                rate_func = running_start
            ),
            ReplacementTransform(l2.copy(), mid_lines),
            Animation(pf1),
            Animation(l1)
        )
        self.play(
            ShowCreation(arrow),
            Write(labels[0], run_time = 1)
        )
        self.wait(2)
        self.play(
            FadeIn(l4),
            Animation(pf3),
            FadeOut(mid_lines),
            FadeIn(l3),
            mover.shift, 3*IN,
            FadeIn(l2),
            Animation(pf1),
            Animation(l1)
        )
        self.play(ReplacementTransform(*labels))
        self.wait(3)


    ####

    def get_photon(self, **kwargs):
        return ShootPhotonThroughFilter.get_photon(self, width = 4, **kwargs)

    def get_lines(self, filter1 = None, filter2 = None, ratio = 1.0):
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
        random.seed(self.random_seed)
        indices_to_block = random.sample(
            list(range(self.n_lines)), n_to_block
        )
        VGroup(*[lines[i] for i in indices_to_block]).set_stroke(width = 0)
        return lines

class PhotonAtSlightAngle(ThreeFilters):
    CONFIG = {
        "filter_x_coordinates" : [3],
        "pol_filter_configs" : [{
            "label_tex" : "",
            "include_arrow_label" : False,
            "radius" : 1.4,
        }],
        "EMWave_config" : {
            "wave_number" : 0,
            "A_vect" : [0, np.sin(np.pi/8), np.cos(np.pi/8)],
            "start_point" : FRAME_X_RADIUS*LEFT,
            "amplitude" : 2,
        },
        "axes_config" : {
            "z_max" : 2.5,
        },
        "radius" : 1.3,
        "lines_depth" : 2.5,
        "line_start_length" : 12,
    }
    def construct(self):
        self.force_skipping()

        self.shoot_photon()
        self.reposition_camera_to_head_on()
        self.write_angle()
        self.write_components()
        self.classical_energy_conception()
        self.reposition_camera_back()
        self.rewrite_15_percent_meaning()
        self.probabalistic_passing()

    def shoot_photon(self):
        photon = self.get_photon(
            rate_func = lambda x : 0.5*x,
            remover = False,
        )
        self.play(photon)
        self.photon = photon

    def reposition_camera_to_head_on(self):
        self.move_camera(
            phi = np.pi/2, theta = 0,
            added_anims = list(it.chain(*[
                [
                    v.rotate_in_place, np.pi/2, v.get_vector(),
                    v.set_fill, None, 0.7,
                ]
                for v in self.photon.mobject
            ])) + [Animation(self.pol_filter)]
        )

    def write_angle(self):
        arc = Arc(
            start_angle = np.pi/2, angle = -np.pi/8,
            radius = self.pol_filter.radius,
        )
        label = TexMobject("22.5^\\circ")
        label.next_to(arc.get_center(), UP+RIGHT, SMALL_BUFF)

        group = VGroup(arc, label)
        group.rotate(np.pi/2, RIGHT)
        group.rotate(np.pi/2, OUT)

        self.play(
            FadeOut(self.pol_filter),
            ShowCreation(arc),
            Write(label, run_time = 1)
        )
        self.wait()

        self.arc = arc
        self.angle_label = label

    def write_components(self):
        d_brace = Brace(Line(ORIGIN, self.radius*RIGHT), UP, buff = SMALL_BUFF)
        d_brace.rotate(np.pi/2 - np.pi/8)
        d_brace.label = d_brace.get_tex("1", buff = SMALL_BUFF)
        d_brace.label.add_background_rectangle()

        h_arrow = Vector(
            self.radius*np.sin(np.pi/8)*RIGHT,
            color = RED,
        )
        h_label = TexMobject("\\sin(22.5^\\circ)")
        h_label.scale(0.7)
        h_label.set_color(RED)
        h_label.next_to(h_arrow.get_center(), DOWN, aligned_edge = LEFT)

        v_arrow = Vector(
            self.radius*np.cos(np.pi/8)*UP,
            color = GREEN
        )
        v_arrow.shift(h_arrow.get_vector())
        v_label = TexMobject("\\cos(22.5^\\circ)")
        v_label.scale(0.7)
        v_label.set_color(GREEN)
        v_label.next_to(v_arrow, RIGHT, SMALL_BUFF)

        state = TexMobject(
            "|\\!\\psi\\rangle", 
            "=", "\\sin(22.5^\\circ)", "|\\!\\rightarrow\\rangle", 
            "+", "\\cos(22.5^\\circ)", "|\\!\\uparrow\\rangle",
        )
        state.set_color_by_tex_to_color_map({
            "psi" : BLUE,
            "rightarrow" : RED,
            "uparrow" : GREEN,
        })
        # state.add_background_rectangle()
        state.to_edge(UP)

        sin_brace = Brace(state.get_part_by_tex("sin"), DOWN, buff = SMALL_BUFF)
        sin_brace.label = sin_brace.get_tex("%.2f"%np.sin(np.pi/8), buff = SMALL_BUFF)
        cos_brace = Brace(state.get_part_by_tex("cos"), DOWN, buff = SMALL_BUFF)
        cos_brace.label = cos_brace.get_tex("%.2f"%np.cos(np.pi/8), buff = SMALL_BUFF)

        group = VGroup(
            d_brace, d_brace.label, 
            h_arrow, h_label,
            v_arrow, v_label,
            state,
            sin_brace, sin_brace.label,
            cos_brace, cos_brace.label,
        )
        group.rotate(np.pi/2, RIGHT)
        group.rotate(np.pi/2, OUT)

        self.play(
            GrowFromCenter(d_brace),
            Write(d_brace.label)
        )
        self.wait()
        self.play(
            GrowFromPoint(h_arrow, ORIGIN),
            Write(h_label, run_time = 1)
        )
        self.play(
            Write(VGroup(*state[:2])),
            ReplacementTransform(
                h_label.copy(), 
                state.get_part_by_tex("sin")
            ),
            ReplacementTransform(
                h_arrow.copy(), 
                state.get_part_by_tex("rightarrow")
            ),
            Write(state.get_part_by_tex("+"))
        )
        self.play(
            GrowFromCenter(sin_brace),
            Write(sin_brace.label, run_time = 1)
        )
        self.wait()
        self.play(
            GrowFromPoint(v_arrow, h_arrow.get_end()),
            Write(v_label, run_time = 1)
        )
        self.play(
            ReplacementTransform(
                v_label.copy(), 
                state.get_part_by_tex("cos")
            ),
            ReplacementTransform(
                v_arrow.copy(), 
                state.get_part_by_tex("uparrow")
            ),
        )
        self.play(
            GrowFromCenter(cos_brace),
            Write(cos_brace.label, run_time = 1)
        )
        self.wait()

        self.d_brace = d_brace
        self.state_equation = state
        self.state_equation.add(
            sin_brace, sin_brace.label,
            cos_brace, cos_brace.label,
        )
        self.sin_brace = sin_brace
        self.cos_brace = cos_brace
        self.h_arrow = h_arrow
        self.h_label = h_label
        self.v_arrow = v_arrow
        self.v_label = v_label

    def classical_energy_conception(self):
        randy = Randolph(mode = "pondering").flip()
        randy.scale(0.7)
        randy.next_to(ORIGIN, LEFT)
        randy.to_edge(DOWN)

        bubble = ThoughtBubble(direction = RIGHT)
        h_content = TexMobject(
            "0.38", "^2", "= 0.15", "\\text{ energy}\\\\",
            "\\text{in the }", "\\rightarrow", "\\text{ direction}"
        )
        alt_h_content = TexMobject(
            "0.38", "^2", "=& 15\\%", "\\text{ of energy}\\\\",
            "&\\text{absorbed}", "", "",
        )
        h_content.set_color_by_tex("rightarrow", RED)
        alt_h_content.set_color_by_tex("rightarrow", RED)
        alt_h_content.scale(0.8)
        v_content = TexMobject(
            "0.92", "^2", "= 0.85", "\\text{ energy}\\\\",
            "\\text{in the }", "\\uparrow", "\\text{ direction}"
        )
        v_content.set_color_by_tex("uparrow", GREEN)

        bubble.add_content(h_content)
        bubble.resize_to_content()
        v_content.move_to(h_content)
        bubble_group = VGroup(bubble, h_content, v_content)
        bubble_group.scale(0.8)
        bubble_group.next_to(randy, UP+LEFT, SMALL_BUFF)

        classically = TextMobject("Classically...")
        classically.next_to(bubble[-1], UP)
        classically.set_color(YELLOW)
        alt_h_content.next_to(classically, DOWN)

        group = VGroup(randy, bubble_group, classically, alt_h_content)
        group.rotate(np.pi/2, RIGHT)
        group.rotate(np.pi/2, OUT)

        filter_lines = self.get_filter_lines(self.pol_filter)

        self.play(
            FadeIn(randy),
            FadeIn(classically),
            ShowCreation(bubble),
        )
        self.play(
            ReplacementTransform(
                self.sin_brace.label.copy(),
                h_content[0]
            ),
            ReplacementTransform(
                self.state_equation.get_part_by_tex("rightarrow").copy(),
                h_content.get_part_by_tex("rightarrow")
            )
        )
        self.play(
            Write(VGroup(*h_content[1:5])),
            Write(h_content.get_part_by_tex("direction")),
            run_time = 2,
        )
        self.wait(2)
        self.play(h_content.shift, 2*IN)
        self.play(
            ReplacementTransform(
                self.cos_brace.label.copy(),
                v_content[0]
            ),
            ReplacementTransform(
                self.state_equation.get_part_by_tex("uparrow").copy(),
                v_content.get_part_by_tex("uparrow")
            )
        )
        self.play(
            Write(VGroup(*v_content[1:5])),
            Write(v_content.get_part_by_tex("direction")),
            run_time = 2,
        )
        self.wait(2)
        self.play(
            FadeOut(randy),
            FadeOut(bubble),
            FadeOut(v_content),
            Transform(h_content, alt_h_content),
            FadeIn(self.pol_filter),
            Animation(self.arc)
        )
        self.play(ShowCreation(filter_lines, lag_ratio = 0))
        self.play(FadeOut(filter_lines))
        self.wait()

        self.classically = VGroup(classically, h_content)

    def reposition_camera_back(self):
        self.move_camera(
            phi = 0.8*np.pi/2, theta = -0.6*np.pi,
            added_anims = [
                FadeOut(self.h_arrow),
                FadeOut(self.h_label),
                FadeOut(self.v_arrow),
                FadeOut(self.v_label),
                FadeOut(self.d_brace),
                FadeOut(self.d_brace.label),
                FadeOut(self.arc),
                FadeOut(self.angle_label),
                Rotate(self.state_equation, np.pi/2, IN),
                Rotate(self.classically, np.pi/2, IN),
            ] + [
                Rotate(
                    v, np.pi/2, 
                    axis = v.get_vector(),
                    in_place = True,
                )
                for v in self.photon.mobject
            ],
            run_time = 1.5
        )

    def rewrite_15_percent_meaning(self):
        self.classically.rotate(np.pi/2, LEFT)
        cross = Cross(self.classically)
        cross.set_color("#ff0000")
        VGroup(self.classically, cross).rotate(np.pi/2, RIGHT)

        new_conception = TextMobject(
            "$0.38^2 = 15\\%$ chance of \\\\ getting blocked"
        )
        new_conception.scale(0.8)
        new_conception.rotate(np.pi/2, RIGHT)
        new_conception.move_to(self.classically, OUT)

        a = self.photon.rate_func(1)
        finish_photon = self.get_blocked_photon(
            rate_func = lambda t : a + (1-a)*t
        )
        finish_photon.mobject.set_fill(opacity = 0.7)

        self.play(ShowCreation(cross))
        self.classically.add(cross)
        self.play(
            self.classically.shift, 4*IN,
            FadeIn(new_conception),
        )
        self.remove(self.photon.mobject)
        self.revert_to_original_skipping_status()
        self.play(
            finish_photon,
            ApplyMethod(
                self.pol_filter.set_color, RED,
                rate_func = squish_rate_func(there_and_back, 0, 0.3),
                run_time = finish_photon.run_time
            )
        )

    def probabalistic_passing(self):
        # photons = [
        #     self.get_photon()
        #     for x in range(3)
        # ] + [self.get_blocked_photon()]
        # random.shuffle(photons)
        # for photon in photons:
        #     added_anims = []
        #     if photon.get_filtered:
        #         added_anims.append(
        #             self.get_filter_absorption_animation(
        #                 self.pol_filter, photon, 
        #             )
        #         )
        #     self.play(photon, *added_anims)
        # self.wait()

        l1 = self.get_lines(None, self.pol_filter)
        l2 = self.get_lines(self.pol_filter, None, 0.85)
        for line in it.chain(l1, l2):
            if line.get_stroke_width() > 0:
                line.set_stroke(width = 3)

        arrow = Arrow(
            2*LEFT, 2*RIGHT, 
            path_arc = 0.8*np.pi,
        )
        label = TexMobject("15\\% \\text{ absorbed}")
        label.next_to(arrow, DOWN)
        group = VGroup(arrow, label)
        group.set_color(RED)
        group.rotate(np.pi/2, RIGHT)
        group.shift(3*RIGHT + 1.5*IN)

        kwargs = {
            "rate_func" : None,
            "lag_ratio" : 0,
        }
        self.play(
            ShowCreation(arrow),
            Write(label, run_time = 1),
            ShowCreation(l1, **kwargs)
        )
        self.play(
            ShowCreation(l2, run_time = 0.5, **kwargs),
            Animation(self.pol_filter),
            Animation(l1)
        )
        self.wait()

    ###

    def get_filter_lines(self, pol_filter):
        lines = VGroup(*[
            Line(
                np.sin(a)*RIGHT + np.cos(a)*UP,
                np.sin(a)*LEFT + np.cos(a)*UP,
                color = RED,
                stroke_width = 2,
            )
            for a in np.linspace(0, np.pi, 15)
        ])
        lines.scale(pol_filter.radius)
        lines.rotate(np.pi/2, RIGHT)
        lines.rotate(np.pi/2, OUT)
        lines.shift(pol_filter.get_center()[0]*RIGHT)
        return lines

    def get_blocked_photon(self, **kwargs):
        return self.get_photon(
            filter_distance = FRAME_X_RADIUS + 3, 
            get_filtered = True,
            **kwargs
        )

class CompareWaveEquations(TeacherStudentsScene):
    def construct(self):
        self.add_equation()
        self.show_complex_plane()
        self.show_interpretations()

    def add_equation(self):
        equation = TexMobject(
            "|\\!\\psi\\rangle",
            "=", "\\alpha", "|\\!\\rightarrow\\rangle",
            "+", "\\beta", "|\\!\\uparrow\\rangle",
        )
        equation.set_color_by_tex_to_color_map({
            "psi" : BLUE,
            "rightarrow" : RED,
            "uparrow" : GREEN,
        })
        equation.next_to(ORIGIN, LEFT)
        equation.to_edge(UP)

        psi_rect = SurroundingRectangle(equation.get_part_by_tex("psi"))
        psi_rect.set_color(WHITE)
        state_words = TextMobject("Polarization \\\\ state")
        state_words.set_color(BLUE)
        state_words.scale(0.8)
        state_words.next_to(psi_rect, DOWN)

        equation.save_state()
        equation.scale(0.01)
        equation.fade(1)
        equation.move_to(self.teacher.get_left())
        equation.shift(SMALL_BUFF*UP)

        self.play(
            equation.restore,
            self.teacher.change, "raise_right_hand",
        )
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = psi_rect,
            added_anims = [
                ShowCreation(psi_rect),
                Write(state_words, run_time = 1)
            ],
            run_time = 1
        )
        self.play(FadeOut(psi_rect))

        self.equation = equation
        self.state_words = state_words

    def show_complex_plane(self):
        new_alpha, new_beta = terms = [
            self.equation.get_part_by_tex(tex).copy()
            for tex in ("alpha", "beta")
        ]
        for term in terms:
            term.save_state()
            term.generate_target()
            term.target.scale(0.7)

        plane = ComplexPlane(
            x_radius = 1.5,
            y_radius = 1.5,
        )
        plane.add_coordinates()
        plane.scale(1.3)
        plane.next_to(ORIGIN, RIGHT, MED_LARGE_BUFF)
        plane.to_edge(UP)

        alpha_dot, beta_dot = [
            Dot(
                plane.coords_to_point(x, 0.5), 
                radius = 0.05,
                color = color
            )
            for x, color in [(-0.5, RED), (0.5, GREEN)]
        ]
        new_alpha.target.next_to(alpha_dot, UP+LEFT, 0.5*SMALL_BUFF)
        new_alpha.target.set_color(RED)
        new_beta.target.next_to(beta_dot, UP+RIGHT, 0.5*SMALL_BUFF)
        new_beta.target.set_color(GREEN)

        rhs = TexMobject(
            "=", "A_y", "e", "^{i(", 
            "2\\pi", "f", "t", "+", "\\phi_y", ")}"
        )
        rhs.scale(0.7)
        rhs.next_to(new_beta.target, RIGHT, SMALL_BUFF)
        rhs.shift(0.5*SMALL_BUFF*UP)
        rhs.set_color_by_tex_to_color_map({
            "A_y" : GREEN,
            "phi" : MAROON_B,
        })
        A_copy = rhs.get_part_by_tex("A_y").copy()
        phi_copy = rhs.get_part_by_tex("phi_y").copy()
        A_line = Line(
            plane.coords_to_point(0, 0),
            plane.coords_to_point(0.5, 0.5),
            color = GREEN,
            stroke_width = 2,
        )

        arc = Arc(angle = np.pi/4, radius = 0.5)
        arc.shift(plane.get_center())

        self.play(
            Write(plane, run_time = 2),
            MoveToTarget(new_alpha),
            MoveToTarget(new_beta),
            DrawBorderThenFill(alpha_dot, run_time = 1),
            DrawBorderThenFill(beta_dot, run_time = 1),
        )
        self.play(
            Write(rhs),
            ShowCreation(A_line),
            ShowCreation(arc)
        )
        self.play(
            phi_copy.next_to, arc, RIGHT, SMALL_BUFF,
            phi_copy.shift, 0.5*SMALL_BUFF*UP
        )
        self.play(
            A_copy.next_to, A_line.get_center(), 
                UP, SMALL_BUFF,
            A_copy.shift, 0.5*SMALL_BUFF*(UP+LEFT),
        )
        self.wait()

    def show_interpretations(self):
        c_words = TexMobject(
            "\\text{Classically: }", "&|\\beta|^2",
            "\\rightarrow",
            "\\text{Component of} \\\\",
            "&\\text{energy in }", "|\\!\\uparrow\\rangle", 
            "\\text{ direction}",
        )
        qm_words = TexMobject(
            "\\text{Quantum: }", "&|\\beta|^2",
            "\\rightarrow",
            "\\text{Probability that}", "\\text{ \\emph{all}} \\\\",
            "&\\text{energy is measured in }", "|\\!\\uparrow\\rangle", 
            "\\text{ direction}",
        )
        for words in c_words, qm_words:
            words.set_color_by_tex_to_color_map({
                "Classically" : YELLOW,
                "Quantum" : BLUE,
                "{all}" : BLUE,
                "beta" : GREEN,
                "uparrow" : GREEN,
            })
            words.scale(0.7)
        c_words.to_edge(LEFT)
        c_words.shift(2*UP)
        qm_words.next_to(c_words, DOWN, MED_LARGE_BUFF, LEFT)

        self.play(
            FadeOut(self.state_words),
            Write(c_words),
            self.teacher.change, "happy"
        )
        self.change_student_modes(
            *["happy"]*3, look_at_arg = c_words
        )
        self.play(Write(qm_words))
        self.change_student_modes(
            "erm", "confused", "pondering",
            look_at_arg = qm_words
        )
        self.wait()

class CircularPhotons(ShootPhotonThroughFilter):
    CONFIG = {
        "EMWave_config" : {
            "phi_vect" : [0, -np.pi/2, 0],
            "wave_number" : 1,
            "start_point" : 10*LEFT,
            "length" : 20,
            "n_vectors" : 60,
        },
        "apply_filter" : False,
    }
    def construct(self):
        self.set_camera_orientation(theta = -0.75*np.pi)
        self.setup_filter()
        self.show_phase_difference()
        self.shoot_circular_photons()
        self.show_filter()
        self.show_vertically_polarized_light()

    def setup_filter(self):
        pf = self.pol_filter
        pf.remove(pf.label)
        pf.remove(pf.arrow)
        self.remove(pf.label, pf.arrow)
        arrows = VGroup(*[
            Arrow(
                v1, v2,
                color = WHITE,
                path_arc = np.pi,
            )
            for v1, v2 in [(LEFT, RIGHT), (RIGHT, LEFT)]
        ])
        arrows.scale(0.7)
        arrows.rotate(np.pi/2, RIGHT)
        arrows.rotate(np.pi/2, OUT)
        arrows.move_to(center_of_mass(pf.points))

        pf.label = arrows
        pf.add(arrows)
        self.remove(pf)

    def show_phase_difference(self):
        equation = TexMobject(
            "|\\!\\circlearrowright\\rangle", 
            "=", "\\frac{1}{\\sqrt{2}}", "|\\!\\rightarrow\\rangle",
            "+", "\\frac{i}{\\sqrt{2}}", "|\\!\\uparrow\\rangle",
        )
        equation.set_color_by_tex_to_color_map({
            "circlearrowright" : BLUE,
            "rightarrow" : RED,
            "uparrow" : GREEN,
        })
        equation.next_to(ORIGIN, LEFT, LARGE_BUFF)
        equation.to_edge(UP)
        rect = SurroundingRectangle(equation.get_part_by_tex("frac{i}"))
        words = TextMobject("Phase shift")
        words.next_to(rect, DOWN)
        words.set_color(YELLOW)

        group = VGroup(equation, rect, words)
        group.rotate(np.pi/2, RIGHT)
        group.rotate(np.pi/4, IN)

        self.play(FadeIn(equation))
        self.play(self.get_circular_photon())
        self.play(
            ShowCreation(rect),
            Write(words, run_time = 1)
        )

        self.circ_equation_group = group

    def shoot_circular_photons(self):
        for x in range(2):
            self.play(self.get_circular_photon())

    def show_filter(self):
        pf = self.pol_filter
        pf.save_state()
        pf.shift(4*OUT)
        pf.fade(1)

        self.play(pf.restore)
        self.play(
            self.get_circular_photon(),
            Animation(self.circ_equation_group)
        )
        self.play(FadeOut(self.circ_equation_group))

    def show_vertically_polarized_light(self):
        equation = TexMobject(
            "|\\!\\uparrow \\rangle", 
            "=", "\\frac{i}{\\sqrt{2}}", "|\\!\\circlearrowleft \\rangle",
            "+", "\\frac{-i}{\\sqrt{2}}", "|\\!\\circlearrowright \\rangle",
        )
        equation.set_color_by_tex_to_color_map({
            "circlearrowright" : BLUE,
            "frac{-i}" : BLUE,
            "circlearrowleft" : YELLOW,
            "frac{i}" : YELLOW,
            "uparrow" : GREEN,
        })
        equation.next_to(ORIGIN, LEFT, LARGE_BUFF)
        equation.to_edge(UP)

        prob = TexMobject(
            "P(", "\\text{passing}", ")",
            "=", "\\left(", "\\frac{-i}{\\sqrt{2}}", "\\right)^2"
        )
        prob.set_color_by_tex("sqrt{2}", BLUE)
        prob.next_to(equation, DOWN)

        group = VGroup(equation, prob)
        group.rotate(np.pi/2, RIGHT)
        group.rotate(np.pi/4, IN)

        em_wave = EMWave(
            wave_number = 0,
            amplitude = 2,
            start_point = 10*LEFT,
            length = 20,
        )
        v_photon = WavePacket(
            em_wave = em_wave, 
            include_M_vects = False,
            run_time = 2
        )
        c_photon = self.get_circular_photon()
        for v_vect in v_photon.mobject:
            v_vect.saved_state.set_fill(GREEN)
            if v_vect.get_start()[0] > 0:
                v_vect.saved_state.set_fill(opacity = 0)
        for c_vect in c_photon.mobject:
            if c_vect.get_start()[0] < 0:
                c_vect.saved_state.set_fill(opacity = 0)
        blocked_v_photon = copy.deepcopy(v_photon)
        blocked_v_photon.get_filtered = True
        blocked_v_photon.filter_distance = 10

        self.play(Write(equation, run_time = 1))
        self.play(v_photon, c_photon)
        self.play(FadeIn(prob))
        bools = 3*[True] + 3*[False]
        random.shuffle(bools)
        for should_pass in bools:
            if should_pass:
                self.play(v_photon, c_photon)
            else:
                self.play(
                    blocked_v_photon,
                    self.get_filter_absorption_animation(
                        self.pol_filter, blocked_v_photon
                    )
                )
        self.wait()

    ####

    def get_circular_photon(self, **kwargs):
        kwargs["run_time"] = kwargs.get("run_time", 2)
        photon = ShootPhotonThroughFilter.get_photon(self, **kwargs)
        photon.E_func = lambda x : np.exp(-0.25*(2*np.pi*x/photon.width)**2)
        return photon

class ClockwisePhotonInsert(Scene):
    def construct(self):
        eq = TexMobject(
            "\\left| \\frac{-i}{\\sqrt{2}} \\right|^2"
        )
        eq.set_color(BLUE)
        VGroup(*it.chain(eq[:4], eq[-5:])).set_color(WHITE)
        eq.set_height(FRAME_HEIGHT - 1)
        eq.to_edge(LEFT)
        self.add(eq)

class OrClickHere(Scene):
    def construct(self):
        words = TextMobject("Or click here")
        words.scale(3)
        arrow = Vector(
            2*UP + 2*RIGHT,
            rectangular_stem_width = 0.1,
            tip_length = 0.5
        )
        arrow.next_to(words, UP).shift(RIGHT)

        self.play(
            Write(words),
            ShowCreation(arrow)
        )
        self.wait()

class WavesPatreonThanks(PatreonThanks):
    CONFIG = {
        "specific_patrons" : [
            "Desmos",
            "CrypticSwarm",
            "Burt Humburg",
            "Charlotte",
            "Juan Batiz-Benet",
            "Ali Yahya",
            "William",
            "Mayank M. Mehrotra",
            "Lukas Biewald",
            "Samantha D. Suplee",
            "James Park",
            "Yana Chernobilsky",
            "Kaustuv DeBiswas",
            "Kathryn Schmiedicke",
            "Yu Jun",
            "dave nicponski",
            "Damion Kistler",
            "Markus Persson",
            "Yoni Nazarathy",
            "Ed Kellett",
            "Joseph John Cox",
            "Dan Rose",
            "Luc Ritchie",
            "Harsev Singh",
            "Mads Elvheim",
            "Erik Sundell",
            "Xueqi Li",
            "David G. Stork",
            "Tianyu Ge",
            "Ted Suzman",
            "Linh Tran",
            "Andrew Busey",
            "Michael McGuffin",
            "John Haley",
            "Ankalagon",
            "Eric Lavault",
            "Boris Veselinovich",
            "Julian Pulgarin",
            "Jeff Linse",
            "Cooper Jones",
            "Ryan Dahl",
            "Mark Govea",
            "Robert Teed",
            "Jason Hise",
            "Meshal Alshammari",
            "Bernd Sing",
            "Nils Schneider",
            "James Thornton",
            "Mustafa Mahdi",
            "Mathew Bramson",
            "Jerry Ling",
            "Vecht",
            "Shimin Kuang",
            "Rish Kundalia",
            "Achille Brighton",
            "Ripta Pasay",
        ],
    }

class Footnote(Scene):
    def construct(self):
        words = TextMobject("""
            \\begin{flushleft}
            \\Large
            By the way, in the quantum mechanical description
            of polarization, states are written like 
            $|\\! \\leftrightarrow \\rangle$ with a double-headed
            arrow, rather than $|\\! \\rightarrow \\rangle$ with
            a single-headed arrow.  This conveys how there's no distinction
            between left and right; they each have the same measurable 
            state: horizontal. \\\\
            \\quad \\\\
            Because of how I chose to motivate things with classical waves,
            I'll stick with the single-headed $|\\! \\rightarrow \\rangle$
            for this video, but just keep in mind that this differs
            from quantum mechanics conventions.
            \\end{flushleft}
        """)
        words.set_width(FRAME_WIDTH - 2)
        self.add(words)











