/*
What a DotCloud holds for the whole of itself. Overlapping with what another kind of
mobject happens to need is of no consequence, since each declares its own block.
*/
layout (std140) uniform MobjectUniforms {
#INSERT common_uniform_members.glsl

    // Measured in pixel widths
    float anti_alias_width;
    // Above zero, a dot fades out towards its edge rather than ending abruptly
    float glow_factor;
};
