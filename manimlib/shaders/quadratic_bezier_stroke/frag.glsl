#version 330

in float signed_dist_to_curve;
in float uv_stroke_width;
in float uv_anti_alias_width;
in vec4 color;

out vec4 frag_color;

void main() {
    if (uv_stroke_width == 0) discard;
    frag_color = color;

    // sdf for the region around the curve we wish to color.
    float signed_dist_to_region = abs(signed_dist_to_curve) - 0.5 * uv_stroke_width;
    frag_color.a *= smoothstep(0.5, -0.5, signed_dist_to_region / uv_anti_alias_width);
}