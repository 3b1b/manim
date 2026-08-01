#version 330

uniform vec3 unit_normal;

out vec4 color;
out float fill_all;
// uv space is where the curve coincides with y = x^2
out vec2 uv_coords;

#INSERT emit_gl_Position.glsl
#INSERT finalize_color.glsl
#INSERT read_data.glsl

// Each bezier contributes two triangles: one reaching back to the mobject's base
// point, which together with those of the other beziers covers the interior of
// the path, and one hugging the curve itself, whose fragments outside the curve
// get cut away.
const int VERTS_PER_CURVE = 6;
// Consecutive beziers share an anchor, so curve n begins at record 2n
const int RECORD_STEP = 2;

// A quadratic bezier curve with these points coincides with y = x^2
const vec2 SIMPLE_QUADRATIC[3] = vec2[3](
    vec2(0.0, 0.0),
    vec2(0.5, 0.0),
    vec2(1.0, 1.0)
);


void main(){
    int curve = gl_VertexID / VERTS_PER_CURVE;
    int corner = gl_VertexID % VERTS_PER_CURVE;
    int record = RECORD_STEP * curve;

    vec3 controls[3] = vec3[3](
        read_vec3(record + 0, DATA_OFFSET_point),
        read_vec3(record + 1, DATA_OFFSET_point),
        read_vec3(record + 2, DATA_OFFSET_point)
    );
    vec4 colors[3] = vec4[3](
        read_vec4(record + 0, DATA_OFFSET_fill_rgba),
        read_vec4(record + 1, DATA_OFFSET_fill_rgba),
        read_vec4(record + 2, DATA_OFFSET_fill_rgba)
    );

    // Curves are marked as ended when the handle after the first anchor is set
    // equal to that anchor. Nothing to draw for those, or for a clear fill, so
    // collapse all six corners onto one point to leave no area to rasterize.
    bool blank = (controls[0] == controls[1]) ||
        (vec3(colors[0].a, colors[1].a, colors[2].a) == vec3(0.0));
    if (blank) {
        gl_Position = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }

    // The fan reaching back to the mobject's first point covers its interior
    vec3 base_point = read_vec3(0, DATA_OFFSET_point);

    // The first triangle fills in towards the base point, the second hugs the
    // curve. No orientation is computed for either, since the sign of their
    // contribution to the winding number comes for free from whether they end up
    // front or back facing once projected.
    int index = corner % 3;
    vec3 point;
    if (corner < 3) {
        fill_all = 1.0;
        point = vec3[3](base_point, controls[0], controls[2])[index];
        color = vec4[3](colors[1], colors[0], colors[2])[index];
    } else {
        fill_all = 0.0;
        point = controls[index];
        color = colors[index];
    }

    uv_coords = SIMPLE_QUADRATIC[index];
    color = finalize_color(color, point, unit_normal);
    emit_gl_Position(point);
}
