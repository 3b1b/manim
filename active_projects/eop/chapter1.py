from big_ol_pile_of_manim_imports import *
from old_projects.eoc.chapter8 import *
from active_projects.eop.histograms import *
from active_projects.eop.independence import *
from active_projects.eop.combinations import *

import scipy.special
import itertools as it


COIN_RADIUS = 0.18
COIN_THICKNESS = 0.4 * COIN_RADIUS
COIN_FORESHORTENING = 0.5
COIN_NB_RIDGES = 20
COIN_STROKE_WIDTH = 2

COIN_SEQUENCE_SPACING = 0.1

GRADE_COLOR_1 = COLOR_HEADS = RED
GRADE_COLOR_2 = COLOR_TAILS = BLUE_E

TALLY_BACKGROUND_WIDTH = 1.0
TALLY_BACKGROUND_COLOR = BLACK

def get_example_quiz():
    quiz = get_quiz(
        "Define ``Brachistochrone'' ",
        "Define ``Tautochrone'' ",
        "Define ``Cycloid'' ",
    )
    rect = SurroundingRectangle(quiz, buff = 0)
    rect.set_fill(color = BLACK, opacity = 1)
    rect.set_stroke(width = 0)
    quiz.add_to_back(rect)
    return quiz

def binary(i):
    # returns an array of 0s and 1s
    if i == 0:
        return []
    j = i
    binary_array = []
    while j > 0:
        jj = j/2
        if jj > 0:
            binary_array.append(j % 2)
        else:
            binary_array.append(1)
        j = jj
    return binary_array[::-1]

def nb_of_ones(i):
    return binary(i).count(1)


def rainbow_color(alpha):
    nb_colors = 100
    rainbow = color_gradient([RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE], nb_colors)
    rainbow = np.append(rainbow,PURPLE)
    index = int(alpha * nb_colors)
    return rainbow[index]

def graded_color(n,k):
    if n != 0:
        alpha = float(k)/n
    else:
        alpha = 0.5
    color = interpolate_color(GRADE_COLOR_1, GRADE_COLOR_2, alpha)
    return color


class PiCreatureCoin(VMobject):
    CONFIG = {
        "diameter": 0.8,
        "thickness": 0.2,
        "nb_ridges" : 7,
        "stroke_color": YELLOW,
        "stroke_width": 3,
        "fill_color": YELLOW,
        "fill_opacity": 0.7,
    }

    def generate_points(self):
        outer_rect = Rectangle(
            width = self.diameter,
            height = self.thickness,
            fill_color  = self.fill_color,
            fill_opacity = self.fill_opacity,
            stroke_color = self.stroke_color,
            stroke_width = 0, #self.stroke_width
        )
        self.add(outer_rect)
        PI = TAU/2
        ridge_angles = np.arange(PI/self.nb_ridges,PI,PI/self.nb_ridges)
        ridge_positions = 0.5 * self.diameter * np.array([
            np.cos(theta) for theta in ridge_angles
        ])
        ridge_color = interpolate_color(BLACK,self.stroke_color,0.5)
        for x in ridge_positions:
            ridge = Line(
                x * RIGHT + 0.5 * self.thickness * DOWN,
                x * RIGHT + 0.5 * self.thickness * UP,
                stroke_color = ridge_color,
                stroke_width = self.stroke_width
            )
            self.add(ridge)

class CoinFlippingPiCreature(PiCreature):

    def __init__(self, mode = "coin_flip_1", **kwargs):

        coin = PiCreatureCoin()
        PiCreature.__init__(self, mode = mode, **kwargs)
        self.coin = coin
        self.add(coin)
        right_arm = self.get_arm_copies()[1]
        coin.rotate(-TAU/24)
        coin.next_to(right_arm, RIGHT+UP, buff = 0)
        coin.shift(0.1 * self.get_width() * LEFT)
        coin.shift(0.2 * DOWN)

    def flip_coin_up(self):
        self.change("coin_flip_2")



class FlipUpAndDown(Animation):
    CONFIG = {
        "vector" : UP,
        "height" : 3,
        "nb_turns" : 1
    }

    def update(self,t):
        self.mobject.shift(self.height * 4 * t * (1 - t) * self.vector)
        self.mobject.rotate(t * self.nb_turns * TAU)

class FlipCoin(AnimationGroup):
    CONFIG = {
        "coin_rate_func" : there_and_back,
        "pi_rate_func" : lambda t : there_and_back_with_pause(t, 1./4)
    }
    def __init__(self, pi_creature, **kwargs):
        digest_config(self, kwargs)
        pi_creature_motion = ApplyMethod(
            pi_creature.flip_coin_up,
            rate_func = self.pi_rate_func,
            **kwargs
        )
        coin_motion = Succession(
            EmptyAnimation(run_time = 1.0),
            FlipUpAndDown(
                pi_creature.coin, 
                vector = UP,
                nb_turns = 5,
                rate_func = self.coin_rate_func,
                **kwargs
            )
        )
        AnimationGroup.__init__(self,pi_creature_motion, coin_motion)

class CoinFlippingPiCreatureScene(Scene):

    def construct(self):

        randy = CoinFlippingPiCreature(color = MAROON_E)
        self.add(randy)
        self.play(FlipCoin(randy, run_time = 3))


class UprightCoin(Circle):
# For use in coin sequences
    CONFIG = {
        "radius": COIN_RADIUS,
        "stroke_width": COIN_STROKE_WIDTH,
        "stroke_color": WHITE,
        "fill_opacity": 1,
        "symbol": "\euro"
    }

    def __init__(self, **kwargs):
        Circle.__init__(self,**kwargs)
        self.symbol_mob = TextMobject(self.symbol, stroke_color = self.stroke_color)
        self.symbol_mob.scale_to_fit_height(0.5*self.get_height()).move_to(self)
        self.add(self.symbol_mob)

class UprightHeads(UprightCoin):
    CONFIG = {
        "fill_color": COLOR_HEADS,
        "symbol": "H",
    }

class UprightTails(UprightCoin):
    CONFIG = {
        "fill_color": COLOR_TAILS,
        "symbol": "T",
    }

class CoinSequence(VGroup):
    CONFIG = {
        "sequence": [],
        "spacing": COIN_SEQUENCE_SPACING,
        "direction": RIGHT
    }

    def __init__(self, sequence, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.sequence = sequence
        offset = 0
        for symbol in self.sequence:
            if symbol == "H":
                new_coin = UprightHeads()
            elif symbol == "T":
                new_coin = UprightTails()
            else:
                new_coin = UprightCoin(symbol = symbol)
            new_coin.shift(offset * self.direction)
            self.add(new_coin)
            offset += self.spacing


class FlatCoin(UprightCoin):
# For use in coin stacks
    CONFIG = {
        "thickness": COIN_THICKNESS,
        "foreshortening": COIN_FORESHORTENING,
        "nb_ridges": COIN_NB_RIDGES
    }

    def __init__(self, **kwargs):
        UprightCoin.__init__(self, **kwargs)
        self.symbol_mob.rotate(TAU/8)
        self.stretch_in_place(self.foreshortening, 1)
        
        # draw the edge
        control_points1 = self.points[12:25].tolist()
        control_points2 = self.copy().shift(self.thickness * DOWN).points[12:25].tolist()
        edge_anchors_and_handles = control_points1
        edge_anchors_and_handles.append(edge_anchors_and_handles[-1] + self.thickness * DOWN)
        edge_anchors_and_handles.append(edge_anchors_and_handles[-1] + self.thickness * UP)
        edge_anchors_and_handles += control_points2[::-1] # list concatenation
        edge_anchors_and_handles.append(edge_anchors_and_handles[-1] + self.thickness * UP)
        edge_anchors_and_handles.append(edge_anchors_and_handles[-1] + self.thickness * DOWN)
        edge_anchors_and_handles.append(control_points1[0])
        #edge_anchors_and_handles = edge_anchors_and_handles[::-1]
        edge = VMobject()
        edge.set_points(edge_anchors_and_handles)
        edge.set_fill(
            color = self.fill_color,
            opacity = self.fill_opacity
        )
        edge.set_stroke(width = self.stroke_width)
        self.add(edge)

        # draw the ridges
        PI = TAU/2
        dtheta = PI/self.nb_ridges
        ridge_angles = np.arange(dtheta,PI,dtheta)
        # add a twist onto each coin
        ridge_angles += np.random.rand(1) * dtheta
        # crop the angles that overshoot on either side
        ridge_angles = ridge_angles[(ridge_angles > 0) * (ridge_angles < PI)]
        ridge_positions = 0.5 * 2 * self.radius * np.array([
            np.cos(theta) for theta in ridge_angles
        ])
        ridge_color = interpolate_color(self.stroke_color, self.fill_color, 0.7)
        for x in ridge_positions:
            y = -(1 - (x/self.radius)**2)**0.5 * self.foreshortening * self.radius
            ridge = Line(
                x * RIGHT + y * UP,
                x * RIGHT + y * UP + self.thickness * DOWN,
                stroke_color = ridge_color,
                stroke_width = self.stroke_width
            )
            self.add(ridge)

        # redraw the unfilled edge to cover the ridge ends
        empty_edge = edge.copy()
        empty_edge.set_fill(opacity = 0)
        self.add(empty_edge)

class FlatHeads(FlatCoin):
    CONFIG = {
        "fill_color": COLOR_HEADS,
        "symbol": "H",
    }
    
class FlatTails(FlatCoin):
    CONFIG = {
        "fill_color": COLOR_TAILS,
        "symbol": "T",
    }
    
class CoinStack(VGroup):
    CONFIG = {
        "coin_thickness": COIN_THICKNESS,
        "size": 5,
        "face": FlatCoin,
    }

    def generate_points(self):
        for n in range(self.size):
            coin = self.face(thickness = self.coin_thickness)
            coin.shift(n * self.coin_thickness * UP)
            self.add(coin)

class HeadsStack(CoinStack):
    CONFIG = {
        "face": FlatHeads
    }

class TailsStack(CoinStack):
    CONFIG = {
        "face": FlatTails
    }

class TallyStack(VGroup):
    CONFIG = {
        "coin_thickness": COIN_THICKNESS,
        "show_decimals": True
    }

    def __init__(self, h, t, anchor = ORIGIN, **kwargs):
        self.nb_heads = h
        self.nb_tails = t
        self.anchor = anchor
        VGroup.__init__(self,**kwargs)

    def generate_points(self):
        stack1 = HeadsStack(size = self.nb_heads, coin_thickness = self.coin_thickness)
        stack2 = TailsStack(size = self.nb_tails, coin_thickness = self.coin_thickness)
        stack1.next_to(self.anchor, LEFT, buff = 0.5 * SMALL_BUFF)
        stack2.next_to(self.anchor, RIGHT, buff = 0.5 * SMALL_BUFF)
        stack1.align_to(self.anchor, DOWN)
        stack2.align_to(self.anchor, DOWN)
        self.heads_stack = stack1
        self.tails_stack = stack2
        self.add(stack1, stack2)
        self.background_rect = background_rect = RoundedRectangle(
            width = TALLY_BACKGROUND_WIDTH,
            height = TALLY_BACKGROUND_WIDTH,
            corner_radius = 0.1,
            fill_color = TALLY_BACKGROUND_COLOR,
            fill_opacity = 1.0,
            stroke_width = 3
        ).align_to(self.anchor, DOWN).shift(0.1 * DOWN)
        self.add_to_back(background_rect)

        self.decimal_tally = DecimalTally(self.nb_heads, self.nb_tails)
        self.position_decimal_tally(self.decimal_tally)
        if self.show_decimals:
            self.add(self.decimal_tally)

    def position_decimal_tally(self, decimal_tally):
        decimal_tally.match_width(self.background_rect)
        decimal_tally.scale(0.6)
        decimal_tally.next_to(self.background_rect.get_top(), DOWN, buff = 0.15)
        return decimal_tally


    def move_anchor_to(self, new_anchor):
        for submob in self.submobjects:
            submob.shift(new_anchor - self.anchor)

        self.anchor = new_anchor
        self.position_decimal_tally(self.decimal_tally)

        return self

class CoinFlipTree(VGroup):
    CONFIG = {
        "total_width": 12,
        "level_height": 0.8,
        "nb_levels": 4,
        "sort_until_level": 3
    }

    def __init__(self, **kwargs):

        VGroup.__init__(self, **kwargs)

        self.rows = []
        for n in range(self.nb_levels + 1):
            if n <= self.sort_until_level:
                self.create_row(n, sorted = True)
            else:
                self.create_row(n, sorted = False)
            

        for row in self.rows:
            for leaf in row:
                dot = Dot()
                dot.move_to(leaf[0])
                line = Line(leaf[2], leaf[0])
                if leaf[2][0] > leaf[0][0]:
                    line_color = COLOR_HEADS
                else:
                    line_color = COLOR_TAILS
                line.set_stroke(color = line_color)
                group = VGroup()
                group.add(dot)
                group.add_to_back(line)
                self.add(group)




    def create_row(self, level, sorted = True):

        if level == 0:
            new_row = [[ORIGIN,0,ORIGIN]] # is its own parent
            self.rows.append(new_row)
            return

        previous_row = self.rows[level - 1]
        new_row = []
        dx = float(self.total_width) / (2 ** level)
        x = - 0.5 * self.total_width + 0.5 * dx
        y = - self.level_height * level
        for root in previous_row:
            root_point = root[0]
            root_tally = root[1]
            for i in range(2): # 0 = heads = left, 1 = tails = right
                leaf = x * RIGHT + y * UP
                new_row.append([leaf, root_tally + i, root_point]) # leaf and its parent
                x += dx

        if sorted:
            # sort the new_row by its tallies
            sorted_row = []
            x = - 0.5 * self.total_width + 0.5 * dx
            for i in range(level + 1):
                for leaf in new_row:
                    if leaf[1] == i:
                        sorted_leaf = leaf
                        sorted_leaf[0][0] = x
                        x += dx
                        sorted_row.append(leaf)
            self.rows.append(sorted_row)
        else:
            self.rows.append(new_row)





class Chapter1OpeningQuote(OpeningQuote):
    CONFIG = {
        "fade_in_kwargs": {
            "submobject_mode": "lagged_start",
            "rate_func": None,
            "lag_factor": 9,
            "run_time": 10,
        },
        "text_size" : "\\normalsize",
        "use_quotation_marks": False,
        "quote" : [
            "To see a world in a grain of sand\\\\",
            "And a heaven in a wild flower,\\\\",
            "Hold infinity in the palm of your hand\\\\",
            "\phantom{r}And eternity in an hour.\\\\"
        ],
        "quote_arg_separator" : " ",
        "highlighted_quote_terms" : {},
        "author" : "William Blake: \\\\ \emph{Auguries of Innocence}",
    }

class Introduction(TeacherStudentsScene):

    CONFIG = {
        "default_pi_creature_kwargs": {
        "color": MAROON_E,
        "flip_at_start": True,
        },
    }

    def construct(self):
        
        self.wait(5)
        
        self.change_student_modes(
            "confused", "frustrated", "dejected",
            look_at_arg = UP + 2 * RIGHT
        )

        self.wait()


        self.get_teacher().change_mode("raise_right_hand")
        self.wait()

        self.wait(30)
        # put examples here in video editor


        # # # # # # # # # # # # # # # # # #
        # show examples of the area model #
        # # # # # # # # # # # # # # # # # #
        

class IllustrateAreaModel1(Scene):

    def construct(self):

        color_A = YELLOW
        color_not_A = YELLOW_E
        color_B = MAROON
        color_not_B = MAROON_E
        opacity_B = 0.7


        # show independent events

        sample_space_width = sample_space_height = 3
        p_of_A = 0.7
        p_of_not_A = 1 - p_of_A
        p_of_B = 0.8
        p_of_not_B = 1 - p_of_B


        rect_A = Rectangle(
            width = p_of_A * sample_space_width,
            height = 1 * sample_space_height,
            stroke_width = 0,
            fill_color = color_A,
            fill_opacity = 1.0
        ).move_to(3 * RIGHT + 1.5 * UP)

        rect_not_A = Rectangle(
            width = p_of_not_A * sample_space_width,
            height = 1 * sample_space_height,
            stroke_width = 0,
            fill_color = color_not_A,
            fill_opacity = 1.0
        ).next_to(rect_A, RIGHT, buff = 0)

        brace_A = Brace(rect_A, DOWN)
        label_A = TexMobject("P(A)").next_to(brace_A, DOWN).scale(0.7)
        brace_not_A = Brace(rect_not_A, DOWN)
        label_not_A = TexMobject("P(\\text{not }A)").next_to(brace_not_A, DOWN).scale(0.7)

        # self.play(
        #     LaggedStart(FadeIn, VGroup(rect_A, rect_not_A), lag_factor = 0.5)
        # )
        # self.play(
        #     ShowCreation(brace_A),
        #     Write(label_A),
        # )



        rect_B = Rectangle(
            width = 1 * sample_space_width,
            height = p_of_B * sample_space_height,
            stroke_width = 0,
            fill_color = color_B,
            fill_opacity = opacity_B
        )
        rect_not_B = Rectangle(
            width = 1 * sample_space_width,
            height = p_of_not_B * sample_space_height,
            stroke_width = 0,
            fill_color = color_not_B,
            fill_opacity = opacity_B
        ).next_to(rect_B, UP, buff = 0)

        VGroup(rect_B, rect_not_B).move_to(VGroup(rect_A, rect_not_A))

        brace_B = Brace(rect_B, LEFT)
        label_B = TexMobject("P(B)").next_to(brace_B, LEFT).scale(0.7)
        brace_not_B = Brace(rect_not_B, LEFT)
        label_not_B = TexMobject("P(\\text{not }B)").next_to(brace_not_B, LEFT).scale(0.7)

        # self.play(
        #     LaggedStart(FadeIn, VGroup(rect_B, rect_not_B), lag_factor = 0.5)
        # )
        # self.play(
        #     ShowCreation(brace_B),
        #     Write(label_B),
        # )

        rect_A_and_B = Rectangle(
            width = p_of_A * sample_space_width,
            height = p_of_B * sample_space_height,
            stroke_width = 3,
            fill_opacity = 0.0
        ).align_to(rect_A, DOWN).align_to(rect_A,LEFT)
        label_A_and_B = TexMobject("P(A\\text{ and }B)").scale(0.7)
        label_A_and_B.move_to(rect_A_and_B)

        # self.play(
        #     ShowCreation(rect_A_and_B)
        # )

        indep_formula = TexMobject("P(A\\text{ and }B)", "=", "P(A)", "\cdot", "P(B)")
        indep_formula = indep_formula.scale(0.7)
        label_p_of_b = indep_formula.get_part_by_tex("P(B)")

        label_A_and_B_copy = label_A_and_B.copy()
        label_A_copy = label_A.copy()
        label_B_copy = label_B.copy()
        # self.add(label_A_and_B_copy, label_A_copy, label_B_copy)

        # self.play(Transform(label_A_and_B_copy, indep_formula[0]))
        # self.play(FadeIn(indep_formula[1]))
        # self.play(Transform(label_A_copy, indep_formula[2]))
        # self.play(FadeIn(indep_formula[3]))
        # self.play(Transform(label_B_copy, indep_formula[4]))

        #self.wait()

        label_A_and_B_copy = indep_formula[0]
        label_A_copy = indep_formula[2]
        label_B_copy = indep_formula[4]

        # show conditional prob

        rect_A_and_B.set_fill(color = RED, opacity = 0.5)
        rect_A_and_not_B = Rectangle(
            width = p_of_A * sample_space_width,
            height = p_of_not_B * sample_space_height,
            stroke_width = 0,
            fill_color = color_not_B,
            fill_opacity = opacity_B
        ).next_to(rect_A_and_B, UP, buff = 0)
        
        rect_not_A_and_B = Rectangle(
            width = p_of_not_A * sample_space_width,
            height = p_of_B * sample_space_height,
            stroke_width = 0,
            fill_color = color_B,
            fill_opacity = opacity_B
        ).next_to(rect_A_and_B, RIGHT, buff = 0)

        rect_not_A_and_not_B = Rectangle(
            width = p_of_not_A * sample_space_width,
            height = p_of_not_B * sample_space_height,
            stroke_width = 0,
            fill_color = color_not_B,
            fill_opacity = opacity_B
        ).next_to(rect_not_A_and_B, UP, buff = 0)


        indep_formula.next_to(rect_not_A, LEFT, buff = 5)
        #indep_formula.shift(UP)

        self.play(Write(indep_formula))

        self.play(
            FadeIn(VGroup(
                rect_A, rect_not_A, brace_A, label_A, brace_B, label_B,
                rect_A_and_not_B, rect_not_A_and_B, rect_not_A_and_not_B,
                rect_A_and_B,
                label_A_and_B,
            ))
        )

        self.wait()


        p_of_B_knowing_A = 0.6
        rect_A_and_B.target = Rectangle(
            width = p_of_A * sample_space_width,
            height = p_of_B_knowing_A * sample_space_height,
            stroke_width = 3,
            fill_color = color_B,
            fill_opacity = opacity_B
        ).align_to(rect_A_and_B, DOWN).align_to(rect_A_and_B, LEFT)

        rect_A_and_not_B.target = Rectangle(
            width = p_of_A * sample_space_width,
            height = (1 - p_of_B_knowing_A) * sample_space_height,
            stroke_width = 0,
            fill_color = color_not_B,
            fill_opacity = opacity_B
        ).next_to(rect_A_and_B.target, UP, buff = 0)

        brace_B.target = Brace(rect_A_and_B.target, LEFT)
        label_B.target = TexMobject("P(B\mid A)").scale(0.7).next_to(brace_B.target, LEFT)


        self.play(
            MoveToTarget(rect_A_and_B),
            MoveToTarget(rect_A_and_not_B),
            MoveToTarget(brace_B),
            MoveToTarget(label_B),
            label_A_and_B.move_to,rect_A_and_B.target
        )
        label_B_knowing_A = label_B

        #self.play(FadeOut(label_B_copy))
        self.remove(indep_formula.get_part_by_tex("P(B)"))
        indep_formula.remove(indep_formula.get_part_by_tex("P(B)"))
        label_B_knowing_A_copy = label_B_knowing_A.copy()
        self.add(label_B_knowing_A_copy)

        self.play(
            label_B_knowing_A_copy.next_to, indep_formula.get_part_by_tex("\cdot"), RIGHT,
        )

        # solve formula for P(B|A)

        rearranged_formula = TexMobject(["P(B\mid A)", "=", "{P(A\\text{ and }B) \over P(A)}"])
        rearranged_formula.move_to(indep_formula)

        self.wait()


        self.play(
            # in some places get_part_by_tex does not find the correct part
            # so I picked out fitting indices
            label_B_knowing_A_copy.move_to, rearranged_formula.get_part_by_tex("P(B\mid A)"),
            label_A_copy.move_to, rearranged_formula[-1][10],
            label_A_and_B_copy.move_to, rearranged_formula[-1][3],
            indep_formula.get_part_by_tex("=").move_to, rearranged_formula.get_part_by_tex("="),
            Transform(indep_formula.get_part_by_tex("\cdot"), rearranged_formula[2][8]),
        )

        rect = SurroundingRectangle(rearranged_formula, buff = 0.5 * MED_LARGE_BUFF)
        self.play(ShowCreation(rect))


        self.wait()





class IllustrateAreaModel2(GraphScene):
    CONFIG = {
        "x_min" : -3.0,
        "x_max" : 3.0,
        "y_min" : 0,
        "y_max" : 1.0,
        "num_rects": 400,
        "y_axis_label" : "",
        "x_axis_label" : "",
        "variable_point_label" : "a",
        "graph_origin": 2.5 * DOWN + 4 * RIGHT,
        "x_axis_width": 5,
        "y_axis_height": 5
    }

    def construct(self):

        # integral bounds
        x_min_1 = -0.0001
        x_max_1 = 0.0001

        x_min_2 = self.x_min
        x_max_2 = self.x_max

        self.setup_axes()
        self.remove(self.x_axis, self.y_axis)
        graph = self.get_graph(lambda x: np.exp(-x**2) * 2.0 / TAU ** 0.5)
        area = self.area = self.get_area(graph, x_min_1, x_max_1)


        pdf_formula = TexMobject("p(x) = {1\over \sigma\sqrt{2\pi}}e^{-{1\over 2}({x\over\sigma})^2}")
        pdf_formula.set_color(graph.color)

        cdf_formula = TexMobject("P(|X| < ", "a", ") = \int", "_{-a}", "^a", "p(x) dx")
        cdf_formula.set_color_by_tex("a", YELLOW)
        cdf_formula.next_to(graph, LEFT, buff = 2)
        pdf_formula.next_to(cdf_formula, UP)

        formulas = VGroup(pdf_formula, cdf_formula)
        self.play(Write(pdf_formula))
        self.play(Write(cdf_formula))
        
        self.wait()


        self.play(ShowCreation(self.x_axis))
        self.play(ShowCreation(graph))
        self.play(FadeIn(area))

        self.v_graph = graph
        self.add_T_label(
            x_min_1,
            label = "-a",
            side = LEFT,
            color = YELLOW,
            animated = False
        )
        self.add_T_label(
            x_max_1,
            label = "a",
            side = RIGHT,
            color = YELLOW,
            animated = False
        )
        # don't show the labels just yet
        self.remove(
            self.left_T_label_group[0],
            self.right_T_label_group[0],
        )

        def integral_update_func(t):
            return scipy.special.erf(
                self.point_to_coords(self.right_v_line.get_center())[0]
            )

        def integral_update_func_percent(t):
            return 100 * integral_update_func(t)
            
        equals_sign = TexMobject("=").next_to(cdf_formula, buff = MED_LARGE_BUFF)

        cdf_value = DecimalNumber(0, color = graph.color, num_decimal_points = 3)
        cdf_value.next_to(equals_sign)
        self.play(
            FadeIn(equals_sign),
            FadeIn(cdf_value)
        )
        self.add_foreground_mobject(cdf_value)

        cdf_percentage = DecimalNumber(0, unit = "\%")
        cdf_percentage.move_to(self.coords_to_point(0,0.2))
        self.add_foreground_mobject(cdf_percentage)

        self.add(ContinualChangingDecimal(
            decimal_number_mobject = cdf_value,
            number_update_func = integral_update_func,
            num_decimal_points = 3
        ))

        self.add(ContinualChangingDecimal(
            decimal_number_mobject = cdf_percentage,
            number_update_func = integral_update_func_percent,
            num_decimal_points = 1
        ))


        anim = self.get_animation_integral_bounds_change(
            graph, x_min_2, x_max_2,
            run_time = 3)


        self.play(
            anim
        )

        rect = SurroundingRectangle(formulas, buff = 0.5 * MED_LARGE_BUFF)
        self.play(ShowCreation(rect))




class IllustrateAreaModel3(Scene):

    def construct(self):

        formula = TexMobject("E[X] = \sum_{i=1}^N p_i x_i").move_to(3 * LEFT + UP)
        self.play(Write(formula))


        x_scale = 5.0
        y_scale = 1.0

        probabilities = np.array([1./8, 3./8, 3./8, 1./8])
        prob_strings = ["{1\over 8}","{3\over 8}","{3\over 8}","{1\over 8}"]
        cumulative_probabilities = np.cumsum(probabilities)
        cumulative_probabilities = np.insert(cumulative_probabilities, 0, 0)
        y_values = np.array([0, 1, 2, 3])

        hist = Histogram(probabilities, y_values,
            mode = "widths",
            x_scale = x_scale,
            y_scale = y_scale,
            x_labels = "none"
        )

        flat_hist = Histogram(probabilities, 0 * y_values,
            mode = "widths",
            x_scale = x_scale,
            y_scale = y_scale,
            x_labels = "none"
        )

        self.play(FadeIn(flat_hist))
        self.play(
            ReplacementTransform(flat_hist, hist)
        )

        braces = VGroup()
        p_labels = VGroup()
        # add x labels (braces)
        for (p,string,bar) in zip(probabilities, prob_strings,hist.bars):
            brace = Brace(bar, DOWN, buff = 0.1)
            p_label = TexMobject(string).next_to(brace, DOWN, buff = SMALL_BUFF).scale(0.7)
            group = VGroup(brace, p_label)
            braces.add(brace)
            p_labels.add(p_label)
            
        self.play(
            LaggedStart(FadeIn,braces),
            LaggedStart(FadeIn, p_labels)
        )



        y_average = np.mean(y_values)
        averaged_y_values = y_average * np.ones(np.shape(y_values))

        averaged_hist = flat_hist = Histogram(probabilities, averaged_y_values,
            mode = "widths",
            x_scale = x_scale,
            y_scale = y_scale,
            x_labels = "none",
            y_labels = "none"
        ).fade(0.2)

        ghost_hist = hist.copy().fade(0.8)
        self.bring_to_back(ghost_hist)

        self.play(Transform(hist, averaged_hist, run_time = 3))
        self.wait()

        average_brace = Brace(averaged_hist, RIGHT, buff = 0.1)
        average_label = TexMobject(str(y_average)).scale(0.7)
        average_label.next_to(average_brace, RIGHT, SMALL_BUFF)
        average_group = VGroup(average_brace, average_label)

        one_brace = Brace(averaged_hist, DOWN, buff = 0.1)
        one_p_label = TexMobject(str(1)).next_to(one_brace, DOWN, buff = SMALL_BUFF).scale(0.7)
        one_group = VGroup(one_brace, one_p_label)

        self.play(
            FadeIn(average_group),
            Transform(braces, one_brace),
            Transform(p_labels, one_p_label),
        )
        
        rect = SurroundingRectangle(formula, buff = 0.5 * MED_LARGE_BUFF)
        self.play(ShowCreation(rect))










class DieFace(SVGMobject):
    
    def __init__(self, value, **kwargs):

        self.value = value
        self.file_name = "Dice-" + str(value)
        self.ensure_valid_file()
        SVGMobject.__init__(self, file_name = self.file_name)
        
class RowOfDice(VGroup):
    CONFIG = {
        "values" : range(1,7),
        "direction": RIGHT,
    }

    def generate_points(self):
        for value in self.values:
            new_die = DieFace(value)
            new_die.submobjects[0].set_fill(opacity = 0)
            new_die.submobjects[0].set_stroke(width = 7)
            new_die.next_to(self, self.direction)
            self.add(new_die)
        self.move_to(ORIGIN)



class ShowUncertainty1(Scene):

    def throw_a_die(self, run_time = 0.3):

        eye = np.random.randint(1,7)
        face = self.row_of_dice.submobjects[eye - 1]

        self.play(
            ApplyMethod(face.submobjects[0].set_fill, {"opacity": 1},
                rate_func = there_and_back,
                run_time = run_time,
            ),
        )

    def construct(self):

        self.row_of_dice = RowOfDice(direction = DOWN).scale(0.5)
        self.add(self.row_of_dice)

        for i in range(5):
            self.throw_a_die()
            self.wait(1)

        for i in range(10):
            self.throw_a_die()
            self.wait(0.3)

        for i in range(100):
            self.throw_a_die(0.05)
            self.wait(0.0)



class IdealizedDieHistogram(Scene):

    def construct(self):

        self.probs = 1.0/6 * np.ones(6)
        x_scale = 1.3

        y_labels = ["${1\over 6}$"] * 6

        hist = Histogram(np.ones(6), self.probs, 
            mode = "widths", 
            x_labels = "none",
            y_labels = y_labels,
            y_label_position = "center",
            y_scale = 20,
            x_scale = x_scale,
        )
        hist.rotate(-TAU/4)

        for label in hist.y_labels_group:
            label.rotate(TAU/4)
        hist.remove(hist.y_labels_group)


        self.play(FadeIn(hist))
        self.play(LaggedStart(FadeIn, hist.y_labels_group))



class ShowUncertainty2(Scene):


    def throw_darts(self, n, run_time = 1):

        points = np.random.normal(
            loc = self.dartboard.get_center(),
            scale = 0.6 * np.ones(3),
            size = (n,3)
        )
        points[:,2] = 0
        dots = VGroup()
        for point in points:
            dot = Dot(point, radius = 0.04, fill_opacity = 0.7)
            dots.add(dot)
            self.add(dot)

        self.play(
            LaggedStart(FadeIn, dots, lag_ratio = 0.01, run_time = run_time)
        )


    def construct(self):

        self.dartboard = ImageMobject("dartboard").scale(2)
        dartboard_circle = Circle(
            radius = self.dartboard.get_width() / 2,
            fill_color = BLACK,
            fill_opacity = 0.5,
            stroke_color = WHITE,
            stroke_width = 5
        )
        self.dartboard.add(dartboard_circle)

        self.add(self.dartboard)
    
        self.throw_darts(5,5)
        self.throw_darts(20,5)
        self.throw_darts(100,5)
        self.throw_darts(1000,5)


SICKLY_GREEN = "#9BBD37"


class SicklyPiCreature(PiCreature):
    CONFIG = {
        "sick_color": SICKLY_GREEN
    }

    def get_slightly_sick(self):

        self.save_state()
        self.set_color(self.sick_color)

    def get_sick(self):

        self.get_slightly_sick()
        self.change_mode("sick")

    def get_better(self):
        self.restore()


class RandyIsSickOrNot(Scene):


    def construct(self):
        title = TextMobject("1 in 200")
        title.to_edge(UP)

        
        randy = SicklyPiCreature()
        randy.scale_to_fit_height(3)
        randy.move_to(2*LEFT)
        randy.change_mode("plain")
        randy.set_color(BLUE)
        randy.save_state()

        self.add(randy)

        p_sick = TexMobject("p(","\\text{sick}",") = 0.5\%").scale(1.7)
        p_sick.set_color_by_tex("sick", SICKLY_GREEN)
        p_sick.next_to(randy, UP, buff = LARGE_BUFF)
        self.add(p_sick)
        self.wait()
        
        self.play(
            ApplyMethod(randy.get_slightly_sick, rate_func = there_and_back)
        )
        self.play(Blink(randy))
        self.wait(2)

        self.play(
            ApplyMethod(randy.get_sick)
        )

        self.play(Blink(randy))
        self.wait()

        self.play(randy.get_better)

        self.play(
            ApplyMethod(randy.get_slightly_sick, rate_func = there_and_back)
        )
        self.play(Blink(randy))
        self.wait(0.5)

        self.play(
            ApplyMethod(randy.get_sick)
        )
        
        self.play(Blink(randy))
        self.play(randy.get_better)
        self.wait(3)



class OneIn200HasDisease(Scene):
    def construct(self):
        title = TextMobject("1 in 200")
        title.to_edge(UP)
        creature = PiCreature()

        all_creatures = VGroup(*[
            VGroup(*[
                creature.copy()
                for y in range(20)
            ]).arrange_submobjects(DOWN, SMALL_BUFF)
            for x in range(10)
        ]).arrange_submobjects(RIGHT, SMALL_BUFF)
        all_creatures.scale_to_fit_height(FRAME_HEIGHT * 0.8)
        all_creatures.next_to(title, DOWN)
        randy = all_creatures[0][0]
        all_creatures[0].remove(randy)
        randy.change_mode("sick")
        randy.set_color(SICKLY_GREEN)
        randy.save_state()
        randy.scale_to_fit_height(3)
        randy.center()
        randy.change_mode("plain")
        randy.set_color(BLUE)

        self.add(randy)

        #p_sick = TexMobject("p(","\\text{sick}",") = 0.5\%")
        #p_sick.set_color_by_tex("sick", SICKLY_GREEN)
        #p_sick.next_to(randy, RIGHT+UP)
        #self.add(p_sick)
        self.wait()
        
        self.play(
            randy.change_mode, "sick",
            randy.set_color, SICKLY_GREEN
        )
        self.play(Blink(randy))
        self.play(randy.restore)
        self.wait()
        self.play(
            Write(title),
            LaggedStart(FadeIn, all_creatures, run_time = 3)
        )
        self.wait()


class RandyFlipsAndStacks(Scene):

    def construct(self):

        randy = CoinFlippingPiCreature(color = MAROON_E)
        randy.scale(0.5).to_edge(LEFT + DOWN)

        heads = tails = 0
        tally = TallyStack(heads, tails, anchor = ORIGIN)

        nb_flips = 10

        flips = np.random.randint(2, size = nb_flips)

        for i in range(nb_flips):

            self.play(FlipCoin(randy))
            self.wait(0.5)

            flip = flips[i]
            if flip == 0:
                heads += 1
            elif flip == 1:
                tails += 1
            else:
                raise Exception("That side does not exist on this coin")

            new_tally = TallyStack(heads, tails, anchor = ORIGIN)

            if tally.nb_heads == 0 and new_tally.nb_heads == 1:
                self.play(FadeIn(new_tally.heads_stack))
            elif tally.nb_tails == 0 and new_tally.nb_tails == 1:
                self.play(FadeIn(new_tally.tails_stack))
            else:
                self.play(Transform(tally, new_tally))

            tally = new_tally



class TwoDiceTable(Scene):

    def construct(self):

        table = VGroup()
        cell_size = 1
        colors = color_gradient([RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE], 13)

        for i in range(1,7):
            for j in range(1,7):
                cell = Square(side_length = cell_size)
                cell.set_fill(color = colors[i+j], opacity = 0.8)
                label = Integer(i+j)
                label.move_to(cell)
                cell.add(label)
                cell.move_to(i*cell_size*RIGHT + j*cell_size*DOWN)
                table.add(cell)

        table.center()
        self.add(table)

        row1 = RowOfDice().match_width(table)
        print row1.is_subpath
        row2 = row1.copy().rotate(-TAU/4)
        print row2.is_subpath
        row1.next_to(table, UP)
        row2.next_to(table, LEFT)
        table.add(row1, row2)
        table.center()



class VisualCovariance(Scene):


    def construct(self):

        size = 4
        square = Square(side_length = size)
        n_points = 30
        cloud = VGroup(*[
            Dot((x + 0.8*y) * RIGHT + y * UP).set_fill(WHITE, 1)
            for x, y in zip(
                np.random.normal(0, 1, n_points),
                np.random.normal(0, 1, n_points)
            )
        ])
        self.add_foreground_mobject(cloud)

        x_axis = Vector(8*RIGHT, color = WHITE).move_to(2.5*DOWN)
        y_axis = Vector(5*UP, color = WHITE).move_to(4*LEFT)

        self.add(x_axis, y_axis)


        random_pairs = [ (p1, p2) for (p1, p2) in
            it.combinations(cloud, 2)
        ]
        np.random.shuffle(random_pairs)



        for (p1, p2) in random_pairs:
            c1, c2 = p1.get_center(), p2.get_center()
            x1, y1, x2, y2 = c1[0], c1[1], c2[0], c2[1]
            if x1 >= x2:
                continue
            if y2 > y1:
                # make a red rect
                color = RED
                opacity = 0.1
               
            elif y2 < y1:
                # make a blue rect
                color = BLUE
                opacity = 0.2

            rect = Rectangle(width = x2 - x1, height = abs(y2 - y1))
            rect.set_fill(color = color, opacity = opacity)
            rect.set_stroke(width = 0)
            rect.move_to((c1+c2)/2)

            self.play(FadeIn(rect), run_time = 0.05)



class BinaryOption(VMobject):

    def __init__(self, mob1, mob2, **kwargs):

        VMobject.__init__(self, **kwargs)
        text = TextMobject("or").scale(0.5)
        mob1.next_to(text, LEFT)
        mob2.next_to(text, RIGHT)
        self.add(mob1, text, mob2)



class BinaryChoices(Scene):

    def construct(self):

        example1 = BinaryOption(UprightHeads(), UprightTails())
        example2 = BinaryOption(Male(), Female())
        example3 = BinaryOption(Checkmark(), Xmark())

        example2.next_to(example1, DOWN, buff = MED_LARGE_BUFF)
        example3.next_to(example2, DOWN, buff = MED_LARGE_BUFF)

        all = VGroup(example1, example2, example3)
        all = all.scale(2)

        self.play(
            LaggedStart(FadeIn, all)
        )


class BrickRow(VMobject):

    CONFIG = {
        "left_color" : YELLOW,
        "right_color" : BLUE,
        "height" : 1.0,
        "width" : 8.0,
        "outcome_shrinkage_factor_x" : 1.0,
        "outcome_shrinkage_factor_y" : 1.0
    }

    def __init__(self, n, **kwargs):
        self.subdiv_level = n
        self.coloring_level = n
        VMobject.__init__(self, **kwargs)


    def generate_points(self):

        self.submobjects = []
        self.rects = self.get_rects_for_level(self.coloring_level)
        self.add(self.rects)
        self.subdivs = self.get_subdivs_for_level(self.subdiv_level)
        self.add(self.subdivs)

        self.border = SurroundingRectangle(self,
            buff = 0, color = WHITE)
        self.add(self.border)



    def get_rects_for_level(self,r):
        rects = VGroup()
        for k in range(r + 1):
            proportion = float(choose(r,k)) / 2**r
            new_rect = Rectangle(
                width = proportion * self.width, 
                height = self.height,
                fill_color = graded_color(r,k),
                fill_opacity = 1,
                stroke_width = 0
            )
            if len(rects.submobjects) > 0:
                new_rect.next_to(rects,RIGHT,buff = 0)
            else:
                new_rect.next_to(self.get_center() + 0.5 * self.width * LEFT, RIGHT, buff = 0)
            rects.add(new_rect)
        return rects


    def get_subdivs_for_level(self,r):
        subdivs = VGroup()
        x = - 0.5 * self.width
        for k in range(0, r):
            proportion = float(choose(r,k)) / 2**r
            x += proportion * self.width
            subdiv = Line(
                x * RIGHT + 0.5 * self.height * UP,
                x * RIGHT + 0.5 * self.height * DOWN,
            )
            subdivs.add(subdiv)
        subdivs.move_to(self.get_center())
        return subdivs


    def get_sequence_subdivs_for_level(self,r):
        subdivs = VGroup()
        x = - 0.5 * self.width
        dx = 1.0 / 2**r
        for k in range(1, 2 ** r):
            proportion = dx
            x += proportion * self.width
            subdiv = DashedLine(
                x * RIGHT + 0.5 * self.height * UP,
                x * RIGHT + 0.5 * self.height * DOWN,
            )
            subdivs.add(subdiv)
        subdivs.move_to(self.get_center())
        return subdivs


    def get_outcome_centers_for_level(self,r):
        
        dpos = float(self.width) / (2 ** r) * RIGHT
        pos = 0.5 * self.width * LEFT + 0.5 * dpos
        centers = []
        for k in range(0, 2 ** r):
            centers.append(self.get_center() + pos + k * dpos)

        return centers

    def get_outcome_rects_for_level(self,r, with_labels = False):

        centers = self.get_outcome_centers_for_level(r)
        outcome_width = self.outcome_shrinkage_factor_x * float(self.width) / (2 ** r)
        outcome_height = self.outcome_shrinkage_factor_y * self.height
        corner_radius = 0 # min(0.1, 0.3 * min(outcome_width, outcome_height))
        # this scales down the corner radius for very narrow rects
        rect = Rectangle( # RoundedRectangle(
            width = outcome_width,
            height = outcome_height,
            #corner_radius = corner_radius,
            fill_color = WHITE,
            fill_opacity = 0.2,
            stroke_width = 0
        )
        rects = VGroup()
        for center in centers:
            rects.add(rect.copy().move_to(center))

        rects.move_to(self.get_center())


        if with_labels == False:
            return rects

        # else
        sequences = self.get_coin_sequences_for_level(r)
        labels = VGroup()
        for (seq, rect) in zip(sequences, rects):
            coin_seq = CoinSequence(seq, direction = DOWN)
            coin_seq.shift(rect.get_center() - coin_seq.get_center())
            # not simply move_to bc coin_seq is not centered
            rect.add(coin_seq)
            rect.label = coin_seq

        return rects

    def get_coin_sequences_for_level(self,r):
        # array of arrays of characters
        if r < 0 or int(r) != r:
            raise Exception("Level must be a positive integer")
        if r == 0:
            return []
        if r == 1:
            return [["H"], ["T"]]

        previous_seq_array = self.get_coin_sequences_for_level(r - 1)
        subdiv_lengths = [choose(r - 1, k) for k in range(r)]

        seq_array = []
        index = 0
        for length in subdiv_lengths:
            
            for seq in previous_seq_array[index:index + length]:
                seq_copy = copy.copy(seq)
                seq_copy.append("H")
                seq_array.append(seq_copy)

            for seq in previous_seq_array[index:index + length]:
                seq_copy = copy.copy(seq)
                seq_copy.append("T")
                seq_array.append(seq_copy)
            index += length

        return seq_array


    def get_outcome_width_for_level(self,r):
        return self.width / (2**r)

    def get_rect_widths_for_level(self, r):
        ret_arr = []
        for k in range(0, r):
            proportion = float(choose(r,k)) / 2**r
            ret_arr.append(proportion * self.width)
        return ret_arr





class SplitRectsInBrickWall(AnimationGroup):

    def __init__(self, mobject, **kwargs):

        r = self.subdiv_level = mobject.subdiv_level + 1
        
        subdivs = VGroup()
        x = -0.5 * mobject.get_width()

        anims = []
        for k in range(0, r):
            proportion = float(choose(r,k)) / 2**r
            x += proportion * mobject.get_width()
            subdiv = DashedLine(
                mobject.get_top() + x * RIGHT,
                mobject.get_bottom() + x * RIGHT,
            )
            subdivs.add(subdiv)
            anims.append(ShowCreation(subdiv))

        mobject.add(subdivs)
        AnimationGroup.__init__(self, *anims, **kwargs)





    # def update_mobject(self, alpha):
    #     for subdiv in self.subdivs:
    #         x = subdiv.get_start()[0]
    #         start = self.mobject.get_center()
    #         start += x * RIGHT + 0.5 * self.mobject.get_height() * UP
    #         end = start + alpha * self.mobject.get_height() * DOWN
    #         subdiv.put_start_and_end_on(start,end)



class JustFlipping(Scene):

    def construct(self):

        randy = CoinFlippingPiCreature().shift(2 * DOWN)
        self.add(randy)

        self.wait(2)

        for i in range(10):
            self.wait()
            self.play(FlipCoin(randy))



class JustFlippingWithResults(Scene):

    def construct(self):

        randy = CoinFlippingPiCreature().shift(2 * DOWN)
        self.add(randy)

        self.wait(2)

        for i in range(10):
            self.wait()
            self.play(FlipCoin(randy))
            result = random.choice(["H", "T"])
            if result == "H":
                coin = UprightHeads().scale(3)
            else:
                coin = UprightTails().scale(3)
            coin.move_to(2 * UP + 2.5 * LEFT + i * 0.6 * RIGHT)
            self.play(FadeIn(coin))



class WhatDoesItReallyMean(TeacherStudentsScene):

    CONFIG = {
        "default_pi_creature_kwargs": {
            "color": MAROON_E,
            "flip_at_start": True,
        },
    }

    def construct(self):

        student_q = TextMobject("What does", "``probability''", "\emph{actually}", "mean?")
        student_q.set_color_by_tex("probability", YELLOW)
        self.student_says(student_q, target_mode = "sassy")
        self.wait()
        self.teacher_says("Don't worry -- philosophy can come later!")
        self.wait()


class DecimalTally(TextMobject):

    def __init__(self, heads, tails, **kwargs):

        TextMobject.__init__(self, str(heads), "\\textemdash\,", str(tails), **kwargs)
        self[0].set_color(COLOR_HEADS)
        self[-1].set_color(COLOR_TAILS)
        # this only works for single-digit tallies



class BrickRowScene(PiCreatureScene):


    def split_tallies(self, direction = DOWN):
        # Split all tally symbols at once and move the copies
        # either horizontally on top of the brick row
        # or diagonally into the bricks

        self.tallies_copy = self.tallies.copy()
        self.add_foreground_mobject(self.tallies_copy)

        tally_targets_left = [
            rect.get_center() + 0.25 * rect.get_width() * LEFT 
            for rect in self.row.rects
        ]

        tally_targets_right = [
            rect.get_center() + 0.25 * rect.get_width() * RIGHT 
            for rect in self.row.rects
        ]

        if np.all(direction == LEFT) or np.all(direction == RIGHT):

            tally_y_pos = self.tallies[0].anchor[1]
            for target in tally_targets_left:
                target[1] = tally_y_pos
            for target in tally_targets_right:
                target[1] = tally_y_pos

        for (i, tally) in enumerate(self.tallies):

            target_left = tally_targets_left[i]
            new_tally_left = TallyStack(tally.nb_heads + 1, tally.nb_tails)
            new_tally_left.move_anchor_to(target_left)
            v = target_left - tally.anchor
            
            self.play(
                tally.move_anchor_to, target_left,
            )
            tally.anchor = target_left
            self.play(Transform(tally, new_tally_left))
            
            tally_copy = self.tallies_copy[i]

            target_right = tally_targets_right[i]
            new_tally_right = TallyStack(tally.nb_heads, tally.nb_tails + 1)
            new_tally_right.move_anchor_to(target_right)
            v = target_right - tally_copy.anchor
            
            self.play(tally_copy.move_anchor_to, target_right)
            tally_copy.anchor = target_right
            self.play(Transform(tally_copy, new_tally_right))

            tally_copy.nb_heads = new_tally_right.nb_heads
            tally_copy.nb_tails = new_tally_right.nb_tails
            tally.nb_heads = new_tally_left.nb_heads
            tally.nb_tails = new_tally_left.nb_tails




    def tally_split_animations(self, direction = DOWN):
        # Just creates the animations and returns them
        # Execution can be timed afterwards
        # Returns two lists: first all those going left, then those to the right

        self.tallies_copy = self.tallies.copy()
        self.add_foreground_mobject(self.tallies_copy)

        tally_targets_left = [
            rect.get_center() + 0.25 * rect.get_width() * LEFT 
            for rect in self.row.rects
        ]

        tally_targets_right = [
            rect.get_center() + 0.25 * rect.get_width() * RIGHT 
            for rect in self.row.rects
        ]

        if np.all(direction == LEFT) or np.all(direction == RIGHT):

            tally_y_pos = self.tallies[0].anchor[1]
            for target in tally_targets_left:
                target[1] = tally_y_pos
            for target in tally_targets_right:
                target[1] = tally_y_pos


        anims1 = []

        for (i, tally) in enumerate(self.tallies):

            target_left = tally_targets_left[i]
            v = target_left - tally.anchor
            
            anims1.append(tally.move_anchor_to)
            anims1.append(target_left)
            
            tally.anchor = target_left
            
            tally_copy = self.tallies_copy[i]

            target_right = tally_targets_right[i]
            v = target_right - tally_copy.anchor
            
            anims1.append(tally_copy.move_anchor_to)
            anims1.append(target_right)
            
            tally_copy.anchor = target_right

        anims2 = []

        for (i, tally) in enumerate(self.tallies):

            new_tally_left = TallyStack(tally.nb_heads + 1, tally.nb_tails)
            new_tally_left.move_anchor_to(tally.anchor)
            anims2.append(Transform(tally, new_tally_left))
            
            tally_copy = self.tallies_copy[i]

            new_tally_right = TallyStack(tally.nb_heads, tally.nb_tails + 1)
            new_tally_right.move_anchor_to(tally_copy.anchor)
            anims2.append(Transform(tally_copy, new_tally_right))

            tally_copy.nb_heads = new_tally_right.nb_heads
            tally_copy.nb_tails = new_tally_right.nb_tails
            tally.nb_heads = new_tally_left.nb_heads
            tally.nb_tails = new_tally_left.nb_tails

        return anims1, anims2


    def split_tallies_at_once(self, direction = DOWN):
        anims1, anims2 = self.tally_split_animations(direction = direction)
        self.play(*(anims1 + anims2))

    def split_tallies_in_two_steps(self, direction = DOWN):
        # First all thiode to the left, then those to the right
        anims1, anims2 = self.tally_split_animations(direction = direction)
        self.play(*anims1)
        self.wait(0.3)
        self.play(*anims2)




    def merge_rects_by_subdiv(self):

        half_merged_row = self.row.copy()
        half_merged_row.subdiv_level += 1
        half_merged_row.generate_points()
        half_merged_row.move_to(self.row)
        self.play(FadeIn(half_merged_row))
        self.row = half_merged_row

    def merge_tallies(self, direction = UP):

        r = self.row.subdiv_level
        tally_targets = [
            rect.get_center()
            for rect in self.row.get_rects_for_level(r)
        ]

        if np.all(direction == LEFT) or np.all(direction == RIGHT):
            y_pos = self.row.get_center()[1] + 1.2 * 0.5 * self.row.get_height()
            for target in tally_targets:
                target[1] = y_pos

        anims = []
        for (tally, target) in zip(self.tallies[1:], tally_targets[1:-1]):
            anims.append(tally.move_anchor_to)
            anims.append(target)

        for (tally, target) in zip(self.tallies_copy[:-1], tally_targets[1:-1]):
            anims.append(tally.move_anchor_to)
            anims.append(target)

        self.play(*anims)
        # update anchors
        for (tally, target) in zip(self.tallies[1:], tally_targets[1:-1]):
            tally.anchor = target
        for (tally, target) in zip(self.tallies_copy[:-1], tally_targets[1:-1]):
            tally.anchor = target

        self.remove(self.tallies_copy)
        self.tallies.add(self.tallies_copy[-1])


    def merge_rects_by_coloring(self):

        merged_row = self.row.copy()
        merged_row.coloring_level += 1
        merged_row.generate_points()
        merged_row.move_to(self.row)

        self.play(FadeIn(merged_row))
        self.row = merged_row



    def move_tallies_on_top(self):
        self.play(
            self.tallies.shift, 1.2 * 0.5 * self.row.height * UP
        )
        for tally in self.tallies:
            tally.anchor += 1.2 * 0.5 * self.row.height * UP

    def create_pi_creature(self):
        randy = CoinFlippingPiCreature(color = MAROON_E)
        return randy

    def construct(self):

        randy = self.get_primary_pi_creature()
        randy = randy.scale(0.5).move_to(3*DOWN + 6*LEFT)
        #self.add(randy)
        self.row = BrickRow(0, height = 2, width = 10)
        self.wait()

        self.play(FadeIn(self.row))

        self.wait()


        # move in all kinds of sequences
        coin_seqs = VGroup()
        for i in range(20):
            n = np.random.randint(1,10)
            seq = [np.random.choice(["H", "T"]) for j in range(n)]
            coin_seq = CoinSequence(seq).scale(1.5)
            loc = np.random.uniform(low = -10, high = 10) * RIGHT
            loc += np.random.uniform(low = -6, high = 6) * UP
            coin_seq.move_to(loc)
            
            coin_seq.target = coin_seq.copy().scale(0.3).move_to(0.4 * loc)
            coin_seq.target.fade(1)
            coin_seqs.add(coin_seq)

        self.play(
            LaggedStart(
                Succession, coin_seqs, lambda m: (FadeIn(m, run_time = 0.1), MoveToTarget(m)),
                run_time = 5,
                lag_ratio = 0.5
            )
        )
        
        self.play(FlipCoin(randy) )

        self.play(SplitRectsInBrickWall(self.row))
        self.merge_rects_by_subdiv()
        self.merge_rects_by_coloring()
        #
        # put tallies on top

        single_flip_labels = VGroup(UprightHeads(), UprightTails())
        for (label, rect) in zip(single_flip_labels, self.row.rects):
            label.next_to(rect, UP)
            self.play(FadeIn(label))
            self.wait()

        self.wait()


        # # # # # # # #
        # SECOND FLIP #
        # # # # # # # #

        self.play(FlipCoin(randy))
        self.wait()

        self.play(
            SplitRectsInBrickWall(self.row)
        )
        self.wait()


        # split sequences
        single_flip_labels_copy = single_flip_labels.copy()
        self.add(single_flip_labels_copy)

        
        v = self.row.get_outcome_centers_for_level(2)[0] - single_flip_labels[0].get_center()
        self.play(
            single_flip_labels.shift, v
        )
        new_heads = VGroup(UprightHeads(), UprightHeads())
        for i in range(2):
            new_heads[i].move_to(single_flip_labels[i])
            new_heads[i].shift(COIN_SEQUENCE_SPACING * DOWN)
        self.play(FadeIn(new_heads))

        v = self.row.get_outcome_centers_for_level(2)[-1] - single_flip_labels_copy[-1].get_center()
        self.play(
            single_flip_labels_copy.shift, v
        )
        new_tails = VGroup(UprightTails(), UprightTails())
        for i in range(2):
            new_tails[i].move_to(single_flip_labels_copy[i])
            new_tails[i].shift(COIN_SEQUENCE_SPACING * DOWN)
        self.play(FadeIn(new_tails))


        decimal_tallies = VGroup()
        # introduce notion of tallies
        for (i, rect) in enumerate(self.row.get_rects_for_level(2)):
            tally = DecimalTally(2-i, i)
            tally.next_to(rect, UP)
            decimal_tallies.add(tally)
            self.play(FadeIn(tally))
            self.wait()

        self.add_foreground_mobject(single_flip_labels)
        self.add_foreground_mobject(new_heads)
        self.add_foreground_mobject(single_flip_labels_copy)
        self.add_foreground_mobject(new_tails)

        # show individual outcomes
        outcomes = self.row.get_outcome_rects_for_level(2, with_labels = False)


        self.play(
            LaggedStart(FadeIn, outcomes)
        )
        self.wait()
        self.play(
            LaggedStart(FadeOut, outcomes),
        )
        self.wait()
        self.play(
            FadeOut(single_flip_labels),
            FadeOut(new_heads),
            FadeOut(single_flip_labels_copy),
            FadeOut(new_tails)
        )
        self.wait()

        self.tallies = VGroup()
        for (i, rect) in enumerate(self.row.get_rects_for_level(2)):
            tally = TallyStack(2-i, i, show_decimals = False)
            tally.move_to(rect)
            self.tallies.add(tally)


        self.play(FadeIn(self.tallies))
        self.wait()

        anims = []
        for (decimal_tally, tally_stack) in zip(decimal_tallies, self.tallies):
            anims.append(ApplyFunction(
                tally_stack.position_decimal_tally, decimal_tally
            ))
        
        self.play(*anims)
        self.wait()

        # replace the original decimal tallies with
        # the ones that belong to the TallyStacks
        for (decimal_tally, tally_stack) in zip(decimal_tallies, self.tallies):
            self.remove(decimal_tally)
            tally_stack.position_decimal_tally(tally_stack.decimal_tally)
            tally_stack.add(tally_stack.decimal_tally)
        
        self.add_foreground_mobject(self.tallies)
        self.merge_rects_by_subdiv()
        self.wait()
        self.merge_rects_by_coloring()
        self.wait()
        

        # # # # # # # # # # # # #
        # CALLBACK TO SEQUENCES #
        # # # # # # # # # # # # #

        outcomes = self.row.get_outcome_rects_for_level(2, with_labels = True)
        subdivs = self.row.get_sequence_subdivs_for_level(2)
        self.play(
            FadeIn(outcomes),
            FadeIn(subdivs),
            FadeOut(self.tallies)
        )

        self.wait()

        rect_to_dice = outcomes[1]
        N = 10
        dice_width = rect_to_dice.get_width()/N
        dice_height = rect_to_dice.get_height()/N
        prototype_dice = Rectangle(
            width = dice_width,
            height = dice_height,
            stroke_width = 2,
            stroke_color = WHITE,
            fill_color = WHITE,
            fill_opacity = 0
        )
        prototype_dice.align_to(rect_to_dice, direction = UP)
        prototype_dice.align_to(rect_to_dice, direction = LEFT)
        all_dice = VGroup()
        for i in range(N):
            for j in range(N):
                dice_copy = prototype_dice.copy()
                dice_copy.shift(j * dice_width * RIGHT + i * dice_height * DOWN)
                all_dice.add(dice_copy)

        self.play(
            LaggedStart(FadeIn, all_dice),
            FadeOut(rect_to_dice.label)
        )

        self.wait()

        table = Ellipse(width = 1.5, height = 1)
        table.set_fill(color = GREEN_E, opacity = 1)
        table.next_to(rect_to_dice, UP)
        self.add(table)
        coin1 = UprightHeads(radius = 0.1)
        coin2 = UprightTails(radius = 0.1)

        def get_random_point_in_ellipse(ellipse):
            width = ellipse.get_width()
            height = ellipse.get_height()
            x = y = 1
            while x**2 + y**2 > 0.9:
                x = np.random.uniform(-1,1)
                y = np.random.uniform(-1,1)            
            x *= width/2
            y *= height/2
            return ellipse.get_center() + x * RIGHT + y * UP


        for dice in all_dice:
            p1 = get_random_point_in_ellipse(table)
            p2 = get_random_point_in_ellipse(table)
            coin1.move_to(p1)
            coin2.move_to(p2)
            self.add(coin1, coin2)
            self.play(
                ApplyMethod(dice.set_fill, {"opacity" : 0.5},
                    rate_func = there_and_back,
                    run_time = 0.05)
            )


        self.wait()

        self.play(
            FadeOut(outcomes),
            FadeOut(subdivs),
            FadeOut(all_dice),
            FadeOut(table),
            FadeOut(coin1),
            FadeOut(coin2),
            FadeIn(self.tallies)
        )

        self.wait()

        # # # # # # # #
        # THIRD  FLIP #
        # # # # # # # #

        # move row up, leace a copy without tallies below
        new_row = self.row.copy()
        self.bring_to_back(new_row)
        self.play(
            self.row.shift,2.5 * UP,
            self.tallies.shift,2.5 * UP,
        )

        self.play(FlipCoin(randy))

        self.wait()
        return

        self.play(
            SplitRectsInBrickWall(self.row)
        )
        self.wait()

        self.split_tallies_in_two_steps()
        self.wait()
        self.merge_rects_by_subdiv()
        self.wait()
        self.merge_tallies()
        self.merge_rects_by_coloring()
        self.wait()
        self.move_tallies_on_top()



        # show individual outcomes
        outcomes = self.row.get_outcome_rects_for_level(3, with_labels = True)
        self.play(
            LaggedStart(FadeIn, outcomes)
        )
        self.wait()
        self.play(
            LaggedStart(FadeOut, outcomes)
        )


        # # # # # # # # # # # # # #
        # # FOURTH FLIP IN DETAIL #
        # # # # # # # # # # # # # #



        # removing the tallies (boy are they sticky)
        self.play(FadeOut(self.tallies))
        self.remove(self.tallies, self.tallies_copy)
        for tally in self.tallies:
            self.remove_foreground_mobject(tally)
            self.remove(tally)
        for tally in self.tallies_copy:
            self.remove_foreground_mobject(tally)
            self.remove(tally)

        # delete all the old crap hidden behind the row
        # before we can move it
        self.remove(*self.mobjects)
        self.add(randy) #,self.decimals,self.decimal_copies)


        previous_row = self.row.copy()
        self.add(previous_row)

        v = 1.25 * self.row.height * UP
        self.play(
            previous_row.shift, v,
            #self.decimals.shift, v,
            #self.decimal_copies.shift, v
        )

        self.add(self.row)
        self.bring_to_back(self.row)
        self.row.shift(v)

        w = 1.5 * self.row.height * DOWN
        self.play(
            self.row.shift, w,
            Animation(previous_row)
        )

        self.play(
            SplitRectsInBrickWall(self.row)
        )
        self.wait()

        self.merge_rects_by_subdiv()

        self.wait()

        n = 3 # level to split
        k = 1 # tally to split

        # show individual outcomes
        outcomes = previous_row.get_outcome_rects_for_level(n, with_labels = False)
        grouped_outcomes = VGroup()
        index = 0
        for i in range(n + 1):
            size = choose(n,i)
            grouped_outcomes.add(VGroup(outcomes[index:index + size]))
            index += size


        grouped_outcomes_copy = grouped_outcomes.copy()

        original_grouped_outcomes = grouped_outcomes.copy()
        # for later reference

        self.play(
            LaggedStart(FadeIn, grouped_outcomes),
            LaggedStart(FadeIn, grouped_outcomes_copy),
        )
        self.wait()

        # show how the outcomes in one tally split into two copies
        # going into the neighboring tallies

        #self.revert_to_original_skipping_status()

        target_outcomes = self.row.get_outcome_rects_for_level(n + 1, with_labels = False)
        grouped_target_outcomes = VGroup()
        index = 0
        old_tally_sizes = [choose(n,i) for i in range(n + 1)]
        new_tally_sizes = [choose(n + 1,i) for i in range(n + 2)]
        for i in range(n + 2):
            size = new_tally_sizes[i]
            grouped_target_outcomes.add(VGroup(target_outcomes[index:index + size]))
            index += size

        self.play(
            Transform(grouped_outcomes[k][0],grouped_target_outcomes[k][0][old_tally_sizes[k - 1]:])
        )

        self.play(
            Transform(grouped_outcomes_copy[k][0],grouped_target_outcomes[k + 1][0][:old_tally_sizes[k]])
        )

        old_tally_sizes.append(0) # makes the edge cases work properly

        # split the other tallies
        for i in range(k) + range(k + 1, n + 1):
            self.play(
                Transform(grouped_outcomes[i][0],
                    grouped_target_outcomes[i][0][old_tally_sizes[i - 1]:]
                ),
                Transform(grouped_outcomes_copy[i][0],
                    grouped_target_outcomes[i + 1][0][:old_tally_sizes[i]]
                )
            )

        
        self.wait()

        # remove outcomes and sizes except for one tally
        anims = []
        for i in range(n + 1):
            if i != k - 1:
                anims.append(FadeOut(grouped_outcomes_copy[i]))
            if i != k:
                anims.append(FadeOut(grouped_outcomes[i]))

        self.play(*anims)

        self.wait()

        self.play(
            Transform(grouped_outcomes_copy[k - 1], original_grouped_outcomes[k - 1])
        )
        self.play(
            Transform(grouped_outcomes[k], original_grouped_outcomes[k])
        )


        new_rects = self.row.get_rects_for_level(n + 1)

        #decimals_copy = self.decimals.copy()
        #decimals_copy2 = self.decimals.copy()

        self.play(
            Transform(grouped_outcomes[k][0],grouped_target_outcomes[k][0][old_tally_sizes[k - 1]:]),
            Transform(grouped_outcomes_copy[k - 1][0],grouped_target_outcomes[k][0][:old_tally_sizes[k]]),
            #decimals_copy[k - 1].move_to, new_rects[k],
            #decimals_copy2[k].move_to, new_rects[k],
        )


        # # # # # # # #
        # FIFTH  FLIP #
        # # # # # # # #

        # self.remove(
        #     grouped_outcomes,
        #     grouped_outcomes_copy,
        #     grouped_target_outcomes,
        #     target_outcomes,
        #     outcomes,
        #     previous_row,
        #     original_grouped_outcomes)
        self.clear()
        self.add(randy, self.row)
        #self.row.shift(0.5 * UP)        
        
        #return

        self.merge_rects_by_coloring()

        self.revert_to_original_skipping_status()

        for i in range(1):

            self.play(FlipCoin(randy))

            self.wait()

            self.play(
                SplitRectsInBrickWall(self.row)
            )
            self.wait()


            #self.split_tallies_at_once(direction = LEFT)
            self.wait()
            self.merge_rects_by_subdiv()
            self.wait()
            #self.merge_tallies(direction = LEFT)
            self.merge_rects_by_coloring()
            #self.merge_decimals()
            self.wait()

class LevelsOfDetailInBrickRow(BrickRowScene):

    def construct(self):

        self.force_skipping()

        randy = CoinFlippingPiCreature()
        randy = randy.scale(0.5).move_to(3*DOWN + 6*LEFT)
        self.add(randy)
        self.row = BrickRow(1, height = 2, width = 10)
        
        #self.decimals = VGroup()

        self.play(FlipCoin(randy),
            FadeIn(self.row))


        self.wait()
        
        # put tallies on top

        self.tallies = VGroup(*[
            TallyStack(1 - i, i) for i in range(2)
        ])
        for (tally, rect) in zip(self.tallies, self.row.rects):
            new_anchor = rect.get_center() + 1.2 * 0.5 * rect.get_height() * UP
            tally.move_anchor_to(new_anchor)
            self.play(FadeIn(tally))

        self.add_foreground_mobject(self.tallies)
        self.wait()


        # # # # # # # #
        # SECOND FLIP #
        # # # # # # # #



        self.play(FlipCoin(randy))
        self.wait()


        self.play(
            SplitRectsInBrickWall(self.row)
        )
        self.wait()

        # show individual outcomes
        outcomes = self.row.get_outcome_rects_for_level(2, with_labels = True)
        self.play(
            LaggedStart(FadeIn, outcomes)
        )
        self.wait()
        self.play(
            LaggedStart(FadeOut, outcomes)
        )

        self.split_tallies_in_two_steps()
        self.wait()
        self.merge_rects_by_subdiv()
        self.wait()
        self.merge_tallies()
        self.merge_rects_by_coloring()
        self.wait()
        self.move_tallies_on_top()
        




class OutlineableBars(VGroup):
    CONFIG = {
        "outline_stroke_width" : 5,
        "stroke_color" : WHITE
    }
    def create_outline(self, animated = False, **kwargs):

        outline_points = []

        for (i, bar) in enumerate(self.submobjects):
            
            if i == 0:
                # start with the lower left
                outline_points.append(bar.get_corner(DOWN + LEFT))

            # upper two points of each bar
            outline_points.append(bar.get_corner(UP + LEFT))
            outline_points.append(bar.get_corner(UP + RIGHT))

            previous_bar = bar
        # close the outline
            # lower right
        outline_points.append(previous_bar.get_corner(DOWN + RIGHT))
            # lower left
        outline_points.append(outline_points[0])

        self.outline = Polygon(*outline_points,
            stroke_width = self.outline_stroke_width,
            stroke_color = self.stroke_color)

        if animated:
            self.play(FadeIn(self.outline, **kwargs))
        return self.outline





class GenericMorphBrickRowIntoHistogram(Scene):

    CONFIG = {
        "level" : 3,
        "bar_width" : 2.0,
        "bar_anchor_height" : -3.0,
        "show_tallies" : False,
    }

    def construct(self):

        self.row = BrickRow(self.level, height = self.bar_width, width = 10)
        self.bars = OutlineableBars(*[self.row.rects[i] for i in range(self.level + 1)])
        self.bar_anchors = [self.bar_anchor_height * UP + self.row.height * (i - 0.5 * self.level) * RIGHT for i in range(self.level + 1)]

        self.add(self.row)

        if self.show_tallies:

            tallies = VMobject()

            for (i,brick) in enumerate(self.row.rects):
                tally = TallyStack(self.level - i, i)
                tally.next_to(brick, UP)
                self.add(tally)
                tallies.add(tally)
                brick.set_stroke(width = 3)

        self.remove(self.row.subdivs, self.row.border)

        anims = []
        for brick in self.row.rects:
            anims.append(brick.rotate)
            anims.append(TAU/4)
        
        if self.show_tallies:
            anims.append(FadeOut(tallies))
        self.play(*anims)

        
        anims = []
        for (i,brick) in enumerate(self.row.rects):
            anims.append(brick.next_to)
            anims.append(self.bar_anchors[i])
            anims.append({"direction" : UP, "buff" : 0})
        self.play(*anims)

        self.bars.create_outline()

        anims = []
        for bar in self.bars.submobjects:
            anims.append(bar.set_stroke)
            anims.append({"width" : 0})
        anims.append(FadeIn(self.bars.outline))
        self.play(*anims)







class MorphBrickRowIntoHistogram3(GenericMorphBrickRowIntoHistogram):
    
    CONFIG = {
        "level" : 3,
        "prob_denominator" : 8,
        "bar_width" : 2.0,
        "bar_anchor_height" : -3.0,
        "show_tallies" : True
    }

    def construct(self):

        super(MorphBrickRowIntoHistogram3,self).construct()
        

        # draw x-axis

        x_axis = Line(ORIGIN, 10 * RIGHT, color = WHITE, buff = 0)
        x_axis.next_to(self.bars, DOWN, buff = 0)
        #x_labels = VMobject(*[TexMobject(str(i)) for i in range(4)])
        x_labels = VMobject()

        for (i, bar) in enumerate(self.bars):
            label = Integer(i)
            label.next_to(self.bar_anchors[i], DOWN)
            x_labels.add(label)

        nb_tails_label = TextMobject("\# of tails")
        nb_tails_label.next_to(x_labels[-1], RIGHT, MED_LARGE_BUFF)
        
        self.play(
            FadeIn(x_axis),
            FadeIn(x_labels),
            FadeIn(nb_tails_label)
        )



        # draw y-guides

        y_guides = VMobject()
        for i in range(1,self.prob_denominator + 1):
            y_guide = Line(5 * LEFT, 5 * RIGHT, stroke_color = GRAY)
            y_guide.move_to(self.bar_anchor_height * UP + i * float(self.row.width) / self.prob_denominator * UP)
            y_guide_label = TexMobject("{" + str(i) + "\over " + str(self.prob_denominator) + "}", color = GRAY)
            y_guide_label.scale(0.7)
            y_guide_label.next_to(y_guide, LEFT)
            y_guide.add(y_guide_label)
            y_guides.add(y_guide)

        self.bring_to_back(y_guides)
        self.play(FadeIn(y_guides), Animation(self.bars))


        total_area_text = TextMobject("total area = 1", color = YELLOW)
        total_area_rect = SurroundingRectangle(total_area_text,
            buff = MED_SMALL_BUFF,
            fill_opacity = 0.5,
            fill_color = BLACK,
            stroke_color = YELLOW
        )

        self.play(
            Write(total_area_text),
            ShowCreation(total_area_rect)
        )

        prob_dist_text = TextMobject("probability distribution", color = YELLOW)
        prob_dist_text.to_corner(UP, buff = LARGE_BUFF)
        prob_dist_rect = SurroundingRectangle(prob_dist_text,
            buff = MED_SMALL_BUFF,
            stroke_color = YELLOW
        )

        self.play(
            Write(prob_dist_text),
            ShowCreation(prob_dist_rect)
        )



class MorphBrickRowIntoHistogram20(GenericMorphBrickRowIntoHistogram):
    CONFIG = {
        "level" : 20,
        "prob_ticks" : 0.05,
        "bar_width" : 0.5,
        "bar_anchor_height" : -3.0,
        "x_ticks": 5
    }

    def construct(self):

        super(MorphBrickRowIntoHistogram20, self).construct()

        x_axis = Line(ORIGIN, 10 * RIGHT, color = WHITE, buff = 0)
        x_axis.next_to(self.bars, DOWN, buff = 0)
        #x_labels = VMobject(*[TexMobject(str(i)) for i in range(4)])
        x_labels = VMobject()
        for (i, bar) in enumerate(self.bars):
            if i % self.x_ticks != 0:
                continue
            label = Integer(i)
            label.next_to(self.bar_anchors[i], DOWN)
            x_labels.add(label)

        nb_tails_label = TextMobject("\# of heads")
        nb_tails_label.next_to(x_labels[-1], RIGHT, MED_LARGE_BUFF)
        
        self.play(
            FadeIn(x_axis),
            FadeIn(x_labels),
            FadeIn(nb_tails_label)
        )

        # draw y-guides

        max_prob = float(choose(self.level, self.level/2)) / 2 ** self.level

        y_guides = VMobject()
        y_guide_heights = []
        prob_grid = np.arange(self.prob_ticks, 1.3 * max_prob, self.prob_ticks)
        for i in prob_grid:
            y_guide = Line(5 * LEFT, 5 * RIGHT, stroke_color = GRAY)
            y_guide_height = self.bar_anchor_height + i * float(self.row.width)
            y_guide_heights.append(y_guide_height)
            y_guide.move_to(y_guide_height * UP)
            y_guide_label = DecimalNumber(i, num_decimal_points = 2, color = GRAY)
            y_guide_label.scale(0.7)
            y_guide_label.next_to(y_guide, LEFT)
            y_guide.add(y_guide_label)
            y_guides.add(y_guide)

        self.bring_to_back(y_guides)
        self.play(FadeIn(y_guides), Animation(self.bars))

        histogram_width = self.bars.get_width()
        histogram_height = self.bars.get_height()

        # scale to fit screen
        self.scale_x = 10.0/(len(self.bars) * self.bar_width)
        self.scale_y = 6.0/histogram_height


        anims = []
        for (bar, x_label) in zip(self.bars, x_labels):
            v = (self.scale_x - 1) * x_label.get_center()[0] * RIGHT
            anims.append(x_label.shift)
            anims.append(v)


        anims.append(self.bars.stretch_about_point)
        anims.append(self.scale_x)
        anims.append(0)
        anims.append(ORIGIN)
        anims.append(self.bars.outline.stretch_about_point)
        anims.append(self.scale_x)
        anims.append(0)
        anims.append(ORIGIN)

        self.play(*anims)

        anims = []
        for (guide, i, h) in zip(y_guides, prob_grid, y_guide_heights):
            new_y_guide_height = self.bar_anchor_height + i * self.scale_y * float(self.row.width)
            v = (new_y_guide_height - h) * UP
            anims.append(guide.shift)
            anims.append(v)

        anims.append(self.bars.stretch_about_point)
        anims.append(self.scale_y)
        anims.append(1)
        anims.append(self.bars.get_bottom())
        anims.append(self.bars.outline.stretch_about_point)
        anims.append(self.scale_y)
        anims.append(1)
        anims.append(self.bars.get_bottom())

        self.play(*anims)

class MorphBrickRowIntoHistogram100(MorphBrickRowIntoHistogram20):
    CONFIG = {
        "level" : 100,
        "x_ticks": 20,
        "prob_ticks": 0.02
    }

class MorphBrickRowIntoHistogram500(MorphBrickRowIntoHistogram20):
    CONFIG = {
        "level" : 500,
        "x_ticks": 100,
        "prob_ticks": 0.01
    }

        


class EntireBrickWall(Scene):

    def construct(self):

        row_height = 0.3
        nb_rows = 20
        start_point = 3 * UP + 1 * LEFT
        
        rows = VMobject()
        rows.add(BrickRow(0, height = row_height))
        rows[0].move_to(start_point)
        self.add(rows)

        zero_counter = Integer(0).next_to(start_point + 0.5 * rows[0].width * RIGHT)
        nb_flips_text = TextMobject("\# of flips")
        nb_flips_text.next_to(zero_counter, RIGHT, buff = LARGE_BUFF)
        self.add(zero_counter, nb_flips_text)

        for i in range(1,nb_rows + 1):
            rows.add(BrickRow(i, height = row_height))
            rows[-1].move_to(start_point + (i - 1) * row_height * DOWN)
            self.bring_to_back(rows[-1])
            anims = [
                rows[-1].shift, row_height * DOWN,
                Animation(rows[-2])
            ]
            
            if i % 5 == 0:
                counter = Integer(i)
                counter.next_to(rows[-1].get_right() + row_height * DOWN, RIGHT)
                anims.append(FadeIn(counter))

            self.play(*anims)

        # draw indices under the last row for the number of tails
        tails_counters = VGroup()
        for (i, rect) in enumerate(rows[-1].rects):
            if i < 6 or i > 14:
                continue
            if i == 6:
                counter = TexMobject("\dots", color = COLOR_TAILS)
                counter.next_to(rect, DOWN, buff = 1.5 * MED_SMALL_BUFF)
            elif i == 14:
                counter = TexMobject("\dots", color = COLOR_TAILS)
                counter.next_to(rect, DOWN, buff = 1.5 * MED_SMALL_BUFF)
                counter.shift(0.2 * RIGHT)
            else:
                counter = Integer(i, color = COLOR_TAILS)
                counter.next_to(rect, DOWN)
            tails_counters.add(counter)

        nb_tails_text = TextMobject("\# of tails", color = COLOR_TAILS)
        nb_tails_text.next_to(tails_counters[-1], RIGHT, buff = LARGE_BUFF)

        self.play(
            LaggedStart(FadeIn, tails_counters),
            FadeIn(nb_tails_text)
        )

        special_brick_copy = rows[-1].rects[13].copy()
        self.play(
            rows.fade, 0.9,
            FadeIn(special_brick_copy)
        )






class QuizResult(Scene):

    def construct(self):

        highlight_color = YELLOW

        nb_students_x = 5
        nb_students_y = 3
        spacing_students_x = 2.0
        spacing_students_y = 2.2

        all_students = VGroup()
        student_points = []
        grades = []
        grades_count = []
        hist_y_values = np.zeros(4)
        for i in range(nb_students_x):
            for j in range(nb_students_y):
                x = i * spacing_students_x
                y = j * spacing_students_y
                pi = PiCreature().scale(0.3)
                pi.move_to([x,y,0])
                all_students.add(pi)
                q1 = np.random.choice([True, False])
                q2 = np.random.choice([True, False])
                q3 = np.random.choice([True, False])
                student_points.append([q1, q2, q3])
                grade = q1*1+q2*1+q3*1
                grades.append(grade)
                hist_y_values[grade] += 1
                # How many times has this grade already occured?
                grade_count = grades.count(grade)
                grades_count.append(grade_count)


        all_students.move_to(ORIGIN)
        self.add(all_students)

        all_quizzes = VGroup()

        quiz = get_example_quiz().scale(0.2)
        for pi in all_students:
            quiz_copy = quiz.copy()
            quiz_copy.next_to(pi, UP)
            all_quizzes.add(quiz_copy)

        master_quiz = get_example_quiz()
        self.play(ShowCreation(master_quiz))
        self.play(Transform(master_quiz, all_quizzes[0]))

        self.play(LaggedStart(FadeIn,all_quizzes))

        grades_mob = VGroup()
        for (pi, quiz, grade) in zip(all_students, all_quizzes, grades):
            grade_mob = TexMobject(str(grade) + "/3")
            grade_mob.move_to(quiz)
            grades_mob.add(grade_mob)

        self.remove(master_quiz)
        self.play(
            FadeOut(all_quizzes),
            FadeIn(grades_mob)
        )

        # self.play(
        #     all_students[2:].fade, 0.8,
        #     grades_mob[2:].fade, 0.8
        # )

        students_points_mob = VGroup()
        for (pi, quiz, points) in zip(all_students, all_quizzes, student_points):
            slot = get_slot_group(points, include_qs = False)
            slot.scale(0.5).move_to(quiz)
            students_points_mob.add(slot)

        self.play(
            #all_students.fade, 0,
            FadeOut(grades_mob),
            FadeIn(students_points_mob)
        )



        anims = []
        anchor_point = 3 * DOWN + 1 * LEFT
        for (pi, grade, grades_count) in zip(all_students, grades, grades_count):
            anims.append(pi.move_to)
            anims.append(anchor_point + grade * RIGHT + grades_count * UP)
        anims.append(FadeOut(students_points_mob))

        self.play(*anims)

        grade_labels = VGroup()
        for i in range(4):
            grade_label = Integer(i, color = highlight_color)
            grade_label.move_to(i * RIGHT)
            grade_labels.add(grade_label)
        grade_labels.next_to(all_students, DOWN)
        out_of_label = TextMobject("out of 3", color = highlight_color)
        out_of_label.next_to(grade_labels, RIGHT, buff = MED_LARGE_BUFF)
        grade_labels.add(out_of_label)
        self.play(Write(grade_labels))

        grade_hist = Histogram(
            np.ones(4),
            hist_y_values,
            mode = "widths",
            x_labels = "none",
            y_label_position = "center",
            bar_stroke_width = 0,
            outline_stroke_width = 5
        )
        grade_hist.move_to(all_students)

        self.play(FadeIn(grade_hist))


        nb_students_label = TextMobject("\# of students", color = highlight_color)
        nb_students_label.move_to(3 * LEFT + 2 * UP)
        arrows = VGroup(*[
            Arrow(nb_students_label, grade_hist.bars[i].get_center(),
                color = highlight_color)
            for i in range(4)
        ])
        self.play(Write(nb_students_label), LaggedStart(ShowCreation,arrows))

        percentage_label = TextMobject("\% of students", color = highlight_color)
        percentage_label.move_to(nb_students_label)
        percentages = hist_y_values / (nb_students_x * nb_students_y) * 100
        anims = []
        for (label, percentage) in zip(grade_hist.y_labels_group, percentages):
            new_label = DecimalNumber(percentage,
                num_decimal_points = 1,
                unit = "\%",
                color = highlight_color
            )
            new_label.move_to(label)
            anims.append(Transform(label, new_label))
        anims.append(ReplacementTransform(nb_students_label, percentage_label))
        self.play(*anims)

        self.remove(all_quizzes)
        # put small copy of class in corner
        for (i,pi) in enumerate(all_students):
            x = i % 5
            y = i / 5
            pi.move_to(x * RIGHT + y * UP)
        all_students.scale(0.8)
        all_students.to_corner(DOWN + LEFT)
        self.play(FadeIn(all_students))

        prob_label = TextMobject("probability", color = highlight_color)
        prob_label.move_to(percentage_label)
        self.play(
            all_students[8].set_color, MAROON_E,
            all_students[:8].fade, 0.6,
            all_students[9:].fade, 0.6,
            ReplacementTransform(percentage_label, prob_label)
        )

        self.play(
            FadeOut(prob_label),
            FadeOut(arrows)
        )

        for i in range(1):
            self.play(
                FlashThroughHistogram(
                    grade_hist,
                    direction = "vertical",
                    mode = "random",
                    run_time = 5
                )
            )













