/*
What holds for every mobject of a frame: where the camera is looking from and along, how
much of the scene the frame covers, and where the light is. One block, written once a frame
by the camera rather than bound for each mobject, see Camera.refresh_uniforms and
shaders.FRAME_UNIFORMS, which this mirrors.
*/
struct FrameUniforms {
    view: mat4x4f,
    frame_rescale_factors: vec3f,
    frame_scale: f32,
    camera_position: vec3f,
    pixel_size: f32,
    light_position: vec3f,
}

@group(0) @binding(0) var<uniform> frame: FrameUniforms;
