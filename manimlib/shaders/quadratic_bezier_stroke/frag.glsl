#version 330

in vec2 uv_coords;

in float uv_stroke_width;
in float uv_anti_alias_width;
in vec4 color;

in float is_linear;

out vec4 frag_color;

const float QUICK_DIST_WIDTH = 0.2;

float dist_to_curve(){
    // In the linear case, the curve will have
    // been set to equal the x axis
    if(bool(is_linear)) return abs(uv_coords.y);

    // Otherwise, find the distance from uv_coords to the curve y = x^2
    float x0 = uv_coords.x;
    float y0 = uv_coords.y;

    // This is a quick approximation for computing
    // the distance to the curve.
    // Evaluate F(x, y) = y - x^2
    // divide by its gradient's magnitude
    float Fxy = y0 - x0 * x0;
    float approx_dist = abs(Fxy) * inversesqrt(1.0 + 4 * x0 * x0);
    if(approx_dist < QUICK_DIST_WIDTH) return approx_dist;

    // Otherwise, solve for the minimal distance.
    // The distance squared between (x0, y0) and a point (x, x^2) looks like
    //
    // (x0 - x)^2 + (y0 - x^2)^2 = x^4 + (1 - 2y0)x^2 - 2x0 * x + (x0^2 + y0^2)
    //
    // Setting the derivative equal to zero (and rescaling) looks like
    // 
    // x^3 + (0.5 - y0) * x - 0.5 * x0 = 0
    //
    // Adapted from https://www.shadertoy.com/view/ws3GD7
    x0 = abs(x0);
    float p = (0.5 - y0) / 3.0;  // p / 3 in usual Cardano's formula notation
    float q = 0.25 * x0;         // -q / 2 in usual Cardano's formula notation
    float disc = q*q + p*p*p;
    float r = sqrt(abs(disc));

    float x = (disc > 0.0) ? 
        // 1 root
        pow(q + r, 1.0 / 3.0) + pow(abs(q - r), 1.0 / 3.0) * sign(-p) :
        // 3 roots
        2.0 * cos(atan(r, q) / 3.0) * sqrt(-p);

    return length(vec2(x0 - x, y0 - x * x));
}


void main() {
    if (uv_stroke_width == 0) discard;
    frag_color = color;

    // sdf for the region around the curve we wish to color.
    float signed_dist = dist_to_curve() - 0.5 * uv_stroke_width;

    frag_color.a *= smoothstep(0.5, -0.5, signed_dist / uv_anti_alias_width);
}