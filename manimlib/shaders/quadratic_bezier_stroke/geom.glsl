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
out float scaled_anti_alias_width;
out float scaled_signed_dist_to_curve;

// Codes for joint types
const int NO_JOINT = 0;
const int AUTO_JOINT = 1;
const int BEVEL_JOINT = 2;
const int MITER_JOINT = 3;

// When the cosine of the angle between
// two vectors is larger than this, we
// consider them aligned
const float COS_THRESHOLD = 0.99;
// Used to determine how many lines to break the curve into
const float POLYLINE_FACTOR = 30;
const int MAX_STEPS = 32;
const float MITER_LIMIT = 3.0;

#INSERT emit_gl_Position.glsl
#INSERT finalize_color.glsl


vec3 get_joint_unit_normal(vec4 joint_product){
    vec3 result = (joint_product.w < COS_THRESHOLD) ?
        joint_product.xyz : v_joint_product[1].xyz;
    float norm = length(result);
    return (norm > 1e-5) ? result / norm : vec3(0.0, 0.0, 1.0);
}


vec4 normalized_joint_product(vec4 joint_product){
    float norm = length(joint_product);
    return (norm > 1e-10) ? joint_product / norm : vec4(0.0, 0.0, 0.0, 1.0);
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


vec3 project(vec3 vect, vec3 normal){
    /* Project the vector onto the plane perpendicular to a given unit normal */
    return vect - dot(vect, normal) * normal;
}

vec3 inverse_joint_product(vec3 vect, vec4 joint_product){
    /* 
    If joint_product represents vec4(cross(v1, v2), dot(v1, v2)), 
    then given v1, this function recovers v2
    */
    float dp = joint_product.w;
    if (abs(dp) > COS_THRESHOLD) return vect;
    vec3 cp = joint_product.xyz;
    vec3 perp = cross(cp, vect);
    float a = dp / dot(vect, vect);
    float b = length(cp) / length(cross(vect, perp));
    return a * vect + b * perp;
}


vec3 step_to_corner(vec3 point, vec3 unit_tan, vec3 unit_normal, vec4 joint_product){
    /*
    Step the the left of a curve.
    First a perpendicular direction is calculated, then it is adjusted
    so as to make a joint.
    */
    vec3 step = normalize(cross(unit_normal, unit_tan));

    // Check if an adjustment is needed
    float cos_angle = joint_product.w;
    if(abs(cos_angle) > 1 - 1e-5 || int(joint_type) == NO_JOINT){
        return step;
    }

    // Adjust based on the joint
    float sin_angle = length(joint_product.xyz) * sign(joint_product.z);
    float shift = (int(joint_type) == MITER_JOINT) ?
        (cos_angle + 1.0) / sin_angle :
        (cos_angle - 1.0) / sin_angle;

    // return step + shift * unit_tan;
    vec3 result = step + shift * unit_tan;
    if (length(result) > MITER_LIMIT){
        result = MITER_LIMIT * normalize(result);
    }
    return result;
}


void emit_point_with_width(
    vec3 point,
    vec3 tangent,
    vec4 joint_product,
    float width,
    vec4 joint_color
){
    // Normalize relevant vectors
    vec3 unit_tan;
    vec4 unit_jp;
    vec3 unit_normal;
    if(bool(flat_stroke)){
        unit_tan = normalize(tangent);
        unit_jp = normalized_joint_product(joint_product);
        unit_normal = get_joint_unit_normal(joint_product);
    }else{
        unit_normal = normalize(camera_position - point);
        unit_tan = normalize(project(tangent, unit_normal));
        vec3 adj_tan = inverse_joint_product(tangent, joint_product);
        adj_tan = project(adj_tan, unit_normal);
        unit_jp = normalized_joint_product(get_joint_product(unit_tan, adj_tan));
    }
    if(unit_normal.z < 0) unit_normal *= -1;  // Choose the "outward" normal direction

    // Figure out the step from the point to the corners of the
    // triangle strip around the polyline
    vec3 step = step_to_corner(point, unit_tan, unit_normal, unit_jp);

    // Set styling
    color = finalize_color(joint_color, point, unit_normal);
    if (width == 0) scaled_anti_alias_width = -1.0;  // Signal to discard in frag
    else scaled_anti_alias_width = 2.0 * anti_alias_width * pixel_size / width;

    // Emit two corners
    // The frag shader will receive a value from -1 to 1,
    // reflecting where in the stroke that point is
    for (int sign = -1; sign <= 1; sign += 2){
        scaled_signed_dist_to_curve = sign;
        emit_gl_Position(point + 0.5 * width * sign * step);
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

    // Compute points along the curve
    vec3 points[MAX_STEPS];
    for (int i = 0; i < MAX_STEPS; i++){
        if (i >= n_steps) break;
        float t = float(i) / (n_steps - 1);
        points[i] = point_on_quadratic(t, c0, c1, c2);
    }

    // Compute joint products
    vec4 joint_products[MAX_STEPS];
    joint_products[0] = v_joint_product[0];
    joint_products[0].xyz *= -1;
    joint_products[n_steps - 1] = v_joint_product[2];
    for (int i = 1; i < MAX_STEPS; i++){
        if (i >= n_steps - 1) break;
        vec3 v1 = points[i] - points[i - 1];
        vec3 v2 = points[i + 1] - points[i];
        joint_products[i] = get_joint_product(v1, v2);
    }

    // Emit vertex pairs aroudn subdivided points
    for (int i = 0; i < MAX_STEPS; i++){
        if (i >= n_steps) break;
        float t = float(i) / (n_steps - 1);
        emit_point_with_width(
            points[i],
            tangent_on_quadratic(t, c1, c2),
            joint_products[i],
            mix(v_stroke_width[0], v_stroke_width[2], t),
            mix(v_color[0], v_color[2], t)
        );
    }
    EndPrimitive();
}