from big_ol_pile_of_manim_imports import *
from active_projects.clacks.question import BlocksAndWallExample


class PreviousTwoVideos(BlocksAndWallExample):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 1e0,
                "velocity": -2,
            }
        },
        "wait_time": 15,
    }

    def construct(self):
        pass
