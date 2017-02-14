
from helpers import *

from scene import Scene
from camera import Camera

class ThreeDCamera(Camera):
    CONFIG = {
        "sun_vect" : UP+LEFT,
        "shading_factor" : 0.5,
    }
    def __init__(self, *args, **kwargs):
        Camera.__init__(self, *args, **kwargs)
        self.unit_sun_vect = self.sun_vect/np.linalg.norm(self.sun_vect)

    def display_multiple_vectorized_mobjects(self, vmobjects):
        def cmp_vmobs(vm1, vm2):
            return cmp(vm1.get_center()[2], vm2.get_center()[2])
        Camera.display_multiple_vectorized_mobjects(
            self, 
            sorted(vmobjects, cmp = cmp_vmobs)
        )

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


class ThreeDScene(Scene):
    CONFIG = {
        "camera_class" : ThreeDCamera,
    }






























