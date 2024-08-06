#version 330

layout (triangles) in;
layout (triangle_strip, max_vertices = 64) out;  // Related to MAX_STEPS below

uniform float anti_alias_width;
uniform float flat_stroke;
uniform float pixel_size;
uniform float joint_type;
uniform float frame_scale;

in vec3 verts[3];

in vec4 v_joint_product[3];
in float v_stroke_width[3];
in vec4 v_color[3];

out vec4 color;
out float scaled_anti_alias_width;
out float scaled_signed_dist_to_curve;

// Codes for joint types
const int NO_JOINT = 0;
const int AUTO_JOINT = 1;
const int BEVEL_JOINT = 2;
const int MITER_JOINT = 3;

// When the cosine of the angle between
// two vectors is larger than this, we
// consider them aligned
const float COS_THRESHOLD = 0.99;
// Used to determine how many lines to break the curve into
const float POLYLINE_FACTOR = 30;
const int MAX_STEPS = 32;
const float MITER_LIMIT = 5.0;

#INSERT emit_gl_Position.glsl
#INSERT finalize_color.glsl


vec3 get_joint_unit_normal(vec4 joint_product){
    float tol = 1e-8;
    if (length(joint_product.xyz) > tol){
        return normalize(joint_product.xyz);
    }
    if (length(v_joint_product[1].xyz) > tol){
        return normalize(v_joint_product[1].xyz);
    }
    return vec3(0.0, 0.0, 1.0);
}


vec3 point_on_quadratic(float t, vec3 c0, vec3 c1, vec3 c2){
    return c0 + c1 * t + c2 * t * t;
}


vec3 tangent_on_quadratic(float t, vec3 c1, vec3 c2){
    return c1 + 2 * c2 * t;
}


vec4 get_joint_product(vec3 v1, vec3 v2){
    return vec4(cross(v1, v2), dot(v1, v2));
}


vec3 project(vec3 vect, vec3 unit_normal){
    /* Project the vector onto the plane perpendicular to a given unit normal */
    return vect - dot(vect, unit_normal) * unit_normal;
}

vec3 inverse_vector_product(vec3 vect, vec3 cross_product, float dot_product){
    /* 
    Suppose cross(v1, v2) = cross_product and dot(v1, v2) = dot_product.
    Given v1, this function return v2.
    */
    return (vect * dot_product - cross(vect, cross_product)) / dot(vect, vect);
}


vec3 step_to_corner(vec3 point, vec3 tangent, vec3 unit_normal, vec4 joint_product, bool inner_joint){
    /*
    Step the the left of a curve.
    First a perpendicular direction is calculated, then it is adjusted
    so as to make a joint.
    */
    vec3 unit_tan = normalize(flat_stroke == 0.0 ? project(tangent, unit_normal) : tangent);
    vec3 step = normalize(cross(unit_normal, unit_tan));

    // Check if we can avoid creating a joint
    if (inner_joint || int(joint_type) == NO_JOINT) return step;

    // Find the angle between
    
    if (flat_stroke == 0){
        // Figure out what joint product would be for everything projected onto
        // the plane perpendicular to the normal direction (which here would be to_camera)
        vec3 adj_tan = inverse_vector_product(tangent, joint_product.xyz, joint_product.w);
        adj_tan = project(adj_tan, unit_normal);
        joint_product = get_joint_product(unit_tan, adj_tan);
    }

    float cos_angle = (length(joint_product) > 1e-10) ? normalize(joint_product).w : 1.0;
    if(cos_angle > 1 - 1e-3) return step;
    float sin_angle = sqrt(1 - cos_angle * cos_angle) * sign(dot(joint_product.xyz, unit_normal));

    // Adjust based on the joint
    float shift = (int(joint_type) == MITER_JOINT) ?
        (cos_angle + 1.0) / sin_angle :
        (cos_angle - 1.0) / sin_angle;

    step = step + shift * unit_tan;
    if (length(step) > MITER_LIMIT){
        step = MITER_LIMIT * normalize(step);
    }

    return step;
}


void emit_point_with_width(
    vec3 point,
    vec3 tangent,
    vec4 joint_product,
    float width,
    vec4 joint_color,
    bool inner_joint
){
    // Find unit normal
    vec3 to_camera = camera_position - point;
    vec3 unit_normal;
    if (flat_stroke == 0.0){
        unit_normal = normalize(to_camera);
    }else{
        unit_normal = get_joint_unit_normal(joint_product);
        unit_normal *= sign(dot(unit_normal, to_camera));  // Choose the "outward" normal direction
    }

    // Figure out the step from the point to the corners of the
    // triangle strip around the polyline
    vec3 step = step_to_corner(point, tangent, unit_normal, joint_product, inner_joint);

    // TODO, this gives a potentially nice effect that's like a ribbon mostly with its
    // broad side to the camera. Currently hard to access via VMobject
    if(flat_stroke == 2.0){
        // Rotate the step towards the unit normal by an amount depending
        // on the camera position 
        float cos_angle = dot(unit_normal, normalize(camera_position));
        float sin_angle = sqrt(max(1 - cos_angle * cos_angle, 0));
        step = cos_angle * step + sin_angle * unit_normal;
    }

    // Set styling
    color = finalize_color(joint_color, point, unit_normal);
    if (width == 0) scaled_anti_alias_width = -1.0;  // Signal to discard in the frag shader
    else scaled_anti_alias_width = 2.0 * anti_alias_width * pixel_size / width;

    // Emit two corners
    // The frag shader will receive a value from -1 to 1,
    // reflecting where in the stroke that point is
    for (int sign = -1; sign <= 1; sign += 2){
        scaled_signed_dist_to_curve = sign;
        emit_gl_Position(point + 0.5 * width * sign * step);
        EmitVertex();
    }
}


void main() {
    // Curves are marked as ended when the handle after
    // the first anchor is set equal to that anchor
    if (verts[0] == verts[1]) return;

    // Coefficients such that the quadratic bezier is c0 + c1 * t  + c2 * t^2
    vec3 c0 = verts[0];
    vec3 c1 = 2 * (verts[1] - verts[0]);
    vec3 c2 = verts[0] - 2 * verts[1] + verts[2];

    // Estimate how many line segment the curve should be divided into
    // based on the area of the triangle defined by these control points
    float area = 0.5 * length(v_joint_product[1].xzy);
    int count = int(round(POLYLINE_FACTOR * sqrt(area) / frame_scale));
    int n_steps = min(2 + count, MAX_STEPS);

    // Emit vertex pairs aroudn subdivided points
    for (int i = 0; i < MAX_STEPS; i++){
        if (i >= n_steps) break;
        float t = float(i) / (n_steps - 1);

        // Point and tangent
        vec3 point = point_on_quadratic(t, c0, c1, c2);
        vec3 tangent = tangent_on_quadratic(t, c1, c2);

        // Style
        float stroke_width = mix(v_stroke_width[0], v_stroke_width[2], t);
        vec4 color = mix(v_color[0], v_color[2], t);

        // This is sent along to prevent needless joint creation
        bool inside_curve = (i > 0 && i < n_steps - 1);

        // Use middle joint product for inner points, flip sign for first one's cross product component
        vec4 joint_product;
        if (i == 0)            joint_product = v_joint_product[0] * vec4(-1, -1, -1, 1);
        else if (inside_curve) joint_product = v_joint_product[1];
        else                   joint_product = v_joint_product[2];

        emit_point_with_width(
            point, tangent, joint_product,
            stroke_width, color,
            inside_curve
        );
    }
    EndPrimitive();
}