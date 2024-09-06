#version 330

uniform vec4 color0;
uniform vec4 color1;
uniform vec4 color2;
uniform vec4 color3;
uniform vec4 color4;

uniform vec2 coef0;
uniform vec2 coef1;
uniform vec2 coef2;
uniform vec2 coef3;
uniform vec2 coef4;
uniform vec2 coef5;

uniform vec2 root0;
uniform vec2 root1;
uniform vec2 root2;
uniform vec2 root3;
uniform vec2 root4;

uniform float n_roots;
uniform float n_steps;
uniform float julia_highlight;
uniform float saturation_factor;
uniform float black_for_cycles;
uniform float is_parameter_space;

in vec3 xyz_coords;

out vec4 frag_color;

#INSERT finalize_color.glsl
#INSERT complex_functions.glsl

const int MAX_DEGREE = 5;
const float CLOSE_ENOUGH = 1e-3;


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
    float threshold = CLOSE_ENOUGH;

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
    n_iters -= log(curr_len) / log(threshold);

    return z;
}


void main() {
    vec2[MAX_DEGREE + 1] coefs = vec2[MAX_DEGREE + 1](coef0, coef1, coef2, coef3, coef4, coef5);
    vec2[MAX_DEGREE] roots = vec2[MAX_DEGREE](root0, root1, root2, root3, root4);
    vec4[MAX_DEGREE] colors = vec4[MAX_DEGREE](color0, color1, color2, color3, color4);

    vec2 z = xyz_coords.xy;

    if(is_parameter_space > 0){
        // In this case, pixel should correspond to one of the roots
        roots[2] = xyz_coords.xy;
        vec2 r0 = roots[0];
        vec2 r1 = roots[1];
        vec2 r2 = roots[2];

        // It is assumed that the polynomial is cubid...
        coefs[0] = -complex_mult(complex_mult(r0, r1), r2);
        coefs[1] = complex_mult(r0, r1) + complex_mult(r0, r2) + complex_mult(r1, r2);
        coefs[2] = -(r0 + r1 + r2);
        coefs[3] = vec2(1.0, 0.0);

        // Seed value is always center of the roots
        z = -coefs[2] / 3.0;
    }

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
    color *= 1.0 + (0.01 * saturation_factor) * (n_iters - 2 * saturation_factor);

    if(black_for_cycles > 0 && min_dist > CLOSE_ENOUGH){
        color = vec4(0.0, 0.0, 0.0, 1.0);
    }

    if(julia_highlight > 0.0){
        float radius = julia_highlight;
        vec2[4] samples = vec2[4](
            z + vec2(radius, 0.0),
            z + vec2(-radius, 0.0),
            z + vec2(0.0, radius),
            z + vec2(0.0, -radius)
        );
        for(int i = 0; i < 4; i++){
            for(int j = 0; j < n_steps; j++){
                vec2 z = samples[i];
                z = z - complex_div(poly(z, coefs), dpoly(z, coefs));
                samples[i] = z;
            }
        }
        float max_dist = 0.0;
        for(int i = 0; i < 4; i++){
            max_dist = max(max_dist, distance(samples[i], samples[(i + 1) % 4]));
        }
        color *= 1.0 * smoothstep(0, 0.1, max_dist);
    }

    frag_color = finalize_color(
        color,
        xyz_coords,
        vec3(0.0, 0.0, 1.0)
    );
 }