#version 330

#INSERT camera_uniform_declarations.glsl

in vec4 color;
in float fill_all;  // Either 0 or 1
in float uv_anti_alias_width;

in vec3 xyz_coords;
in float orientation;
in vec2 uv_coords;
in vec2 uv_b2;
in vec2 simp_coords;
in float bezier_degree;

out vec4 frag_color;


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
    vec2 p = simp_coords;
    float Fp = (p.x * p.x - p.y);
    // Sign takes care of whether we should be filling the inside or outside of curve.
    float sgn = orientation * sign(v2);
    if(sgn * Fp <= 0){
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
