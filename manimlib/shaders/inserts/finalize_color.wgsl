fn float_to_color(value: f32, min_val: f32, max_val: f32, colormap_data: array<vec3f, 9>) -> vec3f {
    let alpha = clamp((value - min_val) / (max_val - min_val), 0.0, 1.0);
    let disc_alpha = min(i32(alpha * 8.0), 7);
    var map = colormap_data;
    return mix(map[disc_alpha], map[disc_alpha + 1], 8.0 * alpha - f32(disc_alpha));
}

fn add_light(color: vec4f, point: vec3f, normal: vec3f) -> vec4f {
    if (all(mob.shading == vec3f(0.0))) { return color; }

    let reflectiveness = mob.shading.x;
    let gloss = mob.shading.y;
    let shadow = mob.shading.z;

    var result = color;
    let to_camera = normalize(frame.camera_position - point);
    let to_light = normalize(frame.light_position - point);

    let light_to_normal = dot(to_light, normal);
    // When unit normal points towards light, brighten
    var bright_factor = max(light_to_normal, 0.0) * reflectiveness;
    // For glossy surface, add extra shine if light beam goes towards camera
    let light_reflection = reflect(-to_light, normal);
    let light_to_cam = dot(light_reflection, to_camera);
    bright_factor += gloss * exp(-3.0 * pow(1.0 - light_to_cam, 2.0));

    result = vec4f(mix(result.rgb, vec3f(1.0), bright_factor), result.a);
    if (light_to_normal < 0.0) {
        // Darken
        result = vec4f(
            mix(result.rgb, vec3f(0.0), max(-light_to_normal, 0.0) * shadow),
            result.a,
        );
    }
    return result;
}

fn finalize_color(color_in: vec4f, point: vec3f, normal: vec3f) -> vec4f {
    var color = color_in;
    ///// INSERT COLOR FUNCTION HERE /////
    // The line above may be replaced by arbitrary code snippets, as per the method
    // Mobject.set_color_by_code
    return add_light(color, point, normal);
}
