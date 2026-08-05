/*
Newton's method run at every pixel of a plane, and the pixel colored by which root the
method converged on. The boundaries between those basins are the fractal.

Two pictures come out of this. Normally the pixel is where the method starts from, and the
polynomial is the one whose coefficients were handed over. When is_parameter_space is set the
pixel is instead a root of a cubic whose other two roots are held fixed, and the method
always starts from the center of the three, so what is drawn is a map of which polynomials
behave which way rather than of which seeds do.

Drawn by NewtonFractal and MetaNewtonFractal, whose uniform_dtype says what mob holds here.
*/
#INSERT mobject_uniforms.wgsl
#INSERT frame_uniforms.wgsl
#INSERT read_data.wgsl
#INSERT project_point.wgsl
#INSERT quad_corners.wgsl
#INSERT finalize_color.wgsl
#INSERT complex_functions.wgsl
#INSERT clip_test.wgsl

/*
Room for a polynomial of degree five, which is one more coefficient than that, and for as
many roots as it has. A complex number is held in a uniform block as the first two of the
four floats a block gives an array element, and is worked with here as the two it needs.
Both arrays are copied into a variable wherever they are indexed by anything worked out at
run time, WGSL only indexing an array which is held in one.
*/
const N_COEFS: u32 = 6u;
const N_ROOTS: u32 = 5u;
alias Coefs = array<vec2f, N_COEFS>;
alias Roots = array<vec2f, N_ROOTS>;

fn read_coefs() -> Coefs {
    var held = mob.coefs;
    var result: Coefs;
    for (var n = 0u; n < N_COEFS; n++) {
        result[n] = held[n].xy;
    }
    return result;
}

fn read_roots() -> Roots {
    var held = mob.roots;
    var result: Roots;
    for (var n = 0u; n < N_ROOTS; n++) {
        result[n] = held[n].xy;
    }
    return result;
}

// How near a root the method has to land before it counts as having found it
const CLOSE_ENOUGH: f32 = 1e-3;

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
    // polynomial is in terms of, rather than where it sits in the scene
    out.plane_point = (point - mob.offset) / mob.scale_factor;
    return out;
}

fn poly(z: vec2f, coefs: Coefs) -> vec2f {
    var terms = coefs;
    var result = vec2f(0.0);
    for (var n = 0; n < i32(mob.n_roots) + 1; n++) {
        result += complex_mult(terms[n], complex_pow(z, n));
    }
    return result;
}

fn dpoly(z: vec2f, coefs: Coefs) -> vec2f {
    var terms = coefs;
    var result = vec2f(0.0);
    for (var n = 1; n < i32(mob.n_roots) + 1; n++) {
        result += f32(n) * complex_mult(terms[n], complex_pow(z, n - 1));
    }
    return result;
}

fn newton_step(z: vec2f, coefs: Coefs) -> vec2f {
    return complex_div(poly(z, coefs), dpoly(z, coefs));
}

struct Search {
    root: vec2f,
    // How many steps it took, nudged by how much nearer than it had to be it ended up, so
    // that shading by this does not band
    steps_taken: f32,
}

fn seek_root(start: vec2f, coefs: Coefs, max_steps: i32) -> Search {
    var result: Search;
    result.root = start;
    var step_size = 0.0;
    for (var i = 0; i < max_steps; i++) {
        result.steps_taken = f32(i);
        let step = newton_step(result.root, coefs);
        step_size = length(step);
        if (step_size < CLOSE_ENOUGH) {
            break;
        }
        result.root -= step;
    }
    result.steps_taken -= log(step_size) / log(CLOSE_ENOUGH);
    return result;
}

fn cubic_through(r0: vec2f, r1: vec2f, r2: vec2f) -> Coefs {
    var coefs = Coefs();
    coefs[0] = -complex_mult(complex_mult(r0, r1), r2);
    coefs[1] = complex_mult(r0, r1) + complex_mult(r0, r2) + complex_mult(r1, r2);
    coefs[2] = -(r0 + r1 + r2);
    coefs[3] = vec2f(1.0, 0.0);
    return coefs;
}

/*
How much the four points a little way around this one spread apart under the same number of
steps. Where the method is well behaved they stay together and this is near zero; on the
boundary between two basins they fly to different roots, which is what the highlight picks
out.
*/
fn basin_spread(z: vec2f, coefs: Coefs, radius: f32) -> f32 {
    var samples = array<vec2f, 4>(
        z + vec2f(radius, 0.0),
        z + vec2f(-radius, 0.0),
        z + vec2f(0.0, radius),
        z + vec2f(0.0, -radius),
    );
    for (var i = 0; i < 4; i++) {
        for (var j = 0; j < i32(mob.n_steps); j++) {
            samples[i] -= newton_step(samples[i], coefs);
        }
    }
    var spread = 0.0;
    for (var i = 0; i < 4; i++) {
        spread = max(spread, distance(samples[i], samples[(i + 1) % 4]));
    }
    return spread;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4f {
    clip_test(in.clip_distances);

    var coefs = read_coefs();
    var roots = read_roots();
    var colors = mob.colors;

    var start = in.plane_point.xy;
    if (mob.is_parameter_space > 0.0) {
        // The pixel is the cubic's third root, the other two being held fixed, and the
        // method always sets off from the center of the three
        roots[2] = start;
        coefs = cubic_through(roots[0], roots[1], roots[2]);
        start = -coefs[2] / 3.0;
    }

    let search = seek_root(start, coefs, i32(mob.n_steps));

    var color = vec4f(0.0);
    var nearest = 1e10;
    for (var i = 0; i < i32(mob.n_roots); i++) {
        let dist = distance(roots[i], search.root);
        if (dist < nearest) {
            nearest = dist;
            color = colors[i];
        }
    }
    // Brighten what took longer to settle, so that the basins show their own structure
    let saturation = mob.saturation_factor;
    color *= 1.0 + (0.01 * saturation) * (search.steps_taken - 2.0 * saturation);

    if (mob.black_for_cycles > 0.0 && nearest > CLOSE_ENOUGH) {
        // It landed on no root at all, having fallen into a cycle instead
        color = vec4f(0.0, 0.0, 0.0, 1.0);
    }

    if (mob.julia_highlight > 0.0) {
        color *= smoothstep(0.0, 0.1, basin_spread(start, coefs, mob.julia_highlight));
    }

    return finalize_color(color, in.plane_point, vec3f(0.0, 0.0, 1.0));
}
