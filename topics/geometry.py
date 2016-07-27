from helpers import *

from mobject import Mobject
from mobject.vectorized_mobject import VMobject

class Arc(VMobject):
    CONFIG = {
        "radius"           : 1.0,
        "start_angle"      : 0,
        "num_anchors"      : 8,
        "anchors_span_full_range" : True,
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
        return [
            np.cos(a)*RIGHT+np.sin(a)*UP
            for a in np.linspace(
                self.start_angle, 
                self.start_angle + self.angle, 
                self.num_anchors
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
        "fill_opacity" : 1.0,
        "color" : WHITE
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
        start, end = self.get_start_and_end()
        return np.linalg.norm(start - end)

    def get_start_and_end(self):
        return self.get_start(), self.get_end()

    def get_start(self):
        return self.points[0]

    def get_end(self):
        return self.points[-1]

    def get_slope(self):
        end = self.get_end()
        rise, run = [
            float(end[i] - start[i])
            for i in [1, 0]
        ]
        return np.inf if run == 0 else rise/run

    def get_angle(self):
        start, end = self.get_start_and_end()
        return angle_of_vector(end-start)

    def put_start_and_end_on(self, new_start, new_end):
        if self.get_length() == 0:
            #TODO, this is hacky
            self.points[0] += 0.01*LEFT
        new_length = np.linalg.norm(new_end - new_start)
        new_angle = angle_of_vector(new_end - new_start)
        self.scale(new_length / self.get_length())
        self.rotate(new_angle - self.get_angle())
        self.shift(new_start - self.get_start())
        return self


class Arrow(Line):
    CONFIG = {
        "color"      : YELLOW_C,
        "tip_length" : 0.25,
        "tip_angle"  : np.pi/6,
        "buff"       : 0.3,
        "propogate_style_to_family" : False,
        "preserve_tip_size_when_scaling" : True,
    }
    def __init__(self, *args, **kwargs):
        if len(args) == 1:
            point = self.pointify(args[0])
            args = (point+UP+LEFT, target)
        Line.__init__(self, *args, **kwargs)
        self.add_tip()

    def add_tip(self, add_at_end = True):
        vect = self.tip_length*RIGHT
        vect = rotate_vector(vect, self.get_angle()+np.pi)
        start, end = self.get_start_and_end()
        if not add_at_end:
            start, end = end, start
            vect = -vect
        tip_points = [
            end+rotate_vector(vect, u*self.tip_angle)
            for u in 1, -1
        ]
        self.tip = VMobject(
            close_new_points = True,
            mark_paths_closed = True,
            fill_color = self.color,
            fill_opacity = 1,
            stroke_color = self.color,
        )
        self.tip.set_anchor_points(
            [tip_points[0], end, tip_points[1]],
            mode = "corners"
        )
        self.add(self.tip)
        self.init_colors()

    def scale(self, scale_factor):
        Line.scale(self, scale_factor)
        if self.preserve_tip_size_when_scaling:
            self.remove(self.tip)
            self.add_tip()
        return self

class Vector(Arrow):
    CONFIG = {
        "color" : YELLOW,
        "buff"  : 0,
    }
    def __init__(self, direction, **kwargs):
        if len(direction) == 2:
            direction = np.append(np.array(direction), 0)
        Arrow.__init__(self, ORIGIN, direction, **kwargs)

class DoubleArrow(Arrow):
    def __init__(self, *args, **kwargs):
        Arrow.__init__(self, *args, **kwargs)
        self.add_tip(add_at_end = False)


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

class RegularPolygon(VMobject):
    CONFIG = {
        "start_angle" : 0
    }
    def __init__(self, n = 3, **kwargs):
        digest_config(self, kwargs, locals())
        start_vect = rotate_vector(RIGHT, self.start_angle)
        vertices = compass_directions(n, start_angle)
        Polygon.__init__(self, *vertices, **kwargs)


class Rectangle(VMobject):
    CONFIG = {
        "color"  : YELLOW,
        "height" : 2.0,
        "width"  : 4.0,
        "mark_paths_closed" : True,
        "close_new_points" : True,
    }
    def generate_points(self):
        y, x = self.height/2., self.width/2.
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

class BackgroundRectangle(Rectangle):
    CONFIG = {
        "color" : BLACK,
        "stroke_width" : 0,
        "fill_opacity" : 0.75,
    }
    def __init__(self, mobject, **kwargs):
        self.lock_style = False
        Rectangle.__init__(self, **kwargs)
        self.lock_style = True
        self.replace(mobject, stretch = True)
        self.original_fill_opacity = self.fill_opacity

    def pointwise_become_partial(self, mobject, a, b):
        self.lock_style = False
        self.set_fill(opacity = b*self.original_fill_opacity)
        self.lock_style = True
        return self

    def fade_to(self, *args, **kwargs):
        self.lock_style = False
        Rectangle.fade_to(self, *args, **kwargs)
        self.lock_style = True
        return self

    def set_style_data(self, *args, **kwargs):
        if self.lock_style:
            return self #Do nothing
        return Rectangle.set_style_data(self, *args, **kwargs)


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



