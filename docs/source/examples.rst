###############
Example Gallery
###############

This gallery contains a collection of best practice code snippets
together with their corresponding video/image output, illustrating
different functionalities all across the library.
These are all under the MIT licence, so feel free to copy & paste them to your projects.
Enjoy this taste of Manim!

.. tip::

   This gallery is not the only place in our documentation where you can see explicit
   code and video examples: there are many more in our
   :doc:`reference manual </reference>` -- see, for example, our documentation for
   the modules :mod:`~.tex_mobject`, :mod:`~.geometry`, :mod:`~.moving_camera_scene`,
   and many more.

   Also, visit our `Twitter <https://twitter.com/manim_community/>`_ for more
   *manimations*!


.. contents:: Overview of thematic video categories
   :backlinks: none
   :local:


Basic Concepts
==============

.. manim:: ManimCELogo
    :save_last_frame:
    :ref_classes: MathTex Circle Square Triangle

    class ManimCELogo(Scene):
        def construct(self):
            self.camera.background_color = "#ece6e2"
            logo_green = "#87c2a5"
            logo_blue = "#525893"
            logo_red = "#e07a5f"
            logo_black = "#343434"
            ds_m = MathTex(r"\mathbb{M}", fill_color=logo_black).scale(7)
            ds_m.shift(2.25 * LEFT + 1.5 * UP)
            circle = Circle(color=logo_green, fill_opacity=1).shift(LEFT)
            square = Square(color=logo_blue, fill_opacity=1).shift(UP)
            triangle = Triangle(color=logo_red, fill_opacity=1).shift(RIGHT)
            logo = VGroup(triangle, square, circle, ds_m)  # order matters
            logo.move_to(ORIGIN)
            self.add(logo)


.. manim:: GradientImageFromArray
    :save_last_frame:
    :ref_classes: ImageMobject

    class GradientImageFromArray(Scene):
        def construct(self):
            n = 256
            imageArray = np.uint8(
                [[i * 256 / n for i in range(0, n)] for _ in range(0, n)]
            )
            image = ImageMobject(imageArray).scale(2)
            self.add(image)

.. manim:: BraceAnnotation
    :save_last_frame:
    :ref_classes: Brace
    :ref_functions: Brace.get_text Brace.get_tex

    class BraceAnnotation(Scene):
        def construct(self):
            dot = Dot([-2, -1, 0])
            dot2 = Dot([2, 1, 0])
            line = Line(dot.get_center(), dot2.get_center()).set_color(ORANGE)
            b1 = Brace(line)
            b1text = b1.get_text("Horizontal distance")
            b2 = Brace(line, direction=line.copy().rotate(PI / 2).get_unit_vector())
            b2text = b2.get_tex("x-x_1")
            self.add(line, dot, dot2, b1, b2, b1text, b2text)

.. manim:: VectorArrow
    :save_last_frame:
    :ref_classes: Dot Arrow NumberPlane Text

    class VectorArrow(Scene):
        def construct(self):
            dot = Dot(ORIGIN)
            arrow = Arrow(ORIGIN, [2, 2, 0], buff=0)
            numberplane = NumberPlane()
            origin_text = Text('(0, 0)').next_to(dot, DOWN)
            tip_text = Text('(2, 2)').next_to(arrow.get_end(), RIGHT)
            self.add(numberplane, dot, arrow, origin_text, tip_text)

.. manim:: BezierSpline
    :save_last_frame:
    :ref_classes: Line VGroup
    :ref_functions: VMobject.add_cubic_bezier_curve

    class BezierSpline(Scene):
        def construct(self):
            np.random.seed(42)
            area = 4

            x1 = np.random.randint(-area, area)
            y1 = np.random.randint(-area, area)
            p1 = np.array([x1, y1, 0])
            destination_dot1 = Dot(point=p1).set_color(BLUE)

            x2 = np.random.randint(-area, area)
            y2 = np.random.randint(-area, area)
            p2 = np.array([x2, y2, 0])
            destination_dot2 = Dot(p2).set_color(RED)

            deltaP = p1 - p2
            deltaPNormalized = deltaP / get_norm(deltaP)

            theta = np.radians(90)
            r = np.array(
                (
                    (np.cos(theta), -np.sin(theta), 0),
                    (np.sin(theta), np.cos(theta), 0),
                    (0, 0, 0),
                )
            )
            senk = r.dot(deltaPNormalized)
            offset = 0.1
            offset_along = 0.5
            offset_connect = 0.25

            dest_line1_point1 = p1 + senk * offset - deltaPNormalized * offset_along
            dest_line1_point2 = p2 + senk * offset + deltaPNormalized * offset_along
            dest_line2_point1 = p1 - senk * offset - deltaPNormalized * offset_along
            dest_line2_point2 = p2 - senk * offset + deltaPNormalized * offset_along
            s1 = p1 - offset_connect * deltaPNormalized
            s2 = p2 + offset_connect * deltaPNormalized
            dest_line1 = Line(dest_line1_point1, dest_line1_point2)
            dest_line2 = Line(dest_line2_point1, dest_line2_point2)

            Lp1s1 = Line(p1, s1)

            Lp1s1.add_cubic_bezier_curve(
                s1,
                s1 - deltaPNormalized * 0.1,
                dest_line2_point1 + deltaPNormalized * 0.1,
                dest_line2_point1 - deltaPNormalized * 0.01,
            )
            Lp1s1.add_cubic_bezier_curve(
                s1,
                s1 - deltaPNormalized * 0.1,
                dest_line1_point1 + deltaPNormalized * 0.1,
                dest_line1_point1,
            )

            Lp2s2 = Line(p2, s2)

            Lp2s2.add_cubic_bezier_curve(
                s2,
                s2 + deltaPNormalized * 0.1,
                dest_line2_point2 - deltaPNormalized * 0.1,
                dest_line2_point2,
            )
            Lp2s2.add_cubic_bezier_curve(
                s2,
                s2 + deltaPNormalized * 0.1,
                dest_line1_point2 - deltaPNormalized * 0.1,
                dest_line1_point2,
            )

            mobjects = VGroup(
                Lp1s1, Lp2s2, dest_line1, dest_line2, destination_dot1, destination_dot2
            )

            mobjects.scale(2)
            self.add(mobjects)


Animations
==========

.. manim:: PointMovingOnShapes
    :ref_classes: Circle Dot Line GrowFromCenter Transform MoveAlongPath Rotating

    class PointMovingOnShapes(Scene):
        def construct(self):
            circle = Circle(radius=1, color=BLUE)
            dot = Dot()
            dot2 = dot.copy().shift(RIGHT)
            self.add(dot)

            line = Line([3, 0, 0], [5, 0, 0])
            self.add(line)

            self.play(GrowFromCenter(circle))
            self.play(Transform(dot, dot2))
            self.play(MoveAlongPath(dot, circle), run_time=2, rate_func=linear)
            self.play(Rotating(dot, about_point=[2, 0, 0]), run_time=1.5)
            self.wait()

.. manim:: MovingAround
    :ref_functions: Mobject.shift VMobject.set_fill Mobject.scale Mobject.rotate

    class MovingAround(Scene):
        def construct(self):
            square = Square(color=BLUE, fill_opacity=1)

            self.play(square.shift, LEFT)
            self.play(square.set_fill, ORANGE)
            self.play(square.scale, 0.3)
            self.play(square.rotate, 0.4)

.. manim:: MovingFrameBox
    :ref_modules: manim.mobject.svg.tex_mobject
    :ref_classes: MathTex SurroundingRectangle

    class MovingFrameBox(Scene):
        def construct(self):
            text=MathTex(
                "\\frac{d}{dx}f(x)g(x)=","f(x)\\frac{d}{dx}g(x)","+",
                "g(x)\\frac{d}{dx}f(x)"
            )
            self.play(Write(text))
            framebox1 = SurroundingRectangle(text[1], buff = .1)
            framebox2 = SurroundingRectangle(text[3], buff = .1)
            self.play(
                ShowCreation(framebox1),
            )
            self.wait()
            self.play(
                ReplacementTransform(framebox1,framebox2),
            )
            self.wait()

.. manim:: RotationUpdater
    :ref_functions: Mobject.add_updater Mobject.remove_updater

    class RotationUpdater(Scene):
        def construct(self):
            def updater_forth(mobj, dt):
                mobj.rotate_about_origin(dt)
            def updater_back(mobj, dt):
                mobj.rotate_about_origin(-dt)
            line_reference = Line(ORIGIN, LEFT).set_color(WHITE)
            line_moving = Line(ORIGIN, LEFT).set_color(YELLOW)
            line_moving.add_updater(updater_forth)
            self.add(line_reference, line_moving)
            self.wait(2)
            line_moving.remove_updater(updater_forth)
            line_moving.add_updater(updater_back)
            self.wait(2)
            line_moving.remove_updater(updater_back)
            self.wait(0.5)

.. manim:: PointWithTrace
    :ref_classes: Rotating
    :ref_functions: VMobject.set_points_as_corners Mobject.add_updater

    class PointWithTrace(Scene):
        def construct(self):
            path = VMobject()
            dot = Dot()
            path.set_points_as_corners([dot.get_center(), dot.get_center()])
            def update_path(path):
                previous_path = path.copy()
                previous_path.add_points_as_corners([dot.get_center()])
                path.become(previous_path)
            path.add_updater(update_path)
            self.add(path, dot)
            self.play(Rotating(dot, radians=PI, about_point=RIGHT, run_time=2))
            self.wait()
            self.play(dot.shift, UP)
            self.play(dot.shift, LEFT)
            self.wait()


Plotting with Manim
===================

.. manim:: SinAndCosFunctionPlot
    :save_last_frame:
    :ref_modules: manim.scene.graph_scene
    :ref_classes: MathTex
    :ref_functions: GraphScene.setup_axes GraphScene.get_graph GraphScene.get_vertical_line_to_graph GraphScene.input_to_graph_point

    class SinAndCosFunctionPlot(GraphScene):
        CONFIG = {
            "x_min": -10,
            "x_max": 10.3,
            "num_graph_anchor_points": 100,
            "y_min": -1.5,
            "y_max": 1.5,
            "graph_origin": ORIGIN,
            "function_color": RED,
            "axes_color": GREEN,
            "x_labeled_nums": range(-10, 12, 2),
        }

        def construct(self):
            self.setup_axes(animate=False)
            func_graph = self.get_graph(np.cos, self.function_color)
            func_graph2 = self.get_graph(np.sin)
            vert_line = self.get_vertical_line_to_graph(TAU, func_graph, color=YELLOW)
            graph_lab = self.get_graph_label(func_graph, label="\\cos(x)")
            graph_lab2 = self.get_graph_label(func_graph2, label="\\sin(x)",
                                x_val=-10, direction=UP / 2)
            two_pi = MathTex(r"x = 2 \pi")
            label_coord = self.input_to_graph_point(TAU, func_graph)
            two_pi.next_to(label_coord, RIGHT + UP)
            self.add(func_graph, func_graph2, vert_line, graph_lab, graph_lab2, two_pi)

.. manim:: GraphAreaPlot
    :save_last_frame:
    :ref_modules: manim.scenes.graph_scene
    :ref_functions: GraphScene.setup_axes GraphScene.get_graph GraphScene.get_vertical_line_to_graph GraphScene.get_area

    class GraphAreaPlot(GraphScene):
        CONFIG = {
            "x_min" : 0,
            "x_max" : 5,
            "y_min" : 0,
            "y_max" : 6,
            "y_tick_frequency" : 1,
            "x_tick_frequency" : 1,
            "x_labeled_nums" : [0,2,3]
        }
        def construct(self):
            self.setup_axes()
            curve1 = self.get_graph(lambda x: 4 * x - x ** 2, x_min=0, x_max=4)
            curve2 = self.get_graph(lambda x: 0.8 * x ** 2 - 3 * x + 4, x_min=0, x_max=4)
            line1 = self.get_vertical_line_to_graph(2, curve1, DashedLine, color=YELLOW)
            line2 = self.get_vertical_line_to_graph(3, curve1, DashedLine, color=YELLOW)
            area1 = self.get_area(curve1, 0.3, 0.6, dx_scaling=10, area_color=BLUE)
            area2 = self.get_area(curve2, 2, 3, bounded=curve1)
            self.add(curve1, curve2, line1, line2, area1, area2)

.. manim:: HeatDiagramPlot
    :save_last_frame:
    :ref_modules: manim.scenes.graph_scene
    :ref_functions: GraphScene.setup_axes GraphScene.coords_to_point

    class HeatDiagramPlot(GraphScene):
        CONFIG = {
            "y_axis_label": r"T[$^\circ C$]",
            "x_axis_label": r"$\Delta Q$",
            "y_min": -8,
            "y_max": 30,
            "x_min": 0,
            "x_max": 40,
            "y_labeled_nums": np.arange(-5, 34, 5),
            "x_labeled_nums": np.arange(0, 40, 5),
        }

        def construct(self):
            data = [20, 0, 0, -5]
            x = [0, 8, 38, 39]
            self.setup_axes()
            dot_collection = VGroup()
            for time, val in enumerate(data):
                dot = Dot().move_to(self.coords_to_point(x[time], val))
                self.add(dot)
                dot_collection.add(dot)
            l1 = Line(dot_collection[0].get_center(), dot_collection[1].get_center())
            l2 = Line(dot_collection[1].get_center(), dot_collection[2].get_center())
            l3 = Line(dot_collection[2].get_center(), dot_collection[3].get_center())
            self.add(l1, l2, l3)


Special Camera Settings
=======================

.. manim:: FollowingGraphCamera
    :ref_modules: manim.scene.moving_camera_scene
    :ref_classes: GraphScene MovingCameraScene MoveAlongPath Restore
    :ref_functions: Mobject.add_updater

    class FollowingGraphCamera(GraphScene, MovingCameraScene):
        def setup(self):
            GraphScene.setup(self)
            MovingCameraScene.setup(self)
        def construct(self):
            self.camera_frame.save_state()
            self.setup_axes(animate=False)
            graph = self.get_graph(lambda x: np.sin(x),
                                   color=BLUE,
                                   x_min=0,
                                   x_max=3 * PI
                                   )
            moving_dot = Dot().move_to(graph.points[0]).set_color(ORANGE)

            dot_at_start_graph = Dot().move_to(graph.points[0])
            dot_at_end_grap = Dot().move_to(graph.points[-1])
            self.add(graph, dot_at_end_grap, dot_at_start_graph, moving_dot)
            self.play( self.camera_frame.scale,0.5,self.camera_frame.move_to,moving_dot)

            def update_curve(mob):
                mob.move_to(moving_dot.get_center())

            self.camera_frame.add_updater(update_curve)
            self.play(MoveAlongPath(moving_dot, graph, rate_func=linear))
            self.camera_frame.remove_updater(update_curve)

            self.play(Restore(self.camera_frame))

.. manim:: MovingZoomedSceneAround
    :ref_modules: manim.scene.zoomed_scene
    :ref_classes: ZoomedScene BackgroundRectangle UpdateFromFunc
    :ref_functions: Mobject.add_updater ZoomedScene.get_zoomed_display_pop_out_animation

    class MovingZoomedSceneAround(ZoomedScene):
    # contributed by TheoremofBeethoven, www.youtube.com/c/TheoremofBeethoven
        CONFIG = {
            "zoom_factor": 0.3,
            "zoomed_display_height": 1,
            "zoomed_display_width": 6,
            "image_frame_stroke_width": 20,
            "zoomed_camera_config": {
                "default_frame_stroke_width": 3,
            },
        }

        def construct(self):
            dot = Dot().shift(UL * 2)
            image = ImageMobject(np.uint8([[0, 100, 30, 200],
                                           [255, 0, 5, 33]]))
            image.set_height(7)
            frame_text = Text("Frame", color=PURPLE).scale(1.4)
            zoomed_camera_text = Text("Zoomed camera", color=RED).scale(1.4)

            self.add(image, dot)
            zoomed_camera = self.zoomed_camera
            zoomed_display = self.zoomed_display
            frame = zoomed_camera.frame
            zoomed_display_frame = zoomed_display.display_frame

            frame.move_to(dot)
            frame.set_color(PURPLE)
            zoomed_display_frame.set_color(RED)
            zoomed_display.shift(DOWN)

            zd_rect = BackgroundRectangle(zoomed_display, fill_opacity=0, buff=MED_SMALL_BUFF)
            self.add_foreground_mobject(zd_rect)

            unfold_camera = UpdateFromFunc(zd_rect, lambda rect: rect.replace(zoomed_display))

            frame_text.next_to(frame, DOWN)

            self.play(ShowCreation(frame), FadeInFrom(frame_text, direction=DOWN))
            self.activate_zooming()

            self.play(self.get_zoomed_display_pop_out_animation(), unfold_camera)
            zoomed_camera_text.next_to(zoomed_display_frame, DOWN)
            self.play(FadeInFrom(zoomed_camera_text, direction=DOWN))
            # Scale in        x   y  z
            scale_factor = [0.5, 1.5, 0]
            self.play(
                frame.scale, scale_factor,
                zoomed_display.scale, scale_factor,
                FadeOut(zoomed_camera_text),
                FadeOut(frame_text)
            )
            self.wait()
            self.play(ScaleInPlace(zoomed_display, 2))
            self.wait()
            self.play(frame.shift, 2.5 * DOWN)
            self.wait()
            self.play(self.get_zoomed_display_pop_out_animation(), unfold_camera, rate_func=lambda t: smooth(1 - t))
            self.play(Uncreate(zoomed_display_frame), FadeOut(frame))
            self.wait()

.. manim:: FixedInFrameMObjectTest
    :save_last_frame:
    :ref_classes: ThreeDScene
    :ref_functions: ThreeDScene.set_camera_orientation ThreeDScene.add_fixed_in_frame_mobjects

    class FixedInFrameMObjectTest(ThreeDScene):
        def construct(self):
            axes = ThreeDAxes()
            self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)
            text3d = Text("This is a 3D text")
            self.add_fixed_in_frame_mobjects(text3d)
            text3d.to_corner(UL)
            self.add(axes)
            self.wait()

.. manim:: ThreeDLightSourcePosition
    :save_last_frame:
    :ref_classes: ThreeDScene ThreeDAxes ParametricSurface
    :ref_functions: ThreeDScene.set_camera_orientation

    class ThreeDLightSourcePosition(ThreeDScene):
        def construct(self):
            axes = ThreeDAxes()
            sphere = ParametricSurface(
                lambda u, v: np.array([
                    1.5 * np.cos(u) * np.cos(v),
                    1.5 * np.cos(u) * np.sin(v),
                    1.5 * np.sin(u)
                ]), v_min=0, v_max=TAU, u_min=-PI / 2, u_max=PI / 2,
                checkerboard_colors=[RED_D, RED_E], resolution=(15, 32)
            )
            self.renderer.camera.light_source.move_to(3*IN) # changes the source of the light
            self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
            self.add(axes, sphere)

.. manim:: ThreeDCameraRotation
    :ref_classes: ThreeDScene ThreeDAxes
    :ref_functions: ThreeDScene.begin_ambient_camera_rotation ThreeDScene.stop_ambient_camera_rotation

    class ThreeDCameraRotation(ThreeDScene):
        def construct(self):
            axes = ThreeDAxes()
            circle=Circle()
            self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
            self.add(circle,axes)
            self.begin_ambient_camera_rotation(rate=0.1)
            self.wait(3)
            self.stop_ambient_camera_rotation()
            self.move_camera(phi=75 * DEGREES, theta=30 * DEGREES)
            self.wait()

.. manim:: ThreeDCameraIllusionRotation
    :ref_classes: ThreeDScene ThreeDAxes
    :ref_functions: ThreeDScene.begin_3dillusion_camera_rotation ThreeDScene.stop_3dillusion_camera_rotation

    class ThreeDCameraIllusionRotation(ThreeDScene):
        def construct(self):
            axes = ThreeDAxes()
            circle=Circle()
            self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
            self.add(circle,axes)
            self.begin_3dillusion_camera_rotation(rate=2)
            self.wait(PI)
            self.stop_3dillusion_camera_rotation()

.. manim:: ThreeDFunctionPlot
    :ref_classes: ThreeDScene ParametricSurface

    class ThreeDFunctionPlot(ThreeDScene):
        def construct(self):
            resolution_fa = 22
            self.set_camera_orientation(phi=75 * DEGREES, theta=-30 * DEGREES)

            def param_plane(u, v):
                x = u
                y = v
                z = 0
                return np.array([x, y, z])

            plane = ParametricSurface(
                param_plane,
                resolution=(resolution_fa, resolution_fa),
                v_min=-2,
                v_max=+2,
                u_min=-2,
                u_max=+2,
            )
            plane.scale_about_point(2, ORIGIN)

            def param_gauss(u, v):
                x = u
                y = v
                d = np.sqrt(x * x + y * y)
                sigma, mu = 0.4, 0.0
                z = np.exp(-((d - mu) ** 2 / (2.0 * sigma ** 2)))
                return np.array([x, y, z])

            gauss_plane = ParametricSurface(
                param_gauss,
                resolution=(resolution_fa, resolution_fa),
                v_min=-2,
                v_max=+2,
                u_min=-2,
                u_max=+2,
            )

            gauss_plane.scale_about_point(2, ORIGIN)
            gauss_plane.set_style(fill_opacity=1)
            gauss_plane.set_style(stroke_color=GREEN)
            gauss_plane.set_fill_by_checkerboard(GREEN, BLUE, opacity=0.1)

            axes = ThreeDAxes()

            self.add(axes)
            self.play(Write(plane))
            self.play(Transform(plane, gauss_plane))
            self.wait()


Advanced Projects
=================

.. manim:: OpeningManim
    :ref_classes: Tex MathTex Write FadeInFrom LaggedStart NumberPlane ShowCreation
    :ref_functions: NumberPlane.prepare_for_nonlinear_transform

    class OpeningManim(Scene):
        def construct(self):
            title = Tex("This is some \\LaTeX")
            basel = MathTex("\\sum_{n=1}^\\infty " "\\frac{1}{n^2} = \\frac{\\pi^2}{6}")
            VGroup(title, basel).arrange(DOWN)
            self.play(
                Write(title),
                FadeInFrom(basel, UP),
            )
            self.wait()

            transform_title = Tex("That was a transform")
            transform_title.to_corner(UP + LEFT)
            self.play(
                Transform(title, transform_title),
                LaggedStart(*map(lambda obj: FadeOutAndShift(obj, direction=DOWN), basel)),
            )
            self.wait()

            grid = NumberPlane()
            grid_title = Tex("This is a grid")
            grid_title.scale(1.5)
            grid_title.move_to(transform_title)

            self.add(grid, grid_title)  # Make sure title is on top of grid
            self.play(
                FadeOut(title),
                FadeInFrom(grid_title, direction=DOWN),
                ShowCreation(grid, run_time=3, lag_ratio=0.1),
            )
            self.wait()

            grid_transform_title = Tex(
                "That was a non-linear function \\\\" "applied to the grid"
            )
            grid_transform_title.move_to(grid_title, UL)
            grid.prepare_for_nonlinear_transform()
            self.play(
                grid.apply_function,
                lambda p: p
                          + np.array(
                    [
                        np.sin(p[1]),
                        np.sin(p[0]),
                        0,
                    ]
                ),
                run_time=3,
            )
            self.wait()
            self.play(Transform(grid_title, grid_transform_title))
            self.wait()

.. manim:: SineCurveUnitCircle
    :ref_classes: MathTex Circle Dot Line VGroup
    :ref_functions: Mobject.add_updater Mobject.remove_updater always_redraw

    class SineCurveUnitCircle(Scene):
        # contributed by heejin_park, https://infograph.tistory.com/230
        def construct(self):
            self.show_axis()
            self.show_circle()
            self.move_dot_and_draw_curve()
            self.wait()

        def show_axis(self):
            x_start = np.array([-6,0,0])
            x_end = np.array([6,0,0])

            y_start = np.array([-4,-2,0])
            y_end = np.array([-4,2,0])

            x_axis = Line(x_start, x_end)
            y_axis = Line(y_start, y_end)

            self.add(x_axis, y_axis)
            self.add_x_labels()

            self.orgin_point = np.array([-4,0,0])
            self.curve_start = np.array([-3,0,0])

        def add_x_labels(self):
            x_labels = [
                MathTex("\pi"), MathTex("2 \pi"),
                MathTex("3 \pi"), MathTex("4 \pi"),
            ]

            for i in range(len(x_labels)):
                x_labels[i].next_to(np.array([-1 + 2*i, 0, 0]), DOWN)
                self.add(x_labels[i])

        def show_circle(self):
            circle = Circle(radius=1)
            circle.move_to(self.orgin_point)

            self.add(circle)
            self.circle = circle

        def move_dot_and_draw_curve(self):
            orbit = self.circle
            orgin_point = self.orgin_point

            dot = Dot(radius=0.08, color=YELLOW)
            dot.move_to(orbit.point_from_proportion(0))
            self.t_offset = 0
            rate = 0.25

            def go_around_circle(mob, dt):
                self.t_offset += (dt * rate)
                # print(self.t_offset)
                mob.move_to(orbit.point_from_proportion(self.t_offset % 1))

            def get_line_to_circle():
                return Line(orgin_point, dot.get_center(), color=BLUE)

            def get_line_to_curve():
                x = self.curve_start[0] + self.t_offset * 4
                y = dot.get_center()[1]
                return Line(dot.get_center(), np.array([x,y,0]), color=YELLOW_A, stroke_width=2 )


            self.curve = VGroup()
            self.curve.add(Line(self.curve_start,self.curve_start))
            def get_curve():
                last_line = self.curve[-1]
                x = self.curve_start[0] + self.t_offset * 4
                y = dot.get_center()[1]
                new_line = Line(last_line.get_end(),np.array([x,y,0]), color=YELLOW_D)
                self.curve.add(new_line)

                return self.curve

            dot.add_updater(go_around_circle)

            origin_to_circle_line = always_redraw(get_line_to_circle)
            dot_to_curve_line = always_redraw(get_line_to_curve)
            sine_curve_line = always_redraw(get_curve)

            self.add(dot)
            self.add(orbit, origin_to_circle_line, dot_to_curve_line, sine_curve_line)
            self.wait(8.5)

            dot.remove_updater(go_around_circle)
