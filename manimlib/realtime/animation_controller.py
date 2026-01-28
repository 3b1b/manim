"""Animation controller for timeline management and seek support."""

from typing import List, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum


class AnimationState(Enum):
    """Animation playback state."""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"


@dataclass
class AnimationRecord:
    """Record of a single animation in the timeline."""
    start_time: float
    duration: float
    animation_func: Callable
    mobject: Any
    target_state: Dict[str, Any]


class AnimationController:
    """
    Manages animation timeline with seek/pause/play controls.

    This controller intercepts ManimGL's play() calls to build a timeline,
    allowing random access to any point in the animation.
    """

    def __init__(self):
        self.timeline: List[AnimationRecord] = []
        self.current_time: float = 0.0
        self.total_duration: float = 0.0
        self.state: AnimationState = AnimationState.STOPPED
        self.playback_speed: float = 1.0

    def record_animation(self, animation, duration: float):
        """
        Record an animation to the timeline.

        Args:
            animation: ManimGL Animation object
            duration: Duration in seconds
        """
        record = AnimationRecord(
            start_time=self.total_duration,
            duration=duration,
            animation_func=animation,
            mobject=getattr(animation, 'mobject', None),
            target_state={}
        )
        self.timeline.append(record)
        self.total_duration += duration

    def seek(self, time: float):
        """
        Seek to a specific time in the animation.

        Args:
            time: Time in seconds (0 to total_duration)
        """
        self.current_time = max(0.0, min(time, self.total_duration))
        # TODO: Calculate and apply object states at this time

    def play(self):
        """Start or resume animation playback."""
        self.state = AnimationState.PLAYING

    def pause(self):
        """Pause animation playback."""
        self.state = AnimationState.PAUSED

    def stop(self):
        """Stop animation and reset to beginning."""
        self.state = AnimationState.STOPPED
        self.current_time = 0.0

    def get_progress(self) -> float:
        """
        Get current playback progress.

        Returns:
            Progress from 0.0 to 1.0
        """
        if self.total_duration == 0:
            return 0.0
        return self.current_time / self.total_duration

    def set_progress(self, progress: float):
        """
        Set playback progress.

        Args:
            progress: Progress from 0.0 to 1.0
        """
        progress = max(0.0, min(1.0, progress))
        self.seek(progress * self.total_duration)

    def clear(self):
        """Clear all animations from timeline."""
        self.timeline.clear()
        self.current_time = 0.0
        self.total_duration = 0.0
        self.state = AnimationState.STOPPED
