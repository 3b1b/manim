vec4 add_light(vec4 raw_color, vec3 point, vec3 unit_normal, vec3 light_coords, float gloss){
    if(gloss == 0.0) return raw_color;

    // TODO, do we actually want this?  It effectively treats surfaces as two-sided
    if(unit_normal.z < 0){
        unit_normal *= -1;
    }

    float camera_distance = 6;  // TODO, read this in as a uniform?
    // Assume everything has already been rotated such that camera is in the z-direction
    vec3 to_camera = vec3(0, 0, camera_distance) - point;
    vec3 to_light = light_coords - point;
    vec3 light_reflection = -to_light + 2 * unit_normal * dot(to_light, unit_normal);
    float dot_prod = dot(normalize(light_reflection), normalize(to_camera));
    float shine = gloss * exp(-3 * pow(1 - dot_prod, 2));
    float dp2 = dot(normalize(to_light), unit_normal);
    float shadow = ((dp2 + 2.0) / 3.0);  // TODO, this should come from the mobject in some way
    return vec4(
        shadow * mix(raw_color.rgb, vec3(1.0), shine),
        raw_color.a
    );
}