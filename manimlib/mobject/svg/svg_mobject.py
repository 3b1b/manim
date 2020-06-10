import itertools as it
import re
import string
import warnings
import os
import hashlib

from xml.dom import minidom

from manimlib.constants import DEFAULT_STROKE_WIDTH
from manimlib.constants import ORIGIN, UP, DOWN, LEFT, RIGHT
from manimlib.constants import BLACK
from manimlib.constants import WHITE
import manimlib.constants as consts

from manimlib.mobject.geometry import Circle
from manimlib.mobject.geometry import Rectangle
from manimlib.mobject.geometry import RoundedRectangle
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.color import *
from manimlib.utils.config_ops import digest_config


def string_to_numbers(num_string):
    num_string = num_string.replace("-", ",-")
    num_string = num_string.replace("e,-", "e-")
    return [
        float(s)
        for s in re.split("[ ,]", num_string)
        if s != ""
    ]


class SVGMobject(VMobject):
    CONFIG = {
        "should_center": True,
        "height": 2,
        "width": None,
        # Must be filled in in a subclass, or when called
        "file_name": None,
        "unpack_groups": True,  # if False, creates a hierarchy of VGroups
        # TODO, style components should be read in, not defaulted
        "stroke_width": DEFAULT_STROKE_WIDTH,
        "fill_opacity": 1.0,
    }

    def __init__(self, file_name=None, **kwargs):
        digest_config(self, kwargs)
        self.file_name = file_name or self.file_name
        self.ensure_valid_file()
        VMobject.__init__(self, **kwargs)
        self.move_into_position()

    def ensure_valid_file(self):
        file_name = self.file_name
        if file_name is None:
            raise Exception("Must specify file for SVGMobject")
        possible_paths = [
            os.path.join(os.path.join("assets", "svg_images"), file_name),
            os.path.join(os.path.join("assets", "svg_images"), file_name + ".svg"),
            os.path.join(os.path.join("assets", "svg_images"), file_name + ".xdv"),
            file_name,
        ]
        for path in possible_paths:
            if os.path.exists(path):
                self.file_path = path
                return
        raise IOError(f"No file matching {file_name} in image directory")

    def init_points(self):
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
        result = []
        if not isinstance(element, minidom.Element):
            return result
        if element.tagName == 'defs':
            self.update_ref_to_element(element)
        elif element.tagName == 'style':
            pass  # TODO, handle style
        elif element.tagName in ['g', 'svg', 'symbol']:
            result += it.chain(*[
                self.get_mobjects_from(child)
                for child in element.childNodes
            ])
        elif element.tagName == 'path':
            result.append(self.path_string_to_mobject(
                element.getAttribute('d')
            ))
        elif element.tagName == 'use':
            result += self.use_to_mobjects(element)
        elif element.tagName == 'rect':
            result.append(self.rect_to_mobject(element))
        elif element.tagName == 'circle':
            result.append(self.circle_to_mobject(element))
        elif element.tagName == 'ellipse':
            result.append(self.ellipse_to_mobject(element))
        elif element.tagName in ['polygon', 'polyline']:
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
        mob = VGroup(*self.get_mobjects_from(g_element))
        self.handle_transforms(g_element, mob)
        return mob.submobjects

    def path_string_to_mobject(self, path_string):
        return VMobjectFromSVGPathstring(path_string)

    def use_to_mobjects(self, use_element):
        # Remove initial "#" character
        ref = use_element.getAttribute("xlink:href")[1:]
        if ref not in self.ref_to_element:
            warnings.warn(f"{ref} not recognized")
            return VGroup()
        return self.get_mobjects_from(
            self.ref_to_element[ref]
        )

    def attribute_to_float(self, attr):
        stripped_attr = "".join([
            char for char in attr
            if char in string.digits + "." + "-"
        ])
        return float(stripped_attr)

    def polygon_to_mobject(self, polygon_element):
        path_string = polygon_element.getAttribute("points")
        for digit in string.digits:
            path_string = path_string.replace(f" {digit}", f"{digit} L")
        path_string = "M" + path_string
        return self.path_string_to_mobject(path_string)

    def circle_to_mobject(self, circle_element):
        x, y, r = [
            self.attribute_to_float(
                circle_element.getAttribute(key)
            )
            if circle_element.hasAttribute(key)
            else 0.0
            for key in ("cx", "cy", "r")
        ]
        return Circle(radius=r).shift(x * RIGHT + y * DOWN)

    def ellipse_to_mobject(self, circle_element):
        x, y, rx, ry = [
            self.attribute_to_float(
                circle_element.getAttribute(key)
            )
            if circle_element.hasAttribute(key)
            else 0.0
            for key in ("cx", "cy", "rx", "ry")
        ]
        return Circle().scale(rx * RIGHT + ry * UP).shift(x * RIGHT + y * DOWN)

    def rect_to_mobject(self, rect_element):
        fill_color = rect_element.getAttribute("fill")
        stroke_color = rect_element.getAttribute("stroke")
        stroke_width = rect_element.getAttribute("stroke-width")
        corner_radius = rect_element.getAttribute("rx")

        # input preprocessing
        if fill_color in ["", "none", "#FFF", "#FFFFFF"] or Color(fill_color) == Color(WHITE):
            opacity = 0
            fill_color = BLACK  # shdn't be necessary but avoids error msgs
        if fill_color in ["#000", "#000000"]:
            fill_color = WHITE
        if stroke_color in ["", "none", "#FFF", "#FFFFFF"] or Color(stroke_color) == Color(WHITE):
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
                width=self.attribute_to_float(
                    rect_element.getAttribute("width")
                ),
                height=self.attribute_to_float(
                    rect_element.getAttribute("height")
                ),
                stroke_width=stroke_width,
                stroke_color=stroke_color,
                fill_color=fill_color,
                fill_opacity=opacity
            )
        else:
            mob = RoundedRectangle(
                width=self.attribute_to_float(
                    rect_element.getAttribute("width")
                ),
                height=self.attribute_to_float(
                    rect_element.getAttribute("height")
                ),
                stroke_width=stroke_width,
                stroke_color=stroke_color,
                fill_color=fill_color,
                fill_opacity=opacity,
                corner_radius=corner_radius
            )

        mob.shift(mob.get_center() - mob.get_corner(UP + LEFT))
        return mob

    def handle_transforms(self, element, mobject):
        # TODO, this could use some cleaning...
        x, y = 0, 0
        try:
            x = self.attribute_to_float(element.getAttribute('x'))
            # Flip y
            y = -self.attribute_to_float(element.getAttribute('y'))
            mobject.shift([x, y, 0])
        except Exception:
            pass

        transform = element.getAttribute('transform')

        try:  # transform matrix
            prefix = "matrix("
            suffix = ")"
            if not transform.startswith(prefix) or not transform.endswith(suffix):
                raise Exception()
            transform = transform[len(prefix):-len(suffix)]
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
            transform = transform[len(prefix):-len(suffix)]
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
            transform = transform[len(prefix):-len(suffix)]
            x, y = string_to_numbers(transform)
            mobject.shift(x * RIGHT + y * DOWN)
        except:
            pass
        # TODO, ...

    def flatten(self, input_list):
        output_list = []
        for i in input_list:
            if isinstance(i, list):
                output_list.extend(self.flatten(i))
            else:
                output_list.append(i)
        return output_list

    def get_all_childNodes_have_id(self, element):
        all_childNodes_have_id = []
        if not isinstance(element, minidom.Element):
            return
        if element.hasAttribute('id'):
            return [element]
        for e in element.childNodes:
            all_childNodes_have_id.append(self.get_all_childNodes_have_id(e))
        return self.flatten([e for e in all_childNodes_have_id if e])

    def update_ref_to_element(self, defs):
        new_refs = dict([(e.getAttribute('id'), e) for e in self.get_all_childNodes_have_id(defs)])
        self.ref_to_element.update(new_refs)

    def move_into_position(self):
        if self.should_center:
            self.center()
        if self.height is not None:
            self.set_height(self.height)
        if self.width is not None:
            self.set_width(self.width)


class VMobjectFromSVGPathstring(VMobject):
    CONFIG = {
        "long_lines": True,
        "should_subdivide_sharp_curves": False,
    }

    def __init__(self, path_string, **kwargs):
        self.path_string = path_string
        super().__init__(**kwargs)

    def init_points(self):
        # TODO, move this caching operation
        # higher up to Mobject somehow.
        hasher = hashlib.sha256()
        hasher.update(self.path_string.encode())
        path_hash = hasher.hexdigest()[:16]

        filepath = os.path.join(
            consts.MOBJECT_POINTS_DIR,
            f"{path_hash}.npy"
        )

        if os.path.exists(filepath):
            self.points = np.load(filepath)
        else:
            self.relative_point = np.array(ORIGIN)
            for command, coord_string in self.get_commands_and_coord_strings():
                new_points = self.string_to_points(command, coord_string)
                self.handle_command(command, new_points)
            if self.should_subdivide_sharp_curves:
                # For a healthy triangulation later
                self.subdivide_sharp_curves()
            # SVG treats y-coordinate differently
            self.stretch(-1, 1, about_point=ORIGIN)
            # Get rid of any null curves
            self.points = self.get_points_without_null_curves()
            # Save to a file for future use
            np.save(filepath, self.points)

    def get_commands_and_coord_strings(self):
        all_commands = list(self.get_command_to_function_map().keys())
        all_commands += [c.lower() for c in all_commands]
        pattern = "[{}]".format("".join(all_commands))
        return zip(
            re.findall(pattern, self.path_string),
            re.split(pattern, self.path_string)[1:]
        )

    def handle_command(self, command, new_points):
        if command.islower():
            # Treat it as a relative command
            new_points += self.relative_point

        func, n_points = self.command_to_function(command)
        func(*new_points[:n_points])
        leftover_points = new_points[n_points:]

        # Recursively handle the rest of the points
        if len(leftover_points) > 0:
            if command.upper() == "M":
                # Treat following points as relative line coordinates
                command = "l"
            if command.islower():
                leftover_points -= self.relative_point
                self.relative_point = self.points[-1]
            self.handle_command(command, leftover_points)
        else:
            # Command is over, reset for future relative commands
            self.relative_point = self.points[-1]

    def string_to_points(self, command, coord_string):
        numbers = string_to_numbers(coord_string)
        if command.upper() in ["H", "V"]:
            i = {"H": 0, "V": 1}[command.upper()]
            xy = np.zeros((len(numbers), 2))
            xy[:, i] = numbers
            if command.isupper():
                xy[:, 1 - i] = self.relative_point[1 - i]
        elif command.upper() == "A":
            raise Exception("Not implemented")
        else:
            xy = np.array(numbers).reshape((len(numbers) // 2, 2))
        result = np.zeros((xy.shape[0], self.dim))
        result[:, :2] = xy
        return result

    def command_to_function(self, command):
        return self.get_command_to_function_map()[command.upper()]

    def get_command_to_function_map(self):
        """
        Associates svg command to VMobject function, and
        the number of arguments it takes in
        """
        return {
            "M": (self.start_new_path, 1),
            "L": (self.add_line_to, 1),
            "H": (self.add_line_to, 1),
            "V": (self.add_line_to, 1),
            "C": (self.add_cubic_bezier_curve_to, 3),
            "S": (self.add_smooth_cubic_curve_to, 2),
            "Q": (self.add_quadratic_bezier_curve_to, 2),
            "T": (self.add_smooth_curve_to, 1),
            "A": (self.add_quadratic_bezier_curve_to, 2),  # TODO
            "Z": (self.close_path, 0),
        }

    def get_original_path_string(self):
        return self.path_string
