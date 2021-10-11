#version 330

uniform vec3 light_source_position;
uniform float gloss;
uniform float shadow;
uniform float focal_distance;

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
uniform float color_mult;
uniform float black_for_cycles;

uniform vec2 frame_shape;

in vec3 xyz_coords;

out vec4 frag_color;

#INSERT finalize_color.glsl
#INSERT complex_functions.glsl

const int MAX_DEGREE = 5;


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
    vec2[MAX_DEGREE + 1] coefs = vec2[MAX_DEGREE + 1](coef0, coef1, coef2, coef3, coef4, coef5);
    vec2[MAX_DEGREE] roots = vec2[MAX_DEGREE](root0, root1, root2, root3, root4);
    vec4[MAX_DEGREE] colors = vec4[MAX_DEGREE](color0, color1, color2, color3, color4);

    vec2 z = xyz_coords.xy;
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
    color *= (1.0 + (color_mult - 1) * (n_iters - 5));

    if(black_for_cycles > 0.0 && min_dist > 1e-2){
        color = vec4(0.0, 0.0, 0.0, 1.0);
    }

    // if(julia_highlight > 0.0){
    //     float factor = min_dist / distance(z, found_root);
    //     factor *= pow(2.0, n_iters);
    //     float t = smoothstep(0, 5, factor);
    //     t *= 2.0;
    //     // color = vec4(0.0) * (1 - t) * (1 - t) + 2 * color * (1 - t) * t + vec4(1.0) * t * t;
    //     color *= t;
    // }

    if(julia_highlight > 0.0){
        float radius = julia_highlight;  // TODO
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
        vec3(0.0, 0.0, 1.0),
        light_source_position,
        gloss,
        shadow
    );
 }