/*
What holds for every mobject of a frame: where the camera is looking from and along, how
much of the scene the frame covers, and where the light is. One block, written once a frame
by the camera rather than pushed into each program separately, see Camera.refresh_uniforms
and shaders.FRAME_UNIFORMS, which this mirrors.

Guarded, since several inserts want these and a block may only be declared once.
*/
#ifndef MANIM_FRAME_UNIFORMS
#define MANIM_FRAME_UNIFORMS

layout (std140) uniform FrameUniforms {
    mat4 view;
    vec3 frame_rescale_factors;
    float frame_scale;
    vec3 camera_position;
    float pixel_size;
    vec3 light_position;
};

#endif
