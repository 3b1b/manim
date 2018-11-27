from big_ol_pile_of_manim_imports import *
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

    def get_cylinder(self):
        return Cylinder(**self.sphere_config)

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
        self.play(LaggedStart(
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
        shadows.arrange_submobjects_in_grid(buff=MED_LARGE_BUFF)
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
        self.play(LaggedStart(FadeInFromLarge, area_labels))
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
            LaggedStart(
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
    def construct(self):
        self.student_says(
            "But why?!?",
            student_index=2,
            target_mode="angry",
            bubble_kwargs={"direction": LEFT},
        )
        self.play(
            self.students[0].change, "pondering", self.screen,
            self.students[1].change, "pondering", self.screen,
            self.teacher.change, "guilty", self.screen,
        )
        self.wait(3)


class TryFittingCirclesDirectly(ExternallyAnimatedScene):
    pass


class PreviewTwoMethods(Scene):
    def construct(self):
        pass  # TODO


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

        self.play(LaggedStart(
            DrawBorderThenFill, VGroup(*lines, *texs)
        ))
        self.wait()


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
        self.play(LaggedStart(Restore, pieces))
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
            LaggedStart(MoveToTarget, pieces),
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
        l_brace, h_brace = equation.braces
        length_label, height_label = equation.labels

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
                line.add(DashedMobject(line, spacing=-1))
                line.set_points([])
                line.set_stroke(width=2)
            lines.set_shade_in_3d(True)
        lat_lines.set_color(RED)
        lon_lines.set_color(PINK)

        self.play(
            *map(ShowCreationThenDestruction, lat_lines),
            run_time=2
        )
        self.add_fixed_in_frame_mobjects(l_brace, length_label)
        self.play(
            GrowFromCenter(l_brace),
            Write(length_label),
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
        equation.arrange_submobjects(RIGHT)
        equation.to_corner(UR)

        brace = Brace(Line(ORIGIN, 0.5 * RIGHT), DOWN)
        l_brace = brace.copy().match_width(lhs, stretch=True)
        h_brace = brace.copy().rotate(-90 * DEGREES)
        h_brace.match_height(lhs, stretch=True)
        l_brace.next_to(lhs, DOWN, buff=SMALL_BUFF)
        h_brace.next_to(lhs, LEFT, buff=SMALL_BUFF)
        braces = VGroup(l_brace, h_brace)

        length_label = TextMobject("Length")
        height_label = TextMobject("Height")
        labels = VGroup(length_label, height_label)
        labels.scale(0.75)
        length_label.next_to(l_brace, DOWN, SMALL_BUFF)
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
        shadow = updating_mobject_from_func(lambda: get_shadow(square))

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
        self.move_camera(
            phi=80 * DEGREES,
            theta=-85 * DEGREES,
        )

    def label_R(self):
        circle = self.circle
        R_line = Line(ORIGIN, circle.get_right())
        R_line.set_color(self.R_color)
        R_label = TexMobject("R")
        R_label.next_to(R_line, IN + DOWN)

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
        d_label.next_to(d_line, IN + DOWN)

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
                d_label.next_to, to_fade_in, IN + DOWN,
            )

        self.d_line = d_line
        self.d_label = d_label

    def show_similar_triangles(self):
        d_line = self.d_line
        d_label = self.d_label
        R_line = self.R_line
        R_label = self.R_label
        example_group = self.example_group
        s_rect = example_group[0]

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
            triangle.copy(),
            TexMobject("\\sim"),
            big_triangle.copy()
        )
        equation.arrange_submobjects(RIGHT, buff=SMALL_BUFF)
        equation.to_corner(UL)
        eq_d = TexMobject("d").next_to(equation[0], DOWN, SMALL_BUFF)
        eq_R = TexMobject("R").next_to(equation[2], DOWN, SMALL_BUFF)

        self.move_camera(
            phi=0 * DEGREES,
            theta=-90 * DEGREES,
            distance=1000,
            added_anims=[
                d_label.next_to, d_line, DOWN, SMALL_BUFF,
                FadeOut(R_label)
            ],
            run_time=2,
        )
        self.play(FadeInFromLarge(triangle, 3))
        self.wait()
        for x in range(2):
            self.play(ShowCreationThenDestruction(base))
        self.wait()
        self.play(ShowCreation(d_line))
        self.wait(2)
        self.play(
            TransformFromCopy(triangle, equation[0]),
            FadeIn(equation[1:]),
            FadeInFromDown(eq_d),
            FadeInFromDown(eq_R),
        )
        self.wait()
        self.play(
            ReplacementTransform(triangle, big_triangle),
            FadeOut(d_label),
            FadeIn(R_label),
        )
        self.add(R_line)
        R_line.set_color(WHITE)
        self.play(ShowCreation(R_line))
        self.wait(3)

        self.add_fixed_in_frame_mobjects(equation, eq_d, eq_R)
        self.move_camera(
            phi=70 * DEGREES,
            theta=-70 * DEGREES,
            added_anims=[
                big_triangle.set_fill, {"opacity": 0.25}
            ]
        )
        self.begin_ambient_camera_rotation()
        lost_hemisphere = self.lost_hemisphere
        lost_hemisphere.restore()
        left_point = self.sphere.get_left()
        lost_hemisphere.rotate(-PI, axis=OUT, about_point=left_point)
        d_label.next_to(d_line, IN, buff=0.3)
        self.play(
            Rotate(
                lost_hemisphere, PI,
                axis=OUT,
                about_point=left_point,
            ),
            VFadeIn(lost_hemisphere),
            FadeOut(self.circle),
            FadeIn(d_label),
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


class LengthScaleLabel(Scene):
    def construct(self):
        text = TexMobject(
            "\\text{Length scale factor} =",
            "\\frac{R}{d}"
        )
        self.play(Write(text))
        self.wait()


class TinierAndTinerRectangles(SphereCylinderScene):
    def construct(self):
        spheres = [
            self.get_sphere(
                resolution=(12 * (2**n), 24 * (2**n)),
                stroke_width=0,
            )
            for n in range(4)
        ]
        self.set_camera_to_default_position()
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
                LaggedStart(Restore, s2)
            )
            self.remove(s1)


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
        "top_phi": 0.5242654422649652,
        "low_phi": 0.655081802831207,
    }

    def construct(self):
        pass
