#version 330

in vec3 point;
in float radius;
in vec4 rgba;

out vec3 v_point;
out float v_radius;
out vec4 v_rgba;


void main(){
    v_point = point;
    v_radius = radius;
    v_rgba = rgba;
}