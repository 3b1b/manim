from big_ol_pile_of_manim_imports import *


DEFAULT_SCALAR_FIELD_COLORS = [BLUE_E, WHITE, RED]


# Helper functions
def get_flow_start_points(x_min=-8, x_max=8,
                          y_min=-5, y_max=5,
                          delta_x=0.5, delta_y=0.5,
                          n_repeats=1,
                          noise_factor=0.01
                          ):
    return np.array([
        x * RIGHT + y * UP + noise_factor * np.random.random(3)
        for n in xrange(n_repeats)
        for x in np.arange(x_min, x_max + delta_x, delta_x)
        for y in np.arange(y_min, y_max + delta_y, delta_y)
    ])


def joukowsky_map(z):
    return z + fdiv(1, z)


def inverse_joukowsky_map(w):
    u = 1 if w.real >= 0 else -1
    return (w + u * np.sqrt(w**2 - 4)) / 2


def derivative(func, dt=1e-7):
    return lambda z: (func(z + dt) - func(z)) / dt


def cylinder_flow_vector_field(point, R=1, U=1):
    z = R3_to_complex(point)
    # return complex_to_R3(1.0 / derivative(joukowsky_map)(z))
    return complex_to_R3(derivative(joukowsky_map)(z).conjugate())


def cylinder_flow_magnitude_field(point):
    return np.linalg.norm(cylinder_flow_vector_field(point))


def get_colored_background_image(scalar_field_func,
                                 number_to_rgb_func,
                                 pixel_height=DEFAULT_PIXEL_HEIGHT,
                                 pixel_width=DEFAULT_PIXEL_WIDTH,
                                 ):
    ph = pixel_height
    pw = pixel_width
    fw = FRAME_WIDTH
    fh = FRAME_HEIGHT
    points_array = np.zeros((ph, pw, 3))
    x_array = np.linspace(-fw / 2, fw / 2, ph).repeat(pw).reshape((ph, pw))
    y_array = np.linspace(fh / 2, -fh / 2, pw).repeat(ph).reshape((pw, ph)).T
    points_array[:, :, 0] = x_array
    points_array[:, :, 1] = y_array
    scalars = np.apply_along_axis(scalar_field_func, 2, points_array)
    rgb_array = number_to_rgb_func(scalars.flatten()).reshape((ph, pw, 3))
    return Image.fromarray((rgb_array * 255).astype('uint8'))


def get_rgb_gradient_function(min_value=0, max_value=1, colors=[BLUE, RED]):
    rgbs = np.array(map(color_to_rgb, colors))

    def func(values):
        alphas = inverse_interpolate(min_value, max_value, values)
        alphas = np.clip(alphas, 0, 1)
        alphas = 1 - alphas  # Why?
        scaled_alphas = alphas * (len(rgbs) - 1)
        indices = scaled_alphas.astype(int)
        next_indices = np.clip(indices + 1, 0, len(rgbs) - 1)
        inter_alphas = scaled_alphas % 1
        inter_alphas = inter_alphas.repeat(3).reshape((len(indices), 3))
        result = interpolate(rgbs[indices], rgbs[next_indices], inter_alphas)
        return result

    return func


def get_color_field_image_file(scalar_func,
                               min_value=0, max_value=2,
                               colors=DEFAULT_SCALAR_FIELD_COLORS
                               ):
    # try_hash
    np.random.seed(0)
    sample_inputs = 5 * np.random.random(size=(10, 3)) - 10
    sample_outputs = np.apply_along_axis(scalar_func, 1, sample_inputs)
    func_hash = hash(
        str(min_value) + str(max_value) + str(colors) + str(sample_outputs)
    )
    file_name = "%d.png" % func_hash
    full_path = os.path.join(RASTER_IMAGE_DIR, file_name)
    if not os.path.exists(full_path):
        print "Rendering color field image " + str(func_hash)
        rgb_gradient_func = get_rgb_gradient_function(
            min_value=min_value,
            max_value=max_value,
            colors=colors
        )
        image = get_colored_background_image(scalar_func, rgb_gradient_func)
        image.save(full_path)
    return full_path


# Continual animations


class VectorFieldFlow(ContinualAnimation):
    CONFIG = {
        "mode": None,
    }

    def __init__(self, mobject, func, **kwargs):
        """
        Func should take in a vector in R3, and output a vector in R3
        """
        self.func = func
        ContinualAnimation.__init__(self, mobject, **kwargs)

    def update_mobject(self, dt):
        self.apply_nudge(dt)

    def apply_nudge(self):
        self.mobject.shift(self.func(self.mobject.get_center()) * dt)


class VectorFieldSubmobjectFlow(VectorFieldFlow):
    def apply_nudge(self, dt):
        for submob in self.mobject:
            submob.shift(self.func(submob.get_center()) * dt)


class VectorFieldPointFlow(VectorFieldFlow):
    def apply_nudge(self, dt):
        self.mobject.apply_function(
            lambda p: p + self.func(p) * dt
        )


class StreamLines(VGroup):
    CONFIG = {
        "start_points_generator": get_flow_start_points,
        "dt": 0.05,
        "virtual_time": 15,
        "n_anchors_per_line": 40,
        "stroke_width": 1,
        "stroke_color": WHITE,
        "color_lines_by_magnitude": True,
        "min_magnitude": 0.5,
        "max_magnitude": 1.5,
        "colors": DEFAULT_SCALAR_FIELD_COLORS,
    }

    def __init__(self, func, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.func = func
        dt = self.dt

        start_points = self.start_points_generator()
        for point in start_points:
            points = [point]
            for t in np.arange(0, self.virtual_time, dt):
                last_point = points[-1]
                points.append(last_point + dt * func(last_point))
            line = VMobject()
            line.set_points_smoothly(
                points[::(len(points) / self.n_anchors_per_line)]
            )
            self.add(line)

        self.set_stroke(self.stroke_color, self.stroke_width)

        if self.color_lines_by_magnitude:
            image_file = get_color_field_image_file(
                lambda p: np.linalg.norm(func(p)),
                min_value=self.min_magnitude,
                max_value=self.max_magnitude,
                colors=self.colors,
            )
            self.color_using_background_image(image_file)


class ShowPassingFlashWithThinningStrokeWidth(AnimationGroup):
    CONFIG = {
        "n_segments": 10,
        "time_width": 0.1,
        "remover": True
    }

    def __init__(self, vmobject, **kwargs):
        digest_config(self, kwargs)
        max_stroke_width = vmobject.get_stroke_width()
        max_time_width = kwargs.pop("time_width", self.time_width)
        AnimationGroup.__init__(self, *[
            ShowPassingFlash(
                vmobject.deepcopy().set_stroke(width=stroke_width),
                time_width=time_width,
                **kwargs
            )
            for stroke_width, time_width in zip(
                np.linspace(0, max_stroke_width, self.n_segments),
                np.linspace(max_time_width, 0, self.n_segments)
            )
        ])


class StreamLineAnimation(ContinualAnimation):
    CONFIG = {
        "lag_range": 4,
        "line_anim_class": ShowPassingFlashWithThinningStrokeWidth,
        "line_anim_config": {
            "run_time": 4,
            "rate_func": None,
            "time_width": 0.3,
        },
    }

    def __init__(self, stream_lines, **kwargs):
        digest_config(self, kwargs)
        self.stream_lines = stream_lines
        group = VGroup()
        for line in stream_lines:
            line.anim = self.line_anim_class(line, **self.line_anim_config)
            line.time = -self.lag_range * random.random()
            group.add(line.anim.mobject)
        ContinualAnimation.__init__(self, group, **kwargs)

    def update_mobject(self, dt):
        stream_lines = self.stream_lines
        for line in stream_lines:
            line.time += dt
            adjusted_time = max(line.time, 0) % line.anim.run_time
            line.anim.update(adjusted_time / line.anim.run_time)

# Scenes


class TestVectorField(Scene):
    CONFIG = {
        "func": cylinder_flow_vector_field,
        "flow_time": 15,
    }

    def construct(self):
        plane = ComplexPlane()
        self.add(plane)

        circle = Circle(stroke_color=YELLOW)
        circle.set_fill(BLACK, 1)
        self.add_foreground_mobject(circle)

        lines = StreamLines(
            self.func,
            start_points_generator=lambda: get_flow_start_points(
                x_min=-8, x_max=-7, y_min=-4, y_max=4,
                delta_x=0.5,
                delta_y=0.1,
                n_repeats=1,
                noise_factor=0.1,
            ),
            stroke_width=2,
        )
        # self.add(lines)
        # self.play(ShowPassingFlashWithThinningStrokeWidth(lines[5], run_time=4))
        # return
        stream_line_animation = StreamLineAnimation(lines)
        self.add(stream_line_animation)
        self.wait(self.flow_time)
        # self.play(VFadeOut(lines))
        # self.remove(stream_line_animation)
        # self.wait()

        # dots = VGroup(*[
        #     Dot().move_to(start_point)
        #     for start_point in get_flow_start_points()
        # ])
        # dots.set_color_by_gradient(YELLOW, RED)
        # self.add(dots)

        # self.add(VectorFieldSubmobjectFlow(dots, self.func))
        # self.wait(5)


class Introduction(Scene):
    CONFIG = {
        "production_quality_flow": True,
    }

    def construct(self):
        self.add_plane()
        self.add_title()
        self.show_numbers()
        self.show_contour_lines()
        self.show_flow()
        self.apply_joukowsky_map()

    def add_plane(self):
        self.plane = ComplexPlane()
        self.plane.add_coordinates()
        self.plane.coordinate_labels.submobjects.pop(-1)
        self.add(self.plane)

    def add_title(self):
        title = TextMobject("Complex Plane")
        title.to_edge(UP, buff=MED_SMALL_BUFF)
        title.add_background_rectangle()
        self.title = title
        self.add(title)

    def show_numbers(self):
        run_time = 5

        unit_circle = self.unit_circle = Circle(
            radius=self.plane.unit_size,
            fill_color=BLACK,
            fill_opacity=0,
            stroke_color=YELLOW
        )
        dot = Dot()
        dot_update = UpdateFromFunc(
            dot, lambda d: d.move_to(unit_circle.point_from_proportion(1))
        )
        exp_tex = TexMobject("e^{", "0.00", "i}")
        zero = exp_tex.get_part_by_tex("0.00")
        zero.fade(1)
        exp_tex_update = UpdateFromFunc(
            exp_tex, lambda et: et.next_to(dot, UR, SMALL_BUFF)
        )
        exp_decimal = DecimalNumber(
            0, num_decimal_places=2,
            include_background_rectangle=True,
            color=YELLOW
        )
        exp_decimal.replace(zero)
        exp_decimal_update = ChangeDecimalToValue(
            exp_decimal, TAU,
            position_update_func=lambda mob: mob.move_to(zero),
            run_time=run_time,
        )

        sample_numbers = [
            complex(-5, 2),
            complex(2, 2),
            complex(3, 1),
            complex(-5, -2),
            complex(-4, 1),
        ]
        sample_labels = VGroup()
        for z in sample_numbers:
            sample_dot = Dot(self.plane.number_to_point(z))
            sample_label = DecimalNumber(
                z,
                num_decimal_places=0,
                include_background_rectangle=True,
            )
            sample_label.next_to(sample_dot, UR, SMALL_BUFF)
            sample_labels.add(VGroup(sample_dot, sample_label))

        self.play(
            ShowCreation(unit_circle, run_time=run_time),
            VFadeIn(exp_tex),
            UpdateFromAlphaFunc(
                exp_decimal,
                lambda ed, a: ed.set_fill(opacity=a)
            ),
            dot_update,
            exp_tex_update,
            exp_decimal_update,
            LaggedStart(
                FadeIn, sample_labels,
                remover=True,
                rate_func=there_and_back,
                run_time=run_time,
            )
        )
        self.play(
            FadeOut(exp_tex),
            FadeOut(exp_decimal),
            FadeOut(dot),
            unit_circle.set_fill, BLACK, {"opacity": 1},
        )
        self.wait()

    def show_contour_lines(self):
        warped_grid = self.warped_grid = self.get_warpable_grid()
        h_line = Line(3 * LEFT, 3 * RIGHT, color=WHITE)  # Hack

        func_label = self.func_label = TexMobject("f(z) = z + 1 / z")
        func_label.add_background_rectangle()
        func_label.next_to(self.title, DOWN, MED_SMALL_BUFF)

        self.remove(self.plane)
        self.add_foreground_mobjects(self.unit_circle, self.title)
        self.play(
            warped_grid.apply_complex_function, inverse_joukowsky_map,
            Animation(h_line, remover=True)
        )
        self.play(Write(func_label))
        self.add_foreground_mobjects(func_label)
        self.wait()

    def show_flow(self):
        stream_lines = self.get_stream_lines()
        stream_lines_copy = stream_lines.copy()
        stream_lines_copy.set_stroke(YELLOW, 1)
        stream_lines_animation = self.get_stream_lines_animation(
            stream_lines
        )

        tiny_buff = 0.0001
        v_lines = VGroup(*[
            Line(
                UP, ORIGIN,
                path_arc=0,
                n_arc_anchors=20,
            ).shift(x * RIGHT)
            for x in np.linspace(0, 1, 5)
        ])
        v_lines.match_background_image_file(stream_lines)
        fast_lines, slow_lines = [
            VGroup(*[
                v_lines.copy().next_to(point, vect, tiny_buff)
                for point, vect in it.product(h_points, [UP, DOWN])
            ])
            for h_points in [
                [0.5 * LEFT, 0.5 * RIGHT],
                [2 * LEFT, 2 * RIGHT],
            ]
        ]
        for lines in fast_lines, slow_lines:
            lines.apply_complex_function(inverse_joukowsky_map)

        self.add(stream_lines_animation)
        self.wait(7)
        self.play(
            ShowCreationThenDestruction(
                stream_lines_copy,
                submobject_mode="all_at_once",
                run_time=3,
            )
        )
        self.wait()
        self.play(ShowCreation(fast_lines))
        self.wait(2)
        self.play(ReplacementTransform(fast_lines, slow_lines))
        self.wait(3)
        self.play(
            FadeOut(slow_lines),
            VFadeOut(stream_lines_animation.mobject)
        )
        self.remove(stream_lines_animation)

    def apply_joukowsky_map(self):
        shift_val = 0.1 * LEFT + 0.2 * UP
        scale_factor = np.linalg.norm(RIGHT - shift_val)
        movers = VGroup(self.warped_grid, self.unit_circle)
        self.unit_circle.insert_n_anchor_points(50)

        stream_lines = self.get_stream_lines()
        stream_lines.scale(scale_factor)
        stream_lines.shift(shift_val)
        stream_lines.apply_complex_function(joukowsky_map)

        self.play(
            movers.scale, scale_factor,
            movers.shift, shift_val,
        )
        self.wait()
        self.play(
            movers.apply_complex_function, joukowsky_map,
            CircleThenFadeAround(self.func_label),
            run_time=2
        )
        self.add(self.get_stream_lines_animation(stream_lines))
        self.wait(20)

    # Helpers

    def get_warpable_grid(self):
        top_grid = NumberPlane()
        top_grid.prepare_for_nonlinear_transform()
        bottom_grid = top_grid.copy()
        tiny_buff = 0.0001
        top_grid.next_to(ORIGIN, UP, buff=tiny_buff)
        bottom_grid.next_to(ORIGIN, DOWN, buff=tiny_buff)
        result = VGroup(top_grid, bottom_grid)
        result.add(*[
            Line(
                ORIGIN, FRAME_WIDTH * RIGHT / 2,
                color=WHITE,
                path_arc=0,
                n_arc_anchors=100,
            ).next_to(ORIGIN, vect, buff=2)
            for vect in LEFT, RIGHT
        ])
        return result

    def get_stream_lines(self):
        func = cylinder_flow_vector_field
        if self.production_quality_flow:
            delta_x = 0.5
            delta_y = 0.1
        else:
            delta_x = 1
            # delta_y = 1
            delta_y = 0.1
        return StreamLines(
            func,
            start_points_generator=lambda: get_flow_start_points(
                x_min=-8, x_max=-7, y_min=-4, y_max=4,
                delta_x=delta_x,
                delta_y=delta_y,
                n_repeats=1,
                noise_factor=0.1,
            ),
            stroke_width=2,
        )

    def get_stream_lines_animation(self, stream_lines):
        if self.production_quality_flow:
            line_anim_class = ShowPassingFlashWithThinningStrokeWidth
        else:
            line_anim_class = ShowPassingFlash
        return StreamLineAnimation(
            stream_lines,
            line_anim_class=line_anim_class,
        )
