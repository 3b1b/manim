from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable
    from manimlib.mobject.mobject import Mobject
    from manimlib.program import Program, Slot
    from manimlib.renderer import Renderer


class DrawList(object):
    """
    What a frame draws, in the order it draws it: a slot for each mobject holding points, each
    knowing the program which draws it.

    A frame is two walks of that list. The first writes every mobject's values into the arenas
    and settles everything else its draw needs; the second draws. They are separate because a
    write reaching the gpu partway through a render pass has no say over which draws see it.

    Programs are kept for as long as the renderer, there being one per kind of mobject rather
    than per mobject. Slots outlive a frame, so that a mobject whose values have not moved is
    not copied again, and are let go of as soon as a frame does not draw it.
    """

    def __init__(self, renderer: Renderer):
        self.renderer = renderer
        self.programs: dict[tuple, Program] = dict()
        self.slots: dict[Mobject, Slot] = dict()

    def draw(self, mobjects: Iterable[Mobject], attachments: dict) -> None:
        slots = self.resolve(mobjects)
        renderer = self.renderer

        renderer.begin_writes()
        for slot in slots:
            slot.program.write(slot)
        renderer.end_writes()

        renderer.begin_frame(attachments)
        for slot in slots:
            slot.program.render(slot)
        renderer.end_frame()

    def resolve(self, mobjects: Iterable[Mobject]) -> list[Slot]:
        """
        A slot for every member of every family, in drawing order, keeping the one it had where
        it has one. A member holding no points, a group say, is passed over, as is one whose
        kind has no shader to be drawn by.
        """
        held = self.slots
        self.slots = dict()
        drawn = []
        for mobject in mobjects:
            for mob in mobject.get_family():
                if len(mob.data) == 0:
                    continue
                slot = held.get(mob)
                if slot is None or slot.replacements is not mob.shader_code_replacements:
                    program = self.program_for(mob)
                    slot = program.slot_class(program, mob)
                self.slots[mob] = slot
                if slot.program.modules:
                    drawn.append(slot)
        return drawn

    def program_for(self, mobject: Mobject) -> Program:
        """
        What draws this mobject, shared with every mobject its program key agrees with, see
        Program.key.
        """
        program_class = mobject.program_class
        key = program_class.key(mobject)
        if key not in self.programs:
            self.programs[key] = program_class(self.renderer, mobject)
        return self.programs[key]
