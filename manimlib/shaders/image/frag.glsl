#version 330


uniform sampler2D Texture;

in vec2 v_im_coords;
in float v_opacity;

out vec4 frag_color;

#INSERT clip_test.glsl

void main() {
    clip_test();
    frag_color = texture(Texture, v_im_coords);
    frag_color.a *= v_opacity;
}