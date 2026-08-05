/*
A surface with an image stretched over it, and optionally a second image for the side facing
away from the light, the two blended by which way the surface faces there.
*/
#INSERT mobject_uniforms.wgsl
#INSERT frame_uniforms.wgsl
#INSERT read_data.wgsl
#INSERT project_point.wgsl
#INSERT surface_mesh.wgsl
#INSERT finalize_color.wgsl
#INSERT clip_test.wgsl

// TEXTURES

// How far either side of facing the light the blend between the two images runs
const DARK_SHIFT: f32 = 0.2;

struct VertexOutput {
    @builtin(position) position: vec4f,
    @location(0) clip_distances: vec4f,
    @location(1) point: vec3f,
    @location(2) unit_normal: vec3f,
    @location(3) im_coords: vec2f,
    @location(4) opacity: f32,
}

@vertex
fn vs_main(@builtin(vertex_index) index: u32) -> VertexOutput {
    var out: VertexOutput;
    let vertex = read_surface_vertex(index);
    if (!vertex.drawn) {
        out.position = vec4f(0.0, 0.0, 0.0, 1.0);
        return out;
    }
    let projection = project_point(vertex.point);
    out.position = projection.position;
    out.clip_distances = projection.clip_distances;
    out.point = vertex.point;
    out.unit_normal = vertex.normal;
    out.im_coords = read_vec2(vertex.index, DATA_OFFSET_im_coords);
    out.opacity = read_float(vertex.index, DATA_OFFSET_opacity);
    return out;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4f {
    clip_test(in.clip_distances);
    var color = textureSample(LightTexture, image_sampler, in.im_coords);
    if (mob.num_textures == 2.0) {
        let dark_color = textureSample(DarkTexture, image_sampler, in.im_coords);
        let facing_light = dot(normalize(frame.light_position - in.point), in.unit_normal);
        color = mix(dark_color, color, smoothstep(-DARK_SHIFT, DARK_SHIFT, facing_light));
    }
    if (color.a == 0.0) { discard; }

    var result = finalize_color(color, in.point, in.unit_normal);
    result.a = in.opacity;
    return result;
}
