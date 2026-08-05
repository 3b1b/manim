/*
A finished frame drawn onto whatever a window gave us to present.

One triangle covers the screen rather than two, its corners reaching past the far side of
clip space so that its middle is exactly what the frame fills, which needs no buffer of
vertices and no index list.
*/
@group(0) @binding(0) var frame_texture: texture_2d<f32>;
@group(0) @binding(1) var frame_sampler: sampler;

struct VertexOutput {
    @builtin(position) position: vec4f,
    @location(0) im_coords: vec2f,
}

@vertex
fn vs_main(@builtin(vertex_index) index: u32) -> VertexOutput {
    var corners = array<vec2f, 3>(vec2f(-1.0, -1.0), vec2f(3.0, -1.0), vec2f(-1.0, 3.0));
    let corner = corners[index];

    var out: VertexOutput;
    out.position = vec4f(corner, 0.0, 1.0);
    // Clip space has y upwards and a texture has it downwards
    out.im_coords = vec2f(0.5 + 0.5 * corner.x, 0.5 - 0.5 * corner.y);
    return out;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4f {
    return textureSample(frame_texture, frame_sampler, in.im_coords);
}
