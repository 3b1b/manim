from big_ol_pile_of_manim_imports import *
from active_projects.ode.part1.shared_constructs import *
from active_projects.ode.part1.pendulum import Pendulum


# TODO: Arguably separate the part showing many
# configurations with the part showing just one.
class VisualizeStates(Scene):
    CONFIG = {
        "coordinate_plane_config": {
            "y_line_frequency": PI / 2,
            # "x_line_frequency": PI / 2,
            "x_line_frequency": 1,
            "y_axis_config": {
                # "unit_size": 1.75,
                "unit_size": 1,
            },
            "y_max": 4,
            "faded_line_ratio": 4,
            "background_line_style": {
                "stroke_width": 1,
            },
        },
        "little_pendulum_config": {
            "length": 1,
            "gravity": 4.9,
            "weight_diameter": 0.3,
            "include_theta_label": False,
            "include_velocity_vector": True,
            "angle_arc_config": {
                "radius": 0.2,
            },
            "velocity_vector_config": {
                "max_tip_length_to_length_ratio": 0.35,
                "max_stroke_width_to_length_ratio": 6,
            },
            "velocity_vector_multiple": 0.25,
            "max_velocity_vector_length_to_length_ratio": 0.8,
        },
        "big_pendulum_config": {
            "length": 1.6,
            "gravity": 4.9,
            "damping": 0.2,
            "weight_diameter": 0.3,
            "include_velocity_vector": True,
            "angle_arc_config": {
                "radius": 0.5,
            },
            "initial_theta": 80 * DEGREES,
            "omega": -1,
            "set_theta_label_height_cap": True,
        },
        "n_thetas": 11,
        "n_omegas": 7,
        # "n_thetas": 5,
        # "n_omegas": 3,
        "initial_grid_wait_time": 15,
    }

    def construct(self):
        self.initialize_plane()

        simple = False
        if simple:
            self.add(self.plane)
        else:
            self.initialize_grid_of_states()
            self.show_all_states_evolving()
            self.show_grid_of_states_creation()
            self.collapse_grid_into_points()
        self.show_state_with_pair_of_numbers()
        self.show_acceleration_dependence()
        self.show_evolution_from_a_start_state()

    def initialize_grid_of_states(self):
        pendulums = VGroup()
        rects = VGroup()
        state_grid = VGroup()
        thetas = self.get_initial_thetas()
        omegas = self.get_initial_omegas()
        for omega in omegas:
            row = VGroup()
            for theta in thetas:
                rect = Rectangle(
                    height=3,
                    width=3,
                    stroke_color=WHITE,
                    stroke_width=2,
                    fill_color=DARKER_GREY,
                    fill_opacity=1,
                )
                pendulum = Pendulum(
                    initial_theta=theta,
                    omega=omega,
                    top_point=rect.get_center(),
                    **self.little_pendulum_config,
                )
                pendulum.add_velocity_vector()
                pendulums.add(pendulum)
                rects.add(rect)
                state = VGroup(rect, pendulum)
                state.rect = rect
                state.pendulum = pendulum
                row.add(state)
            row.arrange(RIGHT, buff=0)
            state_grid.add(row)
        state_grid.arrange(UP, buff=0)

        state_grid.set_height(FRAME_HEIGHT)
        state_grid.center()
        state_grid.save_state(use_deepcopy=True)

        self.state_grid = state_grid
        self.pendulums = pendulums

    def initialize_plane(self):
        plane = self.plane = NumberPlane(
            **self.coordinate_plane_config
        )
        plane.axis_labels = VGroup(
            plane.get_x_axis_label(
                "\\theta", RIGHT, UL, buff=SMALL_BUFF
            ),
            plane.get_y_axis_label(
                "\\dot \\theta", UP, DR, buff=SMALL_BUFF
            ).set_color(YELLOW),
        )
        for label in plane.axis_labels:
            label.add_background_rectangle()
        plane.add(plane.axis_labels)

        plane.y_axis.add_numbers(direction=DL)

        x_axis = plane.x_axis
        label_texs = ["\\pi \\over 2", "\\pi", "3\\pi \\over 2", "\\tau"]
        values = [PI / 2, PI, 3 * PI / 2, TAU]
        x_axis.coordinate_labels = VGroup()
        x_axis.add(x_axis.coordinate_labels)
        for value, label_tex in zip(values, label_texs):
            for u in [-1, 1]:
                tex = label_tex
                if u < 0:
                    tex = "-" + tex
                label = TexMobject(tex)
                label.scale(0.5)
                if label.get_height() > 0.4:
                    label.set_height(0.4)
                point = x_axis.number_to_point(u * value)
                label.next_to(point, DR, SMALL_BUFF)
                x_axis.coordinate_labels.add(label)
        return plane

    def show_all_states_evolving(self):
        state_grid = self.state_grid
        pendulums = self.pendulums

        for pendulum in pendulums:
            pendulum.start_swinging()

        self.add(state_grid)
        self.wait(self.initial_grid_wait_time)

    def show_grid_of_states_creation(self):
        self.remove(self.state_grid)
        self.initialize_grid_of_states()  # Again
        state_grid = self.state_grid

        title = TextMobject("All states")
        title.to_edge(UP, buff=MED_SMALL_BUFF)
        self.all_states_title = title

        state_grid.set_height(
            FRAME_HEIGHT - title.get_height() - 2 * MED_SMALL_BUFF
        )
        state_grid.to_edge(DOWN, buff=0)

        def place_at_top(state):
            state.set_height(3)
            state.center()
            state.next_to(title, DOWN)

        middle_row = state_grid[len(state_grid) // 2]
        middle_row_copy = middle_row.deepcopy()
        right_column_copy = VGroup(*[
            row[-1] for row in state_grid
        ]).deepcopy()

        for state in it.chain(middle_row_copy, right_column_copy):
            place_at_top(state)

        self.add(title)
        self.play(
            ShowIncreasingSubsets(middle_row),
            ShowIncreasingSubsets(middle_row_copy),
            run_time=2,
            rate_func=linear,
        )
        self.wait()
        self.play(
            ShowIncreasingSubsets(state_grid),
            ShowIncreasingSubsets(right_column_copy),
            run_time=2,
            rate_func=linear,
        )
        self.remove(middle_row_copy)
        self.remove(middle_row)
        self.add(state_grid)
        self.remove(right_column_copy)
        self.play(
            ReplacementTransform(
                right_column_copy[-1],
                state_grid[-1][-1],
                remover=True
            )
        )
        self.wait()

    def collapse_grid_into_points(self):
        state_grid = self.state_grid
        plane = self.plane

        dots = VGroup()
        for row in state_grid:
            for state in row:
                dot = Dot(
                    self.get_state_point(state.pendulum),
                    radius=0.05,
                    color=YELLOW,
                    background_stroke_width=3,
                    background_stroke_color=BLACK,
                )
                dot.state = state
                dots.add(dot)

        self.add(plane)
        self.remove(state_grid)
        flat_state_group = VGroup(*it.chain(*state_grid))
        flat_dot_group = VGroup(*it.chain(*dots))
        self.clear()  # The nuclear option
        self.play(
            ShowCreation(plane),
            FadeOut(self.all_states_title),
            LaggedStart(*[
                TransformFromCopy(m1, m2)
                for m1, m2 in zip(flat_state_group, flat_dot_group)
            ], lag_ratio=0.1, run_time=4)
        )
        self.clear()  # Again, not sure why I need this
        self.add(plane, dots)
        self.wait()

        self.state_dots = dots

    def show_state_with_pair_of_numbers(self):
        axis_labels = self.plane.axis_labels

        state = self.get_flexible_state_picture()
        dot = self.get_state_controlling_dot(state)
        h_line = always_redraw(
            lambda: self.get_tracking_h_line(dot.get_center())
        )
        v_line = always_redraw(
            lambda: self.get_tracking_v_line(dot.get_center())
        )

        self.add(dot)
        anims = [GrowFromPoint(state, dot.get_center())]
        if hasattr(self, "state_dots"):
            anims.append(FadeOut(self.state_dots))
        self.play(*anims)

        for line, label in zip([h_line, v_line], axis_labels):
            # self.add(line, dot)
            self.play(
                ShowCreation(line),
                ShowCreationThenFadeAround(label),
                run_time=1
            )
        for vect in LEFT, 3 * UP:
            self.play(
                ApplyMethod(
                    dot.shift, vect,
                    rate_func=there_and_back,
                    run_time=2,
                )
            )
        self.wait()
        for vect in 2 * LEFT, 3 * UP, 2 * RIGHT, 2 * DOWN:
            self.play(dot.shift, vect, run_time=1.5)
        self.wait()

        self.state = state
        self.state_dot = dot
        self.h_line = h_line
        self.v_line = v_line

    def show_acceleration_dependence(self):
        ode = get_ode()
        thetas = ode.get_parts_by_tex("\\theta")
        thetas[0].set_color(RED)
        thetas[1].set_color(YELLOW)
        ode.move_to(
            FRAME_WIDTH * RIGHT / 4 +
            FRAME_HEIGHT * UP / 4,
        )
        ode.add_background_rectangle_to_submobjects()

        self.play(Write(ode))
        self.wait()
        self.play(FadeOut(ode))

    def show_evolution_from_a_start_state(self):
        state = self.state
        dot = self.state_dot

        self.play(
            Rotating(
                dot,
                about_point=dot.get_center() + UR,
                rate_func=smooth,
            )
        )
        self.wait()

        # Show initial trajectory
        state.pendulum.clear_updaters(recursive=False)
        self.tie_dot_position_to_state(dot, state)
        state.pendulum.start_swinging()
        trajectory = self.get_evolving_trajectory(dot)
        self.add(trajectory)
        for x in range(20):
            self.wait()

        # Talk through start
        trajectory.suspend_updating()
        state.pendulum.end_swinging()
        dot.clear_updaters()
        self.tie_state_to_dot_position(state, dot)

        alphas = np.linspace(0, 0.1, 1000)
        index = np.argmin([
            trajectory.point_from_proportion(a)[1]
            for a in alphas
        ])
        alpha = alphas[index]
        sub_traj = trajectory.copy()
        sub_traj.suspend_updating()
        sub_traj.pointwise_become_partial(trajectory, 0, alpha)
        sub_traj.match_style(trajectory)
        sub_traj.set_stroke(width=3)

        self.wait()
        self.play(dot.move_to, sub_traj.get_start())
        self.wait()
        self.play(
            ShowCreation(sub_traj),
            UpdateFromFunc(
                dot, lambda d: d.move_to(sub_traj.get_end())
            ),
            run_time=6,
        )
        self.wait()

        # Comment on physical velocity vs. space position
        v_vect = state.pendulum.velocity_vector
        v_line_copy = self.v_line.copy()
        v_line_copy.clear_updaters()
        v_line_copy.set_stroke(PINK, 5)
        td_label = self.plane.axis_labels[1]
        y_axis_copy = self.plane.y_axis.copy()
        y_axis_copy.submobjects = []
        y_axis_copy.match_style(v_line_copy)

        self.play(ShowCreationThenFadeAround(v_vect))
        self.play(
            ShowCreationThenFadeAround(td_label),
            ShowCreationThenFadeOut(y_axis_copy)
        )
        self.play(ShowCreationThenFadeOut(v_line_copy))
        self.wait()

        # Abstract vs. physical
        abstract = TextMobject("Abstract")
        abstract.add_background_rectangle()
        abstract.scale(2)
        abstract.to_corner(UR)
        physical = TextMobject("Physical")
        physical.next_to(state.get_top(), DOWN)

        self.play(
            ApplyMethod(
                self.plane.set_stroke, YELLOW, 0.5,
                rate_func=there_and_back,
                lag_ratio=0.2,
            ),
            FadeInFromDown(abstract),
            Animation(state),
        )
        self.wait()
        self.play(FadeInFromDown(physical))
        self.wait()

        # Continue on spiral
        sub_traj.resume_updating()
        state.pendulum.clear_updaters(recursive=False)
        state.pendulum.start_swinging()
        dot.clear_updaters()
        self.tie_dot_position_to_state(dot, state)
        self.wait(20)

    #
    def get_initial_thetas(self):
        angle = 3 * PI / 4
        return np.linspace(-angle, angle, self.n_thetas)

    def get_initial_omegas(self):
        return np.linspace(-1.5, 1.5, self.n_omegas)

    def get_state(self, pendulum):
        return (pendulum.get_theta(), pendulum.get_omega())

    def get_state_point(self, pendulum):
        return self.plane.coords_to_point(
            *self.get_state(pendulum)
        )

    def get_flexible_state_picture(self):
        buff = MED_SMALL_BUFF
        height = FRAME_HEIGHT / 2 - buff
        rect = Square(
            side_length=height,
            stroke_color=WHITE,
            stroke_width=2,
            fill_color="#111111",
            fill_opacity=1,
        )
        rect.to_corner(UL, buff=buff / 2)
        pendulum = Pendulum(
            top_point=rect.get_center(),
            **self.big_pendulum_config
        )
        pendulum.fixed_point_tracker.add_updater(
            lambda m: m.move_to(rect.get_center())
        )

        state = VGroup(rect, pendulum)
        state.rect = rect
        state.pendulum = pendulum
        return state

    def get_state_dot(self, state):
        dot = Dot(color=PINK)
        dot.move_to(self.get_state_point(state.pendulum))
        return dot

    def get_state_controlling_dot(self, state):
        dot = self.get_state_dot(state)
        self.tie_state_to_dot_position(state, dot)
        return dot

    def tie_state_to_dot_position(self, state, dot):
        def update_pendulum(pend):
            theta, omega = self.plane.point_to_coords(
                dot.get_center()
            )
            pend.set_theta(theta)
            pend.set_omega(omega)
            return pend
        state.pendulum.add_updater(update_pendulum)
        state.pendulum.get_arc_angle_theta = \
            lambda: self.plane.x_axis.point_to_number(dot.get_center())
        return self

    def tie_dot_position_to_state(self, dot, state):
        dot.add_updater(lambda d: d.move_to(
            self.get_state_point(state.pendulum)
        ))
        return dot

    def get_tracking_line(self, point, axis, color=WHITE):
        number = axis.point_to_number(point)
        axis_point = axis.number_to_point(number)
        return DashedLine(
            axis_point, point,
            dash_length=0.025,
            color=color,
        )

    def get_tracking_h_line(self, point):
        return self.get_tracking_line(
            point, self.plane.y_axis, WHITE,
        )

    def get_tracking_v_line(self, point):
        return self.get_tracking_line(
            point, self.plane.x_axis, YELLOW,
        )

    def get_evolving_trajectory(self, mobject):
        trajectory = VMobject()
        trajectory.start_new_path(mobject.get_center())
        trajectory.set_stroke(RED, 1)

        def update_trajectory(traj):
            point = mobject.get_center()
            if get_norm(trajectory.points[-1] == point) > 0.05:
                traj.add_smooth_curve_to(point)
        trajectory.add_updater(update_trajectory)
        return trajectory


class IntroduceVectorField(VisualizeStates):
    CONFIG = {
        "vector_field_config": {
            "max_magnitude": 3,
            # "delta_x": 2,
            # "delta_y": 2,
        },
        "big_pendulum_config": {
            "initial_theta": -80 * DEGREES,
            "omega": 1,
        }
    }

    def construct(self):
        self.initialize_plane()
        self.add_flexible_state()
        self.initialize_vector_field()
        self.add_equation()
        self.preview_vector_field()
        self.write_vector_derivative()
        self.interpret_first_coordinate()
        self.interpret_second_coordinate()
        self.show_full_vector_field()
        self.show_trajectory()

    def initialize_plane(self):
        super().initialize_plane()
        self.add(self.plane)

    def initialize_vector_field(self):
        self.vector_field = VectorField(
            self.vector_field_func,
            **self.vector_field_config,
        )
        self.vector_field.sort(get_norm)

    def add_flexible_state(self):
        self.state = self.get_flexible_state_picture()
        self.add(self.state)

    def add_equation(self):
        ode = get_ode()
        ode.set_width(self.state.get_width() - MED_LARGE_BUFF)
        ode.next_to(self.state.get_top(), DOWN, SMALL_BUFF)
        thetas = ode.get_parts_by_tex("\\theta")
        thetas[0].set_color(RED)
        thetas[1].set_color(YELLOW)
        ode_word = TextMobject("Differential equation")
        ode_word.match_width(ode)
        ode_word.next_to(ode, DOWN)

        self.play(
            FadeInFrom(ode, 0.5 * DOWN),
            FadeInFrom(ode_word, 0.5 * UP),
        )

        self.ode = ode
        self.ode_word = ode_word

    def preview_vector_field(self):
        vector_field = self.vector_field

        growth = LaggedStartMap(
            GrowArrow, vector_field,
            run_time=3,
            lag_ratio=0.01,
        )
        self.add(
            growth.mobject,
            vector_field,
            self.state, self.ode, self.ode_word
        )

        self.play(growth)
        self.wait()
        self.play(FadeOut(vector_field))
        self.remove(growth.mobject)

    def write_vector_derivative(self):
        state = self.state
        plane = self.plane

        dot = self.get_state_dot(state)

        # Vector
        vect = Arrow(
            plane.coords_to_point(0, 0),
            dot.get_center(),
            buff=0,
            color=dot.get_color()
        )
        vect_sym, d_vect_sym = [
            self.get_vector_symbol(
                "{" + a + "\\theta}(t)",
                "{" + b + "\\theta}(t)",
            )
            for a, b in [("", "\\dot"), ("\\dot", "\\ddot")]
        ]
        # vect_sym.get_entries()[1][0][1].set_color(YELLOW)
        # d_vect_sym.get_entries()[0][0][1].set_color(YELLOW)
        # d_vect_sym.get_entries()[1][0][1].set_color(RED)
        vect_sym.next_to(vect.get_end(), UP, MED_LARGE_BUFF)
        time_inputs = VGroup(*[
            e[-1][-2] for e in vect_sym.get_entries()
        ])

        # Derivative
        ddt = TexMobject("d \\over dt")
        ddt.set_height(0.9 * vect_sym.get_height())
        ddt.next_to(vect_sym, LEFT)
        ddt.set_stroke(BLACK, 5, background=True)
        equals = TexMobject("=")
        equals.add_background_rectangle()
        equals.next_to(vect_sym, RIGHT, SMALL_BUFF)
        d_vect_sym.next_to(equals, RIGHT, SMALL_BUFF)

        # Little vector
        angle_tracker = ValueTracker(0)
        mag_tracker = ValueTracker(0.75)
        d_vect = always_redraw(
            lambda: Vector(
                rotate_vector(
                    mag_tracker.get_value() * RIGHT,
                    angle_tracker.get_value(),
                ),
                color=WHITE
            ).shift(dot.get_center()),
        )
        d_vect_magnitude_factor_tracker = ValueTracker(2)
        real_d_vect = always_redraw(
            lambda: self.vector_field.get_vector(
                dot.get_center()
            ).scale(
                d_vect_magnitude_factor_tracker.get_value(),
                about_point=dot.get_center()
            )
        )

        # Show vector
        self.play(TransformFromCopy(state[1], vect))
        self.play(FadeInFromDown(vect_sym))
        self.wait()
        self.play(ReplacementTransform(vect, dot))
        self.wait()
        self.play(LaggedStartMap(
            ShowCreationThenFadeAround, time_inputs,
            lag_ratio=0.1,
        ))
        self.wait()

        # Write Derivative
        self.play(Write(ddt))
        self.play(
            plane.y_axis.numbers.fade, 1,
            FadeInFrom(equals, LEFT),
            TransformFromCopy(vect_sym, d_vect_sym)
        )
        self.wait()

        # Show as little vector
        equation_group = VGroup(
            ddt, vect_sym, equals, d_vect_sym
        )
        self.play(
            # equation_group.shift, 4 * DOWN,
            equation_group.to_edge, RIGHT, LARGE_BUFF,
            GrowArrow(d_vect),
        )
        self.wait()
        self.play(angle_tracker.set_value, 120 * DEGREES)
        self.play(mag_tracker.set_value, 1.5)
        self.wait()

        # Highlight new vector
        self.play(
            ShowCreationThenFadeAround(d_vect_sym),
            FadeOut(d_vect)
        )
        self.wait()
        self.play(
            TransformFromCopy(d_vect_sym, real_d_vect),
            dot.set_color, WHITE,
        )
        self.wait()

        # Take a walk
        trajectory = VMobject()
        trajectory.start_new_path(dot.get_center())
        dt = 0.01
        for x in range(130):
            p = trajectory.points[-1]
            dp_dt = self.vector_field_func(p)
            trajectory.add_smooth_curve_to(p + dp_dt * dt)
        self.tie_state_to_dot_position(state, dot)
        self.play(
            MoveAlongPath(dot, trajectory),
            run_time=5,
            rate_func=bezier([0, 0, 1, 1]),
        )

        self.state_dot = dot
        self.d_vect = real_d_vect
        self.equation_group = equation_group
        self.d_vect_magnitude_factor_tracker = d_vect_magnitude_factor_tracker

    def interpret_first_coordinate(self):
        equation = self.equation_group
        ddt, vect_sym, equals, d_vect_sym = equation
        dot = self.state_dot

        first_components_copy = VGroup(
            vect_sym.get_entries()[0],
            d_vect_sym.get_entries()[0],
        ).copy()
        rect = SurroundingRectangle(first_components_copy)
        rect.set_stroke(YELLOW, 2)

        equation.save_state()

        self.play(
            ShowCreation(rect),
            equation.fade, 0.5,
            Animation(first_components_copy),
        )
        self.wait()
        dot.save_state()
        self.play(dot.shift, 2 * UP)
        self.wait()
        self.play(dot.shift, 6 * DOWN)
        self.wait()
        self.play(dot.restore)
        self.wait()

        self.play(
            equation.restore,
            FadeOut(rect),
        )
        self.remove(first_components_copy)

    def interpret_second_coordinate(self):
        equation = self.equation_group
        ddt, vect_sym, equals, d_vect_sym = equation

        second_components = VGroup(
            vect_sym.get_entries()[1],
            d_vect_sym.get_entries()[1],
        )
        rect = SurroundingRectangle(second_components)
        rect.set_stroke(YELLOW, 2)

        expanded_derivative = self.get_vector_symbol(
            "{\\dot\\theta}(t)",
            "-\\mu {\\dot\\theta}(t)" +
            "-(g / L) \\sin\\big({\\theta}(t)\\big)",
        )
        expanded_derivative.move_to(d_vect_sym)
        expanded_derivative.to_edge(RIGHT, MED_SMALL_BUFF)
        equals2 = TexMobject("=")
        equals2.next_to(expanded_derivative, LEFT, SMALL_BUFF)

        equation.save_state()
        self.play(
            ShowCreation(rect),
        )
        self.wait()
        self.play(
            FadeInFrom(expanded_derivative, LEFT),
            FadeIn(equals2),
            equation.next_to, equals2, LEFT, SMALL_BUFF,
            MaintainPositionRelativeTo(rect, equation),
            VFadeOut(rect),
        )
        self.wait()

        self.full_equation = VGroup(
            *equation, equals2, expanded_derivative,
        )

    def show_full_vector_field(self):
        vector_field = self.vector_field
        state = self.state
        ode = self.ode
        ode_word = self.ode_word
        equation = self.full_equation
        d_vect = self.d_vect
        dot = self.state_dot

        equation.generate_target()
        equation.target.scale(0.7)
        equation.target.to_edge(DOWN, LARGE_BUFF)
        equation.target.to_edge(LEFT, MED_SMALL_BUFF)
        equation_rect = BackgroundRectangle(equation.target)

        growth = LaggedStartMap(
            GrowArrow, vector_field,
            run_time=3,
            lag_ratio=0.01,
        )
        self.add(
            growth.mobject,
            state, ode, ode_word,
            equation_rect, equation, dot,
            d_vect,
        )
        self.play(
            growth,
            FadeIn(equation_rect),
            MoveToTarget(equation),
            self.d_vect_magnitude_factor_tracker.set_value, 1,
        )

    def show_trajectory(self):
        state = self.state
        dot = self.state_dot

        state.pendulum.clear_updaters(recursive=False)
        self.tie_dot_position_to_state(dot, state)
        state.pendulum.start_swinging()

        trajectory = self.get_evolving_trajectory(dot)
        trajectory.set_stroke(WHITE, 3)

        self.add(trajectory, dot)
        self.wait(25)

    #
    def get_vector_symbol(self, tex1, tex2):
        t2c = {
            "{\\theta}": BLUE,
            "{\\dot\\theta}": YELLOW,
            "{\\omega}": YELLOW,
            "{\\ddot\\theta}": RED,
        }
        return get_vector_symbol(
            tex1, tex2,
            element_to_mobject_config={
                "tex_to_color_map": t2c,
            }
        ).scale(0.9)

    def vector_field_func(self, point):
        x, y = self.plane.point_to_coords(point)
        mu, g, L = [
            self.big_pendulum_config.get(key)
            for key in ["damping", "gravity", "length"]
        ]
        return pendulum_vector_field_func(
            x * RIGHT + y * UP,
            mu=mu, g=g, L=L
        )

    def ask_about_change(self):
        state = self.state

        dot = self.get_state_dot(state)
        d_vect = Vector(0.75 * RIGHT, color=WHITE)
        d_vect.shift(dot.get_center())
        q_mark = always_redraw(
            lambda: TexMobject("?").move_to(
                d_vect.get_end() + 0.4 * rotate_vector(
                    d_vect.get_vector(), 90 * DEGREES,
                ),
            )
        )

        self.play(TransformFromCopy(state[1], dot))
        self.tie_state_to_dot_position(state, dot)
        self.play(
            GrowArrow(d_vect),
            FadeInFromDown(q_mark)
        )
        for x in range(4):
            angle = 90 * DEGREES
            self.play(
                Rotate(
                    d_vect, angle,
                    about_point=d_vect.get_start(),
                )
            )
            self.play(
                dot.shift,
                0.3 * d_vect.get_vector(),
                rate_func=there_and_back,
            )


class ShowPendulumPhaseFlow(IntroduceVectorField):
    CONFIG = {
        "coordinate_plane_config": {
            "x_axis_config": {
                "unit_size": 0.8,
            },
            "x_max": 9,
            "x_min": -9,
        },
        "flow_time": 20,
    }

    def construct(self):
        self.initialize_plane()
        self.initialize_vector_field()
        plane = self.plane
        field = self.vector_field
        self.add(plane, field)

        stream_lines = StreamLines(
            field.func,
            delta_x=0.3,
            delta_y=0.3,
        )
        animated_stream_lines = AnimatedStreamLines(
            stream_lines,
            line_anim_class=ShowPassingFlashWithThinningStrokeWidth,
        )

        self.add(animated_stream_lines)
        self.wait(self.flow_time)


class ShowHighVelocityCase(ShowPendulumPhaseFlow, MovingCameraScene):
    CONFIG = {
        "coordinate_plane_config": {
            "x_max": 15,
            "x_min": -15,
        },
        "vector_field_config": {
            "x_max": 15,
        },
        "big_pendulum_config": {
            "max_velocity_vector_length_to_length_ratio": 1,
        },
    }

    def setup(self):
        MovingCameraScene.setup(self)

    def construct(self):
        self.initialize_plane()
        self.add(self.plane)
        self.initialize_vector_field()
        self.add(self.vector_field)
        self.add_flexible_state()
        self.show_trajectory()

    def show_trajectory(self):
        state = self.state
        plane = self.plane
        field = self.vector_field
        frame = self.camera_frame

        state.to_edge(DOWN, buff=SMALL_BUFF),
        start_point = plane.coords_to_point(0, 4)
        dot = self.get_state_controlling_dot(state)
        dot.move_to(start_point)
        state.update()

        traj = VMobject()
        traj.start_new_path(start_point)
        dt = 0.01
        total_time = 25
        for x in range(int(total_time / dt)):
            end = traj.points[-1]
            dp_dt = field.func(end)
            traj.add_smooth_curve_to(end + dp_dt * dt)

        traj.set_stroke(WHITE, 2)

        self.add(traj, dot)
        self.play(
            ShowCreation(
                traj,
                rate_func=linear,
            ),
            UpdateFromFunc(
                dot, lambda d: d.move_to(traj.points[-1])
            ),
            ApplyMethod(
                frame.shift, TAU * RIGHT,
                rate_func=squish_rate_func(
                    smooth, 0, 0.3,
                )
            ),
            MaintainPositionRelativeTo(state.rect, frame),
            run_time=total_time,
        )


class TweakMuInFormula(Scene):
    def construct(self):
        ode = get_ode()
        ode.to_edge(DOWN, buff=LARGE_BUFF)
        mu = ode.get_part_by_tex("\\mu")
        lil_rect = SurroundingRectangle(mu, buff=0.5 * SMALL_BUFF)
        lil_rect.stretch(1.2, 1, about_edge=DOWN)
        lil_rect.set_stroke(PINK, 2)

        interval = UnitInterval()
        interval.add_numbers(
            *np.arange(0, 1.2, 0.2)
        )
        interval.next_to(ode, UP, LARGE_BUFF)
        big_rect_seed = SurroundingRectangle(interval, buff=MED_SMALL_BUFF)
        big_rect_seed.stretch(1.5, 1, about_edge=DOWN)
        big_rect_seed.stretch(1.2, 0)
        big_rect = VGroup(*[
            DashedLine(v1, v2)
            for v1, v2 in adjacent_pairs(big_rect_seed.get_vertices())
        ])
        big_rect.set_stroke(PINK, 2)

        arrow = Arrow(
            lil_rect.get_top(),
            big_rect_seed.point_from_proportion(0.65),
            buff=SMALL_BUFF,
        )
        arrow.match_color(lil_rect)

        mu_tracker = ValueTracker(0.1)
        get_mu = mu_tracker.get_value

        triangle = Triangle(
            start_angle=-90 * DEGREES,
            stroke_width=0,
            fill_opacity=1,
            fill_color=WHITE,
        )
        triangle.set_height(0.2)
        triangle.add_updater(lambda t: t.next_to(
            interval.number_to_point(get_mu()),
            UP, buff=0,
        ))

        equation = VGroup(
            TexMobject("\\mu = "),
            DecimalNumber(),
        )
        equation.add_updater(
            lambda e: e.arrange(RIGHT).next_to(
                triangle, UP, SMALL_BUFF,
            ).shift(0.4 * RIGHT)
        )
        equation[-1].add_updater(
            lambda d: d.set_value(get_mu()).shift(0.05 * UL)
        )

        self.add(ode)
        self.play(ShowCreation(lil_rect))
        self.play(
            GrowFromPoint(interval, mu.get_center()),
            GrowFromPoint(triangle, mu.get_center()),
            GrowFromPoint(equation, mu.get_center()),
            TransformFromCopy(lil_rect, big_rect),
            ShowCreation(arrow)
        )
        self.wait()
        self.play(mu_tracker.set_value, 0.9, run_time=5)
        self.wait()


class TweakMuInVectorField(ShowPendulumPhaseFlow):
    def construct(self):
        self.initialize_plane()
        plane = self.plane
        self.add(plane)

        mu_tracker = ValueTracker(0.1)
        get_mu = mu_tracker.get_value

        def vector_field_func(p):
            x, y = plane.point_to_coords(p)
            mu = get_mu()
            g = self.big_pendulum_config.get("gravity")
            L = self.big_pendulum_config.get("length")
            return pendulum_vector_field_func(
                x * RIGHT + y * UP,
                mu=mu, g=g, L=L
            )

        def get_vector_field():
            return VectorField(
                vector_field_func,
                **self.vector_field_config,
            )

        field = always_redraw(get_vector_field)
        self.add(field)

        self.play(
            mu_tracker.set_value, 0.9,
            run_time=5,
        )
        field.suspend_updating()

        stream_lines = StreamLines(
            field.func,
            delta_x=0.3,
            delta_y=0.3,
        )
        animated_stream_lines = AnimatedStreamLines(
            stream_lines,
            line_anim_class=ShowPassingFlashWithThinningStrokeWidth,
        )
        self.add(animated_stream_lines)
        self.wait(self.flow_time)


class TakeManyTinySteps(IntroduceVectorField):
    CONFIG = {
        "initial_theta": 60 * DEGREES,
        "initial_theta_dot": 0,
    }

    def construct(self):
        self.initialize_plane()
        self.initialize_vector_field()
        field = self.vector_field
        field.set_opacity(0.35)
        self.add(self.plane, field)

        self.take_many_time_steps()

    def take_many_time_steps(self):
        delta_t_tracker = ValueTracker(0.5)
        get_delta_t = delta_t_tracker.get_value

        time_tracker = ValueTracker(10)
        get_t = time_tracker.get_value

        traj = always_redraw(
            lambda: self.get_time_step_trajectory(
                get_delta_t(), get_t()
            )
        )
        vectors = always_redraw(
            lambda: self.get_path_vectors(
                get_delta_t(), get_t()
            )
        )

        t_label, dt_label = labels = VGroup(*[
            VGroup(
                TexMobject("{} = ".format(s)),
                DecimalNumber(0)
            ).arrange(RIGHT, aligned_edge=DOWN)
            for s in ("t", "{\\Delta t}")
        ])
        init_labels = VGroup(
            TexMobject(
                "\\theta_0", "= \\pi / 3",
                tex_to_color_map={"\\theta": BLUE},
            ),
            TexMobject(
                "{\\dot\\theta}_0 = 0",
                tex_to_color_map={"{\\dot\\theta}": YELLOW},
            ),
        )
        for group in labels, init_labels:
            for label in group:
                label.scale(1.25)
                label.add_background_rectangle()
            group.arrange(DOWN)
            group.shift(FRAME_WIDTH * RIGHT / 4)
        labels.to_edge(UP)
        init_labels.shift(2 * DOWN)

        dt_label[-1].add_updater(
            lambda d: d.set_value(get_delta_t())
        )
        t_label[-1].add_updater(
            lambda d: d.set_value(
                int(get_t() / get_delta_t()) * get_delta_t()
            )
        )

        self.add(traj, vectors, init_labels, labels)
        time_tracker.set_value(0)
        self.play(
            time_tracker.set_value, 10,
            run_time=5,
            rate_func=linear,
        )
        self.wait()
        t_label[-1].clear_updaters()
        self.play(
            delta_t_tracker.set_value, 0.01,
            run_time=7,
        )
        self.wait()

    #
    def get_time_step_points(self, delta_t, total_time):
        plane = self.plane
        field = self.vector_field
        curr_point = plane.coords_to_point(
            self.initial_theta,
            self.initial_theta_dot,
        )
        points = [curr_point]
        t = 0
        while t < total_time:
            new_point = curr_point + field.func(curr_point) * delta_t
            points.append(new_point)
            curr_point = new_point
            t += delta_t
        return points

    def get_time_step_trajectory(self, delta_t, total_time):
        traj = VMobject()
        traj.set_points_as_corners(
            self.get_time_step_points(delta_t, total_time)
        )
        traj.set_stroke(WHITE, 2)
        return traj

    def get_path_vectors(self, delta_t, total_time):
        corners = self.get_time_step_points(
            delta_t, total_time
        )
        result = VGroup()
        for a1, a2 in zip(corners, corners[1:]):
            vector = Arrow(
                a1, a2, buff=0,
            )
            vector.match_style(
                self.vector_field.get_vector(a1)
            )
            result.add(vector)
        return result
