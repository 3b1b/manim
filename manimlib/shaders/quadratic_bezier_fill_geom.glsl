#version 330

layout (triangles) in;
layout (triangle_strip, max_vertices = 5) out;

uniform float scale;
uniform float aspect_ratio;
uniform float anti_alias_width;
uniform vec3 frame_center;

in vec2 bp[3];
in vec4 v_color[3];
in float v_fill_all[3];
in float v_orientation[3];

out vec4 color;
out float fill_type;
out float uv_anti_alias_width;

// uv space is where b0 = (0, 0), b1 = (1, 0), and transform is orthogonal
out vec2 uv_coords;
out vec2 uv_b2;
// wz space is where b0 = (0, 0), b1 = (0.5, 0), b2 = (1, 1)
out vec2 wz_coords;

out float bezier_degree;

const float FILL_INSIDE = 0;
const float FILL_OUTSIDE = 1;
const float FILL_ALL = 2;

const float SQRT5 = 2.236068;


// To my knowledge, there is no notion of #include for shaders,
// so to share functionality between this and others, the caller
// replaces this line with the contents of named file
#INSERT quadratic_bezier_geometry_functions.glsl


mat3 get_xy_to_wz(vec2 b0, vec2 b1, vec2 b2){
    // If linear or null, this matrix is not needed
    if(bezier_degree < 2) return mat3(1.0);

    vec2 inv_col1 = 2 * (b1 - b0);
    vec2 inv_col2 = b2 - 2 * b1 + b0;
    float inv_det = cross(inv_col1, inv_col2);

    mat3 transform = mat3(
        inv_col2.y, -inv_col1.y, 0,
        -inv_col2.x, inv_col1.x, 0,
        0, 0, inv_det
    ) / inv_det;

    mat3 shift = mat3(
        1, 0, 0,
        0, 1, 0,
        -b0.x, -b0.y, 1
    );
    return transform * shift;
}

void set_gl_Position(vec2 p){
    vec2 result = p / scale;
    result.x /= aspect_ratio;
    result -= frame_center.xy;
    gl_Position = vec4(result, 0.0, 1.0);
}


void emit_simple_triangle(){
    for(int i = 0; i < 3; i++){
        color = v_color[i];
        set_gl_Position(bp[i]);
        EmitVertex();
    }
    EndPrimitive();
}


void emit_pentagon(vec2 bp0, vec2 bp1, vec2 bp2, float orientation){
    // Tangent vectors
    vec2 t01 = normalize(bp1 - bp0);
    vec2 t12 = normalize(bp2 - bp1);

    // Inside and left turn -> rot right -> -1
    // Outside and left turn -> rot left -> +1
    // Inside and right turn -> rot left -> +1
    // Outside and right turn -> rot right -> -1
    float c_orient = (cross(t01, t12) > 0) ? 1 : -1;
    c_orient *= orientation;

    bool fill_in = (c_orient > 0);
    fill_type = fill_in ? FILL_INSIDE : FILL_OUTSIDE;

    // float orient = in_or_out * c_orient;

    // Normal vectors
    // Rotate tangent vector 90-degrees clockwise
    // if the curve is positively oriented, otherwise
    // rotate it 90-degrees counterclockwise
    vec2 n01 = orientation * vec2(t01.y, -t01.x);
    vec2 n12 = orientation * vec2(t12.y, -t12.x);

    float aaw = anti_alias_width;
    vec2 nudge1 = fill_in ? 0.5 * aaw * (n01 + n12) : vec2(0);
    vec2 corners[5] = vec2[5](
        bp0 + aaw * n01,
        bp0,
        bp1 + nudge1,
        bp2,
        bp2 + aaw * n12
    );

    int coords_index_map[5] = int[5](0, 1, 2, 3, 4);
    if(!fill_in) coords_index_map = int[5](1, 0, 2, 4, 3);
        
    mat3 xy_to_uv = get_xy_to_uv(bp0, bp1);
    mat3 xy_to_wz = get_xy_to_wz(bp0, bp1, bp2);
    uv_b2 = (xy_to_uv * vec3(bp2, 1)).xy;
    uv_anti_alias_width = anti_alias_width / length(bp1 - bp0);

    for(int i = 0; i < 5; i++){
        vec2 corner = corners[coords_index_map[i]];
        uv_coords = (xy_to_uv * vec3(corner, 1)).xy;
        wz_coords = (xy_to_wz * vec3(corner, 1)).xy;
        // I haven't a clue why an index map doesn't work just
        // as well here, but for some reason it doesn't.
        if(i < 2)       color = v_color[0];
        else if(i == 2) color = v_color[1];
        else            color = v_color[2];
        set_gl_Position(corner);
        EmitVertex();
    }
    EndPrimitive();
}


void main(){
    float fill_all = v_fill_all[0];

    if(fill_all == 1){
        fill_type = FILL_ALL;
        emit_simple_triangle();
    }else{
        vec2 new_bp[3];
        int n = get_reduced_control_points(bp[0], bp[1], bp[2], new_bp);
        bezier_degree = float(n);
        float orientation = v_orientation[0];

        vec2 bp0, bp1, bp2;
        if(n == 0){
            return;  // Don't emit any vertices
        }
        else if(n == 1){
            bp0 = new_bp[0];
            bp2 = new_bp[1];
            bp1 = 0.5 * (bp0 + bp2);
        }else{
            bp0 = new_bp[0];
            bp1 = new_bp[1];
            bp2 = new_bp[2];
        }

        emit_pentagon(bp0, bp1, bp2, orientation);
    }
}

