// Must be used in an environment with the following uniforms:
// uniform mat4 to_screen_space;

vec3 position_point_into_frame(vec3 point){
    // Simply apply the pre-computed to_screen_space matrix.
    return (to_screen_space * vec4(point, 1)).xyz;
}
