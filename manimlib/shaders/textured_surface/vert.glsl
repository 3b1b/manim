#version 330

in vec3 point;
in vec3 du_point;
in vec3 dv_point;
in vec2 im_coords;
in float opacity;

out vec3 v_point;
out vec3 v_normal;
out vec2 v_im_coords;
out float v_opacity;

#INSERT get_gl_Position.glsl
#INSERT get_unit_normal.glsl

void main(){
    v_point = point;
    v_normal = get_unit_normal(point, du_point, dv_point);
    v_im_coords = im_coords;
    v_opacity = opacity;
    gl_Position = get_gl_Position(position_point_into_frame(point));
}