#version 330

in vec3 point;

#INSERT get_gl_Position.glsl

void main(){
    gl_Position = get_gl_Position(position_point_into_frame(point));
}