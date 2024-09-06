#version 330

uniform float frame_scale;
uniform float is_fixed_in_frame;

in vec3 point;
in vec4 stroke_rgba;
in float stroke_width;
in float joint_angle;
in vec3 unit_normal;

// Bezier control point
out vec3 verts;

out vec4 v_color;
out float v_stroke_width;
out float v_joint_angle;
out vec3 v_unit_normal;
out int v_vert_index;

const float STROKE_WIDTH_CONVERSION = 0.01;

void main(){
    verts = point;
    v_color = stroke_rgba;
    v_stroke_width = STROKE_WIDTH_CONVERSION * stroke_width * mix(frame_scale, 1, is_fixed_in_frame);
    v_joint_angle = joint_angle;
    v_unit_normal = unit_normal;
    v_vert_index = gl_VertexID;
}