from __future__ import annotations

import moderngl
import numpy as np
import OpenGL.GL as gl
from PIL import Image

from manimlib.camera.camera_frame import CameraFrame
from manimlib.constants import BLACK
from manimlib.constants import DEFAULT_FPS
from manimlib.constants import DEFAULT_PIXEL_HEIGHT, DEFAULT_PIXEL_WIDTH
from manimlib.constants import FRAME_WIDTH
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.mobject import Point
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
        background_image: Optional[str] = None,
        frame_config: dict = dict(),
        pixel_width: int = DEFAULT_PIXEL_WIDTH,
        pixel_height: int = DEFAULT_PIXEL_HEIGHT,
        fps: int = DEFAULT_FPS,
        # Note: frame height and width will be resized to match the pixel aspect ratio
        background_color: ManimColor = BLACK,
        background_opacity: float = 1.0,
        # Points in vectorized mobjects with norm greater
        # than this value will be rescaled.
        max_allowable_norm: float = FRAME_WIDTH,
        image_mode: str = "RGBA",
        n_channels: int = 4,
        pixel_array_dtype: type = np.uint8,
        light_source_position: Vect3 = np.array([-10, 10, 10]),
        # Although vector graphics handle antialiasing fine
        # without multisampling, for 3d scenes one might want
        # to set samples to be greater than 0.
        samples: int = 0,
    ):
        self.background_image = background_image
        self.window = window
        self.default_pixel_shape = (pixel_width, pixel_height)
        self.fps = fps
        self.max_allowable_norm = max_allowable_norm
        self.image_mode = image_mode
        self.n_channels = n_channels
        self.pixel_array_dtype = pixel_array_dtype
        self.light_source_position = light_source_position
        self.samples = samples

        self.rgb_max_val: float = np.iinfo(self.pixel_array_dtype).max
        self.background_rgba: list[float] = list(color_to_rgba(
            background_color, background_opacity
        ))
        self.uniforms = dict()
        self.init_frame(**frame_config)
        self.init_context()
        self.init_fbo()
        self.init_light_source()

    def init_frame(self, **config) -> None:
        self.frame = CameraFrame(**config)

    def init_context(self) -> None:
        if self.window is None:
            self.ctx: moderngl.Context = moderngl.create_standalone_context()
        else:
            self.ctx: moderngl.Context = self.window.ctx

        self.ctx.enable(moderngl.PROGRAM_POINT_SIZE)
        self.ctx.enable(moderngl.BLEND)

    def init_fbo(self) -> None:
        # This is the buffer used when writing to a video/image file
        self.fbo_for_files = self.get_fbo(self.samples)

        # This is the frame buffer we'll draw into when emitting frames
        self.draw_fbo = self.get_fbo(samples=0)

        if self.window is None:
            self.window_fbo = None
            self.fbo = self.fbo_for_files
        else:
            self.window_fbo = self.ctx.detect_framebuffer()
            self.fbo = self.window_fbo

        self.fbo.use()

    def init_light_source(self) -> None:
        self.light_source = Point(self.light_source_position)

    def use_window_fbo(self, use: bool = True):
        assert(self.window is not None)
        if use:
            self.fbo = self.window_fbo
        else:
            self.fbo = self.fbo_for_files

    # Methods associated with the frame buffer
    def get_fbo(
        self,
        samples: int = 0
    ) -> moderngl.Framebuffer:
        return self.ctx.framebuffer(
            color_attachments=self.ctx.texture(
                self.default_pixel_shape,
                components=self.n_channels,
                samples=samples,
            ),
            depth_attachment=self.ctx.depth_renderbuffer(
                self.default_pixel_shape,
                samples=samples
            )
        )

    def clear(self) -> None:
        self.fbo.clear(*self.background_rgba)

    def blit(self, src_fbo, dst_fbo):
        """
        Copy blocks between fbo's using Blit
        """
        gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, src_fbo.glo)
        gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, dst_fbo.glo)
        gl.glBlitFramebuffer(
            *src_fbo.viewport,
            *src_fbo.viewport,
            gl.GL_COLOR_BUFFER_BIT, gl.GL_LINEAR
        )

    def get_raw_fbo_data(self, dtype: str = 'f1') -> bytes:
        # # Copy blocks from fbo into draw_fbo using Blit
        # gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, self.fbo.glo)
        # gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, self.draw_fbo.glo)
        # src_viewport = self.fbo.viewport
        # gl.glBlitFramebuffer(
        #     *src_viewport,
        #     *self.draw_fbo.viewport,
        #     gl.GL_COLOR_BUFFER_BIT, gl.GL_LINEAR
        # )
        self.blit(self.fbo, self.draw_fbo)
        return self.draw_fbo.read(
            viewport=self.draw_fbo.viewport,
            components=self.n_channels,
            dtype=dtype,
        )

    def get_image(self) -> Image.Image:
        return Image.frombytes(
            'RGBA',
            self.get_pixel_shape(),
            self.get_raw_fbo_data(),
            'raw', 'RGBA', 0, -1
        )

    def get_pixel_array(self) -> np.ndarray:
        raw = self.get_raw_fbo_data(dtype='f4')
        flat_arr = np.frombuffer(raw, dtype='f4')
        arr = flat_arr.reshape([*reversed(self.draw_fbo.size), self.n_channels])
        arr = arr[::-1]
        # Convert from float
        return (self.rgb_max_val * arr).astype(self.pixel_array_dtype)

    # Needed?
    def get_texture(self) -> moderngl.Texture:
        texture = self.ctx.texture(
            size=self.fbo.size,
            components=4,
            data=self.get_raw_fbo_data(),
            dtype='f4'
        )
        return texture

    # Getting camera attributes
    def get_pixel_size(self) -> float:
        return self.frame.get_width() / self.get_pixel_shape()[0]

    def get_pixel_shape(self) -> tuple[int, int]:
        return self.fbo.size

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
        self.frame.set_height(frame_height, stretch=true)
        self.frame.set_width(frame_width, stretch=true)

    # Rendering
    def capture(self, *mobjects: Mobject) -> None:
        self.clear()
        self.refresh_uniforms()
        self.fbo.use()
        for mobject in mobjects:
            mobject.render(self.ctx, self.uniforms)
        if self.window is not None and self.fbo is not self.window_fbo:
            self.blit(self.fbo, self.window_fbo)

    def refresh_uniforms(self) -> None:
        frame = self.frame
        view_matrix = frame.get_view_matrix()
        light_pos = self.light_source.get_location()
        cam_pos = self.frame.get_implied_camera_location()

        self.uniforms.update(
            view=tuple(view_matrix.T.flatten()),
            focal_distance=frame.get_focal_distance() / frame.get_scale(),
            frame_scale=frame.get_scale(),
            pixel_size=self.get_pixel_size(),
            camera_position=tuple(cam_pos),
            light_position=tuple(light_pos),
        )


# Mostly just defined so old scenes don't break
class ThreeDCamera(Camera):
    def __init__(self, samples: int = 4, **kwargs):
        super().__init__(samples=samples, **kwargs)
