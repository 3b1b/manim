/*
A surface is sent as a grid of points, resolution.x rows of resolution.y of them, and
the mesh over that grid is worked out here rather than being handed over as a list of
triangle indices. Each square of the grid becomes a pair of triangles, so every vertex
asks which square it belongs to and which corner of it that makes it.

Six vertices are drawn for every point of the grid, one square's worth, which is one
row and one column more than there are squares to fill. Those spare ones collapse.
*/

// Which corner of a square each vertex of its two triangles sits at, as steps in
// (row, column) from the corner the square is named by
const ivec2 SQUARE_CORNERS[6] = ivec2[6](
    ivec2(0, 0), ivec2(1, 0), ivec2(0, 1),
    ivec2(0, 1), ivec2(1, 0), ivec2(1, 1)
);
const int VERTS_PER_SQUARE = 6;
// Under this, a step from one point of the grid to the next counts as no step at all
const float DEGENERATE_STEP = 1e-8;


int grid_index(ivec2 rc){
    ivec2 shape = ivec2(resolution);
    rc = clamp(rc, ivec2(0), shape - 1);
    return rc.x * shape.y + rc.y;
}


vec3 grid_point(ivec2 rc){
    return read_vec3(grid_index(rc), DATA_OFFSET_point);
}


/*
Which way the surface faces at a point of the grid, from the directions it runs in
either way from there, crossed with one another. Stepping to both neighbors, rather
than to one, keeps this from depending on which corner of which square a vertex is,
and clamping at the edges of the grid leaves the step one sided there.
*/
vec3 grid_normal(ivec2 rc){
    ivec2 row = ivec2(1, 0);
    ivec2 col = ivec2(0, 1);
    vec3 du = grid_point(rc + row) - grid_point(rc - row);
    vec3 dv = grid_point(rc + col) - grid_point(rc - col);
    /*
    A row or column of the grid may be a single point, as at the pole of a sphere, where
    stepping along it gets nowhere. A neighboring row or column stands in then, either
    side serving for whichever end of the grid it happens to be, since a step off the
    grid is clamped back onto the same row.
    */
    if (length(du) < DEGENERATE_STEP) du = grid_point(rc + row + col) - grid_point(rc - row + col);
    if (length(du) < DEGENERATE_STEP) du = grid_point(rc + row - col) - grid_point(rc - row - col);
    if (length(dv) < DEGENERATE_STEP) dv = grid_point(rc + col + row) - grid_point(rc - col + row);
    if (length(dv) < DEGENERATE_STEP) dv = grid_point(rc + col - row) - grid_point(rc - col - row);
    return normalize(cross(du, dv));
}


/*
The point this vertex sits at, which way the surface faces there, and the record it
should read anything else from. False for a vertex past the last row or column of
squares, which has nothing to draw.

Records may be a plain list of triangles rather than a grid, three records to each,
as an imported mesh is, which is what a resolution of zero says. Then a vertex is a
record of its own, and the surface faces whichever way its triangle does.
*/
bool read_surface_vertex(out vec3 point, out vec3 normal, out int index){
    if (resolution.x == 0){
        index = gl_VertexID;
        point = read_vec3(index, DATA_OFFSET_point);
        int first = 3 * (index / 3);
        vec3 corner = read_vec3(first, DATA_OFFSET_point);
        normal = normalize(cross(
            read_vec3(first + 1, DATA_OFFSET_point) - corner,
            read_vec3(first + 2, DATA_OFFSET_point) - corner
        ));
        return true;
    }

    ivec2 shape = ivec2(resolution);
    int square = gl_VertexID / VERTS_PER_SQUARE;
    ivec2 rc = ivec2(square / shape.y, square % shape.y);
    if (rc.x + 1 >= shape.x || rc.y + 1 >= shape.y){
        return false;
    }
    rc += SQUARE_CORNERS[gl_VertexID % VERTS_PER_SQUARE];

    index = grid_index(rc);
    point = grid_point(rc);
    normal = grid_normal(rc);
    return true;
}
