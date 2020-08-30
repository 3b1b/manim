from manimlib.imports import *
from from_3b1b.active.chess import string_to_bools


def get_background(color=GREY_E):
    background = FullScreenRectangle()
    background.set_fill(color, 1)
    background.set_stroke(width=0)
    return background


def get_bit_grid(n_rows, n_cols, bits=None, buff=MED_SMALL_BUFF, height=4):
    bit_pair = VGroup(Integer(0), Integer(1))
    bit_mobs = VGroup(*[
        bit_pair.copy()
        for x in range(n_rows * n_cols)
    ])
    bit_mobs.arrange_in_grid(n_rows, n_cols, buff=buff)
    bit_mobs.set_height(height)
    if bits is None:
        bits = np.random.randint(0, 2, len(bit_mobs))

    for bit_mob, bit in zip(bit_mobs, bits):
        bit_mob[1 - bit].set_opacity(0)

    bit_mobs.n_rows = n_rows
    bit_mobs.n_cols = n_cols
    return bit_mobs


def get_bit_mob_value(bit_mob):
    return int(bit_mob[1].get_fill_opacity() > bit_mob[0].get_fill_opacity())


def bit_grid_to_bits(bit_grid):
    return list(map(get_bit_mob_value, bit_grid))


def toggle_bit(bit):
    for sm in bit:
        sm.set_fill(opacity=1 - sm.get_fill_opacity())
    return bit


def hamming_syndrome(bits):
    return reduce(
        lambda i1, i2: i1 ^ i2,
        [i for i, b in enumerate(bits) if b],
        0,
    )


def string_to_bits(message):
    return [int(b) for b in string_to_bools(message)]


def int_to_bit_string(number, n_bits=None):
    result = "{:b}".format(number)
    if n_bits is not None:
        result = (n_bits - len(result)) * "0" + result
    return result


def get_image_bits(image, bit_height=0.15, buff=MED_SMALL_BUFF):
    bit = Integer(0)
    small_buff = (buff / bit.get_height()) * bit_height
    bit.set_height(bit_height)
    bits = get_bit_grid(
        n_rows=int(image.get_height() / (bit.get_height() + small_buff)),
        n_cols=int(image.get_width() / (bit.get_width() + small_buff)),
        buff=buff
    )
    bits.replace(image)
    return bits


def get_sound_wave():
    sound = VGroup(*[
        Line(DOWN, UP).set_height(
            (0.3 + 0.8 * random.random()) * abs(np.sin(x))
        )
        for x in np.linspace(0, 3 * PI, 100)
    ])
    sound.arrange(RIGHT, buff=0.05)
    return sound


def get_sender_and_receiver(height=2):
    sender = Randolph(height=height)
    receiver = Mortimer(height=height)
    sender.name = TextMobject("Sender")
    receiver.name = TextMobject("Receiver")

    pis = VGroup(sender, receiver)
    names = VGroup(sender.name, receiver.name)

    sender.to_corner(DL)
    receiver.to_corner(DR)
    pis.shift(UP)
    for name, pi in zip(names, pis):
        name.next_to(pi, DOWN)

    return pis, names


def get_ones(block):
    result = VGroup()
    for bit in block:
        if isinstance(bit, Integer):
            value = bit.get_value()
        else:
            value = get_bit_mob_value(bit)
        if value == 1:
            result.add(bit)
    return result


def get_one_rects(block, buff=SMALL_BUFF):
    rects = VGroup()
    for bit in get_ones(block):
        rect = SurroundingRectangle(bit, buff=buff)
        rect.set_stroke(YELLOW, 3)
        rect.set_fill(YELLOW, 0.2)
        rects.add(rect)
    return rects


def get_ones_counter(label, one_rects, buff=MED_LARGE_BUFF):
    counter = Integer()
    counter.match_color(one_rects[0])
    counter.match_height(label[1])
    counter.next_to(label[1], RIGHT, buff=buff, aligned_edge=DOWN)
    f_always(counter.set_value, lambda: len(one_rects))
    return counter


def get_bit_grid_boxes(bit_grid, color=GREY_B, stroke_width=2):
    width = get_norm(bit_grid[1].get_center() - bit_grid[0].get_center())
    height = get_norm(bit_grid[bit_grid.n_cols].get_center() - bit_grid[0].get_center())
    return VGroup(*[
        Rectangle(
            height=height,
            width=width,
            stroke_color=color,
            stroke_width=stroke_width,
        ).move_to(bit)
        for bit in bit_grid
    ])


def get_grid_position_labels(boxes, height=0.25):
    labels = VGroup()
    for n, box in enumerate(boxes):
        label = Integer(n)
        label.set_height(height)
        label.move_to(box, DR)
        label.shift(SMALL_BUFF * UL)
        labels.add(label)
    return labels


def get_bit_n_sublist(input_list, n, bit_value=1):
    return [
        elem
        for i, elem in enumerate(input_list)
        if bool(i & (1 << n)) ^ bool(1 - bit_value)
    ]


def get_bit_n_subgroup(mob, n, bit_value=1):
    """
    If we enumerate mob, this returns a subgroup of all elements
    whose index has a binary representation with the n'th bit
    equal to bit_value
    """
    return VGroup(*get_bit_n_sublist(mob, n, bit_value))


# Special animations
def image_reveal_animation(image, bit_height=0.1):
    box = SurroundingRectangle(image)
    box.set_fill(BLACK, 1)
    box.set_stroke(width=0)
    bits = get_image_bits(image, bit_height=bit_height)

    return AnimationGroup(
        Animation(image),
        ApplyMethod(
            box.stretch, 0, 1, {"about_edge": DOWN}, remover=True,
            rate_func=linear,
        ),
        LaggedStartMap(
            VFadeInThenOut, bits,
            run_time=1,
            lag_ratio=3 / len(bits)
        )
    )


def toggle_bit_anim(bit, target_color=None, **kwargs):
    original = bit.copy()
    original[1 - get_bit_mob_value(original)].rotate(PI)
    toggle_bit(bit)
    if target_color is not None:
        bit.set_color(target_color)

    if "path_arc" not in kwargs:
        kwargs["path_arc"] = PI

    return TransformFromCopy(original, bit, **kwargs)


def zap_anim(bit, bolt_height=0.75):
    bolt = SVGMobject("lightning_bolt")
    bolt[0].add_line_to(bolt[0].get_start())
    bolt.set_fill(RED_B, 1)
    bolt.set_stroke(width=0)
    bolt.set_height(bolt_height)

    bolt.move_to(bit.get_center(), DL)

    outline = bolt.deepcopy()
    outline.set_stroke(RED_D, 2)
    outline.set_fill(opacity=0)

    return AnimationGroup(
        Succession(
            GrowFromPoint(bolt, bolt.get_corner(UR), rate_func=rush_into),
            FadeOut(bolt, run_time=0.5),
        ),
        Succession(
            ShowCreation(outline),
            FadeOut(outline),
        ),
        run_time=1,
    )


def scan_anim(point, bits, final_stroke_width=0, run_time=3, lag_factor=3, show_robot=True, robot_height=0.5):
    lines = VGroup(*[
        Line(
            point, bit.get_center(),
            stroke_color=[GREEN, BLUE][get_bit_mob_value(bit)],
            stroke_width=1,
        )
        for bit in bits
    ])
    anims = [
        LaggedStartMap(
            lambda m, **kw: Succession(
                ShowCreation(m),
                ApplyMethod(m.set_stroke, None, final_stroke_width),
                **kw
            ),
            lines,
            lag_ratio=lag_factor / len(bits),
            run_time=run_time,
            remover=bool(final_stroke_width)
        )
    ]

    if show_robot:
        robot = SVGMobject("robot")
        robot.set_stroke(width=0)
        robot.set_color(GREY)
        robot.set_gloss(1)
        robot.set_height(robot_height)
        robot.move_to(point, UP)
        anims.append(FadeIn(robot))

    return AnimationGroup(*anims)


def focus_scan_anim_lines(scanim, point, final_stroke_width=1):
    lines = scanim.mobject[0]
    for line in lines:
        line.generate_target()
        line.target.put_start_and_end_on(line.get_start(), point)
        line.target.set_stroke(width=final_stroke_width)

    return AnimationGroup(*[
        MoveToTarget(line)
        for line in lines
    ])


def get_xor(height=0.35, color=BLUE_B, stroke_width=4):
    xor = VGroup(
        Line(UP, DOWN),
        Line(LEFT, RIGHT),
        Circle(),
    )
    xor.set_stroke(color, stroke_width)
    xor.set_height(height)
    return xor


# Scenes


class Thumbnail(Scene):
    def construct(self):
        phrases = VGroup(
            TextMobject("One Bit is Wrong"),
            TextMobject("(according to an extended Hamming Code)"),
            TextMobject("Can you tell which?"),
        )
        for phrase in phrases:
            phrase.set_width(12)

        phrases[0].to_edge(UP)
        phrases[0].set_color(BLUE)

        phrases[1].set_width(10)
        phrases[1].set_color(GREY_C)
        phrases[1].next_to(phrases[0], DOWN, SMALL_BUFF)

        phrases[2].to_edge(DOWN, buff=MED_SMALL_BUFF)
        phrases[2].set_color(BLUE_D)

        bits = VGroup(*[
            Integer(i)
            for i in [
                1, 1, 0, 1, 1, 0, 0, 1,
                0, 1, 1, 0, 1, 1, 1, 1,
            ]
        ])
        # bits[0].set_opacity(0)
        bits.arrange_in_grid(2, 8, buff=SMALL_BUFF)
        bits.set_width(9)
        bits.next_to(phrases[1], DOWN)

        self.add(phrases)
        self.add(bits)


class DiskOfBits(Scene):
    def construct(self):
        # Setup disc
        bits = get_bit_grid(2**5, 2**6, height=6)

        inner_r = 1
        outer_r = 3
        annulus = Annulus(
            inner_radius=inner_r * 0.93,
            outer_radius=outer_r * 1.02,
            fill_color=GREY_D,
        )
        annulus.set_gloss(0.5)

        for bit in bits:
            point = bit.get_center()
            norm = get_norm(point)
            to_inner = inner_r - norm
            to_outer = norm - outer_r
            sdf = 10 * max(to_inner, to_outer)
            if 0 < sdf < 0.5:
                bit.scale(1 - sdf)
            elif sdf > 0:
                bits.remove(bit)

        disc = VGroup(annulus, bits)

        # Setup scratch
        scratch_line = Line(disc.get_top(), disc.get_right())
        scratch_line.set_stroke(RED, width=2, opacity=0.75)

        flipped_bits = VGroup()
        for bit in bits:
            point = bit.get_center()
            norm = abs(point[0] + point[1] - 3)
            alpha = 1 - clip(norm / 0.2, 0, 1)
            if alpha > 0.25:
                bit.generate_target()
                bit.target.set_stroke(width=1)
                bit.target.set_color(RED)
                flipped_bits.add(bit)

        # Add disc
        light = self.camera.light_source
        light.move_to([0, -10, 10])

        random_bits = bits.copy()
        random_bits.sort(lambda p: -get_norm(p))
        self.add(annulus)
        self.play(
            LaggedStartMap(FadeIn, random_bits, lag_ratio=10 / len(bits)),
            light.move_to, [-10, 10, 10],
            run_time=1,
        )
        self.clear()
        self.add(disc)

        # Show scratch
        self.play(
            LaggedStartMap(MoveToTarget, flipped_bits),
            ShowCreationThenDestruction(scratch_line),
            run_time=2,
        )

        # Flip 'em'
        self.play(LaggedStartMap(toggle_bit_anim, flipped_bits))
        self.wait()

        # Show image in and image out
        disc.generate_target()
        disc.target.scale(0.5)

        in_image = ImageMobject("Mona_Lisa")
        in_image.to_edge(LEFT)
        in_image.shift(UP)
        in_words = TextMobject("What was\\\\encoded")
        in_words.next_to(in_image, DOWN)
        out_image = in_image.copy()
        out_image.to_edge(RIGHT)
        out_words = TextMobject("What is\\\\decoded")
        out_words.next_to(out_image, DOWN)

        in_arrow = Arrow(
            in_image.get_right(),
            disc.target.get_left() + 0.2 * UP,
            buff=MED_SMALL_BUFF,
        )
        out_arrow = Arrow(
            disc.target.get_right() + 0.2 * UP,
            out_image.get_left(),
            buff=MED_SMALL_BUFF,
        )
        for arrow in in_arrow, out_arrow:
            arrow.set_fill(GREY_B)

        self.play(
            MoveToTarget(disc),
            GrowArrow(out_arrow),
        )

        in_bits = get_bit_grid(40, 33)
        in_bits.replace(in_image, stretch=True)
        in_bits.set_fill(GREY_B)
        out_bits = in_bits.copy()
        out_bits.move_to(out_image)

        out_image_blocker = SurroundingRectangle(out_image)
        out_image_blocker.set_fill(BLACK, 1)
        out_image_blocker.set_stroke(width=0)

        self.add(out_image, out_image_blocker, out_bits, out_words)
        self.play(
            LaggedStart(
                *[
                    Succession(
                        GrowFromPoint(
                            out_bit,
                            random.choice(bits).get_center(),
                        ),
                        FadeOut(out_bit),
                    )
                    for out_bit in out_bits
                ],
                lag_ratio=3 / len(out_bits),
                run_time=12,
            ),
            ApplyMethod(
                out_image_blocker.stretch, 0, 1, {"about_edge": DOWN},
                run_time=12,
                rate_func=bezier([0, 0, 1, 1]),
            ),
            FadeIn(out_words, UP),
        )
        self.wait()
        self.play(
            TransformFromCopy(out_image, in_image),
            ReplacementTransform(
                in_words.copy().replace(out_words).set_opacity(0),
                in_words,
            ),
        )
        self.play(
            LaggedStart(
                *[
                    Succession(
                        FadeIn(in_bit),
                        Transform(in_bit, random.choice(bits)),
                        FadeOut(in_bit),
                    )
                    for in_bit in in_bits
                ],
                lag_ratio=3 / len(in_bits),
                run_time=12,
            ),
            GrowArrow(in_arrow),
        )
        self.wait()

        # Pi Creature
        randy = Randolph()
        randy.set_height(1.5)
        randy.to_edge(DOWN)
        randy.shift(2 * LEFT)

        self.play(FadeIn(randy))
        self.play(randy.change, "maybe")
        self.play(Blink(randy))
        self.play(randy.change, "confused")
        self.wait(2)
        self.play(Blink(randy))
        self.wait()


class TripleRedundancy(Scene):
    def construct(self):
        # Show different file types
        image = ImageMobject("Claude_Shannon")
        image.set_height(6)
        image.to_edge(DOWN)
        video = ImageMobject("ZoeyInGrass")
        video.set_opacity(0)
        sound = get_sound_wave()
        text = TextMobject(
            """
            Fourscore and seven years ago\\\\
            our fathers brought forth, on this\\\\
            continent, a new nation, conceived\\\\
            in liberty, and dedicated to the\\\\
            proposition that all men are created\\\\
            equal. Now we are engaged$\\dots$
            """,
            alignment=""
        )
        code = ImageMobject("Hamming_Code_Snippet")
        files = Group(video, sound, text, code, image)
        for file in files:
            file.match_width(image)
            file.move_to(image, UP)

        brace = Brace(image, UP)
        file_word = TextMobject("Original File")
        file_word.set_height(0.5)
        file_word.next_to(brace, UP)

        self.play(
            GrowFromCenter(brace),
            FadeIn(file_word),
            image_reveal_animation(video),
        )
        video.set_opacity(0)
        self.wait(2)
        for f1, f2 in zip(files, files[1:]):
            self.play(FadeOut(f1), FadeIn(f2))
            self.wait()

        # Show bits
        bits = get_image_bits(image)
        for bit, value in zip(bits, string_to_bits(";)Hi")):
            bit[1 - value].set_opacity(0)
            bit[value].set_opacity(1)
        bits.generate_target()
        bits.target.arrange(RIGHT)
        bits.target.set_height(0.5)
        bits.target.arrange(RIGHT, buff=SMALL_BUFF)
        bits.target.to_edge(LEFT)
        bits.target.shift(UP)
        last_shown_bit_index = 31
        dots = TextMobject("\\dots")
        dots.next_to(bits.target[last_shown_bit_index], RIGHT, aligned_edge=DOWN, buff=SMALL_BUFF)
        new_brace = Brace(VGroup(bits.target[0], dots), UP)
        file_rect = SurroundingRectangle(VGroup(bits.target[0], dots))
        file_rect.set_stroke(BLUE, 4)

        self.play(
            FadeOut(image),
            FadeIn(bits, lag_ratio=1 / len(bits))
        )
        self.play(
            MoveToTarget(bits),
            Transform(brace, new_brace),
            file_word.next_to, new_brace, UP, SMALL_BUFF,
            run_time=3,
        )
        self.play(
            FadeOut(bits[last_shown_bit_index + 1:last_shown_bit_index + 5]),
            FadeIn(dots),
            FadeOut(brace),
            FadeIn(file_rect),
            file_word.next_to, file_rect, UP,
        )
        self.remove(*bits[last_shown_bit_index + 1:])
        bits.remove(*bits[last_shown_bit_index + 1:])
        self.add(bits)
        self.wait()

        # Show redundant copies
        bits.add(dots)
        copies = VGroup(bits.copy(), bits.copy())
        copies.arrange(DOWN, buff=MED_SMALL_BUFF)
        copies.next_to(bits, DOWN, buff=MED_SMALL_BUFF)
        copies.set_color(BLUE)
        copies_rect = SurroundingRectangle(copies, buff=SMALL_BUFF)
        copies_rect.set_stroke(BLUE_E, 4)
        copies_word = TextMobject("Redundant copies")
        copies_word.scale(file_word[0][0].get_height() / copies_word[0][0].get_height())
        copies_word.match_color(copies)
        copies_word.next_to(copies_rect, DOWN)

        self.play(LaggedStart(*[
            TransformFromCopy(bits, bits_copy)
            for bits_copy in copies
        ], lag_ratio=0.5))
        self.play(
            ShowCreation(copies_rect),
            FadeIn(copies_word, UP),
            copies.set_color, WHITE,
        )
        self.wait()

        # Show a correction
        flipper_index = 7
        flipper = bits[flipper_index]
        self.play(
            zap_anim(flipper),
            toggle_bit_anim(flipper),
        )
        self.play()
        self.wait()

        bit_groups = [bits, *copies]
        scan_rect = SurroundingRectangle(
            VGroup(*[group[0] for group in bit_groups])
        )
        scan_rect.set_stroke(GREEN, 5)

        self.add(scan_rect)
        for i in range(flipper_index + 1):
            self.play(
                scan_rect.match_x, bits[i],
                run_time=0.25
            )
            self.wait(0.25)

        bangs = TextMobject("!!!")[0]
        bangs.scale(1.5)
        bangs.set_color(RED)
        bangs.next_to(scan_rect, UP)

        self.play(
            LaggedStartMap(
                FadeIn, bangs,
                lambda m: (m, DOWN),
                run_time=1,
            ),
            scan_rect.set_color, RED
        )
        self.wait()

        flipper_rect = SurroundingRectangle(flipper, buff=SMALL_BUFF)
        flipper_rect.set_stroke(GREEN, 4)
        flipper_rect.set_fill(GREEN, 0.5)
        bangs.unlock_triangulation()
        self.play(
            ReplacementTransform(bangs, flipper_rect)
        )
        self.play(
            toggle_bit_anim(flipper),
            FadeOut(flipper_rect),
            scan_rect.set_color, GREEN,
        )

        for i in range(flipper_index + 1, flipper_index + 5):
            self.play(
                scan_rect.match_x, bits[i],
                run_time=0.25
            )
            self.wait(0.25)
        self.play(FadeOut(scan_rect, 0.2 * RIGHT, run_time=0.5))

        # Show 2/3 of transmission block
        rects = VGroup(file_rect, copies_rect)
        rects.generate_target()
        for rect, width in zip(rects.target, [1, 2]):
            rect.set_width(width, stretch=True)
            rect.set_height(0.75, stretch=True)
            rect.set_fill(rect.get_stroke_color(), opacity=1)
        rects.target[0].set_color(BLUE)
        rects.target[1].set_color(BLUE_E)
        rects.target.set_stroke(width=0)
        rects.target.arrange(RIGHT, buff=0)
        rects.target.set_width(12, stretch=True)
        rects.target.move_to(UP)

        braces = VGroup(*[Brace(rect, UP, buff=SMALL_BUFF) for rect in rects.target])

        frac_labels = VGroup(*[
            DecimalNumber(100 * frac, unit="\\%", num_decimal_places=1)
            for frac in [1 / 3, 2 / 3]
        ])
        for rect, label in zip(rects.target, frac_labels):
            label.move_to(rect)

        copies_word.unlock_triangulation()
        redundancy_word = TextMobject("Redundancy")
        redundancy_word.match_height(copies_word)
        redundancy_word.match_color(copies_word)
        redundancy_word.next_to(braces[1], UP, SMALL_BUFF)

        self.play(
            bits.replace, rects.target[0], {"stretch": True},
            bits.set_opacity, 0,
            copies.replace, rects.target[1], {"stretch": True},
            copies.set_opacity, 0,
            MoveToTarget(rects),
            LaggedStartMap(GrowFromCenter, braces),
            file_word.next_to, braces[0], UP, SMALL_BUFF,
            ReplacementTransform(copies_word, redundancy_word),
            run_time=2,
        )
        self.play(Write(frac_labels))
        self.wait()

        # Show failure for some two-bit errors
        bits = get_bit_grid(3, 1, [0, 0, 0], height=3, buff=SMALL_BUFF)
        bits.next_to(rects, DOWN, buff=MED_LARGE_BUFF)

        self.play(FadeIn(bits))
        self.play(
            LaggedStart(zap_anim(bits[0]), zap_anim(bits[2]), lag_ratio=0.5),
            LaggedStart(toggle_bit_anim(bits[0]), toggle_bit_anim(bits[2]), lag_ratio=0.5),
            run_time=1.5,
        )
        self.wait()
        self.play(FadeOut(bits))

        # Shrink bars
        rects.generate_target()
        p = 9 / 256
        rects.target[0].set_width(1 - p, stretch=True)
        rects.target[1].set_width(p, stretch=True)
        rects.target.arrange(RIGHT, buff=0)
        rects.target.match_width(rects, stretch=True)
        rects.target.move_to(rects)

        braces.generate_target()
        for rect, brace in zip(rects.target, braces.target):
            brace.become(Brace(rect, UP, buff=SMALL_BUFF, min_num_quads=1))

        f_always(frac_labels[0].move_to, rects[0].get_center)
        f_always(frac_labels[1].move_to, rects[1].get_center)
        rl_width = frac_labels[1].get_width()
        f_always(frac_labels[1].set_width, lambda: min(0.95 * rects[1].get_width(), rl_width))

        self.play(
            MoveToTarget(rects),
            MoveToTarget(braces),
            ChangeDecimalToValue(frac_labels[0], 100 * (1 - p)),
            ChangeDecimalToValue(frac_labels[1], 100 * p),
            file_word.next_to, braces.target[0], UP, SMALL_BUFF,
            redundancy_word.next_to, braces.target[1], UP, SMALL_BUFF,
            redundancy_word.to_edge, RIGHT,
            run_time=3,
        )
        self.wait()

        ratio_group = VGroup(rects, braces, frac_labels, file_word, redundancy_word)
        ratio_group.clear_updaters()

        # Show space division for a (256, 247) Hamming code
        bits = get_bit_grid(
            16, 16,
            bits=string_to_bits("There are 10 kinds of people...."),
            buff=0.2, height=5
        )
        bits.to_edge(DOWN, buff=MED_SMALL_BUFF)
        bits.shift(2 * LEFT)
        ecc_bits = bits[-9:]
        ecc_rect = SurroundingRectangle(ecc_bits, buff=0.05)
        ecc_rect.set_stroke(BLUE_E, 2)
        ecc_rect.set_fill(BLUE_E, 0.5)

        block_label = TextMobject("256 bit block")
        ecc_label = TextMobject("9 redundancy bits")
        message_label = TextMobject("247 message bits")

        block_label.next_to(bits, RIGHT, LARGE_BUFF)
        block_label.shift(UP)
        ecc_label.next_to(ecc_bits, RIGHT, LARGE_BUFF)
        ecc_label.to_edge(DOWN, buff=MED_SMALL_BUFF)
        ecc_label.set_color(BLUE)
        message_label.move_to(VGroup(block_label, ecc_label))
        message_label.align_to(block_label, LEFT)
        message_label.set_color(YELLOW)

        self.play(
            ratio_group.to_edge, UP,
            LaggedStartMap(FadeIn, bits, lag_ratio=1 / len(bits)),
            Write(block_label),
        )
        self.wait()
        self.play(
            ReplacementTransform(
                SurroundingRectangle(bits, color=BLUE, stroke_opacity=0),
                ecc_rect
            ),
            Write(ecc_label)
        )
        self.wait()
        self.play(
            LaggedStartMap(
                VFadeInThenOut,
                bits[:-9].copy().set_fill(color=YELLOW),
                lag_ratio=0.1 / len(bits),
                run_time=3,
            ),
            Write(message_label),
        )
        self.wait()

        # Show correction
        flipper = random.choice(bits)

        self.play(
            zap_anim(flipper),
            toggle_bit_anim(flipper),
        )
        self.play(flipper.set_color, RED)

        point = bits.get_corner(DL) + 1.5 * LEFT + UP
        scanim = scan_anim(point, bits, final_stroke_width=0.2)
        lines, robot = scanim.mobject

        self.play(scanim)
        self.play(*[
            Succession(
                ApplyMethod(line.put_start_and_end_on, point, flipper.get_center()),
                ApplyMethod(line.set_stroke, None, 1)
            )
            for line in lines
        ])
        self.play(
            toggle_bit_anim(flipper),
            FadeOut(lines),
            FadeOut(robot),
        )
        self.play(flipper.set_color, WHITE)

        # Show two errors
        two_error_label = TextMobject("Two errors")
        two_error_label.next_to(bits, LEFT, buff=MED_LARGE_BUFF, aligned_edge=UP)
        two_error_label.set_color(RED)

        flippers = VGroup(*random.sample(list(bits), 2))

        self.play(
            FadeIn(two_error_label),
            LaggedStart(*[zap_anim(f) for f in flippers], lag_ratio=0.5),
            LaggedStartMap(toggle_bit_anim, flippers, lag_ratio=0.5),
        )
        self.play(flippers.set_color, RED)
        self.wait()

        scanim = scan_anim(point, bits, final_stroke_width=0.2)
        bangs = TextMobject("!!!")[0]
        bangs.set_color(RED)
        bangs.next_to(point, UL, SMALL_BUFF)
        q_marks = TextMobject("???")[0]
        q_marks.replace(bangs, dim_to_match=1)
        q_marks.match_style(bangs)

        self.play(scanim)
        self.play(
            LaggedStartMap(
                FadeIn, bangs,
                lambda m: (m, 0.25 * DOWN),
                lag_ratio=0.2,
                run_time=1,
            ),
        )
        self.wait()
        bangs.unlock_triangulation()
        self.play(ReplacementTransform(bangs, q_marks, lag_ratio=0.2))
        self.wait()


class TimeLine(Scene):
    def construct(self):
        # Time line
        decades = list(range(1920, 2030, 10))
        timeline = NumberLine(
            (decades[0], decades[-1], 2),
            numbers_with_elongated_ticks=decades,
            width=13
        )
        timeline.add_numbers(
            decades,
            number_config={
                "group_with_commas": False,
                "height": 0.2,
            }
        )
        timeline.numbers.set_stroke(BLACK, 4, background=True)

        # Events
        def get_event(timeline, date, words, direction=UP):
            arrow = Vector(-direction)
            arrow.set_fill(GREY_A, 0.75)
            arrow.shift(timeline.n2p(date) - arrow.get_end())
            arrow.shift(SMALL_BUFF * direction)

            label = TextMobject(words)
            label.scale(0.7)
            label.next_to(arrow.get_start(), np.sign(direction[1]) * UP, SMALL_BUFF)
            label.set_color(GREY_A)
            label.set_stroke(BLACK, 4, background=True)

            event = VGroup(label, arrow)
            return event

        events = VGroup(
            get_event(timeline, 1947, "Hamming codes", 1.5 * UP),
            get_event(timeline, 1948, "Shannon's paper\\\\on information theory", DOWN + 0.2 * LEFT),
            # get_event(timeline, 1949, "Gorlay codes", 0.7 * UP),
            get_event(timeline, 1960, "Reed-Solomon\\\\codes", 0.7 * UP),
            get_event(timeline, 1993, "Turbo codes", UP),
            get_event(timeline, 1995, "Shor codes\\\\(quantum)", DOWN),
        )

        # Title
        title = TextMobject("Error correction codes")
        title.set_color(YELLOW)
        title.set_height(0.5)
        title.to_edge(UP)
        title_underline = Underline(title)
        title_underline.match_color(title)
        title.add(title_underline)
        title.fix_in_frame()

        # Introduce time line
        frame = self.camera.frame
        frame.save_state()
        frame.scale(0.5, about_point=timeline.n2p(1945))
        frame.shift(0.5 * UP)

        self.play(
            Write(timeline),
            Write(timeline.numbers.copy(), remover=True),
            LaggedStart(
                *[Animation(Mobject()) for x in range(1)],
                *[
                    AnimationGroup(
                        Write(event[0], run_time=1),
                        GrowArrow(event[1]),
                    )
                    for event in events
                ],
                lag_ratio=0.75,
            ),
            FadeIn(title, DOWN),
            Restore(frame, run_time=6),
        )
        self.wait(2)

        # Isolate Hamming
        hamming_word = events[0][0]
        rs_word = events[2][0]
        self.play(
            hamming_word.scale, 2, {"about_edge": DL},
            hamming_word.set_fill, WHITE,
            LaggedStart(*[
                ApplyMethod(mob.set_opacity, 0.5)
                for mob in events[1:]
            ]),
            FadeOut(VGroup(title, title_underline))
        )

        invent_words = TextMobject("How to invent")
        invent_words.match_height(hamming_word[0][0])
        invent_words.next_to(events[0], UP, buff=0.3)
        invent_words.set_color(BLUE)

        self.play(Write(invent_words))
        self.wait()

        hamming_word.generate_target()
        hamming_word.target.scale(0.5, about_edge=UL)
        hamming_word.target.set_opacity(0.5)
        hamming_arrow = events[0][1]

        self.play(
            MoveToTarget(hamming_word),
            FadeOut(invent_words),
            hamming_arrow.put_start_and_end_on, hamming_word.target.get_bottom(), hamming_arrow.get_end(),
            hamming_arrow.set_opacity, 0.5,
            rs_word.scale, 1.5, {"about_edge": DOWN},
            rs_word.set_opacity, 1,
            events[2][1].set_opacity, 1,
        )
        self.wait()


class WhatCDsActuallyUse(Scene):
    def construct(self):
        arrow = Vector(2 * RIGHT + UP)
        words = TextMobject("What CDs/DVDs\\\\actually use")
        words.next_to(arrow.get_end(), RIGHT)
        arrow.set_color(YELLOW)
        words.set_color(YELLOW)

        self.play(
            GrowFromPoint(words, arrow.get_start()),
            GrowArrow(arrow)
        )
        self.wait()


class ListOfRelevantMathTopics(Scene):
    def construct(self):
        topics = VGroup(
            TextMobject("$L^1$ norm"),
            TextMobject("Sphere packing"),
            TextMobject("Finite sporadic groups (see Golay codes)"),
            TextMobject("Finite fields"),
            TextMobject("Galois extensions"),
            TextMobject("Lagrange interpolation (see Reed-Solomon)"),
            TextMobject("Discrete Fourier Transform"),
            TexMobject("\\dots")
        )
        topics.arrange(RIGHT, buff=LARGE_BUFF)
        brown = interpolate_color(GREY_BROWN, WHITE, 0.25)
        for topic, color in zip(topics, it.cycle([BLUE_C, BLUE_D, BLUE_B, brown])):
            topic.set_color(color)

        topics.move_to(ORIGIN, LEFT)
        topics.to_edge(UP)
        self.play(topics.shift, (topics.get_width() - 5) * LEFT, run_time=12)
        self.wait()


class Reinvention(TeacherStudentsScene):
    def construct(self):
        self.play(
            self.teacher.change, "raise_right_hand",
            self.get_student_changes(*3 * ["pondering"]),
        )
        self.wait(3)
        self.student_says(
            "I see where\\\\this is going",
            student_index=0,
            target_mode="tease",
        )
        self.look_at(self.students[0].bubble)
        self.play(self.students[0].change, "thinking")
        self.wait(6)


class EaterWrapper(Scene):
    def construct(self):
        bg_rect = FullScreenRectangle()
        bg_rect.set_fill(GREY_E, 1)
        bg_rect.set_stroke(BLACK, 0)
        self.add(bg_rect)

        title = TextMobject("Ben Eater implementing Hamming codes")
        title.set_width(FRAME_WIDTH - 2)
        title.to_edge(UP)
        self.add(title)

        screen_rect = ScreenRectangle()
        screen_rect.set_fill(BLACK, 1)
        screen_rect.set_height(6)
        screen_rect.next_to(title, DOWN, MED_LARGE_BUFF)
        self.add(screen_rect)

        self.add(AnimatedBoundary(screen_rect))
        self.wait(16)


class DataGettingZapped(Scene):
    CONFIG = {
        "random_seed": 1,
    }

    def construct(self):
        # Setup bit array
        # bits = get_bit_grid(50, 100)
        bits = get_bit_grid(25, 50)
        bits.set_color(GREY_B)
        bits.set_height(FRAME_HEIGHT - 0.25)

        image = ImageMobject("LowResMandelbrot")
        image.replace(bits, dim_to_match=0)

        threshold = 0.1
        for bit in bits:
            try:
                rgb = image.point_to_rgb(bit.get_center())
                if get_norm(rgb) > threshold:
                    value = 1
                else:
                    value = 0
                bit[value].set_opacity(1)
                bit[1 - value].set_opacity(0)
            except Exception:
                pass

        self.add(bits)

        # Zippity zap
        bolt = SVGMobject("lightning_bolt")
        bolt[0].add_line_to(bolt[0].get_start())
        bolt.set_fill(RED_B, 1)
        bolt.set_stroke(width=0)
        bolt.set_height(0.5)

        def strike_anim(bit, bolt=bolt, **kwargs):
            bolt = bolt.copy()
            bolt.move_to(bit.get_center(), DL)
            bits.remove(bit)
            bit.generate_target()
            bit.target.set_color(RED)
            bit.target.set_stroke(RED, 1)
            for sm in bit.target:
                sm.set_opacity(1 - sm.get_fill_opacity())

            outline = bolt.deepcopy()
            outline.set_stroke(RED_D, 2)
            outline.set_fill(opacity=0)

            return AnimationGroup(
                Succession(
                    GrowFromPoint(bolt, bolt.get_corner(UR), rate_func=rush_into),
                    FadeOut(bolt, run_time=0.5),
                ),
                Succession(
                    ShowCreation(outline),
                    FadeOut(outline),
                ),
                MoveToTarget(bit),
            )

        for count in range(20):
            self.play(LaggedStart(*[
                strike_anim(random.choice(bits))
                for x in range(int(random.expovariate(0.5)) + 1)
            ], lag_ratio=0.25))
            self.wait(random.expovariate(2))


class AmbientErrorCorrection(Scene):
    CONFIG = {
        "N": 8,
        "bit_grid_height": 7,
    }

    def construct(self):
        N = self.N
        size = (2**(N // 2), 2**(N // 2))
        bits = get_bit_grid(
            *size,
            bits=string_to_bits("Claude Shannon was a total boss!"),
            height=self.bit_grid_height,
        )
        bits.move_to(2 * RIGHT)
        point = 2.5 * LEFT + 2.5 * DOWN
        last_block = VMobject()

        for x in range(10):
            block = get_bit_grid(*size, height=self.bit_grid_height)
            block.move_to(2 * RIGHT)
            syndrome = hamming_syndrome(bit_grid_to_bits(block))

            if random.random() < 0.5:
                syndrome = 0
                toggle_bit(block[syndrome])

            scanim = scan_anim(
                point, bits,
                final_stroke_width=0.2, run_time=3, lag_factor=1,
                show_robot=(x == 0),
            )
            self.play(
                FadeIn(block, 6 * RIGHT),
                FadeOut(last_block, 6 * LEFT),
                run_time=2
            )
            self.play(scanim, run_time=1)
            if syndrome:
                flipper = block[syndrome]
                bangs = TexMobject("!!!")
                bangs.scale(2)
                bangs.next_to(point, UL)
                bangs.set_color(RED)
                self.play(
                    Write(bangs, run_time=0.5),
                    focus_scan_anim_lines(scanim, flipper.get_center()),
                    flipper.set_color, RED,
                )
                self.play(
                    toggle_bit_anim(flipper, target_color=WHITE),
                    ApplyMethod(scanim.mobject[0].set_stroke, None, 0, 0, remover=True),
                    FadeOut(bangs),
                )
            else:
                check = Checkmark()
                check.scale(2)
                check.next_to(point, UL)
                self.play(FadeIn(check, 0.5 * DOWN))
                self.play(FadeOut(check), FadeOut(scanim.mobject[0]))
            last_block = block


class AmbientErrorCorrection6(AmbientErrorCorrection):
    CONFIG = {
        "N": 6
    }


class AmbientErrorCorrection4(AmbientErrorCorrection):
    CONFIG = {
        "N": 4,
        "bit_grid_height": 5,
    }


class ImpossibleToReasonable(Scene):
    def construct(self):
        group = VGroup(
            TextMobject("Impossible"),
            Vector(RIGHT, color=GREY_B),
            TextMobject("Utterly reasonable"),
        )
        group.arrange(RIGHT)
        group.scale(1.5)
        group.to_edge(UP)

        line = Line(LEFT, RIGHT)
        line.set_width(FRAME_WIDTH)
        line.set_stroke(GREY, 2)
        line.next_to(group, DOWN, SMALL_BUFF)
        self.add(line)

        self.play(FadeIn(group[0], 0.5 * UP))
        self.wait()
        self.play(
            GrowArrow(group[1]),
            FadeIn(group[2], LEFT),
        )
        self.wait()


class HammingAtBell(Scene):
    def construct(self):
        # Setup
        hamming_image = ImageMobject("Richard_Hamming")
        hamming_name = TextMobject("Richard Hamming")
        hamming_name.match_width(hamming_image)
        hamming_name.next_to(hamming_image, DOWN, MED_SMALL_BUFF)
        hamming = Group(hamming_image, hamming_name)
        hamming.to_corner(DR)
        hamming.shift(2 * LEFT)

        bell_logo = ImageMobject("BellSystemLogo")
        bell_logo.set_height(3)
        bell_logo.next_to(hamming, LEFT, buff=2)
        bell_logo.to_edge(UP)

        bell_logo_outline = SVGMobject("BellSystemLogo")
        bell_logo_outline.match_height(bell_logo)
        bell_logo_outline.set_stroke(GREY_B, 1)
        bell_logo_outline.set_fill(BLACK, 0)
        bell_logo_outline.move_to(bell_logo)

        punchcard = SVGMobject("punchcard")
        punchcard.set_stroke(width=0)
        punchcard.set_fill(GREY_B, 1)
        punchcard.next_to(bell_logo, DOWN, LARGE_BUFF)
        punchcard.remove(*punchcard[23:])

        years = TextMobject("1940s")
        years.scale(2)
        years.to_edge(UP)

        # Introductions
        self.play(Write(years))
        self.play(FadeIn(hamming[0], RIGHT))
        self.play(Write(hamming[1]))
        self.play(
            FadeOut(years),
            ShowCreationThenFadeOut(bell_logo_outline, lag_ratio=0.1, run_time=4),
            FadeIn(bell_logo, run_time=3),
        )

        self.play(
            FadeIn(punchcard[0]),
            Write(punchcard[1:], lag_ratio=0.5, run_time=4)
        )
        self.add(punchcard)
        self.wait()

        # Zap some bits
        random.seed(3)
        bits = random.sample(list(punchcard[1:]), 4)
        for bit in bits:
            bit.generate_target()
            bit.target.set_color(RED)
            if random.random() < 0.5:
                bit.target.stretch(0.2, 1, about_edge=DOWN)
            else:
                bit.target.shift(1.2 * bit.get_width() * LEFT)
            self.play(
                MoveToTarget(bit),
                zap_anim(bit)
            )
        self.wait()

        # Frustration
        curse = TextMobject("\\$*@\\#*!!?!")[0]
        curse.set_color(RED)
        curse.next_to(hamming, UP)

        self.play(ShowIncreasingSubsets(curse))
        self.wait()


class MultiplePerspectives(Scene):
    def construct(self):
        # Background
        background = VGroup(*[
            Rectangle().set_fill(color, 1)
            for color in [GREY_E, BLACK, GREY_E]
        ])
        background.set_stroke(width=0)
        background.arrange(RIGHT, buff=0)
        background.set_height(FRAME_HEIGHT)
        background.set_width(FRAME_WIDTH, stretch=True)
        self.add(background)

        # Names
        names = VGroup(
            TextMobject("Parity checks"),
            TextMobject("Xor of indices"),
            TextMobject("Matrix"),
        )

        names.set_height(0.6)
        for name, rect in zip(names, background):
            name.match_x(rect)
        names[0].shift(SMALL_BUFF * DOWN)
        names.to_edge(DOWN, buff=1)

        # Objects
        parity_groups = VGroup()
        for n in range(4):
            pg = VGroup(*[Square() for x in range(16)])
            pg.arrange_in_grid(4, 4, buff=0)
            pg.set_height(0.7)
            pg.set_stroke(GREY_A, 2)
            get_bit_n_subgroup(pg, n).set_fill(BLUE, 0.8)
            parity_groups.add(pg)
        parity_groups.arrange_in_grid(2, 2)

        code = ImageMobject("Hamming_Code_Snippet")

        ints = list(random.sample(list(range(16)), 4))
        ints.sort()
        xor_sum = reduce(op.xor, ints)
        bits = [int_to_bit_string(n, n_bits=4) for n in [*ints, xor_sum]]
        column = Group(*map(TextMobject, bits))
        column.arrange(DOWN, SMALL_BUFF)
        column[-1].set_color(YELLOW)
        column[-1].shift(MED_SMALL_BUFF * DOWN)
        line = Line(LEFT, RIGHT)
        line.set_stroke(GREY_B)
        line.set_width(column.get_width() + 0.75)
        line.move_to(column[-2:], RIGHT)
        xor = get_xor()
        xor.next_to(line, UP, SMALL_BUFF, LEFT)
        column.add(line, xor)
        code.set_width(2 * column.get_width())
        code.next_to(column, UP)
        column.add(code)

        matrix = IntegerMatrix(
            [
               [1, 1, 0, 1],
               [1, 0, 1, 1],
               [1, 0, 0, 0],
               [0, 1, 1, 1],
               [0, 1, 0, 0],
               [0, 0, 1, 0],
               [0, 0, 0, 1],
            ],
            v_buff=0.6,
            h_buff=0.75,
        )

        objs = Group(parity_groups, column, matrix)

        for name, obj in zip(names, objs):
            obj.match_width(names[0])
            obj.next_to(name, UP, LARGE_BUFF)
        matrix.scale(0.7, about_edge=DOWN)

        # Introduce
        anims = []
        for name, obj in zip(names, objs):
            anims.append(AnimationGroup(
                FadeIn(name, 0.25 * UP),
                FadeIn(obj, lag_ratio=0, run_time=2),
            ))
        self.play(LaggedStart(*anims, lag_ratio=0.4))
        self.wait()
        for name, obj in zip(names, objs):
            obj.add(name)
        self.add(background[0])
        self.play(
            FadeOut(background),
            objs[0].set_x, 0,
            FadeOut(objs[1], 5 * RIGHT),
            FadeOut(objs[2], 2 * RIGHT),
            run_time=2
        )
        self.wait()


class SetupSixteenBitExample(Scene):
    def construct(self):
        # Title
        title = TextMobject("Reinventing Hamming Codes")
        title.scale(1.5)
        title.to_edge(UP)
        title.set_color(BLUE)
        self.play(Write(title))

        # Simple but not too simple
        block = get_bit_grid(4, 4, bits=string_to_bits(":)"))
        block.move_to(0.5 * DOWN)
        top_row = block[:4]
        top_row.save_state()
        top_row.center()

        simple_words = TextMobject("Simple\\\\", "but not too\\\\simple")
        simple_words.scale(1.5)
        simple_words.next_to(block[4:12], LEFT, buff=LARGE_BUFF)
        top_simp = simple_words[0]
        top_simp.save_state()
        top_simp.set_y(0)

        self.play(
            FadeIn(top_simp),
            ShowIncreasingSubsets(top_row),
        )
        self.play(
            Restore(top_simp),
            Restore(top_row),
            FadeIn(simple_words[1:]),
            LaggedStartMap(FadeIn, block[4:])
        )
        self.add(block)
        self.add(simple_words)

        boxes = get_bit_grid_boxes(block, color=GREEN)
        bits_word = TextMobject("bits")
        bits_word.set_height(0.7)
        bits_word.next_to(boxes, LEFT, buff=LARGE_BUFF)
        counter = Integer(0, edge_to_fix=RIGHT)
        counter.match_height(bits_word)
        counter.next_to(bits_word, LEFT, buff=0.35)
        bit_count_group = VGroup(bits_word, counter)
        bit_count_group.set_color(YELLOW)

        self.play(
            FadeOut(simple_words),
            FadeIn(bits_word),
            UpdateFromAlphaFunc(
                counter,
                lambda m, a: m.set_fill(opacity=a)
            ),
            UpdateFromFunc(
                counter,
                lambda c: c.set_value(len(boxes))
            ),
            ShowIncreasingSubsets(boxes, run_time=2)
        )

        # Enumerate bits
        block.generate_target()
        block.target.space_out_submobjects(1.5)
        block.target.center()

        new_boxes = get_bit_grid_boxes(block.target, color=GREY_B)
        h_buff = get_norm(block.target[0].get_center() - block.target[4].get_center())
        for box in new_boxes:
            box.set_height(h_buff, stretch=True)

        p_labels = VGroup()
        for n, box in enumerate(new_boxes):
            label = Integer(n)
            label.set_height(0.25)
            label.set_color(YELLOW)
            label.move_to(box, DR)
            label.shift(SMALL_BUFF * UL)
            p_labels.add(label)

        self.play(
            MoveToTarget(block),
            Transform(boxes, new_boxes),
            FadeOut(title, UP),
            FadeOut(VGroup(counter, bits_word), LEFT),
        )
        self.play(FadeIn(p_labels, lag_ratio=0.07, run_time=3))
        self.wait()

        # Data bits
        r_boxes = VGroup(*[boxes[2**n] for n in range(4)]).copy()
        r_bits = VGroup(*[block[2**n] for n in range(4)])
        d_bits = VGroup(*[b for b in block if b not in r_bits])

        d_label = TextMobject("12 bits\\\\of data")
        d_label.set_height(1.5)
        d_label.next_to(boxes, RIGHT, aligned_edge=UP, buff=LARGE_BUFF)
        d_label.set_color(BLUE)

        d_lines = VGroup(*[
            Line(
                d_label.get_left(), bit.get_center(),
                color=(TEAL if get_bit_mob_value(bit) else YELLOW)
            )
            for bit in d_bits
        ])
        d_lines.set_stroke(width=1)

        self.play(
            FadeOut(r_bits),
            d_bits.set_color, BLUE,
            FadeIn(d_label),
            p_labels.set_color, WHITE,
        )
        self.play(LaggedStartMap(ShowCreationThenFadeOut, d_lines))
        self.wait()

        # Redundancy bits
        r_label = TextMobject("4 bits for\\\\", "redundancy")
        r_label.match_height(d_label)
        r_label.next_to(boxes, LEFT, aligned_edge=UP, buff=MED_LARGE_BUFF)
        r_label.set_color(GREEN)

        r_boxes.set_fill(GREEN, 0.5)
        self.add(r_boxes, p_labels)
        self.play(
            FadeIn(r_label, 0.2 * RIGHT),
            LaggedStartMap(FadeIn, r_boxes, run_time=2)
        )
        self.wait()

        # Can't cram in copies
        d_bit_copies = d_bits.copy()
        d_bit_copies.generate_target()
        for n, box in enumerate(r_boxes):
            group = d_bit_copies.target[3 * n:3 * (n + 1)]
            group.arrange_in_grid(2, 2, buff=SMALL_BUFF)
            group.set_width(0.4 * box.get_width())
            group.move_to(box)
            group.set_color(YELLOW)

        self.play(ShowCreationThenDestruction(Underline(r_label[1])))
        self.play(MoveToTarget(d_bit_copies, lag_ratio=0.1, run_time=4, rate_func=linear))
        self.wait()
        self.play(
            UpdateFromAlphaFunc(
                d_bit_copies, lambda m, a: m.shift(0.03 * np.sin(7 * TAU * a) * RIGHT).fade(a),
                remover=True
            )
        )

        # Set true redundancy bits
        highlights = boxes.copy()
        highlights.set_stroke(YELLOW, 6)

        for n in range(4):
            h_group = get_bit_n_subgroup(highlights, n)
            bit = r_bits[n]
            if get_bit_mob_value(bit) == 1:
                toggle_bit(bit)

            self.play(
                FadeIn(h_group, lag_ratio=0.2),
                FadeIn(bit)
            )
            anims = [FadeOut(h_group)]
            if n in [2, 3]:
                anims.append(toggle_bit_anim(bit))
            self.play(*anims)

        # Might expect them to come at the end
        movers = [d_bits, r_bits]
        for mover in movers:
            mover.save_state()
            mover.generate_target()

        for b1, b2 in zip(it.chain(d_bits.target, r_bits.target), block):
            b1.move_to(b2)

        for box, bit in zip(r_boxes, r_bits):
            box.bit = bit
            box.add_updater(lambda m: m.move_to(m.bit))

        self.add(*r_boxes)
        self.play(
            *[
                MoveToTarget(mover, lag_ratio=0.1, run_time=3, path_arc=20 * DEGREES)
                for mover in movers
            ],
        )
        self.wait()

        self.play(*[
            Restore(mover, lag_ratio=0.1, run_time=3, path_arc=20 * DEGREES)
            for mover in movers
        ])
        r_boxes.clear_updaters()
        self.wait()

        power_of_2_rects = VGroup(*[
            SurroundingRectangle(p_labels[2**n])
            for n in range(4)
        ])
        self.play(LaggedStartMap(ShowCreationThenFadeOut, power_of_2_rects))

        # Correct to 11 bits
        cross = Cross(d_label[0][:2])
        c_label = TextMobject("Er...11 bits")
        c_label.match_width(d_label)
        c_label.next_to(d_label, DOWN, buff=MED_LARGE_BUFF)
        c_label.set_color(RED)
        q_mark = TexMobject("?")
        q_mark.replace(block[0])
        q_mark.set_color(RED)

        self.play(ShowCreation(cross))
        self.play(Write(c_label))
        self.wait()
        self.play(
            FadeOut(block[0]),
            Write(q_mark),
        )

        randy = Randolph()
        randy.to_corner(DL)

        self.play(
            VFadeIn(randy),
            randy.change, "confused", q_mark
        )
        self.play(Blink(randy))
        self.wait(2)
        self.play(Blink(randy))
        self.wait()

    def old_functions(self):
        # Show redundancy and message
        redundancy_words = TextMobject("Separate some for\\\\redundancy")
        redundancy_words.next_to(block[-4:], LEFT, buff=LARGE_BUFF, aligned_edge=UP)
        redundancy_words.set_color(BLUE)

        vect = redundancy_words.get_center() - bit_count_group.get_center()
        self.play(
            FadeOut(bit_count_group, vect),
            FadeIn(redundancy_words, -vect),
            ApplyMethod(boxes[-4:].set_color, BLUE, lag_ratio=0.2),
            ApplyMethod(block[-4:].set_color, BLUE, lag_ratio=0.2),
        )
        self.wait()

        message_words = TextMobject("Leave the rest\\\\for a message")
        message_words.next_to(block[:-4], LEFT)
        message_words.match_x(redundancy_words)
        message_words.set_color(YELLOW)
        message_words.save_state()
        message_words.replace(redundancy_words)
        message_words.set_opacity(0)

        self.play(
            Restore(message_words),
            boxes[:-4].set_color, YELLOW,
        )
        for x in range(10):
            bits = list(block[:-4])
            random.shuffle(bits)
            for bit in bits:
                if random.random() < 0.5:
                    toggle_bit(bit)
                self.wait(0.2 / 12)
        self.wait()

        # Show correction
        flipper = random.choice(block)
        scanim = scan_anim(
            block.get_corner(DR) + 2 * RIGHT, block,
            final_stroke_width=0.5,
            lag_factor=1,
        )

        self.play(
            zap_anim(flipper),
            toggle_bit_anim(flipper, target_color=RED)
        )
        self.wait()
        self.play(scanim)
        self.play(focus_scan_anim_lines(scanim, flipper.get_center()))
        self.play(
            toggle_bit_anim(flipper, target_color=WHITE),
            FadeOut(scanim.mobject)
        )


class SenderReceiverDynamic(PiCreatureScene):
    def construct(self):
        # Sender and receiver
        sender_word = TextMobject("Sender")
        receiver_word = TextMobject("Receiver")
        words = VGroup(sender_word, receiver_word)
        words.scale(1.5)
        words.set_y(-2)
        sender_word.to_edge(LEFT)
        receiver_word.to_edge(RIGHT)

        sender, receiver = pis = self.pi_creatures
        for pi, word in zip(pis, words):
            pi.set_height(2)
            pi.next_to(word, UP)

        self.clear()
        for pi in pis:
            self.play(
                VFadeIn(pi),
                pi.change, "pondering", ORIGIN,
            )
        for word in words:
            self.play(Write(word, run_time=1))
        self.wait()

        # Message
        block = get_bit_grid(4, 4)
        block.set_height(1.5)
        block.next_to(pis[0].get_corner(UR), UR)

        self.play(
            sender.change, "raise_right_hand",
            FadeIn(block, DOWN, lag_ratio=0.01),
        )
        self.add(sender, block)
        block.save_state()
        self.play(
            block.move_to, sender,
            block.scale, 0.5,
            sender.change, "gracious", sender,
        )
        self.play(LaggedStart(
            ApplyMethod(block[1].set_color, GREEN),
            toggle_bit_anim(block[2], target_color=GREEN),
            ApplyMethod(block[4].set_color, GREEN),
            toggle_bit_anim(block[8], target_color=GREEN),
        ))
        self.wait()
        block.generate_target()
        block.target.scale(2)
        block.target.next_to(receiver, UL)
        self.play(
            MoveToTarget(block, run_time=3, path_arc=-30 * DEGREES),
            receiver.change, "tease", receiver.get_corner(UL) + UP,
            sender.change, "happy", receiver.get_corner(UL) + UP,
        )
        self.play(scan_anim(receiver.get_corner(UL), block, lag_factor=1, show_robot=False))
        self.wait()

        # Replace with machines
        underlines = VGroup(*[Underline(word) for word in words])
        underlines.set_color(YELLOW)
        servers = VGroup(*[SVGMobject("server_stack") for x in range(2)])
        servers.set_color(GREY)
        servers.set_stroke(BLACK, 2)
        servers.set_gloss(0.5)
        for server, pi in zip(servers, pis):
            server.move_to(pi)

        self.play(
            LaggedStartMap(ShowCreationThenFadeOut, underlines, lag_ratio=0.7),
            *[
                ApplyMethod(pi.change, "thinking", pi)
                for pi in pis
            ],
        )
        self.wait()
        self.play(
            *it.chain(*[
                [
                    pi.change, "horrified",
                    pi.shift, 2 * UP,
                    pi.set_opacity, 0
                ]
                for pi in pis
            ]),
            FadeIn(servers, 2 * DOWN)
        )
        self.remove(pis)

        bits_copy = block.copy()
        bits_copy.arrange(RIGHT, buff=SMALL_BUFF)
        bits_copy.set_width(0.7 * servers[1].get_width())
        bits_copy.move_to(servers[1], LEFT)
        bits_copy.shift(SMALL_BUFF * RIGHT)
        self.play(
            LaggedStart(*[
                TransformFromCopy(b1, b2)
                for b1, b2 in zip(block, bits_copy)
            ], run_time=3),
        )

        # Sent and received
        sent_block = block.copy()
        sent_block.next_to(servers[0], UR)
        sent_block.match_y(block)
        wire = VGroup(
            SurroundingRectangle(sent_block),
            Line(sent_block.get_right(), block.get_left(), buff=SMALL_BUFF / 2),
            SurroundingRectangle(block),
        )
        wire.set_stroke(GREY, 2)
        noise_word = TextMobject("Potential noise")
        noise_word.scale(0.75)
        noise_word.set_color(RED)
        noise_word.next_to(wire[1], UP, SMALL_BUFF)

        small_words = VGroup(
            TextMobject("sent"),
            TextMobject("received"),
        )
        for word, mob in zip(small_words, [sent_block, block]):
            word.next_to(mob, UP, buff=0.35)

        self.play(
            ShowCreation(wire[0]),
            FadeIn(small_words[0], 0.5 * DOWN),
            FadeIn(sent_block),
        )
        self.play(
            Transform(sent_block.copy(), block, remover=True, lag_ratio=0.01),
            ShowCreation(wire[1]),
            FadeIn(noise_word, lag_ratio=0.1)
        )
        self.play(
            ShowCreation(wire[2]),
            FadeIn(small_words[1], 0.5 * DOWN)
        )

        # Past and future
        cross_lines = VGroup(*[
            Line(
                word.get_left(), word.get_right(),
                stroke_width=5,
                stroke_color=RED,
            )
            for word in words
        ])
        time_words = VGroup(
            TextMobject("Past"),
            TextMobject("Future"),
        )
        time_words.set_color(BLUE)
        for w1, w2 in zip(words, time_words):
            w2.match_height(w1)
            w2.next_to(w1, DOWN)

        self.play(
            LaggedStartMap(ShowCreation, cross_lines, lag_ratio=0.7),
            LaggedStartMap(ApplyMethod, words, lambda m: (m.set_opacity, 0.75), lag_ratio=0.7),
            run_time=1,
        )
        self.play(
            LaggedStartMap(FadeIn, time_words, lambda m: (m, UP), lag_ratio=0.3)
        )
        self.wait(2)

    def create_pi_creatures(self):
        return VGroup(Randolph(), Mortimer())


class ParityChecks(Scene):
    def construct(self):
        # Show detection
        block = get_bit_grid(4, 4, bits=string_to_bits(":)"))
        block.move_to(3 * LEFT)
        point = block.get_corner(DR) + 2 * RIGHT + UP
        scanim = scan_anim(point, block, final_stroke_width=0.5, run_time=2, lag_factor=2)
        lines, robot = scanim.mobject
        detection_words = TextMobject("Error detected!")
        detection_words.set_color(RED)
        detection_subwords = TextMobject("But I have no idea where!")
        detection_words.next_to(robot.get_top(), UR, SMALL_BUFF)
        detection_subwords.move_to(detection_words, DL)

        self.add(block)
        self.play(scanim)
        self.play(
            GrowFromPoint(detection_words, robot.get_top())
        )
        self.wait()
        self.play(
            detection_words.shift, 0.75 * UP,
            FadeIn(detection_subwords, 0.5 * DOWN),
        )
        self.wait()

        title = TextMobject("Parity Check")[0]
        title.set_color(YELLOW)
        title.set_stroke(BLACK, 3, background=True)
        title.add(Underline(title).shift(0.05 * UP))
        title.scale(1.5)
        title.to_edge(UP)

        self.play(Write(title))
        self.wait()
        self.play(
            LaggedStart(
                FadeOut(scanim.mobject),
                FadeOut(detection_words),
                FadeOut(detection_subwords),
            ),
            block.move_to, DOWN,
        )

        # Single bit vs. message
        pb_rect = SurroundingRectangle(block[0])
        pb_rect.set_stroke(GREEN, 3)
        ms_rect = SurroundingRectangle(block)
        ms_blob = Polygon(
            pb_rect.get_corner(UR) + 0.05 * RIGHT,
            ms_rect.get_corner(UR),
            ms_rect.get_corner(DR),
            ms_rect.get_corner(DL),
            pb_rect.get_corner(DL) + 0.05 * DOWN,
            pb_rect.get_corner(DR) + 0.05 * DR,
        )
        ms_blob.set_stroke(BLUE, 3)

        pb_words = TextMobject("Reserve one special bit")
        pb_words.next_to(pb_rect, LEFT)
        pb_words.match_color(pb_rect)
        ms_words = TextMobject("The rest carry\\\\a message", alignment="")
        ms_words.next_to(ms_blob, RIGHT, aligned_edge=UP)
        ms_words.align_to(pb_words, UP)
        ms_words.match_color(ms_blob)

        self.play(
            FadeIn(pb_words),
            ShowCreation(pb_rect),
        )
        self.wait()
        self.play(
            FadeIn(ms_words),
            ShowCreation(ms_blob),
        )

        # Wave of flips
        k = 3
        for n in range(1, len(block) + k):
            if n < len(block):
                toggle_bit(block[n])
            if 1 <= n - k < len(block):
                toggle_bit(block[n - k])
            self.wait(0.05)

        # Count 1's
        number_ones_label = TextMobject("\\# ", "of 1's: ")
        number_ones_label.set_height(0.7)
        number_ones_label.to_edge(UP)
        number_ones_label.shift(LEFT)

        one_rects = get_one_rects(block)
        one_counter = get_ones_counter(number_ones_label, one_rects)

        self.play(
            FadeIn(number_ones_label, DOWN),
            FadeOut(title, UP),
        )
        self.add(one_counter)
        self.play(ShowIncreasingSubsets(one_rects, run_time=1, rate_func=bezier([0, 0, 1, 1])))
        self.wait()

        # Show need to flip
        want_even_label = TextMobject("Want this\\\\to be even")
        want_even_label.next_to(one_counter, RIGHT, buff=1.5)
        want_even_arrow = Arrow(
            want_even_label.get_left(), one_counter.get_right()
        )
        want_even_label.shift_onto_screen()

        self.play(
            GrowArrow(want_even_arrow),
            FadeIn(want_even_label),
        )
        self.wait()
        self.play(
            LaggedStartMap(
                Indicate, one_rects,
                scale_factor=1.1,
                color=RED,
                lag_ratio=0.2,
                run_time=2,
            )
        )
        self.wait()

        pb = block[0]
        pb_center = pb.get_center()

        self.play(pb.next_to, pb_words, DOWN)
        self.play(toggle_bit_anim(pb))
        self.play(pb.move_to, pb_center)
        one_rects.become(get_one_rects(block))
        self.play(DrawBorderThenFill(one_rects[0]))

        # Show case with no need to flip
        self.play(
            FadeOut(block),
            FadeOut(one_rects),
            FadeOut(one_counter),
        )
        new_block = get_bit_grid(4, 4, bits=string_to_bits("<3"))
        new_block.replace(block)
        block = new_block
        self.play(ShowIncreasingSubsets(block))
        one_rects = get_one_rects(block)
        one_counter = get_ones_counter(number_ones_label, one_rects)
        self.add(one_counter)
        self.play(ShowIncreasingSubsets(one_rects))
        check = Checkmark()
        check.scale(2)
        check.next_to(pb, UP)
        self.play(Write(check, run_time=0.5))
        self.play(FadeOut(check))
        self.wait()

        # Sender and receiver
        self.play(LaggedStart(*map(FadeOut, [
            number_ones_label, one_counter,
            want_even_arrow, want_even_label,
            pb_words, pb_rect,
            ms_words, ms_blob,
            one_rects
        ])))

        pis, names = get_sender_and_receiver()
        sender, receiver = pis

        block.generate_target()
        block.target.scale(0.5)
        block.target.next_to(sender, UR)
        r_block = block.target.copy()
        r_block.next_to(receiver, UL)
        n_block = r_block.copy()
        n_block.move_to(VGroup(block.target, r_block))
        arrows = VGroup(
            Arrow(block.target.get_right(), n_block.get_left()),
            Arrow(n_block.get_right(), r_block.get_left()),
        )
        noise_word = TextMobject("Noise")
        noise_arrow = Vector(0.7 * DOWN)
        noise_arrow.next_to(n_block, UP)
        noise_word.next_to(noise_arrow, UP)
        noise_label = VGroup(noise_word, noise_arrow)
        noise_label.set_color(RED)
        flipper_index = 7

        self.play(
            ApplyMethod(sender.change, "raise_right_hand", block.target),
            VFadeIn(sender),
            FadeIn(names),
            FadeIn(receiver),
            MoveToTarget(block),
        )
        self.play(
            TransformFromCopy(block, n_block),
            GrowArrow(arrows[0]),
            FadeIn(noise_label),
        )
        self.play(
            toggle_bit_anim(n_block[flipper_index], target_color=RED),
            zap_anim(n_block[flipper_index]),
        )
        toggle_bit(r_block[flipper_index])
        self.play(
            TransformFromCopy(n_block, r_block),
            GrowArrow(arrows[1]),
            receiver.change, "pondering", r_block,
        )

        # Recount the 1's
        blocks = (block, r_block)
        one_rects_pair = VGroup(*[get_one_rects(b, buff=0.05) for b in blocks])
        label_pair = VGroup(*[
            TextMobject("\\#", " 1's:").next_to(b, UP, buff=MED_LARGE_BUFF)
            for b in blocks
        ])
        one_counter_pair = VGroup(*[
            get_ones_counter(label, rect, buff=MED_SMALL_BUFF)
            for label, rect in zip(label_pair, one_rects_pair)
        ])

        self.add(label_pair, one_counter_pair)
        self.play(*[
            ShowIncreasingSubsets(group)
            for group in one_rects_pair
        ])
        self.wait()

        bangs = TexMobject("!!!")
        bangs.set_color(RED)
        bangs.next_to(receiver, UP)
        self.play(
            FadeIn(bangs, DOWN),
            receiver.change, "horrified", r_block,
        )
        self.play(Blink(receiver))
        self.wait()

        # Define parity and parity bit
        parity_rects = VGroup(
            SurroundingRectangle(VGroup(block, one_counter_pair[0]), buff=MED_SMALL_BUFF),
            SurroundingRectangle(VGroup(r_block, one_counter_pair[1]), buff=MED_SMALL_BUFF),
        )
        parity_rects[0].set_stroke(BLUE, 2)
        parity_rects[1].set_stroke(RED, 2)

        parity_labels = VGroup(*[
            TextMobject(
                "Parity: ", word,
                tex_to_color_map={word: color}
            ).next_to(rect, UP)
            for word, color, rect in zip(
                ["Even", "Odd"],
                [BLUE, RED],
                parity_rects,
            )
        ])

        for label, rect in zip(parity_labels, parity_rects):
            self.play(
                FadeIn(label, DOWN),
                ShowCreation(rect),
            )
        self.play(LaggedStart(*[
            ShowCreationThenFadeOut(Underline(label[0], color=YELLOW))
            for label in parity_labels
        ], lag_ratio=0.3))
        self.wait()
        self.play(Blink(sender))
        self.play(Blink(receiver))
        for bit, label, rect in zip([0, 1], parity_labels, parity_rects):
            bit_mob = get_bit_grid(1, 1, bits=[bit])[0]
            bit_mob.match_height(label[1])
            bit_mob.match_color(label[1])
            bit_mob.move_to(label[1], LEFT)
            x_shift = (rect.get_center() - VGroup(label[0], bit_mob).get_center()) * RIGHT
            bit_mob.shift(x_shift)
            self.play(
                label[1].replace, bit_mob, {"stretch": True},
                label[1].set_opacity, 0,
                FadeIn(bit_mob),
                label[0].shift, x_shift,
            )
            label.replace_submobject(1, bit_mob)

        pb_rect = SurroundingRectangle(block[0], buff=0.05)
        pb_rect.set_stroke(GREEN, 3)
        pb_label = TextMobject("Parity bit")
        pb_label.move_to(pb_rect)
        pb_label.to_edge(LEFT, buff=MED_SMALL_BUFF)
        pb_label.shift(UP)
        pb_label.match_color(pb_rect)
        pb_arrow = Arrow(
            pb_label.get_bottom() + SMALL_BUFF * DOWN,
            pb_rect.get_left(),
            buff=SMALL_BUFF,
            fill_color=GREEN
        )

        self.play(
            Write(pb_label, run_time=1),
            GrowArrow(pb_arrow),
            ShowCreation(pb_rect),
        )
        for color in [RED, BLUE]:
            self.play(
                toggle_bit_anim(block[0]),
                toggle_bit_anim(parity_labels[0][1], target_color=color),
                parity_rects[0].set_color, color,
            )
            self.wait()

        parity_descriptors = VGroup(
            parity_rects, parity_labels,
            pb_rect, pb_label, pb_arrow,
        )
        self.play(FadeOut(parity_descriptors, lag_ratio=0.1))

        # More than 1 error
        new_filpper_indices = [8, 13]
        n_flippers = VGroup(*[n_block[fi] for fi in new_filpper_indices])
        r_flippers = VGroup(*[r_block[fi] for fi in new_filpper_indices])
        for bit in r_flippers:
            toggle_bit(bit)
        new_one_rects_pair = VGroup(*[get_one_rects(b, buff=0.05) for b in blocks])
        new_one_counter_pair = VGroup(*[
            get_ones_counter(label, rect, buff=MED_SMALL_BUFF)
            for label, rect in zip(label_pair, new_one_rects_pair)
        ])
        for bit in r_flippers:
            toggle_bit(bit)

        self.play(
            LaggedStartMap(
                toggle_bit_anim, n_flippers,
                target_color=RED,
            ),
            LaggedStartMap(toggle_bit_anim, r_flippers),
            LaggedStart(*map(zap_anim, n_flippers)),
            receiver.change, "maybe",
            FadeOut(one_rects_pair[1]),
            FadeOut(one_counter_pair[1]),
        )
        self.remove(one_rects_pair, one_counter_pair)
        one_rects_pair = new_one_rects_pair
        one_counter_pair = new_one_counter_pair
        self.add(one_rects_pair, one_counter_pair)

        self.play(
            ShowIncreasingSubsets(one_rects_pair[1])
        )

        for x in range(2):
            self.play(Blink(receiver))
            self.play(Blink(sender))
            self.wait()

        # Even number of errors
        self.play(
            FadeOut(one_rects_pair[1]),
            FadeOut(one_counter_pair[1]),
            FadeOut(bangs),
            receiver.change, "pondering", r_block,
        )
        temp_rect = SurroundingRectangle(
            n_flippers[1],
            buff=0.05,
            color=GREEN,
        )
        temp_rect.flip()
        self.play(
            ShowCreationThenFadeOut(temp_rect),
            toggle_bit_anim(n_flippers[1], target_color=WHITE),
            toggle_bit_anim(r_flippers[1]),
        )
        self.wait()
        self.play(Blink(receiver))

        one_counter_pair.set_opacity(1)
        self.add(one_counter_pair)
        one_rects_pair[1].set_submobjects(
            get_one_rects(r_block, buff=0.05).submobjects
        )
        self.play(
            ShowIncreasingSubsets(one_rects_pair[1])
        )
        self.play(receiver.change, "hooray", r_block)
        self.wait()
        self.play(receiver.change, "erm")
        self.wait()


class ChangeAnywhereToOneBit(Scene):
    CONFIG = {
        "random_seed": 3,
    }

    def construct(self):
        title = VGroup(
            TextMobject("Change anywhere"),
            Vector(RIGHT),
            TextMobject("One bit of information"),
        )
        title.arrange(RIGHT)
        title.set_width(FRAME_WIDTH - 1)
        title.to_edge(UP)
        self.add(title)

        grid = get_bit_grid(4, 4)
        grid.set_height(4)
        grid.match_x(title[0])
        grid.set_y(-1)
        self.add(grid)

        one_rects = get_one_rects(grid)
        self.add(one_rects)

        parity_words = VGroup(
            TextMobject("Even \\# of 1s", color=BLUE_B),
            TextMobject("Odd \\# of 1s", color=TEAL_D),
        )
        parity_words.scale(1.5)
        parity_words.arrange(DOWN, buff=MED_LARGE_BUFF, aligned_edge=RIGHT)
        parity_words.match_x(title[2])
        parity_words.match_y(grid)
        self.add(parity_words)

        def get_parity_rect(n, words=parity_words):
            return SurroundingRectangle(words[n % 2])

        p_rect = get_parity_rect(len(one_rects))
        self.add(p_rect)

        # Random changes
        for x in range(10):
            bit = random.choice(grid)
            self.play(toggle_bit_anim(bit))
            one_rects.set_submobjects(get_one_rects(grid))
            p_rect.become(get_parity_rect(len(one_rects)))
            self.wait()


class OddNumberCountTo101(Scene):
    def construct(self):
        group = VGroup(
            *[Integer(2 * n + 1) for n in range(1, 50)],
        )
        group.set_color(RED)
        group.scale(2)
        for mob in group[:2]:
            self.add(mob)
            self.wait()
            self.remove(mob)
        self.play(ShowSubmobjectsOneByOne(group[2:]), run_time=6, rate_func=bezier([0, 0, 1, 1]))
        self.wait()


class ComplainAboutParityCheckWeakness(TeacherStudentsScene):
    def construct(self):
        self.embed()

        self.screen.set_fill(BLACK, 1)
        self.add(self.screen)

        self.play(
            PiCreatureSays(
                self.students[1],
                "Wait, it fails\\\\for two flips?",
                target_mode="sassy",
                bubble_kwargs={
                    "height": 3,
                    "width": 3,
                }
            ),
            self.teacher.change, "guilty",
        )
        self.wait()
        self.play(
            PiCreatureSays(
                self.students[2], "Weak!",
                target_mode="angry",
                bubble_kwargs={"direction": LEFT}
            ),
            self.students[0].change, "hesitant"
        )
        self.wait()
        self.play(self.teacher.change, "tease")
        self.wait()
        self.change_student_modes(
            "thinking", "pondering", "pondering",
            look_at_arg=self.screen,
            added_anims=[
                FadeOut(self.students[1].bubble),
                FadeOut(self.students[1].bubble.content),
                FadeOut(self.students[2].bubble),
                FadeOut(self.students[2].bubble.content),
            ]
        )
        self.wait()


class ArrayOfValidMessages(Scene):
    def construct(self):
        # Messages
        title = TextMobject("All possible messages")
        title.to_edge(UP)
        nr = 22
        nc = 46
        dots = VGroup(*[Dot() for x in range(nr * nc)])
        dots.arrange_in_grid(nr, nc)
        dots.set_color(GREY_C)
        dots.set_height(6)
        dots.to_edge(DOWN)
        shuffled_dots = dots.copy()
        shuffled_dots.shuffle()

        self.add(title)
        self.play(Write(shuffled_dots, remover=True, run_time=6, lag_ratio=5 / len(dots)))
        self.add(dots)
        self.wait()

        # Valid messages
        subset = TexMobject("\\subset")
        subset.set_height(0.4)
        subset.to_edge(UP)
        valid_label = TextMobject("Valid messages")
        valid_label.set_color(YELLOW)
        valid_label.next_to(subset, LEFT)

        valid_dots = VGroup()
        for row in range(0, nr, 3):
            for col in range(0, nc, 3):
                valid_dot = dots[row * nc + col]
                valid_dot.generate_target()
                valid_dot.target.scale(2)
                valid_dot.target.set_color(YELLOW)
                valid_dots.add(valid_dot)

        self.play(
            LaggedStartMap(MoveToTarget, valid_dots, run_time=3),
            Write(subset),
            FadeIn(valid_label, LEFT),
            title.next_to, subset, RIGHT,
        )
        self.wait()

        # Words analogy
        example_words = VGroup(
            TextMobject("Hello world", color=YELLOW),
            TextMobject("Helho world", color=GREY_B),
        )
        example_words.scale(1.25)
        index = 12 * nc + 21
        example_dots = VGroup(dots[index], dots[index + 1]).copy()

        example_groups = VGroup()
        for word, dot in zip(example_words, example_dots):
            arrow = Vector(0.7 * DOWN)
            arrow.next_to(dot, UP, SMALL_BUFF)
            word.next_to(arrow, UP, SMALL_BUFF)
            example_group = VGroup(word, arrow, dot)
            example_group.unlock_triangulation()
            example_groups.add(example_group)

        fade_rect = SurroundingRectangle(dots)
        fade_rect.set_stroke(BLACK, 0)
        fade_rect.set_fill(BLACK, 0.7)

        self.play(
            FadeIn(fade_rect),
            FadeIn(example_groups[0])
        )
        self.wait()
        self.play(
            zap_anim(example_words[0][0][3:5]),
            Transform(*example_groups),
        )
        self.wait()
        self.play(FadeOut(example_groups[0]), FadeOut(fade_rect))

        # Corrections
        valid_centers = [vd.get_center() for vd in valid_dots]
        lines = VGroup()
        for dot in dots:
            dc = dot.get_center()
            norms = [get_norm(dc - vc) for vc in valid_centers]
            line = Line(dc, valid_centers[np.argmin(norms)])
            line.set_stroke(WHITE, 1)
            lines.add(line)

        shuffled_lines = VGroup(*lines)
        shuffled_lines.shuffle()

        self.play(ShowCreation(shuffled_lines, lag_ratio=10 / len(lines), run_time=5))
        self.wait()

        # Mandering path between valid messages
        self.add(fade_rect, valid_dots)
        self.play(FadeIn(fade_rect))

        path = [RIGHT, UP, UP, RIGHT, RIGHT, RIGHT, UP, UP, RIGHT, RIGHT, DOWN]
        dist = get_norm(dots[1].get_center() - dots[0].get_center())
        curr = dots[index].get_center()
        arrows = VGroup()
        for vect in path:
            new = curr + dist * vect
            arrows.add(Arrow(curr, new, buff=0, fill_color=RED))
            curr = new

        for arrow in arrows:
            self.play(GrowArrow(arrow), run_time=0.5)
        self.wait()


class RobustForLessThanNErrors(Scene):
    def construct(self):
        words = TextMobject(
            "Robust for ", "$\\le N$", " errors",
        )
        words.to_edge(UP)
        words[1].set_color(YELLOW)
        words[2].shift(0.15 * RIGHT)
        N = words[1][-1]

        num = Integer(1)
        num.set_color(YELLOW)
        num.move_to(N, LEFT)
        num.set_value(1)

        self.play(Write(words, run_time=2))
        self.wait()
        self.remove(N)
        self.add(num)
        self.play(ChangeDecimalToValue(num, 20, run_time=3))
        self.remove(num)
        self.add(N)
        self.wait()


class TwentyQuestions(Scene):
    def construct(self):
        # Hamming's insight
        bits = [
            1, 0, 0, 1,
            0, 1, 0, 0,
            0, 1, 0, 1,
            1, 0, 1, 1,
        ]
        block = get_bit_grid(4, 4, bits=bits)

        hamming = ImageMobject("Richard_Hamming")
        hamming.set_height(3)
        hamming.to_corner(DL)

        bulb = Lightbulb()
        bulb.next_to(hamming.get_corner(UR), UP)

        self.add(block)
        self.play(FadeIn(hamming, 0.5 * RIGHT))
        self.play(Write(bulb, run_time=1, stroke_width=5))
        self.wait()

        # Preview parity checks
        parity_word = TextMobject("Parity check")
        parity_word.set_height(0.7)
        parity_word.set_color(BLUE)
        parity_word.move_to(block, UP)
        parity_word.set_opacity(0)

        back_rects = VGroup(*[
            SurroundingRectangle(bit, buff=MED_SMALL_BUFF / 2).scale(0)
            for bit in get_bit_n_subgroup(block, 0)
        ])
        back_rects.set_stroke(width=0)
        back_rects.set_fill(BLUE_E, 1)

        last_one_rects = VMobject()

        self.add(back_rects, block)

        for n, vect in zip(it.count(), [UP, UP, RIGHT, RIGHT]):
            block.generate_target()
            block.target.set_color(WHITE)
            color_group = get_bit_n_subgroup(block.target, n)
            color_group.set_color(BLUE)
            one_rects = get_one_rects(color_group)

            rects = VGroup(*[
                SurroundingRectangle(bit, buff=MED_SMALL_BUFF / 2)
                for bit in color_group
            ])
            rects.match_style(back_rects)

            self.play(
                FadeOut(last_one_rects),
                MoveToTarget(block),
                parity_word.next_to, color_group, vect, MED_LARGE_BUFF,
                parity_word.set_opacity, 1,
                Transform(back_rects, rects),
            )
            self.play(ShowIncreasingSubsets(one_rects))
            last_one_rects = one_rects

        self.play(
            FadeOut(back_rects),
            FadeOut(last_one_rects),
            FadeOut(parity_word),
            block.set_color, WHITE,
        )

        # Expand to grid
        block.generate_target()
        block.target.space_out_submobjects(1.5)
        block.target.to_edge(LEFT, buff=LARGE_BUFF)

        boxes = get_bit_grid_boxes(block.target)
        p_labels = get_grid_position_labels(boxes)
        p_labels.set_color(GREY_C)

        self.play(
            FadeOut(hamming, LEFT),
            FadeOut(bulb, 1.5 * LEFT),
            MoveToTarget(block),
        )
        self.play(
            ShowCreation(boxes, lag_ratio=0.2),
            FadeIn(p_labels, lag_ratio=0.2),
        )

        # Set up questions
        q_labels = VGroup(*[
            TextMobject(f"Q{n}:")
            for n in range(1, 5)
        ])
        q_labels.set_height(0.5)
        q_labels.arrange(DOWN, buff=1.25)
        q_labels.next_to(boxes, RIGHT, buff=2)

        questions = VGroup()
        for n, q_label in enumerate(q_labels):
            m_grids = VGroup(boxes.copy(), boxes.copy())
            m_grids.set_height(1)
            m_grids.set_width(1, stretch=True)
            colors = [GREY_BROWN, BLUE]
            for k, m_grid in enumerate(m_grids):
                get_bit_n_subgroup(m_grid, n, k).set_fill(colors[k], 0.75)
            vs = TextMobject("or")
            question = VGroup(m_grids[0], vs, m_grids[1])
            question.arrange(RIGHT)
            question.next_to(q_label, RIGHT, buff=MED_SMALL_BUFF)
            question.add_to_back(q_label)
            questions.add(question)

        questions.to_edge(RIGHT, buff=MED_LARGE_BUFF)

        for question in questions:
            question.save_state()
            q_center = question.get_center()
            for mob in question:
                if mob is not question[0]:
                    mob.move_to(q_center)
                mob.set_fill(opacity=0)
                mob.set_stroke(width=0)

        self.play(
            LaggedStartMap(Restore, questions, lag_ratio=0.25),
            run_time=3,
        )
        self.wait()

        questions.save_state()

        # Focus on question 1
        h_rects = boxes.copy()
        h_rects.set_fill(BLUE, 0.5)
        h_groups = VGroup(*[
            get_bit_n_subgroup(h_rects, n)
            for n in range(4)
        ])

        pc_words = TextMobject("Parity check\\\\these 8 bits")
        pc_words.next_to(boxes, RIGHT, aligned_edge=UP)
        pc_words.shift(DOWN)
        pc_words.set_color(BLUE)

        block.save_state()
        self.add(h_groups[0], block, p_labels)
        self.play(
            questions[1:].fade, 0.9,
            FadeIn(h_groups[0], lag_ratio=0.3, run_time=3),
            get_bit_n_subgroup(block, 0, 0).fade, 0.9,
            Write(pc_words, run_time=1)
        )
        self.wait()

        # Scan first group
        def get_sub_scanim(n, boxes=boxes, block=block, **kwargs):
            return scan_anim(
                boxes.get_corner(DR) + UR,
                get_bit_n_subgroup(block, n),
                lag_factor=0.5,
                run_time=2,
                **kwargs
            )

        scanim = get_sub_scanim(0)
        robot = scanim.mobject[-1]
        bangs = TexMobject("!!!")
        bangs.set_color(RED)
        bangs.next_to(robot, UR, buff=SMALL_BUFF)
        check = Checkmark()
        check.next_to(robot, UR, buff=SMALL_BUFF)
        for mob in (bangs, check):
            mob.scale(1.5, about_edge=DL)

        q1_rect = SurroundingRectangle(questions[0][3])

        self.play(scanim)
        self.play(FadeIn(bangs, 0.1 * DOWN, lag_ratio=0.2))
        self.wait()
        self.play(ShowCreation(q1_rect))
        self.wait()
        self.play(
            get_sub_scanim(0, show_robot=False),
            FadeOut(bangs)
        )
        self.play(FadeIn(check, 0.2 * DOWN))
        self.wait()
        self.play(
            q1_rect.move_to, questions[0][1],
        )
        self.play(
            LaggedStartMap(
                ShowCreationThenFadeOut,
                get_bit_n_subgroup(h_rects, 0, 0).copy().set_fill(GREY_BROWN, 0.5)
            )
        )
        self.wait()
        self.play(LaggedStart(*map(FadeOut, [
            robot, check, q1_rect,
        ])))

        # Comment over in pi creature scene
        pass

        # Highlight parity bit
        frame = self.camera.frame
        frame.save_state()

        ecc_rects = VGroup(*[
            h_group[0]
            for h_group in h_groups
        ])
        pb_label = TextMobject("Parity bit")
        pb_label.next_to(ecc_rects[0], UP, MED_LARGE_BUFF)
        pb_arrow = Arrow(
            pb_label.get_bottom() + MED_SMALL_BUFF * LEFT,
            block[1].get_top(),
            buff=0.1
        )
        pb_label.set_color(GREEN)
        pb_arrow.set_color(GREEN)
        pb_arrow.set_stroke(BLACK, 5, background=True)

        h_groups[0].remove(ecc_rects[0])
        self.add(ecc_rects[0], block, p_labels)
        self.play(
            frame.set_height, 9, {"about_edge": DOWN},
            FadeIn(pb_label, 0.5 * DOWN),
            GrowArrow(pb_arrow),
            ecc_rects[0].set_color, GREEN,
        )
        self.wait()
        self.play(ShowCreationThenFadeAround(p_labels[1]))
        self.wait()

        one_rects = get_one_rects(get_bit_n_subgroup(block, 0))
        counter = get_ones_counter(boxes[-2:], one_rects)
        counter.scale(0.5)
        self.add(counter)
        self.play(ShowIncreasingSubsets(one_rects))
        self.wait()
        self.play(toggle_bit_anim(block[1]))
        one_rects.set_submobjects(
            get_one_rects(get_bit_n_subgroup(block, 0)).submobjects
        )
        self.wait()

        # Back to all questions
        self.play(
            LaggedStart(*map(FadeOut, [
                one_rects, counter,
                pb_arrow, pb_label,
                pc_words, h_groups[0]
            ])),
            frame.restore,
        )
        toggle_bit(block.saved_state[1])  # Dumb hack
        self.play(
            questions.restore,
            block.restore,
        )

        # Focus on question 2
        self.play(
            questions[0].fade, 0.9,
            questions[2:].fade, 0.9,
            get_bit_n_subgroup(block, 1, 0).fade, 0.9,
            ecc_rects[0].fade, 0.5,
        )
        self.add(h_groups[1], block, p_labels)
        self.play(FadeIn(h_groups[1], lag_ratio=0.2, run_time=2))

        pb_label.next_to(boxes[2], UP, SMALL_BUFF)
        h_groups[1].remove(ecc_rects[1])
        self.add(ecc_rects[1], block, p_labels)
        self.play(
            FadeIn(pb_label, 0.25 * LEFT),
            ecc_rects[1].set_color, GREEN,
        )
        self.wait()

        # Apply second parity check
        one_rects = get_one_rects(get_bit_n_subgroup(block, 1))
        counter = get_ones_counter(boxes[-2:], one_rects)
        counter.scale(0.5)
        self.add(counter)
        self.play(
            ShowIncreasingSubsets(one_rects)
        )
        self.wait()
        self.play(LaggedStart(*map(FadeOut, [
            one_rects, counter, pb_label,
        ])))

        # Find error in right half
        scanim = get_sub_scanim(1)
        robot = scanim.mobject[-1]
        self.play(
            zap_anim(block[6]),
            toggle_bit_anim(block[6], target_color=RED)
        )
        self.play(scanim)
        self.play(FadeIn(bangs, 0.1 * DOWN, lag_ratio=0.1))
        self.wait()

        q2_rect = q1_rect.copy()
        q2_rect.move_to(questions[1][3])
        self.play(ShowCreation(q2_rect))
        self.wait()

        self.play(
            toggle_bit_anim(block[6], target_color=WHITE),
            FadeOut(bangs),
        )
        self.play(get_sub_scanim(1, show_robot=False))
        self.play(FadeIn(check, 0.2 * DOWN))
        self.wait()
        self.play(q2_rect.move_to, questions[1][1])
        self.play(
            ShowCreationThenFadeOut(
                get_bit_n_subgroup(boxes.copy(), 1, 0).set_fill(GREY_BROWN, 0.5),
                lag_ratio=0.5,
                run_time=2,
            )
        )
        self.wait()

        self.play(
            FadeOut(h_groups[1]),
            FadeOut(robot),
            FadeOut(check),
            FadeOut(q2_rect),
            block.restore,
            Transform(questions[0], questions.saved_state[0]),
            ecc_rects[0].set_fill, GREEN, 0.5,
        )

        # Mention two errors?

        # How to use Q1 with Q2
        q1_rect.move_to(questions[0][3])
        q2_rect.move_to(questions[1][3])
        q1_highlight, q2_highlight = [
            get_bit_n_subgroup(h_rects, n).copy().set_fill(BLUE, 0.5)
            for n in [0, 1]
        ]

        q2_highlight.set_fill(opacity=0)
        q2_highlight.set_stroke(YELLOW, 7)

        self.add(q1_highlight, block, p_labels)
        self.play(
            FadeIn(q1_highlight, lag_ratio=0.2),
            ShowCreation(q1_rect),
            get_bit_n_subgroup(block, 0, 0).fade, 0.9,
            *map(FadeOut, ecc_rects[:2]),
        )
        self.wait()
        self.play(
            FadeIn(q2_highlight, lag_ratio=0.2),
            ShowCreation(q2_rect),
            get_bit_n_subgroup(block, 1, 0)[1::2].fade, 0.9,
        )
        self.wait(2)
        self.play(
            q1_rect.move_to, questions[0][1],
            q1_highlight.move_to, boxes, LEFT,
            q1_highlight.set_fill, GREY_BROWN,
            block.restore,
            FadeOut(q2_highlight),
        )
        self.play(get_bit_n_subgroup(block, 0).fade, 0.9)
        self.wait()
        self.play(
            FadeIn(q2_highlight, lag_ratio=0.2),
            block[::4].fade, 0.9,
        )
        self.wait(2)
        self.play(
            q1_highlight.move_to, boxes, RIGHT,
            q1_highlight.set_fill, BLUE,
            q2_highlight.move_to, boxes, LEFT,
            block.restore,
            q1_rect.move_to, questions[0][3],
            q2_rect.move_to, questions[1][1],
        )
        self.play(
            block[::4].fade, 0.9,
            get_bit_n_subgroup(block, 1).fade, 0.9,
        )
        self.wait(2)
        self.play(
            q1_rect.move_to, questions[0][1],
            q1_highlight.move_to, boxes, LEFT,
            q1_highlight.set_fill, GREY_BROWN,
            block[1::4].fade, 0.9,
            Transform(block[0::4], block.saved_state[0::4]),
        )
        self.wait()

        morty = Mortimer(height=2)
        morty.flip()
        morty.next_to(boxes, RIGHT, buff=0.5, aligned_edge=DOWN)
        words = TextMobject("Or no error\\\\at all!")
        words.next_to(morty, UP)

        self.play(
            VFadeIn(morty),
            morty.change, "shruggie", questions[0],
            FadeIn(words, DOWN)
        )
        self.play(Blink(morty))
        self.wait(2)
        self.play(
            LaggedStart(*map(FadeOut, [
                q1_highlight, q2_highlight[1::2],
                words, morty,
            ])),
            block.restore,
        )
        self.wait()

        column_highlight = q2_highlight[0::2]

        # Choosing a column
        self.play(
            q1_rect.move_to, questions[0][3],
            column_highlight.move_to, boxes[1], UP,
        )
        self.wait()
        self.play(
            q1_rect.move_to, questions[0][1],
            q2_rect.move_to, questions[1][3],
            column_highlight.move_to, boxes[2], UP,
        )
        self.wait()
        self.play(
            q1_rect.move_to, questions[0][3],
            column_highlight.move_to, boxes[3], UP,
        )
        self.wait()

        # Bring back the parity highlights
        self.add(*ecc_rects[:2], block, p_labels)
        self.play(
            LaggedStart(*map(FadeOut, [
                column_highlight, q1_rect, q2_rect
            ])),
            *map(FadeIn, ecc_rects[:2]),
        )
        self.wait()
        for n in [2, 3]:
            self.play(Transform(questions[n], questions.saved_state[n]))
        self.wait()

        # Question 3
        self.add(h_groups[2], block, p_labels)
        self.play(
            get_bit_n_subgroup(block, 2, 0).fade, 0.9,
            FadeIn(h_groups[2], lag_ratio=0.2, run_time=2),
            questions[:2].fade, 0.9,
            questions[3].fade, 0.9,
        )
        self.wait()

        h_groups[2].remove(ecc_rects[2])
        self.add(ecc_rects[2], block, p_labels)
        self.play(
            ecc_rects[2].set_color, GREEN,
            ShowCreationThenFadeOut(SurroundingRectangle(boxes[4], buff=0))
        )
        self.wait()

        one_rects = get_one_rects(get_bit_n_subgroup(block, 2))
        self.play(ShowIncreasingSubsets(one_rects))
        self.wait()
        temp_check = Checkmark()
        temp_check.set_height(0.4)
        temp_check.next_to(block[4], UL, buff=0)
        self.play(Write(temp_check))
        self.play(FadeOut(temp_check))
        self.play(FadeOut(one_rects))
        self.play(
            block.restore,
            FadeOut(h_groups[2]),
        )
        self.wait()

        # Question 4
        self.add(h_groups[3], block, p_labels)
        self.play(
            questions[2].fade, 0.9,
            Transform(questions[3], questions.saved_state[3]),
            get_bit_n_subgroup(block, 3, 0).fade, 0.9,
            FadeIn(h_groups[3], lag_ratio=0.2, run_time=2),
        )
        self.wait()
        h_groups[3].remove(ecc_rects[3])
        self.add(ecc_rects[3], block, p_labels)
        self.play(
            ecc_rects[3].set_color, GREEN,
            ShowCreationThenFadeOut(SurroundingRectangle(boxes[8], buff=0))
        )

        one_rects = get_one_rects(get_bit_n_subgroup(block, 3))
        self.play(ShowIncreasingSubsets(one_rects))
        self.wait()
        self.play(toggle_bit_anim(block[8]))
        toggle_bit(block.saved_state[8])
        one_rects.set_submobjects(get_one_rects(get_bit_n_subgroup(block, 3)))
        self.wait()
        self.play(FadeOut(one_rects, lag_ratio=0.2))
        self.play(
            block.restore,
            questions.restore,
            FadeOut(h_groups[3], lag_ratio=0.2),
        )
        self.wait()

        # Point out rolls of questions
        braces = VGroup(
            Brace(questions[:2], LEFT),
            Brace(questions[2:], LEFT),
        )
        for brace, text in zip(braces, ["column", "row"]):
            brace.words = brace.get_text(f"Which\\\\{text}?")

        for brace in braces:
            self.play(
                GrowFromCenter(brace),
                FadeIn(brace.words, 0.25 * RIGHT)
            )
            self.wait()

        # Example with error at 3
        q_rects = VGroup()
        for question, answer in zip(questions, [1, 1, 0, 0]):
            q_rects.add(SurroundingRectangle(question[1 + 2 * answer]))

        self.play(
            zap_anim(block[3]),
            toggle_bit_anim(block[3], target_color=RED),
        )
        self.wait()

        target_square = SurroundingRectangle(boxes[3::4], buff=0, stroke_width=5)
        for n in range(4):
            highlight = get_bit_n_subgroup(h_rects.copy(), n)
            one_rects = get_one_rects(get_bit_n_subgroup(block, n))
            self.add(highlight, block, p_labels)
            self.play(
                FadeIn(highlight),
                ShowCreation(q_rects[n]),
                ShowIncreasingSubsets(one_rects),
            )
            self.wait()
            self.play(
                FadeOut(highlight),
                FadeOut(one_rects),
            )
            if n == 1:
                self.play(FadeIn(target_square))
            elif n == 3:
                self.play(target_square.replace, boxes[3], {"stretch": True})
        self.wait()
        self.play(
            toggle_bit_anim(block[3], target_color=WHITE)
        )
        self.wait()

        # Binary counting
        for n in range(1, 16):
            target_square.generate_target()
            target_square.target.move_to(boxes[n])
            for k, q_rect in enumerate(q_rects):
                index = 3 if((1 << k) & n) else 1
                q_rect.generate_target()
                q_rect.target.move_to(questions[k][index])
            self.play(*map(MoveToTarget, [target_square, *q_rects]), run_time=0.5)
            self.wait()

        # Bit 0
        for q_rect, question in zip(q_rects, questions):
            q_rect.generate_target()
            q_rect.target.move_to(question[1])

        self.play(
            target_square.move_to, boxes[0],
            LaggedStartMap(MoveToTarget, q_rects),
        )
        self.wait()
        for n in range(4):
            group = get_bit_n_subgroup(h_rects.copy(), n)
            self.play(FadeIn(group, lag_ratio=0.2))
            self.wait(0.5)
            self.play(FadeOut(group))
        self.wait()

        randy = Randolph(height=2)
        randy.next_to(boxes, RIGHT, buff=MED_LARGE_BUFF, aligned_edge=DOWN)
        ne_word = TextMobject("No error?")
        ne_word.next_to(randy, UP, buff=MED_LARGE_BUFF)
        ne_word.shift(0.2 * RIGHT)
        ez_word = TextMobject("or error\\\\at bit 0?")
        ez_word.set_color(RED)
        ez_word.move_to(ne_word, DOWN)

        self.play(
            VFadeIn(randy),
            randy.change, 'pondering', questions,
            FadeOut(braces),
            *[
                FadeOut(brace.words)
                for brace in braces
            ]
        )
        self.play(FadeIn(ne_word, 0.5 * DOWN))
        self.play(Blink(randy))
        self.wait()
        self.play(
            ne_word.next_to, ez_word, UP, MED_LARGE_BUFF,
            FadeIn(ez_word, 0.25 * DOWN),
            randy.change, "confused", target_square,
        )
        self.play(Blink(randy))
        for x in range(2):
            self.play(toggle_bit_anim(block[0]))
        self.play(randy.change, "pondering", questions)

        # Count through again
        for n in [*range(0, 16), 0]:
            target_square.move_to(boxes[n])
            for k, q_rect in enumerate(q_rects):
                index = 3 if((1 << k) & n) else 1
                q_rect.move_to(questions[k][index])
            randy.look_at(target_square)
            self.wait(0.5)

        # Highlight no error
        ne_rect = SurroundingRectangle(ne_word)
        ne_rect.set_stroke(GREY_B, 2)
        ne_comment = TextMobject("17th outcome")
        ne_comment.set_color(GREY_B)
        ne_comment.next_to(ne_rect, UP)

        self.play(
            ShowCreation(ne_rect),
            FadeIn(ne_comment, 0.25 * DOWN),
            randy.change, "maybe", ne_comment,
        )
        for x in range(2):
            self.play(Blink(randy))
            self.wait(2)

        # Nix bit 0
        zero_rect = SurroundingRectangle(boxes[0], buff=0)
        zero_rect.set_fill(BLACK, 1)
        zero_rect.set_stroke(BLACK, 0)
        zero_rect.scale(0.98)

        self.play(
            GrowFromCenter(zero_rect),
            boxes[0].set_stroke, {"width": 0},
            FadeOut(target_square),
            randy.change, "raise_left_hand", zero_rect,
        )
        ne_word.generate_target()
        ne_word.target[0][-1].set_opacity(0)
        ne_word.target.next_to(randy, UP, MED_LARGE_BUFF)
        ne_word.target.set_color(YELLOW)
        self.play(
            MoveToTarget(ne_word),
            LaggedStart(*map(FadeOut, [ne_rect, ne_comment, ez_word]))
        )
        for n in range(4):
            highlight = get_bit_n_subgroup(h_rects.copy(), n)
            one_rects = get_one_rects(get_bit_n_subgroup(block, n))
            self.add(highlight, block, p_labels, zero_rect, one_rects)
            self.wait()
            self.remove(highlight, one_rects)

        # (15, 11) setup
        stat_words = VGroup(
            TextMobject("15", "-bit block"),
            TextMobject("11", " bits of\\\\message", alignment=""),
            TextMobject("4 bits of\\\\redundancy", alignment=""),
        )
        stat_words.arrange(DOWN, buff=MED_LARGE_BUFF, aligned_edge=LEFT)
        stat_words[0].set_color(YELLOW)
        stat_words[2].set_color(GREEN)
        stat_words.next_to(boxes, RIGHT, buff=MED_LARGE_BUFF, aligned_edge=UP)
        stat_words.shift(0.5 * DOWN)

        self.play(
            LaggedStart(*map(FadeOut, [*q_rects, ne_word])),
            randy.change, "tease", stat_words,
            FadeIn(stat_words[0], 0.5 * LEFT)
        )
        self.play(Blink(randy))
        self.play(
            FadeIn(stat_words[1], 0.5 * LEFT),
            LaggedStart(*[
                toggle_bit_anim(bit)
                for i, bit in enumerate(block)
                if i not in [0, 1, 2, 4, 8]
            ])
        )
        self.play(
            LaggedStart(*[
                toggle_bit_anim(bit)
                for i, bit in enumerate(block)
                if i not in [0, 1, 2, 4, 8]
            ])
        )
        self.wait()
        self.play(
            FadeIn(stat_words[2], 0.5 * LEFT),
            LaggedStart(*map(ShowCreationThenFadeAround, [
                block[2**n]
                for n in range(4)
            ]))
        )
        self.play(Blink(randy))

        code_name = TextMobject("(", "15", ", ", "11", ")", " Hamming code")
        code_name.set_height(0.8)
        code_name.to_edge(UP)
        code_name.shift(UP)

        self.play(
            ApplyMethod(frame.set_height, 9, {"about_edge": DOWN}, run_time=2),
            TransformFromCopy(stat_words[0][0], code_name[1]),
            TransformFromCopy(stat_words[1][0], code_name[3]),
            LaggedStart(*map(FadeIn, [
                code_name[i] for i in [0, 2, 4, 5]
            ])),
        )
        self.wait()

        # Bring back bit zero
        self.play(
            LaggedStart(*map(FadeOut, [
                *stat_words, randy,
                *questions, code_name,
            ])),
            ApplyMethod(frame.match_x, block),
            run_time=2
        )

        old_zero_rect = zero_rect
        zero_rect = old_zero_rect.copy()
        zero_rect.set_stroke(YELLOW, 2)
        zero_rect.set_fill(YELLOW, 0.5)
        zero_rect.save_state()
        zero_rect.stretch(0, 1, about_edge=UP)
        zero_words = TextMobject("Can we put this bit to work?")
        zero_words.set_height(0.7)
        zero_words.next_to(zero_rect, UP, MED_LARGE_BUFF)
        zero_words.match_x(block)
        zero_words.set_color(YELLOW)

        self.add(zero_rect, block, p_labels)
        block[0].set_opacity(0)
        self.play(
            FadeOut(old_zero_rect),
            Restore(zero_rect),
            Write(zero_words)
        )
        self.wait()

        # Parity check the whole block
        pc_words = TextMobject("Parity check\\\\ \\emph{the whole block}")
        pc_words.set_height(1.2)
        pc_words.next_to(boxes, LEFT, buff=MED_LARGE_BUFF)

        one_rects = get_one_rects(block)
        counter = get_ones_counter(boxes[-2:], one_rects)
        counter.scale(0.5)

        self.play(
            Write(pc_words, run_time=1),
            ShowCreationThenFadeOut(h_rects.copy()),
        )
        self.wait()
        ecc_bits = VGroup(*[block[2**n] for n in range(4)])
        for x in range(2):
            self.play(LaggedStartMap(toggle_bit_anim, ecc_bits, lag_ratio=0.25, run_time=1))
        self.wait()

        self.add(counter)
        self.play(ShowIncreasingSubsets(one_rects))
        self.wait()
        block[0][1].set_opacity(1)
        self.play(Write(block[0]))
        one_rects.set_submobjects(get_one_rects(block))
        self.wait()
        self.play(*map(FadeOut, [one_rects, counter]))

        # Walk through single and two bit errors
        self.play(
            zap_anim(block[9]),
            toggle_bit_anim(block[9], target_color=RED),
        )
        one_rects.set_submobjects(get_one_rects(block))
        counter.set_opacity(1)
        self.add(counter)
        self.play(ShowIncreasingSubsets(one_rects))
        self.wait()

        self.play(
            zap_anim(block[5]),
            toggle_bit_anim(block[5], target_color=RED),
        )
        one_rects.set_submobjects(get_one_rects(block))
        self.wait()
        self.play(FadeOut(one_rects), FadeOut(counter))

        for n in [2, 3]:
            group = get_bit_n_subgroup(h_rects.copy(), n)
            group.set_fill(opacity=0)
            group.set_stroke(BLUE, 10)
            self.play(ShowCreation(group, lag_ratio=0.5))
            self.play(FadeOut(group))
        self.wait()

        scanim = scan_anim(boxes.get_corner(DR) + 2 * UR, block, lag_factor=0.5, run_time=2)
        robot = scanim.mobject[-1]
        robot.set_color(GREY_B)
        robot.scale(2, about_edge=UP)
        ded_words = TextMobject("At least\\\\2 errors!")
        ded_words.set_color(RED)
        ded_words.next_to(robot, UR, buff=SMALL_BUFF)

        self.play(scanim)
        self.play(FadeIn(ded_words, 0.5 * DOWN))
        self.wait()

        # Extended name
        new_title = TextMobject("Extended Hamming Code")
        new_title.replace(zero_words, dim_to_match=1)
        self.play(
            FadeIn(new_title, DOWN),
            FadeOut(zero_words, UP),
            FadeOut(pc_words),
        )
        self.wait()


class WhatIfTheresAndArrowInECCBits(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "What if an\\\\error-correction bit\\\\needs to be corrected?",
            bubble_kwargs={'width': 5, 'height': 4, "direction": LEFT},
            added_anims=[self.teacher.change, "happy"]
        )
        self.change_student_modes("confused", "confused")
        self.look_at(self.screen)
        self.wait(2)
        self.teacher_says("Try it!", target_mode="hooray")
        self.change_student_modes(*3 * ["pondering"], look_at_arg=self.screen)
        self.wait(2)
        self.change_student_modes(*3 * ["thinking"], look_at_arg=self.screen)
        self.wait(8)


class ErrorAtECCBit(Scene):
    def construct(self):
        bits = get_bit_grid(4, 4, height=6)
        toggle_bit(bits[1])
        toggle_bit(bits[4])
        boxes = get_bit_grid_boxes(bits)
        pos_labels = get_grid_position_labels(boxes)
        ecc_boxes = VGroup(*[boxes[2**n] for n in range(4)])
        ecc_boxes.set_fill(GREEN, 0.5)
        bangs = TextMobject("!!!")
        bangs.set_color(RED)
        bangs.next_to(boxes[2], UP, SMALL_BUFF)

        self.add(boxes, ecc_boxes, pos_labels, bits)
        self.wait()
        self.play(LaggedStartMap(Rotate, ecc_boxes, lambda m: (m, PI)))
        self.wait()
        self.play(
            zap_anim(bits[2]),
            toggle_bit_anim(bits[2], target_color=RED),
        )
        self.play(Write(bangs))
        self.wait()

        for bit in bits:
            bit.remove(bit[1 - get_bit_mob_value(bit)])
        for n in range(4):
            bits.generate_target()
            bits.target.set_opacity(1)
            get_bit_n_subgroup(bits.target, n, 0).set_opacity(0)
            self.play(MoveToTarget(bits))
            self.wait()
        self.play(bits.set_opacity, 1)
        self.wait()


class HalfAsPowerful(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Shouldn't that be\\\\only half as good?",
            target_mode="sassy",
            added_anims=[self.teacher.change, "happy"]
        )
        self.change_student_modes(
            "pondering", "pondering", look_at_arg=self.screen,
            added_anims=[self.teacher.change, "tease"]
        )
        self.look_at(self.screen)
        self.wait(8)


class WhatAboutTwoErrors(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "What about\\\\2 errors?",
        )
        self.play(self.teacher.change, "guilty")
        self.look_at(self.screen)
        self.change_student_modes("erm", "confused")
        self.look_at(self.screen)
        self.wait(4)


class BlockSize256(Scene):
    def construct(self):
        N = 8
        frame = self.camera.frame

        # Bit block
        bits = string_to_bits("You decoded an easter egg. Nice!")
        block = get_bit_grid(2**(N // 2), 2**(N // 2), bits=bits)
        block.set_height(6)
        block.to_edge(LEFT, buff=LARGE_BUFF)
        boxes = get_bit_grid_boxes(block)

        parity_boxes = VGroup(*[boxes[2**k] for k in range(N)])
        parity_boxes.set_fill(GREEN, 0.8)

        bit_boxes = VGroup(*[VGroup(box, bit) for bit, box in zip(block, boxes)])
        to_fade = VGroup()
        to_keep = VGroup()
        for i, bb in enumerate(bit_boxes):
            if i >= 64 or (i % 16) >= 4:
                to_fade.add(bb.copy())
            else:
                to_keep.add(bb.copy())

        to_fade.save_state()
        to_fade.fade(1)
        frame.save_state()
        frame.replace(to_keep, dim_to_match=1)
        frame.scale(1.2)

        self.add(to_keep)
        self.play(
            Restore(frame),
            Restore(to_fade, lag_ratio=0.1),
            run_time=5,
        )

        self.clear()
        self.add(boxes)
        self.add(block)

        # Add title
        title = TextMobject("$256 = 2^8$ bits")
        title.set_height(0.7)
        title.next_to(boxes, UP, MED_LARGE_BUFF)
        title.set_x(0)

        self.play(
            frame.move_to, 0.5 * UP,
            Write(title)
        )
        self.wait()

        # Parity groups
        parity_groups = VGroup()
        for k in range(N):
            group = boxes.copy()
            group.set_fill(BLACK, opacity=0)
            group.set_stroke(GREY_B, 1)
            group.set_height(1.5)
            get_bit_n_subgroup(group, k).set_fill(BLUE_E, 1)
            parity_groups.add(group)

        parity_groups.arrange_in_grid(2, 4, buff=MED_LARGE_BUFF)
        parity_groups.set_width(7)
        VGroup(parity_groups[:4], parity_groups[4:]).arrange(DOWN, buff=1.5)
        parity_groups.to_edge(RIGHT)

        # Question labels
        q_labels = VGroup(*[TextMobject(f"Q{i + 1}") for i in range(N)])
        for label, group in zip(q_labels, parity_groups):
            label.set_height(0.3)
            label.next_to(group, UP, SMALL_BUFF)

        # Add questions
        self.play(
            LaggedStartMap(FadeIn, q_labels, lambda m: (m, DOWN), lag_ratio=0.3, run_time=5),
            LaggedStartMap(FadeIn, parity_groups, lambda m: (m, DOWN), lag_ratio=0.3, run_time=5),
        )
        self.wait()

        # Isolate one square
        pos = 69  # Why not?
        bits = "{0:b}".format(pos)
        bits = (N - len(bits)) * '0' + bits
        bits = bits[::-1]

        yes_no_group = VGroup()
        boxes.save_state()
        possible_positions = list(range(2**N))
        for k, bit, group in zip(it.count(), bits, parity_groups):
            bit_value = int(bit)
            if bit_value:
                word = TextMobject("Yes", color=GREEN)
            else:
                word = TextMobject("No", color=RED)
            word.next_to(group, DOWN)
            yes_no_group.add(word)

            intersect_positions = get_bit_n_sublist(range(2**N), k, bit_value)
            globals()['intersect_positions'] = intersect_positions
            possible_positions = list(filter(
                lambda i: i in intersect_positions,
                possible_positions,
            ))

            boxes.generate_target()
            boxes.target.match_style(boxes.saved_state)
            globals()['possible_positions'] = possible_positions
            globals()['boxes'] = boxes
            VGroup(*[boxes.target[i] for i in possible_positions]).set_fill(BLUE, 1)

            self.play(
                FadeIn(word),
                MoveToTarget(boxes)
            )
            self.wait()

        # Highlight parity bits
        parity_bits_label = TextMobject("8 parity bits")
        parity_bits_label.next_to(boxes, UP, aligned_edge=LEFT)
        parity_bits_label.set_color(GREEN)

        self.play(
            FadeIn(parity_bits_label, DOWN),
            title.to_edge, RIGHT
        )
        self.add(parity_boxes, block)
        self.play(
            LaggedStartMap(Rotate, parity_boxes, lambda m: (m, TAU)),
        )
        self.add(boxes, block)

        # Un-highlight isolated point
        self.play(
            boxes[pos].set_fill, BLACK, 0,
            FadeOut(yes_no_group)
        )

        # Message bits
        message_bits = VGroup(*[
            bit
            for i, bit in enumerate(block)
            if i not in [2**k for k in range(N)]
        ])
        message_bits.shuffle()

        self.play(
            LaggedStart(*[
                toggle_bit_anim(bit)
                for bit in message_bits
            ], lag_ratio=0.01, run_time=3)
        )
        self.wait()

        # Write redundant
        redundant_label = TextMobject("``Redundant''")
        redundant_label.set_color(GREEN)
        redundant_label.next_to(parity_bits_label[-1][-1], RIGHT, MED_LARGE_BUFF, DOWN)

        self.play(Write(redundant_label))

        block.save_state()
        for k in range(N):
            block.target = block.saved_state.copy()
            get_bit_n_subgroup(block.target, k, 0).set_fill(opacity=0)
            self.play(MoveToTarget(block))
            self.wait(0.5)
        self.play(Restore(block))
        self.wait()


class WellAlmost(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("Well...\\\\almost", target_mode="hesitant")
        self.change_student_modes("angry", "sassy", "confused")
        self.wait(3)


class ChecksSpellOutPositionInBinary(Scene):
    def construct(self):
        N = 4
        pos = 7

        # Setup block
        random.seed(0)
        bits = [random.choice([0, 1]) for n in range(2**N)]
        bits[1] = 0
        bits[2] = 1
        bits[4] = 0
        bits[8] = 0
        block = get_bit_grid(2**(N // 2), 2**(N // 2), bits=bits)
        block.set_height(5)
        block.to_edge(LEFT, buff=LARGE_BUFF)
        boxes = get_bit_grid_boxes(block)
        VGroup(*[boxes[2**n] for n in range(N)]).set_fill(GREY_D, 1)

        pos_labels = VGroup(*map(Integer, range(2**N)))
        pos_labels.set_height(0.2)
        for label, box, bit_label in zip(pos_labels, boxes, block):
            label.move_to(box, DR)
            label.shift(0.1 * UL)
            label.set_color(GREY_A)
            bit_label.scale(0.8)

        self.add(boxes)
        self.add(block)
        self.add(pos_labels)

        self.play(
            zap_anim(block[pos]),
            toggle_bit_anim(block[pos]),
        )

        # Setup questions
        parity_groups = VGroup()
        for n in range(N):
            group = boxes.copy()
            group.set_height(1)
            group.set_width(1, stretch=True)
            group.set_fill(BLACK, 0)
            get_bit_n_subgroup(group, n).set_fill(BLUE_D, 1)
            parity_groups.add(group)
        parity_groups.arrange(DOWN, buff=MED_LARGE_BUFF)
        parity_groups.set_height(6)
        parity_groups.to_edge(RIGHT, buff=3)

        q_labels = VGroup(*[TextMobject(f"Q{n + 1}:") for n in range(N)])
        for label, group in zip(q_labels, parity_groups):
            label.next_to(group, LEFT, MED_SMALL_BUFF)

        self.play(
            FadeIn(parity_groups),
            FadeIn(q_labels),
        )

        # Binary search down
        bits_word = "{0:b}".format(pos)
        bits_word = (N - len(bits_word)) * '0' + bits_word
        bits = list(map(int, bits_word[::-1]))

        boxes.save_state()
        yes_no_words = VGroup()
        possible_positions = list(range(2**N))
        for n, bit, group in zip(it.count(), bits, parity_groups):
            if bit:
                word = TextMobject("Yes", color=GREEN)
            else:
                word = TextMobject("No", color=RED)
            word.next_to(group, RIGHT)
            yes_no_words.add(word)

            possible_positions = list(filter(
                lambda i: i in get_bit_n_sublist(range(2**N), n, bit_value=bit),
                possible_positions,
            ))

            boxes.target = boxes.saved_state.copy()
            VGroup(*[boxes.target[i] for i in possible_positions]).set_fill(BLUE_D, 0.8)

            self.play(
                FadeIn(word, 0.5 * LEFT),
                MoveToTarget(boxes),
            )
            self.wait()

        # Spell answer in binary
        binary_answers = VGroup(*[
            Integer(bit).move_to(word).match_color(word)
            for bit, word in zip(bits, yes_no_words)
        ])

        self.play(
            LaggedStartMap(GrowFromCenter, binary_answers),
            LaggedStartMap(ApplyMethod, yes_no_words, lambda m: (m.scale, 0), remover=True),
        )

        # Show value of 7
        frame = self.camera.frame

        binary_pos_label = binary_answers.copy()
        binary_pos_label.generate_target()
        binary_pos_label.target.arrange(LEFT, buff=SMALL_BUFF, aligned_edge=DOWN)

        equation = VGroup(
            Integer(7, color=BLUE),
            TexMobject("\\rightarrow"),
            binary_pos_label.target,
        )
        equation.arrange(RIGHT)
        equation.to_edge(UP, buff=0)

        arrow = Arrow(equation.get_left(), equation.get_right(), buff=0)
        arrow.next_to(equation, DOWN, SMALL_BUFF)
        trans_words = TextMobject("Decimal to binary")
        trans_words.match_width(arrow)
        trans_words.next_to(arrow, DOWN, SMALL_BUFF)

        self.play(
            MoveToTarget(binary_pos_label),
            frame.move_to, 0.5 * UP
        )
        self.play(
            Write(equation[:-1]),
            Write(trans_words),
            GrowArrow(arrow),
            run_time=1,
        )
        self.wait()

        bin_group = VGroup(*equation[:-1], binary_pos_label, arrow, trans_words)

        # Spell out binary
        bin_equation = TexMobject(
            "{7} = {0} \\cdot 8 + {1} \\cdot 4 + {1} \\cdot 2 + {1} \\cdot 1",
            tex_to_color_map={
                "{0}": RED,
                "{1}": GREEN,
                "{7}": BLUE,
            }
        )
        bin_equation.move_to(bin_group, UP)

        bit_parts = list(it.chain(*[
            bin_equation.get_parts_by_tex(f"{{{d}}}")
            for d in [0, 1]
        ]))

        self.play(
            bin_group.next_to, bin_equation, DOWN, LARGE_BUFF,
            *[
                ApplyMethod(m1.copy().replace, m2, {"dim_to_match": 1}, remover=True, run_time=1.5)
                for m1, m2 in zip(binary_pos_label[::-1], bit_parts)
            ],
            ApplyMethod(equation[0].copy().replace, bin_equation[0], remover=True, run_time=1.5)
        )
        self.add(bin_equation[0], *bit_parts)
        self.play(FadeIn(VGroup(*[
            part
            for part in bin_equation
            if part.get_tex_string() not in ["{0}", "{1}", "{7}"]
        ]), lag_ratio=0.1))
        self.add(bin_equation)
        self.wait()

        # Error at 7
        toggle_bit(block[pos])
        self.play(
            zap_anim(block[pos]),
            toggle_bit_anim(block[pos], target_color=RED),
        )
        self.wait()

        # Four parity checks
        for n, label, group, word in zip(it.count(), q_labels, parity_groups, yes_no_words):
            boxes.target = boxes.saved_state.copy()
            get_bit_n_subgroup(boxes.target, n).set_fill(BLUE, 0.8)

            rect = SurroundingRectangle(VGroup(label, group, word), buff=MED_SMALL_BUFF)
            one_rects = get_one_rects(get_bit_n_subgroup(block, n))

            self.play(
                MoveToTarget(boxes),
                ShowCreation(rect),
                ShowIncreasingSubsets(one_rects)
            )
            self.play(
                FadeOut(one_rects),
                FadeOut(rect),
            )
            self.wait(0.5)
        self.play(Restore(boxes))
        self.wait()

        # Other examples
        toggle_bit(block[7])
        block[7].set_color(WHITE)

        bit_parts = VGroup(*bit_parts)
        to_save = VGroup(
            equation[0], bin_equation[0],
            bit_parts, binary_pos_label, binary_answers,
        )
        to_save.save_state()

        ns = random.sample(list(range(16)), 10)
        for n in ns:
            toggle_bit(block[n])
            block[n].set_color(YELLOW)

            nc1 = Integer(n)
            nc1.replace(equation[0], 1)
            nc1.match_color(equation[0])
            equation[0].set_opacity(0)
            nc2 = nc1.copy()
            nc2.replace(bin_equation[0], 1)
            bin_equation[0].set_fill(0)

            new_bits = int_to_bit_string(n, 4)
            new_bit_mobs = VGroup()
            for b1, b2, b3, value in zip(reversed(bit_parts), binary_pos_label, binary_answers, reversed(new_bits)):
                new_mob = TexMobject(value)
                new_mob.set_color(GREEN if int(value) else RED)
                for b in (b1, b2, b3):
                    nmc = new_mob.copy()
                    nmc.replace(b, 1)
                    b.set_opacity(0)
                    new_bit_mobs.add(nmc)

            self.play(*[
                Animation(mob, remover=True, run_time=1)
                for mob in [new_bit_mobs, nc1, nc2]
            ])

            toggle_bit(block[n])
            block[n].set_color(WHITE)

        to_save.restore()
        self.wait()

        # Remove 7 stuff
        self.play(
            FadeOut(VGroup(
                *bin_group, *bin_equation, *binary_answers
            ), lag_ratio=0.1),
            block[pos].set_color, WHITE,
        )

        question_group = VGroup(q_labels, parity_groups)

        # Show numbers 0 through 15
        pos_labels_movers = pos_labels.copy()
        bin_pos_groups = VGroup()
        arrows = VGroup()
        bin_labels = VGroup()

        for n, label in enumerate(pos_labels_movers):
            label.scale(2)
            arrow = TexMobject("\\rightarrow")
            bits_word = "{0:b}".format(n)
            bits_word = (N - len(bits_word)) * '0' + bits_word
            bin_label = VGroup(*[TexMobject(b) for b in bits_word])
            bin_label.arrange(RIGHT, buff=SMALL_BUFF, aligned_edge=DOWN)
            pos_group = VGroup(label, arrow, bin_label)
            pos_group.arrange(RIGHT, buff=MED_SMALL_BUFF)
            bin_pos_groups.add(pos_group)
            arrows.add(pos_group[1])
            bin_labels.add(bin_label)

        bin_pos_groups.arrange_in_grid(8, 2, fill_rows_first=False)
        bin_pos_groups.set_height(7)
        bin_pos_groups.to_edge(RIGHT)
        bin_pos_groups.set_y(0.5)

        self.play(
            FadeOut(question_group),
            FadeIn(arrows, lag_ratio=0.02),
            TransformFromCopy(pos_labels, pos_labels_movers),
        )
        self.play(ShowIncreasingSubsets(bin_labels, run_time=3, rate_func=bezier([0, 0, 1, 1])))
        self.wait()

        # Put bin labels in boxes
        for label, box in zip(bin_labels, boxes):
            label.generate_target()
            label.target.set_width(0.7 * box.get_width())
            label.target.move_to(box, DOWN)
            label.target.shift(SMALL_BUFF * UP)

        for bit in block:
            bit.generate_target()
            bit.target.scale(0.5, about_edge=UP),
            bit.target.fade(0.5)

        kw = {
            "run_time": 5,
            "lag_ratio": 0.3,
        }
        self.play(
            LaggedStartMap(MoveToTarget, bin_labels, **kw),
            LaggedStartMap(FadeOut, arrows, **kw),
            LaggedStartMap(FadeOut, pos_labels_movers, **kw),
            LaggedStartMap(FadeOut, pos_labels, **kw),
            LaggedStartMap(MoveToTarget, block, **kw),
        )
        self.wait()

        # Show confusion
        randy = Randolph()
        randy.flip()
        randy.to_corner(DR, buff=LARGE_BUFF)

        self.play(
            VFadeIn(randy),
            randy.change, "maybe", boxes,
        )
        self.play(PiCreatureBubbleIntroduction(
            randy, "Wait...",
            target_mode="confused",
            bubble_class=ThoughtBubble,
            look_at_arg=boxes.get_top(),
        ))
        self.play(Blink(randy))
        self.wait()

        self.play(LaggedStart(*map(ShowCreationThenFadeAround, bin_labels), lag_ratio=0))
        self.play(randy.change, "maybe")
        self.play(
            LaggedStart(*[ShowCreationThenFadeOut(SurroundingRectangle(b, color=GREEN)) for b in block], lag_ratio=0),
            randy.look_at, boxes.get_bottom(),
        )
        self.play(Blink(randy))
        self.play(
            randy.change, 'pondering', boxes,
            FadeOut(randy.bubble),
            FadeOut(randy.bubble.content),
        )
        for x in range(2):
            self.wait()
            self.play(Blink(randy))
            self.play(randy.change, "thinking")
        self.play(FadeOut(randy))

        # Go through parity group 1 (and setup others)
        bit_arrow_groups = VGroup()
        for n in range(N):
            arrow_group = VGroup()
            for bin_label in bin_labels:
                char = bin_label[-(n + 1)]
                arrow = Triangle(start_angle=-PI / 2)
                arrow.stretch(0.8, 0)
                arrow.set_height(0.8 * char.get_height())
                arrow.next_to(char, UP, buff=0.05)
                arrow.set_stroke(width=0)
                if char.get_tex_string() == '0':
                    arrow.set_fill(GREY, 1)
                else:
                    arrow.set_fill(BLUE, 1)
                arrow_group.add(arrow)
            bit_arrow_groups.add(arrow_group)

        highlight_groups = VGroup()
        for n in range(N):
            highlight_group = boxes.copy()
            highlight_group.set_fill(BLACK, 0)
            get_bit_n_subgroup(highlight_group, n).set_fill(BLUE, 0.5)
            highlight_groups.add(highlight_group)

        questions = VGroup()
        for n in range(N):
            chars = ["\\underline{\\phantom{0}}" for x in range(4)]
            chars[-(n + 1)] = "\\underline{1}"
            question = TextMobject(
                f"""
                If there's an error, does\\\\
                its position look like\\\\
                """,
                " ".join(chars),
                "?"
            )
            question.scale(1.25)
            question[1:].scale(1.5, about_edge=UP)
            question[1:].shift(SMALL_BUFF * DOWN)
            question[1].set_color(BLUE)
            question.next_to(boxes, RIGHT, LARGE_BUFF)
            questions.add(question)

        self.play(
            LaggedStartMap(FadeIn, bit_arrow_groups[0], lag_ratio=0.3, run_time=3),
            FadeOut(block),
        )
        self.play(Transform(boxes, highlight_groups[0]))
        self.wait()
        self.play(Write(questions[0]))
        self.wait()

        # Go through parity groups 2-4
        bit_arrows = bit_arrow_groups[0]
        for n in range(1, N):
            self.play(boxes.set_fill, BLACK, 0)
            self.play(
                Transform(bit_arrows, bit_arrow_groups[n]),
                FadeOut(questions[n - 1])
            )
            self.wait()
            self.play(
                Transform(boxes, highlight_groups[n]),
                FadeIn(questions[n])
            )
            self.wait()

        # Organize questions
        questions.generate_target()
        questions.target.arrange(DOWN, buff=LARGE_BUFF)
        questions.target.set_height(FRAME_HEIGHT - 1)
        questions.target.next_to(boxes, RIGHT, buff=1.5)
        questions.target.match_y(frame)
        questions[:N - 1].set_opacity(0)

        self.play(
            MoveToTarget(questions),
            Restore(boxes),
            FadeOut(bit_arrows),
        )

        fade_anims = []
        for n in range(N):
            rect = SurroundingRectangle(questions[n])
            rect.set_stroke(BLUE, 2)
            self.play(
                FadeIn(highlight_groups[n]),
                FadeIn(rect),
                *fade_anims
            )
            fade_anims = [
                FadeOut(highlight_groups[n]),
                FadeOut(rect),
            ]
        self.play(*fade_anims)

        # Note power of 2 points
        parity_arrows = VGroup(Vector(DOWN), Vector(DOWN), Vector(RIGHT), Vector(RIGHT))
        parity_arrows[0].next_to(boxes[1], UP, SMALL_BUFF)
        parity_arrows[1].next_to(boxes[2], UP, SMALL_BUFF)
        parity_arrows[2].next_to(boxes[4], LEFT, SMALL_BUFF)
        parity_arrows[3].next_to(boxes[8], LEFT, SMALL_BUFF)
        parity_arrows.set_color(GREEN)

        parity_groups = VGroup()
        for n, question in enumerate(questions):
            pg = boxes.copy()
            pg.set_width(pg.get_height(), stretch=True)
            pg.set_height(0.8 * question.get_height())
            pg.set_fill(BLACK, 0)
            get_bit_n_subgroup(pg, n).set_fill(BLUE, 0.8)
            pg.next_to(question, RIGHT, LARGE_BUFF)
            parity_groups.add(pg)

        self.play(
            LaggedStartMap(GrowArrow, parity_arrows),
            ApplyMethod(frame.set_x, -1, run_time=2)
        )
        self.wait()
        rects = VGroup(*[boxes[2**n].copy() for n in range(N)])
        rects.set_fill(BLUE, 0.8)
        self.add(rects, bin_label)
        self.play(
            LaggedStartMap(VFadeInThenOut, rects, lag_ratio=0.5, run_time=5),
            LaggedStartMap(FadeIn, parity_groups, lag_ratio=0.5, run_time=5),
        )
        self.wait()
        self.add(rects, bin_label)
        self.play(
            LaggedStartMap(VFadeInThenOut, rects, lag_ratio=0.5, run_time=5),
        )
        self.wait()


class PowerOfTwoPositions(Scene):
    def construct(self):
        block = get_bit_grid(4, 4)
        block.set_height(5)
        block.to_edge(LEFT, buff=LARGE_BUFF)
        boxes = get_bit_grid_boxes(block)

        numbers = VGroup(*[
            Integer(n).move_to(box)
            for n, box in enumerate(boxes)
        ])

        self.add(numbers)
        self.wait()
        for n in range(4):
            numbers[2**n].scale(1.5)
            numbers[2**n].set_color(YELLOW)
            self.wait(0.25)
        self.wait()


class OneGroupPerParityBit(Scene):
    def construct(self):
        N = 4
        block = get_bit_grid(2**(N // 2), 2**(N // 2))
        block.set_height(5)
        block.to_edge(LEFT, buff=LARGE_BUFF)
        boxes = get_bit_grid_boxes(block)
        pos_labels = get_grid_position_labels(boxes)

        for bit in block:
            bit.scale(0.7)

        parity_boxes = VGroup(*[boxes[2**n] for n in range(N)])
        parity_boxes.set_fill(GREEN, 0.8)
        block.save_state()
        self.add(boxes, pos_labels, block)
        for n in range(4):
            block.restore()
            get_bit_n_subgroup(block, n, 0).set_fill(opacity=0)
            self.wait(1.5)


class LetsWalkThroughAnExample(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Can we walk through\\\\a full example?",
            student_index=1,
            added_anims=[self.teacher.change, "happy"]
        )
        self.change_student_modes("hooray", None, "hooray")
        self.wait(5)
        self.teacher_says(
            "But of\\\\course!",
            target_mode="tease"
        )
        self.change_student_modes("happy", "coin_flip_1", "happy")
        self.wait(4)


class FullExampleWithNewEnd(Scene):
    CONFIG = {
        "random_seed": 3,
    }

    def construct(self):
        # Pull bits out of an image
        image = ImageMobject("Tom_In_Bowtie")
        image.set_height(6)
        image.to_edge(LEFT, buff=LARGE_BUFF)

        bits = get_image_bits(image)
        bits.match_height(image)
        bits.generate_target()
        bits.target.arrange_in_grid(n_cols=11, h_buff=SMALL_BUFF, v_buff=MED_SMALL_BUFF)
        bits.target.next_to(image, RIGHT, LARGE_BUFF, UP)
        for bit, bt in zip(bits, bits.target):
            bit.save_state()
            bit.target = bt
            bit.fade(0.9)

        words = TextMobject("11-bit\\\\chunks")
        words.scale(1.5)
        words.to_edge(RIGHT)
        lines = VGroup()
        for bit in bits.target[10:200:11]:
            line = Line(RIGHT, LEFT)
            line.set_stroke(BLUE, 1)
            line.bit = bit
            line.word = words[0][0]
            line.add_updater(lambda m: m.put_start_and_end_on(
                m.word.get_left() + SMALL_BUFF * LEFT,
                m.bit.get_right() + SMALL_BUFF * RIGHT,
            ))
            lines.add(line)

        self.add(image)
        self.add(bits)
        self.save_state()
        self.play(
            LaggedStartMap(
                Succession, bits,
                lambda m: (Restore(m), MoveToTarget(m)),
                lag_ratio=3 / len(bits),
            ),
            Write(words, rate_func=squish_rate_func(smooth, 0.5, 0.7)),
            ShowCreation(lines, lag_ratio=0.1, rate_func=squish_rate_func(smooth, 0.5, 1)),
            run_time=8
        )

        for line, bit in zip(lines, bits[10::11]):
            line.bit = bit

        for bit in bits:
            if bit.get_center()[1] < -FRAME_HEIGHT / 2:
                bits.remove(bit)

        self.wait()

        # Show many 16 bit blocks
        bits.generate_target()
        bits.target.scale(1.5)
        bits.target.arrange_in_grid(n_cols=11, h_buff=SMALL_BUFF, v_buff=LARGE_BUFF)
        bits.target.move_to(bits, UR)

        box_groups = VGroup()
        box_arrows = VGroup()
        for bit in bits.target[0:77:11]:
            boxes = VGroup(*[Square() for x in range(16)])
            boxes.arrange_in_grid(4, 4, buff=0)
            boxes.set_height(0.8)
            boxes.next_to(bit, LEFT, buff=1.5)
            boxes.set_stroke(GREY_B, 2)
            arrow = Arrow(bit.get_left(), boxes.get_right())
            box_arrows.add(arrow)
            box_groups.add(boxes)

        self.play(
            FadeOut(image, 2 * LEFT),
            MoveToTarget(bits, run_time=2),
            LaggedStartMap(FadeIn, box_groups, run_time=4),
            LaggedStartMap(GrowArrow, box_arrows, run_time=4),
        )
        self.wait()

        # Isolate to one box
        first_bits = bits[:11]
        first_boxes = box_groups[0]

        first_bits.generate_target()
        first_bits.target.set_height(0.6)
        first_bits.target.to_edge(UP)
        first_bits.target.set_x(-3)
        first_boxes.generate_target()
        first_boxes.target.set_height(5)
        first_boxes.target.next_to(first_bits.target, DOWN, LARGE_BUFF)

        self.play(
            MoveToTarget(first_bits),
            MoveToTarget(first_boxes),
            LaggedStart(*map(FadeOut, [
                *bits[11:], box_arrows, box_groups[1:],
                *lines, words,
            ]), lag_ratio=0.01),
            run_time=2
        )

        bits = first_bits
        boxes = first_boxes

        # Try it yourself
        morty = Mortimer()
        morty.to_edge(DR)
        self.play(
            PiCreatureSays(morty, "Try it\\\\yourself", target_mode="hooray"),
            VFadeIn(morty)
        )
        self.play(Blink(morty))
        self.wait(2)
        self.play(LaggedStart(
            FadeOut(morty),
            FadeOut(morty.bubble),
            FadeOut(morty.bubble.content),
        ))

        # Fill block
        N = 4
        ecc_boxes = VGroup(*[boxes[2**n] for n in range(N)])
        message_boxes = VGroup(*[
            box for box in boxes[1:]
            if box not in ecc_boxes
        ])
        pos_labels = get_grid_position_labels(boxes, height=0.2)
        pos_labels.set_color(GREY_B)

        self.play(
            ecc_boxes.set_fill, GREEN, 0.7,
            boxes[0].set_fill, YELLOW, 0.5,
            FadeIn(pos_labels, lag_ratio=0.1)
        )
        self.wait()

        self.play(LaggedStart(*[
            ApplyMethod(bit.move_to, box)
            for bit, box in zip(bits, message_boxes)
        ], run_time=4, lag_ratio=0.3))
        self.wait()

        # Organize bits properly
        bit_template = bits[0].copy()
        if get_bit_mob_value(bit_template) == 1:
            toggle_bit(bit_template)

        new_bits = [None] * 16
        for i in [0, 1, 2, 4, 8]:
            new_bits[i] = bit_template.copy()
            new_bits[i].move_to(boxes[i])

        bits_iter = iter(bits)
        for i, new_bit in enumerate(new_bits):
            if new_bit is None:
                new_bits[i] = next(bits_iter)

        bits = VGroup(*new_bits)

        # Show parity groups
        boxes.save_state()
        self.add(boxes, pos_labels, bits)
        for bit in bits:
            for part in bit:
                if part.get_fill_opacity() > 0:
                    part.set_fill(opacity=1)
            bit.save_state()
        VGroup(*bits[:3], bits[4], bits[8]).set_opacity(0)

        for n in range(N):
            boxes.generate_target()
            boxes.target.set_fill(BLACK, 0)
            get_bit_n_subgroup(boxes.target, n).set_fill(BLUE, 0.8)
            for k in range(n):
                boxes.target[2**k].set_fill(GREEN, 0.5)
            one_rects = get_one_rects(get_bit_n_subgroup(bits, n))
            counter = get_ones_counter(boxes[10:12], one_rects, buff=1.5)
            counter.match_height(bits[0])

            self.play(MoveToTarget(boxes))
            self.add(counter)
            self.play(ShowIncreasingSubsets(one_rects))
            self.wait()
            self.play(Restore(bits[2**n]))
            if counter.get_value() % 2 == 1:
                rect_copy = one_rects[0].copy()
                rect_copy.move_to(bits[2**n])
                one_rects.add(rect_copy)
                bits[2**n][0].set_opacity(1)
                toggle_bit(bits[2**n])
                self.add(rect_copy)
                self.wait()
            self.play(
                LaggedStartMap(FadeOut, VGroup(*one_rects, counter), run_time=1),
            )
        self.play(Restore(boxes))

        # Final parity check
        one_rects = get_one_rects(bits)
        counter = get_ones_counter(boxes[10:12], one_rects, buff=1.5)
        counter.match_height(bits[0])

        self.add(counter)
        self.play(ShowIncreasingSubsets(one_rects))
        self.wait()
        self.play(Restore(bits[0]))
        self.play(LaggedStartMap(FadeOut, VGroup(*one_rects, counter)))
        self.wait()

        # Send as a message
        block_group = VGroup(boxes, pos_labels, bits)
        pis, names = get_sender_and_receiver()
        randy, morty = pis

        line = Line(randy.get_corner(UR), morty.get_corner(UL), buff=MED_SMALL_BUFF)
        line.add(
            Dot().move_to(line.get_start(), RIGHT),
            Dot().move_to(line.get_end(), LEFT),
        )
        line.set_stroke(GREY, 2)
        line_label = TextMobject("Noisy channel")
        line_label.next_to(line, DOWN, SMALL_BUFF)
        line_label.set_color(RED)

        self.play(
            VFadeIn(pis),
            FadeIn(names, DOWN),
            randy.change, "raise_right_hand",
            block_group.set_height, 1,
            block_group.move_to, randy.get_corner(UR), DOWN,
            block_group.shift, 0.1 * UP,
        )
        self.play(
            ShowCreation(line),
            Write(line_label)
        )
        self.play(Blink(randy))
        self.play(
            block_group.match_x, line,
            randy.change, "happy", morty.eyes,
        )

        # Possible changes
        black_box = SurroundingRectangle(block_group, buff=0)
        black_box.set_fill(GREY_D, 1)
        black_box.set_stroke(WHITE, 2)
        change_words = VGroup(
            TextMobject("Maybe flip 0 bits"),
            TextMobject("Maybe flip 1 bit"),
            TextMobject("Maybe flip 2 bits"),
        )
        colors = [WHITE, RED_B, RED]
        for word, color in zip(change_words, colors):
            word.next_to(black_box, UP)
            word.set_color(color)

        morty_arrow = Vector(DOWN)
        morty_arrow.next_to(morty, UP)

        self.play(
            GrowArrow(morty_arrow),
            morty.change, "pondering", morty_arrow
        )
        self.play(ShowCreationThenFadeAround(morty))
        self.play(Blink(morty))
        self.wait()
        self.play(
            morty_arrow.next_to, block_group, UP,
            FadeIn(black_box),
            morty.look_at, black_box,
        )
        self.play(Blink(randy))
        self.wait()
        self.play(Blink(randy))
        self.play(
            FadeIn(change_words[0], 0.25 * DOWN),
            FadeOut(morty_arrow, UP),
            morty.change, "confused", change_words[0],
        )
        for i in [1, 2]:
            self.play(
                FadeIn(change_words[i], 0.25 * DOWN),
                change_words[:i].shift, UP,
            )
        self.wait()
        self.play(Blink(morty))

        error_pos = 10
        toggle_bit(bits[error_pos])

        self.add(block_group, black_box)
        self.play(
            FadeOut(black_box),
            FadeOut(change_words),
        )
        self.play(
            block_group.set_x, line.get_end()[0],
            morty.change, "pondering", line.get_end() + UP,
        )
        self.play(
            Uncreate(line),
            FadeOut(line_label, DOWN),
            FadeOut(randy, DL),
            FadeOut(morty, DR),
            FadeOut(names, DOWN),
            block_group.set_height, 5,
            block_group.set_y, 0,
            block_group.to_edge, RIGHT,
        )
        self.wait()

        # Try it!
        try_it_words = TextMobject("Try it\\\\yourself!")
        try_it_words.scale(2)
        try_it_words.next_to(boxes, LEFT, buff=2)
        self.play(FadeIn(try_it_words, RIGHT))
        self.wait()
        self.play(FadeOut(try_it_words, LEFT))

        # Do parity checks
        working_grid = boxes.copy()
        working_grid.to_edge(LEFT)
        working_grid_words = TextMobject("Possibilities")
        working_grid_words.set_color(BLUE)
        working_grid_words.next_to(working_grid, UP)
        working_grid.set_fill(BLUE, 0.7)
        working_pos_labels = get_grid_position_labels(working_grid)

        counter = Integer(0)
        counter.set_height(0.7)
        counter.set_color(YELLOW)
        counter.next_to(boxes, LEFT, MED_LARGE_BUFF)
        counter.counted = VGroup()
        counter.add_updater(lambda m: m.set_value(len(m.counted)))
        for n in range(N):
            off_bits = get_bit_n_subgroup(bits, n, 0)
            on_bits = get_bit_n_subgroup(bits, n, 1)
            rects = get_one_rects(on_bits)
            counter.counted = rects

            self.play(FadeOut(off_bits))
            self.add(counter)
            self.play(ShowIncreasingSubsets(rects))

            to_fade = get_bit_n_subgroup(working_grid, n, 1 - (len(rects) % 2))
            if n == 0:
                to_fade.set_fill(BLACK, 0)
                self.play(
                    FadeIn(working_grid),
                    FadeIn(working_pos_labels),
                    FadeIn(working_grid_words),
                )
            else:
                self.play(to_fade.set_fill, BLACK, 0)
            self.wait()
            self.play(
                FadeOut(counter),
                FadeOut(rects),
                FadeIn(off_bits),
            )

        # Move working grid
        self.add(working_grid, block_group)
        self.play(
            ApplyMethod(working_grid.move_to, boxes, run_time=2),
            FadeOut(working_grid_words),
            FadeOut(working_pos_labels),
        )

        # Full parity check
        rects = get_one_rects(bits)
        counter.counted = rects
        self.add(counter)
        self.play(ShowIncreasingSubsets(rects))
        self.wait()
        self.play(FadeOut(rects), FadeOut(counter))

        # Correct error bit
        self.play(toggle_bit_anim(bits[error_pos]))
        self.play(FadeOut(working_grid))
        self.wait()

        # Show 11 message bits
        block_group.generate_target()
        block_group.target.center()
        block_group.target.to_edge(DOWN)
        VGroup(*[
            block_group.target[2][i]
            for i in [0, 1, 2, 4, 8]
        ]).set_color(GREY_C)
        self.play(MoveToTarget(block_group))

        message_bits = VGroup(*[
            bit for i, bit in enumerate(bits)
            if i not in [0, 1, 2, 4, 8]
        ])
        message_bits.generate_target()
        message_bits.target.arrange(RIGHT, buff=SMALL_BUFF)
        message_bits.target.to_edge(UP)
        for mb, mt in zip(message_bits, message_bits.target):
            mb.target = mt

        self.play(LaggedStartMap(
            MoveToTarget, message_bits,
            lag_ratio=0.3,
            run_time=4,
        ))
        self.wait()

    def old_parity_checks(self):
        questions = VGroup(*[boxes.copy() for x in range(4)])
        questions.set_height(1)
        questions.arrange(DOWN, buff=0.5)
        questions.set_height(6)
        questions.to_edge(LEFT, buff=1)

        counter = Integer(0, color=YELLOW)
        counter.match_height(bits[0])
        counter.next_to(boxes, LEFT, LARGE_BUFF)

        boxes.save_state()
        self.add(boxes, pos_labels, bits)
        results = VGroup()
        for n, question in enumerate(questions):
            question.set_fill(BLACK, 0)
            get_bit_n_subgroup(question, n).set_fill(BLUE, 0.7)

            one_rects = get_one_rects(get_bit_n_subgroup(bits, n))
            counter.set_value(len(one_rects))

            boxes.generate_target()
            boxes.target.match_style(question)

            self.play(MoveToTarget(boxes))
            self.play(FadeIn(one_rects))

            if counter.get_value() % 2 == 0:
                result = Integer(0, color=GREEN)
            else:
                result = Integer(1, color=RED)
            result.next_to(question, RIGHT)
            results.add(result)

            counter_mover = counter.copy()
            counter_mover.generate_target()
            counter_mover.target.replace(result, stretch=True)
            counter_mover.target.fade(1)
            result.save_state()
            result.replace(counter, stretch=True)
            result.fade(1)

            self.play(
                ReplacementTransform(boxes.copy().set_fill(opacity=0), question),
                MoveToTarget(counter_mover, remover=True),
                Restore(result),
                FadeOut(one_rects),
                FadeOut(counter),
            )
        self.wait()

        one_rects = get_one_rects(bits)
        counter.set_value(len(one_rects))
        words = TextMobject("Likely one error")
        words.next_to(counter, DOWN, LARGE_BUFF, aligned_edge=RIGHT)
        self.play(
            boxes.set_fill, BLACK, 0,
            FadeIn(counter),
            FadeIn(one_rects),
        )
        self.wait()
        self.play(FadeIn(words, 0.1 * UP))
        self.wait()
        self.play(
            FadeOut(VGroup(counter, words, one_rects), lag_ratio=0.2)
        )

        # Read result
        final_result = results.copy()
        final_result.arrange(LEFT, buff=SMALL_BUFF)

        equation = VGroup(
            final_result,
            TexMobject("\\rightarrow"),
            Integer(10)
        )
        equation.arrange(RIGHT)
        equation.to_edge(UP)

        self.play(TransformFromCopy(results, final_result, run_time=3, lag_ratio=0.3))
        self.play(
            Write(equation[1]),
            FadeIn(equation[2], LEFT),
        )
        self.wait()
        boxes.generate_target()
        boxes.target[10].set_fill(BLUE, 0.7)
        self.play(MoveToTarget(boxes))
        self.play(toggle_bit_anim(bits[10]))
        self.wait()

        self.play(
            LaggedStartMap(
                FadeOut, VGroup(*equation, *questions, *results),
                lambda m: (m, DOWN),
            ),
            Restore(boxes),
        )


class ByHandVsSoftwareVsHardware(Scene):
    def construct(self):
        self.add(get_background(GREY_E))

        rects = VGroup(*[ScreenRectangle() for x in range(3)])
        rects.set_stroke(GREY_B)
        rects.set_fill(BLACK, 1)
        rects.arrange(RIGHT, buff=MED_LARGE_BUFF)
        rects.set_width(FRAME_WIDTH - 1)
        rects[0].shift(UP)
        rects[2].shift(DOWN)
        self.add(rects)

        labels = VGroup(
            TextMobject("By hand"),
            TextMobject("In software"),
            TextMobject("In hardware"),
        )
        for label, rect in zip(labels, rects):
            label.next_to(rect, DOWN)

        randy = Randolph(height=1.25)
        randy.next_to(rects[0], UP, SMALL_BUFF)

        self.play(
            LaggedStartMap(
                FadeIn, labels,
                lambda m: (m, 0.5 * UP),
                lag_ratio=0.4,
            ),
            randy.change, 'thinking', rects[0],
        )
        self.play(Blink(randy))
        self.wait()

        randy.generate_target()
        randy.target.next_to(rects[1], UP, SMALL_BUFF)
        randy.target.change("hooray", rects[1])
        self.play(
            MoveToTarget(randy, path_arc=-45 * DEGREES)
        )
        self.play(Blink(randy))
        self.play(randy.change, 'thinking', rects[1])
        self.play(Blink(randy))
        self.wait()


class EndScreen(Scene):
    def construct(self):
        self.add(get_background(GREY_E))

        rects = VGroup(*[ScreenRectangle() for x in range(2)])
        rects.set_stroke(WHITE, 1)
        rects.set_fill(BLACK, 1)
        rects.set_height(3)
        rects.arrange(RIGHT, buff=1)
        rects.shift(UP)
        self.add(rects)

        labels = VGroup(
            TextMobject("Part 2\\\\", "the elegance of it all"),
            TextMobject("Ben Eater\\\\", "doing this on breadboards"),
        )

        for label, rect in zip(labels, rects):
            label[0].scale(1.5, about_edge=DOWN)
            label.scale(0.9)
            label.next_to(rect, DOWN)

        self.add(labels)

        self.add(AnimatedBoundary(rects[0]))
        self.wait()
        self.add(AnimatedBoundary(rects[1]))
        self.wait(19)


# Part 2

class Thumbnail2(Scene):
    def construct(self):
        # TODO, improve
        title = TextMobject("Hamming codes\\\\", "part 2")
        title.set_width(FRAME_WIDTH - 4)
        title[0].set_color(BLUE)
        title[1].set_color(GREY_B)
        self.add(title)


class Part1Wrapper(Scene):
    def construct(self):
        self.add(get_background())
        rect = ScreenRectangle()
        rect.set_fill(BLACK, 1)
        rect.set_stroke(GREY_B, 2)
        rect.set_height(6)
        rect.to_edge(DOWN)
        title = TextMobject("Part 1")
        title.set_height(0.7)
        title.to_edge(UP)

        self.add(rect)
        self.add(AnimatedBoundary(rect, max_stroke_width=2, cycle_rate=0.25))
        self.play(Write(title))
        self.wait(35)


class AskHowItsImplemented(TeacherStudentsScene):
    def construct(self):
        self.student_says("How do you\\\\implement this?")
        self.play(
            self.teacher.change, "happy",
            self.get_student_changes("pondering", "confused"),
        )
        self.look_at(self.screen)
        self.wait(6)


class ScaleUp(Scene):
    def construct(self):
        square_template = Square()
        square_template.set_stroke(GREY_B, 2)
        square_template.set_height(1)
        zero = Integer(0)
        one = Integer(1)

        last_grid = None
        last_parity_groups = None
        last_words = None

        for N in range(4, 13):
            grid = VGroup(*[square_template.copy() for x in range(2**N)])
            grid.arrange_in_grid(
                2**int(math.floor(N / 2)),
                2**int(math.ceil(N / 2)),
                buff=0
            )
            grid.set_width(5.5)
            if N > 8:
                grid.set_stroke(width=1)
            elif N > 10:
                grid.set_stroke(width=0.25)
            grid.set_stroke(background=True)

            grid[0].set_fill(YELLOW, 0.6)
            for n in range(N):
                grid[2**n].set_fill(GREEN, 0.7)

            parity_groups = VGroup()
            for n in range(N):
                group = grid.copy()
                group.set_fill(BLACK, 0)
                get_bit_n_subgroup(group, n).set_fill(BLUE, 0.8)
                parity_groups.add(group)
            parity_groups.arrange_in_grid(n_cols=2, buff=1.5)
            parity_groups.set_width(5)
            max_height = 7
            if parity_groups.get_height() > max_height:
                parity_groups.set_height(max_height)
            parity_groups.to_edge(RIGHT, buff=0.5)

            random.seed(0)
            for square in grid:
                bit = random.choice([zero, one]).copy()
                bit.replace(square, dim_to_match=1)
                bit.scale(0.5)
                square.add(bit)

            redun = "{:.3}".format((N + 1) / (2**N))
            words = TexMobject(
                f"""
                {{ {{{N + 1}}} \\text{{ parity bits}}
                \\over
                {2**N} \\text{{ bits per block}} }}
                \\approx {redun}
                """,
                tex_to_color_map={
                    f"{{{N + 1}}}": GREEN,
                    f"{2**N}": WHITE,
                    f"{redun}": YELLOW,
                },
                fill_color=GREY_A
            )
            words.to_corner(UL, buff=MED_SMALL_BUFF)
            grid.next_to(words, DOWN, aligned_edge=LEFT)

            if last_grid is None:
                self.add(grid)
                self.add(parity_groups)
                self.add(words)
            else:
                self.play(
                    ReplacementTransform(last_grid, grid[:2**(N - 1)]),
                    FadeIn(grid[2**(N - 1):], lag_ratio=0.1, run_time=2),
                    FadeOut(last_parity_groups),
                    LaggedStartMap(FadeIn, parity_groups, lag_ratio=0.2, run_time=2),
                    FadeOut(last_words, UP),
                    FadeIn(words, DOWN),
                )
            self.wait()

            last_grid = grid
            last_parity_groups = parity_groups
            last_words = words


class MillionRatio(Scene):
    def construct(self):
        # Largely copied from above
        N = 20
        words = TexMobject(
            """
            {21 \\text{ parity bits}
            \\over
            1{,}048{,}576 \\text{ bits per block} }
            \\approx 0.00002
            """,
            tex_to_color_map={
                "21": GREEN,
                "1{,}048{,}576": WHITE,
                "0.00002": YELLOW,
            },
            fill_color=GREY_A
        )
        words.to_corner(UL, buff=MED_SMALL_BUFF)

        self.add(words)

        st = Square()
        st.set_stroke(GREY, 0.5)
        grid = VGroup(*[st.copy() for x in range(2**(16))])
        grid.arrange_in_grid(buff=0)
        grid.set_height(6)
        grid.next_to(words, DOWN, aligned_edge=LEFT)

        self.add(grid)

        k = 17
        positions = VGroup(*[
            TexMobject(int_to_bit_string(n, n_bits=20))
            for n in [*range(k), *range(2**N - k // 2, 2**N)]
        ])
        positions.replace_submobject(-k // 2, TexMobject("\\vdots"))
        positions.arrange(DOWN)
        positions.set_height(7)
        positions.to_edge(RIGHT)
        for n in [0, 1, 2, 4, 8, 16]:
            positions[n].set_color(GREEN_B)

        brace = Brace(positions, LEFT, buff=SMALL_BUFF)
        p_label = TextMobject("$2^{20}$\\\\positions")
        p_label.next_to(brace, LEFT, SMALL_BUFF)

        self.play(
            ShowIncreasingSubsets(positions, run_time=3),
            GrowFromPoint(brace, brace.get_top(), run_time=3, rate_func=squish_rate_func(smooth, 0.5, 1)),
            FadeIn(p_label, 0.5 * RIGHT, run_time=3, rate_func=squish_rate_func(smooth, 0.5, 1)),
        )
        self.wait()

        grid.set_stroke(background=True)
        for n in range(16):
            grid.set_fill(BLACK, 0)
            get_bit_n_subgroup(grid, n).set_fill(BLUE, 0.8)
            self.wait(0.5)


class BurstErrors(Scene):
    def construct(self):
        # Setup
        bl = 8
        nb = 4

        bits = get_bit_grid(1, bl * nb, bits=string_to_bits("3b1b"))
        bits.set_height(0.5)
        bits.arrange(RIGHT, buff=SMALL_BUFF)
        bits.move_to(DOWN)
        self.add(bits)

        colors = [BLUE, YELLOW, MAROON_B, TEAL]
        block_words = VGroup(*[
            TextMobject(f"Block {n}", fill_color=color)
            for n, color in zip(range(nb), colors)
        ])
        block_words.set_height(0.5)
        block_words.arrange(RIGHT, buff=LARGE_BUFF)
        block_words.move_to(2 * UP)
        self.add(block_words)

        # Add lines
        lines = VGroup()
        for n, bit in enumerate(bits):
            words = block_words[n // bl]
            line = Line()
            line.match_color(words)
            line.set_stroke(width=2)
            line.words = words
            line.bit = bit
            bit.line = line
            underline = Underline(bit)
            underline.set_stroke(words.get_color(), 4)
            bit.add(underline)
            line.add_updater(lambda m: m.put_start_and_end_on(
                m.words.get_bottom() + SMALL_BUFF * DOWN,
                m.bit.get_top(),
            ))
            lines.add(line)

        self.play(LaggedStartMap(ShowCreation, lines, suspend_mobject_updating=True))
        self.wait()

        # Show burst error
        error_bits = bits[9:13]
        error_words = TextMobject("Burst of errors")
        error_words.next_to(error_bits, DOWN)
        error_words.set_color(RED)
        ruined_words = TextMobject("Ruined")
        ruined_words.set_color(RED)
        ruined_words.next_to(block_words[1], UP)
        strike = Line(LEFT, RIGHT)
        strike.replace(block_words[1])
        strike.set_color(RED)

        self.play(
            LaggedStartMap(toggle_bit_anim, error_bits, target_color=RED),
            LaggedStart(*map(zap_anim, error_bits)),
            Write(error_words)
        )
        self.play(
            ShowCreation(strike),
            FadeIn(ruined_words, 0.5 * DOWN)
        )
        self.wait()
        self.play(
            FadeOut(ruined_words, 0.2 * UP),
            FadeOut(error_words, 0.2 * DOWN),
            FadeOut(strike),
            LaggedStartMap(toggle_bit_anim, error_bits, target_color=WHITE),
            run_time=1,
        )
        for bit in error_bits:
            bit[-1].set_color(YELLOW)

        # Rearrange
        new_order = VGroup()
        for i in range(bl):
            for j in range(nb):
                new_order.add(bits[bl * j + i])
        new_order.generate_target()
        new_order.target.arrange(RIGHT, buff=SMALL_BUFF)
        new_order.target.replace(bits)

        self.play(MoveToTarget(new_order, run_time=3, path_arc=30 * DEGREES))
        self.wait()

        # New burst
        error_bits = new_order[9:13]

        self.play(
            LaggedStartMap(toggle_bit_anim, error_bits, target_color=RED),
            LaggedStart(*map(zap_anim, error_bits)),
            Write(error_words),
        )
        non_error_lines = VGroup()
        for line in lines:
            if line.bit not in error_bits:
                non_error_lines.add(line)
        self.play(non_error_lines.set_stroke, {"width": 1, "opacity": 0.5})
        self.wait()

        error_words = VGroup(*[TextMobject("1 error", fill_color=GREEN) for x in range(4)])
        for ew, bw in zip(error_words, block_words):
            ew.next_to(bw, UP, MED_LARGE_BUFF)

        self.play(LaggedStartMap(FadeIn, error_words, lambda m: (m, DOWN)))
        self.wait()


class BinaryCounting(Scene):
    def construct(self):
        def get_bit_grids(bit_values):
            left_bits = get_bit_grid(4, 1, buff=LARGE_BUFF, bits=bit_values, height=6)
            left_bits.move_to(3 * LEFT)
            right_bits = get_bit_grid(1, 4, buff=SMALL_BUFF, bits=bit_values, height=0.6)
            right_bits.set_submobjects(list(reversed(right_bits)))
            right_bits.move_to(RIGHT + 2 * UP)
            return VGroup(left_bits, right_bits)

        bit_grids = get_bit_grids([0, 0, 0, 0])

        brace = Brace(bit_grids[1], UP)
        counter = Integer(0, edge_to_fix=ORIGIN)
        counter.match_height(bit_grids[1])
        counter.set_color(BLUE)
        counter.next_to(brace, UP)

        boxes = VGroup(*[Square() for x in range(16)])
        boxes.arrange_in_grid(4, 4, buff=0)
        boxes.set_height(4)
        boxes.next_to(bit_grids[1], DOWN, LARGE_BUFF)
        boxes.set_stroke(GREY_B, 2)
        pos_labels = get_grid_position_labels(boxes)

        self.add(bit_grids)
        self.add(brace)
        self.add(counter)
        self.add(boxes)
        self.add(pos_labels)

        for n in range(16):
            bit_values = list(map(int, int_to_bit_string(n, n_bits=4)))
            boxes.generate_target()
            boxes.target.set_fill(BLACK, 0)
            boxes.target[n].set_fill(BLUE, 0.8)
            anims = [
                ChangeDecimalToValue(counter, n),
                MoveToTarget(boxes)
            ]
            for grid in bit_grids:
                for bit, bv in zip(grid, reversed(bit_values)):
                    if get_bit_mob_value(bit) != bv:
                        anims.append(toggle_bit_anim(bit))
            self.play(*anims, run_time=0.5)
            self.wait()


class ReviewOfXOR(Scene):
    CONFIG = {
        "random_seed": 2,
    }

    def construct(self):
        # Setup equations
        xor = get_xor()

        equations = VGroup()
        for n in range(4):
            bits = list(map(int, int_to_bit_string(n, n_bits=2)))
            equation = VGroup(
                Integer(bits[0]),
                xor.copy(),
                Integer(bits[1]),
                TexMobject("="),
                Integer(op.xor(*bits)),
            )
            equation.set_height(0.6)
            equation.arrange(RIGHT)
            equations.add(equation)

        equations.arrange(DOWN, buff=LARGE_BUFF)

        # Intro xor
        equation = equations[1]
        equation.save_state()
        equation.center()
        equation[3:].set_opacity(0)

        arrow = Vector(0.7 * DOWN)
        arrow.next_to(equation[1], UP, SMALL_BUFF)
        xor_word = TextMobject("xor")
        xor_word_long = TextMobject("``exclusive or''")
        xor_words = VGroup(xor_word, xor_word_long)
        xor_words.scale(1.5)
        xor_words.match_color(xor)
        xor_words.next_to(arrow, UP)

        self.add(equation)
        self.play(
            FadeIn(equation[1], 0.5 * UP),
            GrowArrow(arrow),
            Write(xor_word),
        )
        self.wait()
        self.play(
            xor_word.next_to, xor_word_long, UP, MED_SMALL_BUFF,
            FadeIn(xor_word_long, DOWN),
        )
        self.wait()
        self.play(
            FadeOut(arrow),
            xor_words.to_corner, UL,
            Restore(equation),
            FadeIn(equations[2], UP),
        )
        self.wait()
        self.play(
            FadeIn(equations[0], DOWN),
            FadeIn(equations[3], UP),
        )
        self.wait()

        # Parity of two bits
        parity_words = TextMobject("Parity of\\\\two bits")
        parity_words.set_color(YELLOW)
        parity_words.scale(1.5)
        parity_words.to_edge(RIGHT, buff=MED_LARGE_BUFF)

        arrows = VGroup()
        for equation in equations:
            globals()['equation'] = equation
            new_arrows = VGroup(*[
                Arrow(equation[i].get_top(), equation[4].get_top(), path_arc=-60 * DEGREES)
                for i in [0, 2]
            ])
            new_arrows.set_color(YELLOW)
            arrows.add(new_arrows)

        self.play(
            LaggedStartMap(DrawBorderThenFill, arrows),
            FadeIn(parity_words)
        )
        self.wait()

        # Addition mod 2
        mod2_words = TextMobject("Addition\\\\mod 2")
        mod2_words.scale(1.5)
        mod2_words.move_to(parity_words, RIGHT)
        mod2_words.set_color(BLUE)

        self.play(
            FadeIn(mod2_words, DOWN),
            FadeOut(parity_words, UP),
            FadeOut(arrows)
        )
        self.wait()

        # xor of two bit strings
        row_len = 8
        bit_strings = VGroup(*[
            Integer(random.choice([0, 1]), edge_to_fix=ORIGIN)
            for x in range(row_len * 3)
        ])
        bit_strings.arrange_in_grid(
            3, row_len,
            h_buff=SMALL_BUFF,
            v_buff=MED_LARGE_BUFF,
            fill_rows_first=False
        )
        bit_strings.scale(equation[0][0].get_height() / bit_strings[0].get_height())
        rows = VGroup(*[bit_strings[i::3] for i in range(3)])
        rows[0].next_to(rows[1], UP, buff=0.25)

        line = Line(LEFT, RIGHT)
        line.set_width(bit_strings.get_width() + 1)
        line.move_to(bit_strings[-2:], RIGHT)
        line.set_stroke(GREY_B, 3)
        line_xor = xor.copy()
        line_xor.set_height(0.5)
        line_xor.next_to(line, UP, aligned_edge=LEFT)

        for b1, b2, b3 in zip(*[row for row in rows]):
            b3.set_value(b1.get_value() ^ b2.get_value())
            b2.match_x(b1)
            b3.match_x(b1)

        equations.generate_target()
        for n, eq in enumerate(equations.target):
            for k, b1 in enumerate(eq[0::2]):
                target_bit = bit_strings[3 * n + k]
                target_bit.set_value(b1.get_value())
                b1.become(target_bit)
            eq[1].become(line_xor)
            eq[3].fade(1)

        self.play(
            MoveToTarget(equations, run_time=2),
            FadeOut(mod2_words),
            FadeIn(bit_strings[12:], run_time=2, rate_func=squish_rate_func(smooth, 0.5, 1), lag_ratio=0.1),
            ShowCreation(line, run_time=2, rate_func=squish_rate_func(smooth, 0.5, 1))
        )
        self.remove(equations)
        self.add(bit_strings, line_xor)
        self.wait()

        # Highlight columns
        last_rect = VMobject()
        for b1, b2, b3 in zip(*[row for row in rows]):
            rect = SurroundingRectangle(VGroup(b1, b2, b3), buff=SMALL_BUFF)
            rect.set_stroke(BLUE, 2)
            self.play(FadeIn(rect), FadeOut(last_rect))
            last_rect = rect
        self.play(FadeOut(last_rect))

        # Add more rows
        new_rows = VGroup(*[rows[0].copy() for x in range(3)])
        new_rows.arrange(DOWN, buff=0.2)
        new_rows.next_to(rows, UP, buff=0.2)
        for row in new_rows:
            for bit in row:
                bit.set_value(random.choice([0, 1]))

        self.play(
            LaggedStartMap(FadeIn, new_rows, lambda m: (m, DOWN)),
            FadeOut(xor_words),
            FadeOut(rows[2])
        )

        # Compute parities
        parity_words = TextMobject("Computes\\\\parity\\\\of each\\\\column", alignment="")
        parity_words.set_color(YELLOW)
        parity_words.to_corner(UL)
        self.add(parity_words)

        for tup in zip(*[*new_rows, *rows]):
            rects = VGroup()
            for bit in tup[:-1]:
                if bit.get_value() == 1:
                    rect = SurroundingRectangle(bit)
                    rect.set_stroke(YELLOW, 2)
                    rect.set_fill(YELLOW, 0.5)
                    rects.add(rect)
            tup[-1].set_value(len(rects) % 2)
            tup[-1].set_color(YELLOW)
            self.add(rects, *tup)
            self.wait()
            self.remove(rects)
        self.wait()

        # Simpler sum
        self.play(FadeOut(
            VGroup(new_rows, rows[0][4:], rows[1][4:], rows[2][4:]),
            lag_ratio=0.1,
        ))
        for b1, b2, b3 in zip(*[row[:4] for row in rows]):
            b3.set_value(b1.get_value() ^ b2.get_value())
            self.wait(0.25)

        arrows = VGroup()
        integers = VGroup()
        for row, n in zip(rows, [3, 5, 6]):
            arrow = Vector(0.75 * RIGHT)
            arrow.next_to(row[:4], RIGHT, buff=0.2)
            integer = Integer(n)
            integer.match_height(row[0])
            integer.match_color(row[0])
            integer.next_to(arrow, RIGHT, buff=0.2)
            self.play(
                GrowArrow(arrow),
                FadeIn(integer, LEFT)
            )

            arrows.add(arrow)
            integers.add(integer)


class ButWhy(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Hang on...\\\\why?", target_mode="confused",
            added_anims=[self.teacher.change, "tease"]
        )
        self.change_student_modes(
            "maybe", "erm", "confused",
            look_at_arg=self.screen,
        )
        self.wait(6)


class WhyPointToError(Scene):
    def construct(self):
        rect = SurroundingRectangle(TextMobject("0000").scale(2))
        rect.to_edge(RIGHT)
        rect.set_stroke(RED, 3)
        words = TextMobject("Why do these\\\\point to an error?")
        arrow = Vector(0.7 * RIGHT)
        arrow.next_to(rect, LEFT)
        words.next_to(arrow, LEFT)
        words.set_color(RED)

        bit = Integer(0).scale(2)
        bit.next_to(words, UP, buff=0.45)
        bit.shift(1.11 * words.get_width() * LEFT)

        self.play(
            Write(words),
            ShowCreation(rect),
        )
        self.play(GrowArrow(arrow))
        self.wait()
        self.play(
            rect.become, SurroundingRectangle(bit).match_style(rect),
            FadeOut(arrow)
        )
        self.wait()


class SimplePointer(Scene):
    def construct(self):
        arrow = Arrow(ORIGIN, [-4, 1.5, 0])
        arrow.center()
        arrow.set_fill(GREY_B)
        self.play(DrawBorderThenFill(arrow))
        self.wait()


class ArrowPair(Scene):
    def construct(self):
        arrows = VGroup(
            Vector(LEFT),
            Vector(LEFT),
        )
        arrows.scale(1.5)
        arrows.arrange(DOWN, buff=2)
        arrows[0].shift(4 * LEFT)
        arrows.set_fill(YELLOW)

        self.play(*map(GrowArrow, arrows))
        self.wait()


class PythonXorExample(ExternallyAnimatedScene):
    pass


class HammingCodesWithXOR(Scene):
    def construct(self):
        # Setup
        bits = get_bit_grid(4, 4, bits=string_to_bits(":)"))
        bits.to_edge(LEFT, buff=1.5)
        boxes = get_bit_grid_boxes(bits)
        block = VGroup(boxes, bits)
        block.set_height(6)
        for bit in bits:
            bit.set_height(0.7)

        bin_pos_labels = VGroup()
        dec_pos_labels = VGroup()
        for n, box, bit in zip(it.count(), boxes, bits):
            bin_label = VGroup(
                *[Integer(int(c)) for c in int_to_bit_string(n, n_bits=4)]
            )
            bin_label.arrange(RIGHT, buff=SMALL_BUFF, aligned_edge=DOWN)
            bin_label.set_color(GREY_B)
            bin_label.set_width(0.7 * box.get_width())
            bin_label.move_to(box, DOWN)
            bin_label.shift(SMALL_BUFF * UP)
            bin_pos_labels.add(bin_label)

            dec_label = Integer(n)
            dec_label.match_height(bin_label)
            dec_label.match_style(bin_label[0])
            dec_label.move_to(bin_label, DR)
            dec_pos_labels.add(dec_label)

            bit.generate_target()
            bit.target.scale(0.9)
            bit.target.move_to(box, UP)
            bit.target.shift(MED_SMALL_BUFF * DOWN)

        # Enumerate
        self.add(block)
        kw = {"lag_ratio": 0.3, "run_time": 2}
        self.play(LaggedStartMap(FadeIn, dec_pos_labels, **kw))
        self.wait()
        kw["lag_ratio"] = 0.1
        self.play(
            LaggedStartMap(FadeOut, dec_pos_labels, **kw),
            LaggedStartMap(FadeIn, bin_pos_labels, **kw),
            LaggedStartMap(MoveToTarget, bits, **kw),
        )
        self.wait()

        # Highlight ones
        summands = VGroup()
        for bit, box, label in zip(bits, boxes, bin_pos_labels):
            for mob in bit, box, label:
                mob.save_state()
                mob.generate_target()

            if get_bit_mob_value(bit) == 1:
                box.target.set_fill(BLUE, 0.7)
                summands.add(label.copy())
            else:
                bit.target.fade(0.5)
                label.target.fade(0.5)

        self.play(*[
            LaggedStartMap(MoveToTarget, mob, lag_ratio=0.02)
            for mob in [boxes, bits, bin_pos_labels]
        ])
        self.wait()

        # Arrange sum
        summands.generate_target()
        summands.target.arrange(DOWN, buff=SMALL_BUFF)
        summands.target.set_width(1.5)
        summands.target.set_color(WHITE)
        summands.target.to_edge(RIGHT, buff=1.5)
        summands.target.to_edge(UP)

        line = Line(LEFT, RIGHT)
        xor = get_xor()
        line.set_width(summands.target.get_width() + 0.75)
        line.next_to(summands.target, DOWN, aligned_edge=RIGHT, buff=SMALL_BUFF)
        xor.next_to(line, UP, aligned_edge=LEFT)

        self.play(
            MoveToTarget(summands, run_time=2),
            ShowCreation(line),
            ShowCreation(xor),
        )
        self.wait()

        # Perform xor
        result = VGroup()
        rect_columns = VGroup()
        for tup in zip(*summands):
            rects = get_one_rects(tup)
            result_bit = get_bit_grid(1, 1, bits=[len(rects) % 2])[0]
            result_bit.replace(tup[-1], dim_to_match=1)
            result_bit.shift(1.5 * result_bit.get_height() * DOWN)
            result_bit.set_color(YELLOW)

            result.add(result_bit)
            rect_columns.add(rects)

        pre_result = VGroup()
        for summand in summands:
            pr = result.copy()
            pr.save_state()
            pr.move_to(summand)
            pr.fade(1)
            pre_result.add(pr)

        self.play(LaggedStartMap(Restore, pre_result, lag_ratio=0.05, remover=True))
        self.add(result)
        self.wait()
        self.play(ShowCreationThenFadeOut(SurroundingRectangle(result, stroke_color=BLUE)))
        self.wait()

        for n, rects, result_bit in zip(it.count(), reversed(rect_columns), reversed(result)):
            faders = VGroup()
            for bit_vect in [*summands, result]:
                for k, bit in enumerate(reversed(bit_vect)):
                    if k != n:
                        bit.generate_target()
                        bit.target.fade(0.7)
                        faders.add(bit)
            for group in bits, bin_pos_labels:
                sg = get_bit_n_subgroup(group, n, 0)
                sg.generate_target()
                sg.target.fade(1)
                faders.add(sg)
            faders.save_state()

            self.play(LaggedStartMap(MoveToTarget, faders, lag_ratio=0, run_time=1))

            new_rects = VGroup()
            for bit, pos in zip(get_bit_n_subgroup(bits, n), get_bit_n_subgroup(bin_pos_labels, n)):
                if get_bit_mob_value(bit) == 1:
                    nr = SurroundingRectangle(pos[3 - n], buff=0.05)
                    nr.set_fill(YELLOW, 0.25)
                    new_rects.add(nr)

            self.play(
                ShowIncreasingSubsets(rects),
                ShowIncreasingSubsets(new_rects),
            )
            self.wait()
            self.play(
                faders.restore,
                FadeOut(rects),
                FadeOut(new_rects),
            )
        self.wait()

        # Sender manipulations (Doing more by hand than should here...sorry)
        parity_highlights = VGroup(*[boxes[2**n].copy() for n in range(4)])
        parity_highlights.set_stroke(GREEN, 8)
        parity_highlights.set_fill(BLACK, 0)
        self.play(ShowCreation(parity_highlights))

        words = TextMobject("Try to make\\\\this 0000")
        words.set_color(GREEN)
        words.next_to(boxes, RIGHT, MED_LARGE_BUFF)
        words.to_edge(DOWN, buff=1)
        arrow = Arrow(words.get_right(), result.get_left(), buff=0.1)
        arrow.get_lp = words.get_right
        arrow.get_rp = result.get_left
        arrow.add_updater(lambda m: m.put_start_and_end_on(
            m.get_lp() + SMALL_BUFF * RIGHT,
            m.get_rp() + SMALL_BUFF * LEFT,
        ))
        self.play(
            Write(words),
            DrawBorderThenFill(arrow),
        )
        self.wait()

        strike = Cross(summands[0])
        strike.set_stroke(RED, 8)
        self.play(ShowCreation(strike))
        self.add(summands[0], strike)
        bits[2].generate_target()
        toggle_bit(bits[2].target)
        bits[2].target.fade(0.5)
        self.play(
            boxes[2].set_fill, BLACK, 0,
            MoveToTarget(bits[2]),
            bin_pos_labels[2].fade, 0.5,
            toggle_bit_anim(result[2]),
            FadeOut(summands[0]),
            FadeOut(strike),
        )
        summands.remove(summands[0])
        self.wait()

        toggle_bit(bits[8].saved_state)
        self.play(
            boxes[8].set_fill, BLUE, 0.7,
            Restore(bits[8]),
            Restore(bin_pos_labels[8]),
        )
        new_term = bin_pos_labels[8].copy()
        new_term.generate_target()
        new_term.target.set_color(WHITE)
        new_term.target.replace(summands[2])
        self.play(
            MoveToTarget(new_term),
            summands[:3].move_to, summands[1], DOWN,
        )
        self.play(toggle_bit_anim(result[0]))
        self.wait()
        summands.set_submobjects([*summands[:3], new_term, *summands[3:]])
        self.play(FadeOut(words), FadeOut(arrow), FadeOut(parity_highlights))

        # Show 0 -> 1 error
        pos = 11
        self.play(
            Restore(bits[pos]),
            Restore(bin_pos_labels[pos]),
        )
        self.play(toggle_bit_anim(bits[pos], target_color=RED))
        self.wait()

        new_term = bin_pos_labels[pos].copy()
        new_term.generate_target()
        new_term.target.set_color(RED)
        new_term.target.replace(summands[5])
        bottom_group = VGroup(summands[5:], xor, line, result)
        bottom_group.save_state()
        self.play(
            MoveToTarget(new_term),
            bottom_group.move_to, summands[6], UR,
        )
        self.wait(0.25)
        nt_copy = new_term.copy()
        self.play(
            nt_copy.replace, result,
            nt_copy.fade, 1,
            *[
                toggle_bit_anim(b1, path_arc=0)
                for b1, b2 in zip(result, new_term)
                if b2.get_value() == 1
            ]
        )
        self.remove(nt_copy)
        self.wait()
        self.play(
            Restore(bottom_group),
            FadeOut(new_term),
            toggle_bit_anim(bits[pos], target_color=WHITE)
        )
        self.play(
            bits[pos].fade, 0.5,
            bin_pos_labels[pos].fade, 0.5,
        )

        # Show 1 -> 0 error
        pos = 6
        self.play(
            toggle_bit_anim(bits[pos], target_color=RED),
            zap_anim(bits[pos]),
        )
        self.wait()

        new_term = bin_pos_labels[pos].copy()
        new_term.generate_target()
        new_term.target.set_color(RED)
        new_term.target.replace(summands[3])
        bottom_group = VGroup(summands[3:], xor, line, result)
        bottom_group.save_state()
        self.play(
            MoveToTarget(new_term),
            bottom_group.move_to, summands[4], UR,
        )

        for bit in result:
            bit[0].set_opacity(1)
            bit[1].set_opacity(0)
        nt_copy = new_term.copy()
        self.play(
            nt_copy.move_to, result,
            nt_copy.fade, 1,
            *[
                toggle_bit_anim(b1, path_arc=0)
                for b1, b2 in zip(result, new_term)
                if b2.get_value() == 1
            ]
        )
        self.remove(nt_copy)
        self.wait()

        brace = Brace(VGroup(summands[2], new_term), LEFT, buff=SMALL_BUFF)
        brace_bits = summands[2].copy()
        for bb in brace_bits:
            bb.set_value(0)
        brace_bits.next_to(brace, LEFT)
        self.play(GrowFromCenter(brace))
        self.play(
            Transform(summands[2].copy().unlock_triangulation(), brace_bits, remover=True),
            ReplacementTransform(new_term.copy().unlock_triangulation(), brace_bits),
        )
        self.wait()

        arrow = Arrow(result.get_left(), bin_pos_labels[pos].get_corner(DR), path_arc=-30 * DEGREES, buff=0.1)
        self.play(DrawBorderThenFill(arrow))
        self.wait()

        self.play(toggle_bit_anim(bits[pos], target_color=WHITE))
        self.play(
            Restore(bottom_group),
            FadeOut(new_term),
            FadeOut(brace),
            FadeOut(brace_bits),
            FadeOut(arrow),
        )
        self.wait()


class HammingSyndromePython(ExternallyAnimatedScene):
    pass


class WhatAboutTwoBitDetection(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "What about\\\\detecting\\\\two bit errors?"
        )
        self.play(
            self.get_student_changes("angry", "maybe", "raise_left_hand"),
            self.teacher.change, "guilty",
        )
        self.look_at(self.screen)
        self.wait(4)
        self.play(self.teacher.change, "happy")
        self.change_student_modes("confused", "erm", "pondering")
        self.wait(3)


class ConflictingViewsOnXor(TeacherStudentsScene):
    def construct(self):
        self.clear()
        self.add(self.pi_creatures)
        self.student_says(
            "Um...can you\\\\say that again?",
            target_mode="confused",
            student_index=2,
            added_anims=[self.teacher.change, "guilty"]
        )
        self.change_student_modes("pondering", "pondering", look_at_arg=self.screen)
        self.wait(2)
        self.student_says(
            "Why didn't you\\\\just use xors\\\\from the start?",
            target_mode="sassy",
            student_index=1,
        )
        self.look_at(self.students[1].bubble)
        self.wait(5)


class CompareXorToParityChecks(Scene):
    def construct(self):
        # Title
        bg_rect = FullScreenRectangle()
        bg_rect.set_fill(GREY_E, 1)
        bg_rect.set_stroke(width=0)
        self.add(bg_rect)

        title = TextMobject("One algorithm, multiple perspectives")
        title.scale(1.5)
        title.to_edge(UP)
        title.add_to_back(Underline(title))
        self.add(title)

        # Options
        rects = VGroup(*[ScreenRectangle() for x in range(3)])
        rects.set_fill(BLACK, 1)
        rects.set_stroke(GREY_B, 3)
        rects.set_height(3)
        rects.arrange(RIGHT, buff=1)
        rects.shift(-rects[:2].get_center())

        labels = VGroup(
            TextMobject("Multiple parity checks"),
            TextMobject("One big xor"),
            TextMobject("Matrix product"),
        )
        for label, rect in zip(labels, rects):
            label.next_to(rect, DOWN)
        labels.set_color(BLUE)

        self.add(rects[:2])
        self.add(labels[:2])

        self.play(Write(title, run_time=2))
        self.wait(2)

        # Hardware/software labels
        hw_label = TextMobject("(nicer for hardware)")
        sw_label = TextMobject("(nicer for software)")

        for l1, l2 in zip(labels, [hw_label, sw_label]):
            l2.next_to(l1, DOWN)

        self.play(FadeIn(hw_label, 0.25 * UP))
        self.wait()
        self.play(FadeIn(sw_label, 0.25 * UP))
        self.wait()

        # Third view
        icons = Group(
            ImageMobject("ParityCheckIcon"),
            ImageMobject("XorViewIcon"),
        )
        for icon, rect in zip(icons, rects):
            icon.replace(rect)
            icon.scale(0.95)

        groups = Group(
            Group(rects[0], labels[0], icons[0], hw_label),
            Group(rects[1], labels[1], icons[1], sw_label),
            Group(rects[2], labels[2]),
        )
        groups.generate_target()
        groups.target[:2].arrange(DOWN, buff=LARGE_BUFF)
        groups.target[:2].match_height(groups.target[2])
        groups.target[2].next_to(groups.target[:2], RIGHT, LARGE_BUFF)
        groups.target.set_height(5)
        groups.target.center()
        groups.target.to_edge(DOWN, buff=1)
        groups[2].set_opacity(0)
        self.play(MoveToTarget(groups))
        self.wait()


class LogTitle(Scene):
    def construct(self):
        title = TextMobject("$\\text{log}_2(256) = 8$ parity checks")
        title.set_height(0.7)
        title.to_edge(UP)
        underline = Underline(title[0][:4])
        underline.set_color(YELLOW)
        self.add(title)
        self.wait()
        self.play(ShowCreationThenFadeOut(underline))
        self.wait()


class MatrixProduct(Scene):
    def construct(self):
        title = TextMobject("(7, 4) Hamming code")
        title.set_height(0.7)
        title.to_edge(UP)
        title.set_color(GREY_A)

        encoder_matrix = np.array([
           [1, 1, 0, 1],
           [1, 0, 1, 1],
           [1, 0, 0, 0],
           [0, 1, 1, 1],
           [0, 1, 0, 0],
           [0, 0, 1, 0],
           [0, 0, 0, 1],
        ])
        message_matrix = np.array([1, 0, 1, 1]).reshape((4, 1))
        result_matrix = np.dot(encoder_matrix, message_matrix) % 2

        kw = {"v_buff": 0.6, "h_buff": 0.75}
        encoder, message, result = [
            IntegerMatrix(matrix, **kw)
            for matrix in [encoder_matrix, message_matrix, result_matrix]
        ]
        equation = VGroup(
            encoder, message, TexMobject("="), result
        )
        equation.arrange(RIGHT, buff=MED_LARGE_BUFF)
        equation.to_edge(LEFT, buff=2)

        # Labels
        message_label = TextMobject("Content")
        message_label.move_to(message)
        message_label.to_edge(DOWN)
        message_arrow = Arrow(
            message_label.get_top(),
            message.get_bottom(),
        )
        message_label.set_color(YELLOW)
        message_arrow.set_color(YELLOW)

        brace = Brace(result, RIGHT)
        brace_text = brace.get_text("Error-resistant\\\\block")
        brace.set_color(BLUE)
        brace_text.set_color(BLUE)

        # Animate
        self.add(title)
        self.add(equation)

        self.play(FadeIn(message_label, UP), GrowArrow(message_arrow))
        self.play(GrowFromCenter(brace), FadeIn(brace_text, LEFT))

        equation.set_fill(opacity=0.8)
        for n in range(encoder.mob_matrix.shape[0]):
            row = VGroup(*encoder.mob_matrix[n, :]).copy()
            col = VGroup(*message.elements).copy()
            rhs = result.mob_matrix[n, 0].copy()

            mult_group = VGroup(row, col, rhs)
            mult_group.set_fill(YELLOW, 1)
            self.play(
                ShowIncreasingSubsets(row),
                ShowIncreasingSubsets(col),
                FadeIn(rhs),
            )
            self.wait()
            self.remove(mult_group)


class TooManyErrorsTripUpHamming(Scene):
    def construct(self):
        title = TextMobject(
            "$>2$ Errors"," $\\Rightarrow$ ", "Invalid decoding"
        )
        title.set_height(0.7)
        title[2].set_color(RED)
        title.to_edge(UP)
        self.add(title)

        block = get_bit_grid(8, 8, bits=string_to_bits("EpicFail"), height=5.5)
        block.next_to(title, DOWN, MED_LARGE_BUFF)
        self.add(block)

        # Animations
        errors = random.sample(list(range(64)), 3)
        kw = {"lag_ratio": 0.5}
        self.play(
            LaggedStart(*[
                zap_anim(block[pos])
                for pos in errors
            ], **kw),
            LaggedStart(*[
                toggle_bit_anim(block[pos], target_color=RED)
                for pos in errors
            ], **kw),
        )

        scanim = scan_anim(block.get_corner(DR) + UR, block, run_time=5, lag_factor=1)
        self.play(scanim)

        self.play(ShowCreationThenFadeOut(Underline(title[2], color=RED)))
        self.wait()


class LouisPasteurQuote(Scene):
    def construct(self):
        quote = TextMobject("``Luck favors a\\\\prepared mind''")
        quote.scale(2)
        quote.set_stroke(BLACK, 8, background=True)
        self.play(Write(quote))
        self.wait()


class ReedSolomonPreview(Scene):
    def construct(self):
        # Setup
        title = TextMobject("Reed-Solomon basic idea")
        title.set_height(0.5)
        title.to_edge(UP, buff=MED_SMALL_BUFF)

        axes = Axes(
            x_range=(-1, 10, 1), y_range=(-1, 8, 1),
            width=12,
            height=7,
        )
        axes.to_edge(DOWN, buff=SMALL_BUFF)
        axes.set_color(GREY_B)

        cubic = axes.get_graph(
            lambda x: -0.05 * x * (x - 2) * (x - 4) * (x - 8) + 2
        )
        cubic.set_stroke(TEAL, 3)

        self.add(title)
        self.add(axes)

        # Data
        dots = VGroup(*[
            Dot(axes.input_to_graph_point(x, cubic))
            for x in range(0, 8)
        ])
        dots[:4].set_color(YELLOW)
        dots[4:].set_color(BLUE)

        # Input words
        input_words = TextMobject("Input data")
        poly_words = TextMobject("Polynomial\\\\fit")
        redundant_words = TextMobject("Redundancy")

        input_words.next_to(dots[:4], UP, buff=2)
        input_words.set_color(YELLOW)
        input_arrows = VGroup(*[
            Arrow(input_words.get_bottom(), dot.get_center())
            for dot in dots[:4]
        ])
        input_arrows.set_fill(YELLOW)

        poly_words.next_to(dots[5], LEFT)
        poly_words.shift(0.5 * UR)
        poly_words.match_color(cubic)

        redundant_words.move_to(dots[4:].get_center(), LEFT)
        redundant_words.shift(2 * DR + DOWN)
        redundant_words.set_color(BLUE)
        redundant_arrows = VGroup(*[
            Arrow(redundant_words.get_corner(UL), dot.get_center())
            for dot in dots[4:]
        ])
        redundant_arrows.set_color(BLUE)

        # Animations
        kw = {"lag_ratio": 0.5}
        self.play(
            FadeIn(input_words),
            LaggedStartMap(FadeIn, dots[:4], lambda m: (m, UP), **kw),
            LaggedStartMap(GrowArrow, input_arrows, **kw),
        )
        self.add(cubic, *dots[:4])
        self.play(
            ShowCreation(cubic),
            Write(poly_words)
        )
        self.wait()
        self.play(
            FadeIn(redundant_words),
            LaggedStartMap(FadeIn, dots[4:], lambda m: (m, DR), **kw),
            LaggedStartMap(GrowArrow, redundant_arrows, **kw),
        )
        self.wait()

        self.play(LaggedStartMap(
            FadeOut, VGroup(*reversed(self.mobjects)),
            lambda m: (m, 0.2 * normalize(m.get_center())),
            lag_ratio=0.1,
            run_time=2,
        ))
        self.wait()


class HammingThinking(Scene):
    def construct(self):
        hamming = ImageMobject("Richard_Hamming")
        hamming.set_height(3)
        hamming.to_corner(DL)
        randy = Randolph()
        randy.set_opacity(0)
        randy.move_to(hamming)

        self.add(hamming)
        self.wait()
        self.play(PiCreatureBubbleIntroduction(
            randy, "What's the most efficient\\\\I could conceivably be?",
            bubble_class=ThoughtBubble,
        ))
        self.wait()


class RandomWalks(Scene):
    def construct(self):
        # Setup
        N_PATHS = 50
        frame = self.camera.frame
        frame.set_height(2 * FRAME_HEIGHT)

        idea_spot = 10 * RIGHT + 3 * UP
        idea_dot = Dot(idea_spot)
        idea_dot.set_color(YELLOW)
        bulb = Lightbulb()
        bulb.next_to(idea_dot, UP)

        start_point = 7 * LEFT + 3 * DOWN
        start_dot = Dot(start_point, color=WHITE)
        start_dot.scale(2)

        self.add(idea_dot, bulb, start_dot)

        # Paths
        paths = VGroup(*[VGroup() for n in range(N_PATHS)])
        for path in paths:
            path.add(Line(start_point, start_point))
            path.set_stroke(WHITE, 3, 0.5)

        path_dots = VGroup()
        for path in paths:
            dot = Randolph(
                mode="thinking", height=0.25,
                # color=random.choice([BLUE_B, BLUE_C, BLUE_D, GREY_BROWN])
            )
            dot.set_stroke(BLACK, 3, background=True)
            dot.path = path
            dot.add_updater(lambda m: m.move_to(m.path[-1].get_end()))
            path_dots.add(dot)

        self.add(paths)
        self.add(path_dots)

        # Perform search
        magic_path = None
        while magic_path is None:
            new_segments = VGroup()
            for path in paths:
                start = path[-1].get_end()

                # Choose random direction based on loosely sniffing out idea spot
                R_vect = start - idea_spot
                R_vect = rotate_vector(10 * R_vect, TAU * random.random())
                point = idea_spot + R_vect
                to_point = point - start
                angle = angle_of_vector(to_point)
                if -3 * PI / 2 < angle <= -PI / 2:
                    vect = DOWN
                elif -PI / 2 < angle <= PI / 2:
                    vect = RIGHT
                elif PI / 2 < angle <= 3 * PI / 2:
                    vect = UP
                else:
                    vect = LEFT

                end = start + vect
                new_segment = Line(start, end)
                new_segment.match_style(path)

                new_segments.add(new_segment)
                path.add(new_segment)

                if np.isclose(end, idea_spot).all():
                    magic_path = path.copy()
            self.play(
                LaggedStartMap(ShowCreation, new_segments, lag_ratio=10 / N_PATHS),
                run_time=0.5,
            )
            self.add(paths)

        # Highlight magic path
        magic_path.set_stroke(YELLOW, 5, 1)
        self.play(
            paths.fade, 0.7,
            ShowCreation(magic_path, run_time=2),
        )
        self.wait()

        fake_path = VMobject()
        fake_path.start_new_path(start_point)
        for segment in magic_path:
            fake_path.add_line_to(segment.get_end())
        fake_path.match_style(magic_path)

        line = Line(start_point, idea_spot)
        line.match_style(magic_path)
        line.set_stroke(TEAL, 8)

        self.add(fake_path, start_dot)
        self.play(
            ApplyMethod(magic_path.set_opacity, 0.5),
            Transform(fake_path, line, run_time=2),
            paths.fade, 0.5,
            path_dots.fade, 0.5,
        )
        self.wait()


class ThinkingInTermsOfBits(Scene):
    def construct(self):
        word = TextMobject("Information")
        word.scale(2)
        word.next_to(ORIGIN, LEFT, buff=0.7)
        bits = get_bit_grid(11, 8, bits=string_to_bits("Information"))
        bits.set_height(6)
        bits.next_to(ORIGIN, RIGHT, buff=0.7)
        bits.set_color(GREY_A)

        for bit in bits:
            toggle_bit(bit)

        bits.shuffle()

        self.add(word)
        self.add(bits)
        self.play(LaggedStartMap(
            toggle_bit_anim, bits,
            lag_ratio=5 / len(bits),
            run_time=3,
        ))
        self.wait(2)


class SimpleHoldUpBackground(TeacherStudentsScene):
    def construct(self):
        self.play(self.teacher.change, "raise_right_hand", 3 * UP)
        self.change_student_modes("pondering", "thinking", "tease", look_at_arg=3 * UP)
        self.wait(4)
        self.change_student_modes("tease", "hesitant", "happy", look_at_arg=3 * UP)
        self.wait(5)


class HammingEndScreen(PatreonEndScreen):
    CONFIG = {
        "scroll_time": 25
    }
