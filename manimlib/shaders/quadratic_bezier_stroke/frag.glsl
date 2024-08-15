#version 330

// Value between -1 and 1
in float scaled_signed_dist_to_curve;
in float anti_alias_prop;
in vec4 color;

out vec4 frag_color;

void main() {
    if(anti_alias_prop < 0) discard;
    frag_color = color;

    // sdf for the region around the curve we wish to color.
    float signed_dist_to_region = abs(scaled_signed_dist_to_curve) - 1.0;
    frag_color.a *= smoothstep(0, -anti_alias_prop, signed_dist_to_region);
}