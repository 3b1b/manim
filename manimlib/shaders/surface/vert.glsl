#version 330

uniform vec4 clip_plane;

in vec3 point;
in vec3 du_point;
in vec3 dv_point;
in vec4 rgba;

out vec3 xyz_coords;
out vec3 v_normal;
out vec4 v_color;

#INSERT get_gl_Position.glsl
#INSERT get_rotated_surface_unit_normal_vector.glsl
#INSERT finalize_color.glsl

void main(){
    xyz_coords = position_point_into_frame(point);
    v_normal = get_rotated_surface_unit_normal_vector(point, du_point, dv_point);
    v_color = rgba;
    gl_Position = get_gl_Position(xyz_coords);

    if(clip_plane.xyz != vec3(0.0, 0.0, 0.0)){
        gl_ClipDistance[0] = dot(vec4(point, 1.0), clip_plane);
    }

    v_color = finalize_color(
        rgba,
        xyz_coords,
        v_normal,
        light_source_position,
        camera_position,
        reflectiveness,
        gloss,
        shadow
    );
}