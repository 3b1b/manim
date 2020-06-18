from manimlib.imports import *


def boolian_linear_combo(bools):
    return reduce(op.xor, [b * n for n, b in enumerate(bools)], 0)


def string_to_bools(message):
    # For easter eggs on the board
    bits = bin(int.from_bytes(message.encode(), 'big'))[2:]
    bits = (len(message) * 8 - len(bits)) * '0' + bits
    return [bool(int(b)) for b in bits]


def layer_mobject(mobject, nudge=1e-6):
    for i, sm in enumerate(mobject.family_members_with_points()):
        sm.shift(i * nudge * OUT)


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
        self.arrange_in_grid(buff=0)
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
            frame.set_phi, 20 * DEGREES,
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

        self.play(FadeInFromLarge(rect))
        self.play(FlipCoin(coin), FadeOut(rect))


class FromCoinToSquareMaps(Scene):
    CONFIG = {
        "camera_class": ThreeDCamera,
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

        chessboard = Chessboard()
        chessboard.set_height(0.9 * panels[0].get_height())
        coins = CoinsOnBoard(
            chessboard,
            coin_config={
                "disk_resolution": (2, 25),
                # "include_labels": False,
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

        self.play(FadeIn(panels[0]))
        self.wait()


class SlightTweakIsImpossible(ThreeDScene):
    def construct(self):
        # Definitions
        frame = self.camera.frame
        title = TextMobject("Describe any square\\\\with one flip")
        title.set_height(1.2)
        title.to_edge(UP)
        title.fix_in_frame()

        left_board = Chessboard()
        right_board = Chessboard()
        for board, vect in (left_board, LEFT), (right_board, RIGHT):
            board.set_width(4.5)
            board.to_corner(DOWN + vect, buff=LARGE_BUFF)
        coins = CoinsOnBoard(left_board)
        coins.flip_by_message("HammCode")

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
        self.colored_square = right_board[0]
        self.random_flips(3, left_board, coins, get_special_square)
        self.wait()

        # Remove a square
        to_remove = Group(
            left_board[63], right_board[63], coins[63]
        )
        remove_words = TextMobject("Remove one\\\\square")
        remove_words.set_color(RED)
        remove_words.to_corner(DOWN, buff=1.5)
        remove_words.fix_in_frame()

        self.play(FadeIn(remove_words, DOWN))
        self.play(FadeOut(to_remove, 3 * IN))

        # Not possible
        cross = Cross(title)
        cross.fix_in_frame()
        cross.set_stroke(RED, 8)
        imp_words = TextMobject("Impossible!")
        imp_words.fix_in_frame()
        imp_words.next_to(title, RIGHT, buff=1.5)
        imp_words.shift(2 * LEFT)
        imp_words.set_height(0.7)
        imp_words.set_color(RED)

        self.play(ShowCreation(cross))
        self.play(
            title.shift, 2 * LEFT,
            cross.shift, 2 * LEFT,
            FadeIn(imp_words, LEFT)
        )

        # More flips
        self.random_flips(5, left_board, coins, get_special_square)

    def random_flips(self, n, left_board, coins, get_special_square):
        for x in range(n):
            n = random.randint(0, len(coins) - 1)
            pre_square = Square()
            pre_square.replace(left_board)
            pre_square.move_to(left_board, OUT)
            pre_square.set_stroke(BLUE, 3)
            self.play(
                FlipCoin(coins[n]),
                FadeIn(pre_square)
            )
            new_colored_square = get_special_square()
            pre_square.generate_target()
            pre_square.target.replace(new_colored_square[0])
            pre_square.target.set_fill(BLUE, 0.5)
            pre_square.target.set_stroke(width=0)
            self.play(
                new_colored_square.set_color, BLUE,
                self.colored_square.set_color, self.colored_square.original_color,
                MoveToTarget(pre_square, remover=True)
            )
            self.colored_square = new_colored_square


class TwoSquareCase(ThreeDScene):
    def construct(self):
        frame = self.camera.frame

        # Transition to just two square
        chessboard = Chessboard()
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
                run_time=3,
            ),
        )
        self.play(
            small_group.center,
            small_group.set_height, 1.5,
            frame.set_phi, 10 * DEGREES,
        )
        self.wait()

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
            FlipCoin(coins[0]),
            FadeOut(board_rects[1]),
            FadeIn(board_rects[0]),
            state_rect.move_to, states[1],
            arrows[3].match_style, arrows[0],
            arrows[1].match_style, arrows[3],
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

        self.remove(coins)
        self.add(bin_coins)
        self.play(
            LaggedStartMap(GrowFromCenter, Group(*bin_states.family_members_with_points())),
            LaggedStartMap(ApplyMethod, Group(*states.family_members_with_points()), lambda m: (m.scale, 0)),
        )
        self.wait()

        # Add labels
        c_labels = VGroup(*[
            TexMobject(f"c_{i}")
            for i in range(2)
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
        rule_equation = TexMobject("S", "=", "c_1")
        rule_equation_long = TexMobject("S", "=", "0", "\\cdot", "c_0", "+", "1", "\\cdot", "c_1")
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
            TexMobject("S = 0").next_to(low_rect, UP),
            TexMobject("S = 1").next_to(high_rect, UP),
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

        self.add(board_groups[0])
        self.play(get_board_transform(0))
        self.play(get_board_transform(1))
        self.play(get_board_transform(2), Write(dots))
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
            "0", "\\cdot", "c_0", "+",
            "1", "\\cdot", "c_1", "+",
            "2", "\\cdot", "c_2",
        )
        s_sum.set_height(0.6)
        c_sum = s_sum.copy()
        s_sum.center().to_edge(UP)
        c_sum.next_to(s_sum, DOWN, LARGE_BUFF)

        coin_copies = Group()
        for i in range(3):
            part = c_sum.get_part_by_tex(f"c_{i}")
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
            TexMobject(f"S = {n}")
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
        for i, ncs in enumerate(new_csums):
            ncs.coins[i].flip()
            rhs = set_rhs_target(ncs)
            ncs.coins[i].flip()
            self.play(
                TransformFromCopy(csum, ncs, path_arc=30 * DEGREES)
            )
            self.play(
                FlipCoin(ncs.coins[i]),
                MoveToTarget(rhs)
            )
            self.wait()

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


class ShowCube(ThreeDScene):
    def construct(self):
        # ...
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
        coord_labels.set_stroke(BLACK, 3, background=True)

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
                resolution=(51, 26),
            )
            sphere.set_gloss(0.3)
            sphere.set_color(GREY)
            sphere.move_to(vert)
            spheres.add(sphere)

        edges = SGroup()
        for i, j in edge_indices:
            edge = Line3D(verts[i], verts[j])
            edge.set_color(TEAL)
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
        self.play(highlight(-1))

        colors = [RED, GREEN, BLUE]
        anims = []
        for sphere, cl, coords in zip(spheres, coord_labels, vert_coords):
            color = colors[sum([n * x for n, x in enumerate(coords)]) % 3]
            sphere.generate_target()
            cl.generate_target()
            sphere.target.set_color(color)
            cl.target.set_fill(color)
            anims += [MoveToTarget(sphere), MoveToTarget(cl)]

        self.play(
            edges.set_color, GREY, 0.5,
            LaggedStart(*anims, run_time=3)
        )
        self.wait(5)

        # Focus on (0, 0, 0)
        self.play(
            LaggedStartMap(FlipCoin, coins),
            coord_labels[1:].set_opacity, 0.2,
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
                spheres[0].set_opacity, 0.2,
                coord_labels[0].set_opacity, 0.2,
                FlipCoin(coin)
            )
            self.wait()
            line.reverse_points()
            self.add(line, coord_labels)
            self.play(
                FlipCoin(coin),
                ShowCreation(line)
            )
            lines.add(line)
        self.wait(15)

        # Focus on (0, 1, 0)
        self.play(
            FlipCoin(coins[1]),
            Uncreate(lines[1]),
            FadeOut(lines[::2]),
            Group(
                spheres[1], coord_labels[1],
                spheres[4], coord_labels[4],
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
                # spheres[curr_n].set_opacity, 0.2,
                # coord_labels[curr_n].set_opacity, 0.2,
                FlipCoin(coin)
            )
            self.wait()
            line.reverse_points()
            self.add(line, coord_labels)
            self.play(
                FlipCoin(coin),
                ShowCreation(line)
            )
            lines.add(line)
        self.wait(10)

        # Show a few more colorings
        self.play(
            LaggedStartMap(Uncreate, lines),
            spheres.set_opacity, 1,
            coord_labels.set_opacity, 1,
        )
        self.wait()

        title = TextMobject("Strategy", "\\, $\\Leftrightarrow$ \\,", "Coloring")
        title[2].set_submobject_colors_by_gradient(*colors)
        title.set_stroke(BLACK, 5, background=True)
        title.set_height(0.7)
        title.to_edge(UP)
        title.fix_in_frame()

        def get_coloring_animation(ns, spheres=spheres, coord_labels=coord_labels, color=colors):
            anims = []
            for n, sphere, cl in zip(ns, spheres, coord_labels):
                color = colors[int(n)]
                sphere.generate_target()
                cl.generate_target()
                sphere.target.set_color(color)
                cl.target.set_fill(color)
                anims += [MoveToTarget(sphere), MoveToTarget(cl)]
            return LaggedStart(*anims, run_time=1)

        self.play(FadeIn(title, DOWN))
        for x in range(5):
            self.play(get_coloring_animation(np.random.randint(0, 3, 8)))
        self.wait()

        S0 = TexMobject("S = 0")
        S0.to_edge(LEFT)
        S0.shift(UP)
        S0.fix_in_frame()
        self.play(
            FadeIn(S0, DOWN),
            get_coloring_animation([0] * 8)
        )
        self.wait(3)

        bit_sum = TexMobject("S = &(c_0 + c_1 + c_2) \\\\ &\\quad \\mod 3")
        bit_sum.to_edge(LEFT)
        bit_sum.shift(UP)
        bit_sum.fix_in_frame()
        self.play(
            FadeIn(bit_sum, DOWN),
            FadeOut(S0, UP),
            get_coloring_animation([sum(coords) % 3 for coords in vert_coords])
        )
        self.wait(3)
        self.play(FadeOut(bit_sum, UP))

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
        self.wait(10)
        self.remove(board, coins)
        frame.clear_updaters()
        frame.generate_target()
        frame.target.set_rotation(0, 45 * DEGREES)
        frame.target.shift(2 * UP)
        self.play(
            count.shift, UP,
            count.set_opacity, 0.5,
            ShowIncreasingSubsets(full_board, run_time=3),
            ShowIncreasingSubsets(full_coins, run_time=3),
            FadeIn(count64, DOWN),
            MoveToTarget(frame, run_time=3)
        )
        self.wait(3)

        frame.generate_target()
        frame.target.shift(2 * DOWN)
        frame.target.set_rotation(-15 * DEGREES, 70 * DEGREES)
        self.play(
            MoveToTarget(frame, run_time=3),
            LaggedStartMap(FadeOut, full_board),
            LaggedStartMap(FadeOut, full_coins),
            FadeOut(count),
            FadeOut(count64),
        )
        frame.add_updater(lambda m, dt: m.increment_theta(0.01 * dt))
        self.wait(15)


class CubeSupplement(ThreeDScene):
    def construct(self):
        # Map 8 states to square choices
        boards = Group(*[Chessboard(shape=(1, 3)) for x in range(8)])
        boards.arrange(DOWN, buff=MED_LARGE_BUFF)
        boards.set_height(7)
        boards.to_edge(LEFT)

        self.add(boards)

        # Associate choices with colors



        self.embed()


# TODO, have this read names in from a file
class ChessEndScreen(PatreonEndScreen):
    CONFIG = {
        "scroll_time": 20,
    }
