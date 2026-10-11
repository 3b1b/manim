from __future__ import annotations

import numpy as np
from manimlib.mobject.mobject import Mobject
from manimlib.utils.bezier import interpolate
from manimlib.utils.iterables import listify
from manimlib.utils.paths import straight_path

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable
    from manimlib.typing import Self


class ValueTracker(Mobject):
    """
    Not meant to be displayed. Instead the position encodes some
    number, often one which another animation or continual_animation
    uses for its update function, and by treating it as a mobject it can
    still be animated and manipulated just like anything else.

    The value is held here rather than among the uniforms, which are floats laid out
    to match what a shader expects, since a tracker's value may be complex, or an
    array of any length, and never reaches a shader in any case.

    ValueTracker is a :class:`Mobject` that stores a numerical value independently
    of its visual geometry. It is useful for controlling animations, tracking
    changing quantities, and providing values to updater functions. Although it
    is not intended to be displayed, it can be animated and manipulated through
    the normal mobject animation system.

    The stored value is represented internally as a NumPy array. This allows the
    tracker to hold a scalar, a complex number, or an array of values, depending
    on the configured ``value_type``. Its interpolation behavior operates directly
    on the internal representation, allowing subclasses to customize how values
    are encoded and animated.

    Attributes
    ----------
    value_type : type
        NumPy-compatible data type used to store the tracker's value. Defaults
        to ``np.float64``. Subclasses can override this attribute to change the
        internal value representation.
    value : numpy.ndarray
        Internal array containing the tracked value. It is initialized from the
        supplied value after applying ``listify`` and converting to ``value_type``.

    Parameters
    ----------
    value : float, complex, or numpy.ndarray, optional
        Initial value to store. Defaults to ``0``. The value is converted into
        a NumPy array using ``value_type``.
    **kwargs
        Additional keyword arguments forwarded to :class:`Mobject`.

    Methods
    -------
    get_value()
        Return the tracked value as a scalar when the internal array contains
        one element, or as a NumPy array when it contains multiple elements.
    set_value(value)
        Replace the stored value in place and return the tracker itself.
    increment_value(d_value)
        Add a numerical increment to the current value.
    interpolate(mobject1, mobject2, alpha, path_func=straight_path)
        Interpolate the tracker's state between two other trackers.
    become(mobject, match_updaters=False)
        Adopt another tracker's state and copy its internal value array.

    Notes
    -----
    - The tracker is not designed to render a visible object. Its primary purpose
      is to store data that animations and updaters can read.
    - The value is stored separately from shader uniforms because it may contain
      complex numbers or arrays of arbitrary length, which are not necessarily
      suitable for shader inputs.
    - ``listify(value)`` normalizes the input before conversion to a NumPy array.
    - The ``value_type`` class attribute defaults to ``np.float64``. With this
      default, complex inputs may lose their imaginary component during
      conversion, depending on NumPy's conversion behavior. A subclass or
      alternative implementation is needed to preserve complex values reliably.
    - ``get_value`` checks whether the internal array contains exactly one
      element. If so, it returns the first element rather than the array itself.
    - ``set_value`` writes into the existing array using slice assignment.
      This preserves the array object and supports NumPy broadcasting when the
      new value is compatible with the existing array's shape.
    - Because ``set_value`` assigns in place, the new value must be compatible
      with the existing array shape or broadcastable to it. It does not resize
      the internal array.
    - ``increment_value`` reads the current value, adds ``d_value``, and stores
      the result through ``set_value``. It returns ``None``.
    - ``interpolate`` first delegates to ``Mobject.interpolate`` to interpolate
      the inherited mobject state. It then interpolates the internal ``value``
      arrays directly, rather than using the potentially scalar-returning
      ``get_value`` method.
    - The ``alpha`` argument typically represents interpolation progress:
      ``0`` corresponds to the first tracker and ``1`` to the second, with
      intermediate values representing positions between them.
    - The ``path_func`` parameter is forwarded to the parent interpolation
      method. The tracked numerical value is interpolated separately using
      the module-level ``interpolate`` function.
    - Interpolating the stored representation directly allows subclasses to
      encode their values in a custom way and define how that representation
      changes during animation.
    - ``become`` first delegates to the parent implementation, then replaces
      ``self.value`` with a copy of the other tracker's array. Using ``copy``
      prevents both trackers from sharing the same value-array object.
    - ``set_value`` returns ``self``, allowing method chaining. ``interpolate``
      and ``become`` also return ``self``; ``increment_value`` does not.
    - The implementation does not explicitly validate numerical finiteness,
      input dimensionality, or compatibility between the trackers being
      interpolated.
    - Since ``value`` is a NumPy array, callers should use ``get_value`` and
      ``set_value`` when possible rather than replacing or mutating the internal
      array without considering its shape and dtype.

    Examples
    --------
    Create a tracker initialized to zero::

        tracker = ValueTracker()
        print(tracker.get_value())  # 0.0

    Set and retrieve a value::

        tracker.set_value(3.5)
        print(tracker.get_value())  # 3.5

    Increment the current value::

        tracker.increment_value(2)
        print(tracker.get_value())  # 5.5

    Animate a tracker and use its value in an updater::

        tracker = ValueTracker(0)
        dot = Dot()

        dot.add_updater(
            lambda mob: mob.set_x(tracker.get_value())
        )
        self.add(dot)
        self.play(tracker.animate.set_value(3), run_time=2)
        dot.clear_updaters()

    Track multiple values with an array::

        tracker = ValueTracker(np.array([1.0, 2.0, 3.0]))
        tracker.set_value(np.array([4.0, 5.0, 6.0]))
        print(tracker.get_value())

    Interpolate between two trackers manually::

        start = ValueTracker(0)
        end = ValueTracker(10)
        tracker = ValueTracker(0)

        tracker.interpolate(start, end, 0.5)
        print(tracker.get_value())  # 5.0

    Subclass the tracker to use a different storage dtype::

        class ComplexValueTracker(ValueTracker):
            value_type = np.complex128

        tracker = ComplexValueTracker(1 + 2j)
        print(tracker.get_value())

    See Also
    --------
    Mobject
    ValueTracker
    interpolate
    straight_path
    listify
    """

    value_type: type = np.float64

    def __init__(
        self,
        value: float | complex | np.ndarray = 0,
        **kwargs
    ):
        self.value = np.array(listify(value), dtype=self.value_type)
        super().__init__(**kwargs)

    def get_value(self) -> float | complex | np.ndarray:
        result = self.value
        if len(result) == 1:
            return result[0]
        return result

    def set_value(self, value: float | complex | np.ndarray) -> Self:
        # Written in place to keep the broadcasting behavior
        self.value[:] = value
        return self

    def increment_value(self, d_value: float | complex) -> None:
        self.set_value(self.get_value() + d_value)

    def interpolate(
        self,
        mobject1: ValueTracker,
        mobject2: ValueTracker,
        alpha: float,
        path_func: Callable[[np.ndarray, np.ndarray, float], np.ndarray] = straight_path
    ) -> Self:
        super().interpolate(mobject1, mobject2, alpha, path_func)
        # What gets interpolated is the value as held, not as get_value returns it,
        # which is what lets a subclass change how animating it behaves by encoding
        # it differently
        self.value[:] = interpolate(mobject1.value, mobject2.value, alpha)
        return self

    def become(self, mobject: ValueTracker, match_updaters: bool = False) -> Self:
        super().become(mobject, match_updaters)
        self.value = mobject.value.copy()
        return self


class ExponentialValueTracker(ValueTracker):
    """
    Operates just like ValueTracker, except it encodes the value as the
    exponential of a position coordinate, which changes how interpolation
    behaves.

    ExponentialValueTracker inherits from :class:`ValueTracker` but stores the
    natural logarithm of the logical value internally. When the value is
    retrieved, the tracker exponentiates the stored representation. When a new
    value is assigned, it takes the natural logarithm before delegating to the
    parent class.

    This logarithmic encoding makes interpolation occur in log-space rather
    than directly in the original value-space. As a result, interpolating
    between positive values can produce exponential or multiplicative changes
    instead of ordinary linear changes.

    Parameters
    ----------
    value : float or complex, optional
        Initial logical value. The inherited constructor stores this value
        directly unless the subclass or calling code uses ``set_value`` to
        encode it. For correct exponential tracking, initialize the tracker
        with the logarithm of the intended logical value, or ensure the
        initialization behavior is adapted accordingly.
    **kwargs
        Additional keyword arguments forwarded to :class:`ValueTracker`.

    Methods
    -------
    get_value()
        Return the exponential of the internally stored value.
    set_value(value)
        Store the natural logarithm of the supplied value using the parent
        class's ``set_value`` method.

    Notes
    -----
    - The inherited ``ValueTracker`` stores its value in a NumPy array.
    - ``get_value`` calls ``ValueTracker.get_value(self)`` to retrieve the
      internal representation, then applies ``np.exp`` to it.
    - ``set_value`` applies ``np.log`` to the supplied value before delegating
      to ``ValueTracker.set_value``.
    - Because interpolation operates on the stored representation inherited
      from ``ValueTracker``, values are interpolated in logarithmic space.
    - For positive real endpoints ``a`` and ``b``, linear interpolation of
      their logarithms produces the geometric interpolation
      ``a * (b / a) ** alpha`` for ``0 <= alpha <= 1``.
    - This behavior is useful when multiplicative changes are more meaningful
      than additive changes, such as exponential growth, decay, or scale changes.
    - The natural logarithm is defined for positive real inputs. Zero and
      negative real values can produce ``-inf`` or ``nan`` values, respectively.
    - Complex values are supported by NumPy's complex logarithm and exponential,
      subject to the usual branch behavior of the complex logarithm.
    - The inherited constructor initializes ``self.value`` directly from its
      ``value`` argument; it does not call the overridden ``set_value`` method.
      Therefore, passing a logical value directly to the constructor does not
      automatically encode it in logarithmic form. To initialize correctly,
      pass the encoded value or customize the constructor.
    - The implementation does not explicitly validate the input domain or
      handle logarithm-related numerical warnings.
    - ``set_value`` returns the result of ``ValueTracker.set_value``, which is
      the tracker itself, allowing method chaining.

    Examples
    --------
    Create a tracker using an explicitly encoded initial value::

        tracker = ExponentialValueTracker(np.log(1.0))
        print(tracker.get_value())  # 1.0

    Set the logical value through ``set_value``::

        tracker.set_value(8.0)
        print(tracker.get_value())  # Approximately 8.0

    Interpolate between two positive values in logarithmic space::

        start = ExponentialValueTracker(np.log(1.0))
        end = ExponentialValueTracker(np.log(16.0))
        tracker = ExponentialValueTracker(np.log(1.0))

        tracker.interpolate(start, end, 0.5)
        print(tracker.get_value())  # Approximately 4.0

    Animate exponential growth::

        tracker = ExponentialValueTracker(np.log(1.0))
        self.play(
            tracker.animate.set_value(100.0),
            run_time=3,
        )

    See Also
    --------
    ValueTracker
    numpy.exp
    numpy.log
    """

    def get_value(self) -> float | complex:
        return np.exp(ValueTracker.get_value(self))

    def set_value(self, value: float | complex):
        return ValueTracker.set_value(self, np.log(value))


class ComplexValueTracker(ValueTracker):
    """
    A numerical tracker that stores values using NumPy's 128-bit complex
    floating-point data type.

    ComplexValueTracker inherits from :class:`ValueTracker` and overrides the
    ``value_type`` class attribute with ``np.complex128``. This allows the
    tracker to preserve both the real and imaginary components of complex
    numbers while retaining the value manipulation and interpolation behavior
    provided by the parent class.

    Unlike the default ``ValueTracker``, which uses ``np.float64``, this
    subclass can represent values of the form ``a + bj`` without discarding
    their imaginary components during conversion to the internal NumPy array.

    Attributes
    ----------
    value_type : type
        NumPy data type used to store the tracked value. Set to
        ``np.complex128``, which represents complex numbers using
        double-precision floating-point components.

    Parameters
    ----------
    value : float, complex, or numpy.ndarray, optional
        Initial value to store. Inherited from :class:`ValueTracker`.
        Defaults to ``0``. The input is converted to a NumPy array with
        ``dtype=np.complex128``.
    **kwargs
        Additional keyword arguments forwarded to the parent ``ValueTracker``
        constructor.

    Notes
    -----
    - This class does not define its own constructor. Initialization is
      inherited from ``ValueTracker``.
    - The parent constructor converts the initial value into a NumPy array
      using the subclass's ``value_type`` attribute.
    - Both real and imaginary components are preserved when a complex value
      is converted to ``np.complex128``.
    - The inherited ``get_value`` method returns a scalar when the internal
      array contains one element, or a NumPy array when it contains multiple
      elements.
    - The inherited ``set_value`` method updates the existing array in place.
    - The inherited ``increment_value`` method supports adding real or
      complex increments to the tracked value.
    - The inherited interpolation behavior operates on the internal complex
      array, allowing real and imaginary components to change during animation.
    - Since ``np.complex128`` uses double-precision floating-point components,
      it provides approximately 15–16 decimal digits of precision for each
      component, subject to normal floating-point limitations.
    - Complex values can be interpolated numerically, but their interpretation
      depends on the application. Linear interpolation in the complex plane
      does not necessarily follow a circular path or preserve magnitude.
    - This class changes the storage dtype only; it does not automatically
      implement polar-coordinate interpolation, magnitude tracking, or
      phase-unwrapping behavior.

    Examples
    --------
    Create a tracker containing a complex number::

        tracker = ComplexValueTracker(2 + 3j)
        print(tracker.get_value())  # (2+3j)

    Update the real and imaginary components::

        tracker.set_value(4 + 1j)
        print(tracker.get_value())  # (4+1j)

    Increment a complex value::

        tracker = ComplexValueTracker(1 + 2j)
        tracker.increment_value(3 - 1j)
        print(tracker.get_value())  # (4+1j)

    Animate a complex value::

        tracker = ComplexValueTracker(1 + 0j)
        self.play(
            tracker.animate.set_value(0 + 1j),
            run_time=2,
        )

    Store multiple complex values::

        tracker = ComplexValueTracker(
            np.array([1 + 1j, 2 + 3j, 4 - 2j])
        )
        print(tracker.get_value())

    See Also
    --------
    ValueTracker
    ExponentialValueTracker
    numpy.complex128
    """

    value_type: type = np.complex128
