from big_ol_pile_of_manim_imports import *
from once_useful_constructs.light import AmbientLight
from once_useful_constructs.light import Lighthouse
from once_useful_constructs.light import SwitchOn
# from once_useful_constructs.light import LightSource


class IntroduceDistanceProduct(MovingCameraScene):
    CONFIG = {
        "ambient_light_config": {
            "opacity_function": inverse_quadratic(1, 1.1, 1),
            "num_levels": 100,
            # "num_levels": 10,
            "light_radius": 10,
            # "radius": 1,
            "max_opacity": 0.4,
            "color": YELLOW,
        },
        "num_lighthouses": 6,
        "circle_radius": 3,
        "observer_color": MAROON_B,
        "lighthouse_height": 0.5,
        "camera_class": MovingCamera,
    }

    def construct(self):
        self.draw_circle_with_points()
        self.turn_into_lighthouses_and_observer()
        self.show_sum_of_inverse_squares()

    def draw_circle_with_points(self):
        circle = Circle(color=BLUE)
        circle.scale(self.circle_radius)

        lh_dots = self.lh_dots = VGroup(*[
            Dot().move_to(circle.point_from_proportion(alpha))
            for alpha in np.arange(0, 1, 1.0 / self.num_lighthouses)
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

        special_dot = self.special_dot = Dot(color=self.observer_color)
        special_dot.move_to(circle.point_from_proportion(0.04))
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
        lighthouses = self.lighthouses = VGroup()
        lights = self.lights = VGroup()
        for dot in self.lh_dots:
            point = dot.get_center()
            lighthouse = Lighthouse()
            lighthouse.scale_to_fit_height(self.lighthouse_height)
            lighthouse.move_to(point)
            lighthouses.add(lighthouse)

            light = AmbientLight(
                source_point=VectorizedPoint(point),
                **self.ambient_light_config
            )
            lights.add(light)

        observer = self.observer = PiCreature(color=self.observer_color)
        observer.flip()
        observer.move_to(self.special_dot)
        observer.to_edge(RIGHT)

        self.play(
            LaggedStart(FadeOut, self.lh_dots),
            LaggedStart(FadeIn, lighthouses),
            LaggedStart(SwitchOn, lights),
        )
        self.wait()
        self.play(FadeIn(observer))
        self.play(
            observer.scale_to_fit_height, 0.25,
            observer.next_to, self.special_dot, RIGHT, 0.5 * SMALL_BUFF,
        )
        self.wait()

    def show_sum_of_inverse_squares(self):
        lines = VGroup(*[
            Line(self.special_dot.get_center(), dot.get_center())
            for dot in self.lh_dots
        ])
        labels = VGroup(*[TexMobject("d_%d" % i) for i in range(len(lines))])
        for label, line in zip(labels, lines):
            label.scale(0.75)
            vect = rotate_vector(line.get_vector(), TAU / 4)
            vect *= 2 * SMALL_BUFF / np.linalg.norm(vect)
            label.move_to(line.get_center() + vect)

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
            circle_group.scale, 0.8, {"about_edge": DOWN}
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
        self.play(
            circle_group.scale, 0.5,
            circle_group.to_corner, DL,
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
            d_terms.shift, d_terms.get_height() * UP / 2,
            *[
                FadeOut(mob)
                for mob in sum_of_inverse_squares
                if mob not in d_terms and mob not in plusses
            ]
        )
        self.wait()
        self.play(
            FadeOut(plusses),
            d_terms.arrange_submobjects, RIGHT, 0.5 * SMALL_BUFF,
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



































