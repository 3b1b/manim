"""Mobjects representing predefined SVG drawings."""

__all__ = [
    "Lightbulb",
    "BitcoinLogo",
    "Guitar",
    "Speedometer",
    "AoPSLogo",
    "PartyHat",
    "Laptop",
    "PatreonLogo",
    "VideoIcon",
    "VideoSeries",
    "Headphones",
    "Clock",
    "ClockPassesTime",
    "Bubble",
    "SpeechBubble",
    "DoubleSpeechBubble",
    "ThoughtBubble",
    "Car",
    "VectorizedEarth",
    "Logo",
    "DeckOfCards",
    "PlayingCard",
    "SuitSymbol",
]


import itertools as it
import string

from ... import config
from ...animation.animation import Animation
from ...animation.rotation import Rotating
from ...constants import *
from ...mobject.geometry import AnnularSector
from ...mobject.geometry import Arc
from ...mobject.geometry import Circle
from ...mobject.geometry import Line
from ...mobject.geometry import Polygon
from ...mobject.geometry import Rectangle
from ...mobject.geometry import Square
from ...mobject.mobject import Mobject
from ...mobject.svg.svg_mobject import SVGMobject
from ...mobject.svg.tex_mobject import MathTex
from ...mobject.svg.tex_mobject import Tex
from ...mobject.three_dimensions import Cube
from ...mobject.types.vectorized_mobject import VGroup
from ...mobject.types.vectorized_mobject import VMobject
from ...mobject.types.vectorized_mobject import VectorizedPoint
from ...utils.bezier import interpolate
from ...utils.config_ops import digest_config
from ...utils.rate_functions import linear
from ...utils.space_ops import angle_of_vector
from ...utils.space_ops import complex_to_R3
from ...utils.space_ops import rotate_vector
from ...utils.color import (
    YELLOW,
    WHITE,
    DARK_GREY,
    MAROON_B,
    PURPLE,
    GREEN,
    BLACK,
    LIGHT_GREY,
    GREY,
    BLUE_B,
    BLUE_D,
)


class Lightbulb(SVGMobject):
    CONFIG = {
        "file_name": "lightbulb",
        "height": 1,
        "stroke_color": YELLOW,
        "stroke_width": 3,
        "fill_color": YELLOW,
        "fill_opacity": 0,
    }


class BitcoinLogo(SVGMobject):
    CONFIG = {
        "file_name": "Bitcoin_logo",
        "height": 1,
        "fill_color": "#f7931a",
        "inner_color": WHITE,
        "fill_opacity": 1,
        "stroke_width": 0,
    }

    def __init__(self, **kwargs):
        SVGMobject.__init__(self, **kwargs)
        self[0].set_fill(self.fill_color, self.fill_opacity)
        self[1].set_fill(self.inner_color, 1)


class Guitar(SVGMobject):
    CONFIG = {
        "file_name": "guitar",
        "height": 2.5,
        "fill_color": DARK_GREY,
        "fill_opacity": 1,
        "stroke_color": WHITE,
        "stroke_width": 0.5,
    }


class Speedometer(VMobject):
    CONFIG = {
        "arc_angle": 4 * np.pi / 3,
        "num_ticks": 8,
        "tick_length": 0.2,
        "needle_width": 0.1,
        "needle_height": 0.8,
        "needle_color": YELLOW,
    }

    def generate_points(self):
        start_angle = np.pi / 2 + self.arc_angle / 2
        end_angle = np.pi / 2 - self.arc_angle / 2
        self.add(Arc(start_angle=start_angle, angle=-self.arc_angle))
        tick_angle_range = np.linspace(start_angle, end_angle, self.num_ticks)
        for index, angle in enumerate(tick_angle_range):
            vect = rotate_vector(RIGHT, angle)
            tick = Line((1 - self.tick_length) * vect, vect)
            label = MathTex(str(10 * index))
            label.set_height(self.tick_length)
            label.shift((1 + self.tick_length) * vect)
            self.add(tick, label)

        needle = Polygon(
            LEFT,
            UP,
            RIGHT,
            stroke_width=0,
            fill_opacity=1,
            fill_color=self.needle_color,
        )
        needle.stretch_to_fit_width(self.needle_width)
        needle.stretch_to_fit_height(self.needle_height)
        needle.rotate(start_angle - np.pi / 2, about_point=ORIGIN)
        self.add(needle)
        self.needle = needle

        self.center_offset = self.get_center()

    def get_center(self):
        result = VMobject.get_center(self)
        if hasattr(self, "center_offset"):
            result -= self.center_offset
        return result

    def get_needle_tip(self):
        return self.needle.get_anchors()[1]

    def get_needle_angle(self):
        return angle_of_vector(self.get_needle_tip() - self.get_center())

    def rotate_needle(self, angle):
        self.needle.rotate(angle, about_point=self.get_center())
        return self

    def move_needle_to_velocity(self, velocity):
        max_velocity = 10 * (self.num_ticks - 1)
        proportion = float(velocity) / max_velocity
        start_angle = np.pi / 2 + self.arc_angle / 2
        target_angle = start_angle - self.arc_angle * proportion
        self.rotate_needle(target_angle - self.get_needle_angle())
        return self


class AoPSLogo(SVGMobject):
    CONFIG = {
        "file_name": "aops_logo",
        "height": 1.5,
    }

    def __init__(self, **kwargs):
        SVGMobject.__init__(self, **kwargs)
        self.set_stroke(WHITE, width=0)
        colors = [BLUE_E, "#008445", GREEN_B]
        index_lists = [
            (10, 11, 12, 13, 14, 21, 22, 23, 24, 27, 28, 29, 30),
            (0, 1, 2, 3, 4, 15, 16, 17, 26),
            (5, 6, 7, 8, 9, 18, 19, 20, 25),
        ]
        for color, index_list in zip(colors, index_lists):
            for i in index_list:
                self.submobjects[i].set_fill(color, opacity=1)

        self.set_height(self.height)
        self.center()


class PartyHat(SVGMobject):
    CONFIG = {
        "file_name": "party_hat",
        "height": 1.5,
        "stroke_width": 0,
        "fill_opacity": 1,
        "frills_colors": [MAROON_B, PURPLE],
        "cone_color": GREEN,
        "dots_colors": [YELLOW],
    }
    NUM_FRILLS = 7
    NUM_DOTS = 6

    def __init__(self, **kwargs):
        SVGMobject.__init__(self, **kwargs)
        self.set_height(self.height)

        self.frills = VGroup(*self[: self.NUM_FRILLS])
        self.cone = self[self.NUM_FRILLS]
        self.dots = VGroup(*self[self.NUM_FRILLS + 1 :])

        self.frills.set_color_by_gradient(*self.frills_colors)
        self.cone.set_color(self.cone_color)
        self.dots.set_color_by_gradient(*self.dots_colors)


class Laptop(VGroup):
    CONFIG = {
        "width": 3,
        "body_dimensions": [4, 3, 0.05],
        "screen_thickness": 0.01,
        "keyboard_width_to_body_width": 0.9,
        "keyboard_height_to_body_height": 0.5,
        "screen_width_to_screen_plate_width": 0.9,
        "key_color_kwargs": {
            "stroke_width": 0,
            "fill_color": BLACK,
            "fill_opacity": 1,
        },
        "fill_opacity": 1,
        "stroke_width": 0,
        "body_color": LIGHT_GREY,
        "shaded_body_color": GREY,
        "open_angle": np.pi / 4,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        body = Cube(side_length=1)
        for dim, scale_factor in enumerate(self.body_dimensions):
            body.stretch(scale_factor, dim=dim)
        body.set_width(self.width)
        body.set_fill(self.shaded_body_color, opacity=1)
        body.sort(lambda p: p[2])
        body[-1].set_fill(self.body_color)
        screen_plate = body.copy()
        keyboard = VGroup(
            *[
                VGroup(
                    *[Square(**self.key_color_kwargs) for x in range(12 - y % 2)]
                ).arrange(RIGHT, buff=SMALL_BUFF)
                for y in range(4)
            ]
        ).arrange(DOWN, buff=MED_SMALL_BUFF)
        keyboard.stretch_to_fit_width(
            self.keyboard_width_to_body_width * body.get_width(),
        )
        keyboard.stretch_to_fit_height(
            self.keyboard_height_to_body_height * body.get_height(),
        )
        keyboard.next_to(body, OUT, buff=0.1 * SMALL_BUFF)
        keyboard.shift(MED_SMALL_BUFF * UP)
        body.add(keyboard)

        screen_plate.stretch(self.screen_thickness / self.body_dimensions[2], dim=2)
        screen = Rectangle(
            stroke_width=0,
            fill_color=BLACK,
            fill_opacity=1,
        )
        screen.replace(screen_plate, stretch=True)
        screen.scale_in_place(self.screen_width_to_screen_plate_width)
        screen.next_to(screen_plate, OUT, buff=0.1 * SMALL_BUFF)
        screen_plate.add(screen)
        screen_plate.next_to(body, UP, buff=0)
        screen_plate.rotate(
            self.open_angle, RIGHT, about_point=screen_plate.get_bottom()
        )
        self.screen_plate = screen_plate
        self.screen = screen

        axis = Line(
            body.get_corner(UP + LEFT + OUT),
            body.get_corner(UP + RIGHT + OUT),
            color=BLACK,
            stroke_width=2,
        )
        self.axis = axis

        self.add(body, screen_plate, axis)
        self.rotate(5 * np.pi / 12, LEFT, about_point=ORIGIN)
        self.rotate(np.pi / 6, DOWN, about_point=ORIGIN)


class PatreonLogo(SVGMobject):
    CONFIG = {
        "file_name": "patreon_logo",
        "fill_color": "#F96854",
        # "fill_color" : WHITE,
        "fill_opacity": 1,
        "stroke_width": 0,
        "width": 4,
    }

    def __init__(self, **kwargs):
        SVGMobject.__init__(self, **kwargs)
        self.set_width(self.width)
        self.center()


class VideoIcon(SVGMobject):
    CONFIG = {
        "file_name": "video_icon",
    }

    def __init__(self, **kwargs):
        SVGMobject.__init__(self, **kwargs)
        self.width = config["frame_width"] / 12.0
        self.center()
        self.set_width(self.width)
        self.set_stroke(color=WHITE, width=0)
        self.set_fill(color=WHITE, opacity=1)


class VideoSeries(VGroup):
    CONFIG = {
        "num_videos": 11,
        "gradient_colors": [BLUE_B, BLUE_D],
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        videos = [VideoIcon() for x in range(self.num_videos)]
        VGroup.__init__(self, *videos, **kwargs)
        self.arrange()
        self.set_width(config["frame_width"] - config["med_large_buff"])
        self.set_color_by_gradient(*self.gradient_colors)


class Headphones(SVGMobject):
    CONFIG = {
        "file_name": "headphones",
        "height": 2,
        "y_stretch_factor": 0.5,
        "color": GREY,
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self, file_name=self.file_name, **kwargs)
        self.stretch(self.y_stretch_factor, 1)
        self.set_height(self.height)
        self.set_stroke(width=0)
        self.set_fill(color=self.color)


class Clock(VGroup):
    CONFIG = {}

    def __init__(self, **kwargs):
        circle = Circle(color=WHITE)
        ticks = []
        for x in range(12):
            alpha = x / 12.0
            point = complex_to_R3(np.exp(2 * np.pi * alpha * complex(0, 1)))
            length = 0.2 if x % 3 == 0 else 0.1
            ticks.append(Line(point, (1 - length) * point))
        self.hour_hand = Line(ORIGIN, 0.3 * UP)
        self.minute_hand = Line(ORIGIN, 0.6 * UP)
        # for hand in self.hour_hand, self.minute_hand:
        #     #Balance out where the center is
        #     hand.add(VectorizedPoint(-hand.get_end()))

        VGroup.__init__(self, circle, self.hour_hand, self.minute_hand, *ticks)


class ClockPassesTime(Animation):
    CONFIG = {
        "run_time": 5,
        "hours_passed": 12,
        "rate_func": linear,
    }

    def __init__(self, clock, **kwargs):
        digest_config(self, kwargs)
        assert isinstance(clock, Clock)
        rot_kwargs = {"axis": OUT, "about_point": clock.get_center()}
        hour_radians = -self.hours_passed * 2 * np.pi / 12
        self.hour_rotation = Rotating(
            clock.hour_hand, radians=hour_radians, **rot_kwargs
        )
        self.hour_rotation.begin()
        self.minute_rotation = Rotating(
            clock.minute_hand, radians=12 * hour_radians, **rot_kwargs
        )
        self.minute_rotation.begin()
        Animation.__init__(self, clock, **kwargs)

    def interpolate_mobject(self, alpha):
        for rotation in self.hour_rotation, self.minute_rotation:
            rotation.interpolate_mobject(alpha)


class Bubble(SVGMobject):
    CONFIG = {
        "direction": LEFT,
        "center_point": ORIGIN,
        "content_scale_factor": 0.75,
        "height": 5,
        "width": 8,
        "bubble_center_adjustment_factor": 1.0 / 8,
        "file_name": None,
        "fill_color": BLACK,
        "fill_opacity": 0.8,
        "stroke_color": WHITE,
        "stroke_width": 3,
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs, locals())
        if self.file_name is None:
            raise Exception("Must invoke Bubble subclass")
        try:
            SVGMobject.__init__(self, **kwargs)
        except IOError as err:
            self.file_name = os.path.join(FILE_DIR, self.file_name)
            SVGMobject.__init__(self, **kwargs)
        self.center()
        self.stretch_to_fit_height(self.height)
        self.stretch_to_fit_width(self.width)
        if self.direction[0] > 0:
            self.flip()
        self.direction_was_specified = "direction" in kwargs
        self.content = Mobject()

    def get_tip(self):
        # TODO, find a better way
        return self.get_corner(DOWN + self.direction) - 0.6 * self.direction

    def get_bubble_center(self):
        factor = self.bubble_center_adjustment_factor
        return self.get_center() + factor * self.get_height() * UP

    def move_tip_to(self, point):
        mover = VGroup(self)
        if self.content is not None:
            mover.add(self.content)
        mover.shift(point - self.get_tip())
        return self

    def flip(self, axis=UP):
        Mobject.flip(self, axis=axis)
        if abs(axis[1]) > 0:
            self.direction = -np.array(self.direction)
        return self

    def pin_to(self, mobject):
        mob_center = mobject.get_center()
        want_to_flip = np.sign(mob_center[0]) != np.sign(self.direction[0])
        can_flip = not self.direction_was_specified
        if want_to_flip and can_flip:
            self.flip()
        boundary_point = mobject.get_critical_point(UP - self.direction)
        vector_from_center = 1.0 * (boundary_point - mob_center)
        self.move_tip_to(mob_center + vector_from_center)
        return self

    def position_mobject_inside(self, mobject):
        scaled_width = self.content_scale_factor * self.get_width()
        if mobject.get_width() > scaled_width:
            mobject.set_width(scaled_width)
        mobject.shift(self.get_bubble_center() - mobject.get_center())
        return mobject

    def add_content(self, mobject):
        self.position_mobject_inside(mobject)
        self.content = mobject
        return self.content

    def write(self, *text):
        self.add_content(Tex(*text))
        return self

    def resize_to_content(self):
        target_width = self.content.get_width()
        target_width += max(MED_LARGE_BUFF, 2)
        target_height = self.content.get_height()
        target_height += 2.5 * LARGE_BUFF
        tip_point = self.get_tip()
        self.stretch_to_fit_width(target_width)
        self.stretch_to_fit_height(target_height)
        self.move_tip_to(tip_point)
        self.position_mobject_inside(self.content)

    def clear(self):
        self.add_content(VMobject())
        return self


class SpeechBubble(Bubble):
    CONFIG = {"file_name": "Bubbles_speech.svg", "height": 4}


class DoubleSpeechBubble(Bubble):
    CONFIG = {"file_name": "Bubbles_double_speech.svg", "height": 4}


class ThoughtBubble(Bubble):
    CONFIG = {
        "file_name": "Bubbles_thought.svg",
    }

    def __init__(self, **kwargs):
        Bubble.__init__(self, **kwargs)
        self.submobjects.sort(key=lambda m: m.get_bottom()[1])

    def make_green_screen(self):
        self.submobjects[-1].set_fill(GREEN_SCREEN, opacity=1)
        return self


class Car(SVGMobject):
    CONFIG = {
        "file_name": "Car",
        "height": 1,
        "color": LIGHT_GREY,
        "light_colors": [BLACK, BLACK],
    }

    def __init__(self, **kwargs):
        SVGMobject.__init__(self, **kwargs)

        path = self.submobjects[0]
        subpaths = path.get_subpaths()
        path.clear_points()
        for indices in [(0, 1), (2, 3), (4, 6, 7), (5,), (8,)]:
            part = VMobject()
            for index in indices:
                part.append_points(subpaths[index])
            path.add(part)

        self.set_height(self.height)
        self.set_stroke(color=WHITE, width=0)
        self.set_fill(self.color, opacity=1)

        orientation_line = Line(self.get_left(), self.get_right())
        orientation_line.set_stroke(width=0)
        self.add(orientation_line)
        self.orientation_line = orientation_line

        for light, color in zip(self.get_lights(), self.light_colors):
            light.set_fill(color, 1)
            light.is_subpath = False

        self.add_treds_to_tires()

    def move_to(self, point_or_mobject):
        vect = rotate_vector(UP + LEFT, self.orientation_line.get_angle())
        self.next_to(point_or_mobject, vect, buff=0)
        return self

    def get_front_line(self):
        return DashedLine(
            self.get_corner(UP + RIGHT),
            self.get_corner(DOWN + RIGHT),
            color=DISTANCE_COLOR,
            dash_length=0.05,
        )

    def add_treds_to_tires(self):
        for tire in self.get_tires():
            radius = tire.get_width() / 2
            center = tire.get_center()
            tred = Line(
                0.7 * radius * RIGHT, 1.1 * radius * RIGHT, stroke_width=2, color=BLACK
            )
            tred.rotate(PI / 5, about_point=tred.get_end())
            for theta in np.arange(0, 2 * np.pi, np.pi / 4):
                new_tred = tred.copy()
                new_tred.rotate(theta, about_point=ORIGIN)
                new_tred.shift(center)
                tire.add(new_tred)
        return self

    def get_tires(self):
        return VGroup(self[1][0], self[1][1])

    def get_lights(self):
        return VGroup(self.get_front_light(), self.get_rear_light())

    def get_front_light(self):
        return self[1][3]

    def get_rear_light(self):
        return self[1][4]


class VectorizedEarth(SVGMobject):
    CONFIG = {
        "file_name": "earth",
        "height": 1.5,
        "fill_color": BLACK,
    }

    def __init__(self, **kwargs):
        SVGMobject.__init__(self, **kwargs)
        circle = Circle(
            stroke_width=3,
            stroke_color=GREEN,
            fill_opacity=1,
            fill_color=BLUE_C,
        )
        circle.replace(self)
        self.add_to_back(circle)


class Logo(VMobject):
    CONFIG = {
        "pupil_radius": 1.0,
        "outer_radius": 2.0,
        "iris_background_blue": "#74C0E3",
        "iris_background_brown": "#8C6239",
        "blue_spike_colors": [
            "#528EA3",
            "#3E6576",
            "#224C5B",
            BLACK,
        ],
        "brown_spike_colors": [
            "#754C24",
            "#603813",
            "#42210b",
            BLACK,
        ],
        "n_spike_layers": 4,
        "n_spikes": 28,
        "spike_angle": TAU / 28,
    }

    def __init__(self, **kwargs):
        VMobject.__init__(self, **kwargs)
        self.add_iris_back()
        self.add_spikes()
        self.add_pupil()

    def add_iris_back(self):
        blue_iris_back = AnnularSector(
            inner_radius=self.pupil_radius,
            outer_radius=self.outer_radius,
            angle=270 * DEGREES,
            start_angle=180 * DEGREES,
            fill_color=self.iris_background_blue,
            fill_opacity=1,
            stroke_width=0,
        )
        brown_iris_back = AnnularSector(
            inner_radius=self.pupil_radius,
            outer_radius=self.outer_radius,
            angle=90 * DEGREES,
            start_angle=90 * DEGREES,
            fill_color=self.iris_background_brown,
            fill_opacity=1,
            stroke_width=0,
        )
        self.iris_background = VGroup(
            blue_iris_back,
            brown_iris_back,
        )
        self.add(self.iris_background)

    def add_spikes(self):
        layers = VGroup()
        radii = np.linspace(
            self.outer_radius,
            self.pupil_radius,
            self.n_spike_layers,
            endpoint=False,
        )
        radii[:2] = radii[1::-1]  # Swap first two
        if self.n_spike_layers > 2:
            radii[-1] = interpolate(radii[-1], self.pupil_radius, 0.25)

        for radius in radii:
            tip_angle = self.spike_angle
            half_base = radius * np.tan(tip_angle)
            triangle, right_half_triangle = [
                Polygon(
                    radius * UP,
                    half_base * RIGHT,
                    vertex3,
                    fill_opacity=1,
                    stroke_width=0,
                )
                for vertex3 in (
                    half_base * LEFT,
                    ORIGIN,
                )
            ]
            left_half_triangle = right_half_triangle.copy()
            left_half_triangle.flip(UP, about_point=ORIGIN)

            n_spikes = self.n_spikes
            full_spikes = [
                triangle.copy().rotate(-angle, about_point=ORIGIN)
                for angle in np.linspace(0, TAU, n_spikes, endpoint=False)
            ]
            index = (3 * n_spikes) // 4
            if radius == radii[0]:
                layer = VGroup(*full_spikes)
                layer.rotate(-TAU / n_spikes / 2, about_point=ORIGIN)
                layer.brown_index = index
            else:
                half_spikes = [
                    right_half_triangle.copy(),
                    left_half_triangle.copy().rotate(
                        90 * DEGREES,
                        about_point=ORIGIN,
                    ),
                    right_half_triangle.copy().rotate(
                        90 * DEGREES,
                        about_point=ORIGIN,
                    ),
                    left_half_triangle.copy(),
                ]
                layer = VGroup(
                    *it.chain(
                        half_spikes[:1],
                        full_spikes[1:index],
                        half_spikes[1:3],
                        full_spikes[index + 1 :],
                        half_spikes[3:],
                    )
                )
                layer.brown_index = index + 1

            layers.add(layer)

        # Color spikes
        blues = self.blue_spike_colors
        browns = self.brown_spike_colors
        for layer, blue, brown in zip(layers, blues, browns):
            index = layer.brown_index
            layer[:index].set_color(blue)
            layer[index:].set_color(brown)

        self.spike_layers = layers
        self.add(layers)

    def add_pupil(self):
        self.pupil = Circle(
            radius=self.pupil_radius,
            fill_color=BLACK,
            fill_opacity=1,
            stroke_width=0,
            sheen=0.0,
        )
        self.pupil.rotate(90 * DEGREES)
        self.add(self.pupil)

    def cut_pupil(self):
        pupil = self.pupil
        center = pupil.get_center()
        new_pupil = VGroup(
            *[
                pupil.copy().pointwise_become_partial(pupil, a, b)
                for (a, b) in [(0.25, 1), (0, 0.25)]
            ]
        )
        for sector in new_pupil:
            sector.add_cubic_bezier_curve_to(
                [sector.points[-1], *[center] * 3, *[sector.points[0]] * 2]
            )
        self.remove(pupil)
        self.add(new_pupil)
        self.pupil = new_pupil

    def get_blue_part_and_brown_part(self):
        if len(self.pupil) == 1:
            self.cut_pupil()
        # circle = Circle()
        # circle.set_stroke(width=0)
        # circle.set_fill(BLACK, opacity=1)
        # circle.match_width(self)
        # circle.move_to(self)
        blue_part = VGroup(
            self.iris_background[0],
            *[layer[: layer.brown_index] for layer in self.spike_layers],
            self.pupil[0],
        )
        brown_part = VGroup(
            self.iris_background[1],
            *[layer[layer.brown_index :] for layer in self.spike_layers],
            self.pupil[1],
        )
        return blue_part, brown_part


# Cards
class DeckOfCards(VGroup):
    def __init__(self, **kwargs):
        possible_values = list(map(str, list(range(1, 11)))) + ["J", "Q", "K"]
        possible_suits = ["hearts", "diamonds", "spades", "clubs"]
        VGroup.__init__(
            self,
            *[
                PlayingCard(value=value, suit=suit, **kwargs)
                for value in possible_values
                for suit in possible_suits
            ],
        )


class PlayingCard(VGroup):
    CONFIG = {
        "value": None,
        "suit": None,
        "key": None,  # String like "8H" or "KS"
        "height": 2,
        "height_to_width": 3.5 / 2.5,
        "card_height_to_symbol_height": 7,
        "card_width_to_corner_num_width": 10,
        "card_height_to_corner_num_height": 10,
        "color": LIGHT_GREY,
        "turned_over": False,
        "possible_suits": ["hearts", "diamonds", "spades", "clubs"],
        "possible_values": list(map(str, list(range(2, 11)))) + ["J", "Q", "K", "A"],
    }

    def __init__(self, key=None, **kwargs):
        VGroup.__init__(self, key=key, **kwargs)

    def generate_points(self):
        self.add(
            Rectangle(
                height=self.height,
                width=self.height / self.height_to_width,
                stroke_color=WHITE,
                stroke_width=2,
                fill_color=self.color,
                fill_opacity=1,
            )
        )
        if self.turned_over:
            self.set_fill(DARK_GREY)
            self.set_stroke(LIGHT_GREY)
            contents = VectorizedPoint(self.get_center())
        else:
            value = self.get_value()
            symbol = self.get_symbol()
            design = self.get_design(value, symbol)
            corner_numbers = self.get_corner_numbers(value, symbol)
            contents = VGroup(design, corner_numbers)
            self.design = design
            self.corner_numbers = corner_numbers
        self.add(contents)

    def get_value(self):
        value = self.value
        if value is None:
            if self.key is not None:
                value = self.key[:-1]
            else:
                value = random.choice(self.possible_values)
        value = string.upper(str(value))
        if value == "1":
            value = "A"
        if value not in self.possible_values:
            raise Exception("Invalid card value")

        face_card_to_value = {
            "J": 11,
            "Q": 12,
            "K": 13,
            "A": 14,
        }
        try:
            self.numerical_value = int(value)
        except:
            self.numerical_value = face_card_to_value[value]
        return value

    def get_symbol(self):
        suit = self.suit
        if suit is None:
            if self.key is not None:
                suit = dict([(string.upper(s[0]), s) for s in self.possible_suits])[
                    string.upper(self.key[-1])
                ]
            else:
                suit = random.choice(self.possible_suits)
        if suit not in self.possible_suits:
            raise Exception("Invalud suit value")
        self.suit = suit
        symbol_height = float(self.height) / self.card_height_to_symbol_height
        symbol = SuitSymbol(suit, height=symbol_height)
        return symbol

    def get_design(self, value, symbol):
        if value == "A":
            return self.get_ace_design(symbol)
        if value in list(map(str, list(range(2, 11)))):
            return self.get_number_design(value, symbol)
        else:
            return self.get_face_card_design(value, symbol)

    def get_ace_design(self, symbol):
        design = symbol.copy().scale(1.5)
        design.move_to(self)
        return design

    def get_number_design(self, value, symbol):
        num = int(value)
        n_rows = {
            2: 2,
            3: 3,
            4: 2,
            5: 2,
            6: 3,
            7: 3,
            8: 3,
            9: 4,
            10: 4,
        }[num]
        n_cols = 1 if num in [2, 3] else 2
        insertion_indices = {
            5: [0],
            7: [0],
            8: [0, 1],
            9: [1],
            10: [0, 2],
        }.get(num, [])

        top = self.get_top() + symbol.get_height() * DOWN
        bottom = self.get_bottom() + symbol.get_height() * UP
        column_points = [
            interpolate(top, bottom, alpha) for alpha in np.linspace(0, 1, n_rows)
        ]

        design = VGroup(*[symbol.copy().move_to(point) for point in column_points])
        if n_cols == 2:
            space = 0.2 * self.get_width()
            column_copy = design.copy().shift(space * RIGHT)
            design.shift(space * LEFT)
            design.add(*column_copy)
        design.add(
            *[
                symbol.copy().move_to(center_of_mass(column_points[i : i + 2]))
                for i in insertion_indices
            ]
        )
        for symbol in design:
            if symbol.get_center()[1] < self.get_center()[1]:
                symbol.rotate_in_place(np.pi)
        return design

    def get_face_card_design(self, value, symbol):
        return VGroup()

    def get_corner_numbers(self, value, symbol):
        value_mob = Tex(value)
        width = self.get_width() / self.card_width_to_corner_num_width
        height = self.get_height() / self.card_height_to_corner_num_height
        value_mob.set_width(width)
        value_mob.stretch_to_fit_height(height)
        value_mob.next_to(
            self.get_corner(UP + LEFT), DOWN + RIGHT, buff=MED_LARGE_BUFF * width
        )
        value_mob.set_color(symbol.get_color())
        corner_symbol = symbol.copy()
        corner_symbol.set_width(width)
        corner_symbol.next_to(value_mob, DOWN, buff=MED_SMALL_BUFF * width)
        corner_group = VGroup(value_mob, corner_symbol)
        opposite_corner_group = corner_group.copy()
        opposite_corner_group.rotate(np.pi, about_point=self.get_center())

        return VGroup(corner_group, opposite_corner_group)


class SuitSymbol(SVGMobject):
    CONFIG = {
        "height": 0.5,
        "fill_opacity": 1,
        "stroke_width": 0,
        "red": "#D02028",
        "black": BLACK,
    }

    def __init__(self, suit_name, **kwargs):
        digest_config(self, kwargs)
        suits_to_colors = {
            "hearts": self.red,
            "diamonds": self.red,
            "spades": self.black,
            "clubs": self.black,
        }
        if suit_name not in suits_to_colors:
            raise ValueError("Invalid suit name")
        SVGMobject.__init__(self, file_name=suit_name, **kwargs)

        color = suits_to_colors[suit_name]
        self.set_stroke(width=0)
        self.set_fill(color, 1)
        self.set_height(self.height)
