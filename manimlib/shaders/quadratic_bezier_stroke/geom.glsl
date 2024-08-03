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

vec3 unit_normal = vec3(0.0, 0.0, 1.0);

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


void create_joint(
    vec4 joint_product,
    vec3 unit_tan,
    float buff,
    vec3 static_c0,
    out vec3 changing_c0,
    vec3 static_c1,
    out vec3 changing_c1
){
    float cos_angle = joint_product.w;
    if(abs(cos_angle) > COS_THRESHOLD || int(joint_type) == NO_JOINT){
        // No joint
        changing_c0 = static_c0;
        changing_c1 = static_c1;
        return;
    }

    float shift;
    float sin_angle = length(joint_product.xyz) * sign(joint_product.z);
    if(int(joint_type) == MITER_JOINT){
        shift = buff * (-1.0 - cos_angle) / sin_angle;
    }else{
        // For a Bevel joint
        shift = buff * (1.0 - cos_angle) / sin_angle;
    }
    changing_c0 = static_c0 - shift * unit_tan;
    changing_c1 = static_c1 + shift * unit_tan;
}


vec3 left_step(vec3 point, vec3 tangent, vec4 joint_product){
    /*
    Perpendicular vectors to the left of the curve
    */
    vec3 normal = get_joint_unit_normal(joint_product);
    unit_normal = normal;  // Set global unit normal
    if(normal.z < 0) normal *= -1;  // Choose the "outward" normal direction
    if(bool(flat_stroke)){
        return normalize(cross(normal, tangent));
    }else{
        return normalize(cross(camera_position - point, tangent));
    }
}


void emit_point_with_width(
    vec3 point,
    vec3 tangent,
    vec4 joint_product,
    float width,
    vec4 joint_color
){
    vec3 unit_tan = normalize(tangent);
    vec4 unit_jp = normalized_joint_product(joint_product);
    vec3 perp = 0.5 * width * left_step(point, unit_tan, unit_jp);

    vec3 left = point + perp;
    vec3 right = point - perp;
    create_joint(unit_jp, unit_tan, length(perp), left, left, right, right);

    color = finalize_color(joint_color, point, unit_normal);
    if (width == 0) scaled_anti_alias_width = -1.0;  // Signal to discard in frag
    else scaled_anti_alias_width = 2.0 * anti_alias_width * pixel_size / width;

    // Emit two corners
    // The frag shader will receive a value from -1 to 1,
    // reflecting where in the stroke that point is
    scaled_signed_dist_to_curve = -1.0;
    emit_gl_Position(left);
    EmitVertex();
    scaled_signed_dist_to_curve = +1.0;
    emit_gl_Position(right);
    EmitVertex();
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
        joint_products[i] = vec4(cross(v1, v2), dot(v1, v2));
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