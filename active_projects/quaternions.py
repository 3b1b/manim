from big_ol_pile_of_manim_imports import *
# from pprint import pprint


# Constants
# HIGH_QUALITY = True
HIGH_QUALITY = False


# Helpers
def get_three_d_scene_config():
    hq_config = {
        "camera_config": {
            "should_apply_shading": True,
        },
        "three_d_axes_config": {
            "num_axis_pieces": 20,
            "number_line_config": {
                "unit_size": 2,
                "tick_frequency": 0.5,
                "numbers_with_elongated_ticks": [0, 1, 2],
            }
        },
        "sphere_config": {
            "radius": 1,
        }
    }
    lq_added_config = {
        "camera_config": {
            "should_apply_shading": False,
        },
        "three_d_axes_config": {
            "num_axis_pieces": 5,
        },
    }
    if HIGH_QUALITY:
        return hq_config
    else:
        return merge_config([
            lq_added_config,
            hq_config
        ])


def q_mult(q1, q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
    z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
    return np.array([w, x, y, z])


def stereo_project_point(point, axis=0, r=1, max_norm=1000):
    point = fdiv(point * r, point[axis] + r)
    point[axis] = 0
    norm = get_norm(point)
    if norm > max_norm:
        point *= max_norm / norm
    return point


def stereo_project(mobject, axis=0, r=1, outer_r=10, **kwargs):
    epsilon = 1
    for submob in mobject.family_members_with_points():
        points = submob.points
        n = len(points)
        for i in range(n):
            if points[i, axis] == -r:
                js = it.chain(
                    range(i + 1, n),
                    range(i - 1, -1, -1)
                )
                for j in js:
                    if points[j, axis] == -r:
                        continue
                    else:
                        vect = points[j] - points[i]
                        points[i] += epsilon * vect
                        break
        submob.apply_function(
            lambda p: stereo_project_point(p, axis, r, **kwargs)
        )

        # If all points are outside a certain range, this
        # shouldn't be displayed
        norms = np.apply_along_axis(get_norm, 1, submob.points)
        if np.all(norms > outer_r):
            # TODO, instead set opacity?
            # submob.points[:, :] = 0
            submob.set_fill(opacity=0)
            submob.set_stroke(opacity=0)

    return mobject


class Linus(VGroup):
    CONFIG = {
        "body_config": {
            "stroke_width": 15,
            "stroke_color": LIGHT_GREY,
            "sheen": 0.4,
        },
        "height": 2,
    }

    def __init__(self, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.body = self.get_body_line()
        self.eyes = Eyes(self.body)

        self.add(self.body, self.eyes)
        self.set_height(self.height)
        self.center()

    def change_mode(self, mode, thing_to_look_at=None):
        self.eyes.change_mode(mode, thing_to_look_at)
        if mode == "sad":
            self.become_squiggle()
        elif mode == "confused":
            self.become_squiggle(factor=-0.1)
        elif mode == "pleading":
            self.become_squiggle(factor=0.3)
        else:
            self.become_line()
        return self

    def change(self, *args, **kwargs):
        self.change_mode(*args, **kwargs)
        return self

    def look_at(self, thing_to_look_at=None):
        self.eyes.look_at(thing_to_look_at)
        return self

    def blink(self):
        self.eyes.blink()
        return self

    def get_squiggle(self, factor=0.2):
        sine_curve = FunctionGraph(
            lambda x: factor * np.sin(x),
            x_min=0, x_max=TAU,
        )
        sine_curve.rotate(TAU / 4)
        sine_curve.match_style(self.body)
        sine_curve.match_height(self.body)
        sine_curve.move_to(self.body, UP)
        return sine_curve

    def get_body_line(self, **kwargs):
        config = dict(self.body_config)
        config.update(kwargs)
        line = Line(ORIGIN, 1.5 * UP, **config)
        if hasattr(self, "body"):
            line.match_style(self.body)
            line.match_height(self.body)
            line.move_to(self.body, UP)
        return line

    def become_squiggle(self, **kwargs):
        self.body.become(self.get_squiggle(**kwargs))
        return self

    def become_line(self, **kwargs):
        self.body.become(self.get_body_line(**kwargs))
        return self

    def copy(self):
        return self.deepcopy()


class PushPin(SVGMobject):
    CONFIG = {
        "file_name": "push_pin",
        "height": 0.5,
        "sheen": 0.7,
        "fill_color": GREY,
    }

    def __init__(self, **kwargs):
        SVGMobject.__init__(self, **kwargs)
        self.rotate(20 * DEGREES)

    def pin_to(self, point):
        self.move_to(point, DR)


class Hand(SVGMobject):
    CONFIG = {
        "file_name": "pinch_hand",
        "height": 0.4,
        "sheen": 0.2,
        "fill_color": GREY,
    }

    def __init__(self, **kwargs):
        SVGMobject.__init__(self, **kwargs)
        self.add(VectorizedPoint().next_to(self, UP, buff=0.15))


class CheckeredCircle(Circle):
    CONFIG = {
        "n_pieces": 16,
        "colors": [BLUE_E, BLUE_C],
        "stroke_width": 5,
    }

    def __init__(self, **kwargs):
        Circle.__init__(self, **kwargs)
        pieces = self.get_pieces(self.n_pieces)
        self.points = np.zeros((0, 3))
        self.add(*pieces)
        n_colors = len(self.colors)
        for i, color in enumerate(self.colors):
            self[i::n_colors].set_color(color)


# Abstract scenes
class SpecialThreeDScene(ThreeDScene):
    CONFIG = get_three_d_scene_config()

    def get_axes(self):
        return ThreeDAxes(**self.three_d_axes_config)

    def get_sphere(self):
        return Sphere(**self.sphere_config)


# Animated scenes
class Test(SpecialThreeDScene):
    CONFIG = {
        "sphere_config": {}
    }

    def construct(self):
        sphere = self.get_sphere()
        # sphere.set_fill(opacity=0.5)
        axes = self.get_axes()
        cube = Cube()
        cube.set_depth(4)
        cube.set_fill(BLUE_E, opacity=1)

        sphere_shadow = sphere.deepcopy()
        sphere_shadow.add_updater(
            lambda ss: ss.become(
                stereo_project(sphere.deepcopy())
            ).set_fill(BLUE_E, 0.5)
        )

        self.add(axes)
        self.add(sphere)
        self.add(sphere_shadow)
        # self.add(cube)
        self.move_camera(
            phi=70 * DEGREES,
            theta=-45 * DEGREES,
            run_time=0
        )
        # self.begin_ambient_camera_rotation()
        self.play(
            Rotate(sphere, 90 * DEGREES, axis=UP),
            run_time=3,
        )
        self.wait()


class IntroduceLinusTheLinelander(Scene):
    def construct(self):
        self.introduce_linus()
        self.show_real_number_line()
        self.look_at_complex_plane()

    def introduce_linus(self):
        linus = Linus()
        linus.move_to(3 * LEFT)
        name = TextMobject("Linus the Linelander")
        name.next_to(linus, DR, buff=MED_LARGE_BUFF)
        arrow = Arrow(name.get_top(), linus.get_right())

        self.play(FadeInFromDown(linus))
        self.play(
            Write(name),
            GrowArrow(arrow),
            linus.change, "gracious", name,
        )
        self.play(
            linus.become_squiggle, {"factor": -0.1},
        )
        self.play(Blink(linus))
        self.wait()

        self.name_text = name
        self.name_arrow = arrow
        self.linus = linus

    def show_real_number_line(self):
        linus = self.linus
        number_line = NumberLine()
        number_line.add_numbers()
        number_line.to_edge(UP)

        algebra = VGroup(
            TexMobject("3 \\cdot 4 = 12"),
            TexMobject("3 + 4 = 7"),
            TexMobject("(-2) \\cdot 3 = -6"),
        )
        algebra.arrange_submobjects(DOWN)
        algebra.next_to(number_line, DOWN, LARGE_BUFF)
        algebra.shift(3 * RIGHT)

        self.play(
            ShowCreation(number_line.main_line),
            linus.look_at, number_line
        )
        self.play(
            LaggedStart(FadeInFromDown, number_line.numbers),
            LaggedStart(ShowCreation, number_line.tick_marks),
            linus.change, "happy"
        )
        self.play(
            LaggedStart(FadeInFromDown, algebra),
            linus.look_at, algebra
        )
        self.play(Blink(linus))
        self.wait()

        self.algebra = algebra

    def look_at_complex_plane(self):
        linus = self.linus
        to_fade = VGroup(
            self.name_text,
            self.name_arrow,
            self.algebra,
        )
        frame = ScreenRectangle()
        frame.set_width(8)
        frame.to_corner(DR)

        q_marks = VGroup(*[
            TexMobject("?").shift(
                random.random() * RIGHT,
                random.random() * UP,
            )
            for x in range(50)
        ])
        q_marks.next_to(linus.body, UP, buff=0)
        q_marks.set_color_by_gradient(BLUE, GREEN, YELLOW)
        random.shuffle(q_marks.submobjects)
        q_marks_anim = LaggedStart(
            FadeIn, q_marks,
            run_time=15,
            rate_func=there_and_back,
            lag_ratio=0.1
        )
        q_marks_continual = NormalAnimationAsContinualAnimation(q_marks_anim)

        self.play(
            FadeOut(to_fade),
            ShowCreation(frame),
            linus.look_at, frame
        )
        self.add(q_marks_continual)
        self.play(linus.change_mode, "confused")
        self.wait()
        self.play(Blink(linus))
        self.play(linus.change, "confused", frame.get_bottom())
        self.wait()
        self.play(linus.change, "sad", frame.get_center())
        self.wait(10)


class ShowComplexMultiplicationExamples(Scene):
    CONFIG = {
        "plane_config": {
            "x_radius": 9,
            "y_radius": 9,
            "stroke_width": 3,
        },
        "background_plane_config": {
            "color": LIGHT_GREY,
            "secondary_color": DARK_GREY,
            "stroke_width": 0.5,
            "stroke_opacity": 0.5,
            "secondary_line_ratio": 0,
        }
    }

    def construct(self):
        self.add_planes()
        z_tuples = [
            (complex(2, 1), "2 + i", UP),
            (complex(5, 2), "5 + 2i", LEFT),
            (
                complex(-np.sqrt(2) / 2, np.sqrt(2) / 2),
                "-\\frac{\\sqrt{2}}{2} + \\frac{\\sqrt{2}}{2} i",
                LEFT,
            ),
            (complex(-4, 1.5), "-4 + 1.5i", RIGHT),
            (complex(3, 0), "3 + 0i", UP),
            (complex(4, -3), "4 + -3i", UP),
        ]

        for z, z_tex, label_vect in z_tuples:
            self.show_multiplication(z, z_tex, label_vect)

    def add_planes(self, include_title=True):
        plane = ComplexPlane(**self.plane_config)
        self.plane = plane
        background_plane = ComplexPlane(**self.background_plane_config)
        background_plane.add_coordinates()
        self.background_plane = background_plane

        self.add(background_plane)
        self.add(plane)

        if include_title:
            title = TextMobject("Complex plane")
            title.scale(1.5)
            title.to_corner(UL, buff=MED_LARGE_BUFF)
            title.shift(SMALL_BUFF * UR)
            self.title = title
            self.add_foreground_mobjects(title)

    def show_multiplication(self, z, z_tex, label_vect):
        z_color = WHITE
        plane = self.plane
        new_plane = plane.deepcopy()
        real_tex, imag_tex = z_tex.split("+")
        label = TexMobject(
            "\\text{Multiply by}\\\\",
            real_tex, "+", imag_tex,
            alignment="",
        )
        label[1].set_color(GREEN)
        label[3].set_color(RED)
        label.scale(1.2)

        h_line = Line(
            plane.number_to_point(0),
            plane.number_to_point(z.real),
            color=GREEN,
            stroke_width=5,
        )
        v_line = Line(
            plane.number_to_point(z.real),
            plane.number_to_point(z),
            color=RED,
            stroke_width=5,
        )
        lines = VGroup(h_line, v_line)

        z_point = plane.number_to_point(z)
        z_dot = Dot(z_point)
        z_dot.set_color(z_color)
        label[1:].next_to(z_dot, label_vect)
        label[0].next_to(label[1:], UP)
        for mob in label:
            label.add_to_back(BackgroundRectangle(mob))

        one_dot = Dot(plane.number_to_point(1))
        one_dot.set_color(YELLOW)
        for dot in z_dot, one_dot:
            dot.save_state()
            dot.scale(5)
            dot.set_fill(opacity=0)
            dot.set_stroke(width=1, opacity=0.5)
        to_fade_out = VGroup(
            plane, label, lines, z_dot, one_dot
        )

        self.play(
            ShowCreation(lines),
            FadeInFromDown(label),
            Restore(z_dot),
        )
        self.play(Restore(one_dot))
        angle = np.log(z).imag
        self.play(
            one_dot.move_to, z_dot,
            plane.apply_complex_function, lambda w: z * w,
            path_arc=angle,
            run_time=3
        )
        self.wait()
        self.play(
            FadeOut(to_fade_out),
            FadeIn(new_plane),
        )
        self.plane = new_plane


class DefineComplexNumbersPurelyAlgebraically(Scene):
    def construct(self):
        self.add_linus()
        self.add_title()
        self.show_example_number()
        self.show_multiplication()
        self.emphsize_result_has_same_form()

    def add_linus(self):
        linus = self.linus = Linus()
        linus.move_to(3 * LEFT)

    def add_title(self):
        title = self.title = Title(
            "No spatial reasoning, just symbols"
        )
        self.play(
            FadeInFromDown(title[:-1]),
            ShowCreation(title[-1]),
            self.linus.look_at, title
        )

    def show_example_number(self):
        linus = self.linus

        number = TexMobject("2.35", "+", "3.14", "i")
        number.next_to(self.title, DOWN, buff=1.5)
        number.shift(3 * RIGHT)
        real, imag = number[0], number[2]
        real_brace = Brace(real, UP)
        imag_brace = Brace(imag, DOWN)
        real_label = real_brace.get_text("Some real number")
        imag_label = imag_brace.get_text("Some other real number")
        VGroup(real, real_label).set_color(GREEN)
        VGroup(imag, imag_label).set_color(RED)

        i = number[-1]
        i_def = TexMobject("i", "^2", "=", "-1")
        i_def.next_to(
            self.title, DOWN,
            buff=MED_LARGE_BUFF,
            aligned_edge=LEFT,
        )
        i_def_rect = SurroundingRectangle(i_def, color=YELLOW, buff=MED_SMALL_BUFF)
        definition_label = TextMobject("Definition")
        definition_label.next_to(i_def_rect, DOWN)
        definition_label.match_color(i_def_rect)

        self.play(Write(number, run_time=1))
        self.play(
            GrowFromCenter(real_brace),
            LaggedStart(FadeIn, real_label),
            linus.change, "confused", number,
            run_time=1
        )
        self.wait()
        self.play(
            GrowFromCenter(imag_brace),
            LaggedStart(FadeIn, imag_label),
            run_time=1
        )
        self.play(Blink(linus))
        self.play(
            linus.change, "erm", i_def,
            ReplacementTransform(
                i.copy(), i_def[0],
                path_arc=-30 * DEGREES
            ),
            FadeIn(i_def_rect),
            FadeIn(definition_label),
        )
        self.play(Write(i_def[1:]))
        self.wait()
        self.play(Blink(linus))

        self.to_fade = VGroup(
            real_brace, real_label,
            imag_brace, imag_label,
        )
        self.number = number

    def show_multiplication(self):
        linus = self.linus
        to_fade = self.to_fade
        z1 = self.number

        z2 = TexMobject("4", "+", "5", "i")
        z2.match_style(z1)

        for z in z1, z2:
            lp, rp = z.parens = TexMobject("()")
            lp.next_to(z, LEFT, SMALL_BUFF)
            rp.next_to(z, RIGHT, SMALL_BUFF)
            z.real = z[0]
            z.imag = z[2:]
            for part in z.real, z.imag:
                part.targets = [part.copy(), part.copy()]

        z1.generate_target()
        product = VGroup(
            VGroup(z1.target, z1.parens),
            VGroup(z2, z2.parens),
        )
        product.arrange_submobjects(RIGHT, SMALL_BUFF)
        product.move_to(2 * RIGHT + 2 * UP)

        foil = VGroup(*map(TextMobject, [
            "First", "Outside", "Inside", "Last",
        ]))
        foil.arrange_submobjects(
            DOWN, buff=MED_SMALL_BUFF,
            aligned_edge=LEFT
        )
        foil.scale(1.25)
        for word in foil:
            word[0].set_color(BLUE)
        foil.move_to(product).to_edge(DOWN, LARGE_BUFF)

        def get_cdot():
            return TexMobject("\\cdot")

        def get_lp():
            return TexMobject("(")

        def get_rp():
            return TexMobject(")")

        def get_plus():
            return TexMobject("+")

        expansion = VGroup(
            z1.real.targets[0], get_cdot(), z2.real.targets[0], get_plus(),
            z1.real.targets[1], get_cdot(), z2.imag.targets[0], get_plus(),
            z1.imag.targets[0], get_cdot(), z2.real.targets[1], get_plus(),
            z1.imag.targets[1], get_cdot(), z2.imag.targets[1],
        )
        expansion.arrange_submobjects(RIGHT, buff=0.15)
        expansion.next_to(product, DOWN, buff=LARGE_BUFF)
        expansion_parts = VGroup(*[
            expansion[4 * i: 4 * i + 3]
            for i in range(4)
        ])
        expansion_part_braces = VGroup(*[
            Brace(part, DOWN) for part in expansion_parts
        ])
        for word, brace in zip(foil, expansion_part_braces):
            word.next_to(brace, DOWN)

        final_prouct = VGroup(
            get_lp(),
            z1[0].copy(), get_cdot(), z2[0].copy(),
            TexMobject("-"),
            z1[2].copy(), get_cdot(), z2[2].copy(),
            get_rp(), get_plus(),
            get_lp(),
            z1[0].copy(), get_cdot(), z2[2].copy(),
            get_plus(),
            z1[2].copy(), get_cdot(), z2[0].copy(),
            get_rp(), TexMobject("i")
        )
        final_prouct.arrange_submobjects(RIGHT, buff=0.15)
        final_prouct.next_to(expansion, DOWN, buff=2)
        final_arrows = VGroup()
        for i, brace in zip([1, 11, 15, 5], expansion_part_braces):
            target = final_prouct[i:i + 3]
            if i == 5:
                arrow = Line(
                    brace.get_bottom() + SMALL_BUFF * DOWN,
                    target.get_top() + MED_SMALL_BUFF * UP,
                )
                arrow.points[1] = arrow.points[0] + DOWN
                arrow.points[2] = arrow.points[3] + UP
                tip = RegularPolygon(3, start_angle=-100 * DEGREES)
                tip.set_height(0.2)
                tip.set_stroke(width=0)
                tip.set_fill(WHITE, opacity=1)
                tip.move_to(arrow.get_end())
                arrow.add(tip)
            else:
                arrow = Arrow(
                    brace.get_bottom(),
                    target.get_top(),
                    use_rectangular_stem=False,
                )
            final_arrows.add(arrow)
        final_arrows.set_stroke(BLACK, width=6, background=True)

        # Move example number into product
        self.play(
            FadeOut(to_fade),
            MoveToTarget(z1),
            FadeIn(z1.parens),
            FadeInFromDown(z2),
            FadeIn(z2.parens),
            linus.change, "happy", product,
        )
        self.wait()

        # Show distribution
        pairs = list(it.product([z1.real, z1.imag], [z2.real, z2.imag]))
        for i in range(4):
            left, right = pair = VGroup(*pairs[i])
            word = foil[i]
            dot = expansion[4 * i + 1]
            plus = expansion[4 * i + 3] if i < 3 else VMobject()
            brace = expansion_part_braces[i]

            self.play(pair.shift, 0.5 * DOWN)
            self.play(
                FadeIn(dot),
                GrowFromCenter(brace),
                FadeInFromDown(word),
                linus.move_to, 4 * LEFT + DOWN,
                *[
                    ReplacementTransform(
                        part.copy(),
                        part.targets.pop(0)
                    )
                    for part in pair
                ]
            )
            self.play(
                pair.shift, 0.5 * UP,
                FadeIn(plus)
            )
        self.play(Blink(linus))

        self.play(
            FadeOut(foil),
            FadeInFromDown(final_prouct),
            linus.look_at, final_prouct,
        )
        self.play(
            LaggedStart(ShowCreation, final_arrows),
            run_time=3,
        )
        self.play(linus.change, "confused")
        self.wait()

        self.final_prouct = final_prouct

    def emphsize_result_has_same_form(self):
        final_product = self.final_prouct
        real = final_product[1:1 + 7]
        imag = final_product[11:11 + 7]

        real_brace = Brace(real, DOWN)
        real_label = real_brace.get_text("Some real number")
        real_label.set_color(GREEN)
        imag_brace = Brace(imag, DOWN)
        imag_label = imag_brace.get_text(
            "Some other \\\\ real number"
        )
        imag_label.set_color(RED)
        braces = VGroup(real_brace, imag_brace)
        labels = VGroup(real_label, imag_label)
        self.play(
            LaggedStart(GrowFromCenter, braces),
            LaggedStart(Write, labels),
        )
        self.wait()


class TextbookQuaternionDefinition(TeacherStudentsScene):
    CONFIG = {
        "random_seed": 1,
    }

    def construct(self):
        equation = TexMobject(
            """
            (w_1 + x_1 i + y_1 j + z_1 k)
            (w_2 + x_2 i + y_2 j + z_2 k) =
            &(w_1 w_2 - x_1 x_2 - y_1 y_2 - z_1 z_2) \\, +\\\\
            &(w_1 x_2 + x_1 w_2 + y_1 z_2 - z_1 y_2)i \\, +\\\\
            &(w_1 y_2 + y_1 w_2 + z_1 x_2 - x_1 z_2)j \\, +\\\\
            &(w_1 z_2 + z_1 w_2 + x_1 y_2 - y_1 x_2)k \\\\
            """,
            tex_to_color_map={
                "w_1": YELLOW,
                "w_2": YELLOW,
                "x_1": GREEN,
                "x_2": GREEN,
                "y_1": RED,
                "y_2": RED,
                "z_1": BLUE,
                "z_2": BLUE,
            }
        )
        equation.set_width(FRAME_WIDTH - 1)
        equation.to_edge(UP)

        defining_products = VGroup(*[
            TexMobject(
                tex,
                tex_to_color_map={
                    "i": GREEN,
                    "j": RED,
                    "k": BLUE,
                }
            )
            for tex in [
                "i^2 = j^2 = k^2 = -1",
                "ij = -ji = k",
                "ki = -ik = j",
                "jk = -kj = i",
            ]
        ])
        defining_products.arrange_submobjects(DOWN)
        defining_products.next_to(self.students, UP, LARGE_BUFF)
        def_rect = SurroundingRectangle(defining_products)

        self.play(
            LaggedStart(FadeInFromDown, defining_products),
            self.get_student_changes(*3 * ["confused"]),
            self.teacher.change, "raise_right_hand",
        )
        self.play(ShowCreation(def_rect))
        self.play(
            Write(equation, run_time=4, lag_ratio=0.2),
            self.get_student_changes(
                "horrified", "pleading", "sick",
                equation
            ),
            self.teacher.change, "erm", equation,
        )
        self.blink()
        self.look_at(equation.get_corner(UL))
        self.blink()
        self.look_at(equation.get_corner(UR))
        self.wait(2)


class ProblemsWhereComplexNumbersArise(Scene):
    def construct(self):
        text = "Problems where complex numbers are surprisingly useful"
        title = TextMobject(*text.split(" "))
        title.to_edge(UP)
        title.set_color(BLUE)
        underline = Line(LEFT, RIGHT)
        underline.set_width(title.get_width() + 0.5)
        underline.next_to(title, DOWN)

        problems = VGroup(
            TextMobject(
                "Integer solutions to\\\\ $a^2 + b^2 = c^2$",
                alignment=""
            ),
            TextMobject(
                "Understanding\\\\",
                "$1 - \\frac{1}{3} + \\frac{1}{5} - \\frac{1}{7} + \\cdots" +
                "=\\frac{\\pi}{4}$",
                alignment="",
            ),
            TextMobject("Frequency analysis")
        )
        problems.arrange_submobjects(
            DOWN, buff=LARGE_BUFF, aligned_edge=LEFT
        )
        for problem in problems:
            problems.add(Dot().next_to(problem[0], LEFT))
        problems.next_to(underline, DOWN, buff=MED_LARGE_BUFF)
        problems.to_edge(LEFT)
        v_dots = TexMobject("\\vdots")
        v_dots.scale(2)
        v_dots.next_to(problems, DOWN, aligned_edge=LEFT)

        self.add(problems, v_dots)
        self.play(
            ShowCreation(underline),
            LaggedStart(FadeInFromDown, title, lag_ratio=0.5),
            run_time=3
        )
        self.wait()


class WalkThroughComplexMultiplication(ShowComplexMultiplicationExamples):
    CONFIG = {
        "z": complex(2, 3),
        "w": complex(1, -1),
        "z_color": YELLOW,
        "w_color": PINK,
        "product_color": RED,
    }

    def construct(self):
        self.add_planes(include_title=False)
        self.introduce_z_and_w()
        self.show_action_on_all_complex_numbers()

    def introduce_z_and_w(self):
        # Tolerating code repetition here in case I want
        # to specialize behavior for z or w...
        plane = self.plane
        origin = plane.number_to_point(0)

        z_point = plane.number_to_point(self.z)
        z_dot = Dot(z_point)
        z_line = Line(origin, z_point)
        z_label = VGroup(
            TexMobject("z="),
            DecimalNumber(self.z, num_decimal_places=0)
        )
        z_label.arrange_submobjects(
            RIGHT, buff=SMALL_BUFF,
        )
        z_label.next_to(z_dot, UP, buff=SMALL_BUFF)
        z_label.set_color(self.z_color)
        z_label.add_background_rectangle()
        VGroup(z_line, z_dot).set_color(self.z_color)

        w_point = plane.number_to_point(self.w)
        w_dot = Dot(w_point)
        w_line = Line(origin, w_point)
        w_label = VGroup(
            TexMobject("w="),
            DecimalNumber(self.w, num_decimal_places=0)
        )
        w_label.arrange_submobjects(RIGHT, buff=SMALL_BUFF)
        w_label.next_to(w_dot, DOWN, buff=SMALL_BUFF)
        w_label.set_color(self.w_color)
        w_label.add_background_rectangle()
        VGroup(w_line, w_dot).set_color(self.w_color)

        VGroup(
            z_label[1], w_label[1]
        ).shift(0.25 * SMALL_BUFF * DOWN)

        product = TexMobject("z", "\\cdot", "w")
        z_sym, w_sym = product[0], product[2]
        z_sym.set_color(self.z_color)
        w_sym.set_color(self.w_color)
        product.scale(2)
        product.to_corner(UL)
        product.add_background_rectangle()

        self.add(
            z_line, z_label,
            w_line, w_label,
        )
        self.play(LaggedStart(
            FadeInFromLarge, VGroup(z_dot, w_dot),
            lambda m: (m, 5),
            lag_ratio=0.8,
            run_time=1.5
        ))
        self.play(
            ReplacementTransform(z_label[1][0].copy(), z_sym)
        )
        self.add(product[:-1])
        self.play(
            ReplacementTransform(w_label[1][0].copy(), w_sym),
            FadeInAndShiftFromDirection(product[2], LEFT),
            FadeIn(product[0]),
        )
        self.wait()

        self.set_variables_as_attrs(
            product,
            z_point, w_point,
            z_dot, w_dot,
            z_line, w_line,
        )

    def show_action_on_all_complex_numbers(self):
        plane = self.plane
        plane.save_state()
        origin = plane.number_to_point(0)
        z = self.z
        angle = np.log(z).imag
        product_tex = self.product[1:]
        z_sym, cdot, w_sym = product_tex

        product = self.z * self.w
        product_point = plane.number_to_point(product)
        product_dot = Dot(product_point)
        product_line = Line(origin, product_point)
        for mob in product_line, product_dot:
            mob.set_color(self.product_color)

        rect = SurroundingRectangle(VGroup(z_sym, cdot))
        rect.set_fill(BLACK, opacity=1)
        func_words = TextMobject("Function on the plane")
        func_words.next_to(
            rect, DOWN,
            buff=MED_SMALL_BUFF,
            aligned_edge=LEFT,
        )
        func_words.set_color(self.z_color)

        sparkly_plane = VGroup()
        for line in plane.family_members_with_points():
            if self.camera.is_in_frame(line):
                for piece in line.get_pieces(10):
                    p1, p2 = piece.get_pieces(2)
                    p1.rotate(PI)
                    pair = VGroup(p1, p2)
                    pair.scale(0.3)
                    sparkly_plane.add(pair)
        sparkly_plane.sort_submobjects(
            lambda p: 0.1 * get_norm(p) + random.random()
        )
        sparkly_plane.set_color_by_gradient(YELLOW, RED, PINK, BLUE)
        sparkly_plane.set_stroke(width=4)

        pin = PushPin()
        pin.move_to(origin, DR)

        one_dot = Dot(plane.number_to_point(1))
        one_dot.set_fill(WHITE)
        one_dot.set_stroke(BLACK, 1)
        hand = Hand()
        hand.move_to(plane.number_to_point(1), LEFT)

        zero_eq = TexMobject("z \\cdot 0 = 0")
        one_eq = TexMobject("z \\cdot 1 = z")
        equations = VGroup(zero_eq, one_eq)
        equations.arrange_submobjects(DOWN)
        equations.scale(1.5)
        for eq in equations:
            eq.add_background_rectangle()
        equations.next_to(func_words, DOWN)
        equations.to_edge(LEFT)

        product_label = VGroup(
            TexMobject("z \\cdot w ="),
            DecimalNumber(product, num_decimal_places=0)
        )
        product_label.arrange_submobjects(RIGHT)
        product_label[0].shift(0.025 * DOWN)
        product_label.next_to(product_dot, UP, SMALL_BUFF)
        product_label.add_background_rectangle()

        big_rect = Rectangle(
            height=4,
            width=6,
            fill_color=BLACK,
            fill_opacity=0.9,
            stroke_width=0,
        )
        big_rect.to_corner(UL, buff=0)

        self.add(big_rect, product_tex, rect, z_sym, cdot)
        self.play(
            FadeIn(big_rect),
            ShowCreation(rect),
            Write(func_words),
            run_time=1
        )
        self.play(
            ReplacementTransform(
                self.w_line.copy(), product_line,
            ),
            ReplacementTransform(
                self.w_dot.copy(), product_dot,
            ),
            path_arc=angle,
            run_time=3
        )
        self.wait()
        self.play(FadeOut(VGroup(product_line, product_dot)))
        self.play(LaggedStart(
            ShowCreationThenDestruction, sparkly_plane,
            lag_ratio=0.5,
            run_time=2
        ))
        self.play(
            plane.apply_complex_function, lambda w: z * w,
            Transform(self.w_line, product_line),
            Transform(self.w_dot, product_dot),
            path_arc=angle,
            run_time=9,
            rate_func=lambda t: there_and_back_with_pause(t, 2 / 9)
        )
        self.wait()
        self.play(FadeInFrom(pin, UL))
        self.play(Write(zero_eq))
        self.play(
            FadeInFromLarge(one_dot),
            FadeInFrom(hand, UR)
        )
        self.play(Write(one_eq))
        self.wait()
        self.play(
            plane.apply_complex_function, lambda w: z * w,
            ReplacementTransform(self.w_line.copy(), product_line),
            ReplacementTransform(self.w_dot.copy(), product_dot),
            one_dot.move_to, self.z_point,
            hand.move_to, self.z_point, LEFT,
            path_arc=angle,
            run_time=4,
        )
        self.play(Write(product_label))


class ShowUnitCircleActions(ShowComplexMultiplicationExamples):
    CONFIG = {
        "random_seed": 0,
        "plane_config": {
            "secondary_line_ratio": 0,
        }
    }

    def construct(self):
        self.add_planes(include_title=False)
        self.show_unit_circle_actions()

    def show_unit_circle_actions(self):
        plane = self.plane
        origin = plane.number_to_point(0)
        one_point = plane.number_to_point(1)
        one_dot = Dot(one_point)
        one_dot.set_fill(WHITE)
        one_dot.set_stroke(BLACK, 1)
        plane.add(one_dot)

        pin = PushPin()
        pin.move_to(origin, DR)
        hand = Hand()
        update_hand = UpdateFromFunc(
            hand, lambda m: m.move_to(one_dot.get_center(), LEFT)
        )

        circle = Circle(
            color=YELLOW,
            radius=get_norm(one_point - origin)
        )

        self.add(circle)
        self.add(pin, one_dot)
        self.add_foreground_mobjects(hand)

        title = TextMobject(
            "Numbers on the unit circle",
            "$\\rightarrow$", "pure rotation."
        )
        title.set_width(FRAME_WIDTH - 1)
        title.to_edge(UP, buff=MED_SMALL_BUFF)
        title.add_background_rectangle(buff=SMALL_BUFF)
        self.add_foreground_mobjects(title)
        self.background_plane.coordinate_labels.submobjects.pop(-1)

        n_angles = 12
        angles = list(np.linspace(-PI, PI, n_angles + 2)[1:-1])
        random.shuffle(angles)

        for angle in angles:
            plane.save_state()
            temp_plane = plane.copy()

            z = np.exp(complex(0, angle))
            if angle is angles[0]:
                z_label = DecimalNumber(
                    z, num_decimal_places=2,
                )
                z_label.set_stroke(BLACK, width=11, background=True)
                z_label_rect = BackgroundRectangle(z_label)
                z_label_rect.set_fill(opacity=0)
            z_point = plane.number_to_point(z)
            z_arrow = Arrow(2.5 * z_point, z_point, buff=SMALL_BUFF)
            z_dot = Dot(z_point)
            z_label_start_center = z_label.get_center()
            z_label.next_to(
                z_arrow.get_start(),
                np.sign(z_arrow.get_start()[1]) * UP,
            )
            z_label_end_center = z_label.get_center()
            z_group = VGroup(z_arrow, z_dot, z_label)
            z_group.set_color(GREEN)
            z_group.add_to_back(z_label_rect)
            z_arrow.set_stroke(BLACK, 1)
            z_dot.set_stroke(BLACK, 1)

            if angle is angles[0]:
                self.play(
                    FadeInFromDown(z_label_rect),
                    FadeInFromDown(z_label),
                    GrowArrow(z_arrow),
                    FadeInFromLarge(z_dot),
                )
            else:
                alpha_tracker = ValueTracker(0)
                self.play(
                    ReplacementTransform(old_z_dot, z_dot),
                    ReplacementTransform(old_z_arrow, z_arrow),
                    UpdateFromFunc(
                        z_label_rect,
                        lambda m: m.replace(z_label)
                    ),
                    ChangeDecimalToValue(
                        z_label, z,
                        position_update_func=lambda m: m.move_to(
                            interpolate(
                                z_label_start_center,
                                z_label_end_center,
                                alpha_tracker.get_value()
                            )
                        )
                    ),
                    alpha_tracker.set_value, 1,
                    # hand.move_to, one_point, LEFT
                )
            old_z_dot = z_dot
            old_z_arrow = z_arrow
            VGroup(old_z_arrow, old_z_dot)
            self.play(
                Rotate(plane, angle, run_time=2),
                update_hand,
                Animation(z_group),
            )
            self.wait()
            self.add(temp_plane, z_group)
            self.play(
                FadeOut(plane),
                FadeOut(hand),
                FadeIn(temp_plane),
            )
            plane.restore()
            self.remove(temp_plane)
            self.add(plane, *z_group)


class IfYouNeedAWarmUp(TeacherStudentsScene):
    def construct(self):
        screen = self.screen
        screen.set_height(4)
        screen.to_corner(UL)
        self.add(screen)

        self.teacher_says(
            "If you need \\\\ a warm up",
            bubble_kwargs={"width": 3.5, "height": 3},
        )
        self.change_all_student_modes(
            "pondering", look_at_arg=screen,
        )
        self.wait(3)
        self.play(RemovePiCreatureBubble(self.teacher))
        self.wait(3)


class LinusThinksAboutStretching(Scene):
    def construct(self):
        linus = Linus()
        top_line = NumberLine(color=GREY)
        top_line.to_edge(UP)
        top_line.add_numbers()

        linus.move_to(3 * LEFT + DOWN)

        self.add(linus, top_line)

        scalars = [3, 0.5, 2]

        for scalar in scalars:
            lower_line = NumberLine(
                x_min=-14,
                x_max=14,
                color=BLUE
            )
            lower_line.next_to(top_line, DOWN, MED_LARGE_BUFF)
            lower_line.numbers = lower_line.get_number_mobjects()
            for number in lower_line.numbers:
                number.add_updater(lambda m: m.next_to(
                    lower_line.number_to_point(m.get_value()),
                    DOWN, MED_SMALL_BUFF,
                ))
            lower_line.save_state()
            lower_line.numbers.save_state()
            self.add(lower_line, *lower_line.numbers)

            words = TextMobject("Multiply by {}".format(scalar))
            words.next_to(lower_line.numbers, DOWN)

            self.play(
                ApplyMethod(
                    lower_line.stretch, scalar, 0,
                    run_time=2
                ),
                # LaggedStart(FadeIn, words, run_time=1),
                FadeInFromLarge(words, 1.0 / scalar),
                linus.look_at, top_line.number_to_point(scalar)
            )
            self.play(Blink(linus))
            self.play(
                FadeOut(lower_line),
                FadeOut(lower_line.numbers),
                FadeOut(words),
                FadeIn(lower_line.saved_state, remover=True),
                FadeIn(lower_line.numbers.saved_state, remover=True),
                linus.look_at, top_line.number_to_point(0)
            )
        self.play(linus.change, "confused", DOWN + RIGHT)
        self.wait(2)
        self.play(Blink(linus))
        self.wait(2)


class LinusReactions(Scene):
    def construct(self):
        linus = Linus()
        for mode in "confused", "sad", "erm", "angry", "pleading":
            self.play(linus.change, mode, 2 * RIGHT)
            self.wait()
            self.play(Blink(linus))
            self.wait()


class OneDegreeOfFreedomForRotation(Scene):
    def construct(self):
        circle = CheckeredCircle(radius=2, stroke_width=10)
        r_line = Line(circle.get_center(), circle.get_right())
        moving_r_line = r_line.copy()
        right_dot = Dot(color=WHITE)
        right_dot.move_to(circle.get_right())
        circle.add(moving_r_line, right_dot)

        def get_angle():
            return moving_r_line.get_angle() % TAU

        angle_label = Integer(0, unit="^\\circ")
        angle_label.scale(2)
        angle_label.add_updater(
            lambda m: m.set_value(get_angle() / DEGREES)
        )
        angle_label.add_updater(
            lambda m: m.next_to(circle, UP, MED_LARGE_BUFF)
        )

        def get_arc():
            return Arc(
                angle=get_angle(),
                radius=0.5,
                color=LIGHT_GREY,
            )

        arc = get_arc()
        arc.add_updater(lambda m: m.become(get_arc()))

        self.add(circle, r_line, angle_label, arc)
        angles = np.random.uniform(-TAU, TAU, 10)
        for angle in angles:
            self.play(Rotate(circle, angle, run_time=2))


class StereographicProjectionTitle(Scene):
    def construct(self):
        title = TextMobject("Stereographic projection")
        final_title = title.copy()
        final_title.set_width(10)
        final_title.to_edge(UP)

        title.rotate(-90 * DEGREES)
        title.next_to(RIGHT, RIGHT, SMALL_BUFF)
        title.apply_complex_function(np.exp)
        title.rotate(90 * DEGREES)
        title.set_height(6)
        title.to_edge(UP)

        self.play(Write(title))
        self.play(Transform(title, final_title, run_time=2))
        self.wait()


class IntroduceStereographicProjection(MovingCameraScene):
    CONFIG = {
        "n_sample_points": 16,
        "circle_config": {
            "n_pieces": 16,
            "radius": 2,
            "stroke_width": 7,
        },
        "example_angles": [
            30 * DEGREES,
            120 * DEGREES,
            240 * DEGREES,
            80 * DEGREES,
            -60 * DEGREES,
            135 * DEGREES,
        ]
    }

    def construct(self):
        self.setup_plane()
        self.draw_lines()
        self.describe_individual_points()
        self.remind_that_most_points_are_not_projected()

    def setup_plane(self):
        self.plane = self.get_plane()
        self.circle = self.get_circle()
        self.circle_shadow = self.get_circle_shadow()

        self.add(self.plane)
        self.add(self.circle_shadow)
        self.add(self.circle)

    def draw_lines(self):
        plane = self.plane
        circle = self.circle
        circle.save_state()
        circle.generate_target()
        self.project_mobject(circle.target)

        circle_points = self.get_sample_circle_points()
        dots = VGroup(*[Dot(p) for p in circle_points])
        dots.set_sheen(-0.2, DR)
        dots.set_stroke(DARK_GREY, 2, background=True)
        arrows = VGroup()
        for dot in dots:
            dot.scale(0.75)
            dot.generate_target()
            dot.target.move_to(
                self.project(dot.get_center())
            )
            arrow = Arrow(
                dot.get_center(),
                dot.target.get_center(),
            )
            arrows.add(arrow)
        neg_one_point = plane.number_to_point(-1)
        neg_one_dot = Dot(neg_one_point)
        neg_one_dot.set_fill(YELLOW)

        lines = self.get_lines()

        special_index = self.n_sample_points // 2 + 1
        line = lines[special_index]
        dot = dots[special_index]
        arrow = arrows[special_index]
        dot_target_outline = dot.target.copy()
        dot_target_outline.set_stroke(RED, 2)
        dot_target_outline.set_fill(opacity=0)
        dot_target_outline.scale(1.5)

        v_line = Line(UP, DOWN)
        v_line.set_height(FRAME_HEIGHT)
        v_line.set_stroke(RED, 5)

        self.play(LaggedStart(FadeInFromLarge, dots))
        self.play(FadeInFromLarge(neg_one_dot))
        self.add(lines, neg_one_dot, dots)
        self.play(LaggedStart(ShowCreation, lines))
        self.wait()
        self.play(
            lines.set_stroke, {"width": 0.5},
            line.set_stroke, {"width": 4},
        )
        self.play(ShowCreation(dot_target_outline))
        self.play(ShowCreationThenDestruction(v_line))
        self.play(MoveToTarget(dot))
        self.wait()
        self.play(
            lines.set_stroke, {"width": 1},
            FadeOut(dot_target_outline),
            MoveToTarget(circle),
            *map(MoveToTarget, dots),
            run_time=2,
        )
        self.wait()

        self.lines = lines
        self.dots = dots

    def describe_individual_points(self):
        plane = self.plane
        one_point, zero_point, i_point, neg_i_point, neg_one_point = [
            plane.number_to_point(n)
            for n in [1, 0, complex(0, 1), complex(0, -1), -1]
        ]
        i_pin = PushPin()
        i_pin.pin_to(i_point)
        neg_i_pin = PushPin()
        neg_i_pin.pin_to(neg_i_point)

        dot = Dot()
        dot.set_stroke(RED, 3)
        dot.set_fill(opacity=0)
        dot.scale(1.5)
        dot.move_to(one_point)

        arc1 = Arc(angle=TAU / 4, radius=2)
        arc2 = Arc(
            angle=85 * DEGREES, radius=2,
            start_angle=TAU / 4,
        )
        arc3 = Arc(
            angle=-85 * DEGREES, radius=2,
            start_angle=-TAU / 4,
        )
        VGroup(arc1, arc2, arc3).set_stroke(RED)

        frame = self.camera_frame
        frame_height_tracker = ValueTracker(frame.get_height())
        frame_height_growth = ContinualGrowValue(
            frame_height_tracker, rate=0.4
        )

        neg_one_tangent = VGroup(
            Line(ORIGIN, UP),
            Line(ORIGIN, DOWN),
        )
        neg_one_tangent.set_height(25)
        neg_one_tangent.set_stroke(YELLOW, 5)
        neg_one_tangent.move_to(neg_one_point)

        self.play(ShowCreation(dot))
        self.wait()
        self.play(dot.move_to, zero_point)
        self.wait()
        dot.move_to(i_point)
        self.play(ShowCreation(dot))
        self.play(FadeInFrom(i_pin, UL))
        self.wait()
        self.play(
            dot.move_to, neg_i_point,
            path_arc=-60 * DEGREES
        )
        self.play(FadeInFrom(neg_i_pin, UL))
        self.wait()
        self.play(
            dot.move_to, one_point,
            path_arc=-60 * DEGREES
        )
        frame.add_updater(
            lambda m: m.set_height(frame_height_tracker.get_value())
        )

        triplets = [
            (arc1, i_point, TAU / 4),
            (arc2, neg_one_point, TAU / 4),
            (arc3, neg_one_point, -TAU / 4),
        ]
        for arc, point, path_arc in triplets:
            self.play(
                ShowCreation(arc),
                dot.move_to, point, path_arc=path_arc,
                run_time=2
            )
            self.wait()
            self.play(
                ApplyFunction(self.project_mobject, arc, run_time=2)
            )
            self.wait()
            self.play(FadeOut(arc))
            self.wait()
            if arc is arc1:
                self.add(frame, frame_height_growth)
            elif arc is arc2:
                self.play(dot.move_to, neg_i_point)
        frame_height_growth.begin_wind_down()
        self.wait(2)
        self.play(*map(ShowCreation, neg_one_tangent))
        self.wait()
        self.play(FadeOut(neg_one_tangent))
        self.wait(2)
        frame.clear_updaters()
        self.play(
            frame.set_height, FRAME_HEIGHT,
            self.lines.set_stroke, {"width": 0.5},
            FadeOut(self.dots),
            FadeOut(dot),
            run_time=2,
        )

    def remind_that_most_points_are_not_projected(self):
        plane = self.plane
        circle = self.circle

        sample_values = [0, complex(1, 1), complex(-2, -1)]
        sample_points = [
            plane.number_to_point(value)
            for value in sample_values
        ]
        sample_dots = VGroup(*[Dot(p) for p in sample_points])
        sample_dots.set_fill(GREEN)

        self.play(
            FadeOut(self.lines),
            Restore(circle),
        )

        for value, dot in zip(sample_values, sample_dots):
            cross = Cross(dot)
            cross.scale(2)
            label = Integer(value)
            label.next_to(dot, UR, SMALL_BUFF)
            self.play(
                FadeInFromLarge(dot, 3),
                FadeInFromDown(label)
            )
            self.play(ShowCreation(cross))
            self.play(*map(FadeOut, [dot, cross, label]))
        self.wait()
        self.play(
            FadeIn(self.lines),
            MoveToTarget(circle, run_time=2),
        )
        self.wait()

    # Helpers
    def get_plane(self):
        plane = ComplexPlane(
            unit_size=2,
            color=GREY,
            secondary_color=DARK_GREY,
            x_radius=FRAME_WIDTH,
            y_radius=FRAME_HEIGHT,
            stroke_width=2,
        )
        plane.add_coordinates()
        return plane

    def get_circle(self):
        circle = CheckeredCircle(
            **self.circle_config
        )
        circle.set_stroke(width=7)
        return circle

    def get_circle_shadow(self):
        circle_shadow = CheckeredCircle(
            **self.circle_config
        )
        circle_shadow.set_stroke(opacity=0.65)
        return circle_shadow

    def get_sample_circle_points(self):
        plane = self.plane
        n = self.n_sample_points
        numbers = [
            np.exp(complex(0, TAU * x / n))
            for x in range(-(n // 2) + 1, n // 2)
        ]
        return [
            plane.number_to_point(number)
            for number in numbers
        ]

    def get_lines(self):
        plane = self.plane
        neg_one_point = plane.number_to_point(-1)
        circle_points = self.get_sample_circle_points()

        lines = VGroup(*[
            Line(neg_one_point, point)
            for point in circle_points
        ])
        for line in lines:
            line.scale(
                20 / line.get_length(),
                about_point=neg_one_point
            )
            line.set_stroke(YELLOW, 1)
        return lines

    def project(self, point):
        return stereo_project_point(point, axis=0, r=2)

    def project_mobject(self, mobject):
        return stereo_project(mobject, axis=0, r=2, outer_r=6)


class IntroduceStereographicProjectionLinusView(IntroduceStereographicProjection):
    def construct(self):
        self.describe_individual_points()
        self.point_at_infinity()
        self.show_90_degree_rotation()
        self.talk_through_90_degree_rotation()
        self.show_four_rotations()
        self.show_example_angles()

    def describe_individual_points(self):
        plane = self.plane = self.get_plane()
        circle = self.circle = self.get_circle()
        linus = self.linus =self.get_linus()

        angles = np.arange(-135, 180, 45) * DEGREES
        sample_numbers = [
            np.exp(complex(0, angle))
            for angle in angles
        ]
        sample_points = [
            plane.number_to_point(number)
            for number in sample_numbers
        ]
        projected_sample_points = [
            self.project(point)
            for point in sample_points
        ]
        dots = VGroup(*[Dot() for x in range(8)])
        dots.set_fill(WHITE)
        dots.set_stroke(BLACK, 1)

        def generate_dot_updater(circle_piece):
            return lambda d: d.move_to(circle_piece.points[0])

        for dot, piece in zip(dots, circle[::(len(circle) // 8)]):
            dot.add_updater(generate_dot_updater(piece))

        stot = "\\frac{\\sqrt{2}}{2}"
        labels_tex = [
            "\\left(-{}-{}i\\right)".format(stot, stot),
            "-i",
            "\\left({}-{}i\\right)".format(stot, stot),
            "1",
            "\\left({}+{}i\\right)".format(stot, stot),
            "i",
            "\\left(-{}+{}i\\right)".format(stot, stot),
        ]
        labels = VGroup(*[TexMobject(tex) for tex in labels_tex])
        vects = it.cycle([RIGHT, RIGHT])
        arrows = VGroup()
        for label, point, vect in zip(labels, projected_sample_points, vects):
            arrow = Arrow(vect, ORIGIN)
            arrow.next_to(point, vect, 2 * SMALL_BUFF)
            arrows.add(arrow)
            label.set_stroke(width=0, background=True)
            if stot in label.get_tex_string():
                label.set_height(0.8)
            else:
                label.set_height(0.5)
            label.next_to(arrow, vect, SMALL_BUFF)

        frame = self.camera_frame
        frame.set_height(12)

        self.add(linus)
        self.add(circle, *dots)
        self.play(
            ApplyFunction(self.project_mobject, circle),
            run_time=2
        )
        self.play(linus.change, "confused")
        self.wait()
        for i in [1, 0]:
            self.play(
                LaggedStart(GrowArrow, arrows[i::2]),
                LaggedStart(Write, labels[i::2])
            )
            self.play(Blink(linus))

        self.dots = dots

    def point_at_infinity(self):
        circle = self.circle
        linus = self.linus

        label = TextMobject(
            "$-1$ is \\\\ at $\\pm \\infty$"
        )
        label.scale(2)
        label.next_to(circle, LEFT, buff=1.25)
        arrows = VGroup(*[
            Vector(3 * v + 0.0 * RIGHT).next_to(label, v, buff=MED_LARGE_BUFF)
            for v in [UP, DOWN]
        ])
        arrows.set_color(YELLOW)

        self.play(
            Write(label),
            linus.change, "awe", label,
            *map(GrowArrow, arrows)
        )

        self.neg_one_label = VGroup(label, arrows)

    def show_90_degree_rotation(self):
        angle_tracker = ValueTracker(0)
        circle = self.circle
        linus = self.linus
        hand = Hand()
        hand.flip()
        one_dot = self.dots[0]
        hand.add_updater(
            lambda h: h.move_to(one_dot.get_center(), RIGHT)
        )

        def update_circle(circle):
            angle = angle_tracker.get_value()
            new_circle = self.get_circle()
            new_circle.rotate(angle)
            self.project_mobject(new_circle)
            circle.become(new_circle)

        circle.add_updater(update_circle)

        self.play(
            FadeIn(hand),
            one_dot.set_fill, RED,
        )
        for angle in 90 * DEGREES, 0:
            self.play(
                ApplyMethod(
                    angle_tracker.set_value, angle,
                    run_time=3,
                ),
                linus.change, "confused", hand
            )
            self.wait()
            self.play(Blink(linus))

        self.hand = hand
        self.angle_tracker = angle_tracker

    def talk_through_90_degree_rotation(self):
        linus = self.linus
        dots = self.dots
        one_dot = dots[0]
        i_dot = dots[2]
        neg_i_dot = dots[-2]

        kwargs1 = {
            "use_rectangular_stem": False,
            "path_arc": -90 * DEGREES,
            "buff": SMALL_BUFF,
        }
        kwargs2 = dict(kwargs1)
        kwargs2["path_arc"] = -40 * DEGREES
        arrows = VGroup(
            Arrow(one_dot, i_dot, **kwargs1),
            Arrow(i_dot, 6 * UP + LEFT, **kwargs2),
            Arrow(6 * DOWN + LEFT, neg_i_dot, **kwargs2),
            Arrow(neg_i_dot, one_dot, **kwargs1)
        )
        arrows.set_stroke(WHITE, 3)
        one_to_i, i_to_neg_1, neg_one_to_neg_i, neg_i_to_one = arrows

        for arrow in arrows:
            self.play(
                ShowCreation(arrow),
                linus.look_at, arrow
            )
            self.wait(2)

        self.arrows = arrows

    def show_four_rotations(self):
        angle_tracker = self.angle_tracker
        linus = self.linus
        hand = self.hand
        linus.add_updater(lambda l: l.look_at(hand))
        linus.add_updater(lambda l: l.eyes.next_to(l.body, UP, 0))

        for angle in np.arange(TAU / 4, 5 * TAU / 4, TAU / 4):
            self.play(
                ApplyMethod(
                    angle_tracker.set_value, angle,
                    run_time=3,
                ),
            )
            self.wait()
        self.play(FadeOut(self.arrows))

    def show_example_angles(self):
        angle_tracker = self.angle_tracker
        angle_tracker.set_value(0)

        for angle in self.example_angles:
            self.play(
                ApplyMethod(
                    angle_tracker.set_value, angle,
                    run_time=2,
                ),
            )
            self.wait()

    #
    def get_linus(self):
        linus = Linus()
        linus.move_to(3 * RIGHT)
        linus.to_edge(DOWN)
        linus.look_at(ORIGIN)
        return linus


class ShowRotationUnderStereographicProjection(IntroduceStereographicProjection):
    def construct(self):
        self.setup_plane()
        self.apply_projection()
        self.show_90_degree_rotation()
        self.talk_through_90_degree_rotation()
        self.show_four_rotations()
        self.show_example_angles()

    def apply_projection(self):
        plane = self.plane
        circle = self.circle
        neg_one_point = plane.number_to_point(-1)
        neg_one_dot = Dot(neg_one_point)
        neg_one_dot.set_fill(YELLOW)

        lines = self.get_lines()

        def generate_dot_updater(circle_piece):
            return lambda d: d.move_to(circle_piece.points[0])

        for circ, color in [(self.circle_shadow, RED), (self.circle, WHITE)]:
            for piece in circ[::(len(circ) // 8)]:
                dot = Dot(color=color)
                dot.set_fill(opacity=circ.get_stroke_opacity())
                dot.add_updater(generate_dot_updater(piece))
                self.add(dot)

        self.add(lines, neg_one_dot)
        self.play(*map(ShowCreation, lines))
        self.play(
            ApplyFunction(self.project_mobject, circle),
            lines.set_stroke, {"width": 0.5},
            self.camera_frame.set_height, 12,
            run_time=2
        )
        self.wait()

    def show_90_degree_rotation(self):
        circle = self.circle
        circle_shadow = self.circle_shadow

        def get_rotated_one_point():
            return circle_shadow[0].points[0]

        def get_angle():
            return angle_of_vector(get_rotated_one_point())

        self.get_angle = get_angle

        one_dot = Dot(color=RED)
        one_dot.add_updater(
            lambda m: m.move_to(get_rotated_one_point())
        )
        hand = Hand()
        hand.move_to(one_dot.get_center(), LEFT)

        def update_circle(circle):
            new_circle = self.get_circle()
            new_circle.rotate(get_angle())
            self.project_mobject(new_circle)
            circle.become(new_circle)

        circle.add_updater(update_circle)

        self.add(one_dot, hand)
        hand.add_updater(
            lambda h: h.move_to(one_dot.get_center(), LEFT)
        )
        self.play(
            FadeInFrom(hand, RIGHT),
            FadeInFromLarge(one_dot, 3),
        )
        for angle in 90 * DEGREES, -90 * DEGREES:
            self.play(
                Rotate(circle_shadow, angle, run_time=3),
            )
            self.wait(2)

    def talk_through_90_degree_rotation(self):
        plane = self.plane
        points = [
            plane.number_to_point(z)
            for z in [1, complex(0, 1), -1, complex(0, -1)]
        ]
        arrows = VGroup()
        for p1, p2 in adjacent_pairs(points):
            arrow = Arrow(
                p1, p2, path_arc=180 * DEGREES,
                use_rectangular_stem=False,
            )
            arrow.set_stroke(LIGHT_GREY, width=3)
            arrow.tip.set_fill(LIGHT_GREY)
            arrows.add(arrow)

        for arrow in arrows:
            self.play(ShowCreation(arrow))
            self.wait(2)

        self.arrows = arrows

    def show_four_rotations(self):
        circle_shadow = self.circle_shadow
        for x in range(4):
            self.play(
                Rotate(circle_shadow, TAU / 4, run_time=3)
            )
            self.wait()
        self.play(FadeOut(self.arrows))

    def show_example_angles(self):
        circle_shadow = self.circle_shadow
        angle_label = Integer(0, unit="^\\circ")
        angle_label.scale(1.5)
        angle_label.next_to(
            circle_shadow.get_top(), UR,
        )

        self.play(FadeInFromDown(angle_label))
        self.add(angle_label)
        for angle in self.example_angles:
            d_angle = angle - self.get_angle()
            self.play(
                Rotate(circle_shadow, d_angle),
                ChangingDecimal(
                    angle_label,
                    lambda a: (self.get_angle() % TAU) / DEGREES
                ),
                run_time=2
            )
            self.wait()
