#version 330

out vec4 v_color;

#INSERT surface_uniforms.glsl
#INSERT emit_gl_Position.glsl
#INSERT read_data.glsl
#INSERT surface_mesh.glsl
#INSERT finalize_color.glsl

void main(){
    vec3 point;
    vec3 unit_normal;
    int index;
    if (!read_surface_vertex(point, unit_normal, index)){
        gl_Position = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }
    emit_gl_Position(point);
    v_color = finalize_color(read_vec4(index, DATA_OFFSET_rgba), point, unit_normal);
}
