///// INSERT COLOR_MAP FUNCTION HERE /////

vec4 add_light(vec4 color,
               vec3 point,
               vec3 unit_normal,
               vec3 light_coords,
               float gloss,
               float shadow){
    ///// INSERT COLOR FUNCTION HERE /////
    // The line above may be replaced by arbitrary code snippets, as per
    // the method Mobject.set_color_by_code
    if(gloss == 0.0 && shadow == 0.0) return color;

    // TODO, do we actually want this?  It effectively treats surfaces as two-sided
    if(unit_normal.z < 0){
            unit_normal *= -1;
    }

    // TODO, read this in as a uniform?
    float camera_distance = 6;  
    // Assume everything has already been rotated such that camera is in the z-direction
    vec3 to_camera = vec3(0, 0, camera_distance) - point;
    vec3 to_light = light_coords - point;
    vec3 light_reflection = -to_light + 2 * unit_normal * dot(to_light, unit_normal);
    float dot_prod = dot(normalize(light_reflection), normalize(to_camera));
    float shine = gloss * exp(-3 * pow(1 - dot_prod, 2));
    float dp2 = dot(normalize(to_light), unit_normal);
    float darkening = mix(1, max(dp2, 0), shadow);
    return vec4(
            darkening * mix(color.rgb, vec3(1.0), shine),
            color.a
    );
}

vec4 finalize_color(vec4 color,
                    vec3 point,
                    vec3 unit_normal,
                    vec3 light_coords,
                    float gloss,
                    float shadow){
    // Put insertion here instead
    return add_light(color, point, unit_normal, light_coords, gloss, shadow);
}