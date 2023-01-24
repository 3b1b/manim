#version 330

in vec4 color;
in float fill_all;  // Either 0 or 1

in float orientation;
in vec2 uv_coords;

out vec4 frag_color;

void main() {
    if (color.a == 0) discard;
    frag_color = color;
    if (orientation == 0) return;

    float x0 = uv_coords.x;
    float y0 = uv_coords.y;
    float Fxy = y0 - x0 * x0;
    if(orientation * Fxy < 0) discard;

}
