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
from manimlib.utils.iterables import list_difference_update
from manimlib.utils.iterables import join_structured_arrays
from manimlib.utils.family_ops import extract_mobject_family_members
from manimlib.utils.simple_functions import fdiv


# TODO, think about how to incorporate perspective,
# and change get_height, etc. to take orientation into account
class CameraFrame(Mobject):
    CONFIG = {
        "width": FRAME_WIDTH,
        "height": FRAME_HEIGHT,
        "center": ORIGIN,
    }

    def generate_points(self):
        self.points = np.array([UL, UR, DR, DL])
        self.set_width(self.width, stretch=True)
        self.set_height(self.height, stretch=True)
        self.move_to(self.center)


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
        "line_width_multiple": 0.01,
        "background_fbo": None,
    }

    def __init__(self, background=None, **kwargs):
        digest_config(self, kwargs, locals())
        self.rgb_max_val = np.iinfo(self.pixel_array_dtype).max
        self.init_frame()
        self.init_context()
        self.init_frame_buffer()
        self.init_shaders()

    def init_frame(self):
        self.frame = CameraFrame(**self.frame_config)

    def init_context(self):
        # TODO, context with a window?
        ctx = moderngl.create_standalone_context()
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = (
            moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA,
            moderngl.ONE, moderngl.ONE
        )
        self.ctx = ctx

    # Methods associated with the frame buffer
    def init_frame_buffer(self):
        # TODO, account for live window
        self.fbo = self.get_fbo()
        self.fbo.use()
        self.clear()

    def get_fbo(self):
        return self.ctx.simple_framebuffer(self.get_pixel_shape())

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
        if self.background_fbo:
            self.ctx.copy_framebuffer(self.fbo, self.background_fbo)
        else:
            rgba = (*Color(self.background_color).get_rgb(), self.background_opacity)
            self.fbo.clear(*rgba)

    def lock_state_as_background(self):
        self.background_fbo = self.get_fbo()
        self.ctx.copy_framebuffer(self.background_fbo, self.fbo)

    def unlock_background(self):
        self.background_fbo = None

    def reset_pixel_shape(self, new_height, new_width):
        self.pixel_width = new_width
        self.pixel_height = new_height
        self.fbo.release()
        self.init_frame_buffer()

    # Various ways to read from the fbo
    def get_raw_fbo_data(self, dtype='f1'):
        return self.fbo.read(components=self.n_channels, dtype=dtype)

    def get_image(self, pixel_array=None):
        return Image.frombytes(
            'RGBA', self.fbo.size,
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
        return (self.pixel_width, self.pixel_height)

    def get_pixel_width(self):
        return self.get_pixel_shape()[0]

    def get_pixel_height(self):
        return self.get_pixel_shape()[1]

    # TODO, make these work for a rotated frame
    def get_frame_height(self):
        return self.frame.get_height()

    def get_frame_width(self):
        return self.frame.get_width()

    def get_frame_center(self):
        return self.frame.get_center()

    def set_frame_height(self, height):
        self.frame.set_height(height, stretch=True)

    def set_frame_width(self, width):
        self.frame.set_width(width, stretch=True)

    def set_frame_center(self, center):
        self.frame.move_to(center)

    # TODO, account for 3d
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
    def get_mobjects_to_display(self, mobjects, excluded_mobjects=None):
        mobjects = extract_mobject_family_members(
            mobjects, only_those_with_points=True,
        )
        if excluded_mobjects:
            all_excluded = extract_mobject_family_members(excluded_mobjects)
            mobjects = list_difference_update(mobjects, all_excluded)
        return mobjects

    def capture_mobject(self, mobject, **kwargs):
        return self.capture_mobjects([mobject], **kwargs)

    def capture_mobjects(self, mobjects, **kwargs):
        mobjects = self.get_mobjects_to_display(mobjects, **kwargs)
        shader_infos = list(it.chain(*[
            mob.get_shader_info_list()
            for mob in mobjects
        ]))
        # TODO, batching works well when the mobjects are already organized,
        # but can we somehow use z-buffering to better effect here?
        batches = batch_by_property(shader_infos, self.get_shader_id)
        for info_group, sid in batches:
            data = join_structured_arrays(*[info["data"] for info in info_group])
            shader = self.get_shader(sid)
            self.render_from_shader(shader, data)

    # Shader stuff
    def init_shaders(self):
        self.id_to_shader = {}

    def get_shader_id(self, shader_info):
        # A unique id for a shader based on the names of the files holding its code
        return "|".join([
            shader_info.get(key, "")
            for key in ["vert", "geom", "frag"]
        ])

    def get_shader(self, sid):
        if sid not in self.id_to_shader:
            vert, geom, frag = sid.split("|")
            shader = self.ctx.program(
                vertex_shader=self.get_shader_code_from_file(vert),
                geometry_shader=self.get_shader_code_from_file(geom),
                fragment_shader=self.get_shader_code_from_file(frag),
            )
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
        # TODO, think about how uniforms come from mobjects
        # as well.
        fw = self.get_frame_width()
        fh = self.get_frame_height()

        shader['scale'].value = fh / 2
        shader['aspect_ratio'].value = fw / fh
        shader['anti_alias_width'].value = ANTI_ALIAS_WIDTH

    def render_from_shader(self, shader, data):
        vbo = shader.ctx.buffer(data.tobytes())
        vao = shader.ctx.simple_vertex_array(shader, vbo, *data.dtype.names)
        vao.render(moderngl.TRIANGLES)  # TODO, allow different render types


def get_vmob_shader(ctx, type):
    vert_file = f"quadratic_bezier_{type}_vert.glsl"
    geom_file = f"quadratic_bezier_{type}_geom.glsl"
    frag_file = f"quadratic_bezier_{type}_frag.glsl"

    shader = ctx.program(
        vertex_shader=get_code_from_file(vert_file),
        geometry_shader=get_code_from_file(geom_file),
        fragment_shader=get_code_from_file(frag_file),
    )
    set_shader_uniforms(shader)
    return shader


def get_stroke_shader(ctx):
    return get_vmob_shader(ctx, "stroke")


def get_fill_shader(ctx):
    return get_vmob_shader(ctx, "fill")


def render_vmob_stroke(shader, vmobs):
    assert(len(vmobs) > 0)
    data_arrays = [vmob.get_stroke_shader_data() for vmob in vmobs]
    data = join_arrays(*data_arrays)
    send_data_to_shader(shader, data)


def render_vmob_fill(shader, vmobs):
    assert(len(vmobs) > 0)
    data_arrays = [vmob.get_fill_shader_data() for vmob in vmobs]
    data = join_arrays(*data_arrays)
    send_data_to_shader(shader, data)
