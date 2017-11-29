from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from animation.continual_animation import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from topics.objects import *
from topics.probability import *
from topics.complex_numbers import *
from scene import Scene
from scene.reconfigurable_scene import ReconfigurableScene
from scene.zoomed_scene import *
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *
from topics.graph_scene import *
from topics.probability import *

#revert_to_original_skipping_status

def get_stack(
    obj1, obj2, n, k,
    fixed_start = None,
    fixed_end = None,
    ):
    stack = VGroup()
    for indices in it.combinations(range(n), k):
        term = VGroup(*[
             obj1.copy() if i in indices else obj2.copy()
            for i in range(n)
        ])
        if fixed_start:
            term.add_to_back(fixed_start.copy())
        if fixed_end:
            term.add(fixed_end.copy())
        term.arrange_submobjects(RIGHT, buff = SMALL_BUFF)
        stack.add(term)
    stack.arrange_submobjects(DOWN)
    return stack

def get_stacks(obj1, obj2, n, **kwargs):
    stacks = VGroup()
    for k in range(n+1):
        stacks.add(get_stack(obj1, obj2, n, k, **kwargs))
    stacks.arrange_submobjects(
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
        self.scale_to_fit_height(self.height)
        self.highlight(self.color)

class Female(Male):
    CONFIG = {
        "tex" : "\\female",
        "color" : MAROON_B,
    }

######################

class Introduction(Scene):
    CONFIG = {
        "start_n" : 4,
    }
    def construct(self):
        self.write_n_choose_k()
        self.show_binomial_coefficients()
        self.perform_shift()

    def write_n_choose_k(self):
        symbol = TexMobject("n \\choose k")
        words = TextMobject("``n choose k''")
        group = VGroup(symbol, words)
        group.arrange_submobjects(RIGHT)

        self.play(
            FadeIn(symbol),
            Write(words)
        )
        self.dither()

        self.set_variables_as_attrs(n_choose_k_group = group)

    def show_binomial_coefficients(self):
        n = self.start_n
        n_choose_k, n_choose_k_words = self.n_choose_k_group
        binomials = VGroup(*[
            TexMobject("%d \\choose %d"%(n, k))
            for k in range(n+1)
        ])
        binomial_equations = VGroup()
        for k, binomial in enumerate(binomials):
            binomial.scale(0.75)
            number = TexMobject(str(choose(n, k)))
            equation = VGroup(binomial, TexMobject("="), number)
            equation.arrange_submobjects(RIGHT, buff = SMALL_BUFF)
            equation.highlight(YELLOW)
            equation[1].highlight(WHITE)
            binomial_equations.add(equation)
        new_words = TextMobject("``Binomial coefficients''")

        stacks = get_stacks(
            TexMobject("x").highlight(BLUE),
            TexMobject("y").highlight(RED),
            n
        )
        stacks.to_edge(DOWN, buff = LARGE_BUFF)
        for stack, eq in zip(stacks, binomial_equations):
            eq.scale_to_fit_width(0.9*stack.get_width())
            eq.next_to(stack, UP)

        self.play(
            FadeIn(stacks, run_time = 2, submobject_mode = "lagged_start"),
            self.n_choose_k_group.to_edge, UP
        )
        new_words.move_to(n_choose_k_words, LEFT)
        self.play(Transform(n_choose_k_words, new_words))
        for eq in binomial_equations:
            point = VectorizedPoint(n_choose_k.get_center())
            self.play(ReplacementTransform(
                VGroup(n_choose_k, point, point).copy(),
                eq
            ))
            self.dither()

        self.set_variables_as_attrs(stacks, binomial_equations)

    def perform_shift(self):
        n = self.start_n
        to_fade = VGroup(
            self.n_choose_k_group,
            self.binomial_equations
        )
        stacks = self.stacks
        top_stacks = stacks.copy()
        top_stacks.to_edge(UP, buff = MED_SMALL_BUFF)

        line = Line(LEFT, RIGHT, color = WHITE)
        line.scale(SPACE_WIDTH)
        line.next_to(top_stacks, DOWN)

        x = TexMobject("x").highlight(BLUE)
        y = TexMobject("y").highlight(RED)
        add_x, add_y = [
            TextMobject("Prepend", "$%s$"%s).highlight_by_tex(s, color)
            for s, color in ("x", BLUE), ("y", RED)
        ]
        add_x.to_corner(UP+LEFT)
        add_y.to_edge(LEFT).shift(MED_SMALL_BUFF*DOWN)

        new_stacks, new_top_stacks = [
            get_stacks(x, y, n, fixed_start = var)
            for var in y, x
        ]
        new_top_stacks.to_edge(UP, buff = MED_SMALL_BUFF)
        new_stacks.to_edge(DOWN)
        for s in new_stacks, new_top_stacks:
            s.start_terms = VGroup()
            for stack in s:
                for term in stack:
                    s.start_terms.add(term[0])

        s_to_s_distance = \
            new_stacks[1].get_center()[0] - \
            new_stacks[0].get_center()[0]

        self.play(
            FadeOut(to_fade),
            stacks.to_edge, DOWN,
            ReplacementTransform(stacks.copy(), top_stacks),
        )
        self.play(ShowCreation(line))
        self.play(Write(add_x, run_time = 1))
        self.play(Transform(top_stacks, new_top_stacks))
        self.play(LaggedStart(
            Indicate, new_top_stacks.start_terms,
            rate_func = there_and_back,
            run_time = 1,
            remover = True
        ))
        self.dither()
        self.play(Write(add_y, run_time = 1))
        self.play(Transform(stacks, new_stacks))
        self.play(LaggedStart(
            Indicate, new_stacks.start_terms,
            rate_func = there_and_back,
            run_time = 1,
            remover = True
        ))
        self.dither()

        self.play(
            top_stacks.shift, s_to_s_distance*RIGHT/2,
            stacks.shift, s_to_s_distance*LEFT/2,
        )
        self.play(*map(FadeOut, [add_x, add_y, line]))

        point = VectorizedPoint()
        point.move_to(top_stacks[0].get_bottom())
        point.shift(s_to_s_distance*LEFT)
        top_stacks.add_to_back(point)

        point = VectorizedPoint()
        point.move_to(stacks[-1].get_bottom())
        point.shift(s_to_s_distance*RIGHT)
        point.shift(MED_SMALL_BUFF*DOWN)
        stacks.add(point)

        for k, stack, top_stack in zip(it.count(), stacks, top_stacks):
            top_stack.generate_target()
            top_stack.target.next_to(stack, UP, MED_SMALL_BUFF)
            # term = TexMobject(
            #     str(choose(n+1, k)),
            #     "x^%d"%(n+1-k),
            #     "y^%d"%k
            # )
            term = TexMobject(
                "{%d \\choose %d}"%(n+1, k),
                "=",
                str(choose(n+1, k))
            )
            term[0].scale(0.85, about_point = term[0].get_right())
            term[0].highlight(YELLOW)
            term[2].highlight(YELLOW)
            term.scale(0.85)
            term.next_to(top_stack.target, UP)

            self.play(MoveToTarget(top_stack))
            self.play(Write(term))
        self.dither()

class DifferentWaysToThinkAboutNChooseK(Scene):
    CONFIG = {
        "n" : 5,
        "k" : 3,
        "stack_height" : 5,
    }
    def construct(self):
        self.add_n_choose_k_term()
        self.add_stack()
        self.choose_k()
        self.split_stack_by_start()
        self.split_choices_by_start()

    def add_n_choose_k_term(self):
        term = TexMobject("{5 \\choose 3} = 10")
        term.to_edge(UP)
        self.play(FadeIn(term, submobject_mode = "lagged_start"))
        self.dither()

        self.n_choose_k_term = term

    def add_stack(self):
        n, k = self.n, self.k
        x = TexMobject("x").highlight(BLUE)
        y = TexMobject("y").highlight(RED)
        stack = get_stack(x, y, n, k)
        stack.scale_to_fit_height(self.stack_height)
        stack.shift(SPACE_WIDTH*LEFT/2)
        stack.to_edge(DOWN)
        numbers = VGroup(*[
            TexMobject("%d"%(d+1))
            for d in range(choose(n, k))
        ])
        numbers.next_to(stack, UP)

        last_number = None
        for term, number in zip(stack, numbers):
            self.add(term, number)
            if last_number:
                self.remove(last_number)
            self.dither(0.25)
            last_number = number
        self.dither()

        self.stack = stack
        self.stack_count = last_number
        self.numbers = numbers

    def choose_k(self):
        n, k = self.n, self.k

        letter_set = TexMobject(
            "(",
            "A", ",", 
            "B", ",",
            "C", ",",
            "D", ",",
            "E", ")"
        )
        letters = VGroup(*letter_set[1::2])
        letter_set.shift(SPACE_WIDTH*RIGHT/2)
        letter_set.to_edge(UP)

        letter_subsets = list(it.combinations(letters, k))
        subset_mobs = VGroup(*[
            VGroup(*letter_subset).copy().arrange_submobjects(
                RIGHT, buff = SMALL_BUFF
            )
            for letter_subset in letter_subsets
        ]).arrange_submobjects(DOWN, buff = MED_SMALL_BUFF)
        subset_mobs.scale_to_fit_height(self.stack_height)
        subset_mobs.shift(SPACE_WIDTH*RIGHT/2)
        subset_mobs.to_edge(DOWN)

        choose_words = TextMobject("Choose %d"%k)
        choose_words.scale(0.9)
        choose_words.next_to(letter_set, DOWN)
        choose_words.highlight(YELLOW)

        self.revert_to_original_skipping_status()
        self.play(Write(letter_set, run_time = 1))
        self.play(
            Write(choose_words, run_time = 1),
            LaggedStart(FadeIn, subset_mobs)
        )
        self.dither()
        for subset, subset_mob in zip(letter_subsets, subset_mobs):
            VGroup(subset_mob, *subset).highlight(BLUE)
            self.dither(0.5)
            VGroup(*subset).highlight(WHITE)
        self.dither()

        self.set_variables_as_attrs(
            subset_mobs, letter_set, choose_words,
        )

    def split_stack_by_start(self):
        n, k = self.n, self.k
        stack = self.stack
        stack_count = self.stack_count

        top_num = choose(n-1, k-1)
        top_stack = VGroup(*stack[:top_num])
        bottom_stack = VGroup(*stack[top_num:])

        self.play(
            FadeOut(stack_count),
            top_stack.shift, UP
        )
        for stack, new_k in (top_stack, k-1), (bottom_stack, k):
            brace = Brace(stack, RIGHT)
            brace_tex = brace.get_tex(
                "{%d \\choose %d} = %d"%(n-1, new_k, choose(n-1, new_k))
            )
            rect = SurroundingRectangle(VGroup(*[
                VGroup(*term[1:])
                for term in stack
            ]), buff = 0.5*SMALL_BUFF)
            rect.set_stroke(WHITE, 2)
            self.play(
                GrowFromCenter(brace),
                Write(brace_tex),
                ShowCreation(rect)
            )
            self.dither()

    def split_choices_by_start(self):
        subset_mobs = self.subset_mobs
        subset_mobs.generate_target()
        subset_mobs.target.shift(LEFT)
        brace = Brace(subset_mobs.target, RIGHT)
        expression = brace.get_tex(
            "\\frac{5 \\cdot 4 \\cdot 3}{1 \\cdot 2 \\cdot 3}",
            "= 10"
        )

        self.play(
            MoveToTarget(subset_mobs),
            GrowFromCenter(brace)
        )
        self.play(Write(expression))
        self.dither()

class FormulaVsPattern(TeacherStudentsScene):
    def construct(self):
        self.show_formula()
        self.show_pattern()

    def show_formula(self):
        formula = TexMobject(
            "{n \\choose k} = {n! \\over (n-k)!k!}", 
        )
        for i in 1, 5, 9:
            formula[i].highlight(BLUE)
        for i in 2, 11, 14:
            formula[i].highlight(YELLOW)

        self.student_thinks(formula, student_index = 1)
        self.play(self.teacher.change, "sassy")
        self.dither(2)
        self.play(
            FadeOut(self.students[1].bubble),
            FadeOut(formula),
            self.teacher.change, "raise_right_hand",
            self.get_student_changes(*["pondering"]*3)
        )

    def show_pattern(self):
        words = TextMobject(
            "What is the \\\\ probability of a flush?"
        )
        values = random.sample(PlayingCard.CONFIG["possible_values"], 5)
        cards = VGroup(*[
            PlayingCard(value = value, suit = "hearts")
            for value in values
        ])
        cards.arrange_submobjects(RIGHT)
        cards.to_corner(UP+RIGHT)
        words.next_to(cards, LEFT)
        words.shift_onto_screen()

        self.play(LaggedStart(DrawBorderThenFill, cards))
        self.play(Write(words))
        self.dither(3)

class ProbabilityOfThreeWomenInGroupOfFive(Scene):
    CONFIG = {
        "random_seed" : 9,
        "n_people_per_lineup" : 5,
        "n_start_examples" : 7,
        "n_secondary_examples" : 8,
        "time_per_secondary_example" : 0.75,
        "item_line_width" : 0.4,
    }
    def construct(self):
        random.seed(self.random_seed)
        self.introduce_random_choices()
        self.mention_all_possibilities()
        self.show_all_possibilities()
        self.show_all_configurations_with_three_women()
        self.stack_all_choices_by_number_of_women()
        self.go_through_stacks()
        self.remember_this_sensation()
        self.show_answer_to_question()
        self.ask_about_pattern()

    def introduce_random_choices(self):
        title = TextMobject("5 randomly chosen people")
        title.to_edge(UP, buff = MED_SMALL_BUFF)
        self.add(title)

        question = TextMobject(
            "Probability of having \\\\ exactly 3 women?"
        )
        question.highlight(YELLOW)

        lineups = VGroup()
        for x in range(self.n_start_examples):
            lineup = self.get_random_lineup_of_men_and_women()
            lineup.scale(1.5)
            lineup.center()
            women = VGroup(*filter(
                lambda item : "female" in item.get_tex_string(),
                lineup.items
            ))
            anims = [FadeIn(lineup, submobject_mode = "lagged_start")]
            to_fade = VGroup(lineup)
            if x == 2:
                question.next_to(lineup, DOWN, buff = MED_LARGE_BUFF)
                anims.append(Write(question))
            if x >= 2:
                arrows = VGroup(*[
                    Vector(DOWN).next_to(w, UP)
                    for w in women
                ])
                arrows.highlight(MAROON_B)
                words = TextMobject("%d women"%len(women))
                words.highlight(MAROON_B)
                words.next_to(arrows, UP)
                anims += [
                    LaggedStart(GrowArrow, arrows),
                    Write(words)
                ]
                to_fade.add(arrows, words)
            self.play(*anims, run_time = 1)
            self.dither()
            self.play(FadeOut(to_fade))
        self.play(question.next_to, title, DOWN)

        self.title = title
        self.question = question

    def mention_all_possibilities(self):
        words = TextMobject("What are all \\\\ the possibilities?")

        last_lineup = None
        for x in xrange(self.n_secondary_examples):
            lineup = self.get_random_lineup_of_men_and_women()
            lineup.scale(1.5)
            lineup.move_to(ORIGIN, DOWN)
            run_time = self.time_per_secondary_example
            if last_lineup is None:
                words.next_to(lineup, DOWN, MED_LARGE_BUFF)
                self.play(
                    FadeIn(lineup),
                    FadeIn(words),
                    run_time = run_time
                )
            else:
                self.play(
                    last_lineup.items.shift, UP,
                    last_lineup.items.fade, 1,
                    *map(GrowFromCenter, lineup.items),
                    run_time = run_time
                )
                self.remove(last_lineup)
            self.add(lineup)
            last_lineup = lineup

        self.lineup = last_lineup
        self.all_possibilities_words = words

    def show_all_possibilities(self):
        man, woman = Male(), Female()

        vects = [
            1.5*UP,
            0.7*UP,
            0.3*UP,
            3.5*RIGHT,
            1.5*RIGHT,
        ]
        lineup_groups = VGroup()
        for k in range(6):
            lineup_group = VGroup()
            for tup in it.product(*[[man, woman]]*k):
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
            FadeOut(self.all_possibilities_words),
            FadeOut(self.question)
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
                self.play(LaggedStart(
                    ApplyMethod, group,
                    lambda m : (m.shift, MED_SMALL_BUFF*RIGHT),
                    rate_func = there_and_back,
                    lag_ratio = 0.9**i,
                    run_time = 1,
                ))
            self.dither()
            curr_lineup_group = lineup_group
        self.lineups = curr_lineup_group

        eq_32 = TexMobject("=", "32")
        eq_32.move_to(twos.get_right())
        eq_32.highlight_by_tex("32", YELLOW)
        self.play(
            n_possibilities[-1].next_to, eq_32, RIGHT,
            twos.next_to, eq_32, LEFT,
            FadeIn(eq_32),
        )
        self.dither()

        n_possibilities.add(*eq_32)
        self.set_variables_as_attrs(n_possibilities)

    def show_all_configurations_with_three_women(self):
        lineups = self.lineups
        items_to_fade = VGroup()
        lines_to_fade = VGroup()
        women_triplets = VGroup()
        for lineup in lineups:
            lineup.women = VGroup(*filter(
                lambda item : "female" in item.get_tex_string(),
                lineup.items
            ))
            if len(lineup.women) == 3:
                women_triplets.add(*lineup.women)
            else:
                items_to_fade.add(lineup.items)
                lines_to_fade.add(lineup.lines)

        self.play(
            lines_to_fade.set_stroke, LIGHT_GREY, 1,
            items_to_fade.set_fill, None, 0.3,
        )
        self.play(
            women_triplets.highlight, YELLOW,
            run_time = 2,
            rate_func = there_and_back
        )
        self.dither()

    def stack_all_choices_by_number_of_women(self):
        lineups = self.lineups
        stacks = VGroup(*[VGroup() for x in range(6)])
        for lineup in lineups:
            stacks[len(lineup.women)].add(lineup)
        stacks.generate_target()
        stacks.target.scale(0.75)
        for stack in stacks.target:
            stack.arrange_submobjects(DOWN, buff = 2*SMALL_BUFF)
        stacks.target.arrange_submobjects(
            RIGHT, buff = MED_LARGE_BUFF, aligned_edge = DOWN
        )
        stacks.target.to_edge(DOWN)

        self.play(MoveToTarget(
            stacks, 
            run_time = 2,
            path_arc = np.pi/2
        ))
        self.dither()

        self.stacks = stacks

    def go_through_stacks(self):
        stacks = self.stacks
        numbers = VGroup()
        for stack in stacks:
            items = VGroup()
            lines = VGroup()
            women = VGroup()
            for lineup in stack:
                items.add(lineup.items)
                lines.add(lineup.lines)
                for item in lineup.items:
                    if "female" in item.get_tex_string():
                        women.add(item)
            number = TexMobject(str(len(stack)))
            number.highlight(YELLOW)
            number.next_to(stack, UP)
            numbers.add(number)

            self.play(
                items.set_fill, None, 1,
                lines.set_stroke, WHITE, 3,
                Write(number)
            )
            self.play(LaggedStart(Indicate, women, rate_func = there_and_back))
        self.dither()

        self.numbers = numbers

    def remember_this_sensation(self):
        n_possibilities = self.n_possibilities
        n_possibilities_rect = SurroundingRectangle(n_possibilities)
        twos = VGroup(*n_possibilities[:5])
        numbers = self.numbers

        self.play(ShowCreation(n_possibilities_rect))
        self.play(LaggedStart(
            Indicate, twos, 
            rate_func = wiggle
        ))
        self.play(FadeOut(n_possibilities_rect))
        for number in numbers:
            self.play(Indicate(number, color = PINK, run_time = 0.5))
        self.dither()

    def show_answer_to_question(self):
        stacks = self.stacks
        numbers = self.numbers
        n_possibilities = self.n_possibilities
        three_stack = stacks[3]
        to_fade = VGroup(*filter(
            lambda s : s is not three_stack,
            stacks
        ))
        to_fade.add(*filter(
            lambda n : n is not numbers[3],
            numbers
        ))
        to_fade.save_state()
        rect = SurroundingRectangle(
            three_stack,
            color = WHITE,
            stroke_width = 2
        )

        numerator = numbers[3]
        denominator = n_possibilities[-1]
        frac_line = TexMobject("\\quad \\over \\quad")
        for mob in numerator, denominator:
            mob.generate_target()
            mob.save_state()
        frac = VGroup(numerator.target, frac_line, denominator.target)
        frac.arrange_submobjects(DOWN, buff = SMALL_BUFF)
        eq_result = TexMobject("= %.2f"%(10.0/32))
        eq_result.move_to(numerator)
        eq_result.to_edge(RIGHT)
        frac.next_to(eq_result, LEFT)
        prob = TexMobject("P(3", "\\female", ")", "=")
        prob.highlight_by_tex("female", MAROON_B)
        prob.next_to(frac, LEFT)

        self.play(
            ShowCreation(rect),
            to_fade.fade, 0.7,
        )
        self.dither()
        self.play(Write(prob))
        self.dither()
        self.play(
            MoveToTarget(numerator),
            MoveToTarget(denominator),
            Write(frac_line)
        )
        self.dither()
        self.play(Write(eq_result))
        self.dither(2)
        self.play(
            numerator.restore,
            denominator.restore,
            to_fade.restore,
            *map(FadeOut, [
                prob, frac_line, eq_result, 
                rect, self.title, self.n_possibilities,
            ])
        )

    def ask_about_pattern(self):
        question = TextMobject("Where do these \\\\ numbers come from?")
        question.to_edge(UP)
        numbers = self.numbers
        circles = VGroup(*[
            Circle().replace(num, dim_to_match = 1).scale_in_place(1.5)
            for num in numbers
        ])
        circles.highlight(WHITE)

        self.play(LaggedStart(FadeIn, question))
        self.play(LaggedStart(ShowCreationThenDestruction, circles))
        self.dither(2)

    ######

    def get_random_lineup_of_men_and_women(self):
        man, woman = Male(), Female()
        lineup = self.get_lineup(*[
            woman if random.choice([True, False]) else man
            for y in range(self.n_people_per_lineup)
        ])
        return lineup

    def get_lineup(self, *mobjects):
        lines = VGroup(*[
            Line(ORIGIN, self.item_line_width*RIGHT)
            for mob in mobjects
        ])
        lines.arrange_submobjects(RIGHT)
        items = VGroup()
        for line, mob in zip(lines, mobjects):
            item = VectorizedPoint() if mob is None else mob.copy()
            item.next_to(line, UP, SMALL_BUFF)
            items.add(item)
        result = VGroup(lines, items)
        result.lines = lines
        result.items = items
        return result

class RememberThisSensation(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("Remember this \\\\ sensation")
        self.change_student_modes("confused", "pondering", "erm")
        self.dither(2)



















