#version 330

layout (triangles) in;
layout (triangle_strip, max_vertices = 6) out;

in vec3 verts[3];
in vec3 v_base_point[3];

out float depth;

#INSERT emit_gl_Position.glsl


void emit_triangle(vec3 points[3]){
    for(int i = 0; i < 3; i++){
        emit_gl_Position(points[i]);
        EmitVertex();
    }
    EndPrimitive();
}


void main(){
    // Curves are marked as ended when the handle after
    // the first anchor is set equal to that anchor
    if (verts[0] == verts[1]) return;

    // Emit two triangles
    emit_triangle(vec3[3](v_base_point[0], verts[0], verts[2]));
    emit_triangle(vec3[3](verts[0], verts[1], verts[2]));
}

