#version 330

uniform float frame_scale;
uniform float is_fixed_in_frame;

in vec3 point;
in vec4 stroke_rgba;
in float stroke_width;
in vec4 joint_product;

// Bezier control point
out vec3 verts;

out vec4 v_joint_product;
out float v_stroke_width;
out vec4 v_color;
out int v_vert_index;

const float STROKE_WIDTH_CONVERSION = 0.01;

void main(){
    verts = point;
    // v_stroke_width = STROKE_WIDTH_CONVERSION * stroke_width * mix(frame_scale, 1, is_fixed_in_frame);
    v_stroke_width = STROKE_WIDTH_CONVERSION * stroke_width;
    v_joint_product = joint_product;
    v_color = stroke_rgba;
    v_vert_index = gl_VertexID;
}