uniform vec3 light_position;
uniform vec3 camera_position;
uniform vec3 shading;

vec3 float_to_color(float value, float min_val, float max_val, vec3[9] colormap_data){
    float alpha = clamp((value - min_val) / (max_val - min_val), 0.0, 1.0);
    int disc_alpha = min(int(alpha * 8), 7);
    return mix(
        colormap_data[disc_alpha],
        colormap_data[disc_alpha + 1],
        8.0 * alpha - disc_alpha
    );
}


vec4 add_light(vec4 color, vec3 point, vec3 unit_normal){
    if(shading == vec3(0.0)) return color;

    float reflectiveness = shading.x;
    float gloss = shading.y;
    float shadow = shading.z;

    vec4 result = color;
    vec3 to_camera = normalize(camera_position - point);
    vec3 to_light = normalize(light_position - point);

    float light_to_normal = dot(to_light, unit_normal);
    // When unit normal points towards light, brighten
    float bright_factor = max(light_to_normal, 0) * reflectiveness;
    // For glossy surface, add extra shine if light beam goes towards camera
    vec3 light_reflection = reflect(-to_light, unit_normal);
    float light_to_cam = dot(light_reflection, to_camera);
    float shine = gloss * exp(-3 * pow(1 - light_to_cam, 2));
    bright_factor += shine;

    result.rgb = mix(result.rgb, vec3(1.0), bright_factor);
    if (light_to_normal < 0){
        // Darken
        result.rgb = mix(
            result.rgb,
            vec3(0.0),
            max(-light_to_normal, 0) * shadow
        );
    }
    return result;
}

vec4 finalize_color(vec4 color, vec3 point, vec3 unit_normal){
    ///// INSERT COLOR FUNCTION HERE /////
    // The line above may be replaced by arbitrary code snippets, as per
    // the method Mobject.set_color_by_code
    return add_light(color, point, unit_normal);
}