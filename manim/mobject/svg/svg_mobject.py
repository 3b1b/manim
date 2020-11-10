"""Mobjects generated from an SVG file."""


__all__ = ["SVGMobject", "VMobjectFromSVGPathstring", "string_to_numbers"]


import itertools as it
import re
import os
import string
import warnings

from xml.dom import minidom

from ... import config
from ...constants import *
from ...mobject.geometry import Circle
from ...mobject.geometry import Rectangle
from ...mobject.geometry import RoundedRectangle
from ...mobject.types.vectorized_mobject import VGroup
from ...mobject.types.vectorized_mobject import VMobject
from ...utils.color import *
from ...utils.config_ops import digest_config
from ...utils.config_ops import digest_locals


def string_to_numbers(num_string):
    num_string = num_string.replace("-", ",-")
    num_string = num_string.replace("e,-", "e-")
    return [float(s) for s in re.split("[ ,]", num_string) if s != ""]


class SVGMobject(VMobject):
    """A SVGMobject is a Vector Mobject constructed from an SVG (or XDV) file.

    SVGMobjects are constructed from the XML data within the SVG file
    structure. As such, subcomponents from the XML data can be accessed via
    the submobjects attribute. There is varying amounts of support for SVG
    elements, experiment with SVG files at your own peril.

    Examples
    --------

    .. code-block:: python

        class Sample(Scene):
            def construct(self):
                self.play(
                    FadeIn(SVGMobject("manim-logo-sidebar.svg"))
                )

    Parameters
    --------
    file_name : :class:`str`
        The file's path name. When possible, the full path is preferred but a
        relative path may be used as well. Relative paths are relative to the
        directory specified by the `--assets_dir` command line argument.

    Other Parameters
    --------
    should_center : :class:`bool`
        Whether the SVGMobject should be centered to the origin. Defaults to `True`.
    height : :class:`float`
        Specify the final height of the SVG file. Defaults to 2 units.
    width : :class:`float`
        Specify the width the SVG file should occupy. Defaults to `None`.
    unpack_groups : :class:`bool`
        Whether the hierarchies of VGroups generated should be flattened. Defaults to `True`.
    stroke_width : :class:`float`
        The stroke width of the outer edge of an SVG path element. Defaults to `4`.
    fill_opacity : :class:`float`
        Specifies the opacity of the image. `1` is opaque, `0` is transparent. Defaults to `1`.
    """

    CONFIG = {
        "should_center": True,
        "height": 2,
        "width": None,
        # Must be filled in in a subclass, or when called
        "file_name": None,
        "unpack_groups": True,  # if False, creates a hierarchy of VGroups
        "stroke_width": DEFAULT_STROKE_WIDTH,
        "fill_opacity": 1.0,
        # "fill_color" : LIGHT_GREY,
    }

    def __init__(self, file_name=None, **kwargs):
        digest_config(self, kwargs)
        self.file_name = file_name or self.file_name
        self.ensure_valid_file()
        VMobject.__init__(self, **kwargs)
        self.move_into_position()

    def ensure_valid_file(self):
        """Reads self.file_name and determines whether the given input file_name
        is valid.
        """
        if self.file_name is None:
            raise Exception("Must specify file for SVGMobject")

        if os.path.exists(self.file_name):
            self.file_path = self.file_name
            return

        relative = os.path.join(os.getcwd(), self.file_name)
        if os.path.exists(relative):
            self.file_path = relative
            return

        possible_paths = [
            os.path.join(config.get_dir("assets_dir"), self.file_name),
            os.path.join(config.get_dir("assets_dir"), self.file_name + ".svg"),
            os.path.join(config.get_dir("assets_dir"), self.file_name + ".xdv"),
            self.file_name,
            self.file_name + ".svg",
            self.file_name + ".xdv",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                self.file_path = path
                return
        error = "From: {}, could not find {} at either of these locations: {}".format(
            os.getcwd(), self.file_name, possible_paths
        )
        raise IOError(error)

    def generate_points(self):
        """Called by the Mobject abstract base class. Responsible for generating
        the SVGMobject's points from XML tags, populating self.mobjects, and
        any submobjects within self.mobjects.
        """
        doc = minidom.parse(self.file_path)
        self.ref_to_element = {}
        for svg in doc.getElementsByTagName("svg"):
            mobjects = self.get_mobjects_from(svg)
            if self.unpack_groups:
                self.add(*mobjects)
            else:
                self.add(*mobjects[0].submobjects)
        doc.unlink()

    def get_mobjects_from(self, element):
        """Parses a given SVG element into a Mobject.

        Parameters
        ----------
        element : :class:`str`
            The SVG data in the XML to be parsed.

        Returns
        -------
        VMobject
            A VMobject representing the associated SVG element.
        """
        result = []
        if not isinstance(element, minidom.Element):
            return result
        if element.tagName == "defs":
            self.update_ref_to_element(element)
        elif element.tagName == "style":
            pass  # TODO, handle style
        elif element.tagName in ["g", "svg", "symbol"]:
            result += it.chain(
                *[self.get_mobjects_from(child) for child in element.childNodes]
            )
        elif element.tagName == "path":
            temp = element.getAttribute("d")
            if temp != "":
                result.append(self.path_string_to_mobject(temp))
        elif element.tagName == "use":
            result += self.use_to_mobjects(element)
        elif element.tagName == "rect":
            result.append(self.rect_to_mobject(element))
        elif element.tagName == "circle":
            result.append(self.circle_to_mobject(element))
        elif element.tagName == "ellipse":
            result.append(self.ellipse_to_mobject(element))
        elif element.tagName in ["polygon", "polyline"]:
            result.append(self.polygon_to_mobject(element))
        else:
            pass  # TODO
            # warnings.warn("Unknown element type: " + element.tagName)
        result = [m for m in result if m is not None]
        self.handle_transforms(element, VGroup(*result))
        if len(result) > 1 and not self.unpack_groups:
            result = [VGroup(*result)]

        return result

    def g_to_mobjects(self, g_element):
        """Converts the ``g`` SVG element into VMobjects.

        Parameters
        ----------
        g_element : :class:`str`
            A ``g`` element is a group of other SVG elements. As such a ``g`` element is equivalent to a VGroup.

        Returns
        -------
        List[VMobject]
            A list of VMobject reprsented by the group.
        """
        mob = VGroup(*self.get_mobjects_from(g_element))
        self.handle_transforms(g_element, mob)
        return mob.submobjects

    def path_string_to_mobject(self, path_string):
        """Converts a SVG path element's ``d`` attribute to a mobject.

        Parameters
        ----------
        path_string : str
            A path with potentially multiple path commands to create a shape.

        Returns
        -------
        VMobjectFromSVGPathstring
            A VMobject from the given path string, or d attribute.
        """
        return VMobjectFromSVGPathstring(path_string)

    def use_to_mobjects(self, use_element):
        """Converts a SVG <use> element to VMobject.

        Parameters
        ----------
        use_element : str
            An SVG <use> element which represents nodes that should be
            duplicated elsewhere.

        Returns
        -------
        VMobject
            A VMobject
        """
        # Remove initial "#" character
        ref = use_element.getAttribute("xlink:href")[1:]
        if ref not in self.ref_to_element:
            warnings.warn("%s not recognized" % ref)
            return VGroup()
        return self.get_mobjects_from(self.ref_to_element[ref])

    def attribute_to_float(self, attr):
        """A helper method which converts the attribute to float.

        Parameters
        ----------
        attr : str
            An SVG path attribute.

        Returns
        -------
        float
            A float representing the attribute string value.
        """
        stripped_attr = "".join(
            [char for char in attr if char in string.digits + "." + "-"]
        )
        return float(stripped_attr)

    def polygon_to_mobject(self, polygon_element):
        """Constructs a VMobject from a SVG <polygon> element.

        Parameters
        ----------
        polygon_element : str
            An SVG polygon element.

        Returns
        -------
        VMobjectFromSVGPathstring
            A VMobject representing the polygon.
        """
        # TODO, This seems hacky... yes it is.
        path_string = polygon_element.getAttribute("points")
        for digit in string.digits:
            path_string = path_string.replace(" " + digit, " L" + digit)
        path_string = "M" + path_string
        return self.path_string_to_mobject(path_string)

    # <circle class="st1" cx="143.8" cy="268" r="22.6"/>

    def circle_to_mobject(self, circle_element):
        """Creates a Circle VMobject from a SVG <circle> command.

        Parameters
        ----------
        circle_element : str
            A SVG circle path command.

        Returns
        -------
        Circle
            A Circle VMobject
        """
        x, y, r = [
            self.attribute_to_float(circle_element.getAttribute(key))
            if circle_element.hasAttribute(key)
            else 0.0
            for key in ("cx", "cy", "r")
        ]
        return Circle(radius=r).shift(x * RIGHT + y * DOWN)

    def ellipse_to_mobject(self, circle_element):
        """Creates a stretched Circle VMobject from a SVG <circle> path
        command.

        Parameters
        ----------
        circle_element : str
            A SVG circle path command.

        Returns
        -------
        Circle
            A Circle VMobject
        """
        x, y, rx, ry = [
            self.attribute_to_float(circle_element.getAttribute(key))
            if circle_element.hasAttribute(key)
            else 0.0
            for key in ("cx", "cy", "rx", "ry")
        ]
        return Circle().scale(rx * RIGHT + ry * UP).shift(x * RIGHT + y * DOWN)

    def rect_to_mobject(self, rect_element):
        """Converts a SVG <rect> command to a VMobject.

        Parameters
        ----------
        rect_element : str
            A SVG rect path command.

        Returns
        -------
        Rectangle
            Creates either a Rectangle, or RoundRectangle, VMobject from a
            rect element.
        """
        fill_color = rect_element.getAttribute("fill")
        stroke_color = rect_element.getAttribute("stroke")
        stroke_width = rect_element.getAttribute("stroke-width")
        corner_radius = rect_element.getAttribute("rx")

        # input preprocessing
        if fill_color in ["", "none", "#FFF", "#FFFFFF"] or Color(fill_color) == Color(
            WHITE
        ):
            opacity = 0
            fill_color = BLACK  # shdn't be necessary but avoids error msgs
        if fill_color in ["#000", "#000000"]:
            fill_color = WHITE
        if stroke_color in ["", "none", "#FFF", "#FFFFFF"] or Color(
            stroke_color
        ) == Color(WHITE):
            stroke_width = 0
            stroke_color = BLACK
        if stroke_color in ["#000", "#000000"]:
            stroke_color = WHITE
        if stroke_width in ["", "none", "0"]:
            stroke_width = 0

        if corner_radius in ["", "0", "none"]:
            corner_radius = 0

        corner_radius = float(corner_radius)

        if corner_radius == 0:
            mob = Rectangle(
                width=self.attribute_to_float(rect_element.getAttribute("width")),
                height=self.attribute_to_float(rect_element.getAttribute("height")),
                stroke_width=stroke_width,
                stroke_color=stroke_color,
                fill_color=fill_color,
                fill_opacity=opacity,
            )
        else:
            mob = RoundedRectangle(
                width=self.attribute_to_float(rect_element.getAttribute("width")),
                height=self.attribute_to_float(rect_element.getAttribute("height")),
                stroke_width=stroke_width,
                stroke_color=stroke_color,
                fill_color=fill_color,
                fill_opacity=opacity,
                corner_radius=corner_radius,
            )

        mob.shift(mob.get_center() - mob.get_corner(UP + LEFT))
        return mob

    def handle_transforms(self, element, mobject):
        """Applies the SVG transform to the specified mobject. Tranforms include:
        ``rotate``, ``translate``, ``scale``, and ``skew``.

        Parameters
        ----------
        element : str
            The transform command to perform

        mobject : Mobject
            The Mobject to transform.
        """
        x, y = 0, 0
        try:
            x = self.attribute_to_float(element.getAttribute("x"))
            # Flip y
            y = -self.attribute_to_float(element.getAttribute("y"))
            mobject.shift(x * RIGHT + y * UP)
        except:
            pass

        transform = element.getAttribute("transform")

        try:  # transform matrix
            prefix = "matrix("
            suffix = ")"
            if not transform.startswith(prefix) or not transform.endswith(suffix):
                raise Exception()
            transform = transform[len(prefix) : -len(suffix)]
            transform = string_to_numbers(transform)
            transform = np.array(transform).reshape([3, 2])
            x = transform[2][0]
            y = -transform[2][1]
            matrix = np.identity(self.dim)
            matrix[:2, :2] = transform[:2, :]
            matrix[1] *= -1
            matrix[:, 1] *= -1

            for mob in mobject.family_members_with_points():
                mob.points = np.dot(mob.points, matrix)
            mobject.shift(x * RIGHT + y * UP)
        except:
            pass

        try:  # transform scale
            prefix = "scale("
            suffix = ")"
            if not transform.startswith(prefix) or not transform.endswith(suffix):
                raise Exception()
            transform = transform[len(prefix) : -len(suffix)]
            scale_values = string_to_numbers(transform)
            if len(scale_values) == 2:
                scale_x, scale_y = scale_values
                mobject.scale(np.array([scale_x, scale_y, 1]), about_point=ORIGIN)
            elif len(scale_values) == 1:
                scale = scale_values[0]
                mobject.scale(np.array([scale, scale, 1]), about_point=ORIGIN)
        except:
            pass

        try:  # transform translate
            prefix = "translate("
            suffix = ")"
            if not transform.startswith(prefix) or not transform.endswith(suffix):
                raise Exception()
            transform = transform[len(prefix) : -len(suffix)]
            x, y = string_to_numbers(transform)
            mobject.shift(x * RIGHT + y * DOWN)
        except:
            pass
        # TODO, ...

    def flatten(self, input_list):
        """A helper method to flatten the ``input_list`` into an 1D array."""
        output_list = []
        for i in input_list:
            if isinstance(i, list):
                output_list.extend(self.flatten(i))
            else:
                output_list.append(i)
        return output_list

    def get_all_childNodes_have_id(self, element):
        """Gets all child nodes containing the `id` attribute and returns
        them in a flattened list.

        Parameters
        --------
        element : :class:`str`
            An element from SVG XML data. Elements use a unique `id`.

        Returns
        -------
        List[DOM element]
            A flattened list of DOM elements containing the `id` attribute.
        """
        all_childNodes_have_id = []
        if not isinstance(element, minidom.Element):
            return
        if element.hasAttribute("id") and element.tagName not in ("g", "defs"):
            return [element]
        for e in element.childNodes:
            all_childNodes_have_id.append(self.get_all_childNodes_have_id(e))
        return self.flatten([e for e in all_childNodes_have_id if e])

    def update_ref_to_element(self, defs):
        """Updates the ``ref_to_element`` dictionary.
        Parameters
        --------
        defs : :class:`defs`
            The new defs
        """
        new_refs = dict(
            [(e.getAttribute("id"), e) for e in self.get_all_childNodes_have_id(defs)]
        )
        self.ref_to_element.update(new_refs)

    def move_into_position(self):
        """Uses the SVGMobject's config dictionary to set the Mobject's
        width, height, and/or center it. Use ``width``, ``height``, and
        ``should_center`` respectively to modify this.
        """
        if self.should_center:
            self.center()
        if self.height is not None:
            self.set_height(self.height)
        if self.width is not None:
            self.set_width(self.width)


class VMobjectFromSVGPathstring(VMobject):
    def __init__(self, path_string, **kwargs):
        digest_locals(self)
        VMobject.__init__(self, **kwargs)

    def get_path_commands(self):
        """Returns a list of possible path commands used within an SVG ``d``
        attribute.

        See: https://svgwg.org/svg2-draft/paths.html#DProperty for further
        details on what each path command does.

        Returns
        -------
        List[:class:`str`]
            The various upper and lower cased path commands.
        """
        result = [
            "M",  # moveto
            "L",  # lineto
            "H",  # horizontal lineto
            "V",  # vertical lineto
            "C",  # curveto
            "S",  # smooth curveto
            "Q",  # quadratic Bezier curve
            "T",  # smooth quadratic Bezier curveto
            "A",  # elliptical Arc
            "Z",  # closepath
        ]
        result += [s.lower() for s in result]
        return result

    def generate_points(self):
        """Generates points from a given an SVG ``d`` attribute."""
        pattern = "[%s]" % ("".join(self.get_path_commands()))
        pairs = list(
            zip(
                re.findall(pattern, self.path_string),
                re.split(pattern, self.path_string)[1:],
            )
        )
        # Which mobject should new points be added to
        self = self
        for command, coord_string in pairs:
            self.handle_command(command, coord_string)
        # people treat y-coordinate differently
        self.rotate(np.pi, RIGHT, about_point=ORIGIN)

    def handle_command(self, command, coord_string):
        """Core logic for handling each of the various path commands."""
        isLower = command.islower()
        command = command.upper()
        # new_points are the points that will be added to the curr_points
        # list. This variable may get modified in the conditionals below.
        points = self.points
        new_points = self.string_to_points(coord_string)

        if isLower and len(points) > 0:
            new_points += points[-1]

        if command == "M":  # moveto
            self.start_new_path(new_points[0])
            if len(new_points) <= 1:
                return

            # Draw relative line-to values.
            points = self.points
            new_points = new_points[1:]
            command = "L"

            for p in new_points:
                if isLower:
                    # Treat everything as relative line-to until empty
                    p[0] += self.points[-1, 0]
                    p[1] += self.points[-1, 1]
                self.add_line_to(p)
            return

        elif command in ["L", "H", "V"]:  # lineto
            if command == "H":
                new_points[0, 1] = points[-1, 1]
            elif command == "V":
                if isLower:
                    new_points[0, 0] -= points[-1, 0]
                    new_points[0, 0] += points[-1, 1]
                new_points[0, 1] = new_points[0, 0]
                new_points[0, 0] = points[-1, 0]
            self.add_line_to(new_points[0])
            return

        if command == "C":  # curveto
            pass  # Yay! No action required
        elif command in ["S", "T"]:  # smooth curveto
            self.add_smooth_curve_to(*new_points)
            # handle1 = points[-1] + (points[-1] - points[-2])
            # new_points = np.append([handle1], new_points, axis=0)
            return
        elif command == "Q":  # quadratic Bezier curve
            # TODO, this is a suboptimal approximation
            new_points = np.append([new_points[0]], new_points, axis=0)
        elif command == "A":  # elliptical Arc
            raise NotImplementedError()
        elif command == "Z":  # closepath
            return

        # Add first three points
        self.add_cubic_bezier_curve_to(*new_points[0:3])

        # Handle situations where there's multiple relative control points
        if len(new_points) > 3:
            # Add subsequent offset points relatively.
            for i in range(3, len(new_points), 3):
                if isLower:
                    new_points[i : i + 3] -= points[-1]
                    new_points[i : i + 3] += new_points[i - 1]
                self.add_cubic_bezier_curve_to(*new_points[i : i + 3])

    def string_to_points(self, coord_string):
        """Since the SVG file's path command is provided as a string, this
        converts the coordinates into numbers.
        """
        numbers = string_to_numbers(coord_string)
        if len(numbers) % 2 == 1:
            numbers.append(0)
        num_points = len(numbers) // 2
        result = np.zeros((num_points, self.dim))
        result[:, :2] = np.array(numbers).reshape((num_points, 2))
        return result

    def get_original_path_string(self):
        """A simple getter for the path's ``d`` attribute."""
        return self.path_string
