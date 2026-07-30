#version 330

uniform float stroke_width_in_scene_units;

in vec3 point;
in vec4 stroke_rgba;
in float stroke_width;
in float joint_angle;
in vec3 unit_normal;

// Bezier control point
out vec3 verts;

out vec4 v_color;
out float v_stroke_width;
out float v_joint_angle;
out vec3 v_unit_normal;

// Number of units spanned by a stroke_width of 1 in a default scale frame,
// so for instance a stroke_width of 100 comes out one unit thick
const float STROKE_WIDTH_CONVERSION = 0.01;

#INSERT frame_units.glsl

void main(){
    verts = point;
    v_color = stroke_rgba;
    // By default stroke width is measured relative to the frame, so putting it in the
    // units of the space being drawn means scaling by that space's frame size, which
    // keeps a given stroke width looking the same at any zoom level. When it's measured
    // relative to the scene instead, no such conversion is needed, and zooming in makes
    // the stroke look thicker.
    float stroke_width_factor = STROKE_WIDTH_CONVERSION * mix(
        get_frame_unit_size(), 1.0, stroke_width_in_scene_units
    );
    v_stroke_width = stroke_width_factor * stroke_width;
    v_joint_angle = joint_angle;
    v_unit_normal = unit_normal;
}