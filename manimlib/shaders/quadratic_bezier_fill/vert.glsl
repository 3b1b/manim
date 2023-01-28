#version 330

in vec3 point;
in vec4 fill_rgba;
in vec3 base_point;
in vec3 unit_normal;

out vec3 verts;  // Bezier control point
out vec4 v_color;
out vec3 v_base_point;
out vec3 v_unit_normal;
out float v_vert_index;

void main(){
    verts = point;
    v_color = fill_rgba;
    v_base_point = base_point;
    v_unit_normal = unit_normal;
    v_vert_index = gl_VertexID;
}