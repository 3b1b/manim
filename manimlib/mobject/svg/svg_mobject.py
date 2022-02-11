import svgelements as se
import numpy as np
import itertools as it
import os
import hashlib
import re

from manimlib.constants import RIGHT

from manimlib.mobject.geometry import Line
from manimlib.mobject.geometry import Circle
from manimlib.mobject.geometry import Polygon
from manimlib.mobject.geometry import Polyline
from manimlib.mobject.geometry import Rectangle
from manimlib.mobject.geometry import RoundedRectangle
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.config_ops import digest_config
from manimlib.utils.directories import get_mobject_data_dir
from manimlib.utils.images import get_full_vector_image_path
from manimlib.logger import log


def _convert_point_to_3d(x, y):
    return np.array([x, y, 0.0])


class SVGMobject(VMobject):
    CONFIG = {
        "should_center": True,
        "height": 2,
        "width": None,
        # Must be filled in in a subclass, or when called
        "file_name": None,
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

    def init_colors(self):
        # Remove fill_color, fill_opacity,
        # stroke_width, stroke_color, stroke_opacity
        # as each submobject may have those values specified in svg file
        self.set_stroke(
            background=self.draw_stroke_behind_fill,
        )
        self.set_gloss(self.gloss)
        self.set_flat_stroke(self.flat_stroke)
        return self

    def init_points(self):
        with open(self.file_path, "r") as svg_file:
            svg_string = svg_file.read()

        # Create a temporary svg file to dump modified svg to be parsed
        modified_svg_string = self.modify_svg_file(svg_string)
        modified_file_path = self.file_path.replace(".svg", "_.svg")
        with open(modified_file_path, "w") as modified_svg_file:
            modified_svg_file.write(modified_svg_string)

        # `color` attribute handles `currentColor` keyword
        if self.fill_color:
            color = self.fill_color
        elif self.color:
            color = self.color
        else:
            color = "black"
        shapes = se.SVG.parse(
            modified_file_path,
            color=color
        )
        os.remove(modified_file_path)

        mobjects = self.get_mobjects_from(shapes)
        self.add(*mobjects)
        self.flip(RIGHT)  # Flip y
        self.scale(0.75)

    def modify_svg_file(self, svg_string):
        # svgelements cannot handle em, ex units
        # Convert them using 1em = 16px, 1ex = 0.5em = 8px
        def convert_unit(match_obj):
            number = float(match_obj.group(1))
            unit = match_obj.group(2)
            factor = 16 if unit == "em" else 8
            return str(number * factor) + "px"

        number_pattern = r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)(ex|em)(?![a-zA-Z])"
        result = re.sub(number_pattern, convert_unit, svg_string)

        # Add a group tag to set style from configuration
        style_dict = self.generate_context_values_from_config()
        group_tag_begin = "<g " + " ".join([
            f"{k}=\"{v}\""
            for k, v in style_dict.items()
        ]) + ">"
        group_tag_end = "</g>"
        begin_insert_index = re.search(r"<svg[\s\S]*?>", result).end()
        end_insert_index = re.search(r"[\s\S]*(</svg\s*>)", result).start(1)
        result = "".join([
            result[:begin_insert_index],
            group_tag_begin,
            result[begin_insert_index:end_insert_index],
            group_tag_end,
            result[end_insert_index:]
        ])

        return result

    def generate_context_values_from_config(self):
        result = {
            "fill-opacity": self.fill_opacity,
            "stroke-width": self.stroke_width,
            "stroke-opacity": self.stroke_opacity,
        }
        if self.color:
            result["fill"] = result["stroke"] = self.color
        if self.fill_color:
            result["fill"] = self.fill_color
        if self.stroke_color:
            result["stroke"] = self.stroke_color
        return result

    def get_mobjects_from(self, shape):
        if isinstance(shape, se.Group):
            return list(it.chain(*(
                self.get_mobjects_from(child)
                for child in shape
            )))

        mob = self.get_mobject_from(shape)
        if mob is None:
            return []

        if isinstance(shape, se.Transformable) and shape.apply:
            self.handle_transform(mob, shape.transform)
        return [mob]

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
