/*
Everything a VMobject holds which is one value for the whole of it, rather than one
per point. Shared by the stroke and fill shaders, since a mobject sends one buffer
for both of them to read.
*/
layout (std140) uniform MobjectUniforms {
#INSERT common_uniform_members.glsl

    // Measured in pixel widths
    float anti_alias_width;
    // 0 leaves corners as sharp as they can be without jutting out, 1 rounds them all
    float joint_roundness;
    float flat_stroke;
    // If false, stroke width is measured relative to the frame, so that a given width
    // looks the same at any zoom level. If true, relative to the scene.
    float stroke_width_in_scene_units;
    // A filled VMobject is taken to be flat, which is what lets its normal be one
    // value rather than one per point
    vec3 unit_normal;
    // A fill runs between these two colors, over the stretch from gradient_start to
    // gradient_end. Equal colors, the usual case, leave the gradient of no effect.
    vec4 fill_rgba;
    vec4 fill_rgba_end;
    vec3 gradient_start;
    vec3 gradient_end;
    // A width of zero still draws a band just wide enough to anti-alias the edge
    float fill_border_width;
};
