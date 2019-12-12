from manimlib.imports import *
from old_projects.eoc.chapter2 import DISTANCE_COLOR, TIME_COLOR, \
    VELOCITY_COLOR, Car, MoveCar

OUTPUT_COLOR = DISTANCE_COLOR
INPUT_COLOR = TIME_COLOR
DERIVATIVE_COLOR = VELOCITY_COLOR

class Chapter3OpeningQuote(OpeningQuote):
    CONFIG = {
        "quote" : [
            "You know, for a mathematician, he did not have \\\\ enough",
            "imagination.", 
            "But he has become a poet and \\\\ now he is fine.",
        ],
        "highlighted_quote_terms" : {
            "imagination." : BLUE,
        },
        "author" : "David Hilbert"
    }

class PoseAbstractDerivative(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            Given $f(x) = x^2 \\sin(x)$, \\\\
            compute $\\frac{df}{dx}(x)$
        """)
        content_copy = self.teacher.bubble.content.copy()
        self.change_student_modes("sad", "confused", "erm")
        self.wait()
        self.student_says(
            "Why?", target_mode = "sassy",
            added_anims = [
                content_copy.scale, 0.8,
                content_copy.to_corner, UP+LEFT
            ]
        )
        self.play(self.teacher.change_mode, "pondering")
        self.wait(2)

class ContrastAbstractAndConcrete(Scene):
    def construct(self):
        v_line = Line(UP, DOWN).scale(FRAME_Y_RADIUS)
        l_title = TextMobject("Abstract functions")
        l_title.shift(FRAME_X_RADIUS*LEFT/2)
        l_title.to_edge(UP)
        r_title = TextMobject("Applications")
        r_title.shift(FRAME_X_RADIUS*RIGHT/2)
        r_title.to_edge(UP)
        h_line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS)
        h_line.shift((r_title.get_bottom()[1]-MED_SMALL_BUFF)*UP)

        functions = VGroup(*list(map(TexMobject, [
            "f(x) = 2x^2 - x^3",
            "f(x) = \\sin(x)",
            "f(x) = e^x",
            "\\v_dots"
        ])))
        functions.arrange(
            DOWN, 
            aligned_edge = LEFT,
            buff = LARGE_BUFF
        )
        functions.shift(FRAME_X_RADIUS*LEFT/2)
        functions[-1].shift(MED_LARGE_BUFF*RIGHT)

        self.add(l_title, r_title)
        self.play(*list(map(ShowCreation, [h_line, v_line])))
        self.play(Write(functions))
        self.wait()
        anims = [
            method(func_mob)
            for func_mob, method in zip(functions, [
                self.get_car_anim,
                self.get_spring_anim,
                self.get_population_anim,
            ])
        ]
        for anim in anims:
            self.play(FadeIn(anim.mobject))
            self.play(anim)
            self.play(FadeOut(anim.mobject))


    def get_car_anim(self, alignement_mob):
        car = Car()
        point = 2*RIGHT + alignement_mob.get_bottom()[1]*UP
        target_point = point + 5*RIGHT
        car.move_to(point)
        return MoveCar(
            car, target_point, 
            run_time = 5,
        )

    def get_spring_anim(self, alignement_mob):
        compact_spring, extended_spring = [
            ParametricFunction(
                lambda t : (t/denom)*RIGHT+np.sin(t)*UP+np.cos(t)*OUT,
                t_max = 12*np.pi,
            )
            for denom in (12.0, 4.0)
        ]
        for spring in compact_spring, extended_spring:
            spring.scale(0.5)
            spring.rotate(np.pi/6, UP)
            spring.set_color(GREY)
            spring.next_to(ORIGIN, RIGHT)
            spring.shift(
                alignement_mob.get_center()[1]*UP + SMALL_BUFF*RIGHT \
                -spring.points[0]
            )
            weight = Square(
                side_length = 0.5,
                stroke_width = 0, 
                fill_color = LIGHT_GREY,
                fill_opacity = 1,
            )
            weight.move_to(spring.points[-1])
            spring.add(weight)

        return Transform(
            compact_spring, extended_spring, 
            rate_func = lambda t : 1+np.sin(6*np.pi*t),
            run_time = 5
        )

    def get_population_anim(self, alignement_mob):
        colors = color_gradient([BLUE_B, BLUE_E], 12)
        pis = VGroup(*[
            Randolph(
                mode = "happy",
                color = random.choice(colors)
            ).shift(
                4*x*RIGHT + 4*y*UP + \
                2*random.random()*RIGHT + \
                2*random.random()*UP
            )
            for x in range(20)
            for y in range(10)
        ])
        pis.set_height(3)
        pis.center()
        pis.to_edge(DOWN, buff = SMALL_BUFF)
        pis.shift(FRAME_X_RADIUS*RIGHT/2.)

        anims = []
        for index, pi in enumerate(pis):
            if index < 2:
                anims.append(FadeIn(pi))
                continue
            mom_index, dad_index = random.choice(
                list(it.combinations(list(range(index)), 2))
            )
            pi.parents = VGroup(pis[mom_index], pis[dad_index]).copy()
            pi.parents.set_fill(opacity = 0)
        exp = 1
        while 2**exp < len(pis):
            low_index = 2**exp
            high_index = min(2**(exp+1), len(pis))
            these_pis = pis[low_index:high_index]
            anims.append(Transform(
                VGroup(*[pi.parents for pi in these_pis]),
                VGroup(*[VGroup(pi, pi.copy()) for pi in these_pis]),
                lag_ratio = 0.5,
                run_time = 2,
            ))
            exp += 1

        return Succession(*anims, rate_func=linear)

class ApplicationNames(Scene):
    def construct(self):
        for name in "Velocity", "Oscillation", "Population growth":
            mob = TextMobject(name)
            mob.scale(2)
            self.play(Write(mob))
            self.wait(2)
            self.play(FadeOut(mob))

class ListOfRules(PiCreatureScene):
    CONFIG = {
        "use_morty" : False,
    }
    def construct(self):
        rules = VGroup(*list(map(TexMobject, [
            "\\frac{d}{dx} x^n = nx^{n-1}",
            "\\frac{d}{dx} \\sin(x) = \\cos(x)",
            "\\frac{d}{dx} \\cos(x) = -\\sin(x)",
            "\\frac{d}{dx} a^x = \\ln(a) a^x",
            "\\vdots"
        ])))
        rules.arrange(
            DOWN, buff = MED_LARGE_BUFF,
            aligned_edge = LEFT,
        )
        rules[-1].shift(MED_LARGE_BUFF*RIGHT)
        rules.set_height(FRAME_HEIGHT-1)
        rules.next_to(self.pi_creature, RIGHT)
        rules.to_edge(DOWN)

        self.play(
            Write(rules),
            self.pi_creature.change_mode, "pleading",
        )
        self.change_mode("tired")
        self.wait()

class DerivativeOfXSquaredAsGraph(GraphScene, ZoomedScene, PiCreatureScene):
    CONFIG = {
        "start_x" : 2,
        "big_x" : 3,
        "dx" : 0.1,
        "x_min" : -9,
        "x_labeled_nums" : list(range(-8, 0, 2)) + list(range(2, 10, 2)),
        "y_labeled_nums" : list(range(2, 12, 2)),
        "little_rect_nudge" : 0.5*(1.5*UP+RIGHT),
        "graph_origin" : 2.5*DOWN + LEFT,
        "zoomed_canvas_corner" : UP+LEFT,
        "zoomed_canvas_frame_shape" : (4, 4),
    }
    def construct(self):
        self.draw_graph()
        self.ask_about_df_dx()
        self.show_differing_slopes()
        self.mention_alternate_view()

    def draw_graph(self):
        self.setup_axes(animate = True)
        graph = self.get_graph(lambda x : x**2)
        label = self.get_graph_label(
            graph, "f(x) = x^2",
        )
        self.play(ShowCreation(graph))
        self.play(Write(label))
        self.wait()
        self.graph = graph

    def ask_about_df_dx(self):
        ss_group = self.get_secant_slope_group(
            self.start_x, self.graph,
            dx = self.dx,
            dx_label = "dx",
            df_label = "df",
        )
        secant_line = ss_group.secant_line
        ss_group.remove(secant_line)

        v_line, nudged_v_line = [
            self.get_vertical_line_to_graph(
                x, self.graph,
                line_class = DashedLine,
                color = RED,
                dash_length = 0.025
            )
            for x in (self.start_x, self.start_x+self.dx)
        ]

        df_dx = TexMobject("\\frac{df}{dx} ?")
        VGroup(*df_dx[:2]).set_color(ss_group.df_line.get_color())
        VGroup(*df_dx[3:5]).set_color(ss_group.dx_line.get_color())
        df_dx.next_to(
            self.input_to_graph_point(self.start_x, self.graph),
            DOWN+RIGHT,
            buff = MED_SMALL_BUFF
        )

        derivative_q = TextMobject("Derivative?")
        derivative_q.next_to(self.pi_creature.get_corner(UP+LEFT), UP)


        self.play(
            Write(derivative_q, run_time = 1),
            self.pi_creature.change_mode, "speaking"
        )
        self.wait()
        self.play(
            FadeOut(derivative_q),
            self.pi_creature.change_mode, "plain"
        )
        self.play(ShowCreation(v_line))
        self.wait()
        self.play(Transform(v_line.copy(), nudged_v_line))
        self.remove(self.get_mobjects_from_last_animation()[0])
        self.add(nudged_v_line)
        self.wait()
        self.activate_zooming()
        self.little_rectangle.replace(self.big_rectangle)
        self.play(
            FadeIn(self.little_rectangle),
            FadeIn(self.big_rectangle),
        )
        self.play(
            ApplyFunction(
                lambda r : self.position_little_rectangle(r, ss_group),
                self.little_rectangle
            ),
            self.pi_creature.change_mode, "pondering",
            self.pi_creature.look_at, ss_group
        )
        self.play(
            ShowCreation(ss_group.dx_line),
            Write(ss_group.dx_label),
        )
        self.wait()
        self.play(
            ShowCreation(ss_group.df_line),
            Write(ss_group.df_label),
        )
        self.wait()
        self.play(Write(df_dx))
        self.wait()
        self.play(*list(map(FadeOut, [
            v_line, nudged_v_line,
        ])))
        self.ss_group = ss_group

    def position_little_rectangle(self, rect, ss_group):
        rect.set_width(3*self.dx)
        rect.move_to(
            ss_group.dx_line.get_left()
        )
        rect.shift(
            self.dx*self.little_rect_nudge
        )
        return rect

    def show_differing_slopes(self):
        ss_group = self.ss_group
        def rect_update(rect):
            self.position_little_rectangle(rect, ss_group)

        self.play(
            ShowCreation(ss_group.secant_line),
            self.pi_creature.change_mode, "thinking"
        )
        ss_group.add(ss_group.secant_line)
        self.wait()
        for target_x in self.big_x, -self.dx/2, 1, 2:
            self.animate_secant_slope_group_change(
                ss_group, target_x = target_x,
                added_anims = [
                    UpdateFromFunc(self.little_rectangle, rect_update)
                ]
            )
            self.wait()

    def mention_alternate_view(self):
        self.remove(self.pi_creature)
        everything = VGroup(*self.get_mobjects())
        self.add(self.pi_creature)
        self.disactivate_zooming()
        self.play(
            ApplyMethod(
                everything.shift, FRAME_WIDTH*LEFT,
                rate_func = lambda t : running_start(t, -0.1)
            ),
            self.pi_creature.change_mode, "happy"
        )
        self.say("Let's try \\\\ another view.", target_mode = "speaking")
        self.wait(2)

class NudgeSideLengthOfSquare(PiCreatureScene):
    CONFIG = {
        "square_width" : 3,
        "alt_square_width" : 5,
        "dx" : 0.25,
        "alt_dx" : 0.01,
        "square_color" : GREEN,
        "square_fill_opacity" : 0.75,
        "three_color" : GREEN,
        "dx_color" : BLUE_B,
        "is_recursing_on_dx" : False,
        "is_recursing_on_square_width" : False,
    }
    def construct(self):
        ApplyMethod(self.pi_creature.change_mode, "speaking").update(1)
        self.add_function_label()
        self.introduce_square()
        self.increase_area()
        self.write_df_equation()
        self.set_color_shapes()
        self.examine_thin_rectangles()
        self.examine_tiny_square()
        self.show_smaller_dx()
        self.rule_of_thumb()
        self.write_out_derivative()

    def add_function_label(self):
        label = TexMobject("f(x) = x^2")
        label.next_to(ORIGIN, RIGHT, buff = (self.square_width-3)/2.)
        label.to_edge(UP)
        self.add(label)
        self.function_label = label

    def introduce_square(self):
        square = Square(
            side_length = self.square_width,
            stroke_width = 0,
            fill_opacity = self.square_fill_opacity,
            fill_color = self.square_color,
        )
        square.to_corner(UP+LEFT, buff = LARGE_BUFF)
        x_squared = TexMobject("x^2")
        x_squared.move_to(square)

        braces = VGroup()
        for vect in RIGHT, DOWN:
            brace = Brace(square, vect)
            text = brace.get_text("$x$")
            brace.add(text)
            braces.add(brace)

        self.play(
            DrawBorderThenFill(square),
            self.pi_creature.change_mode, "plain"
        )
        self.play(*list(map(GrowFromCenter, braces)))
        self.play(Write(x_squared))
        self.change_mode("pondering")
        self.wait()

        self.square = square
        self.side_braces = braces

    def increase_area(self):
        color_kwargs = {
            "fill_color" : YELLOW,
            "fill_opacity" : self.square_fill_opacity,
            "stroke_width" : 0,
        }
        right_rect = Rectangle(
            width = self.dx,
            height = self.square_width,
            **color_kwargs
        )
        bottom_rect = right_rect.copy().rotate(-np.pi/2)
        right_rect.next_to(self.square, RIGHT, buff = 0)
        bottom_rect.next_to(self.square, DOWN, buff = 0)
        corner_square = Square(
            side_length = self.dx,
            **color_kwargs
        )
        corner_square.next_to(self.square, DOWN+RIGHT, buff = 0)

        right_line = Line(
            self.square.get_corner(UP+RIGHT),
            self.square.get_corner(DOWN+RIGHT),
            stroke_width = 0
        )
        bottom_line = Line(
            self.square.get_corner(DOWN+RIGHT),
            self.square.get_corner(DOWN+LEFT),
            stroke_width = 0
        )
        corner_point = VectorizedPoint(
            self.square.get_corner(DOWN+RIGHT)
        )

        little_braces = VGroup()
        for vect in RIGHT, DOWN:
            brace = Brace(
                corner_square, vect, 
                buff = SMALL_BUFF,
            )
            text = brace.get_text("$dx$", buff = SMALL_BUFF)
            text.set_color(self.dx_color)
            brace.add(text)
            little_braces.add(brace)

        right_brace, bottom_brace = self.side_braces
        self.play(
            Transform(right_line, right_rect),
            Transform(bottom_line, bottom_rect),
            Transform(corner_point, corner_square),
            right_brace.next_to, right_rect, RIGHT, SMALL_BUFF,
            bottom_brace.next_to, bottom_rect, DOWN, SMALL_BUFF,
        )
        self.remove(corner_point, bottom_line, right_line)
        self.add(corner_square, bottom_rect, right_rect)
        self.play(*list(map(GrowFromCenter, little_braces)))
        self.wait()
        self.play(*it.chain(*[
            [mob.shift, vect*SMALL_BUFF]
            for mob, vect in [
                (right_rect, RIGHT),
                (bottom_rect, DOWN),
                (corner_square, DOWN+RIGHT),
                (right_brace, RIGHT),
                (bottom_brace, DOWN),
                (little_braces, DOWN+RIGHT)
            ]
        ]))
        self.change_mode("thinking")
        self.wait()
        self.right_rect = right_rect
        self.bottom_rect = bottom_rect
        self.corner_square = corner_square
        self.little_braces = little_braces

    def write_df_equation(self):
        right_rect = self.right_rect
        bottom_rect = self.bottom_rect
        corner_square = self.corner_square

        df_equation = VGroup(
            TexMobject("df").set_color(right_rect.get_color()),
            TexMobject("="),
            right_rect.copy(),
            TextMobject("+"),
            right_rect.copy(),
            TexMobject("+"),
            corner_square.copy()
        )
        df_equation.arrange()
        df_equation.next_to(
            self.function_label, DOWN, 
            aligned_edge = LEFT,
            buff = SMALL_BUFF
        )
        df, equals, r1, plus1, r2, plus2, s = df_equation

        pairs = [
            (df, self.function_label[0]),
            (r1, right_rect), 
            (r2, bottom_rect), 
            (s, corner_square),
        ]
        for mover, origin in pairs:
            mover.save_state()
            Transform(mover, origin).update(1)
        self.play(df.restore)
        self.wait()
        self.play(
            *[
                mob.restore
                for mob in (r1, r2, s)
            ]+[
                Write(symbol)
                for symbol in (equals, plus1, plus2)
            ], 
            run_time = 2
        )
        self.change_mode("happy")
        self.wait()

        self.df_equation = df_equation

    def set_color_shapes(self):
        df, equals, r1, plus1, r2, plus2, s = self.df_equation

        tups = [
            (self.right_rect, self.bottom_rect, r1, r2),
            (self.corner_square, s)
        ]
        for tup in tups:
            self.play(
                *it.chain(*[
                    [m.scale_in_place, 1.2, m.set_color, RED]
                    for m in tup
                ]), 
                rate_func = there_and_back
            )
            self.wait()

    def examine_thin_rectangles(self):
        df, equals, r1, plus1, r2, plus2, s = self.df_equation

        rects = VGroup(r1, r2)
        thin_rect_brace = Brace(rects, DOWN)
        text = thin_rect_brace.get_text("$2x \\, dx$")
        VGroup(*text[-2:]).set_color(self.dx_color)
        text.save_state()
        alt_text = thin_rect_brace.get_text("$2(3)(0.01)$")
        alt_text[2].set_color(self.three_color)
        VGroup(*alt_text[-5:-1]).set_color(self.dx_color)

        example_value = TexMobject("=0.06")
        example_value.next_to(alt_text, DOWN)

        self.play(GrowFromCenter(thin_rect_brace))
        self.play(
            Write(text),
            self.pi_creature.change_mode, "pondering"
        )
        self.wait()

        xs = VGroup(*[
            brace[-1] 
            for brace in self.side_braces
        ])
        dxs = VGroup(*[
            brace[-1]
            for brace in self.little_braces
        ])
        for group, tex, color in (xs, "3", self.three_color), (dxs, "0.01", self.dx_color):
            group.save_state()            
            group.generate_target()            
            for submob in group.target:
                number = TexMobject(tex)
                number.set_color(color)
                number.move_to(submob, LEFT)
                Transform(submob, number).update(1)
        self.play(MoveToTarget(xs))
        self.play(MoveToTarget(dxs))
        self.wait()
        self.play(Transform(text, alt_text))
        self.wait()
        self.play(Write(example_value))
        self.wait()
        self.play(
            FadeOut(example_value),
            *[
                mob.restore
                for mob in (xs, dxs, text)
            ]
        )
        self.remove(text)
        text.restore()
        self.add(text)

        self.wait()
        self.dxs = dxs
        self.thin_rect_brace = thin_rect_brace
        self.thin_rect_area = text        

    def examine_tiny_square(self):
        text = TexMobject("dx^2")
        VGroup(*text[:2]).set_color(self.dx_color)
        text.next_to(self.df_equation[-1], UP)
        text.save_state()
        alt_text = TextMobject("0.0001")
        alt_text.move_to(text)

        self.play(Write(text))
        self.change_mode("surprised")
        self.wait()
        self.play(
            MoveToTarget(self.dxs),
            self.pi_creature.change_mode, "plain"
        )
        for submob in self.dxs.target:
            number = TexMobject("0.01")
            number.set_color(self.dx_color)
            number.move_to(submob, LEFT)
            Transform(submob, number).update(1)
        self.play(MoveToTarget(self.dxs))
        self.play(
            Transform(text, alt_text),
            self.pi_creature.change_mode, "raise_right_hand"
        )
        self.wait(2)
        self.play(*[
            mob.restore
            for mob in (self.dxs, text)
        ] + [
            self.pi_creature.change_mode, "erm"
        ])
        self.dx_squared = text

    def show_smaller_dx(self):
        self.mobjects_at_start_of_show_smaller_dx = [
            mob.copy() for mob in self.get_mobjects()
        ]
        if self.is_recursing_on_dx:
            return

        alt_scene = self.__class__(
            skip_animations = True,
            dx = self.alt_dx,
            is_recursing_on_dx = True
        )
        for mob in self.get_mobjects():
            mob.save_state()
        self.play(*[
            Transform(*pair)
            for pair in zip(
                self.get_mobjects(),
                alt_scene.mobjects_at_start_of_show_smaller_dx,
            )
        ])
        self.wait()
        self.play(*[
            mob.restore
            for mob in self.get_mobjects()
        ])
        self.change_mode("happy")
        self.wait()

    def rule_of_thumb(self):
        circle = Circle(color = RED)
        dx_squared_group = VGroup(self.dx_squared, self.df_equation[-1])
        circle.replace(dx_squared_group, stretch = True)
        dx_squared_group.add(self.df_equation[-2])
        circle.scale_in_place(1.5)
        safe_to_ignore = TextMobject("Safe to ignore")
        safe_to_ignore.next_to(circle, DOWN, aligned_edge = LEFT)
        safe_to_ignore.set_color(circle.get_color())

        self.play(ShowCreation(circle))
        self.play(
            Write(safe_to_ignore, run_time = 2),
            self.pi_creature.change_mode, "raise_right_hand"
        )
        self.play(
            FadeOut(circle),
            FadeOut(safe_to_ignore),
            dx_squared_group.fade, 0.5,
            dx_squared_group.to_corner, UP+RIGHT,
            self.pi_creature.change_mode, "plain"
        )
        self.wait()

    def write_out_derivative(self):
        df, equals, r1, plus1, r2, plus2, s = self.df_equation
        frac_line = TexMobject("-")
        frac_line.stretch_to_fit_width(df.get_width())
        frac_line.move_to(df)
        dx = VGroup(*self.thin_rect_area[-2:]) 
        x = self.thin_rect_area[1]

        self.play(
            Transform(r1, self.right_rect),
            Transform(r2, self.bottom_rect),
            FadeOut(plus1),
            FadeOut(self.thin_rect_brace)
        )
        self.play(
            self.thin_rect_area.next_to, VGroup(df, equals),
            RIGHT, MED_SMALL_BUFF, UP,
            self.pi_creature.change_mode, "thinking"
        )
        self.wait(2)
        self.play(
            ApplyMethod(df.next_to, frac_line, UP, SMALL_BUFF),
            ApplyMethod(dx.next_to, frac_line, DOWN, SMALL_BUFF),
            Write(frac_line),            
            path_arc = -np.pi
        )
        self.wait()

        brace_xs = [
            brace[-1]
            for brace in self.side_braces
        ]
        xs = list(brace_xs) + [x]
        for x_mob in xs:
            number = TexMobject("(%d)"%self.square_width)
            number.move_to(x_mob, LEFT)
            number.shift(
                (x_mob.get_bottom()[1] - number[1].get_bottom()[1])*UP
            )
            x_mob.save_state()
            x_mob.target = number
        self.play(*list(map(MoveToTarget, xs)))
        self.wait(2)

        #Recursively transform to what would have happened
        #with a wider square width
        self.mobjects_at_end_of_write_out_derivative = self.get_mobjects()
        if self.is_recursing_on_square_width or self.is_recursing_on_dx:
            return
        alt_scene = self.__class__(
            skip_animations = True,
            square_width = self.alt_square_width,
            is_recursing_on_square_width = True,
        )
        self.play(*[
            Transform(*pair)
            for pair in zip(
                self.mobjects_at_end_of_write_out_derivative,
                alt_scene.mobjects_at_end_of_write_out_derivative
            )
        ])
        self.change_mode("happy")
        self.wait(2)

class ChangeInAreaOverChangeInX(Scene):
    def construct(self):
        fractions = []
        for pair in ("Change in area", "Change in $x$"), ("$d(x^2)$", "$dx$"):
            top, bottom = list(map(TextMobject, pair))
            top.set_color(YELLOW)
            bottom.set_color(BLUE_B)
            frac_line = TexMobject("-")
            frac_line.stretch_to_fit_width(top.get_width())
            top.next_to(frac_line, UP, SMALL_BUFF)
            bottom.next_to(frac_line, DOWN, SMALL_BUFF)
            fractions.append(VGroup(
                top, frac_line, bottom
            ))
        words, symbols = fractions

        self.play(Write(words[0], run_time = 1))
        self.play(*list(map(Write, words[1:])), run_time = 1)
        self.wait()
        self.play(Transform(words, symbols))
        self.wait()

class NudgeSideLengthOfCube(Scene):
    CONFIG = {
        "x_color" : BLUE,
        "dx_color" : GREEN,
        "df_color" : YELLOW,
        "use_morty" : False,
        "x" : 3,
        "dx" : 0.2,
        "alt_dx" : 0.02,
        "offset_vect" : OUT,
        "pose_angle" : np.pi/12,
        "pose_axis" : UP+RIGHT,
        "small_piece_scaling_factor" : 0.7,
        "allow_recursion" : True,
    }
    def construct(self):
        self.states = dict()
        if self.allow_recursion:
            self.alt_scene = self.__class__(
                skip_animations = True,
                allow_recursion = False,
                dx = self.alt_dx,
            )

        self.add_title()
        self.introduce_cube()
        self.write_df_equation()
        self.write_derivative()

    def add_title(self):
        title = TexMobject("f(x) = x^3")
        title.shift(FRAME_X_RADIUS*LEFT/2)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait()

    def introduce_cube(self):
        cube = self.get_cube()
        cube.to_edge(LEFT, buff = 2*LARGE_BUFF)
        cube.shift(DOWN)

        dv_pieces = self.get_dv_pices(cube)
        original_dx = self.dx
        self.dx = 0
        alt_dv_pieces = self.get_dv_pices(cube)
        self.dx = original_dx
        alt_dv_pieces.set_fill(opacity = 0)

        x_brace = Brace(cube, LEFT, buff = SMALL_BUFF)
        dx_brace = Brace(
            dv_pieces[1], LEFT, buff = SMALL_BUFF,
        )
        dx_brace.stretch_in_place(1.5, 1)
        for brace, tex in (x_brace, "x"), (dx_brace, "dx"):
            brace.scale_in_place(0.95)
            brace.rotate_in_place(-np.pi/96)
            brace.shift(0.3*(UP+LEFT))
            brace.add(brace.get_text("$%s$"%tex))


        cube_group = VGroup(cube, dv_pieces, alt_dv_pieces)
        self.pose_3d_mobject(cube_group)

        self.play(DrawBorderThenFill(cube))
        self.play(GrowFromCenter(x_brace))
        self.wait()
        self.play(Transform(alt_dv_pieces, dv_pieces))
        self.remove(alt_dv_pieces)
        self.add(dv_pieces)
        self.play(GrowFromCenter(dx_brace))
        self.wait()
        for piece in dv_pieces:
            piece.on_cube_state = piece.copy()
        self.play(*[
            ApplyMethod(
                piece.shift, 
                0.5*(piece.get_center()-cube.get_center())
            )
            for piece in dv_pieces
        ]+[
            ApplyMethod(dx_brace.shift, 0.7*UP)
        ])
        self.wait()

        self.cube = cube
        self.dx_brace = dx_brace
        self.faces, self.bars, self.corner_cube = [
            VGroup(*[
                piece 
                for piece in dv_pieces
                if piece.type == target_type
            ])
            for target_type in ("face", "bar", "corner_cube")
        ]

    def write_df_equation(self):
        df_equation = VGroup(
            TexMobject("df"),
            TexMobject("="),
            self.organize_faces(self.faces.copy()),
            TexMobject("+"),
            self.organize_bars(self.bars.copy()),
            TexMobject("+"),
            self.corner_cube.copy()
        )
        df, equals, faces, plus1, bars, plus2, corner_cube = df_equation
        df.set_color(self.df_color)
        for three_d_mob in faces, bars, corner_cube:
            three_d_mob.scale(self.small_piece_scaling_factor)
            # self.pose_3d_mobject(three_d_mob)
        faces.set_fill(opacity = 0.3)
        df_equation.arrange(RIGHT)
        df_equation.next_to(ORIGIN, RIGHT)
        df_equation.to_edge(UP)

        faces_brace = Brace(faces, DOWN)
        derivative = faces_brace.get_tex("3x^2", "\\, dx")
        extras_brace = Brace(VGroup(bars, corner_cube), DOWN)
        ignore_text = extras_brace.get_text(
            "Multiple \\\\ of $dx^2$"
        )
        ignore_text.scale_in_place(0.7)
        x_squared_dx = TexMobject("x^2", "\\, dx")


        self.play(*list(map(Write, [df, equals])))
        self.grab_pieces(self.faces, faces)
        self.wait()
        self.shrink_dx("Faces are introduced")
        face = self.faces[0]
        face.save_state()
        self.play(face.shift, FRAME_X_RADIUS*RIGHT)
        x_squared_dx.next_to(face, LEFT)
        self.play(Write(x_squared_dx, run_time = 1))
        self.wait()
        for submob, sides in zip(x_squared_dx, [face[0], VGroup(*face[1:])]):
            self.play(
                submob.set_color, RED,
                sides.set_color, RED,
                rate_func = there_and_back
            )
            self.wait()
        self.play(
            face.restore,
            Transform(
                x_squared_dx, derivative,
                replace_mobject_with_target_in_scene = True
            ),
            GrowFromCenter(faces_brace)
        )
        self.wait()
        self.grab_pieces(self.bars, bars, plus1)
        self.grab_pieces(self.corner_cube, corner_cube, plus2)
        self.play(
            GrowFromCenter(extras_brace),
            Write(ignore_text)
        )
        self.wait()
        self.play(*[
            ApplyMethod(mob.fade, 0.7)
            for mob in [
                plus1, bars, plus2, corner_cube, 
                extras_brace, ignore_text
            ]
        ])
        self.wait()

        self.df_equation = df_equation
        self.derivative = derivative

    def write_derivative(self):
        df, equals, faces, plus1, bars, plus2, corner_cube = self.df_equation
        df = df.copy()
        equals = equals.copy()        
        df_equals = VGroup(df, equals)        

        derivative = self.derivative.copy()
        dx = derivative[1]

        extra_stuff = TexMobject("+(\\dots)", "dx^2")
        dx_squared = extra_stuff[1]

        derivative.generate_target()
        derivative.target.shift(2*DOWN)
        extra_stuff.next_to(derivative.target)
        self.play(
            MoveToTarget(derivative),
            df_equals.next_to, derivative.target[0], LEFT,
            df_equals.shift, 0.07*DOWN
        )
        self.play(Write(extra_stuff))
        self.wait()

        frac_line = TexMobject("-")
        frac_line.replace(df)
        extra_stuff.generate_target()
        extra_stuff.target.next_to(derivative[0])
        frac_line2 = TexMobject("-")
        frac_line2.stretch_to_fit_width(
            extra_stuff.target[1].get_width()
        )
        frac_line2.move_to(extra_stuff.target[1])
        extra_stuff.target[1].next_to(frac_line2, UP, buff = SMALL_BUFF)
        dx_below_dx_squared = TexMobject("dx")
        dx_below_dx_squared.next_to(frac_line2, DOWN, buff = SMALL_BUFF)
        self.play(
            FadeIn(frac_line),
            FadeIn(frac_line2),
            df.next_to, frac_line, UP, SMALL_BUFF,
            dx.next_to, frac_line, DOWN, SMALL_BUFF,
            MoveToTarget(extra_stuff),
            Write(dx_below_dx_squared),
            path_arc = -np.pi
        )
        self.wait()
        inner_dx = VGroup(*dx_squared[:-1])
        self.play(
            FadeOut(frac_line2),
            FadeOut(dx_below_dx_squared),
            dx_squared[-1].set_color, BLACK,
            inner_dx.next_to, extra_stuff[0], RIGHT, SMALL_BUFF
        )
        self.wait()
        self.shrink_dx("Derivative is written", restore = False)
        self.play(*[
            ApplyMethod(mob.fade, 0.7)
            for mob in (extra_stuff, inner_dx)
        ])
        self.wait(2)

        anims = []
        for mob in list(self.faces)+list(self.bars)+list(self.corner_cube):
            vect = mob.get_center()-self.cube.get_center()
            anims += [
                mob.shift, -(1./3)*vect
            ]
        anims += self.dx_brace.shift, 0.7*DOWN
        self.play(*anims)
        self.wait()

    def grab_pieces(self, start_pieces, end_pices, to_write = None):
        for piece in start_pieces:
            piece.generate_target()
            piece.target.rotate_in_place(
                np.pi/12, piece.get_center()-self.cube.get_center()
            )
            piece.target.set_color(RED)
        self.play(*list(map(MoveToTarget, start_pieces)), rate_func = wiggle)
        self.wait()
        added_anims = []
        if to_write is not None:
            added_anims.append(Write(to_write))
        self.play(
            Transform(start_pieces.copy(), end_pices),
            *added_anims
        )

    def shrink_dx(self, state_name, restore = True):
        mobjects = self.get_mobjects()
        mobjects_with_points = [
            m for m in mobjects
            if m.get_num_points() > 0
        ]
        #Alt_scene will reach this point, and save copy of self
        #in states dict
        self.states[state_name] = [
            mob.copy() for mob in mobjects_with_points
        ] 
        if not self.allow_recursion:
            return
        if restore:
            movers = self.states[state_name]
            for mob in movers:
                mob.save_state()
            self.remove(*mobjects)
        else:
            movers = mobjects_with_points
        self.play(*[
            Transform(*pair)
            for pair in zip(
                movers,
                self.alt_scene.states[state_name]
            )
        ])
        self.wait()
        if restore:
            self.play(*[m.restore for m in movers])
            self.remove(*movers)
            self.mobjects = mobjects

    def get_cube(self):
        cube = self.get_prism(self.x, self.x, self.x)
        cube.set_fill(color = BLUE, opacity = 0.3)
        cube.set_stroke(color = WHITE, width = 1)
        return cube

    def get_dv_pices(self, cube):
        pieces = VGroup()
        for vect in it.product([0, 1], [0, 1], [0, 1]):
            if np.all(vect == ORIGIN):
                continue
            args = [
                self.x if bit is 0 else self.dx
                for bit in vect
            ]
            piece = self.get_prism(*args)
            piece.next_to(cube, np.array(vect), buff = 0)
            pieces.add(piece)
            if sum(vect) == 1:
                piece.type = "face"
            elif sum(vect) == 2:
                piece.type = "bar"
            else:
                piece.type = "corner_cube"

        return pieces

    def organize_faces(self, faces):
        self.unpose_3d_mobject(faces)
        for face in faces:
            dimensions = [
                face.length_over_dim(dim)
                for dim in range(3)
            ]
            thin_dim = np.argmin(dimensions)
            if thin_dim == 0:
                face.rotate(np.pi/2, DOWN)
            elif thin_dim == 1:
                face.rotate(np.pi/2, RIGHT)
        faces.arrange(OUT, buff = LARGE_BUFF)
        self.pose_3d_mobject(faces)
        return faces

    def organize_bars(self, bars):
        self.unpose_3d_mobject(bars)
        for bar in bars:
            dimensions = [
                bar.length_over_dim(dim)
                for dim in range(3)
            ]
            thick_dim = np.argmax(dimensions)
            if thick_dim == 0:
                bar.rotate(np.pi/2, OUT)
            elif thick_dim == 2:
                bar.rotate(np.pi/2, LEFT)
        bars.arrange(OUT, buff = LARGE_BUFF)
        self.pose_3d_mobject(bars)
        return bars

    def get_corner_cube(self):
        return self.get_prism(self.dx, self.dx,  self.dx)

    def get_prism(self, width, height, depth):
        color_kwargs = {
            "fill_color" : YELLOW,
            "fill_opacity" : 0.4,
            "stroke_color" : WHITE,            
            "stroke_width" : 0.1,
        }
        front = Rectangle(
            width = width,
            height = height,
            **color_kwargs
        )
        face = VGroup(front)
        for vect in LEFT, RIGHT, UP, DOWN:
            if vect is LEFT or vect is RIGHT:
                side = Rectangle(
                    height = height, 
                    width = depth, 
                    **color_kwargs
                )
            else:
                side = Rectangle(
                    height = depth,
                    width = width, 
                    **color_kwargs
                )
            side.next_to(front, vect, buff = 0)
            side.rotate(
                np.pi/2, rotate_vector(vect, -np.pi/2),
                about_point = front.get_edge_center(vect)
            )
            face.add(side)
        return face

    def pose_3d_mobject(self, mobject):
        mobject.rotate_in_place(self.pose_angle, self.pose_axis)
        return mobject

    def unpose_3d_mobject(self, mobject):
        mobject.rotate_in_place(-self.pose_angle, self.pose_axis)
        return mobject

class ShowCubeDVIn3D(Scene):
    def construct(self):
        raise Exception("This scene is only here for the stage_scenes script.")

class GraphOfXCubed(GraphScene):
    CONFIG = {
        "x_min" : -6,
        "x_max" : 6,
        "x_axis_width" : FRAME_WIDTH,
        "x_labeled_nums" : list(range(-6, 7)),
        "y_min" : -35,
        "y_max" : 35,
        "y_axis_height" : FRAME_HEIGHT,
        "y_tick_frequency" : 5,
        "y_labeled_nums" : list(range(-30, 40, 10)),
        "graph_origin" : ORIGIN,
        "dx" : 0.2,
        "deriv_x_min" : -3,
        "deriv_x_max" : 3,
    }
    def construct(self):
        self.setup_axes(animate = False)
        graph = self.get_graph(lambda x : x**3)
        label = self.get_graph_label(
            graph, "f(x) = x^3",
            direction = LEFT,
        )


        deriv_graph, full_deriv_graph = [
            self.get_derivative_graph(
                graph,
                color = DERIVATIVE_COLOR,
                x_min = low_x,
                x_max = high_x,
            )
            for low_x, high_x in [
                (self.deriv_x_min, self.deriv_x_max),
                (self.x_min, self.x_max),
            ]
        ]
        deriv_label = self.get_graph_label(
            deriv_graph,
            "\\frac{df}{dx}(x) = 3x^2",
            x_val = -3, 
            direction = LEFT
        )
        deriv_label.shift(0.5*DOWN)

        ss_group = self.get_secant_slope_group(
            self.deriv_x_min, graph, 
            dx = self.dx,
            dx_line_color = WHITE,
            df_line_color = WHITE,
            secant_line_color = YELLOW,
        )

        self.play(ShowCreation(graph))
        self.play(Write(label, run_time = 1))
        self.wait()
        self.play(Write(deriv_label, run_time = 1))
        self.play(ShowCreation(ss_group, lag_ratio = 0))
        self.animate_secant_slope_group_change(
            ss_group,
            target_x = self.deriv_x_max,
            run_time = 10,
            added_anims = [
                ShowCreation(deriv_graph, run_time = 10)
            ]
        )
        self.play(FadeIn(full_deriv_graph))
        self.wait()
        for x_val in -2, -self.dx/2, 2:
            self.animate_secant_slope_group_change(
                ss_group,
                target_x = x_val,
                run_time = 2
            )
            if x_val != -self.dx/2:
                v_line = self.get_vertical_line_to_graph(
                    x_val, deriv_graph,
                    line_class = DashedLine
                )
                self.play(ShowCreation(v_line))
                self.play(FadeOut(v_line))

class PatternForPowerRule(PiCreatureScene):
    CONFIG = {
        "num_exponents" : 5,
    }
    def construct(self):
        self.introduce_pattern()
        self.generalize_pattern()
        self.show_hopping()

    def introduce_pattern(self):
        exp_range = list(range(1, 1+self.num_exponents))
        colors = color_gradient([BLUE_D, YELLOW], self.num_exponents)
        derivatives = VGroup()
        for exponent, color in zip(exp_range, colors):
            derivative = TexMobject(
                "\\frac{d(x^%d)}{dx} = "%exponent,
                "%d x^{%d}"%(exponent, exponent-1)
            )
            VGroup(*derivative[0][2:4]).set_color(color)
            derivatives.add(derivative)
        derivatives.arrange(
            DOWN, aligned_edge = LEFT,
            buff = MED_LARGE_BUFF
        )
        derivatives.set_height(FRAME_HEIGHT-1)
        derivatives.to_edge(LEFT)

        self.play(FadeIn(derivatives[0]))
        for d1, d2 in zip(derivatives, derivatives[1:]):
            self.play(Transform(
                d1.copy(), d2,
                replace_mobject_with_target_in_scene = True  
            ))
        self.change_mode("thinking")
        self.wait()
        for derivative in derivatives[-2:]:
            derivative.save_state()
            self.play(
                derivative.scale, 2,
                derivative.next_to, derivative,
                RIGHT, SMALL_BUFF, DOWN,
            )
            self.wait(2)
            self.play(derivative.restore)
            self.remove(derivative)
            derivative.restore()
            self.add(derivative)

        self.derivatives = derivatives
        self.colors = colors

    def generalize_pattern(self):
        derivatives = self.derivatives


        power_rule = TexMobject(
            "\\frac{d (x^n)}{dx} = ",
            "nx^{n-1}"
        )
        title = TextMobject("``Power rule''")        
        title.next_to(power_rule, UP, MED_LARGE_BUFF)
        lines = VGroup(*[
            Line(
                deriv.get_right(), power_rule.get_left(),
                buff = MED_SMALL_BUFF,
                color = deriv[0][2].get_color()
            )
            for deriv in derivatives
        ])

        self.play(
            Transform(
                VGroup(*[d[0].copy() for d in derivatives]),
                VGroup(power_rule[0]),
                replace_mobject_with_target_in_scene = True
            ),
            ShowCreation(lines),
            lag_ratio = 0.5,
            run_time = 2,
        )
        self.wait()
        self.play(Write(power_rule[1]))
        self.wait()
        self.play(
            Write(title),
            self.pi_creature.change_mode, "speaking"
        )
        self.wait()

    def show_hopping(self):
        exp_range = list(range(2, 2+self.num_exponents-1))
        self.change_mode("tired")
        for exp, color in zip(exp_range, self.colors[1:]):
            form = TexMobject(
                "x^",
                str(exp),
                "\\rightarrow",
                str(exp),
                "x^",
                str(exp-1)
            )
            form.set_color(color)
            form.to_corner(UP+RIGHT, buff = LARGE_BUFF)
            lhs = VGroup(*form[:2])
            lhs_copy = lhs.copy()
            rhs = VGroup(*form[-2:])
            arrow = form[2]

            self.play(Write(lhs))
            self.play(
                lhs_copy.move_to, rhs, DOWN+LEFT,
                Write(arrow)
            )
            self.wait()
            self.play(
                ApplyMethod(
                    lhs_copy[1].replace, form[3],
                    path_arc = np.pi,
                    rate_func = running_start,
                ),
                FadeIn(
                    form[5],
                    rate_func = squish_rate_func(smooth, 0.5, 1)
                )   
            )
            self.wait()
            self.play(
                self.pi_creature.change_mode, "hesitant",
                self.pi_creature.look_at, lhs_copy
            )
            self.play(*list(map(FadeOut, [form, lhs_copy])))

class PowerRuleAlgebra(Scene):
    CONFIG = {
        "dx_color" : YELLOW,
        "x_color" : BLUE,
    }
    def construct(self):
        x_to_n = TexMobject("x^n")
        down_arrow = Arrow(UP, DOWN, buff = MED_LARGE_BUFF)
        paren_strings = ["(", "x", "+", "dx", ")"]
        x_dx_to_n = TexMobject(*paren_strings +["^n"])
        equals = TexMobject("=")
        equals2 = TexMobject("=")
        full_product = TexMobject(
            *paren_strings*3+["\\cdots"]+paren_strings
        )

        x_to_n.set_color(self.x_color)
        for mob in x_dx_to_n, full_product:
            mob.set_color_by_tex("dx", self.dx_color)
            mob.set_color_by_tex("x", self.x_color)

        nudge_group = VGroup(x_to_n, down_arrow, x_dx_to_n)
        nudge_group.arrange(DOWN)
        nudge_group.to_corner(UP+LEFT)
        down_arrow.next_to(x_to_n[0], DOWN)
        equals.next_to(x_dx_to_n)
        full_product.next_to(equals)
        equals2.next_to(equals, DOWN, 1.5*LARGE_BUFF)

        nudge_brace = Brace(x_dx_to_n, DOWN)
        nudged_output = nudge_brace.get_text("Nudged \\\\ output")
        product_brace = Brace(full_product, UP)
        product_brace.add(product_brace.get_text("$n$ times"))

        self.add(x_to_n)
        self.play(ShowCreation(down_arrow))
        self.play(
            FadeIn(x_dx_to_n),
            GrowFromCenter(nudge_brace),
            GrowFromCenter(nudged_output)
        )
        self.wait()
        self.play(
            Write(VGroup(equals, full_product)),
            GrowFromCenter(
                product_brace,
                rate_func = squish_rate_func(smooth, 0.6, 1)
            ),
            run_time = 3
        )
        self.wait()
        self.workout_product(equals2, full_product)

    def workout_product(self, equals, full_product):
        product_part_tex_pairs = list(zip(full_product, full_product.expression_parts))
        xs, dxs = [
            VGroup(*[
                submob
                for submob, tex in product_part_tex_pairs
                if tex == target_tex
            ])
            for target_tex in ("x", "dx")
        ]

        x_to_n = TexMobject("x^n")
        extra_stuff = TexMobject("+(\\text{Multiple of }\\, dx^2)")
        # extra_stuff.scale(0.8)
        VGroup(*extra_stuff[-4:-2]).set_color(self.dx_color)

        x_to_n.next_to(equals, RIGHT, align_using_submobjects = True)
        x_to_n.set_color(self.x_color)

        xs_copy = xs.copy()
        full_product.save_state()
        self.play(full_product.set_color, WHITE)
        self.play(xs_copy.set_color, self.x_color)
        self.play(
            Write(equals),
            Transform(xs_copy, x_to_n)
        )
        self.wait()
        brace, derivative_term = self.pull_out_linear_terms(
            x_to_n, product_part_tex_pairs, xs, dxs
        )
        self.wait()

        circle = Circle(color = DERIVATIVE_COLOR)
        circle.replace(derivative_term, stretch = True)
        circle.scale_in_place(1.4)
        circle.rotate_in_place(
            Line(
                derivative_term.get_corner(DOWN+LEFT),
                derivative_term.get_corner(UP+RIGHT),
            ).get_angle()
        )

        extra_stuff.next_to(brace, aligned_edge = UP)

        self.play(Write(extra_stuff), full_product.restore)
        self.wait()
        self.play(ShowCreation(circle))
        self.wait()

    def pull_out_linear_terms(self, x_to_n, product_part_tex_pairs, xs, dxs):
        last_group = None
        all_linear_terms = VGroup()
        for dx_index, dx in enumerate(dxs):
            if dx is dxs[-1]:
                v_dots = TexMobject("\\vdots")
                v_dots.next_to(last_group[0], DOWN)
                h_dots_list = [
                    submob
                    for submob, tex in product_part_tex_pairs
                    if tex == "\\cdots"
                ]
                h_dots_copy = h_dots_list[0].copy()
                self.play(ReplacementTransform(
                    h_dots_copy, v_dots,
                ))
                last_group.add(v_dots)
                all_linear_terms.add(v_dots)

            dx_copy = dx.copy()
            xs_copy = xs.copy()
            xs_copy.remove(xs_copy[dx_index])
            self.play(
                dx_copy.set_color, self.dx_color,
                xs_copy.set_color, self.x_color,
                rate_func = squish_rate_func(smooth, 0, 0.5)
            )

            dx_copy.generate_target()
            xs_copy.generate_target()
            target_list = [dx_copy.target] + list(xs_copy.target)
            target_list.sort(
                key=lambda m: m.get_center()[0]
            )
            dots = TexMobject("+", ".", ".", "\\dots")
            for dot_index, dot in enumerate(dots):
                target_list.insert(2*dot_index, dot)
            group = VGroup(*target_list)
            group.arrange(RIGHT, SMALL_BUFF)
            if last_group is None:
                group.next_to(x_to_n, RIGHT)
            else:
                group.next_to(last_group, DOWN, aligned_edge = LEFT)
            last_group = group

            self.play(
                MoveToTarget(dx_copy),
                MoveToTarget(xs_copy),
                Write(dots)
            )
            all_linear_terms.add(dx_copy, xs_copy, dots)

        all_linear_terms.generate_target()
        all_linear_terms.target.scale(0.7)
        brace = Brace(all_linear_terms.target, UP)
        compact = TexMobject("+\\,", "n", "x^{n-1}", "\\,dx")
        compact.set_color_by_tex("x^{n-1}", self.x_color)
        compact.set_color_by_tex("\\,dx", self.dx_color)
        compact.next_to(brace, UP)
        brace.add(compact)
        derivative_term = VGroup(*compact[1:3])

        VGroup(brace, all_linear_terms.target).shift(
            x_to_n[0].get_right()+MED_LARGE_BUFF*RIGHT - \
            compact[0].get_left()
        )

        self.play(MoveToTarget(all_linear_terms))
        self.play(Write(brace, run_time = 1))
        return brace, derivative_term

class ReactToFullExpansion(Scene):
    def construct(self):
        randy = Randolph()
        self.add(randy)

        self.play(randy.change_mode, "pleading")
        self.play(Blink(randy))
        self.play(randy.change_mode, "angry")
        self.wait()
        self.play(randy.change_mode, "thinking")
        self.play(Blink(randy))
        self.wait()

class OneOverX(PiCreatureScene, GraphScene):
    CONFIG = {
        "unit_length" : 3.0,    
        "graph_origin" : (FRAME_X_RADIUS - LARGE_BUFF)*LEFT + 2*DOWN,
        "rectangle_color_kwargs" : {
            "fill_color" : BLUE,
            "fill_opacity" : 0.5,
            "stroke_width" : 1,
            "stroke_color" : WHITE,
        },

        "x_axis_label" : "",
        "y_axis_label" : "",
        "x_min" : 0,
        "y_min" : 0,
        "x_tick_frequency" : 0.5,
        "y_tick_frequency" : 0.5,
        "x_labeled_nums" : list(range(0, 4)),
        "y_labeled_nums" : [1],
        "y_axis_height" : 10,
        "morty_scale_val" : 0.8,
        "area_label_scale_factor" : 0.75,
        "dx" : 0.1,
        "start_x_value" : 1.3,
        "dx_color" : GREEN,
        "df_color" : RED,
    }
    def setup(self):
        for c in self.__class__.__bases__:
            c.setup(self)
        self.x_max = self.x_axis_width/self.unit_length
        self.y_max = self.y_axis_height/self.unit_length

    def construct(self):
        self.force_skipping()

        self.introduce_function()
        self.introduce_puddle()
        self.introduce_graph()
        self.perform_nudge()

    def introduce_function(self):
        func = TexMobject("f(x) = ", "\\frac{1}{x}")
        func.to_edge(UP)
        recip_copy = func[1].copy()
        x_to_neg_one = TexMobject("x^{-1}")
        x_to_neg_one.submobjects.reverse()
        neg_one = VGroup(*x_to_neg_one[:2])
        neg_two = TexMobject("-2")

        self.play(
            Write(func),
            self.pi_creature.change_mode, "pondering"
        )
        self.wait()
        self.play(
            recip_copy.next_to, self.pi_creature, UP+LEFT,
            self.pi_creature.change_mode, "raise_right_hand"
        )
        x_to_neg_one.move_to(recip_copy)
        neg_two.replace(neg_one)
        self.play(ReplacementTransform(recip_copy, x_to_neg_one))
        self.wait()
        self.play(
            neg_one.scale, 1.5,
            neg_one.next_to, x_to_neg_one, LEFT, SMALL_BUFF, DOWN,
            rate_func = running_start,
            path_arc = np.pi
        )
        self.play(FadeIn(neg_two))
        self.wait()
        self.say(
            "More geometry!",
            target_mode = "hooray",
            added_anims = [
                FadeOut(x_to_neg_one),
                FadeOut(neg_two),
            ],
            run_time = 2
        )
        self.wait()
        self.play(RemovePiCreatureBubble(self.pi_creature))

    def introduce_puddle(self):
        rect_group = self.get_rectangle_group(self.start_x_value)

        self.play(
            DrawBorderThenFill(rect_group.rectangle),
            Write(rect_group.area_label),
            self.pi_creature.change_mode, "thinking"
        )
        self.play(
            GrowFromCenter(rect_group.x_brace),
            Write(rect_group.x_label),
        )
        self.wait()
        self.play(
            GrowFromCenter(rect_group.recip_brace),
            Write(rect_group.recip_label),
        )
        self.setup_axes(animate = True)
        self.wait()

        for d in 2, 3:
            self.change_rectangle_group(
                rect_group, d,
                target_group_kwargs = {
                    "x_label" : str(d),
                    "one_over_x_label" : "\\frac{1}{%d}"%d,
                },
                run_time = 2
            )
            self.wait()
        self.change_rectangle_group(rect_group, 3)
        self.wait()

        self.rect_group = rect_group

    def introduce_graph(self):
        rect_group = self.rect_group
        graph = self.get_graph(lambda x : 1./x)
        graph.points = np.array(list(reversed(graph.points)))

        self.change_rectangle_group(
            rect_group, 0.01,
            added_anims = [
                ShowCreation(graph)
            ],
            run_time = 5,
        )
        self.change_mode("happy")
        self.change_rectangle_group(rect_group, self.start_x_value)
        self.wait()

        self.graph = graph

    def perform_nudge(self):
        rect_group = self.rect_group
        graph = self.graph

        rect_copy = rect_group.rectangle.copy()
        rect_copy.set_fill(opacity = 0)
        new_rect = self.get_rectangle(
            self.start_x_value + self.dx
        )

        recip_brace = rect_group.recip_brace
        recip_brace.generate_target()
        recip_brace.target.next_to(
            new_rect, RIGHT, 
            buff = SMALL_BUFF,
            aligned_edge = DOWN,
        )
        recip_label = rect_group.recip_label
        recip_label.generate_target()
        recip_label.target.next_to(recip_brace.target, RIGHT)

        h_lines = VGroup(*[
            DashedLine(
                ORIGIN, (rect_copy.get_width()+LARGE_BUFF)*RIGHT, 
                color = self.df_color,
                stroke_width = 2
            ).move_to(rect.get_corner(UP+LEFT), LEFT)
            for rect in (rect_group.rectangle, new_rect)
        ])

        v_lines = VGroup(*[
            DashedLine(
                ORIGIN, (rect_copy.get_height()+MED_LARGE_BUFF)*UP,
                color = self.dx_color,
                stroke_width = 2
            ).move_to(rect.get_corner(DOWN+RIGHT), DOWN)
            for rect in (rect_group.rectangle, new_rect)
        ])

        dx_brace = Brace(v_lines, UP, buff = 0)
        dx_label = dx_brace.get_text("$dx$")
        dx_brace.add(dx_label)

        df_brace = Brace(h_lines, RIGHT, buff = 0)
        df_label = df_brace.get_text("$d\\left(\\frac{1}{x}\\right)$")
        df_brace.add(df_label)

        negative = TextMobject("Negative")
        negative.set_color(RED)
        negative.next_to(df_label, UP+RIGHT)
        negative.shift(RIGHT)
        negative_arrow = Arrow(
            negative.get_left(),
            df_label.get_corner(UP+RIGHT),
            color = RED
        )

        area_changes = VGroup()
        point_pairs = [
            (new_rect.get_corner(UP+RIGHT), rect_copy.get_corner(DOWN+RIGHT)),
            (new_rect.get_corner(UP+LEFT), rect_copy.get_corner(UP+RIGHT))
        ]
        for color, point_pair in zip([self.dx_color, self.df_color], point_pairs):
            area_change_rect = Rectangle(
                fill_opacity = 1,
                fill_color = color,
                stroke_width = 0
            )
            area_change_rect.replace(
                VGroup(*list(map(VectorizedPoint, point_pair))),
                stretch = True
            )
            area_changes.add(area_change_rect)
        area_gained, area_lost = area_changes

        area_gained_label = TextMobject("Area gained")
        area_gained_label.scale(0.75)
        area_gained_label.next_to(
            rect_copy.get_corner(DOWN+RIGHT), 
            UP+LEFT, buff = SMALL_BUFF
        )
        area_gained_arrow = Arrow(
            area_gained_label.get_top(),
            area_gained.get_center(),
            buff = 0,
            color = WHITE
        )
        
        area_lost_label = TextMobject("Area lost")
        area_lost_label.scale(0.75)
        area_lost_label.next_to(rect_copy.get_left(), RIGHT)
        area_lost_arrow = Arrow(
            area_lost_label.get_top(),
            area_lost.get_center(),
            buff = 0,
            color = WHITE
        )

        question = TexMobject(
            "\\frac{d(1/x)}{dx} = ???"
        )
        question.next_to(
            self.pi_creature.get_corner(UP+LEFT), 
            UP, buff = MED_SMALL_BUFF,
        )

        self.play(
            FadeOut(rect_group.area_label),
            ReplacementTransform(rect_copy, new_rect),
            MoveToTarget(recip_brace),
            MoveToTarget(recip_label),
            self.pi_creature.change_mode, "pondering"
        )
        self.play(
            GrowFromCenter(dx_brace),
            *list(map(ShowCreation, v_lines))
        )
        self.wait()
        self.play(
            GrowFromCenter(df_brace),
            *list(map(ShowCreation, h_lines))
        )
        self.change_mode("confused")
        self.wait()

        self.play(
            FadeIn(area_gained),
            Write(area_gained_label, run_time = 2),
            ShowCreation(area_gained_arrow)
        )
        self.wait()
        self.play(
            FadeIn(area_lost),
            Write(area_lost_label, run_time = 2),
            ShowCreation(area_lost_arrow)
        )
        self.wait()
        self.revert_to_original_skipping_status()###
        self.play(
            Write(negative),
            ShowCreation(negative_arrow)
        )
        self.wait()
        self.play(
            Write(question),
            self.pi_creature.change_mode, "raise_right_hand"
        )
        self.wait(2)


    ########

    def create_pi_creature(self):
        morty = PiCreatureScene.create_pi_creature(self)
        morty.scale(
            self.morty_scale_val, 
            about_point = morty.get_corner(DOWN+RIGHT)
        )
        return morty

    def draw_graph(self):
        self.setup_axes()
        graph = self.get_graph(lambda x : 1./x)

        rect_group = self.get_rectangle_group(0.5)

        self.add(rect_group)
        self.wait()
        self.change_rectangle_group(
            rect_group, 2,
            target_group_kwargs = {
                "x_label" : "2",
                "one_over_x_label" : "\\frac{1}{2}",
            },
            added_anims = [ShowCreation(graph)]
        )
        self.wait()

    def get_rectangle_group(
        self, x, 
        x_label = "x", 
        one_over_x_label = "\\frac{1}{x}"
        ):
        result = VGroup()
        result.x_val = x
        result.rectangle = self.get_rectangle(x)

        result.x_brace, result.recip_brace = braces = [
            Brace(result.rectangle, vect)
            for vect in (UP, RIGHT)
        ]
        result.labels = VGroup()
        for brace, label in zip(braces, [x_label, one_over_x_label]):
            brace.get_text("$%s$"%label)
            result.labels.add(brace.get_text("$%s$"%label))
        result.x_label, result.recip_label = result.labels

        area_label = TextMobject("Area = 1")
        area_label.scale(self.area_label_scale_factor)
        max_width = max(result.rectangle.get_width()-2*SMALL_BUFF, 0)
        if area_label.get_width() > max_width:
            area_label.set_width(max_width)
        area_label.move_to(result.rectangle)
        result.area_label = area_label

        result.add(
            result.rectangle,
            result.x_brace,
            result.recip_brace,
            result.labels,
            result.area_label,
        )
        return result

    def get_rectangle(self, x):
        try:
            y = 1./x
        except ZeroDivisionError:
            y = 100

        rectangle = Rectangle(
            width = x*self.unit_length,
            height = y*self.unit_length,
            **self.rectangle_color_kwargs
        )
        rectangle.move_to(self.graph_origin, DOWN+LEFT)
        return rectangle

    def change_rectangle_group(
        self, 
        rect_group, target_x,
        target_group_kwargs = None,
        added_anims = [],
        **anim_kwargs
        ):
        target_group_kwargs = target_group_kwargs or {}
        if "run_time" not in anim_kwargs:
            anim_kwargs["run_time"] = 3

        target_group = self.get_rectangle_group(target_x, **target_group_kwargs)
        target_labels = target_group.labels
        labels_transform = Transform(
            rect_group.labels,
            target_group.labels
        )

        start_x = float(rect_group.x_val)
        def update_rect_group(group, alpha):
            x = interpolate(start_x, target_x, alpha)
            new_group = self.get_rectangle_group(x, **target_group_kwargs)
            Transform(group, new_group).update(1)
            labels_transform.update(alpha)
            for l1, l2 in zip(rect_group.labels, new_group.labels):
                l1.move_to(l2)
            return rect_group

        self.play(
            UpdateFromAlphaFunc(rect_group, update_rect_group),
            *added_anims,
            **anim_kwargs
        )
        rect_group.x_val = target_x

class AskRecipriocalQuestion(Scene):
    def construct(self):
        tex = TexMobject(
            "(\\text{What number?})",  
            "\\cdot x = 1"
        )
        arrow = Arrow(DOWN+LEFT, UP+RIGHT)
        arrow.move_to(tex[0].get_top(), DOWN+LEFT)
        self.play(Write(tex))
        self.play(ShowCreation(arrow))
        self.wait()

class SquareRootOfX(Scene):
    CONFIG = {
        "square_color_kwargs" : {
            "stroke_color" : WHITE,
            "stroke_width" : 1,
            "fill_color" : BLUE_E,
            "fill_opacity" : 1,
        },
        "bigger_square_color_kwargs" : {
            "stroke_color" : WHITE,
            "stroke_width" : 1,
            "fill_color" : YELLOW,
            "fill_opacity" : 0.7,
        },
        "square_corner" : 6*LEFT+3*UP,
        "square_width" : 3,
        "d_sqrt_x" : 0.3,
    }
    def construct(self):
        self.add_title()
        self.introduce_square()
        self.nudge_square()

    def add_title(self):
        title = TexMobject("f(x) = \\sqrt{x}")
        title.next_to(ORIGIN, RIGHT)
        title.to_edge(UP)
        self.add(title)

    def introduce_square(self):
        square = Square(
            side_length = self.square_width,
            **self.square_color_kwargs
        )
        square.move_to(self.square_corner, UP+LEFT)
        area_label = TextMobject("Area $ = x$")
        area_label.move_to(square)

        bottom_brace, right_brace = braces = VGroup(*[
            Brace(square, vect)
            for vect in (DOWN, RIGHT)
        ])
        for brace in braces:
            brace.add(brace.get_text("$\\sqrt{x}$"))


        self.play(
            DrawBorderThenFill(square),
            Write(area_label)
        )
        self.play(*list(map(FadeIn, braces)))
        self.wait()

        self.square = square
        self.area_label = area_label
        self.braces = braces

    def nudge_square(self):
        square = self.square
        area_label = self.area_label
        bottom_brace, right_brace = self.braces

        bigger_square = Square(
            side_length = self.square_width + self.d_sqrt_x,
            **self.bigger_square_color_kwargs
        )
        bigger_square.move_to(self.square_corner, UP+LEFT)

        square_copy = square.copy()

        lines = VGroup(*[
            DashedLine(
                ORIGIN,
                (self.square_width + MED_LARGE_BUFF)*vect,
                color = WHITE,
                stroke_width = 3
            ).shift(s.get_corner(corner))
            for corner, vect in [(DOWN+LEFT, RIGHT), (UP+RIGHT, DOWN)]
            for s in [square, bigger_square]
        ])
        little_braces = VGroup(*[
            Brace(VGroup(*line_pair), vect, buff = 0)
            for line_pair, vect in [(lines[:2], RIGHT), (lines[2:], DOWN)]
        ])
        for brace in little_braces:
            tex = brace.get_text("$d\\sqrt{x}$", buff = SMALL_BUFF)
            tex.scale_in_place(0.8)
            brace.add(tex)

        area_increase = TextMobject("$dx$ = New area")
        area_increase.set_color(bigger_square.get_color())
        area_increase.next_to(square, RIGHT, 4)

        question = TexMobject("\\frac{d\\sqrt{x}}{dx} = ???")
        VGroup(*question[5:7]).set_color(bigger_square.get_color())
        question.next_to(
            area_increase, DOWN, 
            aligned_edge = LEFT, 
            buff = LARGE_BUFF
        )
        
        self.play(
            Transform(square_copy, bigger_square),
            Animation(square),
            Animation(area_label),
            bottom_brace.next_to, bigger_square, DOWN, SMALL_BUFF, LEFT,
            right_brace.next_to, bigger_square, RIGHT, SMALL_BUFF, UP,
        )
        self.play(Write(area_increase))
        self.play(*it.chain(
            list(map(ShowCreation, lines)),
            list(map(FadeIn, little_braces))
        ))
        self.play(Write(question))
        self.wait()

class MentionSine(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("Let's tackle $\\sin(\\theta)$")
        self.change_student_modes("pondering", "hooray", "erm")
        self.wait(2)
        self.student_thinks("")
        self.zoom_in_on_thought_bubble()

class NameUnitCircle(Scene):
    def construct(self):
        words = TextMobject("Unit circle")
        words.scale(2)
        words.set_color(BLUE)
        self.play(Write(words))
        self.wait()

class DerivativeOfSineIsSlope(Scene):
    def construct(self):
        tex = TexMobject(
            "\\frac{d(\\sin(\\theta))}{d\\theta} = ",
            "\\text{Slope of this graph}"
        )
        tex.set_width(FRAME_WIDTH-1)
        tex.to_edge(DOWN)
        VGroup(*tex[0][2:8]).set_color(BLUE)
        VGroup(*tex[1][-9:]).set_color(BLUE)

        self.play(Write(tex, run_time = 2))
        self.wait()

class IntroduceUnitCircleWithSine(GraphScene):
    CONFIG = {
        "unit_length" : 2.5,
        "graph_origin" : ORIGIN,
        "x_axis_width" : 15,
        "y_axis_height" : 10,
        "x_min" : -3,
        "x_max" : 3,
        "y_min" : -2,
        "y_max" : 2,
        "x_labeled_nums" : [-2, -1, 1, 2],
        "y_labeled_nums" : [-1, 1],
        "x_tick_frequency" : 0.5,
        "y_tick_frequency" : 0.5,
        "circle_color" : BLUE,
        "example_radians" : 0.8,
        "rotations_per_second" : 0.25,
        "include_radial_line_dot" : True,
        "remove_angle_label" : True,
        "line_class" : DashedLine,
        "theta_label" : "= 0.8",
    }
    def construct(self):
        self.setup_axes()
        self.add_title()
        self.introduce_unit_circle()
        self.draw_example_radians()
        self.label_sine()
        self.walk_around_circle()

    def add_title(self):
        title = TexMobject("f(\\theta) = \\sin(\\theta)")
        title.to_corner(UP+LEFT)
        self.add(title)
        self.title = title

    def introduce_unit_circle(self):
        circle = self.get_unit_circle()
        radial_line = Line(ORIGIN, self.unit_length*RIGHT)
        radial_line.set_color(RED)
        if self.include_radial_line_dot:
            dot = Dot()
            dot.move_to(radial_line.get_end())
            radial_line.add(dot)

        self.play(ShowCreation(radial_line))
        self.play(
            ShowCreation(circle),            
            Rotate(radial_line, 2*np.pi),
            run_time = 2,
        )
        self.wait()

        self.circle = circle
        self.radial_line = radial_line

    def draw_example_radians(self):
        circle = self.circle
        radial_line = self.radial_line

        line = Line(
            ORIGIN, self.example_radians*self.unit_length*UP,
            color = YELLOW,
        )
        line.shift(FRAME_X_RADIUS*RIGHT/3).to_edge(UP)
        line.insert_n_curves(10)
        line.make_smooth()

        arc = Arc(
            self.example_radians, radius = self.unit_length,
            color = line.get_color(),
        )
        arc_copy = arc.copy().set_color(WHITE)

        brace = Brace(line, RIGHT)
        brace_text = brace.get_text("$\\theta%s$"%self.theta_label)
        brace_text.set_color(line.get_color())
        theta_copy = brace_text[0].copy()

        self.play(
            GrowFromCenter(line),
            GrowFromCenter(brace),
        )
        self.play(Write(brace_text))
        self.wait()
        self.play(
            line.move_to, radial_line.get_end(), DOWN,
            FadeOut(brace)
        )
        self.play(ReplacementTransform(line, arc))
        self.wait()
        self.play(
            Rotate(radial_line, self.example_radians),
            ShowCreation(arc_copy)
        )
        self.wait()
        arc_copy.generate_target()
        arc_copy.target.scale(0.2)
        theta_copy.generate_target()
        theta_copy.target.next_to(
            arc_copy.target, RIGHT,
            aligned_edge = DOWN,
            buff = SMALL_BUFF
        )
        theta_copy.target.shift(SMALL_BUFF*UP)
        self.play(*list(map(MoveToTarget, [arc_copy, theta_copy])))
        self.wait()

        self.angle_label = VGroup(arc_copy, theta_copy)
        self.example_theta_equation = brace_text

    def label_sine(self):
        radial_line = self.radial_line

        drop_point = radial_line.get_end()[0]*RIGHT
        v_line = self.line_class(radial_line.get_end(), drop_point)
        brace = Brace(v_line, RIGHT)
        brace_text = brace.get_text("$\\sin(\\theta)$")
        brace_text[-2].set_color(YELLOW)

        self.play(ShowCreation(v_line))
        self.play(
            GrowFromCenter(brace),
            Write(brace_text)
        )
        self.wait()
        faders = [brace, brace_text, self.example_theta_equation]
        if self.remove_angle_label:
            faders += self.angle_label
        self.play(*list(map(FadeOut, faders)))

        self.v_line = v_line

    def walk_around_circle(self):
        radial_line = self.radial_line
        v_line = self.v_line

        def v_line_update(v_line):
            drop_point = radial_line.get_end()[0]*RIGHT
            v_line.put_start_and_end_on(
                radial_line.get_end(), drop_point
            )
            return v_line
        filler_arc = self.circle.copy()
        filler_arc.set_color(YELLOW)
        curr_arc_portion = self.example_radians/(2*np.pi)
        filler_portion = 1 - curr_arc_portion
        filler_arc.pointwise_become_partial(filler_arc, curr_arc_portion, 1)

        self.play(
            Rotate(radial_line, filler_portion*2*np.pi),
            ShowCreation(filler_arc),
            UpdateFromFunc(v_line, v_line_update),
            run_time = filler_portion/self.rotations_per_second,
            rate_func=linear,
        )
        for x in range(5):
            self.play(
                Rotate(radial_line, 2*np.pi),
                UpdateFromFunc(v_line, v_line_update),
                run_time = 1./self.rotations_per_second,
                rate_func=linear,
            )

    ##############

    def setup_axes(self):
        GraphScene.setup_axes(self)
        VGroup(*self.x_axis.numbers[:2]).shift(MED_SMALL_BUFF*LEFT)
        VGroup(*self.x_axis.numbers[2:]).shift(SMALL_BUFF*RIGHT)
        self.y_axis.numbers[0].shift(MED_SMALL_BUFF*DOWN)
        self.y_axis.numbers[1].shift(MED_SMALL_BUFF*UP)

    def get_unit_circle(self):
        return Circle(
            radius = self.unit_length,
            color = self.circle_color,
        )

class DerivativeIntuitionFromSineGraph(GraphScene):
    CONFIG = {
        "graph_origin" : 6*LEFT,
        "x_axis_width" : 11,
        "x_min" : 0,
        "x_max" : 4*np.pi,
        "x_labeled_nums" : np.arange(0, 4*np.pi, np.pi),
        "x_tick_frequency" : np.pi/4,
        "x_axis_label" : "$\\theta$",
        "y_axis_height" : 6,
        "y_min" : -2,
        "y_max" : 2,
        "y_tick_frequency" : 0.5,
        "y_axis_label" : "",
    }
    def construct(self):
        self.setup_axes()
        self.draw_sine_graph()
        self.draw_derivative_from_slopes()
        self.alter_derivative_graph()

    def draw_sine_graph(self):
        graph = self.get_graph(np.sin)
        v_line = DashedLine(ORIGIN, UP)
        rps = IntroduceUnitCircleWithSine.CONFIG["rotations_per_second"]
        self.play(
            ShowCreation(graph),
            UpdateFromFunc(v_line, lambda v : self.v_line_update(v, graph)),
            run_time = 2./rps,
            rate_func=linear
        )
        self.wait()
        self.graph = graph

    def draw_derivative_from_slopes(self):
        ss_group = self.get_secant_slope_group(
            0, self.graph,
            dx = 0.01,
            secant_line_color = RED,
        )
        deriv_graph = self.get_graph(np.cos, color = DERIVATIVE_COLOR)
        v_line = DashedLine(
            self.graph_origin, self.coords_to_point(0, 1), 
            color = RED
        )

        self.play(ShowCreation(ss_group, lag_ratio = 0))
        self.play(ShowCreation(v_line))
        self.wait()
        last_theta = 0
        next_theta = np.pi/2
        while last_theta < self.x_max:
            deriv_copy = deriv_graph.copy()
            self.animate_secant_slope_group_change(
                ss_group,
                target_x = next_theta,
                added_anims = [
                    ShowCreation(
                        deriv_copy,
                        rate_func = lambda t : interpolate(
                            last_theta/self.x_max, 
                            next_theta/self.x_max,
                            smooth(t)
                        ),
                        run_time = 3,
                    ),
                    UpdateFromFunc(
                        v_line, 
                        lambda v : self.v_line_update(v, deriv_copy),
                        run_time = 3
                    ),
                ]
            )
            self.wait()
            if next_theta == 2*np.pi:
                words = TextMobject("Looks a lot like $\\cos(\\theta)$")
                words.next_to(self.graph_origin, RIGHT)
                words.to_edge(UP)
                arrow = Arrow(
                    words.get_bottom(), 
                    deriv_graph.point_from_proportion(0.45)
                )
                VGroup(words, arrow).set_color(deriv_graph.get_color())
                self.play(
                    Write(words),
                    ShowCreation(arrow)
                )
            self.remove(deriv_copy)
            last_theta = next_theta
            next_theta += np.pi/2
        self.add(deriv_copy)

        self.deriv_graph = deriv_copy

    def alter_derivative_graph(self):
        func_list = [
            lambda x : 0.5*(np.cos(x)**3 + np.cos(x)),
            lambda x : 0.75*(np.sign(np.cos(x))*np.cos(x)**2 + np.cos(x)),
            lambda x : 2*np.cos(x),
            lambda x : np.cos(x),
        ]
        for func in func_list:
            new_graph = self.get_graph(func, color = DERIVATIVE_COLOR)
            self.play(
                Transform(self.deriv_graph, new_graph),
                run_time = 2
            )
            self.wait()

    ######

    def v_line_update(self, v_line, graph):
        point = graph.point_from_proportion(1)
        drop_point = point[0]*RIGHT
        v_line.put_start_and_end_on(drop_point, point)
        return v_line

    def setup_axes(self):
        GraphScene.setup_axes(self)
        self.x_axis.remove(self.x_axis.numbers)
        self.remove(self.x_axis.numbers)
        for x in range(1, 4):
            if x == 1:
                label = TexMobject("\\pi")
            else:
                label = TexMobject("%d\\pi"%x)
            label.next_to(self.coords_to_point(x*np.pi, 0), DOWN, MED_LARGE_BUFF)
            self.add(label)
        self.x_axis_label_mob.set_color(YELLOW)

class LookToFunctionsMeaning(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            Look to the function's
            actual meaning
        """)
        self.change_student_modes(*["pondering"]*3)
        self.wait(3)

class DerivativeFromZoomingInOnSine(IntroduceUnitCircleWithSine, ZoomedScene):
    CONFIG = {
        "zoom_factor" : 10,
        "zoomed_canvas_frame_shape" : (3, 4.5),
        "include_radial_line_dot" : False,
        "remove_angle_label" : False,
        "theta_label" : "",
        "line_class" : Line,
        "example_radians" : 1.0,
        "zoomed_canvas_corner_buff" : SMALL_BUFF,
        "d_theta" : 0.05,
    }
    def construct(self):
        self.setup_axes()
        self.add_title()
        self.introduce_unit_circle()
        self.draw_example_radians()
        self.label_sine()

        self.zoom_in()
        self.perform_nudge()
        self.show_similar_triangles()
        self.analyze_ratios()

    def zoom_in(self):
        self.activate_zooming()
        self.little_rectangle.next_to(self.radial_line.get_end(), UP, LARGE_BUFF)
        self.play(*list(map(FadeIn, [
            self.little_rectangle, self.big_rectangle
        ])))
        self.play(
            self.little_rectangle.move_to, 
            self.radial_line.get_end(), DOWN+RIGHT,
            self.little_rectangle.shift, 
            SMALL_BUFF*(DOWN+RIGHT)
        )
        self.wait()

    def perform_nudge(self):
        d_theta_arc = Arc(
            start_angle = self.example_radians,
            angle = self.d_theta,
            radius = self.unit_length,
            color = MAROON_B,
            stroke_width = 6
        )
        d_theta_arc.scale(self.zoom_factor)
        d_theta_brace = Brace(
            d_theta_arc,
            rotate_vector(RIGHT, self.example_radians)
        )
        d_theta_label = TexMobject("d\\theta")
        d_theta_label.next_to(
            d_theta_brace.get_center(), d_theta_brace.direction, 
            MED_LARGE_BUFF
        )
        d_theta_label.set_color(d_theta_arc.get_color())

        group = VGroup(d_theta_arc, d_theta_brace, d_theta_label)
        group.scale(1./self.zoom_factor)

        point = self.radial_line.get_end()
        nudged_point = d_theta_arc.point_from_proportion(1)
        interim_point = nudged_point[0]*RIGHT+point[1]*UP
        h_line = DashedLine(
            interim_point, point, 
            dash_length = 0.01
        )
        d_sine_line = Line(interim_point, nudged_point, color = DERIVATIVE_COLOR)
        d_sine_brace = Brace(Line(ORIGIN, UP), LEFT)
        d_sine_brace.set_height(d_sine_line.get_height())
        d_sine_brace.next_to(d_sine_line, LEFT, buff = SMALL_BUFF/self.zoom_factor)
        d_sine = TexMobject("d(\\sin(\\theta))")
        d_sine.set_color(d_sine_line.get_color())
        d_sine.set_width(1.5*self.d_theta*self.unit_length)
        d_sine.next_to(d_sine_brace, LEFT, SMALL_BUFF/self.zoom_factor)

        self.play(ShowCreation(d_theta_arc))
        self.play(
            GrowFromCenter(d_theta_brace),
            FadeIn(d_theta_label)
        )
        self.wait()
        self.play(
            ShowCreation(h_line),
            ShowCreation(d_sine_line)
        )
        self.play(
            GrowFromCenter(d_sine_brace),
            Write(d_sine)
        )
        self.wait()

        self.little_triangle = Polygon(
            nudged_point, point, interim_point
        )
        self.d_theta_group = VGroup(d_theta_brace, d_theta_label)
        self.d_sine_group = VGroup(d_sine_brace, d_sine)

    def show_similar_triangles(self):
        little_triangle = self.little_triangle
        big_triangle = Polygon(
            self.graph_origin,
            self.radial_line.get_end(),
            self.radial_line.get_end()[0]*RIGHT,
        )
        for triangle in little_triangle, big_triangle:
            triangle.set_color(GREEN)
            triangle.set_fill(GREEN, opacity = 0.5)
        big_triangle_copy = big_triangle.copy()
        big_triangle_copy.next_to(ORIGIN, UP+LEFT)

        new_angle_label = self.angle_label.copy()
        new_angle_label.scale(
            little_triangle.get_width()/big_triangle.get_height()
        )
        new_angle_label.rotate(-np.pi/2)
        new_angle_label.shift(little_triangle.points[0])
        new_angle_label[1].rotate_in_place(np.pi/2)

        little_triangle_lines = VGroup(*[
            Line(*list(map(little_triangle.get_corner, pair)))
            for pair in [
                (DOWN+RIGHT, UP+LEFT),
                (UP+LEFT, DOWN+LEFT)
            ]
        ])
        little_triangle_lines.set_color(little_triangle.get_color())

        self.play(DrawBorderThenFill(little_triangle))
        self.play(
            little_triangle.scale, 2, little_triangle.get_corner(DOWN+RIGHT),
            little_triangle.set_color, YELLOW,
            rate_func = there_and_back
        )
        self.wait()
        groups = [self.d_theta_group, self.d_sine_group]
        for group, line in zip(groups, little_triangle_lines):
            self.play(ApplyMethod(
                line.rotate_in_place, np.pi/12,
                rate_func = wiggle,
                remover = True,
            ))
            self.play(
                group.scale, 1.2, group.get_corner(DOWN+RIGHT),
                group.set_color, YELLOW,
                rate_func = there_and_back,
            )
            self.wait()

        self.play(ReplacementTransform(
            little_triangle.copy().set_fill(opacity = 0), 
            big_triangle_copy,
            path_arc = np.pi/2,
            run_time = 2
        ))
        self.wait()
        self.play(
            ReplacementTransform(big_triangle_copy, big_triangle),
            Animation(self.angle_label)
        )
        self.wait()
        self.play(
            self.radial_line.rotate_in_place, np.pi/12,
            Animation(big_triangle),
            rate_func = wiggle,
        )
        self.wait()
        self.play(
            ReplacementTransform(
                big_triangle.copy().set_fill(opacity = 0), 
                little_triangle,
                path_arc = -np.pi/2,
                run_time = 3,
            ),
            ReplacementTransform(
                self.angle_label.copy(),
                new_angle_label,
                path_arc = -np.pi/2,
                run_time = 3,
            ),
        )
        self.play(
            new_angle_label.scale_in_place, 2,
            new_angle_label.set_color, RED,
            rate_func = there_and_back
        )
        self.wait()

    def analyze_ratios(self):
        d_ratio = TexMobject("\\frac{d(\\sin(\\theta))}{d\\theta} = ")
        VGroup(*d_ratio[:9]).set_color(GREEN)
        VGroup(*d_ratio[10:12]).set_color(MAROON_B)
        trig_ratio = TexMobject("\\frac{\\text{Adj.}}{\\text{Hyp.}}")
        VGroup(*trig_ratio[:4]).set_color(GREEN)
        VGroup(*trig_ratio[5:9]).set_color(MAROON_B)
        cos = TexMobject("= \\cos(\\theta)")
        cos.add_background_rectangle()

        group = VGroup(d_ratio, trig_ratio, cos)
        group.arrange()
        group.next_to(
            self.title, DOWN, 
            buff = MED_LARGE_BUFF, 
            aligned_edge = LEFT
        )

        for mob in group:
            self.play(Write(mob))
            self.wait()

class TryWithCos(Scene):
    def construct(self):
        words = TextMobject("What about $\\cos(\\theta)$?")
        words.set_color(YELLOW)
        self.play(Write(words))
        self.wait()

class NextVideo(TeacherStudentsScene):
    def construct(self):
        series = VideoSeries()
        next_video = series[3]
        series.to_edge(UP)

        d_sum = TexMobject("\\frac{d}{dx}(x^3 + x^2)")
        d_product = TexMobject("\\frac{d}{dx} \\sin(x)x^2")
        d_composition = TexMobject("\\frac{d}{dx} \\cos\\left(\\frac{1}{x}\\right)")

        group = VGroup(d_sum, d_product, d_composition)
        group.arrange(RIGHT, buff = 2*LARGE_BUFF)
        group.next_to(VGroup(*self.get_pi_creatures()), UP, buff = LARGE_BUFF)

        self.play(
            FadeIn(
                series,
                lag_ratio = 0.5,
                run_time = 3,
            ),
            *[
                ApplyMethod(pi.look_at, next_video)
                for pi in self.get_pi_creatures()
            ]
        )
        self.play(
            next_video.set_color, YELLOW,
            next_video.shift, MED_LARGE_BUFF*DOWN
        )
        self.wait()
        for mob in group:
            self.play(
                Write(mob, run_time = 1),
                *[
                    ApplyMethod(pi.look_at, mob)
                    for pi in self.get_pi_creatures()
                ]
            )
        self.wait(3)

class Chapter3PatreonThanks(PatreonThanks):
    CONFIG = {
        "specific_patrons" : [
            "Ali Yahya",
            "CrypticSwarm    ",
            "Yu  Jun",
            "Shelby  Doolittle",
            "Dave    Nicponski",
            "Damion  Kistler",
            "Juan    Benet",
            "Othman  Alikhan",
            "Markus  Persson",
            "Dan Buchoff",
            "Derek   Dai",
            "Joseph  John Cox",
            "Luc Ritchie",
            "Guido   Gambardella",
            "Jerry   Ling",
            "Mark    Govea",
            "Vecht   ",
            "Jonathan    Eppele",
            "Shimin Kuang",
            "Rish    Kundalia",
            "Achille Brighton",
            "Kirk    Werklund",
            "Ripta   Pasay",
            "Felipe  Diniz",
        ]
    }

class Promotion(PiCreatureScene):
    CONFIG = {
        "seconds_to_blink" : 5,
    }
    def construct(self):
        url = TextMobject("https://brilliant.org/3b1b/")
        url.to_corner(UP+LEFT)

        rect = Rectangle(height = 9, width = 16)
        rect.set_height(5.5)
        rect.next_to(url, DOWN)
        rect.to_edge(LEFT)

        self.play(
            Write(url),
            self.pi_creature.change, "raise_right_hand"
        )
        self.play(ShowCreation(rect))
        self.wait(2)
        self.change_mode("thinking")
        self.wait()
        self.look_at(url)
        self.wait(10)
        self.change_mode("happy")
        self.wait(10)
        self.change_mode("raise_right_hand")
        self.wait(10)

class Thumbnail(NudgeSideLengthOfCube):
    def construct(self):
        self.introduce_cube()
        VGroup(*self.get_mobjects()).to_edge(DOWN)

        formula = TexMobject(
            "\\frac{d(x^3)}{dx} = 3x^2"
        )
        VGroup(*formula[:5]).set_color(YELLOW)
        VGroup(*formula[-3:]).set_color(GREEN_B)
        formula.set_width(FRAME_X_RADIUS-1)
        formula.to_edge(RIGHT)
        self.add(formula)

        title = TextMobject("Geometric derivatives")
        title.set_width(FRAME_WIDTH-1)
        title.to_edge(UP)
        self.add(title)



















