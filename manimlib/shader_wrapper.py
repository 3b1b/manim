from __future__ import annotations

import copy
import os
import re

import moderngl
import numpy as np

from manimlib.utils.iterables import resize_array
from manimlib.utils.shaders import get_shader_code_from_file

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List


# Mobjects that should be rendered with
# the same shader will be organized and
# clumped together based on keeping track
# of a dict holding all the relevant information
# to that shader


class ShaderWrapper(object):
    def __init__(
        self,
        context: moderngl.context.Context,
        vert_data: np.ndarray,
        vert_indices: np.ndarray | None = None,
        shader_folder: str | None = None,
        uniforms: dict[str, float | np.ndarray] | None = None,  # A dictionary mapping names of uniform variables
        texture_paths: dict[str, str] | None = None,  # A dictionary mapping names to filepaths for textures.
        depth_test: bool = False,
        render_primitive: int = moderngl.TRIANGLE_STRIP,
        is_fill: bool = False,
    ):
        self.ctx = context
        self.vert_data = vert_data
        self.vert_indices = (vert_indices or np.zeros(0)).astype(int)
        self.vert_attributes = vert_data.dtype.names
        self.shader_folder = shader_folder
        self.uniforms = uniforms or dict()
        self.texture_paths = texture_paths or dict()
        self.depth_test = depth_test
        self.render_primitive = str(render_primitive)
        self.is_fill = is_fill
        self.init_program_code()
        self.refresh_id()

    def __eq__(self, shader_wrapper: ShaderWrapper):
        return all((
            np.all(self.vert_data == shader_wrapper.vert_data),
            np.all(self.vert_indices == shader_wrapper.vert_indices),
            self.shader_folder == shader_wrapper.shader_folder,
            all(
                np.all(self.uniforms[key] == shader_wrapper.uniforms[key])
                for key in self.uniforms
            ),
            all(
                self.texture_paths[key] == shader_wrapper.texture_paths[key]
                for key in self.texture_paths
            ),
            self.depth_test == shader_wrapper.depth_test,
            self.render_primitive == shader_wrapper.render_primitive,
        ))

    def copy(self):
        result = copy.copy(self)
        result.vert_data = self.vert_data.copy()
        result.vert_indices = self.vert_indices.copy()
        if self.uniforms:
            result.uniforms = {key: np.array(value) for key, value in self.uniforms.items()}
        if self.texture_paths:
            result.texture_paths = dict(self.texture_paths)
        return result

    def is_valid(self) -> bool:
        return all([
            self.vert_data is not None,
            self.program_code["vertex_shader"] is not None,
            self.program_code["fragment_shader"] is not None,
        ])

    def get_id(self) -> str:
        return self.id

    def get_program_id(self) -> int:
        return self.program_id

    def create_id(self) -> str:
        # A unique id for a shader
        return "|".join(map(str, [
            self.program_id,
            self.uniforms,
            self.texture_paths,
            self.depth_test,
            self.render_primitive,
        ]))

    def refresh_id(self) -> None:
        self.program_id = self.create_program_id()
        self.id = self.create_id()

    def create_program_id(self) -> int:
        return hash("".join((
            self.program_code[f"{name}_shader"] or ""
            for name in ("vertex", "geometry", "fragment")
        )))

    def init_program_code(self) -> None:
        def get_code(name: str) -> str | None:
            return get_shader_code_from_file(
                os.path.join(self.shader_folder, f"{name}.glsl")
            )

        self.program_code: dict[str, str | None] = {
            "vertex_shader": get_code("vert"),
            "geometry_shader": get_code("geom"),
            "fragment_shader": get_code("frag"),
        }

    def get_program_code(self) -> dict[str, str | None]:
        return self.program_code

    def replace_code(self, old: str, new: str) -> None:
        code_map = self.program_code
        for (name, code) in code_map.items():
            if code_map[name] is None:
                continue
            code_map[name] = re.sub(old, new, code_map[name])
        self.refresh_id()

    def use_clip_plane(self):
        if "clip_plane" not in self.uniforms:
            return False
        return any(self.uniforms["clip_plane"])

    def combine_with(self, *shader_wrappers: ShaderWrapper) -> ShaderWrapper:
        if len(shader_wrappers) > 0:
            data_list = [self.vert_data, *(sw.vert_data for sw in shader_wrappers)]
            indices_list = [self.vert_indices, *(sw.vert_indices for sw in shader_wrappers)]
            self.read_in(data_list, indices_list)
        return self

    def read_in(
        self,
        data_list: List[np.ndarray],
        indices_list: List[np.ndarray] | None = None
    ) -> ShaderWrapper:
        # Assume all are of the same type
        total_len = sum(len(data) for data in data_list)
        self.vert_data = resize_array(self.vert_data, total_len)
        if total_len == 0:
            return self

        # Stack the data
        np.concatenate(data_list, out=self.vert_data)

        if indices_list is None:
            self.vert_indices = resize_array(self.vert_indices, 0)
            return self

        total_verts = sum(len(vi) for vi in indices_list)
        if total_verts == 0:
            return self

        self.vert_indices = resize_array(self.vert_indices, total_verts)

        # Stack vert_indices, but adding the appropriate offset
        # alogn the way
        n_points = 0
        n_verts = 0
        for data, indices in zip(data_list, indices_list):
            new_n_verts = n_verts + len(indices)
            self.vert_indices[n_verts:new_n_verts] = indices + n_points
            n_verts = new_n_verts
            n_points += len(data)
        return self
