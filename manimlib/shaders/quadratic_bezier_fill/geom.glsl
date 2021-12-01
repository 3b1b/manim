#version 330

layout (triangles) in;
layout (triangle_strip, max_vertices = 5) out;

uniform float anti_alias_width;

// Needed for get_gl_Position
uniform vec2 frame_shape;
uniform float focal_distance;
uniform float is_fixed_in_frame;
// Needed for finalize_color
uniform vec3 light_source_position;
uniform vec3 camera_position;
uniform float reflectiveness;
uniform float gloss;
uniform float shadow;

in vec3 bp[3];
in vec3 v_global_unit_normal[3];
in vec4 v_color[3];
in float v_vert_index[3];

out vec4 color;
out float fill_all;
out float uv_anti_alias_width;

out vec3 xyz_coords;
out float orientation;
// uv space is where b0 = (0, 0), b1 = (1, 0), and transform is orthogonal
out vec2 uv_coords;
out vec2 uv_b2;
out float bezier_degree;


// Analog of import for manim only
#INSERT quadratic_bezier_geometry_functions.glsl
#INSERT get_gl_Position.glsl
#INSERT get_unit_normal.glsl
#INSERT finalize_color.glsl


void emit_vertex_wrapper(vec3 point, int index){
    color = finalize_color(
        v_color[index],
        point,
        v_global_unit_normal[index],
        light_source_position,
        camera_position,
        reflectiveness,
        gloss,
        shadow
    );
    xyz_coords = point;
    gl_Position = get_gl_Position(xyz_coords);
    EmitVertex();
}


void emit_simple_triangle(){
    for(int i = 0; i < 3; i++){
        emit_vertex_wrapper(bp[i], i);
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
    // Vectors perpendicular to the curve in the plane of the curve pointing outside the curve
    vec3 p0_perp = cross(t01, normal);
    vec3 p2_perp = cross(t12, normal);

    bool fill_inside = orientation > 0;
    float aaw = anti_alias_width;
    vec3 corners[5];
    if(fill_inside){
        // Note, straight lines will also fall into this case, and since p0_perp and p2_perp
        // will point to the right of the curve, it's just what we want
        corners = vec3[5](
            p0 + aaw * p0_perp,
            p0,
            p1 + 0.5 * aaw * (p0_perp + p2_perp),
            p2,
            p2 + aaw * p2_perp
        );
    }else{
        corners = vec3[5](
            p0,
            p0 - aaw * p0_perp,
            p1,
            p2 - aaw * p2_perp,
            p2
        );
    }

    mat4 xyz_to_uv = get_xyz_to_uv(p0, p1, normal);
    uv_b2 = (xyz_to_uv * vec4(p2, 1)).xy;
    uv_anti_alias_width = anti_alias_width / length(p1 - p0);

    for(int i = 0; i < 5; i++){
        vec3 corner = corners[i];
        uv_coords = (xyz_to_uv * vec4(corner, 1)).xy;
        int j = int(sign(i - 1) + 1);  // Maps i = [0, 1, 2, 3, 4] onto j = [0, 0, 1, 2, 2]
        emit_vertex_wrapper(corner, j);
    }
    EndPrimitive();
}


void main(){
    // If vert indices are sequential, don't fill all
    fill_all = float(
        (v_vert_index[1] - v_vert_index[0]) != 1.0 ||
        (v_vert_index[2] - v_vert_index[1]) != 1.0
    );

    if(fill_all == 1.0){
        emit_simple_triangle();
        return;
    }

    vec3 new_bp[3];
    bezier_degree = get_reduced_control_points(vec3[3](bp[0], bp[1], bp[2]), new_bp);
    vec3 local_unit_normal = get_unit_normal(new_bp);
    orientation = sign(dot(v_global_unit_normal[0], local_unit_normal));

    if(bezier_degree >= 1){
        emit_pentagon(new_bp, local_unit_normal);
    }
    // Don't emit any vertices for bezier_degree 0
}

