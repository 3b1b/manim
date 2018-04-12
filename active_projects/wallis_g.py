from big_ol_pile_of_manim_imports import *
from once_useful_constructs.light import AmbientLight
from once_useful_constructs.light import Lighthouse
from once_useful_constructs.light import SwitchOn
# from once_useful_constructs.light import LightSource

PRODUCT_COLOR = BLUE
DEFAULT_OPACITY_FUNCTION = inverse_power_law(1, 1.5, 1, 4)
CHEAP_AMBIENT_LIGHT_CONFIG = {
    "num_levels": 5,
    "radius": 0.25,
    "opacity_function": DEFAULT_OPACITY_FUNCTION,
}


def get_chord_f_label(chord, arg="f", direction=DOWN):
    chord_f = TextMobject("Chord(", "$%s$" % arg, ")", arg_separator="")
    chord_f.set_color_by_tex("$%s$" % arg, YELLOW)
    chord_f.add_background_rectangle()
    chord_f.next_to(chord.get_center(), direction, SMALL_BUFF)
    angle = ((chord.get_angle() + TAU / 2) % TAU) - TAU / 2
    if np.abs(angle) > TAU / 4:
        angle += TAU / 2
    chord_f.rotate(angle, about_point=chord.get_center())
    chord_f.angle = angle
    return chord_f

# Scenes


class DistanceProductScene(MovingCameraScene):
    CONFIG = {
        "ambient_light_config": {
            "opacity_function": DEFAULT_OPACITY_FUNCTION,
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
        "include_lighthouses": True,
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
                include_background_rectangle=True,
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

    def get_distance_product_column(self, column_top):
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
            show_ellipsis=True,
            include_background_rectangle=True,
        )
        product_decimal.scale_to_fit_height(self.numeric_distance_label_height)
        product_decimal.next_to(h_line, DOWN)
        product_decimal.align_to(stacked_labels, RIGHT)
        product_decimal.set_color(BLUE)
        return VGroup(stacked_labels, h_line, times, product_decimal)

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
        group.add(self.observer_dot, self.observer)
        if self.include_lighthouses:
            group.add(self.lighthouses)
        group.add(self.lights)
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

    def show_distance_product_in_column(self, **kwargs):
        group = self.get_distance_product_column(**kwargs)
        stacked_labels, h_line, times, product_decimal = group

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
        power_labels[0].next_to(outer_arrows[-1].get_start(), UR, SMALL_BUFF)
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
        for i in range(2, self.num_lighthouses) + [0]:
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
        self.play(ReplacementTransform(power_labels, L_labels))
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
            "(x-L_0)(x-L_1)\\cdots(x-L_{%d - 1})" % self.num_lighthouses, "=", "0"
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
        sevens = VGroup(polynomial[0][1][1], factored_polynomial[0][1][-4])
        n_terms = VGroup()
        for seven in sevens:
            n_term = TexMobject("N")
            n_term.replace(seven, dim_to_match=1)
            n_term.scale(0.9)
            n_term.shift(0.25 * SMALL_BUFF * DR)
            n_terms.add(n_term)

        self.play(LaggedStart(FadeOut, VGroup(*it.chain(
            L1_rhs, self.outer_arrows, self.L_labels, self.outer_arrow,
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


class PlugObserverIntoPolynomial(DistanceProductScene):
    CONFIG = {
        # "ambient_light_config": CHEAP_AMBIENT_LIGHT_CONFIG,
        "num_lighthouses": 7,
        # This makes it look slightly better, but renders much slower
        "add_lights_in_foreground": True,
    }

    def construct(self):
        self.add_plane()
        self.add_circle_group()
        self.label_roots()
        self.add_polynomial()
        self.point_out_rhs()
        self.introduce_observer()
        self.raise_observer_to_the_N()

    def add_plane(self):
        plane = self.plane = ComplexPlane(
            unit_size=2,
            y_radius=5,
        )
        plane.shift(DOWN)
        plane.add_coordinates()
        plane.coordinate_labels.submobjects.pop(-4)
        self.origin = plane.number_to_point(0)

        self.add(plane)

    def add_circle_group(self):
        self.circle.set_color(RED)
        self.circle.scale_to_fit_width(
            2 * np.linalg.norm(self.plane.number_to_point(1) - self.origin)
        )
        self.circle.move_to(self.origin)

        lights = self.lights = self.get_lights()
        dots = VGroup(*[
            Dot(point) for point in self.get_lh_points()
        ])
        for dot, light in zip(dots, lights):
            light.add_to_back(dot)

        self.add(self.circle, lights)
        if self.add_lights_in_foreground:
            self.add_foreground_mobject(lights)

    def label_roots(self):
        origin = self.origin
        labels = VGroup(*[
            TexMobject("L_%d" % d)
            for d in range(self.num_lighthouses)
        ])
        self.root_labels = labels
        points = self.get_lh_points()
        for label, point in zip(labels, points):
            label.move_to(interpolate(origin, point, 1.2))
        labels[0].align_to(origin, UP)
        labels[0].shift(SMALL_BUFF * DOWN)
        self.add(labels)

    def add_polynomial(self, arg="x"):
        self.polynomial = self.get_polynomial_equation(arg)
        self.add(self.polynomial)

    def point_out_rhs(self):
        rhs = self.get_polynomial_rhs(self.polynomial)
        brace = Brace(rhs, DOWN, buff=SMALL_BUFF)
        brace_text = brace.get_text("Useful for distance product", buff=SMALL_BUFF)
        brace_text.set_color(YELLOW)
        brace_text.add_background_rectangle()

        self.play(
            GrowFromCenter(brace),
            Write(brace_text)
        )
        self.wait()
        self.play(FadeOut(VGroup(brace, brace_text)))

    def introduce_observer(self):
        dot = self.observer_dot = Dot()
        dot.move_to(self.plane.coords_to_point(1.6, 0.8))
        observer = PiCreature(**self.observer_config)
        observer.move_to(dot)
        dot.match_color(observer)

        vect = 2 * DOWN + LEFT
        vect /= np.linalg.norm(vect)
        arrow = self.arrow = Vector(0.5 * vect)
        arrow.next_to(observer, -vect, buff=SMALL_BUFF)
        arrow.set_color(WHITE)

        full_name = TextMobject("Observer")
        var_name = self.var_name = TexMobject("O")
        for mob in full_name, var_name:
            mob.match_color(observer)
            mob.next_to(arrow.get_start(), UP, SMALL_BUFF)
            mob.add_background_rectangle()

        complex_decimal = DecimalNumber(0, include_background_rectangle=True)
        equals = TexMobject("=")
        complex_decimal_animation = ChangingDecimal(
            complex_decimal,
            lambda a: self.plane.point_to_number(dot.get_center()),
            position_update_func=lambda m: m.next_to(equals, RIGHT, SMALL_BUFF)
        )
        complex_decimal_animation.update(0)
        equals_decimal = VGroup(equals, complex_decimal)
        equals_decimal.next_to(var_name, RIGHT)

        new_polynomial = self.get_polynomial_equation("O")
        O_terms = new_polynomial.get_parts_by_tex("O")

        lhs, poly_eq, rhs = self.get_polynomial_split(new_polynomial)
        lhs_rect = SurroundingRectangle(lhs, color=YELLOW)
        rhs_rect = SurroundingRectangle(rhs, color=YELLOW)
        self.lhs, self.rhs = lhs, rhs
        self.lhs_rect, self.rhs_rect = lhs_rect, rhs_rect

        lines = self.lines = self.get_lines()
        lines_update = self.lines_update = UpdateFromFunc(
            lines, lambda l: Transform(l, self.get_lines()).update(1)
        )

        anims_for_dot_movement = self.anims_for_dot_movement = [
            MaintainPositionRelativeTo(arrow, dot),
            MaintainPositionRelativeTo(var_name, arrow),
            MaintainPositionRelativeTo(equals, var_name),
            complex_decimal_animation,
            lines_update,
        ]

        self.play(
            FadeInAndShiftFromDirection(observer, direction=-vect),
            GrowArrow(arrow)
        )
        self.play(Write(full_name))
        self.wait()
        self.play(
            ReplacementTransform(full_name[0], var_name[0]),
            ReplacementTransform(full_name[1][0], var_name[1][0]),
            FadeOut(full_name[1][1:]),
            ReplacementTransform(observer, dot),
            FadeIn(equals_decimal)
        )
        self.add_foreground_mobject(dot)

        # Substitute
        self.wait()
        self.play(
            ReplacementTransform(var_name.copy(), O_terms),
            ReplacementTransform(self.polynomial, new_polynomial)
        )
        self.polynomial = new_polynomial
        self.wait()

        # Show distances
        self.play(ShowCreation(rhs_rect))
        self.play(
            LaggedStart(ShowCreation, lines),
            Animation(dot)
        )

        self.play(
            Rotating(
                dot,
                radians=TAU,
                rate_func=smooth,
                about_point=dot.get_center() + MED_LARGE_BUFF * LEFT,
                run_time=4
            ),
            *anims_for_dot_movement
        )
        self.wait()

        self.remove(rhs_rect)
        self.play(ReplacementTransform(rhs_rect.copy(), lhs_rect))
        self.wait()

        # Move onto circle
        angle = self.observer_angle = TAU / self.num_lighthouses / 3.0
        target_point = self.plane.number_to_point(
            np.exp(complex(0, angle))
        )
        self.play(
            dot.move_to, target_point,
            *anims_for_dot_movement
        )
        self.play(FadeOut(VGroup(
            equals, complex_decimal,
            var_name, arrow,
        )))

    def raise_observer_to_the_N(self):
        dot = self.observer_dot
        origin = self.origin
        radius = self.get_radius()

        text_scale_val = 0.8

        question = TextMobject(
            "What fraction \\\\", "between $L_0$ and $L_1$", "?",
            arg_separator=""
        )
        question.scale(text_scale_val)
        question.next_to(dot, RIGHT)
        question.add_background_rectangle_to_parts()

        f_words = TextMobject("$f$", "of the way")
        third_words = TextMobject("$\\frac{1}{3}$", "of the way")
        for words in f_words, third_words:
            words.scale(text_scale_val)
            words.move_to(question[0])
            words[0].set_color(YELLOW)
            words.add_background_rectangle()

        obs_angle = self.observer_angle
        full_angle = TAU / self.num_lighthouses

        def get_arc(angle):
            result = Arc(angle=angle, radius=radius, color=YELLOW, stroke_width=4)
            result.shift(origin)
            return result

        arc = get_arc(obs_angle)
        O_to_N_arc = get_arc(obs_angle * self.num_lighthouses)

        O_to_N_dot = dot.copy().move_to(O_to_N_arc.point_from_proportion(1))
        O_to_N_arrow = Vector(0.5 * DR).next_to(O_to_N_dot, UL, SMALL_BUFF)
        O_to_N_arrow.set_color(WHITE)
        O_to_N_label = TexMobject("O", "^N")
        O_to_N_label.set_color_by_tex("O", dot.get_color())
        O_to_N_label.next_to(O_to_N_arrow.get_start(), UP, SMALL_BUFF)
        O_to_N_label.shift(SMALL_BUFF * RIGHT)
        O_to_N_group = VGroup(O_to_N_arc, O_to_N_arrow, O_to_N_label)

        around_circle_words = TextMobject("around the circle")
        around_circle_words.scale(text_scale_val)
        around_circle_words.add_background_rectangle()
        around_circle_words.next_to(self.circle.get_top(), UR)

        chord = Line(O_to_N_dot.get_center(), self.circle.get_right())
        chord.set_stroke(GREEN)

        chord_halves = VGroup(
            Line(chord.get_center(), chord.get_start()),
            Line(chord.get_center(), chord.get_end()),
        )
        chord_halves.set_stroke(WHITE, 5)

        chord_label = TexMobject("|", "O", "^N", "-", "1", "|")
        chord_label.set_color_by_tex("O", MAROON_B)
        chord_label.add_background_rectangle()
        chord_label.next_to(chord.get_center(), DOWN, SMALL_BUFF)
        chord_label.rotate(
            chord.get_angle(), about_point=chord.get_center()
        )

        numeric_chord_label = DecimalNumber(
            np.sqrt(3),
            num_decimal_points=4,
            include_background_rectangle=True,
            show_ellipsis=True,
        )
        numeric_chord_label.rotate(chord.get_angle())
        numeric_chord_label.move_to(chord_label)

        self.play(
            FadeIn(question),
            ShowCreation(arc),
        )
        for angle in [full_angle - obs_angle, -full_angle, obs_angle]:
            last_angle = angle_of_vector(dot.get_center() - origin)
            self.play(
                self.lines_update,
                UpdateFromAlphaFunc(
                    arc, lambda arc, a: Transform(
                        arc, get_arc(last_angle + a * angle)
                    ).update(1)
                ),
                Rotate(dot, angle, about_point=origin),
                run_time=2
            )
        self.play(
            FadeOut(question[0]),
            FadeOut(question[2]),
            FadeIn(f_words),
        )
        self.wait()
        self.play(
            FadeOut(self.lines),
            FadeOut(self.root_labels),
        )
        self.play(
            ReplacementTransform(dot.copy(), O_to_N_dot),
            ReplacementTransform(arc, O_to_N_arc),
            path_arc=O_to_N_arc.angle - arc.angle,
        )
        self.add_foreground_mobject(O_to_N_dot)
        self.play(
            FadeIn(O_to_N_label),
            GrowArrow(O_to_N_arrow),
        )
        self.wait()
        self.play(
            FadeOut(question[1]),
            f_words.next_to, around_circle_words, UP, SMALL_BUFF,
            FadeIn(around_circle_words)
        )
        self.wait()
        self.play(
            FadeIn(chord_label[0]),
            ReplacementTransform(self.lhs.copy(), chord_label[1]),
            ShowCreation(chord)
        )
        self.wait()

        # Talk through current example
        light_rings = VGroup(*it.chain(self.lights))
        self.play(LaggedStart(
            ApplyMethod, light_rings,
            lambda m: (m.shift, MED_SMALL_BUFF * UP),
            rate_func=wiggle
        ))
        self.play(
            FadeOut(around_circle_words),
            FadeIn(question[1]),
            ReplacementTransform(f_words, third_words)
        )
        self.play(
            Rotate(dot, 0.05 * TAU, about_point=origin, rate_func=wiggle)
        )
        self.wait(2)
        self.play(ReplacementTransform(dot.copy(), O_to_N_dot, path_arc=TAU / 3))
        self.play(
            third_words.next_to, around_circle_words, UP, SMALL_BUFF,
            FadeIn(around_circle_words),
            FadeOut(question[1])
        )
        self.wait()
        self.play(Indicate(self.lhs))
        for x in range(2):
            self.play(ShowCreationThenDestruction(chord_halves))
        self.play(
            FadeOut(chord_label),
            FadeIn(numeric_chord_label)
        )
        self.wait()
        self.remove(self.lhs_rect)
        self.play(
            FadeOut(chord),
            FadeOut(numeric_chord_label),
            FadeOut(O_to_N_group),
            FadeIn(self.lines),
            ReplacementTransform(self.lhs_rect.copy(), self.rhs_rect)
        )
        self.wait()

        # Add new lights
        for light in self.lights:
            light[1:].fade(0.5)
        added_lights = self.lights.copy()
        added_lights.rotate(full_angle / 2, about_point=origin)
        new_lights = VGroup(*it.chain(*zip(self.lights, added_lights)))
        self.num_lighthouses *= 2
        dot.generate_target()
        dot.target.move_to(self.get_circle_point_at_proportion(
            obs_angle / TAU / 2
        ))
        dot.save_state()
        dot.move_to(dot.target)
        new_lines = self.get_lines()
        dot.restore()

        self.play(Transform(self.lights, new_lights))
        self.play(
            MoveToTarget(dot),
            Transform(self.lines, new_lines)
        )
        self.wait()
        self.play(
            third_words.next_to, question[1], UP, SMALL_BUFF,
            FadeOut(around_circle_words),
            FadeIn(question[1]),
        )
        self.wait()

        chord_group = VGroup(chord, numeric_chord_label[1])
        chord_group.set_color(YELLOW)
        self.add_foreground_mobjects(*chord_group)
        self.play(
            FadeIn(chord),
            FadeIn(numeric_chord_label),
        )
        self.wait()

    # Helpers

    def get_polynomial_equation(self, var="x", color=None):
        if color is None:
            color = self.observer_config["color"]
        equation = TexMobject(
            "\\left(", var, "^N", "-", "1", "\\right)", "=",
            "\\left(", var, "-", "L_0", "\\right)",
            "\\left(", var, "-", "L_1", "\\right)",
            "\\cdots",
            "\\left(", var, "-", "L_{N-1}", "\\right)",
        )
        equation.set_color_by_tex(var, color)
        equation.to_edge(UP)
        equation.add_background_rectangle()
        return equation

    def get_polynomial_rhs(self, polynomial):
        return self.get_polynomial_split(polynomial)[2]

    def get_polynomial_lhs(self, polynomial):
        return self.get_polynomial_split(polynomial)[0]

    def get_polynomial_split(self, polynomial):
        eq = polynomial.get_part_by_tex("=")
        i = polynomial[1].submobjects.index(eq)
        return polynomial[1][:i], polynomial[1][i], polynomial[1][i + 1:]

    def get_lines(self):
        dot = self.observer_dot
        lines = VGroup(*[
            DashedLine(dot.get_center(), point)
            for point in self.get_lh_points()
        ])
        lines.set_stroke(width=2)
        return lines


class PlugObserverIntoPolynomial5Lighthouses(PlugObserverIntoPolynomial):
    CONFIG = {
        "num_lighthouses": 5,
    }


class PlugObserverIntoPolynomial3Lighthouses(PlugObserverIntoPolynomial):
    CONFIG = {
        "num_lighthouses": 3,
    }


class PlugObserverIntoPolynomial2Lighthouses(PlugObserverIntoPolynomial):
    CONFIG = {
        "num_lighthouses": 2,
    }


class DefineChordF(Scene):
    def construct(self):
        radius = 2.5

        full_chord_f = TextMobject("``", "Chord(", "$f$", ")", "''", arg_separator="")
        full_chord_f.set_color_by_tex("$f$", YELLOW)
        full_chord_f.to_edge(UP)
        chord_f = full_chord_f[1:-1]
        chord_f.generate_target()

        circle = Circle(radius=2.5)
        circle.set_color(RED)
        radius_line = Line(circle.get_center(), circle.get_right())
        one_label = TexMobject("1")
        one_label.next_to(radius_line, DOWN, SMALL_BUFF)

        chord = Line(*[circle.point_from_proportion(f) for f in [0, 1. / 3]])
        chord.set_color(YELLOW)
        chord_third = TextMobject("Chord(", "$1/3$", ")", arg_separator="")
        chord_third.set_color_by_tex("1/3", YELLOW)
        for term in chord_third, chord_f.target:
            term.next_to(chord.get_center(), UP, SMALL_BUFF)
            chord_angle = chord.get_angle() + np.pi
            term.rotate(chord_angle, about_point=chord.get_center())

        brace = Brace(Line(ORIGIN, TAU * UP / 3), RIGHT, buff=0)
        brace.generate_target()
        brace.target.stretch(0.5, 0)
        brace.target.apply_complex_function(np.exp)
        VGroup(brace, brace.target).scale(radius)
        brace.next_to(circle.get_right(), RIGHT, SMALL_BUFF, DOWN)
        brace.scale(0.5, about_edge=DOWN)
        brace.target.move_to(brace, DR)
        brace.target.shift(2 * SMALL_BUFF * LEFT)

        f_label = TexMobject("f")
        f_label.set_color(YELLOW)
        point = circle.point_from_proportion(1.0 / 6)
        f_label.move_to(point + 0.4 * (point - circle.get_center()))

        third_label = TexMobject("\\frac{1}{3}")
        third_label.scale(0.7)
        third_label.move_to(f_label)
        third_label.match_color(f_label)

        alphas = np.linspace(0, 1, 4)
        third_arcs = VGroup(*[
            VMobject().pointwise_become_partial(circle, a1, a2)
            for a1, a2 in zip(alphas, alphas[1:])
        ])
        third_arcs.set_color_by_gradient(BLUE, PINK, GREEN)

        # Terms for sine formula
        origin = circle.get_center()
        height = DashedLine(origin, chord.get_center())
        half_chords = VGroup(
            Line(chord.get_start(), chord.get_center()),
            Line(chord.get_end(), chord.get_center()),
        )
        half_chords.set_color_by_gradient(BLUE, PINK)
        alt_radius_line = Line(origin, chord.get_end())
        alt_radius_line.set_color(WHITE)
        angle_arc = Arc(
            radius=0.3,
            angle=TAU / 6,
        )
        angle_arc.shift(origin)
        angle_label = TexMobject("\\frac{f}{2}", "2\\pi")
        angle_label[0][0].set_color(YELLOW)
        angle_label.scale(0.6)
        angle_label.next_to(angle_arc, RIGHT, SMALL_BUFF, DOWN)
        angle_label.shift(SMALL_BUFF * UR)

        circle_group = VGroup(
            circle, chord, radius_line, one_label,
            brace, f_label, chord_f,
            half_chords, height,
            angle_arc, angle_label,
        )

        formula = TexMobject(
            "= 2 \\cdot \\sin\\left(\\frac{f}{2} 2\\pi \\right)",
            "= 2 \\cdot \\sin\\left(f \\pi \\right)",
        )
        for part in formula:
            part[7].set_color(YELLOW)

        # Draw circle and chord
        self.add(radius_line, circle, one_label)
        self.play(Write(full_chord_f))
        self.play(ShowCreation(chord))
        self.play(
            MoveToTarget(chord_f),
            FadeOut(VGroup(full_chord_f[0], full_chord_f[-1]))
        )
        self.play(GrowFromEdge(brace, DOWN))
        self.play(MoveToTarget(brace, path_arc=TAU / 3))
        self.play(Write(f_label))
        self.wait(2)

        # Show third
        self.remove(chord_f, f_label)
        self.play(
            ReplacementTransform(chord_f.copy(), chord_third),
            ReplacementTransform(f_label.copy(), third_label),
        )
        chord_copies = VGroup()
        last_chord = chord
        for color in PINK, BLUE:
            chord_copy = last_chord.copy()
            old_color = chord_copy.get_color()
            self.play(
                Rotate(chord_copy, -TAU / 6, about_point=last_chord.get_end()),
                UpdateFromAlphaFunc(
                    chord_copy,
                    lambda m, a: m.set_stroke(interpolate_color(old_color, color, a))
                )
            )
            chord_copy.reverse_points()
            last_chord = chord_copy
            chord_copies.add(chord_copy)
        self.wait()
        self.play(
            FadeOut(chord_copies),
            ReplacementTransform(chord_third, chord_f),
            ReplacementTransform(third_label, f_label),
        )

        # Show sine formula
        top_chord_f = chord_f.copy()
        top_chord_f.generate_target()
        top_chord_f.target.rotate(-chord_angle)
        top_chord_f.target.center().to_edge(UP, buff=LARGE_BUFF)
        top_chord_f.target.shift(3 * LEFT)
        formula.next_to(top_chord_f.target, RIGHT)

        self.play(
            ShowCreation(height),
            FadeIn(half_chords),
            ShowCreation(angle_arc),
            Write(angle_label)
        )
        self.wait()
        self.play(
            MoveToTarget(top_chord_f),
            circle_group.shift, 1.5 * DOWN,
        )
        self.play(Write(formula[0], run_time=1))
        self.wait()
        self.play(ReplacementTransform(
            formula[0].copy(), formula[1],
            path_arc=45 * DEGREES
        ))
        self.wait()


class DistanceProductIsChordF(PlugObserverIntoPolynomial):
    CONFIG = {
        "include_lighthouses": False,
        "num_lighthouses": 8,
        # "ambient_light_config": CHEAP_AMBIENT_LIGHT_CONFIG,
        # "add_lights_in_foreground": False,
    }

    def construct(self):
        self.add_plane()
        self.add_circle_group()
        self.add_polynomial("O")
        self.add_observer_and_lines()

    def add_observer_and_lines(self):
        fraction = self.observer_fraction = 0.3
        circle = self.circle

        O_dot = self.observer_dot = Dot()
        O_dot.set_color(self.observer_config["color"])
        O_to_N_dot = O_dot.copy()
        O_dot.move_to(self.get_circle_point_at_proportion(fraction / self.num_lighthouses))
        O_to_N_dot.move_to(self.get_circle_point_at_proportion(fraction))

        for dot, vect, tex in [(O_dot, DL, "O"), (O_to_N_dot, DR, "O^N")]:
            arrow = Vector(0.5 * vect, color=WHITE)
            arrow.next_to(dot.get_center(), -vect, SMALL_BUFF)
            label = TexMobject(tex)
            O_part = label[0]
            O_part.match_color(dot)
            label.add_background_rectangle()
            label.next_to(arrow.get_start(), -vect, buff=0, submobject_to_align=O_part)
            dot.arrow = arrow
            dot.label = label
            self.add_foreground_mobject(dot)
            self.add(arrow, label)
            # For the transition to f = 1 / 2
            dot.generate_target()

        fraction_words = VGroup(
            TextMobject("$f$", "of the way"),
            TextMobject("between lighthouses")
        )
        fraction_words.scale(0.8)
        fraction_words[0][0].set_color(YELLOW)
        fraction_words.arrange_submobjects(DOWN, SMALL_BUFF, aligned_edge=LEFT)
        fraction_words.next_to(O_dot.label, RIGHT)
        map(TexMobject.add_background_rectangle, fraction_words)

        f_arc, new_arc = [
            Arc(
                angle=(TAU * f / self.num_lighthouses),
                radius=self.get_radius(),
                color=YELLOW,
            ).shift(circle.get_center())
            for f in fraction, 0.5
        ]
        self.add(f_arc)

        lines = self.lines = self.get_lines()
        labels = self.get_numeric_distance_labels()

        black_rect = Rectangle(height=6, width=3.5)
        black_rect.set_stroke(width=0)
        black_rect.set_fill(BLACK, 1)
        black_rect.to_corner(DL, buff=0)
        colum_group = self.get_distance_product_column(
            column_top=black_rect.get_top() + MED_SMALL_BUFF * DOWN
        )
        stacked_labels, h_line, times, product_decimal = colum_group

        chord = Line(*[
            self.get_circle_point_at_proportion(f)
            for f in 0, fraction
        ])
        chord.set_stroke(YELLOW)
        chord_f = get_chord_f_label(chord)
        chord_f_as_product = chord_f.copy()
        chord_f_as_product.generate_target()
        chord_f_as_product.target.rotate(-chord_f_as_product.angle)
        chord_f_as_product.target.scale(0.8)
        chord_f_as_product.target.move_to(product_decimal, RIGHT)

        # Constructs for the case f = 1 / 2
        new_chord = Line(circle.get_right(), circle.get_left())
        new_chord.match_style(chord)
        chord_half = get_chord_f_label(new_chord, "1/2")

        f_terms = VGroup(fraction_words[0][1][0], chord_f_as_product[1][1])
        half_terms = VGroup(*[
            TexMobject("\\frac{1}{2}").scale(0.6).set_color(YELLOW).move_to(f)
            for f in f_terms
        ])
        half_terms[1].move_to(chord_f_as_product.target[1][1])

        O_dot.target.move_to(self.get_circle_point_at_proportion(0.5 / self.num_lighthouses))
        O_to_N_dot .target.move_to(circle.get_left())
        self.observer_dot = O_dot.target
        new_lines = self.get_lines()

        changing_decimals = []
        radius = self.get_radius()
        for decimal, line in zip(stacked_labels, new_lines):
            changing_decimals.append(
                ChangeDecimalToValue(decimal, line.get_length() / radius)
            )

        equals_two_terms = VGroup(*[
            TexMobject("=2").next_to(mob, DOWN, SMALL_BUFF)
            for mob in chord_half, chord_f_as_product.target
        ])

        # Animations

        self.play(Write(fraction_words))
        self.wait()
        self.play(
            LaggedStart(ShowCreation, lines),
            LaggedStart(FadeIn, labels),
        )
        self.play(
            FadeIn(black_rect),
            ReplacementTransform(labels.copy(), stacked_labels),
            ShowCreation(h_line),
            Write(times),
        )
        self.wait(2)
        self.add_foreground_mobjects(
            chord_f[1], chord, O_dot, O_to_N_dot
        )
        self.play(
            FadeOut(labels),
            ShowCreation(chord),
            FadeIn(chord_f),
        )
        self.play(MoveToTarget(chord_f_as_product))
        self.wait(2)

        # Transition to f = 1 / 2
        self.play(
            Transform(lines, new_lines),
            Transform(f_arc, new_arc),
            Transform(chord, new_chord),
            chord_f.rotate, -chord_f.angle,
            chord_f.move_to, chord_half,
            MoveToTarget(O_dot),
            MoveToTarget(O_to_N_dot),
            MaintainPositionRelativeTo(O_dot.arrow, O_dot),
            MaintainPositionRelativeTo(O_dot.label, O_dot),
            MaintainPositionRelativeTo(O_to_N_dot.arrow, O_to_N_dot),
            MaintainPositionRelativeTo(O_to_N_dot.label, O_to_N_dot),
            *changing_decimals,
            path_arc=(45 * DEGREES),
            run_time=2
        )
        self.play(
            Transform(chord_f, chord_half),
            Transform(f_terms, half_terms),
        )
        self.wait()
        for term in equals_two_terms:
            term.add_background_rectangle()
            self.add_foreground_mobject(term[1])
        self.play(
            Write(equals_two_terms)
        )
        self.wait()






































