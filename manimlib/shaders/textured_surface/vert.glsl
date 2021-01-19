#version 330

#INSERT camera_uniform_declarations.glsl

in vec3 point;
in vec3 du_point;
in vec3 dv_point;
in vec2 im_coords;
in float opacity;

out vec3 xyz_coords;
out vec3 v_normal;
out vec2 v_im_coords;
out float v_opacity;

#INSERT position_point_into_frame.glsl
#INSERT get_gl_Position.glsl
#INSERT get_rotated_surface_unit_normal_vector.glsl

void main(){
    xyz_coords = position_point_into_frame(point);
    v_normal = get_rotated_surface_unit_normal_vector(point, du_point, dv_point);
    v_im_coords = im_coords;
    v_opacity = opacity;
    gl_Position = get_gl_Position(xyz_coords);
}