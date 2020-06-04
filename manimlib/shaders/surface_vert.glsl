#version 330

uniform float aspect_ratio;
uniform float anti_alias_width;
uniform mat4 to_screen_space;
uniform float focal_distance;
uniform vec3 light_source_position;

// uniform sampler2D Texture;

in vec3 point;
in vec3 normal;
// in vec2 im_coords;
in vec4 color;
in float gloss;

// out vec2 v_im_coords;
out vec4 v_color;

// Analog of import for manim only
#INSERT position_point_into_frame.glsl
#INSERT get_gl_Position.glsl
#INSERT add_light.glsl

void main(){
    vec3 xyz_coords = position_point_into_frame(point);
    vec3 unit_normal = normalize(position_point_into_frame(normal));
    // v_im_coords = im_coords;
    v_color = add_light(color, xyz_coords, unit_normal, light_source_position, gloss);
    gl_Position = get_gl_Position(xyz_coords);
}