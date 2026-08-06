/*
A stroke along a path, drawn as a strip of quads following each bezier, with a fan of
triangles rounding off the joint at each end.

The border around a fill is a stroke like any other, except that it takes its color and
width from the fill's fields rather than the stroke's, and that a width of zero still draws
a band just wide enough to anti-alias the fill's edge. That is settled when the shader is
compiled rather than asked per draw, so the two are two modules from this one source, see
VShaderWrapper.init_program.
*/
const IS_FILL_BORDER: bool = false;

#INSERT mobject_uniforms.wgsl
#INSERT frame_uniforms.wgsl
#INSERT read_data.wgsl
#INSERT project_point.wgsl
#INSERT fill_color.wgsl
#INSERT finalize_color.wgsl
#INSERT clip_test.wgsl

// Beyond this much alignment between the tangent and the view direction, the step to the
// side of the curve gets adjusted to avoid glitches
const ALIGNMENT_THRESHOLD: f32 = 0.99;
// Used to determine how many lines to break the curve into
const POLYLINE_FACTOR: f32 = 100.0;
const MAX_STEPS: i32 = 32;
// Stands in for a record index where there is no neighboring curve to read
const NONE: i32 = -1;
// Over this range of turn cosines, a joint eases from a sharp miter to a round end
const ROUND_COS_SHARP: f32 = -0.5;
const ROUND_COS_ROUND: f32 = -0.95;
// Number of units spanned by a stroke_width of 1 in a default scale frame, so for instance
// a stroke_width of 100 comes out one unit thick
const STROKE_WIDTH_CONVERSION: f32 = 0.01;

/*
A bezier is three consecutive records of the buffer, sharing its last with the next curve's
first, so curve n begins at record 2n. It's drawn as one quad for each of the polyline
segments it gets broken into, and that count per curve has to match what VShaderWrapper
draws.

The last few of those segments go instead to a fan of triangles rounding off the joint at
the curve's end. A curve rarely needs anywhere near its full allowance of polyline steps, so
this costs nothing that was being used.
*/
const RECORD_STEP: u32 = 2u;
const VERTS_PER_CURVE: u32 = u32(6 * (MAX_STEPS - 1));
const JOINT_SEGMENTS: i32 = 3;
const POLYLINE_SEGMENTS: i32 = MAX_STEPS - 1 - JOINT_SEGMENTS;
const FAN_TRIANGLES: i32 = 2 * JOINT_SEGMENTS;

// The two triangles of one segment's quad, as (which end of it, which side)
const CORNERS = array<vec2f, 6>(
    vec2f(0.0, -1.0), vec2f(0.0, 1.0), vec2f(1.0, -1.0),
    vec2f(1.0, -1.0), vec2f(0.0, 1.0), vec2f(1.0, 1.0),
);

struct VertexOutput {
    @builtin(position) position: vec4f,
    @location(0) clip_distances: vec4f,
    @location(1) color: vec4f,
    // Distance to the curve, and half the curve's width, both as a ratio of the
    // antialias width
    @location(2) dist_to_aaw: f32,
    @location(3) half_width_to_aaw: f32,
}

fn point_on_quadratic(t: f32, c0: vec3f, c1: vec3f, c2: vec3f) -> vec3f {
    return c0 + c1 * t + c2 * t * t;
}

fn tangent_on_quadratic(t: f32, c1: vec3f, c2: vec3f) -> vec3f {
    return c1 + 2.0 * c2 * t;
}

// The vector as it appears in the plane perpendicular to a given unit normal
fn project(vect: vec3f, normal: vec3f) -> vec3f {
    return vect - dot(vect, normal) * normal;
}

fn rotate_vector(vect: vec3f, normal: vec3f, turn: vec2f) -> vec3f {
    return turn.x * vect + turn.y * cross(normal, vect);
}

/*
The tangent of the curve neighbouring this one at the given end, pointing the same way along
the path. Where the subpath ends, and so has no neighbour to make a joint with, this comes
back as zero.

A border's closing chord is a neighbour like any other curve: it runs straight, so either of its
endpoints stands in for the handle a curve would have had at the other.
*/
fn neighbor_tangent(record: i32, subpath: vec2f, at_start: bool, anchor: vec3f) -> vec3f {
    // How far the subpath reaches either side of the record, see VMobject.set_subpath_range
    let first = record - i32(subpath.x);
    let last = record + i32(subpath.y);
    let closed = all(
        read_vec3(u32(first), DATA_OFFSET_point) == read_vec3(u32(last), DATA_OFFSET_point)
    );
    if (at_start) {
        var previous = NONE;
        if (record > first) {
            previous = record - 1;
        } else if (closed) {
            previous = last - 1;
        } else if (IS_FILL_BORDER) {
            previous = last;
        }
        if (previous == NONE) { return vec3f(0.0); }
        return anchor - read_vec3(u32(previous), DATA_OFFSET_point);
    }
    var next = NONE;
    if (record + 2 < last) {
        next = record + 3;
    } else if (closed || record == last) {
        next = first + 1;
    } else if (IS_FILL_BORDER) {
        next = first;
    }
    if (next == NONE) { return vec3f(0.0); }
    return read_vec3(u32(next), DATA_OFFSET_point) - anchor;
}

/*
The tangent as it appears in the plane the stroke is drawn in, or zero for anything
degenerate, such as the tangent at a repeated point, which leaves no direction to work with
and so no joint to make.
*/
fn flat_tangent(tangent: vec3f, facing_normal: vec3f) -> vec3f {
    let flattened = project(tangent, facing_normal);
    if (all(flattened == vec3f(0.0))) { return vec3f(0.0); }
    return normalize(flattened);
}

/*
How far along its tangent the incoming strip must run to reach where the outgoing strip's
edge meets it, the exact miter. That is the one place the two meet with no gap, but it runs
off arbitrarily far as the turn approaches a full reversal. So a sharpening turn keeps less
and less of that reach, and the roundness setting scales back whatever is left. Either way
the joint fan rounds off what gets given up.
*/
fn joint_shift(tan_in: vec3f, tan_out: vec3f, facing_normal: vec3f) -> f32 {
    let a = flat_tangent(tan_in, facing_normal);
    let b = flat_tangent(tan_out, facing_normal);
    if (all(a == vec3f(0.0)) || all(b == vec3f(0.0))) { return 0.0; }
    let sin_angle = dot(cross(a, b), facing_normal);
    // Both a straight joint and a full reversal want no shift, and both have a vanishing
    // sine, which would otherwise divide out to something unbounded
    if (abs(sin_angle) < 1e-6) { return 0.0; }
    let cos_angle = dot(a, b);
    let keep = smoothstep(ROUND_COS_ROUND, ROUND_COS_SHARP, cos_angle)
        * (1.0 - mob.joint_roundness);
    return keep * (cos_angle - 1.0) / sin_angle;
}

/*
Step perpendicular to the curve, out to the edge of the stroke, then along the curve by
however far the joint at this end reaches.
*/
fn step_to_corner(tangent: vec3f, facing_normal: vec3f, shift: f32, draw_flat: bool) -> vec3f {
    var unflattened = tangent;
    if (!draw_flat) {
        unflattened = project(tangent, facing_normal);
    }
    let unit_tan = normalize(unflattened);
    var step = normalize(cross(facing_normal, unit_tan));

    /*
    For non-flat stroke, there can be glitches when the tangent direction lines up very
    closely with the direction to the camera, treated here as the unit normal. To avoid
    those, this smoothly transitions to a step direction perpendicular to the true curve
    normal.
    */
    let alignment = abs(dot(normalize(tangent), facing_normal));
    if (alignment > ALIGNMENT_THRESHOLD) {
        let perp = normalize(cross(mob.unit_normal, tangent));
        step = mix(
            step, project(step, perp), smoothstep(ALIGNMENT_THRESHOLD, 1.0, alignment),
        );
    }
    return step + shift * unit_tan;
}

@vertex
fn vs_main(@builtin(vertex_index) vertex_index: u32) -> VertexOutput {
    var out: VertexOutput;
    let blank = vec4f(0.0, 0.0, 0.0, 1.0);

    let curve = vertex_index / VERTS_PER_CURVE;
    let within = vertex_index % VERTS_PER_CURVE;
    let segment = i32(within / 6u);
    let tri_vert = i32(within % 6u);
    var corners = CORNERS;
    let corner = corners[tri_vert];
    let record = RECORD_STEP * curve;

    // Segments past the polyline's allowance go to the fan rounding off the joint
    let joint_fan = segment >= POLYLINE_SEGMENTS;

    let subpath = read_vec2(record, DATA_OFFSET_subpath_range);
    var controls = array<vec3f, 3>(
        read_vec3(record, DATA_OFFSET_point),
        read_vec3(record + 1u, DATA_OFFSET_point),
        read_vec3(record + 2u, DATA_OFFSET_point),
    );
    /*
    A fill counts its winding as though every subpath ran back to its own first point, see
    fill.wgsl, so the border traces that chord too, in the slot the curve marking the subpath's
    end sits in. A subpath which already comes round leaves the chord no length, so it draws
    nothing.
    */
    if (IS_FILL_BORDER && subpath.y == 0.0) {
        controls[2] = read_vec3(u32(i32(record) - i32(subpath.x)), DATA_OFFSET_point);
        controls[1] = 0.5 * (controls[0] + controls[2]);
    }
    let widths = array<f32, 3>(
        read_float(record, DATA_OFFSET_stroke_width),
        read_float(record + 1u, DATA_OFFSET_stroke_width),
        read_float(record + 2u, DATA_OFFSET_stroke_width),
    );
    let colors = array<vec4f, 3>(
        read_vec4(record, DATA_OFFSET_stroke_rgba),
        read_vec4(record + 1u, DATA_OFFSET_stroke_rgba),
        read_vec4(record + 2u, DATA_OFFSET_stroke_rgba),
    );

    // Coefficients such that the quadratic bezier is c0 + c1 * t + c2 * t^2
    let c0 = controls[0];
    let c1 = 2.0 * (controls[1] - controls[0]);
    let c2 = controls[0] - 2.0 * controls[1] + controls[2];

    // How many line segments the curve is divided into, from the area of the triangle its
    // control points make
    let area = 0.5 * length(cross(controls[1] - controls[0], controls[2] - controls[0]));
    let count = i32(round(POLYLINE_FACTOR * sqrt(area) / get_frame_unit_size()));
    let n_steps = min(2 + count, POLYLINE_SEGMENTS + 1);

    /*
    Nothing to draw for a curve marked as ended, by setting the handle after the first anchor
    equal to that anchor, nor for one with no width or no opacity, nor for polyline segments
    past however many this curve was divided into. Collapsing all six corners onto one point
    leaves no area to rasterize.
    */
    var nothing_to_draw = all(controls[0] == controls[1]);
    nothing_to_draw = nothing_to_draw || (!joint_fan && segment >= n_steps - 1);
    if (IS_FILL_BORDER) {
        // A fill's border takes its color from the fill rather than from the records
        nothing_to_draw = nothing_to_draw || max(mob.fill_rgba.a, mob.fill_rgba_end.a) == 0.0;
    } else {
        nothing_to_draw = nothing_to_draw
            || all(vec3f(widths[0], widths[1], widths[2]) == vec3f(0.0))
            || all(vec3f(colors[0].a, colors[1].a, colors[2].a) == vec3f(0.0));
    }
    if (nothing_to_draw) {
        out.position = blank;
        return out;
    }

    // The fan sits at the curve's end, where the polyline's last point also lands
    let index = segment + i32(corner.x);
    var t = 1.0;
    if (!joint_fan) {
        t = f32(index) / f32(n_steps - 1);
    }
    var point = controls[2];
    if (!joint_fan) {
        point = point_on_quadratic(t, c0, c1, c2);
    }
    let tangent = tangent_on_quadratic(t, c1, c2);

    /*
    By default stroke width is measured relative to the frame, so putting it in the units of
    the space being drawn means scaling by that space's frame size, which keeps a given
    stroke width looking the same at any zoom level. When it's measured relative to the scene
    instead, no such conversion is needed, and zooming in makes the stroke look thicker.
    */
    var own_width = mix(widths[0], widths[2], t);
    if (IS_FILL_BORDER) {
        own_width = mob.fill_border_width;
    }
    let width = STROKE_WIDTH_CONVERSION
        * mix(get_frame_unit_size(), 1.0, mob.stroke_width_in_scene_units)
        * own_width;

    let draw_flat = mob.flat_stroke != 0.0 || mob.is_fixed_in_frame != 0.0;
    var facing_normal = normalize(frame.camera_position - point);
    if (draw_flat) {
        facing_normal = mob.unit_normal;
    }

    // The fill's color varies linearly, so reading it off at this very point comes to the
    // same thing as interpolating between its ends, for a couple fewer operations
    var own_color = mix(colors[0], colors[2], t);
    if (IS_FILL_BORDER) {
        own_color = fill_color_at(point);
    }
    out.color = finalize_color(own_color, point, facing_normal);

    // anti_alias_width is measured in pixels. The frag shader receives a value from -1 to 1,
    // reflecting where in the stroke this corner is.
    let aaw = max(mob.anti_alias_width * get_pixel_unit_size(), 1e-8);
    let half_width = 0.5 * (width + aaw);

    // Each end of a curve makes a joint with whatever neighbours it there
    let at_start = !joint_fan && index == 0;
    let at_joint = joint_fan || at_start || index == n_steps - 1;
    var neighbor = vec3f(0.0);
    if (at_joint) {
        neighbor = neighbor_tangent(i32(record), subpath, at_start, point);
    }
    let has_joint = at_joint && !all(neighbor == vec3f(0.0));

    /*
    Measured from the incoming tangent to the outgoing one either way, so at a curve's start,
    where this curve is the outgoing one, the shift runs the other direction.
    */
    var shift = 0.0;
    if (has_joint) {
        if (at_start) {
            shift = -joint_shift(neighbor, tangent, facing_normal);
        } else {
            shift = joint_shift(tangent, neighbor, facing_normal);
        }
    }

    var step: vec3f;
    var dist_to_curve: f32;
    var edge_dist: f32;
    if (joint_fan) {
        /*
        Cutting the miter back leaves a wedge uncovered between the two strips, both of which
        end on a line running through this joint. The fan sweeps an arc from one of those
        lines to the other, at the radius the strips' own corners reach, so the cut comes out
        rounded. For an exact miter the two lines coincide and the sweep closes to nothing,
        leaving the corner sharp.
        */
        let tan_in = flat_tangent(tangent, facing_normal);
        let tan_out = flat_tangent(neighbor, facing_normal);
        if (!has_joint || all(tan_in == vec3f(0.0)) || all(tan_out == vec3f(0.0))) {
            out.position = blank;
            return out;
        }
        var outward = -1.0;
        if (dot(cross(tan_in, tan_out), facing_normal) < 0.0) {
            outward = 1.0;
        }
        let edge_in = outward * normalize(cross(facing_normal, tan_in) + shift * tan_in);
        let edge_out = outward * normalize(cross(facing_normal, tan_out) - shift * tan_out);
        let sweep = atan2(
            dot(cross(edge_in, edge_out), facing_normal), dot(edge_in, edge_out),
        );

        // Of each triangle's three vertices, one sits at the joint and two on the arc
        let fan_tri = 2 * (segment - POLYLINE_SEGMENTS) + tri_vert / 3;
        let fan_vert = tri_vert % 3;
        let along = f32(fan_tri + fan_vert - 1) / f32(FAN_TRIANGLES);

        step = rotate_vector(
            edge_in, facing_normal, vec2f(cos(along * sweep), sin(along * sweep)),
        );
        // The corners reach out by this much, being a step out plus a shift along
        edge_dist = sqrt(1.0 + shift * shift) * 0.5 * width;
        dist_to_curve = 0.0;
        if (fan_vert != 0) {
            dist_to_curve = edge_dist + 0.5 * aaw;
        }
    } else {
        step = step_to_corner(tangent, facing_normal, shift, draw_flat);
        edge_dist = 0.5 * width;
        dist_to_curve = corner.y * half_width;
    }

    out.half_width_to_aaw = edge_dist / aaw;
    out.dist_to_aaw = dist_to_curve / aaw;
    let projection = project_point(point + dist_to_curve * step);
    out.position = projection.position;
    out.clip_distances = projection.clip_distances;
    return out;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4f {
    clip_test(in.clip_distances);
    var color = in.color;
    // A signed distance to the region around the curve which is to be colored
    let signed_dist_to_region = abs(in.dist_to_aaw) - in.half_width_to_aaw;
    color.a *= 1.0 - smoothstep(-0.5, 0.5, signed_dist_to_region);
    return color;
}
