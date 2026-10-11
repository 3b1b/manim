from __future__ import annotations

import numpy as np
from PIL import Image

from manimlib.constants import DL, DR, UL, UR
from manimlib.mobject.mobject import Mobject
from manimlib.renderer.texture import ImageFile
from manimlib.utils.bezier import inverse_interpolate
from manimlib.utils.images import get_full_raster_image_path
from manimlib.utils.iterables import listify
from manimlib.utils.iterables import resize_with_interpolation

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence, Tuple
    from manimlib.renderer.texture import TextureSource
    from manimlib.typing import Vect3


class ImageMobject(Mobject):
    """
    A textured image object that displays a raster image on a rectangular
    surface in a Manim scene.

    `ImageMobject` inherits from :class:`Mobject` and renders an image using
    a GPU shader and a texture loaded from an image file. Its geometry
    consists of four corner points, while texture coordinates map the
    source image onto those corners. The vertex shader expands the four
    corner records into the triangles needed to render the rectangular
    image.

    The image's aspect ratio is determined by its original pixel dimensions.
    The constructor sets the displayed height and calculates the width
    accordingly, preserving the source image's aspect ratio.

    Parameters
    ----------
    filename : str
        Path or filename of the raster image to load. The path is resolved
        using ``get_full_raster_image_path``.
    height : float, optional
        Initial displayed height of the image in scene coordinates.
        The width is calculated from the source image's aspect ratio.
        Defaults to 4.0.
    **kwargs
        Additional keyword arguments forwarded to :class:`Mobject`.

    Attributes
    ----------
    height : float
        Requested displayed height stored during initialization.
    image_path : str
        Resolved path of the source image file.
    image : PIL.Image.Image
        Image opened through PIL. Its pixel dimensions determine the
        displayed aspect ratio, and its pixel values are used by
        ``point_to_rgb``.
    data_dtype : np.dtype
        Structured data layout containing:

        - ``point``: three-dimensional position of a corner.
        - ``im_coords``: two-dimensional texture coordinate for that corner.
        - ``opacity``: opacity value associated with the corner.

    shader_file : str
        Shader filename used to render the image: ``image.wgsl``.
    verts_per_record : int
        Number of vertices generated for each corner record: 6.

    Examples
    --------
    Load and display an image at the default height:

        image = ImageMobject("example.png")

    Specify the displayed height:

        image = ImageMobject("example.png", height=3.0)

    Position and scale the image using inherited Mobject methods:

        image = ImageMobject("example.png", height=2.5)
        image.shift(RIGHT * 2)
        image.scale(1.2)

    Set the image opacity:

        image.set_opacity(0.5)

    Sample the source image's color at a point in the image's displayed
    coordinates:

        image = ImageMobject("example.png")
        rgb = image.point_to_rgb(image.get_center())

    Methods
    -------
    init_texture(filename)
        Resolve the image path, open the image with PIL, and return an
        ImageFile texture source for rendering.

    init_data()
        Initialize four corner records with their positions, texture
        coordinates, and opacity values.

    get_source_size()
        Return the source image's pixel dimensions as a ``(width, height)``
        tuple.

    init_points()
        Calculate the displayed width from the source aspect ratio, then
        set the image's displayed height.

    set_opacity(opacity, recurse=True)
        Set opacity values in the image's point data. Values are resized
        with interpolation to match the number of point records.

    set_color(color, opacity=None, recurse=None)
        Return the object unchanged. This implementation does not recolor
        the image through the standard Mobject color interface.

    point_to_rgb(point)
        Sample an RGB color from the source image using a point's position
        in the displayed image coordinates.

    Notes
    -----
    - The source image is loaded by ``init_texture``. The resolved path is
      stored in ``image_path``, the PIL image is stored in ``image``, and
      an ``ImageFile`` object is returned as the GPU texture source.
    - The image geometry uses four corner records, ordered as upper-left,
      lower-left, upper-right, and lower-right. Their texture coordinates
      map the source image across the rectangular surface.
    - The ``verts_per_record`` value is 6 because the shader expands the
      four corners into the two triangles required to cover the rectangle.
    - ``get_source_size`` returns pixel dimensions, not dimensions in scene
      coordinates.
    - ``init_points`` computes the width as ``2 * pixel_width / pixel_height``
      before setting the requested height. This establishes the aspect ratio
      independently of the requested displayed height.
    - ``set_opacity`` updates the opacity field in the image's point data.
      Its ``recurse`` argument is accepted for interface compatibility but
      is not used in this implementation.
    - ``set_color`` is intentionally a no-op. The image's visible colors
      come from its texture, so calling this method does not tint the image.
    - ``point_to_rgb`` converts the supplied point's x- and y-coordinates
      into normalized image coordinates using the image's upper-left and
      lower-right corners. It then samples a source pixel and returns its
      first three channels as floating-point RGB values in the range
      approximately 0 to 1.
    - Pixel indices are calculated using integer conversion, so sampling
      selects discrete pixels rather than interpolating between them.
    - The bounds check in ``point_to_rgb`` uses ``and`` between the two
      out-of-range conditions. Consequently, it raises an exception only
      when both normalized coordinates are outside the range [0, 1].
      A point outside only one coordinate's range is not rejected by this
      condition and may produce an unintended pixel lookup.
    - ``point_to_rgb`` assumes the source pixel provides at least three
      channels. It discards any additional channels, such as alpha, and
      returns only RGB.
    """

    shader_file: str = "image.wgsl"
    data_dtype: np.dtype = np.dtype([
        ('point', np.float32, (3,)),
        ('im_coords', np.float32, (2,)),
        ('opacity', np.float32, (1,)),
    ])
    # The four corners are expanded into the two triangles covering them by the vertex
    # shader, six of the vertices drawn doing that and the rest collapsing
    verts_per_record: int = 6

    def __init__(
        self,
        filename: str,
        height: float = 4.0,
        **kwargs
    ):
        self.height = height
        super().__init__(textures={"Texture": self.init_texture(filename)}, **kwargs)

    def init_texture(self, filename: str) -> TextureSource:
        """
        Where the pixels drawn over the four corners come from, which for an image is the
        file itself. Overridden by anything drawing the same quad from somewhere else, a
        frame of a video say, see VideoMobject.
        """
        self.image_path = get_full_raster_image_path(filename)
        self.image = Image.open(self.image_path)
        return ImageFile(self.image_path)

    def init_data(self) -> None:
        super().init_data(length=4)
        self.data["point"] = [UL, DL, UR, DR]
        self.data["im_coords"] = [(0, 0), (0, 1), (1, 0), (1, 1)]
        self.data["opacity"] = self.opacity

    def get_source_size(self) -> Tuple[int, int]:
        """The pixel size of what is drawn, which is what fixes the aspect ratio"""
        return self.image.size

    def init_points(self) -> None:
        width, height = self.get_source_size()
        self.set_width(2 * width / height, stretch=True)
        self.set_height(self.height)

    def set_opacity(self, opacity: float, recurse: bool = True):
        with self.data.being_written() as data:
            data["opacity"][:, 0] = resize_with_interpolation(
                np.array(listify(opacity)),
                self.get_num_points()
            )
        return self

    def set_color(self, color, opacity=None, recurse=None):
        return self

    def point_to_rgb(self, point: Vect3) -> Vect3:
        x0, y0 = self.get_corner(UL)[:2]
        x1, y1 = self.get_corner(DR)[:2]
        x_alpha = inverse_interpolate(x0, x1, point[0])
        y_alpha = inverse_interpolate(y0, y1, point[1])
        if not (0 <= x_alpha <= 1) and (0 <= y_alpha <= 1):
            # TODO, raise smarter exception
            raise Exception("Cannot sample color from outside an image")

        pw, ph = self.image.size
        rgb = self.image.getpixel((
            int((pw - 1) * x_alpha),
            int((ph - 1) * y_alpha),
        ))[:3]
        return np.array(rgb) / 255
