#version 330

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

uniform float pixel_size;
uniform float anti_alias_width;
uniform float frame_scale;
uniform vec3 camera_position;

in vec3 v_point[1];
in float v_radius[1];
in vec4 v_rgba[1];

out vec4 color;
out float scaled_aaw;
out vec3 point;
out vec3 to_cam;
out vec3 center;
out float radius;
out vec2 uv_coords;

#INSERT emit_gl_Position.glsl

void main(){
    color = v_rgba[0];
    radius = v_radius[0];
    center = v_point[0];
    scaled_aaw = (anti_alias_width * pixel_size) / v_radius[0];

    to_cam = normalize(camera_position - v_point[0]);
    vec3 right = v_radius[0] * normalize(cross(vec3(0, 1, 1), to_cam));
    vec3 up = v_radius[0] * normalize(cross(to_cam, right));

    for(int i = -1; i < 2; i += 2){
        for(int j = -1; j < 2; j += 2){
            point = v_point[0] + i * right + j * up;
            uv_coords = vec2(i, j);
            emit_gl_Position(point);
            EmitVertex();
        }
    }
    EndPrimitive();
}