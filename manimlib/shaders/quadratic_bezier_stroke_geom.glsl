#version 330

layout (triangles) in;
layout (triangle_strip, max_vertices = 5) out;

// Needed for get_gl_Position
uniform vec2 frame_shape;
uniform float focal_distance;
uniform float is_fixed_in_frame;
uniform float anti_alias_width;
uniform vec3 light_source_position;
uniform float joint_type;

in vec3 bp[3];
in vec3 prev_bp[3];
in vec3 next_bp[3];
in vec3 v_global_unit_normal[3];

in vec4 v_color[3];
in float v_stroke_width[3];
in float v_gloss[3];
in float v_shadow[3];

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
#INSERT get_gl_Position.glsl
#INSERT get_unit_normal.glsl
#INSERT add_light.glsl


void flatten_points(in vec3[3] points, out vec3[3] flat_points){
    for(int i = 0; i < 3; i++){
        flat_points[i] = points[i];
        flat_points[i].z = 0;
    }
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


void create_joint(float angle, vec3 unit_tan, float buff, float should_bevel,
                  vec3 static_c0, out vec3 changing_c0,
                  vec3 static_c1, out vec3 changing_c1){
    float shift;
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

    vec3 p0_perp = cross(normal, v01);  // Pointing to the left of the curve from p0
    vec3 p2_perp = cross(normal, v12);  // Pointing to the left of the curve from p2

    // aaw is the added width given around the polygon for antialiasing.
    // In case the normal is faced away from (0, 0, 1), the vector to the
    // camera, this is scaled up.
    float aaw = anti_alias_width;
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
        // The order of corners should be for a triangle_strip.  Last entry is a dummy
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


void find_joint_info(vec3 controls[3], vec3 prev[3], vec3 next[3], int degree, vec3 normal){
    float tol = 1e-8;

    // Made as floats not bools so they can be passed to the frag shader
    has_prev = float(distance(prev[2], controls[0]) < tol);
    has_next = float(distance(next[0], controls[2]) < tol);

    if(bool(has_prev)){
        vec3 tangent = controls[1] - controls[0];
        set_adjascent_info(
            controls[0], tangent, degree, normal, prev,
            bevel_start, angle_from_prev
        );
    }
    if(bool(has_next)){
        vec3 tangent = controls[1] - controls[2];
        set_adjascent_info(
            controls[2], tangent, degree, normal, next,
            bevel_end, angle_to_next
        );
        angle_to_next *= -1;
    }
}


void main() {
    vec3 controls[3];
    bezier_degree = get_reduced_control_points(vec3[3](bp[0], bp[1], bp[2]), controls);
    int degree = int(bezier_degree);

    // Control points are projected to the xy plane before drawing, which in turn
    // gets tranlated to a uv plane.  The z-coordinate information will be remembered
    // by what's sent out to gl_Position, and by how it affects the lighting and stroke width
    vec3 flat_controls[3];
    vec3 flat_prev[3];
    vec3 flat_next[3];
    flatten_points(controls, flat_controls);
    flatten_points(vec3[3](prev_bp[0], prev_bp[1], prev_bp[2]), flat_prev);
    flatten_points(vec3[3](next_bp[0], next_bp[1], next_bp[2]), flat_next);
    vec3 k_hat = vec3(0.0, 0.0, 1.0);

    // Null curve
    if(degree == 0) return;

    find_joint_info(flat_controls, flat_prev, flat_next, degree, k_hat);

    // Find uv conversion matrix
    mat4 xyz_to_uv = get_xyz_to_uv(flat_controls[0], flat_controls[1], k_hat);
    float scale_factor = length(flat_controls[1] - flat_controls[0]);
    uv_anti_alias_width = anti_alias_width / scale_factor;
    uv_b2 = (xyz_to_uv * vec4(controls[2].xy, 0.0, 1.0)).xy;

    // Corners of a bounding region around curve
    vec3 corners[5];
    int n_corners = get_corners(flat_controls, k_hat, degree, corners);

    int index_map[5] = int[5](0, 0, 1, 2, 2);
    if(n_corners == 4) index_map[2] = 2;

    // Emit each corner
    for(int i = 0; i < n_corners; i++){
        uv_coords = (xyz_to_uv * vec4(corners[i], 1.0)).xy;
        uv_stroke_width = v_stroke_width[index_map[i]] / scale_factor;
        // Apply some lighting to the color before sending out.
        vec3 xyz_coords = vec3(corners[i].xy, controls[index_map[i]].z);
        color = add_light(
            v_color[index_map[i]],
            xyz_coords,
            v_global_unit_normal[index_map[i]],
            light_source_position,
            v_gloss[index_map[i]],
            v_shadow[index_map[i]]
        );
        gl_Position = get_gl_Position(xyz_coords);
        EmitVertex();
    }
    EndPrimitive();
}