#INSERT frame_units.wgsl

/*
Where a point of the scene lands on the screen, and how far it sits on the keeping side of
each of the mobject's four clip planes. Both come back together because every vertex shader
wants both, and a struct is how WGSL hands back more than one thing.
*/
struct Projection {
    position: vec4f,
    clip_distances: vec4f,
}

fn clip_distance(point: vec3f, plane: vec4f) -> f32 {
    // A distance is worked out for every plane whether or not it is in use, an unused one
    // being all zeros, which stands for keeping everything
    if (all(plane.xyz == vec3f(0.0))) { return 1.0; }
    return dot(vec4f(point, 1.0), plane);
}

fn project_point(point: vec3f) -> Projection {
    var result = vec4f(point, 1.0);
    // This allows for smooth transitions between objects fixed and unfixed from frame
    result = mix(frame.view * result, result, mob.is_fixed_in_frame);
    // Essentially a projection matrix
    let scaled = result.xyz * frame.frame_rescale_factors;
    /*
    What is left of z decides what hides what, between 0 and w. Everything nearer to the
    camera than the origin has a smaller value of it, and a point at the camera itself would
    divide by zero, which is where the frame's far end comes from.
    */
    var projection: Projection;
    projection.position = vec4f(
        scaled.xy,
        0.5 * (1.0 - 1.1 * scaled.z),
        1.0 - scaled.z,
    );
    projection.clip_distances = vec4f(
        clip_distance(point, mob.clip_plane0),
        clip_distance(point, mob.clip_plane1),
        clip_distance(point, mob.clip_plane2),
        clip_distance(point, mob.clip_plane3),
    );
    return projection;
}
