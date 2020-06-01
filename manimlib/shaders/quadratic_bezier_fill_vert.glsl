#version 330

uniform mat4 to_screen_space;
uniform float focal_distance;

in vec3 point;
in vec4 color;
in float fill_all;  // Either 0 or 1

out vec3 bp;  // Bezier control point
out vec4 v_color;
out float v_fill_all;

// To my knowledge, there is no notion of #include for shaders,
// so to share functionality between this and others, the caller
// replaces this line with the contents of named file
#INSERT position_point_into_frame.glsl

void main(){
    bp = position_point_into_frame(point);
    v_color = color;
    v_fill_all = fill_all;
}