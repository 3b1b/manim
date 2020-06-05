#version 330

uniform sampler2D Texture;
uniform vec3 light_source_position;

in vec3 xyz_coords;
in vec3 v_normal;
in vec2 v_im_coords;
in float v_opacity;
in float v_gloss;

out vec4 frag_color;

#INSERT add_light.glsl

void main() {
    vec4 im_color = texture(Texture, v_im_coords);
    frag_color = add_light(im_color, xyz_coords, normalize(v_normal), light_source_position, v_gloss);
    frag_color.a = v_opacity;
}