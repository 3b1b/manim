from big_ol_pile_of_manim_imports import *

DEFAULT_SCALAR_FIELD_COLORS = [BLUE_E, WHITE, RED]

# Quick note to anyone coming to this file with the
# intent of recreating animations from the video.  Some
# of these, espeically those involving StreamLineAnimation,
# can take an extremely long time to run, but much of the
# computational cost is just for giving subtle little effects
# which don't matter too much.  Switching the line_anim_class
# to ShowPassingFlash will give significant speedups, as will
# increasing the values of delta_x and delta_y in sampling for
# the streamlines.  Certainly while developing, things were not
# run at production quality.


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
    if z == 0:
        return 0
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


def get_rgb_gradient_function(min_value=0, max_value=1,
                              colors=[BLUE, RED],
                              flip_alphas=True,  # Why?
                              ):
    rgbs = np.array(map(color_to_rgb, colors))

    def func(values):
        alphas = inverse_interpolate(min_value, max_value, values)
        alphas = np.clip(alphas, 0, 1)
        if flip_alphas:
            alphas = 1 - alphas
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


def vec_tex(s):
    return "\\vec{\\textbf{%s}}" % s


def four_swirls_function(point):
    x, y = point[:2]
    result = (y**3 - 4 * y) * RIGHT + (x**3 - 16 * x) * UP
    result *= 0.05
    norm = np.linalg.norm(result)
    if norm == 0:
        return result
    # result *= 2 * sigmoid(norm) / norm
    return result


def get_force_field_func(*point_strength_pairs):
    def func(point):
        result = np.array(ORIGIN)
        for center, strength in point_strength_pairs:
            to_center = center - point
            norm = np.linalg.norm(to_center)
            if norm == 0:
                continue
            to_center /= norm**3
            to_center *= strength
            result += to_center
        return result
    return func


def get_chraged_particle(color, sign, radius=0.1):
    result = Circle(
        stroke_color=WHITE,
        stroke_width=0.5,
        fill_color=color,
        fill_opacity=0.8,
        radius=radius
    )
    sign = TexMobject(sign)
    sign.set_stroke(WHITE, 1)
    sign.scale_to_fit_width(0.5 * result.get_width())
    sign.move_to(result)
    result.add(sign)
    return result


def get_proton(radius=0.1):
    return get_chraged_particle(RED, "+", radius)


def get_electron(radius=0.05):
    return get_chraged_particle(BLUE, "-", radius)


# Mobjects


class StreamLines(VGroup):
    CONFIG = {
        "start_points_generator": get_flow_start_points,
        "start_points_generator_config": {},
        "dt": 0.05,
        "virtual_time": 15,
        "n_anchors_per_line": 40,
        "stroke_width": 1,
        "stroke_color": WHITE,
        "color_lines_by_magnitude": True,
        "min_magnitude": 0.5,
        "max_magnitude": 1.5,
        "colors": DEFAULT_SCALAR_FIELD_COLORS,
        "cutoff_norm": 15,
    }

    def __init__(self, func, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.func = func
        dt = self.dt

        start_points = self.start_points_generator(
            **self.start_points_generator_config
        )
        for point in start_points:
            points = [point]
            for t in np.arange(0, self.virtual_time, dt):
                last_point = points[-1]
                points.append(last_point + dt * func(last_point))
                if np.linalg.norm(last_point) > self.cutoff_norm:
                    break
            line = VMobject()
            step = max(1, len(points) / self.n_anchors_per_line)
            line.set_points_smoothly(points[::step])
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


class VectorField(VGroup):
    CONFIG = {
        "delta_x": 0.5,
        "delta_y": 0.5,
        "x_min": int(np.floor(-FRAME_WIDTH / 2)),
        "x_max": int(np.ceil(FRAME_WIDTH / 2)),
        "y_min": int(np.floor(-FRAME_HEIGHT / 2)),
        "y_max": int(np.ceil(FRAME_HEIGHT / 2)),
        "min_magnitude": 0,
        "max_magnitude": 2,
        "colors": DEFAULT_SCALAR_FIELD_COLORS,
        # Takes in actual norm, spits out displayed norm
        "length_func": lambda norm: 0.5 * sigmoid(norm),
        "stroke_color": BLACK,
        "stroke_width": 0.5,
    }

    def __init__(self, func, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.func = func

        rgb_gradient_function = get_rgb_gradient_function(
            self.min_magnitude,
            self.max_magnitude,
            self.colors,
            flip_alphas=False
        )
        for x in np.arange(self.x_min, self.x_max, self.delta_x):
            for y in np.arange(self.y_min, self.y_max, self.delta_y):
                point = x * RIGHT + y * UP
                output = np.array(func(point))
                norm = np.linalg.norm(output)
                if norm == 0:
                    output *= 0
                else:
                    output *= self.length_func(norm) / norm
                # new_norm = np.linalg.norm(output)
                vect = Vector(output)
                vect.shift(point)
                vect.set_fill(rgb_to_color(
                    rgb_gradient_function(np.array([norm]))[0]
                ))
                vect.set_stroke(
                    self.stroke_color,
                    self.stroke_width
                )
                self.add(vect)

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


# TODO: Make it so that you can have a group of streamlines
# varying in response to a changing vector field, and still
# animate the resulting flow
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


class JigglingSubmobjects(ContinualAnimation):
    CONFIG = {
        "amplitude": 0.05,
        "jiggles_per_second": 1,
    }

    def __init__(self, group, **kwargs):
        for submob in group.submobjects:
            submob.jiggling_direction = rotate_vector(
                RIGHT, np.random.random() * TAU,
            )
            submob.jiggling_phase = np.random.random() * TAU
        ContinualAnimation.__init__(self, group, **kwargs)

    def update_mobject(self, dt):
        for submob in self.mobject.submobjects:
            submob.jiggling_phase += dt * self.jiggles_per_second * TAU
            submob.shift(
                self.amplitude *
                submob.jiggling_direction *
                np.sin(submob.jiggling_phase) * dt
            )

# Scenes


class TestVectorField(Scene):
    CONFIG = {
        "func": cylinder_flow_vector_field,
        "flow_time": 15,
    }

    def construct(self):
        vector_field = VectorField(
            lambda p: rotate_vector(cylinder_flow_vector_field(p), TAU / 4)
        )
        vector_field.remove(*filter(
            lambda v: np.linalg.norm(v.get_start()) <= 1,
            vector_field
        ))

        self.add(vector_field)


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
        func_label = self.get_func_label()

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

    def get_func_label(self):
        func_label = self.func_label = TexMobject("f(z) = z + 1 / z")
        func_label.add_background_rectangle()
        func_label.next_to(self.title, DOWN, MED_SMALL_BUFF)
        return func_label

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
        # This line is a bit of a hack
        h_line = Line(LEFT, RIGHT, color=WHITE)
        h_line.set_points([LEFT, LEFT, RIGHT, RIGHT])
        h_line.scale(2)
        result.add(h_line)
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
            start_points_generator_config={
                "x_min": -8,
                "x_max": -7,
                "y_min": -4,
                "y_max": 4,
                "delta_x": delta_x,
                "delta_y": delta_y,
                "n_repeats": 1,
                "noise_factor": 0.1,
            },
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


class ElectricField(Introduction, MovingCameraScene):
    def construct(self):
        self.add_plane()
        self.add_title()
        self.setup_warped_grid()
        self.show_uniform_field()
        self.show_moving_charges()
        self.show_field_lines()

    def setup_warped_grid(self):
        warped_grid = self.warped_grid = self.get_warpable_grid()
        warped_grid.save_state()
        func_label = self.get_func_label()
        unit_circle = self.unit_circle = Circle(
            radius=self.plane.unit_size,
            stroke_color=YELLOW,
            fill_color=BLACK,
            fill_opacity=1
        )

        self.add_foreground_mobjects(self.title, func_label, unit_circle)
        self.remove(self.plane)
        self.play(
            warped_grid.apply_complex_function, inverse_joukowsky_map,
        )
        self.wait()

    def show_uniform_field(self):
        vector_field = self.vector_field = VectorField(
            lambda p: UP,
            colors=[BLUE_E, WHITE, RED]
        )
        protons, electrons = groups = [
            VGroup(*[method(radius=0.2) for x in range(20)])
            for method in get_proton, get_electron
        ]
        for group in groups:
            group.arrange_submobjects(RIGHT, buff=MED_SMALL_BUFF)
            random.shuffle(group.submobjects)
        protons.next_to(FRAME_HEIGHT * DOWN / 2, DOWN)
        electrons.next_to(FRAME_HEIGHT * UP / 2, UP)

        self.play(
            self.warped_grid.restore,
            FadeOut(self.unit_circle),
            FadeOut(self.title),
            FadeOut(self.func_label),
            LaggedStart(GrowArrow, vector_field)
        )
        self.remove_foreground_mobjects(self.title, self.func_label)
        self.wait()
        for group, vect in (protons, UP), (electrons, DOWN):
            self.play(LaggedStart(
                ApplyMethod, group,
                lambda m: (m.shift, (FRAME_HEIGHT + 1) * vect),
                run_time=3,
                rate_func=rush_into
            ))

    def show_moving_charges(self):
        unit_circle = self.unit_circle

        protons = VGroup(*[
            get_proton().move_to(
                rotate_vector(0.275 * n * RIGHT, angle)
            )
            for n in range(4)
            for angle in np.arange(
                0, TAU, TAU / (6 * n) if n > 0 else TAU
            )
        ])
        jiggling_protons = JigglingSubmobjects(protons)
        electrons = VGroup(*[
            get_electron().move_to(
                proton.get_center() +
                proton.radius * rotate_vector(RIGHT, angle)
            )
            for proton in protons
            for angle in [np.random.random() * TAU]
        ])
        jiggling_electrons = JigglingSubmobjects(electrons)
        electrons.generate_target()
        for electron in electrons.target:
            y_part = electron.get_center()[1]
            if y_part > 0:
                electron.shift(2 * y_part * DOWN)

        # New vector field
        def new_electric_field(point):
            if np.linalg.norm(point) < 1:
                return ORIGIN
            vect = cylinder_flow_vector_field(point)
            return rotate_vector(vect, 90 * DEGREES)
        new_vector_field = VectorField(
            new_electric_field,
            colors=self.vector_field.colors
        )

        warped_grid = self.warped_grid

        self.play(GrowFromCenter(unit_circle))
        self.add(jiggling_protons, jiggling_electrons)
        self.add_foreground_mobjects(
            self.vector_field, unit_circle, protons, electrons
        )
        self.play(
            LaggedStart(VFadeIn, protons),
            LaggedStart(VFadeIn, electrons),
        )
        self.play(
            self.camera.frame.scale, 0.7,
            run_time=3
        )
        self.play(
            MoveToTarget(electrons),  # More indication?
            warped_grid.apply_complex_function, inverse_joukowsky_map,
            Transform(
                self.vector_field,
                new_vector_field
            ),
            run_time=3
        )
        self.wait(5)

    def show_field_lines(self):
        h_lines = VGroup(*[
            Line(
                5 * LEFT, 5 * RIGHT,
                path_arc=0,
                n_arc_anchors=50,
                stroke_color=LIGHT_GREY,
                stroke_width=2,
            ).shift(y * UP)
            for y in np.arange(-3, 3.25, 0.25)
            if y != 0
        ])
        h_lines.apply_complex_function(inverse_joukowsky_map)

        self.play(ShowCreation(
            h_lines,
            run_time=2,
            submobject_mode="all_at_once"
        ))
        for x in range(4):
            self.play(LaggedStart(
                ApplyMethod, h_lines,
                lambda m: (m.set_stroke, TEAL, 4),
                rate_func=there_and_back,
            ))


class AskQuestions(TeacherStudentsScene):
    def construct(self):
        div_tex = TexMobject("\\nabla \\cdot", vec_tex("v"))
        curl_tex = TexMobject("\\nabla \\times", vec_tex("v"))
        div_name = TextMobject("Divergence")
        curl_name = TextMobject("Curl")
        div = VGroup(div_name, div_tex)
        curl = VGroup(curl_name, curl_tex)
        for group in div, curl:
            group[1].set_color_by_tex(vec_tex("v"), YELLOW)
            group.arrange_submobjects(DOWN)
        topics = VGroup(div, curl)
        topics.arrange_submobjects(DOWN, buff=LARGE_BUFF)
        topics.move_to(self.hold_up_spot, DOWN)
        div.save_state()
        div.move_to(self.hold_up_spot, DOWN)
        screen = self.screen

        self.student_says(
            "What does fluid flow have \\\\ to do with electricity?",
            added_anims=[self.teacher.change, "happy"]
        )
        self.wait()
        self.student_says(
            "And you mentioned \\\\ complex numbers?",
            student_index=0,
        )
        self.wait(3)
        self.play(
            FadeInFromDown(div),
            self.teacher.change, "raise_right_hand",
            FadeOut(self.students[0].bubble),
            FadeOut(self.students[0].bubble.content),
            self.get_student_changes(*["pondering"] * 3)
        )
        self.play(
            FadeInFromDown(curl),
            div.restore
        )
        self.wait()
        self.look_at(self.screen)
        self.wait()
        self.change_all_student_modes("hooray", look_at_arg=screen)
        self.wait(3)

        topics.generate_target()
        topics.target.to_edge(LEFT, buff=LARGE_BUFF)
        arrow = TexMobject("\\leftrightarrow")
        arrow.scale(2)
        arrow.next_to(topics.target, RIGHT, buff=LARGE_BUFF)
        screen.next_to(arrow, RIGHT, LARGE_BUFF)
        complex_analysis = TextMobject("Complex analysis")
        complex_analysis.next_to(screen, UP)

        self.play(
            MoveToTarget(topics),
            self.get_student_changes(
                "confused", "sassy", "erm",
                look_at_arg=topics.target
            ),
            self.teacher.change, "pondering", screen
        )
        self.play(
            Write(arrow),
            FadeInFromDown(complex_analysis)
        )
        self.look_at(screen)
        self.wait(6)


class IntroduceVectorField(Scene):
    CONFIG = {
        "vector_field_config": {
            # "delta_x": 2,
            # "delta_y": 2,
            "delta_x": 0.5,
            "delta_y": 0.5,
        },
        "stream_line_config": {
            "start_points_generator_config": {
                # "delta_x": 1,
                # "delta_y": 1,
                "delta_x": 0.25,
                "delta_y": 0.25,
            },
            "virtual_time": 3,
        },
        "stream_line_animation_config": {
            # "line_anim_class": ShowPassingFlash,
            "line_anim_class": ShowPassingFlashWithThinningStrokeWidth,
        }
    }

    def construct(self):
        self.add_plane()
        self.add_title()
        self.points_to_vectors()
        self.show_fluid_flow()
        self.show_gravitational_force()
        self.show_magnetic_force()
        self.show_fluid_flow()

    def add_plane(self):
        plane = self.plane = NumberPlane()
        plane.add_coordinates()
        plane.remove(plane.coordinate_labels[-1])
        self.add(plane)

    def add_title(self):
        title = TextMobject("Vector field")
        title.scale(1.5)
        title.to_edge(UP, buff=MED_SMALL_BUFF)
        title.add_background_rectangle(opacity=1, buff=SMALL_BUFF)
        self.add_foreground_mobjects(title)

    def points_to_vectors(self):
        vector_field = self.vector_field = VectorField(
            four_swirls_function,
            **self.vector_field_config
        )
        dots = VGroup()
        for vector in vector_field:
            dot = Dot(radius=0.05)
            dot.move_to(vector.get_start())
            dot.target = vector
            dots.add(dot)

        self.play(LaggedStart(GrowFromCenter, dots))
        self.wait()
        self.play(LaggedStart(MoveToTarget, dots, remover=True))
        self.add(vector_field)
        self.wait()

    def show_fluid_flow(self):
        vector_field = self.vector_field
        stream_lines = StreamLines(
            vector_field.func,
            **self.stream_line_config
        )
        stream_line_animation = StreamLineAnimation(
            stream_lines,
            **self.stream_line_animation_config
        )

        self.add(stream_line_animation)
        self.play(
            vector_field.set_fill, {"opacity": 0.3}
        )
        self.wait(7)
        self.play(
            vector_field.set_fill, {"opacity": 1},
            VFadeOut(stream_line_animation.mobject),
        )
        self.remove(stream_line_animation)

    def show_gravitational_force(self):
        earth = self.earth = ImageMobject("earth")
        moon = self.moon = ImageMobject("moon", height=1)
        earth_center = 3 * RIGHT + 2 * UP
        moon_center = 3 * LEFT + DOWN
        earth.move_to(earth_center)
        moon.move_to(moon_center)

        gravity_func = get_force_field_func((earth_center, 6), (moon_center, 1))
        gravity_field = VectorField(
            gravity_func,
            **self.vector_field_config
        )

        self.add_foreground_mobjects(earth, moon)
        self.play(
            GrowFromCenter(earth),
            GrowFromCenter(moon),
            Transform(self.vector_field, gravity_field),
            run_time=2
        )
        self.vector_field.func = gravity_field.func
        self.wait()

    def show_magnetic_force(self):
        magnetic_func = get_force_field_func(
            (3 * LEFT, 1), (3 * RIGHT, - 1)
        )
        magnetic_field = VectorField(
            magnetic_func,
            **self.vector_field_config
        )
        magnet = VGroup(*[
            Rectangle(
                width=3.5,
                height=1,
                stroke_width=0,
                fill_opacity=1,
                fill_color=color
            )
            for color in BLUE, RED
        ])
        magnet.arrange_submobjects(RIGHT, buff=0)
        for char, vect in ("S", LEFT), ("N", RIGHT):
            letter = TextMobject(char)
            edge = magnet.get_edge_center(vect)
            letter.next_to(edge, -vect, buff=MED_LARGE_BUFF)
            magnet.add(letter)

        self.add_foreground_mobjects(magnet)
        self.play(
            self.earth.scale, 0,
            self.moon.scale, 0,
            DrawBorderThenFill(magnet),
            Transform(self.vector_field, magnetic_field),
            run_time=2
        )
        self.vector_field.func = magnetic_field.func
        self.remove_foreground_mobjects(self.earth, self.moon)


class QuickNoteOnDrawingThese(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Quick note on \\\\ drawing vector fields",
            bubble_kwargs={"width": 5, "height": 3},
            added_anims=[self.get_student_changes(
                "confused", "erm", "sassy"
            )]
        )
        self.look_at(self.screen)
        self.wait(3)


class ShorteningLongVectors(IntroduceVectorField):
    def construct(self):
        self.add_plane()
        self.add_title()
        self.contrast_adjusted_and_non_adjusted()

    def contrast_adjusted_and_non_adjusted(self):
        func = four_swirls_function
        unadjusted = VectorField(
            func, length_func=lambda n: n, colors=[WHITE],
        )
        adjusted = VectorField(func)
        for v1, v2 in zip(adjusted, unadjusted):
            v1.save_state()
            v1.target = v2

        self.add(adjusted)
        self.wait()
        self.play(LaggedStart(
            MoveToTarget, adjusted,
            run_time=3
        ))
        self.wait()
        self.play(LaggedStart(
            ApplyMethod, adjusted,
            lambda m: (m.restore,),
            run_time=3
        ))
        self.wait()


class TimeDependentVectorField(ExternallyAnimatedScene):
    pass


class ChangingElectricField(Scene):
    CONFIG = {
        "vector_field_config": {}
    }

    def construct(self):
        particles = self.particles = VGroup()

        for n in range(9):
            if n % 2 == 0:
                particle = get_proton(radius=0.2)
                particle.charge = +1
            else:
                particle = get_electron(radius=0.2)
                particle.charge = -1
            particle.velocity = np.array(ORIGIN)
            particles.add(particle)
            particle.shift(
                0.2 * random.random() * RIGHT +
                0.2 * random.random() * UP
            )

        particles.arrange_submobjects_in_grid(buff=LARGE_BUFF)

        vector_field = self.get_vector_field()

        def update_vector_field(vector_field):
            new_field = self.get_vector_field()
            Transform(vector_field, new_field).update(1)
            vector_field.func = new_field.func

        def update_particles(particles, dt):
            func = vector_field.func
            for particle in particles:
                force = func(particle.get_center())
                particle.velocity += force * dt
                particle.shift(particle.velocity * dt)

        self.add(
            ContinualUpdateFromFunc(vector_field, update_vector_field),
            ContinualUpdateFromTimeFunc(particles, update_particles),
        )
        self.wait(20)

    def get_vector_field(self):
        func = get_force_field_func(*zip(
            map(Mobject.get_center, self.particles),
            [p.charge for p in self.particles]
        ))
        return VectorField(func, **self.vector_field_config)
