#version 330

in vec3 point;
in vec4 fill_rgba;
in vec3 base_normal;

out vec3 verts;  // Bezier control point
out vec4 v_color;
out vec3 v_base_normal;

void main(){
    verts = point;
    v_color = fill_rgba;
    v_base_normal = base_normal;
}