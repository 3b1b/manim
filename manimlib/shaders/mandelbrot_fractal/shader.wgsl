/*
The Mandelbrot set, or one of its Julia sets, worked out a pixel at a time. The mobject is
one rectangle laid over a plane, so all the shaping happens in the fragment stage: each pixel
iterates z -> z^2 + c and is colored by how long it took to escape, or left black if it never
did.

Which of the two pictures is drawn depends on which of z and c the pixel stands for. When
mandelbrot is set, the pixel is c and the orbit starts at zero; otherwise c is held fixed at
parameter and the pixel is the orbit's own starting point.

Drawn by MandelbrotFractal and JuliaFractal, whose uniform_dtype says what mob holds here.
*/
#INSERT mobject_uniforms.wgsl
#INSERT frame_uniforms.wgsl
#INSERT read_data.wgsl
#INSERT project_point.wgsl
#INSERT quad_corners.wgsl
#INSERT finalize_color.wgsl
#INSERT complex_functions.wgsl
#INSERT clip_test.wgsl

// How far an orbit has to get before it is taken to be on its way to infinity
const OUTER_BOUND: f32 = 2.0;
// How many colors an escape time is spread across, which is how many mob.colors holds
const N_COLORS: u32 = 9u;

struct VertexOutput {
    @builtin(position) position: vec4f,
    @location(0) clip_distances: vec4f,
    @location(1) plane_point: vec3f,
}

@vertex
fn vs_main(@builtin(vertex_index) index: u32) -> VertexOutput {
    var out: VertexOutput;
    if (index >= VERTS_PER_QUAD) {
        out.position = vec4f(0.0, 0.0, 0.0, 1.0);
        return out;
    }
    let point = read_vec3(quad_corner(index), DATA_OFFSET_point);
    let projection = project_point(point);
    out.position = projection.position;
    out.clip_distances = projection.clip_distances;
    // Where the point sits on the plane the fractal is drawn over, which is what the
    // iteration is in terms of, rather than where it sits in the scene
    out.plane_point = (point - mob.offset) / mob.scale_factor;
    return out;
}

/*
The colormap, which is held as a row of four floats per color because that is what a block
puts an array element in, and read here as the three the color takes up.
*/
fn read_colors() -> array<vec3f, N_COLORS> {
    var held = mob.colors;
    var result: array<vec3f, N_COLORS>;
    for (var n = 0u; n < N_COLORS; n++) {
        result[n] = held[n].rgb;
    }
    return result;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4f {
    clip_test(in.clip_distances);

    let colors = read_colors();

    var z: vec2f;
    var c: vec2f;
    if (mob.mandelbrot != 0.0) {
        c = in.plane_point.xy;
        z = vec2f(0.0);
    } else {
        c = mob.parameter;
        z = in.plane_point.xy;
    }

    // Black stands for an orbit which never escaped, so whatever did overwrites this
    var color = vec3f(0.0);
    for (var n = 0; n < i32(mob.n_steps); n++) {
        z = complex_mult(z, z) + c;
        if (length(z) > OUTER_BOUND) {
            /*
            Counting whole steps alone would band the picture, so the step count is nudged
            by how far past the bound this orbit overshot, and by how far out c sits, both
            of which vary smoothly from one pixel to the next.
            */
            var escaped = f32(n);
            escaped += log(OUTER_BOUND) / log(length(z));
            escaped += 0.5 * length(c);
            color = float_to_color(sqrt(escaped), 1.5, 8.0, colors);
            break;
        }
    }

    return finalize_color(
        vec4f(color, mob.opacity), in.plane_point, vec3f(0.0, 0.0, 1.0),
    );
}
