// Copied from surface/frag.glsl

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

uniform vec2 frame_shape;

in vec3 xyz_coords;

out vec4 frag_color;

#INSERT finalize_color.glsl

vec2 complex_mult(vec2 z, vec2 w){
    return vec2(z.x * w.x - z.y * w.y, z.x * w.y + z.y * w.x);
}

vec2 complex_div(vec2 z, vec2 w){
    float w_norm_squared = w.x * w.x + w.y * w.y;
    return complex_mult(z, vec2(w.x, -w.y)) / w_norm_squared;
}

vec2 complex_pow(vec2 z, int n){
    vec2 result = vec2(1.0, 0.0);
    for(int i = 0; i < n; i++){
        result = complex_mult(result, z);
    }
    return result;
}

vec2 poly(vec2 z, vec2[6] coefs){
    vec2 result = vec2(0.0);
    for(int n = 0; n < 6; n++){
        result += complex_mult(coefs[n], complex_pow(z, n));
    }
    return result;
}

vec2 dpoly(vec2 z, vec2[6] coefs){
    vec2 result = vec2(0.0);
    for(int n = 1; n < 6; n++){
        result += n * complex_mult(coefs[n], complex_pow(z, n - 1));
    }
    return result;
}

vec2 seek_root(vec2 z, vec2[6] coefs){
    for(int i = 0; i < int(n_steps); i++){
        vec2 step = complex_div(poly(z, coefs), dpoly(z, coefs));
        if(length(step) < 1e-2){
            break;
        }
        z = z - step;
    }

    return z;
}


void main() {
    vec2[6] coefs = vec2[6](coef0, coef1, coef2, coef3, coef4, coef5);
    vec2[5] roots = vec2[5](root0, root1, root2, root3, root4);
    vec4[5] colors = vec4[5](color0, color1, color2, color3, color4);

    vec2 z = xyz_coords.xy;
    vec2 found_root = seek_root(z, coefs);

    vec4 color = vec4(0.0);
    float curr_min = 1e10;
    for(int i = 0; i < 5; i++){
        float dist = distance(roots[i], found_root);
        if(dist < curr_min){
            curr_min = dist;
            color = colors[i];
        }
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