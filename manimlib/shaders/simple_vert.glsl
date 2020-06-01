#version 330

uniform float aspect_ratio;
uniform float anti_alias_width;
uniform mat4 to_screen_space;
uniform float focal_distance;

in vec3 point;

// Analog of import for manim only
#INSERT get_gl_Position.glsl
#INSERT position_point_into_frame.glsl

void main(){
    gl_Position = get_gl_Position(position_point_into_frame(point));
}