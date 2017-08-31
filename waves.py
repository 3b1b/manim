from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.continual_animation import *
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

E_COLOR = BLUE
M_COLOR = YELLOW

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
        "start_point" : SPACE_WIDTH*LEFT + DOWN + OUT,
        "length" : 2*SPACE_WIDTH,
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

        self.A_vect = np.array(self.A_vect)/np.linalg.norm(self.A_vect)
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
                norm = np.linalg.norm(ov.A_vect)
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
            "start_point" : SPACE_WIDTH*LEFT,
            "phi_vect" : np.ones(3)*np.pi/4,
        },
        "em_wave" : None,
        "run_time" : 4,
        "rate_func" : None,
        "packet_width" : 6,
        "include_E_vects" : True,
        "include_M_vects" : True,
        "filter_distance" : SPACE_WIDTH,
        "get_filtered" : False,
        "remover" : True,
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

    def update_mobject(self, alpha):
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
            distance_from_start = np.linalg.norm(tail - em_wave.start_point)
            if self.get_filtered and distance_from_start > self.filter_distance:
                A = 0
            vect.restore()
            vect.scale(A/vect.get_length(), about_point = tail)

    def E_func(self, x):
        return np.sin(x)*np.exp(-0.25*x*x)

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
        electric.highlight(BLUE)

        title.save_state()
        title.shift(DOWN)
        title.fade(1)

        self.play(
            title.restore,
            morty.change, "raise_right_hand",
        )
        self.play(
            title[0].highlight, BLUE,
            title[1].highlight, YELLOW,
        )
        self.dither()
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
            LaggedStart(
                ShowCreation, vector_field, 
                run_time = 3
            ),
            self.title.center,
            self.title.scale, 1.5,
            self.title.to_edge, UP,
            morty.change, "happy", ORIGIN,
        )
        self.dither()

        self.vector_field = vector_field

    def add_particle(self):
        morty = self.pi_creature
        point = UP+LEFT + SMALL_BUFF*(UP+RIGHT)
        particle = self.get_particle()
        particle.move_to(point)

        vector = self.get_vector(particle.get_center())
        vector.highlight(RED)
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
        self.dither(2)

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
            LaggedStart(FadeIn, VGroup(*particles[1:]))
        )
        self.moving_particles = particles
        self.add_foreground_mobjects(self.moving_particles, self.pi_creature)
        self.always_continually_update = True
        self.dither(10)

    ###

    def continual_update(self):
        Scene.continual_update(self)
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
            lambda m1, m2 : cmp(m1.get_length(), m2.get_length())
        )
        VGroup(*shading_list).gradient_highlight(*self.vector_field_colors)
        result.set_fill(opacity = 0.75)
        result.sort_submobjects(np.linalg.norm)

        return result

    def get_vector(self, point):
        return Vector(self.field_function(point)).shift(point)

    def field_function(self, point):
        x, y = point[:2]
        result = y*RIGHT + np.sin(x)*UP
        return self.normalized(result)

    def normalized(self, vector):
        norm = np.linalg.norm(vector) or 1
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
        self.set_camera_position(0.1, -np.pi/2)
        self.add_title()
        self.add_vector_field()
        self.introduce_moving_charge()
        self.show_force()
        # self.many_charges()

    def add_title(self):
        title = TextMobject("Magnetic", "field")
        title[0].highlight(YELLOW)
        title.scale(1.5)
        title.to_edge(UP)
        title.add_background_rectangle()

        self.add(title)
        self.title = title

    def add_vector_field(self):
        vector_field = self.get_vector_field()

        self.play(
            LaggedStart(ShowCreation, vector_field, run_time = 3),
            Animation(self.title)
        )
        self.dither()

    def introduce_moving_charge(self):
        point = 3*RIGHT + UP
        particle = self.get_particle()
        particle.move_to(point)

        velocity = Vector(2*RIGHT).shift(particle.get_right())
        velocity.highlight(WHITE)
        velocity_word = TextMobject("Velocity")
        velocity_word.highlight(velocity.get_color())
        velocity_word.add_background_rectangle()
        velocity_word.next_to(velocity, UP, 0, LEFT)

        M_vect = self.get_vector(point)
        M_vect.highlight(YELLOW)
        M_vect.shift(SMALL_BUFF*M_vect.get_vector())

        particle.save_state()
        particle.shift(2*SPACE_WIDTH*LEFT)

        self.play(
            particle.restore,
            run_time = 2,
            rate_func = None,
        )
        self.add(velocity)
        self.play(Write(velocity_word, run_time = 0.5))
        # self.play(ShowCreation(M_vect))
        self.dither()

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
        F_word.highlight(F_vect.get_color())
        F_eq = TexMobject(
            "=","q", "\\textbf{v}", "\\times", "\\textbf{B}"
        )
        F_eq.highlight_by_tex_to_color_map({
            "q" : RED,
            "B" : YELLOW,
        })
        F_eq.rotate(np.pi/2, RIGHT)
        F_eq.next_to(F_word, RIGHT)


        self.move_camera(0.8*np.pi/2, -0.55*np.pi)
        self.begin_ambient_camera_rotation()
        self.play(ShowCreation(F_vect))
        self.play(Write(F_word))
        self.dither()
        self.play(Write(F_eq))
        self.dither(8)

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
        self.dither(5)

        
    ###

    def continual_update(self):
        Scene.continual_update(self)
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
        self.add(ThreeDAxes(x_axis_radius = SPACE_WIDTH))

    def loop_in_E(self):
        E_vects = VGroup(*[
            Vector(0.5*rotate_vector(vect, np.pi/2)).shift(vect)
            for vect in compass_directions(8)
        ])
        E_vects.highlight(E_COLOR)
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
        self.dither()
        self.move_camera(0.8*np.pi/2, -0.45*np.pi)
        self.begin_ambient_camera_rotation()
        self.play(M_vect.restore, run_time = 3, rate_func = None)
        self.dither(3)

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
            *map(FadeOut, self.E_vects[1:])
        )
        self.dither()
        self.play(
            E_vect.rotate, np.pi, RIGHT, [], new_point,
            E_vect.scale_about_point, 3, new_point,
            run_time = 4,
            rate_func = None,
        )
        self.dither()

        self.M_circle_center = new_point
        M_vects.add(self.M_vect)
        self.M_vects = M_vects
        self.E_vect = E_vect

    def second_loop_in_E(self):
        E_vects = VGroup(*[
            Vector(1.5*rotate_vector(vect, np.pi/2)).shift(vect)
            for vect in compass_directions(8, LEFT)[1:]
        ])
        E_vects.highlight(E_COLOR)
        point = self.M_circle_center + RIGHT
        E_vects.shift(point)

        M_vect = self.M_vects[3]
        self.M_vects.remove(M_vect)

        self.play(FadeOut(self.M_vects))
        self.play(ShowCreation(E_vects), Animation(M_vect))
        self.play(
            M_vect.rotate, np.pi, RIGHT, [], point,
            run_time = 5,
            rate_func = None,
        )
        self.dither(3)


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
        footnote = TextMobject("*Ignoring currents")
        footnote.scale(0.7)
        eqs = VGroup(eq1, eq2, footnote)
        eqs.arrange_submobjects(DOWN, buff = LARGE_BUFF)
        eqs.scale_to_fit_height(2*SPACE_HEIGHT - 1)
        for eq in eqs:
            eq.highlight_by_tex_to_color_map({
                "E" : E_COLOR,            
                "B" : M_COLOR,
            })

        self.play(Write(eq1, run_time = 2))
        self.dither(3)
        self.play(Write(eq2, run_time = 2))
        self.play(FadeIn(footnote))
        self.dither(3)

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
        self.set_camera_position(0.8*np.pi/2, -0.7*np.pi)
        self.begin_ambient_camera_rotation()

    def construct(self):
        words = TextMobject(
            "Electro", "magnetic", " radiation",
            arg_separator = ""
        )
        words.highlight_by_tex_to_color_map({
            "Electro" : E_COLOR,
            "magnetic" : M_COLOR,
        })
        words.next_to(ORIGIN, LEFT, MED_LARGE_BUFF)
        words.to_edge(UP)
        words.rotate(np.pi/2, RIGHT)

        self.dither(7)
        self.play(Write(words, run_time = 2))
        self.dither(20)

    #####

class SimpleEMWave(IntroduceEMWave):
    def construct(self):
        self.dither(30)

class ListRelevantWaveIdeas(TeacherStudentsScene):
    def construct(self):
        title = TextMobject("Wave","topics")
        title.to_corner(UP + LEFT, LARGE_BUFF)
        title.highlight(BLUE)
        h_line = Line(title.get_left(), title.get_right())
        h_line.next_to(title, DOWN, SMALL_BUFF)

        topics = VGroup(*map(TextMobject, [
            "- Superposition",
            "- Amplitudes",
            "- Phase influences addition",
        ]))
        topics.scale(0.8)
        topics.arrange_submobjects(DOWN, aligned_edge = LEFT)
        topics.next_to(h_line, DOWN, aligned_edge = LEFT)

        quantum = TextMobject("Quantum")
        quantum.highlight(GREEN)
        quantum.move_to(title[0], LEFT)

        wave_point = self.teacher.get_corner(UP+LEFT) + 2*UP
        self.play(
            Animation(VectorizedPoint(wave_point)),
            self.teacher.change, "raise_right_hand"
        )
        self.dither(2)
        self.play(
            Write(title, run_time = 2),
            ShowCreation(h_line)
        )
        self.change_student_modes(
            *["pondering"]*3,
            added_anims = [LaggedStart(
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
        self.dither(5)

class DirectWaveOutOfScreen(IntroduceEMWave):
    CONFIG = {
        "EMWave_config" : {
            "requires_start_up" : False,
            "amplitude" : 2,
            "start_point" : SPACE_WIDTH*LEFT,
            "A_vect" : [0, 1, 0],
            "start_up_time" : 0,
        }
    }
    def setup(self):
        IntroduceEMWave.setup(self)
        self.remove(self.axes)
        for ov in self.em_wave.continual_animations:
            ov.vector.normal_vector = RIGHT
        self.set_camera_position(0.9*np.pi/2, -0.3*np.pi)

    def construct(self):
        self.move_into_position()

    def move_into_position(self):
        self.dither(2)
        self.continual_update()
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
        self.play(
            self.em_wave.M_vects.set_fill, None, 0
        )
        self.dither(2)
        self.play(faded_vectors.set_fill, None, 0)
        self.dither(4)

class ShowVectorEquation(Scene):
    def construct(self):
        self.force_skipping()

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
        self.revert_to_original_skipping_status()        
        self.dither(3)

    def add_plane(self):
        pass

    def write_horizontally_polarized(self):
        pass

    def write_components(self):
        pass

    def show_graph(self):
        pass

    def add_phi(self):
        pass

    def add_amplitude(self):
        pass

    def add_kets(self):
        pass

    def switch_to_vertically_polarized_light(self):
        pass
























