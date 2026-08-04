"""
A throwaway spike, to settle what wgpu-py will and will not let the renderer do before any
of it is ported. Nothing here is meant to be kept: what it produces is answers, a few
images to look at, and corrections to WGPU_PORT_PLAN.md.

    python wgpu_spike.py            # every check
    python wgpu_spike.py stencil    # just the ones whose name contains this

Each check prints one line saying whether what the plan assumes turned out to be true, and
some write a png into wgpu_spike_out/ to be looked at rather than asserted.
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

import numpy as np
import wgpu

OUT = Path(__file__).parent / "wgpu_spike_out"

# The size manim calls low quality, whose rows are 854 * 4 = 3416 bytes, deliberately not a
# multiple of the 256 a texture copy wants
WIDTH, HEIGHT = 854, 480

CHECKS = []


def check(func):
    CHECKS.append(func)
    return func


def get_device() -> wgpu.GPUDevice:
    adapter = wgpu.gpu.request_adapter_sync(power_preference="high-performance")
    return adapter.request_device_sync()


def save(name: str, pixels: np.ndarray) -> str:
    from PIL import Image
    OUT.mkdir(exist_ok=True)
    Image.fromarray(pixels[:, :, :3]).save(OUT / f"{name}.png")
    return f"wgpu_spike_out/{name}.png"


def render_offscreen(
    device: wgpu.GPUDevice,
    draw,
    size=(WIDTH, HEIGHT),
    samples: int = 1,
    depth_stencil: bool = False,
    clear=(0.0, 0.0, 0.0, 1.0),
) -> np.ndarray:
    """
    One frame into a texture of our own, read back as an array. Everything the renderer
    does to write a file, in the shape decision 6 of the plan describes: one color target,
    optionally multisampled with a place to resolve into, and one depth-stencil texture.
    """
    width, height = size
    resolved = device.create_texture(
        size=(width, height, 1),
        format=wgpu.TextureFormat.rgba8unorm,
        usage=wgpu.TextureUsage.RENDER_ATTACHMENT | wgpu.TextureUsage.COPY_SRC,
    )
    attachment = {
        "view": resolved.create_view(),
        "resolve_target": None,
        "clear_value": clear,
        "load_op": wgpu.LoadOp.clear,
        "store_op": wgpu.StoreOp.store,
    }
    if samples > 1:
        multisampled = device.create_texture(
            size=(width, height, 1),
            format=wgpu.TextureFormat.rgba8unorm,
            usage=wgpu.TextureUsage.RENDER_ATTACHMENT,
            sample_count=samples,
        )
        attachment["view"] = multisampled.create_view()
        attachment["resolve_target"] = resolved.create_view()

    pass_args = {"color_attachments": [attachment]}
    if depth_stencil:
        texture = device.create_texture(
            size=(width, height, 1),
            format=wgpu.TextureFormat.depth24plus_stencil8,
            usage=wgpu.TextureUsage.RENDER_ATTACHMENT,
            sample_count=samples,
        )
        pass_args["depth_stencil_attachment"] = {
            "view": texture.create_view(),
            "depth_clear_value": 1.0,
            "depth_load_op": wgpu.LoadOp.clear,
            "depth_store_op": wgpu.StoreOp.store,
            "stencil_clear_value": 0,
            "stencil_load_op": wgpu.LoadOp.clear,
            "stencil_store_op": wgpu.StoreOp.store,
        }

    encoder = device.create_command_encoder()
    render_pass = encoder.begin_render_pass(**pass_args)
    draw(render_pass)
    render_pass.end()
    device.queue.submit([encoder.finish()])

    data = device.queue.read_texture(
        {"texture": resolved, "mip_level": 0, "origin": (0, 0, 0)},
        {"offset": 0, "bytes_per_row": width * 4, "rows_per_image": height},
        (width, height, 1),
    )
    return np.frombuffer(data, np.uint8).reshape((height, width, 4))


# The vertex pulling every shader in manim does after #2482, said the wgpu way: no vertex
# attributes at all, the shader reading its own records out of a buffer by vertex index.
PULLING_WGSL = """
@group(0) @binding(0) var<storage, read> data: array<f32>;

const DATA_STRIDE: u32 = 7u;
const DATA_OFFSET_point: u32 = 0u;
const DATA_OFFSET_rgba: u32 = 3u;

fn read_vec3(record: u32, offset: u32) -> vec3f {
    let base = record * DATA_STRIDE + offset;
    return vec3f(data[base], data[base + 1u], data[base + 2u]);
}

fn read_vec4(record: u32, offset: u32) -> vec4f {
    let base = record * DATA_STRIDE + offset;
    return vec4f(data[base], data[base + 1u], data[base + 2u], data[base + 3u]);
}

struct VertexOutput {
    @builtin(position) position: vec4f,
    @location(0) color: vec4f,
}

@vertex
fn vs_main(@builtin(vertex_index) index: u32) -> VertexOutput {
    var out: VertexOutput;
    out.position = vec4f(read_vec3(index, DATA_OFFSET_point), 1.0);
    out.color = read_vec4(index, DATA_OFFSET_rgba);
    return out;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4f {
    return in.color;
}
"""


def pulling_pipeline(device, records: np.ndarray, blend=None, **pipeline_args):
    """A pipeline drawing straight out of a storage buffer, with a bind group for it"""
    module = device.create_shader_module(code=PULLING_WGSL)
    layout = device.create_bind_group_layout(entries=[{
        "binding": 0,
        "visibility": wgpu.ShaderStage.VERTEX,
        "buffer": {"type": wgpu.BufferBindingType.read_only_storage},
    }])
    buffer = device.create_buffer_with_data(
        data=records, usage=wgpu.BufferUsage.STORAGE | wgpu.BufferUsage.COPY_DST,
    )
    bind_group = device.create_bind_group(layout=layout, entries=[
        {"binding": 0, "resource": {"buffer": buffer, "offset": 0, "size": buffer.size}},
    ])
    pipeline = device.create_render_pipeline(
        layout=device.create_pipeline_layout(bind_group_layouts=[layout]),
        vertex={"module": module, "entry_point": "vs_main", "buffers": []},
        fragment={
            "module": module,
            "entry_point": "fs_main",
            "targets": [{"format": wgpu.TextureFormat.rgba8unorm, "blend": blend}],
        },
        **pipeline_args,
    )
    return pipeline, bind_group, buffer


def triangle_records(color=(1.0, 0.5, 0.0, 1.0)) -> np.ndarray:
    """Three records of seven floats: a point and a color, as a mobject's data would be"""
    dtype = np.dtype([("point", np.float32, (3,)), ("rgba", np.float32, (4,))])
    records = np.zeros(3, dtype=dtype)
    records["point"] = [[-0.8, -0.6, 0.0], [0.8, -0.6, 0.0], [0.0, 0.8, 0.0]]
    records["rgba"] = color
    return records


@check
def environment() -> str:
    """Which backend it picks, which is the whole point of the exercise"""
    adapter = wgpu.gpu.request_adapter_sync(power_preference="high-performance")
    info = adapter.info
    assert info["backend_type"] == "Metal", f"backend is {info['backend_type']}, not Metal"
    return (f"wgpu-py {wgpu.__version__}, {info['device']}, "
            f"{info['backend_type']} backend, {info['adapter_type']}")


@check
def vertex_pulling() -> str:
    """
    A read-only storage buffer read from the vertex stage by index, no attributes. The
    plan says this replaces aliasing the buffer as a texture; if it is not allowed in the
    vertex stage, that whole approach needs rethinking.
    """
    device = get_device()
    records = triangle_records()
    pipeline, bind_group, _ = pulling_pipeline(
        device, records, primitive={"topology": wgpu.PrimitiveTopology.triangle_list},
    )

    def draw(render_pass):
        render_pass.set_pipeline(pipeline)
        render_pass.set_bind_group(0, bind_group)
        render_pass.draw(3)

    pixels = render_offscreen(device, draw)
    middle = pixels[HEIGHT // 2, WIDTH // 2]
    assert tuple(middle[:3]) == (255, 128, 0), f"middle pixel is {middle}, not the fill"
    corner = pixels[2, 2]
    assert tuple(corner[:3]) == (0, 0, 0), f"corner pixel is {corner}, not the clear"
    return f"a storage buffer read by vertex_index draws, {save('vertex_pulling', pixels)}"


@check
def readback_row_padding() -> str:
    """
    Reading a frame back at a width whose rows are not a multiple of 256 bytes, which is
    what the file writer needs and what the plan expects to have to pad around by hand.
    """
    device = get_device()
    assert (WIDTH * 4) % 256 != 0, "pick a width whose rows are awkward"
    records = triangle_records(color=(0.0, 1.0, 0.0, 1.0))
    pipeline, bind_group, _ = pulling_pipeline(
        device, records, primitive={"topology": wgpu.PrimitiveTopology.triangle_list},
    )

    def draw(render_pass):
        render_pass.set_pipeline(pipeline)
        render_pass.set_bind_group(0, bind_group)
        render_pass.draw(3)

    pixels = render_offscreen(device, draw)
    assert pixels.shape == (HEIGHT, WIDTH, 4), f"came back as {pixels.shape}"
    assert tuple(pixels[HEIGHT // 2, WIDTH // 2][:3]) == (0, 255, 0), "wrong pixel"
    return (f"queue.read_texture handles a {WIDTH * 4} byte row itself, "
            f"no padding by hand")


# GLSL names a block member one thing and WGSL another, which is all the layout codegen
# has to change: the offsets either language computes come out the same.
WGSL_MEMBER_TYPES = {
    "float": "f32", "vec2": "vec2f", "vec3": "vec3f", "vec4": "vec4f", "mat4": "mat4x4f",
}


@check
def uniform_block_from_dtype() -> str:
    """
    A mobject's uniforms, laid out by the std140 rules manim already reproduces, read as a
    WGSL struct. If WGSL's uniform layout differs anywhere, a member near the end reads
    the wrong bytes, so the check is on the last member of the largest block there is.
    """
    from manimlib.mobject.types.vectorized_mobject import VMobject
    from manimlib.utils.shaders import uniform_block_code

    dtype = VMobject.uniform_dtype
    members = "\n".join(
        f"    {name}: {WGSL_MEMBER_TYPES[glsl_type]},"
        for glsl_type, name in (
            line.strip().rstrip(";").split() for line in uniform_block_code(dtype).splitlines()
        )
    )
    code = """
struct MobjectUniforms {
%s
}
@group(0) @binding(0) var<uniform> mob: MobjectUniforms;

@vertex
fn vs_main(@builtin(vertex_index) index: u32) -> @builtin(position) vec4f {
    let corners = array(vec2f(-1.0, -1.0), vec2f(3.0, -1.0), vec2f(-1.0, 3.0));
    return vec4f(corners[index], 0.0, 1.0);
}

@fragment
fn fs_main() -> @location(0) vec4f {
    // Members from the end of the block, whose offsets depend on every pad before them
    return vec4f(mob.fill_border_width, mob.gradient_start.x, mob.gradient_end.z, 1.0);
}
""" % members

    device = get_device()
    uniforms = np.zeros(1, dtype=dtype)
    uniforms["fill_border_width"] = 1.0
    uniforms["gradient_start"] = [0.5, 0.0, 0.0]
    uniforms["gradient_end"] = [0.0, 0.0, 0.25]
    module = device.create_shader_module(code=code)
    layout = device.create_bind_group_layout(entries=[{
        "binding": 0,
        "visibility": wgpu.ShaderStage.FRAGMENT,
        "buffer": {"type": wgpu.BufferBindingType.uniform},
    }])
    buffer = device.create_buffer_with_data(
        data=uniforms, usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST,
    )
    bind_group = device.create_bind_group(layout=layout, entries=[
        {"binding": 0, "resource": {"buffer": buffer, "offset": 0, "size": buffer.size}},
    ])
    pipeline = device.create_render_pipeline(
        layout=device.create_pipeline_layout(bind_group_layouts=[layout]),
        vertex={"module": module, "entry_point": "vs_main", "buffers": []},
        fragment={"module": module, "entry_point": "fs_main",
                  "targets": [{"format": wgpu.TextureFormat.rgba8unorm}]},
        primitive={"topology": wgpu.PrimitiveTopology.triangle_list},
    )

    def draw(render_pass):
        render_pass.set_pipeline(pipeline)
        render_pass.set_bind_group(0, bind_group)
        render_pass.draw(3)

    pixels = render_offscreen(device, draw, size=(64, 64))
    got = tuple(pixels[32, 32][:3])
    assert got == (255, 128, 64), f"read {got} from the block, wanted (255, 128, 64)"
    return (f"the std140 dtype manim already builds reads as a WGSL struct, "
            f"{dtype.itemsize} bytes, last member correct")


# Stencil then cover, said as three pipelines rather than as state poked between draws. The
# shape is a five pointed star drawn as a fan of triangles from its middle, whose outline
# crosses itself, so the middle is wound twice and only a winding count fills it correctly.
STAR_WGSL = """
@group(0) @binding(0) var<storage, read> data: array<f32>;

@vertex
fn vs_main(@builtin(vertex_index) index: u32) -> @builtin(position) vec4f {
    let base = index * 2u;
    return vec4f(data[base], data[base + 1u], 0.0, 1.0);
}

@fragment
fn fs_main() -> @location(0) vec4f {
    return vec4f(0.3, 0.7, 1.0, 1.0);
}
"""


def star_fan() -> np.ndarray:
    """A fan of triangles from the middle to each edge of a self crossing star outline"""
    turns = 2  # every second point, so the outline crosses itself
    angles = np.pi / 2 + np.arange(6) * turns * 2 * np.pi / 5
    outline = 0.8 * np.stack([np.cos(angles), np.sin(angles)], axis=1)
    outline[:, 0] *= HEIGHT / WIDTH
    points = []
    for start, end in zip(outline, outline[1:]):
        points += [[0.0, 0.0], list(start), list(end)]
    return np.array(points, dtype=np.float32)


def stencil_pipelines(device, module, pipeline_layout, samples=1):
    """
    Two of the three the plan's state table names for a fill: count the winding, then cover
    where it is nonzero while zeroing it. The border pass in between is a stroke, which is
    a shader of its own and not what this is checking.
    """
    common = dict(
        layout=pipeline_layout,
        vertex={"module": module, "entry_point": "vs_main", "buffers": []},
        primitive={"topology": wgpu.PrimitiveTopology.triangle_list},
        multisample={"count": samples},
    )
    fragment = {"module": module, "entry_point": "fs_main",
                "targets": [{"format": wgpu.TextureFormat.rgba8unorm}]}
    keep = {"compare": wgpu.CompareFunction.always, "fail_op": wgpu.StencilOperation.keep,
            "depth_fail_op": wgpu.StencilOperation.keep,
            "pass_op": wgpu.StencilOperation.keep}

    counting = device.create_render_pipeline(
        **common,
        # No color at all, which is a write mask of zero rather than a missing fragment
        # stage: wgpu wants a fragment stage to have a target
        fragment={"module": module, "entry_point": "fs_main", "targets": [
            {"format": wgpu.TextureFormat.rgba8unorm, "write_mask": 0},
        ]},
        depth_stencil={
            "format": wgpu.TextureFormat.depth24plus_stencil8,
            "depth_write_enabled": False,
            "depth_compare": wgpu.CompareFunction.always,
            "stencil_front": {**keep, "pass_op": wgpu.StencilOperation.increment_wrap},
            "stencil_back": {**keep, "pass_op": wgpu.StencilOperation.decrement_wrap},
            "stencil_read_mask": 0xFF,
            "stencil_write_mask": 0xFF,
        },
    )
    covering = device.create_render_pipeline(
        **common,
        fragment=fragment,
        depth_stencil={
            "format": wgpu.TextureFormat.depth24plus_stencil8,
            "depth_write_enabled": False,
            "depth_compare": wgpu.CompareFunction.always,
            "stencil_front": {
                "compare": wgpu.CompareFunction.not_equal,
                "fail_op": wgpu.StencilOperation.keep,
                "depth_fail_op": wgpu.StencilOperation.zero,
                "pass_op": wgpu.StencilOperation.zero,
            },
            "stencil_back": {
                "compare": wgpu.CompareFunction.not_equal,
                "fail_op": wgpu.StencilOperation.keep,
                "depth_fail_op": wgpu.StencilOperation.zero,
                "pass_op": wgpu.StencilOperation.zero,
            },
            "stencil_read_mask": 0xFF,
            "stencil_write_mask": 0xFF,
        },
    )
    return counting, covering


def draw_star(device, samples=1):
    module = device.create_shader_module(code=STAR_WGSL)
    points = star_fan()
    layout = device.create_bind_group_layout(entries=[{
        "binding": 0,
        "visibility": wgpu.ShaderStage.VERTEX,
        "buffer": {"type": wgpu.BufferBindingType.read_only_storage},
    }])
    buffer = device.create_buffer_with_data(
        data=points, usage=wgpu.BufferUsage.STORAGE | wgpu.BufferUsage.COPY_DST,
    )
    bind_group = device.create_bind_group(layout=layout, entries=[
        {"binding": 0, "resource": {"buffer": buffer, "offset": 0, "size": buffer.size}},
    ])
    counting, covering = stencil_pipelines(
        device, module, device.create_pipeline_layout(bind_group_layouts=[layout]), samples,
    )

    def draw(render_pass):
        # Both passes inside the one render pass, which is what a tile based gpu needs
        render_pass.set_bind_group(0, bind_group)
        for pipeline in (counting, covering):
            render_pass.set_pipeline(pipeline)
            render_pass.draw(len(points))

    return render_offscreen(device, draw, samples=samples, depth_stencil=True)


FILL = np.array([77, 178, 255])


def is_fill(pixel) -> bool:
    """Within a step of the fill color, since a gpu is free to round as it likes"""
    return bool(np.abs(np.array(pixel[:3], int) - FILL).max() <= 2)


@check
def stencil_then_cover() -> str:
    """
    The fill algorithm everything in manim rests on: increment-wrap and decrement-wrap by
    facing, then a cover pass keyed on a nonzero winding which zeroes as it goes.
    """
    device = get_device()
    pixels = draw_star(device)
    middle = pixels[HEIGHT // 2, WIDTH // 2]
    assert is_fill(middle), f"the middle of the star is {middle}, not filled"
    corner = tuple(pixels[4, 4][:3])
    assert corner == (0, 0, 0), f"outside the star is {corner}, not clear"
    filled = np.abs(pixels[:, :, :3].astype(int) - FILL).max(axis=2) <= 2
    fraction = filled.mean()
    assert 0.05 < fraction < 0.35, f"{fraction:.0%} of the frame is filled, not a star"
    # The middle of a five pointed star is wound twice, so a fill counting windings has it
    # solid where one obeying an even-odd rule would leave it hollow
    return (f"winding counted and covered in one pass, the doubly wound middle filled, "
            f"{save('stencil_star', pixels)}")


@check
def stencil_with_msaa() -> str:
    """
    The same with four samples, which ThreeDCamera asks for and which the plan flags as an
    untested combination.
    """
    device = get_device()
    pixels = draw_star(device, samples=4)
    middle = pixels[HEIGHT // 2, WIDTH // 2]
    assert is_fill(middle), f"the middle of the star is {middle}, not filled"
    # An edge pixel should be part way between the fill and the clear, which is the whole
    # point of asking for samples
    column = pixels[:, WIDTH // 2, 2]
    partial = ((column > 8) & (column < 247)).sum()
    assert partial >= 1, "no partly covered pixels, so nothing was resolved"
    return (f"four samples with stencil, {partial} partly covered pixels down the middle, "
            f"{save('stencil_star_msaa', pixels)}")


@check
def error_reporting() -> str:
    """
    What a mistake looks like from Python, since moderngl's friendly messages are what the
    port gives up. Two kinds: source which will not compile, and a pipeline whose bind
    group does not match what the shader declares.
    """
    device = get_device()
    compile_error = ""
    try:
        device.create_shader_module(code="@vertex fn vs() -> @builtin(position) vec4f { }")
    except Exception as e:
        compile_error = f"{type(e).__name__}"
    assert compile_error, "a shader which cannot compile raised nothing"

    validation_error = ""
    try:
        module = device.create_shader_module(code=STAR_WGSL)
        device.create_render_pipeline(
            layout=device.create_pipeline_layout(bind_group_layouts=[]),
            vertex={"module": module, "entry_point": "vs_main", "buffers": []},
            fragment={"module": module, "entry_point": "fs_main",
                      "targets": [{"format": wgpu.TextureFormat.rgba8unorm}]},
            primitive={"topology": wgpu.PrimitiveTopology.triangle_list},
        )
    except Exception as e:
        validation_error = f"{type(e).__name__}"
    assert validation_error, "a pipeline missing the buffer its shader reads raised nothing"
    return f"bad source raises {compile_error}, bad pipeline raises {validation_error}"


# What emit_gl_Position does today, and what it has to do instead. GL clips z to
# [-w, w] and WebGPU to [0, w], so where GL wrote
#
#     result.w = 1.0 - z;  result.z = -0.1 * z;
#
# the same ordering in [0, w] is the midpoint of that and w:
#
#     result.z = 0.5 * (w - 0.1 * z) = 0.5 * (1.0 - 1.1 * z)
#
# which is the usual conversion, clip.z -> (clip.z + clip.w) / 2.
DEPTH_WGSL = """
@group(0) @binding(0) var<storage, read> data: array<f32>;

const REMAPPED: bool = %s;

struct VertexOutput {
    @builtin(position) position: vec4f,
    @location(0) color: vec4f,
}

@vertex
fn vs_main(@builtin(vertex_index) index: u32) -> VertexOutput {
    let base = index * 7u;
    let point = vec3f(data[base], data[base + 1u], data[base + 2u]);
    var out: VertexOutput;
    out.position = vec4f(point.xy, 0.0, 1.0 - point.z);
    if (REMAPPED) {
        out.position.z = 0.5 * (1.0 - 1.1 * point.z);
    } else {
        // What GL asked for, which puts anything nearer than the origin behind wgpu's
        // near plane and has it clipped away
        out.position.z = -0.1 * point.z;
    }
    out.color = vec4f(data[base + 3u], data[base + 4u], data[base + 5u], data[base + 6u]);
    return out;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4f {
    return in.color;
}
"""


# Where each square is meant to land on screen, and how deep it sits. Said as the place it
# should end up rather than the place it starts, since everything is divided by 1 - z on the
# way: the same square put at three depths would come out three sizes.
QUADS = [
    (0.5, (0.2, 0.4, 1.0, 1.0), (0.25, 0.25)),      # nearest, blue
    (0.0, (0.2, 1.0, 0.2, 1.0), (0.0, 0.0)),        # middle, green
    (-1.0, (1.0, 0.2, 0.2, 1.0), (-0.25, -0.25)),   # furthest, red
]
QUAD_RADIUS = 0.3


def overlapping_quads() -> np.ndarray:
    """
    Three squares of one size on screen, at three depths, each overlapping the next.
    Deliberately listed nearest first, so that painting them in the order given would put
    the furthest on top: only the depth test can produce the picture wanted.
    """
    dtype = np.dtype([("point", np.float32, (3,)), ("rgba", np.float32, (4,))])
    records = np.zeros(6 * len(QUADS), dtype=dtype)
    aspect = np.array([HEIGHT / WIDTH, 1.0])
    for index, (z, color, center) in enumerate(QUADS):
        corners = QUAD_RADIUS * np.array([
            [-1.0, -1.0], [1.0, -1.0], [-1.0, 1.0],
            [1.0, -1.0], [1.0, 1.0], [-1.0, 1.0],
        ])
        # Undo the perspective divide the vertex shader will apply, so that the square
        # lands where it was asked to
        wanted = (corners + center) * aspect * (1.0 - z)
        records["point"][6 * index:6 * index + 6, :2] = wanted
        records["point"][6 * index:6 * index + 6, 2] = z
        records["rgba"][6 * index:6 * index + 6] = color
    return records


def draw_depth(device, remapped: bool) -> np.ndarray:
    module = device.create_shader_module(code=DEPTH_WGSL % ("true" if remapped else "false"))
    records = overlapping_quads()
    layout = device.create_bind_group_layout(entries=[{
        "binding": 0,
        "visibility": wgpu.ShaderStage.VERTEX,
        "buffer": {"type": wgpu.BufferBindingType.read_only_storage},
    }])
    buffer = device.create_buffer_with_data(
        data=records, usage=wgpu.BufferUsage.STORAGE | wgpu.BufferUsage.COPY_DST,
    )
    bind_group = device.create_bind_group(layout=layout, entries=[
        {"binding": 0, "resource": {"buffer": buffer, "offset": 0, "size": buffer.size}},
    ])
    pipeline = device.create_render_pipeline(
        layout=device.create_pipeline_layout(bind_group_layouts=[layout]),
        vertex={"module": module, "entry_point": "vs_main", "buffers": []},
        fragment={"module": module, "entry_point": "fs_main",
                  "targets": [{"format": wgpu.TextureFormat.rgba8unorm}]},
        primitive={"topology": wgpu.PrimitiveTopology.triangle_list},
        depth_stencil={
            "format": wgpu.TextureFormat.depth24plus_stencil8,
            "depth_write_enabled": True,
            "depth_compare": wgpu.CompareFunction.less,
        },
    )

    def draw(render_pass):
        render_pass.set_pipeline(pipeline)
        render_pass.set_bind_group(0, bind_group)
        render_pass.draw(len(records))

    return render_offscreen(device, draw, depth_stencil=True)


@check
def depth_remap() -> str:
    """
    Whether the rederived mapping of clip space z puts overlapping things in the right
    order, and whether the mapping GL asked for really does fail, which is what makes this
    the one change in the port that could look nearly right and be wrong.
    """
    device = get_device()
    remapped = draw_depth(device, True)
    save("depth_remapped", remapped)

    def color_at(pixels, ndc):
        x, y = ndc
        aspect = HEIGHT / WIDTH
        column = int(WIDTH * (x * aspect + 1.0) / 2.0)
        row = int(HEIGHT * (1.0 - y) / 2.0)
        return tuple(pixels[row, column][:3])

    def brightest(color):
        return int(np.argmax(color))

    # All three on screen, each where it was asked to be
    assert brightest(color_at(remapped, (-0.45, -0.45))) == 0, "the furthest square is gone"
    assert brightest(color_at(remapped, (0.0, -0.2))) == 1, "the middle square is gone"
    assert brightest(color_at(remapped, (0.45, 0.45))) == 2, "the nearest square is gone"
    # And where two of them overlap, the nearer one wins, whichever was drawn first
    middle_over_far = color_at(remapped, (-0.15, -0.15))
    near_over_middle = color_at(remapped, (0.15, 0.15))
    assert brightest(middle_over_far) == 1, \
        f"the furthest square drew over the middle one, {middle_over_far}"
    assert brightest(near_over_middle) == 2, \
        f"the middle square drew over the nearest one, {near_over_middle}"

    # And the mapping GL wanted loses everything in front of the origin
    raw = draw_depth(device, False)
    save("depth_gl_mapping", raw)
    blue = (np.abs(raw[:, :, :3].astype(int) - [51, 102, 255]).max(axis=2) <= 3).sum()
    assert blue == 0, f"{blue} pixels of the nearest square survived GL's mapping"
    return ("clip.z of (w - 0.1z)/2 orders three overlapping depths correctly, where GL's "
            "-0.1z loses everything nearer than the origin")


@check
def window_without_their_loop() -> str:
    """
    The question the plan calls item one: can a window hand wgpu a surface while manim keeps
    hold of the loop? rendercanvas is built around registering a draw callback and calling
    loop.run(), which manim cannot do, since its own loop is what self.wait and self.embed
    are. But force_draw is public, and glfw is a library rather than a framework, so its
    events can be pumped from here without touching anything private.
    """
    import glfw
    from rendercanvas.glfw import RenderCanvas

    device = get_device()
    canvas = RenderCanvas(size=(480, 270), title="wgpu spike, closing itself shortly")
    context = canvas.get_context("wgpu")
    format = context.get_preferred_format(device.adapter)
    context.configure(device=device, format=format)

    records = triangle_records(color=(0.2, 0.6, 1.0, 1.0))
    module = device.create_shader_module(code=PULLING_WGSL)
    layout = device.create_bind_group_layout(entries=[{
        "binding": 0,
        "visibility": wgpu.ShaderStage.VERTEX,
        "buffer": {"type": wgpu.BufferBindingType.read_only_storage},
    }])
    buffer = device.create_buffer_with_data(
        data=records, usage=wgpu.BufferUsage.STORAGE | wgpu.BufferUsage.COPY_DST,
    )
    bind_group = device.create_bind_group(layout=layout, entries=[
        {"binding": 0, "resource": {"buffer": buffer, "offset": 0, "size": buffer.size}},
    ])
    pipeline = device.create_render_pipeline(
        layout=device.create_pipeline_layout(bind_group_layouts=[layout]),
        vertex={"module": module, "entry_point": "vs_main", "buffers": []},
        fragment={"module": module, "entry_point": "fs_main", "targets": [{"format": format}]},
        primitive={"topology": wgpu.PrimitiveTopology.triangle_list},
    )

    drawn = []
    resizes = []
    canvas.add_event_handler(lambda event: resizes.append(event), "resize")

    def draw_frame():
        target = context.get_current_texture()
        encoder = device.create_command_encoder()
        render_pass = encoder.begin_render_pass(color_attachments=[{
            "view": target.create_view(),
            "resolve_target": None,
            "clear_value": (0.05, 0.05, 0.08, 1.0),
            "load_op": wgpu.LoadOp.clear,
            "store_op": wgpu.StoreOp.store,
        }])
        render_pass.set_pipeline(pipeline)
        render_pass.set_bind_group(0, bind_group)
        render_pass.draw(3)
        render_pass.end()
        device.queue.submit([encoder.finish()])
        drawn.append(canvas.get_physical_size())

    canvas.request_draw(draw_frame)

    # manim's loop, in miniature: pump whatever the window has to say, then draw, at
    # whatever rate the caller feels like, with nobody else in charge
    for step in range(8):
        glfw.poll_events()
        canvas.force_draw()
        if step == 3:
            canvas.set_logical_size(600, 400)

    size = canvas.get_physical_size()
    ratio = canvas.get_pixel_ratio()
    closed_before = canvas.get_closed()
    canvas.close()
    glfw.poll_events()

    assert len(drawn) == 8, f"{len(drawn)} frames drawn out of 8 asked for"
    assert not closed_before, "the window closed on its own"
    assert len(set(drawn)) > 1, "resizing it did not change what was drawn into"
    assert resizes, "no resize event arrived while manim was the one polling"
    return (f"rendercanvas's glfw canvas driven by hand: 8 frames, {len(resizes)} resize "
            f"events, {size[0]}x{size[1]} physical at a pixel ratio of {ratio}")


# Half of a shape thrown away per fragment, which is how clipping works since phase 0c.
# Whether that also keeps the stencil buffer from being written is what decides whether a
# clipped fill counts its windings only where it is kept.
DISCARDING_WGSL = STAR_WGSL.replace(
    """@fragment
fn fs_main() -> @location(0) vec4f {
    return vec4f(0.3, 0.7, 1.0, 1.0);
}""",
    """@fragment
fn fs_main(@builtin(position) position: vec4f) -> @location(0) vec4f {
    if (position.x < %d.0) { discard; }
    return vec4f(0.3, 0.7, 1.0, 1.0);
}""" % (WIDTH // 2),
)


@check
def discard_suppresses_stencil() -> str:
    """
    A fragment thrown away must write no stencil, or a clipped fill would count windings
    where nothing was drawn and then cover the lot.
    """
    device = get_device()
    module = device.create_shader_module(code=DISCARDING_WGSL)
    points = star_fan()
    layout = device.create_bind_group_layout(entries=[{
        "binding": 0,
        "visibility": wgpu.ShaderStage.VERTEX,
        "buffer": {"type": wgpu.BufferBindingType.read_only_storage},
    }])
    buffer = device.create_buffer_with_data(
        data=points, usage=wgpu.BufferUsage.STORAGE | wgpu.BufferUsage.COPY_DST,
    )
    bind_group = device.create_bind_group(layout=layout, entries=[
        {"binding": 0, "resource": {"buffer": buffer, "offset": 0, "size": buffer.size}},
    ])
    counting, covering = stencil_pipelines(
        device, module, device.create_pipeline_layout(bind_group_layouts=[layout]),
    )

    def draw(render_pass):
        render_pass.set_bind_group(0, bind_group)
        for pipeline in (counting, covering):
            render_pass.set_pipeline(pipeline)
            render_pass.draw(len(points))

    pixels = render_offscreen(device, draw, depth_stencil=True)
    filled = np.abs(pixels[:, :, :3].astype(int) - FILL).max(axis=2) <= 2
    left = filled[:, :WIDTH // 2].sum()
    right = filled[:, WIDTH // 2:].sum()
    assert left == 0, f"{left} pixels filled on the side every fragment was thrown away"
    assert right > 1000, f"only {right} pixels filled on the side that was kept"
    return (f"a thrown away fragment writes no stencil: {right} pixels filled where kept, "
            f"none where not, {save('stencil_discarded', pixels)}")


@check
def separate_alpha_blending() -> str:
    """
    Color channels blending the usual way while the alpha channel takes the source's alpha
    whole, which is what keeps drawing something half transparent from eating into the alpha
    of what it lands on, see Camera.init_context.
    """
    device = get_device()
    records = triangle_records(color=(1.0, 0.0, 0.0, 0.5))
    # Large enough to cover the frame, so what is sampled is squarely inside it
    records["point"] = [[-3.0, -1.0, 0.0], [3.0, -1.0, 0.0], [0.0, 3.0, 0.0]]
    pipeline, bind_group, _ = pulling_pipeline(
        device, records,
        blend={
            "color": {
                "src_factor": wgpu.BlendFactor.src_alpha,
                "dst_factor": wgpu.BlendFactor.one_minus_src_alpha,
                "operation": wgpu.BlendOperation.add,
            },
            "alpha": {
                "src_factor": wgpu.BlendFactor.one,
                "dst_factor": wgpu.BlendFactor.one_minus_src_alpha,
                "operation": wgpu.BlendOperation.add,
            },
        },
        primitive={"topology": wgpu.PrimitiveTopology.triangle_list},
    )

    def draw(render_pass):
        render_pass.set_pipeline(pipeline)
        render_pass.set_bind_group(0, bind_group)
        render_pass.draw(3)

    # Onto nothing at all, so what comes out is the source's own alpha rather than half of it
    pixels = render_offscreen(device, draw, size=(64, 64), clear=(0.0, 0.0, 0.0, 0.0))
    red, _, _, alpha = pixels[32, 32]
    assert abs(int(red) - 128) <= 2, f"the color channel came out {red}, not half of red"
    assert abs(int(alpha) - 128) <= 2, \
        f"the alpha channel came out {alpha}, which is what blending it like a color gives"
    return "the alpha channel takes the source's alpha whole while colors blend as usual"


def main() -> int:
    wanted = sys.argv[1] if len(sys.argv) > 1 else ""
    failures = 0
    for func in CHECKS:
        if wanted and wanted not in func.__name__:
            continue
        try:
            note = func()
            print(f"  yes  {func.__name__:22s} {note}")
        except Exception as e:
            failures += 1
            print(f"  NO   {func.__name__:22s} {type(e).__name__}: {e}")
            traceback.print_exc(limit=3)
    print()
    print(f"{failures} of the plan's assumptions did not hold" if failures
          else "every assumption checked held")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
