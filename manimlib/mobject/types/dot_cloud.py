from __future__ import annotations

import numpy as np

from manimlib.constants import GREY_C, YELLOW
from manimlib.constants import ORIGIN, NULL_POINTS
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.types.point_cloud_mobject import PMobject
from manimlib.utils.iterables import resize_with_interpolation
from manimlib.renderer.uniform_block import COMMON_UNIFORMS
from manimlib.renderer.uniform_block import uniform_block_dtype

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy.typing as npt
    from typing import Sequence, Tuple
    from manimlib.typing import ManimColor, Vect3, Vect3Array, Self


DEFAULT_DOT_RADIUS = 0.05
DEFAULT_GLOW_DOT_RADIUS = 0.2
DEFAULT_GRID_HEIGHT = 6
DEFAULT_BUFF_RATIO = 0.5


class DotCloud(PMobject):
    """
    A point-cloud object that renders each point as a camera-facing dot.

    `DotCloud` inherits from :class:`PMobject` and extends its point-based data
    with a radius for each point. Unlike a collection of ordinary geometric
    circles, its dots are rendered using a GPU shader that expands each point
    into a camera-facing quad.

    Each point stores three-dimensional coordinates, a radius, and an RGBA
    color. The shader also supports glow and anti-aliasing controls.

    Parameters
    ----------
    points : Vect3Array, optional
        Initial three-dimensional point coordinates. Each point represents
        the center of a dot. Defaults to NULL_POINTS.
    color : ManimColor, optional
        Initial color assigned through the parent PMobject initialization.
        Defaults to GREY_C.
    opacity : float, optional
        Initial opacity of the dots. Defaults to 1.0.
    radius : float, optional
        Initial radius assigned to every point. Defaults to
        DEFAULT_DOT_RADIUS.
    glow_factor : float, optional
        Glow intensity parameter passed to the shader uniforms.
        Defaults to 0.0.
    anti_alias_width : float, optional
        Width of the shader's anti-aliasing region. Defaults to 2.0.
    **kwargs
        Additional keyword arguments forwarded to PMobject.

    Attributes
    ----------
    radius : float
        Initial radius value stored during initialization. Later radius
        changes are applied to the point data.
    glow_factor : float
        Initial glow factor stored during initialization.
    anti_alias_width : float
        Anti-aliasing width stored during initialization.
    data_dtype : Sequence
        Structured point-data fields containing ``point``, ``radius``,
        and ``rgba`` values.
    uniform_dtype : np.dtype
        Shader uniform layout containing common uniforms, ``anti_alias_width``,
        and ``glow_factor``.
    shader_file : str
        Name of the shader file used to render the dots: ``true_dot.wgsl``.
    verts_per_record : int
        Number of vertices generated for each point record: 6.

    Examples
    --------
    Create a cloud of dots from explicit coordinates:

        points = np.array([
            [-1.0, 0.0, 0.0],
            [ 0.0, 1.0, 0.0],
            [ 1.0, 0.0, 0.0],
        ])

        cloud = DotCloud(points, color=BLUE, radius=0.05)

    Create an initially empty cloud and set its points later:

        cloud = DotCloud(color=RED)
        cloud.set_points(points)

    Create a regular three-dimensional grid:

        cloud = DotCloud(radius=0.04)
        cloud.to_grid(
            n_rows=5,
            n_cols=5,
            n_layers=3,
            h_buff_ratio=1.0,
            v_buff_ratio=1.0,
            d_buff_ratio=1.0,
        )

    Use the same spacing ratio for every dimension:

        cloud.to_grid(
            n_rows=4,
            n_cols=4,
            n_layers=2,
            buff_ratio=0.5,
        )

    Adjust individual point radii:

        cloud.set_radii([0.02, 0.05, 0.08])
        radii = cloud.get_radii()

    Set a uniform radius for all points:

        cloud.set_radius(0.06)
        maximum_radius = cloud.get_radius()

    Scale the dot radii independently of the point positions:

        cloud.scale_radii(1.5)

    Change the glow factor:

        cloud.set_glow_factor(0.8)
        glow = cloud.get_glow_factor()

    Scale the cloud and its radii together:

        cloud.scale(2.0)

    Scale the point positions without scaling the radii:

        cloud.scale(2.0, scale_radii=False)

    Enable 3D shading and depth testing:

        cloud.make_3d(
            reflectiveness=0.5,
            gloss=0.1,
            shadow=0.2,
        )

    Methods
    -------
    to_grid(n_rows, n_cols, n_layers=1, buff_ratio=None,
            h_buff_ratio=1.0, v_buff_ratio=1.0, d_buff_ratio=1.0,
            height=DEFAULT_GRID_HEIGHT)
        Generate regularly arranged point coordinates in a grid or
        three-dimensional lattice, optionally adjusting spacing and height.

    set_radii(radii)
        Assign radii to the points. If the number of supplied radii differs
        from the number of points, resize_with_interpolation is used to
        produce the required number of values.

    get_radii()
        Return the stored radius array.

    set_radius(radius)
        Assign the same radius value to every point and refresh the
        bounding box.

    get_radius()
        Return the maximum radius in the point data.

    scale_radii(scale_factor)
        Multiply the existing radii by the supplied factor.

    set_glow_factor(glow_factor)
        Update the ``glow_factor`` shader uniform.

    get_glow_factor()
        Return the current ``glow_factor`` shader uniform.

    compute_bounding_box()
        Compute the parent bounding box and expand its minimum and maximum
        corners by the maximum dot radius.

    scale(scale_factor, scale_radii=True, **kwargs)
        Scale the point positions using the parent implementation and,
        by default, scale the radii as well.

    make_3d(reflectiveness=0.5, gloss=0.1, shadow=0.2)
        Set shading parameters and enable depth testing.

    Notes
    -----
    - The radius is stored separately for each point in ``data["radius"]``.
    - ``set_radius`` writes the supplied value to all point records, whereas
      ``set_radii`` supports different radii for different points.
    - ``get_radius`` returns the maximum stored radius, not an average.
    - ``scale_radii`` changes dot sizes without directly scaling positions.
    - The ``scale`` method scales radii by default. Set ``scale_radii=False``
      to scale only the point positions.
    - ``to_grid`` first creates integer grid coordinates, then adjusts the
      point cloud's dimensions according to the requested spacing ratios.
      If ``buff_ratio`` is provided, it overrides all three individual
      spacing ratios.
    - In ``to_grid``, ``height`` is applied after the dimension-based
      rescaling when it is not None. The cloud is then centered.
    - ``set_glow_factor`` updates the uniform directly; it does not update
      the stored ``self.glow_factor`` attribute.
    - ``init_uniforms`` initializes the shader uniforms from the stored
      glow factor and anti-aliasing width.
    - ``compute_bounding_box`` expands the bounding box using the maximum
      radius, so it accounts for dot size beyond the point centers.
    - Calling ``get_radius`` on an object with no point records may fail
      because the maximum of an empty radius array is undefined.
    """

    shader_file: str = "true_dot.wgsl"
    # Each dot is expanded into a camera facing quad by the vertex shader
    verts_per_record: int = 6
    data_dtype: Sequence[Tuple[str, type, Tuple[int]]] = [
        ('point', np.float32, (3,)),
        ('radius', np.float32, (1,)),
        ('rgba', np.float32, (4,)),
    ]
    uniform_dtype: np.dtype = uniform_block_dtype(
        *COMMON_UNIFORMS,
        ("anti_alias_width", 1),
        ("glow_factor", 1),
    )

    def __init__(
        self,
        points: Vect3Array = NULL_POINTS,
        color: ManimColor = GREY_C,
        opacity: float = 1.0,
        radius: float = DEFAULT_DOT_RADIUS,
        glow_factor: float = 0.0,
        anti_alias_width: float = 2.0,
        **kwargs
    ):
        self.radius = radius
        self.glow_factor = glow_factor
        self.anti_alias_width = anti_alias_width

        super().__init__(
            color=color,
            opacity=opacity,
            **kwargs
        )
        self.set_radius(self.radius)

        if points is not None:
            self.set_points(points)

    def init_uniforms(self) -> None:
        super().init_uniforms()
        self.uniforms["glow_factor"] = self.glow_factor
        self.uniforms["anti_alias_width"] = self.anti_alias_width

    def to_grid(
        self,
        n_rows: int,
        n_cols: int,
        n_layers: int = 1,
        buff_ratio: float | None = None,
        h_buff_ratio: float = 1.0,
        v_buff_ratio: float = 1.0,
        d_buff_ratio: float = 1.0,
        height: float = DEFAULT_GRID_HEIGHT,
    ) -> Self:
        n_points = n_rows * n_cols * n_layers
        points = np.repeat(range(n_points), 3, axis=0).reshape((n_points, 3))
        points[:, 0] = points[:, 0] % n_cols
        points[:, 1] = (points[:, 1] // n_cols) % n_rows
        points[:, 2] = points[:, 2] // (n_rows * n_cols)
        self.set_points(points.astype(float))

        if buff_ratio is not None:
            v_buff_ratio = buff_ratio
            h_buff_ratio = buff_ratio
            d_buff_ratio = buff_ratio

        radius = self.get_radius()
        ns = [n_cols, n_rows, n_layers]
        brs = [h_buff_ratio, v_buff_ratio, d_buff_ratio]
        self.set_radius(0)
        for n, br, dim in zip(ns, brs, range(3)):
            self.rescale_to_fit(2 * radius * (1 + br) * (n - 1), dim, stretch=True)
        self.set_radius(radius)
        if height is not None:
            self.set_height(height)
        self.center()
        return self

    def set_radii(self, radii: npt.ArrayLike) -> Self:
        n_points = self.get_num_points()
        radii = np.array(radii).reshape((len(radii), 1))
        self.data["radius"] = resize_with_interpolation(radii, n_points)
        self.refresh_bounding_box()
        return self

    def get_radii(self) -> np.ndarray:
        return self.data["radius"]

    def set_radius(self, radius: float) -> Self:
        with self.data.being_written() as data:
            data["radius"] = radius
        self.refresh_bounding_box()
        return self

    def get_radius(self) -> float:
        return self.get_radii().max()

    def scale_radii(self, scale_factor: float) -> Self:
        self.set_radius(scale_factor * self.get_radii())
        return self

    def set_glow_factor(self, glow_factor: float) -> Self:
        self.uniforms["glow_factor"] = glow_factor
        return self

    def get_glow_factor(self) -> float:
        return self.uniforms["glow_factor"]

    def compute_bounding_box(self) -> Vect3Array:
        bb = super().compute_bounding_box()
        radius = self.get_radius()
        bb[0] += np.full((3,), -radius)
        bb[2] += np.full((3,), radius)
        return bb

    def scale(
        self,
        scale_factor: float | npt.ArrayLike,
        scale_radii: bool = True,
        **kwargs
    ) -> Self:
        super().scale(scale_factor, **kwargs)
        if scale_radii:
            self.set_radii(scale_factor * self.get_radii())
        return self

    def make_3d(
        self,
        reflectiveness: float = 0.5,
        gloss: float = 0.1,
        shadow: float = 0.2
    ) -> Self:
        self.set_shading(reflectiveness, gloss, shadow)
        self.apply_depth_test()
        return self


class TrueDot(DotCloud):
    """
    A single shader-rendered dot positioned at a specified three-dimensional
    center.

    `TrueDot` inherits from :class:`DotCloud` and initializes the parent with
    a point array containing exactly one point. It therefore provides a
    convenient way to create an individual dot while retaining DotCloud's
    radius, color, opacity, glow, anti-aliasing, and shading functionality.

    Parameters
    ----------
    center : Vect3, optional
        Three-dimensional coordinates of the dot's center. Defaults to ORIGIN.
    **kwargs
        Additional keyword arguments forwarded to :class:`DotCloud`, such as
        ``color``, ``opacity``, ``radius``, ``glow_factor``, and
        ``anti_alias_width``.

    Examples
    --------
    Create a dot at the origin:

        dot = TrueDot()

    Place a dot at a specific position:

        dot = TrueDot(np.array([1.0, 2.0, 0.0]))

    Customize its appearance:

        dot = TrueDot(
            center=np.array([1.0, 0.0, 0.0]),
            color=BLUE,
            radius=0.08,
            opacity=0.8,
        )

    Create a glowing dot:

        dot = TrueDot(
            center=np.array([0.0, 1.0, 0.0]),
            color=YELLOW,
            radius=0.06,
            glow_factor=0.8,
        )

    Notes
    -----
    - The center is converted into a NumPy array containing one point and
      passed to DotCloud through the ``points`` argument.
    - The dot's position is represented by its point coordinates; its visual
      size is controlled by the radius.
    - Since the parent receives one point, the object starts with exactly
      one dot.
    - All other behavior, including radius management, bounding-box
      calculation, shader rendering, and optional 3D shading, is inherited
      from DotCloud.
    """

    def __init__(self, center: Vect3 = ORIGIN, **kwargs):
        super().__init__(points=np.array([center]), **kwargs)


class GlowDots(DotCloud):
    """
    A point cloud of glowing dots rendered using the DotCloud shader.

    `GlowDots` inherits from :class:`DotCloud` and provides defaults suited
    to a glowing appearance: yellow color, a glow-dot-specific radius, and
    a stronger glow factor. It forwards the supplied points and appearance
    settings to the parent class, which handles point data, shader uniforms,
    and rendering.

    Parameters
    ----------
    points : Vect3Array, optional
        Three-dimensional coordinates of the dots. Defaults to NULL_POINTS.
    color : ManimColor, optional
        Color assigned to the dots. Defaults to YELLOW.
    radius : float, optional
        Radius assigned to every dot. Defaults to DEFAULT_GLOW_DOT_RADIUS.
    glow_factor : float, optional
        Glow intensity parameter passed to the DotCloud shader.
        Defaults to 2.0.
    **kwargs
        Additional keyword arguments forwarded to :class:`DotCloud`.

    Examples
    --------
    Create an empty collection of glowing dots:

        dots = GlowDots()

    Create glowing dots at specified positions:

        points = np.array([
            [-1.0, 0.0, 0.0],
            [ 0.0, 1.0, 0.0],
            [ 1.0, 0.0, 0.0],
        ])

        dots = GlowDots(points)

    Customize the color and glow intensity:

        dots = GlowDots(
            points,
            color=BLUE,
            glow_factor=1.5,
        )

    Adjust the radius:

        dots = GlowDots(
            points,
            radius=0.08,
            glow_factor=2.5,
        )

    Notes
    -----
    - GlowDots does not implement a separate rendering system; it relies on
      DotCloud's shader and point-data representation.
    - The default glow factor is 2.0, but the visual result depends on the
      shader implementation and rendering configuration.
    - Additional options supported by DotCloud, such as ``opacity`` and
      ``anti_alias_width``, can be supplied through ``kwargs``.
    - The constructor does not explicitly expose an ``opacity`` parameter;
      if provided, it is forwarded to DotCloud through ``kwargs``.
    """

    def __init__(
        self,
        points: Vect3Array = NULL_POINTS,
        color: ManimColor = YELLOW,
        radius: float = DEFAULT_GLOW_DOT_RADIUS,
        glow_factor: float = 2.0,
        **kwargs,
    ):
        super().__init__(
            points,
            color=color,
            radius=radius,
            glow_factor=glow_factor,
            **kwargs,
        )


class GlowDot(GlowDots):
    """
    A single glowing dot positioned at a specified three-dimensional center.

    `GlowDot` inherits from :class:`GlowDots` and initializes the parent with
    a NumPy array containing exactly one point. It provides a convenient way
    to create an individual glowing dot while retaining GlowDots' default
    color, radius, and glow settings.

    Parameters
    ----------
    center : Vect3, optional
        Three-dimensional coordinates of the dot's center. Defaults to ORIGIN.
    **kwargs
        Additional keyword arguments forwarded to :class:`GlowDots`, such as
        ``color``, ``radius``, ``glow_factor``, ``opacity``, and
        ``anti_alias_width``.

    Examples
    --------
    Create a glowing dot at the origin:

        dot = GlowDot()

    Position it at a specific location:

        dot = GlowDot(np.array([1.0, 2.0, 0.0]))

    Customize its appearance:

        dot = GlowDot(
            center=np.array([1.0, 0.0, 0.0]),
            color=BLUE,
            radius=0.08,
            glow_factor=2.5,
        )

    Create a glowing dot with reduced glow intensity:

        dot = GlowDot(glow_factor=0.5)

    Notes
    -----
    - The center is wrapped in a one-element NumPy array and passed to
      GlowDots through the ``points`` argument.
    - The resulting object contains one point and uses the rendering
      behavior inherited from DotCloud through GlowDots.
    - The dot's position is determined by its center coordinates, while
      its size and glow are controlled by the inherited radius and
      glow-factor settings.
    - Unless overridden through ``kwargs``, GlowDots supplies its own
      defaults for color, radius, and glow factor.
    """

    def __init__(self, center: Vect3 = ORIGIN, **kwargs):
        super().__init__(points=np.array([center]), **kwargs)
