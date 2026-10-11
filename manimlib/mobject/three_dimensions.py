from __future__ import annotations

import math

import numpy as np

from manimlib.constants import BLUE, BLUE_D, BLUE_E, GREY_A, BLACK
from manimlib.constants import IN, ORIGIN, OUT, RIGHT
from manimlib.constants import PI, TAU
from manimlib.mobject.mobject import Group
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.types.surface import Surface
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.geometry import Polygon
from manimlib.mobject.geometry import Square
from manimlib.utils.bezier import interpolate
from manimlib.utils.iterables import adjacent_pairs
from manimlib.utils.space_ops import compass_directions
from manimlib.utils.space_ops import get_norm
from manimlib.utils.space_ops import z_to_vector

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Tuple, TypeVar
    from manimlib.typing import ManimColor, Vect3, Sequence

    T = TypeVar("T", bound=Mobject)


class SurfaceMesh(VGroup):
    """
    A wireframe mesh that visualizes the parameter-space grid of a Surface.

    SurfaceMesh constructs a collection of smooth curves along the two
    parameter directions of an existing surface. The curves are generated
    from the surface's sampled points and unit normals, producing a mesh
    that follows the surface geometry.

    Parameters
    ----------
    uv_surface : Surface
        The surface whose sampled geometry is used to construct the mesh.
        Its resolution, points, and unit normals are queried during
        initialization of the mesh geometry.
    resolution : Tuple[int, int], optional
        Number of mesh curves to generate along the two parameter directions,
        respectively. Defaults to ``(21, 11)``. This is independent of the
        underlying surface's sampling resolution.
    stroke_width : float, optional
        Width of the mesh curves. Defaults to ``1``.
    stroke_color : ManimColor, optional
        Color of the mesh curves. Defaults to ``GREY_A``.
    normal_nudge : float, optional
        Distance by which sampled surface points are displaced along their
        unit normals before constructing the mesh. Defaults to ``1e-2``.
        This can help offset the mesh slightly from the surface.
    depth_test : bool, optional
        Whether depth testing is enabled for the mesh, as passed to the
        parent ``VGroup`` constructor. Defaults to ``True``.
    **kwargs
        Additional keyword arguments forwarded to ``VGroup``.

    Attributes
    ----------
    uv_surface : Surface
        The surface from which the mesh geometry is generated.
    resolution : Tuple[int, int]
        Requested number of curves in the two parameter directions.
    normal_nudge : float
        Normal displacement applied to sampled points.

    Methods
    -------
    init_points()
        Generates the mesh curves from the surface's sampled points and
        unit normals. Creates one family of curves for each parameter
        direction and adds them to the group.

    Notes
    -----
    - The underlying surface resolution is obtained through
      ``uv_surface.get_resolution()``, yielding ``(full_nu, full_nv)``.
    - The surface's sampled points and unit normals are retrieved using
      ``get_points()`` and ``get_unit_normals()``.
    - Each point is displaced by ``normal_nudge * normal`` before the
      curves are generated.
    - Mesh indices are sampled using ``np.linspace`` and treated as
      floating-point values. The implementation interpolates between
      the floor and ceiling index samples to approximate intermediate
      grid curves.
    - The first family of curves follows the first parameter direction;
      the second family follows the other direction through strided
      indexing of the sampled point array.
    - ``set_points_smoothly()`` is used to create smooth paths through
      the interpolated points.
    - The actual number of curves is ``resolution[0] + resolution[1]``,
      assuming both loops complete successfully.
    - This implementation assumes the surface's point and normal arrays
      follow the expected grid layout, with ``full_nv`` samples per row.
    - The mesh geometry is generated in ``init_points()``. Changing
      ``resolution`` or ``normal_nudge`` afterward does not automatically
      rebuild existing curves.
    - No validation is performed for zero or negative resolution values,
      or for compatibility between the surface's reported resolution and
      its point and normal arrays.

    Examples
    --------
    Create a mesh for an existing surface::

        surface = Surface(
            lambda u, v: np.array([
                u,
                v,
                np.sin(u) * np.cos(v),
            ]),
            u_range=(-2, 2),
            v_range=(-2, 2),
        )
        mesh = SurfaceMesh(surface)
        self.add(surface, mesh)

    Adjust the mesh density and appearance::

        mesh = SurfaceMesh(
            surface,
            resolution=(30, 16),
            stroke_width=0.5,
            stroke_color=BLUE,
            normal_nudge=0.02,
        )
        self.add(mesh)

    Disable depth testing::

        mesh = SurfaceMesh(
            surface,
            depth_test=False,
        )
        self.add(mesh)

    See Also
    --------
    Surface
    VGroup
    VMobject
    """

    def __init__(
        self,
        uv_surface: Surface,
        resolution: Tuple[int, int] = (21, 11),
        stroke_width: float = 1,
        stroke_color: ManimColor = GREY_A,
        normal_nudge: float = 1e-2,
        depth_test: bool = True,
        **kwargs
    ):
        self.uv_surface = uv_surface
        self.resolution = resolution
        self.normal_nudge = normal_nudge

        super().__init__(
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            depth_test=depth_test,
            **kwargs
        )

    def init_points(self) -> None:
        uv_surface = self.uv_surface

        full_nu, full_nv = uv_surface.get_resolution()
        part_nu, part_nv = self.resolution
        # 'indices' are treated as floats. Later, there will be
        # an interpolation between the floor and ceiling of these
        # indices
        u_indices = np.linspace(0, full_nu - 1, part_nu)
        v_indices = np.linspace(0, full_nv - 1, part_nv)

        points = uv_surface.get_points()
        normals = uv_surface.get_unit_normals()
        nudge = self.normal_nudge
        nudged_points = points + nudge * normals

        for ui in u_indices:
            path = VMobject()
            low_ui = full_nv * int(math.floor(ui))
            high_ui = full_nv * int(math.ceil(ui))
            path.set_points_smoothly(interpolate(
                nudged_points[low_ui:low_ui + full_nv],
                nudged_points[high_ui:high_ui + full_nv],
                ui % 1
            ))
            self.add(path)
        for vi in v_indices:
            path = VMobject()
            path.set_points_smoothly(interpolate(
                nudged_points[int(math.floor(vi))::full_nv],
                nudged_points[int(math.ceil(vi))::full_nv],
                vi % 1
            ))
            self.add(path)


# 3D shapes

class Sphere(Surface):
    """
    A three-dimensional spherical surface parameterized by azimuthal and
    polar angles.

    Sphere inherits from :class:`Surface` and defines its geometry through
    the ``uv_func()`` parameterization. The sphere is centered at the origin,
    with a configurable radius and orientation of angular traversal.

    Parameters
    ----------
    u_range : Tuple[float, float], optional
        Range of the azimuthal parameter ``u`` in radians. Defaults to
        ``(0, TAU)``, covering a complete revolution around the vertical axis.
    v_range : Tuple[float, float], optional
        Range of the polar parameter ``v`` in radians. Defaults to
        ``(0, PI)``, covering the sphere from its bottom pole to its top pole.
    resolution : Tuple[int, int], optional
        Number of samples used along the ``u`` and ``v`` parameter directions.
        Defaults to ``(101, 51)``.
    radius : float, optional
        Radius of the sphere. Defaults to ``1.0``.
    clockwise : bool, optional
        Determines the direction of angular traversal around the vertical
        axis. If ``True``, the sign of ``u`` is reversed; otherwise, it is
        positive. Defaults to ``False``.
    **kwargs
        Additional keyword arguments forwarded to :class:`Surface`.

    Attributes
    ----------
    radius : float
        Radius used to scale the sphere's parameterized coordinates.
    clockwise : bool
        Whether the azimuthal parameter uses a reversed sign.

    Methods
    -------
    uv_func(u, v)
        Maps the angular parameters ``u`` and ``v`` to a three-dimensional
        point on the sphere and returns it as a NumPy array.

    Notes
    -----
    - The sphere is centered at the origin.
    - The parameterization is

      ``x = radius * cos(sign * u) * sin(v)``

      ``y = radius * sin(sign * u) * sin(v)``

      ``z = -radius * cos(v)``

      where ``sign = -1`` when ``clockwise`` is true and ``+1`` otherwise.
    - With the default ranges, ``v = 0`` maps to the bottom pole
      ``(0, 0, -radius)``, while ``v = PI`` maps to the top pole
      ``(0, 0, radius)``.
    - The equator corresponds to ``v = PI / 2``.
    - Changing ``u_range`` or ``v_range`` can create a partial spherical
      surface rather than a complete sphere.
    - ``clockwise`` reverses the direction of angular traversal in the
      horizontal plane; it does not change the sphere's radius or center.
    - The class relies on ``Surface`` to sample the parameterization and
      construct the actual surface geometry.

    Examples
    --------
    Create a unit sphere::

        sphere = Sphere()
        self.add(sphere)

    Create a larger sphere::

        sphere = Sphere(radius=2)
        self.add(sphere)

    Create a sphere with reversed azimuthal traversal::

        sphere = Sphere(clockwise=True)
        self.add(sphere)

    Create a partial spherical surface::

        sphere = Sphere(
            u_range=(0, PI),
            v_range=(0, PI / 2),
            resolution=(51, 26),
        )
        self.add(sphere)

    See Also
    --------
    Surface
    ThreeDAxes
    SurfaceMesh
    """

    def __init__(
        self,
        u_range: Tuple[float, float] = (0, TAU),
        v_range: Tuple[float, float] = (0, PI),
        resolution: Tuple[int, int] = (101, 51),
        radius: float = 1.0,
        clockwise=False,
        **kwargs,
    ):
        self.radius = radius
        self.clockwise = clockwise
        super().__init__(
            u_range=u_range,
            v_range=v_range,
            resolution=resolution,
            **kwargs
        )

    def uv_func(self, u: float, v: float) -> np.ndarray:
        sign = -1 if self.clockwise else +1
        return self.radius * np.array([
            math.cos(sign * u) * math.sin(v),
            math.sin(sign * u) * math.sin(v),
            -math.cos(v)
        ])


class Torus(Surface):
    """
    A three-dimensional torus surface parameterized by two angular variables.

    Torus inherits from :class:`Surface` and constructs a ring-shaped surface
    by moving a circular cross-section around a central axis. The parameter
    ``u`` controls the position around the central ring, while ``v`` controls
    the position around the circular cross-section.

    Parameters
    ----------
    u_range : Tuple[float, float], optional
        Range of the angular parameter ``u`` in radians. Defaults to
        ``(0, TAU)``, covering a complete revolution around the central axis.
    v_range : Tuple[float, float], optional
        Range of the angular parameter ``v`` in radians. Defaults to
        ``(0, TAU)``, covering the complete circular cross-section.
    r1 : float, optional
        Major radius: the distance from the origin to the center of the
        circular tube's cross-section. Defaults to ``3.0``.
    r2 : float, optional
        Minor radius: the radius of the circular tube's cross-section.
        Defaults to ``1.0``.
    **kwargs
        Additional keyword arguments forwarded to :class:`Surface`.

    Attributes
    ----------
    r1 : float
        Major radius of the torus.
    r2 : float
        Minor radius of the torus.

    Methods
    -------
    uv_func(u, v)
        Maps the angular parameters ``u`` and ``v`` to a three-dimensional
        point on the torus and returns it as a NumPy array.

    Notes
    -----
    - The torus is centered around the origin and its central axis is the
      z-axis.
    - The parameterization implemented by ``uv_func()`` is

      ``P = (cos(u), sin(u), 0)``

      ``point = (r1 - r2 * cos(v)) * P - r2 * sin(v) * OUT``

    - Equivalently, its coordinates are

      ``x = (r1 - r2 * cos(v)) * cos(u)``

      ``y = (r1 - r2 * cos(v)) * sin(u)``

      ``z = -r2 * sin(v)``

    - ``u`` moves around the central ring, while ``v`` travels around the
      tube's circular cross-section.
    - With the default ranges, both parameters make a full revolution.
    - The minus signs in the parameterization determine the orientation of
      the cross-section; the resulting surface still forms a torus.
    - For a conventional ring torus, ``r1 > r2 > 0``. The implementation
      does not validate these values, so other choices can produce spindle,
      self-intersecting, or degenerate surfaces.
    - The class relies on ``Surface`` to sample the parameterization and
      construct the surface geometry.

    Examples
    --------
    Create a torus with the default radii::

        torus = Torus()
        self.add(torus)

    Create a torus with a larger tube::

        torus = Torus(r1=3, r2=1.5)
        self.add(torus)

    Create a partial torus::

        torus = Torus(
            u_range=(0, PI),
            v_range=(0, TAU),
        )
        self.add(torus)

    See Also
    --------
    Surface
    Sphere
    SurfaceMesh
    """

    def __init__(
        self,
        u_range: Tuple[float, float] = (0, TAU),
        v_range: Tuple[float, float] = (0, TAU),
        r1: float = 3.0,
        r2: float = 1.0,
        **kwargs,
    ):
        self.r1 = r1
        self.r2 = r2
        super().__init__(
            u_range=u_range,
            v_range=v_range,
            **kwargs,
        )

    def uv_func(self, u: float, v: float) -> np.ndarray:
        P = np.array([math.cos(u), math.sin(u), 0])
        return (self.r1 - self.r2 * math.cos(v)) * P - self.r2 * math.sin(v) * OUT


class Cylinder(Surface):
    """
    A three-dimensional cylindrical surface with configurable height, radius,
    axis direction, and angular parameter ranges.

    Cylinder inherits from :class:`Surface`. Its parameterization initially
    describes a unit-radius cylinder aligned with the z-axis. During point
    initialization, the geometry is scaled, stretched to the requested height,
    and rotated so that its axis aligns with the specified direction.

    Parameters
    ----------
    u_range : Tuple[float, float], optional
        Range of the angular parameter ``u`` in radians. Defaults to
        ``(0, TAU)``, covering a complete revolution around the cylinder.
    v_range : Tuple[float, float], optional
        Range of the axial parameter ``v``. Defaults to ``(-1, 1)``.
        The default range has a length of 2 before the height transformation.
    resolution : Tuple[int, int], optional
        Number of samples along the ``u`` and ``v`` parameter directions.
        Defaults to ``(101, 11)``.
    height : float, optional
        Requested axial length of the cylinder. Defaults to ``2``.
    radius : float, optional
        Radius of the cylinder. Defaults to ``1``.
    axis : Vect3, optional
        Vector specifying the direction to which the cylinder's original
        z-axis is aligned. Defaults to ``OUT``.
    **kwargs
        Additional keyword arguments forwarded to :class:`Surface`.

    Attributes
    ----------
    height : float
        Requested height used when stretching the surface.
    radius : float
        Radius used to scale the surface.
    axis : Vect3
        Direction vector used to orient the cylinder.

    Methods
    -------
    init_points()
        Initializes the surface geometry, scales it by ``radius``, stretches
        its depth to ``height``, and applies a matrix that aligns the z-axis
        with ``axis``.

    uv_func(u, v)
        Maps angular parameter ``u`` and axial parameter ``v`` to a point
        on the initial unit-radius cylinder.

    Notes
    -----
    - The initial parameterization is

      ``x = cos(u)``

      ``y = sin(u)``

      ``z = v``

    - The ``u`` parameter determines the position around the cylinder, while
      ``v`` determines the position along its original axis.
    - ``init_points()`` applies transformations in this order:
      scaling by ``radius``, stretching the depth to ``height``, and applying
      ``z_to_vector(axis)``.
    - Because the entire surface is first scaled by ``radius``, the subsequent
      depth stretch determines the final axial dimension independently of the
      initial depth scale.
    - The default ``v_range`` has length 2, so the default height of 2 preserves
      that axial length before accounting for the radius scaling and the
      implementation's depth-stretch behavior.
    - The surface is not capped by this class; it represents the curved
      lateral surface only.
    - The implementation does not validate ``radius``, ``height``, or ``axis``.
      Degenerate or unusual values may produce unexpected geometry.
    - The class relies on ``Surface`` to sample the parameterization and
      initialize its points.

    Examples
    --------
    Create a cylinder with default dimensions::

        cylinder = Cylinder()
        self.add(cylinder)

    Create a taller, wider cylinder::

        cylinder = Cylinder(
            height=4,
            radius=1.5,
        )
        self.add(cylinder)

    Orient the cylinder along another axis::

        cylinder = Cylinder(
            axis=RIGHT,
            height=3,
        )
        self.add(cylinder)

    Create a partial cylinder::

        cylinder = Cylinder(
            u_range=(0, PI),
            v_range=(-1, 1),
        )
        self.add(cylinder)

    See Also
    --------
    Surface
    Sphere
    Torus
    SurfaceMesh
    """

    def __init__(
        self,
        u_range: Tuple[float, float] = (0, TAU),
        v_range: Tuple[float, float] = (-1, 1),
        resolution: Tuple[int, int] = (101, 11),
        height: float = 2,
        radius: float = 1,
        axis: Vect3 = OUT,
        **kwargs,
    ):
        self.height = height
        self.radius = radius
        self.axis = axis
        super().__init__(
            u_range=u_range,
            v_range=v_range,
            resolution=resolution,
            **kwargs
        )

    def init_points(self):
        super().init_points()
        self.scale(self.radius)
        self.set_depth(self.height, stretch=True)
        self.apply_matrix(z_to_vector(self.axis))

    def uv_func(self, u: float, v: float) -> np.ndarray:
        return np.array([np.cos(u), np.sin(u), v])


class Cone(Cylinder):
    """
    A three-dimensional conical surface parameterized by an angular coordinate
    and a vertical coordinate.

    Cone inherits from :class:`Cylinder` and overrides its parameterization
    to make the radius decrease linearly as the vertical parameter increases.
    The default parameter range produces a cone with its base at the bottom
    and its apex at the top.

    Parameters
    ----------
    u_range : Tuple[float, float], optional
        Range of the angular parameter ``u`` in radians. Defaults to
        ``(0, TAU)``, covering a complete revolution around the cone's axis.
    v_range : Tuple[float, float], optional
        Range of the vertical parameter ``v``. Defaults to ``(0, 1)``,
        extending from the base to the apex.
    *args
        Additional positional arguments forwarded to ``Cylinder``.
    **kwargs
        Additional keyword arguments forwarded to ``Cylinder``, including
        supported options such as ``resolution``, ``height``, ``radius``,
        and ``axis``.

    Attributes
    ----------
    Inherited from Cylinder
        ``height``, ``radius``, and ``axis`` are initialized by the parent
        class when supplied through ``args`` or ``kwargs``.

    Methods
    -------
    uv_func(u, v)
        Maps the angular parameter ``u`` and vertical parameter ``v`` to a
        point on the cone's initial parameterized surface.

    Notes
    -----
    - The parameterization implemented by ``uv_func()`` is

      ``x = (1 - v) * cos(u)``

      ``y = (1 - v) * sin(u)``

      ``z = v``

    - At ``v = 0``, the cross-section has unit radius and lies at ``z = 0``.
    - At ``v = 1``, the radius becomes zero, producing the apex at ``z = 1``.
    - For values between 0 and 1, the radius decreases linearly according
      to ``1 - v``.
    - The default ``u_range`` creates a complete cone. A smaller range
      creates only a portion of its curved surface.
    - The inherited ``Cylinder.init_points()`` applies radius scaling,
      depth stretching, and axis alignment after generating the parameterized
      points.
    - Because the parent scales the geometry by ``radius``, the parameterized
      base radius is initially 1 before that scaling.
    - This class constructs only the curved lateral surface; it does not
      explicitly create a filled circular base.
    - The implementation does not validate parameter ranges or dimensions.

    Examples
    --------
    Create a cone with default settings::

        cone = Cone()
        self.add(cone)

    Create a taller cone with a wider base::

        cone = Cone(
            height=3,
            radius=1.5,
        )
        self.add(cone)

    Create a partial cone::

        cone = Cone(
            u_range=(0, PI),
            v_range=(0, 1),
        )
        self.add(cone)

    Orient the cone along another axis::

        cone = Cone(axis=RIGHT, height=2)
        self.add(cone)

    See Also
    --------
    Cylinder
    Surface
    SurfaceMesh
    """

    def __init__(
        self,
        u_range: Tuple[float, float] = (0, TAU),
        v_range: Tuple[float, float] = (0, 1),
        *args,
        **kwargs,
    ):
        super().__init__(u_range=u_range, v_range=v_range, *args, **kwargs)

    def uv_func(self, u: float, v: float) -> np.ndarray:
        return np.array([(1 - v) * np.cos(u), (1 - v) * np.sin(u), v])


class Line3D(Cylinder):
    """
    A three-dimensional line segment represented by a thin cylindrical surface.

    Line3D inherits from :class:`Cylinder` and constructs a cylinder between
    two endpoints. Its axis is determined by the vector from ``start`` to
    ``end``, its height is the distance between those endpoints, and its
    radius is half the requested width. The resulting cylinder is shifted
    to the midpoint of the endpoints.

    Parameters
    ----------
    start : Vect3
        Starting point of the line segment.
    end : Vect3
        Ending point of the line segment.
    width : float, optional
        Diameter of the cylindrical line. Defaults to ``0.05``.
    resolution : Tuple[int, int], optional
        Number of samples along the angular and axial parameter directions.
        Defaults to ``(21, 25)``.
    **kwargs
        Additional keyword arguments forwarded to :class:`Cylinder`, except
        for ``height``, ``radius``, ``axis``, and ``resolution``, which are
        explicitly supplied by this constructor.

    Attributes
    ----------
    Inherited from Cylinder
        The line's cylindrical surface geometry, radius, height, and axis
        are managed by the parent class.

    Notes
    -----
    - The direction vector is computed as ``end - start``.
    - The cylinder's height is ``get_norm(end - start)``, the Euclidean
      distance between the endpoints.
    - The cylinder's radius is ``width / 2``; therefore, ``width`` represents
      the nominal diameter of the line.
    - The direction vector is passed as the cylinder's ``axis`` so that its
      original z-axis is aligned with the segment direction.
    - After the parent constructor builds the cylinder, the object is shifted
      by ``(start + end) / 2`` to place it at the segment's midpoint.
    - This implementation assumes the inherited cylinder geometry is
      initially centered around its local origin.
    - If ``start`` and ``end`` are identical, the axis has zero length.
      The implementation does not explicitly handle this degenerate case.
    - The object is a cylindrical surface rather than a mathematical
      zero-thickness line, and no separate end caps are created here.

    Examples
    --------
    Create a 3D line segment::

        line = Line3D(
            start=np.array([0, 0, 0]),
            end=np.array([2, 1, 3]),
        )
        self.add(line)

    Customize the line's thickness and resolution::

        line = Line3D(
            start=LEFT,
            end=RIGHT + 2 * OUT,
            width=0.1,
            resolution=(32, 20),
        )
        self.add(line)

    Create a vertical segment::

        line = Line3D(
            start=ORIGIN,
            end=2 * OUT,
        )
        self.add(line)

    See Also
    --------
    Cylinder
    Cone
    Surface
    """

    def __init__(
        self,
        start: Vect3,
        end: Vect3,
        width: float = 0.05,
        resolution: Tuple[int, int] = (21, 25),
        **kwargs
    ):
        axis = end - start
        super().__init__(
            height=get_norm(axis),
            radius=width / 2,
            axis=axis,
            resolution=resolution,
            **kwargs
        )
        self.shift((start + end) / 2)


class Disk3D(Surface):
    """
    A flat, circular disk represented as a parameterized three-dimensional surface.

    Disk3D inherits from :class:`Surface` and constructs a disk in the XY-plane
    using a radial parameter and an angular parameter. The generated geometry
    is initially a unit disk and is scaled by the requested radius.

    Parameters
    ----------
    radius : float, optional
        Radius of the disk. Defaults to ``1``.
    u_range : Tuple[float, float], optional
        Range of the radial parameter ``u``. Defaults to ``(0, 1)``, spanning
        from the center to the edge of a unit disk before scaling.
    v_range : Tuple[float, float], optional
        Range of the angular parameter ``v`` in radians. Defaults to
        ``(0, TAU)``, covering a complete revolution.
    resolution : Tuple[int, int], optional
        Number of samples along the radial and angular parameter directions.
        Defaults to ``(2, 100)``.
    **kwargs
        Additional keyword arguments forwarded to :class:`Surface`.

    Methods
    -------
    uv_func(u, v)
        Maps radial parameter ``u`` and angular parameter ``v`` to a point
        in the XY-plane and returns it as a NumPy array.

    Notes
    -----
    - The parameterization implemented by ``uv_func()`` is

      ``x = u * cos(v)``

      ``y = u * sin(v)``

      ``z = 0``

    - The parameter ``u`` controls the radial distance from the origin,
      while ``v`` determines the angular position.
    - With the default ranges, the surface covers a complete disk centered
      at the origin in the XY-plane.
    - The constructor first initializes the surface through ``Surface`` and
      then applies ``self.scale(radius)`` to the generated geometry.
    - The final radial extent depends on both ``radius`` and ``u_range``.
      For example, a radial range of ``(0, 2)`` produces a disk with twice
      the requested radius after scaling.
    - A restricted ``v_range`` produces a partial disk sector rather than
      a complete disk.
    - This class creates a surface, not a separate filled polygon or a
      disk with thickness.
    - The implementation does not validate the radius, parameter ranges,
      or resolution.

    Examples
    --------
    Create a unit disk::

        disk = Disk3D()
        self.add(disk)

    Create a larger disk::

        disk = Disk3D(radius=2)
        self.add(disk)

    Create a partial disk sector::

        disk = Disk3D(
            radius=1.5,
            u_range=(0, 1),
            v_range=(0, PI),
        )
        self.add(disk)

    Increase angular sampling density::

        disk = Disk3D(
            resolution=(5, 150),
        )
        self.add(disk)

    See Also
    --------
    Surface
    Cylinder
    Sphere
    """

    def __init__(
        self,
        radius: float = 1,
        u_range: Tuple[float, float] = (0, 1),
        v_range: Tuple[float, float] = (0, TAU),
        resolution: Tuple[int, int] = (2, 100),
        **kwargs
    ):
        super().__init__(
            u_range=u_range,
            v_range=v_range,
            resolution=resolution,
            **kwargs,
        )
        self.scale(radius)

    def uv_func(self, u: float, v: float) -> np.ndarray:
        return np.array([
            u * math.cos(v),
            u * math.sin(v),
            0
        ])


class Square3D(Surface):
    """
    A flat, square surface in the XY-plane with a configurable side length.

    Square3D inherits from :class:`Surface` and defines a planar square through
    two parameters, ``u`` and ``v``. The initial surface spans the configured
    parameter ranges and is then scaled by half the requested side length.

    Parameters
    ----------
    side_length : float, optional
        Intended side length of the square when both parameter ranges have
        their default values. Defaults to ``2.0``.
    u_range : Tuple[float, float], optional
        Range of the first planar parameter. Defaults to ``(-1, 1)``.
    v_range : Tuple[float, float], optional
        Range of the second planar parameter. Defaults to ``(-1, 1)``.
    resolution : Tuple[int, int], optional
        Number of samples along the two parameter directions. Defaults to
        ``(2, 2)``.
    **kwargs
        Additional keyword arguments forwarded to :class:`Surface`.

    Methods
    -------
    uv_func(u, v)
        Maps the two parameters to a point in the XY-plane and returns it
        as a NumPy array.

    Notes
    -----
    - The parameterization is ``(u, v, 0)``, so the surface lies in the
      XY-plane before any external transformations.
    - The constructor applies ``self.scale(side_length / 2)`` after the
      parent surface has been initialized.
    - With the default parameter ranges, the square spans from ``-1`` to
      ``1`` in each planar direction before scaling, producing the requested
      side length.
    - If custom parameter ranges are supplied, the resulting side lengths
      also depend on those ranges; ``side_length`` acts as a scale factor
      rather than enforcing the final dimensions independently.
    - This class creates a planar surface, not a solid cube or a thick
      square prism.

    Examples
    --------
    Create a square with side length 2::

        square = Square3D()
        self.add(square)

    Create a larger square::

        square = Square3D(side_length=4)
        self.add(square)

    Create a square surface with denser sampling::

        square = Square3D(
            side_length=3,
            resolution=(10, 10),
        )
        self.add(square)

    See Also
    --------
    Surface
    Disk3D
    square_to_cube_faces
    """

    def __init__(
        self,
        side_length: float = 2.0,
        u_range: Tuple[float, float] = (-1, 1),
        v_range: Tuple[float, float] = (-1, 1),
        resolution: Tuple[int, int] = (2, 2),
        **kwargs,
    ):
        super().__init__(
            u_range=u_range, 
            v_range=v_range, 
            resolution=resolution, 
            **kwargs
        )
        self.scale(side_length / 2)

    def uv_func(self, u: float, v: float) -> np.ndarray:
        return np.array([u, v, 0])


def square_to_cube_faces(square: T) -> list[T]:
    radius = square.get_height() / 2
    square.move_to(radius * OUT)
    result = [square.copy()]
    result.extend([
        square.copy().rotate(PI / 2, axis=vect, about_point=ORIGIN)
        for vect in compass_directions(4)
    ])
    result.append(square.copy().rotate(PI, RIGHT, about_point=ORIGIN))
    return result


class Cube(Group):
    """
    A three-dimensional cube constructed from six square surface faces.

    Cube inherits from :class:`Group`. It creates a :class:`Square3D` with the
    requested dimensions and visual properties, converts it into six oriented
    faces using ``square_to_cube_faces()``, and groups those faces together.

    Parameters
    ----------
    color : ManimColor, optional
        Color applied to the square used to construct the faces. Defaults
        to ``BLUE``.
    opacity : float, optional
        Opacity applied to the square surface and its copied faces.
        Defaults to ``1``.
    shading : Tuple[float, float, float], optional
        Shading parameters forwarded to ``Square3D``. Defaults to
        ``(0.1, 0.5, 0.1)``.
    square_resolution : Tuple[int, int], optional
        Sampling resolution of each square face along its two parameter
        directions. Defaults to ``(2, 2)``.
    side_length : float, optional
        Side length of the cube. Defaults to ``2``.
    **kwargs
        Additional keyword arguments forwarded to :class:`Group`.

    Attributes
    ----------
    Inherited from Group
        The six square faces are stored as the group's submobjects and can
        be accessed through the usual group operations.

    Notes
    -----
    - The cube is constructed from six separate ``Square3D`` surface copies.
    - ``square_resolution`` controls the sampling resolution of each face,
      not the number of faces.
    - The face geometry is generated by ``square_to_cube_faces()``, which
      also repositions the original square before producing the copies.
    - The cube's default side length is 2, and the faces are arranged around
      the origin by the helper function.
    - This implementation groups the surface faces; it does not construct
      a single solid mesh or explicitly create a volumetric interior.
    - ``color``, ``opacity``, and ``shading`` are passed to ``Square3D``.
      The resulting visual properties are inherited by the copied faces.
    - Any extra ``kwargs`` are passed to ``Group``, not to ``Square3D``.

    Examples
    --------
    Create a default blue cube::

        cube = Cube()
        self.add(cube)

    Create a larger cube with a custom color::

        cube = Cube(
            side_length=3,
            color=RED,
            opacity=0.8,
        )
        self.add(cube)

    Increase the sampling resolution of each face::

        cube = Cube(
            square_resolution=(10, 10),
        )
        self.add(cube)

    See Also
    --------
    Group
    Square3D
    square_to_cube_faces
    """

    def __init__(
        self,
        color: ManimColor = BLUE,
        opacity: float = 1,
        shading: Tuple[float, float, float] = (0.1, 0.5, 0.1),
        square_resolution: Tuple[int, int] = (2, 2),
        side_length: float = 2,
        **kwargs,
    ):
        face = Square3D(
            resolution=square_resolution,
            side_length=side_length,
            color=color,
            opacity=opacity,
            shading=shading,
        )
        super().__init__(*square_to_cube_faces(face), **kwargs)


class Prism(Cube):
    """
    A three-dimensional rectangular prism constructed by stretching a cube
    independently along its three coordinate dimensions.

    Prism inherits from :class:`Cube`. It first creates the six square faces
    of a cube, then rescales the resulting group to fit the requested width,
    height, and depth. Stretching is enabled so each dimension can be adjusted
    independently.

    Parameters
    ----------
    width : float, optional
        Target extent along dimension 0 (the x-axis). Defaults to ``3.0``.
    height : float, optional
        Target extent along dimension 1 (the y-axis). Defaults to ``2.0``.
    depth : float, optional
        Target extent along dimension 2 (the z-axis). Defaults to ``1.0``.
    **kwargs
        Additional keyword arguments forwarded to :class:`Cube`, including
        its color, opacity, shading, square resolution, and side length.

    Notes
    -----
    - The constructor first initializes the parent ``Cube``.
    - It then calls ``rescale_to_fit(value, dim, stretch=True)`` for each
      requested dimension.
    - The dimension indices correspond to x (0), y (1), and z (2).
    - Since ``stretch=True``, the prism's dimensions are adjusted independently
      rather than preserving the cube's original proportions.
    - The final geometry is a group of six surface faces, not a single solid
      volumetric mesh.
    - The requested dimensions describe target extents along the coordinate
      dimensions; the resulting shape also depends on the parent cube's
      initial geometry.
    - The implementation does not explicitly validate the supplied dimensions.

    Examples
    --------
    Create a prism with the default dimensions::

        prism = Prism()
        self.add(prism)

    Create a wide rectangular prism::

        prism = Prism(
            width=4,
            height=2,
            depth=1,
        )
        self.add(prism)

    Customize the faces through Cube's parameters::

        prism = Prism(
            width=3,
            height=2,
            depth=1,
            color=BLUE,
            opacity=0.8,
            square_resolution=(4, 4),
        )
        self.add(prism)

    See Also
    --------
    Cube
    Square3D
    square_to_cube_faces
    """

    def __init__(
        self,
        width: float = 3.0,
        height: float = 2.0,
        depth: float = 1.0,
        **kwargs
    ):
        super().__init__(**kwargs)
        for dim, value in enumerate([width, height, depth]):
            self.rescale_to_fit(value, dim, stretch=True)


class VGroup3D(VGroup):
    """
    A group of vectorized mobjects configured for three-dimensional rendering
    with optional depth testing and surface shading.

    VGroup3D inherits from :class:`VGroup`, so it can contain multiple
    :class:`VMobject` instances and supports the usual group operations.
    During initialization, it forwards the supplied mobjects and additional
    keyword arguments to ``VGroup``, applies the specified shading parameters,
    and optionally enables depth testing.

    Parameters
    ----------
    *vmobjects : VMobject
        Variable number of vectorized mobjects to include in the group.
    depth_test : bool, optional
        Whether to enable depth testing for the group. When ``True``, objects
        are rendered with depth-aware visibility, helping determine which
        surfaces appear in front of others. Defaults to ``True``.
    shading : tuple of float, optional
        Three shading coefficients passed as positional arguments to
        ``set_shading``. Defaults to ``(0.2, 0.2, 0.2)``. Their precise
        interpretation depends on the shading implementation.
    **kwargs
        Additional keyword arguments forwarded to :class:`VGroup`.

    Notes
    -----
    - The parent ``VGroup`` is initialized before shading is configured.
    - The shading tuple is unpacked into ``set_shading`` using
      ``self.set_shading(*shading)``.
    - Depth testing is enabled only when ``depth_test`` evaluates to ``True``.
    - Disabling depth testing skips the call to ``apply_depth_test``; it does
      not undo depth testing that may already be configured elsewhere.
    - Depth testing affects depth-aware rendering, while shading controls the
      appearance of the group's surfaces.
    - This class does not create three-dimensional geometry by itself.
      The supplied mobjects determine the group's actual geometry.

    Examples
    --------
    Create a group containing multiple vectorized mobjects::

        group = VGroup3D(
            sphere,
            cube,
        )
        self.add(group)

    Configure custom shading coefficients::

        group = VGroup3D(
            sphere,
            cube,
            shading=(0.3, 0.5, 0.2),
        )
        self.add(group)

    Disable depth testing during initialization::

        group = VGroup3D(
            sphere,
            cube,
            depth_test=False,
        )
        self.add(group)

    See Also
    --------
    VGroup
    VMobject
    """

    def __init__(
        self,
        *vmobjects: VMobject,
        depth_test: bool = True,
        shading: Tuple[float, float, float] = (0.2, 0.2, 0.2),
        **kwargs
    ):
        super().__init__(*vmobjects, **kwargs)
        self.set_shading(*shading)
        if depth_test:
            self.apply_depth_test()


class VCube(VGroup3D):
    """
    A three-dimensional cube constructed by arranging six styled square faces
    into a :class:`VGroup3D`.

    VCube inherits from :class:`VGroup3D`. It creates a square with the requested
    side length and visual styling, converts that square into the six faces of a
    cube using ``square_to_cube_faces``, and initializes the group with those
    faces. Additional keyword arguments are forwarded to both the square and
    the resulting three-dimensional group.

    Parameters
    ----------
    side_length : float, optional
        Side length of the square used to construct the cube faces. Defaults
        to ``2.0``.
    fill_color : ManimColor, optional
        Fill color applied to the square and forwarded to the parent group.
        Defaults to ``BLUE_D``.
    fill_opacity : float, optional
        Opacity of the face fill. Defaults to ``1``.
    stroke_width : float, optional
        Width of the face outlines. Defaults to ``0``, which disables visible
        stroke width unless modified by other styling behavior.
    **kwargs
        Additional keyword arguments forwarded to both ``Square`` and
        ``VGroup3D``. Supported arguments depend on the respective constructors.

    Notes
    -----
    - A ``style`` dictionary is created from the fill color, fill opacity,
      stroke width, and additional keyword arguments.
    - A ``Square`` of the requested side length is created using this style.
    - ``square_to_cube_faces(face)`` generates the six faces used to form the
      cube's surface.
    - The generated faces are unpacked into ``VGroup3D`` as individual
      positional mobjects.
    - The same style dictionary is also passed to ``VGroup3D``. Consequently,
      keyword arguments must be compatible with both the ``Square`` and
      ``VGroup3D`` constructors.
    - Since ``VCube`` is a group of faces, it represents the cube's surface
      rather than a single volumetric solid mesh.
    - Depth testing and shading are configured by the inherited ``VGroup3D``
      constructor unless overridden through compatible keyword arguments.
    - The implementation does not explicitly validate ``side_length``,
      ``fill_opacity``, or ``stroke_width``.

    Examples
    --------
    Create a cube with the default appearance::

        cube = VCube()
        self.add(cube)

    Create a larger cube with a custom fill color::

        cube = VCube(
            side_length=3,
            fill_color=GREEN,
            fill_opacity=0.8,
        )
        self.add(cube)

    Create a cube with visible outlines::

        cube = VCube(
            side_length=2,
            fill_color=BLUE_D,
            stroke_width=1,
            stroke_color=WHITE,
        )
        self.add(cube)

    See Also
    --------
    VGroup3D
    Cube
    Square
    square_to_cube_faces
    """

    def __init__(
        self,
        side_length: float = 2.0,
        fill_color: ManimColor = BLUE_D,
        fill_opacity: float = 1,
        stroke_width: float = 0,
        **kwargs
    ):
        style = dict(
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            stroke_width=stroke_width,
            **kwargs
        )
        face = Square(side_length=side_length, **style)
        super().__init__(*square_to_cube_faces(face), **style)


class VPrism(VCube):
    """
    A three-dimensional rectangular prism created by independently stretching
    a :class:`VCube` along its three coordinate dimensions.

    VPrism inherits from :class:`VCube`. It first initializes a cube using the
    provided keyword arguments, then rescales the resulting group to match the
    requested width, height, and depth. Stretching is enabled so each dimension
    can be adjusted independently.

    Parameters
    ----------
    width : float, optional
        Target extent along dimension 0 (the x-axis). Defaults to ``3.0``.
    height : float, optional
        Target extent along dimension 1 (the y-axis). Defaults to ``2.0``.
    depth : float, optional
        Target extent along dimension 2 (the z-axis). Defaults to ``1.0``.
    **kwargs
        Additional keyword arguments forwarded to :class:`VCube`, such as
        ``side_length``, ``fill_color``, ``fill_opacity``, ``stroke_width``,
        and other supported styling or rendering options.

    Notes
    -----
    - The parent ``VCube`` constructor creates the initial cube geometry.
    - The constructor then iterates over ``width``, ``height``, and ``depth``,
      calling ``rescale_to_fit(value, dim, stretch=True)`` for each dimension.
    - The dimension indices correspond to x (0), y (1), and z (2).
    - Setting ``stretch=True`` allows each dimension to change independently
      instead of preserving the original proportions.
    - The resulting object retains the six-face group structure inherited
      from ``VCube`` rather than becoming a single volumetric mesh.
    - The requested dimensions describe target extents along the coordinate
      dimensions. The final geometry also depends on the initial cube geometry
      and the behavior of ``rescale_to_fit``.
    - The constructor does not explicitly validate the supplied dimensions.

    Examples
    --------
    Create a prism with the default dimensions::

        prism = VPrism()
        self.add(prism)

    Create a wide rectangular prism::

        prism = VPrism(
            width=4,
            height=2,
            depth=1,
        )
        self.add(prism)

    Customize the initial cube's appearance::

        prism = VPrism(
            width=3,
            height=2,
            depth=1,
            side_length=2,
            fill_color=BLUE_D,
            fill_opacity=0.8,
            stroke_width=1,
        )
        self.add(prism)

    See Also
    --------
    VCube
    VGroup3D
    square_to_cube_faces
    """

    def __init__(
        self,
        width: float = 3.0,
        height: float = 2.0,
        depth: float = 1.0,
        **kwargs
    ):
        super().__init__(**kwargs)
        for dim, value in enumerate([width, height, depth]):
            self.rescale_to_fit(value, dim, stretch=True)


class Dodecahedron(VGroup3D):
    """
    A three-dimensional regular dodecahedron constructed from twelve pentagonal
    faces and grouped into a depth-aware :class:`VGroup3D`.

    A dodecahedron is a Platonic solid with twelve regular pentagonal faces,
    thirty edges, and twenty vertices. This implementation constructs an initial
    pair of pentagons, generates additional pairs through matrix transformations,
    and then creates the remaining faces by reflecting the generated pentagons
    through the origin.

    Parameters
    ----------
    fill_color : ManimColor, optional
        Fill color applied to the pentagonal faces. Defaults to ``BLUE_E``.
    fill_opacity : float, optional
        Opacity of the face fills. Defaults to ``1``.
    stroke_color : ManimColor, optional
        Color of the pentagon outlines. Defaults to ``BLUE_E``.
    stroke_width : float, optional
        Width of the pentagon outlines. Defaults to ``1``.
    shading : tuple of float, optional
        Three shading coefficients passed to the inherited ``VGroup3D``
        constructor. Defaults to ``(0.2, 0.2, 0.2)``.
    **kwargs
        Additional keyword arguments forwarded to :class:`VGroup3D` and
        included in the style dictionary passed to each ``Polygon``.

    Notes
    -----
    - The constructor creates a style dictionary containing fill, stroke,
      shading, and additional keyword arguments.
    - The golden ratio is calculated as ``(1 + sqrt(5)) / 2`` and used to
      define the vertices of the initial pentagon.
    - The vectors ``x``, ``y``, and ``z`` are obtained from the identity matrix
      and used to construct transformation matrices.
    - The first pentagon is defined by five three-dimensional vertex positions.
    - The second pentagon is created by stretching the first by a factor of
      ``-1`` along dimension 2 about the origin, then reversing its point order.
    - These two pentagons form the initial pair along the positive x-axis.
    - Copies of the initial pair are transformed using matrix operations to
      produce corresponding pairs in other orientations.
    - Each generated pentagon is copied, reflected through the origin using
      ``apply_function``, and reversed to create the opposite-facing faces.
    - The resulting collection contains twelve pentagons, which are passed to
      ``VGroup3D`` for grouping, shading, and depth-testing configuration.
    - The geometry is assembled from polygonal surface faces rather than a
      single volumetric mesh.
    - The implementation does not explicitly validate the styling parameters.

    Examples
    --------
    Create a dodecahedron with the default appearance::

        solid = Dodecahedron()
        self.add(solid)

    Customize the face fill and outlines::

        solid = Dodecahedron(
            fill_color=BLUE_D,
            fill_opacity=0.9,
            stroke_color=WHITE,
            stroke_width=1.5,
        )
        self.add(solid)

    Adjust the shading coefficients::

        solid = Dodecahedron(
            shading=(0.3, 0.5, 0.2),
        )
        self.add(solid)

    See Also
    --------
    VGroup3D
    Polygon
    VCube
    """

    def __init__(
        self,
        fill_color: ManimColor = BLUE_E,
        fill_opacity: float = 1,
        stroke_color: ManimColor = BLUE_E,
        stroke_width: float = 1,
        shading: Tuple[float, float, float] = (0.2, 0.2, 0.2),
        **kwargs,
    ):
        style = dict(
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            shading=shading,
            **kwargs
        )

        # Start by creating two of the pentagons, meeting
        # back to back on the positive x-axis
        phi = (1 + math.sqrt(5)) / 2
        x, y, z = np.identity(3)
        pentagon1 = Polygon(
            np.array([phi, 1 / phi, 0]),
            np.array([1, 1, 1]),
            np.array([1 / phi, 0, phi]),
            np.array([1, -1, 1]),
            np.array([phi, -1 / phi, 0]),
            **style
        )
        pentagon2 = pentagon1.copy().stretch(-1, 2, about_point=ORIGIN)
        pentagon2.reverse_points()
        x_pair = VGroup(pentagon1, pentagon2)
        z_pair = x_pair.copy().apply_matrix(np.array([z, -x, -y]).T)
        y_pair = x_pair.copy().apply_matrix(np.array([y, z, x]).T)

        pentagons = [*x_pair, *y_pair, *z_pair]
        for pentagon in list(pentagons):
            pc = pentagon.copy()
            pc.apply_function(lambda p: -p)
            pc.reverse_points()
            pentagons.append(pc)

        super().__init__(*pentagons, **style)


class Prismify(VGroup3D):
    """
    Creates a three-dimensional prism-like object by extruding a vectorized
    mobject along a specified direction.

    Prismify inherits from :class:`VGroup3D`. It uses the input mobject as the
    base, constructs side walls between adjacent anchor points, and creates a
    translated copy of the base as the opposite face. The resulting faces are
    grouped into a single three-dimensional mobject group.

    Parameters
    ----------
    vmobject : VMobject
        Vectorized mobject used as the base profile. Its anchor points define
        the edges from which the side walls are constructed.
    depth : float, optional
        Distance by which the base profile is extruded along ``direction``.
        Defaults to ``1.0``.
    direction : ndarray or array-like, optional
        Direction vector along which the extrusion occurs. Defaults to ``IN``.
        The vector is multiplied by ``depth`` to obtain the extrusion offset.
    **kwargs
        Additional keyword arguments forwarded to :class:`VGroup3D`.

    Notes
    -----
    - The extrusion displacement is calculated as ``depth * direction``.
    - A copy of the original mobject is added as the first face.
    - The base's anchor points are obtained using ``get_anchors()``.
    - ``adjacent_pairs(points)`` supplies consecutive anchor-point pairs used
      to construct the side walls.
    - Each wall is a ``VMobject`` that matches the original mobject's style.
    - The wall's four corners are defined by the two original points and their
      translated counterparts.
    - A translated copy of the original mobject forms the opposite face.
    - The opposite face has its point order reversed, which can affect its
      orientation and rendering.
    - All generated faces are passed to ``VGroup3D`` as a single group.
    - The implementation assumes straight edges between adjacent anchor points.
      Curved boundaries are not explicitly approximated by curved side walls.
    - The code does not explicitly close an open profile or validate the input
      geometry, depth, or direction vector.
    - The resulting object is a collection of surfaces, not necessarily a
      watertight volumetric mesh.

    Examples
    --------
    Extrude a square along the default direction::

        square = Square()
        prism = Prismify(square, depth=2)
        self.add(prism)

    Extrude a triangle with a custom direction::

        triangle = Triangle()
        prism = Prismify(
            triangle,
            depth=1.5,
            direction=RIGHT,
        )
        self.add(prism)

    Pass additional group options::

        prism = Prismify(
            Square(),
            depth=2,
            direction=OUT,
            shading=(0.3, 0.4, 0.2),
        )
        self.add(prism)

    See Also
    --------
    VGroup3D
    VMobject
    adjacent_pairs
    """

    def __init__(self, vmobject, depth=1.0, direction=IN, **kwargs):
        # At the moment, this assume stright edges
        vect = depth * direction
        pieces = [vmobject.copy()]
        points = vmobject.get_anchors()
        for p1, p2 in adjacent_pairs(points):
            wall = VMobject()
            wall.match_style(vmobject)
            wall.set_points_as_corners([p1, p2, p2 + vect, p1 + vect])
            pieces.append(wall)
        top = vmobject.copy()
        top.shift(vect)
        top.reverse_points()
        pieces.append(top)
        super().__init__(*pieces, **kwargs)
