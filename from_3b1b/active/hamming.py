from manimlib.imports import *
from from_3b1b.active.chess import string_to_bools


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
    return VGroup(*[bit for bit in block if get_bit_mob_value(bit) == 1])


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


def get_bit_n_subgroup(mob, n, bit_value=1):
    """
    If we enumerate mob, this returns a subgroup of all elements
    whose index has a binary representation with the n'th bit
    equal to bit_value
    """
    return VGroup(*[
        sm
        for i, sm in enumerate(mob)
        if bool(i & (1 << n)) ^ bool(1 - bit_value)
    ])


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

    return TransformFromCopy(original, bit, path_arc=PI, **kwargs)


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
        in_words = TextMobject("What was\\\\saved")
        in_words.next_to(in_image, DOWN)
        out_image = in_image.copy()
        out_image.to_edge(RIGHT)
        out_words = TextMobject("What is\\\\read")
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

        # # Show some data
        # full_timeline = VGroup(timeline, events)
        # full_timeline.save_state()
        # full_timeline.generate_target()
        # full_timeline.target.scale(0.25)
        # full_timeline.target.to_corner(DL)

        # message = "You+I=:)"
        # alt_message = "You+I=:("
        # bits = get_bit_grid(8, 8, bits=string_to_bits(message))
        # bits.shift(RIGHT)
        # bits_rect = SurroundingRectangle(bits, buff=SMALL_BUFF)
        # bits_rect.set_stroke(WHITE, 2)
        # bits_arrow = Vector(1.5 * LEFT)
        # bits_arrow.next_to(bits_rect, LEFT)
        # bits_label = TextMobject("Data")
        # bits_label.next_to(bits_arrow, UP)
        # message_labels = VGroup(*[
        #     TextMobject(f"``{s}''")
        #     for s in (message, alt_message)
        # ])
        # message_labels.set_color(GREEN_B)
        # message_labels.next_to(bits_arrow, LEFT)

        # image = ImageMobject("Tom_In_Bowtie")
        # sound = get_sound_wave()
        # code = ImageMobject("Hamming_Code_Snippet")
        # code.set_height(1.5)
        # file_types = Group(image, sound, code)
        # for file in file_types:
        #     file.next_to(bits_arrow, LEFT)

        # ecc_bits = get_bit_grid(1, 6, height=bits[0].get_height())
        # ecc_bits.next_to(bits[-1], RIGHT, MED_SMALL_BUFF)
        # ecc_bits.set_color(YELLOW)
        # ecc_rect = SurroundingRectangle(ecc_bits, buff=SMALL_BUFF)
        # ecc_rect.set_stroke(YELLOW, 2)

        # ecc_label = TextMobject("Some kind of\\\\redundancy")
        # ecc_label.set_color(GREY_A)
        # ecc_label.next_to(ecc_rect, DOWN)

        # self.play(
        #     MoveToTarget(full_timeline, run_time=3),
        #     LaggedStartMap(FadeIn, bits, run_time=2),
        #     ShowCreation(bits_rect, run_time=2),
        #     Write(bits_label),
        # )
        # self.play(
        #     FadeIn(message_labels[0], RIGHT),
        #     GrowArrow(bits_arrow)
        # )
        # self.wait()
        # curr_file = message_labels[0]
        # files = [*file_types, message_labels[0]]
        # anim_types = [image_reveal_animation, Write, FadeIn, FadeIn]
        # for file, anim_type in zip(files, anim_types):
        #     anim = anim_type(file)
        #     self.add(anim.mobject, curr_file)
        #     self.play(
        #         anim,
        #         FadeOut(curr_file),
        #         run_time=1
        #     )
        #     self.wait()
        #     curr_file = file

        # ecc_rect.save_state()
        # ecc_rect.stretch(0, 0, about_edge=LEFT)
        # self.play(
        #     LaggedStartMap(FadeIn, ecc_bits),
        #     Restore(ecc_rect),
        #     FadeIn(ecc_label, UP),
        # )
        # self.wait()

        # # Show Error
        # bolt = SVGMobject("lightning_bolt")
        # bolt.set_height(0.5)
        # bolt.set_color(RED)
        # bolt.move_to(bits[-1].get_center(), DL)

        # self.play(
        #     ShowCreation(bolt),
        #     ApplyMethod(bits[-1].set_color, RED),
        # )
        # self.play(
        #     FadeOut(bolt),
        #     toggle_bit_anim(bits[-1]),
        # )
        # self.play(
        #     FadeOut(message_labels[0]),
        #     FadeIn(message_labels[1]),
        # )
        # self.wait()

        # # Show correction
        # ecc_lines = VGroup(*[
        #     Line(ecc_rect.get_top(), bit.get_center())
        #     for bit in bits
        # ])
        # ecc_lines.set_stroke(YELLOW, 1)
        # self.play(
        #     LaggedStartMap(ShowCreationThenFadeOut, ecc_lines, lag_ratio=0.01)
        # )

        # new_rect = SurroundingRectangle(bits[-1], buff=SMALL_BUFF)
        # self.play(TransformFromCopy(ecc_rect, new_rect))
        # self.play(toggle_bit_anim(bits[-1]))
        # self.play(
        #     bits[-1].set_color, WHITE,
        #     FadeOut(message_labels[1]),
        #     FadeIn(message_labels[0]),
        # )
        # self.play(FadeOut(new_rect))
        # self.wait()

        # # Bring back time line
        # data_pile = VGroup(
        #     message_labels[0],
        #     bits_arrow, bits_label, bits_rect, bits,
        #     ecc_bits, ecc_rect, ecc_label,
        # )

        # self.play(
        #     ApplyMethod(data_pile.scale, 0, {"about_edge": DR}, remover=True),
        #     Restore(full_timeline, run_time=2)
        # )
        # self.wait()

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

        words = TextMobject("How to invent")
        words.match_height(hamming_word[0][0])
        words.next_to(events[0], UP, buff=0.3)
        words.set_color(BLUE)

        self.play(Write(words))
        hamming_word.add(words)
        self.wait()

        hamming_word.generate_target()
        hamming_word.target.scale(0.5, about_edge=UL)
        hamming_word.target.set_opacity(0.5)
        hamming_arrow = events[0][1]

        self.play(
            MoveToTarget(hamming_word),
            hamming_arrow.put_start_and_end_on, hamming_word.target.get_bottom(), hamming_arrow.get_end(),
            hamming_arrow.set_opacity, 0.5,
            rs_word.scale, 1.5, {"about_edge": DOWN},
            rs_word.set_opacity, 1,
            events[2][1].set_opacity, 1,
        )
        self.wait()


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
    def construct(self):
        bits = get_bit_grid(
            16, 16,
            bits=string_to_bits("Claude Shannon was a total boss!")
        )
        bits.set_height(7)
        bits.move_to(2 * RIGHT)
        point = 2.5 * LEFT + 2.5 * DOWN
        last_block = VMobject()

        for x in range(10):
            block = get_bit_grid(16, 16, height=7)
            block.move_to(2 * RIGHT)
            syndrome = hamming_syndrome(bit_grid_to_bits(block))

            if random.random() < 0.5:
                syndrome = 0
                toggle_bit(block[syndrome])

            scanim = scan_anim(
                point, bits,
                final_stroke_width=0.2, run_time=2, lag_factor=1,
                show_robot=(x == 0)
            )
            self.play(
                FadeIn(block, 6 * RIGHT),
                FadeOut(last_block, 6 * LEFT),
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
        movers = [d_bits, r_bits, r_boxes]
        for mover in movers:
            mover.save_state()
            mover.generate_target()

        for b1, b2 in zip(it.chain(d_bits.target, r_bits.target), block):
            b1.move_to(b2)

        for box, bit in zip(r_boxes.target, r_bits.target):
            box.move_to(bit)

        self.play(*[
            MoveToTarget(mover, lag_ratio=0.2, run_time=3, path_arc=PI / 4)
            for mover in movers
        ])
        self.wait()

        self.play(*[
            Restore(mover, lag_ratio=0.2, run_time=3, path_arc=PI / 4)
            for mover in movers
        ])
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

        self.add(words)
        self.add(pis)

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
        def get_scanim(n, boxes=boxes, block=block, **kwargs):
            return scan_anim(
                boxes.get_corner(DR) + UR,
                get_bit_n_subgroup(block, n),
                lag_factor=0.5,
                run_time=2,
                **kwargs
            )

        scanim = get_scanim(0)
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
            get_scanim(0, show_robot=False),
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
        scanim = get_scanim(1)
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
        self.play(get_scanim(1, show_robot=False))
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


class HalfAsPowerful(TeacherStudentsScene):
    def construct(self):
        pass
