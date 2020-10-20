"A camera converts the mobjects contained in a Scene into an array of pixels."


__all__ = ["Camera", "BackgroundColoredVMobjectDisplayer"]


import itertools as it
import operator as op
import time
import copy

from PIL import Image
from scipy.spatial.distance import pdist
import cairo
import numpy as np

from .. import logger, config, camera_config
from ..constants import *
from ..mobject.types.image_mobject import AbstractImageMobject
from ..mobject.mobject import Mobject
from ..mobject.types.point_cloud_mobject import PMobject
from ..mobject.types.vectorized_mobject import VMobject
from ..utils.color import color_to_int_rgba, BLACK
from ..utils.config_ops import digest_config
from ..utils.images import get_full_raster_image_path
from ..utils.iterables import list_difference_update
from ..utils.iterables import remove_list_redundancies
from ..utils.simple_functions import fdiv
from ..utils.space_ops import angle_of_vector
from ..utils.space_ops import get_norm
from ..utils.family import extract_mobject_family_members


class Camera(object):
    """Base camera class.

    This is the object which takes care of what exactly is displayed
    on screen at any given moment.

    Some important CONFIG values and local variables to note are:

    background_image : :class:`str`, optional
        The path to an image that should be the background image.
        If not set, the background is filled with `self.background_color`

    pixel_height : :class:`int`, optional
        The height of the scene in pixels.

    """

    CONFIG = {
        "background_image": None,
        # Note: frame height and width will be resized to match
        # the pixel aspect ratio
        "frame_center": ORIGIN,
        "background_color": BLACK,
        "background_opacity": 1,
        # Points in vectorized mobjects with norm greater
        # than this value will be rescaled.
        "image_mode": "RGBA",
        "n_channels": 4,
        "pixel_array_dtype": "uint8",
        # z_buff_func is only used if the flag above is set to True.
        # round z coordinate to nearest hundredth when comparring
        "z_buff_func": lambda m: np.round(m.get_center()[2], 2),
        "cairo_line_width_multiple": 0.01,
        "use_z_index": True,
    }

    def __init__(self, video_quality_config, background=None, **kwargs):
        """Initialises the Camera.

        Parameters
        ----------
        background : optional
            What self.background should be, by default None as will be set later.
        **kwargs
            Any local variables to be set.
        """
        digest_config(self, kwargs, locals())

        # All of the following are set to EITHER the value passed via kwargs,
        # OR the value stored in the global config dict at the time of
        # _instance construction_.  Before, they were in the CONFIG dict, which
        # is a class attribute and is defined at the time of _class
        # definition_.  This did not allow for creating two Cameras with
        # different configurations in the same session.
        for attr in [
            "pixel_height",
            "pixel_width",
            "frame_height",
            "frame_width",
            "frame_rate",
        ]:
            setattr(self, attr, kwargs.get(attr, config[attr]))

        # This one is in the same boat as the above, but it doesn't have the
        # same name as the corresponding key so it has to be handled on its own
        self.max_allowable_norm = config["frame_width"]

        self.rgb_max_val = np.iinfo(self.pixel_array_dtype).max
        self.pixel_array_to_cairo_context = {}

        # Contains the correct method to process a list of Mobjects of the
        # corresponding class.  If a Mobject is not an instance of a class in
        # this dict (or an instance of a class that inherits from a class in
        # this dict), then it cannot be rendered.

        self.init_background()
        self.resize_frame_shape()
        self.reset()

    def __deepcopy__(self, memo):
        # This is to address a strange bug where deepcopying
        # will result in a segfault, which is somehow related
        # to the aggdraw library
        self.canvas = None
        return copy.copy(self)

    def type_or_raise(self, mobject):
        """Return the type of mobject, if it is a type that can be rendered.

        If `mobject` is an instance of a class that inherits from a class that
        can be rendered, return the super class.  For example, an instance of a
        Square is also an instance of VMobject, and these can be rendered.
        Therefore, `type_or_raise(Square())` returns True.

        Parameters
        ----------
        mobject : :class:`~.Mobject`
            The object to take the type of.

        Notes
        -----
        For a list of classes that can currently be rendered, see :meth:`display_funcs`.

        Returns
        -------
        Type[:class:`~.Mobject`]
            The type of mobjects, if it can be rendered.

        Raises
        ------
        :exc:`TypeError`
            When mobject is not an instance of a class that can be rendered.
        """
        self.display_funcs = {
            VMobject: self.display_multiple_vectorized_mobjects,
            PMobject: self.display_multiple_point_cloud_mobjects,
            AbstractImageMobject: self.display_multiple_image_mobjects,
            Mobject: lambda batch, pa: batch,  # Do nothing
        }
        # We have to check each type in turn because we are dealing with
        # super classes.  For example, if square = Square(), then
        # type(square) != VMobject, but isinstance(square, VMobject) == True.
        for _type in self.display_funcs:
            if isinstance(mobject, _type):
                return _type
        else:
            raise TypeError(f"Displaying an object of class {_type} is not supported")

    def reset_pixel_shape(self, new_height, new_width):
        """This method resets the height and width
        of a single pixel to the passed new_heigh and new_width.

        Parameters
        ----------
        new_height : int, float
            The new height of the entire scene in pixels
        new_width : int, float
            The new width of the entire scene in pixels
        """
        self.pixel_width = new_width
        self.pixel_height = new_height
        self.init_background()
        self.resize_frame_shape()
        self.reset()

    def resize_frame_shape(self, fixed_dimension=0):
        """
        Changes frame_shape to match the aspect ratio
        of the pixels, where fixed_dimension determines
        whether frame_height or frame_width
        remains fixed while the other changes accordingly.

        Parameters
        ----------
        fixed_dimension : int
            If 0, height is scaled with respect to width
            else, width is scaled with respect to height.
        """
        pixel_height = self.pixel_height
        pixel_width = self.pixel_width
        frame_height = self.frame_height
        frame_width = self.frame_width
        aspect_ratio = fdiv(pixel_width, pixel_height)
        if fixed_dimension == 0:
            frame_height = frame_width / aspect_ratio
        else:
            frame_width = aspect_ratio * frame_height
        self.frame_height = frame_height
        self.frame_width = frame_width

    def init_background(self):
        """Initialize the background.
        If self.background_image is the path of an image
        the image is set as background; else, the default
        background color fills the background.
        """
        height = self.pixel_height
        width = self.pixel_width
        if self.background_image is not None:
            path = get_full_raster_image_path(self.background_image)
            image = Image.open(path).convert(self.image_mode)
            # TODO, how to gracefully handle backgrounds
            # with different sizes?
            self.background = np.array(image)[:height, :width]
            self.background = self.background.astype(self.pixel_array_dtype)
        else:
            background_rgba = color_to_int_rgba(
                self.background_color, self.background_opacity
            )
            self.background = np.zeros(
                (height, width, self.n_channels), dtype=self.pixel_array_dtype
            )
            self.background[:, :] = background_rgba

    def get_image(self, pixel_array=None):
        """Returns an image from the passed
        pixel array, or from the current frame
        if the passed pixel array is none.

        Parameters
        ----------
        pixel_array : np.array, list, tuple, optional
            The pixel array from which to get an image, by default None

        Returns
        -------
        PIL.Image
            The PIL image of the array.
        """
        if pixel_array is None:
            pixel_array = self.pixel_array
        return Image.fromarray(pixel_array, mode=self.image_mode)

    def convert_pixel_array(self, pixel_array, convert_from_floats=False):
        """Converts a pixel array from values that have floats in then
        to proper RGB values.

        Parameters
        ----------
        pixel_array : np.array, list, tuple
            Pixel array to convert.
        convert_from_floats : bool, optional
            Whether or not to convert float values to ints, by default False

        Returns
        -------
        np.array
            The new, converted pixel array.
        """
        retval = np.array(pixel_array)
        if convert_from_floats:
            retval = np.apply_along_axis(
                lambda f: (f * self.rgb_max_val).astype(self.pixel_array_dtype),
                2,
                retval,
            )
        return retval

    def set_pixel_array(self, pixel_array, convert_from_floats=False):
        """Sets the pixel array of the camera to the passed pixel array.

        Parameters
        ----------
        pixel_array : np.array, list, tuple
            The pixel array to convert and then set as the camera's pixel array.
        convert_from_floats : bool, optional
            Whether or not to convert float values to proper RGB values, by default False
        """
        converted_array = self.convert_pixel_array(pixel_array, convert_from_floats)
        if not (
            hasattr(self, "pixel_array")
            and self.pixel_array.shape == converted_array.shape
        ):
            self.pixel_array = converted_array
        else:
            # Set in place
            self.pixel_array[:, :, :] = converted_array[:, :, :]

    def set_background(self, pixel_array, convert_from_floats=False):
        """Sets the background to the passed pixel_array after converting
        to valid RGB values.

        Parameters
        ----------
        pixel_array : np.array, list, tuple
            The pixel array to set the background to.
        convert_from_floats : bool, optional
            Whether or not to convert floats values to proper RGB valid ones, by default False
        """
        self.background = self.convert_pixel_array(pixel_array, convert_from_floats)

    # TODO, this should live in utils, not as a method of Camera
    def make_background_from_func(self, coords_to_colors_func):
        """
        Makes a pixel array for the background by using coords_to_colors_func to determine each pixel's color. Each input
        pixel's color. Each input to coords_to_colors_func is an (x, y) pair in space (in ordinary space coordinates; not
        pixel coordinates), and each output is expected to be an RGBA array of 4 floats.

        Parameters
        ----------
        coords_to_colors_func : function
            The function whose input is an (x,y) pair of coordinats and
            whose return values must be the colors for that point
        Returns
        -------
        np.array
            The pixel array which can then be passed to set_background.
        """

        logger.info(
            "Starting set_background; for reference, the current time is ",
            time.strftime("%H:%M:%S"),
        )
        coords = self.get_coords_of_all_pixels()
        new_background = np.apply_along_axis(coords_to_colors_func, 2, coords)
        logger.info(
            "Ending set_background; for reference, the current time is ",
            time.strftime("%H:%M:%S"),
        )

        return self.convert_pixel_array(new_background, convert_from_floats=True)

    def set_background_from_func(self, coords_to_colors_func):
        """
        Sets the background to a pixel array using coords_to_colors_func to determine each pixel's color. Each input
        pixel's color. Each input to coords_to_colors_func is an (x, y) pair in space (in ordinary space coordinates; not
        pixel coordinates), and each output is expected to be an RGBA array of 4 floats.

        Parameters
        ----------
        coords_to_colors_func : function
            The function whose input is an (x,y) pair of coordinats and
            whose return values must be the colors for that point
        """
        self.set_background(self.make_background_from_func(coords_to_colors_func))

    def reset(self):
        """Resets the camera's pixel array
        to that of the background

        Returns
        -------
        Camera
            The camera object after setting the pixel array.
        """ ""
        self.set_pixel_array(self.background)
        return self

    def set_frame_to_background(self, background):
        self.set_pixel_array(background)

    ####

    def get_mobjects_to_display(
        self, mobjects, include_submobjects=True, excluded_mobjects=None
    ):
        """Used to get the list of mobjects to display
        with the camera.

        Parameters
        ----------
        mobjects : Mobject
            The Mobjects
        include_submobjects : bool, optional
            Whether or not to include the submobjects of mobjects, by default True
        excluded_mobjects : list, optional
            Any mobjects to exclude, by default None

        Returns
        -------
        list
            list of mobjects
        """
        if include_submobjects:
            mobjects = extract_mobject_family_members(
                mobjects, use_z_index=self.use_z_index, only_those_with_points=True
            )
            if excluded_mobjects:
                all_excluded = extract_mobject_family_members(
                    excluded_mobjects, use_z_index=self.use_z_index
                )
                mobjects = list_difference_update(mobjects, all_excluded)
        return mobjects

    def is_in_frame(self, mobject):
        """Checks whether the passed mobject is in
        frame or not.

        Parameters
        ----------
        mobject : Mobject
            The mobject for which the checking needs to be done.

        Returns
        -------
        bool
            True if in frame, False otherwise.
        """
        fc = self.frame_center
        fh = self.frame_height
        fw = self.frame_width
        return not reduce(
            op.or_,
            [
                mobject.get_right()[0] < fc[0] - fw,
                mobject.get_bottom()[1] > fc[1] + fh,
                mobject.get_left()[0] > fc[0] + fw,
                mobject.get_top()[1] < fc[1] - fh,
            ],
        )

    def capture_mobject(
        self, mobject, **kwargs
    ):  # TODO Write better docstrings for this method.
        return self.capture_mobjects([mobject], **kwargs)

    def capture_mobjects(self, mobjects, **kwargs):
        """Capture mobjects by printing them on :attr:`pixel_array`.

        This is the essential function that converts the contents of a Scene
        into an array, which is then converted to an image or video.

        Parameters
        ----------
        mobjects : :class:`~.Mobject`
            Mobjects to capture.

        kwargs : Any
            Keyword arguments to be passed to :meth:`get_mobjects_to_display`.

        Notes
        -----
        For a list of classes that can currently be rendered, see :meth:`display_funcs`.

        """
        # The mobjects will be processed in batches (or runs) of mobjects of
        # the same type.  That is, if the list mobjects contains objects of
        # types [VMobject, VMobject, VMobject, PMobject, PMobject, VMobject],
        # then they will be captured in three batches: [VMobject, VMobject,
        # VMobject], [PMobject, PMobject], and [VMobject].  This must be done
        # without altering their order.  it.groupby computes exactly this
        # partition while at the same time preserving order.
        mobjects = self.get_mobjects_to_display(mobjects, **kwargs)
        for group_type, group in it.groupby(mobjects, self.type_or_raise):
            self.display_funcs[group_type](list(group), self.pixel_array)

    # Methods associated with svg rendering

    # NOTE: None of the methods below have been mentioned outside of their definitions. Their DocStrings are not as
    # detailed as possible.

    def get_cached_cairo_context(self, pixel_array):
        """Returns the cached cairo context of the passed
        pixel array if it exists, and None if it doesn't.

        Parameters
        ----------
        pixel_array : np.array
            The pixel array to check.

        Returns
        -------
        cairo.Context
            The cached cairo context.
        """
        return self.pixel_array_to_cairo_context.get(id(pixel_array), None)

    def cache_cairo_context(self, pixel_array, ctx):
        """Caches the passed Pixel array into a Cairo Context

        Parameters
        ----------
        pixel_array : np.array
            The pixel array to cache
        ctx : cairo.Context
            The context to cache it into.
        """
        self.pixel_array_to_cairo_context[id(pixel_array)] = ctx

    def get_cairo_context(self, pixel_array):
        """Returns the cairo context for a pixel array after
        caching it to self.pixel_array_to_cairo_context
        If that array has already been cached, it returns the
        cached version instead.

        Parameters
        ----------
        pixel_array : np.array
            The Pixel array to get the cairo context of.

        Returns
        -------
        cairo.Context
            The cairo context of the pixel array.
        """
        cached_ctx = self.get_cached_cairo_context(pixel_array)
        if cached_ctx:
            return cached_ctx
        pw = self.pixel_width
        ph = self.pixel_height
        fw = self.frame_width
        fh = self.frame_height
        fc = self.frame_center
        surface = cairo.ImageSurface.create_for_data(
            pixel_array, cairo.FORMAT_ARGB32, pw, ph
        )
        ctx = cairo.Context(surface)
        ctx.scale(pw, ph)
        ctx.set_matrix(
            cairo.Matrix(
                fdiv(pw, fw),
                0,
                0,
                -fdiv(ph, fh),
                (pw / 2) - fc[0] * fdiv(pw, fw),
                (ph / 2) + fc[1] * fdiv(ph, fh),
            )
        )
        self.cache_cairo_context(pixel_array, ctx)
        return ctx

    def display_multiple_vectorized_mobjects(self, vmobjects, pixel_array):
        """Displays multiple VMobjects in the pixel_array

        Parameters
        ----------
        vmobjects : list
            list of VMobjects to display
        pixel_array : np.array
            The pixel array
        """
        if len(vmobjects) == 0:
            return
        batch_file_pairs = it.groupby(
            vmobjects, lambda vm: vm.get_background_image_file()
        )
        for file_name, batch in batch_file_pairs:
            if file_name:
                self.display_multiple_background_colored_vmobjects(batch, pixel_array)
            else:
                self.display_multiple_non_background_colored_vmobjects(
                    batch, pixel_array
                )

    def display_multiple_non_background_colored_vmobjects(self, vmobjects, pixel_array):
        """Displays multiple VMobjects in the cairo context, as long as they don't have
        background colors.

        Parameters
        ----------
        vmobjects : list
            list of the VMobjects
        pixel_array : np.ndarray
            The Pixel array to add the VMobjects to.
        """
        ctx = self.get_cairo_context(pixel_array)
        for vmobject in vmobjects:
            self.display_vectorized(vmobject, ctx)

    def display_vectorized(self, vmobject, ctx):
        """Displays a VMobject in the cairo context

        Parameters
        ----------
        vmobject : VMobject
            The Vectorized Mobject to display
        ctx : cairo.Context
            The cairo context to use.

        Returns
        -------
        Camera
            The camera object
        """
        self.set_cairo_context_path(ctx, vmobject)
        self.apply_stroke(ctx, vmobject, background=True)
        self.apply_fill(ctx, vmobject)
        self.apply_stroke(ctx, vmobject)
        return self

    def set_cairo_context_path(self, ctx, vmobject):
        """Sets a path for the cairo context with the vmobject passed

        Parameters
        ----------
        ctx : cairo.Context
            The cairo context
        vmobject : VMobject
            The VMobject

        Returns
        -------
        Camera
            Camera object after setting cairo_context_path
        """
        points = self.transform_points_pre_display(vmobject, vmobject.points)
        # TODO, shouldn't this be handled in transform_points_pre_display?
        # points = points - self.get_frame_center()
        if len(points) == 0:
            return

        ctx.new_path()
        subpaths = vmobject.gen_subpaths_from_points_2d(points)
        for subpath in subpaths:
            quads = vmobject.gen_cubic_bezier_tuples_from_points(subpath)
            ctx.new_sub_path()
            start = subpath[0]
            ctx.move_to(*start[:2])
            for p0, p1, p2, p3 in quads:
                ctx.curve_to(*p1[:2], *p2[:2], *p3[:2])
            if vmobject.consider_points_equals_2d(subpath[0], subpath[-1]):
                ctx.close_path()
        return self

    def set_cairo_context_color(self, ctx, rgbas, vmobject):
        """Sets the color of the cairo context

        Parameters
        ----------
        ctx : cairo.Context
            The cairo context
        rgbas : np.ndarray
            The RGBA array with which to color the context.
        vmobject : VMobject
            The VMobject with which to set the color.

        Returns
        -------
        Camera
            The camera object
        """
        if len(rgbas) == 1:
            # Use reversed rgb because cairo surface is
            # encodes it in reverse order
            ctx.set_source_rgba(*rgbas[0][2::-1], rgbas[0][3])
        else:
            points = vmobject.get_gradient_start_and_end_points()
            points = self.transform_points_pre_display(vmobject, points)
            pat = cairo.LinearGradient(*it.chain(*[point[:2] for point in points]))
            step = 1.0 / (len(rgbas) - 1)
            offsets = np.arange(0, 1 + step, step)
            for rgba, offset in zip(rgbas, offsets):
                pat.add_color_stop_rgba(offset, *rgba[2::-1], rgba[3])
            ctx.set_source(pat)
        return self

    def apply_fill(self, ctx, vmobject):
        """Fills the cairo context

        Parameters
        ----------
        ctx : cairo.Context
            The cairo context
        vmobject : VMobject
            The VMobject

        Returns
        -------
        Camera
            The camera object.
        """
        self.set_cairo_context_color(ctx, self.get_fill_rgbas(vmobject), vmobject)
        ctx.fill_preserve()
        return self

    def apply_stroke(self, ctx, vmobject, background=False):
        """Applies a stroke to the VMobject in the cairo context.

        Parameters
        ----------
        ctx : cairo.Context
            The cairo context
        vmobject : VMobject
            The VMobject
        background : bool, optional
            Whether or not to consider the background when applying this
            stroke width, by default False

        Returns
        -------
        Camera
            The camera object with the stroke applied.
        """
        width = vmobject.get_stroke_width(background)
        if width == 0:
            return self
        self.set_cairo_context_color(
            ctx, self.get_stroke_rgbas(vmobject, background=background), vmobject
        )
        ctx.set_line_width(
            width
            * self.cairo_line_width_multiple
            *
            # This ensures lines have constant width
            # as you zoom in on them.
            (self.frame_width / self.frame_width)
        )
        ctx.stroke_preserve()
        return self

    def get_stroke_rgbas(self, vmobject, background=False):
        """Get's the RGBA array for the stroke of the passed
        VMobject.

        Parameters
        ----------
        vmobject : VMobject
            The VMobject
        background : bool, optional
            Whether or not to consider the background when getting the stroke
            RGBAs, by default False

        Returns
        -------
        np.ndarray
            The RGBA array of the stroke.
        """
        return vmobject.get_stroke_rgbas(background)

    def get_fill_rgbas(self, vmobject):
        """Returns the RGBA array of the fill of the passed VMobject

        Parameters
        ----------
        vmobject : VMobject
            The VMobject

        Returns
        -------
        np.array
            The RGBA Array of the fill of the VMobject
        """
        return vmobject.get_fill_rgbas()

    def get_background_colored_vmobject_displayer(self):
        """Returns the background_colored_vmobject_displayer
        if it exists or makes one and returns it if not.

        Returns
        -------
        BackGroundColoredVMobjectDisplayer
            Object that displays VMobjects that have the same color
            as the background.
        """
        # Quite wordy to type out a bunch
        bcvd = "background_colored_vmobject_displayer"
        if not hasattr(self, bcvd):
            setattr(self, bcvd, BackgroundColoredVMobjectDisplayer(self))
        return getattr(self, bcvd)

    def display_multiple_background_colored_vmobjects(self, cvmobjects, pixel_array):
        """Displays multiple vmobjects that have the same color as the background.

        Parameters
        ----------
        cvmobjects : list
            List of Colored VMobjects
        pixel_array : np.array
            The pixel array.

        Returns
        -------
        Camera
            The camera object.
        """
        displayer = self.get_background_colored_vmobject_displayer()
        cvmobject_pixel_array = displayer.display(*cvmobjects)
        self.overlay_rgba_array(pixel_array, cvmobject_pixel_array)
        return self

    # Methods for other rendering

    # NOTE: Out of the following methods, only `transform_points_pre_display` and `points_to_pixel_coords` have been mentioned outside of their definitions.
    # As a result, the other methods do not have as detailed docstrings as would be preferred.

    def display_multiple_point_cloud_mobjects(self, pmobjects, pixel_array):
        """Displays multiple PMobjects by modifying the passed pixel array.

        Parameters
        ----------
        pmobjects : list
            List of PMobjects
        pixel_array : np.array
            The pixel array to modify.
        """
        for pmobject in pmobjects:
            self.display_point_cloud(
                pmobject,
                pmobject.points,
                pmobject.rgbas,
                self.adjusted_thickness(pmobject.stroke_width),
                pixel_array,
            )

    def display_point_cloud(self, pmobject, points, rgbas, thickness, pixel_array):
        """Displays a PMobject by modifying the Pixel array suitably..
        TODO: Write a description for the rgbas argument.
        Parameters
        ----------
        pmobject : PMobject
            Point Cloud Mobject
        points : list
            The points to display in the point cloud mobject
        rgbas : np.array

        thickness : int, float
            The thickness of each point of the PMobject
        pixel_array : np.array
            The pixel array to modify.
        """
        if len(points) == 0:
            return
        pixel_coords = self.points_to_pixel_coords(pmobject, points)
        pixel_coords = self.thickened_coordinates(pixel_coords, thickness)
        rgba_len = pixel_array.shape[2]

        rgbas = (self.rgb_max_val * rgbas).astype(self.pixel_array_dtype)
        target_len = len(pixel_coords)
        factor = target_len // len(rgbas)
        rgbas = np.array([rgbas] * factor).reshape((target_len, rgba_len))

        on_screen_indices = self.on_screen_pixels(pixel_coords)
        pixel_coords = pixel_coords[on_screen_indices]
        rgbas = rgbas[on_screen_indices]

        ph = self.pixel_height
        pw = self.pixel_width

        flattener = np.array([1, pw], dtype="int")
        flattener = flattener.reshape((2, 1))
        indices = np.dot(pixel_coords, flattener)[:, 0]
        indices = indices.astype("int")

        new_pa = pixel_array.reshape((ph * pw, rgba_len))
        new_pa[indices] = rgbas
        pixel_array[:, :] = new_pa.reshape((ph, pw, rgba_len))

    def display_multiple_image_mobjects(self, image_mobjects, pixel_array):
        """Displays multiple image mobjects by modifiying the passed pixel_array.

        Parameters
        ----------
        image_mobjects : list
            list of ImageMobjects
        pixel_array : np.array
            The pixel array to modify.
        """
        for image_mobject in image_mobjects:
            self.display_image_mobject(image_mobject, pixel_array)

    def display_image_mobject(self, image_mobject, pixel_array):
        """Displays an ImageMobject by changing the pixel_array suitably.

        Parameters
        ----------
        image_mobject : ImageMobject
            The imageMobject to display
        pixel_array : np.ndarray
            The Pixel array to put the imagemobject in.
        """
        corner_coords = self.points_to_pixel_coords(image_mobject, image_mobject.points)
        ul_coords, ur_coords, dl_coords = corner_coords
        right_vect = ur_coords - ul_coords
        down_vect = dl_coords - ul_coords
        center_coords = ul_coords + (right_vect + down_vect) / 2

        sub_image = Image.fromarray(image_mobject.get_pixel_array(), mode="RGBA")

        # Reshape
        pixel_width = max(int(pdist([ul_coords, ur_coords])), 1)
        pixel_height = max(int(pdist([ul_coords, dl_coords])), 1)
        sub_image = sub_image.resize(
            (pixel_width, pixel_height), resample=Image.BICUBIC
        )

        # Rotate
        angle = angle_of_vector(right_vect)
        adjusted_angle = -int(360 * angle / TAU)
        if adjusted_angle != 0:
            sub_image = sub_image.rotate(
                adjusted_angle, resample=Image.BICUBIC, expand=1
            )

        # TODO, there is no accounting for a shear...

        # Paste into an image as large as the camear's pixel array
        full_image = Image.fromarray(
            np.zeros((self.pixel_height, self.pixel_width)), mode="RGBA"
        )
        new_ul_coords = center_coords - np.array(sub_image.size) / 2
        new_ul_coords = new_ul_coords.astype(int)
        full_image.paste(
            sub_image,
            box=(
                new_ul_coords[0],
                new_ul_coords[1],
                new_ul_coords[0] + sub_image.size[0],
                new_ul_coords[1] + sub_image.size[1],
            ),
        )
        # Paint on top of existing pixel array
        self.overlay_PIL_image(pixel_array, full_image)

    def overlay_rgba_array(self, pixel_array, new_array):
        """Overlays an RGBA array on top of the given Pixel array.

        Parameters
        ----------
        pixel_array : np.array
            The original pixel array to modify.
        new_array : np.array
            The new pixel array to overlay.
        """
        self.overlay_PIL_image(pixel_array, self.get_image(new_array))

    def overlay_PIL_image(self, pixel_array, image):
        """Overlays a PIL image on the passed pixel array.

        Parameters
        ----------
        pixel_array : np.ndarray
            The Pixel array
        image : PIL.Image
            The Image to overlay.
        """
        pixel_array[:, :] = np.array(
            Image.alpha_composite(self.get_image(pixel_array), image), dtype="uint8"
        )

    def adjust_out_of_range_points(self, points):
        """If any of the points in the passed array are out of
        the viable range, they are adjusted suitably.

        Parameters
        ----------
        points : np.array
            The points to adjust

        Returns
        -------
        np.array
            The adjusted points.
        """
        if not np.any(points > self.max_allowable_norm):
            return points
        norms = np.apply_along_axis(get_norm, 1, points)
        violator_indices = norms > self.max_allowable_norm
        violators = points[violator_indices, :]
        violator_norms = norms[violator_indices]
        reshaped_norms = np.repeat(
            violator_norms.reshape((len(violator_norms), 1)), points.shape[1], 1
        )
        rescaled = self.max_allowable_norm * violators / reshaped_norms
        points[violator_indices] = rescaled
        return points

    def transform_points_pre_display(
        self, mobject, points
    ):  # TODO: Write more detailed docstrings for this method.
        # NOTE: There seems to be an unused argument `mobject`.

        # Subclasses (like ThreeDCamera) may want to
        # adjust points futher before they're shown
        if not np.all(np.isfinite(points)):
            # TODO, print some kind of warning about
            # mobject having invalid points?
            points = np.zeros((1, 3))
        return points

    def points_to_pixel_coords(
        self, mobject, points
    ):  # TODO: Write more detailed docstrings for this method.
        points = self.transform_points_pre_display(mobject, points)
        shifted_points = points - self.frame_center

        result = np.zeros((len(points), 2))
        pixel_height = self.pixel_height
        pixel_width = self.pixel_width
        frame_height = self.frame_height
        frame_width = self.frame_width
        width_mult = pixel_width / frame_width
        width_add = pixel_width / 2
        height_mult = pixel_height / frame_height
        height_add = pixel_height / 2
        # Flip on y-axis as you go
        height_mult *= -1

        result[:, 0] = shifted_points[:, 0] * width_mult + width_add
        result[:, 1] = shifted_points[:, 1] * height_mult + height_add
        return result.astype("int")

    def on_screen_pixels(self, pixel_coords):
        """Returns array of pixels that are on the screen from a given
        array of pixel_coordinates

        Parameters
        ----------
        pixel_coords : np.array
            The pixel coords to check.

        Returns
        -------
        np.array
            The pixel coords on screen.
        """
        return reduce(
            op.and_,
            [
                pixel_coords[:, 0] >= 0,
                pixel_coords[:, 0] < self.pixel_width,
                pixel_coords[:, 1] >= 0,
                pixel_coords[:, 1] < self.pixel_height,
            ],
        )

    def adjusted_thickness(self, thickness):
        """

        Parameters
        ----------
        thickness : int, float

        Returns
        -------
        float

        """
        # TODO: This seems...unsystematic
        big_sum = op.add(
            camera_config["default_pixel_height"], camera_config["default_pixel_width"]
        )
        this_sum = op.add(self.pixel_height, self.pixel_width)
        factor = fdiv(big_sum, this_sum)
        return 1 + (thickness - 1) / factor

    def get_thickening_nudges(self, thickness):
        """

        Parameters
        ----------
        thickness : int, float

        Returns
        -------
        np.array

        """
        thickness = int(thickness)
        _range = list(range(-thickness // 2 + 1, thickness // 2 + 1))
        return np.array(list(it.product(_range, _range)))

    def thickened_coordinates(self, pixel_coords, thickness):
        """Returns thickened coordinates for a passed array of pixel coords and
        a thickness to thicken by.

        Parameters
        ----------
        pixel_coords : np.array
            Pixel coordinates
        thickness : int, float
            Thickness

        Returns
        -------
        np.array
            Array of thickened pixel coords.
        """
        nudges = self.get_thickening_nudges(thickness)
        pixel_coords = np.array([pixel_coords + nudge for nudge in nudges])
        size = pixel_coords.size
        return pixel_coords.reshape((size // 2, 2))

    # TODO, reimplement using cairo matrix
    def get_coords_of_all_pixels(self):
        """Returns the cartesian coordinates of each pixel.

        Returns
        -------
        np.ndarray
            The array of cartesian coordinates.
        """
        # These are in x, y order, to help me keep things straight
        full_space_dims = np.array([self.frame_width, self.frame_height])
        full_pixel_dims = np.array([self.pixel_width, self.pixel_height])

        # These are addressed in the same y, x order as in pixel_array, but the values in them
        # are listed in x, y order
        uncentered_pixel_coords = np.indices([self.pixel_height, self.pixel_width])[
            ::-1
        ].transpose(1, 2, 0)
        uncentered_space_coords = fdiv(
            uncentered_pixel_coords * full_space_dims, full_pixel_dims
        )
        # Could structure above line's computation slightly differently, but figured (without much
        # thought) multiplying by frame_shape first, THEN dividing by pixel_shape, is probably
        # better than the other order, for avoiding underflow quantization in the division (whereas
        # overflow is unlikely to be a problem)

        centered_space_coords = uncentered_space_coords - fdiv(full_space_dims, 2)

        # Have to also flip the y coordinates to account for pixel array being listed in
        # top-to-bottom order, opposite of screen coordinate convention
        centered_space_coords = centered_space_coords * (1, -1)

        return centered_space_coords


# NOTE: The methods of the following class have not been mentioned outside of their definitons.
# Their DocStrings are not as detailed as preferred.
class BackgroundColoredVMobjectDisplayer(object):
    def __init__(self, camera):
        """
        Parameters
        ----------
        camera : Camera
            Camera object to use.
        """
        self.camera = camera
        self.file_name_to_pixel_array_map = {}
        self.pixel_array = np.array(camera.pixel_array)
        self.reset_pixel_array()

    def reset_pixel_array(self):
        self.pixel_array[:, :] = 0

    def resize_background_array(
        self, background_array, new_width, new_height, mode="RGBA"
    ):
        """Resizes the pixel array represinting the background.

        Parameters
        ----------
        background_array : np.array
            The pixel
        new_width : int, float
            The new width of the background
        new_height : int, float
            The new height of the background
        mode : str, optional
            The PIL image mode, by default "RGBA"

        Returns
        -------
        np.array
            The numpy pixel array of the resized background.
        """
        image = Image.fromarray(background_array)
        image = image.convert(mode)
        resized_image = image.resize((new_width, new_height))
        return np.array(resized_image)

    def resize_background_array_to_match(self, background_array, pixel_array):
        """Resizes the background array to match the passed pixel array.

        Parameters
        ----------
        background_array : np.array
            The prospective pixel array.
        pixel_array : np.array
            The pixel array whose width and height should be matched.

        Returns
        -------
        np.array
            The resized background array.
        """
        height, width = pixel_array.shape[:2]
        mode = "RGBA" if pixel_array.shape[2] == 4 else "RGB"
        return self.resize_background_array(background_array, width, height, mode)

    def get_background_array(self, file_name):
        """Gets the background array that has the passed file_name.

        Parameters
        ----------
        file_name : str
            The file_name of the background image.

        Returns
        -------
        np.ndarray
            The pixel array of the file whose file name is `file_name`
        """
        if file_name in self.file_name_to_pixel_array_map:
            return self.file_name_to_pixel_array_map[file_name]
        full_path = get_full_raster_image_path(file_name)
        image = Image.open(full_path)
        back_array = np.array(image)

        pixel_array = self.pixel_array
        if not np.all(pixel_array.shape == back_array.shape):
            back_array = self.resize_background_array_to_match(back_array, pixel_array)

        self.file_name_to_pixel_array_map[file_name] = back_array
        return back_array

    def display(self, *cvmobjects):
        """Displays the colored VMobjects.

        Parameters
        ----------
        *cvmobjects : VMobject
            The VMobjects

        Returns
        -------
        np.array
            The pixel array with the `cvmobjects` displayed.
        """
        batch_image_file_pairs = it.groupby(
            cvmobjects, lambda cv: cv.get_background_image_file()
        )
        curr_array = None
        for batch, image_file in batch_image_file_pairs:
            background_array = self.get_background_array(image_file)
            pixel_array = self.pixel_array
            self.camera.display_multiple_non_background_colored_vmobjects(
                batch, pixel_array
            )
            new_array = np.array(
                (background_array * pixel_array.astype("float") / 255),
                dtype=self.camera.pixel_array_dtype,
            )
            if curr_array is None:
                curr_array = new_array
            else:
                curr_array = np.maximum(curr_array, new_array)
            self.reset_pixel_array()
        return curr_array
