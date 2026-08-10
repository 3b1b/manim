from __future__ import annotations

import numpy as np
import wgpu

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any
    from manimlib.renderer.gpu import Gpu


class SharedBuffer(object):
    """
    One buffer holding what many mobjects read, a stretch of it each, sent in one write.
    Sending a buffer costs about the same whatever it holds, so gathering beats sending one
    mobject at a time.

    A stretch is claimed for the length of a frame rather than owned. A frame writes everything
    before it draws anything, see Renderer.draw, so stretches are handed out in the order the
    writing goes and given back all at once: no free list, nothing to fragment, nothing freed.

    A scene which is not changing hands them out in the same order every frame, so a mobject
    whose values have not moved finds them in place and copies nothing, and a buffer nothing
    wrote into is not sent.

    A draw is given its own stretch as a dynamic offset, so a shader counts from the front of
    what it was given and nothing about where a mobject's values sit has to live among the
    values themselves, which get interpolated. One bind group serves everything here, so
    stretches begin where the device allows a binding to and the window bound is as wide as the
    widest stretch there has been.
    """

    def __init__(
        self,
        gpu: Gpu,
        layout: Any,
        usage: int,
        alignment: int,
        first_capacity: int,
    ):
        self.gpu = gpu
        self.device = gpu.device
        self.layout = layout
        self.usage = usage | wgpu.BufferUsage.COPY_DST
        self.alignment = alignment
        self.window = alignment
        self.first_capacity = first_capacity
        self.used = 0
        self.capacity = 0
        # Nothing is set aside until a stretch is asked for, a scene having kinds of mobject
        # it never draws
        self.blocks = np.zeros(0, dtype=np.uint8)
        self.bytes = memoryview(self.blocks)
        self.buffer = None
        self.bind_group = None
        # What was written into since the last send, as two ints rather than a tuple: put is
        # called once per mobject per frame, and at that rate building a tuple and comparing
        # through min and max costs more than the copy it is bookkeeping for
        self.dirty_start = -1
        self.dirty_end = 0

    def claim(self, nbytes: int) -> int:
        """
        Where the next stretch goes, as the offset its draw is to be given. There has to be a
        whole window of buffer past the last stretch, so that the binding of even the shortest
        does not run off the end.
        """
        stretch = nbytes + -nbytes % self.alignment
        offset = self.used
        self.used += stretch
        wider = stretch > self.window
        if wider:
            self.window = stretch
        if self.grow_to(self.used + self.window) or wider:
            self.make_bindings()
        return offset

    def grow_to(self, needed: int) -> bool:
        """Room for that many bytes, and whether that meant a new buffer"""
        capacity = max(self.capacity, self.first_capacity)
        while capacity < needed:
            capacity *= 2
        if capacity == self.capacity:
            return False

        # Carried over so that a stretch which was already right stays right, though the new
        # buffer holds none of it yet
        held = self.blocks
        self.capacity = capacity
        self.blocks = np.zeros(capacity, dtype=np.uint8)
        self.blocks[:len(held)] = held
        # A memoryview slice being half the cost of a numpy one at these sizes
        self.bytes = memoryview(self.blocks)
        self.buffer = self.device.create_buffer(size=capacity, usage=self.usage)
        self.dirty_start = 0
        if self.used > self.dirty_end:
            self.dirty_end = self.used
        return True

    def make_bindings(self) -> None:
        """A group afresh, which whatever binds through this one has to hear about"""
        self.bind_group = self.device.create_bind_group(
            layout=self.layout,
            entries=[{"binding": 0, "resource": {
                "buffer": self.buffer, "offset": 0, "size": self.window,
            }}],
        )
        self.gpu.rebinds += 1

    def reset(self) -> None:
        self.used = 0

    def put(
        self,
        offset: int,
        source: np.ndarray,
        record_size: int = 0,
        repeats: int = 0,
    ) -> None:
        """
        Bytes into the buffer, followed by the last record_size of them written again that many
        times, which is what holds one mobject of a run apart from the next.

        The two go in together rather than being put separately, the stretch being one either
        way. put is called once per mobject per frame, and at that rate the marking below costs
        about what the copy does, so halving the calls is worth the two arguments.
        """
        end = offset + len(source)
        self.bytes[offset:end] = source
        if repeats:
            last = source[-record_size:]
            for step in range(repeats):
                self.bytes[end:end + record_size] = last
                end += record_size
        if offset < self.dirty_start or self.dirty_start < 0:
            self.dirty_start = offset
        if end > self.dirty_end:
            self.dirty_end = end

    def upload(self) -> None:
        """Whatever was written into since the last send, in one write"""
        start = self.dirty_start
        if start < 0:
            return
        self.gpu.queue.write_buffer(
            self.buffer, start, self.blocks, start, self.dirty_end - start,
        )
        self.dirty_start = -1
        self.dirty_end = 0

    def matching_claims(self) -> list[bool]:
        """
        For every stretch claimed since the last reset, whether it holds the same bytes as the
        stretch claimed before it, the first counting as different since it follows nothing.
        This is how mobjects are told apart by their uniforms, see Renderer.compare_uniforms.

        Only for a buffer whose claims are all one size, which the uniform buffers are, being
        kept per block size; the reshape below says so by failing where they are not. That is
        what lets a frame's worth of them be compared in one pass rather than a pair at a time.
        """
        blocks = self.blocks[:self.used].reshape((-1, self.window))
        same = np.zeros(len(blocks), dtype=bool)
        if len(blocks) > 1:
            (blocks[1:] == blocks[:-1]).all(axis=1, out=same[1:])
        return same.tolist()
