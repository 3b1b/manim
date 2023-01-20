#version 330

layout (triangles) in;
layout (triangle_strip, max_vertices = 6) out;

uniform float anti_alias_width;
uniform float flat_stroke;
uniform float pixel_size;
uniform float joint_type;

in vec3 verts[3];

in vec4 v_joint_product[3];
in float v_stroke_width[3];
in vec4 v_color[3];
in float v_vert_index[3];

out vec4 color;
out float uv_stroke_width;
out float uv_anti_alias_width;

out float is_linear;

out vec2 uv_coords;

// Codes for joint types
const int NO_JOINT = 0;
const int AUTO_JOINT = 1;
const int BEVEL_JOINT = 2;
const int MITER_JOINT = 3;

// When the cosine of the angle between
// two vectors is larger than this, we
// consider them aligned
const float COS_THRESHOLD = 0.999;

vec3 unit_normal = vec3(0.0, 0.0, 1.0);

#INSERT get_gl_Position.glsl
#INSERT get_xyz_to_uv.glsl
#INSERT finalize_color.glsl


vec3 get_joint_unit_normal(vec4 joint_product){
    vec3 result;
    if(joint_product.w < COS_THRESHOLD){
        result = joint_product.xyz;
    }else{
        result = v_joint_product[1].xyz;
    }
    float norm = length(result);
    return (norm > 1e-5) ? result / norm : vec3(0.0, 0.0, 1.0);
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

// This function is responsible for finding the corners of
// a bounding region around the bezier curve, which can be
// emitted as a triangle fan, with vertices vaguely close
// to control points so that the passage of vert data to
// frag shaders is most natural.
void get_corners(
    // Control points for a bezier curve
    vec3 p0,
    vec3 p1,
    vec3 p2,
    // Unit tangent vectors at p0 and p2
    vec3 v01,
    vec3 v12,
    // Anti-alias width
    float aaw,
    out vec3 corners[6]
){

    float buff0 = 0.5 * v_stroke_width[0] + aaw;
    float buff2 = 0.5 * v_stroke_width[2] + aaw;

    // Add correction for sharp angles to prevent weird bevel effects
    if(v_joint_product[0].w < -0.75) buff0 *= 4 * (v_joint_product[0].w + 1.0);
    if(v_joint_product[2].w < -0.75) buff2 *= 4 * (v_joint_product[2].w + 1.0);

    // Unit normal and joint angles
    vec3 normal0 = get_joint_unit_normal(v_joint_product[0]);
    vec3 normal2 = get_joint_unit_normal(v_joint_product[2]);
    // Set global unit normal
    unit_normal = normal0;

    // Choose the "outward" normal direction
    normal0 *= sign(normal0.z);
    normal2 *= sign(normal2.z);

    vec3 p0_perp;
    vec3 p2_perp;
    if(bool(flat_stroke)){
        // Perpendicular vectors to the left of the curve
        p0_perp = buff0 * normalize(cross(normal0, v01));
        p2_perp = buff2 * normalize(cross(normal2, v12));
    }else{
        // p0_perp = buff0 * normal0;
        // p2_perp = buff2 * normal2;
        p0_perp = buff0 * normalize(cross(camera_position - p0, v01));
        p2_perp = buff2 * normalize(cross(camera_position - p2, v12));
    }
    vec3 p1_perp = 0.5 * (p0_perp + p2_perp);

    // The order of corners should be for a triangle_strip.
    vec3 c0 = p0 + p0_perp;
    vec3 c1 = p0 - p0_perp;
    vec3 c2 = p1 + p1_perp;
    vec3 c3 = p1 - p1_perp;
    vec3 c4 = p2 + p2_perp;
    vec3 c5 = p2 - p2_perp;
    // Move the inner middle control point to make
    // room for the curve
    float orientation = dot(normal0, v_joint_product[1].xyz);
    if(orientation >= 0.0)     c2 = 0.5 * (c0 + c4);
    else if(orientation < 0.0) c3 = 0.5 * (c1 + c5);

    // Account for previous and next control points
    if(bool(flat_stroke)){
        create_joint(v_joint_product[0], v01, buff0, c1, c1, c0, c0);
        create_joint(v_joint_product[2], -v12, buff2, c5, c5, c4, c4);
    }

    corners = vec3[6](c0, c1, c2, c3, c4, c5);
}

void main() {
    // We use the triangle strip primative, but
    // actually only need every other strip element
    if (int(v_vert_index[0]) % 2 == 1) return;

    // Curves are marked as eneded when the handle after
    // the first anchor is set equal to that anchor
    if (verts[0] == verts[1]) return;

    vec3 p0 = verts[0];
    vec3 p1 = verts[1];
    vec3 p2 = verts[2];
    vec3 v01 = normalize(p1 - p0);
    vec3 v12 = normalize(p2 - p1);

    float cos_angle = v_joint_product[1].w;
    is_linear = float(cos_angle > COS_THRESHOLD);

    // We want to change the coordinates to a space where the curve
    // coincides with y = x^2, between some values x0 and x2. Or, in
    // the case of a linear curve just put it on the x-axis
    mat4 xyz_to_uv;
    float uv_scale_factor;
    if(!bool(is_linear)){
        bool too_steep;
        xyz_to_uv = get_xyz_to_uv(p0, p1, p2, 2.0, too_steep);
        if(too_steep) is_linear = 1.0;
        uv_scale_factor = length(xyz_to_uv[0].xyz);
    }

    float scaled_aaw = anti_alias_width * pixel_size;
    vec3 corners[6];
    get_corners(p0, p1, p2, v01, v12, scaled_aaw, corners);

    // Emit each corner
    for(int i = 0; i < 6; i++){
        float stroke_width = v_stroke_width[i / 2];

        if(bool(is_linear)){
            float sign = vec2(-1, 1)[i % 2];
            // In this case, we only really care about
            // the v coordinate
            uv_coords = vec2(0, sign * (0.5 * stroke_width + scaled_aaw));
            uv_anti_alias_width = scaled_aaw;
            uv_stroke_width = stroke_width;
        }else{
            uv_coords = (xyz_to_uv * vec4(corners[i], 1.0)).xy;
            uv_stroke_width = uv_scale_factor * stroke_width;
            uv_anti_alias_width = uv_scale_factor * scaled_aaw;
        }

        color = finalize_color(v_color[i / 2], corners[i], unit_normal);
        gl_Position = get_gl_Position(corners[i]);
        EmitVertex();
    }
    EndPrimitive();
}