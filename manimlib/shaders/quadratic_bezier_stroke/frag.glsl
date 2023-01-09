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