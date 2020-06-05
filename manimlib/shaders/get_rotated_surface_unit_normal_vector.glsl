// Only inlucde in an environment with to_screen_space defined

vec3 get_rotated_surface_unit_normal_vector(vec3 point, vec3 du_point, vec3 dv_point){
    // normal = get_unit_normal(point, du_point, dv_point);
    // return normalize((to_screen_space * vec4(normal, 0.0)).xyz);
    vec3 cp = cross(
        (du_point - point),
        (dv_point - point)
    );
    if(length(cp) == 0){
        // Instead choose a normal to just dv_point - point in the direction of point
        vec3 v2 = dv_point - point;
        cp = cross(cross(v2, point), v2);
    }
    // The zero is deliberate, as we only want to rotate and not shift
    return normalize((to_screen_space * vec4(cp, 0.0)).xyz);
}