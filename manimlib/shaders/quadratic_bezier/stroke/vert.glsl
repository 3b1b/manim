#version 330

/*
The border around a fill is a stroke like any other, except that it takes its
color and width from the fill's fields rather than the stroke's, and that a width
of zero still draws a band just wide enough to anti-alias the fill's edge.
*/
uniform bool is_fill_border;

out vec4 color;
out float dist_to_aaw;
out float half_width_to_aaw;

// Beyond this much alignment between the tangent and the view direction, the step
// to the side of the curve gets adjusted to avoid glitches
const float ALIGNMENT_THRESHOLD = 0.99;
// Used to determine how many lines to break the curve into
const float POLYLINE_FACTOR = 100;
const int MAX_STEPS = 32;
// Stands in for a record index where there is no neighboring curve to read
const int NONE = -1;
/*
Shorter than this and a vector holds no direction worth reading. Squaring
components that small to take a length underflows to zero, so normalizing one
gives NaN, and a single NaN position quietly drops every triangle it touches.
Points that are meant to coincide, such as the anchor and handle marking the end
of a curve, come to rest a hair apart this often enough that testing them for
equality will miss them, so everything degenerate is measured against this instead.
*/
const float DEGENERATE_LENGTH = 1e-12;
// Over this range of turn cosines, a joint eases from a sharp miter to a round end
const float ROUND_COS_START = -0.5;
const float ROUND_COS_END = -0.95;
// Number of units spanned by a stroke_width of 1 in a default scale frame,
// so for instance a stroke_width of 100 comes out one unit thick
const float STROKE_WIDTH_CONVERSION = 0.01;

/*
A bezier is three consecutive records of the buffer, sharing its last with the
next curve's first, so curve n begins at record 2n. It's drawn as one quad for
each of the polyline segments it gets broken into, and that count per curve has
to match what VShaderWrapper draws.

The last few of those segments go instead to a fan of triangles rounding off the
joint at the curve's end. A curve rarely needs anywhere near its full allowance of
polyline steps, so this costs nothing that was being used.
*/
const int RECORD_STEP = 2;
const int VERTS_PER_CURVE = 6 * (MAX_STEPS - 1);
const int JOINT_SEGMENTS = 3;
const int POLYLINE_SEGMENTS = MAX_STEPS - 1 - JOINT_SEGMENTS;
const int FAN_TRIANGLES = 2 * JOINT_SEGMENTS;

// The two triangles of one segment's quad, as (which end of it, which side)
const vec2 CORNERS[6] = vec2[6](
    vec2(0, -1), vec2(0, 1), vec2(1, -1),
    vec2(1, -1), vec2(0, 1), vec2(1, 1)
);

#INSERT vmobject_uniforms.glsl
#INSERT emit_gl_Position.glsl
#INSERT fill_color.glsl
#INSERT finalize_color.glsl
#INSERT read_data.glsl

vec3 point_on_quadratic(float t, vec3 c0, vec3 c1, vec3 c2){
    return c0 + c1 * t + c2 * t * t;
}

vec3 tangent_on_quadratic(float t, vec3 c1, vec3 c2){
    return c1 + 2 * c2 * t;
}

vec3 project(vec3 vect, vec3 normal){
    /* Project the vector onto the plane perpendicular to a given unit normal */
    return vect - dot(vect, normal) * normal;
}

vec3 rotate_vector(vec3 vect, vec3 normal, vec2 turn){
    vec3 perp = cross(normal, vect);
    return turn.x * vect + turn.y * perp;
}

vec3 neighbor_tangent(int record, bool at_start, vec3 anchor){
    /*
    The tangent of the curve neighbouring this one at the given end, pointing the
    same way along the path. Where the subpath ends, and so has no neighbour to make
    a joint with, this comes back as zero.
    */
    vec2 subpath_range = read_vec2(record, DATA_OFFSET_subpath_range);
    int first = int(subpath_range.x);
    int last = int(subpath_range.y);
    bool closed = length(read_vec3(first, DATA_OFFSET_point) - read_vec3(last, DATA_OFFSET_point)) < DEGENERATE_LENGTH;
    if (at_start){
        int prev = record > first ? record - 1 : (closed ? last - 1 : NONE);
        return prev == NONE ? vec3(0.0) : anchor - read_vec3(prev, DATA_OFFSET_point);
    }
    int next = record + 2 < last ? record + 3 : (closed ? first + 1 : NONE);
    return next == NONE ? vec3(0.0) : read_vec3(next, DATA_OFFSET_point) - anchor;
}

bool flatten_tangent(vec3 tangent, vec3 facing_normal, out vec3 result){
    /*
    The tangent as it appears in the plane the stroke is drawn in. Comes back false
    for anything degenerate, such as the tangent at a repeated point, which leaves
    no direction to work with and so no joint to make.
    */
    vec3 flat_tan = project(tangent, facing_normal);
    if (length(flat_tan) < DEGENERATE_LENGTH) return false;
    result = normalize(flat_tan);
    return true;
}

float joint_shift(vec3 tan_in, vec3 tan_out, vec3 facing_normal){
    /*
    How far along its tangent the incoming strip must run to reach where the outgoing
    strip's edge meets it, the exact miter. That is the one place the two meet with no
    gap, but it runs off arbitrarily far as the turn approaches a full reversal. So a
    sharpening turn keeps less and less of that reach, and the roundness setting scales
    back whatever is left. Either way the joint fan rounds off what gets given up.
    */
    vec3 a, b;
    if (!flatten_tangent(tan_in, facing_normal, a)) return 0.0;
    if (!flatten_tangent(tan_out, facing_normal, b)) return 0.0;
    float sin_angle = dot(cross(a, b), facing_normal);
    // Both a straight joint and a full reversal want no shift, and both have a
    // vanishing sine, which would otherwise divide out to something unbounded
    if (abs(sin_angle) < 1e-6) return 0.0;
    float cos_angle = dot(a, b);
    float keep = (1.0 - smoothstep(ROUND_COS_START, ROUND_COS_END, cos_angle))
        * (1.0 - joint_roundness);
    return keep * (cos_angle - 1.0) / sin_angle;
}

vec3 step_to_corner(vec3 tangent, vec3 facing_normal, float shift, bool draw_flat){
    /*
    Step perpendicular to the curve, out to the edge of the stroke, then along the
    curve by however far the joint at this end reaches.
    */
    vec3 unit_tan = normalize(draw_flat ? tangent : project(tangent, facing_normal));
    vec3 step = normalize(cross(facing_normal, unit_tan));

    // For non-flat stroke, there can be glitches when the tangent direction lines up
    // very closely with the direction to the camera, treated here as the unit normal.
    // To avoid those, this smoothly transitions to a step direction perpendicular to
    // the true curve normal.
    float alignment = abs(dot(normalize(tangent), facing_normal));
    if (alignment > ALIGNMENT_THRESHOLD) {
        vec3 perp = normalize(cross(unit_normal, tangent));
        step = mix(step, project(step, perp), smoothstep(ALIGNMENT_THRESHOLD, 1.0, alignment));
    }
    return step + shift * unit_tan;
}

void main(){
    int curve = gl_VertexID / VERTS_PER_CURVE;
    int within = gl_VertexID % VERTS_PER_CURVE;
    int segment = within / 6;
    int tri_vert = within % 6;
    vec2 corner = CORNERS[tri_vert];
    int record = RECORD_STEP * curve;

    // Segments past the polyline's allowance go to the fan rounding off the joint
    bool joint_fan = (segment >= POLYLINE_SEGMENTS);

    vec3 controls[3] = vec3[3](
        read_vec3(record + 0, DATA_OFFSET_point),
        read_vec3(record + 1, DATA_OFFSET_point),
        read_vec3(record + 2, DATA_OFFSET_point)
    );
    float widths[3] = float[3](
        read_float(record + 0, DATA_OFFSET_stroke_width),
        read_float(record + 1, DATA_OFFSET_stroke_width),
        read_float(record + 2, DATA_OFFSET_stroke_width)
    );
    vec4 colors[3] = vec4[3](
        read_vec4(record + 0, DATA_OFFSET_stroke_rgba),
        read_vec4(record + 1, DATA_OFFSET_stroke_rgba),
        read_vec4(record + 2, DATA_OFFSET_stroke_rgba)
    );

    // Coefficients such that the quadratic bezier is c0 + c1 * t  + c2 * t^2
    vec3 c0 = controls[0];
    vec3 c1 = 2 * (controls[1] - controls[0]);
    vec3 c2 = controls[0] - 2 * controls[1] + controls[2];

    // Estimate how many line segments the curve should be divided into
    // based on the area of the triangle defined by these control points
    float area = 0.5 * length(cross(controls[1] - controls[0], controls[2] - controls[0]));
    int count = int(round(POLYLINE_FACTOR * sqrt(area) / get_frame_unit_size()));
    int n_steps = min(2 + count, POLYLINE_SEGMENTS + 1);

    /*
    Nothing to draw for a curve marked as ended, by setting the handle after the
    first anchor equal to that anchor, nor for one with no width or no opacity, nor
    for polyline segments past however many this curve was divided into, nor for a
    joint that has no neighbor to turn towards. Collapsing all six corners onto one
    point leaves no area to rasterize.
    */
    bool blank = (length(controls[1] - controls[0]) < DEGENERATE_LENGTH);
    blank = blank || (!joint_fan && segment >= n_steps - 1);
    if (!is_fill_border){
        blank = blank || (vec3(widths[0], widths[1], widths[2]) == vec3(0.0));
    }
    // A fill's border takes its color from the fill rather than from the records
    blank = blank || (is_fill_border ?
        max(fill_rgba.a, fill_rgba_end.a) == 0.0 :
        vec3(colors[0].a, colors[1].a, colors[2].a) == vec3(0.0));
    if (blank){
        gl_Position = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }

    // The fan sits at the curve's end, where the polyline's last point also lands
    int index = segment + int(corner.x);
    float t = joint_fan ? 1.0 : float(index) / float(n_steps - 1);
    vec3 point = joint_fan ? controls[2] : point_on_quadratic(t, c0, c1, c2);
    vec3 tangent = tangent_on_quadratic(t, c1, c2);
    // Where the handle has come to rest on the anchor at this end, the tangent
    // vanishes and leaves no direction to step away from. Such a curve is a straight
    // run between its anchors, so the chord across it is the direction wanted.
    if (length(tangent) < DEGENERATE_LENGTH) tangent = controls[2] - controls[0];

    // By default stroke width is measured relative to the frame, so putting it in
    // the units of the space being drawn means scaling by that space's frame
    // size, which keeps a given stroke width looking the same at any zoom level.
    // When it's measured relative to the scene instead, no such conversion is
    // needed, and zooming in makes the stroke look thicker.
    float width = STROKE_WIDTH_CONVERSION
        * mix(get_frame_unit_size(), 1.0, stroke_width_in_scene_units)
        * (is_fill_border ? fill_border_width : mix(widths[0], widths[2], t));

    bool draw_flat = bool(flat_stroke) || bool(is_fixed_in_frame);
    vec3 facing_normal = draw_flat ? unit_normal : normalize(camera_position - point);

    // The fill's color varies linearly, so reading it off at this very point comes to
    // the same thing as interpolating between its ends, for a couple fewer operations
    vec4 own_color = is_fill_border ? fill_color_at(point) : mix(colors[0], colors[2], t);
    color = finalize_color(own_color, point, facing_normal);

    // anti_alias_width is measured in pixels. The frag shader receives a value
    // from -1 to 1, reflecting where in the stroke this corner is.
    float aaw = max(anti_alias_width * get_pixel_unit_size(), 1e-8);
    float half_width = 0.5 * (width + aaw);

    // Each end of a curve makes a joint with whatever neighbours it there
    bool at_start = !joint_fan && index == 0;
    bool at_joint = joint_fan || at_start || index == n_steps - 1;
    vec3 neighbor = at_joint ? neighbor_tangent(record, at_start, point) : vec3(0.0);
    bool has_joint = at_joint && length(neighbor) > DEGENERATE_LENGTH;

    /*
    Measured from the incoming tangent to the outgoing one either way, so at a curve's
    start, where this curve is the outgoing one, the shift runs the other direction.
    */
    float shift = 0.0;
    if (has_joint){
        shift = at_start ?
            -joint_shift(neighbor, tangent, facing_normal) :
            joint_shift(tangent, neighbor, facing_normal);
    }

    vec3 step;
    float dist_to_curve;
    float edge_dist;
    if (joint_fan){
        /*
        Cutting the miter back leaves a wedge uncovered between the two strips, both
        of which end on a line running through this joint. The fan sweeps an arc from
        one of those lines to the other, at the radius the strips' own corners reach,
        so the cut comes out rounded. For an exact miter the two lines coincide and
        the sweep closes to nothing, leaving the corner sharp.
        */
        if (!has_joint){
            gl_Position = vec4(0.0, 0.0, 0.0, 1.0);
            return;
        }
        vec3 tan_in, tan_out;
        if (!flatten_tangent(tangent, facing_normal, tan_in) ||
            !flatten_tangent(neighbor, facing_normal, tan_out)){
            gl_Position = vec4(0.0, 0.0, 0.0, 1.0);
            return;
        }
        float outward = dot(cross(tan_in, tan_out), facing_normal) < 0.0 ? 1.0 : -1.0;
        vec3 edge_in = outward * normalize(cross(facing_normal, tan_in) + shift * tan_in);
        vec3 edge_out = outward * normalize(cross(facing_normal, tan_out) - shift * tan_out);
        float sweep = atan(dot(cross(edge_in, edge_out), facing_normal), dot(edge_in, edge_out));

        // Of each triangle's three vertices, one sits at the joint and two on the arc
        int fan_tri = 2 * (segment - POLYLINE_SEGMENTS) + tri_vert / 3;
        int fan_vert = tri_vert % 3;
        float along = float(fan_tri + fan_vert - 1) / float(FAN_TRIANGLES);

        step = rotate_vector(edge_in, facing_normal, vec2(cos(along * sweep), sin(along * sweep)));
        // The corners reach out by this much, being a step out plus a shift along
        edge_dist = sqrt(1.0 + shift * shift) * 0.5 * width;
        dist_to_curve = fan_vert == 0 ? 0.0 : edge_dist + 0.5 * aaw;
    } else {
        step = step_to_corner(tangent, facing_normal, shift, draw_flat);
        edge_dist = 0.5 * width;
        dist_to_curve = corner.y * half_width;
    }

    half_width_to_aaw = edge_dist / aaw;
    dist_to_aaw = dist_to_curve / aaw;
    emit_gl_Position(point + dist_to_curve * step);
}
