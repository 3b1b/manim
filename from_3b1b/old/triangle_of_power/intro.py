from manimlib.imports import *


class TrigAnimation(Animation):
    CONFIG = {
        "rate_func" : None,
        "run_time"  : 5,
        "sin_color" : BLUE,
        "cos_color" : RED,
        "tan_color" : GREEN
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        x_axis = NumberLine(
            x_min = -3, 
            x_max = 3,
            color = BLUE_E
        )
        y_axis = x_axis.copy().rotate(np.pi/2)
        circle = Circle(color = WHITE)
        self.trig_lines = [
            Line(ORIGIN, RIGHT, color = color)
            for color in (self.sin_color, self.cos_color, self.tan_color)
        ]
        mobject = VMobject(
            x_axis, y_axis, circle, 
            *self.trig_lines
        )
        mobject.to_edge(RIGHT)
        self.center = mobject.get_center()
        Animation.__init__(self, mobject, **kwargs)

    def interpolate_mobject(self, alpha):
        theta = 2*np.pi*alpha
        circle_point = np.cos(theta)*RIGHT+np.sin(theta)*UP+self.center
        points = [
            circle_point[0]*RIGHT,
            circle_point[1]*UP+self.center,
            (
                np.sign(np.cos(theta))*np.sqrt(
                    np.tan(theta)**2 - np.sin(theta)**2
                ) + np.cos(theta)
            )*RIGHT + self.center,
        ]
        for line, point in zip(self.trig_lines, points):
            line.set_points_as_corners([circle_point, point])



class Notation(Scene):
    def construct(self):
        self.introduce_notation()
        self.shift_to_good_and_back()
        self.shift_to_visuals()
        self.swipe_left()


    def introduce_notation(self):
        notation = TextMobject("Notation")
        notation.to_edge(UP)

        self.sum1 = TexMobject("\\sum_{n=1}^\\infty \\dfrac{1}{n}")
        self.prod1 = TexMobject("\\prod_{p\\text{ prime}}\\left(1-p^{-s}\\right)")
        self.trigs1 = TexMobject([
            ["\\sin", "(x)"],
            ["\\cos", "(x)"],
            ["\\tan", "(x)"],
        ], next_to_direction = DOWN)
        self.func1 = TexMobject("f(x) = y")
        symbols = [self.sum1, self.prod1, self.trigs1, self.func1]
        for sym, vect in zip(symbols, compass_directions(4, UP+LEFT)):
            sym.scale(0.5)
            vect[0] *= 2
            sym.shift(vect)
        self.symbols = VMobject(*symbols)

        self.play(Write(notation))
        self.play(Write(self.symbols))
        self.wait()
        self.add(notation, self.symbols)



    def shift_to_good_and_back(self):
        sum2 = self.sum1.copy()
        sigma = sum2.submobjects[1]
        plus = TexMobject("+").replace(sigma)
        sum2.submobjects[1] = plus

        prod2 = self.prod1.copy()
        pi = prod2.submobjects[0]
        times = TexMobject("\\times").replace(pi)
        prod2.submobjects[0] = times

        new_sin, new_cos, new_tan = [
            VMobject().set_points_as_corners(
                corners
            ).replace(trig_part.split()[0])
            for corners, trig_part in zip(
                [
                    [RIGHT, RIGHT+UP, LEFT],
                    [RIGHT+UP, LEFT, RIGHT],
                    [RIGHT+UP, RIGHT, LEFT],
                ],
                self.trigs1.split()
            )
        ]
        x1, x2, x3 = [
            trig_part.split()[1]
            for trig_part in self.trigs1.split()
        ]
        trigs2 = VMobject(
            VMobject(new_sin, x1),
            VMobject(new_cos, x2),
            VMobject(new_tan, x3),
        )

        x, arrow, y = TexMobject("x \\rightarrow y").split()
        f = TexMobject("f")
        f.next_to(arrow, UP)
        func2 = VMobject(f, VMobject(), x, VMobject(), arrow, y)
        func2.scale(0.5)
        func2.shift(self.func1.get_center())

        good_symbols = VMobject(sum2, prod2, trigs2, func2)
        bad_symbols = self.symbols.copy()
        self.play(Transform(
            self.symbols, good_symbols, 
            path_arc = np.pi
        ))
        self.wait(3)
        self.play(Transform(
            self.symbols, bad_symbols,
            path_arc = np.pi
        ))
        self.wait()


    def shift_to_visuals(self):
        sigma, prod, trig, func = self.symbols.split()
        new_trig = trig.copy()        
        sin, cos, tan = [
            trig_part.split()[0]
            for trig_part in new_trig.split()
        ]
        trig_anim = TrigAnimation()
        sin.set_color(trig_anim.sin_color)
        cos.set_color(trig_anim.cos_color)
        tan.set_color(trig_anim.tan_color)
        new_trig.to_corner(UP+RIGHT)
        sum_lines = self.get_harmonic_sum_lines()

        self.play(
            Transform(trig, new_trig),
            *it.starmap(ApplyMethod, [
                (sigma.to_corner, UP+LEFT),
                (prod.shift, 15*LEFT),
                (func.shift, 5*UP),
            ])
        )
        sum_lines.next_to(sigma, DOWN)        
        self.remove(prod, func)
        self.play(
            trig_anim,
            Write(sum_lines)
        )
        self.play(trig_anim)
        self.wait()

    def get_harmonic_sum_lines(self):
        result = VMobject()
        for n in range(1, 8):
            big_line = NumberLine(
                x_min = 0,
                x_max = 1.01,
                tick_frequency = 1./n,
                numbers_with_elongated_ticks = [],
                color = WHITE
            )
            little_line = Line(
                big_line.number_to_point(0),
                big_line.number_to_point(1./n),
                color = RED
            )
            big_line.add(little_line)
            big_line.shift(0.5*n*DOWN)
            result.add(big_line)
        return result


    def swipe_left(self):
        everyone = VMobject(*self.mobjects)
        self.play(ApplyMethod(everyone.shift, 20*LEFT))


class ButDots(Scene):
    def construct(self):
        but = TextMobject("but")
        dots = TexMobject("\\dots")
        dots.next_to(but, aligned_edge = DOWN)
        but.shift(20*RIGHT)
        self.play(ApplyMethod(but.shift, 20*LEFT))
        self.play(Write(dots, run_time = 5))
        self.wait()


class ThreesomeOfNotation(Scene):
    def construct(self):
        exp = TexMobject("x^y = z")
        log = TexMobject("\\log_x(z) = y")
        rad = TexMobject("\\sqrt[y]{z} = x")
        exp.to_edge(LEFT).shift(2*UP)
        rad.to_edge(RIGHT).shift(2*DOWN)
        x1, y1, eq, z1 = exp.split()
        l, o, g, x2, p, z2, p, eq, y2 = log.split()
        y3, r, r, z3, eq, x3 = rad.split()
        vars1 = VMobject(x1, y1, z1).copy()
        vars2 = VMobject(x2, y2, z2)
        vars3 = VMobject(x3, y3, z3)

        self.play(Write(exp))
        self.play(Transform(vars1, vars2, path_arc = -np.pi))
        self.play(Write(log))
        self.play(Transform(vars1, vars3, path_arc = -np.pi))
        self.play(Write(rad))
        self.wait()

        words = TextMobject("Artificially unrelated")
        words.to_corner(UP+RIGHT)
        words.set_color(YELLOW)
        self.play(Write(words))
        self.wait()


class TwoThreeEightExample(Scene):
    def construct(self):
        start = TexMobject("2 \\cdot 2 \\cdot 2 = 8")
        two1, dot1, two2, dot2, two3, eq, eight = start.split()
        brace = Brace(VMobject(two1, two3), DOWN)
        three = TexMobject("3").next_to(brace, DOWN, buff = 0.2)
        rogue_two = two1.copy()

        self.add(two1)
        self.play(
            Transform(rogue_two, two2),
            Write(dot1),
            run_time = 0.5
        )
        self.add(two2)
        self.play(
            Transform(rogue_two, two3),
            Write(dot2),
            run_time = 0.5
        )
        self.add(two3)
        self.remove(rogue_two)
        self.play(
            Write(eq), Write(eight), 
            GrowFromCenter(brace),
            Write(three),
            run_time = 1
        )
        self.wait()

        exp = TexMobject("2^3")
        exp.next_to(eq, LEFT)
        exp.shift(0.2*UP)
        base_two, exp_three = exp.split()
        self.play(
            Transform(
                VMobject(two1, dot1, two2, dot2, brace, three),
                exp_three,
                path_arc = -np.pi/2
            ),
            Transform(two3, base_two)
        )
        self.clear()
        self.add(base_two, exp_three, eq, eight)
        self.wait(3)

        rad_three, rad1, rad2, rad_eight, rad_eq, rad_two = \
            TexMobject("\\sqrt[3]{8} = 2").split()
        self.play(*[
            Transform(*pair, path_arc = np.pi/2)
            for pair in [
                (exp_three, rad_three),
                (VMobject(), rad1),
                (VMobject(), rad2),
                (eight, rad_eight),
                (eq, rad_eq),
                (base_two, rad_two)
            ]
        ])
        self.wait()
        self.play(ApplyMethod(
            VMobject(rad1, rad2).set_color, RED,
            rate_func = there_and_back,
            run_time = 2
        ))
        self.remove(rad1, rad2)
        self.wait()

        l, o, g, log_two, p1, log_eight, p2, log_eq, log_three = \
            TexMobject("\\log_2(8) = 3").split()
        self.clear()
        self.play(*[
            Transform(*pair, path_arc = np.pi/2)
            for pair in [
                (rad1, l),
                (rad2, o),
                (rad2.copy(), g),
                (rad_two, log_two),
                (VMobject(), p1),
                (rad_eight, log_eight),
                (VMobject(), p2),
                (rad_eq, log_eq),
                (rad_three, log_three)
            ]
        ])
        self.wait()
        self.play(ApplyMethod(
            VMobject(l, o, g).set_color, RED,
            rate_func = there_and_back,
            run_time = 2
        ))
        self.wait()

class WhatTheHell(Scene):
    def construct(self):
        randy = Randolph()
        randy.to_corner(DOWN+LEFT)
        exp, rad, log = list(map(TexMobject,[
            "2^3 = 8",
            "\\sqrt[3]{8} = 2",
            "\\log_2(8) = 3",
        ]))
        # exp.set_color(BLUE_D)
        # rad.set_color(RED_D)
        # log.set_color(GREEN_D)
        arrow1 = DoubleArrow(DOWN, UP)
        arrow2 = arrow1.copy()
        last = exp
        for mob in arrow1, rad, arrow2, log:
            mob.next_to(last, DOWN)
            last = mob
        q_marks = VMobject(*[
            TexMobject("?!").next_to(arrow, RIGHT)
            for arrow in (arrow1, arrow2)
        ])
        q_marks.set_color(RED_D)
        everyone = VMobject(exp, rad, log, arrow1, arrow2, q_marks)
        everyone.scale(0.7)
        everyone.to_corner(UP+RIGHT)
        phrases = [
            TextMobject(
                ["Communicate with", words]
            ).next_to(mob, LEFT, buff = 1)
            for words, mob in [
                ("position", exp),
                ("a new symbol", rad),
                ("a word", log)
            ]
        ]
        for phrase, color in zip(phrases, [BLUE, RED, GREEN]):
            phrase.split()[1].set_color(color)

        self.play(ApplyMethod(randy.change_mode, "angry"))
        self.play(FadeIn(VMobject(exp, rad, log)))
        self.play(
            ShowCreationPerSubmobject(arrow1),
            ShowCreationPerSubmobject(arrow2)
        )
        self.play(Write(q_marks))
        self.wait()
        self.remove(randy)
        self.play(Write(VMobject(*phrases)))
        self.wait()

class Countermathematical(Scene):
    def construct(self):
        counterintuitive = TextMobject("Counterintuitive")
        mathematical = TextMobject("mathematical")
        intuitive = VMobject(*counterintuitive.split()[7:])
        mathematical.shift(intuitive.get_left()-mathematical.get_left())

        self.add(counterintuitive)
        self.wait()
        self.play(Transform(intuitive, mathematical))
        self.wait()


class PascalsCollision(Scene):
    def construct(self):
        pascals_triangle = PascalsTriangle()
        pascals_triangle.scale(0.5)
        final_triangle = PascalsTriangle()
        final_triangle.fill_with_n_choose_k()
        pascals_triangle.to_corner(UP+LEFT)
        final_triangle.scale(0.7)
        final_triangle.to_edge(UP)
        equation = TexMobject([
            "{n \\choose k}",
            " = \\dfrac{n!}{(n-k)!k!}"
        ])
        equation.scale(0.5)
        equation.to_corner(UP+RIGHT)
        n_choose_k, formula = equation.split()
        words = TextMobject("Seemingly unrelated")
        words.shift(2*DOWN)
        to_remove = VMobject(*words.split()[:-7])

        self.add(pascals_triangle, n_choose_k, formula)
        self.play(Write(words))
        self.wait()
        self.play(
            Transform(pascals_triangle, final_triangle),
            Transform(n_choose_k, final_triangle),
            FadeOut(formula),
            ApplyMethod(to_remove.shift, 5*DOWN)
        )
        self.wait()


class LogarithmProperties(Scene):
    def construct(self):
        randy = Randolph()
        randy.to_corner()
        bubble = ThoughtBubble().pin_to(randy)
        props = [
            TexMobject("\\log_a(x) = \\dfrac{\\log_b(a)}{\\log_b(x)}"),        
            TexMobject("\\log_a(x) = \\dfrac{\\log_b(x)}{\\log_b(a)}"),
            TexMobject("\\log_a(x) = \\log_b(x) - \\log_b(a)"),
            TexMobject("\\log_a(x) = \\log_b(x) + \\log_b(a)"),
            TexMobject("\\log_a(x) = \\dfrac{\\log_b(x)}{\\log_b(a)}"),            
        ]
        bubble.add_content(props[0])
        words = TextMobject("What was it again?")
        words.set_color(YELLOW)
        words.scale(0.5)
        words.next_to(props[0], UP)

        self.play(
            ApplyMethod(randy.change_mode, "confused"),
            ShowCreation(bubble),
            Write(words)
        )
        self.show_frame()
        for i, prop in enumerate(props[1:]):
            self.play(ApplyMethod(bubble.add_content, prop))
            if i%2 == 0:
                self.play(Blink(randy))
            else:
                self.wait()


class HaveToShare(Scene):
    def construct(self):
        words = list(map(TextMobject, [
            "Lovely", "Symmetrical", "Utterly Reasonable"
        ]))
        for w1, w2 in zip(words, words[1:]):
            w2.next_to(w1, DOWN)
        VMobject(*words).center()
        left_dot, top_dot, bottom_dot = [
            Dot(point, radius = 0.1)
            for point in (ORIGIN, RIGHT+0.5*UP, RIGHT+0.5*DOWN)
        ]
        line1, line2 = [
            Line(left_dot.get_center(), dot.get_center(), buff = 0)
            for dot in (top_dot, bottom_dot)
        ]
        share = VMobject(left_dot, top_dot, bottom_dot, line1, line2)
        share.next_to(words[1], RIGHT, buff = 1)
        share.set_color(RED)

        for word in words:
            self.play(FadeIn(word))
        self.wait()
        self.play(Write(share, run_time = 1))
        self.wait()









