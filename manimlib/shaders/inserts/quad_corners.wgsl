/*
For the mobjects which are one rectangle: four points, in the order upper left, lower left,
upper right, lower right, covered by two triangles. Any vertex past the sixth belongs to no
triangle, and the shader collapses it onto a point so that there is nothing to rasterize.
*/
const VERTS_PER_QUAD: u32 = 6u;

fn quad_corner(index: u32) -> u32 {
    // Copied out of the constant because WGSL only indexes an array held in a variable
    var corners = array<u32, 6>(0u, 1u, 2u, 2u, 1u, 3u);
    return corners[index];
}
