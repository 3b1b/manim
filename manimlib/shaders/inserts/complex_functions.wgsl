/*
Arithmetic on complex numbers held as a pair of floats, for the shaders which iterate a
function of one and color a pixel by where it ends up.
*/

fn complex_mult(z: vec2f, w: vec2f) -> vec2f {
    return vec2f(z.x * w.x - z.y * w.y, z.x * w.y + z.y * w.x);
}

fn complex_div(z: vec2f, w: vec2f) -> vec2f {
    return complex_mult(z, vec2f(w.x, -w.y)) / (w.x * w.x + w.y * w.y);
}

fn complex_pow(z: vec2f, n: i32) -> vec2f {
    var result = vec2f(1.0, 0.0);
    for (var i = 0; i < n; i++) {
        result = complex_mult(result, z);
    }
    return result;
}
