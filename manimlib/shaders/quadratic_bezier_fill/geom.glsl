#version 330

layout (triangles) in;
layout (triangle_strip, max_vertices = 5) out;

uniform float anti_alias_width;
uniform float pixel_size;

in vec3 verts[3];
in float v_orientation[3];
in vec4 v_color[3];
in float v_vert_index[3];

out vec4 color;
out float fill_all;
out float uv_anti_alias_width;

out float orientation;
// uv space is where the curve coincides with y = x^2
out vec2 uv_coords;
out float is_linear;

const float ANGLE_THRESHOLD = 1e-3;


// Analog of import for manim only
#INSERT get_gl_Position.glsl
#INSERT get_xyz_to_uv.glsl
#INSERT finalize_color.glsl


void emit_vertex_wrapper(vec3 point, int index, vec3 unit_normal){
    color = finalize_color(v_color[index], point, unit_normal);
    gl_Position = get_gl_Position(point);
    EmitVertex();
}


void emit_simple_triangle(vec3 unit_normal){
    for(int i = 0; i < 3; i++){
        emit_vertex_wrapper(verts[i], i, unit_normal);
    }
    EndPrimitive();
}


void emit_pentagon(
    // Triangle vertices
    vec3 p0,
    vec3 p1,
    vec3 p2,
    // Unit tangent vector
    vec3 t01,
    vec3 t12,
    vec3 unit_normal
){
    // Vectors perpendicular to the curve in the plane of the curve
    // pointing outside the curve
    vec3 p0_perp = cross(t01, unit_normal);
    vec3 p2_perp = cross(t12, unit_normal);

    float angle = acos(clamp(dot(t01, t12), -1, 1));
    is_linear = float(angle < ANGLE_THRESHOLD);

    bool fill_inside = orientation > 0.0;
    float aaw = anti_alias_width * pixel_size;
    vec3 corners[5] = vec3[5](p0, p0, p1, p2, p2);

    if(fill_inside || bool(is_linear)){
        // Add buffer outside the curve
        corners[0] += aaw * p0_perp;
        corners[2] += 0.5 * aaw * (p0_perp + p2_perp);
        corners[4] += aaw * p2_perp;
    }
    if(!fill_inside || bool(is_linear)){
        // Add buffer inside the curve
        corners[1] -= aaw * p0_perp;
        corners[3] -= aaw * p2_perp;
    }

    // Compute xy_to_uv matrix, and potentially re-evaluate bezier degree
    mat4 xyz_to_uv = get_xyz_to_uv(p0, p1, p2, is_linear, is_linear);
    uv_anti_alias_width = aaw * length(xyz_to_uv[0].xyz);

    for(int i = 0; i < 5; i++){
        int j = int(sign(i - 1) + 1);  // Maps i = [0, 1, 2, 3, 4] onto j = [0, 0, 1, 2, 2]
        vec3 corner = corners[i];
        uv_coords = (xyz_to_uv * vec4(corner, 1.0)).xy;
        emit_vertex_wrapper(corner, j, unit_normal);
    }
    EndPrimitive();
}


void main(){
    // If vert indices are sequential, don't fill all
    fill_all = float(
        (v_vert_index[1] - v_vert_index[0]) != 1.0 ||
        (v_vert_index[2] - v_vert_index[1]) != 1.0
    );

    vec3 p0 = verts[0];
    vec3 p1 = verts[1];
    vec3 p2 = verts[2];
    vec3 t01 = p1 - p0;
    vec3 t12 = p2 - p1;
    vec3 unit_normal = normalize(cross(t01, t12));

    if(bool(fill_all)){
        emit_simple_triangle(unit_normal);
        return;
    }
    orientation = v_orientation[1];

    emit_pentagon(
        p0, p1, p2,
        normalize(t01),
        normalize(t12),
        unit_normal
    );
}

