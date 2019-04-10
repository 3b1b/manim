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
                path_arc=90 * DEGREES,
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


class CompareODEToPDE(Scene):
    def construct(self):
        pass


class WriteHeatEquation(Scene):
    def construct(self):
        d1_words = TextMobject("Heat equation\\\\", "(1 dimension)")
        d3_words = TextMobject("Heat equation\\\\", "(3 dimensions)")

        kwargs = {
            "tex_to_color_map": {
                "{T}": YELLOW,
                "{t}": WHITE,
                "{x}": GREEN,
                "{y}": RED,
                "{z}": BLUE,
            }
        }
        d1_equation = TexMobject(
            "{\\partial {T} \\over \\partial {t}}({x}, {t})="
            "{\\partial^2 {T} \\over \\partial {x}^2} ({x}, {t})",
            **kwargs
        )
        d3_equation = TexMobject(
            "{\\partial {T} \\over \\partial {t}} = ",
            "{\\partial^2 {T} \\over \\partial {x}^2} + ",
            "{\\partial^2 {T} \\over \\partial {y}^2} + ",
            "{\\partial^2 {T} \\over \\partial {z}^2}",
            **kwargs
        )

        d1_group = VGroup(d1_words, d1_equation)
        d3_group = VGroup(d3_words, d3_equation)
        groups = VGroup(d1_group, d3_group)
        for group in groups:
            group.arrange(DOWN, buff=MED_LARGE_BUFF)
        groups.arrange(RIGHT, buff=2)
        groups.to_edge(UP)

        d3_rhs = d3_equation[6:]
        d3_brace = Brace(d3_rhs, DOWN)
        nabla_words = TextMobject("Sometimes written as")
        nabla_words.match_width(d3_brace)
        nabla_words.next_to(d3_brace, DOWN)
        nabla_exp = TexMobject("\\nabla^2 {T}", **kwargs)
        nabla_exp.next_to(nabla_words, DOWN)
        # nabla_group = VGroup(nabla_words, nabla_exp)

        d1_group.save_state()
        d1_group.center().to_edge(UP)

        self.play(
            Write(d1_words),
            FadeInFrom(d1_equation, UP),
            run_time=1,
        )
        self.wait(2)
        self.play(
            Restore(d1_group),
            FadeInFrom(d3_group, LEFT)
        )
        self.wait()
        self.play(
            GrowFromCenter(d3_brace),
            Write(nabla_words),
            TransformFromCopy(d3_rhs, nabla_exp),
            run_time=1,
        )
        self.wait()
