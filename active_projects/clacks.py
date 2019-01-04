from big_ol_pile_of_manim_imports import *


class SlidingBlocks(VGroup):
    CONFIG = {
        "block_dynamic_configs": [
            {
                "mass": 100,
                "velocity": -2,
                "distance": 7,
                "width": 1,
            },
            {
                "mass": 1,
                "velocity": 0,
                "distance": 3,
                "width": 1,
            },
        ],
        "block_style": {
            "fill_opacity": 1,
            "fill_color": (GREY, LIGHT_GREY),
            "stroke_width": 3,
            "stroke_color": WHITE,
        }
    }

    def __init__(self, surrounding_scene, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.surrounding_scene = surrounding_scene
        self.floor = surrounding_scene.floor
        self.wall = surrounding_scene.wall

        for config in self.block_dynamic_configs:
            self.add(self.get_block(**config))
        self.add_updater(self.__class__.update_positions)

    def get_block(self, mass, width, distance, velocity):
        block = Square(side_length=width)
        block.set_style(**self.block_style)
        block.move_to(
            self.floor.get_top()[1] * UP +
            (self.wall.get_right()[0] + distance) * RIGHT,
            DL,
        )
        block.mass = mass
        block.velocity = velocity
        label = block.label = TextMobject("{}kg".format(mass))
        label.scale(0.8)
        label.next_to(block, UP, SMALL_BUFF)
        block.add(label)
        return block

    def update_positions(self, dt):
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
            self.surrounding_scene.clack(blocks[1].get_left())
        return self


class BlocksAndWallScene(Scene):
    CONFIG = {
        "print_clack_times": True,
        "sliding_blocks_config": {},
        "floor_y": -2,
        "wall_x": -5,
    }

    def setup(self):
        self.floor = self.get_floor()
        self.wall = self.get_wall()
        self.blocks = SlidingBlocks(self)
        self.clack_times = []
        time_tracker = ValueTracker()
        time_tracker.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(time_tracker)
        self.get_time = time_tracker.get_value

        self.add(self.floor, self.wall, self.blocks)

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

    def get_blocks(self):
        pass

    def clack(self, location):
        self.clack_times.append(self.get_time())


# Animted scenes

class MathAndPhysicsConspiring(Scene):
    def construct(self):
        pass


class ThreeSimpleClacks(BlocksAndWallScene):
    def construct(self):
        self.wait(10)
