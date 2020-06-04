#version 330

// uniform sampler2D Texture;

// in vec2 v_im_coords;
in vec4 v_color;

out vec4 frag_color;

void main() {
    frag_color = v_color;
}