#INSERT frame_uniforms.glsl

/*
Points fixed in frame skip the view matrix (see emit_gl_Position), so they are drawn
in the coordinates of a default scale frame, whereas everything else is drawn in scene
coordinates. The functions below give the size, in whichever of those two spaces is
being drawn, of the units a screen relative length might be measured in, so that such
lengths can be converted without any dependence on the camera's zoom level.
*/

float get_frame_unit_size(){
    // Size of one unit of a default scale frame
    return mix(frame_scale, 1.0, is_fixed_in_frame);
}

float get_pixel_unit_size(){
    // Size of one pixel. Note that pixel_size is measured in scene coordinates,
    // so it must be scaled back down for points fixed in frame.
    return pixel_size * get_frame_unit_size() / frame_scale;
}
