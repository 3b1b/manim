#version 330

uniform mat4 to_screen_space;
uniform float focal_distance;

in vec3 point;
in vec3 prev_point;
in vec3 next_point;

in float stroke_width;
in vec4 color;
in float joint_type;

// Bezier control point
out vec3 bp;
out vec3 prev_bp;
out vec3 next_bp;

out float v_stroke_width;
out vec4 v_color;
out float v_joint_type;

const float STROKE_WIDTH_CONVERSION = 0.0025;

// To my knowledge, there is no notion of #include for shaders,
// so to share functionality between this and others, the caller
// replaces this line with the contents of named file
#INSERT position_point_into_frame.glsl

void main(){
    bp = position_point_into_frame(point);
    prev_bp = position_point_into_frame(prev_point);
    next_bp = position_point_into_frame(next_point);

    v_stroke_width = STROKE_WIDTH_CONVERSION * stroke_width;
    v_stroke_width /= (1 - bp.z);  // Change stroke width by perspective
    v_color = color;
    v_joint_type = joint_type;
}