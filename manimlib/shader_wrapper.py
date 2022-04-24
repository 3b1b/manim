from __future__ import annotations

import copy
import os
import re

import moderngl
import numpy as np

from manimlib.utils.directories import get_shader_dir
from manimlib.utils.file_ops import find_file

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable


# Mobjects that should be rendered with
# the same shader will be organized and
# clumped together based on keeping track
# of a dict holding all the relevant information
# to that shader


class ShaderWrapper(object):
    def __init__(
        self,
        vert_data: np.ndarray | None = None,
        vert_indices: np.ndarray | None = None,
        shader_folder: str | None = None,
        uniforms: dict[str, float] | None = None,  # A dictionary mapping names of uniform variables
        texture_paths: dict[str, str] | None = None,  # A dictionary mapping names to filepaths for textures.
        depth_test: bool = False,
        render_primitive: int = moderngl.TRIANGLE_STRIP,
    ):
        self.vert_data = vert_data
        self.vert_indices = vert_indices
        self.vert_attributes = vert_data.dtype.names
        self.shader_folder = shader_folder
        self.uniforms = uniforms or dict()
        self.texture_paths = texture_paths or dict()
        self.depth_test = depth_test
        self.render_primitive = str(render_primitive)
        self.init_program_code()
        self.refresh_id()

    def copy(self):
        result = copy.copy(self)
        result.vert_data = np.array(self.vert_data)
        if result.vert_indices is not None:
            result.vert_indices = np.array(self.vert_indices)
        if self.uniforms:
            result.uniforms = dict(self.uniforms)
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

    def combine_with(self, *shader_wrappers: ShaderWrapper):
        # Assume they are of the same type
        if len(shader_wrappers) == 0:
            return
        if self.vert_indices is not None:
            num_verts = len(self.vert_data)
            indices_list = [self.vert_indices]
            data_list = [self.vert_data]
            for sw in shader_wrappers:
                indices_list.append(sw.vert_indices + num_verts)
                data_list.append(sw.vert_data)
                num_verts += len(sw.vert_data)
            self.vert_indices = np.hstack(indices_list)
            self.vert_data = np.hstack(data_list)
        else:
            self.vert_data = np.hstack([self.vert_data, *[sw.vert_data for sw in shader_wrappers]])
        return self


# For caching
filename_to_code_map: dict[str, str] = {}


def get_shader_code_from_file(filename: str) -> str | None:
    if not filename:
        return None
    if filename in filename_to_code_map:
        return filename_to_code_map[filename]

    try:
        filepath = find_file(
            filename,
            directories=[get_shader_dir(), "/"],
            extensions=[],
        )
    except IOError:
        return None

    with open(filepath, "r") as f:
        result = f.read()

    # To share functionality between shaders, some functions are read in
    # from other files an inserted into the relevant strings before
    # passing to ctx.program for compiling
    # Replace "#INSERT " lines with relevant code
    insertions = re.findall(r"^#INSERT .*\.glsl$", result, flags=re.MULTILINE)
    for line in insertions:
        inserted_code = get_shader_code_from_file(
            os.path.join("inserts", line.replace("#INSERT ", ""))
        )
        result = result.replace(line, inserted_code)
    filename_to_code_map[filename] = result
    return result


def get_colormap_code(rgb_list: Iterable[float]) -> str:
    data = ",".join(
        "vec3({}, {}, {})".format(*rgb)
        for rgb in rgb_list
    )
    return f"vec3[{len(rgb_list)}]({data})"
