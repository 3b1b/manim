#version 330

in vec3 point;
in vec3 base_normal;

out vec3 verts;
out vec3 v_base_point;

void main(){
    verts = point;
    v_base_point = base_normal;
}