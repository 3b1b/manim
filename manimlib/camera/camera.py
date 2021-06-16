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
from manimlib.utils.simple_functions import fdiv
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
        "focal_distance": 2,
    }

    def init_data(self):
        super().init_data()
        self.data["euler_angles"] = np.array(self.euler_angles, dtype=float)
        self.refresh_rotation_matrix()

    def init_points(self):
        self.set_points([ORIGIN, LEFT, RIGHT, DOWN, UP])
        self.set_width(self.frame_shape[0], stretch=True)
        self.set_height(self.frame_shape[1], stretch=True)
        self.move_to(self.center_point)

    def to_default_state(self):
        self.center()
        self.set_height(FRAME_HEIGHT)
        self.set_width(FRAME_WIDTH)
        self.set_euler_angles(0, 0, 0)
        return self

    def get_euler_angles(self):
        return self.data["euler_angles"]

    def get_inverse_camera_rotation_matrix(self):
        return self.inverse_camera_rotation_matrix

    def refresh_rotation_matrix(self):
        # Rotate based on camera orientation
        theta, phi, gamma = self.get_euler_angles()
        quat = quaternion_mult(
            quaternion_from_angle_axis(theta, OUT, axis_normalized=True),
            quaternion_from_angle_axis(phi, RIGHT, axis_normalized=True),
            quaternion_from_angle_axis(gamma, OUT, axis_normalized=True),
        )
        self.inverse_camera_rotation_matrix = rotation_matrix_transpose_from_quaternion(quat)

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
        self.set_euler_angles(theta, phi, gamma)
        return self

    def set_euler_angles(self, theta=None, phi=None, gamma=None, units=RADIANS):
        if theta is not None:
            self.data["euler_angles"][0] = theta * units
        if phi is not None:
            self.data["euler_angles"][1] = phi * units
        if gamma is not None:
            self.data["euler_angles"][2] = gamma * units
        self.refresh_rotation_matrix()
        return self

    def reorient(self, theta_degrees=None, phi_degrees=None, gamma_degrees=None):
        """
        Shortcut for set_euler_angles, defaulting to taking
        in angles in degrees
        """
        self.set_euler_angles(theta_degrees, phi_degrees, gamma_degrees, units=DEGREES)
        return self

    def set_theta(self, theta):
        return self.set_euler_angles(theta=theta)

    def set_phi(self, phi):
        return self.set_euler_angles(phi=phi)

    def set_gamma(self, gamma):
        return self.set_euler_angles(gamma=gamma)

    def increment_theta(self, dtheta):
        self.data["euler_angles"][0] += dtheta
        self.refresh_rotation_matrix()
        return self

    def increment_phi(self, dphi):
        phi = self.data["euler_angles"][1]
        new_phi = clip(phi + dphi, 0, PI)
        self.data["euler_angles"][1] = new_phi
        self.refresh_rotation_matrix()
        return self

    def increment_gamma(self, dgamma):
        self.data["euler_angles"][2] += dgamma
        self.refresh_rotation_matrix()
        return self

    def get_shape(self):
        return (self.get_width(), self.get_height())

    def get_center(self):
        # Assumes first point is at the center
        return self.get_points()[0]

    def get_width(self):
        points = self.get_points()
        return points[2, 0] - points[1, 0]

    def get_height(self):
        points = self.get_points()
        return points[4, 1] - points[3, 1]

    def get_focal_distance(self):
        return self.focal_distance * self.get_height()

    def interpolate(self, *args, **kwargs):
        super().interpolate(*args, **kwargs)
        self.refresh_rotation_matrix()


class Camera(object):
    CONFIG = {
        "background_image": None,
        "frame_config": {},
        "pixel_width": DEFAULT_PIXEL_WIDTH,
        "pixel_height": DEFAULT_PIXEL_HEIGHT,
        "frame_rate": DEFAULT_FRAME_RATE,
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
        self.refresh_perspective_uniforms()
        self.static_mobject_to_render_group_list = {}

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
        self.refresh_perspective_uniforms()

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
        pw, ph = self.fbo.size
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
        self.refresh_perspective_uniforms()
        for mobject in mobjects:
            for render_group in self.get_render_group_list(mobject):
                self.render(render_group)

    def render(self, render_group):
        shader_wrapper = render_group["shader_wrapper"]
        shader_program = render_group["prog"]
        self.set_shader_uniforms(shader_program, shader_wrapper)
        self.update_depth_test(shader_wrapper)
        render_group["vao"].render(int(shader_wrapper.render_primitive))
        if render_group["single_use"]:
            self.release_render_group(render_group)

    def update_depth_test(self, shader_wrapper):
        if shader_wrapper.depth_test:
            self.ctx.enable(moderngl.DEPTH_TEST)
        else:
            self.ctx.disable(moderngl.DEPTH_TEST)

    def get_render_group_list(self, mobject):
        try:
            return self.static_mobject_to_render_group_list[id(mobject)]
        except KeyError:
            return map(self.get_render_group, mobject.get_shader_wrapper_list())

    def get_render_group(self, shader_wrapper, single_use=True):
        # Data buffers
        vbo = self.ctx.buffer(shader_wrapper.vert_data.tobytes())
        if shader_wrapper.vert_indices is None:
            ibo = None
        else:
            vert_index_data = shader_wrapper.vert_indices.astype('i4').tobytes()
            if vert_index_data:
                ibo = self.ctx.buffer(vert_index_data)
            else:
                ibo = None

        # Program and vertex array
        shader_program, vert_format = self.get_shader_program(shader_wrapper)
        vao = self.ctx.vertex_array(
            program=shader_program,
            content=[(vbo, vert_format, *shader_wrapper.vert_attributes)],
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

    def release_render_group(self, render_group):
        for key in ["vbo", "ibo", "vao"]:
            if render_group[key] is not None:
                render_group[key].release()

    def set_mobjects_as_static(self, *mobjects):
        # Creates buffer and array objects holding each mobjects shader data
        for mob in mobjects:
            self.static_mobject_to_render_group_list[id(mob)] = [
                self.get_render_group(sw, single_use=False)
                for sw in mob.get_shader_wrapper_list()
            ]

    def release_static_mobjects(self):
        for rg_list in self.static_mobject_to_render_group_list.values():
            for render_group in rg_list:
                self.release_render_group(render_group)
        self.static_mobject_to_render_group_list = {}

    # Shaders
    def init_shaders(self):
        # Initialize with the null id going to None
        self.id_to_shader_program = {"": None}

    def get_shader_program(self, shader_wrapper):
        sid = shader_wrapper.get_program_id()
        if sid not in self.id_to_shader_program:
            # Create shader program for the first time, then cache
            # in the id_to_shader_program dictionary
            program = self.ctx.program(**shader_wrapper.get_program_code())
            vert_format = moderngl.detect_format(program, shader_wrapper.vert_attributes)
            self.id_to_shader_program[sid] = (program, vert_format)
        return self.id_to_shader_program[sid]

    def set_shader_uniforms(self, shader, shader_wrapper):
        for name, path in shader_wrapper.texture_paths.items():
            tid = self.get_texture_id(path)
            shader[name].value = tid
        for name, value in it.chain(shader_wrapper.uniforms.items(), self.perspective_uniforms.items()):
            try:
                shader[name].value = value
            except KeyError:
                pass

    def refresh_perspective_uniforms(self):
        frame = self.frame
        pw, ph = self.get_pixel_shape()
        fw, fh = frame.get_shape()
        # TODO, this should probably be a mobject uniform, with
        # the camera taking care of the conversion factor
        anti_alias_width = self.anti_alias_width / (ph / fh)
        # Orient light
        rotation = frame.get_inverse_camera_rotation_matrix()
        light_pos = self.light_source.get_location()
        light_pos = np.dot(rotation, light_pos)

        self.perspective_uniforms = {
            "frame_shape": frame.get_shape(),
            "anti_alias_width": anti_alias_width,
            "camera_center": tuple(frame.get_center()),
            "camera_rotation": tuple(np.array(rotation).T.flatten()),
            "light_source_position": tuple(light_pos),
            "focal_distance": frame.get_focal_distance(),
        }

    def init_textures(self):
        self.path_to_texture_id = {}

    def get_texture_id(self, path):
        if path not in self.path_to_texture_id:
            # A way to increase tid's sequentially
            tid = len(self.path_to_texture_id)
            im = Image.open(path).convert("RGBA")
            texture = self.ctx.texture(
                size=im.size,
                components=len(im.getbands()),
                data=im.tobytes(),
            )
            texture.use(location=tid)
            self.path_to_texture_id[path] = tid
        return self.path_to_texture_id[path]


# Mostly just defined so old scenes don't break
class ThreeDCamera(Camera):
    CONFIG = {
        "samples": 4,
    }
