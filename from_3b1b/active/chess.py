from manimlib.imports import *


class Chessboard(SGroup):
    CONFIG = {
        "shape": (8, 8),
        "height": 7,
        "depth": 0.25,
        "colors": [LIGHT_GREY, DARKER_GREY]
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        nr, nc = self.shape
        cube = Cube(square_resolution=(3, 3))
        # Replace top square with something slightly higher res
        top_square = Square3D(resolution=(5, 5))
        top_square.replace(cube[0])
        cube.replace_submobject(0, top_square)
        self.add(*[cube.copy() for x in range(nc * nr)])
        self.arrange_in_grid(buff=0)
        self.set_height(self.height)
        self.set_depth(self.depth, stretch=True)
        for i, j in it.product(range(nr), range(nc)):
            color = self.colors[(i + j) % 2]
            self[i * nc + j].set_color(color)
        self.center()


class Coin(Group):
    CONFIG = {
        "n_sides": 24,
        "height": 1,
        "depth": 0.1,
        "color": GOLD_D,
        "tails_color": RED,
        "include_labels": True,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        n = self.n_sides + 1
        self.top = Disk3D(resolution=(4, n)).shift(OUT)
        self.bottom = Disk3D(resolution=(4, n)).shift(IN)
        self.edge = Cylinder(height=2, resolution=(n, 2))
        self.add(self.top, self.bottom, self.edge)
        self.set_color(self.color)
        self.bottom.set_color(RED)

        if self.include_labels:
            labels = VGroup(
                TextMobject("H"),
                TextMobject("T"),
            )
            for label, vect in zip(labels, [OUT, IN]):
                label.shift(1.01 * vect)
                label.set_height(0.8)
            labels[1].flip(RIGHT)
            self.add(*labels)
            self.labels = labels

        self.set_height(self.height)
        self.set_depth(self.depth, stretch=True)


class CoinsOnBoard(Group):
    CONFIG = {
        "proportion_of_square_height": 0.7,
        "coin_config": {},
    }

    def __init__(self, chessboard, **kwargs):
        super().__init__(**kwargs)
        prop = self.proportion_of_square_height
        for cube in chessboard:
            coin = Coin(**self.coin_config)
            coin.set_height(prop * cube.get_height())
            coin.next_to(cube, OUT, buff=0)
            self.add(coin)

    def flip_at_random(self, p=0.5):
        for coin in self:
            if random.random() < p:
                coin.flip(RIGHT)
        return self


# Scenes

class Test(Scene):
    CONFIG = {
        "camera_config": {
            "apply_depth_test": True,
        }
    }

    def construct(self):
        chessboard = Chessboard()
        chessboard.move_to(ORIGIN, OUT)

        coins = CoinsOnBoard(chessboard, include_labels=False)
        coins.flip_at_random()

        self.camera.frame.set_rotation(
            phi=45 * DEGREES,
            theta=0 * DEGREES,
        )

        self.add(chessboard)
        self.add(coins)

        # print(get_runtime(self.update_frame))
        self.play(LaggedStartMap(FadeIn, coins, lambda m: (m, UP), run_time=2))
        self.wait()
        self.play(FadeOut(chessboard, RIGHT))
