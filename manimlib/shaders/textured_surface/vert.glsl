#version 330

in vec3 point;
in vec3 normal;
in vec2 im_coords;
in float opacity;

out vec3 v_point;
out vec3 v_normal;
out vec2 v_im_coords;
out float v_opacity;

#INSERT emit_gl_Position.glsl
#INSERT get_unit_normal.glsl

void main(){
    v_point = point;
    v_normal = normal;
    v_im_coords = im_coords;
    v_opacity = opacity;
    emit_gl_Position(point);
}