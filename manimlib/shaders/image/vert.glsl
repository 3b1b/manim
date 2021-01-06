#version 330

uniform vec2 frame_shape;
uniform float anti_alias_width;
uniform mat4 to_screen_space;
uniform float is_fixed_in_frame;
uniform float focal_distance;

uniform sampler2D Texture;

in vec3 point;
in vec2 im_coords;
in float opacity;

out vec2 v_im_coords;
out float v_opacity;

// Analog of import for manim only
#INSERT get_gl_Position.glsl
#INSERT position_point_into_frame.glsl

void main(){
    v_im_coords = im_coords;
    v_opacity = opacity;
    gl_Position = get_gl_Position(position_point_into_frame(point));
}