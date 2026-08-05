/*
Points fixed in frame skip the view matrix (see project_point), so they are drawn in the
coordinates of a default scale frame, whereas everything else is drawn in scene coordinates.
The functions below give the size, in whichever of those two spaces is being drawn, of the
units a screen relative length might be measured in, so that such lengths can be converted
without any dependence on the camera's zoom level.
*/

fn get_frame_unit_size() -> f32 {
    // Size of one unit of a default scale frame
    return mix(frame.frame_scale, 1.0, mob.is_fixed_in_frame);
}

fn get_pixel_unit_size() -> f32 {
    // Size of one pixel. Note that pixel_size is measured in scene coordinates, so it must
    // be scaled back down for points fixed in frame.
    return frame.pixel_size * get_frame_unit_size() / frame.frame_scale;
}
