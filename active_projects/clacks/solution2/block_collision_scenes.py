from big_ol_pile_of_manim_imports import *
from active_projects.clacks.question import BlocksAndWallExample


class PreviousTwoVideos(BlocksAndWallExample):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 1e4,
                "velocity": -2,
                "width": 3,
            },
            "block2_config": {
                "width": 3,
            },
        },
        "wait_time": 15,
    }

    def setup(self):
        videos = Group(
            ImageMobject
        )

        name_mobs = VGroup(*map(TextMobject, names))
        name_mobs.set_stroke(BLACK, 3, background=True)
        name_mobs.set_fill(LIGHT_GREY, 1)
        name_mobs.set_sheen(3, UL)
        name_mobs.scale(2)
        configs = [
            self.sliding_blocks_config["block1_config"],
            self.sliding_blocks_config["block2_config"],
        ]
        for name_mob, config in zip(name_mobs, configs):
            config["width"] = name_mob.get_width()
        self.name_mobs = name_mobs

        super().setup()

    def add_blocks(self):
        super().add_blocks()
        blocks = self.blocks
        name_mobs = self.name_mobs

        blocks.fade(1)

        def update_name_mobs(name_mobs):
            for name_mob, block in zip(name_mobs, self.blocks):
                name_mob.move_to(block)
                target_y = block.get_bottom()[1] + SMALL_BUFF
                curr_y = name_mob[0].get_bottom()[1]
                name_mob.shift((target_y - curr_y) * UP)

        name_mobs.add_updater(update_name_mobs)
        self.add(name_mobs)

        clack_y = self.name_mobs[1].get_center()[1]
        for location, time in self.clack_data:
            location[1] = clack_y

        for block, name_mob in zip(blocks, name_mobs):
            block.label.next_to(name_mob, UP)
            block.label.set_fill(YELLOW, opacity=1)
