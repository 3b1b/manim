
from helpers import *

from mobject.vectorized_mobject import VGroup, VMobject
from topics.geometry import Square
from scene import Scene
from camera import Camera

class ThreeDCamera(Camera):
    CONFIG = {
        "sun_vect" : 3*UP+LEFT,
        "shading_factor" : 0.5,
        "camera_distance" : 20,
    }
    def __init__(self, *args, **kwargs):
        Camera.__init__(self, *args, **kwargs)
        self.unit_sun_vect = self.sun_vect/np.linalg.norm(self.sun_vect)

    def get_stroke_color(self, vmobject):
        return Color(rgb = self.get_shaded_rgb(
            color_to_rgb(vmobject.get_stroke_color()),
            normal_vect = self.get_unit_normal_vect(vmobject)
        ))

    def get_fill_color(self, vmobject):
        return Color(rgb = self.get_shaded_rgb(
            color_to_rgb(vmobject.get_fill_color()),
            normal_vect = self.get_unit_normal_vect(vmobject)
        ))

    def get_shaded_rgb(self, rgb, normal_vect):
        brightness = np.dot(normal_vect, self.unit_sun_vect)
        if brightness > 0:
            alpha = self.shading_factor*brightness
            return interpolate(rgb, np.ones(3), alpha)
        else:
            alpha = -self.shading_factor*brightness
            return interpolate(rgb, np.zeros(3), alpha)

    def get_unit_normal_vect(self, vmobject):
        anchors = vmobject.get_anchors()
        if len(anchors) < 3:
            return OUT
        normal = np.cross(anchors[1]-anchors[0], anchors[2]-anchors[1])
        if normal[2] < 0:
            normal = -normal
        length = np.linalg.norm(normal)
        if length == 0:
            return OUT
        return normal/length

    def display_multiple_vectorized_mobjects(self, vmobjects):
        def z_cmp(*vmobs):
            if all([hasattr(vm, "part_of_three_d_mobject") for vm in vmobs]):
                return cmp(*[
                    vm.get_edge_center(IN)[2]
                    for vm in vmobs
                ])
            else:
                return 0
        Camera.display_multiple_vectorized_mobjects(
            self, sorted(vmobjects, cmp = z_cmp)
        )


    def points_to_pixel_coords(self, points):
        distance_ratios = (self.camera_distance + points[:,2])/self.camera_distance
        scale_factors = interpolate(0, 1, distance_ratios)
        adjusted_points = np.array(points)
        for i in 0, 1:
            adjusted_points[:,i] *= scale_factors

        return Camera.points_to_pixel_coords(self, adjusted_points)


class ThreeDScene(Scene):
    CONFIG = {
        "camera_class" : ThreeDCamera,
    }

##############

class ThreeDMobject(VMobject):
    def __init__(self, **kwargs):
        VMobject.__init__(self, **kwargs)
        for submobject in self.submobject_family():
            submobject.part_of_three_d_mobject = True

class Cube(ThreeDMobject):
    CONFIG = {
        "fill_opacity" : 0.75,
        "fill_color" : BLUE,
        "stroke_width" : 0,
        "propogate_style_to_family" : True,
        "side_length" : 2,
    }
    def generate_points(self):
        for vect in IN, OUT, LEFT, RIGHT, UP, DOWN:
            face = Square(side_length = self.side_length)
            face.shift(self.side_length*OUT/2.0)
            face.apply_function(lambda p : np.dot(p, z_to_vector(vect).T))

            self.add(face)




























