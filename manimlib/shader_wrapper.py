import os
import warnings
import re
import moderngl
import numpy as np
import copy

from manimlib.constants import SHADER_DIR

# Mobjects that should be rendered with
# the same shader will be organized and
# clumped together based on keeping track
# of a dict holding all the relevant information
# to that shader


class ShaderWrapper(object):
    def __init__(self,
                 vert_data=None,
                 vert_indices=None,
                 vert_file=None,
                 geom_file=None,
                 frag_file=None,
                 uniforms=None,  # A dictionary mapping names of uniform variables
                 texture_paths=None,  # A dictionary mapping names to filepaths for textures.
                 depth_test=False,
                 render_primitive=moderngl.TRIANGLE_STRIP,
                 ):
        self.vert_data = vert_data
        self.vert_indices = vert_indices
        self.vert_attributes = vert_data.dtype.names
        self.vert_file = vert_file
        self.geom_file = geom_file
        self.frag_file = frag_file
        self.uniforms = uniforms or dict()
        self.texture_paths = texture_paths or dict()
        self.depth_test = depth_test
        self.render_primitive = str(render_primitive)
        self.id = self.create_id()
        self.program_id = self.create_program_id()

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

    def is_valid(self):
        return all([
            self.vert_data is not None,
            self.vert_file,
            self.frag_file,
        ])

    def get_id(self):
        return self.id

    def get_program_id(self):
        return self.program_id

    def create_id(self):
        # A unique id for a shader
        return "|".join(map(str, [
            self.vert_file,
            self.geom_file,
            self.frag_file,
            self.uniforms,
            self.texture_paths,
            self.depth_test,
            self.render_primitive,
        ]))

    def refresh_id(self):
        self.id = self.create_id()

    def create_program_id(self):
        return "|".join(map(str, [self.vert_file, self.geom_file, self.frag_file]))

    def get_program_code(self):
        return {
            "vertex_shader": get_shader_code_from_file(self.vert_file),
            "geometry_shader": get_shader_code_from_file(self.geom_file),
            "fragment_shader": get_shader_code_from_file(self.frag_file),
        }

    def combine_with(self, *shader_wrappers):
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


def get_shader_code_from_file(filename):
    if not filename:
        return None

    filepath = os.path.join(SHADER_DIR, filename)
    if not os.path.exists(filepath):
        warnings.warn(f"No file at {filepath}")
        return

    with open(filepath, "r") as f:
        result = f.read()

    # To share functionality between shaders, some functions are read in
    # from other files an inserted into the relevant strings before
    # passing to ctx.program for compiling
    # Replace "#INSERT " lines with relevant code
    insertions = re.findall(r"^#INSERT .*\.glsl$", result, flags=re.MULTILINE)
    for line in insertions:
        inserted_code = get_shader_code_from_file(line.replace("#INSERT ", ""))
        result = result.replace(line, inserted_code)
    return result
