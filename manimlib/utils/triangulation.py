# manimlib/utils/triangulation.py
from typing import List, Tuple
import numpy as np

try:
    import mapbox_earcut as earcut
    _HAS_EARCUT = True
except Exception:
    _HAS_EARCUT = False

def triangulate_polygon_with_holes(
    outer: np.ndarray,
    holes: List[np.ndarray]
) -> np.ndarray:
    """
    Returns an (N, 3) int array of triangle indices covering the polygon exactly once.
    `outer` and each hole is an array of shape (M, 2) or (M, 3).
    """
    if not _HAS_EARCUT:
        raise ImportError(
            "mapbox_earcut not available. Install via `pip install mapbox_earcut`."
        )

    def _flatten_xy(a):
        a2 = a[:, :2] if a.shape[1] >= 2 else np.pad(a, ((0,0),(0,2-a.shape[1])))
        return a2.reshape(-1).astype(float)

    vertices = []
    hole_indices = []
    cursor = 0

    outer_flat = _flatten_xy(outer)
    vertices.extend(outer_flat.tolist())
    cursor += outer.shape[0] 

    for h in holes:
        hole_indices.append(cursor)
        h_flat = _flatten_xy(h)
        vertices.extend(h_flat.tolist())
        cursor += h.shape[0]

  
    tri = earcut.triangulate_float64(vertices, hole_indices, 2)
    tri = np.array(tri, dtype=np.int32).reshape(-1, 3)
    return tri
