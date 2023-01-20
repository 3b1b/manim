vec2 xs_on_clean_parabola(vec3 b0, vec3 b1, vec3 b2){
    /*
    Given three control points for a quadratic bezier,
    this returns the two values (x0, x2) such that the
    section of the parabola y = x^2 between those values
    is isometric to the given quadratic bezier.

    Adapated from https://raphlinus.github.io/graphics/curves/2019/12/23/flatten-quadbez.html
    */
    vec3 dd = 2 * b1 - b0 - b2;

    float u0 = dot(b1 - b0, dd);
    float u2 = dot(b2 - b1, dd);
    float cp = length(cross(b2 - b0, dd));

    return vec2(u0 / cp, u2 / cp);
}


mat4 map_triangles(vec3 src0, vec3 src1, vec3 src2, vec3 dst0, vec3 dst1, vec3 dst2){
    /*
    Return an affine transform which maps the triangle (src0, src1, src2)
    onto the triangle (dst0, dst1, dst2)
    */
    mat4 src_mat = mat4(
        src0, 1.0,
        src1, 1.0,
        src2, 1.0,
        vec4(1.0)
    );
    mat4 dst_mat = mat4(
        dst0, 1.0,
        dst1, 1.0,
        dst2, 1.0,
        vec4(1.0)
    );
    return dst_mat * inverse(src_mat);
}


mat4 rotation(vec3 axis, float cos_angle){
    float c = cos_angle;
    float s = sqrt(1 - c * c);  // Sine of the angle
    float oc = 1.0 - c;
    float ax = axis.x;
    float ay = axis.y;
    float az = axis.z;

    return mat4(
        oc * ax * ax + c,      oc * ax * ay + az * s, oc * az * ax - ay * s, 0.0,
        oc * ax * ay - az * s, oc * ay * ay + c,      oc * ay * az + ax * s, 0.0,
        oc * az * ax + ay * s, oc * ay * az - ax * s, oc * az * az + c,      0.0,
        0.0, 0.0, 0.0, 1.0
    );
}


mat4 map_onto_x_axis(vec3 src0, vec3 src1){
    mat4 shift = mat4(1.0);
    shift[3].xyz = -src0;

    // Find rotation matrix between unit vectors in each direction    
    vec3 vect = normalize(src1 - src0);
    // No rotation needed
    if(vect.x > 1 - 1e-6) return shift;

    // Equivalent to cross(vect, vec3(1, 0, 0))
    vec3 axis = normalize(vec3(0.0, vect.z, -vect.y));
    mat4 rotate = rotation(axis, vect.x);
    return rotate * shift;
}


mat4 get_xyz_to_uv(
    vec3 b0, vec3 b1, vec3 b2,
    float threshold,
    out bool exceeds_threshold
){
    /*
    Populates the matrix `result` with an affine transformation which maps a set of
    quadratic bezier controls points into a new coordinate system such that the bezier
    curve coincides with y = x^2.

    If the x-range under this part of the curve exceeds `threshold`, this returns false
    and populates result a matrix mapping b0 and b2 onto the x-axis
    */
    vec2 xs = xs_on_clean_parabola(b0, b1, b2);
    float x0 = xs[0];
    float x1 = 0.5 * (xs[0] + xs[1]);
    float x2 = xs[1];
    // Portions of the parabola y = x^2 where abs(x) exceeds
    // this value are treated as straight lines.
    exceeds_threshold = (min(x0, x2) > threshold || max(x0, x2) < -threshold);
    if(exceeds_threshold){
        return map_onto_x_axis(b0, b2);
    }
    // This triangle on the xy plane should be isometric
    // to (b0, b1, b2), and it should define a quadratic
    // bezier segment aligned with y = x^2
    vec3 dst0 = vec3(x0, x0 * x0, 0.0);
    vec3 dst1 = vec3(x1, x0 * x2, 0.0);
    vec3 dst2 = vec3(x2, x2 * x2, 0.0);
    return map_triangles(b0, b1, b2, dst0, dst1, dst2);
}
