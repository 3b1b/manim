from __future__ import annotations

import copy
import os
import re

import OpenGL.GL as gl
import moderngl
import numpy as np

from manimlib.constants import DEFAULT_PIXEL_HEIGHT
from manimlib.constants import DEFAULT_PIXEL_WIDTH
from manimlib.utils.iterables import resize_array
from manimlib.utils.shaders import get_shader_code_from_file
from manimlib.utils.shaders import get_shader_program
from manimlib.utils.shaders import image_path_to_texture
from manimlib.utils.shaders import get_texture_id
from manimlib.utils.shaders import release_texture

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional


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
        vert_indices: Optional[np.ndarray] = None,
        shader_folder: Optional[str] = None,
        uniforms: Optional[dict[str, float | np.ndarray]] = None,  # A dictionary mapping names of uniform variables
        texture_paths: Optional[dict[str, str]] = None,  # A dictionary mapping names to filepaths for textures.
        depth_test: bool = False,
        render_primitive: int = moderngl.TRIANGLE_STRIP,
    ):
        self.ctx = ctx
        self.vert_data = vert_data
        self.vert_indices = (vert_indices or np.zeros(0)).astype(int)
        self.vert_attributes = vert_data.dtype.names
        self.shader_folder = shader_folder
        self.uniforms = uniforms or dict()
        self.depth_test = depth_test
        self.render_primitive = render_primitive

        self.vbo = None
        self.ibo = None
        self.vao = None

        self.init_program_code()
        self.init_program()
        if texture_paths is not None:
            self.init_textures(texture_paths)
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
            return
        self.program = get_shader_program(self.ctx, **self.program_code)
        self.vert_format = moderngl.detect_format(self.program, self.vert_attributes)

    def init_textures(self, texture_paths: dict[str, str]):
        for name, path in texture_paths.items():
            texture = image_path_to_texture(path, self.ctx)
            tid = get_texture_id(texture)
            self.uniforms[name] = tid

    def __eq__(self, shader_wrapper: ShaderWrapper):
        return all((
            np.all(self.vert_data == shader_wrapper.vert_data),
            np.all(self.vert_indices == shader_wrapper.vert_indices),
            self.shader_folder == shader_wrapper.shader_folder,
            all(
                np.all(self.uniforms[key] == shader_wrapper.uniforms[key])
                for key in self.uniforms
            ),
            self.depth_test == shader_wrapper.depth_test,
            self.render_primitive == shader_wrapper.render_primitive,
        ))

    def __del__(self):
        self.release()

    def copy(self):
        result = copy.copy(self)
        result.vert_data = self.vert_data.copy()
        result.vert_indices = self.vert_indices.copy()
        if self.uniforms:
            result.uniforms = {key: np.array(value) for key, value in self.uniforms.items()}
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

    def replace_code(self, old: str, new: str) -> None:
        code_map = self.program_code
        for (name, code) in code_map.items():
            if code_map[name] is None:
                continue
            code_map[name] = re.sub(old, new, code_map[name])
        self.init_program()
        self.refresh_id()

    # Changing context
    def use_clip_plane(self):
        if "clip_plane" not in self.uniforms:
            return False
        return any(self.uniforms["clip_plane"])

    def set_ctx_depth_test(self, enable: bool = True) -> None:
        if enable:
            self.ctx.enable(moderngl.DEPTH_TEST)
        else:
            self.ctx.disable(moderngl.DEPTH_TEST)

    def set_ctx_clip_plane(self, enable: bool = True) -> None:
        if enable:
            gl.glEnable(gl.GL_CLIP_DISTANCE0)


    # Related to data and rendering
    def render(self, camera_uniforms: dict):
        self.update_program_uniforms(camera_uniforms)
        self.set_ctx_depth_test(self.depth_test)
        self.set_ctx_clip_plane(self.use_clip_plane())

        # TODO, generate on the fly?
        assert(self.vao is not None)
        self.vao.render(self.render_primitive)

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

    def update_program_uniforms(self, camera_uniforms: dict):
        if self.program is None:
            return
        for name, value in (*camera_uniforms.items(), *self.uniforms.items()):
            if name in self.program:
                if isinstance(value, np.ndarray) and value.ndim > 0:
                    value = tuple(value)
                self.program[name].value = value

    def get_vertex_buffer_object(self, refresh: bool = True):
        if refresh:
            self.vbo = self.ctx.buffer(self.vert_data)
        return self.vbo

    def get_index_buffer_object(self, refresh: bool = True):
        if refresh and len(self.vert_indices) > 0:
            self.ibo = self.ctx.buffer(self.vert_indices.astype(np.uint32))
        return self.ibo

    def get_vao(self, refresh: bool = True):
        # Data buffer
        vbo = self.get_vertex_buffer_object(refresh)
        ibo = self.get_index_buffer_object(refresh)
        # Vertex array object
        self.vao = self.ctx.vertex_array(
            program=self.program,
            content=[(vbo, self.vert_format, *self.vert_attributes)],
            index_buffer=ibo,
        )
        return self.vao

    def release(self):
        for obj in (self.vbo, self.ibo, self.vao):
            if obj is not None:
                obj.release()
        self.vbo = None
        self.ibo = None
        self.vao = None


class FillShaderWrapper(ShaderWrapper):
    def __init__(
        self,
        ctx: moderngl.context.Context,
        *args,
        **kwargs
    ):
        super().__init__(ctx, *args, **kwargs)

        size = (2 * DEFAULT_PIXEL_WIDTH, 2 * DEFAULT_PIXEL_HEIGHT)
        self.fill_texture = ctx.texture(
            size=size,
            components=4,
            # Important to make sure floating point (not fixed point) is
            # used so that alpha values are not clipped
            dtype='f2',
        )
        # TODO, depth buffer is not really used yet
        fill_depth = ctx.depth_renderbuffer(size)
        self.fill_fbo = ctx.framebuffer(self.fill_texture, fill_depth)
        self.fill_prog = ctx.program(
            vertex_shader='''
                #version 330

                in vec2 texcoord;
                out vec2 v_textcoord;

                void main() {
                    gl_Position = vec4((2.0 * texcoord - 1.0), 0.0, 1.0);
                    v_textcoord = texcoord;
                }
            ''',
            fragment_shader='''
                #version 330

                uniform sampler2D Texture;

                in vec2 v_textcoord;
                out vec4 frag_color;

                void main() {
                    frag_color = texture(Texture, v_textcoord);
                    frag_color = abs(frag_color);
                    if(frag_color.a == 0) discard;
                    //TODO, set gl_FragDepth;
                }
            ''',
        )

        self.fill_prog['Texture'].value = get_texture_id(self.fill_texture)

        verts = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
        self.fill_texture_vao = ctx.simple_vertex_array(
            self.fill_prog,
            ctx.buffer(verts.astype('f4').tobytes()),
            'texcoord',
        )

    def render(self, camera_uniforms: dict):
        # TODO, these are copied...
        self.update_program_uniforms(camera_uniforms)
        self.set_ctx_depth_test(self.depth_test)
        self.set_ctx_clip_plane(self.use_clip_plane())
        #
        vao = self.vao
        assert(vao is not None)
        winding = (len(self.vert_indices) == 0)
        vao.program['winding'].value = winding
        if not winding:
            vao.render(moderngl.TRIANGLES)
            return
        self.fill_fbo.clear()
        self.fill_fbo.use()
        self.ctx.blend_func = (moderngl.ONE, moderngl.ONE)
        vao.render(self.render_primitive)
        self.ctx.blend_func = moderngl.DEFAULT_BLENDING
        self.ctx.screen.use()
        self.fill_texture_vao.render(moderngl.TRIANGLE_STRIP)
