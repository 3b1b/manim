#version 330

out vec3 v_point;
out vec3 v_unit_normal;
out vec2 v_im_coords;
out float v_opacity;

#INSERT textured_surface_uniforms.glsl
#INSERT emit_gl_Position.glsl
#INSERT read_data.glsl
#INSERT surface_mesh.glsl

void main(){
    vec3 point;
    vec3 unit_normal;
    int index;
    if (!read_surface_vertex(point, unit_normal, index)){
        gl_Position = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }
    v_point = point;
    v_unit_normal = unit_normal;
    v_im_coords = read_vec2(index, DATA_OFFSET_im_coords);
    v_opacity = read_float(index, DATA_OFFSET_opacity);
    emit_gl_Position(point);
}
