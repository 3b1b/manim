#INSERT frame_uniforms.glsl
#INSERT frame_units.glsl

/*
How far a point sits on the keeping side of each of the mobject's four clip planes, for the
fragment shader to cut what falls outside, see clip_test.glsl. A distance is written for
every plane whether or not it is in use, an unused one being all zeros, which stands for
keeping everything.
*/
out vec4 clip_distances;

float clip_distance(vec3 point, vec4 plane){
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
    
    clip_distances = vec4(
        clip_distance(point, clip_plane0),
        clip_distance(point, clip_plane1),
        clip_distance(point, clip_plane2),
        clip_distance(point, clip_plane3)
    );
}
