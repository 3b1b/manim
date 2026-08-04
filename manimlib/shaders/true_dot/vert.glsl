#version 330

out vec4 color;
out float scaled_aaw;
out vec3 point;
out vec3 to_cam;
out vec3 center;
out float radius;
out vec2 uv_coords;

#INSERT dot_cloud_uniforms.glsl
#INSERT emit_gl_Position.glsl
#INSERT read_data.glsl

// Each dot is drawn as a quad facing the camera, so two triangles of corners
const vec2 CORNERS[6] = vec2[6](
    vec2(-1, -1), vec2(-1, 1), vec2(1, -1),
    vec2(1, -1), vec2(-1, 1), vec2(1, 1)
);

void main(){
    int dot_index = gl_VertexID / 6;
    vec2 corner = CORNERS[gl_VertexID % 6];

    center = read_vec3(dot_index, DATA_OFFSET_point);
    radius = read_float(dot_index, DATA_OFFSET_radius);
    color = read_vec4(dot_index, DATA_OFFSET_rgba);

    scaled_aaw = (anti_alias_width * get_pixel_unit_size()) / radius;

    to_cam = normalize(camera_position - center);
    vec3 right = radius * normalize(cross(vec3(0, 1, 1), to_cam));
    vec3 up = radius * normalize(cross(to_cam, right));

    uv_coords = corner;
    point = center + corner.x * right + corner.y * up;
    emit_gl_Position(point);
}
