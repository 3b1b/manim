"""Frame-based snapshot cache system.

Automatically caches scene state at each frame for AI queries.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import copy
import numpy as np
from loguru import logger


@dataclass
class PhysicsState:
    """Physics parameters at a specific time."""
    position: Dict[str, float] = field(default_factory=dict)
    velocity: Dict[str, float] = field(default_factory=dict)
    acceleration: Dict[str, float] = field(default_factory=dict)
    mass: float = 1.0
    kinetic_energy: float = 0.0
    potential_energy: float = 0.0
    total_energy: float = 0.0
    gravity: float = 10.0
    formulas: Dict[str, str] = field(default_factory=dict)


@dataclass
class FrameSnapshot:
    """Snapshot of scene state at a specific time."""
    time: float
    mobject_positions: Dict[str, List[float]] = field(default_factory=dict)
    physics_states: Dict[str, PhysicsState] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    control_values: Dict[str, Any] = field(default_factory=dict)


class SnapshotManager:
    """Manages frame-based snapshot cache for AI queries."""

    def __init__(self, scene, step_size: float = 0.02):
        self.scene = scene
        self.step_size = step_size

        # Frame cache: time -> FrameSnapshot
        self.frame_cache: Dict[float, FrameSnapshot] = {}

        # Persistent data (not time-dependent)
        self.variables: Dict[str, Any] = {}
        self.physics_states: Dict[str, PhysicsState] = {}
        self.labels: Dict[str, str] = {}

        logger.info("[SnapshotManager] Initialized with frame cache")

    def cache_all_frames(self, duration: float):
        """Cache snapshots for all frames in the animation."""
        logger.info(f"[SnapshotManager] Caching frames for {duration:.2f}s...")

        num_frames = int(duration / self.step_size) + 1
        for i in range(num_frames):
            t = i * self.step_size
            self._cache_frame_at(t)

        logger.info(f"[SnapshotManager] Cached {len(self.frame_cache)} frames")

    def _cache_frame_at(self, time: float):
        """Cache a single frame at the given time."""
        # Get mobject positions
        positions = {}
        for i, mob in enumerate(self.scene.mobjects):
            mob_id = f"mob_{i}_{type(mob).__name__}"
            if hasattr(mob, 'get_center'):
                try:
                    center = mob.get_center()
                    positions[mob_id] = [float(center[0]), float(center[1]), float(center[2])]
                except:
                    pass

        # Get control values
        controls = {}
        if hasattr(self.scene, 'qt_widget') and self.scene.qt_widget:
            if hasattr(self.scene.qt_widget, 'hud_overlay'):
                controls = self.scene.qt_widget.hud_overlay.get_all_values()

        snapshot = FrameSnapshot(
            time=time,
            mobject_positions=positions,
            physics_states=copy.deepcopy(self.physics_states),
            variables=copy.deepcopy(self.variables),
            control_values=controls
        )

        self.frame_cache[round(time, 3)] = snapshot

    def get_frame_at(self, time: float) -> Optional[FrameSnapshot]:
        """Get cached frame at or near the given time."""
        time_key = round(time, 3)
        if time_key in self.frame_cache:
            return self.frame_cache[time_key]

        # Find nearest frame
        if self.frame_cache:
            nearest = min(self.frame_cache.keys(), key=lambda t: abs(t - time))
            if abs(nearest - time) < self.step_size:
                return self.frame_cache[nearest]
        return None

    def query_at_time(self, time: float) -> str:
        """Query scene state at a specific time (for AI)."""
        frame = self.get_frame_at(time)
        if not frame:
            return f"No data available at t={time:.2f}s"

        lines = [f"=== Scene at t={frame.time:.2f}s ==="]

        if frame.mobject_positions:
            lines.append("\nObjects:")
            for obj_id, pos in frame.mobject_positions.items():
                lines.append(f"  {obj_id}: ({pos[0]:.2f}, {pos[1]:.2f})")

        if frame.physics_states:
            lines.append("\nPhysics:")
            for obj_id, ps in frame.physics_states.items():
                if ps.position:
                    lines.append(f"  {obj_id}: pos={ps.position}, E={ps.total_energy:.2f}")

        if frame.variables:
            lines.append("\nVariables:")
            for k, v in frame.variables.items():
                lines.append(f"  {k} = {v}")

        return "\n".join(lines)

    # Variable management
    def set_variable(self, name: str, value: Any):
        self.variables[name] = value

    def get_variable(self, name: str, default: Any = None) -> Any:
        return self.variables.get(name, default)

    def get_all_variables(self) -> Dict[str, Any]:
        return copy.deepcopy(self.variables)

    # Physics state management
    def update_physics(self, obj_id: str, **kwargs):
        if obj_id not in self.physics_states:
            self.physics_states[obj_id] = PhysicsState()
        ps = self.physics_states[obj_id]
        for key, value in kwargs.items():
            if hasattr(ps, key):
                setattr(ps, key, value)

    def set_formula(self, obj_id: str, name: str, formula: str):
        if obj_id not in self.physics_states:
            self.physics_states[obj_id] = PhysicsState()
        self.physics_states[obj_id].formulas[name] = formula

    def get_physics_state(self, obj_id: str) -> Optional[PhysicsState]:
        return self.physics_states.get(obj_id)

    def set_physics_state(self, obj_id: str, state: PhysicsState):
        self.physics_states[obj_id] = state

    # Label management
    def add_label(self, obj_id: str, label: str):
        self.labels[obj_id] = label

    def get_label(self, obj_id: str) -> Optional[str]:
        return self.labels.get(obj_id)

    def get_all_labels(self) -> Dict[str, str]:
        return copy.deepcopy(self.labels)

    # For AI context
    def get_current_context(self) -> str:
        """Get current scene context for AI."""
        current_time = self.scene.timeline.current_time
        return self.query_at_time(current_time)

    def clear_cache(self):
        """Clear frame cache."""
        self.frame_cache.clear()
        logger.info("[SnapshotManager] Cache cleared")
