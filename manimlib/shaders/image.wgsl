/*
An image is four corners with a texture stretched over them, so unlike everything else here
the shader does no shaping at all: it reads the corners, and reads the image at each point.
*/
#INSERT mobject_uniforms.wgsl
#INSERT frame_uniforms.wgsl
#INSERT read_data.wgsl
#INSERT project_point.wgsl
#INSERT quad_corners.wgsl
#INSERT clip_test.wgsl

// TEXTURES

struct VertexOutput {
    @builtin(position) position: vec4f,
    @location(0) clip_distances: vec4f,
    @location(1) im_coords: vec2f,
    @location(2) opacity: f32,
}

@vertex
fn vs_main(@builtin(vertex_index) index: u32) -> VertexOutput {
    var out: VertexOutput;
    if (index >= VERTS_PER_QUAD) {
        out.position = vec4f(0.0, 0.0, 0.0, 1.0);
        return out;
    }
    let corner = quad_corner(index);

    let projection = project_point(read_vec3(corner, DATA_OFFSET_point));
    out.position = projection.position;
    out.clip_distances = projection.clip_distances;
    out.im_coords = read_vec2(corner, DATA_OFFSET_im_coords);
    out.opacity = read_float(corner, DATA_OFFSET_opacity);
    return out;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4f {
    clip_test(in.clip_distances);
    var color = textureSample(Texture, image_sampler, in.im_coords);
    color.a *= in.opacity;
    return color;
}
