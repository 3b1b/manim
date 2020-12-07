r"""Animate the display or removal of a mobject from a scene.

.. manim:: CreationModule
    :hide_source:

    from manim import ManimBanner
    class CreationModule(Scene):
        def construct(self):
            s1 = Square()
            s2 = Square()
            s3 = Square()
            s4 = Square()
            VGroup(s1, s2, s3, s4).set_x(0).arrange(buff=1.9).shift(UP)
            s5 = Square()
            s6 = Square()
            s7 = Square()
            VGroup(s5, s6, s7).set_x(0).arrange(buff=2.6).shift(2 * DOWN)
            t1 = Text("Write").scale(0.5).next_to(s1, UP)
            t2 = Text("AddTextLetterByLetter").scale(0.5).next_to(s2, UP)
            t3 = Text("ShowCreation").scale(0.5).next_to(s3, UP)
            t4 = Text("Uncreate").scale(0.5).next_to(s4, UP)
            t5 = Text("DrawBorderThenFill").scale(0.5).next_to(s5, UP)
            t6 = Text("ShowIncreasingSubsets").scale(0.45).next_to(s6, UP)
            t7 = Text("ShowSubmobjectsOneByOne").scale(0.45).next_to(s7, UP)

            self.add(s1, s2, s3, s4, s5, s6, s7, t1, t2, t3, t4, t5, t6, t7)

            texts = [Text("manim").scale(0.6), Text("manim").scale(0.6)]
            texts[0].move_to(s1.get_center())
            texts[1].move_to(s2.get_center())
            self.add(*texts)

            objs = [ManimBanner().scale(0.25) for _ in range(5)]
            objs[0].move_to(s3.get_center())
            objs[1].move_to(s4.get_center())
            objs[2].move_to(s5.get_center())
            objs[3].move_to(s6.get_center())
            objs[4].move_to(s7.get_center())
            self.add(*objs)

            self.play(
                # text creation
                Write(texts[0]),
                AddTextLetterByLetter(texts[1]),
                # mobject creation
                ShowCreation(objs[0]),
                Uncreate(objs[1]),
                DrawBorderThenFill(objs[2]),
                ShowIncreasingSubsets(objs[3]),
                ShowSubmobjectsOneByOne(objs[4]),
                run_time=3,
            )

            self.wait()

"""


__all__ = [
    "ShowPartial",
    "ShowCreation",
    "Uncreate",
    "DrawBorderThenFill",
    "Write",
    "ShowIncreasingSubsets",
    "AddTextLetterByLetter",
    "ShowSubmobjectsOneByOne",
    "AddTextWordByWord",
]


import itertools as it
import typing

import numpy as np
from colour import Color

if typing.TYPE_CHECKING:
    from manim.mobject.svg.text_mobject import Text

from ..animation.animation import Animation
from ..animation.composition import Succession
from ..mobject.mobject import Group, Mobject
from ..mobject.types.vectorized_mobject import VMobject
from ..utils.bezier import integer_interpolate
from ..utils.rate_functions import double_smooth, linear, smooth


class ShowPartial(Animation):
    """Abstract class for Animations that show the VMobject partially.

    Raises
    ------
    :class:`TypeError`
        If ``mobject`` is not an instance of :class:`~.VMobject`.

    See Also
    --------
    :class:`ShowCreation`, :class:`~.ShowPassingFlash`

    """

    def __init__(self, mobject: VMobject, **kwargs):
        if not isinstance(mobject, VMobject):
            raise TypeError("This Animation only works on vectorized mobjects")
        super().__init__(mobject, **kwargs)

    def interpolate_submobject(
        self, submobject: Mobject, starting_sumobject: Mobject, alpha: float
    ) -> None:
        submobject.pointwise_become_partial(
            starting_sumobject, *self._get_bounds(alpha)
        )

    def _get_bounds(self, alpha: float) -> None:
        raise NotImplementedError("Please use ShowCreation or ShowPassingFlash")


class ShowCreation(ShowPartial):
    """Incrementally show a VMobject.

    Parameters
    ----------
    mobject : :class:`~.VMobject`
        The VMobject to animate.

    Raises
    ------
    :class:`TypeError`
        If ``mobject`` is not an instance of :class:`~.VMobject`.

    Examples
    --------
    .. manim:: ShowCreationScene

        class ShowCreationScene(Scene):
            def construct(self):
                self.play(ShowCreation(Square()))

    See Also
    --------
    :class:`~.ShowPassingFlash`

    """

    def __init__(self, mobject: VMobject, lag_ratio: float = 1.0, **kwargs) -> None:
        super().__init__(mobject, lag_ratio=lag_ratio, **kwargs)

    def _get_bounds(self, alpha: float) -> typing.Tuple[int, float]:
        return (0, alpha)


class Uncreate(ShowCreation):
    """Like :class:`ShowCreation` but in reverse.

    See Also
    --------
    :class:`ShowCreation`

    """

    def __init__(
        self,
        mobject: VMobject,
        rate_func: typing.Callable[[float, float], np.ndarray] = lambda t: smooth(
            1 - t
        ),
        remover: bool = True,
        **kwargs
    ) -> None:
        super().__init__(mobject, rate_func=rate_func, remover=remover, **kwargs)


class DrawBorderThenFill(Animation):
    """Draw the border first and then show the fill."""

    def __init__(
        self,
        vmobject: VMobject,
        run_time: float = 2,
        rate_func: typing.Callable[[float], np.ndarray] = double_smooth,
        stroke_width: float = 2,
        stroke_color: str = None,
        draw_border_animation_config: typing.Dict = {},  # what does this dict accept?
        fill_animation_config: typing.Dict = {},
        **kwargs
    ) -> None:
        self._typecheck_input(vmobject)
        super().__init__(vmobject, run_time=run_time, rate_func=rate_func, **kwargs)
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color
        self.draw_border_animation_config = draw_border_animation_config
        self.fill_animation_config = fill_animation_config
        self.outline = None

    def _typecheck_input(self, vmobject: VMobject) -> None:
        if not isinstance(vmobject, VMobject):
            raise TypeError("DrawBorderThenFill only works for VMobjects")

    def begin(self) -> None:
        self.outline = self.get_outline()
        super().begin()

    def get_outline(self) -> Mobject:
        outline = self.mobject.copy()
        outline.set_fill(opacity=0)
        for sm in outline.family_members_with_points():
            sm.set_stroke(color=self.get_stroke_color(sm), width=self.stroke_width)
        return outline

    def get_stroke_color(self, vmobject: VMobject) -> Color:
        if self.stroke_color:
            return self.stroke_color
        elif vmobject.get_stroke_width() > 0:
            return vmobject.get_stroke_color()
        return vmobject.get_color()

    def get_all_mobjects(self) -> typing.List[typing.Union[Mobject, None]]:
        return [*super().get_all_mobjects(), self.outline]

    def interpolate_submobject(
        self, submobject: Mobject, starting_sumobject: Mobject, outline, alpha: float
    ) -> None:  # Fixme: not matching the parent class? What is outline doing here?
        index, subalpha = integer_interpolate(0, 2, alpha)
        if index == 0:
            submobject.pointwise_become_partial(outline, 0, subalpha)
            submobject.match_style(outline)
        else:
            submobject.interpolate(outline, starting_sumobject, subalpha)


class Write(DrawBorderThenFill):
    """Simulate hand-writing a :class:`~.Text` or hand-drawing a :class:`~.VMobject`."""

    def __init__(
        self,
        vmobject: VMobject,
        run_time: float = None,
        lag_ratio: float = None,
        rate_func: typing.Callable[[float], np.ndarray] = linear,
        **kwargs
    ) -> None:
        self.run_time = run_time
        self.lag_ratio = lag_ratio
        self._set_default_config_from_length(vmobject)
        super().__init__(
            vmobject,
            run_time=self.run_time,
            lag_ratio=self.lag_ratio,
            rate_func=rate_func,
            **kwargs,
        )

    def _set_default_config_from_length(self, vmobject: VMobject) -> None:
        length = len(vmobject.family_members_with_points())
        if self.run_time is None:
            if length < 15:
                self.run_time = 1
            else:
                self.run_time = 2
        if self.lag_ratio is None:
            self.lag_ratio = min(4.0 / length, 0.2)


class ShowIncreasingSubsets(Animation):
    """Show one submobject at a time, leaving all previous ones displayed on screen."""

    def __init__(
        self,
        group: Mobject,
        suspend_mobject_updating: bool = False,
        int_func: typing.Callable[[np.ndarray], np.ndarray] = np.floor,
        **kwargs
    ) -> None:
        self.all_submobs = list(group.submobjects)
        self.int_func = int_func
        super().__init__(
            group, suspend_mobject_updating=suspend_mobject_updating, **kwargs
        )

    def interpolate_mobject(self, alpha: float) -> None:
        n_submobs = len(self.all_submobs)
        index = int(self.int_func(alpha * n_submobs))
        self.update_submobject_list(index)

    def update_submobject_list(self, index: int) -> None:
        self.mobject.submobjects = self.all_submobs[:index]


class AddTextLetterByLetter(ShowIncreasingSubsets):
    """Show a :class:`~.Text` letter by letter on the scene.

    Parameters
    ----------
    time_per_char : :class:`float`
        Frequency of appearance of the letters.

    """

    def __init__(
        self,
        text: "Text",
        suspend_mobject_updating: bool = False,
        int_func: typing.Callable[[np.ndarray], np.ndarray] = np.ceil,
        rate_func: typing.Callable[[float], float] = linear,
        time_per_char: float = 0.1,
        run_time: typing.Optional[float] = None,
        **kwargs
    ) -> None:
        # time_per_char must be above 0.06, or the animation won't finish
        self.time_per_char = time_per_char
        self.run_time = run_time
        if self.run_time is None:
            self.run_time = np.max((0.06, self.time_per_char)) * len(text)

        super().__init__(
            text,
            suspend_mobject_updating=suspend_mobject_updating,
            int_func=int_func,
            rate_func=rate_func,
            run_time=self.run_time,
            **kwargs,
        )


class ShowSubmobjectsOneByOne(ShowIncreasingSubsets):
    """Show one submobject at a time, removing all previously displayed ones from screen."""

    def __init__(
        self,
        group: typing.Iterable[Mobject],
        int_func: typing.Callable[[np.ndarray], np.ndarray] = np.ceil,
        **kwargs
    ) -> None:
        new_group = Group(*group)
        super().__init__(new_group, int_func=int_func, **kwargs)

    def update_submobject_list(self, index: int) -> None:
        if index == 0:
            self.mobject.submobjects = []
        else:
            self.mobject.submobjects = self.all_submobs[index - 1]


# TODO, this is broken...
class AddTextWordByWord(Succession):
    """Show a :class:`~.Text` word by word on the scene."""

    def __init__(
        self,
        text_mobject: "Text",
        run_time: float = None,
        time_per_char: float = 0.06,
        **kwargs
    ) -> None:
        self.time_per_char = time_per_char
        tpc = self.time_per_char
        anims = it.chain(
            *[
                [
                    ShowIncreasingSubsets(word, run_time=tpc * len(word)),
                    Animation(word, run_time=0.005 * len(word) ** 1.5),
                ]
                for word in text_mobject
            ]
        )
        super().__init__(*anims, **kwargs)
