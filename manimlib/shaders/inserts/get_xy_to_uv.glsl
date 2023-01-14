float cross2d(vec2 v, vec2 w){
    return v.x * w.y - w.x * v.y;
}


vec2 complex_div(vec2 v, vec2 w){
    return vec2(dot(v, w), cross2d(w, v)) / dot(w, w);
}


vec2 xs_on_clean_parabola(vec2 b0, vec2 b1, vec2 b2){
    /*
    Given three control points for a quadratic bezier,
    this returns the two values (x0, x2) such that the
    section of the parabola y = x^2 between those values
    is isometric to the given quadratic bezier.

    Adapated from https://github.com/raphlinus/raphlinus.github.io/blob/master/_posts/2019-12-23-flatten-quadbez.md
    */
    vec2 dd = normalize(2 * b1 - b0 - b2);

    float u0 = dot(b1 - b0, dd);
    float u2 = dot(b2 - b1, dd);
    float cp = cross2d(b2 - b0, dd);

    return vec2(u0 / cp, u2 / cp);
}


mat3 map_point_pairs(vec2 src0, vec2 src1, vec2 dest0, vec2 dest1){
    /*
    Returns an orthogonal matrix which will map
    src0 onto dest0 and src1 onto dest1.
    */
    mat3 shift1 = mat3(
        1.0, 0.0, 0.0,
        0.0, 1.0, 0.0,
        -src0.x, -src0.y, 1.0
    );
    mat3 shift2 = mat3(
        1.0, 0.0, 0.0,
        0.0, 1.0, 0.0,
        dest0.x, dest0.y, 1.0
    );

    // Compute complex division dest_vect / src_vect to determine rotation
    vec2 complex_rot = complex_div(dest1 - dest0, src1 - src0);
    mat3 rotate = mat3(
        complex_rot.x, complex_rot.y, 0.0,
        -complex_rot.y, complex_rot.x, 0.0,
        0.0, 0.0, 1.0
    );

    return shift2 * rotate * shift1;
}


mat3 get_xy_to_uv(vec2 b0, vec2 b1, vec2 b2, float temp_is_linear, out float is_linear){
    /*
    Returns a matrix for an affine transformation which maps a set of quadratic
    bezier controls points into a new coordinate system such that the bezier curve
    coincides with y = x^2, or in the case of a linear curve, it's mapped to the x-axis.
    */
    vec2 dest0;
    vec2 dest1;
    is_linear = temp_is_linear;
    // Portions of the parabola y = x^2 where abs(x) exceeds
    // this value are treated as straight lines.
    float thresh = 2.0;
    if (!bool(is_linear)){
        vec2 xs = xs_on_clean_parabola(b0, b1, b2);
        float x0 = xs.x;
        float x2 = xs.y;
        if((x0 > thresh && x2 > thresh) || (x0 < -thresh && x2 < -thresh)){
            is_linear = 1.0;
        }else{
            dest0 = vec2(x0, x0 * x0);
            dest1 = vec2(x2, x2 * x2);
        }
    }
    // Check if is_linear status changed above
    if (bool(is_linear)){
        dest0 = vec2(0, 0);
        dest1 = vec2(1, 0);
    }

    return map_point_pairs(b0, b2, dest0, dest1);
}
