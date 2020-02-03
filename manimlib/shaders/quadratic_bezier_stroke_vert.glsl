#version 330

in vec2 point;
in vec2 prev_point;
in vec2 next_point;

in float stroke_width;
in vec4 color;
in float joint_type;

out vec2 bp;  // Bezier control point
out vec2 prev_bp;
out vec2 next_bp;

out float v_stroke_width;
out vec4 v_color;
out float v_joint_type;

// TODO, this should maybe depent on scale
const float STROKE_WIDTH_CONVERSION = 0.01;

void main(){
    v_stroke_width = STROKE_WIDTH_CONVERSION * stroke_width;
    v_color = color;
    v_joint_type = joint_type;

    bp = point;
    prev_bp = prev_point;
    next_bp = next_point;
}