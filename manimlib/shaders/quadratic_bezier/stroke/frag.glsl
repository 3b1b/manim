#version 330


/*
When the stroke is tracing the border of a fill, it gets drawn twice: once
outside the shape and once inside it. Which of the two a fragment belongs to is
settled by the stencil, not by anything geometric, since the path's orientation
decides which side of a curve the interior lies on and the shader has no way to
know it. Outside, the band carries the falling half of the coverage ramp, and
inside the rising half, so that the two together make a single smooth
transition centered on the path.
*/
uniform bool fill_border_inside;

// Distance to the curve, and half the curve width, both as
// a ratio of the antialias width
in float dist_to_aaw;
in float half_width_to_aaw;
in vec4 color;

out vec4 frag_color;

void main() {
    frag_color = color;
    float dist = abs(dist_to_aaw);
    // sdf for the region around the curve we wish to color. Inside a fill, the
    // band is measured from the far edge of the stroke rather than the near one,
    // so that a border wide enough to cover the fragment leaves it fully opaque.
    float coverage = fill_border_inside ?
        1.0 - smoothstep(0.5, -0.5, dist + half_width_to_aaw) :
        smoothstep(0.5, -0.5, dist - half_width_to_aaw);
    frag_color.a *= coverage;
    // This line is replaced in VShaderWrapper
    // MODIFY FRAG COLOR
}
