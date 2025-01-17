#version 330

in vec3 point;
in vec3 d_normal_point;
in vec2 im_coords;
in float opacity;

out vec3 v_point;
out vec3 v_unit_normal;
out vec2 v_im_coords;
out float v_opacity;

uniform float is_sphere;
uniform vec3 center;

#INSERT emit_gl_Position.glsl
#INSERT get_unit_normal.glsl

const float EPSILON = 1e-10;

void main(){
    v_point = point;
    v_unit_normal = normalize(d_normal_point - point);;
    v_im_coords = im_coords;
    v_opacity = opacity;
    emit_gl_Position(point);
}