Shapes, Images and Positions
=================================
.. manim:: ShowScreenResolution
    :save_last_frame:

    class ShowScreenResolution(Scene):
        def construct(self):
            pixel_height = config["pixel_height"]  #  1080 is default
            pixel_width = config["pixel_width"]  # 1920 is default
            frame_width = config["frame_width"]
            frame_height = config["frame_height"]
            self.add(Dot())
            d1 = Line(frame_width * LEFT / 2, frame_width * RIGHT / 2).to_edge(DOWN)
            self.add(d1)
            self.add(Tex(str(pixel_width)).next_to(d1, UP))
            d2 = Line(frame_height * UP / 2, frame_height * DOWN / 2).to_edge(LEFT)
            self.add(d2)
            self.add(Tex(str(pixel_height)).next_to(d2, RIGHT))


.. manim:: GeometricShapes
    :save_last_frame:

    class GeometricShapes(Scene):
        def construct(self):
            d = Dot()
            c = Circle()
            s = Square()
            t = Triangle()
            d.next_to(c, RIGHT)
            s.next_to(c, LEFT)
            t.next_to(c, DOWN)
            self.add(d, c, s, t)

.. manim:: PointMovingOnShapes

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


.. manim:: GradientImageFromArray
    :save_last_frame:

    class GradientImageFromArray(Scene):
        def construct(self):
            n = 256
            imageArray = np.uint8(
                [[i * 256 / n for i in range(0, n)] for _ in range(0, n)]
            )
            image = ImageMobject(imageArray).scale(2)
            self.add(image)


.. manim:: ArcShapeIris
    :save_last_frame:

    class ArcShapeIris(Scene):
        def construct(self):
            colors = [DARK_BLUE, DARK_BROWN, BLUE_E, BLUE_D, BLUE_A, TEAL_B, GREEN_B, YELLOW_E]
            radius = [1 + rad * 0.1 for rad in range(len(colors))]

            circles_group = VGroup()

            # zip(radius, color) makes the iterator [(radius[i], color[i]) for i in range(radius)]
            circles_group.add(*[Circle(radius=rad, stroke_width=10, color=col)
                                for rad, col in zip(radius, colors)])
            self.add(circles_group)


.. manim:: DotInterpolation
    :save_last_frame:

    class DotInterpolation(Scene):
        def construct(self):
            dotL = Dot(color=DARK_GREY)
            dotL.shift(2 * RIGHT)
            dotR = Dot(color=WHITE)
            dotR.shift(2 * LEFT)

            dotMiddle = VMobject().interpolate(dotL, dotR, alpha=0.3)

            self.add(dotL, dotR, dotMiddle)


.. manim:: MovingAround

    class MovingAround(Scene):
        def construct(self):
            square = Square(color=BLUE, fill_opacity=1)

            self.play(square.shift, LEFT)
            self.play(square.set_fill, ORANGE)
            self.play(square.scale, 0.3)
            self.play(square.rotate, 0.4)


.. manim:: TextAlignement
    :save_last_frame:

    class TextAlignement(Scene):
        def construct(self):
            title = Text("K-means clustering and Logistic Regression", color=WHITE)
            title.scale_in_place(0.75)
            self.add(title.to_edge(UP))

            t1 = Text("1. Measuring").set_color(WHITE)
            t1.next_to(ORIGIN, direction=RIGHT, aligned_edge=UP)

            t2 = Text("2. Clustering").set_color(WHITE)
            t2.next_to(t1, direction=DOWN, aligned_edge=LEFT)

            t3 = Text("3. Regression").set_color(WHITE)
            t3.next_to(t2, direction=DOWN, aligned_edge=LEFT)

            t4 = Text("4. Prediction").set_color(WHITE)
            t4.next_to(t3, direction=DOWN, aligned_edge=LEFT)

            x = VGroup(t1, t2, t3, t4).scale_in_place(0.7)
            x.set_opacity(0.5)
            x.submobjects[1].set_opacity(1)
            self.add(x)


.. manim:: BezierSpline
    :save_last_frame:

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

