import numbers
from manimlib.imports import *
from functools import reduce

OPERATION_COLORS = [YELLOW, GREEN, BLUE_B]

def get_equation(index, x = 2, y = 3, z = 8, expression_only = False):
    assert(index in [0, 1, 2])
    if index == 0:
        tex1 = "\\sqrt[%d]{%d}"%(y, z), 
        tex2 = " = %d"%x
    elif index == 1:
        tex1 = "\\log_%d(%d)"%(x, z), 
        tex2 = " = %d"%y
    elif index == 2:
        tex1 = "%d^%d"%(x, y), 
        tex2 = " = %d"%z
    if expression_only:
        tex = tex1
    else:
        tex = tex1+tex2
    return TexMobject(tex).set_color(OPERATION_COLORS[index])

def get_inverse_rules():
    return list(map(TexMobject, [
        "x^{\\log_x(z)} = z",
        "\\log_x\\left(x^y \\right) = y",
        "\\sqrt[y]{x^y} = x",
        "\\left(\\sqrt[y]{z}\\right)^y = z",
        "\\sqrt[\\log_x(z)]{z} = x",
        "\\log_{\\sqrt[y]{z}}(z) = y",
    ]))

def get_top_inverse_rules():
    result = []
    pairs = [#Careful of order here!
        (0, 2),
        (0, 1),
        (1, 0),
        (1, 2),
        (2, 0),
        (2, 1),
    ]
    for i, j in pairs:
        top = get_top_inverse(i, j)
        char = ["x", "y", "z"][j]
        eq = TexMobject("= %s"%char)
        eq.scale(2)
        eq.next_to(top, RIGHT)
        diff = eq.get_center() - top.triangle.get_center()
        eq.shift(diff[1]*UP)
        result.append(VMobject(top, eq))
    return result

def get_top_inverse(i, j):
    args = [None]*3
    k = set([0, 1, 2]).difference([i, j]).pop()
    args[i] = ["x", "y", "z"][i]
    big_top = TOP(*args)
    args[j] = ["x", "y", "z"][j]
    lil_top = TOP(*args, triangle_height_to_number_height = 1.5)
    big_top.set_value(k, lil_top)
    return big_top

class TOP(VMobject):
    CONFIG = {
        "triangle_height_to_number_height" : 3,
        "offset_multiple" : 1.5,
        "radius" : 1.5,
    }
    def __init__(self, x = None, y = None, z = None, **kwargs):
        digest_config(self, kwargs, locals())
        VMobject.__init__(self, **kwargs)

    def generate_points(self):
        vertices = [
            self.radius*rotate_vector(RIGHT, 7*np.pi/6 - i*2*np.pi/3)
            for i in range(3)
        ]
        self.triangle = Polygon(
            *vertices, 
            color = WHITE,
            stroke_width = 5
        )
        self.values = [VMobject()]*3
        self.set_values(self.x, self.y, self.z)

    def set_values(self, x, y, z):
        for i, mob in enumerate([x, y, z]):
            self.set_value(i, mob)

    def set_value(self, index, value):
        self.values[index] = self.put_on_vertex(index, value)
        self.reset_submobjects()

    def put_on_vertex(self, index, value):
        assert(index in [0, 1, 2])
        if value is None:
            value = VectorizedPoint()
        if isinstance(value, numbers.Number):
            value = str(value)
        if isinstance(value, str):
            value = TexMobject(value)
        if isinstance(value, TOP):
            return self.put_top_on_vertix(index, value)
        self.rescale_corner_mobject(value)
        value.center()
        if index == 0:
            offset = -value.get_corner(UP+RIGHT)
        elif index == 1:
            offset = -value.get_bottom()
        elif index == 2:
            offset = -value.get_corner(UP+LEFT)
        value.shift(self.offset_multiple*offset)
        anchors = self.triangle.get_anchors_and_handles()[0]
        value.shift(anchors[index])
        return value

    def put_top_on_vertix(self, index, top):
        top.set_height(2*self.get_value_height())
        vertices = np.array(top.get_vertices())
        vertices[index] = 0
        start = reduce(op.add, vertices)/2
        end = self.triangle.get_anchors_and_handles()[0][index]
        top.shift(end-start)
        return top

    def put_in_vertex(self, index, mobject):
        self.rescale_corner_mobject(mobject)
        mobject.center()
        mobject.shift(interpolate(
            self.get_center(),
            self.get_vertices()[index],
            0.7
        ))
        return mobject


    def get_surrounding_circle(self, color = YELLOW):
        return Circle(
            radius = 1.7*self.radius,
            color = color
        ).shift(
            self.triangle.get_center(),
            (self.triangle.get_height()/6)*DOWN
        )

    def rescale_corner_mobject(self, mobject):
        mobject.set_height(self.get_value_height())
        return self

    def get_value_height(self):
        return self.triangle.get_height()/self.triangle_height_to_number_height

    def get_center(self):
        return center_of_mass(self.get_vertices())

    def get_vertices(self):
        return self.triangle.get_anchors_and_handles()[0][:3]

    def reset_submobjects(self):
        self.submobjects = [self.triangle] + self.values
        return self


class IntroduceNotation(Scene):
    def construct(self):
        top = TOP()
        equation = TexMobject("2^3 = 8")
        equation.to_corner(UP+LEFT)
        two, three, eight = [
            top.put_on_vertex(i, num)
            for i, num in enumerate([2, 3, 8])
        ]

        self.play(FadeIn(equation))
        self.wait()
        self.play(ShowCreation(top))
        for num in two, three, eight:
            self.play(ShowCreation(num), run_time=2)
        self.wait()

class ShowRule(Scene):
    args_list = [(0,), (1,), (2,)]

    @staticmethod
    def args_to_string(index):
        return str(index)
        
    @staticmethod
    def string_to_args(index_string):
        result =  int(index_string)
        assert(result in [0, 1, 2])
        return result

    def construct(self, index):
        equation = get_equation(index)
        equation.to_corner(UP+LEFT)
        top = TOP(2, 3, 8)
        new_top = top.copy()
        equals = TexMobject("=").scale(1.5)
        new_top.next_to(equals, LEFT, buff = 1)
        new_top.values[index].next_to(equals, RIGHT, buff = 1)
        circle = Circle(
            radius = 1.7*top.radius, 
            color = OPERATION_COLORS[index]
        )
        

        self.add(equation, top)
        self.wait()
        self.play(
            Transform(top, new_top),
            ShowCreation(equals)
        )

        circle.shift(new_top.triangle.get_center_of_mass())
        new_circle = circle.copy()
        new_top.put_on_vertex(index, new_circle)
        self.wait()
        self.play(ShowCreation(circle))
        self.wait()
        self.play(
            Transform(circle, new_circle),
            ApplyMethod(new_top.values[index].set_color, circle.color)
        )
        self.wait()


class AllThree(Scene):
    def construct(self):
        tops = []
        equations = []
        args = (2, 3, 8)
        for i in 2, 1, 0:
            new_args = list(args)
            new_args[i] = None
            top = TOP(*new_args, triangle_height_to_number_height = 2)
            # top.set_color(OPERATION_COLORS[i])
            top.shift(i*4.5*LEFT)
            equation = get_equation(i, expression_only = True)
            equation.scale(3)
            equation.next_to(top, DOWN, buff = 0.7)
            tops.append(top)
            equations.append(equation)
        VMobject(*tops+equations).center()
        # name = TextMobject("Triangle of Power")
        # name.to_edge(UP)

        for top, eq in zip(tops, equations):
            self.play(FadeIn(top), FadeIn(eq))
        self.wait(3)
        # self.play(Write(name))
        self.wait()

class SixDifferentInverses(Scene):
    def construct(self):
        rules = get_inverse_rules()
        vects = it.starmap(op.add, it.product(
            [3*UP, 0.5*UP, 2*DOWN], [2*LEFT, 2*RIGHT]
        ))
        for rule, vect in zip(rules, vects):
            rule.shift(vect)
        general_idea = TexMobject("f(f^{-1}(a)) = a")

        self.play(Write(VMobject(*rules)))
        self.wait()
        for s, color in (rules[:4], GREEN), (rules[4:], RED):
            mob = VMobject(*s)
            self.play(ApplyMethod(mob.set_color, color))
            self.wait()
            self.play(ApplyMethod(mob.set_color, WHITE))
        self.play(
            ApplyMethod(VMobject(*rules[::2]).to_edge, LEFT),
            ApplyMethod(VMobject(*rules[1::2]).to_edge, RIGHT),
            GrowFromCenter(general_idea)
        )
        self.wait()

        top_rules = get_top_inverse_rules()
        for rule, top_rule in zip(rules, top_rules):
            top_rule.set_height(1.5)
            top_rule.center()
            top_rule.shift(rule.get_center())
        self.play(*list(map(FadeOut, rules)))
        self.remove(*rules)
        self.play(*list(map(GrowFromCenter, top_rules)))
        self.wait()
        self.remove(general_idea)
        rules = get_inverse_rules()
        original = None
        for i, (top_rule, rule) in enumerate(zip(top_rules, rules)):
            rule.center().to_edge(UP)
            rule.set_color(GREEN if i < 4 else RED)
            self.add(rule)
            new_top_rule = top_rule.copy().center().scale(1.5)
            anims = [Transform(top_rule, new_top_rule)]
            if original is not None:
                anims.append(FadeIn(original))
            original = top_rule.copy()
            self.play(*anims)
            self.wait()
            self.animate_top_rule(top_rule)
            self.remove(rule)

    def animate_top_rule(self, top_rule):
        lil_top, lil_symbol, symbol_index = None, None, None
        big_top = top_rule.submobjects[0]
        equals, right_symbol = top_rule.submobjects[1].split()
        for i, value in enumerate(big_top.values):
            if isinstance(value, TOP):
                lil_top = value
            elif isinstance(value, TexMobject):
                symbol_index = i
            else: 
                lil_symbol_index = i
        lil_symbol = lil_top.values[lil_symbol_index]
                
        assert(lil_top is not None and lil_symbol is not None)
        cancel_parts = [
            VMobject(top.triangle, top.values[symbol_index])
            for top in (lil_top, big_top)
        ]
        new_symbol = lil_symbol.copy()
        new_symbol.replace(right_symbol)
        vect = equals.get_center() - right_symbol.get_center()
        new_symbol.shift(2*vect[0]*RIGHT)
        self.play(
            Transform(*cancel_parts, rate_func = rush_into)
        )
        self.play(
            FadeOut(VMobject(*cancel_parts)),
            Transform(lil_symbol, new_symbol, rate_func = rush_from)
        )
        self.wait()
        self.remove(lil_symbol, top_rule, VMobject(*cancel_parts))


class SixSixSix(Scene):
    def construct(self):
        randy = Randolph(mode = "pondering").to_corner()
        bubble = ThoughtBubble().pin_to(randy)
        rules = get_inverse_rules()
        sixes = TexMobject(["6", "6", "6"], next_to_buff = 1)
        sixes.to_corner(UP+RIGHT)
        sixes = sixes.split()
        speech_bubble = SpeechBubble()
        speech_bubble.pin_to(randy)
        speech_bubble.write("I'll just study art!")

        self.add(randy)
        self.play(ShowCreation(bubble))
        bubble.add_content(VectorizedPoint())
        for i, rule in enumerate(rules):
            if i%2 == 0:
                anim = ShowCreation(sixes[i/2])
            else:
                anim = Blink(randy)
            self.play(
                ApplyMethod(bubble.add_content, rule),
                anim
            )
            self.wait()
        self.wait()
        words = speech_bubble.content
        equation = bubble.content
        speech_bubble.clear()
        bubble.clear()
        self.play(
            ApplyMethod(randy.change_mode, "angry"),
            Transform(bubble, speech_bubble),
            Transform(equation, words),
            FadeOut(VMobject(*sixes))
        )
        self.wait()

class AdditiveProperty(Scene):
    def construct(self):
        exp_rule, log_rule = self.write_old_style_rules()
        t_exp_rule, t_log_rule = self.get_new_style_rules()

        self.play(
            ApplyMethod(exp_rule.to_edge, UP),
            ApplyMethod(log_rule.to_edge, DOWN, 1.5)
        )
        t_exp_rule.next_to(exp_rule, DOWN)
        t_exp_rule.set_color(GREEN)
        t_log_rule.next_to(log_rule, UP)
        t_log_rule.set_color(RED)
        self.play(
            FadeIn(t_exp_rule),
            FadeIn(t_log_rule),
            ApplyMethod(exp_rule.set_color, GREEN),
            ApplyMethod(log_rule.set_color, RED),
        )
        self.wait()
        all_tops = [m for m in t_exp_rule.split()+t_log_rule.split() if isinstance(m, TOP)]
        self.put_in_circles(all_tops)
        self.set_color_appropriate_parts(t_exp_rule, t_log_rule)




    def write_old_style_rules(self):
        start = TexMobject("a^x a^y = a^{x+y}")
        end = TexMobject("\\log_a(xy) = \\log_a(x) + \\log_a(y)")
        start.shift(UP)
        end.shift(DOWN)
        a1, x1, a2, y1, eq1, a3, p1, x2, y2 = start.split()
        a4, x3, y3, eq2, a5, x4, p2, a6, y4 = np.array(end.split())[
            [3, 5, 6, 8, 12, 14, 16, 20, 22]
        ]
        start_copy = start.copy()
        self.play(Write(start_copy))
        self.wait()
        self.play(Transform(
            VMobject(a1, x1, a2, y1, eq1, a3, p1, x2, a3.copy(), y2),
            VMobject(a4, x3, a4.copy(), y3, eq2, a5, p2, x4, a6, y4)
        ))
        self.play(Write(end))
        self.clear()
        self.add(start_copy, end)
        self.wait()
        return start_copy, end

    def get_new_style_rules(self):
        upper_mobs = [
            TOP("a", "x", "R"), Dot(), 
            TOP("a", "y", "R"), TexMobject("="), 
            TOP("a", "x+y")
        ]
        lower_mobs = [
            TOP("a", None, "xy"), TexMobject("="),
            TOP("a", None, "x"), TexMobject("+"),
            TOP("a", None, "y"),
        ]
        for mob in upper_mobs + lower_mobs:
            if isinstance(mob, TOP):
                mob.scale(0.5)
        for group in upper_mobs, lower_mobs:
            for m1, m2 in zip(group, group[1:]):
                m2.next_to(m1)
        for top in upper_mobs[0], upper_mobs[2]:
            top.set_value(2, None)
        upper_mobs = VMobject(*upper_mobs).center().shift(2*UP)
        lower_mobs = VMobject(*lower_mobs).center().shift(2*DOWN)
        return upper_mobs, lower_mobs

    def put_in_circles(self, tops):
        anims = []
        for top in tops:
            for i, value in enumerate(top.values):
                if isinstance(value, VectorizedPoint):
                    index = i
            circle = top.put_on_vertex(index, Circle(color = WHITE))
            anims.append(
                Transform(top.copy().set_color(YELLOW), circle)
            )
        self.add(*[anim.mobject for anim in anims])
        self.wait()
        self.play(*anims)
        self.wait()

    def set_color_appropriate_parts(self, t_exp_rule, t_log_rule):
        #Horribly hacky
        circle1 = t_exp_rule.split()[0].put_on_vertex(
            2, Circle()
        )
        top_dot = t_exp_rule.split()[1]
        circle2 = t_exp_rule.split()[2].put_on_vertex(
            2, Circle()
        )
        top_plus = t_exp_rule.split()[4].values[1]

        bottom_times = t_log_rule.split()[0].values[2]
        circle3 = t_log_rule.split()[2].put_on_vertex(
            1, Circle()
        )
        bottom_plus = t_log_rule.split()[3]
        circle4 = t_log_rule.split()[4].put_on_vertex(
            1, Circle()
        )

        mob_lists = [
            [circle1, top_dot, circle2],
            [top_plus],
            [bottom_times],
            [circle3, bottom_plus, circle4]
        ]
        for mobs in mob_lists:
            copies = VMobject(*mobs).copy()
            self.play(ApplyMethod(
                copies.set_color, YELLOW, 
                run_time = 0.5
            ))
            self.play(ApplyMethod(
                copies.scale_in_place, 1.2,
                rate_func = there_and_back
            ))
            self.wait()
            self.remove(copies)


class DrawInsideTriangle(Scene):
    def construct(self):
        top = TOP()
        top.scale(2)
        dot = top.put_in_vertex(0, Dot())
        plus = top.put_in_vertex(1, TexMobject("+"))
        times = top.put_in_vertex(2, TexMobject("\\times"))
        plus.set_color(GREEN)
        times.set_color(YELLOW)

        self.add(top)
        self.wait()
        for mob in dot, plus, times:
            self.play(Write(mob, run_time = 1))
            self.wait()

class ConstantOnTop(Scene):
    def construct(self):
        top = TOP()
        dot = top.put_in_vertex(1, Dot())
        times1 = top.put_in_vertex(0, TexMobject("\\times"))
        times2 = top.put_in_vertex(2, TexMobject("\\times"))
        times1.set_color(YELLOW)
        times2.set_color(YELLOW)
        three = top.put_on_vertex(1, "3")
        lower_left_x = top.put_on_vertex(0, "x")
        lower_right_x = top.put_on_vertex(2, "x")
        x_cubed = TexMobject("x^3").to_edge(UP)
        x_cubed.submobjects.reverse() #To align better        
        cube_root_x = TexMobject("\\sqrt[3]{x}").to_edge(UP)

        self.add(top)
        self.play(ShowCreation(three))
        self.play(
            FadeIn(lower_left_x),
            Write(x_cubed),
            run_time = 1
        )
        self.wait()
        self.play(*[
            Transform(*pair, path_arc = np.pi)
            for pair in [
                (lower_left_x, lower_right_x),
                (x_cubed, cube_root_x),
            ]
        ])
        self.wait(2)
        for mob in dot, times1, times2:
            self.play(ShowCreation(mob))
            self.wait()

def get_const_top_TOP(*args):
        top = TOP(*args)
        dot = top.put_in_vertex(1, Dot())
        times1 = top.put_in_vertex(0, TexMobject("\\times"))
        times2 = top.put_in_vertex(2, TexMobject("\\times"))
        times1.set_color(YELLOW)
        times2.set_color(YELLOW)
        top.add(dot, times1, times2)
        return top


class MultiplyWithConstantTop(Scene):
    def construct(self):
        top1 = get_const_top_TOP("x", "3")
        top2 = get_const_top_TOP("y", "3")
        top3 = get_const_top_TOP("xy", "3")
        times = TexMobject("\\times")
        equals = TexMobject("=")
        top_exp_equation = VMobject(
            top1, times, top2, equals, top3
        )
        top_exp_equation.arrange()
        old_style_exp = TexMobject("(x^3)(y^3) = (xy)^3")
        old_style_exp.to_edge(UP)
        old_style_exp.set_color(GREEN)
        old_style_rad = TexMobject("\\sqrt[3]{x} \\sqrt[3]{y} = \\sqrt[3]{xy}")
        old_style_rad.to_edge(UP)
        old_style_rad.set_color(RED)

        self.add(top_exp_equation, old_style_exp)
        self.wait(3)

        old_tops = [top1, top2, top3]
        new_tops = []
        for top in old_tops:
            new_top = top.copy()
            new_top.put_on_vertex(2, new_top.values[0])
            new_top.shift(0.5*LEFT)
            new_tops.append(new_top)
        self.play(
            Transform(old_style_exp, old_style_rad),
            Transform(
                VMobject(*old_tops),
                VMobject(*new_tops),
                path_arc = np.pi/2
            )
        )
        self.wait(3)

class RightStaysConstantQ(Scene):
    def construct(self):
        top1, top2, top3 = old_tops = [
            TOP(None, s, "8")
            for s in ("x", "y", TexMobject("x?y"))
        ]
        q_mark = TexMobject("?").scale(2)
        equation = VMobject(
            top1, q_mark, top2, TexMobject("="), top3
        )
        equation.arrange(buff = 0.7)
        symbols_at_top = VMobject(*[
            top.values[1]
            for top in (top1, top2, top3)
        ])
        symbols_at_lower_right = VMobject(*[
            top.put_on_vertex(0, top.values[1].copy())
            for top in (top1, top2, top3)
        ])
        old_style_eq1 = TexMobject("\\sqrt[x]{8} ? \\sqrt[y]{8} = \\sqrt[x?y]{8}")
        old_style_eq1.set_color(BLUE)
        old_style_eq2 = TexMobject("\\log_x(8) ? \\log_y(8) = \\log_{x?y}(8)")
        old_style_eq2.set_color(YELLOW)
        for eq in old_style_eq1, old_style_eq2:
            eq.to_edge(UP)

        randy = Randolph()
        randy.to_corner()
        bubble = ThoughtBubble().pin_to(randy)
        bubble.add_content(TOP(None, None, "8"))

        self.add(randy, bubble)
        self.play(ApplyMethod(randy.change_mode, "pondering"))
        self.wait(3)
        triangle = bubble.content.triangle
        eight = bubble.content.values[2]
        bubble.clear()
        self.play(
            Transform(triangle, equation),
            FadeOut(eight),
            ApplyPointwiseFunction(
                lambda p : (p+2*DOWN)*15/get_norm(p+2*DOWN),
                bubble
            ),
            FadeIn(old_style_eq1),
            ApplyMethod(randy.shift, 3*DOWN + 3*LEFT),
            run_time = 2
        )
        self.remove(triangle)
        self.add(equation)
        self.wait(4)
        self.play(
            Transform(
                symbols_at_top, symbols_at_lower_right, 
                path_arc = np.pi/2
            ),
            Transform(old_style_eq1, old_style_eq2)
        )
        self.wait(2)


class AOplusB(Scene):
    def construct(self):
        self.add(TexMobject(
            "a \\oplus b = \\dfrac{1}{\\frac{1}{a} + \\frac{1}{b}}"
        ).scale(2))
        self.wait()


class ConstantLowerRight(Scene):
    def construct(self):
        top = TOP()
        times = top.put_in_vertex(0, TexMobject("\\times"))
        times.set_color(YELLOW)
        oplus = top.put_in_vertex(1, TexMobject("\\oplus"))
        oplus.set_color(BLUE)
        dot = top.put_in_vertex(2, Dot())
        eight = top.put_on_vertex(2, TexMobject("8"))

        self.add(top)
        self.play(ShowCreation(eight))
        for mob in dot, oplus, times:
            self.play(ShowCreation(mob))
            self.wait()

        top.add(eight)
        top.add(times, oplus, dot)
        top1, top2, top3 = tops = [
            top.copy() for i in range(3)
        ]
        big_oplus = TexMobject("\\oplus").scale(2).set_color(BLUE)
        equals = TexMobject("=")
        equation = VMobject(
            top1, big_oplus, top2, equals, top3
        )
        equation.arrange()
        top3.shift(0.5*RIGHT)
        x, y, xy = [
            t.put_on_vertex(0, s)
            for t, s in zip(tops, ["x", "y", "xy"])
        ]
        old_style_eq = TexMobject(
            "\\dfrac{1}{\\frac{1}{\\log_x(8)} + \\frac{1}{\\log_y(8)}} = \\log_{xy}(8)"
        )
        old_style_eq.to_edge(UP).set_color(RED)

        triple_top_copy = VMobject(*[
            top.copy() for i in range(3)
        ])
        self.clear()
        self.play(
            Transform(triple_top_copy, VMobject(*tops)),
            FadeIn(VMobject(x, y, xy, big_oplus, equals))
        )
        self.remove(triple_top_copy)
        self.add(*tops)
        self.play(Write(old_style_eq))
        self.wait(3)

        syms = VMobject(x, y, xy)
        new_syms = VMobject(*[
            t.put_on_vertex(1, s)
            for t, s in zip(tops, ["x", "y", "x \\oplus y"])
        ])
        new_old_style_eq = TexMobject(
            "\\sqrt[x]{8} \\sqrt[y]{8} = \\sqrt[X]{8}"
        )
        X = new_old_style_eq.split()[-4]
        frac = TexMobject("\\frac{1}{\\frac{1}{x} + \\frac{1}{y}}")
        frac.replace(X)
        frac_lower_right = frac.get_corner(DOWN+RIGHT)
        frac.scale(2)
        frac.shift(frac_lower_right - frac.get_corner(DOWN+RIGHT))
        new_old_style_eq.submobjects[-4] = frac
        new_old_style_eq.to_edge(UP)
        new_old_style_eq.set_color(RED)
        big_times = TexMobject("\\times").set_color(YELLOW)
        big_times.shift(big_oplus.get_center())
        self.play(
            Transform(old_style_eq, new_old_style_eq),
            Transform(syms, new_syms, path_arc = np.pi/2),
            Transform(big_oplus, big_times)
        )
        self.wait(4)


class TowerExponentFrame(Scene):
    def construct(self):
        words = TextMobject("""
            Consider an expression like $3^{3^3}$.  It's 
            ambiguous whether this means $27^3$ or $3^{27}$,
            which is the difference between $19{,}683$ and
            $7{,}625{,}597{,}484{,}987$.  But with the triangle
            of power, the difference is crystal clear:
        """)
        words.set_width(FRAME_WIDTH-1)
        words.to_edge(UP)
        top1 = TOP(TOP(3, 3), 3)
        top2 = TOP(3, (TOP(3, 3)))
        for top in top1, top2:
            top.next_to(words, DOWN)
        top1.shift(3*LEFT)
        top2.shift(3*RIGHT)

        self.add(words, top1, top2)
        self.wait()        


class ExponentialGrowth(Scene):
    def construct(self):
        words = TextMobject("""
            Let's say you are studying a certain growth rate, 
            and you come across an expression like $T^a$.  It
            matters a lot whether you consider $T$ or $a$
            to be the variable, since exponential growth and 
            polynomial growth have very different flavors.  The 
            nice thing about having a triangle that you can write 
            inside is that you can clarify this kind of ambiguity
            by writing a little dot next to the constant and 
            a ``$\\sim$'' next to the variable.
        """)
        words.scale(0.75)
        words.to_edge(UP)
        top = TOP("T", "a")
        top.next_to(words, DOWN)
        dot = top.put_in_vertex(0, TexMobject("\\cdot"))
        sim = top.put_in_vertex(1, TexMobject("\\sim"))

        self.add(words, top, dot, sim)
        self.show_frame()
        self.wait()




class GoExplore(Scene):
    def construct(self):
        explore = TextMobject("Go explore!")
        by_the_way = TextMobject("by the way \\dots")
        by_the_way.shift(20*RIGHT)

        self.play(Write(explore))
        self.wait(4)
        self.play(
            ApplyMethod(
                VMobject(explore, by_the_way).shift,
                20*LEFT
            )
        )
        self.wait(3)










