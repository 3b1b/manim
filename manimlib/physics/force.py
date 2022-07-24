from __future__ import annotations

from abc import ABCMeta, abstractmethod

import numpy as np

from typing import Union, Callable
from manimlib.mobject.mobject import Mobject

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
        mobjects: tuple[Mobject, ...]=()
    ) -> None:
        """
        Initialize a new Force object

        Keyword arguments
        -----------------
        bodies (tuple[Body, ...]): the bodies to which the force applies
        mobjects (tuple[Mobject, ...]): mobject(s) representing the force, should
                 be already set to a desired position (subclasses know
                 how to update them). Regular shapes should be used for 2D
                 simulations and 3D shapes for 3D simulations! Otherwise
                 things MAY BREAK! (default: empty tuple)
        """
        self.bodies: tuple[Body, ...] = bodies
        if not self.bodies:
            raise Exception("No bodies have been provided!")
        self.mobjects: tuple[Mobject, ...] = mobjects
    
    def __str__(self) -> str:
        body_info: str = ','.join([f"body{i}_index={body.index}" for i, body in enumerate(self.bodies, start=1)])
        return (f"{body_info},mobjects={self.mobjects}")

    def update_mobjects(self) -> None:
        """
        Update the foce mobject(s)
        (to be implemented by each subclass)
        """
        pass

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


class PairForce(Force):
    """
    Abstract force class (apply() is not implemented) that applies to
    2 bodies
    """
    def __init__(
        self,
        bodies: tuple[Body, Body],
        mobjects: tuple[Mobject, ...]=(),
    ) -> None:
        """
        Initialize a new PairForce object

        Keyword arguments
        -----------------
        bodies (tuple[Body, Body]): the 2 bodies to which the force applies
        mobjects (tuple[Mobject, ...]): mobject(s) representing the force, should
                 be already set to a desired position (subclasses know
                 how to update them). Regular shapes should be used for 2D
                 simulations and 3D shapes for 3D simulations! Otherwise
                 things MAY BREAK! (default: empty tuple)
        """
        if len(bodies) != 2:
            raise Exception("You must provide exactly 2 bodies!")
        super().__init__(bodies, mobjects)


class PairLineForce(PairForce):
    """
    Abstract force class (apply() is not implemented) that can manage a
    line connecting its 2 bodies as mobject
    """

    def __init__(
        self,
        bodies: tuple[Body, Body],
        mobjects: tuple[Union[Line, Line3D]]=(),
    ) -> None:
        """
        Initialize a new PairLineForce instance

        Keyword arguments
        -----------------
        bodies (tuple[Body, Body]): the 2 bodies to which the force applies
        mobjects (tuple[Line | Line3D]): line representing the force and follows
                 the bodies, may already be set to have the bodies at its
                 extremes (start=bodies[0], end=bodies[1]) (default: empty tuple)
        """
        super().__init__(bodies, mobjects)
    
    def update_mobjects(self) -> None:
        """
        Update the line mobject to follow the bodies
        """
        if not self.mobjects or self.mobjects[0] is None:
            return
        line: Union[Line, Line3D] = self.mobjects[0]
        body1, body2 = self.bodies[0], self.bodies[1]
        delta_pos: np.ndarray =  body2.position - body1.position
        distance: float = np.linalg.norm(delta_pos)
        if isinstance(line, Line):  # for 2D simulations
            line.set_length(distance)
            line.set_angle(np.arctan2(delta_pos[1], delta_pos[0]))
            line.move_to((body1.position+body2.position)/2)
        elif isinstance(line, Line3D):  # TODO: implement this
            print(
                f"({self.__class__.__name__}) WARNING: updating "
                "is not implemented yet."
            )
        else:
            print(
                f"({self.__class__.__name__}) WARNING: the mobject "
                "is not a line. Cannot update it."
            )


class NewtonGravitationalForce(PairLineForce):
    """
    Newton's gravitational force between two masses
    F = - G * m1 * m2 / r^2
    """

    def __init__(
        self,
        bodies: tuple[Body, Body],
        mobjects: tuple[Union[Line, Line3D]]=(),
        G: float=1.0
    ) -> None:
        """
        Initialize a new NewtonGravitationalForce instance

        Keyword arguments
        -----------------
        bodies (tuple[Body, Body]): the bodies to which the force applies
        mobjects (tuple[Line | Line3D]): line representing the force and follows
             the bodies, must already be set to have the bodies at its
             extremes (start=bodies[0], end=bodies[1]) (default: empty tuple)
        G (float): gravitational constant (default: 1.0)
        """
        super().__init__(bodies, mobjects)
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
