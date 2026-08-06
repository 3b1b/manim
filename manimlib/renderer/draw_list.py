from __future__ import annotations

from manimlib.renderer.shader_program import Slot

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Iterable
    from manimlib.mobject.mobject import Mobject
    from manimlib.renderer.shader_program import Program
    from manimlib.renderer.renderer import Renderer


# How many frames a sequence of draws has to hold before it is worth recording. Recording
# costs about half again what making the draws once does, and replaying a fraction of it, so
# a sequence which settles for a moment pays for itself and one which never settles is left
# alone.
FRAMES_BEFORE_RECORDING = 2


class DrawList(object):
    """
    What a frame draws, in the order it draws it: a slot for each mobject holding points, each
    knowing the program which draws it.

    A frame is two walks of that list. The first writes every mobject's values into the shared
    buffers and settles everything else its draw needs; the second draws. They are separate because a
    write reaching the gpu partway through a render pass has no say over which draws see it.

    The second walk is recorded once the first stops finding anything different to say, and
    replayed with one call for as long as that holds, see Renderer.record. A recording holds
    the order of the draws, which stretch each reads, how many vertices each covers and which
    pipeline each runs, and reads the buffers afresh every time: so a scene whose mobjects only
    move, or fade, or are looked at from somewhere else, replays what it recorded.

    Consecutive mobjects which one draw could cover are gathered into runs first, see group,
    so what is written and drawn is a run at a time rather than a mobject at a time. A page of
    plain text is one run.

    Programs are kept for as long as the renderer, there being one per kind of mobject rather
    than per mobject. Slots outlive a frame, so that a mobject whose values have not moved is
    not copied again, and are let go of as soon as a frame does not draw it.
    """

    def __init__(self, renderer: Renderer, record: bool = True, together: bool = True):
        self.renderer = renderer
        self.may_record = record
        self.may_merge = together
        self.programs: dict[tuple, Program] = dict()
        self.slots: dict[Mobject, Slot] = dict()
        self.drawn: list[Slot] = []
        self.leaders: list[Slot] = []
        self.run_lengths: tuple = ()
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
        regroup = False
        for slot in slots:
            if slot.program.write_style(slot):
                regroup = True
            moved = moved or slot.resequenced
        # A frame where nothing which decides the runs moved keeps last frame's
        if moved or regroup:
            lengths = self.group(slots)
            moved = moved or lengths != self.run_lengths
            self.run_lengths = lengths
        for leader in self.leaders:
            leader.program.write_records(leader)
            moved = moved or leader.resequenced
        renderer.end_writes()
        moved = moved or renderer.rebindings != rebindings or renderer.samples != self.samples
        self.samples = renderer.samples

        self.settled = 0 if moved else self.settled + 1
        if moved:
            self.bundle = None
        elif self.may_record and self.settled >= FRAMES_BEFORE_RECORDING \
                and self.bundle is None:
            self.bundle = renderer.record(self.make_draws)

        renderer.begin_frame(attachments)
        if self.bundle is None:
            self.make_draws()
        else:
            renderer.replay(self.bundle)
        renderer.end_frame()

    def make_draws(self) -> None:
        for leader in self.leaders:
            leader.program.render(leader)

    def group(self, slots: list[Slot]) -> tuple:
        """
        Gathers consecutive mobjects which one draw can cover: the same program, nothing about
        them which a draw settles per mobject, and the same style, since a draw carries one
        block of uniforms.

        Leaves the mobjects which draw in self.leaders, each holding the run it draws, and
        gives back how long each run came out, which is what says the gathering has moved.
        """
        runs: list[list[Slot]] = []
        for slot in slots:
            if runs and self.follows(runs[-1][-1], slot):
                runs[-1].append(slot)
            else:
                runs.append([slot])
        self.leaders = []
        lengths = []
        for run in (part for run in runs for part in self.split_by_style(run)):
            run[0].members = run if len(run) > 1 else None
            self.leaders.append(run[0])
            lengths.append(len(run))
        return tuple(lengths)

    def follows(self, last: Slot, slot: Slot) -> bool:
        """
        What one draw settles for every mobject it covers, and so has to agree about.

        A fill is left out of this. It counts its winding across the whole of a draw, so two
        filled mobjects may share one only where they do not overlap, and telling whether they
        do costs more than sharing saves: the answer turns on where they are, so it has to be
        found again whenever any of them moves, and 700 glyphs cost 0.84ms to look through
        against the 0.32ms that drawing them together saves.
        """
        return (
            self.may_merge
            and slot.program is last.program
            and slot.program.merges
            and slot.depth_test == last.depth_test
            and slot.stroke_behind == last.stroke_behind
            and not (slot.has_fill or last.has_fill)
            and not (slot.ordered or last.ordered)
        )

    def split_by_style(self, run: list[Slot]) -> list[list[Slot]]:
        """
        The run cut wherever two neighbours hold different uniforms. Their blocks sit side by
        side in the buffer they share, having been claimed in this order, so one comparison
        answers for the whole run.
        """
        if len(run) == 1:
            return [run]
        shared = run[0].program.uniform_buffer
        stride = shared.window
        first, last = run[0].uniform_offset, run[-1].uniform_offset
        if last - first != (len(run) - 1) * stride:
            return [[slot] for slot in run]
        blocks = shared.blocks[first:last + stride].reshape((len(run), stride))
        alike = (blocks[1:] == blocks[:-1]).all(axis=1)
        parts = []
        start = 0
        for index, same in enumerate(alike, start=1):
            if not same:
                parts.append(run[start:index])
                start = index
        parts.append(run[start:])
        return parts

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
                    slot = Slot(self.program_for(mob), mob)
                self.slots[mob] = slot
                if slot.program.draws:
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
