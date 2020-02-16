#version 330

uniform float scale;
uniform float aspect_ratio;
uniform vec3 frame_center;

uniform sampler2D Texture;

in vec3 point;
in vec2 im_coords;
in float opacity;

out vec2 v_im_coords;
out float v_opacity;

// Analog of import for manim only
#INSERT rotate_point_for_frame.glsl
#INSERT scale_and_shift_point_for_frame.glsl

void main(){
    v_im_coords = im_coords;
    v_opacity = opacity;
    gl_Position = vec4(
        rotate_point_for_frame(
            scale_and_shift_point_for_frame(point)
        ),
        1.0
    );
}