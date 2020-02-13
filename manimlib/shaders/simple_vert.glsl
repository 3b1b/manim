#version 330

uniform float scale;
uniform float aspect_ratio;
uniform float anti_alias_width;
uniform vec3 frame_center;

in vec3 point;

// Analog of import for manim only
#INSERT set_gl_Position.glsl

void main(){
    set_gl_Position(point);
}