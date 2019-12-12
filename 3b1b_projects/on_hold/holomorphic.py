from manimlib.imports import *


class ComplexAnalysisOverlay(Scene):
    def construct(self):
        words = TextMobject("Complex analysis")
        words.scale(1.25)
        words.to_edge(UP)
        words.add_background_rectangle()
        self.add(words)
        self.wait()


class AnalyzeZSquared(ComplexTransformationScene, ZoomedScene):
    CONFIG = {
        "plane_config": {
            "line_frequency": 0.1,
        },
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
        self.backgrounds.set_stroke(GREY, 2)
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
            x_line_frequency=0.1,
            y_line_frequency=0.1,
        )
        self.prepare_for_transformation(top_plane)
        bottom_plane = top_plane.copy()
        tiny_tiny_buff = 0.001
        top_plane.next_to(ORIGIN, UP, buff=tiny_tiny_buff)
        bottom_plane.next_to(ORIGIN, DOWN, buff=tiny_tiny_buff)
        return VGroup(top_plane, bottom_plane)
