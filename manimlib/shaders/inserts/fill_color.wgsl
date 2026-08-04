fn fill_color_at(point: vec3f) -> vec4f {
    /*
    A fill runs between two colors, over the stretch from one of a pair of points to the
    other. Where the two colors are the same, which is the usual case, none of this makes
    any difference.
    */
    let axis = mob.gradient_end - mob.gradient_start;
    let t = dot(point - mob.gradient_start, axis) / max(dot(axis, axis), 1e-8);
    return mix(mob.fill_rgba, mob.fill_rgba_end, t);
}
