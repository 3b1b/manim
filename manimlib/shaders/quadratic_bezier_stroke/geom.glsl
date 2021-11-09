#version 330

layout (triangles) in;
layout (triangle_strip, max_vertices = 5) out;

// Needed for get_gl_Position
uniform vec2 frame_shape;
uniform float focal_distance;
uniform float is_fixed_in_frame;

uniform float anti_alias_width;
uniform float flat_stroke;

//Needed for lighting
uniform vec3 light_source_position;
uniform vec3 camera_position;
uniform float joint_type;
uniform float reflectiveness;
uniform float gloss;
uniform float shadow;

in vec3 bp[3];
in vec3 prev_bp[3];
in vec3 next_bp[3];
in vec3 v_global_unit_normal[3];

in vec4 v_color[3];
in float v_stroke_width[3];

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
const float PI = 3.141592653;


#INSERT quadratic_bezier_geometry_functions.glsl
#INSERT get_gl_Position.glsl
#INSERT get_unit_normal.glsl
#INSERT finalize_color.glsl


void flatten_points(in vec3[3] points, out vec2[3] flat_points){
    for(int i = 0; i < 3; i++){
        float sf = perspective_scale_factor(points[i].z, focal_distance);
        flat_points[i] = sf * points[i].xy;
    }
}


float angle_between_vectors(vec2 v1, vec2 v2){
    float v1_norm = length(v1);
    float v2_norm = length(v2);
    if(v1_norm == 0 || v2_norm == 0) return 0.0;
    float dp = dot(v1, v2) / (v1_norm * v2_norm);
    float angle = acos(clamp(dp, -1.0, 1.0));
    float sn = sign(cross2d(v1, v2));
    return sn * angle;
}


bool find_intersection(vec2 p0, vec2 v0, vec2 p1, vec2 v1, out vec2 intersection){
    // Find the intersection of a line passing through
    // p0 in the direction v0 and one passing through p1 in
    // the direction p1.
    // That is, find a solutoin to p0 + v0 * t = p1 + v1 * s
    float det = -v0.x * v1.y + v1.x * v0.y;
    if(det == 0) return false;
    float t = cross2d(p0 - p1, v1) / det;
    intersection = p0 + v0 * t;
    return true;
}


void create_joint(float angle, vec2 unit_tan, float buff,
                  vec2 static_c0, out vec2 changing_c0,
                  vec2 static_c1, out vec2 changing_c1){
    float shift;
    if(abs(angle) < 1e-3){
        // No joint
        shift = 0;
    }else if(joint_type == MITER_JOINT){
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
int get_corners(vec2 controls[3], int degree, float stroke_widths[3], out vec2 corners[5]){
    vec2 p0 = controls[0];
    vec2 p1 = controls[1];
    vec2 p2 = controls[2];

    // Unit vectors for directions between control points
    vec2 v10 = normalize(p0 - p1);
    vec2 v12 = normalize(p2 - p1);
    vec2 v01 = -v10;
    vec2 v21 = -v12;

    vec2 p0_perp = vec2(-v01.y, v01.x);  // Pointing to the left of the curve from p0
    vec2 p2_perp = vec2(-v12.y, v12.x);  // Pointing to the left of the curve from p2

    // aaw is the added width given around the polygon for antialiasing.
    // In case the normal is faced away from (0, 0, 1), the vector to the
    // camera, this is scaled up.
    float aaw = anti_alias_width;
    float buff0 = 0.5 * stroke_widths[0] + aaw;
    float buff2 = 0.5 * stroke_widths[2] + aaw;
    float aaw0 = (1 - has_prev) * aaw;
    float aaw2 = (1 - has_next) * aaw;

    vec2 c0 = p0 - buff0 * p0_perp + aaw0 * v10;
    vec2 c1 = p0 + buff0 * p0_perp + aaw0 * v10;
    vec2 c2 = p2 + buff2 * p2_perp + aaw2 * v12;
    vec2 c3 = p2 - buff2 * p2_perp + aaw2 * v12;

    // Account for previous and next control points
    if(has_prev > 0) create_joint(angle_from_prev, v01, buff0, c0, c0, c1, c1);
    if(has_next > 0) create_joint(angle_to_next, v21, buff2, c3, c3, c2, c2);

    // Linear case is the simplest
    if(degree == 1){
        // The order of corners should be for a triangle_strip.  Last entry is a dummy
        corners = vec2[5](c0, c1, c3, c2, vec2(0.0));
        return 4;
    }
    // Otherwise, form a pentagon around the curve
    float orientation = sign(cross2d(v01, v12));  // Positive for ccw curves
    if(orientation > 0) corners = vec2[5](c0, c1, p1, c2, c3);
    else                corners = vec2[5](c1, c0, p1, c3, c2);
    // Replace corner[2] with convex hull point accounting for stroke width
    find_intersection(corners[0], v01, corners[4], v21, corners[2]);
    return 5;
}


void set_adjascent_info(vec2 c0, vec2 tangent,
                        int degree,
                        vec2 adj[3],
                        out float bevel,
                        out float angle
                        ){
    bool linear_adj = (angle_between_vectors(adj[1] - adj[0], adj[2] - adj[1]) < 1e-3);
    angle = angle_between_vectors(c0 - adj[1], tangent);
    // Decide on joint type
    bool one_linear = (degree == 1 || linear_adj);
    bool should_bevel = (
        (joint_type == AUTO_JOINT && one_linear) ||
        joint_type == BEVEL_JOINT
    );
    bevel = should_bevel ? 1.0 : 0.0;
}


void find_joint_info(vec2 controls[3], vec2 prev[3], vec2 next[3], int degree){
    float tol = 1e-6;

    // Made as floats not bools so they can be passed to the frag shader
    has_prev = float(distance(prev[2], controls[0]) < tol);
    has_next = float(distance(next[0], controls[2]) < tol);

    if(bool(has_prev)){
        vec2 tangent = controls[1] - controls[0];
        set_adjascent_info(
            controls[0], tangent, degree, prev,
            bevel_start, angle_from_prev
        );
    }
    if(bool(has_next)){
        vec2 tangent = controls[1] - controls[2];
        set_adjascent_info(
            controls[2], tangent, degree, next,
            bevel_end, angle_to_next
        );
        angle_to_next *= -1;
    }
}


void main() {
    // Convert control points to a standard form if they are linear or null
    vec3 controls[3];
    vec3 prev[3];
    vec3 next[3];
    bezier_degree = get_reduced_control_points(vec3[3](bp[0], bp[1], bp[2]), controls);
    if(bezier_degree == 0.0) return;  // Null curve
    int degree = int(bezier_degree);
    get_reduced_control_points(vec3[3](prev_bp[0], prev_bp[1], prev_bp[2]), prev);
    get_reduced_control_points(vec3[3](next_bp[0], next_bp[1], next_bp[2]), next);


    // Adjust stroke width based on distance from the camera
    float scaled_strokes[3];
    for(int i = 0; i < 3; i++){
        float sf = perspective_scale_factor(controls[i].z, focal_distance);
        if(bool(flat_stroke)){
            vec3 to_cam = normalize(vec3(0.0, 0.0, focal_distance) - controls[i]);
            sf *= abs(dot(v_global_unit_normal[i], to_cam));
        }
        scaled_strokes[i] = v_stroke_width[i] * sf;
    }

    // Control points are projected to the xy plane before drawing, which in turn
    // gets tranlated to a uv plane.  The z-coordinate information will be remembered
    // by what's sent out to gl_Position, and by how it affects the lighting and stroke width
    vec2 flat_controls[3];
    vec2 flat_prev[3];
    vec2 flat_next[3];
    flatten_points(controls, flat_controls);
    flatten_points(prev, flat_prev);
    flatten_points(next, flat_next);

    find_joint_info(flat_controls, flat_prev, flat_next, degree);

    // Corners of a bounding region around curve
    vec2 corners[5];
    int n_corners = get_corners(flat_controls, degree, scaled_strokes, corners);

    int index_map[5] = int[5](0, 0, 1, 2, 2);
    if(n_corners == 4) index_map[2] = 2;

    // Find uv conversion matrix
    mat3 xy_to_uv = get_xy_to_uv(flat_controls[0], flat_controls[1]);
    float scale_factor = length(flat_controls[1] - flat_controls[0]);
    uv_anti_alias_width = anti_alias_width / scale_factor;
    uv_b2 = (xy_to_uv * vec3(flat_controls[2], 1.0)).xy;

    // Emit each corner
    for(int i = 0; i < n_corners; i++){
        uv_coords = (xy_to_uv * vec3(corners[i], 1.0)).xy;
        uv_stroke_width = scaled_strokes[index_map[i]] / scale_factor;
        // Apply some lighting to the color before sending out.
        // vec3 xyz_coords = vec3(corners[i], controls[index_map[i]].z);
        vec3 xyz_coords = vec3(corners[i], controls[index_map[i]].z);
        color = finalize_color(
            v_color[index_map[i]],
            xyz_coords,
            v_global_unit_normal[index_map[i]],
            light_source_position,
            camera_position,
            reflectiveness,
            gloss,
            shadow
        );
        gl_Position = vec4(
            get_gl_Position(vec3(corners[i], 0.0)).xy,
            get_gl_Position(controls[index_map[i]]).zw
        );
        EmitVertex();
    }
    EndPrimitive();
}