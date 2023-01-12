#version 330

layout (triangles) in;
layout (triangle_strip, max_vertices = 6) out;

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


#INSERT get_xy_to_uv.glsl
#INSERT get_gl_Position.glsl
#INSERT get_unit_normal.glsl
#INSERT finalize_color.glsl
#INSERT rotate.glsl


float atan2(float y, float x){
    // Normally atan is undefined for x = 0
    if(x == 0) return sign(y) * 0.5 * PI;
    return atan(y, x);
}


float angle_between(vec2 v1, vec2 v2){
    vec2 quot = complex_div(v2, v1);  // Defined in get_xy_to_uv
    return atan2(quot.y, quot.x);
}


void create_joint(float angle, vec2 unit_tan, float buff,
                  vec2 static_c0, out vec2 changing_c0,
                  vec2 static_c1, out vec2 changing_c1){
    float shift;
    if(abs(angle) < ANGLE_THRESHOLD || abs(angle) > 0.99 * PI || int(joint_type) == NO_JOINT){
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
    vec2 controls[3],
    float stroke_widths[3],
    float aaw,  // Anti-alias width
    float angle_from_prev,
    float angle_to_next,
    out vec2 corners[6]
){
    vec2 p0 = controls[0];
    vec2 p1 = controls[1];
    vec2 p2 = controls[2];

    // Unit vectors for directions between control points
    vec2 v01 = normalize(p1 - p0);
    vec2 v12 = normalize(p2 - p1);

    float buff0 = 0.5 * stroke_widths[0] + aaw;
    float buff2 = 0.5 * stroke_widths[2] + aaw;

    // Add correction for sharp angles to prevent weird bevel effects
    float thresh = 0.8 * PI;
    if(angle_from_prev > thresh) buff0 *= sin(angle_from_prev) / sin(thresh);
    if(angle_to_next > thresh) buff2 *= sin(angle_to_next) / sin(thresh);

    // Peperndicular vectors to the left of the curve
    vec2 p0_perp = buff0 * vec2(-v01.y, v01.x);  
    vec2 p2_perp = buff2 * vec2(-v12.y, v12.x);
    vec2 p1_perp = 0.5 * (p0_perp + p2_perp);

    // The order of corners should be for a triangle_strip.
    vec2 c0 = p0 + p0_perp;
    vec2 c1 = p0 - p0_perp;
    vec2 c2 = p1 + p1_perp;
    vec2 c3 = p1 - p1_perp;
    vec2 c4 = p2 + p2_perp;
    vec2 c5 = p2 - p2_perp;
    float cross_prod = cross2d(v01, v12);
    if(cross_prod > 0.0){ // Positive orientation
        c2 = 0.5 * (c0 + c4);
    }else if(cross_prod < 0.0){
        c3 = 0.5 * (c1 + c5);
    }

    // Account for previous and next control points
    create_joint(angle_from_prev, v01, buff0, c1, c1, c0, c0);
    create_joint(angle_to_next, -v12, buff2, c5, c5, c4, c4);

    corners = vec2[6](c0, c1, c2, c3, c4, c5);
}


void main() {
    if (int(v_vert_index[0]) % 2 == 1) return;
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
    float angle = angle_between(flat_verts[1] - flat_verts[0], flat_verts[2] - flat_verts[1]);
    is_linear = float(abs(angle) < ANGLE_THRESHOLD);
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
    vec2 corners[6];
    get_corners(
        flat_verts, scaled_strokes, scaled_aaw,
        angle_from_prev, angle_to_next,
        corners
    );

    // Emit each corner
    for(int i = 0; i < 6; i++){
        int vert_index = i / 2;
        uv_coords = (xy_to_uv * vec3(corners[i], 1.0)).xy;
        uv_stroke_width = uv_scale_factor * scaled_strokes[vert_index];
        // Apply some lighting to the color before sending out.
        vec3 xyz_coords = vec3(corners[i], verts[vert_index].z);
        color = finalize_color(
            v_color[vert_index],
            xyz_coords,
            unit_normal,
            light_source_position,
            camera_position,
            reflectiveness,
            gloss,
            shadow
        );
        gl_Position = get_gl_Position(vec3(corners[i], verts[vert_index].z));
        EmitVertex();
    }
    EndPrimitive();
}