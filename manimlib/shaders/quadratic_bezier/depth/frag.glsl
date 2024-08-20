#version 330

out float frag_depth;

void main() {
    frag_depth = gl_FragCoord.z;
}
