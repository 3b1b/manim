#version 330

layout (triangles) in;
layout (triangle_strip, max_vertices = 32) out;  // Related to MAX_STEPS below

uniform float anti_alias_width;
uniform float flat_stroke;
uniform float pixel_size;
uniform float joint_type;

in vec3 verts[3];

in vec4 v_joint_product[3];
in float v_stroke_width[3];
in vec4 v_color[3];

out vec4 color;
out float uv_stroke_width;
out float uv_anti_alias_width;
out float signed_dist_to_curve;

// Codes for joint types
const int NO_JOINT = 0;
const int AUTO_JOINT = 1;
const int BEVEL_JOINT = 2;
const int MITER_JOINT = 3;

// When the cosine of the angle between
// two vectors is larger than this, we
// consider them aligned
const float COS_THRESHOLD = 0.999;
const int MAX_STEPS = 16;

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


vec3 point_on_curve(float t){
    return verts[0] + 2 * (verts[1] - verts[0]) * t + (verts[0] - 2 * verts[1] + verts[2]) * t * t;
}


vec3 tangent_on_curve(float t){
    return 2 * (verts[1] + -verts[0]) + 2 * (verts[0] - 2 * verts[1] + verts[2]) * t;
}


void map_to_basic(out float x0, out float x2, out float scale_factor){
    /* Find the coordinates and scale factor such that the bezier curve
    defined by verts[] is congruent to a section of the parabola y = x^2
    between x0 and x2, with scale_factor
    */
}


void compute_subdivision(out int n_steps, out float subdivision[MAX_STEPS]){
    /*
    Based on https://raphlinus.github.io/graphics/curves/2019/12/23/flatten-quadbez.html
    */
    float x0;
    float x2;
    float scale_factor;
    map_to_basic(x0, x2, scale_factor);

    if (normalized_joint_product(v_joint_product[1]).w > COS_THRESHOLD){
        // Linear
        n_steps = 2;
    }else{
        n_steps = MAX_STEPS;  // TODO
    }

    for(int i = 0; i < MAX_STEPS; i++){
        if (i >= n_steps) break;
        subdivision[i] = float(i) / (n_steps - 1);
    }
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


vec3 get_perp(vec3 point, vec3 tangent, vec4 joint_product){
    /*
    Perpendicular vectors to the left of the curve
    */
    // Add correction for sharp angles to prevent weird bevel effects
    float mult = 1.0;
    if(joint_product.w < -0.75) mult *= 4 * (joint_product.w + 1.0);
    vec3 normal = get_joint_unit_normal(joint_product);
    // Set global unit normal
    unit_normal = normal;
    // Choose the "outward" normal direction
    if(normal.z < 0) normal *= -1;
    if(bool(flat_stroke)){
        return mult * normalize(cross(normal, tangent));
    }else{
        return mult * normalize(cross(camera_position - point, tangent));
    }
}


void emit_point_with_width(
    vec3 point,
    vec3 tangent,
    vec4 joint_product,
    float width,
    vec4 joint_color,
    float aaw
){
    vec3 unit_tan = normalize(tangent);
    vec4 njp = normalized_joint_product(joint_product);
    float buff = 0.5 * width + aaw;
    vec3 perp = buff * get_perp(point, unit_tan, njp);

    vec3 corners[2] = vec3[2](point + perp, point - perp);  
    create_joint(
        njp, unit_tan, length(perp),
        corners[0], corners[0],
        corners[1], corners[1]
    );

    color = finalize_color(joint_color, point, unit_normal);
    uv_anti_alias_width = aaw;
    uv_stroke_width = width;

    // Emit two corners
    for(int i = 0; i < 2; i++){
        float sign = i % 2 == 0 ? -1 : 1;
        signed_dist_to_curve = sign * buff;
        emit_gl_Position(corners[i]);
        EmitVertex();
    }
}

void main() {
    // Curves are marked as ended when the handle after
    // the first anchor is set equal to that anchor
    if (verts[0] == verts[1]) return;

    // Compute subdivision
    int n_steps;
    float subdivision[MAX_STEPS];
    compute_subdivision(n_steps, subdivision);

    // Compute joint products
    vec3 points[MAX_STEPS];
    vec4 joint_products[MAX_STEPS];
    for (int i = 0; i < MAX_STEPS; i++){
        if (i >= n_steps) break;
        points[i] = point_on_curve(subdivision[i]);
    }
    joint_products[0] = v_joint_product[0];
    joint_products[0].xyz *= -1;
    joint_products[n_steps - 1] = v_joint_product[2];
    for (int i = 1; i < MAX_STEPS; i++){
        if (i >= n_steps - 1) break;
        vec3 v1 = points[i] - points[i - 1];
        vec3 v2 = points[i + 1] - points[i];
        joint_products[i].xyz = cross(v1, v2);
        joint_products[i].w = dot(v1, v2);
    }

    // Emit vertex pairs aroudn subdivided points
    float scaled_aaw = anti_alias_width * pixel_size;
    for (int i = 0; i < MAX_STEPS; i++){
        if (i >= n_steps) break;
        float t = subdivision[i];
        emit_point_with_width(
            points[i],
            tangent_on_curve(t),
            joint_products[i],
            mix(v_stroke_width[0], v_stroke_width[2], t),
            mix(v_color[0], v_color[2], t),
            scaled_aaw
        );
    }
    EndPrimitive();
}