#version 330

in vec3 point;
in float radius;
in vec4 color;

out vec3 v_point;
out float v_radius;
out vec4 v_color;

#INSERT get_gl_Position.glsl

void main(){
    v_point = position_point_into_frame(point);
    v_radius = radius;
    v_color = color;
}