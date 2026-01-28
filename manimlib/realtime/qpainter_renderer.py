"""QPainter renderer for ManimGL mobjects.

This module provides a renderer that converts ManimGL mobjects to QPainter
drawing commands, replacing the OpenGL rendering pipeline.
"""

import numpy as np
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath
from PyQt5.QtCore import Qt, QPointF
from typing import List, Tuple, Optional
from loguru import logger


class QPainterRenderer:
    """Renders ManimGL mobjects using QPainter."""

    def __init__(self, width: int = 1920, height: int = 1080):
        """
        Initialize QPainter renderer.

        Args:
            width: Render width in pixels
            height: Render height in pixels
        """
        self.width = width
        self.height = height

        # ManimGL default frame dimensions
        self.frame_width = 14.222222222222221  # 16:9 aspect ratio
        self.frame_height = 8.0

        # Camera offset (for panning)
        self.camera_offset_x = 0.0
        self.camera_offset_y = 0.0

        # Camera rotation (for 3D)
        self.camera_theta = 0.0
        self.camera_phi = 0.0

        # Background color (can be set externally)
        self.bg_color = None

        # Calculate scale factors for coordinate conversion
        # Use uniform scale to maintain 1:1 aspect ratio
        self.scale_x = width / self.frame_width
        self.scale_y = height / self.frame_height
        self.uniform_scale = min(self.scale_x, self.scale_y)

        # Offset to center the content
        self.center_offset_x = (width - self.frame_width * self.uniform_scale) / 2
        self.center_offset_y = (height - self.frame_height * self.uniform_scale) / 2

        # Track first render for debug logging
        self._first_render = True
        self._last_mobject_count = 0

        logger.info(f"[QPainterRenderer] Initialized {width}x{height}")

    def manim_to_pixel(self, point: np.ndarray) -> Tuple[float, float]:
        """
        Convert ManimGL 3D coordinates to 2D pixel coordinates.

        Args:
            point: 3D point [x, y, z] in ManimGL coordinates

        Returns:
            Tuple of (pixel_x, pixel_y)
        """
        x, y, z = point[0], point[1], point[2] if len(point) > 2 else 0

        # Apply 3D rotation if theta or phi are non-zero
        if hasattr(self, 'camera_theta') and hasattr(self, 'camera_phi'):
            theta = np.radians(self.camera_theta)
            phi = np.radians(self.camera_phi)

            # Rotate around Y axis (theta - horizontal rotation)
            x_rot = x * np.cos(theta) + z * np.sin(theta)
            z_rot = -x * np.sin(theta) + z * np.cos(theta)

            # Rotate around X axis (phi - vertical rotation)
            y_rot = y * np.cos(phi) - z_rot * np.sin(phi)
            z_final = y * np.sin(phi) + z_rot * np.cos(phi)

            x, y = x_rot, y_rot

        # Apply camera offset
        x = x - self.camera_offset_x
        y = y - self.camera_offset_y

        # ManimGL origin is at center, Qt origin is at top-left
        pixel_x = (x + self.frame_width / 2) * self.uniform_scale + self.center_offset_x
        pixel_y = (self.frame_height / 2 - y) * self.uniform_scale + self.center_offset_y
        return pixel_x, pixel_y

    def color_to_qcolor(self, color) -> QColor:
        """
        Convert ManimGL color to QColor.

        Args:
            color: ManimGL color (numpy array [r,g,b] 0-1 OR hex string "#RRGGBB")

        Returns:
            QColor object
        """
        # Handle hex string format
        if isinstance(color, str):
            return QColor(color)

        # Handle numpy array format
        if isinstance(color, np.ndarray) and len(color) >= 3:
            r = int(color[0] * 255)
            g = int(color[1] * 255)
            b = int(color[2] * 255)
            return QColor(r, g, b)

        # Default white
        return QColor(255, 255, 255)

    def render(self, painter: QPainter, mobjects: List):
        """
        Render a list of mobjects using QPainter.

        Args:
            painter: QPainter instance
            mobjects: List of ManimGL mobjects to render
        """
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        # Fill background with custom color or default dark
        if self.bg_color:
            painter.fillRect(0, 0, self.width, self.height, self.bg_color)
        else:
            painter.fillRect(0, 0, self.width, self.height, QColor(43, 43, 43))

        # Count total mobjects rendered
        total_rendered = 0

        # Render each mobject
        for mobject in mobjects:
            total_rendered += self.render_mobject(painter, mobject)

        # Log mobject count on first render or when count changes
        if self._first_render or len(mobjects) != self._last_mobject_count:
            logger.info(f"[QPainterRenderer] Rendering {len(mobjects)} top-level mobjects, {total_rendered} total")
            for i, mob in enumerate(mobjects):
                mob_type = type(mob).__name__
                center = mob.get_center() if hasattr(mob, 'get_center') else [0, 0, 0]
                logger.debug(f"[QPainterRenderer] Mobject {i}: {mob_type} at center {center[:2]}")
            self._first_render = False
            self._last_mobject_count = len(mobjects)

    def render_mobject(self, painter: QPainter, mobject) -> int:
        """
        Render a single mobject and its submobjects recursively.

        Args:
            painter: QPainter instance
            mobject: ManimGL mobject to render

        Returns:
            Number of mobjects rendered
        """
        count = 0
        mob_type = type(mobject).__name__

        # Skip internal/debug mobjects and text-related internal components
        skip_types = (
            'CameraFrame', 'BackgroundRectangle', 'SurroundingRectangle',
            'SingleStringTex', 'TexSymbol', 'Text', 'MarkupText',
            'Paragraph', 'Code'
        )
        if mob_type in skip_types:
            return 0

        # Skip mobjects with hex-like names (internal SVG path IDs)
        if hasattr(mobject, 'name') and mobject.name:
            name = str(mobject.name)
            # Skip if name looks like hex ID (e.g., "77E996354E5B")
            if len(name) >= 8 and all(c in '0123456789abcdefABCDEF- ' for c in name):
                return 0

        # First, recursively render all submobjects
        if hasattr(mobject, 'submobjects'):
            for submob in mobject.submobjects:
                count += self.render_mobject(painter, submob)

        # Get points using get_points() method
        if not hasattr(mobject, 'get_points'):
            return count

        try:
            points = mobject.get_points()
        except Exception as e:
            logger.warning(f"[render_mobject] Failed to get points from {mob_type}: {e}")
            return count

        # Skip if no points
        if points is None or len(points) == 0:
            return count

        # Get mobject properties
        stroke_color = self._get_stroke_color(mobject)
        stroke_width = self._get_stroke_width(mobject)
        stroke_opacity = self._get_stroke_opacity(mobject)
        fill_color = self._get_fill_color(mobject)
        fill_opacity = self._get_fill_opacity(mobject)

        # Skip if completely invisible
        if stroke_opacity == 0 and fill_opacity == 0:
            return count

        # Convert colors
        qstroke_color = self.color_to_qcolor(stroke_color)
        qstroke_color.setAlphaF(stroke_opacity)

        qfill_color = self.color_to_qcolor(fill_color)
        qfill_color.setAlphaF(fill_opacity)

        # Set up pen for stroke
        if stroke_opacity > 0 and stroke_width > 0:
            pen = QPen(qstroke_color)
            pen.setWidthF(stroke_width)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)
        else:
            painter.setPen(Qt.NoPen)

        # Set up brush for fill
        if fill_opacity > 0:
            brush = QBrush(qfill_color)
            painter.setBrush(brush)
        else:
            painter.setBrush(Qt.NoBrush)

        # Create path from points and draw
        path = self.points_to_path(points)
        painter.drawPath(path)

        return count + 1

    def _get_stroke_color(self, mobject) -> np.ndarray:
        """Get stroke color from mobject."""
        if hasattr(mobject, 'get_stroke_color'):
            color = mobject.get_stroke_color()
            if color is not None:
                return color
        return getattr(mobject, 'stroke_color', np.array([1, 1, 1]))

    def _get_stroke_width(self, mobject) -> float:
        """Get stroke width from mobject."""
        if hasattr(mobject, 'get_stroke_width'):
            width = mobject.get_stroke_width()
            if width is not None:
                # Handle numpy arrays
                if hasattr(width, '__iter__') and not isinstance(width, str):
                    width = float(width[0]) if len(width) > 0 else 2.0
                return float(width)
        return float(getattr(mobject, 'stroke_width', 2))

    def _get_stroke_opacity(self, mobject) -> float:
        """Get stroke opacity from mobject."""
        if hasattr(mobject, 'get_stroke_opacity'):
            opacity = mobject.get_stroke_opacity()
            if opacity is not None:
                # Handle numpy arrays (ManimGL sometimes returns arrays)
                if hasattr(opacity, '__iter__') and not isinstance(opacity, str):
                    opacity = float(opacity[0]) if len(opacity) > 0 else 1.0
                return float(opacity)
        return float(getattr(mobject, 'stroke_opacity', 1.0))

    def _get_fill_color(self, mobject) -> np.ndarray:
        """Get fill color from mobject."""
        if hasattr(mobject, 'get_fill_color'):
            color = mobject.get_fill_color()
            if color is not None:
                return color
        return getattr(mobject, 'fill_color', np.array([0, 0, 0]))

    def _get_fill_opacity(self, mobject) -> float:
        """Get fill opacity from mobject."""
        if hasattr(mobject, 'get_fill_opacity'):
            opacity = mobject.get_fill_opacity()
            if opacity is not None:
                # Handle numpy arrays
                if hasattr(opacity, '__iter__') and not isinstance(opacity, str):
                    opacity = float(opacity[0]) if len(opacity) > 0 else 0.0
                return float(opacity)
        return float(getattr(mobject, 'fill_opacity', 0))

    def points_to_path(self, points: np.ndarray) -> QPainterPath:
        """
        Convert ManimGL points to QPainterPath.

        ManimGL VMobject uses quadratic Bezier curves:
        - Format: [anchor0, handle0, anchor1, handle1, anchor2, ...]
        - Each curve segment: anchor -> handle -> next_anchor
        - Total: n anchors + (n-1) handles = 2n-1 points for n anchors

        Args:
            points: Array of 3D points

        Returns:
            QPainterPath
        """
        path = QPainterPath()

        if len(points) == 0:
            return path

        # Move to first anchor point
        start_x, start_y = self.manim_to_pixel(points[0])
        path.moveTo(start_x, start_y)

        # ManimGL uses quadratic Bezier: anchor, control, anchor, control, ...
        # Process in pairs: (control, next_anchor)
        i = 1
        while i + 1 < len(points):
            # Control point
            ctrl_x, ctrl_y = self.manim_to_pixel(points[i])
            # Next anchor
            end_x, end_y = self.manim_to_pixel(points[i + 1])

            # Add quadratic Bezier curve
            path.quadTo(ctrl_x, ctrl_y, end_x, end_y)
            i += 2

        # Handle case where there's a trailing control point (close the path)
        if i < len(points):
            # There's one more control point - use it to close back to start
            ctrl_x, ctrl_y = self.manim_to_pixel(points[i])
            path.quadTo(ctrl_x, ctrl_y, start_x, start_y)

        # Check if path should be closed
        if len(points) >= 3:
            first_point = points[0]
            last_point = points[-1]
            # For closed shapes, last anchor should be very close to first anchor
            # But in ManimGL, they handle this differently - check distance
            distance = np.linalg.norm(first_point[:2] - last_point[:2])
            if distance < 0.01:
                path.closeSubpath()

        return path
