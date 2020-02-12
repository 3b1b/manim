#version 330

in vec4 color;
in float fill_type;
in float uv_anti_alias_width;

in vec2 uv_coords;
in vec2 wz_coords;
in vec2 uv_b2;
in float bezier_degree;

out vec4 frag_color;

const float FILL_INSIDE = 0;
const float FILL_OUTSIDE = 1;
const float FILL_ALL = 2;


// Needed for quadratic_bezier_distance
float modify_distance_for_endpoints(vec2 p, float dist, float t){
    return dist;
}

// To my knowledge, there is no notion of #include for shaders,
// so to share functionality between this and others, the caller
// replaces this line with the contents of quadratic_bezier_sdf.glsl
#INSERT quadratic_bezier_distance.glsl


bool is_inside_curve(){
    if(bezier_degree < 2) return false;

    float value = wz_coords.x * wz_coords.x - wz_coords.y;
    if(fill_type == FILL_INSIDE) return value < 0;
    if(fill_type == FILL_OUTSIDE) return value > 0;
    return false;
}


float sdf(){
    if(is_inside_curve()) return -1;
    return min_dist_to_curve(uv_coords, uv_b2, bezier_degree, false);
}


void main() {
    if (color.a == 0) discard;
    frag_color = color;
    if (fill_type == FILL_ALL) return;
    frag_color.a *= smoothstep(1, 0, sdf() / uv_anti_alias_width);
    // frag_color.a += 0.2;
}