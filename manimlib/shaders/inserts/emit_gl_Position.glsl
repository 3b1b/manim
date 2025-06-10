uniform float is_fixed_in_frame;
uniform mat4 view;
uniform float focal_distance;
uniform vec3 frame_rescale_factors;
uniform vec4 clip_plane;

void emit_gl_Position(vec3 point){
    vec4 result = vec4(point, 1.0);
    // This allows for smooth transitions between objects fixed and unfixed from frame
    result = mix(view * result, result, is_fixed_in_frame);
    // Essentially a projection matrix
    result.xyz *= frame_rescale_factors;
    result.w = 1.0 - result.z;
    // Flip and scale to prevent premature clipping
    result.z *= -0.1;
    gl_Position = result;
    
    if(clip_plane.xyz != vec3(0.0, 0.0, 0.0)){
        gl_ClipDistance[0] = dot(vec4(point, 1.0), clip_plane);
    }
}
