from manimlib.imports import *
from old_projects.clacks.question import BlocksAndWallExample


class PreviousTwoVideos(BlocksAndWallExample):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 1e2,
                "velocity": -2,
                "width": 4,
                "distance": 8,
            },
            "block2_config": {
                "width": 4,
                "distance": 3,
            },
        },
        "floor_y": -3,
        "wait_time": 15,
    }

    def setup(self):
        super().setup()
        blocks = self.blocks
        videos = Group(
            ImageMobject("ClacksSolution1Thumbnail"),
            ImageMobject("ClacksQuestionThumbnail"),
        )
        for n, video, block in zip([2, 1], videos, blocks):
            block.fade(1)
            video.add(SurroundingRectangle(
                video, buff=0,
                color=BLUE,
                stroke_width=3,
            ))
            video.replace(block)

            title = TextMobject("Part {}".format(n))
            title.scale(1.5)
            title.next_to(video, UP, MED_SMALL_BUFF)
            video.add(title)

        def update_videos(videos):
            for video, block in zip(videos, blocks):
                video.move_to(block, DOWN)
                video.shift(0.04 * UP)

        videos.add_updater(update_videos)
        self.add(videos)
        if self.show_flash_animations:
            self.add(self.clack_flashes.mobject)
        self.videos = videos


class IntroducePreviousTwoVideos(PreviousTwoVideos):
    CONFIG = {
        "show_flash_animations": False,
        "include_sound": False,
    }

    def construct(self):
        blocks = self.blocks
        videos = self.videos

        self.remove(blocks)
        videos.clear_updaters()
        self.remove(videos)

        self.play(FadeInFromLarge(videos[1]))
        self.play(TransformFromCopy(
            videos[0].copy().fade(1).shift(2 * RIGHT),
            videos[0],
            rate_func=lambda t: rush_into(t, 3),
        ))
        # self.wait()
