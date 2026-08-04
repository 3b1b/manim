/*
A surface is sent as a grid of points, resolution.x rows of resolution.y of them, and the
mesh over that grid is worked out here rather than being handed over as a list of triangle
indices. Each square of the grid becomes a pair of triangles, so every vertex asks which
square it belongs to and which corner of it that makes it.

Six vertices are drawn for every point of the grid, one square's worth, which is one row and
one column more than there are squares to fill. Those spare ones collapse.
*/

// Which corner of a square each vertex of its two triangles sits at, as steps in
// (row, column) from the corner the square is named by
const SQUARE_CORNERS = array<vec2i, 6>(
    vec2i(0, 0), vec2i(1, 0), vec2i(0, 1),
    vec2i(0, 1), vec2i(1, 0), vec2i(1, 1),
);
const VERTS_PER_SQUARE: u32 = 6u;
// Under this, a step from one point of the grid to the next counts as no step at all
const DEGENERATE_STEP: f32 = 1e-8;

// A point of the surface, which way it faces there, and the record everything else about it
// is read from. Not drawn at all for a vertex past the last row or column of squares.
struct SurfaceVertex {
    drawn: bool,
    point: vec3f,
    normal: vec3f,
    index: u32,
}

fn grid_index(rc_in: vec2i) -> u32 {
    let shape = vec2i(mob.resolution);
    let rc = clamp(rc_in, vec2i(0), shape - vec2i(1));
    return u32(rc.x * shape.y + rc.y);
}

fn grid_point(rc: vec2i) -> vec3f {
    return read_vec3(grid_index(rc), DATA_OFFSET_point);
}

/*
Which way the surface faces at a point of the grid, from the directions it runs in either
way from there, crossed with one another. Stepping to both neighbors, rather than to one,
keeps this from depending on which corner of which square a vertex is, and clamping at the
edges of the grid leaves the step one sided there.
*/
fn grid_normal(rc: vec2i) -> vec3f {
    let row = vec2i(1, 0);
    let col = vec2i(0, 1);
    var du = grid_point(rc + row) - grid_point(rc - row);
    var dv = grid_point(rc + col) - grid_point(rc - col);
    /*
    A row or column of the grid may be a single point, as at the pole of a sphere, where
    stepping along it gets nowhere. A neighboring row or column stands in then, either side
    serving for whichever end of the grid it happens to be, since a step off the grid is
    clamped back onto the same row.
    */
    if (length(du) < DEGENERATE_STEP) {
        du = grid_point(rc + row + col) - grid_point(rc - row + col);
    }
    if (length(du) < DEGENERATE_STEP) {
        du = grid_point(rc + row - col) - grid_point(rc - row - col);
    }
    if (length(dv) < DEGENERATE_STEP) {
        dv = grid_point(rc + col + row) - grid_point(rc - col + row);
    }
    if (length(dv) < DEGENERATE_STEP) {
        dv = grid_point(rc + col - row) - grid_point(rc - col - row);
    }
    return normalize(cross(du, dv));
}

/*
Records may be a plain list of triangles rather than a grid, three records to each, as an
imported mesh is, which is what a resolution of zero says. Then a vertex is a record of its
own, and the surface faces whichever way its triangle does.
*/
fn read_surface_vertex(vertex_index: u32) -> SurfaceVertex {
    var out: SurfaceVertex;
    out.drawn = true;
    if (mob.resolution.x == 0.0) {
        out.index = vertex_index;
        out.point = read_vec3(vertex_index, DATA_OFFSET_point);
        let first = 3u * (vertex_index / 3u);
        let corner = read_vec3(first, DATA_OFFSET_point);
        out.normal = normalize(cross(
            read_vec3(first + 1u, DATA_OFFSET_point) - corner,
            read_vec3(first + 2u, DATA_OFFSET_point) - corner,
        ));
        return out;
    }

    let shape = vec2i(mob.resolution);
    let square = i32(vertex_index / VERTS_PER_SQUARE);
    var rc = vec2i(square / shape.y, square % shape.y);
    if (rc.x + 1 >= shape.x || rc.y + 1 >= shape.y) {
        out.drawn = false;
        return out;
    }
    var corners = SQUARE_CORNERS;
    rc += corners[vertex_index % VERTS_PER_SQUARE];

    out.index = grid_index(rc);
    out.point = grid_point(rc);
    out.normal = grid_normal(rc);
    return out;
}
