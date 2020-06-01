#version 330

in vec3 point;
in vec4 color;
in float fill_all;  // Either 0 or 1

out vec3 bp;  // Bezier control point
out vec4 v_color;
out float v_fill_all;

#INSERT rotate_point_for_frame.glsl

void main(){
    bp = rotate_point_for_frame(point);
    v_color = color;
    v_fill_all = fill_all;
}