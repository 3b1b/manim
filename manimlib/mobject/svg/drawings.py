from operator import le
from os import DirEntry
from manimlib.animation.animation import Animation
from manimlib.animation.composition import AnimationGroup
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
from manimlib.mobject.three_dimensions import VCube
from manimlib.mobject.three_dimensions import Prismify
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.config_ops import digest_config
from manimlib.utils.rate_functions import linear
from manimlib.utils.space_ops import angle_of_vector
from manimlib.utils.space_ops import complex_to_R3
from manimlib.utils.space_ops import midpoint
from manimlib.utils.space_ops import rotate_vector
from manimlib.utils.space_ops import compass_directions

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Tuple, Sequence, Callable
    from manimlib.constants import ManimColor, np_vector

class Checkmark(TexTextFromPresetString):
    tex: str = R"\ding{51}"
    default_color: str = GREEN


class Exmark(TexTextFromPresetString):
    tex: str = R"\ding{55}"
    default_color: str = RED


class Lightbulb(SVGMobject):
    file_name = "lightbulb"

    def __init__(
        self,
        height: float = 1.0,
        color: ManimColor = YELLOW,
        stroke_width: float = 3.0,
        fill_opacity: float = 0.0,
        **kwargs
    ):
        super().__init__(
            height=height,
            color=color,
            stroke_width=stroke_width,
            fill_opacity=fill_opacity,
            **kwargs
        )
        self.insert_n_curves(25)


class Speedometer(VMobject):
    def __init__(
        self,
        arc_angle: float = 4 * np.pi / 3,
        num_ticks: int = 8,
        tick_length: float = 0.2,
        needle_width: float = 0.1,
        needle_height: float = 0.8,
        needle_color: ManimColor = YELLOW,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.arc_angle = arc_angle
        self.num_ticks = num_ticks
        self.tick_length = tick_length
        self.needle_width = needle_width
        self.needle_height = needle_height
        self.needle_color = needle_color

        start_angle = np.pi / 2 + arc_angle / 2
        end_angle = np.pi / 2 - arc_angle / 2
        self.arc = Arc(
            start_angle=start_angle,
            angle=-self.arc_angle
        )
        self.add(self.arc)
        tick_angle_range = np.linspace(start_angle, end_angle, num_ticks)
        for index, angle in enumerate(tick_angle_range):
            vect = rotate_vector(RIGHT, angle)
            tick = Line((1 - tick_length) * vect, vect)
            label = Tex(str(10 * index))
            label.set_height(tick_length)
            label.shift((1 + tick_length) * vect)
            self.add(tick, label)

        needle = Polygon(
            LEFT, UP, RIGHT,
            stroke_width=0,
            fill_opacity=1,
            fill_color=self.needle_color
        )
        needle.stretch_to_fit_width(needle_width)
        needle.stretch_to_fit_height(needle_height)
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
        self.needle.rotate(angle, about_point=self.arc.get_arc_center())
        return self

    def move_needle_to_velocity(self, velocity):
        max_velocity = 10 * (self.num_ticks - 1)
        proportion = float(velocity) / max_velocity
        start_angle = np.pi / 2 + self.arc_angle / 2
        target_angle = start_angle - self.arc_angle * proportion
        self.rotate_needle(target_angle - self.get_needle_angle())
        return self


class Laptop(VGroup):
    def __init__(
        self,
        width: float = 3,
        body_dimensions: Tuple[float, float, float] = (4.0, 3.0, 0.05),
        screen_thickness: float = 0.01,
        keyboard_width_to_body_width: float = 0.9,
        keyboard_height_to_body_height: float = 0.5,
        screen_width_to_screen_plate_width: float = 0.9,
        key_color_kwargs: dict = dict(
            stroke_width=0,
            fill_color=BLACK,
            fill_opacity=1,
        ),
        fill_opacity: float = 1.0,
        stroke_width: float = 0.0,
        body_color: ManimColor = GREY_B,
        shaded_body_color: ManimColor = GREY,
        open_angle: float = np.pi / 4,
        **kwargs
    ):
        super().__init__(**kwargs)

        body = VCube(side_length=1)
        for dim, scale_factor in enumerate(body_dimensions):
            body.stretch(scale_factor, dim=dim)
        body.set_width(width)
        body.set_fill(shaded_body_color, opacity=1)
        body.sort(lambda p: p[2])
        body[-1].set_fill(body_color)
        screen_plate = body.copy()
        keyboard = VGroup(*[
            VGroup(*[
                Square(**key_color_kwargs)
                for x in range(12 - y % 2)
            ]).arrange(RIGHT, buff=SMALL_BUFF)
            for y in range(4)
        ]).arrange(DOWN, buff=MED_SMALL_BUFF)
        keyboard.stretch_to_fit_width(
            keyboard_width_to_body_width * body.get_width(),
        )
        keyboard.stretch_to_fit_height(
            keyboard_height_to_body_height * body.get_height(),
        )
        keyboard.next_to(body, OUT, buff=0.1 * SMALL_BUFF)
        keyboard.shift(MED_SMALL_BUFF * UP)
        body.add(keyboard)

        screen_plate.stretch(screen_thickness /
                             body_dimensions[2], dim=2)
        screen = Rectangle(
            stroke_width=0,
            fill_color=BLACK,
            fill_opacity=1,
        )
        screen.replace(screen_plate, stretch=True)
        screen.scale(screen_width_to_screen_plate_width)
        screen.next_to(screen_plate, OUT, buff=0.1 * SMALL_BUFF)
        screen_plate.add(screen)
        screen_plate.next_to(body, UP, buff=0)
        screen_plate.rotate(
            open_angle, RIGHT,
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
    file_name: str = "video_icon"

    def __init__(
        self,
        width: float = 1.2,
        color=BLUE_A,
        **kwargs
    ):
        super().__init__(color=color, **kwargs)
        self.set_width(width)


class VideoSeries(VGroup):
    def __init__(
        self,
        num_videos: int = 11,
        gradient_colors: Sequence[ManimColor] = [BLUE_B, BLUE_D],
        width: float = FRAME_WIDTH - MED_LARGE_BUFF,
        **kwargs
    ):
        super().__init__(
            *(VideoIcon() for x in range(num_videos)),
            **kwargs
        )
        self.arrange(RIGHT)
        self.set_width(width)
        self.set_color_by_gradient(*gradient_colors)


class Clock(VGroup):
    def __init__(
        self,
        stroke_color: ManimColor = WHITE,
        stroke_width: float = 3.0,
        hour_hand_height: float = 0.3,
        minute_hand_height: float = 0.6,
        tick_length: float = 0.1,
        **kwargs,
    ):
        style = dict(stroke_color=stroke_color, stroke_width=stroke_width)
        circle = Circle(**style)
        ticks = []
        for x, point in enumerate(compass_directions(12, UP)):
            length = tick_length
            if x % 3 == 0:
                length *= 2
            ticks.append(Line(point, (1 - length) * point, **style))
        self.hour_hand = Line(ORIGIN, hour_hand_height * UP, **style)
        self.minute_hand = Line(ORIGIN, minute_hand_height * UP, **style)

        super().__init__(
            circle, self.hour_hand, self.minute_hand,
            *ticks
        )


class ClockPassesTime(AnimationGroup):
    def __init__(
        self,
        clock: Clock,
        run_time: float = 5.0,
        hours_passed: float = 12.0,
        rate_func: Callable[[float], float] = linear,
        **kwargs
    ):
        rot_kwargs = dict(
            axis=OUT,
            about_point=clock.get_center()
        )
        hour_radians = -hours_passed * 2 * PI / 12
        super().__init__(
            Rotating(
                clock.hour_hand,
                angle=hour_radians,
                **rot_kwargs
            ),
            Rotating(
                clock.minute_hand,
                angle=12 * hour_radians,
                **rot_kwargs
            ),
            **kwargs
        )


class Bubble(SVGMobject):
    file_name: str = "Bubbles_speech.svg"

    def __init__(
        self,
        direction: np_vector = LEFT,
        center_point: np_vector = ORIGIN,
        content_scale_factor: float = 0.7,
        height: float = 4.0,
        width: float = 8.0,
        max_height: float | None = None,
        max_width: float | None = None,
        bubble_center_adjustment_factor: float = 0.125,
        fill_color: ManimColor = BLACK,
        fill_opacity: float = 0.8,
        stroke_color: ManimColor = WHITE,
        stroke_width: float = 3.0,
        **kwargs
    ):
        self.direction = direction
        self.bubble_center_adjustment_factor = bubble_center_adjustment_factor

        super().__init__(
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            **kwargs
        )

        self.center()
        self.set_height(height, stretch=True)
        self.set_width(width, stretch=True)
        if max_height:
            self.set_max_height(max_height)
        if max_width:
            self.set_max_width(max_width)
        if direction[0] > 0:
            self.flip()

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
        if want_to_flip:
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
    file_name: str = "Bubbles_speech.svg"


class DoubleSpeechBubble(Bubble):
    file_name: str = "Bubbles_double_speech.svg"


class ThoughtBubble(Bubble):
    file_name: str = "Bubbles_thought.svg"

    def __init__(self, **kwargs):
        Bubble.__init__(self, **kwargs)
        self.submobjects.sort(
            key=lambda m: m.get_bottom()[1]
        )

    def make_green_screen(self):
        self.submobjects[-1].set_fill(GREEN_SCREEN, opacity=1)
        return self


class VectorizedEarth(SVGMobject):
    file_name: str = "earth"

    def __init__(
        self,
        height: float = 2.0,
        **kwargs
    ):
        super().__init__(height=height, **kwargs)
        self.insert_n_curves(20)
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
    def __init__(
        self,
        reflectiveness: float = 1.0,
        stroke_width: float = 0.25,
        stroke_color: ManimColor = BLACK,
        key_depth: float = 0.1,
        black_key_shift: float = 0.05,
        piano_2d_config: dict = dict(
            white_key_color=GREY_A,
            key_buff=0.001
        ),
        **kwargs
    ):
        piano_2d = Piano(**piano_2d_config)
        super().__init__(*(
            Prismify(key, key_depth)
            for key in piano_2d
        ))
        self.set_stroke(stroke_color, stroke_width)
        self.apply_depth_test()

        # Elevate black keys
        for i, key in enumerate(self):
            if piano_2d[i] in piano_2d.black_keys:
                key.shift(black_key_shift * OUT)
