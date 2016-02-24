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

    # def paint_region(region, image_array = None, color = None):
    #     pixels = get_pixels(image_array)
    #     assert region.shape == pixels.shape[:2]
    #     if color is None:
    #         #Random dark color
    #         rgb = 0.5 * np.random.random(3)
    #     else:
    #         rgb = np.array(Color(color).get_rgb()) 
    #     pixels[region.bool_grid] = (255*rgb).astype('uint8')
    #     return pixels

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
            self.display_points(
                mobject.points, mobject.rgbs, 
                self.adjusted_thickness(mobject.point_thickness)
            )

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

    # def add_thickness(pixel_indices_and_rgbs, thickness, width, height):
    #     """
    #     Imagine dragging each pixel around like a paintbrush in
    #     a plus-sign-shaped pixel arrangement surrounding it.

    #     Pass rgb = None to do nothing to them
    #     """
    #     thickness = adjusted_thickness(thickness, width, height)
    #     original = np.array(pixel_indices_and_rgbs)
    #     n_extra_columns = pixel_indices_and_rgbs.shape[1] - 2
    #     for nudge in range(-thickness/2+1, thickness/2+1):
    #         if nudge == 0:
    #             continue
    #         for x, y in [[nudge, 0], [0, nudge]]:
    #             pixel_indices_and_rgbs = np.append(
    #                 pixel_indices_and_rgbs, 
    #                 original+([x, y] + [0]*n_extra_columns),
    #                 axis = 0
    #             )
    #     admissibles = (pixel_indices_and_rgbs[:,0] >= 0) & \
    #                   (pixel_indices_and_rgbs[:,0] < width) & \
    #                   (pixel_indices_and_rgbs[:,1] >= 0) & \
    #                   (pixel_indices_and_rgbs[:,1] < height)
    #     return pixel_indices_and_rgbs[admissibles]

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
















