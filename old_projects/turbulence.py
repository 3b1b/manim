from big_ol_pile_of_manim_imports import *
from old_projects.div_curl import PureAirfoilFlow
from old_projects.div_curl import VectorFieldSubmobjectFlow
from old_projects.div_curl import VectorFieldPointFlow
from old_projects.div_curl import four_swirls_function
from old_projects.lost_lecture import ShowWord


class CreationDestructionMobject(VMobject):
    CONFIG = {
        "start_time": 0,
        "frequency": 0.25,
        "max_ratio_shown": 0.3,
        "use_copy": True,
    }

    def __init__(self, template, **kwargs):
        VMobject.__init__(self, **kwargs)
        if self.use_copy:
            self.ghost_mob = template.copy().fade(1)
            self.add(self.ghost_mob)
        else:
            self.ghost_mob = template
            # Don't add
        self.shown_mob = template.deepcopy()
        self.shown_mob.clear_updaters()
        self.add(self.shown_mob)
        self.total_time = self.start_time

        def update(mob, dt):
            mob.total_time += dt
            period = 1.0 / mob.frequency
            unsmooth_alpha = (mob.total_time % period) / period
            alpha = bezier([0, 0, 1, 1])(unsmooth_alpha)
            mrs = mob.max_ratio_shown
            mob.shown_mob.pointwise_become_partial(
                mob.ghost_mob,
                max(interpolate(-mrs, 1, alpha), 0),
                min(interpolate(0, 1 + mrs, alpha), 1),
            )

        self.add_updater(update)


class Eddy(VMobject):
    CONFIG = {
        "cd_mob_config": {
            "frequency": 0.2,
            "max_ratio_shown": 0.3
        },
        "n_spirils": 5,
        "n_layers": 20,
        "radius": 1,
        "colors": [BLUE_A, BLUE_E],
    }

    def __init__(self, **kwargs):
        VMobject.__init__(self, **kwargs)
        lines = self.get_lines()
        # self.add(lines)
        self.add(*[
            CreationDestructionMobject(line, **self.cd_mob_config)
            for line in lines
        ])
        self.randomize_times()

    def randomize_times(self):
        for submob in self.submobjects:
            if hasattr(submob, "total_time"):
                T = 1.0 / submob.frequency
                submob.total_time = T * random.random()

    def get_lines(self):
        a = 0.2
        return VGroup(*[
            self.get_line(r=self.radius * (1 - a + 2 * a * random.random()))
            for x in range(self.n_layers)
        ])

    def get_line(self, r):
        return ParametricFunction(
            lambda t: r * (t + 1)**(-1) * np.array([
                np.cos(TAU * t),
                np.sin(TAU * t),
                0,
            ]),
            t_min=0.1 * random.random(),
            t_max=self.n_spirils,
            stroke_width=1,
            color=interpolate_color(*self.colors, random.random())
        )


class Chaos(Eddy):
    CONFIG = {
        "n_lines": 12,
        "height": 1,
        "width": 2,
        "n_midpoints": 4,
        "cd_mob_config": {
            "use_copy": False,
            "frequency": 1,
            "max_ratio_shown": 0.8
        }
    }

    def __init__(self, **kwargs):
        VMobject.__init__(self, **kwargs)
        rect = Rectangle(height=self.height, width=self.width)
        rect.move_to(ORIGIN, DL)
        rect.fade(1)
        self.rect = rect
        self.add(rect)

        lines = self.get_lines()
        self.add(*[
            CreationDestructionMobject(line, **self.cd_mob_config)
            for line in lines
        ])
        self.randomize_times()
        lines.fade(1)
        self.add(lines)

    def get_lines(self):
        return VGroup(*[
            self.get_line(y)
            for y in np.linspace(0, self.height, self.n_lines)
        ])

    def get_line(self, y):
        frequencies = [0] + list(2 + 2 * np.random.random(self.n_midpoints)) + [0]
        rect = self.rect
        line = Line(
            y * UP, y * UP + self.width * RIGHT,
            stroke_width=1
        )
        line.insert_n_anchor_points(self.n_midpoints)
        line.total_time = random.random()
        delta_h = self.height / (self.n_lines - 1)

        def update(line, dt):
            x0, y0 = rect.get_corner(DL)[:2]
            x1, y1 = rect.get_corner(UR)[:2]
            line.total_time += dt
            xs = np.linspace(x0, x1, self.n_midpoints + 2)
            new_anchors = [
                np.array([
                    x + 1.0 * delta_h * np.cos(f * line.total_time),
                    y0 + y + 1.0 * delta_h * np.cos(f * line.total_time),
                    0
                ])
                for (x, f) in zip(xs, frequencies)
            ]
            line.set_points_smoothly(new_anchors)

        line.add_updater(update)
        return line


class DoublePendulum(VMobject):
    CONFIG = {
        "start_angles": [3 * PI / 7, 3 * PI / 4],
        "color1": BLUE,
        "color2": RED,
    }

    def __init__(self, **kwargs):
        VMobject.__init__(self, **kwargs)
        line1 = Line(ORIGIN, UP)
        dot1 = Dot(color=self.color1)
        dot1.add_updater(lambda d: d.move_to(line1.get_end()))
        line2 = Line(UP, 2 * UP)
        dot2 = Dot(color=self.color2)
        dot2.add_updater(lambda d: d.move_to(line2.get_end()))
        self.add(line1, line2, dot1, dot2)

        # Largely copied from https://scipython.com/blog/the-double-pendulum/
        # Pendulum rod lengths (m), bob masses (kg).
        L1, L2 = 1, 1
        m1, m2 = 1, 1
        # The gravitational acceleration (m.s-2).
        g = 9.81

        self.state_vect = np.array([
            self.start_angles[0], 0,
            self.start_angles[1], 0,
        ])
        self.state_vect += np.random.random(4) * 1e-7

        def update(group, dt):
            for x in range(2):
                line1, line2 = group.submobjects[:2]
                theta1, z1, theta2, z2 = group.state_vect

                c, s = np.cos(theta1 - theta2), np.sin(theta1 - theta2)

                theta1dot = z1
                z1dot = (m2 * g * np.sin(theta2) * c - m2 * s * (L1 * (z1**2) * c + L2 * z2**2) -
                         (m1 + m2) * g * np.sin(theta1)) / L1 / (m1 + m2 * s**2)
                theta2dot = z2
                z2dot = ((m1 + m2) * (L1 * (z1**2) * s - g * np.sin(theta2) + g * np.sin(theta1) * c) +
                         m2 * L2 * (z2**2) * s * c) / L2 / (m1 + m2 * s**2)

                group.state_vect += 0.5 * dt * np.array([
                    theta1dot, z1dot, theta2dot, z2dot,
                ])
                group.state_vect[1::2] *= 0.9999

            p1 = L1 * np.sin(theta1) * RIGHT - L1 * np.cos(theta1) * UP
            p2 = p1 + L2 * np.sin(theta2) * RIGHT - L2 * np.cos(theta2) * UP

            line1.put_start_and_end_on(ORIGIN, p1)
            line2.put_start_and_end_on(p1, p2)

        self.add_updater(update)


class DoublePendulums(VGroup):
    def __init__(self, **kwargs):
        colors = [BLUE, RED, YELLOW, PINK, MAROON_B, PURPLE, GREEN]
        VGroup.__init__(
            self,
            *[
                DoublePendulum(
                    color1=random.choice(colors),
                    color2=random.choice(colors),
                )
                for x in range(5)
            ],
            **kwargs,
        )


class Diffusion(VMobject):
    CONFIG = {
        "height": 1.5,
        "n_dots": 1000,
        "colors": [RED, BLUE]
    }

    def __init__(self, **kwargs):
        VMobject.__init__(self, **kwargs)
        self.add_dots()
        self.add_invisible_circles()

    def add_dots(self):
        dots = VGroup(*[Dot() for x in range(self.n_dots)])
        dots.arrange_submobjects_in_grid(buff=SMALL_BUFF)
        dots.center()
        dots.set_height(self.height)
        dots.sort_submobjects(lambda p: p[0])
        dots[:len(dots) // 2].set_color(self.colors[0])
        dots[len(dots) // 2:].set_color(self.colors[1])
        dots.set_fill(opacity=0.8)
        self.dots = dots
        self.add(dots)

    def add_invisible_circles(self):
        circles = VGroup()
        for dot in self.dots:
            point = dot.get_center()
            radius = get_norm(point)
            circle = Circle(radius=radius)
            circle.rotate(angle_of_vector(point))
            circle.fade(1)
            circles.add(circle)
            self.add_updater_to_dot(dot, circle)
        self.add(circles)

    def add_updater_to_dot(self, dot, circle):
        dot.total_time = 0
        radius = get_norm(dot.get_center())
        freq = 0.1 + 0.05 * random.random() + 0.05 / radius

        def update(dot, dt):
            dot.total_time += dt
            prop = (freq * dot.total_time) % 1
            dot.move_to(circle.point_from_proportion(prop))

        dot.add_updater(update)


class NavierStokesEquations(TexMobject):
    CONFIG = {
        "tex_to_color_map": {
            "\\rho": YELLOW,
            "\\mu": GREEN,
            "\\textbf{v}": BLUE,
            "p{}": RED,
        },
        "width": 10,
    }

    def __init__(self, **kwargs):
        v_tex = "\\textbf{v}"
        TexMobject.__init__(
            self,
            "\\rho",
            "\\left("
            "{\\partial", v_tex, "\\over",
            "\\partial", "t}",
            "+",
            v_tex, "\\cdot", "\\nabla", v_tex,
            "\\right)",
            "=",
            "-", "\\nabla", "p{}", "+",
            "\\mu", "\\nabla^2", v_tex, "+",
            # "\\frac{1}{3}", "\\mu", "\\nabla",
            # "(", "\\nabla", "\\cdot", v_tex, ")", "+",
            "\\textbf{F}",
            "\\qquad\\qquad",
            "\\nabla", "\\cdot", v_tex, "=", "0",
            **kwargs
        )
        self.set_width(self.width)

    def get_labels(self):
        parts = self.get_parts()
        words = [
            "Analogous to \\\\ mass $\\times$ acceleration",
            "Pressure\\\\forces",
            "Viscous\\\\forces",
            "External\\\\forces",
        ]

        result = VGroup()
        braces = VGroup()
        word_mobs = VGroup()
        for i, part, word in zip(it.count(), parts, words):
            brace = Brace(part, DOWN, buff=SMALL_BUFF)
            word_mob = brace.get_text(word)
            word_mob.scale(0.7, about_edge=UP)
            word_mobs.add(word_mob)
            braces.add(brace)
            result.add(VGroup(brace, word_mob))
        word_mobs[1:].arrange_submobjects(RIGHT, buff=MED_SMALL_BUFF)
        word_mobs[1:].next_to(braces[2], DOWN, SMALL_BUFF)
        word_mobs[1].set_color(RED)
        word_mobs[2].set_color(GREEN)
        return result

    def get_parts(self):
        return VGroup(
            self[:12],
            self[13:16],
            self[17:20],
            self[21:22],
        )


class Test(Scene):
    def construct(self):
        self.add(DoublePendulums())
        self.wait(30)

# Scenes


class EddyReference(Scene):
    CONFIG = {
        "radius": 1,
        "label": "Eddy",
        "label": "",
    }

    def construct(self):
        eddy = Eddy(radius=self.radius)
        new_eddy = eddy.get_lines()
        for line in new_eddy:
            line.set_stroke(
                width=(3 + 3 * random.random())
            )
        label = TextMobject(self.label)
        label.next_to(new_eddy, UP)

        self.play(
            LaggedStart(ShowCreationThenDestruction, new_eddy),
            FadeIn(
                label,
                rate_func=there_and_back_with_pause,
            ),
            run_time=3
        )


class EddyReferenceWithLabel(EddyReference):
    CONFIG = {
        "label": "Eddy"
    }


class EddyLabels(Scene):
    def construct(self):
        labels = VGroup(
            TextMobject("Large eddy"),
            TextMobject("Medium eddy"),
            TextMobject("Small eddy"),
        )
        for label in labels:
            self.play(FadeIn(
                label,
                rate_func=there_and_back_with_pause,
                run_time=3
            ))


class LargeEddyReference(EddyReference):
    CONFIG = {
        "radius": 2,
        "label": ""
    }


class MediumEddyReference(EddyReference):
    CONFIG = {
        "radius": 0.8,
        "label": "Medium eddy"
    }


class SmallEddyReference(EddyReference):
    CONFIG = {
        "radius": 0.25,
        "label": "Small eddy"
    }


class SomeTurbulenceEquations(PiCreatureScene):
    def construct(self):
        randy, morty = self.pi_creatures
        navier_stokes = NavierStokesEquations()
        line = Line(randy.get_right(), morty.get_left())
        navier_stokes.replace(line, dim_to_match=0)
        navier_stokes.scale(1.2)

        distribution = TexMobject(
            "E(k) \\propto k^{-5/3}",
            tex_to_color_map={
                "k": GREEN,
                "-5/3": YELLOW,
            }
        )
        distribution.next_to(morty, UL)
        brace = Brace(distribution, DOWN, buff=SMALL_BUFF)
        brace_words = brace.get_text("Explained soon...")
        brace_group = VGroup(brace, brace_words)

        self.play(
            Write(navier_stokes),
            randy.change, "confused", navier_stokes,
            morty.change, "confused", navier_stokes,
        )
        self.wait(3)
        self.play(
            morty.change, "raise_right_hand", distribution,
            randy.look_at, distribution,
            FadeInFromDown(distribution),
            navier_stokes.fade, 0.5,
        )
        self.play(GrowFromCenter(brace_group))
        self.play(randy.change, "pondering", distribution)
        self.wait(3)
        dist_group = VGroup(distribution, brace_group)
        self.play(
            LaggedStart(FadeOut, VGroup(randy, morty, navier_stokes)),
            dist_group.scale, 1.5,
            dist_group.center,
            dist_group.to_edge, UP,
        )
        self.wait()

    def create_pi_creatures(self):
        randy, morty = Randolph(), Mortimer()
        randy.to_corner(DL)
        morty.to_corner(DR)
        return (randy, morty)


class JokeRingEquation(Scene):
    def construct(self):
        items = VGroup(
            TextMobject("Container with a lip"),
            TextMobject("Fill with smoke (or fog)"),
            TextMobject("Hold awkwardly"),
        )
        line = Line(LEFT, RIGHT).set_width(items.get_width() + 1)
        items.add(line)
        items.add(TextMobject("Vortex ring"))
        items.arrange_submobjects(DOWN, buff=MED_LARGE_BUFF, aligned_edge=LEFT)
        line.shift(LEFT)
        plus = TexMobject("+")
        plus.next_to(line.get_left(), UR, SMALL_BUFF)
        line.add(plus)
        items.to_edge(RIGHT)

        point = 3.8 * LEFT + 0.2 * UP
        arrow1 = Arrow(
            items[0].get_left(), point + 0.8 * UP + 0.3 * RIGHT,
            use_rectangular_stem=False,
            path_arc=90 * DEGREES,
        )
        arrow1.pointwise_become_partial(arrow1, 0, 0.99)

        arrow2 = Arrow(
            items[1].get_left(), point,
        )
        arrows = VGroup(arrow1, arrow2)

        for i in 0, 1:
            self.play(
                FadeInFromDown(items[i]),
                ShowCreation(arrows[i])
            )
            self.wait()
        self.play(LaggedStart(FadeIn, items[2:]))
        self.wait()
        self.play(FadeOut(arrows))
        self.wait()


class VideoOnPhysicsGirlWrapper(Scene):
    def construct(self):
        rect = ScreenRectangle(height=6)
        title = TextMobject("Video on Physics Girl")
        title.scale(1.5)
        title.to_edge(UP)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait()


class LightBouncingOffFogParticle(Scene):
    def construct(self):
        words = TextMobject(
            "Light bouncing\\\\",
            "off fog particles"
        )
        arrow = Vector(UP + 0.5 * RIGHT)
        arrow.next_to(words, UP)
        arrow.set_color(WHITE)

        self.add(words)
        self.play(GrowArrow(arrow))
        self.wait()


class NightHawkInLightWrapper(Scene):
    def construct(self):
        title = TextMobject("NightHawkInLight")
        title.scale(1.5)
        title.to_edge(UP)
        rect = ScreenRectangle(height=6)
        rect.next_to(title, DOWN)
        self.add(title)
        self.play(ShowCreation(rect))
        self.wait()


class CarefulWithLasers(TeacherStudentsScene):
    def construct(self):
        morty = self.teacher
        randy = self.students[1]
        randy2 = self.students[2]
        # randy.change('hooray')
        laser = VGroup(
            Rectangle(
                height=0.1,
                width=0.3,
                fill_color=LIGHT_GREY,
                fill_opacity=1,
                stroke_color=DARK_GREY,
                stroke_width=1,
            ),
            Line(ORIGIN, 10 * RIGHT, color=GREEN_SCREEN)
        )
        laser.arrange_submobjects(RIGHT, buff=0)
        laser.rotate(45 * DEGREES)
        laser.shift(randy.get_corner(UR) - laser[0].get_center() + 0.1 * DR)

        laser.time = 0

        def update_laser(laser, dt):
            laser.time += dt
            laser.rotate(
                0.5 * dt * np.sin(laser.time),
                about_point=laser[0].get_center()
            )
        laser.add_updater(update_laser)

        self.play(LaggedStart(FadeInFromDown, self.pi_creatures, run_time=1))
        self.add(self.pi_creatures, laser)
        for pi in self.pi_creatures:
            pi.add_updater(lambda p: p.look_at(laser[1]))
        self.play(
            ShowCreation(laser),
            self.get_student_changes(
                "surprised", "hooray", "horrified",
                look_at_arg=laser
            )
        )
        self.teacher_says(
            "Careful with \\\\ the laser!",
            target_mode="angry"
        )
        self.wait(2.2)
        morty.save_state()
        randy2.save_state()
        self.play(
            morty.blink, randy2.blink,
            run_time=0.3
        )
        self.wait(2)
        self.play(
            morty.restore, randy2.restore,
            run_time=0.3
        )
        self.wait(2)


class SetAsideTurbulence(PiCreatureScene):
    def construct(self):
        self.pi_creature_says(
            "Forget vortex rings",
            target_mode="speaking"
        )
        self.wait()
        self.pi_creature_says(
            "look at that\\\\ turbulence!",
            target_mode="surprised"
        )
        self.wait()

    def create_pi_creature(self):
        morty = Mortimer()
        morty.to_corner(DR)
        return morty


class WavingRodLabel(Scene):
    def construct(self):
        words = TextMobject(
            "(Waving a small flag \\\\ through the air)"
        )
        self.play(Write(words))
        self.wait()


class SeekOrderWords(Scene):
    def construct(self):
        words = TextMobject("Seek order amidst chaos")
        words.scale(1.5)
        self.play(Write(words))
        self.wait()


class LongEddy(Scene):
    def construct(self):
        self.add(Eddy())
        self.wait(30)


class LongDoublePendulum(Scene):
    def construct(self):
        self.add(DoublePendulums())
        self.wait(30)


class LongDiffusion(Scene):
    def construct(self):
        self.add(Diffusion())
        self.wait(30)


class AskAboutTurbulence(TeacherStudentsScene):
    def construct(self):
        self.pi_creatures_ask()
        self.divide_by_qualitative_quantitative()
        self.three_qualitative_descriptors()
        self.rigorous_definition()

    def pi_creatures_ask(self):
        morty = self.teacher
        randy = self.students[1]
        morty.change("surprised")

        words = TextMobject("Wait,", "what", "exactly \\\\", "is turbulence?")
        question = TextMobject("What", "is turbulence?")
        question.to_edge(UP, buff=MED_SMALL_BUFF)
        h_line = Line(LEFT, RIGHT).set_width(FRAME_WIDTH - 1)
        h_line.next_to(question, DOWN, buff=MED_LARGE_BUFF)

        self.student_says(
            words,
            target_mode='raise_left_hand',
            added_anims=[morty.change, 'pondering']
        )
        self.change_student_modes(
            "erm", "raise_left_hand", "confused",
        )
        self.wait(3)
        self.play(
            morty.change, "raise_right_hand",
            FadeOut(randy.bubble),
            ReplacementTransform(VGroup(words[1], words[3]), question),
            FadeOut(VGroup(words[0], words[2])),
            self.get_student_changes(
                *3 * ["pondering"],
                look_at_arg=question
            )
        )
        self.play(
            ShowCreation(h_line),
            LaggedStart(
                FadeOutAndShiftDown, self.pi_creatures,
                run_time=1,
                lag_ratio=0.8
            )
        )
        self.wait()

        self.question = question
        self.h_line = h_line

    def divide_by_qualitative_quantitative(self):
        v_line = Line(
            self.h_line.get_center(),
            FRAME_HEIGHT * DOWN / 2,
        )
        words = VGroup(
            TextMobject("Features", color=YELLOW),
            TextMobject("Rigorous definition", color=BLUE),
        )
        words.next_to(self.h_line, DOWN)
        words[0].shift(FRAME_WIDTH * LEFT / 4)
        words[1].shift(FRAME_WIDTH * RIGHT / 4)
        self.play(
            ShowCreation(v_line),
            LaggedStart(FadeInFromDown, words)
        )
        self.wait()

        self.words = words

    def three_qualitative_descriptors(self):
        words = VGroup(
            TextMobject("- Eddies"),
            TextMobject("- Chaos"),
            TextMobject("- Diffusion"),
        )
        words.arrange_submobjects(
            DOWN, buff=1.25,
            aligned_edge=LEFT
        )
        words.to_edge(LEFT)
        words.shift(MED_LARGE_BUFF * DOWN)

        # objects = VGroup(
        #     Eddy(),
        #     DoublePendulum(),
        #     Diffusion(),
        # )

        # for word, obj in zip(words, objects):
        for word in words:
            # obj.next_to(word, RIGHT)
            self.play(
                FadeInFromDown(word),
                # VFadeIn(obj)
            )
        self.wait(3)

    def rigorous_definition(self):
        randy = Randolph()
        randy.move_to(FRAME_WIDTH * RIGHT / 4)
        randy.change("pondering", self.words[1])

        self.play(FadeIn(randy))
        self.play(Blink(randy))
        self.wait()
        self.play(randy.change, "shruggie")
        for x in range(2):
            self.play(Blink(randy))
            self.wait()
        self.play(randy.look, LEFT)
        self.wait(2)
        self.play(randy.look, UP)
        self.play(Blink(randy))
        self.wait()


class BumpyPlaneRide(Scene):
    def construct(self):
        plane = SVGMobject(file_name="plane2")
        self.add(plane)

        total_time = 0
        while total_time < 10:
            point = 2 * np.append(np.random.random(2), 2) + DL
            point *= 0.2
            time = 0.2 * random.random()
            total_time += time
            arc = PI * random.random() - PI / 2
            self.play(
                plane.move_to, point,
                run_time=time,
                path_arc=arc
            )


class PureAirfoilFlowCopy(PureAirfoilFlow):
    def modify_vector_field(self, vector_field):
        PureAirfoilFlow.modify_vector_field(self, vector_field)
        vector_field.set_fill(opacity=0.1)
        vector_field.set_stroke(opacity=0.1)


class LaminarFlowLabel(Scene):
    def construct(self):
        words = TextMobject("Laminar flow")
        words.scale(1.5)
        words.to_edge(UP)
        subwords = TextMobject(
            "`Lamina', in Latin, means \\\\"
            "``a thin sheet of material''",
            tex_to_color_map={"Lamina": YELLOW},
            arg_separator="",
        )
        subwords.next_to(words, DOWN, MED_LARGE_BUFF)
        VGroup(words, subwords).set_background_stroke(width=4)
        self.play(Write(words))
        self.wait()
        self.play(FadeInFromDown(subwords))
        self.wait()


class HighCurlFieldBreakingLayers(Scene):
    CONFIG = {
        "flow_anim": VectorFieldSubmobjectFlow,
    }

    def construct(self):
        lines = VGroup(*[
            self.get_line()
            for x in range(20)
        ])
        lines.arrange_submobjects(DOWN, buff=MED_SMALL_BUFF)
        lines[0::2].set_color(BLUE)
        lines[1::2].set_color(RED)
        all_dots = VGroup(*it.chain(*lines))

        def func(p):
            vect = four_swirls_function(p)
            norm = get_norm(vect)
            if norm > 2:
                vect *= 4.0 / get_norm(vect)**2
            return vect

        self.add(lines)
        self.add(self.flow_anim(all_dots, func))
        self.wait(16)

    def get_line(self):
        line = VGroup(*[Dot() for x in range(100)])
        line.set_height(0.1)
        line.arrange_submobjects(RIGHT, buff=0)
        line.set_width(10)
        return line


class HighCurlFieldBreakingLayersLines(HighCurlFieldBreakingLayers):
    CONFIG = {
        "flow_anim": VectorFieldPointFlow
    }

    def get_line(self):
        line = Line(LEFT, RIGHT)
        line.insert_n_anchor_points(500)
        line.set_width(5)
        return line


class VorticitySynonyms(Scene):
    def construct(self):
        words = VGroup(
            TextMobject("High", "vorticity"),
            TexMobject(
                "\\text{a.k.a} \\,",
                "|\\nabla \\times \\vec{\\textbf{v}}| > 0"
            ),
            TextMobject("a.k.a", "high", "swirly-swirly", "factor"),
        )
        words[0].set_color_by_tex("vorticity", BLUE)
        words[1].set_color_by_tex("nabla", BLUE)
        words[2].set_color_by_tex("swirly", BLUE)
        words.arrange_submobjects(
            DOWN,
            aligned_edge=LEFT,
            buff=MED_LARGE_BUFF
        )

        for word in words:
            word.add_background_rectangle()
            self.play(FadeInFromDown(word))
            self.wait()


class VorticityDoesNotImplyTurbulence(TeacherStudentsScene):
    def construct(self):
        t_to_v = TextMobject(
            "Turbulence", "$\\Rightarrow$", "Vorticity",
        )
        v_to_t = TextMobject(
            "Vorticity", "$\\Rightarrow$", "Turbulence",
        )
        for words in t_to_v, v_to_t:
            words.move_to(self.hold_up_spot, DR)
            words.set_color_by_tex_to_color_map({
                "Vorticity": BLUE,
                "Turbulence": GREEN,
            })
        v_to_t.submobjects.reverse()
        cross = Cross(v_to_t[1])

        morty = self.teacher
        self.play(
            morty.change, "raise_right_hand",
            FadeInFromDown(t_to_v)
        )
        self.wait()
        self.play(t_to_v.shift, 2 * UP,)
        self.play(
            TransformFromCopy(t_to_v, v_to_t, path_arc=PI / 2),
            self.get_student_changes(
                "erm", "confused", "sassy",
                run_time=1
            ),
            ShowCreation(cross, run_time=2),
        )
        self.add(cross)
        self.wait(4)


class SurroundingRectangleSnippet(Scene):
    def construct(self):
        rect = Rectangle()
        rect.set_color(YELLOW)
        rect.set_stroke(width=5)
        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))


class FeynmanOnTurbulence(Scene):
    def construct(self):
        feynman = ImageMobject("Feynman_Woods", height=4)
        name = TextMobject("Richard Feynman")
        name.next_to(feynman, DOWN)
        quote = TextMobject(
            "``", "Turbulence", "is the most\\\\"
            "important", "unsolved problem\\\\",
            "of classical physics.''",
            tex_to_color_map={
                "Turbulence": BLUE,
                "unsolved problem\\\\": YELLOW,
            },
        )
        quote[0].shift(SMALL_BUFF * RIGHT)
        quote.next_to(feynman, RIGHT)
        Group(feynman, name, quote).center()

        self.play(
            FadeInFrom(feynman, UP),
            FadeInFrom(name, DOWN),
            Write(quote, run_time=4, lag_factor=5)
        )
        self.wait()


class ShowNavierStokesEquations(Scene):
    def construct(self):
        self.introduce_equations()
        self.ask_about_evolution()
        self.ask_about_reasonable()
        self.ask_about_blowup()
        self.show_money()

    def introduce_equations(self):
        name = TextMobject("Navier-Stokes equations (incompressible)")
        equations = NavierStokesEquations()
        name.to_edge(UP)
        equations.next_to(name, DOWN, MED_LARGE_BUFF)
        labels = equations.get_labels()
        parts = equations.get_parts()
        newtons_second = TextMobject(
            "Newton's 2nd law \\\\ $ma = F$"
        )
        newtons_second.next_to(parts, DOWN)
        variables = TexMobject(
            "&\\textbf{v}", "\\text{ is velocity}\\\\",
            "&\\rho", "\\text{ is density}\\\\",
            "&p{}", "\\text{ is pressure}\\\\",
            "&\\mu", "\\text{ is viscosity}\\\\",
            tex_to_color_map=NavierStokesEquations.CONFIG["tex_to_color_map"]
        )
        variables.to_corner(DL)

        self.play(FadeInFromDown(equations))
        self.play(Write(name))
        self.play(LaggedStart(
            FadeInFrom, variables,
            lambda m: (m, RIGHT),
        ))
        self.wait()
        self.play(Write(newtons_second))
        self.wait()
        self.play(
            FadeInFromDown(labels[0]),
            newtons_second.next_to, variables, RIGHT, LARGE_BUFF
        )
        self.play(CircleThenFadeAround(parts[0]))
        self.wait()
        self.play(LaggedStart(FadeInFrom, labels[1:]))
        self.wait(3)
        self.play(LaggedStart(
            FadeOut, VGroup(*it.chain(labels, variables, newtons_second))
        ))

        self.equations = equations

    def ask_about_evolution(self):
        words = TextMobject(
            "Given a start state...",
            "...how does it evolve?"
        )
        words.arrange_submobjects(RIGHT, buff=2)

        words.next_to(self.equations, DOWN, LARGE_BUFF)

        self.play(Write(words[0]))
        self.wait()
        self.play(Write(words[1]))
        self.wait(2)
        self.play(FadeOut(words))

    def ask_about_reasonable(self):
        question = TextMobject(
            "Do ``reasonable'' \\\\"
            "solutions always\\\\"
            "exist?"
        )
        self.play(FadeInFromDown(question))
        self.wait()

        self.reasonable_question = question

    def ask_about_blowup(self):
        axes, graph = self.get_axes_and_graph()
        question = TextMobject("Is this possible?")
        question.set_color(YELLOW)
        question.move_to(axes.get_corner(UR), LEFT)
        question.align_to(axes, UP)
        q_arrow = Arrow(
            question.get_bottom(),
            graph.point_from_proportion(0.8),
            buff=SMALL_BUFF,
            use_rectangular_stem=False,
            path_arc=-60 * DEGREES
        )
        q_arrow.set_stroke(WHITE, 3)
        morty = Mortimer()
        morty.to_corner(DR)
        morty.change('confused', graph)

        self.play(
            Write(axes, run_time=1),
            self.reasonable_question.to_edge, LEFT,
            self.reasonable_question.shift, DOWN,
        )
        self.play(
            Write(question),
            ShowCreation(graph),
            FadeIn(morty),
        )
        self.add(q_arrow, morty)
        self.play(ShowCreation(q_arrow), Blink(morty))
        self.wait()
        self.play(morty.look_at, question)
        self.wait()
        self.play(morty.change, "maybe", graph)
        self.wait(2)
        to_fade = VGroup(question, q_arrow, axes, graph)
        self.play(
            LaggedStart(FadeOut, to_fade),
            morty.change, "pondering"
        )
        self.wait(2)
        self.play(Blink(morty))
        self.wait(2)

        self.morty = morty

    def show_money(self):
        # Million dollar problem
        problem = TextMobject(
            "Navier-Stokes existence \\\\ and smoothness problems"
        )
        money = TextMobject("\\$1{,}000{,}000")
        money.set_color(GREEN)
        money.next_to(problem, DOWN)
        pi1 = Randolph()
        pi2 = self.morty
        pi1.to_corner(DL)
        pis = VGroup(pi1, pi2)
        for pi in pis:
            pi.change("pondering")
            pi.money_eyes = VGroup()
            for eye in pi.eyes:
                cash = TexMobject("\\$")
                cash.set_color(GREEN)
                cash.replace(eye, dim_to_match=1)
                pi.money_eyes.add(cash)

        self.play(
            ReplacementTransform(
                self.reasonable_question,
                problem,
            ),
            pi2.look_at, problem,
            pi1.look_at, problem,
            VFadeIn(pi1),
        )
        self.wait()
        self.play(FadeInFromLarge(money))
        self.play(
            pi1.change, "hooray",
            pi2.change, "hooray",
        )
        self.play(
            ReplacementTransform(pi1.pupils, pi1.money_eyes),
            ReplacementTransform(pi2.pupils, pi2.money_eyes),
        )
        self.wait()

    # Helpers
    def get_axes_and_graph(self):
        axes = Axes(
            x_min=-1,
            x_max=5,
            y_min=-1,
            y_max=5,
        )
        time = TextMobject("Time")
        time.next_to(axes.x_axis, RIGHT)
        ke = TextMobject("Kinetic energy")
        ke.next_to(axes.y_axis, UP)
        axes.add(time, ke)
        axes.set_height(4)
        axes.center()
        axes.to_edge(DOWN)
        v_line = DashedLine(
            axes.coords_to_point(4, 0),
            axes.coords_to_point(4, 5),
        )
        axes.add(v_line)
        graph = axes.get_graph(
            lambda x: -1.0 / (x - 4),
            x_min=0.01,
            x_max=3.8,
        )
        graph.set_color(BLUE)
        return axes, graph


class NewtonsSecond(Scene):
    def construct(self):
        square = Square(
            stroke_color=WHITE,
            fill_color=LIGHT_GREY,
            fill_opacity=0.5,
            side_length=1
        )
        label = TexMobject("m")
        label.scale(1.5)
        label.move_to(square)
        square.add(label)
        square.save_state()
        arrows = VGroup(
            Vector(0.5 * UP).next_to(square, UP, buff=0),
            Vector(RIGHT).next_to(square, RIGHT, buff=0),
        )

        self.play(
            square.shift, 4 * RIGHT + 2 * UP,
            rate_func=lambda t: t**2,
            run_time=2
        )
        self.wait()
        square.restore()
        self.play(
            LaggedStart(GrowArrow, arrows)
        )
        square.add(arrows)
        self.play(
            square.shift, 4 * RIGHT + 2 * UP,
            rate_func=lambda t: t**2,
            run_time=2
        )
        self.wait()


class CandleLabel(Scene):
    def construct(self):
        word = TextMobject("Candle")
        arrow = Vector(DR, color=WHITE)
        arrow.move_to(word.get_bottom() + SMALL_BUFF * DOWN, UL)
        self.play(
            FadeInFromDown(word),
            GrowArrow(arrow)
        )
        self.wait()


class FiguresOfFluidDynamics(Scene):
    def construct(self):
        names = [
            "Leonhard Euler",
            "George Stokes",
            "Hermann von Helmholtz",
            "Lewis Richardson",
            "Geoffrey Taylor",
            "Andrey Kolmogorov",
        ]
        images = Group(*[
            ImageMobject(name.replace(" ", "_"), height=3)
            for name in names
        ])
        images.arrange_submobjects(RIGHT, buff=MED_SMALL_BUFF)
        image_groups = Group()
        for image, name in zip(images, names):
            name_mob = TextMobject(name)
            name_mob.scale(0.6)
            name_mob.next_to(image, DOWN)
            image_groups.add(Group(image, name_mob))
        image_groups.arrange_submobjects_in_grid(2, 3)
        image_groups.set_height(FRAME_HEIGHT - 1)

        self.play(LaggedStart(
            FadeInFromDown, image_groups,
            lag_ratio=0.5,
            run_time=3
        ))
        self.wait()
        to_fade = image_groups[:-1]
        to_fade.generate_target()
        to_fade.target.space_out_submobjects(3)
        to_fade.target.shift(3 * UL)
        to_fade.target.fade(1)
        self.play(
            MoveToTarget(to_fade, remover=True),
            image_groups[-1].set_height, 5,
            image_groups[-1].center,
        )
        self.wait()


class KineticEnergyBreakdown(Scene):
    def construct(self):
        title = TextMobject("Kinetic energy breakdown")
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT).set_width(FRAME_WIDTH)
        h_line.next_to(title, DOWN)
        v_line = Line(h_line.get_center(), FRAME_HEIGHT * DOWN / 2)
        lc_title = TextMobject("Simpler physics")
        lc_title.set_color(YELLOW)
        rc_title = TextMobject("Turbulence physics")
        rc_title.set_color(GREEN)
        for word, vect in (lc_title, LEFT), (rc_title, RIGHT):
            word.next_to(h_line, DOWN)
            word.shift(FRAME_WIDTH * vect / 4)

        left_items = VGroup(
            TextMobject("- Big moving things"),
            TextMobject("- Heat"),
        )
        left_items.arrange_submobjects(DOWN, aligned_edge=LEFT)
        left_items.next_to(lc_title, DOWN, MED_LARGE_BUFF)
        left_items.to_edge(LEFT)

        self.play(
            Write(VGroup(*it.chain(
                title, h_line, v_line, lc_title, rc_title
            )))
        )
        self.wait()
        for item in left_items:
            self.play(FadeInFrom(item))
            self.wait()


class MovingCar(Scene):
    def construct(self):
        car = Car()
        x = 3
        car.move_to(x * LEFT)
        self.play(MoveCar(car, x * RIGHT, run_time=4))


class Heat(Scene):
    def construct(self):
        box = Square(
            side_length=2,
            stroke_color=WHITE,
        )
        balls = VGroup(*[
            self.get_ball(box)
            for x in range(20)
        ])

        self.add(box, balls)
        self.wait(20)

    def get_ball(self, box):
        speed_factor = random.random()
        ball = Dot(
            radius=0.05,
            color=interpolate_color(BLUE, RED, speed_factor)
        )
        speed = 2 + 3 * speed_factor
        direction = rotate_vector(RIGHT, TAU * random.random())
        ball.velocity = speed * direction
        x0, y0, z0 = box.get_corner(DL)
        x1, y1, z1 = box.get_corner(UR)
        ball.move_to(np.array([
            interpolate(x0, x1, random.random()),
            interpolate(y0, y1, random.random()),
            0
        ]))

        def update(ball, dt):
            ball.shift(ball.velocity * dt)
            if ball.get_left()[0] < box.get_left()[0]:
                ball.velocity[0] = abs(ball.velocity[0])
            if ball.get_right()[0] > box.get_right()[0]:
                ball.velocity[0] = -abs(ball.velocity[0])
            if ball.get_bottom()[1] < box.get_bottom()[1]:
                ball.velocity[1] = abs(ball.velocity[1])
            if ball.get_top()[1] > box.get_top()[1]:
                ball.velocity[1] = -abs(ball.velocity[1])
            return ball

        ball.add_updater(update)
        return ball


class GrowArrowScene(Scene):
    def construct(self):
        arrow = Arrow(UP, DOWN, color=WHITE)
        self.play(GrowArrow(arrow))
        self.wait()


class Poem(Scene):
    def construct(self):
        picture = ImageMobject("Lewis_Richardson")
        picture.set_height(4)
        picture.center().to_edge(LEFT, buff=LARGE_BUFF)

        title = TextMobject("Poem by Lewis F. Richardson")
        title.to_edge(UP)

        poem_text = """
            Big{\\,\\,}whirls have little{\\,\\,}whirls\\\\
            which feed on their velocity,\\\\
            And little{\\,\\,}whirls have lesser{\\,\\,}whirls\\\\
            And so on to viscosity.\\\\
        """
        poem_words = [s for s in poem_text.split(" ") if s]
        poem = TextMobject(*poem_words, alignment="")
        poem.next_to(picture, RIGHT, LARGE_BUFF)

        self.add(picture)
        self.play(FadeInFrom(title, DOWN))
        self.wait()
        for word in poem:
            if "whirl" in word.get_tex_string():
                word.set_color(BLUE)
            self.play(ShowWord(word))
            self.wait(0.005 * len(word)**1.5)


class SwirlDiameterD(Scene):
    def construct(self):
        kwargs = {
            "path_arc": PI,
            "buff": SMALL_BUFF,
            "use_rectangular_stem": False,
            "color": WHITE
        }
        swirl = VGroup(
            Arrow(RIGHT, LEFT, **kwargs),
            Arrow(LEFT, RIGHT, **kwargs),
        )
        swirl.set_stroke(width=5)
        f = 1.5
        swirl.scale(f)

        h_line = DashedLine(
            f * LEFT, f * RIGHT,
            color=YELLOW,
        )
        D_label = TexMobject("D")
        D_label.scale(2)
        D_label.next_to(h_line, UP, SMALL_BUFF)
        D_label.match_color(h_line)
        # diam = VGroup(h_line, D_label)

        self.play(*map(ShowCreation, swirl))
        self.play(
            GrowFromCenter(h_line),
            FadeInFrom(D_label, UP),
        )
        self.wait()


class KolmogorovGraph(Scene):
    def construct(self):
        axes = Axes(
            x_min=-1,
            y_min=-1,
            x_max=7,
            y_max=9,
            y_axis_config={
                "unit_size": 0.7,
            }
        )
        axes.center().shift(1.5 * RIGHT)
        x_label = TexMobject("\\log(D)")
        x_label.next_to(axes.x_axis.get_right(), UP)
        y_label = TexMobject("\\log(\\text{K.E. at length scale D})")
        y_label.scale(0.8)
        y_label.next_to(axes.y_axis.get_top(), LEFT)
        y_label.shift_onto_screen()
        axes.add(x_label, y_label)

        v_lines = VGroup(*[
            DashedLine(
                axes.coords_to_point(x, 0),
                axes.coords_to_point(x, 9),
                color=YELLOW,
                stroke_width=1
            )
            for x in [0.5, 5]
        ])
        inertial_subrange = TextMobject("``Inertial subrange''")
        inertial_subrange.scale(0.7)
        inertial_subrange.next_to(v_lines.get_bottom(), UP)

        def func(x):
            if 0.5 < x < 5:
                return (5 / 3) * x
            elif x < 0.5:
                return 5 * (x - 0.5) + 0.5 * (5 / 3)
            elif x > 5:
                return np.log(x) + (5 / 3) * 5 - np.log(5)

        graph = axes.get_graph(func, x_min=0.3, x_max=7)

        prop_label = TexMobject("\\text{K.E.} \\propto D^{5/3}")
        prop_label.next_to(
            graph.point_from_proportion(0.5), UL,
            buff=0
        )

        self.add(axes)
        self.play(ShowCreation(graph))
        self.play(FadeInFromDown(prop_label))
        self.wait()
        self.add(v_lines)
        self.play(Write(inertial_subrange))
        self.wait()


class TechnicalNote(Scene):
    def construct(self):
        title = TextMobject("Technical note:")
        title.to_edge(UP)
        title.set_color(RED)
        self.add(title)

        words = TextMobject("""
            This idea of quantifying the energy held at different
            length scales is typically defined
            in terms of an ``energy spectrum'' involving the Fourier
            transform of a function measuring the correlations
            between the fluid's velocities at different points in space.
            I know, yikes!
            \\quad\\\\
            \\quad\\\\
            Building up the relevant background for that is a bit cumbersome,
            so we'll be thinking about the energy at different scales in
            terms of all eddy's with a given diameter.  This is admittedly
            a less well-defined notion, but it does capture the spirit
            of Kolmogorov's result.
            \\quad\\\\
            \\quad\\\\
            See the links in the description for more details,
            if you're curious.
        """, alignment="")
        words.scale(0.75)
        words.next_to(title, DOWN, LARGE_BUFF)

        self.add(title, words)


class FiveThirds(TeacherStudentsScene):
    def construct(self):
        words = TextMobject(
            "5/3", "is a sort of fundamental\\\\ constant of turbulence"
        )
        self.teacher_says(words)
        self.change_student_modes("pondering", "maybe", "erm")
        self.play(
            FadeOut(self.teacher.bubble),
            FadeOut(words[1]),
            self.teacher.change, "raise_right_hand",
            words[0].scale, 1.5,
            words[0].move_to, self.hold_up_spot
        )
        self.change_student_modes("thinking", "pondering", "hooray")
        self.wait(3)


class TurbulenceGifLabel(Scene):
    def construct(self):
        title = TextMobject("Turbulence in 2d")
        title.to_edge(UP)

        attribution = TextMobject(
            "Animation by Gabe Weymouth (@gabrielweymouth)"
        )
        attribution.scale(0.5)
        attribution.to_edge(DOWN)

        self.play(Write(title))
        self.play(FadeInFrom(attribution, UP))
        self.wait()


class VortexStretchingLabel(Scene):
    def construct(self):
        title = TextMobject("Vortex stretching")
        self.play(Write(title))
        self.wait()


class VortedStretching(ThreeDScene):
    CONFIG = {
        "n_circles": 200,
    }

    def construct(self):
        axes = ThreeDAxes()
        axes.set_stroke(width=1)
        self.add(axes)
        self.move_camera(
            phi=70 * DEGREES,
            theta=-145 * DEGREES,
            run_time=0,
        )
        self.begin_ambient_camera_rotation()

        short_circles = self.get_cylinder_circles(2, 0.5, 0.5)
        tall_circles = short_circles.copy().scale(0.125)
        tall_circles.stretch(16 * 4, 2)
        torus_circles = tall_circles.copy()
        for circle in torus_circles:
            circle.shift(RIGHT)
            z = circle.get_center()[2]
            circle.shift(z * IN)
            angle = PI * z / 2
            circle.rotate(angle, axis=DOWN, about_point=ORIGIN)

        circles = short_circles.copy()
        flow_lines = self.get_flow_lines(circles)

        self.add(circles, flow_lines)
        self.play(LaggedStart(ShowCreation, circles))
        self.wait(5)
        self.play(Transform(circles, tall_circles, run_time=3))
        self.wait(10)
        self.play(Transform(
            circles, torus_circles,
            run_time=3
        ))
        self.wait(10)

    def get_cylinder_circles(self, radius, radius_var, max_z):
        return VGroup(*[
            ParametricFunction(
                lambda t: np.array([
                    np.cos(TAU * t) * r,
                    np.sin(TAU * t) * r,
                    z
                ]),
                **self.get_circle_kwargs()
            )
            for z in sorted(max_z * np.random.random(self.n_circles))
            for r in [radius + radius_var * random.random()]
        ]).center()

    def get_torus_circles(self, out_r, in_r, in_r_var):
        result = VGroup()
        for u in sorted(np.random.random(self.n_circles)):
            r = in_r + in_r_var * random.random()
            circle = ParametricFunction(
                lambda t: r * np.array([
                    np.cos(TAU * t),
                    np.sin(TAU * t),
                    0,
                ]),
                **self.get_circle_kwargs()
            )
            circle.shift(out_r * RIGHT)
            circle.rotate(
                TAU * u - PI,
                about_point=ORIGIN,
                axis=DOWN,
            )
            result.add(circle)
        return result

    def get_flow_lines(self, circle_group):
        window = 0.3

        def update_circle(circle, dt):
            circle.total_time += dt
            diameter = get_norm(
                circle.template.point_from_proportion(0) -
                circle.template.point_from_proportion(0.5)
            )
            modulus = np.sqrt(diameter) + 0.1
            alpha = (circle.total_time % modulus) / modulus
            circle.pointwise_become_partial(
                circle.template,
                max(interpolate(-window, 1, alpha), 0),
                min(interpolate(0, 1 + window, alpha), 1),
            )

        result = VGroup()
        for template in circle_group:
            circle = template.deepcopy()
            circle.set_stroke(
                color=interpolate_color(BLUE_A, BLUE_E, random.random()),
                # width=3 * random.random()
                width=1,
            )
            circle.template = template
            circle.total_time = 4 * random.random()
            circle.add_updater(update_circle)
            result.add(circle)
        return result

    def get_circle_kwargs(self):
        return {
            "stroke_color": BLACK,
            "stroke_width": 0,
        }


class TurbulenceEndScreen(PatreonEndScreen):
    CONFIG = {
        "specific_patrons": [
            "1stViewMaths",
            "Adrian Robinson",
            "Alexis Olson",
            "Andrew Busey",
            "Ankalagon",
            "Art Ianuzzi",
            "Awoo",
            "Ayan Doss",
            "Bernd Sing",
            "Boris Veselinovich",
            "Brian Staroselsky",
            "Britt Selvitelle",
            "Carla Kirby",
            "Charles Southerland",
            "Chris Connett",
            "Christian Kaiser",
            "Clark Gaebel",
            "Cooper Jones",
            "Danger Dai",
            "Dave B",
            "Dave Kester",
            "David Clark",
            "Delton Ding",
            "Devarsh Desai",
            "eaglle",
            "Eric Younge",
            "Eryq Ouithaqueue",
            "Federico Lebron",
            "Florian Chudigiewitsch",
            "Giovanni Filippi",
            "Hal Hildebrand",
            "Igor Napolskikh",
            "Jacob Magnuson",
            "Jameel Syed",
            "James Hughes",
            "Jan Pijpers",
            "Jason Hise",
            "Jeff Linse",
            "Jeff Straathof",
            "Jerry Ling",
            "John Griffith",
            "John Haley",
            "John V Wertheim",
            "Jonathan Eppele",
            "Jonathan Wilson",
            "Jordan Scales",
            "Joseph John Cox",
            "Julian Pulgarin",
            "Kai-Siang Ang",
            "Kanan Gill",
            "L0j1k",
            "Linh Tran",
            "Luc Ritchie",
            "Ludwig Schubert",
            "Lukas -krtek.net- Novy",
            "Magister Mugit",
            "Magnus Dahlström",
            "Mark B Bahu",
            "Markus Persson",
            "Mathew Bramson",
            "Mathias Jansson",
            "Matt Langford",
            "Matt Roveto",
            "Matthew Cocke",
            "Mehdi Razavi",
            "Michael Faust",
            "Michael Hardel",
            "Mustafa Mahdi",
            "Márton Vaitkus",
            "Nero Li",
            "Oliver Steele",
            "Omar Zrien",
            "Peter Ehrnstrom",
            "Prasant Jagannath",
            "Randy C. Will",
            "Richard Burgmann",
            "Ripta Pasay",
            "Rish Kundalia",
            "Robert Teed",
            "Roobie",
            "Ryan Atallah",
            "Ryan Williams",
            "Sindre Reino Trosterud",
            "Solara570",
            "Song Gao",
            "Steven Soloway",
            "Steven Tomlinson",
            "Stevie Metke",
            "Ted Suzman",
            "Valeriy Skobelev",
            "Xavier Bernard",
            "Yaw Etse",
            "YinYangBalance.Asia",
            "Zach Cardwell",
        ],
    }


class LaserWord(Scene):
    def construct(self):
        self.add(TextMobject("Laser").scale(2))


class TurbulenceWord(Scene):
    def construct(self):
        self.add(TextMobject("Turbulence").scale(2))


class ArrowScene(Scene):
    def construct(self):
        arrow = Arrow(LEFT, RIGHT, color=WHITE)
        arrow.add_to_back(arrow.copy().set_stroke(BLACK, 5))
        self.add(arrow)
