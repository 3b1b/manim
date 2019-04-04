from big_ol_pile_of_manim_imports import *
from active_projects.ode.part1.staging import TourOfDifferentialEquations


class FourierSeriesIntro(Scene):
    def construct(self):
        title_scale_value = 1.5

        title = TextMobject(
            "Fourier ", "Series",
        )
        title.scale(title_scale_value)
        title.to_edge(UP)
        title.generate_target()

        details_coming = TextMobject("Details coming...")
        details_coming.next_to(title.get_corner(DR), DOWN)
        details_coming.set_color(LIGHT_GREY)

        physics = TextMobject("Physics")
        physics.scale(title_scale_value)
        arrow = Arrow(LEFT, RIGHT)
        group = VGroup(physics, arrow, title.target)
        group.arrange(RIGHT)
        physics.align_to(title.target, UP)
        group.to_edge(UP)

        rot_square = Square()
        rot_square.fade(1)
        rot_square.add_updater(lambda m, dt: m.rotate(dt))
        heat = TextMobject("Heat")
        heat.scale(title_scale_value)
        heat.move_to(physics[0][-1], DR)

        def update_heat_colors(heat):
            vertices = rot_square.get_vertices()
            letters = heat.family_members_with_points()
            for letter, vertex in zip(letters, vertices):
                alpha = (normalize(vertex)[0] + 1) / 2
                letter.set_color(interpolate_color(
                    YELLOW, RED, alpha,
                ))
        heat.add_updater(update_heat_colors)

        image = ImageMobject("Joseph Fourier")
        image.set_height(5)
        image.next_to(title, DOWN, MED_LARGE_BUFF)
        image.to_edge(LEFT)
        name = TextMobject("Joseph", "Fourier")
        name.next_to(image, DOWN)

        # self.play(FadeInFromDown(title))
        self.add(title)
        self.play(
            FadeInFromDown(image),
            TransformFromCopy(
                title.get_part_by_tex("Fourier"),
                name.get_part_by_tex("Fourier"),
                path_arc=-45 * DEGREES,
            ),
            FadeIn(name.get_part_by_tex("Joseph")),
        )
        self.play(Write(details_coming, run_time=1))
        self.play(LaggedStartMap(FadeOut, details_coming[0], run_time=1))
        self.wait()
        self.play(
            FadeInFrom(physics, RIGHT),
            GrowArrow(arrow),
            MoveToTarget(title)
        )
        self.wait()
        self.add(rot_square)
        self.play(
            FadeOutAndShift(physics, UP),
            FadeInFromDown(heat, DOWN),
        )
        self.wait(10)


class PartTwoOfTour(TourOfDifferentialEquations):
    CONFIG = {
        "zoomed_thumbnail_index": 1,
    }
