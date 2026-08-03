/*
For kinds of mobject holding nothing of their own beyond what every one of them
has. Those with more declare their own block instead, see vmobject_uniforms.glsl.
*/
layout (std140) uniform MobjectUniforms {
#INSERT common_uniform_members.glsl
};
