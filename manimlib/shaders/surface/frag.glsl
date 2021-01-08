#version 330

uniform vec3 light_source_position;
uniform float gloss;
uniform float shadow;

in vec3 xyz_coords;
in vec3 v_normal;
in vec4 v_color;

out vec4 frag_color;

#INSERT add_light.glsl

void main() {
    frag_color = add_light(
        v_color,
        xyz_coords,
        normalize(v_normal),
        light_source_position,
        gloss,
        shadow
    );
}