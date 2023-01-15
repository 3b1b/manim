#version 330

in vec3 point;

in float joint_angle;
in float stroke_width;
in vec4 color;

// Bezier control point
out vec3 verts;

out float v_joint_angle;
out float v_stroke_width;
out vec4 v_color;
out float v_vert_index;

const float STROKE_WIDTH_CONVERSION = 0.01;

#INSERT get_gl_Position.glsl

void main(){
    verts = position_point_into_frame(point);

    v_stroke_width = STROKE_WIDTH_CONVERSION * stroke_width * frame_shape[1] / 8.0;
    v_joint_angle = joint_angle;
    v_color = color;
    v_vert_index = gl_VertexID;
}