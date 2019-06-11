from manimlib.imports import *
from old_projects.clacks.question import Block
from old_projects.clacks.question import Wall
from old_projects.clacks.question import ClackFlashes


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
            "velocity": -1,
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
        "ps_d2_label_vect": RIGHT,
        "ps_x_line_config": {
            "color": GREEN,
            "stroke_width": 2,
        },
        "ps_y_line_config": {
            "color": RED,
            "stroke_width": 2,
        },
        "clack_sound": "clack",
        "mirror_line_class": Line,
        "mirror_line_style": {
            "stroke_color": WHITE,
            "stroke_width": 1,
        },
        "d1_eq_d2_line_color": MAROON_B,
        "d1_eq_d2_tex": "d1 = d2",
        "trajectory_style": {
            "stroke_color": YELLOW,
            "stroke_width": 2,
        },
        "ps_velocity_vector_length": 0.75,
        "ps_velocity_vector_config": {
            "color": PINK,
            "rectangular_stem_width": 0.025,
            "tip_length": 0.15,
        },
        "block_velocity_vector_length_multiple": 2,
        "block_velocity_vector_config": {
            "color": PINK,
        },
    }

    def setup(self):
        self.total_sliding_time = 0
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
        start_d1, start_d2 = self.get_ds()
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

    def tie_ps_point_to_time_tracker(self):
        if not hasattr(self, "sliding_time_tracker"):
            self.sliding_time_tracker = self.get_time_tracker()

        def update_ps_point(p):
            time = self.sliding_time_tracker.get_value()
            ds = self.time_to_ds(time)
            p.move_to(self.ds_to_point(*ds))

        self.ps_point.add_updater(update_ps_point)
        self.add(self.sliding_time_tracker, self.ps_point)

    def add_clack_flashes(self):
        if hasattr(self, "flash_anims"):
            self.add(*self.flash_anims)
        else:
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
            self.flash_anims = [self.block_flashes, self.ps_flashes]
            for anim in self.flash_anims:
                anim.get_time = self.sliding_time_tracker.get_value
            self.add(*self.flash_anims)

    def get_continually_building_trajectory(self):
        trajectory = VMobject()
        self.trajectory = trajectory
        trajectory.set_style(**self.trajectory_style)

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

    def begin_sliding(self, show_trajectory=True):
        self.tie_ps_point_to_time_tracker()
        self.add_clack_flashes()
        if show_trajectory:
            if hasattr(self, "trajectory"):
                self.trajectory.resume_updating()
            else:
                self.add(self.get_continually_building_trajectory())

    def end_sliding(self):
        self.update_mobjects(dt=0)
        self.ps_point.clear_updaters()
        if hasattr(self, "sliding_time_tracker"):
            self.remove(self.sliding_time_tracker)
        if hasattr(self, "flash_anims"):
            self.remove(*self.flash_anims)
        if hasattr(self, "trajectory"):
            self.trajectory.suspend_updating()
        old_total_sliding_time = self.total_sliding_time
        new_total_sliding_time = self.sliding_time_tracker.get_value()
        self.total_sliding_time = new_total_sliding_time
        for time in self.clack_times:
            if old_total_sliding_time < time < new_total_sliding_time:
                offset = time - new_total_sliding_time
                self.add_sound(
                    "clack",
                    time_offset=offset,
                )

    def slide(self, time, stop_condition=None):
        self.begin_sliding()
        self.wait(time, stop_condition)
        self.end_sliding()

    def slide_until(self, stop_condition, max_time=60):
        self.slide(max_time, stop_condition=stop_condition)

    def get_ps_point_change_anim(self, d1, d2, **added_kwargs):
        b1 = self.block1
        ps_speed = np.sqrt(b1.mass) * abs(b1.velocity)
        curr_d1, curr_d2 = self.get_ds()
        distance = get_norm([curr_d1 - d1, curr_d2 - d2])

        # Default
        kwargs = {
            "run_time": (distance / ps_speed),
            "rate_func": linear,
        }
        kwargs.update(added_kwargs)
        return ApplyMethod(
            self.ps_point.move_to,
            self.ds_to_point(d1, d2),
            **kwargs
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
            block.label.set_stroke(WHITE, 1, background=True)
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
        x_mult = y_mult = 1
        if self.rescale_coordinates:
            x_mult = np.sqrt(self.block1.mass)
            y_mult = np.sqrt(self.block2.mass)
        y_lines = VGroup(*[
            Line(
                c2p(0, 0), c2p(0, axes.y_max * y_mult + 1),
            ).move_to(c2p(x, 0), DOWN)
            for x in np.arange(0, axes.x_max) * x_mult
        ])
        x_lines = VGroup(*[
            Line(
                c2p(0, 0), c2p(axes.x_max * x_mult, 0),
            ).move_to(c2p(0, y), LEFT)
            for y in np.arange(0, axes.y_max) * y_mult
        ])
        line_groups = VGroup(x_lines, y_lines)
        for lines in line_groups:
            lines.set_stroke(BLUE, 1, 0.5)
            lines[1::2].set_stroke(width=0.5, opacity=0.25)
        return line_groups

    def get_axes_labels(self, axes, with_sqrts=None):
        if with_sqrts is None:
            with_sqrts = self.rescale_coordinates
        x_label = TexMobject("x", "=", "d_1")
        y_label = TexMobject("y", "=", "d_2")
        labels = VGroup(x_label, y_label)
        if with_sqrts:
            additions = map(TexMobject, [
                "\\sqrt{m_1}", "\\sqrt{m_2}"
            ])
            for label, addition in zip(labels, additions):
                addition.move_to(label[2], DL)
                label[2].next_to(
                    addition, RIGHT, SMALL_BUFF,
                    aligned_edge=DOWN
                )
                addition[2:].set_color(BLUE)
                label.submobjects.insert(2, addition)
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
                **self.ps_x_line_config,
            )
        self.x_line = always_redraw(get_x_line)
        return self.x_line

    def get_phase_space_y_line(self):
        def get_y_line():
            origin = self.axes.coords_to_point(0, 0)
            point = self.ps_point.get_location()
            x_axis_point = np.array(origin)
            x_axis_point[0] = point[0]
            return DashedLine(
                x_axis_point, point,
                **self.ps_y_line_config,
            )
        self.y_line = always_redraw(get_y_line)
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
            2, self.get_d2, self.y_line,
            self.ps_d2_label_vect,
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

        brace = always_redraw(get_brace)
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
        line.set_color(self.d1_eq_d2_line_color)
        return self.d1_eq_d2_line

    def get_d1_eq_d2_label(self):
        label = TexMobject(self.d1_eq_d2_tex)
        label.scale(0.75)
        line = self.d1_eq_d2_line
        point = interpolate(
            line.get_start(), line.get_end(),
            0.7,
        )
        label.next_to(point, DR, SMALL_BUFF)
        label.match_color(line)
        label.set_stroke(BLACK, 5, background=True)
        self.d1_eq_d2_label = label
        return label

    def get_d2_eq_w2_line(self):
        w2 = self.block2.width
        start = self.ds_to_point(0, w2)
        end = np.array(start)
        end[0] = FRAME_WIDTH / 2
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

    def get_time_tracker(self, time=0):
        time_tracker = self.time_tracker = ValueTracker(time)
        time_tracker.add_updater(
            lambda m, dt: m.increment_value(dt)
        )
        return time_tracker

    # Things associated with velocity
    def get_ps_velocity_vector(self, trajectory):
        vector = Vector(
            self.ps_velocity_vector_length * LEFT,
            **self.ps_velocity_vector_config,
        )

        def update_vector(v):
            anchors = trajectory.get_anchors()
            index = len(anchors) - 2
            vect = np.array(ORIGIN)
            while get_norm(vect) == 0 and index > 0:
                p0, p1 = anchors[index:index + 2]
                vect = p1 - p0
                index -= 1
            angle = angle_of_vector(vect)
            point = self.ps_point.get_location()
            v.set_angle(angle)
            v.shift(point - v.get_start())
        vector.add_updater(update_vector)
        self.ps_velocity_vector = vector
        return vector

    def get_block_velocity_vectors(self, ps_vect):
        blocks = self.blocks
        vectors = VGroup(*[
            Vector(LEFT, **self.block_velocity_vector_config)
            for x in range(2)
        ])
        # TODO: Put in config
        vectors[0].set_color(GREEN)
        vectors[1].set_color(RED)

        def update_vectors(vs):
            v_2d = ps_vect.get_vector()[:2]
            v_2d *= self.block_velocity_vector_length_multiple
            for v, coord, block in zip(vs, v_2d, blocks):
                v.put_start_and_end_on(ORIGIN, coord * RIGHT)
                start = block.get_edge_center(v.get_vector())
                v.shift(start)
        vectors.add_updater(update_vectors)

        self.block_velocity_vectors = vectors
        return vectors


class IntroducePositionPhaseSpace(PositionPhaseSpaceScene):
    CONFIG = {
        "rescale_coordinates": False,
        "d1_eq_d2_tex": "x = y",
        "block1_config": {
            "velocity": 1.5,
        },
        "slide_wait_time": 12,
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

    def show_w2_line(self):
        line = self.d2_eq_w2_line
        label = self.d2_eq_w2_label

        self.play(ShowCreation(line))
        self.play(FadeInFromDown(label))
        self.wait(self.slide_wait_time)
        self.end_sliding()
        self.wait(self.slide_wait_time)


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
        "d1_eq_d2_tex": "x = y",
    }

    def setup(self):
        super().setup()
        self.add(
            self.floor,
            self.wall,
            self.blocks,
            self.axes,
            self.d1_eq_d2_line,
            self.d1_eq_d2_label,
            self.d2_eq_w2_line,
            self.d2_eq_w2_label,
            self.ps_dot,
            self.x_line,
            self.y_line,
            self.ps_d1_label,
            self.ps_d2_label,
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
        self.play(LaggedStartMap(
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
        trajectory = self.trajectory
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
        trajectory = self.trajectory
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
        trajectory = self.trajectory
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
        # w2 = self.block2.get_width()
        ps_point = self.ps_point

        points = []
        while d1 > d2:
            points.append(self.ds_to_point(d1, d2))
            d1 -= 1
        while d2 >= 1:
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
                rate_func=linear,
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
        "trajectory_style": {
            "stroke_width": 2,
        }
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
        self.slide_until(lambda: self.get_ds()[1] < 2)

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

        arc1, arc2 = arcs
        arc1.arrow = Arrow(
            equation[0].get_left(), arc1.get_right(),
            buff=SMALL_BUFF,
            color=WHITE,
            path_arc=0,
        )
        arc2.arrow = Arrow(
            equation[2].get_corner(DL),
            arc2.get_left(),
            path_arc=-120 * DEGREES,
            buff=SMALL_BUFF,
        )
        arc2.arrow.pointwise_become_partial(arc.arrow, 0, 0.95)

        arc1.word = equation[0]
        arc2.word = equation[1:]

        for arc in arcs:
            self.play(
                FadeInFrom(arc.word, LEFT),
                GrowArrow(arc.arrow, path_arc=arc.arrow.path_arc),
            )
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
            TextMobject("Angle of reflection")
        )
        result.arrange(DOWN)
        result.set_stroke(BLACK, 5, background=True)
        return result


class UnscaledPositionPhaseSpaceMass10(FailedAngleRelation):
    CONFIG = {
        "block1_config": {
            "mass": 10
        },
        "wait_time": 25,
    }

    def construct(self):
        self.slide(self.wait_time)


class UnscaledPositionPhaseSpaceMass100(UnscaledPositionPhaseSpaceMass10):
    CONFIG = {
        "block1_config": {
            "mass": 100
        }
    }


class RescaleCoordinates(PositionPhaseSpaceScene, MovingCameraScene):
    CONFIG = {
        "rescale_coordinates": False,
        "ps_d2_label_vect": LEFT,
        "axes_center": 6 * LEFT + 0.65 * DOWN,
        "block1_config": {"distance": 7},
        "wait_time": 30,
    }

    def setup(self):
        PositionPhaseSpaceScene.setup(self)
        MovingCameraScene.setup(self)
        self.add(
            self.floor,
            self.wall,
            self.blocks,
            self.axes,
            self.d1_eq_d2_line,
            self.d1_eq_d2_label,
            self.d2_eq_w2_line,
            self.ps_dot,
            self.x_line,
            self.y_line,
            self.ps_d1_label,
            self.ps_d2_label,
            self.d1_brace,
            self.d2_brace,
            self.d1_label,
            self.d2_label,
        )

    def construct(self):
        self.show_rescaling()
        self.comment_on_ugliness()
        self.put_into_frame()

    def show_rescaling(self):
        axes = self.axes
        blocks = self.blocks
        to_stretch = VGroup(
            axes.added_lines,
            self.d1_eq_d2_line,
            self.ps_point,
        )
        m1 = self.block1.mass
        new_axes_labels = self.get_axes_labels(axes, with_sqrts=True)

        # Show label
        def show_label(index, block, vect):
            self.play(
                ShowCreationThenFadeAround(axes.labels[index])
            )
            self.play(
                Transform(
                    axes.labels[index],
                    VGroup(
                        *new_axes_labels[index][:2],
                        new_axes_labels[index][3]
                    ),
                ),
                GrowFromCenter(new_axes_labels[index][2])
            )
            group = VGroup(
                new_axes_labels[index][2][-2:].copy(),
                TexMobject("="),
                block.label.copy(),
            )
            group.generate_target()
            group.target.arrange(RIGHT, buff=SMALL_BUFF)
            group.target.next_to(block, vect)
            group[1].scale(0)
            group[1].move_to(group.target[1])
            group.target[2].set_fill(WHITE)
            group.target[2].set_stroke(width=0, background=True)
            self.play(MoveToTarget(
                group,
                rate_func=there_and_back_with_pause,
                run_time=3
            ))
            self.remove(group)
            self.wait()

        show_label(0, self.block1, RIGHT)

        # The stretch
        blocks.suspend_updating()
        self.play(
            ApplyMethod(
                to_stretch.stretch, np.sqrt(m1), 0,
                {"about_point": axes.coords_to_point(0, 0)},
            ),
            self.d1_eq_d2_label.shift, 6 * RIGHT,
            run_time=2,
        )
        self.rescale_coordinates = True
        blocks.resume_updating()
        self.wait()

        # Show wiggle
        d1, d2 = self.get_ds()
        for new_d1 in [d1 - 2, d1]:
            self.play(self.get_ps_point_change_anim(
                new_d1, d2,
                rate_func=smooth,
                run_time=2,
            ))
        self.wait()

        # Change y-coord
        show_label(1, self.block2, LEFT)

        axes.remove(axes.labels)
        self.remove(axes.labels)
        axes.labels = new_axes_labels
        axes.add(axes.labels)
        self.add(axes)

    def comment_on_ugliness(self):
        axes = self.axes

        randy = Randolph(height=1.7)
        randy.flip()
        randy.next_to(self.d2_eq_w2_line, UP, buff=0)
        randy.to_edge(RIGHT)
        randy.change("sassy")
        randy.save_state()
        randy.fade(1)
        randy.change("plain")

        self.play(Restore(randy))
        self.play(
            PiCreatureSays(
                randy, "Hideous!",
                bubble_kwargs={"height": 1.5, "width": 2},
                target_mode="angry",
                look_at_arg=axes.labels[0]
            )
        )
        self.play(randy.look_at, axes.labels[1])
        self.play(Blink(randy))
        self.play(
            RemovePiCreatureBubble(
                randy, target_mode="confused"
            )
        )
        self.play(Blink(randy))
        self.play(randy.look_at, axes.labels[0])
        self.wait()
        self.play(FadeOut(randy))

    def put_into_frame(self):
        rect = ScreenRectangle(height=FRAME_HEIGHT + 10)
        inner_rect = ScreenRectangle(height=FRAME_HEIGHT)
        rect.add_subpath(inner_rect.points[::-1])
        rect.set_fill("#333333", opacity=1)
        frame = self.camera_frame

        self.begin_sliding()
        self.add(rect)
        self.play(
            frame.scale, 1.5,
            {"about_point": frame.get_bottom() + UP},
            run_time=2,
        )
        self.wait(self.wait_time)
        self.end_sliding()

    #
    def get_ds(self):
        if self.rescale_coordinates:
            return super().get_ds()
        return (
            self.block1_config["distance"],
            self.block2_config["distance"],
        )


class RescaleCoordinatesMass16(RescaleCoordinates):
    CONFIG = {
        "block1_config": {
            "mass": 16,
            "distance": 10,
        },
        "rescale_coordinates": True,
        "wait_time": 20,
    }

    def construct(self):
        self.put_into_frame()


class RescaleCoordinatesMass64(RescaleCoordinatesMass16):
    CONFIG = {
        "block1_config": {
            "mass": 64,
            "distance": 6,
        },
        "block2_config": {"distance": 3},
    }


class RescaleCoordinatesMass100(RescaleCoordinatesMass16):
    CONFIG = {
        "block1_config": {
            "mass": 100,
            "distance": 6,
            "velocity": 0.5,
        },
        "block2_config": {"distance": 2},
        "wait_time": 25,
    }


class IntroduceVelocityVector(PositionPhaseSpaceScene, MovingCameraScene):
    CONFIG = {
        "zoom": True,
        "ps_x_line_config": {
            "color": WHITE,
            "stroke_width": 1,
            "stroke_opacity": 0.5,
        },
        "ps_y_line_config": {
            "color": WHITE,
            "stroke_width": 1,
            "stroke_opacity": 0.5,
        },
        "axes_center": 6 * LEFT + 0.65 * DOWN,
        "slide_time": 20,
        "new_vect_config": {
            "tip_length": 0.1,
            "rectangular_stem_width": 0.02,
        }
    }

    def setup(self):
        MovingCameraScene.setup(self)
        PositionPhaseSpaceScene.setup(self)
        self.add(
            self.floor,
            self.wall,
            self.blocks,
            self.axes,
            self.d1_eq_d2_line,
            self.d1_eq_d2_label,
            self.d2_eq_w2_line,
            self.x_line,
            self.y_line,
            self.ps_dot,
        )

    def construct(self):
        self.show_velocity_vector()
        self.contrast_with_physical_velocities()
        self.zoom_in_on_vector()
        self.break_down_components()
        self.zoom_out()
        self.relate_x_dot_y_dot_to_v1_v2()
        self.calculate_magnitude()
        self.let_process_play_out()

    def show_velocity_vector(self):
        self.slide(2)
        ps_vect = self.get_ps_velocity_vector(self.trajectory)
        self.play(GrowArrow(ps_vect))
        self.play(ShowCreationThenFadeAround(ps_vect))
        self.wait()

    def contrast_with_physical_velocities(self):
        ps_vect = self.ps_velocity_vector
        block_vectors = self.get_block_velocity_vectors(ps_vect)

        self.play(LaggedStartMap(GrowArrow, block_vectors))
        self.play(Rotating(
            ps_vect,
            angle=TAU,
            about_point=ps_vect.get_start(),
            run_time=5,
            rate_func=smooth,
        ))
        self.wait()
        self.slide_until(lambda: self.get_d2() < 2.5)

    def zoom_in_on_vector(self):
        if not self.zoom:
            self.wait(3)
            return
        ps_vect = self.ps_velocity_vector
        new_vect = Arrow(
            ps_vect.get_start(),
            ps_vect.get_end(),
            buff=0,
            **self.new_vect_config
        )
        new_vect.match_style(ps_vect)

        camera_frame = self.camera_frame
        camera_frame.save_state()
        point = self.ps_point.get_location()
        point += MED_SMALL_BUFF * DOWN
        self.play(
            camera_frame.scale, 0.25, {"about_point": point},
            Transform(ps_vect, new_vect),
            run_time=2,
        )
        self.wait()

    def break_down_components(self):
        # Create vectors
        ps_vect = self.ps_velocity_vector
        start = ps_vect.get_start()
        end = ps_vect.get_end()
        ul_corner = np.array(start)
        dr_corner = np.array(start)
        ul_corner[0] = end[0]
        dr_corner[1] = end[1]

        x_vect = Arrow(
            start, ul_corner,
            buff=0,
            **self.new_vect_config
        )
        y_vect = Arrow(
            start, dr_corner,
            buff=0,
            **self.new_vect_config
        )
        x_vect.set_fill(GREEN, opacity=0.75)
        y_vect.set_fill(RED, opacity=0.75)
        vects = VGroup(x_vect, y_vect)

        # Projection lines
        x_line, y_line = [
            DashedLine(
                ps_vect.get_end(),
                vect.get_end(),
                dash_length=0.01,
                color=vect.get_color(),
            )
            for vect in (x_vect, y_vect)
        ]
        self.projection_lines = VGroup(x_line, y_line)

        # Vector labels
        dx_label = TexMobject("\\frac{dx}{dt}")
        dy_label = TexMobject("\\frac{dy}{dt}")
        labels = VGroup(dx_label, dy_label)
        for label, arrow, direction in zip(labels, vects, [UP, RIGHT]):
            label.scale(0.25)
            buff = 0.25 * SMALL_BUFF
            label.next_to(arrow, direction, buff=buff)
        label.set_stroke(BLACK, 3, background=True)

        if not self.zoom:
            self.grow_labels(labels)

        self.play(
            TransformFromCopy(ps_vect, x_vect),
            ShowCreation(x_line),
        )
        self.play(FadeInFrom(dx_label, 0.25 * DOWN))
        self.wait()
        self.play(
            TransformFromCopy(ps_vect, y_vect),
            ShowCreation(y_line),
        )
        self.play(FadeInFrom(dy_label, 0.25 * LEFT))
        self.wait()

        # Ask about dx_dt
        randy = Randolph()
        randy.match_height(dx_label)
        randy.next_to(dx_label, LEFT, SMALL_BUFF)
        randy.change("confused", dx_label)
        randy.save_state()
        randy.fade(1)
        randy.change("plain")

        self.play(Restore(randy))
        self.play(WiggleOutThenIn(dx_label))
        self.play(Blink(randy))
        self.play(FadeOut(randy))

        self.derivative_labels = labels
        self.component_vectors = vects

    def zoom_out(self):
        if not self.zoom:
            self.wait(2)
            return
        labels = self.derivative_labels
        self.play(
            Restore(self.camera_frame),
            ApplyFunction(self.grow_labels, labels),
            run_time=2
        )

    def relate_x_dot_y_dot_to_v1_v2(self):
        derivative_labels = self.derivative_labels.copy()
        dx_label, dy_label = derivative_labels
        x_label, y_label = self.axes.labels
        m_part = x_label[2]
        block1 = self.block1
        block_vectors = self.block_velocity_vectors

        x_eq = x_label[1]
        dx_eq = TexMobject("=")
        dx_eq.next_to(
            x_eq, DOWN,
            buff=LARGE_BUFF,
            aligned_edge=RIGHT,
        )
        for label in derivative_labels:
            label.generate_target()
            label.target.scale(1.5)
        dx_label.target.next_to(dx_eq, LEFT)
        dx_rhs = TexMobject("\\sqrt{m_1}", "v_1")
        dx_rhs[0][2:].set_color(BLUE)
        dx_rhs[1].set_color(GREEN)
        dx_rhs.next_to(dx_eq, RIGHT)
        alt_v1 = dx_rhs[1].copy()

        self.play(ShowCreationThenFadeAround(x_label))
        self.play(MoveToTarget(dx_label))
        self.play(TransformFromCopy(x_eq, dx_eq))
        self.wait()
        self.play(
            VGroup(block1, m_part).shift, SMALL_BUFF * UP,
            rate_func=wiggle,
        )
        self.wait()
        self.d1_brace.update()
        self.d1_label.update()
        self.play(
            ShowCreationThenFadeAround(x_label[3]),
            FadeIn(self.d1_brace),
            FadeIn(self.d1_label),
        )
        self.wait()
        self.play(
            TransformFromCopy(x_label[3], dx_rhs[1]),
            TransformFromCopy(x_label[2], VGroup(dx_rhs[0])),
        )
        block_vectors.suspend_updating()
        self.play(alt_v1.next_to, block_vectors[0], UP, SMALL_BUFF)
        self.play(
            Rotate(
                block_vectors[0], 10 * DEGREES,
                about_point=block_vectors[0].get_start(),
                rate_func=wiggle,
                run_time=1,
            )
        )
        self.play(FadeOut(alt_v1))
        block_vectors.resume_updating()
        self.wait()

        # dy_label
        y_eq = y_label[1]
        dy_eq = TexMobject("=")
        dy_eq.next_to(y_eq, DOWN, LARGE_BUFF)
        dy_label.target.next_to(dy_eq, LEFT)
        dy_rhs = TexMobject("\\sqrt{m_2}", "v_2")
        dy_rhs[0][2:].set_color(BLUE)
        dy_rhs[1].set_color(RED)
        dy_rhs.next_to(dy_eq, RIGHT)
        VGroup(dy_label.target, dy_eq, dy_rhs).align_to(y_label, LEFT)
        alt_v2 = dy_rhs[1].copy()
        self.play(MoveToTarget(dy_label))
        self.play(
            Write(dy_eq),
            Write(dy_rhs),
        )
        self.play(alt_v2.next_to, block_vectors[1], UP, SMALL_BUFF)
        self.wait()
        self.play(FadeOut(alt_v2))
        self.wait()

        self.derivative_equations = VGroup(
            VGroup(dx_label, dx_eq, dx_rhs),
            VGroup(dy_label, dy_eq, dy_rhs),
        )

    def calculate_magnitude(self):
        corner_rect = Rectangle(
            stroke_color=WHITE,
            stroke_width=1,
            fill_color=BLACK,
            fill_opacity=1,
            height=2.5,
            width=8.5,
        )
        corner_rect.to_corner(UR, buff=0)

        ps_vect = self.ps_velocity_vector
        big_ps_vect = Arrow(
            ps_vect.get_start(), ps_vect.get_end(),
            buff=0,
        )
        big_ps_vect.match_style(ps_vect)
        big_ps_vect.scale(1.5)
        magnitude_bars = TexMobject("||", "||")
        magnitude_bars.match_height(
            big_ps_vect, stretch=True
        )
        rhs_scale_val = 0.8
        rhs = TexMobject(
            "=\\sqrt{"
            "\\left( dx/dt \\right)^2 + "
            "\\left( dy/dt \\right)^2"
            "}"
        )
        rhs.scale(rhs_scale_val)
        group = VGroup(
            magnitude_bars[0], big_ps_vect,
            magnitude_bars[1], rhs
        )
        group.arrange(RIGHT)
        group.next_to(corner_rect.get_corner(UL), DR)

        new_rhs = TexMobject(
            "=", "\\sqrt", "{m_1(v_1)^2 + m_2(v_2)^2}",
            tex_to_color_map={
                "m_1": BLUE,
                "m_2": BLUE,
                "v_1": GREEN,
                "v_2": RED,
            }
        )
        new_rhs.scale(rhs_scale_val)
        new_rhs.next_to(rhs, DOWN, aligned_edge=LEFT)

        final_rhs = TexMobject(
            "=", "\\sqrt{2(\\text{Kinetic energy})}"
        )
        final_rhs.scale(rhs_scale_val)
        final_rhs.next_to(new_rhs, DOWN, aligned_edge=LEFT)

        self.play(
            FadeIn(corner_rect),
            TransformFromCopy(ps_vect, big_ps_vect)
        )
        self.play(Write(magnitude_bars), Write(rhs[0]))
        self.wait()
        self.play(Write(rhs[1:]))
        self.wait()
        self.play(FadeInFrom(new_rhs, UP))
        for equation in self.derivative_equations:
            self.play(ShowCreationThenFadeAround(equation))
        self.wait()
        self.play(FadeInFrom(final_rhs, UP))
        self.wait()

    def let_process_play_out(self):
        self.play(*map(FadeOut, [
            self.projection_lines,
            self.derivative_labels,
            self.component_vectors,
            self.d1_brace,
            self.d1_label,
        ]))
        self.add(self.blocks, self.derivative_equations)
        self.blocks.resume_updating()
        self.slide(self.slide_time)

    #
    def grow_labels(self, labels):
        for label, vect in zip(labels, [DOWN, LEFT]):
            p = label.get_edge_center(vect)
            p += SMALL_BUFF * vect
            label.scale(2.5, about_point=p)
        return labels


class IntroduceVelocityVectorWithoutZoom(IntroduceVelocityVector):
    CONFIG = {
        "zoom": False,
    }


class ShowMomentumConservation(IntroduceVelocityVector):
    CONFIG = {
        "ps_velocity_vector_length": 1.25,
        "block_velocity_vector_length_multiple": 1,
        "block1_config": {
            "distance": 7,
        },
        "axes_config": {
            "y_max": 11,
        },
        "axes_center": 6.5 * LEFT + 1.2 * DOWN,
        "floor_y": -3.75,
        "wait_time": 15,
    }

    def construct(self):
        self.add_velocity_vectors()
        self.contrast_d1_d2_line_with_xy_line()
        self.rearrange_for_slope()
        self.up_to_first_collision()
        self.ask_what_next()
        self.show_conservation_of_momentum()
        self.show_rate_of_change_vector()
        self.show_sqrty_m_vector()
        self.show_dot_product()
        self.show_same_angles()
        self.show_horizontal_bounce()
        self.let_process_play_out()

    def add_velocity_vectors(self):
        self.slide(1)
        self.ps_vect = self.get_ps_velocity_vector(self.trajectory)
        self.block_vectors = self.get_block_velocity_vectors(self.ps_vect)
        self.play(
            GrowArrow(self.ps_vect),
            LaggedStartMap(GrowArrow, self.block_vectors, run_time=1),
        )
        self.add(self.ps_vect, self.block_vectors)

    def contrast_d1_d2_line_with_xy_line(self):
        line = self.d1_eq_d2_line
        label = self.d1_eq_d2_label
        label.to_edge(RIGHT, buff=1.1)
        label.shift(0.65 * DOWN)

        xy_line = line.copy()
        xy_line.set_stroke(YELLOW, 3)
        xy_line.set_angle(45 * DEGREES)
        xy_label = TexMobject("x = y")
        xy_label.next_to(ORIGIN, DOWN, SMALL_BUFF)
        xy_label.rotate(45 * DEGREES, about_point=ORIGIN)
        xy_label.shift(xy_line.point_from_proportion(0.2))
        self.xy_group = VGroup(xy_line, xy_label)

        self.play(
            ShowPassingFlash(
                line.copy().set_stroke(YELLOW, 4)
            ),
            Write(label),
        )
        self.play(
            TransformFromCopy(line, xy_line, run_time=2)
        )
        self.play(Write(xy_label))
        self.wait()

    def rearrange_for_slope(self):
        eqs = VGroup(*reversed(self.axes.labels)).copy()
        y_eq, x_eq = eqs
        for eq in eqs:
            point = VectorizedPoint(eq[1].get_center())
            eq.submobjects.insert(1, point)
            eq.submobjects[3] = eq[3].submobjects[0]
            eq.generate_target()
        eqs_targets = VGroup(*[eq.target for eq in eqs])

        new_eqs = VGroup(
            TexMobject("{y", "\\over", "\\sqrt{m_2}}", "=", "d_2"),
            TexMobject("{x", "\\over", "\\sqrt{m_1}}", "=", "d_1"),
        )
        new_x_eq, new_y_eq = new_eqs
        # Shuffle to align with x_eq and y_eq
        for new_eq in new_eqs:
            new_eq[2][2:].set_color(BLUE)
            new_eq.submobjects = [new_eq[i] for i in [0, 1, 3, 2, 4]]

        eqs_targets.arrange(DOWN, buff=LARGE_BUFF)
        eqs_targets.move_to(RIGHT).to_edge(UP)
        for eq, new_eq in zip(eqs_targets, new_eqs):
            new_eq.move_to(eq)

        self.play(LaggedStartMap(MoveToTarget, eqs, lag_ratio=0.7))
        self.play(*[
            Transform(
                eq, new_eq,
                path_arc=-90 * DEGREES,
            )
            for eq, new_eq in zip(eqs, new_eqs)
        ])
        self.wait()

        # Shuffle back
        for eq in eqs:
            eq[2][2:].set_color(BLUE)
            eq.submobjects = [eq[i] for i in [0, 1, 3, 2, 4]]

        # Set equal
        equals = TexMobject("=")
        for eq in eqs:
            eq.generate_target()
        VGroup(
            x_eq.target[4],
            x_eq.target[3],
            x_eq.target[:3],
        ).arrange(RIGHT)
        for p1, p2 in zip(x_eq, x_eq.target):
            p2.align_to(p1, DOWN)
        group = VGroup(y_eq.target, equals, x_eq.target)
        group.arrange(RIGHT)
        x_eq.target.align_to(y_eq.target, DOWN)
        equals.align_to(y_eq.target[3], DOWN)
        group.to_edge(UP, buff=MED_SMALL_BUFF)
        group.to_edge(RIGHT, buff=3)

        self.play(
            MoveToTarget(y_eq),
            MoveToTarget(x_eq, path_arc=90 * DEGREES),
            GrowFromCenter(equals)
        )
        self.wait()

        # Simplify
        final_eq = TexMobject(
            "y", "=",
            "{\\sqrt{m_2}", "\\over", "\\sqrt{m_1}}",
            "x",
        )
        for part in final_eq.get_parts_by_tex("sqrt"):
            part[2:].set_color(BLUE)
        m_part = final_eq[2:5]

        final_eq.next_to(group, DOWN)
        final_eq.shift(0.4 * UP)
        movers = VGroup(
            y_eq[0], equals.submobjects[0],
            y_eq[2], y_eq[1], x_eq[2],
            x_eq[0]
        ).copy()
        for mover, part in zip(movers, final_eq):
            mover.target = part
        self.play(
            LaggedStartMap(
                MoveToTarget, movers,
                path_arc=30 * DEGREES,
                lag_ratio=0.9
            ),
            VGroup(x_eq, equals, y_eq).scale,
            0.7, {"about_edge": UP},
        )
        self.remove(movers)
        self.add(final_eq)
        self.wait()

        # Highlight slope
        flash_line = self.d1_eq_d2_line.copy()
        flash_line.set_stroke(YELLOW, 5)
        self.play(ShowPassingFlash(flash_line))
        self.play(ShowCreationThenFadeAround(m_part))
        self.wait()

        # Tuck away slope in mind
        slope = m_part.copy()
        slope.generate_target()
        randy = Randolph(height=1.5)
        randy.next_to(final_eq, LEFT, MED_SMALL_BUFF)
        randy.align_to(self.d2_eq_w2_line, DOWN)
        bubble = ThoughtBubble(
            height=1.3, width=1.3, direction=RIGHT,
        )
        bubble.pin_to(randy)
        slope.target.scale(0.5)
        slope.target.move_to(bubble.get_bubble_center())
        randy.change("pondering", slope.target)
        randy.save_state()
        randy.change("plane")
        randy.fade(1)

        self.play(
            Restore(randy),
            Write(bubble),
            MoveToTarget(slope)
        )
        self.play(Blink(randy))

        self.thinking_on_slope_group = VGroup(
            randy, bubble, slope,
        )

        self.to_fade = VGroup(
            eqs, equals, final_eq,
            self.thinking_on_slope_group,
            self.xy_group,
        )

    def up_to_first_collision(self):
        self.begin_sliding()
        self.play(FadeOut(self.to_fade))
        self.wait_until(
            lambda: abs(self.ps_velocity_vector.get_vector()[1]) > 0.01
        )
        self.end_sliding()
        self.wait(3 + 3 / 60)  # Final cut reasons

    def ask_what_next(self):
        ps_vect = self.ps_velocity_vector
        question = TextMobject("What next?")
        question.set_background_stroke(color=BLACK, width=3)
        question.next_to(self.ps_point, UP)

        self.play(FadeInFrom(question, DOWN))
        ps_vect.suspend_updating()
        angles = [0.75 * PI, -0.5 * PI, -0.25 * PI]
        for last_angle, angle in zip(np.cumsum([0] + angles), angles):
            # This is dumb and shouldn't be needed
            ps_vect.rotate(last_angle, about_point=ps_vect.get_start())
            target = ps_vect.copy()
            target.rotate(
                angle,
                about_point=ps_vect.get_start()
            )
            self.play(
                Transform(
                    ps_vect, target,
                    path_arc=angle
                ),
            )
        ps_vect.resume_updating()

        self.whats_next_question = question

    def show_conservation_of_momentum(self):
        equation = self.get_momentum_equation()

        # Main equation
        self.play(FadeInFromDown(equation))
        for part in equation[:2], equation[3:5]:
            outline = part.copy()
            outline.set_fill(opacity=0)
            outline.set_stroke(YELLOW, 3)
            self.play(ShowPassingFlash(
                outline,
                run_time=1.5
            ))
            self.wait(0.5)

        # Dot product
        dot_product = self.get_dot_product()
        dot_product.next_to(equation, DOWN)
        sqrty_m_array = dot_product[0]

        x_label, y_label = self.axes.labels

        self.play(
            FadeOut(self.whats_next_question),
            FadeIn(dot_product),
            Transform(
                x_label[2].copy(),
                sqrty_m_array.get_entries()[0],
                remover=True,
            ),
            Transform(
                y_label[2].copy(),
                sqrty_m_array.get_entries()[1],
                remover=True,
            ),
        )

        self.momentum_equation = equation
        self.dot_product = dot_product

    def show_rate_of_change_vector(self):
        ps_vect = self.ps_velocity_vector
        original_d_array = self.dot_product[2]

        d_array = original_d_array.copy()
        d_array.generate_target()
        d_array.scale(0.75)
        d_array.add_updater(lambda m: m.next_to(
            ps_vect.get_end(),
            np.sign(ps_vect.get_vector()[0]) * RIGHT,
            SMALL_BUFF
        ))

        self.play(TransformFromCopy(original_d_array, d_array))
        self.wait()

        self.d_array = d_array

    def show_sqrty_m_vector(self):
        original_sqrty_m_array = self.dot_product[0]
        sqrty_m_vector = Arrow(
            self.ds_to_point(0, 0),
            # self.ds_to_point(1, 1),
            self.ds_to_point(2, 2),
            buff=0,
            color=YELLOW,
        )

        sqrty_m_array = original_sqrty_m_array.deepcopy()
        sqrty_m_array.scale(0.75)
        sqrty_m_array.next_to(
            sqrty_m_vector.get_end(), UP, SMALL_BUFF
        )

        rise = DashedLine(
            sqrty_m_vector.get_end(),
            sqrty_m_vector.get_corner(DR),
            color=RED,
        )
        run = DashedLine(
            sqrty_m_vector.get_corner(DR),
            sqrty_m_vector.get_start(),
            color=GREEN,
        )
        sqrty_m_array.add_background_to_entries()
        run_label, rise_label = sqrty_m_array.get_entries().copy()
        rise_label.next_to(rise, RIGHT, SMALL_BUFF)
        run_label.next_to(run, DOWN, SMALL_BUFF)

        randy_group = self.thinking_on_slope_group
        randy_group.align_to(self.d2_eq_w2_line, DOWN)
        randy_group.to_edge(LEFT)
        randy_group.shift(2 * RIGHT)

        self.play(GrowArrow(sqrty_m_vector))
        self.play(TransformFromCopy(
            original_sqrty_m_array, sqrty_m_array,
        ))
        self.play(FadeIn(randy_group))
        self.play(
            ShowCreation(rise),
            TransformFromCopy(
                sqrty_m_array.get_entries()[1],
                rise_label,
            ),
        )
        self.add(run, randy_group)
        self.play(
            ShowCreation(run),
            TransformFromCopy(
                sqrty_m_array.get_entries()[0],
                run_label,
            ),
        )
        self.wait()
        self.play(FadeOut(randy_group))
        self.play(FadeOut(VGroup(
            rise, run, rise_label, run_label,
        )))

        # move to ps_point
        point = self.ps_point.get_location()
        sqrty_m_vector.generate_target()
        sqrty_m_vector.target.shift(
            point - sqrty_m_vector.get_start()
        )
        sqrty_m_array.generate_target()
        sqrty_m_array.target.next_to(
            sqrty_m_vector.target.get_end(),
            RIGHT, SMALL_BUFF,
        )
        sqrty_m_array.target.shift(SMALL_BUFF * UP)
        self.play(
            MoveToTarget(sqrty_m_vector),
            MoveToTarget(sqrty_m_array),
            run_time=2
        )

        self.sqrty_m_vector = sqrty_m_vector
        self.sqrty_m_array = sqrty_m_array

    def show_dot_product(self):
        # Highlight arrays
        d_array = self.d_array
        big_d_array = self.dot_product[2]
        m_array = self.sqrty_m_array
        big_m_array = self.dot_product[0]

        self.play(
            ShowCreationThenFadeAround(big_d_array),
            ShowCreationThenFadeAround(d_array),
        )
        self.play(
            ShowCreationThenFadeAround(big_m_array),
            ShowCreationThenFadeAround(m_array),
        )

        # Before and after
        ps_vect = self.ps_velocity_vector
        theta = np.arctan(np.sqrt(self.block2.mass / self.block1.mass))
        self.theta = theta

        ps_vect.suspend_updating()
        kwargs = {"about_point": ps_vect.get_start()}
        for x in range(2):
            for u in [-1, 1]:
                ps_vect.rotate(u * 2 * theta, **kwargs)
                self.update_mobjects(dt=0)
                self.wait()
        ps_vect.resume_updating()

        # Circle
        circle = Circle(
            radius=ps_vect.get_length(),
            arc_center=ps_vect.get_start(),
            color=RED,
            stroke_width=1,
        )
        self.play(
            Rotating(
                ps_vect,
                about_point=ps_vect.get_start(),
                run_time=5,
                rate_func=lambda t: smooth(t, 3),
            ),
            FadeIn(circle),
        )
        self.wait()

        self.ps_vect_circle = circle

    def show_same_angles(self):
        # circle = self.ps_vect_circle
        ps_vect = self.ps_velocity_vector
        ps_point = self.ps_point
        point = ps_point.get_center()
        ghost_ps_vect = ps_vect.copy()
        ghost_ps_vect.clear_updaters()
        ghost_ps_vect.set_fill(opacity=0.5)
        theta = self.theta
        ghost_ps_vect.rotate(
            -2 * theta,
            about_point=ghost_ps_vect.get_start(),
        )

        arc1 = Arc(
            start_angle=PI,
            angle=theta,
            arc_center=point,
            radius=0.5,
            color=WHITE,
        )
        arc2 = arc1.copy()
        arc2.rotate(theta, about_point=point)
        arc3 = arc1.copy()
        arc3.rotate(PI, about_point=point)
        arc1.set_color(BLUE)

        line_pair = VGroup(*[
            Line(point, point + LEFT).rotate(
                angle, about_point=point
            )
            for angle in [0, theta]
        ])
        line_pair.set_stroke(width=0)

        ps_vect.suspend_updating()
        self.play(
            ShowCreation(arc1),
            FadeIn(ghost_ps_vect)
        )
        self.wait()
        self.play(
            Rotate(ps_vect, 2 * theta, about_point=point)
        )
        self.begin_sliding()
        ps_vect.resume_updating()
        self.play(GrowFromPoint(arc2, point))
        self.wait(0.5)
        self.end_sliding()
        self.play(
            TransformFromCopy(arc1, arc3, path_arc=-PI),
            Rotate(line_pair, -PI, about_point=point),
            UpdateFromAlphaFunc(
                line_pair, lambda m, a: m.set_stroke(
                    width=there_and_back(a)**0.5
                )
            ),
        )
        # Show light beam along trajectory
        self.show_trajectory_beam_bounce()
        self.wait()

        # TODO: Add labels for angles?

        self.play(FadeOut(VGroup(
            self.ps_vect_circle, ghost_ps_vect, arc1
        )))

    def show_horizontal_bounce(self):
        self.slide_until(
            lambda: self.ps_velocity_vector.get_vector()[1] > 0
        )
        point = self.ps_point.get_location()
        theta = self.theta
        arc1 = Arc(
            start_angle=0,
            angle=2 * theta,
            radius=0.5,
            arc_center=point,
        )
        arc2 = arc1.copy()
        arc2.rotate(PI - 2 * theta, about_point=point)
        arcs = VGroup(arc1, arc2)

        self.slide(0.5)
        self.play(LaggedStartMap(
            FadeInFromLarge, arcs,
            lag_ratio=0.75,
        ))
        self.show_trajectory_beam_bounce()

    def let_process_play_out(self):
        self.slide(self.wait_time)
        self.wait(10)  # Just to be sure...

    #
    def show_trajectory_beam_bounce(self, n_times=2):
        # Show light beam along trajectory
        beam = self.trajectory.copy()
        beam.clear_updaters()
        beam.set_stroke(YELLOW, 3)
        for x in range(n_times):
            self.play(ShowPassingFlash(
                beam,
                run_time=2,
                rate_func=bezier([0, 0, 1, 1])
            ))

    def get_momentum_equation(self):
        equation = TexMobject(
            "m_1", "v_1", "+", "m_2", "v_2",
            "=", "\\text{const.}",
            tex_to_color_map={
                "m_1": BLUE,
                "m_2": BLUE,
                "v_1": RED,
                "v_2": RED,
            }
        )
        equation.to_edge(UP, buff=MED_SMALL_BUFF)
        return equation

    def get_dot_product(self,
                        m1="\\sqrt{m_1}", m2="\\sqrt{m_2}",
                        d1="dx/dt", d2="dy/dt"):
        sqrty_m = Matrix([[m1], [m2]])
        deriv_array = Matrix([[d1], [d2]])
        for entry in sqrty_m.get_entries():
            if "sqrt" in entry.get_tex_string():
                entry[2:].set_color(BLUE)
        for matrix in sqrty_m, deriv_array:
            matrix.add_to_back(BackgroundRectangle(matrix))
            matrix.get_brackets().scale(0.9)
            matrix.set_height(1.25)
        dot = TexMobject("\\cdot")
        rhs = TexMobject("= \\text{const.}")
        dot_product = VGroup(
            sqrty_m, dot, deriv_array, rhs
        )
        dot_product.arrange(RIGHT, buff=SMALL_BUFF)
        return dot_product


class JustTheProcessNew(PositionPhaseSpaceScene):
    CONFIG = {
        "block1_config": {
            "mass": 16,
            "velocity": -2
        },
        "wait_time": 10,
    }

    def setup(self):
        super().setup()
        self.add(
            self.floor,
            self.wall,
            self.blocks,
            self.axes,
            self.d1_eq_d2_line,
            self.d2_eq_w2_line,
        )

    def construct(self):
        self.slide(self.wait_time)
