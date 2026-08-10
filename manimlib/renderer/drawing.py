from __future__ import annotations

import numpy as np
import wgpu

from manimlib.renderer.pipeline import DEFAULT
from manimlib.renderer.pipeline import KEEP
from manimlib.renderer.pipeline import PipelineState
from manimlib.renderer.shader_source import MOBJECT_GROUP
from manimlib.renderer.shader_source import RESOURCE_GROUP
from manimlib.renderer.shader_source import read_shader_file

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any
    from manimlib.mobject.mobject import Mobject
    from manimlib.renderer.gpu import RenderPass
    from manimlib.renderer.material import Material, ModuleSpec


class Drawing(object):
    """
    One mobject's place in a frame: where its values went in the shared buffers, everything
    else its draw needs to know, and the passes it takes.

    A frame settles all of this before its render pass opens and reads nothing besides while
    drawing, see Renderer.draw. A drawing outlives the frame, so that a mobject whose values
    have not moved is not copied again, and is let go of as soon as a frame does not draw it.

    A mobject says which kind of drawing covers it by its drawing_class. What does not vary
    between two mobjects of a kind lives in the Material they share.
    """
    # Whether several of these mobjects may be drawn by one draw, which asks of their shader
    # that it read every record on the record's own terms, see Renderer.group
    merges = False
    # How many records hold one mobject of a run apart from the next
    records_between = 0

    @classmethod
    def draws(cls, mobject: Mobject) -> bool:
        """Whether this mobject has anything to be drawn by, which a group has not"""
        return bool(mobject.shader_file)

    @classmethod
    def key(cls, mobject: Mobject) -> tuple:
        """What two mobjects have to agree about to share one material"""
        return (
            cls,
            mobject.shader_file,
            mobject.data.dtype,
            mobject.uniforms.dtype,
            tuple(mobject.texture_paths.items()),
            tuple(mobject.shader_code_replacements.items()),
            mobject.verts_per_record,
        )

    @classmethod
    def module_specs(cls, mobject: Mobject) -> list[ModuleSpec]:
        """Which modules this kind of drawing needs compiled, and what to name them by"""
        return [("main", mobject.shader_file, mobject.shader_code_replacements)]

    def __init__(self, material: Material, mobject: Mobject):
        self.material = material
        self.mobject = mobject
        # The arrays this mobject holds, which it binds once and thereafter only writes into
        self.data = mobject.data
        self.uniforms = mobject.uniforms
        # What the modules were compiled from, so a mobject given new code gets a new
        # material, see Renderer.resolve
        self.replacements = mobject.shader_code_replacements
        # Where in the shared buffers this mobject's values went, no stretch yet being none
        self.uniform_offset = -1
        self.data_offset = -1
        # Which version of each array was last written into those stretches, none having been
        # written yet, see StructuredArray.version
        self.uniform_version = 0
        self.data_version = 0
        # Whether the mobject drawn before this one holds the same uniforms, which is not
        # asked here but told, see Renderer.compare_uniforms
        self.repeats_uniforms = False
        # How many records this drawing covers, which for one drawing a run of mobjects
        # together is the whole run's, and for one drawn as part of a run is none
        self.records = 0
        self.depth_test = False
        # Made only for a mobject with images of its own, the rest reading the shared one's
        self.own_bind_group: Any = None
        self.shared_bind_group: Any = None
        # Whether the writing found anything a bundled draw would have baked in to have moved,
        # which for a drawing nothing has drawn yet is everything, see Renderer.draw
        self.invalidated = True
        # The mobjects this one is drawn together with, itself first, or none where it is
        # drawn on its own, see Renderer.group
        self.members: list[Drawing] | None = None

    # Sending what the draw will read

    def write_uniforms(self) -> bool:
        """
        A mobject's uniforms into the buffer they share, along with everything its draw needs
        to know besides where its records went. Settled first, since which mobjects may be
        drawn together depends on it, see Renderer.group.

        Says whether the uniforms had changed since the last frame wrote them, which is what
        decides whether the runs have to be gathered afresh, see Renderer.draw. That answer is
        returned rather than left to be worked out again, this having already taken note of the
        version it wrote. Noting on the way whether any of it moved, which every comparison here
        was making anyway, so that a bundled draw knows to be made again.
        """
        depth_test = self.mobject.depth_test
        self.invalidated = depth_test != self.depth_test
        self.depth_test = depth_test

        # Every frame takes a stretch, one lasting only as long as the frame
        buffer = self.material.uniform_buffer
        version = self.uniforms.version
        changed = version != self.uniform_version
        self.uniform_version = version
        offset = buffer.claim(self.uniforms.array.nbytes)
        moved = offset != self.uniform_offset
        # A scene which is not changing hands its stretches out in the same order every frame,
        # so a mobject whose uniforms have not moved usually finds its values already there
        if changed or moved:
            buffer.put(offset, self.uniforms.bytes)
        self.invalidated = self.invalidated or moved
        self.uniform_offset = offset
        return changed

    def write_records(self) -> None:
        """
        A mobject's records into a stretch of the shared buffer, or, where it draws a run of
        mobjects together, all of theirs into one stretch, back to back with records between
        them holding each one's last record over again: for a vectorized mobject that repeat
        is a null curve, which is already how one mobject's own subpaths are held apart, so
        the run reads as one path and the shaders need know nothing of any of this.

        Either way the mobject which draws is given the whole stretch.
        """
        buffer = self.material.data_buffer
        run = self.members
        if run is None:
            records = len(self.data)
            offset = buffer.claim(self.data.array.nbytes)
            version = self.data.version
            moved = offset != self.data_offset or records != self.records
            if version != self.data_version or moved:
                buffer.put(offset, self.data.bytes)
            self.data_version = version
            self.data_offset = offset
            self.records = records
            self.invalidated = self.invalidated or moved
            return

        record_size = self.material.record_size
        # The array's own length rather than the StructuredArray's, which is a python call
        # per mobject of the run and answers the same
        sizes = [len(drawing.data.array) for drawing in run]
        records = sum(sizes) + self.records_between * (len(run) - 1)
        offset = buffer.claim(records * record_size)
        moved = offset != self.data_offset or records != self.records
        at = offset
        # Every mobject of the run but the last is followed by records holding its own last
        # one over again, which hold it apart from the next
        between = self.records_between
        last = len(run) - 1
        for index, (drawing, size) in enumerate(zip(run, sizes)):
            data = drawing.data
            version = data.version
            if version != drawing.data_version or at != drawing.data_offset:
                buffer.put(
                    at, data.bytes, record_size, between if index != last else 0,
                )
            drawing.data_version = version
            drawing.data_offset = at
            at += (size + between) * record_size
        self.data_offset = offset
        self.records = records
        self.invalidated = self.invalidated or moved

    # Gathering into runs

    def can_follow(self, previous: Drawing) -> bool:
        """
        Whether one draw could cover this mobject along with the one before it, which means
        agreeing about everything a draw settles for every mobject it covers.

        Sharing a material already means sharing a kind, a shader and a record layout, since
        all of those are in the key a material is kept under. The uniforms have to agree too,
        a draw carrying one block of them; that one comparison is made for a whole buffer at a
        time rather than here and read off, see Renderer.compare_uniforms.
        """
        return (
            self.merges
            and previous.material is self.material
            and self.repeats_uniforms
            and self.depth_test == previous.depth_test
        )

    # Drawing

    def draw(self, render_pass: RenderPass) -> None:
        """
        Every pass this mobject takes. What they read is bound once here, all of them reading
        the same two stretches whatever modules run over them.
        """
        material = self.material
        render_pass.bind(
            MOBJECT_GROUP, material.uniform_buffer.bind_group, (self.uniform_offset,),
        )
        render_pass.bind(
            RESOURCE_GROUP, self.resource_bind_group(), (self.data_offset,),
        )
        self.draw_passes(render_pass)

    def resource_bind_group(self) -> Any:
        """
        What this mobject's records and images are read through. Without images of its own it
        reads the shared group, which serves every mobject of its size; with them it needs one
        of its own, made again whenever the shared one is.
        """
        shared = self.material.data_buffer
        if not self.material.textures:
            return shared.bind_group
        if self.shared_bind_group is not shared.bind_group:
            self.shared_bind_group = shared.bind_group
            self.own_bind_group = self.material.make_resource_bind_group()
        return self.own_bind_group

    def draw_passes(self, render_pass: RenderPass) -> None:
        """Every pass this kind of mobject takes, which for most kinds is the one"""
        self.draw_pass(
            render_pass, "main", DEFAULT, self.material.verts_per_record * self.records,
        )

    def draw_pass(
        self,
        render_pass: RenderPass,
        module: str,
        state: PipelineState,
        vertices: int,
        indices: Any = None,
    ) -> None:
        pipeline = self.material.pipeline(module, state.resolved(self.depth_test))
        render_pass.draw(pipeline, vertices, indices)


class SurfaceDrawing(Drawing):
    """
    An opaque surface is drawn in one pass and left to the depth test, which decides what
    hides what however its triangles arrive.

    One which can be seen through cannot: blending is not commutative, so what lies behind has
    to be drawn first. Its triangles are drawn furthest from the camera first, through a buffer
    of indices written before the frame's pass opens, see Surface.is_opaque.
    """

    def __init__(self, material: Material, mobject: Mobject):
        super().__init__(material, mobject)
        # The order this surface's triangles are drawn in, where it is drawn in one
        self.order_buffer: Any = None
        self.order_count = 0
        self.ordered = False

    def write_uniforms(self) -> bool:
        changed = super().write_uniforms()
        surface = self.mobject
        was, count = self.ordered, self.order_count
        # Ordering the triangles writes a buffer of its own, so it belongs among the writes
        sort = surface.sort_to_camera or not surface.is_opaque()
        self.ordered = sort and self.order_triangles_by_depth()
        self.invalidated = self.invalidated or self.ordered != was \
            or self.order_count != count
        return changed

    def order_triangles_by_depth(self) -> bool:
        """
        Lists the vertices of every triangle of the mesh, three to each, those furthest from
        the camera first, in a buffer to be drawn through. False if there are no triangles.
        """
        first_vertices, middles = self.mobject.get_triangles()
        if len(first_vertices) == 0:
            return False
        camera_position = self.material.gpu.frame_uniforms["camera_position"]
        offsets = middles - np.array(camera_position)
        order = np.argsort(-np.einsum("ij,ij->i", offsets, offsets))
        vertices = first_vertices[order, np.newaxis] + np.arange(3)
        self.write_order_buffer(vertices.astype(np.uint32).reshape(-1))
        return True

    def write_order_buffer(self, indices: np.ndarray) -> None:
        if self.order_buffer is not None and self.order_buffer.size != indices.nbytes:
            self.order_buffer.destroy()
            self.order_buffer = None
        if self.order_buffer is None:
            self.order_buffer = self.material.gpu.device.create_buffer(
                size=indices.nbytes,
                usage=wgpu.BufferUsage.INDEX | wgpu.BufferUsage.COPY_DST,
            )
        self.material.gpu.queue.write_buffer(self.order_buffer, 0, indices)
        self.order_count = len(indices)

    def draw_passes(self, render_pass: RenderPass) -> None:
        if not self.ordered:
            super().draw_passes(render_pass)
            return
        self.draw_pass(
            render_pass, "main", DEFAULT, self.order_count, self.order_buffer,
        )


"""
The three passes a fill takes, see VDrawing.draw_fill. Named here rather than beside
PipelineState, since the stencil work below is a fact about filling a path and about nothing
else which is drawn.
"""
WINDING_COUNT = PipelineState(
    depth_test=False,
    depth_write=False,
    color_write=False,
    stencil_ops=(
        ("keep", "increment-wrap", "increment-wrap"),
        ("keep", "decrement-wrap", "decrement-wrap"),
    ),
)
FILL_BORDER = PipelineState(stencil_compare="equal", stencil_ops=(KEEP, KEEP))
WINDING_COVER = PipelineState(
    stencil_compare="not-equal",
    stencil_ops=2 * (("keep", "zero", "zero"),),
)


class VDrawing(Drawing):
    """
    A vectorized mobject is drawn by two shaders: a fill over the region its path encloses,
    and a stroke along the path itself.
    """
    merges = True
    # A curve begins at every other record, so one mobject of a run has to begin at an even
    # one, and every mobject holds an odd number of them
    records_between = 1
    fill_file = "fill.wgsl"
    stroke_file = "stroke.wgsl"
    # Each bezier's fill is two triangles, one covering the interior and one hugging the
    # curve, see fill.wgsl
    fill_verts_per_curve = 6
    # And its stroke a quad for each polyline segment the curve is broken into, the last few
    # going to the fan which rounds off a joint, see stroke.wgsl, whose MAX_STEPS this follows
    stroke_verts_per_curve = 6 * (32 - 1)
    # The one line of the stroke's source which the border compiles differently
    border_declaration = "const IS_FILL_BORDER: bool = false;"

    @classmethod
    def draws(cls, mobject: Mobject) -> bool:
        """Always, the two shaders being named here rather than by the mobject"""
        return True

    @classmethod
    def key(cls, mobject: Mobject) -> tuple:
        return (*super().key(mobject), mobject.shader_code_target)

    @classmethod
    def module_specs(cls, mobject: Mobject) -> list[ModuleSpec]:
        """
        Three modules from two sources: the border around a fill is the stroke shader with one
        constant compiled the other way.
        """
        source = read_shader_file(cls.stroke_file)
        declaration = cls.border_declaration
        if declaration not in source:
            raise ValueError(
                f"The stroke shader no longer declares {declaration!r}, so a fill's border "
                f"would be compiled as an ordinary stroke and vanish"
            )
        border = {declaration: declaration.replace("false", "true")}

        # A snippet is meant for one of the two sources where it names one of their fields,
        # since a snippet reading stroke_rgba would not compile against the fill
        target = mobject.shader_code_target
        replacements = mobject.shader_code_replacements
        nothing: dict[str, str] = dict()
        for_fill = replacements if target in (None, "fill") else nothing
        for_stroke = replacements if target in (None, "stroke") else nothing
        return [
            ("fill", cls.fill_file, for_fill),
            ("stroke", cls.stroke_file, for_stroke),
            ("border", cls.stroke_file, {**for_stroke, **border}),
        ]

    def __init__(self, material: Material, mobject: Mobject):
        super().__init__(material, mobject)
        # Whether the path encloses anything, and which way round its two passes go
        self.has_fill = False
        self.stroke_behind = False
        # Which mobjects this one's fill has been promised not to overlap, see
        # VMobject.draw_fills_together
        self.fill_group: Any = None

    def write_uniforms(self) -> bool:
        stroke_behind = self.mobject.stroke_behind
        fill_group = self.mobject.fill_group
        changed = super().write_uniforms()
        self.invalidated = self.invalidated or stroke_behind != self.stroke_behind \
            or fill_group is not self.fill_group
        self.stroke_behind = stroke_behind
        self.fill_group = fill_group
        # Whether there is anything to fill, worked out when the uniforms saying so change
        # rather than every frame. Without it a shape with no fill still pays for all three
        # fill passes, which in a scene of lines and text is most of the draws.
        if changed:
            has_fill = bool(
                self.uniforms["fill_rgba"][3] or self.uniforms["fill_rgba_end"][3]
            )
            self.invalidated = self.invalidated or has_fill != self.has_fill
            self.has_fill = has_fill
        return changed

    def can_follow(self, previous: Drawing) -> bool:
        """
        A fill counts its winding across the whole of a draw, so two filled mobjects may share
        one only where they do not overlap. Telling whether they do costs more than sharing
        saves, so it is left to the mobjects to say, see VMobject.draw_fills_together, and only
        those which have said so about the same group are gathered.

        Unfilled strokes are gathered whatever they promise, a stroke being drawn along its own
        path and reading nothing of what else the draw covers.
        """
        if not (
            super().can_follow(previous)
            and self.stroke_behind == previous.stroke_behind
        ):
            return False
        if not (self.has_fill or previous.has_fill):
            return True
        return self.fill_group is not None and self.fill_group is previous.fill_group

    def get_num_curves(self) -> int:
        # Consecutive beziers share an anchor, so n points make n // 2 curves
        return self.records // 2

    def stroke_vertices(self, extra_curves: int = 0) -> int:
        return self.stroke_verts_per_curve * (self.get_num_curves() + extra_curves)

    def draw_fill(self, render_pass: RenderPass) -> None:
        """
        Fill is drawn with a "stencil then cover" approach.

        The first pass rasterizes the fill triangles into the stencil buffer alone,
        incrementing for front facing triangles and decrementing for back facing ones. Facing
        being the sign of a triangle's area in screen space, each pixel ends up holding the
        winding number of the path around it, with no triangulation of the shape needed.

        The last pass draws those triangles again where that number is nonzero, zeroing the
        stencil as it goes, so each pixel is colored once by ordinary alpha blending and the
        buffer is left clean for whatever draws next.

        This works only because a drawing which fills holds a single mobject, see can_follow.
        Sharing passes between several would merge their windings into one region, and
        overlapping mobjects would color a shared pixel once between them rather than each
        blending in turn.
        """
        if not self.has_fill:
            return
        vertices = self.fill_verts_per_curve * self.get_num_curves()
        self.draw_pass(render_pass, "fill", WINDING_COUNT, vertices)
        self.draw_fill_border(render_pass)
        self.draw_pass(render_pass, "fill", WINDING_COVER, vertices)

    def draw_fill_border(self, render_pass: RenderPass) -> None:
        """
        Traces the boundary with a stroke in the fill color, which is what anti-aliases the
        fill, a stencil test being all or nothing. Drawn only where the winding number is
        zero, meaning outside the shape, so that its faded edge never blends on top of the
        fill and leaves a seam for partially transparent colors.

        One curve more than the path holds, since the chord closing the last subpath has no
        end-of-subpath curve to be drawn in place of, see stroke.wgsl.
        """
        self.draw_pass(
            render_pass, "border", FILL_BORDER, self.stroke_vertices(extra_curves=1),
        )

    def draw_stroke(self, render_pass: RenderPass) -> None:
        self.draw_pass(render_pass, "stroke", DEFAULT, self.stroke_vertices())

    def draw_passes(self, render_pass: RenderPass) -> None:
        if self.stroke_behind:
            self.draw_stroke(render_pass)
            self.draw_fill(render_pass)
        else:
            self.draw_fill(render_pass)
            self.draw_stroke(render_pass)
