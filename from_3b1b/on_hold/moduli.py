from manimlib.imports import *


class TriangleModuliSpace(Scene):
    CONFIG = {
        "camera_config": {
            "background_image": "chalkboard",
        },
        "degen_color": GREEN_D,
        "x1_color": GREEN_B,
        "y1_color": RED,
        "x_eq_y_color": YELLOW,
        "right_color": TEAL,
        "obtuse_color": PINK,
        "acute_color": GREEN,
        "triangle_fill_opacity": 0.5,
        "random_seed": 0,
        "example_triangle_width": 6,
    }

    def setup(self):
        self.plane = NumberPlane(
            axis_config={
                "unit_size": 2,
            }
        )

    def construct(self):
        self.show_meaning_of_similar()
        self.show_xy_rule()

    def show_meaning_of_similar(self):
        # Setup titles
        title = TextMobject("Space", " of all ", "triangles")
        title.scale(1.5)
        title.to_edge(UP)

        subtitle = TextMobject("up to similarity.")
        subtitle.scale(1.5)
        subtitle.next_to(title, DOWN, MED_SMALL_BUFF)

        question = TextMobject("What ", "is ", "a\\\\", "moduli ", "space", "?")
        question.scale(2)

        # Setup all triangles
        all_triangles, tri_classes = self.get_triangles_and_classes()
        tri_classes[2][1].scale(0.5)
        tri_classes[2][1].scalar *= 0.5

        all_triangles.to_edge(DOWN)

        # Triangles pop up...
        self.play(
            LaggedStartMap(FadeInFromDown, question),
        )
        self.wait()

        self.play(
            ReplacementTransform(
                question.get_part_by_tex("space"),
                title.get_part_by_tex("Space"),
            ),
            FadeOut(question[:-2]),
            FadeOut(question[-1]),
            FadeIn(title[1:]),
            LaggedStartMap(
                DrawBorderThenFill, all_triangles,
                rate_func=bezier([0, 0, 1.5, 1, 1]),
                run_time=5,
                lag_ratio=0.05,
            )
        )
        self.wait()

        # ...Then divide into classes
        tri_classes.generate_target()
        colors = Color(BLUE).range_to(Color(RED), len(tri_classes))
        for group, color in zip(tri_classes.target, colors):
            group.arrange(DOWN)
            group.set_color(color)
        tri_classes.target.arrange(RIGHT, buff=1.25, aligned_edge=UP)
        tri_classes.target.scale(0.85)
        tri_classes.target.to_corner(DL)
        max_width = max([tc.get_width() for tc in tri_classes.target])
        height = tri_classes.target.get_height() + 0.5
        rects = VGroup(*[
            Rectangle(
                height=height,
                width=max_width + 0.25,
                stroke_width=2,
            ).move_to(tri_class, UP)
            for tri_class in tri_classes.target
        ])
        rects.shift(MED_SMALL_BUFF * UP)

        # Dumb shifts
        # tri_classes.target[1][2].shift(0.25 * UP)
        tri_classes.target[2].scale(0.9, about_edge=UP)
        tri_classes.target[2][2].shift(0.2 * UP)
        tri_classes.target[3][0].shift(0.5 * DOWN)
        tri_classes.target[3][1].shift(1.0 * DOWN)
        tri_classes.target[3][2].shift(1.2 * DOWN)
        tri_classes.target[4][1:].shift(0.7 * UP)

        # Dots
        per_class_dots = VGroup(*[
            TexMobject("\\vdots").move_to(
                tri_class
            ).set_y(rects.get_bottom()[1] + 0.4)
            for tri_class in tri_classes.target
        ])
        all_class_dots = TexMobject("\\dots").next_to(
            rects, RIGHT, MED_SMALL_BUFF,
        )

        self.play(
            FadeInFromDown(subtitle),
            MoveToTarget(tri_classes),
        )
        self.play(
            LaggedStartMap(FadeIn, rects),
            Write(per_class_dots),
            Write(all_class_dots),
        )
        self.wait(2)

        # Similar

        tri1 = tri_classes[2][1]
        tri2 = tri_classes[2][2]
        tri1.save_state()
        tri2.save_state()

        sim_sign = TexMobject("\\sim")
        sim_sign.set_width(1)
        sim_sign.move_to(midpoint(rects.get_top(), TOP))
        sim_sign.shift(0.25 * DOWN)

        similar_word = TextMobject("Similar")
        similar_word.scale(1.5)
        similar_word.move_to(sim_sign)
        similar_word.to_edge(UP)

        self.play(
            FadeOutAndShift(VGroup(title, subtitle), UP),
            tri1.next_to, sim_sign, LEFT, 0.75,
            tri2.next_to, sim_sign, RIGHT, 0.75,
        )
        self.play(
            FadeInFromDown(sim_sign),
            Write(similar_word, run_time=1)
        )
        self.wait()

        # Move into place
        tri1_copy = tri1.copy()
        self.play(
            tri1_copy.next_to, tri2,
            RIGHT, LARGE_BUFF,
            path_arc=90 * DEGREES,
        )
        self.play(Rotate(tri1_copy, tri2.angle - tri1.angle))
        self.play(tri1_copy.scale, tri2.scalar / tri1.scalar)
        self.play(
            tri1_copy.move_to, tri2,
        )
        tri1_copy.set_color(YELLOW)
        self.play(
            FadeOut(tri1_copy),
            rate_func=rush_from,
        )
        self.wait(2)

        # Show non-similar example
        not_similar_word = TextMobject("Not ", "Similar")
        not_similar_word.scale(1.5)
        not_similar_word.move_to(similar_word)
        not_similar_word.set_color(RED)

        sim_cross = Line(DL, UR)
        sim_cross.set_color(RED)
        sim_cross.match_width(sim_sign)
        sim_cross.move_to(sim_sign)
        sim_cross.set_stroke(BLACK, 5, background=True)

        tri3 = tri_classes[1][2]
        tri3.save_state()
        tri3.generate_target()
        tri3.target.move_to(tri2, LEFT)

        tri1_copy = tri1.copy()

        self.play(
            Restore(tri2),
            MoveToTarget(tri3),
        )
        self.play(
            ReplacementTransform(
                similar_word[0],
                not_similar_word[1],
            ),
            GrowFromCenter(not_similar_word[0]),
            ShowCreation(sim_cross),
        )
        self.play(tri1_copy.move_to, tri3)
        self.play(Rotate(tri1_copy, 90 * DEGREES))
        self.play(
            tri1_copy.match_height, tri3,
            tri1_copy.move_to, tri3, RIGHT,
        )
        self.play(WiggleOutThenIn(tri1_copy, n_wiggles=10))
        self.play(FadeOut(tri1_copy))

        self.wait()

        # Back to classes
        new_title = TextMobject("Space of all\\\\", "Similarity classes")
        new_title.scale(1.5)
        new_title[1].set_color(YELLOW)
        new_title.to_edge(UP)
        new_title_underline = Line(LEFT, RIGHT)
        new_title_underline.match_width(new_title[1])
        new_title_underline.match_color(new_title[1])
        new_title_underline.next_to(new_title, DOWN, buff=0.05)

        self.play(
            Restore(tri1),
            Restore(tri2),
            Restore(tri3),
            FadeOut(not_similar_word),
            FadeOut(sim_sign),
            FadeOut(sim_cross),
            FadeInFrom(new_title[1], UP),
        )
        self.play(
            ShowCreationThenDestruction(new_title_underline),
            LaggedStartMap(
                ApplyMethod, rects,
                lambda m: (m.set_stroke, YELLOW, 5),
                rate_func=there_and_back,
                run_time=1,
            )
        )
        self.wait()
        self.play(Write(new_title[0]))
        self.wait()

        # Show abstract space
        blob = ThoughtBubble()[-1]
        blob.set_height(2)
        blob.to_corner(UR)

        dots = VGroup(*[
            Dot(color=tri.get_color()).move_to(
                self.get_triangle_x(tri) * RIGHT +
                self.get_triangle_y(tri) * UP,
            )
            for tri_class in tri_classes
            for tri in tri_class[0]
        ])
        dots.space_out_submobjects(2)
        dots.move_to(blob)

        self.play(
            DrawBorderThenFill(blob),
            new_title.shift, LEFT,
        )

        self.play(LaggedStart(
            *[
                ReplacementTransform(
                    tri_class.copy().set_fill(opacity=0),
                    dot
                )
                for tri_class, dot in zip(tri_classes, dots)
            ],
            run_time=3,
            lag_ratio=0.3,
        ))

        # Isolate one triangle

        tri = tri_classes[0][0]
        verts = tri.get_vertices()
        angle = PI + angle_of_vector(verts[1] - verts[2])

        self.play(
            tri.rotate, -angle,
            tri.set_width, self.example_triangle_width,
            tri.center,
            FadeOut(tri_classes[0][1:]),
            FadeOut(tri_classes[1:]),
            FadeOut(rects),
            FadeOut(per_class_dots),
            FadeOut(all_class_dots),
            FadeOut(blob),
            FadeOut(dots),
            FadeOut(new_title),
        )

        self.triangle = tri

    def show_xy_rule(self):
        unit_factor = 4.0

        if hasattr(self, "triangle"):
            triangle = self.triangle
        else:
            triangle = self.get_triangles_and_classes()[0][0]
            verts = triangle.get_vertices()
            angle = PI + angle_of_vector(verts[1] - verts[2])
            triangle.rotate(-angle)
            triangle.set_width(self.example_triangle_width)
            triangle.center()
            self.add(triangle)

        side_trackers = VGroup(*[Line() for x in range(3)])
        side_trackers.set_stroke(width=0, opacity=0)
        side_trackers.triangle = triangle

        def update_side_trackers(st):
            verts = st.triangle.get_vertices()
            st[0].put_start_and_end_on(verts[0], verts[1])
            st[1].put_start_and_end_on(verts[1], verts[2])
            st[2].put_start_and_end_on(verts[2], verts[0])

        side_trackers.add_updater(update_side_trackers)

        def get_length_labels():
            result = VGroup()
            for line in side_trackers:
                vect = normalize(line.get_vector())
                perp_vect = rotate_vector(vect, -90 * DEGREES)
                perp_vect = np.round(perp_vect, 1)
                label = DecimalNumber(line.get_length() / unit_factor)
                label.move_to(line.get_center())
                label.next_to(line.get_center(), perp_vect, buff=0.15)
                result.add(label)
            return result

        side_labels = always_redraw(get_length_labels)

        b_label, c_label, a_label = side_labels
        b_side, c_side, a_side = side_trackers

        # Rescale
        self.add(side_trackers)
        self.play(LaggedStartMap(FadeIn, side_labels, lag_ratio=0.3, run_time=1))
        self.add(side_labels)
        self.wait()
        self.play(triangle.set_width, unit_factor)
        self.play(ShowCreationThenFadeAround(c_label))
        self.wait()

        # Label x and y
        x_label = TexMobject("x")
        y_label = TexMobject("y")
        xy_labels = VGroup(x_label, y_label)
        xy_labels.scale(1.5)

        x_color = self.x1_color
        y_color = self.y1_color

        x_label[0].set_color(x_color)
        y_label[0].set_color(y_color)

        # side_labels.clear_updaters()
        for var, num, vect in zip(xy_labels, [b_label, a_label], [DR, DL]):
            buff = 0.15
            var.move_to(num, vect)
            var.brace = Brace(num, UP)
            var.brace.num = num
            var.brace.add_updater(
                lambda m: m.next_to(m.num, UP, buff=buff)
            )
            var.add_updater(
                lambda m: m.next_to(m.brace, UP, buff=buff)
            )

            var.suspend_updating()
            var.brace.suspend_updating()
            self.play(
                FadeInFrom(var, DOWN),
                Write(var.brace, run_time=1),
                # MoveToTarget(num)
            )
            self.wait()

        # Show plane
        to_move = VGroup(
            triangle,
            side_labels,
            x_label,
            x_label.brace,
            y_label,
            y_label.brace,
        )

        axes = Axes(
            x_min=-0.25,
            x_max=1.5,
            y_min=-0.25,
            y_max=1.5,
            axis_config={
                "tick_frequency": 0.25,
                "unit_size": 3,
            }
        )
        x_axis = axes.x_axis
        y_axis = axes.y_axis

        x_axis.add(TexMobject("x", color=x_color).next_to(x_axis, RIGHT))
        y_axis.add(TexMobject("y", color=y_color).next_to(y_axis, UP))

        for axis, vect in [(x_axis, DOWN), (y_axis, LEFT)]:
            axis.add_numbers(
                0.5, 1.0,
                number_config={"num_decimal_places": 1},
                direction=vect,
            )

        axes.to_corner(DR, buff=LARGE_BUFF)

        self.play(
            to_move.to_corner, UL, {"buff": LARGE_BUFF},
            to_move.shift, MED_LARGE_BUFF * DOWN,
            Write(axes),
        )

        # Show coordinates
        coords = VGroup(b_label.copy(), a_label.copy())

        x_coord, y_coord = coords
        x_coord.add_updater(lambda m: m.set_value(b_side.get_length() / unit_factor))
        y_coord.add_updater(lambda m: m.set_value(a_side.get_length() / unit_factor))

        def get_coord_values():
            return [c.get_value() for c in coords]

        def get_ms_point():
            return axes.c2p(*get_coord_values())

        dot = always_redraw(
            lambda: triangle.copy().set_width(0.1).move_to(get_ms_point())
        )

        y_line = always_redraw(
            lambda: DashedLine(
                x_axis.n2p(x_coord.get_value()),
                get_ms_point(),
                color=y_color,
                stroke_width=1,
            )
        )
        x_line = always_redraw(
            lambda: DashedLine(
                y_axis.n2p(y_coord.get_value()),
                get_ms_point(),
                color=x_color,
                stroke_width=1,
            )
        )

        coord_label = TexMobject("(", "0.00", ",", "0.00", ")")
        cl_buff = 0
        coord_label.next_to(dot, UR, buff=cl_buff)
        for i, coord in zip([1, 3], coords):
            coord.generate_target()
            coord.target.replace(coord_label[i], dim_to_match=0)
            coord_label[i].set_opacity(0)

        self.play(
            MoveToTarget(x_coord),
            MoveToTarget(y_coord),
            FadeIn(coord_label),
            ReplacementTransform(triangle.copy().set_fill(opacity=0), dot),
        )
        coord_label.add(*coords)
        coord_label.add_updater(lambda m: m.next_to(dot, UR, buff=cl_buff))
        self.add(x_label, y_label, dot)
        self.play(
            ShowCreation(x_line),
            ShowCreation(y_line),
        )
        self.wait()

        # Adjust triangle
        tip_tracker = VectorizedPoint(triangle.points[0])

        def update_triangle(tri):
            point = tip_tracker.get_location()
            tri.points[0] = point
            tri.points[-1] = point
            tri.make_jagged()

        triangle.add_updater(update_triangle)

        self.add(tip_tracker)
        self.play(tip_tracker.shift, 0.5 * LEFT + 1.0 * UP)
        self.play(tip_tracker.shift, 2.0 * DOWN)
        self.play(tip_tracker.shift, 1.5 * RIGHT)
        self.play(tip_tracker.shift, 1.0 * LEFT + 1.0 * UP)
        self.wait()

        # Show box
        t2c = {"x": x_color, "y": y_color}
        ineq1 = TexMobject("0", "\\le ", "x", "\\le", "1", tex_to_color_map=t2c)
        ineq2 = TexMobject("0", "\\le ", "y", "\\le", "1", tex_to_color_map=t2c)

        ineqs = VGroup(ineq1, ineq2)
        ineqs.scale(1.5)
        ineqs.arrange(DOWN, buff=MED_LARGE_BUFF)
        ineqs.next_to(triangle, DOWN, buff=1.5)

        box = Square(
            fill_color=DARK_GREY,
            fill_opacity=0.75,
            stroke_color=LIGHT_GREY,
            stroke_width=2,
        )
        box.replace(Line(axes.c2p(0, 0), axes.c2p(1, 1)))
        box_outline = box.copy()
        box_outline.set_fill(opacity=0)
        box_outline.set_stroke(YELLOW, 3)

        self.add(box, axes, x_line, y_line, coord_label, dot)
        self.play(
            FadeIn(box),
            LaggedStartMap(FadeInFromDown, ineqs)
        )
        self.play(
            ShowCreationThenFadeOut(box_outline)
        )
        self.wait()

        # x >= y slice
        region = Polygon(
            axes.c2p(0, 0),
            axes.c2p(1, 0),
            axes.c2p(1, 1),
            fill_color=GREY_BROWN,
            fill_opacity=0.75,
            stroke_color=GREY_BROWN,
            stroke_width=2,
        )
        region_outline = region.copy()
        region_outline.set_fill(opacity=0)
        region_outline.set_stroke(YELLOW, 3)

        x_eq_y_line = Line(axes.c2p(0, 0), axes.c2p(1, 1))
        x_eq_y_line.set_stroke(self.x_eq_y_color, 2)
        x_eq_y_label = TexMobject("x=y", tex_to_color_map=t2c)
        x_eq_y_label.next_to(x_eq_y_line.get_end(), LEFT, MED_LARGE_BUFF)
        x_eq_y_label.shift(0.75 * DL)

        ineq = TexMobject("0", "\\le", "y", "\\le", "x", "\\le", "1")
        ineq.set_color_by_tex("x", x_color)
        ineq.set_color_by_tex("y", y_color)
        ineq.scale(1.5)
        ineq.move_to(ineqs, LEFT)

        self.add(region, axes, x_line, y_line, coord_label, dot)
        self.play(
            FadeIn(region),
            ShowCreation(x_eq_y_line),
            # FadeInFromDown(x_eq_y_label),
            Transform(ineq1[:2], ineq[:2], remover=True),
            Transform(ineq1[2:], ineq[4:], remover=True),
            Transform(ineq2[:4], ineq[:4], remover=True),
            Transform(ineq2[4:], ineq[6:], remover=True),
        )
        self.add(ineq)
        self.play(ShowCreationThenFadeOut(region_outline))
        self.wait()

        # x + y <= 1 slice
        xpy1_line = Line(axes.c2p(0, 1), axes.c2p(1, 0))
        xpy1_line.set_stroke(GREEN, 2)
        xpy1_label = TexMobject("x+y=1", tex_to_color_map=t2c)
        xpy1_label.next_to(xpy1_line.get_start(), RIGHT, MED_LARGE_BUFF)
        xpy1_label.shift(0.75 * DR)

        xpy1_ineq = TexMobject("1 \\le x + y", tex_to_color_map=t2c)
        xpy1_ineq.scale(1.5)
        xpy1_ineq.next_to(ineq, DOWN, buff=MED_LARGE_BUFF)

        ms_region = Polygon(
            axes.c2p(1, 0),
            axes.c2p(0.5, 0.5),
            axes.c2p(1, 1),
            fill_color=BLUE_E,
            fill_opacity=0.75,
            stroke_width=0,
        )
        ms_outline = ms_region.copy()
        ms_outline.set_fill(opacity=0)
        ms_outline.set_stroke(YELLOW, 2)

        tt_line = Line(DOWN, UP, color=WHITE)
        tt_line.set_height(0.25)
        tt_line.add_updater(lambda m: m.move_to(tip_tracker))

        self.play(
            ShowCreation(xpy1_line),
            # FadeInFrom(xpy1_label, DOWN),
            FadeInFrom(xpy1_ineq, UP)
        )
        self.wait()
        self.play(
            tip_tracker.set_y, triangle.get_bottom()[1] + 0.01,
            FadeIn(tt_line),
        )
        self.wait()

        self.add(ms_region, axes, x_line, y_line, coord_label, dot)
        self.play(
            FadeIn(ms_region),
            region.set_fill, DARK_GREY,
        )
        self.wait()

        # Move tip around
        self.play(
            tip_tracker.shift, UP + RIGHT,
            FadeOut(tt_line),
        )
        self.wait()
        self.play(tip_tracker.shift, 0.5 * DOWN + LEFT, run_time=2)
        self.wait()
        self.play(tip_tracker.shift, UP + 0.7 * LEFT, run_time=2)
        self.wait()
        equilateral_point = triangle.get_bottom() + unit_factor * 0.5 * np.sqrt(3) * UP
        self.play(
            tip_tracker.move_to,
            equilateral_point,
            run_time=2,
        )
        self.wait()

        # Label as moduli space
        ms_words = TextMobject("Moduli\\\\", "Space")
        ms_words.scale(1.5)
        ms_words.next_to(ms_region, RIGHT, buff=0.35)
        ms_arrow = Arrow(
            ms_words[1].get_corner(DL),
            ms_region.get_center(),
            path_arc=-90 * DEGREES,
            buff=0.1,
        )
        # ms_arrow.rotate(-10 * DEGREES)
        ms_arrow.shift(0.1 * RIGHT)
        ms_arrow.scale(0.95)

        self.play(
            FadeInFrom(ms_words, LEFT),
        )
        self.play(ShowCreation(ms_arrow))
        self.wait()

        # Show right triangles
        alpha = np.arcsin(0.8)
        vect = rotate_vector(0.6 * unit_factor * LEFT, -alpha)
        new_tip = triangle.get_corner(DR) + vect

        elbow = VMobject()
        elbow.start_new_path(RIGHT)
        elbow.add_line_to(UR)
        elbow.add_line_to(UP)

        elbow.rotate(3 * TAU / 4 - alpha, about_point=ORIGIN)
        elbow.scale(0.2, about_point=ORIGIN)
        elbow.shift(new_tip)

        elbow_circle = Circle()
        elbow_circle.replace(elbow)
        elbow_circle.scale(3)
        elbow_circle.move_to(new_tip)
        elbow_circle.set_stroke(self.right_color, 3)

        right_words = TextMobject("Right triangle")
        right_words.scale(1.5)
        right_words.set_color(self.right_color)
        right_words.next_to(triangle, DOWN, buff=1.5)

        ineqs = VGroup(ineq, xpy1_ineq)

        self.play(
            tip_tracker.move_to, new_tip,
            FadeOut(ms_words),
            FadeOut(ms_arrow),
        )
        self.play(
            ShowCreation(elbow),
            FadeInFrom(right_words, UP),
            FadeOutAndShift(ineqs, DOWN),
        )
        self.play(
            ShowCreationThenFadeOut(elbow_circle),
        )

        # Show circular arc
        pythag_eq = TexMobject("x^2 + y^2", "=", "1", tex_to_color_map=t2c)
        pythag_eq.scale(1.5)
        pythag_eq.next_to(right_words, DOWN, buff=MED_LARGE_BUFF)

        arc = Arc(
            start_angle=90 * DEGREES,
            angle=-90 * DEGREES,
            color=self.right_color,
        )
        arc.replace(box)

        self.play(
            FadeInFrom(pythag_eq, UP),
        )
        self.add(arc, arc)
        self.play(ShowCreation(arc))
        self.wait()

        # Acute region
        arc_piece = VMobject()
        arc_piece.pointwise_become_partial(arc, 0.5, 1.0)

        acute_region = VMobject()
        acute_region.start_new_path(axes.c2p(1, 1))
        acute_region.add_line_to(arc_piece.get_start())
        acute_region.append_vectorized_mobject(arc_piece)
        acute_region.add_line_to(axes.c2p(1, 1))
        acute_region.set_fill(self.acute_color, 1)
        acute_region.set_stroke(width=0)

        obtuse_region = VMobject()
        obtuse_region.start_new_path(axes.c2p(1, 0))
        obtuse_region.add_line_to(axes.c2p(0.5, 0.5))
        obtuse_region.add_line_to(arc_piece.get_start())
        obtuse_region.append_vectorized_mobject(arc_piece)
        obtuse_region.set_fill(self.obtuse_color, 1)
        obtuse_region.set_stroke(width=0)

        acute_words = TextMobject("Acute triangle")
        acute_words.set_color(self.acute_color)
        obtuse_words = TextMobject("Obtuse triangle")
        obtuse_words.set_color(self.obtuse_color)
        for words in [acute_words, obtuse_words]:
            words.scale(1.5)
            words.move_to(right_words)

        eq = pythag_eq[-2]
        gt = TexMobject(">").replace(eq)
        gt.set_color(self.acute_color)
        lt = TexMobject("<").replace(eq)
        lt.set_color(self.obtuse_color)

        self.add(acute_region, coord_label, x_line, y_line, xpy1_line, x_eq_y_line, dot)
        self.play(
            tip_tracker.shift, 0.5 * UP,
            coord_label.set_opacity, 0,
            FadeOut(elbow),
            FadeIn(acute_region),
            FadeOutAndShift(right_words, UP),
            FadeOutAndShift(eq, UP),
            FadeInFrom(acute_words, DOWN),
            FadeInFrom(gt, DOWN),
        )
        self.wait()
        self.play(tip_tracker.shift, 0.5 * RIGHT)
        self.wait()
        self.add(obtuse_region, coord_label, x_line, y_line, xpy1_line, x_eq_y_line, dot)
        self.play(
            tip_tracker.shift, 1.5 * DOWN,
            FadeIn(obtuse_region),
            FadeOutAndShift(acute_words, DOWN),
            FadeOutAndShift(gt, DOWN),
            FadeInFrom(obtuse_words, UP),
            FadeInFrom(lt, UP),
        )
        self.wait()
        self.play(tip_tracker.shift, 0.5 * LEFT)
        self.play(tip_tracker.shift, 0.5 * DOWN)
        self.play(tip_tracker.shift, 0.5 * RIGHT)
        self.play(tip_tracker.shift, 0.5 * UP)
        self.wait()

        # Ambient changes
        self.play(
            FadeOut(obtuse_words),
            FadeOut(pythag_eq[:-2]),
            FadeOut(pythag_eq[-1]),
            FadeOut(lt),
        )
        self.play(
            tip_tracker.move_to, equilateral_point + 0.25 * DL,
            path_arc=30 * DEGREES,
            run_time=8,
        )

    #
    def get_triangles_and_classes(self):
        original_triangles = VGroup(*[
            self.get_random_triangle()
            for x in range(5)
        ])
        original_triangles.submobjects[4] = self.get_random_triangle()  # Hack
        all_triangles = VGroup()
        tri_classes = VGroup()
        for triangle in original_triangles:
            all_triangles.add(triangle)
            tri_class = VGroup()
            tri_class.add(triangle)
            for x in range(2):
                tri_copy = triangle.copy()
                angle = TAU * np.random.random()
                scalar = 0.25 + 1.5 * np.random.random()

                tri_copy.rotate(angle - tri_copy.angle)
                tri_copy.angle = angle
                tri_copy.scale(scalar / tri_copy.scalar)
                tri_copy.scalar = scalar

                all_triangles.add(tri_copy)
                tri_class.add(tri_copy)
            tri_classes.add(tri_class)

        colors = Color(BLUE).range_to(Color(RED), len(all_triangles))
        for triangle, color in zip(all_triangles, colors):
            # triangle.set_color(random_bright_color())
            triangle.set_color(color)

        all_triangles.shuffle()
        all_triangles.arrange_in_grid(3, 5, buff=MED_LARGE_BUFF)
        all_triangles.set_height(6)
        sf = 1.25
        all_triangles.stretch(sf, 0)
        for triangle in all_triangles:
            triangle.stretch(1 / sf, 0)
        # all_triangles.next_to(title, DOWN)
        all_triangles.to_edge(DOWN, LARGE_BUFF)

        return all_triangles, tri_classes

    def get_random_triangle(self, x=None, y=None):
        y = np.random.random()
        x = y + np.random.random()
        if x + y <= 1:
            diff = 1 - (x + y)
            x += diff
            y += diff
        tri = self.get_triangle(x, y)
        tri.angle = TAU * np.random.random()
        tri.scalar = 0.25 + np.random.random() * 1.5

        tri.rotate(tri.angle)
        tri.scale(tri.scalar)
        return tri

    def get_triangle(self, x, y):
        # Enforce assumption that x > y
        if y > x:
            raise Exception("Please ensure x >= y.  Thank you.")
        plane = self.plane

        # Heron
        s = (1 + x + y) / 2.0
        area = np.sqrt(s * (s - 1.0) * (s - x) * (s - y))
        beta = np.arcsin(2 * area / x)
        tip_point = RIGHT + rotate_vector(x * LEFT, -beta)

        color = self.get_triangle_color(x, y)
        return Polygon(
            plane.c2p(0, 0),
            plane.c2p(1, 0),
            plane.c2p(*tip_point[:2]),
            color=color,
            fill_opacity=self.triangle_fill_opacity,
        )

    def get_triangle_color(self, x, y):
        epsilon = 1e-4
        if x + y == 1:
            return self.x_eq_y_color
        elif x == 1:
            return self.x1_color
        elif y == 1:
            return self.y1_color
        elif np.abs(x**2 + y**2 - 1) < epsilon:
            return self.right_color
        elif x**2 + y**2 < 1:
            return self.obtuse_color
        elif x**2 + y**2 > 1:
            return self.acute_color
        assert(False)  # Should not get here

    def get_triangle_xy(self, triangle):
        A, B, C = triangle.get_start_anchors()[:3]
        a = get_norm(B - C)
        b = get_norm(C - A)
        c = get_norm(A - B)
        sides = np.array(sorted([a, b, c]))
        sides = sides / np.max(sides)
        return sides[1], sides[0]

    def get_triangle_x(self, triangle):
        return self.get_triangle_xy(triangle)[0]

    def get_triangle_y(self, triangle):
        return self.get_triangle_xy(triangle)[1]


class Credits(Scene):
    def construct(self):
        items = VGroup(
            TextMobject("Written by\\\\Jayadev Athreya"),
            TextMobject("Illustrated and Narrated by\\\\Grant Sanderson"),
            TextMobject(
                "3Blue1Brown\\\\",
                "\\copyright {} Copyright 2019\\\\",
                "www.3blue1brown.com\\\\",
            ),
        )
        items.arrange(DOWN, buff=LARGE_BUFF)

        items[-1].set_color(LIGHT_GREY)
        items[-1].scale(0.8, about_edge=UP)
        items[-1].to_edge(DOWN)

        self.add(items[-1])
        self.play(LaggedStartMap(FadeInFromDown, items[:-1]))
        self.wait()
