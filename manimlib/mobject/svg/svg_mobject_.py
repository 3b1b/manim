import svgelements as se
import numpy as np
import itertools as it
import os
import hashlib

from manimlib.constants import ORIGIN

from manimlib.mobject.geometry import Line
from manimlib.mobject.geometry import Circle
from manimlib.mobject.geometry import Polygon
from manimlib.mobject.geometry import Polyline
from manimlib.mobject.geometry import Rectangle
from manimlib.mobject.geometry import RoundedRectangle
from manimlib.mobject.svg.text_mobject import Text
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.config_ops import digest_config
from manimlib.utils.directories import get_mobject_data_dir
from manimlib.utils.images import get_full_vector_image_path
from manimlib.logger import log


def _convert_point_to_3d(x, y):
    return np.array([x, y, 0.0])


class SVGMobject_(VMobject):
    CONFIG = {
        "should_center": True,
        "height": 2,
        "width": None,
        # Must be filled in in a subclass, or when called
        "file_name": None,
        #"unpack_groups": True,  # if False, creates a hierarchy of VGroups
        "stroke_width": 0.0,
        "fill_opacity": 1.0,
        "path_string_config": {}  # TODO
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
        pass  # TODO

    def init_points(self):
        #default_style = self.generate_context_from_config()
        context = se.Group(self.generate_context_from_config())
        shapes = se.SVG.parse(
            self.file_path,
            #transform="scale(1,-1)"  # Flip y
        )
        #mobjects = self.get_mobjects_from(drawing)
        #if self.unpack_groups:
        mobject_list = [
            self.get_mobject_from(shape)
            for shape in shapes
        ]
        self.add(*filter(lambda m: m is not None, mobject_list))
        #else:
        #    self.add(*mobjects[0].submobjects)

    #def get_mobjects_from(self, shape):
    #    if isinstance(shape, rlg.Group):
    #        mobs = list(it.chain(*(
    #            self.get_mobjects_from(child)
    #            for child in shape.getContents()
    #        )))
    #        self.handle_transform(mobs, shape.transform)
    #        return mobs

    #    mob = self.get_single_mobject_from(shape)
    #    self.apply_style_to_mobject(mob, shape)
    #    return [mob]

    def generate_context_from_config(self):
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

    def get_mobject_from(self, shape):
        shape_class_to_func_map = {
            se.Path: "path_to_mobject",
            se.SimpleLine: "line_to_mobject",
            se.Rect: "rect_to_mobject",
            se.Circle: "circle_to_mobject",
            se.Ellipse: "ellipse_to_mobject",
            se.Polygon: "polygon_to_mobject",
            se.Polyline: "polyline_to_mobject",
            se.Text: "text_to_mobject"
        }
        for shape_class, func_name in shape_class_to_func_map.items():
            if isinstance(shape, shape_class):
                func_name = shape_class_to_func_map[shape_class]
                mob = self.__getattribute__(func_name)(shape)
                self.apply_style_to_mobject(mob, shape)
                return mob

        log.warning(f"Unsupported element type: {shape.__class__.__name__}")
        return None

        #if tag == 'defs':
        #    self.update_ref_to_element(wrapper, style)
        #elif tag in ['g', 'svg', 'symbol']:
        #    result += it.chain(*(
        #        self.get_mobjects_from(child, style)
        #        for child in wrapper.iter_children()
        #    ))
        #elif tag == 'path':
        #    result.append(self.path_string_to_mobject(
        #        element.get('d'), style
        #    ))
        #elif tag == 'use':
        #    result += self.use_to_mobjects(element, style)
        #elif tag == 'line':
        #    result.append(self.line_to_mobject(element, style))
        #elif tag == 'rect':
        #    result.append(self.rect_to_mobject(element, style))
        #elif tag == 'circle':
        #    result.append(self.circle_to_mobject(element, style))
        #elif tag == 'ellipse':
        #    result.append(self.ellipse_to_mobject(element, style))
        #elif tag in ['polygon', 'polyline']:
        #    result.append(self.polygon_to_mobject(element, style))
        #elif tag == 'style':
        #    pass
        #else:
        #    log.warning(f"Unsupported element type: {tag}")
        #    pass  # TODO, support <text> tag
        #result = [m for m in result if m is not None]
        #self.handle_transform(element, VGroup(*result))
        #if len(result) > 1 and not self.unpack_groups:
        #    result = [VGroup(*result)]

        #return result

    #@staticmethod
    #def handle_transform(mobs, transform):  # TODO: needed?
    #    mat = np.array(transform[:4]).reshape((2, 2)).T
    #    vec = np.array([*transform[4:], 0.0])
    #    for mob in mobs:
    #        mob.apply_matrix(mat)
    #        mob.shift(vec)
    #    return mobs

    @staticmethod
    def apply_style_to_mobject(mob, shape):
        print(shape.stroke_width)  # TODO: stroke_width of text
        mob.set_style(
            stroke_width=shape.stroke_width,
            stroke_color=shape.stroke.hex,
            stroke_opacity=shape.stroke.opacity,
            fill_color=shape.fill.hex,
            fill_opacity=shape.fill.opacity
        )
        ## Initialize
        #mob.set_stroke(width=0.0)
        #if isinstance(shape, rlg.LineShape):
        #    if shape.strokeColor is not None:
        #        mob.set_stroke(
        #            width=shape.strokeWidth,
        #            color="#" + shape.strokeColor.hexval()[2:],
        #            opacity=shape.strokeOpacity
        #        )
        #    if isinstance(shape, rlg.SolidShape):
        #        if shape.fillColor is not None:
        #            mob.set_fill(
        #                color="#" + shape.fillColor.hexval()[2:],
        #                opacity=shape.fillOpacity
        #            )
        #elif isinstance(shape, rlg.String):
        #    if shape.fillColor is not None:
        #        mob.set_fill(
        #            color="#" + shape.fillColor.hexval()[2:],
        #            #opacity=shape.fillOpacity  # TODO
        #        )
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
            rect.y + rect.height / 2   # TODO
        ))
        return mob

    def circle_to_mobject(self, circle):
        mob = Circle(radius=circle.r)
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
        mob = Text(
            text.text,
            font=text.font_family,
            font_size=text.font_size
        ).scale(1 / 0.0076).scale(20)  # TODO: scale
        #mob.shift(np.array([
        #    text.x, text.y, 0.0
        #]))
        return mob


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
            # SVG treats y-coordinate differently
            self.stretch(-1, 1, about_point=ORIGIN)
            # Save to a file for future use
            np.save(points_filepath, self.get_points())
            np.save(tris_filepath, self.get_triangulation())

    def handle_commands(self):
        segment_class_to_func_map = {
            se.Move: ("start_new_path", ("end",)),
            se.Close: ("close_path", ()),
            se.Line: ("add_line_to", ("end",)),
            se.QuadraticBezier: ("add_quadratic_bezier_curve_to", ("control", "end")),
            se.CubicBezier: ("add_cubic_bezier_curve_to", ("control1", "control2", "end"))
        }
        for segment in self.path_obj:
            segment_class = segment.__class__
            func_name, attr_names = segment_class_to_func_map[segment_class]
            points = [
                _convert_point_to_3d(*segment.__getattribute__(attr_name))
                for attr_name in attr_names
            ]
            self.__getattribute__(func_name)(*points)
