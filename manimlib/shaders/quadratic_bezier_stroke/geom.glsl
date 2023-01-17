#version 330

layout (triangles) in;
layout (triangle_strip, max_vertices = 6) out;

uniform float anti_alias_width;
uniform float flat_stroke;
uniform vec2 pixel_shape;
uniform float joint_type;

in vec3 verts[3];

in float v_joint_angle[3];
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

const float PI = 3.141592653;
const float ANGLE_THRESHOLD = 1e-3;


#INSERT get_gl_Position.glsl
#INSERT get_xy_to_uv.glsl
#INSERT finalize_color.glsl


void create_joint(
    float angle,
    vec3 unit_tan,
    float buff,
    vec3 static_c0,
    out vec3 changing_c0,
    vec3 static_c1,
    out vec3 changing_c1
){
    float shift;
    // if(abs(angle) < ANGLE_THRESHOLD || abs(angle) > 0.99 * PI || int(joint_type) == NO_JOINT){
    if(abs(angle) < ANGLE_THRESHOLD || int(joint_type) == NO_JOINT){
        // No joint
        shift = 0;
    }else if(int(joint_type) == MITER_JOINT){
        shift = buff * (-1.0 - cos(angle)) / sin(angle);
    }else{
        // For a Bevel joint
        shift = buff * (1.0 - cos(angle)) / sin(angle);
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
    float stroke_width0,
    float stroke_width2,
    // Unit normal to the whole curve
    vec3 normal,
    // Anti-alias width
    float aaw,
    float angle_from_prev,
    float angle_to_next,
    out vec3 corners[6]
){

    float buff0 = 0.5 * stroke_width0 + aaw;
    float buff2 = 0.5 * stroke_width2 + aaw;

    // Add correction for sharp angles to prevent weird bevel effects (Needed?)
    float thresh = 5 * PI / 6;
    if(angle_from_prev > thresh) buff0 *= 2 * sin(angle_from_prev);
    if(angle_to_next > thresh) buff2 *= 2 * sin(angle_to_next);

    // Perpendicular vectors to the left of the curve
    vec3 p0_perp = buff0 * normalize(cross(normal, v01));
    vec3 p2_perp = buff2 * normalize(cross(normal, v12));
    vec3 p1_perp = 0.5 * (p0_perp + p2_perp);

    // The order of corners should be for a triangle_strip.
    vec3 c0 = p0 + p0_perp;
    vec3 c1 = p0 - p0_perp;
    vec3 c2 = p1 + p1_perp;
    vec3 c3 = p1 - p1_perp;
    vec3 c4 = p2 + p2_perp;
    vec3 c5 = p2 - p2_perp;
    float orientation = dot(normal, cross(v01, v12));
    // Move the inner middle control point to make
    // room for the curve
    if(orientation > 0.0)      c2 = 0.5 * (c0 + c4);  
    else if(orientation < 0.0) c3 = 0.5 * (c1 + c5);

    // Account for previous and next control points
    create_joint(angle_from_prev, v01, buff0, c1, c1, c0, c0);
    create_joint(angle_to_next, -v12, buff2, c5, c5, c4, c4);

    corners = vec3[6](c0, c1, c2, c3, c4, c5);
}


void main() {
    // We use the triangle strip primative, but
    // actually only need every other strip element
    if (int(v_vert_index[0]) % 2 == 1) return;

    // Curves are marked as eneded when the handle after
    // the first anchor is set equal to that anchor
    if (verts[0] == verts[1]) return;

    // TODO, track true unit normal globally (probably as a uniform)
    vec3 unit_normal = vec3(0.0, 0.0, 1.0);
    if(bool(flat_stroke)){
        unit_normal = camera_rotation * vec3(0.0, 0.0, 1.0);
    }

    vec3 p0 = verts[0];
    vec3 p1 = verts[1];
    vec3 p2 = verts[2];
    vec3 v01 = normalize(p1 - p0);
    vec3 v12 = normalize(p2 - p1);

    float angle = acos(clamp(dot(v01, v12), -1, 1));
    is_linear = float(abs(angle) < ANGLE_THRESHOLD);

    // If the curve is flat, put the middle control in the midpoint
    if (bool(is_linear)) p1 = 0.5 * (p0 + p2);

    // We want to change the coordinates to a space where the curve
    // coincides with y = x^2, between some values x0 and x2. Or, in
    // the case of a linear curve (bezier degree 1), just put it on
    // the segment from (0, 0) to (1, 0)
    mat3 xy_to_uv = get_xy_to_uv(p0.xy, p1.xy, p2.xy, is_linear, is_linear);

    float uv_scale_factor = length(xy_to_uv[0].xy);
    float scaled_aaw = anti_alias_width * (frame_shape.y / pixel_shape.y);
    uv_anti_alias_width = uv_scale_factor * scaled_aaw;

    vec3 corners[6];
    get_corners(
        p0, p1, p2, v01, v12,
        v_stroke_width[0],
        v_stroke_width[2],
        unit_normal,
        scaled_aaw,
        v_joint_angle[0],
        v_joint_angle[2],
        corners
    );

    // Emit each corner
    for(int i = 0; i < 6; i++){
        int vert_index = i / 2;
        uv_coords = (xy_to_uv * vec3(corners[i].xy, 1)).xy;
        uv_stroke_width = uv_scale_factor * v_stroke_width[vert_index];
        color = finalize_color(
            v_color[vert_index],
            corners[i],
            unit_normal
        );
        gl_Position = get_gl_Position(position_point_into_frame(corners[i]));
        EmitVertex();
    }
    EndPrimitive();
}