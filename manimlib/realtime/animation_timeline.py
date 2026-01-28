"""Animation timeline system for real-time playback with reverse support.

This module provides a timeline manager that captures ManimGL animations
and allows real-time playback with seek and reverse support.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import time
import copy
import numpy as np
from loguru import logger


@dataclass
class AnimationSegment:
    """Represents a single animation segment in the timeline."""
    animation: Any  # ManimGL Animation object
    start_time: float  # Start time in seconds
    duration: float  # Duration in seconds
    mobjects: List[Any]  # Affected mobjects
    is_initialized: bool = False
    is_finished: bool = False
    last_alpha: float = -1.0  # -1 means never interpolated
    # Store starting points for each mobject to enable proper rewinding
    starting_points: Dict[int, Any] = field(default_factory=dict)

    @property
    def end_time(self) -> float:
        """Get end time of this animation."""
        return self.start_time + self.duration

    def store_starting_state(self):
        """Store the starting points of all mobjects and submobjects before animation."""
        for mob in self.mobjects:
            self._store_mob_state(mob)

    def _store_mob_state(self, mob):
        """Recursively store points for a mobject and its submobjects."""
        if hasattr(mob, 'get_points'):
            try:
                points = mob.get_points()
                if points is not None and len(points) > 0:
                    self.starting_points[id(mob)] = points.copy()
            except Exception as e:
                logger.warning(f"Failed to store starting points: {e}")
        # Recursively store submobjects
        if hasattr(mob, 'submobjects'):
            for submob in mob.submobjects:
                self._store_mob_state(submob)

    def restore_starting_state(self):
        """Restore mobjects and submobjects to their starting state."""
        for mob in self.mobjects:
            self._restore_mob_state(mob)

    def _restore_mob_state(self, mob):
        """Recursively restore points for a mobject and its submobjects."""
        mob_id = id(mob)
        if mob_id in self.starting_points:
            try:
                if hasattr(mob, 'set_points'):
                    mob.set_points(self.starting_points[mob_id].copy())
            except Exception as e:
                logger.warning(f"Failed to restore starting points: {e}")
        # Recursively restore submobjects
        if hasattr(mob, 'submobjects'):
            for submob in mob.submobjects:
                self._restore_mob_state(submob)


@dataclass
class PhysicsSegment:
    """Physics segment with pre-computed states for seek/replay support."""
    start_time: float
    duration: float
    mobject: Any
    updater: Any
    step_size: float = 0.02
    initial_points: Any = None
    # Pre-computed states at each step (computed once at creation)
    precomputed_states: List[Any] = field(default_factory=list)
    is_precomputed: bool = False

    @property
    def end_time(self) -> float:
        return self.start_time + self.duration

    def precompute(self):
        """Pre-compute all physics states at creation time."""
        if self.is_precomputed or self.initial_points is None:
            return

        logger.info(f"[PhysicsSegment] Pre-computing {int(self.duration / self.step_size)} steps...")

        # Restore initial state
        self.mobject.set_points(self.initial_points.copy())
        self.precomputed_states = [self.initial_points.copy()]

        # Simulate and cache each step
        num_steps = int(self.duration / self.step_size)
        for _ in range(num_steps):
            try:
                self.updater(self.mobject, self.step_size)
                points = self.mobject.get_points()
                if points is not None:
                    self.precomputed_states.append(points.copy())
            except Exception as e:
                logger.error(f"[PhysicsSegment] Precompute error: {e}")
                break

        # Restore to initial state after precomputation
        self.mobject.set_points(self.initial_points.copy())
        self.is_precomputed = True
        logger.info(f"[PhysicsSegment] Pre-computed {len(self.precomputed_states)} states")

    def compute_state_at(self, target_time: float):
        """Get pre-computed state at target time."""
        if not self.is_precomputed or not self.precomputed_states:
            return

        if target_time < self.start_time:
            return

        # Calculate step index
        elapsed = min(target_time - self.start_time, self.duration)
        step_idx = int(elapsed / self.step_size)
        step_idx = min(step_idx, len(self.precomputed_states) - 1)

        # Apply pre-computed state
        if step_idx >= 0 and step_idx < len(self.precomputed_states):
            self.mobject.set_points(self.precomputed_states[step_idx].copy())

    def reset(self):
        """Reset to initial state."""
        if self.initial_points is not None:
            self.mobject.set_points(self.initial_points.copy())


class AnimationTimeline:
    """Manages animation timeline for real-time playback with reverse support."""

    def __init__(self):
        """Initialize animation timeline."""
        self.segments: List[AnimationSegment] = []
        self.physics_segments: List[PhysicsSegment] = []  # Physics simulations
        self.current_time: float = 0.0
        self.total_duration: float = 0.0
        self.is_playing: bool = False
        self.playback_speed: float = 1.0  # Negative for reverse
        self.last_update_time: Optional[float] = None
        self._last_logged_time: float = -1.0

        logger.info("[AnimationTimeline] Initialized")

    def add_animation(self, animation, run_time: float = 1.0, starting_points: dict = None):
        """
        Add an animation to the timeline.

        Args:
            animation: ManimGL Animation object
            run_time: Duration of the animation in seconds
            starting_points: Pre-stored starting points (before begin() was called)
        """
        # Get affected mobjects
        mobjects = []
        if hasattr(animation, 'mobject'):
            mobjects = [animation.mobject]
        elif hasattr(animation, 'mobjects'):
            mobjects = list(animation.mobjects) if animation.mobjects else []

        # Create segment
        segment = AnimationSegment(
            animation=animation,
            start_time=self.total_duration,
            duration=run_time,
            mobjects=mobjects,
            is_initialized=True  # begin() was called in RealtimeScene.play()
        )

        # Use pre-stored starting points if provided, otherwise store current state
        if starting_points:
            segment.starting_points = starting_points
        else:
            segment.store_starting_state()

        self.segments.append(segment)
        self.total_duration += run_time

        logger.info(f"[AnimationTimeline] Added animation: {type(animation).__name__}, "
                   f"duration: {run_time}s, total: {self.total_duration}s")

    def add_wait(self, duration: float):
        """
        Add a wait segment to the timeline.

        This extends the timeline duration without any animation,
        allowing updaters to run during playback.

        Args:
            duration: Wait duration in seconds
        """
        self.total_duration += duration
        logger.info(f"[AnimationTimeline] Added wait: {duration}s, total: {self.total_duration}s")

    def add_physics_segment(self, mobject, updater, duration: float):
        """
        Add a physics simulation segment to the timeline.

        Args:
            mobject: The mobject to simulate
            updater: The updater function (mob, dt) -> None
            duration: Duration of the simulation in seconds
        """
        # Store initial state
        initial_points = None
        if hasattr(mobject, 'get_points'):
            points = mobject.get_points()
            if points is not None and len(points) > 0:
                initial_points = points.copy()

        segment = PhysicsSegment(
            start_time=self.total_duration,
            duration=duration,
            mobject=mobject,
            updater=updater,
            initial_points=initial_points
        )

        # Pre-compute all physics states at creation time
        # This ensures replay works correctly (closure variables only used once)
        segment.precompute()

        self.physics_segments.append(segment)
        self.total_duration += duration

        logger.info(f"[AnimationTimeline] Added physics segment: {type(mobject).__name__}, "
                   f"duration: {duration}s, total: {self.total_duration}s")

    def update(self, dt: float):
        """
        Update timeline by time delta.

        Args:
            dt: Time delta in seconds
        """
        if not self.is_playing:
            return

        # Apply playback speed (can be negative for reverse)
        self.current_time += dt * self.playback_speed

        # Clamp to valid range
        if self.current_time >= self.total_duration:
            self.current_time = self.total_duration
            if self.playback_speed > 0:
                self.is_playing = False
                logger.info("[AnimationTimeline] Reached end, paused")
        elif self.current_time <= 0:
            self.current_time = 0
            if self.playback_speed < 0:
                self.is_playing = False
                logger.info("[AnimationTimeline] Reached beginning, paused")

    def seek(self, time: float, snap: bool = True):
        """
        Seek to specific time with proper animation state restoration.

        Args:
            time: Time in seconds
            snap: If True, snap to keyframe only when in creation animation
        """
        old_time = self.current_time

        # Clamp to valid range
        target_time = max(0.0, min(time, self.total_duration))

        # Only snap if we're in the middle of a creation animation
        if snap and self.is_in_creation_animation(target_time):
            target_time = self.snap_to_keyframe(target_time)

        # Skip if time hasn't changed significantly (reduces redundant calculations)
        if abs(target_time - old_time) < 0.001:
            return

        self.current_time = target_time
        is_seeking_backwards = self.current_time < old_time

        # Only restore states when seeking backwards
        if is_seeking_backwards:
            for segment in self.segments:
                # Only restore segments that we're seeking back through
                if segment.start_time <= old_time and segment.start_time > self.current_time:
                    segment.is_finished = False
                    segment.last_alpha = -1.0
                    segment.restore_starting_state()
                    if hasattr(segment.animation, 'begin'):
                        try:
                            segment.animation.begin()
                        except Exception as e:
                            pass  # Silently ignore re-init errors
                elif segment.end_time > self.current_time:
                    # Reset alpha to force update for active segments
                    segment.last_alpha = -1.0

        # Immediately interpolate to the new time
        self.interpolate_animations()

    def play(self):
        """Start forward playback."""
        self.is_playing = True
        self.playback_speed = abs(self.playback_speed) or 1.0  # Ensure positive
        self.last_update_time = time.time()
        logger.info("[AnimationTimeline] Playing forward")

    def play_reverse(self):
        """Start reverse playback."""
        self.is_playing = True
        self.playback_speed = -abs(self.playback_speed) or -1.0  # Ensure negative
        self.last_update_time = time.time()
        logger.info("[AnimationTimeline] Playing reverse")

    def pause(self):
        """Pause playback."""
        self.is_playing = False
        logger.info("[AnimationTimeline] Paused")

    def set_speed(self, speed: float):
        """Set playback speed (negative for reverse)."""
        self.playback_speed = speed
        logger.info(f"[AnimationTimeline] Speed set to {speed}x")

    def get_active_animations(self) -> List[AnimationSegment]:
        """Get animations active at current time."""
        active = []
        for segment in self.segments:
            if segment.start_time <= self.current_time < segment.end_time:
                active.append(segment)
        return active

    def get_keyframes(self) -> List[float]:
        """Get keyframes only for shape creation animations (not text)."""
        # Animation types that need keyframe snapping (invisible in middle states)
        # Note: Write/FadeIn for text are EXCLUDED - text can be partially visible
        creation_anims = ('ShowCreation', 'Create', 'DrawBorderThenFill')

        keyframes = set([0.0])  # Always include start
        for segment in self.segments:
            anim_type = type(segment.animation).__name__
            if anim_type in creation_anims:
                keyframes.add(segment.start_time)
                keyframes.add(segment.end_time)
        if self.total_duration > 0:
            keyframes.add(self.total_duration)
        return sorted(keyframes)

    def is_in_creation_animation(self, time: float) -> bool:
        """Check if time is in the middle of a shape creation animation."""
        # Only snap for shape creation, NOT for text animations
        creation_anims = ('ShowCreation', 'Create', 'DrawBorderThenFill')
        for segment in self.segments:
            anim_type = type(segment.animation).__name__
            if anim_type in creation_anims:
                # Check if time is strictly inside (not at boundaries)
                if segment.start_time < time < segment.end_time:
                    return True
        return False

    def snap_to_keyframe(self, time: float) -> float:
        """Snap a time to the nearest keyframe (always snaps)."""
        keyframes = self.get_keyframes()
        if not keyframes:
            return time
        nearest = min(keyframes, key=lambda k: abs(k - time))
        return nearest

    def interpolate_animations(self):
        """Interpolate all animations and physics at current time."""
        # Interpolate regular animations
        for segment in self.segments:
            self._interpolate_segment(segment)

        # Compute physics states from pre-computed cache
        for physics in self.physics_segments:
            in_range = physics.start_time <= self.current_time <= physics.end_time
            before_start = self.current_time < physics.start_time
            after_end = self.current_time > physics.end_time

            # Log once per second
            if int(self.current_time * 2) != int(self._last_logged_time * 2):
                if self.physics_segments:
                    logger.debug(f"[Timeline] t={self.current_time:.2f}s, physics range=[{physics.start_time:.2f}, {physics.end_time:.2f}], in_range={in_range}")

            if in_range:
                physics.compute_state_at(self.current_time)
            elif before_start:
                # Reset to initial state when seeking before physics segment
                physics.reset()
            elif after_end:
                # Keep final state when past physics segment
                physics.compute_state_at(physics.end_time)

    def _interpolate_segment(self, segment: AnimationSegment):
        """Interpolate a single animation segment."""
        animation = segment.animation

        # CRITICAL: Skip animations that haven't started yet
        # This prevents later animations from overwriting earlier animations' work
        # e.g., at time 0.5, ApplyMethod shouldn't overwrite ShowCreation's half-drawn circle
        if self.current_time < segment.start_time:
            return

        # Calculate alpha for this segment
        if self.current_time >= segment.end_time:
            # After animation ends - set to final state
            target_alpha = 1.0
        else:
            # During animation - interpolate
            target_alpha = (self.current_time - segment.start_time) / segment.duration
            target_alpha = max(0.0, min(1.0, target_alpha))

        # Apply rate function if available
        display_alpha = target_alpha
        if hasattr(animation, 'get_rate_func'):
            rate_func = animation.get_rate_func()
            if rate_func:
                display_alpha = rate_func(target_alpha)
        elif hasattr(animation, 'rate_func') and animation.rate_func:
            display_alpha = animation.rate_func(target_alpha)

        # Only update if alpha changed
        if abs(display_alpha - segment.last_alpha) < 0.001:
            return

        try:
            if hasattr(animation, 'interpolate'):
                animation.interpolate(display_alpha)
                segment.last_alpha = display_alpha

                # Mark as finished if we've completed
                if target_alpha >= 1.0:
                    segment.is_finished = True
        except ValueError as e:
            # Shape mismatch in Transform animations - skip to final state
            if "broadcast" in str(e) or "shape" in str(e):
                try:
                    animation.interpolate(1.0)
                    segment.is_finished = True
                    segment.last_alpha = 1.0
                except:
                    pass
            if int(self.current_time * 10) != int(self._last_logged_time * 10):
                logger.warning(f"[AnimationTimeline] Interpolate shape mismatch, skipped to end")
                self._last_logged_time = self.current_time
        except Exception as e:
            if int(self.current_time * 10) != int(self._last_logged_time * 10):
                anim_type = type(animation).__name__
                logger.error(f"[AnimationTimeline] Failed to interpolate {anim_type}: {type(e).__name__}: {e}")
                self._last_logged_time = self.current_time

    def reset(self):
        """Reset timeline to beginning."""
        self.current_time = 0.0
        self.is_playing = False
        self.playback_speed = 1.0

        # Reset all animation states
        for segment in self.segments:
            segment.is_finished = False
            segment.last_alpha = -1.0
            segment.restore_starting_state()
            if hasattr(segment.animation, 'begin'):
                try:
                    segment.animation.begin()
                except Exception as e:
                    logger.warning(f"[AnimationTimeline] Failed to reset: {e}")

        # Reset physics segments to initial state
        for physics in self.physics_segments:
            physics.reset()

        self.interpolate_animations()
        logger.info("[AnimationTimeline] Reset")

    def clear(self):
        """Clear all animations."""
        self.segments.clear()
        self.physics_segments.clear()
        self.current_time = 0.0
        self.total_duration = 0.0
        self.is_playing = False
        self.playback_speed = 1.0
        logger.info("[AnimationTimeline] Cleared")

    def get_progress(self) -> float:
        """Get current progress as 0-1 value."""
        if self.total_duration <= 0:
            return 0.0
        return self.current_time / self.total_duration

    def set_progress(self, progress: float):
        """Set progress from 0-1 value."""
        self.seek(progress * self.total_duration)

    def is_reversing(self) -> bool:
        """Check if currently playing in reverse."""
        return self.playback_speed < 0
