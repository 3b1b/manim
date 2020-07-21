#!/usr/bin/env python

from manimlib.imports import *

# To watch one of these scenes, run the following:
# python -m manim example_scenes.py SquareToCircle -pl
#
# Use the flat -l for a faster rendering at a lower
# quality.
# Use -s to skip to the end and just save the final frame
# Use the -p to have the animation (or image, if -s was
# used) pop up once done.
# Use -n <number> to skip ahead to the n'th animation of a scene.
# Use -r <number> to specify a resolution (for example, -r 1080
# for a 1920x1080 video)


class OpeningManimExample(Scene):
    def construct(self):
        title = TextMobject("This is some \\LaTeX")
        basel = TexMobject(
            "\\sum_{n=1}^\\infty "
            "\\frac{1}{n^2} = \\frac{\\pi^2}{6}"
        )
        VGroup(title, basel).arrange(DOWN)
        self.play(
            Write(title),
            FadeInFrom(basel, UP),
        )
        self.wait()

        transform_title = TextMobject("That was a transform")
        transform_title.to_corner(UP + LEFT)
        self.play(
            Transform(title, transform_title),
            LaggedStart(*map(FadeOutAndShiftDown, basel)),
        )
        self.wait()

        grid = NumberPlane()
        grid_title = TextMobject("This is a grid")
        grid_title.scale(1.5)
        grid_title.move_to(transform_title)

        self.add(grid, grid_title)  # Make sure title is on top of grid
        self.play(
            FadeOut(title),
            FadeInFromDown(grid_title),
            ShowCreation(grid, run_time=3, lag_ratio=0.1),
        )
        self.wait()

        grid_transform_title = TextMobject(
            "That was a non-linear function \\\\"
            "applied to the grid"
        )
        grid_transform_title.move_to(grid_title, UL)
        grid.prepare_for_nonlinear_transform()
        self.play(
            grid.apply_function,
            lambda p: p + np.array([
                np.sin(p[1]),
                np.sin(p[0]),
                0,
            ]),
            run_time=3,
        )
        self.wait()
        self.play(
            Transform(grid_title, grid_transform_title)
        )
        self.wait()


class SquareToCircle(Scene):
    def construct(self):
        circle = Circle()
        square = Square()
        square.flip(RIGHT)
        square.rotate(-3 * TAU / 8)
        circle.set_fill(PINK, opacity=0.5)

        self.play(ShowCreation(square))
        self.play(Transform(square, circle))
        self.play(FadeOut(square))


class WarpSquare(Scene):
    def construct(self):
        square = Square()
        self.play(ApplyPointwiseFunction(
            lambda point: complex_to_R3(np.exp(R3_to_complex(point))),
            square
        ))
        self.wait()


class WriteStuff(Scene):
    def construct(self):
        example_text = TextMobject(
            "This is a some text",
            tex_to_color_map={"text": YELLOW}
        )
        example_tex = TexMobject(
            "\\sum_{k=1}^\\infty {1 \\over k^2} = {\\pi^2 \\over 6}",
        )
        group = VGroup(example_text, example_tex)
        group.arrange(DOWN)
        group.set_width(FRAME_WIDTH - 2 * LARGE_BUFF)

        self.play(Write(example_text))
        self.play(Write(example_tex))
        self.wait()


class UpdatersExample(Scene):
    def construct(self):
        decimal = DecimalNumber(
            0,
            show_ellipsis=True,
            num_decimal_places=3,
            include_sign=True,
        )
        square = Square().to_edge(UP)

        decimal.add_updater(lambda d: d.next_to(square, RIGHT))
        decimal.add_updater(lambda d: d.set_value(square.get_center()[1]))
        self.add(square, decimal)
        self.play(
            square.to_edge, DOWN,
            rate_func=there_and_back,
            run_time=5,
        )
        self.wait()

class PhysicExample(PhysicScene):
    def construct(self):
        self.set_gravity(9.8 * DOWN)

        grd_body = self.space.static_body
        grd_seg = pymunk.Segment(grd_body, (-10, -2), (10, -2), 0)
        grd_seg.friction = 0.7
        grd_seg.elasticity = 0.8
        grd_shape = Line(
            LEFT*10,
            RIGHT*10
        ).shift(2 * DOWN)

        ground = PhysicMobject(grd_body, grd_seg, grd_shape)
        self.add_static_obj(ground)
        

        for i in range(30):
            mass = 10
            r = 0.5
            size=(r, r)
            moment = pymunk.moment_for_box(mass, size)
            body = pymunk.Body(mass, moment)
            body.angle = i * 0.1
            body.position = (i * 0.3 - 5), 4
            box = pymunk.Poly.create_box(body, size)
            box.friction = 0.5
            box.elasticity = 0.8

            shape = Square()
            shape.stretch_to_fit_height(r)
            shape.stretch_to_fit_width(r)
            shape.set_fill(DARK_BLUE, opacity=1)

            mobj = PhysicMobject(body, box, shape)
            mobj.set_add_time(i * 0.5)

            self.add_physic_obj(mobj)

        self.simulate(20)

class BouncingBall(PhysicScene):
    def construct(self):
        self.set_gravity(9*DOWN)

        r = np.sqrt(2)
        mass = 10

        moment = pymunk.moment_for_circle(mass, 0, r)
        body = pymunk.Body(mass, moment)
        ground_body = self.space.static_body

        body.position = 0, 2
        
        mob = Circle(radius=r)
        mob.set_fill(RED, opacity=0.8).shift(2*UP)
        ground_mob = Line(7 * LEFT, 7 * RIGHT).set_color(GREEN).shift(DOWN)

        shape = pymunk.Circle(body, mob.radius)
        ground_shape = pymunk.Segment(ground_body, (-7, -1), (7, -1), 0)
        shape.friction = ground_shape.friction = 0.9
        shape.elasticity = ground_shape.elasticity = 0.8
        self.add(mob, ground_mob)
        circle = PhysicMobject(body, shape, mob)
        ground = PhysicMobject(ground_body, ground_shape, ground_mob)
        self.add_physic_obj(circle)
        self.add_static_obj(ground)
        self.simulate(4)
        
# See old_projects folder for many, many more