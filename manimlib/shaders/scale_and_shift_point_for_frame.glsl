// Assumes the following uniforms exist in the surrounding context:
// uniform float aspect_ratio;
// TODO, rename

vec3 get_gl_Position(vec3 point){
    point.x /= aspect_ratio;
    return point;
}