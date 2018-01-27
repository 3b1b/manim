#!/usr/bin/env python

from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *
from mobject.point_cloud_mobject import PointCloudDot

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.continual_animation import *
from animation.playground import *

from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.number_line import *
from topics.combinatorics import *
from scene import Scene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

from mobject.vectorized_mobject import *

## To watch one of these scenes, run the following:
## python extract_scene.py -p file_name <SceneName>

LIGHT_COLOR = YELLOW
DEGREES = 360/TAU
SWITCH_ON_RUN_TIME = 1.5


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

        # in theory, this method is only called once, right?
        # so removing submobs shd not be necessary
        for submob in self.submobjects:
            self.remove(submob)

        # create annuli
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
        self.shift(point - self.source_point)
        self.source_point = np.array(point)
        # for submob in self.submobjects:
        #      if type(submob) == Annulus:
        #         submob.shift(self.source_point - submob.get_center())

    def dimming(self,new_alpha):
        old_alpha = self.max_opacity
        self.max_opacity = new_alpha
        for submob in self.submobjects:
            old_submob_alpha = submob.fill_opacity
            new_submob_alpha = old_submob_alpha * new_alpha/old_alpha
            submob.set_fill(opacity = new_submob_alpha)


class Spotlight(VMobject):

    CONFIG = {
        "source_point" : ORIGIN,
        "opacity_function" : lambda r : 1.0/(r+1.0)**2,
        "color" : LIGHT_COLOR,
        "max_opacity" : 1.0,
        "num_levels" : 10,
        "radius" : 5.0,
        "screen" : None,
        "shadow" : VMobject(fill_color = RED, stroke_width = 0, fill_opacity = 1.0)
    }

    def track_screen(self):
        self.generate_points()

    def generate_points(self):

        for submob in self.submobjects:
            self.remove(submob)

        if self.screen != None:
            # look for the screen and create annular sectors
            lower_angle, upper_angle = self.viewing_angles(self.screen)
            dr = self.radius / self.num_levels
            for r in np.arange(0, self.radius, dr):
                alpha = self.max_opacity * self.opacity_function(r)
                annular_sector = AnnularSector(
                    inner_radius = r,
                    outer_radius = r + dr,
                    color = self.color,
                    fill_opacity = alpha,
                    start_angle = lower_angle,
                    angle = upper_angle - lower_angle
                )
                annular_sector.move_arc_center_to(self.source_point)
                self.add(annular_sector)

        self.update_shadow(point = self.source_point)
        self.add(self.shadow)


    def viewing_angle_of_point(self,point):
        distance_vector = point - self.source_point
        angle = angle_of_vector(distance_vector)
        return angle

    def viewing_angles(self,screen):

        viewing_angles = np.array(map(self.viewing_angle_of_point,
            screen.get_anchors()))
        lower_angle = upper_angle = 0
        if len(viewing_angles) != 0:
            lower_angle = np.min(viewing_angles)
            upper_angle = np.max(viewing_angles)
            
        return lower_angle, upper_angle

    def move_source_to(self,point):
        self.source_point = np.array(point)
        self.recalculate_sectors(point = point, screen = self.screen)
        self.update_shadow(point = point)

    def recalculate_sectors(self, point = ORIGIN, screen = None):
        if screen == None:
            return
        for submob in self.submobject_family():
            if type(submob) == AnnularSector:
                lower_angle, upper_angle = self.viewing_angles(screen)
                new_submob = AnnularSector(
                    start_angle = lower_angle,
                    angle = upper_angle - lower_angle,
                    inner_radius = submob.inner_radius,
                    outer_radius = submob.outer_radius
                )
                new_submob.move_arc_center_to(point)
                submob.points = new_submob.points

    def update_shadow(self,point = ORIGIN):
        print "updating shadow"
        use_point = point #self.source_point
        self.shadow.points = self.screen.points
        ray1 = self.screen.points[0] - use_point
        ray2 = self.screen.points[-1] - use_point
        ray1 = ray1/np.linalg.norm(ray1) * 100
        ray1 = rotate_vector(ray1,-TAU/16)
        ray2 = ray2/np.linalg.norm(ray2) * 100
        ray2 = rotate_vector(ray2,TAU/16)
        outpoint1 = self.screen.points[0] + ray1
        outpoint2 = self.screen.points[-1] + ray2
        self.shadow.add_control_points([outpoint2,outpoint1,self.screen.points[0]])
        self.shadow.mark_paths_closed = True


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




class SwitchOn(LaggedStart):
    CONFIG = {
        "lag_ratio": 0.2,
        "run_time": SWITCH_ON_RUN_TIME
    }

    def __init__(self, light, **kwargs):
        if not isinstance(light,AmbientLight) and not isinstance(light,Spotlight):
            raise Exception("Only LightCones and Candles can be switched on")
        LaggedStart.__init__(self,
            FadeIn, light, **kwargs)


class SwitchOff(LaggedStart):
    CONFIG = {
        "lag_ratio": 0.2,
        "run_time": SWITCH_ON_RUN_TIME
    }

    def __init__(self, light, **kwargs):
        if not isinstance(light,AmbientLight) and not isinstance(light,Spotlight):
            raise Exception("Only LightCones and Candles can be switched on")
        light.submobjects = light.submobjects[::-1]
        LaggedStart.__init__(self,
            FadeOut, light, **kwargs)
        light.submobjects = light.submobjects[::-1]





class ScreenTracker(ContinualAnimation):
    def __init__(self, mobject, **kwargs):
        ContinualAnimation.__init__(self, mobject, **kwargs)

    def update_mobject(self, dt):
        self.mobject.recalculate_sectors(
            point = self.mobject.source_point,
            screen = self.mobject.screen)
        self.mobject.update_shadow(self.mobject.source_point)
        


class IntroScene(Scene):
    def construct(self):
        
        screen = Line([2,-2,0],[1,2,0]).shift([1,0,0])
        self.add(screen)

        ambient_light = AmbientLight(
            source_point = np.array([-1,1,0]),
            max_opacity = 1.0,
            opacity_function = lambda r: 1.0/(r/2+1)**2,
            num_levels = 4,
        )

        spotlight = Spotlight(
            source_point = np.array([-1,1,0]),
            max_opacity = 1.0,
            opacity_function = lambda r: 1.0/(r/2+1)**2,
            num_levels = 4,
            screen = screen,
        )

        self.add(spotlight)

        screen_updater = ScreenTracker(spotlight)
        #self.add(ca)

        #self.play(SwitchOn(ambient_light))
        #self.play(ApplyMethod(ambient_light.move_source_to,[-3,1,0]))
        #self.play(SwitchOn(spotlight))
        
        self.add(screen_updater)
        self.play(ApplyMethod(spotlight.screen.rotate,TAU/8))
        self.remove(screen_updater)
        self.play(ApplyMethod(spotlight.move_source_to,[-3,-1,0]))
        self.add(screen_updater)
        spotlight.source_point = [-3,-1,0]
        
        self.play(ApplyMethod(spotlight.dimming,0.2))
        #self.play(ApplyMethod(spotlight.move_source_to,[-4,0,0]))
        
        #self.wait()



