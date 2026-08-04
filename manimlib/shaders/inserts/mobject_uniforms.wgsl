/*
What the mobject being drawn holds for the whole of itself. The members are generated from
its uniform_dtype, so that a shader and the array feeding it cannot drift apart, and every
kind of mobject gets the members its own kind declares, starting with the ones every kind
has, see Mobject.uniform_dtype and shaders.uniform_block_code.
*/
struct MobjectUniforms {
// MOBJECT_UNIFORMS
}

@group(1) @binding(0) var<uniform> mob: MobjectUniforms;
