#version 330

layout (triangles) in;
layout (triangle_strip, max_vertices = 6) out;

in vec3 verts[3];
in vec4 v_color[3];
in vec3 v_base_normal[3];

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


void emit_triangle(vec3 points[3], vec4 v_color[3], vec3 unit_normal){
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


void main(){
    // Curves are marked as ended when the handle after
    // the first anchor is set equal to that anchor
    if (verts[0] == verts[1]) return;

    // Check zero fill
    if (vec3(v_color[0].a, v_color[1].a, v_color[2].a) == vec3(0.0, 0.0, 0.0)) return;

    vec3 base_point = v_base_normal[0];
    vec3 unit_normal = v_base_normal[1];
    // Emit main triangle
    fill_all = 1.0;
    emit_triangle(
        vec3[3](base_point, verts[0], verts[2]),
        vec4[3](v_color[1], v_color[0], v_color[2]),
        unit_normal
    );
    // Edge triangle
    fill_all = 0.0;
    emit_triangle(
        vec3[3](verts[0], verts[1], verts[2]),
        vec4[3](v_color[0], v_color[1], v_color[2]),
        unit_normal
    );
}

