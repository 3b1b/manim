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
    obj_to_obj_buff = SMALL_BUFF,
    vertical_buff = MED_SMALL_BUFF,
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
        term.arrange_submobjects(RIGHT, buff = obj_to_obj_buff)
        stack.add(term)
    stack.arrange_submobjects(DOWN, buff = vertical_buff)
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

    def get_lineup(self, *mobjects, **kwargs):
        buff = kwargs.get("buff", MED_SMALL_BUFF)
        lines = VGroup(*[
            Line(ORIGIN, self.item_line_width*RIGHT)
            for mob in mobjects
        ])
        lines.arrange_submobjects(RIGHT, buff = buff)
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

class GroupsOf6(Scene):
    def construct(self):
        title = TexMobject("2^6 =", "64", "\\text{ Possibilities}")
        title.to_edge(UP, buff = MED_SMALL_BUFF)
        title.highlight_by_tex("64", YELLOW)
        man, woman = Male(), Female()
        stacks = get_stacks(man, woman, 6, vertical_buff = SMALL_BUFF)
        stacks.scale_to_fit_height(6.25)
        stacks.to_edge(DOWN, buff = MED_SMALL_BUFF)
        women_groups = VGroup()
        for stack in stacks:
            for lineup in stack:
                group = VGroup()
                for item in lineup:
                    if "female" in item.get_tex_string():
                        group.add(item)
                women_groups.add(group)

        numbers = VGroup()
        for stack in stacks:
            number = TexMobject(str(len(stack)))
            number.next_to(stack, UP, SMALL_BUFF)
            numbers.add(number)

        self.add(title)
        self.play(LaggedStart(
            LaggedStart, stacks,
            lambda s : (FadeIn, s),
            run_time = 3,
        ))
        self.play(Write(numbers, run_time = 3))
        self.dither()
        self.play(LaggedStart(
            ApplyMethod, women_groups,
            lambda m : (m.highlight, PINK),
            lag_ratio = 0.1,
            rate_func = wiggle,
            run_time = 6,
        ))

class GroupsOf7(Scene):
    def construct(self):
        stack = get_stack(Male(), Female(), 7, 3)
        question = TextMobject(
            "How many groups \\\\ of 7 with 3 ", "$\\female$", "?"
        )
        question.highlight_by_tex("female", MAROON_B)
        question.shift(1.5*UP)

        self.add(question)
        for n, item in enumerate(stack):
            item.center()
            number = TexMobject(str(n))
            number.next_to(ORIGIN, DOWN, LARGE_BUFF)
            self.add(item, number)
            self.dither(0.2)
            self.remove(item, number)
        self.add(item, number)
        self.dither(2)

class BuildFiveFromFour(ProbabilityOfThreeWomenInGroupOfFive):
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
            self.dither()
            curr_lineup_group = lineup_group
        self.lineups = curr_lineup_group

        eq_16 = TexMobject("=", "16")
        eq_16.move_to(twos.get_right())
        eq_16.highlight_by_tex("16", YELLOW)
        self.play(
            n_possibilities[-1].next_to, eq_16, RIGHT,
            twos.next_to, eq_16, LEFT,
            FadeIn(eq_16),
        )
        self.dither()

        n_possibilities.add(eq_16)
        self.n_possibilities = n_possibilities

    def organize_into_stacks(self):
        lineups = self.lineups
        stacks = VGroup(*[VGroup() for x in range(5)])
        for lineup in lineups:
            women = filter(
                lambda m : "female" in m.get_tex_string(),
                lineup.items
            )
            stacks[len(women)].add(lineup)
        stacks.generate_target()
        stacks.target.scale(0.75)
        for stack in stacks.target:
            stack.arrange_submobjects(DOWN, buff = SMALL_BUFF)
        stacks.target.arrange_submobjects(
            RIGHT, buff = MED_LARGE_BUFF, aligned_edge = DOWN
        )
        stacks.target.to_edge(DOWN, buff = MED_SMALL_BUFF)

        self.play(MoveToTarget(
            stacks, 
            run_time = 2,
            path_arc = np.pi/2
        ))
        self.dither()

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
                lineup_copy.highlight(YELLOW)
                number = TexMobject(str(n+1))
                number.next_to(stack, UP)
                self.add(lineup_copy, number)
                self.dither(0.25)
                self.remove(lineup_copy, number)
            self.add(number)
            numbers.add(number)
            self.play(FadeOut(rect))
        self.dither()

        stacks.numbers = numbers

    def split_into_two_possibilities(self):
        bottom_stacks = self.stacks
        top_stacks = bottom_stacks.deepcopy()
        top_group = VGroup(top_stacks, top_stacks.numbers)

        h_line = DashedLine(SPACE_WIDTH*LEFT, SPACE_WIDTH*RIGHT)

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
            new_stacks.arrange_submobjects(
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
        self.dither()

        #Fill extra slot
        add_man = TextMobject("Add", "$\\male$")
        add_man.highlight_by_tex("male", BLUE)
        add_woman = TextMobject("Add", "$\\female$")
        add_woman.highlight_by_tex("female", MAROON_B)

        add_man.next_to(ORIGIN, DOWN).to_edge(LEFT)
        add_woman.to_corner(UP+LEFT)

        for stacks, words in (bottom_stacks, add_man), (top_stacks, add_woman):
            to_fade_in = stacks.to_fade_in
            to_fade_in.set_fill(opacity = 1)
            to_fade_in.save_state()
            Transform(to_fade_in, VGroup(words[-1])).update(1)

            self.play(Write(words, run_time = 1))
            self.play(to_fade_in.restore)
            self.dither()

        #Perform shift
        dist = top_stacks[1].get_center()[0] - top_stacks[0].get_center()[0]
        self.play(
            top_stacks.shift, dist*RIGHT/2,
            top_stacks.numbers.shift, dist*RIGHT/2,
            bottom_stacks.shift, dist*LEFT/2,
            bottom_stacks.numbers.shift, dist*LEFT/2,
        )
        self.dither()
        self.play(*map(FadeOut, [add_man, add_woman, h_line]))

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

        self.play(LaggedStart(ShowCreation, rects, run_time = 1))
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
            expr.arrange_submobjects(RIGHT, buff = SMALL_BUFF)
            expr.next_to(top_stack.target.get_top(), UP)

            new_number = TexMobject(str(
                len(top_stack) + len(bottom_stack) - 2
            ))
            new_number.next_to(expr, UP)
            new_numbers.add(new_number)

            self.play(
                Write(plus),
                *map(MoveToTarget, movers)
            )
        self.play(
            VGroup(top_stacks[-1], top_stacks.numbers[-1]).align_to,
            bottom_stacks, DOWN
        )
        self.dither()

        new_numbers.add_to_back(bottom_stacks.numbers[0].copy())
        new_numbers.add(top_stacks.numbers[-1].copy())
        new_numbers.highlight(PINK)
        self.play(Write(new_numbers, run_time = 3))
        self.dither()

class BuildUpFromStart(Scene):
    CONFIG = {
        "n_iterations" : 7,
    }
    def construct(self):
        stacks = VGroup(VGroup(Male()), VGroup(Female()))
        stacks.arrange_submobjects(RIGHT, buff = LARGE_BUFF)
        stacks.numbers = self.get_numbers(stacks)

        max_width = 2*SPACE_WIDTH - 3
        max_height = SPACE_HEIGHT - 1

        self.add(stacks, stacks.numbers)
        for x in range(self.n_iterations):
            if x < 2:
                dither_time = 1
            else:
                dither_time = 0.2
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
            self.play(*map(MoveToTarget, [top_group, low_group]))
            self.dither(dither_time)

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
                new_stacks.arrange_submobjects(
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
            self.play(*map(MoveToTarget, [
                top_stacks, low_stacks,
                top_stacks.numbers, low_stacks.numbers,
            ]))
            self.dither(dither_time)

            #Shift
            dist = top_stacks[1].get_center()[0] - top_stacks[0].get_center()[0]
            self.play(
                top_group.shift, dist*RIGHT/2,
                low_group.shift, dist*LEFT/2,
            )
            self.dither(dither_time)

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
                expr.arrange_submobjects(RIGHT, buff = SMALL_BUFF)
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
                map(MoveToTarget, all_movers),
                map(Write, plusses),
            ))

            #Add
            new_numbers = self.get_numbers(stacks)
            self.play(ReplacementTransform(
                expressions, VGroup(*map(VGroup, new_numbers))
            ))
            self.dither(dither_time)
            stacks.numbers = new_numbers


    ####

    def get_numbers(self, stacks):
        return VGroup(*[
            TexMobject(str(len(stack))).next_to(stack, UP)
            for stack in stacks
        ])

class PascalsTriangle(Scene):
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
        distance = 0.8
        max_width = 0.7*distance
        angle = 0.2*np.pi
        t_down = rotate_vector(distance*DOWN, -angle)
        t_right = 2*distance*np.sin(angle)*RIGHT

        rows = VGroup()
        for n in range(self.max_n + 1):
            row = VGroup()
            for k in range(n+1):
                num = TexMobject(str(choose(n, k)))
                # if num.get_width() > max_width:
                #     num.scale_to_fit_width(max_width)
                num.shift(n*t_down + k*t_right)
                row.add(num)
            rows.add(row)
        rows.to_edge(UP)

        self.play(FadeIn(rows[1]))
        for last_row, curr_row in zip(rows[1:], rows[2:]):
            self.play(*[
                Transform(
                    last_row.copy(), VGroup(*mobs),
                    remover = True
                )
                for mobs in curr_row[1:], curr_row[:-1]
            ])
            self.add(curr_row)
        self.dither()

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

        rows_to_fade = VGroup(*rows[1:4] + rows[6:])
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
        self.dither(2)
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
        self.dither(2)
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
        self.dither()

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
            LaggedStart(
                Indicate, numbers,
                rate_func = wiggle,
                color = PINK,
            )
        )
        self.play(*map(FadeOut, [
            morty, morty.bubble, morty.bubble.content
        ]))

    def issolate_9_choose_4_term(self):
        rows = self.rows

        for n in range(1, self.max_n+1):
            num = rows[n][0]
            line = get_stack(Female(), Male(), n, 0)[0]
            if n < self.max_n:
                line.next_to(num, LEFT)
            else:
                line.next_to(num, DOWN, MED_LARGE_BUFF)
            self.highlight_num(num)
            self.add(line)
            if n < self.max_n:
                self.dither(0.25)
            else:
                self.dither(1.25)
            self.dehighlight_num(num)
            self.remove(line)
        for k in range(1, 5):
            num = rows[self.max_n][k]
            line = get_stack(Female(), Male(), self.max_n, k)[0]
            line.next_to(num, DOWN, MED_LARGE_BUFF)
            self.highlight_num(num)
            self.add(line)
            self.dither(0.5)
            self.dehighlight_num(num)
            self.remove(line)
        num.highlight(YELLOW)
        num.scale_in_place(1.2)
        self.add(line)
        self.dither()

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
            self.dither(0.1)
            self.remove(line, num)
        self.add(line, num)
        self.dither()
        self.curr_line = line

        #Probability
        expr = TexMobject(
            "P(4", "\\female", "\\text{ out of }", "9", ")", "="
        )
        expr.move_to(num.get_left())
        expr.highlight_by_tex("female", MAROON_B)
        nine_choose_four_term = self.nine_choose_four_term.copy()
        nine_choose_four_term.generate_target()
        nine_choose_four_term.target.scale(1./1.2)
        over_512 = TexMobject("\\quad \\over 2^9")
        frac = VGroup(nine_choose_four_term.target, over_512)
        frac.arrange_submobjects(DOWN, buff = SMALL_BUFF)
        frac.next_to(expr, RIGHT, SMALL_BUFF)
        eq_result = TexMobject("\\approx 0.246")
        eq_result.next_to(frac, RIGHT)

        def show_random_lines(n, dither_time = 1):
            for x in range(n):
                if x == n-1:
                    dither_time = 0
                new_line = random.choice(all_lines)
                new_line.move_to(self.curr_line)
                self.remove(self.curr_line)
                self.curr_line = new_line
                self.add(self.curr_line)
                self.dither(dither_time)

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
            self.nine_choose_four_term.highlight, WHITE,
            *map(FadeOut, [
                expr, nine_choose_four_term,
                over_512, eq_result, self.curr_line
            ])
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
            line.arrange_submobjects(RIGHT, SMALL_BUFF)
            line.shift(SPACE_WIDTH*RIGHT/2 + SPACE_HEIGHT*UP/2)
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
        self.dither()
        curr_line_group = line_groups[0]
        self.play(FadeIn(curr_line_group))
        for line_group in line_groups[1:]:
            self.play(ReplacementTransform(
                curr_line_group, line_group
            ))
            curr_line_group = line_group
        self.dither()

    ###

    def highlight_num(self, num):
        num.highlight(YELLOW)
        num.scale_in_place(1.2)

    def dehighlight_num(self, num):
        num.highlight(WHITE)
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

        max_width = 2*SPACE_WIDTH - 2
        max_height = SPACE_HEIGHT - 1.5

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
                    #     number.scale_to_fit_width(bar.get_width())
                    number.next_to(bar, UP, SMALL_BUFF)

            self.play(*map(MoveToTarget, [
                bars, bars_copy,
                numbers, numbers_copy
            ]))
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
                    mob.scale_to_fit_height(height)

            bars_copy.target[-1].align_to(bars, DOWN)
            numbers_copy.target[-1].next_to(bars_copy.target[-1], UP, SMALL_BUFF)

            self.play(*[
                MoveToTarget(mob, submobject_mode = "lagged_start")
                for mob in bars_copy, numbers, numbers_copy
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
        self.dither()

class IsThereABetterWayToCompute(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Is there a better \\\\ way to compute these?",
            target_mode = "raise_left_hand",
        )
        self.change_student_modes("confused", "raise_left_hand", "erm")
        self.dither()
        self.play(self.teacher.change_mode, "happy")
        self.dither()
        self.teacher_says(
            "There is!  But first...",
            target_mode = "hooray"
        )
        self.dither(2)

class ChooseThreeFromFive(Scene):
    def construct(self):
        self.add_people()
        self.choose_random_triplets()
        self.mention_equivalence_to_previous_question()
        self.show_association_with_binary()
        self.show_how_many_have_ali()
        self.show_four_choose_two_in_binary()

    def add_people(self):
        pass
        
    def choose_random_triplets(self):
        pass
        
    def mention_equivalence_to_previous_question(self):
        pass
        
    def show_association_with_binary(self):
        pass
        
    def show_how_many_have_ali(self):
        pass
        
    def show_four_choose_two_in_binary(self):
        pass
        























