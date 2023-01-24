#version 330

in vec3 point;
in vec4 fill_rgba;
in vec3 base_point;

out vec3 verts;  // Bezier control point
out vec4 v_joint_product;
out vec4 v_color;
out vec3 v_base_point;
out float v_vert_index;
out float v_inst_id;

void main(){
    verts = point;
    v_color = fill_rgba;
    v_base_point = base_point;
    v_vert_index = gl_VertexID;
    v_inst_id = gl_InstanceID;
}