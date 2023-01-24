#version 330

in vec4 color;
in float fill_all;
in vec2 uv_coords;

out vec4 frag_color;

void main() {
    if (color.a == 0) discard;
    frag_color = color;
    if (bool(fill_all)) return;

    float x = uv_coords.x;
    float y = uv_coords.y;
    if(y - x * x < 0) discard;
}
