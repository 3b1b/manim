uniform float is_fixed_in_frame;
uniform mat4 view;
uniform float focal_distance;

const float DEFAULT_FRAME_HEIGHT = 8.0;
const float DEFAULT_FRAME_WIDTH = DEFAULT_FRAME_HEIGHT * 16.0 / 9.0;

vec4 get_gl_Position(vec3 point){
    vec4 result = vec4(point, 1.0);
    if(!bool(is_fixed_in_frame)){
        result = view * result;
    }
    result.x *= 2.0 / DEFAULT_FRAME_WIDTH;
    result.y *= 2.0 / DEFAULT_FRAME_HEIGHT;
    result.z /= focal_distance;
    result.w = 1.0 - result.z;
    // Flip and scale to prevent premature clipping
    result.z *= -0.1;
    return result;
}
