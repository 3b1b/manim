import numpy as np
import itertools as it
import os

from PIL import Image
from colour import Color
import aggdraw
import copy

from helpers import *
from mobject import Mobject, PMobject, VMobject, \
    ImageMobject, Group

class Camera(object):
    CONFIG = {
        "background_image" : None,
        "pixel_shape" : (DEFAULT_HEIGHT, DEFAULT_WIDTH),
        # Note 1: space_shape will be resized to match pixel_shape
        #
        # Note 2: While pixel_shape indicates the actual full height
        # and width of the pixel array, space_shape indicates only 
        # half the height and half the width of space (extending from
        # -space_height to +space_height vertically and from 
        # -space_widtdh to +space_width horizontally)
        # TODO: Rename these to SPACE_X_RADIUS, SPACE_Y_RADIUS
        "space_shape" : (SPACE_HEIGHT, SPACE_WIDTH),
        "space_center" : ORIGIN,
        "background_color" : BLACK,
        #Points in vectorized mobjects with norm greater
        #than this value will be rescaled.
        "max_allowable_norm" : 2*SPACE_WIDTH,
        "image_mode" : "RGBA",
        "n_rgb_coords" : 4,
        "background_alpha" : 0, #Out of rgb_max_val
        "pixel_array_dtype" : 'uint8',
        "use_z_coordinate_for_display_order" : False,
        # z_buff_func is only used if the flag above is set to True.
        # round z coordinate to nearest hundredth when comparring
        "z_buff_func" : lambda m : np.round(m.get_center()[2], 2),
    }

    def __init__(self, background = None, **kwargs):
        digest_config(self, kwargs, locals())
        self.rgb_max_val = np.iinfo(self.pixel_array_dtype).max
        self.init_background()
        self.resize_space_shape()
        self.reset()

    def __deepcopy__(self, memo):
        # This is to address a strange bug where deepcopying
        # will result in a segfault, which is somehow related
        # to the aggdraw library
        self.canvas = None 
        return copy.copy(self)

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
        if self.background_image is not None:
            path = get_full_raster_image_path(self.background_image)
            image = Image.open(path).convert(self.image_mode)
            height, width = self.pixel_shape
            #TODO, how to gracefully handle backgrounds 
            #with different sizes?
            self.background = np.array(image)[:height, :width]
            self.background = self.background.astype(self.pixel_array_dtype)
        else:
            background_rgba = color_to_int_rgba(
                self.background_color, alpha = self.background_alpha
            )
            self.background = np.zeros(
                list(self.pixel_shape)+[self.n_rgb_coords],
                dtype = self.pixel_array_dtype
            )
            self.background[:,:] = background_rgba

    def get_image(self):
        return Image.fromarray(
            self.pixel_array,
            mode = self.image_mode
        )

    def get_pixel_array(self):
        return self.pixel_array

    def convert_pixel_array(self, pixel_array, convert_from_floats = False):
        retval = np.array(pixel_array)
        if convert_from_floats:
            retval = np.apply_along_axis(
                lambda f : (f * self.rgb_max_val).astype(self.pixel_array_dtype),
                2,
                retval)
        return retval

    def set_pixel_array(self, pixel_array, convert_from_floats = False):
        converted_array = self.convert_pixel_array(pixel_array, convert_from_floats)
        if not hasattr(self, "pixel_array"): #TODO: And the shapes match?
            self.pixel_array = converted_array
        else:
            #Set in place
            self.pixel_array[:,:,:] = converted_array[:,:,:]

    def set_background(self, pixel_array, convert_from_floats = False):
        self.background = self.convert_pixel_array(pixel_array, convert_from_floats)

    def make_background_from_func(self, coords_to_colors_func):
        """
        Sets background by using coords_to_colors_func to determine each pixel's color. Each input 
        to coords_to_colors_func is an (x, y) pair in space (in ordinary space coordinates; not 
        pixel coordinates), and each output is expected to be an RGBA array of 4 floats.
        """

        print "Starting set_background_from_func"

        coords = self.get_coords_of_all_pixels()
        new_background = np.apply_along_axis(
            coords_to_colors_func,
            2,
            coords
        )
        return self.convert_pixel_array(new_background, convert_from_floats = True)

    def set_background_from_func(self, coords_to_colors_func):
        self.set_background(self.make_background_from_func(coords_to_colors_func))

    def reset(self):
        self.set_pixel_array(self.background)

    ####

    def extract_mobject_family_members(self, mobjects, only_those_with_points = False):
        if only_those_with_points:
            method = Mobject.family_members_with_points
        else:
            method = Mobject.submobject_family
        return remove_list_redundancies(list(
            it.chain(*[
                method(m)
                for m in mobjects
                if not (isinstance(m, VMobject) and m.is_subpath)
            ])
        ))

    def get_mobjects_to_display(
        self, mobjects, 
        include_submobjects = True,
        excluded_mobjects = None,
        ):
        if include_submobjects:
            mobjects = self.extract_mobject_family_members(
                mobjects, only_those_with_points = True
            )
            if excluded_mobjects:
                all_excluded = self.extract_mobject_family_members(
                    excluded_mobjects
                )
                mobjects = list_difference_update(mobjects, all_excluded)

        if self.use_z_coordinate_for_display_order:
            # Should perhaps think about what happens here when include_submobjects is False,
            # (for now, the onus is then on the caller to ensure this is handled correctly by
            # passing us an appropriately pre-flattened list of mobjects if need be)
            return sorted(
                mobjects,
                lambda a, b: cmp(self.z_buff_func(a), self.z_buff_func(b))
            )
        else:
            return mobjects

    def capture_mobject(self, mobject, **kwargs):
        return self.capture_mobjects([mobject], **kwargs)

    def capture_mobjects(self, mobjects, **kwargs):
        mobjects = self.get_mobjects_to_display(mobjects, **kwargs)

        # Organize this list into batches of the same type, and 
        # apply corresponding function to those batches
        type_func_pairs = [
            (VMobject, self.display_multiple_vectorized_mobjects),
            (PMobject,  self.display_multiple_point_cloud_mobjects),
            (ImageMobject,  self.display_multiple_image_mobjects),
            (Mobject, lambda batch : batch), #Do nothing
        ]
        def get_mobject_type(mobject):
            for mobject_type, func in type_func_pairs:
                if isinstance(mobject, mobject_type):
                    return mobject_type
            raise Exception(
                "Trying to display something which is not of type Mobject"
            )
        batch_type_pairs = batch_by_property(mobjects, get_mobject_type)

        #Display in these batches
        for batch, batch_type in batch_type_pairs:
            #check what the type is, and call the appropriate function
            for mobject_type, func in type_func_pairs:
                if batch_type == mobject_type:
                    func(batch)

    ## Methods associated with svg rendering

    def get_aggdraw_canvas(self):
        if not hasattr(self, "canvas") or not self.canvas:
            self.reset_aggdraw_canvas()
        return self.canvas

    def reset_aggdraw_canvas(self):
        image = Image.fromarray(self.pixel_array, mode = self.image_mode)
        self.canvas = aggdraw.Draw(image)

    def display_multiple_vectorized_mobjects(self, vmobjects):
        if len(vmobjects) == 0:
            return
        batch_file_pairs = batch_by_property(
            vmobjects, 
            lambda vm : vm.get_background_image_file()
        )
        for batch, file_name in batch_file_pairs:
            if file_name:
                self.display_multiple_background_colored_vmobject(batch)
            else:
                self.display_multiple_non_background_colored_vmobjects(batch)

    def display_multiple_non_background_colored_vmobjects(self, vmobjects):
        self.reset_aggdraw_canvas()
        canvas = self.get_aggdraw_canvas()
        for vmobject in vmobjects:
            self.display_vectorized(vmobject, canvas)
        canvas.flush()

    def display_vectorized(self, vmobject, canvas = None):
        if vmobject.is_subpath:
            #Subpath vectorized mobjects are taken care
            #of by their parent
            return
        canvas = canvas or self.get_aggdraw_canvas()
        pen, fill = self.get_pen_and_fill(vmobject)
        pathstring = self.get_pathstring(vmobject)
        symbol = aggdraw.Symbol(pathstring)
        canvas.symbol((0, 0), symbol, pen, fill)

    def get_pen_and_fill(self, vmobject):
        stroke_width = max(vmobject.get_stroke_width(), 0)
        if stroke_width == 0:
            pen = None
        else:
            stroke_rgb = self.get_stroke_rgb(vmobject)
            stroke_hex = rgb_to_hex(stroke_rgb)
            pen = aggdraw.Pen(stroke_hex, stroke_width)

        fill_opacity = int(self.rgb_max_val*vmobject.get_fill_opacity())
        if fill_opacity == 0:
            fill = None
        else:
            fill_rgb = self.get_fill_rgb(vmobject)
            fill_hex = rgb_to_hex(fill_rgb)
            fill = aggdraw.Brush(fill_hex, fill_opacity)

        return (pen, fill)

    def color_to_hex_l(self, color):
        try:
            return color.get_hex_l()
        except:
            return Color(BLACK).get_hex_l()

    def get_stroke_rgb(self, vmobject):
        return vmobject.get_stroke_rgb()

    def get_fill_rgb(self, vmobject):
        return vmobject.get_fill_rgb()

    def get_pathstring(self, vmobject):
        result = ""
        for mob in [vmobject]+vmobject.get_subpath_mobjects():
            points = mob.points
            # points = self.adjust_out_of_range_points(points)            
            if len(points) == 0:
                continue
            aligned_points = self.align_points_to_camera(points)
            coords = self.points_to_pixel_coords(aligned_points)
            coord_strings = coords.flatten().astype(str)
            #Start new path string with M
            coord_strings[0] = "M" + coord_strings[0]
            #The C at the start of every 6th number communicates
            #that the following 6 define a cubic Bezier
            coord_strings[2::6] = map(lambda s : "C" + str(s), coord_strings[2::6])
            #Possibly finish with "Z"
            if vmobject.mark_paths_closed:
                coord_strings[-1] = coord_strings[-1] + " Z"
            result += " ".join(coord_strings)
        return result

    def get_background_colored_vmobject_displayer(self):
        #Quite wordy to type out a bunch
        long_name = "background_colored_vmobject_displayer"
        if not hasattr(self, long_name):
            setattr(self, long_name, BackgroundColoredVMobjectDisplayer(self))
        return getattr(self, long_name)

    def display_multiple_background_colored_vmobject(self, cvmobjects):
        displayer = self.get_background_colored_vmobject_displayer()
        cvmobject_pixel_array = displayer.display(*cvmobjects)
        self.overlay_rgba_array(cvmobject_pixel_array)
        return self

    ## Methods for other rendering

    def display_multiple_point_cloud_mobjects(self, pmobjects):
        for pmobject in pmobjects:
            self.display_point_cloud(
                pmobject.points,
                pmobject.rgbas,
                self.adjusted_thickness(pmobject.stroke_width)
            )

    def display_point_cloud(self, points, rgbas, thickness):
        if len(points) == 0:
            return
        points = self.align_points_to_camera(points)
        pixel_coords = self.points_to_pixel_coords(points)
        pixel_coords = self.thickened_coordinates(
            pixel_coords, thickness
        )
        rgba_len = self.pixel_array.shape[2]

        rgbas = (self.rgb_max_val*rgbas).astype(self.pixel_array_dtype)
        target_len = len(pixel_coords)
        factor = target_len/len(rgbas)
        rgbas = np.array([rgbas]*factor).reshape((target_len, rgba_len))

        on_screen_indices = self.on_screen_pixels(pixel_coords)        
        pixel_coords = pixel_coords[on_screen_indices]        
        rgbas = rgbas[on_screen_indices]

        ph, pw = self.pixel_shape

        flattener = np.array([1, pw], dtype = 'int')
        flattener = flattener.reshape((2, 1))
        indices = np.dot(pixel_coords, flattener)[:,0]
        indices = indices.astype('int')
        
        new_pa = self.pixel_array.reshape((ph*pw, rgba_len))
        new_pa[indices] = rgbas
        self.pixel_array = new_pa.reshape((ph, pw, rgba_len))

    def display_multiple_image_mobjects(self, image_mobjects):
        for image_mobject in image_mobjects:
            self.display_image_mobject(image_mobject)

    def display_image_mobject(self, image_mobject):
        corner_coords = self.points_to_pixel_coords(image_mobject.points)
        ul_coords, ur_coords, dl_coords = corner_coords
        right_vect = ur_coords - ul_coords
        down_vect = dl_coords - ul_coords

        impa = image_mobject.pixel_array

        oh, ow = self.pixel_array.shape[:2] #Outer width and height
        ih, iw = impa.shape[:2] #inner with and height
        rgb_len = self.pixel_array.shape[2]

        image = np.zeros((oh, ow, rgb_len), dtype = self.pixel_array_dtype)

        if right_vect[1] == 0 and down_vect[0] == 0:
            rv0 = right_vect[0]
            dv1 = down_vect[1]
            x_indices = np.arange(rv0, dtype = 'int')*iw/rv0
            y_indices = np.arange(dv1, dtype = 'int')*ih/dv1
            stretched_impa = impa[y_indices][:,x_indices]

            x0, x1 = ul_coords[0], ur_coords[0] 
            y0, y1 = ul_coords[1], dl_coords[1]
            if x0 >= ow or x1 < 0 or y0 >= oh or y1 < 0:
                return
            siy0 = max(-y0, 0) #stretched_impa y0
            siy1 = dv1 - max(y1-oh, 0)
            six0 = max(-x0, 0)
            six1 = rv0 - max(x1-ow, 0)
            x0 = max(x0, 0)
            y0 = max(y0, 0)
            image[y0:y1, x0:x1] = stretched_impa[siy0:siy1, six0:six1]
        else:
            # Alternate (slower) tactice if image is tilted
            # List of all coordinates of pixels, given as (x, y), 
            # which matches the return type of points_to_pixel_coords,
            # even though np.array indexing naturally happens as (y, x)
            all_pixel_coords = np.zeros((oh*ow, 2), dtype = 'int')
            a = np.arange(oh*ow, dtype = 'int')
            all_pixel_coords[:,0] = a%ow
            all_pixel_coords[:,1] = a/ow

            recentered_coords = all_pixel_coords - ul_coords
            coord_norms = np.linalg.norm(recentered_coords, axis = 1)

            with np.errstate(divide = 'ignore'):
                ix_coords, iy_coords = [
                    np.divide(
                        dim*np.dot(recentered_coords, vect),
                        np.dot(vect, vect),
                    )
                    for vect, dim in (right_vect, iw), (down_vect, ih)
                ]
            to_change = reduce(op.and_, [
                ix_coords >= 0, ix_coords < iw,
                iy_coords >= 0, iy_coords < ih,
            ])
            n_to_change = np.sum(to_change)
            inner_flat_coords = iw*iy_coords[to_change] + ix_coords[to_change]
            flat_impa = impa.reshape((iw*ih, rgb_len))
            target_rgbas = flat_impa[inner_flat_coords, :]

            image = image.reshape((ow*oh, rgb_len))
            image[to_change] = target_rgbas
            image = image.reshape((oh, ow, rgb_len))
        self.overlay_rgba_array(image)

    def overlay_rgba_array(self, arr):
        fg = arr
        bg = self.pixel_array
        # rgba_max_val = self.rgb_max_val
        src_rgb, src_a, dst_rgb, dst_a = [
            a.astype(np.float32)/self.rgb_max_val
            for a in fg[...,:3], fg[...,3], bg[...,:3], bg[...,3]
        ]

        out_a = src_a + dst_a*(1.0-src_a)

        # When the output alpha is 0 for full transparency, 
        # we have a choice over what RGB value to use in our
        # output representation. We choose 0.0 here.
        out_rgb = fdiv(
            src_rgb*src_a[..., None] + \
            dst_rgb*dst_a[..., None]*(1.0-src_a[..., None]),
            out_a[..., None],
            zero_over_zero_value = 0.0
        )

        self.pixel_array[..., :3] = out_rgb*self.rgb_max_val
        self.pixel_array[..., 3] = out_a*self.rgb_max_val

    def align_points_to_camera(self, points):
        ## This is where projection should live
        return points - self.space_center

    def adjust_out_of_range_points(self, points):
        if not np.any(points > self.max_allowable_norm):
            return points
        norms = np.apply_along_axis(np.linalg.norm, 1, points)
        violator_indices = norms > self.max_allowable_norm
        violators = points[violator_indices,:]
        violator_norms = norms[violator_indices]
        reshaped_norms = np.repeat(
            violator_norms.reshape((len(violator_norms), 1)), 
            points.shape[1], 1
        )
        rescaled = self.max_allowable_norm * violators / reshaped_norms
        points[violator_indices] = rescaled
        return points

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
        return np.array(list(it.product(_range, _range)))

    def thickened_coordinates(self, pixel_coords, thickness):
        nudges = self.get_thickening_nudges(thickness)
        pixel_coords = np.array([
            pixel_coords + nudge
            for nudge in nudges
        ])
        size = pixel_coords.size
        return pixel_coords.reshape((size/2, 2))

    def get_coords_of_all_pixels(self):
        # These are in x, y order, to help me keep things straight
        full_space_dims = np.array(self.space_shape)[::-1] * 2
        full_pixel_dims = np.array(self.pixel_shape)[::-1]

        # These are addressed in the same y, x order as in pixel_array, but the values in them
        # are listed in x, y order
        uncentered_pixel_coords = np.indices(self.pixel_shape)[::-1].transpose(1, 2, 0)
        uncentered_space_coords = fdiv(
            uncentered_pixel_coords * full_space_dims, 
            full_pixel_dims)
        # Could structure above line's computation slightly differently, but figured (without much 
        # thought) multiplying by space_shape first, THEN dividing by pixel_shape, is probably 
        # better than the other order, for avoiding underflow quantization in the division (whereas 
        # overflow is unlikely to be a problem)

        centered_space_coords = (uncentered_space_coords - fdiv(full_space_dims, 2))

        # Have to also flip the y coordinates to account for pixel array being listed in 
        # top-to-bottom order, opposite of screen coordinate convention
        centered_space_coords = centered_space_coords * (1, -1)

        return centered_space_coords

class BackgroundColoredVMobjectDisplayer(object):
    def __init__(self, camera):
        self.camera = camera
        self.file_name_to_pixel_array_map = {}
        self.init_canvas()

    def init_canvas(self):
        self.pixel_array = np.zeros(
            self.camera.pixel_array.shape,
            dtype = self.camera.pixel_array_dtype,
        )
        self.reset_canvas()

    def reset_canvas(self):
        image = Image.fromarray(self.pixel_array, mode = self.camera.image_mode)
        self.canvas = aggdraw.Draw(image)

    def resize_background_array(
        self, background_array, 
        new_width, new_height, 
        mode = "RGBA"
        ):
        image = Image.fromarray(background_array, mode = mode)
        resized_image = image.resize((new_width, new_height))
        return np.array(resized_image)

    def resize_background_array_to_match(self, background_array, pixel_array):
        height, width = pixel_array.shape[:2]
        mode = "RGBA" if pixel_array.shape[2] == 4 else "RGB"
        return self.resize_background_array(background_array, width, height, mode)

    def get_background_array(self, file_name):
        if file_name in self.file_name_to_pixel_array_map:
            return self.file_name_to_pixel_array_map[file_name]
        full_path = get_full_raster_image_path(file_name)
        image = Image.open(full_path)
        array = np.array(image)

        camera = self.camera
        if not np.all(camera.pixel_array.shape == array.shape):
            array = self.resize_background_array_to_match(array, camera.pixel_array)

        self.file_name_to_pixel_array_map[file_name] = array
        return array

    def display(self, *cvmobjects):
        batch_image_file_pairs = batch_by_property(
            cvmobjects, lambda cv : cv.get_background_image_file()
        )
        curr_array = None
        for batch, image_file in batch_image_file_pairs:
            background_array = self.get_background_array(image_file)
            for cvmobject in batch:
                self.camera.display_vectorized(cvmobject, self.canvas)
            self.canvas.flush()
            new_array = np.array(
                (background_array*self.pixel_array.astype('float')/255),
                dtype = self.camera.pixel_array_dtype
            )
            if curr_array is None:
                curr_array = new_array
            else:
                curr_array = np.maximum(curr_array, new_array)
            self.pixel_array[:,:] = 0
            self.reset_canvas()
        return curr_array


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

# TODO: Add an attribute to mobjects under which they can specify that they should just 
# map their centers but remain otherwise undistorted (useful for labels, etc.)
class MappingCamera(Camera):
    CONFIG = {
        "mapping_func" : lambda p : p,
        "min_anchor_points" : 50,
        "allow_object_intrusion" : False
    }

    def points_to_pixel_coords(self, points):
        return Camera.points_to_pixel_coords(self, np.apply_along_axis(self.mapping_func, 1, points))
    
    def capture_mobjects(self, mobjects, **kwargs):
        mobjects = self.get_mobjects_to_display(mobjects, **kwargs)
        if self.allow_object_intrusion:
            mobject_copies = mobjects
        else:
            mobject_copies = [mobject.copy() for mobject in mobjects]
        for mobject in mobject_copies:
            if isinstance(mobject, VMobject) and \
            0 < mobject.get_num_anchor_points() < self.min_anchor_points:
                mobject.insert_n_anchor_points(self.min_anchor_points)
        Camera.capture_mobjects(
            self, mobject_copies, 
            include_submobjects = False,
            excluded_mobjects = None,
        )

# Note: This allows layering of multiple cameras onto the same portion of the pixel array,
# the later cameras overwriting the former
#
# TODO: Add optional separator borders between cameras (or perhaps peel this off into a 
# CameraPlusOverlay class)
class MultiCamera(Camera):
    def __init__(self, *cameras_with_start_positions, **kwargs):
        self.shifted_cameras = [
            DictAsObject(
            {
                "camera" : camera_with_start_positions[0], 
                "start_x" : camera_with_start_positions[1][1],
                "start_y" : camera_with_start_positions[1][0],
                "end_x" : camera_with_start_positions[1][1] + camera_with_start_positions[0].pixel_shape[1],
                "end_y" : camera_with_start_positions[1][0] + camera_with_start_positions[0].pixel_shape[0],
            })
            for camera_with_start_positions in cameras_with_start_positions
        ]
        Camera.__init__(self, **kwargs)

    def capture_mobjects(self, mobjects, **kwargs):
        for shifted_camera in self.shifted_cameras:
            shifted_camera.camera.capture_mobjects(mobjects, **kwargs)
            
            self.pixel_array[
                shifted_camera.start_y:shifted_camera.end_y, 
                shifted_camera.start_x:shifted_camera.end_x] \
            = shifted_camera.camera.pixel_array

    def set_background(self, pixel_array, **kwargs):
        for shifted_camera in self.shifted_cameras:
            shifted_camera.camera.set_background(
                pixel_array[
                    shifted_camera.start_y:shifted_camera.end_y, 
                    shifted_camera.start_x:shifted_camera.end_x],
                **kwargs
            )

    def set_pixel_array(self, pixel_array, **kwargs):
        Camera.set_pixel_array(self, pixel_array, **kwargs)
        for shifted_camera in self.shifted_cameras:
            shifted_camera.camera.set_pixel_array(
                pixel_array[
                    shifted_camera.start_y:shifted_camera.end_y, 
                    shifted_camera.start_x:shifted_camera.end_x],
                **kwargs
            )

    def init_background(self):
        Camera.init_background(self)
        for shifted_camera in self.shifted_cameras:
            shifted_camera.camera.init_background()

# A MultiCamera which, when called with two full-size cameras, initializes itself
# as a splitscreen, also taking care to resize each individual camera within it
class SplitScreenCamera(MultiCamera):
    def __init__(self, left_camera, right_camera, **kwargs):
        digest_config(self, kwargs)
        self.left_camera = left_camera
        self.right_camera = right_camera
        
        half_width = self.pixel_shape[1] / 2
        for camera in [self.left_camera, self.right_camera]:
            camera.pixel_shape = (self.pixel_shape[0], half_width) # TODO: Round up on one if width is odd
            camera.init_background()
            camera.resize_space_shape()
            camera.reset()

        MultiCamera.__init__(self, (left_camera, (0, 0)), (right_camera, (0, half_width)))


