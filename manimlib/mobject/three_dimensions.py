from manimlib.constants import *
from manimlib.mobject.geometry import Square
from manimlib.mobject.types.surface_mobject import SurfaceMobject
from manimlib.mobject.types.vectorized_mobject import VGroup


class ParametricSurface(SurfaceMobject):
    CONFIG = {
        "u_range": (0, 1),
        "v_range": (0, 1),
        "resolution": (32, 32),
        "surface_piece_config": {},
        "fill_color": BLUE_D,
        "fill_opacity": 1.0,
        "checkerboard_colors": [BLUE_D, BLUE_E],
        "stroke_color": LIGHT_GREY,
        "stroke_width": 0.5,
        "should_make_jagged": False,
        "pre_function_handle_to_anchor_scale_factor": 0.00001,
    }

    def __init__(self, function=None, **kwargs):
        if function is None:
            self.uv_func = self.func
        else:
            self.uv_func = function
        super().__init__(**kwargs)

    def init_points(self):
        epsilon = 1e-6   # For differentials
        nu, nv = self.resolution
        u_range = np.linspace(*self.u_range, nu + 1)
        v_range = np.linspace(*self.v_range, nv + 1)
        # List of three grids, [Pure uv values, those nudged by du, those nudged by dv]
        uv_grids = [
            np.array([[[u, v] for v in v_range] for u in u_range])
            for (du, dv) in [(0, 0), (epsilon, 0), (0, epsilon)]
        ]
        point_grid, points_nudged_du, points_nudged_dv = [
            np.apply_along_axis(lambda p: self.uv_func(*p), 2, uv_grid)
            for uv_grid in uv_grids
        ]
        normal_grid = np.cross(
            (points_nudged_du - point_grid) / epsilon,
            (points_nudged_dv - point_grid) / epsilon,
        )

        self.set_points(
            self.get_triangle_ready_array_from_grid(point_grid),
            self.get_triangle_ready_array_from_grid(normal_grid),
        )

        # self.points = point_grid[indices]

    def get_triangle_ready_array_from_grid(self, grid):
        # Given a grid, say of points or normals, this returns an Nx3 array
        # whose rows are elements from this grid in such such a way that successive
        # triplets of points form triangles covering the grid.
        nu = grid.shape[0] - 1
        nv = grid.shape[1] - 1
        dim = grid.shape[2]
        arr = np.zeros((nu * nv * 6, dim))
        # To match the triangles covering this surface
        arr[0::6] = grid[:-1, :-1].reshape((nu * nv, 3))  # Top left
        arr[1::6] = grid[+1:, :-1].reshape((nu * nv, 3))  # Bottom left
        arr[2::6] = grid[:-1, +1:].reshape((nu * nv, 3))  # Top right
        arr[3::6] = grid[:-1, +1:].reshape((nu * nv, 3))  # Top right
        arr[4::6] = grid[+1:, :-1].reshape((nu * nv, 3))  # Bottom left
        arr[5::6] = grid[+1:, +1:].reshape((nu * nv, 3))  # Bottom right
        return arr

    def func(self, u, v):
        pass


# Sphere, cylinder, cube, prism

class Sphere(ParametricSurface):
    CONFIG = {
        "resolution": (12, 24),
        "radius": 1,
        "u_range": (0, PI),
        "v_range": (0, TAU),
    }

    def func(self, u, v):
        return self.radius * np.array([
            np.cos(v) * np.sin(u),
            np.sin(v) * np.sin(u),
            np.cos(u)
        ])


class Cube(VGroup):
    CONFIG = {
        "fill_opacity": 0.75,
        "fill_color": BLUE,
        "stroke_width": 0,
        "side_length": 2,
    }

    def init_points(self):
        for vect in IN, OUT, LEFT, RIGHT, UP, DOWN:
            face = Square(
                side_length=self.side_length,
                shade_in_3d=True,
            )
            face.flip()
            face.shift(self.side_length * OUT / 2.0)
            face.apply_matrix(z_to_vector(vect))

            self.add(face)


class Prism(Cube):
    CONFIG = {
        "dimensions": [3, 2, 1]
    }

    def init_points(self):
        Cube.init_points(self)
        for dim, value in enumerate(self.dimensions):
            self.rescale_to_fit(value, dim, stretch=True)
