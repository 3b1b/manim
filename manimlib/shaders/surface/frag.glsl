#version 330


in vec4 v_color;
out vec4 frag_color;

#INSERT clip_test.glsl

void main() {
    clip_test();
    frag_color = v_color;
}