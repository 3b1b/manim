#version 330

// in vec4 v_color;
// out vec4 frag_color;

uniform vec3 light_source_position;

in vec3 xyz_coords;
in vec3 v_normal;
in vec4 v_color;
in float v_gloss;
in float v_shadow;

out vec4 frag_color;

#INSERT add_light.glsl

void main() {
    frag_color = add_light(
        v_color,
        xyz_coords,
        normalize(v_normal),
        light_source_position,
        v_gloss,
        v_shadow
    );
}