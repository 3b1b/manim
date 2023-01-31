#version 330

in vec3 point;

#INSERT emit_gl_Position.glsl

void main(){
    emit_gl_Position(point);
}