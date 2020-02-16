// Assumes theese uniforms exist in the surrounding context
// uniform float scale;
// uniform float aspect_ratio;
// uniform float frame_center;

vec3 scale_and_shift_point_for_frame(vec3 point){
    point -= frame_center;
    point /= scale;
    point.x /= aspect_ratio;
    return point;
}