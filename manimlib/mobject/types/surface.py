from __future__ import annotations

import numpy as np
import trimesh
import pywavefront
import logging
from pathlib import Path

from manimlib.constants import GREY
from manimlib.constants import OUT
from manimlib.mobject.mobject import Mobject
from manimlib.renderer.drawing import SurfaceDrawing
from manimlib.mobject.mobject import Group
from manimlib.utils.bezier import integer_interpolate
from manimlib.utils.bezier import interpolate
from manimlib.utils.bezier import inverse_interpolate
from manimlib.utils.images import get_full_raster_image_path
from manimlib.utils.images import get_full_three_d_model_path
from manimlib.utils.iterables import listify
from manimlib.utils.iterables import resize_with_interpolation
from manimlib.utils.simple_functions import clip
from manimlib.utils.space_ops import normalize_along_axis
from manimlib.utils.paths import straight_path
from manimlib.renderer.uniform_block import COMMON_UNIFORMS
from manimlib.renderer.uniform_block import uniform_block_dtype

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Iterable, Sequence, Tuple


    from manimlib.camera.camera import Camera
    from manimlib.typing import ManimColor, Vect3, Vect3Array, Self


def norms_along_axis(vectors: Vect3Array) -> np.ndarray:
    return np.linalg.norm(vectors, axis=-1, keepdims=True)


class Surface(Mobject):
    drawing_class: type = SurfaceDrawing
    shader_file: str = "surface.wgsl"
    # Points are sent as the grid they sample, and the vertex shader works out the mesh
    # over it, expanding each of them into one square's worth of vertices. See
    # inserts/surface_mesh.wgsl
    verts_per_record: int = 6
    data_dtype: np.dtype = np.dtype([
        ('point', np.float32, (3,)),
        ('rgba', np.float32, (4,)),
    ])
    uniform_dtype: np.dtype = uniform_block_dtype(
        *COMMON_UNIFORMS,
        ("resolution", 2),
    )
    # What is_opaque last answered, which it works out afresh whenever the data has moved on
    opaque: bool = True

    def __init__(
        self,
        color: ManimColor = GREY,
        shading: Tuple[float, float, float] = (0.3, 0.2, 0.4),
        depth_test: bool = True,
        u_range: Tuple[float, float] = (0.0, 1.0),
        v_range: Tuple[float, float] = (0.0, 1.0),
        # Resolution counts number of points sampled, which for
        # each coordinate is one more than the the number of
        # rows/columns of approximating squares
        resolution: Tuple[int, int] = (101, 101),
        preferred_creation_axis: int = 1,
        # Only wanted by a surface which folds over itself, see set_sort_to_camera
        sort_to_camera: bool = False,
        **kwargs
    ):
        self.u_range = u_range
        self.v_range = v_range
        # Handed to the uniforms below, which is where it lives from then on, see
        # get_resolution
        self.initial_resolution = resolution
        self.preferred_creation_axis = preferred_creation_axis
        self.sort_to_camera = sort_to_camera
        # Which version of the data the answer below was worked out from, none having been,
        # see is_opaque
        self.opaque_version = 0

        super().__init__(
            **kwargs,
            color=color,
            shading=shading,
            depth_test=depth_test,
        )

    def init_uniforms(self):
        super().init_uniforms()
        self.uniforms["resolution"] = self.initial_resolution

    def get_resolution(self) -> Tuple[int, int]:
        """
        How many rows and columns of points the surface samples. Kept among the uniforms,
        the vertex shader needing it to work the mesh over them out, so this is the one
        place it is written down.
        """
        nu, nv = self.uniforms["resolution"].astype(int)
        return (int(nu), int(nv))

    def set_resolution(self, resolution: Tuple[int, int]) -> Self:
        # It has to match how many points there are, see has_grid
        self.uniforms["resolution"] = resolution
        return self

    def interpolate(
        self,
        mobject1: Mobject,
        mobject2: Mobject,
        alpha: float,
        path_func: Callable[[np.ndarray, np.ndarray, float], np.ndarray] = straight_path
    ) -> Self:
        # A grid of one shape cannot become a grid of another partway, so this one keeps
        # its own, as it keeps its own number of points, which the two have been aligned to
        resolution = self.get_resolution()
        super().interpolate(mobject1, mobject2, alpha, path_func)
        self.set_resolution(resolution)
        return self

    def uv_func(self, u: float, v: float) -> tuple[float, float, float]:
        # To be implemented in subclasses
        return (u, v, 0.0)

    def init_points(self):
        nu, nv = self.get_resolution()
        points = np.apply_along_axis(
            lambda p: self.uv_func(*p), 2, self.get_uv_grid()
        ).reshape((nu * nv, self.dim))
        self.set_points(points)

    def get_uv_grid(self) -> np.array:
        """
        Returns an (nu, nv, 2) array of all pairs of u, v values, where
        (nu, nv) is the resolution
        """
        nu, nv = self.get_resolution()
        u_range = np.linspace(*self.u_range, nu)
        v_range = np.linspace(*self.v_range, nv)
        U, V = np.meshgrid(u_range, v_range, indexing='ij')
        return np.stack([U, V], axis=-1)

    def uv_to_point(self, u, v):
        nu, nv = self.get_resolution()
        verts_by_uv = np.reshape(self.get_points(), (nu, nv, self.dim))

        alpha1 = clip(inverse_interpolate(*self.u_range[:2], u), 0, 1)
        alpha2 = clip(inverse_interpolate(*self.v_range[:2], v), 0, 1)
        scaled_u = alpha1 * (nu - 1)
        scaled_v = alpha2 * (nv - 1)
        u_int = int(scaled_u)
        v_int = int(scaled_v)
        u_int_plus = min(u_int + 1, nu - 1)
        v_int_plus = min(v_int + 1, nv - 1)

        a = verts_by_uv[u_int, v_int, :]
        b = verts_by_uv[u_int, v_int_plus, :]
        c = verts_by_uv[u_int_plus, v_int, :]
        d = verts_by_uv[u_int_plus, v_int_plus, :]

        u_res = scaled_u % 1
        v_res = scaled_v % 1
        return interpolate(
            interpolate(a, b, v_res),
            interpolate(c, d, v_res),
            u_res
        )

    def has_grid(self) -> bool:
        """
        Whether the points held really are a grid of the resolution recorded. An imported
        mesh is not, nor is a surface whose points have been resized by something which
        knows nothing of the grid.
        """
        nu, nv = self.get_resolution()
        return nu > 1 and nv > 1 and len(self.data) == nu * nv

    def resample(self, resolution: Tuple[int, int]) -> Self:
        """
        Samples the surface over a grid of a different shape, interpolating along each
        direction between the points it holds, so that its shape survives the change.
        """
        nu, nv = self.get_resolution()
        new_nu, new_nv = resolution
        # Every field of a record being a float32, the whole of it is resampled in one
        # pass rather than one per field, see StructuredArray.floats
        grid = self.data.floats.reshape((nu, nv, -1))
        grid = resize_with_interpolation(grid, new_nu)
        grid = resize_with_interpolation(grid.transpose(1, 0, 2), new_nv)
        data = np.zeros(new_nu * new_nv, dtype=self.data.dtype)
        data.view(np.float32).reshape((new_nu * new_nv, -1))[:] = \
            grid.transpose(1, 0, 2).reshape((new_nu * new_nv, -1))
        self.set_resolution(resolution)
        self.set_data(data)
        return self

    def align_points(self, mobject: Mobject) -> Self:
        """
        Two surfaces are brought to a common number of points by sampling each over the
        finer of their two grids. Padding out whichever holds fewer, as mobjects are
        aligned in general, would leave its grid stretched out of shape, with rows of
        points repeated and a mesh of slivers between them.
        """
        both = (self, mobject)
        if not all(isinstance(mob, Surface) and mob.has_grid() for mob in both):
            return super().align_points(mobject)
        if self.get_resolution() == mobject.get_resolution():
            return super().align_points(mobject)
        resolution = tuple(map(max, zip(*(mob.get_resolution() for mob in both))))
        for mob in both:
            mob.resample(resolution)
        return self

    def min_opacity(self) -> float:
        """The least opaque any point of the surface is"""
        return float(self.data["rgba"][:, 3].min()) if len(self.data) else 1.0

    def is_opaque(self) -> bool:
        """
        Whether nothing behind the surface shows through it, which decides whether its
        triangles have to be drawn in order, see SurfaceDrawing.

        Asked once a frame, so worked out only when the data has been written to since the last
        ask. It cannot be settled in set_opacity instead: a surface fading in or transforming
        has its alpha interpolated straight into the array, passing no setter.
        """
        version = self.data.version
        if version != self.opaque_version:
            self.opaque_version = version
            self.opaque = self.min_opacity() >= 1
        return self.opaque

    def get_triangles(self) -> Tuple[np.ndarray, Vect3Array]:
        """
        Which vertex each triangle of the mesh starts at, and where the middle of it sits, for
        whatever wants them in an order of its own, see SurfaceDrawing.

        A grid of points is expanded into two triangles per square, taking the corners the
        vertex shader gives them, see inserts/surface_mesh.wgsl. Points which are no grid, as
        an imported mesh's are, are already three to a triangle.

        The middle rather than a corner, cheap as a corner would be, since which corner comes
        first is whatever the parametrization wound first, and nothing which sorts by these
        must depend on that.
        """
        points = self.data["point"]
        if not self.has_grid():
            triangles = len(points) // 3
            corners = points[:3 * triangles].reshape((triangles, 3, 3))
            return 3 * np.arange(triangles), corners.mean(axis=1)

        nu, nv = self.get_resolution()
        grid = points.reshape((nu, nv, 3))
        middles = np.array([
            grid[:-1, :-1] + grid[1:, :-1] + grid[:-1, 1:],
            grid[:-1, 1:] + grid[1:, :-1] + grid[1:, 1:],
        ]).reshape((-1, 3)) / 3
        squares = np.arange(nu - 1)[:, np.newaxis] * nv + np.arange(nv - 1)
        firsts = 6 * squares + np.array([[[0]], [[3]]])
        return firsts.reshape(-1), middles

    def set_sort_to_camera(self, sort: bool = True) -> Self:
        """
        Asks for the surface's triangles to be drawn furthest from the camera first, whether or
        not it can be seen through. One which can be is drawn that way regardless, so this is
        really for turning it off, and for scenes written when it had to be asked for.
        """
        for mob in self.get_family():
            if isinstance(mob, Surface):
                mob.sort_to_camera = sort
        return self

    def always_sort_to_camera(self, camera=None) -> Self:
        # Kept for the scenes which call it. Nothing needs the camera any more, nor an
        # updater to do the sorting, see set_sort_to_camera
        return self.set_sort_to_camera()

    def get_unit_normals(self) -> Vect3Array:
        """
        Which way the surface faces at each of its points, from the directions it runs
        in either way from there. The same thing the vertex shader works out, see
        inserts/surface_mesh.wgsl, for the sake of anything in python which wants it.
        """
        nu, nv = self.get_resolution()
        grid = self.get_points().reshape((nu, nv, 3))
        du = np.gradient(grid, axis=0)
        dv = np.gradient(grid, axis=1)
        # A row or column of the grid may be a single point, as at the pole of a sphere,
        # where stepping along it gets nowhere. Stepping one row or column over does,
        # either side serving for whichever end of the grid it happens to be.
        for shift in (-1, 1):
            du = np.where(norms_along_axis(du) < 1e-8, np.roll(du, shift, axis=1), du)
            dv = np.where(norms_along_axis(dv) < 1e-8, np.roll(dv, shift, axis=0), dv)
        return normalize_along_axis(np.cross(du, dv).reshape((nu * nv, 3)), 1)

    def pointwise_become_partial(
        self,
        smobject: "Surface",
        a: float,
        b: float,
        axis: int | None = None
    ) -> Self:
        assert isinstance(smobject, Surface)
        if axis is None:
            axis = self.preferred_creation_axis
        if a <= 0 and b >= 1:
            self.match_points(smobject)
            return self

        nu, nv = smobject.get_resolution()
        self.data['point'] = self.get_partial_points_array(
            smobject.data['point'], a, b,
            (nu, nv, 3),
            axis=axis
        )
        return self

    def get_partial_points_array(
        self,
        points: Vect3Array,
        a: float,
        b: float,
        resolution: Sequence[int],
        axis: int
    ) -> Vect3Array:
        if len(points) == 0:
            return points
        nu, nv = resolution[:2]
        points = points.reshape(resolution).copy()
        max_index = resolution[axis] - 1
        lower_index, lower_residue = integer_interpolate(0, max_index, a)
        upper_index, upper_residue = integer_interpolate(0, max_index, b)
        if axis == 0:
            points[:lower_index] = interpolate(
                points[lower_index],
                points[lower_index + 1],
                lower_residue
            )
            points[upper_index + 1:] = interpolate(
                points[upper_index],
                points[upper_index + 1],
                upper_residue
            )
        else:
            shape = (nu, 1, resolution[2])
            points[:, :lower_index] = interpolate(
                points[:, lower_index],
                points[:, lower_index + 1],
                lower_residue
            ).reshape(shape)
            points[:, upper_index + 1:] = interpolate(
                points[:, upper_index],
                points[:, upper_index + 1],
                upper_residue
            ).reshape(shape)
        return points.reshape((nu * nv, *resolution[2:]))

    def color_by_uv_function(self, uv_to_color: Callable[[Vect2], Color]):
        uv_grid = self.get_uv_grid()
        self.set_rgba_array_by_color([
            uv_to_color(u, v)
            for u, v in uv_grid.reshape(-1, 2)
        ])
        return self


class ParametricSurface(Surface):
    def __init__(
        self,
        uv_func: Callable[[float, float], Iterable[float]],
        u_range: tuple[float, float] = (0, 1),
        v_range: tuple[float, float] = (0, 1),
        **kwargs
    ):
        self.passed_uv_func = uv_func
        super().__init__(u_range=u_range, v_range=v_range, **kwargs)

    def uv_func(self, u, v):
        return self.passed_uv_func(u, v)


class TexturedSurface(Surface):
    shader_file: str = "textured_surface.wgsl"
    data_dtype: np.dtype = np.dtype([
        ('point', np.float32, (3,)),
        ('im_coords', np.float32, (2,)),
        ('opacity', np.float32, (1,)),
    ])
    uniform_dtype: np.dtype = uniform_block_dtype(
        *COMMON_UNIFORMS,
        ("resolution", 2),
        ("num_textures", 1),
    )

    def __init__(
        self,
        uv_surface: Surface,
        image_file: str,
        dark_image_file: str | None = None,
        **kwargs
    ):
        if not isinstance(uv_surface, Surface):
            raise Exception("uv_surface must be of type Surface")
        # Set texture information
        if dark_image_file is None:
            dark_image_file = image_file
            self.num_textures = 1
        else:
            self.num_textures = 2

        texture_paths = {
            "LightTexture": get_full_raster_image_path(image_file),
            "DarkTexture": get_full_raster_image_path(dark_image_file),
        }

        self.uv_surface = uv_surface
        self.uv_func = uv_surface.uv_func
        self.u_range: Tuple[float, float] = uv_surface.u_range
        self.v_range: Tuple[float, float] = uv_surface.v_range
        self.initial_resolution: Tuple[int, int] = uv_surface.get_resolution()
        super().__init__(
            texture_paths=texture_paths,
            shading=tuple(uv_surface.shading),
            **kwargs
        )

    def init_points(self):
        surf = self.uv_surface
        nu, nv = surf.get_resolution()
        self.resize_points(surf.get_num_points())
        self.set_resolution(surf.get_resolution())
        self.data['point'] = surf.data['point']
        self.data['opacity'][:, 0] = surf.data["rgba"][:, 3]
        self.data["im_coords"] = np.array([
            [u, v]
            for u in np.linspace(0, 1, nu)
            for v in np.linspace(1, 0, nv)  # Reverse y-direction
        ])

    def set_image_coords_by_uv_func(self, uv_func) -> Self:
        """
        uv_func takes in a pair (u, v), and returns a new pair (u', v') used
        for coordinates when reading from the texture
        """
        nu, nv = self.uv_surface.get_resolution()
        self.data["im_coords"] = np.array([
            uv_func(u, v)
            for u in np.linspace(0, 1, nu)
            for v in np.linspace(1, 0, nv)  # Reverse y-direction
        ])
        return self

    def init_uniforms(self):
        super().init_uniforms()
        self.uniforms["num_textures"] = self.num_textures

    def min_opacity(self) -> float:
        # Where a Surface keeps a color per point, this keeps an opacity and takes the color
        # from its image. An image with transparency of its own is not accounted for.
        return float(self.data["opacity"].min()) if len(self.data) else 1.0

    def set_opacity(self, opacity: float | Iterable[float], recurse=True) -> Self:
        op_arr = np.array(listify(opacity))
        with self.data.being_written() as data:
            data["opacity"][:, 0] = resize_with_interpolation(op_arr, len(self.data))
        return self

    def set_color(
        self,
        color: ManimColor | Iterable[ManimColor] | None,
        opacity: float | Iterable[float] | None = None,
        recurse: bool = True
    ) -> Self:
        if opacity is not None:
            self.set_opacity(opacity)
        return self

    def pointwise_become_partial(
        self,
        tsmobject: "TexturedSurface",
        a: float,
        b: float,
        axis: int | None = None
    ) -> Self:
        if axis is None:
            axis = self.preferred_creation_axis
        super().pointwise_become_partial(tsmobject, a, b, axis)
        with self.data.being_written() as data:
            data["im_coords"][:] = tsmobject.data["im_coords"]
        if a <= 0 and b >= 1:
            return self
        nu, nv = tsmobject.get_resolution()
        im_coords[:] = self.get_partial_points_array(
            im_coords, a, b, (nu, nv, 2), axis
        )
        return self


class TexturedGeometry(TexturedSurface):
    """
    An imported mesh, which is a list of triangles rather than a grid of points, so
    each of its faces is written out as three points of its own. A resolution of zero
    is what tells the vertex shader to read them that way, see surface_mesh.wgsl.
    """
    # One vertex per record, the records being the corners of each triangle in turn
    verts_per_record: int = 1

    def __init__(self, geometry: trimesh.base.Trimesh, texture_file: str, **kwargs):
        self.num_textures = 1
        self.geometry = geometry
        self.texture_file = texture_file
        # Not a grid, which is what the vertex shader goes by, see surface_mesh.wgsl
        self.initial_resolution = (0, 0)
        Mobject.__init__(
            self,
            texture_paths={"LightTexture": get_full_raster_image_path(texture_file)}
        )

    def init_points(self):
        # Which point of the mesh each corner of each face is, kept for anything wanting
        # to pick faces out again, e.g. to trim the mesh down
        self.vertex_indices = self.geometry.faces.flatten()
        uv = np.array(self.geometry.visual.uv)
        uv[:, 1] = 1.0 - uv[:, 1]

        self.set_points(np.array(self.geometry.vertices)[self.vertex_indices])
        self.data["im_coords"] = uv[self.vertex_indices]
        self.data["opacity"] = self.opacity


class ThreeDModel(Group):
    def __init__(self, obj_file: str, height=3):
        super().__init__()
        obj_file = get_full_three_d_model_path(obj_file)

        default_texture = Path(Path(obj_file).parent, "texture.png")
        if not default_texture.exists():
            default_texture = get_full_raster_image_path("White.png")

        texture_files = self.get_textures_from_mtl(obj_file)
        mesh = trimesh.load(obj_file)

        if isinstance(mesh, trimesh.Scene):
            self.add(*(
                TexturedGeometry(geom, texture or default_texture)
                for geom, texture in zip(mesh.geometry.values(), texture_files.values())
            ))
        elif isinstance(mesh, trimesh.Geometry):
            # TODO
            self.add(TexturedGeometry(mesh, default_texture))

        self.apply_depth_test()
        self.set_height(height)
        self.center()

    def get_textures_from_mtl(self, obj_filepath, suppress_warnings=True):
        """
        Load an OBJ file and extract all texture filenames from its MTL file.

        Returns:
            dict: {material_name: texture_filepath}
        """

        # Suppress pywavefront warnings if desired
        if suppress_warnings:
            logging.getLogger('pywavefront').setLevel(logging.ERROR)

        # Load the OBJ file (automatically loads MTL)
        obj_scene = pywavefront.Wavefront(obj_filepath, collect_faces=True)

        textures = {}

        # Iterate through materials
        for material_name, material in obj_scene.materials.items():
            if material.texture:
                textures[material_name] = material.texture.path
            else:
                textures[material_name] = None

        return textures
