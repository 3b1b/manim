/*
Cuts away whatever falls outside a mobject's clip planes. The vertex shader works out how
far each point sits on the keeping side of each of the four planes, see project_point.wgsl,
and every fragment shader drops a fragment which any of them puts outside.

Dropping a fragment rather than cutting the geometry is the only way wgpu offers, having no
clip distance on every backend it targets. It comes to the same picture, the boundary being
a hard edge either way since nothing anti-aliases a cut, and a dropped fragment writing
neither color nor depth nor stencil.
*/

fn clip_test(clip_distances: vec4f) {
    if (any(clip_distances < vec4f(0.0))) { discard; }
}
