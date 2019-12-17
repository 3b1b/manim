# -*- coding: utf-8 -*-

import scipy
from manimlib.imports import *
from old_projects.fourier import *

import warnings
warnings.warn("""
    Warning: This file makes use of
    ContinualAnimation, which has since
    been deprecated
""")

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
        "gaussian_distribution_wrapper_config" : {},
        "time_per_change" : 1./60,
        "start_up_time" : 0,
    }
    def __init__(self, prototype, **kwargs):
        digest_config(self, kwargs)
        fill_opacity = self.fill_opacity or prototype.get_fill_opacity()
        if "mu" not in self.gaussian_distribution_wrapper_config:
            self.gaussian_distribution_wrapper_config["mu"] = prototype.get_center()
        self.gaussian_distribution_wrapper = GaussianDistributionWrapper(
            **self.gaussian_distribution_wrapper_config
        )
        self.time_since_last_change = np.inf
        group = VGroup(*[
            prototype.copy().set_fill(opacity = fill_opacity)
            for x in range(self.n_copies)
        ])
        ContinualAnimation.__init__(self, group, **kwargs)
        self.update_mobject(0)

    def update_mobject(self, dt):
        self.time_since_last_change += dt
        if self.time_since_last_change < self.time_per_change:
            return
        self.time_since_last_change = 0

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
        self.logo.set_color(self.logo_color)

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
        self.direction = self.direction/get_norm(self.direction)
        self.radar_dish = radar_dish
        self.target = target
        self.reflection_distance = None
        self.arc = Arc(
            start_angle = -30*DEGREES,
            angle = 60*DEGREES,
        )
        self.arc.set_height(0.75*radar_dish.get_height())
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
            group.set_color(color)
            return Mobject.add_updater(group, update_group)

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
        "complex_to_real_func" : lambda z : z.real,
        "widths" : [6, 0.02, 1],
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
        time_axes.x_axis.add_numbers(*list(range(1, 2*time_mean)))

        frequency_axes = Axes(
            x_min = 0,
            x_max = 8,
            x_axis_config = {"unit_size" : 1.5},
            y_min = -0.025,
            y_max = 0.075,
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
        frequency_label.set_color(FREQUENCY_COLOR)
        frequency_axes.add(frequency_label)
        frequency_axes.move_to(time_axes, LEFT)
        frequency_axes.to_edge(DOWN, buff = LARGE_BUFF)
        frequency_axes.x_axis.add_numbers()

        # Graph information

        #x-coordinate of this point determines width of wave_packet graph
        width_tracker = ExponentialValueTracker(0.5)
        get_width = width_tracker.get_value

        def get_wave_packet_function():
            factor = 1./get_width()
            return lambda t : (factor**0.25)*np.cos(4*TAU*t)*np.exp(-factor*(t-time_mean)**2)

        def get_wave_packet():
            graph = time_axes.get_graph(
                get_wave_packet_function(),
                num_graph_points = 200,
            )
            graph.set_color(YELLOW)
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
        fourier_words = TextMobject("Fourier Transform")
        fourier_words.next_to(arrow, LEFT, buff = MED_LARGE_BUFF)
        sub_words = TextMobject("(To be explained shortly)")
        sub_words.set_color(BLUE)
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
        for width in self.widths:
            self.play(
                width_tracker.set_value, width,
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
        h_line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS)
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
            word[1:].set_color(color)
            word[2].scale(0.75)
            word[2].next_to(word[1], DOWN, buff = 1.5*SMALL_BUFF)
            words.add(word)
        words.arrange(DOWN, aligned_edge = LEFT, buff = MED_LARGE_BUFF)
        words.to_edge(LEFT)

        return words

    def play_sound_anims(self, word):
        morty = self.pi_creature
        wave = FunctionGraph(
            lambda x : 0.3*np.sin(15*x)*np.sin(0.5*x),
            x_min = 0, x_max = 30,
            step_size = 0.001,
        )
        wave.next_to(word, RIGHT)
        rect = BackgroundRectangle(wave, fill_opacity = 1)
        rect.stretch(2, 1)
        rect.next_to(wave, LEFT, buff = 0)
        always_shift(wave, direction=LEFT, rate=5)
        wave_fader = UpdateFromAlphaFunc(
            wave, 
            lambda w, a : w.set_stroke(width = 3*a)
        )
        checkmark = self.get_checkmark(word)

        self.add(wave)
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
        always_shift(target, direction = RIGHT, rate = 1.25)

        pulse = RadarPulse(radar_dish, target)

        checkmark = self.get_checkmark(word)

        self.add(target)
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
        while not pulse.is_finished() and next(count) < 15:
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
        checkmark.set_color(GREEN)
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
        cars.arrange(RIGHT, buff = LARGE_BUFF)
        cars.next_to(
            traffic_light, LEFT, 
            buff = LARGE_BUFF, aligned_edge = DOWN
        )
        car2.pi_creature.set_color(GREY_BROWN)
        car1.start_point = car1.get_corner(DOWN+RIGHT)
        car1.shift(FRAME_X_RADIUS*LEFT)

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
            self.get_multispike_function(list(range(1, 4))),
            x_min = 0.8,
            x_max = 3.8,
        )
        graph.set_color(YELLOW)

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
            LaggedStartMap(FadeIn, VGroup(
                axes, time_label, y_title,
            ))
        )
        self.play(
            self.get_flashes(car1, num_flashes = 3),
            self.get_flashes(car2, num_flashes = 3),
            ShowCreation(graph, rate_func=linear, run_time = 3)
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
        frequency_axes.set_color(LIGHT_GREY)
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
        frequency_graph.set_color(RED)
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
            self.get_multispike_function(list(range(1, n_spikes+1))),
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

        self.play(LaggedStartMap(
            FadeOut, VGroup(
                self.time_graph_label,
                self.frequency_graph_label,
                self.time_graph,
            )
        ))
        self.play(
            ApplyMethod(
                self.time_axes.x_axis.stretch, 2.5, 0,
                {"about_edge" : LEFT},
                run_time = 4,
                rate_func = squish_rate_func(smooth, 0.3, 0.6),
            ),
            UpdateFromFunc(
                self.time_axes.x_axis.tip,
                lambda m : m.move_to(
                    self.time_axes.x_axis.get_right(), 
                    LEFT
                )
            ),
            ShowCreation(
                new_time_graph,
                run_time = n_spikes,
                rate_func=linear,
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
            *list(map(self.get_flashes, self.cars))
        )
        self.play(
            GrowFromCenter(brace),
            Write(text, run_time = 1),
            *list(map(self.get_flashes, self.cars))
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
        graph_width_tracker = ExponentialValueTracker(1)
        def get_graph():
            a = graph_width_tracker.get_value()
            return FunctionGraph(
                lambda x : np.exp(-a*x**2)*np.sin(freq*x)-0.5,
                step_size = 0.001,
            )
        graph = get_graph()
        def graph_update(graph):
            graph.points = get_graph().points
        graph_update_anim = UpdateFromFunc(graph, graph_update)
        def change_width_anim(width, **kwargs):
            a = 2.0/(width**2)
            return AnimationGroup(
                ApplyMethod(graph_width_tracker.set_value, a),
                graph_update_anim,
                **kwargs
            )
        change_width_anim(FRAME_X_RADIUS).update(1)
        graph_update_anim.update(0)

        phrases = [
            TextMobject(*words.split(" "))
            for words in [
                "Very clear frequency",
                "Less clear frequency",
                "Extremely unclear frequency",
            ]
        ]


        #Show graphs and phrases
        widths = [FRAME_X_RADIUS, 1, 0.2]
        for width, phrase in zip(widths, phrases):
            brace = Brace(Line(LEFT, RIGHT), UP)
            brace.stretch(width, 0)
            brace.next_to(graph.get_center(), UP, buff = 1.2)
            phrase.next_to(brace, UP)

            if width is widths[0]:
                self.play(ShowCreation(graph, rate_func=linear)),
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
            phrase.set_color_by_tex_to_color_map({
                "short" : RED,
                "long" : GREEN,
                "wide" : GREEN,
            }, case_sensitive = False)
        phrases.arrange(DOWN)
        phrases.to_edge(UP)

        long_graph = FunctionGraph(
            lambda x : 0.5*np.sin(freq*x),
            x_min = -FRAME_WIDTH,
            x_max = FRAME_WIDTH,
            n_components = 0.001
        )
        long_graph.set_color(BLUE)
        long_graph.next_to(graph, UP, MED_LARGE_BUFF)

        self.play(
            ShowCreation(long_graph),
            *list(map(FadeOut, [last_brace, last_phrase]))
        )
        self.play(
            Write(short_signal_words),
            change_width_anim(widths[2])
        )
        self.play(
            long_graph.stretch, 0.35, 0,
            long_graph.set_color, GREEN,
            run_time = 5,
            rate_func = wiggle
        )
        self.wait()
        self.play(
            Write(long_signal_words),
            change_width_anim(widths[0]),
        )
        self.play(
            long_graph.stretch, 0.95, 0,
            long_graph.set_color, average_color(GREEN, BLUE),
            run_time = 4,
            rate_func = wiggle
        )
        self.wait()

class CrossOutDefinitenessAndCertainty(TeacherStudentsScene):
    def construct(self):
        words = VGroup(
            TextMobject("Definiteness"),
            TextMobject("Certainty"),
        )
        words.arrange(DOWN)
        words.next_to(self.teacher, UP+LEFT)
        crosses = VGroup(*list(map(Cross, words)))

        self.add(words)
        self.play(
            self.teacher.change, "sassy",
            ShowCreation(crosses[0])
        )
        self.play(
            self.get_student_changes(*3*["erm"]),
            ShowCreation(crosses[1])
        )
        self.wait(2)

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
                "numbers_to_show" : list(range(1, 10, 1)),
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
        self.set_color_spike()

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
            LaggedStartMap(FadeIn, self.frequency_axes),
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
        self.play(LaggedStartMap(
            Indicate, self.frequency_axes.x_axis.numbers,
            run_time = 4,
            rate_func = wiggle,
        ))
        self.wait()
        self.play(*list(map(FadeOut, [
            self.frequency_axes, fourier_graph,
            signal_label,  fourier_label,
        ])))

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
            run_time = 10
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

    def set_color_spike(self):
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
        graph.set_color(YELLOW)
        return graph

class RealPartOfInsert(Scene):
    def construct(self):
        words = TextMobject("(Real part of the)")
        words.set_color(RED)
        self.add(words)
        self.play(Write(words))
        self.wait(5)

class CenterOfMassDescription(FourierRecapScene):
    def construct(self):
        self.remove(self.pi_creature)
        circle_plane = self.get_circle_plane()
        circle_plane.save_state()
        circle_plane.generate_target()
        circle_plane.target.set_height(FRAME_HEIGHT)
        circle_plane.target.center()
        circle_plane.target.axes.set_stroke(width = 2)
        circle_plane.targets.set_stroke(width = 2)
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
            for factor in (1, 2)
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
            ShowCreation(long_time_graph, rate_func=linear),
            ShowCreation(long_pol_graph, rate_func=linear),
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
        self.play(*list(map(FadeOut, [
            dot, arrow, self.center_of_mass_dot
        ])))
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
            vect *= 1.3/get_norm(vect)
            arrow = Arrow(vect, ORIGIN, buff = SMALL_BUFF)
            arrow.set_color(YELLOW)
            arrow.shift(point)
            dot.arrow = arrow
        return dots

class FocusRectangleInsert(FourierRecapScene):
    CONFIG = {
        "target_width" : 0.5
    }
    def construct(self):
        self.setup_axes()
        self.clear()
        point = self.frequency_axes.coords_to_point(5, 0.25)
        rect = ScreenRectangle(height = 2.1*FRAME_Y_RADIUS)
        rect.set_stroke(YELLOW, 2)
        self.add(rect)
        self.wait()
        self.play(
            rect.stretch_to_fit_width, self.target_width,
            rect.stretch_to_fit_height, 1.5,
            rect.move_to, point,
            run_time = 2
        )
        self.wait(3)

class BroadPeakFocusRectangleInsert(FocusRectangleInsert):
    CONFIG = {
        "target_width" : 1.5,
    }

class CleanerFourierTradeoff(FourierTradeoff):
    CONFIG = {
        "show_text" : False,
        "complex_to_real_func" : lambda z : z.real,
        "widths" : [0.02, 6, 1],
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
        always_shift(plane, LEFT, 1)
        plane.flip()
        pulse = RadarPulse(dish, plane)
        look_at_anims = [
            Mobject.add_updater(
                pi, lambda pi : pi.look_at(pulse.mobject)
            )
            for pi in self.get_pi_creatures()
        ]

        self.add(dish, plane, pulse, *look_at_anims)
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
            arrow.next_to(graph.peak_point, UP, SMALL_BUFF)
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
        distance_text.set_width(0.9*double_arrow.get_width())
        distance_text.next_to(double_arrow, UP, SMALL_BUFF)

        #v_line anim?

        pulse = RadarPulseSingleton(
            dish, randy, 
            speed = 0.97*speed, #Just needs slightly better alignment
        )
        graph_draw = turn_animation_into_updater(
            ShowCreation(
                sum_graph, 
                rate_func=linear, 
                run_time = 0.97*axes.x_max
            )
        )
        randy_look_at = Mobject.add_updater(
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
        self.play(LaggedStartMap(FadeOut, VGroup(
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

        graph_draw = turn_animation_into_updater(
            ShowCreation(sum_graph, run_time = 8, rate_func=linear)
        )
        pulse = RadarPulse(dish, plane, n_pulse_singletons = 12)
        always_shift(plane, LEFT, 1.5)

        self.add(graph_draw, pulse, plane)
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
        self.remove(graph_draw, pulse, plane)

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
        ).set_color(BLUE)
        echo_fourier_brace = Brace(
            Line(
                frequency_axes.coords_to_point(14, 0.4*f_max),
                frequency_axes.coords_to_point(18, 0.4*f_max),
            ),
            UP,
        ).set_color(YELLOW)
        # braces = [original_fourier_brace, echo_fourier_brace]
        # words = ["original signal", "echo"]
        # for brace, word in zip(braces, words):
        #     brace.add(brace.get_text("F.T. of \\\\ %s"%word))
        fourier_label = TexMobject("||\\text{Fourier transform}||")
        # fourier_label.next_to(sum_graph.fourier_transform, UP, MED_LARGE_BUFF)
        fourier_label.next_to(frequency_axes.y_axis, UP, buff = SMALL_BUFF)
        fourier_label.shift_onto_screen()
        fourier_label.set_color(RED)


        #v_lines
        v_line = DashedLine(
            frequency_axes.coords_to_point(8, 0),
            frequency_axes.coords_to_point(8, 1.2*f_max),
            color = YELLOW,
            dash_length = 0.025,
        )
        v_line_pair = VGroup(*[
            v_line.copy().shift(u*0.6*RIGHT)
            for u in (-1, 1)
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
            num_graph_points = echo_graph.get_num_curves(),
            color = WHITE
        )
        sum_graph.background_image_file = "blue_yellow_gradient"
        return pulse_graph, echo_graph, sum_graph

class DopplerFormulaInsert(Scene):
    def construct(self):
        formula = TexMobject(
            "f_{\\text{echo}", "=",
            "\\left(1 + \\frac{v}{c}\\right)",
            "f_{\\text{pulse}}"
        )
        formula[0].set_color(BLUE)
        formula[3].set_color(YELLOW)

        randy = Randolph(color = BLUE_C)
        formula.scale(1.5)
        formula.next_to(randy, UP+LEFT)
        formula.shift_onto_screen()

        self.add(randy)
        self.play(
            LaggedStartMap(FadeIn, formula),
            randy.change, "pondering", randy.get_bottom(),
        )
        self.play(Blink(randy))
        self.wait(2)
        self.play(Blink(randy))
        self.wait()

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
        doppler_shift_words.set_color(YELLOW)
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
        frequency.set_color(YELLOW)
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
            LaggedStartMap(FadeIn, time, run_time = 1)
        )
        self.play(
            GrowFromCenter(brace),
            LaggedStartMap(FadeIn, frequency, run_time = 1)
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
        dish_words.set_color(BLACK)
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
        echo_object.shift(FRAME_X_RADIUS*RIGHT)
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
            ShowCreation(pulse_graph, rate_func=linear),
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
        self.play(LaggedStartMap(
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
        graphs.set_color_by_gradient(BLUE, YELLOW)
        sum_graph = self.axes.get_graph(
            lambda t : sum([
                graph.underlying_function(t)
                for graph in graphs
            ]),
            num_graph_points = 1000
        )

        noise_function = lambda t : np.sum([
            0.5*np.sin(f*t)/f 
            for f in (2, 3, 5, 7, 11, 13)
        ])
        noisy_graph = self.axes.get_graph(
            lambda t : sum_graph.underlying_function(t)*(1+noise_function(t)),
            num_graph_points = 1000
        )
        for graph in sum_graph, noisy_graph:
            graph.background_image_file = "blue_yellow_gradient"

        pulses = self.get_pulses()

        self.play(
            LaggedStartMap(GrowFromCenter, objects[1:]),
            FadeOut(curr_graph),
            randy.change, "pondering"
        )
        self.add(*pulses)
        self.wait(0.5)
        self.play(
            ShowCreation(
                sum_graph,
                rate_func=linear,
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
                rate_func=linear,
                run_time = 3.5,
            ),
            randy.change, "happy"
        )
        self.wait()

        self.curr_graph = sum_graph
        self.first_echo_graph = graphs[0]
        self.first_echo_graph.set_color(YELLOW)

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
            LaggedStartMap(FadeOut, self.objects),
            LaggedStartMap(FadeOut, VGroup(
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
            always_shift(
                obj, 
                direction = v/get_norm(v),
                rate = get_norm(v)
            )
            for v, obj in zip(object_velocities, objects)
        ]
        pulses = self.get_pulses()
        continual_anims = pulses+movements
        
        self.play(
            FadeOut(self.axes),
            FadeOut(self.first_echo_graph),
            LaggedStartMap(FadeIn, objects),
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
        shifted_graphs.set_color_by_gradient(
            average_color(color, WHITE), 
            color,
            average_color(color, BLACK),
        )
        sum_graph = self.get_sum_graph(frequency_axes, shifted_graphs)
        sum_graph.match_style(fourier_graph)

        shifted_graphs.save_state()

        self.play(ReplacementTransform(
            VGroup(fourier_graph), shifted_graphs,
            lag_ratio = 0.5,
            run_time = 2
        ))
        self.wait()
        self.play(
            shifted_graphs.arrange, DOWN,
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
        new_fourier_graph.set_color(PINK)

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
        shifted_graphs = VGroup(*list(map(
            get_graph, list(map(get_func, self.object_velocities))
        )))
        shifted_graphs.match_style(fourier_graph)
        return shifted_graphs

    def get_sum_graph(self, axes, graphs):
        def get_func(graph):
            return graph.underlying_function
        funcs = list(map(get_func, graphs))
        return axes.get_graph(
            lambda t : sum([func(t) for func in funcs]),
        )

class SummarizeFourierTradeoffForDoppler(Scene):
    def construct(self):
        time_axes = Axes(
            x_min = 0, x_max = 12,
            y_min = -0.5, y_max = 1,
        )
        time_axes.center().to_edge(UP, buff = LARGE_BUFF)
        frequency_axes = time_axes.copy()
        frequency_axes.next_to(time_axes, DOWN, buff = 2)
        time_label = TextMobject("Time")
        frequency_label = TextMobject("Frequency")
        for label, axes in (time_label, time_axes), (frequency_label, frequency_axes):
            label.next_to(axes.get_right(), UP, SMALL_BUFF)
            axes.add(label)
        frequency_label.shift_onto_screen()
        title = TextMobject("Fourier Trade-off")
        title.next_to(time_axes, DOWN)
        self.add(title)


        #Position determines log of scale value for exponentials
        a_mob = VectorizedPoint()
        x_values = [3, 5, 6, 7, 8]
        v_values = [5, 5.5, 5.75, 6.5, 7]
        def get_top_graphs():
            a = np.exp(a_mob.get_center()[0])
            graphs = VGroup(*[
                time_axes.get_graph(lambda t : np.exp(-5*a*(t-x)**2))
                for x in x_values
            ])
            graphs.set_color(WHITE)
            graphs.color_using_background_image("blue_yellow_gradient")
            return graphs
        def get_bottom_graphs():
            a = np.exp(a_mob.get_center()[0])
            graphs = VGroup(*[
                frequency_axes.get_graph(lambda t : np.exp(-(5./a)*(t-v)**2))
                for v in v_values
            ])
            graphs.set_color(RED)
            return graphs

        top_graphs = get_top_graphs()
        bottom_graphs = get_bottom_graphs()
        update_top_graphs = Mobject.add_updater(
            top_graphs, 
            lambda g : Transform(g, get_top_graphs()).update(1)
        )
        update_bottom_graphs = Mobject.add_updater(
            bottom_graphs, 
            lambda g : Transform(g, get_bottom_graphs()).update(1)
        )

        self.add(time_axes, frequency_axes)
        self.add(update_top_graphs, update_bottom_graphs)

        shift_vect = 2*RIGHT
        for s in 1, -2, 1:
            self.play(a_mob.shift, s*shift_vect, run_time = 3)

class MentionUncertaintyPrincipleCopy(MentionUncertaintyPrinciple):
    pass

class IntroduceDeBroglie(Scene):
    CONFIG = {
        "default_wave_frequency" : 1,
        "wave_colors" : [BLUE_D, YELLOW],
        "dispersion_factor" : 1,
        "amplitude" : 1,
    }
    def construct(self):
        text_scale_val = 0.8,

        #Overlay real tower in video editor
        eiffel_tower = Line(3*DOWN, 3*UP, stroke_width = 0)
        picture = ImageMobject("de_Broglie")
        picture.set_height(4)
        picture.to_corner(UP+LEFT)
        name = TextMobject("Louis de Broglie")
        name.next_to(picture, DOWN)

        picture.save_state()
        picture.scale(0)
        picture.move_to(eiffel_tower.get_top())


        broadcasts = [
            Broadcast(
                eiffel_tower.get_top(),
                big_radius = 10,
                n_circles = 10,
                lag_ratio = 0.9,
                run_time = 7,
                rate_func = squish_rate_func(smooth, a, a+0.3),
                color = WHITE,
            )
            for a in np.linspace(0, 0.7, 3)
        ]

        self.play(*broadcasts)
        self.play(picture.restore)
        self.play(Write(name))
        self.wait()

        #Time line
        time_line = NumberLine(
            x_min = 1900,
            x_max = 1935,
            tick_frequency = 1,
            numbers_with_elongated_ticks = list(range(1900, 1941, 10)),
            color = BLUE_D
        )
        time_line.stretch_to_fit_width(FRAME_WIDTH - picture.get_width() - 2)
        time_line.add_numbers(*time_line.numbers_with_elongated_ticks)
        time_line.next_to(picture, RIGHT, MED_LARGE_BUFF, DOWN)

        year_to_words = {
            1914 : "Wold War I begins",
            1915 : "Einstein field equations",
            1916 : "Lewis dot formulas",
            1917 : "Not a lot of physics...because war",
            1918 : "S'more Rutherford badassery",
            1919 : "Eddington confirms general relativity predictions",
            1920 : "World is generally stoked on general relativity",
            1921 : "Einstein gets long overdue Nobel prize",
            1922 : "Stern-Gerlach Experiment",
            1923 : "Compton scattering observed",
            1924 : "de Broglie's thesis"
        }
        arrow = Vector(DOWN, color = WHITE)
        arrow.next_to(time_line.number_to_point(1914), UP)
        words = TextMobject(year_to_words[1914])
        words.scale(text_scale_val)
        date = Integer(1914)
        date.next_to(arrow, UP, LARGE_BUFF)

        def get_year(alpha = 0):
            return int(time_line.point_to_number(arrow.get_end()))

        def update_words(words):
            text = year_to_words.get(get_year(), "Hi there")
            if text not in words.get_tex_string():
                words.__init__(text)
                words.scale(text_scale_val)
            words.move_to(interpolate(
                arrow.get_top(), date.get_bottom(), 0.5
            ))
        update_words(words)
        self.play(
            FadeIn(time_line),
            GrowArrow(arrow),
            Write(words),
            Write(date),
            run_time = 1
        )
        self.wait()
        self.play(
            arrow.next_to, time_line.number_to_point(1924), UP,
            ChangingDecimal(
                date, get_year,
                position_update_func = lambda m : m.next_to(arrow, UP, LARGE_BUFF)
            ),
            UpdateFromFunc(words, update_words),
            run_time = 3,
        )
        self.wait()

        #Transform time_line
        line = time_line
        self.play(
            FadeOut(time_line.numbers),
            VGroup(arrow, words, date).shift, MED_LARGE_BUFF*UP,
            *[
                ApplyFunction(
                    lambda m : m.rotate(TAU/4).set_stroke(width = 0),
                    mob,
                    remover = True
                )
                for mob in time_line.tick_marks
            ]
        )

        #Wave function
        particle = VectorizedPoint()
        axes = Axes(x_min = -1, x_max = 10)
        axes.match_width(line)
        axes.shift(line.get_center() - axes.x_axis.get_center())
        im_line = line.copy()
        im_line.set_color(YELLOW)
        wave_update_animation = self.get_wave_update_animation(
            axes, particle, line, im_line
        )

        for x in range(3):
            particle.move_to(axes.coords_to_point(-10, 0))
            self.play(
                ApplyMethod(
                    particle.move_to, axes.coords_to_point(22, 0),
                    rate_func=linear
                ),
                wave_update_animation,
                run_time = 3
            )
            self.wait()

    ###
    def get_wave_update_animation(self, axes, particle, re_line = None, im_line = None):
        line = Line(
            axes.x_axis.get_left(),
            axes.x_axis.get_right(),
        )
        if re_line is None:
            re_line = line.copy()
            re_line.set_color(self.wave_colors[0])
        if im_line is None:
            im_line = line.copy()
            im_line.set_color(self.wave_colors[1])
        lines = VGroup(im_line, re_line)
        def update_lines(lines):
            waves = self.get_wave_pair(axes, particle)
            for line, wave in zip(lines, waves):
                wave.match_style(line)
                Transform(line, wave).update(1)
        return UpdateFromFunc(lines, update_lines)

    def get_wave(
        self, axes, particle, 
        complex_to_real_func = lambda z : z.real,
        freq = None, 
        **kwargs):
        freq = freq or self.default_wave_frequency
        k0 = 1./freq
        t0 = axes.x_axis.point_to_number(particle.get_center())
        def func(x):
            dispersion = fdiv(1., self.dispersion_factor)*(np.sqrt(1./(1+t0**2)))
            wave_part = complex_to_real_func(np.exp(
                complex(0, TAU*freq*(x-dispersion))
            ))
            bell_part = np.exp(-dispersion*(x-t0)**2)
            amplitude = self.amplitude
            return amplitude*wave_part*bell_part
        graph = axes.get_graph(func)
        return graph

    def get_wave_pair(self, axes, particle, colors = None, **kwargs):
        if colors is None and "color" not in kwargs:
            colors = self.wave_colors
        return VGroup(*[
            self.get_wave(
                axes, particle, 
                C_to_R, color = color, 
                **kwargs
            )
            for C_to_R, color in zip(
                [lambda z : z.imag, lambda z : z.real], 
                colors
            )
        ])

class ShowMomentumFormula(IntroduceDeBroglie, TeacherStudentsScene):
    CONFIG = {
        "default_wave_frequency" : 2,
        "dispersion_factor" : 0.25,
        "p_color" : BLUE,
        "xi_color" : YELLOW,
        "amplitude" : 0.5,
    }
    def construct(self):
        self.introduce_formula()
        self.react_to_claim()

    def introduce_formula(self):
        formula = p, eq, h, xi = TexMobject("p", "=", "h", "\\xi")
        formula.move_to(ORIGIN)
        formula.scale(1.5)

        word_shift_val = 1.75
        p_words = TextMobject("Momentum")
        p_words.next_to(p, UP, LARGE_BUFF).shift(word_shift_val*LEFT)
        p_arrow = Arrow(
            p_words.get_bottom(), p.get_corner(UP+LEFT),
            buff = SMALL_BUFF
        )
        added_p_words = TextMobject("(Classically $m \\times v$)")
        added_p_words.move_to(p_words, DOWN)
        VGroup(p, p_words, added_p_words, p_arrow).set_color(self.p_color)

        xi_words = TextMobject("Spatial frequency")
        added_xi_words = TextMobject("(cycles per unit \\emph{distance})")
        xi_words.next_to(xi, UP, LARGE_BUFF).shift(word_shift_val*RIGHT)
        xi_words.align_to(p_words)
        xi_arrow = Arrow(
            xi_words.get_bottom(), xi.get_corner(UP+RIGHT), 
            buff = SMALL_BUFF
        )
        added_xi_words.move_to(xi_words, DOWN)
        added_xi_words.align_to(added_p_words, DOWN)
        VGroup(xi, xi_words, added_xi_words, xi_arrow).set_color(self.xi_color)

        axes = Axes(
            x_min = 0, x_max = FRAME_WIDTH,
            y_min = -1, y_max = 1,
        )
        axes.center().to_edge(UP, buff = -0.5)
        # axes.next_to(formula, RIGHT)
        particle = VectorizedPoint()
        wave_update_animation = self.get_wave_update_animation(axes, particle)
        wave = wave_update_animation.mobject
        wave[0].set_stroke(width = 0)
        particle.next_to(wave, LEFT, buff = 2)
        wave_propagation = AnimationGroup(
            ApplyMethod(particle.move_to, axes.coords_to_point(30, 0)),
            wave_update_animation,
            run_time = 4,
            rate_func=linear,
        )
        stopped_wave_propagation = AnimationGroup(
            ApplyMethod(particle.move_to, xi_words),
            wave_update_animation,
            run_time = 3,
            rate_func=linear,
        )
        n_v_lines = 10
        v_lines = VGroup(*[
            DashedLine(UP, DOWN)
            for x in range(n_v_lines)
        ])
        v_lines.match_color(xi)
        v_lines.arrange(
            RIGHT,
            buff = float(axes.x_axis.unit_size)/self.default_wave_frequency
        )
        v_lines.move_to(stopped_wave_propagation.sub_anims[0].target_mobject)
        v_lines.align_to(wave)
        v_lines.shift(0.125*RIGHT)
        
        self.add(formula, wave)
        self.play(
            self.teacher.change, "raise_right_hand", 
            GrowArrow(p_arrow),
            Succession(
                Write, p_words,
                ApplyMethod, p_words.next_to, added_p_words, UP,
            ),
            FadeIn(
                added_p_words,
                rate_func = squish_rate_func(smooth, 0.5, 1),
                run_time = 2,
            ),
            wave_propagation
        )
        self.play(
            Write(xi_words),
            GrowArrow(xi_arrow),
            self.get_student_changes("confused", "erm", "sassy"),
            stopped_wave_propagation
        )
        self.play(
            FadeIn(added_xi_words),
            xi_words.next_to, added_xi_words, UP,
        )
        self.play(
            LaggedStartMap(ShowCreation, v_lines),
            self.get_student_changes(*["pondering"]*3)
        )
        self.play(LaggedStartMap(FadeOut, v_lines))
        self.wait()

        self.formula_labels = VGroup(
            p_words, p_arrow, added_p_words,
            xi_words, xi_arrow, added_xi_words, 
        )        
        self.set_variables_as_attrs(wave, wave_propagation, formula)

    def react_to_claim(self):
        formula_labels = self.formula_labels
        full_formula = VGroup(self.formula, formula_labels)
        full_formula.save_state()
        wave_propagation = self.wave_propagation

        student = self.students[2]
        self.student_says(
            "Hang on...",
            bubble_kwargs = {"height" : 2, "width" : 2, "direction" : LEFT},
            target_mode = "sassy",
            student_index = 2,
            added_anims = [self.teacher.change, "plain"]
        )
        student.bubble.add(student.bubble.content)
        self.wait()
        kwargs = {
            "path_arc" : TAU/4,
            "lag_ratio" : 0.5,
            "lag_ratio" : 0.7,
            "run_time" : 1.5,
        }
        self.play(
            full_formula.scale, 0,
            full_formula.move_to, student.eyes.get_bottom()+SMALL_BUFF*DOWN,
            Animation(student.bubble),
            **kwargs
        )
        self.play(full_formula.restore, Animation(student.bubble), **kwargs)
        wave_propagation.update_config(
            rate_func = lambda a : interpolate(0.35, 1, a)
        )
        self.play(
            wave_propagation, 
            RemovePiCreatureBubble(student, target_mode = "confused"),
        )
        wave_propagation.update_config(rate_func = lambda t : t)
        self.student_says(
            "Physics is \\\\ just weird",
            bubble_kwargs = {"height" : 2.5, "width" : 3},
            target_mode = "shruggie",
            student_index = 0,
            added_anims = [ApplyMethod(full_formula.shift, UP)]
        )
        self.wait()
        self.play(
            wave_propagation,
            ApplyMethod(full_formula.shift, DOWN),
            FadeOut(self.students[0].bubble),
            FadeOut(self.students[0].bubble.content),
            self.get_student_changes(*3*["pondering"]),
            self.teacher.change, "pondering",
        )
        self.play(wave_propagation)

class AskPhysicists(PiCreatureScene):
    def construct(self):
        morty, physy1, physy2, physy3 = self.pi_creatures
        formula = TexMobject("p", "=", "h", "\\xi")
        formula.set_color_by_tex_to_color_map({
            "p" : BLUE,
            "\\xi" : YELLOW,
        })
        formula.scale(1.5)

        formula.to_edge(UP)
        formula.save_state()
        formula.shift(DOWN)
        formula.fade(1)
        self.play(formula.restore)
        self.pi_creature_says(
            morty, "So...why?",
            target_mode = "maybe"
        )
        self.wait(2)
        self.play(
            RemovePiCreatureBubble(morty),
            PiCreatureSays(
                physy2,
                "Take the Schrödinger equation \\\\ with $H = \\frac{p^2}{2m}+V(x)$",
                bubble_kwargs = {"fill_opacity" : 0.9},
            ),
        )
        self.play(
            PiCreatureSays(
                physy1,
                "Even classically position and \\\\ momentum are conjugate",
                target_mode = "surprised",
                bubble_kwargs = {"fill_opacity" : 0.9},
            ),
        )
        self.play(
            PiCreatureSays(
                physy3,
                "Consider special relativity \\\\ together with $E = hf$",
                target_mode = "hooray",
                bubble_kwargs = {"fill_opacity" : 0.9},
            ),
            morty.change, "guilty"
        )
        self.wait(2)



    ###

    def create_pi_creatures(self):
        scale_factor = 0.85
        morty = Mortimer().flip()
        morty.scale(scale_factor)
        morty.to_corner(DOWN+LEFT)

        physies = VGroup(*[
            PiCreature(color = c).flip()
            for c in (GREY, LIGHT_GREY, DARK_GREY)
        ])
        physies.arrange(RIGHT, buff = MED_SMALL_BUFF)
        physies.scale(scale_factor)
        physies.to_corner(DOWN+RIGHT)

        self.add(physies)
        return VGroup(morty, *physies)

class SortOfDopplerEffect(PiCreatureScene):
    CONFIG = {
        "omega" : np.pi,
        "arrow_spacing" : 0.25,
    }
    def setup(self):
        PiCreatureScene.setup(self)
        rect = self.screen_rect = ScreenRectangle(height = FRAME_HEIGHT)
        rect.set_stroke(width = 0)
        self.camera = MovingCamera(
            rect, **self.camera_config
        )

    def construct(self):
        screen_rect = self.screen_rect

        #x-coordinate gives time
        t_tracker = VectorizedPoint()
        #x-coordinate gives wave number
        k_tracker = VectorizedPoint(2*RIGHT)
        always_shift(t_tracker, RIGHT, 1)
        def get_wave():
            t = t_tracker.get_center()[0]
            k = k_tracker.get_center()[0]
            omega = self.omega
            color = interpolate_color(
                BLUE, RED, (k-2)/2.0
            )
            func = lambda x : 0.5*np.cos(omega*t - k*x)
            graph = FunctionGraph(
                func,
                x_min = -5*FRAME_X_RADIUS,
                x_max = FRAME_X_RADIUS,
                color = color,
            )
            return VGroup(graph, *[
                Arrow(
                    x*RIGHT, x*RIGHT + func(x)*UP, 
                    color = color
                )
                for x in np.arange(
                    -4*FRAME_X_RADIUS, FRAME_X_RADIUS, 
                    self.arrow_spacing
                )
            ])
            return 
        wave = get_wave()
        wave_update = Mobject.add_updater(
            wave, lambda w : Transform(w, get_wave()).update(1)
        )

        rect = ScreenRectangle(height = 2)
        rect.to_edge(RIGHT)
        always_shift(rect, LEFT, 1)
        rect_movement = rect

        randy = self.pi_creature
        randy_look_at = Mobject.add_updater(
            randy, lambda r : r.look_at(rect)
        )

        ref_frame1 = TextMobject("Reference frame 1")
        # ref_frame1.next_to(randy, UP, aligned_edge = LEFT)
        ref_frame1.to_edge(UP)
        ref_frame2 = TextMobject("Reference frame 2")
        ref_frame2.next_to(rect, UP)
        # ref_frame2.set_fill(opacity = 0)
        ref_frame2_follow = Mobject.add_updater(
            ref_frame2, lambda m : m.next_to(rect, UP)
        )
        ref_frame_1_continual_anim = ContinualAnimation(ref_frame1)

        self.add(
            t_tracker, wave_update, rect_movement, randy_look_at,
            ref_frame2_follow, ref_frame_1_continual_anim
        )
        self.add(ref_frame1)
        self.play(randy.change, "pondering")
        self.wait(4)
        start_height = screen_rect.get_height()
        start_center = screen_rect.get_center()
        self.play(
            UpdateFromAlphaFunc(
                screen_rect,
                lambda m, a : m.move_to(
                    interpolate(start_center, rect.get_center(), a)
                )
            ),
            k_tracker.shift, 2*RIGHT,
        )
        self.play(
            MaintainPositionRelativeTo(
                screen_rect, rect,
                run_time = 4
            ),
        )
        self.play(
            screen_rect.move_to, rect.get_right()+FRAME_X_RADIUS*LEFT,
            k_tracker.shift, 2*LEFT,
        )

        #Frequency words
        temporal_frequency = TextMobject("Temporal", "frequency")
        spatial_frequency = TextMobject("Spatial", "frequency")
        temporal_frequency.move_to(screen_rect).to_edge(UP)
        spatial_frequency.next_to(temporal_frequency, DOWN)
        cross = Cross(temporal_frequency[0])

        time = TextMobject("Time")
        space = TextMobject("Space")
        time.next_to(temporal_frequency, RIGHT, buff = 2)
        space.next_to(time, DOWN)
        space.align_to(spatial_frequency)

        self.play(FadeIn(temporal_frequency))
        self.play(ShowCreation(cross))
        self.play(Write(spatial_frequency))
        self.wait()
        self.play(FadeIn(time), FadeIn(space))
        self.play(
            Transform(time, space),
            Transform(space, time),
            lag_ratio = 0.5,
            run_time = 1,
        )
        self.play(FadeOut(time), FadeOut(space))
        self.wait(3)

    ###

    def create_pi_creature(self):
        return Randolph().scale(0.5).to_corner(DOWN+LEFT)

class HangingWeightsScene(MovingCameraScene):
    CONFIG = {
        "frequency" : 0.5,
        "ceiling_radius" : 3*FRAME_X_RADIUS,
        "n_springs" : 72,
        "amplitude" : 0.6,
        "spring_radius" : 0.15,
    }
    def construct(self):
        self.setup_springs()
        self.setup_weights()
        self.introduce()
        self.show_analogy_with_electron()
        self.metaphor_for_something()
        self.moving_reference_frame()

    def setup_springs(self):
        ceiling = self.ceiling = Line(LEFT, RIGHT)
        ceiling.scale(self.ceiling_radius)
        ceiling.to_edge(UP, buff = LARGE_BUFF)
        self.add(ceiling)

        def get_spring(alpha, height = 2):
            t_max = 6.5
            r = self.spring_radius
            s = (height - r)/(t_max**2)
            spring = ParametricFunction(
                lambda t : op.add(
                    r*(np.sin(TAU*t)*RIGHT+np.cos(TAU*t)*UP),
                    s*((t_max - t)**2)*DOWN,
                ),
                t_min = 0, t_max = t_max,
                color = WHITE,
                stroke_width = 2,
            )
            spring.alpha = alpha
            spring.move_to(ceiling.point_from_proportion(alpha), UP)
            spring.color_using_background_image("grey_gradient")
            return spring
        alphas = np.linspace(0, 1, self.n_springs)
        bezier([0, 1, 0, 1])
        springs = self.springs = VGroup(*list(map(get_spring, alphas)))

        k_tracker = self.k_tracker = VectorizedPoint()
        t_tracker = self.t_tracker = VectorizedPoint()
        always_shift(t_tracker, RIGHT, 1)
        self.t_tracker_walk = t_tracker
        equilibrium_height = springs.get_height()
        def update_springs(springs):
            for spring in springs:
                k = k_tracker.get_center()[0]
                t = t_tracker.get_center()[0]
                f = self.frequency
                x = spring.get_top()[0]
                A = self.amplitude
                d_height = A*np.cos(TAU*f*t - k*x)
                new_spring = get_spring(spring.alpha, 2+d_height)
                Transform(spring, new_spring).update(1)
        spring_update_anim = Mobject.add_updater(springs, update_springs)
        self.spring_update_anim = spring_update_anim
        spring_update_anim.update(0)

        self.play(
            ShowCreation(ceiling),
            LaggedStartMap(ShowCreation, springs)
        )

    def setup_weights(self):
        weights = self.weights = VGroup()
        weight_anims = weight_anims = []
        for spring in self.springs:
            x = spring.get_top()[0]
            mass = np.exp(-0.1*x**2)
            weight = Circle(radius = 0.15)
            weight.start_radius = 0.15
            weight.target_radius = 0.25*mass #For future update
            weight.spring = spring
            weight_anim = Mobject.add_updater(
                weight, lambda w : w.move_to(w.spring.get_bottom())
            )
            weight_anim.update(0)
            weight_anims.append(weight_anim)
            weights.add(weight)
        weights.set_fill(opacity = 1)
        weights.set_color_by_gradient(BLUE_D, BLUE_E, BLUE_D)
        weights.set_stroke(WHITE, 1)

        self.play(LaggedStartMap(GrowFromCenter, weights))
        self.add(self.t_tracker_walk)
        self.add(self.spring_update_anim)
        self.add(*weight_anims)

    def introduce(self):
        arrow = Arrow(4*LEFT, LEFT)
        arrows = VGroup(arrow, arrow.copy().flip(about_point = ORIGIN))
        arrows.set_color(WHITE)

        self.wait(3)
        self.play(*list(map(GrowArrow, arrows)))
        self.play(*[
            UpdateFromAlphaFunc(
                weight, lambda w, a : w.set_width(
                    2*interpolate(w.start_radius, w.target_radius, a)
                ),
                run_time = 2
            )
            for weight in self.weights
        ])
        self.play(FadeOut(arrows))
        self.wait(3)

    def show_analogy_with_electron(self):
        words = TextMobject(
            "Analogous to the energy of a particle \\\\",
            "(in the sense of $E=mc^2$)"
        )
        words.move_to(DOWN)

        self.play(Write(words))
        self.wait(3)
        self.play(FadeOut(words))

    def metaphor_for_something(self):
        de_broglie = ImageMobject("de_Broglie")
        de_broglie.set_height(3.5)
        de_broglie.to_corner(DOWN+RIGHT)
        words = TextMobject("""
            If a photon's energy is carried as a wave \\\\
            is this true for any particle?
        """)
        words.next_to(de_broglie, LEFT)

        einstein = ImageMobject("Einstein")
        einstein.match_height(de_broglie)
        einstein.to_corner(DOWN+LEFT)

        for picture in de_broglie, einstein:
            picture.backdrop = Rectangle()
            picture.backdrop.replace(picture, stretch = True)
            picture.backdrop.set_fill(BLACK, 1)
            picture.backdrop.set_stroke(BLACK, 0)

        self.play(
            Animation(de_broglie.backdrop, remover = True),
            FadeIn(de_broglie)
        )
        self.play(Write(words))
        self.wait(7)
        self.play(
            FadeOut(words),
            Animation(einstein.backdrop, remover = True),
            FadeIn(einstein)
        )
        self.wait(2)

        self.de_broglie = de_broglie
        self.einstein = einstein

    def moving_reference_frame(self):
        rect = ScreenRectangle(height = 2.1*FRAME_Y_RADIUS)
        rect_movement = always_shift(rect, direction = LEFT, rate = 2)
        camera_frame = self.camera_frame

        self.add(rect)
        self.play( 
            Animation(self.de_broglie.backdrop, remover = True),
            FadeOut(self.de_broglie),
            Animation(self.einstein.backdrop, remover = True),
            FadeOut(self.einstein),
        )
        self.play(camera_frame.scale, 3, {"about_point" : 2*UP})
        self.play(rect.shift, FRAME_WIDTH*RIGHT, path_arc = -TAU/2)
        self.add(rect_movement)
        self.wait(3)

        def zoom_into_reference_frame():
            original_height = camera_frame.get_height()
            original_center = camera_frame.get_center()
            self.play(
                UpdateFromAlphaFunc(
                    camera_frame, lambda c, a : c.set_height(
                        interpolate(original_height, 0.95*rect.get_height(), a)
                    ).move_to(
                        interpolate(original_center, rect.get_center(), a)
                    )
                ),
                ApplyMethod(self.k_tracker.shift, RIGHT)
            )
            self.play(MaintainPositionRelativeTo(
                camera_frame, rect,
                run_time = 6
            ))
            self.play(
                camera_frame.set_height, original_height,
                camera_frame.move_to, original_center,
                ApplyMethod(self.k_tracker.shift, LEFT)
            )

        zoom_into_reference_frame()
        self.wait()
        self.play(
            UpdateFromAlphaFunc(rect, lambda m, a : m.set_stroke(width = 2*(1-a)))
        )

        index = int(0.5*len(self.springs))
        weights = VGroup(self.weights[index], self.weights[index+4])
        flashes = list(map(self.get_peak_flash_anim, weights))
        weights.save_state()
        weights.set_fill(RED)
        self.add(*flashes)
        self.wait(5)

        rect.align_to(camera_frame, RIGHT)
        self.play(UpdateFromAlphaFunc(rect, lambda m, a : m.set_stroke(width = 2*a)))

        randy = Randolph(mode = "pondering")
        randy.look(UP+RIGHT)
        de_broglie = ImageMobject("de_Broglie")
        de_broglie.set_height(6)
        de_broglie.next_to(4*DOWN, DOWN)
        self.add(
            Mobject.add_updater(
                randy, lambda m : m.next_to(
                    rect.get_corner(DOWN+LEFT), UP+RIGHT, MED_LARGE_BUFF,
                ).look_at(weights)
            ),
            de_broglie
        )
        self.wait(2)

        zoom_into_reference_frame()
        self.wait(8)

    ###

    def get_peak_flash_anim(self, weight):
        mobject = Mobject() #Dummy
        mobject.last_y = 0
        mobject.last_dy = 0
        mobject.curr_anim = None
        mobject.curr_anim_time = 0
        mobject.time_since_last_flash = 0
        def update(mob, dt):
            mob.time_since_last_flash += dt
            point = weight.get_center()
            y = point[1]
            mob.dy = y - mob.last_y
            different_dy = np.sign(mob.dy) != np.sign(mob.last_dy)
            if different_dy and mob.time_since_last_flash > 0.5:
                mob.curr_anim = Flash(
                    VectorizedPoint(point),
                    flash_radius = 0.5,
                    line_length = 0.3,
                    run_time = 0.2,
                )
                mob.submobjects = [mob.curr_anim.mobject]
                mob.time_since_last_flash = 0
            mob.last_y = float(y)
            mob.last_dy = float(mob.dy)
            ##
            if mob.curr_anim:
                mob.curr_anim_time += dt
                if mob.curr_anim_time > mob.curr_anim.run_time:
                    mob.curr_anim = None
                    mob.submobjects = []
                    mob.curr_anim_time = 0
                    return
                mob.curr_anim.update(mob.curr_anim_time/mob.curr_anim.run_time)

        return Mobject.add_updater(mobject, update)

class MinutPhysicsWrapper(Scene):
    def construct(self):
        logo = ImageMobject("minute_physics_logo", invert = True)
        logo.to_corner(UP+LEFT)
        self.add(logo)

        title = TextMobject("Minute Physics on special relativity")
        title.to_edge(UP).shift(MED_LARGE_BUFF*RIGHT)

        screen_rect = ScreenRectangle()
        screen_rect.set_width(title.get_width() + LARGE_BUFF)
        screen_rect.next_to(title, DOWN)

        self.play(ShowCreation(screen_rect))
        self.play(Write(title))
        self.wait(2)

class WhatDoesTheFourierTradeoffTellUs(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "So! What does \\\\ the Fourier trade-off \\\\ tell us?",
            target_mode = "surprised",
            bubble_kwargs = {"width" : 4, "height" : 3}
        )
        self.change_student_modes(*["thinking"]*3)
        self.wait(4)

class FourierTransformOfWaveFunction(Scene):
    CONFIG = {
        "wave_stroke_width" : 3,
        "wave_color" : BLUE,
    }
    def construct(self):
        self.show_wave_packet()
        self.take_fourier_transform()
        self.show_correlations_with_pure_frequencies()
        self.this_is_momentum()
        self.show_tradeoff()

    def setup(self):
        self.x0_tracker = ValueTracker(-3)
        self.k_tracker = ValueTracker(1)
        self.a_tracker = ExponentialValueTracker(0.5)

    def show_wave_packet(self):
        axes = Axes(
            x_min = 0, x_max = 12,
            y_min = -1, y_max = 1,
            y_axis_config = {
                "tick_frequency" : 0.5
            }
        )
        position_label = TextMobject("Position")
        position_label.next_to(axes.x_axis.get_right(), UP)
        axes.add(position_label)
        axes.center().to_edge(UP, buff = LARGE_BUFF)

        wave = self.get_wave(axes)
        wave_update_animation = UpdateFromFunc(
            wave, lambda w : Transform(w, self.get_wave(axes)).update(1)
        )

        self.add(axes, wave)
        self.play(
            self.x0_tracker.set_value, 5,
            wave_update_animation,
            run_time = 3,
        )
        self.wait()

        self.wave_function = wave.underlying_function
        self.wave_update_animation = wave_update_animation
        self.wave = wave
        self.axes = axes

    def take_fourier_transform(self):
        wave = self.wave
        wave_update_animation = self.wave_update_animation
        frequency_axes = Axes(
            x_min = 0, x_max = 3,
            x_axis_config = {
                "unit_size" : 4,
                "tick_frequency" : 0.25,
                "numbers_with_elongated_ticks" : [1, 2]
            },
            y_min = -0.15,
            y_max = 0.15,
            y_axis_config = {
                "unit_size" : 7.5,
                "tick_frequency" : 0.05,
            }
        )
        label = self.frequency_x_axis_label = TextMobject("Spatial frequency")
        label.next_to(frequency_axes.x_axis.get_right(), UP)
        frequency_axes.add(label)
        frequency_axes.move_to(self.axes, LEFT)
        frequency_axes.to_edge(DOWN, buff = LARGE_BUFF)
        label.shift_onto_screen()

        def get_wave_function_fourier_graph():
            return get_fourier_graph(
                frequency_axes, self.get_wave_func(),
                t_min = 0, t_max = 15,
            )
        fourier_graph = get_wave_function_fourier_graph()
        self.fourier_graph_update_animation = UpdateFromFunc(
            fourier_graph, lambda m : Transform(
                m, get_wave_function_fourier_graph()
            ).update(1)
        )

        wave_copy = wave.copy()
        wave_copy.generate_target()
        wave_copy.target.move_to(fourier_graph, LEFT)
        wave_copy.target.fade(1)
        fourier_graph.save_state()
        fourier_graph.move_to(wave, LEFT)
        fourier_graph.fade(1)

        arrow = Arrow(
            self.axes.coords_to_point(5, -1),
            frequency_axes.coords_to_point(1, 0.1),
            color = YELLOW,
        )
        fourier_label = TextMobject("Fourier Transform")
        fourier_label.next_to(arrow.get_center(), RIGHT)

        self.play(ReplacementTransform(
            self.axes.copy(), frequency_axes
        ))
        self.play(
            MoveToTarget(wave_copy, remover = True),
            fourier_graph.restore,
            GrowArrow(arrow),
            Write(fourier_label, run_time = 1),
        )
        self.wait()

        self.frequency_axes = frequency_axes
        self.fourier_graph = fourier_graph
        self.fourier_label = VGroup(arrow, fourier_label)

    def show_correlations_with_pure_frequencies(self):
        frequency_axes = self.frequency_axes
        axes = self.axes

        sinusoid = axes.get_graph(
            lambda x : 0.5*np.cos(TAU*x),
            x_min = -FRAME_X_RADIUS, x_max = 3*FRAME_X_RADIUS,
        )
        sinusoid.to_edge(UP, buff = SMALL_BUFF)

        v_line = DashedLine(1.5*UP, ORIGIN, color = YELLOW)
        v_line.move_to(frequency_axes.coords_to_point(1, 0), DOWN)

        f_equals = TexMobject("f = ")
        freq_decimal = DecimalNumber(1)
        freq_decimal.next_to(f_equals, RIGHT, buff = SMALL_BUFF)
        freq_label = VGroup(f_equals, freq_decimal)
        freq_label.next_to(
            v_line, UP, SMALL_BUFF, 
            submobject_to_align = f_equals[0]
        )

        self.play(
            ShowCreation(sinusoid),
            ShowCreation(v_line),
            Write(freq_label, run_time = 1),
            FadeOut(self.fourier_label)
        )
        last_f = 1
        for f in 1.4, 0.7, 1:
            self.play(
                sinusoid.stretch,f/last_f, 0, 
                    {"about_point" : axes.coords_to_point(0, 0)},
                v_line.move_to, frequency_axes.coords_to_point(f, 0), DOWN,
                MaintainPositionRelativeTo(freq_label, v_line),
                ChangeDecimalToValue(freq_decimal, f),
                run_time = 3,
            )
            last_f = f
        self.play(*list(map(FadeOut, [
            sinusoid, v_line,  freq_label
        ])))

    def this_is_momentum(self):
        formula = TexMobject("p", "=", "h", "\\xi")
        formula.set_color_by_tex_to_color_map({
            "p" : BLUE,
            "xi" : YELLOW,
        })
        formula.next_to(
            self.frequency_x_axis_label, UP
        )

        f_max = 0.12
        brace = Brace(Line(2*LEFT, 2*RIGHT), UP)
        brace.move_to(self.frequency_axes.coords_to_point(1, f_max), DOWN)
        words = TextMobject("This wave \\\\ describes momentum")
        words.next_to(brace, UP)

        self.play(Write(formula))
        self.wait()
        self.play(
            GrowFromCenter(brace),
            Write(words)
        )
        brace.add(words)
        for k in 2, 0.5, 1:
            self.play(
                self.k_tracker.set_value, k,
                self.wave_update_animation,
                self.fourier_graph_update_animation,
                UpdateFromFunc(
                    brace, lambda b : b.move_to(
                        self.frequency_axes.coords_to_point(
                            self.k_tracker.get_value(),
                            f_max,
                        ),
                        DOWN
                    )
                ),
                run_time = 2
            )
        self.wait()
        self.play(*list(map(FadeOut, [brace, words, formula])))

    def show_tradeoff(self):
        for a in 5, 0.1, 0.01, 10, 0.5:
            self.play(
                ApplyMethod(
                    self.a_tracker.set_value, a,
                    run_time = 2
                ),
                self.wave_update_animation,
                self.fourier_graph_update_animation
            )
            self.wait()

    ##

    def get_wave_func(self):
        x0 = self.x0_tracker.get_value()
        k = self.k_tracker.get_value()
        a = self.a_tracker.get_value()
        A = a**(0.25)
        return lambda x : A*np.cos(TAU*k*x)*np.exp(-a*(x - x0)**2)

    def get_wave(self, axes):
        return axes.get_graph(
            self.get_wave_func(), 
            color = self.wave_color,
            stroke_width = self.wave_stroke_width
        )

class DopplerComparisonTodos(TODOStub):
    CONFIG = {
        "message" : """
            Insert some Doppler footage, 
            insert some hanging spring scene,
            insert position-momentum Fourier trade-off
        """
    }

class MusicalNote(AddingPureFrequencies):
    def construct(self):
        speaker = self.speaker = SVGMobject(file_name = "speaker")
        speaker.move_to(2*DOWN)
        randy = self.pi_creature

        axes = Axes(
            x_min = 0, x_max = 10,
            y_min = -1.5, y_max = 1.5
        )
        axes.center().to_edge(UP)
        time_label = TextMobject("Time")
        time_label.next_to(axes.x_axis.get_right(), UP)
        axes.add(time_label)

        graph = axes.get_graph(
            lambda x : op.mul(
                np.exp(-0.2*(x-4)**2),
                0.3*(np.cos(2*TAU*x) + np.cos(3*TAU*x) + np.cos(5*TAU*x)),
            ),
        )
        graph.set_color(BLUE)
        v_line = DashedLine(ORIGIN, 0.5*UP)
        v_line_update = UpdateFromFunc(
            v_line, lambda l : l.put_start_and_end_on_with_projection(
                graph.points[-1],
                axes.x_axis.number_to_point(
                    axes.x_axis.point_to_number(graph.points[-1])
                )
            )
        )

        self.add(speaker, axes)
        self.play(
            randy.change, "pondering",
            self.get_broadcast_animation(n_circles = 6, run_time  = 5),
            self.get_broadcast_animation(n_circles = 12, run_time = 5),
            ShowCreation(graph, run_time = 5, rate_func=linear),
            v_line_update
        )
        self.wait(2)

class AskAboutUncertainty(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "What does this have \\\\ to do with ``certainty''",
            bubble_kwargs = {"direction" : LEFT},
            student_index = 2
        )
        self.play(PiCreatureSays(
            self.students[0], 
            "What even are \\\\ these waves?",
            target_mode = "confused"
        ))
        self.wait(2)

class ProbabalisticDetection(FourierTransformOfWaveFunction):
    CONFIG = {
        "wave_stroke_width" : 2,
    }
    def construct(self):
        self.setup_wave()
        self.detect_only_single_points()
        self.show_probability_distribution()
        self.show_concentration_of_the_wave()

    def setup_wave(self):
        axes = Axes(
            x_min = 0, x_max = 10,
            y_min = -0.5, y_max = 1.5,
            y_axis_config = {
                "unit_size" : 1.5,
                "tick_frequency" : 0.25,
            }
        )
        axes.set_stroke(width = 2)
        axes.center()
        self.x0_tracker.set_value(5)
        self.k_tracker.set_value(1)
        self.a_tracker.set_value(0.2)
        wave = self.get_wave(axes)
        self.wave_update_animation = UpdateFromFunc(
            wave, lambda w : Transform(w, self.get_wave(axes)).update(1)
        )

        self.k_tracker.save_state()
        self.k_tracker.set_value(0)
        bell_curve = self.get_wave(axes)
        self.k_tracker.restore()
        bell_curve.set_stroke(width = 0)
        bell_curve.set_fill(BLUE, opacity = 0.5)
        squared_bell_curve = axes.get_graph(
            lambda x : bell_curve.underlying_function(x)**2
        ).match_style(bell_curve)

        self.set_variables_as_attrs(
            axes, wave, bell_curve, squared_bell_curve
        )

    def detect_only_single_points(self):
        particle = ProbabalisticDotCloud(
            n_copies = 100, 
            fill_opacity = 0.05, 
            time_per_change = 0.05,
        )
        particle.mobject[0].set_fill(BLUE, opacity = 1)
        gdw = particle.gaussian_distribution_wrapper

        rect = Rectangle(
            stroke_width = 0,
            height = 0.5,
            width = 2,
        )
        rect.set_fill(YELLOW, 0.3)
        rect.move_to(self.axes.coords_to_point(self.x0_tracker.get_value(), 0))
        brace = Brace(rect, UP, buff = 0)
        question = TextMobject("Do we detect the particle \\\\ in this region?")
        question.next_to(brace, UP)
        question.add_background_rectangle()
        rect.save_state()
        rect.stretch(0, 0)

        gdw_anim = Mobject.add_updater(
            gdw, lambda m : m.set_width(
                2.0/(self.a_tracker.get_value()**(0.5))
            ).move_to(rect)
        )

        self.add(rect, brace, question)

        yes = TextMobject("Yes").set_color(GREEN)
        no = TextMobject("No").set_color(RED)
        for word in yes, no:
            word.next_to(rect, DOWN)
            # word.add_background_rectangle()
        answer = VGroup()
        def update_answer(answer):
            px = particle.mobject[0].get_center()[0]
            lx = rect.get_left()[0]
            rx = rect.get_right()[0]
            if lx < px < rx:
                answer.submobjects = [yes]
            else:
                answer.submobjects = [no]
        answer_anim = Mobject.add_updater(answer, update_answer)

        self.add(gdw_anim, particle)
        self.play(
            GrowFromCenter(brace),
            rect.restore,
            Write(question)
        )
        self.wait()
        self.add(answer_anim)
        self.wait(4)
        self.add_foreground_mobjects(answer, particle.mobject)

        self.question_group = VGroup(question, brace)
        self.particle = particle
        self.rect = rect

    def show_probability_distribution(self):
        axes = self.axes
        wave = self.wave
        bell_curve = self.bell_curve
        question_group = self.question_group
        gdw = self.particle.gaussian_distribution_wrapper
        rect = self.rect

        v_lines = VGroup(*[
            DashedLine(ORIGIN, 3*UP).move_to(point, DOWN)
            for point in (rect.get_left(), rect.get_right())
        ])
        
        self.play(
            FadeIn(VGroup(axes, wave)),
            question_group.next_to, v_lines, UP, {"buff" : 0},
            *list(map(ShowCreation, v_lines))
        )
        self.wait(10)

    def show_concentration_of_the_wave(self):
        self.play(
            self.a_tracker.set_value, 5,
            self.wave_update_animation,
        )
        self.wait(10)

class HeisenbergCommentTodos(TODOStub):
    CONFIG = {
        "message" : "Insert position-momentum trade-off"
    }

class HeisenbergPetPeeve(PiCreatureScene):
    def construct(self):
        morty, other = self.pi_creatures
        particle = ProbabalisticDotCloud()
        gdw = particle.gaussian_distribution_wrapper
        gdw.to_edge(UP, buff = LARGE_BUFF)
        gdw.stretch_to_fit_width(3)
        gdw.rotate(3*DEGREES)

        self.add(particle)
        self.wait()
        self.play(PiCreatureSays(
            other, """
            According to the H.U.P., the \\\\
            universe is unknowable!
            """,
            target_mode = "speaking"
        ))
        self.play(morty.change, "angry")
        self.wait(3)
        self.play(
            PiCreatureSays(
                morty, "Well, yes and no",
                target_mode = "sassy",
            ),
            RemovePiCreatureBubble(
                other, target_mode = "erm"
            )
        )
        self.wait(4)

    ###
    def create_pi_creatures(self):
        morty = Mortimer()
        morty.to_corner(DOWN+RIGHT)
        other = PiCreature(color = MAROON_E)
        other.to_edge(DOWN).shift(3*LEFT)
        return VGroup(morty, other)

class OneLevelDeeper(Scene):
    def construct(self):
        heisenberg = ImageMobject("Heisenberg")
        heisenberg.to_corner(UP+LEFT)
        self.add(heisenberg)

        hup_words = TextMobject("Heisenberg's uncertainty principle")
        wave_words = TextMobject("Interpretation of the wave function")
        arrow = Vector(UP)
        group = VGroup(hup_words, arrow, wave_words)
        group.arrange(DOWN)

        randomness = ProbabalisticMobjectCloud(
            TextMobject("Randomness"),
            n_copies = 5,
            time_per_change = 0.05
        )
        gdw = randomness.gaussian_distribution_wrapper
        gdw.rotate(TAU/4)
        gdw.set_height(1)
        # gdw.set_width(4)
        gdw.next_to(hup_words, UP, MED_LARGE_BUFF)

        self.add(hup_words, randomness)
        self.wait(4)
        self.play(
            FadeIn(wave_words),
            GrowArrow(arrow),
            ApplyMethod(
                gdw.next_to, wave_words, DOWN, MED_LARGE_BUFF,
                path_arc = TAU/2,
            )
        )
        self.wait(6)

class BetterTranslation(TeacherStudentsScene):
    def construct(self):
        english_term = TextMobject("Uncertainty principle")
        german_word = TextMobject("Unschärferelation")
        translation = TextMobject("Unsharpness relation")

        to_german_words = TextMobject("In German")
        to_german_words.scale(0.5)
        to_german_arrow = Vector(DOWN, color = WHITE, buff = SMALL_BUFF)
        to_german_words.next_to(to_german_arrow, RIGHT, SMALL_BUFF)
        to_german_words.set_color(YELLOW)
        to_german_group = VGroup(to_german_arrow, to_german_words)

        translation_words = TextMobject("Literal translation")
        translation_words.scale(0.5)
        translation_arrow = Vector(DOWN, color = WHITE, buff = SMALL_BUFF)
        translation_words.next_to(translation_arrow, LEFT, SMALL_BUFF)
        translation_words.set_color(YELLOW)
        translation_group = VGroup(translation_arrow, translation_words)

        english_term.next_to(self.teacher, UP+LEFT)
        english_term.save_state()
        english_term.shift(DOWN)
        english_term.fade(1)
        self.play(
            english_term.restore,
            self.get_student_changes(*["pondering"]*3)
        )
        self.wait()

        german_word.move_to(english_term)
        to_german_group.next_to(
            german_word, UP,
            submobject_to_align = to_german_arrow
        )
        self.play(
            self.teacher.change, "raise_right_hand", 
            english_term.next_to, to_german_arrow, UP
        )
        self.play(
            GrowArrow(to_german_arrow),
            FadeIn(to_german_words),
            ReplacementTransform(
                english_term.copy().fade(1),
                german_word
            )
        )
        self.wait(2)

        group = VGroup(english_term, to_german_group, german_word)
        translation.move_to(german_word)
        translation_group.next_to(
            german_word, UP,
            submobject_to_align = translation_arrow
        )
        self.play(
            group.next_to, translation_arrow, UP,
        )
        self.play(
            GrowArrow(translation_arrow),
            FadeIn(translation_words),
            ReplacementTransform(
                german_word.copy().fade(1),
                translation
            )
        )
        self.change_student_modes(*["happy"]*3)
        self.wait(2)

class ThinkOfHeisenbergUncertainty(PiCreatureScene):
    def construct(self):
        morty = self.pi_creature
        morty.center().to_edge(DOWN).shift(LEFT)

        dot_cloud = ProbabalisticDotCloud()
        dot_gdw = dot_cloud.gaussian_distribution_wrapper
        dot_gdw.set_width(1)
        dot_gdw.rotate(TAU/8)
        dot_gdw.move_to(FRAME_X_RADIUS*RIGHT/2),

        vector_cloud = ProbabalisticVectorCloud(
            center_func = dot_gdw.get_center
        )
        vector_gdw = vector_cloud.gaussian_distribution_wrapper
        vector_gdw.set_width(0.1)
        vector_gdw.rotate(TAU/8)
        vector_gdw.next_to(dot_gdw, UP+LEFT, LARGE_BUFF)

        time_tracker = ValueTracker(0)
        self.add()
        freq = 1
        continual_anims = [
            always_shift(time_tracker, direction = RIGHT, rate = 1),
            Mobject.add_updater(
                dot_gdw,
                lambda d : d.set_width(
                    (np.cos(freq*time_tracker.get_value()) + 1.1)/2
                )
            ),
            Mobject.add_updater(
                vector_gdw,
                lambda d : d.set_width(
                    (-np.cos(freq*time_tracker.get_value()) + 1.1)/2
                )
            ),
            dot_cloud, vector_cloud
        ]
        self.add(*continual_anims)

        position, momentum, time, frequency = list(map(TextMobject, [
            "Position", "Momentum", "Time", "Frequency"
        ]))
        VGroup(position, time).set_color(BLUE)
        VGroup(momentum, frequency).set_color(YELLOW)
        groups = VGroup()
        for m1, m2 in (position, momentum), (time, frequency):
            arrow = TexMobject("\\updownarrow").scale(1.5)
            group = VGroup(m1, arrow, m2)
            group.arrange(DOWN)
            lp, rp = parens = TexMobject("\\big(\\big)")
            parens.stretch(1.5, 1)
            parens.match_height(group)
            lp.next_to(group, LEFT, buff = SMALL_BUFF)
            rp.next_to(group, RIGHT, buff = SMALL_BUFF)
            group.add(parens)
            groups.add(group)
        arrow = TexMobject("\\Leftrightarrow").scale(2)
        groups.submobjects.insert(1, arrow)
        groups.arrange(RIGHT)
        groups.next_to(morty, UP+RIGHT, LARGE_BUFF)
        groups.shift_onto_screen()


        self.play(PiCreatureBubbleIntroduction(
            morty, "Heisenberg \\\\ uncertainty \\\\ principle",
            bubble_class = ThoughtBubble,
            bubble_kwargs = {"height" : 4, "width" : 4, "direction" : RIGHT},
            target_mode = "pondering"
        ))
        self.wait()
        self.play(morty.change, "confused", dot_gdw)
        self.wait(10)
        self.play(
            ApplyMethod(
                VGroup(dot_gdw, vector_gdw ).shift, 
                FRAME_X_RADIUS*RIGHT,
                rate_func = running_start
            )
        )
        self.remove(*continual_anims)
        self.play(
            morty.change, "raise_left_hand", groups,
            FadeIn(
                groups, 
                lag_ratio = 0.5,
                run_time = 3,
            )
        )
        self.wait(2)

# End things

class PatreonMention(PatreonThanks):
    def construct(self):
        morty = Mortimer()
        morty.next_to(ORIGIN, DOWN)

        patreon_logo = PatreonLogo()
        patreon_logo.to_edge(UP)

        thank_you = TextMobject("Thank you.")
        thank_you.next_to(patreon_logo, DOWN)

        self.play(
            DrawBorderThenFill(patreon_logo),
            morty.change, "gracious"
        )
        self.play(Write(thank_you))
        self.wait(3)

class Promotion(PiCreatureScene):
    CONFIG = {
        "camera_class" : ThreeDCamera,
        "seconds_to_blink" : 5,
    }
    def construct(self):
        aops_logo = AoPSLogo()
        aops_logo.next_to(self.pi_creature, UP+LEFT)
        url = TextMobject(
            "AoPS.com/", "3b1b",
            arg_separator = ""
        )
        url.to_corner(UP+LEFT)
        url_rect = Rectangle(color = BLUE)
        url_rect.replace(
            url.get_part_by_tex("3b1b"),
            stretch = True
        )

        url_rect.stretch_in_place(1.1, dim = 1)

        rect = Rectangle(height = 9, width = 16)
        rect.set_height(4.5)
        rect.next_to(url, DOWN)
        rect.to_edge(LEFT)
        rect.set_stroke(width = 0)
        mathy = Mathematician()
        mathy.flip()
        mathy.to_corner(DOWN+RIGHT)
        morty = self.pi_creature
        morty.save_state()
        book = ImageMobject("AoPS_volume_2")
        book.set_height(2)
        book.next_to(mathy, UP+LEFT).shift(MED_LARGE_BUFF*LEFT)
        mathy.get_center = mathy.get_top

        words = TextMobject("""
            Interested in working for \\\\ 
            one of my favorite math\\\\ 
            education companies?
        """, alignment = "")
        words.to_edge(UP)

        arrow = Arrow(
            aops_logo.get_top(),
            morty.get_top(),
            path_arc = -0.4*TAU,
            stroke_width = 5,
            tip_length = 0.5,
        )
        arrow.tip.shift(SMALL_BUFF*DOWN)

        self.add(words)
        self.play(
            self.pi_creature.change_mode, "raise_right_hand",
            *[
                DrawBorderThenFill(
                    submob,
                    run_time = 2,
                    rate_func = squish_rate_func(double_smooth, a, a+0.5)
                )
                for submob, a in zip(aops_logo, np.linspace(0, 0.5, len(aops_logo)))
            ]
        )
        self.play(
            words.scale, 0.75,
            words.next_to, url, DOWN, LARGE_BUFF,
            words.shift_onto_screen,
            Write(url),
        )
        self.wait(2)
        self.play(
            LaggedStartMap(
                ApplyFunction, aops_logo,
                lambda mob : (lambda m : m.shift(0.2*UP).set_color(YELLOW), mob),
                rate_func = there_and_back, 
                run_time = 1,
            ),
            morty.change, "thinking"
        )
        self.wait()
        self.play(ShowCreation(arrow))
        self.play(FadeOut(arrow))
        self.wait()

        # To teacher
        self.play(
            morty.change_mode, "plain",
            morty.flip,
            morty.scale, 0.7,
            morty.next_to, mathy, LEFT, LARGE_BUFF,
            morty.to_edge, DOWN,
            FadeIn(mathy),
        )
        self.play(
            PiCreatureSays(
                mathy, "",
                bubble_kwargs = {"width" : 5},
                look_at_arg = morty.eyes,
            ),
            morty.change, "happy",
            aops_logo.shift, 1.5*UP + 0.5*RIGHT
        )
        self.play(Blink(mathy))
        self.wait()
        self.play(
            RemovePiCreatureBubble(
                mathy, target_mode = "raise_right_hand"
            ),
            aops_logo.to_corner, UP+RIGHT,
            aops_logo.shift, MED_SMALL_BUFF*DOWN,
            GrowFromPoint(book, mathy.get_corner(UP+LEFT)),
        )
        self.play(morty.change, "pondering", book)
        self.wait(3)
        self.play(Blink(mathy))
        self.wait()
        self.play(
            Animation(
                BackgroundRectangle(book, fill_opacity = 1),
                remover = True
            ),
            FadeOut(book),
        )
        print(self.num_plays)
        self.play(
            FadeOut(words),
            ShowCreation(rect),
            morty.restore,
            morty.change, "happy", rect,
            FadeOut(mathy),
        )
        self.wait(10)
        self.play(ShowCreation(url_rect))
        self.play(
            FadeOut(url_rect),
            url.get_part_by_tex("3b1b").set_color, BLUE,
        )
        self.wait(15)

class PuzzleStatement(Scene):
    def construct(self):
        aops_logo = AoPSLogo()
        url = TextMobject("AoPS.com/3b1b")
        url.next_to(aops_logo, UP)
        group = VGroup(aops_logo, url)
        group.to_edge(UP)
        self.add(group)

        words = TextMobject("""
            AoPS must choose one of 20 people to send to a 
            tug-of-war tournament.  We don't care who we send, 
            as long as we don't send our weakest person. \\\\ \\\\

            Each person has a different strength, but we don't know 
            those strengths.  We get 10 intramural 10-on-10 matches 
            to determine who we send.  Can we make sure we don't send
             the weakest person?
        """, alignment = "")
        words.set_width(FRAME_WIDTH - 2)
        words.next_to(group, DOWN, LARGE_BUFF)
        self.play(LaggedStartMap(FadeIn, words, run_time = 5, lag_ratio = 0.2))
        self.wait(2)

class UncertaintyEndScreen(PatreonEndScreen):
    CONFIG = {
        "specific_patrons" : [
            "CrypticSwarm",
            "Ali Yahya",
            "Juan Benet",
            "Markus Persson",
            "Damion Kistler",
            "Burt Humburg",
            "Yu Jun",
            "Dave Nicponski",
            "Kaustuv DeBiswas",
            "Joseph John Cox",
            "Luc Ritchie",
            "Achille Brighton",
            "Rish Kundalia",
            "Yana Chernobilsky",
            "Shìmín Kuang",
            "Mathew Bramson",
            "Jerry Ling",
            "Mustafa Mahdi",
            "Meshal Alshammari",
            "Mayank M. Mehrotra",
            "Lukas Biewald",
            "Robert Teed",
            "Samantha D. Suplee",
            "Mark Govea",
            "John Haley",
            "Julian Pulgarin",
            "Jeff Linse",
            "Cooper Jones",
            "Desmos  ",
            "Boris Veselinovich",
            "Ryan Dahl",
            "Ripta Pasay",
            "Eric Lavault",
            "Randall Hunt",
            "Andrew Busey",
            "Mads Elvheim",
            "Tianyu Ge",
            "Awoo",
            "Dr. David G. Stork",
            "Linh Tran",
            "Jason Hise",
            "Bernd Sing",
            "James   H. Park",
            "Ankalagon   ",
            "Mathias Jansson",
            "David Clark",
            "Ted Suzman",
            "Eric Chow",
            "Michael Gardner",
            "David Kedmey",
            "Jonathan Eppele",
            "Clark Gaebel",
            "Jordan Scales",
            "Ryan Atallah",
            "supershabam ",
            "1stViewMaths",
            "Jacob Magnuson",
            "Chloe Zhou",
            "Ross Garber",
            "Thomas Tarler",
            "Isak Hietala",
            "Egor Gumenuk",
            "Waleed Hamied",
            "Oliver Steele",
            "Yaw Etse",
            "David B",
            "Delton Ding",
            "James Thornton",
            "Felix Tripier",
            "Arthur Zey",
            "George Chiesa",
            "Norton Wang",
            "Kevin Le",
            "Alexander Feldman",
            "David MacCumber",
            "Jacob Kohl",
            "Frank Secilia",
            "George John",
            "Akash Kumar",
            "Britt Selvitelle",
            "Jonathan Wilson",
            "Michael Kunze",
            "Giovanni Filippi",
            "Eric Younge",
            "Prasant Jagannath",
            "Andrejs olins",
            "Cody Brocious",
        ],
    }

class Thumbnail(Scene):
    def construct(self):
        uncertainty_principle = TextMobject("Uncertainty \\\\", "principle")
        uncertainty_principle[1].shift(SMALL_BUFF*UP)
        quantum = TextMobject("Quantum")
        VGroup(uncertainty_principle, quantum).scale(2.5)
        uncertainty_principle.to_edge(UP, MED_LARGE_BUFF)
        quantum.to_edge(DOWN, MED_LARGE_BUFF)

        arrow = TexMobject("\\Downarrow")
        arrow.scale(4)
        arrow.move_to(Line(
            uncertainty_principle.get_bottom(),
            quantum.get_top(),
        ))

        cross = Cross(arrow)
        cross.set_stroke(RED, 20)

        is_word, not_word = is_not = TextMobject("is", "\\emph{NOT}")
        is_not.scale(3)
        is_word.move_to(arrow)
        # is_word.shift(0.6*UP)
        not_word.set_color(RED)
        not_word.set_stroke(RED, 3)
        not_word.rotate(10*DEGREES, about_edge = DOWN+LEFT)
        not_word.next_to(is_word, DOWN, 0.1*SMALL_BUFF)

        dot_cloud = ProbabalisticDotCloud(
            n_copies = 1000,
        )
        dot_gdw = dot_cloud.gaussian_distribution_wrapper
        # dot_gdw.rotate(3*DEGREES)
        dot_gdw.rotate(25*DEGREES)
        # dot_gdw.scale(2)
        dot_gdw.scale(2)
        # dot_gdw.move_to(quantum.get_bottom()+SMALL_BUFF*DOWN)
        dot_gdw.move_to(quantum)



        def get_func(a):
            return lambda t : 0.5*np.exp(-a*t**2)*np.cos(TAU*t)
        axes = Axes(
            x_min = -6, x_max = 6,
            x_axis_config = {"unit_size" : 0.25}
        )
        graphs = VGroup(*[
            axes.get_graph(get_func(a))
            for a in (10, 3, 1, 0.3, 0.1,)
        ])
        graphs.arrange(DOWN, buff = 0.6)
        graphs.to_corner(UP+LEFT)
        graphs.set_color_by_gradient(BLUE_B, BLUE_D)

        frequency_axes = Axes(
            x_min = 0, x_max = 2,
            x_axis_config = {"unit_size" : 1}
        )
        fourier_graphs = VGroup(*[
            get_fourier_graph(
                frequency_axes, graph.underlying_function,
                t_min = -10, t_max = 10,
            )
            for graph in graphs
        ])
        for graph, fourier_graph in zip(graphs, fourier_graphs):
            fourier_graph.pointwise_become_partial(fourier_graph, 0.02, 0.06)
            fourier_graph.scale(3)
            fourier_graph.stretch(3, 1)
            fourier_graph.move_to(graph)
            fourier_graph.to_edge(RIGHT)

        self.add(graphs, fourier_graphs)


        self.add(dot_cloud)
        self.add(
            uncertainty_principle, quantum,
        )
        self.add(arrow, cross)
        # self.add(is_word)
        # self.add(is_not)















