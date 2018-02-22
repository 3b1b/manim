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
from topics.light import *

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
        if "mu" not in self.gaussian_distribution_wrapper_config:
            self.gaussian_distribution_wrapper_config["mu"] = prototype.get_center()
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
        "color" : LIGHT_GREY,
        "height" : 1,
    }
    def __init__(self, **kwargs):
        SVGMobject.__init__(self, **kwargs)
        self.rotate(-TAU/4)

class FalconHeavy(SVGMobject):
    CONFIG = {
        "file_name" : "falcon_heavy",
        "color" : WHITE,
        "logo_color" : BLUE_E,
        "height" : 1.5,
    }
    def __init__(self, **kwargs):
        SVGMobject.__init__(self, **kwargs)
        self.logo = self[-9:]
        self.logo.highlight(self.logo_color)

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

class Flash(AnimationGroup):
    CONFIG = {
        "line_length" : 0.2,
        "num_lines" : 12,
        "flash_radius" : 0.3,
        "line_stroke_width" : 3,
    }
    def __init__(self, mobject, color = YELLOW, **kwargs):
        digest_config(self, kwargs)
        original_color = mobject.get_color()
        on_and_off = UpdateFromAlphaFunc(
            mobject.copy(), lambda m, a : m.highlight(
                color if a < 0.5 else original_color
            ),
            remover = True
        )
        lines = VGroup()
        for angle in np.arange(0, TAU, TAU/self.num_lines):
            line = Line(ORIGIN, self.line_length*RIGHT)
            line.shift((self.flash_radius - self.line_length)*RIGHT)
            line.rotate(angle, about_point = ORIGIN)
            lines.add(line)
        lines.move_to(mobject)
        lines.highlight(color)
        line_anims = [
            ShowCreationThenDestruction(
                line, rate_func = squish_rate_func(smooth, 0, 0.5)
            )
            for line in lines
        ]
        fade_anims = [
            UpdateFromAlphaFunc(
                line, lambda m, a : m.set_stroke(
                    width = self.line_stroke_width*(1-a)
                ),
                rate_func = squish_rate_func(smooth, 0, 0.75)
            )
            for line in lines
        ]
        
        AnimationGroup.__init__(
            self, on_and_off, *line_anims+fade_anims, **kwargs
        )

class MultipleFlashes(Succession):
    CONFIG = {
        "run_time_per_flash" : 1.0,
        "num_flashes" : 3,
    }
    def __init__(self, *args, **kwargs):
        digest_config(self, kwargs)
        kwargs["run_time"] = self.run_time_per_flash
        Succession.__init__(self, *[
            Flash(*args, **kwargs)
            for x in range(self.num_flashes)
        ])

class TrafficLight(SVGMobject):
    CONFIG = {
        "file_name" : "traffic_light",
        "height" : 0.7,
        "post_height" : 2,
        "post_width" : 0.05,
    }
    def __init__(self, **kwargs):
        SVGMobject.__init__(self, **kwargs)
        post = Rectangle(
            height = self.post_height,
            width = self.post_width,
            stroke_width = 0,
            fill_color = WHITE,
            fill_opacity = 1,
        )
        self.move_to(post.get_top(), DOWN)
        self.add_to_back(post)

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
    CONFIG = {
        "show_text" : True,
        "complex_to_real_func" : abs,
    }
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
        time_label.scale(1.5)
        time_label.next_to(
            time_axes.x_axis.get_right(), UP+LEFT,
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
            y_max = 0.1,
            y_axis_config = {
                "unit_size" : 30,
                "tick_frequency" : 0.025,
            },
            color = TEAL,
        )
        frequency_label = TextMobject("Frequency")
        frequency_label.scale(1.5)
        frequency_label.next_to(
            frequency_axes.x_axis.get_right(), UP+LEFT,
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
                frequency_axes, 
                get_wave_packet_function(),
                t_min = time_mean - time_radius,
                t_max = time_mean + time_radius,
                n_samples = 2*time_radius*17,
                complex_to_real_func = self.complex_to_real_func,
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
            wave_packet, frequency_axes.coords_to_point(
                4, frequency_axes.y_max/2,
            ),
            color = FREQUENCY_COLOR,
        )
        fourier_words = TextMobject("$|$Fourier Transform$|$")
        fourier_words.next_to(arrow, LEFT, buff = MED_LARGE_BUFF)
        sub_words = TextMobject("(To be explained shortly)")
        sub_words.highlight(BLUE)
        sub_words.scale(0.75)
        sub_words.next_to(fourier_words, DOWN)

        #Draw items
        self.add(time_axes, frequency_axes)
        self.play(ShowCreation(wave_packet, rate_func = double_smooth))
        anims = [ReplacementTransform(
            wave_packet.copy(), fourier_graph
        )]
        if self.show_text:
            anims += [
                GrowArrow(arrow),
                Write(fourier_words, run_time = 1)
            ]
        self.play(*anims)
        # self.play(FadeOut(arrow))
        self.wait()
        for width in 6, 0.02, 1:
            self.play(
                width_tracker.move_to, width*RIGHT,
                wave_packet_update,
                fourier_graph_update,
                run_time = 3
            )
            if sub_words not in self.mobjects and self.show_text:
                self.play(FadeIn(sub_words))
            else:
                self.wait()
        self.wait()

class ShowPlan(PiCreatureScene):
    def construct(self):
        self.add_title()
        words = self.get_words()
        self.play_sound_anims(words[0])
        self.play_doppler_anims(words[1])
        self.play_quantum_anims(words[2])

    def add_title(self):
        title = TextMobject("The plan")
        title.scale(1.5)
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT).scale(SPACE_WIDTH)
        h_line.next_to(title, DOWN)
        self.add(title, h_line)

    def get_words(self):
        trips = [
            ("sound waves", "(time vs. frequency)", YELLOW),
            ("Doppler radar", "(distance vs. velocity)", GREEN),
            ("quantum particles", "(position vs. momentum)", BLUE),
        ]
        words = VGroup()
        for topic, tradeoff, color in trips:
            word = TextMobject("Uncertainty for", topic, tradeoff)
            word[1:].highlight(color)
            word[2].scale(0.75)
            word[2].next_to(word[1], DOWN, buff = 1.5*SMALL_BUFF)
            words.add(word)
        words.arrange_submobjects(DOWN, aligned_edge = LEFT, buff = MED_LARGE_BUFF)
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

    def play_doppler_anims(self, word):
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
            Write(word),
            DrawBorderThenFill(radar_dish),
            UpdateFromAlphaFunc(
                target, lambda m, a : m.set_fill(opacity = a)
            ),
            morty.change, "pondering",
            run_time = 1
        )
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

    def play_quantum_anims(self, word):
        morty = self.pi_creature
        dot_cloud = ProbabalisticDotCloud()
        gdw = dot_cloud.gaussian_distribution_wrapper
        gdw.next_to(word, DOWN, MED_LARGE_BUFF)
        gdw.rotate(5*DEGREES)
        gdw.save_state()
        gdw.scale(0)


        checkmark = self.get_checkmark(word)
        ish = TextMobject("$\\dots$ish")
        ish.next_to(checkmark, RIGHT, -SMALL_BUFF, DOWN)

        self.add(dot_cloud)
        self.play(
            Write(word),
            FadeIn(dot_cloud.mobject),
            morty.change, "confused",
        )
        self.play(gdw.restore, run_time = 2)
        self.play(Write(checkmark))
        self.wait()
        self.play(
            Write(ish), 
            morty.change, 'maybe'
        )
        self.wait(6)


    ##

    def get_checkmark(self, word):
        checkmark = TexMobject("\\checkmark")
        checkmark.highlight(GREEN)
        checkmark.scale(1.25)
        checkmark.next_to(word[1], UP+RIGHT, buff = 0)
        return checkmark

class StartWithIntuition(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "You already \\\\ have this \\\\ intuition",
            bubble_kwargs = {
                "height" : 3.5,
                "width" : 3,
            },
        )
        self.change_student_modes("pondering", "erm", "maybe")
        self.look_at(VectorizedPoint(4*LEFT + 2*UP))
        self.wait(5)

class TwoCarsAtRedLight(Scene):
    CONFIG = {
        "text_scale_val" : 0.75,
    }
    def construct(self):
        self.pull_up_behind()
        self.flash_in_sync_short_time()
        self.show_low_confidence()
        self.flash_in_sync_long_time()
        self.show_high_confidence()

    def pull_up_behind(self):
        #Setup Traffic light
        traffic_light = TrafficLight()
        traffic_light.move_to(6*RIGHT + 2.5*DOWN, DOWN)
        source_point = VectorizedPoint(
            traffic_light[2].get_right()
        )
        screen = Line(ORIGIN, UP)
        screen.next_to(source_point, RIGHT, LARGE_BUFF)
        red_light = Spotlight(
            color = RED,
            source_point = source_point,
            radius = 0.5,
            screen = screen,
            num_levels = 20,
            opacity_function = lambda r : 1/(10*r**2+1)
        )
        red_light.fade(0.5)
        red_light.rotate(TAU/2, about_edge = LEFT)
        self.add(red_light, traffic_light)

        #Setup cars
        car1, car2 = cars = self.cars = VGroup(*[
            Car() for x in range(2)
        ])
        cars.arrange_submobjects(RIGHT, buff = LARGE_BUFF)
        cars.next_to(
            traffic_light, LEFT, 
            buff = LARGE_BUFF, aligned_edge = DOWN
        )
        car2.pi_creature.highlight(GREY_BROWN)
        car1.start_point = car1.get_corner(DOWN+RIGHT)
        car1.shift(SPACE_WIDTH*LEFT)

        #Pull up car
        self.add(cars)
        self.play(
            SwitchOn(
                red_light, 
                rate_func = squish_rate_func(smooth, 0, 0.3),
            ),
            Animation(traffic_light),
            self.get_flashes(car2, num_flashes = 3),
            MoveCar(
                car1, car1.start_point,
                run_time = 3,
                rate_func = rush_from,
            )
        )

    def flash_in_sync_short_time(self):
        car1, car2 = cars = self.cars

        #Setup axes
        axes = Axes(
            x_min = 0,
            x_max = 5,
            y_min = 0, 
            y_max = 2,
            y_axis_config = {
                "tick_frequency" : 0.5,
            },
        )
        axes.x_axis.add_numbers(1, 2, 3)
        time_label = TextMobject("Time")
        time_label.scale(self.text_scale_val)
        time_label.next_to(axes.x_axis.get_right(), DOWN)
        y_title = TextMobject("Signal")
        y_title.scale(self.text_scale_val)
        y_title.next_to(axes.y_axis, UP, SMALL_BUFF)
        axes.add(time_label, y_title)
        axes.to_corner(UP+LEFT, buff = MED_SMALL_BUFF)
        graph = axes.get_graph(
            self.get_multispike_function(range(1, 4)),
            x_min = 0.8,
            x_max = 3.8,
        )
        graph.highlight(YELLOW)

        #Label short duration
        brace = Brace(Line(
            axes.input_to_graph_point(1, graph),
            axes.input_to_graph_point(3, graph),
        ), UP)
        text = TextMobject("Short duration observation")
        text.scale(self.text_scale_val)
        text.next_to(brace, UP, SMALL_BUFF)
        text.align_to(
            axes.coords_to_point(0.25, 0), LEFT
        )


        self.play(
            self.get_flashes(car1, num_flashes = 2),
            self.get_flashes(car2, num_flashes = 2),
            LaggedStart(FadeIn, VGroup(
                axes, time_label, y_title,
            ))
        )
        self.play(
            self.get_flashes(car1, num_flashes = 3),
            self.get_flashes(car2, num_flashes = 3),
            ShowCreation(graph, rate_func = None, run_time = 3)
        )
        self.play(
            self.get_flashes(car1, num_flashes = 10),
            self.get_flashes(car2, num_flashes = 10, run_time_per_flash = 0.98),
            GrowFromCenter(brace),
            Write(text),
        )

        self.time_axes = axes
        self.time_graph = graph
        self.time_graph_label = VGroup(
            brace, text
        )

    def show_low_confidence(self):
        car1, car2 = cars = self.cars
        time_axes = self.time_axes

        #Setup axes
        frequency_axes = Axes(
            x_min = 0,
            x_max = 3,
            y_min = 0,
            y_max = 1.5,
            y_axis_config = {
                "tick_frequency" : 0.5,
            }
        )
        frequency_axes.next_to(time_axes, DOWN, LARGE_BUFF)
        frequency_axes.highlight(LIGHT_GREY)
        frequency_label = TextMobject("Frequency")
        frequency_label.scale(self.text_scale_val)
        frequency_label.next_to(frequency_axes.x_axis.get_right(), DOWN)
        frequency_axes.add(
            frequency_label,
            VectorizedPoint(frequency_axes.y_axis.get_top())
        )
        frequency_axes.x_axis.add_numbers(1, 2)
        frequency_graph = frequency_axes.get_graph(
            lambda x : np.exp(-4*(x-1)**2),
            x_min = 0,
            x_max = 2,
        )
        frequency_graph.highlight(RED)
        peak_point = frequency_axes.input_to_graph_point(
            1, frequency_graph
        )

        #Setup label
        label = TextMobject("Low confidence")
        label.scale(self.text_scale_val)
        label.move_to(peak_point + UP+RIGHT, DOWN)
        label.match_color(frequency_graph)
        arrow = Arrow(label.get_bottom(), peak_point, buff = 2*SMALL_BUFF)
        arrow.match_color(frequency_graph)

        self.play(
            ReplacementTransform(
                self.time_axes.copy(), frequency_axes
            ),
            ReplacementTransform(
                self.time_graph.copy(), frequency_graph
            ),
        )
        self.play(
            Write(label), 
            GrowArrow(arrow)
        )
        self.wait()

        self.frequency_axes = frequency_axes
        self.frequency_graph = frequency_graph
        self.frequency_graph_label = VGroup(
            label, arrow
        )

    def flash_in_sync_long_time(self):
        time_graph = self.time_graph
        time_axes = self.time_axes
        frequency_graph = self.frequency_graph
        frequency_axes = self.frequency_axes

        n_spikes = 12
        new_time_graph = time_axes.get_graph(
            self.get_multispike_function(range(1, n_spikes+1)),
            x_min = 0.8,
            x_max = n_spikes + 0.8,
        )
        new_time_graph.match_color(time_graph)

        new_frequency_graph = frequency_axes.get_graph(
            lambda x : np.exp(-500*(x-1)**2),
            x_min = 0,
            x_max = 2,
            num_anchors = 500,
        )
        new_frequency_graph.match_color(self.frequency_graph)

        def pin_freq_graph_end_points(freq_graph):
            freq_graph.points[0] = frequency_axes.coords_to_point(0, 0)
            freq_graph.points[-1] = frequency_axes.coords_to_point(2, 0)

        self.play(LaggedStart(
            FadeOut, VGroup(
                self.time_graph_label,
                self.frequency_graph_label,
                self.time_graph,
            )
        ))
        self.play(
            ApplyMethod(
                self.time_axes.x_axis.main_line.stretch, 2.5, 0,
                {"about_edge" : LEFT},
                run_time = 4,
                rate_func = squish_rate_func(smooth, 0.3, 0.6),
            ),
            UpdateFromFunc(
                self.time_axes.x_axis.tip,
                lambda m : m.move_to(
                    self.time_axes.x_axis.main_line.get_right(), 
                    LEFT
                )
            ),
            ShowCreation(
                new_time_graph,
                run_time = n_spikes,
                rate_func = None,
            ),
            ApplyMethod(
                frequency_graph.stretch, 0.1, 0,
                run_time = n_spikes,
            ),
            UpdateFromFunc(frequency_graph, pin_freq_graph_end_points),
            *[
                self.get_flashes(car, num_flashes = n_spikes)
                for car in self.cars
            ]
        )

        self.new_time_graph = new_time_graph
        self.new_frequency_graph = new_frequency_graph

    def show_high_confidence(self):
        #Frequency stuff
        arrow = self.frequency_graph_label[1]
        label = TextMobject("High confidence")
        label.scale(self.text_scale_val)
        label.next_to(arrow.get_start(), UP, SMALL_BUFF)
        label.match_color(arrow)

        frequency_axes = self.frequency_axes

        #Time stuff
        new_time_graph = self.new_time_graph
        brace = Brace(new_time_graph, UP, buff = SMALL_BUFF)
        text = TextMobject("Long duration observation")
        text.scale(self.text_scale_val)
        text.next_to(brace, UP, buff = SMALL_BUFF)

        self.play(
            FadeIn(label),
            GrowArrow(arrow),
            *map(self.get_flashes, self.cars)
        )
        self.play(
            GrowFromCenter(brace),
            Write(text, run_time = 1),
            *map(self.get_flashes, self.cars)
        )
        self.play(*[
            self.get_flashes(car, num_flashes = 10)
            for car in self.cars
        ])

    ###

    def get_flashes(self, car, colors = [YELLOW, RED], num_flashes = 1, **kwargs):
        return AnimationGroup(*[
            MultipleFlashes(light, color, num_flashes = num_flashes, **kwargs)
            for light, color in zip(car.get_lights(), colors)
        ])

    def get_multispike_function(self, spike_times):
        return lambda x : sum([
            1.25*np.exp(-100*(x-m)**2)
            for m in spike_times
        ])

class VariousMusicalNotes(Scene):
    def construct(self):
        freq = 20
        # x-coordinate of this point represents log(a)
        # where the bell curve component of the signal
        # is exp(-a*(x**2))
        graph_width_tracker = VectorizedPoint()
        graph_width_tracker.move_to(np.log(2)*RIGHT)
        def get_graph():
            a = np.exp(graph_width_tracker.get_center()[0])
            return FunctionGraph(
                lambda x : np.exp(-a*x**2)*np.sin(freq*x)-0.5,
                num_anchor_points = 500,
            )
        graph = get_graph()
        def graph_update(graph):
            graph.points = get_graph().points
        graph_update_anim = UpdateFromFunc(graph, graph_update)
        def change_width_anim(width, **kwargs):
            a = 2.0/(width**2)
            return AnimationGroup(
                ApplyMethod(
                    graph_width_tracker.move_to,
                    np.log(a)*RIGHT
                ),
                graph_update_anim,
                **kwargs
            )

        phrases = [
            TextMobject(*words.split(" "))
            for words in [
                "Less clear frequency",
                "Extremely unclear frequency",
                "Very clear frequency",
            ]
        ]


        #Show graphs and phrases
        widths = [1, 0.2, SPACE_WIDTH]
        for width, phrase in zip(widths, phrases):
            brace = Brace(Line(LEFT, RIGHT), UP)
            brace.stretch(width, 0)
            brace.next_to(graph.get_center(), UP, buff = 1.2)
            phrase.next_to(brace, UP)

            if width is widths[0]:
                self.play(ShowCreation(graph, rate_func = None)),
                self.play(
                    GrowFromCenter(brace),
                    Write(phrase, run_time = 1)
                )
            else:
                self.play(
                    change_width_anim(width),
                    ReplacementTransform(
                        VGroup(last_phrase, last_brace),
                        VGroup(phrase, brace),
                        rate_func = squish_rate_func(smooth, 0.5, 1),
                    ),
                    run_time = 2
                )
            self.wait()
            # self.play(*map(FadeOut, [graph, brace, phrase]))
            last_phrase = phrase
            last_brace = brace

        #Talk about correlations
        short_signal_words = TextMobject(
            "Short", "signal", "correlates",
            "with", "wide range", "of frequencies"
        )
        long_signal_words = TextMobject(
            "Only", "wide", "signals", "correlate",
            "with a", "short range", "of frequencies"
        )
        phrases = VGroup(short_signal_words, long_signal_words)
        for phrase in phrases:
            phrase.scale(0.8)
            phrase.highlight_by_tex_to_color_map({
                "short" : RED,
                "long" : GREEN,
                "wide" : GREEN,
            }, case_sensitive = False)
        phrases.arrange_submobjects(DOWN)
        phrases.to_edge(UP)

        long_graph = FunctionGraph(
            lambda x : 0.5*np.sin(freq*x),
            x_min = -2*SPACE_WIDTH,
            x_max = 2*SPACE_WIDTH,
            num_anchor_points = 1000
        )
        long_graph.highlight(BLUE)
        long_graph.next_to(graph, UP, MED_LARGE_BUFF)

        self.play(
            ShowCreation(long_graph),
            *map(FadeOut, [last_brace, last_phrase])
        )
        self.play(
            Write(short_signal_words),
            change_width_anim(widths[1])
        )
        self.play(
            long_graph.stretch, 0.35, 0,
            long_graph.highlight, GREEN,
            run_time = 5,
            rate_func = wiggle
        )
        self.wait()
        self.play(
            Write(long_signal_words),
            change_width_anim(widths[2]),
        )
        self.play(
            long_graph.stretch, 0.95, 0,
            long_graph.highlight, average_color(GREEN, BLUE),
            run_time = 4,
            rate_func = wiggle
        )
        self.wait()

class BringInFourierTranform(TeacherStudentsScene):
    def construct(self):
        fourier = TextMobject("Fourier")
        fourier.scale(1.5)
        fourier.next_to(self.teacher.get_corner(UP+LEFT), UP, LARGE_BUFF)
        fourier.save_state()
        fourier.shift(DOWN)
        fourier.fade(1)

        self.play(
            self.teacher.change, "raise_right_hand",
            fourier.restore
        )
        self.change_student_modes("happy", "erm", "confused")
        self.look_at(3*LEFT + 2*UP)
        self.wait(3)

class LastVideoWrapper(Scene):
    def construct(self):
        title = TextMobject("Visualizing the Fourier Transform")
        title.to_edge(UP)
        screen_rect = ScreenRectangle(height = 6)
        screen_rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(screen_rect))
        self.wait()

class FourierRecapScene(DrawFrequencyPlot):
    CONFIG = {
        "frequency_axes_config" : {
            "x_max" : 10.0,
            "x_axis_config" : {
                "unit_size" : 0.7,
                "numbers_to_show" : range(1, 10, 1),
            }
        },
        "initial_winding_frequency" : 0.1,
    }
    def construct(self):
        self.setup_axes()
        self.preview_fourier_plot()
        self.wrap_signal_around_circle()
        self.match_winding_to_beat_frequency()
        self.follow_center_of_mass()
        self.draw_fourier_plot()
        self.highlight_spike()

    def setup_axes(self):
        self.remove(self.pi_creature)
        time_axes = self.get_time_axes()
        time_axes.to_edge(UP, buff = MED_SMALL_BUFF)
        time_axes.scale(0.9, about_edge = UP)
        frequency_axes = self.get_frequency_axes()
        circle_plane = self.get_circle_plane()

        self.add(time_axes)

        self.set_variables_as_attrs(
            time_axes, frequency_axes,
            circle_plane
        )

    def preview_fourier_plot(self):
        time_graph = self.graph = self.get_time_graph(
            width = 2,
            num_graph_points = 200,
        )
        fourier_graph = self.get_fourier_transform_graph(
            time_graph
        )
        fourier_graph.pointwise_become_partial(fourier_graph, 0.1, 1)

        #labels
        signal_label = TextMobject("Signal")
        fourier_label = TextMobject("Fourier transform")
        signal_label.next_to(time_graph, UP, buff = SMALL_BUFF)
        fourier_label.next_to(fourier_graph, UP)
        fourier_label.match_color(fourier_graph)

        self.play(
            ShowCreation(time_graph, run_time = 2),
            Write(signal_label),
        )
        self.wait()
        self.play(
            LaggedStart(FadeIn, self.frequency_axes),
            ReplacementTransform(
                time_graph.copy(),
                fourier_graph,
                run_time = 2
            ),
            ReplacementTransform(
                signal_label.copy(),
                fourier_label,
                run_time = 2,
                rate_func = squish_rate_func(smooth, 0.5, 1)
            ),
        )
        self.wait()
        self.play(LaggedStart(
            Indicate, self.frequency_axes.x_axis.numbers,
            run_time = 4,
            rate_func = wiggle,
        ))
        self.wait()
        self.play(*map(FadeOut, [
            self.frequency_axes, fourier_graph,
            signal_label,  fourier_label,
        ]))

        self.time_graph = time_graph
        self.set_variables_as_attrs(time_graph, fourier_label)

    def wrap_signal_around_circle(self):
        time_graph = self.time_graph
        circle_plane = self.circle_plane
        freq = self.initial_winding_frequency
        pol_graph = self.get_polarized_mobject(time_graph, freq)
        winding_freq_label = self.get_winding_frequency_label()
        winding_freq_label.add_to_back(BackgroundRectangle(winding_freq_label))
        winding_freq_label.move_to(circle_plane.get_top(), DOWN)

        self.add_foreground_mobjects(winding_freq_label)
        self.play(
            Write(circle_plane, run_time = 1),
            ReplacementTransform(
                time_graph.copy(), pol_graph,
                path_arc = -TAU/4,
                run_time_per_flash = 2,
                run_time = 2,
            ),
            FadeIn(winding_freq_label),
        )
        freq = 0.3
        self.change_frequency(freq, run_time = 2)
        ghost_pol_graph = pol_graph.copy()
        self.remove(pol_graph)
        self.play(ghost_pol_graph.set_stroke, {"width" : 0.5})
        self.play(
            *self.get_vector_animations(time_graph),
            run_time = 15
        )
        self.remove(ghost_pol_graph)
        self.wait()

    def match_winding_to_beat_frequency(self):
        self.v_lines_indicating_periods = self.get_v_lines_indicating_periods(0.3)
        self.add(self.v_lines_indicating_periods)
        for freq in range(1, 6):
            self.change_frequency(freq, run_time = 5)
        self.play(
            *self.get_vector_animations(
                self.time_graph,
                draw_polarized_graph = False
            ),
            rate_func = lambda t : 0.3*t,
            run_time = 5
        )
        self.wait()

    def follow_center_of_mass(self):
        com_dot = self.get_center_of_mass_dot()
        self.generate_center_of_mass_dot_update_anim()
        com_arrow = Arrow(UP+3*RIGHT, ORIGIN)
        com_arrow.shift(com_dot.get_center())
        com_arrow.match_color(com_dot)
        com_words = TextMobject("Center of mass")
        com_words.next_to(com_arrow.get_start(), UP)
        com_words.match_color(com_arrow)
        com_words.add_background_rectangle()

        com_dot.save_state()
        com_dot.move_to(com_arrow.get_start())
        com_dot.fade(1)

        self.play(
            com_dot.restore,
            GrowArrow(com_arrow, rate_func = squish_rate_func(smooth, 0.2, 1)),
            Write(com_words),
        )
        self.wait()
        squished_func = squish_rate_func(smooth, 0, 0.2)
        self.change_frequency(
            4,
            added_anims = [
                FadeOut(com_arrow, rate_func = squished_func),
                FadeOut(com_words, rate_func = squished_func),
            ],
            run_time = 5
        )

    def draw_fourier_plot(self):
        frequency_axes = self.frequency_axes
        fourier_label = self.fourier_label

        self.change_frequency(0, run_time = 2)
        self.play(
            FadeIn(frequency_axes),
            FadeIn(fourier_label),
        )

        fourier_graph = self.get_fourier_transform_graph(self.time_graph)
        self.get_fourier_graph_drawing_update_anim(fourier_graph)
        self.generate_fourier_dot_transform(fourier_graph)

        self.change_frequency(5, run_time = 20)
        self.wait()
        self.change_frequency(7.5, run_time = 10)
        self.fourier_graph_drawing_update_anim = Animation(Mobject())
        self.fourier_graph = fourier_graph

    def highlight_spike(self):
        spike_point = self.frequency_axes.input_to_graph_point(
            5, self.fourier_graph
        )
        circle = Circle(color = YELLOW, radius = 0.25)
        circle.move_to(spike_point)
        circle.save_state()
        circle.scale(5)
        circle.fade(1)

        self.change_frequency(5)
        self.play(circle.restore)
        self.play(FadeOut(circle))
        self.wait()
        for x in range(2):
            self.change_frequency(5.2, run_time = 3)
            self.change_frequency(4.8, run_time = 3)
        self.change_frequency(5, run_time = 1.5)
        self.wait()


    #########

    def get_time_graph(self, frequency = 5, width = 2, **kwargs):
        # low_x = center-width/2
        # high_x = center+width/2
        # new_smooth = lambda x : np.clip(smooth((x+0.5)), 0, 1)
        # def func(x):
        #     pure_signal = 0.9*np.cos(TAU*frequency*x)
        #     factor = new_smooth(x - low_x) - new_smooth(x-high_x)
        #     return 1 + factor*pure_signal
        graph = self.time_axes.get_graph(
            lambda x : 1+0.9*np.cos(TAU*frequency*x),
            x_min = 0, x_max = width,
            **kwargs
        )
        graph.highlight(YELLOW)
        return graph

class CenterOfMassDescription(FourierRecapScene):
    def construct(self):
        self.remove(self.pi_creature)
        circle_plane = self.get_circle_plane()
        circle_plane.save_state()
        circle_plane.generate_target()
        circle_plane.target.scale_to_fit_height(2*SPACE_HEIGHT)
        circle_plane.target.center()
        circle_plane.target.axes.set_stroke(width = 2)
        circle_plane.target.main_lines.set_stroke(width = 2)
        circle_plane.target.secondary_lines.set_stroke(width = 1)

        start_coords = (0.5, 0.5)
        alt_coords = (0.8, 0.8)

        com_dot = Dot(color = self.center_of_mass_color)
        com_dot.move_to(circle_plane.coords_to_point(*start_coords))

        self.add(circle_plane, com_dot)
        self.wait()
        self.play(
            MoveToTarget(circle_plane),
            com_dot.move_to, 
            circle_plane.target.coords_to_point(*start_coords)
        )
        self.wait()

        alt_com_dot = com_dot.copy().move_to(
            circle_plane.coords_to_point(*alt_coords)
        )

        for dot in com_dot, alt_com_dot:
            line = Line(ORIGIN, dot.get_center())
            line.match_color(com_dot)
            angle = line.get_angle()
            line.rotate(-angle, about_point = ORIGIN)
            brace = Brace(line, UP)
            words = brace.get_text("Strength of frequency")
            words.add_background_rectangle()
            dot.length_label_group = VGroup(line, brace, words)
            dot.length_label_group.rotate(angle, about_point = ORIGIN)

        line, brace, words = com_dot.length_label_group
        self.play(
            GrowFromCenter(line),
            GrowFromCenter(brace),
            FadeIn(words),
        )
        self.wait()
        self.play(
            Transform(
                com_dot.length_label_group,
                alt_com_dot.length_label_group,
            ),
            Transform(com_dot, alt_com_dot),
            rate_func = there_and_back,
            run_time = 4,
        )

        #Do rotation
        line = com_dot.length_label_group[0]
        com_dot.length_label_group.remove(line)
        angle = line.get_angle()
        arc, alt_arc = [
            Arc(
                start_angle = 0, 
                angle = factor*angle,
                radius = 0.5,
            )
            for factor in 1, 2
        ]
        theta = TexMobject("\\theta")
        theta.shift(1.5*arc.point_from_proportion(0.5))

        self.play(
            FadeOut(com_dot.length_label_group),
            Animation(line),
            ShowCreation(arc),
            Write(theta)
        )
        self.play(
            Rotate(
                VGroup(line, com_dot),
                angle, about_point = ORIGIN
            ),
            Transform(arc, alt_arc),
            theta.move_to, 1.5*alt_arc.point_from_proportion(0.5),
            rate_func = there_and_back,
            run_time = 4
        )
        self.wait()

class AskAboutLongVsShort(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "What happens if we \\\\ change the length of \\\\ the signal?",
            student_index = 2,
        )
        self.play(
            self.teacher.change, "happy",
            self.get_student_changes("pondering", "confused", "raise_right_hand")
        )
        self.wait(5)

class LongAndShortSignalsInWindingMachine(FourierRecapScene):
    CONFIG = {
        "num_fourier_graph_points" : 1000,
    }
    def construct(self):
        self.setup_axes()
        self.extend_for_long_time()
        self.note_sharp_fourier_peak()
        self.very_short_signal()
        self.note_wide_fourier_peak()

    def setup_axes(self):
        FourierRecapScene.setup_axes(self)
        self.add(self.circle_plane)
        self.add(self.frequency_axes)
        self.time_graph = self.graph = self.get_time_graph(width = 2)
        self.add(self.time_graph)

        self.force_skipping()
        self.wrap_signal_around_circle()

        fourier_graph = self.get_fourier_transform_graph(self.time_graph)
        self.fourier_graph = fourier_graph
        self.add(fourier_graph)
        self.change_frequency(5)

        self.revert_to_original_skipping_status()

    def extend_for_long_time(self):
        short_time_graph = self.time_graph
        long_time_graph = self.get_time_graph(
            width = 10,
            num_graph_points = 500,
        )
        long_time_graph.set_stroke(width = 2)
        new_freq = 5.1
        long_pol_graph = self.get_polarized_mobject(
            long_time_graph,
            freq = new_freq
        )
        fourier_graph = self.fourier_graph

        self.change_frequency(new_freq)
        self.play(
            FadeOut(self.graph),
            FadeOut(self.graph.polarized_mobject),
            FadeOut(fourier_graph)
        )
        self.play(
            ShowCreation(long_time_graph, rate_func = None),
            ShowCreation(long_pol_graph, rate_func = None),
            run_time = 5
        )
        self.wait()

        self.time_graph = self.graph = long_time_graph

    def note_sharp_fourier_peak(self):
        fourier_graph = self.get_fourier_transform_graph(
            self.time_graph, 
            num_graph_points = self.num_fourier_graph_points
        )
        self.fourier_graph = fourier_graph
        self.note_fourier_peak(fourier_graph, 5, 5.1)

    def very_short_signal(self):
        time_graph = self.time_graph
        fourier_graph = self.fourier_graph
        short_time_graph = self.get_time_graph(width = 0.6)
        new_freq = 5.1
        short_pol_graph = self.get_polarized_mobject(
            short_time_graph,
            freq = new_freq
        )

        self.play(
            FadeOut(fourier_graph),
            FadeOut(time_graph),
            FadeOut(time_graph.polarized_mobject),
        )
        self.play(
            ShowCreation(short_time_graph),
            ShowCreation(short_time_graph.polarized_mobject),
        )
        self.graph = self.time_graph = short_time_graph
        self.change_frequency(6.66, run_time = 5)

    def note_wide_fourier_peak(self):
        fourier_graph = self.get_fourier_transform_graph(
            self.graph, 
            num_graph_points = self.num_fourier_graph_points
        )
        self.fourier_graph = fourier_graph
        self.note_fourier_peak(fourier_graph, 5, 6.66)


    ###

    def note_fourier_peak(self, fourier_graph, freq1, freq2):
        fourier_graph = self.fourier_graph
        dots = self.get_fourier_graph_dots(fourier_graph, freq1, freq2)
        self.get_center_of_mass_dot()
        self.generate_center_of_mass_dot_update_anim()
        self.generate_fourier_dot_transform(fourier_graph)
        dot = self.fourier_graph_dot
        arrow = Arrow(UP, ORIGIN, buff = SMALL_BUFF)
        arrow.next_to(dot, UP, buff = SMALL_BUFF)

        self.play(ShowCreation(fourier_graph))
        self.change_frequency(freq1,
            added_anims = [
                MaintainPositionRelativeTo(arrow, dot),
                UpdateFromAlphaFunc(
                    arrow,
                    lambda m, a : m.set_fill(opacity = a)
                ),
            ],
            run_time = 3,
        )
        self.wait()
        self.change_frequency(freq2,
            added_anims = [
                MaintainPositionRelativeTo(arrow, dot)
            ],
            run_time = 3
        )
        self.wait()
        self.play(*map(FadeOut, [
            dot, arrow, self.center_of_mass_dot
        ]))
        #This is not great...
        for attr in "center_of_mass_dot", "fourier_graph_dot":
            self.__dict__.pop(attr)


    def get_fourier_graph_dots(self, fourier_graph, *freqs):
        axis_point = self.frequency_axes.coords_to_point(4.5, -0.25)
        dots = VGroup()
        for freq in freqs:
            point = self.frequency_axes.input_to_graph_point(freq, fourier_graph)
            dot = Dot(point)
            dot.scale(0.5)
            dots.add(dot)
            vect = point - axis_point
            vect *= 1.3/np.linalg.norm(vect)
            arrow = Arrow(vect, ORIGIN, buff = SMALL_BUFF)
            arrow.highlight(YELLOW)
            arrow.shift(point)
            dot.arrow = arrow
        return dots

class CleanerFourierTradeoff(FourierTradeoff):
    CONFIG = {
        "show_text" : False,
        "complex_to_real_func" : lambda z : z.real,
    }

class MentionDopplerRadar(TeacherStudentsScene):
    def construct(self):
        words = TextMobject("Doppler Radar")
        words.next_to(self.teacher, UP)
        words.save_state()
        words.shift(DOWN).fade(1)
        dish = RadarDish()
        dish.next_to(self.students, UP, buff = 2, aligned_edge = LEFT)
        plane = Plane()
        plane.to_edge(RIGHT)
        plane.align_to(dish)
        plane_flight = AmbientMovement(
            plane, 
            direction = LEFT,
            rate = 1,
        )
        plane.flip()
        pulse = RadarPulse(dish, plane)
        look_at_anims = [
            ContinualUpdateFromFunc(
                pi, lambda pi : pi.look_at(pulse.mobject)
            )
            for pi in self.get_pi_creatures()
        ]

        self.add(dish, plane_flight, pulse, *look_at_anims)
        self.play(
            self.teacher.change, "hooray",
            words.restore
        )
        self.change_student_modes("pondering", "erm", "sassy")
        self.wait(2)
        self.play(
            self.teacher.change, "happy",
            self.get_student_changes(*["thinking"]*3)
        )
        self.wait()
        dish.set_stroke(width = 0)
        self.play(UpdateFromAlphaFunc(
            VGroup(plane, dish),
            lambda m, a : m.set_fill(opacity = 1 - a)
        ))

class IntroduceDopplerRadar(Scene):
    CONFIG = {
        "frequency_spread_factor" : 100,
    }
    def construct(self):
        self.setup_axes()
        self.measure_distance_with_time()
        self.show_frequency_shift()
        self.show_frequency_shift_in_fourier()

    def setup_axes(self):
        self.dish = RadarDish()
        self.dish.to_corner(UP+LEFT)
        axes = Axes(
            x_min = 0,
            x_max = 10,
            y_min = -1.5,
            y_max = 1.5
        )
        axes.move_to(DOWN)
        time_label = TextMobject("Time")
        time_label.next_to(axes.x_axis.get_right(), UP)
        axes.time_label = time_label
        axes.add(time_label)
        self.axes = axes

        self.add(self.dish)
        self.add(axes)

    def measure_distance_with_time(self):
        dish = self.dish
        axes = self.axes
        distance = 5
        time_diff = 5
        speed = (2*distance)/time_diff
        randy = Randolph().flip()
        randy.match_height(dish)
        randy.move_to(dish.get_right(), LEFT)
        randy.shift(distance*RIGHT)

        pulse_graph, echo_graph, sum_graph = \
            self.get_pulse_and_echo_graphs(
                self.get_single_pulse_graph,
                (1,), (1+time_diff,)
            )
        words = ["Original signal", "Echo"]
        for graph, word in zip([pulse_graph, echo_graph], words):
            arrow = Vector(DOWN)
            arrow.next_to(graph.peak_point, UP, MED_SMALL_BUFF)
            arrow.match_color(graph)
            graph.arrow = arrow
            label = TextMobject(word)
            label.next_to(arrow.get_start(), UP, SMALL_BUFF)
            label.match_color(graph)
            graph.label = label

        double_arrow = DoubleArrow(
            pulse_graph.peak_point,
            echo_graph.peak_point,
            color = WHITE
        )
        distance_text = TextMobject("$2 \\times$ distance/(signal speed)")
        distance_text.scale_to_fit_width(0.9*double_arrow.get_width())
        distance_text.next_to(double_arrow, UP, SMALL_BUFF)

        #v_line anim?

        pulse = RadarPulseSingleton(
            dish, randy, 
            speed = 0.97*speed, #Just needs slightly better alignment
        )
        graph_draw = NormalAnimationAsContinualAnimation(
            ShowCreation(
                sum_graph, 
                rate_func = None, 
                run_time = 0.97*axes.x_max
            )
        )
        randy_look_at = ContinualUpdateFromFunc(
            randy, lambda pi : pi.look_at(pulse.mobject)
        )
        axes_anim = ContinualAnimation(axes)

        self.add(randy_look_at, axes_anim, graph_draw)
        self.wait(0.5)
        self.add(pulse)
        self.play(
            Write(pulse_graph.label),
            GrowArrow(pulse_graph.arrow),
            run_time = 1,
        )
        self.play(randy.change, "pondering")
        self.wait(time_diff - 2)
        self.play(
            Write(echo_graph.label),
            GrowArrow(echo_graph.arrow),
            run_time = 1
        )
        self.wait()
        self.play(
            GrowFromCenter(double_arrow),
            FadeIn(distance_text)
        )
        self.wait()

        self.remove(graph_draw, pulse, randy_look_at, axes_anim)
        self.add(axes)
        self.play(LaggedStart(FadeOut, VGroup(
            sum_graph, randy,
            pulse_graph.arrow, pulse_graph.label,
            echo_graph.arrow, echo_graph.label,
            double_arrow, distance_text
        )))

    def show_frequency_shift(self):
        axes = self.axes
        dish = self.dish
        plane = Plane()
        plane.flip()
        plane.move_to(dish)
        plane.to_edge(RIGHT)

        time_diff = 6

        pulse_graph, echo_graph, sum_graph = graphs = \
            self.get_pulse_and_echo_graphs(
                self.get_frequency_pulse_graph,
                (1,25), (1+time_diff,50)
            )
        for graph in graphs:
            graph.set_stroke(width = 3)
        signal_graph = self.get_frequency_pulse_graph(1)

        pulse_brace = Brace(Line(ORIGIN, RIGHT), UP)
        pulse_brace.move_to(axes.coords_to_point(1, 1.2))
        echo_brace = pulse_brace.copy()
        echo_brace.stretch(0.6, 0)
        echo_brace.move_to(axes.coords_to_point(7, 1.2))
        pulse_text = pulse_brace.get_text("Original signal")
        pulse_text.add_background_rectangle()
        echo_text = echo_brace.get_text("Echo")
        echo_subtext = TextMobject("(Higher frequency)")
        echo_subtext.next_to(echo_text, RIGHT)
        echo_subtext.match_color(echo_graph)

        graph_draw = NormalAnimationAsContinualAnimation(
            ShowCreation(sum_graph, run_time = 8, rate_func = None)
        )
        pulse = RadarPulse(dish, plane, n_pulse_singletons = 12)
        plane_flight = AmbientMovement(
            plane, direction = LEFT, rate = 1.5
        )

        self.add(graph_draw, pulse, plane_flight)
        self.play(UpdateFromAlphaFunc(
            plane, lambda m, a : m.set_fill(opacity = a)
        ))
        self.play(
            GrowFromCenter(pulse_brace),
            FadeIn(pulse_text),
        )
        self.wait(3)
        self.play(
            GrowFromCenter(echo_brace),
            GrowFromCenter(echo_text),
        )
        self.play(UpdateFromAlphaFunc(
            plane, lambda m, a : m.set_fill(opacity = 1-a)
        ))
        #Only for when -s is run
        graph_draw.update(10) 
        self.wait(0.1)
        self.play(Write(echo_subtext, run_time = 1))
        self.wait()
        self.remove(graph_draw, pulse, plane_flight)

        pulse_graph.set_stroke(width = 0)
        echo_graph.set_stroke(width = 0)
        self.time_graph_group = VGroup(
            axes, pulse_brace, pulse_text,
            echo_brace, echo_text, echo_subtext,
            pulse_graph, echo_graph, sum_graph,
        )
        self.set_variables_as_attrs(*self.time_graph_group)

    def show_frequency_shift_in_fourier(self):
        sum_graph = self.sum_graph
        pulse_graph = self.pulse_graph
        pulse_label = VGroup(self.pulse_brace, self.pulse_text)
        echo_graph = self.echo_graph
        echo_label = VGroup(
            self.echo_brace, self.echo_text, self.echo_subtext
        )

        #Setup all fourier graph stuff
        f_max = 0.02
        frequency_axes = Axes(
            x_min = 0, x_max = 20,
            x_axis_config = {"unit_size" : 0.5},
            y_min = -f_max, y_max = f_max,
            y_axis_config = {
                "unit_size" : 50,
                "tick_frequency" : 0.01,
            },
        )
        frequency_axes.move_to(self.axes, LEFT)
        frequency_axes.to_edge(DOWN)
        frequency_label = TextMobject("Frequency")
        frequency_label.next_to(
            frequency_axes.x_axis.get_right(), UP,
        )
        frequency_label.to_edge(RIGHT)
        frequency_axes.add(frequency_label)

        for graph in pulse_graph, echo_graph, sum_graph:
            graph.fourier_transform = get_fourier_graph(
                frequency_axes, graph.underlying_function,
                frequency_axes.x_min, 25,
                complex_to_real_func = abs,
            )

        #Braces labeling F.T.
        original_fourier_brace = Brace(
            Line(
                frequency_axes.coords_to_point(7, 0.9*f_max),
                frequency_axes.coords_to_point(9, 0.9*f_max),
            ),
            UP,
        ).highlight(BLUE)
        echo_fourier_brace = Brace(
            Line(
                frequency_axes.coords_to_point(14, 0.4*f_max),
                frequency_axes.coords_to_point(18, 0.4*f_max),
            ),
            UP,
        ).highlight(YELLOW)
        # braces = [original_fourier_brace, echo_fourier_brace]
        # words = ["original signal", "echo"]
        # for brace, word in zip(braces, words):
        #     brace.add(brace.get_text("F.T. of \\\\ %s"%word))
        fourier_label = TexMobject("||\\text{Fourier transform}||")
        # fourier_label.next_to(sum_graph.fourier_transform, UP, MED_LARGE_BUFF)
        fourier_label.next_to(frequency_axes.y_axis, UP, buff = SMALL_BUFF)
        fourier_label.shift_onto_screen()
        fourier_label.highlight(RED)


        #v_lines
        v_line = DashedLine(
            frequency_axes.coords_to_point(8, 0),
            frequency_axes.coords_to_point(8, 1.2*f_max),
            color = YELLOW,
            dashed_segment_length = 0.025,
        )
        v_line_pair = VGroup(*[
            v_line.copy().shift(u*0.6*RIGHT)
            for u in -1, 1
        ])
        v_line = VGroup(v_line)

        double_arrow = DoubleArrow(
            frequency_axes.coords_to_point(8, 0.007),
            frequency_axes.coords_to_point(16, 0.007),
            buff = 0,
            color = WHITE
        )

        self.play(
            self.time_graph_group.to_edge, UP,
            ApplyMethod(
                self.dish.shift, 2*UP, 
                remover = True
            ),
            FadeIn(frequency_axes)
        )
        self.wait()
        self.play(
            FadeOut(sum_graph),
            FadeOut(echo_label),
            pulse_graph.set_stroke, {"width" : 3},
        )
        self.play(
            ReplacementTransform(
                pulse_label[0].copy(),
                original_fourier_brace
            ),
            ShowCreation(pulse_graph.fourier_transform)
        )
        self.play(Write(fourier_label))
        self.wait()
        self.play(ShowCreation(v_line))
        self.wait()
        self.play(ReplacementTransform(v_line, v_line_pair))
        self.wait()
        self.play(FadeOut(v_line_pair))
        self.wait()

        self.play(
            FadeOut(pulse_graph),
            FadeIn(sum_graph),
            ReplacementTransform(
                pulse_graph.fourier_transform,
                sum_graph.fourier_transform
            )
        )
        self.play(FadeIn(echo_label))
        self.play(ReplacementTransform(
            echo_label[0].copy(),
            echo_fourier_brace,
        ))
        self.wait(2)
        self.play(GrowFromCenter(double_arrow))
        self.wait()


    ###

    def get_graph(self, func, **kwargs):
        graph = self.axes.get_graph(func, **kwargs)
        graph.peak_point = self.get_peak_point(graph)
        return graph

    def get_single_pulse_graph(self, x, **kwargs):
        return self.get_graph(self.get_single_pulse_function(x), **kwargs)

    def get_single_pulse_function(self, x):
        return lambda t : -2*np.sin(10*(t-x))*np.exp(-100*(t-x)**2)

    def get_frequency_pulse_graph(self, x, freq = 50, **kwargs):
        return self.get_graph(
            self.get_frequency_pulse_function(x, freq), 
            num_graph_points = 700,
            **kwargs
        )

    def get_frequency_pulse_function(self, x, freq):
        factor = self.frequency_spread_factor
        return lambda t : op.mul(
            2*np.cos(2*freq*(t-x)),
            min(np.exp(-(freq**2/factor)*(t-x)**2), 0.5)
        )

    def get_peak_point(self, graph):
        anchors = graph.get_anchors()
        return anchors[np.argmax([p[1] for p in anchors])]

    def get_pulse_and_echo_graphs(self, func, args1, args2):
        pulse_graph = func(*args1, color = BLUE)
        echo_graph = func(*args2, color = YELLOW)
        sum_graph = self.axes.get_graph(
            lambda x : sum([
                pulse_graph.underlying_function(x),
                echo_graph.underlying_function(x),
            ]),
            num_graph_points = echo_graph.get_num_anchor_points(),
            color = WHITE
        )
        sum_graph.background_image_file = "blue_yellow_gradient"
        return pulse_graph, echo_graph, sum_graph

class MentionPRFNuance(TeacherStudentsScene):
    def construct(self):
        title = TextMobject(
            "Speed of light", "$\\gg$", "Speed of a plane"
        )
        title.to_edge(UP)
        self.add(title)

        axes = self.axes = Axes(
            x_min = 0, x_max = 10,
            y_min = 0, y_max = 2,
        )
        axes.next_to(title, DOWN, buff = MED_LARGE_BUFF)
        frequency_label = TextMobject("Frequency")
        frequency_label.scale(0.7)
        frequency_label.next_to(axes.x_axis.get_right(), UP)
        axes.add(frequency_label)
        self.add(axes)

        pulse_x, shift_x = 4, 6
        pulse_graph = self.get_spike_graph(pulse_x)
        shift_graph = self.get_spike_graph(shift_x)
        shift_graph.set_stroke(YELLOW, 2)
        peak_points = VGroup(pulse_graph.peak_point, shift_graph.peak_point)
        self.add(pulse_graph)

        brace = Brace(peak_points, UP, buff = SMALL_BUFF)
        displayed_doppler_shift = TextMobject("How I'm showing the \\\\", "Doppler shift")
        actual_doppler_shift = TextMobject("Actual\\\\", "Doppler shift")
        doppler_shift_words = VGroup(displayed_doppler_shift, actual_doppler_shift)
        doppler_shift_words.highlight(YELLOW)
        doppler_shift_words.scale(0.75)
        displayed_doppler_shift.next_to(brace, UP, buff = SMALL_BUFF)
        actual_doppler_shift.move_to(pulse_graph.peak_point)
        actual_doppler_shift.align_to(displayed_doppler_shift)

        self.play(
            Animation(pulse_graph),
            self.teacher.change, "raise_right_hand", 
            run_time = 1
        )
        self.play(
            ShowCreation(shift_graph),
            FadeIn(brace),
            Write(displayed_doppler_shift, run_time = 1),
            self.get_student_changes(*3*["sassy"]),
        )
        self.play(
            UpdateFromAlphaFunc(
                shift_graph, 
                lambda g, a : Transform(
                    g, self.get_spike_graph(
                        interpolate(shift_x, pulse_x+0.01, a),
                    ).match_style(shift_graph)
                ).update(1),
            ),
            UpdateFromFunc(
                brace,
                lambda b : b.match_width(
                    peak_points, stretch = True
                ).next_to(peak_points, UP, SMALL_BUFF)
            ),
            Transform(
                displayed_doppler_shift, actual_doppler_shift,
                rate_func = squish_rate_func(smooth, 0.3, 0.6)
            ),
            run_time = 3
        )
        self.wait(2)

        everything = VGroup(
            title,
            axes, pulse_graph, shift_graph,
            brace, displayed_doppler_shift
        )
        rect = SurroundingRectangle(everything, color = WHITE)
        everything.add(rect)

        self.teacher_says(
            "I'll ignore certain \\\\ nuances for now.",
            target_mode = "shruggie",
            added_anims = [
                everything.scale, 0.4,
                everything.to_corner, UP+LEFT,
                UpdateFromAlphaFunc(
                    rect, lambda m, a : m.set_stroke(width = 2*a)
                )
            ],
        )
        self.change_student_modes(*3*["hesitant"])
        self.wait(2)




    def get_spike_graph(self, x, color = RED, **kwargs):
        graph = self.axes.get_graph(
            lambda t : np.exp(-10*(t-x)**2)*np.cos(10*(t-x)),
            color = color,
            **kwargs
        )
        graph.peak_point = VectorizedPoint(self.axes.input_to_graph_point(x, graph))
        graph.add(graph.peak_point)
        return graph

class TimeAndFrequencyGivePositionAndVelocity(IntroduceDopplerRadar):
    def construct(self):
        x = 7
        freq = 25

        axes = self.axes = Axes(
            x_min = 0, x_max = 10,
            y_min = -2, y_max = 2,
        )
        axes.center()
        title = TextMobject("Echo signal")
        title.next_to(axes.y_axis, UP)
        axes.add(title)
        axes.to_edge(UP)
        graph = self.get_frequency_pulse_graph(x = x, freq = freq)
        graph.background_image_file = "blue_yellow_gradient"

        arrow = Arrow(
            axes.coords_to_point(0, -1.5),
            axes.coords_to_point(x, -1.5),
            color = WHITE,
            buff = SMALL_BUFF,
        )
        time = TextMobject("Time")
        time.next_to(arrow, DOWN, SMALL_BUFF)

        delta_x = 0.7
        brace = Brace(
            Line(
                axes.coords_to_point(x-delta_x, 1), 
                axes.coords_to_point(x+delta_x, 1)
            ),
            UP
        )
        frequency = TextMobject("Frequency")
        frequency.highlight(YELLOW)
        frequency.next_to(brace, UP, SMALL_BUFF)

        time_updown_arrow = TexMobject("\\Updownarrow")
        time_updown_arrow.next_to(time, DOWN, SMALL_BUFF)
        freq_updown_arrow = time_updown_arrow.copy()
        freq_updown_arrow.next_to(frequency, UP, SMALL_BUFF)
        distance = TextMobject("Distance")
        distance.next_to(time_updown_arrow, DOWN, SMALL_BUFF)
        velocity = TextMobject("Velocity")
        velocity.next_to(freq_updown_arrow, UP, SMALL_BUFF)
        VGroup(freq_updown_arrow, velocity).match_style(frequency)

        self.add(axes)
        self.play(ShowCreation(graph))
        self.play(
            GrowArrow(arrow),
            LaggedStart(FadeIn, time, run_time = 1)
        )
        self.play(
            GrowFromCenter(brace),
            LaggedStart(FadeIn, frequency, run_time = 1)
        )
        self.wait()
        self.play(
            GrowFromPoint(time_updown_arrow, time_updown_arrow.get_top()),
            ReplacementTransform(
                time.copy().fade(1), 
                distance
            )
        )
        self.play(
            GrowFromPoint(freq_updown_arrow, freq_updown_arrow.get_top()),
            ReplacementTransform(
                frequency.copy().fade(1), 
                velocity
            )
        )
        self.wait()

class RadarOperatorUncertainty(Scene):
    def construct(self):
        dish = RadarDish()
        dish.scale(3)
        dish.move_to(4*RIGHT + 2*DOWN)
        dish_words = TextMobject("3b1b industrial \\\\ enterprises")
        dish_words.scale(0.25)
        dish_words.set_stroke(BLACK, 0.5)
        dish_words.highlight(BLACK)
        dish_words.move_to(dish, DOWN)
        dish_words.shift(SMALL_BUFF*(UP+2*LEFT))
        dish.add(dish_words)
        randy = Randolph()
        randy.next_to(dish, LEFT, aligned_edge = DOWN)
        bubble = randy.get_bubble(
            width = 7,
            height = 4,
        )

        echo_object = Square()
        echo_object.move_to(dish)
        echo_object.shift(SPACE_WIDTH*RIGHT)
        pulse = RadarPulse(dish, echo_object, speed = 6)

        plane = Plane().scale(0.5)
        plane.move_to(bubble.get_bubble_center()+LEFT)
        plane_cloud = ProbabalisticMobjectCloud(
            plane, 
            fill_opacity = 0.3,
            n_copies = 10,
        )
        plane_gdw = plane_cloud.gaussian_distribution_wrapper

        vector_cloud = ProbabalisticVectorCloud(
            center_func = plane_gdw.get_center,
        )
        vector_gdw = vector_cloud.gaussian_distribution_wrapper
        vector_gdw.scale(0.05)
        vector_gdw.move_to(plane_gdw)
        vector_gdw.shift(2*RIGHT)


        self.add(randy, dish, bubble, plane_cloud, pulse)
        self.play(randy.change, "confused")
        self.wait(3)
        self.add(vector_cloud)
        for i in range(3):
            for plane_factor, vector_factor, freq in (0.05, 10, 0.01), (20, 0.1, 0.1):
                pulse.internal_time = 0
                pulse.frequency = freq
                self.play(
                    randy.change, "pondering", plane,
                    plane_gdw.scale, plane_factor,
                    vector_gdw.scale, vector_factor,
                )
                self.wait(2)

class AmbiguityInLongEchos(IntroduceDopplerRadar, PiCreatureScene):
    CONFIG = {
        "object_x_coords" : [7, 4, 6, 9, 8],
        "frequency_spread_factor" : 200,
        "n_pulse_singletons" : 16,
        "pulse_frequency" : 0.025,
    }
    def construct(self):
        self.setup_axes()
        self.setup_objects()
        self.send_long_pulse_single_echo()
        self.introduce_multiple_objects()
        self.use_short_pulse()
        self.fourier_transform_of_one_pulse()
        self.show_echos_of_moving_objects()
        self.overlapping_frequenies_of_various_objects()
        self.echos_of_long_pure_signal_in_frequency_space()
        self.concentrated_fourier_requires_long_time()

    def setup_axes(self):
        axes = self.axes = Axes(
            x_min = 0, x_max = 10,
            y_min = -1.5, y_max = 1.5,
        )
        time_label = TextMobject("Time")
        time_label.next_to(axes.x_axis.get_right(), UP)
        axes.add(time_label)
        axes.center()
        axes.shift(DOWN)
        self.add(axes)

        dish = self.dish = RadarDish()
        dish.move_to(axes, LEFT)
        dish.to_edge(UP, buff = LARGE_BUFF)
        self.add(dish)

    def setup_objects(self):
        objects = self.objects = VGroup(
            Plane().flip(),
            SVGMobject(
                file_name = "blimp", 
                color = BLUE_C,
                height = 0.5,
            ),
            SVGMobject(
                file_name = "biplane", 
                color = RED_D,
                height = 0.5,
            ),
            SVGMobject(
                file_name = "helicopter", 
                color = LIGHT_GREY,
                height = 0.5,
            ).rotate(-TAU/24),
            FalconHeavy(),
        )
        y_shifts = [0.25, 0, 0.5, 0.25, -0.5]
        for x, y, obj in zip(self.object_x_coords, y_shifts, objects):
            obj.move_to(self.axes.coords_to_point(x, 0))
            obj.align_to(self.dish)
            obj.shift(y*UP)

        self.object_velocities = [
            0.7*LEFT,
            0.1*RIGHT,
            0.4*LEFT,
            0.4*RIGHT,
            0.5*UP,
        ]

    def send_long_pulse_single_echo(self):
        x = self.object_x_coords[0]
        plane = self.objects[0]
        self.add(plane)
        randy = self.pi_creature
        self.remove(randy)

        pulse_graph = self.get_frequency_pulse_graph(x)
        pulse_graph.background_image_file = "blue_yellow_gradient"

        pulse = self.get_pulse(self.dish, plane)

        brace = Brace(
            Line(
                self.axes.coords_to_point(x-1, 1),
                self.axes.coords_to_point(x+1, 1),
            ), UP
        )
        words = brace.get_text("Spread over time")

        self.add(pulse)
        self.wait()
        squished_rate_func = squish_rate_func(smooth, 0.6, 0.9)
        self.play(
            ShowCreation(pulse_graph, rate_func = None),
            GrowFromCenter(brace, rate_func = squished_rate_func),
            Write(words, rate_func = squished_rate_func),
            run_time = 3,
        )
        self.remove(pulse)
        self.play(FadeIn(randy))
        self.play(PiCreatureBubbleIntroduction(
            randy, "Who cares?",
            bubble_class = ThoughtBubble,
            bubble_kwargs = {
                "direction" : LEFT,
                "width" : 2,
                "height": 1.5,
            },
            target_mode = "maybe",
            look_at_arg = brace,
        ))
        self.play(Blink(randy))
        self.play(LaggedStart(
            FadeOut, VGroup(
                randy.bubble, randy.bubble.content, 
                brace, words,
            )
        ))

        self.curr_graph = pulse_graph

    def introduce_multiple_objects(self):
        objects = self.objects
        x_coords = self.object_x_coords
        curr_graph = self.curr_graph
        randy = self.pi_creature

        graphs = VGroup(*[
            self.get_frequency_pulse_graph(x)
            for x in x_coords
        ])
        graphs.gradient_highlight(BLUE, YELLOW)
        sum_graph = self.axes.get_graph(
            lambda t : sum([
                graph.underlying_function(t)
                for graph in graphs
            ]),
            num_graph_points = 1000
        )

        noise_function = lambda t : np.sum([
            0.5*np.sin(f*t)/f 
            for f in 2, 3, 5, 7, 11, 13
        ])
        noisy_graph = self.axes.get_graph(
            lambda t : sum_graph.underlying_function(t)*(1+noise_function(t)),
            num_graph_points = 1000
        )
        for graph in sum_graph, noisy_graph:
            graph.background_image_file = "blue_yellow_gradient"

        pulses = self.get_pulses()

        self.play(
            LaggedStart(GrowFromCenter, objects[1:]),
            FadeOut(curr_graph),
            randy.change, "pondering"
        )
        self.add(*pulses)
        self.wait(0.5)
        self.play(
            ShowCreation(
                sum_graph,
                rate_func = None,
                run_time = 3.5,
            ),
            randy.change, "confused"
        )
        self.remove(*pulses)
        self.play(randy.change, "pondering")
        self.play(Transform(
            sum_graph, noisy_graph,
            rate_func = lambda t : wiggle(t, 4),
            run_time = 3
        ))
        self.wait(2)

        self.curr_graph = sum_graph

    def use_short_pulse(self):
        curr_graph = self.curr_graph
        objects = self.objects
        x_coords = self.object_x_coords
        randy = self.pi_creature

        self.frequency_spread_factor = 10
        self.n_pulse_singletons = 4
        self.pulse_frequency = 0.015

        graphs = VGroup(*[
            self.get_frequency_pulse_graph(x)
            for x in x_coords
        ])
        sum_graph = self.axes.get_graph(
            lambda t : sum([
                graph.underlying_function(t)
                for graph in graphs
            ]),
            num_graph_points = 1000
        )
        sum_graph.background_image_file = "blue_yellow_gradient"

        pulses = self.get_pulses()

        self.play(FadeOut(curr_graph))
        self.add(*pulses)
        self.wait(0.5)
        self.play(
            ShowCreation(
                sum_graph,
                rate_func = None,
                run_time = 3.5,
            ),
            randy.change, "happy"
        )
        self.wait()

        self.curr_graph = sum_graph
        self.first_echo_graph = graphs[0]
        self.first_echo_graph.highlight(YELLOW)

    def fourier_transform_of_one_pulse(self):
        frequency_axes = Axes(
            x_min = 0, x_max = 20,
            x_axis_config = {
                "unit_size" : 0.5, 
                "tick_frequency" : 2, 
            },
            y_min = -.01, y_max = .01,
            y_axis_config = {
                "unit_size" : 110,
                "tick_frequency" : 0.006
            }
        )
        frequency_label = TextMobject("Frequency")
        frequency_label.next_to(frequency_axes.x_axis.get_right(), UP)
        frequency_axes.add(frequency_label)
        first_echo_graph = self.first_echo_graph

        self.play(
            ApplyMethod(
                VGroup(self.axes, first_echo_graph).to_edge, UP,
                {"buff" : SMALL_BUFF},
                rate_func = squish_rate_func(smooth, 0.5, 1)
            ),
            LaggedStart(FadeOut, self.objects),
            LaggedStart(FadeOut, VGroup(
                self.curr_graph, self.dish, self.pi_creature
            )),
            run_time = 2
        )

        #
        frequency_axes.next_to(self.axes, DOWN, LARGE_BUFF, LEFT)
        fourier_graph = get_fourier_graph(
            frequency_axes, first_echo_graph.underlying_function,
            t_min = 0, t_max = 25,
            complex_to_real_func = np.abs,
        )
        fourier_graph.save_state()
        fourier_graph.move_to(first_echo_graph)
        h_vect = 4*RIGHT
        fourier_graph.shift(h_vect)
        fourier_graph.fade(1)

        f = 8
        v_line = DashedLine(
            frequency_axes.coords_to_point(f, 0),
            frequency_axes.coords_to_point(f, frequency_axes.y_max),
        )
        v_lines = VGroup(
            v_line.copy().shift(2*LEFT),
            v_line.copy().shift(2*RIGHT),
        )
        rect = Rectangle(stroke_width = 0, fill_color = YELLOW, fill_opacity = 0.25)
        rect.replace(v_lines, stretch = True)
        rect.save_state()
        rect.stretch(0, 0)

        self.play(Write(frequency_axes, run_time = 1))
        self.play(
            ApplyFunction(
                lambda m : m.move_to(fourier_graph.saved_state).shift(-h_vect).fade(1),
                first_echo_graph.copy(),
                remover = True,
            ),
            fourier_graph.restore
        )
        self.wait()
        self.play(ShowCreation(v_line))
        self.play(
            ReplacementTransform(VGroup(v_line), v_lines),
            rect.restore
        )
        self.wait()
        self.play(FadeOut(v_lines), FadeOut(rect))

        self.frequency_axes = frequency_axes
        self.fourier_graph = fourier_graph

    def show_echos_of_moving_objects(self):
        objects = self.objects
        objects.save_state()
        object_velocities = self.object_velocities

        movements = self.object_movements = [
            AmbientMovement(
                obj, 
                direction = v/np.linalg.norm(v),
                rate = np.linalg.norm(v)
            )
            for v, obj in zip(object_velocities, objects)
        ]
        pulses = self.get_pulses()
        continual_anims = pulses+movements
        
        self.play(
            FadeOut(self.axes),
            FadeOut(self.first_echo_graph),
            LaggedStart(FadeIn, objects),
            FadeIn(self.dish)
        )
        self.add(*continual_anims)
        self.wait(4)
        self.play(*[
            UpdateFromAlphaFunc(
                obj, 
                lambda m, a : m.set_fill(opacity = 1-a),
            )
            for obj in objects
        ])
        self.remove(*continual_anims)
        self.wait()

    def overlapping_frequenies_of_various_objects(self):
        frequency_axes = self.frequency_axes
        fourier_graph = self.fourier_graph
        shifted_graphs = self.get_shifted_frequency_graphs(fourier_graph)
        color = fourier_graph.get_color()
        shifted_graphs.gradient_highlight(
            average_color(color, WHITE), 
            color,
            average_color(color, BLACK),
        )
        sum_graph = self.get_sum_graph(frequency_axes, shifted_graphs)
        sum_graph.match_style(fourier_graph)

        shifted_graphs.save_state()

        self.play(ReplacementTransform(
            VGroup(fourier_graph), shifted_graphs,
            submobject_mode = "lagged_start",
            run_time = 2
        ))
        self.wait()
        self.play(
            shifted_graphs.arrange_submobjects, DOWN,
            shifted_graphs.move_to, fourier_graph, DOWN,
        )
        self.wait()
        self.play(shifted_graphs.restore),
        self.play(ReplacementTransform(
            shifted_graphs, VGroup(sum_graph),
        ))
        self.wait()

        self.curr_fourier_graph = sum_graph

    def echos_of_long_pure_signal_in_frequency_space(self):
        curr_fourier_graph = self.curr_fourier_graph
        f_max = self.frequency_axes.y_max
        new_fourier_graph = self.frequency_axes.get_graph(
            lambda x : f_max * np.exp(-100*(x-8)**2),
            num_graph_points = 1000,
        )
        new_fourier_graph.highlight(PINK)

        self.play(
            FadeOut(curr_fourier_graph),
            FadeIn(new_fourier_graph),
        )
        self.fourier_graph = new_fourier_graph
        self.overlapping_frequenies_of_various_objects()

    def concentrated_fourier_requires_long_time(self):
        objects = self.objects
        objects.restore()
        object_movements = self.object_movements
        self.n_pulse_singletons = 32
        pulses = self.get_pulses()
        randy = self.pi_creature

        continual_anims = object_movements+pulses
        self.play(FadeIn(randy))
        self.add(*continual_anims)
        self.play(randy.change, "angry", *[
            UpdateFromAlphaFunc(obj, lambda m, a : m.set_fill(opacity = a))
            for obj in objects
        ])
        self.play(Blink(randy))
        self.wait(2)
        self.play(Blink(randy))
        self.wait()
        self.play(randy.change, "plain", *[
            UpdateFromAlphaFunc(obj, lambda m, a : m.set_fill(opacity = 1-a))
            for obj in objects
        ])
        self.wait()


    ###

    def get_frequency_pulse_graph(self, x, freq = 25, **kwargs):
        graph = IntroduceDopplerRadar.get_frequency_pulse_graph(
            self, x, freq, **kwargs
        )
        return graph

    def get_pulse(self, dish, echo_object):
        return RadarPulse(
            dish, echo_object, 
            n_pulse_singletons = self.n_pulse_singletons,
            frequency = 0.025,
            speed = 5.0,
        )

    def get_pulses(self):
        return [
            self.get_pulse(
                self.dish.copy().shift(0.01*obj.get_center()[0]),
                obj
            )
            for obj in self.objects
        ]

    def create_pi_creature(self):
        randy = Randolph()
        randy.scale(0.5).flip()
        randy.to_edge(RIGHT, buff = 1.7).shift(0.5*UP)
        return randy

    def get_shifted_frequency_graphs(self, fourier_graph):
        frequency_axes = self.frequency_axes
        def get_func(v):
            return lambda f : fourier_graph.underlying_function(np.clip(
                f-5*v[0], 
                frequency_axes.x_min,
                frequency_axes.x_max,
            ))
        def get_graph(func):
            return frequency_axes.get_graph(func)
        shifted_graphs = VGroup(*map(
            get_graph, map(get_func, self.object_velocities)
        ))
        shifted_graphs.match_style(fourier_graph)
        return shifted_graphs

    def get_sum_graph(self, axes, graphs):
        def get_func(graph):
            return graph.underlying_function
        funcs = map(get_func, graphs)
        return axes.get_graph(
            lambda t : sum([func(t) for func in funcs]),
        )

class SummarizeFourierTradeoffForDoppler(Scene):
    def construct(self):
        pass











