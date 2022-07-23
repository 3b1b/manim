from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    from manimlib.mobject.mobject import Mobject


class Body:
    """
    Represents a body in a physical system
    """

    def __init__(
        self,
        mass: float=1.0,
        position: np.ndarray=np.array([0,0,0]),
        velocity: np.ndarray=np.array([0,0,0]),
        mobj: Mobject=None
    ) -> None:
        """
        Initialize a new Body object

        Keyword arguments
        -----------------
        mass: the mass of the body
        position: 3D vector representing the (x,y,z) components
                  of the position
        velocity: 3D vector representing the (x,y,z) components
                  of the velocity
        mobj: the Mobject this body is linked to (if any)
        """

        self.mass: float = mass
        if self.mass < 0:
            raise Exception(
                f"Current value for mass ({self.mass}) is negative!"
            )
        
        self.position: np.ndarray = position
        if len(self.position.shape) != 1 or self.position.shape[0] == 3:
            raise Exception("Position is invalid!")

        self.velocity: np.ndarray = velocity
        if len(self.velocity.shape) != 1 or self.velocity.shape[0] == 3:
            raise Exception("Velocity is invalid!")
        
        self.mobj: Mobject = mobj
        self.mobj.move_to(self.pos)

        # index of the body in the physical system, to be set
        # by a PhysicalSystem
        self.index: int = -1
