from __future__ import annotations

from manimlib.renderer.material import Material
from manimlib.utils.iterables import batch_by_comparison

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable, Iterable
    from manimlib.mobject.mobject import Mobject
    from manimlib.renderer.drawing import Drawing
    from manimlib.renderer.gpu import Gpu, RenderPass
    from manimlib.renderer.shared_buffer import SharedBuffer


# How many frames a sequence of draws has to hold before it is worth bundling. Making a bundle
# costs about half again what making the draws once does, and replaying it a fraction of that,
# so a sequence which settles for a moment pays for itself and one which never settles is left
# alone.
FRAMES_BEFORE_BUNDLING = 2


class Bundling(object):
    """
    When a frame's draws are worth gathering into a render bundle, and for how long the one
    gathered still says what this frame means.

    Anything which notices that a bundle would now draw the wrong thing says so with
    invalidate, rather than each such thing being remembered and asked about afterwards.
    """

    def __init__(self, allowed: bool = True):
        self.allowed = allowed
        self.bundle: Any = None
        self.settled = 0
        self.stale = True

    def invalidate(self) -> None:
        self.stale = True

    def take(self, make: Callable[[], Any]) -> Any:
        """
        The bundle to replay this frame, or none where the draws have to be made afresh. Makes
        one where they have held still long enough to be worth it.
        """
        if self.stale:
            self.stale = False
            self.settled = 0
            self.bundle = None
        else:
            self.settled += 1
            if self.bundle is None and self.allowed \
                    and self.settled >= FRAMES_BEFORE_BUNDLING:
                self.bundle = make()
        return self.bundle


class Renderer(object):
    """
    What a frame draws, in the order it draws it: a drawing for each mobject holding points,
    each knowing the material which draws it.

    A frame is two walks of that list. The first writes every mobject's values into the shared
    buffers and settles everything else its draw needs; the second draws. They are separate
    because a write reaching the gpu partway through a render pass has no say over which draws
    see it.

    The second walk is gathered into a bundle once the first stops finding anything different
    to say, and replayed with one call for as long as that holds, see Bundling. A bundle holds
    the order of the draws, which stretch each reads, how many vertices each covers and which
    pipeline each runs, and reads the buffers afresh every time: so a scene whose mobjects only
    move, or fade, or are looked at from somewhere else, replays what it gathered.

    Consecutive mobjects which one draw could cover are gathered into runs first, see group, so
    what is written and drawn is a run at a time rather than a mobject at a time. A page of
    plain text is one run.

    Materials are kept for as long as the gpu, there being one per kind of mobject rather than
    per mobject.
    """

    def __init__(self, gpu: Gpu, bundle: bool = True, together: bool = True):
        self.gpu = gpu
        self.may_merge = together
        self.bundling = Bundling(allowed=bundle)
        self.materials: dict[tuple, Material] = dict()
        self.drawings: dict[Mobject, Drawing] = dict()
        self.drawn: list[Drawing] = []
        self.leaders: list[Drawing] = []
        self.run_lengths: tuple = ()
        self.samples = gpu.samples

    def draw(self, mobjects: Iterable[Mobject], attachments: dict) -> None:
        gpu = self.gpu
        drawings = self.resolve(mobjects)
        if drawings != self.drawn:
            self.bundling.invalidate()
        self.drawn = drawings

        rebinds = gpu.rebinds
        gpu.begin_writes()
        regroup = False
        for drawing in drawings:
            if drawing.write_uniforms():
                regroup = True
            if drawing.invalidated:
                self.bundling.invalidate()
        # A frame where nothing which decides the runs moved keeps last frame's
        if self.bundling.stale or regroup:
            lengths = self.group(drawings)
            if lengths != self.run_lengths:
                self.bundling.invalidate()
            self.run_lengths = lengths
        for leader in self.leaders:
            leader.write_records()
            if leader.invalidated:
                self.bundling.invalidate()
        gpu.end_writes()
        if gpu.rebinds != rebinds or gpu.samples != self.samples:
            self.bundling.invalidate()
        self.samples = gpu.samples

        bundle = self.bundling.take(lambda: gpu.bundle(self.make_draws))
        with gpu.render_pass(attachments) as render_pass:
            if bundle is None:
                self.make_draws(render_pass)
            else:
                render_pass.replay(bundle)

    def make_draws(self, render_pass: RenderPass) -> None:
        for leader in self.leaders:
            leader.draw(render_pass)

    def group(self, drawings: list[Drawing]) -> tuple:
        """
        Gathers consecutive mobjects which one draw can cover: the same material, nothing about
        them which a draw settles per mobject, and the same uniforms, since a draw carries one
        block of them.

        Leaves the mobjects which draw in self.leaders, each holding the run it draws, and
        gives back how long each run came out, which is what says the gathering has moved.
        """
        if not self.may_merge:
            self.leaders = list(drawings)
            return (1,) * len(drawings)

        self.compare_uniforms(drawings)
        runs = batch_by_comparison(
            drawings, lambda prev, drawing: drawing.can_follow(prev)
        )

        # Pull out first of each run as a leader
        self.leaders = []
        lengths = []
        for run in runs:
            run[0].members = run if len(run) > 1 else None
            self.leaders.append(run[0])
            lengths.append(len(run))
        return tuple(lengths)

    def compare_uniforms(self, drawings: list[Drawing]) -> None:
        """
        Tells every mobject whether the one drawn before it holds the same uniforms, which is
        the last thing can_follow needs and the one thing not worth asking a pair at a time.

        Each mobject claimed a block of its uniform buffer as it was written, in drawing order,
        so one pass over a buffer answers for every mobject which took a block from it, see
        SharedBuffer.matching_claims. A mobject only ever reads its answer against one of its
        own material, and two of a material share a buffer with nothing claiming between them,
        so the block before a mobject's own is the block of the mobject before it.
        """
        matching: dict[SharedBuffer, list[bool]] = dict()
        for drawing in drawings:
            buffer = drawing.material.uniform_buffer
            claims = matching.get(buffer)
            if claims is None:
                claims = matching[buffer] = buffer.matching_claims()
            drawing.repeats_uniforms = claims[drawing.uniform_offset // buffer.window]

    def resolve(self, mobjects: Iterable[Mobject]) -> list[Drawing]:
        """
        A drawing for every member of every family which has anything to draw, in drawing
        order, keeping the one it had where it has one. A member holding no points, a group
        say, is passed over, as is one whose kind has no shader to be drawn by.
        """
        held = self.drawings
        self.drawings = dict()
        drawn = []
        for mobject in mobjects:
            for mob in mobject.get_family():
                drawing_class = mob.drawing_class
                if len(mob.data) == 0 or not drawing_class.draws(mob):
                    continue
                drawing = held.get(mob)
                if drawing is None or drawing.replacements is not mob.shader_code_replacements:
                    drawing = drawing_class(self.material_for(mob, drawing_class), mob)
                self.drawings[mob] = drawing
                drawn.append(drawing)
        return drawn

    def material_for(self, mobject: Mobject, drawing_class: type) -> Material:
        """
        What draws this mobject, shared with every mobject its key agrees with, see
        Drawing.key.
        """
        key = drawing_class.key(mobject)
        if key not in self.materials:
            self.materials[key] = Material(
                self.gpu, mobject, drawing_class.module_specs(mobject),
            )
        return self.materials[key]
