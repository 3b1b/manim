uniform float is_fixed_in_frame;
uniform mat4 view;
uniform float focal_distance;
uniform vec3 frame_rescale_factors;

void emit_gl_Position(vec3 point){
    vec4 result = vec4(point, 1.0);
    // This allow for smooth transitions between objects fixed and unfixed from frame
    result = mix(view * result, result, is_fixed_in_frame);
    // Essentially a projection matrix
    result.xyz *= frame_rescale_factors;
    result.w = 1.0 - result.z;
    // Flip and scale to prevent premature clipping
    result.z *= -0.1;
    gl_Position = result;
}
