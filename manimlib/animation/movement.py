from __future__ import annotations

from manimlib.animation.animation import Animation
from manimlib.utils.rate_functions import linear

import numpy as np
from scipy.integrate import odeint

from typing import TYPE_CHECKING, Iterable, NewType

if TYPE_CHECKING:
    from typing import Callable, Sequence

    # import numpy as np

    from manimlib.mobject.mobject import Mobject


class Homotopy(Animation):
    CONFIG = {
        "run_time": 3,
        "apply_function_kwargs": {},
    }

    def __init__(
        self,
        homotopy: Callable[[float, float, float, float], Sequence[float]],
        mobject: Mobject,
        **kwargs
    ):
        """
        Homotopy is a function from
        (x, y, z, t) to (x', y', z')
        """
        self.homotopy = homotopy
        super().__init__(mobject, **kwargs)

    def function_at_time_t(
        self,
        t: float
    ) -> Callable[[np.ndarray], Sequence[float]]:
        return lambda p: self.homotopy(*p, t)

    def interpolate_submobject(
        self,
        submob: Mobject,
        start: Mobject,
        alpha: float
    ) -> None:
        submob.match_points(start)
        submob.apply_function(
            self.function_at_time_t(alpha),
            **self.apply_function_kwargs
        )


class SmoothedVectorizedHomotopy(Homotopy):
    CONFIG = {
        "apply_function_kwargs": {"make_smooth": True},
    }


class ComplexHomotopy(Homotopy):
    def __init__(
        self,
        complex_homotopy: Callable[[complex, float], Sequence[float]],
        mobject: Mobject,
        **kwargs
    ):
        """
        Given a function form (z, t) -> w, where z and w
        are complex numbers and t is time, this animates
        the state over time
        """
        def homotopy(x, y, z, t):
            c = complex_homotopy(complex(x, y), t)
            return (c.real, c.imag, z)
        super().__init__(homotopy, mobject, **kwargs)


class PhaseFlow(Animation):
    CONFIG = {
        "virtual_time": 1,
        "rate_func": linear,
        "suspend_mobject_updating": False,
    }

    def __init__(
        self,
        function: Callable[[np.ndarray], np.ndarray],
        mobject: Mobject,
        **kwargs
    ):
        self.function = function
        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        if hasattr(self, "last_alpha"):
            dt = self.virtual_time * (alpha - self.last_alpha)
            self.mobject.apply_function(
                lambda p: p + dt * self.function(p)
            )
        self.last_alpha = alpha


class MoveAlongPath(Animation):
    CONFIG = {
        "suspend_mobject_updating": False,
    }

    def __init__(self, mobject: Mobject, path: Mobject, **kwargs):
        self.path = path
        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        point = self.path.point_from_proportion(alpha)
        self.mobject.move_to(point)


####################################################################
# BEGIN: jCode custom animations                                   #
####################################################################

#### NEWTON GRAVITATION 2D ####
class NewtonGravitation2D(Animation):
    """
    Evolves a group of mobjects (with self.submobjects) using
    Newton's gravitation and Runge Kutta 4th order time integrator

    Simplified from https://github.com/jCodingStuff/NBodyProblem
    """

    CONFIG = {
        "ndimensions": 2,  # number of spatial dimentions
        "grav_constant": 1.0,  # value of the gravitational constant G
    }

    def __init__(
        self,
        t: np.ndarray,
        masses: np.ndarray,
        y0: np.ndarray,
        mobject: Mobject,
        **kwargs
    ):
        """
        Initialize a new NewtonGravitation2D object

        t: times for the system (to be passed to the integrator)
        masses: masses of the system
        y0: initial state vector (first positions then velocities)
        """
        super().__init__(mobject, **kwargs)
        # Integrate over time
        extra_args = (
            self.ndimensions,
            self.grav_constant,
            masses.shape[0],
            masses,
        )
        self.y = odeint(self.dydt, y0, t, args=extra_args)

    def interpolate_mobject(self, alpha: float) -> None:
        index = np.floor(alpha*self.y.shape[0])
        state = self.y[index]
        for i, submobj in enumerate(self.mobject.submobjects):
            point: np.ndarray = state[i*self.ndimensions:i*self.ndimensions+2]
            submobj.move_to((point[0], point[1], 0.0))

    @staticmethod
    def dydt(
        y: np.ndarray,
        t: float,
        d: int,
        G: float,
        n: int,
        masses: Iterable[float]
    ) -> np.ndarray:
        """
        Returns the derivative with respect to time of the state vector

        Keyword arguments
        -----------------
        y: state vector (x,y positions of masses followed by their velocity,
           that is, it includes 4*n elements)
        t: current time of the system
        d: number of dimensions
        G: gravitational constant
        n: number of masses in the system
        masses: an iterable containing the mass values for each mass
        """
        # Split info from state vector
        velocities: np.ndarray = y[d*n]
        # Reshape positions so that every row contains the location of that mass
        positions: np.ndarray = np.reshape(y[:d*n], (n, d))
        # Create the accelerations structure
        accelerations: np.ndarray = np.zeros((n, d))

        # Fill accelerations
        for i, acc in enumerate(accelerations):
            for j, pos in enumerate(positions):
                if i != j:
                    diff_vector = positions[i] - pos
                    acc -= masses[j] * (diff_vector / (np.linalg.norm(diff_vector)**3))

        return np.concatenate((velocities, G*accelerations.flatten()))

####################################################################
# END: jCode custom animations                                     #
####################################################################