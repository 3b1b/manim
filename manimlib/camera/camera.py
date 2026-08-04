from __future__ import annotations

import numpy as np
import wgpu
from PIL import Image

from manimlib.camera.camera_frame import CameraFrame
from manimlib.constants import BLACK
from manimlib.constants import DEFAULT_RESOLUTION
from manimlib.constants import FRAME_HEIGHT
from manimlib.constants import FRAME_WIDTH
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.mobject import Point
from manimlib.renderer import COLOR_FORMAT
from manimlib.renderer import DEPTH_STENCIL_FORMAT
from manimlib.renderer import Renderer
from manimlib.utils.color import color_to_rgba

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional
    from manimlib.typing import ManimColor, Vect3
    from manimlib.window import Window


class Camera(object):
    def __init__(
        self,
        window: Optional[Window] = None,
        frame_config: dict = dict(),
        # Note: frame height and width will be resized to match this resolution aspect ratio
        resolution=DEFAULT_RESOLUTION,
        fps: int = 30,
        background_color: ManimColor = BLACK,
        background_opacity: float = 1.0,
        light_source_position: Vect3 = np.array([-10, 10, 10]),
        # Although vector graphics handle antialiasing fine
        # without multisampling, for 3d scenes one might want
        # to set samples to be greater than 0.
        samples: int = 0,
    ):
        self.window = window
        self.default_pixel_shape = resolution  # Rename?
        self.fps = fps
        self.light_source_position = light_source_position
        self.samples = samples

        self.background_rgba: list[float] = list(color_to_rgba(
            background_color, background_opacity
        ))
        self.init_frame(**frame_config)
        self.init_renderer()
        self.init_target()
        self.init_light_source()

    def init_frame(self, **config) -> None:
        self.frame = CameraFrame(**config)

    def init_renderer(self) -> None:
        self.renderer = Renderer()

    def init_target(self) -> None:
        """
        What every frame is drawn into: one color texture and one depth-stencil texture,
        whatever the frame is for. Where samples are being taken there is a second color
        texture holding them, which the first is resolved down to.

        This is the whole of it. Under GL there were three framebuffers and a pair of blits,
        because a multisampled buffer cannot be blit with rescaling and because a window
        owns a framebuffer of its own; here a window is somewhere to present a texture to
        rather than somewhere to draw.
        """
        device = self.renderer.device
        self.pixel_shape = self.default_pixel_shape
        width, height = self.pixel_shape
        samples = self.renderer.samples = max(1, self.samples)

        self.color_texture = device.create_texture(
            size=(width, height, 1),
            format=COLOR_FORMAT,
            usage=(
                wgpu.TextureUsage.RENDER_ATTACHMENT
                | wgpu.TextureUsage.COPY_SRC
                | wgpu.TextureUsage.TEXTURE_BINDING
            ),
        )
        self.multisample_texture = None
        if samples > 1:
            self.multisample_texture = device.create_texture(
                size=(width, height, 1),
                format=COLOR_FORMAT,
                usage=wgpu.TextureUsage.RENDER_ATTACHMENT,
                sample_count=samples,
            )
        self.depth_stencil_texture = device.create_texture(
            size=(width, height, 1),
            format=DEPTH_STENCIL_FORMAT,
            usage=wgpu.TextureUsage.RENDER_ATTACHMENT,
            sample_count=samples,
        )

        # A view onto a texture is the same every frame, so they are made along with it
        drawn_into = self.multisample_texture or self.color_texture
        self.color_view = drawn_into.create_view()
        self.resolve_view = self.color_texture.create_view() if samples > 1 else None
        self.depth_stencil_view = self.depth_stencil_texture.create_view()

    def init_light_source(self) -> None:
        self.light_source = Point(self.light_source_position)

    def use_window_fbo(self, use: bool = True):
        # Which size to draw at when there is a window, see the port plan's decision 6.
        # Nothing to do until the window is ported.
        pass

    def get_attachments(self) -> dict:
        """
        The textures a frame is drawn into, and what to do with what they already hold.
        Clearing them is what beginning the pass does, so nothing needs clearing by hand:
        under GL this was a clear of the color buffer and another of the stencil.
        """
        return {
            "color_attachments": [{
                "view": self.color_view,
                "resolve_target": self.resolve_view,
                "clear_value": tuple(self.background_rgba),
                "load_op": wgpu.LoadOp.clear,
                "store_op": wgpu.StoreOp.store,
            }],
            "depth_stencil_attachment": {
                "view": self.depth_stencil_view,
                "depth_clear_value": 1.0,
                "depth_load_op": wgpu.LoadOp.clear,
                "depth_store_op": wgpu.StoreOp.store,
                "stencil_clear_value": 0,
                "stencil_load_op": wgpu.LoadOp.clear,
                "stencil_store_op": wgpu.StoreOp.store,
            },
        }

    def get_frame_bytes(self) -> bytes:
        """
        The frame as it stands, four bytes to a pixel, a row at a time from the top. GL
        handed these back from the bottom up, which everything reading them had to undo.
        """
        width, height = self.pixel_shape
        return bytes(self.renderer.queue.read_texture(
            {"texture": self.color_texture, "mip_level": 0, "origin": (0, 0, 0)},
            {"offset": 0, "bytes_per_row": 4 * width, "rows_per_image": height},
            (width, height, 1),
        ))

    def get_image(self) -> Image.Image:
        return Image.frombytes("RGBA", self.pixel_shape, self.get_frame_bytes())

    # Getting camera attributes
    def get_pixel_size(self) -> float:
        return self.frame.get_width() / self.get_pixel_shape()[0]

    def get_pixel_shape(self) -> tuple[int, int]:
        return self.pixel_shape

    def get_pixel_width(self) -> int:
        return self.get_pixel_shape()[0]

    def get_pixel_height(self) -> int:
        return self.get_pixel_shape()[1]

    def get_aspect_ratio(self):
        pw, ph = self.get_pixel_shape()
        return pw / ph

    def get_frame_height(self) -> float:
        return self.frame.get_height()

    def get_frame_width(self) -> float:
        return self.frame.get_width()

    def get_frame_shape(self) -> tuple[float, float]:
        return (self.get_frame_width(), self.get_frame_height())

    def get_frame_center(self) -> np.ndarray:
        return self.frame.get_center()

    def get_location(self) -> tuple[float, float, float]:
        return self.frame.get_implied_camera_location()

    def resize_frame_shape(self, fixed_dimension: bool = False) -> None:
        """
        Changes frame_shape to match the aspect ratio
        of the pixels, where fixed_dimension determines
        whether frame_height or frame_width
        remains fixed while the other changes accordingly.
        """
        frame_height = self.get_frame_height()
        frame_width = self.get_frame_width()
        aspect_ratio = self.get_aspect_ratio()
        if not fixed_dimension:
            frame_height = frame_width / aspect_ratio
        else:
            frame_width = aspect_ratio * frame_height
        self.frame.set_height(frame_height, stretch=True)
        self.frame.set_width(frame_width, stretch=True)

    # Rendering
    def capture(self, *mobjects: Mobject) -> None:
        wrappers = [
            wrapper
            for mobject in mobjects
            for wrapper in mobject.get_shader_wrappers(self.renderer)
        ]
        # Everything the frame sends to the gpu, before the pass it draws in opens, since a
        # write reaching the gpu partway through a pass has no say over which draws see it
        self.refresh_uniforms()
        self.renderer.send_frame_uniforms()
        for wrapper in wrappers:
            wrapper.write_buffers()

        self.renderer.begin_frame(self.get_attachments())
        for wrapper in wrappers:
            wrapper.render()
        self.renderer.end_frame()

    def refresh_uniforms(self) -> None:
        """
        What every program reads about where the frame, the camera and the light are,
        written into the block they all share, see Renderer.
        """
        frame = self.frame
        self.renderer.frame_uniforms.update(
            view=frame.get_view_matrix().T.flatten(),
            frame_scale=frame.get_scale(),
            frame_rescale_factors=(
                2.0 / FRAME_WIDTH,
                2.0 / FRAME_HEIGHT,
                frame.get_scale() / frame.get_focal_distance(),
            ),
            pixel_size=self.get_pixel_size(),
            camera_position=frame.get_implied_camera_location(),
            light_position=self.light_source.get_location(),
        )


# Mostly just defined so old scenes don't break
class ThreeDCamera(Camera):
    def __init__(self, samples: int = 4, **kwargs):
        super().__init__(samples=samples, **kwargs)
