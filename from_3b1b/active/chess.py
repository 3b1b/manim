from manimlib.imports import *


class Test(Scene):
    CONFIG = {
        "camera_config": {
            "apply_depth_test": True,
        }
    }

    def construct(self):
        chessboard = SGroup(*[
            Cube(square_resolution=(4, 4))
            for x in range(64)
        ])
        chessboard.arrange_in_grid(buff=0)
        chessboard.set_height(7)
        chessboard.set_depth(0.25, stretch=True)
        colors = [LIGHT_GREY, DARKER_GREY]
        for i, j in it.product(range(8), range(8)):
            chessboard[i * 8 + j].set_color(colors[(i + j) % 2])
        chessboard.move_to(ORIGIN, OUT)

        coin = SGroup(
            Disk3D(resolution=(1, 24)).shift(OUT),
            Disk3D(resolution=(1, 24)).shift(IN),
            Cylinder(height=2, resolution=(24, 1))
        )
        coin.set_height(1)
        coin.set_depth(0.1, stretch=True)
        coin.set_color(GOLD_D, 1)
        coin[1].set_color(RED, 1)

        coins = SGroup()
        for cube in chessboard:
            coin = coin.copy()
            if random.random() < 0.5:
                coin.rotate(PI, UP)
            coin.set_height(0.7 * cube.get_height())
            coin.next_to(cube, OUT, buff=0)
            coins.add(coin)

        self.camera.frame.set_rotation(
            phi=45 * DEGREES,
            theta=0 * DEGREES,
        )

        self.add(chessboard)
        self.add(coins)
