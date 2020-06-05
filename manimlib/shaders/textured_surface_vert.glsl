#version 330

uniform float aspect_ratio;
uniform float anti_alias_width;
uniform mat4 to_screen_space;
uniform float focal_distance;
uniform vec3 light_source_position;

// uniform sampler2D Texture;

in vec3 point;
in vec3 normal;
in vec2 im_coords;
in float opacity;
in float gloss;

out vec3 xyz_coords;
out vec3 v_normal;
out vec2 v_im_coords;
out float v_opacity;
out float v_gloss;


// These lines will get replaced
#INSERT position_point_into_frame.glsl
#INSERT get_gl_Position.glsl

void main(){
    xyz_coords = position_point_into_frame(point);
    v_normal = position_point_into_frame(normal);
    v_im_coords = im_coords;
    v_opacity = opacity;
    v_gloss = gloss;
    gl_Position = get_gl_Position(xyz_coords);
}