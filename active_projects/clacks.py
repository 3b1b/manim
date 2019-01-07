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
        },
        "block2_config": {
            "mass": 1,
            "velocity": 0,
            "distance": 3,
            "width": None,
            "color": None,
        },
        "block_style": {
            "fill_opacity": 1,
            "stroke_width": 3,
            "stroke_color": WHITE,
            "sheen_direction": UL,
            "sheen_factor": 0.5,
            "sheen_direction": UL,
        }
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

        self.clack_data = self.get_clack_data()

    def get_block(self, mass, distance, velocity, width, color):
        if width is None:
            width = self.mass_to_width(mass)
        if color is None:
            color = self.mass_to_color(mass)
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
        label = block.label = TextMobject(
            "{:,}\\,kg".format(int(mass))
        )
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
        "include_sound_file": True,
        "count_clacks": True,
        "sliding_blocks_config": {},
        "floor_y": -2,
        "wall_x": -6,
        "counter_label": "\\# Collisions: ",
        "collision_sound": "clack.wav",
    }

    def setup(self):
        self.floor = self.get_floor()
        self.wall = self.get_wall()
        self.blocks = SlidingBlocks(self, **self.sliding_blocks_config)
        self.clack_data = self.blocks.clack_data
        self.clack_flashes = ClackFlashes(self.clack_data)
        self.add(self.floor, self.wall, self.blocks, self.clack_flashes)

        if self.count_clacks:
            self.add_counter()
        self.track_time()

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
        clack_group = VGroup(
            counter_label,
            counter_mob,
        )
        clack_group.to_corner(UR)
        clack_group.shift(LEFT)
        self.add(clack_group)

        self.counter_mob = counter_mob

    def get_wall(self):
        wall = Line(self.floor_y * UP, FRAME_HEIGHT * UP / 2)
        wall.shift(self.wall_x * RIGHT)
        lines = VGroup(*[
            Line(ORIGIN, 0.25 * UR)
            for x in range(15)
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
        if self.include_sound_file:
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


class LightBouncing(Scene):
    CONFIG = {
        "theta": np.arctan(0.1)
    }

    def construct(self):
        pass


class BlocksAndWallExampleSameMass(BlocksAndWallScene):
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


class BlocksAndWallExampleMass1e1(BlocksAndWallExampleSameMass):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 1e1,
                "velocity": -1.5,
            }
        },
        "wait_time": 20,
    }


class BlocksAndWallExampleMass1e2(BlocksAndWallExampleSameMass):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 1e2,
                "velocity": -1,
            }
        },
        "wait_time": 20,
    }


class BlocksAndWallExampleMass1e4(BlocksAndWallExampleSameMass):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 1e4,
                "velocity": -1.5,
            },
        },
        "wait_time": 25,
    }


class BlocksAndWallExampleMass1e4SlowMo(BlocksAndWallExampleSameMass):
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


class BlocksAndWallExampleMass1e6(BlocksAndWallExampleSameMass):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 1e6,
                "velocity": -1,
            },
        },
        "wait_time": 20,
    }


class BlocksAndWallExampleMass1e6SlowMo(BlocksAndWallExampleSameMass):
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


class BlocksAndWallExampleMass1e8(BlocksAndWallExampleSameMass):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 1e8,
                "velocity": -1,
            },
        },
        "wait_time": 25,
    }


class BlocksAndWallExampleMass1e10(BlocksAndWallExampleSameMass):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 1e10,
                "velocity": -1,
            },
        },
        "wait_time": 25,
    }
