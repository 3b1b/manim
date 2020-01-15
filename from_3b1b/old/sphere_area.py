from manimlib.imports import *
from active_projects.shadows import *


# Abstract scenes

class Cylinder(Sphere):
    """
    Inherits from sphere so as to be as aligned as possible
    for transformations
    """

    def func(self, u, v):
        return np.array([
            np.cos(v),
            np.sin(v),
            np.cos(u)
        ])


class UnwrappedCylinder(Cylinder):
    def func(self, u, v):
        return np.array([
            v - PI,
            -self.radius,
            np.cos(u)
        ])


class ParametricDisc(Sphere):
    CONFIG = {
        "u_min": 0,
        "u_max": 1,
        "stroke_width": 0,
        "checkerboard_colors": [BLUE_D],
    }

    def func(self, u, v):
        return np.array([
            u * np.cos(v),
            u * np.sin(v),
            0,
        ])


class SphereCylinderScene(SpecialThreeDScene):
    CONFIG = {
        "cap_config": {
            "stroke_width": 1,
            "stroke_color": WHITE,
            "fill_color": BLUE_D,
            "fill_opacity": 1,
        }
    }

    def get_cylinder(self, **kwargs):
        config = merge_dicts_recursively(self.sphere_config, kwargs)
        return Cylinder(**config)

    def get_cylinder_caps(self):
        R = self.sphere_config["radius"]
        caps = VGroup(*[
            Circle(
                radius=R,
                **self.cap_config,
            ).shift(R * vect)
            for vect in [IN, OUT]
        ])
        caps.set_shade_in_3d(True)
        return caps

    def get_unwrapped_cylinder(self):
        return UnwrappedCylinder(**self.sphere_config)

    def get_xy_plane(self):
        pass

    def get_ghost_surface(self, surface):
        result = surface.copy()
        result.set_fill(BLUE_E, opacity=0.5)
        result.set_stroke(WHITE, width=0.5, opacity=0.5)
        return result

    def project_point(self, point):
        radius = self.sphere_config["radius"]
        result = np.array(point)
        result[:2] = normalize(result[:2]) * radius
        return result

    def project_mobject(self, mobject):
        return mobject.apply_function(self.project_point)


# Scenes for video

class AskAboutShadowRelation(SpecialThreeDScene):
    CONFIG = {
        "R_color": YELLOW,
        "space_out_factor": 1.15,
    }

    def construct(self):
        self.show_surface_area()
        self.show_four_circles()
        self.ask_why()
        self.show_all_pieces()

    def show_surface_area(self):
        sphere = self.get_sphere()
        sphere.set_fill(BLUE_E, opacity=0.5)
        sphere.add_updater(
            lambda s, dt: s.rotate(0.1 * dt, axis=OUT)
        )
        pieces = sphere.deepcopy()
        pieces.space_out_submobjects(1.5)
        pieces.shift(IN)
        pieces.set_color(GREEN)

        # radial_line = Line(ORIGIN, sphere.get_right())
        # R_label = TexMobject("R")
        # R_label.set_color(BLUE)
        # R_label.rotate(90 * DEGREES, RIGHT)
        # R_label.next_to(radial_line, OUT, SMALL_BUFF)

        sa_equation = TexMobject(
            "\\text{Surface area} = 4\\pi R^2",
            tex_to_color_map={"R": BLUE}
        )
        sa_equation.scale(1.5)
        sa_equation.to_edge(UP)

        self.set_camera_orientation(
            phi=70 * DEGREES,
            theta=-90 * DEGREES,
        )
        self.add_fixed_in_frame_mobjects(sa_equation)
        self.play(
            Write(sphere, stroke_width=1),
            FadeInFromDown(sa_equation),
            # ShowCreation(radial_line),
            # FadeInFrom(R_label, IN),
        )
        # self.play(
        #     Transform(
        #         sphere, pieces,
        #         rate_func=there_and_back_with_pause,
        #         run_time=2
        #     )
        # )
        self.play(LaggedStartMap(
            UpdateFromAlphaFunc, sphere,
            lambda mob: (mob, lambda m, a: m.set_fill(
                color=interpolate_color(BLUE_E, YELLOW, a),
                opacity=interpolate(0.5, 1, a)
            )),
            rate_func=there_and_back,
            lag_ratio=0.1,
            run_time=4
        ))
        self.play(
            sphere.scale, 0.75,
            sphere.shift, 3 * LEFT,
            sa_equation.shift, 3 * LEFT,
        )
        self.wait(2)

        self.sphere = sphere
        self.sa_equation = sa_equation

    def show_four_circles(self):
        sphere = self.sphere
        shadow = Circle(
            radius=sphere.get_width() / 2,
            stroke_color=WHITE,
            stroke_width=1,
            fill_color=BLUE_E,
            fill_opacity=1,
        )
        radial_line = Line(
            shadow.get_center(),
            shadow.get_right(),
            color=YELLOW
        )
        R_label = TexMobject("R").set_color(self.R_color)
        R_label.scale(0.8)
        R_label.next_to(radial_line, DOWN, SMALL_BUFF)
        shadow.add(radial_line, R_label)
        shadow.move_to(
            self.camera.transform_points_pre_display(sphere, [sphere.get_center()])[0]
        )

        shadows = VGroup(*[shadow.copy() for x in range(4)])
        shadows.arrange_in_grid(buff=MED_LARGE_BUFF)
        shadows.to_edge(RIGHT)

        area_label = TexMobject(
            "\\pi R^2",
            tex_to_color_map={"R": self.R_color}
        )
        area_label.scale(1.2)
        area_labels = VGroup(*[
            area_label.copy().move_to(interpolate(
                mob.get_center(), mob.get_top(), 0.5
            ))
            for mob in shadows
        ])

        # shadow.move_to(sphere)
        self.add_fixed_in_frame_mobjects(shadow)
        self.play(DrawBorderThenFill(shadow))
        anims = []
        for new_shadow in shadows:
            old_shadow = shadow.copy()
            self.add_fixed_in_frame_mobjects(old_shadow)
            anims.append(Transform(
                old_shadow, new_shadow, remover=True
            ))
        self.remove(shadow)
        self.play(*anims)
        self.add_fixed_in_frame_mobjects(shadows, area_labels)
        self.play(LaggedStartMap(FadeInFromLarge, area_labels))
        self.wait()

        self.shadows = shadows
        self.shadow_area_labels = area_labels

    def ask_why(self):
        pass

    def show_all_pieces(self):
        shadows = self.shadows
        area_labels = self.shadow_area_labels
        sphere = self.sphere

        shadow_pieces_group = VGroup()
        for shadow in shadows:
            pieces = ParametricSurface(
                func=lambda u, v: np.array([
                    u * np.cos(TAU * v),
                    u * np.sin(TAU * v),
                    0,
                ]),
                resolution=(12, 24)
            )
            pieces.replace(shadow)
            pieces.match_style(sphere)
            shadow_pieces_group.add(pieces)

        self.add_fixed_in_frame_mobjects(shadow_pieces_group)
        self.play(
            FadeOut(shadows),
            FadeOut(area_labels),
            FadeIn(shadow_pieces_group)
        )
        self.show_area_pieces(sphere)
        self.wait()
        self.show_area_pieces(*shadow_pieces_group)
        self.wait(2)
        self.unshow_area_pieces(sphere, *shadow_pieces_group)
        self.wait(3)

    def show_area_pieces(self, *mobjects):
        for mob in mobjects:
            mob.generate_target()
            mob.target.space_out_submobjects(self.space_out_factor)
        self.play(*map(MoveToTarget, mobjects))
        self.play(*[
            LaggedStartMap(
                ApplyMethod, mob,
                lambda m: (m.set_fill, YELLOW, 1),
                rate_func=there_and_back,
                lag_ratio=0.25,
                run_time=1.5
            )
            for mob in mobjects
        ])

    def unshow_area_pieces(self, *mobjects):
        self.play(*[
            ApplyMethod(
                mob.space_out_submobjects,
                1.0 / self.space_out_factor
            )
            for mob in mobjects
        ])


class ButWhy(TeacherStudentsScene):
    CONFIG = {
        "student_mode": "raise_right_hand",
        "question": "But why?",
        "teacher_mode": "guilty"
    }

    def construct(self):
        for student in self.students:
            student.change("pondering", self.screen)
        self.student_says(
            "But why?",
            student_index=2,
            target_mode=self.student_mode,
            bubble_kwargs={"direction": LEFT},
        )
        self.play(
            self.teacher.change, self.teacher_mode, self.students[2]
        )
        self.wait(5)


class ButWhyHappy(ButWhy):
    CONFIG = {
        "teacher_mode": "happy"
    }


class ButWhySassy(ButWhy):
    CONFIG = {
        "teacher_mode": "sassy"
    }


class ButWhyHesitant(ButWhy):
    CONFIG = {
        "teacher_mode": "hesitant"
    }


class ButWhyAngry(ButWhy):
    CONFIG = {
        "teacher_mode": "angry"
    }


class TryFittingCirclesDirectly(ExternallyAnimatedScene):
    pass


class PreviewTwoMethods(MovingCameraScene):
    def construct(self):
        thumbnails = Group(
            ImageMobject("SphereSurfaceProof1"),
            ImageMobject("SphereSurfaceProof2"),
        )
        for thumbnail in thumbnails:
            thumbnail.set_width(FRAME_WIDTH / 2 - 1)
            thumbnail.add_to_back(SurroundingRectangle(
                thumbnail, buff=0,
                stroke_color=WHITE,
                stroke_width=5
            ))
        thumbnails.arrange(RIGHT, buff=LARGE_BUFF)

        title = TextMobject("Two proofs")
        title.scale(2)
        title.to_edge(UP)

        frame = self.camera.frame

        self.add(title)
        for thumbnail in thumbnails:
            self.play(FadeInFromDown(thumbnail))
        self.wait()
        for thumbnail in thumbnails:
            frame.save_state()
            self.play(
                frame.replace, thumbnail,
                run_time=2
            )
            self.wait()
            self.play(Restore(frame, run_time=2))


class MapSphereOntoCylinder(SphereCylinderScene):
    def construct(self):
        sphere = self.get_sphere()
        sphere_ghost = self.get_ghost_surface(sphere)
        sphere_ghost.set_stroke(width=0)
        axes = self.get_axes()
        cylinder = self.get_cylinder()
        cylinder.set_fill(opacity=0.75)
        radius = cylinder.get_width() / 2

        self.add(axes, sphere_ghost, sphere)
        self.wait()
        self.begin_ambient_camera_rotation()
        self.move_camera(
            **self.default_angled_camera_position,
            run_time=2,
        )
        self.wait(2)
        self.play(
            ReplacementTransform(sphere, cylinder),
            run_time=3
        )
        self.wait(3)

        # Get rid of caps
        caps = self.get_cylinder_caps()
        caps[1].set_shade_in_3d(False)
        label = TextMobject("Label")
        label.scale(1.5)
        label.stretch(0.8, 0)
        label.rotate(90 * DEGREES, RIGHT)
        label.rotate(90 * DEGREES, OUT)
        label.shift(np.log(radius + SMALL_BUFF) * RIGHT)
        label.apply_complex_function(np.exp)
        label.rotate(90 * DEGREES, IN, about_point=ORIGIN)
        label.shift(OUT)
        label.set_background_stroke(width=0)

        self.play(FadeIn(caps))
        self.wait()
        self.play(
            caps.space_out_submobjects, 2,
            caps.fade, 1,
            remover=True
        )
        self.play(Write(label))
        self.wait(2)
        self.play(FadeOut(label))

        # Unwrap
        unwrapped_cylinder = self.get_unwrapped_cylinder()
        unwrapped_cylinder.set_fill(opacity=0.75)
        self.play(
            ReplacementTransform(cylinder, unwrapped_cylinder),
            run_time=3
        )
        self.stop_ambient_camera_rotation()
        self.move_camera(
            phi=90 * DEGREES,
            theta=-90 * DEGREES,
        )

        # Show dimensions
        stroke_width = 5
        top_line = Line(
            PI * radius * LEFT + radius * OUT,
            PI * radius * RIGHT + radius * OUT,
            color=YELLOW,
            stroke_width=stroke_width,
        )
        side_line = Line(
            PI * radius * LEFT + radius * OUT,
            PI * radius * LEFT + radius * IN,
            color=RED,
            stroke_width=stroke_width,
        )
        lines = VGroup(top_line, side_line)
        lines.shift(radius * DOWN)
        two_pi_R = TexMobject("2\\pi R")
        two_R = TexMobject("2R")
        texs = VGroup(two_pi_R, two_R)
        for tex in texs:
            tex.scale(1.5)
            tex.rotate(90 * DEGREES, RIGHT)
        two_pi_R.next_to(top_line, OUT)
        two_R.next_to(side_line, RIGHT)

        self.play(
            ShowCreation(top_line),
            FadeInFrom(two_pi_R, IN)
        )
        self.wait()
        self.play(
            ShowCreation(side_line),
            FadeInFrom(two_R, RIGHT)
        )
        self.wait()


class CircumferenceOfCylinder(SphereCylinderScene):
    def construct(self):
        sphere = self.get_sphere()
        sphere_ghost = self.get_ghost_surface(sphere)
        cylinder = self.get_cylinder()
        cylinder_ghost = self.get_ghost_surface(cylinder)
        cylinder_ghost.set_stroke(width=0)

        radius = self.sphere_config["radius"]
        circle = Circle(radius=radius)
        circle.set_stroke(YELLOW, 5)
        circle.shift(radius * OUT)

        height = Line(radius * IN, radius * OUT)
        height.shift(radius * LEFT)
        height.set_stroke(RED, 5)

        self.set_camera_orientation(
            phi=70 * DEGREES,
            theta=-95 * DEGREES,
        )
        self.begin_ambient_camera_rotation(0.01)
        self.add(sphere_ghost, cylinder_ghost)
        self.wait()
        self.play(ShowCreation(circle))
        self.wait(2)
        self.play(ShowCreation(height))
        self.wait(5)


class UnfoldCircles(Scene):
    CONFIG = {
        "circle_style": {
            "fill_color": GREY_BROWN,
            "fill_opacity": 0,
            "stroke_color": GREY_BROWN,
            "stroke_width": 2,
        },
        "radius": 1.0,
        "dr": 0.01,
    }

    def construct(self):
        self.show_rectangle_with_formula()
        self.add_four_circles()

    def show_rectangle_with_formula(self):
        TexMobject.CONFIG["background_stroke_width"] = 1
        R = self.radius
        rect = Rectangle(width=TAU * R, height=2 * R)
        rect.set_fill(BLUE_E, 1)
        rect.set_stroke(width=0)
        p0, p1, p2 = [rect.get_corner(v) for v in (DL, UL, UR)]
        h_line = Line(p0, p1)
        h_line.set_stroke(RED, 3)
        w_line = Line(p1, p2)
        w_line.set_stroke(YELLOW, 3)
        two_R = TexMobject("2", "R")
        two_R.next_to(h_line, LEFT)
        two_pi_R = TexMobject("2", "\\pi", "R")
        two_pi_R.next_to(w_line, UP)

        pre_area_label = TexMobject(
            "2\\cdot", "2", "\\pi", "R", "\\cdot R"
        )
        area_label = TexMobject("4", "\\pi", "R^2")
        for label in [area_label, pre_area_label]:
            label.next_to(rect.get_center(), UP, SMALL_BUFF)

        self.rect_group = VGroup(
            rect, h_line, w_line,
            two_R, two_pi_R, area_label
        )
        self.area_label = area_label
        self.rect = rect

        self.add(rect, h_line, w_line, two_R, two_pi_R)
        self.play(
            TransformFromCopy(two_R[0], pre_area_label[0]),
            TransformFromCopy(two_R[1], pre_area_label[-1]),
            TransformFromCopy(two_pi_R, pre_area_label[1:-1]),
        )
        self.wait()
        self.play(
            ReplacementTransform(pre_area_label[:2], area_label[:1]),
            ReplacementTransform(pre_area_label[2], area_label[1]),
            ReplacementTransform(pre_area_label[3:], area_label[2:]),
        )
        self.wait()
        self.play(
            self.rect_group.to_corner, UL,
            {"buff": MED_SMALL_BUFF}
        )

    def add_four_circles(self):
        rect_group = self.rect_group
        radius = self.radius

        radii_lines = VGroup(*[
            Line(radius * UP, ORIGIN).set_stroke(WHITE, 2)
            for x in range(4)
        ])
        radii_lines.arrange_in_grid(buff=1.3)
        radii_lines[2:].shift(RIGHT)
        radii_lines.next_to(rect_group, DOWN, buff=1.3)
        R_labels = VGroup(*[
            TexMobject("R").next_to(line, LEFT, SMALL_BUFF)
            for line in radii_lines
        ])

        unwrap_factor_tracker = ValueTracker(0)

        def get_circle(line):
            return always_redraw(
                lambda: self.get_unwrapped_circle(
                    radius=radius, dr=self.dr,
                    unwrap_factor=unwrap_factor_tracker.get_value(),
                    center=line.get_top()
                )
            )

        circles = VGroup(*[get_circle(line) for line in radii_lines])
        circle_copies = circles.copy()
        for mob in circle_copies:
            mob.clear_updaters()

        self.play(
            LaggedStartMap(Write, circle_copies, lag_ratio=0.7),
            LaggedStartMap(Write, R_labels),
            LaggedStartMap(ShowCreation, radii_lines),
        )
        self.remove(circle_copies)
        self.add(circles, radii_lines, R_labels)
        self.wait()
        self.play(
            radii_lines[2:].shift, 2.9 * RIGHT,
            R_labels[2:].shift, 2.9 * RIGHT,
            VGroup(
                radii_lines[:2], R_labels[:2]
            ).to_edge, LEFT, {"buff": 1.0}
        )
        self.play(
            unwrap_factor_tracker.set_value, 1,
            run_time=2
        )
        self.wait()

        # Move triangles
        triangles = circles.copy()
        for triangle in triangles:
            triangle.clear_updaters()
            border = Polygon(*[
                triangle.get_corner(vect)
                for vect in (DL, UL, DR)
            ])
            border.set_stroke(WHITE, 1)
            triangle.add(border)
            triangle.generate_target()
        rect = self.rect
        for i, triangle in enumerate(triangles):
            if i % 2 == 1:
                triangle.target.rotate(PI)
            vect = UP if i < 2 else DOWN
            triangle.target.move_to(rect, vect)

        self.play(FadeIn(triangles))
        self.add(triangles, triangles.copy(), self.area_label)
        self.play(MoveToTarget(triangles[0]))
        self.wait()
        self.play(LaggedStartMap(MoveToTarget, triangles))
        self.wait()

    #
    def get_unwrapped_circle(self, radius, dr, unwrap_factor=0, center=ORIGIN):
        radii = np.arange(0, radius + dr, dr)
        rings = VGroup()
        for r in radii:
            r_factor = 1 + 3 * (r / radius)
            alpha = unwrap_factor**r_factor
            alpha = np.clip(alpha, 0, 0.9999)
            angle = interpolate(TAU, 0, alpha)
            length = TAU * r
            arc_radius = length / angle
            ring = Arc(
                start_angle=-90 * DEGREES,
                angle=angle,
                radius=arc_radius,
                **self.circle_style
            )
            ring.shift(center + (r - arc_radius) * DOWN)
            # ring = AnnularSector(
            #     inner_radius=r1,
            #     outer_radius=r2,
            #     angle=TAU,
            #     start_angle=-TAU / 4,
            #     **self.circle_style
            # )
            rings.add(ring)
        return rings


class ShowProjection(SphereCylinderScene):
    CONFIG = {
        # "default_angled_camera_position": {
        #     "theta": -155 * DEGREES,
        # }
    }

    def construct(self):
        self.setup_shapes()
        self.show_many_tiny_rectangles()
        self.project_all_rectangles()
        self.focus_on_one()
        self.label_sides()
        self.show_length_scaled_up()
        self.show_height_scaled_down()

    def setup_shapes(self):
        self.sphere = self.get_sphere()
        self.cylinder = self.get_cylinder()
        self.ghost_sphere = self.get_ghost_surface(self.sphere)
        self.ghost_sphere.scale(0.99)
        self.ghost_cylinder = self.get_ghost_surface(self.cylinder)
        self.ghost_cylinder.set_stroke(width=0)

        self.add(self.get_axes())
        self.set_camera_to_default_position()
        self.begin_ambient_camera_rotation()

    def show_many_tiny_rectangles(self):
        ghost_sphere = self.ghost_sphere
        pieces = self.sphere.copy()
        random.shuffle(pieces.submobjects)
        for piece in pieces:
            piece.save_state()
        pieces.space_out_submobjects(2)
        pieces.fade(1)

        self.add(ghost_sphere)
        self.play(LaggedStartMap(Restore, pieces))
        self.wait()

        self.pieces = pieces

    def project_all_rectangles(self):
        pieces = self.pieces
        for piece in pieces:
            piece.save_state()
            piece.generate_target()
            self.project_mobject(piece.target)
            piece.target.set_fill(opacity=0.5)

        example_group = self.get_example_group([1, -1, 2])
        proj_lines = example_group[1]
        self.example_group = example_group

        self.play(*map(ShowCreation, proj_lines))
        self.play(
            LaggedStartMap(MoveToTarget, pieces),
        )
        self.wait()

    def focus_on_one(self):
        ghost_cylinder = self.ghost_cylinder
        pieces = self.pieces

        example_group = self.example_group
        original_rect, rect_proj_lines, rect = example_group

        equation = self.get_equation(rect)
        lhs, equals, rhs = equation[:3]
        lhs.save_state()
        rhs.save_state()

        self.play(
            FadeIn(ghost_cylinder),
            FadeOut(pieces),
            FadeIn(original_rect),
        )
        self.play(TransformFromCopy(original_rect, rect))
        self.wait()
        self.add_fixed_in_frame_mobjects(lhs, equals, rhs)
        self.move_fixed_in_frame_mob_to_unfixed_mob(lhs, original_rect)
        self.move_fixed_in_frame_mob_to_unfixed_mob(rhs, rect)
        self.play(
            Restore(lhs),
            Restore(rhs),
            FadeInFromDown(equals),
        )
        self.wait(5)

        self.equation = equation
        self.example_group = example_group

    def label_sides(self):
        sphere = self.sphere
        equation = self.equation
        w_brace, h_brace = equation.braces
        width_label, height_label = equation.labels

        u_values, v_values = sphere.get_u_values_and_v_values()
        radius = sphere.radius
        lat_lines = VGroup(*[
            ParametricFunction(
                lambda t: radius * sphere.func(u, t),
                t_min=sphere.v_min,
                t_max=sphere.v_max,
            )
            for u in u_values
        ])
        lon_lines = VGroup(*[
            ParametricFunction(
                lambda t: radius * sphere.func(t, v),
                t_min=sphere.u_min,
                t_max=sphere.u_max,
            )
            for v in v_values
        ])
        for lines in lat_lines, lon_lines:
            for line in lines:
                line.add(DashedVMobject(line, spacing=-1))
                line.set_points([])
                line.set_stroke(width=2)
            lines.set_shade_in_3d(True)
        lat_lines.set_color(RED)
        lon_lines.set_color(PINK)

        self.play(
            *map(ShowCreationThenDestruction, lat_lines),
            run_time=2
        )
        self.add_fixed_in_frame_mobjects(w_brace, width_label)
        self.play(
            GrowFromCenter(w_brace),
            Write(width_label),
        )
        self.wait()
        self.play(
            *map(ShowCreationThenDestruction, lon_lines),
            run_time=2
        )
        self.add_fixed_in_frame_mobjects(h_brace, height_label)
        self.play(
            GrowFromCenter(h_brace),
            Write(height_label),
        )
        self.wait(2)

    def show_length_scaled_up(self):
        ghost_sphere = self.ghost_sphere
        example_group = self.example_group
        equation = self.equation
        equation.save_state()
        new_example_groups = [
            self.get_example_group([1, -1, z])
            for z in [6, 0.25]
        ]
        r1, lines, r2 = example_group

        self.stop_ambient_camera_rotation()
        self.move_camera(
            phi=65 * DEGREES,
            theta=-80 * DEGREES,
            added_anims=[
                ghost_sphere.set_stroke, {"opacity": 0.1},
                lines.set_stroke, {"width": 3},
            ]
        )
        for eg in new_example_groups:
            eg[1].set_stroke(width=3)
        self.show_length_stretch_of_rect(example_group)
        all_example_groups = [example_group, *new_example_groups]
        for eg1, eg2 in zip(all_example_groups, all_example_groups[1:]):
            if eg1 is new_example_groups[0]:
                self.move_camera(
                    phi=70 * DEGREES,
                    theta=-110 * DEGREES
                )
            self.remove(eg1)
            self.play(
                ReplacementTransform(eg1.deepcopy(), eg2),
                Transform(
                    equation,
                    self.get_equation(eg2[2])
                )
            )
            if eg1 is example_group:
                self.move_camera(
                    phi=0,
                    theta=-90 * DEGREES,
                )
            self.show_length_stretch_of_rect(eg2)
        self.play(
            ReplacementTransform(all_example_groups[-1], example_group),
            Restore(equation)
        )

    def show_length_stretch_of_rect(self, example_group):
        s_rect, proj_lines, c_rect = example_group
        rects = VGroup(s_rect, c_rect)
        line1, line2 = lines = VGroup(*[
            Line(m.get_anchors()[1], m.get_anchors()[2])
            for m in rects
        ])
        lines.set_stroke(YELLOW, 5)
        lines.set_shade_in_3d(True)
        proj_lines_to_fade = VGroup(
            proj_lines[0],
            proj_lines[3],
        )
        self.play(
            FadeIn(lines[0]),
            FadeOut(rects),
            FadeOut(proj_lines_to_fade)
        )
        for x in range(3):
            anims = []
            if lines[1] in self.mobjects:
                anims.append(FadeOut(lines[1]))
            self.play(
                TransformFromCopy(lines[0], lines[1]),
                *anims
            )
        self.play(
            FadeOut(lines),
            FadeIn(rects),
            FadeIn(proj_lines_to_fade),
        )
        self.remove(rects, proj_lines_to_fade)
        self.add(example_group)

    def show_height_scaled_down(self):
        ghost_sphere = self.ghost_sphere
        ghost_cylinder = self.ghost_cylinder
        example_group = self.example_group
        equation = self.equation
        r1, lines, r2 = example_group
        to_fade = VGroup(*[
            mob
            for mob in it.chain(ghost_sphere, ghost_cylinder)
            if np.dot(mob.get_center(), [1, 1, 0]) < 0
        ])
        to_fade.save_state()

        new_example_groups = [
            self.get_example_group([1, -1, z])
            for z in [6, 0.25]
        ]
        for eg in new_example_groups:
            eg[::2].set_stroke(YELLOW, 2)
            eg.set_stroke(width=1)
        all_example_groups = VGroup(example_group, *new_example_groups)

        self.play(
            to_fade.shift, IN,
            to_fade.fade, 1,
            remover=True
        )
        self.move_camera(
            phi=85 * DEGREES,
            theta=-135 * DEGREES,
            added_anims=[
                lines.set_stroke, {"width": 1},
                r1.set_stroke, YELLOW, 2, 1,
                r2.set_stroke, YELLOW, 2, 1,
            ]
        )
        self.show_shadow(example_group)
        for eg1, eg2 in zip(all_example_groups, all_example_groups[1:]):
            self.remove(*eg1.get_family())
            self.play(
                ReplacementTransform(eg1.deepcopy(), eg2),
                Transform(
                    equation,
                    self.get_equation(eg2[2])
                )
            )
            self.show_shadow(eg2)
        self.move_camera(
            phi=70 * DEGREES,
            theta=-115 * DEGREES,
            added_anims=[
                ReplacementTransform(
                    all_example_groups[-1],
                    example_group,
                ),
                Restore(equation),
            ]
        )
        self.begin_ambient_camera_rotation()
        self.play(Restore(to_fade))
        self.wait(5)

    def show_shadow(self, example_group):
        s_rect, lines, c_rect = example_group
        for x in range(3):
            self.play(TransformFromCopy(s_rect, c_rect))

    #
    def get_projection_lines(self, piece):
        result = VGroup()
        radius = self.sphere_config["radius"]
        for corner in piece.get_anchors()[:-1]:
            start = np.array(corner)
            end = np.array(corner)
            start[:2] = np.zeros(2)
            end[:2] = (radius + 0.03) * normalize(end[:2])
            kwargs = {
                "color": YELLOW,
                "stroke_width": 0.5,
            }
            result.add(VGroup(*[
                Line(p1, p2, **kwargs)
                for p1, p2 in [(start, corner), (corner, end)]
            ]))
        result.set_shade_in_3d(True)
        return result

    def get_equation(self, rect):
        length = get_norm(rect.get_anchors()[1] - rect.get_anchors()[0])
        height = get_norm(rect.get_anchors()[2] - rect.get_anchors()[1])
        lhs = Rectangle(width=length, height=height)
        rhs = Rectangle(width=height, height=length)
        eq_rects = VGroup(lhs, rhs)
        eq_rects.set_stroke(width=0)
        eq_rects.set_fill(YELLOW, 1)
        eq_rects.scale(2)
        equals = TexMobject("=")
        equation = VGroup(lhs, equals, rhs)
        equation.arrange(RIGHT)
        equation.to_corner(UR)

        brace = Brace(Line(ORIGIN, 0.5 * RIGHT), DOWN)
        w_brace = brace.copy().match_width(lhs, stretch=True)
        h_brace = brace.copy().rotate(-90 * DEGREES)
        h_brace.match_height(lhs, stretch=True)
        w_brace.next_to(lhs, DOWN, buff=SMALL_BUFF)
        h_brace.next_to(lhs, LEFT, buff=SMALL_BUFF)
        braces = VGroup(w_brace, h_brace)

        width_label = TextMobject("Width")
        height_label = TextMobject("Height")
        labels = VGroup(width_label, height_label)
        labels.scale(0.75)
        width_label.next_to(w_brace, DOWN, SMALL_BUFF)
        height_label.next_to(h_brace, LEFT, SMALL_BUFF)

        equation.braces = braces
        equation.labels = labels
        equation.add(braces, labels)

        return equation

    def move_fixed_in_frame_mob_to_unfixed_mob(self, m1, m2):
        phi = self.camera.phi_tracker.get_value()
        theta = self.camera.theta_tracker.get_value()
        target = m2.get_center()
        target = rotate_vector(target, -theta - 90 * DEGREES, OUT)
        target = rotate_vector(target, -phi, RIGHT)

        m1.move_to(target)
        m1.scale(0.1)
        m1.shift(SMALL_BUFF * UR)
        return m1

    def get_example_group(self, vect):
        pieces = self.pieces
        rect = pieces[np.argmax([
            np.dot(r.saved_state.get_center(), vect)
            for r in pieces
        ])].saved_state.copy()
        rect_proj_lines = self.get_projection_lines(rect)
        rect.set_fill(YELLOW, 1)
        original_rect = rect.copy()
        self.project_mobject(rect)
        rect.shift(
            0.001 * np.array([*rect.get_center()[:2], 0])
        )
        result = VGroup(original_rect, rect_proj_lines, rect)
        result.set_shade_in_3d(True)
        return result


class SlantedShadowSquishing(ShowShadows):
    CONFIG = {
        "num_reorientations": 4,
        "random_seed": 2,
    }

    def setup(self):
        ShowShadows.setup(self)
        self.surface_area_label.fade(1)
        self.shadow_area_label.fade(1)
        self.shadow_area_decimal.fade(1)

    def construct(self):
        # Show creation
        self.set_camera_orientation(
            phi=70 * DEGREES,
            theta=-150 * DEGREES,
        )
        self.begin_ambient_camera_rotation(0.01)
        square = self.obj3d.deepcopy()
        square.clear_updaters()
        shadow = always_redraw(lambda: get_shadow(square))

        # Reorient
        self.add(square, shadow)
        for n in range(self.num_reorientations):
            angle = 40 * DEGREES
            self.play(
                Rotate(square, angle, axis=RIGHT),
                run_time=2
            )

    def get_object(self):
        square = Square()
        square.set_shade_in_3d(True)
        square.set_height(2)
        square.set_stroke(WHITE, 0.5)
        square.set_fill(BLUE_C, 1)
        return square


class JustifyLengthStretch(ShowProjection):
    CONFIG = {
        "R_color": RED,
        "d_color": WHITE,
        "d_ambiguity_iterations": 4,
    }

    def construct(self):
        self.setup_shapes()
        self.add_ghosts()
        self.add_example_group()
        self.cut_cross_section()
        self.label_R()
        self.label_d()
        self.show_similar_triangles()

    def add_ghosts(self):
        self.add(self.ghost_sphere, self.ghost_cylinder)

    def add_example_group(self):
        self.pieces = self.sphere
        for piece in self.pieces:
            piece.save_state()
        self.example_group = self.get_example_group([1, 0.1, 1.5])
        self.add(self.example_group)
        self.set_camera_orientation(theta=-45 * DEGREES)

    def cut_cross_section(self):
        sphere = self.ghost_sphere
        cylinder = self.ghost_cylinder
        to_fade = VGroup(*[
            mob
            for mob in it.chain(sphere, cylinder)
            if np.dot(mob.get_center(), DOWN) > 0
        ])
        self.lost_hemisphere = to_fade
        to_fade.save_state()

        circle = Circle(
            stroke_width=2,
            stroke_color=PINK,
            radius=self.sphere.radius
        )
        circle.rotate(90 * DEGREES, RIGHT)
        self.circle = circle

        self.example_group.set_stroke(YELLOW, 1)

        self.stop_ambient_camera_rotation()
        self.play(
            Rotate(
                to_fade, -PI,
                axis=OUT,
                about_point=sphere.get_left(),
                run_time=2
            ),
            VFadeOut(to_fade, run_time=2),
            FadeIn(circle),
        )
        # self.move_camera(
        #     phi=80 * DEGREES,
        #     theta=-85 * DEGREES,
        # )

    def label_R(self):
        circle = self.circle
        R_line = Line(ORIGIN, circle.get_right())
        R_line.set_color(self.R_color)
        R_label = TexMobject("R")
        R_label.next_to(R_line, IN)

        self.add_fixed_orientation_mobjects(R_label)
        self.play(
            ShowCreation(R_line),
            FadeInFrom(R_label, IN),
        )
        self.wait()

        self.R_line = R_line
        self.R_label = R_label

    def label_d(self):
        example_group = self.example_group
        s_rect = example_group[0]
        d_line = self.get_d_line(
            s_rect.get_corner(IN + RIGHT + DOWN)
        )
        alt_d_line = self.get_d_line(
            s_rect.get_corner(OUT + LEFT + DOWN)
        )
        d_label = TexMobject("d")
        d_label.next_to(d_line, IN)

        self.add_fixed_orientation_mobjects(d_label)
        self.play(
            ShowCreation(d_line),
            FadeInFrom(d_label, IN),
        )
        self.wait()
        for x in range(self.d_ambiguity_iterations):
            to_fade_out = [d_line, alt_d_line][x % 2]
            to_fade_in = [d_line, alt_d_line][(x + 1) % 2]
            self.play(
                FadeIn(to_fade_in),
                FadeOut(to_fade_out),
                d_label.next_to, to_fade_in, IN,
            )

        self.d_line = d_line
        self.d_label = d_label

    def show_similar_triangles(self):
        d_line = self.d_line
        d_label = self.d_label
        R_line = self.R_line
        R_label = self.R_label
        example_group = self.example_group
        s_rect, proj_lines, c_rect = example_group

        p1 = s_rect.get_anchors()[1]
        p2 = s_rect.get_anchors()[2]
        p0 = np.array(p1)
        p0[:2] = np.zeros(2)
        triangle = Polygon(p0, p1, p2)
        triangle.set_stroke(width=0)
        triangle.set_fill(GREEN, opacity=1)
        base = Line(p1, p2)
        base.set_stroke(PINK, 3)

        big_triangle = Polygon(
            p0, self.project_point(p1), self.project_point(p2)
        )
        big_triangle.set_stroke(width=0)
        big_triangle.set_fill(RED, opacity=1)

        equation = VGroup(
            triangle.copy().rotate(-3 * DEGREES),
            TexMobject("\\sim"),
            big_triangle.copy().rotate(-3 * DEGREES)
        )
        equation.arrange(RIGHT, buff=SMALL_BUFF)
        equation.to_corner(UL)
        eq_d = TexMobject("d").next_to(equation[0], DOWN, SMALL_BUFF)
        eq_R = TexMobject("R").next_to(equation[2], DOWN, SMALL_BUFF)
        VGroup(equation, eq_d, eq_R).rotate(20 * DEGREES, axis=RIGHT)

        for mob in [triangle, big_triangle]:
            mob.set_shade_in_3d(True)
            mob.set_fill(opacity=0.8)

        self.move_camera(
            phi=40 * DEGREES,
            theta=-85 * DEGREES,
            added_anims=[
                d_label.next_to, d_line, DOWN, SMALL_BUFF,
                d_line.set_stroke, {"width": 1},
                FadeOut(proj_lines[0]),
                FadeOut(proj_lines[3]),
                FadeOut(R_label)
            ],
            run_time=2,
        )
        point = VectorizedPoint(p0)
        point.set_shade_in_3d(True)
        self.play(
            ReplacementTransform(point, triangle),
            Animation(self.camera.phi_tracker)
        )
        self.add_fixed_in_frame_mobjects(equation, eq_d, eq_R)
        self.play(
            FadeInFrom(equation[0], 7 * RIGHT + 2.5 * DOWN),
            FadeIn(equation[1:]),
            FadeInFromDown(eq_d),
            FadeInFromDown(eq_R),
            Animation(self.camera.phi_tracker)
        )
        self.wait()
        for x in range(2):
            self.play(ShowCreationThenDestruction(base))
        self.wait()
        d_line_copy = d_line.copy().set_stroke(WHITE, 3)
        self.play(ShowCreation(d_line_copy))
        self.play(FadeOut(d_line_copy))
        self.wait(2)
        R_label.next_to(R_line, DOWN, SMALL_BUFF)
        R_label.shift(0.25 * IN)
        self.play(
            ReplacementTransform(triangle, big_triangle),
            FadeIn(R_label),
            Animation(self.camera.phi_tracker)
        )
        self.wait(3)

        self.move_camera(
            phi=70 * DEGREES,
            theta=-70 * DEGREES,
            added_anims=[
                big_triangle.set_fill, {"opacity": 0.25},
                d_label.next_to, d_line, IN, {"buff": 0.3},
            ]
        )
        self.begin_ambient_camera_rotation()
        lost_hemisphere = self.lost_hemisphere
        lost_hemisphere.restore()
        left_point = self.sphere.get_left()
        lost_hemisphere.rotate(-PI, axis=OUT, about_point=left_point)
        self.play(
            Rotate(
                lost_hemisphere, PI,
                axis=OUT,
                about_point=left_point,
                run_time=2,
            ),
            VFadeIn(lost_hemisphere),
            FadeOut(self.circle),
            R_line.set_color, self.R_color,
        )
        self.wait(10)

    #
    def get_d_line(self, sphere_point):
        end = sphere_point
        start = np.array(end)
        start[:2] = np.zeros(2)

        d_line = Line(start, end)
        d_line.set_color(self.d_color)
        return d_line


class JustifyLengthStretchHigherRes(JustifyLengthStretch):
    CONFIG = {
        "sphere_config": {
            "resolution": (2 * 24, 2 * 48)
        },
    }


class JustifyLengthStretchHighestRes(JustifyLengthStretch):
    CONFIG = {
        "sphere_config": {
            "resolution": (4 * 24, 4 * 48)
        },
    }


class ProTipNameThings(Scene):
    CONFIG = {
        "tip_descriptor": "(Deceptively simple) problem solving tip:",
        "tip": "Start with names",
    }

    def construct(self):
        words = TextMobject(
            self.tip_descriptor,
            self.tip,
        )
        words[1].set_color(YELLOW)
        words.to_edge(UP)

        self.play(FadeIn(words[0]))
        self.wait()
        self.play(FadeInFromDown(words[1]))
        self.wait()


class WidthScaleLabel(Scene):
    def construct(self):
        text = TexMobject(
            "\\text{Width scale factor} =",
            "\\frac{R}{d}"
        )
        self.play(Write(text))
        self.wait()


class HeightSquishLabel(Scene):
    def construct(self):
        text = TexMobject(
            "\\text{Height squish factor} =",
            "\\frac{R}{d}"
        )
        self.play(Write(text))
        self.wait()


class TinierAndTinerRectangles(SphereCylinderScene):
    CONFIG = {
        "n_iterations": 5,
    }

    def construct(self):
        spheres = [
            self.get_sphere(
                resolution=(12 * (2**n), 24 * (2**n)),
                stroke_width=0,
            )
            for n in range(self.n_iterations)
        ]

        self.set_camera_to_default_position()
        self.add(self.get_axes())
        self.begin_ambient_camera_rotation()
        self.add(spheres[0])
        for s1, s2 in zip(spheres, spheres[1:]):
            self.wait()
            random.shuffle(s2.submobjects)
            for piece in s2:
                piece.save_state()
            s2.space_out_submobjects(1.2)
            s2.fade(1)
            for piece in s1:
                piece.add(VectorizedPoint(piece.get_center() / 2))
            self.play(
                LaggedStartMap(Restore, s2)
            )
            self.remove(s1)
        self.wait(5)


class LimitViewToCrossSection(JustifyLengthStretch):
    CONFIG = {
        "d_ambiguity_iterations": 0,
    }

    def construct(self):
        self.setup_shapes()
        self.add_ghosts()
        self.add_example_group()
        self.cut_cross_section()
        self.label_R()
        self.label_d()
        self.move_camera(
            phi=90 * DEGREES,
            theta=-90 * DEGREES,
        )
        self.play(
            FadeOut(self.ghost_sphere),
            FadeOut(self.ghost_cylinder),
        )


class JustifyHeightSquish(MovingCameraScene):
    CONFIG = {
        # As measured from previous scene
        "top_phi": 0.5242654422649652,
        "low_phi": 0.655081802831207,
        "radius": 2,
        "R_color": RED,
        "d_color": WHITE,
        "little_triangle_color": BLUE,
        "big_triangle_color": GREY_BROWN,
        "alpha_color": WHITE,
        "beta_color": WHITE,
    }

    def construct(self):
        self.recreate_cross_section()
        self.show_little_triangle()
        self.show_tangent_to_radius()
        self.tweak_parameter()
        self.label_angles()

    def recreate_cross_section(self):
        axes = Axes(
            axis_config={
                "unit_size": 2,
            }
        )
        circle = Circle(
            radius=self.radius,
            stroke_color=PINK,
            stroke_width=2,
        )
        R_line = self.get_R_line(90 * DEGREES)
        R_line.set_color(self.R_color)
        R_label = TexMobject("R")
        R_label.next_to(R_line, DOWN, SMALL_BUFF)
        d_lines = VGroup(*[
            self.get_d_line(phi)
            for phi in [self.low_phi, self.top_phi]
        ])
        d_line = d_lines[0]
        d_line.set_color(self.d_color)
        d_label = TexMobject("d")
        d_label.next_to(d_line, DOWN, SMALL_BUFF)

        proj_lines = VGroup(*[
            self.get_R_line(phi)
            for phi in [self.top_phi, self.low_phi]
        ])
        proj_lines.set_stroke(YELLOW, 1)

        s_rect_line, c_rect_line = [
            Line(
                *[l.get_end() for l in lines],
                stroke_color=YELLOW,
                stroke_width=2,
            )
            for lines in [d_lines, proj_lines]
        ]

        mobjects = [
            axes, circle,
            R_line, d_line,
            R_label, d_label,
            proj_lines,
            s_rect_line, c_rect_line,
        ]
        self.add(*mobjects)
        self.set_variables_as_attrs(*mobjects)

    def show_little_triangle(self):
        phi = self.low_phi
        d_phi = abs(self.low_phi - self.top_phi)
        tri_group = self.get_double_triangle_group(phi, d_phi)
        lil_tri, big_tri = tri_group
        frame = self.camera_frame
        frame.save_state()
        scale_factor = 0.1
        sw_sf = 0.2  # stroke_width scale factor
        d_sf = 0.3  # d_label scale factor

        hyp = lil_tri.hyp
        leg = lil_tri.leg2
        leg.rotate(PI)
        VGroup(hyp, leg).set_stroke(YELLOW, 1)
        hyp_word = TextMobject("Rectangle height $\\rightarrow$")
        leg_word = TextMobject("$\\leftarrow$ Projection")
        words = VGroup(hyp_word, leg_word)
        words.set_height(0.4 * lil_tri.get_height())
        words.set_background_stroke(width=0)
        hyp_word.next_to(hyp.get_center(), LEFT, buff=0.05)
        leg_word.next_to(leg, RIGHT, buff=0.02)

        stroke_width_changers = VGroup()
        for mob in self.mobjects:
            if mob in [self.d_label, frame]:
                continue
            mob.generate_target()
            mob.save_state()
            mob.target.set_stroke(
                width=sw_sf * mob.get_stroke_width()
            )
            stroke_width_changers.add(mob)

        self.play(
            frame.scale, scale_factor,
            frame.move_to, lil_tri,
            self.d_label.scale, d_sf, {"about_edge": UP},
            *map(MoveToTarget, stroke_width_changers)
        )
        self.play(DrawBorderThenFill(lil_tri, stroke_width=0.5))
        self.wait()
        self.play(
            ShowCreation(hyp),
            LaggedStartMap(
                DrawBorderThenFill, hyp_word,
                stroke_width=0.5,
                run_time=1,
            ),
        )
        self.wait()
        self.play(TransformFromCopy(hyp, leg))
        self.play(TransformFromCopy(
            hyp_word, leg_word,
            path_arc=-PI / 2,
        ))
        self.wait()
        self.play(
            frame.restore,
            self.d_label.scale, 1 / d_sf, {"about_edge": UP},
            *map(Restore, stroke_width_changers),
            run_time=3
        )

        self.set_variables_as_attrs(
            hyp_word, leg_word, tri_group
        )

    def show_tangent_to_radius(self):
        tri_group = self.tri_group
        lil_tri, big_tri = tri_group
        lil_hyp = lil_tri.hyp
        phi = self.low_phi
        circle_point = self.get_circle_point(phi)

        tangent = lil_hyp.copy()
        tangent.set_stroke(WHITE, 2)
        tangent.scale(5 / tangent.get_length())
        tangent.move_to(circle_point)

        R_line = self.R_line
        R_label = self.R_label
        d_label = self.d_label
        elbow = Elbow(angle=(-phi - PI / 2), width=0.15)
        elbow.shift(circle_point)
        elbow.set_stroke(WHITE, 1)
        self.tangent_elbow = elbow

        self.play(GrowFromPoint(tangent, circle_point))
        self.wait()
        self.play(
            Rotate(
                R_line, 90 * DEGREES - phi,
                about_point=ORIGIN,
            ),
            R_label.next_to, 0.5 * circle_point, DR, {"buff": 0},
            d_label.shift, SMALL_BUFF * UL,
        )
        self.play(ShowCreation(elbow))
        self.wait()
        self.add(big_tri, d_label, R_line, elbow)
        d_label.set_background_stroke(width=0)
        self.play(DrawBorderThenFill(big_tri))
        self.wait()

        self.set_variables_as_attrs(tangent, elbow)

    def tweak_parameter(self):
        tri_group = self.tri_group
        lil_tri = tri_group[0]
        d_label = self.d_label
        d_line = self.d_line
        R_label = self.R_label
        R_line = self.R_line
        frame = self.camera_frame

        to_fade = VGroup(
            self.proj_lines,
            self.s_rect_line, self.c_rect_line,
            self.hyp_word, self.leg_word,
            lil_tri.hyp, lil_tri.leg2,
        )
        rad_tangent = VGroup(
            R_line,
            self.tangent,
            self.elbow,
        )

        phi_tracker = ValueTracker(self.low_phi)

        self.play(
            frame.scale, 0.6,
            frame.shift, UR,
            R_label.scale, 0.6, {"about_edge": UL},
            d_label.scale, 0.6,
            {"about_point": d_label.get_top() + SMALL_BUFF * DOWN},
            *map(FadeOut, to_fade),
        )

        curr_phi = self.low_phi
        d_phi = abs(self.top_phi - self.low_phi)
        alt_phis = [
            80 * DEGREES,
            20 * DEGREES,
            50 * DEGREES,
            curr_phi
        ]
        for new_phi in alt_phis:
            self.add(tri_group, d_label)
            self.play(
                phi_tracker.set_value, new_phi,
                UpdateFromFunc(
                    tri_group,
                    lambda tg: tg.become(
                        self.get_double_triangle_group(
                            phi_tracker.get_value(),
                            d_phi
                        )
                    )
                ),
                Rotate(
                    rad_tangent,
                    -(new_phi - curr_phi),
                    about_point=ORIGIN,
                ),
                MaintainPositionRelativeTo(R_label, R_line),
                UpdateFromFunc(
                    d_line,
                    lambda dl: dl.become(
                        self.get_d_line(phi_tracker.get_value())
                    ),
                ),
                MaintainPositionRelativeTo(d_label, d_line),
                run_time=2
            )
            self.wait()
            curr_phi = new_phi
        for tri in tri_group:
            self.play(Indicate(tri))
        self.wait()
        self.play(*map(FadeIn, to_fade))
        self.remove(phi_tracker)

    def label_angles(self):
        # Getting pretty hacky here...
        tri_group = self.tri_group
        lil_tri, big_tri = tri_group
        d_label = self.d_label
        R_label = self.R_label
        frame = self.camera_frame

        alpha = self.low_phi
        beta = 90 * DEGREES - alpha
        circle_point = self.get_circle_point(alpha)
        alpha_arc = Arc(
            start_angle=90 * DEGREES,
            angle=-alpha,
            radius=0.2,
            stroke_width=2,
        )
        beta_arc = Arc(
            start_angle=PI,
            angle=beta,
            radius=0.2,
            stroke_width=2,
        )
        beta_arc.shift(circle_point)
        alpha_label = TexMobject("\\alpha")
        alpha_label.scale(0.5)
        alpha_label.set_color(self.alpha_color)
        alpha_label.next_to(alpha_arc, UP, buff=SMALL_BUFF)
        alpha_label.shift(0.05 * DR)
        beta_label = TexMobject("\\beta")
        beta_label.scale(0.5)
        beta_label.set_color(self.beta_color)
        beta_label.next_to(beta_arc, LEFT, buff=SMALL_BUFF)
        beta_label.shift(0.07 * DR)
        VGroup(alpha_label, beta_label).set_background_stroke(width=0)

        elbow = Elbow(width=0.15, angle=-90 * DEGREES)
        elbow.shift(big_tri.get_corner(UL))
        elbow.set_stroke(width=2)

        equation = TexMobject(
            "\\alpha", "+", "\\beta", "+",
            "90^\\circ", "=", "180^\\circ"
        )
        equation.scale(0.6)
        equation.next_to(frame.get_corner(UR), DL)

        movers = VGroup(
            alpha_label.deepcopy(), beta_label.deepcopy(),
            elbow.copy()
        )
        indices = [0, 2, 4]
        for mover, index in zip(movers, indices):
            mover.target = VGroup(equation[index])

        # Show equation
        self.play(
            FadeOut(d_label),
            FadeOut(R_label),
            ShowCreation(alpha_arc),
            ShowCreation(beta_arc),
        )
        self.wait()
        self.play(FadeInFrom(alpha_label, UP))
        self.wait()
        self.play(FadeInFrom(beta_label, LEFT))
        self.wait()
        self.play(ShowCreation(elbow))
        self.wait()

        self.play(
            LaggedStartMap(MoveToTarget, movers),
            LaggedStartMap(FadeInFromDown, equation[1:4:2])
        )
        self.wait()
        self.play(FadeInFrom(equation[-2:], LEFT))
        self.remove(equation, movers)
        self.add(equation)
        self.wait()

        # Zoom in
        self.remove(self.tangent_elbow)
        stroke_width_changers = VGroup(*[
            mob for mob in self.mobjects
            if mob not in [
                beta_arc, beta_label, frame, equation,
            ]
        ])
        for mob in stroke_width_changers:
            mob.generate_target()
            mob.save_state()
            mob.target.set_stroke(
                width=0.3 * mob.get_stroke_width()
            )
        equation.set_background_stroke(width=0)
        scaled_arcs = VGroup(beta_arc, self.tangent_elbow)
        beta_label.set_background_stroke(color=BLACK, width=0.3)
        self.play(
            ApplyMethod(
                VGroup(frame, equation).scale, 0.15,
                {"about_point": circle_point + 0.1 * LEFT},
            ),
            ApplyMethod(
                beta_label.scale, 0.3,
                {"about_point": circle_point},
            ),
            scaled_arcs.set_stroke, {"width": 0.3},
            scaled_arcs.scale, 0.3, {"about_point": circle_point},
            *map(MoveToTarget, stroke_width_changers)
        )

        # Show small triangle angles
        TexMobject.CONFIG["background_stroke_width"] = 0
        words = VGroup(self.hyp_word, self.leg_word)
        alpha_arc1 = Arc(
            start_angle=90 * DEGREES + beta,
            angle=0.95 * alpha,
            radius=0.3 * 0.2,
            stroke_width=beta_arc.get_stroke_width(),
        ).shift(circle_point)
        alpha_arc2 = Arc(
            start_angle=0,
            angle=-0.95 * alpha,
            radius=0.3 * 0.2,
            stroke_width=beta_arc.get_stroke_width(),
        ).shift(lil_tri.hyp.get_end())
        beta_arc1 = Arc(
            start_angle=90 * DEGREES,
            angle=beta,
            radius=0.3 * 0.2,
            stroke_width=beta_arc.get_stroke_width(),
        ).shift(circle_point)
        deg90 = TexMobject("90^\\circ")
        deg90.set_height(0.8 * beta_label.get_height())
        deg90.next_to(self.tangent_elbow, DOWN, buff=0.025)
        # deg90.set_background_stroke(width=0)
        q_mark = TexMobject("?")
        q_mark.set_height(0.5 * beta_label.get_height())
        q_mark.next_to(alpha_arc1, LEFT, buff=0.025)
        q_mark.shift(0.01 * UP)
        alpha_label1 = TexMobject("\\alpha")
        alpha_label1.set_height(0.7 * q_mark.get_height())
        alpha_label1.move_to(q_mark)

        alpha_label2 = alpha_label1.copy()
        alpha_label2.next_to(
            alpha_arc2, RIGHT, buff=0.01
        )
        alpha_label2.set_background_stroke(color=BLACK, width=0.3)

        beta_label1 = beta_label.copy()
        beta_label1.scale(0.7)
        beta_label1.set_background_stroke(color=BLACK, width=0.3)
        beta_label1.next_to(
            beta_arc1, UP, buff=0.01
        )
        beta_label1.shift(0.01 * LEFT)

        self.play(FadeOut(words))
        self.play(FadeInFrom(deg90, 0.1 * UP))
        self.wait(0.25)
        self.play(WiggleOutThenIn(beta_label))
        self.wait(0.25)
        self.play(
            ShowCreation(alpha_arc1),
            FadeInFrom(q_mark, 0.1 * RIGHT)
        )
        self.wait()
        self.play(ShowPassingFlash(
            self.tangent.copy().scale(0.1).set_stroke(PINK, 0.5)
        ))
        self.wait()
        self.play(ReplacementTransform(q_mark, alpha_label1))
        self.play(ShowCreationThenFadeAround(
            equation,
            surrounding_rectangle_config={
                "buff": 0.015,
                "stroke_width": 0.5,
            },
        ))
        self.wait()
        self.play(
            ShowCreation(alpha_arc2),
            FadeIn(alpha_label2),
        )
        self.play(
            ShowCreation(beta_arc1),
            FadeIn(beta_label1),
        )
        self.wait()

    #
    def get_double_triangle_group(self, phi, d_phi):
        p0 = self.get_circle_point(phi)
        p1 = self.get_circle_point(phi - d_phi)
        p2 = np.array(p1)
        p2[0] = p0[0]

        little_triangle = Polygon(
            p0, p1, p2,
            stroke_width=0,
            fill_color=self.little_triangle_color,
            fill_opacity=1,
        )
        big_triangle = Polygon(
            p0, ORIGIN, p0 - p0[0] * RIGHT,
            stroke_width=0,
            fill_color=self.big_triangle_color,
            fill_opacity=1
        )
        result = VGroup(little_triangle, big_triangle)
        for tri in result:
            p0, p1, p2 = tri.get_anchors()[:3]
            tri.hyp = Line(p0, p1)
            tri.leg1 = Line(p1, p2)
            tri.leg2 = Line(p2, p0)
            tri.side_lines = VGroup(
                tri.hyp, tri.leg1, tri.leg2
            )
            tri.side_lines.set_stroke(WHITE, 1)
        result.set_stroke(width=0)
        return result

    def get_R_line(self, phi):
        y = self.radius * np.cos(phi)
        x = self.radius
        return Line(ORIGIN, x * RIGHT).shift(y * UP)

    def get_d_line(self, phi):
        end = self.get_circle_point(phi)
        start = np.array(end)
        start[0] = 0
        return Line(start, end)

    def get_circle_point(self, phi):
        return rotate_vector(self.radius * UP, -phi)


class ProTipTangentRadii(ProTipNameThings):
    CONFIG = {
        "tip_descriptor": "Pro tip:",
        "tip": "A circle's tangent is perpendicular to its radius",
    }


class ProTipTweakParameters(ProTipNameThings):
    CONFIG = {
        "tip_descriptor": "Pro tip:",
        "tip": "Tweak parameters $\\rightarrow$ make",
    }


class DrawSquareThenFade(Scene):
    def construct(self):
        square = Square(color=YELLOW, stroke_width=5)
        self.play(ShowCreation(square))
        self.play(FadeOut(square))


class WhyAreWeDoingThis(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Hang on, what \\\\ are we doing?",
            student_index=2,
            bubble_kwargs={"direction": LEFT},
            target_mode="hesitant"
        )
        self.change_student_modes(
            "maybe", "pondering", "hesitant",
            added_anims=[self.teacher.change, "tease"]
        )
        self.wait(3)
        self.play(
            RemovePiCreatureBubble(self.students[2]),
            self.teacher.change, "raise_right_hand",
            self.change_student_modes(*2 * ["pondering"])
        )
        self.look_at(self.screen)
        self.wait(2)


class SameEffectAsRotating(Scene):
    CONFIG = {
        "rectangle_config": {
            "height": 2,
            "width": 1,
            "stroke_width": 0,
            "fill_color": YELLOW,
            "fill_opacity": 1,
            "background_stroke_width": 2,
            "background_stroke_color": BLACK,
        },
        "x_stretch": 2,
        "y_stretch": 0.5,
    }

    def construct(self):
        rect1 = Rectangle(**self.rectangle_config)
        rect2 = rect1.copy()
        rect2.stretch(self.x_stretch, 0)
        rect2.stretch(self.y_stretch, 1)
        rotated_rect1 = rect1.copy()
        rotated_rect1.rotate(-90 * DEGREES)

        arrow = Arrow(ORIGIN, RIGHT, buff=0, color=WHITE)
        group = VGroup(rect1, arrow, rect2)
        group.arrange(RIGHT)
        group.center()
        moving_rect = rect1.copy()

        low_brace = always_redraw(
            lambda: Brace(
                moving_rect, DOWN, buff=SMALL_BUFF,
                min_num_quads=2,
            )
        )
        right_brace = always_redraw(
            lambda: Brace(
                moving_rect, RIGHT, buff=SMALL_BUFF,
                min_num_quads=2,
            )
        )
        times_R_over_d = TexMobject("\\times \\frac{R}{d}")
        times_d_over_R = TexMobject("\\times \\frac{d}{R}")
        times_R_over_d.add_updater(
            lambda m: m.next_to(low_brace, DOWN, SMALL_BUFF)
        )
        times_d_over_R.add_updater(
            lambda m: m.next_to(right_brace, RIGHT, SMALL_BUFF)
        )

        self.add(rect1, arrow)
        self.play(moving_rect.move_to, rect2)
        self.add(low_brace)
        self.play(
            moving_rect.match_width, rect2, {"stretch": True},
            FadeIn(times_R_over_d),
        )
        self.add(right_brace)
        self.play(
            moving_rect.match_height, rect2, {"stretch": True},
            FadeIn(times_d_over_R),
        )
        self.wait()
        rotated_rect1.move_to(moving_rect)
        self.play(TransformFromCopy(
            rect1, rotated_rect1,
            path_arc=-90 * DEGREES,
            run_time=2
        ))


class NotSameEffectAsRotating(SameEffectAsRotating):
    CONFIG = {
        "rectangle_config": {
            "width": 1.5,
            "height": 1.5,
        }
    }


class ShowParameterization(Scene):
    def construct(self):
        u_color = PINK
        v_color = GREEN
        tex_kwargs = {
            "tex_to_color_map": {
                "u": u_color,
                "v": v_color,
            }
        }
        vector = Matrix(
            [
                ["\\text{cos}(u)\\text{sin}(v)"],
                ["\\text{sin}(u)\\text{sin}(v)"],
                ["\\text{cos}(v)"]
            ],
            element_to_mobject_config=tex_kwargs,
            element_alignment_corner=DOWN,
        )
        vector.to_edge(UP)

        ranges = VGroup(
            TexMobject("0 \\le u \\le 2\\pi", **tex_kwargs),
            TexMobject("0 \\le v \\le \\pi", **tex_kwargs),
            TextMobject(
                "Sample $u$ and $v$ with \\\\ the same density",
                tex_to_color_map={
                    "$u$": u_color,
                    "$v$": v_color,
                }
            )
        )
        ranges.arrange(DOWN)
        ranges.next_to(vector, DOWN)

        self.add(vector)
        self.add(ranges)


class RdLabels(Scene):
    def construct(self):
        rect = Rectangle(height=1, width=0.5)
        cR = TexMobject("cR")
        cR.next_to(rect, LEFT, SMALL_BUFF)
        cd = TexMobject("cd")
        cd.next_to(rect, DOWN, SMALL_BUFF)

        labels = VGroup(cd, cR)
        for label in labels:
            label[1].set_color(BLUE)
            self.play(FadeInFromDown(label))


class RotateAllPiecesWithExpansion(ShowProjection):
    CONFIG = {
        "sphere_config": {
            "radius": 1.5,
        },
        "with_expansion": True
    }

    def construct(self):
        self.setup_shapes()
        self.rotate_all_pieces()

    def rotate_all_pieces(self):
        sphere = self.sphere
        cylinder = self.cylinder
        ghost_sphere = self.ghost_sphere
        ghost_sphere.scale(0.99)

        # Shuffle sphere and cylinder same way
        random.seed(0)
        random.shuffle(sphere.submobjects)
        random.seed(0)
        random.shuffle(cylinder.submobjects)

        sphere_target = VGroup()
        for piece in sphere:
            p0, p1, p2, p3 = piece.get_anchors()[:4]
            piece.set_points_as_corners([
                p3, p0, p1, p2, p3
            ])
            piece.generate_target()
            sphere_target.add(piece.target)
            piece.target.move_to(
                (1 + random.random()) * piece.get_center()
            )

        self.add(ghost_sphere, sphere)
        self.wait()
        if self.with_expansion:
            self.play(LaggedStartMap(
                MoveToTarget, sphere
            ))
        self.wait()
        self.play(*[
            Rotate(piece, 90 * DEGREES, axis=piece.get_center())
            for piece in sphere
        ])
        self.wait()
        self.play(Transform(sphere, cylinder, run_time=2))
        self.wait(5)


class RotateAllPiecesWithoutExpansion(RotateAllPiecesWithExpansion):
    CONFIG = {
        "with_expansion": False,
    }


class ThinkingCritically(PiCreatureScene):
    def construct(self):
        randy = self.pi_creature

        self.play(randy.change, "pondering")
        self.wait()
        self.play(
            randy.change, "hesitant", 2 * UP,
        )
        self.wait()
        self.play(randy.change, "sassy")
        self.wait()
        self.play(randy.change, "angry")
        self.wait(4)


class WriteNotEquals(Scene):
    def construct(self):
        symbol = TexMobject("\\ne")
        symbol.scale(2)
        symbol.set_background_stroke(width=0)
        self.play(Write(symbol))
        self.wait()


class RectangulatedSphere(SphereCylinderScene):
    CONFIG = {
        "sphere_config": {
            "resolution": (10, 20)
        },
        "uniform_color": False,
        "wait_time": 10,
    }

    def construct(self):
        sphere = self.get_sphere()
        if self.uniform_color:
            sphere.set_stroke(BLUE_E, width=0.5)
            sphere.set_fill(BLUE_E)
        self.set_camera_to_default_position()
        self.begin_ambient_camera_rotation(0.05)
        self.add(sphere)
        self.wait(self.wait_time)


class SmoothSphere(RectangulatedSphere):
    CONFIG = {
        "sphere_config": {
            "resolution": (200, 400),
        },
        "uniform_color": True,
        "wait_time": 0,
    }


class SequenceOfSpheres(SphereCylinderScene):
    def construct(self):
        n_shapes = 4
        spheres, cylinders = groups = VGroup(*[
            VGroup(*[
                func(resolution=(n, 2 * n))
                for k in range(1, n_shapes + 1)
                for n in [3 * (2**k)]
            ])
            for func in [self.get_sphere, self.get_cylinder]
        ])
        groups.scale(0.5)
        for group in groups:
            for shape in group:
                for piece in shape:
                    piece.make_jagged()
                shape.set_stroke(width=0)

        for group in groups:
            group.add(self.get_oriented_tex("?").scale(2))
            group.arrange(RIGHT, buff=LARGE_BUFF)
        groups.arrange(IN, buff=1.5)

        all_equals = VGroup()
        for sphere, cylinder in zip(spheres, cylinders):
            equals = self.get_oriented_tex("=")
            equals.scale(1.5)
            equals.rotate(90 * DEGREES, UP)
            equals.move_to(interpolate(
                sphere.get_nadir(), cylinder.get_zenith(), 0.5
            ))
            all_equals.add(equals)
        all_equals.remove(all_equals[-1])

        arrow_groups = VGroup()
        for group in groups:
            arrow_group = VGroup()
            for m1, m2 in zip(group, group[1:]):
                arrow = self.get_oriented_tex("\\rightarrow")
                arrow.move_to(interpolate(
                    m1.get_right(), m2.get_left(), 0.5
                ))
                arrow_group.add(arrow)
            arrow_groups.add(arrow_group)

        q_marks = VGroup(*[
            group[-1]
            for group in groups
        ])
        final_arrows = VGroup(
            arrow_groups[0][-1],
            arrow_groups[1][-1],
        )
        for arrow in final_arrows:
            dots = self.get_oriented_tex("\\dots")
            dots.next_to(arrow, RIGHT, SMALL_BUFF)
            arrow.add(dots)
        q_marks.shift(MED_LARGE_BUFF * RIGHT)
        tilted_final_arrows = VGroup(
            final_arrows[0].copy().rotate(
                -45 * DEGREES, axis=DOWN
            ).shift(0.75 * IN),
            final_arrows[1].copy().rotate(
                45 * DEGREES, axis=DOWN
            ).shift(0.75 * OUT),
        )
        final_q_mark = q_marks[0].copy()
        final_q_mark.move_to(q_marks)

        self.set_camera_orientation(
            phi=80 * DEGREES,
            theta=-90 * DEGREES,
        )

        for i in range(n_shapes):
            anims = [
                FadeInFrom(spheres[i], LEFT),
                FadeInFrom(cylinders[i], LEFT),
            ]
            if i > 0:
                anims += [
                    Write(arrow_group[i - 1])
                    for arrow_group in arrow_groups
                ]
            self.play(*anims, run_time=1)
            self.play(GrowFromCenter(all_equals[i]))
        self.play(
            FadeInFrom(q_marks, LEFT),
            Write(final_arrows)
        )
        self.wait()
        self.play(
            Transform(final_arrows, tilted_final_arrows),
            Transform(q_marks, VGroup(final_q_mark)),
        )
        self.wait()

    def get_oriented_tex(self, tex):
        result = TexMobject(tex)
        result.rotate(90 * DEGREES, RIGHT)
        return result


class WhatIsSurfaceArea(SpecialThreeDScene):
    CONFIG = {
        "change_power": True,
    }

    def construct(self):
        title = TextMobject("What is surface area?")
        title.scale(1.5)
        title.to_edge(UP)
        title.shift(0.035 * RIGHT)
        self.add_fixed_in_frame_mobjects(title)

        power_tracker = ValueTracker(1)
        surface = always_redraw(
            lambda: self.get_surface(
                radius=3,
                amplitude=1,
                power=power_tracker.get_value()
            )
        )

        pieces = surface.copy()
        pieces.clear_updaters()
        random.shuffle(pieces.submobjects)

        self.set_camera_to_default_position()
        self.begin_ambient_camera_rotation()
        # self.add(self.get_axes())
        self.play(LaggedStartMap(
            DrawBorderThenFill, pieces,
            lag_ratio=0.2,
        ))
        self.remove(pieces)
        self.add(surface)
        if self.change_power:
            self.play(
                power_tracker.set_value, 5,
                run_time=2
            )
            self.play(
                power_tracker.set_value, 1,
                run_time=2
            )
        self.wait(2)

    def get_surface(self, radius, amplitude, power):
        def alt_pow(x, y):
            return np.sign(x) * (np.abs(x) ** y)
        return ParametricSurface(
            lambda u, v: radius * np.array([
                v * np.cos(TAU * u),
                v * np.sin(TAU * u),
                0,
            ]) + amplitude * np.array([
                0,
                0,
                (v**2) * alt_pow(np.sin(5 * TAU * u), power),
            ]),
            resolution=(100, 20),
            v_min=0.01
        )


class AltWhatIsSurfaceArea(WhatIsSurfaceArea):
    CONFIG = {
        "change_power": False,
    }

    def get_surface(self, radius, amplitude, power):
        return ParametricSurface(
            lambda u, v: radius * (1 - 0.8 * (v**2) ** power) * np.array([
                np.cos(TAU * u) * (1 + 0.5 * v * np.sin(5 * TAU * u)),
                np.sin(TAU * u) * (1 + 0.5 * v * np.sin(5 * TAU * u)),
                v,
            ]),
            v_min=-1,
            v_max=1,
            resolution=(100, 25),
        )


class EoCWrapper(Scene):
    def construct(self):
        title = TextMobject("Essence of calculus")
        title.scale(1.5)
        title.to_edge(UP)
        rect = ScreenRectangle(height=6)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait()


class RoleOfCalculus(SpecialThreeDScene):
    CONFIG = {
        "camera_config": {
            "light_source_start_point": [-4, 5, 7],
        }
    }

    def construct(self):
        calc = TexMobject("\\int", "\\int")
        calc.space_out_submobjects(0.4)
        calc.scale(2)
        arrow = Vector(2 * RIGHT, color=WHITE)
        sphere = self.get_sphere()
        sphere.rotate(70 * DEGREES, axis=LEFT)

        group = VGroup(calc, arrow, sphere)
        group.arrange(RIGHT)
        group.shift(0.5 * RIGHT)
        cross = Cross(group[:2], stroke_width=10)

        # arrow2 = arrow.copy()

        self.add(calc, arrow)
        self.play(Write(sphere))
        self.wait()
        self.play(ShowCreation(cross))
        self.wait()
        self.play(
            sphere.next_to, ORIGIN, LEFT, 1.0,
            arrow.move_to, ORIGIN, LEFT,
            calc.next_to, ORIGIN, RIGHT, 2.25,
            FadeOut(cross),
            path_arc=PI,
            run_time=2,
        )
        self.wait()


class UnwrappedCircleLogic(UnfoldCircles):
    CONFIG = {
        "radius": 1.25,
        "dr": 0.01,
    }

    def construct(self):
        radius = self.radius
        dr = self.dr

        TexMobject.CONFIG["background_stroke_width"] = 2
        unwrap_factor_tracker = ValueTracker(0)
        center_tracker = VectorizedPoint()
        highligt_prop_tracker = ValueTracker(0.5)

        def get_highlight_prop():
            return highligt_prop_tracker.get_value()

        def get_r():
            return radius * get_highlight_prop()

        center_tracker.move_to(4.5 * LEFT)

        def get_unwrapped_circle():
            result = self.get_unwrapped_circle(
                radius=radius, dr=dr,
                unwrap_factor=unwrap_factor_tracker.get_value(),
                center=center_tracker.get_center()
            )
            self.get_submob_from_prop(
                result, get_highlight_prop()
            ).set_stroke(YELLOW, 2)
            return result

        unwrapped_circle = always_redraw(get_unwrapped_circle)
        circle = unwrapped_circle.copy()
        circle.clear_updaters()
        R_line = Line(circle.get_center(), circle.get_bottom())
        R_line.set_stroke(WHITE, 2)
        R_label = TexMobject("R")
        R_label.next_to(R_line, LEFT)
        circle_group = VGroup(circle, R_line, R_label)

        tri_R_line = always_redraw(
            lambda: Line(
                ORIGIN, radius * DOWN
            ).shift(center_tracker.get_center())
        )

        # Unwrap
        self.play(FadeInFromDown(circle_group))
        self.add(circle_group, unwrapped_circle, tri_R_line, R_label)
        circle_group.set_stroke(opacity=0.5)
        self.play(
            unwrap_factor_tracker.set_value, 1,
            run_time=2
        )
        self.play(
            center_tracker.move_to,
            circle.get_right() + (radius + MED_SMALL_BUFF) * RIGHT,
            circle_group.set_stroke, {"opacity": 1},
        )
        self.wait()

        # Change radius
        r_line = always_redraw(
            lambda: Line(
                ORIGIN, get_r() * DOWN,
                stroke_width=2,
                stroke_color=WHITE,
            ).shift(circle.get_center())
        )
        r_label = TexMobject("r")
        r_label.add_updater(
            lambda m: m.next_to(r_line, LEFT, SMALL_BUFF)
        )
        two_pi_r_label = TexMobject("2\\pi r")
        two_pi_r_label.add_updater(
            lambda m: m.next_to(
                self.get_submob_from_prop(
                    unwrapped_circle,
                    get_highlight_prop(),
                ), DOWN, SMALL_BUFF
            )
        )

        circle.add_updater(
            lambda m: m.match_style(unwrapped_circle)
        )

        self.play(
            ReplacementTransform(R_line, r_line),
            ReplacementTransform(R_label, r_label),
            FadeInFromDown(
                two_pi_r_label.copy().clear_updaters(),
                remover=True
            )
        )
        self.add(two_pi_r_label)
        for prop in [0.2, 0.8, 0.5]:
            self.play(
                highligt_prop_tracker.set_value, prop,
                run_time=2
            )

        # Show line
        line = Line(*[
            unwrapped_circle.get_corner(vect)
            for vect in (UL, DR)
        ])
        line.set_color(PINK)
        line.set_fill(BLACK, 1)
        line_word = TextMobject("Line")
        line_word.next_to(ORIGIN, UP, SMALL_BUFF)
        line_word.rotate(line.get_angle(), about_point=ORIGIN)
        line_word.shift(line.get_center())

        curve = line.copy()
        curve.points[1] = unwrapped_circle.get_corner(DL)
        not_line = TextMobject("Not line")
        not_line.rotate(line.get_angle() / 2)
        not_line.move_to(line_word)
        not_line.shift(0.3 * DOWN)

        self.play(
            ShowCreation(line),
            Write(line_word),
        )
        self.wait()
        self.play(highligt_prop_tracker.set_value, 1)
        self.wait()

        # Bend
        line.save_state()
        line_word.save_state()
        self.play(
            Transform(line, curve),
            Transform(line_word, not_line),
        )
        self.wait()
        self.play(
            Restore(line),
            Restore(line_word),
            # FadeIn(two_pi_r_label),
        )
        self.wait()

    def get_submob_from_prop(self, mob, prop):
        n = len(mob.submobjects)
        return mob[min(int(prop * n), n - 1)]


class AskAboutDirectConnection(TeacherStudentsScene, SpecialThreeDScene):
    CONFIG = {
        "camera_config": {
            "light_source_start_point": [-4, 5, 7],
        }
    }

    def construct(self):
        sphere = Sphere()
        cylinder = Cylinder()
        for mob in sphere, cylinder:
            mob.rotate(70 * DEGREES, LEFT)
        formula = TexMobject("4\\pi R^2")
        formula.set_color(BLUE)
        circle = Circle()
        circle.set_stroke(width=0)
        circle.set_fill(GREY_BROWN, 1)
        area_label = TexMobject("\\pi R^2", background_stroke_width=0)
        area_label.scale(1.5)
        circle.add(area_label)
        group = VGroup(
            sphere, cylinder, formula, circle
        )
        for mob in group:
            mob.set_height(1.5)
        formula.scale(0.5)
        group.arrange(RIGHT, buff=1.5)
        group.to_edge(UP, buff=2)
        group[1:3].to_edge(UP)

        arrows = VGroup()
        for m1, m2 in zip(group, group[1:]):
            arrow = Arrow(
                m1.get_center(), m2.get_center(),
                buff=1,
                color=WHITE
            )
            arrows.add(arrow)
        direct_arrow = Arrow(
            sphere, circle, color=WHITE
        )
        q_marks = TexMobject(*"???")
        q_marks.space_out_submobjects(1.5)
        q_marks.scale(1.5)
        q_marks.next_to(direct_arrow, DOWN)

        self.play(
            self.teacher.change, "raise_right_hand",
            self.get_student_changes(
                *3 * ["pondering"],
                look_at_arg=group,
            ),
            LaggedStartMap(FadeInFromDown, group),
            LaggedStartMap(GrowArrow, arrows)
        )
        self.wait()
        self.play(
            self.teacher.change, "pondering",
            self.students[2].change, "raise_right_hand",
            GrowArrow(direct_arrow),
            LaggedStartMap(
                FadeInFrom, q_marks,
                lambda m: (m, UP),
                lag_ratio=0.8,
                run_time=1.5,
            )
        )
        self.change_student_modes(
            "erm", "sassy", "raise_right_hand",
        )
        self.wait(2)
        self.look_at(group)
        self.wait(2)


class ExercisesGiveLearning(MovingCameraScene):
    def construct(self):
        bulb = Lightbulb()
        arrow1 = Arrow(ORIGIN, RIGHT, buff=0)
        lectures = TextMobject("Lectures")
        exercises = TextMobject("Exercises")
        frame = self.camera_frame
        frame.scale(0.7)

        bulb.next_to(arrow1, RIGHT)
        for word in lectures, exercises:
            word.next_to(arrow1, LEFT)

        cross = Cross(lectures)

        # Knock down lectures
        self.add(lectures)
        self.play(GrowArrow(arrow1))
        self.play(LaggedStartMap(DrawBorderThenFill, bulb))
        self.play(ShowCreation(cross))
        self.play(
            VGroup(lectures, cross).shift, DOWN,
            FadeInFrom(exercises, UP)
        )
        self.wait()

        # Show self
        arrow2 = arrow1.copy()
        arrow2.next_to(lectures, LEFT)
        logo = Logo()
        logo.set_height(1)
        logo.next_to(arrow2, LEFT)
        pupil_copy = logo.pupil.copy()

        self.add(logo, pupil_copy)
        self.play(
            frame.shift, 1.5 * LEFT,
            Write(logo, run_time=1.5)
        )
        self.remove(pupil_copy)
        self.play(
            GrowArrow(arrow2),
            FadeOut(cross)
        )
        self.wait()
        self.play(
            VGroup(logo, arrow2).next_to,
            exercises, LEFT
        )
        self.wait()


class NobodyLikesHomework(TeacherStudentsScene):
    def construct(self):
        self.change_student_modes(
            "angry", "pleading", "angry",
            added_anims=[self.teacher.change, "guilty"]
        )
        self.wait()
        self.change_all_student_modes(
            "tired", look_at_arg=8 * RIGHT + 4 * DOWN,
            added_anims=[self.teacher.change, "tease"]
        )
        self.wait(2)


class ChallengeMode(Scene):
    def construct(self):
        words = TextMobject("Challenge mode: Predict the proof")
        words.scale(1.5)
        words.to_edge(UP)
        self.play(Write(words))
        self.wait()


class SecondProof(SpecialThreeDScene):
    CONFIG = {
        "sphere_config": {
            "resolution": (30, 30),
        },
        "n_random_subsets": 12,
    }

    def construct(self):
        self.setup_shapes()
        self.divide_into_rings()
        self.show_shadows()
        self.correspond_to_every_other_ring()
        self.cut_cross_section()
        self.show_theta()
        self.enumerate_rings()
        self.ask_about_ring_circumference()
        self.ask_about_shadow_area()
        self.ask_about_2_to_1_correspondance()
        self.show_all_shadow_rings()
        self.ask_about_global_correspondance()

    def setup_shapes(self):
        sphere = self.get_sphere()
        sphere.set_stroke(WHITE, width=0.25)
        self.add(sphere)
        self.sphere = sphere

        u_values, v_values = sphere.get_u_values_and_v_values()
        rings = VGroup(*[VGroup() for u in u_values])
        for piece in sphere:
            rings[piece.u_index].add(piece.copy())
        self.set_ring_colors(rings)
        self.rings = rings

        self.axes = self.get_axes()
        self.add(self.axes)

        self.set_camera_to_default_position()
        self.begin_ambient_camera_rotation()

    def divide_into_rings(self):
        rings = self.rings

        self.play(FadeIn(rings), FadeOut(self.sphere))
        self.play(
            rings.space_out_submobjects, 1.5,
            rate_func=there_and_back_with_pause,
            run_time=3
        )
        self.wait(2)
        rings.save_state()

    def show_shadows(self):
        rings = self.rings
        north_rings = rings[:len(rings) // 2]
        ghost_rings = rings.copy()
        ghost_rings.set_fill(opacity=0.0)
        ghost_rings.set_stroke(WHITE, width=0.5, opacity=0.2)

        north_rings.submobjects.reverse()
        shadows = self.get_shadow(north_rings)
        for piece in shadows.family_members_with_points():
            piece.set_stroke(
                piece.get_fill_color(),
                width=0.5,
            )
        for shadow in shadows:
            shadow.save_state()
        shadows.become(north_rings)

        self.add(ghost_rings)
        self.play(FadeOut(rings), Animation(shadows))
        self.play(LaggedStartMap(Restore, shadows))
        self.wait()
        self.move_camera(phi=40 * DEGREES)
        self.wait(3)

        # Show circle
        radius = self.sphere_config["radius"]
        radial_line = Line(ORIGIN, radius * RIGHT)
        radial_line.set_stroke(RED)
        R_label = TexMobject("R")
        R_label.set_background_stroke(width=1)
        R_label.next_to(radial_line, DOWN)

        self.play(
            FadeInFromDown(R_label),
            ShowCreation(radial_line)
        )
        self.play(Rotating(
            radial_line, angle=TAU,
            about_point=ORIGIN,
            rate_func=smooth,
            run_time=3,
        ))
        self.wait()

        self.set_variables_as_attrs(
            shadows, ghost_rings,
            radial_line, R_label
        )

    def correspond_to_every_other_ring(self):
        rings = self.rings
        shadows = self.shadows
        shadows.submobjects.reverse()

        rings.restore()
        self.set_ring_colors(rings)
        every_other_ring = rings[1::2]
        self.move_camera(
            phi=70 * DEGREES,
            theta=-135 * DEGREES,
            added_anims=[
                FadeOut(self.R_label),
                FadeOut(self.radial_line),
            ],
            run_time=2,
        )
        shadows_copy = shadows.copy()
        shadows.fade(1)
        self.play(
            ReplacementTransform(
                shadows_copy, every_other_ring
            ),
            FadeOut(self.ghost_rings),
            run_time=2,
        )
        self.wait(5)

        self.every_other_ring = every_other_ring

    def cut_cross_section(self):
        shadows = self.shadows
        every_other_ring = self.every_other_ring
        rings = self.rings

        back_half = self.get_hemisphere(rings, UP)
        front_half = self.get_hemisphere(rings, DOWN)
        front_half_ghost = front_half.copy()
        front_half_ghost.set_fill(opacity=0.2)
        front_half_ghost.set_stroke(opacity=0)

        # shaded_back_half = back_half.copy()
        # for piece in shaded_back_half.family_members_with_points():
        #     piece.points = piece.points[::-1]
        # shaded_back_half.scale(0.999)
        # shaded_back_half.set_fill(opacity=0.5)

        radius = self.sphere_config["radius"]
        circle = Circle(radius=radius)
        circle.set_stroke(PINK, 2)
        circle.rotate(90 * DEGREES, RIGHT)

        every_other_ring_copy = every_other_ring.copy()
        self.add(every_other_ring_copy)
        self.remove(every_other_ring)
        rings.set_fill(opacity=0.8)
        rings.set_stroke(opacity=0.6)
        self.play(
            FadeIn(back_half),
            FadeIn(front_half_ghost),
            FadeIn(circle),
            FadeOut(shadows),
            FadeOut(every_other_ring_copy),
        )
        self.wait()

        self.set_variables_as_attrs(
            back_half, front_half,
            front_half_ghost,
            slice_circle=circle
        )

    def show_theta(self):
        theta_tracker = ValueTracker(0)
        get_theta = theta_tracker.get_value
        theta_group = always_redraw(
            lambda: self.get_theta_group(get_theta())
        )
        theta_mob_opacity_tracker = ValueTracker(0)
        get_theta_mob_opacity = theta_mob_opacity_tracker.get_value
        theta_mob = theta_group[-1]
        theta_mob.add_updater(
            lambda m: m.set_fill(opacity=get_theta_mob_opacity())
        )
        theta_mob.add_updater(
            lambda m: m.set_background_stroke(
                width=get_theta_mob_opacity()
            )
        )

        lit_ring = always_redraw(
            lambda: self.get_ring_from_theta(
                self.rings, get_theta()
            ).copy().set_color(YELLOW)
        )

        self.stop_ambient_camera_rotation()
        self.move_camera(theta=-60 * DEGREES)

        self.add(theta_group, lit_ring)
        n_rings = len(self.rings) - 1
        lit_ring_index = int((30 / 180) * n_rings)
        angle = PI * lit_ring_index / n_rings
        for alpha in [angle, 0, PI, angle]:
            self.play(
                theta_tracker.set_value, alpha,
                theta_mob_opacity_tracker.set_value, 1,
                Animation(self.camera.phi_tracker),
                run_time=2,
            )
            self.wait()

        # Label d-theta
        radius = self.sphere_config["radius"]
        d_theta = PI / len(self.rings)
        alt_theta = get_theta() + d_theta
        alt_theta_group = self.get_theta_group(alt_theta)
        alt_R_line = alt_theta_group[1]
        # d_theta_arc = Arc(
        #     start_angle=get_theta(),
        #     angle=d_theta,
        #     radius=theta_group[0].radius,
        #     stroke_color=PINK,
        #     stroke_width=3,
        # )
        # d_theta_arc.rotate(90 * DEGREES, axis=RIGHT, about_point=ORIGIN)
        brace = Brace(Line(ORIGIN, radius * d_theta * RIGHT), UP)
        brace.rotate(90 * DEGREES, RIGHT)
        brace.next_to(self.sphere, OUT, buff=0)
        brace.add_to_back(brace.copy().set_stroke(BLACK, 3))
        brace.rotate(
            get_theta() + d_theta / 2,
            axis=UP,
            about_point=ORIGIN,
        )
        brace_label = TexMobject("R\\,d\\theta")
        brace_label.rotate(90 * DEGREES, RIGHT)
        brace_label.next_to(brace, OUT + RIGHT, buff=0)
        radial_line = self.radial_line
        R_label = self.R_label
        R_label.rotate(90 * DEGREES, RIGHT)
        R_label.next_to(radial_line, IN, SMALL_BUFF)

        self.play(
            TransformFromCopy(theta_group[1], alt_R_line),
            GrowFromCenter(brace),
            Animation(self.camera.phi_tracker),
        )
        self.wait()
        self.move_camera(
            phi=90 * DEGREES,
            theta=-90 * DEGREES,
        )
        self.wait()
        self.play(
            FadeInFrom(brace_label, IN),
        )
        self.play(
            ShowCreation(radial_line),
            FadeIn(R_label),
        )
        self.wait()
        self.move_camera(
            phi=70 * DEGREES,
            theta=-70 * DEGREES,
        )
        self.wait(3)

        self.set_variables_as_attrs(
            theta_tracker, lit_ring, theta_group,
            brace, brace_label, d_theta,
            alt_R_line, theta_mob_opacity_tracker,
        )

    def enumerate_rings(self):
        pass  # Skip, for now...

    def ask_about_ring_circumference(self):
        theta = self.theta_tracker.get_value()
        radius = self.sphere_config["radius"]
        circle = Circle(
            radius=radius * np.sin(theta)
        )
        circle.shift(radius * np.cos(theta) * OUT)
        circle.set_stroke(Color("red"), 5)

        to_fade = VGroup(
            self.R_label, self.radial_line,
            self.brace, self.brace_label
        )

        self.move_camera(
            phi=0 * DEGREES,
            theta=-90 * DEGREES,
            added_anims=[FadeOut(to_fade)]
        )
        self.play(ShowCreation(circle))
        self.wait()
        self.move_camera(
            phi=70 * DEGREES,
            theta=-70 * DEGREES,
            added_anims=[
                FadeIn(to_fade),
                FadeOut(circle),
            ]
        )
        self.wait()

    def ask_about_shadow_area(self):
        lit_ring = self.lit_ring
        lit_ring_copy = lit_ring.copy()
        lit_ring_copy.clear_updaters()

        all_shadows = self.shadows
        all_shadows.set_fill(BLUE_E, 0.5)
        for piece in all_shadows.family_members_with_points():
            piece.set_stroke(width=0)

        radius = self.sphere_config["radius"]
        shadow = self.get_shadow(lit_ring)
        theta = self.theta_tracker.get_value()
        d_theta = self.d_theta

        def get_dashed_line(angle):
            p0 = np.cos(angle) * OUT + np.sin(angle) * RIGHT
            p0 *= radius
            p1 = np.array([*p0[:2], 0])
            result = DashedLine(p0, p1)
            result.set_stroke(WHITE, 1)
            result.add_to_back(
                result.copy().set_stroke(BLACK, 2)
            )
            result.set_shade_in_3d(True)
            return result

        dashed_lines = VGroup(*[
            get_dashed_line(t)
            for t in [theta, theta + d_theta]
        ])

        self.play(
            ReplacementTransform(lit_ring_copy, shadow),
            FadeOut(self.R_label),
            FadeOut(self.radial_line),
            Animation(self.camera.phi_tracker),
            *map(ShowCreation, dashed_lines),
            run_time=2,
        )
        self.wait(2)

        self.set_variables_as_attrs(
            dashed_lines,
            lit_shadow=shadow,
        )

    def ask_about_2_to_1_correspondance(self):
        theta_tracker = ValueTracker(0)
        get_theta = theta_tracker.get_value
        new_lit_ring = always_redraw(
            lambda: self.get_ring_from_theta(
                self.rings, get_theta()
            ).copy().set_color(PINK)
        )

        self.add(new_lit_ring)
        for angle in [PI, 0, PI]:
            self.play(
                theta_tracker.set_value, angle,
                Animation(self.camera.phi_tracker),
                run_time=3
            )
        self.remove(new_lit_ring)
        self.remove(theta_tracker)

    def show_all_shadow_rings(self):
        lit_ring_copy = self.lit_ring.copy()
        lit_ring_copy.clear_updaters()
        self.remove(self.lit_ring)
        theta_group_copy = self.theta_group.copy()
        theta_group_copy.clear_updaters()
        self.remove(self.theta_group, *self.theta_group)
        to_fade = VGroup(
            theta_group_copy, self.alt_R_line,
            self.brace, self.brace_label,
            lit_ring_copy, self.lit_shadow,
            self.slice_circle,
            self.dashed_lines,
        )

        R_label = self.R_label
        radial_line = self.radial_line
        R_label.rotate(
            -90 * DEGREES,
            axis=RIGHT, about_point=radial_line.get_center()
        )
        shadows = self.shadows
        self.set_ring_colors(shadows, [GREY_BROWN, DARK_GREY])
        for submob in shadows:
            submob.save_state()
        shadows.become(self.rings.saved_state[:len(shadows)])

        self.play(
            FadeOut(to_fade),
            LaggedStartMap(FadeIn, shadows),
            self.theta_mob_opacity_tracker.set_value, 0,
        )
        self.play(
            LaggedStartMap(Restore, shadows),
            ApplyMethod(
                self.camera.phi_tracker.set_value, 60 * DEGREES,
            ),
            ApplyMethod(
                self.camera.theta_tracker.set_value, -130 * DEGREES,
            ),
            run_time=3
        )
        self.play(
            ShowCreation(radial_line),
            FadeIn(R_label),
            Animation(self.camera.phi_tracker),
        )
        self.begin_ambient_camera_rotation()
        self.wait()

        rings = self.rings
        rings_copy = rings.saved_state.copy()
        self.set_ring_colors(rings_copy)
        self.play(
            FadeOut(R_label),
            FadeOut(radial_line),
            FadeIn(rings_copy)
        )
        self.remove(rings_copy)
        rings.become(rings_copy)
        self.add(rings)

    def ask_about_global_correspondance(self):
        rings = self.rings

        self.play(
            FadeOut(rings[::2])
        )
        self.wait(8)

    #
    def set_ring_colors(self, rings, colors=[BLUE_E, BLUE_D]):
        for i, ring in enumerate(rings):
            color = colors[i % len(colors)]
            ring.set_fill(color, opacity=1)
            ring.set_stroke(color, width=0.5, opacity=1)
            for piece in ring:
                piece.insert_n_curves(4)
                piece.on_sphere = True
                piece.points = np.array([
                    *piece.points[3:-1],
                    *piece.points[:3],
                    piece.points[3]
                ])
        return rings

    def get_shadow(self, mobject):
        result = mobject.copy()
        result.apply_function(
            lambda p: np.array([*p[:2], 0])
        )
        return result

    def get_hemisphere(self, group, vect):
        if len(group.submobjects) == 0:
            if np.dot(group.get_center(), vect) > 0:
                return group
            else:
                return VMobject()
        else:
            return VGroup(*[
                self.get_hemisphere(submob, vect)
                for submob in group
            ])

    def get_northern_hemisphere(self, group):
        return self.get_hemisphere(group, OUT)

    def get_theta(self, ring):
        piece = ring[0]
        point = piece.points[3]
        return np.arccos(point[2] / get_norm(point))

    def get_theta_group(self, theta):
        arc = Arc(
            start_angle=90 * DEGREES,
            angle=-theta,
            radius=0.5,
        )
        arc.rotate(90 * DEGREES, RIGHT, about_point=ORIGIN)
        arc.set_stroke(YELLOW, 2)
        theta_mob = TexMobject("\\theta")
        theta_mob.rotate(90 * DEGREES, RIGHT)
        vect = np.cos(theta / 2) * OUT + np.sin(theta / 2) * RIGHT
        theta_mob.move_to(
            (arc.radius + 0.25) * normalize(vect),
        )
        theta_mob.set_background_stroke(width=1)

        radius = self.sphere_config["radius"]
        point = arc.point_from_proportion(1)
        radial_line = Line(
            ORIGIN, radius * normalize(point)
        )
        radial_line.set_stroke(WHITE, 2)

        return VGroup(arc, radial_line, theta_mob)

    def get_ring_from_theta(self, rings, theta):
        n_rings = len(rings)
        index = min(int((theta / PI) * n_rings), n_rings - 1)
        return rings[index]


class SecondProofHigherRes(SecondProof):
    CONFIG = {
        "sphere_config": {
            "resolution": (60, 60),
        },
    }


class SecondProofHighestRes(SecondProof):
    CONFIG = {
        "sphere_config": {
            "resolution": (120, 120),
        },
    }


class RangeFrom0To180(Scene):
    def construct(self):
        angle = Integer(0, unit="^\\circ")
        angle.scale(2)

        self.add(angle)
        self.wait()
        self.play(ChangeDecimalToValue(
            angle, 180,
            run_time=2,
        ))
        self.wait()


class Question1(Scene):
    def construct(self):
        kwargs = {
            "tex_to_color_map": {
                "circumference": RED,
            }
        }
        question = TextMobject(
            """
            \\small
            Question \\#1: What is the circumference of\\\\
            one of these rings (in terms of $R$ and $\\theta$)?\\\\
            """,
            **kwargs
        )
        prompt = TextMobject(
            """
            Multiply this circumference by $R\\,d\\theta$ to \\\\
            get an approximation of the ring's area.
            """,
            **kwargs

        )
        for words in question, prompt:
            words.set_width(FRAME_WIDTH - 1)

        self.play(FadeInFromDown(question))
        self.wait(2)
        for word in question, prompt:
            word.circum = word.get_part_by_tex("circumference")
            word.remove(word.circum)
        self.play(
            FadeOutAndShift(question, UP),
            FadeInFromDown(prompt),
            question.circum.replace, prompt.circum,
            run_time=1.5
        )
        self.wait()


class YouCouldIntegrate(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Integrate?",
            student_index=2,
            bubble_kwargs={"direction": LEFT},
        )
        self.play(self.teacher.change, "hesitant")
        self.wait()
        self.teacher_says(
            "We'll be a bit \\\\ more Archimedean",
            target_mode="speaking"
        )
        self.change_all_student_modes("confused")
        self.wait()


class Question2(Scene):
    def construct(self):
        question = TextMobject(
            """
            Question \\#2: What is the area of the shadow of\\\\
            one of these rings?  (In terms of $R$, $\\theta$, and $d\\theta$).
            """,
            tex_to_color_map={
                "shadow": YELLOW,
            }
        )
        question.set_width(FRAME_WIDTH - 1)

        self.play(FadeInFromDown(question))
        self.wait()


class Question3(Scene):
    def construct(self):
        question = TextMobject("Question \\#3:")
        question.to_edge(LEFT)
        equation = TextMobject(
            "(Shadow area)", "=", "$\\frac{1}{2}$",
            "(Area of one of the rings)"
        )
        equation[0][1:-1].set_color(YELLOW)
        equation[3][1:-1].set_color(PINK)
        equation.next_to(question, RIGHT)
        which_one = TextMobject("Which one?")
        # which_one.set_color(YELLOW)
        brace = Brace(equation[-1], DOWN, buff=SMALL_BUFF)
        which_one.next_to(brace, DOWN, SMALL_BUFF)

        self.add(question)
        self.play(FadeInFrom(equation))
        self.wait()
        self.play(
            GrowFromCenter(brace),
            Write(which_one)
        )
        self.wait()


class ExtraHint(Scene):
    def construct(self):
        title = TextMobject("Extra hint")
        title.scale(2.5)
        title.shift(UP)
        equation = TexMobject(
            "\\sin(2\\theta) = 2\\sin(\\theta)\\cos(\\theta)"
        )
        equation.next_to(title, DOWN)
        self.add(title, equation)


class Question4(Scene):
    def construct(self):
        question = TextMobject(
            "Question \\#4:",
            "Explain how the shadows relate to\\\\"
            "every other ring on the sphere.",
            tex_to_color_map={
                "shadows": YELLOW,
                "every other ring": BLUE,
            }
        )

        self.add(question[0])
        self.wait()
        self.play(FadeInFromDown(question[1:]))
        self.wait()


class Question5(Scene):
    def construct(self):
        question = TextMobject(
            """
            Question \\#5: Why does this imply that the \\\\
            shadow is $\\frac{1}{4}$ the surface area?
            """
        )
        self.play(FadeInFromDown(question))
        self.wait()


class SpherePatronThanks(Scene):
    CONFIG = {
        "specific_patrons": [
            "1stViewMaths",
            "Adrian Robinson",
            "Alexis Olson",
            "Ali Yahya",
            "Andrew Busey",
            "Ankalagon",
            "Antonio Juarez",
            "Art Ianuzzi",
            "Arthur Zey",
            "Awoo",
            "Bernd Sing",
            "Boris Veselinovich",
            "Brian Staroselsky",
            "brian tiger chow",
            "Brice Gower",
            "Britt Selvitelle",
            "Burt Humburg",
            "Carla Kirby",
            "Charles Southerland",
            "Chris Connett",
            "Christian Kaiser",
            "Clark Gaebel",
            "Cooper Jones",
            "Danger Dai",
            "Dave B",
            "Dave Kester",
            "dave nicponski",
            "David Clark",
            "David Gow",
            "Delton Ding",
            "Devarsh Desai",
            "Devin Scott",
            "eaglle",
            "Eric Younge",
            "Eryq Ouithaqueue",
            "Evan Phillips",
            "Federico Lebron",
            "Florian Chudigiewitsch",
            "Giovanni Filippi",
            "Graham",
            "Hal Hildebrand",
            "J",
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
            "John Shaughnessy",
            "John V Wertheim",
            "Jonathan Eppele",
            "Jonathan Wilson",
            "Joseph John Cox",
            "Joseph Kelly",
            "Juan Benet",
            "Julian Pulgarin",
            "Kai-Siang Ang",
            "Kanan Gill",
            "Kaustuv DeBiswas",
            "L0j1k",
            "Linh Tran",
            "Luc Ritchie",
            "Ludwig Schubert",
            "Lukas -krtek.net- Novy",
            "Lukas Biewald",
            "Magister Mugit",
            "Magnus Dahlström",
            "Magnus Lysfjord",
            "Mark B Bahu",
            "Markus Persson",
            "Mathew Bramson",
            "Mathias Jansson",
            "Matt Langford",
            "Matt Roveto",
            "Matt Russell",
            "Matthew Cocke",
            "Maurício Collares",
            "Mehdi Razavi",
            "Michael Faust",
            "Michael Hardel",
            "MrSneaky",
            "Mustafa Mahdi",
            "Márton Vaitkus",
            "Nathan Jessurun",
            "Nero Li",
            "Oliver Steele",
            "Omar Zrien",
            "Peter Ehrnstrom",
            "Peter Mcinerney",
            "Quantopian",
            "Randy C. Will",
            "Richard Burgmann",
            "Ripta Pasay",
            "Rish Kundalia",
            "Robert Teed",
            "Roobie",
            "Roy Larson",
            "Ryan Atallah",
            "Ryan Williams",
            "Scott Walter, Ph.D.",
            "Sindre Reino Trosterud",
            "soekul",
            "Solara570",
            "Song Gao",
            "Steven Soloway",
            "Stevie Metke",
            "Ted Suzman",
            "Valeriy Skobelev",
            "Vassili Philippov",
            "Xavier Bernard",
            "Yana Chernobilsky",
            "Yaw Etse",
            "YinYangBalance Asia",
            "Zach Cardwell",
        ],
    }

    def construct(self):
        self.add_title()
        self.show_columns()

    def add_title(self):
        title = TextMobject("Funded by the community, with special thanks to:")
        title.set_color(YELLOW)
        title.to_edge(UP)
        underline = Line(LEFT, RIGHT)
        underline.set_width(title.get_width() + MED_SMALL_BUFF)
        underline.next_to(title, DOWN, SMALL_BUFF)
        title.add(underline)

        self.add(title)
        self.title = title

    def show_columns(self):
        random.seed(1)
        random.shuffle(self.specific_patrons)
        patrons = VGroup(*[
            TextMobject(name)
            for name in self.specific_patrons
        ])
        columns = VGroup()
        column_size = 15
        for n in range(0, len(patrons), column_size):
            column = patrons[n:n + column_size]
            column.arrange(
                DOWN,
                aligned_edge=LEFT
            )
            columns.add(column)
        columns.set_height(6)
        for group in columns[:4], columns[4:]:
            for k, column in enumerate(group):
                column.move_to(
                    6.5 * LEFT + 3.75 * k * RIGHT + 2.5 * UP,
                    UL
                )

        self.add(columns[:4])
        self.wait()
        for k in range(4):
            self.play(
                FadeOut(columns[k]),
                FadeIn(columns[k + 4]),
            )
        self.wait()


class EndScreen(PatreonEndScreen):
    CONFIG = {
        "thanks_words": "",
    }


class ForThoseStillAround(Scene):
    def construct(self):
        words = TextMobject("Still here?")
        words.scale(1.5)
        url = TextMobject("3blue1brown.com/store")
        # url.scale(1.5)
        url.to_edge(UP, buff=MED_SMALL_BUFF)

        self.play(Write(words))
        self.wait()
        self.play(ReplacementTransform(words, url))
        self.wait()


class PatronWords(Scene):
    def construct(self):
        words = TextMobject("\\$2+ Patrons get \\\\ 50\\% off")
        words.to_corner(UL)
        words.set_color(RED)
        self.add(words)


class PlushMe(TeacherStudentsScene):
    def construct(self):
        self.student_says("Plushie me?")
        self.change_student_modes("happy", None, "happy")
        self.play(self.teacher.change, "confused")
        self.wait()
        self.teacher_says("...why?", target_mode="maybe")
        self.wait(2)


class Thumbnail(SpecialThreeDScene):
    CONFIG = {
        "camera_config": {
            "light_source_start_point": [-10, 5, 7],
        }
    }

    def construct(self):
        radius = 1.75
        sphere = self.get_sphere(radius=radius)
        sphere.rotate(70 * DEGREES, LEFT)
        sphere.set_fill(BLUE_E)
        sphere.set_stroke(WHITE, 0.5)

        circles = VGroup(*[
            Circle(radius=radius)
            for x in range(4)
        ])
        circles.set_stroke(WHITE, 2)
        circles.set_fill(BLUE_E, 1)
        circles[0].set_fill(GREY_BROWN)
        circles.arrange_in_grid()
        for circle in circles:
            formula = TexMobject("\\pi", "R", "^2")
            formula.set_color_by_tex("R", YELLOW)
            formula.scale(2)
            formula.move_to(circle)
            circle.add(formula)

        equals = TexMobject("=")
        equals.scale(3)

        group = VGroup(sphere, equals, circles)
        group.arrange(RIGHT, buff=MED_SMALL_BUFF)
        equals.shift(3 * SMALL_BUFF * RIGHT)

        why = TextMobject("Why?!")
        why.set_color(YELLOW)
        why.scale(2.5)
        why.next_to(sphere, UP)

        sa_formula = TexMobject("4\\pi", "R", "^2")
        sa_formula.set_color_by_tex("R", YELLOW)
        sa_formula.scale(2)
        sa_formula.next_to(sphere, DOWN)

        self.camera.distance_tracker.set_value(100)

        self.add(sphere, equals, circles, why, sa_formula)
