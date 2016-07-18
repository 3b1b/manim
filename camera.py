import numpy as np
import itertools as it
import os

from PIL import Image
from colour import Color
import aggdraw

from helpers import *
from mobject import PMobject, VMobject

class Camera(object):
    CONFIG = {
        #background of a different shape will overwrite this
        "pixel_shape" : (DEFAULT_HEIGHT, DEFAULT_WIDTH),
        #this will be resized to match pixel_shape
        "space_shape" : (SPACE_HEIGHT, SPACE_WIDTH),
        "space_center" : ORIGIN,
        "background_color" : BLACK,
    }

    def __init__(self, background = None, **kwargs):
        digest_config(self, kwargs, locals())
        self.init_background()
        self.resize_space_shape()
        self.reset()

    def resize_space_shape(self, fixed_dimension = 0):
        """
        Changes space_shape to match the aspect ratio 
        of pixel_shape, where fixed_dimension determines
        whether space_shape[0] (height) or space_shape[1] (width)
        remains fixed while the other changes accordingly.
        """
        aspect_ratio = float(self.pixel_shape[1])/self.pixel_shape[0]
        space_height, space_width = self.space_shape
        if fixed_dimension == 0:
            space_width = aspect_ratio*space_height
        else:
            space_height = space_width/aspect_ratio
        self.space_shape = (space_height, space_width)

    def init_background(self):
        if self.background is not None:
            self.pixel_shape = self.background.shape[:2]
        else:
            background_rgb = color_to_int_rgb(self.background_color)
            self.background = np.zeros(
                list(self.pixel_shape)+[3],
                dtype = 'uint8'
            )
            self.background[:,:] = background_rgb

    def get_image(self):
        return np.array(self.pixel_array)

    def set_image(self, pixel_array):
        self.pixel_array = np.array(pixel_array)

    def reset(self):
        self.set_image(np.array(self.background))

    def capture_mobject(self, mobject):
        return self.capture_mobjects([mobject])

    def capture_mobjects(self, mobjects, include_submobjects = True):
        if include_submobjects:
            mobjects = it.chain(*[
                mob.family_members_with_points() 
                for mob in mobjects
            ])
        vmobjects = []
        for mobject in mobjects:
            if isinstance(mobject, VMobject):
                vmobjects.append(mobject)
            elif isinstance(mobject, PMobject):
                self.display_point_cloud(
                    mobject.points, mobject.rgbs, 
                    self.adjusted_thickness(mobject.stroke_width)
                )
            #TODO, more?  Call out if it's unknown?
        image = Image.fromarray(self.pixel_array, mode = "RGB")
        canvas = aggdraw.Draw(image)
        for vmobject in vmobjects:
            self.display_vectorized(vmobject, canvas)
        canvas.flush()            
        self.pixel_array[:,:] = np.array(image)


    def display_region(self, region):
        (h, w) = self.pixel_shape
        scalar = 2*self.space_shape[0] / h
        xs =  scalar*np.arange(-w/2, w/2)+self.space_center[0]
        ys = -scalar*np.arange(-h/2, h/2)+self.space_center[1]
        x_array = np.dot(np.ones((h, 1)), xs.reshape((1, w)))
        y_array = np.dot(ys.reshape(h, 1), np.ones((1, w)))
        covered = region.condition(x_array, y_array)
        rgb = np.array(Color(region.color).get_rgb())
        rgb = (255*rgb).astype('uint8')
        self.pixel_array[covered] = rgb


    def display_vectorized(self, vmobject, canvas):
        if vmobject.is_subpath:
            #Subpath vectorized mobjects are taken care
            #of by their parent
            return
        pen, fill = self.get_pen_and_fill(vmobject)
        pathstring = self.get_pathstring(vmobject)
        symbol = aggdraw.Symbol(pathstring)
        canvas.symbol((0, 0), symbol, pen, fill)


    def get_pen_and_fill(self, vmobject):
        pen = aggdraw.Pen(
            vmobject.get_stroke_color().get_hex_l(),
            max(vmobject.stroke_width, 0)
        )
        fill = aggdraw.Brush(
            vmobject.get_fill_color().get_hex_l(),
            opacity = int(255*vmobject.get_fill_opacity())
        )
        return (pen, fill)

    def get_pathstring(self, vmobject):
        result = ""        
        for mob in [vmobject]+vmobject.get_subpath_mobjects():
            points = mob.points
            if len(points) == 0:
                continue
            coords = self.points_to_pixel_coords(points)
            start = "M%d %d"%tuple(coords[0])
            #(handle1, handle2, anchor) tripletes
            triplets = zip(*[
                coords[i+1::3]
                for i in range(3)
            ])
            cubics = [
                "C" + " ".join(map(str, it.chain(*triplet)))
                for triplet in triplets
            ]
            end = "Z" if vmobject.mark_paths_closed else ""
            result += " ".join([start] + cubics + [end])
        return result

    def display_point_cloud(self, points, rgbs, thickness):
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

        ph, pw = self.pixel_shape

        flattener = np.array([1, pw], dtype = 'int')
        flattener = flattener.reshape((2, 1))
        indices = np.dot(pixel_coords, flattener)[:,0]
        indices = indices.astype('int')
        
        new_pa = self.pixel_array.reshape((ph*pw, 3))
        new_pa[indices] = rgbs
        self.pixel_array = new_pa.reshape((ph, pw, 3))


    def align_points_to_camera(self, points):
        ## This is where projection should live
        return points - self.space_center

    def points_to_pixel_coords(self, points):
        result = np.zeros((len(points), 2))
        ph, pw = self.pixel_shape
        sh, sw = self.space_shape
        width_mult  = pw/sw/2
        width_add   = pw/2        
        height_mult = ph/sh/2
        height_add  = ph/2
        #Flip on y-axis as you go
        height_mult *= -1

        result[:,0] = points[:,0]*width_mult + width_add
        result[:,1] = points[:,1]*height_mult + height_add
        return result.astype('int')

    def on_screen_pixels(self, pixel_coords):
        return reduce(op.and_, [
            pixel_coords[:,0] >= 0,
            pixel_coords[:,0] < self.pixel_shape[1],
            pixel_coords[:,1] >= 0,
            pixel_coords[:,1] < self.pixel_shape[0],
        ])

    def adjusted_thickness(self, thickness):
        big_shape = PRODUCTION_QUALITY_CAMERA_CONFIG["pixel_shape"]
        factor = sum(big_shape)/sum(self.pixel_shape)
        return 1 + (thickness-1)/factor

    def get_thickening_nudges(self, thickness):
        _range = range(-thickness/2+1, thickness/2+1)
        return np.array(
            list(it.product([0], _range))+
            list(it.product(_range, [0]))
        )

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
    CONFIG = {
        "aligned_dimension" : "width" #or height
    }
    def __init__(self, mobject, **kwargs):
        digest_locals(self)
        Camera.__init__(self, **kwargs)

    def capture_mobjects(self, *args, **kwargs):
        self.space_center = self.mobject.get_center()
        self.realign_space_shape()        
        Camera.capture_mobjects(self, *args, **kwargs)

    def realign_space_shape(self):
        height, width = self.space_shape
        if self.aligned_dimension == "height":
            self.space_shape = (self.mobject.get_height()/2, width)
        else:
            self.space_shape = (height, self.mobject.get_width()/2)
        self.resize_space_shape(
            0 if self.aligned_dimension == "height" else 1
        )
        













