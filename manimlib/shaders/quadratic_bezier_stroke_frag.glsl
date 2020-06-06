#version 330

uniform mat4 to_screen_space;
uniform vec3 light_source_position;

in vec2 uv_coords;
in vec2 uv_b2;

in float uv_stroke_width;
in vec4 color;
in float uv_anti_alias_width;

in float has_prev;
in float has_next;
in float bevel_start;
in float bevel_end;
in float angle_from_prev;
in float angle_to_next;

in float bezier_degree;

out vec4 frag_color;


float cross2d(vec2 v, vec2 w){
    return v.x * w.y - w.x * v.y;
}


float modify_distance_for_endpoints(vec2 p, float dist, float t){
    float buff = 0.5 * uv_stroke_width - uv_anti_alias_width;
    // Check the beginning of the curve
    if(t == 0){
        // Clip the start
        if(has_prev == 0) return max(dist, -p.x + buff);
        // Bevel start
        if(bevel_start == 1){
            float a = angle_from_prev;
            mat2 rot = mat2(
                cos(a), sin(a),
                -sin(a), cos(a)
            );
            // Dist for intersection of two lines
            float bevel_d = max(abs(p.y), abs((rot * p).y));
            // Dist for union of this intersection with the real curve
            return min(dist, bevel_d);
        }
        // Otherwise, start will be rounded off
    }else if(t == 1){
        // Check the end of the curve
        // TODO, too much code repetition
        vec2 v21 = (bezier_degree == 2) ? vec2(1, 0) - uv_b2 : vec2(-1, 0);
        float len_v21 = length(v21);
        if(len_v21 == 0){
            v21 = -uv_b2;
            len_v21 = length(v21);
        }

        float perp_dist = dot(p - uv_b2, v21) / len_v21;
        if(has_next == 0) return max(dist, -perp_dist + buff);
        // Bevel end
        if(bevel_end == 1){
            float a = -angle_to_next;
            mat2 rot = mat2(
                cos(a), sin(a),
                -sin(a), cos(a)
            );
            vec2 v21_unit = v21 / length(v21);
            float bevel_d = max(
                abs(cross2d(p - uv_b2, v21_unit)),
                abs(cross2d((rot * (p - uv_b2)), v21_unit))
            );
            return min(dist, bevel_d);
        }
        // Otherwise, end will be rounded off
    }
    return dist;
}

// To my knowledge, there is no notion of #include for shaders,
// so to share functionality between this and others, the caller
// replaces this line with the contents of named file
#INSERT quadratic_bezier_distance.glsl


void main() {
    if (uv_stroke_width == 0) discard;
    float dist_to_curve = min_dist_to_curve(uv_coords, uv_b2, bezier_degree);
    // An sdf for the region around the curve we wish to color.
    float signed_dist = abs(dist_to_curve) - 0.5 * uv_stroke_width;

    frag_color = color;
    frag_color.a *= smoothstep(0.5, -0.5, signed_dist / uv_anti_alias_width);

    // frag_color.a += 0.3;
}