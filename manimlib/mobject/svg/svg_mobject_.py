import numpy as np
import itertools as it

from svglib.svglib import svg2rlg
import reportlab.graphics.shapes as rlg

from manimlib.constants import BLACK

from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.config_ops import digest_config
from manimlib.utils.images import get_full_vector_image_path
from manimlib.logger import log


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
        drawing = svg2rlg(self.file_path)
        mobjects = self.get_mobjects_from(drawing)
        #if self.unpack_groups:
        self.add(*mobjects) # TODO
        #else:
        #    self.add(*mobjects[0].submobjects)

    def get_mobjects_from(self, rlg_shape):
        if isinstance(rlg_shape, rlg.Group):
            mobs = list(it.chain(*(
                self.get_mobjects_from(child)
                for child in rlg_shape.getContents()
            )))
            self.handle_transform(mobs, rlg_shape.transform)
            return mobs

        mob = self.get_single_mobject_from(rlg_shape)
        self.parse_style_for_mobject(mob, rlg_shape)
        return [mob]

    def get_single_mobject_from(self, rlg_shape):
        if isinstance(rlg_shape, rlg.Path):
            return self.path_to_mobject(rlg_shape)

        if isinstance(rlg_shape, rlg.Line):
            return self.line_to_mobject(rlg_shape)

        if isinstance(rlg_shape, rlg.Rect):
            return self.rect_to_mobject(rlg_shape)

        if isinstance(rlg_shape, rlg.Circle):
            return self.circle_to_mobject(rlg_shape)

        if isinstance(rlg_shape, rlg.Ellipse):
            return self.ellipse_to_mobject(rlg_shape)

        if isinstance(rlg_shape, rlg.Polygon):
            return self.polygon_to_mobject(rlg_shape)

        if isinstance(rlg_shape, rlg.Polyline):
            return self.polyline_to_mobject(rlg_shape)

        # TODO, support String & Image
        log.warning(f"Unsupported element type: {rlg_shape.__class__.__name__}")
        return []




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

    @staticmethod
    def handle_transform(mobs, transform):
        mat = np.array(transform[:4]).reshape((2, 2)).T
        vec = np.array([*transform[4:], 0.0])
        for mob in mobs:
            mob.apply_matrix(mat)
            mob.shift(vec)
        return mobs

    @staticmethod
    def parse_style_for_mobject(mob, rlg_shape):
        # TODO
        #if rlg_shape.fillColor is not None:
        #    fill_color = "#" + rlg_shape.fillColor.hexval()[2:]
        #else:
        #    fill_color = BLACK
        fill_color = "#" + rlg_shape.fillColor.hexval()[2:]
        fill_opacity = rlg_shape.fillOpacity
        stroke_width = rlg_shape.strokeWidth
        if rlg_shape.strokeColor is not None:
            stroke_color = "#" + rlg_shape.strokeColor.hexval()[2:]
        else:
            stroke_color = BLACK
        stroke_opacity = rlg_shape.strokeOpacity
        mob.set_fill(
            color=fill_color,
            opacity=fill_opacity
        )
        mob.set_stroke(
            width=stroke_width,
            color=stroke_color,
            opacity=stroke_opacity
        )
        return mob

    def path_to_mobject(self, rlg_shape):
        mob = VMobject()
        command_to_function_list = (
            (mob.start_new_path, 1),             # move to
            (mob.add_line_to, 1),                # line to
            (mob.add_cubic_bezier_curve_to, 3),  # curve to
            (mob.close_path, 0),                 # close path
        )
        points = np.array(rlg_shape.points).reshape((-1, 2))
        points = np.hstack((points, np.zeros((points.shape[0], 1))))
        current_index = 0
        for op in rlg_shape.operators:
            func, arg_count = command_to_function_list[op]
            next_index = current_index + arg_count
            func(*points[current_index:next_index])
            current_index = next_index
        return mob

    def line_to_mobject(self, rlg_shape):
        pass

    def rect_to_mobject(self, rlg_shape):
        pass

    def circle_to_mobject(self, rlg_shape):
        pass

    def ellipse_to_mobject(self, rlg_shape):
        pass

    def polygon_to_mobject(self, rlg_shape):
        pass

    def polyline_to_mobject(self, rlg_shape):
        pass
