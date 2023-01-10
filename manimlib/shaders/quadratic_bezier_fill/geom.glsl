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

const float ANGLE_THRESHOLD = 1e-3;


// Analog of import for manim only
#INSERT get_xy_to_uv.glsl
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


void emit_pentagon(vec3[3] points){
    vec2 p0 = points[0].xy;
    vec2 p1 = points[1].xy;
    vec2 p2 = points[2].xy;

    // Tangent vectors
    vec2 t01 = normalize(p1 - p0);
    vec2 t12 = normalize(p2 - p1);

    // Vectors perpendicular to the curve in the plane
    // of the curve pointing outside the curve
    float cross_prod = cross2d(t01, t12);
    float sgn = cross_prod >= 0.0 ? 1.0 : -1.0;
    vec2 p0_perp = sgn * vec2(t01.y, -t01.x);
    vec2 p2_perp = sgn * vec2(t12.y, -t12.x);

    float angle = asin(clamp(cross_prod, -1, 1));
    is_linear = float(abs(angle) < ANGLE_THRESHOLD);

    bool fill_inside = orientation > 0.0;
    float aaw = anti_alias_width * frame_shape.y / pixel_shape.y;
    vec2 corners[5] = vec2[5](p0, p0, p1, p2, p2);

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
    mat3 xy_to_uv = get_xy_to_uv(vec2[3](p0, p1, p2), is_linear, is_linear);
    uv_anti_alias_width = aaw * length(xy_to_uv[0].xy);

    for(int i = 0; i < 5; i++){
        int j = int(sign(i - 1) + 1);  // Maps i = [0, 1, 2, 3, 4] onto j = [0, 0, 1, 2, 2]
        vec3 corner = vec3(corners[i], points[j].z);
        uv_coords = (xy_to_uv * vec3(corners[i], 1.0)).xy;
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

    if(bool(fill_all)){
        emit_simple_triangle();
        return;
    }

    vec3[3] verts = vec3[3](bp[0], bp[1], bp[2]);
    unit_normal = get_unit_normal(verts);
    orientation = v_orientation[0];

    emit_pentagon(verts);
}

