from manimlib.imports import *


def q_mult(q1, q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
    z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
    return np.array([w, x, y, z])


def stereo_project_point(point, axis=0, r=1, max_norm=10000):
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


class Felix(PiCreature):
    CONFIG = {
        "color": GREEN_D
    }


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
        "height": 0.5,
        "sheen": 0.2,
        "fill_color": ORANGE,
    }

    def __init__(self, **kwargs):
        SVGMobject.__init__(self, **kwargs)
        # self.rotate(30 * DEGREES)
        self.add(VectorizedPoint().next_to(self, UP, buff=0.17))


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


class StereoProjectedSphere(Sphere):
    CONFIG = {
        "stereo_project_config": {
            "axis": 2,
        },
        "max_r": 32,
        "max_width": FRAME_WIDTH,
        "max_height": FRAME_WIDTH,
        "max_depth": FRAME_WIDTH,
        "radius": 1,
    }

    def __init__(self, rotation_matrix=None, **kwargs):
        digest_config(self, kwargs)
        if rotation_matrix is None:
            rotation_matrix = np.identity(3)
        self.rotation_matrix = rotation_matrix

        self.stereo_project_config["r"] = self.radius
        ParametricSurface.__init__(
            self, self.post_projection_func, **kwargs
        )
        self.submobjects.sort(
            key=lambda m: -m.get_width()
        )
        self.fade_far_out_submobjects()

    def post_projection_func(self, u, v):
        point = self.radius * Sphere.func(self, u, v)
        rot_point = np.dot(point, self.rotation_matrix.T)
        result = stereo_project_point(
            rot_point, **self.stereo_project_config
        )
        epsilon = 1e-4
        if np.any(np.abs(result) == np.inf) or np.any(np.isnan(result)):
            return self.func(u + epsilon, v)
        return result

    def fade_far_out_submobjects(self, **kwargs):
        max_r = kwargs.get("max_r", self.max_r)
        max_width = kwargs.get("max_width", self.max_width)
        max_height = kwargs.get("max_height", self.max_height)
        max_depth = kwargs.get("max_depth", self.max_depth)
        for submob in self.submobjects:
            violations = [
                np.any(np.apply_along_axis(get_norm, 1, submob.get_anchors()) > max_r),
                submob.get_width() > max_width,
                submob.get_height() > max_height,
                submob.get_depth() > max_depth
            ]
            if any(violations):
                # self.remove(submob)
                submob.fade(1)
        return self


class StereoProjectedSphereFromHypersphere(StereoProjectedSphere):
    CONFIG = {
        "stereo_project_config": {
            "axis": 0,
        },
        "radius": 2,
        "multiply_from_right": False,
    }

    def __init__(self, quaternion=None, null_axis=0, **kwargs):
        if quaternion is None:
            quaternion = np.array([1, 0, 0, 0])
        self.quaternion = quaternion
        self.null_axis = null_axis
        ParametricSurface.__init__(self, self.q_mult_projection_func, **kwargs)
        self.fade_far_out_submobjects()

    def q_mult_projection_func(self, u, v):
        point = list(Sphere.func(self, u, v))
        point.insert(self.null_axis, 0)
        if self.multiply_from_right:
            post_q_mult = q_mult(point, self.quaternion)
        else:
            post_q_mult = q_mult(self.quaternion, point)
        projected = list(self.radius * stereo_project_point(
            post_q_mult, **self.stereo_project_config
        ))
        if np.any(np.abs(projected) == np.inf):
            return self.func(u + 0.001, v)
        ignored_axis = self.stereo_project_config["axis"]
        projected.pop(ignored_axis)
        return np.array(projected)


class StereoProjectedCircleFromHypersphere(CheckeredCircle):
    CONFIG = {
        "n_pieces": 48,
        "radius": 2,
        "max_length": 3 * FRAME_WIDTH,
        "max_r": 50,
        "basis_vectors": [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
        ],
        "multiply_from_right": False,
    }

    def __init__(self, quaternion=None, **kwargs):
        CheckeredCircle.__init__(self, **kwargs)
        if quaternion is None:
            quaternion = [1, 0, 0, 0]
        self.quaternion = quaternion
        self.pre_positioning_matrix = self.get_pre_positioning_matrix()
        self.apply_function(self.projection)
        self.remove_large_pieces()
        self.set_shade_in_3d(True)

    def get_pre_positioning_matrix(self):
        v1, v2 = [np.array(v) for v in self.basis_vectors]
        v1 = normalize(v1)
        v2 = v2 - np.dot(v1, v2) * v1
        v2 = normalize(v2)
        return np.array([v1, v2]).T

    def projection(self, point):
        q1 = self.quaternion
        q2 = np.dot(self.pre_positioning_matrix, point[:2]).flatten()
        if self.multiply_from_right:
            new_q = q_mult(q2, q1)
        else:
            new_q = q_mult(q1, q2)
        projected = stereo_project_point(
            new_q, axis=0, r=self.radius,
        )
        if np.any(projected == np.inf) or np.any(np.isnan(projected)):
            epsilon = 1e-6
            return self.projection(rotate_vector(point, epsilon))
        return projected[1:]

    def remove_large_pieces(self):
        for piece in self:
            length = get_norm(piece.points[0] - piece.points[-1])
            violations = [
                length > self.max_length,
                get_norm(piece.get_center()) > self.max_r,
            ]
            if any(violations):
                piece.fade(1)


class QuaternionTracker(ValueTracker):
    CONFIG = {
        "force_unit": True,
        "dim": 4,
    }

    def __init__(self, four_vector=None, **kwargs):
        Mobject.__init__(self, **kwargs)
        if four_vector is None:
            four_vector = np.array([1, 0, 0, 0])
        self.set_value(four_vector)
        if self.force_unit:
            self.add_updater(lambda q: q.normalize())

    def set_value(self, vector):
        self.points = np.array(vector).reshape((1, 4))
        return self

    def get_value(self):
        return self.points[0]

    def normalize(self):
        self.set_value(normalize(
            self.get_value(),
            fall_back=np.array([1, 0, 0, 0])
        ))
        return self


class RubiksCube(VGroup):
    CONFIG = {
        "colors": [
            "#FFD500",  # Yellow
            "#C41E3A",  # Orange
            "#009E60",  # Green
            "#FF5800",  # Red
            "#0051BA",  # Blue
            "#FFFFFF"   # White
        ],
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        vectors = [OUT, RIGHT, UP, LEFT, DOWN, IN]
        faces = [
            self.create_face(color, vector)
            for color, vector in zip(self.colors, vectors)
        ]
        VGroup.__init__(self, *it.chain(*faces), **kwargs)
        self.set_shade_in_3d(True)

    def create_face(self, color, vector):
        squares = VGroup(*[
            self.create_square(color)
            for x in range(9)
        ])
        squares.arrange_in_grid(
            3, 3,
            buff=0
        )
        squares.set_width(2)
        squares.move_to(OUT, OUT)
        squares.apply_matrix(z_to_vector(vector))
        return squares

    def create_square(self, color):
        square = Square(
            stroke_width=3,
            stroke_color=BLACK,
            fill_color=color,
            fill_opacity=1,
            side_length=1,
        )
        square.flip()
        return square
        # back = square.copy()
        # back.set_fill(BLACK, 0.85)
        # back.set_stroke(width=0)
        # back.shift(0.5 * IN)
        # return VGroup(square, back)

    def get_face(self, vect):
        self.sort(lambda p: np.dot(p, vect))
        return self[-(12 + 9):]


# Abstract scenes


class ManyNumberSystems(Scene):
    def construct(self):
        # Too much dumb manually positioning in here...
        title = Title("Number systems")
        name_location_color_example_tuples = [
            ("Reals", [-4, 2, 0], YELLOW, "1.414"),
            ("Complex numbers", [4, 0, 0], BLUE, "2 + i"),
            ("Quaternions", [0, 2, 0], PINK, "2 + 7i + 1j + 8k"),
            ("Rationals", [3, -2, 0], RED, "1 \\over 3"),
            ("p-adic numbers", [-2, -2, 0], GREEN, "\\overline{142857}2"),
            ("Octonions", [-3, 0, 0], LIGHT_GREY, "3e_1 - 2.3e_2 + \\dots + 1.6e_8"),
        ]
        systems = VGroup()
        for name, location, color, ex in name_location_color_example_tuples:
            system = TextMobject(name)
            system.set_color(color)
            system.move_to(location)
            example = TexMobject(ex)
            example.next_to(system, DOWN)
            system.add(example)
            systems.add(system)
        R_label, C_label, H_label = systems[:3]

        number_line = NumberLine(x_min=-3, x_max=3)
        number_line.add_numbers()
        number_line.shift(0.25 * FRAME_WIDTH * LEFT)
        number_line.shift(0.5 * DOWN)
        R_example_dot = Dot(number_line.number_to_point(1.414))
        plane = ComplexPlane(x_radius=3.5, y_radius=2.5)
        plane.add_coordinates()
        plane.shift(0.25 * FRAME_WIDTH * RIGHT)
        plane.shift(0.5 * DOWN)
        C_example_dot = Dot(plane.coords_to_point(2, 1))

        self.add(title)
        self.play(FadeInFromLarge(H_label))
        self.play(LaggedStartMap(
            FadeInFromLarge, VGroup(*it.chain(systems[:2], systems[3:])),
            lambda m: (m, 4)
        ))
        self.wait()
        self.add(number_line, plane, systems)
        self.play(
            R_label.move_to, 0.25 * FRAME_WIDTH * LEFT + 2 * UP,
            C_label.move_to, 0.25 * FRAME_WIDTH * RIGHT + 2 * UP,
            H_label.move_to, 0.75 * FRAME_WIDTH * RIGHT + 2 * UP,
            FadeOutAndShift(systems[3:], 2 * DOWN),
            Write(number_line),
            Write(plane),
            GrowFromCenter(R_example_dot),
            R_label[-1].next_to, R_example_dot, UP,
            GrowFromCenter(C_example_dot),
            C_label[-1].next_to, C_example_dot, UR, SMALL_BUFF,
            C_label[-1].shift, 0.4 * LEFT,
        )
        number_line.add(R_example_dot)
        plane.add(C_example_dot)
        self.wait(2)
        self.play(LaggedStartMap(
            ApplyMethod,
            VGroup(
                H_label,
                VGroup(plane, C_label),
                VGroup(number_line, R_label),
            ),
            lambda m: (m.shift, 0.5 * FRAME_WIDTH * LEFT),
            lag_ratio=0.8,
        ))
        randy = Randolph(height=1.5)
        randy.next_to(plane, RIGHT)
        randy.to_edge(DOWN)
        self.play(
            randy.change, "maybe", H_label,
            VFadeIn(randy),
        )
        self.play(Blink(randy))
        self.play(randy.change, "confused", H_label.get_top())
        self.wait()


class RotationsIn3d(SpecialThreeDScene):
    def construct(self):
        self.set_camera_orientation(**self.get_default_camera_position())
        self.begin_ambient_camera_rotation(rate=0.02)
        sphere = self.get_sphere()
        vectors = VGroup(*[
            Vector(u * v, color=color).next_to(sphere, u * v, buff=0)
            for v, color in zip(
                [RIGHT, UP, OUT],
                [GREEN, RED, BLUE],
            )
            for u in [-1, 1]
        ])
        vectors.set_shade_in_3d(True)
        sphere.add(vectors)

        self.add(self.get_axes())
        self.add(sphere)
        angle_axis_pairs = [
            (90 * DEGREES, RIGHT),
            (120 * DEGREES, UR),
            (-45 * DEGREES, OUT),
            (60 * DEGREES, IN + DOWN),
            (90 * DEGREES, UP),
            (30 * DEGREES, UP + OUT + RIGHT),
        ]
        for angle, axis in angle_axis_pairs:
            self.play(Rotate(
                sphere, angle,
                axis=axis,
                run_time=2,
            ))
            self.wait()


class IntroduceHamilton(Scene):
    def construct(self):
        hamilton = ImageMobject("Hamilton", height=6)
        hamilton.to_corner(UL)
        shamrock = SVGMobject(file_name="shamrock")
        shamrock.set_height(1)
        shamrock.set_color("#009a49")
        shamrock.set_fill(opacity=0.25)
        shamrock.next_to(hamilton.get_corner(UL), DR)
        shamrock.align_to(hamilton, UP)
        hamilton_name = TextMobject(
            "William Rowan Hamilton"
        )
        hamilton_name.match_width(hamilton)
        hamilton_name.next_to(hamilton, DOWN)

        quote = TextMobject(
            """\\huge ...Every morning in the early part of the above-cited
            month, on my coming down to breakfast, your (then)
            little brother William Edwin, and yourself, used to
            ask me,""",
            "``Well, Papa, can you multiply triplets''?",
            """Whereto I was always obliged to reply, with a sad
            shake of the head: ``No, I can only add and subtract
            them.''...""",
            alignment=""
        )
        quote.set_color_by_tex("Papa", YELLOW)
        quote = VGroup(*it.chain(*quote))
        quote.set_width(FRAME_WIDTH - hamilton.get_width() - 2)
        quote.to_edge(RIGHT)
        quote_rect = SurroundingRectangle(quote, buff=MED_SMALL_BUFF)
        quote_rect.set_stroke(WHITE, 2)
        quote_rect.stretch(1.1, 1)
        quote_label = TextMobject(
            "August 5, 1865 Letter\\\\from Hamilton to his son"
        )
        quote_label.next_to(quote_rect, UP)
        quote_label.set_color(BLUE)
        VGroup(quote, quote_rect, quote_label).to_edge(UP)

        plaque = ImageMobject("BroomBridgePlaque")
        plaque.set_width(FRAME_WIDTH / 2)
        plaque.to_edge(LEFT)
        plaque.shift(UP)
        equation = TexMobject(
            "i^2 = j^2 = k^2 = ijk = -1",
            tex_to_color_map={"i": GREEN, "j": RED, "k": BLUE}
        )
        equation_rect = Rectangle(width=3.25, height=0.7)
        equation_rect.move_to(3.15 * LEFT + 0.25 * DOWN)
        equation_rect.set_color(WHITE)
        equation_arrow = Vector(DOWN)
        equation_arrow.match_color(equation_rect)
        equation_arrow.next_to(equation_rect, DOWN)
        equation.next_to(equation_arrow, DOWN)

        self.play(
            FadeInFromDown(hamilton),
            Write(hamilton_name),
        )
        self.play(DrawBorderThenFill(shamrock))
        self.wait()

        self.play(
            LaggedStartMap(
                FadeIn, quote,
                lag_ratio=0.2,
                run_time=4
            ),
            FadeInFromDown(quote_label),
            ShowCreation(quote_rect)
        )
        self.wait(3)
        self.play(
            ApplyMethod(
                VGroup(hamilton, shamrock, hamilton_name).to_edge, RIGHT,
                run_time=2,
                rate_func=squish_rate_func(smooth, 0.5, 1),
            ),
            LaggedStartMap(
                FadeOutAndShiftDown, VGroup(*it.chain(
                    quote, quote_rect, quote_label
                ))
            )
        )
        self.wait()
        self.play(FadeIn(plaque))
        self.play(
            ShowCreation(equation_rect),
            GrowArrow(equation_arrow)
        )
        self.play(ReplacementTransform(
            equation.copy().replace(equation_rect).fade(1),
            equation
        ))
        self.wait()


class QuaternionHistory(Scene):
    CONFIG = {
        "names_and_quotes": [
            (
                "Oliver Heaviside",
                """\\huge ``As far as the vector analysis I required was
                concerned, the quaternion was not only not
                required, but was a positive evil of no
                inconsiderable magnitude.''"""
            ),
            (
                "Lord Kelvin",
                """\\huge ``Quaternions... though beautifully \\\\ ingenious,
                have been an unmixed evil to those who have
                touched them in any way, including Clerk Maxwell.''"""
            ),
        ]
    }

    def construct(self):
        self.show_dot_product_and_cross_product()
        self.teaching_students_quaternions()
        self.show_anti_quaternion_quote()
        self.mad_hatter()

    def show_dot_product_and_cross_product(self):
        date = TexMobject("1843")
        date.scale(2)
        date.to_edge(UP)

        t2c = self.t2c = {
            "x_1": GREEN,
            "x_2": GREEN,
            "y_1": RED,
            "y_2": RED,
            "z_1": BLUE,
            "z_2": BLUE,
        }

        def get_colored_tex_mobject(tex):
            return TexMobject(tex, tex_to_color_map=t2c)

        v1, v2 = [
            Matrix([
                ["{}_{}".format(c, i)]
                for c in "xyz"
            ], element_to_mobject=get_colored_tex_mobject)
            for i in (1, 2)
        ]
        dot_rhs = get_colored_tex_mobject(
            "x_1 x_2 + y_1 y_2 + z_1 z_2",
        )
        cross_rhs = Matrix([
            ["y_1 z_2 - z_1 y_2"],
            ["z_1 x_2 - x_1 z_2"],
            ["x_1 y_2 - y_1 x_2"],
        ], element_to_mobject=get_colored_tex_mobject)

        dot_product = VGroup(
            v1.copy(), TexMobject("\\cdot").scale(2),
            v2.copy(), TexMobject("="),
            dot_rhs
        )
        cross_product = VGroup(
            v1.copy(), TexMobject("\\times"),
            v2.copy(), TexMobject("="),
            cross_rhs
        )
        for product in dot_product, cross_product:
            product.arrange(RIGHT, buff=2 * SMALL_BUFF)
            product.set_height(1.5)
        dot_product.next_to(date, DOWN, buff=MED_LARGE_BUFF)
        dot_product.to_edge(LEFT, buff=LARGE_BUFF)
        cross_product.next_to(
            dot_product, DOWN,
            buff=MED_LARGE_BUFF,
            aligned_edge=LEFT,
        )

        self.play(FadeInFrom(dot_product, 2 * RIGHT))
        self.play(FadeInFrom(cross_product, 2 * LEFT))
        self.wait()
        self.play(FadeInFromDown(date))
        self.play(ApplyMethod(dot_product.fade, 0.7))
        self.play(ApplyMethod(cross_product.fade, 0.7))
        self.wait()
        self.play(
            FadeOutAndShift(dot_product, 2 * LEFT),
            FadeOutAndShift(cross_product, 2 * RIGHT),
        )

        self.date = date

    def teaching_students_quaternions(self):
        hamilton = ImageMobject("Hamilton")
        hamilton.set_height(4)
        hamilton.pixel_array = hamilton.pixel_array[:, ::-1, :]
        hamilton.to_corner(UR)
        hamilton.shift(MED_SMALL_BUFF * DOWN)

        colors = color_gradient([BLUE_E, GREY_BROWN, BLUE_B], 7)
        random.shuffle(colors)
        students = VGroup(*[
            PiCreature(color=color)
            for color in colors
        ])
        students.set_height(2)
        students.arrange(RIGHT)
        students.set_width(FRAME_WIDTH - hamilton.get_width() - 1)
        students.to_corner(DL)

        equation = TexMobject("""
            (x_1 i + y_1 j + z_1 k)
            (x_2 i + y_2 j + z_2 k)
            =
            (-x_1 x_2 - y_1 y_2 - z_1 z_2) +
            (y_1 z_2 - z_1 y_2)i +
            (z_1 x_2 - x_1 z_2)j +
            (x_1 y_2 - y_1 x_2)k
        """, tex_to_color_map=self.t2c)
        equation.set_width(FRAME_WIDTH - 1)
        equation.to_edge(UP, buff=MED_SMALL_BUFF)

        images = Group()
        image_labels = VGroup()
        images_with_labels = Group()
        names = ["Peter Tait", "Robert Ball", "Macfarlane Alexander"]
        for name in names:
            image = ImageMobject(name)
            image.set_height(3)
            label = TextMobject(name)
            label.scale(0.5)
            label.next_to(image, DOWN)
            image.label = label
            image_labels.add(label)
            images.add(image)
            images_with_labels.add(Group(image, label))
        images_with_labels.arrange(RIGHT)
        images_with_labels.next_to(hamilton, LEFT, LARGE_BUFF)
        images_with_labels.shift(MED_LARGE_BUFF * DOWN)
        society_title = TextMobject("Quaternion society")
        society_title.next_to(images, UP, MED_LARGE_BUFF, UP)

        def blink_wait(n_loops):
            for x in range(n_loops):
                self.play(Blink(random.choice(students)))
                self.wait(random.random())

        self.play(
            FadeInFromDown(hamilton),
            Write(
                self.date,
                rate_func=lambda t: smooth(1 - t),
                remover=True
            )
        )
        self.play(LaggedStartMap(
            FadeInFrom, students,
            lambda m: (m, LEFT),
        ))
        self.play(
            LaggedStartMap(
                ApplyMethod, students,
                lambda pi: (
                    pi.change,
                    random.choice(["confused", "maybe", "erm"]),
                    3 * LEFT + 2 * UP,
                ),
            ),
            Write(equation),
        )
        blink_wait(3)
        self.play(
            LaggedStartMap(FadeInFromDown, images),
            LaggedStartMap(FadeInFromLarge, image_labels),
            Write(society_title)
        )
        blink_wait(3)
        self.play(
            FadeOutAndShift(hamilton, RIGHT),
            LaggedStartMap(
                FadeOutAndShift, images_with_labels,
                lambda m: (m, UP)
            ),
            FadeOutAndShift(students, DOWN),
            FadeOut(society_title),
            run_time=1
        )

        self.equation = equation

    def show_anti_quaternion_quote(self):
        group = self.get_dissenter_images_quotes_and_names()
        images, quotes, names = group
        self.play(
            LaggedStartMap(FadeInFromDown, images),
            LaggedStartMap(FadeInFromLarge, names),
            lag_ratio=0.75,
            run_time=2,
        )
        for quote in quotes:
            self.play(LaggedStartMap(
                FadeIn, VGroup(*quote.family_members_with_points()),
                lag_ratio=0.3
            ))
            self.wait()
        self.play(FadeOut(images_with_quotes))

    def mad_hatter(self):
        title = TextMobject(
            "Lewis Carroll's", "``Alice in wonderland''"
        )
        title.to_edge(UP, buff=LARGE_BUFF)
        author_brace = Brace(title[0], DOWN)
        aka = TextMobject("a.k.a. Mathematician Charles Dodgson")
        aka.scale(0.8)
        aka.set_color(BLUE)
        aka.next_to(author_brace, DOWN)

        quote = TextMobject(
            """
                ``Why, you might just as well say that\\\\
                ‘I see what I eat’ is the same thing as\\\\
                ‘I eat what I see’!''
            """,
            tex_to_color_map={
                "I see what I eat": BLUE,
                "I eat what I see": YELLOW,
            },
            alignment=""
        )
        quote.to_edge(UP, buff=LARGE_BUFF)

        hatter = PiCreature(color=RED, mode="surprised")
        hat = SVGMobject(file_name="hat")
        hat_back = hat.copy()
        hat_back[0].remove(*[
            sm for sm in hat_back[0] if sm.is_subpath
        ])
        hat_back.set_fill(DARK_GREY)
        hat.add_to_back(hat_back)
        hat.set_height(1.25)
        hat.next_to(hatter.body, UP, buff=-MED_SMALL_BUFF)
        hatter.add(hat)
        hatter.look(DL)
        hatter.pupils[1].save_state()
        hatter.look(UL)
        hatter.pupils[1].restore()
        hatter.set_height(2)

        hare = SVGMobject(file_name="bunny")
        mouse = SVGMobject(file_name="mouse")
        for mob in hare, mouse:
            mob.set_color(LIGHT_GREY)
            mob.set_sheen(0.2, UL)
            mob.set_height(1.5)

        characters = VGroup(hatter, hare, mouse)
        for mob, p in zip(characters, [UP, DL, DR]):
            mob.move_to(p)
        hare.shift(MED_SMALL_BUFF * LEFT)

        characters.space_out_submobjects(1.5)
        characters.to_edge(DOWN)

        def change_single_place(char, **kwargs):
            i = characters.submobjects.index(char)
            target = characters[(i + 1) % 3]
            return ApplyMethod(
                char.move_to, target,
                path_arc=-90 * DEGREES,
                **kwargs
            )

        def get_change_places():
            return LaggedStartMap(
                change_single_place, characters,
                lag_ratio=0.6
            )

        self.play(
            Write(title),
            LaggedStartMap(FadeInFromDown, characters)
        )
        self.play(
            get_change_places(),
            GrowFromCenter(author_brace),
            FadeIn(aka)
        )
        for x in range(4):
            self.play(get_change_places())
        self.play(
            FadeOutAndShift(VGroup(title, author_brace, aka)),
            FadeInFromDown(quote),
        )
        self.play(get_change_places())
        self.play(
            get_change_places(),
            VFadeOut(characters, run_time=2)
        )
        self.remove(characters)
        self.wait()

    #
    def get_dissenter_images_quotes_and_names(self):
        names_and_quotes = self.names_and_quotes
        images = Group()
        quotes = VGroup()
        names = VGroup()
        images_with_quotes = Group()
        for name, quote_text in names_and_quotes:
            image = Group(ImageMobject(name))
            image.set_height(4)
            label = TextMobject(name)
            label.next_to(image, DOWN)
            names.add(label)
            quote = TextMobject(
                quote_text,
                tex_to_color_map={
                    "positive evil": RED,
                    "unmixed evil": RED,
                },
                alignment=""
            )
            quote.scale(0.3)
            quote.next_to(image, UP)
            images.add(image)
            quotes.add(quote)
            images_with_quotes.add(Group(image, label, quote))

        images_with_quotes.arrange(RIGHT, buff=LARGE_BUFF)
        images_with_quotes.to_edge(DOWN, MED_LARGE_BUFF)
        return Group(images, quotes, names)


class QuaternionRotationOverlay(Scene):
    def construct(self):
        equations = VGroup(
            TexMobject(
                "p", "\\rightarrow",
                "{}",
                "{}",
                "\\left(q_1",
                "p",
                "q_1^{-1}\\right)",
                "{}",
                "{}",
            ),
            TexMobject(
                "p", "\\rightarrow",
                "{}",
                "\\left(q_2",
                "\\left(q_1",
                "p",
                "q_1^{-1}\\right)",
                "q_2^{-1}\\right)",
                "{}",
            ),
            TexMobject(
                "p", "\\rightarrow",
                "\\left(q_3",
                "\\left(q_2",
                "\\left(q_1",
                "p",
                "q_1^{-1}\\right)",
                "q_2^{-1}\\right)",
                "q_3^{-1}\\right)",
            ),
        )
        for equation in equations:
            equation.set_color_by_tex_to_color_map({
                "1": GREEN, "2": RED, "3": BLUE,
            })
            equation.set_color_by_tex("rightarrow", WHITE)
            equation.to_corner(UL)

        equation = equations[0].copy()
        self.play(Write(equation))
        self.wait()
        for new_equation in equations[1:]:
            self.play(
                Transform(equation, new_equation)
            )
            self.wait(2)


class RotateCubeThreeTimes(SpecialThreeDScene):
    def construct(self):
        cube = RubiksCube()
        cube.set_fill(opacity=0.8)
        cube.set_stroke(width=1)
        randy = Randolph(mode="pondering")
        randy.set_height(cube.get_height() - 2 * SMALL_BUFF)
        randy.move_to(cube.get_edge_center(OUT))
        randy.set_fill(opacity=0.8)
        # randy.set_shade_in_3d(True)
        cube.add(randy)
        axes = self.get_axes()

        self.add(axes, cube)
        self.move_camera(
            phi=70 * DEGREES,
            theta=-140 * DEGREES,
        )
        self.begin_ambient_camera_rotation(rate=0.02)
        self.wait(2)
        self.play(Rotate(cube, TAU / 4, RIGHT, run_time=3))
        self.wait(2)
        self.play(Rotate(cube, TAU / 4, UP, run_time=3))
        self.wait(2)
        self.play(Rotate(cube, -TAU / 3, np.ones(3), run_time=3))
        self.wait(7)


class QuantumSpin(Scene):
    def construct(self):
        title = Title("Two-state system")

        electron = Dot(color=BLUE)
        electron.set_height(1)
        electron.set_sheen(0.3, UL)
        electron.set_fill(opacity=0.8)
        kwargs = {
            "path_arc": PI,
        }
        curved_arrows = VGroup(
            Arrow(RIGHT, LEFT, **kwargs),
            Arrow(LEFT, RIGHT, **kwargs),
        )
        curved_arrows.set_color(LIGHT_GREY)
        curved_arrows.set_stroke(width=2)

        y_arrow = Vector(UP)
        y_arrow.set_color(RED)

        y_ca = curved_arrows.copy()
        y_ca.rotate(70 * DEGREES, LEFT)
        y_group = VGroup(y_ca[0], y_arrow, electron.copy(), y_ca[1])

        x_arrow = y_arrow.copy().rotate(90 * DEGREES, IN, about_point=ORIGIN)
        x_arrow.set_color(GREEN)
        x_ca = curved_arrows.copy()
        x_ca.rotate(70 * DEGREES, UP)
        x_group = VGroup(x_ca[0], x_arrow, electron.copy(), x_ca[1])

        z_ca = curved_arrows.copy()
        z_group = VGroup(electron.copy(), z_ca, Dot(color=BLUE))

        groups = VGroup(x_group, y_group, z_group)
        groups.arrange(RIGHT, buff=1.5)
        groups.move_to(UP)

        y_ca.rotation = Rotating(
            y_ca, axis=rotate_vector(OUT, 70 * DEGREES, LEFT)
        )
        x_ca.rotation = Rotating(
            x_ca, axis=rotate_vector(OUT, 70 * DEGREES, UP)
        )
        z_ca.rotation = Rotating(z_ca, axis=OUT)
        rotations = [ca.rotation for ca in [x_ca, y_ca, z_ca]]

        matrices = VGroup(
            Matrix([["0", "1"], ["1", "0"]]),
            Matrix([["0", "-i"], ["i", "0"]]),
            Matrix([["1", "0"], ["0", "-1"]]),
        )
        for matrix, group in zip(matrices, groups):
            matrix.next_to(group, DOWN)
        for matrix in matrices[1:]:
            matrix.align_to(matrices[0], DOWN)

        self.add(title, groups)
        self.play()
        self.play(
            LaggedStartMap(FadeInFromDown, matrices, run_time=3),
            *rotations
        )
        for x in range(2):
            self.play(*rotations)


class HereWeTackle4d(TeacherStudentsScene):
    def construct(self):
        titles = VGroup(
            TextMobject(
                "This video:\\\\",
                "Quaternions in 4d"
            ),
            TextMobject(
                "Next video:\\\\",
                "Quaternions acting on 3d"
            )
        )
        for title in titles:
            title.move_to(self.hold_up_spot, DOWN)
        titles[0].set_color(YELLOW)

        self.play(
            self.teacher.change, "raise_right_hand",
            FadeInFromDown(titles[0]),
            self.get_student_changes("confused", "horrified", "sad")
        )
        self.look_at(self.screen)
        self.wait()
        self.change_student_modes(
            "erm", "thinking", "pondering",
            look_at_arg=self.screen
        )
        self.wait(3)
        self.change_student_modes(
            "pondering", "confused", "happy"
        )
        self.look_at(self.screen)
        self.wait(3)
        self.play(
            self.teacher.change, "hooray",
            FadeInFrom(titles[1]),
            ApplyMethod(
                titles[0].shift, 2 * UP,
                rate_func=squish_rate_func(smooth, 0.2, 1)
            )
        )
        self.change_all_student_modes("hooray")
        self.play(self.teacher.change, "happy")
        self.look_at(self.screen)
        self.wait(3)
        self.change_student_modes("pondering", "happy", "thinking")
        self.wait(4)


class TableOfContents(Scene):
    def construct(self):
        chapters = VGroup(
            TextMobject(
                "\\underline{Chapter 1}\\\\", "Linus the Linelander"
            ),
            TextMobject(
                "\\underline{Chapter 2}\\\\", "Felix the Flatlander"
            ),
            TextMobject(
                "\\underline{Chapter 3}\\\\", " You, the 3d-lander"
            ),
        )
        for chapter in chapters:
            chapter.space_out_submobjects(1.5)
        chapters.arrange(
            DOWN, buff=1.5, aligned_edge=LEFT
        )
        chapters.to_edge(LEFT)

        for chapter in chapters:
            self.play(FadeInFromDown(chapter))
            self.wait(2)
        for chapter in chapters:
            chapters.save_state()
            other_chapters = VGroup(*[
                c for c in chapters if c is not chapter
            ])
            self.play(
                chapter.set_width, 0.5 * FRAME_WIDTH,
                chapter.center,
                other_chapters.fade, 1
            )
            self.wait(3)
            self.play(chapters.restore)


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
        algebra.arrange(DOWN)
        algebra.next_to(number_line, DOWN, LARGE_BUFF)
        algebra.shift(3 * RIGHT)

        self.play(
            ShowCreation(number_line),
            linus.look_at, number_line
        )
        self.play(
            LaggedStartMap(FadeInFromDown, number_line.numbers),
            LaggedStartMap(ShowCreation, number_line.tick_marks),
            linus.change, "happy"
        )
        self.play(
            LaggedStartMap(FadeInFromDown, algebra),
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
        q_marks_anim = LaggedStartMap(
            FadeIn, q_marks,
            run_time=15,
            rate_func=there_and_back,
            lag_ratio=0.1
        )
        q_marks_continual = turn_animation_into_updater(q_marks_anim)

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
            LaggedStartMap(FadeIn, real_label),
            linus.change, "confused", number,
            run_time=1
        )
        self.wait()
        self.play(
            GrowFromCenter(imag_brace),
            LaggedStartMap(FadeIn, imag_label),
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
        product.arrange(RIGHT, SMALL_BUFF)
        product.move_to(2 * RIGHT + 2 * UP)

        foil = VGroup(*map(TextMobject, [
            "First", "Outside", "Inside", "Last",
        ]))
        foil.arrange(
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
        expansion.arrange(RIGHT, buff=0.15)
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
        final_prouct.arrange(RIGHT, buff=0.15)
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
            LaggedStartMap(ShowCreation, final_arrows),
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
            LaggedStartMap(GrowFromCenter, braces),
            LaggedStartMap(Write, labels),
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
        defining_products.arrange(DOWN)
        defining_products.next_to(self.students, UP, LARGE_BUFF)
        def_rect = SurroundingRectangle(defining_products)

        self.play(
            LaggedStartMap(FadeInFromDown, defining_products),
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
        self.play(self.teacher.change, "sassy", equation)
        self.wait(2)
        self.change_all_student_modes("pondering")
        self.look_at(equation)
        self.wait()
        self.play(self.teacher.change, "thinking", equation)
        self.wait(8)


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
        problems.arrange(
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
            LaggedStartMap(FadeInFromDown, title, lag_ratio=0.5),
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
        z_label.arrange(
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
        w_label.arrange(RIGHT, buff=SMALL_BUFF)
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
        self.play(LaggedStartMap(
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
            FadeInFrom(product[2], LEFT),
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
        sparkly_plane.sort(
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
        equations.arrange(DOWN)
        equations.scale(1.5)
        for eq in equations:
            eq.add_background_rectangle()
        equations.next_to(func_words, DOWN)
        equations.to_edge(LEFT)

        product_label = VGroup(
            TexMobject("z \\cdot w ="),
            DecimalNumber(product, num_decimal_places=0)
        )
        product_label.arrange(RIGHT)
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
        self.play(LaggedStartMap(
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
                # LaggedStartMap(FadeIn, words, run_time=1),
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
        center_dot = Dot(color=WHITE)

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

        self.add(circle, center_dot, r_line, angle_label, arc)
        angles = IntroduceStereographicProjection.CONFIG.get(
            "example_angles"
        )
        for angle in angles:
            self.play(Rotate(circle, angle, run_time=4))
            self.wait()


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

        self.play(LaggedStartMap(FadeInFromLarge, dots))
        self.play(FadeInFromLarge(neg_one_dot))
        self.add(lines, neg_one_dot, dots)
        self.play(LaggedStartMap(ShowCreation, lines))
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
        frame_height_growth = frame_height_tracker.add_updater(
            lambda m, dt: m.set_value(m.get_value + 0.5 * dt)
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
            if value is sample_values[1]:
                label.next_to(dot, UL, SMALL_BUFF)
            else:
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
        rotater = 1
        if hasattr(self, "circle_shadow"):
            point = self.circle_shadow[0].points[0]
            rotater = complex(*point[:2])
            rotater /= abs(rotater)
        numbers = [
            rotater * np.exp(complex(0, TAU * x / n))
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
            length = line.get_length()
            line.scale(20 / length, about_point=neg_one_point)
            line.set_stroke(YELLOW, np.clip(length, 0, 1))
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
        linus = self.linus = self.get_linus()

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

        stot = "(\\sqrt{2} / 2)"
        labels_tex = [
            "-{}-{}i".format(stot, stot),
            "-i",
            "{}-{}i".format(stot, stot),
            "1",
            "{}+{}i".format(stot, stot),
            "i",
            "-{}+{}i".format(stot, stot),
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
                label.set_height(0.5)
            else:
                label.set_height(0.5)
                label.set_stroke(WHITE, 2, background=True)
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
                LaggedStartMap(GrowArrow, arrows[i::2]),
                LaggedStartMap(Write, labels[i::2])
            )
            self.play(Blink(linus))

        self.dots = dots

    def point_at_infinity(self):
        circle = self.circle
        linus = self.linus

        label = TextMobject(
            "$-1$ is \\\\ at $\\pm \\infty$"
        )
        label.scale(1.5)
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
                    run_time=4,
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

        lines = always_redraw(self.get_lines)

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
            run_time=2
        )
        self.play(
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
                run_time=4
            )
            self.wait()


class WriteITimesW(Scene):
    def construct(self):
        mob = TexMobject("i", "\\cdot", "w")
        mob[0].set_color(GREEN)
        mob.scale(3)
        self.play(Write(mob))
        self.wait()


class IntroduceFelix(PiCreatureScene, SpecialThreeDScene):
    def setup(self):
        PiCreatureScene.setup(self)
        SpecialThreeDScene.setup(self)

    def construct(self):
        self.introduce_felix()
        self.add_plane()
        self.show_in_three_d()

    def introduce_felix(self):
        felix = self.felix = self.pi_creature

        arrow = Vector(DL, color=WHITE)
        arrow.next_to(felix, UR)

        label = TextMobject("Felix the Flatlander")
        label.next_to(arrow.get_start(), UP)

        self.add(felix)
        self.play(
            felix.change, "wave_1", label,
            Write(label),
            GrowArrow(arrow),
        )
        self.play(Blink(felix))
        self.play(felix.change, "thinking", label)

        self.to_fade = VGroup(label, arrow)

    def add_plane(self):
        plane = NumberPlane(y_radius=10)
        axes = self.get_axes()
        to_fade = self.to_fade
        felix = self.felix

        self.add(axes, plane, felix)
        self.play(
            ShowCreation(axes),
            ShowCreation(plane),
            FadeOut(to_fade),
        )
        self.wait()

        self.plane = plane
        self.axes = axes

    def show_in_three_d(self):
        felix = self.pi_creature
        plane = self.plane
        axes = self.axes

        # back_plane = Rectangle().replace(plane, stretch=True)
        # back_plane.shade_in_3d = True
        # back_plane.set_fill(LIGHT_GREY, opacity=0.5)
        # back_plane.set_sheen(1, UL)
        # back_plane.shift(SMALL_BUFF * IN)
        # back_plane.set_stroke(width=0)
        # back_plane = ParametricSurface(
        #     lambda u, v: u * RIGHT + v * UP
        # )
        # back_plane.replace(plane, stretch=True)
        # back_plane.set_stroke(width=0)
        # back_plane.set_fill(LIGHT_GREY, opacity=0.5)

        sphere = self.get_sphere()
        # sphere.set_fill(BLUE_E, 0.5)

        self.move_camera(
            phi=70 * DEGREES,
            theta=-110 * DEGREES,
            added_anims=[FadeOut(plane)],
            run_time=2
        )
        self.begin_ambient_camera_rotation()
        self.add(axes, sphere)
        self.play(
            Write(sphere),
            felix.change, "confused"
        )
        self.wait()

        axis_angle_pairs = [
            (RIGHT, 90 * DEGREES),
            (OUT, 45 * DEGREES),
            (UR + OUT, 120 * DEGREES),
            (RIGHT, 90 * DEGREES),
        ]
        for axis, angle in axis_angle_pairs:
            self.play(Rotate(
                sphere, angle=angle, axis=axis,
                run_time=2,
            ))
        self.wait(2)

    #
    def create_pi_creature(self):
        return Felix().move_to(4 * LEFT + 2 * DOWN)


class IntroduceThreeDNumbers(SpecialThreeDScene):
    CONFIG = {
        "camera_config": {
            "exponential_projection": False,
        }
    }

    def construct(self):
        self.add_third_axis()
        self.reorient_axes()
        self.show_example_number()

    def add_third_axis(self):
        plane = ComplexPlane(
            y_radius=FRAME_WIDTH / 4,
            unit_size=2,
            secondary_line_ratio=1,
        )
        plane.add_coordinates()
        title = TextMobject("Complex Plane")
        title.scale(1.8)
        title.add_background_rectangle()
        title.to_corner(UL, buff=MED_SMALL_BUFF)

        real_line = Line(LEFT, RIGHT).set_width(FRAME_WIDTH)
        imag_line = Line(DOWN, UP).set_height(FRAME_HEIGHT)
        real_line.set_color(YELLOW)
        imag_line.set_color(RED)

        for label in plane.coordinate_labels:
            label.remove(label.background_rectangle)
            label.shift(SMALL_BUFF * IN)
            self.add_fixed_orientation_mobjects(label)
        reals = plane.coordinate_labels[:7]
        imags = plane.coordinate_labels[7:]

        self.add(plane, title)
        for line, group in (real_line, reals), (imag_line, imags):
            line.set_stroke(width=5)
            self.play(
                ShowCreationThenDestruction(line),
                LaggedStartMap(
                    Indicate, group,
                    rate_func=there_and_back,
                    color=line.get_color(),
                ),
                run_time=2,
            )

        self.plane = plane
        self.title = title

    def reorient_axes(self):
        z_axis = NumberLine(unit_size=2)
        z_axis.rotate(90 * DEGREES, axis=DOWN)
        z_axis.rotate(90 * DEGREES, axis=OUT)
        z_axis.set_color(WHITE)
        z_axis_top = Line(
            z_axis.number_to_point(0),
            z_axis.get_end(),
        )
        z_axis_top.match_style(z_axis)

        z_unit_line = Line(
            z_axis.number_to_point(0),
            z_axis.number_to_point(1),
            color=RED,
            stroke_width=5
        )

        j_labels = VGroup(
            TexMobject("-2j"),
            TexMobject("-j"),
            TexMobject("j"),
            TexMobject("2j"),
        )
        for label, num in zip(j_labels, [-2, -1, 1, 2]):
            label.next_to(z_axis.number_to_point(num), RIGHT, MED_SMALL_BUFF)
            self.add_fixed_orientation_mobjects(label)

        plane = self.plane

        colored_ = Line(LEFT, RIGHT).set_width(FRAME_WIDTH)
        y_line = Line(DOWN, UP).set_height(FRAME_WIDTH)
        z_line = Line(IN, OUT).set_depth(FRAME_WIDTH)
        colored_.set_stroke(GREEN, 5)
        y_line.set_stroke(RED, 5)
        z_line.set_stroke(YELLOW, 5)
        colored_coord_lines = VGroup(colored_, y_line, z_line)

        coord_lines = VGroup(
            plane.axes[0], plane.axes[1], z_axis,
        )
        for i1, i2 in [(0, 2), (1, 0), (2, 1)]:
            coord_lines[i1].target = coord_lines[i2].copy()

        new_title = TextMobject("Imaginary plane")
        new_title.replace(self.title)
        new_title.move_to(self.title)

        self.add(z_axis, plane, z_axis_top)
        self.move_camera(
            phi=70 * DEGREES,
            theta=-80 * DEGREES,
            added_anims=[
                plane.set_stroke, {"opacity": 0.5},
            ],
            run_time=2,
        )
        self.begin_ambient_camera_rotation(rate=0.02)
        self.wait()
        self.play(FadeInFrom(j_labels, IN))
        z_axis.add(j_labels)
        self.play(
            ShowCreationThenDestruction(z_unit_line),
            run_time=2
        )
        self.wait(4)

        group = VGroup(*it.chain(plane.coordinate_labels, j_labels))
        for label in group:
            label.generate_target()
            axis = np.ones(3)
            label.target.rotate_about_origin(-120 * DEGREES, axis=axis)
            label.target.rotate(120 * DEGREES, axis=axis)
        for y, label in zip([-2, -1, 1, 2], j_labels):
            label.target.scale(0.65)
            label.target.next_to(
                2 * y * UP, RIGHT, 2 * SMALL_BUFF
            )
        self.remove(z_axis_top)
        self.play(
            LaggedStartMap(MoveToTarget, group, lag_ratio=0.8),
            LaggedStartMap(MoveToTarget, coord_lines, lag_ratio=0.8),
            FadeOut(self.title),
            FadeIn(new_title),
            run_time=3
        )
        self.add(z_axis_top)
        self.wait(3)
        for line, wait in zip(colored_coord_lines, [False, True, True]):
            self.play(
                ShowCreationThenDestruction(line),
                run_time=2
            )
            if wait:
                self.wait()

    def show_example_number(self):
        x, y, z = coords = 2 * np.array([1.5, -1, 1.25])
        dot = Sphere(radius=0.05)
        dot.set_fill(LIGHT_GREY)
        dot.move_to(coords)
        point_line = Line(ORIGIN, coords)
        point_line.set_stroke(WHITE, 1)

        z_line = Line(ORIGIN, z * OUT)
        x_line = Line(z_line.get_end(), z_line.get_end() + x * RIGHT)
        y_line = Line(x_line.get_end(), x_line.get_end() + y * UP)

        x_line.set_stroke(GREEN, 5)
        y_line.set_stroke(RED, 5)
        z_line.set_stroke(YELLOW, 5)
        lines = VGroup(z_line, x_line, y_line)

        number_label = TexMobject(
            str(z / 2), "+", str(x / 2), "i", "+", str(y / 2), "j",
            tex_to_color_map={
                str(z / 2): YELLOW,
                str(x / 2): GREEN,
                str(y / 2): RED,
            }
        )
        number_label.next_to(ORIGIN, RIGHT, LARGE_BUFF)
        number_label.to_edge(UP)

        self.add_fixed_in_frame_mobjects(number_label)
        self.play(
            ShowCreation(point_line),
            FadeInFrom(dot, -coords),
            FadeInFromDown(number_label)
        )
        self.wait()
        for num, line in zip([z, x, y], lines):
            tex = number_label.get_part_by_tex(str(num / 2))
            rect = SurroundingRectangle(tex)
            rect.set_color(WHITE)

            self.add_fixed_in_frame_mobjects(rect)
            self.play(
                ShowCreation(line),
                ShowCreationThenDestruction(rect),
                run_time=2
            )
            self.remove_fixed_in_frame_mobjects(rect)
            self.wait()
        self.wait(15)


class MentionImpossibilityOf3dNumbers(TeacherStudentsScene):
    def construct(self):
        equations = VGroup(
            TexMobject("ij = ?"),
            TexMobject("ji = ?"),
        )
        equations.arrange(RIGHT, buff=LARGE_BUFF)
        equations.scale(1.5)
        equations.to_edge(UP)
        self.add(equations)

        why = TextMobject("Why not?")
        why.next_to(self.students[1], UP)

        self.teacher_says(
            "Such 3d numbers \\\\ have no good \\\\ multiplication rule",
            bubble_kwargs={"width": 4, "height": 3},
        )
        self.change_all_student_modes("confused")
        self.wait(2)
        self.play(
            self.students[1].change, "maybe",
            FadeInFromLarge(why),
        )
        self.wait(4)


class SphereExamplePointsDecimal(Scene):
    CONFIG = {
        "point_rotation_angle_axis_pairs": [
            (45 * DEGREES, DOWN),
            (120 * DEGREES, OUT),
            (35 * DEGREES, rotate_vector(RIGHT, 30 * DEGREES)),
            (90 * DEGREES, IN),
        ]
    }

    def construct(self):
        decimals = VGroup(*[
            DecimalNumber(
                0,
                num_decimal_places=3,
                color=color,
                include_sign=True,
                edge_to_fix=RIGHT,
            )
            for color in [YELLOW, GREEN, RED]
        ])
        number_label = VGroup(
            decimals[0], TexMobject("+"),
            decimals[1], TexMobject("i"), TexMobject("+"),
            decimals[2], TexMobject("j"),
        )
        number_label.arrange(RIGHT, buff=SMALL_BUFF)
        number_label.to_corner(UL)

        point = VectorizedPoint(OUT)

        def generate_decimal_updater(decimal, index):
            shifted_i = (index - 1) % 3
            decimal.add_updater(lambda d: d.set_value(
                point.get_location()[shifted_i]
            ))
            return decimal

        for i, decimal in enumerate(decimals):
            self.add(generate_decimal_updater(decimal, i))

        decimal_braces = VGroup()
        for decimal, char in zip(decimals, "wxy"):
            brace = Brace(decimal, DOWN, buff=SMALL_BUFF)
            label = brace.get_tex(char, buff=SMALL_BUFF)
            label.match_color(decimal)
            brace.add(label)
            decimal_braces.add(brace)

        equation = TexMobject(
            "w^2 + x^2 + y^2 = 1",
            tex_to_color_map={
                "w": YELLOW,
                "x": GREEN,
                "y": RED,
            }
        )
        equation.next_to(decimal_braces, DOWN, MED_LARGE_BUFF)

        self.add(number_label)
        self.add(decimal_braces)
        self.add(equation)

        pairs = self.point_rotation_angle_axis_pairs
        for angle, axis in pairs:
            self.play(
                Rotate(point, angle, axis=axis, about_point=ORIGIN),
                run_time=2
            )
            self.wait()


class TwoDStereographicProjection(IntroduceFelix):
    CONFIG = {
        "camera_config": {
            "exponential_projection": False,
        },
        "sphere_sample_point_u_range": np.arange(
            0, PI, PI / 16,
        ),
        "sphere_sample_point_v_range": np.arange(
            0, TAU, TAU / 16,
        ),
        "n_sample_rotation_cycles": 2,
        "lift_labels": True,
    }

    def construct(self):
        self.add_parts()
        self.talk_through_sphere()
        self.draw_projection_lines()
        self.show_point_at_infinity()
        self.show_a_few_rotations()

    def add_parts(self, run_time=1):
        felix = self.felix = self.pi_creature
        felix.shift(1.5 * DL)
        axes = self.axes = self.get_axes()
        sphere = self.sphere = self.get_sphere()

        c2p = axes.coords_to_point
        labels = self.labels = VGroup(
            TexMobject("i").next_to(c2p(1, 0, 0), DR, SMALL_BUFF),
            TexMobject("-i").next_to(c2p(-1, 0, 0), DL, SMALL_BUFF),
            TexMobject("j").next_to(c2p(0, 1, 0), UL, SMALL_BUFF),
            TexMobject("-j").next_to(c2p(0, -1, 0), DL, SMALL_BUFF),
            TexMobject("1").rotate(
                90 * DEGREES, RIGHT,
            ).next_to(c2p(0, 0, 1), RIGHT + OUT, SMALL_BUFF),
            TexMobject("-1").rotate(
                90 * DEGREES, RIGHT,
            ).next_to(c2p(0, 0, -1), RIGHT + IN, SMALL_BUFF),
        )
        if self.lift_labels:
            for sm in labels[:4].family_members_with_points():
                sm.add(VectorizedPoint(
                    0.25 * DOWN + 0.25 * OUT
                ))
        labels.set_stroke(width=0, background=True)
        for submob in labels.get_family():
            submob.shade_in_3d = True

        self.add(felix, axes, sphere, labels)
        self.move_camera(
            **self.get_default_camera_position(),
            run_time=run_time
        )
        self.begin_ambient_camera_rotation(rate=0.01)
        self.play(
            felix.change, "pondering", sphere,
            run_time=run_time,
        )

    def talk_through_sphere(self):
        point = VectorizedPoint(OUT)
        arrow = Vector(IN, shade_in_3d=True)
        arrow.set_fill(PINK)
        arrow.set_stroke(BLACK, 1)

        def get_dot():
            dot = Sphere(radius=0.05, u_max=PI / 2)
            dot.set_fill(PINK)
            dot.set_stroke(width=0)
            dot.move_to(2.05 * OUT)
            dot.apply_matrix(
                z_to_vector(normalize(point.get_location())),
                about_point=ORIGIN
            )
            return dot

        dot = get_dot()
        dot.add_updater(
            lambda d: d.become(get_dot())
        )

        def update_arrow(arrow):
            target_point = 2.1 * point.get_location()
            rot_matrix = np.dot(
                z_to_vector(normalize(target_point)),
                np.linalg.inv(
                    z_to_vector(normalize(-arrow.get_vector()))
                )
            )
            arrow.apply_matrix(rot_matrix)
            arrow.shift(target_point - arrow.get_end())
            return arrow
        arrow.add_updater(update_arrow)

        self.add(self.sphere, dot, arrow)
        pairs = SphereExamplePointsDecimal.CONFIG.get(
            "point_rotation_angle_axis_pairs"
        )
        for angle, axis in pairs:
            self.play(
                Rotate(point, angle, axis=axis, about_point=ORIGIN),
                run_time=2
            )
            self.wait()
        self.play(FadeOut(dot), FadeOut(arrow))

    def draw_projection_lines(self):
        sphere = self.sphere
        axes = self.axes
        radius = sphere.get_width() / 2

        neg_one_point = axes.coords_to_point(0, 0, -1)
        neg_one_dot = Dot(
            neg_one_point,
            color=YELLOW,
            shade_in_3d=True
        )

        xy_plane = StereoProjectedSphere(
            u_max=15 * PI / 16,
            **self.sphere_config
        )
        xy_plane.set_fill(WHITE, 0.25)
        xy_plane.set_stroke(width=0)

        point_mob = VectorizedPoint(2 * OUT)
        point_mob.add_updater(
            lambda m: m.move_to(radius * normalize(m.get_center()))
        )
        point_mob.move_to([1, -1, 1])
        point_mob.update(0)

        def get_projection_line(sphere_point):
            to_sphere = Line(neg_one_point, sphere_point)
            to_plane = Line(
                sphere_point,
                self.project_point(sphere_point)
            )
            line = VGroup(to_sphere, to_plane)
            line.set_stroke(YELLOW, 3)
            for submob in line:
                submob.shade_in_3d = True
            return line

        def get_sphere_dot(sphere_point):
            dot = Dot()
            dot.set_shade_in_3d(True)
            dot.set_fill(PINK)
            dot.shift(OUT)
            dot.apply_matrix(
                z_to_vector(sphere_point),
                about_point=ORIGIN,
            )
            dot.move_to(1.01 * sphere_point)
            dot.add(VectorizedPoint(5 * sphere_point))
            return dot

        def get_projection_dot(sphere_point):
            projection = self.project_point(sphere_point)
            dot = Dot(projection, shade_in_3d=True)
            dot.add(VectorizedPoint(dot.get_center() + 0.1 * OUT))
            dot.set_fill(WHITE)
            return dot

        point = point_mob.get_location()
        dot = get_sphere_dot(point)
        line = get_projection_line(point)
        projection_dot = get_projection_dot(point)

        sample_points = [
            radius * sphere.func(u, v)
            for u in self.sphere_sample_point_u_range
            for v in self.sphere_sample_point_v_range
        ]

        lines = VGroup(*[get_projection_line(p) for p in sample_points])
        lines.set_stroke(width=1)
        north_lines = lines[:len(lines) // 2]
        south_lines = lines[len(lines) // 2:]

        self.add(xy_plane, sphere)
        self.play(Write(xy_plane))
        self.wait(2)
        self.play(sphere.set_fill, BLUE_E, 0.5)
        self.play(FadeInFromLarge(dot))
        self.play(
            FadeIn(neg_one_dot),
            ShowCreation(line),
        )
        self.wait(2)
        self.play(ReplacementTransform(
            dot.copy(), projection_dot
        ))

        def get_point():
            return 2 * normalize(point_mob.get_location())

        dot.add_updater(
            lambda d: d.become(get_sphere_dot(get_point()))
        )
        line.add_updater(
            lambda l: l.become(get_projection_line(get_point()))
        )
        projection_dot.add_updater(
            lambda d: d.become(get_projection_dot(get_point()))
        )

        self.play(
            point_mob.move_to,
            radius * normalize(np.array([1, -1, -1])),
            run_time=3
        )
        self.move_camera(
            theta=-150 * DEGREES,
            run_time=3
        )
        self.add(axes, sphere, xy_plane, dot, line)
        for point in np.array([-2, 1, -0.5]), np.array([-0.01, -0.01, 1]):
            self.play(
                point_mob.move_to,
                radius * normalize(point),
                run_time=3
            )
        self.wait(2)

        # Project norther hemisphere
        north_hemisphere = self.get_sphere()
        n = len(north_hemisphere)
        north_hemisphere.remove(*north_hemisphere[n // 2:])
        north_hemisphere.generate_target()
        self.project_mobject(north_hemisphere.target)
        north_hemisphere.set_fill(opacity=0.8)

        self.play(
            LaggedStartMap(ShowCreation, north_lines),
            FadeIn(north_hemisphere)
        )
        self.play(
            MoveToTarget(north_hemisphere),
            run_time=3,
            rate_func=lambda t: smooth(0.99 * t)
        )
        self.play(FadeOut(north_lines))
        self.wait(2)

        # Unit circle
        circle = Sphere(
            radius=2.01,
            u_min=PI / 2 - 0.01,
            u_max=PI / 2 + 0.01,
            resolution=(1, 24),
        )
        for submob in circle:
            submob.add(VectorizedPoint(1.5 * submob.get_center()))
        circle.set_fill(YELLOW)
        circle_path = Circle(radius=2)
        circle_path.rotate(-90 * DEGREES)

        self.play(FadeInFromLarge(circle))
        self.play(point_mob.move_to, circle_path.points[0])
        self.play(MoveAlongPath(point_mob, circle_path, run_time=6))
        self.move_camera(
            phi=0,
            theta=-90 * DEGREES,
            rate_func=there_and_back_with_pause,
            run_time=6,
        )
        self.play(point_mob.move_to, OUT)
        self.wait()

        # Southern hemisphere
        south_hemisphere = self.get_sphere()
        n = len(south_hemisphere)
        south_hemisphere.remove(*south_hemisphere[:n // 2])
        south_hemisphere.remove(
            *south_hemisphere[-sphere.resolution[1]:]
        )
        south_hemisphere.generate_target()
        self.project_mobject(south_hemisphere.target)
        south_hemisphere.set_fill(opacity=0.8)
        south_hemisphere.target[-sphere.resolution[1] // 2:].set_fill(
            opacity=0
        )

        self.play(
            LaggedStartMap(ShowCreation, south_lines),
            FadeIn(south_hemisphere)
        )
        self.play(
            MoveToTarget(south_hemisphere),
            FadeOut(south_lines),
            FadeOut(xy_plane),
            run_time=3,
            rate_func=lambda t: smooth(0.99 * t)
        )
        self.wait(3)

        self.projected_sphere = VGroup(
            north_hemisphere,
            south_hemisphere,
        )
        self.equator = circle
        self.point_mob = point_mob

    def show_point_at_infinity(self):
        points = list(compass_directions(
            12, start_vect=rotate_vector(RIGHT, 3.25 * DEGREES)
        ))
        points.pop(7)
        points.pop(2)
        arrows = VGroup(*[
            Arrow(6 * p, 11 * p)
            for p in points
        ])
        arrows.set_fill(RED)
        arrows.set_stroke(RED, 5)
        neg_ones = VGroup(*[
            TexMobject("-1").next_to(arrow.get_start(), -p)
            for p, arrow in zip(points, arrows)
        ])
        neg_ones.set_stroke(width=0, background=True)

        sphere_arcs = VGroup()
        for angle in np.arange(0, TAU, TAU / 12):
            arc = Arc(PI, radius=2)
            arc.set_stroke(RED)
            arc.rotate(PI / 2, axis=DOWN, about_point=ORIGIN)
            arc.rotate(angle, axis=OUT, about_point=ORIGIN)
            sphere_arcs.add(arc)
        sphere_arcs.set_stroke(RED)

        self.play(
            LaggedStartMap(GrowArrow, arrows),
            LaggedStartMap(Write, neg_ones)
        )
        self.wait(3)
        self.play(
            FadeOut(self.projected_sphere),
            FadeOut(arrows),
            FadeOut(neg_ones),
        )
        for x in range(2):
            self.play(
                ShowCreationThenDestruction(
                    sphere_arcs,
                    lag_ratio=0,
                    run_time=3,
                )
            )

    def show_a_few_rotations(self):
        sphere = self.sphere
        felix = self.felix
        point_mob = self.point_mob
        point_mob.add_updater(
            lambda m: m.move_to(sphere.get_all_points()[0])
        )
        coord_point_mobs = VGroup(
            VectorizedPoint(RIGHT),
            VectorizedPoint(UP),
            VectorizedPoint(OUT),
        )
        for pm in coord_point_mobs:
            pm.shade_in_3d = True

        def get_rot_matrix():
            return np.array([
                pm.get_location()
                for pm in coord_point_mobs
            ]).T

        def get_projected_sphere():
            result = StereoProjectedSphere(
                get_rot_matrix(),
                max_r=10,
                **self.sphere_config,
            )
            result.set_fill(opacity=0.2)
            result.fade_far_out_submobjects(max_r=32)
            for submob in result:
                if submob.get_center()[1] < -11:
                    submob.fade(1)
            return result

        projected_sphere = get_projected_sphere()
        projected_sphere.add_updater(
            lambda m: m.become(get_projected_sphere())
        )

        def get_projected_equator():
            equator = CheckeredCircle(
                n_pieces=24,
                radius=2,
            )
            for submob in equator.get_family():
                submob.shade_in_3d = True
            equator.set_stroke(YELLOW, 5)
            equator.apply_matrix(get_rot_matrix())
            self.project_mobject(equator)
            return equator

        projected_equator = get_projected_equator()
        projected_equator.add_updater(
            lambda m: m.become(get_projected_equator())
        )

        self.add(sphere, projected_sphere)
        self.move_camera(phi=60 * DEGREES)
        self.play(
            sphere.set_fill_by_checkerboard,
            BLUE_E, BLUE_D, {"opacity": 0.8},
            FadeIn(projected_sphere)
        )
        sphere.add(coord_point_mobs)
        sphere.add(self.equator)
        self.add(projected_equator)
        pairs = self.get_sample_rotation_angle_axis_pairs()
        for x in range(self.n_sample_rotation_cycles):
            for angle, axis in pairs:
                self.play(
                    Rotate(
                        sphere, angle=angle, axis=axis,
                        about_point=ORIGIN,
                        run_time=3,
                    ),
                    felix.change, "confused",
                )
                self.wait()

        self.projected_sphere = projected_sphere

    #
    def project_mobject(self, mobject):
        return stereo_project(mobject, axis=2, r=2, outer_r=20)

    def project_point(self, point):
        return stereo_project_point(point, axis=2, r=2)

    def get_sample_rotation_angle_axis_pairs(self):
        return SphereExamplePointsDecimal.CONFIG.get(
            "point_rotation_angle_axis_pairs"
        )


class FelixViewOfProjection(TwoDStereographicProjection):
    CONFIG = {}

    def construct(self):
        self.add_axes()
        self.show_a_few_rotations()

    def add_axes(self):
        axes = Axes(
            axis_config={
                "unit_size": 2,
                "color": WHITE,
            }
        )
        labels = VGroup(
            TexMobject("i"),
            TexMobject("-i"),
            TexMobject("j"),
            TexMobject("-j"),
            TexMobject("1"),
        )
        coords = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
        vects = [DOWN, DOWN, RIGHT, RIGHT, 0.25 * DR]
        for label, coords, vect in zip(labels, coords, vects):
            point = axes.coords_to_point(*coords)
            label.next_to(point, vect, buff=MED_SMALL_BUFF)

        self.add(axes, labels)
        self.pi_creature.change("confused")

    def show_a_few_rotations(self):
        felix = self.pi_creature
        coord_point_mobs = VGroup([
            VectorizedPoint(point)
            for point in [RIGHT, UP, OUT]
        ])

        def get_rot_matrix():
            return np.array([
                pm.get_location()
                for pm in coord_point_mobs
            ]).T

        def get_projected_sphere():
            return StereoProjectedSphere(
                get_rot_matrix(),
                **self.sphere_config,
            )

        def get_projected_equator():
            equator = Circle(radius=2, num_anchors=24)
            equator.set_stroke(YELLOW, 5)
            equator.apply_matrix(get_rot_matrix())
            self.project_mobject(equator)
            return equator

        projected_sphere = get_projected_sphere()
        projected_sphere.add_updater(
            lambda m: m.become(get_projected_sphere())
        )

        equator = get_projected_equator()
        equator.add_updater(
            lambda m: m.become(get_projected_equator())
        )

        dot = Dot(color=PINK)
        dot.add_updater(
            lambda d: d.move_to(
                self.project_point(
                    np.dot(2 * OUT, get_rot_matrix().T)
                )
            )
        )
        hand = Hand()
        hand.add_updater(
            lambda h: h.move_to(dot.get_center(), LEFT)
        )
        felix.add_updater(lambda f: f.look_at(dot))

        self.add(projected_sphere)
        self.add(equator)
        self.add(dot)
        self.add(hand)

        pairs = self.get_sample_rotation_angle_axis_pairs()
        for x in range(self.n_sample_rotation_cycles):
            for angle, axis in pairs:
                self.play(
                    Rotate(
                        coord_point_mobs, angle=angle, axis=axis,
                        about_point=ORIGIN,
                        run_time=3,
                    ),
                )
                self.wait()


class ShowRotationsJustWithReferenceCircles(TwoDStereographicProjection):
    CONFIG = {
        "flat_view": False,
    }

    def construct(self):
        self.add_parts(run_time=1)
        self.begin_ambient_camera_rotation(rate=0.03)
        self.edit_parts()
        self.show_1i_circle()
        self.show_1j_circle()
        self.show_random_circle()
        self.show_rotations()

    def edit_parts(self):
        sphere = self.sphere
        axes = self.axes
        axes.set_stroke(width=1)
        xy_plane = StereoProjectedSphere(u_max=15 * PI / 16)
        xy_plane.set_fill(WHITE, 0.2)
        xy_plane.set_stroke(width=0, opacity=0)

        self.add(xy_plane, sphere)
        self.play(
            FadeIn(xy_plane),
            sphere.set_fill, BLUE_E, {"opacity": 0.2},
            sphere.set_stroke, {"width": 0.1, "opacity": 0.5}
        )

    def show_1i_circle(self):
        axes = self.axes

        circle = self.get_circle(GREEN_E, GREEN)
        circle.rotate(TAU / 4, RIGHT)
        circle.rotate(TAU / 4, DOWN)

        projected = self.get_projected_circle(circle)

        labels = VGroup(*map(TexMobject, ["0", "2i", "3i"]))
        labels.set_shade_in_3d(True)
        if self.flat_view:
            labels.fade(1)
        for label, x in zip(labels, [0, 2, 3]):
            label.next_to(
                axes.coords_to_point(x, 0, 0), DR, SMALL_BUFF
            )

        self.play(ShowCreation(circle, run_time=3))
        self.wait()
        self.play(ReplacementTransform(
            circle.copy(), projected,
            run_time=3
        ))
        # self.axes.x_axis.pieces.set_stroke(width=0)
        self.wait(7)
        self.move_camera(
            phi=60 * DEGREES,
        )
        self.play(
            LaggedStartMap(
                FadeInFrom, labels,
                lambda m: (m, UP)
            )
        )
        self.wait(2)
        self.play(FadeOut(labels))

        self.one_i_circle = circle
        self.projected_one_i_circle = projected

    def show_1j_circle(self):
        circle = self.get_circle(RED_E, RED)
        circle.rotate(TAU / 4, DOWN)

        projected = self.get_projected_circle(circle)

        self.move_camera(theta=-170 * DEGREES)
        self.play(ShowCreation(circle, run_time=3))
        self.wait()
        self.play(ReplacementTransform(
            circle.copy(), projected, run_time=3
        ))
        # self.axes.y_axis.pieces.set_stroke(width=0)
        self.wait(3)

        self.one_j_circle = circle
        self.projected_one_j_circle = projected

    def show_random_circle(self):
        sphere = self.sphere

        circle = self.get_circle(BLUE_E, BLUE)
        circle.set_width(2 * sphere.radius * np.sin(30 * DEGREES))
        circle.shift(sphere.radius * np.cos(30 * DEGREES) * OUT)
        circle.rotate(150 * DEGREES, UP, about_point=ORIGIN)

        projected = self.get_projected_circle(circle)

        self.play(ShowCreation(circle, run_time=2))
        self.wait()
        self.play(ReplacementTransform(
            circle.copy(), projected,
            run_time=2
        ))
        self.wait(3)
        self.play(
            FadeOut(circle),
            FadeOut(projected),
        )

    def show_rotations(self):
        sphere = self.sphere
        c1i = self.one_i_circle
        pc1i = self.projected_one_i_circle
        c1j = self.one_j_circle
        pc1j = self.projected_one_j_circle
        cij = self.get_circle(YELLOW_E, YELLOW)
        pcij = self.get_projected_circle(cij)

        circles = VGroup(c1i, c1j, cij)
        x_axis = self.axes.x_axis
        y_axis = self.axes.y_axis

        arrow = Arrow(
            2 * RIGHT, 2 * UP,
            buff=SMALL_BUFF,
            path_arc=PI,
        )
        arrow.set_stroke(LIGHT_GREY, 3)
        arrow.tip.set_fill(LIGHT_GREY)
        arrows = VGroup(arrow, *[
            arrow.copy().rotate(angle, about_point=ORIGIN)
            for angle in np.arange(TAU / 4, TAU, TAU / 4)
        ])
        arrows.rotate(TAU / 4, RIGHT, about_point=ORIGIN)
        arrows.rotate(TAU / 2, OUT, about_point=ORIGIN)
        arrows.rotate(TAU / 4, UP, about_point=ORIGIN)
        arrows.space_out_submobjects(1.2)

        self.play(FadeInFromLarge(cij))
        sphere.add(circles)

        pc1i.add_updater(
            lambda c: c.become(self.get_projected_circle(c1i))
        )
        pc1j.add_updater(
            lambda c: c.become(self.get_projected_circle(c1j))
        )
        pcij.add_updater(
            lambda c: c.become(self.get_projected_circle(cij))
        )
        self.add(pcij)

        # About j-axis
        self.play(ShowCreation(arrows, run_time=3, rate_func=linear))
        self.wait(3)
        for x in range(2):
            y_axis.pieces.set_stroke(width=1)
            self.play(
                Rotate(sphere, 90 * DEGREES, axis=UP),
                run_time=4,
            )
            y_axis.pieces.set_stroke(width=0)
            self.wait(2)

        # About i axis
        self.move_camera(theta=-45 * DEGREES)
        self.play(Rotate(arrows, TAU / 4, axis=OUT))
        self.wait(2)
        for x in range(2):
            x_axis.pieces.set_stroke(width=1)
            self.play(
                Rotate(sphere, -90 * DEGREES, axis=RIGHT),
                run_time=4,
            )
            x_axis.pieces.set_stroke(width=0)
            self.wait(2)
        self.wait(2)

        # About real axis
        self.move_camera(
            theta=-135 * DEGREES,
            added_anims=[FadeOut(arrows)]
        )
        self.ambient_camera_rotation.rate = 0.01
        for x in range(2):
            x_axis.pieces.set_stroke(width=1)
            y_axis.pieces.set_stroke(width=1)
            self.play(
                Rotate(sphere, 90 * DEGREES, axis=OUT),
                run_time=4,
            )
            # x_axis.pieces.set_stroke(width=0)
            # y_axis.pieces.set_stroke(width=0)
            self.wait(2)

    #
    def get_circle(self, *colors):
        sphere = self.sphere
        circle = CheckeredCircle(colors=colors, n_pieces=48)
        circle.set_shade_in_3d(True)
        circle.match_width(sphere)
        if self.flat_view:
            circle[::2].fade(1)

        return circle

    def get_projected_circle(self, circle):
        result = circle.deepcopy()
        self.project_mobject(result)
        result[::2].fade(1)
        for sm in result:
            if sm.get_width() > FRAME_WIDTH:
                sm.fade(1)
            if sm.get_height() > FRAME_HEIGHT:
                sm.fade(1)
        return result


class ReferernceSpheresFelixView(ShowRotationsJustWithReferenceCircles):
    CONFIG = {
        "flat_view": True,
        "lift_labels": False,
    }

    def add_parts(self, **kwargs):
        ShowRotationsJustWithReferenceCircles.add_parts(self, **kwargs)
        one = TexMobject("1")
        one.next_to(ORIGIN, DR, SMALL_BUFF)
        self.add(one)

    def get_default_camera_position(self):
        return {}

    def move_camera(self, **kwargs):
        kwargs["phi"] = 0
        kwargs["theta"] = -90 * DEGREES
        ShowRotationsJustWithReferenceCircles.move_camera(self, **kwargs)

    def begin_ambient_camera_rotation(self, rate):
        self.ambient_camera_rotation = VectorizedPoint()

    def capture_mobjects_in_camera(self, mobjects, **kwargs):
        mobs_on_xy = [
            sm
            for sm in self.camera.extract_mobject_family_members(
                mobjects, only_those_with_points=True
            )
            if abs(sm.get_center()[2]) < 0.001
        ]
        return Scene.capture_mobjects_in_camera(self, mobs_on_xy, **kwargs)


class IntroduceQuaternions(Scene):
    def construct(self):
        self.compare_three_number_systems()
        self.mention_four_perpendicular_axes()
        self.bring_back_complex()
        self.show_components_of_quaternion()

    def compare_three_number_systems(self):
        numbers = self.get_example_numbers()
        labels = VGroup(
            TextMobject("Complex number"),
            TextMobject("Not-actually-a-number-system 3d number"),
            TextMobject("Quaternion"),
        )

        for number, label in zip(numbers, labels):
            label.next_to(number, UP, aligned_edge=LEFT)

            self.play(
                FadeInFromDown(number),
                Write(label),
            )
            self.play(ShowCreationThenFadeAround(
                number[2:],
                surrounding_rectangle_config={"color": BLUE}
            ))
            self.wait()

        shift_size = FRAME_HEIGHT / 2 - labels[2].get_top()[1] - MED_LARGE_BUFF
        self.play(
            numbers.shift, shift_size * UP,
            labels.shift, shift_size * UP,
        )

        self.numbers = numbers
        self.labels = labels

    def mention_four_perpendicular_axes(self):
        number = self.numbers[2]
        three_axes = VGroup(*[
            self.get_simple_axes(label, color)
            for label, color in zip(
                ["i", "j", "k"],
                [GREEN, RED, BLUE],
            )
        ])
        three_axes.arrange(RIGHT, buff=LARGE_BUFF)
        three_axes.next_to(number, DOWN, LARGE_BUFF)

        self.play(LaggedStartMap(FadeInFromLarge, three_axes))
        self.wait(2)

        self.three_axes = three_axes

    def bring_back_complex(self):
        numbers = self.numbers
        labels = self.labels
        numbers[0].move_to(numbers[1], LEFT)
        labels[0].move_to(labels[1], LEFT)
        numbers.remove(numbers[1])
        labels.remove(labels[1])

        group = VGroup(numbers, labels)
        self.play(
            group.to_edge, UP,
            FadeOutAndShift(self.three_axes, DOWN)
        )
        self.wait()

    def show_components_of_quaternion(self):
        quat = self.numbers[-1]
        real_part = quat[0]
        imag_part = quat[2:]
        real_brace = Brace(real_part, DOWN)
        imag_brace = Brace(imag_part, DOWN)
        real_word = TextMobject("Real \\\\ part")
        imag_word = TextMobject("Imaginary \\\\ part")
        scalar_word = TextMobject("Scalar \\\\ part")
        vector_word = TextMobject("``Vector'' \\\\ part")
        for word in real_word, scalar_word:
            word.next_to(real_brace, DOWN, SMALL_BUFF)
        for word in imag_word, vector_word:
            word.next_to(imag_brace, DOWN, SMALL_BUFF)
        braces = VGroup(real_brace, imag_brace)
        VGroup(scalar_word, vector_word).set_color(YELLOW)

        self.play(
            LaggedStartMap(GrowFromCenter, braces),
            LaggedStartMap(
                FadeInFrom, VGroup(real_word, imag_word),
                lambda m: (m, UP)
            )
        )
        self.wait()
        self.play(
            FadeOutAndShift(real_word, DOWN),
            FadeInFrom(scalar_word, DOWN),
        )
        self.wait(2)
        self.play(ChangeDecimalToValue(real_part, 0))
        self.wait()
        self.play(
            FadeOutAndShift(imag_word, DOWN),
            FadeInFrom(vector_word, DOWN)
        )
        self.wait(2)

    #
    def get_example_numbers(self):
        number_2d = VGroup(
            DecimalNumber(3.14),
            TexMobject("+"),
            DecimalNumber(1.59),
            TexMobject("i")
        )
        number_3d = VGroup(
            DecimalNumber(2.65),
            TexMobject("+"),
            DecimalNumber(3.58),
            TexMobject("i"),
            TexMobject("+"),
            DecimalNumber(9.79),
            TexMobject("j"),
        )
        number_4d = VGroup(
            DecimalNumber(3.23),
            TexMobject("+"),
            DecimalNumber(8.46),
            TexMobject("i"),
            TexMobject("+"),
            DecimalNumber(2.64),
            TexMobject("j"),
            TexMobject("+"),
            DecimalNumber(3.38),
            TexMobject("k"),
        )
        numbers = VGroup(number_2d, number_3d, number_4d)
        for number in numbers:
            number.arrange(RIGHT, buff=SMALL_BUFF)
            for part in number:
                if isinstance(part, TexMobject):
                    # part.set_color_by_tex_to_color_map({
                    #     "i": GREEN,
                    #     "j": RED,
                    #     "k": BLUE,
                    # })
                    if part.get_tex_string() == "j":
                        part.shift(0.5 * SMALL_BUFF * DL)
            number[2].set_color(GREEN)
            if len(number) > 5:
                number[5].set_color(RED)
            if len(number) > 8:
                number[8].set_color(BLUE)
        numbers.arrange(
            DOWN, buff=2, aligned_edge=LEFT
        )
        numbers.center()
        numbers.shift(LEFT)
        return numbers

    def get_simple_axes(self, label, color):
        axes = Axes(
            x_min=-2.5,
            x_max=2.5,
            y_min=-2.5,
            y_max=2.5,
        )
        axes.set_height(2.5)
        label_mob = TexMobject(label)
        label_mob.set_color(color)
        label_mob.next_to(axes.coords_to_point(0, 1.5), RIGHT, SMALL_BUFF)
        reals_label_mob = TextMobject("Reals")
        reals_label_mob.next_to(
            axes.coords_to_point(1, 0), DR, SMALL_BUFF
        )
        axes.add(label_mob, reals_label_mob)
        return axes


class SimpleImaginaryQuaternionAxes(SpecialThreeDScene):
    def construct(self):
        self.three_d_axes_config.update({
            "axis_config": {"unit_size": 2},
            "x_min": -2,
            "x_max": 2,
            "y_min": -2,
            "y_max": 2,
            "z_min": -1.25,
            "z_max": 1.25,
        })
        axes = self.get_axes()
        labels = VGroup(*[
            TexMobject(tex).set_color(color)
            for tex, color in zip(
                ["i", "j", "k"],
                [GREEN, RED, BLUE]
            )
        ])
        labels[0].next_to(axes.coords_to_point(1, 0, 0), DOWN + IN, SMALL_BUFF)
        labels[1].next_to(axes.coords_to_point(0, 1, 0), RIGHT, SMALL_BUFF)
        labels[2].next_to(axes.coords_to_point(0, 0, 1), RIGHT, SMALL_BUFF)

        self.add(axes)
        self.add(labels)
        for label in labels:
            self.add_fixed_orientation_mobjects(label)

        self.move_camera(**self.get_default_camera_position())
        self.begin_ambient_camera_rotation(rate=0.05)
        self.wait(15)


class ShowDotProductCrossProductFromOfQMult(Scene):
    def construct(self):
        v_tex = "\\vec{\\textbf{v}}"
        product = TexMobject(
            "(", "w_1", "+",
            "x_1", "i", "+", "y_1", "j", "+", "z_1", "k", ")"
            "(", "w_2", "+",
            "x_2", "i", "+", "y_2", "j", "+", "z_2", "k", ")",
            "=",
            "(w_1", ",", v_tex + "_1", ")",
            "(w_2", ",", v_tex + "_2", ")",
            "="
        )
        product.set_width(FRAME_WIDTH - 1)

        i1 = product.index_of_part_by_tex("x_1")
        i2 = product.index_of_part_by_tex(")")
        i3 = product.index_of_part_by_tex("x_2")
        i4 = product.index_of_part_by_tex("z_2") + 2
        vector_parts = [product[i1:i2], product[i3:i4]]

        vector_defs = VGroup()
        braces = VGroup()
        for i, vp in zip(it.count(1), vector_parts):
            brace = Brace(vp, UP)
            vector = Matrix([
                ["x_" + str(i)],
                ["y_" + str(i)],
                ["z_" + str(i)],
            ])
            colors = [GREEN, RED, BLUE]
            for mob, color in zip(vector.get_entries(), colors):
                mob.set_color(color)
            group = VGroup(
                TexMobject("{}_{} = ".format(v_tex, i)),
                vector,
            )
            group.arrange(RIGHT, SMALL_BUFF)
            group.next_to(brace, UP)

            braces.add(brace)
            vector_defs.add(group)

        result = TexMobject(
            "\\left(", "w_1", "w_2",
            "-", v_tex + "_1", "\\cdot", v_tex, "_2", ",\\,",
            "w_1", v_tex + "_2", "+", "w_2", v_tex + "_1",
            "+", "{}_1 \\times {}_2".format(v_tex, v_tex),
            "\\right)"
        )
        result.match_width(product)
        result.next_to(product, DOWN, LARGE_BUFF)
        for mob in product, result:
            mob.set_color_by_tex_to_color_map({
                "w": YELLOW,
                "x": GREEN,
                "y": RED,
                "z": BLUE,
            })
            mob.set_color_by_tex(v_tex, WHITE)

        self.add(product)
        self.add(braces)
        self.add(vector_defs)
        self.play(LaggedStartMap(FadeInFromLarge, result))
        self.wait()


class ShowComplexMagnitude(ShowComplexMultiplicationExamples):
    def construct(self):
        self.add_planes()
        plane = self.plane
        tex_to_color_map = {
            "a": YELLOW,
            "b": GREEN,
        }

        z = complex(3, 2)
        z_point = plane.number_to_point(z)
        z_dot = Dot(z_point)
        z_dot.set_color(PINK)
        z_line = Line(plane.number_to_point(0), z_point)
        z_line.set_stroke(WHITE, 2)
        z_label = TexMobject(
            "z", "=", "a", "+", "b", "i",
            tex_to_color_map=tex_to_color_map
        )
        z_label.add_background_rectangle()
        z_label.next_to(z_dot, UR, buff=SMALL_BUFF)
        z_norm_label = TexMobject("||z||")
        z_norm_label.add_background_rectangle()
        z_norm_label.next_to(ORIGIN, UP, SMALL_BUFF)
        z_norm_label.rotate(z_line.get_angle(), about_point=ORIGIN)
        z_norm_label.shift(z_line.get_center())

        h_line = Line(
            plane.number_to_point(0),
            plane.number_to_point(z.real),
            stroke_color=YELLOW,
            stroke_width=5,
        )
        v_line = Line(
            plane.number_to_point(z.real),
            plane.number_to_point(z),
            stroke_color=GREEN,
            stroke_width=5,
        )

        z_norm_equation = TexMobject(
            "||z||", "=", "\\sqrt", "{a^2", "+", "b^2", "}",
            tex_to_color_map=tex_to_color_map
        )
        z_norm_equation.set_background_stroke(width=0)
        z_norm_equation.add_background_rectangle()
        z_norm_equation.next_to(z_label, UP)

        self.add(z_line, h_line, v_line, z_dot, z_label)
        self.play(ShowCreation(z_line))
        self.play(FadeInFromDown(z_norm_label))
        self.wait()
        self.play(
            FadeIn(z_norm_equation[0]),
            FadeIn(z_norm_equation[2:]),
            TransformFromCopy(
                z_norm_label[1:],
                VGroup(z_norm_equation[1]),
            ),
        )
        self.wait()


class BreakUpQuaternionMultiplicationInParts(Scene):
    def construct(self):
        q1_color = MAROON_B
        q2_color = YELLOW

        product = TexMobject(
            "q_1", "\\cdot", "q_2", "=",
            "\\left(", "{q_1", "\\over", "||", "q_1", "||}", "\\right)",
            "||", "q_1", "||", "\\cdot", "q_2",
        )
        product.set_color_by_tex("q_1", q1_color)
        product.set_color_by_tex("q_2", q2_color)
        lhs = product[:3]
        scale_part = product[-5:]
        rotate_part = product[4:-5]
        lhs_rect = SurroundingRectangle(lhs)
        lhs_rect.set_color(YELLOW)
        lhs_words = TextMobject("Quaternion \\\\ multiplication")
        lhs_words.next_to(lhs_rect, UP, LARGE_BUFF)
        scale_brace = Brace(scale_part, UP)
        rotate_brace = Brace(rotate_part, DOWN)
        scale_words = TextMobject("Scale", "$q_2$")
        scale_words.set_color_by_tex("q_2", q2_color)
        scale_words.next_to(scale_brace, UP)
        rotate_words = TextMobject("Apply special \\\\ 4d rotation")
        rotate_words.next_to(rotate_brace, DOWN)

        norm_equation = TexMobject(
            "||", "q_1", "||", "=",
            "||", "w_1", "+",
            "x_1", "i", "+",
            "y_1", "j", "+",
            "z_1", "k", "||", "=",
            "\\sqrt",
            "{w_1^2", "+",
            "x_1^2", "+",
            "y_1^2", "+",
            "z_1^2", "}",
        )
        # norm_equation.set_color_by_tex_to_color_map({
        #     "w": YELLOW,
        #     "x": GREEN,
        #     "y": RED,
        #     "z": BLUE,
        # })
        norm_equation.set_color_by_tex("q_1", q1_color)
        norm_equation.to_edge(UP)
        norm_equation.set_background_stroke(width=0)

        line1 = Line(ORIGIN, 0.5 * LEFT + 3 * UP)
        line2 = Line(ORIGIN, UR)
        zero_dot = Dot()
        zero_label = TexMobject("0")
        zero_label.next_to(zero_dot, DOWN, SMALL_BUFF)
        q1_dot = Dot(line1.get_end())
        q2_dot = Dot(line2.get_end())
        q1_label = TexMobject("q_1").next_to(q1_dot, UP, SMALL_BUFF)
        q2_label = TexMobject("q_2").next_to(q2_dot, UR, SMALL_BUFF)
        VGroup(q1_dot, q1_label).set_color(q1_color)
        VGroup(q2_dot, q2_label).set_color(q2_color)
        dot_group = VGroup(
            line1, line2, q1_dot, q2_dot, q1_label, q2_label,
            zero_dot, zero_label,
        )
        dot_group.set_height(3)
        dot_group.center()
        dot_group.to_edge(LEFT)

        q1_dot.add_updater(lambda d: d.move_to(line1.get_end()))
        q1_label.add_updater(lambda l: l.next_to(q1_dot, UP, SMALL_BUFF))
        q2_dot.add_updater(lambda d: d.move_to(line2.get_end()))
        q2_label.add_updater(lambda l: l.next_to(q2_dot, UR, SMALL_BUFF))

        self.add(norm_equation)
        self.wait()
        self.play(
            FadeInFromDown(lhs),
            Write(dot_group),
        )
        self.add(*dot_group)
        self.add(
            VGroup(line2, q2_dot, q2_label).copy().fade(0.5)
        )
        self.play(
            ShowCreation(lhs_rect),
            FadeIn(lhs_words)
        )
        self.play(FadeOut(lhs_rect))
        self.wait()
        self.play(
            TransformFromCopy(lhs, product[3:]),
            # FadeOut(lhs_words)
        )
        self.play(
            GrowFromCenter(scale_brace),
            Write(scale_words),
        )
        self.play(
            line2.scale, 2, {"about_point": line2.get_start()}
        )
        self.wait()
        self.play(
            GrowFromCenter(rotate_brace),
            FadeInFrom(rotate_words, UP),
        )
        self.play(
            Rotate(
                line2, -line1.get_angle(),
                about_point=line2.get_start(),
                run_time=3
            )
        )
        self.wait()

        # Ask
        randy = Randolph(height=2)
        randy.flip()
        randy.next_to(rotate_words, RIGHT)
        randy.to_edge(DOWN)
        q_marks = TexMobject("???")
        random.shuffle(q_marks.submobjects)
        q_marks.next_to(randy, UP)
        self.play(
            FadeIn(randy)
        )
        self.play(
            randy.change, "confused", rotate_words,
            ShowCreationThenFadeAround(rotate_words),
        )
        self.play(LaggedStartMap(
            FadeInFrom, q_marks,
            lambda m: (m, LEFT),
            lag_ratio=0.8,
        ))
        self.play(Blink(randy))
        self.wait(2)


class SphereProjectionsWrapper(Scene):
    def construct(self):
        rect_rows = VGroup(*[
            VGroup(*[
                ScreenRectangle(height=3)
                for x in range(3)
            ]).arrange(RIGHT, buff=LARGE_BUFF)
            for y in range(2)
        ]).arrange(DOWN, buff=2 * LARGE_BUFF)
        rect_rows.set_width(FRAME_WIDTH - 1)

        sphere_labels = VGroup(
            TextMobject("Circle in 2d"),
            TextMobject("Sphere in 3d"),
            TextMobject("Hypersphere in 4d"),
        )
        for label, rect in zip(sphere_labels, rect_rows[0]):
            label.next_to(rect, UP)

        projected_labels = VGroup(
            TextMobject("Sterographically projected \\\\ circle in 1d"),
            TextMobject("Sterographically projected \\\\ sphere in 2d"),
            TextMobject("Sterographically projected \\\\ hypersphere in 3d"),
        )
        for label, rect in zip(projected_labels, rect_rows[1]):
            label.match_width(rect)
            label.next_to(rect, UP)

        q_marks = TexMobject("???")
        q_marks.scale(2)
        q_marks.move_to(rect_rows[0][2])

        self.add(rect_rows)
        for l1, l2 in zip(sphere_labels, projected_labels):
            added_anims = []
            if l1 is sphere_labels[2]:
                added_anims.append(FadeIn(q_marks))
            self.play(FadeIn(l1), *added_anims)
            self.play(FadeIn(l2))
            self.wait()


class HypersphereStereographicProjection(SpecialThreeDScene):
    CONFIG = {
        # "fancy_dot": False,
        "fancy_dot": True,
        "initial_quaternion_sample_values": [
            [0, 1, 0, 0],
            [-1, 1, 0, 0],
            [0, 0, 1, 1],
            [0, 1, -1, 1],
        ],
        "unit_labels_scale_factor": 1,
    }

    def construct(self):
        self.setup_axes()
        self.introduce_quaternion_label()
        self.show_one()
        self.show_unit_sphere()
        self.show_quaternions_with_nonzero_real_part()
        self.emphasize_only_units()
        self.show_reference_spheres()

    def setup_axes(self):
        axes = self.axes = self.get_axes()
        axes.set_stroke(width=1)
        self.add(axes)
        self.move_camera(
            **self.get_default_camera_position(),
            run_time=0
        )
        self.begin_ambient_camera_rotation(rate=0.01)

    def introduce_quaternion_label(self):
        q_tracker = QuaternionTracker()
        coords = [
            DecimalNumber(0, color=color, include_sign=sign, edge_to_fix=RIGHT)
            for color, sign in zip(
                [YELLOW, GREEN, RED, BLUE],
                [False, True, True, True],
            )
        ]
        label = VGroup(
            coords[0], VectorizedPoint(),
            coords[1], TexMobject("i"),
            coords[2], TexMobject("j"),
            coords[3], TexMobject("k"),
        )
        label.arrange(RIGHT, buff=SMALL_BUFF)
        label.to_corner(UR)

        def update_label(label):
            self.remove_fixed_in_frame_mobjects(label)
            quat = q_tracker.get_value()
            for value, coord in zip(quat, label[::2]):
                coord.set_value(value)
            self.add_fixed_in_frame_mobjects(label)
            return label

        label.add_updater(update_label)
        self.pink_dot_label = label

        def get_pq_point():
            point = self.project_quaternion(q_tracker.get_value())
            if get_norm(point) > 100:
                return point * 100 / get_norm(point)
            return point

        pq_dot = self.get_dot()
        pq_dot.add_updater(lambda d: d.move_to(get_pq_point()))
        dot_radius = pq_dot.get_width() / 2

        def get_pq_line():
            point = get_pq_point()
            norm = get_norm(point)
            origin = self.axes.coords_to_point(0, 0, 0)
            if norm > dot_radius:
                point -= origin
                point *= (norm - dot_radius) / norm
                point += origin
            result = Line(origin, point)
            result.set_stroke(width=1)
            return result

        pq_line = get_pq_line()
        pq_line.add_updater(lambda cl: cl.become(get_pq_line()))

        self.add(q_tracker, label, pq_line, pq_dot)

        self.q_tracker = q_tracker
        self.q_label = label
        self.pq_line = pq_line
        self.pq_dot = pq_dot

        rect = SurroundingRectangle(label, color=WHITE)
        self.add_fixed_in_frame_mobjects(rect)
        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))
        self.remove_fixed_orientation_mobjects(rect)

        for value in self.initial_quaternion_sample_values:
            self.set_quat(value)
            self.wait()

    def show_one(self):
        q_tracker = self.q_tracker

        one_label = TexMobject("1")
        one_label.rotate(TAU / 4, RIGHT)
        one_label.next_to(ORIGIN, IN + RIGHT, SMALL_BUFF)
        one_label.set_shade_in_3d(True)
        one_label.set_background_stroke(width=0)

        self.play(
            ApplyMethod(
                q_tracker.set_value, [1, 0, 0, 0],
                run_time=2
            ),
            FadeInFromDown(one_label)
        )
        self.wait(4)

    def show_unit_sphere(self):
        sphere = self.sphere = self.get_projected_sphere(
            quaternion=[1, 0, 0, 0], null_axis=0,
            solid=False,
            stroke_width=0.5
        )
        self.specially_color_sphere(sphere)
        labels = self.get_unit_labels()
        labels.remove(labels[3])

        real_part = self.q_label[0]
        brace = Brace(real_part, DOWN)
        words = TextMobject("Real part zero")
        words.next_to(brace, DOWN, SMALL_BUFF, LEFT)

        self.play(Write(sphere))
        self.play(LaggedStartMap(
            FadeInFrom, labels,
            lambda m: (m, IN)
        ))
        self.add_fixed_in_frame_mobjects(brace, words)
        self.set_quat(
            [0, 1, 0, 0],
            added_anims=[
                GrowFromCenter(brace),
                Write(words),
            ]
        )
        self.wait()
        self.set_quat([0, 1, -1, 1])
        self.wait(2)
        self.set_quat([0, -1, -1, 1])
        self.wait(2)
        self.set_quat([0, 0, 0, 1])
        self.wait(2)
        self.set_quat([0, 0, -1, 0])
        self.wait(2)
        self.set_quat([0, 1, 0, 0])
        self.wait(2)
        self.play(FadeOut(words))
        self.remove_fixed_in_frame_mobjects(words)

        self.real_part_brace = brace

    def show_quaternions_with_nonzero_real_part(self):
        # Positive real part
        self.set_quat(
            [1, 1, 2, 0],
            added_anims=[
                ApplyMethod(
                    self.sphere.copy().scale, 0,
                    remover=True
                )
            ]
        )
        self.wait(2)
        self.set_quat([4, 0, -1, -1])
        self.wait(2)
        # Negative real part
        self.set_quat(
            [-1, 1, 2, 0],
            added_anims=[
                ApplyFunction(
                    lambda s: s.scale(10).fade(1),
                    self.sphere.copy(),
                    remover=True
                )
            ]
        )
        self.wait(2)
        self.set_quat([-2, 0, -1, 1])
        self.wait(2)
        self.set_quat([-1, 1, 0, 0])
        self.move_camera(theta=-160 * DEGREES, run_time=3)
        self.set_quat([-1, 0.001, 0, 0])
        self.wait(2)

    def emphasize_only_units(self):
        q_label = self.q_label
        brace = self.real_part_brace

        brace.target = Brace(q_label, DOWN, buff=SMALL_BUFF)
        words = TextMobject(
            "Only those where \\\\",
            "$w^2 + x^2 + y^2 + z^2 = 1$"
        )
        words.next_to(brace.target, DOWN, SMALL_BUFF)

        self.add_fixed_in_frame_mobjects(words)
        self.play(
            MoveToTarget(brace),
            Write(words)
        )
        self.set_quat([1, 1, 1, 1])
        self.wait(2)
        self.set_quat([1, 1, -1, 1])
        self.wait(2)
        self.set_quat([-1, 1, -1, 1])
        self.wait(8)
        self.play(FadeOut(brace), FadeOut(words))
        self.remove_fixed_in_frame_mobjects(brace, words)

    # TODO
    def show_reference_spheres(self):
        sphere = self.sphere
        self.move_camera(
            phi=60 * DEGREES,
            theta=-150 * DEGREES,
            added_anims=[
                self.q_tracker.set_value, [1, 0, 0, 0]
            ]
        )
        sphere_ijk = self.get_projected_sphere(null_axis=0)
        sphere_1jk = self.get_projected_sphere(null_axis=1)
        sphere_1ik = self.get_projected_sphere(null_axis=2)
        sphere_1ij = self.get_projected_sphere(null_axis=3)
        circle = StereoProjectedCircleFromHypersphere(axes=[0, 1])

        circle_words = TextMobject(
            "Circle through\\\\", "$1, i, -1, -i$"
        )
        sphere_1ij_words = TextMobject(
            "Sphere through\\\\", "$1, i, j, -1, -i, -j$"
        )
        sphere_1jk_words = TextMobject(
            "Sphere through\\\\", "$1, j, k, -1, -j, -k$"
        )
        sphere_1ik_words = TextMobject(
            "Sphere through\\\\", "$1, i, k, -1, -i, -k$"
        )
        for words in [circle_words, sphere_1ij_words, sphere_1jk_words, sphere_1ik_words]:
            words.to_corner(UL)
            self.add_fixed_in_frame_mobjects(words)

        self.play(
            ShowCreation(circle),
            Write(circle_words),
        )
        self.set_quat([0, 1, 0, 0])
        self.set_quat([1, 0, 0, 0])
        self.remove(sphere)
        sphere_ijk.match_style(sphere)
        self.add(sphere_ijk)

        # Show xy plane
        self.play(
            FadeOutAndShift(circle_words, DOWN),
            FadeInFromDown(sphere_1ij_words),
            FadeOut(circle),
            sphere_ijk.set_stroke, {"width": 0.0}
        )
        self.play(Write(sphere_1ij))
        self.wait(10)
        return

        # Show yz plane
        self.play(
            FadeOutAndShift(sphere_1ij_words, DOWN),
            FadeInFromDown(sphere_1jk_words),
            sphere_1ij.set_fill, BLUE_E, 0.25,
            sphere_1ij.set_stroke, {"width": 0.0},
            Write(sphere_1jk)
        )
        self.wait(5)

        # Show xz plane
        self.play(
            FadeOutAndShift(sphere_1jk_words, DOWN),
            FadeInFromDown(sphere_1ik_words),
            sphere_1jk.set_fill, GREEN_E, 0.25,
            sphere_1jk.set_stroke, {"width": 0.0},
            Write(sphere_1ik)
        )
        self.wait(5)
        self.play(
            sphere_1ik.set_fill, RED_E, 0.25,
            sphere_1ik.set_stroke, {"width": 0.0},
            FadeOut(sphere_1ik_words)
        )

        # Start applying quaternion multiplication
        kwargs = {"solid": False, "stroke_width": 0}
        sphere_ijk.add_updater(
            lambda s: s.become(self.get_projected_sphere(0, **kwargs))
        )
        sphere_1jk.add_updater(
            lambda s: s.become(self.get_projected_sphere(1, **kwargs))
        )
        sphere_1ik.add_updater(
            lambda s: s.become(self.get_projected_sphere(2, **kwargs))
        )
        sphere_1ij.add_updater(
            lambda s: s.become(self.get_projected_sphere(3, **kwargs))
        )

        self.set_quat([0, 1, 1, 1])

    #
    def project_quaternion(self, quat):
        return self.axes.coords_to_point(
            *stereo_project_point(quat, axis=0, r=1)[1:]
        )

    def get_dot(self):
        if self.fancy_dot:
            sphere = self.get_sphere()
            sphere.set_width(0.2)
            sphere.set_stroke(width=0)
            sphere.set_fill(PINK)
            return sphere
        else:
            return VGroup(
                Dot(color=PINK),
                Dot(color=PINK).rotate(TAU / 4, RIGHT),
            )

    def get_unit_labels(self):
        c2p = self.axes.coords_to_point
        tex_coords_vects = [
            ("i", [1, 0, 0], IN + RIGHT),
            ("-i", [-1, 0, 0], IN + LEFT),
            ("j", [0, 1, 0], UP + OUT + RIGHT),
            ("-j", [0, -1, 0], RIGHT + DOWN),
            ("k", [0, 0, 1], OUT + RIGHT),
            ("-k", [0, 0, -1], IN + RIGHT),
        ]
        labels = VGroup()
        for tex, coords, vect in tex_coords_vects:
            label = TexMobject(tex)
            label.scale(self.unit_labels_scale_factor)
            label.rotate(90 * DEGREES, RIGHT)
            label.next_to(c2p(*coords), vect, SMALL_BUFF)
            labels.add(label)
        labels.set_shade_in_3d(True)
        labels.set_background_stroke(width=0)
        return labels

    def set_quat(self, value, run_time=3, added_anims=None):
        if added_anims is None:
            added_anims = []
        self.play(
            self.q_tracker.set_value, value,
            *added_anims,
            run_time=run_time
        )

    def get_projected_sphere(self, null_axis, quaternion=None, solid=True, **kwargs):
        if quaternion is None:
            quaternion = self.get_multiplier()
        axes_to_color = {
            0: interpolate_color(YELLOW, BLACK, 0.5),
            1: GREEN_E,
            2: RED_D,
            3: BLUE_E,
        }
        color = axes_to_color[null_axis]
        config = dict(self.sphere_config)
        config.update({
            "stroke_color": WHITE,
            "stroke_width": 0.5,
            "stroke_opacity": 0.5,
            "max_r": 24,
        })
        if solid:
            config.update({
                "checkerboard_colors": [
                    color, interpolate_color(color, BLACK, 0.5)
                ],
                "fill_opacity": 1,
            })
        else:
            config.update({
                "checkerboard_colors": [],
                "fill_color": color,
                "fill_opacity": 0.25,
            })
        config.update(kwargs)
        sphere = StereoProjectedSphereFromHypersphere(
            quaternion=quaternion,
            null_axis=null_axis,
            **config
        )
        sphere.set_shade_in_3d(True)
        return sphere

    def get_projected_circle(self, quaternion=None, **kwargs):
        if quaternion is None:
            quaternion = self.get_multiplier()
        return StereoProjectedCircleFromHypersphere(quaternion, **kwargs)

    def get_multiplier(self):
        return self.q_tracker.get_value()

    def specially_color_sphere(self, sphere):
        sphere.set_color_by_gradient(BLUE, GREEN, PINK)
        return sphere
        # for submob in sphere:
        #     u, v = submob.u1, submob.v1
        #     x = np.cos(v) * np.sin(u)
        #     y = np.sin(v) * np.sin(u)
        #     z = np.cos(u)
        #     # rgb = sum([
        #     #     (x**2) * hex_to_rgb(GREEN),
        #     #     (y**2) * hex_to_rgb(RED),
        #     #     (z**2) * hex_to_rgb(BLUE),
        #     # ])
        #     # clip_in_place(rgb, 0, 1)
        #     # color = rgb_to_hex(rgb)
        #     color = interpolate_color(BLUE, RED, ((z**3) + 1) / 2)
        #     submob.set_fill(color)
        # return sphere


class MissingLabels(Scene):
    def construct(self):
        labels = VGroup(
            TexMobject("i").move_to(UR),
            TexMobject("1").move_to(0.3 * DOWN),
            TexMobject("-i").move_to(DOWN + 1.2 * LEFT),
            TexMobject("-j").move_to(1.7 * RIGHT + 0.8 * DOWN),
        )
        labels.set_background_stroke(width=0)
        self.add(labels)


class RuleOfQuaternionMultiplicationOverlay(Scene):
    def construct(self):
        q_mob, times_mob, p_mob = q_times_p = TexMobject(
            "q", "\\cdot", "p"
        )
        q_times_p.scale(2)
        q_mob.set_color(MAROON_B)
        p_mob.set_color(YELLOW)
        q_arrow = Vector(DOWN, color=WHITE)
        q_arrow.next_to(q_mob, UP)
        p_arrow = Vector(UP, color=WHITE)
        p_arrow.next_to(p_mob, DOWN)

        q_words = TextMobject("Think of as\\\\ an action")
        q_words.next_to(q_arrow, UP)
        p_words = TextMobject("Think of as\\\\ a point")
        p_words.next_to(p_arrow, DOWN)

        i_mob = TexMobject("i")[0]
        i_mob.scale(2)
        i_mob.move_to(q_mob, RIGHT)
        i_mob.set_color(GREEN)

        self.add(q_times_p)
        self.play(
            FadeInFrom(q_words, UP),
            GrowArrow(q_arrow),
        )
        self.play(
            FadeInFrom(p_words, DOWN),
            GrowArrow(p_arrow),
        )
        self.wait()
        self.play(*map(FadeOut, [
            q_words, q_arrow,
            p_words, p_arrow,
        ]))
        self.play(
            FadeInFromDown(i_mob),
            FadeOutAndShift(q_mob, UP)
        )
        product = VGroup(i_mob, times_mob, p_mob)
        self.play(product.to_edge, UP)

        # Show i products
        underline = Line(LEFT, RIGHT)
        underline.set_width(product.get_width() + MED_SMALL_BUFF)
        underline.next_to(product, DOWN)

        kwargs = {
            "tex_to_color_map": {
                "i": GREEN,
                "j": RED,
                "k": BLUE
            }
        }
        i_products = VGroup(
            TexMobject("i", "\\cdot", "1", "=", "i", **kwargs),
            TexMobject("i", "\\cdot", "i", "=", "-1", **kwargs),
            TexMobject("i", "\\cdot", "j", "=", "k", **kwargs),
            TexMobject("i", "\\cdot", "k", "=", "-j", **kwargs),
        )
        i_products.scale(2)
        i_products.arrange(
            DOWN, buff=MED_LARGE_BUFF,
            aligned_edge=LEFT,
        )
        i_products.next_to(underline, DOWN, LARGE_BUFF)
        i_products.align_to(i_mob, LEFT)

        self.play(ShowCreation(underline))
        self.wait()
        for i_product in i_products:
            self.play(TransformFromCopy(
                product, i_product[:3]
            ))
            self.wait()
            self.play(TransformFromCopy(
                i_product[:3], i_product[3:],
            ))
            self.wait()

        rect = SurroundingRectangle(
            VGroup(product, i_products),
            buff=0.4
        )
        rect.set_stroke(WHITE, width=5)
        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))


class RuleOfQuaternionMultiplication(HypersphereStereographicProjection):
    CONFIG = {
        "fancy_dot": True,
        "initial_quaternion_sample_values": [],
    }

    def construct(self):
        self.setup_all_trackers()
        self.show_multiplication_by_i_on_circle_1i()
        self.show_multiplication_by_i_on_circle_jk()
        self.show_multiplication_by_i_on_ijk_sphere()

    def setup_all_trackers(self):
        self.setup_multiplier_tracker()
        self.force_skipping()
        self.setup_axes()
        self.introduce_quaternion_label()
        self.add_unit_labels()
        self.revert_to_original_skipping_status()

    def setup_multiplier_tracker(self):
        self.multiplier_tracker = QuaternionTracker([1, 0, 0, 0])
        self.multiplier_tracker.add_updater(
            lambda m: m.set_value(normalize(
                m.get_value(),
                fall_back=[1, 0, 0, 0]
            ))
        )
        self.add(self.multiplier_tracker)

    def add_unit_labels(self):
        labels = self.unit_labels = self.get_unit_labels()
        one_label = TexMobject("1")
        one_label.scale(self.unit_labels_scale_factor)
        one_label.set_shade_in_3d(True)
        one_label.rotate(90 * DEGREES, RIGHT)
        one_label.next_to(ORIGIN, IN + RIGHT, SMALL_BUFF)
        labels.add(one_label)
        self.add(labels)

    def show_multiplication_by_i_on_circle_1i(self):
        m_tracker = self.multiplier_tracker

        def get_circle_1i():
            return self.get_projected_circle(
                basis_vectors=[
                    [1, 0, 0, 0],
                    [1, 1, 0, 0],
                ],
                colors=[GREEN, YELLOW],
                quaternion=m_tracker.get_value(),
            )
        circle = get_circle_1i()
        arrows = self.get_i_circle_arrows()

        def set_to_q_value(mt):
            mt.set_value(self.q_tracker.get_value())

        self.play(ShowCreation(circle, run_time=2))
        self.play(LaggedStartMap(ShowCreation, arrows, lag_ratio=0.25))
        self.wait()
        circle.add_updater(lambda c: c.become(get_circle_1i()))
        m_tracker.add_updater(set_to_q_value)
        self.add(m_tracker)
        self.set_quat([0, 1, 0, 0])
        self.wait()
        self.set_quat([-1, 0.001, 0, 0])
        self.wait()
        self.q_tracker.set_value([-1, -0.001, 0, 0])
        self.set_quat([0, -1, 0, 0])
        self.wait()
        self.set_quat([1, 0, 0, 0])
        self.wait(3)
        self.play(FadeOut(arrows))

        m_tracker.remove_updater(set_to_q_value)
        self.circle_1i = circle

    def show_multiplication_by_i_on_circle_jk(self):
        def get_circle_jk():
            return self.get_projected_circle(
                basis_vectors=[
                    [0, 0, 1, 0],
                    [0, 0, 0, 1],
                ],
                colors=[RED, BLUE_E]
            )
        circle = get_circle_jk()
        arrows = self.get_jk_circle_arrows()
        m_tracker = self.multiplier_tracker
        q_tracker = self.q_tracker

        def set_q_to_mj(qt):
            qt.set_value(q_mult(
                m_tracker.get_value(), [0, 0, 1, 0]
            ))

        self.move_camera(theta=-50 * DEGREES)
        self.play(ShowCreation(circle, run_time=2))
        circle.add_updater(lambda c: c.become(get_circle_jk()))
        self.wait(10)
        self.stop_ambient_camera_rotation()
        self.begin_ambient_camera_rotation(rate=-0.01)
        self.play(*map(ShowCreation, arrows))
        self.wait()
        self.set_quat([0, 0, 1, 0], run_time=1)
        q_tracker.add_updater(set_q_to_mj, index=0)
        self.add(self.circle_1i)
        self.play(
            m_tracker.set_value, [0, 1, 0, 0],
            run_time=3
        )
        self.wait()
        self.play(
            m_tracker.set_value, [-1, 0.001, 0, 0],
            run_time=3
        )
        self.wait()
        m_tracker.set_value([-1, 0.001, 0, 0])
        self.play(
            m_tracker.set_value, [0, -1, 0, 0],
            run_time=3
        )
        self.wait()
        self.play(
            m_tracker.set_value, [1, 0, 0, 0],
            run_time=3
        )
        self.wait()
        q_tracker.remove_updater(set_q_to_mj)
        self.play(
            FadeOut(arrows),
            q_tracker.set_value, [1, 0, 0, 0],
        )
        self.wait(10)

        self.circle_jk = circle

    def show_multiplication_by_i_on_ijk_sphere(self):
        m_tracker = self.multiplier_tracker
        q_tracker = self.q_tracker
        m_tracker.add_updater(lambda m: m.set_value(q_tracker.get_value()))

        def get_sphere():
            result = self.get_projected_sphere(null_axis=0, solid=False)
            self.specially_color_sphere(result)
            return result

        sphere = get_sphere()

        self.play(Write(sphere))
        sphere.add_updater(lambda s: s.become(get_sphere()))

        self.set_quat([0, 1, 0, 0])
        self.wait()
        self.set_quat([-1, 0.001, 0, 0])
        self.wait()
        self.q_tracker.set_value([-1, -0.001, 0, 0])
        self.set_quat([0, -1, 0, 0])
        self.wait()
        self.set_quat([1, 0, 0, 0])
        self.wait(3)

    #
    def get_multiplier(self):
        return self.multiplier_tracker.get_value()

    def get_i_circle_arrows(self):
        c2p = self.axes.coords_to_point
        i_arrow = Arrow(
            ORIGIN, 2 * RIGHT, path_arc=-120 * DEGREES,
            buff=SMALL_BUFF,
        )
        neg_one_arrow = Arrow(
            ORIGIN, 5.5 * RIGHT + UP,
            path_arc=-30 * DEGREES,
            buff=SMALL_BUFF,
        )
        neg_i_arrow = Arrow(
            4.5 * LEFT + 1.5 * UP, ORIGIN,
            path_arc=-30 * DEGREES,
            buff=SMALL_BUFF,
        )
        one_arrow = i_arrow.copy()
        result = VGroup(i_arrow, neg_one_arrow, neg_i_arrow, one_arrow)
        for arrow in result:
            arrow.set_color(LIGHT_GREY)
            arrow.set_stroke(width=3)
            arrow.rotate(90 * DEGREES, RIGHT)
        i_arrow.next_to(c2p(0, 0, 0), OUT + RIGHT, SMALL_BUFF)
        neg_one_arrow.next_to(c2p(1, 0, 0), OUT + RIGHT, SMALL_BUFF)
        neg_i_arrow.next_to(c2p(-1, 0, 0), OUT + LEFT, SMALL_BUFF)
        one_arrow.next_to(c2p(0, 0, 0), OUT + LEFT, SMALL_BUFF)
        return result

    def get_jk_circle_arrows(self):
        arrow = Arrow(
            1.5 * RIGHT, 1.5 * UP,
            path_arc=90 * DEGREES,
            buff=SMALL_BUFF,
            use_rectangular_stem=False
        )
        arrow.set_color(LIGHT_GREY)
        arrow.set_stroke(width=3)
        arrows = VGroup(*[
            arrow.copy().rotate(angle, about_point=ORIGIN)
            for angle in np.arange(0, TAU, TAU / 4)
        ])
        arrows.rotate(90 * DEGREES, RIGHT)
        arrows.rotate(90 * DEGREES, OUT)
        return arrows


class ShowDistributionOfI(TeacherStudentsScene):
    def construct(self):
        tex_to_color_map = {
            "q": PINK,
            "w": YELLOW,
            "x": GREEN,
            "y": RED,
            "z": BLUE,
        }
        top_product = TexMobject(
            "q", "\\cdot", "\\left(",
            "w", "1", "+", "x", "i", "+", "y", "j", "+", "z", "k",
            "\\right)"
        )
        top_product.to_edge(UP)
        self.add(top_product)
        bottom_product = TexMobject(
            "w", "q", "\\cdot", "1",
            "+", "x", "q", "\\cdot", "i",
            "+", "y", "q", "\\cdot", "j",
            "+", "z", "q", "\\cdot", "k",
        )
        bottom_product.next_to(top_product, DOWN, MED_LARGE_BUFF)

        for product in [top_product, bottom_product]:
            for tex, color in tex_to_color_map.items():
                product.set_color_by_tex(tex, color, substring=False)

        self.student_says(
            "What does it do \\\\ to other quaternions?",
            target_mode="raise_left_hand"
        )
        self.change_student_modes(
            "pondering", "raise_left_hand", "erm",
            look_at_arg=top_product,
        )
        self.wait(2)
        self.play(
            self.teacher.change, "raise_right_hand",
            RemovePiCreatureBubble(self.students[1], target_mode="pondering"),
            *[
                TransformFromCopy(
                    top_product.get_parts_by_tex(tex, substring=False),
                    bottom_product.get_parts_by_tex(tex, substring=False),
                    run_time=2
                )
                for tex in ["1", "w", "x", "i", "y", "j", "z", "k", "+"]
            ]
        )
        self.play(*[
            TransformFromCopy(
                top_product.get_parts_by_tex(tex, substring=False),
                bottom_product.get_parts_by_tex(tex, substring=False),
                run_time=2
            )
            for tex in ["q", "\\cdot"]
        ])
        self.change_all_student_modes("thinking")
        self.wait(3)


class ComplexPlane135(Scene):
    def construct(self):
        plane = ComplexPlane(unit_size=2)
        plane.add_coordinates()
        for mob in plane.coordinate_labels:
            mob.scale(2, about_edge=UR)

        angle = 3 * TAU / 8
        circle = Circle(radius=2, color=YELLOW)
        arc = Arc(angle, radius=0.5)
        angle_label = Integer(0, unit="^\\circ")
        angle_label.next_to(arc.point_from_proportion(0.5), UR, SMALL_BUFF)
        line = Line(ORIGIN, 2 * RIGHT)

        point = circle.point_from_proportion(angle / TAU)
        dot = Dot(point, color=PINK)
        arrow = Vector(DR)
        arrow.next_to(dot, UL, SMALL_BUFF)
        arrow.match_color(dot)
        label = TexMobject("-\\frac{\\sqrt{2}}{2} + \\frac{\\sqrt{2}}{2} i")
        label.next_to(arrow.get_start(), UP, SMALL_BUFF)
        label.set_background_stroke(width=0)

        self.add(plane, circle, line, dot, label, arrow)
        self.play(
            Rotate(line, angle, about_point=ORIGIN),
            ShowCreation(arc),
            ChangeDecimalToValue(angle_label, 135),
            run_time=3
        )
        self.wait()


class ShowMultiplicationBy135Example(RuleOfQuaternionMultiplication):
    CONFIG = {
        "fancy_dot": True,
    }

    def construct(self):
        self.setup_all_trackers()
        self.add_circles()
        self.add_ijk_sphere()
        self.show_multiplication()

    def add_circles(self):
        self.circle_1i = self.add_auto_updating_circle(
            basis_vectors=[
                [1, 0, 0, 0],
                [0, 1, 0, 0],
            ],
            colors=[YELLOW, GREEN_E]
        )
        self.circle_jk = self.add_auto_updating_circle(
            basis_vectors=[
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ],
            colors=[RED, BLUE_E]

        )

    def add_auto_updating_circle(self, **circle_config):
        circle = self.get_projected_circle(**circle_config)
        circle.add_updater(
            lambda c: c.become(self.get_projected_circle(**circle_config))
        )
        self.add(circle)
        return circle

    def add_ijk_sphere(self):
        def get_sphere():
            result = self.get_projected_sphere(
                null_axis=0,
                solid=False,
                stroke_width=0.5,
                stroke_opacity=0.2,
                fill_opacity=0.2,
            )
            self.specially_color_sphere(result)
            return result
        sphere = get_sphere()
        sphere.add_updater(lambda s: s.become(get_sphere()))
        self.add(sphere)
        self.sphere = sphere

    def show_multiplication(self):
        m_tracker = self.multiplier_tracker

        quat = normalize(np.array([-1, 1, 0, 0]))
        point = self.project_quaternion(quat)
        arrow = Vector(DR)
        arrow.next_to(point, UL, MED_SMALL_BUFF)
        arrow.set_color(PINK)
        label = TexMobject(
            "-{\\sqrt{2} \\over 2}", "+",
            "{\\sqrt{2} \\over 2}", "i",
        )
        label.next_to(arrow.get_start(), UP)
        label.set_background_stroke(width=0)

        def get_one_point():
            return self.circle_1i[0].points[0]

        def get_j_point():
            return self.circle_jk[0].points[0]

        one_point = VectorizedPoint()
        one_point.add_updater(lambda v: v.set_location(get_one_point()))
        self.add(one_point)

        hand = Hand()
        hand.rotate(45 * DEGREES, RIGHT)
        hand.add_updater(
            lambda h: h.move_to(get_one_point(), LEFT)
        )

        j_line = Line(ORIGIN, get_j_point())
        moving_j_line = j_line.deepcopy()
        moving_j_line.add_updater(
            lambda m: m.put_start_and_end_on(ORIGIN, get_j_point())
        )

        self.add(j_line, moving_j_line)
        self.set_camera_orientation(
            phi=60 * DEGREES, theta=-70 * DEGREES
        )
        self.play(
            FadeInFromLarge(label, 3),
            GrowArrow(arrow)
        )
        self.set_quat(quat)
        self.wait(5)
        self.play(FadeInFromLarge(hand))
        self.add(m_tracker)
        for q in [quat, [1, 0, 0, 0], quat]:
            self.play(
                m_tracker.set_value, q,
                UpdateFromFunc(
                    m_tracker,
                    lambda m: m.set_value(normalize(m.get_value()))
                ),
                run_time=5
            )
            self.wait()


class JMultiplicationChart(Scene):
    def construct(self):
        # Largely copy-pasted....what are you gonna do about it?
        product = TexMobject("j", "\\cdot", "p")
        product[0].set_color(RED)
        product.scale(2)
        product.to_edge(UP)

        underline = Line(LEFT, RIGHT)
        underline.set_width(product.get_width() + MED_SMALL_BUFF)
        underline.next_to(product, DOWN)

        kwargs = {
            "tex_to_color_map": {
                "i": GREEN,
                "j": RED,
                "k": BLUE
            }
        }
        j_products = VGroup(
            TexMobject("j", "\\cdot", "1", "=", "j", **kwargs),
            TexMobject("j", "\\cdot", "j", "=", "-1", **kwargs),
            TexMobject("j", "\\cdot", "i", "=", "-k", **kwargs),
            TexMobject("j", "\\cdot", "k", "=", "i", **kwargs),
        )
        j_products.scale(2)
        j_products.arrange(
            DOWN, buff=MED_LARGE_BUFF,
            aligned_edge=LEFT,
        )
        j_products.next_to(underline, DOWN, LARGE_BUFF)
        j_products.align_to(product, LEFT)

        self.play(FadeInFromDown(product))
        self.play(ShowCreation(underline))
        self.wait()
        for j_product in j_products:
            self.play(TransformFromCopy(
                product, j_product[:3]
            ))
            self.wait()
            self.play(TransformFromCopy(
                j_product[:3], j_product[3:],
            ))
            self.wait()

        rect = SurroundingRectangle(
            VGroup(product, j_products),
            buff=MED_SMALL_BUFF
        )
        rect.set_stroke(WHITE, width=5)
        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))


class ShowJMultiplication(ShowMultiplicationBy135Example):
    CONFIG = {
        "fancy_dot": True,
        "run_time_per_rotation": 4,
    }

    def construct(self):
        self.setup_all_trackers()
        self.add_circles()
        self.add_ijk_sphere()
        self.show_multiplication()

    def add_circles(self):
        self.circle_1j = self.add_auto_updating_circle(
            basis_vectors=[
                [1, 0, 0, 0],
                [0, 0, 1, 0],
            ],
            colors=[YELLOW, RED]
        )
        self.circle_ik = self.add_auto_updating_circle(
            basis_vectors=[
                [0, 1, 0, 0],
                [0, 0, 0, 1],
            ],
            colors=[GREEN, BLUE_E]
        )

    def show_multiplication(self):
        self.set_camera_orientation(theta=-80 * DEGREES)

        q_tracker = self.q_tracker
        m_tracker = self.multiplier_tracker

        def normalize_tracker(t):
            t.set_value(normalize(t.get_value()))

        updates = [
            UpdateFromFunc(tracker, normalize_tracker)
            for tracker in (q_tracker, m_tracker)
        ]

        run_time = self.run_time_per_rotation
        self.play(
            m_tracker.set_value, [0, 0, 1, 0],
            q_tracker.set_value, [0, 0, 1, 0],
            *updates,
            run_time=run_time,
        )
        self.wait(2)
        self.play(
            m_tracker.set_value, [-1, 0, 1e-3, 0],
            q_tracker.set_value, [-1, 0, 1e-3, 0],
            *updates,
            run_time=run_time,
        )
        self.wait(2)

        # Show ik circle
        circle = self.circle_ik.deepcopy()
        circle.clear_updaters()
        self.play(FadeInFromLarge(circle, remover=True))
        m_tracker.set_value([-1, 0, 0, 0])
        q_tracker.set_value([0, 1, 0, 0])
        self.wait()
        self.play(
            m_tracker.set_value, [0, 0, -1, 0],
            q_tracker.set_value, [0, 0, 0, -1],
            *updates,
            run_time=run_time,
        )
        self.wait(2)
        self.play(
            m_tracker.set_value, [1, 0, -1e-3, 0],
            q_tracker.set_value, [0, -1, 0, 0],
            *updates,
            run_time=run_time,
        )
        self.wait(2)


class ShowArbitraryMultiplication(ShowMultiplicationBy135Example):
    CONFIG = {
        "fancy_dot": True,
        "run_time_per_rotation": 4,
        "special_quaternion": [-0.5, 0.5, 0.5, 0.5],
    }

    def construct(self):
        self.setup_all_trackers()
        self.add_circles()
        self.add_ijk_sphere()
        self.show_multiplication()

    def add_circles(self):
        self.circle1 = self.add_auto_updating_circle(
            basis_vectors=[
                [1, 0, 0, 0],
                [0, 1, 1, 1],
            ],
            colors=[YELLOW_E, YELLOW]
        )
        bv1 = normalize([0, -1, -1, 2])
        bv2 = [0] + list(normalize(np.cross([1, 1, 1], bv1[1:])))
        self.circle2 = self.add_auto_updating_circle(
            basis_vectors=[bv1, bv2],
            colors=[WHITE, GREY]
        )

    def show_multiplication(self):
        q_tracker = self.q_tracker
        m_tracker = self.multiplier_tracker
        run_time = self.run_time_per_rotation

        def normalize_tracker(t):
            t.set_value(normalize(t.get_value()))

        # for tracker in q_tracker, m_tracker:
        #     self.add(Mobject.add_updater(tracker, normalize_tracker))
        updates = [
            UpdateFromFunc(tracker, normalize_tracker)
            for tracker in (q_tracker, m_tracker)
        ]

        special_q = self.special_quaternion
        pq_point = self.project_quaternion(special_q)
        label = TextMobject("Some unit quaternion")
        label.set_color(PINK)
        label.rotate(90 * DEGREES, RIGHT)
        label.next_to(pq_point, IN + RIGHT, SMALL_BUFF)

        circle1, circle2 = self.circle1, self.circle2
        for circle in [circle1, circle2]:
            circle.tucked_away_updaters = circle.updaters
            circle.clear_updaters()
            self.remove(circle)

        hand = Hand()
        hand.rotate(90 * DEGREES, RIGHT)
        hand.move_to(ORIGIN, LEFT)
        hand.set_shade_in_3d(True)
        one_dot = self.get_dot()
        one_dot.set_color(YELLOW_E)
        one_dot.move_to(ORIGIN)
        one_dot.add_updater(
            lambda m: m.move_to(circle1[0].points[0])
        )
        self.add(one_dot)

        self.stop_ambient_camera_rotation()
        self.begin_ambient_camera_rotation(rate=0.02)
        self.set_quat(special_q)
        self.play(FadeInFrom(label, IN))
        self.wait(3)
        for circle in [circle1, circle2]:
            self.play(ShowCreation(circle, run_time=3))
            circle.updaters = circle.tucked_away_updaters
            self.wait(2)
        self.play(
            FadeInFrom(hand, 2 * IN + 2 * RIGHT),
            run_time=2
        )
        hand.add_updater(
            lambda h: h.move_to(circle1[0].points[0], LEFT)
        )

        for quat in [special_q, [1, 0, 0, 0], special_q]:
            self.play(
                m_tracker.set_value, special_q,
                *updates,
                run_time=run_time,
            )
            self.wait()


class MentionCommutativity(TeacherStudentsScene):
    def construct(self):
        kwargs = {
            "tex_to_color_map": {
                "q": MAROON_B,
                "p": YELLOW,
                "i": GREEN,
                "j": RED,
                "k": BLUE,
            }
        }
        general_eq = TexMobject("q \\cdot p \\ne p \\cdot q", **kwargs)
        general_eq.get_part_by_tex("\\ne").submobjects.reverse()
        ij_eq = TexMobject("i \\cdot j = k", **kwargs)
        ji_eq = TexMobject("j \\cdot i = -k", **kwargs)

        for mob in [general_eq, ij_eq, ji_eq]:
            mob.move_to(self.hold_up_spot, DOWN)

        words = TextMobject("Multiplication doesn't \\\\ commute")
        words.next_to(general_eq, UP, MED_LARGE_BUFF)
        words.shift_onto_screen()

        joke = TextMobject("Quaternions work from home")
        joke.scale(0.75)
        joke.to_corner(UL, MED_SMALL_BUFF)

        self.play(
            FadeInFromDown(general_eq),
            self.teacher.change, "raise_right_hand",
            self.get_student_changes("erm", "confused", "sassy")
        )
        self.play(FadeInFrom(words, RIGHT))
        self.wait(2)
        self.play(
            ReplacementTransform(words, joke),
            general_eq.shift, UP,
            FadeInFromDown(ij_eq),
            self.get_student_changes(*["pondering"] * 3)
        )
        self.look_at(self.screen)
        self.wait(3)
        self.play(
            FadeInFrom(ji_eq),
            LaggedStartMap(
                ApplyMethod, VGroup(ij_eq, general_eq),
                lambda m: (m.shift, UP),
                lag_ratio=0.8,
            )
        )
        self.look_at(self.screen)
        self.wait(5)


class RubuiksCubeOperations(SpecialThreeDScene):
    def construct(self):
        self.set_camera_orientation(**self.get_default_camera_position())
        self.begin_ambient_camera_rotation()
        cube = RubiksCube()
        cube.shift(2.5 * RIGHT)
        cube2 = cube.copy()

        self.add(cube)
        self.play(
            Rotate(cube.get_face(RIGHT), 90 * DEGREES, RIGHT),
            run_time=2
        )
        self.play(
            Rotate(cube.get_face(DOWN), 90 * DEGREES, UP),
            run_time=2
        )
        self.wait()
        self.play(
            cube.shift, 5 * LEFT,
            FadeIn(cube2)
        )
        self.play(
            Rotate(cube2.get_face(DOWN), 90 * DEGREES, UP),
            run_time=2
        )
        self.play(
            Rotate(cube2.get_face(RIGHT), 90 * DEGREES, RIGHT),
            run_time=2
        )
        self.wait(6)


class RotationsOfCube(SpecialThreeDScene):
    def construct(self):
        self.set_camera_orientation(**self.get_default_camera_position())
        self.begin_ambient_camera_rotation(0.0001)
        cube = RubiksCube()
        cube2 = cube.copy()
        axes = self.get_axes()
        axes.scale(0.75)

        label1 = TextMobject(
            "z-axis\\\\",
            "then x-axis"
        )
        label2 = TextMobject(
            "x-axis\\\\",
            "then z-axis"
        )
        for label in [label1, label2]:
            for part in label:
                part.add_background_rectangle()
            label.rotate(90 * DEGREES, RIGHT)
            label.move_to(3 * OUT + 0.5 * IN)

        self.add(axes, cube)
        self.play(
            Rotate(cube, 90 * DEGREES, OUT, run_time=2),
            FadeInFrom(label1[0], IN),
        )
        self.play(
            Rotate(cube, 90 * DEGREES, RIGHT, run_time=2),
            FadeInFrom(label1[1], IN),
        )
        self.wait()
        self.play(
            cube.shift, 5 * RIGHT,
            label1.shift, 5 * RIGHT,
            Write(cube2, run_time=1)
        )
        self.play(
            Rotate(cube2, 90 * DEGREES, RIGHT, run_time=2),
            FadeInFrom(label2[0], IN),
        )
        self.play(
            Rotate(cube2, 90 * DEGREES, OUT, run_time=2),
            FadeInFrom(label2[1], IN),
        )
        self.wait(5)


class OneFinalPoint(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("One final point!")
        self.change_student_modes("happy", "tease", "thinking")
        self.wait(3)


class MultiplicationFromTheRight(Scene):
    def construct(self):
        i, dot, j = product = TexMobject("i", "\\cdot", "j")
        product.set_height(1.5)
        product.to_edge(UP, buff=LARGE_BUFF)
        i.set_color(GREEN)
        j.set_color(RED)
        i_rect = SurroundingRectangle(i)
        j_rect = SurroundingRectangle(j)
        i_rect.match_height(j_rect, about_edge=UP, stretch=True)
        VGroup(i_rect, j_rect).set_color(WHITE)
        action_words = TextMobject("Think of as \\\\ an action")
        point_words = TextMobject("Think of as \\\\ a point")
        action_words.next_to(i_rect, LEFT)
        point_words.next_to(j_rect, RIGHT)

        arrow = Arrow(
            i.get_top(),
            j.get_top(),
            path_arc=-PI,
        )
        arrow.set_stroke(width=2)

        self.add(product)
        self.play(ShowCreation(arrow))
        self.play(
            FadeIn(i_rect),
            Write(action_words)
        )
        self.wait()
        self.play(
            FadeIn(j_rect),
            Write(point_words)
        )
        self.wait(2)
        self.play(arrow.flip)
        self.play(Swap(point_words, action_words))


class MultiplicationByJFromRight(ShowJMultiplication):
    def show_multiplication(self):
        self.set_camera_orientation(theta=-80 * DEGREES)

        q_tracker = self.q_tracker
        m_tracker = self.multiplier_tracker

        def normalize_tracker(t):
            t.set_value(normalize(t.get_value()))

        updates = [
            UpdateFromFunc(tracker, normalize_tracker)
            for tracker in (q_tracker, m_tracker)
        ]

        run_time = self.run_time_per_rotation

        m_values = [[1, 0, 0, 0]]
        q_values = [[0, 1, 0, 0]]
        for values in m_values, q_values:
            for x in range(4):
                values.append(
                    q_mult(values[-1], [0, 0, 1, 0])
                )

        for m_val, q_val in zip(m_values, q_values):
            self.play(
                m_tracker.set_value, m_val,
                q_tracker.set_value, q_val,
                *updates,
                run_time=run_time,
            )
            self.wait(2)

    def get_projected_sphere(self, *args, **kwargs):
        kwargs["multiply_from_right"] = True
        return ShowJMultiplication.get_projected_sphere(
            self, *args, **kwargs
        )

    def get_projected_circle(self, *args, **kwargs):
        kwargs["multiply_from_right"] = True
        return ShowJMultiplication.get_projected_circle(
            self, *args, **kwargs
        )


class HowQuaternionsRotate3dPoints(Scene):
    def construct(self):
        title = TextMobject(
            "Coming up:\\\\",
            "How quaternions act on 3d points"
        )
        title.to_edge(UP)

        expression = TexMobject(
            "q", "\\cdot", "p", "\\cdot", "q^{-1}"
        )
        expression.scale(2)
        expression.set_color_by_tex("q", PINK)
        expression.set_color_by_tex("p", YELLOW)

        right_arrow = Arrow(
            expression[0].get_top(),
            expression[2].get_top(),
            path_arc=-PI,
            color=WHITE,
        )
        right_arrow.set_stroke(width=4)
        left_arrow = right_arrow.copy()
        left_arrow.flip(about_point=expression[2].get_top())
        left_arrow.shift(SMALL_BUFF * RIGHT)

        self.add(title)
        self.play(Write(expression))
        self.play(ShowCreation(right_arrow))
        self.play(ShowCreation(left_arrow))
        self.wait()


class HoldUpQuanta(TeacherStudentsScene):
    def construct(self):
        logo = ImageMobject("Quanta logo")
        logo.set_width(6)
        logo.next_to(self.teacher, UR)
        logo.to_edge(RIGHT, buff=2)

        words = TextMobject("Associated quaternion post")
        words.to_edge(UP, buff=LARGE_BUFF)
        arrow = Arrow(logo.get_top(), words.get_bottom())

        self.play(
            FadeInFromDown(logo),
            self.teacher.change, "raise_right_hand"
        )
        self.change_all_student_modes("hooray")
        self.play(
            GrowArrow(arrow),
            GrowFromPoint(words, arrow.get_start())
        )
        self.wait(3)


class ShareWithFriends(PiCreatureScene):
    def construct(self):
        pi1, pi2 = self.pi_creatures

        self.pi_creature_says(
            pi1, "Come learn about \\\\ quaternions!",
            bubble_kwargs={
                "direction": LEFT,
                "width": 4,
                "height": 3,
            },
            target_mode="hooray",
            look_at_arg=pi2.eyes,
            added_anims=[
                ApplyMethod(
                    pi2.change, "confused",
                    run_time=1.5,
                    rate_func=squish_rate_func(smooth, 0.3, 1)
                )
            ]
        )
        bubble = ThoughtBubble(
            direction=RIGHT,
            width=4,
            height=4,
        )
        bubble.pin_to(pi2)
        bubble.write("What's that, some\\\\kind of particle?")
        bubble.resize_to_content()
        VGroup(bubble, bubble.content).shift_onto_screen(buff=SMALL_BUFF)
        self.play(
            pi2.look_at, pi1.eyes,
            pi1.look_at, pi2.eyes,
            ShowCreation(bubble),
            Write(bubble.content),
        )
        self.wait(1)
        self.play(
            RemovePiCreatureBubble(pi1, target_mode="raise_right_hand")
        )
        self.wait()

        time_words = TextMobject("Oh man...\\\\30 minutes")
        time_words.move_to(bubble.content)
        self.play(
            Animation(VectorizedPoint().next_to(pi1, UL, LARGE_BUFF)),
            pi2.change, "sad",
            FadeOutAndShift(bubble.content, DOWN),
            FadeInFromDown(time_words, DOWN),
        )
        self.wait(7)

    def create_pi_creatures(self):
        pi1 = PiCreature(color=BLUE)
        pi1.to_edge(DOWN)
        pi1.flip()
        pi1.shift(2.5 * RIGHT)
        pi2 = PiCreature(color=RED)
        pi2.to_edge(DOWN)
        pi2.shift(2 * LEFT)
        return [pi1, pi2]


class QuaternionEndscreen(PatreonEndScreen):
    CONFIG = {
        "specific_patrons": [
            "Juan Benet",
            "Matt Russell",
            "soekul",
            "Desmos",
            "Burt Humburg",
            "Dinesh Dharme",
            "Scott Walter",
            "Brice Gower",
            "Peter Mcinerney",
            "brian tiger chow",
            "Joseph Kelly",
            "Roy Larson",
            "Andrew Sachs",
            "Hoàng Tùng Lâm",
            "Devin Scott",
            "Akash Kumar",
            "Arthur Zey",
            "David Kedmey",
            "Ali Yahya",
            "Mayank M. Mehrotra",
            "Lukas Biewald",
            "Yana Chernobilsky",
            "Kaustuv DeBiswas",
            "Yu Jun",
            "dave nicponski",
            "Jordan Scales",
            "Markus Persson",
            "Lukáš Nový",
            "Fela",
            "Randy C. Will",
            "Britt Selvitelle",
            "Jonathan Wilson",
            "Ryan Atallah",
            "Joseph John Cox",
            "Luc Ritchie",
            "Ryan Williams",
            "Michael Hardel",
            "Federico Lebron",
            "L0j1k",
            "Ayan Doss",
            "Dylan Houlihan",
            "Steven Soloway",
            "Art Ianuzzi",
            "Nate Heckmann",
            "Michael Faust",
            "Richard Comish",
            "Nero Li",
            "Valeriy Skobelev",
            "Adrian Robinson",
            "Solara570",
            "Peter Ehrnstrom",
            "Kai Siang   Ang",
            "Alexis Olson",
            "Ludwig Schubert",
            "Omar Zrien",
            "Sindre Reino Trosterud",
            "Jeff Straathof",
            "Matt Langford",
            "Matt Roveto",
            "Magister Mugit",
            "Stevie Metke",
            "Cooper Jones",
            "James Hughes",
            "John V Wertheim",
            "Song Gao",
            "Richard Burgmann",
            "John Griffith",
            "Chris Connett",
            "Steven Tomlinson",
            "Jameel Syed",
            "Bong Choung",
            "Zhilong Yang",
            "Giovanni Filippi",
            "Eric Younge",
            "Prasant Jagannath",
            "Cody Brocious",
            "James H. Park",
            "Norton Wang",
            "Kevin Le",
            "Oliver Steele",
            "Yaw Etse",
            "Dave B",
            "Delton Ding",
            "Thomas Tarler",
            "1stViewMaths",
            "Jacob Magnuson",
            "Clark Gaebel",
            "Mathias Jansson",
            "David Clark",
            "Michael Gardner",
            "Mads Elvheim",
            "Awoo",
            "Dr  David G. Stork",
            "Ted Suzman",
            "Linh Tran",
            "Andrew Busey",
            "John Haley",
            "Ankalagon",
            "Eric Lavault",
            "Boris Veselinovich",
            "Julian Pulgarin",
            "Jeff Linse",
            "Robert Teed",
            "Jason Hise",
            "Bernd Sing",
            "James Thornton",
            "Mustafa Mahdi",
            "Mathew Bramson",
            "Jerry Ling",
            "Rish Kundalia",
            "Achille Brighton",
            "Ripta Pasay",
        ],
    }


class ThumbnailP1(RuleOfQuaternionMultiplication):
    CONFIG = {
        "three_d_axes_config": {
            "num_axis_pieces": 20,
        },
        "unit_labels_scale_factor": 1.5,
        "quaternion": [1, 0, 0, 0],
    }

    def construct(self):
        self.setup_all_trackers()
        self.remove(self.pink_dot_label)
        q_tracker = self.q_tracker
        m_tracker = self.multiplier_tracker

        # quat = normalize([-0.5, 0.5, -0.5, 0.5])
        quat = normalize(self.quaternion)
        m_tracker.set_value(quat)
        q_tracker.set_value(quat)
        proj_sphere = self.get_projected_sphere(0, solid=False)
        # self.specially_color_sphere(proj_sphere)
        proj_sphere.set_color_by_gradient(
            BLUE, YELLOW
        )
        proj_sphere.set_stroke(WHITE)
        proj_sphere.set_fill(opacity=0.4)
        for i, face in enumerate(proj_sphere):
            alpha = i / len(proj_sphere)
            opacity = 0.7 * (1 - there_and_back(alpha))
            face.set_fill(opacity=opacity)

        # unit_sphere = self.get_projected_sphere(0, quaternion=[1, 0, 0, 0], solid=False)
        # self.specially_color_sphere(unit_sphere)
        # unit_sphere.set_stroke(width=0)
        # proj_sphere.set_fill_by_checkerboard(BLUE_E, BLUE, opacity=0.8)
        for face in proj_sphere:
            face.points = face.points[::-1]
            max_r = np.max(np.apply_along_axis(get_norm, 1, face.points))
            if max_r > 30:
                face.fade(1)

        for label in self.unit_labels:
            label.set_shade_in_3d(False)
            label.set_background_stroke(color=BLACK, width=2)

        self.add(proj_sphere)
        # self.add(unit_sphere)

        for mobject in self.mobjects:
            try:
                mobject.shift(IN)
            except ValueError:
                pass

        self.set_camera_orientation(
            phi=70 * DEGREES,
            theta=-110 * DEGREES,
        )


class ThumbnailP2(ThumbnailP1):
    CONFIG = {
        "quaternion": [0, 1, 0, 0],
    }


class ThumbnailOverlay(Scene):
    def construct(self):
        title = TextMobject("Quaternions \\\\", "visualized")
        title.set_width(7)
        # title[1].scale(0.7, about_edge=UP)
        title.to_edge(UP, buff=MED_SMALL_BUFF)
        v_line = Line(DOWN, UP)
        v_line.set_height(FRAME_HEIGHT)

        title.set_background_stroke(color=BLACK, width=1)

        for part in (title[0][4:6], title[1][4:5]):
            rect = BackgroundRectangle(part)
            rect.set_fill(opacity=1)
            rect.stretch(0.9, 0)
            rect.stretch(1.1, 1)
            title.add_to_back(rect)
        # title.add_to_back(BackgroundRectangle(title[0]))

        arrow = Arrow(LEFT, RIGHT)
        arrow.scale(1.5)
        arrow.tip.scale(2)
        arrow.set_stroke(width=10)
        arrow.set_color(YELLOW)

        self.add(v_line)
        self.add(arrow)
        self.add(title)
