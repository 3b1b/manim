from big_ol_pile_of_manim_imports import *
import subprocess
from pydub import AudioSegment


MIN_TIME_BETWEEN_FLASHES = 0.004


class SlidingBlocks(VGroup):
    CONFIG = {
        "block1_config": {
            "mass": 1,
            "velocity": -2,
            "distance": 7,
            "width": None,
            "color": None,
            "label_text": None,
        },
        "block2_config": {
            "mass": 1,
            "velocity": 0,
            "distance": 3,
            "width": None,
            "color": None,
            "label_text": None,
        },
        "block_style": {
            "fill_opacity": 1,
            "stroke_width": 3,
            "stroke_color": WHITE,
            "sheen_direction": UL,
            "sheen_factor": 0.5,
            "sheen_direction": UL,
        },
        "collect_clack_data": True,
    }

    def __init__(self, surrounding_scene, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.surrounding_scene = surrounding_scene
        self.floor = surrounding_scene.floor
        self.wall = surrounding_scene.wall

        self.block1 = self.get_block(**self.block1_config)
        self.block2 = self.get_block(**self.block2_config)
        self.mass_ratio = self.block2.mass / self.block1.mass
        self.phase_space_point_tracker = self.get_phase_space_point_tracker()
        self.add(
            self.block1, self.block2,
            self.phase_space_point_tracker,
        )
        self.add_updater(self.__class__.update_positions)

        if self.collect_clack_data:
            self.clack_data = self.get_clack_data()

    def get_block(self, mass, distance, velocity, width, color, label_text):
        if width is None:
            width = self.mass_to_width(mass)
        if color is None:
            color = self.mass_to_color(mass)
        if label_text is None:
            label_text = "{:,}\\,kg".format(int(mass))
        block = Square(side_length=width)
        block.mass = mass
        block.velocity = velocity

        style = dict(self.block_style)
        style["fill_color"] = color

        block.set_style(**style)
        block.move_to(
            self.floor.get_top()[1] * UP +
            (self.wall.get_right()[0] + distance) * RIGHT,
            DL,
        )
        label = block.label = TextMobject(label_text)
        label.scale(0.8)
        label.next_to(block, UP, SMALL_BUFF)
        block.add(label)
        return block

    def get_phase_space_point_tracker(self):
        block1, block2 = self.block1, self.block2
        w2 = block2.get_width()
        s1 = block1.get_left()[0] - self.wall.get_right()[0] - w2
        s2 = block2.get_right()[0] - self.wall.get_right()[0] - w2
        result = VectorizedPoint([
            s1 * np.sqrt(block1.mass),
            s2 * np.sqrt(block2.mass),
            0
        ])

        result.velocity = np.array([
            np.sqrt(block1.mass) * block1.velocity,
            np.sqrt(block2.mass) * block2.velocity,
            0
        ])
        return result

    def update_positions(self, dt):
        self.phase_space_point_tracker.shift(
            self.phase_space_point_tracker.velocity * dt
        )
        self.update_blocks_from_phase_space_point_tracker()

    def old_update_positions(self, dt):
        # Based on velocity diagram bouncing...didn't work for
        # large masses, due to frame rate mismatch
        blocks = self.submobjects
        for block in blocks:
            block.shift(block.velocity * dt * RIGHT)
        if blocks[0].get_left()[0] < blocks[1].get_right()[0]:
            # Two blocks collide
            m1 = blocks[0].mass
            m2 = blocks[1].mass
            v1 = blocks[0].velocity
            v2 = blocks[1].velocity
            v_phase_space_point = np.array([
                np.sqrt(m1) * v1, -np.sqrt(m2) * v2
            ])
            angle = 2 * np.arctan(np.sqrt(m2 / m1))
            new_vps_point = rotate_vector(v_phase_space_point, angle)
            for block, value in zip(blocks, new_vps_point):
                block.velocity = value / np.sqrt(block.mass)
            blocks[1].move_to(blocks[0].get_corner(DL), DR)
            self.surrounding_scene.clack(blocks[0].get_left())
        if blocks[1].get_left()[0] < self.wall.get_right()[0]:
            # Second block hits wall
            blocks[1].velocity *= -1
            blocks[1].move_to(self.wall.get_corner(DR), DL)
            if blocks[0].get_left()[0] < blocks[1].get_right()[0]:
                blocks[0].move_to(blocks[1].get_corner(DR), DL)
            self.surrounding_scene.clack(blocks[1].get_left())
        return self

    def update_blocks_from_phase_space_point_tracker(self):
        block1, block2 = self.block1, self.block2

        ps_point = self.phase_space_point_tracker.get_location()
        theta = np.arctan(np.sqrt(self.mass_ratio))
        ps_point_angle = angle_of_vector(ps_point)
        n_clacks = int(ps_point_angle / theta)
        reflected_point = rotate_vector(
            ps_point,
            -2 * np.ceil(n_clacks / 2) * theta
        )
        reflected_point = np.abs(reflected_point)

        shadow_wall_x = self.wall.get_right()[0] + block2.get_width()
        floor_y = self.floor.get_top()[1]
        s1 = reflected_point[0] / np.sqrt(block1.mass)
        s2 = reflected_point[1] / np.sqrt(block2.mass)
        block1.move_to(
            (shadow_wall_x + s1) * RIGHT +
            floor_y * UP,
            DL,
        )
        block2.move_to(
            (shadow_wall_x + s2) * RIGHT +
            floor_y * UP,
            DR,
        )

        self.surrounding_scene.update_num_clacks(n_clacks)

    def get_clack_data(self):
        ps_point = self.phase_space_point_tracker.get_location()
        ps_velocity = self.phase_space_point_tracker.velocity
        if ps_velocity[1] != 0:
            raise Exception(
                "Haven't implemented anything to gather clack "
                "data from a start state with block2 moving"
            )
        y = ps_point[1]
        theta = np.arctan(np.sqrt(self.mass_ratio))

        clack_data = []
        for k in range(1, int(PI / theta) + 1):
            clack_ps_point = np.array([
                y / np.tan(k * theta),
                y,
                0
            ])
            time = get_norm(ps_point - clack_ps_point) / get_norm(ps_velocity)
            reflected_point = rotate_vector(
                clack_ps_point,
                -2 * np.ceil((k - 1) / 2) * theta
            )
            block2 = self.block2
            s2 = reflected_point[1] / np.sqrt(block2.mass)
            location = np.array([
                self.wall.get_right()[0] + s2,
                block2.get_center()[1],
                0
            ])
            if k % 2 == 1:
                location += block2.get_width() * RIGHT
            clack_data.append((location, time))
        return clack_data

    def mass_to_color(self, mass):
        colors = [
            LIGHT_GREY,
            BLUE_B,
            BLUE_D,
            BLUE_E,
            BLUE_E,
            DARK_GREY,
            DARK_GREY,
            BLACK,
        ]
        index = min(int(np.log10(mass)), len(colors) - 1)
        return colors[index]

    def mass_to_width(self, mass):
        return 1 + 0.25 * np.log10(mass)


class ClackFlashes(ContinualAnimation):
    CONFIG = {
        "flash_config": {
            "run_time": 0.5,
            "line_length": 0.1,
            "flash_radius": 0.2,
        },
        "start_up_time": 0,
    }

    def __init__(self, clack_data, **kwargs):
        digest_config(self, kwargs)
        self.flashes = []
        group = Group()
        last_time = 0
        for location, time in clack_data:
            if (time - last_time) < MIN_TIME_BETWEEN_FLASHES:
                continue
            last_time = time
            flash = Flash(location, **self.flash_config)
            flash.start_time = time
            flash.end_time = time + flash.run_time
            self.flashes.append(flash)
        ContinualAnimation.__init__(self, group, **kwargs)

    def update_mobject(self, dt):
        total_time = self.external_time
        for flash in self.flashes:
            if flash.start_time < total_time < flash.end_time:
                if flash.mobject not in self.mobject:
                    self.mobject.add(flash.mobject)
                flash.update(
                    (total_time - flash.start_time) / flash.run_time
                )
            else:
                if flash.mobject in self.mobject:
                    self.mobject.remove(flash.mobject)


class BlocksAndWallScene(Scene):
    CONFIG = {
        "include_sound": True,
        "count_clacks": True,
        "counter_group_shift_vect": LEFT,
        "sliding_blocks_config": {},
        "floor_y": -2,
        "wall_x": -6,
        "n_wall_ticks": 15,
        "counter_label": "\\# Collisions: ",
        "collision_sound": "clack.wav",
        "show_flash_animations": True,
    }

    def setup(self):
        self.track_time()
        self.add_floor_and_wall()
        self.add_blocks()
        if self.show_flash_animations:
            self.add_flash_animations()

        if self.count_clacks:
            self.add_counter()

    def add_floor_and_wall(self):
        self.floor = self.get_floor()
        self.wall = self.get_wall()
        self.add(self.floor, self.wall)

    def add_blocks(self):
        self.blocks = SlidingBlocks(self, **self.sliding_blocks_config)
        if hasattr(self.blocks, "clack_data"):
            self.clack_data = self.blocks.clack_data
        self.add(self.blocks)

    def add_flash_animations(self):
        self.clack_flashes = ClackFlashes(self.clack_data)
        self.add(self.clack_flashes)

    def track_time(self):
        time_tracker = ValueTracker()
        time_tracker.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(time_tracker)
        self.get_time = time_tracker.get_value

    def add_counter(self):
        self.n_clacks = 0
        counter_label = TextMobject(self.counter_label)
        counter_mob = Integer(self.n_clacks)
        counter_mob.next_to(
            counter_label[-1], RIGHT,
            aligned_edge=DOWN,
        )
        counter_group = VGroup(
            counter_label,
            counter_mob,
        )
        counter_group.to_corner(UR)
        counter_group.shift(self.counter_group_shift_vect)
        self.add(counter_group)

        self.counter_mob = counter_mob

    def get_wall(self):
        wall = Line(self.floor_y * UP, FRAME_HEIGHT * UP / 2)
        wall.shift(self.wall_x * RIGHT)
        lines = VGroup(*[
            Line(ORIGIN, 0.25 * UR)
            for x in range(self.n_wall_ticks)
        ])
        lines.set_stroke(width=1)
        lines.arrange_submobjects(UP, buff=MED_SMALL_BUFF)
        lines.move_to(wall, DR)
        wall.add(lines)
        return wall

    def get_floor(self):
        floor = Line(self.wall_x * RIGHT, FRAME_WIDTH * RIGHT / 2)
        floor.shift(self.floor_y * UP)
        return floor

    def update_num_clacks(self, n_clacks):
        if hasattr(self, "n_clacks"):
            if n_clacks == self.n_clacks:
                return
            self.counter_mob.set_value(n_clacks)

    def create_sound_file(self, clack_data):
        directory = get_scene_output_directory(self.__class__)
        clack_file = os.path.join(
            directory, 'sounds', self.collision_sound,
        )
        output_file = self.get_movie_file_path(extension='.wav')
        times = [
            time
            for location, time in clack_data
            if time < 300  # In case of any extremes
        ]

        clack = AudioSegment.from_wav(clack_file)
        total_time = max(times) + 1
        clacks = AudioSegment.silent(int(1000 * total_time))
        last_position = 0
        min_diff = int(1000 * MIN_TIME_BETWEEN_FLASHES)
        for time in times:
            position = int(1000 * time)
            d_position = position - last_position
            if d_position < min_diff:
                continue
            if time > self.get_time():
                break
            last_position = position
            clacks = clacks.fade(-50, start=position, end=position + 10)
            clacks = clacks.overlay(
                clack,
                position=position
            )
        clacks.export(output_file, format="wav")
        return output_file

    def close_movie_pipe(self):
        Scene.close_movie_pipe(self)
        if self.include_sound:
            sound_file_path = self.create_sound_file(self.clack_data)
            movie_path = self.get_movie_file_path()
            temp_path = self.get_movie_file_path(str(self) + "TempSound")
            commands = [
                "ffmpeg",
                "-i", movie_path,
                "-i", sound_file_path,
                "-c:v", "copy", "-c:a", "aac",
                '-loglevel', 'error',
                "-strict", "experimental",
                temp_path,
            ]
            subprocess.call(commands)
            subprocess.call(["rm", sound_file_path])
            subprocess.call(["mv", temp_path, movie_path])

# Animated scenes


class MathAndPhysicsConspiring(Scene):
    def construct(self):
        v_line = Line(DOWN, UP).scale(FRAME_HEIGHT)
        v_line.save_state()
        v_line.fade(1)
        v_line.scale(0)
        math_title = TextMobject("Math")
        math_title.set_color(BLUE)
        physics_title = TextMobject("Physics")
        physics_title.set_color(YELLOW)
        for title, vect in (math_title, LEFT), (physics_title, RIGHT):
            title.scale(2)
            title.shift(vect * FRAME_WIDTH / 4)
            title.to_edge(UP)

        math_stuffs = VGroup(
            TexMobject("\\pi = {:.16}\\dots".format(PI)),
            self.get_tangent_image(),
        )
        math_stuffs.arrange_submobjects(DOWN, buff=MED_LARGE_BUFF)
        math_stuffs.next_to(math_title, DOWN, LARGE_BUFF)
        to_fade = VGroup(math_title, *math_stuffs, physics_title)

        self.play(
            LaggedStart(
                FadeInFromDown, to_fade,
                lag_ratio=0.7,
                run_time=3,
            ),
            Restore(v_line, run_time=2, path_arc=PI / 2),
        )
        self.wait()

    def get_tangent_image(self):
        axes = Axes(
            x_min=-1.5,
            x_max=1.5,
            y_min=-1.5,
            y_max=1.5,
        )
        circle = Circle()
        circle.set_color(WHITE)
        theta = 30 * DEGREES
        arc = Arc(angle=theta, radius=0.4)
        theta_label = TexMobject("\\theta")
        theta_label.scale(0.5)
        theta_label.next_to(arc.get_center(), RIGHT, buff=SMALL_BUFF)
        theta_label.shift(0.025 * UL)
        line = Line(ORIGIN, rotate_vector(RIGHT, theta))
        line.set_color(WHITE)
        one = TexMobject("1").scale(0.5)
        one.next_to(line.point_from_proportion(0.7), UL, 0.5 * SMALL_BUFF)
        tan_line = Line(
            line.get_end(),
            (1.0 / np.cos(theta)) * RIGHT
        )
        tan_line.set_color(RED)
        tan_text = TexMobject("\\tan(\\theta)")
        tan_text.rotate(tan_line.get_angle())
        tan_text.scale(0.5)
        tan_text.move_to(tan_line)
        tan_text.match_color(tan_line)
        tan_text.shift(0.2 * normalize(line.get_vector()))

        result = VGroup(
            axes, circle,
            line, one,
            arc, theta_label,
            tan_line, tan_text,
        )
        result.set_height(4)
        return result


class LightBouncing(MovingCameraScene):
    CONFIG = {
        "theta": np.arctan(0.15),
        "show_fanning": False,
        "mirror_shift_vect": 5 * LEFT,
        "mirror_length": 10,
        "beam_start_x": 12,
        "beam_height": 1,
    }

    def construct(self):
        theta = self.theta
        h_line = Line(ORIGIN, self.mirror_length * RIGHT)
        d_line = h_line.copy().rotate(theta, about_point=ORIGIN)
        mirrors = VGroup(h_line, d_line)
        self.add(mirrors)

        beam_height = self.beam_height
        start_point = self.beam_start_x * RIGHT + beam_height * UP
        points = [start_point] + [
            np.array([
                (beam_height / np.tan(k * theta)),
                beam_height,
                0,
            ])
            for k in range(1, int(PI / theta))
        ] + [rotate(start_point, PI, UP)]
        reflected_points = []
        for k, point in enumerate(points):
            reflected_point = rotate_vector(point, -2 * (k // 2) * theta)
            reflected_point[1] = abs(reflected_point[1])
            reflected_points.append(reflected_point)
        beam = VMobject()
        beam.set_points_as_corners(reflected_points)
        beam.set_stroke(YELLOW, 2)

        anims = [self.get_beam_anim(beam)]

        if self.show_fanning:
            for k in range(2, int(PI / theta) + 1):
                line = h_line.copy()
                line.set_stroke(WHITE, 1)
                line.rotate(k * theta, about_point=ORIGIN)
                self.add(line)
            straight_beam = VMobject()
            straight_beam.set_points_as_corners(points)
            straight_beam.set_stroke(YELLOW, 2)
            anims.append(self.get_beam_anim(straight_beam))

        self.camera_frame.shift(-self.mirror_shift_vect)
        self.play(*anims)
        self.wait()

    def get_beam_anim(self, beam):
        dot = Dot()
        dot.scale(0.5)
        dot.match_color(beam)
        return AnimationGroup(
            ShowPassingFlash(
                beam,
                run_time=5,
                rate_func=lambda t: smooth(t, 5),
                time_width=0.05,
            ),
            UpdateFromFunc(
                dot,
                lambda m: m.move_to(beam.points[-1])
            ),
        )


class BlocksAndWallExample(BlocksAndWallScene):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 1e0,
                "velocity": -2,
            }
        },
        "wait_time": 10,
    }

    def construct(self):
        self.wait(self.wait_time)


class BlocksAndWallExampleMass1e1(BlocksAndWallExample):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 1e1,
                "velocity": -1.5,
            }
        },
        "wait_time": 20,
    }


class CowToSphere(ExternallyAnimatedScene):
    pass


class NoFrictionLabel(Scene):
    def construct(self):
        words = TextMobject("Frictionless")
        words.shift(2 * RIGHT)
        words.add_updater(
            lambda m, dt: m.shift(dt * LEFT)
        )

        self.play(VFadeIn(words))
        self.wait(2)
        self.play(VFadeOut(words))


class Mass1e1WithElasticLabel(BlocksAndWallExampleMass1e1):
    def add_flash_animations(self):
        super().add_flash_animations()
        flashes = self.clack_flashes
        label = TextMobject(
            "Purely elastic collisions\\\\"
            "(no energy lost)"
        )
        label.set_color(YELLOW)
        label.move_to(2 * LEFT + 2 * UP)
        self.add(label)
        self.add(*[
            self.get_arrow(label, flashes, flash)
            for flash in flashes.flashes
        ])

    def get_arrow(self, label, clack_flashes, flash):
        arrow = Arrow(
            label.get_bottom(),
            flash.mobject.get_center() + 0.5 * UP,
        )
        arrow.set_fill(YELLOW)

        def set_opacity(arrow):
            time = self.get_time()
            from_start = time - flash.start_time
            if from_start < 0:
                opacity = 0
            else:
                opacity = smooth(1 - from_start)
            arrow.set_fill(opacity=opacity)

        arrow.add_updater(set_opacity)
        return arrow


class AskAboutSoundlessness(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Wait, elastic collisions should\\\\"
            "make no sound, right?",
        )
        self.play(self.teacher.change, "guilty")
        self.wait(2)
        self.play(
            RemovePiCreatureBubble(self.students[1], target_mode="confused"),
            self.teacher.change, "raise_right_hand",
            added_anims=[
                self.get_student_changes("pondering", "confused", "thinking")
            ]
        )
        self.look_at(self.screen)
        self.wait(3)


class ShowCreationRect(Scene):
    def construct(self):
        rect = SurroundingRectangle(TextMobject("\\# Collisions: 3"))
        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))
        self.wait()


class BlocksAndWallExampleSameMass(BlocksAndWallExample):
    pass


class ShowLeftArrow(Scene):
    def construct(self):
        arrow = Vector(2 * LEFT, color=RED)
        self.play(GrowArrow(arrow))
        self.wait()
        self.play(FadeOut(arrow))


class AskWhatWillHappen(PiCreatureScene):
    def construct(self):
        morty = self.pi_creature
        morty.set_color(GREY_BROWN)

        self.pi_creature_says(
            "What will\\\\"
            "happen?",
            target_mode="maybe",
            look_at_arg=4 * DR,
        )
        self.wait(3)


class BlocksAndWallExampleMass1e2(BlocksAndWallExample):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 1e2,
                "velocity": -1,
            }
        },
        "wait_time": 20,
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


class BlocksAndWallExampleMass1e4SlowMo(BlocksAndWallExample):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 1e4,
                "velocity": -0.1,
                "distance": 4.1
            },
        },
        "wait_time": 50,
        "collision_sound": "slow_clack.wav",
    }


class SlowMotionLabel(Scene):
    def construct(self):
        words = TextMobject("Slow motion replay")
        words.scale(2).to_edge(UP)
        self.play(Write(words))
        self.wait()


class BlocksAndWallExampleMass1e6(BlocksAndWallExample):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 1e6,
                "velocity": -1,
            },
        },
        "wait_time": 20,
    }


class BlocksAndWallExampleMass1e6SlowMo(BlocksAndWallExample):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 1e6,
                "velocity": -0.1,
                "distance": 4.1
            },
        },
        "wait_time": 60,
        "collision_sound": "slow_clack.wav",
    }


class BlocksAndWallExampleMass1e8(BlocksAndWallExample):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 1e8,
                "velocity": -1,
            },
        },
        "wait_time": 25,
    }


class BlocksAndWallExampleMass1e10(BlocksAndWallExample):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 1e10,
                "velocity": -1,
            },
        },
        "wait_time": 25,
    }


class GalperinPaperScroll(ExternallyAnimatedScene):
    pass


class PiComputingAlgorithmsAxes(Scene):
    def construct(self):
        self.setup_axes()
        self.add_methods()

    def setup_axes(self):
        axes = Axes(
            x_min=0,
            y_min=0,
            x_max=9,
            y_max=5,
            number_line_config={
                "tick_frequency": 100,
                "numbers_with_elongated_ticks": [],
            }
        )

        y_label = TextMobject("Efficiency")
        y_label.rotate(90 * DEGREES)
        y_label.next_to(axes.y_axis, LEFT, SMALL_BUFF)
        x_label = TextMobject("Elegance")
        x_label.next_to(axes.x_axis, DOWN, SMALL_BUFF)
        axes.add(y_label, x_label)
        axes.center().to_edge(DOWN)
        self.axes = axes

        title = TextMobject("Algorithms for computing $\\pi$")
        title.scale(1.5)
        title.to_edge(UP, buff=MED_SMALL_BUFF)

        self.add(title, axes)

    def add_methods(self):
        method_location_list = [
            (self.get_machin_like_formula(), (1, 4.5)),
            (self.get_viete(), (3, 3.5)),
            (self.get_measuring_tape(), (0.5, 1)),
            (self.get_monte_carlo(), (2, 0.2)),
            (self.get_basel(), (6, 1)),
            (self.get_blocks_image(), (8, 0.1)),
        ]

        algorithms = VGroup()
        for method, location in method_location_list:
            cross = TexMobject("\\times")
            cross.set_color(RED)
            cross.move_to(self.axes.coords_to_point(*location))
            method.next_to(cross, UP, SMALL_BUFF)
            method.align_to(cross, LEFT)
            method.shift_onto_screen()
            algorithms.add(VGroup(method, cross))

        self.play(LaggedStart(
            FadeInFromDown, algorithms,
            run_time=4,
            lag_ratio=0.4,
        ))
        self.wait()
        self.play(CircleThenFadeAround(algorithms[-1][0]))

    def get_machin_like_formula(self):
        formula = TexMobject(
            "\\frac{\\pi}{4} = "
            "12\\arctan\\left(\\frac{1}{49}\\right) + "
            "32\\arctan\\left(\\frac{1}{57}\\right) - "
            "5\\arctan\\left(\\frac{1}{239}\\right) + "
            "12\\arctan\\left(\\frac{1}{110{,}443}\\right)"
        )
        formula.scale(0.5)
        return formula

    def get_viete(self):
        formula = TexMobject(
            "\\frac{2}{\\pi} = "
            "\\frac{\\sqrt{2}}{2} \\cdot"
            "\\frac{\\sqrt{2 + \\sqrt{2}}}{2} \\cdot"
            "\\frac{\\sqrt{2 + \\sqrt{2 + \\sqrt{2}}}}{2} \\cdots"
        )
        formula.scale(0.5)
        return formula

    def get_measuring_tape(self):
        return TextMobject("Measuring tape").scale(0.75)

    def get_monte_carlo(self):
        return TextMobject("Monte Carlo").scale(0.75)

    def get_basel(self):
        formula = TexMobject(
            "\\frac{\\pi^2}{6} = "
            "\\sum_{n=1}^\\infty \\frac{1}{n^2}"
        )
        formula.scale(0.5)
        return formula

    def get_blocks_image(self):
        scene = BlocksAndWallScene(
            write_to_movie=False,
            skip_animations=True,
            count_clacks=False,
            floor_y=1,
            wall_x=0,
            n_wall_ticks=6,
            sliding_blocks_config={
                "block1_config": {
                    "mass": 1e2,
                    "velocity": -0.01,
                    "distance": 3.5
                },
                "block2_config": {
                    "distance": 1,
                    "velocity": 0,
                },
            }
        )
        group = VGroup(
            scene.wall, scene.floor,
            scene.blocks.block1,
            scene.blocks.block2,
        )
        group.set_width(3)
        return group


class StepsOfTheAlgorithm(TeacherStudentsScene):
    def construct(self):
        steps = VGroup(
            TextMobject("Step 1:", "Implement a physics engine"),
            TextMobject(
                "Step 2:",
                "Choose the number of digits, $d$,\\\\"
                "of $\\pi$ that you want to compute"
            ),
            TextMobject(
                "Step 3:",
                "Set one mass to $100^{d - 1}$, the other to $1$"
            ),
            TextMobject("Step 4:", "Count collisions"),
        )
        steps.arrange_submobjects(
            DOWN,
            buff=MED_LARGE_BUFF,
            aligned_edge=LEFT,
        )
        steps.to_corner(UL)
        steps.scale(0.8)

        for step in steps:
            self.play(
                FadeInFromDown(step[0]),
                self.teacher.change, "raise_right_hand"
            )
            self.play(
                Write(step[1], run_time=2),
                self.get_student_changes(
                    *["pondering"] * 3,
                    look_at_arg=step,
                )
            )
            self.wait()
        self.change_student_modes(
            "sassy", "erm", "confused",
            look_at_arg=steps,
            added_anims=[self.teacher.change, "happy"]
        )
        self.wait(3)


class CompareToGalacticMass(Scene):
    def construct(self):
        self.add_digits_of_pi()
        self.show_mass()
        self.show_galactic_black_holes()
        self.show_total_count()

    def add_digits_of_pi(self):
        # 20 digits of pi
        digits = TexMobject("3.1415926535897932384...")
        digits.set_width(FRAME_WIDTH - 3)
        digits.to_edge(UP)

        highlighted_digits = VGroup(*[
            d.copy().set_background_stroke(color=BLUE, width=5)
            for d in [digits[0], *digits[2:-3]]
        ])
        counter = Integer(0)
        counter.scale(1.5)
        counter.set_color(BLUE)
        brace = VMobject()
        self.add(counter, brace)

        for k in range(len(highlighted_digits)):
            if k == 0:
                self.add(digits[0])
            else:
                self.remove(highlighted_digits[k - 1])
            self.add(digits[k + 1])
            self.add(highlighted_digits[k])
            counter.increment_value()
            brace.become(Brace(highlighted_digits[:k + 1], DOWN))
            counter.next_to(brace, DOWN)
            self.wait(0.1)
        self.add(digits)
        self.remove(*highlighted_digits)

        digits_word = TextMobject("digits")
        digits_word.scale(1.5)
        digits_word.match_color(counter)
        counter.generate_target()
        group = VGroup(counter.target, digits_word)
        group.arrange_submobjects(
            RIGHT,
            index_of_submobject_to_align=0,
            aligned_edge=DOWN,
            buff=0.7,
        )
        group.next_to(brace, DOWN)
        self.play(
            MoveToTarget(counter),
            FadeInFrom(digits_word, LEFT),
        )
        self.wait()

        self.pi_digits_group = VGroup(
            digits, brace, counter, digits_word
        )

    def show_mass(self):
        bw_scene = BlocksAndWallExample(
            write_to_movie=False,
            skip_animations=True,
            count_clacks=False,
            show_flash_animations=False,
            floor_y=0,
            wall_x=-2,
            n_wall_ticks=8,
            sliding_blocks_config={
                "block1_config": {
                    "mass": 1e6,
                    "velocity": -0.01,
                    "distance": 4.5,
                    "label_text": "$100^{(20 - 1)}$ kg",
                    "color": BLACK,
                },
                "block2_config": {
                    "distance": 1,
                    "velocity": 0,
                },
            }
        )
        block1 = bw_scene.blocks.block1
        block2 = bw_scene.blocks.block2
        group = VGroup(
            bw_scene.wall, bw_scene.floor,
            block1, block2
        )
        group.center()
        group.to_edge(DOWN)

        arrow = Vector(2 * LEFT, color=RED)
        arrow.shift(block1.get_center())
        group.add(arrow)

        brace = Brace(block1.label[:-2], UP, buff=SMALL_BUFF)
        number_words = TextMobject(
            "100", *["billion"] * 4,
        )
        number_words.next_to(brace, UP, buff=SMALL_BUFF)
        VGroup(brace, number_words).set_color(YELLOW)

        self.play(Write(group))
        self.wait()
        last_word = number_words[0].copy()
        last_word.next_to(brace, UP, SMALL_BUFF)
        self.play(
            GrowFromCenter(brace),
            FadeInFromDown(last_word),
        )
        for k in range(1, len(number_words) + 1):
            self.remove(last_word)
            last_word = number_words[:k].copy()
            last_word.next_to(brace, UP, SMALL_BUFF)
            self.add(last_word)
            self.wait(0.4)
        self.wait()
        self.remove(last_word)
        self.add(number_words)
        group.add(brace, number_words)
        self.play(group.to_corner, DL)

        self.block1 = block1
        self.block2 = block2
        self.block_setup_group = group

    def show_galactic_black_holes(self):
        black_hole = SVGMobject(file_name="black_hole")
        black_hole.set_color(BLACK)
        black_hole.set_sheen(0.2, UL)
        black_hole.set_height(1)
        black_holes = VGroup(*[
            black_hole.copy() for k in range(10)
        ])
        black_holes.arrange_submobjects_in_grid(5, 2)
        black_holes.to_corner(DR)
        random.shuffle(black_holes.submobjects)
        for bh in black_holes:
            bh.save_state()
            bh.scale(3)
            bh.set_fill(DARK_GREY, 0)

        equals = TexMobject("=")
        equals.scale(2)
        equals.next_to(self.block1, RIGHT)

        words = TextMobject("10x Sgr A$^*$ \\\\ supermassive \\\\ black hole")
        words.next_to(equals, RIGHT)
        self.add(words)

        self.play(
            Write(equals),
            Write(words),
            LaggedStart(
                Restore, black_holes,
                run_time=3
            )
        )
        self.wait()

        self.black_hole_words = VGroup(equals, words)
        self.black_holes = black_holes

    def show_total_count(self):
        digits = self.pi_digits_group[0]
        to_fade = self.pi_digits_group[1:]
        tex_string = "{:,}".format(31415926535897932384)
        number = TexMobject(tex_string)
        number.scale(1.5)
        number.to_edge(UP)

        commas = VGroup(*[
            mob
            for c, mob in zip(tex_string, number)
            if c is ","
        ])
        dots = VGroup(*[
            mob
            for c, mob in zip(digits.get_tex_string(), digits)
            if c is "."
        ])

        self.play(FadeOut(to_fade))
        self.play(
            ReplacementTransform(
                VGroup(*filter(lambda m: m not in dots, digits)),
                VGroup(*filter(lambda m: m not in commas, number)),
            ),
            ReplacementTransform(
                dots, commas,
                submobject_mode="lagged_start",
                run_time=2
            )
        )

        group0 = number[:2].copy()
        group1 = number[3:3 + 9 + 2].copy()
        group2 = number[-(9 + 2):].copy()
        for group in group0, group1, group2:
            group.set_background_stroke(color=BLUE, width=5)
            self.add(group)
            self.wait(0.5)
            self.remove(group)


class BlocksAndWallExampleGalacticMass(BlocksAndWallExample):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 1e10,
                "velocity": -1,
                "label_text": "$100^{(20 - 1)}$\\,kg",
                "width": 2,
            },
        },
        "wait_time": 25,
        "counter_group_shift_vect": 5 * LEFT,
        "count_clacks": False,
    }

    def setup(self):
        super().setup()
        words = TextMobject(
            "Burst of $10^{38}$ clacks per second"
        )
        words.scale(1.5)
        words.to_edge(UP)
        self.add(words)


class CompareAlgorithmToPhysics(PiCreatureScene):
    def construct(self):
        morty = self.pi_creature
        right_pic = ImageMobject(
            self.get_image_file_path().replace(
                str(self), "PiComputingAlgorithmsAxes"
            )
        )
        right_rect = SurroundingRectangle(right_pic, buff=0, color=WHITE)
        right_pic.add(right_rect)
        right_pic.set_height(3)
        right_pic.next_to(morty, UR)
        right_pic.shift_onto_screen()

        left_rect = right_rect.copy()
        left_rect.next_to(morty, UL)
        left_rect.shift_onto_screen()

        self.play(
            FadeInFromDown(right_pic),
            morty.change, "raise_right_hand",
        )
        self.wait()
        self.play(
            FadeInFromDown(left_rect),
            morty.change, "raise_left_hand",
        )
        self.wait()

        digits = TexMobject("3.141592653589793238462643383279502884197...")
        digits.set_width(FRAME_WIDTH - 1)
        digits.to_edge(UP)
        self.play(
            FadeOutAndShift(right_pic, 5 * RIGHT),
            # FadeOutAndShift(left_rect, 5 * LEFT),
            FadeOut(left_rect),
            PiCreatureBubbleIntroduction(
                morty, "This doesn't seem \\\\ like me...",
                bubble_class=ThoughtBubble,
                bubble_kwargs={"direction": LEFT},
                target_mode="pondering",
                look_at_arg=left_rect,
            ),
            LaggedStart(
                FadeInFrom, digits,
                lambda m: (m, LEFT),
                run_time=5,
                lag_ratio=0.2,
            )
        )
        self.blink()
        self.wait()
        self.play(morty.change, "confused", left_rect)
        self.wait(5)

    def create_pi_creature(self):
        return Mortimer().flip().to_edge(DOWN)


class AskAboutWhy(TeacherStudentsScene):
    def construct(self):
        circle = Circle(radius=2, color=YELLOW)
        circle.next_to(self.teacher, UL)
        ke_conservation = TexMobject(
            "\\frac{1}{2}m_1 v_1^2 + "
            "\\frac{1}{2}m_2 v_2^2 = \\text{const.}"
        )
        ke_conservation.move_to(circle)

        self.student_says("But why?")
        self.change_student_modes(
            "erm", "raise_left_hand", "sassy",
            added_anims=[self.teacher.change, "happy"]
        )
        self.wait()
        self.play(
            ShowCreation(circle),
            RemovePiCreatureBubble(self.students[1]),
            self.teacher.change, "raise_right_hand",
        )
        self.change_all_student_modes(
            "pondering", look_at_arg=circle
        )
        self.wait(2)
        self.play(
            Write(ke_conservation),
            circle.stretch, 1.5, 0,
        )
        self.change_all_student_modes("confused")
        self.look_at(circle)
        self.wait(3)


class LightBouncingNoFanning(LightBouncing):
    CONFIG = {
        "mirror_shift_vect": 2 * DOWN,
        "mirror_length": 6,
        "beam_start_x": 8,
        "beam_height": 0.5,
    }


class LightBouncingFanning(LightBouncingNoFanning):
    CONFIG = {
        "show_fanning": True,
    }


class NextVideo(Scene):
    def construct(self):
        pass
