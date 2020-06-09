// Assumes the following uniforms exist in the surrounding context:
// uniform vec2 frame_shape;
// uniform float focal_distance;
// uniform float is_fixed_in_frame;

const vec2 DEFAULT_FRAME_SHAPE = vec2(8 * 16 / 9, 8);

vec4 get_gl_Position(vec3 point){
    if(!bool(is_fixed_in_frame)){
        point.x *= 2 / frame_shape.x;
        point.y *= 2 / frame_shape.y;
        point.z /= focal_distance;
        point.xy /= max(1 - point.z, 0);
        // Todo, does this discontinuity add weirdness?  Theoretically, by this point,
        // the z-coordiante of gl_Position only matter for z-indexing.  The reason
        // for thie line is to avoid agressive clipping of distant points.
        if(point.z < 0) point.z *= 0.1;
    } else{
        point.x *= 2 / DEFAULT_FRAME_SHAPE.x;
        point.y *= 2 / DEFAULT_FRAME_SHAPE.y;

    }
    return vec4(point.xy, -point.z, 1);
}