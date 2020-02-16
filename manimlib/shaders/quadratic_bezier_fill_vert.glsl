#version 330

in vec3 point;
in vec4 color;
// fill_all is 0 or 1
in float fill_all;
// orientation is +1 for counterclockwise curves, -1 otherwise
in float orientation;

out vec3 bp;  // Bezier control point
out vec4 v_color;
out float v_fill_all;
out float v_orientation;


#INSERT rotate_point_for_frame.glsl


void main(){
    bp = rotate_point_for_frame(point);
    v_color = color;
    v_fill_all = fill_all;
    v_orientation = orientation;
}