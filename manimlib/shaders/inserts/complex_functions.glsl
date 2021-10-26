vec2 complex_mult(vec2 z, vec2 w){
    return vec2(z.x * w.x - z.y * w.y, z.x * w.y + z.y * w.x);
}

vec2 complex_div(vec2 z, vec2 w){
    return complex_mult(z, vec2(w.x, -w.y)) / (w.x * w.x + w.y * w.y);
}

vec2 complex_pow(vec2 z, int n){
    vec2 result = vec2(1.0, 0.0);
    for(int i = 0; i < n; i++){
        result = complex_mult(result, z);
    }
    return result;
}