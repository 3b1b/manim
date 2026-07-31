from __future__ import annotations

import copy
import os
import re

import OpenGL.GL as gl
import moderngl
import numpy as np

from manimlib.config import parse_cli
from manimlib.utils.shaders import get_shader_code_from_file
from manimlib.utils.shaders import get_shader_program
from manimlib.utils.shaders import image_path_to_texture
from manimlib.utils.shaders import set_program_uniform

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, Iterable
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
        code_replacements: dict[str, str] = dict(),
        verts_per_record: int = 0,
    ):
        self.ctx = ctx
        self.vert_data = vert_data
        self.vert_attributes = vert_data.dtype.names
        self.shader_folder = shader_folder
        self.depth_test = depth_test
        self.verts_per_record = verts_per_record
        self.render_primitive = moderngl.TRIANGLES if verts_per_record else render_primitive
        self.texture_paths = texture_paths or dict()

        self.program_uniform_mirror: UniformDict = dict()
        self.camera_uniforms: UniformDict = dict()
        self.bind_to_mobject_uniforms(mobject_uniforms or dict())

        self.init_program_code()
        for old, new in code_replacements.items():
            self.replace_code(old, new)
        self.init_program()
        self.init_textures()
        self.init_vertex_objects()
        self.refresh_id()

    def __deepcopy__(self, memo):
        # Don't allow deepcopies, e.g. if the mobject with this ShaderWrapper as an
        # attribute gets copies. Returning None means the parent object with this ShaderWrapper
        # as an attribute should smoothly handle this case.
        return None

    def init_program_code(self) -> None:
        def get_code(name: str) -> str | None:
            return get_shader_code_from_file(
                os.path.join(self.shader_folder, f"{name}.glsl")
            )

        self.program_code: dict[str, str | None] = {
            "vertex_shader": get_code("vert"),
            "fragment_shader": get_code("frag"),
        }
        if self.verts_per_record:
            layout = self.get_data_layout_code()
            for name, code in self.program_code.items():
                if code is not None:
                    self.program_code[name] = code.replace("// DATA_LAYOUT", layout)

    def get_data_layout_code(self) -> str:
        """
        Constants describing where each field of a vertex record sits within the
        buffer, in units of floats.

        Shaders which pull records out of the buffer themselves, rather than
        having the fields handed to them as vertex attributes, use these to index
        by field name, so that the layout doesn't have to be written out twice.
        """
        dtype = self.vert_data.dtype
        lines = [f"const int DATA_STRIDE = {dtype.itemsize // 4};"]
        lines.extend(
            f"const int DATA_OFFSET_{name} = {dtype.fields[name][1] // 4};"
            for name in dtype.names
        )
        return "\n".join(lines)

    def init_program(self):
        if not self.shader_folder:
            self.program = None
            self.vert_format = None
            self.programs = []
            return
        self.program = get_shader_program(self.ctx, **self.program_code)
        if self.verts_per_record:
            self.vert_format = None
        else:
            self.vert_format = moderngl.detect_format(self.program, self.vert_attributes)
        self.programs = [self.program]

    def init_textures(self):
        self.texture_names_to_ids = dict()
        self.textures = []
        for name, path in self.texture_paths.items():
            self.add_texture(name, image_path_to_texture(path, self.ctx))
        if self.verts_per_record:
            # The vertex buffer, exposed to the shader as a texture it can index
            self.texture_names_to_ids["Data"] = len(self.textures)

    def init_vertex_objects(self):
        self.vbo = None
        self.vaos = []
        self.vert_counts = []
        self.data_texture = None

    def add_texture(self, name: str, texture: moderngl.Texture):
        max_units = self.ctx.info['GL_MAX_TEXTURE_IMAGE_UNITS']
        if len(self.textures) >= max_units:
            raise ValueError(f"Unable to use more than {max_units} textures for a program")
        # The position in the list determines its id
        self.texture_names_to_ids[name] = len(self.textures)
        self.textures.append(texture)

    def bind_to_mobject_uniforms(self, mobject_uniforms: UniformDict):
        self.mobject_uniforms = mobject_uniforms

    def get_id(self) -> int:
        return self.id

    def refresh_id(self) -> None:
        self.id = hash("".join(map(str, [
            "".join(map(str, self.program_code.values())),
            self.mobject_uniforms,
            self.depth_test,
            self.render_primitive,
            self.texture_paths,
        ])))

    def replace_code(self, old: str, new: str) -> None:
        code_map = self.program_code
        for name in code_map:
            if code_map[name] is None:
                continue
            code_map[name] = re.sub(old, new, code_map[name])
        self.init_program()
        self.refresh_id()

    # Changing context
    def num_clip_planes(self):
        count = 0
        for n in range(4):
            key = f"clip_plane{n}"
            if key in self.mobject_uniforms and any(self.mobject_uniforms[key]):
                count = n + 1
        return count

    def set_ctx_depth_test(self, enable: bool = True) -> None:
        if enable:
            self.ctx.enable(moderngl.DEPTH_TEST)
        else:
            self.ctx.disable(moderngl.DEPTH_TEST)

    def set_ctx_clip_plane(self, num_planes: int = 0) -> None:
        clip_distances = [
            gl.GL_CLIP_DISTANCE0,
            gl.GL_CLIP_DISTANCE1,
            gl.GL_CLIP_DISTANCE2,
            gl.GL_CLIP_DISTANCE3,
        ]
        for n, clip_dist in enumerate(clip_distances):
            if n < num_planes:
                gl.glEnable(clip_dist)
            else:
                gl.glDisable(clip_dist)

    # Adding data

    def read_in(self, data_list: Iterable[np.ndarray]):
        data_list = list(data_list)
        # Keep track of which stretch of the buffer belongs to which mobject,
        # since fills must be drawn one mobject at a time. See render_fill.
        self.vert_counts = [len(data) for data in data_list]
        total_len = sum(self.vert_counts)
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
        if self.verts_per_record:
            # Nothing is fed in as a vertex attribute. The shader reads records
            # out of the buffer directly, expanding each into several vertices.
            self.init_data_texture()
            self.vaos = [
                self.ctx.vertex_array(program=program, content=[], mode=self.render_primitive)
                for program in self.programs
            ]
            return
        # Vertex array object
        self.vaos = [
            self.ctx.vertex_array(
                program=program,
                content=[(self.vbo, self.vert_format, *self.vert_attributes)],
                mode=self.render_primitive,
            )
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
        self.set_ctx_clip_plane(self.num_clip_planes())
        for tid, texture in enumerate(self.textures):
            texture.use(tid)
        if self.data_texture is not None:
            gl.glActiveTexture(gl.GL_TEXTURE0 + self.texture_names_to_ids["Data"])
            gl.glBindTexture(gl.GL_TEXTURE_BUFFER, self.data_texture)

    def render(self):
        n_verts = self.verts_per_record * len(self.vert_data) if self.verts_per_record else -1
        for vao in self.vaos:
            vao.render(vertices=n_verts)

    def update_program_uniforms(self, camera_uniforms: UniformDict):
        self.camera_uniforms = camera_uniforms
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
        if self.data_texture is not None:
            gl.glDeleteTextures([self.data_texture])
        self.init_vertex_objects()

    def release_textures(self):
        for texture in self.textures:
            texture.release()
            del texture
        self.textures = []
        self.texture_names_to_ids = dict()


class VShaderWrapper(ShaderWrapper):
    """
    A bezier sits in three consecutive records of the buffer, and both shaders
    read those records themselves rather than being handed vertex attributes.
    The fill shader turns each curve into two triangles, and the stroke shader
    into one quad per polyline segment, up to MAX_STEPS of them.
    """
    fill_verts_per_record = 6 // 3
    stroke_verts_per_record = 6 * (32 - 1) // 3  # MAX_STEPS in stroke/vert.glsl

    def __init__(
        self,
        ctx: moderngl.context.Context,
        vert_data: np.ndarray,
        shader_folder: Optional[str] = None,
        mobject_uniforms: Optional[UniformDict] = None,  # A dictionary mapping names of uniform variables
        texture_paths: Optional[dict[str, str]] = None,  # A dictionary mapping names to filepaths for textures.
        depth_test: bool = False,
        render_primitive: int = moderngl.TRIANGLES,
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
            render_primitive=render_primitive,
            verts_per_record=self.fill_verts_per_record,
        )
        for old, new in code_replacements.items():
            self.replace_code_program(old, new, program_type)

    def init_program_code(self) -> None:
        self.program_code = {
            f"{vtype}_{name}": get_shader_code_from_file(
                os.path.join("quadratic_bezier", f"{vtype}", f"{name}.glsl")
            )
            for vtype in ["stroke", "fill"]
            for name in ["vert", "frag"]
        }
        layout = self.get_data_layout_code()
        for name, code in self.program_code.items():
            if code is not None:
                self.program_code[name] = code.replace("// DATA_LAYOUT", layout)

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

    def init_vertex_objects(self):
        self.vbo = None
        self.stroke_vao = None
        self.fill_vao = None
        self.vaos = []
        self.vert_counts = []
        self.data_texture = None

    def generate_vaos(self):
        self.init_data_texture()
        # Neither shader is handed any vertex attributes, since both read the
        # buffer themselves. The border around a fill comes from the stroke
        # program too, differing only by the is_fill_border uniform.
        self.stroke_vao = self.ctx.vertex_array(
            program=self.stroke_program, content=[], mode=self.render_primitive
        )
        self.fill_vao = self.ctx.vertex_array(
            program=self.fill_program, content=[], mode=self.render_primitive
        )
        self.vaos = [self.stroke_vao, self.fill_vao]

    def set_backstroke(self, value: bool = True):
        self.stroke_behind = value

    def refresh_id(self):
        super().refresh_id()
        self.id = hash(str(self.id) + str(self.stroke_behind))
        
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
        self.refresh_id()

    # Rendering
    def render_stroke(self):
        if self.stroke_vao is None:
            return
        set_program_uniform(self.stroke_program, "is_fill_border", False)
        self.stroke_vao.render(vertices=self.stroke_verts_per_record * len(self.vert_data))

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

        This has to happen one mobject at a time. Sharing a single pair of passes
        across the whole batch would merge their winding numbers into one region,
        so that overlapping mobjects would color a shared pixel once between them
        rather than each blending in turn.
        """
        if self.fill_vao is None:
            return

        gl.glEnable(gl.GL_STENCIL_TEST)
        set_program_uniform(self.stroke_program, "is_fill_border", True)
        for first, count in self.get_fill_ranges():
            self.render_fill_range(first, count)
        gl.glDisable(gl.GL_STENCIL_TEST)

    def get_fill_ranges(self) -> list[tuple[int, int]]:
        """
        Groups the mobjects in this batch into as few stretches of the buffer as
        possible, such that no two mobjects sharing a stretch overlap on screen.

        Mobjects which don't overlap can be filled together, since then no pixel
        is touched by more than one of them, and it's worth finding these runs
        because each stretch costs a few draw calls to render.
        """
        counts = self.vert_counts
        if len(counts) == 0:
            return []
        if len(counts) == 1:
            return [(0, counts[0])]

        lows, highs = self.get_screen_bounding_boxes()
        if lows is None:
            # Without knowing where things land on screen, every mobject has to
            # be treated as if it might overlap the others
            return list(zip(np.cumsum([0, *counts[:-1]]).tolist(), counts))

        ranges = []
        first, count = 0, counts[0]
        (run_x0, run_y0), (run_x1, run_y1) = lows[0], highs[0]
        for i in range(1, len(counts)):
            (x0, y0), (x1, y1) = lows[i], highs[i]
            if x0 < run_x1 and x1 > run_x0 and y0 < run_y1 and y1 > run_y0:
                # Overlaps what's accumulated so far, so start a new stretch
                ranges.append((first, count))
                first, count = first + count, counts[i]
                run_x0, run_y0, run_x1, run_y1 = x0, y0, x1, y1
            else:
                count += counts[i]
                run_x0, run_y0 = min(run_x0, x0), min(run_y0, y0)
                run_x1, run_y1 = max(run_x1, x1), max(run_y1, y1)
        ranges.append((first, count))
        return ranges

    def get_screen_bounding_boxes(self):
        """
        Returns the lower and upper corners, in screen coordinates, of the box
        bounding each mobject in this batch.

        The projection here mirrors what emit_gl_Position.glsl does, and needs to
        stay in step with it. Bezier control points bound their curve, so taking
        the extremes of the raw points gives a box which is a little generous,
        but never too small.
        """
        uniforms = self.camera_uniforms
        if "view" not in uniforms or min(self.vert_counts) == 0:
            return None, None

        offsets = np.cumsum([0, *self.vert_counts[:-1]])
        points = self.vert_data["point"]
        lows = np.minimum.reduceat(points, offsets)
        highs = np.maximum.reduceat(points, offsets)

        # All eight corners of each box, as an (n, 8, 3) array
        pairs = np.stack([lows, highs])
        corners = np.stack([
            np.stack([pairs[i, :, 0], pairs[j, :, 1], pairs[k, :, 2]], axis=-1)
            for i in (0, 1) for j in (0, 1) for k in (0, 1)
        ], axis=1)

        # Uniforms hold the view matrix flattened in column major order. Points
        # fixed in frame skip it, and may be partway through being fixed.
        view = np.array(uniforms["view"]).reshape((4, 4)).T
        fixed = float(self.mobject_uniforms.get("is_fixed_in_frame", 0.0))
        viewed = corners @ view[:3, :3].T + view[:3, 3]
        viewed = fixed * corners + (1 - fixed) * viewed
        viewed = viewed * np.array(uniforms["frame_rescale_factors"])

        # Points at or behind the camera plane have no meaningful projection, so
        # whichever mobjects contain them get a box covering everything, which
        # keeps them from being grouped with anything else
        ws = 1.0 - viewed[:, :, 2]
        offscreen = (ws <= 1e-6).any(axis=1)
        screen = viewed[:, :, :2] / np.where(ws <= 1e-6, 1.0, ws)[:, :, np.newaxis]
        mins, maxs = screen.min(axis=1), screen.max(axis=1)
        mins[offscreen] = -np.inf
        maxs[offscreen] = np.inf

        return mins.tolist(), maxs.tolist()

    def render_fill_range(self, first: int, count: int):
        # The range is given in records, which each shader turns into a different
        # number of vertices
        fill_first = first * self.fill_verts_per_record
        fill_count = count * self.fill_verts_per_record
        border_first = first * self.stroke_verts_per_record
        border_count = count * self.stroke_verts_per_record

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
        self.fill_vao.render(first=fill_first, vertices=fill_count)

        gl.glColorMask(*4 * [gl.GL_TRUE])
        gl.glDepthMask(gl.GL_TRUE)
        self.set_ctx_depth_test(self.depth_test)

        # Trace the boundary of the shape with a stroke in the fill color, which
        # is what anti-aliases the fill, since a stencil test is all or nothing.
        # It's drawn only where the winding number is zero, meaning outside the
        # shape, both because the inside is about to be filled in anyway, and so
        # that its faded edge never blends on top of the fill, which would leave
        # a seam along the boundary for partially transparent colors.
        gl.glStencilFunc(gl.GL_EQUAL, 0, 0xFF)
        gl.glStencilOp(gl.GL_KEEP, gl.GL_KEEP, gl.GL_KEEP)
        self.stroke_vao.render(first=border_first, vertices=border_count)

        # Pass 2: Color in everywhere the winding number is nonzero. Zeroing the
        # stencil on the way through means the first triangle to cover a pixel
        # is the only one to color it, and that no clearing is needed afterwards.
        # Note that zeroing on depth failure matters just as much as on depth
        # success, else occluded fills would leave the buffer dirty.
        gl.glStencilFunc(gl.GL_NOTEQUAL, 0, 0xFF)
        gl.glStencilOp(gl.GL_KEEP, gl.GL_ZERO, gl.GL_ZERO)
        self.fill_vao.render(first=fill_first, vertices=fill_count)

    def render(self):
        if self.stroke_behind:
            self.render_stroke()
            self.render_fill()
        else:
            self.render_fill()
            self.render_stroke()


