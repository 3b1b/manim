"""RealtimeScene - ManimGL Scene wrapper for PyQt5/6 integration.

This module provides a custom Scene class that extends ManimGL's Scene
to work within a PyQt6 QOpenGLWidget instead of creating its own window.
"""

from manimlib import Scene
from typing import Optional, Any
import numpy as np
from loguru import logger
from .render_adapter import RenderAdapter
from .qt_window import QtWindow
from .animation_timeline import AnimationTimeline
from .snapshot import SnapshotManager


class RealtimeScene(Scene):
    """
    Extended ManimGL Scene that can be embedded in PyQt6.

    This class hijacks ManimGL's window management and redirects
    rendering to a QOpenGLWidget context.
    """

    def __init__(self, qt_widget=None, skip_animations=False, **kwargs):
        """
        Initialize RealtimeScene.

        Args:
            qt_widget: QWidget instance to display rendered image
            skip_animations: If True, skip animation playback (for static scenes)
            **kwargs: Additional arguments passed to Scene
        """
        self.qt_widget = qt_widget
        self.qt_window = None

        # Create animation timeline for real-time playback with seek support
        self.timeline = AnimationTimeline()

        # Scene variables (for AI to store/retrieve data)
        self.variables = {}

        # Control panel reference (set by MainWindow)
        self.control_panel = None

        # CRITICAL: Pass window=None to use ManimGL's standalone mode
        # This creates an independent OpenGL context for offscreen rendering
        kwargs['window'] = None

        # Initialize parent Scene with standalone mode
        super().__init__(skip_animations=skip_animations, **kwargs)

        # Create snapshot manager after scene is initialized
        self.snapshot_manager = SnapshotManager(self)

        # Manually call setup() to initialize scene with test objects
        self.setup()

        # Scene is now ready for AI-generated content
        # Objects will be added dynamically through AI code execution

        # Create QtWindow wrapper after Scene initialization
        if qt_widget is not None:
            self.qt_window = QtWindow(qt_widget, scene=self)

    def setup(self):
        """
        Override setup to initialize scene with simple axes.
        """
        from loguru import logger
        from manimlib import Axes

        logger.info("[RealtimeScene.setup] Initializing axes...")

        # Extended axes with optimized range for performance
        self.axes = Axes(
            x_range=[-20, 20, 1],
            y_range=[-20, 20, 1],
            axis_config={
                "stroke_color": "#666666",
                "stroke_width": 2,
                "include_ticks": True,
                "tick_size": 0.05,
            },
        )
        self.add(self.axes)

        logger.info(f"[RealtimeScene.setup] Added axes, mobjects: {len(self.mobjects)}")

    def play(self, *animations, **kwargs):
        """
        Override play() to capture animations for timeline instead of playing immediately.

        Args:
            *animations: ManimGL Animation objects
            **kwargs: Animation parameters (run_time, etc.)
        """
        run_time = kwargs.get('run_time', 1.0)

        logger.info(f"[RealtimeScene.play] Capturing {len(animations)} animations, run_time={run_time}")

        # Add each animation to timeline
        for animation in animations:
            # Get mobject from animation - try different attribute names
            # Note: Use 'is None' because ManimGL mobjects return False in bool context
            mobject = getattr(animation, 'mobject', None)
            if mobject is None:
                mobject = getattr(animation, 'starting_mobject', None)
            if mobject is None:
                mobjects_list = getattr(animation, 'mobjects', None)
                if mobjects_list and len(mobjects_list) > 0:
                    mobject = mobjects_list[0]

            # Add mobject to scene before initializing animation
            if mobject is not None and mobject not in self.mobjects:
                self.add(mobject)
                logger.info(f"[RealtimeScene.play] Added {type(mobject).__name__} to scene")
            elif mobject is not None:
                logger.debug(f"[RealtimeScene.play] {type(mobject).__name__} already in scene")

            # IMPORTANT: Store starting state BEFORE begin() modifies the mobject
            # This is needed for proper timeline rewinding
            starting_points = {}
            if mobject is not None and hasattr(mobject, 'get_points'):
                try:
                    points = mobject.get_points()
                    if points is not None and len(points) > 0:
                        starting_points[id(mobject)] = points.copy()
                except Exception as e:
                    logger.warning(f"[RealtimeScene.play] Failed to store starting points: {e}")

            # Initialize animation
            try:
                if hasattr(animation, 'begin'):
                    animation.begin()
                    logger.debug(f"[RealtimeScene.play] Called begin() on {type(animation).__name__}")

                    # CRITICAL: Restore mobject to final state after begin()
                    # This ensures subsequent animations see the correct state
                    # Without this, ApplyMethod would store a collapsed circle as its starting state
                    if hasattr(animation, 'interpolate'):
                        animation.interpolate(1.0)
                        logger.debug(f"[RealtimeScene.play] Called interpolate(1.0) to restore mobject state")

            except Exception as e:
                logger.error(f"[RealtimeScene.play] Failed to initialize animation: {e}")

            # Check again after begin() - some animations might add mobjects differently
            if mobject is not None and mobject not in self.mobjects:
                self.add(mobject)
                logger.info(f"[RealtimeScene.play] Added {type(mobject).__name__} to scene after begin()")

            # Add to timeline for playback (pass pre-stored starting points)
            self.timeline.add_animation(animation, run_time=run_time, starting_points=starting_points)

        # Auto-play: start playing if not already playing
        if not self.timeline.is_playing and len(self.timeline.segments) > 0:
            logger.info("[RealtimeScene.play] Auto-starting playback")
            self.timeline.play()

        logger.info(f"[RealtimeScene.play] Timeline now has {len(self.timeline.segments)} segments, "
                   f"total duration: {self.timeline.total_duration:.2f}s")

    def wait(self, duration: float = 1.0):
        """
        Wait for a duration, allowing updaters to run.

        This captures mobject updaters and creates physics segments
        for proper timeline-based simulation.

        Args:
            duration: Time to wait in seconds
        """
        logger.info(f"[RealtimeScene.wait] Adding wait/physics segment: {duration}s")

        # Find all mobjects with updaters and create physics segments
        physics_count = 0
        for mob in self.mobjects:
            updaters = getattr(mob, 'updaters', [])
            if updaters:
                logger.info(f"[RealtimeScene.wait] Found {len(updaters)} updaters on {type(mob).__name__}")
                # Create a physics segment for each updater
                for updater in updaters:
                    self.timeline.add_physics_segment(mob, updater, duration)
                    physics_count += 1

        # If no physics, just add wait time
        if physics_count == 0:
            self.timeline.add_wait(duration)
        else:
            logger.info(f"[RealtimeScene.wait] Created {physics_count} physics segments")

        # Auto-play if not already playing
        if not self.timeline.is_playing:
            logger.info("[RealtimeScene.wait] Auto-starting playback")
            self.timeline.play()

    def construct(self):
        """
        Override construct - this is where user code will be executed.
        """
        pass

    def get_snapshot(self) -> dict:
        """
        Get current scene state for AI context.

        Returns:
            Dictionary containing scene state
        """
        return {
            'mobjects': [str(mob) for mob in self.mobjects],
            'camera_position': self.camera.get_center(),
            'current_time': self.timeline.current_time,
            'total_duration': self.timeline.total_duration,
            'is_playing': self.timeline.is_playing,
            'animation_count': len(self.timeline.segments)
        }

    def seek_to_time(self, time: float, snap: bool = True):
        """
        Seek animation to specific time.

        Args:
            time: Time in seconds to seek to
            snap: If True, snap to keyframe when in creation animation
        """
        logger.info(f"[RealtimeScene.seek_to_time] Seeking to {time:.2f}s (snap={snap})")
        self.timeline.seek(time, snap=snap)
        # seek() already calls interpolate_animations(), no need to call again

    def update(self, dt: float):
        """
        Update scene for real-time playback.

        Args:
            dt: Time delta in seconds since last update
        """
        # Update timeline
        self.timeline.update(dt)

        # Always interpolate animations to ensure current state is rendered
        # This handles both playing and paused states
        self.timeline.interpolate_animations()

        # Call updaters on all mobjects (for physics simulations)
        # IMPORTANT: Always call updaters when playing, regardless of animation state
        if self.timeline.is_playing:
            self._update_mobjects(dt * self.timeline.playback_speed)

        # Debug: Log timeline state periodically (every ~2 seconds)
        if hasattr(self, '_last_state_log'):
            if self.timeline.current_time - self._last_state_log > 2.0:
                logger.debug(f"[RealtimeScene.update] t={self.timeline.current_time:.2f}s, "
                           f"playing={self.timeline.is_playing}, "
                           f"duration={self.timeline.total_duration:.2f}s, "
                           f"mobjects={len(self.mobjects)}")
                self._last_state_log = self.timeline.current_time
        else:
            self._last_state_log = 0.0

    def _update_mobjects(self, dt: float):
        """
        Call updaters on all mobjects and their submobjects.

        Args:
            dt: Time delta in seconds (can be negative for reverse)
        """
        updater_count = 0

        def update_recursive(mob, dt):
            """Recursively update mobject and all submobjects."""
            nonlocal updater_count
            # Get updaters - ManimGL stores them in 'updaters' attribute
            updaters = getattr(mob, 'updaters', [])
            for updater in updaters:
                try:
                    updater(mob, abs(dt))
                    updater_count += 1
                except Exception as e:
                    logger.warning(f"Updater error on {type(mob).__name__}: {e}")

            # Also update submobjects
            submobs = getattr(mob, 'submobjects', [])
            for submob in submobs:
                update_recursive(submob, dt)

        # Update all top-level mobjects
        for mob in self.mobjects:
            update_recursive(mob, dt)

        # Log periodically (every ~1 second)
        if updater_count > 0 and int(self.timeline.current_time * 2) != int((self.timeline.current_time - dt) * 2):
            logger.debug(f"[RealtimeScene] Called {updater_count} updaters at t={self.timeline.current_time:.2f}s")
