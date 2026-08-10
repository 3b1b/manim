from __future__ import annotations

import re

from manimlib.renderer.shader_source import DATA_BINDING
from manimlib.renderer.shader_source import FIRST_TEXTURE_BINDING
from manimlib.renderer.shader_source import SAMPLER_BINDING
from manimlib.renderer.shader_source import get_shader_code

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Sequence
    from manimlib.mobject.mobject import Mobject
    from manimlib.renderer.gpu import Gpu
    from manimlib.renderer.pipeline import PipelineState

    # A module to compile, as the name a drawing asks for it by, the file it comes from, and
    # what to rewrite in that file's source
    ModuleSpec = tuple[str, str, dict[str, str]]


class Material(object):
    """
    Everything one kind of mobject is drawn with, and nothing about any particular one: the
    modules its shaders compile to, the layouts and images they read through, and the buffers
    its values are gathered in.

    One material stands behind however many mobjects agree about all of that, see
    Renderer.material_for, and it is the same object frame after frame. What varies per mobject
    is a Drawing, and what varies per pass is a PipelineState.
    """

    def __init__(self, gpu: Gpu, mobject: Mobject, specs: Sequence[ModuleSpec]):
        self.gpu = gpu
        self.verts_per_record = mobject.verts_per_record
        self.record_size = mobject.data.dtype.itemsize
        self.texture_paths = dict(mobject.texture_paths)

        self.resource_layout, self.pipeline_layout = gpu.bind_layouts(len(self.texture_paths))
        # Where these mobjects' values go each frame, see SharedBuffer
        self.uniform_buffer = gpu.uniform_buffer(mobject.uniforms.array.nbytes)
        self.data_buffer = gpu.data_buffer(self.record_size)

        self.textures = [gpu.texture(path) for path in self.texture_paths.values()]
        self.sampler = gpu.sampler() if self.texture_paths else None
        self.modules = {
            name: gpu.module(self.get_code(mobject, filename, replacements))
            for name, filename, replacements in specs
        }

    def get_code(self, mobject: Mobject, filename: str, replacements: dict[str, str]) -> str:
        """
        A shader's source, told where the fields of one of these mobjects' records sit and what
        it holds for the whole of itself, which is all the source depends on.
        """
        code = get_shader_code(
            filename, mobject.data.dtype, mobject.uniforms.dtype, tuple(self.texture_paths),
        )
        for old, new in replacements.items():
            code = re.sub(old, new, code)
        return code

    def pipeline(self, module: str, state: PipelineState) -> Any:
        """The pipeline for one pass, naming the module by what the drawing asked for it as"""
        return self.gpu.pipeline(self.pipeline_layout, self.modules[module], state)

    def make_resource_bind_group(self) -> Any:
        """
        A group through which one mobject reads its records and its own images. Only a mobject
        with images needs one; the rest read the shared group of the buffer they sit in, which
        serves every mobject of their size, see Drawing.resource_bind_group.
        """
        shared = self.data_buffer
        entries = [{"binding": DATA_BINDING, "resource": {
            "buffer": shared.buffer, "offset": 0, "size": shared.window,
        }}]
        entries.append({"binding": SAMPLER_BINDING, "resource": self.sampler})
        entries += [
            {"binding": FIRST_TEXTURE_BINDING + index, "resource": texture.create_view()}
            for index, texture in enumerate(self.textures)
        ]
        return self.gpu.device.create_bind_group(layout=self.resource_layout, entries=entries)
