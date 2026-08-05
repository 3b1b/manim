/*
A dot is drawn as a quad facing the camera, with the disc cut out of it per fragment, so
that it stays round however close the camera gets and however the frame is turned.
*/
#INSERT mobject_uniforms.wgsl
#INSERT frame_uniforms.wgsl
#INSERT read_data.wgsl
#INSERT project_point.wgsl
#INSERT finalize_color.wgsl
#INSERT clip_test.wgsl

// Two triangles of corners, one quad's worth
const CORNERS = array<vec2f, 6>(
    vec2f(-1.0, -1.0), vec2f(-1.0, 1.0), vec2f(1.0, -1.0),
    vec2f(1.0, -1.0), vec2f(-1.0, 1.0), vec2f(1.0, 1.0),
);
const VERTS_PER_DOT: u32 = 6u;

struct VertexOutput {
    @builtin(position) position: vec4f,
    @location(0) clip_distances: vec4f,
    @location(1) color: vec4f,
    @location(2) scaled_aaw: f32,
    @location(3) point: vec3f,
    @location(4) to_cam: vec3f,
    @location(5) center: vec3f,
    @location(6) radius: f32,
    @location(7) uv_coords: vec2f,
}

@vertex
fn vs_main(@builtin(vertex_index) index: u32) -> VertexOutput {
    let dot_index = index / VERTS_PER_DOT;
    var corners = CORNERS;
    let corner = corners[index % VERTS_PER_DOT];

    let center = read_vec3(dot_index, DATA_OFFSET_point);
    let radius = read_float(dot_index, DATA_OFFSET_radius);

    let to_cam = normalize(frame.camera_position - center);
    let right = radius * normalize(cross(vec3f(0.0, 1.0, 1.0), to_cam));
    let up = radius * normalize(cross(to_cam, right));
    let point = center + corner.x * right + corner.y * up;

    let projection = project_point(point);

    var out: VertexOutput;
    out.position = projection.position;
    out.clip_distances = projection.clip_distances;
    out.color = read_vec4(dot_index, DATA_OFFSET_rgba);
    out.scaled_aaw = (mob.anti_alias_width * get_pixel_unit_size()) / radius;
    out.point = point;
    out.to_cam = to_cam;
    out.center = center;
    out.radius = radius;
    out.uv_coords = corner;
    return out;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4f {
    clip_test(in.clip_distances);
    let r = length(in.uv_coords);
    if (r > 1.0) { discard; }

    var color = in.color;
    if (mob.glow_factor > 0.0) {
        color.a *= pow(1.0 - r, mob.glow_factor);
    }
    if (any(mob.shading != vec3f(0.0))) {
        let point_3d = in.point + in.radius * sqrt(1.0 - r * r) * in.to_cam;
        color = finalize_color(color, point_3d, normalize(point_3d - in.center));
    }
    // Said with its edges the right way round, since a reversed smoothstep is
    // undefined in WGSL, and smoothstep(a, b, x) is exactly 1 - smoothstep(b, a, x)
    color.a *= 1.0 - smoothstep(1.0 - in.scaled_aaw, 1.0, r);
    return color;
}
