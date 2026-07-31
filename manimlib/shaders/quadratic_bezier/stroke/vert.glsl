#version 330

uniform float anti_alias_width;
uniform float flat_stroke;
uniform float joint_type;
uniform float stroke_width_in_scene_units;
/*
The border around a fill is a stroke like any other, except that it takes its
color and width from the fill's fields rather than the stroke's, and that a width
of zero still draws a band just wide enough to anti-alias the fill's edge.
*/
uniform bool is_fill_border;

out vec4 color;
out float dist_to_aaw;
out float half_width_to_aaw;

// Codes for joint types
const int NO_JOINT = 0;
const int AUTO_JOINT = 1;
const int BEVEL_JOINT = 2;
const int MITER_JOINT = 3;

// When the cosine of the angle between
// two vectors is larger than this, we
// consider them aligned
const float COS_THRESHOLD = 0.999;
// Used to determine how many lines to break the curve into
const float POLYLINE_FACTOR = 100;
const int MAX_STEPS = 32;
const float MITER_COS_ANGLE_THRESHOLD = -0.8;
// Number of units spanned by a stroke_width of 1 in a default scale frame,
// so for instance a stroke_width of 100 comes out one unit thick
const float STROKE_WIDTH_CONVERSION = 0.01;

/*
A bezier sits in three consecutive records of the buffer, and is drawn as one
quad for each of the polyline segments it gets broken into. The vertex count per
curve has to match what VShaderWrapper draws.
*/
const int RECORDS_PER_CURVE = 3;
const int VERTS_PER_CURVE = 6 * (MAX_STEPS - 1);

// The two triangles of one segment's quad, as (which end of it, which side)
const vec2 CORNERS[6] = vec2[6](
    vec2(0, -1), vec2(0, 1), vec2(1, -1),
    vec2(1, -1), vec2(0, 1), vec2(1, 1)
);

#INSERT emit_gl_Position.glsl
#INSERT finalize_color.glsl
#INSERT read_data.glsl


vec3 point_on_quadratic(float t, vec3 c0, vec3 c1, vec3 c2){
    return c0 + c1 * t + c2 * t * t;
}


vec3 tangent_on_quadratic(float t, vec3 c1, vec3 c2){
    return c1 + 2 * c2 * t;
}


vec3 project(vec3 vect, vec3 unit_normal){
    /* Project the vector onto the plane perpendicular to a given unit normal */
    return vect - dot(vect, unit_normal) * unit_normal;
}


vec3 rotate_vector(vec3 vect, vec3 unit_normal, float angle){
    vec3 perp = cross(unit_normal, vect);
    return cos(angle) * vect + sin(angle) * perp;
}


vec3 step_to_corner(
    vec3 tangent,
    vec3 unit_normal,
    vec3 curve_normal,
    float joint_angle,
    bool inside_curve,
    bool draw_flat
){
    /*
    Step to the left of a curve.
    First a perpendicular direction is calculated, then it is adjusted
    so as to make a joint.
    */
    vec3 unit_tan = normalize(draw_flat ? tangent : project(tangent, unit_normal));

    // Step to stroke width bound should be perpendicular
    // both to the tangent and the normal direction
    vec3 step = normalize(cross(unit_normal, unit_tan));

    // For non-flat stroke, there can be glitches when the tangent direction
    // lines up very closely with the direction to the camera, treated here
    // as the unit normal. To avoid those, this smoothly transitions to a step
    // direction perpendicular to the true curve normal.
    if(joint_angle != 0){
        float alignment = abs(dot(normalize(tangent), unit_normal));
        float alignment_threshold = 0.97;  // This could maybe be chosen in a more principled way based on stroke width
        if (alignment > alignment_threshold) {
            vec3 perp = normalize(cross(curve_normal, tangent));
            step = mix(step, project(step, perp), smoothstep(alignment_threshold, 1.0, alignment));
        }
    }

    if (inside_curve || int(joint_type) == NO_JOINT) return step;

    float cos_angle = cos(joint_angle);
    float sin_angle = sin(joint_angle);

    if (abs(cos_angle) > COS_THRESHOLD) return step;

    // Below here, figure out the adjustment to bevel or miter a joint
    if (!draw_flat){
        // Figure out what joint product would be for everything projected onto
        // the plane perpendicular to the normal direction (which here would be to_camera)
        step = normalize(cross(unit_normal, unit_tan));  // Back to original step
        vec3 adj_tan = rotate_vector(tangent, curve_normal, joint_angle);
        adj_tan = project(adj_tan, unit_normal);
        cos_angle = dot(unit_tan, normalize(adj_tan));
        sin_angle = sqrt(1 - cos_angle * cos_angle) * sign(joint_angle) * sign(dot(unit_normal, curve_normal));
    }

    // If joint type is auto, it will bevel for cos(angle) > MITER_COS_ANGLE_THRESHOLD,
    // and smoothly transition to miter for those with sharper angles
    float miter_factor;
    if (joint_type == BEVEL_JOINT){
        miter_factor = 0.0;
    }else if (joint_type == MITER_JOINT){
        miter_factor = 1.0;
    }else {
        float mcat1 = MITER_COS_ANGLE_THRESHOLD;
        float mcat2 = mix(mcat1, -1.0, 0.5);
        miter_factor = smoothstep(mcat1, mcat2, cos_angle);
    }

    float shift = (cos_angle + mix(-1, 1, miter_factor)) / sin_angle;
    return step + shift * unit_tan;
}


void main(){
    int curve = gl_VertexID / VERTS_PER_CURVE;
    int within = gl_VertexID % VERTS_PER_CURVE;
    int segment = within / 6;
    vec2 corner = CORNERS[within % 6];
    int record = RECORDS_PER_CURVE * curve;

    int width_offset = is_fill_border ? DATA_OFFSET_fill_border_width : DATA_OFFSET_stroke_width;
    int color_offset = is_fill_border ? DATA_OFFSET_fill_rgba : DATA_OFFSET_stroke_rgba;

    vec3 controls[3] = vec3[3](
        read_vec3(record + 0, DATA_OFFSET_point),
        read_vec3(record + 1, DATA_OFFSET_point),
        read_vec3(record + 2, DATA_OFFSET_point)
    );
    float widths[3] = float[3](
        read_float(record + 0, width_offset),
        read_float(record + 1, width_offset),
        read_float(record + 2, width_offset)
    );
    vec4 colors[3] = vec4[3](
        read_vec4(record + 0, color_offset),
        read_vec4(record + 1, color_offset),
        read_vec4(record + 2, color_offset)
    );

    // Coefficients such that the quadratic bezier is c0 + c1 * t  + c2 * t^2
    vec3 c0 = controls[0];
    vec3 c1 = 2 * (controls[1] - controls[0]);
    vec3 c2 = controls[0] - 2 * controls[1] + controls[2];

    // Estimate how many line segments the curve should be divided into
    // based on the area of the triangle defined by these control points
    float area = 0.5 * length(cross(controls[1] - controls[0], controls[2] - controls[0]));
    int count = int(round(POLYLINE_FACTOR * sqrt(area) / get_frame_unit_size()));
    int n_steps = min(2 + count, MAX_STEPS);

    /*
    Nothing to draw for a curve marked as ended, by setting the handle after the
    first anchor equal to that anchor, nor for one with no width or no opacity,
    nor for segments past however many this curve was divided into. Collapsing
    all six corners onto one point leaves no area to rasterize.
    */
    bool blank = (controls[0] == controls[1]) || (segment >= n_steps - 1);
    if (!is_fill_border){
        blank = blank || (vec3(widths[0], widths[1], widths[2]) == vec3(0.0));
    }
    blank = blank || (vec3(colors[0].a, colors[1].a, colors[2].a) == vec3(0.0));
    if (blank){
        gl_Position = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }

    int index = segment + int(corner.x);
    float t = float(index) / float(n_steps - 1);

    // Point and tangent
    vec3 point = point_on_quadratic(t, c0, c1, c2);
    vec3 tangent = tangent_on_quadratic(t, c1, c2);

    // By default stroke width is measured relative to the frame, so putting it in
    // the units of the space being drawn means scaling by that space's frame
    // size, which keeps a given stroke width looking the same at any zoom level.
    // When it's measured relative to the scene instead, no such conversion is
    // needed, and zooming in makes the stroke look thicker.
    float width = STROKE_WIDTH_CONVERSION
        * mix(get_frame_unit_size(), 1.0, stroke_width_in_scene_units)
        * mix(widths[0], widths[2], t);
    vec4 joint_color = mix(colors[0], colors[2], t);

    // This prevents needless joint creation
    bool inside_curve = (index > 0 && index < n_steps - 1);

    // Use middle joint product for inner points, flip sign for first one's cross product component
    float joint_angle;
    if (index == 0){
        joint_angle = -read_float(record + 0, DATA_OFFSET_joint_angle);
    }
    else if (inside_curve){
        joint_angle = 0;
    }
    else {
        joint_angle = read_float(record + 2, DATA_OFFSET_joint_angle);
    }

    // Base points and unit normals are interleaved into one array, with the
    // former on even records and the latter on odd ones
    vec3 curve_normal = read_vec3(record + 1, DATA_OFFSET_base_normal);
    bool draw_flat = bool(flat_stroke) || bool(is_fixed_in_frame);
    vec3 unit_normal = draw_flat ? curve_normal : normalize(camera_position - point);

    color = finalize_color(joint_color, point, unit_normal);

    // Step from the point to a corner of the strip around the polyline
    vec3 step = step_to_corner(
        tangent, unit_normal, curve_normal, joint_angle, inside_curve, draw_flat
    );

    // anti_alias_width is measured in pixels. The frag shader receives a value
    // from -1 to 1, reflecting where in the stroke this corner is.
    float aaw = max(anti_alias_width * get_pixel_unit_size(), 1e-8);
    float dist_to_curve = corner.y * 0.5 * (width + aaw);
    half_width_to_aaw = 0.5 * width / aaw;
    dist_to_aaw = dist_to_curve / aaw;
    emit_gl_Position(point + dist_to_curve * step);
}
