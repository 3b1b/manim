#version 330

uniform vec2 frame_shape;
uniform float anti_alias_width;
uniform mat4 to_screen_space;
uniform float is_fixed_in_frame;
uniform float focal_distance;

in vec3 point;
in float radius;
in vec4 color;

out vec3 v_point;
out float v_radius;
out vec4 v_color;

#INSERT position_point_into_frame.glsl

void main(){
    v_point = position_point_into_frame(point);
    v_radius = radius;
    v_color = color;
}