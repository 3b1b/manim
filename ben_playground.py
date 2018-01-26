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
    # * possibly a target
    # * an opacity function and its inverse
    # * a light color
    # * a max opacity

    # If the target is None, create annuli.
    # If there is a target, create annular sectors.

    CONFIG = {
        "source_point" : ORIGIN,
        "opacity_function" : lambda r : 1.0/(r+1.0)**2,
        "color" : LIGHT_COLOR,
        "max_opacity" : 1.0,
        "num_levels" : 10,
        "radius" : 5.0
    }

    def generate_points(self):

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

        # else:

        #     # look for the screen and create annular sectors
        #     lower_angle, upper_angle = self.viewing_angles(self.screen)
        #     dr = self.radius / self.num_levels
        #     for r in np.arange(0, self.radius, dr):
        #         alpha = self.max_opacity * self.opacity_function(r)
        #         annular_sector = AnnularSector(
        #             inner_radius = r,
        #             outer_radius = r + dr,
        #             color = self.color,
        #             fill_opacity = alpha,
        #             start_angle = lower_angle,
        #             angle = upper_angle - lower_angle
        #         )
        #         annular_sector.move_arc_center_to(self.source_point)
        #         self.add(annular_sector)





    # def redraw(self):
        # if self.screen != None:
        #     lower_angle, upper_angle = self.viewing_angles(self.screen)
        #     for submob in self.submobjects:
        #         if type(submob) == AnnularSector:
        #             submob.start_angle = lower_angle
        #             submob.angle = upper_angle - lower_angle
        #             submob.generate_points()
        #             submob.move_arc_center_to(self.source_point)

        
                    #submob.generate_points()


    def move_source_to(self,point):
        self.source_point = np.array(point)
        for submob in self.submobjects:
             if type(submob) == Annulus:
                submob.shift(self.source_point - submob.get_center())

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
        "screen" : None
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
        self.shift(np.array(point) - self.source_point)
        self.generate_points()

    def dimming(self,new_alpha):
        old_alpha = self.max_opacity
        self.max_opacity = new_alpha
        for submob in self.submobjects:
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


# class LightSource(Mobject):

#     # A light source is composed of:
#     # * a lighthouse
#     # * possibly a screen
#     # * and two light fields:
#     #    * an undirected one (annuli)
#     #    * one directed at the screen (annular sectors)

#     CONFIG = {
#         "location" : ORIGIN,
#         "icon" : SVGMobject(file_name = 'lighthouse', height = 0.5),
#         "ambient_light" : LightField(),
#         "spot_light_field" : LightField(),
#     }

#     def __init__(self,**kwargs):
#         Mobject.__init__(self,**kwargs)
#         self.icon.next_to(self.location, DOWN, buff = 0)
#         self.spot_light_field.max_opacity = 0
#         self.ambient_light_field.move_source_to(self.location)
#         self.spot_light_field.move_source_to(self.location)
#         self.add(self.icon,self.ambient_light_field,self.spot_light_field)

#     def dim_ambient(self,new_alpha):
#         self.ambient_light_field.dimming(new_alpha)



class ScreenTracker(ContinualAnimation):
    def __init__(self, spotlight, screen, **kwargs):
        self.spotlight = spotlight
        self.screen = screen
        ContinualAnimation.__init__(self, self.spotlight, **kwargs)

#    def update_mobject(self, dt):
        #self.spotlight.generate_points()




class IntroScene(Scene):
    def construct(self):
        
        screen = Square().shift([4,0,0])
        #ambient_light = AmbientLight(
        #    source_point = np.array([-1,1,0]),
        #    max_opacity = 1.0,
        #    opacity_function = lambda r: 1.0/(r/1+1)**2,
        #    num_levels = 10,
        #)

        #ambient_light.move_source_to([-5,0,0])
        self.add(screen)#,ambient_light)

        spotlight = Spotlight(
            source_point = np.array([-1,1,0]),
            max_opacity = 1.0,
            opacity_function = lambda r: 1.0/(r/2+1)**2,
            num_levels = 10,
            screen = screen,
        )

        self.add(spotlight)

        ca = ScreenTracker(spotlight,screen)
        self.add(ca)

        #self.play(SwitchOn(ambient_light))
        #self.play(ApplyMethod(ambient_light.move_source_to,[-3,1,0]))
        #self.play(SwitchOn(spotlight))
        #self.play(ApplyMethod(spotlight.move_source_to,[-3,-1,0]))
        #self.play(ApplyMethod(spotlight.dimming,0.2))
        self.play(screen.rotate, TAU/8, run_time = 3)
        self.play(ApplyMethod(spotlight.move_source_to,[-4,0,0]))
        
        self.wait()



