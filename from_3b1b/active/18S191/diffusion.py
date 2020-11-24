from manimlib.imports import *


class Diffusion1D(Scene):
    CONFIG = {
        "n_dots": 100,
        "y_range": (0, 100, 10),
        "x_range": (-20, 20),
        "show_y_axis": False,
        "dot_radius": 0.07,
        "dot_opacity": 0.5,
        "dither_dots": True,
        "total_steps": 100,
        "clip_at_bounds": True,
    }

    def construct(self):
        y_range = self.y_range
        x_range = self.x_range

        # Set up axes
        axes = Axes(
            x_range=x_range,
            y_range=y_range,
            axis_config={
                "stroke_width": 2,
                "include_tip": False,
            },
            width=FRAME_WIDTH,
            height=FRAME_HEIGHT - 1,
        )

        axes.x_axis.add_numbers(
            range(*x_range, 5)
        )

        if self.show_y_axis:
            axes.y_axis.add_numbers(
                np.arange(*y_range) + y_range[2],
                number_config={'height': 0.2}
            )
        else:
            axes.y_axis.scale(0, about_point=axes.c2p(0, 0))

        axes.center()
        x_unit = axes.c2p(1, 0)[0] - axes.c2p(0, 0)[0]
        y_unit = axes.c2p(0, 1)[1] - axes.c2p(0, 0)[1]

        self.add(axes)

        # Set up time label
        time_label = self.get_time_label()
        self.add(time_label)

        # Set up dots (make generalizable)
        dots = self.get_dots()
        dots.move_to(axes.c2p(0, 0))
        self.adjust_initial_dot_positions(dots, x_unit)
        self.add(dots)

        # Set up bars
        bars = VGroup()
        epsilon = 1e-6

        for x in range(x_range[0], x_range[1] + 1):
            bar = Rectangle()
            bar.x = x
            bar.set_width(0.5 * x_unit)
            bar.set_height(epsilon, stretch=True)
            bar.move_to(axes.c2p(x, 0), DOWN)
            bars.add(bar)

        bars.set_fill(GREY, 0.8)
        bars.set_stroke(LIGHT_GREY, 0.2)

        def update_bars(bars, dots=dots, y_unit=y_unit, epsilon=epsilon):
            for bar in bars:
                count = 0
                for dot in dots:
                    if dot.x == bar.x:
                        count += 1
                bar.set_height(
                    count * y_unit + epsilon,
                    about_edge=bar.get_bottom(),
                    stretch=True
                )

        update_bars(bars, dots)

        self.add(bars, dots)

        # Include rule for updating
        def step(dots=dots, bars=bars,
                 x_unit=x_unit, x_range=x_range,
                 time_label=time_label):
            time_label[1].increment_value()
            for dot in dots:
                u = random.choice([-1, 1])

                if self.clip_at_bounds:
                    # Boundary condition
                    if dot.x == x_range[0]:
                        u = max(0, u)
                    elif dot.x == x_range[1]:
                        u = min(0, u)
                dot.shift(u * x_unit * RIGHT)
                dot.x += u

            update_bars(bars)

        # Let it play out.
        for t in range(self.total_steps):
            if t < 6:
                self.wait()
            else:
                self.wait(0.1)
            step()

    def get_time_label(self):
        time_label = VGroup(
            TextMobject("Time: "),
            Integer(0),
        )
        time_label.arrange(RIGHT, aligned_edge=DOWN)
        time_label.to_corner(UR)
        time_label.shift(0.5 * LEFT)
        return time_label

    def get_dots(self):
        dots = VGroup(*[Dot() for x in range(self.n_dots)])
        dots.set_height(2 * self.dot_radius)
        dots.set_fill(opacity=self.dot_opacity)

        for dot in dots:
            dot.x = 0
            if self.dither_dots:
                dot.shift(
                    self.dot_radius * random.random() * RIGHT,
                    self.dot_radius * random.random() * UP
                )
            dot.set_color(interpolate_color(
                BLUE_B, BLUE_D, random.random()
            ))

        return dots

    def adjust_initial_dot_positions(self, dots, x_unit):
        pass


class Diffusion1DWith1Dot(Diffusion1D):
    CONFIG = {
        "n_dots": 1,
        "dot_radius": 0.1,
        "dot_opacity": 1,
        "dither_dots": False,
    }


class Diffusion1DStepFunction(Diffusion1D):
    CONFIG = {
        "n_dots": 15000,
        "initial_range": (-20, 0),
        "y_range": (0, 1000, 100),
        "total_steps": 100,
    }

    def adjust_initial_dot_positions(self, dots, x_unit):
        initial_positions = list(range(*self.initial_range))
        for n, dot in enumerate(dots):
            x = initial_positions[n % len(initial_positions)]
            dot.x = x
            dot.shift(x * x_unit * RIGHT)


class Diffusion1DStepFunctionGraphed(Diffusion1DStepFunction):
    CONFIG = {
        "show_y_axis": True,
        "total_steps": 500,
    }


class DiffusionDeltaGraphed(Diffusion1D):
    CONFIG = {
        "n_dots": 1000,
        "show_y_axis": True,
        "y_range": (0, 1000, 100),
        "total_steps": 200,
    }


class DiffusionDeltaGraphedTripleStart(DiffusionDeltaGraphed):
    CONFIG = {
        "n_dots": 2000,
    }

    def adjust_initial_dot_positions(self, dots, x_unit):
        for n, dot in enumerate(dots):
            x = int(n % 4 - 1.5)
            dot.x = x
            dot.shift(x * x_unit * RIGHT)


class DiffusionDeltaGraphedShowingMean(DiffusionDeltaGraphed):
    CONFIG = {
        "n_dots": 10000,
        "y_range": (0, 10000, 1000),
        "clip_at_bounds": False,
        "total_steps": 100,
    }

    def adjust_initial_dot_positions(self, dots, x_unit):
        # Hack, just using this to add something new and updated
        label = VGroup(
            TexMobject("\\overline{x^2} = "),
            DecimalNumber(0),
        )
        label.arrange(RIGHT)
        label.to_corner(UL)
        label.add_updater(lambda m: m[1].set_value(np.mean([
            dot.x**2 for dot in dots
        ])))

        self.add(label)


class Diffusion2D(Diffusion1D):
    CONFIG = {
        "n_dots": 100,
        "dot_opacity": 0.5,
        "dither_dots": True,
        "grid_dimensions": (19, 35),
    }

    def construct(self):
        grid_dimensions = self.grid_dimensions

        # Setup grid
        grid = VGroup(*[
            Square()
            for x in range(grid_dimensions[0])
            for y in range(grid_dimensions[1])
        ])
        grid.arrange_in_grid(*grid_dimensions, buff=0)
        grid.set_height(FRAME_HEIGHT)
        grid.set_stroke(LIGHT_GREY, 1)

        self.add(grid)

        step_size = get_norm(grid[1].get_center() - grid[0].get_center())

        # Add time label
        time_label = self.get_time_label()
        br = BackgroundRectangle(time_label)
        br.stretch(1.5, 0, about_edge=LEFT)
        time_label.add_to_back(br)
        self.add(time_label)

        # Initialize dots
        dots = self.get_dots()
        self.add(dots)

        # Rule for updating
        def step(dots=dots, step_size=step_size, time_label=time_label):
            for dot in dots:
                vect = random.choice([
                    UP, DOWN, LEFT, RIGHT, ORIGIN
                ])
                dot.shift(step_size * vect)
            time_label[-1].increment_value()

        # Let it play out
        for t in range(self.total_steps):
            if t < 6:
                self.wait()
            else:
                self.wait(0.1)
            step()


class Diffusion2D1Dot(Diffusion2D):
    CONFIG = {
        "n_dots": 1,
        "dither_dots": False,
        "dot_opacity": 1,
        "total_steps": 50,
    }


class Diffusion2D10KDots(Diffusion2D):
    CONFIG = {
        "n_dots": 10000,
        "dot_opacity": 0.2,
        "total_steps": 200,
    }
