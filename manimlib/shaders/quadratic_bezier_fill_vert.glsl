#version 330

in vec3 point;
in vec4 color;
in float fill_type;

out vec2 bp;  // Bezier control point
out vec4 v_color;
out float v_fill_type;


void main(){
    bp = point.xy;  // TODO
    v_color = color;
    v_fill_type = fill_type;
}