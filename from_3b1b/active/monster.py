from manimlib.imports import *


MONSTER_SIZE = 808017424794512875886459904961710757005754368000000000
BABY_MONSTER_SIZE = 4154781481226426191177580544000000


def get_monster(height=3):
    monster = SVGMobject("monster")
    monster.set_fill(GREY_BROWN)
    monster.set_stroke(BLACK, 0.1)
    monster.set_height(height)
    return monster


def get_baby_monster():
    return get_monster().stretch(0.7, 1)


def blink_monster(monster):
    monster.generate_target()
    left_eye_points = monster.target[0].points[498:528]
    right_eye_points = monster.target[0].points[582:612]
    for points in left_eye_points, right_eye_points:
        points[:, 1] = points[0, 1]
    return MoveToTarget(monster, rate_func=squish_rate_func(there_and_back, 0.4, 0.6))


def get_size_bars(mob, stroke_width=3, buff=SMALL_BUFF):
    bars = VGroup(*[Line(UP, DOWN) for x in range(2)])
    bars.match_height(mob)
    bars[0].next_to(mob, LEFT, buff=buff)
    bars[1].next_to(mob, RIGHT, buff=buff)
    bars.set_stroke(WHITE, stroke_width)
    return bars


def get_monster_size_label():
    size_label = TextMobject("{:,}".format(MONSTER_SIZE))[0]
    size_parts = VGroup(*[
        size_label[i:i + 12]
        for i in range(0, len(size_label), 12)
    ])
    size_parts.arrange(DOWN, buff=SMALL_BUFF, aligned_edge=LEFT)
    return size_label


def get_snowflake(height=2):
    snowflake = SVGMobject("snowflake")
    snowflake.set_fill(GREY_C, 1)
    snowflake.set_gloss(1)
    snowflake.set_shadow(0.2)
    snowflake.set_stroke(WHITE, 1)
    snowflake.set_height(height)
    return snowflake


def get_cube(color=BLUE_D, opacity=1, height=2, frame=None):
    poor_cube = Cube()
    cube = Cube(square_resolution=(10, 10))
    cube.set_color(color, opacity)
    cube.center()

    for face, p_face in zip(cube, poor_cube):
        face.add(*[
            Line3D(p_face.points[i], p_face.points[j], width=0.02, color=GREY_B)
            for i, j in [(0, 1), (1, 3), (3, 2), (2, 0)]
        ])

    cube.set_height(height)
    return cube


def get_glassy_cube(frame):
    verts = np.array(list(it.product(*3 * [[-1, 1]])))
    edges = [
        (v1, v2)
        for v1, v2 in it.combinations(verts, 2)
        if sum(v1 == v2) == 2
    ]
    corner_dots = Group(*[
        Sphere(resolution=(51, 26),).set_height(0.25).move_to(vert)
        for vert in verts
    ])
    corner_dots.set_color(GREY_B)
    edge_rods = Group(*[
        Line3D(v1, v2)
        for v1, v2 in edges
    ])

    faces = Cube(square_resolution=(10, 10))
    faces.set_height(2)
    faces.set_color(BLUE_E, 0.3)
    faces.add_updater(lambda m, f=frame: m.sort(lambda p: np.dot(p, [np.sign(f.euler_angles[0]) * 0.2, -1, 0.2])))

    cube = Group(corner_dots, edge_rods, faces)
    cube.corner_dots = corner_dots
    cube.edge_rods = edge_rods
    cube.faces = faces
    return cube


def get_rot_icon(degrees, mobject, mini_mob_height=1.25):
    mini_mob = mobject.copy()
    temp_height = 1.75
    mini_mob.set_height(temp_height)
    mini_mob.set_stroke(width=0)
    mini_mob.center()
    angle = min(degrees * DEGREES, 170 * DEGREES)
    arc1 = Arrow(
        RIGHT, rotate_vector(RIGHT, angle),
        path_arc=angle,
        buff=0
    )
    arc2 = arc1.copy().rotate(PI, about_point=ORIGIN)
    label = Integer(degrees, unit="^\\circ")
    label.set_height(0.25)
    half_vect = rotate_vector(RIGHT, angle / 2)
    label.next_to(half_vect, half_vect, buff=MED_SMALL_BUFF)
    icon = VGroup(mini_mob, arc1, arc2, label)
    icon.scale(mini_mob_height / temp_height)
    return icon


def get_flip_icon(angle, mobject, opacity=0.75, mini_mob_height=1.25):
    mini_mob = mobject.copy()
    mini_mob.set_stroke(width=0)
    mini_mob.set_fill(opacity=opacity)
    mini_mob.set_height(mini_mob_height)
    mini_mob.center()
    sym_line = DashedLine(LEFT, RIGHT)
    sym_line.set_stroke(WHITE, 2)
    sym_line.set_width(1.2 * mini_mob_height)
    sym_line.rotate(angle)
    sym_line.move_to(mini_mob)
    back_line = sym_line.copy()
    back_line.set_stroke(BLACK, 5)
    return VGroup(mini_mob, back_line, sym_line)


def get_permutation_arrows(mobs, permutation, arc=PI / 2):
    arrows = VGroup()
    for i in range(len(permutation)):
        j = permutation[i]
        u = -1 if mobs[i].get_x() < mobs[j].get_x() else 1
        arrow = Arrow(
            mobs[i].get_edge_center(u * UP),
            mobs[j].get_edge_center(u * UP),
            buff=SMALL_BUFF,
            path_arc=arc,
        )
        arrow.insert_n_curves(10)
        arrow.set_stroke(BLACK, 2, background=True)
        arrow.set_fill(BLUE, 0.8)
        arrows.add(arrow)
    return arrows


def permutation_animation(mobs, perm=None, arc=PI / 2, lag_factor=3, run_time=None):
    if perm is None:
        targets = list(mobs)
        random.shuffle(targets)
    else:
        targets = [mobs[i] for i in perm]

    kw = {"lag_ratio": lag_factor / len(mobs)}
    if run_time is not None:
        kw["run_time"] = run_time
    return LaggedStart(
        *[
            ApplyMethod(m1.move_to, m2, path_arc=arc)
            for m1, m2 in zip(mobs, targets)
        ],
        **kw
    )


def get_named_image(name, height=3):
    image = ImageMobject(name)
    image.set_height(height)

    name = TextMobject(name)
    name.match_width(image)
    name.next_to(image, DOWN)
    group = Group(image, name)
    return group


# Scenes

class Thumbnail(Scene):
    def construct(self):
        monster = get_monster()
        monster.set_height(7)
        monster.to_edge(LEFT)
        monster.set_gloss(0.2)

        words = TextMobject("The\\\\Monster", alignment="")
        words.scale(3)
        words.to_edge(RIGHT)

        self.add(monster)
        self.add(words)


class AskAboutFavoriteMegaNumber(TeacherStudentsScene):
    CONFIG = {
        "background_color": BLACK,
    }

    def construct(self):
        self.remove(self.pi_creatures)
        # YouTubers
        title = TextMobject("What's your favorite number $> 1{,}000{,}000$?")
        title.set_width(FRAME_WIDTH - 1)
        title.to_edge(UP)

        images = Group(
            ImageMobject("standupmaths"),
            ImageMobject("singingbanana"),
            ImageMobject("Ben Sparks"),
            ImageMobject("Zoe Griffiths"),
            ImageMobject("tomrocksmaths"),
            ImageMobject("James Tanton"),
            ImageMobject("blackpenredpen"),
            ImageMobject("Eddie Woo"),
        )
        images.arrange_in_grid(2, 4, buff=MED_LARGE_BUFF)
        images.set_width(FRAME_WIDTH - 2)
        images.next_to(title, DOWN, MED_LARGE_BUFF)

        self.play(
            FadeIn(title, DOWN),
            LaggedStartMap(
                FadeIn, images,
                lambda m: (m, -0.1 * m.get_center()),
                lag_ratio=0.3,
                run_time=5,
            )
        )
        self.wait()

        # Pi Creatures
        self.teacher_says(
            "And we want\\\\you to join!",
            target_mode="surprised",
            bubble_kwargs={
                "height": 3,
                "width": 4,
            },
            added_anims=[
                VFadeIn(self.pi_creatures),
                images.scale, 0.2,
                images.space_out_submobjects, 10,
                images.set_opacity, 0,
            ],
        )
        self.remove(images)
        self.change_student_modes("guilty", "hooray", "wave_2")
        self.wait(5)


class IntroduceMonsterSize(Scene):
    def construct(self):
        # Show number
        max_width = FRAME_WIDTH - 1
        size_label = TextMobject("{:,}".format(MONSTER_SIZE))[0]
        size_label.set_width(max_width)

        n_syms = len(size_label)
        partials = VGroup()
        for n in range(len(size_label) + 1):
            partial = size_label[:n].copy()
            partial.set_height(1.5)
            if partial.get_width() > max_width:
                partial.set_width(max_width)
            partial.center()
            partial.set_color(interpolate_color(BLUE, YELLOW, n / n_syms))
            partials.add(partial)

        self.play(
            UpdateFromAlphaFunc(
                size_label,
                lambda m, a: m.set_submobjects(
                    partials[int(a * n_syms)].submobjects
                ),
                run_time=6,
                rate_func=bezier([0, 0, 1, 1])
            )
        )
        self.wait()

        # Show factorization
        factors = TexMobject(
            r"= 2^{46} \cdot 3^{20} \cdot 5^{9} \cdot 7^{6} \cdot 11^{2} \cdot 13^{3} \cdot 17 \cdot 19 \cdot 23 \cdot 29 \cdot 31 \cdot 41 \cdot 47 \cdot 59 \cdot 71"
        )
        factors.set_width(max_width)
        approx = TexMobject("\\approx 8\\times 10^{53}")
        approx.set_height(0.8)
        approx.move_to(DOWN)
        factors.next_to(approx, UP, buff=MED_LARGE_BUFF)

        self.play(
            size_label.next_to, factors, UP, MED_LARGE_BUFF,
            FadeIn(factors, 0.5 * DOWN),
            Write(approx),
        )
        self.wait()

        value_group = VGroup(size_label, factors, approx)

        # Jupiter
        jupiter = TexturedSurface(Sphere(), "JupiterTexture")
        jupiter.rotate(90 * DEGREES, RIGHT)
        jupiter.set_height(3.5)
        jupiter.to_edge(DOWN)
        jupiter.add_updater(lambda m, dt: m.rotate(-0.1 * dt, UP))
        jupiter.set_shadow(0.9)

        self.play(
            UpdateFromAlphaFunc(jupiter, lambda m, a: m.set_opacity(a)),
            ApplyMethod(value_group.to_edge, UP, run_time=2)
        )
        self.wait(4)

        # Alternate intelligences
        alien = SVGMobject("alien")
        alien.set_height(3)
        alien.to_corner(DL)
        alien.set_stroke(GREEN, width=0)
        alien.set_fill(GREEN_E, 1)

        server = SVGMobject("server_stack")
        server.set_height(3)
        server.to_corner(DR)
        server.set_stroke(BLACK, 2)
        server.set_fill(GREY, 1)
        server.set_gloss(0.5)

        alien_words = TextMobject("Interesting!")
        alien_words.set_color(GREEN)
        alien_words.next_to(alien, UR, buff=-MED_SMALL_BUFF)
        server_words = TextMobject("Very interesting\\\\indeed!")
        server_words.next_to(server, LEFT)

        self.play(
            FadeOut(jupiter, DOWN),
            DrawBorderThenFill(alien),
        )
        self.play(Write(server))
        self.wait()
        for words in alien_words, server_words:
            self.play(Write(words, run_time=1))
            self.wait()

        # What is it?
        question = TextMobject("What is it?")
        question.scale(2)
        question.move_to(UP)

        self.play(
            LaggedStartMap(
                FadeOut,
                VGroup(factors, approx, alien_words, alien, server_words, server),
                lambda m: (m, DOWN),
            ),
            ApplyMethod(size_label.move_to, 0.5 * DOWN, run_time=2),
            FadeIn(question, UP, run_time=2, rate_func=squish_rate_func(smooth, 0.5, 1)),
        )
        self.wait()

        monster = get_monster()
        monster.next_to(size_label, UP)
        monster.to_edge(RIGHT, buff=2)
        m_size_bars = get_size_bars(monster, buff=MED_SMALL_BUFF, stroke_width=5)

        self.play(
            question.shift, 2 * LEFT,
            DrawBorderThenFill(monster),
            run_time=2,
        )
        self.play(ShowCreation(m_size_bars, lag_ratio=0.4))
        self.wait(2)
        self.play(LaggedStart(*[
            FadeOut(mob, DOWN)
            for mob in self.mobjects
        ]))


class IntroduceGroupTheory(Scene):
    def construct(self):
        # Title
        over_title = TextMobject("An introduction\\\\to")
        over_title.scale(2.5)
        over_title.move_to(ORIGIN, DOWN)

        title = TextMobject("Group theory")
        title.scale(2.5)
        title.next_to(over_title, DOWN, buff=0.5)

        arrows = VGroup(Vector(DOWN), Vector(UP))
        arrows.arrange(RIGHT, buff=SMALL_BUFF)
        arrows.scale(2)
        arrows.next_to(title, DOWN, buff=MED_LARGE_BUFF)

        sym_amb = SVGMobject("symmetry_ambigram")
        sym_amb.set_stroke(width=0)
        sym_amb.set_fill(BLUE, 1)
        sym_amb.match_width(title)
        sym_amb.next_to(arrows, DOWN)
        sym_amb_ghost = sym_amb.copy()
        sym_amb_ghost.set_fill(WHITE, 0.2)

        self.add(over_title, title)
        self.wait()
        self.play(
            title.scale, 2.0 / 2.5,
            title.to_edge, UP,
            FadeOut(over_title, UP)
        )

        self.play(FadeIn(title, DOWN))
        self.play(
            LaggedStartMap(GrowArrow, arrows, run_time=1),
            Write(sym_amb, run_time=2)
        )
        self.add(sym_amb_ghost, sym_amb)
        self.play(Rotate(sym_amb, PI, run_time=2))
        self.remove(sym_amb_ghost)
        self.wait()

        # Symmetries of a face
        face = ImageMobject("average_face")
        face.set_height(5)

        sym_word = TextMobject("Symmetric")
        sym_word.scale(2)
        sym_word.to_edge(UP)
        face.next_to(sym_word, DOWN, buff=MED_LARGE_BUFF)
        sym_word.save_state()
        sym_word.replace(sym_amb)
        sym_word.set_opacity(0)

        face_citation = TextMobject("``Average face'' from the Face Research Lab\\\\DeBruine, Lisa \\& Jones, Benedict (2017)")
        face_citation.set_height(0.4)
        face_citation.next_to(face, DOWN)
        face_citation.to_corner(DL)

        sym_line = DashedLine(face.get_top(), face.get_bottom())
        sym_line.scale(1.05)
        sym_line.set_stroke(WHITE, 2)

        self.play(
            FadeIn(face, DOWN),
            FadeIn(face_citation),
            LaggedStartMap(FadeOut, VGroup(*arrows, title), lambda m: (m, UP)),
            sym_amb.replace, sym_word.saved_state, {"stretch": True},
            sym_amb.set_opacity, 0,
            Restore(sym_word),
        )
        self.remove(sym_amb)
        self.wait()
        self.play(ShowCreation(sym_line), FadeOut(face_citation))
        sym_line.rotate(PI)
        self.play(ApplyMethod(face.stretch, -1, 0, run_time=2))
        self.wait()

        sym_to_action = TextMobject("Symmetry", " $\\Rightarrow$ ", "\\emph{Action}")
        sym_to_action.set_color_by_tex("Action", YELLOW)
        sym_to_action.replace(sym_word, dim_to_match=1)
        sym_word.unlock_triangulation()
        self.play(
            ReplacementTransform(sym_word[0], sym_to_action[0]),
            Write(sym_to_action[1]),
            FadeIn(sym_to_action[2], LEFT),
        )
        self.play(ApplyMethod(face.stretch, -1, 0, run_time=2))
        self.wait()

        # Symmetries of a snowflake
        snowflake = get_snowflake()
        snowflake.set_height(5)
        snowflake.next_to(sym_to_action, DOWN, MED_LARGE_BUFF)
        self.play(
            FadeOut(face),
            Uncreate(sym_line),
            ShowCreationThenFadeOut(snowflake.copy().set_stroke(WHITE, 2).set_fill(opacity=0)),
            FadeIn(snowflake, run_time=2),
        )

        def get_flake_rot_icon(degrees, snowflake=snowflake):
            return get_rot_icon(degrees, snowflake)

        def get_flake_flip_icon(angle, snowflake=snowflake):
            return get_flip_icon(angle, snowflake)

        rot_icons = VGroup(
            get_flake_rot_icon(60),
            get_flake_rot_icon(120),
        )
        flip_icons = VGroup(
            get_flake_flip_icon(60 * DEGREES),
            get_flake_flip_icon(30 * DEGREES),
        )
        for icons, vect in [(rot_icons, LEFT), (flip_icons, RIGHT)]:
            icons.arrange(DOWN, buff=MED_LARGE_BUFF)
            icons.to_edge(vect)

        self.play(
            FadeIn(rot_icons[0]),
            Rotate(snowflake, 60 * DEGREES)
        )
        self.wait()
        self.play(
            FadeIn(rot_icons[1]),
            Rotate(snowflake, 120 * DEGREES)
        )
        self.wait()

        sym_line = DashedLine(snowflake.get_bottom(), snowflake.get_top())
        sym_line.scale(1.1)
        sym_line.set_stroke(WHITE, 2)
        sym_line.set_angle(60 * DEGREES)
        sym_line.move_to(snowflake)
        self.play(
            ShowCreation(sym_line),
            FadeIn(flip_icons[0]),
        )
        self.play(
            Rotate(snowflake, PI, axis=rotate_vector(RIGHT, 60 * DEGREES)),
        )
        self.play(
            sym_line.set_angle, 30 * DEGREES,
            sym_line.move_to, snowflake,
            FadeIn(flip_icons[1]),
        )
        self.play(
            Rotate(snowflake, PI, axis=rotate_vector(RIGHT, 30 * DEGREES)),
        )

        # Collection of all snowflake symmetries
        rot_icons.generate_target()
        flip_icons.generate_target()
        d6_group = VGroup(
            get_flake_rot_icon(0),
            rot_icons.target[0],
            rot_icons.target[1],
            get_flake_rot_icon(180),
            get_flake_rot_icon(-120),
            get_flake_rot_icon(-60),
            get_flake_flip_icon(0),
            flip_icons.target[1],
            flip_icons.target[0],
            get_flake_flip_icon(90 * DEGREES),
            get_flake_flip_icon(120 * DEGREES),
            get_flake_flip_icon(150 * DEGREES),
        )
        d6_group.arrange_in_grid(2, 6)
        d6_group.set_width(FRAME_WIDTH - 2)
        d6_group.set_gloss(0)
        d6_group.set_shadow(0)
        for mob in d6_group.get_family():
            if isinstance(mob, SVGMobject):
                mob.set_fill(GREY_C, 1)
                mob.set_stroke(WHITE, 0.25)

        self.play(
            MoveToTarget(rot_icons),
            MoveToTarget(flip_icons),
            ApplyMethod(snowflake.scale, 0, remover=True),
            ApplyMethod(sym_line.scale, 0, remover=True),
        )
        self.play(LaggedStartMap(FadeIn, d6_group))
        self.remove(rot_icons, flip_icons)
        self.wait()

        # Name groups
        group_name = TextMobject("Group", "$^*$")
        group_name.scale(2)
        group_name.to_edge(UP)
        footnote = TextMobject("$^*$er...kind of.  Keep watching")
        footnote.set_height(0.3)
        footnote.to_corner(UR)
        footnote.add(group_name[1])
        footnote.set_color(YELLOW)
        group_name.remove(group_name[1])
        d6_rect = SurroundingRectangle(d6_group)
        d6_rect.set_stroke(BLUE, 2)

        self.play(
            FadeOut(sym_to_action, UP),
            FadeIn(group_name, DOWN),
            ShowCreation(d6_rect),
        )
        self.play(
            FadeIn(
                footnote,
                rate_func=there_and_back_with_pause,
                run_time=3,
                remover=True
            )
        )
        self.wait()

        anims = []
        for icon, deg in zip(d6_group[1:], [60, 120, 180, -120, -60]):
            anims.append(Rotate(icon[0], deg * DEGREES))
        for icon, deg in zip(d6_group[6:], range(0, 180, 30)):
            anims.append(Rotate(icon[0], PI, axis=rotate_vector(RIGHT, deg * DEGREES)))
        random.shuffle(anims)
        self.play(LaggedStart(*anims, lag_ratio=0.3, run_time=5))
        self.play(LaggedStart(*reversed(anims), lag_ratio=0.3, run_time=5))

        # Identity
        id_rect = SurroundingRectangle(d6_group[0])
        id_words = TextMobject("The do-nothing", "\\\\action", alignment="")
        id_words.to_corner(UL)
        id_arrow = Arrow(id_words[1].get_bottom(), id_rect.get_top(), buff=0.2)
        id_arrow.match_color(id_rect)
        self.play(
            ShowCreation(id_rect)
        )
        self.play(
            FadeIn(id_words, lag_ratio=0.1),
            GrowArrow(id_arrow),
        )
        self.wait()

        # Count d6
        rects = VGroup(id_rect, *map(SurroundingRectangle, d6_group[1:]))
        counter = Integer(0)
        counter.set_height(0.8)
        counter.next_to(d6_rect, DOWN, MED_LARGE_BUFF)
        counter.set_color(YELLOW)
        counter.add_updater(lambda m, rects=rects: m.set_value(len(rects)))

        self.add(counter)
        self.play(
            FadeOut(id_words),
            FadeOut(id_arrow),
            ShowIncreasingSubsets(rects, int_func=np.ceil, run_time=2),
            UpdateFromAlphaFunc(counter, lambda m, a: m.set_opacity(a))
        )
        self.wait()

        d6_name = TexMobject("D_6")
        d6_name.scale(2)
        d6_name.move_to(counter)
        d6_name.set_color(BLUE)
        self.play(
            FadeOut(rects, lag_ratio=0.1),
            FadeOut(counter, 0.2 * UP),
            FadeIn(d6_name, 0.2 * DOWN),
        )
        self.wait()

        # Name C2
        face_group = Group(face, face.deepcopy())
        face_group.set_height(4)
        face_group.arrange(RIGHT, buff=LARGE_BUFF)
        face_group.next_to(group_name, DOWN, MED_LARGE_BUFF)
        sym_line = DashedLine(2 * UP, 2 * DOWN)
        sym_line.set_stroke(WHITE, 2)
        sym_line.move_to(face_group[1])
        sym_line.set_height(face_group[1].get_height() * 1.1)
        face_group[1].add(sym_line)

        self.play(
            d6_rect.replace, face_group, {"stretch": True},
            d6_rect.scale, 1.1,
            FadeOut(d6_group),
            FadeOut(d6_name, DOWN),
            *[
                FadeIn(f, -0.5 * f.get_center())
                for f in face_group
            ],
        )
        self.play(face_group[1].stretch, -1, 0)
        self.wait()

        z2_name = TexMobject("C_2")
        z2_name.match_color(d6_name)
        z2_name.match_height(d6_name)
        z2_name.next_to(d6_rect, DOWN, MED_LARGE_BUFF)
        self.play(Write(z2_name))
        self.wait()


class ZooOfGroups(ThreeDScene):
    def construct(self):
        self.camera.light_source.move_to([-10, 5, 20])

        dot_pair = VGroup(Dot(), Dot())
        dot_pair.set_height(0.5)
        dot_pair.arrange(RIGHT, buff=LARGE_BUFF)
        dot_pair.set_color(GREY_B)

        snowflake = get_snowflake(height=2)

        k4_axes = Group(
            Line3D(LEFT, RIGHT, color=RED),
            Line3D(DOWN, UP, color=GREEN),
            Line3D(IN, OUT, color=BLUE),
        )
        k4_axes.set_height(3)

        quat_group = TexMobject("\\{1, -1, i , -i\\\\j, -j, k, -k\\}")

        cube = get_cube(color=BLUE_D, opacity=1)
        cube.rotate(15 * DEGREES, OUT)
        cube.rotate(80 * DEGREES, LEFT)

        sphere = Sphere()
        sphere = Group(
            sphere,
            SurfaceMesh(sphere, resolution=(21, 11))
        )
        sphere[1].set_stroke(WHITE, 0.5, 0.5)
        sphere.rotate(90 * DEGREES, LEFT)
        sphere.rotate(0.2 * DEGREES, RIGHT)
        sphere[0].sort_faces_back_to_front()
        sphere.rotate(90 * DEGREES, UP)
        sphere.set_height(3)

        circle = Circle()
        circle.set_height(3)

        monster_object = TexMobject("196{,}", "883")
        monster_object.arrange(DOWN, buff=0, aligned_edge=LEFT)
        monster_object.set_height(1.5)
        monster_object.add(Eyes(monster_object))
        monster_object[-1].scale(0.8, about_edge=DR)

        qubit = TexMobject(
            "\\alpha|0\\rangle + \\beta|1\\rangle",
            tex_to_color_map={"\\alpha": BLUE, "\\beta": YELLOW}
        )
        qubit.set_height(1)
        qubit.set_height(1)

        groups = Group(
            Group(TexMobject("C_2"), dot_pair),
            Group(TexMobject("D_6"), snowflake),
            Group(TexMobject("K_4"), k4_axes),
            Group(TexMobject("Q_8"), quat_group),
            Group(TexMobject("S_4"), cube),
            Group(TexMobject("SO(3)"), sphere),
            Group(TexMobject("\\mathds{R}^+ / \\mathds{Z}"), circle),
            Group(TexMobject("SU(2)"), qubit),
            Group(get_monster(), monster_object),
        )

        for group in groups:
            group[0].set_height(1)
            group.arrange(RIGHT, buff=LARGE_BUFF)

        groups[-1][0].scale(2)

        groups.arrange_in_grid(3, 3)
        groups.set_width(FRAME_WIDTH - 1)
        groups[:3].shift(0.5 * UP)
        groups[-3:].shift(0.5 * DOWN)

        self.play(LaggedStart(*[
            FadeIn(group[0], -0.5 * group.get_center())
            for group in groups
        ]))
        self.play(LaggedStart(*[
            FadeInFromLarge(group[1])
            for group in groups
        ]))
        self.play(LaggedStart(
            Rotate(dot_pair, PI),
            Blink(monster_object[-1]),
            Rotate(cube, PI / 2, axis=cube[0].get_center() - cube[-1].get_center()),
            Rotate(snowflake, 120 * DEGREES),
            Rotate(k4_axes, PI, axis=RIGHT),
            Rotate(sphere, 170 * DEGREES, axis=UP),
            run_time=3,
            lag_ratio=0.1,
        ))
        self.wait()

        self.play(
            groups[-1].scale, 3,
            groups[-1].center,
            groups[-1].space_out_submobjects, 1.5,
            *[
                FadeOut(mob, mob.get_center() - groups[-1].get_center())
                for mob in groups[:-1]
            ]
        )
        self.play(monster_object[-1].look_at, groups[-1][0])
        self.play(Blink(monster_object[-1]))
        self.play(blink_monster(groups[-1][0]))
        self.wait()


class SymmetriesOfACube(ThreeDScene):
    def construct(self):
        # Setup
        frame = self.camera.frame
        light = self.camera.light_source
        light.move_to(5 * LEFT + 20 * DOWN + 10 * OUT)

        plane = NumberPlane(x_range=(-10, 10), y_range=(-10, 10))
        plane.shift(IN)

        cube = get_cube(color=BLUE_D, opacity=1)
        cube.set_gloss(0.5)
        cube.set_shadow(0.2)

        frame.set_rotation(
            phi=70 * DEGREES,
            theta=-30 * DEGREES,
        )
        frame.add_updater(lambda m, dt, sc=self: m.set_theta(-30 * DEGREES * np.cos(sc.time * 0.05)))
        self.add(frame)

        self.add(plane)
        self.add(cube)

        # Ask about structure
        question = TextMobject("What structure is being preserved?")
        question.set_height(0.7)
        question.to_edge(UP)
        question.fix_in_frame()

        def get_rotation(deg, axis, cube=cube):
            return Rotate(cube, deg * DEGREES, axis=axis, run_time=1.5)

        pairs = [
            (90, UP),
            (90, RIGHT),
            (90, OUT),
            (120, [1, 1, 1]),
            (120, [1, -1, 1]),
            (180, UP),
        ]
        for deg, axis in pairs:
            self.play(get_rotation(deg, axis))
            if axis is pairs[1][1]:
                self.play(FadeIn(question, DOWN))
            self.wait()

        # Count cube symmetries
        count_label = TextMobject("24 ", "symmetries")
        count_label.set_color_by_tex("24", YELLOW)
        count_label.set_height(0.7)
        count_label.fix_in_frame()
        count_label.to_edge(UP)

        self.play(
            FadeIn(count_label, DOWN),
            FadeOut(question, UP),
        )
        self.play(get_rotation(120, [1, -1, -1]))
        self.wait()
        self.play(get_rotation(90, LEFT))
        self.wait()
        self.play(get_rotation(120, [1, -1, -1]))
        self.wait()
        self.play(get_rotation(180, OUT))
        self.wait()

        # Bigger group
        reflection_plane = Square3D(resolution=(10, 10))
        reflection_plane.set_width(4)
        reflection_plane.move_to(cube)
        reflection_plane.set_color(GREY, opacity=0.75)
        reflection_plane.rotate(PI / 2, DOWN)

        cross24 = Cross(count_label[0])
        cross24.fix_in_frame()
        label48 = TexMobject("48")
        label48.set_color(GREEN)
        label48.match_height(count_label[0])
        label48.move_to(count_label[0], DOWN)
        label48.fix_in_frame()

        self.play(FadeInFromLarge(reflection_plane))
        self.play(
            ShowCreation(cross24),
            ApplyMethod(cube.stretch, -1, 0),
        )
        self.wait()
        self.play(
            Rotate(reflection_plane, PI / 2, axis=UP)
        )
        self.play(
            ApplyMethod(cube.stretch, -1, 2),
        )
        self.wait()
        self.play(Rotate(reflection_plane, PI / 4, UP))
        self.play(
            cube.stretch, -1, 2,
            cube.rotate, PI / 2, UP,
        )
        self.wait()
        self.add(count_label[0], cross24)
        self.play(
            count_label[0].shift, 2 * LEFT,
            cross24.shift, 2 * LEFT,
            FadeIn(label48, UP),
        )
        self.play(
            reflection_plane.rotate, PI / 4, UP,
            reflection_plane.rotate, PI / 2, OUT,
        )
        self.play(
            cube.stretch, -1, 1,
        )
        self.wait()
        self.play(FadeOut(reflection_plane))
        self.wait()

        # Permute faces
        cross48 = Cross(label48)
        cross48.fix_in_frame()
        self.play(ShowCreation(cross48))
        label48.add(cross48)

        label24 = count_label[0]
        label24.add(cross24)
        count_label.remove(label24)

        def explostion_transform(self=self, cube=cube):
            cube_copy = cube.copy()
            self.play(
                cube.space_out_submobjects, 1.5,
                cube.shift, 0.5 * OUT,
            )
            exploded_cube_copy = cube.copy()
            self.play(LaggedStart(*[
                Rotate(
                    face,
                    axis=face.get_center() - cube.get_center(),
                    angle=random.choice([0, PI / 2, -PI / 2, PI])
                )
                for face in cube
            ]))
            perm = list(range(6))
            random.shuffle(perm)
            globals()['perm'] = perm  # TODO
            self.play(LaggedStart(*[
                Transform(face, cube[perm[i]])
                for i, face in enumerate(cube)
            ], lag_ratio=0.1))
            cube.become(exploded_cube_copy)
            self.play(Transform(cube, cube_copy))
            self.wait()

        for x in range(3):
            explostion_transform()

        # Largest size
        count = Integer(188743680)
        count.fix_in_frame()
        old_counts = VGroup(label24, label48)
        old_counts.generate_target()
        old_counts.target.to_edge(LEFT)
        count.match_height(old_counts)
        count.next_to(old_counts.target, RIGHT, buff=LARGE_BUFF)
        count.set_color(BLUE_B)
        self.play(
            MoveToTarget(old_counts),
            FadeIn(count),
            count_label.next_to, count, RIGHT,
        )
        for x in range(3):
            explostion_transform()
        self.wait(2)


class WeirdCubeSymmetryUnderbrace(Scene):
    def construct(self):
        brace = Brace(Line(LEFT, RIGHT).set_width(3), DOWN)
        tex = brace.get_tex("(8^6)(6!)")
        VGroup(brace, tex).set_color(WHITE)
        VGroup(brace, tex).set_stroke(BLACK, 8, background=True)
        self.play(
            GrowFromCenter(brace),
            FadeIn(tex, 0.25 * UP)
        )
        self.wait()


class PermutationGroups(Scene):
    def construct(self):
        # Setup
        question = TextMobject("What about no structure?")
        question.scale(1.5)
        question.to_edge(UP)

        perm_words = TextMobject("All ", "permutations")
        perm_words.scale(1.5)
        perm_words.next_to(question, DOWN, buff=0.7)
        perm_words.set_color(BLUE)

        dots = VGroup(*[Dot() for x in range(6)])
        dots.set_fill(GREY_B)
        dots.set_height(0.5)
        dots.arrange(RIGHT, buff=LARGE_BUFF)
        dots.shift(DOWN)
        alt_dots = dots.copy()

        self.add(question)
        self.play(ShowIncreasingSubsets(dots))

        # Permutations
        def get_permutation(self=self, dots=dots, arc=PI / 2):
            perm = list(range(len(dots)))
            random.shuffle(perm)
            arrows = get_permutation_arrows(dots, perm, arc)
            for i, dot in enumerate(dots):
                dot.target = dots[perm[i]]

            arrows.set_opacity(0)
            return Succession(
                UpdateFromAlphaFunc(arrows, lambda m, a: m.set_opacity(a)),
                LaggedStartMap(MoveToTarget, dots, path_arc=arc, lag_ratio=0.15, run_time=2),
                UpdateFromAlphaFunc(arrows, lambda m, a: m.set_opacity(1 - a)),
            )

        permutations = Succession(*[
            get_permutation()
            for x in range(20)
        ])
        animated_perm_mob = cycle_animation(permutations)
        self.add(animated_perm_mob)
        self.wait(5)
        self.play(FadeIn(perm_words, UP))
        self.wait(10)

        # Count perms
        perm_count = TexMobject("6!")
        perm_count.match_height(perm_words[0])
        perm_count.match_color(perm_words[0])
        perm_count.move_to(perm_words[0], RIGHT)
        full_count = Integer(720, edge_to_fix=RIGHT)
        full_count.match_height(perm_count)
        full_count.move_to(perm_count, DR)
        full_count.shift(0.7 * RIGHT)
        full_count.match_color(perm_count)
        equals = TexMobject("=")
        equals.scale(1.5)
        equals.next_to(full_count, LEFT)
        equals.match_color(perm_count)
        perm_count.next_to(equals, LEFT)
        full_count.set_value(0)

        self.remove(animated_perm_mob)
        dots = alt_dots
        self.add(alt_dots)
        self.play(
            FadeIn(full_count, LEFT),
            FadeOut(perm_words[0], RIGHT),
            perm_words[1].shift, 0.7 * RIGHT,
        )

        all_perms = list(it.permutations(range(6)))
        arrows = VGroup()
        self.add(arrows)
        self.play(
            ChangeDecimalToValue(full_count, 720),
            UpdateFromAlphaFunc(
                arrows,
                lambda m, a, dots=dots, all_perms=all_perms: m.set_submobjects(
                    get_permutation_arrows(dots, all_perms[int(np.round(719 * a))])
                )
            ),
            run_time=20,
        )
        self.play(
            FadeIn(perm_count, RIGHT),
            Write(equals),
        )
        self.wait(2)

        perm_label = VGroup(perm_count, equals, full_count, perm_words[1])

        # Revisit snowflake symmetries
        dots.generate_target()
        for dot, point in zip(dots.target, compass_directions(6, UP)):
            dot.move_to(2 * point)

        self.play(
            FadeOut(arrows),
            FadeOut(perm_label, UP),
            FadeOut(question, 0.5 * UP),
            MoveToTarget(dots),
        )

        lines = VGroup()
        for d1, d2 in it.combinations(dots, 2):
            lines.add(Line(
                d1.get_center(),
                d2.get_center(),
                buff=d1.get_width() / 4,
            ))
        lines.set_stroke(WHITE, 2)
        hexy = VGroup(dots, lines)
        hexy.unlock_unit_normal()
        hexy.add_updater(lambda m: m.refresh_unit_normal())

        self.play(LaggedStartMap(ShowCreation, lines))
        self.wait()
        self.play(Rotate(hexy, 60 * DEGREES))
        self.wait()
        self.play(Rotate(hexy, -120 * DEGREES))
        self.wait()
        self.play(Rotate(hexy, PI, axis=UP))
        self.wait()
        self.play(Rotate(hexy, PI, axis=rotate_vector(RIGHT, 60 * DEGREES)))
        self.wait()

        # Back to a row
        dots.generate_target()
        dots.target.arrange(RIGHT, buff=LARGE_BUFF)
        dots.target.move_to(0.5 * DOWN)
        for line in lines:
            line.generate_target()
            line.target.set_angle(0)
            line.target.set_stroke(WHITE, 0, 0)

        perm_label.to_edge(UP, buff=LARGE_BUFF)
        self.play(
            MoveToTarget(dots),
            FadeIn(perm_label),
            LaggedStartMap(MoveToTarget, lines, run_time=1.5)
        )

        # Bump it up to 12
        new_dots = dots.copy()
        new_dots.shift(1.5 * DOWN)

        new_perm_label = VGroup(
            TexMobject("12!"),
            TexMobject("="),
            Integer(math.factorial(12)),
            TextMobject("permutations")[0],
        )
        new_perm_label.arrange(RIGHT)
        new_perm_label.match_height(perm_label)
        new_perm_label.set_color(YELLOW)
        new_perm_label.move_to(perm_label)
        new_perm_label[0].align_to(perm_label[2][0], DOWN)

        perm_label.unlock_triangulation()
        old_full_count_center = full_count.get_center()
        self.play(
            ChangeDecimalToValue(
                perm_label[2], new_perm_label[2].get_value(),
                run_time=3
            ),
            UpdateFromAlphaFunc(
                perm_label[2], lambda m, a: m.move_to(interpolate(
                    old_full_count_center,
                    new_perm_label[2].get_center(),
                    a
                )).set_color(interpolate_color(BLUE, YELLOW, a))
            ),
            ShowIncreasingSubsets(new_dots),
            *[
                ReplacementTransform(perm_label[i], new_perm_label[i])
                for i in [0, 1, 3]
            ]
        )
        self.remove(perm_label)
        perm_label = new_perm_label
        self.add(perm_label)
        dots.add(*new_dots)

        self.wait()

        for x in range(5):
            perm = list(range(12))
            random.shuffle(perm)
            self.play(LaggedStart(*[
                Transform(dots[i], dots[perm[i]], path_arc=PI / 2)
                for i in range(12)
            ]))
            self.wait()

        # Show 101 dots
        new_perm_label = VGroup(
            TexMobject("101!"),
            TexMobject("\\approx"),
            TexMobject("9.43 \\times 10^{159}"),
            TextMobject("permutations")[0]
        )
        new_perm_label.arrange(RIGHT)
        new_perm_label.match_height(perm_label)
        new_perm_label[2].align_to(new_perm_label[0], DOWN)
        new_perm_label[3].shift(SMALL_BUFF * DOWN)
        new_perm_label.move_to(perm_label, RIGHT)

        new_dots = VGroup(*[dots[0].copy() for x in range(101)])
        new_dots.arrange_in_grid(7, 13)
        new_dots.set_height(5)
        new_dots.to_edge(DOWN)

        self.play(
            FadeOut(perm_label),
            FadeIn(new_perm_label),
            ReplacementTransform(dots, new_dots[-len(dots):]),
            ShowIncreasingSubsets(new_dots[:-len(dots)], run_time=2)
        )
        self.add(new_dots)
        perm_label = new_perm_label
        dots = new_dots

        labels = VGroup()
        for i, dot in enumerate(new_dots):
            label = Integer(i + 1, fill_color=BLACK)
            label.replace(dot, dim_to_match=1)
            label.scale(0.3)
            labels.add(label)
        labels.set_stroke(width=0)

        self.play(FadeIn(labels))
        self.remove(labels)
        for dot, label in zip(dots, labels):
            dot.add(label)

        for x in range(6):
            self.play(permutation_animation(dots, lag_factor=1))
            self.wait(0.5)

        # Name S_n
        perm_label[3].generate_target()
        new_perm_label = VGroup(
            TexMobject("n!").match_height(perm_label[0]),
            perm_label[3].target,
        )
        new_perm_label.arrange(RIGHT, buff=MED_LARGE_BUFF)
        new_perm_label[0].align_to(new_perm_label[1][-1], DOWN)
        new_perm_label.next_to(perm_label[0], RIGHT, MED_LARGE_BUFF)
        new_perm_label[0].save_state()
        new_perm_label[0].replace(perm_label[0], stretch=True)
        new_perm_label[0].set_opacity(0)

        Sn_name = TexMobject("S_n")
        Sn_name.match_height(new_perm_label)
        Sn_name.next_to(new_perm_label, RIGHT, buff=LARGE_BUFF)
        Sn_name.set_color(YELLOW)

        self.play(
            perm_label[0].replace, new_perm_label[0], {"stretch": True},
            perm_label[0].set_opacity, 0,
            FadeOut(perm_label[1:3], RIGHT),
            MoveToTarget(perm_label[3]),
            Restore(new_perm_label[0]),
        )
        self.play(FadeIn(Sn_name, LEFT))

        self.remove(perm_label)
        perm_label = new_perm_label
        self.add(perm_label)

        self.play(permutation_animation(dots))

        # Down to a square
        new_dots = dots[:4]
        faders = dots[4:]
        new_dots.generate_target()
        for dot in new_dots.target:
            dot.set_height(0.8)
        new_dots.target.arrange_in_grid(2, 2, buff=LARGE_BUFF)
        new_dots.target.center()

        self.play(
            MoveToTarget(new_dots),
            FadeOut(faders),
        )
        dots = new_dots
        for x in range(2):
            self.play(permutation_animation(dots, [2, 0, 3, 1], lag_factor=0))
            self.wait()


class IsItUseful(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Is any of\\\\this useful?",
            student_index=2,
            target_mode="sassy",
            added_anims=[self.teacher.change, "guilty"]
        )
        self.change_student_modes("angry", "confused")
        self.wait(3)
        self.teacher_says("Extremely!")
        self.change_student_modes("pondering", "thinking", "pondering", look_at_arg=self.screen)
        self.wait(4)


class SolutionsToPolynomials(Scene):
    def construct(self):
        # Show quintic shuffling
        colors = list(Color(BLUE).range_to(YELLOW, 5))
        quintic = TexMobject(
            "x^5 - x - 1",
            "=",
            "(x - r_0)",
            "(x - r_1)",
            "(x - r_2)",
            "(x - r_3)",
            "(x - r_4)",
            tex_to_color_map={
                f"r_{i}": colors[i]
                for i in range(5)
            }
        )
        root_syms = VGroup(*[quintic.get_part_by_tex(f"r_{i}") for i in range(5)])
        quintic.set_width(FRAME_WIDTH - 1)
        quintic.to_edge(UP)

        plane = ComplexPlane(x_range=(-2, 2), y_range=(-2, 2))
        plane.set_height(6)
        plane.to_edge(DOWN, buff=MED_SMALL_BUFF)
        plane.add_coordinate_labels()
        for label in plane.coordinate_labels:
            label.scale(0.7, about_edge=UR)

        def get_root_dots(roots, plane=plane, colors=colors):
            return VGroup(*[
                Dot(
                    plane.n2p(root),
                    radius=0.1,
                    color=color,
                ).set_stroke(BLACK, 2, background=True)
                for root, color in zip(roots, colors)
            ])

        root_dots = get_root_dots([
            1.1673,
            0.181232 + 1.08395j,
            0.181232 - 1.08395j,
            -0.764884 + 0.352472j,
            -0.764884 - 0.352472j,
        ])

        self.add(quintic)
        self.add(plane)
        self.play(LaggedStart(*[
            ReplacementTransform(rs.copy(), rd)
            for rs, rd in zip(root_syms, root_dots)
        ], run_time=3, lag_ratio=0.3))
        self.wait()

        root_syms.save_state()
        root_dots.save_state()

        for x in range(5):
            perm = list(range(5))
            random.shuffle(perm)
            self.play(*[
                permutation_animation(mob, perm, arc=30 * DEGREES, lag_factor=0.5)
                for mob in [root_syms, root_dots]
            ])
            self.wait(0.5)
        self.play(
            Restore(root_syms, path_arc=60 * DEGREES),
            Restore(root_dots, path_arc=60 * DEGREES),
        )

        # Down to quadratic
        quadratic_lhs = TexMobject("x^2 - x - 1")
        quadratic_lhs.match_height(quintic[0])
        quadratic_lhs.move_to(quintic[0], RIGHT)

        self.play(
            FadeOut(quintic[0], UP),
            FadeIn(quadratic_lhs, DOWN),
            FadeOut(quintic[8:], UP),
            MaintainPositionRelativeTo(root_dots, plane),
            UpdateFromAlphaFunc(root_dots, lambda m, a: m.set_opacity(1 - a)),
            plane.to_edge, LEFT,
        )
        self.remove(root_dots)
        root_dots.set_opacity(1)
        root_dots.save_state()

        quad_root_dots = get_root_dots([
            (1 + u * np.sqrt(5)) / 2 for u in [-1, 1]
        ])

        self.play(LaggedStart(*[
            ReplacementTransform(root_sym.copy(), root_dot)
            for root_dot, root_sym in zip(quad_root_dots, root_syms)
        ]))
        self.wait()

        # Quadratic formula
        quadratic_formula = TexMobject(
            "{-b \\pm \\sqrt{\\,b^2 - 4ac} \\over 2a}",
        )
        quadratic_formula.set_height(1.5)
        quadratic_formula.to_edge(RIGHT, buff=LARGE_BUFF)

        quad_form_name = TextMobject("Quadratic formula")
        quad_form_name.set_height(0.5)
        quad_form_name.next_to(quadratic_formula, DOWN, LARGE_BUFF)
        quad_form_name.set_color(GREY_B)

        self.play(
            Write(quadratic_formula),
            FadeIn(quad_form_name, DOWN)
        )
        self.wait()

        # Cubic
        cubic_lhs = TexMobject("x^3 - x - 1")
        cubic_lhs.replace(quadratic_lhs)

        cubic_root_dots = get_root_dots([
            1.3247,
            -0.66236 + 0.56228j,
            -0.66236 - 0.56228j,
        ])

        cubic_formula = TexMobject(
            r"\sqrt[3]{-\frac{q}{2}+\sqrt{\frac{q^{2}}{4}+\frac{p^{3}}{27}}}+\sqrt[3]{-\frac{q}{2}-\sqrt{\frac{q^{2}}{4}+\frac{p^{3}}{27}}}",
        )
        cubic_formula.replace(quadratic_formula, dim_to_match=1)
        cubic_formula.to_edge(RIGHT, buff=MED_SMALL_BUFF)
        cubic_formula.scale(0.8, about_edge=RIGHT)

        cubic_form_name = TextMobject("Cubic formula (reduced)")
        cubic_form_name.replace(quad_form_name, dim_to_match=1)
        cubic_form_name.match_style(quad_form_name)

        self.play(
            ReplacementTransform(quad_root_dots, cubic_root_dots),
            FadeIn(quintic[8:11], DOWN),
            FadeIn(cubic_lhs, DOWN),
            FadeOut(quadratic_lhs, UP),
        )
        self.play(
            LaggedStart(
                FadeOut(quadratic_formula, 2 * RIGHT),
                FadeOut(quad_form_name, 2 * RIGHT),
            ),
            LaggedStart(
                FadeIn(cubic_formula, 2 * LEFT),
                FadeIn(cubic_form_name, 2 * LEFT),
            ),
        )
        self.wait()

        # Quartic (largely copied from above)
        quartic_lhs = TexMobject("x^4 - x - 1")
        quartic_lhs.replace(quadratic_lhs)

        quartic_root_dots = get_root_dots([
            1.2207,
            -0.72449,
            -0.24813 + 1.0340j,
            -0.24813 - 1.0340j,
        ])

        quartic_formula = TexMobject(r"""
            r_{i}&=-\frac{b}{4 a}-S \pm \frac{1}{2} \sqrt{-4 S^{2}-2 p \pm \frac{q}{S}}\\\\
            &\text{Where}\\\\
            p&=\frac{8 a c-3 b^{2}}{8 a^{2}} \qquad \qquad
            q=\frac{b^{3}-4 a b c+8 a^{2} d}{8 a^{3}}\\\\
            S&=\frac{1}{2} \sqrt{-\frac{2}{3} p+\frac{1}{3 a}\left(Q+\frac{\Delta_{0}}{Q}\right)}\\\\
            Q&=\sqrt[3]{\frac{\Delta_{1}+\sqrt{\Delta_{1}^{2}-4 \Delta_{0}^{3}}}{2}}\\\\
            \Delta_{0}&=c^{2}-3 b d+12 a e\\\\
            \Delta_{1}&=2 c^{3}-9 b c d+27 b^{2} e+27 a d^{2}-72 a c e\\\\
        """)
        quartic_formula.set_height(6)
        quartic_formula.next_to(plane, RIGHT, LARGE_BUFF)

        self.play(
            FadeOut(cubic_formula, 2 * RIGHT),
            FadeOut(cubic_form_name, 2 * RIGHT),
            ReplacementTransform(cubic_root_dots, quartic_root_dots),
            FadeIn(quintic[11:14], DOWN),
            FadeIn(quartic_lhs, DOWN),
            FadeOut(cubic_lhs, UP),
        )
        self.play(
            Write(quartic_formula, run_time=3),
        )
        self.wait(2)

        # Back to quintic
        self.play(
            ReplacementTransform(quartic_root_dots, root_dots),
            FadeIn(quintic[0], DOWN),
            FadeOut(quartic_lhs, UP),
            FadeIn(quintic[14:], DOWN),
            FadeOut(quartic_formula, 0.1 * DOWN, lag_ratio=0.01),
        )

        # Wonder about the quintic
        mathy = PiCreature(color=GREY)
        mathy.flip()
        mathy.next_to(quintic, DOWN, buff=1.5)
        mathy.to_edge(RIGHT)

        self.play(
            VFadeIn(mathy),
            mathy.change, "confused", root_syms,
        )
        self.play(Blink(mathy))
        self.wait()
        self.play(
            mathy.change, "pondering", root_syms[3]
        )
        self.play(Blink(mathy))
        self.wait()

        mathy.add_updater(lambda m, sym=root_syms[3]: m.look_at(sym))

        # Show a few permutations
        s5_name = TexMobject("S_5")
        s5_name.scale(1.5)
        s5_name.next_to(plane, RIGHT, MED_LARGE_BUFF, aligned_edge=UP)
        s5_name.shift(DOWN)

        s5_lines = VGroup()
        for dot in root_dots:
            line = Line(s5_name.get_left(), dot.get_center())
            line.match_color(dot)
            line.set_stroke(width=1)
            line.dot = dot
            line.start = line.get_start()
            s5_lines.add(line)

        s5_lines.set_stroke(opacity=0.5)

        self.play(
            FadeIn(s5_name),
            ShowCreation(s5_lines, lag_ratio=0.5),
        )
        for line in s5_lines:
            line.add_updater(lambda m: m.put_start_and_end_on(m.start, m.dot.get_center()))
        self.add(*s5_lines)

        for x in range(5):
            perm = list(range(5))
            random.shuffle(perm)
            self.play(*[
                permutation_animation(mob, perm, arc=30 * DEGREES, lag_factor=0.5)
                for mob in [root_syms, root_dots]
            ])
            self.wait(0.5)

        self.play(
            VFadeOut(s5_lines),
            Restore(root_syms),
            Restore(root_dots),
            FadeOut(mathy),
        )

        # No formula
        r0_value = TexMobject(
            "r_0", "=", "1.1673\\dots",
        )
        r0_value.set_color_by_tex("r_0", BLUE)
        r0_value.scale(1.5)
        r0_value.next_to(plane, RIGHT, MED_LARGE_BUFF)
        r0_value.shift(DOWN)

        self.play(
            LaggedStart(*[
                AnimationGroup(
                    ShowCreationThenFadeAround(dot),
                    ShowCreationThenFadeAround(sym),
                )
                for sym, dot in zip(root_syms, root_dots)
            ], lag_ratio=0.3, run_time=3),
        )
        self.play(TransformFromCopy(root_syms[0], r0_value[0]))
        self.play(Write(r0_value[1:]))
        self.add(r0_value)
        self.wait()

        # Arithmetic symbols
        symbols = VGroup(*[
            TexMobject(s)
            for s in ["+", "-", "\\times", "/", "\\sqrt[n]{\\qquad}"]
        ])
        symbols[:4].arrange_in_grid(2, 2)
        symbols[4].next_to(symbols[:4], RIGHT, MED_LARGE_BUFF)
        symbols.move_to(s5_name)
        symbols.to_edge(RIGHT)
        symbols_rect = SurroundingRectangle(symbols, buff=MED_SMALL_BUFF)
        symbols_rect.set_stroke(BLUE, 2)

        arrow = Arrow(symbols_rect.get_corner(DL), r0_value[2][3].get_top())
        cross = Cross(arrow)
        cross.stretch(0.5, 1)

        self.play(
            FadeIn(symbols, lag_ratio=0.2, run_time=1.5),
            ShowCreation(symbols_rect),
        )
        self.wait()
        self.play(GrowArrow(arrow))
        self.play(ShowCreation(cross))
        self.wait()


class MentionGroupsInPhysics(TeacherStudentsScene):
    def construct(self):
        # Intro
        self.teacher_says("Groups are ubiquitous\\\\in physics.")
        self.change_student_modes("thinking", "happy", "hesitant")
        self.wait(4)

        noether = ImageMobject("EmmyNoether")
        noether.set_height(3)
        noether.to_corner(UL)

        nt_label = TextMobject("Noether's theorem")
        nt_label.set_height(0.5)
        nt_label.move_to(self.hold_up_spot, DOWN)

        self.play(
            FadeIn(nt_label, DOWN),
            FadeIn(noether, DOWN),
            FadeOut(VGroup(self.teacher.bubble, self.teacher.bubble.content)),
            self.teacher.change, "raise_right_hand",
        )
        self.change_student_modes("pondering", "pondering", "thinking", look_at_arg=nt_label)

        # Theorem
        nt_label.generate_target()
        nt_label.target.center().to_edge(UP)
        rule = VGroup(
            TextMobject("Conservation law", color=BLUE),
            TexMobject("\\Leftrightarrow"),
            TextMobject("Symmetry", color=YELLOW),
        )
        rule.set_height(0.5)
        rule.arrange(RIGHT)
        rule.next_to(nt_label.target, DOWN, MED_LARGE_BUFF)

        self.look_at(
            nt_label.target,
            added_anims=[MoveToTarget(nt_label)]
        )
        self.play(
            self.teacher.change, "happy", rule,
            *[
                FadeIn(part, rule.get_center() - part.get_center())
                for part in rule
            ],
        )
        self.wait(2)

        # Examples
        examples = VGroup(
            TextMobject("Momentum", " $\\Leftrightarrow$ ", "Translation in space"),
            TextMobject("Energy", " $\\Leftrightarrow$ ", "Translation in time"),
        )
        examples.arrange(DOWN, buff=MED_LARGE_BUFF)
        examples.next_to(rule, DOWN, buff=MED_LARGE_BUFF)
        for example in examples:
            example[0].set_color(BLUE)
            example[2].set_color(YELLOW)
            example.shift((rule[1].get_x() - example[1].get_x()) * RIGHT)

        self.play(
            self.teacher.change, "raise_right_hand",
            FadeIn(examples[0], UP),
            self.get_student_changes("confused", "erm", "pondering")
        )
        self.look_at(rule)
        self.wait()
        self.play(FadeIn(examples[1], UP))
        self.wait(4)
        self.change_student_modes("thinking", "maybe", "thinking")
        self.wait(4)


class AmbientDodecSymmetries(ThreeDScene):
    def construct(self):
        pass


class NotGroupsGroupAction(Scene):
    def construct(self):
        words = VGroup(
            TextMobject("Group"),
            TextMobject("Group", " action"),
        )
        words.scale(2)
        words.arrange(DOWN, buff=MED_LARGE_BUFF, aligned_edge=LEFT)
        words.to_corner(UL)
        group, group_action = words

        cross = Cross(group)

        self.add(group)
        self.wait()
        self.play(ShowCreation(cross))
        self.play(
            TransformFromCopy(group[0], group_action[0]),
            Animation(cross.copy(), remover=True)
        )
        self.play(Write(group_action[1]))
        self.wait()


class ElementsAsAbstractions(TeacherStudentsScene):
    def construct(self):
        # Three
        self.teacher_says("Three")
        self.wait()

        s_copies = self.students.copy()
        s_copies.scale(0.3)
        bubble = self.students[0].get_bubble(
            s_copies,
            width=5,
            height=4,
        )
        self.play(
            self.students[0].change, "pondering",
            Write(bubble),
            FadeIn(bubble.content, lag_ratio=0.3),
        )
        self.wait(2)

        numeral = Integer(3)
        numeral.replace(bubble.content, dim_to_match=1)
        bubble.content.generate_target()
        for pi in bubble.content.target:
            pi.change("horrified")
            pi.shift(UP)
            pi.set_opacity(0)

        self.play(MoveToTarget(bubble.content))
        self.remove(bubble.content)
        self.play(
            Write(numeral),
            self.students[0].change, "happy", numeral,
        )
        self.look_at(numeral)
        self.wait(2)

        # Element of D6
        self.camera.light_source.set_x(0)
        snowflake = get_snowflake()
        rot_icon = get_rot_icon(60, snowflake)
        inclusion = VGroup(
            rot_icon,
            TexMobject("\\in").scale(2),
            TexMobject("D_6").scale(2),
        )
        inclusion.arrange(RIGHT)
        inclusion.next_to(self.hold_up_spot, UL, MED_LARGE_BUFF)

        self.play(
            LaggedStart(
                FadeOut(self.teacher.bubble),
                FadeOut(self.teacher.bubble.content),
                FadeOut(bubble),
                FadeOut(numeral),
                FadeIn(inclusion, DOWN),
            ),
            self.teacher.change, "raise_right_hand",
        )
        self.look_at(inclusion)
        self.wait()
        self.play(Rotate(rot_icon[0], 60 * DEGREES))
        self.wait()

        rot_icon.generate_target()
        rot_icon.target.to_corner(UL)
        r_sym = TexMobject("r").scale(2)
        r_sym.move_to(rot_icon, RIGHT)

        self.look_at(
            rot_icon.target,
            added_anims=[MoveToTarget(rot_icon)],
        )
        self.look_at(
            r_sym,
            added_anims=[Write(r_sym)]
        )
        self.change_all_student_modes(
            "confused",
            look_at_arg=r_sym,
        )
        self.wait(2)
        inclusion.remove(rot_icon)
        inclusion.add(r_sym)

        # Back to 3
        numeral.move_to(self.hold_up_spot, DOWN)

        self.play(
            inclusion.to_edge, LEFT,
            inclusion.set_color, GREY_B,
            Write(numeral),
            self.get_student_changes(*3 * ["pondering"], look_at_arg=numeral),
            self.teacher.change, "tease", numeral,
        )
        self.wait(2)

        # Operations
        add = TexMobject("3", "+", "5", "=", "8")
        mult = TexMobject("3", "\\cdot", "5", "=", "15")
        ops = VGroup(add, mult)
        ops.match_height(numeral)
        ops.arrange(DOWN, buff=LARGE_BUFF, aligned_edge=LEFT)
        ops.to_corner(UR, buff=LARGE_BUFF)

        self.remove(numeral)
        self.play(
            LaggedStart(*[
                TransformFromCopy(numeral[0], form[0])
                for form in ops
            ]),
            *[
                ApplyMethod(pi.look_at, ops)
                for pi in self.pi_creatures
            ]
        )
        self.play(
            LaggedStart(*[
                Write(form[1:])
                for form in ops
            ])
        )
        self.wait(3)

        # Literal forms
        quincunx = VGroup(*[Dot() for x in range(5)])
        quincunx[:4].arrange_in_grid()
        quincunx.space_out_submobjects(0.7)
        triplet = VGroup(quincunx[0], quincunx[3], quincunx[4]).copy()
        triplet.set_color(BLUE)
        octet = VGroup(*[Dot() for x in range(9)])
        octet.arrange_in_grid(3, 3)
        octet.remove(octet[4])
        octet.space_out_submobjects(0.5)

        sum_dots = VGroup(triplet, quincunx, octet)
        for sd, sym in zip(sum_dots, ops[0][0::2]):
            sd.move_to(sym)

        octet.shift(SMALL_BUFF * RIGHT)

        quincunx_trip = VGroup(*[quincunx.copy() for x in range(3)])
        quincunx_trip.arrange(RIGHT, buff=MED_LARGE_BUFF)
        for quin in quincunx_trip:
            rect = SurroundingRectangle(quin)
            rect.set_stroke(BLUE, 3)
            quin.add(rect)
        quincunx_trip.move_to(ops[1][2], RIGHT)

        fifteen = VGroup(*[Dot() for x in range(15)])
        fifteen.arrange_in_grid(3, 5)
        fifteen.space_out_submobjects(0.5)
        fifteen.move_to(ops[1][4], LEFT)

        mult_dots = VGroup(quincunx_trip, fifteen)

        self.play(
            FadeOut(ops[0][0::2], UP),
            FadeIn(sum_dots, DOWN),
        )
        self.play(
            FadeOut(VGroup(*ops[1][:3], ops[1][4]), UP),
            FadeIn(mult_dots, DOWN),
            self.get_student_changes(*3 * ["erm"], look_at_arg=mult_dots),
        )
        self.wait(4)
        self.play(
            LaggedStart(*[
                ApplyMethod(mob.scale, 0, remover=True)
                for mob in [*sum_dots, *mult_dots]
            ]),
            LaggedStart(*[
                FadeIn(mob)
                for mob in [*ops[0][0::2], *ops[1][:3], ops[1][4]]
            ]),
            self.get_student_changes(*3 * ["happy"]),
        )
        self.wait(2)

        # Show group sum
        flip_icon = get_flip_icon(0, snowflake)
        rhs_icon = get_flip_icon(30 * DEGREES, snowflake)
        rot_icon.generate_target()

        group_prod = VGroup(
            rot_icon.target,
            TexMobject("\\times").scale(2),
            flip_icon,
            TexMobject("=").scale(2),
            rhs_icon
        )
        group_prod.set_gloss(0)
        for icon in group_prod[::2]:
            icon[0].set_stroke(width=0)
            icon[0].set_fill(GREY_A, 1)
        group_prod.arrange(RIGHT)
        group_prod.to_edge(UP)

        self.play(
            FadeOut(ops, RIGHT),
            FadeOut(inclusion, LEFT),
            MoveToTarget(rot_icon),
            LaggedStartMap(FadeIn, group_prod[1:], lag_ratio=0.5, run_time=2),
            self.get_student_changes(
                "sassy", "erm", "confused",
                look_at_arg=group_prod,
            ),
            self.teacher.change, "raise_right_hand",
        )
        group_prod.replace_submobject(0, rot_icon)
        self.add(group_prod)
        self.wait(2)

        # Show successive actions
        snowflake = get_snowflake()
        snowflake.move_to(0.5 * UP)
        snowflake.match_x(group_prod[1])
        alt_flake = snowflake.copy()
        alt_flake.match_x(rhs_icon)

        self.play(
            TransformFromCopy(rot_icon[0], snowflake)
        )

        def get_numbers(flake):
            vect = 1.2 * (flake.get_top() - flake.get_center())
            points = VGroup(*[
                VectorizedPoint(rotate_vector(vect, angle))
                for angle in np.arange(0, TAU, TAU / 6)
            ])
            points.move_to(flake)
            numbers = VGroup(*[Integer(i + 1) for i in range(6)])
            numbers.scale(0.5)
            for num, point in zip(numbers, points):
                num.point = point
                num.add_updater(lambda m: m.move_to(m.point))
            flake.add(points)
            return numbers

        sn_nums = get_numbers(snowflake)
        as_nums = get_numbers(alt_flake)

        self.play(
            FadeIn(sn_nums, lag_ratio=0.1),
            self.get_student_changes(*3 * ["pondering"], look_at_arg=snowflake)
        )
        self.add(*sn_nums)
        self.play(
            Rotate(snowflake, PI, RIGHT),
            ShowCreationThenFadeAround(flip_icon),
        )
        self.wait()
        self.play(
            Rotate(snowflake, 60 * DEGREES),
            ShowCreationThenFadeAround(rot_icon),
        )
        self.wait()

        self.look_at(
            alt_flake,
            added_anims=[TransformFromCopy(rhs_icon[0], alt_flake)]
        )
        self.play(FadeIn(as_nums, lag_ratio=0.1))
        self.add(*as_nums)

        line = rhs_icon.submobjects[-1].copy()
        line.scale(2)
        line.set_stroke(YELLOW, 3)
        line.move_to(alt_flake)
        self.play(ShowCreation(line))
        self.play(
            Rotate(alt_flake, PI, axis=line.get_vector())
        )
        self.play(
            FadeOut(line),
            self.get_student_changes(*3 * ["thinking"])
        )
        self.wait(3)


class MultiplicationTable(Scene):
    def construct(self):
        # Grid
        grid = VGroup(*[Square() for x in range(64)])
        grid.arrange_in_grid(8, 8, buff=0)
        grid.set_stroke(WHITE, 2)
        grid.set_height(6.5)
        grid.to_edge(DOWN, buff=0.5)
        self.add(grid)

        # Action icons
        square = Square()
        square.rotate(45 * DEGREES)
        square.set_height(1)
        square.set_fill(BLUE_D, 1)
        icons = VGroup(
            *[
                get_rot_icon(deg, square)
                for deg in [0, 90, 180, -90]
            ] + [
                get_flip_icon(angle, square, opacity=1)
                for angle in np.arange(0, PI, PI / 4)
            ]
        )
        icons[0].remove(icons[0][-1])
        icons.match_height(grid[0])
        icons.scale(0.8)
        for icon in icons:
            icon[0].rotate(-45 * DEGREES)

        left_icons = icons.copy()
        top_icons = icons.copy()

        for icon_group, grid_group, vect in [(left_icons, grid[0::8], LEFT), (top_icons, grid[:8], UP)]:
            for gs, icon in zip(grid_group, icon_group):
                icon.shift(gs.get_edge_center(vect) - icon[0].get_center())
                icon.shift(0.6 * gs.get_width() * vect)

        for icon in top_icons:
            icon[0].set_fill(GREY_BROWN)

        self.add(left_icons, top_icons)

        # Figure out full table
        def pmult(perm1, perm2):
            return [perm1[i] for i in perm2]

        r = [1, 2, 3, 0]
        s = [3, 2, 1, 0]
        r2 = pmult(r, r)
        r3 = pmult(r2, r)
        perms = [
            list(range(4)), r, r2, r3,
            s,
            pmult(r, s),
            pmult(r2, s),
            pmult(r3, s),
        ]

        table = np.zeros((8, 8), dtype=int)
        table_icons = VGroup()
        for n, square in enumerate(grid):
            i = n // 8
            j = n % 8
            perm = pmult(perms[i], perms[j])
            index = perms.index(perm)
            table[i, j] = index
            icon = icons[index].copy()
            icon[0].set_color(BLUE_E)
            icon.set_opacity(1)
            icon.shift(square.get_center() - icon[0].get_center())

            pre_icon = VGroup(icon.copy(), icon.copy())
            pre_icon.save_state()
            pre_icon.set_opacity(0)
            pre_icon[0].move_to(left_icons[i])
            pre_icon[1].move_to(top_icons[j])
            icon.pre_icon = pre_icon

            table_icons.add(icon)

        # Show all product
        sorted_icons = list(table_icons)

        frame = self.camera.frame
        frame.save_state()
        frame.scale(0.6)
        frame.move_to(top_icons.get_top() + MED_SMALL_BUFF * UL, UP)

        turn_animation_into_updater(Restore(frame, run_time=20, rate_func=bezier([0, 0, 1, 1])))
        self.add(frame)

        for sorted_index, icon in enumerate(sorted_icons):
            n = table_icons.submobjects.index(icon)
            i = n // 8
            j = n % 8
            rects = VGroup(
                SurroundingRectangle(left_icons[i]),
                SurroundingRectangle(top_icons[j]),
                grid[n].copy().set_fill(GREEN_E, 0.5)
            )
            rects.set_stroke(YELLOW, 2)
            self.add(rects, *self.mobjects)
            self.add(icon)
            if sorted_index < 8:
                pass  # Don't wait
            elif sorted_index < 24:
                self.wait(1)
            else:
                self.wait(0.15)
            self.remove(rects)
        self.add(table_icons)
        self.wait(2)

        # Symbolically
        symbols = VGroup(
            TexMobject("1"),
            TexMobject("r"),
            TexMobject("r^2"),
            TexMobject("r^3"),
            TexMobject("s"),
            TexMobject("rs"),
            TexMobject("r^2 s"),
            TexMobject("r^3 s"),
        )
        symbols.set_height(0.4 * grid[0].get_height())

        left_symbols = symbols.copy()
        top_symbols = symbols.copy()
        for symbol_group, icon_group in [(left_symbols, left_icons), (top_symbols, top_icons)]:
            for symbol, icon in zip(symbol_group, icon_group):
                symbol.move_to(icon[0], DOWN)

        table_symbols = VGroup()
        for n, icon in enumerate(table_icons):
            i = n // 8
            j = n % 8
            symbol = symbols[table[i, j]].copy()
            symbol.move_to(icon[0], DOWN)
            table_symbols.add(symbol)

        self.play(
            LaggedStart(*[
                ApplyMethod(mob.scale, 0, remover=True)
                for mob in [*left_icons, *top_icons, *table_icons]
            ]),
            LaggedStart(*[
                GrowFromCenter(mob)
                for mob in [*left_symbols, *top_symbols, *table_symbols]
            ]),
        )
        self.wait()

        # Show some products
        last_rects = VGroup()
        for x in range(10):
            n = random.randint(0, 63)
            i = n // 8
            j = n % 8
            rects = VGroup(
                SurroundingRectangle(left_symbols[i]),
                SurroundingRectangle(top_symbols[j]),
                grid[n].copy().set_stroke(YELLOW, 4).set_fill(YELLOW, 0.5)
            )
            self.add(rects, *self.mobjects)
            self.play(
                FadeOut(last_rects),
                FadeIn(rects),
            )
            self.wait(2)
            last_rects = rects
        self.play(FadeOut(last_rects))
        self.wait()


class UsualMultiplicationTable(Scene):
    def construct(self):
        # Setup grid
        grid = VGroup(*[
            VGroup(*[Square() for x in range(4)]).arrange(RIGHT, buff=0)
            for y in range(4)
        ]).arrange(DOWN, buff=0)
        grid.set_height(6)
        grid.to_edge(DOWN, buff=0.5)
        grid.set_fill(GREY_E, 1)
        dots = VGroup(
            *[TexMobject("\\dots").scale(2).next_to(row, RIGHT) for row in grid[:-1]],
            *[TexMobject("\\vdots").scale(2).next_to(square, DOWN) for square in grid[-1][:-1]],
            TexMobject("\\ddots").scale(2).next_to(grid[-1][-1], DR),
        )

        self.add(grid)

        # Setup abstract dots
        table_dots = VGroup()
        for i, row in zip(it.count(1), grid):
            for j, square in zip(it.count(1), row):
                dots = VGroup(*[Dot() for x in range(i * j)])
                dots.arrange_in_grid(i, j, buff=SMALL_BUFF)
                dots.scale(0.9)
                dots.move_to(square)
                table_dots.add(dots)

        left_dots = table_dots[0::4].copy()
        left_dots.shift(grid[0][0].get_width() * LEFT)
        left_dots.set_color(BLUE)

        top_dots = table_dots[0:4].copy()
        top_dots.shift(grid[0][0].get_height() * UP)
        top_dots.set_color(RED)

        dot_groups = VGroup(left_dots, top_dots, table_dots)

        # Numerals
        sym_groups = VGroup()
        for dot_group in dot_groups:
            sym_group = VGroup()
            for dots in dot_group:
                numeral = Integer(len(dots))
                numeral.set_height(0.6)
                numeral.move_to(dots)
                numeral.match_color(dots)
                sym_group.add(numeral)
            sym_groups.add(sym_group)

        left_syms, top_syms, table_syms = sym_groups

        # Add symbols
        ls_copies = left_syms.copy().unlock_triangulation()
        ts_copies = top_syms.copy().unlock_triangulation()

        self.add(left_syms, top_syms)
        self.play(LaggedStart(*[
            AnimationGroup(
                Transform(ls_copies[i].copy(), table_syms[4 * i + j].copy(), remover=True),
                Transform(ts_copies[j].copy(), table_syms[4 * i + j].copy(), remover=True),
            )
            for i, j in it.product(range(4), range(4))
        ], lag_ratio=0.3))
        self.add(table_syms)
        self.wait()

        # To dots
        self.play(
            FadeOut(sym_groups),
            FadeIn(dot_groups),
        )
        self.wait()

        # Show a few products
        last_rects = VGroup()
        ns = random.sample(range(16), 5)
        for n in ns:
            i = n // 4
            j = n % 4
            rects = VGroup(
                SurroundingRectangle(left_dots[i]),
                SurroundingRectangle(top_dots[j]),
                grid[i][j].copy().set_fill(YELLOW, 0.5),
            )
            rects.set_stroke(YELLOW, 4)
            self.play(FadeIn(rects), FadeOut(last_rects), run_time=0.5)
            self.wait()
            last_rects = rects
        self.play(FadeOut(last_rects))

        # Back to syms
        self.play(
            dot_groups.fade, 0.8,
            FadeIn(sym_groups),
        )
        self.wait()

        # Benefits
        frame = self.camera.frame
        frame.generate_target()
        frame.target.set_x(grid.get_right()[0])
        frame.target.scale(1.1)

        benefit = VGroup(
            TextMobject("Abstraction").scale(1.5),
            Vector(DOWN),
            TextMobject("Less cumbersome").scale(1.5),
        )
        benefit.arrange(DOWN)
        benefit.next_to(grid, RIGHT, buff=LARGE_BUFF)

        turn_animation_into_updater(MoveToTarget(frame, run_time=3))
        self.add(frame)

        self.play(Write(benefit[0]))
        self.play(GrowArrow(benefit[1]))
        self.play(FadeIn(benefit[2], UP))
        self.wait()


class MentionTheMonster(Scene):
    def construct(self):
        monster = get_monster()
        monster.set_height(6)

        self.add(monster)
        self.wait()
        self.play(blink_monster(monster))
        self.wait()

        size_label = get_monster_size_label()
        size_label.match_height(monster)
        size_label.to_edge(RIGHT, buff=LARGE_BUFF)

        self.play(
            ApplyMethod(monster.next_to, size_label, LEFT, LARGE_BUFF, run_time=2),
            ShowIncreasingSubsets(size_label, run_time=6)
        )
        self.play(blink_monster(monster))
        self.wait()


class FrustratedAtGroups(TeacherStudentsScene):
    def construct(self):
        formula = TexMobject(r"|G|=|Z(G)|+\sum i\left[G: C_{G}\left(x_{i}\right)\right]")
        formula.move_to(self.hold_up_spot, DOWN)
        formula.shift(0.5 * UL)

        self.play(
            self.teacher.change, "raise_right_hand",
            FadeIn(formula, DOWN),
        )
        self.change_student_modes("confused", "horrified", "pleading")
        self.look_at(formula.get_left())
        self.wait(2)
        self.look_at(formula.get_right())
        self.wait(2)


class WikiPageOnGroups(ExternallyAnimatedScene):
    pass


class AnalogyWithCounts(Scene):
    def construct(self):
        # Setup
        line = Line(LEFT, RIGHT)
        words = TextMobject("Abstraction of")
        words.match_width(line)
        words.scale(0.9)
        words.next_to(line, UP, SMALL_BUFF)
        line.add(words)
        line.rotate(-90 * DEGREES)
        line.scale(0.5)

        diagrams = VGroup(*[
            VGroup(mob1, line.copy(), mob2)
            for mob1, mob2 in [
                (TextMobject("Groups"), TextMobject("Symmetry actions")),
                (TexMobject("D_6"), get_snowflake(height=1)),
                (TextMobject("Numbers"), TextMobject("Counts")),
                (TexMobject("9").scale(1.5), VGroup(*[Dot() for x in range(9)]).arrange_in_grid(buff=SMALL_BUFF)),
            ]
        ])
        for diagram, vect in zip(diagrams, [LEFT, LEFT, RIGHT, RIGHT]):
            diagram[0].set_color(YELLOW)
            diagram[2].set_fill(BLUE)
            diagram.arrange(DOWN)
            diagram.scale(1.5)
            diagram.shift(3.5 * vect - diagram[1].get_center())

        # Show diagrams
        self.add(diagrams[0][0])
        self.play(
            Write(diagrams[0][1]),
            FadeIn(diagrams[0][2], 2 * UP),
        )
        self.wait()
        self.play(*[
            AnimationGroup(
                ReplacementTransform(
                    m2.copy().replace(m1, stretch=True).set_opacity(0),
                    m2,
                ),
                Transform(
                    m1.copy(),
                    m1.copy().replace(m2, stretch=True).set_opacity(0),
                    remover=True
                )
            )
            for m1, m2 in zip(diagrams[0], diagrams[2])
        ])
        self.wait()

        self.play(
            FadeOut(diagrams[0]),
            FadeIn(diagrams[1]),
        )
        flake = diagrams[1][2]
        self.add(flake)
        self.play(
            FadeOut(diagrams[2]),
            FadeIn(diagrams[3]),
            Rotate(flake, 60 * DEGREES),
        )
        self.play(Rotate(flake, PI, UP))
        self.play(Rotate(flake, -120 * DEGREES))
        self.play(Rotate(flake, PI, RIGHT))
        self.play(Rotate(flake, 120 * DEGREES))
        self.play(Rotate(flake, PI, UP))
        self.play(
            VFadeOut(diagrams[1]),
            Rotate(flake, 180 * DEGREES),
            FadeIn(diagrams[0]),
            FadeOut(diagrams[3]),
            FadeIn(diagrams[2]),
        )
        self.wait(2)


class ButWhy(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "But, why?",
            target_mode="maybe",
            added_anims=[LaggedStart(
                ApplyMethod(self.teacher.change, "guilty"),
                ApplyMethod(self.students[0].change, "confused"),
                ApplyMethod(self.students[1].change, "sassy"),
                lag_ratio=0.5,
            )]
        )
        self.wait(3)


class CubeRotations(ThreeDScene):
    def construct(self):
        # Set frame motion
        frame = self.camera.frame
        frame.set_rotation(phi=80 * DEGREES)
        frame.add_updater(lambda m, sc=self: m.set_rotation(theta=-20 * DEGREES * np.cos(0.1 * sc.time)))
        self.add(frame)

        # Setup cube
        cube = get_glassy_cube(frame)
        cube.set_height(3)
        axes = ThreeDAxes(axis_config={"include_tip": False})
        axes.apply_depth_test()

        self.add(axes)
        self.add(cube)

        # Apply rotations
        quats = self.get_quaternions()
        self.wait()
        for quat in quats:
            angle, axis = angle_axis_from_quaternion(quat)

            line = Line3D(-5 * axis, 5 * axis, prefered_creation_axis=0)
            line.set_color(YELLOW)
            if angle < 1e-6:
                line.scale(0)
            # line.apply_depth_test()
            deg_label = Integer(int(np.round(angle / DEGREES)), unit="^\\circ")
            deg_label.scale(2)
            deg_label.to_edge(UP)
            deg_label.shift(2 * LEFT)
            deg_label.fix_in_frame()

            self.add(line, *self.mobjects)
            self.play(ShowCreation(line), FadeIn(deg_label))
            self.play(Rotate(cube, angle, axis=axis))
            line.scale(-1)
            self.play(Uncreate(line), FadeOut(deg_label))

    def get_quaternions(self, n_rotations=30):
        ijk = [
            quaternion_from_angle_axis(90 * DEGREES, axis)
            for axis in [RIGHT, UP, OUT]
        ]
        result = []
        for x in range(n_rotations):
            n = random.randint(1, 10)
            curr = quaternion_from_angle_axis(0, RIGHT)
            for y in range(n):
                curr = quaternion_mult(curr, random.choice(ijk))
            result.append(curr)

        # Add on those rotations around diagonals for the end
        for oi in [OUT, IN]:
            for vect in [UL, UR, DR, DL]:
                result.append(quaternion_from_angle_axis(120 * DEGREES, vect + oi))
        return result


class QuadrupletShufflings(CubeRotations):
    def construct(self):
        # Background
        bg_rect = FullScreenFadeRectangle()
        bg_rect.set_fill(GREY_E, 1)
        bg_rect.set_stroke(width=0)
        self.add(bg_rect)

        # Setup dots
        dots = VGroup(*[Dot() for x in range(4)])
        dots.set_height(0.5)
        dots.arrange(RIGHT, buff=MED_LARGE_BUFF)
        dots.set_color(GREY_B)

        for n, dot in enumerate(dots):
            label = Integer(n + 1)
            label.set_height(0.25)
            label.set_color(BLACK)
            label.move_to(dot)
            dot.add(label)

        self.add(dots)
        self.wait()

        # Permutations
        for quat in self.get_quaternions():
            perm = self.quaternion_to_perm(quat)

            arrows = get_permutation_arrows(dots, perm)
            self.play(FadeIn(arrows))
            self.play(permutation_animation(dots, perm, lag_factor=0.2, run_time=1))
            self.play(FadeOut(arrows))

    def quaternion_to_perm(self, quat):
        angle, axis = angle_axis_from_quaternion(quat)

        base_vects = [UL, UR, DR, DL]
        rot_vects = [
            rotate_vector(v + OUT, angle, axis)
            for v in base_vects
        ]
        perm = []
        for vect in rot_vects:
            if vect[2] < 0:
                vect *= -1
            vect[2] = 0
            i = np.argmin([get_norm(vect - bv) for bv in base_vects])
            perm.append(i)
        return perm


class EightShufflingsOfOrderThree(Scene):
    def construct(self):
        bg_rect = FullScreenFadeRectangle()
        bg_rect.set_fill(GREY_E, 1)
        bg_rect.set_stroke(width=0)
        self.add(bg_rect)

        # Setup dots
        dots_template = VGroup(*[Dot() for x in range(4)])
        dots_template.set_height(0.5)
        dots_template.arrange(RIGHT, buff=MED_SMALL_BUFF)
        dots_template.set_color(GREY_B)

        for n, dot in enumerate(dots_template):
            label = Integer(n + 1)
            label.set_height(0.25)
            label.set_color(BLACK)
            label.move_to(dot)
            dot.add(label)

        all_dots = VGroup(*[dots_template.copy() for x in range(8)])
        all_dots.arrange_in_grid(4, 2, buff=1.25)
        VGroup(all_dots[0::2], all_dots[1::2]).arrange(RIGHT, buff=2)

        d_gen = iter(all_dots)
        for trip in it.combinations(range(4), 3):
            trip = np.array(trip)
            perm1 = np.array(list(range(4)))
            perm2 = np.array(list(range(4)))
            perm1[trip] = trip[[1, 2, 0]]
            perm2[trip] = trip[[2, 0, 1]]
            for perm in [perm1, perm2]:
                dots = next(d_gen)
                arrows = get_permutation_arrows(dots, perm)
                dots.add(arrows)
                dots.perm = perm
                for i in trip:
                    dots[i].set_stroke(YELLOW, 1)
                    dots[i][1].set_stroke(width=0)

        self.play(ShowIncreasingSubsets(all_dots, run_time=4, rate_func=linear))
        self.wait()
        for x in range(3):
            self.play(*[
                permutation_animation(dots, dots.perm, lag_factor=0)
                for dots in all_dots
            ])
        self.wait()


class Isomorphism(Scene):
    def construct(self):
        # Frame
        frame = self.camera.frame
        frame.focal_distance = 20

        # Rotation equation
        def get_rot_icon(angle=0, axis=OUT, frame=frame):
            cube = get_glassy_cube(frame)
            cube.set_height(1)
            arc_arrows = VGroup(*[
                Arrow(
                    u * RIGHT,
                    u * rotate_vector(RIGHT, 160 * DEGREES),
                    buff=0,
                    path_arc=160 * DEGREES,
                    width=0.05,
                )
                for u in [1, -1]
            ])
            arc_arrows.set_color(GREY_B)
            axis_line = DashedLine(IN, OUT)
            axis_line.set_stroke(YELLOW, 2)

            rot_icon = Group(arc_arrows, axis_line, cube)
            rot_icon.set_gloss(0.5)
            rot_icon.apply_depth_test()

            rot_icon.rotate(angle, axis)
            rot_icon.rotate(-15 * DEGREES, OUT)
            rot_icon.rotate(75 * DEGREES, LEFT)

            return rot_icon

        rot_icon_equation = Group(
            get_rot_icon(90 * DEGREES, UP),
            TexMobject("\\times").scale(2),
            get_rot_icon(90 * DEGREES, RIGHT),
            TexMobject("=").scale(2),
            get_rot_icon(0, OUT),
        )
        rot_icons = rot_icon_equation[0::2]
        rot_icon_equation.arrange(RIGHT, buff=LARGE_BUFF)
        rot_icon_equation.shift(1.5 * UP)

        icon_labels = VGroup(*[
            TextMobject(f"$180^\\circ$ about\\\\{axis} axis")
            for axis in "xyz"
        ])
        for icon, label in zip(rot_icon_equation[0::2], icon_labels):
            icon[-1][-1].set_opacity(0.5)
            label.scale(0.8)
            label.move_to(icon)
            label.to_edge(UP)
            icon.add(label)

        # Permutation equation
        dots = VGroup(*[Dot() for x in range(4)])
        dots.set_height(0.4)
        dots.set_color(GREY_B)
        dots.arrange(RIGHT)
        # for n, dot in enumerate(dots):
        #     label = Integer(n + 1)
        #     label.set_color(BLACK)
        #     label.set_height(0.6 * dot.get_height())
        #     label.move_to(dot)
        #     dot.add(label)

        perms = [
            [1, 0, 3, 2],
            [3, 2, 1, 0],
            [2, 3, 0, 1],
        ]
        perm_terms = VGroup()
        for perm in perms:
            perm_term = VGroup(dots.copy(), get_permutation_arrows(dots, perm))
            perm_term.perm = perm
            perm_terms.add(perm_term)
        perm_equation = VGroup(
            perm_terms[0],
            TexMobject("\\times").scale(2),
            perm_terms[1],
            TexMobject("=").scale(2),
            perm_terms[2],
        )
        perm_equation.arrange(RIGHT, buff=LARGE_BUFF)
        perm_equation.move_to(2 * DOWN)

        # Bijection lines
        bij_lines = VGroup()
        for m1, m2 in zip(rot_icons, perm_terms):
            line = Line(m1.get_bottom(), m2.get_top(), buff=0.2)
            line.set_angle(-PI / 2, about_point=line.get_center())
            bij_lines.add(line)

        bij_lines.set_color(GREEN)

        rot_icons[-1].match_x(bij_lines[2])

        # Add terms
        self.add(rot_icons)
        for rot_icon, line, perm_term in zip(rot_icons, bij_lines, perm_terms):
            self.play(
                # FadeIn(rot_icon),
                GrowFromPoint(line, line.get_top()),
                FadeIn(perm_term, 2 * UP),
            )
        self.wait()
        self.play(Write(VGroup(
            *rot_icon_equation[1::2],
            *perm_equation[1::2],
        )))
        self.wait(2)

        # Composition
        rot_anims = [
            AnimationGroup(
                Rotate(rot_icon[2], PI, axis=rot_icon[1].get_vector()),
                ShowCreationThenFadeAround(rot_icon[-1]),
            )
            for rot_icon in rot_icons
        ]
        perm_anims = [
            permutation_animation(perm_term[0], perm_term.perm, lag_factor=0.1)
            for perm_term in perm_terms
        ]

        self.play(rot_anims[1])
        self.play(rot_anims[0])
        self.wait()
        self.play(rot_anims[2])
        self.wait()
        self.play(LaggedStartMap(ShowCreation, bij_lines, lag_ratio=0.5))
        self.wait()
        self.play(perm_anims[1])
        self.play(perm_anims[0])
        self.wait()
        self.play(perm_anims[2])
        self.wait()


class IsomorphismWord(Scene):
    def construct(self):
        word = TextMobject("``Isomorphism''")
        word.scale(2)
        word.to_edge(UP)
        self.play(FadeIn(word, DOWN))
        self.wait()


class AskAboutCubeDiagonals(QuadrupletShufflings):
    def construct(self):
        # Setup
        frame = self.camera.frame
        frame.set_rotation(phi=80 * DEGREES)
        frame.add_updater(lambda m, sc=self: m.set_rotation(theta=-20 * DEGREES * np.cos(0.1 * sc.time)))

        cube = get_glassy_cube(frame)
        cube.set_height(3)
        axes = ThreeDAxes(axis_config={"include_tip": False})

        colors = [RED, GREEN, BLUE, YELLOW]
        diagonals = Group(*[
            Line3D(vect + OUT, -vect - OUT, color=color)
            for color, vect in zip(colors, [UL, UR, DR, DL])
        ])
        diagonals.match_height(cube.edge_rods)

        diag_markers = Group(*[
            Line3D(ORIGIN, UP, color=color)
            for color in colors
        ])
        diag_markers.arrange(RIGHT, buff=MED_LARGE_BUFF)
        diag_markers.to_corner(UL, buff=LARGE_BUFF)
        diag_markers.fix_in_frame()

        # Color corners
        cds = cube.corner_dots
        for diag in diagonals:
            globals()['diag'] = diag
            Group(*[
                cds[np.argmin([get_norm(cd.get_center() - diag.points[i]) for cd in cds])]
                for i in [0, -1]
            ]).match_color(diag)

        cube.add_to_back(diagonals)

        # Rotations
        self.add(axes, cube)
        self.add(diag_markers)
        self.add(frame)
        for quat in self.get_quaternions():
            angle, axis = angle_axis_from_quaternion(quat)
            perm = self.quaternion_to_perm(quat)
            perm_arrows = get_permutation_arrows(diag_markers, perm)
            perm_arrows.fix_in_frame()

            self.play(FadeIn(perm_arrows))
            self.play(
                Rotate(cube, angle, axis=axis),
                permutation_animation(diag_markers, perm, lag_factor=0.1),
                run_time=2,
            )
            self.play(FadeOut(perm_arrows))
            self.wait()

            inv_perm = self.quaternion_to_perm(quaternion_conjugate(quat))
            diag_markers.set_submobjects([diag_markers[i] for i in inv_perm])


class S4WithMultipleChildren(Scene):
    def construct(self):
        # Setup
        bg_rect = FullScreenFadeRectangle()
        bg_rect.set_fill(GREY_E, 1)
        self.add(bg_rect)

        s_rects = VGroup(*[ScreenRectangle() for x in range(3)])
        s_rects.arrange(RIGHT, buff=MED_LARGE_BUFF)
        s_rects.set_width(FRAME_WIDTH - 1)
        s_rects.set_stroke(WHITE, 2)
        s_rects.set_fill(BLACK, 1)
        s_rects.move_to(DOWN)
        self.add(s_rects)

        s4_label = TexMobject("S_4")
        s4_label.scale(2)
        s4_label.to_edge(UP)

        lines = VGroup(*[
            Line(rect.get_top(), s4_label.get_bottom(), buff=0.2)
            for rect in s_rects
        ])

        # Arising
        self.play(LaggedStartMap(ShowCreation, lines, lag_ratio=0.5))
        self.play(FadeIn(s4_label, DOWN))
        self.wait(2)

        # Triplets
        three = Integer(3)
        three.scale(2)
        three.move_to(s4_label)

        pis = VGroup(*[Randolph(color=c) for c in [BLUE_C, BLUE_E, BLUE_D]])
        pis.arrange(RIGHT)
        vects = VGroup(*[Vector(RIGHT) for x in range(3)])
        vects.arrange(RIGHT, buff=SMALL_BUFF)
        vects.rotate(30 * DEGREES)
        vects.set_color(TEAL)
        triangle = RegularPolygon(3)
        triangle.set_stroke(BLUE_B, 4)
        triangle.add(*[Dot(vert, color=BLUE_D) for vert in triangle.get_vertices()])
        triangle.set_stroke(background=True)
        triplets = VGroup(pis, vects, triangle)

        for trip, rect in zip(triplets, s_rects):
            trip.set_width(0.8 * rect.get_width())
            if trip.get_height() > 0.8 * rect.get_height():
                trip.set_height(0.8 * rect.get_height())
            trip.move_to(rect)

        self.play(
            FadeOut(s4_label, UP),
            FadeIn(three, DOWN),
            LaggedStartMap(FadeIn, pis, lag_ratio=0.5, run_time=1),
        )
        for trip in triplets[1:]:
            self.play(FadeIn(trip, lag_ratio=0.5))
        self.play(Blink(pis[0]))
        self.play(Blink(pis[2]))

        # Back to s4
        self.play(
            FadeOut(three, DOWN),
            FadeIn(s4_label, UP),
            FadeOut(triplets, lag_ratio=0.2, run_time=2),
        )
        self.wait()


class AutQ8(Scene):
    def construct(self):
        tex = TexMobject("\\text{Aut}(Q_8)", tex_to_color_map={"Q_8": BLUE})
        tex.scale(2)
        self.play(Write(tex))
        self.wait()


class GroupsBeyondActions(Scene):
    def construct(self):
        groups = TextMobject("Groups")
        sym_acts = TextMobject("Symmetric\\\\Actions")
        others = TextMobject("Other things\\\\which ``multiply''")
        VGroup(groups, sym_acts, others).scale(1.5)
        line = Line(UP, DOWN)

        sym_acts.set_color(BLUE)
        others.set_color(interpolate_color(GREY_BROWN, WHITE, 0.5))

        VGroup(
            groups, line, sym_acts
        ).arrange(DOWN, buff=MED_LARGE_BUFF)

        line.add_updater(lambda m: m.put_start_and_end_on(
            groups.get_bottom() + 0.3 * DOWN,
            sym_acts.get_top() + 0.3 * UP,
        ))

        others.move_to(sym_acts)
        others.to_edge(RIGHT)
        others_line = Line(groups.get_bottom(), others.get_top(), buff=0.3)

        self.add(groups, line, sym_acts)
        self.wait()
        self.play(
            sym_acts.to_edge, LEFT, LARGE_BUFF,
            FadeIn(others, 2 * UL),
            ShowCreation(others_line),
            run_time=2,
        )
        self.wait()


class RAddToRMult(ExternallyAnimatedScene):
    pass


class AskAboutAllTheGroups(TeacherStudentsScene):
    def construct(self):
        # Ask
        question = TextMobject("What are all the groups", "?")
        self.teacher_holds_up(question)
        self.change_student_modes("pondering", "thinking", "erm")
        self.wait(2)

        question.generate_target()
        question.target.to_corner(UL)
        self.teacher_says(
            "Now you can\\\\ask something\\\\more sophisticated.",
            target_mode="hooray",
            added_anims=[
                MoveToTarget(question, run_time=2),
                self.get_student_changes(
                    "erm", "pondering", "pondering",
                    look_at_arg=question.target
                )
            ]
        )
        self.wait(2)
        self.play(
            RemovePiCreatureBubble(
                self.teacher, target_mode="tease",
                look_at_arg=question.get_right(),
            ),
            question.set_x, 0,
        )

        # Add up to isomorphism
        caveat = TextMobject("up to \\emph{isomorphism}")
        caveat.next_to(question, DOWN)
        caveat.set_color(YELLOW)

        self.play(
            Write(caveat, run_time=1),
            question[1].next_to, caveat[0][-1], RIGHT, SMALL_BUFF, DOWN,
            question[1].match_color, caveat,
            self.get_student_changes(*3 * ["thinking"], look_at_arg=question)
        )
        question.add(caveat)
        self.wait(2)
        self.look_at(self.screen)
        self.wait(2)
        self.look_at(question)

        # Alt question
        sym_question = TextMobject("What are all the\\\\", "symmetric", " things", "?")
        self.teacher_holds_up(sym_question)

        cross = Cross(sym_question)
        self.look_at(
            cross,
            added_anims=[
                ShowCreation(cross),
                self.get_student_changes("erm", "sassy", "hesitant")
            ]
        )
        self.wait()

        abs_question = TextMobject("What are all the", " \\emph{ways}\\\\", "things ", "can be ", "symmetric", "?")
        new_words = VGroup(abs_question[1], abs_question[3])
        new_words.match_color(caveat)
        abs_question.move_to(sym_question)
        abs_question.shift_onto_screen()
        self.play(
            *[
                ReplacementTransform(sym_question[i], abs_question[j], path_arc=10 * DEGREES)
                for i, j in [(0, 0), (1, 4), (2, 2), (3, 5)]
            ],
            FadeOut(cross),
            self.get_student_changes("happy", "thinking", "tease"),
        )
        self.play(
            self.teacher.change, "speaking", abs_question,
            Write(new_words),
        )
        self.look_at(abs_question)
        self.wait(2)

        # Formula
        suggestions = VGroup(*[
            TextMobject("Some ", word, "?", tex_to_color_map={word: color})
            for word, color in [
                ("formula", RED),
                ("procedure", MAROON_B),
                ("algorithm", PINK),
            ]
        ])
        for words in suggestions:
            words.move_to(abs_question, UP)
            words.to_edge(LEFT, buff=LARGE_BUFF)

        self.play(
            FadeIn(suggestions[0], DOWN),
            self.get_student_changes(*3 * ["pondering"], look_at_arg=suggestions),
            self.teacher.change, "happy",
        )
        self.wait()
        for words1, words2 in zip(suggestions, suggestions[1:]):
            self.play(
                FadeOut(words1[1], UP),
                FadeIn(words2[1], DOWN),
                ReplacementTransform(words1[2], words2[2])
            )
            self.remove(words1)
            self.add(words2)
            self.wait()
        self.wait(3)
        self.play(
            FadeOut(
                VGroup(question, abs_question, suggestions[-1]),
                0.5 * DOWN,
                lag_ratio=0.02,
                run_time=2,
            )
        )


class ThisQuestionIsHard(Scene):
    def construct(self):
        # Setup line
        line = NumberLine(x_range=(0, 1, 0.1), width=12)
        line.shift(UP)
        arrows = VGroup(
            Arrow(line.n2p(0.5), line.n2p(0), fill_color=GREEN),
            Arrow(line.n2p(0.5), line.n2p(1), fill_color=RED),
        )
        arrows.shift(2.5 * DOWN)
        words = VGroup(TextMobject("Easier"), TextMobject("Harder"))
        for word, arrow in zip(words, arrows):
            word.match_color(arrow)
            word.next_to(arrow, DOWN, SMALL_BUFF)

        self.add(line)
        self.add(arrows)
        self.add(words)

        # Add problems
        problems = VGroup(
            TexMobject("1 + 1"),
            VGroup(
                TexMobject("\\frac{2^{289}+1}{2^{17}+1}=2^{a_{1}}+\\ldots+2^{a_{k}}"),
                TexMobject("a_1 < \\ldots < a_k"),
                TexMobject("a_1, \\dots, a_k \\in \\mathds{Z}^+"),
            ),
            VGroup(
                TexMobject("{a \\over b + c} + {b \\over c + a} + {c \\over b + c} = 4"),
                TexMobject("a, b, c \\in \\mathds{Z}^+"),
            ),
            VGroup(
                TexMobject("x^n + y^n = z^n"),
                TexMobject("x, y, z \\in \\mathds{Z}"),
            ),
        )
        colors = Color(GREEN).range_to(RED, 4)
        for prob, x, color in zip(problems, [0, 0.3, 0.7, 1], colors):
            triangle = Triangle()
            triangle.set_height(0.2)
            triangle.set_stroke(width=0)
            triangle.set_fill(color, 1)
            triangle.move_to(line.n2p(x), UP)
            prob.arrange(DOWN)
            prob.scale(0.5)
            prob.next_to(triangle, DOWN)
            prob.add(triangle)
            prob.set_color(color)

        self.add(problems)

        # Group question
        tri = Triangle(start_angle=-90 * DEGREES)
        tri.set_height(0.3)
        tri.set_stroke(width=0)
        tri.set_fill(GREY_B, 1)
        tri.move_to(line.n2p(0.5), DOWN)
        question = TextMobject("What are all\\\\the groups?")
        question.next_to(tri, UP)

        ext_line = line.copy()
        ext_line.move_to(line.get_right(), LEFT)

        frame = self.camera.frame

        self.play(
            DrawBorderThenFill(tri),
            FadeIn(question, DOWN)
        )
        question.add(tri)
        self.play(question.move_to, line.n2p(0.9), DOWN)
        self.wait()
        self.play(
            ShowCreation(ext_line),
            question.move_to, line.n2p(1.3), DOWN,
            ApplyMethod(frame.scale, 1.3, {"about_edge": LEFT}, run_time=2)
        )
        self.wait()


class AmbientSnowflakeSymmetries(Scene):
    def construct(self):
        title = TexMobject("D_6")
        title.scale(3)
        title.to_edge(LEFT, buff=1)
        title.set_color(BLUE)
        self.add(title)

        snowflake = get_snowflake()
        snowflake.set_height(5)
        snowflake.set_stroke(width=0)
        snowflake.move_to(2 * RIGHT)
        self.add(snowflake)

        for n in range(10):
            if random.choice([True, False]):
                deg = random.choice([-120, -60, 60, 120])
                icon = get_rot_icon(deg, snowflake, snowflake.get_height())
                anim = Rotate(snowflake, deg * DEGREES)
            else:
                deg = random.choice(range(30, 180, 30))
                angle = deg * DEGREES
                icon = get_flip_icon(angle, snowflake, mini_mob_height=snowflake.get_height())
                anim = Rotate(snowflake, PI, axis=rotate_vector(RIGHT, angle))
            icon.shift(snowflake.get_center() - icon[0].get_center())
            self.play(anim, FadeIn(icon[1:]))
            self.play(FadeOut(icon[1:]))


class IntroduceSimpleGroups(Scene):
    def construct(self):
        # Setup
        bg_rect = FullScreenFadeRectangle(fill_color=GREY_E, fill_opacity=1)
        self.add(bg_rect)

        groups = TextMobject("Groups")
        groups.scale(2)
        groups.to_edge(UP)
        inf_groups = TextMobject("Infinite groups")
        fin_groups = TextMobject("Finite groups")
        children = VGroup(inf_groups, fin_groups)
        children.scale(1.5)
        children.arrange(RIGHT, buff=2)
        children.next_to(groups, DOWN, buff=2)
        child_lines = VGroup(*[
            Line(groups.get_bottom(), child.get_top(), buff=0)
            for child in children
        ])
        child_lines.set_stroke(WHITE, 2)
        s_rects = VGroup(*[
            ScreenRectangle(height=3).move_to(child)
            for child in children
        ])
        s_rects.next_to(children, DOWN)
        s_rects.set_fill(BLACK, 1)

        # Introductions
        self.add(groups)
        self.wait()
        self.play(
            ShowCreation(child_lines[0]),
            FadeIn(inf_groups, 2 * UR),
            FadeIn(s_rects[0])
        )
        self.wait(2)
        self.play(
            ShowCreation(child_lines[1]),
            FadeIn(fin_groups, 2 * UL),
            FadeIn(s_rects[1]),
        )
        self.wait()

        self.add(s_rects, fin_groups)
        self.play(
            Uncreate(child_lines),
            FadeOut(inf_groups, 3 * LEFT),
            FadeOut(s_rects[0], 3 * LEFT),
            FadeOut(groups, 2 * UP),
            fin_groups.move_to, groups,
            s_rects[1].replace, bg_rect,
            s_rects[1].set_stroke, {"width": 0},
            run_time=2,
        )
        self.remove(s_rects, bg_rect)

        # Comparison titles
        bg_rects = VGroup(*[
            Rectangle(
                height=FRAME_HEIGHT,
                width=FRAME_WIDTH / 3,
                fill_color=color,
                fill_opacity=1,
                stroke_width=0
            )
            for color in [GREY_D, GREY_E, BLACK]
        ])
        bg_rects.arrange(RIGHT, buff=0)
        bg_rects.center()

        fin_groups.generate_target()
        titles = VGroup(
            TextMobject("Integers").scale(1.5),
            TextMobject("Molecules").scale(1.5),
            fin_groups.target,
        )
        sub_titles = VGroup(*[
            TextMobject("break down into\\\\", word)
            for word in ("primes", "atoms", "simple groups")
        ])

        for rect, title, sub_title in zip(bg_rects, titles, sub_titles):
            title.move_to(rect, UP)
            title.shift(0.5 * DOWN)
            sub_title.next_to(title, DOWN)
            sub_title[1].set_color(BLUE)
            sub_title.align_to(sub_titles[0], UP)

        # Comparison diagrams
        H_sphere = Sphere()
        H_sphere.set_height(0.5)
        H_sphere.set_color(RED)
        H_atom = Group(
            H_sphere,
            TextMobject("H").scale(0.5).move_to(H_sphere)
        )
        O_sphere = Sphere()
        O_sphere.set_height(1)
        O_sphere.set_color(BLUE)
        O_atom = Group(
            O_sphere,
            TextMobject("O").scale(0.75).move_to(O_sphere)
        )
        H2O = Group(
            O_atom.copy(),
            H_atom.copy().move_to([-0.45, 0.35, 0]),
            H_atom.copy().move_to([0.45, 0.35, 0]),
        )

        trees = Group(
            VGroup(
                Integer(60),
                VGroup(*map(Integer, [2, 2, 3, 5])),
            ),
            Group(
                H2O,
                Group(H_atom.copy(), H_atom.copy(), O_atom.copy())
            ),
            VGroup(
                TexMobject("S_4"),
                VGroup(*[
                    TexMobject(
                        "C_" + str(n),
                        fill_color=(RED_B if n == 2 else BLUE)
                    )
                    for n in [2, 2, 2, 3]
                ]),
            )
        )
        for tree, rect in zip(trees, bg_rects):
            root, children = tree
            children.arrange(RIGHT, buff=0.35)
            children.next_to(root, DOWN, buff=1.2)
            lines = VGroup()
            for child in children:
                lines.add(Line(root.get_bottom(), child.get_top(), buff=0.1))
            tree.add(lines)
            tree.move_to(rect)
            tree.shift(DOWN)

        # Slice screen
        self.add(bg_rects, fin_groups)
        for rect in bg_rects:
            rect.save_state()
            rect.shift(LEFT)
            rect.set_fill(BLACK, 1)
        self.play(
            MoveToTarget(fin_groups),
            LaggedStartMap(Restore, bg_rects, lag_ratio=0.3)
        )

        # Breakdowns
        for title, sub_title, tree in zip(titles, sub_titles, trees):
            root, children, lines = tree
            self.play(
                FadeIn(title),
                FadeIn(root),
            )
            globals()['root'] = root
            self.play(
                ShowCreation(lines),
                LaggedStart(*[
                    GrowFromPoint(child, root)
                    for child in children
                ]),
                FadeIn(sub_title)
            )
            self.wait()

        # Theorem
        theorem_name = TextMobject("(Jordan–Hölder Theorem)")
        theorem_name.scale(0.7)
        theorem_name.next_to(sub_titles[2], DOWN)
        self.play(Write(theorem_name, run_time=1))
        self.wait()


class SymmetriesOfCirleAndLine(Scene):
    def construct(self):
        line = NumberLine((0, 100, 1))
        line.move_to(2 * UP)

        circle = Circle(radius=1)
        circle_ticks = VGroup(*[
            Line(0.95 * vect, 1.05 * vect)
            for vect in compass_directions(12)
        ])
        circle.add(circle_ticks)
        circle.set_stroke(BLUE, 3)
        circle.scale(1.5)
        circle.next_to(line, DOWN, buff=2)
        circle.shift(RIGHT)

        R_label = TexMobject("\\mathds{R}")
        RmodZ = TexMobject("\\mathds{R} / \\mathds{Z}")
        R_label.set_height(0.9)
        R_label.next_to(line, UP, MED_LARGE_BUFF)
        RmodZ.set_height(0.9)
        RmodZ.next_to(circle, LEFT, LARGE_BUFF)
        R_label.match_x(RmodZ)

        self.add(line)
        self.add(circle)
        self.add(R_label)
        self.add(RmodZ)

        # Rotations and shifts
        for n in range(10):
            x = interpolate(-20, 20, random.random())
            self.play(
                line.shift, x * RIGHT,
                Rotate(circle, -x / PI),
                run_time=2,
            )
            self.wait()

        self.embed()


class QuinticImpliesCyclicDecomposition(Scene):
    def construct(self):
        # Title
        title = TextMobject("Quintic formula")
        title.scale(1.5)
        title.to_edge(UP)
        details = TextMobject(
            "Solve ",
            "$a_5 x^5 + a_4 x^4 + a_3 x^3 + a_2 x^2 + a_1 x + a_0$\\\\",
            " using only ",
            "+, -, $\\times$, $/$, and $\\sqrt[n]{\\quad}$"
        )
        details[1].set_color(BLUE)
        details[3].set_color(TEAL)
        details.match_width(title)
        details.scale(1.2)
        details.next_to(title, DOWN)

        self.clear()
        self.add(title)
        self.wait()
        self.play(FadeIn(details, 0.5 * UP))
        self.wait()

        full_title = VGroup(title, details)

        # Show Implication
        implies = TexMobject("\\Downarrow").scale(2)
        implies.next_to(details, DOWN, LARGE_BUFF)

        s5 = TexMobject("S_5")
        prime_children = VGroup(
            TexMobject("C_{p_1}"),
            TexMobject("C_{p_2}"),
            TexMobject("\\vdots"),
            TexMobject("C_{p_n}"),
        )
        prime_children.set_color(RED_B)

        real_children = VGroup(
            TexMobject("A_5"),
            TexMobject("C_2"),
        )
        real_children.set_color(GREEN)

        for children, buff in (prime_children, MED_LARGE_BUFF), (real_children, LARGE_BUFF):
            children.arrange(DOWN, buff=buff, aligned_edge=LEFT)
            children.next_to(s5, RIGHT, buff=0.5 + 0.25 * len(children))
            children.lines = VGroup()
            for child in children:
                children.lines.add(
                    Line(s5.get_right(), child.get_left(), buff=0.1)
                )
        prime_children[2].shift(SMALL_BUFF * RIGHT)

        VGroup(
            s5, prime_children.lines, prime_children,
            real_children.lines, real_children,
        ).next_to(implies, DOWN)

        # Show decomps
        implies.save_state()
        implies.stretch(0, 1, about_edge=UP)
        self.play(
            Restore(implies),
            GrowFromPoint(s5, implies.get_top()),
        )
        self.play(
            LaggedStartMap(ShowCreation, prime_children.lines, lag_ratio=0.3),
            LaggedStartMap(
                FadeIn, prime_children,
                lambda m: (m, s5.get_right() - m.get_center()),
                lag_ratio=0.3,
            )
        )
        self.wait()
        self.play(
            FadeOut(prime_children, RIGHT),
            *[
                ApplyMethod(line.scale, 0, {"about_point": line.get_end()}, remover=True)
                for line in prime_children.lines
            ],
            LaggedStartMap(ShowCreation, real_children.lines, lag_ratio=0.3),
            LaggedStartMap(
                FadeIn, real_children,
                lambda m: (m, s5.get_right() - m.get_center()),
                lag_ratio=0.3,
            )
        )
        self.play(ShowCreationThenFadeAround(real_children[0]))

        # Reverse implication
        title_rect = SurroundingRectangle(full_title)
        title_rect.set_stroke(RED, 2)
        not_exists = TextMobject("No\\\\such\\\\thing")
        not_exists.match_height(title_rect)
        not_exists.set_color(RED)
        not_exists.next_to(title_rect, LEFT)
        full_title.add(title_rect, not_exists)

        self.play(
            Rotate(implies, PI),
            VFadeIn(title_rect),
            VFadeIn(not_exists),
            full_title.shift, 0.5 * RIGHT,
        )


class CommentOnNontrivialFactFromGroupDecomposition(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "I...don't\\\\get it.",
            target_mode="confused",
            student_index=2,
            look_at_arg=self.screen,
            added_anims=[self.teacher.change, "guilty"],
        )
        self.change_student_modes("maybe", "tired", look_at_arg=self.screen)
        self.wait(4)

        fp_words = TextMobject("Fact about\\\\polynomials")
        fp_words.scale(1.25)
        as_words = TextMobject("``Atomic structure''\\\\of a group")
        as_words.scale(1.25)
        implies = TexMobject("\\Rightarrow").scale(2)

        self.teacher_holds_up(
            fp_words,
            added_anims=[
                RemovePiCreatureBubble(self.students[2]),
            ]
        )
        self.change_student_modes("pondering", "hesitant", "plain", look_at_arg=fp_words)
        self.wait()
        as_words.next_to(fp_words, LEFT, buff=1.5)
        implies.move_to(midpoint(as_words.get_right(), fp_words.get_left()))

        self.play(
            FadeIn(as_words, RIGHT),
            Write(implies),
            self.get_student_changes(*3 * ["pondering"], look_at_arg=as_words)
        )
        self.wait(5)


class TwoStepsToAllFiniteGroups(Scene):
    def construct(self):
        # List
        title = TextMobject("How to categorize all finite groups")
        title.scale(1.5)
        title.add(Underline(title))
        title.to_edge(UP)

        steps = VGroup(
            TextMobject("1. ", "Find all the ", "simple groups", "."),
            TextMobject("2. ", "Find all the ", "ways to\\\\", "combine ", "simple groups", "."),
        )
        steps[1][3:].next_to(steps[1][1], DOWN, SMALL_BUFF, aligned_edge=LEFT)
        steps.arrange(DOWN, aligned_edge=LEFT, buff=2)
        steps.set_y(-0.5)
        steps.to_edge(LEFT)
        for step in steps:
            step.set_color_by_tex("simple groups", TEAL)

        self.add(title)
        self.wait()
        self.play(LaggedStartMap(
            FadeIn, VGroup(steps[0][0], steps[1][0]),
            lambda m: (m, RIGHT),
            lag_ratio=0.4,
        ))
        self.wait()
        self.play(FadeIn(steps[0][1:], lag_ratio=0.1))
        self.wait()
        self.play(
            TransformFromCopy(steps[0][1], steps[1][1]),
            TransformFromCopy(steps[0][2], steps[1][4]),
            FadeIn(VGroup(*[steps[1][i] for i in (2, 3, 5)])),
        )
        self.wait()

        # Periodic table
        table = VGroup(*[
            VGroup(*[
                Square() for x in range(n)
            ]).arrange(DOWN, buff=0)
            for n in [7, 6, *[4] * 10, *[6] * 5, 7]
        ])
        table.arrange(RIGHT, buff=0, aligned_edge=DOWN)
        table.set_width(4)
        table.to_edge(RIGHT)
        table.match_y(steps[0])
        table.set_stroke(GREY_A, 2)

        table_arrow = Arrow(
            steps[0].get_right(), table.get_left(),
            buff=0.5,
        )

        self.play(
            GrowArrow(table_arrow),
            FadeIn(table, lag_ratio=0.1, run_time=3),
        )
        self.wait()

        # Chemistry
        chem_words = TextMobject("All of chemistry")
        chem_words.match_y(steps[1])
        chem_words.match_x(table)
        chem_words.set_color(RED)
        chem_arrow = Arrow(
            steps[1].get_right(), chem_words.get_left(),
            buff=0.5
        )
        self.play(
            GrowArrow(chem_arrow),
            Write(chem_words),
        )
        self.wait()

        # Found all simples
        top_group = VGroup(steps[0], table_arrow, table)
        bottom_group = VGroup(steps[1], chem_arrow, chem_words)
        frame = self.camera.frame

        top_rect = SurroundingRectangle(top_group, buff=MED_LARGE_BUFF)
        top_rect.set_stroke(GREEN, 4)
        check = Checkmark()
        check.set_height(0.7)
        check.next_to(top_rect, UP, aligned_edge=LEFT)
        check.shift(RIGHT)

        self.play(
            frame.scale, 1.1,
            bottom_group.shift, 0.5 * DOWN,
            bottom_group.set_opacity, 0.5,
            ShowCreation(top_rect),
            FadeOut(title, UP),
        )
        self.play(Write(check))
        self.wait()

        proof_words = TextMobject("(prove you have them all.)")
        proof_words.next_to(steps[0], DOWN)
        proof_words.set_color(GREY_A)
        self.play(Write(proof_words, run_time=2))
        self.wait()

        # What was involved
        stats = VGroup(
            TextMobject("1955-2004"),
            TextMobject("$10{,}000+$ pages"),
            TextMobject("100's of mathematicians"),
            TextMobject("Plenty of computation"),
        )
        stats.arrange_in_grid(buff=1.5, aligned_edge=LEFT)
        stats.next_to(top_rect, DOWN, buff=LARGE_BUFF)
        for stat in stats:
            dot = Dot()
            dot.next_to(stat, LEFT)
            stat.add(dot)

        turn_animation_into_updater(ApplyMethod(frame.shift, DOWN, run_time=3))
        self.add(frame)
        for stat in stats:
            self.play(FadeIn(stat), bottom_group.set_opacity, 0)
            self.wait(0.5)
        self.remove(bottom_group)

        # 2004 paper mention
        stats.generate_target()
        stats.target.arrange(DOWN, buff=MED_LARGE_BUFF, aligned_edge=LEFT)
        stats.target.move_to(stats, UL)

        last_paper = TextMobject(
            "The Classification of Quasithin Groups\\\\",
            "Aschbacher and Smith (2004)\\\\",
            "(12{,}000 pages!)",
        )
        last_paper.scale(0.7)
        last_paper[:-1].set_color(YELLOW)
        last_paper.move_to(stats, RIGHT)
        last_paper.shift(RIGHT)

        self.play(
            FadeIn(last_paper, DOWN),
            MoveToTarget(stats),
        )
        self.wait()

        # Quote
        quote = TextMobject(
            """
            ``...undoubtedly one of the most\\\\
            extraordinary theorems that pure\\\\
            mathematics has ever seen.''\\\\
            """,
            "-Richard Elwes",
            alignment="",
        )
        quote.scale(0.9)
        quote[0].set_color(YELLOW)
        quote[-1].shift(MED_SMALL_BUFF * DR)
        quote.move_to(last_paper, LEFT)

        self.play(
            FadeIn(quote),
            FadeOut(last_paper),
        )
        self.wait()


class ClassificationOfSimpleGroups(Scene):
    def construct(self):
        # Title
        class_title = TextMobject("Classification of finite simple groups")
        class_title.set_width(FRAME_WIDTH - 4)
        class_title.add(Underline(class_title).set_color(GREY_B))
        class_title.to_edge(UP)
        self.add(class_title)

        # 18 families
        square_template = Square(side_length=0.3)
        square_template.set_stroke(GREY_B, 2)
        square_template.set_fill(BLUE_E, 0.5)
        families_grid = VGroup(*[
            VGroup(*[square_template.copy() for x in range(8)])
            for y in range(18)
        ])
        for family in families_grid:
            family.arrange(DOWN, buff=0)
            dots = TexMobject("\\vdots")
            dots.next_to(family, DOWN)
            family.add(dots)
        families_grid.arrange(RIGHT, buff=MED_SMALL_BUFF)
        families_grid.to_edge(LEFT)
        families_grid.set_y(-1)

        families_title = TextMobject("18 infinite families")
        families_title.set_color(BLUE)
        families_title.next_to(families_grid, UP, MED_LARGE_BUFF)

        self.play(
            FadeIn(families_title),
            FadeIn(families_grid, lag_ratio=0.1, run_time=4),
        )
        self.wait()

        # Analogize to periodic table
        families_grid.generate_target()
        families_grid.save_state()
        families_grid.target.arrange(RIGHT, buff=0)
        families_grid.target.move_to(families_grid)
        faders = VGroup(*[
            column[:n]
            for column, n in zip(families_grid.target, [
                0, 1, *[3] * 10, *[1] * 5, 0,
            ])
        ])
        faders.set_opacity(0)

        self.play(MoveToTarget(families_grid, lag_ratio=0.001))
        self.wait(2)
        self.play(Restore(families_grid))

        # Sporadic
        sporadics = VGroup(*[square_template.copy() for x in range(26)])
        buff = 0.1
        sporadics[:20].arrange_in_grid(10, 2, buff=buff)
        sporadics[20:].arrange(DOWN, buff=buff)
        sporadics[20:].next_to(sporadics[:20], RIGHT, buff)
        sporadics.next_to(families_grid, RIGHT, buff=1.5, aligned_edge=UP)
        sporadics.set_fill(YELLOW_E)

        pre_sporadics_title = TextMobject("26", " leftovers")
        sporadics_title = TextMobject("26", " ``sporadic''\\\\groups")
        for title in pre_sporadics_title, sporadics_title:
            title.set_color(YELLOW)
            title.next_to(sporadics, UP, MED_LARGE_BUFF)
        sporadics_title.shift(MED_SMALL_BUFF * DOWN)

        self.play(
            FadeIn(pre_sporadics_title, DOWN),
            ShowIncreasingSubsets(sporadics, run_time=3),
        )
        self.wait()
        self.play(
            ReplacementTransform(pre_sporadics_title[0], sporadics_title[0]),
            FadeOut(pre_sporadics_title[1], UP),
            FadeIn(sporadics_title[1], DOWN),
        )
        self.wait()

        # Show prime cyclic groups
        families_grid.save_state()
        column = families_grid[0]

        def prepare_column(column):
            column.generate_target()
            column.target.set_height(FRAME_HEIGHT)
            column.target.move_to(5 * LEFT)
            column.target.to_edge(UP)
            column.target[-1].scale(0.5, about_point=column.target[-2].get_bottom())

        prepare_column(column)

        self.play(
            MoveToTarget(column),
            FadeOut(families_grid[1:], lag_ratio=0.1),
            FadeOut(families_title),
            FadeOut(class_title, UP),
            FadeOut(sporadics, 2 * RIGHT),
            FadeOut(sporadics_title, 2 * RIGHT),
        )

        # C5
        c_names = VGroup(*[
            TexMobject(f"C_{{{p}}}")
            for p in [2, 3, 5, 7, 11, 13, 17, 19]
        ])

        def put_in_square(mob, square, factor=0.4):
            mob.set_height(factor * square.get_height())
            mob.move_to(square)

        def put_names_in_column(names, column):
            for name, square in zip(names, column):
                put_in_square(name, square)

        put_names_in_column(c_names, column)

        self.play(FadeIn(c_names, lag_ratio=0.1))
        self.wait()

        pentagon = RegularPolygon(5)
        pentagon.set_height(3)
        pentagon.set_fill(TEAL_E, 0.5)
        pentagon.set_stroke(WHITE, 1)
        pentagon.move_to(2 * RIGHT)
        c_names.save_state()
        c5 = c_names[2]
        c5.generate_target()
        c5.target.scale(2)
        c5.target.next_to(pentagon, UP, LARGE_BUFF)

        self.play(
            MoveToTarget(c5),
            DrawBorderThenFill(pentagon, run_time=1),
        )
        pcenter = center_of_mass(pentagon.get_vertices())
        for n in [1, -2, 2]:
            self.play(Rotate(pentagon, n * TAU / 5, about_point=pcenter))
            self.wait(0.5)
        self.play(
            Restore(c_names),
            FadeOut(pentagon)
        )

        c_names.generate_target()
        c_names.target.replace(families_grid.saved_state[0])
        c_names.target.scale(0.9)
        c_names.target.set_opacity(0)
        families_grid[1:].fade(1)

        self.play(
            Restore(families_grid),
            MoveToTarget(c_names, remover=True)
        )

        # Alternating
        column = families_grid[1]
        prepare_column(column)
        self.play(
            MoveToTarget(column),
            FadeOut(families_grid[0]),
            FadeOut(families_grid[2:], lag_ratio=0.1),
        )

        a_names = VGroup(*[
            TexMobject(f"A_{{{n}}}")
            for n in range(5, 5 + len(column) - 1)
        ])
        put_names_in_column(a_names, column)
        self.play(FadeIn(a_names, lag_ratio=0.1))

        dots = VGroup(*[Dot() for x in range(5)])
        dots.set_height(0.5)
        dots.arrange(RIGHT, buff=MED_LARGE_BUFF)
        dots.set_submobject_colors_by_gradient(RED, YELLOW)
        dots.move_to(RIGHT)

        a5 = a_names[0]
        a5.save_state()
        a5.generate_target()
        a5.target.scale(2)
        a5.target.next_to(dots, UP, buff=1.5)

        self.play(
            FadeIn(dots, lag_ratio=0.1),
            MoveToTarget(a5),
        )
        for x in range(5):
            perm = list(range(5))
            swaps = 1  # Lie
            while swaps % 2 == 1:
                random.shuffle(perm)
                swaps = 0
                for i, j in it.combinations(perm, 2):
                    if j < i:
                        swaps += 1
            arrows = get_permutation_arrows(dots, perm)
            self.play(
                FadeIn(arrows),
                permutation_animation(dots, perm, lag_factor=0.1),
            )
            self.play(FadeOut(arrows))
        self.wait()

        self.play(
            FadeOut(dots, lag_ratio=0.1),
            Restore(a5),
        )
        self.wait()

        a_names.generate_target()
        a_names.target.replace(families_grid.saved_state[1])
        a_names.target.scale(0.9)
        a_names.target.fade(1)

        self.play(
            Restore(families_grid),
            MoveToTarget(a_names, remover=True),
            FadeIn(families_title),
            FadeIn(class_title),
        )

        # Others
        others_rect = SurroundingRectangle(families_grid[2:])
        others_rect.set_stroke(YELLOW, 2)
        others_name = TextMobject("Groups of\\\\Lie type")
        others_name.set_color(YELLOW)
        others_name.next_to(others_rect, RIGHT)
        self.play(ShowCreation(others_rect))
        self.play(FadeIn(others_name))
        self.wait()
        self.play(FadeOut(others_name), FadeOut(others_rect))

        # Back to sporadics
        self.play(
            ShowIncreasingSubsets(sporadics),
            FadeIn(sporadics_title),
        )
        self.wait()

        # Look closer at sporadics
        sporadics.generate_target()
        sporadics.target.rotate(PI, axis=UL)
        sporadics.target.set_width(FRAME_WIDTH - 1)
        sporadics.target.center().to_edge(DOWN)

        sporadics_title.save_state()
        sporadics.save_state()

        self.play(
            sporadics_title.scale, 1.25,
            sporadics_title.center,
            sporadics_title.to_edge, UP,
            MoveToTarget(sporadics),
            FadeOut(families_grid, LEFT),
            FadeOut(families_title, LEFT),
            FadeOut(class_title, UP),
        )

        # Monster
        monster = get_monster()
        put_in_square(monster, sporadics[0], 0.9)
        monster_name = TextMobject("Monster", " group")
        monster_name.next_to(sporadics[0], UP, LARGE_BUFF)
        monster_name.shift_onto_screen()
        monster_arrow = Arrow(monster_name.get_bottom(), monster.get_top())

        size_label = TextMobject("{:,}".format(MONSTER_SIZE))[0]
        size_label.scale(0.8)
        size_label.move_to(monster_name, LEFT)

        self.play(
            sporadics[0].set_fill, {"opacity": 0},
            FadeIn(monster)
        )
        self.play(
            Write(monster_name),
            GrowArrow(monster_arrow),
        )
        self.wait()

        # sporadics_title.generate_target()
        # sporadics_title.target.scale(1 / 1.5)
        # sporadics_title.target.to_corner(UR)
        self.play(
            monster_name.shift, 0.6 * UP,
            ShowIncreasingSubsets(size_label, run_time=2),
            # MoveToTarget(sporadics_title, run_time=2, rate_func=squish_rate_func(smooth, 0.5, 1))
        )
        self.wait()

        # Baby monster
        full_monster_label = VGroup(monster_name, size_label)
        full_monster_label.save_state()
        full_monster_label.generate_target()
        full_monster_label.target.to_edge(UP, buff=MED_SMALL_BUFF)
        full_monster_label.target.set_opacity(0.7)

        baby_name = TextMobject("Baby monster group")
        baby_name.move_to(size_label, LEFT)
        baby_arrow = Arrow(baby_name.get_bottom(), sporadics[1].get_corner(UR) + SMALL_BUFF * DL)
        baby_arrow.set_stroke(BLACK, 6, background=True)
        baby_size_label = TextMobject("{:,}".format(BABY_MONSTER_SIZE))[0]
        baby_size_label.scale(0.8)
        baby_size_label.move_to(baby_name, LEFT)

        baby_monster = get_baby_monster()
        baby_monster.set_width(0.9 * sporadics[1].get_width())
        baby_monster.move_to(sporadics[1])
        baby_monster.shift(SMALL_BUFF * DOWN)

        self.remove(monster_arrow)
        self.play(
            MoveToTarget(full_monster_label),
            TransformFromCopy(monster_arrow, baby_arrow),
            FadeIn(baby_name, DOWN),
            sporadics[1].set_fill, {"opacity": 0},
            FadeIn(baby_monster),
            FadeOut(sporadics_title, UP),
        )
        self.wait()
        self.play(
            baby_name.shift, 0.6 * UP,
            ShowIncreasingSubsets(baby_size_label, run_time=2)
        )
        self.wait()

        # 20 vs. 6
        top_20 = sporadics[:20]
        top_20.generate_target()
        top_20.target.shift(2 * UP)
        top_20.target[1:].set_fill(GREEN, 0.8)

        self.play(
            MoveToTarget(top_20),
            MaintainPositionRelativeTo(monster, sporadics[0]),
            MaintainPositionRelativeTo(baby_monster, sporadics[1]),
            UpdateFromAlphaFunc(baby_monster, lambda m, a: m.set_opacity(1 - a), remover=True),
            ApplyMethod(baby_arrow.scale, 0, {"about_point": baby_arrow.get_start()}, remover=True),
            FadeOut(baby_size_label, UP),
            FadeOut(baby_name, UP),
            full_monster_label.set_fill, WHITE, 1,
        )

        monster_name.generate_target()
        monster_name.target.arrange(DOWN, buff=MED_SMALL_BUFF, aligned_edge=LEFT)
        monster_name.target.next_to(sporadics[0], UP, SMALL_BUFF, aligned_edge=LEFT)

        happy_family_name = TextMobject("``Happy family''")
        happy_family_name.set_height(0.7)
        happy_family_name.to_edge(UP)
        happy_family_name.set_color(GREEN)

        self.play(
            MoveToTarget(monster_name),
            FadeOut(size_label, DOWN),
            FadeIn(happy_family_name, UP),
        )
        self.wait()

        pariahs = sporadics[20:]
        pariahs_name = TextMobject("``Pariahs''")
        pariahs_name.set_height(0.7)
        pariahs_name.next_to(pariahs, UP, MED_LARGE_BUFF)
        pariahs_name.set_color(YELLOW)

        self.play(
            FadeIn(pariahs_name, UP),
            pariahs.set_fill, YELLOW, 0.7,
        )
        self.wait()


class ImSorryWhat(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "I'm sorry, what?!",
            target_mode="sassy",
            look_at_arg=self.screen,
        )
        self.change_student_modes("angry", "maybe", "sassy", look_at_arg=self.screen)
        self.wait(3)
        self.change_student_modes("pleading", "confused", "erm", look_at_arg=self.screen)
        self.wait(5)


class TellMeTheresAChildrensBook(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Please tell me\\\\there's a children's\\\\book about this!",
            target_mode="surprised",
            added_anims=[self.teacher.change, "tease"]
        )
        self.change_student_modes("happy", "coin_flip_1", look_at_arg=self.screen)
        self.look_at(self.screen)
        self.wait(5)


class AskWhatTheMonsterActsOn(Scene):
    def construct(self):
        # Setup
        question = TextMobject(
            "The monster group describes the symmetries of ",
            "$\\underline{\\qquad\\qquad\\qquad}$",
        )
        question[1].set_color(YELLOW)
        question.to_edge(UP)

        monster = get_monster()
        monster.set_height(5)
        monster.to_corner(DL)

        self.add(monster)
        self.play(FadeIn(question, DOWN))
        self.wait()

        # Dimension counts
        dim_words = VGroup(*[
            TextMobject(
                "Something in\\\\",
                "{:,}".format(n),
                " dimensions",
                "?"
            )
            for n in [2, 3, 4, 5, 196883]
        ])
        dim_words.scale(1.25)
        dim_words.to_edge(RIGHT, buff=LARGE_BUFF)
        dim_words.set_y(1.5)

        final_words = dim_words[-1]
        dim = Integer(196883, edge_to_fix=ORIGIN)
        dim.replace(final_words[1])
        dim.match_style(final_words[1])
        final_words.replace_submobject(1, dim)
        final_words[-1].set_opacity(0)

        cross = Cross(dim_words)
        cross.set_stroke(RED, 8)
        for dim_word in dim_words[:-1]:
            cross.replace(dim_word[1], stretch=True)
            self.add(dim_word)
            self.wait()
            self.play(ShowCreation(cross, run_time=0.5))
            self.wait(0.5)
            self.remove(dim_word, cross)

        penult = dim_words[-2]
        dim.set_value(0)
        for i in 0, 2:
            final_words[i].save_state()
            final_words[i].replace(penult[i])
        self.play(
            Restore(final_words[0]),
            Restore(final_words[2]),
            FadeOut(penult[3]),
            ChangingDecimal(
                dim,
                lambda a: interpolate(5, 196883, a),
                run_time=8,
                rate_func=rush_from,
            ),
            UpdateFromAlphaFunc(
                Mobject(),
                lambda m, a, fw=final_words: fw.set_color(interpolate_color(WHITE, YELLOW, a)),
                remover=True
            )
        )
        final_words.add(dim)
        self.add(final_words)
        self.wait()
        self.play(blink_monster(monster))
        self.wait()

        # Elements of the monster
        in_sym = TexMobject("\\in")
        in_sym.scale(2.5)

        monster.generate_target()
        monster.target.center().to_edge(RIGHT)
        in_sym.next_to(monster.target, LEFT, MED_LARGE_BUFF)

        self.play(
            MoveToTarget(monster),
            FadeOut(question, 3 * RIGHT),
            FadeOut(final_words, 2 * RIGHT),
            FadeIn(in_sym, 3 * LEFT),
        )

        matrix = IntegerMatrix(
            np.random.randint(0, 2, size=(6, 6)),
            v_buff=0.8,
            h_buff=0.8,
        )
        matrix.set_height(4)
        matrix.next_to(in_sym, LEFT, MED_LARGE_BUFF)

        mob_matrix = matrix.get_mob_matrix()
        groups_to_dots = [
            (mob_matrix[4, :4], TexMobject("\\vdots")),
            (mob_matrix[:4, 4], TexMobject("\\ldots")),
            (VGroup(mob_matrix[4, 4]), TexMobject("\\ddots")),
        ]
        for group, dots in groups_to_dots:
            for elem in group:
                dots_copy = dots.copy()
                dots_copy.move_to(elem)
                elem.set_submobjects(dots_copy)

        braces = VGroup(
            Brace(matrix.get_entries(), DOWN),
            Brace(matrix.get_entries(), LEFT),
        )
        braces[1].shift(MED_SMALL_BUFF * LEFT)
        for brace in braces:
            brace.add(brace.get_text("196{,}882"))
        braces.set_color(BLUE)

        gigs_label = TextMobject("Each element $\\approx$ 4.5 Gigabytes of data!")
        gigs_label.next_to(matrix, UP, MED_LARGE_BUFF)

        self.play(Write(matrix, run_time=1))
        self.play(
            LaggedStartMap(GrowFromCenter, braces, lag_ratio=0.5, run_time=1),
            FadeIn(gigs_label, DOWN)
        )
        self.play(blink_monster(monster))
        self.wait()


class MonsterQuotes(Scene):
    def construct(self):
        images = [
            get_named_image("John Conway"),
            get_named_image("Richard Borcherds"),
        ]

        quotes = [
            TextMobject(
                """
                ``Nothing has given me the feeling\\\\
                that I understand why the monster\\\\
                is there.''\\\\
                """,
                alignment="",
            ),
            TextMobject(
                """
                ``The monster simple group . . . appears\\\\
                to rely on numerous bizarre coincidences\\\\
                to exist.''\\\\
                """,
                alignment="",
            ),
        ]
        faders = []
        self.clear()
        for image, quote, color in zip(images, quotes, [YELLOW, WHITE]):
            quote[0].set_color(color)

            image.set_height(5)
            image.to_edge(LEFT)
            image[1].set_color(GREY_B)
            quote.next_to(image, RIGHT, buff=1, aligned_edge=UP)
            quote.shift(DOWN)
            quote.shift_onto_screen()

            self.play(
                FadeIn(image, DOWN),
                FadeIn(quote, lag_ratio=0.1, run_time=3),
                *faders,
            )
            self.wait(4)
            faders = [FadeOut(image, UP), FadeOut(quote)]


class MonstrousMoonshine(Scene):
    def construct(self):
        # Time line
        decades = list(range(1970, 2030, 10))
        timeline = NumberLine(
            (decades[0], decades[-1], 1),
            numbers_with_elongated_ticks=decades,
            tick_size=0.075,
            width=13,
        )
        timeline.add_numbers(decades, number_config={"group_with_commas": False})
        timeline.move_to(DOWN)
        self.add(timeline)

        triangle = Triangle()
        triangle.rotate(PI)
        triangle.set_height(0.25)
        triangle.set_fill(BLUE_C, 1)
        triangle.set_stroke(WHITE, 0)
        triangle.move_to(timeline.n2p(2020), DOWN)
        self.add(triangle)

        self.play(
            triangle.move_to, timeline.n2p(1978), DOWN,
            run_time=3,
        )

        # McKay
        mckay = get_named_image("John McKay")
        mckay[0].flip()
        mckay.next_to(triangle, UP)

        self.play(FadeIn(mckay, DOWN))
        self.wait()

        theories = VGroup(
            TextMobject("Finite group theory"),
            TextMobject("Galois theory"),
        )
        theories.arrange(RIGHT, buff=1.5)
        theories.next_to(mckay, RIGHT, LARGE_BUFF)
        theories_line, theories_arrow = [
            func(
                *[theory.get_top() for theory in theories],
                path_arc=-90 * DEGREES,
                buff=0.2,
            ).shift(0.25 * UP)
            for func in [Line, Arrow]
        ]
        theories_line.set_stroke(BLUE_C, 6)
        theories_arrow.set_fill(BLUE_C)

        self.play(FadeIn(theories[0], LEFT))
        self.play(
            GrowFromPoint(theories[1], theories_line.get_start(), path_arc=-90 * DEGREES),
            ShowCreationThenFadeOut(theories_line, run_time=2),
            FadeIn(theories_arrow, rate_func=squish_rate_func(smooth, 0.3, 1), run_time=2)
        )
        self.wait()

        theories_group = VGroup(theories, theories_arrow)

        # j function
        j_func = TexMobject(
            "j(\\tau)  =q^{-1}+744+196{,}884 q+21{,}493{,}760 q^{2}+864{,}299{,}970 q^{3}+\\cdots\\\\",
            "\\big(q = e^{2\\pi i \\tau}\\big)",
            tex_to_color_map={
                "\\tau": TEAL,
                "q": BLUE,
                "196{,}884": WHITE,
            }
        )
        j_func.scale(0.7)
        j_func[-5:].shift([-0.5, -0.25, 0])
        j_func.next_to(mckay, RIGHT, aligned_edge=DOWN)
        j_func.shift(0.5 * UP)

        special_num = j_func.get_part_by_tex("196{,}884")
        special_num_underline = Underline(special_num)
        special_num_underline.set_stroke(YELLOW, 3)

        self.play(
            theories_group.scale, 0.5, {"about_edge": UL},
            theories_group.to_edge, UP,
            Write(j_func)
        )
        self.wait()
        self.play(
            ShowCreation(special_num_underline),
            special_num.set_color, YELLOW,
        )
        self.wait()

        j_coloring = ImageMobject("J_Invariant_Coloring")
        j_coloring.set_width(FRAME_WIDTH)
        j_coloring.to_edge(DOWN, buff=0)
        j_coloring.set_opacity(0.25)
        self.add(j_coloring, *self.mobjects)
        self.play(FadeIn(j_coloring))
        self.wait(0.5)
        self.play(FadeOut(j_coloring), FadeOut(special_num_underline))
        self.wait()

        # Conway
        conway = get_named_image("John Conway")
        conway[0].flip()
        conway.move_to(mckay)
        conway.to_edge(RIGHT)
        moonshine = TextMobject("Moonshine!")
        moonshine.set_height(0.6)
        moonshine.next_to(conway, LEFT, MED_LARGE_BUFF, aligned_edge=UP)
        moonshine.set_color(YELLOW)

        self.play(
            FadeOut(timeline, DOWN),
            FadeOut(triangle, DOWN),
            j_func.to_edge, DOWN,
            FadeOut(theories_group),
            FadeIn(conway, DOWN),
        )
        self.play(Write(moonshine))
        self.wait()

        # Conjecture
        conjecture = TextMobject("Monstrous ", "moonshine\\\\", " conjecture")
        conjecture_icon = VGroup(
            get_monster().set_height(1),
            TexMobject("\\leftrightarrow"),
            TexMobject("j(\\tau)", tex_to_color_map={"\\tau": TEAL}),
        )
        conjecture_icon.arrange(RIGHT, buff=SMALL_BUFF)
        conjecture_icon.set_height(1.5)
        conjecture_icon.next_to(timeline.n2p(1979), UP, MED_LARGE_BUFF)
        conjecture.next_to(conjecture_icon, UP, MED_LARGE_BUFF)

        self.play(
            FadeIn(timeline, DOWN),
            FadeIn(triangle, DOWN),
            FadeOut(mckay, UP),
            Transform(
                moonshine,
                moonshine.copy().replace(conjecture[1], stretch=True).fade(1),
                remover=True,
            ),
            ReplacementTransform(
                conjecture[1].copy().replace(moonshine, stretch=True).fade(1),
                conjecture[1],
            ),
            Write(conjecture[0::2]),
        )
        self.play(
            FadeIn(conjecture_icon, lag_ratio=0.1),
            triangle.move_to, timeline.n2p(1979), DOWN,
        )
        self.play(blink_monster(conjecture_icon[0]))
        self.wait()

        conjecture_group = VGroup(conjecture, conjecture_icon)

        # Borcherds
        borcherds = get_named_image("Richard Borcherds")
        borcherds.next_to(timeline.n2p(1992), UP, MED_LARGE_BUFF)

        self.play(
            conjecture_group.scale, 0.5, {"about_edge": DOWN},
            triangle.move_to, timeline.n2p(1992), DOWN,
            FadeOut(conway, RIGHT),
            FadeIn(borcherds, 2 * LEFT)
        )
        self.wait(2)
        self.play(
            triangle.move_to, timeline.n2p(1998), DOWN,
            MaintainPositionRelativeTo(borcherds, triangle),
        )

        medal = ImageMobject("Fields Medal")
        medal.set_height(1)
        medal.move_to(borcherds.get_corner(UR), LEFT)
        self.play(FadeIn(medal, DOWN))
        self.wait()


class StringTheory(Scene):
    def construct(self):
        monster = get_monster()
        monster.set_height(4)
        arrow = TexMobject("\\leftrightarrow").scale(2)

        n = 10
        points = compass_directions(n)
        freqs = np.random.random(n) + 0.3

        string = VMobject()
        string.set_stroke([BLUE, TEAL, BLUE, TEAL, BLUE, TEAL, BLUE], 4)

        def update_string(string, points=points, freqs=freqs, sc=self):
            for point, freq in zip(points, freqs):
                point[:] = normalize(point) * (1 + 0.2 * np.sin(TAU * freq * sc.time))
            string.set_points_smoothly([*points, points[0]])

        string.add_updater(update_string)

        arrow.next_to(string, LEFT, LARGE_BUFF)
        monster.next_to(arrow, LEFT, LARGE_BUFF)
        # self.camera.frame.move_to(arrow)
        self.camera.frame.scale(0.5)

        st_name = TextMobject("String theory")
        st_name.scale(1.5)
        st_name.next_to(string, UP, LARGE_BUFF)

        sg_name = TextMobject("Sporadic groups")
        sg_name.scale(1.5)
        sg_name.next_to(monster, DOWN)

        self.add(monster)
        self.add(arrow)
        self.add(string)
        self.wait(2)
        self.play(Write(sg_name))
        self.play(Write(st_name))
        for x in range(4):
            self.play(blink_monster(monster))
            self.wait(5)


class MonsterThanks(PatreonEndScreen):
    pass
