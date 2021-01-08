// Assumes the following uniforms exist in the surrounding context:
// uniform mat4 to_screen_space;
// uniform float is_fixed_in_frame;

vec3 position_point_into_frame(vec3 point){
    if(bool(is_fixed_in_frame)){
        return point;
    }else{
        // Simply apply the pre-computed to_screen_space matrix.
        return (to_screen_space * vec4(point, 1)).xyz;
    }
}
