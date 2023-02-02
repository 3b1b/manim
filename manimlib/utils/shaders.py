from __future__ import annotations

import os
import re
from functools import lru_cache
import moderngl
from PIL import Image
import numpy as np

from manimlib.config import parse_cli
from manimlib.config import get_configuration
from manimlib.utils.customization import get_customization
from manimlib.utils.directories import get_shader_dir
from manimlib.utils.file_ops import find_file

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence, Optional, Tuple
    from moderngl.vertex_array import VertexArray
    from moderngl.framebuffer import Framebuffer


ID_TO_TEXTURE: dict[int, moderngl.Texture] = dict()


@lru_cache()
def image_path_to_texture(path: str, ctx: moderngl.Context) -> moderngl.Texture:
    im = Image.open(path).convert("RGBA")
    return ctx.texture(
        size=im.size,
        components=len(im.getbands()),
        data=im.tobytes(),
    )


def get_texture_id(texture: moderngl.Texture) -> int:
    tid = 0
    while tid in ID_TO_TEXTURE:
        tid += 1
    ID_TO_TEXTURE[tid] = texture
    texture.use(location=tid)
    return tid


def release_texture(texture_id: int):
    texture = ID_TO_TEXTURE.pop(texture_id, None)
    if texture is not None:
        texture.release()


@lru_cache()
def get_shader_program(
        ctx: moderngl.context.Context,
        vertex_shader: str,
        fragment_shader: Optional[str] = None,
        geometry_shader: Optional[str] = None,
    ) -> moderngl.Program:
    return ctx.program(
        vertex_shader=vertex_shader,
        fragment_shader=fragment_shader,
        geometry_shader=geometry_shader,
    )


@lru_cache()
def get_shader_code_from_file(filename: str) -> str | None:
    if not filename:
        return None

    try:
        filepath = find_file(
            filename,
            directories=[get_shader_dir(), "/"],
            extensions=[],
        )
    except IOError:
        return None

    with open(filepath, "r") as f:
        result = f.read()

    # To share functionality between shaders, some functions are read in
    # from other files an inserted into the relevant strings before
    # passing to ctx.program for compiling
    # Replace "#INSERT " lines with relevant code
    insertions = re.findall(r"^#INSERT .*\.glsl$", result, flags=re.MULTILINE)
    for line in insertions:
        inserted_code = get_shader_code_from_file(
            os.path.join("inserts", line.replace("#INSERT ", ""))
        )
        result = result.replace(line, inserted_code)
    return result


def get_colormap_code(rgb_list: Sequence[float]) -> str:
    data = ",".join(
        "vec3({}, {}, {})".format(*rgb)
        for rgb in rgb_list
    )
    return f"vec3[{len(rgb_list)}]({data})"



@lru_cache()
def get_fill_canvas(ctx: moderngl.Context) -> Tuple[Framebuffer, VertexArray]:
    """
    Because VMobjects with fill are rendered in a funny way, using
    alpha blending to effectively compute the winding number around
    each pixel, they need to be rendered to a separate texture, which
    is then composited onto the ordinary frame buffer.

    This returns a texture, loaded into a frame buffer, and a vao
    which can display that texture as a simple quad onto a screen,
    along with the rgb value which is meant to be discarded.
    """
    cam_config = get_configuration(parse_cli())['camera_config']
    size = (cam_config['pixel_width'], cam_config['pixel_height'])

    # Important to make sure dtype is floating point (not fixed point)
    # so that alpha values can be negative and are not clipped
    texture = ctx.texture(size=size, components=4, dtype='f2')
    depth_texture = ctx.depth_texture(size=size)
    texture_fbo = ctx.framebuffer(texture, depth_texture)

    simple_program = ctx.program(
        vertex_shader='''
            #version 330

            in vec2 texcoord;
            out vec2 uv;

            void main() {
                gl_Position = vec4((2.0 * texcoord - 1.0), 0.0, 1.0);
                uv = texcoord;
            }
        ''',
        fragment_shader='''
            #version 330

            uniform sampler2D Texture;
            uniform sampler2D DepthTexture;

            in vec2 uv;
            out vec4 color;

            void main() {
                color = texture(Texture, uv);
                if(color.a == 0) discard;

                // Counteract scaling in fill frag
                color.a *= 1.06;

                gl_FragDepth = texture(DepthTexture, uv)[0];
            }
        ''',
    )

    simple_program['Texture'].value = get_texture_id(texture)
    simple_program['DepthTexture'].value = get_texture_id(depth_texture)

    verts = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    fill_texture_vao = ctx.simple_vertex_array(
        simple_program,
        ctx.buffer(verts.astype('f4').tobytes()),
        'texcoord',
        mode=moderngl.TRIANGLE_STRIP
    )
    return (texture_fbo, fill_texture_vao)
