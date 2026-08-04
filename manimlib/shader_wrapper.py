from __future__ import annotations

import os
import re
from functools import lru_cache

import wgpu

import numpy as np

from manimlib.renderer import COLOR_FORMAT
from manimlib.renderer import CULL_BACK
from manimlib.renderer import CULL_FRONT
from manimlib.renderer import DEFAULT
from manimlib.renderer import FILL_BORDER
from manimlib.renderer import WINDING_COUNT
from manimlib.renderer import WINDING_COVER
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


@lru_cache()
def get_bind_layouts(device, frame_layout, texture_count: int):
    """
    What a shader may bind: the values for the whole frame, the values for the mobject being
    drawn, and its records along with a texture for each image its kind names.

    None of that varies between two mobjects of a kind, so it is made once for each number
    of textures a kind might have. Which matters: a pipeline is built against these, so
    making them per mobject would have every mobject compiling pipelines of its own.
    """
    resource_entries = [{
        "binding": DATA_BINDING,
        "visibility": wgpu.ShaderStage.VERTEX | wgpu.ShaderStage.FRAGMENT,
        "buffer": {"type": wgpu.BufferBindingType.read_only_storage},
    }]
    if texture_count:
        resource_entries.append({
            "binding": SAMPLER_BINDING,
            "visibility": wgpu.ShaderStage.FRAGMENT,
            "sampler": {"type": wgpu.SamplerBindingType.filtering},
        })
        resource_entries += [{
            "binding": FIRST_TEXTURE_BINDING + index,
            "visibility": wgpu.ShaderStage.FRAGMENT,
            "texture": {"sample_type": wgpu.TextureSampleType.float},
        } for index in range(texture_count)]

    mobject_layout = device.create_bind_group_layout(entries=[{
        "binding": 0,
        "visibility": wgpu.ShaderStage.VERTEX | wgpu.ShaderStage.FRAGMENT,
        "buffer": {"type": wgpu.BufferBindingType.uniform},
    }])
    resource_layout = device.create_bind_group_layout(entries=resource_entries)
    pipeline_layout = device.create_pipeline_layout(bind_group_layouts=[
        frame_layout, mobject_layout, resource_layout,
    ])
    return mobject_layout, resource_layout, pipeline_layout


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
    One mobject's side of the gpu: the module it is drawn by, the buffers holding what it
    sends, the groups those are bound in, and the drawing itself.

    A mobject names a folder holding one shader, compiled once between all the mobjects
    naming it, and hands over the two arrays it keeps: its data, a record per point, and its
    uniforms, one value for the whole of it. Those sit here as a storage buffer and a uniform
    buffer. Values which hold for every mobject at once, where the camera is and the like,
    are no business of a wrapper's, being bound once a frame by the renderer.

    No shader is handed vertex attributes. Each reads the records of its buffer itself, as a
    flat array of floats indexed by the vertex being drawn, and expands every record into
    verts_per_record vertices, always triangles, see inserts/read_data.wgsl.

    Drawing comes in two halves, so that every write a frame makes lands before any of its
    draws: write_buffers sends what has changed, and render binds this mobject's groups,
    asks for the pipeline each pass wants, and draws. There is one wrapper to a mobject
    rather than to a kind of mobject, which is what lets a fill count its own winding in the
    stencil buffer without the mobject beside it joining in, and what any drawing taking
    more than one pass is built on.
    """

    def __init__(
        self,
        renderer: Renderer,
        mobject_data: StructuredArray,
        mobject_uniforms: Uniforms,
        shader_folder: Optional[str] = None,
        texture_paths: Optional[dict[str, str]] = None,
        depth_test: bool = False,
        code_replacements: dict[str, str] = dict(),
        verts_per_record: int = 0,
    ):
        self.renderer = renderer
        self.device = renderer.device
        self.mobject_data = mobject_data
        self.mobject_uniforms = mobject_uniforms
        self.shader_folder = shader_folder
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
        Where the fields of one of this mobject's vertex records sit, which along with what
        it holds for the whole of itself is all that the shader source generated for it
        depends on, and so is also the key that source gets cached under.
        """
        dtype = self.mobject_data.dtype
        self.data_layout = (
            dtype.itemsize // 4,
            tuple((name, dtype.fields[name][1] // 4) for name in dtype.names),
        )
        self.mobject_layout, self.resource_layout, self.pipeline_layout = get_bind_layouts(
            self.device, self.renderer.frame_layout, len(self.texture_paths),
        )

    def init_program(self) -> None:
        # A mobject naming no folder, a group say, has nothing to be drawn by
        self.code = self.get_code(self.shader_folder) if self.shader_folder else None
        self.module = None if self.code is None else get_shader_module(self.device, self.code)
        self.modules = [] if self.module is None else [self.module]

    def get_code(self, folder: str) -> str | None:
        return get_shader_code(
            os.path.join(folder, "shader.wgsl"),
            self.data_layout,
            self.mobject_uniforms.dtype,
            tuple(self.texture_paths),
        )

    def replace_code(self, old: str, new: str) -> None:
        self.code = re.sub(old, new, self.code)
        self.module = get_shader_module(self.device, self.code)
        self.modules = [self.module]

    def init_resources(self) -> None:
        self.data_buffer = None
        self.uniform_buffer = None
        self.mobject_bind_group = None
        self.resource_bind_group = None
        self.textures = [
            image_path_to_texture(path, self.device)
            for path in self.texture_paths.values()
        ]
        self.sampler = None
        if self.texture_paths:
            self.sampler = self.device.create_sampler(
                mag_filter=wgpu.FilterMode.linear, min_filter=wgpu.FilterMode.linear,
            )
        # Which write to each of the mobject's arrays was the last to be sent
        self.data_version = 0
        self.uniform_version = 0

    # Sending what the draw will read

    def write_buffers(self) -> None:
        """
        The mobject's two arrays into their buffers, where either has been written to since
        it was last sent. Every wrapper of a frame does this before any of them draws, since
        a write reaching the gpu partway through a render pass has no say over whether the
        draws before it see the old values or the new, see Camera.capture.
        """
        if not self.modules:
            return
        self.write_data_buffer()
        self.write_uniform_buffer()

    def write_data_buffer(self) -> None:
        array = self.mobject_data.array
        if len(array) == 0:
            return
        # A buffer's size is settled when it is made, so a resized array wants a new one,
        # and whatever was bound to the old one has to be bound afresh
        if self.data_buffer is not None and self.data_buffer.size != array.nbytes:
            self.data_buffer.destroy()
            self.data_buffer = None
        if self.data_buffer is None:
            self.data_buffer = self.device.create_buffer(
                size=array.nbytes,
                usage=wgpu.BufferUsage.STORAGE | wgpu.BufferUsage.COPY_DST,
            )
            self.resource_bind_group = None
        elif self.mobject_data.version == self.data_version:
            return
        self.renderer.queue.write_buffer(self.data_buffer, 0, array)
        self.data_version = self.mobject_data.version

    def write_uniform_buffer(self) -> None:
        array = self.mobject_uniforms.array
        if self.uniform_buffer is None:
            self.uniform_buffer = self.device.create_buffer(
                size=array.nbytes,
                usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST,
            )
            self.mobject_bind_group = None
        elif self.mobject_uniforms.version == self.uniform_version:
            return
        self.renderer.queue.write_buffer(self.uniform_buffer, 0, array)
        self.uniform_version = self.mobject_uniforms.version

    def get_bind_groups(self):
        """
        The two groups a draw of this mobject binds, made afresh whenever a buffer they
        point at has been replaced.
        """
        if self.mobject_bind_group is None:
            self.mobject_bind_group = self.device.create_bind_group(
                layout=self.mobject_layout,
                entries=[{"binding": 0, "resource": {
                    "buffer": self.uniform_buffer,
                    "offset": 0,
                    "size": self.uniform_buffer.size,
                }}],
            )
        if self.resource_bind_group is None:
            entries = [{"binding": DATA_BINDING, "resource": {
                "buffer": self.data_buffer, "offset": 0, "size": self.data_buffer.size,
            }}]
            if self.textures:
                entries.append({"binding": SAMPLER_BINDING, "resource": self.sampler})
                for index, texture in enumerate(self.textures):
                    entries.append({
                        "binding": FIRST_TEXTURE_BINDING + index,
                        "resource": texture.create_view(),
                    })
            self.resource_bind_group = self.device.create_bind_group(
                layout=self.resource_layout, entries=entries,
            )
        return self.mobject_bind_group, self.resource_bind_group

    # Drawing

    def get_pipeline(self, state: DrawState, module):
        """
        The pipeline for one of this mobject's passes. Everything a pass settles is in there:
        which module runs, what it may bind, and all of what the state names, so a pipeline
        is what gets cached and there is nothing left to say around the draw itself.
        """
        samples = self.renderer.samples
        # A module is compiled from code which names the mobject's images, so which images
        # there are, and therefore which layout a pipeline reading them wants, is already
        # settled by the module and needs no part of the key
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
                primitive={
                    "topology": wgpu.PrimitiveTopology.triangle_list,
                    "cull_mode": state.cull or wgpu.CullMode.none,
                },
                depth_stencil=state.depth_stencil_descriptor(self.depth_test),
                multisample={"count": samples},
            )

        return self.renderer.get_pipeline(key, build)

    def bind_for_draw(self, state: DrawState, module):
        """
        Points the frame's pass at what this draw reads and how it is to behave, handing
        back the pass for whichever kind of draw follows. Whatever the pass has been told
        already it is not told again, see Renderer.bind.
        """
        mobject_group, resource_group = self.get_bind_groups()
        self.renderer.bind(MOBJECT_GROUP, mobject_group)
        self.renderer.bind(RESOURCE_GROUP, resource_group)
        self.renderer.use_pipeline(self.get_pipeline(state, module))
        return self.renderer.pass_

    def draw(self, state: DrawState, module, vertices: int) -> None:
        """One pass over this mobject's records"""
        self.bind_for_draw(state, module).draw(vertices)

    def draw_through(self, state: DrawState, module, indices, count: int) -> None:
        """
        One pass over this mobject's records in the order a buffer of indices gives, each
        index being the vertex the shader is to work out.
        """
        render_pass = self.bind_for_draw(state, module)
        render_pass.set_index_buffer(indices, wgpu.IndexFormat.uint32)
        render_pass.draw_indexed(count)

    def render(self) -> None:
        if not self.modules or len(self.mobject_data) == 0:
            return
        self.draw_passes()

    def draw_passes(self) -> None:
        """Every pass this kind of mobject takes, which for most kinds is the one"""
        self.draw(DEFAULT, self.module, self.verts_per_record * len(self.mobject_data))

    def release(self) -> None:
        for buffer in (self.data_buffer, self.uniform_buffer):
            if buffer is not None:
                buffer.destroy()
        self.init_resources()


class SurfaceShaderWrapper(ShaderWrapper):
    """
    A surface is drawn in two passes, the side of it facing away from the camera before the
    side facing towards it, so that a see through one blends in the order it should: what
    lies behind first, what lies in front over the top of it.

    Nothing here asks whether a surface is see through. For an opaque one the depth test
    settles which side wins whatever order they arrive in, so the two passes come out exactly
    as one would.

    Which side faces which way is taken from the winding of the mesh, which follows how the
    surface is parametrized, the same thing its normals follow. A surface whose normals point
    inwards, and which is therefore already lit as though seen from inside, has its two
    passes the other way around as well.

    A surface which folds over itself needs more than which way it faces, since which of its
    own folds lies in front has nothing to do with that. Such a one can ask for
    sort_to_camera, and then its triangles are drawn in order of their distance from the
    camera, furthest first, through a buffer of indices written before the frame's pass opens.
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
        the camera first, in a buffer to be drawn through. False if there is nothing to order
        that way: records which are no grid, as an imported mesh's are.
        """
        camera_position = self.renderer.frame_uniforms["camera_position"]
        nu, nv = self.mobject_uniforms["resolution"].astype(int)
        if nu < 2 or nv < 2:
            return False

        # Where the middle of each triangle of each square sits, the two of them taking the
        # corners the vertex shader gives them, see inserts/surface_mesh.wgsl
        points = self.mobject_data["point"].reshape((nu, nv, 3))
        middles = np.array([
            points[:-1, :-1] + points[1:, :-1] + points[:-1, 1:],
            points[:-1, 1:] + points[1:, :-1] + points[1:, 1:],
        ])
        offsets = middles.reshape((-1, 3)) / 3 - np.array(camera_position)
        order = np.argsort(-np.einsum("ij,ij->i", offsets, offsets))

        # Which vertices each of those triangles is drawn from, six per square, the first
        # three making one triangle and the last three the other
        squares = np.arange(nu - 1)[:, np.newaxis] * nv + np.arange(nv - 1)
        firsts = 6 * squares + np.array([[[0]], [[3]]])
        vertices = firsts.reshape(-1)[order, np.newaxis] + np.arange(3)
        self.write_order_buffer(vertices.astype(np.uint32).reshape(-1))
        return True

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
            return
        vertices = self.verts_per_record * len(self.mobject_data)
        for state in (CULL_FRONT, CULL_BACK):
            self.draw(state, self.module, vertices)


class VShaderWrapper(ShaderWrapper):
    """
    A vectorized mobject is drawn by two shaders rather than one: a fill over the region its
    path encloses, and a stroke along the path itself. So it holds two modules, and names
    which of them each of its passes runs.
    """
    fill_folder = os.path.join("quadratic_bezier", "fill")
    stroke_folder = os.path.join("quadratic_bezier", "stroke")
    # Each bezier's fill is two triangles, one covering the interior and one hugging the
    # curve, see quadratic_bezier/fill/shader.wgsl
    fill_verts_per_curve = 6
    # And its stroke is a quad for each polyline segment the curve is broken into, the last
    # few of them going to the fan which rounds off a joint, see
    # quadratic_bezier/stroke/shader.wgsl, whose MAX_STEPS this follows
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
        self.fill_code = self.get_code(self.fill_folder)
        self.stroke_code = self.get_code(self.stroke_folder)
        self.build_modules()

    def build_modules(self) -> None:
        """
        Three modules from two sources. The border around a fill is the stroke shader with
        one constant compiled the other way, which is what wgpu asks for in place of a
        uniform read per draw, and costs nothing: a module is compiled once per source.
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
        incrementing for front facing triangles and decrementing for back facing ones. Since
        facing is just the sign of a triangle's area in screen space, each pixel ends up
        holding the winding number of the path around it, with no need for a triangulation of
        the shape.

        The second pass draws those same triangles again, but only where that winding number
        is nonzero, and zeros out the stencil as it goes. This means each pixel is colored
        exactly once, using ordinary alpha blending, and that the stencil buffer is left
        clean for whatever draws next.

        Note this only works because a wrapper holds a single mobject. Sharing one pair of
        passes between several would merge their winding numbers into one region, so that
        overlapping mobjects would color a shared pixel once between them rather than each
        blending in turn.
        """
        vertices = self.fill_verts_per_curve * self.get_num_curves()
        # Counting the windings needs no color, and must see every triangle of the path
        # whatever stands in front of it, which is what WINDING_COUNT says
        self.draw(WINDING_COUNT, self.fill_module, vertices)
        self.draw_fill_border()
        # Coloring in everywhere the count came out nonzero, zeroing it on the way through,
        # so that each pixel is colored once and the buffer is left clean
        self.draw(WINDING_COVER, self.fill_module, vertices)

    def draw_fill_border(self) -> None:
        """
        Traces the boundary of the shape with a stroke in the fill color, which is what
        anti-aliases the fill, a stencil test being all or nothing. It is drawn only where
        the winding number is zero, meaning outside the shape, both because the inside is
        about to be filled in anyway, and so that its faded edge never blends on top of the
        fill, which would leave a seam along the boundary for partially transparent colors.
        """
        self.draw(FILL_BORDER, self.border_module, self.stroke_vertices())

    def draw_stroke(self) -> None:
        self.draw(DEFAULT, self.stroke_module, self.stroke_vertices())

    def stroke_vertices(self) -> int:
        return self.stroke_verts_per_curve * self.get_num_curves()

    def draw_passes(self) -> None:
        if self.stroke_behind:
            self.draw_stroke()
            self.draw_fill()
        else:
            self.draw_fill()
            self.draw_stroke()
