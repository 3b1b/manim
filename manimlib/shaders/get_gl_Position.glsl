// Assumes the following uniforms exist in the surrounding context:
// uniform float aspect_ratio;

vec4 get_gl_Position(vec3 point){
    // Extremely minimal modification, but that might change later...
    point.x /= aspect_ratio;
    // Todo, does this discontinuity add weirdness?  Theoretically, by this point,
    // the z-coordiante of gl_Position only matter for z-indexing.  The reason
    // for thie line is to avoid agressive clipping of distant points.
    if(point.z < 0) point.z *= 0.1;
    return vec4(point, 1);
}