#version 330

layout (triangles) in;
layout (triangle_strip, max_vertices = 5) out;

uniform float anti_alias_width;

// Needed for get_gl_Position
uniform vec2 frame_shape;
uniform vec2 pixel_shape;
uniform float focal_distance;
uniform float is_fixed_in_frame;
// Needed for finalize_color
uniform vec3 light_source_position;
uniform vec3 camera_position;
uniform float reflectiveness;
uniform float gloss;
uniform float shadow;

in vec3 bp[3];
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

vec3 unit_normal;


// Analog of import for manim only
#INSERT quadratic_bezier_geometry_functions.glsl
#INSERT get_gl_Position.glsl
#INSERT get_unit_normal.glsl
#INSERT finalize_color.glsl


void emit_vertex_wrapper(vec3 point, int index){
    color = finalize_color(
        v_color[index],
        point,
        unit_normal,
        light_source_position,
        camera_position,
        reflectiveness,
        gloss,
        shadow
    );
    gl_Position = get_gl_Position(point);
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

    bool fill_inside = orientation > 0.0;
    float aaw = anti_alias_width * frame_shape.y / pixel_shape.y;
    vec3 corners[5];
    if(bool(is_linear)){
        // For straight lines, buff out in both directions
        corners = vec3[5](
            p0 + aaw * p0_perp,
            p0 - aaw * p0_perp,
            p1 + 0.5 * aaw * (p0_perp + p2_perp),
            p2 - aaw * p2_perp,
            p2 + aaw * p2_perp
        );
    } else if(fill_inside){
        // If curved, and filling insight, just buff out away interior
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

    // Compute xy_to_uv matrix, and potentially re-evaluate bezier degree
    mat3 xy_to_uv = get_xy_to_uv(
        vec2[3](p0.xy, p1.xy, p2.xy),
        is_linear, is_linear
    );
    uv_anti_alias_width = aaw * length(xy_to_uv[0].xy);

    for(int i = 0; i < 5; i++){
        vec3 corner = corners[i];
        uv_coords = (xy_to_uv * vec3(corner.xy, 1.0)).xy;
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

    vec3 v01 = normalize(bp[1] - bp[0]);
    vec3 v12 = normalize(bp[2] - bp[1]);
    float angle = acos(clamp(dot(v01, v12), -1, 1));
    is_linear = float(angle < 1e-3);
    vec3[3] new_bp = vec3[3](bp[0], bp[1], bp[2]);
    unit_normal = get_unit_normal(new_bp);
    orientation = v_orientation[0];

    emit_pentagon(new_bp, unit_normal);
}

