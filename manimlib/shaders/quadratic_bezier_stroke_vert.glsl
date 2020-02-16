#version 330

in vec3 point;
in vec3 prev_point;
in vec3 next_point;

in float stroke_width;
in vec4 color;
in float joint_type;

out vec3 bp;  // Bezier control point
out vec3 prev_bp;
out vec3 next_bp;

out float v_stroke_width;
out vec4 v_color;
out float v_joint_type;

// TODO, this should maybe depend on scale
const float STROKE_WIDTH_CONVERSION = 0.01;


#INSERT rotate_point_for_frame.glsl


void main(){
    v_stroke_width = STROKE_WIDTH_CONVERSION * stroke_width;
    v_color = color;
    v_joint_type = joint_type;

    bp = rotate_point_for_frame(point);
    prev_bp = rotate_point_for_frame(prev_point);
    next_bp = rotate_point_for_frame(next_point);
}