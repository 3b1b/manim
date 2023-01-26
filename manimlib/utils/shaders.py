from __future__ import annotations

import os
import re
from functools import lru_cache
import moderngl
from PIL import Image

from manimlib.constants import DEFAULT_PIXEL_HEIGHT
from manimlib.constants import DEFAULT_PIXEL_WIDTH
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
def get_intermediary_palette(ctx) -> Tuple[Framebuffer, VertexArray]:
    """
    Creates a texture, loaded into a frame buffer, and a vao
    which can display that texture as a simple quad onto a screen.
    """
    size = (2 * DEFAULT_PIXEL_WIDTH, 2 * DEFAULT_PIXEL_HEIGHT)
    texture = ctx.texture(
        size=size,
        components=4,
        # Important to make sure floating point (not fixed point) is
        # used so that alpha values are not clipped
        dtype='f2',
    )
    depth_buffer = ctx.depth_renderbuffer(size)  # TODO, currently not used
    texture_fbo = ctx.framebuffer(texture, depth_buffer)

    simple_program = ctx.program(
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
            uniform sampler2D DepthTexture;
            uniform float v_nudge;
            uniform float h_nudge;

            in vec2 v_textcoord;
            out vec4 frag_color;

            void main() {
                // Apply poor man's anti-aliasing
                vec2 tc0 = v_textcoord + vec2(v_nudge, h_nudge);
                vec2 tc1 = v_textcoord + vec2(v_nudge, -h_nudge);
                vec2 tc2 = v_textcoord + vec2(-v_nudge, h_nudge);
                vec2 tc3 = v_textcoord + vec2(-v_nudge, -h_nudge);
                frag_color = 
                    0.25 * abs(texture(Texture, tc0)) +
                    0.25 * abs(texture(Texture, tc1)) +
                    0.25 * abs(texture(Texture, tc2)) +
                    0.25 * abs(texture(Texture, tc3));
                if(frag_color.a == 0) discard;
                //TODO, set gl_FragDepth;
            }
        ''',
    )

    simple_program['Texture'].value = get_texture_id(texture)
    # Quarter pixel width/height
    simple_program['h_nudge'].value = 0.25 / size[0]
    simple_program['v_nudge'].value = 0.25 / size[1]

    verts = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    fill_texture_vao = ctx.simple_vertex_array(
        simple_program,
        ctx.buffer(verts.astype('f4').tobytes()),
        'texcoord',
    )
    return (texture_fbo, fill_texture_vao)
