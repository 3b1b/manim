#version 330

layout (triangles) in;
layout (triangle_strip, max_vertices = 5) out;

// Needed for get_gl_Position
uniform vec2 frame_shape;
uniform vec2 pixel_shape;
uniform float focal_distance;
uniform float is_fixed_in_frame;

uniform float anti_alias_width;
uniform float flat_stroke;
uniform mat3 camera_rotation;

//Needed for lighting
uniform vec3 light_source_position;
uniform vec3 camera_position;
uniform float joint_type;
uniform float reflectiveness;
uniform float gloss;
uniform float shadow;

in vec3 verts[3];

in float v_joint_angle[3];
in float v_stroke_width[3];
in vec4 v_color[3];

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


#INSERT get_xy_to_uv.glsl
#INSERT get_gl_Position.glsl
#INSERT get_unit_normal.glsl
#INSERT finalize_color.glsl
#INSERT rotate.glsl


float angle_between(vec2 v1, vec2 v2){
    float abs_angle = acos(clamp(dot(normalize(v1), normalize(v2)), -1.0, 1.0));
    float sgn = sign(cross2d(v1, v2));
    return sgn * abs_angle;
}


void create_joint(float angle, vec2 unit_tan, float buff,
                  vec2 static_c0, out vec2 changing_c0,
                  vec2 static_c1, out vec2 changing_c1){
    float shift;
    if(abs(angle) < ANGLE_THRESHOLD || abs(angle) > 0.99 * PI || int(joint_type) == NO_JOINT){
        // No joint
        shift = 0;
    // }else if(int(joint_type) == MITER_JOINT || (int(joint_type) == AUTO_JOINT && abs(angle) > 0.95 * PI)){
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
// emitted as a triangle fan
int get_corners(
    vec2 controls[3],
    float stroke_widths[3],
    float aaw,  // Anti-alias width
    float angle_from_prev,
    float angle_to_next,
    out vec2 corners[5]
){
    vec2 p0 = controls[0];
    vec2 p1 = controls[1];
    vec2 p2 = controls[2];

    // Unit vectors for directions between control points
    vec2 v01 = normalize(p1 - p0);
    vec2 v12 = normalize(p2 - p1);

    float cross_prod = cross2d(v01, v12);
    float sgn = (cross_prod >= 0.0 || bool(is_linear)) ? 1.0 : -1.0;
    vec2 p0_perp = sgn * vec2(-v01.y, v01.x);  // Pointing to the inside of the curve from p0
    vec2 p2_perp = sgn * vec2(-v12.y, v12.x);  // Pointing to the inside of the curve from p2

    // This is to prevent weird bevel artifacts for sharp angles
    if(abs(angle_from_prev) > 0.5 * PI){
        stroke_widths[0] *= sin(angle_from_prev);
        stroke_widths[1] = 0.5 * (stroke_widths[0] + stroke_widths[2]);
    }
    if(abs(angle_to_next) > 0.5 * PI){
        stroke_widths[2] *= sin(angle_to_next);
        stroke_widths[1] = 0.5 * (stroke_widths[0] + stroke_widths[2]);
    }

    float buff0 = 0.5 * stroke_widths[0] + aaw;
    float buff2 = 0.5 * stroke_widths[2] + aaw;

    vec2 c0 = p0 - buff0 * p0_perp;
    vec2 c1 = p0 + buff0 * p0_perp;
    vec2 c2 = p2 + buff2 * p2_perp;
    vec2 c3 = p2 - buff2 * p2_perp;

    // Account for previous and next control points
    create_joint(angle_from_prev, v01, buff0, c0, c0, c1, c1);
    create_joint(angle_to_next, -v12, buff2, c3, c3, c2, c2);

    // Linear case is the simplest
    if(bool(is_linear)){
        // The order of corners should be for a triangle_strip.  Last entry is a dummy
        corners = vec2[5](c0, c1, c3, c2, vec2(0.0));
        return 4;
    }
    // Otherwise, form a pentagon around the curve
    corners = vec2[5](c0, c1, p1, c2, c3);
    corners[2] -= buff0 * p0_perp + buff2 * p2_perp;
    return 5;
}


void main() {
    if (distance(verts[0], verts[1]) == 0 || distance(verts[1], verts[2]) == 0) return;

    vec3 unit_normal = camera_rotation * vec3(0.0, 0.0, 1.0); // TODO, track true unit normal globally

    float scaled_strokes[3];
    for(int i = 0; i < 3; i++){
        scaled_strokes[i] = v_stroke_width[i];
        if(bool(flat_stroke)){
            vec3 to_cam = normalize(vec3(0.0, 0.0, focal_distance) - verts[i]);
            scaled_strokes[i] *= abs(dot(unit_normal, to_cam));
        }
    }

    // Set joint information, potentially recomputing based on perspective
    float angle_from_prev = v_joint_angle[0];
    float angle_to_next = v_joint_angle[2];

    if(angle_from_prev > 0.0 && unit_normal != vec3(0.0, 0.0, 1.0)){
        vec3 v01 = verts[1] - verts[0];
        vec3 from_prev = rotate(v01, angle_from_prev, unit_normal);
        angle_from_prev = angle_between(from_prev.xy, v01.xy);
    }
    if(angle_to_next > 0.0 && unit_normal != vec3(0.0, 0.0, 1.0)){
        vec3 v12 = verts[2] - verts[1];
        vec3 to_next = rotate(v12, -angle_to_next, unit_normal);
        angle_to_next = angle_between(v12.xy, to_next.xy);
    }

    // Control points are projected to the xy plane before drawing, which in turn
    // gets tranlated to a uv plane.  The z-coordinate information will be remembered
    // by what's sent out to gl_Position, and by how it affects the lighting and stroke width
    vec2 flat_verts[3] = vec2[3](verts[0].xy, verts[1].xy, verts[2].xy);

    // If the curve is flat, put the middle control in the midpoint
    is_linear = float(abs(v_joint_angle[1]) < ANGLE_THRESHOLD);
    if (bool(is_linear)){
        flat_verts[1] = 0.5 * (flat_verts[0] + flat_verts[2]);
    }

    // We want to change the coordinates to a space where the curve
    // coincides with y = x^2, between some values x0 and x2. Or, in
    // the case of a linear curve (bezier degree 1), just put it on
    // the segment from (0, 0) to (1, 0)
    mat3 xy_to_uv = get_xy_to_uv(flat_verts, is_linear, is_linear);

    float uv_scale_factor = length(xy_to_uv[0].xy);
    float scaled_aaw = anti_alias_width * (frame_shape.y / pixel_shape.y);
    uv_anti_alias_width = uv_scale_factor * scaled_aaw;

    // Corners of a bounding region around curve
    vec2 corners[5];
    int n_corners = get_corners(
        flat_verts, scaled_strokes, scaled_aaw,
        angle_from_prev, angle_to_next,
        corners
    );

    int index_map[5] = int[5](0, 0, 1, 2, 2);
    if(n_corners == 4) index_map[2] = 2;

    // Emit each corner
    for(int i = 0; i < n_corners; i++){
        uv_coords = (xy_to_uv * vec3(corners[i], 1.0)).xy;
        uv_stroke_width = uv_scale_factor * scaled_strokes[index_map[i]];
        // Apply some lighting to the color before sending out.
        vec3 xyz_coords = vec3(corners[i], verts[index_map[i]].z);
        color = finalize_color(
            v_color[index_map[i]],
            xyz_coords,
            unit_normal,
            light_source_position,
            camera_position,
            reflectiveness,
            gloss,
            shadow
        );
        gl_Position = get_gl_Position(vec3(corners[i], verts[index_map[i]].z));
        EmitVertex();
    }
    EndPrimitive();
}