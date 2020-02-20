from manimlib.imports import *


# Images of randomness

def fix_percent(sym):
    # Really need to make this unneeded...
    new_sym = sym.copy()
    n = 222
    p1 = sym.points[:n]
    p2 = sym.points[n:]
    sym.points = p1
    new_sym.points = p2
    sym.add(new_sym)
    sym.lock_triangulation()


def get_random_process(choices, shuffle_time=2, total_time=4, change_rate=0.05,
                       h_buff=0.05, v_buff=0.05):
    content = choices[0]

    container = Square()
    container.set_opacity(0)
    container.set_width(content.get_width() + 2 * h_buff, stretch=True)
    container.set_height(content.get_height() + 2 * v_buff, stretch=True)
    container.move_to(content)
    container.add(content)
    container.time = 0
    container.last_change_time = 0

    def update(container, dt):
        container.time += dt
        time = container.time
        change = all([
            (time % total_time) < shuffle_time,
            (time - container.last_change_time) > change_rate,
        ])
        if change:
            mob = container.submobjects[0]
            new_mob = random.choice(choices)
            new_mob.match_height(mob)
            new_mob.move_to(container, DL)
            new_mob.shift(2 * np.random.random() * h_buff * RIGHT)
            new_mob.shift(2 * np.random.random() * v_buff * UP)
            container.submobjects = [new_mob]
            container.last_change_time = time

    container.add_updater(update)
    return container


def get_coin(color, symbol):
    coin = VGroup()
    circ = Circle()
    circ.set_fill(color, 1)
    circ.set_stroke(WHITE, 2)
    circ.set_height(1)
    label = TextMobject(symbol)
    label.set_height(0.5 * circ.get_height())
    label.move_to(circ)
    coin.add(circ, label)
    coin.symbol = symbol
    coin.lock_triangulation()
    return coin


def get_random_coin(**kwargs):
    coins = VGroup(
        get_coin(BLUE_E, "H"),
        get_coin(RED_E, "T"),
    )
    return get_random_process(coins, **kwargs)


def get_die_faces():
    dot = Dot()
    dot.set_width(0.15)
    dot.set_color(BLUE_B)

    square = Square()
    square.round_corners(0.25)
    square.set_stroke(WHITE, 2)
    square.set_fill(DARKER_GREY, 1)
    square.set_width(0.6)

    edge_groups = [
        (ORIGIN,),
        (UL, DR),
        (UL, ORIGIN, DR),
        (UL, UR, DL, DR),
        (UL, UR, ORIGIN, DL, DR),
        (UL, UR, LEFT, RIGHT, DL, DR),
    ]

    arrangements = VGroup(*[
        VGroup(*[
            dot.copy().move_to(square.get_bounding_box_point(ec))
            for ec in edge_group
        ])
        for edge_group in edge_groups
    ])
    square.set_width(1)

    faces = VGroup(*[
        VGroup(square.copy(), arrangement)
        for arrangement in arrangements
    ])
    faces.arrange(RIGHT)

    return faces


def get_random_die(**kwargs):
    return get_random_process(get_die_faces(), **kwargs)


def get_random_card(height=1, **kwargs):
    cards = DeckOfCards()
    cards.set_height(height)
    return get_random_process(cards, **kwargs)
