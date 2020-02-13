// Assumes theese uniforms exist in the surrounding context
// uniform float scale;
// uniform float aspect_ratio;
// uniform float frame_center;

void set_gl_Position(vec3 point){
    // TODO, orient in 3d based on certain rotation matrices
    point /= scale;
    point.x /= aspect_ratio;
    point -= frame_center;
    gl_Position = vec4(point, 1.0);
}