#version 330

layout (triangles) in;
layout (triangle_strip, max_vertices = 5) out;

// Needed for get_gl_Position
uniform float aspect_ratio;
uniform float focal_distance;
uniform float anti_alias_width;

in vec3 bp[3];
in vec3 prev_bp[3];
in vec3 next_bp[3];
in vec3 v_global_unit_normal[3];

in vec4 v_color[3];
in float v_stroke_width[3];
in float v_joint_type[3];
in float v_gloss[3];

out vec4 color;
out float uv_stroke_width;
out float gloss;
out float uv_anti_alias_width;

out float has_prev;
out float has_next;
out float bevel_start;
out float bevel_end;
out float angle_from_prev;
out float angle_to_next;

out float bezier_degree;

out vec3 xyz_coords;
out vec3 global_unit_normal;
out vec2 uv_coords;
out vec2 uv_b2;

// Codes for joint types
const float AUTO_JOINT = 0;
const float ROUND_JOINT = 1;
const float BEVEL_JOINT = 2;
const float MITER_JOINT = 3;


// To my knowledge, there is no notion of #include for shaders,
// so to share functionality between this and others, the caller
// replaces this line with the contents of named file
#INSERT quadratic_bezier_geometry_functions.glsl
#INSERT get_gl_Position.glsl
#INSERT get_unit_normal.glsl


float get_aaw_scalar(vec3 normal){
    return min(abs(normal.z), 5);
}


float angle_between_vectors(vec3 v1, vec3 v2, vec3 normal){
    float v1_norm = length(v1);
    float v2_norm = length(v2);
    if(v1_norm == 0 || v2_norm == 0) return 0;
    vec3 nv1 = v1 / v1_norm;
    vec3 nv2 = v2 / v2_norm;
    // float signed_area = clamp(dot(cross(nv1, nv2), normal), -1, 1);
    // return asin(signed_area);
    float unsigned_angle = acos(clamp(dot(nv1, nv2), -1, 1));
    float sn = sign(dot(cross(nv1, nv2), normal));
    return sn * unsigned_angle;
}


bool find_intersection(vec3 p0, vec3 v0, vec3 p1, vec3 v1, vec3 normal, out vec3 intersection){
    // Find the intersection of a line passing through
    // p0 in the direction v0 and one passing through p1 in
    // the direction p1.
    // That is, find a solutoin to p0 + v0 * t = p1 + v1 * s
    // float det = -v0.x * v1.y + v1.x * v0.y;
    float det = dot(cross(v1, v0), normal);
    if(det == 0){
        // intersection = p0;
        return false;
    }
    float t = dot(cross(p0 - p1, v1), normal) / det;
    intersection = p0 + v0 * t;
    return true;
}


bool is_between(vec3 p, vec3 a, vec3 b){
    // Assumes three points fall on a line, returns whether
    // or not p sits between a and b.
    float d_pa = distance(p, a);
    float d_pb = distance(p, b);
    float d_ab = distance(a, b);
    return (d_ab >= d_pa && d_ab >= d_pb);
}


// Tries to detect if one of the corners defined by the buffer around
// b0 and b2 should be modified to form a better convex hull
bool should_motify_corner(vec3 c, vec3 from_c, vec3 o1, vec3 o2, vec3 from_o, vec3 normal, float buff){
    vec3 int1;
    vec3 int2;
    find_intersection(c, from_c, o1, from_o, normal, int1);
    find_intersection(c, from_c, o2, from_o, normal, int2);
    return !is_between(int2, c + 1 * from_c * buff, int1);
}


void create_joint(float angle, vec3 unit_tan, float buff, float should_bevel,
                  vec3 static_c0, out vec3 changing_c0,
                  vec3 static_c1, out vec3 changing_c1){
    float shift;
    float joint_type = v_joint_type[0];
    bool miter = (
        (joint_type == AUTO_JOINT && abs(angle) > 2.8 && should_bevel == 1) ||
        (joint_type == MITER_JOINT)
    );
    if(abs(angle) < 1e-3){
        // No joint
        shift = 0;
    }else if(miter){
        shift = buff * (-1.0 - cos(angle)) / sin(angle);
    }else{
        // For a Bevel joint
        shift = buff * (1.0 - cos(angle)) / sin(angle);
    }
    changing_c0 = static_c0 - shift * unit_tan;
    changing_c1 = static_c1 + shift * unit_tan;
}


// This function is responsible for finding the corners of
// a bounding region around the bezier curve, which can be
// emitted as a triangle fan
int get_corners(vec3 controls[3], vec3 normal, int degree, out vec3 corners[5]){
    vec3 p0 = controls[0];
    vec3 p1 = controls[1];
    vec3 p2 = controls[2];

    // Unit vectors for directions between control points
    vec3 v10 = normalize(p0 - p1);
    vec3 v12 = normalize(p2 - p1);
    vec3 v01 = -v10;
    vec3 v21 = -v12;

    // 
    vec3 p0_perp = cross(normal, v01);  // Pointing to the left of the curve from p0
    vec3 p2_perp = cross(normal, v12);  // Pointing to the left of the curve from p2

    // aaw is the added width given around the polygon for antialiasing.
    // In case the normal is faced away from (0, 0, 1), the vector to the
    // camera, this is scaled up.
    float aaw = anti_alias_width / get_aaw_scalar(normal);
    float buff0 = 0.5 * v_stroke_width[0] + aaw;
    float buff2 = 0.5 * v_stroke_width[2] + aaw;
    float aaw0 = (1 - has_prev) * aaw;
    float aaw2 = (1 - has_next) * aaw;

    vec3 c0 = p0 - buff0 * p0_perp + aaw0 * v10;
    vec3 c1 = p0 + buff0 * p0_perp + aaw0 * v10;
    vec3 c2 = p2 + buff2 * p2_perp + aaw2 * v12;
    vec3 c3 = p2 - buff2 * p2_perp + aaw2 * v12;

    // Account for previous and next control points
    if(has_prev > 0) create_joint(angle_from_prev, v01, buff0, bevel_start, c0, c0, c1, c1);
    if(has_next > 0) create_joint(angle_to_next, v21, buff2, bevel_end, c3, c3, c2, c2);

    // Linear case is the simplest
    if(degree == 1){
        // Swap between 2 and 3 is deliberate, the order of corners
        // should be for a triangle_strip.  Last entry is a dummy
        corners = vec3[5](c0, c1, c3, c2, vec3(0.0));
        return 4;
    }
    // Otherwise, form a pentagon around the curve
    float orientation = sign(dot(cross(v01, v12), normal));  // Positive for ccw curves
    if(orientation > 0) corners = vec3[5](c0, c1, p1, c2, c3);
    else                corners = vec3[5](c1, c0, p1, c3, c2);
    // Replace corner[2] with convex hull point accounting for stroke width
    find_intersection(corners[0], v01, corners[4], v21, normal, corners[2]);
    return 5;
}


void set_adjascent_info(vec3 c0, vec3 tangent,
                        int degree,
                        vec3 normal,
                        vec3 adj[3],
                        out float bevel,
                        out float angle
                        ){
    float joint_type = v_joint_type[0];
    vec3 new_adj[3];
    float adj_degree = get_reduced_control_points(adj, new_adj);
    // Check if adj_degree is zero?
    angle = angle_between_vectors(c0 - new_adj[1], tangent, normal);
    // Decide on joint type
    bool one_linear = (degree == 1 || adj_degree == 1.0);
    bool should_bevel = (
        (joint_type == AUTO_JOINT && one_linear) ||
        joint_type == BEVEL_JOINT
    );
    bevel = should_bevel ? 1.0 : 0.0;
}


void set_previous_and_next(vec3 controls[3], int degree, vec3 normal){
    float a_tol = 1e-8;

    // Made as floats not bools so they can be passed to the frag shader
    has_prev = float(distance(prev_bp[2], bp[0]) < a_tol);
    has_next = float(distance(next_bp[0], bp[2]) < a_tol);

    if(has_prev > 0){
        vec3 tangent = controls[1] - controls[0];
        set_adjascent_info(
            controls[0], tangent, degree, normal,
            vec3[3](prev_bp[0], prev_bp[1], prev_bp[2]),
            bevel_start, angle_from_prev
        );
    }
    if(has_next > 0){
        vec3 tangent = controls[1] - controls[2];
        set_adjascent_info(
            controls[2], tangent, degree, normal,
            vec3[3](next_bp[0], next_bp[1], next_bp[2]),
            bevel_end, angle_to_next
        );
        angle_to_next *= -1;
    }
}


void main() {
    vec3 unit_normal = v_global_unit_normal[0];
    // anti_alias_width /= cos(0.5 * acos(abs(unit_normal.z)));

    vec3 controls[3];
    bezier_degree = get_reduced_control_points(vec3[3](bp[0], bp[1], bp[2]), controls);
    int degree = int(bezier_degree);

    // Null curve
    if(degree == 0) return;

    set_previous_and_next(controls, degree, unit_normal);

    // Find uv conversion matrix
    mat4 xyz_to_uv = get_xyz_to_uv(controls[0], controls[1], unit_normal);
    float scale_factor = length(controls[1] - controls[0]);
    uv_anti_alias_width = anti_alias_width / scale_factor / get_aaw_scalar(unit_normal);
    uv_b2 = (xyz_to_uv * vec4(controls[2], 1.0)).xy;

    // Corners of a bounding region around curve
    vec3 corners[5];
    int n_corners = get_corners(controls, unit_normal, degree, corners);

    int index_map[5] = int[5](0, 0, 1, 2, 2);
    if(n_corners == 4) index_map[2] = 2;

    // Emit each corner
    for(int i = 0; i < n_corners; i++){
        xyz_coords = corners[i];
        uv_coords = (xyz_to_uv * vec4(xyz_coords, 1.0)).xy;
        uv_stroke_width = v_stroke_width[index_map[i]] / scale_factor;
        color = v_color[index_map[i]];
        gloss = v_gloss[index_map[i]];
        global_unit_normal = v_global_unit_normal[index_map[i]];
        gl_Position = get_gl_Position(xyz_coords);
        EmitVertex();
    }
    EndPrimitive();
}