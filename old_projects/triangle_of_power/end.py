from manimlib.imports import *

from old_projects.triangle_of_power.triangle import TOP, OPERATION_COLORS

class DontLearnFromSymbols(Scene):
    def construct(self):
        randy = Randolph().to_corner()
        bubble = randy.get_bubble()
        bubble.content_scale_factor = 0.6
        bubble.add_content(TOP(2, 3, 8).scale(0.7))
        equation = VMobject(
            TOP(2, "x"), 
            TexMobject("\\times"),
            TOP(2, "y"),
            TexMobject("="),
            TOP(2, "x+y")
        )
        equation.arrange()
        q_marks = TextMobject("???")
        q_marks.set_color(YELLOW)
        q_marks.next_to(randy, UP)

        self.add(randy)
        self.play(FadeIn(bubble))
        self.wait()
        top = bubble.content
        bubble.add_content(equation)
        self.play(
            FadeOut(top),
            ApplyMethod(randy.change_mode, "sassy"),
            Write(bubble.content),
            Write(q_marks),
            run_time = 1
        )
        self.wait(3)


class NotationReflectsMath(Scene):
    def construct(self):
        top_expr = TextMobject("Notation $\\Leftrightarrow$ Math")
        top_expr.shift(2*UP)
        better_questions = TextMobject("Better questions")
        arrow = Arrow(top_expr, better_questions)

        self.play(Write(top_expr))
        self.play(
            ShowCreationPerSubmobject(
                arrow,
                rate_func = lambda t : min(smooth(3*t), 1)
            ),
            Write(better_questions),
            run_time = 3
        )
        self.wait(2)

class AsymmetriesInTheMath(Scene):
    def construct(self):
        assyms_of_top = VMobject(
            TextMobject("Asymmetries of "),
            TOP("a", "b", "c", radius = 0.75).set_color(BLUE)
        ).arrange()
        assyms_of_top.to_edge(UP)
        assyms_of_math = TextMobject("""
            Asymmetries of 
            $\\underbrace{a \\cdot a \\cdots a}_{\\text{$b$ times}} = c$
        """)
        VMobject(*assyms_of_math.split()[13:]).set_color(YELLOW)
        assyms_of_math.next_to(assyms_of_top, DOWN, buff = 2)
        rad = TexMobject("\\sqrt{\\quad}").to_edge(LEFT).shift(UP)
        rad.set_color(RED)
        log = TexMobject("\\log").next_to(rad, DOWN)
        log.set_color(RED)

        self.play(FadeIn(assyms_of_top))
        self.wait()
        self.play(FadeIn(assyms_of_math))
        self.wait()
        self.play(Write(VMobject(rad, log)))
        self.wait()

class AddedVsOplussed(Scene):
    def construct(self):
        top = TOP()
        left_times  = top.put_in_vertex(0, TexMobject("\\times"))
        left_dot    = top.put_in_vertex(0, Dot())
        right_times = top.put_in_vertex(2, TexMobject("\\times"))
        right_dot   = top.put_in_vertex(2, Dot())
        plus        = top.put_in_vertex(1, TexMobject("+"))
        oplus       = top.put_in_vertex(1, TexMobject("\\oplus"))
        left_times.set_color(YELLOW)        
        right_times.set_color(YELLOW)        
        plus.set_color(GREEN)        
        oplus.set_color(BLUE)

        self.add(top, left_dot, plus, right_times)
        self.wait()
        self.play(
            Transform(
                VMobject(left_dot, plus, right_times),
                VMobject(right_dot, oplus, left_times),
                path_arc = np.pi/2
            )
        )
        self.wait()



class ReciprocalTop(Scene):
    def construct(self):
        top = TOP()
        start_two = top.put_on_vertex(2, 2)
        end_two = top.put_on_vertex(0, 2)
        x = top.put_on_vertex(1, "x")
        one_over_x = top.put_on_vertex(1, "\\dfrac{1}{x}")
        x.set_color(GREEN)
        one_over_x.set_color(BLUE)
        start_two.set_color(YELLOW)
        end_two.set_color(YELLOW)

        self.add(top, start_two, x)
        self.wait()
        self.play(
            Transform(
                VMobject(start_two, x),
                VMobject(end_two, one_over_x)
            ),
            ApplyMethod(top.rotate, np.pi, UP, path_arc = np.pi/7)
        )
        self.wait()



class NotSymbolicPatterns(Scene):
    def construct(self):
        randy = Randolph()
        symbolic_patterns = TextMobject("Symbolic patterns")
        symbolic_patterns.to_edge(RIGHT).shift(UP)
        line = Line(LEFT, RIGHT, color = RED, stroke_width = 7)
        line.replace(symbolic_patterns)
        substantive_reasoning = TextMobject("Substantive reasoning")
        substantive_reasoning.to_edge(RIGHT).shift(DOWN)

        self.add(randy, symbolic_patterns)
        self.wait()
        self.play(ShowCreation(line))
        self.play(
            Write(substantive_reasoning),
            ApplyMethod(randy.change_mode, "pondering_looking_left"),
            run_time = 1
        )
        self.wait(2)
        self.play(
            ApplyMethod(line.shift, 10*DOWN),
            ApplyMethod(substantive_reasoning.shift, 10*DOWN),
            ApplyMethod(randy.change_mode, "sad"),
            run_time = 1
        )
        self.wait(2)

class ChangeWeCanBelieveIn(Scene):
    def construct(self):
        words = TextMobject("Change we can believe in")
        change = VMobject(*words.split()[:6])
        top = TOP(radius = 0.75)
        top.shift(change.get_right()-top.get_right())

        self.play(Write(words))
        self.play(
            FadeOut(change),
            GrowFromCenter(top)
        )
        self.wait(3)



class TriangleOfPowerIsBetter(Scene):
    def construct(self):
        top = TOP("x", "y", "z", radius = 0.75)
        top.set_color(BLUE)
        alts = VMobject(*list(map(TexMobject, [
            "x^y", "\\log_x(z)", "\\sqrt[y]{z}"
        ])))
        for mob, color in zip(alts.split(), OPERATION_COLORS):
            mob.set_color(color)
        alts.arrange(DOWN)
        greater_than = TexMobject(">")
        top.next_to(greater_than, LEFT)
        alts.next_to(greater_than, RIGHT)

        self.play(Write(VMobject(top, greater_than, alts)))
        self.wait()


class InYourOwnNotes(Scene):
    def construct(self):
        anims = [
            self.get_log_anim(3*LEFT), 
            self.get_exp_anim(3*RIGHT), 
        ]
        for anim in anims:
            self.add(anim.mobject)
        self.wait(2)
        self.play(*anims)
        self.wait(2)


    def get_log_anim(self, center):
        O_log_n = TexMobject(["O(", "\\log(n)", ")"])
        O_log_n.shift(center)
        log_n = O_log_n.split()[1]
        #super hacky
        g = log_n.split()[2]
        for mob in g.submobjects:
            mob.is_subpath = False 
            mob.set_fill(BLACK, 1.0)
            log_n.add(mob)
        g.submobjects = []
        #end hack
        top = TOP(2, None, "n", radius = 0.75)
        top.set_width(log_n.get_width())
        top.shift(log_n.get_center())
        new_O_log_n = O_log_n.copy()
        new_O_log_n.submobjects[1] = top
        return Transform(O_log_n, new_O_log_n)


    def get_exp_anim(self, center):
        epii = TexMobject("e^{\\pi i} = -1")
        epii.shift(center)
        top = TOP("e", "\\pi i", "-1", radius = 0.75)
        top.shift(center)
        e, pi, i, equals, minus, one = epii.split()
        ##hacky
        loop = e.submobjects[0]
        loop.is_subpath = False
        loop.set_fill(BLACK, 1.0)
        e.submobjects = []
        ##
        start = VMobject(
            equals,
            VMobject(e, loop), 
            VMobject(pi, i),
            VMobject(minus, one)
        )
        return Transform(start, top)



class Qwerty(Scene):
    def construct(self):
        qwerty = VMobject(
            TextMobject(list("QWERTYUIOP")),
            TextMobject(list("ASDFGHJKL")),
            TextMobject(list("ZXCVBNM")),
        )
        qwerty.arrange(DOWN)
        dvorak = VMobject(
            TextMobject(list("PYFGCRL")),
            TextMobject(list("AOEUIDHTNS")),
            TextMobject(list("QJKXBMWVZ")),
        )
        dvorak.arrange(DOWN)
        d1, d2, d3 = dvorak.split()
        d1.shift(0.9*RIGHT)
        d3.shift(0.95*RIGHT)

        self.add(qwerty)
        self.wait(2)
        self.play(Transform(qwerty, dvorak))
        self.wait(2)


class ShowLog(Scene):
    def construct(self):
        equation = VMobject(*[
            TOP(2, None, "x"), 
            TexMobject("+"),
            TOP(2, None, "y"),
            TexMobject("="),
            TOP(2, None, "xy")
        ]).arrange()
        old_eq = TexMobject("\\log_2(x) + \\log_2(y) = \\log_2(xy)")
        old_eq.to_edge(UP)
        
        self.play(FadeIn(equation))
        self.wait(3)
        self.play(FadeIn(old_eq))
        self.wait(2)


class NoOneWillActuallyDoThis(Scene):
    def construct(self):
        randy = Randolph().to_corner()
        bubble = SpeechBubble().pin_to(randy)
        words = TextMobject("No one will actually do this...")
        tau_v_pi = TexMobject("\\tau > \\pi").scale(2)
        morty = Mortimer("speaking").to_corner(DOWN+RIGHT)
        morty_bubble = SpeechBubble(
            direction = RIGHT, 
            height = 4
        )
        morty_bubble.pin_to(morty)
        final_words = TextMobject("If this war is won, it will \\\\ not be won with that attitude")
        lil_thought_bubble = ThoughtBubble(height = 3, width = 5)
        lil_thought_bubble.set_fill(BLACK, 1.0)
        lil_thought_bubble.pin_to(randy)
        lil_thought_bubble.write("Okay buddy, calm down, it's notation \\\\ we're talking about not war.")
        lil_thought_bubble.show()


        self.add(randy)
        self.play(
            ApplyMethod(randy.change_mode, "sassy"),            
            ShowCreation(bubble)
        )
        bubble.add_content(words)
        self.play(Write(words), run_time = 2)
        self.play(Blink(randy))
        bubble.add_content(tau_v_pi)
        self.play(
            FadeOut(words),
            GrowFromCenter(tau_v_pi),
            ApplyMethod(randy.change_mode, "speaking")
        )
        self.remove(words)
        self.play(Blink(randy))
        self.wait(2)
        self.play(
            FadeOut(bubble),
            FadeIn(morty),
            ShowCreation(morty_bubble),
            ApplyMethod(randy.change_mode, "plain")
        )
        morty_bubble.add_content(final_words)
        self.play(Write(final_words))
        self.wait()
        self.play(Blink(morty))
        self.wait(2)
        self.play(ShowCreation(lil_thought_bubble))














