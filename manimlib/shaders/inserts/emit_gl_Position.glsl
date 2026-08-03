uniform mat4 view;
uniform float focal_distance;
uniform vec3 frame_rescale_factors;

#INSERT frame_units.glsl

float clip_distance(vec3 point, vec4 plane){
    /*
    Clipping stays switched on, so a distance has to be written for every plane,
    whether or not it's in use. An unset plane is all zeros, which stands for
    keeping everything.
    */
    if (plane.xyz == vec3(0.0)) return 1.0;
    return dot(vec4(point, 1.0), plane);
}

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
    
    gl_ClipDistance[0] = clip_distance(point, clip_plane0);
    gl_ClipDistance[1] = clip_distance(point, clip_plane1);
    gl_ClipDistance[2] = clip_distance(point, clip_plane2);
    gl_ClipDistance[3] = clip_distance(point, clip_plane3);
}
