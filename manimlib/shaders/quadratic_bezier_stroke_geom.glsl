#version 330

layout (triangles) in;
layout (triangle_strip, max_vertices = 5) out;

uniform float scale;
uniform float aspect_ratio;
uniform float anti_alias_width;
uniform vec3 frame_center;

in vec2 bp[3];
in vec2 prev_bp[3];
in vec2 next_bp[3];

in vec4 v_color[3];
in float v_stroke_width[3];
in float v_joint_type[3];

out vec4 color;
out float uv_stroke_width;
out float uv_anti_alias_width;

out float has_prev;
out float has_next;
out float bevel_start;
out float bevel_end;
out float angle_from_prev;
out float angle_to_next;

out float bezier_degree;

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
#INSERT set_gl_Position.glsl


float angle_between_vectors(vec2 v1, vec2 v2){
    vec2 nv1 = normalize(v1);
    vec2 nv2 = normalize(v2);
    float unsigned_angle = acos(clamp(dot(nv1, nv2), -1, 1));
    float sn = sign(cross(nv1, nv2));
    return sn * unsigned_angle;
}


bool find_intersection(vec2 p0, vec2 v0, vec2 p1, vec2 v1, out vec2 intersection){
    // Find the intersection of a line passing through
    // p0 in the direction v0 and one passing through p1 in
    // the direction p1.
    // That is, find a solutoin to p0 + v0 * t = p1 + v1 * s
    // float det = -v0.x * v1.y + v1.x * v0.y;
    float det = cross(v1, v0);
    if(det == 0){
        // intersection = p0;
        return false;
    }
    float t = cross(p0 - p1, v1) / det;
    intersection = p0 + v0 * t;
    return true;
}


bool is_between(vec2 p, vec2 a, vec2 b){
    // Assumes three points fall on a line, returns whether
    // or not p sits between a and b.
    float d_pa = distance(p, a);
    float d_pb = distance(p, b);
    float d_ab = distance(a, b);
    return (d_ab >= d_pa && d_ab >= d_pb);
}


// Tries to detect if one of the corners defined by the buffer around
// b0 and b2 should be modified to form a better convex hull
bool should_motify_corner(vec2 c, vec2 from_c, vec2 o1, vec2 o2, vec2 from_o, float buff){
    vec2 int1;
    vec2 int2;
    find_intersection(c, from_c, o1, from_o, int1);
    find_intersection(c, from_c, o2, from_o, int2);
    return !is_between(int2, c + 1 * from_c * buff, int1);
}


void create_joint(float angle, vec2 unit_tan, float buff, float should_bevel,
                  vec2 static_c0, out vec2 changing_c0,
                  vec2 static_c1, out vec2 changing_c1){
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
int get_corners(vec2 controls[3], int degree, out vec2 corners[5]){
    // Unit vectors for directions between
    // Various control points
    vec2 v02, v20, v10, v01, v12, v21;

    vec2 p0 = controls[0];
    vec2 p2 = controls[degree];
    v02 = normalize(p2 - p0);
    v20 = -v02;
    if(degree == 2){
        v10 = normalize(p0 - controls[1]);
        v12 = normalize(p2 - controls[1]);
    }else{
        v10 = v20;
        v12 = v02;
    }
    v01 = -v10;
    v21 = -v12;

    // Find bounding points around ends
    vec2 p0_perp = vec2(-v01.y, v01.x);
    vec2 p2_perp = vec2(-v21.y, v21.x);

    float buff0 = 0.5 * v_stroke_width[0] + anti_alias_width;
    float buff2 = 0.5 * v_stroke_width[2] + anti_alias_width;
    float aaw0 = (1 - has_prev) * anti_alias_width;
    float aaw2 = (1 - has_next) * anti_alias_width;

    vec2 c0 = p0 - buff0 * p0_perp + aaw0 * v10;
    vec2 c1 = p0 + buff0 * p0_perp + aaw0 * v10;
    vec2 c2 = p2 - p2_perp * buff2 + aaw2 * v12;
    vec2 c3 = p2 + p2_perp * buff2 + aaw2 * v12;

    // Account for previous and next control points
    if(has_prev == 1){
        create_joint(angle_from_prev, v01, buff0, bevel_start, c0, c0, c1, c1);
    }
    if(has_next == 1){
        create_joint(-angle_to_next, v21, buff2, bevel_end, c2, c2, c3, c3);
    }

    // Linear case is the simplets
    if(degree == 1){
        // Swap between 2 and 3 is deliberate, the order of corners
        // should be for a triangle_strip.  Last entry is a dummy
        corners = vec2[5](c0, c1, c3, c2, vec2(0.0));
        return 4;
    }

    // Some admitedly complicated logic to (hopefully efficiently)
    // make sure corners forms a convex hull around the curve.
    if(cross(v10, v12) > 0){
        bool change_c0 = (
            // has_prev == 0 &&
            dot(v21, v20) > 0 &&
            should_motify_corner(c0, v01, c2, c3, v21, buff0)
        );
        if(change_c0) c0 = p0 + p2_perp * buff0;

        bool change_c3 = (
            // has_next == 0 &&
            dot(v01, v02) > 0 &&
            should_motify_corner(c3, v21, c1, c0, v01, buff2)
        );
        if(change_c3) c3 = p2 - p0_perp * buff2;

        vec2 i12;
        find_intersection(c1, v01, c2, v21, i12);
        corners = vec2[5](c1, c0, i12, c3, c2);
    }else{
        bool change_c1 = (
            // has_prev == 0 &&
            dot(v21, v20) > 0 &&
            should_motify_corner(c1, v01, c3, c2, v21, buff0)
        );
        if(change_c1) c1 = p0 - p2_perp * buff0;

        bool change_c2 = (
            // has_next == 0 &&
            dot(v01, v02) > 0 &&
            should_motify_corner(c2, v21, c0, c1, v01, buff2)
        );
        if(change_c2) c2 = p2 + p0_perp * buff2;

        vec2 i03;
        find_intersection(c0, v01, c3, v21, i03);
        corners = vec2[5](c0, c1, i03, c2, c3);
    }
    return 5;
}


void set_adjascent_info(vec2 c0, vec2 tangent,
                        int degree, int mult, int flip,
                        vec2 adj[3],
                        out float has,
                        out float bevel,
                        out float angle
                        ){
    float joint_type = v_joint_type[0];

    has = 0;
    bevel = 0;
    angle = 0;

    vec2 new_adj[3];
    int adj_degree = get_reduced_control_points(
        adj[0], adj[1], adj[2], new_adj
    );
    has = float(adj_degree > 0);
    if(has == 1){
        vec2 adj = new_adj[mult * adj_degree - flip];
        angle = flip * angle_between_vectors(c0 - adj, tangent);
    }
    // Decide on joint type
    bool one_linear = (degree == 1 || adj_degree == 1);
    bool should_bevel = (
        (joint_type == AUTO_JOINT && one_linear) ||
        joint_type == BEVEL_JOINT
    );
    bevel = should_bevel ? 1.0 : 0.0;
}


void set_previous_and_next(vec2 controls[3], int degree){
    float a_tol = 1e-10;

    if(distance(prev_bp[2], bp[0]) < a_tol){
        vec2 tangent = controls[1] - controls[0];
        set_adjascent_info(
            controls[0], tangent, degree, 1, 1,
            vec2[3](prev_bp[0], prev_bp[1], prev_bp[2]),
            has_prev, bevel_start, angle_from_prev
        );
    }
    if(distance(next_bp[0], bp[2]) < a_tol){
        vec2 tangent = controls[degree - 1] - controls[degree];
        set_adjascent_info(
            controls[degree], tangent, degree, 0, -1,
            vec2[3](next_bp[0], next_bp[1], next_bp[2]),
            has_next, bevel_end, angle_to_next
        );
    }
}


void main() {
    vec2 controls[3];
    int degree = get_reduced_control_points(bp[0], bp[1], bp[2], controls);
    bezier_degree = float(degree);

    // Null curve or linear with higher index than needed
    if(degree == 0) return;

    set_previous_and_next(controls, degree);

    // Find uv conversion matrix
    mat3 xy_to_uv = get_xy_to_uv(controls[0], controls[1]);
    float scale_factor = length(controls[1] - controls[0]);
    uv_anti_alias_width = anti_alias_width / scale_factor;
    uv_b2 = (xy_to_uv * vec3(bp[2], 1.0)).xy;

    // Corners of a bounding region around curve
    vec2 corners[5];
    int n_corners = get_corners(controls, degree, corners);

    // Get style info aligned to the corners
    float stroke_widths[5];
    vec4 stroke_colors[5];
    int index_map[5];
    if(n_corners == 4) index_map = int[5](0, 0, 2, 2, 2);
    else index_map = int[5](0, 0, 1, 2, 2);
    for(int i = 0; i < 5; i++){
        stroke_widths[i] = v_stroke_width[index_map[i]];
        stroke_colors[i] = v_color[index_map[i]];
    }

    // Emit each corner
    for(int i = 0; i < n_corners; i++){
        vec2 corner = corners[i];
        uv_coords = (xy_to_uv * vec3(corner, 1.0)).xy;

        uv_stroke_width = stroke_widths[i] / scale_factor;
        color = stroke_colors[i];

        set_gl_Position(vec3(corner, 0));
        EmitVertex();
    }
    EndPrimitive();
}