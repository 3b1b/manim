uniform vec4 fill_rgba;
uniform vec4 fill_rgba_end;
uniform vec3 gradient_center;
uniform vec3 gradient_axis;

vec4 fill_color_at(vec3 point){
    /*
    A fill runs between two colors along its gradient axis, which is centered on the
    mobject and scaled so that the two ends land on the extremes of it. Where the two
    colors are the same, which is the usual case, none of this makes any difference.
    */
    return mix(fill_rgba, fill_rgba_end, 0.5 + dot(point - gradient_center, gradient_axis));
}
