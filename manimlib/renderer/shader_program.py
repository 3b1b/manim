from __future__ import annotations

import re

import numpy as np
import wgpu

from manimlib.renderer.renderer import COLOR_FORMAT
from manimlib.renderer.renderer import DEFAULT
from manimlib.renderer.renderer import FILL_BORDER
from manimlib.renderer.renderer import WINDING_COUNT
from manimlib.renderer.renderer import WINDING_COVER
from manimlib.renderer.renderer import get_bind_layouts
from manimlib.utils.shaders import DATA_BINDING
from manimlib.utils.shaders import FIRST_TEXTURE_BINDING
from manimlib.utils.shaders import MOBJECT_GROUP
from manimlib.utils.shaders import RESOURCE_GROUP
from manimlib.utils.shaders import SAMPLER_BINDING
from manimlib.utils.shaders import get_shader_code
from manimlib.utils.shaders import get_shader_module
from manimlib.utils.shaders import image_path_to_texture

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.mobject.mobject import Mobject
    from manimlib.utils.structured_array import StructuredArray
    from manimlib.renderer.renderer import DrawState, Renderer


# Color channels blend in the usual way, but the alpha channel takes the source's alpha
# whole, so that drawing something half transparent onto an opaque background leaves it
# opaque rather than eating into its alpha.
BLEND = {
    "color": {
        "src_factor": wgpu.BlendFactor.src_alpha,
        "dst_factor": wgpu.BlendFactor.one_minus_src_alpha,
        "operation": wgpu.BlendOperation.add,
    },
    "alpha": {
        "src_factor": wgpu.BlendFactor.one,
        "dst_factor": wgpu.BlendFactor.one_minus_src_alpha,
        "operation": wgpu.BlendOperation.add,
    },
}


class Slot(object):
    """
    One mobject's place in a frame: where its values went in the shared buffers, and everything
    else its draw needs to know.

    The write phase settles all of this and the draw phase reads nothing besides, so what gets
    drawn is decided before the pass opens, see DrawList. The last few belong to one kind of
    drawing each, which is cheaper than a slot per kind of mobject.
    """

    def __init__(self, program: Program, mobject: Mobject):
        self.program = program
        self.mobject = mobject
        # The arrays this mobject holds, which it binds once and thereafter only writes into
        self.data = mobject.data
        self.uniforms = mobject.uniforms
        # What the program was compiled from, so a mobject given new code gets a new program,
        # see DrawList.resolve
        self.replacements = mobject.shader_code_replacements
        # Where in the shared buffers this mobject's values went, no stretch yet being none
        self.uniform_offset = -1
        self.data_offset = -1
        # How many records this slot's draw covers, which for one drawing a run of mobjects
        # together is the whole run's, and for one drawn as part of a run is none
        self.records = 0
        self.depth_test = False
        # Made only for a mobject with images of its own, the rest reading the shared one's
        self.resource_bind_group = None
        self.shared_bind_group = None
        # Whether the write phase found anything a recorded draw would have baked in to have
        # moved, which for a slot nothing has drawn yet is everything, see DrawList
        self.resequenced = True
        # Whether the path encloses anything, and which way round its two passes go, see
        # VProgram
        self.has_fill = False
        self.stroke_behind = False
        # The mobjects this one is drawn together with, itself first, or none where it is
        # drawn on its own, see DrawList.group
        self.members: list[Slot] | None = None
        # The order a surface's triangles are drawn in, where it is drawn in one, see
        # SurfaceProgram
        self.order_buffer = None
        self.order_count = 0
        self.ordered = False


class Program(object):
    """
    Everything about drawing which does not vary between two mobjects of a kind: the modules
    they are drawn by, what they may bind, the buffers their values are gathered in, and the
    passes each of them takes.

    A mobject says which of these draws it by its program_class, and one program stands behind
    however many mobjects agree about the rest, see DrawList.program_for. Per mobject there is
    only a Slot.

    No shader is handed vertex attributes. Each reads the records of its shared buffer itself,
    as a flat array of floats indexed by the vertex being drawn, and expands every record into
    verts_per_record vertices, always triangles, see inserts/read_data.wgsl.
    """
    # Whether several of these mobjects may be drawn by one draw, which asks of their shader
    # that it read every record on the record's own terms, see DrawList.group
    merges = False
    # How many records hold one mobject of a run apart from the next
    records_between = 0

    @classmethod
    def key(cls, mobject: Mobject) -> tuple:
        """What two mobjects have to agree about to be drawn by the same program"""
        return (
            cls,
            mobject.shader_file,
            mobject.data.dtype,
            mobject.uniforms.dtype,
            tuple(mobject.texture_paths.items()),
            tuple(mobject.shader_code_replacements.items()),
            mobject.verts_per_record,
        )

    def __init__(self, renderer: Renderer, mobject: Mobject):
        self.renderer = renderer
        self.device = renderer.device
        self.verts_per_record = mobject.verts_per_record
        self.texture_paths = dict(mobject.texture_paths)
        self.init_bindings(mobject)
        self.init_program(mobject)
        self.init_textures()

    # What the shader is told about a mobject, and what it may bind

    def init_bindings(self, mobject: Mobject) -> None:
        self.resource_layout, self.pipeline_layout = get_bind_layouts(
            self.device, self.renderer.frame_layout, self.renderer.mobject_layout,
            len(self.texture_paths),
        )
        # Where these mobjects' values go each frame, see SharedBuffer
        self.record_size = mobject.data.dtype.itemsize
        self.uniform_buffer = self.renderer.uniform_buffer_for(mobject.uniforms.array.nbytes)
        self.data_buffer = self.renderer.data_buffer_for(self.record_size)

    def init_program(self, mobject: Mobject) -> None:
        # A mobject naming no shader, a group say, has nothing to be drawn by
        self.module = None
        self.draws = bool(mobject.shader_file)
        if not self.draws:
            return
        self.module = get_shader_module(
            self.device,
            self.get_code(mobject, mobject.shader_file, mobject.shader_code_replacements),
        )

    def get_code(self, mobject: Mobject, filename: str, replacements: dict[str, str]) -> str:
        """
        A shader's source, told where the fields of one of these mobjects' records sit and what
        it holds for the whole of itself, which is all the source depends on and so is what it
        gets cached under.
        """
        dtype = mobject.data.dtype
        layout = (
            dtype.itemsize // 4,
            tuple((name, dtype.fields[name][1] // 4) for name in dtype.names),
        )
        code = get_shader_code(
            filename, layout, mobject.uniforms.dtype, tuple(self.texture_paths),
        )
        for old, new in replacements.items():
            code = re.sub(old, new, code)
        return code

    def init_textures(self) -> None:
        self.textures = [
            image_path_to_texture(path, self.device)
            for path in self.texture_paths.values()
        ]
        self.sampler = None
        if self.texture_paths:
            self.sampler = self.device.create_sampler(
                mag_filter=wgpu.FilterMode.linear, min_filter=wgpu.FilterMode.linear,
            )

    def get_resource_bind_group(self, slot: Slot):
        """
        What a mobject's records and images are read through. Without images of its own it
        reads the shared group, which serves every mobject of its size; with them it needs one
        of its own, made again whenever the shared one is.
        """
        shared = self.data_buffer
        if not self.textures:
            return shared.bind_group
        if slot.shared_bind_group is not shared.bind_group:
            slot.shared_bind_group = shared.bind_group
            entries = [{"binding": DATA_BINDING, "resource": {
                "buffer": shared.buffer, "offset": 0, "size": shared.window,
            }}]
            entries.append({"binding": SAMPLER_BINDING, "resource": self.sampler})
            for index, texture in enumerate(self.textures):
                entries.append({
                    "binding": FIRST_TEXTURE_BINDING + index,
                    "resource": texture.create_view(),
                })
            slot.resource_bind_group = self.device.create_bind_group(
                layout=self.resource_layout, entries=entries,
            )
        return slot.resource_bind_group

    # Sending what the draw will read

    def write_style(self, slot: Slot) -> bool:
        """
        A mobject's uniforms into the buffer they share, along with everything its draw needs
        to know besides where its records went. Settled first, since which mobjects may be
        drawn together depends on it, see DrawList.group, and says whether the style moved.

        Noting on the way whether any of it moved, which every comparison here was making
        anyway, so that a recorded draw knows to be made again.
        """
        depth_test = slot.mobject.depth_test
        slot.resequenced = depth_test != slot.depth_test
        slot.depth_test = depth_test
        return self.write_uniforms(slot)

    def write_records(self, leader: Slot) -> None:
        """
        A mobject's records into a stretch of the shared buffer, or, where it draws a run of
        mobjects together, all of theirs into one stretch, back to back with records between
        them holding each one's last record over again: for a vectorized mobject that repeat
        is a null curve, which is already how one mobject's own subpaths are held apart, so
        the run reads as one path and the shaders need know nothing of any of this.

        Either way the mobject which draws is given the whole stretch.
        """
        run = leader.members
        if run is None:
            data = leader.data
            records = len(data)
            offset = self.data_buffer.claim(data.array.nbytes)
            changed = data.has_changed(observer=leader)
            moved = offset != leader.data_offset or records != leader.records
            if changed or moved:
                self.data_buffer.put(offset, data.bytes)
            leader.data_offset = offset
            leader.records = records
            leader.resequenced = leader.resequenced or moved
            return

        sizes = [len(slot.data) for slot in run]
        records = sum(sizes) + self.records_between * (len(run) - 1)
        offset = self.data_buffer.claim(records * self.record_size)
        moved = offset != leader.data_offset or records != leader.records
        at = offset
        last = len(run) - 1
        for index, (slot, size) in enumerate(zip(run, sizes)):
            data = slot.data
            changed = data.has_changed(observer=slot)
            if changed or at != slot.data_offset:
                self.data_buffer.put(at, data.bytes)
                if index != last:
                    self.write_gap(at + size * self.record_size, data)
            slot.data_offset = at
            at += (size + self.records_between) * self.record_size
        leader.records = records
        leader.resequenced = leader.resequenced or moved

    def write_gap(self, offset: int, data: StructuredArray) -> None:
        """The last record over again, as many times as hold one mobject apart from the next"""
        last = data.bytes[-self.record_size:]
        for step in range(self.records_between):
            self.data_buffer.put(offset + step * self.record_size, last)

    def write_uniforms(self, slot: Slot) -> bool:
        """
        Into a stretch of the shared buffer, saying whether the uniforms had changed since the
        last frame asked. Every frame takes a stretch, one lasting only as long as the frame.

        The answer is returned rather than left to be asked again, since asking counts as
        having looked, see StructuredArray.has_changed.
        """
        uniforms = slot.uniforms
        changed = uniforms.has_changed(observer=slot)
        offset = self.uniform_buffer.claim(uniforms.array.nbytes)
        moved = offset != slot.uniform_offset
        # A scene which is not changing hands its stretches out in the same order every frame,
        # so a mobject whose uniforms have not moved usually finds its values already there
        if changed or moved:
            self.uniform_buffer.put(offset, uniforms.bytes)
        slot.resequenced = slot.resequenced or moved
        slot.uniform_offset = offset
        return changed

    # Drawing

    def get_pipeline(self, state: DrawState, module, depth_test: bool):
        """
        The pipeline for one of these mobjects' passes. The renderer holds them, so every
        mobject of a kind draws through the same ones rather than building its own.
        """
        samples = self.renderer.samples
        # The module already settles which images there are, and so which layout a pipeline
        # reading them wants
        key = (module, state, depth_test, samples)
        pipeline = self.renderer.pipelines.get(key)
        if pipeline is None:
            pipeline = self.renderer.pipelines[key] = self.device.create_render_pipeline(
                layout=self.pipeline_layout,
                vertex={"module": module, "entry_point": "vs_main", "buffers": []},
                fragment={
                    "module": module,
                    "entry_point": "fs_main",
                    "targets": [{
                        "format": COLOR_FORMAT,
                        "blend": BLEND,
                        "write_mask": state.color_write_mask,
                    }],
                },
                primitive={"topology": wgpu.PrimitiveTopology.triangle_list},
                depth_stencil=state.depth_stencil_descriptor(depth_test),
                multisample={"count": samples},
            )
        return pipeline

    def draw(self, slot: Slot, state: DrawState, module, vertices: int, indices=None) -> None:
        """
        One pass over a mobject's records, taking them in the order a buffer of indices gives
        where it is handed one, each index being the vertex the shader is to work out.
        """
        self.renderer.use_pipeline(self.get_pipeline(state, module, slot.depth_test))
        if indices is None:
            self.renderer.pass_.draw(vertices)
        else:
            self.renderer.pass_.set_index_buffer(indices, wgpu.IndexFormat.uint32)
            self.renderer.pass_.draw_indexed(vertices)

    def render(self, slot: Slot) -> None:
        """
        Every pass a mobject takes. What they read is bound once here, all of them reading the
        same two stretches whatever program runs over them.
        """
        self.renderer.bind(
            MOBJECT_GROUP, self.uniform_buffer.bind_group, (slot.uniform_offset,),
        )
        self.renderer.bind(
            RESOURCE_GROUP, self.get_resource_bind_group(slot), (slot.data_offset,),
        )
        self.draw_passes(slot)

    def draw_passes(self, slot: Slot) -> None:
        """Every pass this kind of mobject takes, which for most kinds is the one"""
        self.draw(slot, DEFAULT, self.module, self.verts_per_record * slot.records)


class SurfaceProgram(Program):
    """
    An opaque surface is drawn in one pass and left to the depth test, which decides what
    hides what however its triangles arrive.

    One which can be seen through cannot: blending is not commutative, so what lies behind has
    to be drawn first. Its triangles are drawn furthest from the camera first, through a buffer
    of indices written before the frame's pass opens, see Surface.is_opaque.
    """
    def write_style(self, slot: Slot) -> bool:
        restyled = super().write_style(slot)
        surface = slot.mobject
        was, count = slot.ordered, slot.order_count
        # Ordering the triangles writes a buffer of its own, so it belongs among the writes
        sort = surface.sort_to_camera or not surface.is_opaque()
        slot.ordered = sort and self.order_triangles_by_depth(slot)
        slot.resequenced = slot.resequenced or slot.ordered != was \
            or slot.order_count != count
        return restyled

    def order_triangles_by_depth(self, slot: Slot) -> bool:
        """
        Lists the vertices of every triangle of the mesh, three to each, those furthest from
        the camera first, in a buffer to be drawn through. False if there are no triangles.
        """
        first_vertices, middles = self.get_triangles(slot.mobject)
        if len(first_vertices) == 0:
            return False
        camera_position = self.renderer.frame_uniforms["camera_position"]
        offsets = middles - np.array(camera_position)
        order = np.argsort(-np.einsum("ij,ij->i", offsets, offsets))
        vertices = first_vertices[order, np.newaxis] + np.arange(3)
        self.write_order_buffer(slot, vertices.astype(np.uint32).reshape(-1))
        return True

    def get_triangles(self, surface: Mobject):
        """
        Which vertex each triangle of the mesh starts at, and where the middle of it sits.

        A grid of points is expanded into two triangles per square, taking the corners the
        vertex shader gives them, see inserts/surface_mesh.wgsl. Records which are no grid, as
        an imported mesh's are, are already three to a triangle.

        The middle rather than a corner, cheap as a corner would be, since which corner comes
        first is whatever the parametrization wound first, and the picture must not depend on
        that.
        """
        points = surface.data["point"]
        nu, nv = surface.uniforms["resolution"].astype(int)

        if nu < 2 or nv < 2:
            triangles = len(points) // 3
            corners = points[:3 * triangles].reshape((triangles, 3, 3))
            return 3 * np.arange(triangles), corners.mean(axis=1)

        grid = points.reshape((nu, nv, 3))
        middles = np.array([
            grid[:-1, :-1] + grid[1:, :-1] + grid[:-1, 1:],
            grid[:-1, 1:] + grid[1:, :-1] + grid[1:, 1:],
        ]).reshape((-1, 3)) / 3
        squares = np.arange(nu - 1)[:, np.newaxis] * nv + np.arange(nv - 1)
        firsts = 6 * squares + np.array([[[0]], [[3]]])
        return firsts.reshape(-1), middles

    def write_order_buffer(self, slot: Slot, indices: np.ndarray) -> None:
        if slot.order_buffer is not None and slot.order_buffer.size != indices.nbytes:
            slot.order_buffer.destroy()
            slot.order_buffer = None
        if slot.order_buffer is None:
            slot.order_buffer = self.device.create_buffer(
                size=indices.nbytes,
                usage=wgpu.BufferUsage.INDEX | wgpu.BufferUsage.COPY_DST,
            )
        self.renderer.queue.write_buffer(slot.order_buffer, 0, indices)
        slot.order_count = len(indices)

    def draw_passes(self, slot: Slot) -> None:
        if not slot.ordered:
            super().draw_passes(slot)
            return
        self.draw(slot, DEFAULT, self.module, slot.order_count, slot.order_buffer)


class VProgram(Program):
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
    def key(cls, mobject: Mobject) -> tuple:
        return (*super().key(mobject), mobject.shader_program_type)

    def init_program(self, mobject: Mobject) -> None:
        """
        Three modules from two sources: the border around a fill is the stroke shader with one
        constant compiled the other way.
        """
        program_type = mobject.shader_program_type
        nothing: dict[str, str] = dict()
        replacements = mobject.shader_code_replacements
        # A snippet is meant for one of the two sources where it names one of their fields,
        # since a snippet reading stroke_rgba would not compile against the fill
        fill_code = self.get_code(
            mobject, self.fill_file,
            replacements if program_type in (None, "fill") else nothing,
        )
        stroke_code = self.get_code(
            mobject, self.stroke_file,
            replacements if program_type in (None, "stroke") else nothing,
        )
        declaration = self.border_declaration
        border_code = stroke_code.replace(declaration, declaration.replace("false", "true"))
        if border_code == stroke_code:
            raise ValueError(
                f"The stroke shader no longer declares {declaration!r}, so a fill's border "
                f"would be compiled as an ordinary stroke and vanish"
            )
        self.fill_module = get_shader_module(self.device, fill_code)
        self.stroke_module = get_shader_module(self.device, stroke_code)
        self.border_module = get_shader_module(self.device, border_code)
        self.draws = True

    def write_style(self, slot: Slot) -> bool:
        restyled = super().write_style(slot)
        stroke_behind = slot.mobject.stroke_behind
        slot.resequenced = slot.resequenced or stroke_behind != slot.stroke_behind
        slot.stroke_behind = stroke_behind
        return restyled

    def write_uniforms(self, slot: Slot) -> bool:
        # Whether there is anything to fill, worked out when the uniforms saying so change
        # rather than every frame. Without it a shape with no fill still pays for all three
        # fill passes, which in a scene of lines and text is most of the draws.
        if not super().write_uniforms(slot):
            return False
        uniforms = slot.uniforms
        has_fill = bool(uniforms["fill_rgba"][3] or uniforms["fill_rgba_end"][3])
        slot.resequenced = slot.resequenced or has_fill != slot.has_fill
        slot.has_fill = has_fill
        return True

    def get_num_curves(self, slot: Slot) -> int:
        # Consecutive beziers share an anchor, so n points make n // 2 curves
        return slot.records // 2

    def draw_fill(self, slot: Slot) -> None:
        """
        Fill is drawn with a "stencil then cover" approach.

        The first pass rasterizes the fill triangles into the stencil buffer alone,
        incrementing for front facing triangles and decrementing for back facing ones. Facing
        being the sign of a triangle's area in screen space, each pixel ends up holding the
        winding number of the path around it, with no triangulation of the shape needed.

        The last pass draws those triangles again where that number is nonzero, zeroing the
        stencil as it goes, so each pixel is colored once by ordinary alpha blending and the
        buffer is left clean for whatever draws next.

        This works only because a slot holds a single mobject. Sharing passes between several
        would merge their windings into one region, and overlapping mobjects would color a
        shared pixel once between them rather than each blending in turn.
        """
        if not slot.has_fill:
            return
        vertices = self.fill_verts_per_curve * self.get_num_curves(slot)
        self.draw(slot, WINDING_COUNT, self.fill_module, vertices)
        self.draw_fill_border(slot)
        self.draw(slot, WINDING_COVER, self.fill_module, vertices)

    def draw_fill_border(self, slot: Slot) -> None:
        """
        Traces the boundary with a stroke in the fill color, which is what anti-aliases the
        fill, a stencil test being all or nothing. Drawn only where the winding number is
        zero, meaning outside the shape, so that its faded edge never blends on top of the
        fill and leaves a seam for partially transparent colors.

        One curve more than the path holds, since the chord closing the last subpath has no
        end-of-subpath curve to be drawn in place of, see stroke.wgsl.
        """
        self.draw(
            slot, FILL_BORDER, self.border_module, self.stroke_vertices(slot, extra_curves=1),
        )

    def draw_stroke(self, slot: Slot) -> None:
        self.draw(slot, DEFAULT, self.stroke_module, self.stroke_vertices(slot))

    def stroke_vertices(self, slot: Slot, extra_curves: int = 0) -> int:
        return self.stroke_verts_per_curve * (self.get_num_curves(slot) + extra_curves)

    def draw_passes(self, slot: Slot) -> None:
        if slot.stroke_behind:
            self.draw_stroke(slot)
            self.draw_fill(slot)
        else:
            self.draw_fill(slot)
            self.draw_stroke(slot)
