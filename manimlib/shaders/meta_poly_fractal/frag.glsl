#version 330

uniform vec3 light_source_position;
uniform float gloss;
uniform float shadow;
uniform float focal_distance;

uniform vec4 color0;
uniform vec4 color1;
uniform vec4 color2;

uniform vec2 root0;
uniform vec2 root1;

// uniform vec2 coef0;
// uniform vec2 coef1;
// uniform vec2 coef2;
// uniform vec2 coef3;

uniform vec2 z0;

uniform float n_roots;
uniform float n_steps;
uniform float julia_highlight;
uniform float color_mult;

uniform vec2 frame_shape;

in vec3 xyz_coords;

out vec4 frag_color;

#INSERT finalize_color.glsl
#INSERT complex_functions.glsl

const int MAX_DEGREE = 3;

vec2 poly(vec2 z, vec2[MAX_DEGREE + 1] coefs){
    vec2 result = vec2(0.0);
    for(int n = 0; n < int(n_roots) + 1; n++){
        result += complex_mult(coefs[n], complex_pow(z, n));
    }
    return result;
}

vec2 dpoly(vec2 z, vec2[MAX_DEGREE + 1] coefs){
    vec2 result = vec2(0.0);
    for(int n = 1; n < int(n_roots) + 1; n++){
        result += n * complex_mult(coefs[n], complex_pow(z, n - 1));
    }
    return result;
}

vec2 seek_root(vec2 z, vec2[MAX_DEGREE + 1] coefs, int max_steps, out float n_iters){
    float last_len;
    float curr_len;
    float threshold = 1e-3;

    for(int i = 0; i < max_steps; i++){
        last_len = curr_len;
        n_iters = float(i);
        vec2 step = complex_div(poly(z, coefs), dpoly(z, coefs));
        curr_len = length(step);
        if(curr_len < threshold){
            break;
        }
        z = z - step;
    }
    n_iters -= clamp((threshold - curr_len) / (last_len - curr_len), 0.0, 1.0);

    return z;
}

void main() {
    vec2 root2 = xyz_coords.xy;

    vec2 coef0 = -complex_mult(complex_mult(root0, root1), root2);
    vec2 coef1 = complex_mult(root0, root1) + complex_mult(root0, root2) + complex_mult(root1, root2);
    vec2 coef2 = -(root0 + root1 + root2);
    vec2 coef3 = vec2(1.0, 0.0);

    vec2[MAX_DEGREE + 1] coefs = vec2[MAX_DEGREE + 1](coef0, coef1, coef2, coef3);
    vec2[MAX_DEGREE] roots = vec2[MAX_DEGREE](root0, root1, root2);
    vec4[MAX_DEGREE] colors = vec4[MAX_DEGREE](color0, color1, color2);

    // vec2 z = z0;
    vec2 z = -coef2 / 3.0;
    float n_iters;
    vec2 found_root = seek_root(z, coefs, int(n_steps), n_iters);

    vec4 color = vec4(0.0);
    float min_dist = 1e10;
    float dist;
    for(int i = 0; i < int(n_roots); i++){
        dist = distance(roots[i], found_root);
        if(dist < min_dist){
            min_dist = dist;
            color = colors[i];
        }
    }
    // color *= (1.0 + (color_mult - 1) * (n_iters - 5));

    if (min_dist > 1e-2){
        color = vec4(0.0, 0.0, 0.0, 1.0);
    }

    frag_color = finalize_color(
        color,
        xyz_coords,
        vec3(0.0, 0.0, 1.0),
        light_source_position,
        gloss,
        shadow
    );
 }