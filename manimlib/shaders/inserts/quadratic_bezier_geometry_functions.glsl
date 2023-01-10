float cross2d(vec2 v, vec2 w){
    return v.x * w.y - w.x * v.y;
}


vec2 complex_div(vec2 v, vec2 w){
    return vec2(dot(v, w), cross2d(w, v)) / dot(w, w);
}


vec2 xs_on_clean_parabola(vec2 controls[3]){
    /*
    Given three control points for a quadratic bezier,
    this returns the two values (x0, x2) such that the
    section of the parabola y = x^2 between those values
    is isometric to the given quadratic bezier.

    Adapated from https://github.com/raphlinus/raphlinus.github.io/blob/master/_posts/2019-12-23-flatten-quadbez.md
    */
    vec2 b0 = controls[0];
    vec2 b1 = controls[1];
    vec2 b2 = controls[2];

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


mat3 get_xy_to_uv(vec2 controls[3], float bezier_degree, out float new_bezier_degree){
    vec2[2] dest;
    new_bezier_degree = bezier_degree;
    if (bezier_degree == 1.0){
        dest[0] = vec2(0, 0);
        dest[1] = vec2(1, 0);
    }else{
        vec2 xs = xs_on_clean_parabola(controls);
        float x0 = xs.x;
        float x2 = xs.y;
        float thresh = 2.0;
        if((x0 > thresh && x2 > thresh) || (x0 < -thresh && x2 < -thresh)){
            dest[0] = vec2(0, 0);
            dest[1] = vec2(1, 0);
            new_bezier_degree = 1.0;
        }else{
            dest[0] = vec2(x0, x0 * x0);
            dest[1] = vec2(x2, x2 * x2);
        }
    }
    return map_point_pairs(
        controls[0], controls[2], dest[0], dest[1]
    );
}


// Orthogonal matrix to convert to a uv space defined so that
// b0 goes to [0, 0] and b1 goes to [1, 0]
mat4 get_xyz_to_uv(vec3 b0, vec3 b1, vec3 unit_normal){
    mat4 shift = mat4(
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        -b0.x, -b0.y, -b0.z, 1
    );

    float scale_factor = length(b1 - b0);
    vec3 I = (b1 - b0) / scale_factor;
    vec3 K = unit_normal;
    vec3 J = cross(K, I);
    // Transpose (hence inverse) of matrix taking
    // i-hat to I, k-hat to unit_normal, and j-hat to their cross
    mat4 rotate = mat4(
        I.x, J.x, K.x, 0.0,
        I.y, J.y, K.y, 0.0,
        I.z, J.z, K.z, 0.0,
        0.0, 0.0, 0.0, 1.0
    );
    return (1.0 / scale_factor) * rotate * shift;
}
