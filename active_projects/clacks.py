from big_ol_pile_of_manim_imports import *


class SlidingBlocks(VGroup):
    CONFIG = {
        "block1_config": {
            "mass": 1,
            "velocity": -2,
            "distance": 7,
            "width": 1,
        },
        "block2_config": {
            "mass": 1,
            "velocity": 0,
            "distance": 3,
            "width": 1,
        },
        "block_style": {
            "fill_opacity": 1,
            "fill_color": (GREY, LIGHT_GREY),
            "stroke_width": 3,
            "stroke_color": WHITE,
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
        self.phase_space_point_tracker = self.get_phase_space_point_tracker()
        self.add(
            self.block1, self.block2,
            self.phase_space_point_tracker,
        )
        self.add_updater(self.__class__.update_positions)

        # From here, there's enough information to create
        # a list of all clack times and locations

    def get_block(self, mass, width, distance, velocity):
        block = Square(side_length=width)
        block.mass = mass
        block.velocity = velocity

        block.set_style(**self.block_style)
        block.set_fill(color=interpolate_color(
            block.get_fill_color(),
            BLUE_E,
            (1 - 1.0 / (max(np.log10(mass), 1)))
        ))
        block.move_to(
            self.floor.get_top()[1] * UP +
            (self.wall.get_right()[0] + distance) * RIGHT,
            DL,
        )
        label = block.label = TextMobject(
            "{:,}\\,kg".format(mass)
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
        theta = np.arctan(np.sqrt(block2.mass / block1.mass))
        ps_point_angle = angle_of_vector(ps_point)
        n_clacks = int(ps_point_angle / theta)
        # TODO, pass on n_clack information to surrounding_scene
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


class BlocksAndWallScene(Scene):
    CONFIG = {
        "print_clack_times": False,
        "count_clacks": True,
        "sliding_blocks_config": {},
        "floor_y": -2,
        "wall_x": -5,
    }

    def setup(self):
        self.floor = self.get_floor()
        self.wall = self.get_wall()
        self.blocks = SlidingBlocks(self, **self.sliding_blocks_config)
        self.add(self.floor, self.wall, self.blocks)
        if self.count_clacks:
            self.add_clack_counter()

        self.track_times()

    def track_times(self):
        self.clack_times = []
        time_tracker = ValueTracker()
        time_tracker.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(time_tracker)
        self.get_time = time_tracker.get_value

    def add_clack_counter(self):
        clack_counter_label = TextMobject("\\# Clacks: ")
        clack_counter = Integer(0)
        clack_counter.next_to(
            clack_counter_label[-1], RIGHT,
            aligned_edge=DOWN,
        )
        clack_group = VGroup(
            clack_counter_label,
            clack_counter,
        )
        clack_group.to_corner(UR)
        clack_group.shift(LEFT)
        self.add(clack_group)

        self.clack_counter = clack_counter

    def tear_down(self):
        if self.print_clack_times:
            print(self.clack_times)

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

    def clack(self, location):
        self.clack_times.append(self.get_time())
        if self.count_clacks:
            self.clack_counter.increment_value()


# Animted scenes

class MathAndPhysicsConspiring(Scene):
    def construct(self):
        pass


class ThreeSimpleClacks(BlocksAndWallScene):
    CONFIG = {
        "sliding_blocks_config": {
            "block1_config": {
                "mass": 100,
                "width": 1.5,
            }
        }
    }

    def construct(self):
        while self.blocks[0].get_left()[0] < FRAME_WIDTH / 2:
            self.wait(1)
