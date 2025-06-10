#version 330

layout (triangles) in;
layout (triangle_strip, max_vertices = 64) out;  // Related to MAX_STEPS below

uniform float anti_alias_width;
uniform float flat_stroke;
uniform float pixel_size;
uniform float joint_type;
uniform float frame_scale;

in vec3 verts[3];

in float v_joint_angle[3];
in float v_stroke_width[3];
in vec4 v_color[3];
in vec3 v_unit_normal[3];

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

#INSERT emit_gl_Position.glsl
#INSERT finalize_color.glsl



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


vec3 step_to_corner(vec3 point, vec3 tangent, vec3 unit_normal, float joint_angle, bool inside_curve, bool draw_flat){
    /*
    Step the the left of a curve.
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
            vec3 perp = normalize(cross(v_unit_normal[1], tangent));
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
        vec3 adj_tan = rotate_vector(tangent, v_unit_normal[1], joint_angle);
        adj_tan = project(adj_tan, unit_normal);
        cos_angle = dot(unit_tan, normalize(adj_tan));
        sin_angle = sqrt(1 - cos_angle * cos_angle) * sign(joint_angle) * sign(dot(unit_normal, v_unit_normal[1]));
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


void emit_point_with_width(
    vec3 point,
    vec3 tangent,
    float joint_angle,
    float width,
    vec4 joint_color,
    bool inside_curve,
    bool draw_flat
){
    // Find unit normal
    vec3 unit_normal = draw_flat ? v_unit_normal[1] : normalize(camera_position - point);

    // Set styling
    color = finalize_color(joint_color, point, unit_normal);

    // Figure out the step from the point to the corners of the
    // triangle strip around the polyline
    vec3 step = step_to_corner(point, tangent, unit_normal, joint_angle, inside_curve, draw_flat);
    float aaw = max(anti_alias_width * pixel_size, 1e-8);

    // Emit two corners
    // The frag shader will receive a value from -1 to 1,
    // reflecting where in the stroke that point is
    for (int sign = -1; sign <= 1; sign += 2){
        float dist_to_curve = sign * 0.5 * (width + aaw);
        emit_gl_Position(point + dist_to_curve * step);
        half_width_to_aaw = 0.5 * width / aaw;
        dist_to_aaw = dist_to_curve / aaw;
        EmitVertex();
    }
}


void main() {
    // Curves are marked as ended when the handle after
    // the first anchor is set equal to that anchor
    if (verts[0] == verts[1]) return;

    // Check null stroke
    if (vec3(v_stroke_width[0], v_stroke_width[1], v_stroke_width[2]) == vec3(0.0, 0.0, 0.0)) return;
    if (vec3(v_color[0].a, v_color[1].a, v_color[2].a) == vec3(0.0, 0.0, 0.0)) return;

    bool draw_flat = bool(flat_stroke) || bool(is_fixed_in_frame);

    // Coefficients such that the quadratic bezier is c0 + c1 * t  + c2 * t^2
    vec3 c0 = verts[0];
    vec3 c1 = 2 * (verts[1] - verts[0]);
    vec3 c2 = verts[0] - 2 * verts[1] + verts[2];

    // Estimate how many line segment the curve should be divided into
    // based on the area of the triangle defined by these control points
    float area = 0.5 * length(cross(verts[1] - verts[0], verts[2] - verts[0]));
    int count = int(round(POLYLINE_FACTOR * sqrt(area) / frame_scale));
    int n_steps = min(2 + count, MAX_STEPS);

    // Emit vertex pairs aroudn subdivided points
    for (int i = 0; i < MAX_STEPS; i++){
        if (i >= n_steps) break;
        float t = float(i) / (n_steps - 1);

        // Point and tangent
        vec3 point = point_on_quadratic(t, c0, c1, c2);
        vec3 tangent = tangent_on_quadratic(t, c1, c2);

        // Style
        float stroke_width = mix(v_stroke_width[0], v_stroke_width[2], t);
        vec4 color = mix(v_color[0], v_color[2], t);

        // This is sent along to prevent needless joint creation
        bool inside_curve = (i > 0 && i < n_steps - 1);

        // Use middle joint product for inner points, flip sign for first one's cross product component
        float joint_angle;
        if (i == 0){
            joint_angle = -v_joint_angle[0];
        }
        else if (inside_curve){
            joint_angle = 0;
        }
        else {
            joint_angle = v_joint_angle[2];
        }

        emit_point_with_width(
            point, tangent, joint_angle,
            stroke_width, color,
            inside_curve, draw_flat
        );
    }
    EndPrimitive();
}