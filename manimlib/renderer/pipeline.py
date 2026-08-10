from __future__ import annotations

from dataclasses import dataclass
from dataclasses import replace
from functools import lru_cache

import wgpu

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


# Stencil bits alongside the depth, which a fill counting windings needs
DEPTH_STENCIL_FORMAT = wgpu.TextureFormat.depth24plus_stencil8
COLOR_FORMAT = wgpu.TextureFormat.rgba8unorm

KEEP = ("keep", "keep", "keep")

# Color channels blend in the usual way, but the alpha channel takes the source's alpha
# whole, so that drawing something half transparent onto an opaque background leaves it
# opaque rather than eating into its alpha.
BLEND = {
    "color": {
        "src_factor": wgpu.BlendFactor.src_alpha,
        "dst_factor": wgpu.BlendFactor.one_minus_src_alpha,
        "operation": wgpu.BlendOperation.add,
    },
    "alpha": {
        "src_factor": wgpu.BlendFactor.one,
        "dst_factor": wgpu.BlendFactor.one_minus_src_alpha,
        "operation": wgpu.BlendOperation.add,
    },
}


@dataclass(frozen=True)
class PipelineState:
    """
    The fixed function half of a pipeline: everything about how a draw behaves beyond which
    module runs and what it reads. There are only the few combinations named here and beside
    VDrawing, and a pipeline is built for each.

    depth_test is None where the mobject decides, which is most of them, and is settled into a
    state of its own before any pipeline is asked for, see resolved. So a pipeline is keyed on
    a module, one of these, and the sample count, with nothing left over.
    """
    depth_test: bool | None = None
    depth_write: bool = True
    color_write: bool = True
    # What the stencil buffer is compared against, "always" leaving it out of the decision
    stencil_compare: str = "always"
    # What to leave in the stencil buffer when the test fails, when depth fails, and when
    # the fragment is drawn: once for front facing triangles, once for back facing ones
    stencil_ops: tuple[tuple[str, str, str], tuple[str, str, str]] = (KEEP, KEEP)

    @lru_cache(maxsize=None)
    def resolved(self, depth_test: bool) -> PipelineState:
        """
        This state with the mobject's own choice of depth test settled into it, or as it
        stands where the state has already made that choice for itself. Two answers per
        state, so they are worked out once and looked up thereafter.
        """
        if self.depth_test is not None:
            return self
        return replace(self, depth_test=depth_test)

    def depth_stencil_descriptor(self) -> dict:
        """This state as a pipeline descriptor wants it"""
        def face(ops):
            fail, depth_fail, passed = ops
            return {
                "compare": self.stencil_compare,
                "fail_op": fail,
                "depth_fail_op": depth_fail,
                "pass_op": passed,
            }

        front, back = self.stencil_ops
        return {
            "format": DEPTH_STENCIL_FORMAT,
            "depth_write_enabled": self.depth_write,
            "depth_compare": "less" if self.depth_test else "always",
            "stencil_front": face(front),
            "stencil_back": face(back),
            "stencil_read_mask": 0xFF,
            "stencil_write_mask": 0xFF,
        }

    @property
    def color_write_mask(self) -> int:
        return 0xF if self.color_write else 0


DEFAULT = PipelineState()


def build_pipeline(
    device: Any, layout: Any, module: Any, state: PipelineState, samples: int,
) -> Any:
    """
    One pipeline. No shader is handed vertex attributes, hence the empty list of vertex
    buffers: each reads the records of its buffer itself, as a flat array of floats indexed by
    the vertex being drawn, and expands every record into a fixed number of vertices, always
    triangles, see inserts/read_data.wgsl.
    """
    return device.create_render_pipeline(
        layout=layout,
        vertex={"module": module, "entry_point": "vs_main", "buffers": []},
        fragment={
            "module": module,
            "entry_point": "fs_main",
            "targets": [{
                "format": COLOR_FORMAT,
                "blend": BLEND,
                "write_mask": state.color_write_mask,
            }],
        },
        primitive={"topology": wgpu.PrimitiveTopology.triangle_list},
        depth_stencil=state.depth_stencil_descriptor(),
        multisample={"count": samples},
    )
