from manimlib.imports import *
from active_projects.ode.part1.staging import TourOfDifferentialEquations


class PartTwoOfTour(TourOfDifferentialEquations):
    CONFIG = {
        "zoomed_thumbnail_index": 1,
    }

    def construct(self):
        self.add_title()
        self.show_thumbnails()
        self.zoom_in_to_one_thumbnail()

    def zoom_in_to_one_thumbnail(self):
        frame = self.camera_frame
        thumbnails = self.thumbnails

        ode = TextMobject("Ordinary\\\\", "Differential Equation")
        pde = TextMobject("Partial\\\\", "Differential Equation")
        for word, thumbnail, vect in zip([ode, pde], thumbnails, [DOWN, UP]):
            word.match_width(thumbnail)
            word.next_to(thumbnail, vect)
        ode[0].set_color(BLUE)
        pde[0].set_color(YELLOW)

        self.add(ode)

        frame.save_state()
        self.play(
            frame.replace,
            thumbnails[0],
            run_time=1,
        )
        self.play(
            Restore(frame, run_time=3),
        )
        self.play(
            TransformFromCopy(ode, pde),
        )
        self.play(
            ApplyMethod(
                frame.replace, thumbnails[1],
                path_arc=(-30 * DEGREES),
                run_time=3
            ),
        )
        self.wait()


class BrownianMotion(Scene):
    CONFIG = {
        "wait_time": 60,
        "L": 3,  # Box in [-L, L] x [-L, L]
        "n_particles": 100,
        "m1": 1,
        "m2": 100,
        "r1": 0.05,
        "r2": 0.5,
        "max_v": 5,
        "random_seed": 2,
    }

    def construct(self):
        self.add_title()
        self.add_particles()
        self.wait(self.wait_time)

    def add_title(self):
        square = Square(side_length=2 * self.L)
        title = TextMobject("Brownian motion")
        title.scale(1.5)
        title.next_to(square, UP)

        self.add(square)
        self.add(title)

    def add_particles(self):
        m1 = self.m1
        m2 = self.m2
        r1 = self.r1
        r2 = self.r2
        L = self.L
        max_v = self.max_v
        n_particles = self.n_particles

        lil_particles = VGroup(*[
            self.get_particle(m1, r1, L, max_v)
            for k in range(n_particles)
        ])
        big_particle = self.get_particle(m2, r2, L=r2, max_v=0)
        big_particle.set_fill(YELLOW, 1)

        for p in lil_particles:
            if self.are_colliding(p, big_particle):
                lil_particles.remove(p)
        all_particles = VGroup(big_particle, *lil_particles)
        all_particles.add_updater(self.update_particles)

        path = self.get_traced_path(big_particle)

        self.add(all_particles)
        self.add(path)

        self.particles = all_particles
        self.big_particle = big_particle
        self.path = path

    def get_particle(self, m, r, L, max_v):
        dot = Dot(radius=r)
        dot.set_fill(WHITE, 0.7)
        dot.mass = m
        dot.radius = r
        dot.center = op.add(
            np.random.uniform(-L + r, L - r) * RIGHT,
            np.random.uniform(-L + r, L - r) * UP
        )
        dot.move_to(dot.center)
        dot.velocity = rotate_vector(
            np.random.uniform(0, max_v) * RIGHT,
            np.random.uniform(0, TAU),
        )
        return dot

    def are_colliding(self, p1, p2):
        d = get_norm(p1.get_center() - p2.get_center())
        return (d < p1.radius + p2.radius)

    def get_traced_path(self, particle):
        path = VMobject()
        path.set_stroke(BLUE, 3)
        path.start_new_path(particle.get_center())

        buff = 0.02

        def update_path(path):
            new_point = particle.get_center()
            if get_norm(new_point - path.get_last_point()) > buff:
                path.add_line_to(new_point)

        path.add_updater(update_path)
        return path

    def update_particles(self, particles, dt):
        for p1 in particles:
            p1.center += p1.velocity * dt

            # Check particle collisions
            buff = 0.01
            for p2 in particles:
                if p1 is p2:
                    continue
                v = p2.center - p1.center
                dist = get_norm(v)
                r_sum = p1.radius + p2.radius
                diff = dist - r_sum
                if diff < 0:
                    unit_v = v / dist
                    p1.center += (diff - buff) * unit_v / 2
                    p2.center += -(diff - buff) * unit_v / 2
                    u1 = p1.velocity
                    u2 = p2.velocity
                    m1 = p1.mass
                    m2 = p2.mass
                    v1 = (
                        (m2 * (u2 - u1) + m1 * u1 + m2 * u2) /
                        (m1 + m2)
                    )
                    v2 = (
                        (m1 * (u1 - u2) + m1 * u1 + m2 * u2) /
                        (m1 + m2)
                    )
                    p1.velocity = v1
                    p2.velocity = v2

            # Check edge collisions
            r1 = p1.radius
            c1 = p1.center
            for i in [0, 1]:
                if abs(c1[i]) + r1 > self.L:
                    c1[i] = np.sign(c1[i]) * (self.L - r1)
                    p1.velocity[i] *= -1 * op.mul(
                        np.sign(p1.velocity[i]),
                        np.sign(c1[i])
                    )

        for p in particles:
            p.move_to(p.center)
        return particles


class AltBrownianMotion(BrownianMotion):
    CONFIG = {
        "wait_time": 20,
        "n_particles": 100,
        "m2": 10,
    }


class BlackScholes(AltBrownianMotion):
    def construct(self):
        # For some reason I'm amused by the thought
        # Of this graph perfectly matching the Brownian
        # Motion y-coordiante
        self.add_title()
        self.add_particles()
        self.particles.set_opacity(0)
        self.remove(self.path)
        self.add_graph()
        self.wait(self.wait_time)

    def add_title(self):
        title = TextMobject("Black-Sholes equations")
        title.scale(1.5)
        title.next_to(2 * UP, UP)

        equation = TexMobject(
            "{\\partial V \\over \\partial t}", "+",
            "\\frac{1}{2} \\sigma^2 S^2",
            "{\\partial^2 V \\over \\partial S^2}", "+",
            "rS", "{\\partial V \\over \\partial S}",
            "-rV", "=", "0",
        )
        equation.scale(0.8)
        equation.next_to(title, DOWN)

        self.add(title)
        self.add(equation)
        self.title = title
        self.equation = equation

    def add_graph(self):
        axes = Axes(
            x_min=-1,
            x_max=20,
            y_min=0,
            y_max=10,
            number_line_config={
                "unit_size": 0.5,
            },
        )
        axes.set_height(4)
        axes.move_to(DOWN)

        def get_graph_point():
            return axes.c2p(
                self.get_time(),
                5 + 2 * self.big_particle.get_center()[1]
            )

        graph = VMobject()
        graph.match_style(self.path)
        graph.start_new_path(get_graph_point())
        graph.add_updater(
            lambda g: g.add_line_to(get_graph_point())
        )

        self.add(axes)
        self.add(graph)


class ContrastChapters1And2(Scene):
    def construct(self):
        c1_frame, c2_frame = frames = VGroup(*[
            ScreenRectangle(height=3.5)
            for x in range(2)
        ])
        frames.arrange(RIGHT, buff=LARGE_BUFF)

        c1_title, c2_title = titles = VGroup(
            TextMobject("Chapter 1"),
            TextMobject("Chapter 2"),
        )
        titles.scale(1.5)

        ode, pde = des = VGroup(
            TextMobject(
                "Ordinary",
                "Differential Equations\\\\",
                "ODEs",
            ),
            TextMobject(
                "Partial",
                "Differential Equations\\\\",
                "PDEs",
            ),
        )
        ode[0].set_color(BLUE)
        pde[0].set_color(YELLOW)
        for de in des:
            de[-1][0].match_color(de[0])
            de[-1].scale(1.5, about_point=de.get_top())

        for title, frame, de in zip(titles, frames, des):
            title.next_to(frame, UP)
            de.match_width(frame)
            de.next_to(frame, DOWN)

        lt = TexMobject("<")
        lt.move_to(Line(ode.get_right(), pde.get_left()))
        lt.scale(2, about_edge=UP)

        c1_words = TextMobject(
            "They're", "really\\\\", "{}",
            "freaking", "hard\\\\",
            "to", "solve\\\\",
        )
        c1_words.set_height(0.5 * c1_frame.get_height())
        c1_words.move_to(c1_frame)

        c2_words = TextMobject(
            "They're", "really", "\\emph{really}\\\\",
            "freaking", "hard\\\\",
            "to", "solve\\\\",
        )
        c2_words.set_color_by_tex("\\emph", YELLOW)
        c2_words.move_to(c2_frame)
        edit_shift = MED_LARGE_BUFF * RIGHT
        c2_edits = VGroup(
            TextMobject("sometimes").next_to(
                c2_words[1:3], UP,
                aligned_edge=LEFT,
            ),
            Line(
                c2_words[1].get_left(),
                c2_words[2].get_right(),
                stroke_width=8,
            ),
            TextMobject("not too").next_to(
                c2_words[3], LEFT,
            ),
            Line(
                c2_words[3].get_left(),
                c2_words[3].get_right(),
                stroke_width=8,
            ),
        )
        c2_edits.set_color(RED)
        c2_edits[2:].shift(edit_shift)

        self.add(titles)
        self.add(frames)
        self.add(des)

        self.wait()
        self.play(LaggedStartMap(
            FadeInFromDown, c1_words,
            lag_ratio=0.1,
        ))
        self.wait()
        # self.play(FadeIn(ode))
        self.play(
            # TransformFromCopy(ode, pde),
            TransformFromCopy(c1_words, c2_words),
            Write(lt)
        )
        self.wait()
        self.play(
            Write(c2_edits[:2], run_time=1),
        )
        self.play(
            c2_words[3:5].shift, edit_shift,
            Write(c2_edits[2:]),
            run_time=1,
        )
        self.wait()


class ShowCubeFormation(ThreeDScene):
    CONFIG = {
        "camera_config": {
            "shading_factor": 1.0,
        },
        "color": False,
    }

    def construct(self):
        light_source = self.camera.light_source
        light_source.move_to(np.array([-6, -3, 6]))

        cube = Cube(
            side_length=4,
            fill_color=GREY,
            stroke_color=WHITE,
            stroke_width=0.5,
        )
        cube.set_fill(opacity=1)
        if self.color:
            # cube[0].set_color(BLUE)
            # cube[1].set_color(RED)
            # for face in cube[2:]:
            #     face.set_color([BLUE, RED])
            cube.color_using_background_image("VerticalTempGradient")

        # light_source.next_to(cube, np.array([1, -1, 1]), buff=2)

        cube_3d = cube.copy()
        cube_2d = cube_3d.copy().stretch(0, 2)
        cube_1d = cube_2d.copy().stretch(0, 1)
        cube_0d = cube_1d.copy().stretch(0, 0)

        cube.become(cube_0d)

        self.set_camera_orientation(
            phi=70 * DEGREES,
            theta=-145 * DEGREES,
        )
        self.begin_ambient_camera_rotation(rate=0.05)

        for target in [cube_1d, cube_2d, cube_3d]:
            self.play(
                Transform(cube, target, run_time=1.5)
            )
        self.wait(8)


class ShowCubeFormationWithColor(ShowCubeFormation):
    CONFIG = {
        "color": True,
    }


class ShowRect(Scene):
    CONFIG = {
        "height": 1,
        "width": 3,
    }

    def construct(self):
        rect = Rectangle(
            height=self.height,
            width=self.width,
        )
        rect.set_color(YELLOW)
        self.play(ShowCreationThenFadeOut(rect))


class ShowSquare(ShowRect):
    CONFIG = {
        "height": 1,
        "width": 1,
    }


class ShowHLine(Scene):
    def construct(self):
        line = Line(LEFT, RIGHT)
        line.set_color(BLUE)
        self.play(ShowCreationThenFadeOut(line))


class ShowCross(Scene):
    def construct(self):
        cross = Cross(Square())
        cross.set_width(3)
        cross.set_height(1, stretch=True)
        self.play(ShowCreation(cross))


class TwoBodyEquations(Scene):
    def construct(self):
        kw = {
            "tex_to_color_map": {
                "x_1": LIGHT_GREY,
                "y_1": LIGHT_GREY,
                "x_2": BLUE,
                "y_2": BLUE,
                "=": WHITE,
            }
        }
        equations = VGroup(
            TexMobject(
                "{d^2 x_1 \\over dt^2}",
                "=",
                "{x_2 - x_1 \\over m_1 \\left(",
                "(x_2 - x_1)^2 + (y_2 - y_1)^2",
                "\\right)^{3/2}",
                **kw
            ),
            TexMobject(
                "{d^2 y_1 \\over dt^2}",
                "=",
                "{y_2 - y_1 \\over m_1 \\left(",
                "(x_2 - x_1)^2 + (y_2 - y_1)^2",
                "\\right)^{3/2}",
                **kw
            ),
            TexMobject(
                "{d^2 x_2 \\over dt^2}",
                "=",
                "{x_1 - x_2 \\over m_2 \\left(",
                "(x_2 - x_1)^2 + (y_2 - y_1)^2",
                "\\right)^{3/2}",
                **kw
            ),
            TexMobject(
                "{d^2 y_2 \\over dt^2}",
                "=",
                "{y_1 - y_2 \\over m_2 \\left(",
                "(x_2 - x_1)^2 + (y_2 - y_1)^2",
                "\\right)^{3/2}",
                **kw
            ),
        )

        equations.arrange(DOWN, buff=LARGE_BUFF)
        equations.set_height(6)
        equations.to_edge(LEFT)

        variables = VGroup()
        lhss = VGroup()
        rhss = VGroup()
        for equation in equations:
            variable = equation[1]
            lhs = equation[:4]
            rhs = equation[4:]
            variables.add(variable)
            lhss.add(lhs)
            rhss.add(rhs)
        lhss_copy = lhss.copy()

        for variable, lhs in zip(variables, lhss):
            variable.save_state()
            variable.match_height(lhs)
            variable.scale(0.7)
            variable.move_to(lhs, LEFT)

        self.play(LaggedStart(*[
            FadeInFrom(v, RIGHT)
            for v in variables
        ]))
        self.wait()
        self.play(
            LaggedStartMap(Restore, variables),
            FadeIn(
                lhss_copy,
                remover=True,
                lag_ratio=0.1,
                run_time=2,
            )
        )
        self.add(lhss)
        self.wait()
        self.play(LaggedStartMap(
            FadeIn, rhss
        ))
        self.wait()
        self.play(
            LaggedStart(*[
                ShowCreationThenFadeAround(lhs[:3])
                for lhs in lhss
            ])
        )
        self.wait()
        self.play(
            LaggedStartMap(
                ShowCreationThenFadeAround,
                rhss,
            )
        )
        self.wait()


class LaplacianIntuition(SpecialThreeDScene):
    CONFIG = {
        "three_d_axes_config": {
            "x_min": -5,
            "x_max": 5,
            "y_min": -5,
            "y_max": 5,
        },
        "surface_resolution": 32,
    }

    def construct(self):
        axes = self.get_axes()
        axes.scale(0.5, about_point=ORIGIN)
        self.set_camera_to_default_position()
        self.begin_ambient_camera_rotation()

        def func(x, y):
            return np.array([
                x, y,
                2.7 + 0.5 * (np.sin(x) + np.cos(y)) -
                0.025 * (x**2 + y**2)
            ])

        surface_config = {
            "u_min": -5,
            "u_max": 5,
            "v_min": -5,
            "v_max": 5,
            "resolution": self.surface_resolution,
        }
        # plane = ParametricSurface(
        #     lambda u, v: np.array([u, v, 0]),
        #     **surface_config
        # )
        # plane.set_stroke(WHITE, width=0.1)
        # plane.set_fill(WHITE, opacity=0.1)
        plane = Square(
            side_length=10,
            stroke_width=0,
            fill_color=WHITE,
            fill_opacity=0.1,
        )
        plane.center()
        plane.set_shade_in_3d(True)

        surface = ParametricSurface(
            func, **surface_config
        )
        surface.set_stroke(BLUE, width=0.1)
        surface.set_fill(BLUE, opacity=0.25)

        self.add(axes, plane, surface)

        point = VectorizedPoint(np.array([2, -2, 0]))
        dot = Dot()
        dot.set_color(GREEN)
        dot.add_updater(lambda d: d.move_to(point))
        line = always_redraw(lambda: DashedLine(
            point.get_location(),
            func(*point.get_location()[:2]),
            background_image_file="VerticalTempGradient",
        ))

        circle = Circle(radius=0.25)
        circle.set_color(YELLOW)
        circle.insert_n_curves(20)
        circle.add_updater(lambda m: m.move_to(point))
        circle.set_shade_in_3d(True)
        surface_circle = always_redraw(
            lambda: circle.copy().apply_function(
                lambda p: func(*p[:2])
            ).shift(
                0.02 * IN
            ).color_using_background_image("VerticalTempGradient")
        )

        self.play(FadeInFromLarge(dot))
        self.play(ShowCreation(line))
        self.play(TransformFromCopy(dot, circle))
        self.play(
            Transform(
                circle.copy(),
                surface_circle.copy().clear_updaters(),
                remover=True,
            )
        )
        self.add(surface_circle)

        self.wait()
        for vect in [4 * LEFT, DOWN, 4 * RIGHT, UP]:
            self.play(
                point.shift, vect,
                run_time=3,
            )


class StrogatzMention(PiCreatureScene):
    def construct(self):
        self.show_book()
        self.show_motives()
        self.show_pages()

    def show_book(self):
        morty = self.pi_creature
        book = ImageMobject("InfinitePowers")
        book.set_height(5)
        book.to_edge(LEFT)

        steve = ImageMobject("Strogatz_by_bricks")
        steve.set_height(5)
        steve.to_edge(LEFT)

        name = TextMobject("Steven Strogatz")
        name.match_width(steve)
        name.next_to(steve, DOWN)

        self.think(
            "Hmm...many good\\\\lessons here...",
            run_time=1
        )
        self.wait()
        self.play(FadeInFromDown(steve))
        self.wait()
        self.play(
            FadeInFrom(book, DOWN),
            steve.shift, 4 * RIGHT,
            RemovePiCreatureBubble(
                morty, target_mode="thinking"
            )
        )
        self.wait(3)
        self.play(
            FadeOut(steve),
            FadeOut(morty),
        )

        self.book = book

    def show_motives(self):
        motives = VGroup(
            TextMobject("1) Scratch and itch"),
            TextMobject("2) Make people love math"),
        )
        motives.scale(1.5)
        motives.arrange(
            DOWN, LARGE_BUFF,
            aligned_edge=LEFT,
        )
        motives.move_to(
            Line(
                self.book.get_right(),
                FRAME_WIDTH * RIGHT / 2
            )
        )
        motives.to_edge(UP)

        for motive in motives:
            self.play(FadeInFromDown(motive))
            self.wait(2)
        self.play(FadeOut(motives))

    def show_pages(self):
        book = self.book
        pages = Group(*[
            ImageMobject("IP_Sample_Page{}".format(i))
            for i in range(1, 4)
        ])
        for page in pages:
            page.match_height(book)
            page.next_to(book, RIGHT)

        last_page = VectorizedPoint()
        for page in pages:
            self.play(
                FadeOut(last_page),
                FadeIn(page)
            )
            self.wait()
            last_page = page

        self.play(FadeOut(last_page))

    def create_pi_creature(self):
        return Mortimer().to_corner(DR)


class Thumbnail(Scene):
    def construct(self):
        image = ImageMobject("HeatSurfaceExampleFlipped")
        image.set_height(6.5)
        image.to_edge(DOWN, buff=-SMALL_BUFF)
        self.add(image)

        equation = TexMobject(
            "{\\partial {T} \\over \\partial {t}}", "=",
            "\\alpha", "\\nabla^2 {T}",
            tex_to_color_map={
                "{t}": YELLOW,
                "{T}": RED,
            }
        )
        equation.scale(2)
        equation.to_edge(UP)

        self.add(equation)

        Group(equation, image).shift(1.5 * RIGHT)

        question = TextMobject("What is\\\\this?")
        question.scale(2.5)
        question.to_edge(LEFT)
        arrow = Arrow(
            question.get_top(),
            equation.get_left(),
            buff=0.5,
            path_arc=-90 * DEGREES,
        )
        arrow.set_stroke(width=5)

        self.add(question, arrow)


class ShowNewton(Scene):
    def construct(self):
        pass


class ShowCupOfWater(Scene):
    def construct(self):
        pass
