// Assumes theese uniforms exist in the surrounding context
// uniform float scale;
// uniform float aspect_ratio;
// uniform float frame_center;

vec4 point_to_gl_Position(vec3 p){
    vec3 result = p / scale;
    result.x /= aspect_ratio;
    result -= frame_center;
    gl_Position = vec4(result, 1.0);
}