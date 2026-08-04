from __future__ import annotations

import os
import re
from functools import lru_cache

import wgpu

from manimlib.renderer import COLOR_FORMAT
from manimlib.renderer import DEFAULT
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
        self.code = self.get_code()
        self.module = None if self.code is None else get_shader_module(self.device, self.code)

    def get_code(self) -> str | None:
        return get_shader_code(
            os.path.join(self.shader_folder, "shader.wgsl"),
            self.data_layout,
            self.mobject_uniforms.dtype,
            tuple(self.texture_paths),
        )

    def replace_code(self, old: str, new: str) -> None:
        self.code = re.sub(old, new, self.code)
        self.module = get_shader_module(self.device, self.code)

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
        if self.module is None:
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

    def get_pipeline(self, state: DrawState):
        """
        The pipeline for one of this mobject's passes. Everything a pass settles is in there:
        which module runs, what it may bind, and all of what the state names, so a pipeline
        is what gets cached and there is nothing left to say around the draw itself.
        """
        samples = self.renderer.samples
        key = (self.module, len(self.texture_paths), state, self.depth_test, samples)

        def build():
            return self.device.create_render_pipeline(
                layout=self.pipeline_layout,
                vertex={"module": self.module, "entry_point": "vs_main", "buffers": []},
                fragment={
                    "module": self.module,
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

    def draw(self, state: DrawState = DEFAULT, vertices: int | None = None) -> None:
        """One pass over this mobject's records, in the state given"""
        render_pass = self.renderer.pass_
        mobject_group, resource_group = self.get_bind_groups()
        render_pass.set_bind_group(MOBJECT_GROUP, mobject_group)
        render_pass.set_bind_group(RESOURCE_GROUP, resource_group)
        render_pass.set_pipeline(self.get_pipeline(state))
        if vertices is None:
            vertices = self.verts_per_record * len(self.mobject_data)
        render_pass.draw(vertices)

    def render(self) -> None:
        if self.module is None or len(self.mobject_data) == 0:
            return
        self.draw()

    def release(self) -> None:
        for buffer in (self.data_buffer, self.uniform_buffer):
            if buffer is not None:
                buffer.destroy()
        self.init_resources()


class SurfaceShaderWrapper(ShaderWrapper):
    """Not drawn yet on this branch, see phase 2c of WGPU_PORT_PLAN.md"""

    def __init__(self, *args, sort_to_camera: bool = False, **kwargs):
        self.sort_to_camera = sort_to_camera
        super().__init__(*args, **kwargs)

    def render(self) -> None:
        raise NotImplementedError(
            "Surfaces are not drawn yet on this branch, see phase 2c of WGPU_PORT_PLAN.md"
        )


class VShaderWrapper(ShaderWrapper):
    """Not drawn yet on this branch, see phase 2c of WGPU_PORT_PLAN.md"""

    def __init__(
        self,
        *args,
        program_type: str | None = None,
        stroke_behind: bool = False,
        **kwargs,
    ):
        self.stroke_behind = stroke_behind
        super().__init__(*args, **kwargs)

    def replace_code_program(self, old: str, new: str, program_type: str | None = None):
        self.replace_code(old, new)

    def render(self) -> None:
        raise NotImplementedError(
            "VMobjects are not drawn yet on this branch, see phase 2c of WGPU_PORT_PLAN.md"
        )
