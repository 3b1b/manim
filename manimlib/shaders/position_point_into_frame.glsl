// Must be used in an environment with the following uniforms:
// uniform mat4 to_screen_space;
// uniform float focal_distance;

vec3 position_point_into_frame(vec3 point){
    // Apply the pre-computed to_screen_space matrix.
    vec4 new_point = to_screen_space * vec4(point, 1);
    return new_point.xyz;
}
