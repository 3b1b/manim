from traceback import *

from scipy.spatial import ConvexHull

from manimlib.animation.composition import LaggedStartMap
from manimlib.animation.fading import FadeIn
from manimlib.animation.fading import FadeOut
from manimlib.animation.transform import Transform
from manimlib.constants import *
from manimlib.mobject.geometry import AnnularSector
from manimlib.mobject.geometry import Annulus
from manimlib.mobject.svg.svg_mobject import SVGMobject
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.types.vectorized_mobject import VectorizedPoint
from manimlib.utils.space_ops import angle_between_vectors
from manimlib.utils.space_ops import project_along_vector
from manimlib.utils.space_ops import rotate_vector
from manimlib.utils.space_ops import z_to_vector

LIGHT_COLOR = YELLOW
SHADOW_COLOR = BLACK
SWITCH_ON_RUN_TIME = 1.5
FAST_SWITCH_ON_RUN_TIME = 0.1
NUM_LEVELS = 30
NUM_CONES = 7  # in first lighthouse scene
NUM_VISIBLE_CONES = 5  # ibidem
ARC_TIP_LENGTH = 0.2
AMBIENT_FULL = 0.8
AMBIENT_DIMMED = 0.5
SPOTLIGHT_FULL = 0.8
SPOTLIGHT_DIMMED = 0.5
LIGHTHOUSE_HEIGHT = 0.8

DEGREES = TAU / 360


def inverse_power_law(maxint, scale, cutoff, exponent):
    return (lambda r: maxint * (cutoff / (r / scale + cutoff))**exponent)


def inverse_quadratic(maxint, scale, cutoff):
    return inverse_power_law(maxint, scale, cutoff, 2)


class SwitchOn(LaggedStartMap):
    CONFIG = {
        "lag_ratio": 0.2,
        "run_time": SWITCH_ON_RUN_TIME
    }

    def __init__(self, light, **kwargs):
        if (not isinstance(light, AmbientLight) and not isinstance(light, Spotlight)):
            raise Exception(
                "Only AmbientLights and Spotlights can be switched on")
        LaggedStartMap.__init__(
            self, FadeIn, light, **kwargs
        )


class SwitchOff(LaggedStartMap):
    CONFIG = {
        "lag_ratio": 0.2,
        "run_time": SWITCH_ON_RUN_TIME
    }

    def __init__(self, light, **kwargs):
        if (not isinstance(light, AmbientLight) and not isinstance(light, Spotlight)):
            raise Exception(
                "Only AmbientLights and Spotlights can be switched off")
        light.submobjects = light.submobjects[::-1]
        LaggedStartMap.__init__(self, FadeOut, light, **kwargs)
        light.submobjects = light.submobjects[::-1]


class Lighthouse(SVGMobject):
    CONFIG = {
        "file_name": "lighthouse",
        "height": LIGHTHOUSE_HEIGHT,
        "fill_color": WHITE,
        "fill_opacity": 1.0,
    }

    def move_to(self, point):
        self.next_to(point, DOWN, buff=0)


class AmbientLight(VMobject):

    # Parameters are:
    # * a source point
    # * an opacity function
    # * a light color
    # * a max opacity
    # * a radius (larger than the opacity's dropoff length)
    # * the number of subdivisions (levels, annuli)

    CONFIG = {
        "source_point": VectorizedPoint(location=ORIGIN, stroke_width=0, fill_opacity=0),
        "opacity_function": lambda r: 1.0 / (r + 1.0)**2,
        "color": LIGHT_COLOR,
        "max_opacity": 1.0,
        "num_levels": NUM_LEVELS,
        "radius": 5.0
    }

    def generate_points(self):
        # in theory, this method is only called once, right?
        # so removing submobs shd not be necessary
        #
        # Note: Usually, yes, it is only called within Mobject.__init__,
        # but there is no strong guarantee of that, and you may want certain
        # update functions to regenerate points here and there.
        for submob in self.submobjects:
            self.remove(submob)

        self.add(self.source_point)

        # create annuli
        self.radius = float(self.radius)
        dr = self.radius / self.num_levels
        for r in np.arange(0, self.radius, dr):
            alpha = self.max_opacity * self.opacity_function(r)
            annulus = Annulus(
                inner_radius=r,
                outer_radius=r + dr,
                color=self.color,
                fill_opacity=alpha
            )
            annulus.move_to(self.get_source_point())
            self.add(annulus)

    def move_source_to(self, point):
        # old_source_point = self.get_source_point()
        # self.shift(point - old_source_point)
        self.move_to(point)

        return self

    def get_source_point(self):
        return self.source_point.get_location()

    def dimming(self, new_alpha):
        old_alpha = self.max_opacity
        self.max_opacity = new_alpha
        for submob in self.submobjects:
            old_submob_alpha = submob.fill_opacity
            new_submob_alpha = old_submob_alpha * new_alpha / old_alpha
            submob.set_fill(opacity=new_submob_alpha)


class Spotlight(VMobject):
    CONFIG = {
        "source_point": VectorizedPoint(location=ORIGIN, stroke_width=0, fill_opacity=0),
        "opacity_function": lambda r: 1.0 / (r / 2 + 1.0)**2,
        "color": GREEN,  # LIGHT_COLOR,
        "max_opacity": 1.0,
        "num_levels": 10,
        "radius": 10.0,
        "screen": None,
        "camera_mob": None
    }

    def projection_direction(self):
        # Note: This seems reasonable, though for it to work you'd
        # need to be sure that any 3d scene including a spotlight
        # somewhere assigns that spotlights "camera" attribute
        # to be the camera associated with that scene.
        if self.camera_mob is None:
            return OUT
        else:
            [phi, theta, r] = self.camera_mob.get_center()
            v = np.array([np.sin(phi) * np.cos(theta),
                          np.sin(phi) * np.sin(theta), np.cos(phi)])
            return v  # /get_norm(v)

    def project(self, point):
        v = self.projection_direction()
        w = project_along_vector(point, v)
        return w

    def get_source_point(self):
        return self.source_point.get_location()

    def generate_points(self):
        self.submobjects = []

        self.add(self.source_point)

        if self.screen is not None:
            # look for the screen and create annular sectors
            lower_angle, upper_angle = self.viewing_angles(self.screen)
            self.radius = float(self.radius)
            dr = self.radius / self.num_levels
            lower_ray, upper_ray = self.viewing_rays(self.screen)

            for r in np.arange(0, self.radius, dr):
                new_sector = self.new_sector(r, dr, lower_angle, upper_angle)
                self.add(new_sector)

    def new_sector(self, r, dr, lower_angle, upper_angle):
        alpha = self.max_opacity * self.opacity_function(r)
        annular_sector = AnnularSector(
            inner_radius=r,
            outer_radius=r + dr,
            color=self.color,
            fill_opacity=alpha,
            start_angle=lower_angle,
            angle=upper_angle - lower_angle
        )
        # rotate (not project) it into the viewing plane
        rotation_matrix = z_to_vector(self.projection_direction())
        annular_sector.apply_matrix(rotation_matrix)
        # now rotate it inside that plane
        rotated_RIGHT = np.dot(RIGHT, rotation_matrix.T)
        projected_RIGHT = self.project(RIGHT)
        omega = angle_between_vectors(rotated_RIGHT, projected_RIGHT)
        annular_sector.rotate(omega, axis=self.projection_direction())
        annular_sector.move_arc_center_to(self.get_source_point())

        return annular_sector

    def viewing_angle_of_point(self, point):
        # as measured from the positive x-axis
        v1 = self.project(RIGHT)
        v2 = self.project(np.array(point) - self.get_source_point())
        absolute_angle = angle_between_vectors(v1, v2)
        # determine the angle's sign depending on their plane's
        # choice of orientation. That choice is set by the camera
        # position, i. e. projection direction

        if np.dot(self.projection_direction(), np.cross(v1, v2)) > 0:
            return absolute_angle
        else:
            return -absolute_angle

    def viewing_angles(self, screen):

        screen_points = screen.get_anchors()
        projected_screen_points = list(map(self.project, screen_points))

        viewing_angles = np.array(list(map(self.viewing_angle_of_point,
                                           projected_screen_points)))

        lower_angle = upper_angle = 0
        if len(viewing_angles) != 0:
            lower_angle = np.min(viewing_angles)
            upper_angle = np.max(viewing_angles)

        if upper_angle - lower_angle > TAU / 2:
            lower_angle, upper_angle = upper_angle, lower_angle + TAU
        return lower_angle, upper_angle

    def viewing_rays(self, screen):

        lower_angle, upper_angle = self.viewing_angles(screen)
        projected_RIGHT = self.project(
            RIGHT) / get_norm(self.project(RIGHT))
        lower_ray = rotate_vector(
            projected_RIGHT, lower_angle, axis=self.projection_direction())
        upper_ray = rotate_vector(
            projected_RIGHT, upper_angle, axis=self.projection_direction())

        return lower_ray, upper_ray

    def opening_angle(self):
        l, u = self.viewing_angles(self.screen)
        return u - l

    def start_angle(self):
        l, u = self.viewing_angles(self.screen)
        return l

    def stop_angle(self):
        l, u = self.viewing_angles(self.screen)
        return u

    def move_source_to(self, point):
        self.source_point.set_location(np.array(point))
        # self.source_point.move_to(np.array(point))
        # self.move_to(point)
        self.update_sectors()
        return self

    def update_sectors(self):
        if self.screen is None:
            return
        for submob in self.submobjects:
            if type(submob) == AnnularSector:
                lower_angle, upper_angle = self.viewing_angles(self.screen)
                # dr = submob.outer_radius - submob.inner_radius
                dr = self.radius / self.num_levels
                new_submob = self.new_sector(
                    submob.inner_radius, dr, lower_angle, upper_angle
                )
                # submob.points = new_submob.points
                # submob.set_fill(opacity = 10 * self.opacity_function(submob.outer_radius))
                Transform(submob, new_submob).update(1)

    def dimming(self, new_alpha):
        old_alpha = self.max_opacity
        self.max_opacity = new_alpha
        for submob in self.submobjects:
            # Note: Maybe it'd be best to have a Shadow class so that the
            # type can be checked directly?
            if type(submob) != AnnularSector:
                # it's the shadow, don't dim it
                continue
            old_submob_alpha = submob.fill_opacity
            new_submob_alpha = old_submob_alpha * new_alpha / old_alpha
            submob.set_fill(opacity=new_submob_alpha)

    def change_opacity_function(self, new_f):
        self.opacity_function = new_f
        dr = self.radius / self.num_levels

        sectors = []
        for submob in self.submobjects:
            if type(submob) == AnnularSector:
                sectors.append(submob)

        for (r, submob) in zip(np.arange(0, self.radius, dr), sectors):
            if type(submob) != AnnularSector:
                # it's the shadow, don't dim it
                continue
            alpha = self.opacity_function(r)
            submob.set_fill(opacity=alpha)

# Warning: This class is likely quite buggy.


class LightSource(VMobject):
    # combines:
    # a lighthouse
    # an ambient light
    # a spotlight
    # and a shadow
    CONFIG = {
        "source_point": VectorizedPoint(location=ORIGIN, stroke_width=0, fill_opacity=0),
        "color": LIGHT_COLOR,
        "num_levels": 10,
        "radius": 10.0,
        "screen": None,
        "opacity_function": inverse_quadratic(1, 2, 1),
        "max_opacity_ambient": AMBIENT_FULL,
        "max_opacity_spotlight": SPOTLIGHT_FULL,
        "camera_mob": None
    }

    def generate_points(self):

        self.add(self.source_point)

        self.lighthouse = Lighthouse()
        self.ambient_light = AmbientLight(
            source_point=VectorizedPoint(location=self.get_source_point()),
            color=self.color,
            num_levels=self.num_levels,
            radius=self.radius,
            opacity_function=self.opacity_function,
            max_opacity=self.max_opacity_ambient
        )
        if self.has_screen():
            self.spotlight = Spotlight(
                source_point=VectorizedPoint(location=self.get_source_point()),
                color=self.color,
                num_levels=self.num_levels,
                radius=self.radius,
                screen=self.screen,
                opacity_function=self.opacity_function,
                max_opacity=self.max_opacity_spotlight,
                camera_mob=self.camera_mob
            )
        else:
            self.spotlight = Spotlight()

        self.shadow = VMobject(fill_color=SHADOW_COLOR,
                               fill_opacity=1.0, stroke_color=BLACK)
        self.lighthouse.next_to(self.get_source_point(), DOWN, buff=0)
        self.ambient_light.move_source_to(self.get_source_point())

        if self.has_screen():
            self.spotlight.move_source_to(self.get_source_point())
            self.update_shadow()

        self.add(self.ambient_light, self.spotlight,
                 self.lighthouse, self.shadow)

    def has_screen(self):
        if self.screen is None:
            return False
        elif np.size(self.screen.points) == 0:
            return False
        else:
            return True

    def dim_ambient(self):
        self.set_max_opacity_ambient(AMBIENT_DIMMED)

    def set_max_opacity_ambient(self, new_opacity):
        self.max_opacity_ambient = new_opacity
        self.ambient_light.dimming(new_opacity)

    def dim_spotlight(self):
        self.set_max_opacity_spotlight(SPOTLIGHT_DIMMED)

    def set_max_opacity_spotlight(self, new_opacity):
        self.max_opacity_spotlight = new_opacity
        self.spotlight.dimming(new_opacity)

    def set_camera_mob(self, new_cam_mob):
        self.camera_mob = new_cam_mob
        self.spotlight.camera_mob = new_cam_mob

    def set_screen(self, new_screen):
        if self.has_screen():
            self.spotlight.screen = new_screen
        else:
            # Note: See below
            index = self.submobjects.index(self.spotlight)
            # camera_mob = self.spotlight.camera_mob
            self.remove(self.spotlight)
            self.spotlight = Spotlight(
                source_point=VectorizedPoint(location=self.get_source_point()),
                color=self.color,
                num_levels=self.num_levels,
                radius=self.radius,
                screen=new_screen,
                camera_mob=self.camera_mob,
                opacity_function=self.opacity_function,
                max_opacity=self.max_opacity_spotlight,
            )
            self.spotlight.move_source_to(self.get_source_point())

            # Note: This line will make spotlight show up at the end
            # of the submojects list, which can make it show up on
            # top of the shadow. To make it show up in the
            # same spot, you could try the following line,
            # where "index" is what I defined above:
            self.submobjects.insert(index, self.spotlight)
            # self.add(self.spotlight)

        # in any case
        self.screen = new_screen

    def move_source_to(self, point):
        apoint = np.array(point)
        v = apoint - self.get_source_point()
        # Note: As discussed, things stand to behave better if source
        # point is a submobject, so that it automatically interpolates
        # during an animation, and other updates can be defined wrt
        # that source point's location
        self.source_point.set_location(apoint)
        # self.lighthouse.next_to(apoint,DOWN,buff = 0)
        # self.ambient_light.move_source_to(apoint)
        self.lighthouse.shift(v)
        # self.ambient_light.shift(v)
        self.ambient_light.move_source_to(apoint)
        if self.has_screen():
            self.spotlight.move_source_to(apoint)
        self.update()
        return self

    def change_spotlight_opacity_function(self, new_of):
        self.spotlight.change_opacity_function(new_of)

    def set_radius(self, new_radius):
        self.radius = new_radius
        self.ambient_light.radius = new_radius
        self.spotlight.radius = new_radius

    def update(self):
        self.update_lighthouse()
        self.update_ambient()
        self.spotlight.update_sectors()
        self.update_shadow()

    def update_lighthouse(self):
        self.lighthouse.move_to(self.get_source_point())
        # new_lh = Lighthouse()
        # new_lh.move_to(ORIGIN)
        # new_lh.apply_matrix(self.rotation_matrix())
        # new_lh.shift(self.get_source_point())
        # self.lighthouse.submobjects = new_lh.submobjects

    def update_ambient(self):
        new_ambient_light = AmbientLight(
            source_point=VectorizedPoint(location=ORIGIN),
            color=self.color,
            num_levels=self.num_levels,
            radius=self.radius,
            opacity_function=self.opacity_function,
            max_opacity=self.max_opacity_ambient
        )
        new_ambient_light.apply_matrix(self.rotation_matrix())
        new_ambient_light.move_source_to(self.get_source_point())
        self.ambient_light.submobjects = new_ambient_light.submobjects

    def get_source_point(self):
        return self.source_point.get_location()

    def rotation_matrix(self):

        if self.camera_mob is None:
            return np.eye(3)

        phi = self.camera_mob.get_center()[0]
        theta = self.camera_mob.get_center()[1]

        R1 = np.array([
            [1, 0, 0],
            [0, np.cos(phi), -np.sin(phi)],
            [0, np.sin(phi), np.cos(phi)]
        ])

        R2 = np.array([
            [np.cos(theta + TAU / 4), -np.sin(theta + TAU / 4), 0],
            [np.sin(theta + TAU / 4), np.cos(theta + TAU / 4), 0],
            [0, 0, 1]
        ])

        R = np.dot(R2, R1)
        return R

    def update_shadow(self):
        point = self.get_source_point()
        projected_screen_points = []
        if not self.has_screen():
            return
        for point in self.screen.get_anchors():
            projected_screen_points.append(self.spotlight.project(point))

        projected_source = project_along_vector(
            self.get_source_point(), self.spotlight.projection_direction())

        projected_point_cloud_3d = np.append(
            projected_screen_points,
            np.reshape(projected_source, (1, 3)),
            axis=0
        )
        # z_to_vector(self.spotlight.projection_direction())
        rotation_matrix = self.rotation_matrix()
        back_rotation_matrix = rotation_matrix.T  # i. e. its inverse

        rotated_point_cloud_3d = np.dot(
            projected_point_cloud_3d, back_rotation_matrix.T)
        # these points now should all have z = 0

        point_cloud_2d = rotated_point_cloud_3d[:, :2]
        # now we can compute the convex hull
        hull_2d = ConvexHull(point_cloud_2d)  # guaranteed to run ccw
        hull = []

        # we also need the projected source point
        source_point_2d = np.dot(self.spotlight.project(
            self.get_source_point()), back_rotation_matrix.T)[:2]

        index = 0
        for point in point_cloud_2d[hull_2d.vertices]:
            if np.all(np.abs(point - source_point_2d) < 1.0e-6):
                source_index = index
                index += 1
                continue
            point_3d = np.array([point[0], point[1], 0])
            hull.append(point_3d)
            index += 1

        hull_mobject = VMobject()
        hull_mobject.set_points_as_corners(hull)
        hull_mobject.apply_matrix(rotation_matrix)

        anchors = hull_mobject.get_anchors()

        # add two control points for the outer cone
        if np.size(anchors) == 0:
            self.shadow.points = []
            return

        ray1 = anchors[source_index - 1] - projected_source
        ray1 = ray1 / get_norm(ray1) * 100

        ray2 = anchors[source_index] - projected_source
        ray2 = ray2 / get_norm(ray2) * 100
        outpoint1 = anchors[source_index - 1] + ray1
        outpoint2 = anchors[source_index] + ray2

        new_anchors = anchors[:source_index]
        new_anchors = np.append(new_anchors, np.array(
            [outpoint1, outpoint2]), axis=0)
        new_anchors = np.append(new_anchors, anchors[source_index:], axis=0)
        self.shadow.set_points_as_corners(new_anchors)

        # shift it closer to the camera so it is in front of the spotlight
        self.shadow.mark_paths_closed = True


# Redefining what was once a ContinualAnimation class
# as a function
def ScreenTracker(light_source):
    light_source.add_updater(lambda m: m.update())
    return light_source
