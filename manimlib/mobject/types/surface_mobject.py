import numpy as np
import moderngl

from PIL import Image

from manimlib.constants import *
from manimlib.mobject.mobject import Mobject
from manimlib.utils.color import color_to_rgba
from manimlib.utils.images import get_full_raster_image_path


class SurfaceMobject(Mobject):
    CONFIG = {
        "color": GREY,
        "opacity": 1,
        "gloss": 0.3,
        "render_primative": moderngl.TRIANGLES,
        "vert_shader_file": "surface_vert.glsl",
        "frag_shader_file": "surface_frag.glsl",
        "shader_dtype": [
            ('point', np.float32, (3,)),
            ('normal', np.float32, (3,)),
            ('color', np.float32, (4,)),
            ('gloss', np.float32, (1,)),
        ]
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def init_points(self):
        self.points = np.zeros((0, self.dim))
        self.normals = np.zeros((0, self.dim))

    def init_colors(self):
        self.set_color(self.color, self.opacity)

    def set_points(self, points, normals=None):
        self.points = np.array(points)
        if normals is None:
            v01 = points[1:-1] - points[:-2]
            v02 = points[2:] - points[:-2]
            crosses = np.cross(v01, v02)
            crosses[1::2] *= -1  # Because of reversed orientation of every other triangle in the strip
            self.normals = np.vstack([
                crosses,
                crosses[-1:].repeat(2, 0)  # Repeat last entry twice
            ])
        else:
            self.normals = np.array(normals)

    def set_color(self, color, opacity):
        # TODO, allow for multiple colors
        rgba = color_to_rgba(color, opacity)
        self.rgbas = np.array([rgba])

    def set_gloss(self, gloss, family=True):
        self.gloss = gloss
        if family:
            for sm in self.submobjects:
                sm.set_gloss(gloss, family)
        return self

    def apply_function(self, function, **kwargs):
        # Apply it to infinitesimal neighbors to preserve normals
        pass

    def rotate(self, axis, angle, **kwargs):
        # Account for normals
        pass

    def stretch(self, factor, dim, **kwargs):
        # Account for normals
        pass

    def get_shader_data(self):
        data = self.get_blank_shader_data_array(len(self.points))
        data["point"] = self.points
        data["normal"] = self.normals
        data["color"] = self.rgbas
        data["gloss"] = self.gloss
        return data


class ParametricSurface(SurfaceMobject):
    CONFIG = {
        "u_range": (0, 1),
        "v_range": (0, 1),
        "resolution": (100, 100),
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
            np.array([[[u + du, v + dv] for v in v_range] for u in u_range])
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

    def get_triangle_ready_array_from_grid(self, grid):
        # Given a grid, say of points or normals, this returns an Nx3 array
        # whose rows are elements from this grid in such such a way that successive
        # triplets of points form triangles covering the grid.
        nu, nv, dim = grid.shape
        nu -= 1
        nv -= 1
        arr = np.zeros((nu * nv * 6, dim))
        # To match the triangles covering this surface
        arr[0::6] = grid[:-1, :-1].reshape((nu * nv, dim))  # Top left
        arr[1::6] = grid[+1:, :-1].reshape((nu * nv, dim))  # Bottom left
        arr[2::6] = grid[:-1, +1:].reshape((nu * nv, dim))  # Top right
        arr[3::6] = grid[:-1, +1:].reshape((nu * nv, dim))  # Top right
        arr[4::6] = grid[+1:, :-1].reshape((nu * nv, dim))  # Bottom left
        arr[5::6] = grid[+1:, +1:].reshape((nu * nv, dim))  # Bottom right
        return arr

    def func(self, u, v):
        raise Exception("Not implemented")


class TexturedSurfaceMobject(SurfaceMobject):
    CONFIG = {
        "vert_shader_file": "textured_surface_vert.glsl",
        "frag_shader_file": "textured_surface_frag.glsl",
        "shader_dtype": [
            ('point', np.float32, (3,)),
            ('normal', np.float32, (3,)),
            ('im_coords', np.float32, (2,)),
            ('opacity', np.float32, (1,)),
            ('gloss', np.float32, (1,)),
        ]
    }

    def __init__(self, uv_surface, filename, **kwargs):
        if not isinstance(uv_surface, ParametricSurface):
            raise Exception("uv_surface must be of type Paramet")
        path = get_full_raster_image_path(filename)
        self.image = Image.open(path)
        self.texture_path = path
        super().__init__(**kwargs)

        self.set_points(
            uv_surface.points,
            uv_surface.normals,
        )
        self.opacity = uv_surface.rgbas[:, 3]
        self.gloss = uv_surface.gloss

        # Init im_coords
        nu, nv = uv_surface.resolution
        u_range = np.linspace(0, 1, nu + 1)
        v_range = np.linspace(0, 1, nv + 1)  # Upsidedown?
        uv_grid = np.array([[[u, v] for v in v_range] for u in u_range])
        self.im_coords = uv_surface.get_triangle_ready_array_from_grid(uv_grid)

    def set_opacity(self, opacity, family=True):
        self.opacity = opacity
        if family:
            for sm in self.submobjects:
                sm.set_opacity(opacity, family)
        return self

    def get_shader_data(self):
        data = self.get_blank_shader_data_array(len(self.points))
        data["point"] = self.points
        data["normal"] = self.normals
        data["im_coords"] = self.im_coords
        data["opacity"] = self.opacity
        data["gloss"] = self.gloss
        return data
