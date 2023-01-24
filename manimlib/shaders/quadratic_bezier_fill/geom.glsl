#version 330

layout (triangles) in;
layout (triangle_strip, max_vertices = 3) out;

uniform float anti_alias_width;
uniform float pixel_size;
uniform vec3 corner;

in vec3 verts[3];
in vec4 v_color[3];
in vec3 v_base_point[3];
in float v_vert_index[3];
in float v_inst_id[3];

out vec4 color;
out float fill_all;
// uv space is where the curve coincides with y = x^2
out vec2 uv_coords;


// Analog of import for manim only
#INSERT get_gl_Position.glsl
#INSERT get_unit_normal.glsl
#INSERT finalize_color.glsl


void emit_vertex_wrapper(vec3 point, vec4 v_color, vec3 unit_normal){
    color = finalize_color(v_color, point, unit_normal);
    gl_Position = get_gl_Position(point);
    EmitVertex();
}


void main(){
    // We use the triangle strip primative, but
    // actually only need every other strip element
    if (int(v_vert_index[0]) % 2 == 1) return;

    // Curves are marked as ended when the handle after
    // the first anchor is set equal to that anchor
    if (verts[0] == verts[1]) return;

    if (v_color[0].a == 0 && v_color[1].a == 0 && v_color[2].a == 0) return;

    vec3 unit_normal = get_unit_normal(verts[0], verts[1], verts[2]);

    if(int(v_inst_id[0]) % 2 == 0){
        // Emit main triangle
        fill_all = 1.0;
        uv_coords = vec2(0.0);
        emit_vertex_wrapper(v_base_point[0], v_color[0], unit_normal);
        emit_vertex_wrapper(verts[0], v_color[0], unit_normal);
        emit_vertex_wrapper(verts[2], v_color[2], unit_normal);
    }else{
        // Emit edge triangle
        fill_all = 0.0;
        // A quadratic bezier curve with these points coincides with y = x^2
        vec2 uv_coords_arr[3] = vec2[3](
            vec2(0.0, 0.0),
            vec2(0.5, 0),
            vec2(1.0, 1.0)
        );
        for(int i = 0; i < 3; i ++){
            uv_coords = uv_coords_arr[i];
            emit_vertex_wrapper(verts[i], v_color[i], unit_normal);
        }
    }
    EndPrimitive();
}

