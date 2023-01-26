#version 330

uniform bool winding;

in vec4 color;
in float fill_all;
in float orientation;
in vec2 uv_coords;

out vec4 frag_color;

void main() {
    if (color.a == 0) discard;
    frag_color = color;

    // Pre-multiply alphas
    if(winding) frag_color *= frag_color.a;

    // Give a sign based on orientation so that
    // additive blending cancels as needed
    if(winding && orientation < 0) frag_color *= -1;

    if (bool(fill_all)) return;

    float x = uv_coords.x;
    float y = uv_coords.y;
    float Fxy = (y - x * x);
    if(!winding && orientation < 0) Fxy *= -1;
    if(Fxy < 0) discard;
}
