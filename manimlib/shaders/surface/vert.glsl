#version 330

uniform vec4 clip_plane;

in vec3 point;
in vec3 normal;
in vec4 rgba;

out vec4 v_color;

#INSERT emit_gl_Position.glsl
#INSERT get_unit_normal.glsl
#INSERT finalize_color.glsl

void main(){
    emit_gl_Position(point);
    v_color = finalize_color(rgba, point, normalize(normal));

    if(clip_plane.xyz != vec3(0.0, 0.0, 0.0)){
        gl_ClipDistance[0] = dot(vec4(point, 1.0), clip_plane);
    }
}