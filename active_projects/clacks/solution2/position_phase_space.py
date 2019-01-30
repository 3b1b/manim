from big_ol_pile_of_manim_imports import *
from active_projects.clacks.question import Block
from active_projects.clacks.question import Wall
from active_projects.clacks.question import ClackFlashes


class PositionPhaseSpaceScene(Scene):
    CONFIG = {
        "rescale_coordinates": True,
        "wall_x": -6,
        "wall_config": {
            "height": 1.6,
            "tick_spacing": 0.35,
            "tick_length": 0.2,
        },
        "wall_height": 1.5,
        "floor_y": -3.5,
        "block1_config": {
            "mass": 10,
            "distance": 9,
            "velocity": 1,
            "width": 1.6,
        },
        "block2_config": {
            "mass": 1,
            "distance": 4,
        },
        "axes_config": {
            "x_min": -0.5,
            "x_max": 31,
            "y_min": -0.5,
            "y_max": 10.5,
            "x_axis_config": {
                "unit_size": 0.4,
                "tick_frequency": 2,
            },
            "y_axis_config": {
                "unit_size": 0.4,
                "tick_frequency": 2,
            },
        },
        "axes_center": 5 * LEFT + 0.65 * DOWN,
        "ps_dot_config": {
            "fill_color": RED,
            "background_stroke_width": 1,
            "background_stroke_color": BLACK,
            "radius": 0.05,
        },
        "clack_sound": "clack",
        "mirror_line_class": Line,
        "mirror_line_style": {
            "stroke_color": WHITE,
            "stroke_width": 1,
        },
    }

    def setup(self):
        self.all_items = [
            self.get_floor(),
            self.get_wall(),
            self.get_blocks(),
            self.get_axes(),
            self.get_phase_space_point(),
            self.get_phase_space_x_line(),
            self.get_phase_space_y_line(),
            self.get_phase_space_dot(),
            self.get_phase_space_d1_label(),
            self.get_phase_space_d2_label(),
            self.get_d1_brace(),
            self.get_d2_brace(),
            self.get_d1_label(),
            self.get_d2_label(),
            self.get_d1_eq_d2_line(),
            self.get_d1_eq_d2_label(),
            self.get_d2_eq_w2_line(),
            self.get_d2_eq_w2_label(),
        ]

    def get_floor_wall_corner(self):
        return self.wall_x * RIGHT + self.floor_y * UP

    def get_mass_ratio(self):
        return op.truediv(
            self.block1.mass,
            self.block2.mass,
        )

    def d1_to_x(self, d1):
        if self.rescale_coordinates:
            d1 *= np.sqrt(self.block1.mass)
        return d1

    def d2_to_y(self, d2):
        if self.rescale_coordinates:
            d2 *= np.sqrt(self.block2.mass)
        return d2

    def ds_to_point(self, d1, d2):
        return self.axes.coords_to_point(
            self.d1_to_x(d1), self.d2_to_y(d2),
        )

    def point_to_ds(self, point):
        x, y = self.axes.point_to_coords(point)
        if self.rescale_coordinates:
            x /= np.sqrt(self.block1.mass)
            y /= np.sqrt(self.block2.mass)
        return (x, y)

    def get_d1(self):
        return self.get_ds()[0]

    def get_d2(self):
        return self.get_ds()[1]

    def get_ds(self):
        return self.point_to_ds(self.ps_point.get_location())

    # Relevant for sliding
    def tie_blocks_to_ps_point(self):
        def update_blocks(blocks):
            d1, d2 = self.point_to_ds(self.ps_point.get_location())
            b1, b2 = blocks
            corner = self.get_floor_wall_corner()
            b1.move_to(corner + d1 * RIGHT, DL)
            b2.move_to(corner + d2 * RIGHT, DR)
        self.blocks.add_updater(update_blocks)

    def time_to_ds(self, time):
        # Deals in its own phase space, different
        # from the one displayed
        m1 = self.block1.mass
        m2 = self.block2.mass
        v1 = self.block1.velocity
        start_d1 = self.block1_config["distance"]
        start_d2 = self.block2_config["distance"]
        w2 = self.block2.width
        start_d2 += w2
        ps_speed = np.sqrt(m1) * abs(v1)
        theta = np.arctan(np.sqrt(m2 / m1))

        def ds_to_ps_point(d1, d2):
            return np.array([
                d1 * np.sqrt(m1),
                d2 * np.sqrt(m2),
                0
            ])

        def ps_point_to_ds(point):
            return (
                point[0] / np.sqrt(m1),
                point[1] / np.sqrt(m2),
            )

        ps_point = ds_to_ps_point(start_d1, start_d2)
        wedge_corner = ds_to_ps_point(w2, w2)
        ps_point -= wedge_corner
        # Pass into the mirror worlds
        ps_point += time * ps_speed * LEFT
        # Reflect back to the real world
        angle = angle_of_vector(ps_point)
        n = int(angle / theta)
        if n % 2 == 0:
            ps_point = rotate_vector(ps_point, -n * theta)
        else:
            ps_point = rotate_vector(
                ps_point,
                -(n + 1) * theta,
            )
            ps_point[1] = abs(ps_point[1])
        ps_point += wedge_corner
        return ps_point_to_ds(ps_point)

    def get_clack_data(self):
        # Copying from time_to_ds.  Not great, but
        # maybe I'll factor things out properly later.
        m1 = self.block1.mass
        m2 = self.block2.mass
        v1 = self.block1.velocity
        w2 = self.block2.get_width()
        h2 = self.block2.get_height()
        ps_speed = np.sqrt(m1) * abs(v1)
        theta = np.arctan(np.sqrt(m2 / m1))

        def ds_to_ps_point(d1, d2):
            return np.array([
                d1 * np.sqrt(m1),
                d2 * np.sqrt(m2),
                0
            ])

        def ps_point_to_ds(point):
            return (
                point[0] / np.sqrt(m1),
                point[1] / np.sqrt(m2),
            )

        ps_point = ds_to_ps_point(*self.get_ds())
        wedge_corner = ds_to_ps_point(w2, w2)
        ps_point -= wedge_corner
        y = ps_point[1]

        clack_data = []
        for k in range(1, int(PI / theta) + 1):
            clack_ps_point = np.array([
                y / np.tan(k * theta), y, 0
            ])
            time = get_norm(ps_point - clack_ps_point) / ps_speed
            reflected_point = rotate_vector(
                clack_ps_point,
                -2 * np.ceil((k - 1) / 2) * theta
            )
            d1, d2 = ps_point_to_ds(reflected_point + wedge_corner)
            loc1 = self.get_floor_wall_corner() + h2 * UP / 2 + d2 * RIGHT
            if k % 2 == 0:
                loc1 += w2 * LEFT
            loc2 = self.ds_to_point(d1, d2)
            clack_data.append((time, loc1, loc2))
        return clack_data

    def get_clack_flashes(self):
        pass  # TODO

    def tie_ps_point_to_time_tracker(self):
        time_tracker = self.get_time_tracker()

        def update_ps_point(p):
            time = time_tracker.get_value()
            ds = self.time_to_ds(time)
            p.move_to(self.ds_to_point(*ds))
        self.ps_point.add_updater(update_ps_point)
        self.add(time_tracker)

    def add_clack_flashes(self):
        clack_data = self.get_clack_data()
        self.clack_times = [
            time for (time, loc1, loc2) in clack_data
        ]
        self.block_flashes = ClackFlashes([
            (loc1, time)
            for (time, loc1, loc2) in clack_data
        ])
        self.ps_flashes = ClackFlashes([
            (loc2, time)
            for (time, loc1, loc2) in clack_data
        ])
        self.add(
            self.block_flashes,
            self.ps_flashes,
        )

    def begin_sliding(self):
        self.tie_ps_point_to_time_tracker()
        self.add_clack_flashes()

    def end_sliding(self):
        self.ps_point.clear_updaters()
        self.remove(self.time_tracker)
        for attr in ["block_flashes", "ps_flashes"]:
            if hasattr(self, attr):
                self.remove(getattr(self, attr))
        total_time = self.time_tracker.get_value()
        for time in self.clack_times:
            if time < total_time:
                offset = total_time - time
                self.add_sound(
                    "clack",
                    time_offset=-offset,
                )

    def get_continually_building_trajectory(self):
        trajectory = VMobject()
        self.continually_building_trajectory = trajectory
        trajectory.set_stroke(YELLOW, 1)

        def get_point():
            return np.array(self.ps_point.get_location())

        points = [get_point(), get_point()]
        trajectory.set_points_as_corners(points)
        epsilon = 0.001

        def update_trajectory(trajectory):
            new_point = get_point()
            p1, p2 = trajectory.get_anchors()[-2:]
            angle = angle_between_vectors(
                p2 - p1,
                new_point - p2,
            )
            if angle > epsilon:
                points.append(new_point)
            else:
                points[-1] = new_point
            trajectory.set_points_as_corners(points)

        trajectory.add_updater(update_trajectory)
        return trajectory

    def get_ps_point_change_anim(self, d1, d2):
        b1 = self.block1
        ps_speed = np.sqrt(b1.mass) * abs(b1.velocity)
        curr_d1, curr_d2 = self.get_ds()
        distance = get_norm([curr_d1 - d1, curr_d2 - d2])
        return ApplyMethod(
            self.ps_point.move_to,
            self.ds_to_point(d1, d2),
            run_time=(distance / ps_speed),
            rate_func=None,
        )

    # Mobject getters
    def get_floor(self):
        floor = self.floor = Line(
            self.wall_x * RIGHT,
            FRAME_WIDTH * RIGHT / 2,
            stroke_color=WHITE,
            stroke_width=3,
        )
        floor.move_to(self.get_floor_wall_corner(), LEFT)
        return floor

    def get_wall(self):
        wall = self.wall = Wall(**self.wall_config)
        wall.move_to(self.get_floor_wall_corner(), DR)
        return wall

    def get_blocks(self):
        blocks = self.blocks = VGroup()
        for n in [1, 2]:
            config = getattr(self, "block{}_config".format(n))
            block = Block(**config)
            block.move_to(self.get_floor_wall_corner(), DL)
            block.shift(config["distance"] * RIGHT)
            block.label.move_to(block)
            block.label.set_fill(BLACK)
            block.label.set_stroke(WHITE, 3, background=True)
            self.blocks.add(block)
        self.block1, self.block2 = blocks
        return blocks

    def get_axes(self):
        axes = self.axes = Axes(**self.axes_config)
        axes.set_stroke(LIGHT_GREY, 2)
        axes.shift(
            self.axes_center - axes.coords_to_point(0, 0)
        )
        axes.labels = self.get_axes_labels(axes)
        axes.add(axes.labels)
        axes.added_lines = self.get_added_axes_lines(axes)
        axes.add(axes.added_lines)
        return axes

    def get_added_axes_lines(self, axes):
        c2p = axes.coords_to_point
        y_lines = VGroup(*[
            Line(
                c2p(0, 0), c2p(0, axes.y_max + 1),
            ).move_to(c2p(x, 0), DOWN)
            for x in np.arange(0, axes.x_max)
        ])
        x_lines = VGroup(*[
            Line(
                c2p(0, 0), c2p(axes.x_max, 0),
            ).move_to(c2p(0, y), LEFT)
            for y in np.arange(0, axes.y_max)
        ])
        line_groups = VGroup(x_lines, y_lines)
        for lines in line_groups:
            lines.set_stroke(BLUE, 1, 0.5)
            lines[1::2].set_stroke(width=0.5, opacity=0.25)
        return line_groups

    def get_axes_labels(self, axes):
        x_label = TexMobject("x = ", "d_1")
        y_label = TexMobject("y = ", "d_2")
        labels = VGroup(x_label, y_label)
        if self.rescale_coordinates:
            additions = map(TexMobject, [
                "\\sqrt{m_1}", "\\sqrt{m_2}"
            ])
            for label, addition in zip(labels, additions):
                addition.move_to(label[1], DL)
                label[1].next_to(
                    addition, RIGHT, SMALL_BUFF,
                    aligned_edge=DOWN
                )
                addition[2:].set_color(BLUE)
                label.add(addition)
        x_label.next_to(axes.x_axis.get_right(), DL, MED_SMALL_BUFF)
        y_label.next_to(axes.y_axis.get_top(), DR, MED_SMALL_BUFF)
        for label in labels:
            label.shift_onto_screen()
        return labels

    def get_phase_space_point(self):
        ps_point = self.ps_point = VectorizedPoint()
        ps_point.move_to(self.ds_to_point(
            self.block1.distance,
            self.block2.distance + self.block2.width
        ))
        self.tie_blocks_to_ps_point()
        return ps_point

    def get_phase_space_x_line(self):
        def get_x_line():
            origin = self.axes.coords_to_point(0, 0)
            point = self.ps_point.get_location()
            y_axis_point = np.array(origin)
            y_axis_point[1] = point[1]
            return DashedLine(
                y_axis_point, point,
                color=GREEN,
                stroke_width=2,
            )
        self.x_line = updating_mobject_from_func(get_x_line)
        return self.x_line

    def get_phase_space_y_line(self):
        def get_y_line():
            origin = self.axes.coords_to_point(0, 0)
            point = self.ps_point.get_location()
            x_axis_point = np.array(origin)
            x_axis_point[0] = point[0]
            return DashedLine(
                x_axis_point, point,
                color=RED,
                stroke_width=2,
            )
        self.y_line = updating_mobject_from_func(get_y_line)
        return self.y_line

    def get_phase_space_dot(self):
        self.ps_dot = ps_dot = Dot(**self.ps_dot_config)
        ps_dot.add_updater(lambda m: m.move_to(self.ps_point))
        return ps_dot

    def get_d_label(self, n, get_d):
        label = VGroup(
            TexMobject("d_{}".format(n), "="),
            DecimalNumber(),
        )
        color = GREEN if n == 1 else RED
        label[0].set_color_by_tex("d_", color)
        label.scale(0.7)
        label.set_stroke(BLACK, 3, background=True)

        def update_value(label):
            lhs, rhs = label
            rhs.set_value(get_d())
            rhs.next_to(
                lhs, RIGHT, SMALL_BUFF,
                aligned_edge=DOWN,
            )
        label.add_updater(update_value)
        return label

    def get_phase_space_d_label(self, n, get_d, line, vect):
        label = self.get_d_label(n, get_d)
        label.add_updater(
            lambda m: m.next_to(line, vect, SMALL_BUFF)
        )
        return label

    def get_phase_space_d1_label(self):
        self.ps_d1_label = self.get_phase_space_d_label(
            1, self.get_d1, self.x_line, UP,
        )
        return self.ps_d1_label

    def get_phase_space_d2_label(self):
        self.ps_d2_label = self.get_phase_space_d_label(
            2, self.get_d2, self.y_line, RIGHT,
        )
        return self.ps_d2_label

    def get_d_brace(self, get_right_point):
        line = Line(LEFT, RIGHT).set_width(6)

        def get_brace():
            right_point = get_right_point()
            left_point = np.array(right_point)
            left_point[0] = self.wall_x
            line.put_start_and_end_on(left_point, right_point)
            return Brace(line, UP, buff=SMALL_BUFF)

        brace = updating_mobject_from_func(get_brace)
        return brace

    def get_d1_brace(self):
        self.d1_brace = self.get_d_brace(
            lambda: self.block1.get_corner(UL)
        )
        return self.d1_brace

    def get_d2_brace(self):
        self.d2_brace = self.get_d_brace(
            lambda: self.block2.get_corner(UR)
        )
        # self.flip_brace_nip()
        return self.d2_brace

    def flip_brace_nip(self, brace):
        nip_index = (len(brace) // 2) - 1
        nip = brace[nip_index:nip_index + 2]
        rect = brace[nip_index - 1]
        center = rect.get_center()
        center[0] = nip.get_center()[0]
        nip.rotate(PI, about_point=center)

    def get_brace_d_label(self, n, get_d, brace, vect, buff):
        label = self.get_d_label(n, get_d)
        label.add_updater(
            lambda m: m.next_to(brace, vect, buff)
        )
        return label

    def get_d1_label(self):
        self.d1_label = self.get_brace_d_label(
            1, self.get_d1, self.d1_brace, UP, SMALL_BUFF,
        )
        return self.d1_label

    def get_d2_label(self):
        self.d2_label = self.get_brace_d_label(
            2, self.get_d2, self.d2_brace, UP, 0
        )
        return self.d2_label

    def get_d1_eq_d2_line(self):
        start = self.ds_to_point(0, 0)
        end = self.ds_to_point(15, 15)
        line = self.d1_eq_d2_line = self.mirror_line_class(start, end)
        line.set_style(**self.mirror_line_style)
        line.set_color(PINK)
        return self.d1_eq_d2_line

    def get_d1_eq_d2_label(self):
        label = TexMobject("d1 = d2")
        label.scale(0.75)
        line = self.d1_eq_d2_line
        point = interpolate(
            line.get_start(), line.get_end(),
            0.7,
        )
        label.next_to(point, DR, SMALL_BUFF)
        label.set_stroke(BLACK, 3, background=True)
        label.match_color(line)
        self.d1_eq_d2_label = label
        return label

    def get_d2_eq_w2_line(self):
        w2 = self.block2.width
        start = self.ds_to_point(0, w2)
        end = self.ds_to_point(30, w2)
        self.d2_eq_w2_line = self.mirror_line_class(start, end)
        self.d2_eq_w2_line.set_style(**self.mirror_line_style)
        return self.d2_eq_w2_line

    def get_d2_eq_w2_label(self):
        label = TexMobject("d2 = \\text{block width}")
        label.scale(0.75)
        label.next_to(self.d2_eq_w2_line, UP, SMALL_BUFF)
        label.to_edge(RIGHT, buff=MED_SMALL_BUFF)
        self.d2_eq_w2_label = label
        return label

    def get_time_tracker(self):
        time_tracker = self.time_tracker = ValueTracker(0)
        time_tracker.add_updater(
            lambda m, dt: m.increment_value(dt)
        )
        return time_tracker


class IntroducePositionPhaseSpace(PositionPhaseSpaceScene):
    CONFIG = {
        "rescale_coordinates": False,
        "block1_config": {
            "velocity": 1.5,
        },
        "slide_wait_time": 30,
    }

    def setup(self):
        super().setup()
        self.add(
            self.floor,
            self.wall,
            self.blocks,
            self.axes,
        )

    def construct(self):
        self.show_coordinates()
        self.show_xy_line()
        self.let_process_play_out()
        self.show_w2_line()

    def show_coordinates(self):
        ps_point = self.ps_point
        axes = self.axes

        self.play(Write(axes.added_lines))
        self.play(FadeInFromLarge(self.ps_dot, scale_factor=10))
        self.play(
            ShowCreation(self.x_line),
            GrowFromPoint(
                self.d1_brace,
                self.d1_brace.get_left(),
            ),
            Indicate(axes.labels[0]),
        )
        self.play(
            FadeInFromDown(self.ps_d1_label),
            FadeInFromDown(self.d1_label),
        )
        self.play(ps_point.shift, 0.5 * LEFT)
        self.play(ps_point.shift, 0.5 * RIGHT)
        self.wait()
        self.play(
            ShowCreation(self.y_line),
            GrowFromPoint(
                self.d2_brace,
                self.d2_brace.get_left(),
            ),
            Indicate(axes.labels[1]),
        )
        self.play(
            FadeInFromDown(self.ps_d2_label),
            FadeInFromDown(self.d2_label),
        )
        self.play(ps_point.shift, 0.5 * UP)
        self.play(ps_point.shift, 0.5 * DOWN)
        self.wait()
        self.play(Rotating(
            ps_point,
            about_point=ps_point.get_location() + 0.5 * RIGHT,
            run_time=3,
            rate_func=smooth,
        ))
        self.wait()

    def show_xy_line(self):
        ps_point = self.ps_point
        ps_point.save_state()
        d1, d2 = self.point_to_ds(ps_point.get_location())

        xy_line = self.d1_eq_d2_line
        xy_label = self.d1_eq_d2_label
        xy_line.set_stroke(YELLOW)
        xy_label.set_color(YELLOW)

        self.play(
            ShowCreation(xy_line),
            Write(xy_label),
        )
        self.play(
            ps_point.move_to, self.ds_to_point(d2, d2),
            run_time=3
        )
        self.wait()
        for d in [3, 7]:
            self.play(
                ps_point.move_to, self.ds_to_point(d, d),
                run_time=2
            )
            self.wait()
        self.play(ps_point.restore)
        self.wait()

    def let_process_play_out(self):
        self.begin_sliding()
        sliding_trajectory = self.get_continually_building_trajectory()
        self.add(sliding_trajectory, self.ps_dot)
        self.wait(self.slide_wait_time)
        self.end_sliding()

    def show_w2_line(self):
        line = self.d2_eq_w2_line
        label = self.d2_eq_w2_label

        self.play(ShowCreation(line))
        self.play(FadeInFromDown(label))
        self.wait()


class SpecialShowPassingFlash(ShowPassingFlash):
    CONFIG = {
        "max_time_width": 0.1,
    }

    def get_bounds(self, alpha):
        tw = self.time_width
        max_tw = self.max_time_width
        upper = interpolate(0, 1 + max_tw, alpha)
        lower = upper - tw
        upper = min(upper, 1)
        lower = max(lower, 0)
        return (lower, upper)


class EqualMassCase(PositionPhaseSpaceScene):
    CONFIG = {
        "block1_config": {
            "mass": 1,
            "width": 1,
            "velocity": 1.5,
        },
        "rescale_coordinates": False,
    }

    def setup(self):
        super().setup()
        self.add(
            self.floor,
            self.wall,
            self.blocks,
            self.axes,
            self.ps_dot,
            self.x_line,
            self.y_line,
            self.ps_d1_label,
            self.ps_d2_label,
            self.d1_eq_d2_line,
            self.d1_eq_d2_label,
            self.d2_eq_w2_line,
            self.d2_eq_w2_label,
        )

    def construct(self):
        self.show_same_mass()
        self.show_first_point()
        self.up_to_first_collision()
        self.up_to_second_collision()
        self.up_to_third_collision()

        self.fade_distance_indicators()
        self.show_beam_bouncing()

    def show_same_mass(self):
        blocks = self.blocks
        self.play(LaggedStart(
            Indicate, blocks,
            lag_ratio=0.8,
            run_time=1,
        ))

    def show_first_point(self):
        ps_dot = self.ps_dot
        ps_point = self.ps_point
        d1, d2 = self.get_ds()

        self.play(FocusOn(ps_dot))
        self.play(ShowCreationThenFadeOut(
            Circle(color=RED).replace(ps_dot).scale(2),
            run_time=1
        ))
        self.wait()
        self.play(
            ps_point.move_to, self.ds_to_point(d1 - 1, d2),
            rate_func=wiggle,
            run_time=3,
        )
        # self.play(ps_point.move_to, self.ds_to_point(d1, d2))
        self.wait()

    def up_to_first_collision(self):
        ps_point = self.ps_point
        d1, d2 = self.get_ds()
        block1 = self.block1
        block2 = self.block2
        xy_line = self.d1_eq_d2_line
        xy_line_label = self.d1_eq_d2_label

        block_arrow = Vector(LEFT, color=RED)
        block_arrow.block = block1
        block_arrow.add_updater(
            lambda m: m.shift(
                m.block.get_center() - m.get_start()
            )
        )
        ps_arrow = Vector(LEFT, color=RED)
        ps_arrow.next_to(ps_point, DL, buff=SMALL_BUFF)

        block_labels = VGroup(block1.label, block2.label)
        block_label_copies = block_labels.copy()

        def update_bl_copies(bl_copies):
            for bc, b in zip(bl_copies, block_labels):
                bc.move_to(b)
        block_label_copies.add_updater(update_bl_copies)

        trajectory = self.get_continually_building_trajectory()

        self.add(block_arrow, ps_arrow, block_label_copies)
        self.play(
            GrowArrow(block_arrow),
            GrowArrow(ps_arrow),
        )
        self.add(trajectory)
        self.play(self.get_ps_point_change_anim(d2, d2))
        block_arrow.block = block2
        ps_arrow.rotate(90 * DEGREES)
        ps_arrow.next_to(ps_point, DR, SMALL_BUFF)
        self.add_sound(self.clack_sound)
        self.play(
            Flash(ps_point),
            Flash(block1.get_left()),
            self.get_ps_point_change_anim(d2, d2 - 1)
        )
        self.play(
            ShowPassingFlash(
                xy_line.copy().set_stroke(YELLOW, 3)
            ),
            Indicate(xy_line_label),
        )

        trajectory.suspend_updating()
        self.wait()

        self.ps_arrow = ps_arrow
        self.block_arrow = block_arrow

    def up_to_second_collision(self):
        trajectory = self.continually_building_trajectory
        ps_point = self.ps_point
        ps_arrow = self.ps_arrow
        block_arrow = self.block_arrow

        d1, d2 = self.get_ds()
        w2 = self.block2.get_width()

        trajectory.resume_updating()
        self.play(self.get_ps_point_change_anim(d1, w2))
        block_arrow.rotate(PI)
        ps_arrow.rotate(PI)
        ps_arrow.next_to(ps_point, UR, SMALL_BUFF)
        self.add_sound(self.clack_sound)
        self.play(
            Flash(self.block2.get_left()),
            Flash(ps_point),
            self.get_ps_point_change_anim(d1, w2 + 1)
        )

        trajectory.suspend_updating()
        self.wait()

    def up_to_third_collision(self):
        trajectory = self.continually_building_trajectory
        ps_point = self.ps_point
        ps_arrow = self.ps_arrow
        block_arrow = self.block_arrow
        d1, d2 = self.get_ds()

        trajectory.resume_updating()
        self.play(self.get_ps_point_change_anim(d1, d1))
        block_arrow.block = self.block1
        ps_arrow.rotate(-90 * DEGREES)
        ps_arrow.next_to(ps_point, DR, SMALL_BUFF)
        self.add_sound(self.clack_sound)
        self.play(
            Flash(self.block2.get_left()),
            Flash(ps_point.get_location()),
            self.get_ps_point_change_anim(d1 + 10, d1)
        )
        trajectory.suspend_updating()

    def fade_distance_indicators(self):
        trajectory = self.continually_building_trajectory
        self.play(
            trajectory.set_stroke, {"width": 1},
            *map(FadeOut, [
                self.ps_arrow,
                self.block_arrow,
                self.x_line,
                self.y_line,
                self.ps_d1_label,
                self.ps_d2_label,
            ])
        )
        trajectory.clear_updaters()

    def show_beam_bouncing(self):
        d1, d2 = self.get_ds()
        d1 = int(d1)
        d2 = int(d2)
        w2 = self.block2.get_width()
        ps_point = self.ps_point

        points = []
        while d1 > d2:
            points.append(self.ds_to_point(d1, d2))
            d1 -= 1
        while d2 >= int(w2):
            points.append(self.ds_to_point(d1, d2))
            d2 -= 1
        points += list(reversed(points))[1:]
        trajectory = VMobject()
        trajectory.set_points_as_corners(points)
        flashes = [
            SpecialShowPassingFlash(
                trajectory.copy().set_stroke(YELLOW, width=6 - n),
                time_width=(0.01 * n),
                max_time_width=0.05,
                remover=True
            )
            for n in np.arange(0, 6, 0.25)
        ]
        flash_mob = flashes[0].mobject  # Lol

        def update_ps_point_from_flas_mob(ps_point):
            if len(flash_mob.points) > 0:
                ps_point.move_to(flash_mob.points[-1])
            else:
                ps_point.move_to(trajectory.points[0])

        # Mirror words
        xy_line = self.d1_eq_d2_line
        w2_line = self.d2_eq_w2_line
        lines = VGroup(xy_line, w2_line)
        for line in lines:
            word = TextMobject("Mirror")
            word.next_to(ORIGIN, UP, SMALL_BUFF)
            word.rotate(line.get_angle(), about_point=ORIGIN)
            word.shift(line.get_center())
            line.word = word

        for line in lines:
            line.set_stroke(LIGHT_GREY)
            line.set_sheen(1, LEFT)
            self.play(
                Write(line.word),
                line.set_sheen, 1, RIGHT,
                line.set_stroke, {"width": 2},
                run_time=1,
            )

        # TODO, clacks?
        for x in range(3):
            self.play(
                UpdateFromFunc(
                    ps_point,
                    update_ps_point_from_flas_mob,
                ),
                *flashes,
                run_time=3,
                rate_func=None,
            )
            self.wait()


class FailedAngleRelation(PositionPhaseSpaceScene):
    CONFIG = {
        "block1_config": {
            "distance": 10,
            "velocity": -1.5,
        },
        "block2_config": {
            "distance": 5,
        },
        "rescale_coordinates": False,
    }

    def setup(self):
        super().setup()
        self.add(
            self.floor,
            self.wall,
            self.blocks,
            self.axes,
            self.ps_dot,
            self.x_line,
            self.y_line,
            self.d1_eq_d2_line,
            self.d1_eq_d2_label,
            self.d2_eq_w2_line,
            self.d2_eq_w2_label,
        )

    def construct(self):
        self.show_first_collision()
        self.show_angles()

    def show_first_collision(self):
        ps_point = self.ps_point
        trajectory = self.get_continually_building_trajectory()
        trajectory.set_stroke(YELLOW, 2)

        self.add(ps_point, trajectory)
        self.begin_sliding()
        self.wait_until(lambda: self.get_ds()[1] < 2)
        self.end_sliding()
        trajectory.suspend_updating()

        self.trajectory = trajectory

    def show_angles(self):
        trajectory = self.trajectory
        arcs = self.get_arcs(trajectory)
        equation = self.get_word_equation()
        equation.next_to(
            trajectory.points[0], UR, MED_SMALL_BUFF,
            index_of_submobject_to_align=0,
        )

        for arc in arcs:
            line = Line(ORIGIN, RIGHT)
            line.set_stroke(WHITE, 2)
            line.rotate(arc.start_angle)
            line.shift(arc.arc_center - line.get_start())
            arc.line = line

        self.play(LaggedStart(
            FadeInFromDown,
            VGroup(*reversed(equation)),
            lag_ratio=0.75,
        ))
        for arc in arcs:
            # TODO, add arrows
            self.play(
                ShowCreation(arc),
                arc.line.rotate, arc.angle,
                {"about_point": arc.line.get_start()},
                UpdateFromAlphaFunc(
                    arc.line,
                    lambda m, a: m.set_stroke(
                        opacity=(there_and_back(a)**0.5)
                    )
                ),
                run_time=2,
            )

    #
    def get_arcs(self, trajectory):
        p0, p1, p2 = trajectory.get_anchors()[1:4]
        arc_config = {
            "stroke_color": WHITE,
            "stroke_width": 2,
            "radius": 0.5,
            "arc_center": p1,
        }
        arc1 = Arc(
            start_angle=0,
            angle=45 * DEGREES,
            **arc_config
        )
        a2_start = angle_of_vector(DL)
        a2_angle = angle_between_vectors((p2 - p1), DL)
        arc2 = Arc(
            start_angle=a2_start,
            angle=a2_angle,
            **arc_config
        )
        return VGroup(arc1, arc2)

    def get_word_equation(self):
        result = VGroup(
            TextMobject("Angle of incidence"),
            TexMobject("\\ne").rotate(90 * DEGREES),
            TextMobject("Angle of refraction")
        )
        result.arrange_submobjects(DOWN)
        return result
