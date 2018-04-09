from big_ol_pile_of_manim_imports import *
from once_useful_constructs.light import AmbientLight
from once_useful_constructs.light import Lighthouse
from once_useful_constructs.light import SwitchOn
# from once_useful_constructs.light import LightSource


class IntroduceDistanceProduct(Scene):
    CONFIG = {
        "ambient_light_config": {
            "opacity_function": inverse_quadratic(1, 1.1, 1),
            # "num_levels": 100,
            "num_levels": 10,
            # "light_radius": 10,
            "radius": 1,
            "max_opacity": 0.5,
            "color": YELLOW,
        },
        "num_lighthouses": 8,
        "circle_radius": 3,
        "observer_color": MAROON_B,
        "lighthouse_height": 0.5,
    }

    def construct(self):
        self.draw_circle_with_points()
        self.turn_into_lighthouses_and_observer()
        self.show_sum_of_inverse_squares()
        self.transition_to_distance_product()

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
        lighthouses = VGroup()
        lights = VGroup()
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

        observer = PiCreature(color=self.observer_color)
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
        pass

    def transition_to_distance_product(self):
        pass



































