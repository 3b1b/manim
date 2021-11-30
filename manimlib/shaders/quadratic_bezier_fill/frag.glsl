#version 330

#INSERT camera_uniform_declarations.glsl

in vec4 color;
in float fill_all;  // Either 0 or 1
in float uv_anti_alias_width;

in vec3 xyz_coords;
in float orientation;
in vec2 uv_coords;
in vec2 uv_b2;
in float bezier_degree;

out vec4 frag_color;

// Needed for quadratic_bezier_distance insertion below
float modify_distance_for_endpoints(vec2 p, float dist, float t){
    return dist;
}

#INSERT quadratic_bezier_distance.glsl


float sdf(){
    if(bezier_degree < 2){
        return abs(uv_coords[1]);
    }
    float u2 = uv_b2.x;
    float v2 = uv_b2.y;
    // For really flat curves, just take the distance to x-axis
    if(abs(v2 / u2) < 0.1 * uv_anti_alias_width){
        return abs(uv_coords[1]);
    }
    // For flat-ish curves, take the curve
    else if(abs(v2 / u2) < 0.5 * uv_anti_alias_width){
        return min_dist_to_curve(uv_coords, uv_b2, bezier_degree);
    }
    // I know, I don't love this amount of arbitrary-seeming branching either,
    // but a number of strange dimples and bugs pop up otherwise.

    // This converts uv_coords to yet another space where the bezier points sit on
    // (0, 0), (1/2, 0) and (1, 1), so that the curve can be expressed implicityly
    // as y = x^2.
    mat2 to_simple_space = mat2(
        v2, 0,
        2 - u2, 4 * v2
    );
    vec2 p = to_simple_space * uv_coords;
    // Sign takes care of whether we should be filling the inside or outside of curve.
    float sgn = orientation * sign(v2);
    float Fp = (p.x * p.x - p.y);
    if(sgn * Fp < 0){
        return 0.0;
    }else{
        return min_dist_to_curve(uv_coords, uv_b2, bezier_degree);
    }
}


void main() {
    if (color.a == 0) discard;
    frag_color = color;
    if (fill_all == 1.0) return;
    frag_color.a *= smoothstep(1, 0, sdf() / uv_anti_alias_width);
}
