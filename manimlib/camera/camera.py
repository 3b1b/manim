from __future__ import annotations

import itertools as it
import math

import moderngl
import numpy as np
import OpenGL.GL as gl
from PIL import Image
from scipy.spatial.transform import Rotation

from manimlib.constants import BLACK
from manimlib.constants import DEGREES, RADIANS
from manimlib.constants import DEFAULT_FPS
from manimlib.constants import DEFAULT_PIXEL_HEIGHT, DEFAULT_PIXEL_WIDTH
from manimlib.constants import FRAME_HEIGHT, FRAME_WIDTH
from manimlib.constants import DOWN, LEFT, ORIGIN, OUT, RIGHT, UP
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.mobject import Point
from manimlib.utils.color import color_to_rgba
from manimlib.utils.simple_functions import fdiv
from manimlib.utils.space_ops import normalize

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.shader_wrapper import ShaderWrapper
    from manimlib.typing import ManimColor, Vect3
    from manimlib.window import Window
    from typing import Any, Iterable

class CameraFrame(Mobject):
    def __init__(
        self,
        frame_shape: tuple[float, float] = (FRAME_WIDTH, FRAME_HEIGHT),
        center_point: Vect3 = ORIGIN,
        focal_dist_to_height: float = 2.0,
        **kwargs,
    ):
        self.frame_shape = frame_shape
        self.center_point = center_point
        self.focal_dist_to_height = focal_dist_to_height
        self.view_matrix = np.identity(4)
        super().__init__(**kwargs)

    def init_uniforms(self) -> None:
        super().init_uniforms()
        # As a quaternion
        self.uniforms["orientation"] = Rotation.identity().as_quat()
        self.uniforms["focal_dist_to_height"] = self.focal_dist_to_height

    def init_points(self) -> None:
        self.set_points([ORIGIN, LEFT, RIGHT, DOWN, UP])
        self.set_width(self.frame_shape[0], stretch=True)
        self.set_height(self.frame_shape[1], stretch=True)
        self.move_to(self.center_point)

    def set_orientation(self, rotation: Rotation):
        self.uniforms["orientation"][:] = rotation.as_quat()
        return self

    def get_orientation(self):
        return Rotation.from_quat(self.uniforms["orientation"])

    def to_default_state(self):
        self.center()
        self.set_height(FRAME_HEIGHT)
        self.set_width(FRAME_WIDTH)
        self.set_orientation(Rotation.identity())
        return self

    def get_euler_angles(self):
        return self.get_orientation().as_euler("zxz")[::-1]

    def get_theta(self):
        return self.get_euler_angles()[0]

    def get_phi(self):
        return self.get_euler_angles()[1]

    def get_gamma(self):
        return self.get_euler_angles()[2]

    def get_inverse_camera_rotation_matrix(self):
        return self.get_orientation().as_matrix().T

    def get_view_matrix(self):
        """
        Returns a 4x4 for the affine transformation mapping a point
        into the camera's internal coordinate system
        """
        result = self.view_matrix
        result[:] = np.identity(4)
        result[:3, 3] = -self.get_center()
        rotation = np.identity(4)
        rotation[:3, :3] = self.get_inverse_camera_rotation_matrix()
        result[:] = np.dot(rotation, result)
        return result

    def rotate(self, angle: float, axis: np.ndarray = OUT, **kwargs):
        rot = Rotation.from_rotvec(angle * normalize(axis))
        self.set_orientation(rot * self.get_orientation())
        return self

    def set_euler_angles(
        self,
        theta: float | None = None,
        phi: float | None = None,
        gamma: float | None = None,
        units: float = RADIANS
    ):
        eulers = self.get_euler_angles()  # theta, phi, gamma
        for i, var in enumerate([theta, phi, gamma]):
            if var is not None:
                eulers[i] = var * units
        self.set_orientation(Rotation.from_euler("zxz", eulers[::-1]))
        return self

    def reorient(
        self,
        theta_degrees: float | None = None,
        phi_degrees: float | None = None,
        gamma_degrees: float | None = None,
    ):
        """
        Shortcut for set_euler_angles, defaulting to taking
        in angles in degrees
        """
        self.set_euler_angles(theta_degrees, phi_degrees, gamma_degrees, units=DEGREES)
        return self

    def set_theta(self, theta: float):
        return self.set_euler_angles(theta=theta)

    def set_phi(self, phi: float):
        return self.set_euler_angles(phi=phi)

    def set_gamma(self, gamma: float):
        return self.set_euler_angles(gamma=gamma)

    def increment_theta(self, dtheta: float):
        self.rotate(dtheta, OUT)
        return self

    def increment_phi(self, dphi: float):
        self.rotate(dphi, self.get_inverse_camera_rotation_matrix()[0])
        return self

    def increment_gamma(self, dgamma: float):
        self.rotate(dgamma, self.get_inverse_camera_rotation_matrix()[2])
        return self

    def set_focal_distance(self, focal_distance: float):
        self.uniforms["focal_dist_to_height"] = focal_distance / self.get_height()
        return self

    def set_field_of_view(self, field_of_view: float):
        self.uniforms["focal_dist_to_height"] = 2 * math.tan(field_of_view / 2)
        return self

    def get_shape(self):
        return (self.get_width(), self.get_height())

    def get_center(self) -> np.ndarray:
        # Assumes first point is at the center
        return self.get_points()[0]

    def get_width(self) -> float:
        points = self.get_points()
        return points[2, 0] - points[1, 0]

    def get_height(self) -> float:
        points = self.get_points()
        return points[4, 1] - points[3, 1]

    def get_focal_distance(self) -> float:
        return self.uniforms["focal_dist_to_height"] * self.get_height()

    def get_field_of_view(self) -> float:
        return 2 * math.atan(self.uniforms["focal_dist_to_height"] / 2)

    def get_implied_camera_location(self) -> np.ndarray:
        to_camera = self.get_inverse_camera_rotation_matrix()[2]
        dist = self.get_focal_distance()
        return self.get_center() + dist * to_camera


class Camera(object):
    def __init__(
        self,
        window: Window | None = None,
        background_image: str | None = None,
        frame_config: dict = dict(),
        pixel_width: int = DEFAULT_PIXEL_WIDTH,
        pixel_height: int = DEFAULT_PIXEL_HEIGHT,
        fps: int = DEFAULT_FPS,
        # Note: frame height and width will be resized to match the pixel aspect ratio
        background_color: ManimColor = BLACK,
        background_opacity: float = 1.0,
        # Points in vectorized mobjects with norm greater
        # than this value will be rescaled.
        max_allowable_norm: float = FRAME_WIDTH,
        image_mode: str = "RGBA",
        n_channels: int = 4,
        pixel_array_dtype: type = np.uint8,
        light_source_position: Vect3 = np.array([-10, 10, 10]),
        # Although vector graphics handle antialiasing fine
        # without multisampling, for 3d scenes one might want
        # to set samples to be greater than 0.
        samples: int = 0,
    ):
        self.background_image = background_image
        self.window = window
        self.default_pixel_shape = (pixel_width, pixel_height)
        self.fps = fps
        self.max_allowable_norm = max_allowable_norm
        self.image_mode = image_mode
        self.n_channels = n_channels
        self.pixel_array_dtype = pixel_array_dtype
        self.light_source_position = light_source_position
        self.samples = samples

        self.rgb_max_val: float = np.iinfo(self.pixel_array_dtype).max
        self.background_rgba: list[float] = list(color_to_rgba(
            background_color, background_opacity
        ))
        self.perspective_uniforms = dict()
        self.init_frame(**frame_config)
        self.init_context(window)
        self.init_shaders()
        self.init_textures()
        self.init_light_source()
        self.refresh_perspective_uniforms()
        self.init_fill_fbo(self.ctx)  # Experimental
        # A cached map from mobjects to their associated list of render groups
        # so that these render groups are not regenerated unnecessarily for static
        # mobjects
        self.mob_to_render_groups = {}

    def init_frame(self, **config) -> None:
        self.frame = CameraFrame(**config)

    def init_context(self, window: Window | None = None) -> None:
        if window is None:
            self.ctx = moderngl.create_standalone_context()
            self.fbo = self.get_fbo(self.samples)
        else:
            self.ctx = window.ctx
            self.fbo = self.ctx.detect_framebuffer()
        self.fbo.use()
        self.set_ctx_blending()

        self.ctx.enable(moderngl.PROGRAM_POINT_SIZE)

        # This is the frame buffer we'll draw into when emitting frames
        self.draw_fbo = self.get_fbo(samples=0)

    def init_fill_fbo(self, ctx):
        # Experimental
        self.fill_texture = ctx.texture(
            size=self.get_pixel_shape(),
            components=4,
            samples=self.samples,
        )
        # TODO, depth buffer is not really used yet
        fill_depth = ctx.depth_renderbuffer(self.get_pixel_shape(), samples=self.samples)
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
                    if(frag_color.a == 0) discard;
                }
            ''',
        )
        tid = self.n_textures
        self.fill_texture.use(tid)
        self.fill_prog['Texture'].value = tid
        self.n_textures += 1
        verts = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
        self.fill_texture_vao = ctx.simple_vertex_array(
            self.fill_prog,
            ctx.buffer(verts.astype('f4').tobytes()),
            'texcoord',
        )

    def set_ctx_blending(self, enable: bool = True) -> None:
        if enable:
            self.ctx.enable(moderngl.BLEND)
        else:
            self.ctx.disable(moderngl.BLEND)

    def set_ctx_depth_test(self, enable: bool = True) -> None:
        if enable:
            self.ctx.enable(moderngl.DEPTH_TEST)
        else:
            self.ctx.disable(moderngl.DEPTH_TEST)

    def set_ctx_clip_plane(self, enable: bool = True) -> None:
        if enable:
            gl.glEnable(gl.GL_CLIP_DISTANCE0)

    def init_light_source(self) -> None:
        self.light_source = Point(self.light_source_position)

    # Methods associated with the frame buffer
    def get_fbo(
        self,
        samples: int = 0
    ) -> moderngl.Framebuffer:
        return self.ctx.framebuffer(
            color_attachments=self.ctx.texture(
                self.default_pixel_shape,
                components=self.n_channels,
                samples=samples,
            ),
            depth_attachment=self.ctx.depth_renderbuffer(
                self.default_pixel_shape,
                samples=samples
            )
        )

    def clear(self) -> None:
        self.fbo.clear(*self.background_rgba)

    def get_raw_fbo_data(self, dtype: str = 'f1') -> bytes:
        # Copy blocks from fbo into draw_fbo using Blit
        gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, self.fbo.glo)
        gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, self.draw_fbo.glo)
        if self.window is not None:
            src_viewport = self.window.viewport
        else:
            src_viewport = self.fbo.viewport
        gl.glBlitFramebuffer(
            *src_viewport,
            *self.draw_fbo.viewport,
            gl.GL_COLOR_BUFFER_BIT, gl.GL_LINEAR
        )
        return self.draw_fbo.read(
            viewport=self.draw_fbo.viewport,
            components=self.n_channels,
            dtype=dtype,
        )

    def get_image(self) -> Image.Image:
        return Image.frombytes(
            'RGBA',
            self.get_pixel_shape(),
            self.get_raw_fbo_data(),
            'raw', 'RGBA', 0, -1
        )

    def get_pixel_array(self) -> np.ndarray:
        raw = self.get_raw_fbo_data(dtype='f4')
        flat_arr = np.frombuffer(raw, dtype='f4')
        arr = flat_arr.reshape([*reversed(self.draw_fbo.size), self.n_channels])
        arr = arr[::-1]
        # Convert from float
        return (self.rgb_max_val * arr).astype(self.pixel_array_dtype)

    # Needed?
    def get_texture(self) -> moderngl.Texture:
        texture = self.ctx.texture(
            size=self.fbo.size,
            components=4,
            data=self.get_raw_fbo_data(),
            dtype='f4'
        )
        return texture

    # Getting camera attributes
    def get_pixel_size(self) -> float:
        return self.frame.get_shape()[0] / self.get_pixel_shape()[0]

    def get_pixel_shape(self) -> tuple[int, int]:
        return self.draw_fbo.size

    def get_pixel_width(self) -> int:
        return self.get_pixel_shape()[0]

    def get_pixel_height(self) -> int:
        return self.get_pixel_shape()[1]

    def get_aspect_ratio(self):
        pw, ph = self.get_pixel_shape()
        return pw / ph

    def get_frame_height(self) -> float:
        return self.frame.get_height()

    def get_frame_width(self) -> float:
        return self.frame.get_width()

    def get_frame_shape(self) -> tuple[float, float]:
        return (self.get_frame_width(), self.get_frame_height())

    def get_frame_center(self) -> np.ndarray:
        return self.frame.get_center()

    def get_location(self) -> tuple[float, float, float]:
        return self.frame.get_implied_camera_location()

    def resize_frame_shape(self, fixed_dimension: bool = False) -> None:
        """
        Changes frame_shape to match the aspect ratio
        of the pixels, where fixed_dimension determines
        whether frame_height or frame_width
        remains fixed while the other changes accordingly.
        """
        frame_height = self.get_frame_height()
        frame_width = self.get_frame_width()
        aspect_ratio = self.get_aspect_ratio()
        if not fixed_dimension:
            frame_height = frame_width / aspect_ratio
        else:
            frame_width = aspect_ratio * frame_height
        self.frame.set_height(frame_height, stretch=true)
        self.frame.set_width(frame_width, stretch=true)

    # Rendering
    def capture(self, *mobjects: Mobject) -> None:
        self.refresh_perspective_uniforms()
        for mobject in mobjects:
            for render_group in self.get_render_group_list(mobject):
                self.render(render_group)

    def render(self, render_group: dict[str, Any]) -> None:
        shader_wrapper = render_group["shader_wrapper"]
        shader_program = render_group["prog"]
        primitive = int(shader_wrapper.render_primitive)
        self.set_shader_uniforms(shader_program, shader_wrapper)
        self.set_ctx_depth_test(shader_wrapper.depth_test)
        self.set_ctx_clip_plane(shader_wrapper.use_clip_plane)

        if shader_wrapper.is_fill:
            self.render_fill(render_group["vao"], primitive)
        else:
            render_group["vao"].render(primitive)

        if render_group["single_use"]:
            self.release_render_group(render_group)

    def render_fill(self, vao, render_primitive: int):
        """
        VMobject fill is handled in a special way, where emited triangles
        must be blended with moderngl.FUNC_SUBTRACT so as to effectively compute
        a winding number around each pixel. This is rendered to a separate texture,
        then that texture is overlayed onto the current fbo
        """
        self.fill_fbo.clear(0.0, 0.0, 0.0, 0.0)
        self.fill_fbo.use()
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.ONE, moderngl.ONE
        self.ctx.blend_equation = moderngl.FUNC_SUBTRACT
        vao.render(render_primitive, instances=2)
        self.ctx.blend_func = moderngl.DEFAULT_BLENDING
        self.ctx.blend_equation = moderngl.FUNC_ADD
        self.fbo.use()
        self.fill_texture.use(0)
        self.fill_prog['Texture'].value = 0
        self.fill_texture_vao.render(moderngl.TRIANGLE_STRIP)

    def get_render_group_list(self, mobject: Mobject) -> Iterable[dict[str, Any]]:
        if mobject.is_changing():
            return self.generate_render_group_list(mobject)

        # Otherwise, cache result for later use
        key = id(mobject)
        if key not in self.mob_to_render_groups:
            self.mob_to_render_groups[key] = list(self.generate_render_group_list(mobject))
        return self.mob_to_render_groups[key]

    def generate_render_group_list(self, mobject: Mobject) -> Iterable[dict[str, Any]]:
        return (
            self.get_render_group(sw, single_use=mobject.is_changing())
            for sw in mobject.get_shader_wrapper_list()
        )

    def get_render_group(
        self,
        shader_wrapper: ShaderWrapper,
        single_use: bool = True
    ) -> dict[str, Any]:
        # Data buffer
        vert_data = shader_wrapper.vert_data
        indices = shader_wrapper.vert_indices
        if len(indices) == 0:
            ibo = None
        elif single_use:
            ibo = self.ctx.buffer(indices.astype(np.uint32))
        else:
            # The vao.render call is strangely longer
            # when an index buffer is used, so if the
            # mobject is not changing, meaning only its
            # uniforms are being updated, just create
            # a larger data array based on the indices
            # and don't bother with the ibo
            vert_data = vert_data[indices]
            ibo = None
        vbo = self.ctx.buffer(vert_data)

        # Program and vertex array
        shader_program, vert_format = self.get_shader_program(shader_wrapper)
        attributes = shader_wrapper.vert_attributes
        vao = self.ctx.vertex_array(
            program=shader_program,
            content=[(vbo, vert_format, *attributes)],
            index_buffer=ibo,
        )
        return {
            "vbo": vbo,
            "ibo": ibo,
            "vao": vao,
            "prog": shader_program,
            "shader_wrapper": shader_wrapper,
            "single_use": single_use,
        }

    def release_render_group(self, render_group: dict[str, Any]) -> None:
        for key in ["vbo", "ibo", "vao"]:
            if render_group[key] is not None:
                render_group[key].release()

    def refresh_static_mobjects(self) -> None:
        for render_group in it.chain(*self.mob_to_render_groups.values()):
            self.release_render_group(render_group)
        self.mob_to_render_groups = {}

    # Shaders
    def init_shaders(self) -> None:
        # Initialize with the null id going to None
        self.id_to_shader_program: dict[int, tuple[moderngl.Program, str] | None] = {hash(""): None}

    def get_shader_program(
        self,
        shader_wrapper: ShaderWrapper
    ) -> tuple[moderngl.Program, str] | None:
        sid = shader_wrapper.get_program_id()
        if sid not in self.id_to_shader_program:
            # Create shader program for the first time, then cache
            # in the id_to_shader_program dictionary
            program = self.ctx.program(**shader_wrapper.get_program_code())
            vert_format = moderngl.detect_format(program, shader_wrapper.vert_attributes)
            self.id_to_shader_program[sid] = (program, vert_format)
        return self.id_to_shader_program[sid]

    def set_shader_uniforms(
        self,
        shader: moderngl.Program,
        shader_wrapper: ShaderWrapper
    ) -> None:
        for name, path in shader_wrapper.texture_paths.items():
            tid = self.get_texture_id(path)
            shader[name].value = tid
        for name, value in it.chain(self.perspective_uniforms.items(), shader_wrapper.uniforms.items()):
            if name in shader:
                if isinstance(value, np.ndarray) and value.ndim > 0:
                    value = tuple(value)
                shader[name].value = value

    def refresh_perspective_uniforms(self) -> None:
        frame = self.frame
        view_matrix = frame.get_view_matrix()
        light_pos = self.light_source.get_location()
        cam_pos = self.frame.get_implied_camera_location()

        self.perspective_uniforms.update(
            frame_shape=frame.get_shape(),
            pixel_size=self.get_pixel_size(),
            view=tuple(view_matrix.T.flatten()),
            camera_position=tuple(cam_pos),
            light_position=tuple(light_pos),
            focal_distance=frame.get_focal_distance(),
        )

    def init_textures(self) -> None:
        self.n_textures: int = 0
        self.path_to_texture: dict[
            str, tuple[int, moderngl.Texture]
        ] = {}

    def get_texture_id(self, path: str) -> int:
        if path not in self.path_to_texture:
            tid = self.n_textures
            self.n_textures += 1
            im = Image.open(path).convert("RGBA")
            texture = self.ctx.texture(
                size=im.size,
                components=len(im.getbands()),
                data=im.tobytes(),
            )
            texture.use(location=tid)
            self.path_to_texture[path] = (tid, texture)
        return self.path_to_texture[path][0]

    def release_texture(self, path: str):
        tid_and_texture = self.path_to_texture.pop(path, None)
        if tid_and_texture:
            tid_and_texture[1].release()
        return self


# Mostly just defined so old scenes don't break
class ThreeDCamera(Camera):
    def __init__(self, samples: int = 4, **kwargs):
        super().__init__(samples=samples, **kwargs)
