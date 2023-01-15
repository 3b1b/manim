#version 330

in vec3 point;
in float orientation;
in vec4 color;
in float vert_index;

out vec3 verts;  // Bezier control point
out float v_orientation;
out vec4 v_color;
out float v_vert_index;

// Analog of import for manim only
#INSERT get_gl_Position.glsl

void main(){
    verts = position_point_into_frame(point);
    v_orientation = orientation;
    v_color = color;
    v_vert_index = vert_index;
}