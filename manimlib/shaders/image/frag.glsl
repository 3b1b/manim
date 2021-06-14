#version 330

uniform sampler2D Texture;

in vec2 v_im_coords;
in float v_opacity;

out vec4 frag_color;

void main() {
    frag_color = texture(Texture, v_im_coords);
    frag_color.a *= v_opacity;
}