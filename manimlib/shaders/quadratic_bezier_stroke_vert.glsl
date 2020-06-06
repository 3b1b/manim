#version 330

uniform mat4 to_screen_space;
uniform float focal_distance;

in vec3 point;
in vec3 prev_point;
in vec3 next_point;
in vec3 unit_normal;

in float stroke_width;
in vec4 color;
in float joint_type;
in float gloss;
in float shadow;

// Bezier control point
out vec3 bp;
out vec3 prev_bp;
out vec3 next_bp;
out vec3 v_global_unit_normal;

out float v_stroke_width;
out vec4 v_color;
out float v_joint_type;
out float v_gloss;
out float v_shadow;

const float STROKE_WIDTH_CONVERSION = 0.0025;

// To my knowledge, there is no notion of #include for shaders,
// so to share functionality between this and others, the caller
// replaces this line with the contents of named file
#INSERT position_point_into_frame.glsl

void main(){
    bp = position_point_into_frame(point);
    prev_bp = position_point_into_frame(prev_point);
    next_bp = position_point_into_frame(next_point);
    v_global_unit_normal = normalize(position_point_into_frame(unit_normal));

    v_stroke_width = STROKE_WIDTH_CONVERSION * stroke_width;
    v_color = color;
    v_joint_type = joint_type;
    v_gloss = gloss;
    v_shadow = shadow;
}