from manimlib.imports import *


class SideGigToFullTime(Scene):
    def construct(self):
        morty = Mortimer()
        morty.next_to(ORIGIN, DOWN)
        self.add(morty)

        self.side_project(morty)
        self.income(morty)
        self.full_time(morty)

    def side_project(self, morty):
        rect = PictureInPictureFrame()
        rect.next_to(morty, UP+LEFT)
        side_project = TextMobject("Side project")
        side_project.next_to(rect, UP)
        dollar_sign = TexMobject("\\$")
        cross = VGroup(*[
            Line(vect, -vect, color = RED)
            for vect in (UP+RIGHT, UP+LEFT)
        ])
        cross.set_height(dollar_sign.get_height())
        no_money = VGroup(dollar_sign, cross)
        no_money.next_to(rect, DOWN)

        self.play(
            morty.change_mode, "raise_right_hand",
            morty.look_at, rect
        )
        self.play(
            Write(side_project),
            ShowCreation(rect)
        )
        self.wait()
        self.play(Blink(morty))
        self.wait()
        self.play(Write(dollar_sign))
        self.play(ShowCreation(cross))

        self.screen_title = side_project
        self.cross = cross

    def income(self, morty):
        dollar_signs = VGroup(*[
            TexMobject("\\$")
            for x in range(10)
        ])
        dollar_signs.arrange(RIGHT, buff = LARGE_BUFF)
        dollar_signs.set_color(BLACK)
        dollar_signs.next_to(morty.eyes, RIGHT, buff = 2*LARGE_BUFF)

        self.play(
            morty.change_mode, "happy",
            morty.look_at, dollar_signs, 
            dollar_signs.shift, LEFT,
            dollar_signs.set_color, GREEN
        )
        for x in range(5):
            last_sign = dollar_signs[0]
            dollar_signs.remove(last_sign)
            self.play(
                FadeOut(last_sign),
                dollar_signs.shift, LEFT
            )
        random.shuffle(dollar_signs.submobjects)
        self.play(
            ApplyMethod(
                dollar_signs.shift, 
                (FRAME_Y_RADIUS+1)*DOWN,
                lag_ratio = 0.5
            ),
            morty.change_mode, "guilty",
            morty.look, DOWN+RIGHT
        )
        self.play(Blink(morty))

    def full_time(self, morty):
        new_title = TextMobject("Full time")
        new_title.move_to(self.screen_title)
        q_mark = TexMobject("?")
        q_mark.next_to(self.cross)
        q_mark.set_color(GREEN)

        self.play(morty.look_at, q_mark)
        self.play(Transform(self.screen_title, new_title))
        self.play(
            Transform(self.cross, q_mark),
            morty.change_mode, "confused"
        )
        self.play(Blink(morty))
        self.wait()
        self.play(
            morty.change_mode, "happy",
            morty.look, UP+RIGHT
        )
        self.play(Blink(morty))
        self.wait()

class TakesTime(Scene):
    def construct(self):
        rect = PictureInPictureFrame(height = 4)
        rect.to_edge(RIGHT, buff = LARGE_BUFF)
        clock = Clock()
        clock.hour_hand.set_color(BLUE_C)
        clock.minute_hand.set_color(BLUE_D)
        clock.next_to(rect, LEFT, buff = LARGE_BUFF)
        self.add(rect)
        self.play(ShowCreation(clock))
        for x in range(3):
            self.play(ClockPassesTime(clock))

class GrowingToDoList(Scene):
    def construct(self):
        morty = Mortimer()
        morty.flip()
        morty.next_to(ORIGIN, DOWN+LEFT)
        title = TextMobject("3blue1brown to-do list")
        title.next_to(ORIGIN, RIGHT)
        title.to_edge(UP)
        underline = Line(title.get_left(), title.get_right())
        underline.next_to(title, DOWN)

        lines = VGroup(*list(map(TextMobject, [
            "That one on topology",
            "Something with quaternions",
            "Solving puzzles with binary counting",
            "Tatoos on math",
            "Laplace stuffs",
            "The role of memorization in math",
            "Strangeness of the axiom of choice",
            "Tensors",
            "Different view of $e^{\\pi i}$",
            "Quadratic reciprocity",
            "Fourier stuffs",
            "$1+2+3+\\cdots = -\\frac{1}{12}$",
            "Understanding entropy",
        ])))
        lines.scale(0.65)
        lines.arrange(DOWN, buff = MED_SMALL_BUFF, aligned_edge = LEFT)
        lines.set_color_by_gradient(BLUE_C, YELLOW)
        lines.next_to(title, DOWN, buff = LARGE_BUFF/2.)
        lines.to_edge(RIGHT)

        self.play(
            Write(title),
            morty.look_at, title
        )
        self.play(
            Write(lines[0]), 
            morty.change_mode, "erm",
            run_time = 1
        )
        for line in lines[1:3]:
            self.play(
                Write(line), 
                morty.look_at, line,
                run_time = 1
            )
        self.play(
            morty.change_mode, "pleading",
            morty.look_at, lines,
            Write(
                VGroup(*lines[3:]),
            )
        )

class TwoTypesOfVideos(Scene):
    def construct(self):
        morty = Mortimer().shift(2*DOWN)
        stand_alone = TextMobject("Standalone videos")
        stand_alone.shift(FRAME_X_RADIUS*LEFT/2)
        stand_alone.to_edge(UP)
        series = TextMobject("Series")
        series.shift(FRAME_X_RADIUS*RIGHT/2)
        series.to_edge(UP)
        box = Rectangle(width = 16, height = 9, color = WHITE)
        box.set_height(3)
        box.next_to(stand_alone, DOWN)
        series_list = VGroup(*[  
            TextMobject("Essence of %s"%s)
            for s in [
                "linear algebra",
                "calculus",
                "probability",
                "real analysis",
                "complex analysis",
                "ODEs",
            ]
        ])
        series_list.arrange(DOWN, aligned_edge = LEFT, buff = MED_SMALL_BUFF)
        series_list.set_width(FRAME_X_RADIUS-2)
        series_list.next_to(series, DOWN, buff = MED_SMALL_BUFF)
        series_list.to_edge(RIGHT)

        fridays = TextMobject("Every other friday")
        when_done = TextMobject("When series is done")
        for words, vect in (fridays, LEFT), (when_done, RIGHT):
            words.set_color(YELLOW)
            words.next_to(
                morty, vect, 
                buff = MED_SMALL_BUFF, 
                aligned_edge = UP
            )
        unless = TextMobject("""
            Unless you're
            a patron \\dots
        """)
        unless.next_to(when_done, DOWN, buff = MED_SMALL_BUFF)

        self.add(morty)
        self.play(Blink(morty))
        self.play(
            morty.change_mode, "raise_right_hand",
            morty.look_at, stand_alone,
            Write(stand_alone, run_time = 2),
        )
        self.play(
            morty.change_mode, "raise_left_hand",
            morty.look_at, series,
            Write(series, run_time = 2),
        )
        self.play(Blink(morty))
        self.wait()
        self.play(
            morty.change_mode, "raise_right_hand",
            morty.look_at, box,
            ShowCreation(box)
        )
        for x in range(3):
            self.wait(2)
            self.play(Blink(morty))            
        self.play(
            morty.change_mode, "raise_left_hand",
            morty.look_at, series
        )
        for i, words in enumerate(series_list):
            self.play(Write(words), run_time = 1)
        self.play(Blink(morty))
        self.wait()
        self.play(series_list[1].set_color, BLUE)
        self.wait(2)
        self.play(Blink(morty))
        self.wait()
        pairs = [
            (fridays, "speaking"), 
            (when_done, "wave_2") ,
            (unless, "surprised"),
        ]
        for words, mode in pairs:
            self.play(
                Write(words),
                morty.change_mode, mode,
                morty.look_at, words
            )
            self.wait()

class ClassWatching(TeacherStudentsScene):
    def construct(self):
        rect = PictureInPictureFrame(height = 4)
        rect.next_to(self.get_teacher(), UP, buff = LARGE_BUFF/2.)
        rect.to_edge(RIGHT)
        self.add(rect)
        for pi in self.get_students():
            pi.look_at(rect)

        self.random_blink(5)
        self.change_student_modes(
            "raise_left_hand",
            "raise_right_hand",            
            "sassy",
        )
        self.play(self.get_teacher().change_mode, "pondering")
        self.random_blink(3)

class RandolphWatching(Scene):
    def construct(self):
        randy = Randolph()
        randy.shift(2*LEFT)
        randy.look(RIGHT)

        self.add(randy)
        self.wait()
        self.play(Blink(randy))
        self.wait()
        self.play(
            randy.change_mode, "pondering",
            randy.look, RIGHT
        )
        self.play(Blink(randy))
        self.wait()

class RandolphWatchingWithLaptop(Scene):
    pass

class GrowRonaksSierpinski(Scene):
    CONFIG = {
        "colors" : [BLUE, YELLOW, BLUE_C, BLUE_E],
        "dot_radius" : 0.08,
        "n_layers" : 64,
    }
    def construct(self):
        sierp = self.get_ronaks_sierpinski(self.n_layers)
        dots = self.get_dots(self.n_layers)
        self.triangle = VGroup(sierp, dots)
        self.triangle.scale(1.5)
        self.triangle.shift(3*UP)
        sierp_layers = sierp.submobjects
        dot_layers = dots.submobjects

        last_dot_layer = dot_layers[0]
        self.play(ShowCreation(last_dot_layer))
        run_time = 1
        for n, sierp_layer, dot_layer in zip(it.count(1), sierp_layers, dot_layers[1:]):
            self.play(
                ShowCreation(sierp_layer, lag_ratio=1),
                Animation(last_dot_layer),
                run_time = run_time
            )
            self.play(ShowCreation(
                dot_layer,
                run_time = run_time,
                lag_ratio=1,
            ))
            # if n == 2:
            #     dot = dot_layer[1]
            #     words = TextMobject("Stop growth at pink")
            #     words.next_to(dot, DOWN, 2)
            #     arrow = Arrow(words, dot)
            #     self.play(
            #         Write(words),
            #         ShowCreation(arrow)
            #     )
            #     self.wait()
            #     self.play(*map(FadeOut, [words, arrow]))
            log2 = np.log2(n)
            if n > 2 and log2-np.round(log2) == 0 and n < self.n_layers:
                self.wait()
                self.rescale()
                run_time /= 1.3
            last_dot_layer = dot_layer

    def rescale(self):
        shown_mobs = VGroup(*self.get_mobjects())
        shown_mobs_copy = shown_mobs.copy()
        self.remove(shown_mobs)
        self.add(shown_mobs_copy)
        top = shown_mobs.get_top()
        self.triangle.scale(0.5)
        self.triangle.move_to(top, aligned_edge = UP)
        self.play(Transform(shown_mobs_copy, shown_mobs))
        self.remove(shown_mobs_copy)
        self.add(shown_mobs)

    def get_pascal_point(self, n, k):
        return n*rotate_vector(RIGHT, -2*np.pi/3) + k*RIGHT

    def get_lines_at_layer(self, n):
        lines = VGroup()
        for k in range(n+1):
            if choose(n, k)%2 == 1:
                p1 = self.get_pascal_point(n, k)
                p2 = self.get_pascal_point(n+1, k)
                p3 = self.get_pascal_point(n+1, k+1)
                lines.add(Line(p1, p2), Line(p1, p3))
        return lines

    def get_dot_layer(self, n):
        dots = VGroup()
        for k in range(n+1):
            p = self.get_pascal_point(n, k)
            dot = Dot(p, radius = self.dot_radius)
            if choose(n, k)%2 == 0:
                if choose(n-1, k)%2 == 0:
                    continue
                dot.set_color(PINK)
            else:
                dot.set_color(WHITE)
            dots.add(dot)
        return dots

    def get_ronaks_sierpinski(self, n_layers):
        ronaks_sierpinski = VGroup()
        for n in range(n_layers):
            ronaks_sierpinski.add(self.get_lines_at_layer(n))
        ronaks_sierpinski.set_color_by_gradient(*self.colors)
        ronaks_sierpinski.set_stroke(width = 0)##TODO
        return ronaks_sierpinski

    def get_dots(self, n_layers):
        dots = VGroup()        
        for n in range(n_layers+1):
            dots.add(self.get_dot_layer(n))
        return dots

class PatreonLogo(Scene):
    def construct(self):
        words1 = TextMobject(
            "Support future\\\\",
            "3blue1brown videos"
        )
        words2 = TextMobject(
            "Early access to\\\\",
            "``Essence of'' series"
        )
        for words in words1, words2:
            words.scale(2)
            words.to_edge(DOWN)
        self.play(Write(words1))
        self.wait(2)
        self.play(Transform(words1, words2))
        self.wait(2)

class PatreonLogin(Scene):
    pass

class PythagoreanTransformation(Scene):
    def construct(self):
        tri1 = VGroup(
            Line(ORIGIN, 2*RIGHT, color = BLUE),
            Line(2*RIGHT, 3*UP, color = YELLOW),
            Line(3*UP, ORIGIN, color = MAROON_B),
        )
        tri1.shift(2.5*(DOWN+LEFT))
        tri2, tri3, tri4 = copies = [
            tri1.copy().rotate(-i*np.pi/2)
            for i in range(1, 4)
        ]
        a = TexMobject("a").next_to(tri1[0], DOWN, buff = MED_SMALL_BUFF)
        b = TexMobject("b").next_to(tri1[2], LEFT, buff = MED_SMALL_BUFF)
        c = TexMobject("c").next_to(tri1[1].get_center(), UP+RIGHT)

        c_square = Polygon(*[
            tri[1].get_end()
            for tri in [tri1] + copies
        ])
        c_square.set_stroke(width = 0)
        c_square.set_fill(color = YELLOW, opacity = 0.5)
        c_square_tex = TexMobject("c^2")
        big_square = Polygon(*[
            tri[0].get_start()
            for tri in [tri1] + copies
        ])
        big_square.set_color(WHITE)
        a_square = Square(side_length = 2)
        a_square.shift(1.5*(LEFT+UP))
        a_square.set_stroke(width = 0)
        a_square.set_fill(color = BLUE, opacity = 0.5)
        a_square_tex = TexMobject("a^2")
        a_square_tex.move_to(a_square)
        b_square = Square(side_length = 3)
        b_square.move_to(
            a_square.get_corner(DOWN+RIGHT),
            aligned_edge = UP+LEFT
        )
        b_square.set_stroke(width = 0)
        b_square.set_fill(color = MAROON_B, opacity = 0.5)
        b_square_tex = TexMobject("b^2")
        b_square_tex.move_to(b_square)

        self.play(ShowCreation(tri1, run_time = 2))
        self.play(*list(map(Write, [a, b, c])))
        self.wait()
        self.play(
            FadeIn(c_square),
            Animation(c)
        )
        self.play(Transform(c, c_square_tex))
        self.wait(2)
        mover = tri1.copy()
        for copy in copies:
            self.play(Transform(
                mover, copy,
                path_arc = -np.pi/2
            ))
            self.add(copy)
        self.remove(mover)
        self.add(big_square, *[tri1]+copies)
        self.wait(2)
        self.play(*list(map(FadeOut, [a, b, c, c_square])))
        self.play(
            tri3.shift,
            tri1.get_corner(UP+LEFT) -\
            tri3.get_corner(UP+LEFT)
        )
        self.play(tri2.shift, 2*RIGHT)
        self.play(tri4.shift, 3*UP)
        self.wait()
        self.play(FadeIn(a_square))
        self.play(FadeIn(b_square))
        self.play(Write(a_square_tex))
        self.play(Write(b_square_tex))
        self.wait(2)

class KindWordsOnEoLA(TeacherStudentsScene):
    def construct(self):
        rect = Rectangle(width = 16, height = 9, color = WHITE)
        rect.set_height(4)
        title = TextMobject("Essence of linear algebra")
        title.to_edge(UP)
        rect.next_to(title, DOWN)
        self.play(
            Write(title), 
            ShowCreation(rect),
            *[
                ApplyMethod(pi.look_at, rect)
                for pi in self.get_pi_creatures()
            ],
            run_time = 2
        )
        self.random_blink()
        self.change_student_modes(*["hooray"]*3)
        self.random_blink()
        self.play(self.get_teacher().change_mode, "happy")
        self.random_blink()

class MakeALotOfPiCreaturesHappy(Scene):
    def construct(self):
        width = 7
        height = 4
        pis = VGroup(*[
            VGroup(*[
                Randolph()
                for x in range(7)
            ]).arrange(RIGHT, buff = MED_LARGE_BUFF)
            for x in range(4)
        ]).arrange(DOWN, buff = MED_LARGE_BUFF)

        pi_list = list(it.chain(*[
            layer.submobjects
            for layer in pis.submobjects
        ]))
        random.shuffle(pi_list)
        colors = color_gradient([BLUE_D, GREY_BROWN], len(pi_list))
        for pi, color in zip(pi_list, colors):
            pi.set_color(color)
        pis = VGroup(*pi_list)
        pis.set_height(6)

        self.add(pis)
        pis.generate_target()
        self.wait()
        for pi, color in zip(pis.target, colors):
            pi.change_mode("hooray")
            # pi.scale_in_place(1)
            pi.set_color(color)
        self.play(
            MoveToTarget(
                pis,
                run_time = 2,
                lag_ratio = 0.5,
            )
        )
        for x in range(10):
            pi = random.choice(pi_list)
            self.play(Blink(pi))


class IntegrationByParts(Scene):
    def construct(self):
        rect = Rectangle(width = 5, height = 3)
        # f = lambda t : 4*np.sin(t*np.pi/2)
        f = lambda t : 4*t
        g = lambda t : 3*smooth(t)
        curve = ParametricFunction(lambda t : f(t)*RIGHT + g(t)*DOWN)
        curve.set_color(YELLOW)
        curve.center()
        rect = Rectangle()
        rect.replace(curve, stretch = True)

        regions = []
        for vect, color in (UP+RIGHT, BLUE), (DOWN+LEFT, GREEN):
            region = curve.copy()
            region.add_line_to(rect.get_corner(vect))
            region.set_stroke(width = 0)
            region.set_fill(color = color, opacity = 0.5)
            regions.append(region)
        upper_right, lower_left = regions

        v_lines, h_lines = VGroup(), VGroup()
        for alpha in np.linspace(0, 1, 30):
            point = curve.point_from_proportion(alpha)
            top_point = curve.points[0][1]*UP + point[0]*RIGHT
            left_point = curve.points[0][0]*RIGHT + point[1]*UP
            v_lines.add(Line(top_point, point))
            h_lines.add(Line(left_point, point))
        v_lines.set_color(BLUE_E)
        h_lines.set_color(GREEN_E)

        equation = TexMobject(
            "\\int_0^1 g\\,df", 
            "+\\int_0^1 f\\,dg",
            "= \\big(fg \\big)_0^1"
        )
        equation.to_edge(UP)
        equation.set_color_by_tex(
            "\\int_0^1 g\\,df",
            upper_right.get_color()
        )
        equation.set_color_by_tex(
            "+\\int_0^1 f\\,dg",
            lower_left.get_color()
        )

        left_brace = Brace(rect, LEFT)
        down_brace = Brace(rect, DOWN)
        g_T = left_brace.get_text("$g(t)\\big|_0^1$")
        f_T = down_brace.get_text("$f(t)\\big|_0^1$")

        self.draw_curve(curve)
        self.play(ShowCreation(rect))
        self.play(*list(map(Write, [down_brace, left_brace, f_T, g_T])))
        self.wait()
        self.play(FadeIn(upper_right))
        self.play(
            ShowCreation(
                v_lines,
                run_time = 2
            ),
            Animation(curve),
            Animation(rect)
        )
        self.play(Write(equation[0]))
        self.wait()
        self.play(FadeIn(lower_left))
        self.play(
            ShowCreation(
                h_lines,
                run_time = 2
            ),
            Animation(curve),
            Animation(rect)
        )
        self.play(Write(equation[1]))
        self.wait()
        self.play(Write(equation[2]))
        self.wait()

    def draw_curve(self, curve):
        lp, lnum, comma, rnum, rp = coords = TexMobject(
            "\\big(f(", "t", "), g(", "t", ")\\big)"
        )
        coords.set_color_by_tex("0.00", BLACK)
        dot = Dot(radius = 0.1)
        dot.move_to(curve.points[0])
        coords.next_to(dot, UP+RIGHT)
        self.play(
            ShowCreation(curve),
            UpdateFromFunc(
                dot,
                lambda d : d.move_to(curve.points[-1])
            ),
            MaintainPositionRelativeTo(coords, dot),
            run_time = 5,
            rate_func=linear
        )
        self.wait()
        self.play(*list(map(FadeOut, [coords, dot])))

class EndScreen(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            """
            See you every 
            other friday!
            """,
            target_mode = "hooray"
        )
        self.change_student_modes(*["happy"]*3)
        self.random_blink()































