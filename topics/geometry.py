from helpers import *

from mobject import Mobject
from mobject.vectorized_mobject import VMobject

class Arc(VMobject):
    CONFIG = {
        "radius"           : 1.0,
        "start_angle"      : 0,
        "num_anchors"      : 8,
        "anchors_span_full_range" : True
    }
    def __init__(self, angle, **kwargs):
        digest_locals(self)
        VMobject.__init__(self, **kwargs)

    def generate_points(self):
        self.set_anchor_points(
            self.get_unscaled_anchor_points(),
            mode = "smooth"
        )
        self.scale(self.radius)

    def get_unscaled_anchor_points(self):
        step = self.angle/self.num_anchors
        end_angle = self.start_angle + self.angle 
        if self.anchors_span_full_range:
            end_angle += step
        return [
            np.cos(a)*RIGHT+np.sin(a)*UP
            for a in np.arange(
                self.start_angle, end_angle, step
            )
        ]

class Circle(Arc):
    CONFIG = {
        "color" : RED,
        "close_new_points" : True,
        "anchors_span_full_range" : False
    }
    def __init__(self, **kwargs):
        Arc.__init__(self, 2*np.pi, **kwargs)

class Dot(Circle): #Use 1D density, even though 2D
    CONFIG = {
        "radius"       : 0.05,
        "stroke_width" : 0,
        "fill_color"   : WHITE,
        "fill_opacity" : 1.0
    }
    def __init__(self, point = ORIGIN, **kwargs):
        Circle.__init__(self, **kwargs)
        self.shift(point)
        self.init_colors()


class Line(VMobject):
    CONFIG = {
        "buff" : 0,
    }
    def __init__(self, start, end, **kwargs):
        digest_config(self, kwargs)
        self.set_start_and_end(start, end)
        VMobject.__init__(self, **kwargs)

    def set_start_and_end(self, start, end):
        start_to_end = self.pointify(end) - self.pointify(start)
        vect = np.zeros(len(start_to_end))
        longer_dim = np.argmax(map(abs, start_to_end))
        vect[longer_dim] = start_to_end[longer_dim]
        self.start, self.end = [
            arg.get_edge_center(unit*vect)
            if isinstance(arg, Mobject)
            else np.array(arg)
            for arg, unit in zip([start, end], [1, -1])
        ]
        start_to_end = self.end - self.start
        length = np.linalg.norm(start_to_end)
        if length > 2*self.buff:
            start_to_end /= np.linalg.norm(start_to_end)
            self.start = self.start + self.buff*start_to_end
            self.end = self.end - self.buff*start_to_end

    def pointify(self, mob_or_point):
        if isinstance(mob_or_point, Mobject):
            return mob_or_point.get_center()
        return np.array(mob_or_point)

    def generate_points(self):
        self.set_points_as_corners([self.start, self.end])

    def get_length(self):
        return np.linalg.norm(self.start - self.end)

    def get_start_and_end(self):
        return self.points[0], self.points[-1]

    def get_slope(self):
        start, end = self.get_start_and_end()
        rise, run = [
            float(end[i] - start[i])
            for i in [1, 0]
        ]
        return np.inf if run == 0 else rise/run

    def get_angle(self):
        start, end = self.get_start_and_end()
        return angle_of_vector(end-start)

class Arrow(Line):
    CONFIG = {
        "color"      : YELLOW_C,
        "tip_length" : 0.25,
        "buff"       : 0.3,
    }
    def __init__(self, *args, **kwargs):
        if len(args) == 1:
            point = self.pointify(args[0])
            args = (point+UP+LEFT, target)
        Line.__init__(self, *args, **kwargs)
        self.add_tip()

    def add_tip(self):
        vect = self.start-self.end
        length = np.linalg.norm(vect)
        vect *= self.tip_length/length
        tip_points = [
            self.end+rotate_vector(vect, u*np.pi/5)
            for u in 1, -1
        ]
        self.tip = VMobject(close_new_points = False)
        self.tip.set_anchor_points(
            [tip_points[0], self.end, tip_points[1]],
            mode = "corners"
        )
        self.add(self.tip)
        self.init_colors()

class Vector(Arrow):
    CONFIG = {
        "color" : WHITE,
        "buff"  : 0,
    }
    def __init__(self, start, direction, **kwargs):
        Arrow.__init__(self, start, end, **kwargs)

class Cross(VMobject):
    CONFIG = {
        "color"  : YELLOW,
        "radius" : 0.3
    }
    def generate_points(self):
        p1, p2, p3, p4 = self.radius * np.array([
            UP+LEFT, 
            DOWN+RIGHT,
            UP+RIGHT, 
            DOWN+LEFT,
        ])
        self.add(Line(p1, p2), Line(p3, p4))
        self.init_colors()

class CubicBezier(VMobject):
    def __init__(self, points, **kwargs):
        VMobject.__init__(self, **kwargs)
        self.set_points(points)

class Polygon(VMobject):
    CONFIG = {
        "color" : GREEN_D,
        "mark_paths_closed" : True,
        "close_new_points" : True,
    }
    def __init__(self, *vertices, **kwargs):
        assert len(vertices) > 1
        digest_locals(self)
        VMobject.__init__(self, **kwargs)

    def generate_points(self):
        self.set_anchor_points(self.vertices, mode = "corners")

    def get_vertices(self):
        return self.get_anchors_and_handles()[0]


class Rectangle(VMobject):
    CONFIG = {
        "color"  : YELLOW,
        "height" : 2.0,
        "width"  : 4.0,
        "mark_paths_closed" : True,
        "close_new_points" : True,
    }
    def generate_points(self):
        y, x = self.height/2, self.width/2
        self.set_anchor_points([
            x*LEFT+y*UP,
            x*RIGHT+y*UP,
            x*RIGHT+y*DOWN,
            x*LEFT+y*DOWN
        ], mode = "corners")

class Square(Rectangle):
    CONFIG = {
        "side_length" : 2.0,
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        Rectangle.__init__(
            self, 
            height = self.side_length,
            width = self.side_length,
            **kwargs
        )


class Grid(VMobject):
    CONFIG = {
        "height" : 6.0,
        "width"  : 6.0,
    }
    def __init__(self, rows, columns, **kwargs):
        digest_config(self, kwargs, locals())
        VMobject.__init__(self, **kwargs)

    def generate_points(self):
        x_step = self.width / self.columns
        y_step = self.height / self.rows

        for x in np.arange(0, self.width+x_step, x_step):
            self.add(Line(
                [x-self.width/2., -self.height/2., 0],
                [x-self.width/2., self.height/2., 0],
            ))
        for y in np.arange(0, self.height+y_step, y_step):
            self.add(Line(
                [-self.width/2., y-self.height/2., 0],
                [self.width/2., y-self.height/2., 0]
            ))



