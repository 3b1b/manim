from helpers import *

from mobject import Mobject, Mobject1D, Point

class Dot(Mobject1D): #Use 1D density, even though 2D
    DEFAULT_CONFIG = {
        "radius" : 0.05
    }
    def __init__(self, center_point = ORIGIN, **kwargs):
        digest_locals(self)
        Mobject1D.__init__(self, **kwargs)

    def generate_points(self):
        self.add_points([
            np.array((t*np.cos(theta), t*np.sin(theta), 0)) + self.center_point
            for t in np.arange(self.epsilon, self.radius, self.epsilon)
            for new_epsilon in [2*np.pi*self.epsilon*self.radius/t]
            for theta in np.arange(0, 2 * np.pi, new_epsilon)
        ])

class Cross(Mobject1D):
    DEFAULT_CONFIG = {
        "color"  : YELLOW,
        "radius" : 0.3
    }
    def __init__(self, center_point = ORIGIN, **kwargs):
        digest_locals(self)
        Mobject1D.__init__(self, **kwargs)

    def generate_points(self):
        self.add_points([
            (sgn * x, x, 0)
            for x in np.arange(-self.radius / 2, self.radius/2, self.epsilon)
            for sgn in [-1, 1]
        ])
        self.shift(self.center_point)


class Line(Mobject1D):
    DEFAULT_CONFIG = {
        "buff" : 0
    }
    def __init__(self, start, end, **kwargs):
        digest_config(self, kwargs)
        self.set_start_and_end(start, end)
        Mobject1D.__init__(self, **kwargs)

    def set_start_and_end(self, start, end):
        preliminary_start, preliminary_end = [
            arg.get_center() 
            if isinstance(arg, Mobject) 
            else np.array(arg).astype('float')
            for arg in start, end
        ]
        start_to_end = preliminary_end - preliminary_start
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

    def generate_points(self):
        self.add_line(self.start, self.end)

    def get_length(self):
        return np.linalg.norm(self.start - self.end)

    def get_slope(self):
        rise, run = [
            float(self.end[i] - self.start[i])
            for i in [1, 0]
        ]
        return rise/run

class Arrow(Line):
    DEFAULT_CONFIG = {
        "color"      : YELLOW_C,
        "tip_length" : 0.25,
        "buff"       : 0.3,
    }
    def __init__(self, *args, **kwargs):
        if len(args) == 1:
            target = args[0]
            if isinstance(target, Mobject):
                point = target.get_center()
            else:
                point = target
            args = (point+UP+LEFT, target)
        Line.__init__(self, *args, **kwargs)
        self.add_tip()

    def add_tip(self):
        num_points = self.get_num_points()
        vect = self.start-self.end
        length = np.linalg.norm(vect)
        vect = vect*self.tip_length/length
        self.add_points([
            interpolate(self.end, self.end+v, t)
            for t in np.arange(0, 1, self.tip_length*self.epsilon)
            for v in [
                rotate_vector(vect, np.pi/4, axis)
                for axis in IN, OUT
            ]
        ])
        self.num_tip_points = self.get_num_points()-num_points

    def remove_tip(self):
        if not hasattr(self, "num_tip_points"):
            return self
        for attr in "points", "rgbs":
            setattr(self, attr, getattr(self, attr)[:-self.num_tip_points])
        return self

class CurvedLine(Line):
    def __init__(self, start, end, via = None, **kwargs):
        self.set_start_and_end(start, end)
        if via == None:
            self.via = rotate_vector(
                self.end - self.start, 
                np.pi/3, [0,0,1]
            ) + self.start
        elif isinstance(via, Mobject):
            self.via = via.get_center()
        else:
            self.via = via
        Line.__init__(self, start, end, **kwargs)

    def generate_points(self):
        self.add_points([
            interpolate(
                interpolate(self.start, self.end, t),
                self.via,
                t*(1-t)
            )
            for t in np.arange(0, 1, self.epsilon)
        ])


class Arc(Mobject1D):
    DEFAULT_CONFIG = {
        "radius"      : 1.0,
        "start_angle" : 0,
    }
    def __init__(self, angle, **kwargs):
        digest_locals(self)
        Mobject1D.__init__(self, **kwargs)

    def generate_points(self):
        sign = 1 if self.angle >= 0 else -1
        self.add_points([
            (self.radius*np.cos(theta), self.radius*np.sin(theta), 0)
            for theta in np.arange(
                self.start_angle, 
                self.start_angle+self.angle, 
                sign*self.epsilon/self.radius
            )
        ])

class Circle(Arc):
    DEFAULT_CONFIG = {
        "color" : RED,
    }
    def __init__(self, **kwargs):
        Arc.__init__(self, angle = 2*np.pi, **kwargs)

class Polygon(Mobject1D):
    DEFAULT_CONFIG = {
        "color"       : GREEN_D,
        "edge_colors" : None
    }
    def __init__(self, *vertices, **kwargs):
        assert len(vertices) > 1
        digest_locals(self)
        Mobject1D.__init__(self, **kwargs)

    def generate_points(self):
        if self.edge_colors:
            colors = it.cycle(self.edge_colors)
        else:
            colors = it.cycle([self.color])
        self.indices_of_vertices = []
        for start, end in adjascent_pairs(self.vertices):
            self.indices_of_vertices.append(self.get_num_points())
            self.add_line(start, end, color = colors.next())


    def get_vertices(self):
        return self.vertices[self.indices_of_vertices]



class Grid(Mobject1D):
    DEFAULT_CONFIG = {
        "height" : 6.0,
        "width"  : 6.0,
    }
    def __init__(self, rows, columns, **kwargs):
        digest_config(self, kwargs, locals())
        Mobject1D.__init__(self, **kwargs)

    def generate_points(self):
        x_step = self.width / self.columns
        y_step = self.height / self.rows

        for x in np.arange(0, self.width+x_step, x_step):
            self.add_line(
                [x-self.width/2., -self.height/2., 0],
                [x-self.width/2., self.height/2., 0],
            )
        for y in np.arange(0, self.height+y_step, y_step):
            self.add_line(
                [-self.width/2., y-self.height/2., 0],
                [self.width/2., y-self.height/2., 0]
            )

class Rectangle(Grid):
    DEFAULT_CONFIG = {
        "color"  : YELLOW,
        "height" : 2.0,
        "width"  : 4.0,
    }
    def __init__(self, **kwargs):
        Grid.__init__(self, 1, 1, **kwargs)

    def generate_points(self):
        wh = [self.width/2.0, self.height/2.0]
        self.add_points([
            (x, u, 0) if dim==0 else (u, x, 0)
            for dim in 0, 1
            for u in wh[1-dim], -wh[1-dim]
            for x in np.arange(-wh[dim], wh[dim], self.epsilon)
        ])

class Square(Rectangle):
    DEFAULT_CONFIG = {
        "side_length" : 2.0,
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        for arg in ["height", "width"]:
            kwargs[arg] = self.side_length
        Rectangle.__init__(self, **kwargs)





