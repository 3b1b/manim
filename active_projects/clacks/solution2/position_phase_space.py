from big_ol_pile_of_manim_imports import *
from active_projects.clacks.question import Block
from active_projects.clacks.question import Wall


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
            "distance": 7,
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
        }
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
            self.get_time_tracker(),
        ]

    def get_corner(self):
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

    def tie_blocks_to_ps_point(self):
        def update_blocks(blocks):
            d1, d2 = self.point_to_ds(self.ps_point.get_location())
            b1, b2 = blocks
            corner = self.get_corner()
            b1.move_to(corner + d1 * RIGHT, DL)
            b2.move_to(corner + d2 * RIGHT, DR)
        self.blocks.add_updater(update_blocks)

    def time_to_ds(self, time):
        # Deals in its own phase space, different
        # from the one displayed
        m1 = self.block1.mass
        m2 = self.block2.mass
        v1 = self.block1.velocity
        # v2 = self.block2.velocity
        d1 = self.block1_config["distance"]
        d2 = self.block2_config["distance"]
        w2 = self.block2.width
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

        ps_point = ds_to_ps_point(d1, d2 + w2)
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

    def get_clack_flashes(self):
        pass  # TODO

    # Mobject getters
    def get_floor(self):
        floor = self.floor = Line(
            self.wall_x * RIGHT,
            FRAME_WIDTH * RIGHT / 2,
            stroke_color=WHITE,
            stroke_width=3,
        )
        floor.move_to(self.get_corner(), LEFT)
        return floor

    def get_wall(self):
        wall = self.wall = Wall(**self.wall_config)
        wall.move_to(self.get_corner(), DR)
        return wall

    def get_blocks(self):
        blocks = self.blocks = VGroup()
        for n in [1, 2]:
            config = getattr(self, "block{}_config".format(n))
            block = Block(**config)
            block.move_to(self.get_corner(), DL)
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
        axes.add(self.get_axes_labels(axes))
        return axes

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
        brace = Brace(line, UP)

        def update_brace(brace):
            right_point = get_right_point()
            left_point = np.array(right_point)
            left_point[0] = self.wall_x
            line.put_start_and_end_on(left_point, right_point)
            brace.match_width(line, stretch=True)
            brace.next_to(line, UP, buff=0)

        brace.add_updater(update_brace)
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

    def get_brace_d_label(self, n, get_d, brace, vect):
        label = self.get_d_label(n, get_d)
        label.add_updater(
            lambda m: m.next_to(brace, vect, 0)
        )
        return label

    def get_d1_label(self):
        self.d1_label = self.get_brace_d_label(
            1, self.get_d1, self.d1_brace, UP
        )
        return self.d1_label

    def get_d2_label(self):
        self.d2_label = self.get_brace_d_label(
            2, self.get_d2, self.d2_brace, UP
        )
        return self.d2_label

    def get_d1_eq_d2_line(self):
        start = self.ds_to_point(0, 0)
        end = self.ds_to_point(15, 15)
        self.d1_eq_d2_line = DashedLine(start, end)
        self.d1_eq_d2_line.set_stroke(WHITE, 2)
        return self.d1_eq_d2_line

    def get_d1_eq_d2_label(self):
        label = TexMobject("d1 = d2")
        label.scale(0.75)
        line = self.d1_eq_d2_line
        for i in range(len(line)):
            if line[i].get_top()[1] > FRAME_HEIGHT / 2:
                break
        label.next_to(line[i - 3], DR, SMALL_BUFF)
        self.d1_eq_d2_label = label
        return label

    def get_d2_eq_w2_line(self):
        w2 = self.block2.width
        start = self.ds_to_point(0, w2)
        end = self.ds_to_point(30, w2)
        self.d2_eq_w2_line = DashedLine(start, end)
        self.d2_eq_w2_line.set_stroke(WHITE, 2)
        return self.d2_eq_w2_line

    def get_d2_eq_w2_label(self):
        label = TexMobject("d2 = \\text{block width}")
        label.scale(0.75)
        label.next_to(self.d2_eq_w2_line, UP, SMALL_BUFF)
        label.to_edge(RIGHT, buff=MED_SMALL_BUFF)
        self.d2_eq_w_label = label
        return label

    def get_time_tracker(self):
        time_tracker = self.time_tracker = ValueTracker(0)
        time_tracker.add_updater(
            lambda m, dt: m.increment_value(dt)
        )
        self.get_time = time_tracker.get_value
        self.add(time_tracker)
        return time_tracker


class IntroducePositionPhaseSpace(PositionPhaseSpaceScene):
    CONFIG = {
        "rescale_coordinates": False,
    }

    def construct(self):
        self.show_coordinates()
        self.show_xy_line()
        self.let_process_play_out()

        self.add(*self.all_items)
        self.ps_point.add_updater(
            lambda m: m.move_to(self.ds_to_point(
                *self.time_to_ds(self.get_time())
            ))
        )
        self.wait(10)
        # self.play(Rotating(
        #     self.ps_point,
        #     about_point=self.ps_point.get_location() + RIGHT,
        #     run_time=3
        # ))

    def show_coordinates(self):
        pass

    def show_xy_line(self):
        pass

    def let_process_play_out(self):
        pass


class EqualMassCase(IntroducePositionPhaseSpace):
    def construct(self):
        self.show_first_point()
        self.up_to_first_collision()
        self.ask_about_momentum_transfer()
        self.up_to_second_collision()
        self.up_to_third_collision()

    def show_first_point(self):
        pass

    def up_to_first_collision(self):
        pass

    def ask_about_momentum_transfer(self):
        pass

    def up_to_second_collision(self):
        pass

    def up_to_third_collision(self):
        pass
