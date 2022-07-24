from __future__ import annotations

import numpy as np
from scipy.integrate import odeint

from typing import TYPE_CHECKING

from manimlib.mobject.mobject import Mobject
from manimlib.scene.scene import Scene
from manimlib.animation.animation import Animation
from manimlib.physics.physical_system import PhysicalSystem
from manimlib.constants import DIMENSIONS, DEFAULT_FPS

if TYPE_CHECKING:
    from typing import Callable


class EvolvePhysicalSystem(Animation):
    """
    Evolves a PhysicalSystem object
    (integrates it over time)
    """

    def __init__(
        self,
        mobject: PhysicalSystem,
        integrator: Callable[
            [
                Callable[[np.ndarray, float, PhysicalSystem], np.ndarray],
                np.ndarray,
                np.ndarray,
                tuple
            ],
            np.ndarray
        ]=odeint,
        t: np.ndarray=np.linspace(0, 10, DEFAULT_FPS*100),
        scene: Scene=None,
        background_mobjects: list[Mobject]=[],
        foreground_mobjects: list[Mobject]=[],
        **kwargs
    ):
        """
        Initialize a new EvolvePhysicalSystem instance

        Keyword arguments
        -----------------
        integrator (Callable[[], np.ndarray]): 
        mobject (PhysicalSystem): the PhysicalSystem mobject
        integrator (Callable[
                [
                    Callable[[np.ndarray, float, PhysicalSystem], np.ndarray],
                    np.ndarray,
                    np.ndarray,
                    tuple
                ],
                np.ndarray
            ]): function in terms of (dydt, y0, t, args) returning a matrix where each row
                is the state at every point in the t vector.
                dydt (provided by this class) is a function in terms of the state y0 at a
                certain time and the physical system (coming from args[0]), returning the
                derivative (vector) of the state with respect to time.
                y0 is the initial state (vector).
                t is the vector of time-points in which to get the state.
                args is a tuple containing any extra arguments dydt may need.
                For an example of the 'integrator' function, see odeint in scipy.integrate, which
                is the default value.
        t (np.ndarray[N]): vector containing all time-points of integration, must be monotonic
                           (default np.linspace(0, 10, DEFAULT_FPS*100))
        scene (Scene): scene is needed if we want to keep the body mobject, force mobject,
                       body tracer rendering order (default None)
        background_mobjects (list[Mobject]): mobjects that form part of the background and should be
                            brought to the back of the rendering order in each animation step, first in the
                            list is the furthest object in the back (default: empty list)
        foreground_mobjects (list[Mobject]): mobjects that form part of the foreground and should be
                            brought to the front of the rendering order in each animation step, last in the
                            list is the closest object in the front (default: empty list)
        kwargs (dict[str, Any]): arguments to be interpreted by
               the Animation superclass
        """
        super().__init__(mobject, **kwargs)
        # Save properties
        self.n_bodies: int = self.mobject.get_n_bodies()
        self.scene: Scene = scene
        self.background_mobjects: list[Mobject] = background_mobjects
        self.foreground_mobjects: list[Mobject] = foreground_mobjects
        # Assemble initial state (positions and velocities)
        y0: np.ndarray = np.concatenate(
            [
                body.position for body in mobject.bodies
            ] + [
                body.velocity for body in mobject.bodies
            ]
        )
        # Integrate (single element tuples must have a comma at the end)
        self.y: np.ndarray = integrator(self.dydt, y0, t, (self.mobject,))

    def interpolate_mobject(self, alpha: float) -> None:
        row_index: int = min(
            int(np.floor(alpha*self.y.shape[0])),
            self.y.shape[0]-1
        )
        state: np.ndarray = self.y[row_index,:]
        for i, body in enumerate(self.mobject.bodies):
            pos = state[i*DIMENSIONS:(i+1)*DIMENSIONS]
            vel = state[(i+self.n_bodies)*DIMENSIONS:(i+self.n_bodies+1)*DIMENSIONS]
            body.set_velocity(vel)
            body.set_position(pos, update_mobject_position=True)
            body.update_tracer()
            if body.tracer is not None:
                self.scene.bring_to_back(body.tracer)
            if body.mobj is not None:
                self.scene.bring_to_front(body.mobj)
        # Update mobjects in forces
        for force in self.mobject.forces:
            force.update_mobjects()
        # Handle background and foreground mobjects
        if self.background_mobjects:
            self.scene.bring_to_back(*self.background_mobjects)
        if self.foreground_mobjects:
            self.scene.bring_to_front(*self.foreground_mobjects)

    @staticmethod
    def dydt(
        y: np.ndarray,
        t: float,
        system: PhysicalSystem
    ) -> np.ndarray:
        """
        Compute the derivative of the state a physical system

        Keyword arguments
        -----------------
        y (np.ndarray[nbodies*2*DIMENSIONS]): state containing
          the position of each body and then its velocity
        t (float): current time
        system (PhysicalSystem): the physical system instance

        Returns
        -----------------
        The derivative of the state vector
        (np.ndarray[nbodies*2*DIMENSIONS]) containing the
        velocities and then accelerations
        """
        n_bodies: int = system.get_n_bodies()
        masses: np.ndarray = system.get_masses()
        # Split info from state vector
        velocities: np.ndarray = y[DIMENSIONS*n_bodies:].reshape((n_bodies, DIMENSIONS))
        # Reshape positions so that every row contains the location of that mass
        positions: np.ndarray = y[:DIMENSIONS*n_bodies].reshape((n_bodies, DIMENSIONS))
        # Update the positions and velocities of the bodies in the system
        system.update_positions(positions)
        system.update_velocities(velocities)
        # Create structure for forces
        forces: np.ndarray = np.zeros((n_bodies, DIMENSIONS))
        # Apply the forces in the system
        for force in system.forces:
            force.apply(forces)
        # Get the accelerations (a=F/m)
        accelerations: np.ndarray = forces/masses.reshape((n_bodies,1))
        # Return derivative of the state
        return np.concatenate((velocities.flatten(), accelerations.flatten()))
