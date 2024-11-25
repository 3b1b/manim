#version 330

in vec3 point;
in vec3 du_point;
in vec3 dv_point;
in vec4 rgba;

out vec4 v_color;

#INSERT emit_gl_Position.glsl
#INSERT get_unit_normal.glsl
#INSERT finalize_color.glsl

const float EPSILON = 1e-10;

void main(){
    emit_gl_Position(point);
    vec3 du = (du_point - point);
    vec3 dv = (dv_point - point);
    vec3 normal = cross(du, dv);
    float mag = length(normal);
    vec3 unit_normal = (mag < EPSILON) ? vec3(0, 0, sign(point.z)) : normal / mag;
    v_color = finalize_color(rgba, point, unit_normal);
}