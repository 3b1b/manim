from manimlib.imports import *


def boolian_linear_combo(bools):
    return reduce(op.xor, [b * n for n, b in enumerate(bools)], 0)


def string_to_bools(message):
    # For easter eggs on the board
    as_int = int.from_bytes(message.encode(), 'big')
    bits = "{0:b}".format(as_int)
    bits = (len(message) * 8 - len(bits)) * '0' + bits
    return [bool(int(b)) for b in bits]


def layer_mobject(mobject, nudge=1e-6):
    for i, sm in enumerate(mobject.family_members_with_points()):
        sm.shift(i * nudge * OUT)


def int_to_bit_coords(n, min_dim=3):
    bits = "{0:b}".format(n)
    bits = (min_dim - len(bits)) * '0' + bits
    return np.array(list(map(int, bits)))


def bit_coords_to_int(bits):
    return sum([(2**n) * b for n, b in enumerate(reversed(bits))])


def get_vertex_sphere(height=0.4, color=GREY, resolution=(21, 21)):
    sphere = Sphere(resolution=resolution)
    sphere.set_height(height)
    sphere.set_color(color)
    return sphere


def get_bit_string(bit_coords):
    result = VGroup(*[Integer(int(b)) for b in bit_coords])
    result.arrange(RIGHT, buff=SMALL_BUFF)
    result.set_stroke(BLACK, 4, background=True)
    return result


class Chessboard(SGroup):
    CONFIG = {
        "shape": (8, 8),
        "height": 7,
        "depth": 0.25,
        "colors": [LIGHT_GREY, DARKER_GREY],
        "gloss": 0.2,
        "square_resolution": (3, 3),
        "top_square_resolution": (5, 5),
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        nr, nc = self.shape
        cube = Cube(square_resolution=self.square_resolution)
        # Replace top square with something slightly higher res
        top_square = Square3D(resolution=self.top_square_resolution)
        top_square.replace(cube[0])
        cube.replace_submobject(0, top_square)
        self.add(*[cube.copy() for x in range(nc * nr)])
        self.arrange_in_grid(nr, nc, buff=0)
        self.set_height(self.height)
        self.set_depth(self.depth, stretch=True)
        for i, j in it.product(range(nr), range(nc)):
            color = self.colors[(i + j) % 2]
            self[i * nc + j].set_color(color)
        self.center()
        self.set_gloss(self.gloss)


class Coin(Group):
    CONFIG = {
        "disk_resolution": (4, 51),
        "height": 1,
        "depth": 0.1,
        "color": GOLD_D,
        "tails_color": RED,
        "include_labels": True,
        "numeric_labels": False,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        res = self.disk_resolution
        self.top = Disk3D(resolution=res, gloss=0.2)
        self.bottom = self.top.copy()
        self.top.shift(OUT)
        self.bottom.shift(IN)
        self.edge = Cylinder(height=2, resolution=(res[1], 2))
        self.add(self.top, self.bottom, self.edge)
        self.rotate(90 * DEGREES, OUT)
        self.set_color(self.color)
        self.bottom.set_color(RED)

        if self.include_labels:
            chars = "10" if self.numeric_labels else "HT"
            labels = VGroup(*[TextMobject(c) for c in chars])
            for label, vect in zip(labels, [OUT, IN]):
                label.shift(1.02 * vect)
                label.set_height(0.8)
            labels[1].rotate(PI, RIGHT)
            labels.apply_depth_test()
            labels.set_stroke(width=0)
            self.add(*labels)
            self.labels = labels

        self.set_height(self.height)
        self.set_depth(self.depth, stretch=True)

    def is_heads(self):
        return self.top.get_center()[2] > self.bottom.get_center()[2]

    def flip(self, axis=RIGHT):
        super().flip(axis)


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
        bools = np.random.random(len(self)) < p
        self.flip_by_bools(bools)
        return self

    def flip_by_message(self, message):
        self.flip_by_bools(string_to_bools(message))
        return self

    def flip_by_bools(self, bools):
        for coin, head in zip(self, bools):
            if coin.is_heads() ^ head:
                coin.flip()
        return self

    def get_bools(self):
        return [coin.is_heads() for coin in self]


class Key(SVGMobject):
    CONFIG = {
        "file_name": "key",
        "fill_color": YELLOW_D,
        "fill_opacity": 1,
        "stroke_color": YELLOW_D,
        "stroke_width": 0,
        "gloss": 0.5,
        "depth_test": True,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rotate(PI / 2, OUT)


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
        "camera_class": ThreeDCamera,
    }

    def construct(self):
        # Setup
        frame = self.camera.frame

        chessboard = Chessboard()
        chessboard.move_to(ORIGIN, OUT)

        grid = NumberPlane(
            x_range=(0, 8), y_range=(0, 8),
            faded_line_ratio=0
        )
        grid.match_height(chessboard)
        grid.next_to(chessboard, OUT, 1e-8)
        low_grid = grid.copy()
        low_grid.next_to(chessboard, IN, 1e-8)
        grid.add(low_grid)
        grid.set_stroke(GREY, width=2)
        grid.set_gloss(0.5)
        grid.prepare_for_nonlinear_transform(0)

        coins = CoinsOnBoard(chessboard)
        coins.set_gloss(0.2)
        coins_to_flip = Group()
        head_bools = string_to_bools('3b1b  :)')
        for coin, heads in zip(coins, head_bools):
            if not heads:
                coins_to_flip.add(coin)
        coins_to_flip.shuffle()

        count_label = VGroup(
            Integer(0, edge_to_fix=RIGHT),
            TextMobject("Coins")
        )
        count_label.arrange(RIGHT, aligned_edge=DOWN)
        count_label.to_corner(UL)
        count_label.fix_in_frame()

        # Draw board and coins
        frame.set_rotation(-25 * DEGREES, 70 * DEGREES, 0)
        self.play(
            FadeIn(chessboard),
            ShowCreationThenDestruction(grid, lag_ratio=0.01),
            frame.set_theta, 0,
            frame.set_phi, 45 * DEGREES,
            run_time=3,
        )
        self.wait()

        self.add(count_label)
        self.play(
            ShowIncreasingSubsets(coins),
            UpdateFromFunc(count_label[0], lambda m, c=coins: m.set_value(len(c))),
            rate_func=bezier([0, 0, 1, 1]),
            run_time=2,
        )
        self.wait()
        self.play(LaggedStartMap(FlipCoin, coins_to_flip, run_time=6, lag_ratio=0.1))
        self.add(coins)
        coins.unlock_shader_data()
        self.wait()

        # Show key
        key = Key()
        key.rotate(PI / 4, RIGHT)
        key.move_to(3 * OUT)
        key.scale(0.8)
        key.to_edge(LEFT, buff=1)

        k = boolian_linear_combo(head_bools) ^ 63  # To make the flip below the actual solution
        key_cube = Cube(resolution=(6, 6))
        key_cube.match_color(chessboard[k])
        key_cube.replace(chessboard[k], stretch=True)
        chessboard.replace_submobject(k, key_cube)
        key_square = key_cube[0]
        chessboard.generate_target()
        chessboard.save_state()
        for i, cube in enumerate(chessboard.target):
            if i == k:
                cube[0].set_color(MAROON_E)
            else:
                cube.set_color(interpolate_color(cube.get_color(), BLACK, 0.8))

        key.generate_target()
        key.target.rotate(PI / 4, LEFT)
        key.target.set_width(0.7 * key_square.get_width())
        key.target.next_to(key_square, IN, buff=SMALL_BUFF)

        self.play(FadeIn(key, LEFT))
        self.wait()
        self.play(
            FadeOut(coins, lag_ratio=0.01),
            MoveToTarget(chessboard),
        )
        ks_top = key_square.get_top()
        self.play(
            Rotate(key_square, PI / 2, axis=LEFT, about_point=ks_top),
            MoveToTarget(key),
            frame.set_phi, 60 * DEGREES,
            run_time=2,
        )
        self.play(
            Rotate(key_square, PI / 2, axis=RIGHT, about_point=ks_top),
            run_time=2,
        )
        chessboard.unlock_shader_data()
        chessboard.saved_state[k][0].match_color(key_square)
        self.play(
            chessboard.restore,
            FadeIn(coins),
            frame.set_phi, 0 * DEGREES,
            frame.move_to, 2 * LEFT,
            run_time=3
        )

        # State goal
        goal = TextMobject(
            "Communicate where\\\\the key is",
            " by turning\\\\over one coin.",
            alignment=""
        )
        goal.next_to(count_label, DOWN, LARGE_BUFF, LEFT)
        goal.fix_in_frame()
        goal[1].set_color(YELLOW)

        self.play(FadeIn(goal[0]))
        self.wait()
        self.play(FadeIn(goal[1]))
        self.wait()

        coin = coins[63]
        rect = SurroundingRectangle(coin, color=TEAL)
        rect.set_opacity(0.5)
        rect.save_state()
        rect.replace(chessboard)
        rect.set_stroke(width=0)
        rect.set_fill(opacity=0)

        self.play(Restore(rect, run_time=2))
        self.add(coin, rect)
        self.play(FlipCoin(coin), FadeOut(rect))


class PrisonerPuzzleSetting(PiCreatureScene):
    CONFIG = {
        "camera_config": {
            "background_color": GREY_E
        }
    }

    def create_pi_creatures(self):
        p1 = PiCreature(color=BLUE_C, height=2)
        p2 = PiCreature(color=RED, height=2)
        warden = PiCreature(color=GREY_BROWN, height=2.5)
        warden.flip()
        result = VGroup(p1, p2, warden)
        result.arrange(RIGHT, buff=2, aligned_edge=DOWN)
        warden.shift(RIGHT)
        result.center().to_edge(DOWN, buff=1.5)
        return result

    def construct(self):
        pis = self.pi_creatures
        p1, p2, warden = self.pi_creatures

        names = VGroup(
            TextMobject("Prisoner 1\\\\(you)"),
            TextMobject("Prisoner 2"),
            TextMobject("Warden"),
        )
        for name, pi in zip(names, pis):
            name.match_color(pi.body)
            name.next_to(pi, DOWN)

        question = TextMobject(
            "Why do mathematicians\\\\always set their puzzles\\\\in prisons?",
            alignment=""
        )
        question.to_corner(UR)

        self.remove(warden)
        warden.look_at(p2.eyes)
        self.play(
            LaggedStartMap(FadeIn, pis[:2], run_time=1.5, lag_ratio=0.3),
            LaggedStartMap(FadeIn, names[:2], run_time=1.5, lag_ratio=0.3),
        )
        self.play(
            p1.change, "sad",
            p2.change, "pleading", warden.eyes
        )
        self.play(
            FadeIn(warden),
            FadeIn(names[2]),
        )
        self.play(warden.change, "conniving", p2.eyes)
        self.wait()
        self.play(FadeIn(question, lag_ratio=0.1))
        self.wait(3)
        self.play(FadeOut(question))
        self.wait(2)


class FromCoinToSquareMaps(ThreeDScene):
    CONFIG = {
        "messages": [
            "Please, ",
            "go watch",
            "Stand-up",
            "Maths on",
            "YouTube."
        ],
        "flip_lag_ratio": 0.05,
    }

    def construct(self):
        messages = self.messages

        board1 = Chessboard()
        board1.set_width(5.5)
        board1.to_corner(DL)

        board2 = board1.copy()
        board2.to_corner(DR)

        coins = CoinsOnBoard(board1)
        bools = string_to_bools(messages[0])
        for coin, head in zip(coins, bools):
            if not head:
                coin.flip(RIGHT)

        for cube in board2:
            cube.original_color = cube.get_color()

        arrow = Arrow(board1.get_right(), board2.get_left())
        arrow.tip.set_stroke(width=0)

        title1 = TextMobject("Pattern of coins")
        title2 = TextMobject("Individual square")

        for title, board in [(title1, board1), (title2, board2)]:
            title.scale(0.5 / title[0][0].get_height())
            title.next_to(board, UP, MED_LARGE_BUFF)

        title2.align_to(title1, UP)

        def get_special_square(coins=coins, board=board2):
            bools = [coin.is_heads() for coin in coins]
            return board[boolian_linear_combo(bools)]

        self.add(board1)
        self.add(title1)
        self.add(coins)

        self.play(
            GrowArrow(arrow),
            FadeIn(board2, 2 * LEFT)
        )
        square = get_special_square()
        rect = SurroundingRectangle(square, buff=0)
        rect.set_color(PINK)
        rect.next_to(square, OUT, buff=0.01)
        self.play(
            square.set_color, MAROON_C,
            ShowCreation(rect),
            FadeIn(title2)
        )

        for message in messages[1:]:
            new_bools = string_to_bools(message)
            coins_to_flip = Group()
            for coin, to_heads in zip(coins, new_bools):
                if coin.is_heads() ^ to_heads:
                    coins_to_flip.add(coin)
            coins_to_flip.shuffle()
            self.play(LaggedStartMap(
                FlipCoin, coins_to_flip,
                lag_ratio=self.flip_lag_ratio,
                run_time=1,
            ))

            new_square = get_special_square()
            self.play(
                square.set_color, square.original_color,
                new_square.set_color, MAROON_C,
                rect.move_to, new_square, OUT,
                rect.shift, 0.01 * OUT,
            )
            square = new_square
            self.wait()


class FromCoinToSquareMapsSingleFlips(FromCoinToSquareMaps):
    CONFIG = {
        "messages": [
            "FlipBits",
            "BlipBits",
            "ClipBits",
            "ChipBits",
            "ChipBats",
            "ChipRats",
        ]
    }


class DiagramOfProgression(ThreeDScene):
    def construct(self):
        # Setup panels
        P1_COLOR = BLUE_C
        P2_COLOR = RED

        rect = Rectangle(4, 2)
        rect.set_fill(GREY_E, 1)
        panels = Group()
        for x in range(4):
            panels.add(Group(rect.copy()))
        panels.arrange_in_grid(buff=1)
        panels[::2].shift(0.5 * LEFT)
        panels.set_width(FRAME_WIDTH - 2)
        panels.center().to_edge(DOWN)
        p1_shift = panels[1].get_center() - panels[0].get_center()
        panels[1].move_to(panels[0])

        chessboard = Chessboard()
        chessboard.set_height(0.9 * panels[0].get_height())
        coins = CoinsOnBoard(
            chessboard,
            coin_config={
                "disk_resolution": (2, 25),
            }
        )
        coins.flip_by_message("Tau > Pi")

        for panel in panels[1:]:
            cb = chessboard.copy()
            co = coins.copy()
            cb.next_to(panel.get_right(), LEFT)
            co.next_to(cb, OUT, 0)
            panel.chessboard = cb
            panel.coins = co
            panel.add(cb, co)

        kw = {
            "tex_to_color_map": {
                "Prisoner 1": P1_COLOR,
                "Prisoner 2": P2_COLOR,
            }
        }
        titles = VGroup(
            TextMobject("Prisoners conspire", **kw),
            TextMobject("Prisoner 1 sees key", **kw),
            TextMobject("Prisoner 1 flips coin", **kw),
            TextMobject("Prisoner 2 guesses key square", **kw),
        )

        for panel, title in zip(panels, titles):
            title.next_to(panel, UP)
            panel.title = title
            panel.add(title)

        # Darken first chessboard
        for coin in panels[1].coins:
            coin.remove(coin.edge)
            if coin.is_heads():
                coin.remove(coin.bottom)
                coin.remove(coin.labels[1])
            else:
                coin.remove(coin.top)
                coin.remove(coin.labels[0])
            coin.set_opacity(0.25)

        # Add characters
        prisoner1 = PiCreature(color=P1_COLOR)
        prisoner2 = PiCreature(color=P2_COLOR)
        pis = VGroup(prisoner1, prisoner2)
        pis.arrange(RIGHT, buff=1)
        pis.set_height(1.5)

        p0_pis = pis.copy()
        p0_pis.set_height(2.0, about_edge=DOWN)
        p0_pis[1].flip()
        p0_pis.next_to(panels[0].get_bottom(), UP, SMALL_BUFF)
        p0_pis[0].change("pondering", p0_pis[1].eyes)
        p0_pis[1].change("speaking", p0_pis[0].eyes)
        panels[0].add(p0_pis)

        p1_pi = pis[0].copy()
        p1_pi.next_to(panels[1].get_corner(DL), UR, SMALL_BUFF)
        p1_pi.change("happy")
        key = Key()
        key.set_height(0.5)
        key.next_to(p1_pi, UP)
        key.set_color(YELLOW)
        key_cube = panels[1].chessboard[18]
        key_square = Square()
        key_square.replace(key_cube)
        key_square.set_stroke(width=3)
        key_square.match_color(key)
        p1_pi.look_at(key_square)
        key_arrow = Arrow(
            key.get_right() + SMALL_BUFF * UP,
            key_square.get_corner(UL),
            path_arc=-45 * DEGREES,
            buff=SMALL_BUFF
        )
        key_arrow.tip.set_stroke(width=0)
        key_arrow.match_color(key)
        panels[1].add(p1_pi, key)

        p2_pi = pis[0].copy()
        p2_pi.next_to(panels[2].get_corner(DL), UR, SMALL_BUFF)
        p2_pi.change("tease")
        flip_coin = panels[2].coins[38]
        panels[3].coins[38].flip()
        flip_square = Square()
        flip_square.replace(panels[2].chessboard[38])
        flip_square.set_stroke(BLUE, 5)
        for coin in panels[2].coins:
            if coin is not flip_coin:
                coin.remove(coin.edge)
                if coin.is_heads():
                    coin.remove(coin.bottom)
                    coin.remove(coin.labels[1])
                else:
                    coin.remove(coin.top)
                    coin.remove(coin.labels[0])
                coin.set_opacity(0.25)
        panels[2].add(p2_pi)

        p3_pi = pis[1].copy()
        p3_pi.next_to(panels[3].get_corner(DL), UR, SMALL_BUFF)
        p3_pi.shift(MED_LARGE_BUFF * RIGHT)
        p3_pi.change("confused")
        panels[3].add(p3_pi)

        # Animate each panel in
        self.play(FadeIn(panels[1], DOWN))
        self.play(
            ShowCreation(key_arrow),
            FadeInFromLarge(key_square),
        )
        panels[1].add(key_arrow, key_square)
        self.wait()

        self.play(FadeIn(panels[2], UP))
        self.play(
            ShowCreation(flip_square),
            FlipCoin(flip_coin),
            p2_pi.look_at, flip_coin,
        )
        self.wait()

        self.play(FadeIn(panels[3], LEFT))
        self.wait()

        self.play(
            FadeIn(panels[0], LEFT),
            panels[1].shift, p1_shift,
        )
        self.wait()


class ImpossibleVariations(FromCoinToSquareMaps):
    CONFIG = {
        "messages": [
            "FlipBits",
            "BlipBits",
            "ClipBits",
            "ChipBits",
            "ChipBats",
            "ChipRats",
            "ChipVats",
            "ChipFats",
            "ChapFats",
        ]
    }

    def construct(self):
        # Definitions
        frame = self.camera.frame
        title = TextMobject("Describe any square\\\\with one flip")
        title.set_height(1.2)
        title.to_edge(UP)
        title.fix_in_frame()
        messages = it.cycle(self.messages)

        left_board = Chessboard()
        right_board = Chessboard()
        for board, vect in (left_board, LEFT), (right_board, RIGHT):
            board.set_width(4.5)
            board.to_corner(DOWN + vect, buff=LARGE_BUFF)
        coins = CoinsOnBoard(left_board)
        coins.flip_by_message(next(messages))

        arrow = Arrow(left_board.get_right(), right_board.get_left())

        # Prepare for colorings
        for cube in right_board:
            cube.original_color = cube.get_color()

        def get_special_square(board=right_board, coins=coins):
            return board[boolian_linear_combo(coins.get_bools())]

        frame.set_phi(45 * DEGREES)

        # Introduce boards
        self.add(title)
        group = Group(*left_board, *coins, *right_board)
        self.play(
            LaggedStartMap(FadeInFromLarge, group, lambda m: (m, 1.3), lag_ratio=0.01),
            GrowArrow(arrow)
        )

        # Flip one at a time
        square = Square()
        square.set_stroke(TEAL, 3)
        square.replace(right_board[0])
        square.move_to(right_board[0], OUT)
        self.moving_square = square
        self.colored_square = right_board[0]

        for x in range(8):
            self.set_board_message(next(messages), left_board, coins, get_special_square)
            self.wait()

        # To 6x6
        to_fade = Group()
        for grid in left_board, right_board, coins:
            for n, mob in enumerate(grid):
                row = n // 8
                col = n % 8
                if not ((0 < row < 7) and (0 < col < 7)):
                    to_fade.add(mob)

        cross = Cross(title)
        cross.fix_in_frame()
        cross.set_stroke(RED, 8)
        cross.shift(2 * LEFT)
        imp_words = TextMobject("Impossible!")
        imp_words.fix_in_frame()
        imp_words.next_to(title, RIGHT, buff=1.5)
        imp_words.shift(2 * LEFT)
        imp_words.set_height(0.7)
        imp_words.set_color(RED)

        self.play(to_fade.set_opacity, 0.05)
        self.play(
            title.shift, 2 * LEFT,
            FadeIn(cross, 2 * RIGHT),
            FadeIn(imp_words, LEFT)
        )
        self.wait()
        self.play(to_fade.set_opacity, 1)

        # Remove a square
        to_remove = Group(
            left_board[63], right_board[63], coins[63]
        )
        remove_words = TextMobject("Remove one\\\\square")
        remove_words.set_color(RED)
        remove_words.to_corner(DOWN, buff=1.5)
        remove_words.fix_in_frame()

        self.play(
            FadeIn(remove_words, DOWN),
            FadeOut(to_remove, 3 * IN),
        )

    def set_board_message(self, message, left_board, coins, get_special_square):
        new_bools = string_to_bools(message)
        coins_to_flip = Group()
        for coin, to_heads in zip(coins, new_bools):
            if coin.is_heads() ^ to_heads:
                coins_to_flip.add(coin)
        coins_to_flip.shuffle()
        self.play(LaggedStartMap(
            FlipCoin, coins_to_flip,
            lag_ratio=self.flip_lag_ratio,
            run_time=1,
        ))

        new_colored_square = get_special_square()
        self.play(
            new_colored_square.set_color, BLUE,
            self.colored_square.set_color, self.colored_square.original_color,
            self.moving_square.move_to, get_special_square(), OUT,
        )
        self.colored_square = new_colored_square


class ErrorCorrectionMention(Scene):
    def construct(self):
        # Setup board
        message = "Do math!"
        error_message = "Do meth!"
        board = Chessboard()
        board.set_width(5)
        board.to_corner(DL)
        coins = CoinsOnBoard(board)
        coins.flip_by_message(message)
        bools = coins.get_bools()

        right_board = board.copy()
        right_board.to_corner(DR)
        right_board.set_opacity(0.5)
        right_board[boolian_linear_combo(bools)].set_color(BLUE, 1)

        arrow = Arrow(board.get_right(), right_board.get_left())

        words = TextMobject("Feels a bit like ", "Error correction codes", "$\\dots$")
        words.scale(1.2)
        words.to_edge(UP)

        self.add(board, coins, right_board)
        self.add(arrow)
        self.add(words)

        # Go from board diagram to bit string
        bits = VGroup()
        for coin in coins:
            bit = Integer(1 if coin.is_heads() else 0)
            bit.replace(coin, dim_to_match=1)
            bits.add(bit)

            coin.generate_target()
            coin.target.rotate(90 * DEGREES, RIGHT)
            coin.target.set_opacity(0)

        bits_rect = SurroundingRectangle(bits, buff=MED_SMALL_BUFF)
        bits_rect.set_stroke(YELLOW, 2)
        data_label = TextMobject("Data")
        data_label.next_to(bits_rect, UP)
        data_label.set_color(YELLOW)

        meaning_label = TextMobject(f"``{message}''")
        error_meaning_label = TextMobject(f"``{error_message}''")
        for label in meaning_label, error_meaning_label:
            label.scale(1.5)
            label.next_to(arrow, RIGHT)
        error_meaning_label[0][5].set_color(RED)

        message_label = TextMobject("Message")
        message_label.set_color(BLUE)
        message_label.next_to(meaning_label, UP, buff=1.5)
        message_label.to_edge(RIGHT, LARGE_BUFF)
        message_arrow = Arrow(
            message_label.get_bottom(),
            meaning_label.get_top(),
        )
        message_arrow = Arrow(
            message_label.get_left(),
            meaning_label.get_top(),
            path_arc=70 * DEGREES,
        )

        self.play(
            LaggedStartMap(MoveToTarget, coins),
            LaggedStartMap(FadeOut, board),
            Write(bits),
            run_time=3
        )
        self.play(
            words[1].set_x, 0,
            FadeOut(words[0], LEFT),
            FadeOut(words[2], LEFT),
        )
        self.play(
            ShowCreation(bits_rect),
            FadeIn(data_label, DOWN)
        )
        self.play(
            FadeOut(right_board),
            FadeIn(message_label, DOWN),
            ShowCreation(message_arrow),
            FadeIn(meaning_label)
        )
        self.wait()

        # Describe ECC
        error_index = 8 * 4 + 5
        error_bit = bits[error_index]
        error_bit.unlock_triangulation()
        error_bit_rect = SurroundingRectangle(error_bit)
        error_bit_rect.set_stroke(RED, 2)

        self.play(
            FadeInFromLarge(error_bit_rect),
            error_bit.set_value, 1 - error_bit.get_value(),
            error_bit.set_color, RED,
        )
        meaning_label.save_state()
        meaning_label.unlock_triangulation()
        self.play(
            Transform(meaning_label, error_meaning_label)
        )
        self.wait()

        # Ask about correction
        question = TextMobject("How can you\\\\detect the error?")
        question.next_to(bits_rect, RIGHT, aligned_edge=UP)
        self.play(Write(question))
        self.wait(2)

        ecc = VGroup()
        for bit in int_to_bit_coords(boolian_linear_combo(bools), 6):
            ecc.add(Integer(bit).match_height(bits[0]))
        ecc.arrange(RIGHT, buff=0.2)
        ecc.set_color(GREEN)
        ecc.next_to(bits, RIGHT, MED_LARGE_BUFF, aligned_edge=DOWN)
        ecc_rect = SurroundingRectangle(ecc, buff=MED_SMALL_BUFF)
        ecc_rect.set_stroke(GREEN, 2)

        ecc_name = words[1]
        ecc_name.generate_target()
        ecc_name.target[-1].set_opacity(0)
        ecc_name.target.scale(0.75)
        ecc_name.target.next_to(ecc_rect)
        ecc_name.target.match_color(ecc)

        frame = self.camera.frame

        self.play(
            MoveToTarget(ecc_name),
            ShowIncreasingSubsets(ecc),
            ShowCreation(ecc_rect),
            ApplyMethod(frame.move_to, DOWN, run_time=2)
        )
        self.wait()

        # Show correction at play
        lines = VGroup()
        for bit in bits:
            line = Line(ecc_rect.get_top(), bit.get_center())
            line.set_stroke(GREEN, 1, opacity=0.7)
            lines.add(line)

        alert = TexMobject("!!!")[0]
        alert.arrange(RIGHT, buff=SMALL_BUFF)
        alert.scale(1.5)
        alert.set_color(RED)
        alert.next_to(ecc_rect, UP)

        self.play(LaggedStartMap(
            ShowCreationThenFadeOut, lines,
            lag_ratio=0.02, run_time=3
        ))
        self.play(FadeIn(alert, DOWN, lag_ratio=0.2))
        self.wait()
        self.play(ShowCreation(lines, lag_ratio=0))
        for line in lines:
            line.generate_target()
            line.target.become(lines[error_index])
        self.play(LaggedStartMap(MoveToTarget, lines, lag_ratio=0, run_time=1))
        self.play(
            error_bit.set_value, 0,
            Restore(meaning_label)
        )
        self.play(
            FadeOut(lines),
            FadeOut(alert),
            FadeOut(error_bit_rect),
            error_bit.set_color, WHITE,
        )
        self.wait()

        # Hamming name
        hamming_label = TextMobject("e.g. Hamming codes")
        hamming_label.move_to(ecc_name, LEFT)

        self.play(
            Write(hamming_label),
            FadeOut(ecc_name, DOWN)
        )
        self.wait()


class StandupMathsWrapper(Scene):
    CONFIG = {
        "title": "Solution on Stand-up Maths"
    }

    def construct(self):
        fsr = FullScreenFadeRectangle()
        fsr.set_fill(GREY_E, 1)
        self.add(fsr)

        title = TextMobject(self.title)
        title.scale(1.5)
        title.to_edge(UP)

        rect = ScreenRectangle(height=6)
        rect.set_stroke(WHITE, 2)
        rect.set_fill(BLACK, 1)
        rect.next_to(title, DOWN)
        rb = AnimatedBoundary(rect)

        self.add(rect, rb)
        self.play(Write(title))
        self.wait(30)


class ComingUpWrapper(StandupMathsWrapper):
    CONFIG = {
        "title": "Coming up"
    }


class TitleCard(Scene):
    def construct(self):
        n = 6
        board = Chessboard(shape=(n, n))
        for square in board:
            square.set_color(interpolate_color(square.get_color(), BLACK, 0.25))
        # board[0].set_opacity(0)

        grid = NumberPlane(
            x_range=(0, n),
            y_range=(0, n),
            faded_line_ratio=0
        )
        grid.match_height(board)
        grid.next_to(board, OUT, 1e-8)
        low_grid = grid.copy()
        low_grid.next_to(board, IN, 1e-8)
        grid.add(low_grid)
        grid.set_stroke(GREY, width=1)
        grid.set_gloss(0.5)
        grid.prepare_for_nonlinear_transform(0)
        grid.rotate(PI, RIGHT)

        frame = self.camera.frame
        frame.set_phi(45 * DEGREES)

        text = TextMobject("The impossible\\\\chessboard puzzle")
        # text.set_width(board.get_width() - 0.5)
        text.set_width(FRAME_WIDTH - 2)
        text.set_stroke(BLACK, 10, background=True)
        text.fix_in_frame()
        self.play(
            ApplyMethod(frame.set_phi, 0, run_time=5),
            ShowCreationThenDestruction(grid, lag_ratio=0.02, run_time=3),
            LaggedStartMap(FadeIn, board, run_time=3, lag_ratio=0),
            Write(text, lag_ratio=0.1, run_time=3, stroke_color=BLUE_A),
        )
        self.wait(2)


class WhatAreWeDoingHere(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Wait, what are we\\\\doing here then?",
            target_mode="sassy",
            added_anims=[self.get_student_changes("hesitant", "angry", "sassy")],
            run_time=2
        )
        self.play(self.teacher.change, "tease")
        self.wait(6)


class HowCanWeVisualizeSolutions(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "How can we\\\\visualize solutions",
            bubble_kwargs={
                "height": 3,
                "width": 4,
                "fill_opacity": 0,
            },
            added_anims=[self.get_student_changes("pondering", "thinking", "pondering")]
        )
        self.look_at(self.screen),
        self.wait(1)
        self.change_student_modes("thinking", "erm", "confused")
        self.wait(5)


class TwoSquareCase(ThreeDScene):
    CONFIG = {
        "coin_names": ["c_0", "c_1"]
    }

    def construct(self):
        frame = self.camera.frame

        # Transition to just two square
        chessboard = Chessboard()
        chessboard.shift(2 * IN + UP)
        coins = CoinsOnBoard(chessboard)
        coins.flip_by_message("To 2 bits")

        to_remove = Group(*it.chain(*zip(chessboard[:1:-1], coins[:1:-1])))
        small_board = chessboard[:2]
        coin_pair = coins[:2]
        small_group = Group(small_board, coin_pair)

        frame.set_phi(45 * DEGREES)

        two_square_words = TextMobject("What about a 2-square board?")
        two_square_words.fix_in_frame()
        two_square_words.set_height(0.5)
        two_square_words.center().to_edge(UP)

        self.add(chessboard, coins)
        self.play(
            Write(two_square_words, run_time=1),
            LaggedStartMap(
                FadeOut, to_remove,
                lambda m: (m, DOWN),
                run_time=2,
                lag_ratio=0.01
            ),
            small_group.center,
            small_group.set_height, 1.5,
            frame.set_phi, 10 * DEGREES,
            run_time=2
        )
        self.wait(3)

        coins = coin_pair

        # Show two locations for the key
        key = Key()
        key.set_width(0.7 * small_board[0].get_width())
        key.move_to(small_board[0])
        key.shift(0.01 * OUT)

        coin_pair.shift(0.04 * OUT)
        s0_top = small_board[0][0].get_top()
        s1_top = small_board[1][0].get_top()

        s0_rot_group = Group(small_board[0][0], coin_pair[0])
        s1_rot_group = Group(small_board[1][0], coin_pair[1])

        self.add(key)
        angle = 170 * DEGREES
        self.play(
            Rotate(s0_rot_group, angle, LEFT, about_point=s0_top),
            Rotate(s1_rot_group, angle, LEFT, about_point=s1_top),
            frame.set_phi, 45 * DEGREES,
        )
        self.wait()
        self.play(
            key.match_x, small_board[1],
            path_arc=PI,
            path_arc_axis=UP,
        )
        self.wait()
        self.play(
            Rotate(s0_rot_group, angle, RIGHT, about_point=s0_top),
            Rotate(s1_rot_group, angle, RIGHT, about_point=s1_top),
            frame.set_phi, 0,
            run_time=2,
        )
        self.wait()

        # Show four states pointing to two message
        states = VGroup(*[
            TextMobject(letters, tex_to_color_map={"H": GOLD, "T": RED_D})
            for letters in ["TT", "HT", "TH", "HH"]
        ])
        states.set_height(0.8)
        states.arrange(DOWN, buff=1)
        states.to_edge(LEFT)

        self.play(
            FadeOut(two_square_words),
            FlipCoin(coins[1]),
            FadeIn(states[0])
        )
        self.play(
            FlipCoin(coins[0]),
            FadeIn(states[1])
        )
        self.play(
            FlipCoin(coins[0]),
            FlipCoin(coins[1]),
            FadeIn(states[2])
        )
        self.play(
            FlipCoin(coins[0]),
            FadeIn(states[3])
        )
        self.wait()

        key_copy = key.copy()
        key_copy.match_x(small_board[0])
        small_board_copy = small_board.copy()
        small_boards = Group(small_board_copy, small_board)
        for board, vect in zip(small_boards, [UP, DOWN]):
            board.generate_target()
            board.target.set_opacity(0.7)
            board.target.shift(2 * vect)
            board.target.set_depth(0.01, stretch=True)
        self.add(key, key_copy, *small_boards)
        self.play(
            FadeOut(coins),
            MoveToTarget(small_board),
            MaintainPositionRelativeTo(key, small_board),
            MoveToTarget(small_board_copy),
            MaintainPositionRelativeTo(key_copy, small_board_copy),
        )
        self.add(*small_boards, key, key_copy)

        arrows = VGroup()
        for i in range(4):
            arrows.add(Arrow(states[i].get_right(), small_boards[i // 2].get_left()))
        arrows.set_opacity(0.75)

        self.play(LaggedStartMap(GrowArrow, arrows, lag_ratio=0.3))
        self.wait()

        # Show one flip changing interpretation
        coins.next_to(states, LEFT, buff=1.5)

        def get_state(coins=coins):
            bools = [c.is_heads() for c in coins]
            return sum([b * (2**n) for n, b in enumerate(reversed(bools))])

        n = 3
        state_rect = SurroundingRectangle(states[n])
        board_rects = VGroup()
        for board in small_boards:
            br = SurroundingRectangle(board, buff=0)
            br.move_to(board, OUT)
            br.set_stroke(YELLOW, 3)
            board_rects.add(br)

        self.play(
            ApplyMethod(frame.shift, 4.5 * LEFT, run_time=1),
            FadeIn(coins),
            FadeIn(state_rect),
            FadeIn(board_rects[1]),
            arrows[n].set_color, YELLOW,
            arrows[n].set_opacity, 1,
        )
        self.wait()
        self.play(
            FlipCoin(coins[1]),
            FadeOut(board_rects[1]),
            FadeIn(board_rects[0]),
            state_rect.move_to, states[1],
            arrows[3].match_style, arrows[0],
            arrows[1].match_style, arrows[3],
        )
        self.wait()
        self.play(
            FlipCoin(coins[0]),
            state_rect.move_to, states[0],
            arrows[0].match_style, arrows[1],
            arrows[1].match_style, arrows[3],
        )
        self.wait()
        self.play(
            FlipCoin(coins[0]),
            state_rect.move_to, states[1],
            arrows[0].match_style, arrows[1],
            arrows[1].match_style, arrows[0],
        )
        self.wait()

        # Erase H and T, replace with 1 and 0
        bin_states = VGroup(*[
            TextMobject(letters, tex_to_color_map={"1": GOLD, "0": RED_D})
            for letters in ["00", "10", "01", "11"]
        ])
        for bin_state, state in zip(bin_states, states):
            for bit, letter in zip(bin_state, state):
                bit.replace(letter, dim_to_match=1)
        bin_coins = CoinsOnBoard(small_board, coin_config={"numeric_labels": True})
        bin_coins[1].flip()
        bin_coins.move_to(coins)

        coins.unlock_shader_data()
        self.play(
            FadeOut(coins, IN),
            FadeIn(bin_coins),
        )
        self.play(
            LaggedStartMap(GrowFromCenter, Group(*bin_states.family_members_with_points())),
            LaggedStartMap(ApplyMethod, Group(*states.family_members_with_points()), lambda m: (m.scale, 0)),
        )
        self.wait()

        # Add labels
        c_labels = VGroup(*[
            TexMobject(name)
            for name in self.coin_names
        ])
        arrow_kw = {
            "tip_config": {
                "width": 0.2,
                "length": 0.2,
            },
            "buff": 0.1,
            "color": GREY_B,
        }
        # s_label_arrows = VGroup()
        # for high_square, low_square, label in zip(*small_boards, s_labels):
        #     label.move_to(Group(high_square, low_square))
        #     label.arrows = VGroup(
        #         Arrow(label.get_bottom(), low_square.get_top(), **arrow_kw),
        #         Arrow(label.get_top(), high_square.get_bottom(), **arrow_kw),
        #     )
        #     s_label_arrows.add(*label.arrows)

        #     self.play(
        #         FadeIn(label),
        #         *map(GrowArrow, label.arrows)
        #     )

        c_label_arrows = VGroup()
        for label, coin in zip(c_labels, bin_coins):
            label.next_to(coin, UP, LARGE_BUFF)
            arrow = Arrow(label.get_bottom(), coin.get_top(), **arrow_kw)
            c_label_arrows.add(arrow)

            self.play(
                FadeIn(label),
                GrowArrow(arrow)
            )
        self.wait()

        # Coin 1 communicates location
        bit1_rect = SurroundingRectangle(
            VGroup(
                bin_states[0][1],
                bin_states[-1][1],
            ),
            buff=SMALL_BUFF,
        )
        coin1_rect = SurroundingRectangle(
            Group(c_labels[1], bin_coins[1]),
            buff=SMALL_BUFF,
        )
        for rect in bit1_rect, coin1_rect:
            rect.insert_n_curves(100)
            nd = int(12 * get_norm(rect.get_area_vector()))
            rect.become(DashedVMobject(rect, num_dashes=nd))
            rect.set_stroke(WHITE, 2)

        kw = {
            "stroke_width": 2,
            "stroke_color": YELLOW,
            "buff": 0.05,
        }
        zero_rects, one_rects = [
            VGroup(
                SurroundingRectangle(bin_states[0][1], **kw),
                SurroundingRectangle(bin_states[1][1], **kw),
            ),
            VGroup(
                SurroundingRectangle(bin_states[2][1], **kw),
                SurroundingRectangle(bin_states[3][1], **kw),
            ),
        ]

        self.play(
            ShowCreation(bit1_rect),
            ShowCreation(coin1_rect),
            FadeOut(state_rect),
        )
        self.wait()
        self.play(board_rects[0].stretch, 0.5, 0, {"about_edge": LEFT})
        self.play(ShowCreation(zero_rects))
        self.wait()
        self.play(
            FadeOut(board_rects[0]),
            FadeOut(zero_rects),
            FadeIn(board_rects[1])
        )
        self.play(
            board_rects[1].stretch, 0.5, 0, {"about_edge": RIGHT}
        )
        self.play(
            FlipCoin(bin_coins[1]),
            arrows[1].match_style, arrows[0],
            arrows[3].match_style, arrows[1],
        )
        self.play(ShowCreation(one_rects[1]))
        self.wait()

        # Talk about null bit
        null_word = TextMobject("Null bit")
        null_word.next_to(bin_coins[0], DOWN, buff=1.5, aligned_edge=LEFT)
        null_arrow = Arrow(null_word.get_top(), bin_coins[0].get_bottom())

        self.play(
            Write(null_word),
            GrowArrow(null_arrow)
        )
        self.wait()

        for i in (0, 1, 0):
            self.play(
                FlipCoin(bin_coins[0]),
                arrows[3 - i].match_style, arrows[0],
                arrows[2 + i].match_style, arrows[3 - i],
                FadeOut(one_rects[1 - i]),
                FadeIn(one_rects[i]),
            )
            self.wait()

        # Written mathematically
        frame.generate_target()
        frame.target.set_height(10, about_edge=DOWN)
        rule_words = TextMobject("Rule: Just look at coin 1")
        rule_words.set_height(0.6)
        rule_words.next_to(frame.target.get_corner(UL), DR, buff=0.5)
        rule_arrow = Vector(1.5 * RIGHT)
        rule_arrow.next_to(rule_words, RIGHT)
        rule_arrow.set_color(BLUE)
        rule_equation = TexMobject("S", "=", self.coin_names[1])
        rule_equation_long = TexMobject(
            "S", "=", "0", "\\cdot",
            self.coin_names[0], "+", "1", "\\cdot",
            self.coin_names[1],
        )

        for equation in rule_equation, rule_equation_long:
            equation.set_color_by_tex("S", YELLOW)
            equation.set_height(0.7)
            equation.next_to(rule_arrow, RIGHT)

        s_labels = VGroup(
            TexMobject("S", "= 0"),
            TexMobject("S", "= 1"),
        )
        for label, board in zip(s_labels, small_boards):
            label.set_height(0.5)
            label.next_to(board, UP)
            label.set_color_by_tex("S", YELLOW)

        self.play(
            MoveToTarget(frame),
            FadeIn(rule_words, 2 * DOWN)
        )
        self.wait()
        for label in s_labels:
            self.play(Write(label))
        self.wait()
        self.play(
            GrowArrow(rule_arrow),
            FadeIn(rule_equation, LEFT),
        )
        self.wait()
        mid_equation = rule_equation_long[2:-1]
        mid_equation.save_state()
        mid_equation.scale(0, about_edge=LEFT)
        self.play(
            Transform(rule_equation[:2], rule_equation_long[:2]),
            Transform(rule_equation[2], rule_equation_long[-1]),
            Restore(mid_equation),
        )
        self.wait()


class TwoSquaresAB(TwoSquareCase):
    CONFIG = {
        "coin_names": ["a", "b"]
    }


class IGotThis(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Pssh, I got this",
            target_mode="tease",
            look_at_arg=self.screen,
            added_anims=[self.teacher.change, "happy", self.screen],
            run_time=2,
        )
        self.change_student_modes(
            "thinking", "pondering",
            look_at_arg=self.screen
        )
        self.wait(6)


class WalkingTheSquare(ThreeDScene):
    def construct(self):
        # Setup objects
        plane = NumberPlane(
            x_range=(-2, 2, 1),
            y_range=(-2, 2, 1),
            height=15,
            width=15,
            faded_line_ratio=3,
            axis_config={"include_tip": False}
        )
        plane.move_to(1.5 * DOWN)
        plane.add_coordinate_labels()
        plane.x_axis.add_numbers([0])

        board = Chessboard(shape=(1, 2))
        board.set_height(1.5)
        board.move_to(plane.c2p(-0.75, 0.75))
        coins = CoinsOnBoard(
            board,
            coin_config={"numeric_labels": True}
        )
        coins.flip(RIGHT)

        coords = [(0, 0), (0, 1), (1, 0), (1, 1)]
        coord_labels = VGroup()
        dots = VGroup()
        for x, y in coords:
            label = TexMobject(f"({x}, {y})")
            point = plane.c2p(x, y)
            label.next_to(point, UR, buff=0.25)
            dot = Dot(point, radius=0.075)
            dot.set_color(GREY)
            dots.add(dot)
            coord_labels.add(label)

        active_dot = Dot(radius=0.15, color=YELLOW)
        active_dot.move_to(plane.c2p(0, 0))

        # Walk around square
        self.play(Write(plane))
        self.play(
            FadeIn(board),
            FadeIn(coins),
            FadeIn(active_dot),
            FadeIn(coord_labels[0]),
        )
        edges = VGroup()
        for i, j, c in [(0, 1, 1), (1, 3, 0), (3, 2, 1), (2, 0, 0)]:
            edge = Line(plane.c2p(*coords[i]), plane.c2p(*coords[j]))
            edge.set_stroke(PINK, 3)
            edges.add(edge)

            anims = [
                FlipCoin(coins[c]),
                ShowCreation(edge),
                ApplyMethod(active_dot.move_to, dots[j])
            ]
            if j != 0:
                anims += [
                    FadeInFromPoint(coord_labels[j], coord_labels[i].get_center()),
                ]
            self.add(edge, dots[i], active_dot)
            self.play(*anims)
        self.add(edges, dots, active_dot)
        self.wait()

        # Show a few more flips
        self.play(
            FlipCoin(coins[0]),
            active_dot.move_to, dots[2],
        )
        self.play(
            FlipCoin(coins[1]),
            active_dot.move_to, dots[3],
        )
        self.play(
            FlipCoin(coins[1]),
            active_dot.move_to, dots[2],
        )
        self.wait()

        # Circles illustrating scheme
        low_rect = SurroundingRectangle(
            VGroup(edges[3], coord_labels[0], coord_labels[2], plane.x_axis.numbers[-1]),
            buff=0.25,
        )
        low_rect.round_corners()
        low_rect.insert_n_curves(30)
        low_rect.set_stroke(YELLOW, 3)
        high_rect = low_rect.copy()
        high_rect.shift(dots[1].get_center() - dots[0].get_center())

        key = Key()
        key.set_color(YELLOW)
        key.set_gloss(0)
        key.match_width(board[0])
        key.next_to(board[0], UP, SMALL_BUFF)

        s_labels = VGroup(
            TexMobject("\\text{Key} = 0").next_to(low_rect, UP, SMALL_BUFF),
            TexMobject("\\text{Key} = 1").next_to(high_rect, UP, SMALL_BUFF),
        )

        self.play(
            ShowCreation(low_rect),
        )
        self.play(
            FadeIn(key, DOWN),
            FadeIn(s_labels[0], DOWN),
        )
        self.play(
            FlipCoin(coins[0]),
            active_dot.move_to, dots[0],
        )
        self.wait(0.5)
        self.play(
            FlipCoin(coins[0]),
            active_dot.move_to, dots[2],
        )
        self.wait()
        self.play(
            TransformFromCopy(low_rect, high_rect),
            FadeIn(s_labels[1], DOWN),
            low_rect.set_stroke, GREY, 1,
            FlipCoin(coins[1]),
            active_dot.move_to, dots[3],
            key.match_x, board[1],
        )
        self.wait()
        self.play(
            FlipCoin(coins[0]),
            active_dot.move_to, dots[1],
        )
        self.wait()
        self.play(
            FlipCoin(coins[1]),
            active_dot.move_to, dots[0],
            key.match_x, board[0],
            high_rect.match_style, low_rect,
            low_rect.match_style, high_rect,
        )
        self.wait()


class ThreeSquareCase(ThreeDScene):
    CONFIG = {
        "coin_names": ["c_0", "c_1", "c_2"]
    }

    def construct(self):
        # Show sequence of boards
        boards = Group(
            Chessboard(shape=(1, 2), height=0.25 * 1),
            Chessboard(shape=(1, 3), height=0.25 * 1),
            Chessboard(shape=(2, 2), height=0.25 * 2),
            Chessboard(shape=(8, 8), height=0.25 * 8),
        )
        dots = TexMobject("\\dots")
        group = Group(*boards[:3], dots, boards[3])

        group.arrange(RIGHT)
        group.set_width(FRAME_WIDTH - 1)

        board_groups = Group()
        for board in boards:
            board.coins = CoinsOnBoard(board, coin_config={"numeric_labels": True})
            board_groups.add(Group(board, board.coins))
        boards[0].coins.flip_at_random()
        boards[1].coins.flip_by_bools([False, True, False])
        boards[2].coins.flip_at_random()
        boards[3].coins.flip_by_message("3 Fails!")

        def get_board_transform(i, bgs=board_groups):
            return TransformFromCopy(
                bgs[i], bgs[i + 1],
                path_arc=PI / 2,
                run_time=2,
            )

        frame = self.camera.frame
        frame.save_state()
        frame.scale(0.5)
        frame.move_to(boards[:2])

        self.add(board_groups[0])
        self.play(get_board_transform(0))
        turn_animation_into_updater(Restore(frame, run_time=4))
        self.add(frame)
        self.play(get_board_transform(1))
        self.play(
            Write(dots),
            get_board_transform(2),
        )
        self.wait()

        # Isolate 3 square board
        board_group = board_groups[1]
        board = boards[1]
        coins = board.coins

        title = TextMobject("Three square case")
        title.set_height(0.7)
        title.to_edge(UP)

        board_group.generate_target()
        board_group.target.set_width(4)
        board_group.target.move_to(DOWN, OUT)

        self.save_state()
        self.play(
            MoveToTarget(board_group, rate_func=squish_rate_func(smooth, 0.5, 1)),
            Write(title),
            LaggedStartMap(FadeOut, Group(
                board_groups[0],
                board_groups[2],
                dots,
                board_groups[3],
            ), lambda m: (m, DOWN)),
            run_time=2,
        )
        self.wait()

        # Try 0*c0 + 1*c1 + 2*c2
        s_sum = TexMobject(
            "0", "\\cdot", self.coin_names[0], "+",
            "1", "\\cdot", self.coin_names[1], "+",
            "2", "\\cdot", self.coin_names[2],
        )
        s_sum.set_height(0.6)
        c_sum = s_sum.copy()
        s_sum.center().to_edge(UP)
        c_sum.next_to(s_sum, DOWN, LARGE_BUFF)

        coin_copies = Group()
        for i in range(3):
            part = c_sum.get_part_by_tex(self.coin_names[i], substring=False)
            coin_copy = coins[i].copy()
            coin_copy.set_height(1.2 * c_sum[0].get_height())
            coin_copy.move_to(part)
            coin_copy.align_to(c_sum, UP)
            part.set_opacity(0)
            coin_copies.add(coin_copy)

        self.play(
            FadeOut(title),
            FadeIn(s_sum[:3]),
            FadeIn(c_sum[:2]),
        )
        self.play(TransformFromCopy(coins[0], coin_copies[0]))
        self.wait()
        self.play(
            FadeIn(s_sum[3:7]),
            FadeIn(c_sum[3:6]),
        )
        self.play(TransformFromCopy(coins[1], coin_copies[1]))
        self.wait()
        self.play(
            FadeIn(s_sum[7:11]),
            FadeIn(c_sum[7:10]),
        )
        self.play(TransformFromCopy(coins[2], coin_copies[2]))
        self.wait()
        self.add(s_sum, c_sum, coin_copies)

        rhs = VGroup(TexMobject("="), Integer(1))
        rhs.arrange(RIGHT)
        rhs[1].set_color(YELLOW)
        rhs.match_height(c_sum[0])
        rhs.next_to(c_sum, RIGHT, aligned_edge=UP)
        braces = VGroup(
            Brace(c_sum[0:3], DOWN),
            Brace(c_sum[0:7], DOWN),
            Brace(c_sum[0:11], DOWN),
        )
        for brace, n in zip(braces, [0, 1, 1]):
            brace.add(brace.get_tex(n))
            brace.unlock_triangulation()
        self.play(GrowFromCenter(braces[0]))
        self.wait()
        self.play(ReplacementTransform(braces[0], braces[1]))
        self.wait()
        self.play(ReplacementTransform(braces[1], braces[2]))
        self.play(
            TransformFromCopy(braces[2][-1], rhs[1], path_arc=-PI / 2),
            Write(rhs[0]),
        )
        self.play(FadeOut(braces[2]))
        self.wait()

        # Show values of S
        s_labels = VGroup(*[
            TexMobject(f"K = {n}")
            for n in range(3)
        ])
        for label, square in zip(s_labels, board):
            label.next_to(square, UP)
            label.set_width(0.8 * square.get_width())
            label.set_color(YELLOW)

        key = Key(depth_test=False)
        key.set_stroke(BLACK, 3, background=True)
        key.set_width(0.8 * board[0].get_width())
        key.move_to(board[0])

        self.play(
            coins.next_to, board, DOWN,
            coins.match_z, coins,
            board.set_opacity, 0.75,
            FadeIn(key),
            FadeIn(s_labels[0])
        )
        self.wait(0.5)
        for i in (1, 2):
            self.play(
                ApplyMethod(key.move_to, board[i], path_arc=-45 * DEGREES),
                s_labels[i - 1].set_fill, GREY, 0.25,
                FadeIn(s_labels[i]),
            )
            self.wait(0.5)

        # Mod 3 label
        mod3_label = TextMobject("(mod 3)")
        mod3_label.match_height(s_sum)
        mod3_label.set_color(BLUE)
        mod3_label.next_to(s_sum, RIGHT, buff=0.75)

        rhs_rhs = TexMobject("\\equiv 0")
        rhs_rhs.match_height(rhs)
        rhs_rhs.next_to(rhs, RIGHT)

        self.play(Write(mod3_label))
        self.wait()
        rhs[1].unlock_triangulation()
        self.play(
            FlipCoin(coins[2]),
            FlipCoin(coin_copies[2]),
            rhs[1].set_value, 3,
        )
        self.wait()
        self.play(Write(rhs_rhs))
        self.wait()
        self.play(
            rhs[1].set_value, 0,
            FadeOut(rhs_rhs)
        )

        # Show a few flips
        for i in [2, 1, 0, 2, 1, 2, 0]:
            bools = coins.get_bools()
            bools[i] = not bools[i]
            new_sum = sum([n * b for n, b in enumerate(bools)]) % 3
            self.play(
                FlipCoin(coins[i]),
                FlipCoin(coin_copies[i]),
                rhs[1].set_value, new_sum,
            )
            self.wait()

        # Show general sum
        general_sum = TexMobject(r"\sum ^{63}_{n=0}n\cdot c_n")
        mod_64 = TextMobject("(mod 64)")
        mod_64.next_to(general_sum, DOWN)
        general_sum.add(mod_64)
        general_sum.to_corner(UL)

        self.play(FadeIn(general_sum))
        self.wait()
        self.play(FadeOut(general_sum))

        # Walk through 010 example
        self.play(
            s_labels[2].set_fill, GREY, 0.25,
            s_labels[0].set_fill, YELLOW, 1,
            ApplyMethod(key.move_to, board[0], path_arc=30 * DEGREES)
        )
        self.wait()
        self.play(
            FlipCoin(coins[1]),
            FlipCoin(coin_copies[1]),
            rhs[1].set_value, 0,
        )
        self.wait()
        square = Square()
        square.set_stroke(YELLOW, 3)
        square.replace(board[0])
        square[0].move_to(board[0], OUT)
        self.play(ShowCreation(square))
        self.wait()
        self.play(FadeOut(square))

        # Walk through alternate flip on 010 example
        self.play(
            FlipCoin(coins[1]),
            FlipCoin(coin_copies[1]),
            rhs[1].set_value, 1,
        )

        morty = Mortimer(height=1.5, mode="hooray")
        morty.to_corner(DR)
        bubble = SpeechBubble(height=2, width=2)
        bubble.pin_to(morty)
        bubble.write("There's another\\\\way!")

        self.play(
            FadeIn(morty),
            ShowCreation(bubble),
            Write(bubble.content, run_time=1),
        )
        self.play(Blink(morty))
        self.play(
            FadeOut(VGroup(morty, bubble, bubble.content))
        )

        self.play(
            FlipCoin(coins[2]),
            FlipCoin(coin_copies[2]),
            rhs[1].set_value, 3,
        )
        self.wait()
        self.play(rhs[1].set_value, 0)
        self.wait()


class ThreeSquaresABC(ThreeSquareCase):
    CONFIG = {
        "coin_names": ["a", "b", "c"]
    }


class TreeOfThreeFlips(ThreeDScene):
    def construct(self):
        # Setup sums
        csum = Group(
            TexMobject("0 \\cdot"),
            Coin(numeric_labels=True),
            TexMobject("+\\,1 \\cdot"),
            Coin(numeric_labels=True),
            TexMobject("+\\,2 \\cdot"),
            Coin(numeric_labels=True),
            TexMobject("="),
            Integer(0)
        )
        csum.coins = csum[1:7:2]
        csum.coins.set_height(1.5 * csum[0].get_height())
        csum.coins.flip(RIGHT)
        csum.coins[1].flip(RIGHT)
        csum.arrange(RIGHT, buff=0.1)
        csum[-1].align_to(csum[0], DOWN)
        csum[-1].shift(SMALL_BUFF * RIGHT)
        csum.to_edge(LEFT)

        csum_rect = SurroundingRectangle(csum, buff=SMALL_BUFF)
        csum_rect.set_stroke(WHITE, 1)

        # Set rhs values
        def set_rhs_target(cs, colors=[RED, GREEN, BLUE]):
            bools = [c.is_heads() for c in cs.coins]
            value = sum([n * b for n, b in enumerate(bools)]) % 3
            cs[-1].unlock_triangulation()
            cs[-1].generate_target()
            cs[-1].target.set_value(value)
            cs[-1].target.set_color(colors[value])
            return cs[-1]

        rhs = set_rhs_target(csum)
        rhs.become(rhs.target)

        # Create copies
        new_csums = Group()
        for i in range(3):
            new_csum = csum.deepcopy()
            new_csum.coins = new_csum[1:7:2]
            new_csums.add(new_csum)
        new_csums.arrange(DOWN, buff=1.5)
        new_csums.next_to(csum, RIGHT, buff=3)

        # Arrows
        arrows = VGroup()
        for i, ncs in enumerate(new_csums):
            arrow = Arrow(csum_rect.get_right(), ncs.get_left())
            label = TextMobject(f"Flip coin {i}")
            label.set_height(0.3)
            label.set_fill(GREY_A)
            label.set_stroke(BLACK, 3, background=True)
            label.next_to(ORIGIN, UP, buff=0)
            label.rotate(arrow.get_angle(), about_point=ORIGIN)
            label.shift(arrow.get_center())
            arrow.label = label
            arrows.add(arrow)
        arrows.set_color(GREY)

        # Initial state label
        is_label = TextMobject(
            "Initial state: 010",
            tex_to_color_map={"0": RED_D, "1": GOLD_D}
        )
        is_label.set_height(0.4)
        is_label.next_to(csum_rect, UP, aligned_edge=LEFT)

        # Show three flips
        self.add(csum)
        self.add(csum_rect)
        self.add(is_label)
        self.wait()

        anims = []
        for i, arrow, ncs in zip(it.count(), arrows, new_csums):
            anims += [
                GrowArrow(arrow),
                FadeIn(arrow.label, lag_ratio=0.2),
            ]
        self.play(LaggedStart(*anims))
        for indices in [[0], [1, 2]]:
            self.play(*[
                TransformFromCopy(csum, new_csums[i], path_arc=30 * DEGREES, run_time=2)
                for i in indices
            ])
            self.wait()
            for i in indices:
                ncs = new_csums[i]
                ncs.coins[i].flip()
                rhs = set_rhs_target(ncs)
                ncs.coins[i].flip()
                self.play(
                    FlipCoin(ncs.coins[i]),
                    MoveToTarget(rhs)
                )

        # Put key in square 2
        board = Chessboard(shape=(1, 3), square_resolution=(5, 5))
        board.set_gloss(0.5)
        board.set_width(3)
        board.set_depth(0.25, stretch=True)
        board.space_out_submobjects(factor=1.001)
        board.next_to(ORIGIN, LEFT)
        board.to_edge(UP)
        board.shift(IN)
        board.rotate(60 * DEGREES, LEFT)
        opening_square = board[2][0]
        opening_square_top = opening_square.get_corner(UP + IN)

        key = Key()
        key.to_corner(UL, buff=LARGE_BUFF)
        key.shift(OUT)
        key.generate_target()
        key.target.scale(0.3)
        key.target.rotate(60 * DEGREES, LEFT)
        key.target.move_to(board[2][0])

        self.play(
            FadeIn(board, DOWN),
            FadeIn(key)
        )
        self.play(
            MoveToTarget(key, path_arc=30 * DEGREES),
            Rotate(opening_square, 90 * DEGREES, LEFT, about_point=opening_square_top),
        )
        self.play(
            Rotate(opening_square, 90 * DEGREES, RIGHT, about_point=opening_square_top),
            key.next_to, board[1], RIGHT, buff=0.01,
        )
        self.wait()
        self.remove(key)
        self.play(Rotate(board, 0 * DEGREES, RIGHT, run_time=0))
        self.play(Rotate(board, 60 * DEGREES, RIGHT))

        # Put coins on
        coins = csum.coins.copy()
        for coin, cube in zip(coins, board):
            coin.generate_target()
            coin.target.next_to(cube, OUT, buff=0)
        self.play(LaggedStartMap(MoveToTarget, coins, run_time=2))
        self.wait()


class SeventyFivePercentChance(Scene):
    def construct(self):
        # Setup column
        rows = []
        n_shown = 5
        coins = Group()
        nums = VGroup()
        for n in it.chain(range(n_shown), range(64 - n_shown, 64)):
            coin = Coin(numeric_labels=True)
            coin.set_height(0.7)
            if (random.random() < 0.5 or (n == 2)) and (n != 62):
                coin.flip()
            num = Integer(n)
            row = Group(
                coin,
                TexMobject("\\cdot"),
                num,
                TexMobject("+"),
            )
            VGroup(*row[1:]).set_stroke(BLACK, 3, background=True)
            row.arrange(RIGHT, buff=MED_SMALL_BUFF)
            rows.append(row)
            coins.add(coin)
            nums.add(num)

        vdots = TexMobject("\\vdots")
        rows = Group(*rows[:n_shown], vdots, *rows[n_shown:])
        rows.arrange(DOWN, buff=MED_SMALL_BUFF, aligned_edge=LEFT)
        vdots.match_x(rows[0][2])
        rows.set_height(7)
        rows.to_edge(RIGHT)
        rows[-1][-1].set_opacity(0)

        nums = VGroup(*nums[:n_shown], vdots, *nums[n_shown:])
        self.play(Write(nums))
        self.wait()
        self.play(
            LaggedStartMap(FadeIn, rows, lag_ratio=0.1, run_time=3),
            Animation(nums.copy(), remover=True),
        )
        self.wait()

        # Show desired sums
        brace = Brace(rows, LEFT)
        b_label = brace.get_text("Sum mod 64")
        sum_label = TextMobject("=\\, 53 (say)")
        sum_label.next_to(b_label, DOWN)
        want_label = TextMobject("Need to encode 55 (say)")
        want_label.next_to(sum_label, DOWN, buff=0.25, aligned_edge=RIGHT)
        want_label.set_color(YELLOW)
        need_label = TextMobject("Must add 2")
        need_label.next_to(want_label, DOWN, buff=0.25)
        need_label.set_color(BLUE)

        for label in b_label, sum_label, want_label, need_label:
            label.set_stroke(BLACK, 7, background=True)

        self.play(
            GrowFromCenter(brace),
            FadeIn(b_label, RIGHT)
        )
        self.wait(2)
        self.play(FadeIn(sum_label, 0.25 * UP))
        self.wait(2)
        self.play(LaggedStart(
            FadeIn(want_label, UP),
            FadeIn(need_label, UP),
            lag_ratio=0.3
        ))
        self.wait()

        # Show attempts
        s_rect = SurroundingRectangle(rows[2])

        self.play(ShowCreation(s_rect))
        self.wait()
        self.play(FlipCoin(rows[2][0]))
        self.wait(2)

        self.play(
            s_rect.move_to, rows[-2],
            s_rect.stretch, 1.1, 0,
        )
        self.wait()
        self.play(FlipCoin(rows[-2][0]))
        self.wait()


class ModNStrategy(ThreeDScene):
    def construct(self):
        # Board
        n_shown = 5
        board = Chessboard()
        coins = CoinsOnBoard(board, coin_config={"numeric_labels": True})
        coins.flip_by_message(r"75% odds")

        nums = VGroup()
        for n, square in enumerate(board):
            num = Integer(n)
            num.set_height(0.4 * square.get_height())
            num.next_to(square, OUT, buff=0)
            nums.add(num)
        nums.set_stroke(BLACK, 3, background=True)

        coins.generate_target()
        for coin in coins.target:
            coin.set_opacity(0.2)
            coin[-2:].set_opacity(0)

        self.add(board)
        self.add(coins)
        self.wait()
        self.play(
            MoveToTarget(coins),
            FadeIn(nums, lag_ratio=0.1)
        )
        self.wait()

        # # Compress
        # square_groups = Group(*[
        #     Group(square, coin, num)
        #     for square, coin, num in zip(board, coins, nums)
        # ])
        # segments = Group(
        #     square_groups[:n_shown],
        #     square_groups[n_shown:-n_shown],
        #     square_groups[-n_shown:],
        # )
        # segments.generate_target()
        # dots = TexMobject("\\cdots")
        # dots.center()
        # segments.target[0].next_to(dots, LEFT)
        # segments.target[2].next_to(dots, RIGHT)
        # segments.target[1].scale(0)
        # segments.target[1].move_to(dots)

        # self.play(
        #     Write(dots),
        #     MoveToTarget(segments),
        # )
        # self.wait()
        # self.remove(segments[1])

        # # Raise coins
        # coins = Group(*coins[:n_shown], *coins[-n_shown:])
        # nums = VGroup(*nums[:n_shown], *nums[-n_shown:])
        # board = Group(*board[:n_shown], *board[-n_shown:])
        # coins.unlock_shader_data()
        # self.play(
        #     coins.shift, UP,
        #     coins.set_opacity, 1,
        # )

        # Setup sum
        mid_coins = coins[n_shown:-n_shown]
        mid_nums = nums[n_shown:-n_shown]
        coins = Group(*coins[:n_shown], *coins[-n_shown:])
        nums = VGroup(*nums[:n_shown], *nums[-n_shown:])
        nums.generate_target()
        coins.generate_target()
        coins.target.set_opacity(1)

        full_sum = Group()
        to_fade_in = VGroup()
        for num, coin in zip(nums.target, coins.target):
            coin.set_height(0.7)
            num.set_height(0.5)
            summand = Group(
                coin,
                TexMobject("\\cdot"),
                num,
                TexMobject("+"),
            )
            to_fade_in.add(summand[1], summand[3])
            VGroup(*summand[1:]).set_stroke(BLACK, 3, background=True)
            summand.arrange(RIGHT, buff=MED_SMALL_BUFF)

            full_sum.add(summand)

        dots = TexMobject("\\dots")
        full_sum = Group(*full_sum[:n_shown], dots, *full_sum[n_shown:])
        full_sum.arrange(RIGHT, buff=MED_SMALL_BUFF)
        full_sum.set_width(FRAME_WIDTH - 1)
        full_sum[-1][-1].scale(0, about_edge=LEFT)
        full_sum.move_to(UP)

        brace = Brace(full_sum, DOWN)
        s_label = VGroup(
            TextMobject("Sum (mod 64) = "),
            Integer(53),
        )
        s_label[1].set_color(BLUE)
        s_label[1].match_height(s_label[0][0][0])
        s_label.arrange(RIGHT)
        s_label[1].align_to(s_label[0][0][0], DOWN)
        s_label.next_to(brace, DOWN)

        words = TextMobject("Can't know if a flip will add or subtract")
        words.to_edge(UP)

        for mob in mid_coins, mid_nums:
            mob.generate_target()
            mob.target.move_to(dots)
            mob.target.scale(0)
            mob.target.set_opacity(0)

        self.play(
            FadeOut(board, IN),
            MoveToTarget(mid_coins, remover=True),
            MoveToTarget(mid_nums, remover=True),
            MoveToTarget(nums),
            MoveToTarget(coins),
            Write(dots),
            FadeIn(to_fade_in, lag_ratio=0.1),
            run_time=2
        )
        self.play(
            GrowFromCenter(brace),
            FadeIn(s_label, 0.25 * UP)
        )
        self.wait()

        self.play(Write(words, run_time=1))
        self.wait()

        # Do some flips
        s_label[1].add_updater(lambda m: m.set_value(m.get_value() % 64))
        for x in range(10):
            n = random.randint(-n_shown, n_shown - 1)
            coin = coins[n]
            n = n % 64
            diff_label = Integer(n, include_sign=True)
            if not coin.is_heads():
                diff_label.set_color(GREEN)
            else:
                diff_label.set_color(RED)
                diff_label.set_value(-diff_label.get_value())
            diff_label.next_to(coin, UP, aligned_edge=LEFT)
            self.play(
                ChangeDecimalToValue(
                    s_label[1],
                    s_label[1].get_value() + n,
                    rate_func=squish_rate_func(smooth, 0.5, 1)
                ),
                FlipCoin(coin),
                FadeIn(diff_label, 0.5 * DOWN)
            )
            self.play(FadeOut(diff_label))
            self.wait()


class ShowCube(ThreeDScene):
    def construct(self):
        # Camera stuffs
        frame = self.camera.frame
        light = self.camera.light_source
        light.move_to([-10, -10, 20])

        # Plane and axes
        plane = NumberPlane(
            x_range=(-2, 2, 1),
            y_range=(-2, 2, 1),
            height=15,
            width=15,
            faded_line_ratio=3,
            axis_config={"include_tip": False}
        )
        plane.add_coordinate_labels()
        plane.coordinate_labels.set_stroke(width=0)
        axes = ThreeDAxes(
            x_range=(-2, 2, 1),
            y_range=(-2, 2, 1),
            z_range=(-2, 2, 1),
            height=15,
            width=15,
            depth=15,
        )
        axes.apply_depth_test()

        # Vertices and edges
        vert_coords = [
            (n % 2, (n // 2) % 2, (n // 4) % 2)
            for n in range(8)
        ]
        verts = []
        coord_labels = VGroup()
        coord_labels_2d = VGroup()
        for coords in vert_coords:
            vert = axes.c2p(*coords)
            verts.append(vert)
            x, y, z = coords
            label = TexMobject(f"({x}, {y}, {z})")
            label.set_height(0.3)
            label.next_to(vert, UR, SMALL_BUFF)
            label.rotate(89 * DEGREES, RIGHT, about_point=vert)
            coord_labels.add(label)
            if z == 0:
                label_2d = TexMobject(f"({x}, {y})")
                label_2d.set_height(0.3)
                label_2d.next_to(vert, UR, SMALL_BUFF)
                coord_labels_2d.add(label_2d)

        edge_indices = [
            (0, 1), (0, 2), (1, 3), (2, 3),
            (0, 4), (1, 5), (2, 6), (3, 7),
            (4, 5), (4, 6), (5, 7), (6, 7),
        ]

        # Vertex and edge drawings
        spheres = SGroup()
        for vert in verts:
            sphere = Sphere(
                radius=0.1,
                resolution=(9, 9),
            )
            sphere.set_gloss(0.3)
            sphere.set_color(GREY)
            sphere.move_to(vert)
            spheres.add(sphere)

        edges = SGroup()
        for i, j in edge_indices:
            edge = Line3D(
                verts[i], verts[j],
                resolution=(5, 51),
                width=0.04,
                gloss=0.5,
            )
            edge.set_color(GREY_BROWN)
            edges.add(edge)

        # Setup highlight animations
        def highlight(n, spheres=spheres, coord_labels=coord_labels):
            anims = []
            for k, sphere, cl in zip(it.count(), spheres, coord_labels):
                if k == n:
                    sphere.save_state()
                    cl.save_state()
                    sphere.generate_target()
                    cl.generate_target()
                    cl.target.set_fill(YELLOW)
                    sphere.target.set_color(YELLOW)
                    Group(cl.target, sphere.target).scale(1.5, about_point=sphere.get_center())
                    anims += [
                        MoveToTarget(sphere),
                        MoveToTarget(cl),
                    ]
                elif sphere.get_color() == Color(YELLOW):
                    anims += [
                        Restore(sphere),
                        Restore(cl),
                    ]
            return AnimationGroup(*anims)

        # Setup 2d case
        frame.move_to(1.5 * UP)
        self.add(plane)
        self.play(
            LaggedStartMap(FadeIn, coord_labels_2d),
            LaggedStartMap(GrowFromCenter, spheres[:4]),
            LaggedStartMap(GrowFromCenter, edges[:4]),
        )
        self.wait()

        # Transition to 3d case
        frame.generate_target()
        frame.target.set_rotation(-25 * DEGREES, 70 * DEGREES)
        frame.target.move_to([1, 2, 0])
        frame.target.set_height(10)
        to_grow = Group(*edges[4:], *spheres[4:], *coord_labels[4:])
        to_grow.save_state()
        to_grow.set_depth(0, about_edge=IN, stretch=True)

        rf = squish_rate_func(smooth, 0.5, 1)
        self.play(
            MoveToTarget(frame),
            ShowCreation(axes.z_axis),
            Restore(to_grow, rate_func=rf),
            FadeOut(coord_labels_2d, rate_func=rf),
            *[
                FadeInFromPoint(cl, cl2.get_center(), rate_func=squish_rate_func(smooth, 0.5, 1))
                for cl, cl2 in zip(coord_labels[:4], coord_labels_2d)
            ],
            run_time=3
        )

        frame.start_time = self.time
        frame.scene = self
        frame.add_updater(lambda m: m.set_theta(
            -25 * DEGREES * math.cos((m.scene.time - m.start_time) * PI / 60)
        ))

        self.add(axes.z_axis)
        self.add(edges)
        self.add(spheres)

        self.play(
            LaggedStart(*[Indicate(s, color=GREEN) for s in spheres], run_time=2, lag_ratio=0.1),
            LaggedStart(*[Indicate(c, color=GREEN) for c in coord_labels], run_time=2, lag_ratio=0.1),
        )

        # Add chessboard
        board = Chessboard(
            shape=(1, 3), height=1,
            square_resolution=(5, 5),
        )
        board.move_to(plane.c2p(-1, 0), DOWN + IN)
        coins = CoinsOnBoard(board, coin_config={"numeric_labels": True})

        self.play(
            FadeIn(board),
            FadeIn(coins),
            highlight(7)
        )

        # Walk along a few edges
        for ci in [1, 2, 0, 1, 2, 1, 0, 1]:
            coin = coins[ci]
            curr_n = sum([(2**k) * c.is_heads() for k, c in enumerate(coins)])
            coin.flip()
            new_n = sum([(2**k) * c.is_heads() for k, c in enumerate(coins)])
            coin.flip()
            line = Line(verts[curr_n], verts[new_n])
            line.set_stroke(YELLOW, 3)
            self.play(
                FlipCoin(coin),
                highlight(new_n),
                ShowCreationThenDestruction(line)
            )
            self.wait()

        # Color the corners
        self.play(
            highlight(-1),
            edges.set_color, GREY, 0.5,
        )

        colors = [RED, GREEN, BLUE_D]
        title = TextMobject("Strategy", "\\, $\\Leftrightarrow$ \\,", "Coloring")
        title[2].set_submobject_colors_by_gradient(*colors)
        title.set_stroke(BLACK, 5, background=True)
        title.set_height(0.7)
        title.to_edge(UP)
        title.shift(LEFT)
        title.fix_in_frame()

        color_label_templates = [
            TexMobject(char, color=color).rotate(PI / 2, RIGHT).match_depth(coord_labels[0])
            for char, color in zip("RGB", colors)
        ]
        coord_labels.color_labels = VGroup(*[VMobject() for cl in coord_labels])

        def get_coloring_animation(ns,
                                   spheres=spheres,
                                   coord_labels=coord_labels,
                                   colors=colors,
                                   color_label_templates=color_label_templates,
                                   ):
            anims = []
            new_color_labels = VGroup()
            for n, sphere, coord_label, old_color_label in zip(ns, spheres, coord_labels, coord_labels.color_labels):
                color = colors[int(n)]
                sphere.generate_target()
                coord_label.generate_target()
                sphere.target.set_color(color)
                coord_label.target.set_fill(color)
                color_label = color_label_templates[n].copy()
                color_label.next_to(coord_label, RIGHT, SMALL_BUFF)
                anims += [
                    MoveToTarget(sphere),
                    MoveToTarget(coord_label),
                    FadeIn(color_label, 0.25 * IN),
                    FadeOut(old_color_label, 0.25 * OUT),
                ]
                new_color_labels.add(color_label)
            coord_labels.color_labels = new_color_labels
            return LaggedStart(*anims, run_time=2)

        self.play(
            FadeIn(title, DOWN),
            get_coloring_animation(np.random.randint(0, 3, 8)),
        )
        self.wait()
        for x in range(4):
            self.play(get_coloring_animation(np.random.randint(0, 3, 8)))
            self.wait()

        # Some specific color examples
        S0 = TexMobject("\\text{Key} = 0")
        S0.to_edge(LEFT)
        S0.shift(UP)
        S0.fix_in_frame()
        self.play(
            FadeIn(S0, DOWN),
            get_coloring_animation([0] * 8)
        )
        self.wait(5)

        bit_sum = TexMobject("\\text{Key} = \\,&c_0 + c_1")
        bit_sum.scale(0.8)
        bit_sum.to_edge(LEFT)
        bit_sum.shift(UP)
        bit_sum.fix_in_frame()
        self.play(
            FadeIn(bit_sum, DOWN),
            FadeOut(S0, UP),
            get_coloring_animation([sum(coords[:2]) for coords in vert_coords])
        )
        self.wait(6)

        bit_sum_with_coefs = TexMobject(
            "\\text{Key} = \\,&(0\\cdot c_0 + 1\\cdot c_1 + 2\\cdot c_2) \\\\ &\\quad \\mod 3"
        )
        bit_sum_with_coefs.scale(0.8)
        bit_sum_with_coefs.move_to(bit_sum, LEFT)
        bit_sum_with_coefs.fix_in_frame()
        self.play(
            FadeIn(bit_sum_with_coefs, DOWN),
            FadeOut(bit_sum, UP),
            get_coloring_animation([np.dot(coords, [0, 1, 2]) % 3 for coords in vert_coords])
        )
        self.wait(4)

        # Focus on (0, 0, 0)
        self.play(
            FlipCoin(coins),
            coord_labels[1:].set_opacity, 0.2,
            coord_labels.color_labels[1:].set_opacity, 0.2,
            spheres[1:].set_opacity, 0.2,
        )
        self.wait(2)

        lines = VGroup()
        for n in [1, 2, 4]:
            line = Line(verts[0], verts[n], buff=0.1)
            line.set_stroke(YELLOW, 3)
            coin = coins[int(np.log2(n))]
            self.play(
                ShowCreationThenDestruction(line),
                spheres[n].set_opacity, 1,
                coord_labels[n].set_opacity, 1,
                coord_labels.color_labels[n].set_opacity, 1,
                FlipCoin(coin)
            )
            line.reverse_points()
            self.add(line, coord_labels)
            self.play(
                FlipCoin(coin),
                ShowCreation(line)
            )
            lines.add(line)
        self.wait(10)

        # Focus on (0, 1, 0)
        self.play(
            FlipCoin(coins[1]),
            Uncreate(lines[1]),
            FadeOut(lines[::2]),
            Group(
                spheres[0], coord_labels[0], coord_labels.color_labels[0],
                spheres[1], coord_labels[1], coord_labels.color_labels[1],
                spheres[4], coord_labels[4], coord_labels.color_labels[4],
            ).set_opacity, 0.2,
        )
        self.wait(3)

        lines = VGroup()
        curr_n = 2
        for n in [1, 2, 4]:
            new_n = n ^ curr_n
            line = Line(verts[curr_n], verts[new_n], buff=0.1)
            line.set_stroke(YELLOW, 3)
            coin = coins[int(np.log2(n))]
            self.play(
                ShowCreationThenDestruction(line),
                spheres[new_n].set_opacity, 1,
                coord_labels[new_n].set_opacity, 1,
                coord_labels.color_labels[new_n].set_opacity, 1,
                FlipCoin(coin)
            )
            line.reverse_points()
            self.add(line, coord_labels)
            self.play(
                FlipCoin(coin),
                ShowCreation(line)
            )
            lines.add(line)
        self.wait(10)
        self.play(
            LaggedStartMap(Uncreate, lines),
            spheres.set_opacity, 1,
            coord_labels.set_opacity, 1,
            coord_labels.color_labels.set_opacity, 1,
            FadeOut(bit_sum_with_coefs),
        )
        self.wait()
        for x in range(8):
            self.play(get_coloring_animation(np.random.randint(0, 3, 8)))
            self.wait()

        # Count all strategies
        count = TextMobject("$3^8$ total strategies")
        count64 = TextMobject("$64^{(2^{64})}$ total strategies")
        for words in count, count64:
            words.to_edge(LEFT, buff=MED_SMALL_BUFF)
            words.shift(UP)
            words.fix_in_frame()

        full_board = Chessboard()
        full_board.set_height(6)
        full_board.next_to(axes.c2p(0, 0, 0), np.array([-1, 1, 1]), buff=0)
        full_board.shift(SMALL_BUFF * UP + LEFT)

        full_coins = CoinsOnBoard(full_board, coin_config={"numeric_labels": True})
        full_coins.flip_by_message("64^ 2^64")

        self.play(FadeIn(count, DOWN))
        self.wait(4)
        self.remove(board, coins)
        frame.clear_updaters()
        frame.generate_target()
        frame.target.set_rotation(0, 45 * DEGREES)
        frame.target.shift(2 * UP)
        self.play(
            count.shift, UP,
            count.set_opacity, 0.5,
            ShowIncreasingSubsets(full_board, run_time=4),
            ShowIncreasingSubsets(full_coins, run_time=4),
            FadeIn(count64, DOWN),
            MoveToTarget(frame, run_time=5)
        )

        messages = [
            "Or, use ",
            "Burnside",
            "to count",
            "modulo  ",
            "symmetry",
        ]
        for message in messages:
            bools = string_to_bools(message)
            to_flip = Group()
            for head, coin in zip(bools, full_coins):
                if head ^ coin.is_heads():
                    to_flip.add(coin)
            self.play(
                LaggedStartMap(FlipCoin, to_flip, run_time=1)
            )
            self.wait(0.5)

        frame.generate_target()
        frame.target.shift(2 * DOWN)
        frame.target.set_rotation(-15 * DEGREES, 70 * DEGREES)
        full_coins.unlock_shader_data()
        self.play(
            MoveToTarget(frame, run_time=3),
            LaggedStartMap(FadeOut, full_board),
            LaggedStartMap(FadeOut, full_coins),
            FadeOut(count),
            FadeOut(count64),
        )
        frame.add_updater(lambda m, dt: m.increment_theta(0.01 * dt))
        self.wait(30)


class CubeSupplement(ThreeDScene):
    CONFIG = {
        "try_different_strategies": False,
    }

    def construct(self):
        # Map 8 states to square choices
        boards = Group(*[Chessboard(shape=(1, 3)) for x in range(8)])
        boards.arrange(DOWN, buff=0.5 * boards[0].get_height())
        boards.set_height(7)
        boards.to_edge(LEFT)

        coin_sets = Group(*[
            CoinsOnBoard(board, coin_config={"numeric_labels": True})
            for board in boards
        ])
        vert_coords = [[n // 4, (n // 2) % 2, n % 2] for n in range(7, -1, -1)]
        for coords, coins in zip(vert_coords, coin_sets):
            coins.flip_by_bools(coords)

        def get_choice_boards(values, boards):
            choices = VGroup()
            for value, board in zip(values, boards):
                choice = VGroup(*[Square() for x in range(3)])
                choice.arrange(RIGHT, buff=0)
                choice.match_height(board)
                choice.next_to(board, RIGHT, buff=1.25)
                choice.set_fill(GREY_D, 1)
                choice.set_stroke(WHITE, 1)
                choice[value].set_fill(TEAL)
                choices.add(choice)
            return choices

        colors = [RED, GREEN, BLUE_D]
        color_words = ["Red", "Green", "Blue"]
        s_values = [sum([n * v for n, v in enumerate(cs)]) % 3 for cs in vert_coords]
        choice_boards = get_choice_boards(s_values, boards)
        c_labels = VGroup()
        s_arrows = VGroup()
        for value, board, choice_board in zip(s_values, boards, choice_boards):
            arrow = Vector(RIGHT)
            arrow.next_to(board, RIGHT, SMALL_BUFF)
            c_label = TextMobject(color_words[value], color=colors[value])
            c_label.next_to(choice_board, RIGHT)
            c_labels.add(c_label)
            s_arrows.add(arrow)

            choice_board.generate_target()
            choice_board.target[value].set_fill(colors[value])

        self.play(
            LaggedStartMap(FadeIn, boards, lag_ratio=0.25),
            LaggedStartMap(FadeIn, coin_sets, lag_ratio=0.25),
            run_time=3
        )
        self.play(
            LaggedStartMap(GrowArrow, s_arrows, lag_ratio=0.25),
            LaggedStartMap(FadeIn, choice_boards, lambda m: (m, LEFT), lag_ratio=0.25),
        )
        self.wait()

        # Fork
        if self.try_different_strategies:
            for x in range(5):
                values = list(np.arange(8) % 3)
                random.shuffle(values)
                new_cboards = get_choice_boards(values, boards)
                self.play(
                    LaggedStartMap(FadeOut, choice_boards, lambda m: (m, 0.25 * UP)),
                    LaggedStartMap(FadeIn, new_cboards, lambda m: (m, 0.25 * DOWN)),
                )
                choice_boards = new_cboards
                self.wait(2)

        else:
            # Associate choices with colors
            self.play(
                LaggedStartMap(MoveToTarget, choice_boards),
                LaggedStartMap(FadeIn, c_labels),
            )
            self.wait()


class TryDifferentCaseThreeStrategies(CubeSupplement):
    CONFIG = {
        "try_different_strategies": True,
    }


class CubeEdgeDescription(Scene):
    CONFIG = {
        "camera_config": {"background_color": GREY_E}
    }

    def construct(self):
        bits = VGroup(*[
            VGroup(*[
                Integer(int(b))
                for b in string_to_bools(char)
            ]).arrange(RIGHT, buff=SMALL_BUFF)
            for char in "hi"
        ])
        bits.arrange(DOWN, buff=LARGE_BUFF)
        arrow = Arrow(
            bits[0][7].get_bottom(),
            bits[1][7].get_top(),
            buff=SMALL_BUFF,
            tip_config={"length": 0.15, "width": 0.15}
        )
        arrow.set_color(BLUE)
        words = TextMobject("Bit flip")
        words.set_color(BLUE)
        words.next_to(arrow, LEFT)
        bf_group = VGroup(bits, arrow, words)
        parens = TexMobject("()")[0]
        parens.scale(2)
        parens.match_height(bf_group, stretch=True)
        parens[0].next_to(bf_group, LEFT, SMALL_BUFF)
        parens[1].next_to(bf_group, RIGHT, SMALL_BUFF)
        bf_group.add(parens)
        bf_group.to_edge(UP)

        cube_words = TextMobject("Edge of an\\\\n-dimensional cube")
        top_group = VGroup(
            bf_group,
            Vector(RIGHT),
            cube_words
        )
        top_group.arrange(RIGHT)
        top_group.to_edge(UP)

        self.add(bf_group)
        bits.unlock_triangulation()
        self.play(
            TransformFromCopy(*bits),
            GrowArrow(arrow),
            FadeIn(words, 0.25 * UP)
        )
        self.wait()
        self.play(
            GrowArrow(top_group[1]),
            FadeIn(cube_words, LEFT)
        )
        self.wait()


class EdgeColoringExample(Scene):
    def construct(self):
        words = VGroup(
            TextMobject(
                "Color edges\\\\red or blue",
                tex_to_color_map={"red": RED, "blue": BLUE}
            ),
            TextMobject("Prove there is a\\\\monochromatic triangle", alignment=""),
        )
        words.arrange(DOWN, buff=LARGE_BUFF, aligned_edge=LEFT)
        words.to_edge(RIGHT)
        words.to_edge(UP, buff=LARGE_BUFF)

        def get_graph(words=words):
            points = compass_directions(6)
            points *= 3
            verts = VGroup(*[Dot(p, radius=0.1) for p in points])
            verts.set_fill(GREY_B, 1)
            edges = VGroup(*[
                Line(p1, p2, color=random.choice([RED, BLUE]))
                for p1, p2 in it.combinations(points, 2)
            ])
            graph = VGroup(verts, edges)
            graph.set_height(6)
            graph.next_to(words, LEFT, LARGE_BUFF)
            graph.set_y(0)
            graph.set_stroke(background=True)
            return graph

        graph = get_graph()

        self.add(words)
        self.add(graph)
        self.wait()
        for x in range(2):
            new_graph = get_graph()
            self.play(
                ShowCreation(
                    new_graph, lag_ratio=0.1,
                    run_time=3,
                ),
                ApplyMethod(
                    graph[1].set_stroke, None, 0,
                    run_time=2,
                )
            )
            graph = new_graph
        self.wait(4)


class GrahamsConstant(Scene):
    def construct(self):
        lhs = TexMobject("g_{64}", "=")
        lhs[0][1:].scale(0.7, about_edge=DL)
        lhs.scale(2)

        rhs = VGroup()
        for ndots in [1, 3, 6, 7, 9, 12]:
            row = VGroup(*[
                TexMobject("3"),
                TexMobject("\\uparrow\\uparrow"),
                VGroup(*[
                    TexMobject("\\cdot") for x in range(ndots)
                ]).arrange(RIGHT, buff=0.2),
                TexMobject("\\uparrow\\uparrow"),
                TexMobject("3"),
            ])
            row.arrange(RIGHT, buff=MED_SMALL_BUFF)
            if ndots == 1:
                rc = row.get_center()
                row[:2].move_to(rc, RIGHT)
                row[2].set_opacity(0)
                row[3:].move_to(rc, LEFT)
            row.add(Brace(row[1:-1], DOWN, buff=SMALL_BUFF))
            rhs.add(row)
        rhs[0][-1].set_opacity(0)
        rhs.replace_submobject(3, TexMobject("\\vdots"))
        rhs.arrange(UP)
        rhs.next_to(lhs, RIGHT)

        rbrace = Brace(rhs, RIGHT)
        rbrace_tex = rbrace.get_text("64 times")

        equation = VGroup(lhs, rhs, rbrace, rbrace_tex)
        equation.center().to_edge(LEFT, buff=LARGE_BUFF)

        self.add(lhs, rhs[0])
        self.play(TransformFromCopy(rhs[0], rhs[1]),)
        self.play(TransformFromCopy(rhs[1], rhs[2]))
        self.play(
            Write(rhs[3]),
            TransformFromCopy(rhs[2], rhs[4]),
        )
        self.play(
            TransformFromCopy(rhs[4], rhs[5]),
            GrowFromCenter(rbrace),
            Write(rbrace_tex)
        )
        self.wait()


class ThinkAboutNewTrick(PiCreatureScene, ThreeDScene):
    def construct(self):
        randy = self.pi_creature

        board = Chessboard(shape=(1, 3))
        board.set_height(1.5)
        coins = CoinsOnBoard(board)
        coins.flip_at_random()

        self.add(board, coins)
        self.play(randy.change, "confused", board)

        for x in range(4):
            self.play(FlipCoin(random.choice(coins)))
            if x == 1:
                self.play(randy.change, "maybe")
            else:
                self.wait()


class AttemptAColoring(ThreeDScene):
    def construct(self):
        # Setup cube
        short_vert_height = 0.3
        tall_vert_height = 0.4

        vert_coords = np.array(list(map(int_to_bit_coords, range(8))))
        vert_coords = vert_coords - 0.5
        vert_coords = vert_coords * 4
        vert_coords[:, 2] *= 1.25  # Stretch in the z
        cube = Group()
        cube.verts = SGroup()
        cube.edges = VGroup()
        cube.add(cube.verts, cube.edges)
        for n, coords in enumerate(vert_coords):
            vert = Sphere(resolution=(21, 21))
            vert.set_height(short_vert_height)
            vert.rotate(90 * DEGREES, RIGHT)
            vert.move_to(coords)
            cube.verts.add(vert)
            vert.edges = VGroup()
            for m, coords2 in enumerate(vert_coords):
                if sum(int_to_bit_coords(n ^ m)) == 1:
                    edge = Line(coords, coords2)
                    cube.edges.add(edge)
                    vert.edges.add(edge)
            vert.edges.apply_depth_test()

        cube.edges.set_color(GREY)
        cube.edges.apply_depth_test()

        cube.rotate(30 * DEGREES, DOWN)
        cube.to_edge(RIGHT)
        cube.set_height(4)

        self.play(
            ShowCreation(cube.edges, lag_ratio=0.1),
            LaggedStartMap(FadeInFromLarge, cube.verts, lambda m: (m, 0.2)),
            run_time=2,
        )

        # Setup cube color
        def get_colored_vertices(values, verts=cube.verts):
            color_choices = [RED, GREEN, BLUE_D]
            color_label_choices = ["R", "G", "B"]
            vert_targets = SGroup()
            labels = VGroup()
            for n, vert in zip(values, verts):
                color = color_choices[n]
                v_target = vert.copy()
                if n == -1:
                    v_target.set_height(short_vert_height)
                    v_target.set_color(GREY)
                    label = VectorizedPoint()
                else:
                    v_target.set_color(color)
                    v_target.set_height(tall_vert_height)
                    label = TexMobject(color_label_choices[n])
                    label.set_color(color)
                    label.set_stroke(BLACK, 3, background=True)
                label.next_to(vert, UR, buff=0)
                vert_targets.add(v_target)
                labels.add(label)
            return vert_targets, labels

        new_verts, color_labels = get_colored_vertices(np.arange(0, 8) % 3)
        for vert, label in zip(cube.verts, color_labels):
            vert.label = label

        self.play(
            Transform(cube.verts, new_verts),
            Write(color_labels),
            run_time=2,
        )
        self.wait()

        def get_color_change_animations(values, verts=cube.verts, labels=color_labels, gcv=get_colored_vertices):
            new_verts, new_labels = gcv(values)
            old_labels = labels.copy()
            labels.become(new_labels)
            return [
                Transform(verts, new_verts),
                LaggedStartMap(FadeOut, old_labels, lambda m: (m, 0.5 * UP), lag_ratio=0.03),
                LaggedStartMap(FadeIn, labels, lambda m: (m, 0.5 * DOWN), lag_ratio=0.03),
            ]

        # Prepare a few colorings
        mod3_strategy = [
            np.dot(int_to_bit_coords(n), [0, 1, 2]) % 3
            for n in range(8)
        ]
        sum_bits = [sum(int_to_bit_coords(n)) % 3 for n in range(8)]

        self.play(*get_color_change_animations(sum_bits))
        self.wait()
        self.play(*get_color_change_animations(mod3_strategy))
        self.wait()

        # Pull out vertices with their neighbors
        # first just one, then all of them.
        trees = Group()
        tree_targets = Group()
        for n, vert in enumerate(cube.verts):
            tree = Group()
            tree.root = vert.copy()
            tree.root.origin = tree.root.get_center()
            tree.edges = VGroup()
            tree.leafs = Group()
            tree.labels = Group()
            for mask in [1, 2, 4]:
                leaf = cube.verts[n ^ mask]
                leaf.origin = leaf.get_center()
                label = leaf.label.copy()
                label.original = leaf.label
                tree.edges.add(Line(vert.get_center(), leaf.get_center()))
                tree.leafs.add(leaf.copy())
                tree.labels.add(label)
            tree.edges.apply_depth_test()
            tree.edges.match_style(vert.edges)
            tree.edges.save_state()
            tree.add(tree.root, tree.edges, tree.leafs, tree.labels)
            trees.add(tree)

            tree.generate_target(use_deepcopy=True)
            for edge, leaf, label, y in zip(tree.target.edges, tree.target.leafs, tree.target.labels, [0.4, 0, -0.4]):
                start = vert.get_center()
                end = start + RIGHT + y * UP
                edge.set_points_as_corners([start, end])
                leaf.move_to(edge.get_end())
                label.next_to(leaf, RIGHT, buff=SMALL_BUFF)
                label.scale(0.7)
            tree_targets.add(tree.target)
        tree_targets.arrange_in_grid(4, 2, buff=LARGE_BUFF)
        tree_targets[1::2].shift(0.5 * RIGHT)
        tree_targets.set_height(6)
        tree_targets.center()
        tree_targets.to_corner(DL)

        self.play(
            MoveToTarget(trees[0]),
            run_time=3,
        )
        self.wait()
        self.play(
            LaggedStartMap(
                MoveToTarget, trees[1:],
                lag_ratio=0.3,
            ),
            run_time=6,
        )
        self.add(trees)
        self.wait()

        # Show what we want
        want_rect = SurroundingRectangle(trees, buff=MED_SMALL_BUFF)
        want_rect.set_stroke(WHITE, 1)
        want_label = TextMobject("What we want")
        want_label.next_to(want_rect, UP)

        trees.save_state()
        anims = []
        for tree in trees:
            anims.append(ApplyMethod(tree.root.set_color, GREY))
            colors = [RED, GREEN, BLUE_D]
            letters = ["R", "G", "B"]
            for color, letter, leaf, label in zip(colors, letters, tree.leafs, tree.labels):
                new_label = TextMobject(letter)
                new_label.set_fill(color)
                new_label.replace(label, dim_to_match=1)
                old_label = label.copy()
                label.become(new_label)
                anims += [
                    FadeIn(label, 0.1 * LEFT),
                    FadeOut(old_label, 0.1 * RIGHT),
                    ApplyMethod(leaf.set_color, color),
                ]

        cube.verts.generate_target()
        cube.verts.save_state()
        cube.verts.target.set_color(GREY)
        for vert in cube.verts.target:
            vert.scale(0.75)
        self.play(
            ShowCreation(want_rect),
            Write(want_label),
            LaggedStart(*anims, lag_ratio=0.001, run_time=3),
            FadeOut(color_labels),
            MoveToTarget(cube.verts),
        )
        self.add(trees)
        trees.unlock_shader_data()
        self.wait()

        # Try to fit these back onto the cube
        # First attempt
        def restore_tree(tree, **kwargs):
            anims = []
            for mob in [tree.root, *tree.leafs]:
                anims.append(ApplyMethod(mob.move_to, mob.origin))
            for label in tree.labels:
                label.generate_target()
                label.target.replace(label.original, dim_to_match=1)
                anims.append(MoveToTarget(label))
            anims.append(Restore(tree.edges))
            return AnimationGroup(*anims, **kwargs)

        tree_copies = trees.deepcopy()
        self.play(restore_tree(tree_copies[0], run_time=2))
        self.wait()
        self.play(restore_tree(tree_copies[1], run_time=2))
        self.wait()

        frame = self.camera.frame
        self.play(
            UpdateFromAlphaFunc(
                frame,
                lambda m, a: m.move_to(0.1 * wiggle(a, 6) * RIGHT),
            ),
            FadeOut(tree_copies[0]),
            FadeOut(tree_copies[1]),
        )

        # Second attempt
        def restore_vertex(n, verts=cube.verts, labels=color_labels):
            return AnimationGroup(
                Transform(verts[n], verts.saved_state[n]),
                FadeIn(labels[n], DOWN)
            )

        for i in [0, 4, 2, 1]:
            self.play(restore_vertex(i))
        self.wait()
        self.play(ShowCreationThenFadeAround(cube.verts[4]))
        for i in [6, 5]:
            self.play(restore_vertex(i))
        self.wait()

        q_marks = VGroup(*[TexMobject("???") for x in range(2)])
        q_marks[0].next_to(cube.verts[7], UP, SMALL_BUFF)
        q_marks[1].next_to(cube.verts[3], UP, SMALL_BUFF)
        self.play(Write(q_marks))
        self.wait()

        # Mention it'll never work
        nv_label = TextMobject("It'll never work!")
        nv_label.set_height(0.5)
        nv_label.next_to(cube, UP, buff=0.75)

        cube_copy = cube.deepcopy()
        self.remove(cube)
        self.add(cube_copy)
        new_verts, new_labels = get_colored_vertices([-1] * 8)
        self.play(
            Transform(cube_copy.verts, new_verts),
            FadeOut(q_marks),
            FadeOut(color_labels[:3]),
            FadeOut(color_labels[4:7]),
        )
        self.add(cube_copy)
        self.play(FadeIn(nv_label, DOWN))
        for vert in cube_copy.verts:
            vert.generate_target()
            vert.target.scale(0.01)
            vert.target.set_opacity(0)
        self.play(
            LaggedStartMap(Uncreate, cube_copy.edges),
            LaggedStartMap(MoveToTarget, cube_copy.verts),
        )

        # Highlight symmetry
        rects = VGroup()
        for tree in trees:
            t_rect = SurroundingRectangle(
                Group(tree.leafs, tree.labels),
                buff=SMALL_BUFF
            )
            t_rect.set_stroke(YELLOW, 2)
            rects.add(t_rect)

        self.play(LaggedStartMap(ShowCreationThenFadeOut, rects, lag_ratio=0.025, run_time=3))
        self.wait()

        # Show implication
        implies = TexMobject("\\Rightarrow")
        implies.set_height(0.7)
        implies.next_to(want_rect, RIGHT)
        number_labels = VGroup(*[
            TextMobject("Number of ", f"{color} vertices")
            for color in ["red", "green", "blue"]
        ])
        for color, label in zip(colors, number_labels):
            label[1].set_color(color)
        number_labels.set_height(0.5)
        number_labels.arrange(DOWN, buff=1.5, aligned_edge=LEFT)
        number_labels.next_to(implies, RIGHT, MED_LARGE_BUFF)

        vert_eqs = VGroup(*[TexMobject("=") for x in range(2)])
        vert_eqs.scale(1.5)
        vert_eqs.rotate(90 * DEGREES)
        vert_eqs[0].move_to(number_labels[0:2])
        vert_eqs[1].move_to(number_labels[1:3])

        rhss = VGroup()
        for label in number_labels:
            rhs = TexMobject("= \\frac{8}{3}")
            rhs.scale(1.25)
            rhs.next_to(label, RIGHT)
            rhss.add(rhs)

        self.play(
            Write(implies),
            FadeOut(nv_label),
        )
        self.play(
            GrowFromCenter(vert_eqs),
            FadeIn(number_labels[0], DOWN),
            FadeIn(number_labels[1]),
            FadeIn(number_labels[2], UP),
        )
        self.wait()
        self.play(Write(rhss))
        self.wait(2)
        self.play(
            LaggedStartMap(
                FadeOut, VGroup(*number_labels, *vert_eqs, *rhss, *implies),
            ),
            ShowCreation(cube.edges, lag_ratio=0.1),
            LaggedStartMap(FadeInFromLarge, cube.verts, lambda m: (m, 0.2)),
        )
        self.add(cube)
        new_verts, color_labels = get_colored_vertices(mod3_strategy)
        true_trees = trees.saved_state
        self.play(
            Transform(cube.verts, new_verts),
            FadeIn(color_labels),
            FadeOut(trees),
            FadeOut(want_label)
        )
        self.play(FadeIn(true_trees))
        self.wait()

        # Count colors
        for edge in cube.edges:
            edge.insert_n_curves(10)

        red_total = Integer(height=0.6)
        red_total.next_to(want_rect, UP)
        red_total.set_color(RED)
        self.play(FadeIn(red_total))

        all_label_rects = VGroup()
        for n in range(8):
            tree = true_trees[n]
            vert = cube.verts[n]
            neighbor_highlights = VGroup()
            new_edges = VGroup()
            label_rects = VGroup()
            for mask, label in zip([1, 2, 4], tree.labels):
                neighbor = cube.verts[n ^ mask]
                edge = Line(vert, neighbor, buff=0)
                edge.set_stroke(YELLOW, 5)
                edge.insert_n_curves(10)
                new_edges.add(edge)
                if neighbor.get_color() == Color(RED):
                    circ = Circle()
                    circ.set_stroke(YELLOW, 3)
                    circ.replace(neighbor)
                    neighbor_highlights.add(circ)
                    rect = SurroundingRectangle(label, buff=0.025)
                    rect.set_stroke(YELLOW, 2)
                    label_rects.add(rect)
            new_edges.apply_depth_test()
            new_edges.shift(0.01 * OUT)
            new_tree_edges = tree.edges.copy()
            new_tree_edges.set_stroke(YELLOW, 3)
            new_tree_edges.shift(0.01 * OUT)

            self.play(
                *map(ShowCreation, [*new_edges, *new_tree_edges]),
            )
            for highlight, rect in zip(neighbor_highlights, label_rects):
                self.play(
                    FadeInFromLarge(highlight, 1.2),
                    FadeInFromLarge(rect, 1.2),
                    run_time=0.25
                )
                red_total.increment_value()
                self.wait(0.25)

            self.play(
                FadeOut(neighbor_highlights),
                FadeOut(new_edges),
                FadeOut(new_tree_edges),
            )
            all_label_rects.add(*label_rects)
        self.wait()

        # Show count to 8
        new_verts = get_colored_vertices([-1] * 8)[0]
        self.play(
            FadeOut(true_trees),
            FadeOut(all_label_rects),
            FadeOut(red_total),
            FadeOut(color_labels),
            Transform(cube.verts, new_verts),
        )
        self.play(FadeIn(trees))
        label_rects = VGroup()
        for tree in trees:
            rect = SurroundingRectangle(tree.labels[0], buff=0.025)
            rect.match_style(all_label_rects[0])
            label_rects.add(rect)

        self.play(
            ShowIncreasingSubsets(label_rects, rate_func=linear),
            UpdateFromFunc(
                red_total, lambda m, lr=label_rects: m.set_value(len(lr))
            )
        )
        self.wait()

        # Show red corners
        r_verts = SGroup(cube.verts[3], cube.verts[4]).copy()
        r_labels = VGroup()
        r_edge_groups = VGroup()
        for r_vert in r_verts:
            r_label = TexMobject("R")
            r_label.set_color(RED)
            r_label.next_to(r_vert, UR, buff=0)
            r_labels.add(r_label)
            r_vert.set_height(tall_vert_height)
            r_vert.set_color(RED)
            edges = VGroup()
            for edge in r_vert.edges:
                to_r_edge = edge.copy()
                to_r_edge.reverse_points()
                to_r_edge.set_stroke(YELLOW, 3)
                to_r_edge.shift(0.01 * OUT)
                edges.add(to_r_edge)
            edges.apply_depth_test()
            r_edge_groups.add(edges)

        self.play(
            LaggedStartMap(FadeInFromLarge, r_verts),
            LaggedStartMap(FadeInFromLarge, r_labels),
            run_time=1,
        )
        self.wait()
        for edges in r_edge_groups:
            self.play(ShowCreationThenDestruction(edges, lag_ratio=0.1))
        self.wait()

        rhs = TexMobject("=", "3", "\\, (\\text{\\# Red corners})")
        rhs[2].set_color(RED)
        rhs.match_height(red_total)
        rhs[:2].match_height(red_total, about_edge=RIGHT)
        rhs.next_to(red_total, RIGHT)

        self.play(Write(rhs))
        self.wait()

        three = rhs[1]
        three.generate_target()
        three.target.move_to(red_total, RIGHT)
        over = TexMobject("/")
        over.match_height(three)
        over.next_to(three.target, LEFT, MED_SMALL_BUFF)
        self.play(
            MoveToTarget(three, path_arc=90 * DEGREES),
            red_total.next_to, over, LEFT, MED_SMALL_BUFF,
            FadeIn(over, UR),
            rhs[2].move_to, three, LEFT,
        )
        self.wait()

        np_label = TextMobject("Not possible!")
        np_label.set_height(0.6)
        np_label.next_to(rhs, RIGHT, LARGE_BUFF)
        self.play(Write(np_label))
        self.wait()


class TryTheProofYourself(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Can you predict\\\\the proof?",
            target_mode="hooray",
            bubble_kwargs={
                "height": 3,
                "width": 3,
            },
        )
        self.teacher.bubble.set_fill(opacity=0)
        self.change_student_modes(
            "pondering", "thinking", "confused",
            look_at_arg=self.screen,
        )
        self.wait(3)
        self.change_student_modes("thinking", "pondering", "erm", look_at_arg=self.screen)
        self.wait(4)
        self.change_student_modes("tease", "pondering", "thinking", look_at_arg=self.screen)
        self.wait(5)


class HighDimensionalCount(ThreeDScene):
    def construct(self):
        # Definitions
        N = 6
        colors = [RED, GREEN, BLUE_D, YELLOW, PINK, TEAL]
        coords = np.array([0, 1, 1, 1, 0, 0])

        # Add chess board
        board = Chessboard(shape=(2, 3))
        board.set_height(2)
        board.to_corner(UL)

        grid = NumberPlane(
            x_range=(0, 3), y_range=(0, 2),
            faded_line_ratio=0
        )
        grid.match_height(board)
        grid.match_width(board, stretch=True)
        grid.next_to(board, OUT, 1e-8)
        grid.set_gloss(0.5)

        coins = CoinsOnBoard(board, coin_config={"numeric_labels": True})
        coins.flip_by_bools(coords)
        coin_labels = VGroup()
        for i, coin in zip(coords, coins):
            coin_labels.add(coin.labels[1 - i])

        self.play(
            ShowCreationThenFadeOut(grid, lag_ratio=0.1),
            FadeIn(board),
            FadeIn(coins, lag_ratio=0.1),
            run_time=2
        )

        # Setup corners
        def get_vert(height=0.4, color=RED):
            return get_vertex_sphere(height, color)

        def get_vert_label(coords):
            args = ["("]
            for coord in coords:
                args.append(str(coord))
                args.append(",")
            args[-1] = ")"
            return TexMobject(*args)

        def get_board_with_highlights(n, height=1, N=N, colors=colors):
            board = VGroup(*[Square() for x in range(N)])
            board.arrange_in_grid(2, 3, buff=0)
            board.set_fill(GREY_E, 1)
            board.set_stroke(WHITE, 1)
            board.set_height(height)
            board[n].set_fill(colors[n])
            return board

        vert = get_vert()
        vert_label = get_vert_label(coords)
        vert_board = get_board_with_highlights(0)
        vert_label.next_to(vert, LEFT)
        vert_board.next_to(vert_label, DOWN, MED_LARGE_BUFF)
        neighbors = SGroup()
        for color in colors:
            neighbors.add(get_vert(color=color))
        neighbors.arrange(DOWN, buff=0.75)
        neighbors.next_to(vert, RIGHT, buff=2)
        neighbor_labels = VGroup()
        edges = VGroup()
        neighbor_boards = VGroup()
        for n, neighbor in enumerate(neighbors):
            edge = Line(
                vert.get_center(),
                neighbor.get_center(),
                buff=vert.get_height() / 2,
            )
            new_coords = list(coords)
            new_coords[n] ^= 1
            label = get_vert_label(new_coords)
            label.next_to(neighbor, RIGHT)
            label.add(SurroundingRectangle(label[2 * n + 1], buff=0.05))
            n_board = get_board_with_highlights(n, height=0.7)
            n_board.next_to(label, RIGHT)

            neighbor_boards.add(n_board)
            edges.add(edge)
            neighbor_labels.add(label)

        vertex_group = Group(
            vert_board, vert_label, vert,
            edges,
            neighbors, neighbor_labels, neighbor_boards
        )
        vertex_group.to_corner(DL)

        # Show coords with states
        cl_mover = coin_labels.copy()
        cl_mover.generate_target()
        for m1, m2 in zip(cl_mover.target, vert_label[1::2]):
            m1.replace(m2)
        self.play(
            MoveToTarget(cl_mover),
        )
        self.play(
            FadeIn(vert_label),
            FadeOut(cl_mover)
        )
        self.play(FadeIn(vert_board))
        self.wait()
        self.play(
            ShowIncreasingSubsets(neighbor_labels),
            ShowCreation(edges),
        )
        self.wait()
        self.play(LaggedStartMap(
            TransformFromCopy, neighbor_boards,
            lambda m, b=vert_board: (b, m)
        ))
        self.wait()

        # Show one vertex
        self.play(FadeInFromLarge(vert))
        self.play(LaggedStartMap(
            TransformFromCopy, neighbors,
            lambda m, v=vert: (v, m)
        ))
        self.wait()

        # Isolate vertex
        edges.apply_depth_test()
        tree = Group(vert, edges, neighbors)
        tree.generate_target()
        tree.target[0].scale(0.5)
        tree.target[2].scale(0.5)
        tree.target[2].arrange(DOWN, buff=0)
        tree.target[2].next_to(vert, RIGHT, MED_LARGE_BUFF)
        for edge, nv in zip(tree.target[1], tree.target[2]):
            new_edge = Line(
                vert.get_center(),
                nv.get_center(),
            )
            edge.become(new_edge)
            edge.set_stroke(WHITE, 2)
        tree.target.rotate(-90 * DEGREES)
        tree.target.center()

        short_label = vert_label[1::2]
        short_label.generate_target()
        short_label.target.arrange(RIGHT, buff=SMALL_BUFF)
        short_label.target.match_width(tree.target)
        short_label.target.next_to(tree.target, UP)
        short_label.target.set_fill(GREY_A)

        self.play(
            MoveToTarget(tree),
            MoveToTarget(short_label),
            LaggedStartMap(FadeOut, Group(
                vert_label[0::2],
                vert_board,
                *neighbor_labels,
                *neighbor_boards,
                *board,
                *coins,
            )),
            run_time=2,
        )
        tree.add(short_label)

        # Show all vertices
        def get_bit_string(n, template=short_label):
            bits = VGroup(*map(Integer, int_to_bit_coords(n, min_dim=6)))
            bits.arrange(RIGHT, buff=0.075)
            bits.match_height(template)
            bits.set_color(GREY_A)
            return bits

        new_trees = Group()
        for n in [0, 1, 62, 63]:
            new_tree = tree.copy()
            bits = get_bit_string(n)
            bits.move_to(new_tree[3])
            new_tree.replace_submobject(3, bits)
            new_trees.add(new_tree)
        for new_tree, color in zip(new_trees, [YELLOW, GREEN, RED, BLUE_D]):
            new_tree[0].set_color(color)
        new_trees.arrange(RIGHT, buff=MED_LARGE_BUFF)
        new_trees.move_to(tree)
        new_trees[:2].to_edge(LEFT)
        new_trees[2:].to_edge(RIGHT)

        dots = VGroup(*[TexMobject("\\dots") for x in range(2)])
        dots.scale(2)
        dots[0].move_to(Group(new_trees[1], tree))
        dots[1].move_to(Group(new_trees[2], tree))

        top_brace = Brace(new_trees, UP, buff=MED_LARGE_BUFF)
        total_label = top_brace.get_text("$2^n$ total vertices", buff=MED_LARGE_BUFF)

        low_brace = Brace(tree, DOWN)
        neighbors_label = low_brace.get_text("n neighbors")

        self.play(
            GrowFromCenter(low_brace),
            Write(neighbors_label, run_time=1)
        )
        self.wait()
        self.play(
            GrowFromCenter(dots),
            GrowFromCenter(top_brace),
            LaggedStartMap(
                TransformFromCopy, new_trees,
                lambda m, t=tree: (t, m)
            ),
            Write(total_label, run_time=1),
            run_time=2,
        )
        self.wait()

        # Count red neighbors
        middle_tree = tree
        frame = self.camera.frame
        self.play(frame.move_to, UP)

        count = Integer(1)
        count.set_color(RED)
        count.scale(1.5)
        count.next_to(total_label, UP, LARGE_BUFF, aligned_edge=LEFT)
        two_to_n_label = TexMobject("2^n")
        two_to_n_label.scale(1.5)
        two_to_n_label.set_color(RED)
        two_to_n_label.move_to(count, LEFT)

        n_arrows = VGroup()
        for tree in [*new_trees[:2], middle_tree, *new_trees[2:]]:
            arrow = Vector(
                [-1, -2, 0],
                tip_config={"width": 0.2, "length": 0.2}
            )
            arrow.match_height(tree[1])
            arrow.next_to(tree[2][0], UR, buff=0)
            arrow.set_color(RED)
            n_arrows.add(arrow)

        self.add(n_arrows[0], count)
        self.wait()
        self.add(n_arrows[1])
        count.increment_value()
        self.wait()
        self.play(
            ChangeDecimalToValue(count, 63, rate_func=rush_into),
            LaggedStartMap(FadeIn, n_arrows[2:], lag_ratio=0.5),
            run_time=3
        )
        self.remove(count)
        self.add(two_to_n_label)
        self.wait()

        rhs = TexMobject("=", "n", "\\cdot", "(\\text{\\# Red vertices})")
        rhs.scale(1.5)
        rhs.next_to(two_to_n_label, RIGHT)
        rhs.shift(0.05 * DOWN)
        rhs.set_color_by_tex("Red", RED)
        highlighted_edges = VGroup(*middle_tree[1], new_trees[2][1]).copy()
        highlighted_edges.set_stroke(YELLOW, 3)
        highlighted_edges.shift(0.01 * OUT)
        edge_anim = ShowCreationThenFadeOut(
            highlighted_edges, lag_ratio=0.3
        )

        self.play(edge_anim)
        self.play(Write(rhs), run_time=1)
        self.play(edge_anim)
        self.wait(2)

        # Conclusion
        pairs = VGroup(VGroup(TexMobject("n"), TexMobject("2^n")))
        pairs.set_color(YELLOW)
        for n in range(1, 10):
            pairs.add(VGroup(Integer(n), Integer(2**n)))
        for pair in pairs:
            pair.arrange(RIGHT, buff=0.75, aligned_edge=DOWN)
            line = Line(LEFT, RIGHT)
            line.set_stroke(WHITE, 1)
            line.set_width(2)
            line.next_to(pair, DOWN, aligned_edge=LEFT)
            line.shift(SMALL_BUFF * LEFT)
            pair.add(line)
            pairs.add(pair)
        pairs.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        pairs.set_height(7)
        pairs.to_edge(LEFT)
        pairs.shift(UP)

        marks = VGroup()
        for n, pair in zip(it.count(1), pairs[1:]):
            if sum(int_to_bit_coords(n)) == 1:
                mark = Checkmark()
            else:
                mark = Exmark()
            mark.move_to(pair[1], LEFT)
            mark.shift(RIGHT)
            marks.add(mark)

        v_line = Line(UP, DOWN)
        v_line.set_height(7)
        v_line.set_stroke(WHITE, 1)
        v_line.set_x((pairs[0][0].get_right() + pairs[0][1].get_left())[0] / 2)
        v_line.match_y(pairs)
        pairs.add(v_line)

        new_trees.generate_target()
        new_trees.target[:2].move_to(middle_tree, RIGHT)
        shift_vect = new_trees.target[0].get_center() - new_trees[0].get_center()

        self.play(
            MoveToTarget(new_trees),
            top_brace.match_width, new_trees.target, {"about_edge": RIGHT},
            total_label.shift, shift_vect * 0.5,
            n_arrows[:2].shift, shift_vect,
            FadeOut(middle_tree, RIGHT),
            FadeOut(n_arrows[2], RIGHT),
            FadeOut(dots[0], 2 * RIGHT),
            Write(pairs)
        )
        self.play(LaggedStartMap(
            FadeIn, marks,
            lambda m: (m, 0.2 * LEFT),
            lag_ratio=0.4,
            run_time=5,
        ))
        self.wait()


class SimpleRect(Scene):
    def construct(self):
        rect = SurroundingRectangle(
            VGroup(Integer(4), Integer(16), Integer(0)).arrange(RIGHT, MED_LARGE_BUFF),
        )
        self.play(ShowCreation(rect))
        self.wait(2)
        self.play(FadeOut(rect))


class WhenIsItHopeless(Scene):
    def construct(self):
        boards = Group(
            Chessboard(shape=(1, 3)),
            Chessboard(shape=(2, 2)),
            Chessboard(shape=(2, 3)),
            Chessboard(shape=(2, 3)),
            Chessboard(shape=(2, 4)),
            Chessboard(shape=(2, 4)),
            Chessboard(shape=(3, 3)),
            Chessboard(shape=(3, 4)),
            Chessboard(shape=(3, 4)),
            Chessboard(shape=(3, 4)),
        )
        last_board = None
        last_coins = None
        last_words = None
        for n, board in zip(it.count(3), boards):
            board.scale(1 / board[0].get_height())
            coins = CoinsOnBoard(board)
            coins.flip_at_random()
            diff = len(board) - n
            if diff > 0:
                board[-diff:].set_opacity(0)
                coins[-diff:].set_opacity(0)

            if sum(int_to_bit_coords(n)) == 1:
                words = TextMobject("Maybe possible")
                words.set_color(GREEN)
            else:
                words = TextMobject("Futile!")
                words.set_color(RED)
            words.scale(1.5)
            words.next_to(board, UP, MED_LARGE_BUFF)

            if n == 3:
                self.play(
                    FadeIn(board),
                    FadeIn(coins),
                    FadeIn(words, DOWN),
                )
            else:
                self.play(
                    ReplacementTransform(last_board, board),
                    ReplacementTransform(last_coins, coins),
                    FadeOut(last_words),
                    FadeIn(words, DOWN),
                )
            self.wait()

            last_board = board
            last_coins = coins
            last_words = words


class FourDCubeColoringFromTrees(ThreeDScene):
    def construct(self):
        # Camera stuffs
        frame = self.camera.frame
        light = self.camera.light_source
        light.move_to([-25, -20, 20])

        # Setup cube
        colors = [RED, GREEN, BLUE_D, YELLOW]
        cube = self.get_hypercube()
        for n, vert in enumerate(cube.verts):
            code = boolian_linear_combo(int_to_bit_coords(n, 4))
            cube.verts[n].set_color(colors[code])

        # Create trees
        trees = Group()
        original_trees = Group()
        for vert in cube.verts:
            tree = Group(
                vert,
                vert.edges,
                vert.neighbors,
            ).copy()
            original = tree.copy()
            original[0].set_color(GREY)
            original[0].scale(0)
            original_trees.add(original)
            trees.add(tree)
        for tree in trees:
            tree[0].set_color(GREY)
            tree[0].rotate(90 * DEGREES, LEFT)
            sorted_verts = Group(*tree[2])
            sorted_verts.submobjects.sort(key=lambda m: m.get_color().hex)
            sorted_verts.arrange(DOWN, buff=SMALL_BUFF)
            sorted_verts.next_to(tree[0], RIGHT, buff=0.75)
            for edge, neighbor in zip(tree[1], tree[2]):
                edge.become(Line3D(
                    tree[0].get_center(),
                    neighbor.get_center(),
                    resolution=edge.resolution,
                ))
                neighbor.rotate(90 * DEGREES, LEFT)

        trees.arrange_in_grid(4, 4, buff=MED_LARGE_BUFF)
        for i in range(4):
            trees[i::4].shift(0.5 * i * RIGHT)
        trees.center()
        trees.set_height(6)
        trees.rotate(PI / 2, RIGHT)
        trees.move_to(10 * LEFT, LEFT)

        frame.set_phi(90 * DEGREES)
        frame.move_to(5 * LEFT)
        self.add(trees)
        self.wait()

        # Show transition
        anims = []
        for tree, original in zip(trees, original_trees):
            anims.append(Transform(tree, original))
        self.play(
            frame.set_rotation, 20 * DEGREES, 70 * DEGREES,
            frame.move_to, ORIGIN,
            LaggedStart(*anims, lag_ratio=0.2),
            run_time=8,
        )
        self.remove(trees)
        self.add(cube)
        frame.add_updater(lambda m, dt: m.increment_theta(2 * dt * DEGREES))
        self.wait(30)

    def get_hypercube(self, dim=4, width=4):
        hc_points = self.get_hypercube_points(dim, width)
        cube = Group()
        cube.verts = SGroup()
        cube.edges = SGroup()
        cube.add(cube.verts, cube.edges)
        for point in hc_points:
            vert = get_vertex_sphere(resolution=(25, 13))
            vert.rotate(PI / 2, UP)
            vert.move_to(point)
            cube.verts.add(vert)
            vert.edges = SGroup()
            vert.neighbors = SGroup()
        for n in range(2**dim):
            for power in range(dim):
                k = n ^ (1 << power)
                edge = Line3D(
                    hc_points[n],
                    hc_points[k],
                    width=0.05,
                    resolution=(31, 31)
                )
                cube.edges.add(edge)
                cube.verts[n].edges.add(edge)
                cube.verts[n].neighbors.add(cube.verts[k])
        return cube

    def get_hypercube_points(self, dim=4, width=4):
        all_coords = [
            int_to_bit_coords(n, dim).astype(float)
            for n in range(2**dim)
        ]
        vertex_holder = Mobject()
        vertex_holder.set_points([
            sum([c * v for c, v in zip(reversed(coords), [RIGHT, UP, OUT])])
            for coords in all_coords
        ])
        vertex_holder.center()
        if dim == 4:
            vertex_holder.points[8:] *= 2
        vertex_holder.set_width(width)
        return vertex_holder.points


class IntroduceHypercube(FourDCubeColoringFromTrees):
    def construct(self):
        # Camera stuffs
        frame = self.camera.frame
        light = self.camera.light_source
        light.move_to([-25, -20, 20])

        # Setup cubes
        cubes = [
            self.get_hypercube(dim=d)
            for d in range(5)
        ]

        def reconnect_edges(cube):
            for vert in cube.verts:
                for edge, neighbor in zip(vert.edges, vert.neighbors):
                    edge.become(Line3D(
                        vert.get_center(),
                        neighbor.get_center(),
                        resolution=edge.resolution
                    ))

        # Show increasing dimensions
        label = VGroup(Integer(0), TexMobject("D"))
        label.arrange(RIGHT, buff=SMALL_BUFF)
        label.scale(1.5)
        label.to_edge(UP)
        label.fix_in_frame()

        def get_cube_intro_anim(n, cubes=cubes, reconnect_edges=reconnect_edges, label=label):
            if n == 0:
                return GrowFromCenter(cubes[n])
            self.remove(cubes[n - 1])
            cubes[n].save_state()
            for v1, v2 in zip(cubes[n].verts, it.cycle(cubes[n - 1].verts)):
                v1.move_to(v2)
            reconnect_edges(cubes[n])
            if n == 1:
                cubes[n].edges.scale(0)
            return AnimationGroup(
                Restore(cubes[n]),
                ChangeDecimalToValue(label[0], n),
            )

        self.play(
            FadeIn(label, DOWN),
            get_cube_intro_anim(0)
        )
        self.wait()
        for n in [1, 2]:
            self.play(get_cube_intro_anim(n))
            self.wait()
        self.play(
            get_cube_intro_anim(3),
            ApplyMethod(
                frame.set_rotation, -20 * DEGREES, 75 * DEGREES,
                run_time=3
            )
        )
        frame.add_updater(lambda m, dt: m.increment_theta(dt * DEGREES))
        self.wait(4)

        # Flatten cube
        flat_cube = self.get_hypercube(3)
        for n, vert in enumerate(flat_cube.verts):
            point = vert.get_center()
            if n < 4:
                point *= 1.5
            else:
                point *= 0.75
            point[2] = 0
            vert.move_to(point)
        reconnect_edges(flat_cube)

        plane = NumberPlane(x_range=(-10, 10), y_range=(-10, 10), faded_line_ratio=0)
        plane.set_opacity(0.25)
        plane.apply_depth_test()
        plane.axes.shift(0.01 * OUT)
        plane.shift(0.02 * IN)

        cubes[3].save_state()
        self.add(cubes[3], plane)
        self.play(
            FadeIn(plane, run_time=2),
            Transform(cubes[3], flat_cube, run_time=2),
        )
        self.wait(7)
        self.play(
            Restore(cubes[3], run_time=2),
            FadeOut(plane)
        )
        self.play(get_cube_intro_anim(4), run_time=3)
        self.wait(10)

        # Highlight some neighbor groups
        colors = [RED, GREEN, BLUE_D, YELLOW]
        for x in range(6):
            vert = random.choice(cubes[4].verts)
            neighbors = vert.neighbors.copy()
            neighbors.save_state()
            neighbors.generate_target()
            new_edges = VGroup()
            for neighbor, color in zip(neighbors.target, colors):
                neighbor.set_color(color)
                edge = Line(
                    vert.get_center(),
                    neighbor.get_center(),
                    buff=vert.get_height() / 2,
                )
                edge.set_stroke(color, 5)
                new_edges.add(edge)
            self.remove(vert.neighbors)
            self.play(
                ShowCreation(new_edges, lag_ratio=0.2),
                MoveToTarget(neighbors),
            )
            self.wait(1)
            self.play(
                FadeOut(new_edges),
                Restore(neighbors),
            )
            self.remove(neighbors)
            self.add(vert.neighbors)

        # Show valid coloring
        cubes[4].generate_target()
        for n, vert in enumerate(cubes[4].target[0]):
            code = boolian_linear_combo(int_to_bit_coords(n, 4))
            vert.set_color(colors[code])
        self.play(MoveToTarget(cubes[4], lag_ratio=0.2, run_time=3))
        self.wait(15)


# Animations for Matt
class WantAdditionToBeSubtraction(ThreeDScene):
    def construct(self):
        # Add sum
        coins = CoinsOnBoard(
            Chessboard(shape=(1, 4)),
            coin_config={"numeric_labels": True},
        )
        for coin in coins[0], coins[2]:
            coin.flip()

        coefs = VGroup(*[TexMobject(f"X_{i}") for i in range(len(coins))])
        full_sum = Group()
        to_fade = VGroup()
        for coin, coef in zip(coins, coefs):
            coin.set_height(0.7)
            coef.set_height(0.5)
            summand = Group(coin, TexMobject("\\cdot"), coef, TexMobject("+"))
            to_fade.add(*summand[1::2])
            summand.arrange(RIGHT, buff=0.2)
            full_sum.add(summand)
        full_sum.add(TexMobject("\\dots"))
        full_sum.arrange(RIGHT, buff=0.2)
        to_fade.add(full_sum[-1])

        some_label = TextMobject("Some kind of ``numbers''")
        some_label.next_to(full_sum, DOWN, buff=2)
        arrows = VGroup(*[
            Arrow(some_label.get_top(), coef.get_bottom())
            for coef in coefs
        ])

        for coin in coins:
            coin.save_state()
            coin.rotate(90 * DEGREES, UP)
            coin.set_opacity(0)

        self.play(
            LaggedStartMap(Restore, coins, lag_ratio=0.3),
            run_time=1
        )
        self.play(
            FadeIn(to_fade),
            LaggedStartMap(FadeInFromPoint, coefs, lambda m: (m, some_label.get_top())),
            LaggedStartMap(GrowArrow, arrows),
            Write(some_label, run_time=1)
        )
        self.wait()
        self.play(FadeOut(some_label), FadeOut(arrows))

        # Show a flip
        add_label = TexMobject("+X_2", color=GREEN)
        sub_label = TexMobject("-X_2", color=RED)
        for label in add_label, sub_label:
            label.next_to(coins[2], UR)
            label.match_height(coefs[2])
            self.play(
                FlipCoin(coins[2]),
                FadeIn(label, 0.5 * DOWN)
            )
            self.play(FadeOut(label))

        # What we want
        want_label = TextMobject("Want: ", "$X_i = -X_i$")
        eq = TextMobject("$X_i + X_i = 0$")
        want_label.next_to(full_sum, DOWN, LARGE_BUFF)
        eq.next_to(want_label[1], DOWN, aligned_edge=LEFT)

        self.play(FadeIn(want_label))
        self.wait()
        self.play(FadeIn(eq, UP))
        self.wait()


class BitVectorSum(ThreeDScene):
    def construct(self):
        # Setup
        board = Chessboard(shape=(1, 4))
        board.set_height(1)
        coins = CoinsOnBoard(board, coin_config={"numeric_labels": True})
        coins[2].flip()

        all_coords = [np.array([b0, b1]) for b0, b1 in it.product(range(2), range(2))]
        bit_vectors = VGroup(*[
            IntegerMatrix(coords.reshape((2, 1))).set_height(1)
            for coords in all_coords
        ])
        bit_vectors.arrange(RIGHT, buff=2)
        bit_vectors.to_edge(UP)
        bit_vectors.set_stroke(BLACK, 4, background=True)

        arrows = VGroup(
            Arrow(board[0].get_corner(UL), bit_vectors[0].get_corner(DR)),
            Arrow(board[1].get_corner(UP), bit_vectors[1].get_corner(DOWN)),
            Arrow(board[2].get_corner(UP), bit_vectors[2].get_corner(DOWN)),
            Arrow(board[3].get_corner(UR), bit_vectors[3].get_corner(DL)),
        )

        # Show vectors
        self.add(board)
        self.add(coins)
        for arrow, vector in zip(arrows, bit_vectors):
            self.play(
                GrowArrow(arrow),
                FadeInFromPoint(vector, arrow.get_start()),
            )
            self.wait()

        # Move coins
        coin_copies = coins.copy()
        cdots = VGroup()
        plusses = VGroup()
        for cc, vector in zip(coin_copies, bit_vectors):
            dot = TexMobject("\\cdot")
            dot.next_to(vector, LEFT, MED_SMALL_BUFF)
            cdots.add(dot)
            plus = TexMobject("+")
            plus.next_to(vector, RIGHT, MED_SMALL_BUFF)
            plusses.add(plus)
            cc.next_to(dot, LEFT, MED_SMALL_BUFF)
        plusses[-1].set_opacity(0)

        for coin, cc, dot, plus in zip(coins, coin_copies, cdots, plusses):
            self.play(
                TransformFromCopy(coin, cc),
                Write(dot),
            )
            self.play(Write(plus))
        self.wait()

        # Show sum
        eq = TexMobject("=")
        eq.move_to(plusses[-1])

        def get_rhs(coins=coins, bit_vectors=bit_vectors, all_coords=all_coords, eq=eq):
            bit_coords = sum([
                (b * coords)
                for coords, b in zip(all_coords, coins.get_bools())
            ]) % 2
            n = bit_coords_to_int(bit_coords)
            result = bit_vectors[n].copy()
            result.next_to(eq, RIGHT)
            result.n = n
            return result

        def get_rhs_anim(rhs, bit_vectors=bit_vectors):
            bv_copies = bit_vectors.copy()
            bv_copies.generate_target()
            for bv in bv_copies.target:
                bv.move_to(rhs)
                bv.set_opacity(0)
            bv_copies.target[rhs.n].set_opacity(1)
            return AnimationGroup(
                MoveToTarget(bv_copies, remover=True),
                ShowIncreasingSubsets(Group(rhs), int_func=np.floor)
            )

        rhs = get_rhs()

        mod2_label = TextMobject("(Add mod 2)")
        mod2_label.next_to(rhs, DOWN, MED_LARGE_BUFF)
        mod2_label.to_edge(RIGHT)

        self.play(
            Write(eq),
            get_rhs_anim(rhs),
            FadeIn(mod2_label),
            FadeOut(board),
            FadeOut(coins),
            FadeOut(arrows),
        )
        self.wait(2)

        # Show some flips
        for x in range(8):
            i = random.randint(0, 3)
            rect = SurroundingRectangle(Group(coin_copies[i], bit_vectors[i]))
            old_rhs = rhs
            coins[i].flip()
            rhs = get_rhs()
            self.play(
                ShowCreation(rect),
                FlipCoin(coin_copies[i]),
                FadeOut(old_rhs, RIGHT),
                FadeIn(rhs, LEFT),
            )
            self.play(FadeOut(rect))
            self.wait(2)


class ExampleSquareAsBinaryNumber(Scene):
    def construct(self):
        # Setup
        board = Chessboard()
        nums = VGroup()
        bin_nums = VGroup()
        for n, square in enumerate(board):
            bin_num = VGroup(*[
                Integer(int(b))
                for b in int_to_bit_coords(n, min_dim=6)
            ])
            bin_num.arrange(RIGHT, buff=SMALL_BUFF)
            bin_num.set_width((square.get_width() * 0.8))
            num = Integer(n)
            num.set_height(square.get_height() * 0.4)

            for mob in num, bin_num:
                mob.move_to(square, OUT)
                mob.set_stroke(BLACK, 4, background=True)

            num.generate_target()
            num.target.replace(bin_num, stretch=True)
            num.target.set_opacity(0)
            bin_num.save_state()
            bin_num.replace(num, stretch=True)
            bin_num.set_opacity(0)

            nums.add(num)
            bin_nums.add(bin_num)

        # Transform to binary
        self.add(board, nums)
        self.wait()
        original_nums = nums.copy()
        self.play(LaggedStart(*[
            AnimationGroup(MoveToTarget(num), Restore(bin_num))
            for num, bin_num in zip(nums, bin_nums)
        ]), lag_ratio=0.1)
        self.remove(nums)
        nums = original_nums
        self.wait(2)

        self.play(
            bin_nums.set_stroke, None, 0,
            bin_nums.set_opacity, 0.1,
        )
        self.wait()

        # Count
        n = 43
        self.play(
            board[n].set_color, MAROON_E,
            Animation(bin_nums[n]),
        )

        last = VMobject()
        shown_nums = VGroup()
        for k in [0, 8, 16, 24, 32, 40, 41, 42, 43]:
            nums[k].set_fill(YELLOW)
            self.add(nums[k])
            self.play(last.set_fill, WHITE, run_time=0.5)
            last = nums[k]
            shown_nums.add(last)
            if k == 40:
                self.wait()
        self.wait()
        self.play(LaggedStartMap(FadeOut, shown_nums[:-1]))
        self.wait()
        self.play(
            FadeOut(last),
            bin_nums[n].set_opacity, 1,
            bin_nums[n].set_fill, YELLOW
        )
        self.wait()


class ShowCurrAndTarget(Scene):
    CONFIG = {
        "bit_strings": [
            "011010",
            "110001",
            "101011",
        ]
    }

    def construct(self):
        words = VGroup(
            TextMobject("Current: "),
            TextMobject("Need to change:"),
            TextMobject("Target: "),
        )
        words.arrange(DOWN, buff=0.75, aligned_edge=RIGHT)

        def get_bit_aligned_bit_string(bit_coords):
            result = VGroup(*[Integer(int(b)) for b in bit_coords])
            for i, bit in enumerate(result):
                bit.move_to(ORIGIN, LEFT)
                bit.shift(i * RIGHT * 0.325)
            result.set_stroke(BLACK, 4, background=True)
            return result

        bit_strings = VGroup(*[
            get_bit_aligned_bit_string(bs)
            for bs in self.bit_strings
        ])
        for word, bs in zip(words, bit_strings):
            bs.next_to(word, RIGHT)

        words[1].set_fill(YELLOW)
        bit_strings[1].set_fill(YELLOW)

        self.add(words[::2])
        self.add(bit_strings[::2])
        self.wait()
        self.play(FadeIn(words[1]))

        for n in reversed(range(6)):
            rect = SurroundingRectangle(Group(
                bit_strings[0][n],
                bit_strings[2][n],
                buff=0.05,
            ))
            rect.insert_n_curves(100)
            rect = DashedVMobject(rect, num_dashes=40)
            rect.set_stroke(WHITE, 2)
            self.play(ShowCreation(rect))
            self.wait()
            self.play(FadeIn(bit_strings[1][n]))
            self.play(FadeOut(rect))


class ShowCurrAndTargetAlt(ShowCurrAndTarget):
    CONFIG = {
        "bit_strings": [
            "110100",
            "010101",
            "100001",
        ]
    }


class EulerDiagram(Scene):
    def construct(self):
        colors = [RED, GREEN, BLUE]
        vects = compass_directions(3, UP)
        circles = VGroup(*[
            Circle(
                radius=2,
                fill_color=color,
                stroke_color=color,
                fill_opacity=0.5,
                stroke_width=3,
            ).shift(1.2 * vect)
            for vect, color in zip(vects, colors)
        ])
        bit_coords = list(map(int_to_bit_coords, range(8)))
        bit_strings = VGroup(*map(get_bit_string, bit_coords))
        bit_strings.center()
        r1 = 2.2
        r2 = 1.4
        bit_strings[0].next_to(circles[0], LEFT).shift(UP)
        bit_strings[1].shift(r1 * vects[0])
        bit_strings[2].shift(r1 * vects[1])
        bit_strings[3].shift(r2 * (vects[0] + vects[1]))
        bit_strings[4].shift(r1 * vects[2])
        bit_strings[5].shift(r2 * (vects[0] + vects[2]))
        bit_strings[6].shift(r2 * (vects[1] + vects[2]))

        self.add(circles)

        for circle in circles:
            circle.save_state()

        for coords, bstring in zip(bit_coords[1:], bit_strings[1:]):
            for circ, coord in zip(circles, reversed(coords)):
                circ.generate_target()
                if coord:
                    circ.target.become(circ.saved_state)
                else:
                    circ.target.set_opacity(0.1)
            self.play(
                FadeIn(bstring),
                *map(MoveToTarget, circles),
                run_time=0.25,
            )
            self.wait(0.75)
        self.wait()
        self.play(FadeIn(bit_strings[0], DOWN))
        self.wait()


class ShowBoardRegions(ThreeDScene):
    def construct(self):
        # Setup
        board = Chessboard()
        nums = VGroup()
        pre_bin_nums = VGroup()
        bin_nums = VGroup()
        for n, square in enumerate(board):
            bin_num = VGroup(*[
                Integer(int(b), fill_color=GREY_A)
                for b in int_to_bit_coords(n, min_dim=6)
            ])
            bin_num.arrange(RIGHT, buff=SMALL_BUFF)
            bin_num.set_width((square.get_width() * 0.8))
            num = Integer(n)
            num.set_height(square.get_height() * 0.4)

            for mob in num, bin_num:
                mob.move_to(square, OUT)
                mob.set_stroke(BLACK, 4, background=True)

            bin_num.align_to(square, DOWN)
            bin_num.shift(SMALL_BUFF * UP)

            pre_bin_num = num.copy()
            pre_bin_num.generate_target()
            pre_bin_num.target.replace(bin_num, stretch=True)
            pre_bin_num.target.set_opacity(0)

            num.generate_target()
            num.target.scale(0.7)
            num.target.align_to(square, UP)
            num.target.shift(SMALL_BUFF * DOWN)

            bin_num.save_state()
            bin_num.replace(num, stretch=True)
            bin_num.set_opacity(0)

            nums.add(num)
            bin_nums.add(bin_num)
            pre_bin_nums.add(pre_bin_num)

        # Transform to binary
        self.add(board)
        self.play(
            ShowIncreasingSubsets(nums, run_time=4, rate_func=bezier([0, 0, 1, 1]))
        )
        self.wait()
        self.play(
            LaggedStart(*[
                AnimationGroup(
                    MoveToTarget(num),
                    MoveToTarget(pbn),
                    Restore(bin_num),
                )
                for num, pbn, bin_num in zip(nums, pre_bin_nums, bin_nums)
            ], lag_ratio=1.5 / 64),
        )
        self.remove(pre_bin_nums)
        self.wait(2)

        # Build groups to highlight
        one_groups = VGroup()
        highlights = VGroup()
        for i in reversed(range(6)):
            one_group = VGroup()
            highlight = VGroup()
            for bin_num, square in zip(bin_nums, board):
                boundary_square = Square()
                # boundary_square.set_stroke(YELLOW, 4)
                boundary_square.set_stroke(BLUE, 4)
                boundary_square.set_fill(BLUE, 0.25)
                boundary_square.replace(square)
                boundary_square.move_to(square, OUT)
                bit = bin_num[i]
                if bit.get_value() == 1:
                    one_group.add(bit)
                    highlight.add(boundary_square)
            one_group.save_state()
            one_groups.add(one_group)
            highlights.add(highlight)

        # Highlight hit_groups
        curr_highlight = None
        for one_group, highlight in zip(one_groups, highlights):
            one_group.generate_target()
            one_group.target.set_fill(YELLOW)
            one_group.target.set_stroke(YELLOW, 2)
            if curr_highlight is None:
                self.play(MoveToTarget(one_group))
                self.wait()
                self.play(DrawBorderThenFill(highlight, lag_ratio=0.1, run_time=3))
                curr_highlight = highlight
            else:
                self.play(
                    MoveToTarget(one_group),
                    Transform(curr_highlight, highlight)
                )
            self.wait()
            self.play(Restore(one_group))
        self.wait()
        self.play(FadeOut(curr_highlight))


class ShowFinalStrategy(Scene):
    CONFIG = {
        "show_with_lines": False,
    }

    def construct(self):
        # Setup board and such
        board = Chessboard()
        board.to_edge(RIGHT)
        coins = CoinsOnBoard(board, coin_config={"numeric_labels": True})
        coins.flip_by_message("3b1b  :)")

        encoding_lines = VGroup(*[Line(ORIGIN, 0.5 * RIGHT) for x in range(6)])
        encoding_lines.arrange(LEFT, buff=SMALL_BUFF)
        encoding_lines.next_to(board, LEFT, LARGE_BUFF)
        encoding_lines.shift(UP)

        code_words = TextMobject("Encoding")
        code_words.next_to(encoding_lines, DOWN)

        add_words = TextMobject("Check the parity\\\\of these coins")
        add_words.next_to(board, LEFT, LARGE_BUFF, aligned_edge=UP)

        self.add(board, coins)
        self.add(encoding_lines)
        self.add(code_words)

        # Set up groups
        fade_groups = Group()
        line_groups = VGroup()
        mover_groups = VGroup()
        count_mobs = VGroup()
        one_groups = VGroup()
        bits = VGroup()
        for i in range(6):
            bit = Integer(0)
            bit.next_to(encoding_lines[i], UP, SMALL_BUFF)
            bits.add(bit)

            count_mob = Integer(0)
            count_mob.set_color(RED)
            count_mob.next_to(add_words, DOWN, MED_SMALL_BUFF)
            count_mobs.add(count_mob)

            line_group = VGroup()
            fade_group = Group()
            mover_group = VGroup()
            one_rect_group = VGroup()
            count = 0
            for n, coin in enumerate(coins):
                if bool(n & (1 << i)):
                    line_group.add(Line(
                        coin.get_center(),
                        bit.get_center(),
                    ))
                    mover_group.add(coin.labels[1 - int(coin.is_heads())].copy())
                    if coin.is_heads():
                        one_rect_group.add(SurroundingRectangle(coin))
                        count += 1
                else:
                    fade_group.add(coin)
            bit.set_value(count % 2)
            fade_group.save_state()
            line_group.set_stroke(BLUE, width=1, opacity=0.5)
            fade_groups.add(fade_group)
            line_groups.add(line_group)
            mover_groups.add(mover_group)
            one_groups.add(one_rect_group)

        # Animate
        for lines, fades, movers, og, cm, bit in zip(line_groups, fade_groups, mover_groups, one_groups, count_mobs, bits):
            self.play(
                FadeIn(add_words),
                fades.set_opacity, 0.1,
            )
            if self.show_with_lines:
                for mover in movers:
                    mover.generate_target()
                    mover.target.replace(bit)
                    mover.target.set_opacity(0)
                bit.save_state()
                bit.replace(movers[0])
                bit.set_opacity(0)
                self.play(
                    LaggedStartMap(ShowCreation, lines, run_time=2),
                    LaggedStartMap(MoveToTarget, movers, lag_ratio=0.01),
                    Restore(bit)
                )
                self.remove(movers)
                self.add(bit)
                self.play(
                    FadeOut(lines)
                )
            else:
                self.play(
                    ShowIncreasingSubsets(og),
                    UpdateFromFunc(cm, lambda m: m.set_value(len(og)))
                )
                self.play(FadeInFromPoint(bit, cm.get_center()))
                self.play(
                    FadeOut(og),
                    FadeOut(cm),
                )

            self.play(
                FadeOut(add_words),
                Restore(fades),
            )
            self.remove(fades)
            self.add(coins)
        self.wait()


class ShowFinalStrategyWithFadeLines(ShowFinalStrategy):
    CONFIG = {
        "show_with_lines": True,
    }


class Thumbnail(ThreeDScene):
    def construct(self):
        # Board
        board = Chessboard(
            # shape=(8, 8),
            shape=(6, 6),
            square_resolution=(5, 5),
            top_square_resolution=(7, 7),
        )
        board.set_gloss(0.5)

        coins = CoinsOnBoard(
            board,
            coin_config={
                "disk_resolution": (8, 51),
            }
        )
        coins.flip_by_message("(Collab)")

        bools = np.array(string_to_bools("Collab"))
        bools = bools.reshape((6, 8))[:, 2:]
        coins.flip_by_bools(bools.flatten())

        # board[0].set_opacity(0)
        # coins[0].set_opacity(0)

        # k = boolian_linear_combo(coins.get_bools())
        k = 6

        board[k].set_color(YELLOW)

        self.add(board)
        self.add(coins)

        # Move them
        Group(board, coins).shift(DOWN + 2 * RIGHT)

        frame = self.camera.frame
        frame.set_rotation(phi=50 * DEGREES)

        # Title
        title = TextMobject("Impossible")
        title.fix_in_frame()
        title.set_width(8)
        title.to_edge(UP)
        title.set_stroke(BLACK, 6, background=True)
        self.add(title)

        # Instructions
        message = TextMobject(
            "Flip one coin\\\\to describe a\\\\",
            "unique square",
            alignment="",
        )
        message[1].set_color(YELLOW)
        message.scale(1.25)
        message.to_edge(LEFT)
        message.shift(1.25 * DOWN)
        message.fix_in_frame()
        arrow = Arrow(
            message.get_corner(UR),
            message.get_corner(UR) + 3 * RIGHT + UP,
            path_arc=-90 * DEGREES,
        )
        arrow.fix_in_frame()
        arrow.shift(1.5 * LEFT)
        arrow.set_color(YELLOW)

        self.add(message)
        self.add(arrow)


class ChessEndScreen(PatreonEndScreen):
    CONFIG = {
        "scroll_time": 25,
    }
