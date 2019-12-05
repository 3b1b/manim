from manimlib.imports import *

#revert_to_original_skipping_status

def get_stack(
    obj1, obj2, n, k,
    fixed_start = None,
    fixed_end = None,
    obj_to_obj_buff = SMALL_BUFF,
    vertical_buff = MED_SMALL_BUFF,
    ):
    stack = VGroup()
    for indices in it.combinations(list(range(n)), k):
        term = VGroup(*[
             obj1.copy() if i in indices else obj2.copy()
            for i in range(n)
        ])
        if fixed_start:
            term.add_to_back(fixed_start.copy())
        if fixed_end:
            term.add(fixed_end.copy())
        term.arrange(RIGHT, buff = obj_to_obj_buff)
        stack.add(term)
    stack.arrange(DOWN, buff = vertical_buff)
    return stack

def get_stacks(obj1, obj2, n, **kwargs):
    stacks = VGroup()
    for k in range(n+1):
        stacks.add(get_stack(obj1, obj2, n, k, **kwargs))
    stacks.arrange(
        RIGHT, 
        buff = MED_LARGE_BUFF,
        aligned_edge = DOWN
    )
    return stacks

class Male(TexMobject):
    CONFIG = {
        "height" : 0.4,
        "tex" : "\\male",
        "color" : BLUE,
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        TexMobject.__init__(self, self.tex, **kwargs)
        self.set_height(self.height)
        self.set_color(self.color)

class Female(Male):
    CONFIG = {
        "tex" : "\\female",
        "color" : MAROON_B,
    }

class PascalsTriangle(VGroup):
    CONFIG = {
        "n_rows" : 9,
        "distance" : 0.8,
        "max_width_to_distance_ratio" : 0.7,
        "angle" : 0.2*np.pi,
    }
    def __init__(self, **kwargs):
        VGroup.__init__(self, **kwargs)

        distance = self.distance
        angle = self.angle
        max_width = self.max_width_to_distance_ratio * distance
        t_down = rotate_vector(distance*DOWN, -angle)
        t_right = 2*distance*np.sin(angle)*RIGHT

        for n in range(self.n_rows):
            row = VGroup()
            for k in range(n+1):
                num = TexMobject(str(choose(n, k)))
                num.shift(n*t_down + k*t_right)
                row.add(num)
            self.add(row)
        self.center()

######################

class ExperienceProblemSolver(PiCreatureScene):
    def construct(self):
        self.add_equation()
        self.jenny_solves()
        self.no_genius()
        self.think_about_patterns()

    def add_equation(self):
        equation = TexMobject(
            "\\frac{x^3 + y^3}{(x+y)^2} + \\frac{3xy}{x+y}"
        )
        equation.to_edge(UP)

        self.play(Write(equation))
        self.wait()

        self.equation = equation

    def jenny_solves(self):
        randy, jenny = self.randy, self.jenny
        jenny_words = TextMobject("It's just $x+y$")
        randy_words = TextMobject("...wait...")
        randy_words.next_to(randy.get_corner(UP+RIGHT), RIGHT)

        self.pi_creature_says(
            jenny, jenny_words, 
            target_mode = "hooray",
            bubble_kwargs = {"height" : 2, "width" : 3}
        )
        self.wait()
        self.play(
            randy.change, "confused", self.equation,
            Write(randy_words)
        )
        self.play(randy.look_at, self.equation.get_left())
        self.play(randy.look_at, jenny.eyes)
        self.play(jenny.change, "happy")
        self.play(randy.change, "tired")
        self.wait()
        self.play(*list(map(FadeOut, [
            jenny.bubble, jenny_words, randy_words
        ])))

    def no_genius(self):
        randy, jenny = self.randy, self.jenny

        lightbulb = Lightbulb()
        lightbulb.next_to(jenny, UP)
        cross = Cross(lightbulb)
        cross.set_stroke(RED, 8)

        self.play(LaggedStartMap(ShowCreation, lightbulb))
        self.play(
            ShowCreation(cross),
            jenny.change, "sassy", cross,
            randy.change, "happy"
        )
        self.wait(2)

        self.to_fade = VGroup(lightbulb, cross)

    def think_about_patterns(self):
        randy, jenny = self.randy, self.jenny
        rows = PascalsTriangle(
            n_rows = 6,
            distance = 0.6,
        )
        rows.scale(0.8)
        for row in rows:
            for num in row:
                n = float(num.get_tex_string())
                num.set_color(interpolate_color(
                    BLUE, YELLOW, n/10.0
                ))

        self.pi_creature_thinks(
            jenny, "",
            bubble_kwargs = {"width" : 5, "height" : 4.2},
            added_anims = [
                FadeOut(self.to_fade),
                FadeOut(self.equation),
                randy.change, "plain"
            ]
        )
        rows.move_to(
            jenny.bubble.get_bubble_center() + \
            MED_SMALL_BUFF*(UP+LEFT)
        )
        self.play(FadeIn(rows[0]))
        for last_row, curr_row in zip(rows, rows[1:]):
            self.play(*[
                Transform(
                    last_row.copy(), VGroup(*mobs),
                    remover = True
                )
                for mobs in (curr_row[1:], curr_row[:-1])
            ])
            self.add(curr_row)
        self.wait(3)




    ############

    def create_pi_creatures(self):
        randy = Randolph()
        randy.to_edge(DOWN)
        randy.shift(4*LEFT)
        jenny = PiCreature(color = BLUE_C).flip()
        jenny.to_edge(DOWN)
        jenny.shift(4*RIGHT)
        self.randy, self.jenny = randy, jenny
        return randy, jenny

class InitialFiveChooseThreeExample(Scene):
    CONFIG = {
        "n" : 5,
        "zero_color" : BLUE,
        "one_color" : PINK,
    }
    def construct(self):
        self.show_all_stacks()
        self.add_title()
        self.show_binomial_name()
        self.issolate_single_stack()
        self.count_chosen_stack()
        self.count_ways_to_fill_slots()
        self.walk_though_notation()
        self.emphasize_pattern_over_number()

    def show_all_stacks(self):
        stacks = get_stacks(
            self.get_obj1(), self.get_obj2(), self.n,
            vertical_buff = SMALL_BUFF
        )
        stacks.to_edge(DOWN, buff = MED_LARGE_BUFF)

        for stack in stacks:
            self.play(FadeIn(
                stack, 
                run_time = 0.2*len(stack),
                lag_ratio = 0.5
            ))
        self.wait()

        self.set_variables_as_attrs(stacks)

    def add_title(self):
        n = self.n
        stacks = self.stacks

        n_choose_k = TexMobject("n \\choose k")
        n_choose_k_words = TextMobject("``n choose k''")
        nCk_group = VGroup(n_choose_k, n_choose_k_words)
        nCk_group.arrange(RIGHT)
        nCk_group.to_edge(UP)

        binomials = VGroup(*[
            TexMobject("%d \\choose %d"%(n, k))
            for k in range(n+1)
        ])
        binomial_equations = VGroup()
        for k, binomial in enumerate(binomials):
            binomial.scale(0.75)
            number = TexMobject(str(choose(n, k)))
            equation = VGroup(binomial, TexMobject("="), number)
            equation.arrange(RIGHT, buff = SMALL_BUFF)
            equation.set_color(YELLOW)
            equation[1].set_color(WHITE)
            binomial_equations.add(equation)

        for stack, eq in zip(stacks, binomial_equations):
            eq.set_width(0.9*stack.get_width())
            eq.next_to(stack, UP)

        mover = VGroup()
        for eq in binomial_equations:
            point = VectorizedPoint(n_choose_k.get_center())
            group = VGroup(n_choose_k, point, point).copy()
            group.target = eq
            mover.add(group)

        self.play(FadeIn(nCk_group))
        self.play(LaggedStartMap(
            MoveToTarget, mover,
            run_time = 3,
        ))
        self.remove(mover)
        self.add(binomial_equations)
        self.wait()

        self.set_variables_as_attrs(
            n_choose_k, n_choose_k_words,
            binomial_equations
        )

    def show_binomial_name(self):
        new_words = TextMobject("``Binomial coefficients''")
        new_words.move_to(self.n_choose_k_words, LEFT)

        self.play(Transform(self.n_choose_k_words, new_words))
        self.wait(2)

    def issolate_single_stack(self):
        stack = self.stacks[3]
        equation = self.binomial_equations[3]

        to_fade = VGroup(*self.stacks)
        to_fade.add(*self.binomial_equations)
        to_fade.add(self.n_choose_k, self.n_choose_k_words)
        to_fade.remove(stack, equation)

        self.play(
            FadeOut(to_fade),
            equation.scale, 1.5, equation.get_bottom(),
        )
        self.wait()
        for line in stack:
            ones = VGroup(*[mob for mob in line if "1" in mob.get_tex_string()])
            line.ones = ones
            self.play(LaggedStartMap(
                ApplyMethod, ones,
                lambda mob : (mob.set_color, YELLOW),
                rate_func = there_and_back,
                lag_ratio = 0.7,
                run_time = 1,
            ))

    def count_chosen_stack(self):
        stack = self.stacks[3]
        for i, line in enumerate(stack):
            number = TexMobject(str(i+1))
            number.next_to(stack, LEFT)
            brace = Brace(VGroup(*stack[:i+1]), LEFT)
            number.next_to(brace, LEFT)
            line.save_state()
            line.set_color(YELLOW)
            self.add(number, brace)
            self.wait(0.25)
            self.remove(number, brace)
            line.restore()
        self.add(number, brace)
        self.wait()

        self.set_variables_as_attrs(
            stack_brace = brace,
            stack_count = number
        )

    def count_ways_to_fill_slots(self):
        lines = VGroup(*[Line(ORIGIN, 0.25*RIGHT) for x in range(5)])
        lines.arrange(RIGHT)
        lines.next_to(self.stacks[3], LEFT, LARGE_BUFF, UP)

        self.play(ShowCreation(lines))
        count = 1
        for indices in it.combinations(list(range(5)), 3):
            ones = VGroup(*[
                self.get_obj1().next_to(lines[i], UP)
                for i in indices
            ])
            num = TexMobject(str(count))
            num.next_to(lines, DOWN)
            self.add(ones, num)
            self.wait(0.35)
            self.remove(ones, num)
            count += 1
        self.add(num, ones)
        self.wait()
        self.play(*list(map(FadeOut, [lines, num, ones])))

    def walk_though_notation(self):
        equation = self.binomial_equations[3]
        rect = SurroundingRectangle(equation[0])
        rect.set_color(WHITE)
        words = TextMobject("``5 choose 3''")
        words.next_to(rect, UP)

        self.play(Write(words))
        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))
        self.wait(2)

    def emphasize_pattern_over_number(self):
        morty = Mortimer().flip()
        morty.to_corner(DOWN+LEFT)
        words = TextMobject("Remember the pattern \\\\ not the number")
        words.next_to(morty, UP)
        words.shift_onto_screen()

        self.play(FadeIn(morty))
        self.play(
            morty.change, "speaking",
            Write(words, run_time = 2)
        )
        self.play(
            Blink(morty),
            morty.change, "happy"
        )
        self.revert_to_original_skipping_status()
        last_ones = VGroup()
        last_ones.save_state()
        for x in range(2):
            for line in self.stacks[3]:
                ones = line.ones
                ones.save_state()
                self.play(
                    ones.set_color, YELLOW,
                    last_ones.restore,
                    morty.look_at, ones,
                    run_time = 0.25
                )
                last_ones = ones
            self.wait()

    ####

    def get_obj1(self):
        return TexMobject("1").set_color(self.one_color)

    def get_obj2(self):
        return TexMobject("0").set_color(self.zero_color)

class SixChooseThreeExample(InitialFiveChooseThreeExample):
    CONFIG = {
        "n" : 6,
        "k" : 3,
        "stack_height" : 7,
    }
    def construct(self):
        self.show_stack()
        self.talk_through_one_line()
        self.count_stack()
        self.think_about_pattern()

    def show_stack(self):
        stack = get_stack(
            self.get_obj1(), self.get_obj2(),
            self.n, self.k,
            vertical_buff = SMALL_BUFF
        )
        stack.set_height(self.stack_height)
        stack.to_edge(DOWN)
        for line in stack:
            line.ones = VGroup(*[mob for mob in line if "1" in mob.get_tex_string()])

        equation = TexMobject(
            "{%d \\choose %d}"%(self.n, self.k),
            "=", str(choose(self.n, self.k))
        )
        equation.set_color(YELLOW)
        equation.set_color_by_tex("=", WHITE)
        equation.next_to(stack, RIGHT, LARGE_BUFF)

        self.add(equation)
        self.play(LaggedStartMap(
            FadeIn, stack,
            lag_ratio = 0.1,
            run_time = 10,
        ))
        self.wait()

        self.set_variables_as_attrs(stack)

    def talk_through_one_line(self):
        line = self.stack[8]
        line.save_state()
        distance = FRAME_X_RADIUS/2

        self.play(line.shift, distance*LEFT)

        brace = Brace(line, UP)
        n_options = TextMobject(str(self.n), "options")
        n_options.set_color_by_tex(str(self.n), YELLOW)
        n_options.next_to(brace, UP)
        arrows = VGroup(*[
            Vector(0.5*UP).next_to(one, DOWN, SMALL_BUFF)
            for one in line.ones
        ])
        arrows.set_color(self.one_color)
        choose_k = TextMobject("Choose", str(self.k), "of them")
        choose_k.set_color_by_tex(str(self.k), YELLOW)
        choose_k.next_to(arrows, DOWN)

        self.play(
            GrowFromCenter(brace),
            Write(n_options),
            run_time = 1
        )
        self.play(
            LaggedStartMap(GrowArrow, arrows),
            Write(choose_k, run_time = 1)
        )
        self.wait(2)
        self.play(
            line.restore,
            *list(map(FadeOut, [brace, n_options, arrows, choose_k]))
        )

    def count_stack(self):
        stack = self.stack
        for i, line in enumerate(stack):
            brace = Brace(VGroup(*stack[:i+1]), LEFT)
            num = TexMobject(str(i+1))
            num.next_to(brace, LEFT)
            line.ones.save_state()
            line.ones.set_color(YELLOW)
            line.ones.set_stroke(RED, 1)
            self.add(brace, num)
            self.wait(0.15)
            self.remove(brace, num)
            line.ones.restore()
        self.add(brace, num)
        self.wait()

        lhs = TexMobject(
            "\\frac{6 \\cdot 5 \\cdot 3}{1 \\cdot 2 \\cdot 3} ="
        )
        lhs.next_to(num, LEFT)
        coming_soon = TextMobject("Coming soon...")
        coming_soon.next_to(lhs, UP)
        coming_soon.set_color(MAROON_B)

        self.play(*list(map(FadeIn, [lhs, coming_soon])))
        self.wait()
        self.play(
            ApplyMethod(
                lhs.shift, 0.65*FRAME_X_RADIUS*(LEFT+UP),
                path_arc = np.pi/2,
                rate_func = running_start,
                remover = True,
            ),
            *list(map(FadeOut, [brace, num, coming_soon]))
        )
        self.wait()

    def think_about_pattern(self):
        self.revert_to_original_skipping_status()
        last_ones = VGroup()
        last_ones.save_state()
        for x in range(2):
            for line in self.stack:
                ones = line.ones
                ones.save_state()
                self.play(
                    ones.set_color, YELLOW,
                    ones.set_stroke, RED, 1,
                    last_ones.restore,
                    run_time = 0.2
                )
                last_ones = ones
        self.wait()

class SixChooseThreeInOtherContext(Scene):
    def construct(self):
        self.add_dots()
        self.count_paths_to_three_three()

    def add_dots(self):
        n = 4
        dots = VGroup(*[Dot() for x in range(n**2)])
        dots.arrange_in_grid(n, n, buff = LARGE_BUFF)
        dots.next_to(ORIGIN, LEFT)
        self.add(dots)

        self.dots = dots
        self.dot_to_dot_distance = get_norm(
            dots[1].get_center() - dots[0].get_center()
        )

    def count_paths_to_three_three(self):
        dots = self.dots
        d = self.dot_to_dot_distance
        lower_left = dots.get_corner(DOWN+LEFT)
        lower_left += dots[0].radius*(UP+RIGHT)

        right = Vector(d*RIGHT, color = PINK)
        up = Vector(d*UP, color = BLUE)

        last_rights = None
        last_ups = None
        last_line = None
        for indices in it.combinations(list(range(6)), 3):
            bools = [i in indices for i in range(6)]
            arrows = VGroup(*[
                right.deepcopy() if b else up.deepcopy()
                for b in bools
            ])
            last_point = np.array(lower_left)
            ups, rights = VGroup(), VGroup()
            for arrow, b in zip(arrows, bools):
                arrow.shift(last_point - arrow.get_start())
                last_point = arrow.get_end()
                group = rights if b else ups
                group.add(arrow)

            line = VGroup(*[arrow.tip.copy() for arrow in arrows])
            line.arrange(RIGHT, buff = 0.5*SMALL_BUFF)
            if last_line is None:
                line.shift(FRAME_X_RADIUS*RIGHT/2)
                line.to_edge(UP)
                self.play(
                    ShowCreation(arrows),
                    ShowCreation(line)
                )
            else:
                line.next_to(last_line, DOWN, SMALL_BUFF)
                self.play(
                    FadeIn(line),
                    ReplacementTransform(last_rights, rights),
                    ReplacementTransform(last_ups, ups),
                )
            last_rights = rights
            last_ups = ups
            last_line = line
        self.wait()

# class Introduction(Scene):
#     CONFIG = {
#         "start_n" : 4,
#     }
#     def construct(self):
#         self.write_n_choose_k()
#         self.show_binomial_coefficients()
#         self.perform_shift()

#     def write_n_choose_k(self):
#         symbol = TexMobject("n \\choose k")
#         words = TextMobject("``n choose k''")
#         group = VGroup(symbol, words)
#         group.arrange(RIGHT)

#         self.play(
#             FadeIn(symbol),
#             Write(words)
#         )
#         self.wait()

#         self.set_variables_as_attrs(n_choose_k_group = group)

#     def show_binomial_coefficients(self):
#         n = self.start_n
#         n_choose_k, n_choose_k_words = self.n_choose_k_group
#         binomials = VGroup(*[
#             TexMobject("%d \\choose %d"%(n, k))
#             for k in range(n+1)
#         ])
#         binomial_equations = VGroup()
#         for k, binomial in enumerate(binomials):
#             binomial.scale(0.75)
#             number = TexMobject(str(choose(n, k)))
#             equation = VGroup(binomial, TexMobject("="), number)
#             equation.arrange(RIGHT, buff = SMALL_BUFF)
#             equation.set_color(YELLOW)
#             equation[1].set_color(WHITE)
#             binomial_equations.add(equation)
#         new_words = TextMobject("``Binomial coefficients''")

#         stacks = get_stacks(
#             TexMobject("x").set_color(BLUE),
#             TexMobject("y").set_color(RED),
#             n
#         )
#         stacks.to_edge(DOWN, buff = LARGE_BUFF)
#         for stack, eq in zip(stacks, binomial_equations):
#             eq.set_width(0.9*stack.get_width())
#             eq.next_to(stack, UP)

#         self.play(
#             FadeIn(stacks, run_time = 2, lag_ratio = 0.5),
#             self.n_choose_k_group.to_edge, UP
#         )
#         new_words.move_to(n_choose_k_words, LEFT)
#         self.play(Transform(n_choose_k_words, new_words))
#         for eq in binomial_equations:
#             point = VectorizedPoint(n_choose_k.get_center())
#             self.play(ReplacementTransform(
#                 VGroup(n_choose_k, point, point).copy(),
#                 eq
#             ))
#             self.wait()

#         self.set_variables_as_attrs(stacks, binomial_equations)

#     def perform_shift(self):
#         n = self.start_n
#         to_fade = VGroup(
#             self.n_choose_k_group,
#             self.binomial_equations
#         )
#         stacks = self.stacks
#         top_stacks = stacks.copy()
#         top_stacks.to_edge(UP, buff = MED_SMALL_BUFF)

#         line = Line(LEFT, RIGHT, color = WHITE)
#         line.scale(FRAME_X_RADIUS)
#         line.next_to(top_stacks, DOWN)

#         x = TexMobject("x").set_color(BLUE)
#         y = TexMobject("y").set_color(RED)
#         add_x, add_y = [
#             TextMobject("Prepend", "$%s$"%s).set_color_by_tex(s, color)
#             for s, color in ("x", BLUE), ("y", RED)
#         ]
#         add_x.to_corner(UP+LEFT)
#         add_y.to_edge(LEFT).shift(MED_SMALL_BUFF*DOWN)

#         new_stacks, new_top_stacks = [
#             get_stacks(x, y, n, fixed_start = var)
#             for var in y, x
#         ]
#         new_top_stacks.to_edge(UP, buff = MED_SMALL_BUFF)
#         new_stacks.to_edge(DOWN)
#         for s in new_stacks, new_top_stacks:
#             s.start_terms = VGroup()
#             for stack in s:
#                 for term in stack:
#                     s.start_terms.add(term[0])

#         s_to_s_distance = \
#             new_stacks[1].get_center()[0] - \
#             new_stacks[0].get_center()[0]

#         self.play(
#             FadeOut(to_fade),
#             stacks.to_edge, DOWN,
#             ReplacementTransform(stacks.copy(), top_stacks),
#         )
#         self.play(ShowCreation(line))
#         self.play(Write(add_x, run_time = 1))
#         self.play(Transform(top_stacks, new_top_stacks))
#         self.play(LaggedStartMap(
#             Indicate, new_top_stacks.start_terms,
#             rate_func = there_and_back,
#             run_time = 1,
#             remover = True
#         ))
#         self.wait()
#         self.play(Write(add_y, run_time = 1))
#         self.play(Transform(stacks, new_stacks))
#         self.play(LaggedStartMap(
#             Indicate, new_stacks.start_terms,
#             rate_func = there_and_back,
#             run_time = 1,
#             remover = True
#         ))
#         self.wait()

#         self.play(
#             top_stacks.shift, s_to_s_distance*RIGHT/2,
#             stacks.shift, s_to_s_distance*LEFT/2,
#         )
#         self.play(*map(FadeOut, [add_x, add_y, line]))

#         point = VectorizedPoint()
#         point.move_to(top_stacks[0].get_bottom())
#         point.shift(s_to_s_distance*LEFT)
#         top_stacks.add_to_back(point)

#         point = VectorizedPoint()
#         point.move_to(stacks[-1].get_bottom())
#         point.shift(s_to_s_distance*RIGHT)
#         point.shift(MED_SMALL_BUFF*DOWN)
#         stacks.add(point)

#         for k, stack, top_stack in zip(it.count(), stacks, top_stacks):
#             top_stack.generate_target()
#             top_stack.target.next_to(stack, UP, MED_SMALL_BUFF)
#             # term = TexMobject(
#             #     str(choose(n+1, k)),
#             #     "x^%d"%(n+1-k),
#             #     "y^%d"%k
#             # )
#             term = TexMobject(
#                 "{%d \\choose %d}"%(n+1, k),
#                 "=",
#                 str(choose(n+1, k))
#             )
#             term[0].scale(0.85, about_point = term[0].get_right())
#             term[0].set_color(YELLOW)
#             term[2].set_color(YELLOW)
#             term.scale(0.85)
#             term.next_to(top_stack.target, UP)

#             self.play(MoveToTarget(top_stack))
#             self.play(Write(term))
#         self.wait()

# class DifferentWaysToThinkAboutNChooseK(Scene):
#     CONFIG = {
#         "n" : 5,
#         "k" : 3,
#         "stack_height" : 5,
#     }
#     def construct(self):
#         self.add_n_choose_k_term()
#         self.add_stack()
#         self.choose_k()
#         self.split_stack_by_start()
#         self.split_choices_by_start()

#     def add_n_choose_k_term(self):
#         term = TexMobject("{5 \\choose 3} = 10")
#         term.to_edge(UP)
#         self.play(FadeIn(term, lag_ratio = 0.5))
#         self.wait()

#         self.n_choose_k_term = term

#     def add_stack(self):
#         n, k = self.n, self.k
#         x = TexMobject("x").set_color(BLUE)
#         y = TexMobject("y").set_color(RED)
#         stack = get_stack(x, y, n, k)
#         stack.set_height(self.stack_height)
#         stack.shift(FRAME_X_RADIUS*LEFT/2)
#         stack.to_edge(DOWN)
#         numbers = VGroup(*[
#             TexMobject("%d"%(d+1))
#             for d in range(choose(n, k))
#         ])
#         numbers.next_to(stack, UP)

#         last_number = None
#         for term, number in zip(stack, numbers):
#             self.add(term, number)
#             if last_number:
#                 self.remove(last_number)
#             self.wait(0.25)
#             last_number = number
#         self.wait()

#         self.stack = stack
#         self.stack_count = last_number
#         self.numbers = numbers

#     def choose_k(self):
#         n, k = self.n, self.k

#         letter_set = TexMobject(
#             "(",
#             "A", ",", 
#             "B", ",",
#             "C", ",",
#             "D", ",",
#             "E", ")"
#         )
#         letters = VGroup(*letter_set[1::2])
#         letter_set.shift(FRAME_X_RADIUS*RIGHT/2)
#         letter_set.to_edge(UP)

#         letter_subsets = list(it.combinations(letters, k))
#         subset_mobs = VGroup(*[
#             VGroup(*letter_subset).copy().arrange(
#                 RIGHT, buff = SMALL_BUFF
#             )
#             for letter_subset in letter_subsets
#         ]).arrange(DOWN, buff = MED_SMALL_BUFF)
#         subset_mobs.set_height(self.stack_height)
#         subset_mobs.shift(FRAME_X_RADIUS*RIGHT/2)
#         subset_mobs.to_edge(DOWN)

#         choose_words = TextMobject("Choose %d"%k)
#         choose_words.scale(0.9)
#         choose_words.next_to(letter_set, DOWN)
#         choose_words.set_color(YELLOW)

#         self.revert_to_original_skipping_status()
#         self.play(Write(letter_set, run_time = 1))
#         self.play(
#             Write(choose_words, run_time = 1),
#             LaggedStartMap(FadeIn, subset_mobs)
#         )
#         self.wait()
#         for subset, subset_mob in zip(letter_subsets, subset_mobs):
#             VGroup(subset_mob, *subset).set_color(BLUE)
#             self.wait(0.5)
#             VGroup(*subset).set_color(WHITE)
#         self.wait()

#         self.set_variables_as_attrs(
#             subset_mobs, letter_set, choose_words,
#         )

#     def split_stack_by_start(self):
#         n, k = self.n, self.k
#         stack = self.stack
#         stack_count = self.stack_count

#         top_num = choose(n-1, k-1)
#         top_stack = VGroup(*stack[:top_num])
#         bottom_stack = VGroup(*stack[top_num:])

#         self.play(
#             FadeOut(stack_count),
#             top_stack.shift, UP
#         )
#         for stack, new_k in (top_stack, k-1), (bottom_stack, k):
#             brace = Brace(stack, RIGHT)
#             brace_tex = brace.get_tex(
#                 "{%d \\choose %d} = %d"%(n-1, new_k, choose(n-1, new_k))
#             )
#             rect = SurroundingRectangle(VGroup(*[
#                 VGroup(*term[1:])
#                 for term in stack
#             ]), buff = 0.5*SMALL_BUFF)
#             rect.set_stroke(WHITE, 2)
#             self.play(
#                 GrowFromCenter(brace),
#                 Write(brace_tex),
#                 ShowCreation(rect)
#             )
#             self.wait()

#     def split_choices_by_start(self):
#         subset_mobs = self.subset_mobs
#         subset_mobs.generate_target()
#         subset_mobs.target.shift(LEFT)
#         brace = Brace(subset_mobs.target, RIGHT)
#         expression = brace.get_tex(
#             "\\frac{5 \\cdot 4 \\cdot 3}{1 \\cdot 2 \\cdot 3}",
#             "= 10"
#         )

#         self.play(
#             MoveToTarget(subset_mobs),
#             GrowFromCenter(brace)
#         )
#         self.play(Write(expression))
#         self.wait()

# class FormulaVsPattern(TeacherStudentsScene):
#     def construct(self):
#         self.show_formula()
#         self.show_pattern()

#     def show_formula(self):
#         formula = TexMobject(
#             "{n \\choose k} = {n! \\over (n-k)!k!}", 
#         )
#         for i in 1, 5, 9:
#             formula[i].set_color(BLUE)
#         for i in 2, 11, 14:
#             formula[i].set_color(YELLOW)

#         self.student_thinks(formula, student_index = 1)
#         self.play(self.teacher.change, "sassy")
#         self.wait(2)
#         self.play(
#             FadeOut(self.students[1].bubble),
#             FadeOut(formula),
#             self.teacher.change, "raise_right_hand",
#             self.get_student_changes(*["pondering"]*3)
#         )

#     def show_pattern(self):
#         words = TextMobject(
#             "What is the \\\\ probability of a flush?"
#         )
#         values = random.sample(PlayingCard.CONFIG["possible_values"], 5)
#         cards = VGroup(*[
#             PlayingCard(value = value, suit = "hearts")
#             for value in values
#         ])
#         cards.arrange(RIGHT)
#         cards.to_corner(UP+RIGHT)
#         words.next_to(cards, LEFT)
#         words.shift_onto_screen()

#         self.play(LaggedStartMap(DrawBorderThenFill, cards))
#         self.play(Write(words))
#         self.wait(3)

class ProbabilityOfKWomenInGroupOfFive(Scene):
    CONFIG = {
        "random_seed" : 0,
        "n_people_per_lineup" : 5,
        "n_examples" : 18,
        "item_line_width" : 0.4,
    }
    def construct(self):
        self.ask_question()
        self.show_all_possibilities()
        self.stack_all_choices_by_number_of_women()
        self.go_through_stacks()
        self.remember_this_sensation()
        self.show_answer_to_question()
        self.ask_about_pattern()

    def ask_question(self):
        title = TextMobject("5 randomly chosen people")
        title.to_edge(UP)
        self.add(title)

        lineup_point = 1.5*UP
        prob_words = VGroup(*[
            TextMobject(
                "Probability of", str(n), "women?"
            ).set_color_by_tex(str(n), YELLOW)
            for n in range(self.n_people_per_lineup+1)
        ])
        prob_words.arrange(DOWN)
        prob_words.next_to(lineup_point, DOWN, MED_LARGE_BUFF)

        def get_lineup():
            lineup = self.get_random_lineup_of_men_and_women()
            lineup.scale(1.5)
            lineup.move_to(lineup_point, DOWN)
            return lineup

        last_lineup = get_lineup()
        self.play(LaggedStartMap(FadeIn, last_lineup, run_time = 1))

        for x in range(self.n_examples):
            lineup = get_lineup()
            anims = [last_lineup.items.fade, 1]
            anims += list(map(GrowFromCenter, lineup.items))
            if x >= 12 and x-12 < len(prob_words):
                anims.append(FadeIn(prob_words[x-12]))
            self.play(*anims, run_time = 0.75)
            self.remove(last_lineup)
            self.add(lineup)
            self.wait(0.25)
            last_lineup = lineup

        self.title = title
        self.prob_words = prob_words
        self.lineup = last_lineup

    def show_all_possibilities(self):
        man, woman = Male(), Female()

        vects = [
            1.5*UP,
            0.65*UP,
            0.25*UP,
            3.5*RIGHT,
            1.5*RIGHT,
        ]
        lineup_groups = VGroup()
        for k in range(6):
            lineup_group = VGroup()
            for tup in it.product(*[[woman, man]]*k):
                lineup = self.get_lineup(*list(tup) + (5-k)*[None])
                lineup.scale(1.4*(0.9)**k)
                lineup.move_to(0.5*DOWN)
                for mob, vect in zip(tup, vects):
                    if mob is woman:
                        lineup.shift(vect)
                    else:
                        lineup.shift(-vect)
                lineup_group.add(lineup)
            lineup_groups.add(lineup_group)

        n_possibilities = TexMobject(
            "2 \\cdot", "2 \\cdot", "2 \\cdot", "2 \\cdot", "2",
            "\\text{ Possibilities}"
        )
        n_possibilities.next_to(self.title, DOWN)
        twos = VGroup(*n_possibilities[-2::-1])
        twos.set_color(YELLOW)
        two_anims = [
            ReplacementTransform(
                VectorizedPoint(twos[0].get_center()), 
                twos[0]
            )
        ] + [
            ReplacementTransform(t1.copy(), t2)
            for t1, t2 in zip(twos, twos[1:])
        ]

        curr_lineup_group = lineup_groups[0]
        self.play(
            ReplacementTransform(self.lineup, curr_lineup_group[0]),
            FadeOut(self.prob_words)
        )
        for i, lineup_group in enumerate(lineup_groups[1:]):
            anims = [ReplacementTransform(curr_lineup_group, lineup_group)]
            anims += two_anims[:i+1]
            if i == 0:
                anims.append(FadeIn(n_possibilities[-1]))
            self.remove(twos)
            self.play(*anims)

            men, women = VGroup(), VGroup()
            for lineup in lineup_group:
                item = lineup.items[i]
                if "female" in item.get_tex_string():
                    women.add(item)
                else:
                    men.add(item)
            for group in men, women:
                self.play(LaggedStartMap(
                    ApplyMethod, group,
                    lambda m : (m.shift, MED_SMALL_BUFF*RIGHT),
                    rate_func = there_and_back,
                    lag_ratio = 0.9**i,
                    run_time = 1,
                ))
            self.wait()
            curr_lineup_group = lineup_group
        self.lineups = curr_lineup_group

        eq_32 = TexMobject("=", "32")
        eq_32.move_to(twos.get_right())
        eq_32.set_color_by_tex("32", YELLOW)
        self.play(
            n_possibilities[-1].next_to, eq_32, RIGHT,
            twos.next_to, eq_32, LEFT,
            FadeIn(eq_32),
        )
        self.wait()

        n_possibilities.add(*eq_32)
        self.set_variables_as_attrs(n_possibilities)

    def stack_all_choices_by_number_of_women(self):
        lineups = self.lineups
        stacks = VGroup(*[VGroup() for x in range(6)])
        for lineup in lineups:
            lineup.women = VGroup(*[m for m in lineup.items if "female" in m.get_tex_string()])
            stacks[len(lineup.women)].add(lineup)
        stacks.generate_target()
        stacks.target.scale(0.75)
        for stack in stacks.target:
            stack.arrange(DOWN, buff = 1.5*SMALL_BUFF)
        stacks.target.arrange(
            RIGHT, buff = MED_LARGE_BUFF, aligned_edge = DOWN
        )
        stacks.target.to_edge(DOWN)

        self.play(MoveToTarget(
            stacks, 
            run_time = 2,
            path_arc = np.pi/2
        ))
        self.wait()

        self.stacks = stacks

    def go_through_stacks(self):
        stacks = self.stacks
        n = len(stacks) - 1
        equations = VGroup()
        for k, stack in enumerate(stacks):
            items = VGroup()
            lines = VGroup()
            women = VGroup()
            for lineup in stack:
                items.add(lineup.items)
                lines.add(lineup.lines)
                for item in lineup.items:
                    if "female" in item.get_tex_string():
                        women.add(item)
            equation = TexMobject(
                "{%d \\choose %d}"%(n, k),
                "=",
                str(len(stack))
            )
            equation[0].scale_in_place(0.6)
            equation.arrange(RIGHT, SMALL_BUFF)
            equation.set_color(YELLOW)
            equation.set_color_by_tex("=", WHITE)
            equation.next_to(stack, UP)
            equations.add(equation)

            self.play(
                items.set_fill, None, 1,
                lines.set_stroke, WHITE, 3,
                Write(equation, run_time = 1)
            )
            self.play(LaggedStartMap(Indicate, women, rate_func = there_and_back))
        self.wait()

        self.equations = equations
        self.numbers = VGroup(*[eq[-1] for eq in equations])

    def remember_this_sensation(self):
        n_possibilities = self.n_possibilities
        n_possibilities_rect = SurroundingRectangle(n_possibilities)
        twos = VGroup(*n_possibilities[:5])
        numbers = self.numbers

        self.play(ShowCreation(n_possibilities_rect))
        self.play(LaggedStartMap(
            Indicate, twos, 
            rate_func = wiggle
        ))
        self.play(FadeOut(n_possibilities_rect))
        for number in numbers:
            self.play(Indicate(number, color = PINK, run_time = 0.5))
        self.wait()

    def show_answer_to_question(self):
        stacks = self.stacks
        numbers = self.numbers
        n_possibilities = VGroup(
            self.n_possibilities[-1],
            self.n_possibilities[-3]
        )
        n_possibilities_part_to_fade = VGroup(
            self.n_possibilities[-2],
            *self.n_possibilities[:-3]
        )
        total = n_possibilities[-1]
        title = self.title
        n = self.n_people_per_lineup

        self.play(
            FadeOut(title),
            FadeOut(n_possibilities_part_to_fade),
            n_possibilities.to_corner, UP+RIGHT
        )
        for k, stack, num in zip(it.count(), stacks, numbers):
            rect = SurroundingRectangle(stack)
            num.save_state()
            prob_words = TexMobject(
                "P(", "\\#", "\\female", "=", str(k), ")"
                "=", "{\\quad \\over", "32}",
                "\\approx", "%0.3f"%(choose(n, k)/32.0)
            )
            prob_words.set_color_by_tex_to_color_map({
                "female" : MAROON_B,
                "32" : YELLOW,
            })
            frac_line = prob_words.get_parts_by_tex("over")
            prob_words.to_corner(UP+LEFT)

            self.play(
                num.next_to, frac_line, UP, SMALL_BUFF,
                FadeIn(prob_words)
            )
            self.play(ShowCreation(rect))
            self.wait(2)
            self.play(
                num.restore,
                FadeOut(rect),
                FadeOut(prob_words)
            )

    def ask_about_pattern(self):
        question = TextMobject("Where do these \\\\ numbers come from?")
        question.to_edge(UP)
        numbers = self.numbers
        circles = VGroup(*[
            Circle().replace(num, dim_to_match = 1).scale_in_place(1.5)
            for num in numbers
        ])
        circles.set_color(WHITE)

        self.play(LaggedStartMap(FadeIn, question))
        self.play(LaggedStartMap(ShowCreationThenDestruction, circles))
        self.wait(2)

    ######

    def get_random_lineup_of_men_and_women(self):
        man, woman = Male(), Female()
        lineup = self.get_lineup(*[
            woman if random.choice([True, False]) else man
            for y in range(self.n_people_per_lineup)
        ])
        return lineup

    def get_lineup(self, *mobjects, **kwargs):
        buff = kwargs.get("buff", MED_SMALL_BUFF)
        lines = VGroup(*[
            Line(ORIGIN, self.item_line_width*RIGHT)
            for mob in mobjects
        ])
        lines.arrange(RIGHT, buff = buff)
        items = VGroup()
        for line, mob in zip(lines, mobjects):
            item = VectorizedPoint() if mob is None else mob.copy()
            item.next_to(line, UP, SMALL_BUFF)
            items.add(item)
        result = VGroup(lines, items)
        result.lines = lines
        result.items = items
        return result

class AskAboutAllPossibilities(ProbabilityOfKWomenInGroupOfFive):
    def construct(self):
        man, woman = Male(), Female()
        all_lineups = VGroup()
        for bits in it.product(*[[False, True]]*5):
            mobs = [
                woman.copy() if bit else man.copy()
                for bit in bits
            ]
            all_lineups.add(self.get_lineup(*mobs))
        brace = Brace(all_lineups, UP)
        question = brace.get_text("What are all possibilities?")

        self.add(brace, question)
        for lineup in all_lineups:
            self.add(lineup)
            self.wait(0.25)
            self.remove(lineup)

class RememberThisSensation(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("Remember this \\\\ sensation")
        self.change_student_modes("confused", "pondering", "erm")
        self.wait(2)

class TeacherHoldingSomething(TeacherStudentsScene):
    def construct(self):
        self.play(
            self.teacher.change, "raise_right_hand",
        )
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = 2*UP+2*RIGHT
        )
        self.wait(6)

# class GroupsOf6(Scene):
#     def construct(self):
#         title = TexMobject("2^6 =", "64", "\\text{ Possibilities}")
#         title.to_edge(UP, buff = MED_SMALL_BUFF)
#         title.set_color_by_tex("64", YELLOW)
#         man, woman = Male(), Female()
#         stacks = get_stacks(man, woman, 6, vertical_buff = SMALL_BUFF)
#         stacks.set_height(6.25)
#         stacks.to_edge(DOWN, buff = MED_SMALL_BUFF)
#         women_groups = VGroup()
#         for stack in stacks:
#             for lineup in stack:
#                 group = VGroup()
#                 for item in lineup:
#                     if "female" in item.get_tex_string():
#                         group.add(item)
#                 women_groups.add(group)

#         numbers = VGroup()
#         for stack in stacks:
#             number = TexMobject(str(len(stack)))
#             number.next_to(stack, UP, SMALL_BUFF)
#             numbers.add(number)

#         self.add(title)
#         self.play(LaggedStartMap(
#             LaggedStartMap, stacks,
#             lambda s : (FadeIn, s),
#             run_time = 3,
#         ))
#         self.play(Write(numbers, run_time = 3))
#         self.wait()
#         self.play(LaggedStartMap(
#             ApplyMethod, women_groups,
#             lambda m : (m.set_color, PINK),
#             lag_ratio = 0.1,
#             rate_func = wiggle,
#             run_time = 6,
#         ))

# class GroupsOf7(Scene):
#     def construct(self):
#         stack = get_stack(Male(), Female(), 7, 3)
#         question = TextMobject(
#             "How many groups \\\\ of 7 with 3 ", "$\\female$", "?"
#         )
#         question.set_color_by_tex("female", MAROON_B)
#         question.shift(1.5*UP)

#         self.add(question)
#         for n, item in enumerate(stack):
#             item.center()
#             number = TexMobject(str(n))
#             number.next_to(ORIGIN, DOWN, LARGE_BUFF)
#             self.add(item, number)
#             self.wait(0.2)
#             self.remove(item, number)
#         self.add(item, number)
#         self.wait(2)

class BuildFiveFromFour(ProbabilityOfKWomenInGroupOfFive):
    def construct(self):
        self.show_all_configurations_of_four()
        self.organize_into_stacks()
        self.walk_through_stacks()
        self.split_into_two_possibilities()
        self.combine_stacks()

    def show_all_configurations_of_four(self):
        man, woman = Male(), Female()
        n = 4
        vects = [
            1.5*UP,
            0.5*UP,
            3.5*RIGHT,
            1.5*RIGHT,
        ]
        lineup_groups = VGroup()
        for k in range(n+1):
            lineup_group = VGroup()
            for tup in it.product(*[[man, woman]]*k):
                lineup = self.get_lineup(*list(tup) + (n-k)*[None])
                lineup.scale(1.4*(0.9)**k)
                lineup.move_to(0.5*DOWN)
                for mob, vect in zip(tup, vects):
                    if mob is woman:
                        lineup.shift(vect)
                    else:
                        lineup.shift(-vect)
                lineup_group.add(lineup)
            lineup_groups.add(lineup_group)

        n_possibilities = TexMobject(
            "2 \\cdot", "2 \\cdot", "2 \\cdot", "2",
            "\\text{ Possibilities}"
        )
        n_possibilities.to_edge(UP)
        twos = VGroup(*n_possibilities[-2::-1])
        two_anims = [
            ReplacementTransform(
                VectorizedPoint(twos[0].get_center()), 
                twos[0]
            )
        ] + [
            ReplacementTransform(t1.copy(), t2)
            for t1, t2 in zip(twos, twos[1:])
        ]

        curr_lineup_group = lineup_groups[0]
        self.play(
            ShowCreation(curr_lineup_group[0]),
        )
        for i, lineup_group in enumerate(lineup_groups[1:]):
            anims = [ReplacementTransform(curr_lineup_group, lineup_group)]
            anims += two_anims[:i+1]
            if i == 0:
                anims.append(FadeIn(n_possibilities[-1]))
            self.remove(twos)
            self.play(*anims)
            self.wait()
            curr_lineup_group = lineup_group
        self.lineups = curr_lineup_group

        eq_16 = TexMobject("=", "16")
        eq_16.move_to(twos.get_right())
        eq_16.set_color_by_tex("16", YELLOW)
        self.play(
            n_possibilities[-1].next_to, eq_16, RIGHT,
            twos.next_to, eq_16, LEFT,
            FadeIn(eq_16),
        )
        self.wait()

        n_possibilities.add(eq_16)
        self.n_possibilities = n_possibilities

    def organize_into_stacks(self):
        lineups = self.lineups
        stacks = VGroup(*[VGroup() for x in range(5)])
        for lineup in lineups:
            women = [m for m in lineup.items if "female" in m.get_tex_string()]
            stacks[len(women)].add(lineup)
        stacks.generate_target()
        stacks.target.scale(0.75)
        for stack in stacks.target:
            stack.arrange(DOWN, buff = SMALL_BUFF)
        stacks.target.arrange(
            RIGHT, buff = MED_LARGE_BUFF, aligned_edge = DOWN
        )
        stacks.target.to_edge(DOWN, buff = MED_SMALL_BUFF)

        self.play(MoveToTarget(
            stacks, 
            run_time = 2,
            path_arc = np.pi/2
        ))
        self.wait()

        self.stacks = stacks

    def walk_through_stacks(self):
        stacks = self.stacks
        numbers = VGroup()

        for stack in stacks:
            rect = SurroundingRectangle(stack)
            rect.set_stroke(WHITE, 2)
            self.play(ShowCreation(rect))
            for n, lineup in enumerate(stack):
                lineup_copy = lineup.copy()
                lineup_copy.set_color(YELLOW)
                number = TexMobject(str(n+1))
                number.next_to(stack, UP)
                self.add(lineup_copy, number)
                self.wait(0.25)
                self.remove(lineup_copy, number)
            self.add(number)
            numbers.add(number)
            self.play(FadeOut(rect))
        self.wait()

        stacks.numbers = numbers

    def split_into_two_possibilities(self):
        bottom_stacks = self.stacks
        top_stacks = bottom_stacks.deepcopy()
        top_group = VGroup(top_stacks, top_stacks.numbers)

        h_line = DashedLine(FRAME_X_RADIUS*LEFT, FRAME_X_RADIUS*RIGHT)

        #Initial split
        self.play(
            FadeOut(self.n_possibilities),
            top_group.to_edge, UP, MED_SMALL_BUFF,
        )
        self.play(ShowCreation(h_line))

        #Add extra slot
        for stacks, sym in (top_stacks, Female()), (bottom_stacks, Male()):
            sym.set_fill(opacity = 0)
            new_stacks = VGroup()
            to_fade_in = VGroup()
            for stack in stacks:
                new_stack = VGroup()
                for lineup in stack:
                    new_lineup = self.get_lineup(*[
                        Female() if "female" in item.get_tex_string() else Male()
                        for item in lineup.items
                    ] + [sym], buff = SMALL_BUFF)
                    new_lineup.replace(lineup, dim_to_match = 1)
                    new_stack.add(new_lineup)
                    for group in lineup.items, lineup.lines:
                        point = VectorizedPoint(group[-1].get_center())
                        group.add(point)
                    to_fade_in.add(lineup.items[-1])
                new_stacks.add(new_stack)
            new_stacks.arrange(
                RIGHT, buff = MED_LARGE_BUFF, aligned_edge = DOWN
            )
            new_stacks.move_to(stacks, DOWN)
            stacks.target = new_stacks
            stacks.to_fade_in = to_fade_in

            stacks.numbers.generate_target()
            for number, stack in zip(stacks.numbers.target, new_stacks):
                number.next_to(stack, UP)

        for stacks in top_stacks, bottom_stacks:
            self.play(
                MoveToTarget(stacks),
                MoveToTarget(stacks.numbers)
            )
        self.wait()

        #Fill extra slot
        add_man = TextMobject("Add", "$\\male$")
        add_man.set_color_by_tex("male", BLUE)
        add_woman = TextMobject("Add", "$\\female$")
        add_woman.set_color_by_tex("female", MAROON_B)

        add_man.next_to(ORIGIN, DOWN).to_edge(LEFT)
        add_woman.to_corner(UP+LEFT)

        for stacks, words in (bottom_stacks, add_man), (top_stacks, add_woman):
            to_fade_in = stacks.to_fade_in
            to_fade_in.set_fill(opacity = 1)
            to_fade_in.save_state()
            Transform(to_fade_in, VGroup(words[-1])).update(1)

            self.play(Write(words, run_time = 1))
            self.play(to_fade_in.restore)
            self.wait()

        #Perform shift
        dist = top_stacks[1].get_center()[0] - top_stacks[0].get_center()[0]
        self.play(
            top_stacks.shift, dist*RIGHT/2,
            top_stacks.numbers.shift, dist*RIGHT/2,
            bottom_stacks.shift, dist*LEFT/2,
            bottom_stacks.numbers.shift, dist*LEFT/2,
        )
        self.wait()
        self.play(*list(map(FadeOut, [add_man, add_woman, h_line])))

        self.set_variables_as_attrs(top_stacks, bottom_stacks)

    def combine_stacks(self):
        top_stacks = self.top_stacks
        bottom_stacks = self.bottom_stacks

        rects = VGroup()
        for stacks, color in (top_stacks, MAROON_C), (bottom_stacks, BLUE_D):
            for stack in stacks:
                rect = SurroundingRectangle(stack)
                rect.set_stroke(color, 2)
                rects.add(rect)
                stack.add(rect)

        new_numbers = VGroup()

        self.play(LaggedStartMap(ShowCreation, rects, run_time = 1))
        for i, top_stack in enumerate(top_stacks[:-1]):
            bottom_stack = bottom_stacks[i+1]
            top_number = top_stacks.numbers[i]
            bottom_number = bottom_stacks.numbers[i+1]
            movers = top_stack, top_number, bottom_number
            for mob in movers:
                mob.generate_target()
            top_stack.target.move_to(bottom_stack.get_top(), DOWN)
            plus = TexMobject("+")
            expr = VGroup(top_number.target, plus, bottom_number.target)
            expr.arrange(RIGHT, buff = SMALL_BUFF)
            expr.next_to(top_stack.target.get_top(), UP)

            new_number = TexMobject(str(
                len(top_stack) + len(bottom_stack) - 2
            ))
            new_number.next_to(expr, UP)
            new_numbers.add(new_number)

            self.play(
                Write(plus),
                *list(map(MoveToTarget, movers))
            )
        self.play(
            VGroup(top_stacks[-1], top_stacks.numbers[-1]).align_to,
            bottom_stacks, DOWN
        )
        self.wait()

        new_numbers.add_to_back(bottom_stacks.numbers[0].copy())
        new_numbers.add(top_stacks.numbers[-1].copy())
        new_numbers.set_color(PINK)
        self.play(Write(new_numbers, run_time = 3))
        self.wait()

class BuildUpFromStart(Scene):
    CONFIG = {
        "n_iterations" : 7,
    }
    def construct(self):
        stacks = VGroup(VGroup(Male()), VGroup(Female()))
        stacks.arrange(RIGHT, buff = LARGE_BUFF)
        stacks.numbers = self.get_numbers(stacks)

        max_width = FRAME_WIDTH - 3
        max_height = FRAME_Y_RADIUS - 1

        self.add(stacks, stacks.numbers)
        for x in range(self.n_iterations):
            if x < 2:
                wait_time = 1
            else:
                wait_time = 0.2
            #Divide
            low_stacks = stacks
            low_group = VGroup(low_stacks, low_stacks.numbers)
            top_stacks = stacks.deepcopy()
            top_group = VGroup(top_stacks, top_stacks.numbers)
            for group, vect in (top_group, UP), (low_group, DOWN):
                group.generate_target()
                if group[0].get_height() > max_height:
                    group.target[0].stretch_to_fit_height(max_height)
                    for stack, num in zip(*group.target):
                        num.next_to(stack, UP)
                group.target.next_to(ORIGIN, vect)
            self.play(*list(map(MoveToTarget, [top_group, low_group])))
            self.wait(wait_time)

            #Expand
            for stacks, i in (low_stacks, 0), (top_stacks, -1):
                sym = stacks[i][i][i]
                new_stacks = VGroup()
                for stack in stacks:
                    new_stack = VGroup()
                    for line in stack:
                        new_line = line.copy()
                        new_sym = sym.copy()
                        buff = 0.3*line.get_height()
                        new_sym.next_to(line, RIGHT, buff = buff)
                        new_line.add(new_sym)
                        line.add(VectorizedPoint(line[-1].get_center()))
                        new_stack.add(new_line)
                    new_stacks.add(new_stack)
                new_stacks.arrange(
                    RIGHT, buff = LARGE_BUFF, aligned_edge = DOWN
                )
                if new_stacks.get_width() > max_width:
                    new_stacks.stretch_to_fit_width(max_width)
                if new_stacks.get_height() > max_height:
                    new_stacks.stretch_to_fit_height(max_height)
                new_stacks.move_to(stacks, DOWN)
                stacks.target = new_stacks
                stacks.numbers.generate_target()

                for num, stack in zip(stacks.numbers.target, new_stacks):
                    num.next_to(stack, UP)
            self.play(*list(map(MoveToTarget, [
                top_stacks, low_stacks,
                top_stacks.numbers, low_stacks.numbers,
            ])))
            self.wait(wait_time)

            #Shift
            dist = top_stacks[1].get_center()[0] - top_stacks[0].get_center()[0]
            self.play(
                top_group.shift, dist*RIGHT/2,
                low_group.shift, dist*LEFT/2,
            )
            self.wait(wait_time)

            #Stack
            all_movers = VGroup()
            plusses = VGroup()
            expressions = VGroup(low_stacks.numbers[0])
            stacks = VGroup(low_stacks[0])
            v_buff = 0.25*stacks[0][0].get_height()

            for i, top_stack in enumerate(top_stacks[:-1]):
                low_stack = low_stacks[i+1]
                top_num = top_stacks.numbers[i]
                low_num = low_stacks.numbers[i+1]
                movers = [top_stack, top_num, low_num]
                for mover in movers:
                    mover.generate_target()
                plus = TexMobject("+")
                expr = VGroup(top_num.target, plus, low_num.target)
                expr.arrange(RIGHT, buff = SMALL_BUFF)
                top_stack.target.next_to(low_stack, UP, buff = v_buff)
                expr.next_to(top_stack.target, UP)

                all_movers.add(*movers)
                plusses.add(plus)
                expressions.add(VGroup(top_num, plus, low_num))
                stacks.add(VGroup(*it.chain(low_stack, top_stack)))

            last_group = VGroup(top_stacks[-1], top_stacks.numbers[-1])
            last_group.generate_target()
            last_group.target.align_to(low_stacks, DOWN)
            all_movers.add(last_group)
            stacks.add(top_stacks[-1])
            expressions.add(top_stacks.numbers[-1])

            self.play(*it.chain(
                list(map(MoveToTarget, all_movers)),
                list(map(Write, plusses)),
            ))

            #Add
            new_numbers = self.get_numbers(stacks)
            self.play(ReplacementTransform(
                expressions, VGroup(*list(map(VGroup, new_numbers)))
            ))
            self.wait(wait_time)
            stacks.numbers = new_numbers


    ####

    def get_numbers(self, stacks):
        return VGroup(*[
            TexMobject(str(len(stack))).next_to(stack, UP)
            for stack in stacks
        ])

class IntroducePascalsTriangle(Scene):
    CONFIG = {
        "max_n" : 9,
    }
    def construct(self):
        self.show_triangle()
        self.show_sum_of_two_over_rule()
        self.keep_in_mind_what_these_mean()
        self.issolate_9_choose_4_term()
        self.show_9_choose_4_pattern()
        self.cap_off_triangle()

    def show_triangle(self):
        rows = PascalsTriangle(n_rows = self.max_n+1)
        self.play(FadeIn(rows[1]))
        for last_row, curr_row in zip(rows[1:], rows[2:]):
            self.play(*[
                Transform(
                    last_row.copy(), VGroup(*mobs),
                    remover = True
                )
                for mobs in (curr_row[1:], curr_row[:-1])
            ])
            self.add(curr_row)
        self.wait()

        self.rows = rows

    def show_sum_of_two_over_rule(self):
        rows = self.rows

        example = rows[5][3]
        ex_top1 = rows[4][2]
        ex_top2 = rows[4][3]

        rects = VGroup()
        for mob, color in (example, GREEN), (ex_top1, BLUE), (ex_top2, YELLOW):
            mob.rect = SurroundingRectangle(mob, color = color)
            rects.add(mob.rect)

        rows_to_fade = VGroup(*rows[1:4], *rows[6:])
        rows_to_fade.save_state()

        top_row = rows[4]
        low_row = rows[5]
        top_row_copy = top_row.copy()
        top_row.save_state()
        top_row.add(ex_top2.rect)
        top_row_copy.add(ex_top1.rect)
        h_line = Line(LEFT, RIGHT)
        h_line.stretch_to_fit_width(low_row.get_width() + 2)
        h_line.next_to(low_row, UP, 1.5*SMALL_BUFF)
        plus = TexMobject("+")
        plus.next_to(h_line.get_left(), UP+RIGHT, buff = 1.5*SMALL_BUFF)

        self.play(ShowCreation(example.rect))
        self.play(
            ReplacementTransform(example.rect.copy(), ex_top1.rect),
            ReplacementTransform(example.rect.copy(), ex_top2.rect),
        )
        self.wait(2)
        self.play(rows_to_fade.fade, 1)
        self.play(
            top_row.align_to, low_row, LEFT,
            top_row_copy.next_to, top_row, UP,
            top_row_copy.align_to, low_row, RIGHT,
        )
        self.play(
            ShowCreation(h_line),
            Write(plus)
        )
        self.wait(2)
        for row in top_row, top_row_copy:
            row.remove(row[-1])
        self.play(
            rows_to_fade.restore,
            top_row.restore,
            Transform(
                top_row_copy, top_row.saved_state,
                remover = True
            ),
            FadeOut(VGroup(h_line, plus)),
            FadeOut(rects),
        )
        self.wait()

    def keep_in_mind_what_these_mean(self):
        morty = Mortimer().flip()
        morty.scale(0.7)
        morty.to_edge(LEFT)
        morty.shift(DOWN)

        numbers = VGroup(*it.chain(*self.rows[1:]))
        random.shuffle(numbers.submobjects)

        self.play(FadeIn(morty))
        self.play(PiCreatureSays(
            morty, "Keep in mind \\\\ what these mean.",
            bubble_kwargs = {
                "width" : 3.5,
                "height" : 2.5,
            }
        ))
        self.play(
            Blink(morty),
            LaggedStartMap(
                Indicate, numbers,
                rate_func = wiggle,
                color = PINK,
            )
        )
        self.play(*list(map(FadeOut, [
            morty, morty.bubble, morty.bubble.content
        ])))

    def issolate_9_choose_4_term(self):
        rows = self.rows

        for n in range(1, self.max_n+1):
            num = rows[n][0]
            line = get_stack(Female(), Male(), n, 0)[0]
            if n < self.max_n:
                line.next_to(num, LEFT)
            else:
                line.next_to(num, DOWN, MED_LARGE_BUFF)
            self.set_color_num(num)
            self.add(line)
            if n < self.max_n:
                self.wait(0.25)
            else:
                self.wait(1.25)
            self.dehighlight_num(num)
            self.remove(line)
        for k in range(1, 5):
            num = rows[self.max_n][k]
            line = get_stack(Female(), Male(), self.max_n, k)[0]
            line.next_to(num, DOWN, MED_LARGE_BUFF)
            self.set_color_num(num)
            self.add(line)
            self.wait(0.5)
            self.dehighlight_num(num)
            self.remove(line)
        num.set_color(YELLOW)
        num.scale_in_place(1.2)
        self.add(line)
        self.wait()

        self.nine_choose_four_term = num
        self.nine_choose_four_line = line

    def show_9_choose_4_pattern(self):
        rows = VGroup(*self.rows[1:])
        all_stacks = get_stacks(Female(), Male(), 9)
        stack = all_stacks[4]
        all_lines = VGroup(*it.chain(*all_stacks))

        self.play(
            rows.shift, 3*UP,
            self.nine_choose_four_line.shift, 2.5*UP,
        )
        self.remove(self.nine_choose_four_line)

        for n, line in enumerate(stack):
            line.next_to(self.nine_choose_four_term, DOWN, LARGE_BUFF)
            num = Integer(n+1)
            num.next_to(line, DOWN, MED_LARGE_BUFF)
            self.add(line, num)
            self.wait(0.1)
            self.remove(line, num)
        self.add(line, num)
        self.wait()
        self.curr_line = line

        #Probability
        expr = TexMobject(
            "P(4", "\\female", "\\text{ out of }", "9", ")", "="
        )
        expr.move_to(num.get_left())
        expr.set_color_by_tex("female", MAROON_B)
        nine_choose_four_term = self.nine_choose_four_term.copy()
        nine_choose_four_term.generate_target()
        nine_choose_four_term.target.scale(1./1.2)
        over_512 = TexMobject("\\quad \\over 2^9")
        frac = VGroup(nine_choose_four_term.target, over_512)
        frac.arrange(DOWN, buff = SMALL_BUFF)
        frac.next_to(expr, RIGHT, SMALL_BUFF)
        eq_result = TexMobject("\\approx 0.246")
        eq_result.next_to(frac, RIGHT)

        def show_random_lines(n, wait_time = 1):
            for x in range(n):
                if x == n-1:
                    wait_time = 0
                new_line = random.choice(all_lines)
                new_line.move_to(self.curr_line)
                self.remove(self.curr_line)
                self.curr_line = new_line
                self.add(self.curr_line)
                self.wait(wait_time)

        self.play(FadeOut(num), FadeIn(expr))
        show_random_lines(4)
        self.play(
            MoveToTarget(nine_choose_four_term),
            Write(over_512)
        )
        show_random_lines(4)
        self.play(Write(eq_result))
        show_random_lines(6)
        self.play(
            self.nine_choose_four_term.scale_in_place, 1./1.2,
            self.nine_choose_four_term.set_color, WHITE,
            *list(map(FadeOut, [
                expr, nine_choose_four_term,
                over_512, eq_result, self.curr_line
            ]))
        )
        self.play(rows.shift, 3*DOWN)

    def cap_off_triangle(self):
        top_row = self.rows[0]
        circle = Circle(color = YELLOW)
        circle.replace(top_row, dim_to_match = 1)
        circle.scale_in_place(1.5)

        line_groups = VGroup()
        for n in range(4, -1, -1):
            line = VGroup(*[
                random.choice([Male, Female])()
                for k in range(n)
            ])
            if n == 0:
                line.add(Line(LEFT, RIGHT).scale(0.1).set_stroke(BLACK, 0))
            line.arrange(RIGHT, SMALL_BUFF)
            line.shift(FRAME_X_RADIUS*RIGHT/2 + FRAME_Y_RADIUS*UP/2)
            brace = Brace(line, UP)
            if n == 1:
                label = "1 Person"
            else:
                label = "%d People"%n
            brace_text = brace.get_text(label)
            line_group = VGroup(line, brace, brace_text)
            line_groups.add(line_group)

        self.play(ShowCreation(circle))
        self.play(Write(top_row))
        self.wait()
        curr_line_group = line_groups[0]
        self.play(FadeIn(curr_line_group))
        for line_group in line_groups[1:]:
            self.play(ReplacementTransform(
                curr_line_group, line_group
            ))
            curr_line_group = line_group
        self.wait()

    ###

    def set_color_num(self, num):
        num.set_color(YELLOW)
        num.scale_in_place(1.2)

    def dehighlight_num(self, num):
        num.set_color(WHITE)
        num.scale_in_place(1.0/1.2)

class StacksApproachBellCurve(Scene):
    CONFIG = {
        "n_iterations" : 30,
    }
    def construct(self):
        bar = Square(side_length = 1)
        bar.set_fill(BLUE)
        bar.set_stroke(width = 0)
        bars = VGroup(bar)

        numbers = VGroup(Integer(1))
        numbers.next_to(bars, UP, SMALL_BUFF)

        max_width = FRAME_WIDTH - 2
        max_height = FRAME_Y_RADIUS - 1.5

        for x in range(self.n_iterations):
            if x == 0:
                distance = 1.5
            else:
                distance = bars[1].get_center()[0] - bars[0].get_center()[0]

            bars_copy = bars.copy()

            #Copy and shift
            for mob, vect in (bars, DOWN), (bars_copy, UP):
                mob.generate_target()
                if mob.target.get_height() > max_height:
                    mob.target.stretch_to_fit_height(max_height)
                if mob.target.get_width() > max_width:
                    mob.target.stretch_to_fit_width(max_width)
                mob.target.next_to(ORIGIN, vect, MED_LARGE_BUFF)
            colors = color_gradient([BLUE, YELLOW], len(bars)+1)
            for color, bar in zip(colors, bars.target):
                bar.set_fill(color)
            for color, bar in zip(colors[1:], bars_copy.target):
                bar.set_fill(color)
            bars_copy.set_fill(opacity = 0)

            numbers_copy = numbers.copy()
            for bs, ns in (bars, numbers), (bars_copy, numbers_copy):
                ns.generate_target()
                for bar, number in zip(bs.target, ns.target):
                    # if number.get_width() > bar.get_width():
                    #     number.set_width(bar.get_width())
                    number.next_to(bar, UP, SMALL_BUFF)

            self.play(*list(map(MoveToTarget, [
                bars, bars_copy,
                numbers, numbers_copy
            ])))
            self.play(
                bars.shift, distance*LEFT/2,
                numbers.shift, distance*LEFT/2,
                bars_copy.shift, distance*RIGHT/2,
                numbers_copy.shift, distance*RIGHT/2,
            )

            #Stack
            bars_copy.generate_target()
            numbers.generate_target()
            numbers_copy.generate_target()
            new_numbers = VGroup()
            min_scale_val = 1
            for i in range(len(bars)-1):
                top_bar = bars_copy.target[i]
                low_bar = bars[i+1]
                top_num = numbers_copy.target[i]
                low_num = numbers.target[i+1]
                new_num = Integer(top_num.number + low_num.number)
                if new_num.get_width() > top_bar.get_width():
                    min_scale_val = min(
                        min_scale_val, 
                        top_bar.get_width() / new_num.get_width()
                    )
                new_numbers.add(new_num)

                top_bar.move_to(low_bar.get_top(), DOWN)
                new_num.next_to(top_bar, UP, SMALL_BUFF)
                Transform(low_num, new_num).update(1)
                Transform(top_num, new_num).update(1)
            for group in new_numbers, numbers.target[1:], numbers_copy.target[:-1]:
                for num in group:
                    num.scale(min_scale_val, about_point = num.get_bottom())
            if x > 1:
                height = numbers.target[1].get_height()
                for mob in numbers.target[0], numbers_copy.target[-1]:
                    mob.set_height(height)

            bars_copy.target[-1].align_to(bars, DOWN)
            numbers_copy.target[-1].next_to(bars_copy.target[-1], UP, SMALL_BUFF)

            self.play(*[
                MoveToTarget(mob, lag_ratio = 0.5)
                for mob in (bars_copy, numbers, numbers_copy)
            ])
            self.remove(numbers, numbers_copy)
            numbers = VGroup(numbers[0])
            numbers.add(*new_numbers)
            numbers.add(numbers_copy[-1])

            #Resize lower bars
            for top_bar, low_bar in zip(bars_copy[:-1], bars[1:]):
                bottom = low_bar.get_bottom()
                low_bar.replace(
                    VGroup(low_bar, top_bar),
                    stretch = True
                )
                low_bar.move_to(bottom, DOWN)
            bars.add(bars_copy[-1])
            self.remove(bars_copy)
            self.add(bars)

        self.add(numbers)
        self.wait()

# class IsThereABetterWayToCompute(TeacherStudentsScene):
#     def construct(self):
#         self.student_says(
#             "Is there a better \\\\ way to compute these?",
#             target_mode = "raise_left_hand",
#         )
#         self.change_student_modes("confused", "raise_left_hand", "erm")
#         self.wait()
#         self.play(self.teacher.change_mode, "happy")
#         self.wait()
#         self.teacher_says(
#             "There is!  But first...",
#             target_mode = "hooray"
#         )
#         self.wait(2)

class ChooseThreeFromFive(InitialFiveChooseThreeExample, PiCreatureScene):
    CONFIG = {
        "n" : 5,
        "k" : 3,
        "pi_creature_scale_val" : 0.3,
        "people_colors" : [
             PURPLE, BLUE, GREEN, GOLD_E, GREY,
        ],
    }
    def construct(self):
        self.remove(self.people)
        self.show_binary_strings()
        self.add_people()
        self.choose_triplets()
        self.show_association_with_binary(3)
        self.show_association_with_binary(5)
        self.order_doesnt_matter()
        self.that_phrase_is_confusing()
        self.pattern_is_unambiguous()

    def show_binary_strings(self):
        n, k = self.n, self.k
        stack = get_stack(
            self.get_obj1(), self.get_obj2(), n, k,
            vertical_buff = SMALL_BUFF,
        )
        stack.to_edge(DOWN, buff = LARGE_BUFF)
        equation = TexMobject(
            "{%d \\choose %d}"%(n, k),
            "=", str(choose(n, k)),
        )
        equation[0].scale(0.75, about_point = equation[0].get_right())
        equation.next_to(stack, UP)

        for i, line in enumerate(stack):
            num = TexMobject(str(i+1))
            num.next_to(stack, UP)
            self.add(line, num)
            self.wait(0.25)
            self.remove(num)
        self.play(
            Write(VGroup(*equation[:-1])),
            ReplacementTransform(num, equation[-1])
        )
        self.wait()

        self.set_variables_as_attrs(stack, equation)

    def add_people(self):
        people = self.people

        names = self.get_names(people)
        braces = self.get_people_braces(people)

        self.play(
            Write(braces),
            LaggedStartMap(FadeIn, people),
            VGroup(self.stack, self.equation).to_edge, RIGHT, LARGE_BUFF
        )
        self.play(LaggedStartMap(FadeIn, names))

        self.set_variables_as_attrs(names, braces)

    def choose_triplets(self):
        movers = VGroup()
        movers.generate_target()
        max_name_width = max([n.get_width() for n in self.names])
        for name_triplet in it.combinations(self.names, 3):
            mover = VGroup(*name_triplet).copy()
            mover.generate_target()
            if hasattr(self, "stack"):
                mover.target.set_height(self.stack[0].get_height())
            for name in mover.target[:2]:
                name[-1].set_fill(opacity = 1)
            mover.target.arrange(RIGHT, MED_SMALL_BUFF)
            movers.add(mover)
            movers.target.add(mover.target)
        movers.target.arrange(
            DOWN, buff = SMALL_BUFF,
            aligned_edge = LEFT,
        )
        movers.target.next_to(self.people, DOWN, MED_LARGE_BUFF)
        if hasattr(self, "stack"):
            movers.target.align_to(self.stack, UP)

        self.play(LaggedStartMap(
            MoveToTarget, movers,
            lag_ratio = 0.2,
            run_time = 4,
        ))
        self.wait()

        self.name_triplets = movers
        
    def show_association_with_binary(self, index):
        people = self.people
        names = self.names
        for mob in people, names:
            mob.save_state()
            mob.generate_target()

        line = self.stack[index].copy()
        triplet = self.name_triplets[index]
        triplet.save_state()
        line.generate_target()
        for bit, name in zip(line.target, self.names):
            bit.next_to(name, UP)

        line_rect = SurroundingRectangle(line)
        full_line_rect = SurroundingRectangle(VGroup(line, triplet))
        people_rects = VGroup()
        for pi, name, obj in zip(people.target, names.target, line):
            if "1" in obj.get_tex_string():
                rect = SurroundingRectangle(VGroup(pi, name))
                people_rects.add(rect)
                pi.change_mode("hooray")
            else:
                pi.fade(0.5)
                name.fade(0.5)

        self.play(ShowCreation(line_rect))
        self.play(MoveToTarget(line))
        self.play(
            LaggedStartMap(ShowCreation, people_rects),
            MoveToTarget(people),
            MoveToTarget(names),
        )
        self.wait()
        self.play(
            ReplacementTransform(line_rect, full_line_rect),
            triplet.set_color, YELLOW
        )
        self.wait(2)
        self.play(
            people.restore,
            names.restore,
            triplet.restore,
            FadeOut(line),
            FadeOut(full_line_rect),
            FadeOut(people_rects),
        )

    def order_doesnt_matter(self):
        triplet = self.name_triplets[0].copy()
        triplet.set_fill(opacity = 1)
        triplet.next_to(
            self.name_triplets, RIGHT,
            buff = LARGE_BUFF,
            aligned_edge = UP,
        )
        updownarrow = TexMobject("\\Updownarrow")
        updownarrow.set_color(YELLOW)
        updownarrow.next_to(triplet, DOWN, SMALL_BUFF)
        permutations = VGroup()
        for indices in it.permutations(list(range(len(triplet)))):
            perm = triplet.copy()
            resorter = VGroup(*[
                perm[i] for i in indices
            ])
            resorter.arrange(RIGHT, MED_SMALL_BUFF)
            resorter.next_to(updownarrow, DOWN)
            permutations.add(perm)

        words = TextMobject("``Order doesn't matter''")
        words.scale(0.75)
        words.set_color(BLUE)
        words.next_to(permutations, DOWN)

        self.play(ReplacementTransform(
            self.name_triplets[0].copy(), triplet
        ))
        curr_perm = permutations[0]
        self.play(
            ReplacementTransform(triplet.copy(), curr_perm),
            Write(updownarrow)
        )
        for i in range(8):
            new_perm = permutations[i%(len(permutations)-1)+1]
            anims = [
                Transform(
                    curr_perm, new_perm,
                    path_arc = np.pi,
                )
            ]
            if i == 1:
                self.wait()
            if i == 4:
                anims.append(Write(words, run_time = 1))
            self.play(*anims)
        self.play(*list(map(FadeOut, [triplet, curr_perm, updownarrow])))

        self.order_doesnt_matter_words = words

    def that_phrase_is_confusing(self):
        odm_words = self.order_doesnt_matter_words
        odm_words_outline = VGroup()
        for letter in odm_words:
            mob = VMobject()
            mob.points = letter.points
            odm_words_outline.add(mob)
        odm_words_outline.set_fill(opacity = 0)
        odm_words_outline.set_stroke(YELLOW, 1)

        line = self.stack[0].copy()

        q_marks = TextMobject("???")
        q_marks.next_to(odm_words, DOWN)
        q_marks.set_color(YELLOW)

        self.play(
            LaggedStartMap(
                ShowCreationThenDestruction, odm_words_outline,
                lag_ratio = 0.2,
                run_time = 1,
            ),
            LaggedStartMap(
                ApplyMethod, self.people,
                lambda pi : (pi.change, "confused", odm_words,)
            ),
            LaggedStartMap(FadeIn, q_marks),
        )
        self.play(line.next_to, odm_words, UP)
        for x in range(6):
            line.generate_target()
            resorter = VGroup(*line.target)
            resorter.sort(lambda p : random.random())
            resorter.arrange(RIGHT, buff = SMALL_BUFF)
            resorter.move_to(line)
            self.play(MoveToTarget(line, path_arc = np.pi))
        self.play(FadeOut(q_marks))

        line.sort(lambda p : p[0])
        words = VGroup(*list(map(TextMobject, ["First", "Second", "Fifth"])))
        words.set_color(YELLOW)
        words.scale(0.75)
        word_arrow_groups = VGroup()
        for i, word in zip([0, 1, 4], words):
            arrow = Vector(0.5*DOWN)
            arrow.set_color(YELLOW)
            arrow.next_to(line[i], UP, SMALL_BUFF)
            word.next_to(arrow, UP, SMALL_BUFF)
            word_arrow_groups.add(VGroup(word, arrow))

        for x in range(2):
            for i in range(len(word_arrow_groups)+1):
                anims = []
                if i > 0:
                    anims.append(FadeOut(word_arrow_groups[i-1]))
                if i < len(word_arrow_groups):
                    anims.append(FadeIn(word_arrow_groups[i]))
                self.play(*anims)
            self.wait()
            word_arrow_groups.submobjects = [
                word_arrow_groups[j]
                for j in (1, 2, 0)
            ]
        self.play(*list(map(FadeOut, [line, odm_words])))

    def pattern_is_unambiguous(self):
        all_ones = VGroup()
        for line in self.stack:
            ones = VGroup(*[m for m in line if "1" in m.get_tex_string()]).copy()
            ones.set_color(YELLOW)
            all_ones.add(ones)

        self.play(
            LaggedStartMap(
                FadeIn, all_ones,
                lag_ratio = 0.2,
                run_time = 3,
                rate_func = there_and_back
            ),
            LaggedStartMap(
                ApplyMethod, self.people,
                lambda pi : (pi.change, "happy", ones),
            )
        )
        self.wait()
        for trip in it.combinations(self.people, 3):
            rects = VGroup(*list(map(SurroundingRectangle, trip)))
            self.add(rects)
            self.wait(0.3)
            self.remove(rects)
        self.wait()

    ###

    def create_pi_creatures(self):
        people = VGroup(*[
            PiCreature(color = color).scale(self.pi_creature_scale_val)
            for color in self.people_colors
        ])
        people.arrange(RIGHT)
        people.shift(3*LEFT)
        people.to_edge(UP, buff = 1.25)
        self.people = people
        return people

    def get_names(self, people):
        names = VGroup(*[
            TextMobject(name + ",")
            for name in ("Ali", "Ben", "Cam", "Denis", "Evan")
        ])
        for name, pi in zip(names, people):
            name[-1].set_fill(opacity = 0)
            name.scale(0.75)
            name.next_to(pi, UP, 2*SMALL_BUFF)
            pi.name = name
        return names

    def get_people_braces(self, people):
        group = VGroup(people, *[pi.name for pi in people])
        lb, rb = braces = TexMobject("\\{ \\}")
        braces.scale(2)
        braces.stretch_to_fit_height(1.3*group.get_height())
        lb.next_to(group, LEFT, SMALL_BUFF)
        rb.next_to(group, RIGHT, SMALL_BUFF)
        return braces

class SubsetProbabilityExample(ChooseThreeFromFive):
    CONFIG = {
        "random_seed" : 1,
    }
    def construct(self):
        self.setup_people()
        self.ask_question()
        self.show_all_triplets()
        self.circle_those_with_ali()

    def setup_people(self):
        people = self.people
        names = self.get_names(people)
        braces = self.get_people_braces(people)
        group = VGroup(people, names, braces)

        self.play(group.shift, -group.get_center()[0]*RIGHT)
        self.wait()

        self.set_variables_as_attrs(names, braces)

    def ask_question(self):
        pi_name_groups = VGroup(*[
            VGroup(pi, pi.name)
            for pi in self.people
        ])

        words = TextMobject(
            "Choose 3 people randomly.\\\\",
            "Probability", "Ali", "is one of them?"
        )
        words.set_color_by_tex("Ali", self.people[0].get_color())
        words.next_to(pi_name_groups, DOWN, 2*LARGE_BUFF)

        checkmark = TexMobject("\\checkmark").set_color(GREEN)
        cross = TexMobject("\\times").set_color(RED)
        for mob in checkmark, cross:
            mob.scale(2)
            mob.next_to(self.braces, DOWN, aligned_edge = LEFT)
            mob.shift(MED_SMALL_BUFF*LEFT)

        ali = pi_name_groups[0]

        self.play(FadeIn(words))
        for x in range(4):
            group = VGroup(*random.sample(pi_name_groups, 3))
            group.save_state()
            group.generate_target()
            group.target.shift(LARGE_BUFF*DOWN)
            for pi, name in group.target:
                pi.change("hooray", checkmark)
            if ali in group:
                symbol = checkmark
                rect = SurroundingRectangle(
                    group.target[group.submobjects.index(ali)]
                )
                rect.set_stroke(GREEN)
            else:
                symbol = cross
                rect = VGroup()

            run_time = 1
            self.play(
                MoveToTarget(group),
                FadeIn(symbol),
                ShowCreation(rect),
                run_time = run_time,
            )
            self.wait(0.5)
            self.play(
                group.restore,
                FadeOut(symbol),
                FadeOut(rect),
                run_time = run_time,
            )

        self.question = words
        self.set_variables_as_attrs(pi_name_groups)

    def show_all_triplets(self):
        self.play(
            self.question.scale, 0.75,
            self.question.to_corner, UP+RIGHT,
            VGroup(self.people, self.names, self.braces).to_edge, LEFT,
        )
        self.choose_triplets()

        brace = Brace(self.name_triplets, RIGHT)
        total_count = brace.get_tex(
            "{5 \\choose 3}", "=", "10",
            buff = MED_LARGE_BUFF
        )
        total_count.set_color(BLUE)
        self.play(
            GrowFromCenter(brace),
            Write(total_count),
        )
        self.wait()

        self.set_variables_as_attrs(brace, total_count)

    def circle_those_with_ali(self):
        name_triplets = self.name_triplets
        five_choose_three, equals, ten = self.total_count
        names = self.names

        with_ali = VGroup(*name_triplets[:6])
        alis = VGroup(*[group[0] for group in with_ali])
        rect = SurroundingRectangle(with_ali)

        frac_lines = VGroup()
        for vect in LEFT, RIGHT:
            frac_line = TexMobject("\\quad \\over \\quad")
            if vect is LEFT:
                frac_line.stretch(1.5, 0)
            frac_line.next_to(equals, vect)
            frac_lines.add(frac_line)
        four_choose_two = TexMobject("4 \\choose 2")
        four_choose_two.next_to(frac_lines[0], UP, SMALL_BUFF)
        six = TexMobject("6")
        six.next_to(frac_lines[1], UP, SMALL_BUFF)

        self.play(
            ShowCreation(rect),
            alis.set_color, YELLOW
        )
        for pair in it.combinations(names[1:], 2):
            arrows = VGroup()
            for pi in pair:
                arrow = Vector(0.5*DOWN, color = YELLOW)
                arrow.next_to(pi, UP)
                arrows.add(arrow)
            self.add(arrows)
            self.wait(0.5)
            self.remove(arrows)
        self.add(arrows)
        self.wait()
        self.play(
            FadeIn(frac_lines),
            five_choose_three.next_to, frac_lines[0], DOWN, SMALL_BUFF,
            ten.next_to, frac_lines[1], DOWN, SMALL_BUFF,
            Write(four_choose_two)
        )
        self.wait()
        self.play(ReplacementTransform(
            four_choose_two.copy(), six
        ))
        self.play(FadeOut(arrows))

        for x in range(20):
            name_rect = SurroundingRectangle(random.choice(name_triplets))
            name_rect.set_color(BLUE)
            name_rect.set_fill(BLUE, opacity = 0.25)
            self.play(Animation(name_rect, run_time = 0))
            self.wait(0.25)
            self.remove(name_rect)

class StudentsGetConfused(PiCreatureScene):
    def construct(self):
        pi1, pi2 = self.pi_creatures
        line = VGroup(
            Male(), Female(), Female(), Male(), Female()
        )
        width = line.get_width()
        for i, mob in enumerate(line):
            mob.shift((i*width+SMALL_BUFF)*RIGHT)
        line.scale(1.5)
        line.arrange(RIGHT, SMALL_BUFF)
        line.move_to(self.pi_creatures, UP)

        self.add(line)
        self.play(
            self.get_shuffle_anim(line),
            PiCreatureSays(
                pi1, "Wait \\dots order matters now?",
                target_mode = "confused",
                look_at_arg = line
            )
        )
        self.play(
            self.get_shuffle_anim(line),
            *[
                ApplyMethod(pi.change, "confused", line)
                for pi in self.pi_creatures
            ]
        )
        for x in range(4):
            self.play(self.get_shuffle_anim(line))
        self.wait()

    def create_pi_creatures(self):
        pis = VGroup(*[
            Randolph(color = color)
            for color in (BLUE_D, BLUE_B)
        ])
        pis[1].flip()
        pis.arrange(RIGHT, buff = 5)
        pis.to_edge(DOWN)
        return pis

    def get_shuffle_anim(self, line):
        indices = list(range(len(line)))
        random.shuffle(indices)
        line.generate_target()
        for i, m in zip(indices, line.target):
            m.move_to(line[i])
        return MoveToTarget(line, path_arc = np.pi)

class HowToComputeNChooseK(ChooseThreeFromFive):
    CONFIG = {
        "n" : 5,
        "k" : 3,
        "line_colors" : [GREEN, YELLOW],
        "n_permutaitons_to_show" : 5,
    }
    def construct(self):
        self.force_skipping()

        self.setup_people()
        self.choose_example_ordered_triplets()
        self.count_possibilities()
        self.show_permutations_of_ABC()
        self.count_permutations_of_ABC()
        self.reset_stage()
        self.show_whats_being_counted()

        self.revert_to_original_skipping_status()
        self.indicate_final_answer()

    def setup_people(self):
        people = self.people
        names = self.get_names(people)
        braces = self.get_people_braces(people)
        people_group = VGroup(people, names, braces)
        people_group.center().to_edge(UP, buff = MED_LARGE_BUFF)

        self.add(people_group)
        self.set_variables_as_attrs(
            names, people_group,
            people_braces = braces
        )

    def choose_example_ordered_triplets(self):
        n, k = self.n, self.k
        names = self.names

        lines, place_words = self.get_lines_and_place_words()

        for x in range(3):
            chosen_names = VGroup(*random.sample(names, k))
            chosen_names.save_state()
            for name, line, word in zip(chosen_names, lines, place_words):
                name.generate_target()
                name.target.next_to(line, UP, SMALL_BUFF)
                anims = [MoveToTarget(name)]
                if x == 0:
                    anims += [ShowCreation(line), FadeIn(word)]
                self.play(*anims)
            self.wait()
            self.play(chosen_names.restore)
        self.wait()

        self.set_variables_as_attrs(lines, place_words)

    def count_possibilities(self):
        n, k = self.n, self.k
        lines = self.lines

        choice_counts = self.get_choice_counts(n, k)
        arrows = self.get_choice_count_arrows(choice_counts)

        name_rects = VGroup()
        for name in self.names:
            name.rect = SurroundingRectangle(name)
            name_rects.add(name.rect)

        chosen_names = VGroup(*random.sample(self.names, k))
        self.names.save_state()

        for name, line, count, arrow in zip(chosen_names, lines, choice_counts, arrows):
            self.play(
                FadeIn(count),
                LaggedStartMap(
                    FadeIn, name_rects,
                    rate_func = there_and_back,
                    remover = True,
                )
            )
            self.play(
                name.next_to, line, UP, SMALL_BUFF,
                GrowArrow(arrow)
            )
            self.wait()

            name_rects.remove(name.rect)
            name_rects.set_stroke(YELLOW, 3)

        #Consolidate choice counts
        choice_numbers = VGroup(*[
            cc.submobjects.pop(1) 
            for cc in choice_counts
        ])
        choice_numbers.generate_target()
        dots = VGroup(*[TexMobject("\\cdot") for x in range(k-1)])
        product = VGroup(*it.chain(*list(zip(choice_numbers.target, dots))))
        product.add(choice_numbers.target[-1])
        product.arrange(RIGHT, buff = SMALL_BUFF)
        chosen_names_brace = Brace(chosen_names, UP)
        product.next_to(chosen_names_brace, UP)

        self.play(
            FadeOut(choice_counts),
            FadeOut(arrows),
            MoveToTarget(choice_numbers),
            Write(dots),
            GrowFromCenter(chosen_names_brace),
        )
        self.wait()

        self.set_variables_as_attrs(
            chosen_names, chosen_names_brace, choice_numbers,
            choice_numbers_dots = dots,
        )

    def show_permutations_of_ABC(self):
        chosen_names = self.chosen_names
        lines = self.lines

        n_perms = self.n_permutaitons_to_show + 1
        for indices in list(it.permutations(list(range(3))))[1:n_perms]:
            self.play(*[
                ApplyMethod(
                    name.next_to, lines[i], UP, SMALL_BUFF,
                    path_arc = np.pi
                )
                for i, name in zip(indices, chosen_names)
            ])
            self.wait(0.5)

    def count_permutations_of_ABC(self):
        n, k = self.n, self.k
        lines = self.lines

        chosen_names = self.chosen_names
        brace = self.chosen_names_brace
        numerator = VGroup(
            self.choice_numbers, self.choice_numbers_dots,
        )
        frac_line = Line(LEFT, RIGHT)
        frac_line.replace(numerator, dim_to_match = 0)
        frac_line.to_edge(RIGHT)

        choice_counts = self.get_choice_counts(k, k)
        arrows = self.get_choice_count_arrows(choice_counts)

        self.play(
            chosen_names.shift, UP,
            chosen_names.to_edge, LEFT,
            numerator.next_to, frac_line, UP, SMALL_BUFF,
            FadeOut(brace),
        )
        shuffled_names = random.sample(chosen_names, k)
        for line, name, count, arrow in zip(lines, shuffled_names, choice_counts, arrows):
            self.play(FadeIn(count), GrowArrow(arrow))
            self.play(
                name.next_to, line, UP, SMALL_BUFF,
                path_arc = -np.pi/3,
            )
            self.wait()

        #Consolidate choice counts
        choice_numbers = VGroup(*[
            cc.submobjects.pop(1) 
            for cc in choice_counts
        ])
        choice_numbers.generate_target()
        dots = VGroup(*[TexMobject("\\cdot") for x in range(k-1)])
        product = VGroup(*it.chain(*list(zip(choice_numbers.target, dots))))
        product.add(choice_numbers.target[-1])
        product.arrange(RIGHT, buff = SMALL_BUFF)
        product.next_to(frac_line, DOWN, SMALL_BUFF)

        self.play(
            FadeOut(choice_counts),
            FadeOut(arrows),
            MoveToTarget(choice_numbers),
            Write(dots),
            ShowCreation(frac_line),
        )
        self.wait()

        self.fraction = VGroup(
            numerator, frac_line, VGroup(choice_numbers, dots)
        )

    def reset_stage(self):
        n, k = self.n, self.k
        n_choose_k_equals = TexMobject(
            "{%d \\choose %d} ="%(n, k)
        )
        n_choose_k_equals.next_to(ORIGIN, RIGHT, LARGE_BUFF)
        n_choose_k_equals.to_edge(UP, LARGE_BUFF)

        self.play(
            self.names.restore,
            FadeOut(self.lines),
            FadeOut(self.place_words),
        )
        self.play(
            self.people_group.to_edge, LEFT,
            FadeIn(n_choose_k_equals),
            self.fraction.next_to, n_choose_k_equals, RIGHT, SMALL_BUFF
        )

    def show_whats_being_counted(self):
        n, k = self.n, self.k
        letters = VGroup(*[name[0] for name in self.names])

        rhs = TexMobject("=", "{60", "\\over", "6}")
        rhs.next_to(self.fraction, RIGHT)

        all_groups = VGroup()
        lines = VGroup()
        for ordered_triplet in it.combinations(letters, k):
            line = VGroup()
            for triplet in it.permutations(ordered_triplet):
                group = VGroup(*triplet).copy()
                group.save_state()
                group.arrange(RIGHT, buff = SMALL_BUFF)
                line.add(group)
                all_groups.add(group)
            line.arrange(RIGHT, buff = LARGE_BUFF)
            lines.add(line)
        lines.arrange(DOWN)
        lines.scale(0.8)
        lines.to_edge(DOWN)
        rects = VGroup(*[
            SurroundingRectangle(
                line, buff = 0,
                stroke_width = 0,
                fill_color = BLUE,
                fill_opacity = 0.5,
            )
            for line in lines
        ])

        self.play(
            Write(VGroup(*rhs[:-1])),
            LaggedStartMap(
                ApplyMethod, all_groups,
                lambda g : (g.restore,),
                rate_func = lambda t : smooth(1-t),
                run_time = 4,
                lag_ratio = 0.2,
            ),
        )
        self.wait()
        self.play(
            LaggedStartMap(FadeIn, rects),
            Write(rhs[-1])
        )
        self.wait()

        self.ordered_triplets = lines
        self.triplet_group_rects = rects
        self.rhs = rhs

    def indicate_final_answer(self):
        ordered_triplets = self.ordered_triplets
        rects = self.triplet_group_rects
        fraction = VGroup(*self.rhs[1:])
        frac_rect = SurroundingRectangle(fraction)

        brace = Brace(rects, LEFT)
        brace_tex = brace.get_tex("10")

        self.play(FocusOn(fraction))
        self.play(ShowCreation(frac_rect))
        self.play(FadeOut(frac_rect))
        self.wait()
        self.play(
            GrowFromCenter(brace),
            Write(brace_tex),
        )
        self.wait()


    ####

    def get_choice_counts(self, n, k):
        people_braces = self.people_braces
        choice_counts = VGroup(*[
            TextMobject(
                "(", str(n0), " choices", ")",
                arg_separator = ""
            )
            for n0 in range(n, n-k, -1)
        ])
        choice_counts.arrange(RIGHT, buff = SMALL_BUFF)
        choice_counts.set_color_by_gradient(*self.line_colors)
        choice_counts.next_to(people_braces, DOWN)
        return choice_counts

    def get_choice_count_arrows(self, choice_counts):
        lines = self.lines
        return VGroup(*[
            Arrow(
                count.get_bottom(), 
                line.get_center() + MED_LARGE_BUFF*UP,
                color = line.get_color()
            )
            for count, line in zip(choice_counts, lines)
        ])

    def get_lines_and_place_words(self):
        n, k = self.n, self.k
        width = max([n.get_width() for n in self.names]) + MED_SMALL_BUFF
        lines = VGroup(*[
            Line(ORIGIN, width*RIGHT)
            for x in range(k)
        ])
        lines.arrange(RIGHT)
        lines.next_to(ORIGIN, DOWN, buff = LARGE_BUFF)
        place_words = VGroup(*[
            TexMobject("%d^\\text{%s}"%(i+1, s))
            for i, s in zip(
                list(range(k)), 
                it.chain(["st", "nd", "rd"], it.repeat("th"))
            )
        ])
        for mob in place_words, lines:
            mob.set_color_by_gradient(*self.line_colors)
        for word, line in zip(place_words, lines):
            word.next_to(line, DOWN, SMALL_BUFF)

        self.set_variables_as_attrs(lines, place_words)
        return lines, place_words

class NineChooseFourExample(HowToComputeNChooseK):
    CONFIG = {
        "random_seed" : 2,
        "n" : 9,
        "k" : 4,
        "line_colors" : [RED, MAROON_B],
        "n_permutaitons_to_show" : 3,
    }
    def construct(self):
        self.setup_people()
        self.show_n_choose_k()
        self.show_n_choose_k_pattern()
        self.choose_k_people()
        self.count_how_to_choose_k()
        self.show_permutations()
        self.finish_computation()

    def setup_people(self):
        self.remove(self.people)
        self.people = TextMobject(" ".join([
            chr(ord('A') + i )
            for i in range(self.n)
        ]))
        self.people.set_color_by_gradient(BLUE, YELLOW)
        self.names = self.people
        self.people.to_edge(UP, buff = LARGE_BUFF + MED_SMALL_BUFF)
        lb, rb = braces = TextMobject("\\{\\}")
        braces.scale(1.5)
        lb.next_to(self.people, LEFT, SMALL_BUFF)
        rb.next_to(self.people, RIGHT, SMALL_BUFF)

        self.people_group = VGroup(braces, self.people)
        self.people_braces = braces

    def show_n_choose_k(self):
        n, k = self.n, self.k
        n_choose_k = TexMobject("{%d \\choose %d}"%(n, k))
        n_choose_k.to_corner(UP + LEFT)
        self.play(FadeIn(n_choose_k))
        self.set_variables_as_attrs(n_choose_k)

    def show_n_choose_k_pattern(self):
        n, k = self.n, self.k
        stack = get_stack(
            TexMobject("1").set_color(PINK),
            TexMobject("0").set_color(BLUE),
            n, k
        )
        l = len(stack)
        n_stacks = 6
        columns = VGroup(*[
            VGroup(*stack[(i*l)/n_stacks:((i+1)*l)/n_stacks])
            for i in range(n_stacks)
        ])
        columns.arrange(
            RIGHT, 
            aligned_edge = UP,
            buff = MED_LARGE_BUFF
        )
        columns.set_height(7)
        columns.to_corner(DOWN + RIGHT)

        for line in stack:
            self.play(FadeIn(line, run_time = 0.1))
        self.wait(2)
        self.play(FadeOut(
            stack, lag_ratio = 0.5, run_time = 2
        ))

    def choose_k_people(self):
        n, k = self.n, self.k
        people = self.people
        braces = self.people_braces

        n_items = TextMobject("%d items"%n)
        choose_k = TextMobject("choose %d"%k)
        n_items.next_to(people, UP, buff = MED_LARGE_BUFF)
        choose_k.next_to(people, DOWN, buff = LARGE_BUFF)

        chosen_subset = VGroup(*random.sample(people, k))

        self.play(
            Write(braces),
            LaggedStartMap(FadeIn, people, run_time = 1),
            FadeIn(n_items),
        )
        self.wait()
        self.play(
            FadeIn(choose_k),
            LaggedStartMap(
                ApplyMethod, chosen_subset,
                lambda m : (m.shift, MED_LARGE_BUFF*DOWN)
            )
        )
        self.wait()
        self.play(
            chosen_subset.shift, MED_LARGE_BUFF*UP,
            n_items.next_to, n_items.get_center(), LEFT,
            choose_k.next_to, n_items.get_center(), RIGHT,
        )

    def count_how_to_choose_k(self):
        lines, place_words = self.get_lines_and_place_words()
        self.play(
            LaggedStartMap(FadeIn, lines),
            LaggedStartMap(FadeIn, place_words),
            run_time = 1
        )
        self.count_possibilities()

    def show_permutations(self):
        self.show_permutations_of_ABC()
        self.count_permutations_of_ABC()

    def finish_computation(self):
        equals = TexMobject("=")
        equals.shift(2*LEFT)
        fraction = self.fraction
        six = fraction[0][0][3]
        eight = fraction[0][0][1]
        two_three = VGroup(*fraction[2][0][1:3])
        four = fraction[2][0][0]

        rhs = TexMobject("= 9 \\cdot 2 \\cdot 7 = 126")

        self.play(
            self.names.restore,
            FadeOut(self.lines),
            FadeOut(self.place_words),
            self.n_choose_k.next_to, equals, LEFT,
            self.fraction.next_to, equals, RIGHT,
            FadeIn(equals),
        )
        self.wait()

        for mob in six, eight, two_three, four:
            mob.cross = Cross(mob)
            mob.cross.set_stroke("red", 5)
        two = TexMobject("2")
        two.set_color(eight.get_fill_color())
        two.next_to(eight, UP)
        rhs.next_to(fraction, RIGHT)

        self.play(
            ShowCreation(six.cross),
            ShowCreation(two_three.cross),
        )
        self.wait()
        self.play(
            ShowCreation(eight.cross),
            ShowCreation(four.cross),
            FadeIn(two)
        )
        self.wait()
        self.play(Write(rhs))
        self.wait()

class WeirdKindOfCancelation(TeacherStudentsScene):
    def construct(self):
        fraction = TexMobject(
            "{5 \\cdot 4 \\cdot 3", 
            "\\text{ ordered}", "\\text{ triplets}",
            "\\over",
            "1 \\cdot 2 \\cdot 3", "\\text{ orderings \\;\\qquad}}"
        )
        top_numbers, ordered, triplets, frac_line, bottom_numbers, orderings = fraction
        for mob in top_numbers, bottom_numbers:
            mob.set_color_by_gradient(GREEN, YELLOW)
        fraction.next_to(self.teacher, UP+LEFT)

        names = VGroup(*list(map(TextMobject, [
            "Ali", "Ben", "Cam", "Denis", "Evan"
        ])))
        names.arrange(RIGHT)
        names.to_edge(UP, buff = LARGE_BUFF)
        names.save_state()
        lb, rb = braces = TexMobject("\\{\\}")
        braces.scale(2)
        lb.next_to(names, LEFT, SMALL_BUFF)
        rb.next_to(names, RIGHT, SMALL_BUFF)

        chosen_names = VGroup(*random.sample(names, 3))
        chosen_names.generate_target()
        chosen_names.target.arrange(RIGHT)
        chosen_names.target.next_to(top_numbers, UP, MED_LARGE_BUFF)
        for name, name_target in zip(chosen_names, chosen_names.target):
            name.target = name_target

        self.teacher_says("It's like unit cancellation.")
        self.change_student_modes(*["confused"]*3)
        self.play(
            RemovePiCreatureBubble(
                self.teacher, target_mode = "raise_right_hand"
            ),
            LaggedStartMap(FadeIn, fraction, run_time = 1),
            FadeIn(braces),
            LaggedStartMap(FadeIn, names)
        )
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = fraction
        )

        #Go through numerators
        for num, name in zip(top_numbers[::2], chosen_names):
            rect = SurroundingRectangle(num)
            name.target.set_color(num.get_color())
            self.play(
                ShowCreationThenDestruction(rect),
                MoveToTarget(name),
            )
        self.wait(2)

        #Go through denominators
        permutations = list(it.permutations(list(range(3))))[1:]

        self.shuffle(chosen_names, permutations[:2])
        self.play(LaggedStartMap(
            ShowCreationThenDestruction,
            VGroup(*list(map(SurroundingRectangle, bottom_numbers[::2])))
        ))
        self.shuffle(chosen_names, permutations[2:])
        self.wait()

        #Show cancelation
        top_cross = Cross(ordered)
        bottom_cross = Cross(orderings)

        self.play(
            ShowCreation(top_cross),
            self.teacher.change, "maybe",
        )
        self.play(ShowCreation(bottom_cross))
        self.change_student_modes(*["happy"]*3)
        self.wait(3)

    ###

    def shuffle(self, mobject, permutations):
        for permutation in permutations:
            self.play(*[
                ApplyMethod(
                    m.move_to, mobject[i].get_center(),
                    path_arc = np.pi,
                )
                for i, m in zip(permutation, mobject)
            ])

class ABCNotBCA(Scene):
    def construct(self):
        words = TextMobject("If order mattered:")
        equation = TextMobject("(A, B, C) $\\ne$ (B, C, A)")
        equation.set_color(YELLOW)
        equation.next_to(words, DOWN)
        group = VGroup(words, equation)
        group.set_width(FRAME_WIDTH - 1)
        group.to_edge(DOWN)
        self.add(words, equation)

class ShowFormula(Scene):
    def construct(self):
        specific_formula = TexMobject(
            "{9 \\choose 4}", "=",
            "{9 \\cdot 8 \\cdot 7 \\cdot 6", "\\over",
            "4 \\cdot 3 \\cdot 2 \\cdot 1}"
        )
        general_formula = TexMobject(
            "{n \\choose k}", "=",
            "{n \\cdot (n-1) \\cdots (n-k+1)", "\\over",
            "k \\cdot (k-1) \\cdots 2 \\cdot 1}"
        )
        for i, j in (0, 1), (2, 0), (2, 3), (2, 11):
            general_formula[i][j].set_color(BLUE)
        for i, j in (0, 2), (2, 13), (4, 0), (4, 3):
            general_formula[i][j].set_color(YELLOW)
        formulas = VGroup(specific_formula, general_formula)
        formulas.arrange(DOWN, buff = 2)
        formulas.to_edge(UP)

        self.play(FadeIn(specific_formula))
        self.play(FadeIn(general_formula))
        self.wait(3)

class ConfusedPi(Scene):
    def construct(self):
        morty = Mortimer()
        morty.scale(2.5)
        morty.to_corner(UP+LEFT)
        morty.look(UP+LEFT)

        self.add(morty)
        self.play(Blink(morty))
        self.play(morty.change, "confused")
        self.wait()
        self.play(Blink(morty))
        self.wait(2)

class SumsToPowerOf2(Scene):
    CONFIG = {
        "n" : 5,
        "alt_n" : 7,
    }
    def construct(self):
        self.setup_stacks()
        self.count_32()
        self.show_sum_as_n_choose_k()
        self.show_alternate_sum()

    def setup_stacks(self):
        stacks = get_stacks(
            TexMobject("1").set_color(PINK),
            TexMobject("0").set_color(BLUE),
            n = self.n,
            vertical_buff = SMALL_BUFF,
        )
        stacks.to_corner(DOWN+LEFT)
        numbers = VGroup(*[
            TexMobject(str(choose(self.n, k)))
            for k in range(self.n + 1)
        ])
        for number, stack in zip(numbers, stacks):
            number.next_to(stack, UP)

        self.play(
            LaggedStartMap(FadeIn, stacks),
            LaggedStartMap(FadeIn, numbers),
        )
        self.wait()

        self.set_variables_as_attrs(stacks, numbers)

    def count_32(self):
        lines = VGroup(*it.chain(*self.stacks))
        rhs = TexMobject("= 2^{%d}"%self.n)
        rhs.to_edge(UP, buff = LARGE_BUFF)
        rhs.to_edge(RIGHT, buff = 2)

        numbers = self.numbers.copy()
        numbers.target = VGroup(*[
            TexMobject("{%d \\choose %d}"%(self.n, k))
            for k in range(self.n + 1)
        ])
        plusses = VGroup(*[TexMobject("+") for n in numbers])
        plusses.remove(plusses[-1])
        plusses.add(TexMobject("="))
        sum_group = VGroup(*it.chain(*list(zip(
            numbers.target, plusses
        ))))
        sum_group.arrange(RIGHT, SMALL_BUFF)
        sum_group.next_to(numbers, UP, LARGE_BUFF)
        sum_group.shift(MED_LARGE_BUFF*RIGHT)

        for i, line in zip(it.count(1), lines):
            line_copy = line.copy().set_color(YELLOW)
            number = Integer(i)
            number.scale(1.5)
            number.to_edge(UP)
            VGroup(number, line_copy).set_color(YELLOW)
            self.add(line_copy, number)
            self.wait(0.15)
            self.remove(line_copy, number)
        sum_result = number
        self.add(sum_result)
        self.wait()

        sum_result.target = TexMobject(str(2**self.n))
        sum_result.target.set_color(sum_result.get_color())
        sum_result.target.next_to(sum_group, RIGHT)
        rhs.next_to(sum_result.target, RIGHT, aligned_edge = DOWN)
        self.play(
            MoveToTarget(sum_result),
            MoveToTarget(numbers),
            Write(plusses),
            Write(rhs),
        )
        self.wait()

        self.set_variables_as_attrs(
            plusses, sum_result, rhs,
            n_choose_k_terms = numbers
        )

    def show_sum_as_n_choose_k(self):
        numbers = self.numbers
        plusses = self.plusses
        n_choose_k_terms = self.n_choose_k_terms
        rhs = VGroup(self.sum_result, self.rhs)
        n = self.n


        fractions = self.get_fractions(n)
        plusses.generate_target()
        sum_group = VGroup(*it.chain(*list(zip(
            fractions, plusses.target
        ))))
        sum_group.arrange(RIGHT, buff = 2*SMALL_BUFF)
        sum_group.next_to(rhs, LEFT)
        sum_group.shift(0.5*SMALL_BUFF*DOWN)

        self.play(
            Transform(n_choose_k_terms, fractions),
            MoveToTarget(plusses),
            lag_ratio = 0.5,
            run_time = 2
        )
        self.wait()

    def show_alternate_sum(self):
        fractions = self.get_fractions(self.alt_n)
        fractions.remove(*fractions[4:-1])
        fractions.submobjects.insert(4, TexMobject("\\cdots"))
        plusses = VGroup(*[
            TexMobject("+") for f in fractions[:-1]
        ] + [TexMobject("=")])
        sum_group = VGroup(*it.chain(*list(zip(
            fractions, plusses
        ))))
        sum_group.arrange(RIGHT)
        sum_group.next_to(
            self.n_choose_k_terms, DOWN,
            aligned_edge = LEFT, buff = LARGE_BUFF
        )
        sum_group.shift(SMALL_BUFF*DOWN)
        rhs = TexMobject(
            str(2**self.alt_n), 
            "=", "2^{%d}"%(self.alt_n)
        )
        rhs[0].set_color(YELLOW)
        rhs.next_to(sum_group, RIGHT)

        self.play(
            LaggedStartMap(FadeOut, self.stacks),
            LaggedStartMap(FadeOut, self.numbers),
            LaggedStartMap(FadeIn, sum_group),
        )
        self.play(LaggedStartMap(FadeIn, rhs))
        self.wait(2)

    ####

    def get_fractions(self, n):
        fractions = VGroup(TexMobject("1"))
        dot_str = " \\!\\cdot\\! "
        for k in range(1, n+1):
            ts = str(n)
            bs = "1"
            for i in range(1, k):
                ts += dot_str + str(n-i)
                bs += dot_str + str(i+1)
            fraction = TexMobject("{%s \\over %s}"%(ts, bs))
            fractions.add(fraction)
        return fractions

class AskWhyTheyAreCalledBinomial(TeacherStudentsScene):
    def construct(self):
        example_binomials = VGroup(*[
            TexMobject("(x+y)^%d"%d)
            for d in range(2, 7)
        ])
        example_binomials.arrange(UP)
        example_binomials.next_to(
            self.teacher.get_corner(UP+LEFT), UP 
        )

        pascals = PascalsTriangle(n_rows = 6)
        pascals.set_height(3)
        pascals.to_corner(UP+LEFT, buff = MED_SMALL_BUFF)
        pascals.set_color_by_gradient(BLUE, YELLOW)

        binomial_word = TextMobject(
            "Bi", "nomials",
            arg_separator = "",
        )
        binomial_word.set_color_by_tex("Bi", YELLOW)
        binomial_word.set_color_by_tex("nomials", WHITE)
        binomial_word.next_to(example_binomials, LEFT, buff = 1.5)
        arrows = VGroup(*[
            Arrow(binomial_word.get_right(), binom.get_left())
            for binom in example_binomials
        ])
        arrows.set_color(BLUE)

        two_variables = TextMobject("Two", "variables")
        two_variables.next_to(binomial_word, DOWN)
        two_variables.shift(SMALL_BUFF*LEFT)
        for tv, bw in zip(two_variables, binomial_word):
            tv.set_color(bw.get_color())

        self.student_says(
            "Why are they called \\\\ ``binomial coefficients''?"
        )
        self.play(LaggedStartMap(FadeIn, pascals))
        self.wait()
        self.play(
            FadeIn(example_binomials[0]),
            RemovePiCreatureBubble(self.students[1]),
            self.teacher.change, "raise_right_hand",
        )
        moving_binom = example_binomials[0].copy()
        for binom in example_binomials[1:]:
            self.play(Transform(moving_binom, binom))
            self.add(binom)
        self.wait()

        #Name themn
        self.play(
            Write(binomial_word),
            LaggedStartMap(GrowArrow, arrows)
        )
        self.change_student_modes(*["pondering"]*3)
        self.play(Write(two_variables))
        self.wait(2)

class NextVideo(Scene):
    def construct(self):
        title = TextMobject("Next video: Binomial distribution")
        title.to_edge(UP)
        screen = ScreenRectangle(height = 6)
        screen.next_to(title, DOWN)

        self.play(
            Write(title),
            ShowCreation(screen)
        )
        self.wait()

class CombinationsPatreonEndScreen(PatreonEndScreen):
    CONFIG = {
        "specific_patrons" : [
            "Randall Hunt",
            "Desmos",
            "Burt Humburg",
            "CrypticSwarm",
            "Juan Benet",
            "David Kedmey",
            "Ali Yahya",
            "Mayank M. Mehrotra",
            "Lukas Biewald",
            "Yana Chernobilsky",
            "Kaustuv DeBiswas",
            "Kathryn Schmiedicke",
            "Yu Jun",
            "Dave Nicponski",
            "Damion Kistler",
            "Jordan Scales",
            "Markus Persson",
            "Egor Gumenuk",
            "Yoni Nazarathy",
            "Ryan Atallah",
            "Joseph John Cox",
            "Luc Ritchie",
            "Supershabam",
            "James Park",
            "Samantha D. Suplee",
            "Delton Ding",
            "Thomas Tarler",
            "Jonathan Eppele",
            "Isak Hietala",
            "1stViewMaths",
            "Jacob Magnuson",
            "Mark Govea",
            "Dagan Harrington",
            "Clark Gaebel",
            "Eric Chow",
            "Mathias Jansson",
            "David Clark",
            "Michael Gardner",
            "Mads Elvheim",
            "Erik Sundell",
            "Awoo",
            "Dr. David G. Stork",
            "Tianyu Ge",
            "Ted Suzman",
            "Linh Tran",
            "Andrew Busey",
            "John Haley",
            "Ankalagon",
            "Eric Lavault",
            "Boris Veselinovich",
            "Julian Pulgarin",
            "Jeff Linse",
            "Cooper Jones",
            "Ryan Dahl",
            "Robert Teed",
            "Jason Hise",
            "Meshal Alshammari",
            "Bernd Sing",
            "James Thornton",
            "Mustafa Mahdi",
            "Mathew Bramson",
            "Jerry Ling",
            "Shimin Kuang",
            "Rish Kundalia",
            "Achille Brighton",
            "Ripta Pasay",
        ]
    }

class Thumbnail(Scene):
    def construct(self):
        n_choose_k = TexMobject("n \\choose k")
        n_choose_k[1].set_color(YELLOW)
        n_choose_k[2].set_color(YELLOW)
        n_choose_k.scale(2)
        n_choose_k.to_edge(UP)
        stacks = get_stacks(
            TexMobject("1").set_color(PINK),
            TexMobject("0").set_color(BLUE),
            n = 5, vertical_buff = SMALL_BUFF,
        )
        stacks.to_edge(DOWN)
        stacks.shift(MED_SMALL_BUFF*LEFT)

        self.add(n_choose_k, stacks)





















