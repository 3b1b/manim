#version 330

layout (triangles) in;
layout (triangle_strip, max_vertices = 64) out;  // Related to MAX_STEPS below

uniform float anti_alias_width;
uniform float flat_stroke;
uniform float pixel_size;
uniform float joint_type;
uniform float frame_scale;

in vec3 verts[3];

in vec4 v_joint_product[3];
in float v_stroke_width[3];
in vec4 v_color[3];

out vec4 color;
out float dist_to_curve;
out float half_stroke_width;
out float half_anti_alias_width;

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


vec3 get_joint_unit_normal(vec4 joint_product){
    float tol = 1e-8;
    if (length(joint_product.xyz) > tol){
        return normalize(joint_product.xyz);
    }
    if (length(v_joint_product[1].xyz) > tol){
        return normalize(v_joint_product[1].xyz);
    }
    return vec3(0.0, 0.0, 1.0);
}


vec4 unit_joint_product(vec4 joint_product){
    float tol = 1e-8;
    float norm = length(joint_product);
    return (norm < tol) ? vec4(0.0, 0.0, 0.0, 1.0) : joint_product / norm;
}


vec3 point_on_quadratic(float t, vec3 c0, vec3 c1, vec3 c2){
    return c0 + c1 * t + c2 * t * t;
}


vec3 tangent_on_quadratic(float t, vec3 c1, vec3 c2){
    return c1 + 2 * c2 * t;
}


vec4 get_joint_product(vec3 v1, vec3 v2){
    return vec4(cross(v1, v2), dot(v1, v2));
}


vec3 project(vec3 vect, vec3 unit_normal){
    /* Project the vector onto the plane perpendicular to a given unit normal */
    return vect - dot(vect, unit_normal) * unit_normal;
}

vec3 inverse_vector_product(vec3 vect, vec3 cross_product, float dot_product){
    /* 
    Suppose cross(v1, v2) = cross_product and dot(v1, v2) = dot_product.
    Given v1, this function return v2.
    */
    return (vect * dot_product - cross(vect, cross_product)) / dot(vect, vect);
}


vec3 step_to_corner(vec3 point, vec3 tangent, vec3 unit_normal, vec4 joint_product, bool inside_curve){
    /*
    Step the the left of a curve.
    First a perpendicular direction is calculated, then it is adjusted
    so as to make a joint.
    */
    vec3 unit_tan = normalize(flat_stroke == 0.0 ? project(tangent, unit_normal) : tangent);

    // Step to stroke width bound should be perpendicular
    // both to the tangent and the normal direction
    vec3 step = normalize(cross(unit_normal, unit_tan));

    // For non-flat stroke, there can be glitches when the tangent direction
    // lines up very closely with the direction to the camera, treated here
    // as the unit normal. To avoid those, this smoothly transitions to a step
    // direction perpendicular to the true curve normal.
    float alignment = abs(dot(normalize(tangent), unit_normal));
    float alignment_threshold = 0.97;  // This could maybe be chosen in a more principled way based on stroke width
    if (alignment > alignment_threshold) {
        vec3 perp = normalize(cross(get_joint_unit_normal(joint_product), tangent));
        step = mix(step, project(step, perp), smoothstep(alignment_threshold, 1.0, alignment));
    }

    if (inside_curve || int(joint_type) == NO_JOINT) return step;

    vec4 unit_jp = unit_joint_product(joint_product);
    float cos_angle = unit_jp.w;

    if (cos_angle > COS_THRESHOLD) return step;

    // Below here, figure out the adjustment to bevel or miter a joint
    if (flat_stroke == 0){
        // Figure out what joint product would be for everything projected onto
        // the plane perpendicular to the normal direction (which here would be to_camera)
        step = normalize(cross(unit_normal, unit_tan));  // Back to original step
        vec3 adj_tan = inverse_vector_product(tangent, unit_jp.xyz, unit_jp.w);
        adj_tan = project(adj_tan, unit_normal);
        vec4 flat_jp = get_joint_product(unit_tan, adj_tan);
        cos_angle = unit_joint_product(flat_jp).w;
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
        float mcat2 = 0.5 * (mcat1 - 1.0);
        miter_factor = smoothstep(mcat1, mcat2, cos_angle);
    }

    float sin_angle = sqrt(1 - cos_angle * cos_angle) * sign(dot(joint_product.xyz, unit_normal));
    float shift = (cos_angle + mix(-1, 1, miter_factor)) / sin_angle;

    return step + shift * unit_tan;
}


void emit_point_with_width(
    vec3 point,
    vec3 tangent,
    vec4 joint_product,
    float width,
    vec4 joint_color,
    bool inside_curve
){
    // Find unit normal
    vec3 to_camera = camera_position - point;
    vec3 unit_normal;
    if (flat_stroke == 0.0){
        unit_normal = normalize(to_camera);
    }else{
        unit_normal = get_joint_unit_normal(joint_product);
        unit_normal *= sign(dot(unit_normal, to_camera));  // Choose the "outward" normal direction
    }

    // Set styling
    color = finalize_color(joint_color, point, unit_normal);
    half_anti_alias_width = 0.5 * anti_alias_width * pixel_size;
    half_stroke_width = 0.5 * width;

    // Figure out the step from the point to the corners of the
    // triangle strip around the polyline
    vec3 step = step_to_corner(point, tangent, unit_normal, joint_product, inside_curve);

    // Emit two corners
    // The frag shader will receive a value from -1 to 1,
    // reflecting where in the stroke that point is
    for (int sign = -1; sign <= 1; sign += 2){
        dist_to_curve = sign * (half_stroke_width + half_anti_alias_width);
        emit_gl_Position(point + dist_to_curve * step);
        EmitVertex();
    }
}


void main() {
    // Curves are marked as ended when the handle after
    // the first anchor is set equal to that anchor
    if (verts[0] == verts[1]) return;

    // Coefficients such that the quadratic bezier is c0 + c1 * t  + c2 * t^2
    vec3 c0 = verts[0];
    vec3 c1 = 2 * (verts[1] - verts[0]);
    vec3 c2 = verts[0] - 2 * verts[1] + verts[2];

    // Estimate how many line segment the curve should be divided into
    // based on the area of the triangle defined by these control points
    float area = 0.5 * length(v_joint_product[1].xzy);
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
        vec4 joint_product;
        if (i == 0)            joint_product = v_joint_product[0] * vec4(-1, -1, -1, 1);
        else if (inside_curve) joint_product = v_joint_product[1];
        else                   joint_product = v_joint_product[2];

        emit_point_with_width(
            point, tangent, joint_product,
            stroke_width, color,
            inside_curve
        );
    }
    EndPrimitive();
}