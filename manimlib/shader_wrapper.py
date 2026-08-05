from __future__ import annotations

import re

import wgpu

import numpy as np

from manimlib.renderer import COLOR_FORMAT
from manimlib.renderer import DEFAULT
from manimlib.renderer import FILL_BORDER
from manimlib.renderer import WINDING_COUNT
from manimlib.renderer import WINDING_COVER
from manimlib.renderer import get_bind_layouts
from manimlib.utils.shaders import DATA_BINDING
from manimlib.utils.shaders import FIRST_TEXTURE_BINDING
from manimlib.utils.shaders import get_shader_code
from manimlib.utils.shaders import get_shader_module
from manimlib.utils.shaders import image_path_to_texture
from manimlib.utils.shaders import MOBJECT_GROUP
from manimlib.utils.shaders import RESOURCE_GROUP
from manimlib.utils.shaders import SAMPLER_BINDING

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional
    from manimlib.renderer import DrawState, Renderer
    from manimlib.utils.shaders import Uniforms
    from manimlib.utils.structured_array import StructuredArray


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


class ShaderWrapper(object):
    """
    One mobject's side of the gpu: the module it is drawn by, where in the arenas its values
    are, and the drawing itself.

    A mobject names one shader file, compiled once between all the mobjects naming it, and
    hands over the two arrays it keeps: its data, a record per point, and its uniforms, one
    value for the whole of it. Neither gets a buffer of its own; both go in a stretch of an
    arena shared with every mobject whose values are the same size, and what a wrapper holds
    of them is where that stretch was, see Arena.

    No shader is handed vertex attributes. Each reads the records of its arena itself, as a
    flat array of floats indexed by the vertex being drawn, and expands every record into
    verts_per_record vertices, always triangles, see inserts/read_data.wgsl.

    Drawing comes in two halves, so that every write a frame makes lands before any of its
    draws: write_buffers puts the values where the draw will read them, and render binds and
    draws. There is one wrapper to a mobject rather than to a kind of mobject, which is what
    lets a fill count its own winding in the stencil buffer without the mobject beside it
    joining in.
    """

    def __init__(
        self,
        renderer: Renderer,
        mobject_data: StructuredArray,
        mobject_uniforms: Uniforms,
        shader_file: Optional[str] = None,
        texture_paths: Optional[dict[str, str]] = None,
        depth_test: bool = False,
        code_replacements: dict[str, str] = dict(),
        verts_per_record: int = 0,
    ):
        self.renderer = renderer
        self.device = renderer.device
        self.mobject_data = mobject_data
        self.mobject_uniforms = mobject_uniforms
        self.shader_file = shader_file
        self.texture_paths = texture_paths or dict()
        self.depth_test = depth_test
        self.verts_per_record = verts_per_record

        self.init_layouts()
        self.init_program()
        for old, new in code_replacements.items():
            self.replace_code(old, new)
        self.init_resources()

    def __deepcopy__(self, memo):
        # Don't allow deepcopies, e.g. if the mobject with this ShaderWrapper as an
        # attribute gets copied. Returning None means the parent object with this
        # ShaderWrapper as an attribute should smoothly handle this case.
        return None

    # What the shader is told about the mobject, and what it may bind

    def init_layouts(self) -> None:
        """
        Where the fields of one of this mobject's records sit. Together with its uniform dtype
        this is all the generated shader source depends on, so it is the key that source is
        cached under.
        """
        dtype = self.mobject_data.dtype
        self.data_layout = (
            dtype.itemsize // 4,
            tuple((name, dtype.fields[name][1] // 4) for name in dtype.names),
        )
        self.resource_layout, self.pipeline_layout = get_bind_layouts(
            self.device, self.renderer.frame_layout, self.renderer.mobject_layout,
            len(self.texture_paths),
        )
        # Where this mobject's values go each frame, see Arena
        self.uniform_arena = self.renderer.uniform_arena_for(
            self.mobject_uniforms.array.nbytes,
        )
        self.data_arena = self.renderer.data_arena_for(dtype.itemsize)

    def init_program(self) -> None:
        # A mobject naming no shader, a group say, has nothing to be drawn by
        self.code = self.get_code(self.shader_file) if self.shader_file else None
        self.module = None if self.code is None else get_shader_module(self.device, self.code)
        self.modules = [] if self.module is None else [self.module]

    def get_code(self, filename: str) -> str | None:
        return get_shader_code(
            filename,
            self.data_layout,
            self.mobject_uniforms.dtype,
            tuple(self.texture_paths),
        )

    def replace_code(self, old: str, new: str) -> None:
        self.code = re.sub(old, new, self.code)
        self.module = get_shader_module(self.device, self.code)
        self.modules = [self.module]

    def init_resources(self) -> None:
        # Where in their arenas this mobject's values went, no stretch yet being none
        self.uniform_offset = -1
        self.data_offset = -1
        # Made only for a mobject with images of its own, the rest reading the arena's
        self.resource_bind_group = None
        self.arena_bind_group = None
        self.textures = [
            image_path_to_texture(path, self.device)
            for path in self.texture_paths.values()
        ]
        self.sampler = None
        if self.texture_paths:
            self.sampler = self.device.create_sampler(
                mag_filter=wgpu.FilterMode.linear, min_filter=wgpu.FilterMode.linear,
            )

    # Sending what the draw will read

    def write_buffers(self) -> None:
        """
        The mobject's two arrays into their arenas. Every wrapper of a frame does this before
        any of them draws, a write reaching the gpu partway through a pass having no say over
        which draws see it, see Camera.capture.
        """
        if not self.modules:
            return
        self.write_data_buffer()
        self.write_uniform_buffer()

    def write_data_buffer(self) -> None:
        """Into a stretch of the arena, remembering where so the draw can be given it"""
        data = self.mobject_data
        if len(data.array) == 0:
            return
        changed = data.has_changed(observer=self)
        offset = self.data_arena.claim_stretch(data.array.nbytes)
        if changed or offset != self.data_offset:
            self.data_arena.put(offset, data.bytes)
        self.data_offset = offset

    def write_uniform_buffer(self) -> bool:
        """
        Into a row of the arena, saying whether the uniforms had changed since the last frame
        asked. Every frame takes a row, one lasting only as long as the frame.

        The answer is returned rather than left to be asked again, since asking counts as
        having looked, see StructuredArray.has_changed.
        """
        uniforms = self.mobject_uniforms
        changed = uniforms.has_changed(observer=self)
        offset = self.uniform_arena.next_row()
        # A scene which is not changing hands its rows out in the same order every frame, so
        # a mobject whose uniforms have not moved usually finds its own values already there
        if changed or offset != self.uniform_offset:
            self.uniform_arena.put(offset, uniforms.bytes)
        self.uniform_offset = offset
        return changed

    def get_resource_bind_group(self):
        """
        What this mobject's records and images are read through. Without images of its own it
        reads the arena's group, shared with every mobject of its size; with them it needs one
        of its own, made again whenever the arena makes its own again.
        """
        arena = self.data_arena
        if not self.textures:
            return arena.bind_group
        if self.arena_bind_group is not arena.bind_group:
            self.arena_bind_group = arena.bind_group
            entries = [{"binding": DATA_BINDING, "resource": {
                "buffer": arena.buffer, "offset": 0, "size": arena.window,
            }}]
            entries.append({"binding": SAMPLER_BINDING, "resource": self.sampler})
            for index, texture in enumerate(self.textures):
                entries.append({
                    "binding": FIRST_TEXTURE_BINDING + index,
                    "resource": texture.create_view(),
                })
            self.resource_bind_group = self.device.create_bind_group(
                layout=self.resource_layout, entries=entries,
            )
        return self.resource_bind_group

    # Drawing

    def get_pipeline(self, state: DrawState, module):
        """
        The pipeline for one of this mobject's passes. The renderer holds them, so every
        mobject of a kind draws through the same ones rather than building its own.
        """
        samples = self.renderer.samples
        # The module already settles which images there are, and so which layout a pipeline
        # reading them wants
        key = (module, state, self.depth_test, samples)

        def build():
            return self.device.create_render_pipeline(
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
                depth_stencil=state.depth_stencil_descriptor(self.depth_test),
                multisample={"count": samples},
            )

        return self.renderer.get_pipeline(key, build)

    def draw(self, state: DrawState, module, vertices: int) -> None:
        """One pass over this mobject's records"""
        self.renderer.use_pipeline(self.get_pipeline(state, module))
        self.renderer.pass_.draw(vertices)

    def draw_through(self, state: DrawState, module, indices, count: int) -> None:
        """
        One pass over this mobject's records in the order a buffer of indices gives, each
        index being the vertex the shader is to work out.
        """
        self.renderer.use_pipeline(self.get_pipeline(state, module))
        self.renderer.pass_.set_index_buffer(indices, wgpu.IndexFormat.uint32)
        self.renderer.pass_.draw_indexed(count)

    def render(self) -> None:
        """
        Every pass this mobject takes. What they read is bound once here, all of them reading
        the same two stretches whatever program runs over them.
        """
        if not self.modules or len(self.mobject_data) == 0:
            return
        self.renderer.bind(
            MOBJECT_GROUP, self.uniform_arena.bind_group, (self.uniform_offset,),
        )
        self.renderer.bind(
            RESOURCE_GROUP, self.get_resource_bind_group(), (self.data_offset,),
        )
        self.draw_passes()

    def draw_passes(self) -> None:
        """Every pass this kind of mobject takes, which for most kinds is the one"""
        self.draw(DEFAULT, self.module, self.verts_per_record * len(self.mobject_data))


class SurfaceShaderWrapper(ShaderWrapper):
    """
    An opaque surface is drawn in one pass and left to the depth test, which decides what
    hides what however its triangles arrive.

    One which can be seen through cannot: blending is not commutative, so what lies behind has
    to be drawn first. Its triangles are drawn furthest from the camera first, through a buffer
    of indices written before the frame's pass opens, see Surface.is_opaque.
    """

    def __init__(self, *args, sort_to_camera: bool = False, **kwargs):
        self.sort_to_camera = sort_to_camera
        super().__init__(*args, **kwargs)

    def init_resources(self) -> None:
        super().init_resources()
        self.order_buffer = None
        self.order_count = 0
        self.ordered = False

    def write_buffers(self) -> None:
        super().write_buffers()
        # Ordering the triangles writes a buffer of its own, so it belongs among the writes
        self.ordered = self.sort_to_camera and self.order_triangles_by_depth()

    def order_triangles_by_depth(self) -> bool:
        """
        Lists the vertices of every triangle of the mesh, three to each, those furthest from
        the camera first, in a buffer to be drawn through. False if there are no triangles.
        """
        first_vertices, middles = self.get_triangles()
        if len(first_vertices) == 0:
            return False
        camera_position = self.renderer.frame_uniforms["camera_position"]
        offsets = middles - np.array(camera_position)
        order = np.argsort(-np.einsum("ij,ij->i", offsets, offsets))
        vertices = first_vertices[order, np.newaxis] + np.arange(3)
        self.write_order_buffer(vertices.astype(np.uint32).reshape(-1))
        return True

    def get_triangles(self):
        """
        Which vertex each triangle of the mesh starts at, and where the middle of it sits.

        A grid of points is expanded into two triangles per square, taking the corners the
        vertex shader gives them, see inserts/surface_mesh.wgsl. Records which are no grid, as
        an imported mesh's are, are already three to a triangle.

        The middle rather than a corner, cheap as a corner would be, since which corner comes
        first is whatever the parametrization wound first, and the picture must not depend on
        that.
        """
        points = self.mobject_data["point"]
        nu, nv = self.mobject_uniforms["resolution"].astype(int)

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

    def write_order_buffer(self, indices: np.ndarray) -> None:
        if self.order_buffer is not None and self.order_buffer.size != indices.nbytes:
            self.order_buffer.destroy()
            self.order_buffer = None
        if self.order_buffer is None:
            self.order_buffer = self.device.create_buffer(
                size=indices.nbytes,
                usage=wgpu.BufferUsage.INDEX | wgpu.BufferUsage.COPY_DST,
            )
        self.renderer.queue.write_buffer(self.order_buffer, 0, indices)
        self.order_count = len(indices)

    def draw_passes(self) -> None:
        if self.ordered:
            self.draw_through(DEFAULT, self.module, self.order_buffer, self.order_count)
        else:
            self.draw(DEFAULT, self.module, self.verts_per_record * len(self.mobject_data))


class VShaderWrapper(ShaderWrapper):
    """
    A vectorized mobject is drawn by two shaders: a fill over the region its path encloses,
    and a stroke along the path itself.
    """
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

    def __init__(
        self,
        *args,
        program_type: str | None = None,
        stroke_behind: bool = False,
        **kwargs,
    ):
        self.stroke_behind = stroke_behind
        # Which of the two sources a code replacement is meant for, where it is meant for
        # one of them: a snippet reading stroke_rgba would not compile against the fill
        self.program_type = program_type
        super().__init__(*args, **kwargs)

    def init_program(self) -> None:
        self.fill_code = self.get_code(self.fill_file)
        self.stroke_code = self.get_code(self.stroke_file)
        self.build_modules()

    def init_resources(self) -> None:
        super().init_resources()
        self.has_fill = False

    def write_uniform_buffer(self) -> bool:
        # Whether there is anything to fill, worked out when the uniforms saying so change
        # rather than every frame. Without it a shape with no fill still pays for all three
        # fill passes, which in a scene of lines and text is most of the draws.
        if not super().write_uniform_buffer():
            return False
        uniforms = self.mobject_uniforms
        self.has_fill = bool(uniforms["fill_rgba"][3] or uniforms["fill_rgba_end"][3])
        return True

    def build_modules(self) -> None:
        """
        Three modules from two sources: the border around a fill is the stroke shader with one
        constant compiled the other way.
        """
        border_declaration = self.border_declaration
        border_code = self.stroke_code.replace(
            border_declaration, border_declaration.replace("false", "true"),
        )
        if border_code == self.stroke_code:
            raise ValueError(
                f"The stroke shader no longer declares {border_declaration!r}, so a fill's "
                f"border would be compiled as an ordinary stroke and vanish"
            )
        self.fill_module = get_shader_module(self.device, self.fill_code)
        self.stroke_module = get_shader_module(self.device, self.stroke_code)
        self.border_module = get_shader_module(self.device, border_code)
        self.modules = [self.fill_module, self.stroke_module, self.border_module]

    def replace_code(self, old: str, new: str) -> None:
        if self.program_type in (None, "fill"):
            self.fill_code = re.sub(old, new, self.fill_code)
        if self.program_type in (None, "stroke"):
            self.stroke_code = re.sub(old, new, self.stroke_code)
        self.build_modules()

    def get_num_curves(self) -> int:
        # Consecutive beziers share an anchor, so n points make n // 2 curves
        return len(self.mobject_data) // 2

    def draw_fill(self) -> None:
        """
        Fill is drawn with a "stencil then cover" approach.

        The first pass rasterizes the fill triangles into the stencil buffer alone,
        incrementing for front facing triangles and decrementing for back facing ones. Facing
        being the sign of a triangle's area in screen space, each pixel ends up holding the
        winding number of the path around it, with no triangulation of the shape needed.

        The last pass draws those triangles again where that number is nonzero, zeroing the
        stencil as it goes, so each pixel is colored once by ordinary alpha blending and the
        buffer is left clean for whatever draws next.

        This works only because a wrapper holds a single mobject. Sharing passes between
        several would merge their windings into one region, and overlapping mobjects would
        color a shared pixel once between them rather than each blending in turn.
        """
        if not self.has_fill:
            return
        vertices = self.fill_verts_per_curve * self.get_num_curves()
        self.draw(WINDING_COUNT, self.fill_module, vertices)
        self.draw_fill_border()
        self.draw(WINDING_COVER, self.fill_module, vertices)

    def draw_fill_border(self) -> None:
        """
        Traces the boundary with a stroke in the fill color, which is what anti-aliases the
        fill, a stencil test being all or nothing. Drawn only where the winding number is
        zero, meaning outside the shape, so that its faded edge never blends on top of the
        fill and leaves a seam for partially transparent colors.

        One curve more than the path holds, since the chord closing the last subpath has no
        end-of-subpath curve to be drawn in place of, see stroke.wgsl.
        """
        self.draw(FILL_BORDER, self.border_module, self.stroke_vertices(extra_curves=1))

    def draw_stroke(self) -> None:
        self.draw(DEFAULT, self.stroke_module, self.stroke_vertices())

    def stroke_vertices(self, extra_curves: int = 0) -> int:
        return self.stroke_verts_per_curve * (self.get_num_curves() + extra_curves)

    def draw_passes(self) -> None:
        if self.stroke_behind:
            self.draw_stroke()
            self.draw_fill()
        else:
            self.draw_fill()
            self.draw_stroke()
