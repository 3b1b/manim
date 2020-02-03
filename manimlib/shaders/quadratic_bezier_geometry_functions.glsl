// This file is not a shader, it's just a set of
// functions meant to be inserted into other shaders.

float cross(vec2 v, vec2 w){
    return v.x * w.y - w.x * v.y;
}

// Matrix to convert to a uv space defined so that
// b0 goes to [0, 0] and b1 goes to [1, 0]
mat3 get_xy_to_uv(vec2 b0, vec2 b1){
    vec2 T = b1 - b0;

    mat3 shift = mat3(
        1, 0, 0,
        0, 1, 0,
        -b0.x, -b0.y, 1
    );
    mat3 rotate_and_scale = mat3(
        T.x, -T.y, 0,
        T.y, T.x, 0,
        0, 0, 1
    ) / dot(T, T);
    return rotate_and_scale * shift;
}


// Returns 0 for null curve, 1 for linear, 2 for quadratic.
// Populates new_points with bezier control points for the curve,
// which for quadratics will be the same, but for linear and null
// might change.  The idea is to inform the caller of the degree,
// while also passing tangency information in the linear case.
int get_reduced_control_points(vec2 b0, vec2 b1, vec2 b2, out vec2 new_points[3]){
    float epsilon = 1e-6;
    vec2 v01 = (b1 - b0);
    vec2 v12 = (b2 - b1);
    bool distinct_01 = length(v01) > epsilon;  // v01 is considered nonzero
    bool distinct_12 = length(v12) > epsilon;  // v12 is considered nonzero
    int n_uniques = int(distinct_01) + int(distinct_12);
    if(n_uniques == 2){
        bool linear = dot(normalize(v01), normalize(v12)) > 1 - epsilon;
        if(linear){
            new_points[0] = b0;
            new_points[1] = b2;
            return 1;
        }else{
            new_points[0] = b0;
            new_points[1] = b1;
            new_points[2] = b2;
            return 2;
        }
    }else if(n_uniques == 1){
        new_points[0] = b0;
        new_points[1] = b2;
        return 1;
    }else{
        new_points[0] = b0;
        return 0;
    }
}