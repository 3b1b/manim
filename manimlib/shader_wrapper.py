from __future__ import annotations

import copy
import os
import re

import OpenGL.GL as gl
import moderngl
import numpy as np

from manimlib.utils.iterables import resize_array
from manimlib.utils.shaders import get_shader_code_from_file
from manimlib.utils.shaders import get_shader_program
from manimlib.utils.shaders import image_path_to_texture
from manimlib.utils.shaders import get_texture_id
from manimlib.utils.shaders import get_fill_canvas
from manimlib.utils.shaders import release_texture
from manimlib.utils.shaders import set_program_uniform

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional, Dict
    from manimlib.typing import UniformDict


# Mobjects that should be rendered with
# the same shader will be organized and
# clumped together based on keeping track
# of a dict holding all the relevant information
# to that shader


class ShaderWrapper(object):
    def __init__(
        self,
        ctx: moderngl.context.Context,
        vert_data: np.ndarray,
        shader_folder: Optional[str] = None,
        mobject_uniforms: Optional[UniformDict] = None,  # A dictionary mapping names of uniform variables
        texture_paths: Optional[dict[str, str]] = None,  # A dictionary mapping names to filepaths for textures.
        depth_test: bool = False,
        render_primitive: int = moderngl.TRIANGLE_STRIP,
    ):
        self.ctx = ctx
        self.vert_data = vert_data
        self.vert_attributes = vert_data.dtype.names
        self.shader_folder = shader_folder
        self.depth_test = depth_test
        self.render_primitive = render_primitive

        self.program_uniform_mirror: UniformDict = dict()
        self.bind_to_mobject_uniforms(mobject_uniforms or dict())

        self.init_program_code()
        self.init_program()
        self.texture_names_to_ids = dict()
        if texture_paths is not None:
            self.init_textures(texture_paths)
        self.init_vertex_objects()
        self.refresh_id()

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

    def init_program(self):
        if not self.shader_folder:
            self.program = None
            self.vert_format = None
            self.programs = []
            return
        self.program = get_shader_program(self.ctx, **self.program_code)
        self.vert_format = moderngl.detect_format(self.program, self.vert_attributes)
        self.programs = [self.program]

    def init_textures(self, texture_paths: dict[str, str]):
        self.texture_names_to_ids = {
            name: get_texture_id(image_path_to_texture(path, self.ctx))
            for name, path in texture_paths.items()
        }

    def init_vertex_objects(self):
        self.vbo = None
        self.vaos = []

    def bind_to_mobject_uniforms(self, mobject_uniforms: UniformDict):
        self.mobject_uniforms = mobject_uniforms

    def __eq__(self, shader_wrapper: ShaderWrapper):
        return all((
            # np.all(self.vert_data == shader_wrapper.vert_data),
            self.shader_folder == shader_wrapper.shader_folder,
            all(
                self.mobject_uniforms[key] == shader_wrapper.mobject_uniforms[key]
                for key in self.mobject_uniforms
            ),
            self.depth_test == shader_wrapper.depth_test,
            self.render_primitive == shader_wrapper.render_primitive,
        ))

    def copy(self):
        result = copy.copy(self)
        result.ctx = self.ctx
        result.vert_data = self.vert_data.copy()
        result.init_vertex_objects()
        return result

    def is_valid(self) -> bool:
        return all([
            # self.vert_data is not None,
            self.program_code["vertex_shader"] is not None,
            self.program_code["fragment_shader"] is not None,
        ])

    def get_id(self) -> str:
        return self.id

    def create_id(self) -> str:
        # A unique id for a shader
        program_id = hash("".join(map(str, self.program_code.values())))
        return "|".join(map(str, [
            program_id,
            self.mobject_uniforms,
            self.depth_test,
            self.render_primitive,
            self.texture_names_to_ids,
        ]))

    def refresh_id(self) -> None:
        self.id = self.create_id()

    def replace_code(self, old: str, new: str) -> None:
        code_map = self.program_code
        for name in code_map:
            if code_map[name] is None:
                continue
            code_map[name] = re.sub(old, new, code_map[name])
        self.init_program()
        self.refresh_id()

    # Changing context
    def use_clip_plane(self):
        if "clip_plane" not in self.mobject_uniforms:
            return False
        return any(self.mobject_uniforms["clip_plane"])

    def set_ctx_depth_test(self, enable: bool = True) -> None:
        if enable:
            self.ctx.enable(moderngl.DEPTH_TEST)
        else:
            self.ctx.disable(moderngl.DEPTH_TEST)

    def set_ctx_clip_plane(self, enable: bool = True) -> None:
        if enable:
            gl.glEnable(gl.GL_CLIP_DISTANCE0)

    # Adding data

    def combine_with(self, *shader_wrappers: ShaderWrapper) -> ShaderWrapper:
        if len(shader_wrappers) > 0:
            self.read_in([self.vert_data, *(sw.vert_data for sw in shader_wrappers)])
            vbos = [
                vbo
                for vbo in [self.vbo, *(sw.vbo for sw in shader_wrappers)]
                if vbo is not None
            ]
            total_size = sum(vbo.size for vbo in vbos)
            new_vbo = self.ctx.buffer(reserve=total_size)
            offset = 0
            for vbo in vbos:
                new_vbo.write(vbo.read(), offset=offset)
                offset += vbo.size
            self.vbo = new_vbo
        return self

    def read_in(
        self,
        data_list: Iterable[np.ndarray],
        indices_list: Iterable[np.ndarray] | None = None
    ):
        if indices_list is not None:
            data_list = [data[indices] for data, indices in zip(data_list, indices_list)]

        total_len = sum(map(len, data_list))
        if total_len == 0:
            if self.vbo is not None:
                self.vbo.clear()
            return

        # If possible, read concatenated data into existing list
        if len(self.vert_data) != total_len:
            self.vert_data = np.concatenate(data_list)
        else:
            np.concatenate(data_list, out=self.vert_data)

        # Either create new vbo, or read data into it
        total_size = self.vert_data.itemsize * total_len
        if self.vbo is not None and self.vbo.size != total_size:
            self.release()  # This sets vbo to be None
        if self.vbo is None:
            self.vbo = self.ctx.buffer(self.vert_data)
            self.generate_vaos()
        else:
            self.vbo.write(self.vert_data)

    def generate_vaos(self):
        # Vertex array object
        self.vaos = [
            self.ctx.vertex_array(
                program=program,
                content=[(self.vbo, self.vert_format, *self.vert_attributes)],
                mode=self.render_primitive,
            )
            for program in self.programs
        ]

    # Related to data and rendering
    def pre_render(self):
        self.set_ctx_depth_test(self.depth_test)
        self.set_ctx_clip_plane(self.use_clip_plane())

    def render(self):
        for vao in self.vaos:
            vao.render()

    def update_program_uniforms(self, camera_uniforms: UniformDict):
        for program in self.programs:
            if program is None:
                continue
            for uniforms in [self.mobject_uniforms, camera_uniforms, self.texture_names_to_ids]:
                for name, value in uniforms.items():
                    set_program_uniform(program, name, value)

    def release(self):
        for obj in (self.vbo, *self.vaos):
            if obj is not None:
                obj.release()
        self.init_vertex_objects()


class VShaderWrapper(ShaderWrapper):
    def __init__(
        self,
        ctx: moderngl.context.Context,
        vert_data: np.ndarray,
        shader_folder: Optional[str] = None,
        mobject_uniforms: Optional[UniformDict] = None,  # A dictionary mapping names of uniform variables
        texture_paths: Optional[dict[str, str]] = None,  # A dictionary mapping names to filepaths for textures.
        depth_test: bool = False,
        # render_primitive: int = moderngl.TRIANGLES,
        render_primitive: int = moderngl.TRIANGLE_STRIP,
        stroke_behind: bool = False,
    ):
        super().__init__(
            ctx=ctx,
            vert_data=vert_data,
            shader_folder=shader_folder,
            mobject_uniforms=mobject_uniforms,
            texture_paths=texture_paths,
            depth_test=depth_test,
            render_primitive=render_primitive,
        )
        self.stroke_behind = stroke_behind
        self.fill_canvas = get_fill_canvas(self.ctx)

    def init_program_code(self) -> None:
        self.program_code = {
            f"{vtype}_{name}": get_shader_code_from_file(
                os.path.join(f"quadratic_bezier_{vtype}", f"{name}.glsl")
            )
            for vtype in ["stroke", "fill", "depth"]
            for name in ["vert", "geom", "frag"]
        }

    def init_program(self):
        self.stroke_program = get_shader_program(
            self.ctx,
            vertex_shader=self.program_code["stroke_vert"],
            geometry_shader=self.program_code["stroke_geom"],
            fragment_shader=self.program_code["stroke_frag"],
        )
        self.fill_program = get_shader_program(
            self.ctx,
            vertex_shader=self.program_code["fill_vert"],
            geometry_shader=self.program_code["fill_geom"],
            fragment_shader=self.program_code["fill_frag"],
        )
        self.fill_depth_program = get_shader_program(
            self.ctx,
            vertex_shader=self.program_code["depth_vert"],
            geometry_shader=self.program_code["depth_geom"],
            fragment_shader=self.program_code["depth_frag"],
        )
        self.programs = [self.stroke_program, self.fill_program, self.fill_depth_program]

        # Full vert format looks like this (total of 4x23 = 92 bytes):
        # point 3
        # stroke_rgba 4
        # stroke_width 1
        # joint_product 4
        # fill_rgba 4
        # base_point 3
        # unit_normal 3
        # fill_border_width 1
        self.stroke_vert_format = '3f 4f 1f 4f 44x'
        self.stroke_vert_attributes = ['point', 'stroke_rgba', 'stroke_width', 'joint_product']

        self.fill_vert_format = '3f 36x 4f 3f 3f 4x'
        self.fill_vert_attributes = ['point', 'fill_rgba', 'base_point', 'unit_normal']

        self.fill_border_vert_format = '3f 20x 4f 4f 24x 1f'
        self.fill_border_vert_attributes = ['point', 'joint_product', 'stroke_rgba', 'stroke_width']

        self.fill_depth_vert_format = '3f 52x 3f 16x'
        self.fill_depth_vert_attributes = ['point', 'base_point']

    def init_vertex_objects(self):
        self.vbo = None
        self.stroke_vao = None
        self.fill_vao = None
        self.fill_border_vao = None
        self.vaos = []

    def generate_vaos(self):
        self.stroke_vao = self.ctx.vertex_array(
            program=self.stroke_program,
            content=[(self.vbo, self.stroke_vert_format, *self.stroke_vert_attributes)],
            mode=self.render_primitive,
        )
        self.fill_vao = self.ctx.vertex_array(
            program=self.fill_program,
            content=[(self.vbo, self.fill_vert_format, *self.fill_vert_attributes)],
            mode=self.render_primitive,
        )
        self.fill_border_vao = self.ctx.vertex_array(
            program=self.stroke_program,
            content=[(self.vbo, self.fill_border_vert_format, *self.fill_border_vert_attributes)],
            mode=self.render_primitive,
        )
        self.fill_depth_vao = self.ctx.vertex_array(
            program=self.fill_depth_program,
            content=[(self.vbo, self.fill_depth_vert_format, *self.fill_depth_vert_attributes)],
            mode=self.render_primitive,
        )
        self.vaos = [self.stroke_vao, self.fill_vao, self.fill_border_vao, self.fill_depth_vao]

    def set_backstroke(self, value: bool = True):
        self.stroke_behind = value

    # TODO, think about create_id, replace_code
    def is_valid(self) -> bool:
        return self.vert_data is not None  # Isn't this always true?

    # TODO, motidify read in to handle triangulation case for non-winding fill?

    # Rendering
    def render_stroke(self):
        if self.stroke_vao is None:
            return
        self.stroke_vao.render()

    def render_fill(self):
        if self.fill_vao is None:
            return

        # TODO, need a new test here...or to just kill non-winding fill?
        winding = True
        self.fill_program['winding'].value = winding
        if not winding:
            self.fill_vao.render()
            return

        original_fbo = self.ctx.fbo
        texture_fbo, depth_texture_fbo, texture_vao = self.fill_canvas

        texture_fbo.clear()
        texture_fbo.use()
        gl.glBlendFuncSeparate(
            # Ordinary blending for colors
            gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA,
            # The effect of blending with -a / (1 - a)
            # should be to cancel out
            gl.GL_ONE_MINUS_DST_ALPHA, gl.GL_ONE,
        )

        # Be sure not to apply depth test while rendering fill
        # but set it back to where it was after
        apply_depth_test = bool(gl.glGetBooleanv(gl.GL_DEPTH_TEST))
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.fill_vao.render()
        if apply_depth_test:
            depth_texture_fbo.clear(1.0)
            depth_texture_fbo.use()
            gl.glBlendFunc(gl.GL_ONE, gl.GL_ONE)
            gl.glBlendEquation(gl.GL_MIN)
            self.fill_depth_vao.render()
            self.ctx.enable(moderngl.DEPTH_TEST)

        # Border width is used for antialiasing. Take the maximum between these
        # two alphas, before compositing back to the rest of the scene
        gl.glBlendFuncSeparate(
            gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA,
            gl.GL_ONE, gl.GL_ZERO
        )
        gl.glBlendEquationSeparate(gl.GL_FUNC_ADD, gl.GL_MAX)
        self.fill_border_vao.render()

        original_fbo.use()
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glBlendEquation(gl.GL_FUNC_ADD)
        texture_vao.render()

    def render(self):
        if self.stroke_behind:
            self.render_stroke()
            self.render_fill()
        else:
            self.render_fill()
            self.render_stroke()
