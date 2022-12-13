#version 330

#INSERT camera_uniform_declarations.glsl

in vec3 point;
in vec3 prev_point;
in vec3 next_point;
in vec3 unit_normal;

in float stroke_width;
in vec4 color;

// Bezier control point
out vec3 bp;
out vec3 prev_bp;
out vec3 next_bp;
out vec3 v_global_unit_normal;

out float v_stroke_width;
out vec4 v_color;

const float STROKE_WIDTH_CONVERSION = 0.01;

#INSERT position_point_into_frame.glsl

void main(){
    bp = position_point_into_frame(point);
    prev_bp = position_point_into_frame(prev_point);
    next_bp = position_point_into_frame(next_point);
    v_global_unit_normal = rotate_point_into_frame(unit_normal);

    v_stroke_width = STROKE_WIDTH_CONVERSION * stroke_width * frame_shape[1] / 8.0;
    v_color = color;
}