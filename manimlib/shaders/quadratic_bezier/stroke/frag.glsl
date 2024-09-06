#version 330

// Distance to the curve, and half the curve width, both as
// a ratio of the antialias width
in float dist_to_aaw;
in float half_width_to_aaw;
in vec4 color;

out vec4 frag_color;

void main() {
    frag_color = color;
    // sdf for the region around the curve we wish to color.
    float signed_dist_to_region = abs(dist_to_aaw) - half_width_to_aaw;
    frag_color.a *= smoothstep(0.5, -0.5, signed_dist_to_region);
    // This line is replaced in VShaderWrapper
    // MODIFY FRAG COLOR
}