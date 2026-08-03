from __future__ import annotations

import os
import re

import OpenGL.GL as gl
import moderngl
import numpy as np

from manimlib.utils.shaders import MOBJECT_BLOCK_NAME
from manimlib.utils.shaders import check_uniform_block
from manimlib.utils.shaders import get_shader_code
from manimlib.utils.shaders import get_shared_uniform
from manimlib.utils.shaders import get_shader_program
from manimlib.utils.shaders import image_path_to_texture
from manimlib.utils.shaders import set_program_sampler
from manimlib.utils.shaders import set_program_uniform
from manimlib.utils.shaders import Uniforms

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional

UNIFORM_BLOCK_BINDING = 0


class ShaderWrapper(object):
    """
    Every shader is handed no vertex attributes at all. Each reads the records of the
    vertex buffer itself, by way of a texture pointed at it, and expands each of them
    into verts_per_record vertices, all of them triangles. See inserts/read_data.glsl.
    """

    def __init__(
        self,
        ctx: moderngl.context.Context,
        vert_data: np.ndarray,
        mobject_uniforms: Uniforms,
        shader_folder: Optional[str] = None,
        texture_paths: Optional[dict[str, str]] = None,  # A dictionary mapping names to filepaths for textures.
        depth_test: bool = False,
        code_replacements: dict[str, str] = dict(),
        verts_per_record: int = 0,
    ):
        self.ctx = ctx
        self.vert_data = vert_data
        self.shader_folder = shader_folder
        self.depth_test = depth_test
        self.verts_per_record = verts_per_record
        self.texture_paths = texture_paths or dict()

        self.mobject_uniforms = mobject_uniforms

        self.init_program_code()
        for old, new in code_replacements.items():
            self.replace_code(old, new)
        self.init_program()
        self.init_textures()
        self.init_vertex_objects()

    def __deepcopy__(self, memo):
        # Don't allow deepcopies, e.g. if the mobject with this ShaderWrapper as an
        # attribute gets copies. Returning None means the parent object with this ShaderWrapper
        # as an attribute should smoothly handle this case.
        return None

    def init_program_code(self) -> None:
        self.init_layouts()
        self.program_code: dict[str, str | None] = {
            "vertex_shader": self.get_code("vert"),
            "fragment_shader": self.get_code("frag"),
        }

    def get_code(self, name: str) -> str | None:
        return get_shader_code(
            os.path.join(self.shader_folder, f"{name}.glsl"),
            self.data_layout,
        )

    def init_layouts(self) -> None:
        """
        Describes where the fields of one of this mobject's vertex records sit, which
        is all that the shader source generated for it depends on, and so is also the
        key that source gets cached under.
        """
        dtype = self.vert_data.dtype
        self.data_layout = (
            dtype.itemsize // 4,
            tuple((name, dtype.fields[name][1] // 4) for name in dtype.names),
        )

    def init_program(self):
        if not self.shader_folder:
            self.program = None
            self.programs = []
        else:
            self.program = get_shader_program(self.ctx, **self.program_code)
            self.programs = [self.program]
        self.init_uniform_block()

    def init_uniform_block(self):
        """
        Points whichever programs read the mobject's uniforms at the buffer they will
        travel in. Its layout is settled by the mobject's uniform_dtype, so nothing is
        needed here beyond making sure the shaders agree about it.
        """
        dtype = self.mobject_uniforms.array.dtype
        self.has_uniform_block = False
        for program in self.programs:
            if program is None or not check_uniform_block(program, dtype):
                continue
            program[MOBJECT_BLOCK_NAME].binding = UNIFORM_BLOCK_BINDING
            self.has_uniform_block = True

    def init_textures(self):
        self.texture_names_to_ids = dict()
        self.textures = []
        for name, path in self.texture_paths.items():
            self.add_texture(name, image_path_to_texture(path, self.ctx))
        # The vertex buffer, exposed to the shader as a texture it can index
        self.texture_names_to_ids["Data"] = len(self.textures)

    def init_vertex_objects(self):
        self.vbo = None
        self.vaos = []
        self.data_texture = None
        self.uniform_buffer = None

    def add_texture(self, name: str, texture: moderngl.Texture):
        max_units = self.ctx.info['GL_MAX_TEXTURE_IMAGE_UNITS']
        if len(self.textures) >= max_units:
            raise ValueError(f"Unable to use more than {max_units} textures for a program")
        # The position in the list determines its id
        self.texture_names_to_ids[name] = len(self.textures)
        self.textures.append(texture)

    def replace_code(self, old: str, new: str) -> None:
        code_map = self.program_code
        for name in code_map:
            if code_map[name] is None:
                continue
            code_map[name] = re.sub(old, new, code_map[name])
        self.init_program()

    # Changing context
    def set_ctx_depth_test(self, enable: bool = True) -> None:
        if enable:
            self.ctx.enable(moderngl.DEPTH_TEST)
        else:
            self.ctx.disable(moderngl.DEPTH_TEST)

    # Adding data

    def read_in(self, data: np.ndarray):
        self.vert_data = data
        if len(data) == 0:
            if self.vbo is not None:
                self.vbo.clear()
            return

        # Either create a new buffer, or write over the existing one
        size = data.itemsize * len(data)
        if self.vbo is not None and self.vbo.size != size:
            self.release()  # This sets vbo to be None
        if self.vbo is None:
            self.vbo = self.ctx.buffer(data)
            self.generate_vaos()
        else:
            self.vbo.write(data)

    def generate_vaos(self):
        if not self.programs:
            # Nothing to draw with, e.g. a mobject holding points but naming no shader
            return
        self.init_data_texture()
        self.vaos = [
            self.ctx.vertex_array(program=program, content=[], mode=moderngl.TRIANGLES)
            for program in self.programs
        ]

    def init_data_texture(self):
        """
        Points a buffer texture at the vertex buffer, so shaders can index into
        it. This aliases the existing buffer rather than copying it, so it needs
        to be redone whenever the buffer itself is replaced.
        """
        if self.data_texture is None:
            self.data_texture = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_BUFFER, self.data_texture)
        gl.glTexBuffer(gl.GL_TEXTURE_BUFFER, gl.GL_R32F, self.vbo.glo)

    # Related to data and rendering
    def pre_render(self):
        self.set_ctx_depth_test(self.depth_test)
        for tid, texture in enumerate(self.textures):
            texture.use(tid)
        if self.data_texture is not None:
            gl.glActiveTexture(gl.GL_TEXTURE0 + self.texture_names_to_ids["Data"])
            gl.glBindTexture(gl.GL_TEXTURE_BUFFER, self.data_texture)
        if self.uniform_buffer is not None:
            self.uniform_buffer.bind_to_uniform_block(UNIFORM_BLOCK_BINDING)

    def render(self):
        n_verts = self.verts_per_record * len(self.vert_data)
        for vao in self.vaos:
            vao.render(vertices=n_verts)

    def update_program_uniforms(self):
        """
        The mobject's own uniforms live in a buffer of its own, rewritten only when
        one of them has changed. Those shared by every program, e.g. describing the
        camera, are set once a frame by set_shared_uniforms instead.
        """
        self.write_uniform_buffer()
        for program in self.programs:
            if program is None:
                continue
            for name, unit in self.texture_names_to_ids.items():
                set_program_sampler(program, name, unit)

    def write_uniform_buffer(self):
        uniforms = self.mobject_uniforms
        # A shader reading none of them declares no block for them to travel in
        if not self.has_uniform_block:
            return
        if self.uniform_buffer is None:
            self.uniform_buffer = self.ctx.buffer(uniforms.array)
        elif uniforms.changed:
            self.uniform_buffer.write(uniforms.array)
        else:
            return
        uniforms.changed = False

    def release(self):
        for obj in (self.vbo, *self.vaos):
            if obj is not None:
                obj.release()
        if self.data_texture is not None:
            gl.glDeleteTextures([self.data_texture])
        if self.uniform_buffer is not None:
            self.uniform_buffer.release()
        self.init_vertex_objects()


class SurfaceShaderWrapper(ShaderWrapper):
    """
    A surface is drawn in two passes, the side of it facing away from the camera before
    the side facing towards it, so that a see through one blends in the order it should:
    what lies behind first, what lies in front over the top of it.

    Nothing here asks whether a surface is see through. For an opaque one the depth test
    settles which side wins whatever order they arrive in, so the two passes come out
    exactly as one would.

    Which side faces which way is taken from the winding of the mesh, which follows how
    the surface is parametrized, the same thing its normals follow. A surface whose
    normals point inwards, and which is therefore already lit as though seen from inside,
    has its two passes the other way around as well.

    A surface which folds over itself needs more than which way it faces, since which of
    its own folds lies in front has nothing to do with that. Such a one can ask for
    sort_to_camera, and then its squares are drawn in order of their distance from the
    camera, furthest first, which is worked out here from the camera position every
    program is given anyway.
    """

    def __init__(self, *args, sort_to_camera: bool = False, **kwargs):
        self.sort_to_camera = sort_to_camera
        super().__init__(*args, **kwargs)

    def init_vertex_objects(self):
        super().init_vertex_objects()
        self.order_ibo = None
        self.order_vao = None

    def render(self):
        if self.sort_to_camera and self.order_triangles_by_depth():
            self.order_vao.render(vertices=self.order_ibo.size // 4)
            return
        gl.glEnable(gl.GL_CULL_FACE)
        for culled in (gl.GL_FRONT, gl.GL_BACK):
            gl.glCullFace(culled)
            super().render()
        gl.glDisable(gl.GL_CULL_FACE)

    def order_triangles_by_depth(self) -> bool:
        """
        Lists the vertices of every triangle of the mesh, three to each, those furthest
        from the camera first, in a buffer to be drawn through. False if there is nothing
        to order that way: no camera yet, or records which are no grid, as an imported
        mesh's are.
        """
        camera_position = get_shared_uniform("camera_position")
        nu, nv = self.mobject_uniforms["resolution"].astype(int)
        if camera_position is None or nu < 2 or nv < 2:
            return False

        # Where the middle of each triangle of each square sits, the two of them taking
        # the corners the vertex shader gives them, see inserts/surface_mesh.glsl
        points = self.vert_data["point"].reshape((nu, nv, 3))
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
        self.write_order_buffer(vertices.astype(np.uint32).tobytes())
        return True

    def write_order_buffer(self, data: bytes):
        if self.order_ibo is not None and self.order_ibo.size != len(data):
            self.order_ibo.release()
            self.order_vao.release()
            self.order_ibo = None
        if self.order_ibo is None:
            self.order_ibo = self.ctx.buffer(data)
            self.order_vao = self.ctx.vertex_array(
                program=self.program,
                content=[],
                index_buffer=self.order_ibo,
                index_element_size=4,
                mode=moderngl.TRIANGLES,
            )
        else:
            self.order_ibo.write(data)

    def release(self):
        for obj in (self.order_ibo, self.order_vao):
            if obj is not None:
                obj.release()
        super().release()


class VShaderWrapper(ShaderWrapper):
    """
    A bezier sits in three consecutive records of the buffer, and both shaders
    read those records themselves rather than being handed vertex attributes.
    The fill shader turns each curve into two triangles, and the stroke shader
    into one quad per polyline segment, up to MAX_STEPS of them.
    """
    fill_verts_per_curve = 6
    stroke_verts_per_curve = 6 * (32 - 1)  # MAX_STEPS in stroke/vert.glsl

    def __init__(
        self,
        ctx: moderngl.context.Context,
        vert_data: np.ndarray,
        mobject_uniforms: Uniforms,
        shader_folder: Optional[str] = None,
        texture_paths: Optional[dict[str, str]] = None,  # A dictionary mapping names to filepaths for textures.
        depth_test: bool = False,
        code_replacements: dict[str, str] = dict(),
        program_type: str | None = None,
        stroke_behind: bool = False,
    ):
        self.stroke_behind = stroke_behind
        super().__init__(
            ctx=ctx,
            vert_data=vert_data,
            shader_folder=shader_folder,
            mobject_uniforms=mobject_uniforms,
            texture_paths=texture_paths,
            depth_test=depth_test,
        )
        for old, new in code_replacements.items():
            self.replace_code_program(old, new, program_type)

    def init_program_code(self) -> None:
        self.init_layouts()
        self.program_code = {
            f"{vtype}_{name}": get_shader_code(
                os.path.join("quadratic_bezier", f"{vtype}", f"{name}.glsl"),
                self.data_layout,
            )
            for vtype in ["stroke", "fill"]
            for name in ["vert", "frag"]
        }

    def init_program(self):
        self.stroke_program = get_shader_program(
            self.ctx,
            vertex_shader=self.program_code["stroke_vert"],
            fragment_shader=self.program_code["stroke_frag"],
        )
        self.fill_program = get_shader_program(
            self.ctx,
            vertex_shader=self.program_code["fill_vert"],
            fragment_shader=self.program_code["fill_frag"],
        )
        self.programs = [self.stroke_program, self.fill_program]
        self.init_uniform_block()

    def init_vertex_objects(self):
        self.has_fill = False
        self.vbo = None
        self.stroke_vao = None
        self.fill_vao = None
        self.vaos = []
        self.data_texture = None
        self.uniform_buffer = None

    def generate_vaos(self):
        self.init_data_texture()
        # Neither shader is handed any vertex attributes, since both read the
        # buffer themselves. The border around a fill comes from the stroke
        # program too, differing only by the is_fill_border uniform.
        self.stroke_vao = self.ctx.vertex_array(
            program=self.stroke_program, content=[], mode=moderngl.TRIANGLES
        )
        self.fill_vao = self.ctx.vertex_array(
            program=self.fill_program, content=[], mode=moderngl.TRIANGLES
        )
        self.vaos = [self.stroke_vao, self.fill_vao]

    def write_uniform_buffer(self):
        # Whether there is any fill to draw, noted whenever the uniforms change rather
        # than looked at per frame. Many a mobject is stroke alone, and would otherwise
        # pay for all three of the fill passes, and the state they set, for nothing.
        uniforms = self.mobject_uniforms
        if uniforms.changed:
            self.has_fill = bool(uniforms["fill_rgba"][3] or uniforms["fill_rgba_end"][3])
        super().write_uniform_buffer()

    def get_num_curves(self) -> int:
        # Consecutive beziers share an anchor, so n points make n // 2 curves
        return len(self.vert_data) // 2

    def replace_code_program(self, old: str, new: str, program_type: str | None = None):
        if program_type is None:
            # fallback to generic behaviour
            super().replace_code(old, new)
            return

        valid = {"stroke", "fill"}
        if program_type not in valid:
            raise ValueError(f"Invalid program_type: {program_type}")

        for name in self.program_code:
            if self.program_code[name] is None:
                continue
            if not name.startswith(program_type):
                continue
            self.program_code[name] = re.sub(old, new, self.program_code[name])

        self.init_program()

    # Rendering
    def render_stroke(self):
        if self.stroke_vao is None:
            return
        set_program_uniform(self.stroke_program, "is_fill_border", False)
        self.stroke_vao.render(vertices=self.stroke_verts_per_curve * self.get_num_curves())

    def render_fill(self):
        """
        Fill is drawn with a "stencil then cover" approach.

        The first pass rasterizes the fill triangles into the stencil buffer
        alone, incrementing for front facing triangles and decrementing for back
        facing ones. Since facing is just the sign of a triangle's area in screen
        space, each pixel ends up holding the winding number of the path around
        it, with no need for a triangulation of the shape.

        The second pass draws those same triangles again, but only where that
        winding number is nonzero, and zeros out the stencil as it goes. This
        means each pixel is colored exactly once, using ordinary alpha blending,
        and that the stencil buffer is left clean for whatever draws next.

        Note this only works because a wrapper holds a single mobject. Sharing one
        pair of passes between several would merge their winding numbers into one
        region, so that overlapping mobjects would color a shared pixel once
        between them rather than each blending in turn.
        """
        if self.fill_vao is None or not self.has_fill:
            return

        gl.glEnable(gl.GL_STENCIL_TEST)

        # Pass 1: Count the winding number around each pixel. Depth testing must
        # be off here, since an occluded triangle which failed to contribute
        # would throw off the count, and depth writing must be off so that these
        # invisible triangles don't clobber the depth buffer.
        self.ctx.disable(moderngl.DEPTH_TEST)
        gl.glDepthMask(gl.GL_FALSE)
        gl.glColorMask(*4 * [gl.GL_FALSE])
        gl.glStencilFunc(gl.GL_ALWAYS, 0, 0xFF)
        gl.glStencilOpSeparate(gl.GL_FRONT, gl.GL_KEEP, gl.GL_INCR_WRAP, gl.GL_INCR_WRAP)
        gl.glStencilOpSeparate(gl.GL_BACK, gl.GL_KEEP, gl.GL_DECR_WRAP, gl.GL_DECR_WRAP)
        self.fill_vao.render(vertices=self.fill_verts_per_curve * self.get_num_curves())

        gl.glColorMask(*4 * [gl.GL_TRUE])
        gl.glDepthMask(gl.GL_TRUE)
        self.set_ctx_depth_test(self.depth_test)

        # Trace the boundary of the shape with a stroke in the fill color, which
        # is what anti-aliases the fill, since a stencil test is all or nothing.
        # It's drawn only where the winding number is zero, meaning outside the
        # shape, both because the inside is about to be filled in anyway, and so
        # that its faded edge never blends on top of the fill, which would leave
        # a seam along the boundary for partially transparent colors.
        set_program_uniform(self.stroke_program, "is_fill_border", True)
        gl.glStencilFunc(gl.GL_EQUAL, 0, 0xFF)
        gl.glStencilOp(gl.GL_KEEP, gl.GL_KEEP, gl.GL_KEEP)
        self.stroke_vao.render(vertices=self.stroke_verts_per_curve * self.get_num_curves())

        # Pass 2: Color in everywhere the winding number is nonzero. Zeroing the
        # stencil on the way through means the first triangle to cover a pixel
        # is the only one to color it, and that no clearing is needed afterwards.
        # Note that zeroing on depth failure matters just as much as on depth
        # success, else occluded fills would leave the buffer dirty.
        gl.glStencilFunc(gl.GL_NOTEQUAL, 0, 0xFF)
        gl.glStencilOp(gl.GL_KEEP, gl.GL_ZERO, gl.GL_ZERO)
        self.fill_vao.render(vertices=self.fill_verts_per_curve * self.get_num_curves())

        gl.glDisable(gl.GL_STENCIL_TEST)

    def render(self):
        if self.stroke_behind:
            self.render_stroke()
            self.render_fill()
        else:
            self.render_fill()
            self.render_stroke()


