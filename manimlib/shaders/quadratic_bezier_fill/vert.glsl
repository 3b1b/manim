#version 330

uniform mat4 to_screen_space;
uniform float is_fixed_in_frame;

in vec3 point;
in vec3 unit_normal;
in vec4 color;
in float vert_index;

out vec3 bp;  // Bezier control point
out vec3 v_global_unit_normal;
out vec4 v_color;
out float v_vert_index;

// Analog of import for manim only
#INSERT position_point_into_frame.glsl

void main(){
    bp = position_point_into_frame(point);
    v_global_unit_normal = normalize(to_screen_space * vec4(unit_normal, 0)).xyz;
    v_color = color;
    v_vert_index = vert_index;
}