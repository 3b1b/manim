from manimlib.imports import *
# import scipy.stats


SICKLY_GREEN = "#9BBD37"
COLOR_MAP = {
    "S": BLUE,
    "I": RED,
    "R": GREY_D,
}


def update_time(mob, dt):
    mob.time += dt


class Person(VGroup):
    CONFIG = {
        "status": "S",  # S, I or R
        "height": 0.2,
        "color_map": COLOR_MAP,
        "infection_ring_style": {
            "stroke_color": RED,
            "stroke_opacity": 0.8,
            "stroke_width": 0,
        },
        "infection_radius": 0.5,
        "infection_animation_period": 2,
        "max_speed": 1,
        "dl_bound": [-FRAME_WIDTH / 2, -FRAME_HEIGHT / 2],
        "ur_bound": [FRAME_WIDTH / 2, FRAME_HEIGHT / 2],
        "gravity_well": None,
        "gravity_strength": 1,
        "wander_step_size": 1,
        "wander_step_duration": 1,
        "social_distance_factor": 0,
        "n_repulsion_points": 10,
        "social_distance_color": YELLOW,
        "max_social_distance_stroke_width": 5,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.time = 0
        self.last_step_change = -1
        self.change_anims = []
        self.velocity = np.zeros(3)
        self.infection_start_time = np.inf
        self.infection_end_time = np.inf
        self.repulsion_points = []

        self.center_point = VectorizedPoint()
        self.add(self.center_point)
        self.add_body()
        self.add_infection_ring()
        self.set_status(self.status, run_time=0)

        # Updaters
        self.add_updater(update_time)
        self.add_updater(lambda m, dt: m.update_position(dt))
        self.add_updater(lambda m, dt: m.update_infection_ring(dt))
        self.add_updater(lambda m: m.progress_through_change_anims())

    def add_body(self):
        body = self.get_body()
        body.set_height(self.height)
        body.move_to(self.get_center())
        self.add(body)
        self.body = body

    def get_body(self, status):
        person = SVGMobject(file_name="person")
        person.set_stroke(width=0)
        return person

    def set_status(self, status, run_time=1):
        start_color = self.color_map[self.status]
        end_color = self.color_map[status]
        anims = [
            UpdateFromAlphaFunc(
                self.body,
                lambda m, a: m.set_color(interpolate_color(
                    start_color, end_color, a
                )),
                run_time=run_time,
            )
        ]
        for anim in anims:
            self.push_anim(anim)

        if status == "I":
            self.infection_start_time = self.time
            self.infection_ring.set_stroke(width=0, opacity=0)
        if self.status == "I":
            self.infection_end_time = self.time

        self.status = status

    def push_anim(self, anim):
        anim.begin()
        anim.start_time = self.time
        self.change_anims.append(anim)
        return self

    def pop_anim(self, anim):
        anim.update(1)
        anim.finish()
        self.change_anims.remove(anim)

    def add_infection_ring(self):
        self.infection_ring = Circle(
            radius=self.height / 2,
        )
        self.infection_ring.set_style(**self.infection_ring_style)
        self.add(self.infection_ring)
        self.infection_ring.time = 0
        return self

    def update_position(self, dt):
        center = self.get_center()
        total_force = np.zeros(3)

        # Gravity
        if self.wander_step_size != 0:
            if (self.time - self.last_step_change) > self.wander_step_duration:
                vect = rotate_vector(RIGHT, TAU * random.random())
                self.gravity_well = center + self.wander_step_size * vect
                self.last_step_change = self.time

        if self.gravity_well is not None:
            to_well = (self.gravity_well - center)
            dist = get_norm(to_well)
            if dist != 0:
                total_force += self.gravity_strength * to_well / (dist**3)

        # Potentially avoid neighbors
        if self.social_distance_factor > 0:
            repulsion_force = np.zeros(3)
            min_dist = np.inf
            for point in self.repulsion_points:
                to_point = point - center
                dist = get_norm(to_point)
                if dist < min_dist:
                    min_dist = dist
                if dist > 0:
                    repulsion_force -= self.social_distance_factor * to_point / (dist**3)
            self.body.set_stroke(
                self.social_distance_color,
                width=clip(4 * min_dist - 1, 0, self.max_social_distance_stroke_width),
                background=True,
            )
            total_force += repulsion_force

        # Avoid walls
        wall_force = np.zeros(3)
        for i in range(2):
            to_lower = center[i] - self.dl_bound[i]
            to_upper = self.ur_bound[i] - center[i]

            # Bounce
            if to_lower < 0:
                self.velocity[i] = abs(self.velocity[i])
            if to_upper < 0:
                self.velocity[i] = -abs(self.velocity[i])

            # Repelling force
            wall_force[i] += max((-1 + 1 / to_lower), 0)
            wall_force[i] -= max((-1 + 1 / to_upper), 0)
        total_force += wall_force

        # Apply force
        self.velocity += total_force * dt

        # Limit speed
        speed = get_norm(self.velocity)
        if speed > self.max_speed:
            self.velocity *= self.max_speed / speed

        # Update velocity
        self.shift(self.velocity * dt)

    def update_infection_ring(self, dt):
        ring = self.infection_ring
        if not (self.infection_start_time <= self.time <= self.infection_end_time + 1):
            return self

        ring_time = self.time - self.infection_start_time
        period = self.infection_animation_period

        alpha = (ring_time % period) / period
        ring.set_height(interpolate(
            self.height,
            self.infection_radius,
            smooth(alpha),
        ))
        ring.set_stroke(
            width=interpolate(
                0, 5,
                there_and_back(alpha),
            ),
            opacity=min([
                min([ring_time, 1]),
                min([self.infection_end_time + 1 - self.time, 1]),
            ]),
        )

        return self

    def progress_through_change_anims(self):
        for anim in self.change_anims:
            if anim.run_time == 0:
                alpha = 1
            else:
                alpha = (self.time - anim.start_time) / anim.run_time
            anim.update(alpha)
            if alpha >= 1:
                self.pop_anim(anim)

    def get_center(self):
        return self.center_point.points[0]


class DotPerson(Person):
    def get_body(self):
        return Dot()


class PiPerson(Person):
    CONFIG = {
        "mode_map": {
            "S": "guilty",
            "I": "sick",
            "R": "tease",
        }
    }

    def get_body(self):
        return Randolph()

    def set_status(self, status, run_time=1):
        super().set_status(status)

        target = self.body.copy()
        target.change(self.mode_map[status])
        target.set_color(self.color_map[status])

        transform = Transform(self.body, target)
        transform.begin()

        def update(body, alpha):
            transform.update(alpha)
            body.move_to(self.center_point)

        anims = [
            UpdateFromAlphaFunc(self.body, update, run_time=run_time),
        ]
        for anim in anims:
            self.push_anim(anim)

        return self


class SIRSimulation(VGroup):
    CONFIG = {
        "n_cities": 1,
        "city_population": 100,
        "box_size": 7,
        "person_type": PiPerson,
        "person_config": {
            "height": 0.2,
            "infection_radius": 0.6,
            "gravity_strength": 1,
            "wander_step_size": 1,
        },
        "p_infection_per_day": 0.2,
        "infection_time": 5,
        "travel_rate": 0,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.time = 0
        self.add_updater(update_time)

        self.add_boxes()
        self.add_people()

        self.add_updater(lambda m, dt: m.update_statusses(dt))

    def add_boxes(self):
        boxes = VGroup()
        for x in range(self.n_cities):
            box = Square()
            box.set_height(self.box_size)
            box.set_stroke(WHITE, 3)
            boxes.add(box)
        boxes.arrange_in_grid(buff=LARGE_BUFF)
        self.add(boxes)
        self.boxes = boxes

    def add_people(self):
        people = VGroup()
        for box in self.boxes:
            dl_bound = box.get_corner(DL)
            ur_bound = box.get_corner(UR)
            for x in range(self.city_population):
                person = self.person_type(
                    dl_bound=dl_bound,
                    ur_bound=ur_bound,
                    **self.person_config
                )
                person.move_to([
                    interpolate(lower, upper, random.random())
                    for lower, upper in zip(dl_bound, ur_bound)
                ])
                person.box = box
                people.add(person)

        # Choose a patient zero
        random.choice(people).set_status("I")
        self.add(people)
        self.people = people

    def update_statusses(self, dt):
        s_group, i_group = [
            list(filter(
                lambda m: m.status == status,
                self.people
            ))
            for status in ["S", "I"]
        ]

        for s_person in s_group:
            for i_person in i_group:
                dist = get_norm(i_person.get_center() - s_person.get_center())
                if dist < s_person.infection_radius and random.random() < self.p_infection_per_day * dt:
                    s_person.set_status("I")
        for i_person in i_group:
            if (i_person.time - i_person.infection_start_time) > self.infection_time:
                i_person.set_status("R")

        # Travel
        if self.travel_rate > 0:
            path_func = path_along_arc(45 * DEGREES)
            for person in self.people:
                if random.random() < self.travel_rate * dt:
                    new_box = random.choice(self.boxes)
                    person.box = new_box
                    person.dl_bound = new_box.get_corner(DL)
                    person.ur_bound = new_box.get_corner(UR)
                    person.old_center = person.get_center()
                    person.new_center = new_box.get_center()
                    anim = UpdateFromAlphaFunc(
                        person,
                        lambda m, a: m.move_to(path_func(
                            m.old_center, m.new_center, a,
                        )),
                        run_time=3,
                    )
                    person.push_anim(anim)

        # Social distancing
        centers = np.array([person.get_center() for person in self.people])
        for center, person in zip(centers, self.people):
            if person.social_distance_factor > 0:
                diffs = np.linalg.norm(centers - center, axis=1)
                person.repulsion_points = centers[np.argsort(diffs)[1:person.n_repulsion_points + 1]]

    def get_status_counts(self):
        return np.array([
            len(list(filter(
                lambda m: m.status == status,
                self.people
            )))
            for status in "SIR"
        ])

    def get_status_proportions(self):
        counts = self.get_status_counts()
        return counts / sum(counts)


class SIRGraph(VGroup):
    CONFIG = {
        "color_map": COLOR_MAP,
        "height": 7,
        "width": 5,
        "update_frequency": 0.5,
        "include_braces": False,
    }

    def __init__(self, simulation, **kwargs):
        super().__init__(**kwargs)
        self.simulation = simulation
        self.data = [simulation.get_status_proportions()] * 2
        self.add_axes()
        self.add_graph()
        self.add_x_labels()

        self.time = 0
        self.last_update_time = 0
        self.add_updater(update_time)
        self.add_updater(lambda m: m.update_graph())
        self.add_updater(lambda m: m.update_x_labels())

    def add_axes(self):
        axes = Axes(
            y_min=0,
            y_max=1,
            y_axis_config={
                "tick_frequency": 0.1,
            },
            x_min=0,
            x_max=1,
            axis_config={
                "include_tip": False,
            },
        )
        origin = axes.c2p(0, 0)
        axes.x_axis.set_width(self.width, about_point=origin, stretch=True)
        axes.y_axis.set_height(self.height, about_point=origin, stretch=True)

        self.add(axes)
        self.axes = axes

    def add_graph(self):
        self.graph = self.get_graph(self.data)
        self.add(self.graph)

    def add_x_labels(self):
        self.x_labels = VGroup()
        self.x_ticks = VGroup()
        self.add(self.x_ticks, self.x_labels)

    def get_graph(self, data):
        axes = self.axes
        i_points = []
        s_points = []
        for x, props in zip(np.linspace(0, 1, len(data)), data):
            i_point = axes.c2p(x, props[1])
            s_point = axes.c2p(x, sum(props[:2]))
            i_points.append(i_point)
            s_points.append(s_point)

        r_points = [
            axes.c2p(0, 1),
            axes.c2p(1, 1),
            *s_points[::-1],
            axes.c2p(0, 1),
        ]
        s_points.extend([
            *i_points[::-1],
            s_points[0],
        ])
        i_points.extend([
            axes.c2p(1, 0),
            axes.c2p(0, 0),
            i_points[0],
        ])

        points_lists = [s_points, i_points, r_points]
        regions = VGroup(VMobject(), VMobject(), VMobject())

        for region, status, points in zip(regions, "SIR", points_lists):
            region.set_points_as_corners(points)
            region.set_stroke(width=0)
            region.set_fill(self.color_map[status], 1)
        regions[0].set_fill(opacity=0.5)

        return regions

    def update_graph(self):
        if (self.time - self.last_update_time) > self.update_frequency:
            self.data.append(self.simulation.get_status_proportions())
            self.graph.become(self.get_graph(self.data))
            self.last_update_time = self.time

    def update_x_labels(self):
        tick_height = 0.03 * self.graph.get_height()
        tick_template = Line(DOWN, UP)
        tick_template.set_height(tick_height)

        def get_tick(x):
            tick = tick_template.copy()
            tick.move_to(self.axes.c2p(x / self.time, 0))
            return tick

        def get_label(x, tick):
            label = Integer(x)
            label.set_height(tick_height)
            label.next_to(tick, DOWN, buff=0.5 * tick_height)
            return label

        self.x_labels.set_submobjects([])
        self.x_ticks.set_submobjects([])

        if self.time < 15:
            tick_range = range(1, int(self.time) + 1)
        elif self.time < 50:
            tick_range = range(5, int(self.time) + 1, 5)
        elif self.time < 100:
            tick_range = range(10, int(self.time) + 1, 10)

        for x in tick_range:
            tick = get_tick(x)
            label = get_label(x, tick)
            self.x_ticks.add(tick)
            self.x_labels.add(label)

        if 10 < self.time < 15:
            alpha = (self.time - 10) / 5
            for tick, label in zip(self.x_ticks, self.x_labels):
                if label.get_value() % 5 != 0:
                    label.set_opacity(1 - alpha)
                    tick.set_opacity(1 - alpha)


class GraphBraces(VGroup):
    CONFIG = {
        "update_frequency": 0.5,
    }

    def __init__(self, graph, simulation, **kwargs):
        super().__init__(**kwargs)
        axes = self.axes = graph.axes
        self.simulation = simulation

        ys = np.linspace(0, 1, 4)
        self.lines = VGroup(*[
            Line(axes.c2p(1, y1), axes.c2p(1, y2))
            for y1, y2 in zip(ys, ys[1:])
        ])
        self.braces = VGroup(*[Brace(line, RIGHT) for line in self.lines])
        self.labels = VGroup(
            TextMobject("Susceptible", color=COLOR_MAP["S"]),
            TextMobject("Infectious", color=COLOR_MAP["I"]),
            TextMobject("Recovered", color=COLOR_MAP["R"]),
        )

        self.max_label_height = graph.get_height() * 0.05

        self.add(self.braces, self.labels)

        self.time = 0
        self.last_update_time = 0
        self.add_updater(update_time)
        self.add_updater(lambda m: m.update_braces())

    def update_braces(self):
        if (self.time - self.last_update_time) <= self.update_frequency:
            return

        self.last_update_time = self.time
        lines = self.lines
        braces = self.braces
        labels = self.labels
        axes = self.axes

        props = self.simulation.get_status_proportions()
        ys = np.cumsum([0, props[1], props[0], props[2]])

        epsilon = 1e-6
        for i, y1, y2 in zip([1, 0, 2], ys, ys[1:]):
            lines[i].set_points_as_corners([
                axes.c2p(1, y1),
                axes.c2p(1, y2),
            ])
            height = lines[i].get_height()

            braces[i].set_height(
                max(height, epsilon),
                stretch=True
            )
            braces[i].next_to(lines[i], RIGHT)
            label_height = clip(height, epsilon, self.max_label_height)
            labels[i].scale(label_height / labels[i][0][0].get_height())
            labels[i].next_to(braces[i], RIGHT)
        return self


class ValueSlider(NumberLine):
    CONFIG = {
        "x_min": 0,
        "x_max": 1,
        "tick_frequency": 0.1,
        "numbers_with_elongated_ticks": [],
        "numbers_to_show": np.linspace(0, 1, 6),
        "decimal_number_config": {
            "num_decimal_places": 1,
        },
        "stroke_width": 5,
        "width": 8,
        "marker_color": BLUE,
    }

    def __init__(self, name, value, **kwargs):
        super().__init__(**kwargs)
        self.set_width(self.width, stretch=True)
        self.add_numbers()

        self.marker = ArrowTip(start_angle=-90 * DEGREES)
        self.marker.move_to(self.n2p(value), DOWN)
        self.marker.set_color(self.marker_color)
        self.add(self.marker)

        self.label = DecimalNumber(value)
        self.label.next_to(self.marker, UP)
        self.add(self.label)

        self.name = TextMobject(name)
        self.name.scale(1.25)
        self.name.next_to(self, DOWN)
        self.name.match_color(self.marker)
        self.add(self.name)

    def get_change_anim(self, new_value, **kwargs):
        start_value = self.label.get_value()
        m2l = self.label.get_center() - self.marker.get_center()

        def update(mob, alpha):
            interim_value = interpolate(start_value, new_value, alpha)
            mob.marker.move_to(mob.n2p(interim_value), DOWN)
            mob.label.move_to(mob.marker.get_center() + m2l)
            mob.label.set_value(interim_value)

        return UpdateFromAlphaFunc(self, update, **kwargs)


# Scenes

class RunSimpleSimulation(Scene):
    CONFIG = {
        "simulation_config": {
            "person_type": PiPerson,
            "n_cities": 1,
            "city_population": 100,
            "person_config": {
                "infection_radius": 0.75,
                "social_distance_factor": 0,
                "gravity_strength": 0.2,
                "max_speed": 0.5,
            },
            "travel_rate": 0,
            "infection_time": 5,
        },
        "graph_config": {
            "update_frequency": 0.25,
        },
        "graph_height_to_frame_height": 0.5,
        "graph_width_to_frame_height": 0.75,
        "include_graph_braces": True,
    }

    def setup(self):
        self.add_simulation()
        self.position_camera()
        self.add_graph()
        self.add_sliders()

    def construct(self):
        for x in range(5):
            self.wait(5)

    def add_simulation(self):
        self.simulation = SIRSimulation(**self.simulation_config)
        self.add(self.simulation)

    def position_camera(self):
        frame = self.camera.frame
        boxes = self.simulation.boxes
        min_height = boxes.get_height() + 1
        min_width = 3 * boxes.get_width()
        if frame.get_height() < min_height:
            frame.set_height(min_height)
        if frame.get_width() < min_width:
            frame.set_width(min_width)

        frame.next_to(boxes.get_right(), LEFT, buff=-0.1 * boxes.get_width())

    def add_graph(self):
        frame = self.camera.frame
        frame_height = frame.get_height()
        graph = SIRGraph(
            self.simulation,
            height=self.graph_height_to_frame_height * frame_height,
            width=self.graph_width_to_frame_height * frame_height,
            **self.graph_config,
        )
        graph.move_to(frame, UL)
        graph.shift(0.05 * DR * frame_height)
        self.add(graph)
        self.graph = graph

        if self.include_graph_braces:
            self.graph_braces = GraphBraces(
                graph,
                self.simulation,
                update_frequency=graph.update_frequency
            )
            self.add(self.graph_braces)

    def add_sliders(self):
        pass


class RunSimpleSimulationWithDots(RunSimpleSimulation):
    CONFIG = {
        "person_type": DotPerson,
    }


class SimpleSocialDistancing(RunSimpleSimulation):
    CONFIG = {
        "simulation_config": {
            "person_type": PiPerson,
            "n_cities": 1,
            "city_population": 100,
            "person_config": {
                "infection_radius": 0.75,
                "social_distance_factor": 2,
                "gravity_strength": 0.1,
            },
            "travel_rate": 0,
            "infection_time": 5,
        },
    }

    def construct(self):
        for x in range(5):
            self.wait(5)


class SimpleTravel(RunSimpleSimulation):
    CONFIG = {
        "simulation_config": {
            "person_type": DotPerson,
            "n_cities": 12,
            "city_population": 100,
            "person_config": {
                "infection_radius": 0.75,
                "social_distance_factor": 0,
                "gravity_strength": 0.5,
            },
            "travel_rate": 0.02,
            "infection_time": 5,
        },
    }

    def construct(self):
        for x in range(10):
            self.wait(5)

    def add_sliders(self):
        slider = ValueSlider(
            "Travel rate",
            self.simulation.travel_rate,
            x_min=0,
            x_max=0.1,
            tick_frequency=0.01,
            numbers_with_elongated_ticks=[],
            numbers_to_show=np.linspace(0, 0.1, 6),
            decimal_number_config={
                "num_decimal_places": 2,
            }
        )
        slider.match_width(self.graph)
        slider.next_to(self.graph, DOWN, buff=5)
        self.add(slider)
        self.slider = slider
