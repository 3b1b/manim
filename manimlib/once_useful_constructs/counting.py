from manimlib.animation.creation import ShowCreation
from manimlib.animation.fading import FadeIn
from manimlib.animation.transform import MoveToTarget
from manimlib.animation.transform import Transform
from manimlib.constants import *
from manimlib.mobject.geometry import Arrow
from manimlib.mobject.geometry import Circle
from manimlib.mobject.geometry import Dot
from manimlib.mobject.svg.tex_mobject import TexMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.scene.scene import Scene


class CountingScene(Scene):
    CONFIG = {
        "digit_place_colors": [YELLOW, MAROON_B, RED, GREEN, BLUE, PURPLE_D],
        "counting_dot_starting_position": (FRAME_X_RADIUS - 1) * RIGHT + (FRAME_Y_RADIUS - 1) * UP,
        "count_dot_starting_radius": 0.5,
        "dot_configuration_height": 2,
        "ones_configuration_location": UP + 2 * RIGHT,
        "num_scale_factor": 2,
        "num_start_location": 2 * DOWN,
    }

    def setup(self):
        self.dots = VGroup()
        self.number = 0
        self.max_place = 0
        self.number_mob = VGroup(TexMobject(str(self.number)))
        self.number_mob.scale(self.num_scale_factor)
        self.number_mob.shift(self.num_start_location)

        self.dot_templates = []
        self.dot_template_iterators = []
        self.curr_configurations = []

        self.arrows = VGroup()

        self.add(self.number_mob)

    def get_template_configuration(self, place):
        # This should probably be replaced for non-base-10 counting scenes
        down_right = (0.5) * RIGHT + (np.sqrt(3) / 2) * DOWN
        result = []
        for down_right_steps in range(5):
            for left_steps in range(down_right_steps):
                result.append(
                    down_right_steps * down_right + left_steps * LEFT
                )
        return reversed(result[:self.get_place_max(place)])

    def get_dot_template(self, place):
        # This should be replaced for non-base-10 counting scenes
        dots = VGroup(*[
            Dot(
                point,
                radius=0.25,
                fill_opacity=0,
                stroke_width=2,
                stroke_color=WHITE,
            )
            for point in self.get_template_configuration(place)
        ])
        dots.set_height(self.dot_configuration_height)
        return dots

    def add_configuration(self):
        new_template = self.get_dot_template(len(self.dot_templates))
        new_template.move_to(self.ones_configuration_location)
        left_vect = (new_template.get_width() + LARGE_BUFF) * LEFT
        new_template.shift(
            left_vect * len(self.dot_templates)
        )
        self.dot_templates.append(new_template)
        self.dot_template_iterators.append(
            it.cycle(new_template)
        )
        self.curr_configurations.append(VGroup())

    def count(self, max_val, run_time_per_anim=1):
        for x in range(max_val):
            self.increment(run_time_per_anim)

    def increment(self, run_time_per_anim=1):
        moving_dot = Dot(
            self.counting_dot_starting_position,
            radius=self.count_dot_starting_radius,
            color=self.digit_place_colors[0],
        )
        moving_dot.generate_target()
        moving_dot.set_fill(opacity=0)
        kwargs = {
            "run_time": run_time_per_anim
        }

        continue_rolling_over = True
        first_move = True
        place = 0
        while continue_rolling_over:
            added_anims = []
            if first_move:
                added_anims += self.get_digit_increment_animations()
                first_move = False
            moving_dot.target.replace(
                next(self.dot_template_iterators[place])
            )
            self.play(MoveToTarget(moving_dot), *added_anims, **kwargs)
            self.curr_configurations[place].add(moving_dot)

            if len(self.curr_configurations[place].split()) == self.get_place_max(place):
                full_configuration = self.curr_configurations[place]
                self.curr_configurations[place] = VGroup()
                place += 1
                center = full_configuration.get_center_of_mass()
                radius = 0.6 * max(
                    full_configuration.get_width(),
                    full_configuration.get_height(),
                )
                circle = Circle(
                    radius=radius,
                    stroke_width=0,
                    fill_color=self.digit_place_colors[place],
                    fill_opacity=0.5,
                )
                circle.move_to(center)
                moving_dot = VGroup(circle, full_configuration)
                moving_dot.generate_target()
                moving_dot[0].set_fill(opacity=0)
            else:
                continue_rolling_over = False

    def get_digit_increment_animations(self):
        result = []
        self.number += 1
        is_next_digit = self.is_next_digit()
        if is_next_digit:
            self.max_place += 1
        new_number_mob = self.get_number_mob(self.number)
        new_number_mob.move_to(self.number_mob, RIGHT)
        if is_next_digit:
            self.add_configuration()
            place = len(new_number_mob.split()) - 1
            result.append(FadeIn(self.dot_templates[place]))
            arrow = Arrow(
                new_number_mob[place].get_top(),
                self.dot_templates[place].get_bottom(),
                color=self.digit_place_colors[place]
            )
            self.arrows.add(arrow)
            result.append(ShowCreation(arrow))
        result.append(Transform(
            self.number_mob, new_number_mob,
            lag_ratio=0.5
        ))
        return result

    def get_number_mob(self, num):
        result = VGroup()
        place = 0
        max_place = self.max_place
        while place < max_place:
            digit = TexMobject(str(self.get_place_num(num, place)))
            if place >= len(self.digit_place_colors):
                self.digit_place_colors += self.digit_place_colors
            digit.set_color(self.digit_place_colors[place])
            digit.scale(self.num_scale_factor)
            digit.next_to(result, LEFT, buff=SMALL_BUFF, aligned_edge=DOWN)
            result.add(digit)
            place += 1
        return result

    def is_next_digit(self):
        return False

    def get_place_num(self, num, place):
        return 0

    def get_place_max(self, place):
        return 0


class PowerCounter(CountingScene):
    def is_next_digit(self):
        number = self.number
        while number > 1:
            if number % self.base != 0:
                return False
            number /= self.base
        return True

    def get_place_max(self, place):
        return self.base

    def get_place_num(self, num, place):
        return (num / (self.base ** place)) % self.base


class CountInDecimal(PowerCounter):
    CONFIG = {
        "base": 10,
    }

    def construct(self):
        for x in range(11):
            self.increment()
        for x in range(85):
            self.increment(0.25)
        for x in range(20):
            self.increment()


class CountInTernary(PowerCounter):
    CONFIG = {
        "base": 3,
        "dot_configuration_height": 1,
        "ones_configuration_location": UP + 4 * RIGHT
    }

    def construct(self):
        self.count(27)

    # def get_template_configuration(self):
    #     return [ORIGIN, UP]


class CountInBinaryTo256(PowerCounter):
    CONFIG = {
        "base": 2,
        "dot_configuration_height": 1,
        "ones_configuration_location": UP + 5 * RIGHT
    }

    def construct(self):
        self.count(128, 0.3)

    def get_template_configuration(self):
        return [ORIGIN, UP]


class FactorialBase(CountingScene):
    CONFIG = {
        "dot_configuration_height": 1,
        "ones_configuration_location": UP + 4 * RIGHT
    }

    def construct(self):
        self.count(30, 0.4)

    def is_next_digit(self):
        return self.number == self.factorial(self.max_place + 1)

    def get_place_max(self, place):
        return place + 2

    def get_place_num(self, num, place):
        return (num / self.factorial(place + 1)) % self.get_place_max(place)

    def factorial(self, n):
        if (n == 1):
            return 1
        else:
            return n * self.factorial(n - 1)
