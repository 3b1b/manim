#version 330

uniform sampler2D LightTexture;
uniform sampler2D DarkTexture;
uniform vec3 light_source_position;

in vec3 xyz_coords;
in vec3 v_normal;
in vec2 v_im_coords;
in float v_opacity;
in float v_gloss;
in float v_shadow;

out vec4 frag_color;

#INSERT add_light.glsl

void main() {
    vec4 light_color = texture(LightTexture, v_im_coords);
    vec4 dark_color = texture(DarkTexture, v_im_coords);
    float dp = dot(
        normalize(light_source_position - xyz_coords),
        normalize(v_normal)
    );
    float alpha = smoothstep(-0.1, 0.1, dp);
    vec4 color = mix(dark_color, light_color, alpha);

    frag_color = add_light(
        color,
        xyz_coords,
        normalize(v_normal),
        light_source_position,
        v_gloss,
        v_shadow
    );
    frag_color.a = v_opacity;
}