#version 330

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

uniform float anti_alias_width;
uniform vec2 pixel_shape;

in vec3 v_point[1];
in float v_radius[1];
in vec4 v_color[1];

out vec4 color;
out float radius;
out vec2 center;
out vec2 point;
out float scaled_aaw;

#INSERT get_gl_Position.glsl

void main() {
    color = v_color[0];
    radius = v_radius[0];
    center = v_point[0].xy;
    
    scaled_aaw = (frame_shape.y / pixel_shape.y);
    radius = v_radius[0] / max(1.0 - v_point[0].z / focal_distance / frame_shape.y, 0.0);
    float rpa = radius + scaled_aaw;

    for(int i = 0; i < 4; i++){
        // To account for perspective

        int x_index = 2 * (i % 2) - 1;
        int y_index = 2 * (i / 2) - 1;
        vec3 corner = v_point[0] + vec3(x_index * rpa, y_index * rpa, 0.0);

        gl_Position = get_gl_Position(corner);
        point = corner.xy;
        EmitVertex();
    }
    EndPrimitive();
}