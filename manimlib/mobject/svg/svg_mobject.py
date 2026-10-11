from __future__ import annotations

from xml.etree import ElementTree as ET

import numpy as np
import svgelements as se
import io
from pathlib import Path

from manimlib.constants import RIGHT
from manimlib.constants import TAU
from manimlib.logger import log
from manimlib.mobject.geometry import Circle
from manimlib.mobject.geometry import Line
from manimlib.mobject.geometry import Polygon
from manimlib.mobject.geometry import Polyline
from manimlib.mobject.geometry import Rectangle
from manimlib.mobject.geometry import RoundedRectangle
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.bezier import quadratic_bezier_points_for_arc
from manimlib.utils.images import get_full_vector_image_path
from manimlib.utils.iterables import hash_obj
from manimlib.utils.space_ops import rotation_about_z

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manimlib.typing import ManimColor, Vect3Array


# A stroke_width of 100 spans one unit of a default scale frame, see
# STROKE_WIDTH_CONVERSION in shaders/stroke.wgsl
STROKE_WIDTHS_PER_UNIT: float = 100.0

SVG_HASH_TO_MOB_MAP: dict[int, list[VMobject]] = {}
PATH_TO_POINTS: dict[str, Vect3Array] = {}


def get_svg_content_height(svg_string: str) -> float:
    # Strip root attributes to match SVGMobject.modify_xml_tree,
    # which avoids viewBox unit conversions (e.g. pt to px for dvisvgm)
    root = ET.fromstring(svg_string)
    root.attrib.clear()
    data_stream = io.BytesIO()
    ET.ElementTree(root).write(data_stream)
    data_stream.seek(0)
    svg = se.SVG.parse(data_stream)
    bbox = svg.bbox()
    if bbox is None:
        raise ValueError("SVG has no content to measure")
    return bbox[3] - bbox[1]


def _convert_point_to_3d(x: float, y: float) -> np.ndarray:
    return np.array([x, y, 0.0])


class SVGMobject(VMobject):
    """
    Convert an SVG (Scalable Vector Graphics) document into a hierarchy of
    Manim :class:`VMobject` objects.

    ``SVGMobject`` reads SVG markup from a string or file, parses its XML
    structure, converts supported SVG geometry into Manim vector objects,
    preserves applicable SVG styling and transformations, and combines the
    resulting objects into a single :class:`VMobject`-based group.

    It is designed to make vector artwork created in external graphics
    applications usable inside Manim scenes. The resulting object can be
    positioned, scaled, recolored, animated, and manipulated using the usual
    Manim mobject methods.

    The class supports SVG paths, straight lines, rectangles, circles,
    ellipses, polygons, and polylines. SVG groups and ``<use>`` elements are
    not directly converted into separate mobjects by ``mobjects_from_svg``;
    however, referenced path geometry can be resolved when processing paths.

    SVG text conversion is not implemented in this class: ``text_to_mobject``
    is currently a placeholder.

    Class Attributes
    ----------------
    file_name : str
        Default SVG filename used when the constructor receives neither a
        nonempty ``svg_string`` nor a nonempty ``file_name`` argument.
        The default is an empty string.
    height : float or None
        Default target height for the resulting object. The class default is
        ``2.0``. A constructor-level ``height`` overrides it when truthy.
    width : float or None
        Default target width for the resulting object. The class default is
        ``None``, meaning no width-based resizing is requested unless a width
        is supplied explicitly.

    Parameters
    ----------
    file_name : str, optional
        Name or path identifier of an SVG file to load. The file is resolved
        using ``get_full_vector_image_path``. Defaults to an empty string.
    svg_string : str, optional
        SVG XML markup supplied directly as a string. When nonempty, this
        takes precedence over both the constructor's ``file_name`` and the
        class-level ``self.file_name``.
    should_center : bool, optional
        Whether to center the imported geometry around the origin before
        applying the requested height and width. Defaults to ``True``.
    height : float or None, optional
        Target height of the resulting mobject. If the argument is falsy,
        ``self.height`` is used instead. With the default class configuration,
        the object is resized to a height of 2.0.
    width : float or None, optional
        Target width of the resulting mobject. If the argument is falsy,
        ``self.width`` is used instead. If the effective width is ``None``,
        width-based resizing is skipped.
    color : ManimColor, optional
        General color override applied to both fill and stroke after SVG
        geometry has been imported and resized. The implementation uses
        ``color or fill_color`` for the fill override and
        ``color or stroke_color`` for the stroke override. Consequently, a
        truthy ``color`` takes precedence over the corresponding specific
        color argument.
    fill_color : ManimColor, optional
        Fill color override applied after SVG import. If ``color`` is truthy,
        ``color`` takes precedence over this argument.
    fill_opacity : float or None, optional
        Fill opacity override applied after SVG import. ``None`` leaves the
        corresponding style value unchanged by this final style operation.
    stroke_width : float or None, optional
        Stroke-width override applied after SVG import and geometric resizing.
    stroke_color : ManimColor, optional
        Stroke color override applied after SVG import. If ``color`` is truthy,
        ``color`` takes precedence over this argument.
    stroke_opacity : float or None, optional
        Stroke opacity override applied after SVG import.
    svg_default : dict, optional
        Dictionary specifying fallback/default styling for SVG elements when
        their own styling does not provide a value. The default dictionary
        contains the keys ``color``, ``opacity``, ``fill_color``,
        ``fill_opacity``, ``stroke_width``, ``stroke_color``, and
        ``stroke_opacity``, all initialized to ``None``.

        The dictionary is copied during initialization. Its values are
        converted into SVG style attributes by ``generate_config_style_dict``.
        Only values represented by that method's conversion mapping are
        applied. In particular, the mapping uses ``color`` and ``fill_color``
        for SVG fill, ``color`` and ``stroke_color`` for SVG stroke, and
        ``opacity`` for both fill and stroke opacity.
    path_string_config : dict, optional
        Configuration forwarded to :class:`VMobjectFromSVGPath` when SVG paths
        are converted into Manim vector objects. The dictionary is copied
        during initialization.
    **kwargs
        Additional keyword arguments passed to ``VMobject.__init__`` through
        ``super().__init__``.

    Attributes
    ----------
    svg_string : str
        The SVG markup used to construct the mobject.
    svg_default : dict
        A copy of the configured default SVG styling dictionary.
    path_string_config : dict
        A copy of the path-conversion configuration dictionary.
    submobjects : list[VMobject]
        The converted SVG elements contained in the mobject hierarchy.

    Initialization Process
    ----------------------
    The constructor performs the following operations:

    1. Selects the SVG source. A nonempty ``svg_string`` has the highest
       priority, followed by the constructor's ``file_name``, followed by
       the class or instance attribute ``self.file_name``. If all three are
       empty, an exception is raised.
    2. Copies ``svg_default`` and ``path_string_config`` so that the
       instance stores its own dictionaries.
    3. Initializes the parent ``VMobject``.
    4. Parses and converts the SVG through ``init_svg_mobject``.
    5. Calls ``ensure_positive_orientation`` to normalize the orientation
       according to Manim's implementation.
    6. Determines the effective target height and width, records the current
       height, and optionally centers the object.
    7. Resizes the object to the requested height and/or width.
    8. Adjusts stroke widths to account for the geometry's resizing.
    9. Applies the final fill and stroke overrides using ``set_style``.

    The final style overrides are deliberately applied after resizing so that
    a requested stroke width is not unintentionally scaled by the resizing
    operation.

    Source Selection and Caching
    ----------------------------
    The SVG geometry is initialized by ``init_svg_mobject``. Before parsing
    the document, the method calculates a hash from ``hash_seed``.

    The ``hash_seed`` property returns a tuple containing:
        - The class name.
        - The ``svg_default`` dictionary.
        - The ``path_string_config`` dictionary.
        - The SVG markup itself.

    The resulting hash is used as a key in ``SVG_HASH_TO_MOB_MAP``. If a
    matching entry exists, the stored submobjects are copied and reused.
    Otherwise, the SVG markup is parsed and converted, and copies of the
    resulting submobjects are stored in the cache.

    Copying cached submobjects avoids reusing the same mutable mobject
    instances across different ``SVGMobject`` instances.

    After obtaining the submobjects, ``init_svg_mobject`` adds them to the
    object and calls ``flip(RIGHT)`` to reverse the SVG's vertical orientation
    relative to Manim's coordinate system.

    Important: the cache key includes the SVG source and the two configuration
    dictionaries, but not the requested height, width, centering, or final
    style overrides. Those operations are performed after cached geometry is
    retrieved.

    SVG Parsing Pipeline
    --------------------
    The method ``mobjects_from_svg_string`` implements the main parsing
    pipeline:

    1. Parses the XML string into an ``xml.etree.ElementTree``.
    2. Calls ``modify_xml_tree`` to prepare the XML for SVG parsing.
    3. Serializes the modified XML into an in-memory byte stream.
    4. Parses the byte stream with ``svgelements.SVG.parse``.
    5. Calls ``mobjects_from_svg`` to convert supported elements into Manim
       mobjects.

    Malformed XML or SVG content that the underlying parser cannot process
    may raise an exception.

    XML Style Modification
    ----------------------
    ``modify_xml_tree`` creates a new SVG root element and wraps the original
    SVG content in two groups:

    - A configuration-style group containing default style attributes.
    - A root-style group containing selected style attributes from the original
      SVG root.

    The style attributes copied from the original root are:
    ``fill``, ``fill-opacity``, ``stroke``, ``stroke-opacity``,
    ``stroke-width``, and ``style``.

    The method uses ``generate_config_style_dict`` to construct the default
    style attributes. These defaults are represented as SVG group attributes,
    allowing styles specified on individual SVG elements to participate in
    normal SVG style inheritance.

    The method does not copy every original root attribute into the new root.
    Instead, the original root's children are placed inside the newly created
    style groups.

    Default Style Generation
    ------------------------
    ``generate_config_style_dict`` translates selected entries in
    ``self.svg_default`` into SVG presentation attributes:

    - ``fill`` uses ``color`` and ``fill_color``.
    - ``fill-opacity`` uses ``opacity`` and ``fill_opacity``.
    - ``stroke`` uses ``color`` and ``stroke_color``.
    - ``stroke-opacity`` uses ``opacity`` and ``stroke_opacity``.
    - ``stroke-width`` uses ``stroke_width``.

    For each SVG attribute, the method iterates through its associated
    configuration keys and assigns a value when that key is not ``None``.
    Because later keys overwrite earlier ones, ``fill_color`` takes precedence
    over ``color`` for fill, ``fill_opacity`` takes precedence over ``opacity``
    for fill opacity, ``stroke_color`` takes precedence over ``color`` for
    stroke, and ``stroke_opacity`` takes precedence over ``opacity`` for
    stroke opacity.

    The values are converted to strings because SVG presentation attributes
    are textual XML attributes.

    Supported SVG Elements
    ----------------------
    ``mobjects_from_svg`` iterates through the parsed SVG elements and
    dispatches supported element types to their conversion methods.

    Supported types include:

    - ``svgelements.Path``: converted by ``path_to_mobject`` into a
      ``VMobjectFromSVGPath``.
    - ``svgelements.SimpleLine``: converted by ``line_to_mobject`` into a
      Manim ``Line``.
    - ``svgelements.Rect``: converted by ``rect_to_mobject`` into a
      ``Rectangle`` or ``RoundedRectangle``.
    - ``svgelements.Circle`` and ``svgelements.Ellipse``: converted by
      ``ellipse_to_mobject`` into a Manim ``Circle`` whose dimensions are
      adjusted to match the parsed ellipse.
    - ``svgelements.Polygon``: converted by ``polygon_to_mobject`` into a
      Manim ``Polygon``.
    - ``svgelements.Polyline``: converted by ``polyline_to_mobject`` into a
      Manim ``Polyline``.

    ``svgelements.Group`` and ``svgelements.Use`` objects are skipped by
    the main element-dispatch loop. Elements whose exact type is
    ``svgelements.SVGElement`` are also skipped. Unsupported element types
    generate a warning and are ignored.

    The text conversion branch is commented out, so SVG text elements are
    not converted by this dispatch method.

    After conversion, objects without points are discarded. For parsed
    ``GraphicObject`` instances, the SVG fill and stroke properties are
    applied using ``apply_style_to_mobject``. For parsed ``Transformable``
    instances whose ``apply`` attribute is true, their transformation
    matrices are applied using ``handle_transform``.

    The resulting mobjects are returned in a list, which is then added to
    the parent ``SVGMobject``.

    Path Conversion
    ---------------
    ``path_to_mobject`` converts a parsed SVG path into a
    ``VMobjectFromSVGPath``.

    If the path's identifier exists in ``svg.objects``, the method retrieves
    the referenced path geometry and constructs the mobject from that
    geometry. If the current path contains a transform, the transform is
    applied manually to preserve the referenced geometry's precision and
    avoid unnecessarily duplicating entries in ``PATH_TO_POINTS``.

    Otherwise, the method directly constructs ``VMobjectFromSVGPath`` from
    the parsed path.

    The ``path_string_config`` dictionary is forwarded to the path mobject
    constructor in either case.

    Line Conversion
    ---------------
    ``line_to_mobject`` converts an SVG straight line into a Manim ``Line``.
    Its endpoints are converted from SVG coordinates into Manim's 3D
    coordinate representation by ``_convert_point_to_3d``.

    Rectangle Conversion
    --------------------
    ``rect_to_mobject`` converts an SVG rectangle according to its corner
    radius information.

    If either ``rx`` or ``ry`` equals zero, the method creates a standard
    ``Rectangle`` using the parsed width and height.

    Otherwise, it creates a ``RoundedRectangle`` using:
        - The SVG rectangle's width.
        - An initial height adjusted by ``rect.rx / rect.ry``.
        - ``rect.rx`` as the initial corner radius.

    The rounded rectangle is then stretched to the SVG rectangle's actual
    height. Finally, the object is shifted to the converted center point
    of the SVG rectangle.

    Ellipse and Circle Conversion
    -----------------------------
    ``ellipse_to_mobject`` constructs a Manim ``Circle`` using the parsed
    horizontal radius ``ellipse.rx``. It then stretches the circle vertically
    to a height of ``2 * ellipse.ry`` and shifts it to the parsed center.

    For a circular SVG element, the horizontal and vertical radii are equal,
    so the resulting geometry remains circular. For an elliptical element,
    the vertical stretch produces an ellipse-shaped mobject.

    Polygon and Polyline Conversion
    -------------------------------
    ``polygon_to_mobject`` converts each SVG polygon vertex into a Manim
    coordinate and passes the resulting points to ``Polygon``.

    ``polyline_to_mobject`` performs the same coordinate conversion for
    polyline vertices and constructs a Manim ``Polyline``.

    Transformation Handling
    -----------------------
    ``handle_transform`` converts a ``svgelements.Matrix`` into a 2D NumPy
    matrix and a 3D translation vector.

    The linear transformation is applied using ``mob.apply_matrix(mat)``,
    and the translation is applied afterward using ``mob.shift(vec)``.

    The method returns the transformed mobject, allowing the transformation
    operation to be used as part of a conversion pipeline.

    The special transform handling in ``path_to_mobject`` uses a point-wise
    transformation function instead. It applies the referenced path's
    linear transformation and translation directly to the stored points.

    Style Application
    -----------------
    ``apply_style_to_mobject`` applies the fill and stroke properties of a
    parsed SVG graphic object to a Manim mobject.

    The method determines whether a stroke is present by checking whether
    ``shape.stroke`` and its ``hexrgb`` value are not ``None``. When a valid
    stroke color exists, it uses the parsed stroke width, color, and opacity.
    Otherwise, it sets the stroke width to zero.

    This check is important because ``svgelements`` may report a default
    stroke width of ``1.0`` even when the SVG explicitly specifies
    ``stroke: none``.

    The fill color and opacity are obtained from ``shape.fill`` and applied
    to the mobject. The method returns the modified mobject.

    Stroke-Width Scaling
    --------------------
    ``scale_stroke_widths`` adjusts stroke widths throughout the mobject
    family after geometric resizing.

    Parameters
    ----------
    factor : float
        Multiplicative factor applied to each applicable stroke width.

    If ``factor`` equals ``1``, the method returns immediately. Otherwise,
    it traverses ``self.get_family()`` and skips mobjects whose ``data``
    array is empty. This avoids attempting to adjust stroke widths on group
    objects that contain no geometry of their own.

    For every remaining mobject, the method obtains its current stroke widths,
    multiplies them by ``factor``, and applies the result with
    ``recurse=False`` so that the operation is performed on the current
    family member rather than recursively repeating on its descendants.

    The constructor calculates the scaling factor from the final height
    divided by the initial height, multiplied by ``STROKE_WIDTHS_PER_UNIT``.
    This helps keep stroke thickness consistent with the resized SVG artwork.

    Methods
    -------
    scale_stroke_widths(factor)
        Adjust stroke widths across the mobject family by a multiplicative
        factor.
    init_svg_mobject()
        Retrieve cached geometry or parse the SVG, add its submobjects, and
        flip the vertical orientation.
    hash_seed
        Property returning the tuple used to generate the SVG geometry cache
        key.
    mobjects_from_svg_string(svg_string)
        Parse SVG XML markup and return converted Manim mobjects.
    file_name_to_svg_string(file_name)
        Read an SVG file resolved by ``get_full_vector_image_path`` and
        return its contents as a string.
    modify_xml_tree(element_tree)
        Wrap the SVG content in groups that provide configured default
        styling and selected original root styling.
    generate_config_style_dict()
        Convert supported ``svg_default`` entries into SVG presentation
        attributes.
    mobjects_from_svg(svg)
        Dispatch supported parsed SVG elements to their conversion methods.
    handle_transform(mob, matrix)
        Static method that applies a parsed SVG transformation matrix.
    apply_style_to_mobject(mob, shape)
        Static method that applies parsed fill and stroke styling.
    path_to_mobject(path, svg)
        Convert an SVG path to ``VMobjectFromSVGPath``, including handling
        referenced path geometry.
    line_to_mobject(line)
        Convert a straight SVG line to a Manim ``Line``.
    rect_to_mobject(rect)
        Convert an SVG rectangle to a Manim ``Rectangle`` or
        ``RoundedRectangle``.
    ellipse_to_mobject(ellipse)
        Convert an SVG circle or ellipse to a Manim ``Circle``-based shape.
    polygon_to_mobject(polygon)
        Convert an SVG polygon to a Manim ``Polygon``.
    polyline_to_mobject(polyline)
        Convert an SVG polyline to a Manim ``Polyline``.
    text_to_mobject(text)
        Placeholder for SVG text conversion. The method currently returns
        ``None`` implicitly because its body contains only ``pass``.

    Examples
    --------
    Load an SVG file by filename:

    >>> icon = SVGMobject("my_icon.svg")
    >>> icon.get_height()
    2.0

    The default target height is 2.0 unless overridden by the class or
    constructor configuration.

    Load SVG markup directly from a string:

    >>> svg = '''
    ... <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
    ...   <circle cx="50" cy="50" r="40" fill="red"/>
    ... </svg>
    ... '''
    >>> icon = SVGMobject(svg_string=svg)

    Set a custom height and center the imported object:

    >>> icon = SVGMobject(
    ...     "my_icon.svg",
    ...     height=3.0,
    ...     should_center=True,
    ... )

    Set a custom width and apply a fill override:

    >>> icon = SVGMobject(
    ...     "my_icon.svg",
    ...     width=4.0,
    ...     fill_color=BLUE,
    ... )

    Override both fill and stroke using a general color:

    >>> icon = SVGMobject(
    ...     "my_icon.svg",
    ...     color=YELLOW,
    ...     stroke_width=2.0,
    ... )

    Configure default SVG styling:

    >>> icon = SVGMobject(
    ...     "my_icon.svg",
    ...     svg_default={
    ...         "color": None,
    ...         "opacity": None,
    ...         "fill_color": BLUE,
    ...         "fill_opacity": 1.0,
    ...         "stroke_width": 1.0,
    ...         "stroke_color": WHITE,
    ...         "stroke_opacity": 1.0,
    ...     },
    ... )

    Customize path conversion:

    >>> icon = SVGMobject(
    ...     "my_icon.svg",
    ...     path_string_config={
    ...         # Add supported VMobjectFromSVGPath options here.
    ...     },
    ... )

    Use the SVG mobject in a scene:

    >>> icon = SVGMobject("my_icon.svg", height=2.5)
    >>> icon.shift(LEFT)
    >>> self.add(icon)
    >>> self.play(icon.animate.scale(1.2).shift(RIGHT))

    Inspect the parsed geometry:

    >>> icon = SVGMobject("my_icon.svg")
    >>> len(icon.submobjects)
    >>> icon.get_width(), icon.get_height()

    Notes on Parameter Behavior
    ---------------------------
    The constructor uses ``height = height or self.height`` and
    ``width = width or self.width``. Therefore, values such as ``0`` are
    treated as requests to use the class or instance defaults rather than
    as literal target dimensions.

    Centering occurs before height and width resizing. If ``should_center``
    is false, the original placement is retained before resizing; scaling
    may therefore preserve a placement relative to the origin that differs
    from the centered case.

    If both a target height and target width are provided, the height is
    applied first and the width second. These operations can change the
    aspect ratio because the second resize may stretch the object to the
    requested width independently of its height.

    The final color/style overrides are applied after the geometry and stroke
    widths have been processed. SVG-specific style values may therefore be
    overridden by the explicit constructor parameters.

    The method ``text_to_mobject`` is not a functioning text converter.
    SVG text support should not be assumed merely because the method exists.

    Raises
    ------
    Exception
        Raised explicitly if neither a nonempty SVG string nor a usable
        filename is available. File-reading, XML parsing, SVG parsing, and
        geometry-conversion errors may also propagate from the underlying
        functions and libraries.
    """

    file_name: str = ""
    height: float | None = 2.0
    width: float | None = None

    def __init__(
        self,
        file_name: str = "",
        svg_string: str = "",
        should_center: bool = True,
        height: float | None = None,
        width: float | None = None,
        # Style that overrides the original svg
        color: ManimColor = None,
        fill_color: ManimColor = None,
        fill_opacity: float | None = None,
        stroke_width: float | None = None,
        stroke_color: ManimColor = None,
        stroke_opacity: float | None = None,
        # Style that fills only when not specified
        # If None, regarded as default values from svg standard
        svg_default: dict = dict(
            color=None,
            opacity=None,
            fill_color=None,
            fill_opacity=None,
            stroke_width=None,
            stroke_color=None,
            stroke_opacity=None,
        ),
        path_string_config: dict = dict(),
        **kwargs
    ):
        if svg_string != "":
            self.svg_string = svg_string
        elif file_name != "":
            self.svg_string = self.file_name_to_svg_string(file_name)
        elif self.file_name != "":
            self.svg_string = self.file_name_to_svg_string(self.file_name)
        else:
            raise Exception("Must specify either a file_name or svg_string SVGMobject")

        self.svg_default = dict(svg_default)
        self.path_string_config = dict(path_string_config)

        super().__init__(**kwargs)
        self.init_svg_mobject()
        self.ensure_positive_orientation()

        # Initialize position
        height = height or self.height
        width = width or self.width

        initial_height = self.get_height()

        if should_center:
            self.center()
        if height is not None:
            self.set_height(height)
        if width is not None:
            self.set_width(width)

        # Widths read from the file are in the svg's own user units, while the geometry
        # above has just been resized to the requested height or width. Converting them
        # keeps a stroke the thickness it looks in the file, whatever units that file
        # happens to be drawn in.
        if initial_height > 0:
            units_per_user_unit = self.get_height() / initial_height
            self.scale_stroke_widths(STROKE_WIDTHS_PER_UNIT * units_per_user_unit)

        # Rather than passing style into super().__init__
        # do it after svg has been taken in. Left until last so that a width asked for
        # here is the width drawn, rather than something the resizing above has scaled.
        self.set_style(
            fill_color=color or fill_color,
            fill_opacity=fill_opacity,
            stroke_color=color or stroke_color,
            stroke_width=stroke_width,
            stroke_opacity=stroke_opacity,
        )

    def scale_stroke_widths(self, factor: float) -> None:
        if factor == 1:
            return
        for mob in self.get_family():
            # The group holding the shapes carries no points of its own, so no widths either
            if len(mob.data) == 0:
                continue
            mob.set_stroke(width=factor * mob.get_stroke_widths(), recurse=False)

    def init_svg_mobject(self) -> None:
        hash_val = hash_obj(self.hash_seed)
        if hash_val in SVG_HASH_TO_MOB_MAP:
            submobs = [sm.copy() for sm in SVG_HASH_TO_MOB_MAP[hash_val]]
        else:
            submobs = self.mobjects_from_svg_string(self.svg_string)
            SVG_HASH_TO_MOB_MAP[hash_val] = [sm.copy() for sm in submobs]

        self.add(*submobs)
        self.flip(RIGHT)  # Flip y

    @property
    def hash_seed(self) -> tuple:
        # Returns data which can uniquely represent the result of `init_points`.
        # The hashed value of it is stored as a key in `SVG_HASH_TO_MOB_MAP`.
        return (
            self.__class__.__name__,
            self.svg_default,
            self.path_string_config,
            self.svg_string
        )

    def mobjects_from_svg_string(self, svg_string: str) -> list[VMobject]:
        element_tree = ET.ElementTree(ET.fromstring(svg_string))
        new_tree = self.modify_xml_tree(element_tree)

        # New svg based on tree contents
        data_stream = io.BytesIO()
        new_tree.write(data_stream)
        data_stream.seek(0)
        svg = se.SVG.parse(data_stream)
        data_stream.close()

        return self.mobjects_from_svg(svg)

    def file_name_to_svg_string(self, file_name: str) -> str:
        return Path(get_full_vector_image_path(file_name)).read_text()

    def modify_xml_tree(self, element_tree: ET.ElementTree) -> ET.ElementTree:
        config_style_attrs = self.generate_config_style_dict()
        style_keys = (
            "fill",
            "fill-opacity",
            "stroke",
            "stroke-opacity",
            "stroke-width",
            "style"
        )
        root = element_tree.getroot()
        style_attrs = {
            k: v
            for k, v in root.attrib.items()
            if k in style_keys
        }

        # Ignore other attributes in case that svgelements cannot parse them
        SVG_XMLNS = "{http://www.w3.org/2000/svg}"
        new_root = ET.Element("svg")
        config_style_node = ET.SubElement(new_root, f"{SVG_XMLNS}g", config_style_attrs)
        root_style_node = ET.SubElement(config_style_node, f"{SVG_XMLNS}g", style_attrs)
        root_style_node.extend(root)
        return ET.ElementTree(new_root)

    def generate_config_style_dict(self) -> dict[str, str]:
        keys_converting_dict = {
            "fill": ("color", "fill_color"),
            "fill-opacity": ("opacity", "fill_opacity"),
            "stroke": ("color", "stroke_color"),
            "stroke-opacity": ("opacity", "stroke_opacity"),
            "stroke-width": ("stroke_width",)
        }
        svg_default_dict = self.svg_default
        result = {}
        for svg_key, style_keys in keys_converting_dict.items():
            for style_key in style_keys:
                if svg_default_dict[style_key] is None:
                    continue
                result[svg_key] = str(svg_default_dict[style_key])
        return result

    def mobjects_from_svg(self, svg: se.SVG) -> list[VMobject]:
        result = []
        for shape in svg.elements():
            if isinstance(shape, (se.Group, se.Use)):
                continue
            elif isinstance(shape, se.Path):
                mob = self.path_to_mobject(shape, svg)
            elif isinstance(shape, se.SimpleLine):
                mob = self.line_to_mobject(shape)
            elif isinstance(shape, se.Rect):
                mob = self.rect_to_mobject(shape)
            elif isinstance(shape, (se.Circle, se.Ellipse)):
                mob = self.ellipse_to_mobject(shape)
            elif isinstance(shape, se.Polygon):
                mob = self.polygon_to_mobject(shape)
            elif isinstance(shape, se.Polyline):
                mob = self.polyline_to_mobject(shape)
            # elif isinstance(shape, se.Text):
            #     mob = self.text_to_mobject(shape)
            elif type(shape) == se.SVGElement:
                continue
            else:
                log.warning("Unsupported element type: %s", type(shape))
                continue
            if not mob.has_points():
                continue
            if isinstance(shape, se.GraphicObject):
                self.apply_style_to_mobject(mob, shape)
            if isinstance(shape, se.Transformable) and shape.apply:
                self.handle_transform(mob, shape.transform)
            result.append(mob)
        return result

    @staticmethod
    def handle_transform(mob: VMobject, matrix: se.Matrix) -> VMobject:
        mat = np.array([
            [matrix.a, matrix.c],
            [matrix.b, matrix.d]
        ])
        vec = np.array([matrix.e, matrix.f, 0.0])
        mob.apply_matrix(mat)
        mob.shift(vec)
        return mob

    @staticmethod
    def apply_style_to_mobject(
        mob: VMobject,
        shape: se.GraphicObject
    ) -> VMobject:
        # svgelements hands back a stroke width of 1.0 even for a shape painted with
        # `stroke: none`, so the width is only taken when a stroke color came with it.
        # Otherwise it is zeroed, which is what an unstroked shape should draw as.
        has_stroke = shape.stroke is not None and shape.stroke.hexrgb is not None
        mob.set_style(
            stroke_width=shape.stroke_width if has_stroke else 0.0,
            stroke_color=shape.stroke.hexrgb if has_stroke else None,
            stroke_opacity=shape.stroke.opacity if has_stroke else None,
            fill_color=shape.fill.hexrgb,
            fill_opacity=shape.fill.opacity
        )
        return mob

    def path_to_mobject(self, path: se.Path, svg: se.SVG) -> VMobjectFromSVGPath:
        if path.id in svg.objects:
            # If this path reuses a referenced definition (<use>), build the mobject from
            # the original geometry.
            # We apply the transform ourselves so we (1) keep the full precision of the 
            # reference and (2) only store one entry in PATH_TO_POINTS.
            ref_path = svg.objects[path.id]
            mob = VMobjectFromSVGPath(ref_path, **self.path_string_config)
            if 'transform' in path.values:
                matrix = se.Matrix(path.values['transform'])
                rotation = np.array([[matrix.a, matrix.b],
                                     [matrix.c, matrix.d]])
                translation = np.array([[matrix.e, matrix.f]])
                mob.apply_points_function(
                    lambda points: np.concatenate([points[:, :2] @ rotation + translation,
                                                   points[:, [2]]],
                                                  axis=1),
                    about_point=None,
                    about_edge=None,
                    works_on_bounding_box=False)
            return mob
        else:
            return VMobjectFromSVGPath(path, **self.path_string_config)

    def line_to_mobject(self, line: se.SimpleLine) -> Line:
        return Line(
            start=_convert_point_to_3d(line.x1, line.y1),
            end=_convert_point_to_3d(line.x2, line.y2)
        )

    def rect_to_mobject(self, rect: se.Rect) -> Rectangle:
        if rect.rx == 0 or rect.ry == 0:
            mob = Rectangle(
                width=rect.width,
                height=rect.height,
            )
        else:
            mob = RoundedRectangle(
                width=rect.width,
                height=rect.height * rect.rx / rect.ry,
                corner_radius=rect.rx
            )
            mob.stretch_to_fit_height(rect.height)
        mob.shift(_convert_point_to_3d(
            rect.x + rect.width / 2,
            rect.y + rect.height / 2
        ))
        return mob

    def ellipse_to_mobject(self, ellipse: se.Circle | se.Ellipse) -> Circle:
        mob = Circle(radius=ellipse.rx)
        mob.stretch_to_fit_height(2 * ellipse.ry)
        mob.shift(_convert_point_to_3d(
            ellipse.cx, ellipse.cy
        ))
        return mob

    def polygon_to_mobject(self, polygon: se.Polygon) -> Polygon:
        points = [
            _convert_point_to_3d(*point)
            for point in polygon
        ]
        return Polygon(*points)

    def polyline_to_mobject(self, polyline: se.Polyline) -> Polyline:
        points = [
            _convert_point_to_3d(*point)
            for point in polyline
        ]
        return Polyline(*points)

    def text_to_mobject(self, text: se.Text):
        pass


class VMobjectFromSVGPath(VMobject):
    """
    Convert an SVG path into a Manim vector mobject by interpreting its path
    segments and constructing the corresponding Bézier curves and line paths.

    ``VMobjectFromSVGPath`` is a specialized subclass of :class:`VMobject`
    designed to convert a parsed ``svgelements.Path`` object into Manim's
    internal point representation. It processes the path's individual
    segments, translates their SVG coordinates into Manim coordinates, and
    builds the geometry using Manim's path-construction methods.

    The class supports the following SVG path segment types:
        - ``Move``: Begin a new subpath.
        - ``Close``: Close the current subpath.
        - ``Line``: Add a straight line segment.
        - ``QuadraticBezier``: Add a quadratic Bézier curve.
        - ``CubicBezier``: Add a cubic Bézier curve.
        - ``Arc``: Convert an elliptical SVG arc into a sequence of quadratic
          Bézier curve segments.

    To avoid repeatedly converting identical path strings, the class uses the
    module-level ``PATH_TO_POINTS`` cache. Once a path has been converted,
    its point data can be reused by subsequent instances with the same SVG
    path-data string.

    Parameters
    ----------
    path_obj : se.Path
        A parsed SVG path object containing the geometric segments to convert.
        Its ``d()`` method supplies the path-data string used for caching.
    **kwargs
        Additional keyword arguments passed to ``VMobject.__init__``.

    Attributes
    ----------
    path_obj : se.Path
        The original parsed SVG path object used to construct the geometry.
    transform_cache : tuple[se.Matrix, np.ndarray, np.ndarray] or None
        A cache containing the inverse transformation matrix, the associated
        2D rotation/linear transformation array, and the translation vector
        used while processing SVG arcs. Initialized to ``None`` and populated
        when the first arc requires transformation information.

    Initialization
    --------------
    The constructor initializes ``transform_cache`` to ``None``, stores the
    provided path object in ``self.path_obj``, and invokes the parent
    ``VMobject`` constructor.

    The parent initialization process calls ``init_points`` as part of
    constructing the mobject's geometry.

    Point Initialization and Caching
    --------------------------------
    ``init_points`` converts the SVG path into Manim points.

    The method obtains the path-data string using ``self.path_obj.d()`` and
    checks whether that string is present in ``PATH_TO_POINTS``.

    If the path string is not cached:
        1. ``handle_commands`` processes the SVG path segments.
        2. The generated point data is copied and stored in ``PATH_TO_POINTS``.

    If the path string is already cached, the saved points are passed to
    ``self.set_points`` instead of rebuilding the path.

    The cache stores point data rather than complete mobject instances.
    This allows different instances to reuse the geometric conversion while
    maintaining their own mobject objects.

    The cache key is the path-data string. It does not explicitly include
    the path's transformation metadata or other configuration. Consequently,
    the same path-data string may reuse the same cached points even when
    other path properties differ.

    Segment Processing
    ------------------
    ``handle_commands`` defines a mapping between supported SVG segment
    classes and the corresponding Manim path-building operations.

    The mapping is:

    - ``se.Move`` → ``start_new_path(end)``
    - ``se.Close`` → ``close_path()``
    - ``se.Line`` → ``add_line_to(end, allow_null_line=False)``
    - ``se.QuadraticBezier`` → ``add_quadratic_bezier_curve_to(control, end, allow_null_curve=False)``
    - ``se.CubicBezier`` → ``add_cubic_bezier_curve_to(control1, control2, end)``

    The method iterates over ``self.path_obj`` and checks each segment's
    exact class. Arc segments are handled separately by ``handle_arc``.
    All other segments are dispatched through the mapping.

    For the mapped segment types, the required coordinate attributes are
    read from each segment and converted to Manim's 3D coordinate format
    using ``_convert_point_to_3d`` before being passed to the selected
    function.

    After processing the segments, the method checks whether a new path has
    been started. If ``has_new_path_started()`` returns true, it removes the
    last two points using ``resize_points``. This handles a trailing
    ``Z M`` command pattern that would otherwise leave unwanted geometry
    points behind.

    Arc Conversion
    --------------
    ``handle_arc`` converts an SVG elliptical arc into Manim-compatible
    quadratic Bézier geometry while accounting for the path's SVG transform.

    SVG arcs can be represented by elliptical geometry, sweep angles,
    rotation, and coordinate transformations. Manim's path representation
    requires the arc to be approximated using its own curve primitives.
    This method performs that conversion in several stages.

    1. **Retrieve transformation data**

       If ``transform_cache`` already exists, the method reuses the cached
       inverse transformation, linear transformation array, and translation
       vector.

       Otherwise, it constructs an ``se.Matrix`` from the path's ``transform``
       attribute, defaulting to an empty transform string if that attribute
       is absent. It then builds the linear transformation matrix and
       translation vector and computes the inverse transformation.

       The resulting values are saved in ``transform_cache``.

    2. **Apply the inverse transformation**

       The SVG arc is multiplied by the inverse transformation matrix.
       This removes the combined effect of the path's transform while the
       arc's intermediate geometry is calculated.

       The code's comments explain that the matrix obtained from the path
       accounts for the combined effects of parent-group transformations in
       the SVG representation.

    3. **Determine the number of curve components**

       The number of quadratic Bézier components is calculated from the
       absolute sweep angle:

       ``n_components = ceil(8 * abs(arc.sweep) / TAU)``

       This makes the number of components proportional to the angular extent
       of the arc. A larger sweep generally requires more components.

    4. **Generate unit-circle arc points**

       ``quadratic_bezier_points_for_arc`` generates the control-point data
       needed to represent the arc on a unit circle. The resulting points are
       rotated according to the arc's starting parameter angle using
       ``rotation_about_z``.

    5. **Convert the unit-circle arc to elliptical geometry**

       The x-coordinates are scaled by ``arc.rx`` and the y-coordinates by
       ``arc.ry``. The points are then rotated by the arc's own ellipse
       rotation, obtained from ``arc.get_rotation().as_radians``.

       The arc's center is added to place the points at the correct location.

    6. **Apply the original transformation**

       The linear transformation is applied to the first two coordinates,
       followed by the translation vector. This transforms the computed
       points back into the coordinate system expected for the original SVG
       geometry.

    7. **Append the generated points**

       ``arc_points[1:]`` is passed to ``append_points``. The first point is
       omitted because it corresponds to the beginning of the arc, which is
       expected to connect to the geometry already present in the path.

    Transformation Cache
    --------------------
    The ``transform_cache`` attribute avoids recalculating the same
    transformation information for every arc in a path.

    When the first arc is processed, the method:
        - Creates an ``se.Matrix`` from the path's transform attribute.
        - Builds a 2D linear transformation array from the matrix entries.
        - Extracts the translation components into a 3D vector.
        - Inverts the transformation matrix.
        - Stores the inverse matrix, linear transformation array, and
          translation vector in ``self.transform_cache``.

    Subsequent arcs reuse these values.

    The cached matrix is the inverse matrix after ``transform.inverse()``
    has been called. The stored ``rot`` and ``shift`` arrays retain the
    linear transformation and translation values extracted before inversion.

    Methods
    -------
    init_points()
        Initialize the mobject's point data from the SVG path, reusing
        ``PATH_TO_POINTS`` when the path-data string has already been cached.
    handle_commands()
        Interpret the supported SVG path segments and construct the
        corresponding Manim paths and curves.
    handle_arc(arc)
        Convert an SVG elliptical arc into quadratic Bézier point data while
        accounting for the path's transformation.

    Raises
    ------
    KeyError
        May occur in ``handle_commands`` if a segment class other than
        ``se.Arc`` is not present in the segment-to-function mapping.
    AttributeError
        May occur if the supplied path or one of its segments lacks an
        expected attribute or method.
    ValueError or other numerical exceptions
        May propagate from transformation inversion or geometric operations
        if the SVG transformation is invalid or non-invertible.

    Notes
    -----
    This class depends on ``svgelements`` for SVG path parsing and on Manim's
    vector-mobject methods for constructing the final geometry.

    The class does not parse SVG markup itself. It expects an already-parsed
    ``se.Path`` object, which is why it is commonly used by higher-level SVG
    import classes.

    The class relies on several module-level names, including ``PATH_TO_POINTS``,
    ``_convert_point_to_3d``, ``quadratic_bezier_points_for_arc``,
    ``rotation_about_z``, and ``TAU``. These must be available in the module
    where the class is defined.

    Examples
    --------
    Create a path using ``svgelements`` and convert it:

    >>> import svgelements as se
    >>> path = se.Path("M 0,0 L 1,0 L 1,1")
    >>> mob = VMobjectFromSVGPath(path)

    Create a curved path:

    >>> path = se.Path("M 0,0 C 1,0 1,1 2,1")
    >>> mob = VMobjectFromSVGPath(path)

    Create a closed triangular path:

    >>> path = se.Path("M 0,0 L 1,0 L 0.5,1 Z")
    >>> mob = VMobjectFromSVGPath(path)

    Use the resulting mobject in a scene:

    >>> path = se.Path("M 0,0 L 1,0 L 1,1")
    >>> mob = VMobjectFromSVGPath(path)
    >>> self.add(mob)
    """

    def __init__(
        self,
        path_obj: se.Path,
        **kwargs
    ):
        # caches (transform.inverse(), rot, shift)
        self.transform_cache: tuple[se.Matrix, np.ndarray, np.ndarray] | None = None

        self.path_obj = path_obj
        super().__init__(**kwargs)

    def init_points(self) -> None:
        # After a given svg_path has been converted into points, the result
        # will be saved so that future calls for the same pathdon't need to
        # retrace the same computation.
        path_string = self.path_obj.d()
        if path_string not in PATH_TO_POINTS:
            self.handle_commands()
            # Save for future use
            PATH_TO_POINTS[path_string] = self.get_points().copy()
        else:
            points = PATH_TO_POINTS[path_string]
            self.set_points(points)

    def handle_commands(self) -> None:
        segment_class_to_func_map = {
            se.Move: (self.start_new_path, ("end",)),
            se.Close: (self.close_path, ()),
            se.Line: (lambda p: self.add_line_to(p, allow_null_line=False), ("end",)),
            se.QuadraticBezier: (lambda c, e: self.add_quadratic_bezier_curve_to(c, e, allow_null_curve=False), ("control", "end")),
            se.CubicBezier: (self.add_cubic_bezier_curve_to, ("control1", "control2", "end"))
        }
        for segment in self.path_obj:
            segment_class = segment.__class__
            if segment_class is se.Arc:
                self.handle_arc(segment)
            else:
                func, attr_names = segment_class_to_func_map[segment_class]
                points = [
                    _convert_point_to_3d(*segment.__getattribute__(attr_name))
                    for attr_name in attr_names
                ]
                func(*points)

        # Get rid of the side effect of trailing "Z M" commands.
        if self.has_new_path_started():
            self.resize_points(self.get_num_points() - 2)

    def handle_arc(self, arc: se.Arc) -> None:
        if self.transform_cache is not None:
            transform, rot, shift = self.transform_cache
        else:
            # The transform obtained in this way considers the combined effect
            # of all parent group transforms in the SVG.
            # Therefore, the arc can be transformed inversely using this transform
            # to correctly compute the arc path before transforming it back.
            transform = se.Matrix(self.path_obj.values.get('transform', ''))
            rot = np.array([
                [transform.a, transform.c],
                [transform.b, transform.d]
            ])
            shift = np.array([transform.e, transform.f, 0])
            transform.inverse()
            self.transform_cache = (transform, rot, shift)

        # Apply inverse transformation to the arc so that its path can be correctly computed
        arc *= transform

        # The value of n_components is chosen based on the implementation of VMobject.arc_to
        n_components = int(np.ceil(8 * abs(arc.sweep) / TAU))

        # Obtain the required angular segments on the unit circle
        arc_points = quadratic_bezier_points_for_arc(arc.sweep, n_components)
        arc_points @= np.array(rotation_about_z(arc.get_start_t())).T

        # Transform to an ellipse, considering rotation and translating the ellipse center
        arc_points[:, 0] *= arc.rx
        arc_points[:, 1] *= arc.ry
        arc_points @= np.array(rotation_about_z(arc.get_rotation().as_radians)).T
        arc_points += [*arc.center, 0]

        # Transform back
        arc_points[:, :2] @= rot.T
        arc_points += shift

        self.append_points(arc_points[1:])
