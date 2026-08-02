
vec4 fill_color_at(vec3 point){
    /*
    A fill runs between two colors, over the stretch from one of a pair of points to
    the other. Where the two colors are the same, which is the usual case, none of this
    makes any difference.
    */
    vec3 axis = gradient_end - gradient_start;
    float t = dot(point - gradient_start, axis) / max(dot(axis, axis), 1e-8);
    return mix(fill_rgba, fill_rgba_end, t);
}
