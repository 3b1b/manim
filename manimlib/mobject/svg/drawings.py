from manimlib.animation.animation import Animation
from manimlib.animation.rotation import Rotating
from manimlib.constants import *
from manimlib.mobject.boolean_ops import Difference
from manimlib.mobject.geometry import Arc
from manimlib.mobject.geometry import Circle
from manimlib.mobject.geometry import Line
from manimlib.mobject.geometry import Polygon
from manimlib.mobject.geometry import Rectangle
from manimlib.mobject.geometry import Square
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.svg.svg_mobject import SVGMobject
from manimlib.mobject.svg.tex_mobject import Tex
from manimlib.mobject.svg.tex_mobject import TexText
from manimlib.mobject.svg.tex_mobject import TexTextFromPresetString
from manimlib.mobject.three_dimensions import Cube
from manimlib.mobject.three_dimensions import Prismify
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.config_ops import digest_config
from manimlib.utils.rate_functions import linear
from manimlib.utils.space_ops import angle_of_vector
from manimlib.utils.space_ops import complex_to_R3
from manimlib.utils.space_ops import midpoint
from manimlib.utils.space_ops import rotate_vector

class Checkmark(TexTextFromPresetString):
    tex: str = R"\ding{51}"
    default_color: str = GREEN


class Exmark(TexTextFromPresetString):
    tex: str = R"\ding{55}"
    default_color: str = RED



class Lightbulb(SVGMobject):
    CONFIG = {
        "height": 1,
        "stroke_color": YELLOW,
        "stroke_width": 3,
        "fill_color": YELLOW,
        "fill_opacity": 0,
    }

    def __init__(self, **kwargs):
        super().__init__("lightbulb", **kwargs)
        self.insert_n_curves(25)


class Speedometer(VMobject):
    CONFIG = {
        "arc_angle": 4 * np.pi / 3,
        "num_ticks": 8,
        "tick_length": 0.2,
        "needle_width": 0.1,
        "needle_height": 0.8,
        "needle_color": YELLOW,
    }

    def init_points(self):
        start_angle = np.pi / 2 + self.arc_angle / 2
        end_angle = np.pi / 2 - self.arc_angle / 2
        self.add(Arc(
            start_angle=start_angle,
            angle=-self.arc_angle
        ))
        tick_angle_range = np.linspace(start_angle, end_angle, self.num_ticks)
        for index, angle in enumerate(tick_angle_range):
            vect = rotate_vector(RIGHT, angle)
            tick = Line((1 - self.tick_length) * vect, vect)
            label = Tex(str(10 * index))
            label.set_height(self.tick_length)
            label.shift((1 + self.tick_length) * vect)
            self.add(tick, label)

        needle = Polygon(
            LEFT, UP, RIGHT,
            stroke_width=0,
            fill_opacity=1,
            fill_color=self.needle_color
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
        return angle_of_vector(
            self.get_needle_tip() - self.get_center()
        )

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
        "body_color": GREY_B,
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
        keyboard = VGroup(*[
            VGroup(*[
                Square(**self.key_color_kwargs)
                for x in range(12 - y % 2)
            ]).arrange(RIGHT, buff=SMALL_BUFF)
            for y in range(4)
        ]).arrange(DOWN, buff=MED_SMALL_BUFF)
        keyboard.stretch_to_fit_width(
            self.keyboard_width_to_body_width * body.get_width(),
        )
        keyboard.stretch_to_fit_height(
            self.keyboard_height_to_body_height * body.get_height(),
        )
        keyboard.next_to(body, OUT, buff=0.1 * SMALL_BUFF)
        keyboard.shift(MED_SMALL_BUFF * UP)
        body.add(keyboard)

        screen_plate.stretch(self.screen_thickness /
                             self.body_dimensions[2], dim=2)
        screen = Rectangle(
            stroke_width=0,
            fill_color=BLACK,
            fill_opacity=1,
        )
        screen.replace(screen_plate, stretch=True)
        screen.scale(self.screen_width_to_screen_plate_width)
        screen.next_to(screen_plate, OUT, buff=0.1 * SMALL_BUFF)
        screen_plate.add(screen)
        screen_plate.next_to(body, UP, buff=0)
        screen_plate.rotate(
            self.open_angle, RIGHT,
            about_point=screen_plate.get_bottom()
        )
        self.screen_plate = screen_plate
        self.screen = screen

        axis = Line(
            body.get_corner(UP + LEFT + OUT),
            body.get_corner(UP + RIGHT + OUT),
            color=BLACK,
            stroke_width=2
        )
        self.axis = axis

        self.add(body, screen_plate, axis)
        self.rotate(5 * np.pi / 12, LEFT, about_point=ORIGIN)
        self.rotate(np.pi / 6, DOWN, about_point=ORIGIN)


class VideoIcon(SVGMobject):
    CONFIG = {
        "width": FRAME_WIDTH / 12.,
    }

    def __init__(self, **kwargs):
        super().__init__(file_name="video_icon", **kwargs)
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
        self.set_width(FRAME_WIDTH - MED_LARGE_BUFF)
        self.set_color_by_gradient(*self.gradient_colors)


class Clock(VGroup):
    CONFIG = {}

    def __init__(self, **kwargs):
        circle = Circle(color=WHITE)
        ticks = []
        for x in range(12):
            alpha = x / 12.
            point = complex_to_R3(
                np.exp(2 * np.pi * alpha * complex(0, 1))
            )
            length = 0.2 if x % 3 == 0 else 0.1
            ticks.append(
                Line(point, (1 - length) * point)
            )
        self.hour_hand = Line(ORIGIN, 0.3 * UP)
        self.minute_hand = Line(ORIGIN, 0.6 * UP)
        # for hand in self.hour_hand, self.minute_hand:
        #     #Balance out where the center is
        #     hand.add(VectorizedPoint(-hand.get_end()))

        VGroup.__init__(
            self, circle,
            self.hour_hand, self.minute_hand,
            *ticks
        )


class ClockPassesTime(Animation):
    CONFIG = {
        "run_time": 5,
        "hours_passed": 12,
        "rate_func": linear,
    }

    def __init__(self, clock, **kwargs):
        digest_config(self, kwargs)
        assert(isinstance(clock, Clock))
        rot_kwargs = {
            "axis": OUT,
            "about_point": clock.get_center()
        }
        hour_radians = -self.hours_passed * 2 * np.pi / 12
        self.hour_rotation = Rotating(
            clock.hour_hand,
            angle=hour_radians,
            **rot_kwargs
        )
        self.hour_rotation.begin()
        self.minute_rotation = Rotating(
            clock.minute_hand,
            angle=12 * hour_radians,
            **rot_kwargs
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
        "content_scale_factor": 0.7,
        "height": 5,
        "width": 8,
        "max_height": None,
        "max_width": None,
        "bubble_center_adjustment_factor": 1. / 8,
        "file_name": None,
        "fill_color": BLACK,
        "fill_opacity": 0.8,
        "stroke_color": WHITE,
        "stroke_width": 3,
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        if self.file_name is None:
            raise Exception("Must invoke Bubble subclass")
        SVGMobject.__init__(self, self.file_name, **kwargs)
        self.center()
        self.set_height(self.height, stretch=True)
        self.set_width(self.width, stretch=True)
        if self.max_height:
            self.set_max_height(self.max_height)
        if self.max_width:
            self.set_max_width(self.max_width)
        if self.direction[0] > 0:
            self.flip()
        if "direction" in kwargs:
            self.direction = kwargs["direction"]
            self.direction_was_specified = True
        else:
            self.direction_was_specified = False
        self.content = Mobject()
        self.refresh_triangulation()

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
        self.refresh_unit_normal()
        self.refresh_triangulation()
        if abs(axis[1]) > 0:
            self.direction = -np.array(self.direction)
        return self

    def pin_to(self, mobject):
        mob_center = mobject.get_center()
        want_to_flip = np.sign(mob_center[0]) != np.sign(self.direction[0])
        can_flip = not self.direction_was_specified
        if want_to_flip and can_flip:
            self.flip()
        boundary_point = mobject.get_bounding_box_point(UP - self.direction)
        vector_from_center = 1.0 * (boundary_point - mob_center)
        self.move_tip_to(mob_center + vector_from_center)
        return self

    def position_mobject_inside(self, mobject):
        mobject.set_max_width(self.content_scale_factor * self.get_width())
        mobject.set_max_height(self.content_scale_factor * self.get_height() / 1.5)
        mobject.shift(self.get_bubble_center() - mobject.get_center())
        return mobject

    def add_content(self, mobject):
        self.position_mobject_inside(mobject)
        self.content = mobject
        return self.content

    def write(self, *text):
        self.add_content(TexText(*text))
        return self

    def resize_to_content(self, buff=0.75):
        width = self.content.get_width()
        height = self.content.get_height()
        target_width = width + min(buff, height)
        target_height = 1.35 * (self.content.get_height() + buff)
        tip_point = self.get_tip()
        self.stretch_to_fit_width(target_width, about_point=tip_point)
        self.stretch_to_fit_height(target_height, about_point=tip_point)
        self.position_mobject_inside(self.content)

    def clear(self):
        self.add_content(VMobject())
        return self


class SpeechBubble(Bubble):
    CONFIG = {
        "file_name": "Bubbles_speech.svg",
        "height": 4
    }


class DoubleSpeechBubble(Bubble):
    CONFIG = {
        "file_name": "Bubbles_double_speech.svg",
        "height": 4
    }


class ThoughtBubble(Bubble):
    CONFIG = {
        "file_name": "Bubbles_thought.svg",
    }

    def __init__(self, **kwargs):
        Bubble.__init__(self, **kwargs)
        self.submobjects.sort(
            key=lambda m: m.get_bottom()[1]
        )

    def make_green_screen(self):
        self.submobjects[-1].set_fill(GREEN_SCREEN, opacity=1)
        return self


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


class Piano(VGroup):
    n_white_keys = 52
    black_pattern = [0, 2, 3, 5, 6]
    white_keys_per_octave = 7
    white_key_dims = (0.15, 1.0)
    black_key_dims = (0.1, 0.66)
    key_buff = 0.02
    white_key_color = WHITE
    black_key_color = GREY_E
    total_width = 13

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_white_keys()
        self.add_black_keys()
        self.sort_keys()
        self[:-1].reverse_points()
        self.set_width(self.total_width)

    def add_white_keys(self):
        key = Rectangle(*self.white_key_dims)
        key.set_fill(self.white_key_color, 1)
        key.set_stroke(width=0)
        self.white_keys = key.get_grid(1, self.n_white_keys, buff=self.key_buff)
        self.add(*self.white_keys)

    def add_black_keys(self):
        key = Rectangle(*self.black_key_dims)
        key.set_fill(self.black_key_color, 1)
        key.set_stroke(width=0)

        self.black_keys = VGroup()
        for i in range(len(self.white_keys) - 1):
            if i % self.white_keys_per_octave not in self.black_pattern:
                continue
            wk1 = self.white_keys[i]
            wk2 = self.white_keys[i + 1]
            bk = key.copy()
            bk.move_to(midpoint(wk1.get_top(), wk2.get_top()), UP)
            big_bk = bk.copy()
            big_bk.stretch((bk.get_width() + self.key_buff) / bk.get_width(), 0)
            big_bk.stretch((bk.get_height() + self.key_buff) / bk.get_height(), 1)
            big_bk.move_to(bk, UP)
            for wk in wk1, wk2:
                wk.become(Difference(wk, big_bk).match_style(wk))
            self.black_keys.add(bk)
        self.add(*self.black_keys)

    def sort_keys(self):
        self.sort(lambda p: p[0])


class Piano3D(VGroup):
    CONFIG = {
        "depth_test": True,
        "reflectiveness": 1.0,
        "stroke_width": 0.25,
        "stroke_color": BLACK,
        "key_depth": 0.1,
        "black_key_shift": 0.05,
    }
    piano_2d_config = {
        "white_key_color": GREY_A,
        "key_buff": 0.001
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        piano_2d = Piano(**self.piano_2d_config)
        super().__init__(*(
            Prismify(key, self.key_depth)
            for key in piano_2d
        ))
        self.set_stroke(self.stroke_color, self.stroke_width)
        self.apply_depth_test()
        # Elevate black keys
        for i, key in enumerate(self):
            if piano_2d[i] in piano_2d.black_keys:
                key.shift(self.black_key_shift * OUT)
