#version 330

layout (triangles) in;
layout (triangle_strip, max_vertices = 6) out;

uniform bool winding;

in vec3 verts[3];
in vec4 v_color[3];
in vec3 v_base_point[3];
in float v_vert_index[3];
in vec3 v_unit_normal[3];

out vec4 color;
out float fill_all;
out float orientation;
// uv space is where the curve coincides with y = x^2
out vec2 uv_coords;

// A quadratic bezier curve with these points coincides with y = x^2
const vec2 SIMPLE_QUADRATIC[3] = vec2[3](
    vec2(0.0, 0.0),
    vec2(0.5, 0),
    vec2(1.0, 1.0)
);

// Analog of import for manim only
#INSERT emit_gl_Position.glsl
#INSERT finalize_color.glsl


void emit_triangle(vec3 points[3], vec4 v_color[3]){
    vec3 unit_normal = v_unit_normal[1];

    orientation = sign(determinant(mat3(
        unit_normal,
        points[1] - points[0],
        points[2] - points[0]
    )));

    for(int i = 0; i < 3; i++){
        uv_coords = SIMPLE_QUADRATIC[i];
        color = finalize_color(v_color[i], points[i], unit_normal);
        emit_gl_Position(points[i]);
        EmitVertex();
    }
    EndPrimitive();
}


void emit_simple_triangle(){
    emit_triangle(
        vec3[3](verts[0], verts[1], verts[2]),
        vec4[3](v_color[0], v_color[1], v_color[2])
    );
}


void main(){
    // Curves are marked as ended when the handle after
    // the first anchor is set equal to that anchor
    if (verts[0] == verts[1]) return;

    if(winding){
        // Emit main triangle
        fill_all = 1.0;
        emit_triangle(
            vec3[3](v_base_point[0], verts[0], verts[2]),
            vec4[3](v_color[1], v_color[0], v_color[2])
        );
        // Edge triangle
        fill_all = 0.0;
        emit_simple_triangle();
    }else{
        // In this case, one should fill all if the vertices are
        // not in sequential order
        fill_all = float(
            (v_vert_index[1] - v_vert_index[0]) != 1.0 ||
            (v_vert_index[2] - v_vert_index[1]) != 1.0
        );
        emit_simple_triangle();
    }
}

