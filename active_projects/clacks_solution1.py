from big_ol_pile_of_manim_imports import *
from active_projects.clacks import *


# TODO, add solution image
class FromPuzzleToSolution(MovingCameraScene):
    def construct(self):
        big_rect = FullScreenFadeRectangle()
        big_rect.set_fill(DARK_GREY, 0.5)
        self.add(big_rect)

        rects = VGroup(ScreenRectangle(), ScreenRectangle())
        rects.set_height(3)
        rects.arrange_submobjects(RIGHT, buff=2)

        titles = VGroup(
            TextMobject("Puzzle"),
            TextMobject("Solution"),
        )

        images = Group(
            ImageMobject("BlocksAndWallExampleMass16"),
            ImageMobject("SphereSurfaceProof2"),  # TODO
        )
        for title, rect, image in zip(titles, rects, images):
            title.scale(1.5)
            title.next_to(rect, UP)
            image.replace(rect)
            self.add(image, rect, title)

        frame = self.camera_frame
        frame.save_state()

        self.play(
            frame.replace, images[0],
            run_time=3
        )
        self.wait()
        self.play(Restore(frame, run_time=3))
        self.play(
            frame.replace, images[1],
            run_time=3,
        )
        self.wait()


class BlocksAndWallExampleMass16(BlocksAndWallExample):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 16,
                "velocity": -1.5,
            },
        },
        "wait_time": 25,
    }


class Mass16WithElasticLabel(Mass1e1WithElasticLabel):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 16,
            }
        },
    }


class BlocksAndWallExampleMass64(BlocksAndWallExample):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 64,
                "velocity": -1.5,
            },
        },
        "wait_time": 25,
    }


class BlocksAndWallExampleMass1e4(BlocksAndWallExample):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 1e4,
                "velocity": -1.5,
            },
        },
        "wait_time": 25,
    }


class BlocksAndWallExampleMassMillion(BlocksAndWallExample):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 1e6,
                "velocity": -0.9,
                "label_text": "$100^{3}$ kg"
            },
        },
        "wait_time": 30,
        "million_fade_time": 4,
        "min_time_between_sounds": 0.002,
    }

    def setup(self):
        super().setup()
        self.add_million_label()

    def add_million_label(self):
        first_label = self.blocks.block1.label
        brace = Brace(first_label[:-2], UP, buff=SMALL_BUFF)
        new_label = TexMobject("1{,}000{,}000")
        new_label.next_to(brace, UP, buff=SMALL_BUFF)
        new_label.add(brace)
        new_label.set_color(YELLOW)

        def update_label(label):
            d_time = self.get_time() - self.million_fade_time
            opacity = smooth(d_time)
            label.set_fill(opacity=d_time)

        new_label.add_updater(update_label)
        first_label.add(new_label)


class BlocksAndWallExampleMassTrillion(BlocksAndWallExample):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 1e12,
                "velocity": -1,
            },
        },
        "wait_time": 30,
        "min_time_between_sounds": 0.001,
    }


class AskAboutFindingNewVelocities(Scene):
    CONFIG = {
        "floor_y": -3,
        "wall_x": -6.5,
        "wall_height": 7,
        "block1_config": {
            "mass": 10,
            "fill_color": BLUE_E,
            "velocity": -1,
        },
        "block2_config": {"mass": 1},
        "block1_start_x": 7,
        "block2_start_x": 3,
        "v_arrow_scale_value": 1.0,
        "is_halted": False,
    }

    def setup(self):
        self.add_clack_sound_file()

    def construct(self):
        self.add_clack_sound_file()
        self.add_floor()
        self.add_wall()
        self.add_blocks()
        self.add_velocity_labels()

        self.ask_about_transfer()
        self.show_ms_and_vs()
        self.show_value_on_equations()

    def add_clack_sound_file(self):
        self.clack_file = os.path.join(
            VIDEO_DIR, "active_projects",
            "clacks", "sounds", "clack.wav"
        )

    def add_floor(self):
        floor = self.floor = Line(
            self.wall_x * RIGHT,
            (FRAME_WIDTH / 2) * RIGHT,
        )
        floor.shift(self.floor_y * UP)
        self.add(floor)

    def add_wall(self):
        wall = self.wall = Wall(height=self.wall_height)
        wall.move_to(
            self.wall_x * RIGHT + self.floor_y * UP,
            DR,
        )
        self.add(wall)

    def add_blocks(self):
        block1 = self.block1 = Block(**self.block1_config)
        block2 = self.block2 = Block(**self.block2_config)
        blocks = self.blocks = VGroup(block1, block2)
        block1.move_to(self.block1_start_x * RIGHT + self.floor_y * UP, DOWN)
        block2.move_to(self.block2_start_x * RIGHT + self.floor_y * UP, DOWN)

        self.add_velocity_phase_space_point()
        # Add arrows
        for block in blocks:
            arrow = Vector(self.block_to_v_vector(block))
            arrow.set_color(RED)
            arrow.set_stroke(BLACK, 1, background=True)
            arrow.move_to(block.get_center(), RIGHT)
            block.arrow = arrow
            block.add(arrow)

            block.v_label = DecimalNumber(
                block.velocity,
                num_decimal_places=2,
                background_stroke_width=2,
            )
            block.v_label.set_color(RED)
            block.add(block.v_label)

        # Add updater
        blocks.add_updater(self.update_blocks)
        self.add(
            blocks,
            block2.arrow, block1.arrow,
            block2.v_label, block1.v_label,
        )

    def add_velocity_phase_space_point(self):
        self.vps_point = VectorizedPoint([
            np.sqrt(self.block1.mass) * self.block1.velocity,
            np.sqrt(self.block2.mass) * self.block2.velocity,
            0
        ])

    def add_velocity_labels(self):
        v_labels = self.get_next_velocity_labels()

        self.add(v_labels)

    def ask_about_transfer(self):
        energy_expression, momentum_expression = \
            self.get_energy_and_momentum_expressions()
        energy_words = TextMobject("Conservation of energy:")
        energy_words.move_to(UP)
        energy_words.to_edge(LEFT, buff=1.5)
        momentum_words = TextMobject("Conservation of momentum:")
        momentum_words.next_to(
            energy_words, DOWN,
            buff=0.7,
        )

        energy_expression.next_to(energy_words, RIGHT, MED_LARGE_BUFF)
        momentum_expression.next_to(energy_expression, DOWN)
        momentum_expression.next_to(momentum_words, RIGHT)

        velocity_labels = self.all_velocity_labels
        randy = Randolph(height=2)
        randy.next_to(velocity_labels, DR)
        randy.save_state()
        randy.fade(1)

        # Up to collisions
        self.go_through_next_collision(include_velocity_label_animation=True)
        self.play(
            randy.restore,
            randy.change, "pondering", velocity_labels[0],
        )
        self.halt()
        self.play(randy.look_at, velocity_labels[-1])
        self.play(Blink(randy))
        self.play(
            FadeInFrom(energy_words, RIGHT),
            FadeInFromDown(energy_expression),
            FadeOut(randy),
        )
        self.wait()
        self.play(
            FadeInFrom(momentum_words, RIGHT),
            FadeInFromDown(momentum_expression)
        )
        self.wait()

        self.energy_expression = energy_expression
        self.energy_words = energy_words
        self.momentum_expression = momentum_expression
        self.momentum_words = momentum_words

    def show_ms_and_vs(self):
        block1 = self.block1
        block2 = self.block2
        energy_expression = self.energy_expression
        momentum_expression = self.momentum_expression

        for block in self.blocks:
            block.shift_onto_screen()

        m1_labels = VGroup(
            block1.label,
            energy_expression.get_part_by_tex("m_1"),
            momentum_expression.get_part_by_tex("m_1"),
        )
        m2_labels = VGroup(
            block2.label,
            energy_expression.get_part_by_tex("m_2"),
            momentum_expression.get_part_by_tex("m_2"),
        )
        v1_labels = VGroup(
            block1.v_label,
            energy_expression.get_part_by_tex("v_1"),
            momentum_expression.get_part_by_tex("v_1"),
        )
        v2_labels = VGroup(
            block2.v_label,
            energy_expression.get_part_by_tex("v_2"),
            momentum_expression.get_part_by_tex("v_2"),
        )
        label_groups = VGroup(
            m1_labels, m2_labels,
            v1_labels, v2_labels,
        )
        for group in label_groups:
            group.rects = VGroup(*map(
                SurroundingRectangle,
                group
            ))

        for group in label_groups:
            self.play(LaggedStart(
                ShowCreation, group.rects,
                lag_ratio=0.8,
                run_time=1,
            ))
            self.play(FadeOut(group.rects))

    def show_value_on_equations(self):
        energy_expression = self.energy_expression
        momentum_expression = self.momentum_expression
        energy_text = VGroup(energy_expression, self.energy_words)
        momentum_text = VGroup(momentum_expression, self.momentum_words)
        block1 = self.block1
        block2 = self.block2
        block1.save_state()
        block2.save_state()

        v_terms, momentum_v_terms = [
            VGroup(*[
                expr.get_part_by_tex("v_{}".format(d))
                for d in [1, 2]
            ])
            for expr in [energy_expression, momentum_expression]
        ]
        v_braces = VGroup(*[
            Brace(term, UP, buff=SMALL_BUFF)
            for term in v_terms
        ])
        v_decimals = VGroup(*[DecimalNumber(0) for x in range(2)])

        def update_v_decimals(v_decimals):
            values = self.get_velocities()
            for decimal, value, brace in zip(v_decimals, values, v_braces):
                decimal.set_value(value)
                decimal.next_to(brace, UP, SMALL_BUFF)

        update_v_decimals(v_decimals)

        energy_const_brace, momentum_const_brace = [
            Brace(
                expr.get_part_by_tex("const"), UP,
                buff=SMALL_BUFF,
            )
            for expr in [energy_expression, momentum_expression]
        ]

        sqrt_m_vect = np.array([
            np.sqrt(self.block1.mass),
            np.sqrt(self.block2.mass),
            0
        ])

        def get_energy():
            return 0.5 * get_norm(self.vps_point.get_location())**2

        def get_momentum():
            return np.dot(self.vps_point.get_location(), sqrt_m_vect)

        energy_decimal = DecimalNumber(get_energy())
        energy_decimal.next_to(energy_const_brace, UP, SMALL_BUFF)
        momentum_decimal = DecimalNumber(get_momentum())
        momentum_decimal.next_to(momentum_const_brace, UP, SMALL_BUFF)

        VGroup(
            energy_const_brace, energy_decimal,
            momentum_const_brace, momentum_decimal,
        ).set_color(YELLOW)

        self.play(
            ShowCreationThenFadeAround(energy_expression),
            momentum_text.set_fill, {"opacity": 0.25},
            FadeOut(self.all_velocity_labels),
        )
        self.play(*[
            *map(GrowFromCenter, v_braces),
            *map(VFadeIn, v_decimals),
            GrowFromCenter(energy_const_brace),
            FadeIn(energy_decimal),
        ])
        energy_decimal.add_updater(
            lambda m: m.set_value(get_energy())
        )
        v_decimals.add_updater(update_v_decimals)
        self.add(v_decimals)
        self.unhalt()
        for x in range(4):
            self.go_through_next_collision()
        energy_decimal.clear_updaters()
        momentum_decimal.set_value(get_momentum())
        self.halt()
        self.play(*[
            momentum_text.set_fill, {"opacity": 1},
            FadeOut(energy_text),
            FadeOut(energy_const_brace),
            FadeOut(energy_decimal),
            GrowFromCenter(momentum_const_brace),
            FadeIn(momentum_decimal),
            *[
                ApplyMethod(b.next_to, vt, UP, SMALL_BUFF)
                for b, vt in zip(v_braces, momentum_v_terms)
            ],
        ])
        self.unhalt()
        momentum_decimal.add_updater(
            lambda m: m.set_value(get_momentum())
        )
        momentum_decimal.add_updater(
            lambda m: m.next_to(momentum_const_brace, UP, SMALL_BUFF)
        )
        for x in range(4):
            self.go_through_next_collision()
        self.wait(10)

    # Helpers

    def get_energy_and_momentum_expressions(self):
        tex_to_color_map = {
            "v_1": RED_B,
            "v_2": RED_B,
            "m_1": BLUE_C,
            "m_2": BLUE_C,
        }
        energy_expression = TexMobject(
            "\\frac{1}{2} m_1 (v_1)^2 + ",
            "\\frac{1}{2} m_2 (v_2)^2 = ",
            "\\text{const.}",
            tex_to_color_map=tex_to_color_map,
        )
        momentum_expression = TexMobject(
            "m_1 v_1 + m_2 v_2 =", "\\text{const.}",
            tex_to_color_map=tex_to_color_map
        )
        return VGroup(
            energy_expression,
            momentum_expression,
        )

    def go_through_next_collision(self, include_velocity_label_animation=False):
        block2 = self.block2
        if block2.velocity >= 0:
            self.wait_until(self.blocks_are_hitting)
            self.add_sound(self.clack_file)
            self.transfer_momentum()
            edge = RIGHT
        else:
            self.wait_until(self.block2_is_hitting_wall)
            self.add_sound(self.clack_file)
            self.reflect_block2()
            edge = LEFT
        anims = [Flash(block2.get_edge_center(edge))]
        if include_velocity_label_animation:
            anims.append(self.get_next_velocity_labels_animation())
        self.play(*anims, run_time=0.5)

    def get_next_velocity_labels_animation(self):
        return FadeInFrom(
            self.get_next_velocity_labels(),
            LEFT,
            run_time=0.5
        )

    def get_next_velocity_labels(self, v1=None, v2=None):
        new_labels = self.get_velocity_labels(v1, v2)
        if hasattr(self, "all_velocity_labels"):
            arrow = Vector(RIGHT)
            arrow.next_to(self.all_velocity_labels)
            new_labels.next_to(arrow, RIGHT)
            new_labels.add(arrow)
        else:
            self.all_velocity_labels = VGroup()
        self.all_velocity_labels.add(new_labels)
        return new_labels

    def get_velocity_labels(self, v1=None, v2=None):
        default_vs = self.get_velocities()
        v1 = v1 or default_vs[0]
        v2 = v2 or default_vs[1]
        labels = VGroup(
            TexMobject("v_1 = {:.2f}".format(v1)),
            TexMobject("v_2 = {:.2f}".format(v2)),
        )
        labels.arrange_submobjects(
            DOWN,
            buff=MED_SMALL_BUFF,
            aligned_edge=LEFT,
        )
        labels.scale(0.9)
        for label in labels:
            label[:2].set_color(RED)
        labels.next_to(self.wall, RIGHT)
        labels.to_edge(UP, buff=MED_SMALL_BUFF)
        return labels

    def update_blocks(self, blocks, dt):
        for block, velocity in zip(blocks, self.get_velocities()):
            block.velocity = velocity
            if not self.is_halted:
                block.shift(block.velocity * dt * RIGHT)
            center = block.get_center()
            block.arrow.put_start_and_end_on(
                center,
                center + self.block_to_v_vector(block),
            )
            max_height = 0.25
            block.v_label.set_value(block.velocity)
            if block.v_label.get_height() > max_height:
                block.v_label.set_height(max_height)
            block.v_label.next_to(
                block.arrow.get_start(), UP,
                buff=SMALL_BUFF,
            )
        return blocks

    def block_to_v_vector(self, block):
        return block.velocity * self.v_arrow_scale_value * RIGHT

    def blocks_are_hitting(self):
        x1 = self.block1.get_left()[0]
        x2 = self.block2.get_right()[0]
        buff = 0.01
        return (x1 < x2 + buff)

    def block2_is_hitting_wall(self):
        x2 = self.block2.get_left()[0]
        buff = 0.01
        return (x2 < self.wall_x + buff)

    def get_velocities(self):
        m1 = self.block1.mass
        m2 = self.block2.mass
        vps_coords = self.vps_point.get_location()
        return [
            vps_coords[0] / np.sqrt(m1),
            vps_coords[1] / np.sqrt(m2),
        ]

    def transfer_momentum(self):
        m1 = self.block1.mass
        m2 = self.block2.mass
        theta = np.arctan(np.sqrt(m2 / m1))
        self.reflect_block2()
        self.vps_point.rotate(2 * theta, about_point=ORIGIN)

    def reflect_block2(self):
        self.vps_point.points[:, 1] *= -1

    def halt(self):
        self.is_halted = True

    def unhalt(self):
        self.is_halted = False


class IntroduceVelocityPhaseSpace(AskAboutFindingNewVelocities):
    CONFIG = {
        "wall_height": 1.5,
        "floor_y": -3.5,
        "block1_start_x": 5,
        "block2_start_x": 0,
        "axes_config": {
            "x_axis_config": {
                "x_min": -5.5,
                "x_max": 6,
            },
            "y_axis_config": {
                "x_min": -3.5,
                "x_max": 4,
            },
            "number_line_config": {
                "unit_size": 0.7,
            },
        },
    }

    def construct(self):
        self.add_wall_floor_and_blocks()
        self.show_two_equations()
        self.draw_axes()
        self.draw_ellipse()
        self.rescale_axes()
        self.show_starting_point()
        self.show_initial_collide()
        self.ask_about_where_to_land()
        self.show_conservation_of_momentum_equation()
        self.show_momentum_line()
        self.reiterate_meaning_of_line_and_circle()
        self.reshow_first_jump()
        self.show_bounce_off_wall()
        self.show_reflection_about_x()
        self.show_remaining_collisions()

    def add_wall_floor_and_blocks(self):
        self.add_floor()
        self.add_wall()
        self.add_blocks()
        self.halt()

    def show_two_equations(self):
        equations = self.get_energy_and_momentum_expressions()
        equations.arrange_submobjects(DOWN, buff=LARGE_BUFF)
        equations.shift(UP)
        v1_terms, v2_terms = v_terms = VGroup(*[
            VGroup(*[
                expr.get_parts_by_tex(tex)
                for expr in equations
            ])
            for tex in ("v_1", "v_2")
        ])
        for eq in equations:
            eq.highlighted_copy = eq.copy()
            eq.highlighted_copy.set_fill(opacity=0)
            eq.highlighted_copy.set_stroke(YELLOW, 3)

        self.add(equations)
        self.play(
            ShowCreation(equations[0].highlighted_copy),
            run_time=0.75,
        )
        self.play(
            FadeOut(equations[0].highlighted_copy),
            ShowCreation(equations[1].highlighted_copy),
            run_time=0.75,
        )
        self.play(
            FadeOut(equations[1].highlighted_copy),
            run_time=0.75,
        )
        self.play(LaggedStart(
            Indicate, v_terms,
            lag_ratio=0.75,
            rate_func=there_and_back,
        ))
        self.wait()

        self.equations = equations

    def draw_axes(self):
        equations = self.equations
        energy_expression, momentum_expression = equations

        axes = self.axes = Axes(**self.axes_config)
        axes.to_edge(UP, buff=SMALL_BUFF)
        axes.set_stroke(width=2)

        # Axes labels
        x_axis_labels = VGroup(
            TexMobject("x = ", "v_1"),
            TexMobject("x = ", "\\sqrt{m_1}", "\\cdot", "v_1"),
        )
        y_axis_labels = VGroup(
            TexMobject("y = ", "v_2"),
            TexMobject("y = ", "\\sqrt{m_2}", "\\cdot", "v_2"),
        )
        axis_labels = self.axis_labels = VGroup(x_axis_labels, y_axis_labels)
        for label_group in axis_labels:
            for label in label_group:
                label.set_color_by_tex("v_", RED)
                label.set_color_by_tex("m_", BLUE)
        for label in x_axis_labels:
            label.next_to(axes.x_axis.get_right(), UP)
        for label in y_axis_labels:
            label.next_to(axes.y_axis.get_top(), DR)

        # Introduce axes and labels
        self.play(
            equations.scale, 0.8,
            equations.to_corner, UL, {"buff": MED_SMALL_BUFF},
            Write(axes),
        )
        self.wait()
        self.play(
            momentum_expression.set_fill, {"opacity": 0.2},
            Indicate(energy_expression, scale_factor=1.05),
        )
        self.wait()
        for n in range(2):
            tex = "v_{}".format(n + 1)
            self.play(
                TransformFromCopy(
                    energy_expression.get_part_by_tex(tex),
                    axis_labels[n][0].get_part_by_tex(tex),
                ),
                FadeInFromDown(axis_labels[n][0][0]),
            )

        # Show vps_dot
        vps_dot = self.vps_dot = Dot(color=RED)
        vps_dot.set_stroke(BLACK, 2, background=True)
        vps_dot.add_updater(
            lambda m: m.move_to(axes.coords_to_point(
                *self.get_velocities()
            ))
        )

        vps_point = self.vps_point
        vps_point.save_state()
        kwargs = {
            "path_arc": PI / 3,
            "run_time": 2,
        }
        target_locations = [
            6 * RIGHT + 2 * UP,
            6 * RIGHT + 2 * DOWN,
            6 * LEFT + 1 * UP,
        ]
        self.add(vps_dot)
        for target_location in target_locations:
            self.play(
                vps_point.move_to, target_location,
                **kwargs,
            )
        self.play(Restore(vps_point, **kwargs))
        self.wait()

    def draw_ellipse(self):
        vps_dot = self.vps_dot
        vps_point = self.vps_point
        axes = self.axes
        energy_expression = self.equations[0]

        ellipse = self.ellipse = Circle(color=YELLOW)
        ellipse.set_stroke(BLACK, 5, background=True)
        ellipse.rotate(PI)
        ellipse.replace(
            Polygon(*[
                axes.coords_to_point(x, y * np.sqrt(10))
                for x, y in [(1, 0), (0, 1), (-1, 0), (0, -1)]
            ]),
            stretch=True
        )

        self.play(Indicate(energy_expression, scale_factor=1.05))
        self.add(ellipse, vps_dot)
        self.play(
            ShowCreation(ellipse),
            Rotating(vps_point, about_point=ORIGIN),
            run_time=6,
            rate_func=lambda t: smooth(t, 3),
        )
        self.wait()

    def rescale_axes(self):
        ellipse = self.ellipse
        axis_labels = self.axis_labels
        equations = self.equations
        vps_point = self.vps_point
        vps_dot = self.vps_dot
        vps_dot.clear_updaters()
        vps_dot.add_updater(
            lambda m: m.move_to(ellipse.get_left())
        )

        brief_circle = ellipse.copy()
        brief_circle.stretch(np.sqrt(10), 0)
        brief_circle.set_stroke(WHITE, 2)

        xy_equation = self.xy_equation = TexMobject(
            "\\frac{1}{2}",
            "\\left(", "x^2", "+", "y^2", "\\right)",
            "=", "\\text{const.}"
        )
        xy_equation.scale(0.8)
        xy_equation.next_to(equations[0], DOWN)

        self.play(ShowCreationThenFadeOut(brief_circle))
        for i, labels, block in zip(it.count(), axis_labels, self.blocks):
            self.play(ShowCreationThenFadeAround(labels[0]))
            self.play(
                ReplacementTransform(labels[0][0], labels[1][0]),
                ReplacementTransform(labels[0][-1], labels[1][-1]),
                FadeInFromDown(labels[1][1:-1]),
                ellipse.stretch, np.sqrt(block.mass), i,
            )
            self.wait()

        vps_dot.clear_updaters()
        vps_dot.add_updater(
            lambda m: m.move_to(self.axes.coords_to_point(
                *self.vps_point.get_location()[:2]
            ))
        )

        self.play(
            FadeInFrom(xy_equation, UP),
            FadeOut(equations[1])
        )
        self.wait()
        curr_x = vps_point.get_location()[0]
        for x in [0.5 * curr_x, 2 * curr_x, curr_x]:
            axes_center = self.axes.coords_to_point(0, 0)
            self.play(
                vps_point.move_to, x * RIGHT,
                UpdateFromFunc(
                    ellipse,
                    lambda m: m.set_width(
                        2 * get_norm(
                            vps_dot.get_center() - axes_center,
                        ),
                    ).move_to(axes_center)
                ),
                run_time=2,
            )
        self.wait()

    def show_starting_point(self):
        vps_dot = self.vps_dot
        block1, block2 = self.blocks

        self.unhalt()
        self.wait(3)
        self.halt()
        self.play(ShowCreationThenFadeAround(vps_dot))
        self.wait()

    def show_initial_collide(self):
        self.unhalt()
        self.go_through_next_collision()
        self.wait()
        self.halt()
        self.wait()

    def ask_about_where_to_land(self):
        self.play(
            Rotating(
                self.vps_point,
                about_point=ORIGIN,
                run_time=6,
                rate_func=lambda t: smooth(t, 3),
            ),
        )
        self.wait(2)

    def show_conservation_of_momentum_equation(self):
        equations = self.equations
        energy_expression, momentum_expression = equations
        momentum_expression.set_fill(opacity=1)
        momentum_expression.shift(MED_SMALL_BUFF * UP)
        momentum_expression.shift(MED_SMALL_BUFF * LEFT)
        xy_equation = self.xy_equation

        momentum_xy_equation = self.momentum_xy_equation = TexMobject(
            "\\sqrt{m_1}", "x", "+",
            "\\sqrt{m_2}", "y", "=",
            "\\text{const.}",
        )
        momentum_xy_equation.set_color_by_tex("m_", BLUE)
        momentum_xy_equation.scale(0.8)
        momentum_xy_equation.next_to(
            momentum_expression, DOWN,
            buff=MED_LARGE_BUFF,
            aligned_edge=RIGHT,
        )

        self.play(
            FadeOut(xy_equation),
            energy_expression.set_fill, {"opacity": 0.2},
            FadeInFromDown(momentum_expression)
        )
        self.play(ShowCreationThenFadeAround(momentum_expression))
        self.wait()
        self.play(FadeInFrom(momentum_xy_equation, UP))
        self.wait()

    def show_momentum_line(self):
        vps_dot = self.vps_dot
        m1 = self.block1.mass
        m2 = self.block2.mass
        line = Line(np.sqrt(m2) * LEFT, np.sqrt(m1) * DOWN)
        line.scale(4)
        line.set_stroke(GREEN, 3)
        line.move_to(vps_dot)

        slope_label = TexMobject(
            "\\text{Slope =}", "-\\sqrt{\\frac{m_1}{m_2}}"
        )
        slope_label.scale(0.8)
        slope_label.next_to(vps_dot, LEFT, LARGE_BUFF)
        slope_arrow = Arrow(
            slope_label.get_right(),
            line.point_from_proportion(0.45),
            buff=SMALL_BUFF,
        )
        slope_group = VGroup(line, slope_label, slope_arrow)
        foreground_mobs = VGroup(
            self.equations[1], self.momentum_xy_equation,
            self.blocks, self.vps_dot
        )
        for mob in foreground_mobs:
            if isinstance(mob, TexMobject):
                mob.set_stroke(BLACK, 3, background=True)

        self.add(line, *foreground_mobs)
        self.play(ShowCreation(line))
        self.play(
            FadeInFrom(slope_label, RIGHT),
            GrowArrow(slope_arrow),
        )
        self.wait()
        self.add(slope_group, *foreground_mobs)
        self.play(slope_group.shift, 4 * RIGHT, run_time=3)
        self.play(slope_group.shift, 5 * LEFT, run_time=3)
        self.play(
            slope_group.shift, RIGHT,
            run_time=1,
            rate_func=lambda t: t**4,
        )
        self.wait()

        self.momentum_line = line
        self.slope_group = slope_group

    def reiterate_meaning_of_line_and_circle(self):
        line_vect = self.momentum_line.get_vector()
        vps_point = self.vps_point

        for x in [0.25, -0.5, 0.25]:
            self.play(
                vps_point.shift, x * line_vect,
                run_time=2
            )
        self.wait()
        self.play(Rotating(
            vps_point,
            about_point=ORIGIN,
            rate_func=lambda t: smooth(t, 3),
        ))
        self.wait()

    def reshow_first_jump(self):
        vps_point = self.vps_point
        curr_point = vps_point.get_location()
        start_point = get_norm(curr_point) * LEFT

        for n in range(8):
            vps_point.move_to(
                [start_point, curr_point][n % 2]
            )
            self.wait(0.5)
        self.wait()

    def show_bounce_off_wall(self):
        self.unhalt()
        self.go_through_next_collision()
        self.halt()

    def show_reflection_about_x(self):
        vps_point = self.vps_point

        curr_location = vps_point.get_location()
        old_location = np.array(curr_location)
        old_location[1] *= -1

        # self.play(
        #     ApplyMethod(
        #         self.block2.move_to, self.wall.get_corner(DR), DL,
        #         path_arc=30 * DEGREES,
        #     )
        # )
        for n in range(4):
            self.play(
                vps_point.move_to,
                [old_location, curr_location][n % 2]
            )
        self.wait()

    def show_remaining_collisions(self):
        line = self.momentum_line
        # slope_group = self.slope_group
        vps_dot = self.vps_dot
        axes = self.axes
        slope = np.sqrt(self.block2.mass / self.block1.mass)

        end_region = Polygon(
            axes.coords_to_point(0, 0),
            axes.coords_to_point(10, 0),
            axes.coords_to_point(10, slope * 10),
            stroke_width=0,
            fill_color=GREEN,
            fill_opacity=0.3
        )

        self.unhalt()
        for x in range(7):
            self.go_through_next_collision()
            if x == 0:
                self.halt()
                self.play(line.move_to, vps_dot)
                self.wait()
                self.unhalt()
        self.play(FadeIn(end_region))
        self.go_through_next_collision()
        self.wait(5)

    # Helpers
    def add_update_line(self, func):
        if hasattr(self, "vps_dot"):
            old_vps_point = self.vps_dot.get_center()
            func()
            self.vps_dot.update()
            new_vps_point = self.vps_dot.get_center()
            line = Line(old_vps_point, new_vps_point)
            line.set_stroke(WHITE, 2)
            self.add(line)
        else:
            func()

    def transfer_momentum(self):
        self.add_update_line(super().transfer_momentum)

    def reflect_block2(self):
        self.add_update_line(super().reflect_block2)


class CircleDiagramFromSlidingBlocks(Scene):
    CONFIG = {
        "BlocksAndWallSceneClass": BlocksAndWallExampleMass1e1,
        "circle_config": {
            "radius": 2,
            "stroke_color": YELLOW,
            "stroke_width": 2,
        },
        "line_style": {
            "stroke_color": WHITE,
            "stroke_width": 1,
        }
    }

    def construct(self):
        sliding_blocks_scene = self.BlocksAndWallSceneClass(
            show_flash_animations=False,
            write_to_movie=False,
            wait_time=0,
        )
        blocks = sliding_blocks_scene.blocks
        times = [pair[1] for pair in blocks.clack_data]
        self.show_circle_lines(
            times=times,
            slope=(-1 / np.sqrt(blocks.mass_ratio))
        )

    def show_circle_lines(self, times, slope):
        circle = Circle(**self.circle_config)
        radius = circle.radius
        theta = np.arctan(-1 / slope)
        axes = VGroup(Line(LEFT, RIGHT), Line(DOWN, UP))
        axes.set_width(circle.get_width() + 1, stretch=True)
        axes.set_height(circle.get_height() + 0.5, stretch=True)
        axes.set_stroke(LIGHT_GREY, 1)

        n_clacks = int(PI / theta)
        points = []
        for n in range(n_clacks + 1):
            theta_mult = (n + 1) // 2
            angle = 2 * theta * theta_mult
            if n % 2 == 0:
                angle *= -1
            new_point = radius * np.array([
                -np.cos(angle), -np.sin(angle), 0
            ])
            points.append(new_point)

        dot = Dot(color=RED)
        dot.move_to(points[0])

        self.add(axes, circle, dot)

        last_time = 0
        for time, p1, p2 in zip(times, points, points[1:]):
            if time > 300:
                time = last_time + 1
            self.wait(time - last_time)
            last_time = time

            line = Line(p1, p2)
            line.set_style(**self.line_style)
            dot.move_to(p2)
            self.add(line, dot)


class CircleDiagramFromSlidingBlocksSameMass(CircleDiagramFromSlidingBlocks):
    CONFIG = {
        "BlocksAndWallSceneClass": BlocksAndWallExampleSameMass
    }


class CircleDiagramFromSlidingBlocksSameMass1e1(CircleDiagramFromSlidingBlocks):
    CONFIG = {
        "BlocksAndWallSceneClass": BlocksAndWallExampleMass1e1
    }


class CircleDiagramFromSlidingBlocks1e2(CircleDiagramFromSlidingBlocks):
    CONFIG = {
        "BlocksAndWallSceneClass": BlocksAndWallExampleMass1e2
    }


class CircleDiagramFromSlidingBlocks1e4(CircleDiagramFromSlidingBlocks):
    CONFIG = {
        "BlocksAndWallSceneClass": BlocksAndWallExampleMass1e4
    }
