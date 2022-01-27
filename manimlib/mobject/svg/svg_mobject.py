import itertools as it
import re
import string
import os
import hashlib

import cssselect2
from colour import web2hex
from xml.etree import ElementTree
from tinycss2 import serialize as css_serialize
from tinycss2 import parse_stylesheet, parse_declaration_list

from manimlib.constants import ORIGIN, UP, DOWN, LEFT, RIGHT, IN
from manimlib.constants import DEGREES, PI

from manimlib.mobject.geometry import Circle
from manimlib.mobject.geometry import Rectangle
from manimlib.mobject.geometry import RoundedRectangle
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.color import *
from manimlib.utils.config_ops import digest_config
from manimlib.utils.directories import get_mobject_data_dir
from manimlib.utils.images import get_full_vector_image_path
from manimlib.utils.simple_functions import clip
from manimlib.logger import log


DEFAULT_STYLE = {
    "fill": "black",
    "stroke": "none",
    "fill-opacity": "1",
    "stroke-opacity": "1",
    "stroke-width": 0,
}


def cascade_element_style(element, inherited):
    style = inherited.copy()

    for attr in DEFAULT_STYLE:
        if element.get(attr):
            style[attr] = element.get(attr)

    if element.get("style"):
        for style_spec in element.get("style").split(";"):
            style_spec = style_spec.strip()
            try:
                key, value = style_spec.split(":")
            except ValueError as e:
                if not style_spec.strip():
                    pass
                else:
                    raise e
            else:
                style[key.strip()] = value.strip()

    return style


def parse_color(color):
    color = color.strip()

    if color[0:3] == "rgb":
        splits = color[4:-1].strip().split(",")
        if splits[0].strip()[-1] == "%":
            parsed_rgbs = [float(i.strip()[:-1]) / 100.0 for i in splits]
        else:
            parsed_rgbs = [int(i) / 255.0 for i in splits]
        return rgb_to_hex(parsed_rgbs)

    else:
        return web2hex(color)


def fill_default_values(style, default_style):
    default = DEFAULT_STYLE.copy()
    default.update(default_style)
    for attr in default:
        if attr not in style:
            style[attr] = default[attr]


def parse_style(style, default_style):
    manim_style = {}
    fill_default_values(style, default_style)

    manim_style["fill_opacity"] = float(style["fill-opacity"])
    manim_style["stroke_opacity"] = float(style["stroke-opacity"])
    manim_style["stroke_width"] = float(style["stroke-width"])

    if style["fill"] == "none":
        manim_style["fill_opacity"] = 0
    else:
        manim_style["fill_color"] = parse_color(style["fill"])

    if style["stroke"] == "none":
        manim_style["stroke_width"] = 0
        if "fill_color" in manim_style:
            manim_style["stroke_color"] = manim_style["fill_color"]
    else:
        manim_style["stroke_color"] = parse_color(style["stroke"])

    return manim_style


class SVGMobject(VMobject):
    CONFIG = {
        "should_center": True,
        "height": 2,
        "width": None,
        # Must be filled in in a subclass, or when called
        "file_name": None,
        "unpack_groups": True,  # if False, creates a hierarchy of VGroups
        "stroke_width": 0.0,
        "fill_opacity": 1.0,
        "path_string_config": {}
    }

    def __init__(self, file_name=None, **kwargs):
        digest_config(self, kwargs)
        self.file_name = file_name or self.file_name
        if file_name is None:
            raise Exception("Must specify file for SVGMobject")
        self.file_path = get_full_vector_image_path(file_name)

        super().__init__(**kwargs)
        self.move_into_position()

    def move_into_position(self):
        if self.should_center:
            self.center()
        if self.height is not None:
            self.set_height(self.height)
        if self.width is not None:
            self.set_width(self.width)

    def init_colors(self, override=False):
        super().init_colors(override=override)

    def init_points(self):
        etree = ElementTree.parse(self.file_path)
        wrapper = cssselect2.ElementWrapper.from_xml_root(etree)
        svg = etree.getroot()
        namespace = svg.tag.split("}")[0][1:]
        self.ref_to_element = {}
        self.css_matcher = cssselect2.Matcher()

        for style in etree.findall(f"{{{namespace}}}style"):
            self.parse_css_style(style.text)

        mobjects = self.get_mobjects_from(wrapper, dict())
        if self.unpack_groups:
            self.add(*mobjects)
        else:
            self.add(*mobjects[0].submobjects)

    def get_mobjects_from(self, wrapper, style):
        element = wrapper.etree_element
        result = []
        if not isinstance(element, ElementTree.Element):
            return result

        matches = self.css_matcher.match(wrapper)
        if matches:
            for match in matches:
                _, _, _, css_style = match
                style.update(css_style)
        style = cascade_element_style(element, style)

        tag = element.tag.split("}")[-1]
        if tag == 'defs':
            self.update_ref_to_element(element, style)
        elif tag == 'style':
            pass
        elif tag in ['g', 'svg', 'symbol']:
            result += it.chain(*(
                self.get_mobjects_from(child, style)
                for child in wrapper.iter_children()
            ))
        elif tag == 'path':
            result.append(self.path_string_to_mobject(
                element.get('d'), style
            ))
        elif tag == 'use':
            result += self.use_to_mobjects(element, style)
        elif tag == 'rect':
            result.append(self.rect_to_mobject(element, style))
        elif tag == 'circle':
            result.append(self.circle_to_mobject(element, style))
        elif tag == 'ellipse':
            result.append(self.ellipse_to_mobject(element, style))
        elif tag in ['polygon', 'polyline']:
            result.append(self.polygon_to_mobject(element, style))
        else:
            log.warning(f"Unsupported element type: {tag}")
            pass  # TODO
        result = [m.insert_n_curves(0) for m in result if m is not None]
        self.handle_transforms(element, VGroup(*result))
        if len(result) > 1 and not self.unpack_groups:
            result = [VGroup(*result)]

        return result

    def generate_default_style(self):
        style = {
            "fill-opacity": self.fill_opacity,
            "stroke-width": self.stroke_width,
            "stroke-opacity": self.stroke_opacity,
        }
        if self.color:
            style["fill"] = style["stroke"] = self.color
        if self.fill_color:
            style["fill"] = self.fill_color
        if self.stroke_color:
            style["stroke"] = self.stroke_color
        return style
    
    def parse_css_style(self, css):
        rules = parse_stylesheet(css, True, True)
        for rule in rules:
            selectors = cssselect2.compile_selector_list(rule.prelude)
            declarations = parse_declaration_list(rule.content)
            style = {
                declaration.name: css_serialize(declaration.value)
                for declaration in declarations
                if declaration.name in DEFAULT_STYLE
            }
            payload = style
            for selector in selectors:
                self.css_matcher.add_selector(selector, payload)

    def path_string_to_mobject(self, path_string, style):
        return VMobjectFromSVGPathstring(
            path_string,
            **self.path_string_config,
            **parse_style(style, self.generate_default_style()),
        )

    def use_to_mobjects(self, use_element, local_style):
        # Remove initial "#" character
        ref = use_element.get("xlink:href")[1:]
        if ref not in self.ref_to_element:
            log.warning(f"{ref} not recognized")
            return VGroup()
        def_element, def_style = self.ref_to_element[ref]
        style = local_style.copy()
        style.update(def_style)
        return self.get_mobjects_from(
            def_element, style
        )

    def attribute_to_float(self, attr):
        stripped_attr = "".join([
            char for char in attr
            if char in string.digits + "." + "-"
        ])
        return float(stripped_attr)

    def polygon_to_mobject(self, polygon_element, style):
        path_string = polygon_element.get("points")
        for digit in string.digits:
            path_string = path_string.replace(f" {digit}", f"L {digit}")
        path_string = path_string.replace("L", "M", 1)
        return self.path_string_to_mobject(path_string, style)

    def circle_to_mobject(self, circle_element, style):
        x, y, r = (
            self.attribute_to_float(circle_element.get(key, "0.0"))
            for key in ("cx", "cy", "r")
        )
        return Circle(
            radius=r,
            **parse_style(style, self.generate_default_style())
        ).shift(x * RIGHT + y * DOWN)

    def ellipse_to_mobject(self, circle_element, style):
        x, y, rx, ry = (
            self.attribute_to_float(circle_element.get(key, "0.0"))
            for key in ("cx", "cy", "rx", "ry")
        )
        result = Circle(**parse_style(style, self.generate_default_style()))
        result.stretch(rx, 0)
        result.stretch(ry, 1)
        result.shift(x * RIGHT + y * DOWN)
        return result

    def rect_to_mobject(self, rect_element, style):
        stroke_width = rect_element.get("stroke-width", "")
        corner_radius = rect_element.get("rx", "")

        if stroke_width in ["", "none", "0"]:
            stroke_width = 0

        if corner_radius in ["", "0", "none"]:
            corner_radius = 0

        corner_radius = float(corner_radius)

        parsed_style = parse_style(style, self.generate_default_style())
        parsed_style["stroke_width"] = stroke_width

        if corner_radius == 0:
            mob = Rectangle(
                width=self.attribute_to_float(
                    rect_element.get("width", "")
                ),
                height=self.attribute_to_float(
                    rect_element.get("height", "")
                ),
                **parsed_style,
            )
        else:
            mob = RoundedRectangle(
                width=self.attribute_to_float(
                    rect_element.get("width", "")
                ),
                height=self.attribute_to_float(
                    rect_element.get("height", "")
                ),
                corner_radius=corner_radius,
                **parsed_style
            )

        mob.shift(mob.get_center() - mob.get_corner(UP + LEFT))
        return mob

    def handle_transforms(self, element, mobject):
        x, y = (
            self.attribute_to_float(element.get(key, "0.0"))
            for key in ("x", "y")
        )
        mobject.shift(x * RIGHT + y * DOWN)

        transform_names = [
            "matrix",
            "translate", "translateX", "translateY",
            "scale", "scaleX", "scaleY",
            "rotate",
            "skewX", "skewY"
        ]
        transform_pattern = re.compile("|".join([x + r"[^)]*\)" for x in transform_names]))
        number_pattern = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?")
        transforms = transform_pattern.findall(element.get('transform', ''))[::-1]

        for transform in transforms:
            op_name, op_args = transform.split("(")
            op_name = op_name.strip()
            op_args = [float(x) for x in number_pattern.findall(op_args)]

            if op_name == "matrix":
                self._handle_matrix_transform(mobject, op_name, op_args)
            elif op_name.startswith("translate"):
                self._handle_translate_transform(mobject, op_name, op_args)
            elif op_name.startswith("scale"):
                self._handle_scale_transform(mobject, op_name, op_args)
            elif op_name == "rotate":
                self._handle_rotate_transform(mobject, op_name, op_args)
            elif op_name.startswith("skew"):
                self._handle_skew_transform(mobject, op_name, op_args)

    def _handle_matrix_transform(self, mobject, op_name, op_args):
        transform = np.array(op_args).reshape([3, 2])
        x = transform[2][0]
        y = -transform[2][1]
        matrix = np.identity(self.dim)
        matrix[:2, :2] = transform[:2, :]
        matrix[1] *= -1
        matrix[:, 1] *= -1
        for mob in mobject.family_members_with_points():
            mob.apply_matrix(matrix.T)
        mobject.shift(x * RIGHT + y * UP)

    def _handle_translate_transform(self, mobject, op_name, op_args):
        if op_name.endswith("X"):
            x, y = op_args[0], 0
        elif op_name.endswith("Y"):
            x, y = 0, op_args[0]
        else:
            x, y = op_args
        mobject.shift(x * RIGHT + y * DOWN)

    def _handle_scale_transform(self, mobject, op_name, op_args):
        if op_name.endswith("X"):
            sx, sy = op_args[0], 1
        elif op_name.endswith("Y"):
            sx, sy = 1, op_args[0]
        elif len(op_args) == 2:
            sx, sy = op_args
        else:
            sx = sy = op_args[0]
        if sx < 0:
            mobject.flip(UP)
            sx = -sx
        if sy < 0:
            mobject.flip(RIGHT)
            sy = -sy
        mobject.scale(np.array([sx, sy, 1]), about_point=ORIGIN)

    def _handle_rotate_transform(self, mobject, op_name, op_args):
        if len(op_args) == 1:
            mobject.rotate(op_args[0] * DEGREES, axis=IN, about_point=ORIGIN)
        else:
            deg, x, y = op_args
            mobject.rotate(deg * DEGREES, axis=IN, about_point=np.array([x, y, 0]))

    def _handle_skew_transform(self, mobject, op_name, op_args):
        rad = op_args[0] * DEGREES
        if op_name == "skewX":
            tana = np.tan(rad)
            self._handle_matrix_transform(mobject, None, [1., 0., tana, 1., 0., 0.])
        elif op_name == "skewY":
            tana = np.tan(rad)
            self._handle_matrix_transform(mobject, None, [1., tana, 0., 1., 0., 0.])

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
        if not isinstance(element, ElementTree.Element):
            return
        if element.get('id'):
            return [element]
        for e in element.childNodes:
            all_childNodes_have_id.append(self.get_all_childNodes_have_id(e))
        return self.flatten([e for e in all_childNodes_have_id if e])

    def update_ref_to_element(self, defs, style):
        new_refs = dict([(e.get('id', ''), (e, style)) for e in self.get_all_childNodes_have_id(defs)])
        self.ref_to_element.update(new_refs)


class VMobjectFromSVGPathstring(VMobject):
    CONFIG = {
        "long_lines": False,
        "should_subdivide_sharp_curves": False,
        "should_remove_null_curves": False,
    }

    def __init__(self, path_string, **kwargs):
        self.path_string = path_string
        super().__init__(**kwargs)

    def init_points(self):
        # After a given svg_path has been converted into points, the result
        # will be saved to a file so that future calls for the same path
        # don't need to retrace the same computation.
        hasher = hashlib.sha256(self.path_string.encode())
        path_hash = hasher.hexdigest()[:16]
        points_filepath = os.path.join(get_mobject_data_dir(), f"{path_hash}_points.npy")
        tris_filepath = os.path.join(get_mobject_data_dir(), f"{path_hash}_tris.npy")

        if os.path.exists(points_filepath) and os.path.exists(tris_filepath):
            self.set_points(np.load(points_filepath))
            self.triangulation = np.load(tris_filepath)
            self.needs_new_triangulation = False
        else:
            self.handle_commands()
            if self.should_subdivide_sharp_curves:
                # For a healthy triangulation later
                self.subdivide_sharp_curves()
            if self.should_remove_null_curves:
                # Get rid of any null curves
                self.set_points(self.get_points_without_null_curves())
            # SVG treats y-coordinate differently
            self.stretch(-1, 1, about_point=ORIGIN)
            # Save to a file for future use
            np.save(points_filepath, self.get_points())
            np.save(tris_filepath, self.get_triangulation())

    def get_commands_and_coord_strings(self):
        all_commands = list(self.get_command_to_function_map().keys())
        all_commands += [c.lower() for c in all_commands]
        pattern = "[{}]".format("".join(all_commands))
        return zip(
            re.findall(pattern, self.path_string),
            re.split(pattern, self.path_string)[1:]
        )

    def handle_commands(self):
        relative_point = ORIGIN
        for command, coord_string in self.get_commands_and_coord_strings():
            func, number_types_str = self.command_to_function(command)
            upper_command = command.upper()
            if upper_command == "Z":
                func()  # `close_path` takes no arguments
                relative_point = self.get_last_point()
                continue

            number_types = np.array(list(number_types_str))
            n_numbers = len(number_types_str)
            number_list = _PathStringParser(coord_string, number_types_str).args
            number_groups = np.array(number_list).reshape((-1, n_numbers))

            for ind, numbers in enumerate(number_groups):
                if command.islower():
                    # Treat it as a relative command
                    numbers[number_types == "x"] += relative_point[0]
                    numbers[number_types == "y"] += relative_point[1]

                if upper_command == "A":
                    args = [*numbers[:5], np.array([*numbers[5:7], 0.0])]
                elif upper_command == "H":
                    args = [np.array([numbers[0], relative_point[1], 0.0])]
                elif upper_command == "V":
                    args = [np.array([relative_point[0], numbers[0], 0.0])]
                else:
                    args = list(np.hstack((
                        numbers.reshape((-1, 2)), np.zeros((n_numbers // 2, 1))
                    )))
                if upper_command == "M" and ind != 0:
                    # M x1 y1 x2 y2  is equal to  M x1 y1 L x2 y2
                    func, _ = self.command_to_function("L")
                func(*args)
                relative_point = self.get_last_point()

    def add_elliptical_arc_to(self, rx, ry, x_axis_rotation, large_arc_flag, sweep_flag, point):
        def close_to_zero(a, threshold=1e-5):
            return abs(a) < threshold

        def solve_2d_linear_equation(a, b, c):
            """
            Using Crammer's rule to solve the linear equation `[a b]x = c`
            where `a`, `b` and `c` are all 2d vectors.
            """
            def det(a, b):
                return a[0] * b[1] - a[1] * b[0]
            d = det(a, b)
            if close_to_zero(d):
                raise Exception("Cannot handle 0 determinant.")
            return [det(c, b) / d, det(a, c) / d]

        def get_arc_center_and_angles(x0, y0, rx, ry, phi, large_arc_flag, sweep_flag, x1, y1):
            """
            The parameter functions of an ellipse rotated `phi` radians counterclockwise is (on `alpha`):
                x = cx + rx * cos(alpha) * cos(phi) + ry * sin(alpha) * sin(phi),
                y = cy + rx * cos(alpha) * sin(phi) - ry * sin(alpha) * cos(phi).
            Now we have two points sitting on the ellipse: `(x0, y0)`, `(x1, y1)`, corresponding to 4 equations,
            and we want to hunt for 4 variables: `cx`, `cy`, `alpha0` and `alpha_1`.
            Let `d_alpha = alpha1 - alpha0`, then:
            if `sweep_flag = 0` and `large_arc_flag = 1`, then `PI <= d_alpha < 2 * PI`;
            if `sweep_flag = 0` and `large_arc_flag = 0`, then `0 < d_alpha <= PI`;
            if `sweep_flag = 1` and `large_arc_flag = 0`, then `-PI <= d_alpha < 0`;
            if `sweep_flag = 1` and `large_arc_flag = 1`, then `-2 * PI < d_alpha <= -PI`.
            """
            xd = x1 - x0
            yd = y1 - y0
            if close_to_zero(xd) and close_to_zero(yd):
                raise Exception("Cannot find arc center since the start point and the end point meet.")
            # Find `p = cos(alpha1) - cos(alpha0)`, `q = sin(alpha1) - sin(alpha0)`
            eq0 = [rx * np.cos(phi), ry * np.sin(phi), xd]
            eq1 = [rx * np.sin(phi), -ry * np.cos(phi), yd]
            p, q = solve_2d_linear_equation(*zip(eq0, eq1))
            # Find `s = (alpha1 - alpha0) / 2`, `t = (alpha1 + alpha0) / 2`
            # If `sin(s) = 0`, this requires `p = q = 0`,
            # implying `xd = yd = 0`, which is impossible.
            sin_s = (p ** 2 + q ** 2) ** 0.5 / 2
            if sweep_flag:
                sin_s = -sin_s
            sin_s = clip(sin_s, -1, 1)
            s = np.arcsin(sin_s)
            if large_arc_flag:
                if not sweep_flag:
                    s = PI - s
                else:
                    s = -PI - s
            sin_t = -p / (2 * sin_s)
            cos_t = q / (2 * sin_s)
            cos_t = clip(cos_t, -1, 1)
            t = np.arccos(cos_t)
            if sin_t <= 0:
                t = -t
            # We can make sure `0 < abs(s) < PI`, `-PI <= t < PI`.
            alpha0 = t - s
            alpha_1 = t + s
            cx = x0 - rx * np.cos(alpha0) * np.cos(phi) - ry * np.sin(alpha0) * np.sin(phi)
            cy = y0 - rx * np.cos(alpha0) * np.sin(phi) + ry * np.sin(alpha0) * np.cos(phi)
            return cx, cy, alpha0, alpha_1

        def get_point_on_ellipse(cx, cy, rx, ry, phi, angle):
            return np.array([
                cx + rx * np.cos(angle) * np.cos(phi) + ry * np.sin(angle) * np.sin(phi),
                cy + rx * np.cos(angle) * np.sin(phi) - ry * np.sin(angle) * np.cos(phi),
                0
            ])

        def convert_elliptical_arc_to_quadratic_bezier_curve(
            cx, cy, rx, ry, phi, start_angle, end_angle, n_components=8
        ):
            theta = (end_angle - start_angle) / n_components / 2
            handles = np.array([
                get_point_on_ellipse(cx, cy, rx / np.cos(theta), ry / np.cos(theta), phi, a)
                for a in np.linspace(
                    start_angle + theta,
                    end_angle - theta,
                    n_components,
                )
            ])
            anchors = np.array([
                get_point_on_ellipse(cx, cy, rx, ry, phi, a)
                for a in np.linspace(
                    start_angle + theta * 2,
                    end_angle,
                    n_components,
                )
            ])
            return handles, anchors

        phi = x_axis_rotation * DEGREES
        x0, y0 = self.get_last_point()[:2]
        cx, cy, start_angle, end_angle = get_arc_center_and_angles(
            x0, y0, rx, ry, phi, large_arc_flag, sweep_flag, point[0], point[1]
        )
        handles, anchors = convert_elliptical_arc_to_quadratic_bezier_curve(
            cx, cy, rx, ry, phi, start_angle, end_angle
        )
        for handle, anchor in zip(handles, anchors):
            self.add_quadratic_bezier_curve_to(handle, anchor)

    def command_to_function(self, command):
        return self.get_command_to_function_map()[command.upper()]

    def get_command_to_function_map(self):
        """
        Associates svg command to VMobject function, and
        the types of arguments it takes in
        """
        return {
            "M": (self.start_new_path, "xy"),
            "L": (self.add_line_to, "xy"),
            "H": (self.add_line_to, "x"),
            "V": (self.add_line_to, "y"),
            "C": (self.add_cubic_bezier_curve_to, "xyxyxy"),
            "S": (self.add_smooth_cubic_curve_to, "xyxy"),
            "Q": (self.add_quadratic_bezier_curve_to, "xyxy"),
            "T": (self.add_smooth_curve_to, "xy"),
            "A": (self.add_elliptical_arc_to, "uuaffxy"),
            "Z": (self.close_path, ""),
        }

    def get_original_path_string(self):
        return self.path_string


class InvalidPathError(ValueError):
    pass


class _PathStringParser:
    # modified from https://github.com/regebro/svg.path/
    def __init__(self, arguments, rules):
        self.args = []
        arguments = bytearray(arguments, "ascii")
        self._strip_array(arguments)
        while arguments:
            for rule in rules:
                self._rule_to_function_map[rule](arguments)

    @property
    def _rule_to_function_map(self):
        return {
            "x": self._get_number,
            "y": self._get_number,
            "a": self._get_number,
            "u": self._get_unsigned_number,
            "f": self._get_flag,
        }

    def _strip_array(self, arg_array):
        # wsp: (0x9, 0x20, 0xA, 0xC, 0xD) with comma 0x2C
        # https://www.w3.org/TR/SVG/paths.html#PathDataBNF
        while arg_array and arg_array[0] in [0x9, 0x20, 0xA, 0xC, 0xD, 0x2C]:
            arg_array[0:1] = b""

    def _get_number(self, arg_array):
        pattern = re.compile(rb"^[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?")
        res = pattern.search(arg_array)
        if not res:
            raise InvalidPathError(f"Expected a number, got '{arg_array}'")
        number = float(res.group())
        self.args.append(number)
        arg_array[res.start():res.end()] = b""
        self._strip_array(arg_array)
        return number

    def _get_unsigned_number(self, arg_array):
        number = self._get_number(arg_array)
        if number < 0:
            raise InvalidPathError(f"Expected an unsigned number, got '{number}'")
        return number

    def _get_flag(self, arg_array):
        flag = arg_array[0]
        if flag != 48 and flag != 49:
            raise InvalidPathError(f"Expected a flag (0/1), got '{chr(flag)}'")
        flag -= 48
        self.args.append(flag)
        arg_array[0:1] = b""
        self._strip_array(arg_array)
        return flag
