from big_ol_pile_of_manim_imports import *
from once_useful_constructs.light import AmbientLight
from once_useful_constructs.light import Lighthouse
from once_useful_constructs.light import SwitchOn
# from once_useful_constructs.light import LightSource

PRODUCT_COLOR = BLUE
CHEAP_AMBIENT_LIGHT_CONFIG = {
    "num_levels": 5,
    "radius": 0.5,
}


class DistanceProductScene(MovingCameraScene):
    CONFIG = {
        "ambient_light_config": {
            "opacity_function": inverse_power_law(1, 1.5, 1, 4),
            "num_levels": 100,
            "light_radius": 5,
            "max_opacity": 0.8,
            "color": PRODUCT_COLOR,
        },
        "circle_color": BLUE,
        "circle_radius": 3,
        "num_lighthouses": 6,
        "lighthouse_height": 0.5,
        "ignored_lighthouse_indices": [],
        "observer_config": {
            "color": MAROON_B,
            "mode": "pondering",
            "height": 0.25,
            "flip_at_start": True,
        },
        "observer_fraction": 1.0 / 3,
        "d_label_height": 0.35,
        "numeric_distance_label_height": 0.25,
        "default_product_column_top": FRAME_WIDTH * RIGHT / 4 + 1.5 * UP,
    }

    def setup(self):
        super(DistanceProductScene, self).setup()
        self.circle = Circle(
            color=self.circle_color,
            radius=self.circle_radius,
        )

    def get_circle_point_at_proportion(self, alpha):
        radius = self.get_radius()
        center = self.circle.get_center()
        angle = alpha * TAU
        unit_circle_point = np.cos(angle) * RIGHT + np.sin(angle) * UP
        return radius * unit_circle_point + center

    def get_lh_points(self):
        return np.array([
            self.get_circle_point_at_proportion(fdiv(i, self.num_lighthouses))
            for i in range(self.num_lighthouses)
            if i not in self.ignored_lighthouse_indices
        ])

    def get_observer_point(self, fraction=None):
        if fraction is None:
            fraction = self.observer_fraction
        return self.get_circle_point_at_proportion(fraction / self.num_lighthouses)

    def get_observer(self):
        observer = self.observer = PiCreature(**self.observer_config)
        observer.next_to(self.get_observer_point(), RIGHT, buff=SMALL_BUFF)
        return observer

    def get_observer_dot(self):
        self.observer_dot = Dot(
            self.get_observer_point(),
            color=self.observer_config["color"]
        )
        return self.observer_dot

    def get_lighthouses(self):
        self.lighthouses = VGroup()
        for point in self.get_lh_points():
            lighthouse = Lighthouse()
            lighthouse.scale_to_fit_height(self.lighthouse_height)
            lighthouse.move_to(point)
            self.lighthouses.add(lighthouse)
        return self.lighthouses

    def get_lights(self):
        self.lights = VGroup()
        for point in self.get_lh_points():
            light = AmbientLight(
                source_point=VectorizedPoint(point),
                **self.ambient_light_config
            )
            self.lights.add(light)
        return self.lights

    def get_distance_lines(self):
        self.distance_lines = VGroup(*[
            Line(self.get_observer_point(), point)
            for point in self.get_lh_points()
        ])
        return self.distance_lines

    def get_symbolic_distance_labels(self):
        if not hasattr(self, "distance_lines"):
            self.get_distance_lines()
        self.d_labels = VGroup()
        for i, line in enumerate(self.distance_lines):
            d_label = TexMobject("d_%d" % i)
            d_label.scale_to_fit_height(self.d_label_height)
            vect = rotate_vector(line.get_vector(), 90 * DEGREES)
            vect *= 2.5 * SMALL_BUFF / np.linalg.norm(vect)
            d_label.move_to(line.get_center() + vect)
            self.d_labels.add(d_label)
        return self.d_labels

    def get_numeric_distance_labels(self, num_decimal_points=3, show_ellipsis=True):
        radius = self.circle.get_width() / 2
        if not hasattr(self, "distance_lines"):
            self.get_distance_lines()
        labels = self.numeric_distance_labels = VGroup()
        for line in self.distance_lines:
            label = DecimalNumber(
                line.get_length() / radius,
                num_decimal_points=num_decimal_points,
                show_ellipsis=show_ellipsis,
            )
            label.scale_to_fit_height(self.numeric_distance_label_height)
            max_width = 0.5 * line.get_length()
            if label.get_width() > max_width:
                label.scale_to_fit_width(max_width)
            angle = (line.get_angle() % TAU) - TAU / 2
            if np.abs(angle) > TAU / 4:
                angle += np.sign(angle) * np.pi
            label.angle = angle
            label.next_to(line.get_center(), UP, SMALL_BUFF)
            label.rotate(angle, about_point=line.get_center())
            labels.add(label)
        return labels

    def get_circle_group(self):
        group = VGroup(self.circle)
        if not hasattr(self, "observer_dot"):
            self.get_observer_dot()
        if not hasattr(self, "observer"):
            self.get_observer()
        if not hasattr(self, "lighthouses"):
            self.get_lighthouses()
        if not hasattr(self, "lights"):
            self.get_lights()
        group.add(
            self.observer_dot,
            self.observer,
            self.lighthouses,
            self.lights,
        )
        return group

    def setup_lighthouses_and_observer(self):
        self.add(*self.get_circle_group())

    # Numerical results

    def get_radius(self):
        return self.circle.get_width() / 2.0

    def get_distance_product(self, fraction=None):
        radius = self.get_radius()
        observer_point = self.get_observer_point(fraction)
        distances = [
            np.linalg.norm(point - observer_point) / radius
            for point in self.get_lh_points()
        ]
        return reduce(op.mul, distances, 1.0)

    # Animating methods

    def add_numeric_distance_labels(self, show_line_creation=True):
        anims = []
        if not hasattr(self, "distance_lines"):
            self.get_distance_lines()
        if not hasattr(self, "numeric_distance_labels"):
            self.get_numeric_distance_labels()
        if show_line_creation:
            anims.append(LaggedStart(ShowCreation, self.distance_lines))
        anims.append(LaggedStart(FadeIn, self.numeric_distance_labels))

        self.play(*anims)

    def show_distance_product_in_column(self, column_top=None):
        if not hasattr(self, "numeric_distance_labels"):
            self.get_numeric_distance_labels()
        if column_top is None:
            column_top = self.default_product_column_top
        labels = self.numeric_distance_labels
        stacked_labels = labels.copy()
        for label in stacked_labels:
            label.rotate(-label.angle)
            label.scale_to_fit_height(self.numeric_distance_label_height)
        stacked_labels.arrange_submobjects(DOWN)
        stacked_labels.move_to(column_top, UP)

        h_line = Line(LEFT, RIGHT)
        h_line.scale_to_fit_width(1.5 * stacked_labels.get_width())
        h_line.next_to(stacked_labels, DOWN, aligned_edge=RIGHT)
        times = TexMobject("\\times")
        times.next_to(h_line, UP, SMALL_BUFF, aligned_edge=LEFT)

        product_decimal = DecimalNumber(
            self.get_distance_product(),
            num_decimal_points=3,
            show_ellipsis=True
        )
        product_decimal.scale_to_fit_height(self.numeric_distance_label_height)
        product_decimal.next_to(h_line, DOWN)
        product_decimal.align_to(stacked_labels, RIGHT)
        product_decimal.set_color(BLUE)

        self.play(ReplacementTransform(labels.copy(), stacked_labels))
        self.play(
            ShowCreation(h_line),
            Write(times)
        )
        self.play(
            ReplacementTransform(
                stacked_labels.copy(),
                VGroup(product_decimal)
            )
        )


class IntroduceDistanceProduct(DistanceProductScene):
    CONFIG = {
        "ambient_light_config": {
            # "num_levels": 10,
            # "radius": 1,
            "color": YELLOW,
        },
    }

    def construct(self):
        self.draw_circle_with_points()
        self.turn_into_lighthouses_and_observer()
        self.show_sum_of_inverse_squares()

    def draw_circle_with_points(self):
        circle = self.circle

        lh_dots = self.lh_dots = VGroup(*[
            Dot(point) for point in self.get_lh_points()
        ])
        lh_dot_arrows = VGroup(*[
            Arrow(*[
                interpolate(circle.get_center(), dot.get_center(), a)
                for a in 0.6, 0.9
            ], buff=0)
            for dot in lh_dots
        ])
        evenly_space_dots_label = TextMobject("Evenly-spaced \\\\ dots")
        evenly_space_dots_label.scale_to_fit_width(0.5 * circle.get_width())
        evenly_space_dots_label.move_to(circle)

        special_dot = self.special_dot = self.get_observer_dot()
        special_dot_arrow = Vector(DL)
        special_dot_arrow.next_to(special_dot, UR, SMALL_BUFF)
        special_dot_arrow.match_color(special_dot)
        special_dot_label = TextMobject("Special dot")
        special_dot_label.next_to(
            special_dot_arrow.get_start(), UP, SMALL_BUFF)
        special_dot_label.match_color(special_dot)
        special_dot.save_state()
        special_dot.next_to(special_dot_arrow, UR)
        special_dot.set_fill(opacity=0)

        self.play(ShowCreation(circle))
        self.play(
            LaggedStart(ShowCreation, lh_dots),
            LaggedStart(GrowArrow, lh_dot_arrows),
            Write(evenly_space_dots_label)
        )
        self.wait()
        self.play(
            special_dot.restore,
            GrowArrow(special_dot_arrow),
            Write(special_dot_label, run_time=1),
            FadeOut(VGroup(lh_dot_arrows, evenly_space_dots_label))
        )
        self.wait()
        self.play(FadeOut(VGroup(special_dot_arrow, special_dot_label)))

    def turn_into_lighthouses_and_observer(self):
        lighthouses = self.get_lighthouses()
        lights = self.get_lights()

        observer = self.get_observer()
        observer.save_state()
        observer.scale_to_fit_height(2)
        observer.change_mode("happy")
        observer.to_edge(RIGHT)

        self.play(
            LaggedStart(FadeOut, self.lh_dots),
            LaggedStart(FadeIn, lighthouses),
            LaggedStart(SwitchOn, lights),
        )
        self.wait()
        self.play(FadeIn(observer))
        self.play(observer.restore)
        self.wait()

    def show_sum_of_inverse_squares(self):
        lines = self.get_distance_lines()
        labels = self.get_symbolic_distance_labels()

        sum_of_inverse_squares = TexMobject(*it.chain(*[
            ["{1", "\\over", "(", "d_%d" % i, ")", "^2}", "+"]
            for i in range(len(lines))
        ]))
        sum_of_inverse_squares.submobjects.pop(-1)
        sum_of_inverse_squares.to_edge(UP)
        d_terms = sum_of_inverse_squares.get_parts_by_tex("d_")
        d_terms.set_color(YELLOW)
        plusses = sum_of_inverse_squares.get_parts_by_tex("+")
        last_term = sum_of_inverse_squares[-6:]
        non_d_terms = VGroup(*filter(
            lambda m: m not in d_terms and m not in last_term,
            sum_of_inverse_squares
        ))

        brace = Brace(sum_of_inverse_squares, DOWN)
        brace_text = brace.get_text("Total intensity of light")

        arrow = Vector(DOWN, color=WHITE).next_to(brace, DOWN)
        basel_sum = TexMobject(
            "{1 \\over 1^2} + ",
            "{1 \\over 2^2} + ",
            "{1 \\over 3^2} + ",
            "{1 \\over 4^2} + ",
            "\\cdots",
        )
        basel_sum.next_to(arrow, DOWN)
        basel_cross = Cross(basel_sum)
        useful_for = TextMobject("Useful for")
        useful_for.next_to(arrow, RIGHT)

        wallis_product = TexMobject(
            "{2 \\over 1} \\cdot", "{2 \\over 3} \\cdot",
            "{4 \\over 3} \\cdot", "{4 \\over 5} \\cdot",
            "{6 \\over 5} \\cdot", "{6 \\over 7} \\cdot",
            "\\cdots"
        )
        wallis_product.move_to(basel_sum)

        light_rings = VGroup(*it.chain(*self.lights))

        self.play(
            LaggedStart(ShowCreation, lines),
            LaggedStart(Write, labels),
        )
        circle_group = VGroup(*self.get_top_level_mobjects())
        self.wait()
        self.play(
            ReplacementTransform(labels[-1].copy(), last_term[3]),
            Write(VGroup(*it.chain(last_term[:3], last_term[4:])))
        )
        self.remove(last_term)
        self.add(last_term)
        self.wait()
        self.play(
            Write(non_d_terms),
            ReplacementTransform(
                labels[:-1].copy(),
                d_terms[:-1],
            ),
            circle_group.scale, 0.8, {"about_point": FRAME_Y_RADIUS * DOWN}
        )
        self.wait()
        self.play(LaggedStart(
            ApplyMethod, light_rings,
            lambda m: (m.set_fill, {"opacity": 2 * m.get_fill_opacity()}),
            rate_func=there_and_back,
            run_time=3,
        ))
        self.wait()

        # Mention useful just to basel problem
        circle_group.save_state()
        v_point = VectorizedPoint(FRAME_X_RADIUS * LEFT + FRAME_Y_RADIUS * DOWN)
        self.play(
            circle_group.next_to, v_point, UR, {"submobject_to_align": self.circle},
            circle_group.scale, 0.5, {"about_point": v_point.get_center()},
        )
        self.play(
            GrowFromCenter(brace),
            Write(brace_text)
        )
        self.wait()
        self.play(
            FadeOut(brace_text),
            GrowArrow(arrow),
            FadeIn(useful_for),
            FadeIn(basel_sum),
        )
        self.wait()
        self.play(
            ShowCreation(basel_cross),
            FadeOut(VGroup(arrow, useful_for, brace))
        )
        basel_group = VGroup(basel_sum, basel_cross)
        self.play(
            basel_group.scale, 0.5,
            basel_group.to_corner, DR,
        )
        self.play(Write(wallis_product))
        self.wait()

        # Transition to distance product
        self.play(
            circle_group.restore,
            wallis_product.match_width, basel_sum,
            wallis_product.next_to, basel_sum, UP, {"aligned_edge": RIGHT},
        )
        self.play(
            d_terms.shift, 0.75 * d_terms.get_height() * UP,
            d_terms.set_color, PRODUCT_COLOR,
            light_rings.set_fill, PRODUCT_COLOR,
            *[
                FadeOut(mob)
                for mob in sum_of_inverse_squares
                if mob not in d_terms and mob not in plusses
            ]
        )
        self.wait()
        self.play(
            FadeOut(plusses),
            d_terms.arrange_submobjects, RIGHT, 0.25 * SMALL_BUFF,
            d_terms.move_to, sum_of_inverse_squares, DOWN,
        )
        self.wait()

        # Label distance product
        brace = Brace(d_terms, UP, buff=SMALL_BUFF)
        distance_product_label = brace.get_text("``Distance product''")

        self.play(
            GrowFromCenter(brace),
            Write(distance_product_label)
        )
        line_copies = lines.copy().set_color(RED)
        self.play(LaggedStart(ShowCreationThenDestruction, line_copies))
        self.wait()
        self.play(LaggedStart(
            ApplyFunction, light_rings,
            lambda mob: (
                lambda m: m.shift(MED_SMALL_BUFF * UP).set_fill(opacity=2 * m.get_fill_opacity()),
                mob
            ),
            rate_func=wiggle,
            run_time=6,
        ))
        self.wait()


class Lemma1(DistanceProductScene):
    CONFIG = {
        "circle_radius": 2.5,
        "observer_fraction": 0.5,
        # "ambient_light_config": {
        #     "num_levels": 5,
        #     "radius": 1,
        # },
        "lighthouse_height": 0.25,
        "lemma_text": "distance product = 2",
    }

    def construct(self):
        self.add_title()
        self.add_circle_group()
        self.state_lemma_premise()
        self.show_product()

    def add_title(self):
        title = self.title = TextMobject("Two lemmas:")
        title.set_color(YELLOW)
        title.to_edge(UP, buff=MED_SMALL_BUFF)
        self.add(title)

    def add_circle_group(self):
        self.circle.to_corner(DL)
        circle_group = self.get_circle_group()
        self.play(LaggedStart(FadeIn, VGroup(*circle_group.family_members_with_points())))

    def state_lemma_premise(self):
        premise = TextMobject("Lemma 1: If observer is halfway between lighthouses,")
        self.premise = premise
        premise.next_to(self.title, DOWN)

        frac = 1.0 / self.num_lighthouses
        arc1, arc2 = arcs = VGroup(VMobject(), VMobject())
        arc1.pointwise_become_partial(self.circle, 0, frac / 2)
        arc2.pointwise_become_partial(self.circle, frac / 2, frac)
        arc1.reverse_points()
        arcs.set_stroke(YELLOW, 5)
        show_arcs = ShowCreationThenDestruction(
            arcs,
            submobject_mode="all_at_once",
            run_time=2,
        )

        self.play(Write(premise), show_arcs, run_time=2)
        self.wait()
        self.play(show_arcs)
        self.wait()

    def show_product(self):
        lemma = TextMobject(self.lemma_text)
        lemma.set_color(BLUE)
        lemma.next_to(self.premise, DOWN)
        self.add_numeric_distance_labels()
        self.play(Write(lemma, run_time=1))
        self.show_distance_product_in_column()
        self.wait()


class Lemma1With7Lighthouses(Lemma1):
    CONFIG = {
        "num_lighthouses": 7,
    }


class Lemma1With8Lighthouses(Lemma1):
    CONFIG = {
        "num_lighthouses": 8,
    }


class Lemma1With9Lighthouses(Lemma1):
    CONFIG = {
        "num_lighthouses": 9,
    }


class Lemma2(Lemma1):
    CONFIG = {
        # "ambient_light_config": CHEAP_AMBIENT_LIGHT_CONFIG,
        "lemma_text": "distance product = \\# Initial lighthouses"
    }

    def construct(self):
        self.add_title()
        self.add_circle_group()
        self.state_lemma_premise()
        self.replace_first_lighthouse()
        self.show_product()

    def state_lemma_premise(self):
        premise = self.premise = TextMobject(
            "Lemma 2: If the observer replaces a lighthouse,"
        )
        premise.next_to(self.title, DOWN)

        self.play(Write(premise, run_time=1))

    def replace_first_lighthouse(self):
        dot = self.observer_dot
        observer_anim = MaintainPositionRelativeTo(self.observer, dot)
        lighthouse_group = VGroup(self.lighthouses[0], self.lights[0])
        point = self.get_lh_points()[0]

        self.play(
            lighthouse_group.shift, 5 * RIGHT,
            lighthouse_group.fade, 1,
            run_time=1.5,
            rate_func=running_start,
            remover=True,
        )
        self.play(
            dot.move_to, point,
            observer_anim,
            path_arc=(-120 * DEGREES),
        )
        self.wait()

        self.ignored_lighthouse_indices = [0]
        self.observer_fraction = 0
        for group in self.lighthouses, self.lights:
            self.lighthouses.submobjects.pop(0)


class Lemma2With7Lighthouses(Lemma2):
    CONFIG = {
        "num_lighthouses": 7,
    }


class Lemma2With8Lighthouses(Lemma2):
    CONFIG = {
        "num_lighthouses": 8,
    }


class Lemma2With9Lighthouses(Lemma2):
    CONFIG = {
        "num_lighthouses": 9,
    }


class FromGeometryToAlgebra(DistanceProductScene):
    CONFIG = {
        "num_lighthouses": 7,
        # "ambient_light_config": CHEAP_AMBIENT_LIGHT_CONFIG,
    }

    def construct(self):
        self.setup_lights()
        self.point_out_evenly_spaced()
        self.transition_to_complex_plane()
        self.discuss_powers()
        self.raise_everything_to_the_nth()

    def setup_lights(self):
        circle = self.circle
        circle.scale_to_fit_height(5, about_edge=DOWN)
        lights = self.get_lights()
        dots = VGroup(*[Dot(point) for point in self.get_lh_points()])
        for dot, light in zip(dots, lights):
            light.add_to_back(dot)

        self.add(circle, lights)

    def point_out_evenly_spaced(self):
        circle = self.circle
        step = 1.0 / self.num_lighthouses / 2
        alpha_range = np.arange(0, 1 + step, step)
        arcs = VGroup(*[
            VMobject().pointwise_become_partial(circle, a1, a2)
            for a1, a2 in zip(alpha_range, alpha_range[1:])
        ])
        arcs.set_stroke(YELLOW, 5)

        for arc in arcs[::2]:
            arc.reverse_points()

        arcs_anim = ShowCreationThenDestruction(
            arcs, submobject_mode="all_at_once", run_time=2
        )

        spacing_words = self.spacing_words = TextMobject("Evenly-spaced")
        spacing_words.scale_to_fit_width(self.get_radius())
        spacing_words.move_to(circle)

        arrows = self.get_arrows()

        geometric_words = self.geometric_words = TextMobject("Geometric property")
        geometric_words.to_edge(UP)
        geometric_words.add_background_rectangle()

        self.add(geometric_words)
        self.play(
            FadeIn(spacing_words),
            arcs_anim,
            *map(GrowArrow, arrows)
        )
        self.play(FadeOut(arrows), arcs_anim)
        self.wait()

    def transition_to_complex_plane(self):
        plane = self.complex_plane = ComplexPlane(
            unit_size=2, y_radius=6, x_radius=9,
        )
        plane.shift(1.5 * RIGHT)
        plane.add_coordinates()
        origin = plane.number_to_point(0)
        h_line = Line(plane.number_to_point(-1), plane.number_to_point(1))

        circle = self.circle
        circle_group = VGroup(circle, self.lights)
        circle_group.generate_target()
        circle_group.target.scale(h_line.get_width() / circle.get_width())
        circle_group.target.shift(
            origin - circle_group.target[0].get_center()
        )
        circle_group.target[0].set_stroke(RED)

        geometric_words = self.geometric_words
        geometric_words.generate_target()
        arrow = TexMobject("\\rightarrow")
        arrow.add_background_rectangle()
        algebraic_words = TextMobject("Algebraic property")
        algebraic_words.add_background_rectangle()
        word_group = VGroup(geometric_words.target, arrow, algebraic_words)
        word_group.arrange_submobjects(RIGHT)
        word_group.move_to(origin)
        word_group.to_edge(UP)

        unit_circle_words = TextMobject("Unit circle", "")
        unit_circle_words.match_color(circle_group.target[0])
        for part in unit_circle_words:
            part.add_background_rectangle()
        unit_circle_words.next_to(origin, UP)

        complex_plane_words = TextMobject("Complex Plane")
        self.complex_plane_words = complex_plane_words
        complex_plane_words.move_to(word_group)
        complex_plane_words.add_background_rectangle()

        roots_of_unity_words = TextMobject("Roots of\\\\", "unity")
        roots_of_unity_words.move_to(origin)
        roots_of_unity_words.set_color(YELLOW)
        for part in roots_of_unity_words:
            part.add_background_rectangle()

        self.play(
            Write(plane),
            MoveToTarget(circle_group),
            FadeOut(self.spacing_words),
            MoveToTarget(geometric_words),
            FadeIn(arrow),
            FadeIn(algebraic_words),
        )
        word_group.submobjects[0] = geometric_words
        self.play(Write(unit_circle_words, run_time=1))

        # Show complex values
        outer_arrows = self.outer_arrows = self.get_arrows()
        for arrow, point in zip(outer_arrows, self.get_lh_points()):
            arrow.rotate(np.pi, about_point=point)
        outer_arrow = self.outer_arrow = outer_arrows[3].copy()

        values = map(plane.point_to_number, self.get_lh_points())
        complex_decimal = self.complex_decimal = DecimalNumber(
            values[3],
            num_decimal_points=3,
            include_background_rectangle=True
        )
        complex_decimal.next_to(outer_arrow.get_start(), LEFT, SMALL_BUFF)
        complex_decimal_rect = SurroundingRectangle(complex_decimal)
        complex_decimal_rect.fade(1)

        self.play(
            FadeIn(complex_plane_words),
            FadeOut(word_group),
            FadeIn(complex_decimal),
            FadeIn(outer_arrow)
        )
        self.wait(2)
        self.play(
            ChangeDecimalToValue(
                complex_decimal, values[1],
                tracked_mobject=complex_decimal_rect
            ),
            complex_decimal_rect.next_to, outer_arrows[1].get_start(), UP, SMALL_BUFF,
            Transform(outer_arrow, outer_arrows[1]),
            run_time=1.5
        )
        self.wait()

        arrows = self.get_arrows()
        arrows.set_color(YELLOW)
        self.play(
            ReplacementTransform(unit_circle_words, roots_of_unity_words),
            LaggedStart(GrowArrow, arrows)
        )
        self.wait()
        self.play(
            complex_plane_words.move_to, word_group,
            LaggedStart(FadeOut, VGroup(*it.chain(
                arrows, roots_of_unity_words
            )))
        )

        # Turn decimal into z
        x_term = self.x_term = TexMobject("x")
        x_term.add_background_rectangle()
        x_term.move_to(complex_decimal, DOWN)
        x_term.shift(0.5 * SMALL_BUFF * (DR))
        self.play(ReplacementTransform(complex_decimal, x_term))

    def discuss_powers(self):
        x_term = self.x_term
        outer_arrows = self.outer_arrows
        outer_arrows.add(outer_arrows[0].copy())
        plane = self.complex_plane
        origin = plane.number_to_point(0)

        question = TextMobject("What is $x^2$")
        question.next_to(x_term, RIGHT, LARGE_BUFF)
        question.set_color(YELLOW)

        lh_points = list(self.get_lh_points())
        lh_points.append(lh_points[0])
        lines = VGroup(*[
            Line(origin, point)
            for point in lh_points
        ])
        lines.set_color(GREEN)
        step = 1.0 / self.num_lighthouses
        angle_arcs = VGroup(*[
            Arc(angle=alpha * TAU, radius=0.35).shift(origin)
            for alpha in np.arange(0, 1 + step, step)
        ])
        angle_labels = VGroup()
        for i, arc in enumerate(angle_arcs):
            label = TexMobject("(%d / %d)\\tau" % (i, self.num_lighthouses))
            label.scale(0.5)
            label.add_background_rectangle()
            point = arc.point_from_proportion(0.5)
            point += 1.2 * (point - origin)
            label.move_to(point)
            angle_labels.add(label)

        line = self.angle_line = lines[1].copy()
        line_ghost = DashedLine(line.get_start(), line.get_end())
        self.ghost_angle_line = line_ghost
        line_ghost.set_stroke(line.get_color(), 2)
        angle_arc = angle_arcs[1].copy()
        angle_label = angle_labels[1].copy()
        angle_label.shift(0.25 * SMALL_BUFF * DR)

        magnitude_label = TexMobject("1")
        magnitude_label.next_to(line.get_center(), UL, buff=SMALL_BUFF)

        power_labels = VGroup()
        for i, arrow in enumerate(outer_arrows):
            label = TexMobject("x^%d" % i)
            label.next_to(
                arrow.get_start(), -arrow.get_vector(),
                submobject_to_align=label[0]
            )
            label.add_background_rectangle()
            power_labels.add(label)
        power_labels[-1].next_to(outer_arrows[-1].get_start(), UR, SMALL_BUFF)
        power_labels.submobjects[1] = x_term

        L_labels = self.L_labels = VGroup(*[
            TexMobject("L_%d" % i).move_to(power_label, DOWN).add_background_rectangle()
            for i, power_label in enumerate(power_labels)
        ])

        # Ask about squaring
        self.play(Write(question))
        self.wait()
        self.play(
            ShowCreation(line),
            Write(magnitude_label)
        )
        self.wait()
        self.play(
            ShowCreation(angle_arc),
            Write(angle_label)
        )
        self.wait()
        self.add(line_ghost)
        for i in range(2, self.num_lighthouses + 1):
            anims = [
                Transform(angle_arc, angle_arcs[i]),
                Transform(angle_label, angle_labels[i]),
                Transform(line, lines[i], path_arc=TAU / self.num_lighthouses),
            ]
            if i == 2:
                anims.append(FadeOut(magnitude_label))
            if i == 3:
                anims.append(FadeOut(question))
            self.play(*anims)
            new_anims = [
                GrowArrow(outer_arrows[i]),
                Write(power_labels[i]),
            ]
            if i == 2:
                new_anims.append(FadeOut(self.complex_plane_words))
            self.play(*new_anims)
            self.wait()
        self.play(ReplacementTransform(power_labels[1:], L_labels[1:]))
        self.wait()
        self.play(
            Rotate(self.lights, TAU / self.num_lighthouses / 2),
            rate_func=wiggle
        )
        self.wait()
        self.play(
            FadeOut(angle_arc),
            FadeOut(angle_label),
            *map(ShowCreationThenDestruction, lines)
        )
        self.wait()

    def raise_everything_to_the_nth(self):
        func_label = TexMobject("L \\rightarrow L^7")
        func_label.set_color(YELLOW)
        func_label.to_corner(UL, buff=LARGE_BUFF)
        func_label.add_background_rectangle()

        polynomial_scale_factor = 0.8

        polynomial = TexMobject("x^%d - 1" % self.num_lighthouses, "=", "0")
        polynomial.scale(polynomial_scale_factor)
        polynomial.next_to(func_label, UP)
        polynomial.to_edge(LEFT)

        factored_polynomial = TexMobject(
            "(x-L_1)(x-L_2)\\cdots(x-L_%d)" % self.num_lighthouses, "=", "0"
        )
        factored_polynomial.scale(polynomial_scale_factor)
        factored_polynomial.next_to(polynomial, DOWN, aligned_edge=LEFT)
        for group in polynomial, factored_polynomial:
            for part in group:
                part.add_background_rectangle()

        origin = self.complex_plane.number_to_point(0)

        lights = self.lights
        lights.save_state()
        rotations = []
        for i, light in enumerate(lights):
            rotations.append(Rotating(
                light,
                radians=(i * TAU - i * TAU / self.num_lighthouses),
                about_point=origin,
                rate_func=bezier([0, 0, 1, 1]),
            ))

        self.play(Write(func_label, run_time=1))
        for i, rotation in enumerate(rotations[:4]):
            if i == 3:
                rect = SurroundingRectangle(polynomial)
                rect.set_color(YELLOW)
                self.play(
                    FadeIn(polynomial),
                    ShowCreationThenDestruction(rect)
                )
            self.play(
                rotation,
                run_time=np.sqrt(i + 1)
            )
        self.play(*rotations[4:], run_time=3)
        self.wait()

        self.play(lights.restore)
        self.play(
            FadeOut(func_label),
            FadeIn(factored_polynomial)
        )
        self.wait(3)
        self.play(
            factored_polynomial[0].next_to, polynomial[1], RIGHT, 1.5 * SMALL_BUFF,
            FadeOut(polynomial[2]),
            FadeOut(factored_polynomial[1:]),
        )

        # Comment on formula
        formula = VGroup(polynomial[0], polynomial[1], factored_polynomial[0])
        rect = SurroundingRectangle(formula)

        brace = Brace(factored_polynomial[0], DOWN)
        brace2 = Brace(polynomial[0], DOWN)

        morty = PiCreature(color=GREY_BROWN)
        morty.scale(0.5)
        morty.next_to(brace.get_center(), DL, buff=LARGE_BUFF)

        L1_rhs = TexMobject("= \\cos(\\tau / 7) + \\\\", "\\sin(\\tau / 7)i")
        L1_rhs.next_to(self.L_labels[1], RIGHT, aligned_edge=UP)
        for part in L1_rhs:
            part.add_background_rectangle()

        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))
        self.wait()
        self.play(GrowFromCenter(brace))
        self.play(FadeIn(morty))
        self.play(morty.change, "horrified", brace)
        self.play(Blink(morty))
        self.wait()
        self.play(
            Write(L1_rhs),
            morty.change, "confused", L1_rhs
        )
        self.play(Blink(morty))
        self.wait()
        self.play(
            Transform(brace, brace2),
            morty.change, "hooray", brace2
        )
        self.play(Blink(morty))
        self.wait()

        # Nothing special about 7
        new_lights = self.lights.copy()
        new_lights.rotate(
            TAU / self.num_lighthouses / 2,
            about_point=origin
        )
        sevens = VGroup(polynomial[0][1][1], factored_polynomial[0][1][-2])
        n_terms = VGroup()
        for seven in sevens:
            n_term = TexMobject("N")
            n_term.replace(seven, dim_to_match=1)
            n_term.scale(0.9)
            n_term.shift(0.25 * SMALL_BUFF * DR)
            n_terms.add(n_term)

        self.play(LaggedStart(FadeOut, VGroup(*it.chain(
            L1_rhs, self.outer_arrows, self.L_labels[1:], self.outer_arrow,
            self.angle_line, self.ghost_angle_line
        ))))
        self.play(LaggedStart(SwitchOn, new_lights), morty.look_at, new_lights)
        self.play(Transform(sevens, n_terms))
        self.wait()
        self.play(Blink(morty))
        self.wait()
    #

    def get_arrows(self):
        return VGroup(*[
            Arrow(
                interpolate(self.circle.get_center(), point, 0.6),
                interpolate(self.circle.get_center(), point, 0.9),
                buff=0
            )
            for point in self.get_lh_points()
        ])
































