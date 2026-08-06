from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Iterable
    from manimlib.mobject.mobject import Mobject
    from manimlib.program import Program, Slot
    from manimlib.renderer import Renderer


# How many frames a sequence of draws has to hold before it is worth recording. Recording
# costs about half again what making the draws once does, and replaying a fraction of it, so
# a sequence which settles for a moment pays for itself and one which never settles is left
# alone.
FRAMES_BEFORE_RECORDING = 2


class DrawList(object):
    """
    What a frame draws, in the order it draws it: a slot for each mobject holding points, each
    knowing the program which draws it.

    A frame is two walks of that list. The first writes every mobject's values into the arenas
    and settles everything else its draw needs; the second draws. They are separate because a
    write reaching the gpu partway through a render pass has no say over which draws see it.

    The second walk is recorded once the first stops finding anything different to say, and
    replayed with one call for as long as that holds, see Renderer.record. A recording holds
    the order of the draws, which stretch each reads, how many vertices each covers and which
    pipeline each runs, and reads the arenas afresh every time: so a scene whose mobjects only
    move, or fade, or are looked at from somewhere else, replays what it recorded.

    Programs are kept for as long as the renderer, there being one per kind of mobject rather
    than per mobject. Slots outlive a frame, so that a mobject whose values have not moved is
    not copied again, and are let go of as soon as a frame does not draw it.
    """

    def __init__(self, renderer: Renderer, record: bool = True):
        self.renderer = renderer
        self.may_record = record
        self.programs: dict[tuple, Program] = dict()
        self.slots: dict[Mobject, Slot] = dict()
        self.drawn: list[Slot] = []
        self.settled = 0
        self.bundle: Any = None
        self.samples = renderer.samples

    def draw(self, mobjects: Iterable[Mobject], attachments: dict) -> None:
        renderer = self.renderer
        slots = self.resolve(mobjects)
        moved = slots != self.drawn
        self.drawn = slots

        rebindings = renderer.rebindings
        renderer.begin_writes()
        for slot in slots:
            slot.program.write(slot)
            moved = moved or slot.resequenced
        renderer.end_writes()
        moved = moved or renderer.rebindings != rebindings or renderer.samples != self.samples
        self.samples = renderer.samples

        self.settled = 0 if moved else self.settled + 1
        if moved:
            self.bundle = None
        elif self.may_record and self.settled >= FRAMES_BEFORE_RECORDING \
                and self.bundle is None:
            self.bundle = renderer.record(lambda: self.make_draws(slots))

        renderer.begin_frame(attachments)
        if self.bundle is None:
            self.make_draws(slots)
        else:
            renderer.replay(self.bundle)
        renderer.end_frame()

    def make_draws(self, slots: list[Slot]) -> None:
        for slot in slots:
            slot.program.render(slot)

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
