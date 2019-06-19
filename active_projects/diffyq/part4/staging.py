from manimlib.imports import *
from active_projects.ode.part3.temperature_graphs import TemperatureGraphScene
from active_projects.ode.part2.wordy_scenes import WriteHeatEquationTemplate


class RelationToOtherVideos(Scene):
    CONFIG = {
        "camera_config": {
            "background_color": DARK_GREY,
        },
    }

    def construct(self):
        # Show three videos
        videos = self.get_video_thumbnails()
        brace = Brace(videos, UP)
        text = TextMobject("Heat equation")
        text.scale(2)
        text.next_to(brace, UP)

        self.play(
            LaggedStartMap(
                FadeInFrom, videos,
                lambda m: (m, LEFT),
                lag_ratio=0.4,
                run_time=2,
            ),
            GrowFromCenter(brace),
            FadeInFromDown(text),
        )
        self.wait()
        group = Group(text, brace, videos)

        # Show Fourier thinking
        fourier = ImageMobject("Joseph Fourier")
        fourier.set_height(4)
        fourier.to_edge(RIGHT)
        group.generate_target()
        group.target.to_edge(DOWN)
        fourier.align_to(group.target[0], DOWN)
        bubble = ThoughtBubble(
            direction=RIGHT,
            width=3,
            height=2,
            fill_opacity=0.5,
            stroke_color=WHITE,
        )
        bubble[-1].shift(0.25 * DOWN + 0.5 * LEFT)
        bubble[:-1].rotate(20 * DEGREES)
        for mob in bubble[:-1]:
            mob.rotate(-20 * DEGREES)
        bubble.move_tip_to(
            fourier.get_corner(UL) + DOWN
        )
        bubble.to_edge(UP, buff=SMALL_BUFF)

        self.play(
            MoveToTarget(group),
            FadeInFrom(fourier, LEFT)
        )
        self.play(Write(bubble, run_time=1))
        self.wait()

        # Discount first two
        first_two = videos[:2]
        first_two.generate_target()
        first_two.target.scale(0.5)
        first_two.target.to_corner(DL)
        new_brace = Brace(first_two.target, UP)

        self.play(
            # fourier.scale, 0.8,
            fourier.match_x, new_brace,
            fourier.to_edge, UP,
            MoveToTarget(first_two),
            Transform(brace, new_brace),
            text.scale, 0.7,
            text.next_to, new_brace, UP,
            FadeOutAndShift(bubble, LEFT),
        )
        self.play(
            videos[2].scale, 1.7,
            videos[2].to_corner, UR,
        )
        self.wait()

    #
    def get_video_thumbnails(self):
        thumbnails = Group(
            ImageMobject("diffyq_part2_thumbnail"),
            ImageMobject("diffyq_part3_thumbnail"),
            ImageMobject("diffyq_part4_thumbnail"),
        )
        for thumbnail in thumbnails:
            thumbnail.set_height(4)
            thumbnail.add(SurroundingRectangle(
                thumbnail,
                color=WHITE,
                stroke_width=2,
                buff=0
            ))
        thumbnails.arrange(RIGHT, buff=LARGE_BUFF)
        thumbnails.set_width(FRAME_WIDTH - 1)
        return thumbnails


class ShowLinearity(WriteHeatEquationTemplate, TemperatureGraphScene):
    CONFIG = {
        "temp_text": "Temp",
        "alpha": 0.1,
        "axes_config": {
            "z_max": 2,
            "z_min": -2,
            "z_axis_config": {
                "tick_frequency": 0.5,
                "unit_size": 1.5,
            },
        },
        "default_surface_config": {
            "resolution": (16, 16)
            # "resolution": (4, 4)
        },
        "freqs": [2, 5],
    }

    def setup(self):
        TemperatureGraphScene.setup(self)
        WriteHeatEquationTemplate.setup(self)

    def construct(self):
        self.init_camera()
        self.add_three_graphs()
        self.show_words()
        self.add_function_labels()
        self.change_scalars()

    def init_camera(self):
        self.camera.set_distance(1000)

    def add_three_graphs(self):
        axes_group = self.get_axes_group()
        axes0, axes1, axes2 = axes_group
        freqs = self.freqs
        scalar_trackers = Group(
            ValueTracker(1),
            ValueTracker(1),
        )
        graphs = VGroup(
            self.get_graph(axes0, [freqs[0]], [scalar_trackers[0]]),
            self.get_graph(axes1, [freqs[1]], [scalar_trackers[1]]),
            self.get_graph(axes2, freqs, scalar_trackers),
        )

        plus = TexMobject("+").scale(2)
        equals = TexMobject("=").scale(2)
        plus.move_to(midpoint(
            axes0.get_right(),
            axes1.get_left(),
        ))
        equals.move_to(midpoint(
            axes1.get_right(),
            axes2.get_left(),
        ))

        self.add(axes_group)
        self.add(graphs)
        self.add(plus)
        self.add(equals)

        self.axes_group = axes_group
        self.graphs = graphs
        self.scalar_trackers = scalar_trackers
        self.plus = plus
        self.equals = equals

    def show_words(self):
        equation = self.get_d1_equation()
        name = TextMobject("Heat equation")
        name.next_to(equation, DOWN)
        name.set_color_by_gradient(RED, YELLOW)
        group = VGroup(equation, name)
        group.to_edge(UP)

        shift_val = 0.5 * RIGHT

        arrow = Vector(1.5 * RIGHT)
        arrow.move_to(group)
        arrow.shift(shift_val)
        linear_word = TextMobject("``Linear''")
        linear_word.scale(2)
        linear_word.next_to(arrow, RIGHT)

        self.add(group)
        self.wait()
        self.play(
            ShowCreation(arrow),
            group.next_to, arrow, LEFT
        )
        self.play(FadeInFrom(linear_word, LEFT))
        self.wait()

    def add_function_labels(self):
        axes_group = self.axes_group
        graphs = self.graphs

        solution_labels = VGroup()
        for axes in axes_group:
            label = TextMobject("Solution", "$\\checkmark$")
            label.set_color_by_tex("checkmark", GREEN)
            label.next_to(axes, DOWN)
            solution_labels.add(label)

        kw = {
            "tex_to_color_map": {
                "T_1": BLUE,
                "T_2": GREEN,
            }
        }
        T1 = TexMobject("a", "T_1", **kw)
        T2 = TexMobject("b", "T_2", **kw)
        T_sum = TexMobject("T_1", "+", "T_2", **kw)
        T_sum_with_scalars = TexMobject(
            "a", "T_1", "+", "b", "T_2", **kw
        )

        T1.next_to(graphs[0], UP)
        T2.next_to(graphs[1], UP)
        T_sum.next_to(graphs[2], UP)
        T_sum.shift(SMALL_BUFF * DOWN)
        T_sum_with_scalars.move_to(T_sum)

        a_brace = Brace(T1[0], UP, buff=SMALL_BUFF)
        b_brace = Brace(T2[0], UP, buff=SMALL_BUFF)
        s1_decimal = DecimalNumber()
        s1_decimal.match_color(T1[1])
        s1_decimal.next_to(a_brace, UP, SMALL_BUFF)
        s1_decimal.add_updater(lambda m: m.set_value(
            self.scalar_trackers[0].get_value()
        ))
        s2_decimal = DecimalNumber()
        s2_decimal.match_color(T2[1])
        s2_decimal.next_to(b_brace, UP, SMALL_BUFF)
        s2_decimal.add_updater(lambda m: m.set_value(
            self.scalar_trackers[1].get_value()
        ))

        self.play(
            FadeInFrom(T1[1], DOWN),
            FadeInFrom(solution_labels[0], UP),
        )
        self.play(
            FadeInFrom(T2[1], DOWN),
            FadeInFrom(solution_labels[1], UP),
        )
        self.wait()
        self.play(
            TransformFromCopy(T1[1], T_sum[0]),
            TransformFromCopy(T2[1], T_sum[2]),
            TransformFromCopy(self.plus, T_sum[1]),
            *[
                Transform(
                    graph.copy().set_fill(opacity=0),
                    graphs[2].copy().set_fill(opacity=0),
                    remover=True
                )
                for graph in graphs[:2]
            ]
        )
        self.wait()
        self.play(FadeInFrom(solution_labels[2], UP))
        self.wait()

        # Show constants
        self.play(
            FadeIn(T1[0]),
            FadeIn(T2[0]),
            FadeIn(a_brace),
            FadeIn(b_brace),
            FadeIn(s1_decimal),
            FadeIn(s2_decimal),
            FadeOut(T_sum),
            FadeIn(T_sum_with_scalars),
        )

    def change_scalars(self):
        s1, s2 = self.scalar_trackers

        kw = {
            "run_time": 2,
        }
        for graph in self.graphs:
            graph.resume_updating()
        self.play(s2.set_value, -0.5, **kw)
        self.play(s1.set_value, -0.2, **kw)
        self.play(s2.set_value, 1.5, **kw)
        self.play(s1.set_value, 1.2)
        self.play(s2.set_value, 0.3)
        self.wait()

    #
    def get_axes_group(self):
        axes_group = VGroup(*[
            self.get_axes()
            for x in range(3)
        ])
        axes_group.arrange(RIGHT, buff=2)
        axes_group.set_width(FRAME_WIDTH - 1)
        axes_group.to_edge(DOWN, buff=1)
        return axes_group

    def get_axes(self):
        axes = self.get_three_d_axes()
        # axes.input_plane.set_fill(opacity=0)
        # axes.input_plane.set_stroke(width=0.5)
        # axes.add(axes.input_plane)
        self.orient_three_d_mobject(axes)
        axes.rotate(-5 * DEGREES, UP)
        axes.set_width(4)
        axes.x_axis.label.next_to(
            axes.x_axis.get_end(), DOWN,
            buff=2 * SMALL_BUFF
        )
        return axes

    def get_graph(self, axes, freqs, scalar_trackers):
        L = axes.x_max
        a = self.alpha

        def func(x, t):
            scalars = [st.get_value() for st in scalar_trackers]
            return np.sum([
                s * np.cos(k * x) * np.exp(-a * (k**2) * t)
                for freq, s in zip(freqs, scalars)
                for k in [freq * PI / L]
            ])

        def get_surface_graph_group():
            return VGroup(
                self.get_surface(axes, func),
                self.get_time_slice_graph(axes, func, t=0),
            )

        result = always_redraw(get_surface_graph_group)
        result.suspend_updating()
        return result
