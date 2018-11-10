
from big_ol_pile_of_manim_imports import *

from old_projects.div_curl import VectorField
from old_projects.div_curl import get_force_field_func

COBALT = "#0047AB"


class Orbiting(ContinualAnimation):
    CONFIG = {
        "rate": 7.5,
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

        planet = self.planet
        star = self.star
        ellipse = self.ellipse

        rate = self.rate
        radius_vector = planet.get_center() - star.get_center()
        rate *= 1.0 / get_norm(radius_vector)

        prop = self.proportion
        d_prop = 0.001
        ds = get_norm(op.add(
            ellipse.point_from_proportion((prop + d_prop) % 1),
            -ellipse.point_from_proportion(prop),
        ))

        delta_prop = (d_prop / ds) * rate * dt

        self.proportion = (self.proportion + delta_prop) % 1
        planet.move_to(
            ellipse.point_from_proportion(self.proportion)
        )


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


class ShowWord(Animation):
    CONFIG = {
        "time_per_char": 0.06,
        "rate_func": None,
    }

    def __init__(self, word, **kwargs):
        assert(isinstance(word, SingleStringTexMobject))
        digest_config(self, kwargs)
        run_time = kwargs.pop(
            "run_time",
            self.time_per_char * len(word)
        )
        self.stroke_width = word.get_stroke_width()
        Animation.__init__(self, word, run_time=run_time, **kwargs)

    def update_mobject(self, alpha):
        word = self.mobject
        stroke_width = self.stroke_width
        count = int(alpha * len(word))
        remainder = (alpha * len(word)) % 1
        word[:count].set_fill(opacity=1)
        word[:count].set_stroke(width=stroke_width)
        if count < len(word):
            word[count].set_fill(opacity=remainder)
            word[count].set_stroke(width=remainder * stroke_width)
            word[count + 1:].set_fill(opacity=0)
            word[count + 1:].set_stroke(width=0)

# Animations


class TakeOver(PiCreatureScene):
    CONFIG = {
        "default_pi_creature_kwargs": {
            "color": GREY_BROWN,
            "flip_at_start": True,
        },
        "default_pi_creature_start_corner": DR,
    }

    def construct(self):
        gradient = ImageMobject("white_black_gradient")
        gradient.set_height(FRAME_HEIGHT)
        self.add(gradient)

        morty = self.pi_creatures
        henry = ImageMobject("Henry_As_Stick")
        henry.set_height(4)
        henry.to_edge(LEFT)
        henry.to_edge(DOWN)

        self.add(morty, henry)
        self.pi_creature_says(
            "Muahaha!  All \\\\ mine now.",
            bubble_kwargs={"fill_opacity": 0.5},
            bubble_creation_class=FadeIn,
            target_mode="conniving",
            added_anims=[henry.rotate, 5 * DEGREES]
        )
        self.wait(2)


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

        line = lines[len(lines) // 5]
        line_dot = Dot(line.get_center(), color=YELLOW)
        line_dot.scale(0.5)

        ghost_line = self.get_ghost_lines(line)
        ghost_lines = self.get_ghost_lines(lines)

        rot_words = TextMobject("Rotate $90^\\circ$ \\\\ about center")
        rot_words.next_to(line_dot, RIGHT)

        elbow = self.get_elbow(line)

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

    def get_elbow(self, line):
        elbow = VGroup(Line(UP, UL), Line(UL, LEFT))
        elbow.set_stroke(width=1)
        elbow.scale(0.2, about_point=ORIGIN)
        elbow.rotate(
            line.get_angle() - 90 * DEGREES,
            about_point=ORIGIN
        )
        elbow.shift(line.get_center())
        return elbow

    def get_ellipse(self):
        center = self.circle.get_center()
        e_point = self.get_eccentricity_point()
        radius = self.circle.get_width() / 2

        # Ellipse parameters
        a = radius / 2
        c = get_norm(e_point - center) / 2
        b = np.sqrt(a**2 - c**2)

        result = Circle(radius=b, color=self.ellipse_color)
        result.stretch(a / b, 0)
        result.move_to(Line(center, e_point))
        return result


class ShowFullStory(Scene):
    def construct(self):
        directory = os.path.join(
            MEDIA_DIR,
            "animations/active_projects/lost_lecture/images"
        )
        scene_names = [
            "ShowEmergingEllipse",
            "ShowFullStory",
            "FeynmanFameStart",
            "TheMotionOfPlanets",
            "FeynmanElementaryQuote",
            "DrawingEllipse",
            "ShowEllipseDefiningProperty",
            "ProveEllipse",
            "KeplersSecondLaw",
            "AngularMomentumArgument",
            "HistoryOfAngularMomentum",
            "FeynmanRecountingNewton",
            "IntroduceShapeOfVelocities",
            "ShowEqualAngleSlices",
            "PonderOverOffCenterDiagram",
            "UseVelocityDiagramToDeduceCurve",
        ]
        images = Group(*[
            ImageMobject(os.path.join(directory, name + ".png"))
            for name in scene_names
        ])
        for image in images:
            image.add(
                SurroundingRectangle(image, buff=0, color=WHITE)
            )
        images.arrange_submobjects_in_grid(n_rows=4)

        images.scale(
            1.01 * FRAME_WIDTH / images[0].get_width()
        )
        images.shift(-images[0].get_center())

        self.play(
            images.set_width, FRAME_WIDTH - 1,
            images.center,
            run_time=3,
        )
        self.wait()
        self.play(
            images.shift, -images[2].get_center(),
            images.scale, FRAME_WIDTH / images[2].get_width(),
            {"about_point": ORIGIN},
            run_time=3,
        )
        self.wait()


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
        comet.set_width(0.3)

        feynman = ImageMobject("Feynman")
        feynman.set_height(6)
        feynman.next_to(ORIGIN, LEFT)
        feynman.to_edge(UP)
        feynman_name = TextMobject("Richard Feynman")
        feynman_name.next_to(feynman, DOWN)
        feynman.save_state()
        feynman.shift(2 * DOWN)
        feynman_rect = BackgroundRectangle(
            feynman, fill_opacity=1
        )

        group = VGroup(circle, ghost_lines, lines, e_dot, ellipse)

        self.add(group)
        self.add(Orbiting(comet, e_dot, ellipse))
        self.add_foreground_mobjects(comet)
        self.wait()
        self.play(
            feynman.restore,
            MaintainPositionRelativeTo(feynman_rect, feynman),
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
            book.set_height(6)
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
        bongo.set_height(1)
        bongo.set_color(WHITE)
        bongo.next_to(safe, RIGHT, LARGE_BUFF)

        objects = VGroup(safe, bongo)

        feynman_smile = ImageMobject("Feynman_Los_Alamos")
        feynman_smile.set_height(4)
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
        feynman_teacher = ImageMobject("Feynman_teaching")
        feynman_teacher.set_width(FRAME_WIDTH / 2 - 1)
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
        sun.set_height(0.7)
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
        book.set_height(4)
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
            planet.set_height(0.5)
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


class TeacherHoldingUp(TeacherStudentsScene):
    def construct(self):
        self.play(
            self.teacher.change, "raise_right_hand"
        )
        self.change_all_student_modes("pondering")
        self.look_at(ORIGIN)
        self.wait(5)


class AskAboutEllipses(TheMotionOfPlanets):
    CONFIG = {
        "camera_config": {"background_opacity": 1},
        "sun_height": 0.5,
        "sun_center": ORIGIN,
        "animate_sun": True,
        "a": 3.5,
        "b": 2.0,
        "ellipse_color": WHITE,
        "ellipse_stroke_width": 1,
        "comet_height": 0.2,
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
        sun = ImageMobject("sun", height=self.sun_height)
        sun.move_to(self.sun_center)
        self.sun = sun
        self.add(sun)
        if self.animate_sun:
            sun_animation = SunAnimation(sun)
            self.add(sun_animation)
            self.add_foreground_mobjects(
                sun_animation.mobject
            )
        else:
            self.add_foreground_mobjects(sun)

    def add_orbit(self):
        sun = self.sun
        comet = self.get_comet()
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

        animation = ContinualUpdate(
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
                new_decimal.set_width(max_width)
            new_decimal.next_to(radial_line, UP, SMALL_BUFF)
            VGroup(new_decimal, radial_line).rotate(
                -angle, about_point=ORIGIN
            )
            Transform(measurement, new_decimal).update(1)

        radius_measurement_animation = ContinualUpdate(
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
                radius_in_denominator_ref, LEFT
            )
        )

        # Force arrow
        force_arrow, force_arrow_animation = self.get_force_arrow_and_update(
            self.comet
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
        equation.set_width(6)

        equation.to_corner(DR, buff=MED_LARGE_BUFF)
        cross = Cross(equation)

        self.play(Write(equation))
        self.wait(6)
        self.play(ShowCreation(cross))
        self.wait(6)

    # Helpers
    def get_comet(self):
        comet = ImageMobject("comet")
        comet.set_height(self.comet_height)
        return comet

    def get_ellipse(self):
        a = self.a
        b = self.b
        c = np.sqrt(a**2 - b**2)
        ellipse = Circle(radius=a)
        ellipse.set_stroke(
            self.ellipse_color,
            self.ellipse_stroke_width,
        )
        ellipse.stretch(fdiv(b, a), dim=1)
        ellipse.move_to(
            self.sun.get_center() + c * LEFT,
        )
        self.focus_points = [
            self.sun.get_center(),
            self.sun.get_center() + 2 * c * LEFT,
        ]
        return ellipse

    def get_force_arrow_and_update(self, comet, scale_factor=1):
        force_arrow = Arrow(LEFT, RIGHT, color=YELLOW)
        sun = self.sun

        def update_force_arrow(arrow):
            radial_line = Line(
                sun.get_center(), comet.get_center()
            )
            radius = radial_line.get_length()
            # target_length = 1 / radius**2
            target_length = scale_factor / radius  # Lies!
            arrow.scale(
                target_length / arrow.get_length()
            )
            arrow.rotate(
                np.pi + radial_line.get_angle() - arrow.get_angle()
            )
            arrow.shift(
                radial_line.get_end() - arrow.get_start()
            )
        force_arrow_animation = ContinualUpdate(
            force_arrow, update_force_arrow
        )

        return force_arrow, force_arrow_animation

    def get_radial_line_and_update(self, comet):
        line = Line(LEFT, RIGHT)
        line.set_stroke(LIGHT_GREY, 1)
        line_update = ContinualUpdate(
            line, lambda l: l.put_start_and_end_on(
                self.sun.get_center(),
                comet.get_center(),
            )
        )
        return line, line_update


class FeynmanSaysItBest(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Feynman says \\\\ it best",
            added_anims=[
                self.get_student_changes(
                    "hooray", "happy", "erm"
                )
            ]
        )
        self.wait(3)


class FeynmanElementaryQuote(Scene):
    def construct(self):
        quote_text = """
            \\large
            I am going to give what I will call an
            \\emph{elementary} demonstration.  But elementary
            does not mean easy to understand.  Elementary
            means that very little is required
            to know ahead of time in order to understand it,
            except to have an infinite amount of intelligence.
        """
        quote_parts = [s for s in quote_text.split(" ") if s]
        quote = TextMobject(
            *quote_parts,
            tex_to_color_map={
                "\\emph{elementary}": BLUE,
                "elementary": BLUE,
                "Elementary": BLUE,
                "infinite": YELLOW,
                "amount": YELLOW,
                "of": YELLOW,
                "intelligence": YELLOW,
                "very": RED,
                "little": RED,
            },
            alignment=""
        )
        quote[-1].shift(2 * SMALL_BUFF * LEFT)
        quote.set_width(FRAME_WIDTH - 1)
        quote.to_edge(UP)
        quote.get_part_by_tex("of").set_color(WHITE)

        nothing = TextMobject("nothing")
        nothing.scale(0.9)
        very = quote.get_part_by_tex("very")
        nothing.shift(very[0].get_left() - nothing[0].get_left())
        nothing.set_color(RED)

        for word in quote:
            if word is very:
                self.add_foreground_mobjects(nothing)
                self.play(ShowWord(nothing))
                self.wait(0.2)
                nothing.sort_submobjects(lambda p: -p[0])
                self.play(LaggedStart(
                    FadeOut, nothing,
                    run_time=1
                ))
                self.remove_foreground_mobject(nothing)
            back_word = word.copy().set_stroke(BLACK, 5)
            self.add_foreground_mobjects(back_word, word)
            self.play(
                ShowWord(back_word),
                ShowWord(word),
            )
            self.wait(0.005 * len(word)**1.5)
        self.wait()

        # Show thumbnails
        images = Group(
            ImageMobject("Calculus_Thumbnail"),
            ImageMobject("Fourier_Thumbnail"),
        )
        for image in images:
            image.set_height(3)
        images.arrange_submobjects(RIGHT, buff=LARGE_BUFF)
        images.to_edge(DOWN, buff=LARGE_BUFF)
        images[1].move_to(images[0])
        crosses = VGroup(*list(map(Cross, images)))
        crosses.set_stroke("RED", 10)

        for image, cross in zip(images, crosses):
            image.rect = SurroundingRectangle(
                image,
                stroke_width=3,
                stroke_color=WHITE,
                buff=0
            )
            cross.scale(1.1)
        self.play(
            FadeInFromDown(images[0]),
            FadeInFromDown(images[0].rect)
        )
        self.play(ShowCreation(crosses[0]))
        self.wait()
        self.play(
            FadeOutAndShiftDown(images[0]),
            FadeOutAndShiftDown(images[0].rect),
            FadeOutAndShiftDown(crosses[0]),
            FadeInFromDown(images[1]),
            FadeInFromDown(images[1].rect),
        )
        self.play(ShowCreation(crosses[1]))
        self.wait()


class LostLecturePicture(TODOStub):
    CONFIG = {"camera_config": {"background_opacity": 1}}

    def construct(self):
        picture = ImageMobject("Feynman_teaching")
        picture.set_height(FRAME_WIDTH)
        picture.to_corner(UL, buff=0)
        picture.fade(0.5)

        self.play(
            picture.to_corner, DR, {"buff": 0},
            picture.shift, 1.5 * DOWN,
            path_arc=60 * DEGREES,
            run_time=20,
            rate_func=bezier([0, 0, 1, 1])
        )


class AskAboutInfiniteIntelligence(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Infinite intelligence?",
            target_mode="confused"
        )
        self.play(
            self.get_student_changes("horrified", "confused", "sad"),
            self.teacher.change, "happy",
        )
        self.wait()
        self.teacher_says(
            "Stay focused, \\\\ go full screen, \\\\ and you'll be fine.",
            added_anims=[self.get_student_changes(*["happy"] * 3)]
        )
        self.wait()
        self.look_at(self.screen)
        self.wait(5)


class TableOfContents(Scene):
    def construct(self):
        items = VGroup(
            TextMobject("How the ellipse will arise"),
            TextMobject("Kepler's 2nd law"),
            TextMobject("The shape of velocities"),
        )
        items.arrange_submobjects(
            DOWN, buff=LARGE_BUFF, aligned_edge=LEFT
        )
        items.to_edge(LEFT, buff=1.5)
        for item in items:
            item.add(Dot().next_to(item, LEFT))
            item.generate_target()
            item.target.set_fill(GREY, opacity=0.5)

        title = Title("The plan")
        scale_factor = 1.2

        self.add(title)
        self.play(LaggedStart(
            FadeIn, items,
            run_time=1,
            lag_ratio=0.7,
        ))
        self.wait()
        for item in items:
            other_items = VGroup(*[m for m in items if m is not item])
            new_item = item.copy()
            new_item.scale(scale_factor, about_edge=LEFT)
            new_item.set_fill(WHITE, 1)
            self.play(
                Transform(item, new_item),
                *list(map(MoveToTarget, other_items))
            )
            self.wait()


class DrawEllipseOverlay(Scene):
    def construct(self):
        ellipse = Circle()
        ellipse.stretch_to_fit_width(7.0)
        ellipse.stretch_to_fit_height(3.8)
        ellipse.shift(1.05 * UP + 0.48 * LEFT)
        ellipse.set_stroke(RED, 8)

        image = ImageMobject(
            os.path.join(
                get_image_output_directory(self.__class__),
                "HeldUpEllipse.jpg"
            )
        )
        image.set_height(FRAME_HEIGHT)

        # self.add(image)
        self.play(ShowCreation(ellipse))
        self.wait()
        self.play(FadeOut(ellipse))


class ShowEllipseDefiningProperty(Scene):
    CONFIG = {
        "camera_config": {"background_opacity": 1},
        "ellipse_color": BLUE,
        "a": 4.0,
        "b": 3.0,
        "distance_labels_scale_factor": 1.0,
    }

    def construct(self):
        self.add_ellipse()
        self.add_focal_lines()
        self.add_distance_labels()
        self.label_foci()
        self.label_focal_sum()

    def add_ellipse(self):
        a = self.a
        b = self.b
        ellipse = Circle(radius=a, color=self.ellipse_color)
        ellipse.stretch(fdiv(b, a), dim=1)
        ellipse.to_edge(LEFT, buff=LARGE_BUFF)
        self.ellipse = ellipse
        self.add(ellipse)

    def add_focal_lines(self):
        push_pins = VGroup(*[
            SVGMobject(
                file_name="push_pin",
                color=LIGHT_GREY,
                fill_opacity=0.8,
                height=0.5,
            ).move_to(point, DR).shift(0.05 * RIGHT)
            for point in self.get_foci()
        ])

        dot = Dot()
        dot.scale(0.5)
        position_tracker = ValueTracker(0.125)
        dot_update = ContinualUpdate(
            dot,
            lambda d: d.move_to(
                self.ellipse.point_from_proportion(
                    position_tracker.get_value() % 1
                )
            )
        )
        position_tracker_wander = ContinualMovement(
            position_tracker, rate=0.05,
        )

        lines, lines_update_animation = self.get_focal_lines_and_update(
            self.get_foci, dot
        )

        self.add_foreground_mobjects(push_pins, dot)
        self.add(dot_update)
        self.play(LaggedStart(
            FadeInAndShiftFromDirection, push_pins,
            lambda m: (m, 2 * UP + LEFT),
            run_time=1,
            lag_ratio=0.75
        ))
        self.play(ShowCreation(lines))
        self.add(lines_update_animation)
        self.add(position_tracker_wander)
        self.wait(2)

        self.position_tracker = position_tracker
        self.focal_lines = lines

    def add_distance_labels(self):
        lines = self.focal_lines
        colors = [YELLOW, PINK]

        distance_labels, distance_labels_animation = \
            self.get_distance_labels_and_update(lines, colors)

        sum_expression, numbers, number_updates = \
            self.get_sum_expression_and_update(
                lines, colors, lambda mob: mob.to_corner(UR)
            )

        sum_expression_fading_rect = BackgroundRectangle(
            sum_expression, fill_opacity=1
        )

        sum_rect = SurroundingRectangle(numbers[-1])
        constant_words = TextMobject("Stays constant")
        constant_words.next_to(sum_rect, DOWN, aligned_edge=RIGHT)
        VGroup(sum_rect, constant_words).set_color(BLUE)

        self.add(distance_labels_animation)
        self.add(*number_updates)
        self.add(sum_expression)
        self.add_foreground_mobjects(sum_expression_fading_rect)
        self.play(
            VFadeIn(distance_labels),
            FadeOut(sum_expression_fading_rect),
        )
        self.remove_foreground_mobject(sum_expression_fading_rect)
        self.wait(7)
        self.play(
            ShowCreation(sum_rect),
            Write(constant_words)
        )
        self.wait(7)
        self.play(FadeOut(sum_rect), FadeOut(constant_words))

        self.sum_expression = sum_expression
        self.sum_rect = sum_rect

    def label_foci(self):
        foci = self.get_foci()
        focus_words = VGroup(*[
            TextMobject("Focus").next_to(focus, DOWN)
            for focus in foci
        ])
        foci_word = TextMobject("Foci")
        foci_word.move_to(focus_words)
        foci_word.shift(MED_SMALL_BUFF * UP)
        connecting_lines = VGroup(*[
            Arrow(
                foci_word.get_edge_center(-edge),
                focus_word.get_edge_center(edge),
                buff=MED_SMALL_BUFF,
                stroke_width=2,
            )
            for focus_word, edge in zip(focus_words, [LEFT, RIGHT])
        ])

        translation = TextMobject(
            "``Foco'' $\\rightarrow$ Fireplace"
        )
        translation.to_edge(RIGHT)
        translation.shift(UP)
        sun = ImageMobject("sun", height=0.5)
        sun.move_to(foci[0])
        sun_animation = SunAnimation(sun)

        self.play(FadeInFromDown(focus_words))
        self.wait(2)
        self.play(
            ReplacementTransform(focus_words.copy(), foci_word),
        )
        self.play(*list(map(ShowCreation, connecting_lines)))
        for word in list(focus_words) + [foci_word]:
            word.add_background_rectangle()
            self.add_foreground_mobjects(word)
        self.wait(4)
        self.play(Write(translation))
        self.wait(2)
        self.play(GrowFromCenter(sun))
        self.add(sun_animation)
        self.wait(8)

    def label_focal_sum(self):
        sum_rect = self.sum_rect

        focal_sum = TextMobject("``Focal sum''")
        focal_sum.scale(1.5)
        focal_sum.next_to(sum_rect, DOWN, aligned_edge=RIGHT)
        VGroup(sum_rect, focal_sum).set_color(RED)

        footnote = TextMobject(
            """
            \\Large
            *This happens to equal the longest distance
            across the ellipse, so perhaps the more standard
            terminology would be ``major axis'', but I want
            some terminology that conveys the idea of adding
            two distances to the foci.
            """,
            alignment="",
        )
        footnote.set_width(5)
        footnote.to_corner(DR)
        footnote.set_stroke(WHITE, 0.5)

        self.play(FadeInFromDown(focal_sum))
        self.play(Write(sum_rect))
        self.wait()
        self.play(FadeIn(footnote))
        self.wait(2)
        self.play(FadeOut(footnote))
        self.wait(8)

    # Helpers
    def get_foci(self):
        ellipse = self.ellipse
        a = ellipse.get_width() / 2
        b = ellipse.get_height() / 2
        c = np.sqrt(a**2 - b**2)
        center = ellipse.get_center()
        return [
            center + c * RIGHT,
            center + c * LEFT,
        ]

    def get_focal_lines_and_update(self, get_foci, focal_sum_point):
        lines = VGroup(Line(LEFT, RIGHT), Line(LEFT, RIGHT))
        lines.set_stroke(width=2)

        def update_lines(lines):
            foci = get_foci()
            for line, focus in zip(lines, foci):
                line.put_start_and_end_on(
                    focus, focal_sum_point.get_center()
                )
            lines[1].rotate(np.pi)
        lines_update_animation = ContinualUpdate(
            lines, update_lines
        )
        return lines, lines_update_animation

    def get_distance_labels_and_update(self, lines, colors):
        distance_labels = VGroup(
            DecimalNumber(0), DecimalNumber(0),
        )
        for label in distance_labels:
            label.scale(self.distance_labels_scale_factor)

        def update_distance_labels(labels):
            for label, line, color in zip(labels, lines, colors):
                angle = -line.get_angle()
                if np.abs(angle) > 90 * DEGREES:
                    angle = 180 * DEGREES + angle
                line.rotate(angle, about_point=ORIGIN)
                new_decimal = DecimalNumber(line.get_length())
                new_decimal.scale(
                    self.distance_labels_scale_factor
                )
                max_width = 0.6 * line.get_width()
                if new_decimal.get_width() > max_width:
                    new_decimal.set_width(max_width)
                new_decimal.next_to(line, UP, SMALL_BUFF)
                new_decimal.set_color(color)
                new_decimal.add_to_back(
                    new_decimal.copy().set_stroke(BLACK, 5)
                )
                VGroup(new_decimal, line).rotate(
                    -angle, about_point=ORIGIN
                )
                label.submobjects = list(new_decimal.submobjects)

        distance_labels_animation = ContinualUpdate(
            distance_labels, update_distance_labels
        )

        return distance_labels, distance_labels_animation

    def get_sum_expression_and_update(self, lines, colors, sum_position_func):
        sum_expression = TexMobject("0.00", "+", "0.00", "=", "0.00")
        sum_position_func(sum_expression)
        number_refs = sum_expression.get_parts_by_tex("0.00")
        number_refs.set_fill(opacity=0)
        numbers = VGroup(*[DecimalNumber(0) for ref in number_refs])
        for number, color in zip(numbers, colors):
            number.set_color(color)

        # Not the most elegant...
        number_updates = [
            ContinualChangingDecimal(
                numbers[0], lambda a: lines[0].get_length(),
                position_update_func=lambda m: m.move_to(
                    number_refs[1], LEFT
                )
            ),
            ContinualChangingDecimal(
                numbers[1], lambda a: lines[1].get_length(),
                position_update_func=lambda m: m.move_to(
                    number_refs[0], LEFT
                )
            ),
            ContinualChangingDecimal(
                numbers[2], lambda a: sum(map(Line.get_length, lines)),
                position_update_func=lambda m: m.move_to(
                    number_refs[2], LEFT
                )
            ),
        ]

        return sum_expression, numbers, number_updates


class GeometryProofLand(Scene):
    CONFIG = {
        "colors": [
            PINK, RED, YELLOW, GREEN, GREEN_A, BLUE,
            MAROON_E, MAROON_B, YELLOW, BLUE,
        ],
        "text": "Geometry proof land",
    }

    def construct(self):
        word = self.get_geometry_proof_land_word()
        word_outlines = word.deepcopy()
        word_outlines.set_fill(opacity=0)
        word_outlines.set_stroke(WHITE, 1)
        colors = list(self.colors)
        random.shuffle(colors)
        word_outlines.set_color_by_gradient(*colors)
        word_outlines.set_stroke(width=5)

        circles = VGroup()
        for letter in word:
            circle = Circle()
            # circle = letter.copy()
            circle.replace(letter, dim_to_match=1)
            circle.scale(3)
            circle.set_stroke(WHITE, 0)
            circle.set_fill(letter.get_color(), 0)
            circles.add(circle)
            circle.target = letter

        self.play(
            LaggedStart(MoveToTarget, circles),
            run_time=2
        )
        self.add(word_outlines, circles)
        self.play(LaggedStart(
            FadeIn, word_outlines,
            run_time=3,
            rate_func=there_and_back,
        ), Animation(circles))
        self.wait()

    def get_geometry_proof_land_word(self):
        word = TextMobject(self.text)
        word.rotate(-90 * DEGREES)
        word.scale(0.25)
        word.shift(3 * RIGHT)
        word.apply_complex_function(np.exp)
        word.rotate(90 * DEGREES)
        word.set_width(9)
        word.center()
        word.to_edge(UP)
        word.set_color_by_gradient(*self.colors)
        word.set_background_stroke(width=0)
        return word


class ProveEllipse(ShowEmergingEllipse, ShowEllipseDefiningProperty):
    CONFIG = {
        "eccentricity_vector": 1.5 * RIGHT,
        "ellipse_color": PINK,
        "distance_labels_scale_factor": 0.7,
    }

    def construct(self):
        self.setup_ellipse()
        self.hypothesize_foci()
        self.setup_and_show_focal_sum()
        self.show_circle_radius()
        self.limit_to_just_one_line()
        self.look_at_perpendicular_bisector()
        self.show_orbiting_planet()

    def setup_ellipse(self):
        circle = self.circle = self.get_circle()
        circle.to_edge(LEFT)
        ep = self.get_eccentricity_point()
        ep_dot = self.ep_dot = Dot(ep, color=YELLOW)
        lines = self.lines = self.get_lines()
        for line in lines:
            line.save_state()
        ghost_lines = self.ghost_lines = self.get_ghost_lines(lines)
        ellipse = self.ellipse = self.get_ellipse()

        self.add(ghost_lines, circle, lines, ep_dot)
        self.play(
            LaggedStart(MoveToTarget, lines),
            Animation(ep_dot),
        )
        self.play(ShowCreation(ellipse))
        self.wait()

    def hypothesize_foci(self):
        circle = self.circle
        ghost_lines = self.ghost_lines
        ghost_lines_copy = ghost_lines.copy().set_stroke(YELLOW, 3)

        center = circle.get_center()
        center_dot = Dot(center, color=RED)
        # ep = self.get_eccentricity_point()
        ep_dot = self.ep_dot
        dots = VGroup(center_dot, ep_dot)

        center_label = TextMobject("Circle center")
        ep_label = TextMobject("Eccentric point")
        labels = VGroup(center_label, ep_label)
        vects = [UL, DR]
        arrows = VGroup()
        for label, dot, vect in zip(labels, dots, vects):
            label.next_to(dot, vect, MED_LARGE_BUFF)
            label.match_color(dot)
            label.add_to_back(
                label.copy().set_stroke(BLACK, 5)
            )
            arrow = Arrow(
                label.get_corner(-vect),
                dot.get_corner(vect),
                buff=SMALL_BUFF
            )
            arrow.match_color(dot)
            arrow.add_to_back(arrow.copy().set_stroke(BLACK, 5))
            arrows.add(arrow)

        labels_target = labels.copy()
        labels_target.arrange_submobjects(
            DOWN, aligned_edge=LEFT
        )
        guess_start = TextMobject("Guess: Foci = ")
        brace = Brace(labels_target, LEFT)
        full_guess = VGroup(guess_start, brace, labels_target)
        full_guess.arrange_submobjects(RIGHT)
        full_guess.to_corner(UR)

        self.play(
            FadeInFromDown(labels[1]),
            GrowArrow(arrows[1]),
        )
        self.play(LaggedStart(
            ShowPassingFlash, ghost_lines_copy
        ))
        self.wait()
        self.play(ReplacementTransform(circle.copy(), center_dot))
        self.add_foreground_mobjects(dots)
        self.play(
            FadeInFromDown(labels[0]),
            GrowArrow(arrows[0]),
        )
        self.wait()
        self.play(
            Write(guess_start),
            GrowFromCenter(brace),
            run_time=1
        )
        self.play(
            ReplacementTransform(labels.copy(), labels_target)
        )
        self.wait()
        self.play(FadeOut(labels), FadeOut(arrows))

        self.center_dot = center_dot

    def setup_and_show_focal_sum(self):
        circle = self.circle
        ellipse = self.ellipse

        focal_sum_point = VectorizedPoint()
        focal_sum_point.move_to(circle.get_top())
        dots = [self.ep_dot, self.center_dot]
        colors = list(map(Mobject.get_color, dots))

        def get_foci():
            return list(map(Mobject.get_center, dots))

        focal_lines, focal_lines_update_animation = \
            self.get_focal_lines_and_update(get_foci, focal_sum_point)
        distance_labels, distance_labels_update_animation = \
            self.get_distance_labels_and_update(focal_lines, colors)
        sum_expression, numbers, number_updates = \
            self.get_sum_expression_and_update(
                focal_lines, colors,
                lambda mob: mob.to_edge(RIGHT).shift(UP)
            )

        to_add = self.focal_sum_things_to_add = [
            focal_lines_update_animation,
            distance_labels_update_animation,
            sum_expression,
        ] + list(number_updates)

        self.play(
            ShowCreation(focal_lines),
            Write(distance_labels),
            FadeIn(sum_expression),
            Write(numbers),
            run_time=1
        )
        self.wait()
        self.add(*to_add)

        points = [
            ellipse.get_top(),
            circle.point_from_proportion(0.2),
            ellipse.point_from_proportion(0.2),
            ellipse.point_from_proportion(0.4),
        ]
        for point in points:
            self.play(
                focal_sum_point.move_to, point
            )
            self.wait()
        self.remove(*to_add)
        self.play(*list(map(FadeOut, [
            focal_lines, distance_labels,
            sum_expression, numbers
        ])))

        self.set_variables_as_attrs(
            focal_lines, focal_lines_update_animation,
            focal_sum_point,
            distance_labels, distance_labels_update_animation,
            sum_expression,
            numbers, number_updates
        )

    def show_circle_radius(self):
        circle = self.circle
        center = circle.get_center()
        point = circle.get_right()
        color = GREEN
        radius = Line(center, point, color=color)
        radius_measurement = DecimalNumber(radius.get_length())
        radius_measurement.set_color(color)
        radius_measurement.next_to(radius, UP, SMALL_BUFF)
        radius_measurement.add_to_back(
            radius_measurement.copy().set_stroke(BLACK, 5)
        )
        group = VGroup(radius, radius_measurement)
        group.rotate(30 * DEGREES, about_point=center)

        self.play(ShowCreation(radius))
        self.play(Write(radius_measurement))
        self.wait()
        self.play(Rotating(
            group,
            rate_func=smooth,
            run_time=7,
            about_point=center
        ))
        self.play(FadeOut(group))

    def limit_to_just_one_line(self):
        lines = self.lines
        ghost_lines = self.ghost_lines
        ep_dot = self.ep_dot

        index = int(0.2 * len(lines))
        line = lines[index]
        ghost_line = ghost_lines[index]
        to_fade = VGroup(*list(lines) + list(ghost_lines))
        to_fade.remove(line, ghost_line)

        P_dot = Dot(line.saved_state.get_end())
        P_label = TexMobject("P")
        P_label.next_to(P_dot, UP, SMALL_BUFF)

        self.add_foreground_mobjects(self.ellipse)
        self.play(LaggedStart(Restore, lines))
        self.play(
            FadeOut(to_fade),
            ghost_line.set_stroke, YELLOW, 3,
            line.set_stroke, WHITE, 3,
            ReplacementTransform(ep_dot.copy(), P_dot),
        )
        self.play(FadeInFromDown(P_label))
        self.wait()

        for l in lines:
            l.generate_target()
            l.target.rotate(
                90 * DEGREES,
                about_point=l.get_center()
            )

        self.set_variables_as_attrs(
            line, ghost_line,
            P_dot, P_label
        )

    def look_at_perpendicular_bisector(self):
        # Alright, this method's gonna blow up.  Let's go!
        circle = self.circle
        ellipse = self.ellipse
        ellipse.save_state()
        lines = self.lines
        line = self.line
        ghost_lines = self.ghost_lines
        ghost_line = self.ghost_line
        P_dot = self.P_dot
        P_label = self.P_label

        elbow = self.get_elbow(line)
        self.play(
            MoveToTarget(line, path_arc=90 * DEGREES),
            ShowCreation(elbow)
        )

        # Perpendicular bisector label
        label = TextMobject("``Perpendicular bisector''")
        label.scale(0.75)
        label.set_color(YELLOW)
        label.next_to(ORIGIN, UP, MED_SMALL_BUFF)
        label.add_background_rectangle()
        angle = line.get_angle() + np.pi
        label.rotate(angle, about_point=ORIGIN)
        label.shift(line.get_center())

        # Dot defining Q point
        Q_dot = Dot(color=GREEN)
        Q_dot.move_to(self.focal_sum_point)
        focal_sum_point_animation = NormalAnimationAsContinualAnimation(
            MaintainPositionRelativeTo(
                self.focal_sum_point, Q_dot
            )
        )
        self.add(focal_sum_point_animation)
        Q_dot.move_to(line.point_from_proportion(0.9))
        Q_dot.save_state()

        Q_label = TexMobject("Q")
        Q_label.scale(0.7)
        Q_label.match_color(Q_dot)
        Q_label.add_to_back(Q_label.copy().set_stroke(BLACK, 5))
        Q_label.next_to(Q_dot, UL, buff=0)
        Q_label_animation = NormalAnimationAsContinualAnimation(
            MaintainPositionRelativeTo(Q_label, Q_dot)
        )

        # Pretty hacky...
        def distance_label_shift_update(label):
            line = self.focal_lines[0]
            if line.get_end()[0] > line.get_start()[0]:
                vect = label.get_center() - line.get_center()
                label.shift(-2 * vect)
        distance_label_shift_update_animation = ContinualUpdate(
            self.distance_labels[0],
            distance_label_shift_update
        )
        self.focal_sum_things_to_add.append(
            distance_label_shift_update_animation
        )

        # Define QP line
        QP_line = Line(LEFT, RIGHT)
        QP_line.match_style(self.focal_lines)
        QP_line_update = ContinualUpdate(
            QP_line, lambda l: l.put_start_and_end_on(
                Q_dot.get_center(), P_dot.get_center(),
            )
        )

        QE_line = Line(LEFT, RIGHT)
        QE_line.set_stroke(YELLOW, 3)
        QE_line_update = ContinualUpdate(
            QE_line, lambda l: l.put_start_and_end_on(
                Q_dot.get_center(),
                self.get_eccentricity_point()
            )
        )

        # Define similar triangles
        triangles = VGroup(*[
            Polygon(
                Q_dot.get_center(),
                line.get_center(),
                end_point,
                fill_opacity=1,
            )
            for end_point in [
                P_dot.get_center(),
                self.get_eccentricity_point()
            ]
        ])
        triangles.set_color_by_gradient(RED_C, COBALT)
        triangles.set_stroke(WHITE, 2)

        # Add even more distant label updates
        def distance_label_rotate_update(label):
            QE_line_update.update(0)
            angle = QP_line.get_angle() - QE_line.get_angle()
            label.rotate(angle, about_point=Q_dot.get_center())
            return label

        distance_label_rotate_update_animation = ContinualUpdate(
            self.distance_labels[0],
            distance_label_rotate_update
        )

        # Hook up line to P to P_dot
        radial_line = DashedLine(ORIGIN, 3 * RIGHT)
        radial_line_update = UpdateFromFunc(
            radial_line, lambda l: l.put_start_and_end_on(
                circle.get_center(),
                P_dot.get_center()
            )
        )

        def put_dot_at_intersection(dot):
            point = line_intersection(
                line.get_start_and_end(),
                radial_line.get_start_and_end()
            )
            dot.move_to(point)
            return dot

        keep_Q_dot_at_intersection = UpdateFromFunc(
            Q_dot, put_dot_at_intersection
        )
        Q_dot.restore()

        ghost_line_update_animation = UpdateFromFunc(
            ghost_line, lambda l: l.put_start_and_end_on(
                self.get_eccentricity_point(),
                P_dot.get_center()
            )
        )

        def update_perp_bisector(line):
            line.scale(ghost_line.get_length() / line.get_length())
            line.rotate(ghost_line.get_angle() - line.get_angle())
            line.rotate(90 * DEGREES)
            line.move_to(ghost_line)
        perp_bisector_update_animation = UpdateFromFunc(
            line, update_perp_bisector
        )
        elbow_update_animation = UpdateFromFunc(
            elbow,
            lambda e: Transform(e, self.get_elbow(ghost_line)).update(1)
        )

        P_dot_movement_updates = [
            radial_line_update,
            keep_Q_dot_at_intersection,
            MaintainPositionRelativeTo(
                P_label, P_dot
            ),
            ghost_line_update_animation,
            perp_bisector_update_animation,
            elbow_update_animation,
        ]

        # Comment for tangency
        sum_rect = SurroundingRectangle(
            self.numbers[-1]
        )
        tangency_comment = TextMobject(
            "Always $\\ge$ radius"
        )
        tangency_comment.next_to(
            sum_rect, DOWN,
            aligned_edge=RIGHT
        )
        VGroup(sum_rect, tangency_comment).set_color(GREEN)

        # Why is this needed?!?
        self.add(*self.focal_sum_things_to_add)
        self.wait(0.01)
        self.remove(*self.focal_sum_things_to_add)

        # Show label
        self.play(Write(label))
        self.wait()

        # Show Q_dot moving about a little
        self.play(
            FadeOut(label),
            FadeIn(self.focal_lines),
            FadeIn(self.distance_labels),
            FadeIn(self.sum_expression),
            FadeIn(self.numbers),
            ellipse.set_stroke, {"width": 0.5},
        )
        self.add(*self.focal_sum_things_to_add)
        self.play(
            FadeInFromDown(Q_label),
            GrowFromCenter(Q_dot)
        )
        self.wait()
        self.add_foreground_mobjects(Q_dot)
        self.add(Q_label_animation)
        self.play(
            Q_dot.move_to, line.point_from_proportion(0.05),
            rate_func=there_and_back,
            run_time=4
        )
        self.wait()

        # Show similar triangles
        self.play(
            FadeIn(triangles[0]),
            ShowCreation(QP_line),
            Animation(elbow),
        )
        self.add(QP_line_update)
        for i in range(3):
            self.play(
                FadeIn(triangles[(i + 1) % 2]),
                FadeOut(triangles[i % 2]),
                Animation(self.distance_labels),
                Animation(elbow)
            )
        self.play(
            FadeOut(triangles[1]),
            Animation(self.distance_labels)
        )

        # Move first distance label
        # (boy, this got messy...hopefully no one ever has
        # to read this.)
        angle = QP_line.get_angle() - QE_line.get_angle()
        Q_point = Q_dot.get_center()
        for x in range(2):
            self.play(ShowCreationThenDestruction(QE_line))
        distance_label_copy = self.distance_labels[0].copy()
        self.play(
            ApplyFunction(
                distance_label_rotate_update,
                distance_label_copy,
                path_arc=angle
            ),
            Rotate(QE_line, angle, about_point=Q_point)
        )
        self.play(FadeOut(QE_line))
        self.remove(distance_label_copy)
        self.add(distance_label_rotate_update_animation)
        self.focal_sum_things_to_add.append(
            distance_label_rotate_update_animation
        )
        self.wait()
        self.play(
            Q_dot.move_to, line.point_from_proportion(0),
            run_time=4,
            rate_func=there_and_back
        )

        # Trace out ellipse
        self.play(ShowCreation(radial_line))
        self.wait()
        self.play(
            ApplyFunction(put_dot_at_intersection, Q_dot),
            run_time=3,
        )
        self.wait()
        self.play(
            Rotating(
                P_dot,
                about_point=circle.get_center(),
                rate_func=bezier([0, 0, 1, 1]),
                run_time=10,
            ),
            ellipse.restore,
            *P_dot_movement_updates
        )
        self.wait()

        # Talk through tangency
        self.play(
            ShowCreation(sum_rect),
            Write(tangency_comment),
        )
        points = [line.get_end(), line.get_start(), Q_dot.get_center()]
        run_times = [1, 3, 2]
        for point, run_time in zip(points, run_times):
            self.play(Q_dot.move_to, point, run_time=run_time)
        self.wait()

        self.remove(*self.focal_sum_things_to_add)
        self.play(*list(map(FadeOut, [
            radial_line,
            QP_line,
            P_dot, P_label,
            Q_dot, Q_label,
            elbow,
            self.distance_labels,
            self.numbers,
            self.sum_expression,
            sum_rect,
            tangency_comment,
        ])))
        self.wait()

        # Show all lines
        lines.remove(line)
        ghost_lines.remove(ghost_line)
        for line in lines:
            line.generate_target()
            line.target.rotate(90 * DEGREES)
        self.play(
            LaggedStart(FadeIn, ghost_lines),
            LaggedStart(FadeIn, lines),
        )
        self.play(LaggedStart(MoveToTarget, lines))
        self.wait()

    def show_orbiting_planet(self):
        ellipse = self.ellipse
        ep_dot = self.ep_dot
        planet = ImageMobject("earth")
        planet.set_height(0.25)
        orbit = Orbiting(planet, ep_dot, ellipse)

        lines = self.lines

        def update_lines(lines):
            for gl, line in zip(self.ghost_lines, lines):
                intersection = line_intersection(
                    [self.circle.get_center(), gl.get_end()],
                    line.get_start_and_end()
                )
                distance = get_norm(
                    intersection - planet.get_center()
                )
                if distance < 0.025:
                    line.set_stroke(BLUE, 3)
                    self.add(line)
                else:
                    line.set_stroke(WHITE, 1)

        lines_update_animation = ContinualUpdate(
            lines, update_lines
        )

        self.add(orbit)
        self.add(lines_update_animation)
        self.add_foreground_mobjects(planet)
        self.wait(12)


class Enthusiast(Scene):
    def construct(self):
        randy = Randolph(color=BLUE_C)
        randy.flip()
        self.play(randy.change, "surprised")
        self.play(Blink(randy))
        self.wait()


class SimpleThinking(Scene):
    def construct(self):
        randy = Randolph(color=BLUE_C)
        randy.flip()
        self.play(randy.change, "thinking", 3 * UP)
        self.play(Blink(randy))
        self.wait()
        self.play(randy.change, "hooray", 3 * UP)
        self.play(Blink(randy))
        self.wait()


class EndOfGeometryProofiness(GeometryProofLand):
    def construct(self):
        geometry_word = self.get_geometry_proof_land_word()
        orbital_mechanics = TextMobject("Orbital Mechanics")
        orbital_mechanics.scale(1.5)
        orbital_mechanics.to_edge(UP)
        underline = Line(LEFT, RIGHT)
        underline.match_width(orbital_mechanics)
        underline.next_to(orbital_mechanics, DOWN, SMALL_BUFF)

        self.play(LaggedStart(FadeOutAndShiftDown, geometry_word))
        self.play(FadeInFromDown(orbital_mechanics))
        self.play(ShowCreation(underline))
        self.wait()


class KeplersSecondLaw(AskAboutEllipses):
    CONFIG = {
        "sun_center": 4 * RIGHT + 0.75 * DOWN,
        "animate_sun": True,
        "a": 5.0,
        "b": 3.0,
        "ellipse_stroke_width": 2,
        "area_color": COBALT,
        "area_opacity": 0.75,
        "arc_color": YELLOW,
        "arc_stroke_width": 3,
        "n_sample_sweeps": 5,
        "fade_sample_areas": True,
    }

    def construct(self):
        self.add_title()
        self.add_sun()
        self.add_orbit()
        self.add_foreground_mobjects(self.comet)

        self.show_several_sweeps()
        self.contrast_close_to_far()

    def add_title(self):
        title = TextMobject("Kepler's 2nd law:")
        title.scale(1.0)
        title.to_edge(UP)
        self.add(title)
        self.title = title

        subtitle = TextMobject(
            "Orbits sweep a constant area per unit time"
        )
        subtitle.next_to(title, DOWN, buff=0.2)
        subtitle.set_color(BLUE)
        self.add(subtitle)

    def show_several_sweeps(self):
        shown_areas = VGroup()
        for x in range(self.n_sample_sweeps):
            self.wait()
            area = self.show_area_sweep()
            shown_areas.add(area)
        self.wait()
        if self.fade_sample_areas:
            self.play(FadeOut(shown_areas))

    def contrast_close_to_far(self):
        orbit = self.orbit
        sun_point = self.sun.get_center()

        start_prop = 0.9
        self.wait_until_proportion(start_prop)
        self.show_area_sweep()
        end_prop = orbit.proportion
        arc = self.get_arc(start_prop, end_prop)
        radius = Line(sun_point, arc.points[0])
        radius.set_color(WHITE)

        radius_words = self.get_radius_words(radius, "Short")
        radius_words.next_to(radius.get_center(), LEFT, SMALL_BUFF)

        arc_words = TextMobject("Long arc")
        arc_words.rotate(90 * DEGREES)
        arc_words.scale(0.5)
        arc_words.next_to(RIGHT, RIGHT)
        arc_words.apply_complex_function(np.exp)
        arc_words.scale(0.8)
        arc_words.next_to(
            arc, RIGHT, buff=-SMALL_BUFF
        )
        arc_words.shift(4 * SMALL_BUFF * DOWN)
        arc_words.match_color(arc)

        # Show stubby arc
        # self.remove(orbit)
        # self.add(self.comet)
        self.play(
            ShowCreation(radius),
            Write(radius_words),
        )
        self.play(
            ShowCreation(arc),
            Write(arc_words)
        )

        # Show narrow arc
        # (Code repetition...uck)
        start_prop = 0.475
        self.wait_until_proportion(start_prop)
        self.show_area_sweep()
        end_prop = orbit.proportion
        short_arc = self.get_arc(start_prop, end_prop)
        long_radius = Line(sun_point, short_arc.points[0])
        long_radius.set_color(WHITE)
        long_radius_words = self.get_radius_words(long_radius, "Long")

        short_arc_words = TextMobject("Short arc")
        short_arc_words.scale(0.5)
        short_arc_words.rotate(90 * DEGREES)
        short_arc_words.next_to(short_arc, LEFT, SMALL_BUFF)
        short_arc_words.match_color(short_arc)

        self.play(
            ShowCreation(long_radius),
            Write(long_radius_words),
        )
        self.play(
            ShowCreation(short_arc),
            Write(short_arc_words)
        )
        self.wait(15)

    # Helpers
    def show_area_sweep(self, time=1.0):
        orbit = self.orbit
        start_prop = orbit.proportion
        area = self.get_area(start_prop, start_prop)
        area_update = UpdateFromFunc(
            area,
            lambda a: Transform(
                a, self.get_area(start_prop, orbit.proportion)
            ).update(1)
        )

        self.play(area_update, run_time=time)

        return area

    def get_area(self, prop1, prop2):
        """
        Return a mobject illustrating the area swept
        out between a point prop1 of the way along
        the ellipse, and prop2 of the way.
        """
        sun_point = self.sun.get_center()
        arc = self.get_arc(prop1, prop2)

        # Add lines from start
        result = VMobject()
        result.append_vectorized_mobject(
            Line(sun_point, arc.points[0])
        )
        result.append_vectorized_mobject(arc)
        result.append_vectorized_mobject(
            Line(arc.points[-1], sun_point)
        )

        result.set_stroke(WHITE, width=0)
        result.set_fill(
            self.area_color,
            self.area_opacity,
        )
        return result

    def get_arc(self, prop1, prop2):
        ellipse = self.get_ellipse()
        prop1 = prop1 % 1.0
        prop2 = prop2 % 1.0

        if prop2 > prop1:
            arc = VMobject().pointwise_become_partial(
                ellipse, prop1, prop2
            )
        elif prop1 > prop2:
            arc, arc_extension = [
                VMobject().pointwise_become_partial(
                    ellipse, p1, p2
                )
                for p1, p2 in [(prop1, 1.0), (0.0, prop2)]
            ]
            arc.append_vectorized_mobject(arc_extension)
        else:
            arc = VectorizedPoint(
                ellipse.point_from_proportion(prop1)
            )

        arc.set_stroke(
            self.arc_color,
            self.arc_stroke_width,
        )

        return arc

    def wait_until_proportion(self, prop):
        if self.skip_animations:
            self.orbit.proportion = prop
        else:
            while (self.orbit.proportion % 1) < prop:
                self.wait(self.frame_duration)

    def get_radius_words(self, radius, adjective):
        radius_words = TextMobject(
            "%s radius" % adjective,
        )
        min_width = 0.8 * radius.get_length()
        if radius_words.get_width() > min_width:
            radius_words.set_width(min_width)
        radius_words.match_color(radius)
        radius_words.next_to(ORIGIN, UP, SMALL_BUFF)
        angle = radius.get_angle()
        angle = ((angle + PI) % TAU) - PI
        if np.abs(angle) > PI / 2:
            angle += PI
        radius_words.rotate(angle, about_point=ORIGIN)
        radius_words.shift(radius.get_center())
        return radius_words


class NonEllipticalKeplersLaw(KeplersSecondLaw):
    CONFIG = {
        "animate_sun": True,
        "sun_center": 2 * RIGHT,
        "n_sample_sweeps": 10,
    }

    def construct(self):
        self.add_sun()
        self.add_orbit()
        self.show_several_sweeps()

    def add_orbit(self):
        sun = self.sun
        comet = ImageMobject("comet", height=0.5)
        orbit_shape = self.get_ellipse()

        orbit = self.orbit = Orbiting(comet, sun, orbit_shape)
        self.add(orbit_shape)
        self.add(orbit)

        arrow, arrow_update = self.get_force_arrow_and_update(
            comet
        )
        alt_arrow_update = ContinualUpdate(
            arrow, lambda a: a.scale(
                1.0 / a.get_length(),
                about_point=a.get_start()
            )
        )
        self.add(arrow_update, alt_arrow_update)
        self.add_foreground_mobjects(comet, arrow)

        self.ellipse = orbit_shape

    def get_ellipse(self):
        orbit_shape = ParametricFunction(
            lambda t: (1 + 0.2 * np.sin(5 * TAU * t)) * np.array([
                np.cos(TAU * t),
                np.sin(TAU * t),
                0
            ])
        )
        orbit_shape.set_height(7)
        orbit_shape.stretch(1.5, 0)
        orbit_shape.shift(LEFT)
        orbit_shape.set_stroke(LIGHT_GREY, 1)
        return orbit_shape


class AngularMomentumArgument(KeplersSecondLaw):
    CONFIG = {
        "animate_sun": False,
        "sun_center": 4 * RIGHT + DOWN,
        "comet_start_point": 4 * LEFT,
        "comet_end_point": 5 * LEFT + DOWN,
        "comet_height": 0.3,
    }

    def construct(self):
        self.add_sun()
        self.show_small_sweep()
        self.show_sweep_dimensions()
        self.show_conservation_of_angular_momentum()

    def show_small_sweep(self):
        sun_center = self.sun_center
        comet_start = self.comet_start_point
        comet_end = self.comet_end_point
        triangle = Polygon(
            sun_center, comet_start, comet_end,
            fill_opacity=1,
            fill_color=COBALT,
            stroke_width=0,
        )
        triangle.save_state()
        alt_triangle = Polygon(
            sun_center,
            interpolate(comet_start, comet_end, 0.9),
            comet_end
        )
        alt_triangle.match_style(triangle)

        comet = self.get_comet()
        comet.move_to(comet_start)

        velocity_vector = Arrow(
            comet_start, comet_end,
            color=WHITE,
            buff=0
        )
        velocity_vector_label = TexMobject("\\vec{\\textbf{v}}")
        velocity_vector_label.next_to(
            velocity_vector.get_center(), UL,
            buff=SMALL_BUFF
        )

        small_time_label = TextMobject(
            "Small", "time", "$\\Delta t$",
        )
        small_time_label.to_edge(UP)
        small = small_time_label.get_part_by_tex("Small")
        small_rect = SurroundingRectangle(small)

        self.add_foreground_mobjects(comet)
        self.play(
            ShowCreation(
                triangle,
                rate_func=lambda t: interpolate(1.0 / 3, 2.0 / 3, t)
            ),
            MaintainPositionRelativeTo(
                velocity_vector, comet
            ),
            MaintainPositionRelativeTo(
                velocity_vector_label,
                velocity_vector,
            ),
            ApplyMethod(
                comet.move_to, comet_end,
                rate_func=None,
            ),
            run_time=2,
        )
        self.play(Write(small_time_label), run_time=2)
        self.wait()
        self.play(
            Transform(triangle, alt_triangle),
            ShowCreation(small_rect),
            small.set_color, YELLOW,
        )
        self.wait()
        self.play(
            Restore(triangle),
            FadeOut(small_rect),
            small.set_color, WHITE,
        )
        self.wait()

        self.triangle = triangle
        self.comet = comet
        self.delta_t = small_time_label.get_part_by_tex(
            "$\\Delta t$"
        )
        self.velocity_vector = velocity_vector
        self.small_time_label = small_time_label

    def show_sweep_dimensions(self):
        triangle = self.triangle
        # velocity_vector = self.velocity_vector
        delta_t = self.delta_t
        comet = self.comet

        triangle_points = triangle.get_anchors()[:3]
        top = triangle_points[1]

        area_label = TexMobject(
            "\\text{Area}", "=", "\\frac{1}{2}",
            "\\text{Base}", "\\times", "\\text{Height}",
        )
        area_label.set_color_by_tex_to_color_map({
            "Base": PINK,
            "Height": YELLOW,
        })
        area_label.to_edge(UP)
        equals = area_label.get_part_by_tex("=")
        area_expression = TexMobject(
            "=", "\\frac{1}{2}", "R", "\\times",
            "\\vec{\\textbf{v}}_\\perp",
            "\\Delta t",
        )
        area_expression.set_color_by_tex_to_color_map({
            "R": PINK,
            "textbf{v}": YELLOW,
        })
        area_expression.next_to(area_label, DOWN)
        area_expression.align_to(equals, LEFT)

        self.R_v_perp = VGroup(*area_expression[-4:-1])
        self.R_v_perp_rect = SurroundingRectangle(
            self.R_v_perp,
            stroke_color=BLUE,
            fill_color=BLACK,
            fill_opacity=1,
        )

        base = Line(triangle_points[2], triangle_points[0])
        base.set_stroke(PINK, 3)
        base_point = line_intersection(
            base.get_start_and_end(),
            [top, top + DOWN]
        )
        height = Line(top, base_point)
        height.set_stroke(YELLOW, 3)

        radius_label = TextMobject("Radius")
        radius_label.next_to(base, DOWN, SMALL_BUFF)
        radius_label.match_color(base)

        R_term = area_expression.get_part_by_tex("R")
        R_term.save_state()
        R_term.move_to(radius_label[0])
        R_term.set_fill(opacity=0.5)

        v_perp = Arrow(*height.get_start_and_end(), buff=0)
        v_perp.set_color(YELLOW)
        v_perp.shift(comet.get_center() - v_perp.get_start())
        v_perp_label = TexMobject(
            "\\vec{\\textbf{v}}_\\perp"
        )
        v_perp_label.set_color(YELLOW)
        v_perp_label.next_to(v_perp, RIGHT, buff=SMALL_BUFF)

        v_perp_delta_t = VGroup(v_perp_label.copy(), delta_t.copy())
        v_perp_delta_t.generate_target()
        v_perp_delta_t.target.arrange_submobjects(RIGHT, buff=SMALL_BUFF)
        v_perp_delta_t.target.next_to(height, RIGHT, SMALL_BUFF)
        self.small_time_label.add(v_perp_delta_t[1])

        self.play(
            FadeInFromDown(area_label),
            self.small_time_label.scale, 0.5,
            self.small_time_label.to_corner, UL,
        )
        self.wait()
        self.play(
            ShowCreation(base),
            Write(radius_label),
        )
        self.wait()
        self.play(ShowCreation(height))
        self.wait()
        self.play(
            GrowArrow(v_perp),
            Write(v_perp_label, run_time=1),
        )
        self.wait()
        self.play(MoveToTarget(v_perp_delta_t))
        self.wait()
        self.play(*[
            ReplacementTransform(
                area_label.get_part_by_tex(tex).copy(),
                area_expression.get_part_by_tex(tex),
            )
            for tex in ("=", "\\frac{1}{2}", "\\times")
        ])
        self.play(Restore(R_term))
        self.play(ReplacementTransform(
            v_perp_delta_t.copy(),
            VGroup(*area_expression[-2:])
        ))
        self.wait()

    def show_conservation_of_angular_momentum(self):
        R_v_perp = self.R_v_perp
        R_v_perp_rect = self.R_v_perp_rect
        sun_center = self.sun_center
        comet = self.comet
        comet.save_state()

        vector_field = VectorField(
            get_force_field_func((sun_center, -1))
        )
        vector_field.set_fill(opacity=0.8)
        vector_field.sort_submobjects(
            lambda p: -get_norm(p - sun_center)
        )

        stays_constant = TextMobject("Stays constant")
        stays_constant.next_to(
            R_v_perp_rect, DR, buff=MED_LARGE_BUFF
        )
        stays_constant.match_color(R_v_perp_rect)
        stays_constant_arrow = Arrow(
            stays_constant.get_left(),
            R_v_perp_rect.get_bottom(),
            color=R_v_perp_rect.get_color()
        )

        sun_dot = Dot(sun_center, fill_opacity=0.25)
        big_dot = Dot(fill_opacity=0, radius=FRAME_WIDTH)

        R_v_perp.save_state()
        R_v_perp.generate_target()
        R_v_perp.target.to_edge(LEFT, buff=MED_LARGE_BUFF)
        lp, rp = parens = TexMobject("()")
        lp.next_to(R_v_perp.target, LEFT)
        rp.next_to(R_v_perp.target, RIGHT)

        self.play(Transform(
            big_dot, sun_dot,
            run_time=1,
            remover=True
        ))
        self.wait()
        self.play(
            DrawBorderThenFill(R_v_perp_rect),
            Animation(R_v_perp),
            Write(stays_constant, run_time=1),
            GrowArrow(stays_constant_arrow),
        )
        self.wait()
        foreground = VGroup(*self.get_mobjects())
        self.play(
            LaggedStart(GrowArrow, vector_field),
            Animation(foreground)
        )
        for x in range(3):
            self.play(
                LaggedStart(
                    ApplyFunction, vector_field,
                    lambda mob: (lambda m: m.scale(1.1).set_fill(opacity=1), mob),
                    rate_func=there_and_back,
                    run_time=1
                ),
                Animation(foreground)
            )
        self.play(
            FadeIn(parens),
            MoveToTarget(R_v_perp),
        )
        self.play(
            comet.scale, 2,
            comet.next_to, parens, RIGHT, {"buff": SMALL_BUFF}
        )
        self.wait()
        self.play(
            FadeOut(parens),
            R_v_perp.restore,
            comet.restore,
        )
        self.wait(3)


class KeplersSecondLawImage(KeplersSecondLaw):
    CONFIG = {
        "animate_sun": False,
        "n_sample_sweeps": 8,
        "fade_sample_areas": False,
    }

    def construct(self):
        self.add_sun()
        self.add_foreground_mobjects(self.sun)
        self.add_orbit()
        self.add_foreground_mobjects(self.comet)
        self.show_several_sweeps()


class HistoryOfAngularMomentum(TeacherStudentsScene):
    CONFIG = {
        "camera_config": {"fill_opacity": 1}
    }

    def construct(self):
        am = VGroup(TextMobject("Angular momentum"))
        k2l = TextMobject("Kepler's 2nd law")
        arrow = Arrow(ORIGIN, RIGHT)

        group = VGroup(am, arrow, k2l)
        group.arrange_submobjects(RIGHT)
        group.next_to(self.hold_up_spot, UL)

        k2l_image = ImageMobject("Kepler2ndLaw")
        k2l_image.match_width(k2l)
        k2l_image.next_to(k2l, UP)
        k2l.add(k2l_image)

        angular_momentum_formula = TexMobject(
            "R", "\\times", "m", "\\vec{\\textbf{v}}_\\perp",
        )
        angular_momentum_formula.set_color_by_tex_to_color_map({
            "R": PINK,
            "v": YELLOW,
        })
        angular_momentum_formula.next_to(am, UP)
        am.add(angular_momentum_formula)

        self.play(
            self.teacher.change, "raise_right_hand",
            FadeInFromDown(group),
            self.get_student_changes(*3 * ["pondering"])
        )
        self.wait()
        self.play(
            am.next_to, arrow, RIGHT,
            {"index_of_submobject_to_align": 0},
            k2l.next_to, arrow, LEFT,
            {"index_of_submobject_to_align": 0},
            path_arc=90 * DEGREES,
            run_time=2
        )
        self.wait(3)


class FeynmanRecountingNewton(Scene):
    CONFIG = {
        "camera_config": {"background_opacity": 1},
    }

    def construct(self):
        feynman_teaching = ImageMobject("Feynman_teaching")
        feynman_teaching.set_width(FRAME_WIDTH)

        newton = ImageMobject("Newton")
        principia = ImageMobject("Principia_equal_area")
        images = [newton, principia]
        for image in images:
            image.set_height(5)
        newton.to_corner(UL)
        principia.next_to(newton, RIGHT)
        for image in images:
            image.rect = SurroundingRectangle(
                image, color=WHITE, buff=0,
            )

        self.play(FadeInFromDown(feynman_teaching, run_time=2))
        self.wait()
        self.play(
            FadeInFromDown(newton),
            FadeInFromDown(newton.rect),
        )
        self.wait()
        self.play(*[
            FadeInAndShiftFromDirection(
                mob, direction=3 * LEFT
            )
            for mob in (principia, principia.rect)
        ])
        self.wait()


class IntroduceShapeOfVelocities(AskAboutEllipses, MovingCameraScene):
    CONFIG = {
        "animate_sun": True,
        "sun_center": 2 * RIGHT,
        "a": 4.0,
        "b": 3.5,
        "num_vectors": 25,
    }

    def construct(self):
        self.setup_orbit()
        self.warp_orbit()
        self.reference_inverse_square_law()
        self.show_velocity_vectors()
        self.collect_velocity_vectors()

    def setup_orbit(self):
        self.add_sun()
        self.add_orbit()
        self.add_foreground_mobjects(self.comet)

    def warp_orbit(self):
        def func(z, c=3.5):
            return 1 * (np.exp((1.0 / c) * (z) + 1) - np.exp(1))

        ellipse = self.ellipse
        ellipse.save_state()
        ellipse.generate_target()
        ellipse.target.stretch(0.7, 1)
        ellipse.target.apply_complex_function(func)
        ellipse.target.replace(ellipse, dim_to_match=1)

        self.wait(5)
        self.play(MoveToTarget(ellipse, run_time=2))
        self.wait(5)

    def reference_inverse_square_law(self):
        ellipse = self.ellipse
        force_equation = TexMobject(
            "F", "=", "{G", "M", "m", "\\over", "R^2}"
        )
        force_equation.move_to(ellipse)
        force_equation.set_color_by_tex("F", YELLOW)

        force_arrow, force_arrow_update = self.get_force_arrow_and_update(
            self.comet, scale_factor=3,
        )
        radial_line, radial_line_update = self.get_radial_line_and_update(
            self.comet
        )

        self.add(radial_line_update)
        self.add(force_arrow_update)
        self.play(
            Restore(ellipse),
            Write(force_equation),
            UpdateFromAlphaFunc(
                force_arrow,
                lambda m, a: m.set_fill(opacity=a)
            ),
            UpdateFromAlphaFunc(
                radial_line,
                lambda m, a: m.set_stroke(width=a)
            ),
        )
        self.wait(10)

    def show_velocity_vectors(self):
        alphas = np.linspace(0, 1, self.num_vectors, endpoint=False)
        vectors = VGroup(*[
            self.get_velocity_vector(alpha)
            for alpha in alphas
        ])

        moving_vector, moving_vector_animation = self.get_velocity_vector_and_update()

        self.play(LaggedStart(
            ShowCreation, vectors,
            lag_ratio=0.2,
            run_time=3,
        ))
        self.wait(5)

        self.add(moving_vector_animation)
        self.play(
            FadeOut(vectors),
            VFadeIn(moving_vector)
        )
        self.wait(10)
        vectors.set_fill(opacity=0.5)
        self.play(
            LaggedStart(ShowCreation, vectors),
            Animation(moving_vector)
        )
        self.wait(5)

        self.velocity_vectors = vectors
        self.moving_vector = moving_vector

    def collect_velocity_vectors(self):
        vectors = self.velocity_vectors.copy()
        frame = self.camera_frame
        ellipse = self.ellipse

        frame_shift = 2.5 * LEFT
        root_point = ellipse.get_left() + 3 * LEFT + 1 * UP
        vector_targets = VGroup()
        for vector in vectors:
            vector.target = Arrow(
                root_point,
                root_point + vector.get_vector(),
                buff=0,
                rectangular_stem_width=0.025,
                tip_length=0.2,
                color=vector.get_color(),
            )
            vector.target.add_to_back(
                vector.target.copy().set_stroke(BLACK, 5)
            )
            vector_targets.add(vector.target)

        circle = Circle(color=YELLOW)
        circle.replace(vector_targets)
        circle.scale(1.04)

        velocity_space = TextMobject("Velocity space")
        velocity_space.next_to(circle, UP)

        rect = SurroundingRectangle(
            VGroup(circle, velocity_space),
            buff=MED_LARGE_BUFF,
            color=WHITE,
        )

        self.play(
            ApplyMethod(
                frame.shift, frame_shift,
                run_time=2,
            ),
            LaggedStart(
                MoveToTarget, vectors,
                run_time=4,
            ),
            FadeInFromDown(velocity_space),
            FadeInFromDown(rect),
        )
        self.wait(2)
        self.play(
            ShowCreation(circle),
            Animation(vectors)
        )
        self.wait(24)

    # Helpers
    def get_velocity_vector(self, alpha, d_alpha=0.01, scalar=3.0):
        norm = get_norm
        ellipse = self.ellipse
        sun_center = self.sun.get_center()

        min_length = 0.1 * scalar
        max_length = 0.5 * scalar

        p1, p2 = [
            ellipse.point_from_proportion(a)
            for a in (alpha, alpha + d_alpha)
        ]
        vector = Arrow(
            p1, p2, buff=0
        )
        radius_vector = p1 - sun_center
        curr_v_perp = norm(np.cross(
            vector.get_vector(),
            radius_vector / norm(radius_vector)
        ))
        vector.scale(
            scalar / (norm(curr_v_perp) * norm(radius_vector)),
            about_point=vector.get_start()
        )
        vector.set_color(
            interpolate_color(
                BLUE, RED, inverse_interpolate(
                    min_length, max_length,
                    vector.get_length()
                )
            )
        )
        vector.add_to_back(
            vector.copy().set_stroke(BLACK, 5)
        )
        return vector

    def get_velocity_vector_and_update(self):
        moving_vector = self.get_velocity_vector(0)

        def update_moving_vector(vector):
            new_vector = self.get_velocity_vector(
                self.orbit.proportion,
            )
            Transform(vector, new_vector).update(1)

        moving_vector_animation = ContinualUpdate(
            moving_vector, update_moving_vector
        )
        return moving_vector, moving_vector_animation


class AskWhy(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Um...why?",
            target_mode="confused",
            student_index=2,
            bubble_kwargs={"direction": LEFT},
        )
        self.play(
            self.teacher.change, "happy",
            self.get_student_changes(
                "raise_left_hand", "sassy", "confused"
            )
        )
        self.wait(5)


class FeynmanConfusedByNewton(Scene):
    def construct(self):
        pass


class ShowEqualAngleSlices(IntroduceShapeOfVelocities):
    CONFIG = {
        "animate_sun": True,
        "theta": 30 * DEGREES,
    }

    def construct(self):
        self.setup_orbit()
        self.show_equal_angle_slices()
        self.ask_about_time_per_slice()
        self.areas_are_proportional_to_radius_squared()
        self.show_inverse_square_law()
        self.directly_compare_velocity_vectors()

    def setup_orbit(self):
        IntroduceShapeOfVelocities.setup_orbit(self)
        self.remove(self.orbit)
        self.add(self.comet)

    def show_equal_angle_slices(self):
        sun_center = self.sun.get_center()
        ellipse = self.ellipse

        def get_cos_angle_diff(v1, v2):
            return np.dot(
                v1 / get_norm(v1),
                v2 / get_norm(v2),
            )

        lines = VGroup()
        angle_arcs = VGroup()
        thetas = VGroup()
        angles = np.arange(0, TAU, self.theta)
        for angle in angles:
            prop = angle / TAU
            vect = rotate_vector(RIGHT, angle)
            end_point = ellipse.point_from_proportion(prop)
            curr_cos = get_cos_angle_diff(
                end_point - sun_center, vect
            )
            coss_diff = (1 - curr_cos)
            while abs(coss_diff) > 0.00001:
                d_prop = 0.001
                alt_end = ellipse.point_from_proportion(
                    (prop + d_prop) % 1
                )
                alt_cos = get_cos_angle_diff(alt_end - sun_center, vect)
                d_cos = (alt_cos - curr_cos)

                delta_prop = (coss_diff / d_cos) * d_prop
                prop += delta_prop
                end_point = ellipse.point_from_proportion(prop)
                curr_cos = get_cos_angle_diff(end_point - sun_center, vect)
                coss_diff = 1 - curr_cos

            line = Line(sun_center, end_point)
            line.prop = prop
            lines.add(line)

            angle_arc = AnnularSector(
                angle=self.theta,
                inner_radius=1,
                outer_radius=1.05,
            )
            angle_arc.rotate(angle, about_point=ORIGIN)
            angle_arc.scale(0.5, about_point=ORIGIN)
            angle_arc.shift(sun_center)
            angle_arc.mid_angle = angle + self.theta / 2
            angle_arcs.add(angle_arc)

            theta = TexMobject("\\theta")
            theta.scale(0.6)
            vect = rotate_vector(RIGHT, angle_arc.mid_angle)
            theta.move_to(
                angle_arc.get_center() + 0.2 * vect
            )
            thetas.add(theta)

        arcs = VGroup()
        wedges = VGroup()
        for l1, l2 in adjacent_pairs(lines):
            arc = VMobject()
            arc.pointwise_become_partial(
                ellipse, l1.prop, (l2.prop or 1.0)
            )
            arcs.add(arc)

            wedge = VMobject()
            wedge.append_vectorized_mobject(
                Line(sun_center, arc.points[0])
            )
            wedge.append_vectorized_mobject(arc)
            wedge.append_vectorized_mobject(
                Line(arc.points[-1], sun_center)
            )
            wedges.add(wedge)

        lines.set_stroke(LIGHT_GREY, 2)
        angle_arcs.set_color_by_gradient(
            YELLOW, BLUE, RED, PINK, YELLOW
        )
        arcs.set_color_by_gradient(BLUE, YELLOW)
        wedges.set_stroke(width=0)
        wedges.set_fill(opacity=1)
        wedges.set_color_by_gradient(BLUE, COBALT, BLUE_E, BLUE)

        kwargs = {
            "run_time": 6,
            "lag_ratio": 0.2,
            "rate_func": there_and_back,
        }
        faders = VGroup(wedges, angle_arcs, thetas)
        faders.set_fill(opacity=0.4)
        thetas.set_fill(opacity=0)

        self.play(
            FadeIn(faders),
            *list(map(ShowCreation, lines))
        )
        self.play(*[
            LaggedStart(
                ApplyMethod, fader,
                lambda m: (m.set_fill, {"opacity": 1}),
                **kwargs
            )
            for fader in faders
        ] + [Animation(lines)])
        self.wait()

        self.lines = lines
        self.wedges = wedges
        self.arcs = arcs
        self.angle_arcs = angle_arcs
        self.thetas = thetas

    def ask_about_time_per_slice(self):
        wedge1 = self.wedges[0]
        wedge2 = self.wedges[len(self.wedges) / 2]
        arc1 = self.arcs[0]
        arc2 = self.arcs[len(self.arcs) / 2]
        comet = self.comet
        frame = self.camera_frame

        words1 = TextMobject(
            "Time spent \\\\ traversing \\\\ this slice?"
        )
        words2 = TextMobject("How about \\\\ this one?")

        words1.to_corner(UR)
        words2.next_to(wedge2, LEFT, MED_LARGE_BUFF)

        arrow1 = Arrow(
            words1.get_bottom(),
            wedge1.get_center() + wedge1.get_height() * DOWN / 2,
            color=WHITE,
        )
        arrow2 = Arrow(
            words2.get_right(),
            wedge2.get_center() + wedge2.get_height() * UL / 4,
            color=WHITE
        )

        foreground = VGroup(
            self.ellipse, self.angle_arcs,
            self.lines, comet,
        )
        self.play(
            Write(words1),
            wedge1.set_fill, {"opacity": 1},
            GrowArrow(arrow1),
            Animation(foreground),
            frame.scale, 1.2,
        )
        self.play(MoveAlongPath(comet, arc1, rate_func=None))
        self.play(
            Write(words2),
            wedge2.set_fill, {"opacity": 1},
            Write(arrow2),
            Animation(foreground),
        )
        self.play(MoveAlongPath(comet, arc2, rate_func=None, run_time=3))
        self.wait()

        self.area_questions = VGroup(words1, words2)
        self.area_question_arrows = VGroup(arrow1, arrow2)
        self.highlighted_wedges = VGroup(wedge1, wedge2)

    def areas_are_proportional_to_radius_squared(self):
        wedges = self.highlighted_wedges
        wedge = wedges[1]
        frame = self.camera_frame
        ellipse = self.ellipse
        sun_center = self.sun.get_center()

        line = self.lines[len(self.lines) / 2]
        thick_line = line.copy().set_stroke(PINK, 4)
        radius_word = TextMobject("Radius")
        radius_word.next_to(thick_line, UP, SMALL_BUFF)
        radius_word.match_color(thick_line)

        arc = self.arcs[len(self.arcs) / 2]
        thick_arc = arc.copy().set_stroke(RED, 4)

        scaling_group = VGroup(
            wedge, thick_line, radius_word, thick_arc
        )

        expression = TextMobject(
            "Time", "$\\propto$",
            "Area", "$\\propto$", "$(\\text{Radius})^2$"
        )
        expression.next_to(ellipse, UP, LARGE_BUFF)

        prop_to_brace = Brace(expression[1], DOWN, buff=SMALL_BUFF)
        prop_to_words = TextMobject("(proportional to)")
        prop_to_words.scale(0.7)
        prop_to_words.next_to(prop_to_brace, DOWN, SMALL_BUFF)
        VGroup(prop_to_words, prop_to_brace).set_color(GREEN)

        self.play(
            Write(expression[:3]),
            frame.shift, 0.5 * UP,
            FadeInFromDown(prop_to_words),
            GrowFromCenter(prop_to_brace),
        )
        self.wait(2)
        self.play(
            ShowCreation(thick_line),
            FadeInFromDown(radius_word)
        )
        self.wait()
        self.play(ShowCreationThenDestruction(thick_arc))
        self.play(ShowCreation(thick_arc))
        self.wait()
        self.play(Write(expression[3:]))
        self.play(
            scaling_group.scale, 0.5,
            {"about_point": sun_center},
            Animation(self.area_question_arrows),
            Animation(self.comet),
            rate_func=there_and_back,
            run_time=4,
        )
        self.wait()

        expression.add(prop_to_brace, prop_to_words)
        self.proportionality_expression = expression

    def show_inverse_square_law(self):
        prop_exp = self.proportionality_expression
        comet = self.comet
        frame = self.camera_frame
        ellipse = self.ellipse
        orbit = self.orbit
        next_line = self.lines[(len(self.lines) / 2) + 1]

        arc = self.arcs[len(self.arcs) / 2]

        force_expression = TexMobject(
            "ma", "=", "\\text{Force}",
            "\\propto", "\\frac{1}{(\\text{Radius})^2}"
        )
        force_expression.next_to(ellipse, LEFT, MED_LARGE_BUFF)
        force_expression.align_to(prop_exp, UP)
        force_expression.set_color_by_tex("Force", YELLOW)

        acceleration_expression = TexMobject(
            "a", "=", "{\\Delta v",
            "\\over", "\\Delta t}",
            "\\propto", "{1 \\over (\\text{Radius})^2}"
        )
        acceleration_expression.next_to(
            force_expression, DOWN, buff=0.75,
            aligned_edge=LEFT
        )

        delta_v_expression = TexMobject(
            "\\Delta v}", "\\propto",
            "{\\Delta t", "\\over", "(\\text{Radius})^2}"
        )
        delta_v_expression.next_to(
            acceleration_expression, DOWN, buff=0.75,
            aligned_edge=LEFT
        )
        delta_t_numerator = delta_v_expression.get_part_by_tex(
            "\\Delta t"
        )
        moving_R_squared = prop_exp.get_part_by_tex("Radius").copy()
        moving_R_squared.generate_target()
        moving_R_squared.target.move_to(delta_t_numerator, DOWN)
        moving_R_squared.target.set_color(GREEN)

        randy = Randolph()
        randy.next_to(force_expression, DOWN, LARGE_BUFF)

        force_vector, force_vector_update = self.get_force_arrow_and_update(
            comet, scale_factor=3,
        )
        moving_vector, moving_vector_animation = self.get_velocity_vector_and_update()

        self.play(
            FadeOut(self.area_questions),
            FadeOut(self.area_question_arrows),
            FadeInFromDown(force_expression),
            frame.shift, 2 * LEFT,
        )
        self.remove(*self.area_questions)
        self.play(
            randy.change, "confused", force_expression,
            VFadeIn(randy)
        )
        self.wait(2)
        self.play(
            randy.change, "pondering", force_expression[0],
            ShowPassingFlashAround(force_expression[:2]),
        )
        self.play(Blink(randy))
        self.play(
            FadeInFromDown(acceleration_expression),
            randy.change, "hooray", force_expression,
            randy.shift, 2 * DOWN,
        )
        self.wait(2)
        self.play(Blink(randy))
        self.play(randy.change, "thinking")
        self.wait()

        self.play(
            comet.move_to, arc.points[0],
            path_arc=90 * DEGREES
        )
        force_vector_update.update(0)
        self.play(
            Blink(randy),
            GrowArrow(force_vector)
        )
        self.add(force_vector_update)
        self.add_foreground_mobjects(comet)
        # Slightly hacky orbit treatment here...
        orbit.proportion = 0.5
        moving_vector_animation.update(0)
        start_velocity_vector = moving_vector.copy()
        self.play(
            GrowArrow(start_velocity_vector),
            randy.look_at, moving_vector
        )
        self.add(moving_vector_animation)
        self.add(orbit)
        while orbit.proportion < next_line.prop:
            self.wait(self.frame_duration)
        self.remove(orbit)
        self.add_foreground_mobjects(comet)
        self.wait(2)
        self.play(
            randy.change, "pondering", force_expression,
            randy.shift, 2 * DOWN,
            FadeInFromDown(delta_v_expression)
        )
        self.play(Blink(randy))
        self.wait(2)
        self.play(
            delta_t_numerator.scale, 1.5, {"about_edge": DOWN},
            delta_t_numerator.set_color, YELLOW
        )
        self.play(CircleThenFadeAround(prop_exp[:-2]))
        self.play(
            delta_t_numerator.fade, 1,
            MoveToTarget(moving_R_squared),
            randy.change, "happy", delta_v_expression
        )
        delta_v_expression.add(moving_R_squared)
        self.wait()
        self.play(FadeOut(randy))

        self.start_velocity_vector = start_velocity_vector
        self.end_velocity_vector = moving_vector.copy()
        self.moving_vector = moving_vector
        self.force_expressions = VGroup(
            force_expression,
            acceleration_expression,
            delta_v_expression,
        )

    def directly_compare_velocity_vectors(self):
        ellipse = self.ellipse
        lines = self.lines
        expressions = self.force_expressions
        vectors = VGroup(*[
            self.get_velocity_vector(line.prop)
            for line in lines
        ])
        index = len(vectors) / 2
        v1 = vectors[index]
        v2 = vectors[index + 1]

        root_point = ellipse.get_left() + 3 * LEFT + DOWN
        root_dot = Dot(root_point)

        for vector in vectors:
            vector.save_state()
            vector.target = Arrow(
                *vector.get_start_and_end(),
                color=vector.get_color(),
                buff=0
            )
            vector.target.scale(2)
            vector.target.shift(
                root_point - vector.target.get_start()
            )
            vector.target.add_to_back(
                vector.target.copy().set_stroke(BLACK, 5)
            )

        difference_vectors = VGroup()
        external_angle_lines = VGroup()
        external_angle_arcs = VGroup()
        for vect1, vect2 in adjacent_pairs(vectors):
            diff_vect = Arrow(
                vect1.target.get_end(),
                vect2.target.get_end(),
                buff=0,
                color=YELLOW,
                rectangular_stem_width=0.025,
                tip_length=0.15
            )
            diff_vect.add_to_back(
                diff_vect.copy().set_stroke(BLACK, 2)
            )
            difference_vectors.add(diff_vect)

            line = Line(
                diff_vect.get_start(),
                diff_vect.get_start() + 2 * diff_vect.get_vector(),
            )
            external_angle_lines.add(line)

            arc = Arc(self.theta, stroke_width=2)
            arc.rotate(line.get_angle(), about_point=ORIGIN)
            arc.scale(0.4, about_point=ORIGIN)
            arc.shift(line.get_center())
            external_angle_arcs.add(arc)
        external_angle_lines.set_stroke(LIGHT_GREY, 2)
        diff_vect = difference_vectors[index]

        polygon = Polygon(*[
            vect.target.get_end()
            for vect in vectors
        ])
        polygon.set_fill(BLUE_E, opacity=0.8)
        polygon.set_stroke(WHITE, 3)

        self.play(CircleThenFadeAround(v1))
        self.play(
            MoveToTarget(v1),
            GrowFromCenter(root_dot),
            expressions.scale, 0.5, {"about_edge": UL}
        )
        self.wait()
        self.play(
            ReplacementTransform(
                v1.saved_state.copy(), v2.saved_state,
                path_arc=self.theta
            )
        )
        self.play(MoveToTarget(v2), Animation(root_dot))
        self.wait()
        self.play(GrowArrow(diff_vect))
        self.wait()

        n = len(vectors)
        for i in range(n - 1):
            v1 = vectors[(i + index + 1) % n]
            v2 = vectors[(i + index + 2) % n]
            diff_vect = difference_vectors[(i + index + 1) % n]
            # TODO, v2.saved_state is on screen untracked
            self.play(ReplacementTransform(
                v1.saved_state.copy(), v2.saved_state,
                path_arc=self.theta
            ))
            self.play(
                MoveToTarget(v2),
                GrowArrow(diff_vect)
            )
        self.add(self.orbit)
        self.wait()
        self.play(
            LaggedStart(ShowCreation, external_angle_lines),
            LaggedStart(ShowCreation, external_angle_arcs),
            Animation(difference_vectors),
        )
        self.add_foreground_mobjects(difference_vectors)
        self.wait(2)
        self.play(FadeIn(polygon))
        self.wait(5)
        self.play(FadeOut(polygon))
        self.wait(15)
        self.play(FadeIn(polygon))


class ShowEqualAngleSlices15DegreeSlices(ShowEqualAngleSlices):
    CONFIG = {
        "animate_sun": True,
        "theta": 15 * DEGREES,
    }


class ShowEqualAngleSlices5DegreeSlices(ShowEqualAngleSlices):
    CONFIG = {
        "animate_sun": True,
        "theta": 5 * DEGREES,
    }


class IKnowThisIsTricky(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "All you need is \\\\ infinite intelligence",
            bubble_kwargs={
                "width": 4,
                "height": 3,
            },
            added_anims=[
                self.get_student_changes(
                    *3 * ["horrified"],
                    look_at_arg=self.screen
                )
            ]
        )
        self.look_at(self.screen)
        self.wait(3)


class PonderOverOffCenterDiagram(PiCreatureScene):
    def construct(self):
        randy, morty = self.pi_creatures
        velocity_diagram = self.get_velocity_diagram()
        bubble = randy.get_bubble()

        rect = SurroundingRectangle(
            velocity_diagram,
            buff=MED_LARGE_BUFF,
            color=LIGHT_GREY
        )
        rect.stretch(1.2, 1, about_edge=DOWN)
        words = TextMobject("Velocity space")
        words.next_to(rect.get_top(), DOWN)

        self.play(
            LaggedStart(GrowFromCenter, velocity_diagram),
            randy.change, "pondering",
            morty.change, "confused",
        )
        self.wait(2)
        self.play(ShowCreation(bubble))
        self.wait(2)
        self.play(
            FadeOut(bubble),
            randy.change, "confused",
            morty.change, "pondering",
            ShowCreation(rect)
        )
        self.play(Write(words))
        self.wait(2)

    def create_pi_creatures(self):
        randy = Randolph(height=2.5)
        randy.to_corner(DL)
        morty = Mortimer(height=2.5)
        morty.to_corner(DR)
        return randy, morty

    def get_velocity_diagram(self):
        circle = Circle(color=WHITE, radius=2)
        circle.rotate(90 * DEGREES)
        circle.to_edge(DOWN, buff=LARGE_BUFF)
        root_point = interpolate(
            circle.get_center(),
            circle.get_bottom(),
            0.5,
        )
        dot = Dot(root_point)
        vectors = VGroup()
        for a in np.arange(0, 1, 1.0 / 24):
            end_point = circle.point_from_proportion(a)
            vector = Arrow(root_point, end_point, buff=0)
            vector.set_color(interpolate_color(
                BLUE, RED,
                inverse_interpolate(
                    1, 3, vector.get_length(),
                )
            ))
            vector.add_to_back(vector.copy().set_stroke(BLACK, 5))
            vectors.add(vector)

        vectors.add_to_back(circle)
        vectors.add(dot)
        return vectors


class OneMoreTrick(TeacherStudentsScene):
    def construct(self):
        for student in self.students:
            student.change("tired")
        self.teacher_says("Just one more \\\\ tricky bit!")
        self.change_all_student_modes("hooray")
        self.wait(3)


class UseVelocityDiagramToDeduceCurve(ShowEqualAngleSlices):
    CONFIG = {
        "animate_sun": True,
        "theta": 15 * DEGREES,
        "index": 6,
    }

    def construct(self):
        self.setup_orbit()
        self.setup_velocity_diagram()
        self.show_theta_degrees()
        self.match_velocity_vector_to_tangency()
        self.replace_vectors_with_lines()
        self.not_that_velocity_vector_is_theta()
        self.ask_about_curve()
        self.show_90_degree_rotation()
        self.show_geometry_of_rotated_diagram()

    def setup_orbit(self):
        ShowEqualAngleSlices.setup_orbit(self)
        self.force_skipping()
        self.show_equal_angle_slices()
        self.revert_to_original_skipping_status()

        orbit_word = self.orbit_word = TextMobject("Orbit")
        orbit_word.scale(1.5)
        orbit_word.next_to(self.ellipse, UP, LARGE_BUFF)
        self.add(orbit_word)

    def setup_velocity_diagram(self):
        ellipse = self.ellipse
        root_point = ellipse.get_left() + 4 * LEFT + DOWN
        frame = self.camera_frame

        root_dot = Dot(root_point)
        vectors = VGroup()
        original_vectors = VGroup()
        for line in self.lines:
            vector = self.get_velocity_vector(line.prop)
            vector.save_state()
            original_vectors.add(vector.copy())
            vector.target = self.get_velocity_vector(
                line.prop, scalar=8.0
            )
            vector.target.shift(
                root_point - vector.target.get_start()
            )

            vectors.add(vector)

        circle = Circle()
        circle.rotate(92 * DEGREES)
        circle.replace(VGroup(*[v.target for v in vectors]))
        circle.set_stroke(WHITE, 2)
        circle.shift(
            (root_point[0] - circle.get_center()[0]) * RIGHT
        )
        circle.shift(0.035 * LEFT)  # ?!?

        velocities_word = TextMobject("Velocities")
        velocities_word.scale(1.5)
        velocities_word.next_to(circle, UP)
        velocities_word.align_to(self.orbit_word, DOWN)

        frame.scale(1.2)
        frame.shift(3 * LEFT + 0.5 * UP)

        self.play(ApplyWave(ellipse))
        self.play(*list(map(GrowArrow, vectors)))
        self.play(
            LaggedStart(
                MoveToTarget, vectors,
                lag_ratio=1,
                run_time=2
            ),
            GrowFromCenter(root_dot),
            FadeInFromDown(velocities_word),
        )
        self.add_foreground_mobjects(root_dot)
        self.play(
            ShowCreation(circle),
            Animation(vectors),
        )
        self.wait()

        self.vectors = vectors
        self.original_vectors = original_vectors
        self.velocity_circle = circle
        self.root_dot = root_dot
        self.circle = circle

    def show_theta_degrees(self):
        lines = self.lines
        ellipse = self.ellipse
        circle = self.circle
        vectors = self.vectors
        comet = self.comet
        sun_center = self.sun.get_center()

        index = self.index
        angle = fdiv(index, len(lines)) * TAU
        thick_line = lines[index].copy()
        thick_line.set_stroke(RED, 3)
        horizontal = lines[0].copy()
        horizontal.set_stroke(WHITE, 3)

        ellipse_arc = VMobject()
        ellipse_arc.pointwise_become_partial(
            ellipse, 0, thick_line.prop
        )
        ellipse_arc.set_stroke(YELLOW, 3)

        ellipse_wedge = self.get_wedge(ellipse_arc, sun_center)
        ellipse_wedge_start = self.get_wedge(
            VectorizedPoint(ellipse.get_right()), sun_center
        )

        ellipse_angle_arc = Arc(
            self.theta * index,
            radius=0.5
        )
        ellipse_angle_arc.shift(sun_center)
        ellipse_theta = TexMobject("\\theta")
        ellipse_theta.next_to(ellipse_angle_arc, RIGHT, MED_SMALL_BUFF)
        ellipse_theta.shift(2 * SMALL_BUFF * UL)

        vector = vectors[index].deepcopy()
        vector.set_fill(YELLOW)
        vector.save_state()
        Transform(vector, vectors[0]).update(1)
        vector.set_fill(YELLOW)
        circle_arc = VMobject()
        circle_arc.pointwise_become_partial(
            circle, 0, fdiv(index, len(vectors))
        )
        circle_arc.set_stroke(RED, 4)
        circle_theta = TexMobject("\\theta")
        circle_theta.scale(1.5)
        circle_theta.next_to(circle_arc, UP, SMALL_BUFF)
        circle_theta.shift(SMALL_BUFF * DL)

        circle_wedge = self.get_wedge(circle_arc, circle.get_center())
        circle_wedge.set_fill(PINK)
        circle_wedge_start = self.get_wedge(
            Line(circle.get_top(), circle.get_top()),
            circle.get_center()
        ).match_style(circle_wedge)

        circle_center_dot = Dot(circle.get_center())
        # circle_center_dot.set_color(BLUE)

        self.play(FocusOn(comet))
        self.play(
            ReplacementTransform(
                ellipse_wedge_start, ellipse_wedge,
                path_arc=angle,
            ),
            FadeIn(ellipse_arc),
            ShowCreation(ellipse_angle_arc),
            Write(ellipse_theta),
            ReplacementTransform(
                lines[0].copy(), thick_line,
                path_arc=angle
            ),
            MoveAlongPath(comet, ellipse_arc),
            run_time=2
        )
        self.wait()
        self.play(
            ReplacementTransform(
                circle_wedge_start, circle_wedge,
                path_arc=angle
            ),
            ShowCreation(circle_arc),
            Write(circle_theta),
            Restore(vector, path_arc=angle),
            GrowFromCenter(circle_center_dot),
            FadeIn(horizontal),
            run_time=2
        )
        self.wait()

        self.set_variables_as_attrs(
            index,
            ellipse_wedge, ellipse_arc,
            ellipse_angle_arc, ellipse_theta,
            thick_line, horizontal,
            circle_wedge, circle_arc,
            circle_theta, circle_center_dot,
            highlighted_vector=vector
        )

    def match_velocity_vector_to_tangency(self):
        vector = self.highlighted_vector
        comet = self.comet
        original_vector = self.original_vectors[self.index].copy()
        original_vector.set_fill(YELLOW)

        tangent_line = Line(
            *original_vector.get_start_and_end()
        )
        tangent_line.set_stroke(LIGHT_GREY, 3)
        tangent_line.scale(5)
        tangent_line.move_to(comet)

        self.play(
            ReplacementTransform(
                vector.copy(), original_vector,
                run_time=2
            ),
            Animation(comet),
        )
        self.wait()
        self.play(
            ShowCreation(tangent_line),
            Animation(original_vector),
            Animation(comet),
        )
        self.wait()

        self.set_variables_as_attrs(
            example_tangent_line=tangent_line,
            example_tangent_vector=original_vector,
        )

    def replace_vectors_with_lines(self):
        vectors = self.vectors
        original_vectors = self.original_vectors
        root_dot = self.root_dot
        highlighted_vector = self.highlighted_vector

        lines = VGroup()
        tangent_lines = VGroup()
        for vect, o_vect in zip(vectors, original_vectors):
            line = Line(*vect.get_start_and_end())
            t_line = Line(*o_vect.get_start_and_end())
            t_line.scale(5)
            t_line.move_to(o_vect.get_start())

            lines.add(line)
            tangent_lines.add(t_line)

            vect.generate_target()
            vect.target.scale(0, about_point=root_dot.get_center())

        lines.set_stroke(GREEN, 2)
        tangent_lines.set_stroke(GREEN, 2)

        highlighted_line = Line(
            *highlighted_vector.get_start_and_end(),
            stroke_color=YELLOW,
            stroke_width=4
        )

        self.play(
            LaggedStart(MoveToTarget, vectors),
            highlighted_vector.scale, 0,
            {"about_point": root_dot.get_center()},
            Animation(highlighted_vector),
            Animation(self.circle_wedge),
            Animation(self.circle_arc),
            Animation(self.circle),
            Animation(self.circle_center_dot),
        )
        self.remove(vectors, highlighted_vector)
        self.play(
            LaggedStart(ShowCreation, lines),
            ShowCreation(highlighted_line),
            Animation(highlighted_vector),
        )
        self.wait()
        self.play(
            ReplacementTransform(
                lines.copy(),
                tangent_lines,
                run_time=3,
            )
        )
        self.wait()
        self.play(FadeOut(tangent_lines))

        self.eccentric_lines = lines
        self.highlighted_line = highlighted_line

    def not_that_velocity_vector_is_theta(self):
        vector = self.example_tangent_vector
        v_line = Line(DOWN, UP)
        v_line.move_to(vector.get_start(), DOWN)
        angle = vector.get_angle() - 90 * DEGREES
        arc = Arc(angle, radius=0.5)
        arc.rotate(90 * DEGREES, about_point=ORIGIN)
        arc.shift(vector.get_start())

        theta_q = TexMobject("\\theta ?")
        theta_q.next_to(arc, UP)
        theta_q.shift(SMALL_BUFF * LEFT)
        cross = Cross(theta_q)

        self.play(ShowCreation(v_line))
        self.play(
            ShowCreation(arc),
            FadeInFromDown(theta_q),
        )
        self.wait()
        self.play(ShowCreation(cross))
        self.wait()
        self.play(*list(map(FadeOut, [v_line, arc, theta_q, cross])))
        self.wait()
        self.play(
            ReplacementTransform(
                self.ellipse_theta.copy(), self.circle_theta,
            ),
            ReplacementTransform(
                self.ellipse_angle_arc.copy(), self.circle_arc,
            ),
            run_time=2,
        )
        self.wait()
        self.play(
            ReplacementTransform(
                self.circle.copy(),
                self.circle_center_dot,
            )
        )
        self.wait()

    def ask_about_curve(self):
        ellipse = self.ellipse
        circle = self.circle
        line = self.highlighted_line.copy()
        vector = self.example_tangent_vector

        morty = Mortimer(height=2.5)
        morty.move_to(ellipse.get_corner(UL))
        morty.shift(MED_SMALL_BUFF * LEFT)

        self.play(FadeIn(morty))
        self.play(
            morty.change, "confused", ellipse,
            ShowCreationThenDestruction(
                ellipse.copy().set_stroke(BLUE, 3),
                run_time=2
            )
        )
        self.play(
            Blink(morty),
            ApplyWave(ellipse),
        )
        self.play(morty.look_at, circle)
        self.play(morty.change, "pondering", circle)
        self.play(Blink(morty))
        self.play(morty.look_at, ellipse)
        self.play(morty.change, "maybe", ellipse)
        self.play(
            line.move_to, vector, run_time=2
        )
        self.play(FadeOut(line))
        self.wait()
        self.play(morty.look_at, circle)
        self.wait()
        self.play(FadeOut(morty))

    def show_90_degree_rotation(self):
        circle = self.circle
        circle_setup = VGroup(
            circle, self.eccentric_lines,
            self.circle_wedge,
            self.circle_arc,
            self.highlighted_line,
            self.circle_center_dot,
            self.root_dot,
            self.circle_theta,
        )
        circle_setup.generate_target()
        angle = -90 * DEGREES
        circle_setup.target.rotate(
            angle,
            about_point=circle.get_center()
        )
        circle_setup.target[-1].rotate(-angle)
        circle_setup.target[2].set_fill(opacity=0)
        circle_setup.target[2].set_stroke(WHITE, 4)

        self.play(MoveToTarget(circle_setup, path_arc=angle))
        self.wait()

        lines = self.eccentric_lines
        highlighted_line = self.highlighted_line
        ghost_lines = lines.copy()
        ghost_lines.set_stroke(width=1)
        ghost_lines[self.index].set_stroke(YELLOW, 4)
        for mob in list(lines) + [highlighted_line]:
            mob.generate_target()
            mob.save_state()
            mob.target.rotate(-angle)

        foci = [
            self.root_dot.get_center(),
            circle.get_center(),
        ]
        a = circle.get_width() / 4
        c = get_norm(foci[1] - foci[0]) / 2
        b = np.sqrt(a**2 - c**2)
        little_ellipse = Circle(radius=a)
        little_ellipse.stretch(b / a, 1)
        little_ellipse.move_to(center_of_mass(foci))
        little_ellipse.set_stroke(PINK, 4)

        self.add(ghost_lines)
        self.play(
            LaggedStart(
                MoveToTarget, lines,
                lag_ratio=0.1,
                run_time=8,
            ),
            MoveToTarget(highlighted_line),
            path_arc=-angle,
        )
        self.play(ShowCreation(little_ellipse))
        self.wait(2)
        self.play(
            little_ellipse.replace, self.ellipse,
            run_time=4,
            rate_func=there_and_back_with_pause
        )
        self.wait(2)

        self.play(*[
            Restore(
                mob,
                path_arc=angle,
                run_time=4,
                rate_func=there_and_back_with_pause
            )
            for mob in list(lines) + [highlighted_line]
        ] + [Animation(little_ellipse)])

        self.ghost_lines = ghost_lines
        self.little_ellipse = little_ellipse

    def show_geometry_of_rotated_diagram(self):
        ellipse = self.ellipse
        little_ellipse = self.little_ellipse
        circle = self.circle
        perp_line = self.highlighted_line.copy()
        perp_line.rotate(PI)
        circle_arc = self.circle_arc
        arc_copy = circle_arc.copy()
        center = circle.get_center()
        velocity_vector = self.example_tangent_vector

        e_line = perp_line.copy().rotate(90 * DEGREES)
        c_line = Line(center, e_line.get_end())
        c_line.set_stroke(WHITE, 4)

        # lines = [c_line, e_line, perp_line]

        tangency_point = line_intersection(
            perp_line.get_start_and_end(),
            c_line.get_start_and_end(),
        )
        tangency_point_dot = Dot(tangency_point)
        tangency_point_dot.set_color(BLUE)
        tangency_point_dot.save_state()
        tangency_point_dot.scale(5)
        tangency_point_dot.set_fill(opacity=0)

        def indicate(line):
            red_copy = line.copy().set_stroke(RED, 5)
            return ShowPassingFlash(red_copy, run_time=2)

        self.play(
            self.ghost_lines.set_stroke, {"width": 0.5},
            self.eccentric_lines.set_stroke, {"width": 0.5},
            *list(map(WiggleOutThenIn, [e_line, c_line]))
        )
        for x in range(3):
            self.play(
                indicate(e_line),
                indicate(c_line),
            )
        self.play(WiggleOutThenIn(perp_line))
        for x in range(2):
            self.play(indicate(perp_line))
        self.play(Restore(tangency_point_dot))
        self.add_foreground_mobjects(tangency_point_dot)
        self.wait(2)
        self.play(
            arc_copy.scale, 0.15, {"about_point": center},
            run_time=2
        )
        self.wait(2)
        self.play(
            perp_line.move_to, velocity_vector,
            run_time=4,
            rate_func=there_and_back_with_pause
        )
        self.wait()
        self.play(
            little_ellipse.replace, ellipse,
            run_time=4,
            rate_func=there_and_back_with_pause
        )
        self.wait()

    # Helpers
    def get_wedge(self, arc, center_point, opacity=0.8):
        wedge = VMobject()
        wedge.append_vectorized_mobject(
            Line(center_point, arc.points[0])
        )
        wedge.append_vectorized_mobject(arc)
        wedge.append_vectorized_mobject(
            Line(arc.points[-1], center_point)
        )
        wedge.set_stroke(width=0)
        wedge.set_fill(COBALT, opacity=opacity)
        return wedge


class ShowSunVectorField(Scene):
    def construct(self):
        sun_center = IntroduceShapeOfVelocities.CONFIG["sun_center"]
        vector_field = VectorField(
            get_force_field_func((sun_center, -1))
        )
        vector_field.set_fill(opacity=0.8)
        vector_field.sort_submobjects(
            lambda p: -get_norm(p - sun_center)
        )

        for vector in vector_field:
            vector.generate_target()
            vector.target.set_fill(opacity=1)
            vector.target.set_stroke(YELLOW, 0.5)

        for x in range(3):
            self.play(LaggedStart(
                MoveToTarget, vector_field,
                rate_func=there_and_back,
                lag_ratio=0.5,
            ))


class TryToRememberProof(PiCreatureScene):
    def construct(self):
        randy = self.pi_creature

        words = TextMobject("Oh god...how \\\\ did it go?")
        words.next_to(randy, UP)
        words.shift_onto_screen()

        self.play(
            randy.change, "telepath",
            FadeInFromDown(words)
        )
        self.look_at(ORIGIN)
        self.wait(2)
        self.play(randy.change, "concerned_musician")
        self.look_at(ORIGIN)
        self.wait(3)


class PatYourselfOnTheBack(TeacherStudentsScene):
    CONFIG = {
        "camera_config": {"background_opacity": 1},
    }

    def construct(self):
        self.teacher_says(
            "Pat yourself \\\\ on the back!",
            target_mode="hooray"
        )
        self.change_all_student_modes("happy")
        self.wait(3)
        self.play(
            RemovePiCreatureBubble(
                self.teacher,
                target_mode="raise_right_hand"
            ),
            self.get_student_changes(
                *3 * ["pondering"],
                look_at_arg=self.screen
            )
        )
        self.look_at(UP)
        self.wait(8)
        self.change_student_modes(*3 * ["thinking"])
        self.look_at(UP)
        self.wait(12)
        self.teacher_says("I just love this!")

        feynman = ImageMobject("Feynman", height=4)
        feynman.to_corner(UL)
        chess = ImageMobject("ChessGameOfTheCentury")
        chess.set_height(4)
        chess.next_to(feynman)

        self.play(FadeInFromDown(feynman))
        self.wait()
        self.play(
            RemovePiCreatureBubble(self.teacher, target_mode="happy"),
            FadeInFromDown(chess)
        )
        self.wait(2)


class Thumbnail(ShowEmergingEllipse):
    CONFIG = {
        "num_lines": 50,
    }

    def construct(self):
        background = ImageMobject("Feynman_teaching")
        background.set_width(FRAME_WIDTH)
        background.scale(1.05)
        background.to_corner(UR, buff=0)
        background.shift(2 * UP)

        self.add(background)

        circle = self.get_circle()
        circle.set_stroke(width=6)
        circle.set_height(6.5)
        circle.to_corner(UL)
        circle.set_fill(BLACK, 0.9)
        lines = self.get_lines()
        lines.set_stroke(YELLOW, 5)
        lines.set_color_by_gradient(YELLOW, RED)
        ghost_lines = self.get_ghost_lines(lines)
        for line in lines:
            line.rotate(90 * DEGREES)
        ellipse = self.get_ellipse()
        ellipse.set_stroke(BLUE, 6)
        sun = ImageMobject("sun", height=0.5)
        sun.move_to(self.get_eccentricity_point())

        circle_group = VGroup(circle, ghost_lines, lines, ellipse, sun)
        self.add(circle_group)

        l1 = Line(
            circle.point_from_proportion(0.175),
            6.25 * RIGHT + 0.75 * DOWN
        )
        l2 = Line(
            circle.point_from_proportion(0.75),
            6.25 * RIGHT + 2.5 * DOWN
        )
        l2a = VMobject().pointwise_become_partial(l2, 0, 0.56)
        l2b = VMobject().pointwise_become_partial(l2, 0.715, 1)
        expand_lines = VGroup(l1, l2a, l2b)

        expand_lines.set_stroke("RED", 5)
        self.add(expand_lines)
        self.add(circle_group)

        small_group = circle_group.copy()
        small_group.scale(0.2)
        small_group.stretch(1.35, 1)
        small_group.move_to(6.2 * RIGHT + 1.6 * DOWN)
        for mob in small_group:
            if isinstance(mob, VMobject) and mob.get_stroke_width() > 1:
                mob.set_stroke(width=1)
        small_group[0].set_fill(opacity=0.25)
        self.add(small_group)

        title = TextMobject(
            "Feynman's \\\\", "Lost \\\\", "Lecture",
            alignment=""
        )
        title.scale(2.4)
        for part in title:
            part.add_to_back(
                part.copy().set_stroke(BLACK, 12).set_fill(BLACK, 1)
            )
        title.to_corner(UR)
        title[2].to_edge(RIGHT)
        title[1].shift(0.9 * RIGHT)
        title.shift(0.5 * LEFT)
        self.add(title)
