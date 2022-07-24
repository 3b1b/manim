from __future__ import annotations

from abc import ABCMeta, abstractmethod

import numpy as np

from typing import Union

from manimlib.physics.body import Body
from manimlib.mobject.geometry import Line
from manimlib.mobject.three_dimensions import Line3D


class Force(metaclass=ABCMeta):
    """
    Represents a force among/for bodies in a physical
    system
    """

    def __init__(
        self,
        bodies: tuple[Body, ...],
        line: Union[Line, Line3D]=None
    ) -> None:
        """
        Initialize a new Force object

        Keyword arguments
        -----------------
        bodies (list[Body]): the bodies to which the force applies
        line: (Line | Line3D): line representing the force and follows
              the bodies, must already be set to have the bodies at its
              extremes (default None)
        """
        self.bodies: tuple[Body] = bodies
        if not self.bodies:
            raise Exception("No bodies have been provided!")
        self.line = line
    
    def __str__(self) -> str:
        body_info: str = ','.join([f"body{i}_index={body.index}" for i, body in enumerate(self.bodies, start=1)])
        return (f"{body_info},line={self.line}")

    @abstractmethod
    def apply(self, forces: np.ndarray) -> None:
        """
        Apply the force and add the contributions to the 'total'
        forces in the system

        Keyword arguments
        -----------------
        forces (np.ndarray[nbodies, DIMENSIONS]): each row stores the
               total force exerted in the body with that index
        """
        pass


class NewtonGravitationalForce(Force):
    """
    Newton's gravitational force between two masses
    F = - G * m1 * m2 / r^2
    """

    def __init__(
        self,
        bodies: tuple[Body],
        line: Union[Line, Line3D]=None,
        G: float=1.0
    ) -> None:
        """
        Initialize a new NewtonGravitationalForce instance

        Keyword arguments
        -----------------
        bodies (list[Body]): the bodies to which the force applies
        line (Line | Line3D): line representing the force and follows
             the bodies, must already be set to have the bodies at its
             extremes (default None)
        G (float): gravitational constant (default: 1.0)
        """
        if len(bodies) != 2:
            raise Exception("You must provide 2 bodies!")
        super().__init__(bodies)
        self.G: float = G
    
    def __str__(self) -> str:
        return (f"{self.__class__.__name__}<{super().__str__()},"
                f"G={self.G}>")

    def apply(self, forces: np.ndarray) -> None:
        body1, body2 = self.bodies[0], self.bodies[1]
        delta_pos: np.ndarray = body2.position - body1.position
        distance: float = np.linalg.norm(delta_pos)
        if distance > 0:  # apply the force
            force: np.ndarray = self.G * body1.mass * body2.mass * delta_pos / distance**3
            forces[body1.index] += force
            forces[body2.index] -= force
