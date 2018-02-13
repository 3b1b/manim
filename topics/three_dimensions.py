
from helpers import *

from mobject.vectorized_mobject import VGroup, VMobject, VectorizedPoint
from topics.geometry import Square, Line
from scene import Scene
from camera import Camera
from animation.continual_animation import AmbientMovement
from animation.transform import ApplyMethod

class CameraWithPerspective(Camera):
    CONFIG = {
        "camera_distance" : 20,
    }
    def points_to_pixel_coords(self, points):
        distance_ratios = np.divide(
            self.camera_distance,
            self.camera_distance - points[:,2]
        )
        scale_factors = interpolate(0, 1, distance_ratios)
        adjusted_points = np.array(points)
        for i in 0, 1:
            adjusted_points[:,i] *= scale_factors

        return Camera.points_to_pixel_coords(self, adjusted_points)

class ThreeDCamera(CameraWithPerspective):
    CONFIG = {
        "sun_vect" : 5*UP+LEFT,
        "shading_factor" : 0.2,
        "distance" : 5.,
        "default_distance" : 5.,
        "phi" : 0, #Angle off z axis
        "theta" : -TAU/4, #Rotation about z axis
    }
    def __init__(self, *args, **kwargs):
        Camera.__init__(self, *args, **kwargs)
        self.unit_sun_vect = self.sun_vect/np.linalg.norm(self.sun_vect)
        ## rotation_mobject lives in the phi-theta-distance space
        self.rotation_mobject = VectorizedPoint()
        ## moving_center lives in the x-y-z space
        ## It representes the center of rotation
        self.moving_center = VectorizedPoint(self.space_center)
        self.set_position(self.phi, self.theta, self.distance)

    def modified_rgb(self, vmobject, rgb):
        if should_shade_in_3d(vmobject):
            return self.get_shaded_rgb(rgb, self.get_unit_normal_vect(vmobject))
        else:
            return rgb

    def get_stroke_rgb(self, vmobject):
        return self.modified_rgb(vmobject, vmobject.get_stroke_rgb())

    def get_fill_rgb(self, vmobject):
        return self.modified_rgb(vmobject, vmobject.get_fill_rgb())

    def get_shaded_rgb(self, rgb, normal_vect):
        brightness = np.dot(normal_vect, self.unit_sun_vect)**2
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
        camera_point = self.spherical_coords_to_point(
            *self.get_spherical_coords()
        )
        def z_cmp(*vmobs):
            # Compare to three dimensional mobjects based on 
            # how close they are to the camera
            # return cmp(*[
            #     -np.linalg.norm(vm.get_center()-camera_point)
            #     for vm in vmobs
            # ])
            three_d_status = map(should_shade_in_3d, vmobs)
            has_points = [vm.get_num_points() > 0 for vm in vmobs]
            if all(three_d_status) and all(has_points):
                cmp_vect = self.get_unit_normal_vect(vmobs[1])
                return cmp(*[
                    np.dot(vm.get_center(), cmp_vect)
                    for vm in vmobs
                ])
            else:
                return 0
        Camera.display_multiple_vectorized_mobjects(
            self, sorted(vmobjects, cmp = z_cmp)
        )

    def get_spherical_coords(self, phi = None, theta = None, distance = None):
        curr_phi, curr_theta, curr_d = self.rotation_mobject.points[0]
        if phi is None: phi = curr_phi
        if theta is None: theta = curr_theta
        if distance is None: distance = curr_d
        return np.array([phi, theta, distance])

    def get_cartesian_coords(self, phi = None, theta = None, distance = None):
        spherical_coords_array = self.get_spherical_coords(phi,theta,distance)
        phi2 = spherical_coords_array[0]
        theta2 = spherical_coords_array[1]
        d2 = spherical_coords_array[2]
        return self.spherical_coords_to_point(phi2,theta2,d2)

    def get_phi(self):
        return self.get_spherical_coords()[0]

    def get_theta(self):
        return self.get_spherical_coords()[1]

    def get_distance(self):
        return self.get_spherical_coords()[2]

    def spherical_coords_to_point(self, phi, theta, distance):
        return distance*np.array([
            np.sin(phi)*np.cos(theta),
            np.sin(phi)*np.sin(theta),
            np.cos(phi)
        ])

    def get_center_of_rotation(self, x = None, y = None, z = None):
        curr_x, curr_y, curr_z = self.moving_center.points[0]
        if x is None:
            x = curr_x
        if y is None:
            y = curr_y
        if z is None:
            z = curr_z
        return np.array([x, y, z])

    def set_position(self, phi = None, theta = None, distance = None,
                     center_x = None, center_y = None, center_z = None):
        point = self.get_spherical_coords(phi, theta, distance)
        self.rotation_mobject.move_to(point)
        self.phi, self.theta, self.distance = point
        center_of_rotation = self.get_center_of_rotation(center_x, center_y, center_z)
        self.moving_center.move_to(center_of_rotation)
        self.space_center = self.moving_center.points[0]

    def get_view_transformation_matrix(self):
        return (self.default_distance / self.get_distance()) * np.dot(
            rotation_matrix(self.get_phi(), LEFT),
            rotation_about_z(-self.get_theta() - np.pi/2),
        )

    def points_to_pixel_coords(self, points):
        matrix = self.get_view_transformation_matrix()
        new_points = np.dot(points, matrix.T)
        self.space_center = self.moving_center.points[0]

        return Camera.points_to_pixel_coords(self, new_points)

class ThreeDScene(Scene):
    CONFIG = {
        "camera_class" : ThreeDCamera,
        "ambient_camera_rotation" : None,
    }

    def set_camera_position(self, phi = None, theta = None, distance = None,
                            center_x = None, center_y = None, center_z = None):
        self.camera.set_position(phi, theta, distance, center_x, center_y, center_z)

    def begin_ambient_camera_rotation(self, rate = 0.01):
        self.ambient_camera_rotation = AmbientMovement(
            self.camera.rotation_mobject,
            direction = UP,
            rate = rate
        )
        self.add(self.ambient_camera_rotation)

    def stop_ambient_camera_rotation(self):
        if self.ambient_camera_rotation is not None:
            self.remove(self.ambient_camera_rotation)
        self.ambient_camera_rotation = None

    def move_camera(
        self,
        phi = None, theta = None, distance = None,
        center_x = None, center_y = None, center_z = None,
        added_anims = [],
        **kwargs
        ):
        target_point = self.camera.get_spherical_coords(phi, theta, distance)
        movement = ApplyMethod(
            self.camera.rotation_mobject.move_to,
            target_point,
            **kwargs
        )
        target_center = self.camera.get_center_of_rotation(center_x, center_y, center_z)
        movement_center = ApplyMethod(
            self.camera.moving_center.move_to,
            target_center,
            **kwargs
        )
        is_camera_rotating = self.ambient_camera_rotation in self.continual_animations
        if is_camera_rotating:
            self.remove(self.ambient_camera_rotation)
        self.play(movement, movement_center, *added_anims)
        target_point = self.camera.get_spherical_coords(phi, theta, distance)
        if is_camera_rotating:
            self.add(self.ambient_camera_rotation)

    def get_moving_mobjects(self, *animations):
        moving_mobjects = Scene.get_moving_mobjects(self, *animations)
        if self.camera.rotation_mobject in moving_mobjects:
            return list_update(self.mobjects, moving_mobjects)
        return moving_mobjects

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
        "fill_opacity" : 0.75,
        "fill_color" : BLUE,
        "stroke_width" : 0,
        "propagate_style_to_family" : True,
        "side_length" : 2,
    }
    def generate_points(self):
        for vect in IN, OUT, LEFT, RIGHT, UP, DOWN:
            face = Square(side_length = self.side_length)
            face.shift(self.side_length*OUT/2.0)
            face.apply_function(lambda p : np.dot(p, z_to_vector(vect).T))

            self.add(face)

class Prism(Cube):
    CONFIG = {
        "dimensions" : [3, 2, 1]
    }
    def generate_points(self):
        Cube.generate_points(self)
        for dim, value in enumerate(self.dimensions):
            self.rescale_to_fit(value, dim, stretch = True)


























