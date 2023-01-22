#version 330

uniform float pixel_size;
uniform float anti_alias_width;

in vec3 point;
in float radius;
in vec4 rgba;

out vec4 color;
out float scaled_aaw;
out vec3 v_point;
out vec3 light_pos;

#INSERT get_gl_Position.glsl

void main(){
    v_point = point;
    color = rgba;
    scaled_aaw = (anti_alias_width * pixel_size) / radius;

    gl_Position = get_gl_Position(point);
    float z = -10 * gl_Position.z;
    float scaled_radius = radius * 1.0 / (1.0 - z);
    gl_PointSize = 2 * ((scaled_radius / pixel_size) + anti_alias_width);
}