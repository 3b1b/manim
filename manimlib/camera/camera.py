from functools import reduce
import operator as op
import moderngl
from colour import Color

from PIL import Image
import numpy as np
import itertools as it

from manimlib.constants import *
from manimlib.mobject.mobject import Mobject
from manimlib.utils.config_ops import digest_config
from manimlib.utils.iterables import batch_by_property
from manimlib.utils.simple_functions import fdiv
from manimlib.utils.shaders import shader_info_to_id
from manimlib.utils.shaders import shader_id_to_info
from manimlib.utils.shaders import get_shader_code_from_file


# TODO, think about how to incorporate perspective,
# and change get_height, etc. to take orientation into account
class CameraFrame(Mobject):
    CONFIG = {
        "width": FRAME_WIDTH,
        "height": FRAME_HEIGHT,
        "center": ORIGIN,
    }

    def init_points(self):
        self.points = np.array([UL, UR, DR, DL])
        self.set_width(self.width, stretch=True)
        self.set_height(self.height, stretch=True)
        self.move_to(self.center)
        self.save_state()


class Camera(object):
    CONFIG = {
        "background_image": None,
        "frame_config": {
            "width": FRAME_WIDTH,
            "height": FRAME_HEIGHT,
            "center": ORIGIN,
        },
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
        "line_width_multiple": 0.01,
    }

    def __init__(self, ctx=None, **kwargs):
        digest_config(self, kwargs, locals())
        self.rgb_max_val = np.iinfo(self.pixel_array_dtype).max
        self.init_frame()
        self.init_context(ctx)
        self.init_shaders()
        self.init_textures()

    def init_frame(self):
        self.frame = CameraFrame(**self.frame_config)

    def init_context(self, ctx=None):
        if ctx is not None:
            self.ctx = ctx
            self.fbo = self.ctx.detect_framebuffer()
        else:
            self.ctx = moderngl.create_standalone_context()
            self.fbo = self.get_fbo()
            self.fbo.use()

        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = (
            moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA,
            moderngl.ONE, moderngl.ONE
        )
        self.background_fbo = None

    # Methods associated with the frame buffer
    def get_fbo(self):
        return self.ctx.simple_framebuffer(
            (self.pixel_width, self.pixel_height)
        )

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
        self.set_frame_height(frame_height)
        self.set_frame_width(frame_width)

    def clear(self):
        rgba = (*Color(self.background_color).get_rgb(), self.background_opacity)
        self.fbo.clear(*rgba)

    def reset_pixel_shape(self, new_width, new_height):
        self.pixel_width = new_width
        self.pixel_height = new_height
        self.refresh_shader_uniforms()

    # Various ways to read from the fbo
    def get_raw_fbo_data(self, dtype='f1'):
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

    # TODO, make these work for a rotated frame
    def get_frame_height(self):
        return self.frame.get_height()

    def get_frame_width(self):
        return self.frame.get_width()

    def get_frame_shape(self):
        return (self.get_frame_width(), self.get_frame_height())

    def get_frame_center(self):
        return self.frame.get_center()

    def set_frame_height(self, height):
        self.frame.set_height(height, stretch=True)

    def set_frame_width(self, width):
        self.frame.set_width(width, stretch=True)

    def set_frame_center(self, center):
        self.frame.move_to(center)

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

    # TODO, account for 3d
    # Also, move this to CameraFrame?
    def is_in_frame(self, mobject):
        fc = self.get_frame_center()
        fh = self.get_frame_height()
        fw = self.get_frame_width()
        return not reduce(op.or_, [
            mobject.get_right()[0] < fc[0] - fw,
            mobject.get_bottom()[1] > fc[1] + fh,
            mobject.get_left()[0] > fc[0] + fw,
            mobject.get_top()[1] < fc[1] - fh,
        ])

    # Rendering
    def capture(self, *mobjects, **kwargs):
        for mobject in mobjects:
            mobject.render(camera=self)

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
            if info["texture_path"]:
                # TODO, this currently assumes that the uniform Sampler2D
                # is named Texture
                tid = self.get_texture_id(info["texture_path"])
                shader["Texture"].value = tid

            self.set_shader_uniforms(shader)
            self.id_to_shader[sid] = shader
        return self.id_to_shader[sid]

    def set_shader_uniforms(self, shader):
        if shader is None:
            return
        # TODO, think about how uniforms come from mobjects as well.
        fh = self.get_frame_height()
        fc = self.get_frame_center()
        pw, ph = self.get_pixel_shape()

        mapping = {
            'scale': fh / 2,  # Scale based on frame size
            'aspect_ratio': (pw / ph),  # AR based on pixel shape
            'anti_alias_width': ANTI_ALIAS_WIDTH_OVER_FRAME_HEIGHT * fh,
            'frame_center': tuple(fc),
        }
        for key, value in mapping.items():
            try:
                shader[key].value = value
            except KeyError:
                pass

    def refresh_shader_uniforms(self):
        for sid, shader in self.id_to_shader.items():
            self.set_shader_uniforms(shader)

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
