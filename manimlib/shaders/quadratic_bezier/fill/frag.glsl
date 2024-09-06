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
    /*
    We want negatively oriented triangles to be canceled with positively
    oriented ones. The easiest way to do this is to give them negative alpha,
    and change the blend function to just add them. However, this messes with
    usual blending, so instead the following line is meant to let this canceling
    work even for the normal blending equation:

    (1 - alpha) * dst + alpha * src

    We want the effect of blending with a positively oriented triangle followed
    by a negatively oriented one to return to whatever the original frag value
    was. You can work out this will work if the alpha for negative orientations
    is changed to -alpha / (1 - alpha). This has a singularity at alpha = 1,
    so we cap it at a value very close to 1. Effectively, the purpose of this
    cap is to make sure the original fragment color can be recovered even after
    blending with an (alpha = 1) color.
    */
    float a = 0.95 * frag_color.a;
    if(orientation < 0) a = -a / (1 - a);
    frag_color.a = a;

    if (bool(fill_all)) return;

    float x = uv_coords.x;
    float y = uv_coords.y;
    float Fxy = (y - x * x);
    if(Fxy < 0) discard;
}
