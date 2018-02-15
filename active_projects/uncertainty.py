from helpers import *
import scipy

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from animation.continual_animation import *
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
from topics.common_scenes import *
from scene import Scene
from scene.reconfigurable_scene import ReconfigurableScene
from scene.zoomed_scene import *
from camera import Camera
from mobject import *
from mobject.image_mobject import *
from mobject.vectorized_mobject import *
from mobject.svg_mobject import *
from mobject.tex_mobject import *
from topics.graph_scene import *

from active_projects.fourier import *


FREQUENCY_COLOR = RED
USE_ALMOST_FOURIER_BY_DEFAULT = False

class GaussianDistributionWrapper(Line):
    """
    This is meant to encode a 2d normal distribution as
    a mobject (so as to be able to have it be interpolated
    during animations).  It is a line whose center is the mean
    mu of a distribution, and whose radial vector (center to end)
    is the distribution's standard deviation
    """
    CONFIG = {
        "stroke_width" : 0,
        "mu" : ORIGIN,
        "sigma" : RIGHT,
    }
    def __init__(self, **kwargs):
        Line.__init__(self, ORIGIN, RIGHT, **kwargs)
        self.change_parameters(self.mu, self.sigma)

    def change_parameters(self, mu = None, sigma = None):
        curr_mu, curr_sigma = self.get_parameters()
        mu = mu if mu is not None else curr_mu
        sigma = sigma if sigma is not None else curr_sigma
        self.put_start_and_end_on(mu - sigma, mu + sigma)
        return self

    def get_parameters(self):
        """ Return mu_x, mu_y, sigma_x, sigma_y"""
        center, end = self.get_center(), self.get_end()
        return center, end-center

    def get_random_points(self, size = 1):
        mu, sigma = self.get_parameters()
        return np.array([
            np.array([
                np.random.normal(mu_coord, sigma_coord)
                for mu_coord, sigma_coord in zip(mu, sigma)
            ])
            for x in range(size)
        ])

class ProbabalisticMobjectCloud(ContinualAnimation):
    CONFIG = {
        "fill_opacity" : 0.25,
        "n_copies" : 100,
        "gaussian_distribution_wrapper_config" : {}
    }
    def __init__(self, prototype, **kwargs):
        digest_config(self, kwargs)
        fill_opacity = self.fill_opacity or prototype.get_fill_opacity()
        self.gaussian_distribution_wrapper = GaussianDistributionWrapper(
            **self.gaussian_distribution_wrapper_config
        )
        group = VGroup(*[
            prototype.copy().set_fill(opacity = fill_opacity)
            for x in range(self.n_copies)
        ])
        ContinualAnimation.__init__(self, group, **kwargs)

    def update_mobject(self, dt):
        group = self.mobject
        points = self.gaussian_distribution_wrapper.get_random_points(len(group))
        for mob, point in zip(group, points):
            self.update_mobject_by_point(mob, point)
        return self

    def update_mobject_by_point(self, mobject, point):
        mobject.move_to(point)
        return self

class ProbabalisticDotCloud(ProbabalisticMobjectCloud):
    CONFIG = {
        "color" : BLUE,
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        dot = Dot(color = self.color)
        ProbabalisticMobjectCloud.__init__(self, dot)

class ProbabalisticVectorCloud(ProbabalisticMobjectCloud):
    CONFIG = {
        "color" : RED,
        "n_copies" : 20,
        "fill_opacity" : 0.5,
        "center_func" : lambda : ORIGIN,
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        vector = Vector(
            RIGHT, color = self.color,
            max_tip_length_to_length_ratio = 1,
        )
        ProbabalisticMobjectCloud.__init__(self, vector)

    def update_mobject_by_point(self, vector, point):
        vector.put_start_and_end_on(
            self.center_func(),
            point
        )

class RadarDish(SVGMobject):
    CONFIG = {
        "file_name" : "radar_dish",
        "fill_color" : LIGHT_GREY,
        "stroke_color" : WHITE,
        "stroke_width" : 1,
        "height" : 1,
    }

class Plane(SVGMobject):
    CONFIG = {
        "file_name" : "plane",
        "color" : GREY,
        "height" : 1,
    }
    def __init__(self, **kwargs):
        SVGMobject.__init__(self, **kwargs)
        self.rotate(-TAU/8)

class RadarPulseSingleton(ContinualAnimation):
    CONFIG = {
        "speed" : 3.0,
        "direction" : RIGHT,
        "start_up_time" : 0,
        "fade_in_time" : 0.5,
        "color" : WHITE,
        "stroke_width" : 3,
    }
    def __init__(self, radar_dish, target, **kwargs):
        digest_config(self, kwargs)
        self.direction = self.direction/np.linalg.norm(self.direction)
        self.radar_dish = radar_dish
        self.target = target
        self.reflection_distance = None
        self.arc = Arc(
            start_angle = -30*DEGREES,
            angle = 60*DEGREES,
        )
        self.arc.scale_to_fit_height(0.75*radar_dish.get_height())
        self.arc.move_to(radar_dish, UP+RIGHT)
        self.start_points = np.array(self.arc.points)
        self.start_center = self.arc.get_center()
        self.finished = False

        ContinualAnimation.__init__(self, self.arc, **kwargs)
        
    def update_mobject(self, dt):
        arc = self.arc
        total_distance = self.speed*self.internal_time
        arc.points = np.array(self.start_points)
        arc.shift(total_distance*self.direction)

        if self.internal_time < self.fade_in_time:
            alpha = np.clip(self.internal_time/self.fade_in_time, 0, 1)
            arc.set_stroke(self.color, alpha*self.stroke_width)

        if self.reflection_distance is None:
            #Check if reflection is happening
            arc_point = arc.get_edge_center(self.direction)
            target_point = self.target.get_edge_center(-self.direction)
            arc_distance = np.dot(arc_point, self.direction)
            target_distance = np.dot(target_point, self.direction)
            if arc_distance > target_distance:
                self.reflection_distance = target_distance
        #Don't use elif in case the above code creates reflection_distance
        if self.reflection_distance is not None:
            delta_distance = total_distance - self.reflection_distance
            point_distances = np.dot(self.direction, arc.points.T)
            diffs = point_distances - self.reflection_distance
            shift_vals = np.outer(-2*np.maximum(diffs, 0), self.direction)
            arc.points += shift_vals

            #Check if done
            arc_point = arc.get_edge_center(-self.direction)
            if np.dot(arc_point, self.direction) < np.dot(self.start_center, self.direction):
                self.finished = True
                self.arc.fade(1)

    def is_finished(self):
        return self.finished

class RadarPulse(ContinualAnimation):
    CONFIG = {
        "n_pulse_singletons" : 8,
        "frequency" : 0.05,
        "colors" : [BLUE, YELLOW]
    }
    def __init__(self, *args, **kwargs):
        digest_config(self, kwargs)
        colors = color_gradient(self.colors, self.n_pulse_singletons)
        self.pulse_singletons = [
            RadarPulseSingleton(*args, color = color, **kwargs)
            for color in colors
        ]
        pluse_mobjects = VGroup(*[ps.mobject for ps in self.pulse_singletons])
        ContinualAnimation.__init__(self, pluse_mobjects, **kwargs)
        
    def update_mobject(self, dt):
        for i, ps in enumerate(self.pulse_singletons):
            ps.internal_time = self.internal_time - i*self.frequency
            ps.update_mobject(dt)

    def is_finished(self):
        return all([ps.is_finished() for ps in self.pulse_singletons])

###################

class MentionUncertaintyPrinciple(TeacherStudentsScene):
    def construct(self):
        title = TextMobject("Heisenberg Uncertainty Principle")
        title.to_edge(UP)

        dot_cloud = ProbabalisticDotCloud()
        vector_cloud = ProbabalisticVectorCloud(
            gaussian_distribution_wrapper_config = {"sigma_x" : 0.2},
            center_func = lambda : dot_cloud.gaussian_distribution_wrapper.get_parameters()[0],
        )
        for cloud in dot_cloud, vector_cloud:
            cloud.gaussian_distribution_wrapper.next_to(
                title, DOWN, 2*LARGE_BUFF
            )
        vector_cloud.gaussian_distribution_wrapper.shift(3*RIGHT)

        def get_brace_text_group_update(gdw, vect, text, color):
            brace = Brace(gdw, vect)
            text = brace.get_tex("2\\sigma_{\\text{%s}}"%text, buff = SMALL_BUFF)
            group = VGroup(brace, text)
            def update_group(group):
                brace, text = group
                brace.match_width(gdw, stretch = True)
                brace.next_to(gdw, vect)
                text.next_to(brace, vect, buff = SMALL_BUFF)
            group.highlight(color)
            return ContinualUpdateFromFunc(group, update_group)

        dot_brace_anim = get_brace_text_group_update(
            dot_cloud.gaussian_distribution_wrapper,
            DOWN, "position", dot_cloud.color
        )
        vector_brace_anim = get_brace_text_group_update(
            vector_cloud.gaussian_distribution_wrapper,
            UP, "momentum", vector_cloud.color
        )

        self.add(title)
        self.add(dot_cloud)
        self.play(
            Write(title),
            self.teacher.change, "raise_right_hand",
            self.get_student_changes(*["pondering"]*3)
        )
        self.play(
            Write(dot_brace_anim.mobject, run_time = 1)
        )
        self.add(dot_brace_anim)
        self.wait()
        # self.wait(2)
        self.play(
            dot_cloud.gaussian_distribution_wrapper.change_parameters, 
            {"sigma" : 0.1*RIGHT},
            run_time = 2,
        )
        self.wait()
        self.add(vector_cloud)
        self.play(
            FadeIn(vector_brace_anim.mobject)
        )
        self.add(vector_brace_anim)
        self.play(
            vector_cloud.gaussian_distribution_wrapper.change_parameters,
            {"sigma" : RIGHT},
            self.get_student_changes(*3*["confused"]),
            run_time = 3,
        )
        #Back and forth
        for x in range(2):
            self.play(
                dot_cloud.gaussian_distribution_wrapper.change_parameters,
                {"sigma" : 2*RIGHT},
                vector_cloud.gaussian_distribution_wrapper.change_parameters,
                {"sigma" : 0.1*RIGHT},
                run_time = 3,
            )
            self.change_student_modes("thinking", "erm", "sassy")
            self.play(
                dot_cloud.gaussian_distribution_wrapper.change_parameters,
                {"sigma" : 0.1*RIGHT},
                vector_cloud.gaussian_distribution_wrapper.change_parameters,
                {"sigma" : 1*RIGHT},
                run_time = 3,
            )
            self.wait()

class FourierTradeoff(Scene):
    def construct(self):
        #Setup axes
        time_mean = 4
        time_axes = Axes(
            x_min = 0,
            x_max = 2*time_mean,
            x_axis_config = {"unit_size" : 1.5},
            y_min = -2, 
            y_max = 2,
            y_axis_config = {"unit_size" : 0.5}
        )
        time_label = TextMobject("Time")
        time_label.next_to(
            time_axes.x_axis.get_right(), UP,
            buff = MED_SMALL_BUFF,
        )
        time_axes.add(time_label)
        time_axes.center().to_edge(UP)
        time_axes.x_axis.add_numbers(*range(1, 2*time_mean))

        frequency_axes = Axes(
            x_min = 0,
            x_max = 8,
            x_axis_config = {"unit_size" : 1.5},
            y_min = 0,
            y_max = 15,
            y_axis_config = {
                "unit_size" : 0.15,
                "tick_frequency" : 5,
            },
            color = TEAL,
        )
        frequency_label = TextMobject("Frequency")
        frequency_label.next_to(
            frequency_axes.x_axis.get_right(), UP,
            buff = MED_SMALL_BUFF, 
        )
        frequency_label.highlight(FREQUENCY_COLOR)
        frequency_axes.add(frequency_label)
        frequency_axes.move_to(time_axes, LEFT)
        frequency_axes.to_edge(DOWN, buff = LARGE_BUFF)
        frequency_axes.x_axis.add_numbers()

        # Graph information

        #x-coordinate of this point determines width of wave_packet graph
        width_tracker = VectorizedPoint(0.5*RIGHT)
        def get_width():
            return width_tracker.get_center()[0]

        def get_wave_packet_function():
            factor = 1./get_width()
            return lambda t : np.sqrt(factor)*np.cos(4*TAU*t)*np.exp(-factor*(t-time_mean)**2)

        def get_wave_packet():
            graph = time_axes.get_graph(
                get_wave_packet_function(),
                num_graph_points = 200,
            )
            graph.highlight(YELLOW)
            return graph

        time_radius = 10
        def get_wave_packet_fourier_transform():
            return get_fourier_graph(
                frequency_axes, get_wave_packet_function(),
                t_min = time_mean - time_radius,
                t_max = time_mean + time_radius,
                n_samples = 2*time_radius*17,
                # complex_to_real_func = abs,
                complex_to_real_func = lambda z : z.real,
                color = FREQUENCY_COLOR,
            )

        wave_packet = get_wave_packet()
        wave_packet_update = UpdateFromFunc(
            wave_packet, 
            lambda g : Transform(g, get_wave_packet()).update(1)
        )
        fourier_graph = get_wave_packet_fourier_transform()
        fourier_graph_update = UpdateFromFunc(
            fourier_graph, 
            lambda g : Transform(g, get_wave_packet_fourier_transform()).update(1)
        )

        arrow = Arrow(
            wave_packet, frequency_axes.coords_to_point(4, 10),
            color = FREQUENCY_COLOR,
        )
        fourier_words = TextMobject("Fourier Transform")
        fourier_words.next_to(arrow, RIGHT, buff = MED_LARGE_BUFF)
        sub_words = TextMobject("(To be explained shortly)")
        sub_words.highlight(BLUE)
        sub_words.scale(0.75)
        sub_words.next_to(fourier_words, DOWN)

        #Draw items
        self.add(time_axes, frequency_axes)
        self.play(ShowCreation(wave_packet, rate_func = double_smooth))
        self.play(
            ReplacementTransform(
                wave_packet.copy(),
                fourier_graph,
            ),
            GrowArrow(arrow),
            Write(fourier_words, run_time = 1)
        )
        # self.play(FadeOut(arrow))
        self.wait()
        for width in 6, 0.1, 1:
            self.play(
                width_tracker.move_to, width*RIGHT,
                wave_packet_update,
                fourier_graph_update,
                run_time = 3
            )
            if sub_words not in self.mobjects:
                self.play(FadeIn(sub_words))
            else:
                self.wait()
        self.wait()

class ShowPlan(PiCreatureScene):
    def construct(self):
        self.add_title()
        words = self.get_words()
        self.play_sound_anims(words[0])
        self.play_doppler_anims(words[1], words[0])
        self.play_quantum_anims(words[2], words[1])

    def add_title(self):
        title = TextMobject("The plan")
        title.scale(1.5)
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT).scale(SPACE_WIDTH)
        h_line.next_to(title, DOWN)
        self.add(title, h_line)

    def get_words(self):
        colors = [YELLOW, GREEN, BLUE]
        topics = ["sound waves", "Doppler radar", "quantum particles"]
        words = VGroup()
        for topic, color in zip(topics, colors):
            word = TextMobject("Uncertainty for", topic)
            word[1].highlight(color)
            words.add(word)
        words.arrange_submobjects(DOWN, aligned_edge = LEFT, buff = LARGE_BUFF)
        words.to_edge(LEFT)

        return words

    def play_sound_anims(self, word):
        morty = self.pi_creature
        wave = FunctionGraph(
            lambda x : 0.3*np.sin(15*x)*np.sin(0.5*x),
            x_min = 0, x_max = 30,
            num_anchor_points = 500,
        )
        wave.next_to(word, RIGHT)
        rect = BackgroundRectangle(wave, fill_opacity = 1)
        rect.stretch(2, 1)
        rect.next_to(wave, LEFT, buff = 0)
        wave_shift = AmbientMovement(
            wave, direction = LEFT, rate = 5
        )
        wave_fader = UpdateFromAlphaFunc(
            wave, 
            lambda w, a : w.set_stroke(width = 3*a)
        )
        checkmark = self.get_checkmark(word)

        self.add(wave_shift)
        self.add_foreground_mobjects(rect, word)
        self.play(
            Animation(word),
            wave_fader,
            morty.change, "raise_right_hand", word
        )
        self.wait(2)
        wave_fader.rate_func = lambda a : 1-smooth(a)
        self.add_foreground_mobjects(checkmark)
        self.play(
            Write(checkmark),
            morty.change, "happy",
            wave_fader, 
        )
        self.remove_foreground_mobjects(rect, word)
        self.add(word)
        self.wait()

    def play_doppler_anims(self, word, to_fade):
        morty = self.pi_creature

        radar_dish = RadarDish()
        radar_dish.next_to(word, DOWN, aligned_edge = LEFT)
        target = Plane()
        # target.match_height(radar_dish)
        target.next_to(radar_dish, RIGHT, buff = LARGE_BUFF)
        target_movement = AmbientMovement(target, direction = RIGHT, rate = 1.25)

        pulse = RadarPulse(radar_dish, target)

        checkmark = self.get_checkmark(word)

        self.add(target_movement)
        self.play(
            to_fade.fade, 0.5,
            Write(word),
            DrawBorderThenFill(radar_dish),
            UpdateFromAlphaFunc(
                target, lambda m, a : m.set_fill(opacity = a)
            ),
            morty.change, "pondering",
            run_time = 1
        )
        self.wait()
        self.add(pulse)
        count = it.count() #TODO, this is not a great hack...
        while not pulse.is_finished() and count.next() < 15:
            self.play(
                morty.look_at, pulse.mobject,
                run_time = 0.5
            )
        self.play(
            Write(checkmark),
            UpdateFromAlphaFunc(
                target, lambda m, a : m.set_fill(opacity = 1-a)
            ),
            FadeOut(radar_dish),
            morty.change, "happy"
        )
        self.wait()




    def play_quantum_anims(self, word, to_fade):
        pass

    ##

    def get_checkmark(self, word):
        checkmark = TexMobject("\\checkmark")
        checkmark.highlight(GREEN)
        checkmark.scale(1.5)
        checkmark.next_to(word, UP+RIGHT, buff = 0)
        return checkmark




































