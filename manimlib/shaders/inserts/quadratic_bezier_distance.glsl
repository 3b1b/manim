// All of this is with respect to a curve that's been rotated/scaled
// so that b0 = (0, 0) and b1 = (1, 0).  That is, b2 entirely
// determines the shape of the curve

uniform float joint_type;


vec2 bezier(float t, vec2 b2){
    return vec2(
        2 * t * (1 - t) + b2.x * t*t,
        b2.y * t * t
    );
}


float cube_root(float x){
    return sign(x) * pow(abs(x), 1.0 / 3.0);
}


int cubic_solve(float a, float b, float c, float d, out float roots[3]){
    // Normalize so a = 1
    b = b / a;
    c = c / a;
    d = d / a;

    float  p = c - b*b / 3.0;
    float  q = b * (2.0*b*b - 9.0*c) / 27.0 + d;
    float p3 = p*p*p;
    float  disc = q*q + 4.0*p3 / 27.0;
    float offset = -b / 3.0;
    if(disc >= 0.0){
        float z = sqrt(disc);
        float u = (-q + z) / 2.0;
        float v = (-q - z) / 2.0;
        u = cube_root(u);
        v = cube_root(v);
        roots[0] = offset + u + v;
        return 1;
    }
    float u = sqrt(-p / 3.0);
    float v = acos(-sqrt( -27.0 / p3) * q / 2.0) / 3.0;
    float m = cos(v);
    float n = sin(v) * 1.732050808;

    float all_roots[3] = float[3](
        offset + u * (n - m),
        offset - u * (n + m),
        offset + u * (m + m)
    );

    // Only accept roots with a positive derivative
    int n_valid_roots = 0;
    for(int i = 0; i < 3; i++){
        float r = all_roots[i];
        if(3*r*r + 2*b*r + c > 0){ 
            roots[n_valid_roots] = r;
            n_valid_roots++;
        }
    }
    return n_valid_roots;
}


float dist_to_line(vec2 p, vec2 b2){
    if(joint_type == 1){
        float t = p.x / b2.x;
        if (t < 0) return length(p);
        if (t > 1) return distance(p, b2);
    }
    return abs(p.y);
}


float dist_to_point_on_curve(vec2 p, float t, vec2 b2){
    return length(p - bezier(t, b2));
}


float min_dist_to_curve(vec2 p, vec2 b2, float degree){
    // Check if curve is really a a line
    if(degree == 1) return dist_to_line(p, b2);

    // Try finding the exact sdf by solving the equation
    // (d/dt) dist^2(t) = 0, which amount to the following
    // cubic.
    float xm2 = uv_b2.x - 2.0;
    float y = uv_b2.y;
    float a = xm2*xm2 + y*y;
    float b = 3 * xm2;
    float c = -(p.x*xm2 + p.y*y) + 2;
    float d = -p.x;

    float roots[3];
    int n = cubic_solve(a, b, c, d, roots);  
    // At most 2 roots will have been populated.
    float d0 = dist_to_point_on_curve(p, roots[0], b2);
    if(n == 1) return d0;
    float d1 = dist_to_point_on_curve(p, roots[1], b2);
    return min(d0, d1);
}