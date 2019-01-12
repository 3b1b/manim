from big_ol_pile_of_manim_imports import *
from active_projects.clacks import *



class LastVideo(Scene):
    def construct(self):
        pass


class BlocksAndWallExampleMass16(BlocksAndWallExample):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 16,
                "velocity": -1.5,
            },
        },
        "wait_time": 25,
    }



class Mass16WithElasticLabel(Mass1e1WithElasticLabel):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 16,
            }
        },
    }


class BlocksAndWallExampleMass64(BlocksAndWallExample):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 64,
                "velocity": -1.5,
            },
        },
        "wait_time": 25,
    }