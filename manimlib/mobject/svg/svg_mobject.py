import os
import hashlib
import itertools as it
from xml.etree import ElementTree as ET

import svgelements as se
import numpy as np

from manimlib.constants import RIGHT
from manimlib.mobject.geometry import Line
from manimlib.mobject.geometry import Circle
from manimlib.mobject.geometry import Polygon
from manimlib.mobject.geometry import Polyline
from manimlib.mobject.geometry import Rectangle
from manimlib.mobject.geometry import RoundedRectangle
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.config_ops import digest_config
from manimlib.utils.directories import get_mobject_data_dir
from manimlib.utils.images import get_full_vector_image_path
from manimlib.utils.iterables import hash_obj
from manimlib.logger import log


SVG_HASH_TO_MOB_MAP = {}


def _convert_point_to_3d(x, y):
    return np.array([x, y, 0.0])


class SVGMobject(VMobject):
    CONFIG = {
        "should_center": True,
        "height": 2,
        "width": None,
        "file_name": None,
        # Style that overrides the original svg
        "color": None,
        "opacity": None,
        "fill_color": None,
        "fill_opacity": None,
        "stroke_width": None,
        "stroke_color": None,
        "stroke_opacity": None,
        # Style that fills only when not specified
        # If None, regarded as default values from svg standard
        "svg_default": {
            "color": None,
            "opacity": None,
            "fill_color": None,
            "fill_opacity": None,
            "stroke_width": None,
            "stroke_color": None,
            "stroke_opacity": None,
        },
        "path_string_config": {},
    }

    def __init__(self, file_name=None, **kwargs):
        super().__init__(**kwargs)
        self.file_name = file_name or self.file_name
        self.init_svg_mobject()
        self.init_colors()
        self.move_into_position()

    def init_svg_mobject(self):
        hash_val = hash_obj(self.hash_seed)
        if hash_val in SVG_HASH_TO_MOB_MAP:
            mob = SVG_HASH_TO_MOB_MAP[hash_val].copy()
            self.add(*mob)
            return

        self.generate_mobject()
        SVG_HASH_TO_MOB_MAP[hash_val] = self.copy()

    @property
    def hash_seed(self):
        # Returns data which can uniquely represent the result of `init_points`.
        # The hashed value of it is stored as a key in `SVG_HASH_TO_MOB_MAP`.
        return (
            self.__class__.__name__,
            self.svg_default,
            self.path_string_config,
            self.file_name
        )

    def generate_mobject(self):
        file_path = self.get_file_path()
        element_tree = ET.parse(file_path)
        new_tree = self.modify_xml_tree(element_tree)
        # Create a temporary svg file to dump modified svg to be parsed
        modified_file_path = file_path.replace(".svg", "_.svg")
        new_tree.write(modified_file_path)

        svg = se.SVG.parse(modified_file_path)
        os.remove(modified_file_path)

        mobjects = self.get_mobjects_from(svg)
        self.add(*mobjects)
        self.flip(RIGHT)  # Flip y

    def get_file_path(self):
        if self.file_name is None:
            raise Exception("Must specify file for SVGMobject")
        return get_full_vector_image_path(self.file_name)

    def modify_xml_tree(self, element_tree):
        config_style_dict = self.generate_config_style_dict()
        style_keys = (
            "fill",
            "fill-opacity",
            "stroke",
            "stroke-opacity",
            "stroke-width",
            "style"
        )
        root = element_tree.getroot()
        root_style_dict = {
            k: v for k, v in root.attrib.items()
            if k in style_keys
        }

        new_root = ET.Element("svg", {})
        config_style_node = ET.SubElement(new_root, "g", config_style_dict)
        root_style_node = ET.SubElement(config_style_node, "g", root_style_dict)
        root_style_node.extend(root)
        return ET.ElementTree(new_root)

    def generate_config_style_dict(self):
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

    def get_mobjects_from(self, svg):
        result = []
        for shape in svg.elements():
            if isinstance(shape, se.Group):
                continue
            mob = self.get_mobject_from(shape)
            if mob is None:
                continue
            if isinstance(shape, se.Transformable) and shape.apply:
                self.handle_transform(mob, shape.transform)
            result.append(mob)
        return result

    @staticmethod
    def handle_transform(mob, matrix):
        mat = np.array([
            [matrix.a, matrix.c],
            [matrix.b, matrix.d]
        ])
        vec = np.array([matrix.e, matrix.f, 0.0])
        mob.apply_matrix(mat)
        mob.shift(vec)
        return mob

    def get_mobject_from(self, shape):
        shape_class_to_func_map = {
            se.Path: self.path_to_mobject,
            se.SimpleLine: self.line_to_mobject,
            se.Rect: self.rect_to_mobject,
            se.Circle: self.circle_to_mobject,
            se.Ellipse: self.ellipse_to_mobject,
            se.Polygon: self.polygon_to_mobject,
            se.Polyline: self.polyline_to_mobject,
            # se.Text: self.text_to_mobject,  # TODO
        }
        for shape_class, func in shape_class_to_func_map.items():
            if isinstance(shape, shape_class):
                mob = func(shape)
                self.apply_style_to_mobject(mob, shape)
                return mob

        shape_class_name = shape.__class__.__name__
        if shape_class_name != "SVGElement":
            log.warning(f"Unsupported element type: {shape_class_name}")
        return None

    @staticmethod
    def apply_style_to_mobject(mob, shape):
        mob.set_style(
            stroke_width=shape.stroke_width,
            stroke_color=shape.stroke.hex,
            stroke_opacity=shape.stroke.opacity,
            fill_color=shape.fill.hex,
            fill_opacity=shape.fill.opacity
        )
        return mob

    def path_to_mobject(self, path):
        return VMobjectFromSVGPath(path, **self.path_string_config)

    def line_to_mobject(self, line):
        return Line(
            start=_convert_point_to_3d(line.x1, line.y1),
            end=_convert_point_to_3d(line.x2, line.y2)
        )

    def rect_to_mobject(self, rect):
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

    def circle_to_mobject(self, circle):
        # svgelements supports `rx` & `ry` but `r`
        mob = Circle(radius=circle.rx)
        mob.shift(_convert_point_to_3d(
            circle.cx, circle.cy
        ))
        return mob

    def ellipse_to_mobject(self, ellipse):
        mob = Circle(radius=ellipse.rx)
        mob.stretch_to_fit_height(2 * ellipse.ry)
        mob.shift(_convert_point_to_3d(
            ellipse.cx, ellipse.cy
        ))
        return mob

    def polygon_to_mobject(self, polygon):
        points = [
            _convert_point_to_3d(*point)
            for point in polygon
        ]
        return Polygon(*points)

    def polyline_to_mobject(self, polyline):
        points = [
            _convert_point_to_3d(*point)
            for point in polyline
        ]
        return Polyline(*points)

    def text_to_mobject(self, text):
        pass

    def move_into_position(self):
        if self.should_center:
            self.center()
        if self.height is not None:
            self.set_height(self.height)
        if self.width is not None:
            self.set_width(self.width)


class VMobjectFromSVGPath(VMobject):
    CONFIG = {
        "long_lines": False,
        "should_subdivide_sharp_curves": False,
        "should_remove_null_curves": False,
    }

    def __init__(self, path_obj, **kwargs):
        # Get rid of arcs
        path_obj.approximate_arcs_with_quads()
        self.path_obj = path_obj
        super().__init__(**kwargs)

    def init_points(self):
        # After a given svg_path has been converted into points, the result
        # will be saved to a file so that future calls for the same path
        # don't need to retrace the same computation.
        path_string = self.path_obj.d()
        hasher = hashlib.sha256(path_string.encode())
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
            # Save to a file for future use
            np.save(points_filepath, self.get_points())
            np.save(tris_filepath, self.get_triangulation())

    def handle_commands(self):
        segment_class_to_func_map = {
            se.Move: (self.start_new_path, ("end",)),
            se.Close: (self.close_path, ()),
            se.Line: (self.add_line_to, ("end",)),
            se.QuadraticBezier: (self.add_quadratic_bezier_curve_to, ("control", "end")),
            se.CubicBezier: (self.add_cubic_bezier_curve_to, ("control1", "control2", "end"))
        }
        for segment in self.path_obj:
            segment_class = segment.__class__
            func, attr_names = segment_class_to_func_map[segment_class]
            points = [
                _convert_point_to_3d(*segment.__getattribute__(attr_name))
                for attr_name in attr_names
            ]
            func(*points)

        # Get rid of the side effect of trailing "Z M" commands.
        if self.has_new_path_started():
            self.resize_points(self.get_num_points() - 1)
