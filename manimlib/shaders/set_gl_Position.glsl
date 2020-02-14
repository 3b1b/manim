// Assumes theese uniforms exist in the surrounding context
// uniform float scale;
// uniform float aspect_ratio;
// uniform float frame_center;

void set_gl_Position(vec3 point){
    // TODO, orient in 3d based on certain rotation matrices
    point -= frame_center;
    point /= scale;
    point.x /= aspect_ratio;
    gl_Position = vec4(point, 1.0);
}