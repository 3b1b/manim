/*
Each bezier of a path contributes two triangles: one reaching back to the mobject's base
point, which together with those of the other beziers covers the interior of the path, and
one hugging the curve itself, whose fragments falling outside it are cut away.

Nothing here decides what is inside the path. The winding number around each pixel does,
counted in the stencil buffer from which way each of these triangles happens to face once
projected, see VShaderWrapper.render_fill.
*/
#INSERT mobject_uniforms.wgsl
#INSERT frame_uniforms.wgsl
#INSERT read_data.wgsl
#INSERT project_point.wgsl
#INSERT fill_color.wgsl
#INSERT finalize_color.wgsl
#INSERT clip_test.wgsl

const VERTS_PER_CURVE: u32 = 6u;
// Consecutive beziers share an anchor, so curve n begins at record 2n
const RECORD_STEP: u32 = 2u;

// A quadratic bezier curve with these points coincides with y = x^2
const SIMPLE_QUADRATIC = array<vec2f, 3>(
    vec2f(0.0, 0.0), vec2f(0.5, 0.0), vec2f(1.0, 1.0),
);

struct VertexOutput {
    @builtin(position) position: vec4f,
    @location(0) clip_distances: vec4f,
    @location(1) color: vec4f,
    // Whether this vertex belongs to the triangle covering the interior, which is kept
    // whole, rather than to the one hugging the curve, which gets cut
    @location(2) fill_all: f32,
    // uv space is where the curve coincides with y = x^2
    @location(3) uv_coords: vec2f,
}

@vertex
fn vs_main(@builtin(vertex_index) index: u32) -> VertexOutput {
    var out: VertexOutput;
    let curve = index / VERTS_PER_CURVE;
    let corner = index % VERTS_PER_CURVE;
    let record = RECORD_STEP * curve;

    let controls = array<vec3f, 3>(
        read_vec3(record, DATA_OFFSET_point),
        read_vec3(record + 1u, DATA_OFFSET_point),
        read_vec3(record + 2u, DATA_OFFSET_point),
    );
    /*
    Curves are marked as ended when the handle after the first anchor is set equal to that
    anchor. Nothing to draw for those, or for a clear fill, so collapse all six corners onto
    one point to leave no area to rasterize.
    */
    if (all(controls[0] == controls[1]) || max(mob.fill_rgba.a, mob.fill_rgba_end.a) == 0.0) {
        out.position = vec4f(0.0, 0.0, 0.0, 1.0);
        return out;
    }

    /*
    The fan reaching back to the first point of this curve's own subpath covers the interior.
    Where the subpath closes back on itself the anchor makes no difference, the winding coming
    out the same wherever the fan reaches from; where it is left open, the fan is what closes
    it, and its own start is where the border closes it too, see stroke.wgsl.
    */
    let subpath = read_vec2(record, DATA_OFFSET_subpath_range);
    let base_point = read_vec3(u32(i32(record) - i32(subpath.x)), DATA_OFFSET_point);

    /*
    The first triangle fills in towards the base point, the second hugs the curve. No
    orientation is computed for either, since the sign of their contribution to the winding
    number comes for free from whether they end up front or back facing once projected.
    */
    let corner_index = corner % 3u;
    var point: vec3f;
    var fan = array<vec3f, 3>(base_point, controls[0], controls[2]);
    var curve_points = controls;
    if (corner < 3u) {
        out.fill_all = 1.0;
        point = fan[corner_index];
    } else {
        out.fill_all = 0.0;
        point = curve_points[corner_index];
    }

    var uv = SIMPLE_QUADRATIC;
    out.uv_coords = uv[corner_index];
    out.color = finalize_color(fill_color_at(point), point, mob.unit_normal);
    let projection = project_point(point);
    out.position = projection.position;
    out.clip_distances = projection.clip_distances;
    return out;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4f {
    clip_test(in.clip_distances);
    if (in.color.a == 0.0) { discard; }
    /*
    For the triangles hugging a bezier curve, cut away the part of the triangle falling
    outside it. In uv space the curve coincides with y = x^2. Note that this same test runs
    during both the stencil and the cover pass, so the region counted is exactly the region
    colored in.
    */
    if (in.fill_all == 0.0 && in.uv_coords.y < in.uv_coords.x * in.uv_coords.x) { discard; }
    return in.color;
}
