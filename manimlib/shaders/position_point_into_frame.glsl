// Must be used in an environment with the following uniforms:
// uniform mat4 to_screen_space;
// uniform float focal_distance;

vec3 position_point_into_frame(vec3 point){
    // Most of the heavy lifting is done by the pre-computed
    // to_screen_space matrix; here's there just a little added
    // perspective morphing.
    vec4 new_point = to_screen_space * vec4(point, 1);
    new_point.z /= focal_distance;
    new_point.xy /= max(1 - new_point.z, 0);
    return new_point.xyz;
}
