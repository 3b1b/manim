#version 330

uniform vec3 light_source_position;
uniform vec3 camera_position;
uniform float reflectiveness;
uniform float gloss;
uniform float shadow;
uniform float focal_distance;

in vec3 xyz_coords;
in vec3 v_normal;
in vec4 v_color;

out vec4 frag_color;

#INSERT finalize_color.glsl

void main() {
    frag_color = finalize_color(
        v_color,
        xyz_coords,
        normalize(v_normal),
        light_source_position,
        camera_position,
        reflectiveness,
        gloss,
        shadow
    );
}