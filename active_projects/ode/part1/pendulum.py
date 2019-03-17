from big_ol_pile_of_manim_imports import *


class Pendulum(VGroup):
    CONFIG = {
        "length": 3,
        "gravity": 9.8,
        "weight_diameter": 0.5,
        "initial_theta": 0.3,
        "omega": 0,
        "damping": 0.1,
        "top_point": 2 * UP,
        "rod_style": {
            "stroke_width": 3,
            "stroke_color": LIGHT_GREY,
            "sheen_direction": UP,
            "sheen_factor": 1,
        },
        "weight_style": {
            "stroke_width": 0,
            "fill_opacity": 1,
            "fill_color": DARK_GREY,
            "sheen_direction": UL,
            "sheen_factor": 0.5,
        },
        "dashed_line_config": {
            "num_dashes": 25,
            "stroke_color": WHITE,
            "stroke_width": 2,
        },
        "angle_arc_config": {
            "radius": 1,
            "stroke_color": WHITE,
            "stroke_width": 2,
        },
        "velocity_vector_config": {
            "color": RED,
        },
        "n_steps_per_frame": 10,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_fixed_point()
        self.create_rod()
        self.create_weight()
        self.rotating_group = VGroup(self.rod, self.weight)
        self.create_dashed_line()
        self.create_angle_arc()

        self.set_theta(self.initial_theta)
        self.update()

    def create_fixed_point(self):
        self.fixed_point_tracker = VectorizedPoint(self.top_point)

    def create_rod(self):
        rod = self.rod = Line(UP, DOWN)
        rod.set_height(self.length)
        rod.set_style(**self.rod_style)
        rod.move_to(self.get_fixed_point(), UP)
        self.add(rod)

    def create_weight(self):
        weight = self.weight = Circle()
        weight.set_width(self.weight_diameter)
        weight.set_style(**self.weight_style)
        weight.move_to(self.rod.get_end())
        self.add(weight)

    def create_dashed_line(self):
        line = self.dashed_line = DashedLine(
            self.get_fixed_point(),
            self.get_fixed_point() + self.length * DOWN,
            **self.dashed_line_config
        )
        self.add_to_back(line)

    def create_angle_arc(self):
        self.angle_arc = always_redraw(lambda: Arc(
            arc_center=self.get_fixed_point(),
            start_angle=-90 * DEGREES,
            angle=self.get_theta(),
            **self.angle_arc_config,
        ))
        self.add(self.angle_arc)

    def add_velocity_vector(self):
        def make_vector():
            omega = self.get_omega()
            theta = self.get_theta()
            vector = Vector(
                0.5 * omega * RIGHT,
                **self.velocity_vector_config,
            )
            vector.rotate(theta, about_point=ORIGIN)
            vector.shift(self.rod.get_end())
            return vector

        self.velocity_vector = always_redraw(make_vector)
        self.add(self.velocity_vector)
        return self

    def add_theta_label(self):
        label = self.theta_label = TexMobject("\\theta")

        def update_label(l):
            top = self.get_fixed_point()
            arc_center = self.angle_arc.point_from_proportion(0.5)
            l.move_to(top + 1.3 * (arc_center - top))
        label.add_updater(update_label)
        self.add(label)

    #
    def get_theta(self):
        theta = self.rod.get_angle() - self.dashed_line.get_angle()
        theta = (theta + PI) % TAU - PI
        return theta

    def set_theta(self, theta):
        self.rotating_group.rotate(
            theta - self.get_theta()
        )
        self.rotating_group.shift(
            self.get_fixed_point() - self.rod.get_start(),
        )
        return self

    def get_omega(self):
        return self.omega

    def set_omega(self, omega):
        self.omega = omega
        return self

    def get_fixed_point(self):
        return self.fixed_point_tracker.get_location()

    #
    def start_swinging(self):
        self.add_updater(Pendulum.update_by_gravity)

    def end_swinging(self):
        self.remove_updater(Pendulum.update_by_gravity)

    def update_by_gravity(self, dt):
        theta = self.get_theta()
        omega = self.get_omega()
        nspf = self.n_steps_per_frame
        for x in range(nspf):
            d_theta = omega * dt / nspf
            d_omega = op.add(
                -self.damping * omega,
                -(self.gravity / self.length) * np.sin(theta),
            ) * dt / nspf
            theta += d_theta
            omega += d_omega
        self.set_theta(theta)
        self.set_omega(omega)
        return self


class GravityVector(Vector):
    CONFIG = {
        "color": YELLOW,
        "length": 1,
    }

    def __init__(self, pendulum, **kwargs):
        super().__init__(DOWN)
        self.pendulum = pendulum
        self.scale(self.length)
        self.add_updater(lambda m: m.shift(
            pendulum.rod.get_end() - self.get_start(),
        ))

    def add_component_lines(self):
        self.component_lines = always_redraw(self.create_component_lines)
        self.add(self.component_lines)

    def create_component_lines(self):
        theta = self.pendulum.get_theta()
        x_new = rotate(RIGHT, theta)
        base = self.get_start()
        tip = self.get_end()
        vect = tip - base
        corner = base + x_new * np.dot(vect, x_new)
        kw = {"dash_length": 0.025}
        return VGroup(
            DashedLine(base, corner, **kw),
            DashedLine(tip, corner, **kw),
        )


class PendulumTest(Scene):
    def construct(self):
        pendulum = Pendulum(
            initial_theta=150 * DEGREES,
        )
        pendulum.add_velocity_vector()
        pendulum.add_theta_label()

        gravity_vector = GravityVector(pendulum)
        gravity_vector.add_component_lines()

        self.add(pendulum, gravity_vector)
        pendulum.start_swinging()
        self.wait(10)
