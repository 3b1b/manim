import moderngl
from colour import Color
import OpenGL.GL as gl

from PIL import Image
import numpy as np
import itertools as it

from manimlib.constants import *
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.mobject import Point
from manimlib.utils.config_ops import digest_config
from manimlib.utils.bezier import interpolate
from manimlib.utils.iterables import batch_by_property
from manimlib.utils.simple_functions import fdiv
from manimlib.utils.shaders import shader_info_to_id
from manimlib.utils.shaders import shader_id_to_info
from manimlib.utils.shaders import get_shader_code_from_file
from manimlib.utils.simple_functions import clip
from manimlib.utils.space_ops import angle_of_vector
from manimlib.utils.space_ops import rotation_matrix_transpose_from_quaternion
from manimlib.utils.space_ops import rotation_matrix_transpose
from manimlib.utils.space_ops import quaternion_from_angle_axis
from manimlib.utils.space_ops import quaternion_mult


class CameraFrame(Mobject):
    CONFIG = {
        "frame_shape": (FRAME_WIDTH, FRAME_HEIGHT),
        "center_point": ORIGIN,
        # Theta, phi, gamma
        "euler_angles": [0, 0, 0],
        "focal_distance": 4,
    }

    def init_points(self):
        self.points = np.array([ORIGIN, LEFT, RIGHT, DOWN, UP])
        self.set_width(self.frame_shape[0], stretch=True)
        self.set_height(self.frame_shape[1], stretch=True)
        self.move_to(self.center_point)
        self.euler_angles = np.array(self.euler_angles, dtype='float64')

    def to_default_state(self):
        self.center()
        self.set_height(FRAME_HEIGHT)
        self.set_width(FRAME_WIDTH)
        self.set_rotation(0, 0, 0)
        return self

    def get_inverse_camera_position_matrix(self):
        result = np.identity(4)
        # First shift so that origin of real space coincides with camera origin
        result[:3, 3] = -self.get_center().T
        # Rotate based on camera orientation
        result[:3, :3] = np.dot(self.get_inverse_camera_rotation_matrix(), result[:3, :3])
        return result

    def get_inverse_camera_rotation_matrix(self):
        theta, phi, gamma = self.euler_angles
        quat = quaternion_mult(
            quaternion_from_angle_axis(theta, OUT, axis_normalized=True),
            quaternion_from_angle_axis(phi, RIGHT, axis_normalized=True),
            quaternion_from_angle_axis(gamma, OUT, axis_normalized=True),
        )
        return rotation_matrix_transpose_from_quaternion(quat)

    def rotate(self, angle, axis=OUT, **kwargs):
        curr_rot_T = self.get_inverse_camera_rotation_matrix()
        added_rot_T = rotation_matrix_transpose(angle, axis)
        new_rot_T = np.dot(curr_rot_T, added_rot_T)
        Fz = new_rot_T[2]
        phi = np.arccos(Fz[2])
        theta = angle_of_vector(Fz[:2]) + PI / 2
        partial_rot_T = np.dot(
            rotation_matrix_transpose(phi, RIGHT),
            rotation_matrix_transpose(theta, OUT),
        )
        gamma = angle_of_vector(np.dot(partial_rot_T, new_rot_T.T)[:, 0])
        # TODO, write a function that converts quaternions to euler angles
        self.euler_angles[:] = theta, phi, gamma
        return self

    def set_rotation(self, theta=0, phi=0, gamma=0):
        self.euler_angles[:] = theta, phi, gamma
        return self

    def set_theta(self, theta):
        self.euler_angles[0] = theta

    def set_phi(self, phi):
        self.euler_angles[1] = phi

    def set_gamma(self, gamma):
        self.euler_angles[2] = gamma

    def increment_theta(self, dtheta):
        self.euler_angles[0] += dtheta
        return self

    def increment_phi(self, dphi):
        self.euler_angles[1] = clip(self.euler_angles[1] + dphi, 0, PI)
        return self

    def increment_gamma(self, dgamma):
        self.euler_angles[2] += dgamma
        return self

    def get_shape(self):
        return (
            self.points[:, 0].max() - self.points[:, 0].min(),
            self.points[:, 1].max() - self.points[:, 1].min(),
        )

    def get_center(self):
        # Assumes first point is at the center
        return self.points[0]

    def get_focal_distance(self):
        return self.focal_distance

    def interpolate(self, frame1, frame2, alpha, path_func):
        self.euler_angles[:] = interpolate(
            frame1.euler_angles,
            frame2.euler_angles,
            alpha
        )
        self.points = interpolate(
            frame1.points,
            frame2.points,
            alpha,
        )


class Camera(object):
    CONFIG = {
        "background_image": None,
        "frame_config": {},
        "pixel_height": DEFAULT_PIXEL_HEIGHT,
        "pixel_width": DEFAULT_PIXEL_WIDTH,
        "frame_rate": DEFAULT_FRAME_RATE,  # TODO, move this elsewhere
        # Note: frame height and width will be resized to match
        # the pixel aspect ratio
        "background_color": BLACK,
        "background_opacity": 1,
        # Points in vectorized mobjects with norm greater
        # than this value will be rescaled.
        "max_allowable_norm": FRAME_WIDTH,
        "image_mode": "RGBA",
        "n_channels": 4,
        "pixel_array_dtype": 'uint8',
        "light_source_position": [-10, 10, 10],
        # Measured in pixel widths, used for vector graphics
        "anti_alias_width": 1.5,
        # Although vector graphics handle antialiasing fine
        # without multisampling, for 3d scenes one might want
        # to set samples to be greater than 0.
        "samples": 0,
    }

    def __init__(self, ctx=None, **kwargs):
        digest_config(self, kwargs, locals())
        self.rgb_max_val = np.iinfo(self.pixel_array_dtype).max
        self.background_rgba = [
            *Color(self.background_color).get_rgb(),
            self.background_opacity
        ]
        self.init_frame()
        self.init_context(ctx)
        self.init_shaders()
        self.init_textures()
        self.init_light_source()

    def init_frame(self):
        self.frame = CameraFrame(**self.frame_config)

    def init_context(self, ctx=None):
        if ctx is None:
            ctx = moderngl.create_standalone_context()
            fbo = self.get_fbo(ctx, 0)
        else:
            fbo = ctx.detect_framebuffer()

        # For multisample antialiasing
        fbo_msaa = self.get_fbo(ctx, self.samples)
        fbo_msaa.use()

        ctx.enable(moderngl.BLEND)
        ctx.blend_func = (
            moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA,
            moderngl.ONE, moderngl.ONE
        )

        self.ctx = ctx
        self.fbo = fbo
        self.fbo_msaa = fbo_msaa

    def init_light_source(self):
        self.light_source = Point(self.light_source_position)

    # Methods associated with the frame buffer
    def get_fbo(self, ctx, samples=0):
        pw = self.pixel_width
        ph = self.pixel_height
        return ctx.framebuffer(
            color_attachments=ctx.texture(
                (pw, ph),
                components=self.n_channels,
                samples=samples,
            ),
            depth_attachment=ctx.depth_renderbuffer(
                (pw, ph),
                samples=samples
            )
        )

    def clear(self):
        self.fbo.clear(*self.background_rgba)
        self.fbo_msaa.clear(*self.background_rgba)

    def reset_pixel_shape(self, new_width, new_height):
        self.pixel_width = new_width
        self.pixel_height = new_height
        self.refresh_shader_uniforms()

    def get_raw_fbo_data(self, dtype='f1'):
        # Copy blocks from the fbo_msaa to the drawn fbo using Blit
        pw, ph = (self.pixel_width, self.pixel_height)
        gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, self.fbo_msaa.glo)
        gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, self.fbo.glo)
        gl.glBlitFramebuffer(0, 0, pw, ph, 0, 0, pw, ph, gl.GL_COLOR_BUFFER_BIT, gl.GL_LINEAR)
        return self.fbo.read(
            viewport=self.fbo.viewport,
            components=self.n_channels,
            dtype=dtype,
        )

    def get_image(self, pixel_array=None):
        return Image.frombytes(
            'RGBA',
            self.get_pixel_shape(),
            self.get_raw_fbo_data(),
            'raw', 'RGBA', 0, -1
        )

    def get_pixel_array(self):
        raw = self.get_raw_fbo_data(dtype='f4')
        flat_arr = np.frombuffer(raw, dtype='f4')
        arr = flat_arr.reshape([*self.fbo.size, self.n_channels])
        # Convert from float
        return (self.rgb_max_val * arr).astype(self.pixel_array_dtype)

    # Needed?
    def get_texture(self):
        texture = self.ctx.texture(
            size=self.fbo.size,
            components=4,
            data=self.get_raw_fbo_data(),
            dtype='f4'
        )
        return texture

    # Getting camera attributes
    def get_pixel_shape(self):
        return self.fbo.viewport[2:4]
        # return (self.pixel_width, self.pixel_height)

    def get_pixel_width(self):
        return self.get_pixel_shape()[0]

    def get_pixel_height(self):
        return self.get_pixel_shape()[1]

    def get_frame_height(self):
        return self.frame.get_height()

    def get_frame_width(self):
        return self.frame.get_width()

    def get_frame_shape(self):
        return (self.get_frame_width(), self.get_frame_height())

    def get_frame_center(self):
        return self.frame.get_center()

    def resize_frame_shape(self, fixed_dimension=0):
        """
        Changes frame_shape to match the aspect ratio
        of the pixels, where fixed_dimension determines
        whether frame_height or frame_width
        remains fixed while the other changes accordingly.
        """
        pixel_height = self.get_pixel_height()
        pixel_width = self.get_pixel_width()
        frame_height = self.get_frame_height()
        frame_width = self.get_frame_width()
        aspect_ratio = fdiv(pixel_width, pixel_height)
        if fixed_dimension == 0:
            frame_height = frame_width / aspect_ratio
        else:
            frame_width = aspect_ratio * frame_height
        self.frame.set_height(frame_height)
        self.frame.set_width(frame_width)

    def pixel_coords_to_space_coords(self, px, py, relative=False):
        # pw, ph = self.fbo.size
        # Bad hack, not sure why this is needed.
        pw, ph = self.get_pixel_shape()
        pw //= 2
        ph //= 2
        fw, fh = self.get_frame_shape()
        fc = self.get_frame_center()
        if relative:
            return 2 * np.array([px / pw, py / ph, 0])
        else:
            # Only scale wrt one axis
            scale = fh / ph
            return fc + scale * np.array([(px - pw / 2), (py - ph / 2), 0])

    # Rendering
    def capture(self, *mobjects, **kwargs):
        self.refresh_shader_uniforms()

        shader_infos = it.chain(*[
            mob.get_shader_info_list()
            for mob in mobjects
        ])
        batches = batch_by_property(shader_infos, shader_info_to_id)

        for info_group, sid in batches:
            data = np.hstack([info["data"] for info in info_group])
            shader = self.get_shader(info_group[0])
            render_primative = int(info_group[0]["render_primative"])
            depth_test = info_group[0]["depth_test"]
            self.render(shader, data, render_primative, depth_test)

    def render(self, shader, data, render_primative, depth_test=False):
        if data is None or len(data) == 0:
            return
        if shader is None:
            return
        if depth_test:
            self.ctx.enable(moderngl.DEPTH_TEST)
        else:
            self.ctx.disable(moderngl.DEPTH_TEST)

        vbo = self.ctx.buffer(data.tobytes())
        vao = self.ctx.simple_vertex_array(shader, vbo, *data.dtype.names)
        vao.render(render_primative)

    # Shaders
    def init_shaders(self):
        # Initialize with the null id going to None
        self.id_to_shader = {"": None}

    def get_shader(self, shader_info):
        sid = shader_info_to_id(shader_info)
        if sid not in self.id_to_shader:
            info = shader_id_to_info(sid)
            shader = self.ctx.program(
                vertex_shader=get_shader_code_from_file(info["vert"]),
                geometry_shader=get_shader_code_from_file(info["geom"]),
                fragment_shader=get_shader_code_from_file(info["frag"]),
            )
            if info["texture_paths"]:
                for name, path in info["texture_paths"].items():
                    tid = self.get_texture_id(path)
                    shader[name].value = tid
            self.set_shader_uniforms(shader, sid)
            self.id_to_shader[sid] = shader
        return self.id_to_shader[sid]

    def set_shader_uniforms(self, shader, sid):
        if shader is None:
            return

        pw, ph = self.get_pixel_shape()
        fw, fh = self.frame.get_shape()
        anti_alias_width = self.anti_alias_width / (ph / fh)
        transform = self.frame.get_inverse_camera_position_matrix()
        light = self.light_source.get_location()
        transformed_light = np.dot(transform, [*light, 1])[:3]
        mapping = dict()
        mapping['to_screen_space'] = tuple(transform.T.flatten())
        mapping['frame_shape'] = self.frame.get_shape()
        mapping['focal_distance'] = self.frame.get_focal_distance()
        mapping['anti_alias_width'] = anti_alias_width
        mapping['light_source_position'] = tuple(transformed_light)
        # Potentially overwrite with whatever came from the mobject
        mapping.update(shader_id_to_info(sid)["uniforms"])

        for key, value in mapping.items():
            try:
                shader[key].value = value
            except KeyError:
                pass

    def refresh_shader_uniforms(self):
        for sid, shader in self.id_to_shader.items():
            self.set_shader_uniforms(shader, sid)

    def init_textures(self):
        self.path_to_texture_id = {}

    def get_texture_id(self, path):
        if path not in self.path_to_texture_id:
            # A way to increase tid's sequentially
            tid = len(self.path_to_texture_id)
            im = Image.open(path)
            texture = self.ctx.texture(
                size=im.size,
                components=len(im.getbands()),
                data=im.tobytes(),
            )
            texture.use(location=tid)
            self.path_to_texture_id[path] = tid
        return self.path_to_texture_id[path]


class ThreeDCamera(Camera):
    CONFIG = {
        "samples": 8,
    }
