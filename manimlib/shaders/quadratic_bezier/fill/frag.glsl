#version 330


in vec4 color;
in float fill_all;
in vec2 uv_coords;

out vec4 frag_color;

void main() {
    if (color.a == 0) discard;

    // For the triangles hugging a bezier curve, cut away the part of the
    // triangle falling outside it. In uv space the curve coincides with y = x^2.
    // Note that this same test runs during both the stencil and the cover pass,
    // so the region counted is exactly the region colored in.
    if (!bool(fill_all) && uv_coords.y < uv_coords.x * uv_coords.x) discard;

    frag_color = color;
}
