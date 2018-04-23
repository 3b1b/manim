from big_ol_pile_of_manim_imports import *
from old_projects.eoc.chapter8 import *
from active_projects.eop.histograms import *

import scipy.special

COIN_RADIUS = 0.18
COIN_THICKNESS = 0.4 * COIN_RADIUS
COIN_FORESHORTENING = 0.5
COIN_NB_RIDGES = 20
COIN_STROKE_WIDTH = 2

COIN_SEQUENCE_SPACING = 0.1

GRADE_COLOR_1 = COLOR_HEADS = RED
GRADE_COLOR_2 = COLOR_TAILS = BLUE

TALLY_BACKGROUND_WIDTH = 1.0

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

    def __init__(self, **kwargs):

        coin = PiCreatureCoin()
        PiCreature.__init__(self,**kwargs)
        self.coin = coin
        self.add(coin)
        right_arm = self.get_arm_copies()[1]
        coin.next_to(right_arm, RIGHT+UP, buff = 0)
        coin.shift(0.15 * self.get_width() * LEFT)

    def flip_coin_up(self):
        self.change("raise_right_hand")

class FlipUpAndDown(Animation):
    CONFIG = {
        "vector" : UP,
        "nb_turns" : 1
    }

    def update(self,t):
        self.mobject.shift(4 * t * (1 - t) * self.vector)
        self.mobject.rotate(t * self.nb_turns * TAU)

class FlipCoin(AnimationGroup):
    CONFIG = {
        "rate_func" : there_and_back
    }
    def __init__(self, pi_creature, **kwargs):
        digest_config(self, kwargs)
        pi_creature_motion = ApplyMethod(
            pi_creature.flip_coin_up,
            rate_func = self.rate_func,
            **kwargs
        )
        coin_motion = Succession(
            EmptyAnimation(run_time = 1.0),
            FlipUpAndDown(
                pi_creature.coin, 
                vector = UP,
                nb_turns = 5,
                rate_func = self.rate_func,
                **kwargs
            )
        )
        AnimationGroup.__init__(self,pi_creature_motion, coin_motion)

class CoinFlippingPiCreatureScene(Scene):

    def construct(self):

        randy = CoinFlippingPiCreature()
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
        "coin_thickness": COIN_THICKNESS
    }

    def __init__(self,h,t,anchor = ORIGIN, **kwargs):
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
        background_rect = RoundedRectangle(
            width = TALLY_BACKGROUND_WIDTH,
            height = TALLY_BACKGROUND_WIDTH,
            corner_radius = 0.1,
            fill_color = DARK_GREY,
            fill_opacity = 1.0,
            stroke_width = 3
        ).align_to(self.anchor, DOWN).shift(0.1 * DOWN)
        self.add_to_back(background_rect)

    def move_anchor_to(self, new_anchor):
        for submob in self.submobjects:
            submob.shift(new_anchor - self.anchor)

        self.anchor = new_anchor
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
        self.show_series()
        self.show_examples()

    def show_series(self):
        series = VideoSeries(num_videos = 11)
        series.to_edge(UP)
        this_video = series[0]
        this_video.set_color(YELLOW)
        this_video.save_state()
        this_video.set_fill(opacity = 0)
        this_video.center()
        this_video.scale_to_fit_height(FRAME_HEIGHT)
        self.this_video = this_video


        words = TextMobject(
            "Welcome to \\\\",
            "Essence of Probability"
        )
        words.set_color_by_tex("Essence of Probability", YELLOW)

        self.teacher.change_mode("happy")
        self.play(
            FadeIn(
                series,
                submobject_mode = "lagged_start",
                run_time = 2
            ),
            Blink(self.get_teacher())
        )
        self.teacher_says(words, target_mode = "hooray")
        self.change_student_modes(
            *["hooray"]*3,
            look_at_arg = series[1].get_left(),
            added_anims = [
                ApplyMethod(this_video.restore, run_time = 3),
            ]
        )
        self.play(*[
            ApplyMethod(
                video.shift, 0.5*video.get_height()*DOWN,
                run_time = 3,
                rate_func = squish_rate_func(
                    there_and_back, alpha, alpha+0.3
                )
            )
            for video, alpha in zip(series, np.linspace(0, 0.7, len(series)))
        ]+[
            Animation(self.teacher.bubble),
            Animation(self.teacher.bubble.content),
        ])

        self.play(
            FadeOut(self.teacher.bubble),
            FadeOut(self.teacher.bubble.content),
            self.get_teacher().change_mode, "raise_right_hand",
            *[
                ApplyMethod(pi.change_mode, "pondering")
                for pi in self.get_students()
            ]
        )
        self.wait()

        self.series = series


    def show_examples(self):

        self.wait(10)
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

    def throw_a_die(self):

        eye = np.random.randint(1,7)
        face = self.row_of_dice.submobjects[eye - 1]

        self.play(
            ApplyMethod(face.submobjects[0].set_fill, {"opacity": 1},
                rate_func = there_and_back,
                run_time = 0.3,
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

        for i in range(10):
            self.throw_a_die()
            self.wait(0.1)



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





class ShowUncertainty3(Scene):

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



SICKLY_GREEN = "#9BBD37"

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

        p_sick = TexMobject("p(","\\text{sick}",") = 0.5\%")
        p_sick.set_color_by_tex("sick", SICKLY_GREEN)
        p_sick.next_to(randy, RIGHT+UP)
        self.add(p_sick)
        self.wait()
        self.play(
            randy.change_mode, "sick",
            randy.set_color, SICKLY_GREEN
        )
        self.play(Blink(randy))
        self.play(randy.restore)
        self.play(
            FadeOut(p_sick),
            Write(title),
            LaggedStart(FadeIn, all_creatures, run_time = 3)
        )
        self.wait()



class PascalBrickWall(VMobject):

    CONFIG = {
        "left_color" : YELLOW,
        "right_color" : BLUE,
        "height" : 1.0,
        "width" : 8.0,
        "outcome_shrinkage_factor_x" : 0.85,
        "outcome_shrinkage_factor_y" : 0.95
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
        corner_radius = min(0.1, 0.3 * min(outcome_width, outcome_height))
        # this scales down the corner radius for very narrow rects
        rect = RoundedRectangle(
            width = outcome_width,
            height = outcome_height,
            corner_radius = corner_radius,
            fill_color = BLACK,
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





class SplitRectsInBrickWall(Animation):

    def __init__(self, mobject, **kwargs):

        r = self.subdiv_level = mobject.subdiv_level + 1
        
        self.subdivs = VGroup()
        x = - 0.5 * mobject.width

        for k in range(0, r):
            proportion = float(choose(r,k)) / 2**r
            x += proportion * mobject.width
            subdiv = DashedLine(
                mobject.get_center() + x * RIGHT + 0.5 * mobject.height * UP,
                mobject.get_center() + x * RIGHT + 0.5 * mobject.height * UP,
            )
            self.subdivs.add(subdiv)

        mobject.add(self.subdivs)

        Animation.__init__(self, mobject, **kwargs)





    def update_mobject(self, alpha):
        for subdiv in self.subdivs:
            x = subdiv.get_start()[0]
            start = self.mobject.get_center()
            start += x * RIGHT + 0.5 * self.mobject.height * UP
            end = start + alpha * self.mobject.height * DOWN
            subdiv.put_start_and_end_on(start,end)





class PascalBrickWallScene(Scene):

    def split_tallies(self, direction = DOWN):

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

            if len(self.decimals) > 0:
                decimal = self.decimals[i]
            else:
                decimal = VMobject()

            target_left = tally_targets_left[i]
            new_tally_left = TallyStack(tally.nb_heads + 1, tally.nb_tails)
            new_tally_left.move_anchor_to(target_left)
            v = target_left - tally.anchor
            
            self.play(
                tally.move_anchor_to, target_left,
                decimal.shift,v
            )
            tally.anchor = target_left
            self.play(Transform(tally, new_tally_left))
            
            tally_copy = self.tallies_copy[i]
            decimal_copy = decimal.copy()

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
        if len(self.decimals) > 0:
            self.decimal_copies = VGroup()

        for (i, tally) in enumerate(self.tallies):

            if len(self.decimals) > 0:
                decimal = self.decimals[i]
            else:
                decimal = VMobject()

            target_left = tally_targets_left[i]
            v = target_left - tally.anchor
            
            anims1.append(tally.move_anchor_to)
            anims1.append(target_left)
            anims1.append(decimal.shift)
            anims1.append(v)
            
            tally.anchor = target_left
            
            tally_copy = self.tallies_copy[i]
            decimal_copy = decimal.copy()

            target_right = tally_targets_right[i]
            v = target_right - tally_copy.anchor
            
            anims1.append(tally_copy.move_anchor_to)
            anims1.append(target_right)
            anims1.append(decimal_copy.shift)
            anims1.append(v)
            if len(self.decimals) > 0:
                self.decimal_copies.add(decimal_copy)
            
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



        if len(self.decimals) > 0:
            self.add_foreground_mobject(self.decimal_copies)

        return anims1, anims2

    def split_tallies_at_once(self, direction = DOWN):
        anims1, anims2 = self.tally_split_animations(direction = direction)
        self.play(*(anims1 + anims2))

    def split_tallies_in_two_steps(self, direction = DOWN):
        anims1, anims2 = self.tally_split_animations(direction = direction)
        self.play(*anims1)
        self.wait(0.3)
        self.play(*anims2)




    def split_decimals_alone(self):

        r = self.row.coloring_level
        targets_left = []
        targets_right = []

        for rect in self.row.get_rects_for_level(r):
            target = rect.get_center() + 0.25 * rect.get_width() * LEFT
            targets_left.append(target)
            target = rect.get_center() + 0.25 * rect.get_width() * RIGHT
            targets_right.append(target)

        anims = []
        self.decimal_copies = VGroup()

        for (i, decimal) in enumerate(self.decimals):

            anims.append(decimal.move_to)
            anims.append(targets_left[i])

            decimal_copy = decimal.copy()
            
            anims.append(decimal_copy.move_to)
            anims.append(targets_right[i])
            self.decimal_copies.add(decimal_copy)
            

        self.play(*anims)

        self.add_foreground_mobject(self.decimal_copies)





    def merge_rects_by_subdiv(self):

        half_merged_row = self.row.copy()
        half_merged_row.subdiv_level += 1
        half_merged_row.generate_points()
        half_merged_row.move_to(self.row.get_center())
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

        self.play(FadeIn(merged_row))
        self.row = merged_row


    def merge_decimals(self):

        anims = []
        if self.decimals in self.mobjects:
            anims.append(FadeOut(self.decimals))
        if self.decimal_copies in self.mobjects:
            anims.append(FadeOut(self.decimal_copies))
        
        self.new_decimals = VGroup()
        self.decimal_copies = VGroup()

        r = self.row.coloring_level
        for (i, rect) in enumerate(self.row.rects):
            k = choose(r,i)
            decimal = Integer(k)
            decimal.move_to(rect)
            if rect.get_width() < 0.2:
                # then the rect is too narrow,
                # let the decimal go in dignity
                decimal.set_stroke(width = 0)
                decimal.set_fill(opacity = 0)
            self.new_decimals.add(decimal)

        anims.append(FadeIn(self.new_decimals))
        self.play(*anims)

        self.remove(self.decimal_copies)
        self.decimals = self.new_decimals.copy()
        #self.remove(self.new_decimals)
        self.add_foreground_mobject(self.decimals)




    def move_tallies_on_top(self):
        self.play(
            self.tallies.shift, 1.2 * 0.5 * self.row.height * UP
        )
        for tally in self.tallies:
            tally.anchor += 1.2 * 0.5 * self.row.height * UP

    def construct(self):

        #self.force_skipping()

        randy = CoinFlippingPiCreature()
        randy = randy.scale(0.5).move_to(3*DOWN + 6*LEFT)
        self.add(randy)
        self.row = PascalBrickWall(1, height = 2, width = 10)
        
        self.decimals = VGroup()

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

        self.split_tallies_in_two_steps()
        self.wait()
        self.merge_rects_by_subdiv()
        self.wait()
        self.merge_tallies()
        self.merge_rects_by_coloring()
        self.wait()
        self.move_tallies_on_top()
        
        # show individual outcomes
        outcomes = self.row.get_outcome_rects_for_level(2, with_labels = True)
        self.play(
            LaggedStart(FadeIn, outcomes)
        )
        self.wait()
        self.play(
            LaggedStart(FadeOut, outcomes)
        )

        # show their numbers
        nb_outcomes = [1,2,1]
        self.decimals = VGroup()
        for (n,rect) in zip(nb_outcomes, self.row.rects):
            decimal = Integer(n).move_to(rect)
            self.decimals.add(decimal)
        self.play(
            LaggedStart(FadeIn, self.decimals)
        )
        self.wait()
        self.play(
            LaggedStart(FadeOut, self.decimals)
        )

        self.decimals = VGroup()



        # # # # # # # #
        # THIRD  FLIP #
        # # # # # # # #


        self.play(FlipCoin(randy))

        self.wait()


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

        # show their numbers
        nb_outcomes = [1,3,3,1]
        self.decimals = VGroup()
        for (n,rect) in zip(nb_outcomes, self.row.rects):
            decimal = Integer(n).move_to(rect)
            self.decimals.add(decimal)
        self.play(
            LaggedStart(FadeIn, self.decimals)
        )
        self.wait()
        self.add_foreground_mobject(self.decimals)


        # # # # # # # #
        # FOURTH FLIP #
        # # # # # # # #

        self.play(FlipCoin(randy))

        self.wait()

        self.play(
            SplitRectsInBrickWall(self.row)
        )
        self.wait()

        self.add_foreground_mobject(self.tallies[-1])
        # this tweaks an undesirable overlap in the next animation
        self.split_tallies_at_once(direction = LEFT)
        self.wait()
        self.merge_rects_by_subdiv()
        self.wait()
        self.merge_tallies(direction = LEFT)
        self.merge_rects_by_coloring()
        self.merge_decimals()
        self.wait()


        # # # # # # # #
        # FIFTH  FLIP #
        # # # # # # # #

        self.play(FlipCoin(randy))

        self.wait()

        self.play(
            SplitRectsInBrickWall(self.row)
        )
        self.wait()

        self.split_tallies_at_once(direction = LEFT)
        self.wait()
        self.merge_rects_by_subdiv()
        self.wait()
        self.merge_tallies(direction = LEFT)
        self.merge_rects_by_coloring()
        self.merge_decimals()
        self.wait()


        # # # # # # # #
        # SIXTH  FLIP #
        # # # # # # # #


        self.revert_to_original_skipping_status()

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
        self.add(randy,self.decimals,self.decimal_copies)


        previous_row = self.row.copy()
        self.add(previous_row)

        v = 1.25 * self.row.height * UP
        self.play(
            previous_row.shift, v,
            self.decimals.shift, v,
            self.decimal_copies.shift, v
        )

        self.add(self.row)
        self.bring_to_back(self.row)
        self.row.shift(v)

        w = 1.5 * self.row.height * DOWN
        self.play(
            self.row.shift, w
        )

        self.play(
            SplitRectsInBrickWall(self.row)
        )
        self.wait()

        self.merge_rects_by_subdiv()

        self.wait()


        # show individual outcomes
        outcomes = previous_row.get_outcome_rects_for_level(5, with_labels = False)
        grouped_outcomes = VGroup()
        index = 0
        for i in range(6):
            size = choose(5,i)
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

        n = 5 # level to split
        k = 2 # tally to split

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
            Transform(grouped_outcomes[k],grouped_target_outcomes[k][0][old_tally_sizes[k - 1]:])
        )

        self.play(
            Transform(grouped_outcomes_copy[k],grouped_target_outcomes[k + 1][0][:old_tally_sizes[k]])
        )


        old_tally_sizes.append(0) # makes the ege cases work properly

        # split the other 
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

        decimals_copy = self.decimals.copy()
        decimals_copy2 = self.decimals.copy()

        self.play(
            Transform(grouped_outcomes[k],grouped_target_outcomes[k][0][old_tally_sizes[k - 1]:]),
            Transform(grouped_outcomes_copy[k - 1],grouped_target_outcomes[k][0][:old_tally_sizes[k]]),
            decimals_copy[k - 1].move_to, new_rects[k],
            decimals_copy2[k].move_to, new_rects[k],
            )

        # show new outcome sizes
        new_decimals = VGroup()
        for (i,rect) in zip(new_tally_sizes, new_rects):
            decimal = Integer(i).move_to(rect)
            new_decimals.add(decimal)

        self.play(
            FadeOut(decimals_copy[k - 1]),
            FadeOut(decimals_copy2[k]),
            FadeIn(new_decimals[k])
        )

        # move the old decimals into the new row
        anims = []
        anims.append(decimals_copy2[0].move_to)
        anims.append(new_rects[0])
        for i in range(1,k) + range(k + 1, n):
            anims.append(decimals_copy[i - 1].move_to)
            anims.append(new_rects[i])
            anims.append(decimals_copy2[i].move_to)
            anims.append(new_rects[i])
        anims.append(decimals_copy[n].move_to)
        anims.append(new_rects[n + 1])

        self.play(*anims)

        # fade them out and fade in their sums
        anims = []
        for i in range(1,k) + range(k + 1, n):
            anims.append(FadeOut(decimals_copy[i - 1]))
            anims.append(FadeOut(decimals_copy2[i]))
            anims.append(FadeIn(new_decimals[i]))

        self.play(*anims)

        self.add_foreground_mobject(new_decimals)



























