/*
A surface is a grid of points, whose mesh and whose normals are both worked out from the
grid itself rather than handed over, see surface_mesh.wgsl.
*/
#INSERT mobject_uniforms.wgsl
#INSERT frame_uniforms.wgsl
#INSERT read_data.wgsl
#INSERT project_point.wgsl
#INSERT surface_mesh.wgsl
#INSERT finalize_color.wgsl
#INSERT clip_test.wgsl

struct VertexOutput {
    @builtin(position) position: vec4f,
    @location(0) clip_distances: vec4f,
    @location(1) color: vec4f,
}

@vertex
fn vs_main(@builtin(vertex_index) index: u32) -> VertexOutput {
    var out: VertexOutput;
    let vertex = read_surface_vertex(index);
    if (!vertex.drawn) {
        out.position = vec4f(0.0, 0.0, 0.0, 1.0);
        return out;
    }
    let projection = project_point(vertex.point);
    out.position = projection.position;
    out.clip_distances = projection.clip_distances;
    out.color = finalize_color(
        read_vec4(vertex.index, DATA_OFFSET_rgba), vertex.point, vertex.normal,
    );
    return out;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4f {
    clip_test(in.clip_distances);
    return in.color;
}
