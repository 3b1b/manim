#version 330

out vec2 v_im_coords;
out float v_opacity;

#INSERT mobject_uniforms.glsl
#INSERT emit_gl_Position.glsl
#INSERT read_data.glsl

// The image is four corners, in the order upper left, lower left, upper right, lower
// right, and these are the two triangles covering it
const int QUAD[6] = int[6](0, 1, 2, 2, 1, 3);

void main(){
    if (gl_VertexID >= 6){
        // Six vertices cover the image, and whatever else is drawn collapses
        gl_Position = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }
    int corner = QUAD[gl_VertexID];
    v_im_coords = read_vec2(corner, DATA_OFFSET_im_coords);
    v_opacity = read_float(corner, DATA_OFFSET_opacity);
    emit_gl_Position(read_vec3(corner, DATA_OFFSET_point));
}
