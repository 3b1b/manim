from __future__ import annotations

import numpy as np
import trimesh
import pywavefront
import logging
from pathlib import Path

from manimlib.constants import GREY
from manimlib.constants import OUT
from manimlib.mobject.mobject import Mobject
from manimlib.renderer.texture import ImageFile
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
    """
    A parametrically defined surface represented by a two-dimensional grid
    of three-dimensional points.

    `Surface` inherits from :class:`Mobject` and represents a surface using
    a regular grid sampled over two parameter ranges, ``u_range`` and
    ``v_range``. Each grid point is mapped to a three-dimensional position
    by ``uv_func(u, v)``. The GPU vertex shader uses these sampled points to
    construct the surface mesh, expanding each grid cell into two triangles.

    The class also supports grid resampling, interpolation between surfaces,
    opacity detection, triangle sorting, normal calculation, partial surface
    creation, and coloring based on parameter coordinates.

    Parameters
    ----------
    color : ManimColor, optional
        Base color used to initialize the surface. Defaults to GREY.
    shading : Tuple[float, float, float], optional
        Shading parameters forwarded to Mobject. Defaults to (0.3, 0.2, 0.4).
    depth_test : bool, optional
        Whether depth testing is enabled. Defaults to True.
    u_range : Tuple[float, float], optional
        Inclusive start and end values of the first surface parameter.
        Defaults to (0.0, 1.0).
    v_range : Tuple[float, float], optional
        Inclusive start and end values of the second surface parameter.
        Defaults to (0.0, 1.0).
    resolution : Tuple[int, int], optional
        Number of sampled points along the u and v directions, respectively.
        Each dimension includes both endpoints. Defaults to (101, 101).
    preferred_creation_axis : int, optional
        Default parameter-grid axis used when creating a partial surface.
        Defaults to 1.
    sort_to_camera : bool, optional
        Whether surface triangles should be sorted from farthest to nearest
        relative to the camera when the drawing system supports this option.
        Defaults to False.
    **kwargs
        Additional keyword arguments forwarded to Mobject.

    Attributes
    ----------
    u_range : Tuple[float, float]
        Parameter interval along the u direction.
    v_range : Tuple[float, float]
        Parameter interval along the v direction.
    initial_resolution : Tuple[int, int]
        Resolution supplied during initialization. It is used to initialize
        the resolution uniform.
    preferred_creation_axis : int
        Default axis used by ``pointwise_become_partial``.
    sort_to_camera : bool
        Whether triangles should be sorted relative to the camera.
    opaque : bool
        Cached result of the most recent opacity check.
    opaque_version : int
        Data version associated with the cached opacity result.
    drawing_class : type
        Drawing implementation used for rendering: SurfaceDrawing.
    shader_file : str
        Shader filename used for rendering: ``surface.wgsl``.
    verts_per_record : int
        Number of vertices generated for each grid-point record: 6.
    data_dtype : np.dtype
        Structured point data containing three-dimensional positions and
        RGBA colors.
    uniform_dtype : np.dtype
        Shader uniform layout containing common uniforms and the two-component
        surface resolution.

    Examples
    --------
    Define a simple surface using a custom parameterization:

        class PlaneSurface(Surface):
            def uv_func(self, u, v):
                return (u, v, 0.0)

        surface = PlaneSurface(
            u_range=(-2, 2),
            v_range=(-1, 1),
            resolution=(20, 10),
        )

    Create a spherical surface by mapping parameters to 3D coordinates:

        class SphereSurface(Surface):
            def uv_func(self, u, v):
                return (
                    np.cos(u) * np.sin(v),
                    np.sin(u) * np.sin(v),
                    np.cos(v),
                )

        sphere = SphereSurface(
            u_range=(0, TAU),
            v_range=(0, PI),
            resolution=(50, 30),
        )

    Change the sampling resolution:

        surface.set_resolution((40, 40))

    Resample an existing grid while interpolating its stored data:

        surface.resample((60, 60))

    Convert a parameter pair to a point on the sampled surface:

        point = surface.uv_to_point(0.5, 0.5)

    Retrieve the sampled parameter grid:

        uv_grid = surface.get_uv_grid()

    Check whether the stored points still form a regular grid:

        if surface.has_grid():
            print(surface.get_resolution())

    Check surface opacity:

        opaque = surface.is_opaque()
        minimum_opacity = surface.min_opacity()

    Calculate unit normals at sampled points:

        normals = surface.get_unit_normals()

    Color the surface according to its parameter coordinates:

        surface.color_by_uv_function(
            lambda u, v: interpolate_color(BLUE, RED, u)
        )

    Sort surface triangles relative to the camera:

        surface.set_sort_to_camera(True)

    Create a partial surface from another surface:

        partial = Surface()
        partial.pointwise_become_partial(
            surface,
            0.2,
            0.8,
            axis=1,
        )

    Methods
    -------
    init_uniforms()
        Initialize shader uniforms, including the configured grid resolution.

    get_resolution()
        Return the current resolution as a pair of integers obtained from
        the resolution uniform.

    set_resolution(resolution)
        Update the resolution uniform. The new resolution must remain
        consistent with the number and arrangement of stored point records.

    interpolate(mobject1, mobject2, alpha, path_func=straight_path)
        Interpolate the object's data between two mobjects while preserving
        this surface's current resolution.

    uv_func(u, v)
        Map a parameter pair to a three-dimensional point. Subclasses should
        override this method to define their geometry.

    init_points()
        Generate the initial grid of points by evaluating ``uv_func`` over
        the sampled parameter grid.

    get_uv_grid()
        Return an array with shape ``(nu, nv, 2)`` containing all sampled
        parameter pairs.

    uv_to_point(u, v)
        Approximate a surface point by interpolating between nearby sampled
        grid points corresponding to the supplied parameters.

    has_grid()
        Return whether the stored data contains exactly the expected number
        of records for a valid grid with both resolution dimensions greater
        than one.

    resample(resolution)
        Resample all stored floating-point fields over a grid of a different
        resolution, then update the data and resolution uniform.

    align_points(mobject)
        Align two compatible surfaces by resampling both to the maximum
        resolution along each axis. Otherwise, use the parent alignment
        implementation.

    min_opacity()
        Return the minimum alpha value among all stored RGBA records, or
        1.0 if the surface has no records.

    is_opaque()
        Return whether the surface is fully opaque, recalculating the answer
        when the underlying point data version changes.

    get_triangles()
        Return triangle starting indices and triangle centers for sorting.
        Handles both regular grid data and non-grid mesh data.

    set_sort_to_camera(sort=True)
        Set the camera-sorting flag on every Surface in the object's family.

    always_sort_to_camera(camera=None)
        Compatibility method that enables camera sorting. The camera argument
        is not used.

    get_unit_normals()
        Calculate approximate unit normals at the sampled grid points using
        finite differences along the two parameter directions.

    pointwise_become_partial(smobject, a, b, axis=None)
        Make this surface represent a partial interval of another Surface
        along the selected grid axis.

    get_partial_points_array(points, a, b, resolution, axis)
        Produce a point array representing a partial parameter interval,
        interpolating boundary rows or columns at the interval endpoints.

    color_by_uv_function(uv_to_color)
        Assign colors by evaluating a color function at every sampled
        parameter pair.

    Notes
    -----
    - The resolution is stored in shader uniforms. ``get_resolution`` reads
      from those uniforms rather than treating ``initial_resolution`` as
      the current resolution.
    - For a grid with resolution ``(nu, nv)``, the surface stores ``nu * nv``
      point records. The grid has ``(nu - 1) * (nv - 1)`` rectangular cells,
      each expanded into two triangles by the shader.
    - Both resolution dimensions must exceed one for ``has_grid`` to return
      True. The stored record count must also equal ``nu * nv``.
    - ``uv_to_point`` clamps normalized parameter coordinates to the [0, 1]
      interval before selecting nearby grid points. It performs interpolation
      across the sampled grid, rather than evaluating ``uv_func`` directly.
    - ``resample`` interpolates the complete floating-point record data,
      not only point coordinates, so associated color fields are resampled too.
    - ``align_points`` uses the finer resolution along each axis when both
      objects are valid grids. This avoids padding a coarser grid with
      repeated points, which could distort the resulting mesh.
    - ``is_opaque`` checks the minimum alpha value. A surface is considered
      opaque only when every stored alpha value is at least 1.0. The result
      is cached against the point-data version.
    - ``get_triangles`` uses triangle centers rather than a fixed corner
      for sorting, avoiding dependence on the orientation of the parameterization.
    - For grid data, ``get_triangles`` returns two triangle centers per grid
      cell. For non-grid data, it treats consecutive groups of three points
      as triangles and ignores any incomplete trailing group.
    - ``get_unit_normals`` estimates tangent directions with NumPy's gradient
      function, takes their cross product, and normalizes the results.
      Degenerate directions are replaced using neighboring grid directions
      where possible.
    - ``pointwise_become_partial`` copies the full source points when the
      requested interval covers the entire [0, 1] range. Otherwise, it
      updates the point field using ``get_partial_points_array``.
    - ``get_partial_points_array`` expects an axis of 0 or 1. It interpolates
      at the lower and upper interval boundaries while collapsing points
      outside the selected interval toward those boundaries.
    - ``color_by_uv_function`` evaluates its callable with two positional
      arguments, ``u`` and ``v``, for each sampled parameter pair, despite
      the callable annotation being written as ``Callable[[Vect2], Color]``.
    - The default ``uv_func`` produces the flat mapping ``(u, v, 0.0)``.
      Subclasses normally override it to define a meaningful surface.
    """

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
    """
    A surface defined by a user-provided parametric function of two variables.

    `ParametricSurface` inherits from :class:`Surface` and allows the surface
    geometry to be specified by passing a callable that maps a pair of
    parameters ``(u, v)`` to a point in three-dimensional space.

    The supplied function is stored as ``passed_uv_func``. Whenever the
    parent class samples the surface, the overridden ``uv_func`` delegates
    the calculation to this callable.

    Parameters
    ----------
    uv_func : Callable[[float, float], Iterable[float]]
        Function that accepts two parameters, ``u`` and ``v``, and returns
        an iterable of coordinates representing a point on the surface.
        Typically, the returned coordinates are ``(x, y, z)``.
    u_range : tuple[float, float], optional
        Start and end values of the first parameter. Defaults to (0, 1).
    v_range : tuple[float, float], optional
        Start and end values of the second parameter. Defaults to (0, 1).
    **kwargs
        Additional keyword arguments forwarded to :class:`Surface`, such as
        ``resolution``, ``color``, ``shading``, ``depth_test``, and
        ``sort_to_camera``.

    Attributes
    ----------
    passed_uv_func : Callable[[float, float], Iterable[float]]
        The original parametric function supplied to the constructor.

    Examples
    --------
    Create a flat rectangular surface:

        surface = ParametricSurface(
            lambda u, v: (u, v, 0),
            u_range=(-2, 2),
            v_range=(-1, 1),
        )

    Create a curved surface:

        surface = ParametricSurface(
            lambda u, v: (
                u,
                v,
                np.sin(u) * np.cos(v),
            ),
            u_range=(-PI, PI),
            v_range=(-PI, PI),
            resolution=(50, 50),
        )

    Create a spherical surface using angular parameters:

        sphere = ParametricSurface(
            lambda u, v: (
                np.cos(u) * np.sin(v),
                np.sin(u) * np.sin(v),
                np.cos(v),
            ),
            u_range=(0, TAU),
            v_range=(0, PI),
            resolution=(60, 30),
        )

    Create a helicoidal surface:

        surface = ParametricSurface(
            lambda u, v: (
                v * np.cos(u),
                v * np.sin(u),
                u,
            ),
            u_range=(0, TAU),
            v_range=(0, 2),
            resolution=(60, 30),
        )

    Notes
    -----
    - The callable is stored in ``passed_uv_func`` before the parent
      constructor runs, allowing the inherited surface initialization to
      call the overridden ``uv_func``.
    - The overridden ``uv_func`` simply returns the result of
      ``passed_uv_func(u, v)``. It does not perform additional coordinate
      transformations or validate the returned coordinates.
    - The function should return coordinates compatible with the surface's
      three-dimensional point representation.
    - The parameter ranges determine the interval sampled by the parent
      class, while the ``resolution`` keyword controls how many samples
      are taken along each parameter direction.
    - The resulting geometry is sampled and stored as a grid. Changing the
      callable later does not automatically regenerate the existing points;
      the surface must be reinitialized or its points regenerated for the
      new function to affect the geometry.
    """

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
    """
    A surface that maps one or more image textures onto the geometry of an
    existing Surface.

    `TexturedSurface` inherits from :class:`Surface` and uses another surface
    to define its geometry, parameter ranges, and sampling resolution. Instead
    of storing an RGBA color for every point, it stores texture coordinates
    and opacity values. The GPU shader samples the supplied image textures
    to determine the visible colors across the surface.

    The class supports a light texture and an optional dark texture, allowing
    different images to be used for light and dark rendering modes.

    Parameters
    ----------
    uv_surface : Surface
        Surface providing the geometry, parameterization, ranges, shading,
        and initial resolution. Must be an instance of Surface.
    image_file : str
        Path or filename of the primary image texture. Its resolved path is
        loaded as the ``LightTexture``.
    dark_image_file : str or None, optional
        Optional image texture used as the ``DarkTexture``. If omitted,
        the primary image is used for both texture slots and ``num_textures``
        is set to 1. If supplied, ``num_textures`` is set to 2.
    **kwargs
        Additional keyword arguments forwarded to :class:`Surface`.

    Attributes
    ----------
    uv_surface : Surface
        Source surface whose sampled geometry is used by this object.
    uv_func : Callable
        Reference to the source surface's ``uv_func``.
    u_range : Tuple[float, float]
        Parameter range copied from the source surface.
    v_range : Tuple[float, float]
        Parameter range copied from the source surface.
    initial_resolution : Tuple[int, int]
        Initial sampling resolution copied from the source surface.
    num_textures : int
        Number of active textures indicated to the shader: 1 when no separate
        dark image is supplied, otherwise 2.
    data_dtype : np.dtype
        Structured data layout containing point coordinates, two-dimensional
        image coordinates, and per-point opacity.
    uniform_dtype : np.dtype
        Shader uniform layout containing common uniforms, surface resolution,
        and the number of active textures.
    shader_file : str
        Shader filename used for rendering: ``textured_surface.wgsl``.

    Examples
    --------
    Apply an image texture to a parametric surface:

        surface = ParametricSurface(
            lambda u, v: (u, v, 0),
            u_range=(-2, 2),
            v_range=(-1, 1),
            resolution=(100, 100),
        )

        textured = TexturedSurface(
            surface,
            "texture.png",
        )

    Provide a separate dark-mode texture:

        textured = TexturedSurface(
            surface,
            image_file="light_texture.png",
            dark_image_file="dark_texture.png",
        )

    Change how surface parameters map to texture coordinates:

        textured.set_image_coords_by_uv_func(
            lambda u, v: (u, 1 - v)
        )

    Set the surface opacity:

        textured.set_opacity(0.5)

    Supply different opacity values for the sampled points:

        textured.set_opacity(np.linspace(0.2, 1.0, 100))

    Change opacity through the color interface:

        textured.set_color(None, opacity=0.7)

    Methods
    -------
    init_points()
        Copy the source surface's point positions and resolution, transfer
        its alpha values into the opacity field, and generate image
        coordinates over the normalized texture domain. The v-coordinate
        sampling order is reversed to account for image-coordinate orientation.

    set_image_coords_by_uv_func(uv_func)
        Remap each normalized texture coordinate pair through a callable
        that accepts ``(u, v)`` and returns a new pair ``(u_prime, v_prime)``.

    init_uniforms()
        Initialize the inherited uniforms and set ``num_textures`` for the
        shader.

    min_opacity()
        Return the minimum stored opacity, or 1.0 if there are no records.

    set_opacity(opacity, recurse=True)
        Set per-point opacity values, resizing the supplied values through
        interpolation to match the number of records.

    set_color(color, opacity=None, recurse=True)
        Preserve the texture's colors. If opacity is supplied, update the
        opacity values; the color argument itself does not recolor the texture.

    pointwise_become_partial(tsmobject, a, b, axis=None)
        Apply the inherited partial-surface operation and copy the source
        object's texture coordinates, with additional handling intended to
        keep texture mapping aligned with the partial geometry.

    Notes
    -----
    - The constructor checks ``uv_surface`` with ``isinstance`` and raises
      an Exception if the supplied object is not a Surface.
    - Both texture slots are created even when only one image is supplied.
      In that case, the same image file is used for LightTexture and
      DarkTexture, while ``num_textures`` remains 1.
    - The source surface provides the geometry. ``init_points`` copies its
      point coordinates instead of evaluating ``uv_func`` independently.
    - The source surface's RGBA alpha channel is copied into the new
      object's opacity field during point initialization.
    - Texture coordinates are generated from normalized values between
      0 and 1. The v-coordinate values are enumerated from 1 down to 0
      to reverse the vertical image-coordinate direction.
    - ``set_image_coords_by_uv_func`` changes the texture-coordinate mapping,
      not the geometric point positions. The callable is evaluated for
      every normalized coordinate pair.
    - ``min_opacity`` considers only the stored opacity field. It does not
      account for transparency that may already exist in the source image.
    - ``set_opacity`` interpolates the provided values to the number of
      point records. Its ``recurse`` parameter is accepted but not used.
    - ``set_color`` does not apply the supplied color because visible colors
      are sampled from the texture. Only its optional opacity argument has
      an effect.
    - ``pointwise_become_partial`` defaults to the inherited preferred
      creation axis when ``axis`` is None.
    - In the supplied implementation, the partial-texture-coordinate section
      references ``im_coords`` without defining it locally or qualifying it
      as ``self.data["im_coords"]``. Unless ``im_coords`` exists in the
      surrounding scope, a partial interval may raise a NameError. This
      section should be checked before relying on partial textured surfaces.
    """

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

        textures = {
            "LightTexture": ImageFile(get_full_raster_image_path(image_file)),
            "DarkTexture": ImageFile(get_full_raster_image_path(dark_image_file)),
        }

        self.uv_surface = uv_surface
        self.uv_func = uv_surface.uv_func
        self.u_range: Tuple[float, float] = uv_surface.u_range
        self.v_range: Tuple[float, float] = uv_surface.v_range
        self.initial_resolution: Tuple[int, int] = uv_surface.get_resolution()
        super().__init__(
            textures=textures,
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
    TexturedGeometry
    ================

    A textured 3D mesh represented as a collection of independent triangles.

    TexturedGeometry extends TexturedSurface but is designed for imported mesh
    geometry, where each face is represented by three vertices rather than by
    a regular grid of points. It stores the mesh's vertex positions, texture
    coordinates, and opacity in the data structures expected by the rendering
    pipeline.

    The vertex shader determines that the geometry is a triangle mesh from
    the zero-valued initial resolution. See ``surface_mesh.wgsl`` for the
    corresponding shader behavior.

    Parameters
    ----------
    geometry : trimesh.base.Trimesh
        The input Trimesh object containing the mesh's vertices, triangular
        faces, and visual information such as UV texture coordinates.
    texture_file : str
        Path or identifier for the image file used to texture the mesh.
    **kwargs
        Additional keyword arguments accepted by the surrounding API. This
        implementation does not explicitly forward them to the parent class.

    Attributes
    ----------
    num_textures : int
        Set to ``1``, indicating that the object uses one texture.
    geometry : trimesh.base.Trimesh
        The original input mesh.
    texture_file : str
        The texture image path or identifier supplied during initialization.
    initial_resolution : tuple[int, int]
        Set to ``(0, 0)`` to indicate that the geometry is not a regular
        surface grid.
    verts_per_record : int
        Class attribute set to ``1``. Each stored vertex record represents
        one vertex, so triangle faces are represented by three records.
    vertex_indices : numpy.ndarray
        Flattened face-index array. Each entry identifies a vertex in the
        original mesh, and the order preserves the mesh's face connectivity.
    data["im_coords"] : numpy.ndarray
        UV texture coordinates corresponding to the expanded vertex records.
        The vertical UV coordinate is flipped during initialization.
    data["opacity"]
        The object's opacity values, assigned after the points and texture
        coordinates are initialized.

    Initialization
    --------------
    The constructor performs the following operations:

    1. Sets ``num_textures`` to ``1``.
    2. Stores the input mesh and texture filename.
    3. Sets ``initial_resolution`` to ``(0, 0)`` to distinguish this mesh
       from a regularly sampled surface.
    4. Calls ``Mobject.__init__`` directly, supplying a texture dictionary
       whose ``"LightTexture"`` entry is an ``ImageFile`` created from the
       resolved raster-image path.

    Calling ``Mobject.__init__`` directly means this constructor does not
    invoke ``TexturedSurface.__init__``. It relies on the explicit setup
    performed here and on the relevant inherited behavior.

    Point Initialization
    --------------------
    ``init_points`` prepares the mesh data for rendering:

    1. Flattens ``geometry.faces`` into ``vertex_indices``. For triangular
       faces, every three consecutive indices describe one face.
    2. Converts ``geometry.visual.uv`` into a NumPy array.
    3. Flips the vertical texture coordinate using ``1.0 - uv[:, 1]``.
       This adjusts the UV convention to match the texture-coordinate
       orientation expected by the renderer.
    4. Uses the flattened indices to select vertices from
       ``geometry.vertices`` and passes the resulting array to ``set_points``.
       Shared vertices are consequently repeated when they occur in multiple
       faces.
    5. Selects the corresponding UV coordinates using the same flattened
       indices and stores them in ``data["im_coords"]``.
    6. Copies the current opacity attribute into ``data["opacity"]``.

    The method assumes the mesh provides compatible triangular face indices
    and UV coordinates. In particular, the UV array must have entries
    corresponding to the mesh vertices.

    Notes
    -----
    - This class represents imported triangle meshes, not a parametrically
      sampled surface grid.
    - The zero-valued initial resolution is meaningful to the rendering
      shader; it should not be interpreted as an instruction to create a
      mesh with no vertices.
    - The flattened index array establishes the correspondence between
      original mesh vertices, expanded triangle vertices, and UV coordinates.
    - Flipping the vertical UV component changes the texture mapping
      orientation without changing the mesh's 3D vertex positions.
    - The constructor accepts ``**kwargs`` but does not use or forward them
      in the shown implementation.
    - The implementation expects ``geometry.visual.uv`` to be available.
      Meshes without UV coordinates may require preprocessing before they
      can be textured correctly.

    Examples
    --------
    Given a Trimesh object with triangular faces and UV coordinates:

        mesh = trimesh.load("model.obj")
        textured_mesh = TexturedGeometry(
            geometry=mesh,
            texture_file="texture.png",
        )

    The object initializes its rendering data from the mesh and associates
    the supplied texture image with the ``"LightTexture"`` texture slot.

    Actual rendering depends on the surrounding ManimGL scene, renderer,
    shader implementation, and the validity of the mesh's texture data.
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
            textures={"LightTexture": ImageFile(get_full_raster_image_path(texture_file))}
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
    """
    ThreeDModel
    ===========

    A 3D model loader that imports an OBJ file, assigns textures to its
    geometry, and arranges the resulting objects into a Group.

    ThreeDModel uses Trimesh to load the model geometry and PyWavefront to
    inspect its material definitions and extract texture filenames from the
    associated MTL file. Each imported mesh is wrapped in a TexturedGeometry
    object, which is then added to the group.

    After loading, the model has depth testing enabled, is scaled to the
    requested height, and is centered.

    Parameters
    ----------
    obj_file : str
        Filename or path identifying the OBJ model to load. The path is
        resolved using ``get_full_three_d_model_path`` before loading.
    height : float, default=3
        Target height assigned to the resulting group through ``set_height``.
        The actual scaling behavior depends on the inherited implementation.

    Attributes
    ----------
    No additional public instance attributes are explicitly defined in this
    constructor beyond those inherited from Group and populated through its
    methods. The group contains the TexturedGeometry objects created from
    the imported mesh.

    Model Loading Process
    ---------------------
    The constructor performs the following operations:

    1. Initializes the parent ``Group``.
    2. Resolves the OBJ file path using ``get_full_three_d_model_path``.
    3. Looks for a file named ``texture.png`` in the resolved OBJ file's
       parent directory.
    4. If that file does not exist, resolves ``White.png`` through
       ``get_full_raster_image_path`` as the default texture.
    5. Calls ``get_textures_from_mtl`` to obtain texture paths associated
       with the OBJ file's materials.
    6. Loads the OBJ file using ``trimesh.load``.
    7. Handles the loaded result according to its type:
       - If the result is a ``trimesh.Scene``, iterates over its geometry
         objects and creates a ``TexturedGeometry`` for each one, pairing
         each geometry with the corresponding texture path or the default
         texture when the material texture is missing.
       - If the result is a ``trimesh.Geometry``, adds one
         ``TexturedGeometry`` using the default texture. The implementation
         contains a TODO comment in this branch, indicating that this case
         may need further development.
    8. Enables depth testing through ``apply_depth_test``.
    9. Sets the group's height using ``set_height(height)``.
    10. Centers the group using ``center``.

    Texture Selection
    -----------------
    The default texture is initially assumed to be ``texture.png`` beside
    the OBJ file. If that file is absent, the code falls back to the
    application's resolved ``White.png`` image.

    For scene-based models, textures returned by ``get_textures_from_mtl``
    are matched to geometry using the iteration order of the values in
    ``mesh.geometry`` and ``texture_files``. If a geometry's associated
    texture value is ``None`` or otherwise falsy, the default texture is
    used.

    This matching relies on the geometry and material mappings having
    compatible iteration order and corresponding entries. The code uses
    ``zip``, so unmatched trailing entries are silently ignored if the
    collections differ in length.

    Method: get_textures_from_mtl
    -----------------------------
    get_textures_from_mtl(obj_filepath, suppress_warnings=True)

    Loads an OBJ file with PyWavefront and returns the texture path
    associated with each material.

    Parameters
    ----------
    obj_filepath : str
        Path to the OBJ file whose materials should be inspected.
    suppress_warnings : bool, default=True
        If true, sets the ``pywavefront`` logger's level to ``logging.ERROR``
        to suppress messages below the error level.

    Returns
    -------
    dict
        A dictionary mapping material names to texture paths. Materials
        without an associated texture are mapped to ``None``.

    Method Behavior
    ---------------
    1. Optionally sets the ``pywavefront`` logger to ``logging.ERROR``.
    2. Loads the OBJ file with ``pywavefront.Wavefront``, using
       ``collect_faces=True`` and allowing PyWavefront to load its
       associated material information.
    3. Iterates through ``obj_scene.materials``.
    4. For each material, stores ``material.texture.path`` if a texture
       exists; otherwise, stores ``None``.
    5. Returns the resulting material-to-texture dictionary.

    Notes
    -----
    - This method changes the global logging level for the ``pywavefront``
      logger when warning suppression is enabled. The original logger level
      is not restored by this implementation.
    - The constructor expects the required OBJ, MTL, and texture resources
      to be accessible through the relevant loaders and path-resolution
      helpers.
    - Although the texture extraction method returns paths keyed by
      material name, the constructor pairs texture values with geometry
      values by iteration order rather than explicitly matching each
      geometry to its material.
    - The single-geometry branch currently uses the default texture rather
      than selecting a texture from the extracted material mapping.
    - The ``trimesh.Geometry`` branch includes a TODO comment, so its
      behavior may not cover every kind of geometry returned by Trimesh.
    - This implementation does not explicitly handle loading errors,
      missing OBJ files, malformed MTL files, or unsupported geometry.
    - The final appearance depends on the imported geometry, available UV
      coordinates, texture files, TexturedGeometry, and the renderer's
      depth-testing behavior.

    Examples
    --------
    Load a model and add it to a scene:

        model = ThreeDModel("models/robot.obj")
        scene.add(model)

    Specify a target height:

        model = ThreeDModel("models/robot.obj", height=5)

    Inspect the material texture mapping separately:

        textures = model.get_textures_from_mtl("models/robot.obj")
        print(textures)

    The paths shown in these examples are illustrative. The actual model
    and texture files must be available through the configured path helpers.
    """

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
