from __future__ import annotations

from manimlib.constants import DIMENSIONS
from manimlib.mobject.mobject import Group
from manimlib.physics.body import Body
from manimlib.physics.force import Force
import numpy as np

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.mobject.mobject import Mobject


class PhysicalSystem(Group):
    """
    Represents a physical system
    (all submobjects in this class should have already been added
    to the scene)
    """

    def __init__(self, bodies: list[Body]=[], forces: list[Force]=[], **kwargs):
        """
        Initialize a new PhysicalSystem object

        Keyword arguments
        -----------------
        bodies (list[Body]): bodies to be added to the system (default: empty list)
        forces (list[Force]): forces to be added to the system (default: empty list)
        """
        # Aggregate all submobjects and pass them to the superclass constructor
        mobjects: list[Mobject] = [
            body.mobj for body in bodies if body.mobj is not None
        ] + [
            body.tracer for body in bodies if body.tracer is not None
        ] + [
            force.line for force in forces if force.line is not None
        ]
        super().__init__(*mobjects, **kwargs)
        self.bodies: list[Body] = bodies
        for i, body in enumerate(self.bodies):  # set indices for the bodies
            body.index = i
        self.forces: list[Force] = forces

    def __str__(self):
        body_str: str = [str(body) for body in self.bodies]
        force_str: str = [str(force) for force in self.forces]
        return f"{self.__class__.__name__}<bodies={body_str},forces={force_str}>"

    def get_n_bodies(self) -> int:
        """
        Get the number of bodies in the system

        Returns
        -----------------
        The number of bodies (int)
        """
        return len(self.bodies)

    def get_n_forces(self) -> int:
        """
        Get the number of forces in the system

        Returns
        -----------------
        The number of forces (int)
        """
        return len(self.forces)

    def get_masses(self) -> np.ndarray:
        """
        Get a vector containing the masses of the bodies in
        the system

        Returns
        -----------------
        An np.ndarray[n_bodies] of floats containing the masses
        """
        return np.array([body.mass for body in self.bodies])

    def update_positions(self, positions: np.ndarray) -> None:
        """
        Update positions of the bodies in the system

        Keyword arguments
        -----------------
        positions (np.ndarray[n_bodies, DIMENSIONS]): position for
                  each body in the system
        """
        desired_shape: tuple[int, int] = (self.get_n_bodies(), DIMENSIONS)
        if positions.shape != desired_shape:
            raise Exception(
                f"The shape of the provided positions {positions.shape}"
                f" does not match {desired_shape}"
            )
        for body, position in zip(self.bodies, positions):
            body.set_position(position)
    
    def update_velocities(self, velocities: np.ndarray) -> None:
        """
        Update velocities of the bodies in the system

        Keyword arguments
        -----------------
        velocities (np.ndarray[n_bodies, DIMENSIONS]): position for
                  each body in the system
        """
        desired_shape: tuple[int, int] = (self.get_n_bodies(), DIMENSIONS)
        if velocities.shape != desired_shape:
            raise Exception(
                f"The shape of the provided velocities {velocities.shape}"
                f" does not match {desired_shape}"
            )
        for body, velocity in zip(self.bodies, velocities):
            body.set_velocity(velocity)

    def fill_forces(self, **kwargs) -> None:
        """
        Some subclasses will be able to fill forces by themselves with 
        this method

        Keyword arguments
        -----------------
        kwargs (dict[str, Any]): option dictionary to be interpreted by each
               subclass
        """
        pass