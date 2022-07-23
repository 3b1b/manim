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
        mass: float,
        pos: np.ndarray,
        mobj: Mobject
    ) -> None:
        """
        Initialize a new Body object
        """

        self.mass: float = mass
        if self.mass < 0:
            raise Exception(
                f"Current value for mass ({self.mass}) is negative!"
            )
        
        self.pos: np.ndarray = pos
        if len(self.pos.shape) != 1 or self.pos.shape[0] == 3:
            raise Exception("Position is invalid!")
        
        self.mobj: Mobject = mobj
        self.mobj.move_to(self.pos)

        # index of the body in the physical system, to be set
        # by a PhysicalSystem
        self.index: int = -1
