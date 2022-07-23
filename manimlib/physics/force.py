from abc import ABCMeta, abstractmethod

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    from manimlib.physics.body import Body



class Force(metaclass=ABCMeta):
    """
    Represents a force among bodies in a physical
    system
    """

    def __init__(self, bodies: tuple[Body]) -> None:
        """
        Initialize a new Force object

        Keyword arguments
        -----------------
        bodies: the bodies to which the force applies
        """
        self.bodies: tuple[Body] = bodies
        if not self.bodies:
            raise Exception("No bodies have been provided!")
    
    @abstractmethod
    def apply(forces: np.ndarray):
        """
        Apply the force and add the contributions to the 'total'
        forces in the system

        Keyword arguments
        -----------------
        forces: with shape (nbodies, DIMENSIONS), each row stores the
                total force exerted in the body with that index
        """
        pass


class NewtonGravitationalForce(Force):
    """
    Newton's gravitational force between two masses
    F = - G * m1 * m2 / r^2
    """

    def __init__(self, bodies: tuple[Body]) -> None:
        super().__init__(bodies)