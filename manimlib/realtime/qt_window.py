"""Qt-compatible Window class for ManimGL.

This module provides a Window replacement that uses Qt's OpenGL context
instead of creating a pyglet window.
"""

import moderngl
from typing import Optional, Tuple


class QtWindow:
    """
    Qt-compatible window that mimics ManimGL's Window interface.

    This class provides the same interface as ManimGL's Window class,
    but uses Qt's OpenGL context for rendering.
    """

    def __init__(self, qt_widget, scene=None, size: Optional[Tuple[int, int]] = None):
        """
        Initialize QtWindow.

        Args:
            qt_widget: QOpenGLWidget instance
            scene: ManimGL Scene instance
            size: Window size (width, height)
        """
        self.qt_widget = qt_widget
        self.scene = scene

        # Window properties
        self._size = size or (1280, 720)
        self.width, self.height = self._size
        self.aspect_ratio = self.width / self.height

        # OpenGL context (will be initialized later)
        self.ctx: Optional[moderngl.Context] = None
        self.fbo = None

        # State flags
        self.is_closing = False
        self.hidden = False
        self.visible = True

        # Mouse state
        self.mouse_states = {}

        # Viewport
        self.viewport = (0, 0, self.width, self.height)

    def init_mgl_context(self):
        """Initialize ModernGL context from Qt's OpenGL context."""
        from loguru import logger

        # Create ModernGL context (will automatically use current Qt context)
        self.ctx = moderngl.create_context()

        # Use ModernGL's screen framebuffer (default framebuffer)
        self.fbo = self.ctx.screen

        logger.info(f"[QtWindow] Created ModernGL context")
        logger.info(f"[QtWindow] Using screen framebuffer: {self.fbo}")

        return self.ctx

    def init_for_scene(self, scene):
        """Initialize window for a specific scene."""
        self.scene = scene

        # Initialize ModernGL context
        if self.ctx is None:
            self.init_mgl_context()

        # Force camera to use Qt's framebuffer
        if hasattr(scene, 'camera'):
            if hasattr(scene.camera, 'ctx'):
                scene.camera.ctx = self.ctx

            # CRITICAL FIX: Force camera to use Qt's framebuffer
            if hasattr(scene.camera, 'fbo'):
                scene.camera.fbo = self.fbo
                scene.camera.window_fbo = self.fbo
                print(f"[QtWindow] Forced camera to use Qt framebuffer: {self.fbo}")

            # Set camera frame size (use ManimGL's scene coordinates, not pixels!)
            # ManimGL default frame height is 8.0 units
            # Let ManimGL calculate width based on aspect ratio
            scene.camera.frame.set_height(8.0)
            print(f"[QtWindow] Set camera frame height to 8.0 (ManimGL default)")

    def render(self):
        """Render scene using ManimGL's standalone mode."""
        if self.scene and hasattr(self.scene, 'camera'):
            try:
                from loguru import logger
                from PIL import Image
                import numpy as np

                # Debug camera state
                logger.info(f"[QtWindow] Camera fbo: {self.scene.camera.fbo}")
                logger.info(f"[QtWindow] Camera ctx: {self.scene.camera.ctx}")
                logger.info(f"[QtWindow] FBO size: {self.scene.camera.fbo.size if self.scene.camera.fbo else 'None'}")

                # TEST: Manually clear framebuffer to red to verify it works
                fbo = self.scene.camera.fbo
                fbo.use()
                self.scene.camera.ctx.clear(1.0, 0.0, 0.0)  # Clear to red
                logger.info("[QtWindow] Cleared framebuffer to RED for testing")

                # Let ManimGL render to its own standalone framebuffer
                # self.scene.camera.capture(*self.scene.mobjects)

                # Read pixels from ManimGL's framebuffer
                fbo = self.scene.camera.fbo
                width, height = fbo.size
                data = fbo.read(components=3, dtype='u1')

                # Convert to numpy array
                img_array = np.frombuffer(data, dtype=np.uint8)
                img_array = img_array.reshape((height, width, 3))

                # Flip vertically (OpenGL origin is bottom-left, Qt is top-left)
                img_array = np.flipud(img_array)

                # Convert to PIL Image for Qt display
                self.rendered_image = Image.fromarray(img_array, 'RGB')

                # Debug: Check if image has any non-black pixels
                non_black_pixels = np.sum(img_array > 0)
                total_pixels = img_array.size
                logger.info(f"[QtWindow] Rendered {len(self.scene.mobjects)} mobjects")
                logger.info(f"[QtWindow] Non-black pixels: {non_black_pixels}/{total_pixels} ({100*non_black_pixels/total_pixels:.2f}%)")

            except Exception as e:
                from loguru import logger
                logger.exception(f"[QtWindow] render() failed: {e}")

    def _render_mobject(self, draw, mobject):
        """Render a single mobject using PIL."""
        from loguru import logger

        # Get mobject type
        mobject_type = mobject.__class__.__name__

        # Get color (convert from ManimGL format to RGB)
        color = (255, 255, 255)  # Default white
        if hasattr(mobject, 'color'):
            # ManimGL colors are numpy arrays [r, g, b] in range 0-1
            import numpy as np
            if isinstance(mobject.color, np.ndarray):
                color = tuple((mobject.color[:3] * 255).astype(int))

        # Render based on type
        if 'Circle' in mobject_type:
            self._render_circle(draw, mobject, color)
        elif 'Square' in mobject_type or 'Rectangle' in mobject_type:
            self._render_square(draw, mobject, color)
        else:
            logger.warning(f"[QtWindow] Unknown mobject type: {mobject_type}")

    def _render_circle(self, draw, mobject, color):
        """Render a circle."""
        # Get radius (ManimGL uses scene coordinates, need to convert to pixels)
        radius = 1.0  # Default
        if hasattr(mobject, 'radius'):
            radius = mobject.radius

        # Convert to pixel coordinates
        # ManimGL scene: width=14.22, height=8.0 (for 16:9 aspect ratio)
        # Center is at (0, 0) in scene coordinates
        pixel_radius = int(radius * self.height / 8.0)

        # Get position (default to center)
        center_x = self.width // 2
        center_y = self.height // 2

        # Draw circle
        bbox = [
            center_x - pixel_radius,
            center_y - pixel_radius,
            center_x + pixel_radius,
            center_y + pixel_radius
        ]
        draw.ellipse(bbox, outline=color, width=3)

    def _render_square(self, draw, mobject, color):
        """Render a square."""
        # Get side length
        side_length = 2.0  # Default
        if hasattr(mobject, 'side_length'):
            side_length = mobject.side_length

        # Convert to pixel coordinates
        pixel_size = int(side_length * self.height / 8.0)

        # Get position (default to center)
        center_x = self.width // 2
        center_y = self.height // 2

        # Draw square
        bbox = [
            center_x - pixel_size // 2,
            center_y - pixel_size // 2,
            center_x + pixel_size // 2,
            center_y + pixel_size // 2
        ]
        draw.rectangle(bbox, outline=color, width=3)

    def clear(self, r=0.0, g=0.0, b=0.0, a=1.0):
        """Clear the framebuffer with specified color."""
        if self.ctx:
            # Let camera clear its background normally
            self.ctx.clear(r, g, b, a)

    def swap_buffers(self):
        """Swap buffers (handled by Qt)."""
        # Qt handles buffer swapping automatically
        pass

    def on_resize(self, width: int, height: int):
        """Handle window resize."""
        self.width = width
        self.height = height
        self._size = (width, height)
        self.aspect_ratio = width / height if height > 0 else 1.0
        self.viewport = (0, 0, width, height)

    def close(self):
        """Close the window."""
        self.is_closing = True

    def destroy(self):
        """Destroy window resources."""
        if self.ctx:
            self.ctx.release()

    # Event handlers (to be connected to Qt events)
    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse press."""
        if self.scene:
            self.scene.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        """Handle mouse release."""
        if self.scene:
            self.scene.on_mouse_release(x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """Handle mouse drag."""
        if self.scene:
            self.scene.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_key_press(self, symbol, modifiers):
        """Handle key press."""
        if self.scene:
            self.scene.on_key_press(symbol, modifiers)
