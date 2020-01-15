
from manimlib.imports import *


# Quick note to anyone coming to this file with the
# intent of recreating animations from the video.  Some
# of these, especially those involving AnimatedStreamLines,
# can take an extremely long time to run, but much of the
# computational cost is just for giving subtle little effects
# which don't matter too much.  Switching the line_anim_class
# to ShowPassingFlash will give significant speedups, as will
# increasing the values of delta_x and delta_y in sampling for
# the stream lines.  Certainly while developing, things were not
# run at production quality.

FOX_COLOR = "#DF7F20"
RABBIT_COLOR = "#C6D6EF"


# Warning, this file uses ContinualChangingDecimal,
# which has since been been deprecated.  Use a mobject
# updater instead


# Helper functions
def joukowsky_map(z):
    if z == 0:
        return 0
    return z + fdiv(1, z)


def inverse_joukowsky_map(w):
    u = 1 if w.real >= 0 else -1
    return (w + u * np.sqrt(w**2 - 4)) / 2


def derivative(func, dt=1e-7):
    return lambda z: (func(z + dt) - func(z)) / dt


def negative_gradient(potential_func, dt=1e-7):
    def result(p):
        output = potential_func(p)
        dx = dt * RIGHT
        dy = dt * UP
        dz = dt * OUT
        return -np.array([
            (potential_func(p + dx) - output) / dt,
            (potential_func(p + dy) - output) / dt,
            (potential_func(p + dz) - output) / dt,
        ])
    return result


def divergence(vector_func, dt=1e-7):
    def result(point):
        value = vector_func(point)
        return sum([
            (vector_func(point + dt * RIGHT) - value)[i] / dt
            for i, vect in enumerate([RIGHT, UP, OUT])
        ])
    return result


def two_d_curl(vector_func, dt=1e-7):
    def result(point):
        value = vector_func(point)
        return op.add(
            (vector_func(point + dt * RIGHT) - value)[1] / dt,
            -(vector_func(point + dt * UP) - value)[0] / dt,
        )
    return result


def cylinder_flow_vector_field(point, R=1, U=1):
    z = R3_to_complex(point)
    # return complex_to_R3(1.0 / derivative(joukowsky_map)(z))
    return complex_to_R3(derivative(joukowsky_map)(z).conjugate())


def cylinder_flow_magnitude_field(point):
    return get_norm(cylinder_flow_vector_field(point))


def vec_tex(s):
    return "\\vec{\\textbf{%s}}" % s


def four_swirls_function(point):
    x, y = point[:2]
    result = (y**3 - 4 * y) * RIGHT + (x**3 - 16 * x) * UP
    result *= 0.05
    norm = get_norm(result)
    if norm == 0:
        return result
    # result *= 2 * sigmoid(norm) / norm
    return result


def get_force_field_func(*point_strength_pairs, **kwargs):
    radius = kwargs.get("radius", 0.5)

    def func(point):
        result = np.array(ORIGIN)
        for center, strength in point_strength_pairs:
            to_center = center - point
            norm = get_norm(to_center)
            if norm == 0:
                continue
            elif norm < radius:
                to_center /= radius**3
            elif norm >= radius:
                to_center /= norm**3
            to_center *= -strength
            result += to_center
        return result
    return func


def get_charged_particles(color, sign, radius=0.1):
    result = Circle(
        stroke_color=WHITE,
        stroke_width=0.5,
        fill_color=color,
        fill_opacity=0.8,
        radius=radius
    )
    sign = TexMobject(sign)
    sign.set_stroke(WHITE, 1)
    sign.set_width(0.5 * result.get_width())
    sign.move_to(result)
    result.add(sign)
    return result


def get_proton(radius=0.1):
    return get_charged_particles(RED, "+", radius)


def get_electron(radius=0.05):
    return get_charged_particles(BLUE, "-", radius)


def preditor_prey_vector_field(point):
    alpha = 30.0
    beta = 1.0
    gamma = 30.0
    delta = 1.0
    x, y = point[:2]
    result = 0.05 * np.array([
        alpha * x - beta * x * y,
        delta * x * y - gamma * y,
        0,
    ])
    return rotate(result, 1 * DEGREES)

# Mobjects

# TODO, this is untested after turning it from a
# ContinualAnimation into a VGroup
class JigglingSubmobjects(VGroup):
    CONFIG = {
        "amplitude": 0.05,
        "jiggles_per_second": 1,
    }

    def __init__(self, group, **kwargs):
        VGroup.__init__(self, **kwargs)
        for submob in group.submobjects:
            submob.jiggling_direction = rotate_vector(
                RIGHT, np.random.random() * TAU,
            )
            submob.jiggling_phase = np.random.random() * TAU
            self.add(submob)
        self.add_updater(lambda m, dt: m.update(dt))

    def update(self, dt):
        for submob in self.submobjects:
            submob.jiggling_phase += dt * self.jiggles_per_second * TAU
            submob.shift(
                self.amplitude *
                submob.jiggling_direction *
                np.sin(submob.jiggling_phase) * dt
            )

# Scenes


class Introduction(MovingCameraScene):
    CONFIG = {
        "stream_lines_config": {
            "start_points_generator_config": {
                "delta_x": 1.0 / 8,
                "delta_y": 1.0 / 8,
                "y_min": -8.5,
                "y_max": 8.5,
            }
        },
        "vector_field_config": {},
        "virtual_time": 3,
    }

    def construct(self):
        # Divergence
        def div_func(p):
            return p / 3
        div_vector_field = VectorField(
            div_func, **self.vector_field_config
        )
        stream_lines = StreamLines(
            div_func, **self.stream_lines_config
        )
        stream_lines.shuffle()
        div_title = self.get_title("Divergence")

        self.add(div_vector_field)
        self.play(
            LaggedStartMap(ShowPassingFlash, stream_lines),
            FadeIn(div_title[0]),
            *list(map(GrowFromCenter, div_title[1]))
        )

        # Curl
        def curl_func(p):
            return rotate_vector(p / 3, 90 * DEGREES)

        curl_vector_field = VectorField(
            curl_func, **self.vector_field_config
        )
        stream_lines = StreamLines(
            curl_func, **self.stream_lines_config
        )
        stream_lines.shuffle()
        curl_title = self.get_title("Curl")

        self.play(
            ReplacementTransform(div_vector_field, curl_vector_field),
            ReplacementTransform(
                div_title, curl_title,
                path_arc=90 * DEGREES
            ),
        )
        self.play(ShowPassingFlash(stream_lines, run_time=3))
        self.wait()

    def get_title(self, word):
        title = TextMobject(word)
        title.scale(2)
        title.to_edge(UP)
        title.add_background_rectangle()
        return title


class ShowWritingTrajectory(TeacherStudentsScene):
    def construct(self):
        self.add_screen()
        self.show_meandering_path()
        self.show_previous_video()

    def add_screen(self):
        self.screen.scale(1.4, about_edge=UL)
        self.add(self.screen)

    def show_meandering_path(self):
        solid_path = VMobject().set_points_smoothly([
            3 * UP + 2 * RIGHT,
            2 * UP + 4 * RIGHT,
            3.5 * UP + 3.5 * RIGHT,
            2 * UP + 3 * RIGHT,
            3 * UP + 7 * RIGHT,
            3 * UP + 5 * RIGHT,
            UP + 6 * RIGHT,
            2 * RIGHT,
            2 * UP + 2 * RIGHT,
            self.screen.get_right()
        ])
        step = 1.0 / 80
        dashed_path = VGroup(*[
            VMobject().pointwise_become_partial(
                solid_path, x, x + step / 2
            )
            for x in np.arange(0, 1 + step, step)
        ])
        arrow = Arrow(
            solid_path.points[-2],
            solid_path.points[-1],
            buff=0
        )
        dashed_path.add(arrow.tip)
        dashed_path.set_color_by_gradient(BLUE, YELLOW)

        self.play(
            ShowCreation(
                dashed_path,
                rate_func=bezier([0, 0, 1, 1]),
                run_time=5,
            ),
            self.teacher.change, "raise_right_hand",
            self.get_student_changes(*["sassy"] * 3)
        )
        self.play(
            LaggedStartMap(
                ApplyMethod, dashed_path,
                lambda m: (m.scale, 0),
                remover=True
            ),
            self.teacher.change, "tease",
            self.get_student_changes(
                *["pondering"] * 3,
                look_at_arg=self.screen
            )
        )

    def show_previous_video(self):
        screen = self.screen

        arrow = Vector(LEFT, color=WHITE)
        arrow.next_to(screen, RIGHT)
        prev_words = TextMobject("Previous video")
        prev_words.next_to(arrow, RIGHT)

        screen.generate_target()
        screen.target.set_height(3.75)
        screen.target.to_corner(UR)
        complex_words = TextMobject("Complex derivatives")
        complex_words.next_to(
            screen.target, LEFT,
            buff=2 * SMALL_BUFF + arrow.get_length()
        )

        self.play(
            GrowArrow(arrow),
            Write(prev_words)
        )
        self.wait(3)
        self.play(
            arrow.flip,
            arrow.next_to, screen.target, LEFT, SMALL_BUFF,
            MoveToTarget(screen),
            FadeOut(prev_words),
            Write(complex_words),
            self.teacher.change, "raise_right_hand",
            path_arc=30 * DEGREES
        )
        self.change_student_modes("erm", "sassy", "confused")
        self.look_at(screen)
        self.wait(2)
        self.change_student_modes("pondering", "confused", "sassy")
        self.wait(2)

        bubble = self.teacher.get_bubble(
            bubble_class=SpeechBubble,
            height=3, width=5
        )
        complex_words.generate_target()
        complex_words.target.move_to(bubble.get_bubble_center())
        # self.play(
        #     FadeOut(screen),
        #     FadeOut(arrow),
        #     ShowCreation(bubble),
        #     self.teacher.change, "hooray",
        #     MoveToTarget(complex_words),
        # )

        s0 = self.students[0]
        s0.target_center = s0.get_center()

        def update_s0(s0, dt):
            s0.target_center += dt * LEFT * 0.5
            s0.move_to(s0.target_center)

        self.add(Mobject.add_updater(s0, update_s0))
        self.change_student_modes("tired", "horrified", "sad")
        self.play(s0.look, LEFT)
        self.wait(4)


class TestVectorField(Scene):
    CONFIG = {
        "func": cylinder_flow_vector_field,
        "flow_time": 15,
    }

    def construct(self):
        lines = StreamLines(
            four_swirls_function,
            virtual_time=3,
            min_magnitude=0,
            max_magnitude=2,
        )
        self.add(AnimatedStreamLines(
            lines,
            line_anim_class=ShowPassingFlash
        ))
        self.wait(10)


class CylinderModel(Scene):
    CONFIG = {
        "production_quality_flow": True,
        "vector_field_func": cylinder_flow_vector_field,
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
            LaggedStartMap(
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
                lag_ratio=0,
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
        scale_factor = get_norm(RIGHT - shift_val)
        movers = VGroup(self.warped_grid, self.unit_circle)
        self.unit_circle.insert_n_curves(50)

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
            ShowCreationThenFadeAround(self.func_label),
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
            for vect in (LEFT, RIGHT)
        ])
        # This line is a bit of a hack
        h_line = Line(LEFT, RIGHT, color=WHITE)
        h_line.set_points([LEFT, LEFT, RIGHT, RIGHT])
        h_line.scale(2)
        result.add(h_line)
        return result

    def get_stream_lines(self):
        func = self.vector_field_func
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
            virtual_time=15,
        )

    def get_stream_lines_animation(self, stream_lines):
        if self.production_quality_flow:
            line_anim_class = ShowPassingFlashWithThinningStrokeWidth
        else:
            line_anim_class = ShowPassingFlash
        return AnimatedStreamLines(
            stream_lines,
            line_anim_class=line_anim_class,
        )


class OkayNotToUnderstand(Scene):
    def construct(self):
        words = TextMobject(
            "It's okay not to \\\\ understand this just yet."
        )
        morty = Mortimer()
        morty.change("confused")
        words.next_to(morty, UP)
        self.add(morty, words)


class ThatsKindOfInteresting(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Cool!", target_mode="hooray",
            student_index=2,
            added_anims=[self.teacher.change, "happy"]
        )
        self.change_student_modes("happy", "happy")
        self.wait(2)


class ElectricField(CylinderModel, MovingCameraScene):
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
            for method in (get_proton, get_electron)
        ]
        for group in groups:
            group.arrange(RIGHT, buff=MED_SMALL_BUFF)
            random.shuffle(group.submobjects)
        protons.next_to(FRAME_HEIGHT * DOWN / 2, DOWN)
        electrons.next_to(FRAME_HEIGHT * UP / 2, UP)

        self.play(
            self.warped_grid.restore,
            FadeOut(self.unit_circle),
            FadeOut(self.title),
            FadeOut(self.func_label),
            LaggedStartMap(GrowArrow, vector_field)
        )
        self.remove_foreground_mobjects(self.title, self.func_label)
        self.wait()
        for group, vect in (protons, UP), (electrons, DOWN):
            self.play(LaggedStartMap(
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
            if get_norm(point) < 1:
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
            LaggedStartMap(VFadeIn, protons),
            LaggedStartMap(VFadeIn, electrons),
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
        for h_line in h_lines:
            h_line.save_state()

        voltage = DecimalNumber(
            10, num_decimal_places=1,
            unit="\\, V",
            color=YELLOW,
            include_background_rectangle=True,
        )
        vp_prop = 0.1
        voltage_point = VectorizedPoint(
            h_lines[4].point_from_proportion(vp_prop)
        )

        def get_voltage(dummy_arg):
            y = voltage_point.get_center()[1]
            return 10 - y

        voltage_update = voltage.add_updater(
            lambda d: d.set_value(get_voltage),
        )
        voltage.add_updater(
            lambda d: d.next_to(
                voltage_point, UP, SMALL_BUFF
            )
        )

        self.play(ShowCreation(
            h_lines,
            run_time=2,
            lag_ratio=0
        ))
        self.add(voltage_update)
        self.add_foreground_mobjects(voltage)
        self.play(
            UpdateFromAlphaFunc(
                voltage, lambda m, a: m.set_fill(opacity=a)
            ),
            h_lines[4].set_stroke, YELLOW, 4,
        )
        for hl1, hl2 in zip(h_lines[4:], h_lines[5:]):
            self.play(
                voltage_point.move_to,
                hl2.point_from_proportion(vp_prop),
                hl1.restore,
                hl2.set_stroke, YELLOW, 3,
                run_time=0.5
            )
            self.wait(0.5)


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
            group.arrange(DOWN)
        topics = VGroup(div, curl)
        topics.arrange(DOWN, buff=LARGE_BUFF)
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


class ScopeMeiosis(PiCreatureScene):
    CONFIG = {
        "default_pi_creature_kwargs": {
            "flip_at_start": True,
            "color": GREY_BROWN,
        },
        "default_pi_creature_start_corner": DR,
    }

    def construct(self):
        morty = self.pi_creature
        section_titles = VGroup(*list(map(TextMobject, [
            "Background on div/curl",
            "Conformal maps",
            "Conformal map $\\Rightarrow" +
            "\\text{div}\\textbf{F} = " +
            "\\text{curl}\\textbf{F} = 0$",
            "Complex derivatives",
        ])))
        sections = VGroup(*[
            VGroup(title, self.get_lines(title, 3))
            for title in section_titles
        ])
        sections.arrange(
            DOWN, buff=MED_LARGE_BUFF,
            aligned_edge=LEFT
        )
        sections.to_edge(UP)

        top_title = section_titles[0]
        lower_sections = sections[1:]

        self.add(sections)
        modes = [
            "pondering",
            "pondering",
            "bump",
            "bump",
            "concerned_musician",
            "concerned_musician",
        ]

        for n, mode in zip(list(range(6)), modes):
            if n % 2 == 1:
                top_title = lines
                lines = self.get_lines(top_title, 4)
            else:
                lines = self.get_lines(top_title, 6)
            lower_sections.generate_target()
            lower_sections.target.next_to(
                lines, DOWN, MED_LARGE_BUFF, LEFT,
            )
            self.play(
                ShowCreation(lines),
                MoveToTarget(lower_sections),
                morty.change, mode, lines,
            )

    def get_lines(self, title, n_lines):
        lines = VGroup(*[
            Line(3 * LEFT, 3 * RIGHT, color=LIGHT_GREY)
            for x in range(n_lines)
        ])
        lines.arrange(DOWN, buff=MED_SMALL_BUFF)
        lines.next_to(
            title, DOWN,
            buff=MED_LARGE_BUFF,
            aligned_edge=LEFT
        )
        lines[-1].pointwise_become_partial(
            lines[-1], 0, random.random()
        )
        return lines


class WhyAreYouTellingUsThis(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Cool story bro...\\\\ how about the actual math?",
            target_mode="sassy",
            added_anims=[self.teacher.change, "guilty"]
        )
        self.change_student_modes("angry", "sassy", "angry")
        self.wait(2)


class TopicsAndConnections(Scene):
    CONFIG = {
        "random_seed": 1,
    }

    def construct(self):
        dots = VGroup(*[
            Dot(8 * np.array([
                random.random(),
                random.random(),
                0
            ]))
            for n in range(5)
        ])
        topics = VGroup(*[
            TextMobject(word).next_to(
                dot, RIGHT, SMALL_BUFF
            )
            for dot, word in zip(dots, [
                "Divergence/curl",
                "Fluid flow",
                "Electricity and magnetism",
                "Conformal maps",
                "Complex numbers"
            ])
        ])
        for topic in topics:
            topic.add_to_back(
                topic.copy().set_stroke(BLACK, 2)
            )

        VGroup(dots, topics).center()
        for dot in dots:
            dot.save_state()
            dot.scale(3)
            dot.set_fill(opacity=0)

        connections = VGroup(*[
            DashedLine(d1.get_center(), d2.get_center())
            for d1, d2 in it.combinations(dots, 2)
        ])
        connections.set_stroke(YELLOW, 2)

        full_rect = FullScreenFadeRectangle()

        self.play(
            LaggedStartMap(
                ApplyMethod, dots,
                lambda d: (d.restore,)
            ),
            LaggedStartMap(Write, topics),
        )
        self.wait()
        self.play(
            LaggedStartMap(ShowCreation, connections),
            Animation(topics),
            Animation(dots),
        )
        self.wait()
        self.play(
            FadeIn(full_rect),
            Animation(topics[0]),
            Animation(dots[0]),
        )
        self.wait()


class OnToTheLesson(Scene):
    def construct(self):
        words = TextMobject("On to the lesson!")
        words.scale(1.5)
        self.add(words)
        self.play(FadeInFromDown(words))
        self.wait()


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

        self.play(LaggedStartMap(GrowFromCenter, dots))
        self.wait()
        self.play(LaggedStartMap(MoveToTarget, dots, remover=True))
        self.add(vector_field)
        self.wait()

    def show_fluid_flow(self):
        vector_field = self.vector_field
        stream_lines = StreamLines(
            vector_field.func,
            **self.stream_line_config
        )
        stream_line_animation = AnimatedStreamLines(
            stream_lines,
            **self.stream_line_animation_config
        )

        self.add(stream_line_animation)
        self.play(
            vector_field.set_fill, {"opacity": 0.5}
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

        gravity_func = get_force_field_func((earth_center, -6), (moon_center, -1))
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
            (3 * LEFT, -1), (3 * RIGHT, +1)
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
            for color in (BLUE, RED)
        ])
        magnet.arrange(RIGHT, buff=0)
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
        self.play(LaggedStartMap(
            MoveToTarget, adjusted,
            run_time=3
        ))
        self.wait()
        self.play(LaggedStartMap(
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
        particles = self.get_particles()
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
            Mobject.add_updater(vector_field, update_vector_field),
            Mobject.add_updater(particles, update_particles),
        )
        self.wait(20)

    def get_particles(self):
        particles = self.particles = VGroup()
        for n in range(9):
            if n % 2 == 0:
                particle = get_proton(radius=0.2)
                particle.charge = +1
            else:
                particle = get_electron(radius=0.2)
                particle.charge = -1
            particle.velocity = np.random.normal(0, 0.1, 3)
            particles.add(particle)
            particle.shift(np.random.normal(0, 0.2, 3))

        particles.arrange_in_grid(buff=LARGE_BUFF)
        return particles

    def get_vector_field(self):
        func = get_force_field_func(*list(zip(
            list(map(Mobject.get_center, self.particles)),
            [p.charge for p in self.particles]
        )))
        self.vector_field = VectorField(func, **self.vector_field_config)
        return self.vector_field


class InsertAirfoildTODO(TODOStub):
    CONFIG = {"message": "Insert airfoil flow animation"}


class ThreeDVectorField(ExternallyAnimatedScene):
    pass


class ThreeDVectorFieldEquation(Scene):
    def construct(self):
        vector = Matrix([
            "yz",
            "xz",
            "xy",
        ])
        vector.set_height(FRAME_HEIGHT - 1)
        self.add(vector)


class GravityFluidFlow(IntroduceVectorField):
    def construct(self):
        self.vector_field = VectorField(
            lambda p: np.array(ORIGIN),
            **self.vector_field_config
        )
        self.show_gravitational_force()
        self.show_fluid_flow()


class TotallyToScale(Scene):
    def construct(self):
        words = TextMobject(
            "Totally drawn to scale. \\\\ Don't even worry about it."
        )
        words.set_width(FRAME_WIDTH - 1)
        words.add_background_rectangle()
        self.add(words)
        self.wait()


# TODO: Revisit this
class FluidFlowAsHillGradient(CylinderModel, ThreeDScene):
    CONFIG = {
        "production_quality_flow": False,
    }

    def construct(self):
        def potential(point):
            x, y = point[:2]
            result = 2 - 0.01 * op.mul(
                ((x - 4)**2 + y**2),
                ((x + 4)**2 + y**2)
            )
            return max(-10, result)

        vector_field_func = negative_gradient(potential)

        stream_lines = StreamLines(
            vector_field_func,
            virtual_time=3,
            color_lines_by_magnitude=False,
            start_points_generator_config={
                "delta_x": 0.2,
                "delta_y": 0.2,
            }
        )
        for line in stream_lines:
            line.points[:, 2] = np.apply_along_axis(
                potential, 1, line.points
            )
        stream_lines_animation = self.get_stream_lines_animation(
            stream_lines
        )

        plane = NumberPlane()

        self.add(plane)
        self.add(stream_lines_animation)
        self.wait(3)
        self.begin_ambient_camera_rotation(rate=0.1)
        self.move_camera(
            phi=70 * DEGREES,
            run_time=2
        )
        self.wait(5)


class DefineDivergence(ChangingElectricField):
    CONFIG = {
        "vector_field_config": {
            "length_func": lambda norm: 0.3,
            "min_magnitude": 0,
            "max_magnitude": 1,
        },
        "stream_line_config": {
            "start_points_generator_config": {
                "delta_x": 0.125,
                "delta_y": 0.125,
            },
            "virtual_time": 5,
            "n_anchors_per_line": 10,
            "min_magnitude": 0,
            "max_magnitude": 1,
            "stroke_width": 2,
        },
        "stream_line_animation_config": {
            "line_anim_class": ShowPassingFlash,
        },
        "flow_time": 10,
        "random_seed": 7,
    }

    def construct(self):
        self.draw_vector_field()
        self.show_flow()
        self.point_out_sources_and_sinks()
        self.show_divergence_values()

    def draw_vector_field(self):
        particles = self.get_particles()
        random.shuffle(particles.submobjects)
        particles.remove(particles[0])
        particles.arrange_in_grid(
            n_cols=4, buff=3
        )
        for particle in particles:
            particle.shift(
                np.random.normal(0, 0.75) * RIGHT,
                np.random.normal(0, 0.5) * UP,
            )
            particle.shift_onto_screen(buff=2 * LARGE_BUFF)
            particle.charge *= 0.125
        vector_field = self.get_vector_field()

        self.play(
            LaggedStartMap(GrowArrow, vector_field),
            LaggedStartMap(GrowFromCenter, particles),
            run_time=4
        )
        self.wait()
        self.play(LaggedStartMap(FadeOut, particles))

    def show_flow(self):
        stream_lines = StreamLines(
            self.vector_field.func,
            **self.stream_line_config
        )
        stream_line_animation = AnimatedStreamLines(
            stream_lines,
            **self.stream_line_animation_config
        )
        self.add(stream_line_animation)
        self.wait(self.flow_time)

    def point_out_sources_and_sinks(self):
        particles = self.particles
        self.positive_points, self.negative_points = [
            [
                particle.get_center()
                for particle in particles
                if u * particle.charge > 0
            ]
            for u in (+1, -1)
        ]
        pair_of_vector_circle_groups = VGroup()
        for point_set in self.positive_points, self.negative_points:
            vector_circle_groups = VGroup()
            for point in point_set:
                vector_circle_group = VGroup()
                for angle in np.linspace(0, TAU, 12, endpoint=False):
                    step = 0.5 * rotate_vector(RIGHT, angle)
                    vect = self.vector_field.get_vector(point + step)
                    vect.set_color(WHITE)
                    vect.set_stroke(width=2)
                    vector_circle_group.add(vect)
                vector_circle_groups.add(vector_circle_group)
            pair_of_vector_circle_groups.add(vector_circle_groups)

            self.play(
                self.vector_field.set_fill, {"opacity": 0.5},
                LaggedStartMap(
                    LaggedStartMap, vector_circle_groups,
                    lambda vcg: (GrowArrow, vcg),
                ),
            )
            self.wait(4)
            self.play(FadeOut(vector_circle_groups))
        self.play(self.vector_field.set_fill, {"opacity": 1})
        self.positive_vector_circle_groups = pair_of_vector_circle_groups[0]
        self.negative_vector_circle_groups = pair_of_vector_circle_groups[1]
        self.wait()

    def show_divergence_values(self):
        positive_points = self.positive_points
        negative_points = self.negative_points
        div_func = divergence(self.vector_field.func)

        circle = Circle(color=WHITE, radius=0.2)
        circle.add(Dot(circle.get_center(), radius=0.02))
        circle.move_to(positive_points[0])

        div_tex = TexMobject(
            "\\text{div} \\, \\textbf{F}(x, y) = "
        )
        div_tex.add_background_rectangle()
        div_tex_update = Mobject.add_updater(
            div_tex, lambda m: m.next_to(circle, UP, SMALL_BUFF)
        )

        div_value = DecimalNumber(
            0,
            num_decimal_places=1,
            include_background_rectangle=True,
            include_sign=True,
        )
        div_value_update = ContinualChangingDecimal(
            div_value,
            lambda a: np.round(div_func(circle.get_center()), 1),
            position_update_func=lambda m: m.next_to(div_tex, RIGHT, SMALL_BUFF),
            include_sign=True,
        )

        self.play(
            ShowCreation(circle),
            FadeIn(div_tex),
            FadeIn(div_value),
        )
        self.add(div_tex_update)
        self.add(div_value_update)

        self.wait()
        for point in positive_points[1:-1]:
            self.play(circle.move_to, point)
            self.wait(1.5)
        for point in negative_points:
            self.play(circle.move_to, point)
            self.wait(2)
        self.wait(4)
        # self.remove(div_tex_update)
        # self.remove(div_value_update)
        # self.play(
        #     ApplyMethod(circle.scale, 0, remover=True),
        #     FadeOut(div_tex),
        #     FadeOut(div_value),
        # )


class DefineDivergenceJustFlow(DefineDivergence):
    CONFIG = {
        "flow_time": 10,
    }

    def construct(self):
        self.force_skipping()
        self.draw_vector_field()
        self.revert_to_original_skipping_status()
        self.clear()
        self.show_flow()


class DefineDivergenceSymbols(Scene):
    def construct(self):
        tex_mob = TexMobject(
            "\\text{div}",
            "\\textbf{F}",
            "(x, y)",
            "=",
        )
        div, F, xy, eq = tex_mob
        output = DecimalNumber(0, include_sign=True)
        output.next_to(tex_mob, RIGHT)
        time_tracker = ValueTracker()
        always_shift(time_tracker, rate=1)
        self.add(time_tracker)
        output_animation = ContinualChangingDecimal(
            output, lambda a: 3 * np.cos(int(time_tracker.get_value())),
        )

        F.set_color(BLUE)
        xy.set_color(YELLOW)

        F_brace = Brace(F, UP, buff=SMALL_BUFF)
        F_label = F_brace.get_text(
            "Vector field function",
        )
        F_label.match_color(F)
        xy_brace = Brace(xy, DOWN, buff=SMALL_BUFF)
        xy_label = xy_brace.get_text("Some point")
        xy_label.match_color(xy)
        output_brace = Brace(output, UP, buff=SMALL_BUFF)
        output_label = output_brace.get_text(
            "Measure of how much \\\\ "
            "$(x, y)$ ``generates'' fluid"
        )
        brace_label_pairs = [
            (F_brace, F_label),
            (xy_brace, xy_label),
            (output_brace, output_label),
        ]

        self.add(tex_mob, output_animation)
        fade_anims = []
        for brace, label in brace_label_pairs:
            self.play(
                GrowFromCenter(brace),
                FadeInFromDown(label),
                *fade_anims
            )
            self.wait(2)
            fade_anims = list(map(FadeOut, [brace, label]))
        self.wait()


class DivergenceAtSlowFastPoint(Scene):
    CONFIG = {
        "vector_field_config": {
            "length_func": lambda norm: 0.1 + 0.4 * norm / 4.0,
            "min_magnitude": 0,
            "max_magnitude": 3,
        },
        "stream_lines_config": {
            "start_points_generator_config": {
                "delta_x": 0.125,
                "delta_y": 0.125,
            },
            "virtual_time": 1,
            "min_magnitude": 0,
            "max_magnitude": 3,
        },
    }

    def construct(self):
        def func(point):
            return 3 * sigmoid(point[0]) * RIGHT
        vector_field = self.vector_field = VectorField(
            func, **self.vector_field_config
        )

        circle = Circle(color=WHITE)
        slow_words = TextMobject("Slow flow in")
        fast_words = TextMobject("Fast flow out")
        words = VGroup(slow_words, fast_words)
        for word, vect in zip(words, [LEFT, RIGHT]):
            word.add_background_rectangle()
            word.next_to(circle, vect)

        div_tex = TexMobject(
            "\\text{div}\\,\\textbf{F}(x, y) > 0"
        )
        div_tex.add_background_rectangle()
        div_tex.next_to(circle, UP)

        self.add(vector_field)
        self.add_foreground_mobjects(circle, div_tex)
        self.begin_flow()
        self.wait(2)
        for word in words:
            self.add_foreground_mobjects(word)
            self.play(Write(word))
        self.wait(8)

    def begin_flow(self):
        stream_lines = StreamLines(
            self.vector_field.func,
            **self.stream_lines_config
        )
        stream_line_animation = AnimatedStreamLines(stream_lines)
        stream_line_animation.update(3)
        self.add(stream_line_animation)


class DivergenceAsNewFunction(Scene):
    def construct(self):
        self.add_plane()
        self.show_vector_field_function()
        self.show_divergence_function()

    def add_plane(self):
        plane = self.plane = NumberPlane()
        plane.add_coordinates()
        self.add(plane)

    def show_vector_field_function(self):
        func = self.func
        unscaled_vector_field = VectorField(
            func,
            length_func=lambda norm: norm,
            colors=[BLUE_C, YELLOW, RED],
            delta_x=np.inf,
            delta_y=np.inf,
        )

        in_dot = Dot(color=PINK)
        in_dot.move_to(3.75 * LEFT + 1.25 * UP)

        def get_input():
            return in_dot.get_center()

        def get_out_vect():
            return unscaled_vector_field.get_vector(get_input())

        # Tex
        func_tex = TexMobject(
            "\\textbf{F}(", "+0.00", ",", "+0.00", ")", "=",
        )
        dummy_in_x, dummy_in_y = func_tex.get_parts_by_tex("+0.00")
        func_tex.add_background_rectangle()
        rhs = DecimalMatrix(
            [[0], [0]],
            element_to_mobject_config={
                "num_decimal_places": 2,
                "include_sign": True,
            },
            include_background_rectangle=True
        )
        rhs.next_to(func_tex, RIGHT)
        dummy_out_x, dummy_out_y = rhs.get_mob_matrix().flatten()

        VGroup(func_tex, rhs).to_corner(UL, buff=MED_SMALL_BUFF)

        VGroup(
            dummy_in_x, dummy_in_y,
            dummy_out_x, dummy_out_y,
        ).set_fill(BLACK, opacity=0)

        # Changing decimals
        in_x, in_y, out_x, out_y = [
            DecimalNumber(0, include_sign=True)
            for x in range(4)
        ]
        VGroup(in_x, in_y).set_color(in_dot.get_color())
        VGroup(out_x, out_y).set_color(get_out_vect().get_fill_color())
        in_x_update = ContinualChangingDecimal(
            in_x, lambda a: get_input()[0],
            position_update_func=lambda m: m.move_to(dummy_in_x)
        )
        in_y_update = ContinualChangingDecimal(
            in_y, lambda a: get_input()[1],
            position_update_func=lambda m: m.move_to(dummy_in_y)
        )
        out_x_update = ContinualChangingDecimal(
            out_x, lambda a: func(get_input())[0],
            position_update_func=lambda m: m.move_to(dummy_out_x)
        )
        out_y_update = ContinualChangingDecimal(
            out_y, lambda a: func(get_input())[1],
            position_update_func=lambda m: m.move_to(dummy_out_y)
        )

        self.add(func_tex, rhs)
        # self.add(Mobject.add_updater(
        #     rhs, lambda m: m.next_to(func_tex, RIGHT)
        # ))

        # Where those decimals actually change
        self.add(in_x_update, in_y_update)

        in_dot.save_state()
        in_dot.move_to(ORIGIN)
        self.play(in_dot.restore)
        self.wait()
        self.play(*[
            ReplacementTransform(
                VGroup(mob.copy().fade(1)),
                VGroup(out_x, out_y),
            )
            for mob in (in_x, in_y)
        ])
        out_vect = get_out_vect()
        VGroup(out_x, out_y).match_style(out_vect)
        out_vect.save_state()
        out_vect.move_to(rhs)
        out_vect.set_fill(opacity=0)
        self.play(out_vect.restore)
        self.out_vect_update = Mobject.add_updater(
            out_vect,
            lambda ov: Transform(ov, get_out_vect()).update(1)
        )

        self.add(self.out_vect_update)
        self.add(out_x_update, out_y_update)

        self.add(Mobject.add_updater(
            VGroup(out_x, out_y),
            lambda m: m.match_style(out_vect)
        ))
        self.wait()

        for vect in DOWN, 2 * RIGHT, UP:
            self.play(
                in_dot.shift, 3 * vect,
                run_time=3
            )
            self.wait()

        self.in_dot = in_dot
        self.out_vect = out_vect
        self.func_equation = VGroup(func_tex, rhs)
        self.out_x, self.out_y = out_x, out_y
        self.in_x, self.in_y = out_x, out_y
        self.in_x_update = in_x_update
        self.in_y_update = in_y_update
        self.out_x_update = out_x_update
        self.out_y_update = out_y_update

    def show_divergence_function(self):
        vector_field = VectorField(self.func)
        vector_field.remove(*[
            v for v in vector_field
            if v.get_start()[0] < 0 and v.get_start()[1] > 2
        ])
        vector_field.set_fill(opacity=0.5)
        in_dot = self.in_dot

        def get_neighboring_points(step_sizes=[0.3], n_angles=12):
            point = in_dot.get_center()
            return list(it.chain(*[
                [
                    point + step_size * step
                    for step in compass_directions(n_angles)
                ]
                for step_size in step_sizes
            ]))

        def get_vector_ring():
            return VGroup(*[
                vector_field.get_vector(point)
                for point in get_neighboring_points()
            ])

        def get_stream_lines():
            return StreamLines(
                self.func,
                start_points_generator=get_neighboring_points,
                start_points_generator_config={
                    "step_sizes": np.arange(0.1, 0.5, 0.1)
                },
                virtual_time=1,
                stroke_width=3,
            )

        def show_flow():
            stream_lines = get_stream_lines()
            random.shuffle(stream_lines.submobjects)
            self.play(LaggedStartMap(
                ShowCreationThenDestruction,
                stream_lines,
                remover=True
            ))

        vector_ring = get_vector_ring()
        vector_ring_update = Mobject.add_updater(
            vector_ring,
            lambda vr: Transform(vr, get_vector_ring()).update(1)
        )

        func_tex, rhs = self.func_equation
        out_x, out_y = self.out_x, self.out_y
        out_x_update = self.out_x_update
        out_y_update = self.out_y_update
        div_tex = TexMobject("\\text{div}")
        div_tex.add_background_rectangle()
        div_tex.move_to(func_tex, LEFT)
        div_tex.shift(2 * SMALL_BUFF * RIGHT)

        self.remove(out_x_update, out_y_update)
        self.remove(self.out_vect_update)
        self.add(self.in_x_update, self.in_y_update)
        self.play(
            func_tex.next_to, div_tex, RIGHT, SMALL_BUFF,
            {"submobject_to_align": func_tex[1][0]},
            Write(div_tex),
            FadeOut(self.out_vect),
            FadeOut(out_x),
            FadeOut(out_y),
            FadeOut(rhs),
        )
        # This line is a dumb hack around a Scene bug
        self.add(*[
            Mobject.add_updater(
                mob, lambda m: m.set_fill(None, 0)
            )
            for mob in (out_x, out_y)
        ])
        self.add_foreground_mobjects(div_tex)
        self.play(
            LaggedStartMap(GrowArrow, vector_field),
            LaggedStartMap(GrowArrow, vector_ring),
        )
        self.add(vector_ring_update)
        self.wait()

        div_func = divergence(self.func)
        div_rhs = DecimalNumber(
            0, include_sign=True,
            include_background_rectangle=True
        )
        div_rhs_update = ContinualChangingDecimal(
            div_rhs, lambda a: div_func(in_dot.get_center()),
            position_update_func=lambda d: d.next_to(func_tex, RIGHT, SMALL_BUFF)
        )

        self.play(FadeIn(div_rhs))
        self.add(div_rhs_update)
        show_flow()

        for vect in 2 * RIGHT, 3 * DOWN, 2 * LEFT, 2 * LEFT:
            self.play(in_dot.shift, vect, run_time=3)
            show_flow()
        self.wait()

    def func(self, point):
        x, y = point[:2]
        return np.sin(x + y) * RIGHT + np.sin(y * x / 3) * UP


class DivergenceZeroCondition(Scene):
    def construct(self):
        title = TextMobject(
            "For actual (incompressible) fluid flow:"
        )
        title.to_edge(UP)
        equation = TexMobject(
            "\\text{div} \\, \\textbf{F} = 0 \\quad \\text{everywhere}"
        )
        equation.next_to(title, DOWN)

        for mob in title, equation:
            mob.add_background_rectangle(buff=MED_SMALL_BUFF / 2)
            self.add_foreground_mobjects(mob)
        self.wait(1)


class PureCylinderFlow(Scene):
    def construct(self):
        self.add_vector_field()
        self.begin_flow()
        self.add_circle()
        self.wait(5)

    def add_vector_field(self):
        vector_field = VectorField(
            cylinder_flow_vector_field,
        )
        for vector in vector_field:
            if get_norm(vector.get_start()) < 1:
                vector_field.remove(vector)
        vector_field.set_fill(opacity=0.75)
        self.modify_vector_field(vector_field)
        self.add_foreground_mobjects(vector_field)

    def begin_flow(self):
        stream_lines = StreamLines(
            cylinder_flow_vector_field,
            colors=[BLUE_E, BLUE_D, BLUE_C],
            start_points_generator_config={
                "delta_x": 0.125,
                "delta_y": 0.125,
            },
            virtual_time=5,
        )
        self.add(stream_lines)
        for stream_line in stream_lines:
            if get_norm(stream_line.points[0]) < 1:
                stream_lines.remove(stream_line)

        self.modify_flow(stream_lines)

        stream_line_animation = AnimatedStreamLines(stream_lines)
        stream_line_animation.update(3)

        self.add(stream_line_animation)

    def add_circle(self):
        circle = Circle(
            radius=1,
            stroke_color=YELLOW,
            fill_color=BLACK,
            fill_opacity=1,
        )
        self.modify_flow(circle)
        self.add_foreground_mobjects(circle)

    def modify_flow(self, mobject):
        pass

    def modify_vector_field(self, vector_field):
        pass


class PureAirfoilFlow(PureCylinderFlow):
    def modify_flow(self, mobject):
        vect = 0.1 * LEFT + 0.2 * UP
        mobject.scale(get_norm(vect - RIGHT))
        mobject.shift(vect)
        mobject.apply_complex_function(joukowsky_map)
        return mobject

    def modify_vector_field(self, vector_field):
        def func(z):
            w = complex(-0.1, 0.2)
            n = abs(w - 1)
            return joukowsky_map(inverse_joukowsky_map(z) - w / n)

        def new_vector_field_func(point):
            z = R3_to_complex(point)
            return complex_to_R3(derivative(func)(z).conjugate())

        vf = VectorField(new_vector_field_func, delta_y=0.33)
        Transform(vector_field, vf).update(1)
        vf.set_fill(opacity=0.5)


class IntroduceCurl(IntroduceVectorField):
    CONFIG = {
        "stream_line_animation_config": {
            "line_anim_class": ShowPassingFlash,
        },
        "stream_line_config": {
            "start_points_generator_config": {
                "delta_x": 0.125,
                "delta_y": 0.125,
            },
            "virtual_time": 1,
        }
    }

    def construct(self):
        self.add_title()
        self.show_vector_field()
        self.begin_flow()
        self.show_rotation()

    def add_title(self):
        title = self.title = Title(
            "Curl",
            match_underline_width_to_text=True,
            scale_factor=1.5,
        )
        title.add_background_rectangle()
        title.to_edge(UP, buff=MED_SMALL_BUFF)
        self.add_foreground_mobjects(title)

    def show_vector_field(self):
        vector_field = self.vector_field = VectorField(
            four_swirls_function,
            **self.vector_field_config
        )
        vector_field.submobjects.sort(
            key=lambda v: v.get_length()
        )

        self.play(LaggedStartMap(GrowArrow, vector_field))
        self.wait()

    def begin_flow(self):
        stream_lines = StreamLines(
            self.vector_field.func,
            **self.stream_line_config
        )
        stream_line_animation = AnimatedStreamLines(
            stream_lines,
            **self.stream_line_animation_config
        )

        self.add(stream_line_animation)
        self.wait(3)

    def show_rotation(self):
        clockwise_arrows, counterclockwise_arrows = [
            VGroup(*[
                self.get_rotation_arrows(clockwise=cw).move_to(point)
                for point in points
            ])
            for cw, points in [
                (True, [2 * UP, 2 * DOWN]),
                (False, [4 * LEFT, 4 * RIGHT]),
            ]
        ]

        for group, u in (counterclockwise_arrows, +1), (clockwise_arrows, -1):
            for arrows in group:
                label = TexMobject(
                    "\\text{curl} \\, \\textbf{F}",
                    ">" if u > 0 else "<",
                    "0"
                )
                label.add_background_rectangle()
                label.next_to(arrows, DOWN)
                self.add_foreground_mobjects(label)
                always_rotate(arrows, rate=u * 30 * DEGREES)
                self.play(
                    FadeIn(arrows),
                    FadeIn(label)
                )
        self.wait(2)
        for group in counterclockwise_arrows, clockwise_arrows:
            self.play(FocusOn(group[0]))
            self.play(
                UpdateFromAlphaFunc(
                    group,
                    lambda mob, alpha: mob.set_color(
                        interpolate_color(WHITE, PINK, alpha)
                    ).set_stroke(
                        width=interpolate(5, 10, alpha)
                    ),
                    rate_func=there_and_back,
                    run_time=2
                )
            )
            self.wait()
        self.wait(6)

    # Helpers
    def get_rotation_arrows(self, clockwise=True, width=1):
        result = VGroup(*[
            Arrow(
                *points,
                buff=2 * SMALL_BUFF,
                path_arc=90 * DEGREES
            ).set_stroke(width=5)
            for points in adjacent_pairs(compass_directions(4, RIGHT))
        ])
        if clockwise:
            result.flip()
        result.set_width(width)
        return result


class ShearCurl(IntroduceCurl):
    def construct(self):
        self.show_vector_field()
        self.begin_flow()
        self.wait(2)
        self.comment_on_relevant_region()

    def show_vector_field(self):
        vector_field = self.vector_field = VectorField(
            self.func, **self.vector_field_config
        )
        vector_field.submobjects.key=sort(
            key=lambda a: a.get_length()
        )
        self.play(LaggedStartMap(GrowArrow, vector_field))

    def comment_on_relevant_region(self):
        circle = Circle(color=WHITE, radius=0.75)
        circle.next_to(ORIGIN, UP, LARGE_BUFF)
        self.play(ShowCreation(circle))

        slow_words, fast_words = words = [
            TextMobject("Slow flow below"),
            TextMobject("Fast flow above")
        ]
        for word, vect in zip(words, [DOWN, UP]):
            word.add_background_rectangle(buff=SMALL_BUFF)
            word.next_to(circle, vect)
            self.add_foreground_mobjects(word)
            self.play(Write(word))
            self.wait()

        twig = Rectangle(
            height=0.8 * 2 * circle.radius,
            width=SMALL_BUFF,
            stroke_width=0,
            fill_color=GREY_BROWN,
            fill_opacity=1,
        )
        twig.add(Dot(twig.get_center()))
        twig.move_to(circle)
        always_rotate(
            twig, rate=-90 * DEGREES,
        )

        self.play(FadeInFrom(twig, UP))
        self.add(twig_rotation)
        self.wait(16)

    # Helpers
    def func(self, point):
        return 0.5 * point[1] * RIGHT


class FromKAWrapper(TeacherStudentsScene):
    def construct(self):
        screen = self.screen
        self.play(
            self.teacher.change, "raise_right_hand",
            self.get_student_changes(
                "pondering", "confused", "hooray",
            )
        )
        self.look_at(screen)
        self.wait(2)
        self.change_student_modes("erm", "happy", "confused")
        self.wait(3)
        self.teacher_says(
            "Our focus is \\\\ the 2d version",
            bubble_kwargs={"width": 4, "height": 3},
            added_anims=[self.get_student_changes(
                "happy", "hooray", "happy"
            )]
        )
        self.wait()


class ShowCurlAtVariousPoints(IntroduceCurl):
    CONFIG = {
        "func": four_swirls_function,
        "sample_points": [
            4 * RIGHT,
            2 * UP,
            4 * LEFT,
            2 * DOWN,
            ORIGIN,
            3 * RIGHT + 2 * UP,
            3 * LEFT + 2 * UP,
        ],
        "vector_field_config": {
            "fill_opacity": 0.75
        },
        "stream_line_config": {
            "virtual_time": 5,
            "start_points_generator_config": {
                "delta_x": 0.25,
                "delta_y": 0.25,
            }
        }
    }

    def construct(self):
        self.add_plane()
        self.show_vector_field()
        self.begin_flow()
        self.show_curl_at_points()

    def add_plane(self):
        plane = NumberPlane()
        plane.add_coordinates()
        self.add(plane)
        self.plane = plane

    def show_curl_at_points(self):
        dot = Dot()
        circle = Circle(radius=0.25, color=WHITE)
        circle.move_to(dot)
        circle_update = Mobject.add_updater(
            circle,
            lambda m: m.move_to(dot)
        )

        curl_tex = TexMobject(
            "\\text{curl} \\, \\textbf{F}(x, y) = "
        )
        curl_tex.add_background_rectangle(buff=0.025)
        curl_tex_update = Mobject.add_updater(
            curl_tex,
            lambda m: m.next_to(circle, UP, SMALL_BUFF)
        )

        curl_func = two_d_curl(self.func)
        curl_value = DecimalNumber(
            0, include_sign=True,
            include_background_rectangle=True,
        )
        curl_value_update = ContinualChangingDecimal(
            curl_value,
            lambda a: curl_func(dot.get_center()),
            position_update_func=lambda m: m.next_to(
                curl_tex, RIGHT, buff=0
            ),
            include_background_rectangle=True,
            include_sign=True,
        )

        points = self.sample_points
        self.add(dot, circle_update)
        self.play(
            dot.move_to, points[0],
            VFadeIn(dot),
            VFadeIn(circle),
        )
        curl_tex_update.update(0)
        curl_value_update.update(0)
        self.play(Write(curl_tex), FadeIn(curl_value))
        self.add(curl_tex_update, curl_value_update)
        self.wait()
        for point in points[1:]:
            self.play(dot.move_to, point, run_time=3)
            self.wait(2)
        self.wait(2)


class IllustrationUseVennDiagram(Scene):
    def construct(self):
        title = Title("Divergence \\& Curl")
        title.to_edge(UP, buff=MED_SMALL_BUFF)

        useful_for = TextMobject("Useful for")
        useful_for.next_to(title, DOWN)
        useful_for.set_color(BLUE)

        fluid_flow = TextMobject("Fluid \\\\ flow")
        fluid_flow.next_to(ORIGIN, UL)
        ff_circle = Circle(color=YELLOW)
        ff_circle.surround(fluid_flow, stretch=True)
        fluid_flow.match_color(ff_circle)

        big_circle = Circle(
            fill_color=BLUE,
            fill_opacity=0.2,
            stroke_color=BLUE,
        )
        big_circle.stretch_to_fit_width(9)
        big_circle.stretch_to_fit_height(6)
        big_circle.next_to(useful_for, DOWN, SMALL_BUFF)

        illustrated_by = TextMobject("Illustrated by")
        illustrated_by.next_to(
            big_circle.point_from_proportion(3. / 8), UL
        )
        illustrated_by.match_color(ff_circle)
        illustrated_by_arrow = Arrow(
            illustrated_by.get_bottom(),
            ff_circle.get_left(),
            path_arc=90 * DEGREES,
            color=YELLOW,
        )
        illustrated_by_arrow.pointwise_become_partial(
            illustrated_by_arrow, 0, 0.95
        )

        examples = VGroup(
            TextMobject("Electricity"),
            TextMobject("Magnetism"),
            TextMobject("Phase flow"),
            TextMobject("Stokes' theorem"),
        )
        points = [
            2 * RIGHT + 0.5 * UP,
            2 * RIGHT + 0.5 * DOWN,
            2 * DOWN,
            2 * LEFT + DOWN,
        ]
        for example, point in zip(examples, points):
            example.move_to(point)

        self.play(Write(title), run_time=1)
        self.play(
            Write(illustrated_by),
            ShowCreation(illustrated_by_arrow),
            run_time=1,
        )
        self.play(
            ShowCreation(ff_circle),
            FadeIn(fluid_flow),
        )
        self.wait()
        self.play(
            Write(useful_for),
            DrawBorderThenFill(big_circle),
            Animation(fluid_flow),
            Animation(ff_circle),
        )
        self.play(LaggedStartMap(
            FadeIn, examples,
            run_time=3,
        ))
        self.wait()


class MaxwellsEquations(Scene):
    CONFIG = {
        "faded_opacity": 0.3,
    }

    def construct(self):
        self.add_equations()
        self.circle_gauss_law()
        self.circle_magnetic_divergence()
        self.circle_curl_equations()

    def add_equations(self):
        title = Title("Maxwell's equations")
        title.to_edge(UP, buff=MED_SMALL_BUFF)

        tex_to_color_map = {
            "\\textbf{E}": BLUE,
            "\\textbf{B}": YELLOW,
            "\\rho": WHITE,
        }

        equations = self.equations = VGroup(*[
            TexMobject(
                tex, tex_to_color_map=tex_to_color_map
            )
            for tex in [
                """
                    \\text{div} \\, \\textbf{E} =
                    {\\rho \\over \\varepsilon_0}
                """,
                """\\text{div} \\, \\textbf{B} = 0""",
                """
                    \\text{curl} \\, \\textbf{E} =
                    -{\\partial \\textbf{B} \\over \\partial t}
                """,
                """
                    \\text{curl} \\, \\textbf{B} =
                    \\mu_0 \\left(
                        \\textbf{J} + \\varepsilon_0
                        {\\partial \\textbf{E} \\over \\partial t}
                    \\right)
                """,
            ]
        ])
        equations.arrange(
            DOWN, aligned_edge=LEFT,
            buff=MED_LARGE_BUFF
        )

        field_definitions = VGroup(*[
            TexMobject(text, tex_to_color_map=tex_to_color_map)
            for text in [
                "\\text{Electric field: } \\textbf{E}",
                "\\text{Magnetic field: } \\textbf{B}",
            ]
        ])
        field_definitions.arrange(
            RIGHT, buff=MED_LARGE_BUFF
        )
        field_definitions.next_to(title, DOWN, MED_LARGE_BUFF)
        equations.next_to(field_definitions, DOWN, MED_LARGE_BUFF)
        field_definitions.shift(MED_SMALL_BUFF * UP)

        self.add(title)
        self.add(field_definitions)
        self.play(LaggedStartMap(
            FadeIn, equations,
            run_time=3,
            lag_range=0.4
        ))
        self.wait()

    def circle_gauss_law(self):
        equation = self.equations[0]
        rect = SurroundingRectangle(equation)
        rect.set_color(RED)
        rho = equation.get_part_by_tex("\\rho")
        sub_rect = SurroundingRectangle(rho)
        sub_rect.match_color(rect)
        rho_label = TextMobject("Charge density")
        rho_label.next_to(sub_rect, RIGHT)
        rho_label.match_color(sub_rect)
        gauss_law = TextMobject("Gauss's law")
        gauss_law.next_to(rect, RIGHT)

        self.play(
            ShowCreation(rect),
            Write(gauss_law, run_time=1),
            self.equations[1:].set_fill, {"opacity": self.faded_opacity}
        )
        self.wait(2)
        self.play(
            ReplacementTransform(rect, sub_rect),
            FadeOut(gauss_law),
            FadeIn(rho_label),
            rho.match_color, sub_rect,
        )
        self.wait()
        self.play(
            self.equations.to_edge, LEFT,
            MaintainPositionRelativeTo(rho_label, equation),
            MaintainPositionRelativeTo(sub_rect, equation),
            VFadeOut(rho_label),
            VFadeOut(sub_rect),
        )
        self.wait()

    def circle_magnetic_divergence(self):
        equations = self.equations
        rect = SurroundingRectangle(equations[1])

        self.play(
            equations[0].set_fill, {"opacity": self.faded_opacity},
            equations[1].set_fill, {"opacity": 1.0},
        )
        self.play(ShowCreation(rect))
        self.wait(3)
        self.play(FadeOut(rect))

    def circle_curl_equations(self):
        equations = self.equations
        rect = SurroundingRectangle(equations[2:])
        randy = Randolph(height=2)
        randy.flip()
        randy.next_to(rect, RIGHT, aligned_edge=DOWN)
        randy.look_at(rect)

        self.play(
            equations[1].set_fill, {"opacity": self.faded_opacity},
            equations[2:].set_fill, {"opacity": 1.0},
        )
        self.play(ShowCreation(rect))
        self.play(
            randy.change, "confused",
            VFadeIn(randy),
        )
        self.play(Blink(randy))
        self.play(randy.look_at, 2 * RIGHT)
        self.wait(3)
        self.play(
            FadeOut(rect),
            randy.change, "pondering",
            randy.look_at, rect,
        )
        self.wait()
        self.play(Blink(randy))
        self.wait()


class ThatWeKnowOf(Scene):
    def construct(self):
        words = TextMobject("*That we know of!")
        self.add(words)


class IllustrateGaussLaw(DefineDivergence, MovingCameraScene):
    CONFIG = {
        "flow_time": 10,
        "stream_line_config": {
            "start_points_generator_config": {
                "delta_x": 1.0 / 16,
                "delta_y": 1.0 / 16,
                "x_min": -2,
                "x_max": 2,
                "y_min": -1.5,
                "y_max": 1.5,
            },
            "color_lines_by_magnitude": True,
            "colors": [BLUE_E, BLUE_D, BLUE_C],
            "stroke_width": 3,
        },
        "stream_line_animation_config": {
            "line_anim_class": ShowPassingFlashWithThinningStrokeWidth,
            "line_anim_config": {
                "n_segments": 5,
            }
        },
        "final_frame_width": 4,
    }

    def construct(self):
        particles = self.get_particles()
        vector_field = self.get_vector_field()

        self.add_foreground_mobjects(vector_field)
        self.add_foreground_mobjects(particles)
        self.zoom_in()
        self.show_flow()

    def get_particles(self):
        particles = VGroup(
            get_proton(radius=0.1),
            get_electron(radius=0.1),
        )
        particles.arrange(RIGHT, buff=2.25)
        particles.shift(0.25 * UP)
        for particle, sign in zip(particles, [+1, -1]):
            particle.charge = sign

        self.particles = particles
        return particles

    def zoom_in(self):
        self.play(
            self.camera_frame.set_width, self.final_frame_width,
            run_time=2
        )


class IllustrateGaussMagnetic(IllustrateGaussLaw):
    CONFIG = {
        "final_frame_width": 7,
        "stream_line_config": {
            "start_points_generator_config": {
                "delta_x": 1.0 / 16,
                "delta_y": 1.0 / 16,
                "x_min": -3.5,
                "x_max": 3.5,
                "y_min": -2,
                "y_max": 2,
            },
            "color_lines_by_magnitude": True,
            "colors": [BLUE_E, BLUE_D, BLUE_C],
            "stroke_width": 3,
        },
        "stream_line_animation_config": {
            "start_up_time": 0,
        },
        "flow_time": 10,
    }

    def construct(self):
        self.add_wires()
        self.show_vector_field()
        self.zoom_in()
        self.show_flow()

    def add_wires(self):
        top, bottom = [
            Circle(
                radius=0.275,
                stroke_color=WHITE,
                fill_color=BLACK,
                fill_opacity=1
            )
            for x in range(2)
        ]
        top.add(TexMobject("\\times").scale(0.5))
        bottom.add(Dot().scale(0.5))
        top.move_to(1 * UP)
        bottom.move_to(1 * DOWN)

        self.add_foreground_mobjects(top, bottom)

    def show_vector_field(self):
        vector_field = self.vector_field = VectorField(
            self.func, **self.vector_field_config
        )
        vector_field.submobjects.sort(
            key=lambda a: -a1.get_length()
        )
        self.play(LaggedStartMap(GrowArrow, vector_field))
        self.add_foreground_mobjects(
            vector_field, *self.foreground_mobjects
        )

    def func(self, point):
        x, y = point[:2]
        top_part = np.array([(y - 1.0), -x, 0])
        bottom_part = np.array([-(y + 1.0), x, 0])
        norm = get_norm
        return 1 * op.add(
            top_part / (norm(top_part) * norm(point - UP) + 0.1),
            bottom_part / (norm(bottom_part) * norm(point - DOWN) + 0.1),
            # top_part / (norm(top_part)**2 + 1),
            # bottom_part / (norm(bottom_part)**2 + 1),
        )


class IllustrateEMCurlEquations(ExternallyAnimatedScene):
    pass


class RelevantInNonSpatialCircumstances(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            """
                $\\textbf{div}$ and $\\textbf{curl}$ are \\\\
                even useful in some \\\\
                non-spatial problems
            """,
            target_mode="hooray"
        )
        self.change_student_modes(
            "sassy", "confused", "hesitant"
        )
        self.wait(3)


class ShowTwoPopulations(Scene):
    CONFIG = {
        "total_num_animals": 80,
        "start_num_foxes": 40,
        "start_num_rabbits": 20,
        "animal_height": 0.5,
        "final_wait_time": 30,
        "count_word_scale_val": 1,
    }

    def construct(self):
        self.introduce_animals()
        self.evolve_system()

    def introduce_animals(self):
        foxes = self.foxes = VGroup(*[
            self.get_fox()
            for n in range(self.total_num_animals)
        ])
        rabbits = self.rabbits = VGroup(*[
            self.get_rabbit()
            for n in range(self.total_num_animals)
        ])
        foxes[self.start_num_foxes:].set_fill(opacity=0)
        rabbits[self.start_num_rabbits:].set_fill(opacity=0)

        fox, rabbit = examples = VGroup(foxes[0], rabbits[0])
        for mob in examples:
            mob.save_state()
            mob.set_height(3)
        examples.arrange(LEFT, buff=2)

        preditor, prey = words = VGroup(
            TextMobject("Predator"),
            TextMobject("Prey")
        )
        for mob, word in zip(examples, words):
            word.scale(1.5)
            word.next_to(mob, UP)
            self.play(
                FadeInFromDown(mob),
                Write(word, run_time=1),
            )
        self.play(
            LaggedStartMap(
                ApplyMethod, examples,
                lambda m: (m.restore,)
            ),
            LaggedStartMap(FadeOut, words),
            *[
                LaggedStartMap(
                    FadeIn,
                    group[1:],
                    run_time=4,
                    lag_ratio=0.1,
                    rate_func=lambda t: np.clip(smooth(2 * t), 0, 1)
                )
                for group in [foxes, rabbits]
            ]
        )

    def evolve_system(self):
        foxes = self.foxes
        rabbits = self.rabbits
        phase_point = VectorizedPoint(
            self.start_num_rabbits * RIGHT +
            self.start_num_foxes * UP
        )
        self.add(move_along_vector_field(
            phase_point,
            preditor_prey_vector_field,
        ))

        def get_num_rabbits():
            return phase_point.get_center()[0]

        def get_num_foxes():
            return phase_point.get_center()[1]

        def get_updater(pop_size_getter):
            def update(animals):
                target_num = pop_size_getter()
                for n, animal in enumerate(animals):
                    animal.set_fill(
                        opacity=np.clip(target_num - n, 0, 1)
                    )
                target_int = int(np.ceil(target_num))
                tail = animals.submobjects[target_int:]
                random.shuffle(tail)
                animals.submobjects[target_int:] = tail

            return update

        self.add(Mobject.add_updater(
            foxes, get_updater(get_num_foxes)
        ))
        self.add(Mobject.add_updater(
            rabbits, get_updater(get_num_rabbits)
        ))

        # Add counts for foxes and rabbits
        labels = self.get_pop_labels()
        num_foxes = Integer(10)
        num_foxes.scale(self.count_word_scale_val)
        num_foxes.next_to(labels[0], RIGHT)
        num_foxes.align_to(labels[0][0][1], DOWN)
        num_rabbits = Integer(10)
        num_rabbits.scale(self.count_word_scale_val)
        num_rabbits.next_to(labels[1], RIGHT)
        num_rabbits.align_to(labels[1][0][1], DOWN)

        num_foxes.add_updater(lambda d: d.set_value(get_num_foxes()))
        num_rabbits.add_updater(lambda d: d.set_value(get_num_rabbits()))

        self.add(num_foxes, num_rabbits)

        for count in num_foxes, num_rabbits:
            self.add(Mobject.add_updater(
                count, self.update_count_color,
            ))

        self.play(
            FadeIn(labels),
            *[
                UpdateFromAlphaFunc(count, lambda m, a: m.set_fill(opacity=a))
                for count in (num_foxes, num_rabbits)
            ]
        )

        self.wait(self.final_wait_time)

    # Helpers

    def get_animal(self, name, color):
        result = SVGMobject(
            file_name=name,
            height=self.animal_height,
            fill_color=color,
        )
        # for submob in result.family_members_with_points():
            # if submob.is_subpath:
            #     submob.is_subpath = False
            #     submob.set_fill(
            #         interpolate_color(color, BLACK, 0.8),
            #         opacity=1
            #     )
        x_shift, y_shift = [
            (2 * random.random() - 1) * max_val
            for max_val in [
                FRAME_WIDTH / 2 - 2,
                FRAME_HEIGHT / 2 - 2
            ]
        ]
        result.shift(x_shift * RIGHT + y_shift * UP)
        return result

    def get_fox(self):
        return self.get_animal("fox", FOX_COLOR)

    def get_rabbit(self):
        # return self.get_animal("rabbit", WHITE)
        return self.get_animal("bunny", RABBIT_COLOR)

    def get_pop_labels(self):
        labels = VGroup(
            TextMobject("\\# Foxes: "),
            TextMobject("\\# Rabbits: "),
        )
        for label in labels:
            label.scale(self.count_word_scale_val)
        labels.arrange(RIGHT, buff=2)
        labels.to_edge(UP)
        return labels

    def update_count_color(self, count):
        count.set_fill(interpolate_color(
            BLUE, RED, (count.number - 20) / 30.0
        ))
        return count


class PhaseSpaceOfPopulationModel(ShowTwoPopulations, PiCreatureScene, MovingCameraScene):
    CONFIG = {
        "origin": 5 * LEFT + 2.5 * DOWN,
        "vector_field_config": {
            "max_magnitude": 50,
        },
        "pi_creatures_start_on_screen": False,
        "default_pi_creature_kwargs": {
            "height": 1.8
        },
        "flow_time": 10,
    }

    def setup(self):
        MovingCameraScene.setup(self)
        PiCreatureScene.setup(self)

    def construct(self):
        self.add_axes()
        self.add_example_point()
        self.write_differential_equations()
        self.add_vectors()
        self.show_phase_flow()

    def add_axes(self):
        axes = self.axes = Axes(
            x_min=0,
            x_max=55,
            x_axis_config={"unit_size": 0.15},
            y_min=0,
            y_max=55,
            y_axis_config={"unit_size": 0.09},
            axis_config={
                "tick_frequency": 10,
            },
        )
        axes.shift(self.origin)
        for axis in axes.x_axis, axes.y_axis:
            axis.add_numbers(*list(range(10, 60, 10)))

        axes_labels = self.axes_labels = VGroup(*[
            VGroup(
                method().set_height(0.75),
                TextMobject("Population"),
            ).arrange(RIGHT, buff=MED_SMALL_BUFF)
            for method in (self.get_rabbit, self.get_fox)
        ])
        for axis, label, vect in zip(axes, axes_labels, [RIGHT, UP]):
            label.next_to(
                axis, vect,
                submobject_to_align=label[0]
            )

        self.add(axes, axes_labels)

    def add_example_point(self):
        axes = self.axes
        origin = self.origin
        x = self.start_num_rabbits
        y = self.start_num_foxes
        point = axes.coords_to_point(x, y)
        x_point = axes.coords_to_point(x, 0)
        y_point = axes.coords_to_point(0, y)
        v_line = DashedLine(x_point, point)
        h_line = DashedLine(y_point, point)
        v_line.set_color(FOX_COLOR)
        h_line.set_color(LIGHT_GREY)
        dot = Dot(point)

        coord_pair = TexMobject(
            "(10, 10)", substrings_to_isolate=["10"]
        )
        pop_sizes = VGroup(Integer(10), Integer(10))
        pop_sizes[0].set_color(LIGHT_GREY)
        pop_sizes[1].set_color(FOX_COLOR)
        tens = coord_pair.get_parts_by_tex("10")
        tens.fade(1)

        def get_pop_size_update(i):
            return ContinualChangingDecimal(
                pop_sizes[i],
                lambda a: int(np.round(
                    axes.point_to_coords(dot.get_center())[i]
                )),
                position_update_func=lambda m: m.move_to(tens[i])
            )
        coord_pair.add_background_rectangle()
        coord_pair_update = Mobject.add_updater(
            coord_pair, lambda m: m.next_to(dot, UR, SMALL_BUFF)
        )
        pop_sizes_updates = [get_pop_size_update(i) for i in (0, 1)]

        phase_space = TextMobject("``Phase space''")
        phase_space.set_color(YELLOW)
        phase_space.scale(1.5)
        phase_space.to_edge(UP)
        phase_space.shift(2 * RIGHT)

        self.play(ShowCreation(v_line))
        self.play(ShowCreation(h_line))
        dot.save_state()
        dot.move_to(origin)
        self.add(coord_pair_update)
        self.add(*pop_sizes_updates)
        self.play(
            dot.restore,
            VFadeIn(coord_pair),
            UpdateFromAlphaFunc(pop_sizes, lambda m, a: m.set_fill(opacity=a)),
        )
        self.wait()
        self.play(Write(phase_space))
        self.wait(2)
        self.play(FadeOut(VGroup(h_line, v_line, phase_space)))
        self.play(Rotating(
            dot,
            about_point=axes.coords_to_point(30, 30),
            rate_func=smooth,
        ))

        self.dot = dot
        self.coord_pair = coord_pair
        self.coord_pair_update = coord_pair_update
        self.pop_sizes = pop_sizes
        self.pop_sizes_updates = pop_sizes_updates

    def write_differential_equations(self):
        equations = self.get_equations()
        equations.shift(2 * DOWN)
        rect = SurroundingRectangle(equations, color=YELLOW)
        rect.set_fill(BLACK, 0.8)
        title = TextMobject("Differential equations")
        title.next_to(rect, UP)
        title.set_color(rect.get_stroke_color())
        self.differential_equation_group = VGroup(
            rect, equations, title
        )
        self.differential_equation_group.to_corner(UR)

        randy = self.pi_creature
        randy.next_to(rect, DL)

        self.play(
            Write(title, run_time=1),
            ShowCreation(rect)
        )
        self.play(
            LaggedStartMap(FadeIn, equations),
            randy.change, "confused", equations,
            VFadeIn(randy),
        )
        self.wait(3)

    def add_vectors(self):
        origin = self.axes.coords_to_point(0, 0)
        dot = self.dot
        randy = self.pi_creature

        def rescaled_field(point):
            x, y = self.axes.point_to_coords(point)
            result = preditor_prey_vector_field(np.array([x, y, 0]))
            return self.axes.coords_to_point(*result[:2]) - origin

        self.vector_field_config.update({
            "x_min": origin[0] + 0.5,
            "x_max": self.axes.get_right()[0] + 1,
            "y_min": origin[1] + 0.5,
            "y_max": self.axes.get_top()[1],
        })
        vector_field = VectorField(
            rescaled_field, **self.vector_field_config
        )

        def get_dot_vector():
            vector = vector_field.get_vector(dot.get_center())
            vector.scale(1, about_point=vector.get_start())
            return vector

        dot_vector = get_dot_vector()

        self.play(
            LaggedStartMap(GrowArrow, vector_field),
            randy.change, "thinking", dot,
            Animation(self.differential_equation_group)
        )
        self.wait(3)
        self.play(
            Animation(dot),
            vector_field.set_fill, {"opacity": 0.2},
            Animation(self.differential_equation_group),
            GrowArrow(dot_vector),
            randy.change, "pondering",
        )
        self.wait()
        self.play(
            dot.move_to, dot_vector.get_end(),
            dot.align_to, dot, RIGHT,
            run_time=3,
        )
        self.wait(2)
        self.play(
            dot.move_to, dot_vector.get_end(),
            run_time=3,
        )
        self.wait(2)
        for x in range(6):
            new_dot_vector = get_dot_vector()
            fade_anims = [
                FadeOut(dot_vector),
                FadeIn(new_dot_vector),
                Animation(dot),
            ]
            if x == 4:
                fade_anims += [
                    vector_field.set_fill, {"opacity": 0.5},
                    FadeOut(randy),
                    FadeOut(self.differential_equation_group),
                ]
            self.play(*fade_anims)
            dot_vector = new_dot_vector
            self.play(dot.move_to, dot_vector.get_end())

        dot_movement = move_along_vector_field(
            dot, lambda p: 0.3 * vector_field.func(p)
        )
        self.add(dot_movement)
        self.play(FadeOut(dot_vector))
        self.wait(10)
        self.play(
            vector_field.set_fill, {"opacity": 1.0},
            VFadeOut(dot),
            VFadeOut(self.coord_pair),
            UpdateFromAlphaFunc(self.pop_sizes, lambda m, a: m.set_fill(opacity=1 - a)),
        )
        self.remove(
            dot_movement,
            self.coord_pair_update,
            *self.pop_sizes_updates
        )
        self.wait()

        self.vector_field = vector_field

    def show_phase_flow(self):
        vector_field = self.vector_field
        stream_lines = StreamLines(
            vector_field.func,
            start_points_generator_config={
                "x_min": vector_field.x_min,
                "x_max": vector_field.x_max,
                "y_min": vector_field.y_min,
                "y_max": vector_field.y_max,
                "delta_x": 0.25,
                "delta_y": 0.25,
            },
            min_magnitude=vector_field.min_magnitude,
            max_magnitude=vector_field.max_magnitude,
            virtual_time=4,
        )
        stream_line_animation = AnimatedStreamLines(
            stream_lines,
        )
        self.add(stream_line_animation)
        self.add_foreground_mobjects(vector_field)
        self.wait(self.flow_time)
        self.play(
            self.camera_frame.scale, 1.5, {"about_point": self.origin},
            run_time=self.flow_time,
        )
        self.wait(self.flow_time)

    #
    def get_equations(self):
        variables = ["X", "YY"]
        equations = TexMobject(
            """
                {dX \\over dt} =
                X \\cdot (\\alpha - \\beta YY \\,) \\\\
                \\quad \\\\
                {dYY \\over dt} =
                YY \\cdot (\\delta X - \\gamma)
            """,
            substrings_to_isolate=variables
        )
        animals = [self.get_rabbit(), self.get_fox().flip()]
        for char, animal in zip(variables, animals):
            for part in equations.get_parts_by_tex(char):
                animal_copy = animal.copy()
                animal_copy.set_height(0.5)
                animal_copy.move_to(part, DL)
                part.become(animal_copy)
        return equations


class PhaseFlowWords(Scene):
    def construct(self):
        words = TextMobject("``Phase flow''")
        words.scale(2)
        self.play(Write(words))
        self.wait()


class PhaseFlowQuestions(Scene):
    def construct(self):
        questions = VGroup(
            TextMobject(
                "Which points does the flow \\\\" +
                "converge to?  Diverge away from?",
            ),
            TextMobject("Where are there cycles?"),
        )
        questions.arrange(DOWN, buff=LARGE_BUFF)
        questions.to_corner(UR)
        for question in questions:
            self.play(FadeInFromDown(question))
            self.wait(2)


class ToolsBeyondDivAndCurlForODEs(PiCreatureScene):
    CONFIG = {
        "default_pi_creature_kwargs": {
            "color": GREY_BROWN,
        },
        "default_pi_creature_start_corner": DOWN,
    }

    def construct(self):
        morty = self.pi_creature
        div_curl = TextMobject("div \\\\", "curl")
        div_curl.set_color_by_tex("div", BLUE)
        div_curl.set_color_by_tex("curl", YELLOW)
        div_curl.next_to(morty.get_corner(UL), UP, MED_LARGE_BUFF)

        jacobian = TextMobject("Analyze the \\\\ Jacobian")
        jacobian.set_color(GREEN)
        jacobian.next_to(morty.get_corner(UR), UP, MED_LARGE_BUFF)

        flow_intuitions = TextMobject("Flow-based intuitions")
        flow_intuitions.next_to(
            VGroup(div_curl, jacobian),
            UP, buff=1.5
        )
        arrow1 = Arrow(div_curl.get_top(), flow_intuitions.get_bottom())
        arrow2 = Arrow(flow_intuitions.get_bottom(), jacobian.get_top())

        self.play(
            FadeInFromDown(div_curl),
            morty.change, "raise_left_hand",
        )
        self.wait()
        self.play(
            FadeInFromDown(jacobian),
            morty.change, "raise_right_hand"
        )
        self.wait()
        self.play(
            ReplacementTransform(
                flow_intuitions.copy().fade(1).move_to(div_curl),
                flow_intuitions,
            ),
            GrowArrow(arrow1),
            morty.change, "pondering"
        )
        self.wait(0.5)
        self.play(GrowArrow(arrow2))
        self.wait()


class AskAboutComputation(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Sure, but how do you \\\\" +
            "\\emph{compute} $\\textbf{div}$ and $\\textbf{curl}$?",
            target_mode="sassy",
        )
        self.change_student_modes(
            "confused", "sassy", "angry",
            added_anims=[self.teacher.change, "guilty"]
        )
        self.wait()
        self.teacher_says(
            "Are you familiar \\\\" +
            "with my work \\\\" +
            "at Khan Academy?",
            target_mode="speaking",
            bubble_kwargs={"width": 4, "height": 3}
        )
        self.change_student_modes(
            * 3 * ["pondering"],
            look_at_arg=self.screen
        )
        self.wait(5)


class QuickWordsOnNotation(Scene):
    def construct(self):
        words = TextMobject("Quick words on notation:")
        words.scale(1.5)
        self.play(FadeInFromDown(words))
        self.wait()


class NablaNotation(PiCreatureScene, MovingCameraScene):
    CONFIG = {
        "default_pi_creature_kwargs": {
            "color": GREY_BROWN,
        },
        "default_pi_creature_start_corner": DL,
    }

    def setup(self):
        MovingCameraScene.setup(self)
        PiCreatureScene.setup(self)

    def construct(self):
        self.show_notation()
        self.show_expansion()
        self.zoom_out()

    def show_notation(self):
        morty = self.pi_creature

        tex_to_color_map = {
            "\\text{div}": BLUE,
            "\\nabla \\cdot": BLUE,
            "\\text{curl}": YELLOW,
            "\\nabla \\times": YELLOW,
        }
        div_equation = TexMobject(
            "\\text{div} \\, \\textbf{F} = \\nabla \\cdot \\textbf{F}",
            tex_to_color_map=tex_to_color_map
        )
        div_nabla = div_equation.get_part_by_tex("\\nabla")
        curl_equation = TexMobject(
            "\\text{curl} \\, \\textbf{F} = \\nabla \\times \\textbf{F}",
            tex_to_color_map=tex_to_color_map
        )
        curl_nabla = curl_equation.get_part_by_tex("\\nabla")
        equations = VGroup(div_equation, curl_equation)
        equations.arrange(DOWN, buff=LARGE_BUFF)
        equations.next_to(morty, UP, 2)
        equations.to_edge(LEFT)

        self.play(
            FadeInFromDown(div_equation),
            morty.change, "raise_right_hand"
        )
        self.wait()
        self.play(WiggleOutThenIn(div_nabla, scale_value=1.5))
        self.wait()
        self.play(
            FadeInFromDown(curl_equation),
            morty.change, "raise_left_hand"
        )
        self.wait()
        self.play(WiggleOutThenIn(curl_nabla, scale_value=1.5))
        self.wait()

        self.equations = equations

    def show_expansion(self):
        equations = self.equations
        morty = self.pi_creature

        nabla_vector = Matrix([
            ["\\partial \\over \\partial x"],
            ["\\partial \\over \\partial y"],
        ], v_buff=1.5)
        F_vector = Matrix([
            ["\\textbf{F}_x"],
            ["\\textbf{F}_y"],
        ], v_buff=1.2)
        nabla_vector.match_height(F_vector)

        div_lhs, curl_lhs = lhs_groups = VGroup(*[
            VGroup(
                nabla_vector.deepcopy(),
                TexMobject(tex).scale(1.5),
                F_vector.copy(),
                TexMobject("=")
            )
            for tex in ("\\cdot", "\\times")
        ])
        colors = [BLUE, YELLOW]
        for lhs, color in zip(lhs_groups, colors):
            lhs.arrange(RIGHT, buff=MED_SMALL_BUFF)
            VGroup(lhs[0].brackets, lhs[1]).set_color(color)
        div_lhs.to_edge(UP)
        curl_lhs.next_to(div_lhs, DOWN, buff=LARGE_BUFF)

        div_rhs = TexMobject(
            "{\\partial F_x \\over \\partial x} + " +
            "{\\partial F_y \\over \\partial y}"
        )
        curl_rhs = TexMobject(
            "{\\partial F_y \\over \\partial x} - " +
            "{\\partial F_x \\over \\partial y}"
        )
        rhs_groups = VGroup(div_rhs, curl_rhs)
        for rhs, lhs in zip(rhs_groups, lhs_groups):
            rhs.next_to(lhs, RIGHT)

        for rhs, tex, color in zip(rhs_groups, ["div", "curl"], colors):
            rhs.rect = SurroundingRectangle(rhs, color=color)
            rhs.label = TexMobject(
                "\\text{%s}" % tex,
                "\\, \\textbf{F}"
            )
            rhs.label.set_color(color)
            rhs.label.next_to(rhs.rect, UP)

        for i in 0, 1:
            self.play(
                ReplacementTransform(
                    equations[i][2].copy(),
                    lhs_groups[i][0].brackets
                ),
                ReplacementTransform(
                    equations[i][3].copy(),
                    lhs_groups[i][2],
                ),
                morty.change, "pondering",
                *[
                    GrowFromPoint(mob, equations[i].get_right())
                    for mob in [
                        lhs_groups[i][0].get_entries(),
                        lhs_groups[i][1],
                        lhs_groups[i][3]
                    ]
                ],
                run_time=2
            )
            self.wait()
        self.wait()
        for rhs in rhs_groups:
            self.play(
                Write(rhs),
                morty.change, 'confused'
            )
            self.play(
                ShowCreation(rhs.rect),
                FadeInFromDown(rhs.label),
            )
            self.wait()
        self.play(morty.change, "erm")
        self.wait(3)

    def zoom_out(self):
        screen_rect = self.camera_frame.copy()
        screen_rect.set_stroke(WHITE, 3)
        screen_rect.scale(1.01)
        words = TextMobject("Something deeper at play...")
        words.scale(1.3)
        words.next_to(screen_rect, UP)

        self.add(screen_rect)
        self.play(
            self.camera_frame.set_height, FRAME_HEIGHT + 3,
            Write(words, rate_func=squish_rate_func(smooth, 0.3, 1)),
            run_time=2,
        )
        self.wait()


class DivCurlDotCross(Scene):
    def construct(self):
        rects = VGroup(*[
            ScreenRectangle(height=2.5)
            for n in range(4)
        ])
        rects.arrange_in_grid(n_rows=2, buff=LARGE_BUFF)
        rects[2:].shift(MED_LARGE_BUFF * DOWN)
        titles = VGroup(*list(map(TextMobject, [
            "Divergence", "Curl",
            "Dot product", "Cross product"
        ])))
        for title, rect in zip(titles, rects):
            title.next_to(rect, UP)

        self.add(rects, titles)


class ShowDotProduct(MovingCameraScene):
    CONFIG = {
        "prod_tex": "\\cdot"
    }

    def construct(self):
        plane = NumberPlane()
        v1 = Vector(RIGHT, color=BLUE)
        v2 = Vector(UP, color=YELLOW)

        dot_product = TexMobject(
            "\\vec{\\textbf{v}}", self.prod_tex,
            "\\vec{\\textbf{w}}", "="
        )
        dot_product.set_color_by_tex_to_color_map({
            "textbf{v}": BLUE,
            "textbf{w}": YELLOW,
        })
        dot_product.add_background_rectangle()
        dot_product.next_to(2.25 * UP, RIGHT)
        dot_product_value = DecimalNumber(
            1.0,
            include_background_rectangle=True,
        )
        dot_product_value.next_to(dot_product)
        dot_product_value_update = ContinualChangingDecimal(
            dot_product_value,
            lambda a: self.get_product(v1, v2),
            include_background_rectangle=True,
        )

        self.camera_frame.set_height(4)
        self.camera_frame.move_to(DL, DL)
        self.add(plane)
        self.add(dot_product, dot_product_value_update)
        self.add_additional_continual_animations(v1, v2)
        self.add_foreground_mobjects(v1, v2)
        for n in range(5):
            self.play(
                Rotate(v1, 45 * DEGREES, about_point=ORIGIN),
                Rotate(v2, -45 * DEGREES, about_point=ORIGIN),
                run_time=3,
                rate_func=there_and_back
            )
            self.wait(0.5)

    def get_product(self, v1, v2):
        return np.dot(v1.get_vector(), v2.get_vector())

    def add_additional_continual_animations(self, v1, v2):
        pass


class ShowCrossProduct(ShowDotProduct):
    CONFIG = {
        "prod_tex": "\\times"
    }

    def get_product(self, v1, v2):
        return get_norm(
            np.cross(v1.get_vector(), v2.get_vector())
        )

    def add_additional_continual_animations(self, v1, v2):
        square = Square(
            stroke_color=YELLOW,
            stroke_width=3,
            fill_color=YELLOW,
            fill_opacity=0.2,
        )

        self.add(Mobject.add_updater(
            square,
            lambda s: s.set_points_as_corners([
                ORIGIN,
                v1.get_end(),
                v1.get_end() + v2.get_end(),
                v2.get_end(),
            ])
        ))


class DivergenceTinyNudgesView(MovingCameraScene):
    CONFIG = {
        "scale_factor": 0.25,
        "point": ORIGIN,
    }

    def construct(self):
        self.add_vector_field()
        self.zoom_in()
        self.take_tiny_step()
        self.show_dot_product()
        self.show_circle_of_values()
        self.switch_to_curl_words()
        self.rotate_difference_vectors()

    def add_vector_field(self):
        plane = self.plane = NumberPlane()

        def func(p):
            x, y = p[:2]
            result = np.array([
                np.sin(x + 0.1),
                np.cos(2 * y),
                0
            ])
            result /= (get_norm(result)**0.5 + 1)
            return result

        vector_field = self.vector_field = VectorField(
            func,
            length_func=lambda n: 0.5 * sigmoid(n),
            # max_magnitude=1.0,
        )
        self.add(plane)
        self.add(vector_field)

    def zoom_in(self):
        point = self.point
        vector_field = self.vector_field
        sf = self.scale_factor

        vector_field.vector_config.update({
            "rectangular_stem_width": 0.02,
            "tip_length": 0.1,
        })
        vector_field.length_func = lambda n: n
        vector = vector_field.get_vector(point)

        input_dot = Dot(point).scale(sf)
        input_words = TextMobject("$(x_0, y_0)$").scale(sf)
        input_words.next_to(input_dot, DL, SMALL_BUFF * sf)
        output_words = TextMobject("Output").scale(sf)
        output_words.add_background_rectangle()
        output_words.next_to(vector.get_top(), UP, sf * SMALL_BUFF)
        output_words.match_color(vector)

        self.play(
            self.camera_frame.scale, sf,
            self.camera_frame.move_to, point,
            FadeOut(vector_field),
            FadeIn(vector),
            run_time=2
        )
        self.add_foreground_mobjects(input_dot)
        self.play(
            FadeInFrom(input_dot, SMALL_BUFF * DL),
            Write(input_words),
        )
        self.play(
            Indicate(vector),
            Write(output_words),
        )
        self.wait()

        self.set_variables_as_attrs(
            point, vector, input_dot,
            input_words, output_words,
        )

    def take_tiny_step(self):
        sf = self.scale_factor
        vector_field = self.vector_field
        point = self.point
        vector = self.vector
        output_words = self.output_words
        input_dot = self.input_dot

        nudge = 0.5 * RIGHT
        nudged_point = point + nudge

        new_vector = vector_field.get_vector(nudged_point)
        new_vector.set_color(YELLOW)
        new_dot = Dot(nudged_point).scale(sf)
        step_vector = Arrow(
            point, nudged_point,
            buff=0,
            color=TEAL,
            **vector_field.vector_config
        )
        step_vector.set_stroke(BLACK, 0.5)

        new_output_words = TextMobject("New output").scale(sf)
        new_output_words.add_background_rectangle()
        new_output_words.next_to(new_vector.get_end(), UP, sf * SMALL_BUFF)
        new_output_words.match_color(new_vector)
        step_words = TextMobject("Step").scale(sf)
        step_words.next_to(step_vector, UP, buff=0)
        step_words.set_color(step_vector.get_fill_color())
        step_words.add_background_rectangle()
        small_step_words = TextMobject("(think tiny step)").scale(sf)
        small_step_words.next_to(
            step_words, RIGHT,
            buff=sf * MED_SMALL_BUFF,
        )
        small_step_words.add_background_rectangle()
        small_step_words.match_style(step_words)

        shifted_vector = vector.copy().shift(nudge)
        diff_vector = Arrow(
            shifted_vector.get_end(),
            new_vector.get_end(),
            buff=0,
            color=RED,
            **vector_field.vector_config
        )
        diff_words = TextMobject("Difference").scale(sf)
        diff_words.add_background_rectangle()
        diff_words.next_to(diff_vector.get_start(), UR, buff=2 * sf * SMALL_BUFF)
        diff_words.match_color(diff_vector)
        diff_words.rotate(
            diff_vector.get_angle(),
            about_point=diff_vector.get_start()
        )

        self.play(
            GrowArrow(step_vector),
            Write(step_words),
            ReplacementTransform(input_dot.copy(), new_dot)
        )
        self.add_foreground_mobjects(new_dot)
        self.play(FadeIn(small_step_words))
        self.play(FadeOut(small_step_words))
        self.play(
            ReplacementTransform(vector.copy(), new_vector),
            ReplacementTransform(output_words.copy(), new_output_words),
        )
        self.wait()
        self.play(ReplacementTransform(
            vector.copy(), shifted_vector,
            path_arc=-TAU / 4
        ))
        self.wait()
        self.play(
            FadeOut(output_words),
            FadeOut(new_output_words),
            GrowArrow(diff_vector),
            Write(diff_words)
        )
        self.wait()
        self.play(
            vector.scale, 0, {"about_point": vector.get_start()},
            shifted_vector.scale, 0, {"about_point": shifted_vector.get_start()},
            ReplacementTransform(
                new_vector,
                diff_vector.copy().shift(-vector.get_vector()),
                remover=True
            ),
            diff_vector.shift, -vector.get_vector(),
            MaintainPositionRelativeTo(diff_words, diff_vector),
            run_time=2
        )
        self.wait()

        self.set_variables_as_attrs(
            step_vector, step_words,
            diff_vector, diff_words,
        )

    def show_dot_product(self):
        sf = self.scale_factor
        point = self.point
        step_vector = self.step_vector
        step_words = self.step_words
        diff_vector = self.diff_vector
        diff_words = self.diff_words
        vects = VGroup(step_vector, diff_vector)

        moving_step_vector = step_vector.copy()
        moving_diff_vector = diff_vector.copy()

        def update_moving_diff_vector(dv):
            step = moving_step_vector.get_vector()
            o1 = self.vector_field.get_vector(point).get_vector()
            o2 = self.vector_field.get_vector(point + step).get_vector()
            diff = o2 - o1
            dv.put_start_and_end_on(
                moving_step_vector.get_end(),
                moving_step_vector.get_end() + diff,
            )
        self.moving_diff_vector_update = Mobject.add_updater(
            moving_diff_vector,
            update_moving_diff_vector
        )
        self.add(self.moving_diff_vector_update)

        div_text = self.get_operator_text("div")

        step_words_copy = step_words.copy()
        diff_words_copy = diff_words.copy()
        copies = VGroup(step_words_copy, diff_words_copy)

        substrings = ["Step", "Difference"]
        dot_product = TextMobject(
            "(Step) $\\cdot$ (Difference)",
            substrings_to_isolate=substrings,
            arg_separator="",
        ).scale(sf)
        group = VGroup(div_text, dot_product)
        group.arrange(RIGHT, buff=sf * MED_SMALL_BUFF)
        group.next_to(
            self.camera_frame.get_top(), DOWN,
            buff=sf * MED_SMALL_BUFF
        )

        for substring, mob, vect in zip(substrings, copies, vects):
            part = dot_product.get_part_by_tex(substring)
            mob.generate_target()
            mob.target.rotate(-vect.get_angle())
            mob.target.replace(part)
            # part.set_fill(opacity=0)
            part.match_color(mob)
        dot_product.add_background_rectangle()

        brace = Brace(
            dot_product.copy().scale(1 / sf, about_point=ORIGIN), DOWN,
            buff=SMALL_BUFF
        ).scale(sf, about_point=ORIGIN)
        dp_kwargs = {
            "include_sign": True,
        }
        dot_product_value = DecimalNumber(1.0, **dp_kwargs)
        dot_product_value.scale(sf)
        dot_product_value.next_to(brace, DOWN, sf * SMALL_BUFF)
        dot_product_value_update = ContinualChangingDecimal(
            dot_product_value,
            lambda a: np.dot(
                moving_step_vector.get_vector(),
                moving_diff_vector.get_vector(),
            ),
            **dp_kwargs
        )

        self.play(
            Write(dot_product),
            LaggedStartMap(MoveToTarget, copies)
        )
        self.remove(copies)
        self.play(FadeIn(div_text))
        self.play(ShowPassingFlashAround(
            div_text[1:3],
            surrounding_rectangle_config={"buff": sf * SMALL_BUFF}
        ))
        self.add(BackgroundRectangle(dot_product_value))
        self.play(
            GrowFromCenter(brace),
            Write(dot_product_value),
        )
        self.add(dot_product_value_update)
        self.wait()

        self.set_variables_as_attrs(
            div_text, dot_product,
            moving_step_vector,
            moving_diff_vector,
            dot_product_value,
            dot_product_value_update,
            brace,
        )

    def show_circle_of_values(self):
        point = self.point
        moving_step_vector = self.moving_step_vector
        moving_diff_vector = self.moving_diff_vector

        all_diff_vectors = VGroup()
        all_step_vectors = VGroup()
        # Loop around
        n_samples = 12
        angle = TAU / n_samples
        self.add_foreground_mobjects(self.step_words)
        for n in range(n_samples):
            self.play(
                Rotating(
                    moving_step_vector,
                    radians=angle,
                    about_point=point,
                    run_time=15.0 / n_samples,
                    rate_func=linear,
                )
            )
            step_vector_copy = moving_step_vector.copy()
            diff_vector_copy = moving_diff_vector.copy()
            diff_vector_copy.set_stroke(BLACK, 0.5)
            self.add(step_vector_copy, diff_vector_copy)
            all_step_vectors.add(step_vector_copy)
            all_diff_vectors.add(diff_vector_copy)
        self.remove(
            self.step_vector, self.diff_vector,
            self.moving_step_vector, self.moving_diff_vector,
            self.moving_diff_vector_update,
            self.dot_product_value_update
        )
        self.remove_foreground_mobjects(self.step_words)
        self.play(
            FadeOut(self.brace),
            FadeOut(self.dot_product_value),
            FadeOut(self.step_words),
            FadeOut(self.diff_words),
        )
        self.wait()

        for s in 0.6, -0.6:
            for step, diff in zip(all_step_vectors, all_diff_vectors):
                diff.generate_target()
                diff.target.put_start_and_end_on(
                    step.get_end(),
                    step.get_end() + s * step.get_vector()
                )
            self.play(
                all_step_vectors.set_fill, {"opacity": 0.5},
                LaggedStartMap(
                    MoveToTarget, all_diff_vectors,
                    run_time=3
                ),
            )
            self.wait()
            self.show_stream_lines(lambda p: s * (p - point))
            self.wait()

        self.set_variables_as_attrs(
            all_step_vectors, all_diff_vectors,
        )

    def switch_to_curl_words(self):
        sf = self.scale_factor
        div_text = self.div_text
        dot_product = self.dot_product

        curl_text = self.get_operator_text("curl")
        cross_product = TextMobject(
            "(Step) $\\times$ (Difference)",
            tex_to_color_map={
                "Step": TEAL,
                "Difference": RED
            },
            arg_separator="",
        ).scale(sf)
        cross_product.add_background_rectangle(opacity=1)

        group = VGroup(curl_text, cross_product)
        group.arrange(RIGHT, buff=sf * MED_SMALL_BUFF)
        group.next_to(self.camera_frame.get_top(), sf * DOWN)

        self.play(
            dot_product.shift, sf * DOWN,
            dot_product.fade, 1,
            remover=True
        )
        self.play(FadeInFrom(cross_product, sf * DOWN))
        self.play(
            div_text.shift, sf * DOWN,
            div_text.fade, 1,
            remover=True
        )
        self.play(FadeInFrom(curl_text, sf * DOWN))
        self.wait()

    def rotate_difference_vectors(self):
        point = self.point
        all_step_vectors = self.all_step_vectors
        all_diff_vectors = self.all_diff_vectors

        for s in 0.6, -0.6:
            for step, diff in zip(all_step_vectors, all_diff_vectors):
                diff.generate_target()
                diff.target.put_start_and_end_on(
                    step.get_end(),
                    step.get_end() + s * rotate_vector(
                        step.get_vector(),
                        90 * DEGREES
                    )
                )
            self.play(
                LaggedStartMap(
                    MoveToTarget, all_diff_vectors,
                    run_time=2
                ),
            )
            self.wait()
            self.show_stream_lines(
                lambda p: s * rotate_vector((p - point), 90 * DEGREES)
            )
            self.wait()

        self.set_variables_as_attrs(
            all_step_vectors, all_diff_vectors,
        )

    # Helpers

    def get_operator_text(self, operator):
        text = TextMobject(
            operator + "\\,",
            "$\\textbf{F}(x_0, y_0)\\,$",
            "corresponds to average of",
            arg_separator=""
        ).scale(self.scale_factor)
        text.set_color_by_tex(operator, YELLOW)
        text.add_background_rectangle()
        return text

    def show_stream_lines(self, func):
        point = self.point
        stream_lines = StreamLines(
            func,
            start_points_generator_config={
                "x_min": point[0] - 2,
                "x_max": point[0] + 2,
                "y_min": point[1] - 1,
                "y_max": point[1] + 1,
                "delta_x": 0.025,
                "delta_y": 0.025,
            },
            virtual_time=1,
        )
        random.shuffle(stream_lines.submobjects)
        self.play(LaggedStartMap(
            ShowPassingFlash,
            stream_lines,
            run_time=4,
        ))


class ZToHalfFlowNearWall(ComplexTransformationScene, MovingCameraScene):
    CONFIG = {
        "num_anchors_to_add_per_line": 200,
        "plane_config": {"y_radius": 8}
    }

    def setup(self):
        MovingCameraScene.setup(self)
        ComplexTransformationScene.setup(self)

    def construct(self):
        # self.camera.frame.shift(2 * UP)
        self.camera.frame.scale(0.5, about_point=ORIGIN)

        plane = NumberPlane(
            x_radius=15,
            y_radius=25,
            y_unit_size=0.5,
            secondary_line_ratio=0,
        )
        plane.next_to(ORIGIN, UP, buff=0.001)
        horizontal_lines = VGroup(*[l for l in list(planes) + [plane.axes[0]] if np.abs(l.get_center()[0]) < 0.1])
        plane.set_stroke(MAROON_B, width=2)
        horizontal_lines.set_stroke(BLUE, width=2)

        self.prepare_for_transformation(plane)
        self.add_transformable_mobjects(plane)

        self.background.set_stroke(width=2)
        for label in self.background.coordinate_labels:
            label.set_stroke(width=0)
            label.scale(0.75, about_edge=UR)

        words = TextMobject("(Idealized) Flow \\\\", "near a wall")
        words.scale(0.75)
        words.add_background_rectangle_to_submobjects()
        words.next_to(0.75 * UP, LEFT, MED_LARGE_BUFF)
        equation = TexMobject("z \\rightarrow z^{1/2}")
        equation.scale(0.75)
        equation.add_background_rectangle()
        equation.next_to(words, UP)

        self.apply_complex_function(
            lambda x: x**(1. / 2),
            added_anims=[Write(equation)]
        )
        self.play(Write(words, run_time=1))

        def func(point):
            z = R3_to_complex(point)
            d_half = derivative(lambda z: z**2)
            return complex_to_R3(d_half(z).conjugate())

        stream_lines = StreamLines(
            func,
            start_points_generator_config={
                "x_min": 0.01,
                "y_min": 0.01,
                "delta_x": 0.125,
                "delta_y": 0.125,
            },
            virtual_time=3,
            stroke_width=2,
            max_magnitude=10,
        )
        stream_line_animation = AnimatedStreamLines(stream_lines)

        self.add(stream_line_animation)
        self.wait(7)


class IncmpressibleAndIrrotational(Scene):
    def construct(self):
        div_0 = TextMobject("div$\\textbf{F} = 0$")
        curl_0 = TextMobject("curl$\\textbf{F}$ = 0")
        incompressible = TextMobject("Incompressible")
        irrotational = TextMobject("Irrotational")

        for text in [div_0, curl_0, incompressible, irrotational]:
            self.stylize_word_for_background(text)

        div_0.to_edge(UP)
        curl_0.next_to(div_0, DOWN, MED_LARGE_BUFF)

        for op, word in (div_0, incompressible), (curl_0, irrotational):
            op.generate_target()
            group = VGroup(op.target, word)
            group.arrange(RIGHT, buff=MED_LARGE_BUFF)
            group.move_to(op)

        self.play(FadeInFromDown(div_0))
        self.play(FadeInFromDown(curl_0))
        self.wait()
        self.play(
            MoveToTarget(div_0),
            FadeInFromDown(incompressible),
        )
        self.wait()
        self.play(
            MoveToTarget(curl_0),
            FadeInFromDown(irrotational),
        )
        self.wait()

        rect = SurroundingRectangle(VGroup(curl_0, irrotational))
        question = TextMobject("Does this actually happen?")
        question.next_to(rect, DOWN)
        question.match_color(rect)
        self.stylize_word_for_background(question)

        self.play(ShowCreation(rect))
        self.play(Write(question))
        self.wait()

    def stylize_word_for_background(self, word):
        word.add_background_rectangle()


class NoChargesOverlay(Scene):
    def construct(self):
        rect = FullScreenFadeRectangle()
        rect.set_fill(BLUE_D, 0.75)
        circle = Circle(radius=1.5, num_anchors=5000)
        circle.rotate(135 * DEGREES)
        rect.add_subpath(circle.points)

        words = TextMobject("No charges outside wire")
        words.scale(1.5)
        words.to_edge(UP)

        self.add(rect, words)


# End message
class BroughtToYouBy(PiCreatureScene):
    CONFIG = {
        "pi_creatures_start_on_screen": False,
    }

    def construct(self):
        self.brought_to_you_by()
        self.just_you_and_me()

    def brought_to_you_by(self):
        so_words = TextMobject("So", "...", arg_separator="")
        so_words.scale(2)

        btyb = TextMobject("Brought to you", "by")
        btyb.scale(1.5)
        btyb_line = Line(LEFT, RIGHT)
        btyb_line.next_to(btyb, RIGHT, SMALL_BUFF)
        btyb_line.align_to(btyb[0], DOWN)
        btyb_group = VGroup(btyb, btyb_line)
        btyb_group.center()

        you_word = TextMobject("\\emph{you}")
        you_word.set_color(YELLOW)
        you_word.scale(1.75)
        you_word.move_to(btyb_line)
        you_word.align_to(btyb, DOWN)

        only_word = TextMobject("(only)")
        only_word.scale(1.25)
        only_brace = Brace(only_word, DOWN, buff=SMALL_BUFF)
        only_group = VGroup(only_word, only_brace)
        only_group.next_to(
            VGroup(btyb[0][-1], btyb[1][0]), UP, SMALL_BUFF
        )
        only_group.set_color(RED)

        full_group = VGroup(btyb_group, only_group, you_word)
        full_group.generate_target()
        full_group.target.scale(0.4)
        full_group.target.to_corner(UL)

        patreon_logo = PatreonLogo()
        patreon_logo.scale(0.4)
        patreon_logo.next_to(full_group.target, DOWN)

        self.play(
            Write(so_words[0]),
            LaggedStartMap(
                DrawBorderThenFill, so_words[1],
                run_time=5
            ),
        )
        self.play(
            so_words.shift, DOWN,
            so_words.fade, 1,
            remover=True
        )
        self.play(FadeInFromDown(btyb_group))
        self.wait()
        self.play(Write(you_word))
        self.play(
            GrowFromCenter(only_brace),
            Write(only_word)
        )
        self.wait()
        self.play(MoveToTarget(
            full_group,
            rate_func=running_start,
        ))
        self.play(LaggedStartMap(
            DrawBorderThenFill, patreon_logo
        ))
        self.wait()

    def just_you_and_me(self):
        randy, morty = self.pi_creatures
        for pi in self.pi_creatures:
            pi.change("pondering")
        math = TexMobject("\\sum_{n=1}^\\infty \\frac{1}{n^s}")
        math.scale(2)
        math.move_to(self.pi_creatures)

        spiral = Line(0.5 * RIGHT, 0.5 * RIGHT + 70 * UP)
        spiral.insert_n_curves(1000)
        from from_3b1b.old.zeta import zeta
        spiral.apply_complex_function(zeta)
        step = 0.1
        spiral = VGroup(*[
            VMobject().pointwise_become_partial(
                spiral, a, a + step
            )
            for a in np.arange(0, 1, step)
        ])
        spiral.set_color_by_gradient(BLUE, YELLOW, RED)
        spiral.scale(0.5)
        spiral.move_to(math)

        self.play(FadeInFromDown(randy))
        self.play(FadeInFromDown(morty))
        self.play(
            Write(math),
            randy.change, "hooray",
            morty.change, "hooray",
        )
        self.look_at(math)
        self.play(
            ShowCreation(spiral, run_time=6, rate_func=linear),
            math.scale, 0.5,
            math.shift, 3 * UP,
            randy.change, "thinking",
            morty.change, "thinking",
        )
        self.play(LaggedStartMap(FadeOut, spiral, run_time=3))
        self.wait(3)

    # Helpers
    def create_pi_creatures(self):
        randy = Randolph(color=BLUE_C)
        randy.to_edge(DOWN).shift(4 * LEFT)
        morty = Mortimer()
        morty.to_edge(DOWN).shift(4 * RIGHT)
        return VGroup(randy, morty)


class ThoughtsOnAds(Scene):
    def construct(self):
        title = Title(
            "Internet advertising",
            match_underline_width_to_text=True,
            underline_buff=SMALL_BUFF,
        )

        line = NumberLine(
            color=LIGHT_GREY,
            x_min=0,
            x_max=12,
            numbers_with_elongated_ticks=[]
        )
        line.move_to(DOWN)

        arrows = VGroup(Vector(2 * LEFT), Vector(2 * RIGHT))
        arrows.arrange(RIGHT, buff=2)
        arrows.next_to(line, DOWN)

        misaligned = TextMobject("Misaligned")
        misaligned.next_to(arrows[0], DOWN)
        aligned = TextMobject("Well-aligned")
        aligned.next_to(arrows[1], DOWN)

        VGroup(arrows[0], misaligned).set_color(RED)
        VGroup(arrows[1], aligned).set_color(BLUE)

        left_text = TextMobject(
            "Any website presented \\\\",
            "as a click-maximizing \\\\ slideshow"
        )
        left_text.scale(0.8)
        left_text.next_to(line, UP, buff=MED_LARGE_BUFF)
        left_text.to_edge(LEFT)

        viewer, brand, creator = vcb = VGroup(
            *list(map(TextMobject, ["viewer", "brand", "creator"]))
        )
        brand.next_to(creator, LEFT, LARGE_BUFF)
        viewer.next_to(vcb[1:], UP, LARGE_BUFF)
        arrow_config = {
            "path_arc": 60 * DEGREES,
            "tip_length": 0.15,
        }
        vcb_arrows = VGroup(*[
            VGroup(
                Arrow(p1, p2, **arrow_config),
                Arrow(p2, p1, **arrow_config),
            )
            for p1, p2 in [
                (creator.get_left(), brand.get_right()),
                (brand.get_top(), viewer.get_bottom()),
                (viewer.get_bottom(), creator.get_top()),
            ]
        ])
        vcb_arrows.set_stroke(width=2)
        vcb_arrows.set_color(BLUE)
        vcb_group = VGroup(vcb, vcb_arrows)
        vcb_group.next_to(line, UP, buff=MED_LARGE_BUFF)
        vcb_group.to_edge(RIGHT)

        knob = RegularPolygon(n=3, start_angle=-90 * DEGREES)
        knob.set_height(0.25)
        knob.set_stroke(width=0)
        knob.set_fill(YELLOW, 1)
        knob.move_to(line.get_left(), DOWN)

        right_rect = Rectangle(
            width=3,
            height=0.25,
            stroke_color=WHITE,
            stroke_width=2,
            fill_color=BLUE,
            fill_opacity=0.5
        )
        right_rect.move_to(line, RIGHT)
        right_rect_label = Group(
            ImageMobject("3b1b_logo", height=1),
            TextMobject("(hopefully)").scale(0.8)
        )
        right_rect_label.arrange(DOWN, buff=SMALL_BUFF)
        # TextMobject(
        #     "Where I hope \\\\ I've been"
        # )
        right_rect_label.next_to(
            right_rect, UP, SMALL_BUFF
        )
        # right_rect_label.set_color(BLUE)

        self.add(title)
        self.play(ShowCreation(line))
        self.play(
            Write(misaligned),
            Write(aligned),
            *list(map(GrowArrow, arrows)),
            run_time=1
        )

        self.play(
            FadeIn(left_text),
            FadeInFrom(knob, 2 * RIGHT)
        )
        self.wait()
        self.play(
            LaggedStartMap(FadeInFromDown, vcb),
            LaggedStartMap(ShowCreation, vcb_arrows),
            ApplyMethod(
                knob.move_to, line.get_right(), DOWN,
                run_time=2
            )
        )
        self.wait(2)
        self.play(vcb_group.shift, 2 * UP)
        self.play(
            DrawBorderThenFill(right_rect),
            FadeIn(right_rect_label),
        )
        self.wait()


class HoldUpPreviousPromo(PiCreatureScene):
    CONFIG = {
        "default_pi_creature_kwargs": {
            "color": GREY_BROWN,
            "flip_at_start": True,
        },
        "default_pi_creature_start_corner": DR,
    }

    def construct(self):
        morty = self.pi_creature
        screen_rect = ScreenRectangle(height=5)
        screen_rect.to_corner(UL)

        self.play(
            FadeInFromDown(screen_rect),
            morty.change, "raise_right_hand",
        )
        self.wait(5)


class GoalWrapper(Scene):
    def construct(self):
        goal = TextMobject(
            "Goal: Teach/remind people \\\\ that they love math"
        )
        goal.to_edge(UP)
        self.add(goal)

        screen_rect = ScreenRectangle(height=6)
        screen_rect.next_to(goal, DOWN)
        self.play(ShowCreation(screen_rect))
        self.wait()


class PeopleValueGraph(GraphScene):
    CONFIG = {
        "x_axis_label": "People reached",
        "y_axis_label": "Value per person",
        "x_min": 0,
        "x_max": 12,
        "x_axis_width": 11,
        "y_max": 8,
        "y_axis_height": 5,
        "graph_origin": 2 * DOWN + 5 * LEFT,
        "riemann_rectangles_config": {
            "dx": 0.01,
            "stroke_width": 0,
            "start_color": GREEN,
            "end_color": BLUE,
        }
    }

    def construct(self):
        self.setup_axes()
        self.tweak_labels()
        self.add_curve()
        self.comment_on_incentives()
        self.change_curve()

    def tweak_labels(self):
        self.add_foreground_mobjects(self.x_axis_label_mob)
        self.y_axis_label_mob.to_edge(LEFT)

    def add_curve(self):
        graph = self.graph = self.get_graph(
            lambda x: 7 * np.exp(-0.5 * x),
        )

        self.play(
            ShowCreation(graph),
            rate_func=bezier([0, 0, 1, 1]),
            run_time=3
        )

    def comment_on_incentives(self):
        reach_arrow = Vector(5 * RIGHT)
        reach_arrow.next_to(
            self.x_axis, DOWN,
            buff=SMALL_BUFF,
            aligned_edge=RIGHT
        )
        reach_words = TextMobject("Maximize reach?")
        reach_words.next_to(reach_arrow, DOWN, buff=SMALL_BUFF)
        reach_words.match_color(reach_arrow)

        area = self.area = self.get_riemann_rectangles(
            self.graph, **self.riemann_rectangles_config
        )
        area_words = TextMobject("Maximize this area")
        area_words.set_color(BLUE)
        area_words.move_to(self.coords_to_point(4, 5))
        area_arrow = Arrow(
            area_words.get_bottom(),
            self.coords_to_point(1.5, 2)
        )

        self.play(GrowArrow(reach_arrow))
        self.play(Write(reach_words))
        self.wait()
        self.play(
            LaggedStartMap(DrawBorderThenFill, area),
            Animation(self.graph),
            Animation(self.axes),
            Write(area_words),
            GrowArrow(area_arrow),
        )
        self.wait()

        self.area_label_group = VGroup(area_words, area_arrow)

    def change_curve(self):
        new_graph = self.get_graph(
            lambda x: interpolate(
                7 * np.exp(-0.01 * x),
                7 * np.exp(-3 * x),
                smooth(np.clip(x / 5, 0, 1))
            )
        )
        new_area = self.get_riemann_rectangles(
            new_graph, **self.riemann_rectangles_config
        )

        self.play(
            Transform(self.area, new_area),
            Transform(self.graph, new_graph),
            self.area_label_group[0].shift, RIGHT,
            Animation(self.area_label_group),
            Animation(self.axes),
            run_time=4,
        )
        self.wait()


class DivCurlEndScreen(PatreonEndScreen):
    CONFIG = {
        "specific_patrons": [
            "Juan Benet",
            "Keith Smith",
            "Chloe Zhou",
            "Desmos ",
            "Burt Humburg",
            "CrypticSwarm",
            "Andrew Sachs",
            "Devin Scott",
            "Akash Kumar",
            "Felix Tripier",
            "Arthur Zey",
            "David Kedmey",
            "Ali Yahya",
            "Mayank M. Mehrotra",
            "Lukas Biewald",
            "Yana Chernobilsky",
            "Kaustuv DeBiswas",
            "Yu Jun",
            "Dave Nicponski",
            "Damion Kistler",
            "Jordan Scales",
            "Markus Persson",
            "Fela ",
            "Fred Ehrsam",
            "Randy C. Will",
            "Britt Selvitelle",
            "Jonathan Wilson",
            "Ryan Atallah",
            "Joseph John Cox",
            "Luc Ritchie",
            "Omar Zrien",
            "Sindre Reino Trosterud",
            "Jeff Straathof",
            "Matt Langford",
            "Matt Roveto",
            "Marek Cirkos",
            "Magister Mugit",
            "Stevie Metke",
            "Cooper Jones",
            "James Hughes",
            "John V Wertheim",
            "Chris Giddings",
            "Song Gao",
            "Alexander Feldman",
            "Richard Burgmann",
            "John Griffith",
            "Chris Connett",
            "Steven Tomlinson",
            "Jameel Syed",
            "Bong Choung",
            "Ignacio Freiberg",
            "Zhilong Yang",
            "Giovanni Filippi",
            "Eric Younge",
            "Prasant Jagannath",
            "James H. Park",
            "Norton Wang",
            "Kevin Le",
            "Tianyu Ge",
            "David MacCumber",
            "Oliver Steele",
            "Yaw Etse",
            "Dave B",
            "Waleed Hamied",
            "George Chiesa",
            "supershabam ",
            "Delton Ding",
            "Thomas Tarler",
            "1stViewMaths",
            "Jacob Magnuson",
            "Mark Govea",
            "Clark Gaebel",
            "Mathias Jansson",
            "David Clark",
            "Michael Gardner",
            "Mads Elvheim",
            "Awoo ",
            "Dr . David G. Stork",
            "Ted Suzman",
            "Linh Tran",
            "Andrew Busey",
            "John Haley",
            "Ankalagon ",
            "Eric Lavault",
            "Boris Veselinovich",
            "Julian Pulgarin",
            "Jeff Linse",
            "Robert Teed",
            "Jason Hise",
            "Bernd Sing",
            "Mustafa Mahdi",
            "Mathew Bramson",
            "Jerry Ling",
            "Sh\\`im\\'in Ku\\=ang",
            "Rish Kundalia",
            "Achille Brighton",
            "Ripta Pasay",
        ],
    }
