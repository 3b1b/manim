#version 330

layout (triangles) in;
layout (triangle_strip, max_vertices = 5) out;

uniform float anti_alias_width;
// Needed for get_gl_Position
uniform float aspect_ratio;
uniform float focal_distance;

in vec3 bp[3];
in vec4 v_color[3];
in float v_fill_all[3];
in float v_gloss[3];

out vec4 color;
out float fill_all;
out float uv_anti_alias_width;

out vec3 xyz_coords;
out vec3 unit_normal;
// uv space is where b0 = (0, 0), b1 = (1, 0), and transform is orthogonal
out vec2 uv_coords;
out vec2 uv_b2;
out float bezier_degree;
out float gloss;

// To my knowledge, there is no notion of #include for shaders,
// so to share functionality between this and others, the caller
// in manim replaces this line with the contents of named file
#INSERT quadratic_bezier_geometry_functions.glsl
#INSERT get_gl_Position.glsl
#INSERT get_unit_normal.glsl

void emit_simple_triangle(){
    for(int i = 0; i < 3; i++){
        color = v_color[i];
        gloss = v_gloss[i];
        xyz_coords = bp[i];
        gl_Position = get_gl_Position(bp[i]);
        EmitVertex();
    }
    EndPrimitive();
}


void emit_pentagon(vec3[3] points, vec3 normal){
    vec3 p0 = points[0];
    vec3 p1 = points[1];
    vec3 p2 = points[2];
    // Tangent vectors
    vec3 t01 = normalize(p1 - p0);
    vec3 t12 = normalize(p2 - p1);
    // Vectors normal to the curve in the plane of the curve
    vec3 n01 = cross(t01, normal);
    vec3 n12 = cross(t12, normal);

    // Assume you always fill in to the left of the curve
    float orient = sign(dot(cross(t01, t12), normal));
    bool fill_in = (orient > 0);

    float aaw = anti_alias_width / normal.z;
    vec3 nudge1 = fill_in ? 0.5 * aaw * (n01 + n12) : vec3(0);
    vec3 corners[5] = vec3[5](
        p0 + aaw * n01,
        p0,
        p1 + nudge1,
        p2,
        p2 + aaw * n12
    );

    int coords_index_map[5] = int[5](0, 1, 2, 3, 4);
    if(!fill_in) coords_index_map = int[5](1, 0, 2, 4, 3);
        
    mat4 xyz_to_uv = get_xyz_to_uv(p0, p1, normal);
    uv_b2 = (xyz_to_uv * vec4(p2, 1)).xy;
    uv_anti_alias_width = anti_alias_width / length(p1 - p0);

    for(int i = 0; i < 5; i++){
        vec3 corner = corners[coords_index_map[i]];
        xyz_coords = corner;
        uv_coords = (xyz_to_uv * vec4(corner, 1)).xy;
        // I haven't a clue why an index map doesn't work just
        // as well here, but for some reason it doesn't.
        int j = int(sign(i - 1) + 1);  // Maps 0, 1, 2, 3, 4 onto 0, 0, 1, 2, 2
        color = v_color[j];
        gloss = v_gloss[j];
        gl_Position = get_gl_Position(corner);
        EmitVertex();
    }
    EndPrimitive();
}


void main(){
    fill_all = v_fill_all[0];
    unit_normal = get_unit_normal(bp[0], bp[1], bp[2]);

    if(fill_all == 1){
        emit_simple_triangle();
        return;
    }

    vec3 new_bp[3];
    bezier_degree = get_reduced_control_points(vec3[3](bp[0], bp[1], bp[2]), new_bp);
    if(bezier_degree == 0) return;  // Don't emit any vertices
    emit_pentagon(new_bp, unit_normal);
}

