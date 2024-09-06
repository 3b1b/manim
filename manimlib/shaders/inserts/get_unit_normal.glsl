vec3 get_unit_normal(vec3 p0, vec3 p1, vec3 p2){
    float tol = 1e-6;
    vec3 v1 = normalize(p1 - p0);
    vec3 v2 = normalize(p2 - p0);
    vec3 cp = cross(v1, v2);
    float cp_norm = length(cp);

    if(cp_norm > tol) return cp / cp_norm;

    // Otherwise, three pionts form a line, so find
    // a normal vector to that line in the plane shared
    // with the z-axis
    vec3 comb = v1 + v2;
    cp = cross(cross(comb, vec3(0.0, 0.0, 1.0)), comb);
    cp_norm = length(cp);
    if(cp_norm > tol) return cp / cp_norm;

    // Otherwise, the points line up with the z-axis.
    return vec3(0.0, -1.0, 0.0);
}