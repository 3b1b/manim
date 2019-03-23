from big_ol_pile_of_manim_imports import *
from active_projects.ode.part1.shared_constructs import *
from active_projects.ode.part1.pendulum import Pendulum


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
            "length": 1.7,
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
        # "n_thetas": 11,
        # "n_omegas": 7,
        "n_thetas": 3,
        "n_omegas": 5,
        "initial_grid_wait_time": 15,
    }

    def construct(self):
        self.initialize_grid_of_states()
        self.initialize_plane()

        simple = True
        if simple:
            self.add(self.plane)
        else:
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
        state_grid = self.state_grid
        pendulums = self.pendulums

        title = TextMobject("All states")
        title.to_edge(UP, buff=MED_SMALL_BUFF)
        self.all_states_title = title

        self.remove(state_grid)
        state_grid.restore()
        for pendulum in pendulums:
            pendulum.end_swinging()

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
        )
        self.wait()
        self.play(
            ShowIncreasingSubsets(state_grid),
            ShowIncreasingSubsets(right_column_copy),
            run_time=2,
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
        self.play(
            ShowCreation(plane),
            LaggedStart(*[
                TransformFromCopy(m1, m2)
                for m1, m2 in zip(
                    VGroup(*it.chain(*state_grid)),
                    VGroup(*it.chain(*dots)),
                )
            ], lag_ratio=0.1, run_time=4)
        )
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
        for vect in 2 * LEFT, 3 * UP, 2 * DR:
            self.play(dot.shift, vect)
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

        # alphas = np.linspace(0, 0.1, 100)
        alphas = np.linspace(0, 1, 1000)
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
        abstract.scale(2)
        abstract.to_corner(UR)
        physical = TextMobject("Physical")
        physical.next_to(state.get_top(), DOWN)

        self.play(
            ApplyMethod(
                self.plane.set_stroke, YELLOW, 1,
                rate_func=there_and_back,
                lag_ratio=0.01,
            ),
            Write(abstract),
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
        height = (FRAME_HEIGHT - SMALL_BUFF) / 2
        rect = Square(
            side_length=height,
            stroke_color=WHITE,
            stroke_width=2,
            fill_color="#111111",
            fill_opacity=1,
        )
        rect.to_corner(UL, buff=SMALL_BUFF / 2)
        pendulum = Pendulum(
            top_point=rect.get_center(),
            **self.big_pendulum_config
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
            if not np.all(trajectory.points[-1] == point):
                traj.add_smooth_curve_to(point)
        trajectory.add_updater(update_trajectory)
        return trajectory


class NewSceneName(Scene):
    def construct(self):
        pass
