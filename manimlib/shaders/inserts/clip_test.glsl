/*
Cuts away whatever falls outside a mobject's clip planes.

The vertex shader works out how far each point sits on the keeping side of each of the four
planes, see emit_gl_Position.glsl, and every fragment shader drops a fragment which any of
them puts outside. Dropping a fragment rather than cutting the geometry is what a hardware
clip distance did until now; it comes to the same picture, the boundary being a hard edge
either way since nothing anti-aliases a cut, and a dropped fragment writing neither color
nor depth nor stencil. It is also the only way wgpu offers, which has no clip distance on
every backend it targets.
*/
in vec4 clip_distances;

void clip_test(){
    if (any(lessThan(clip_distances, vec4(0.0)))) discard;
}
