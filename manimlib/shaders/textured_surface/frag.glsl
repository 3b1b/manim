#version 330

uniform sampler2D LightTexture;
uniform sampler2D DarkTexture;
uniform float num_textures;
uniform vec3 light_source_position;
uniform vec3 camera_position;
uniform float reflectiveness;
uniform float gloss;
uniform float shadow;
uniform float focal_distance;

in vec3 xyz_coords;
in vec3 v_normal;
in vec2 v_im_coords;
in float v_opacity;

out vec4 frag_color;

#INSERT finalize_color.glsl

const float dark_shift = 0.2;

void main() {
    vec4 color = texture(LightTexture, v_im_coords);
    if(num_textures == 2.0){
        vec4 dark_color = texture(DarkTexture, v_im_coords);
        float dp = dot(
            normalize(light_source_position - xyz_coords),
            normalize(v_normal)
        );
        float alpha = smoothstep(-dark_shift, dark_shift, dp);
        color = mix(dark_color, color, alpha);
    }

    frag_color = finalize_color(
        color,
        xyz_coords,
        normalize(v_normal),
        light_source_position,
        camera_position,
        reflectiveness,
        gloss,
        shadow
    );
    frag_color.a = v_opacity;
}