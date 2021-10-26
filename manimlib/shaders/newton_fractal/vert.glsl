#version 330

#INSERT camera_uniform_declarations.glsl

in vec3 point;
out vec3 xyz_coords;

uniform float scale_factor;
uniform vec3 offset;

#INSERT position_point_into_frame.glsl
#INSERT get_gl_Position.glsl

void main(){
    xyz_coords = (point - offset) / scale_factor;
    gl_Position = get_gl_Position(position_point_into_frame(point));
}