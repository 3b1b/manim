#version 330

uniform float glow_factor;
uniform mat4 perspective;

in vec4 color;
in float scaled_aaw;
in vec3 v_point;

out vec4 frag_color;

// This include a delaration of uniform vec3 shading
#INSERT finalize_color.glsl

void main() {
    vec2 vect = 2.0 * gl_PointCoord.xy - vec2(1.0);
    float r = length(vect);
    if(r > 1.0 + scaled_aaw) discard;

    frag_color = color;

    if(glow_factor > 0){
        frag_color.a *= pow(1 - r, glow_factor);
    }

    if(shading != vec3(0.0)){
        vec3 normal = vec3(vect, sqrt(1 - r * r));
        normal = (perspective * vec4(normal, 0.0)).xyz;
        frag_color = finalize_color(frag_color, v_point, normal);
    }

    frag_color.a *= smoothstep(1.0, 1.0 - scaled_aaw, r);
}