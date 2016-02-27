import numpy as np
import itertools as it
import os
import sys
from PIL import Image
import cv2
from colour import Color
import progressbar

from helpers import *

class Camera(object):
    DEFAULT_CONFIG = {
        #background of a different shape will overwrite these
        "pixel_width"      : DEFAULT_WIDTH,
        "pixel_height"     : DEFAULT_HEIGHT,
        "background_color" : BLACK,
        #
        "space_height"     : SPACE_HEIGHT,
        "space_center"     : ORIGIN,
    }

    def __init__(self, background = None, **kwargs):
        digest_config(self, kwargs, locals())
        self.init_background()
        self.reset()

        width_to_height = float(self.pixel_width) / self.pixel_height
        self.space_width = self.space_height * width_to_height

    def init_background(self):
        if self.background:
            shape = self.background.shape[:2]
            self.pixel_height, self.pixel_width = shape
        else:
            background_color = Color(self.background_color)
            background_rgb = (255*np.array(
                background_color.get_rgb()
            )).astype('uint8')
            ones = np.ones(
                (self.pixel_height, self.pixel_width, 1),
                dtype = 'uint8'
            )
            self.background = np.dot(
                ones, background_rgb.reshape((1, 3))
            )

    def get_image(self):
        return np.array(self.pixel_array)

    def set_image(self, pixel_array):
        self.pixel_array = np.array(pixel_array)

    def reset(self):
        self.set_image(np.array(self.background))

    def capture_mobject(self, mobject):
        return self.capture_mobjects([mobject])

    def capture_mobjects(self, mobjects, include_sub_mobjects = True):
        if include_sub_mobjects:
            all_families = [
                mob.submobject_family() 
                for mob in mobjects
            ]
            mobjects = reduce(op.add, all_families, [])
            
        for mobject in mobjects:
            if mobject.display_mode == "region":
                self.display_region(mobject)
            elif mobject.display_mode == "points":
                self.display_points(
                    mobject.points, mobject.rgbs, 
                    self.adjusted_thickness(mobject.point_thickness)
                )
            else:
                raise Exception("Invalid display mode")

    def display_region(self, region):
        (h, w) = self.pixel_height, self.pixel_width
        scalar = 2*self.space_height / h
        xs =  scalar*np.arange(-w/2, w/2)
        ys = -scalar*np.arange(-h/2, h/2)
        x_array = np.dot(np.ones((h, 1)), xs.reshape((1, w)))
        y_array = np.dot(ys.reshape(h, 1), np.ones((1, w)))
        covered = region.condition(x_array, y_array)
        rgb = np.array(Color(region.color).get_rgb())
        rgb = (255*rgb).astype('uint8')
        self.pixel_array[covered] = rgb

    def display_points(self, points, rgbs, thickness):
        if len(points) == 0:
            return
        points = self.align_points_to_camera(points)
        pixel_coords = self.points_to_pixel_coords(points)
        pixel_coords = self.thickened_coordinates(
            pixel_coords, thickness
        )

        rgbs = (255*rgbs).astype('uint8')
        target_len = len(pixel_coords)
        factor = target_len/len(rgbs)
        rgbs = np.array([rgbs]*factor).reshape((target_len, 3))

        on_screen_indices = self.on_screen_pixels(pixel_coords)        
        pixel_coords = pixel_coords[on_screen_indices]        
        rgbs = rgbs[on_screen_indices]

        flattener = np.array([1, self.pixel_width], dtype = 'int')
        flattener = flattener.reshape((2, 1))
        indices = np.dot(pixel_coords, flattener)[:,0]
        indices = indices.astype('int')

        pw, ph = self.pixel_width, self.pixel_height
        # new_array = np.zeros((pw*ph, 3), dtype = 'uint8')
        # new_array[indices, :] = rgbs
        new_pa = self.pixel_array.reshape((ph*pw, 3))
        new_pa[indices] = rgbs
        self.pixel_array = new_pa.reshape((ph, pw, 3))


    def align_points_to_camera(self, points):
        ## This is where projection should live
        return points - self.space_center

    def points_to_pixel_coords(self, points):
        result = np.zeros((len(points), 2))
        width_mult  = self.pixel_width/self.space_width/2
        width_add   = self.pixel_width/2        
        height_mult = self.pixel_height/self.space_height/2
        height_add  = self.pixel_height/2
        #Flip on y-axis as you go
        height_mult *= -1

        result[:,0] = points[:,0]*width_mult + width_add
        result[:,1] = points[:,1]*height_mult + height_add
        return result.astype('int')

    def on_screen_pixels(self, pixel_coords):
        return reduce(op.and_, [
            pixel_coords[:,0] >= 0,
            pixel_coords[:,0] < self.pixel_width,
            pixel_coords[:,1] >= 0,
            pixel_coords[:,1] < self.pixel_height,
        ])

    def adjusted_thickness(self, thickness):
        big_width = PRODUCTION_QUALITY_DISPLAY_CONFIG["width"]
        big_height = PRODUCTION_QUALITY_DISPLAY_CONFIG["height"]
        factor = (big_width + big_height) / \
                 (self.pixel_width + self.pixel_height)
        return 1 + (thickness-1)/factor

    def get_thickening_nudges(self, thickness):
        _range = range(-thickness/2+1, thickness/2+1)
        return np.array(list(it.product(*[_range]*2)))

    def thickened_coordinates(self, pixel_coords, thickness):
        nudges = self.get_thickening_nudges(thickness)
        pixel_coords = np.array([
            pixel_coords + nudge
            for nudge in nudges
        ])
        size = pixel_coords.size
        return pixel_coords.reshape((size/2, 2))



class MovingCamera(Camera):
    """
    Stays in line with the height, width and position
    of a given mobject
    """
    def __init__(self, mobject, **kwargs):
        digest_locals(self)
        Camera.__init__(self, **kwargs)

    def capture_mobjects(self, *args, **kwargs):
        self.space_height = self.mobject.get_height()
        self.space_center = self.mobject.get_center()












