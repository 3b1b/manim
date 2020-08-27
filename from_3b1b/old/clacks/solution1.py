from manimlib.imports import *
from from_3b1b.old.clacks.question import *
from from_3b1b.old.div_curl import ShowTwoPopulations


OUTPUT_DIRECTORY = "clacks/solution1"


class FromPuzzleToSolution(MovingCameraScene):
    def construct(self):
        big_rect = FullScreenFadeRectangle()
        big_rect.set_fill(DARK_GREY, 0.5)
        self.add(big_rect)

        rects = VGroup(ScreenRectangle(), ScreenRectangle())
        rects.set_height(3)
        rects.arrange(RIGHT, buff=2)

        titles = VGroup(
            TextMobject("Puzzle"),
            TextMobject("Solution"),
        )

        images = Group(
            ImageMobject("BlocksAndWallExampleMass16"),
            ImageMobject("AnalyzeCircleGeometry"),
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


class First6DigitsOfPi(DigitsOfPi):
    CONFIG = {"n_digits": 6}


class FavoritesInDescription(Scene):
    def construct(self):
        words = TextMobject("(See the description for \\\\ some favorites)")
        words.scale(1.5)
        self.add(words)


class V1EqualsV2Line(Scene):
    def construct(self):
        line = Line(LEFT, 7 * RIGHT)
        eq = TexMobject("v_1", "=", "v_2")
        eq.set_color_by_tex("v_", RED)
        eq.next_to(RIGHT, UR, SMALL_BUFF)
        self.play(
            Write(eq, run_time=1),
            ShowCreation(line),
        )
        self.wait()


class PhaseSpaceTitle(Scene):
    def construct(self):
        title = TextMobject("Phase space")
        title.scale(1.5)
        title.to_edge(UP)
        rect = ScreenRectangle(height=6)
        rect.next_to(title, DOWN)
        self.add(rect)
        self.play(Write(title, run_time=1))
        self.wait()


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
        self.clack_file = os.path.join(SOUND_DIR, "clack.wav")

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
        self.play(randy.change, "confused")
        self.play(Blink(randy))
        self.wait()
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
            self.play(LaggedStartMap(
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
        self.vps_point.save_state()
        for x in range(8):
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
        self.vps_point.restore()
        momentum_decimal.add_updater(
            lambda m: m.set_value(get_momentum())
        )
        momentum_decimal.add_updater(
            lambda m: m.next_to(momentum_const_brace, UP, SMALL_BUFF)
        )
        for x in range(9):
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
        labels.arrange(
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
            "axis_config": {
                "unit_size": 0.7,
            },
        },
        "momentum_line_scale_factor": 4,
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
        equations.arrange(DOWN, buff=LARGE_BUFF)
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
        self.play(LaggedStartMap(
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
        mass_ratio = self.block1.mass / self.block2.mass
        ellipse.replace(
            Polygon(*[
                axes.coords_to_point(x, y * np.sqrt(mass_ratio))
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

        mass_ratio = self.block1.mass / self.block2.mass
        brief_circle = ellipse.copy()
        brief_circle.stretch(np.sqrt(mass_ratio), 0)
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
        line.scale(self.momentum_line_scale_factor)
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

        group = VGroup(
            self.ellipse,
            self.lines[-1],
            self.vps_dot.copy().clear_updaters()
        )
        for x in range(2):
            self.play(
                Rotate(
                    group, PI, RIGHT,
                    about_point=self.axes.coords_to_point(0, 0)
                ),
            )
        self.remove(group[-1])

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
        if not hasattr(self, "lines"):
            self.lines = VGroup()
        if hasattr(self, "vps_dot"):
            old_vps_point = self.vps_dot.get_center()
            func()
            self.vps_dot.update()
            new_vps_point = self.vps_dot.get_center()
            line = Line(old_vps_point, new_vps_point)
            line.set_stroke(WHITE, 2)
            self.add(line)
            self.lines.add(line)
        else:
            func()

    def transfer_momentum(self):
        self.add_update_line(super().transfer_momentum)

    def reflect_block2(self):
        self.add_update_line(super().reflect_block2)


class IntroduceVelocityPhaseSpaceWith16(IntroduceVelocityPhaseSpace):
    CONFIG = {
        "block1_config": {
            "mass": 16,
            "velocity": -0.5,
        },
        "momentum_line_scale_factor": 0,
    }


class SimpleRect(Scene):
    def construct(self):
        self.add(Rectangle(width=6, height=2, color=WHITE))


class SurprisedRandy(Scene):
    def construct(self):
        randy = Randolph()
        self.play(FadeIn(randy))
        self.play(randy.change, "surprised", 3 * UR)
        self.play(Blink(randy))
        self.wait()
        self.play(randy.change, "pondering", 3 * UR)
        self.play(Blink(randy))
        self.wait(2)
        self.play(FadeOut(randy))


class HuntForPi(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Hunt for $\\pi$!",
            bubble_kwargs={"direction": LEFT},
            target_mode="hooray"
        )
        self.change_all_student_modes(
            "hooray",
            added_anims=[self.teacher.change, "happy"]
        )
        self.wait()


class StretchBySqrt10(Scene):
    def construct(self):
        arrow = DoubleArrow(2 * LEFT, 2 * RIGHT)
        arrow.tip[1].shift(0.05 * LEFT)
        value = TexMobject("\\sqrt{10}")
        value.next_to(arrow, UP)
        arrow.save_state()
        arrow.stretch(0, 0)
        self.play(
            Restore(arrow),
            Write(value, run_time=1),
        )
        self.wait()


class XCoordNegative(Scene):
    def construct(self):
        rect = Rectangle(height=4, width=4)
        rect.set_stroke(width=0)
        rect.set_fill(RED, 0.5)
        rect.save_state()
        rect.stretch(0, 0, about_edge=RIGHT)
        self.play(Restore(rect))
        self.wait()


class YCoordZero(Scene):
    def construct(self):
        rect = Rectangle(height=4, width=8)
        rect.set_stroke(width=0)
        rect.set_fill(WHITE, 0.5)
        rect.save_state()
        self.play(
            rect.stretch, 0.01, 1,
            rect.set_fill, {"opacity": 1}
        )
        self.wait()


class CircleDiagramFromSlidingBlocks(Scene):
    CONFIG = {
        "BlocksAndWallSceneClass": BlocksAndWallExampleMass1e1,
        "circle_config": {
            "radius": 2,
            "stroke_color": YELLOW,
            "stroke_width": 3,
        },
        "lines_style": {
            "stroke_color": WHITE,
            "stroke_width": 2,
        },
        "axes_config": {
            "style": {
                "stroke_color": LIGHT_GREY,
                "stroke_width": 1,
            },
            "width": 5,
            "height": 4.5,
        },
        "end_zone_style": {
            "stroke_width": 0,
            "fill_color": GREEN,
            "fill_opacity": 0.3,
        },
        "show_dot": True,
        "show_vector": False,
    }

    def construct(self):
        sliding_blocks_scene = self.BlocksAndWallSceneClass(
            show_flash_animations=False,
            write_to_movie=False,
            wait_time=0,
            file_writer_config={
                "output_directory": ".",
            }
        )
        blocks = sliding_blocks_scene.blocks
        times = [pair[1] for pair in blocks.clack_data]
        self.mass_ratio = 1 / blocks.mass_ratio
        self.show_circle_lines(
            times=times,
            slope=(-1 / np.sqrt(blocks.mass_ratio))
        )

    def show_circle_lines(self, times, slope):
        circle = self.get_circle()
        axes = self.get_axes()
        lines = self.get_lines(circle.radius, slope)
        end_zone = self.get_end_zone()

        dot = Dot(color=RED, radius=0.06)
        dot.move_to(lines[0].get_start())

        vector = Vector(lines[0].get_start())
        vector.set_color(RED)
        vector.add_updater(lambda v: v.put_start_and_end_on(
            ORIGIN, dot.get_center()
        ))
        vector.set_stroke(BLACK, 2, background=True)

        dot.set_opacity(int(self.show_dot))
        vector.set_opacity(int(self.show_vector))

        self.add(end_zone, axes, circle, dot, vector)

        last_time = 0
        for time, line in zip(times, lines):
            if time > 300:
                time = last_time + 1
            self.wait(time - last_time)
            last_time = time
            dot.move_to(line.get_end())
            self.add(line, dot, vector)
        self.wait()

    def get_circle(self):
        circle = Circle(**self.circle_config)
        circle.rotate(PI)  # Nice to have start point on left
        return circle

    def get_axes(self):
        config = self.axes_config
        axes = VGroup(
            Line(LEFT, RIGHT).set_width(config["width"]),
            Line(DOWN, UP).set_height(config["height"])
        )
        axes.set_style(**config["style"])
        return axes

    def get_lines(self, radius, slope):
        theta = np.arctan(-1 / slope)
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

        lines = VGroup(*[
            Line(p1, p2)
            for p1, p2 in zip(points, points[1:])
        ])
        lines.set_style(**self.lines_style)
        return lines

    def get_end_zone(self):
        slope = 1 / np.sqrt(self.mass_ratio)
        x = self.axes_config["width"] / 2
        zone = Polygon(
            ORIGIN, x * RIGHT, x * RIGHT + slope * x * UP,
        )
        zone.set_style(**self.end_zone_style)
        return zone


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


class AnnouncePhaseDiagram(CircleDiagramFromSlidingBlocks):
    def construct(self):
        pd_words = TextMobject("Phase diagram")
        pd_words.scale(1.5)
        pd_words.move_to(self.hold_up_spot, DOWN)
        pd_words_border = pd_words.copy()
        pd_words_border.set_stroke(YELLOW, 2)
        pd_words_border.set_fill(opacity=0)

        simple_words = TextMobject("Simple but powerful")
        simple_words.next_to(pd_words, UP, LARGE_BUFF)
        simple_words.shift(LEFT)
        simple_words.set_color(BLUE)
        simple_arrow = Arrow(
            simple_words.get_bottom(),
            pd_words.get_top(),
            color=simple_words.get_color(),
        )

        self.play(
            self.teacher.change, "raise_right_hand",
            FadeInFromDown(pd_words)
        )
        self.change_student_modes(
            "pondering", "thinking", "pondering",
            added_anims=[ShowCreationThenFadeOut(pd_words_border)]
        )
        self.wait()
        self.play(
            FadeInFrom(simple_words, RIGHT),
            GrowArrow(simple_arrow),
            self.teacher.change, "hooray",
        )
        self.change_student_modes(
            "thinking", "happy", "thinking",
        )
        self.wait(3)


class AnalyzeCircleGeometry(CircleDiagramFromSlidingBlocks, MovingCameraScene):
    CONFIG = {
        "mass_ratio": 16,
        "circle_config": {
            "radius": 3,
        },
        "axes_config": {
            "width": FRAME_WIDTH,
            "height": FRAME_HEIGHT,
        },
        "lines_style": {
            "stroke_width": 2,
        },
    }

    def construct(self):
        self.add_mass_ratio_label()
        self.add_circle_with_lines()
        self.show_equal_arc_lengths()
        self.use_arc_lengths_to_count()
        self.focus_on_three_points()
        self.show_likewise_for_all_jumps()
        self.drop_arc_for_each_hop()
        self.try_adding_one_more_arc()
        self.zoom_out()

    def add_mass_ratio_label(self, mass_ratio=None):
        mass_ratio = mass_ratio or self.mass_ratio
        mass_ratio_label = TextMobject(
            "Mass ratio =", "{:,} : 1".format(mass_ratio)
        )
        mass_ratio_label.to_corner(UL, buff=MED_SMALL_BUFF)
        self.add(mass_ratio_label)
        self.mass_ratio_label = mass_ratio_label

    def add_circle_with_lines(self):
        circle = self.get_circle()
        axes = self.get_axes()
        axes_labels = self.get_axes_labels(axes)
        slope = -np.sqrt(self.mass_ratio)
        lines = self.get_lines(
            radius=circle.radius,
            slope=slope,
        )
        end_zone = self.get_end_zone()

        end_zone_words = TextMobject("End zone")
        end_zone_words.set_height(0.25)
        end_zone_words.next_to(ORIGIN, UP, SMALL_BUFF)
        end_zone_words.to_edge(RIGHT, buff=MED_SMALL_BUFF)
        end_zone_words.set_color(GREEN)

        self.add(
            axes, axes_labels,
            circle, end_zone, end_zone_words,
        )
        self.play(ShowCreation(lines, run_time=3, rate_func=linear))
        self.wait()

        self.set_variables_as_attrs(
            circle, axes, lines,
            end_zone, end_zone_words,
        )

    def show_equal_arc_lengths(self):
        circle = self.circle
        radius = circle.radius
        theta = self.theta = np.arctan(1 / np.sqrt(self.mass_ratio))
        n_arcs = int(PI / (2 * theta))

        lower_arcs = VGroup(*[
            Arc(
                start_angle=(PI + n * 2 * theta),
                angle=(2 * theta),
                radius=radius
            )
            for n in range(n_arcs + 1)
        ])
        lower_arcs[0::2].set_color(RED)
        lower_arcs[1::2].set_color(BLUE)

        upper_arcs = lower_arcs.copy()
        upper_arcs.rotate(PI, axis=RIGHT, about_point=ORIGIN)
        upper_arcs[0::2].set_color(BLUE)
        upper_arcs[1::2].set_color(RED)

        all_arcs = VGroup(*it.chain(*zip(lower_arcs, upper_arcs)))
        if int(PI / theta) % 2 == 1:
            all_arcs.remove(all_arcs[-1])

        arc_copies = lower_arcs.copy()
        for arc_copy in arc_copies:
            arc_copy.generate_target()
        for arc in arc_copies:
            arc.target.rotate(-(arc.start_angle - PI + theta))

        equal_signs = VGroup(*[
            TexMobject("=") for x in range(len(lower_arcs))
        ])
        equal_signs.scale(0.8)
        for sign in equal_signs:
            sign.generate_target()

        movers = VGroup(*it.chain(*zip(
            arc_copies, equal_signs
        )))
        movers.remove(movers[-1])
        mover_targets = VGroup(*[mover.target for mover in movers])
        mover_targets.arrange(RIGHT, buff=SMALL_BUFF)
        mover_targets.next_to(ORIGIN, DOWN)
        mover_targets.to_edge(LEFT)

        equal_signs.scale(0)
        equal_signs.fade(1)
        equal_signs.move_to(mover_targets)

        all_arcs.save_state()
        for arc in all_arcs:
            arc.rotate(90 * DEGREES)
            arc.fade(1)
            arc.set_stroke(width=20)
        self.play(Restore(
            all_arcs, lag_ratio=0.5,
            run_time=2,
        ))
        self.wait()
        self.play(LaggedStartMap(MoveToTarget, movers))
        self.wait()

        self.arcs_equation = movers
        self.lower_arcs = lower_arcs
        self.upper_arcs = upper_arcs
        self.all_arcs = all_arcs

    def use_arc_lengths_to_count(self):
        all_arcs = self.all_arcs
        lines = self.lines

        arc_counts = VGroup()
        for n, arc in enumerate(all_arcs):
            count_mob = Integer(n + 1)
            count_mob.scale(0.75)
            buff = SMALL_BUFF
            if len(all_arcs) > 100:
                count_mob.scale(0.1)
                count_mob.set_stroke(WHITE, 0.25)
                buff = 0.4 * SMALL_BUFF
            point = arc.point_from_proportion(0.5)
            count_mob.next_to(point, normalize(point), buff)
            arc_counts.add(count_mob)

        self.play(
            FadeOut(lines),
            FadeOut(all_arcs),
            FadeOut(self.arcs_equation),
        )
        self.play(
            ShowIncreasingSubsets(all_arcs),
            ShowIncreasingSubsets(lines),
            ShowIncreasingSubsets(arc_counts),
            run_time=5,
            rate_func=bezier([0, 0, 1, 1])
        )
        self.wait()

        for group in all_arcs, arc_counts:
            targets = VGroup()
            for elem in group:
                elem.generate_target()
                targets.add(elem.target)
            targets.space_out_submobjects(1.2)

        kwargs = {
            "rate_func": there_and_back,
            "run_time": 3,
        }
        self.play(
            LaggedStartMap(MoveToTarget, all_arcs, **kwargs),
            LaggedStartMap(MoveToTarget, arc_counts, **kwargs),
        )

        self.arc_counts = arc_counts

    def focus_on_three_points(self):
        lines = self.lines
        arcs = self.all_arcs
        arc_counts = self.arc_counts
        theta = self.theta

        arc = arcs[4]

        lines.save_state()
        line_pair = lines[3:5]
        lines_to_fade = VGroup(*lines[:3], *lines[5:])

        three_points = [
            line_pair[0].get_start(),
            line_pair[1].get_start(),
            line_pair[1].get_end(),
        ]
        three_dots = VGroup(*map(Dot, three_points))
        three_dots.set_color(RED)

        theta_arc = Arc(
            radius=1,
            start_angle=-90 * DEGREES,
            angle=theta
        )
        theta_arc.shift(three_points[1])
        theta_label = TexMobject("\\theta")
        theta_label.next_to(theta_arc, DOWN, SMALL_BUFF)

        center_lines = VGroup(
            Line(three_points[0], ORIGIN),
            Line(ORIGIN, three_points[2]),
        )
        center_lines.match_style(line_pair)

        two_theta_arc = Arc(
            radius=1,
            start_angle=(center_lines[0].get_angle() + PI),
            angle=2 * theta
        )
        two_theta_label = TexMobject("2\\theta")
        arc_center = two_theta_arc.point_from_proportion(0.5)
        two_theta_label.next_to(
            arc_center, normalize(arc_center), SMALL_BUFF
        )
        two_theta_label.shift(SMALL_BUFF * RIGHT)

        to_fade = VGroup(arc_counts, arcs, lines_to_fade)

        self.play(
            LaggedStartMap(
                FadeOut, VGroup(*to_fade.family_members_with_points())
            )
        )
        lines_to_fade.fade(1)
        self.play(FadeInFromLarge(three_dots[0]))
        self.play(TransformFromCopy(*three_dots[:2]))
        self.play(TransformFromCopy(*three_dots[1:3]))
        self.wait()
        self.play(
            ShowCreation(theta_arc),
            FadeInFrom(theta_label, UP)
        )
        self.wait()
        self.play(
            line_pair.set_stroke, WHITE, 1,
            TransformFromCopy(line_pair, center_lines),
            TransformFromCopy(theta_arc, two_theta_arc),
            TransformFromCopy(theta_label, two_theta_label),
        )
        self.wait()
        self.play(
            TransformFromCopy(two_theta_arc, arc),
            two_theta_label.move_to, 2.7 * arc_center,
        )
        self.wait()

        self.three_dots = three_dots
        self.theta_group = VGroup(theta_arc, theta_label)
        self.center_lines_group = VGroup(
            center_lines, two_theta_arc,
        )
        self.two_theta_label = two_theta_label

    def show_likewise_for_all_jumps(self):
        lines = self.lines
        arcs = self.all_arcs

        every_other_line = lines[::2]

        self.play(
            Restore(
                lines,
                lag_ratio=0.5,
                run_time=2
            ),
            FadeOut(self.center_lines_group),
            FadeOut(self.three_dots),
        )
        self.play(LaggedStartMap(
            ApplyFunction, every_other_line,
            lambda line: (
                lambda l: l.scale(10 / l.get_length()).set_stroke(BLUE, 3),
                line
            )
        ))
        self.play(Restore(lines))
        self.wait()

        # Shift theta label
        last_point = lines[3].get_end()
        last_arc = arcs[4]
        two_theta_label = self.two_theta_label
        theta_group_copy = self.theta_group.copy()
        for line, arc in zip(lines[5:10:2], arcs[6:11:2]):
            new_point = line.get_end()
            arc_point = arc.point_from_proportion(0.5)
            self.play(
                theta_group_copy.shift, new_point - last_point,
                two_theta_label.move_to, 1.1 * arc_point,
                FadeIn(arc),
                FadeOut(last_arc),
            )
            self.wait()
            last_point = new_point
            last_arc = arc
        self.play(
            FadeOut(theta_group_copy),
            FadeOut(two_theta_label),
            FadeOut(last_arc),
        )
        self.wait()

    def drop_arc_for_each_hop(self):
        lines = self.lines
        arcs = self.all_arcs

        two_theta_labels = VGroup()
        wedges = VGroup()
        for arc in arcs:
            label = TexMobject("2\\theta")
            label.scale(0.8)
            label.move_to(1.1 * arc.point_from_proportion(0.5))
            two_theta_labels.add(label)

            wedge = arc.copy()
            wedge.add_line_to(ORIGIN)
            wedge.add_line_to(wedge.points[0])
            wedge.set_stroke(width=0)
            wedge.set_fill(arc.get_color(), 0.2)
            wedges.add(wedge)

        self.remove(lines)
        for line, arc, label, wedge in zip(lines, arcs, two_theta_labels, wedges):
            self.play(
                ShowCreation(line),
                FadeInFrom(arc, normalize(arc.get_center())),
                FadeInFrom(label, normalize(arc.get_center())),
                FadeIn(wedge),
            )

        self.wedges = wedges
        self.two_theta_labels = two_theta_labels

    def try_adding_one_more_arc(self):
        wedges = self.wedges
        theta = self.theta

        last_wedge = wedges[-1]
        new_wedge = last_wedge.copy()
        new_wedge.set_color(PURPLE)
        new_wedge.set_stroke(WHITE, 1)

        self.play(FadeIn(new_wedge))
        for angle in [-2 * theta, 4 * DEGREES, -2 * DEGREES]:
            self.play(Rotate(new_wedge, angle, about_point=ORIGIN))
            self.wait()
        self.play(
            new_wedge.shift, 10 * RIGHT,
            rate_func=running_start,
            path_arc=-30 * DEGREES,
        )
        self.remove(new_wedge)

    def zoom_out(self):
        frame = self.camera_frame
        self.play(
            frame.scale, 2, {"about_point": (TOP + RIGHT_SIDE)},
            run_time=3
        )
        self.wait()

    # Helpers
    def get_axes_labels(self, axes):
        axes_labels = VGroup(
            TexMobject("x = ", "\\sqrt{m_1}", "\\cdot", "v_1"),
            TexMobject("y = ", "\\sqrt{m_2}", "\\cdot", "v_2"),
        )
        for label in axes_labels:
            label.set_height(0.4)
        axes_labels[0].next_to(ORIGIN, DOWN, SMALL_BUFF)
        axes_labels[0].to_edge(RIGHT, MED_SMALL_BUFF)
        axes_labels[1].next_to(ORIGIN, RIGHT, SMALL_BUFF)
        axes_labels[1].to_edge(UP, SMALL_BUFF)
        return axes_labels


class InscribedAngleTheorem(Scene):
    def construct(self):
        self.add_title()
        self.show_circle()
        self.let_point_vary()

    def add_title(self):
        title = TextMobject("Inscribed angle theorem")
        title.scale(1.5)
        title.to_edge(UP)
        self.add(title)
        self.title = title

    def show_circle(self):
        # Boy is this over engineered...
        circle = self.circle = Circle(
            color=BLUE,
            radius=2,
        )
        center_dot = Dot(circle.get_center(), color=WHITE)
        self.add(circle, center_dot)

        angle_trackers = self.angle_trackers = VGroup(
            ValueTracker(TAU / 4),
            ValueTracker(PI),
            ValueTracker(-TAU / 4),
        )

        def get_point(angle):
            return circle.point_from_proportion(
                (angle % TAU) / TAU
            )

        def get_dot(angle):
            dot = Dot(get_point(angle))
            dot.set_color(RED)
            dot.set_stroke(BLACK, 3, background=True)
            return dot

        def get_dots():
            return VGroup(*[
                get_dot(at.get_value())
                for at in angle_trackers
            ])

        def update_labels(labels):
            center = circle.get_center()
            for dot, label in zip(dots, labels):
                label.move_to(
                    center + 1.2 * (dot.get_center() - center)
                )

        def get_lines():
            lines = VGroup(*[
                Line(d1.get_center(), d2.get_center())
                for d1, d2 in zip(dots, dots[1:])
            ])
            lines.set_stroke(WHITE, 3)
            return lines

        def get_center_lines():
            points = [
                dots[0].get_center(),
                circle.get_center(),
                dots[2].get_center(),
            ]
            lines = VGroup(*[
                Line(p1, p2)
                for p1, p2 in zip(points, points[1:])
            ])
            lines.set_stroke(LIGHT_GREY, 3)
            return lines

        def get_angle_label(lines, tex, reduce_angle=True):
            a1 = (lines[0].get_angle() + PI) % TAU
            a2 = lines[1].get_angle()
            diff = (a2 - a1)
            if reduce_angle:
                diff = ((diff + PI) % TAU) - PI
            point = lines[0].get_end()
            arc = Arc(
                start_angle=a1,
                angle=diff,
                radius=0.5,
            )
            arc.shift(point)
            arc_center = arc.point_from_proportion(0.5)
            label = TexMobject(tex)
            vect = (arc_center - point)
            vect = (0.3 + get_norm(vect)) * normalize(vect)
            label.move_to(point + vect)
            return VGroup(arc, label)

        def get_theta_label():
            return get_angle_label(lines, "\\theta")

        def get_2theta_label():
            return get_angle_label(center_lines, "2\\theta", False)

        dots = get_dots()
        lines = get_lines()
        center_lines = get_center_lines()
        labels = VGroup(*[
            TexMobject("P_{}".format(n + 1))
            for n in range(3)
        ])
        update_labels(labels)
        theta_label = get_theta_label()
        two_theta_label = get_2theta_label()

        self.play(
            FadeInFromDown(labels[0]),
            FadeInFromLarge(dots[0]),
        )
        self.play(
            TransformFromCopy(*labels[:2]),
            TransformFromCopy(*dots[:2]),
            ShowCreation(lines[0]),
        )
        self.play(
            ShowCreation(lines[1]),
            TransformFromCopy(*labels[1:3]),
            TransformFromCopy(*dots[1:3]),
            Write(theta_label),
        )
        self.wait()

        # Add updaters
        labels.add_updater(update_labels)
        dots.add_updater(lambda m: m.become(get_dots()))
        lines.add_updater(lambda m: m.become(get_lines()))
        center_lines.add_updater(lambda m: m.become(get_center_lines()))
        theta_label.add_updater(lambda m: m.become(get_theta_label()))
        two_theta_label.add_updater(lambda m: m.become(get_2theta_label()))

        self.add(labels, lines, dots, theta_label)
        # Further animations
        self.play(
            angle_trackers[0].set_value, TAU / 8,
        )
        self.play(
            angle_trackers[2].set_value, -TAU / 8,
        )
        self.wait()
        center_lines.update()
        two_theta_label.update()
        self.play(
            TransformFromCopy(lines.copy().clear_updaters(), center_lines),
            TransformFromCopy(theta_label.copy().clear_updaters(), two_theta_label),
        )
        self.wait()

        self.add(center_lines, two_theta_label)

    def let_point_vary(self):
        p1_tracker, p2_tracker, p3_tracker = self.angle_trackers

        kwargs = {"run_time": 2}
        for angle in [TAU / 4, 3 * TAU / 4]:
            self.play(
                p2_tracker.set_value, angle,
                **kwargs
            )
            self.wait()
        self.play(
            p1_tracker.set_value, PI,
            **kwargs
        )
        self.wait()
        self.play(
            p3_tracker.set_value, TAU / 3,
            **kwargs
        )
        self.wait()
        self.play(
            p2_tracker.set_value, 7 * TAU / 8,
            **kwargs
        )
        self.wait()


class SimpleSlopeLabel(Scene):
    def construct(self):
        label = TexMobject(
            "\\text{Slope}", "=",
            "-\\frac{\\sqrt{m_1}}{\\sqrt{m_2}}"
        )
        vector = Vector(DOWN + 2 * LEFT, color=WHITE)
        vector.move_to(label[0].get_bottom(), UR)
        vector.shift(SMALL_BUFF * DOWN)
        self.play(
            Write(label),
            GrowArrow(vector),
        )
        self.wait()


class AddTwoThetaManyTimes(Scene):
    def construct(self):
        expression = TexMobject(
            "2\\theta", "+",
            "2\\theta", "+",
            "2\\theta", "+",
            "\\cdots", "+",
            "2\\theta",
            "<", "2\\pi",
        )
        expression.to_corner(UL)

        brace = Brace(expression[:-2], DOWN)
        question = brace.get_text("Max number of times?")
        question.set_color(YELLOW)

        central_question_group = self.get_central_question()
        simplified, lil_brace, new_question = central_question_group
        central_question_group.next_to(question, DOWN, LARGE_BUFF)
        new_question.align_to(question, LEFT)

        for n in range(5):
            self.add(expression[:2 * n + 1])
            self.wait(0.25)
        self.play(
            FadeInFrom(expression[-2:], LEFT),
            GrowFromCenter(brace),
            FadeInFrom(question, UP)
        )
        self.wait(3)
        self.play(
            TransformFromCopy(expression[:-2], simplified[:3]),
            TransformFromCopy(expression[-2:], simplified[3:]),
            TransformFromCopy(brace, lil_brace),
        )
        self.play(Write(new_question))
        self.wait()

        self.central_question_group = central_question_group
        self.show_example()

    def get_central_question(self, brace_vect=DOWN):
        expression = TexMobject(
            "N", "\\cdot", "\\theta", "<", "\\pi"
        )
        N = expression[0]
        N.set_color(BLUE)
        brace = Brace(N, brace_vect, buff=SMALL_BUFF)
        question = brace.get_text(
            "Maximal integer?",
        )
        question.set_color(YELLOW)
        result = VGroup(expression, brace, question)
        result.to_corner(UL)
        return result

    def show_example(self):
        equation = self.get_changable_equation(0.01, n_decimal_places=2)
        expression, brace, question = self.central_question_group
        N_mob, dot_theta_eq, rhs, comp_pi = equation

        equation.next_to(expression, DOWN, 2, aligned_edge=LEFT)

        self.play(
            TransformFromCopy(expression[0], N_mob),
            TransformFromCopy(expression[1:4], dot_theta_eq),
            TransformFromCopy(expression[4], rhs),
            TransformFromCopy(expression[4], comp_pi),
        )
        self.wait()
        self.play(
            ChangeDecimalToValue(N_mob, 314, run_time=5)
        )
        self.wait()
        self.play(ChangeDecimalToValue(N_mob, 315))
        self.wait()
        self.play(ChangeDecimalToValue(N_mob, 314))
        self.wait()
        self.play(ShowCreationThenFadeAround(N_mob))

    #
    def get_changable_equation(self, value, tex_string=None, n_decimal_places=10):
        int_mob = Integer(1)
        int_mob.set_color(BLUE)
        formatter = "({:0." + str(n_decimal_places) + "f})"
        tex_string = tex_string or formatter.format(value)
        tex_mob = TexMobject("\\cdot", tex_string, "=")
        rhs = DecimalNumber(value, num_decimal_places=n_decimal_places)

        def align_number(mob):
            y0 = mob[0].get_center()[1]
            y1 = tex_mob[1][1:-1].get_center()[1]
            mob.shift((y1 - y0) * UP)

        int_mob.add_updater(
            lambda m: m.next_to(tex_mob, LEFT, SMALL_BUFF)
        )
        int_mob.add_updater(align_number)
        rhs.add_updater(
            lambda m: m.set_value(value * int_mob.get_value())
        )
        rhs.add_updater(
            lambda m: m.next_to(tex_mob, RIGHT, SMALL_BUFF)
        )
        rhs.add_updater(align_number)

        def get_comp_pi():
            if rhs.get_value() < np.pi:
                result = TexMobject("< \\pi")
                result.set_color(GREEN)
            elif rhs.get_value() > np.pi:
                result = TexMobject("> \\pi")
                result.set_color(RED)
            else:
                result = TexMobject("= \\pi")
            result.next_to(rhs, RIGHT, 2 * SMALL_BUFF)
            result[1].scale(1.5, about_edge=LEFT)
            return result

        comp_pi = always_redraw(get_comp_pi)

        return VGroup(int_mob, tex_mob, rhs, comp_pi)


class AskAboutTheta(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "But what is $\\theta$?",
            target_mode="raise_left_hand",
        )
        self.change_student_modes(
            "confused", "sassy", "raise_left_hand",
            added_anims=[self.teacher.change, "happy"]
        )
        self.wait(3)


class ComputeThetaFor1e4(AnalyzeCircleGeometry):
    CONFIG = {
        "mass_ratio": 100,
    }

    def construct(self):
        self.add_mass_ratio_label()
        self.add_circle_with_three_lines()
        self.write_slope()
        self.show_tangent()

    def add_circle_with_three_lines(self):
        circle = self.get_circle()
        axes = self.get_axes()
        slope = -np.sqrt(self.mass_ratio)
        lines = self.get_lines(
            radius=circle.radius,
            slope=slope,
        )
        end_zone = self.get_end_zone()
        axes_labels = self.get_axes_labels(axes)
        axes.add(axes_labels)

        lines_to_fade = VGroup(*lines[:11], *lines[13:])
        two_lines = lines[11:13]

        theta = self.theta = np.arctan(-1 / slope)
        arc = Arc(
            start_angle=(-90 * DEGREES),
            angle=theta,
            radius=2,
            arc_center=two_lines[0].get_end(),
        )
        theta_label = TexMobject("\\theta")
        theta_label.scale(0.8)
        theta_label.next_to(arc, DOWN, SMALL_BUFF)

        self.add(end_zone, axes, circle)
        self.play(ShowCreation(lines, rate_func=linear))
        self.play(
            lines_to_fade.set_stroke, WHITE, 1, 0.3,
            ShowCreation(arc),
            FadeInFrom(theta_label, UP)
        )

        self.two_lines = two_lines
        self.lines = lines
        self.circle = circle
        self.axes = axes
        self.theta_label_group = VGroup(theta_label, arc)

    def write_slope(self):
        line = self.two_lines[1]
        slope_label = TexMobject(
            "\\text{Slope}", "=",
            "\\frac{\\text{rise}}{\\text{run}}", "=",
            "\\frac{-\\sqrt{m_1}}{\\sqrt{m_2}}", "=", "-10"
        )
        for mob in slope_label:
            mob.add_to_back(mob.copy().set_stroke(BLACK, 6))
        slope_label.next_to(line.get_center(), UR, buff=1)
        slope_arrow = Arrow(
            slope_label[0].get_bottom(),
            line.point_from_proportion(0.45),
            color=RED,
            buff=SMALL_BUFF,
        )
        new_line = line.copy().set_color(RED)

        self.play(
            FadeInFromDown(slope_label[:3]),
            ShowCreation(new_line),
            GrowArrow(slope_arrow),
        )
        self.remove(new_line)
        line.match_style(new_line)
        self.play(
            FadeInFrom(slope_label[3:5], LEFT)
        )
        self.wait()
        self.play(
            Write(slope_label[5]),
            TransformFromCopy(
                self.mass_ratio_label[1][:3],
                slope_label[6]
            )
        )
        self.wait()

        self.slope_label = slope_label
        self.slope_arrow = slope_arrow

    def show_tangent(self):
        l1, l2 = self.two_lines
        theta = self.theta
        theta_label_group = self.theta_label_group

        tan_equation = TexMobject(
            "\\tan", "(", "\\theta", ")", "=",
            "{\\text{run}", "\\over", "-\\text{rise}}", "=",
            "\\frac{1}{10}",
        )
        tan_equation.scale(0.9)
        tan_equation.to_edge(LEFT, buff=MED_SMALL_BUFF)
        tan_equation.shift(2 * UP)
        run_word = tan_equation.get_part_by_tex("run")
        rise_word = tan_equation.get_part_by_tex("rise")

        p1, p2 = l1.get_start(), l1.get_end()
        p3 = p1 + get_norm(p2 - p1) * np.tan(theta) * RIGHT
        triangle = Polygon(p1, p2, p3)
        triangle.set_stroke(width=0)
        triangle.set_fill(GREEN, 0.5)

        opposite = Line(p1, p3)
        adjacent = Line(p1, p2)
        opposite.set_stroke(BLUE, 3)
        adjacent.set_stroke(PINK, 3)

        arctan_equation = TexMobject(
            "\\theta", "=", "\\arctan", "(", "1 / 10", ")"
        )
        arctan_equation.next_to(tan_equation, DOWN, MED_LARGE_BUFF)

        self.play(
            FadeInFromDown(tan_equation[:8]),
        )
        self.play(
            TransformFromCopy(theta_label_group[1], opposite),
            run_word.set_color, opposite.get_color()
        )
        self.play(WiggleOutThenIn(run_word))
        self.play(
            TransformFromCopy(opposite, adjacent),
            rise_word.set_color, adjacent.get_color()
        )
        self.play(WiggleOutThenIn(rise_word))
        self.wait()
        self.play(TransformFromCopy(
            self.slope_label[-1],
            tan_equation[-2:],
        ))
        self.wait(2)

        indices = [2, 4, 0, 1, -1, 3]
        movers = VGroup(*[tan_equation[i] for i in indices]).copy()
        for mover, target in zip(movers, arctan_equation):
            mover.target = target
        # Swap last two
        sm = movers.submobjects
        sm[-1], sm[-2] = sm[-2], sm[-1]
        self.play(LaggedStartMap(
            Transform, movers[:-1],
            lambda m: (m, m.target),
            lag_ratio=1,
            run_time=1,
            path_arc=PI / 6,
        ))
        self.play(MoveToTarget(movers[-1]))
        self.remove(movers)
        self.add(arctan_equation)
        self.play(ShowCreationThenFadeAround(arctan_equation))
        self.wait()


class ThetaChart(Scene):
    def construct(self):
        self.create_columns()
        self.populate_columns()
        self.show_values()
        self.highlight_example(2)
        self.highlight_example(3)

    def create_columns(self):
        titles = VGroup(*[
            TextMobject("Mass ratio"),
            TextMobject("$\\theta$ formula"),
            TextMobject("$\\theta$ value"),
        ])
        titles.scale(1.5)
        titles.arrange(RIGHT, buff=1.5)
        titles[1].shift(MED_SMALL_BUFF * LEFT)
        titles[2].shift(MED_SMALL_BUFF * RIGHT)
        titles.to_corner(UL)

        lines = VGroup()
        for t1, t2 in zip(titles, titles[1:]):
            line = Line(TOP, BOTTOM)
            x = np.mean([t1.get_center()[0], t2.get_center()[0]])
            line.shift(x * RIGHT)
            lines.add(line)

        h_line = Line(LEFT_SIDE, RIGHT_SIDE)
        h_line.next_to(titles, DOWN)
        h_line.to_edge(LEFT, buff=0)
        lines.add(h_line)
        lines.set_stroke(WHITE, 1)

        self.play(
            LaggedStartMap(FadeInFromDown, titles),
            LaggedStartMap(ShowCreation, lines, lag_ratio=0.8),
        )

        self.h_line = h_line
        self.titles = titles

    def populate_columns(self):
        top_h_line = self.h_line
        x_vals = [t.get_center()[0] for t in self.titles]

        entries = [
            (
                "$m_1$ : $m_2$",
                "$\\arctan(\\sqrt{m_2} / \\sqrt{m_1})$",
                ""
            )
        ] + [
            (
                "{:,} : 1".format(10**(2 * exp)),
                "$\\arctan(1 / {:,})$".format(10**exp),
                self.get_theta_decimal(exp),
            )
            for exp in [1, 2, 3, 4, 5]
        ]

        h_lines = VGroup(top_h_line)
        entry_mobs = VGroup()
        for entry in entries:
            mobs = VGroup(*map(TextMobject, entry))
            for mob, x in zip(mobs, x_vals):
                mob.shift(x * RIGHT)
            delta_y = (mobs.get_height() / 2) + MED_SMALL_BUFF
            y = h_lines[-1].get_center()[1] - delta_y
            mobs.shift(y * UP)
            mobs[0].set_color(BLUE)
            mobs[2].set_color(YELLOW)
            entry_mobs.add(mobs)

            h_line = DashedLine(LEFT_SIDE, RIGHT_SIDE)
            h_line.shift((y - delta_y) * UP)
            h_lines.add(h_line)

        self.play(
            LaggedStartMap(
                FadeInFromDown,
                VGroup(*[em[:2] for em in entry_mobs]),
            ),
            LaggedStartMap(ShowCreation, h_lines[1:]),
            lag_ratio=0.1,
            run_time=5,
        )

        self.entry_mobs = entry_mobs
        self.h_lines = h_lines

    def show_values(self):
        values = VGroup(*[em[2] for em in self.entry_mobs])
        for value in values:
            self.play(LaggedStartMap(
                FadeIn, value,
                lag_ratio=0.1,
                run_time=0.5
            ))
            self.wait(0.5)

    def highlight_example(self, exp):
        entry_mobs = self.entry_mobs
        example = entry_mobs[exp]
        other_entries = VGroup(*entry_mobs[:exp], *entry_mobs[exp + 1:])

        value = example[-1]
        rhs = TexMobject("\\approx {:}".format(10**(-exp)))
        rhs.next_to(value, RIGHT)
        rhs.to_edge(RIGHT, buff=MED_SMALL_BUFF)
        value.generate_target()
        value.target.set_fill(opacity=1)
        value.target.scale(0.9)
        value.target.next_to(rhs, LEFT, SMALL_BUFF)

        self.play(
            other_entries.set_fill, {"opacity": 0.25},
            example.set_fill, {"opacity": 1},
            ShowCreationThenFadeAround(example)
        )
        self.wait()
        self.play(
            MoveToTarget(value),
            Write(rhs),
        )
        self.wait()
        value.add(rhs)

    def get_theta_decimal(self, exp):
        theta = np.arctan(10**(-exp))
        rounded_theta = np.floor(1e10 * theta) / 1e10
        return "{:0.10f}\\dots".format(rounded_theta)


class CentralQuestionFor1e2(AddTwoThetaManyTimes):
    CONFIG = {
        "exp": 2,
    }

    def construct(self):
        exp = self.exp
        question = self.get_central_question(UP)
        pi_value = TexMobject(" = {:0.10f}\\dots".format(PI))
        pi_value.next_to(question[0][-1], RIGHT, SMALL_BUFF)
        pi_value.shift(0.3 * SMALL_BUFF * UP)
        question.add(pi_value)

        max_count = int(PI * 10**exp)

        question.center().to_edge(UP)
        self.add(question)

        b10_equation = self.get_changable_equation(
            10**(-exp), n_decimal_places=exp
        )
        b10_equation.next_to(question, DOWN, buff=1.5)
        arctan_equation = self.get_changable_equation(
            np.arctan(10**(-exp)), n_decimal_places=10,
        )
        arctan_equation.next_to(b10_equation, DOWN, MED_LARGE_BUFF)
        eq_centers = [
            eq[1][2].get_center()
            for eq in [b10_equation, arctan_equation]
        ]
        arctan_equation.shift((eq_centers[1][0] - eq_centers[1][0]) * RIGHT)

        # b10_brace = Brace(b10_equation[1][1][1:-1], UP)
        arctan_brace = Brace(arctan_equation[1][1][1:-1], DOWN)
        # b10_tex = b10_brace.get_tex("1 / 10")
        arctan_tex = arctan_brace.get_tex(
            "\\theta = \\arctan(1 / {:,})".format(10**exp)
        )

        int_mobs = b10_equation[0], arctan_equation[0]

        self.add(*b10_equation, *arctan_equation)
        # self.add(b10_brace, b10_tex)
        self.add(arctan_brace, arctan_tex)

        self.wait()
        self.play(*[
            ChangeDecimalToValue(int_mob, max_count, run_time=8)
            for int_mob in int_mobs
        ])
        self.wait()
        self.play(*[
            ChangeDecimalToValue(int_mob, max_count + 1, run_time=1)
            for int_mob in int_mobs
        ])
        self.wait()
        self.play(*[
            ChangeDecimalToValue(int_mob, max_count, run_time=1)
            for int_mob in int_mobs
        ])
        self.play(ShowCreationThenFadeAround(int_mobs[1]))
        self.wait()


class AnalyzeCircleGeometry1e2(AnalyzeCircleGeometry):
    CONFIG = {
        "mass_ratio": 100,
    }


class CentralQuestionFor1e3(CentralQuestionFor1e2):
    CONFIG = {"exp": 3}


class AskAboutArctanOfSmallValues(TeacherStudentsScene):
    def construct(self):
        self.add_title()

        equation1 = TexMobject(
            "\\arctan", "(", "x", ")", "\\approx", "x"
        )
        equation1.set_color_by_tex("arctan", YELLOW)
        equation2 = TexMobject(
            "x", "\\approx", "\\tan", "(", "x", ")",
        )
        equation2.set_color_by_tex("tan", BLUE)
        for mob in equation1, equation2:
            mob.move_to(self.hold_up_spot, DOWN)

        self.play(
            FadeInFromDown(equation1),
            self.teacher.change, "raise_right_hand",
            self.get_student_changes(
                "erm", "sassy", "confused"
            )
        )
        self.look_at(3 * UL)
        self.play(equation1.shift, UP)
        self.play(
            TransformFromCopy(
                VGroup(*[equation1[i] for i in (2, 4, 5)]),
                VGroup(*[equation2[i] for i in (0, 1, 4)]),
            )
        )
        self.play(
            TransformFromCopy(
                VGroup(*[equation1[i] for i in (0, 1, 3)]),
                VGroup(*[equation2[i] for i in (2, 3, 5)]),
            ),
            self.get_student_changes(
                "confused", "erm", "sassy",
            ),
        )
        self.look_at(3 * UL)
        self.wait(3)
        # self.student_says("Why?", target_mode="maybe")
        # self.wait(3)

    def add_title(self):
        title = TextMobject("For small $x$")
        subtitle = TextMobject("(e.g. $x = 0.001$)")
        subtitle.scale(0.75)
        subtitle.next_to(title, DOWN)
        title.add(subtitle)
        # title.scale(1.5)
        # title.to_edge(UP, buff=MED_SMALL_BUFF)
        title.move_to(self.hold_up_spot)
        title.to_edge(UP)
        self.add(title)


class ActanAndTanGraphs(GraphScene):
    CONFIG = {
        "x_min": -PI / 8,
        "x_max": 5 * PI / 8,
        "y_min": -PI / 8,
        "y_max": 4 * PI / 8,
        "x_tick_frequency": PI / 8,
        "x_leftmost_tick": -PI / 8,
        "y_tick_frequency": PI / 8,
        "y_leftmost_tick": -PI / 8,
        "x_axis_width": 10,
        "y_axis_height": 7,
        "graph_origin": 2.5 * DOWN + 5 * LEFT,
        "num_graph_anchor_points": 500,
    }

    def construct(self):
        self.setup_axes()
        axes = self.axes
        labels = VGroup(
            TexMobject("\\pi / 8"),
            TexMobject("\\pi / 4"),
            TexMobject("3\\pi / 8"),
            TexMobject("\\pi / 2"),
        )
        for n, label in zip(it.count(1), labels):
            label.scale(0.75)
            label.next_to(self.coords_to_point(n * PI / 8, 0), DOWN)
            self.add(label)

        id_graph = self.get_graph(lambda x: x, x_max=1.5)
        arctan_graph = self.get_graph(np.arctan, x_max=1.5)
        tan_graph = self.get_graph(np.tan, x_max=1.5)
        graphs = VGroup(id_graph, arctan_graph, tan_graph)

        id_label = TexMobject("f(x) = x")
        arctan_label = TexMobject("\\arctan(x)")
        tan_label = TexMobject("\\tan(x)")
        labels = VGroup(id_label, arctan_label, tan_label)
        for label, graph in zip(labels, graphs):
            label.match_color(graph)
            label.next_to(graph.points[-1], RIGHT)
            if label.get_bottom()[1] > FRAME_HEIGHT / 2:
                label.next_to(graph.point_from_proportion(0.75), LEFT)

        arctan_x_tracker = ValueTracker(3 * PI / 8)
        arctan_v_line = always_redraw(
            lambda: self.get_vertical_line_to_graph(
                arctan_x_tracker.get_value(),
                arctan_graph,
                line_class=DashedLine,
                color=WHITE,
            )
        )
        tan_x_tracker = ValueTracker(2 * PI / 8)
        tan_v_line = always_redraw(
            lambda: self.get_vertical_line_to_graph(
                tan_x_tracker.get_value(),
                tan_graph,
                line_class=DashedLine,
                color=WHITE,
            )
        )

        self.add(axes)
        self.play(
            ShowCreation(id_graph),
            Write(id_label)
        )
        self.play(
            ShowCreation(arctan_graph),
            Write(arctan_label)
        )
        self.add(arctan_v_line)
        self.play(arctan_x_tracker.set_value, 0, run_time=2)
        self.wait()
        self.play(
            TransformFromCopy(arctan_graph, tan_graph),
            TransformFromCopy(arctan_label, tan_label),
        )
        self.add(tan_v_line)
        self.play(tan_x_tracker.set_value, 0, run_time=2)
        self.wait()


class UnitCircleIntuition(Scene):
    def construct(self):
        self.draw_unit_circle()
        self.show_angle()
        self.show_fraction()
        self.show_fraction_approximation()

    def draw_unit_circle(self):
        unit_size = 2.5
        axes = Axes(
            axis_config={"unit_size": unit_size},
            x_min=-2.5, x_max=2.5,
            y_min=-1.5, y_max=1.5,
        )
        axes.set_stroke(width=1)
        self.add(axes)

        radius_line = Line(ORIGIN, axes.coords_to_point(1, 0))
        radius_line.set_color(BLUE)
        r_label = TexMobject("1")
        r_label.add_updater(
            lambda m: m.next_to(radius_line.get_center(), DOWN, SMALL_BUFF)
        )
        circle = Circle(radius=unit_size, color=WHITE)

        self.add(radius_line, r_label)
        self.play(
            Rotating(radius_line, about_point=ORIGIN),
            ShowCreation(circle),
            run_time=2,
            rate_func=smooth,
        )

        self.radius_line = radius_line
        self.r_label = r_label
        self.circle = circle
        self.axes = axes

    def show_angle(self):
        circle = self.circle

        tan_eq = TexMobject(
            "\\tan", "(", "\\theta", ")", "=",
            tex_to_color_map={"\\theta": RED},
        )
        tan_eq.next_to(ORIGIN, RIGHT, LARGE_BUFF)
        tan_eq.to_edge(UP, buff=LARGE_BUFF)

        theta_tracker = ValueTracker(0)
        get_theta = theta_tracker.get_value

        def get_r_line():
            return Line(
                circle.get_center(),
                circle.point_at_angle(get_theta())
            )
        r_line = always_redraw(get_r_line)

        def get_arc(radius=None, **kwargs):
            if radius is None:
                alpha = inverse_interpolate(0, 20 * DEGREES, get_theta())
                radius = interpolate(2, 1, alpha)
            return Arc(
                radius=radius,
                start_angle=0,
                angle=get_theta(),
                arc_center=circle.get_center(),
                **kwargs
            )
        arc = always_redraw(get_arc)
        self.circle_arc = always_redraw(
            lambda: get_arc(radius=circle.radius, color=RED)
        )

        def get_theta_label():
            label = TexMobject("\\theta")
            label.set_height(min(arc.get_height(), 0.3))
            label.set_color(RED)
            center = circle.get_center()
            vect = arc.point_from_proportion(0.5) - center
            vect = (get_norm(vect) + 2 * SMALL_BUFF) * normalize(vect)
            label.move_to(center + vect)
            return label
        theta_label = always_redraw(get_theta_label)

        def get_height_line():
            p2 = circle.point_at_angle(get_theta())
            p1 = np.array(p2)
            p1[1] = circle.get_center()[1]
            return Line(
                p1, p2,
                stroke_color=YELLOW,
                stroke_width=3,
            )
        self.height_line = always_redraw(get_height_line)

        def get_width_line():
            p2 = circle.get_center()
            p1 = circle.point_at_angle(get_theta())
            p1[1] = p2[1]
            return Line(
                p1, p2,
                stroke_color=PINK,
                stroke_width=3,
            )
        self.width_line = always_redraw(get_width_line)

        def get_h_label():
            label = TexMobject("h")
            height_line = self.height_line
            label.match_color(height_line)
            label.set_height(min(height_line.get_height(), 0.3))
            label.set_stroke(BLACK, 3, background=True)
            label.next_to(height_line, RIGHT, SMALL_BUFF)
            return label
        self.h_label = always_redraw(get_h_label)

        def get_w_label():
            label = TexMobject("w")
            width_line = self.width_line
            label.match_color(width_line)
            label.next_to(width_line, DOWN, SMALL_BUFF)
            return label
        self.w_label = always_redraw(get_w_label)

        self.add(r_line, theta_label, arc, self.radius_line)
        self.play(
            FadeInFromDown(tan_eq),
            theta_tracker.set_value, 20 * DEGREES,
        )
        self.wait()

        self.tan_eq = tan_eq
        self.theta_tracker = theta_tracker

    def show_fraction(self):
        height_line = self.height_line
        width_line = self.width_line
        h_label = self.h_label
        w_label = self.w_label
        tan_eq = self.tan_eq

        rhs = TexMobject(
            "{\\text{height}", "\\over", "\\text{width}}"
        )
        rhs.next_to(tan_eq, RIGHT)
        rhs.get_part_by_tex("height").match_color(height_line)
        rhs.get_part_by_tex("width").match_color(width_line)

        for mob in [height_line, width_line, h_label, w_label]:
            mob.update()

        self.play(
            ShowCreation(height_line.copy().clear_updaters(), remover=True),
            FadeInFrom(h_label.copy().clear_updaters(), RIGHT, remover=True),
            Write(rhs[:2])
        )
        self.add(height_line, h_label)
        self.play(
            ShowCreation(width_line.copy().clear_updaters(), remover=True),
            FadeInFrom(w_label.copy().clear_updaters(), UP, remover=True),
            self.r_label.fade, 1,
            Write(rhs[2])
        )
        self.add(width_line, w_label)
        self.wait()

        self.rhs = rhs

    def show_fraction_approximation(self):
        theta_tracker = self.theta_tracker
        approx_rhs = TexMobject(
            "\\approx", "{\\theta", "\\over", "1}",
        )
        height, over1, width = self.rhs
        approx, theta, over2, one = approx_rhs
        approx_rhs.set_color_by_tex("\\theta", RED)
        approx_rhs.next_to(self.rhs, RIGHT, MED_SMALL_BUFF)

        self.play(theta_tracker.set_value, 5 * DEGREES)
        self.play(Write(VGroup(approx, over2)))
        self.wait()
        self.play(Indicate(width))
        self.play(TransformFromCopy(width, one))
        self.wait()
        self.play(Indicate(height))
        self.play(TransformFromCopy(height, theta))
        self.wait()


class TangentTaylorSeries(TeacherStudentsScene):
    def construct(self):
        series = TexMobject(
            "\\tan", "(", "\\theta", ")", "=", "\\theta", "+",
            "\\frac{1}{3}", "\\theta", "^3", "+",
            "\\frac{2}{15}", "\\theta", "^5", "+", "\\cdots",
            tex_to_color_map={"\\theta": YELLOW},
        )
        series.move_to(2 * UP)
        series.move_to(self.hold_up_spot, DOWN)
        series_error = series[7:]
        series_error_rect = SurroundingRectangle(series_error)

        example = TexMobject(
            "\\tan", "\\left(", "\\frac{1}{100}", "\\right)",
            "=", "\\frac{1}{100}", "+",
            "\\frac{1}{3}", "\\left(",
            "\\frac{1}{1{,}000{,}000}",
            "\\right)", "+",
            "\\frac{2}{15}", "\\left(",
            "\\frac{1}{10{,}000{,}000{,}000}",
            "\\right)", "+", "\\cdots",
        )
        example.set_color_by_tex("\\frac{1}{1", BLUE)
        example.set_width(FRAME_WIDTH - 1)
        example.next_to(self.students, UP, buff=2)
        example.shift_onto_screen()
        error = example[7:]
        error_rect = SurroundingRectangle(error)
        error_rect.set_color(RED)
        error_decimal = DecimalNumber(
            np.tan(0.01) - 0.01,
            num_decimal_places=15,
        )
        error_decimal.next_to(error_rect, DOWN)
        approx = TexMobject("\\approx")
        approx.next_to(error_decimal, LEFT)
        error_decimal.add(approx)
        error_decimal.match_color(error_rect)

        self.play(
            FadeInFromDown(series),
            self.teacher.change, "raise_right_hand",
        )
        self.play(
            ShowCreation(series_error_rect),
            self.get_student_changes(*3 * ["pondering"])
        )
        self.play(FadeOut(series_error_rect))
        self.play(
            series.center, series.to_edge, UP,
        )
        self.look_at(series)
        self.play(
            TransformFromCopy(series[:8], example[:8]),
            TransformFromCopy(series[8], example[9]),
            TransformFromCopy(series[10:12], example[11:13]),
            TransformFromCopy(series[12], example[14]),
            TransformFromCopy(series[14:], example[16:]),
            *map(GrowFromCenter, [example[i] for i in (8, 10, 13, 15)])
        )
        self.change_student_modes("happy", "confused", "sad")
        self.play(ShowCreation(error_rect))
        self.play(ShowIncreasingSubsets(error_decimal))
        self.change_all_student_modes("hooray")
        self.wait(3)


class AnalyzeCircleGeometry1e4(AnalyzeCircleGeometry):
    CONFIG = {
        "mass_ratio": 10000,
    }


class SumUpWrapper(Scene):
    def construct(self):
        title = TextMobject("To sum up:")
        title.scale(1.5)
        title.to_edge(UP)
        screen_rect = ScreenRectangle(height=6)
        screen_rect.set_fill(BLACK, 1)
        screen_rect.next_to(title, DOWN)
        self.add(FullScreenFadeRectangle(
            fill_color=DARK_GREY,
            fill_opacity=0.5
        ))
        self.play(
            FadeInFromDown(title),
            FadeIn(screen_rect),
        )
        self.wait()


class ConservationLawSummary(Scene):
    def construct(self):
        energy_eq = TexMobject(
            "\\frac{1}{2}", "m_1", "(", "v_1", ")", "^2", "+",
            "\\frac{1}{2}", "m_2", "(", "v_2", ")", "^2", "=",
            "\\text{const.}",
        )
        energy_word = TextMobject("Energy")
        energy_word.scale(2)
        circle = Circle(color=YELLOW, radius=2)
        energy_group = VGroup(energy_word, energy_eq, circle)
        momentum_eq = TexMobject(
            "m_1", "v_1", "+", "m_2", "v_2", "=",
            "\\text{const.}",
        )
        momentum_word = TextMobject("Momentum")
        momentum_word.scale(2)
        line = Line(ORIGIN, RIGHT + np.sqrt(10) * DOWN)
        line.set_color(GREEN)
        momentum_group = VGroup(momentum_word, momentum_eq, line)

        equations = VGroup(energy_eq, momentum_eq)
        words = VGroup(energy_word, momentum_word)

        for equation in equations:
            equation.set_color_by_tex("m_", BLUE)
            equation.set_color_by_tex("v_", RED)

        words.arrange(
            DOWN, buff=3,
        )
        words.to_edge(LEFT, buff=1.5)

        for group in energy_group, momentum_group:
            arrow = Arrow(
                LEFT, 2 * RIGHT,
                rectangular_stem_width=0.1,
                tip_length=0.5,
                color=WHITE
            )
            arrow.next_to(group[0], RIGHT)
            group[1].next_to(group[0], DOWN)
            group[2].next_to(arrow, RIGHT)
            group[2].set_stroke(width=6)
            group.add(arrow)
        # line.scale(4, about_edge=DR)
        red_energy_word = energy_word.copy()
        red_energy_word.set_fill(opacity=0)
        red_energy_word.set_stroke(RED, 2)

        self.add(energy_group, momentum_group)
        self.wait()
        self.play(
            LaggedStartMap(
                ShowCreationThenDestruction,
                red_energy_word
            ),
        )
        for color in [RED, BLUE, PINK, YELLOW]:
            self.play(ShowCreation(
                circle.copy().set_color(color),
            ))


class FinalCommentsOnPhaseSpace(Scene):
    def construct(self):
        self.add_title()
        self.show_related_fields()
        self.state_to_point()
        self.puzzle_as_remnant()

    def add_title(self):
        title = self.title = TextMobject("Phase space")
        title.scale(2)
        title.to_edge(UP)
        title.set_color(YELLOW)

        self.play(Write(title))

    def show_related_fields(self):
        title = self.title

        images = Group(
            ImageMobject("ClacksThumbnail"),
            ImageMobject("PictoralODE"),
            # ImageMobject("DoublePendulumStart"),
            ImageMobject("MobiusStrip"),
        )
        colors = [BLUE_D, GREY_BROWN, BLUE_C]
        for image, color in zip(images, colors):
            image.set_height(2.5)
            image.add(SurroundingRectangle(
                image,
                color=color,
                stroke_width=5,
                buff=0,
            ))
        images.arrange(RIGHT)
        images.move_to(DOWN)

        arrows = VGroup(*[
            Arrow(
                title.get_bottom(), image.get_top(),
                color=WHITE,
            )
            for image in images
        ])

        for image, arrow in zip(images, arrows):
            self.play(
                GrowArrow(arrow),
                GrowFromPoint(image, title.get_bottom()),
            )
            self.wait()
        self.wait()

        self.to_fade = Group(images, arrows)

    def state_to_point(self):
        state = TextMobject("State")
        arrow = Arrow(
            2 * LEFT, 2 * RIGHT,
            color=WHITE,
            rectangular_stem_width=0.1,
            tip_length=0.5
        )
        point = TextMobject("Point")
        dynamics = TextMobject("Dynamics")
        geometry = TextMobject("Geometry")
        words = VGroup(state, point, dynamics, geometry)
        for word in words:
            word.scale(2)

        group = VGroup(state, arrow, point)
        group.arrange(RIGHT, buff=MED_LARGE_BUFF)
        group.move_to(2.5 * DOWN)

        dynamics.move_to(state, RIGHT)
        geometry.move_to(point, LEFT)

        self.play(
            FadeOutAndShift(self.to_fade, UP),
            FadeInFrom(state, UP)
        )
        self.play(
            GrowArrow(arrow),
            FadeInFrom(point, LEFT)
        )
        self.wait(2)
        for w1, w2 in [(state, dynamics), (point, geometry)]:
            self.play(
                FadeOutAndShift(w1, UP),
                FadeInFrom(w2, DOWN),
            )
            self.wait()
        self.wait()

    def puzzle_as_remnant(self):
        pass


class AltShowTwoPopulations(ShowTwoPopulations):
    CONFIG = {
        "count_word_scale_val": 2,
    }


class SimpleTeacherHolding(TeacherStudentsScene):
    def construct(self):
        self.play(self.teacher.change, "raise_right_hand")
        self.change_all_student_modes("pondering")
        self.wait(3)


class EndScreen(PatreonEndScreen):
    CONFIG = {
        "specific_patrons": [
            "Juan Benet",
            "Vassili Philippov",
            "Burt Humburg",
            "Matt Russell",
            "soekul",
            "Richard Barthel",
            "Nathan Jessurun",
            "Ali Yahya",
            "dave nicponski",
            "Yu Jun",
            "Kaustuv DeBiswas",
            "Yana Chernobilsky",
            "Lukas Biewald",
            "Arthur Zey",
            "Roy Larson",
            "Joseph Kelly",
            "Peter Mcinerney",
            "Scott Walter, Ph.D.",
            "Magnus Lysfjord",
            "Evan Phillips",
            "Graham",
            "Mauricio Collares",
            "Quantopian",
            "Jordan Scales",
            "Lukas -krtek.net- Novy",
            "John Shaughnessy",
            "Joseph John Cox",
            "Ryan Atallah",
            "Britt Selvitelle",
            "Jonathan Wilson",
            "Randy C. Will",
            "Magnus Dahlström",
            "David Gow",
            "J",
            "Luc Ritchie",
            "Rish Kundalia",
            "Bob Sanderson",
            "Mathew Bramson",
            "Mustafa Mahdi",
            "Robert Teed",
            "Cooper Jones",
            "Jeff Linse",
            "John Haley",
            "Boris Veselinovich",
            "Andrew Busey",
            "Awoo",
            "Linh Tran",
            "Ripta Pasay",
            "David Clark",
            "Mathias Jansson",
            "Clark Gaebel",
            "Bernd Sing",
            "Jason Hise",
            "Ankalagon",
            "Dave B",
            "Ted Suzman",
            "Chris Connett",
            "Eric Younge",
            "1stViewMaths",
            "Jacob Magnuson",
            "Jonathan Eppele",
            "Delton Ding",
            "James Hughes",
            "Stevie Metke",
            "Yaw Etse",
            "John Griffith",
            "Magister Mugit",
            "Ludwig Schubert",
            "Giovanni Filippi",
            "Matt Langford",
            "Matt Roveto",
            "Jameel Syed",
            "Richard Burgmann",
            "Solara570",
            "Alexis Olson",
            "Jeff Straathof",
            "John V Wertheim",
            "Sindre Reino Trosterud",
            "Song Gao",
            "Peter Ehrnstrom",
            "Valeriy Skobelev",
            "Art Ianuzzi",
            "Michael Faust",
            "Omar Zrien",
            "Adrian Robinson",
            "Federico Lebron",
            "Kai-Siang Ang",
            "Michael Hardel",
            "Nero Li",
            "Ryan Williams",
            "Charles Southerland",
            "Devarsh Desai",
            "Hal Hildebrand",
            "Jan Pijpers",
            "L0j1k",
            "Mark B Bahu",
            "Márton Vaitkus",
            "Richard Comish",
            "Zach Cardwell",
            "Brian Staroselsky",
            "Matthew Cocke",
            "Christian Kaiser",
            "Danger Dai",
            "Dave Kester",
            "eaglle",
            "Florian Chudigiewitsch",
            "Roobie",
            "Xavier Bernard",
            "YinYangBalance.Asia",
            "Eryq Ouithaqueue",
            "Kanan Gill",
            "j eduardo perez",
            "Antonio Juarez",
            "Owen Campbell-Moore",
        ],
    }


class SolutionThumbnail(Thumbnail):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "label_text": "$100^{d}$ kg",
            },
            "collect_clack_data": False,
        },
    }

    def add_text(self):
        word = TextMobject("Solution")
        question = TextMobject("How many collisions?")
        word.set_width(7)
        question.match_width(word)
        question.next_to(word, UP)
        group = VGroup(word, question)
        group.to_edge(UP, buff=MED_LARGE_BUFF)
        word.set_color(RED)
        question.set_color(YELLOW)
        group.set_stroke(RED, 2, background=True)
        self.add(group)
