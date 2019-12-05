from manimlib.imports import *


class HoldUpMultivariableChainRule(TeacherStudentsScene):
    def construct(self):
        title = TextMobject("Multivariable chain rule")
        title.to_edge(UP, buff=MED_SMALL_BUFF)
        screen = ScreenRectangle()
        screen.next_to(title, DOWN)

        morty = self.teacher

        self.add(title)
        self.play(
            morty.change, "raise_right_hand",
            FadeInFromDown(screen)
        )
        self.change_all_student_modes(
            "confused", look_at_arg=screen
        )
        self.look_at(screen)
        self.wait(10)


class ComputationalNetwork(MovingCameraScene):
    CONFIG = {
        "x_color": YELLOW,
        "f_color": BLUE,
        "g_color": GREEN,
        "h_color": RED,
    }

    def construct(self):
        self.draw_network()
        self.walk_through_parts()
        self.write_dh_dx_goal()
        self.feed_forward_input()
        self.compare_x_and_h_wiggling()
        self.expand_out_h_as_function_of_x()
        self.show_four_derivatives()
        self.show_chain_rule()
        self.talk_through_mvcr_parts()
        self.plug_in_expressions()
        self.plug_in_values()
        self.discuss_meaning_of_result()

    def draw_network(self):
        x = TexMobject("x")
        f_formula = TexMobject("f", "=", "x", "^2")
        g_formula = TexMobject("g", "=", "\\cos(\\pi", "x", ")")
        h_formula = TexMobject("h", "=", "f", "^2", "g")

        self.tex_to_color_map = {
            "x": self.x_color,
            "f": self.f_color,
            "g": self.g_color,
            "h": self.h_color,
        }

        formulas = VGroup(x, f_formula, g_formula, h_formula)
        formula_groups = VGroup()
        for formula in formulas:
            formula.box = SurroundingRectangle(formula)
            formula.box.set_color(WHITE)
            formula.group = VGroup(formula, formula.box)
            formula.set_color_by_tex_to_color_map(
                self.tex_to_color_map
            )
            formula_groups.add(formula.group)
        f_formula.box.match_width(
            g_formula.box, stretch=True, about_edge=LEFT
        )

        fg_group = VGroup(f_formula.group, g_formula.group)
        fg_group.arrange(DOWN, buff=LARGE_BUFF)
        fg_group.to_edge(UP)
        x.group.next_to(fg_group, LEFT, buff=2)
        h_formula.group.next_to(fg_group, RIGHT, buff=2)

        xf_line = Line(x.box.get_right(), f_formula.box.get_left())
        xg_line = Line(x.box.get_right(), g_formula.box.get_left())
        fh_line = Line(f_formula.box.get_right(), h_formula.box.get_left())
        gh_line = Line(g_formula.box.get_right(), h_formula.box.get_left())

        graph_edges = VGroup(
            xf_line, xg_line, fh_line, gh_line
        )

        self.play(
            Write(x),
            FadeIn(x.box),
        )
        self.play(
            ShowCreation(xf_line),
            ShowCreation(xg_line),
            ReplacementTransform(x.box.copy(), f_formula.box),
            ReplacementTransform(x.box.copy(), g_formula.box),
        )
        self.play(
            Write(f_formula),
            Write(g_formula),
        )
        self.play(
            ShowCreation(fh_line),
            ShowCreation(gh_line),
            ReplacementTransform(f_formula.box.copy(), h_formula.box),
            ReplacementTransform(g_formula.box.copy(), h_formula.box),
        )
        self.play(Write(h_formula))
        self.wait()

        network = VGroup(formula_groups, graph_edges)

        self.set_variables_as_attrs(
            x, f_formula, g_formula, h_formula,
            xf_line, xg_line, fh_line, gh_line,
            formulas, formula_groups,
            graph_edges, network
        )

    def walk_through_parts(self):
        x = self.x
        f_formula = self.f_formula
        g_formula = self.g_formula
        h_formula = self.h_formula

        def indicate(mob):
            return ShowCreationThenDestructionAround(
                mob,
                surrounding_rectangle_config={
                    "buff": 0.5 * SMALL_BUFF,
                    "color": mob.get_color()
                }
            )

        for formula in f_formula, g_formula:
            self.play(indicate(formula[0]))
            self.play(ReplacementTransform(
                x.copy(),
                formula.get_parts_by_tex("x"),
                path_arc=PI / 3
            ))
            self.wait()

        self.play(indicate(h_formula[0]))
        self.play(ReplacementTransform(
            f_formula[0].copy(),
            h_formula.get_part_by_tex("f"),
            path_arc=PI / 3
        ))
        self.play(ReplacementTransform(
            g_formula[0].copy(),
            h_formula.get_part_by_tex("g"),
            path_arc=PI / 3
        ))
        self.wait()

    def write_dh_dx_goal(self):
        deriv = TexMobject(
            "{dh", "\\over", "dx}", "(", "2", ")"
        )
        deriv.set_color_by_tex_to_color_map(
            self.tex_to_color_map
        )
        deriv.scale(1.5)
        deriv.move_to(DOWN)

        self.play(FadeInFromDown(deriv[:3]))
        self.play(ShowCreationThenDestructionAround(deriv[:3]))
        self.wait(2)
        self.play(Write(deriv[3:]))
        self.wait()

        self.dh_dx_at_two = deriv

    def feed_forward_input(self):
        formula_groups = self.formula_groups
        x, f_formula, g_formula, h_formula = self.formulas
        dh_dx_at_two = self.dh_dx_at_two

        values = [2, 4, 1, 16]
        value_labels = VGroup()
        for formula_group, value in zip(formula_groups, values):
            label = TexMobject("=", str(value))
            eq, value_mob = label
            eq.rotate(90 * DEGREES)
            eq.next_to(value_mob, UP, SMALL_BUFF)
            var = formula_group[0][0]
            label[1].match_color(var)
            # label.next_to(formula_group, DOWN, SMALL_BUFF)
            label.next_to(var, DOWN, SMALL_BUFF)
            eq.add_background_rectangle(buff=SMALL_BUFF, opacity=1)
            value_labels.add(label)
        x_val_label, f_val_label, g_val_label, h_val_label = value_labels
        two, four, one, sixteen = [vl[1] for vl in value_labels]

        self.play(
            ReplacementTransform(
                dh_dx_at_two.get_part_by_tex("2").copy(),
                two,
            ),
            Write(x_val_label[0])
        )
        self.wait()

        two_copy1 = two.copy()
        two_copy2 = two.copy()
        four_copy = four.copy()
        one_copy = one.copy()
        x_in_f = f_formula.get_part_by_tex("x")
        x_in_g = g_formula.get_part_by_tex("x")
        f_in_h = h_formula.get_part_by_tex("f")
        g_in_h = h_formula.get_part_by_tex("g")

        self.play(
            two_copy1.move_to, x_in_f, DOWN,
            x_in_f.set_fill, {"opacity": 0},
        )
        self.wait()
        self.play(Write(f_val_label))
        self.wait()
        self.play(
            two_copy2.move_to, x_in_g, DOWN,
            x_in_g.set_fill, {"opacity": 0},
        )
        self.wait()
        self.play(Write(g_val_label))
        self.wait()

        self.play(
            four_copy.move_to, f_in_h, DOWN,
            f_in_h.set_fill, {"opacity": 0},
        )
        self.play(
            one_copy.move_to, g_in_h, DOWN,
            g_in_h.set_fill, {"opacity": 0},
        )
        self.wait()
        self.play(Write(h_val_label))
        self.wait()

        self.value_labels = value_labels
        self.revert_to_formula_animations = [
            ApplyMethod(term.set_fill, {"opacity": 1})
            for term in (x_in_f, x_in_g, f_in_h, g_in_h)
        ] + [
            FadeOut(term)
            for term in (two_copy1, two_copy2, four_copy, one_copy)
        ]

    def compare_x_and_h_wiggling(self):
        x_val = self.value_labels[0][1]
        h_val = self.value_labels[3][1]

        x_line = NumberLine(
            x_min=0,
            x_max=4,
            include_numbers=True,
            numbers_to_show=[0, 2, 4],
            unit_size=0.75,
        )
        x_line.next_to(
            x_val, DOWN, LARGE_BUFF,
            aligned_edge=RIGHT
        )
        h_line = NumberLine(
            x_min=0,
            x_max=32,
            include_numbers=True,
            numbers_with_elongated_ticks=[0, 16, 32],
            numbers_to_show=[0, 16, 32],
            tick_frequency=1,
            tick_size=0.05,
            unit_size=1.0 / 12,
        )
        h_line.next_to(
            h_val, DOWN, LARGE_BUFF,
            aligned_edge=LEFT
        )

        x_dot = Dot(color=self.x_color)
        x_dot.move_to(x_line.number_to_point(2))
        x_arrow = Arrow(self.x.get_bottom(), x_dot.get_top())
        x_arrow.match_color(x_dot)

        h_dot = Dot(color=self.h_color)
        h_dot.move_to(h_line.number_to_point(16))
        h_arrow = Arrow(self.h_formula[0].get_bottom(), h_dot.get_top())
        h_arrow.match_color(h_dot)

        self.play(
            ShowCreation(x_line),
            ShowCreation(h_line),
        )
        self.play(
            GrowArrow(x_arrow),
            GrowArrow(h_arrow),
            ReplacementTransform(x_val.copy(), x_dot),
            ReplacementTransform(h_val.copy(), h_dot),
        )
        self.wait()
        for x in range(2):
            self.play(
                x_dot.shift, 0.25 * RIGHT,
                h_dot.shift, 0.35 * RIGHT,
                rate_func=wiggle,
                run_time=1,
            )

        self.set_variables_as_attrs(
            x_line, h_line,
            x_dot, h_dot,
            x_arrow, h_arrow,
        )

    def expand_out_h_as_function_of_x(self):
        self.play(*self.revert_to_formula_animations)

        deriv = self.dh_dx_at_two

        expanded_formula = TexMobject(
            "h = x^4 \\cos(\\pi x)",
            tex_to_color_map=self.tex_to_color_map
        )
        expanded_formula.move_to(deriv)
        cross = Cross(expanded_formula)

        self.play(
            FadeInFromDown(expanded_formula),
            deriv.scale, 1.0 / 1.5,
            deriv.shift, DOWN,
        )
        self.wait()
        self.play(ShowCreation(cross))
        self.wait()
        self.play(
            FadeOut(VGroup(expanded_formula, cross)),
            deriv.shift, UP,
        )
        for edge in self.graph_edges:
            self.play(ShowCreationThenDestruction(
                edge.copy().set_stroke(YELLOW, 6)
            ))

    def show_four_derivatives(self):
        lines = self.graph_edges
        xf_line, xg_line, fh_line, gh_line = lines

        df_dx = TexMobject("df", "\\over", "dx")
        dg_dx = TexMobject("dg", "\\over", "dx")
        dh_df = TexMobject("\\partial h", "\\over", "\\partial f")
        dh_dg = TexMobject("\\partial h", "\\over", "\\partial g")
        derivatives = VGroup(df_dx, dg_dx, dh_df, dh_dg)

        df_dx.next_to(xf_line.get_center(), UP, SMALL_BUFF)
        dg_dx.next_to(xg_line.get_center(), DOWN, SMALL_BUFF)
        dh_df.next_to(fh_line.get_center(), UP, SMALL_BUFF)
        dh_dg.next_to(gh_line.get_center(), DOWN, SMALL_BUFF)

        partial_terms = VGroup(
            dh_df[0][0],
            dh_df[2][0],
            dh_dg[0][0],
            dh_dg[2][0],
        )
        partial_term_rects = VGroup(*[
            SurroundingRectangle(pt, buff=0.05)
            for pt in partial_terms
        ])
        partial_term_rects.set_stroke(width=0)
        partial_term_rects.set_fill(TEAL, 0.5)

        self.play(FadeOut(self.value_labels))
        for derivative in derivatives:
            derivative.set_color_by_tex_to_color_map(self.tex_to_color_map)
            derivative.add_to_back(derivative.copy().set_stroke(BLACK, 5))
            self.play(FadeInFromDown(derivative))
            self.wait()

        self.play(
            LaggedStartMap(FadeIn, partial_term_rects),
            Animation(derivatives)
        )
        self.wait()
        self.play(
            LaggedStartMap(FadeOut, partial_term_rects),
            Animation(derivatives)
        )

        self.derivatives = derivatives

    def show_chain_rule(self):
        dh_dx_at_two = self.dh_dx_at_two
        dh_dx = dh_dx_at_two[:3]
        at_two = dh_dx_at_two[3:]
        derivatives = self.derivatives.copy()
        df_dx, dg_dx, dh_df, dh_dg = derivatives

        frame = self.camera_frame

        self.play(
            frame.shift, 3 * UP,
            dh_dx.to_edge, UP,
            dh_dx.shift, 3 * LEFT + 3 * UP,
            at_two.set_fill, {"opacity": 0},
        )

        for deriv in derivatives:
            deriv.generate_target()
        rhs = VGroup(
            TexMobject("="),
            df_dx.target, dh_df.target,
            TexMobject("+"),
            dg_dx.target, dh_dg.target
        )
        rhs.arrange(
            RIGHT,
            buff=2 * SMALL_BUFF,
        )
        rhs.next_to(dh_dx, RIGHT)
        for deriv in derivatives:
            y = rhs[0].get_center()[1]
            alt_y = deriv.target[2].get_center()[1]
            deriv.target.shift((y - alt_y) * UP)

        self.play(
            Write(rhs[::3]),
            LaggedStartMap(MoveToTarget, derivatives)
        )
        self.wait()

        self.chain_rule_derivatives = derivatives
        self.chain_rule_rhs = rhs

    def talk_through_mvcr_parts(self):
        derivatives = self.derivatives
        cr_derivatives = self.chain_rule_derivatives

        df_dx, dg_dx, dh_df, dh_dg = cr_derivatives

        df, dx1 = df_dx[1::2]
        dg, dx2 = dg_dx[1::2]
        del_h1, del_f = dh_df[1::2]
        del_h2, del_g = dh_dg[1::2]
        terms = VGroup(df, dx1, dg, dx2, del_h1, del_f, del_h2, del_g)
        for term in terms:
            term.rect = SurroundingRectangle(
                term,
                buff=0.5 * SMALL_BUFF,
                stroke_width=0,
                fill_color=TEAL,
                fill_opacity=0.5
            )
        for derivative in derivatives:
            derivative.rect = SurroundingRectangle(
                derivative,
                color=TEAL
            )

        del_h_sub_f = TexMobject("f")
        del_h_sub_f.scale(0.5)
        del_h_sub_f.next_to(del_h1.get_corner(DR), RIGHT, buff=0)
        del_h_sub_f.set_color(self.f_color)

        lines = self.graph_edges
        top_lines = lines[::2].copy()
        bottom_lines = lines[1::2].copy()
        for group in top_lines, bottom_lines:
            group.set_stroke(YELLOW, 6)

        self.add_foreground_mobjects(cr_derivatives)
        rect = dx1.rect.copy()
        rect.save_state()
        rect.scale(3)
        rect.set_fill(opacity=0)

        self.play(
            rect.restore,
            FadeIn(derivatives[0].rect)
        )
        self.wait()
        self.play(Transform(rect, df.rect))
        self.wait()
        self.play(
            rect.replace, df_dx, {"stretch": True},
            rect.scale, 1.1,
        )
        self.wait()
        self.play(
            Transform(rect, del_f.rect),
            FadeOut(derivatives[0].rect),
            FadeIn(derivatives[2].rect),
        )
        self.wait()
        self.play(Transform(rect, del_h1.rect))
        self.wait()
        self.play(ReplacementTransform(
            del_f[1].copy(), del_h_sub_f,
            path_arc=PI,
        ))
        self.wait()
        self.play(
            del_h_sub_f.shift, UR,
            del_h_sub_f.fade, 1,
            rate_func=running_start,
            remover=True
        )
        self.wait()
        self.play(
            Transform(rect, del_f.rect),
            ReplacementTransform(rect.copy(), df.rect),
        )
        self.wait()
        for x in range(3):
            self.play(ShowCreationThenDestruction(
                top_lines,
                lag_ratio=1,
            ))
        self.wait()
        self.play(
            rect.replace, cr_derivatives[1::2], {"stretch": True},
            rect.scale, 1.1,
            FadeOut(df.rect),
            FadeOut(derivatives[2].rect),
            FadeIn(derivatives[1].rect),
            FadeIn(derivatives[3].rect),
        )
        self.wait()
        self.play(
            Transform(rect, dg.rect),
            FadeOut(derivatives[3].rect)
        )
        self.wait()
        self.play(Transform(rect, dx2.rect))
        self.wait()
        self.play(
            Transform(rect, del_h2.rect),
            FadeOut(derivatives[1].rect),
            FadeIn(derivatives[3].rect),
        )
        self.wait()
        self.play(Transform(rect, del_g.rect))
        self.wait()
        self.play(
            rect.replace, cr_derivatives, {"stretch": True},
            rect.scale, 1.1,
            FadeOut(derivatives[3].rect)
        )
        for x in range(3):
            self.play(*[
                ShowCreationThenDestruction(
                    group,
                    lag_ratio=1,
                )
                for group in (top_lines, bottom_lines)
            ])
        self.wait()
        self.play(FadeOut(rect))
        self.remove_foreground_mobject(cr_derivatives)

    def plug_in_expressions(self):
        lhs = VGroup(
            self.dh_dx_at_two[:3],
            self.chain_rule_rhs[::3],
            self.chain_rule_derivatives,
        )
        lhs.generate_target()
        lhs.target.to_edge(LEFT)
        df_dx, dg_dx, dh_df, dh_dg = self.chain_rule_derivatives

        formulas = self.formulas
        x, f_formula, g_formula, h_formula = formulas

        full_derivative = TexMobject(
            "=",
            "(", "2", "x", ")",
            "(", "2", "f", "g", ")",
            "+",
            "(", "-\\sin(", "\\pi", "x", ")", "\\pi", ")",
            "(", "f", "^2", ")"
        )
        full_derivative.next_to(lhs.target, RIGHT)
        full_derivative.set_color_by_tex_to_color_map(
            self.tex_to_color_map
        )

        self.play(MoveToTarget(lhs))
        self.play(Write(full_derivative[0]))

        # df/dx
        self.play(
            f_formula.shift, UP,
            df_dx.shift, 0.5 * DOWN
        )
        self.play(
            ReplacementTransform(
                f_formula[2:].copy(),
                full_derivative[2:4],
            ),
            FadeIn(full_derivative[1:5:3])
        )
        self.wait()
        self.play(
            f_formula.shift, DOWN,
            df_dx.shift, 0.5 * UP
        )
        self.wait()

        # dg/dx
        self.play(
            g_formula.shift, 0.75 * UP,
            dg_dx.shift, 0.5 * DOWN
        )
        self.play(
            ReplacementTransform(
                g_formula[2:].copy(),
                full_derivative[12:17],
            ),
            FadeIn(full_derivative[11:18:6]),
            Write(full_derivative[10]),
        )
        self.wait()
        self.play(
            g_formula.shift, 0.75 * DOWN,
            dg_dx.shift, 0.5 * UP
        )
        self.wait()

        # dh/df
        self.play(
            h_formula.shift, UP,
            dh_df.shift, 0.5 * DOWN
        )
        self.wait()
        self.play(
            ReplacementTransform(
                h_formula[2:].copy(),
                full_derivative[6:9],
            ),
            FadeIn(full_derivative[5:10:4])
        )
        self.wait()
        self.play(
            dh_df.shift, 0.5 * UP
        )

        # dh/dg
        self.play(
            dh_dg.shift, 0.5 * DOWN,
        )
        self.wait()
        self.play(
            ReplacementTransform(
                h_formula[2:].copy(),
                full_derivative[19:21],
            ),
            FadeIn(full_derivative[18:22:3])
        )
        self.wait()
        self.play(
            h_formula.shift, DOWN,
            dh_dg.shift, 0.5 * UP
        )
        self.wait()

        self.full_derivative = full_derivative

    def plug_in_values(self):
        full_derivative = self.full_derivative
        value_labels = self.value_labels

        rhs = TexMobject(
            """
            =
            (2 \\cdot 2)
            (2 \\cdot 4 \\cdot 1) +
            (-\\sin(\\pi 2)\\pi)(4^2)
            """,
            tex_to_color_map={
                "2": self.x_color,
                "4": self.f_color,
                "1": self.g_color,
                "^2": WHITE,
            }
        )
        rhs.next_to(full_derivative, DOWN, aligned_edge=LEFT)

        result = TexMobject("=", "32", "+", "0")
        result.next_to(rhs, DOWN, aligned_edge=LEFT)

        self.play(LaggedStartMap(Write, value_labels))
        self.wait()
        self.play(ReplacementTransform(
            full_derivative.copy(), rhs,
            lag_ratio=0.5,
            run_time=2
        ))
        self.wait()
        self.play(Write(result))
        self.wait()

    def discuss_meaning_of_result(self):
        x_dot = self.x_dot
        h_dot = self.h_dot

        for x in range(3):
            self.play(
                x_dot.shift, 0.25 * RIGHT,
                h_dot.shift, RIGHT,
                run_time=2,
                rate_func=lambda t: wiggle(t, 4)
            )
            self.wait()
