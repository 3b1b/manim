"""Render adapter to redirect ManimGL rendering to QOpenGLWidget.

This module provides the bridge between ManimGL's rendering system
and PyQt6's QOpenGLWidget, allowing ManimGL to render into a Qt context
instead of creating its own window.
"""

from typing import Optional
import moderngl


class RenderAdapter:
    """
    Adapter to redirect ManimGL's OpenGL rendering to QOpenGLWidget.

    This class intercepts ManimGL's window and context creation,
    providing a Qt-compatible OpenGL context instead.
    """

    def __init__(self, qt_widget=None):
        """
        Initialize the render adapter.

        Args:
            qt_widget: QOpenGLWidget instance to render into
        """
        self.qt_widget = qt_widget
        self.ctx: Optional[moderngl.Context] = None
        self.fbo = None  # Framebuffer object

    def initialize_context(self):
        """
        Initialize ModernGL context from Qt's OpenGL context.

        This creates a ModernGL context that uses Qt's OpenGL context,
        allowing ManimGL to render into the Qt widget.
        """
        if self.qt_widget is None:
            raise ValueError("Qt widget not set")

        # Create ModernGL context from current OpenGL context
        # Note: This assumes Qt's OpenGL context is current
        self.ctx = moderngl.create_context()

        # Get widget size
        width = self.qt_widget.width()
        height = self.qt_widget.height()

        # Create framebuffer if needed
        # ManimGL might need a specific framebuffer setup

        return self.ctx

    def get_context(self):
        """Get the ModernGL context."""
        return self.ctx

    def resize(self, width: int, height: int):
        """
        Handle resize events.

        Args:
            width: New width
            height: New height
        """
        # Update framebuffer size if needed
        pass

    def cleanup(self):
        """Clean up resources."""
        if self.fbo:
            self.fbo.release()
        if self.ctx:
            self.ctx.release()
