#version 330

#INSERT camera_uniform_declarations.glsl

in vec2 uv_coords;
in vec2 uv_b2;

in float uv_stroke_width;
in vec4 color;
in float uv_anti_alias_width;

in float has_prev;
in float has_next;
in float bezier_degree;

out vec4 frag_color;


#INSERT quadratic_bezier_distance.glsl


float cross2d(vec2 v, vec2 w){
    return v.x * w.y - w.x * v.y;
}

float modify_distance_for_endpoints(vec2 p, float dist, float t){
    if (0 <= t && t <= 1) return dist;

    float buff = 0.5 * uv_stroke_width - uv_anti_alias_width;
    // Check the beginning of the curve
    if(t < 0 && has_prev == 0) return max(dist, -p.x + buff);

    if(t > 1){
        // Check the end of the curve
        vec2 v21 = vec2(1, 0) - uv_b2;
        float len_v21 = length(v21);
        if(len_v21 == 0) len_v21 = length(-uv_b2);

        float perp_dist = dot(p - uv_b2, v21) / len_v21;
        if(has_next == 0) return max(dist, -perp_dist + buff);
    }
    return dist;
}


float dist_to_curve(){
    float dist = min_dist_to_curve(uv_coords, uv_b2, bezier_degree);
    if(has_prev == 0 && uv_coords.x < 0){
        float buff = 0.5 * uv_stroke_width - uv_anti_alias_width;
        return max(-uv_coords.x + buff, dist);
    }
    if(has_next == 0 && uv_coords.x > uv_b2.x){
        float buff = 0.5 * uv_stroke_width - uv_anti_alias_width;
        vec2 v12 = normalize(uv_b2 - vec2(1, 0));
        float perp_dist = dot(uv_coords - uv_b2, v12);
        if (perp_dist > 0) return max(perp_dist + buff, dist);
    }
    return dist;
}


void main() {
    if (uv_stroke_width == 0) discard;

    // An sdf for the region around the curve we wish to color.
    float signed_dist = abs(dist_to_curve()) - 0.5 * uv_stroke_width;

    frag_color = color;
    frag_color.a *= smoothstep(0.5, -0.5, signed_dist / uv_anti_alias_width);
}