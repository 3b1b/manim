from __future__ import annotations

import numpy as np
from PIL import Image

from manimlib.constants import DL, DR, UL, UR
from manimlib.mobject.mobject import Mobject
from manimlib.utils.bezier import inverse_interpolate
from manimlib.utils.images import get_full_raster_image_path
from manimlib.utils.iterables import listify
from manimlib.utils.iterables import resize_with_interpolation

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence, Tuple
    from manimlib.typing import Vect3


class ImageMobject(Mobject):
    shader_folder: str = "image"
    shader_dtype: Sequence[Tuple[str, type, Tuple[int]]] = [
        ('point', np.float32, (3,)),
        ('im_coords', np.float32, (2,)),
        ('opacity', np.float32, (1,)),
    ]

    def __init__(        
        self,
        filename: str,
        height: float = 4.0,
        **kwargs
    ):
        self.height = height
        self.image_path = get_full_raster_image_path(filename)
        self.image = Image.open(self.image_path)
        super().__init__(texture_paths={"Texture": self.image_path}, **kwargs)

    def init_data(self) -> None:
        self.data = {
            "points": np.array([UL, DL, UR, DR]),
            "im_coords": np.array([(0, 0), (0, 1), (1, 0), (1, 1)]),
            "opacity": self.opacity * np.ones((4, 1)),
        }

    def init_points(self) -> None:
        size = self.image.size
        self.set_width(2 * size[0] / size[1], stretch=True)
        self.set_height(self.height)

    def set_opacity(self, opacity: float, recurse: bool = True):
        op_arr = np.array([[o] for o in listify(opacity)])
        for mob in self.get_family(recurse):
            mob.data["opacity"][:] = resize_with_interpolation(op_arr, mob.get_num_points())
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
        ))
        return np.array(rgb) / 255

    def get_shader_data(self) -> np.ndarray:
        shader_data = super().get_shader_data()
        self.read_data_to_shader(shader_data, "im_coords", "im_coords")
        self.read_data_to_shader(shader_data, "opacity", "opacity")
        return shader_data
