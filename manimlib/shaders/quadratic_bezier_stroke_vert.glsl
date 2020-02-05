#version 330

in vec3 point;
in vec3 prev_point;
in vec3 next_point;

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

    bp = point.xy;  // TODO, apply some kind of 3d rotation or shift first
    prev_bp = prev_point.xy;
    next_bp = next_point.xy;
}