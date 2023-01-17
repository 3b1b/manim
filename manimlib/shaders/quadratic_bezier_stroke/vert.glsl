#version 330

uniform vec2 frame_shape;

in vec3 point;
in vec4 stroke_rgba;
in float stroke_width;
in float joint_angle;

// Bezier control point
out vec3 verts;

out float v_joint_angle;
out float v_stroke_width;
out vec4 v_color;
out float v_vert_index;

const float STROKE_WIDTH_CONVERSION = 0.01;

void main(){
    verts = point;
    v_stroke_width = STROKE_WIDTH_CONVERSION * stroke_width * frame_shape[1] / 8.0;
    v_joint_angle = joint_angle;
    v_color = stroke_rgba;
    v_vert_index = gl_VertexID;
}