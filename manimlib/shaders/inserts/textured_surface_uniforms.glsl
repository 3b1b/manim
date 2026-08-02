/*
What a TexturedSurface holds for the whole of itself, beyond what every mobject does.
*/
layout (std140) uniform MobjectUniforms {
#INSERT common_uniform_members.glsl

    // Whether a dark mode texture was given alongside the light one, in which case
    // the two are blended by which way the surface faces
    float num_textures;
};
