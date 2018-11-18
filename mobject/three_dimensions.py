from __future__ import absolute_import

from constants import *

from mobject.types.vectorized_mobject import VMobject
from mobject.geometry import Square

from utils.space_ops import z_to_vector

##############


def should_shade_in_3d(mobject):
    return hasattr(mobject, "shade_in_3d") and mobject.shade_in_3d


def shade_in_3d(mobject):
    for submob in mobject.submobject_family():
        submob.shade_in_3d = True


def turn_off_3d_shading(mobject):
    for submob in mobject.submobject_family():
        submob.shade_in_3d = False


class ThreeDMobject(VMobject):
    def __init__(self, *args, **kwargs):
        VMobject.__init__(self, *args, **kwargs)
        shade_in_3d(self)


class Cube(ThreeDMobject):
    CONFIG = {
        "fill_opacity": 0.75,
        "fill_color": BLUE,
        "stroke_width": 0,
        "propagate_style_to_family": True,
        "side_length": 2,
    }

    def generate_points(self):
        for vect in IN, OUT, LEFT, RIGHT, UP, DOWN:
            face = Square(side_length=self.side_length)
            face.shift(self.side_length * OUT / 2.0)
            face.apply_function(lambda p: np.dot(p, z_to_vector(vect).T))

            self.add(face)

## eps: distance between points

class Sphere(ThreeDMobject):
    CONFIG = {
        'fill_opacity': .75,
        'fill_color': BLUE,
        'stroke_width': 0,
        'propagate_style_to_family': True,
        'side_length': 2
    }
    def __init__(self, r, eps, opacity = .75):
        self.r = r
        self.eps = eps
        self.CONFIG['fill_opacity'] = opacity
        ThreeDMobject.__init__(self)

    def generate_points(self):
        points = [
            (
                self.r * (np.sin(phi) * np.cos(theta)), 
                self.r * (np.sin(phi) * np.sin(theta)), 
                self.r * np.cos(phi)
            ) 
            for phi in np.arange(0, 2 * np.pi, self.eps) 
            for theta in np.arange(0, 2 * np.pi, self.eps) 
        ]
        for vect in points:
            face = Square(side_length=self.eps)
            scalefactor = np.linalg.norm(vect)
            face.shift(scalefactor * OUT / 2.0)
            face.apply_function(lambda p: np.dot(p, z_to_vector(vect).T))
            self.add(face)
        shade_in_3d(self)


class Prism(Cube):
    CONFIG = {
        "dimensions": [3, 2, 1]
    }

    def generate_points(self):
        Cube.generate_points(self)
        for dim, value in enumerate(self.dimensions):
            self.rescale_to_fit(value, dim, stretch=True)

class Torus(ThreeDMobject):
    CONFIG = {
        'fill_opacity': .75,
        'fill_color': BLUE,
        'stroke_width': 0,
        'propagate_style_to_family': True,
        'side_length': 2
     }
    def __init__(self, r1, r2, eps, opacity=.75):
        self.r1 = r1
        self.r2 = r2
        self.eps = eps
        self.CONFIG['fill_opacity'] = opacity
        ThreeDMobject.__init__(self)


    def generate_points(self):
        points = [ 
            (
                (self.r1 + self.r2 * np.cos(theta)) * np.cos(phi),
                (self.r1 + self.r2 * np.cos(theta)) * np.sin(phi), 
                self.r2 * np.sin(theta)
            ) 
            for phi in np.arange(0, 2 * np.pi, self.eps) 
            for theta in np.arange(0, 2 * np.pi, self.eps) 
        ]
        for vect in points:
            face = Square(side_length=self.eps)
            scalefactor = np.linalg.norm(vect)
            face.shift(scalefactor * OUT / 2.0)
            face.apply_function(lambda p: np.dot(p, z_to_vector(vect).T))
            self.add(face)
        shade_in_3d(self)



class Parametric3D(ThreeDMobject):
    CONFIG = {
        'fill_opacity': 0.75,
        'fill_color': BLUE,
        'stroke_width': 0,
        'propagate_style_to_family': True
    }

    def __init__(self, f, g, h, phi_min, phi_max, theta_min, theta_max, eps, opacity = .75):
        self.f = f # x(t)
        self.g = g # y(t)
        self.h = h # z(t)
        self.phi_min = phi_min
        self.phi_max = phi_max
        self.theta_min = theta_min
        self.theta_max = theta_max
        self.eps = eps
        self.CONFIG['fill_opacity'] = opacity
        ThreeDMobject.__init__(self)

    def generate_points(self):
        points = [
            (
                self.f(phi, theta), 
                self.g(phi, theta), 
                self.h(phi, theta)
            ) 
            for phi in np.arange(self.phi_min, self.phi_max, self.eps) 
            for theta in np.arange(self.theta_min, self.theta_max, self.eps) 
        ]
        for vect in points:
            face = Square(side_length=self.eps)
            scalefactor = np.linalg.norm(vect)
            face.shift(scalefactor * OUT / 2.0)
            face.apply_function(lambda p: np.dot(p, z_to_vector(vect).T))
            self.add(face)
        shade_in_3d(self)