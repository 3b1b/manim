from __future__ import absolute_import
from big_ol_pile_of_manim_imports import *


class Orbiting(ContinualAnimation):
    CONFIG = {
        "rate": 0.3,
    }

    def __init__(self, planet, star, ellipse, **kwargs):
        self.planet = planet
        self.star = star
        self.ellipse = ellipse
        # Proportion of the way around the ellipse
        self.proportion = 0
        planet.move_to(ellipse.point_from_proportion(0))

        ContinualAnimation.__init__(self, planet, **kwargs)

    def update_mobject(self, dt):
        # time = self.internal_time
        rate = self.rate

        planet = self.planet
        star = self.star
        ellipse = self.ellipse

        rate *= 1 / np.linalg.norm(
            planet.get_center() - star.get_center()
        )
        self.proportion += rate * dt
        self.proportion = self.proportion % 1
        planet.move_to(ellipse.point_from_proportion(self.proportion))


class SunAnimation(ContinualAnimation):
    CONFIG = {
        "rate": 0.2,
        "angle": 60 * DEGREES,
    }

    def __init__(self, sun, **kwargs):
        self.sun = sun
        self.rotated_sun = sun.deepcopy()
        self.rotated_sun.rotate(60 * DEGREES)
        ContinualAnimation.__init__(
            self, Group(sun, self.rotated_sun), **kwargs
        )

    def update_mobject(self, dt):
        time = self.internal_time
        a = (np.sin(self.rate * time * TAU) + 1) / 2.0
        self.rotated_sun.rotate(-self.angle)
        self.rotated_sun.move_to(self.sun)
        self.rotated_sun.rotate(self.angle)
        self.rotated_sun.pixel_array = np.array(
            a * self.sun.pixel_array,
            dtype=self.sun.pixel_array.dtype
        )

# Animations


class ShowEmergingEllipse(Scene):
    CONFIG = {
        "circle_radius": 3,
        "circle_color": BLUE,
        "num_lines": 150,
        "lines_stroke_width": 1,
        "eccentricity_vector": 2 * RIGHT,
        "ghost_lines_stroke_color": LIGHT_GREY,
        "ghost_lines_stroke_width": 0.5,
        "ellipse_color": PINK,
    }

    def construct(self):
        circle = self.get_circle()
        e_point = self.get_eccentricity_point()
        e_dot = Dot(e_point, color=YELLOW)
        lines = self.get_lines()
        ellipse = self.get_ellipse()

        fade_rect = FullScreenFadeRectangle()

        line = lines[len(lines) / 5]
        line_dot = Dot(line.get_center(), color=YELLOW)
        line_dot.scale(0.5)

        ghost_line = self.get_ghost_lines(line)
        ghost_lines = self.get_ghost_lines(lines)

        rot_words = TextMobject("Rotate $90^\\circ$ \\\\ about center")
        rot_words.next_to(line_dot, RIGHT)

        elbow = VGroup(Line(UP, UL), Line(UL, LEFT))
        elbow.set_stroke(width=1)
        elbow.scale(0.2, about_point=ORIGIN)
        elbow.rotate(
            line.get_angle() - 90 * DEGREES,
            about_point=ORIGIN
        )
        elbow.shift(line.get_center())

        eccentric_words = TextMobject("``Eccentric'' point")
        eccentric_words.next_to(circle.get_center(), DOWN)

        ellipse_words = TextMobject("Perfect ellipse")
        ellipse_words.next_to(ellipse, UP, SMALL_BUFF)

        for text in rot_words, ellipse_words:
            text.add_to_back(text.copy().set_stroke(BLACK, 5))

        shuffled_lines = VGroup(*lines)
        random.shuffle(shuffled_lines.submobjects)

        self.play(ShowCreation(circle))
        self.play(
            FadeInAndShiftFromDirection(e_dot, LEFT),
            Write(eccentric_words, run_time=1)
        )
        self.wait()
        self.play(
            LaggedStart(ShowCreation, shuffled_lines),
            Animation(VGroup(e_dot, circle)),
            FadeOut(eccentric_words)
        )
        self.add(ghost_lines)
        self.add(e_dot, circle)
        self.wait()
        self.play(
            FadeIn(fade_rect),
            Animation(line),
            GrowFromCenter(line_dot),
            FadeInFromDown(rot_words),
        )
        self.wait()
        self.add(ghost_line)
        self.play(
            MoveToTarget(line, path_arc=90 * DEGREES),
            Animation(rot_words),
            ShowCreation(elbow)
        )
        self.wait()
        self.play(
            FadeOut(fade_rect),
            FadeOut(line_dot),
            FadeOut(rot_words),
            FadeOut(elbow),
            Animation(line),
            Animation(ghost_line)
        )
        self.play(
            LaggedStart(MoveToTarget, lines, run_time=4),
            Animation(VGroup(e_dot, circle))
        )
        self.wait()
        self.play(
            ShowCreation(ellipse),
            FadeInFromDown(ellipse_words)
        )
        self.wait()

    def get_circle(self):
        circle = self.circle = Circle(
            radius=self.circle_radius,
            color=self.circle_color
        )
        return circle

    def get_eccentricity_point(self):
        return self.circle.get_center() + self.eccentricity_vector

    def get_lines(self):
        center = self.circle.get_center()
        radius = self.circle.get_width() / 2
        e_point = self.get_eccentricity_point()
        lines = VGroup(*[
            Line(
                e_point,
                center + rotate_vector(radius * RIGHT, angle)
            )
            for angle in np.linspace(0, TAU, self.num_lines)
        ])
        lines.set_stroke(width=self.lines_stroke_width)
        for line in lines:
            line.generate_target()
            line.target.rotate(90 * DEGREES)
        return lines

    def get_ghost_lines(self, lines):
        return lines.copy().set_stroke(
            color=self.ghost_lines_stroke_color,
            width=self.ghost_lines_stroke_width
        )

    def get_ellipse(self):
        center = self.circle.get_center()
        e_point = self.get_eccentricity_point()
        radius = self.circle.get_width() / 2

        # Ellipse parameters
        a = radius / 2
        c = np.linalg.norm(e_point - center) / 2
        b = np.sqrt(a**2 - c**2)

        result = Circle(radius=b, color=self.ellipse_color)
        result.stretch(a / b, 0)
        result.move_to(Line(center, e_point))
        return result


class FeynmanAndOrbitingPlannetOnEllipseDiagram(ShowEmergingEllipse):
    def construct(self):
        circle = self.get_circle()
        lines = self.get_lines()
        ghost_lines = self.get_ghost_lines(lines)
        for line in lines:
            MoveToTarget(line).update(1)
        ellipse = self.get_ellipse()
        e_dot = Dot(self.get_eccentricity_point())
        e_dot.set_color(YELLOW)

        comet = ImageMobject("earth")
        comet.scale_to_fit_width(0.3)

        feynman_cut = ImageMobject("FeynmanCut")
        feynman_cut.scale_to_fit_height(4)
        feynman_cut.next_to(ORIGIN, LEFT)
        feynman_cut.shift(UP)
        feynman_name = TextMobject("Richard Feynman")
        feynman_name.next_to(feynman_cut, DOWN)
        feynman_cut.save_state()
        feynman_cut.shift(2 * DOWN)
        feynman_rect = BackgroundRectangle(
            feynman_cut, fill_opacity=1
        )

        group = VGroup(circle, ghost_lines, lines, e_dot, ellipse)

        self.add(group)
        self.add(Orbiting(comet, e_dot, ellipse))
        self.add_foreground_mobjects(comet)
        self.wait()
        self.play(
            feynman_cut.restore,
            MaintainPositionRelativeTo(feynman_rect, feynman_cut),
            VFadeOut(feynman_rect),
            group.to_edge, RIGHT,
        )
        self.play(Write(feynman_name))
        self.wait()
        self.wait(10)


class FeynmanFame(Scene):
    def construct(self):
        books = VGroup(
            ImageMobject("Feynman_QED_cover"),
            ImageMobject("Surely_Youre_Joking_cover"),
            ImageMobject("Feynman_Lectures_cover"),
        )
        for book in books:
            book.scale_to_fit_height(6)
            book.move_to(FRAME_WIDTH * LEFT / 4)

        feynman_diagram = self.get_feynman_diagram()
        feynman_diagram.next_to(ORIGIN, RIGHT)
        fd_parts = VGroup(*reversed(feynman_diagram.family_members_with_points()))

        # As a physicist
        self.play(self.get_book_intro(books[0]))
        self.play(LaggedStart(
            Write, feynman_diagram,
            run_time=4
        ))
        self.wait()
        self.play(
            self.get_book_intro(books[1]),
            self.get_book_outro(books[0]),
            LaggedStart(
                ApplyMethod, fd_parts,
                lambda m: (m.scale, 0),
                run_time=1
            ),
        )
        self.remove(feynman_diagram)
        self.wait()

        # As a public figure
        safe = SVGMobject(file_name="safe", height=2)
        safe_rect = SurroundingRectangle(safe, buff=0)
        safe_rect.set_stroke(width=0)
        safe_rect.set_fill(DARK_GREY, 1)
        safe.add_to_back(safe_rect)

        bongo = SVGMobject(file_name="bongo")
        bongo.scale_to_fit_height(1)
        bongo.set_color(WHITE)
        bongo.next_to(safe, RIGHT, LARGE_BUFF)

        objects = VGroup(safe, bongo)

        feynman_smile = ImageMobject("Feynman_smile")
        feynman_smile.match_width(objects)
        feynman_smile.next_to(objects, DOWN)

        VGroup(objects, feynman_smile).next_to(ORIGIN, RIGHT)

        joke = TextMobject(
            "``Science is the belief \\\\ in the ignorance of \\\\ experts.''"
        )
        joke.move_to(objects)

        self.play(LaggedStart(
            DrawBorderThenFill, objects,
            lag_ratio=0.75
        ))
        self.play(self.get_book_intro(feynman_smile))
        self.wait()
        self.play(
            objects.shift, 2 * UP,
            VFadeOut(objects)
        )
        self.play(Write(joke))
        self.wait(2)

        self.play(
            self.get_book_intro(books[2]),
            self.get_book_outro(books[1]),
            LaggedStart(FadeOut, joke, run_time=1),
            ApplyMethod(
                feynman_smile.shift, FRAME_HEIGHT * DOWN,
                remover=True
            )
        )

        # As a teacher
        feynman_teacher = ImageMobject("Feynman_teacher")
        feynman_teacher.scale_to_fit_width(FRAME_WIDTH / 2 - 1)
        feynman_teacher.next_to(ORIGIN, RIGHT)

        self.play(self.get_book_intro(feynman_teacher))
        self.wait(3)

    def get_book_animation(self, book,
                           initial_shift,
                           animated_shift,
                           opacity_func
                           ):
        rect = BackgroundRectangle(book, fill_opacity=1)
        book.shift(initial_shift)

        return AnimationGroup(
            ApplyMethod(book.shift, animated_shift),
            UpdateFromAlphaFunc(
                rect, lambda r, a: r.move_to(book).set_fill(
                    opacity=opacity_func(a)
                ),
                remover=True
            )
        )

    def get_book_intro(self, book):
        return self.get_book_animation(
            book, 2 * DOWN, 2 * UP, lambda a: 1 - a
        )

    def get_book_outro(self, book):
        return ApplyMethod(book.shift, FRAME_HEIGHT * UP, remover=True)

    def get_feynman_diagram(self):
        x_min = -1.5
        x_max = 1.5
        arrow = Arrow(LEFT, RIGHT, buff=0, use_rectangular_stem=False)
        arrow.tip.move_to(arrow.get_center())
        arrows = VGroup(*[
            arrow.copy().rotate(angle).next_to(point, vect, buff=0)
            for (angle, point, vect) in [
                (-45 * DEGREES, x_min * RIGHT, UL),
                (-135 * DEGREES, x_min * RIGHT, DL),
                (-135 * DEGREES, x_max * RIGHT, UR),
                (-45 * DEGREES, x_max * RIGHT, DR),
            ]
        ])
        labels = VGroup(*[
            TexMobject(tex)
            for tex in ["e^-", "e^+", "\\text{\\=q}", "q"]
        ])
        vects = [UR, DR, UL, DL]
        for arrow, label, vect in zip(arrows, labels, vects):
            label.next_to(arrow.get_center(), vect, buff=SMALL_BUFF)

        wave = FunctionGraph(
            lambda x: 0.2 * np.sin(2 * TAU * x),
            x_min=x_min,
            x_max=x_max,
        )
        wave_label = TexMobject("\\gamma")
        wave_label.next_to(wave, UP, SMALL_BUFF)
        labels.add(wave_label)

        squiggle = ParametricFunction(
            lambda t: np.array([
                t + 0.5 * np.sin(TAU * t),
                0.5 * np.cos(TAU * t),
                0,
            ]),
            t_min=0,
            t_max=4,
        )
        squiggle.scale(0.25)
        squiggle.set_color(BLUE)
        squiggle.rotate(-30 * DEGREES)
        squiggle.next_to(
            arrows[2].point_from_proportion(0.75),
            DR, buff=0
        )
        squiggle_label = TexMobject("g")
        squiggle_label.next_to(squiggle, UR, buff=-MED_SMALL_BUFF)
        labels.add(squiggle_label)

        return VGroup(arrows, wave, squiggle, labels)


class FeynmanLecturesScreenCaptureFrame(Scene):
    def construct(self):
        url = TextMobject("http://www.feynmanlectures.caltech.edu/")
        url.to_edge(UP)

        screen_rect = ScreenRectangle(height=6)
        screen_rect.next_to(url, DOWN)

        self.add(url)
        self.play(ShowCreation(screen_rect))
        self.wait()


class TheMotionOfPlanets(Scene):
    CONFIG = {
        "camera_config": {"background_opacity": 1},
        "random_seed": 2,
    }

    def construct(self):
        self.add_title()
        self.setup_orbits()

    def add_title(self):
        title = TextMobject("``The motion of planets around the sun''")
        title.set_color(YELLOW)
        title.to_edge(UP)
        title.add_to_back(title.copy().set_stroke(BLACK, 5))
        self.add(title)
        self.title = title

    def setup_orbits(self):
        sun = ImageMobject("sun")
        sun.scale_to_fit_height(0.7)
        planets, ellipses, orbits = self.get_planets_ellipses_and_orbits(sun)

        archivist_words = TextMobject(
            "Judith Goodstein (Caltech archivist)"
        )
        archivist_words.to_corner(UL)
        archivist_words.shift(1.5 * DOWN)
        archivist_words.add_background_rectangle()
        alt_name = TextMobject("David Goodstein (Caltech physicist)")
        alt_name.next_to(archivist_words, DOWN, aligned_edge=LEFT)
        alt_name.add_background_rectangle()

        book = ImageMobject("Lost_Lecture_cover")
        book.scale_to_fit_height(4)
        book.next_to(alt_name, DOWN)

        self.add(SunAnimation(sun))
        self.add(ellipses, planets)
        self.add(self.title)
        self.add(*orbits)
        self.add_foreground_mobjects(planets)
        self.wait(10)
        self.play(
            VGroup(ellipses, sun).shift, 3 * RIGHT,
            FadeInFromDown(archivist_words),
            Animation(self.title)
        )
        self.add_foreground_mobjects(archivist_words)
        self.wait(3)
        self.play(FadeInFromDown(alt_name))
        self.add_foreground_mobjects(alt_name)
        self.wait()
        self.play(FadeInFromDown(book))
        self.wait(15)

    def get_planets_ellipses_and_orbits(self, sun):
        planets = VGroup(
            ImageMobject("mercury"),
            ImageMobject("venus"),
            ImageMobject("earth"),
            ImageMobject("mars"),
            ImageMobject("comet")
        )
        sizes = [0.383, 0.95, 1.0, 0.532, 0.3]
        orbit_radii = [0.254, 0.475, 0.656, 1.0, 3.0]
        orbit_eccentricies = [0.206, 0.006, 0.0167, 0.0934, 0.967]

        for planet, size in zip(planets, sizes):
            planet.scale_to_fit_height(0.5)
            planet.scale(size)

        ellipses = VGroup(*[
            Circle(radius=r, color=WHITE, stroke_width=1)
            for r in orbit_radii
        ])
        for circle, ec in zip(ellipses, orbit_eccentricies):
            a = circle.get_height() / 2
            c = ec * a
            b = np.sqrt(a**2 - c**2)
            circle.stretch(b / a, 1)
            c = np.sqrt(a**2 - b**2)
            circle.shift(c * RIGHT)
        for circle in ellipses:
            circle.rotate(
                TAU * np.random.random(),
                about_point=ORIGIN
            )

        ellipses.scale(3.5, about_point=ORIGIN)

        orbits = [
            Orbiting(
                planet, sun, circle,
                rate=0.25 * r**(2 / 3)
            )
            for planet, circle, r in zip(planets, ellipses, orbit_radii)
        ]
        orbits[-1].proportion = 0.15
        orbits[-1].rate = 0.5

        return planets, ellipses, orbits


class AskAboutEllipses(TheMotionOfPlanets):
    CONFIG = {
        "camera_config": {"background_opacity": 1},
        "animate_sun": True,
    }

    def construct(self):
        self.add_title()
        self.add_sun()
        self.add_orbit()
        self.add_focus_lines()
        self.add_force_labels()
        self.comment_on_imperfections()
        self.set_up_differential_equations()

    def add_title(self):
        title = Title("Why are orbits ellipses?")
        self.add(title)
        self.title = title

    def add_sun(self):
        sun = ImageMobject("sun", height=0.5)
        self.sun = sun
        self.add(sun)
        if self.animate_sun:
            self.add(SunAnimation(sun))

    def add_orbit(self):
        sun = self.sun
        comet = ImageMobject("comet")
        comet.scale_to_fit_height(0.2)
        ellipse = self.get_ellipse()
        orbit = Orbiting(comet, sun, ellipse)

        self.add(ellipse)
        self.add(orbit)

        self.ellipse = ellipse
        self.comet = comet
        self.orbit = orbit

    def add_focus_lines(self):
        f1, f2 = self.focus_points
        comet = self.comet
        lines = VGroup(Line(LEFT, RIGHT), Line(LEFT, RIGHT))
        lines.set_stroke(LIGHT_GREY, 1)

        def update_lines(lines):
            l1, l2 = lines
            P = comet.get_center()
            l1.put_start_and_end_on(f1, P)
            l2.put_start_and_end_on(f2, P)
            return lines

        animation = ContinualUpdateFromFunc(
            lines, update_lines
        )
        self.add(animation)
        self.wait(8)

        self.focus_lines = lines
        self.focus_lines_animation = animation

    def add_force_labels(self):
        radial_line = self.focus_lines[0]

        # Radial line measurement
        radius_measurement_kwargs = {
            "num_decimal_places": 3,
            "color": BLUE,
        }
        radius_measurement = DecimalNumber(1, **radius_measurement_kwargs)

        def update_radial_measurement(measurement):
            angle = -radial_line.get_angle() + np.pi
            radial_line.rotate(angle, about_point=ORIGIN)
            new_decimal = DecimalNumber(
                radial_line.get_length(),
                **radius_measurement_kwargs
            )
            max_width = 0.6 * radial_line.get_width()
            if new_decimal.get_width() > max_width:
                new_decimal.scale_to_fit_width(max_width)
            new_decimal.next_to(radial_line, UP, SMALL_BUFF)
            VGroup(new_decimal, radial_line).rotate(
                -angle, about_point=ORIGIN
            )
            Transform(measurement, new_decimal).update(1)

        radius_measurement_animation = ContinualUpdateFromFunc(
            radius_measurement, update_radial_measurement
        )

        # Force equation
        force_equation = TexMobject(
            "F = {GMm \\over (0.000)^2}",
            tex_to_color_map={
                "F": YELLOW,
                "0.000": BLACK,
            }
        )
        force_equation.next_to(self.title, DOWN)
        force_equation.to_edge(RIGHT)
        radius_in_denominator_ref = force_equation.get_part_by_tex("0.000")
        radius_in_denominator = DecimalNumber(
            0, **radius_measurement_kwargs
        )
        radius_in_denominator.scale(0.95)
        update_radius_in_denominator = ContinualChangingDecimal(
            radius_in_denominator,
            lambda a: radial_line.get_length(),
            position_update_func=lambda mob: mob.move_to(
                radius_in_denominator_ref,
            )
        )

        # Force arrow
        force_arrow = Arrow(LEFT, RIGHT, color=YELLOW)

        def update_force_arrow(arrow):
            radius = radial_line.get_length()
            # target_length = 1 / radius**2
            target_length = 1 / radius  # Lies!
            arrow.scale(
                target_length / arrow.get_length()
            )
            arrow.rotate(
                np.pi + radial_line.get_angle() - arrow.get_angle()
            )
            arrow.shift(
                radial_line.get_end() - arrow.get_start()
            )
        force_arrow_animation = ContinualUpdateFromFunc(
            force_arrow, update_force_arrow
        )

        inverse_square_law_words = TextMobject(
            "``Inverse square law''"
        )
        inverse_square_law_words.next_to(force_equation, DOWN, MED_LARGE_BUFF)
        inverse_square_law_words.to_edge(RIGHT)
        force_equation.next_to(inverse_square_law_words, UP, MED_LARGE_BUFF)

        def v_fade_in(mobject):
            return UpdateFromAlphaFunc(
                mobject,
                lambda mob, alpha: mob.set_fill(opacity=alpha)
            )

        self.add(update_radius_in_denominator)
        self.add(radius_measurement_animation)
        self.play(
            FadeIn(force_equation),
            v_fade_in(radius_in_denominator),
            v_fade_in(radius_measurement)
        )
        self.add(force_arrow_animation)
        self.play(v_fade_in(force_arrow))
        self.wait(8)
        self.play(Write(inverse_square_law_words))
        self.wait(9)

        self.force_equation = force_equation
        self.inverse_square_law_words = inverse_square_law_words
        self.force_arrow = force_arrow
        self.radius_measurement = radius_measurement

    def comment_on_imperfections(self):
        planets, ellipses, orbits = self.get_planets_ellipses_and_orbits(self.sun)
        orbits.pop(-1)
        ellipses.submobjects.pop(-1)
        planets.submobjects.pop(-1)

        scale_factor = 20
        center = self.sun.get_center()
        ellipses.save_state()
        ellipses.scale(scale_factor, about_point=center)

        self.add(*orbits)
        self.play(ellipses.restore, Animation(planets))
        self.wait(7)
        self.play(
            ellipses.scale, scale_factor, {"about_point": center},
            Animation(planets)
        )
        self.remove(*orbits)
        self.remove(planets, ellipses)
        self.wait(2)

    def set_up_differential_equations(self):
        d_dt = TexMobject("{d \\over dt}")
        in_vect = Matrix(np.array([
            "x(t)",
            "y(t)",
            "\\dot{x}(t)",
            "\\dot{y}(t)",
        ]))
        equals = TexMobject("=")
        out_vect = Matrix(np.array([
            "\\dot{x}(t)",
            "\\dot{y}(t)",
            "-x(t) / (x(t)^2 + y(t)^2)^{3/2}",
            "-y(t) / (x(t)^2 + y(t)^2)^{3/2}",
        ]), element_alignment_corner=ORIGIN)

        equation = VGroup(d_dt, in_vect, equals, out_vect)
        equation.arrange_submobjects(RIGHT, buff=SMALL_BUFF)
        equation.scale_to_fit_width(6)

        equation.to_corner(DR, buff=MED_LARGE_BUFF)
        cross = Cross(equation)

        self.play(Write(equation))
        self.wait(6)
        self.play(ShowCreation(cross))
        self.wait(6)

    # Helpers
    def get_ellipse(self):
        a = 7.0
        b = 4.0
        c = np.sqrt(a**2 - b**2)
        ellipse = Circle(radius=a / 2)
        ellipse.set_stroke(WHITE, 1)
        ellipse.stretch(b / a, dim=1)
        ellipse.move_to(
            self.sun.get_center() + c * LEFT / 2
        )
        self.focus_points = [
            self.sun.get_center(),
            self.sun.get_center() + c * LEFT,
        ]
        return ellipse


class FeynmanElementaryQuote(Scene):
    def construct(self):
        quote = TextMobject(
            """
            I am going to give what I will call an
            \\emph{elementary} demonstration.  But elementary
            does not mean easy to understand.  Elementary
            means that [nothing] very little is requried
            to know ahead of time in order to understand it,
            except to have an infinite amount of intelligence.
            """,
            tex_to_color_map={
                "\\emph{elementary}": BLUE,
                "elementary": BLUE,
                "Elementary": BLUE,
            }
        )

        self.add(quote)

