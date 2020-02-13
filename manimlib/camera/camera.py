from functools import reduce
import operator as op
import moderngl
import re
from colour import Color

from PIL import Image
import numpy as np
import itertools as it

from manimlib.constants import *
from manimlib.mobject.mobject import Mobject
from manimlib.utils.config_ops import digest_config
from manimlib.utils.iterables import batch_by_property
from manimlib.utils.simple_functions import fdiv


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
        pw, ph = self.get_pixel_shape()
        fw, fh = self.get_frame_shape()
        fc = self.get_frame_center()
        if relative:
            return 2 * np.array([px / pw, py / ph, 0])
        else:
            # Only scale wrt one axis
            scale = fh / ph
            return np.array([
                scale * (px - pw / 2) - fc[0],
                scale * (py - py / 2) - fc[0],
                -fc[2] / 2,
            ])

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
        shader_infos = list(it.chain(*[
            mob.get_shader_info_list()
            for mob in mobjects
        ]))
        # TODO, batching works well when the mobjects are already organized,
        # but can we somehow use z-buffering to better effect here?
        batches = batch_by_property(shader_infos, self.get_shader_id)
        for info_group, sid in batches:
            shader = self.get_shader(sid)
            data = np.hstack([info["data"] for info in info_group])
            render_primative = info_group[0]["render_primative"]
            self.render_from_shader(shader, data, render_primative)

    # Shaders
    def init_shaders(self):
        # Initialize with the null id going to None
        self.id_to_shader = {"": None}

    def get_shader_id(self, shader_info):
        # A unique id for a shader based on the names of the files holding its code
        vert, geom, frag, text = [
            shader_info.get(key, "") or ""
            for key in ["vert", "geom", "frag", "texture_path"]
        ]
        if not vert or not frag:
            # Not an actual shader
            return ""
        return "|".join([vert, geom, frag, text])

    def get_shader(self, sid):
        if sid not in self.id_to_shader:
            vert, geom, frag, text = sid.split("|")
            shader = self.ctx.program(
                vertex_shader=self.get_shader_code_from_file(vert),
                geometry_shader=self.get_shader_code_from_file(geom),
                fragment_shader=self.get_shader_code_from_file(frag),
            )
            if text:
                # TODO, this currently assumes that the uniform Sampler2D
                # is named Texture
                tid = self.get_texture_id(text)
                shader["Texture"].value = tid

            self.set_shader_uniforms(shader)
            self.id_to_shader[sid] = shader
        return self.id_to_shader[sid]

    def get_shader_code_from_file(self, filename):
        if len(filename) == 0:
            return None

        filepath = os.path.join(SHADER_DIR, filename)
        if not os.path.exists(filepath):
            warnings.warn(f"No file at {file_path}")
            return

        with open(filepath, "r") as f:
            result = f.read()

        # To share functionality between shaders, some functions are read in
        # from other files an inserted into the relevant strings before
        # passing to ctx.program for compiling
        # Replace "#INSERT " lines with relevant code
        insertions = re.findall(r"^#INSERT .*\.glsl$", result, flags=re.MULTILINE)
        for line in insertions:
            inserted_code = self.get_shader_code_from_file(line.replace("#INSERT ", ""))
            result = result.replace(line, inserted_code)
        return result

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
            'anti_alias_width': ANTI_ALIAS_WIDTH,
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

    def render_from_shader(self, shader, data, render_primative):
        if data is None or shader is None or len(data) == 0:
            return
        vbo = self.ctx.buffer(data.tobytes())
        vao = self.ctx.simple_vertex_array(shader, vbo, *data.dtype.names)
        vao.render(render_primative)

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
