from manimlib.mobject.mobject import Mobject

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.physics.body import Body
    from manimlib.physics.force import Force

class PhysicalSystem(Mobject):
    """
    Represents a physical system
    """

    def __init__(self, bodies: list[Body]=[], forces: list[Force]=[], **kwargs):
        super().__init__(**kwargs)
        self.bodies: list[Body] = bodies
        for i, body in enumerate(self.bodies):  # set indices for the bodies
            body.index = i
        self.forces: list[Force] = forces