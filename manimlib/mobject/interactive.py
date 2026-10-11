from __future__ import annotations

import numpy as np

from manimlib.constants import FRAME_HEIGHT, FRAME_WIDTH
from manimlib.constants import DOWN, LEFT, ORIGIN, RIGHT, UP
from manimlib.constants import MED_LARGE_BUFF, MED_SMALL_BUFF, SMALL_BUFF
from manimlib.constants import BLACK, BLUE, GREEN, GREY_A, GREY_C, RED, WHITE, DEFAULT_MOBJECT_COLOR
from manimlib.event_keys import Keys
from manimlib.event_keys import Mods
from manimlib.mobject.mobject import Group
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.geometry import Circle
from manimlib.mobject.geometry import Dot
from manimlib.mobject.geometry import Line
from manimlib.mobject.geometry import Rectangle
from manimlib.mobject.geometry import RoundedRectangle
from manimlib.mobject.geometry import Square
from manimlib.mobject.svg.text_mobject import Text
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.value_tracker import ValueTracker
from manimlib.utils.color import rgb_to_hex
from manimlib.utils.space_ops import get_closest_point_on_line
from manimlib.utils.space_ops import get_norm

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable
    from manimlib.typing import ManimColor


# Interactive Mobjects

class MotionMobject(Mobject):
    """
    Wrap a Mobject to make it draggable with the mouse.

    MotionMobject allows a user to interactively reposition a Mobject by
    clicking and dragging it in the scene. It registers a mouse-drag
    listener on the wrapped object and moves that object to the position
    provided by the drag event.

    The wrapped Mobject receives a no-op updater to help prevent it from
    being treated as a static object.

    Parameters
    ----------
    mobject : Mobject
        The object that should be draggable. The object is added as a
        submobject of the MotionMobject.

    **kwargs
        Additional keyword arguments forwarded to :class:`Mobject`.

    Attributes
    ----------
    mobject : Mobject
        The wrapped object that responds to mouse-drag events.

    Methods
    -------
    mob_on_mouse_drag(mob, event_data)
        Moves the dragged object to the point specified by the event data.

    Examples
    --------
    Make a circle draggable::

        circle = Circle()
        draggable_circle = MotionMobject(circle)
        self.add(draggable_circle)

    Make a text label draggable::

        label = Text("Drag me")
        draggable_label = MotionMobject(label)
        self.add(draggable_label)

    Wrap an existing object without creating a copy::

        square = Square()
        draggable_square = MotionMobject(square)
        self.add(draggable_square)

    Notes
    -----
    - The constructor checks that ``mobject`` is an instance of
      :class:`Mobject`; otherwise, an ``AssertionError`` is raised.
    - The mouse-drag listener is registered on the wrapped object through
      ``add_mouse_drag_listner``.
    - During dragging, ``event_data["point"]`` provides the target position.
    - The callback moves the object using ``mob.move_to(...)`` and returns
      ``False``.
    - The wrapped object is added directly as a submobject, so this wrapper
      does not create an independent copy of it.
    - The no-op updater is attached to the wrapped object to help avoid
      locking it as a static Mobject.
    - Interactive dragging requires a rendering or preview environment
      that supports mouse events.

    See Also
    --------
    Mobject
        Base class for objects in the scene.
    """

    def __init__(self, mobject: Mobject, **kwargs):
        super().__init__(**kwargs)
        assert isinstance(mobject, Mobject)
        self.mobject = mobject
        self.mobject.add_mouse_drag_listner(self.mob_on_mouse_drag)
        # To avoid locking it as static mobject
        self.mobject.add_updater(lambda mob: None)
        self.add(mobject)

    def mob_on_mouse_drag(self, mob: Mobject, event_data: dict[str, np.ndarray]) -> bool:
        mob.move_to(event_data["point"])
        return False


class Button(Mobject):
    """
    Wrap a Mobject and execute a callback when it receives a mouse-press event.

    Button provides a simple way to make an existing Mobject behave like an
    interactive button. It registers a mouse-press listener on the supplied
    Mobject and calls the user-defined ``on_click`` callback when the event
    is dispatched to that object.

    The callback receives the Mobject associated with the mouse-press event,
    similar to how a Mobject updater receives the object it updates.

    Event Handling
    --------------
    The event system follows an event-bubbling model inspired by the DOM
    event model in JavaScript. Mouse and keyboard events are dispatched
    through the event system, and listeners can return ``False`` to stop
    the event from bubbling further.

    Button's internal mouse-press handler calls ``on_click(mob)`` and then
    returns ``False``. This prevents the mouse-press event from continuing
    to bubble beyond this handler according to the event system's
    dispatching rules.

    Parameters
    ----------
    mobject : Mobject
        The visual object that acts as the button. A mouse-press listener
        is registered on this object, which is then added as a submobject
        of the Button.

    on_click : Callable[[Mobject], Any]
        The callback to execute when the button receives a mouse-press
        event. It must accept one argument: the Mobject passed to the
        internal event handler. The callback's return value is not used
        by Button.

    **kwargs
        Additional keyword arguments forwarded to :class:`Mobject`.

    Attributes
    ----------
    on_click : Callable
        The user-provided callback invoked by the mouse-press handler.

    mobject : Mobject
        The visual object wrapped by the Button.

    Methods
    -------
    mob_on_mouse_press(mob, event_data)
        Handles the mouse-press event by invoking ``on_click(mob)`` and
        returning ``False`` to stop further event bubbling.

    Examples
    --------
    Create a button that prints a message when clicked::

        def handle_click(mob):
            print("Button clicked!")

        visual = Square()
        button = Button(visual, on_click=handle_click)
        self.add(button)

    Change an object's color when clicked::

        def change_color(mob):
            mob.set_color(RED)

        square = Square()
        button = Button(square, on_click=change_color)
        self.add(button)

    Use a text object as a button::

        def handle_click(mob):
            print("Selected:", mob)

        label = Text("Click me")
        button = Button(label, on_click=handle_click)
        self.add(button)

    Modify the scene from a callback::

        def enlarge(mob):
            mob.scale(1.2)

        circle = Circle()
        button = Button(circle, on_click=enlarge)
        self.add(button)

    Notes
    -----
    - ``mobject`` must be an instance of :class:`Mobject`; otherwise, the
      constructor raises an ``AssertionError``.
    - The supplied Mobject is used directly rather than copied.
    - The callback receives one argument, the event-associated Mobject.
      It does not receive ``event_data`` through the Button callback.
    - The internal handler accepts ``event_data`` because it follows the
      event-listener callback interface, but does not use it.
    - The mouse-press listener is registered through
      ``add_mouse_press_listner``.
    - Button does not itself perform hit-testing, draw a button background,
      or define hover, pressed, or released visual states. Those behaviors
      depend on the event system and any additional code.
    - The interaction requires a rendering or preview environment that
      dispatches mouse events.
    - The event system also exposes listeners for mouse motion, press,
      release, drag, scroll, and keyboard press and release events.
      These can be registered or removed using the corresponding
      Mobject listener methods.

    See Also
    --------
    Mobject
        Base class for scene objects and event-listener registration.
    MotionMobject
        Wraps a Mobject to make it draggable using mouse-drag events.

    References
    ----------
    Event bubbling in the DOM event model:
    https://www.quirksmode.org/js/events_order.html
    """

    def __init__(self, mobject: Mobject, on_click: Callable[[Mobject]], **kwargs):
        super().__init__(**kwargs)
        assert isinstance(mobject, Mobject)
        self.on_click = on_click
        self.mobject = mobject
        self.mobject.add_mouse_press_listner(self.mob_on_mouse_press)
        self.add(self.mobject)

    def mob_on_mouse_press(self, mob: Mobject, event_data) -> bool:
        self.on_click(mob)
        return False


# Controls

class ControlMobject(ValueTracker):
    """
    A ValueTracker-based base class for interactive controls in a scene.

    ControlMobject extends ValueTracker with support for attaching visual
    Mobjects and defining custom behavior when its value changes. It is
    intended to be subclassed to implement controls that validate a new
    value and animate the visual representation of that value.

    The control is fixed in the camera frame and receives a no-op updater
    to help prevent its data from being locked as static while waiting
    in a scene.

    Parameters
    ----------
    value : float
        The initial value stored by the ValueTracker.

    *mobjects : Mobject
        Zero or more Mobjects to attach to the control. These can represent
        the control's visual components.

    **kwargs
        Additional keyword arguments forwarded to :class:`ValueTracker`.

    Attributes
    ----------
    Inherited from ValueTracker
        The tracked numeric value and the methods used to access or update it.

    Methods
    -------
    set_value(value)
        Validates the requested value, invokes the animation hook, and then
        updates the underlying ValueTracker value.

    assert_value(value)
        Validation hook for subclasses. The base implementation does nothing.

    set_value_anim(value)
        Animation hook for subclasses. The base implementation does nothing.

    Examples
    --------
    Create a basic control with an initial value::

        control = ControlMobject(0.5)

    Attach visual objects to a control::

        track = Line(LEFT, RIGHT)
        marker = Dot()

        control = ControlMobject(0.5, track, marker)
        self.add(control)

    Subclass ControlMobject to validate values and define custom animation::

        class BoundedControl(ControlMobject):
            def assert_value(self, value):
                assert 0 <= value <= 1, "Value must be between 0 and 1"

            def set_value_anim(self, value):
                # Implement the visual update or animation here.
                pass

        control = BoundedControl(0.5)

    Notes
    -----
    - ``ControlMobject`` is a base class intended for extension. Its
      ``assert_value`` and ``set_value_anim`` methods are placeholders and
      do not implement validation or animation by themselves.
    - ``set_value`` calls ``assert_value(value)`` first, followed by
      ``set_value_anim(value)``, and then delegates the actual value update
      to ``ValueTracker.set_value(self, value)``.
    - If validation raises an exception, the animation hook and underlying
      value update are not reached.
    - Subclasses should implement ``assert_value`` to enforce valid input
      and ``set_value_anim`` to update or animate their visual components.
    - The constructor attaches the supplied Mobjects as submobjects.
    - The no-op updater is added to help avoid static-mobject data locking.
    - ``fix_in_frame()`` keeps the control fixed relative to the camera
      frame rather than behaving like an ordinary world-space object.
    - The class does not define a particular visual appearance or input
      mechanism. Subclasses must provide the behavior appropriate to
      their intended control.

    See Also
    --------
    ValueTracker
        Stores a numeric value that can be accessed and updated.
    Mobject
        Base class for visual objects in a scene.
    """

    def __init__(self, value: float, *mobjects: Mobject, **kwargs):
        super().__init__(value=value, **kwargs)
        self.add(*mobjects)

        # To avoid lock_static_mobject_data while waiting in scene
        self.add_updater(lambda mob: None)
        self.fix_in_frame()

    def set_value(self, value: float):
        self.assert_value(value)
        self.set_value_anim(value)
        return ValueTracker.set_value(self, value)

    def assert_value(self, value):
        # To be implemented in subclasses
        pass

    def set_value_anim(self, value):
        # To be implemented in subclasses
        pass


class EnableDisableButton(ControlMobject):
    """
    A clickable Boolean control that switches between enabled and disabled states.

    EnableDisableButton is a ControlMobject subclass that represents a Boolean
    value using a colored rectangle. It registers a mouse-press listener so
    that clicking the control toggles its state.

    When enabled, the rectangle uses ``enable_color``; when disabled, it uses
    ``disable_color``. The current value is stored through the inherited
    ValueTracker interface.

    Parameters
    ----------
    value : bool, default=True
        Initial state of the control. ``True`` represents enabled, and
        ``False`` represents disabled.

    value_type : np.dtype, default=np.dtype(bool)
        NumPy data type associated with the control's value. The constructor
        stores this parameter, but the shown implementation does not use it
        to convert or validate values.

    rect_kwargs : dict, default={"width": 0.5, "height": 0.5, "fill_opacity": 1.0}
        Keyword arguments passed to Rectangle to configure the control's
        visual appearance.

    enable_color : ManimColor, default=GREEN
        Fill color used when the control is enabled.

    disable_color : ManimColor, default=RED
        Fill color used when the control is disabled.

    **kwargs
        Additional keyword arguments forwarded to ControlMobject.

    Attributes
    ----------
    value : bool
        Stores the initial value supplied to the constructor. In this
        implementation, this attribute is not automatically updated when
        the inherited ValueTracker value changes.

    value_type : np.dtype
        The stored NumPy data type parameter.

    rect_kwargs : dict
        Configuration passed to the Rectangle constructor.

    enable_color : ManimColor
        Color used for the enabled state.

    disable_color : ManimColor
        Color used for the disabled state.

    box : Rectangle
        Rectangle that visually represents the control's current state.

    Methods
    -------
    assert_value(value)
        Checks that the supplied value is a Python bool.

    set_value_anim(value)
        Updates the rectangle's fill color to reflect the requested state.

    toggle_value()
        Switches the tracked value between True and False.

    on_mouse_press(mob, event_data)
        Toggles the control when a mouse-press event is received.

    Examples
    --------
    Create an enabled control::

        control = EnableDisableButton()
        self.add(control)

    Create a control that starts disabled::

        control = EnableDisableButton(value=False)
        self.add(control)

    Customize the enabled and disabled colors::

        control = EnableDisableButton(
            value=True,
            enable_color=BLUE,
            disable_color=GRAY,
        )
        self.add(control)

    Toggle the state programmatically::

        control = EnableDisableButton(value=True)
        control.toggle_value()

        print(control.get_value())  # False

    Set the state explicitly::

        control = EnableDisableButton()
        control.set_value(False)

    Notes
    -----
    - The control creates a Rectangle using ``rect_kwargs`` and passes it
      to the ControlMobject constructor as a visual submobject.
    - ``assert_value`` uses ``isinstance(value, bool)``. Values such as
      ``1`` and ``np.bool_(True)`` are not accepted by this check.
    - ``set_value_anim`` changes the rectangle's fill color immediately;
      it does not define a time-based animation.
    - ``toggle_value`` obtains the current tracked value, negates it, and
      calls the parent class's ``set_value`` method. This invokes the
      validation and visual-update hooks before updating the ValueTracker.
    - A mouse press invokes ``toggle_value`` and returns ``False`` from
      the event callback to stop further event bubbling according to the
      event system's dispatch rules.
    - The constructor stores the initial value in ``self.value`` before
      initializing the parent class. Subsequent changes update the inherited
      tracked value; the separate ``self.value`` attribute is not explicitly
      synchronized by the shown methods.
    - ``value_type`` is stored for possible use by subclasses or other code,
      but it does not perform type conversion in this implementation.
    - Interactive clicking requires an environment that dispatches mouse
      events to Mobjects.

    See Also
    --------
    ControlMobject
        Base class for value-based visual controls.
    Button
        Wraps a Mobject and invokes a callback on mouse press.
    ValueTracker
        Stores a value that can be read and updated.
    """

    def __init__(
        self,
        value: bool = True,
        value_type: np.dtype = np.dtype(bool),
        rect_kwargs: dict = {
            "width": 0.5,
            "height": 0.5,
            "fill_opacity": 1.0
        },
        enable_color: ManimColor = GREEN,
        disable_color: ManimColor = RED,
        **kwargs
    ):
        self.value = value
        self.value_type = value_type
        self.rect_kwargs = rect_kwargs
        self.enable_color = enable_color
        self.disable_color = disable_color

        self.box = Rectangle(**self.rect_kwargs)
        super().__init__(value, self.box, **kwargs)
        self.add_mouse_press_listner(self.on_mouse_press)

    def assert_value(self, value: bool) -> None:
        assert isinstance(value, bool)

    def set_value_anim(self, value: bool) -> None:
        if value:
            self.box.set_fill(self.enable_color)
        else:
            self.box.set_fill(self.disable_color)

    def toggle_value(self) -> None:
        super().set_value(not self.get_value())

    def on_mouse_press(self, mob: Mobject, event_data) -> bool:
        mob.toggle_value()
        return False


class Checkbox(ControlMobject):
    """
    A clickable Boolean control that displays a checkmark or a cross.

    Checkbox is a ControlMobject subclass that represents a Boolean value
    using a rectangular outline and an overlaid symbol. When the value is
    True, a checkmark is displayed; when the value is False, a cross is
    displayed.

    The control registers a mouse-press listener so that clicking it toggles
    its value and replaces the displayed symbol accordingly.

    Parameters
    ----------
    value : bool, default=True
        Initial Boolean state. True displays a checkmark, while False
        displays a cross.

    value_type : np.dtype, default=np.dtype(bool)
        NumPy data type associated with the control's value. This parameter
        is stored but is not used for conversion in the current implementation.

    rect_kwargs : dict, default={"width": 0.5, "height": 0.5, "fill_opacity": 0.0}
        Keyword arguments passed to Rectangle to configure the checkbox outline.

    checkmark_kwargs : dict, default={"stroke_color": GREEN, "stroke_width": 6}
        Keyword arguments passed to the Line objects that form the checkmark.

    cross_kwargs : dict, default={"stroke_color": RED, "stroke_width": 6}
        Keyword arguments passed to the Line objects that form the cross.

    box_content_buff : float, default=SMALL_BUFF
        Buffer value stored by the checkbox. It is not used by the shown
        implementation to position or size the symbols.

    **kwargs
        Additional keyword arguments forwarded to ControlMobject.

    Attributes
    ----------
    value_type : np.dtype
        Stored NumPy data type parameter.

    rect_kwargs : dict
        Configuration used to construct the rectangular outline.

    checkmark_kwargs : dict
        Styling configuration for the checkmark lines.

    cross_kwargs : dict
        Styling configuration for the cross lines.

    box_content_buff : float
        Stored buffer parameter.

    box : Rectangle
        Rectangular outline surrounding the checkbox symbol.

    box_content : VGroup
        Group of Line objects representing the currently displayed
        checkmark or cross.

    Methods
    -------
    assert_value(value)
        Checks that the supplied value is a Python bool.

    toggle_value()
        Toggles the tracked value between True and False.

    set_value_anim(value)
        Replaces the current symbol with a checkmark or cross to reflect
        the requested value.

    on_mouse_press(mob, event_data)
        Toggles the checkbox when it receives a mouse-press event.

    get_checkmark()
        Constructs and returns the checkmark as a VGroup.

    get_cross()
        Constructs and returns the cross as a VGroup.

    Examples
    --------
    Create a checkbox that starts checked::

        checkbox = Checkbox()
        self.add(checkbox)

    Create a checkbox that starts unchecked::

        checkbox = Checkbox(value=False)
        self.add(checkbox)

    Customize the symbol colors and stroke widths::

        checkbox = Checkbox(
            value=True,
            checkmark_kwargs={
                "stroke_color": GREEN,
                "stroke_width": 8,
            },
            cross_kwargs={
                "stroke_color": RED,
                "stroke_width": 8,
            },
        )
        self.add(checkbox)

    Toggle the checkbox programmatically::

        checkbox = Checkbox(value=True)
        checkbox.toggle_value()

        print(checkbox.get_value())  # False

    Set the state explicitly::

        checkbox = Checkbox()
        checkbox.set_value(False)

    Notes
    -----
    - The constructor creates the outline and initializes the symbol based
      on the supplied initial value.
    - The outline and symbol are added to the control through the
      ControlMobject constructor.
    - The checkmark consists of two Line objects grouped into a VGroup.
      The cross also consists of two Line objects grouped into a VGroup.
    - Both symbols are stretched to the outline's width and height, scaled
      by 0.5, and moved to the center of the outline.
    - When the value changes, set_value_anim uses ``become`` to replace
      the existing symbol's geometry with the newly constructed symbol.
      The existing box_content object is retained as the control's submobject.
    - The symbol update is immediate; this method does not itself create
      a time-based animation.
    - The value validator uses ``isinstance(value, bool)``. Integers such
      as 0 and 1, as well as NumPy Boolean scalars, do not pass this check.
    - The ``value_type`` and ``box_content_buff`` parameters are stored,
      but neither affects behavior in the shown implementation.
    - A mouse press calls toggle_value and returns False from the event
      callback to stop further event bubbling according to the event
      dispatcher's rules.
    - Interactive clicking requires an environment that dispatches mouse
      events to Mobjects.

    See Also
    --------
    ControlMobject
        Base class for value-based visual controls.
    EnableDisableButton
        A Boolean control that indicates its state using fill colors.
    Button
        Wraps a Mobject and invokes a callback on mouse press.
    """

    def __init__(
        self,
        value: bool = True,
        value_type: np.dtype = np.dtype(bool),
        rect_kwargs: dict = {
            "width": 0.5,
            "height": 0.5,
            "fill_opacity": 0.0
        },
        checkmark_kwargs: dict = {
            "stroke_color": GREEN,
            "stroke_width": 6,
        },
        cross_kwargs: dict = {
            "stroke_color": RED,
            "stroke_width": 6,
        },
        box_content_buff: float = SMALL_BUFF,
        **kwargs
    ):
        self.value_type = value_type
        self.rect_kwargs = rect_kwargs
        self.checkmark_kwargs = checkmark_kwargs
        self.cross_kwargs = cross_kwargs
        self.box_content_buff = box_content_buff

        self.box = Rectangle(**self.rect_kwargs)
        self.box_content = self.get_checkmark() if value else self.get_cross()
        super().__init__(value, self.box, self.box_content, **kwargs)
        self.add_mouse_press_listner(self.on_mouse_press)

    def assert_value(self, value: bool) -> None:
        assert isinstance(value, bool)

    def toggle_value(self) -> None:
        super().set_value(not self.get_value())

    def set_value_anim(self, value: bool) -> None:
        if value:
            self.box_content.become(self.get_checkmark())
        else:
            self.box_content.become(self.get_cross())

    def on_mouse_press(self, mob: Mobject, event_data) -> None:
        mob.toggle_value()
        return False

    # Helper methods

    def get_checkmark(self) -> VGroup:
        checkmark = VGroup(
            Line(UP / 2 + 2 * LEFT, DOWN + LEFT, **self.checkmark_kwargs),
            Line(DOWN + LEFT, UP + RIGHT, **self.checkmark_kwargs)
        )

        checkmark.stretch_to_fit_width(self.box.get_width())
        checkmark.stretch_to_fit_height(self.box.get_height())
        checkmark.scale(0.5)
        checkmark.move_to(self.box)
        return checkmark

    def get_cross(self) -> VGroup:
        cross = VGroup(
            Line(UP + LEFT, DOWN + RIGHT, **self.cross_kwargs),
            Line(UP + RIGHT, DOWN + LEFT, **self.cross_kwargs)
        )

        cross.stretch_to_fit_width(self.box.get_width())
        cross.stretch_to_fit_height(self.box.get_height())
        cross.scale(0.5)
        cross.move_to(self.box)
        return cross


class LinearNumberSlider(ControlMobject):
    """
    A draggable slider for selecting a numeric value within a bounded interval.

    LinearNumberSlider is a ControlMobject subclass that represents a
    number using a horizontal bar and a draggable circular handle. Dragging
    the handle updates the control's value according to its position along
    the slider axis.

    The slider maps positions on the axis linearly to values between
    ``min_value`` and ``max_value``. Values obtained from dragging are
    quantized to increments of ``step`` measured from ``min_value``.

    Parameters
    ----------
    value : float, default=0
        Initial numeric value. It must lie between ``min_value`` and
        ``max_value``, inclusive.

    value_type : type, default=np.float64
        Numeric type associated with the value. This parameter is stored
        but is not used to cast values in the shown implementation.

    min_value : float, default=-10.0
        Minimum permitted value and the value mapped to the left endpoint
        of the slider axis.

    max_value : float, default=10.0
        Maximum permitted value and the value mapped to the right endpoint
        of the slider axis.

    step : float, default=1.0
        Increment used to quantize values obtained from dragging. The
        quantization is calculated relative to ``min_value``.

    rounded_rect_kwargs : dict, default={"height": 0.075, "width": 2, "corner_radius": 0.0375}
        Keyword arguments passed to RoundedRectangle to configure the
        slider bar.

    circle_kwargs : dict, default={"radius": 0.1, "stroke_color": GREY_A, "fill_color": GREY_A, "fill_opacity": 1.0}
        Keyword arguments passed to Circle to configure the draggable handle.

    **kwargs
        Additional keyword arguments forwarded to ControlMobject.

    Attributes
    ----------
    value_type : type
        Stored numeric type parameter.

    min_value : float
        Lower bound of the slider's numeric range.

    max_value : float
        Upper bound of the slider's numeric range.

    step : float
        Increment used when quantizing values obtained from dragging.

    rounded_rect_kwargs : dict
        Configuration used to construct the slider bar.

    circle_kwargs : dict
        Configuration used to construct the circular handle.

    bar : RoundedRectangle
        Visible horizontal bar representing the slider.

    slider : Circle
        Draggable circular handle indicating the current value.

    slider_axis : Line
        Invisible line defining the slider's movement axis and endpoints.

    Methods
    -------
    assert_value(value)
        Raises an AssertionError if the value lies outside the permitted
        interval.

    set_value_anim(value)
        Moves the circular handle to the position corresponding to the
        supplied value.

    slider_on_mouse_drag(mob, event_data)
        Converts the drag position into a numeric value and updates the
        slider.

    get_value_from_point(point)
        Projects a point onto the slider axis and returns the corresponding
        value quantized to the nearest lower step relative to min_value.

    Examples
    --------
    Create a slider with the default range::

        slider = LinearNumberSlider()
        self.add(slider)

    Create a slider with a custom range and step size::

        slider = LinearNumberSlider(
            value=25,
            min_value=0,
            max_value=100,
            step=5,
        )
        self.add(slider)

    Customize the bar and handle appearance::

        slider = LinearNumberSlider(
            value=0,
            min_value=-5,
            max_value=5,
            step=0.5,
            rounded_rect_kwargs={
                "width": 4,
                "height": 0.1,
                "corner_radius": 0.05,
            },
            circle_kwargs={
                "radius": 0.12,
                "fill_color": BLUE,
                "stroke_color": WHITE,
                "fill_opacity": 1,
            },
        )
        self.add(slider)

    Set the value programmatically::

        slider = LinearNumberSlider(
            value=0,
            min_value=-10,
            max_value=10,
            step=1,
        )
        slider.set_value(5)

        print(slider.get_value())  # 5

    Notes
    -----
    - The constructor creates a RoundedRectangle as the visible bar and a
      Circle as the draggable handle.
    - The slider axis is a Line connecting the left and right bounding-box
      points of the bar. Its opacity is set to zero, making it invisible.
    - The handle is initially moved to the axis line before the parent
      constructor initializes the ControlMobject.
    - A mouse-drag listener is registered on the circular handle.
    - The value-to-position mapping is linear:

      .. math::

          p = \frac{v - v_{\min}}{v_{\max} - v_{\min}}

      where ``p`` is the proportion along the axis and ``v`` is the value.

    - During dragging, the pointer is projected onto the slider axis using
      ``get_closest_point_on_line``. The distance ratio along the axis is
      then converted to a value and quantized using ``step``.
    - The quantization formula is equivalent to taking the lower step
      relative to ``min_value``; it does not round to the mathematically
      nearest step.
    - ``assert_value`` checks only the bounds. It does not validate that
      ``step`` is positive or that the bounds differ.
    - A positive ``step`` is expected. A zero step causes division by zero,
      while a negative step does not provide the intended increment behavior.
    - ``max_value`` should differ from ``min_value`` because the mapping
      divides by their difference.
    - The initial value is validated by the inherited ControlMobject
      initialization only if that initialization invokes the subclass
      validation hook.
    - ``value_type`` is stored but does not automatically convert the
      control's value to the requested type.

    See Also
    --------
    ControlMobject
        Base class for value-based visual controls.
    ValueTracker
        Stores a numeric value that can be read and updated.
    EnableDisableButton
        A Boolean control represented by a colored rectangle.
    """

    def __init__(
        self,
        value: float = 0,
        value_type: type = np.float64,
        min_value: float = -10.0,
        max_value: float = 10.0,
        step: float = 1.0,
        rounded_rect_kwargs: dict = {
            "height": 0.075,
            "width": 2,
            "corner_radius": 0.0375
        },
        circle_kwargs: dict = {
            "radius": 0.1,
            "stroke_color": GREY_A,
            "fill_color": GREY_A,
            "fill_opacity": 1.0
        },
        **kwargs
    ):
        self.value_type = value_type
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.rounded_rect_kwargs = rounded_rect_kwargs
        self.circle_kwargs = circle_kwargs

        self.bar = RoundedRectangle(**self.rounded_rect_kwargs)
        self.slider = Circle(**self.circle_kwargs)
        self.slider_axis = Line(
            start=self.bar.get_bounding_box_point(LEFT),
            end=self.bar.get_bounding_box_point(RIGHT)
        )
        self.slider_axis.set_opacity(0.0)
        self.slider.move_to(self.slider_axis)

        self.slider.add_mouse_drag_listner(self.slider_on_mouse_drag)

        super().__init__(value, self.bar, self.slider, self.slider_axis, **kwargs)

    def assert_value(self, value: float) -> None:
        assert self.min_value <= value <= self.max_value

    def set_value_anim(self, value: float) -> None:
        prop = (value - self.min_value) / (self.max_value - self.min_value)
        self.slider.move_to(self.slider_axis.point_from_proportion(prop))

    def slider_on_mouse_drag(self, mob, event_data: dict[str, np.ndarray]) -> bool:
        self.set_value(self.get_value_from_point(event_data["point"]))
        return False

    # Helper Methods

    def get_value_from_point(self, point: np.ndarray) -> float:
        start, end = self.slider_axis.get_start_and_end()
        point_on_line = get_closest_point_on_line(start, end, point)
        prop = get_norm(point_on_line - start) / get_norm(end - start)
        value = self.min_value + prop * (self.max_value - self.min_value)
        no_of_steps = int((value - self.min_value) / self.step)
        value_nearest_to_step = self.min_value + no_of_steps * self.step
        return value_nearest_to_step


class ColorSliders(Group):
    """
    An interactive color picker built from RGB and alpha sliders.

    ColorSliders combines four LinearNumberSlider controls to select the
    red, green, blue, and alpha components of a color. The RGB sliders use
    integer values from 0 to 255, while the alpha slider uses values from
    0 to 1.

    A preview rectangle displays the selected color and opacity. A
    checkerboard background is placed behind the preview to make
    transparency easier to distinguish from opaque colors.

    Parameters
    ----------
    sliders_kwargs : dict, default={}
        Additional keyword arguments passed to each LinearNumberSlider.
        The component-specific values for ``value``, ``min_value``,
        ``max_value``, and ``step`` are supplied internally. Avoid passing
        duplicate keys through this dictionary.

    rect_kwargs : dict, default={"width": 2.0, "height": 0.5, "stroke_opacity": 1.0}
        Keyword arguments passed to the Rectangle used for the color preview.
        The same dimensions are used to construct the checkerboard background.

    background_grid_kwargs : dict, default={"colors": [GREY_A, GREY_C], "single_square_len": 0.1}
        Configuration for the checkerboard background. ``colors`` supplies
        the alternating square colors, and ``single_square_len`` determines
        the approximate size of each square.

    sliders_buff : float, default=MED_LARGE_BUFF
        Vertical spacing between the four sliders.

    default_rgb_value : int, default=255
        Initial value for each RGB slider. The default of 255 initializes
        the preview to white.

    default_a_value : int, default=1
        Initial value for the alpha slider. The default of 1 represents
        full opacity.

    **kwargs
        Additional keyword arguments forwarded to Group.

    Attributes
    ----------
    sliders_kwargs : dict
        Configuration passed to each LinearNumberSlider.

    rect_kwargs : dict
        Configuration for the selected-color preview rectangle.

    background_grid_kwargs : dict
        Configuration for the checkerboard background.

    sliders_buff : float
        Vertical spacing between sliders.

    default_rgb_value : int
        Initial value assigned to the red, green, and blue sliders.

    default_a_value : int
        Initial value assigned to the alpha slider.

    r_slider : LinearNumberSlider
        Slider controlling the red component, with a range of 0 to 255
        and a step of 1.

    g_slider : LinearNumberSlider
        Slider controlling the green component, with a range of 0 to 255
        and a step of 1.

    b_slider : LinearNumberSlider
        Slider controlling the blue component, with a range of 0 to 255
        and a step of 1.

    a_slider : LinearNumberSlider
        Slider controlling opacity, with a range of 0 to 1 and a step of 0.04.

    sliders : Group
        Group containing the four sliders, arranged vertically.

    selected_color_box : Rectangle
        Preview rectangle whose fill color and opacity are updated from
        the current slider values.

    background : VGroup
        Checkerboard grid behind the color preview.

    Methods
    -------
    get_background()
        Constructs and returns the checkerboard background.

    set_value(r, g, b, a)
        Sets all four slider values.

    get_value()
        Returns an array containing normalized red, green, blue, and alpha
        components.

    get_picked_color()
        Returns the selected RGB color as a hexadecimal string.

    get_picked_opacity()
        Returns the selected alpha value as a float.

    Examples
    --------
    Create a color picker with its default settings::

        color_picker = ColorSliders()
        self.add(color_picker)

    Set the selected color to red with full opacity::

        color_picker = ColorSliders()
        color_picker.set_value(255, 0, 0, 1)
        self.add(color_picker)

    Set a semi-transparent purple color::

        color_picker = ColorSliders()
        color_picker.set_value(128, 0, 255, 0.5)

        hex_color = color_picker.get_picked_color()
        opacity = color_picker.get_picked_opacity()

        print(hex_color)
        print(opacity)

    Read the normalized RGBA components::

        color_picker = ColorSliders()
        color_picker.set_value(255, 128, 0, 1)

        rgba = color_picker.get_value()
        # Array containing normalized red, green, blue, and alpha values.

    Customize the preview dimensions and slider spacing::

        color_picker = ColorSliders(
            rect_kwargs={
                "width": 3.0,
                "height": 0.75,
                "stroke_opacity": 1.0,
            },
            sliders_buff=0.5,
        )
        self.add(color_picker)

    Notes
    -----
    - The red, green, and blue sliders each use a range of 0 to 255 with
      an increment of 1. The alpha slider uses a range of 0 to 1 with an
      increment of 0.04.
    - Each slider handle is colored to identify its component: red, green,
      blue, or a black-to-white gradient for alpha.
    - The preview rectangle has an updater that calls ``get_picked_color``
      and ``get_picked_opacity`` to refresh its fill color and opacity.
    - The checkerboard is generated using Square objects arranged into a
      grid. Its squares alternate through the supplied ``colors`` sequence.
    - The grid dimensions are calculated from the preview dimensions and
      ``single_square_len``. The number of columns is increased by one when
      it is even, producing an odd number of columns.
    - ``get_value`` divides the RGB components by 255 and leaves alpha
      unchanged, returning an array in the order ``(r, g, b, a)``.
    - ``get_picked_color`` converts the normalized RGB components to a
      hexadecimal string using ``rgb_to_hex``. Alpha is handled separately
      by ``get_picked_opacity``.
    - ``set_value`` updates each slider sequentially. Each component must
      satisfy the corresponding slider's allowed range.
    - The preview and checkerboard group is fixed in the camera frame
      before the complete group is arranged vertically with the sliders.
    - The alpha slider's default step of 0.04 does not divide the interval
      from 0 to 1 into an integer number of equal steps. The exact reachable
      values depend on the slider's quantization logic.
    - The shown return annotation ``np.ndarary`` appears to be a typo;
      the method actually returns a NumPy array, so ``np.ndarray`` would
      be the appropriate annotation.

    See Also
    --------
    LinearNumberSlider
        Draggable numeric slider used to select each color component.
    Group
        Groups multiple Mobjects into a single composite object.
    rgb_to_hex
        Converts RGB components into a hexadecimal color representation.
    """

    def __init__(
        self,
        sliders_kwargs: dict = {},
        rect_kwargs: dict = {
            "width": 2.0,
            "height": 0.5,
            "stroke_opacity": 1.0
        },
        background_grid_kwargs: dict = {
            "colors": [GREY_A, GREY_C],
            "single_square_len": 0.1
        },
        sliders_buff: float = MED_LARGE_BUFF,
        default_rgb_value: int = 255,
        default_a_value: int = 1,
        **kwargs
    ):
        self.sliders_kwargs = sliders_kwargs
        self.rect_kwargs = rect_kwargs
        self.background_grid_kwargs = background_grid_kwargs
        self.sliders_buff = sliders_buff
        self.default_rgb_value = default_rgb_value
        self.default_a_value = default_a_value

        rgb_kwargs = {"value": self.default_rgb_value, "min_value": 0, "max_value": 255, "step": 1}
        a_kwargs = {"value": self.default_a_value, "min_value": 0, "max_value": 1, "step": 0.04}

        self.r_slider = LinearNumberSlider(**self.sliders_kwargs, **rgb_kwargs)
        self.g_slider = LinearNumberSlider(**self.sliders_kwargs, **rgb_kwargs)
        self.b_slider = LinearNumberSlider(**self.sliders_kwargs, **rgb_kwargs)
        self.a_slider = LinearNumberSlider(**self.sliders_kwargs, **a_kwargs)
        self.sliders = Group(
            self.r_slider,
            self.g_slider,
            self.b_slider,
            self.a_slider
        )
        self.sliders.arrange(DOWN, buff=self.sliders_buff)

        self.r_slider.slider.set_color(RED)
        self.g_slider.slider.set_color(GREEN)
        self.b_slider.slider.set_color(BLUE)
        self.a_slider.slider.set_color_by_gradient(BLACK, WHITE)

        self.selected_color_box = Rectangle(**self.rect_kwargs)
        self.selected_color_box.add_updater(
            lambda mob: mob.set_fill(
                self.get_picked_color(), self.get_picked_opacity()
            )
        )
        self.background = self.get_background()

        super().__init__(
            Group(self.background, self.selected_color_box).fix_in_frame(),
            self.sliders,
            **kwargs
        )

        self.arrange(DOWN)

    def get_background(self) -> VGroup:
        single_square_len = self.background_grid_kwargs["single_square_len"]
        colors = self.background_grid_kwargs["colors"]
        width = self.rect_kwargs["width"]
        height = self.rect_kwargs["height"]
        rows = int(height / single_square_len)
        cols = int(width / single_square_len)
        cols = (cols + 1) if (cols % 2 == 0) else cols

        single_square = Square(single_square_len)
        grid = single_square.get_grid(n_rows=rows, n_cols=cols, buff=0.0)
        grid.stretch_to_fit_width(width)
        grid.stretch_to_fit_height(height)
        grid.move_to(self.selected_color_box)

        for idx, square in enumerate(grid):
            assert isinstance(square, Square)
            square.set_stroke(width=0.0, opacity=0.0)
            square.set_fill(colors[idx % len(colors)], 1.0)

        return grid

    def set_value(self, r: float, g: float, b: float, a: float):
        self.r_slider.set_value(r)
        self.g_slider.set_value(g)
        self.b_slider.set_value(b)
        self.a_slider.set_value(a)

    def get_value(self) -> np.ndarary:
        r = self.r_slider.get_value() / 255
        g = self.g_slider.get_value() / 255
        b = self.b_slider.get_value() / 255
        alpha = self.a_slider.get_value()
        return np.array((r, g, b, alpha))

    def get_picked_color(self) -> str:
        rgba = self.get_value()
        return rgb_to_hex(rgba[:3])

    def get_picked_opacity(self) -> float:
        rgba = self.get_value()
        return rgba[3]


class Textbox(ControlMobject):
    """
    An interactive text input control that accepts keyboard input in a scene.

    Textbox is a ControlMobject subclass that combines a rectangular input
    box with a text object. When active, it listens for keyboard events and
    updates its stored string value in response to supported key presses.
    Clicking the rectangle toggles the active state, and the rectangle's
    stroke color indicates whether the textbox is active.

    The displayed text is resized to fit within the box and repositioned
    when its value changes.

    Parameters
    ----------
    value : str, default=""
        Initial text displayed in the textbox and stored as its value.

    value_type : np.dtype, default=np.dtype(object)
        Data type associated with the stored value. This parameter is saved
        as an attribute but is not used to convert the string in the shown
        implementation.

    box_kwargs : dict, default={"width": 2.0, "height": 1.0, "fill_color": DEFAULT_MOBJECT_COLOR, "fill_opacity": 1.0}
        Keyword arguments passed to Rectangle to configure the input box.

    text_kwargs : dict, default={"color": BLUE}
        Keyword arguments passed to Text to configure the displayed text.

    text_buff : float, default=MED_SMALL_BUFF
        Horizontal buffer reserved on each side of the text when fitting it
        to the box's width.

    isInitiallyActive : bool, default=False
        Determines whether the textbox starts in the active state.

    active_color : ManimColor, default=BLUE
        Stroke color used when the textbox is active.

    deactive_color : ManimColor, default=RED
        Stroke color used when the textbox is inactive.

    **kwargs
        Additional keyword arguments forwarded to ControlMobject.

    Attributes
    ----------
    value_type : np.dtype
        Stored value type parameter.

    box_kwargs : dict
        Configuration used to construct the rectangular input box.

    text_kwargs : dict
        Configuration used to construct the displayed Text object.

    text_buff : float
        Horizontal spacing reserved around the displayed text.

    isInitiallyActive : bool
        Initial active-state setting supplied to the constructor.

    active_color : ManimColor
        Stroke color indicating the active state.

    deactive_color : ManimColor
        Stroke color indicating the inactive state.

    isActive : bool
        Current active state. Clicking the box toggles this attribute.

    box : Rectangle
        Rectangular input area. Its stroke color changes with the active state.

    text : Text
        Text object displaying the current string value.

    Methods
    -------
    set_value_anim(value)
        Updates the displayed text when the tracked value changes.

    update_text(value)
        Rebuilds the displayed text, fits it to the box, and positions it
        inside the input area.

    active_anim(isActive)
        Updates the box stroke color to reflect the active state.

    box_on_mouse_press(mob, event_data)
        Toggles the active state when the input box is clicked.

    on_key_press(mob, event_data)
        Processes supported keyboard events while the textbox is active.

    Examples
    --------
    Create an initially inactive textbox::

        textbox = Textbox()
        self.add(textbox)

    Create a textbox with initial text::

        textbox = Textbox(value="Hello")
        self.add(textbox)

    Start with the textbox active::

        textbox = Textbox(
            value="Type here",
            isInitiallyActive=True,
        )
        self.add(textbox)

    Customize the box and text appearance::

        textbox = Textbox(
            value="Name",
            box_kwargs={
                "width": 3.0,
                "height": 0.8,
                "fill_color": BLACK,
                "fill_opacity": 1.0,
            },
            text_kwargs={"color": WHITE},
            active_color=GREEN,
            deactive_color=RED,
        )
        self.add(textbox)

    Read or programmatically change the value::

        textbox = Textbox(value="Manim")
        print(textbox.get_value())

        textbox.set_value("ManimGL")

    Notes
    -----
    - The constructor creates the Rectangle and Text objects, registers a
      mouse-press listener on the rectangle, and registers a key-press
      listener on the Textbox itself.
    - Clicking the box toggles ``isActive`` and changes the rectangle's
      stroke color. The click handler returns ``False`` to stop further
      event bubbling according to the event system's dispatch rules.
    - Keyboard input is processed only when ``mob.isActive`` is True.
    - The key handler reads ``symbol`` and ``modifiers`` from ``event_data``.
      It appends alphanumeric characters, converts them to uppercase when
      Shift is held, and otherwise converts them to lowercase.
    - The handler also contains branches for space, Tab, and Backspace.
      Space appends the character represented by the key symbol, Tab appends
      a tab character, and Backspace removes the final character.
    - The implementation calls ``chr(symbol)`` before checking special keys.
      Depending on the key constants and event representation, this may not
      produce a meaningful character for special keys.
    - The shown handler does not implement arrow-key navigation, cursor
      positioning, selection, clipboard operations, Enter-key submission,
      or general modifier-based shortcuts.
    - Unsupported keys do not intentionally modify the value. However,
      the handler still calls ``set_value`` with the unchanged value and
      returns ``False`` while active.
    - ``update_text`` reinitializes the existing Text object with the new
      string and styling, fits its width to the box minus the horizontal
      buffers, and limits its height to the height measured before resizing.
    - A no-op or other updater behavior is not used to implement text editing;
      the actual editing logic resides in ``on_key_press``.
    - ``value_type`` is stored but does not convert the value into another
      type. The control is designed around string input.
    - Interactive typing requires a rendering or preview environment that
      dispatches keyboard and mouse events.

    See Also
    --------
    ControlMobject
        Base class for value-based visual controls.
    Button
        Wraps a Mobject and invokes a callback on mouse press.
    Checkbox
        A clickable Boolean control with a checkmark or cross.
    """

    def __init__(
        self,
        value: str = "",
        value_type: np.dtype = np.dtype(object),
        box_kwargs: dict = {
            "width": 2.0,
            "height": 1.0,
            "fill_color": DEFAULT_MOBJECT_COLOR,
            "fill_opacity": 1.0,
        },
        text_kwargs: dict = {
            "color": BLUE
        },
        text_buff: float = MED_SMALL_BUFF,
        isInitiallyActive: bool = False,
        active_color: ManimColor = BLUE,
        deactive_color: ManimColor = RED,
        **kwargs
    ):
        self.value_type = value_type
        self.box_kwargs = box_kwargs
        self.text_kwargs = text_kwargs
        self.text_buff = text_buff
        self.isInitiallyActive = isInitiallyActive
        self.active_color = active_color
        self.deactive_color = deactive_color

        self.isActive = self.isInitiallyActive
        self.box = Rectangle(**self.box_kwargs)
        self.box.add_mouse_press_listner(self.box_on_mouse_press)
        self.text = Text(value, **self.text_kwargs)
        super().__init__(value, self.box, self.text, **kwargs)
        self.update_text(value)
        self.active_anim(self.isActive)
        self.add_key_press_listner(self.on_key_press)

    def set_value_anim(self, value: str) -> None:
        self.update_text(value)

    def update_text(self, value: str) -> None:
        text = self.text
        self.remove(text)
        text.__init__(value, **self.text_kwargs)
        height = text.get_height()
        text.set_width(self.box.get_width() - 2 * self.text_buff)
        if text.get_height() > height:
            text.set_height(height)
        text.add_updater(lambda mob: mob.move_to(self.box))
        text.fix_in_frame()
        self.add(text)

    def active_anim(self, isActive: bool) -> None:
        if isActive:
            self.box.set_stroke(self.active_color)
        else:
            self.box.set_stroke(self.deactive_color)

    def box_on_mouse_press(self, mob, event_data) -> bool:
        self.isActive = not self.isActive
        self.active_anim(self.isActive)
        return False

    def on_key_press(self, mob: Mobject, event_data: dict[str, int]) -> bool | None:
        symbol = event_data["symbol"]
        modifiers = event_data["modifiers"]
        char = chr(symbol)
        if mob.isActive:
            old_value = mob.get_value()
            new_value = old_value
            if char.isalnum():
                if modifiers & Mods.SHIFT:
                    new_value = old_value + char.upper()
                else:
                    new_value = old_value + char.lower()
            elif symbol == Keys.SPACE:
                new_value = old_value + char
            elif symbol == Keys.TAB:
                new_value = old_value + '\t'
            elif symbol == Keys.BACKSPACE:
                new_value = old_value[:-1] or ''
            mob.set_value(new_value)
            return False


class ControlPanel(Group):
    """
    A draggable control panel that groups interactive controls inside a movable
    panel, with an opener that can be repositioned to reveal or hide the panel.

    The panel contains a collection of :class:`ControlMobject` instances arranged
    vertically. Its opener can be dragged vertically, moving the panel and its
    controls along with it. Mouse-wheel scrolling shifts the controls vertically
    within the panel.

    Parameters
    ----------
    *controls : ControlMobject
        Interactive controls to place inside the panel. They are arranged
        vertically when the controls group is initialized.
    panel_kwargs : dict, optional
        Keyword arguments passed to :class:`Rectangle` to construct the panel.
        Defaults to a grey rectangle with width ``FRAME_WIDTH / 4``, height
        ``MED_SMALL_BUFF + FRAME_HEIGHT``, full fill opacity, and no stroke.
    opener_kwargs : dict, optional
        Keyword arguments passed to :class:`Rectangle` to construct the panel
        opener. Defaults to a grey rectangle with width ``FRAME_WIDTH / 8``,
        height ``0.5``, and full fill opacity.
    opener_text_kwargs : dict, optional
        Keyword arguments passed to :class:`Text` to create the opener label.
        Defaults to the text ``"Control Panel"`` with font size ``20``.
    **kwargs
        Additional keyword arguments passed to the parent :class:`Group`
        constructor.

    Attributes
    ----------
    panel_kwargs : dict
        Configuration dictionary used to create the panel rectangle.
    opener_kwargs : dict
        Configuration dictionary used to create the opener rectangle.
    opener_text_kwargs : dict
        Configuration dictionary used to create the opener label.
    panel : Rectangle
        Main panel rectangle. It is initially positioned beyond the top-left
        corner and receives mouse-scroll events.
    panel_opener_rect : Rectangle
        Rectangle forming the draggable panel opener.
    panel_info_text : Text
        Text label displayed on the opener rectangle.
    panel_opener : Group
        Group containing the opener rectangle and its text. Dragging this group
        vertically repositions the panel and controls.
    controls : Group
        Group containing the supplied controls, arranged vertically during
        initialization.

    Methods
    -------
    move_panel_and_controls_to_panel_opener()
        Repositions the panel directly above the opener rectangle and positions
        the controls above the opener with a buffer, preserving the controls'
        previous horizontal coordinate.
    add_controls(*new_controls)
        Adds controls to the controls group and repositions the panel and controls.
    remove_controls(*controls_to_remove)
        Removes the specified controls from the controls group and repositions
        the panel and remaining controls.
    open_panel()
        Moves the opener to the bottom-left corner while preserving its current
        horizontal coordinate, then repositions the panel and controls. Returns
        this ControlPanel instance.
    close_panel()
        Moves the opener to the top-left corner while preserving its current
        horizontal coordinate, then repositions the panel and controls. Returns
        this ControlPanel instance.
    panel_opener_on_mouse_drag(mob, event_data)
        Handles dragging the opener by matching its vertical position to the
        pointer position, then repositions the panel and controls. Returns False
        to stop event propagation.
    panel_on_mouse_scroll(mob, event_data)
        Shifts the controls vertically according to the vertical scroll offset.
        The displacement is ten times the vertical offset. Returns False to stop
        event propagation.

    Notes
    -----
    - The panel, opener, and controls are grouped together, and ``fix_in_frame()``
      is called during initialization so the control panel remains fixed relative
      to the camera frame.
    - The panel is initially moved above the upper-left corner. The final
      positioning of the panel and controls is determined by
      ``move_panel_and_controls_to_panel_opener()``.
    - ``open_panel()`` and ``close_panel()`` reposition the opener to the bottom-
      left and top-left corners, respectively. They do not animate the transition.
    - Dragging the opener changes its vertical position to match the pointer.
      Its horizontal coordinate is not directly updated by the drag handler.
    - Scrolling moves the entire controls group vertically; no clipping,
      scrolling bounds, or automatic restoration of the controls' original
      position is implemented in this class.
    - ``add_controls()`` and ``remove_controls()`` update group membership and
      reposition the panel and controls, but do not explicitly rearrange newly
      added controls or restore their original ordering.
    - The scroll handler uses only ``event_data["offset"][1]``. Horizontal scroll
      offsets are ignored.
    - The default argument dictionaries are mutable objects. Avoid modifying
      them in place if you want to prevent shared-default side effects.

    Examples
    --------
    Create a panel containing a checkbox and a slider::

        checkbox = Checkbox(value=False)
        slider = LinearNumberSlider(
            value=0.5,
            min_value=0,
            max_value=1,
            step=0.1,
        )

        panel = ControlPanel(checkbox, slider)
        self.add(panel)

    Move the opener to the bottom or top of the frame::

        panel.open_panel()
        panel.close_panel()

    Add or remove a control after initialization::

        panel.add_controls(Checkbox(value=True))
        panel.remove_controls(checkbox)

    See Also
    --------
    ControlMobject
    Checkbox
    LinearNumberSlider
    Group
    Rectangle
    Text
    """

    def __init__(
        self,
        *controls: ControlMobject,
        panel_kwargs: dict = {
            "width": FRAME_WIDTH / 4,
            "height": MED_SMALL_BUFF + FRAME_HEIGHT,
            "fill_color": GREY_C,
            "fill_opacity": 1.0,
            "stroke_width": 0.0
        },
        opener_kwargs: dict = {
            "width": FRAME_WIDTH / 8,
            "height": 0.5,
            "fill_color": GREY_C,
            "fill_opacity": 1.0
        },
        opener_text_kwargs: dict = {
            "text": "Control Panel",
            "font_size": 20
        },
        **kwargs
    ):
        self.panel_kwargs = panel_kwargs
        self.opener_kwargs = opener_kwargs
        self.opener_text_kwargs = opener_text_kwargs

        self.panel = Rectangle(**self.panel_kwargs)
        self.panel.to_corner(UP + LEFT, buff=0)
        self.panel.shift(self.panel.get_height() * UP)
        self.panel.add_mouse_scroll_listner(self.panel_on_mouse_scroll)

        self.panel_opener_rect = Rectangle(**self.opener_kwargs)
        self.panel_info_text = Text(**self.opener_text_kwargs)
        self.panel_info_text.move_to(self.panel_opener_rect)

        self.panel_opener = Group(self.panel_opener_rect, self.panel_info_text)
        self.panel_opener.next_to(self.panel, DOWN, aligned_edge=DOWN)
        self.panel_opener.add_mouse_drag_listner(self.panel_opener_on_mouse_drag)

        self.controls = Group(*controls)
        self.controls.arrange(DOWN, center=False, aligned_edge=ORIGIN)
        self.controls.move_to(self.panel)

        super().__init__(
            self.panel, self.panel_opener,
            self.controls,
            **kwargs
        )

        self.move_panel_and_controls_to_panel_opener()
        self.fix_in_frame()

    def move_panel_and_controls_to_panel_opener(self) -> None:
        self.panel.next_to(
            self.panel_opener_rect,
            direction=UP,
            buff=0
        )

        controls_old_x = self.controls.get_x()
        self.controls.next_to(
            self.panel_opener_rect,
            direction=UP,
            buff=MED_SMALL_BUFF
        )

        self.controls.set_x(controls_old_x)

    def add_controls(self, *new_controls: ControlMobject) -> None:
        self.controls.add(*new_controls)
        self.move_panel_and_controls_to_panel_opener()

    def remove_controls(self, *controls_to_remove: ControlMobject) -> None:
        self.controls.remove(*controls_to_remove)
        self.move_panel_and_controls_to_panel_opener()

    def open_panel(self):
        panel_opener_x = self.panel_opener.get_x()
        self.panel_opener.to_corner(DOWN + LEFT, buff=0.0)
        self.panel_opener.set_x(panel_opener_x)
        self.move_panel_and_controls_to_panel_opener()
        return self

    def close_panel(self):
        panel_opener_x = self.panel_opener.get_x()
        self.panel_opener.to_corner(UP + LEFT, buff=0.0)
        self.panel_opener.set_x(panel_opener_x)
        self.move_panel_and_controls_to_panel_opener()
        return self

    def panel_opener_on_mouse_drag(self, mob, event_data: dict[str, np.ndarray]) -> bool:
        point = event_data["point"]
        self.panel_opener.match_y(Dot(point))
        self.move_panel_and_controls_to_panel_opener()
        return False

    def panel_on_mouse_scroll(self, mob, event_data: dict[str, np.ndarray]) -> bool:
        offset = event_data["offset"]
        factor = 10 * offset[1]
        self.controls.set_y(self.controls.get_y() + factor)
        return False
