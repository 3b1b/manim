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
    CONFIG = {
        "pixel_width"      : DEFAULT_WIDTH,
        "pixel_height"     : DEFAULT_HEIGHT,
        "space_height"     : SPACE_HEIGHT,
        "space_center"     : ORIGIN,
        "background_color" : BLACK,
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
            background_rgb = np.array(background_color.get_rgb())
            ones = np.ones(
                (self.pixel_height, self.pixel_width, 1),
                dtype = 'uint8'
            )
            self.background = np.dot(
                ones, background_rgb.reshape((1, 3))
            )

    def get_image(self):
        return self.pixel_array

    def reset(self):
        self.pixel_array = np.array(self.background)

    # def get_pixels(image_array): #TODO, FIX WIDTH/HEIGHT PROBLEM HERE
    #     if image_array is None:
    #         return np.zeros(
    #             (DEFAULT_HEIGHT, DEFAULT_WIDTH, 3), 
    #             dtype = 'uint8'
    #         )
    #     else:
    #         pixels = np.array(image_array).astype('uint8')
    #         assert len(pixels.shape) == 3 and pixels.shape[2] == 3
    #         return pixels

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
        # pixels = get_pixels(image_array)
        # height = pixels.shape[0]
        # width  = pixels.shape[1]
        # space_height = SPACE_HEIGHT
        # space_width  = SPACE_HEIGHT * width / height
        # pixels = pixels.reshape((pixels.size/3, 3)).astype('uint8')

        if include_sub_mobjects:
            all_families = [
                mob.submobject_family() 
                for mob in mobjects
            ]
            mobjects = reduce(op.add, all_families, [])
            
        for mobject in mobjects:
            self.display_points(
                mobject.points, mobject.rgbs, 
                mobject.point_thickness
            )

    def display_points(self, points, rgbs, thickness):
        points = self.project_onto_screen(points)
        pixel_coordinates = self.pixel_coordinates_of_points(points)
        rgbs = (255*rgbs).astype('uint8')
        on_screen_indices = self.on_screen_pixels(pixel_coordinates)
        pixel_coordinates = pixel_coordinates[on_screen_indices]
        rgbs = rgbs[on_screen_indices]

        flattener = np.array([1, self.width], dtype = 'int')
        flattener = flattener.reshape((2, 1))
        indices = np.dot(pixel_coordinates, flattener)[:,0]

        pw, ph = self.pixel_width, self.pixel_height
        self.pixel_array.reshape((pw*ph, 3))
        self.pixel_array[indices] = rgbs.astype('uint8')
        self.pixel_array.reshape((ph, pw, 3))

    def project_onto_screen(points):
        ## TODO
        points[:,2] = 0

    def pixel_coordinates_of_points(self, points):
        result = np.zeros((len(points), 2))
        width_mult  = self.pixel_width/self.space_width/2
        width_add   = self.pixel_width/2        
        height_mult = self.pixel_height/self.space_height/2
        height_add  = self.pixel_height/2
        #Flip on y-axis as you go
        height_mult *= -1

        result[:,0] = points[:,0]*width_mult + width_add
        result[:,1] = points[:,1]*height_mult + height_add
        return result

    def on_screen_pixels(self, pixel_coordinates):
        return (pixel_coordinates[:,0] < 0) | \
               (pixel_coordinates[:,0] >= width) | \
               (pixel_coordinates[:,1] < 0) | \
               (pixel_coordinates[:,1] >= height)


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

    def adjusted_thickness(thickness, width, height):
        big_width = PRODUCTION_QUALITY_DISPLAY_CONFIG["width"]
        big_height = PRODUCTION_QUALITY_DISPLAY_CONFIG["height"]
        factor = (big_width + big_height) / (width + height)
        return 1 + (thickness-1)/facto



















