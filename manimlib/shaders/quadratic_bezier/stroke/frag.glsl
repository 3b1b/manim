#version 330

// Value between -1 and 1
in float dist_to_curve;
in float half_stroke_width;
in float half_anti_alias_width;
in vec4 color;

out vec4 frag_color;

void main() {
    if(half_stroke_width == 0) discard;
    frag_color = color;

    // sdf for the region around the curve we wish to color.
    float signed_dist_to_region = abs(dist_to_curve) - half_stroke_width;
    frag_color.a *= smoothstep(half_anti_alias_width, -half_anti_alias_width, signed_dist_to_region);
}