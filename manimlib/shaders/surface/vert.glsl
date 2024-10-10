#version 330

in vec3 point;
in vec3 du_point;
in vec3 dv_point;
in vec4 rgba;

out vec4 v_color;

#INSERT emit_gl_Position.glsl
#INSERT get_unit_normal.glsl
#INSERT finalize_color.glsl

void main(){
    emit_gl_Position(point);
    vec3 normal = cross(normalize(du_point - point), normalize(dv_point - point));
    v_color = finalize_color(rgba, point, normalize(normal));
}