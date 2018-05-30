from big_ol_pile_of_manim_imports import *


# Helper functions
def get_flow_start_points(x_min=-8, x_max=8,
                          y_min=-5, y_max=5,
                          delta_x=0.5, delta_y=0.5,
                          n_repeats=1,
                          noise_factor=0.01
                          ):
    return np.array([
        x * RIGHT + y * UP + noise_factor * np.random.random(3)
        for n in xrange(n_repeats)
        for x in np.arange(x_min, x_max + delta_x, delta_x)
        for y in np.arange(y_min, y_max + delta_y, delta_y)
    ])


def joukowsky_map(z):
    return z + fdiv(1, z)


def inverse_joukowsky_map(w):
    u = 1 if w.real <= 0 else -1
    return (w + u * np.sqrt(w**2 - 4)) / 2


def derivative(func, dt=1e-7):
    return lambda z: (func(z + dt) - func(z)) / dt


def cylinder_flow_vector_field(point, R=1, U=1):
    z = R3_to_complex(point)
    return complex_to_R3(1.0 / derivative(joukowsky_map)(z))


# Continual animations

class VectorFieldFlow(ContinualAnimation):
    CONFIG = {
        "mode": None,
    }

    def __init__(self, mobject, func, **kwargs):
        """
        Func should take in a vector in R3, and output a vector in R3
        """
        self.func = func
        ContinualAnimation.__init__(self, mobject, **kwargs)

    def update_mobject(self, dt):
        self.apply_nudge(dt)

    def apply_nudge(self):
        self.mobject.shift(self.func(self.mobject.get_center()) * dt)


class VectorFieldSubmobjectFlow(VectorFieldFlow):
    def apply_nudge(self, dt):
        for submob in self.mobject:
            submob.shift(self.func(submob.get_center()) * dt)


class VectorFieldPointFlow(VectorFieldFlow):
    def apply_nudge(self, dt):
        self.mobject.apply_function(
            lambda p: p + self.func(p) * dt
        )


class StreamLines(VGroup):
    CONFIG = {
        "start_points_generator": get_flow_start_points,
        "dt": 0.05,
        "virtual_time": 20,
        "n_anchors_per_line": 30,
        "stroke_width": 1,
        "stroke_color": WHITE,
    }

    def __init__(self, func, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.func = func
        dt = self.dt

        start_points = self.start_points_generator()
        for point in start_points:
            points = [point]
            for t in np.arange(0, self.virtual_time, dt):
                last_point = points[-1]
                points.append(last_point + dt * func(last_point))
            line = VMobject()
            line.set_points_smoothly(
                points[::(len(points) / self.n_anchors_per_line)]
            )
            self.add(line)

        self.set_stroke(self.stroke_color, self.stroke_width)


class StreamLineAnimation(ContinualAnimation):
    CONFIG = {
        "lag_range": 4,
        "line_anim_class": ShowPassingFlash,
        "line_anim_config": {
            "run_time": 4,
            "rate_func": None,
            "time_width": 0.4,
        },
    }

    def __init__(self, stream_lines, **kwargs):
        digest_config(self, kwargs)
        self.stream_lines = stream_lines
        for line in stream_lines:
            line.anim = self.line_anim_class(line, **self.line_anim_config)
            line.time = -self.lag_range * random.random()
        ContinualAnimation.__init__(self, stream_lines, **kwargs)

    def update_mobject(self, dt):
        stream_lines = self.stream_lines
        for line in stream_lines:
            line.time += dt
            adjusted_time = max(line.time, 0) % line.anim.run_time
            line.anim.update(adjusted_time / line.anim.run_time)

# Scenes


class TestVectorField(Scene):
    CONFIG = {
        "func": cylinder_flow_vector_field,
    }

    def construct(self):
        plane = ComplexPlane()
        self.add(plane)

        circle = Circle(stroke_color=YELLOW)
        circle.set_fill(BLACK, 1)
        self.add_foreground_mobject(circle)

        lines = StreamLines(
            self.func,
            start_points_generator=lambda: get_flow_start_points(
                x_min=-8, x_max=-7, y_min=-2, y_max=2,
                delta_x=0.5, delta_y=0.2,
                n_repeats=4,
                noise_factor=0.2,
            ),
        )
        self.add(lines)
        return
        stream_line_animation = StreamLineAnimation(lines)
        self.add(stream_line_animation)
        self.wait(8)
        self.play(VFadeOut(lines))
        self.remove(stream_line_animation)
        self.wait()

        # dots = VGroup(*[
        #     Dot().move_to(start_point)
        #     for start_point in get_flow_start_points()
        # ])
        # dots.set_color_by_gradient(YELLOW, RED)
        # self.add(dots)

        # self.add(VectorFieldSubmobjectFlow(dots, self.func))
        # self.wait(5)


class ComplexAnalysisOverlay(Scene):
    def construct(self):
        words = TextMobject("Complex analysis")
        words.scale(1.25)
        words.to_edge(UP)
        words.add_background_rectangle()
        self.add(words)
        self.wait()


class CompelxAnalyticFluidFlow(ComplexTransformationScene, MovingCameraScene):
    CONFIG = {
        "num_anchors_to_add_per_line": 200,
        "plane_config": {"y_radius": 8}
    }

    def setup(self):
        MovingCameraScene.setup(self)
        ComplexTransformationScene.setup(self)

    def construct(self):
        self.camera.frame.shift(2 * UP)
        self.camera.frame.scale(0.5, about_point=ORIGIN)

        plane = NumberPlane(
            x_radius=15,
            y_radius=25,
            y_unit_size=0.5,
            secondary_line_ratio=0,
        )
        plane.next_to(ORIGIN, UP, buff=0.001)
        horizontal_lines = VGroup(*filter(
            lambda l: np.abs(l.get_center()[0]) < 0.1,
            list(plane.main_lines) + [plane.axes[0]]
        ))
        plane.set_stroke(MAROON_B, width=2)
        horizontal_lines.set_stroke(BLUE, width=2)
        for line in horizontal_lines:
            # To lag the paths of the droplets
            line.scale(1 + random.random())

        self.prepare_for_transformation(plane)
        self.add_transformable_mobjects(plane)

        self.background.set_stroke(width=2)
        for label in self.background.coordinate_labels:
            label.set_stroke(width=0)
            label.scale(0.75, about_edge=UR)

        words = TextMobject("Flow near \\\\", "a wall")
        words.scale(0.75)
        words.add_background_rectangle_to_submobjects()
        words.next_to(0.75 * UP, LEFT, MED_LARGE_BUFF)
        equation = TexMobject("z \\rightarrow z^{1/2}")
        equation.scale(0.75)
        equation.add_background_rectangle()
        equation.next_to(words, UP)

        self.apply_complex_function(
            lambda x: x**(1. / 2),
            added_anims=[Write(equation)]
        )
        self.play(Write(words, run_time=1))

        dots = VGroup()
        num_dots_per_line = 50
        for x in range(num_dots_per_line):
            for line in horizontal_lines:
                dot = Dot(radius=0.025)
                opacity = 1.0 - x / float(num_dots_per_line)
                dot.set_fill(opacity=opacity)
                dot.path = line
                dots.add(dot)
        dots.set_color_by_gradient(BLUE_B, BLUE_D)

        self.play(LaggedStart(
            MoveAlongPath, dots,
            lambda d: (d, d.path),
            run_time=3,
            lag_ratio=0.9
        ))


class AnalyzeZSquared(ComplexTransformationScene, ZoomedScene):
    CONFIG = {
        "num_anchors_to_add_per_line": 20,
        "complex_homotopy": lambda z, t: z**(1.0 + t),
        "zoom_factor": 0.05,
    }

    def setup(self):
        ComplexTransformationScene.setup(self)
        ZoomedScene.setup(self)

    def construct(self):
        self.edit_background_plane()
        self.add_title()
        # self.add_transforming_planes()
        # self.preview_some_numbers()
        self.zoom_in_to_one_plus_half_i()
        self.write_derivative()

    def add_title(self):
        title = TexMobject("z \\rightarrow z^2")
        title.add_background_rectangle()
        title.scale(1.5)
        title.to_corner(UL, buff=MED_SMALL_BUFF)
        self.add_foreground_mobject(title)

    def edit_background_plane(self):
        self.background.main_lines.set_stroke(GREY, 2)
        self.background.secondary_lines.set_stroke(DARK_GREY, 1)
        self.add_foreground_mobject(self.background.coordinate_labels)

    def add_transforming_planes(self):
        self.plane = self.get_plane()
        self.add_transformable_mobjects(self.plane)

    def preview_some_numbers(self):
        dots = VGroup(*[
            Dot().move_to(self.background.number_to_point(z))
            for z in [
                1, 2, complex(0, 1),
                -1, complex(2, 0.5), complex(-1, -1), complex(3, 0.5),
            ]
        ])
        dots.set_color_by_gradient(RED, YELLOW)
        d_angle = 30 * DEGREES

        dot_groups = VGroup()
        for dot in dots:
            point = dot.get_center()
            z = self.background.point_to_number(point)
            z_out = self.complex_homotopy(z, 1)
            out_point = self.background.number_to_point(z_out)
            path_arc = angle_of_vector(point)
            if abs(z - 1) < 0.01:
                # One is special
                arrow = Arc(
                    start_angle=(-90 * DEGREES + d_angle),
                    angle=(360 * DEGREES - 2 * d_angle),
                    radius=0.25
                )
                arrow.add_tip(tip_length=0.15)
                arrow.pointwise_become_partial(arrow, 0, 0.9)
                arrow.next_to(dot, UP, buff=0)
            else:
                arrow = Arrow(
                    point, out_point,
                    use_rectangular_stem=False,
                    path_arc=path_arc,
                    buff=SMALL_BUFF,
                )
            arrow.match_color(dot)

            out_dot = dot.copy()
            # out_dot.set_fill(opacity=0.5)
            out_dot.set_stroke(BLUE, 1)
            out_dot.move_to(out_point)
            dot.path_arc = path_arc
            dot.out_dot = out_dot

            dot_group = VGroup(dot, arrow, out_dot)
            dot_groups.add(dot_group)

            dot_copy = dot.copy()
            dot.save_state()
            dot.scale(3)
            dot.fade(1)

            dot_group.anim = Succession(
                ApplyMethod(dot.restore),
                AnimationGroup(
                    ShowCreation(arrow),
                    ReplacementTransform(
                        dot_copy, out_dot,
                        path_arc=path_arc
                    )
                )
            )

        for dot_group in dot_groups[:3]:
            self.play(dot_group.anim)
            self.wait()
        self.play(*[dg.anim for dg in dot_groups[3:]])

        self.apply_complex_homotopy(
            self.complex_homotopy,
            added_anims=[Animation(dot_groups)]
        )
        self.wait()
        self.play(FadeOut(dot_groups))
        self.wait()
        self.play(FadeOut(self.plane))
        self.transformable_mobjects.remove(self.plane)

    def zoom_in_to_one_plus_half_i(self):
        z = complex(1, 0.5)
        point = self.background.number_to_point(z)
        point_mob = VectorizedPoint(point)
        frame = self.zoomed_camera.frame
        frame.move_to(point)
        tiny_plane = NumberPlane(
            x_radius=2, y_radius=2,
            color=GREEN,
            secondary_color=GREEN_E
        )
        tiny_plane.replace(frame)

        plane = self.get_plane()

        words = TextMobject("What does this look like")
        words.add_background_rectangle()
        words.next_to(self.zoomed_display, LEFT, aligned_edge=UP)
        arrow = Arrow(words.get_bottom(), self.zoomed_display.get_left())
        VGroup(words, arrow).set_color(YELLOW)

        self.play(FadeIn(plane))
        self.activate_zooming(animate=True)
        self.play(ShowCreation(tiny_plane))
        self.wait()
        self.add_transformable_mobjects(plane, tiny_plane, point_mob)
        self.add_foreground_mobjects(words, arrow)
        self.apply_complex_homotopy(
            self.complex_homotopy,
            added_anims=[
                Write(words),
                GrowArrow(arrow),
                MaintainPositionRelativeTo(frame, point_mob)
            ]
        )
        self.wait(2)

    def write_derivative(self):
        pass

    # Helpers

    def get_plane(self):
        top_plane = NumberPlane(
            y_radius=FRAME_HEIGHT / 2,
        )
        self.prepare_for_transformation(top_plane)
        bottom_plane = top_plane.copy()
        tiny_tiny_buff = 0.001
        top_plane.next_to(ORIGIN, UP, buff=tiny_tiny_buff)
        bottom_plane.next_to(ORIGIN, DOWN, buff=tiny_tiny_buff)
        return VGroup(top_plane, bottom_plane)
