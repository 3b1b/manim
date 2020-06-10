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


class FlipCoin(Animation):
    CONFIG = {
        "axis": RIGHT,
        "run_time": 1,
        "shift_dir": OUT,
    }

    def __init__(self, coin, **kwargs):
        super().__init__(coin, **kwargs)
        self.shift_vect = coin.get_height() * self.shift_dir / 2

    def interpolate_mobject(self, alpha):
        coin = self.mobject
        for sm, start_sm in self.families:
            sm.points[:] = start_sm.points
        coin.rotate(alpha * PI, axis=self.axis)
        coin.shift(4 * alpha * (1 - alpha) * self.shift_vect)
        return coin

# Scenes

class IntroducePuzzle(Scene):
    CONFIG = {
        "camera_config": {
            "apply_depth_test": True,
            "samples": 8,
        }
    }

    def construct(self):
        frame = self.camera.frame

        chessboard = Chessboard()
        chessboard.move_to(ORIGIN, OUT)

        plane = NumberPlane(
            x_range=(0, 8), y_range=(0, 8),
            faded_line_ratio=1,
        )

        coins = CoinsOnBoard(chessboard, include_labels=False)
        coins_random_order = Group(*coins)
        coins_random_order.shuffle()

        frame.set_phi(45 * DEGREES)

        self.add(chessboard)
        self.play(LaggedStartMap(FadeIn, coins_random_order, lambda m: (m, UP), run_time=1))
        self.add(coins)
        self.wait()

        coins_to_flip = Group(*[c for c in coins_random_order if random.random() < 0.5])
        self.play(LaggedStartMap(FlipCoin, coins_to_flip, run_time=1, lag_ratio=0.05))
        self.wait()

        self.embed()
