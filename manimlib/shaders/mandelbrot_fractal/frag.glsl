#version 330

uniform vec2 parameter;
uniform float opacity;
uniform float n_steps;
uniform float mandelbrot;

uniform vec3 color0;
uniform vec3 color1;
uniform vec3 color2;
uniform vec3 color3;
uniform vec3 color4;
uniform vec3 color5;
uniform vec3 color6;
uniform vec3 color7;
uniform vec3 color8;

in vec3 xyz_coords;

out vec4 frag_color;

#INSERT finalize_color.glsl
#INSERT complex_functions.glsl

const int MAX_DEGREE = 5;

void main() {
    vec3 color_map[9] = vec3[9](
        color0, color1, color2, color3,
        color4, color5, color6, color7, color8
    );
    vec3 color;

    vec2 z;
    vec2 c;

    if(bool(mandelbrot)){
        c = xyz_coords.xy;
        z = vec2(0.0, 0.0);
    }else{
        c = parameter;
        z = xyz_coords.xy;
    }

    float outer_bound = 2.0;
    bool stable = true;
    for(int n = 0; n < int(n_steps); n++){
        z = complex_mult(z, z) + c;
        if(length(z) > outer_bound){
            float float_n = float(n);
            float_n += log(outer_bound) / log(length(z));
            float_n += 0.5 * length(c);
            color = float_to_color(sqrt(float_n), 1.5, 8.0, color_map);
            stable = false;
            break;
        }
    }
    if(stable){
        color = vec3(0.0, 0.0, 0.0);
    }

    frag_color = finalize_color(
        vec4(color, opacity),
        xyz_coords,
        vec3(0.0, 0.0, 1.0)
    );
 }