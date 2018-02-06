from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.continual_animation import *

from animation.playground import *
from topics.geometry import *
from topics.functions import *
from scene import Scene
from camera import Camera
from mobject.svg_mobject import *
from topics.three_dimensions import *

from scipy.spatial import ConvexHull

import traceback

LIGHT_COLOR = YELLOW
SWITCH_ON_RUN_TIME = 1.5
FAST_SWITCH_ON_RUN_TIME = 0.1
NUM_LEVELS = 30
NUM_CONES = 7 # in first lighthouse scene
NUM_VISIBLE_CONES = 5 # ibidem
ARC_TIP_LENGTH = 0.2
AMBIENT_FULL = 0.5
AMBIENT_DIMMED = 0.2
SPOTLIGHT_FULL = 0.9
SPOTLIGHT_DIMMED = 0.2

LIGHT_COLOR = YELLOW
DEGREES = TAU/360

inverse_power_law = lambda maxint,scale,cutoff,exponent: \
    (lambda r: maxint * (cutoff/(r/scale+cutoff))**exponent)
inverse_quadratic = lambda maxint,scale,cutoff: inverse_power_law(maxint,scale,cutoff,2)



class LightSource(VMobject):

    # combines:
    # a lighthouse
    # an ambient light
    # a spotlight
    # and a shadow

    CONFIG = {
        "source_point": ORIGIN,
        "color": LIGHT_COLOR,
        "num_levels": 10,
        "radius": 5,
        "screen": None,
        "opacity_function": inverse_quadratic(1,2,1),
        "max_opacity_ambient": AMBIENT_FULL,
        "max_opacity_spotlight": SPOTLIGHT_FULL
    }

    def generate_points(self):
        print "LightSource.generate_points"
        self.lighthouse = Lighthouse()
        self.ambient_light = AmbientLight(
            source_point = self.source_point,
            color = self.color,
            num_levels = self.num_levels,
            radius = self.radius,
            opacity_function = self.opacity_function,
            max_opacity = self.max_opacity_ambient
        )
        if self.has_screen():
            self.spotlight = Spotlight(
                source_point = self.source_point,
                color = self.color,
                num_levels = self.num_levels,
                radius = self.radius,
                screen = self.screen,
                opacity_function = self.opacity_function,
                max_opacity = self.max_opacity_spotlight
            )
        else:
            self.spotlight = Spotlight()

        self.shadow = VMobject(fill_color = "BLACK", fill_opacity = 1.0, stroke_color = BLACK)
        self.lighthouse.next_to(self.source_point,DOWN,buff = 0)
        self.ambient_light.move_source_to(self.source_point)

        if self.has_screen():
            self.spotlight.move_source_to(self.source_point)
            self.update_shadow()

        self.add(self.ambient_light,self.spotlight,self.lighthouse, self.shadow)

    def has_screen(self):
        return (self.screen != None)

    def dim_ambient(self):
        self.set_max_opacity_ambient(AMBIENT_DIMMED)

    def set_max_opacity_ambient(self,new_opacity):
        self.max_opacity_ambient = new_opacity
        self.ambient_light.dimming(new_opacity)

    def dim_spotlight(self):
        self.set_max_opacity_spotlight(SPOTLIGHT_DIMMED)

    def set_max_opacity_spotlight(self,new_opacity):
        self.max_opacity_spotlight = new_opacity
        self.spotlight.dimming(new_opacity)

    def set_screen(self, new_screen):
        if self.has_screen():
            self.spotlight.screen = new_screen
        else:
            self.remove(self.spotlight)
            self.spotlight = Spotlight(
                source_point = self.source_point,
                color = self.color,
                num_levels = self.num_levels,
                radius = self.radius,
                screen = new_screen
            )
            self.spotlight.move_source_to(self.source_point)
            self.add(self.spotlight)
        
        # in any case
        self.screen = new_screen




    def move_source_to(self,point):
        print "LightSource.move_source_to"
        apoint = np.array(point)
        v = apoint - self.source_point
        self.source_point = apoint
        self.lighthouse.next_to(apoint,DOWN,buff = 0)
        self.ambient_light.move_source_to(apoint)
        #if self.has_screen():
        #    self.spotlight.move_source_to(apoint)
        #self.update()
        return self






        
    def set_radius(self,new_radius):
        self.radius = new_radius
        self.ambient_light.radius = new_radius
        self.spotlight.radius = new_radius

    def update(self):
        print "LightSource.update"
        self.spotlight.update_sectors()
        self.update_shadow()


    def update_shadow(self):
        
        point = self.source_point
        projected_screen_points = []
        if not self.has_screen():
            return
        for point in self.screen.get_anchors():
            projected_screen_points.append(self.spotlight.project(point))

        projected_source = project_along_vector(self.source_point,self.spotlight.projection_direction())

        projected_point_cloud_3d = np.append(projected_screen_points,
            np.reshape(projected_source,(1,3)),axis = 0)
        rotation_matrix = z_to_vector(self.spotlight.projection_direction())
        back_rotation_matrix = rotation_matrix.T # i. e. its inverse

        rotated_point_cloud_3d = np.dot(projected_point_cloud_3d,back_rotation_matrix.T)
        # these points now should all have z = 0
        point_cloud_2d = rotated_point_cloud_3d[:,:2]
        # now we can compute the convex hull
        hull_2d = ConvexHull(point_cloud_2d) # guaranteed to run ccw
        hull = []

        # we also need the projected source point
        source_point_2d = np.dot(self.spotlight.project(self.source_point),back_rotation_matrix.T)[:2]
        
        index = 0
        for point in point_cloud_2d[hull_2d.vertices]:
            if np.all(point - source_point_2d < 1.0e-6):
                source_index = index
                continue
            point_3d = np.array([point[0], point[1], 0])
            hull.append(point_3d)
            index += 1

        index = source_index
        
        hull_mobject = VMobject()
        hull_mobject.set_points_as_corners(hull)
        hull_mobject.apply_matrix(rotation_matrix)


        anchors = hull_mobject.get_anchors()

        # add two control points for the outer cone


        ray1 = anchors[index - 1] - projected_source
        ray1 = ray1/np.linalg.norm(ray1) * 100
        ray2 = anchors[index] - projected_source
        ray2 = ray2/np.linalg.norm(ray2) * 100
        outpoint1 = anchors[index - 1] + ray1
        outpoint2 = anchors[index] + ray2

        new_anchors = anchors[:index]
        new_anchors = np.append(new_anchors,np.array([outpoint1, outpoint2]),axis = 0)
        new_anchors = np.append(new_anchors,anchors[index:],axis = 0)
        self.shadow.set_points_as_corners(new_anchors)

        # shift it one unit closer to the camera so it is in front of the spotlight
        #self.shadow.shift(-500*self.projection_direction())
        self.shadow.mark_paths_closed = True



class SwitchOn(LaggedStart):
    CONFIG = {
        "lag_ratio": 0.2,
        "run_time": SWITCH_ON_RUN_TIME
    }

    def __init__(self, light, **kwargs):
        if (not isinstance(light,AmbientLight) and not isinstance(light,Spotlight)):
            raise Exception("Only AmbientLights and Spotlights can be switched on")
        LaggedStart.__init__(self,
            FadeIn, light, **kwargs)


class SwitchOff(LaggedStart):
    CONFIG = {
        "lag_ratio": 0.2,
        "run_time": SWITCH_ON_RUN_TIME
    }

    def __init__(self, light, **kwargs):
        if (not isinstance(light,AmbientLight) and not isinstance(light,Spotlight)):
            raise Exception("Only AmbientLights and Spotlights can be switched off")
        light.submobjects = light.submobjects[::-1]
        LaggedStart.__init__(self,
            FadeOut, light, **kwargs)
        light.submobjects = light.submobjects[::-1]




class Lighthouse(SVGMobject):
    CONFIG = {
        "file_name" : "lighthouse",
        "height" : 0.5
    }

    def move_to(self,point):
        self.next_to(point, DOWN, buff = 0)


class AmbientLight(VMobject):

    # Parameters are:
    # * a source point
    # * an opacity function
    # * a light color
    # * a max opacity
    # * a radius (larger than the opacity's dropoff length)
    # * the number of subdivisions (levels, annuli)

    CONFIG = {
        "source_point" : ORIGIN,
        "opacity_function" : lambda r : 1.0/(r+1.0)**2,
        "color" : LIGHT_COLOR,
        "max_opacity" : 1.0,
        "num_levels" : 10,
        "radius" : 5.0
    }

    def generate_points(self):
        print "AmbientLight.generate_points"
        self.source_point = np.array(self.source_point)

        # in theory, this method is only called once, right?
        # so removing submobs shd not be necessary
        for submob in self.submobjects:
            self.remove(submob)

        # create annuli
        self.radius = float(self.radius)
        dr = self.radius / self.num_levels
        for r in np.arange(0, self.radius, dr):
            alpha = self.max_opacity * self.opacity_function(r)
            annulus = Annulus(
                inner_radius = r,
                outer_radius = r + dr,
                color = self.color,
                fill_opacity = alpha
            )
            annulus.move_arc_center_to(self.source_point)
            self.add(annulus)



    def move_source_to(self,point):


        for line in traceback.format_stack():
            print line.strip()

        print "AmbientLight.move_source_to blablub"
        v = np.array(point) - self.source_point
        print "test"
        self.source_point = np.array(point)
        self.shift(v)
        return self







    def dimming(self,new_alpha):
        old_alpha = self.max_opacity
        self.max_opacity = new_alpha
        for submob in self.submobjects:
            old_submob_alpha = submob.fill_opacity
            new_submob_alpha = old_submob_alpha * new_alpha / old_alpha
            submob.set_fill(opacity = new_submob_alpha)


class Spotlight(VMobject):

    CONFIG = {
        "source_point" : ORIGIN,
        "opacity_function" : lambda r : 1.0/(r/2+1.0)**2,
        "color" : LIGHT_COLOR,
        "max_opacity" : 1.0,
        "num_levels" : 10,
        "radius" : 5.0,
        "screen" : None,
        "camera": None
    }

    def projection_direction(self):
        if self.camera == None:
            return OUT
        else:
            v = self.camera.get_cartesian_coords()
            return v/np.linalg.norm(v)

    def project(self,point):
        v = self.projection_direction()
        w = project_along_vector(point,v)
        return w

    def generate_points(self):

        self.submobjects = []

        if self.screen != None:
            # look for the screen and create annular sectors
            lower_angle, upper_angle = self.viewing_angles(self.screen)
            self.radius = float(self.radius)
            dr = self.radius / self.num_levels
            lower_ray, upper_ray = self.viewing_rays(self.screen)

            for r in np.arange(0, self.radius, dr):
                new_sector = self.new_sector(r,dr,lower_angle,upper_angle)
                self.add(new_sector)

        #self.update_shadow(point = self.source_point)
        #self.add_to_back(self.shadow)

    def new_sector(self,r,dr,lower_angle,upper_angle):

        alpha = self.max_opacity * self.opacity_function(r)
        annular_sector = AnnularSector(
            inner_radius = r,
            outer_radius = r + dr,
            color = self.color,
            fill_opacity = alpha,
            start_angle = lower_angle,
            angle = upper_angle - lower_angle
        )
        # rotate (not project) it into the viewing plane
        rotation_matrix = z_to_vector(self.projection_direction())
        annular_sector.apply_matrix(rotation_matrix)
        # now rotate it inside that plane
        rotated_RIGHT = np.dot(RIGHT, rotation_matrix.T)
        projected_RIGHT = self.project(RIGHT)
        omega = angle_between_vectors(rotated_RIGHT,projected_RIGHT)
        annular_sector.rotate(omega, axis = self.projection_direction())
        annular_sector.move_arc_center_to(self.source_point)

        return annular_sector

    def viewing_angle_of_point(self,point):
        # as measured from the positive x-axis
        v1 = self.project(RIGHT)
        v2 = self.project(np.array(point) - self.source_point)
        absolute_angle = angle_between_vectors(v1, v2)
        # determine the angle's sign depending on their plane's
        # choice of orientation. That choice is set by the camera
        # position, i. e. projection direction
        if np.dot(self.projection_direction(),np.cross(v1, v2)) > 0:
            return absolute_angle
        else:
            return -absolute_angle


    def viewing_angles(self,screen):

        screen_points = screen.get_anchors()
        projected_screen_points = map(self.project,screen_points)

        viewing_angles = np.array(map(self.viewing_angle_of_point,
            projected_screen_points))
        lower_angle = upper_angle = 0
        if len(viewing_angles) != 0:
            lower_angle = np.min(viewing_angles)
            upper_angle = np.max(viewing_angles)

        return lower_angle, upper_angle

    def viewing_rays(self,screen):

        lower_angle, upper_angle = self.viewing_angles(screen)
        projected_RIGHT = self.project(RIGHT)/np.linalg.norm(self.project(RIGHT))
        lower_ray = rotate_vector(projected_RIGHT,lower_angle, axis = self.projection_direction())
        upper_ray = rotate_vector(projected_RIGHT,upper_angle, axis = self.projection_direction())
        
        return lower_ray, upper_ray


    def opening_angle(self):
        l,u = self.viewing_angles(self.screen)
        return u - l

    def start_angle(self):
        l,u = self.viewing_angles(self.screen)
        return l

    def stop_angle(self):
        l,u = self.viewing_angles(self.screen)
        return u

    def move_source_to(self,point):
        self.source_point = np.array(point)
        self.update_sectors()
        return self


    def update_sectors(self):
        if self.screen == None:
            return
        for submob in self.submobject_family():
            if type(submob) == AnnularSector:
                lower_angle, upper_angle = self.viewing_angles(self.screen)
                dr = submob.outer_radius - submob.inner_radius
                new_submob = self.new_sector(submob.inner_radius,dr,lower_angle,upper_angle)
                submob.points = new_submob.points






    def dimming(self,new_alpha):
        old_alpha = self.max_opacity
        self.max_opacity = new_alpha
        for submob in self.submobjects:
            if type(submob) != AnnularSector:
                # it's the shadow, don't dim it
                continue
            old_submob_alpha = submob.fill_opacity
            new_submob_alpha = old_submob_alpha * new_alpha/old_alpha
            submob.set_fill(opacity = new_submob_alpha)

    def change_opacity_function(self,new_f):
        self.opacity_function = new_f
        dr = self.radius/self.num_levels

        sectors = []
        for submob in self.submobjects:
            if type(submob) == AnnularSector:
                sectors.append(submob)

        for (r,submob) in zip(np.arange(0,self.radius,dr),sectors):
            if type(submob) != AnnularSector:
                # it's the shadow, don't dim it
                continue
            alpha = self.opacity_function(r)
            submob.set_fill(opacity = alpha)



class ScreenTracker(ContinualAnimation):

    def update_mobject(self, dt):
        self.mobject.update()
        
