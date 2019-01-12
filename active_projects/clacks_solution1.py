from big_ol_pile_of_manim_imports import *
from active_projects.clacks import *



# TODO, add solution image
class FromPuzzleToSolution(MovingCameraScene):
    def construct(self):
        big_rect = FullScreenFadeRectangle()
        big_rect.set_fill(DARK_GREY, 0.5)
        self.add(big_rect)

        rects = VGroup(ScreenRectangle(), ScreenRectangle())
        rects.set_height(3)
        rects.arrange_submobjects(RIGHT, buff=2)

        titles = VGroup(
            TextMobject("Puzzle"),
            TextMobject("Solution"),
        )

        images = Group(
            ImageMobject("BlocksAndWallExampleMass16"),
            ImageMobject("SphereSurfaceProof2"), # TODO
        )
        for title, rect, image in zip(titles, rects, images):
            title.scale(1.5)
            title.next_to(rect, UP)
            image.replace(rect)
            self.add(image, rect, title)

        frame = self.camera_frame
        frame.save_state()

        self.play(
            frame.replace, images[0],
            run_time=3
        )
        self.wait()
        self.play(Restore(frame, run_time=3))
        self.play(
            frame.replace, images[1],
            run_time=3,
        )
        self.wait()



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


class BlocksAndWallExampleMass1e4(BlocksAndWallExample):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 64,
                "velocity": -1.5,
            },
        },
        "wait_time": 25,
    }


class BlocksAndWallExampleMassMillion(BlocksAndWallExample):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 1e6,
                "velocity": -0.9,
                "label_text": "$100^{3}$ kg"
            },
        },
        "wait_time": 30,
        "million_fade_time": 4,
        "min_time_between_sounds": 0.002,
    }

    def setup(self):
        super().setup()
        self.add_million_label()

    def add_million_label(self):
        first_label = self.blocks.block1.label
        brace = Brace(first_label[:-2], UP, buff=SMALL_BUFF)
        new_label = TexMobject("1{,}000{,}000")
        new_label.next_to(brace, UP, buff=SMALL_BUFF)
        new_label.add(brace)
        new_label.set_color(YELLOW)

        def update_label(label):
            d_time = self.get_time() - self.million_fade_time
            opacity = smooth(d_time)
            label.set_fill(opacity=d_time)

        new_label.add_updater(update_label)
        first_label.add(new_label)


class BlocksAndWallExampleMassTrillion(BlocksAndWallExample):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 1e12,
                "velocity": -1,
            },
        },
        "wait_time": 30,
        "min_time_between_sounds": 0.001,
    }

