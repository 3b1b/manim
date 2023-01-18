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
    vec3 cp = cross(b2 - b0, dd);
    float denom = length(cp);

    return vec2(u0 / denom, u2 / denom);
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


mat4 map_point_pairs(vec3 src0, vec3 src1, vec3 dest0, vec3 dest1){
    /*
    Returns an orthogonal matrix which will map
    src0 onto dest0 and src1 onto dest1.
    */
    mat4 shift1 = mat4(
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        -src0.x, -src0.y, -src0.z, 1.0
    );
    mat4 shift2 = mat4(
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        dest0.x, dest0.y, dest0.z, 1.0
    );

    // Find rotation matrix between unit vectors in each direction    
    vec3 src_v = src1 - src0;
    vec3 dst_v = dest1 - dest0;
    float src_len = length(src_v);
    float dst_len = length(dst_v);
    float scale = dst_len / src_len;
    src_v /= src_len;
    dst_v /= dst_len;

    vec3 cp = cross(src_v, dst_v);
    float dp = dot(src_v, dst_v);

    float s = length(cp); // Sine of the angle between them
    float c = dp;         // Cosine of the angle between them

    if(s < 1e-8){
        // No rotation needed
        return shift2 * shift1;
    }

    vec3 axis = cp / s;   // Axis of rotation
    float oc = 1.0 - c;
    float ax = axis.x;
    float ay = axis.y;
    float az = axis.z;

    // Rotation matrix about axis, with a given angle corresponding to s and c.
    mat4 rotate = scale * mat4(
        oc * ax * ax + c,      oc * ax * ay + az * s, oc * az * ax - ay * s, 0.0,
        oc * ax * ay - az * s, oc * ay * ay + c,      oc * ay * az + ax * s, 0.0,
        oc * az * ax + ay * s, oc * ay * az - ax * s, oc * az * az + c,      0.0,
        0.0, 0.0, 0.0, 1.0 / scale
    );

    return shift2 * rotate * shift1;
}


mat4 get_xyz_to_uv(vec3 b0, vec3 b1, vec3 b2, float temp_is_linear, out float is_linear){
    /*
    Returns a matrix for an affine transformation which maps a set of quadratic
    bezier controls points into a new coordinate system such that the bezier curve
    coincides with y = x^2, or in the case of a linear curve, it's mapped to the x-axis.
    */
    vec3 dest0;
    vec3 dest1;
    vec3 dest2;
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
            dest0 = vec3(x0, x0 * x0, 0.0);
            dest1 = vec3(0.5 * (x0 + x2), x0 * x2, 0.0);
            dest2 = vec3(x2, x2 * x2, 0.0);
        }
    }
    // Check if is_linear status changed above
    if (bool(is_linear)){
        dest0 = vec3(0.0, 0.0, 0.0);
        dest2 = vec3(1.0, 0.0, 0.0);
        return map_point_pairs(b0, b2, dest0, dest2);
    }

    // return map_point_pairs(b0, b2, dest0, dest1);
    return map_triangles(b0, b1, b2, dest0, dest1, dest2);
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
