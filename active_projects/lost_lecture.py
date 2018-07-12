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

# Animations


class ShowEmergingEllipse(Scene):
    CONFIG = {
        "circle_radius": 3,
        "circle_color": BLUE,
        "num_lines": 100,
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
            Write(ellipse_words, run_time=1)
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
    def construct(self):
        self.add_title()
        self.setup_orbits()

    def add_title(self):
        pass

    def setup_orbits(self):
        pass
