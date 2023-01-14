#version 330

#INSERT camera_uniform_declarations.glsl

uniform vec3 light_source_position;
uniform vec3 camera_position;
uniform float reflectiveness;
uniform float gloss;
uniform float shadow;

in vec3 point;
in vec3 du_point;
in vec3 dv_point;
in vec4 color;

out vec3 xyz_coords;
out vec3 v_normal;
out vec4 v_color;

#INSERT position_point_into_frame.glsl
#INSERT get_gl_Position.glsl
#INSERT get_rotated_surface_unit_normal_vector.glsl
#INSERT finalize_color.glsl

void main(){
    xyz_coords = position_point_into_frame(point);
    v_normal = get_rotated_surface_unit_normal_vector(point, du_point, dv_point);
    v_color = color;
    gl_Position = get_gl_Position(xyz_coords);

    v_color = finalize_color(
        color,
        xyz_coords,
        v_normal,
        light_source_position,
        camera_position,
        reflectiveness,
        gloss,
        shadow
    );
}