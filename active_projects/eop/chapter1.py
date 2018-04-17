from big_ol_pile_of_manim_imports import *
from old_projects.eoc.chapter8 import *
from active_projects.eop.histograms import *

import scipy.special

COIN_RADIUS = 0.3
COIN_THICKNESS = 0.4 * COIN_RADIUS
COIN_FORESHORTENING = 0.3
COIN_NB_RIDGES = 20
COIN_STROKE_WIDTH = 2

COIN_SEQUENCE_SPACING = 0.1

GRADE_COLOR_1 = COLOR_HEADS = RED
GRADE_COLOR_2 = COLOR_TAILS = BLUE


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
        "spacing": COIN_SEQUENCE_SPACING
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
            new_coin.shift(offset * RIGHT)
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
        stack1.next_to(self.anchor, LEFT, buff = SMALL_BUFF)
        stack2.next_to(self.anchor, RIGHT, buff = SMALL_BUFF)
        stack1.align_to(self.anchor, DOWN)
        stack2.align_to(self.anchor, DOWN)
        self.heads_stack = stack1
        self.tails_stack = stack2
        self.add(stack1, stack2)

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

        #print "tallies for row", level, ":", [new_row[i][1] for i in range(2**level)]

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
            print "sorted roots:", [sorted_row[i][2][0] for i in range(2**level)]
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
        self.show_area_model1()

    def show_series(self):
        series = VideoSeries()
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
            *[
                ApplyMethod(pi.change_mode, "pondering")
                for pi in self.get_pi_creatures()
            ]
        )
        self.wait()

        self.series = series

        # # # # # # # # # # # # # # # # # #
        # show examples of the area model #
        # # # # # # # # # # # # # # # # # #
        

    def show_area_model1(self):

        # show independent events

        sample_space_width = sample_space_height = 2.5
        p_of_A = 0.7
        p_of_not_A = 1 - p_of_A
        p_of_B = 0.8
        p_of_not_B = 1 - p_of_B


        rect_A = Rectangle(
            width = p_of_A * sample_space_width,
            height = 1 * sample_space_height,
            stroke_width = 0,
            fill_color = BLUE,
            fill_opacity = 1.0
        ).move_to(2 * RIGHT + 1.5 * UP)

        rect_not_A = Rectangle(
            width = p_of_not_A * sample_space_width,
            height = 1 * sample_space_height,
            stroke_width = 0,
            fill_color = BLUE_E,
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
            fill_color = GREEN,
            fill_opacity = 0.5
        )
        rect_not_B = Rectangle(
            width = 1 * sample_space_width,
            height = p_of_not_B * sample_space_height,
            stroke_width = 0,
            fill_color = GREEN_E,
            fill_opacity = 0.5
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
        indep_formula = indep_formula.scale(0.7).next_to(rect_not_B, UP, buff = MED_LARGE_BUFF)

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

        rect_A_and_B.set_fill(color = GREEN, opacity = 0.5)
        rect_A_and_not_B = Rectangle(
            width = p_of_A * sample_space_width,
            height = p_of_not_B * sample_space_height,
            stroke_width = 0,
            fill_color = GREEN_E,
            fill_opacity = 0.5
        ).next_to(rect_A_and_B, UP, buff = 0)
        
        rect_not_A_and_B = Rectangle(
            width = p_of_not_A * sample_space_width,
            height = p_of_B * sample_space_height,
            stroke_width = 0,
            fill_color = GREEN,
            fill_opacity = 0.5
        ).next_to(rect_A_and_B, RIGHT, buff = 0)

        rect_not_A_and_not_B = Rectangle(
            width = p_of_not_A * sample_space_width,
            height = p_of_not_B * sample_space_height,
            stroke_width = 0,
            fill_color = GREEN_E,
            fill_opacity = 0.5
        ).next_to(rect_not_A_and_B, UP, buff = 0)


        indep_formula.next_to(rect_not_A, LEFT, buff = 4)
        indep_formula.shift(UP)

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
            fill_color = GREEN,
            fill_opacity = 0.5
        ).align_to(rect_A_and_B, DOWN).align_to(rect_A_and_B, LEFT)

        rect_A_and_not_B.target = Rectangle(
            width = p_of_A * sample_space_width,
            height = (1 - p_of_B_knowing_A) * sample_space_height,
            stroke_width = 0,
            fill_color = GREEN_E,
            fill_opacity = 0.5
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
            Transform(indep_formula.get_part_by_tex("\cdot"), rearranged_formula[2][6]),
        )


        self.play(
            FadeOut(VGroup(
                indep_formula, rect_A, rect_B, rect_not_A, rect_not_B,
                rect_A_and_B, rect_A_and_not_B, rect_not_A_and_B, rect_not_A_and_not_B,
                brace_A, brace_B, label_A, label_B_knowing_A, label_A_and_B,
                label_B_knowing_A_copy
            ))
        )


# # # # # # # # # # # # # # # # #
# Old version with SampleSpace  #
# # # # # # # # # # # # # # # # #

    # def show_independent_events(self):
    #     sample_space = SampleSpace(
    #         full_space_config = {
    #             "height" : 3,
    #             "width" : 3,
    #             "fill_opacity" : 0
    #         }
    #     )
    #     sample_space.divide_horizontally(0.4)
    #     sample_space.horizontal_parts.set_fill(opacity = 0)
    #     h_labels = [
    #         TexMobject("P(", "A", ")"),
    #         TexMobject("P(\\text{not }", "A", ")"),
    #     ]
    #     for label in h_labels:
    #         label.scale(0.7)
    #         #self.color_label(label)
    #     sample_space.get_side_braces_and_labels(h_labels)
    #     sample_space.add_braces_and_labels()
    #     h_parts = sample_space.horizontal_parts
    #     for (label, part) in zip(h_labels, h_parts):
    #         label.next_to(part, 2 * LEFT)
    #         sample_space.add(label)

    #     values = [0.2, 0.2]
    #     color_pairs = [(GREEN, BLUE), (GREEN_E, BLUE_E)]
    #     v_parts = VGroup()
    #     for tup in zip(h_parts, values, color_pairs):
    #         part, value, colors = tup
    #         part.divide_vertically(value, colors = colors)
    #         part.vertical_parts.set_fill(opacity = 0.8)
    #         #label = TexMobject(
    #         #    "P(", "B", "|", given_str, "A", ")"
    #         #)
    #         #label.scale(0.7)
    #         #self.color_label(label)
    #         if part == h_parts[0]:
    #             part.get_subdivision_braces_and_labels(
    #                 part.vertical_parts, [label], DOWN
    #             )
    #             sample_space.add(
    #                 part.vertical_parts.braces,
    #             #    part.vertical_parts.labels,
    #             )
    #         v_parts.add(part.vertical_parts.submobjects)
            

    #     v_labels = [
    #         TexMobject("P(", "B", ")"),
    #         TexMobject("P(\\text{not }", "B", ")"),
    #     ]
    #     for (label, part) in zip(v_labels, v_parts[1::2]):
    #         label.scale(0.7)
    #         label.next_to(part, DOWN)
    #         sample_space.add(label)


    #     sample_space.to_edge(LEFT)

    #     self.add(sample_space)
    #     self.sample_space = sample_space

    #     self.wait()





    # def color_label(self, label):
    #     label.set_color_by_tex("B", RED)
    #     label.set_color_by_tex("I", GREEN)




class IllustrateAreaModel2(GraphScene):
    CONFIG = {
        "x_min" : -3.5,
        "x_max" : 3.5,
        "y_min" : -0,
        "y_max" : 0.6,
        "graph_origin": 3*DOWN,
        "num_rects": 20,
        "y_axis_label" : "",
        "x_axis_label" : "",
        "variable_point_label" : "x",
        "y_axis_height" : 4,
        "graph_origin": 2.5 * DOWN + 3 * LEFT,
        "x_axis_width": 5,
        "y_axis_height": 3
    }

    def construct(self):

        x_max_1 = 0
        x_min_1 = -x_max_1

        x_max_2 = 3.5
        x_min_2 = -x_max_2


        self.setup_axes()
        graph = self.get_graph(lambda x: np.exp(-x**2) / ((0.5 * TAU) ** 0.5))

        self.add(graph)

        cdf_formula = TexMobject("P(|X-\mu| < x) = \int_{-x}^x {\exp(-{1\over 2}({t\over \sigma})^2) \over \sigma\sqrt{2\pi}} dt")
        
        cdf_formula.set_color_by_tex("x", YELLOW)
        cdf_formula.next_to(graph, RIGHT, buff = -1)
        self.add(cdf_formula)
        

        self.v_graph = graph
        self.add_T_label(x_min_1, color = YELLOW, animated = False)
        
        self.remove(self.T_label_group, self.right_v_line)
        #self.T_label_group[0].set_fill(opacity = 0).set_stroke(width = 0)
        #self.T_label_group[1].set_fill(opacity = 0).set_stroke(width = 0)
        #self.right_v_line.set_fill(opacity = 0).set_stroke(width = 0)

        #self.add(self.T_label_group)
        area = self.area = self.get_area(graph, x_min_1, x_max_1)
        
        right_bound_label = TexMobject("x", color = YELLOW)
        right_bound_label.next_to(self.coords_to_point(0,0), DOWN)
        right_bound_label.target = right_bound_label.copy().next_to(self.coords_to_point(self.x_max,0), DOWN)
        right_bound_label.set_fill(opacity = 0).set_stroke(width = 0)
        
        left_bound_label = TexMobject("-x", color = YELLOW)
        left_bound_label.next_to(self.coords_to_point(0,0), DOWN)
        left_bound_label.target = right_bound_label.copy().next_to(self.coords_to_point(self.x_min,0), DOWN)
        left_bound_label.set_fill(opacity = 0).set_stroke(width = 0)

        #integral = self.get_riemann_rectangles(
            #graph,x_min = self.x_min, x_max = x_max_1)
        self.add(area)

        def integral_update_func(t):
            return 100 * scipy.special.erf(
                self.point_to_coords(self.right_v_line.get_center())[0]
            )

        cdf_value = DecimalNumber(0, unit = "\%")
        cdf_value.move_to(self.coords_to_point(0,0.2))
        self.add_foreground_mobject(cdf_value)

        self.add(ContinualChangingDecimal(
            decimal_number_mobject = cdf_value,
            number_update_func = integral_update_func,
            num_decimal_points = 1
        ))

        anim = self.get_animation_integral_bounds_change(
            graph, x_min_2, x_max_2, run_time = 3)

        # changing_cdf_value = ChangingDecimal(
        #     decimal_number_mobject = cdf_value,
        #     number_update_func = integral_update_func,
        #     num_decimal_points = 1
        # )

        self.play(
            anim
        )





class IllustrateAreaModel3(Scene):

    def construct(self):

        formula = TexMobject("E[X] = \sum_{i=1}^N p_i x_i").move_to(3 * LEFT + UP)
        self.add(formula)


        x_scale = 5.0
        y_scale = 1.0

        probabilities = np.array([1./8, 3./8, 3./8, 1./8])
        prob_strings = ["{1\over 8}","{3\over 8}","{3\over 8}","{1\over 8}"]
        cumulative_probabilities = np.cumsum(probabilities)
        cumulative_probabilities = np.insert(cumulative_probabilities, 0, 0)
        print cumulative_probabilities
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
                Write(group)
            )



        labels = VGroup()
        for (y, bar) in zip(y_values, hist.bars):
            label = TexMobject(str(int(y))).scale(0.7).next_to(bar, UP, buff = SMALL_BUFF)
            self.play(FadeIn(label))
            labels.add(label)

        y_average = np.mean(y_values)
        averaged_y_values = y_average * np.ones(np.shape(y_values))

        averaged_hist = flat_hist = Histogram(probabilities, averaged_y_values,
            mode = "widths",
            x_scale = x_scale,
            y_scale = y_scale,
            x_labels = "none"
        ).fade(0.2)

        ghost_hist = hist.copy().fade(0.8)
        labels.fade(0.8)
        self.bring_to_back(ghost_hist)

        self.play(Transform(hist, averaged_hist))

        average_label = TexMobject(str(y_average)).scale(0.7).next_to(averaged_hist, UP, SMALL_BUFF)

        one_brace = Brace(averaged_hist, DOWN, buff = 0.1)
        one_p_label = TexMobject(str(1)).next_to(one_brace, DOWN, buff = SMALL_BUFF).scale(0.7)
        one_group = VGroup(one_brace, one_p_label)

        self.play(
            FadeIn(average_label),
            Transform(braces, one_brace),
            Transform(p_labels, one_p_label),
        )
        











class AreaSplitting(Scene):

    def create_rect_row(self,n):
        rects_group = VGroup()
        for k in range(n+1):
            proportion = float(choose(n,k)) / 2**n
            new_rect = Rectangle(
                width = proportion * WIDTH, 
                height = HEIGHT,
                fill_color = graded_color(n,k),
                fill_opacity = 1
            )
            new_rect.next_to(rects_group,RIGHT,buff = 0)
            rects_group.add(new_rect)
        return rects_group

    def split_rect_row(self,rect_row):

        split_row = VGroup()
        for rect in rect_row.submobjects:
            half = rect.copy().stretch_in_place(0.5,0)
            left_half = half.next_to(rect.get_center(),LEFT,buff = 0)
            right_half = half.copy().next_to(rect.get_center(),RIGHT,buff = 0)
            split_row.add(left_half, right_half)
        return split_row


    def rect_center(self,n,i,j):
        if n < 0:
            raise Exception("wrong indices " + str(n) + ", " + str(i) + ", " + str(j))
        if i < 0 or i > n:
            raise Exception("wrong indices " + str(n) + ", " + str(i) + ", " + str(j))
        if j > choose(n,i) or j < 0:
            raise Exception("wrong indices " + str(n) + ", " + str(i) + ", " + str(j))

        rect = self.brick_array[n][i]
        width = rect.get_width()
        left_x = rect.get_center()[0] - width/2
        spacing = width / choose(n,i)
        x = left_x + (j+0.5) * spacing
        return np.array([x,rect.get_center()[1], rect.get_center()[2]])

    def construct(self):

        # Draw the bricks

        brick_wall = VGroup()
        rect_row = self.create_rect_row(0)
        rect_row.move_to(3.5*UP + 0*HEIGHT*DOWN)
        self.add(rect_row)
        brick_wall.add(rect_row)
        self.brick_array = [[rect_row.submobjects[0]]]

        for n in range(NB_ROWS):
            # copy and shift
            new_rect_row = rect_row.copy()
            self.add(new_rect_row)
            self.play(new_rect_row.shift,HEIGHT * DOWN)
            self.wait()

            #split
            split_row = self.split_rect_row(new_rect_row)
            self.play(FadeIn(split_row))
            self.remove(new_rect_row)
            self.wait()

            # merge
            rect_row = self.create_rect_row(n+1)
            rect_row.move_to(3.5*UP + (n+1)*HEIGHT*DOWN)
            self.play(FadeIn(rect_row))
            brick_wall.add(rect_row)
            self.remove(split_row)
            self.wait()

            # add to brick dict
            rect_array = []
            for rect in rect_row.submobjects:
                rect_array.append(rect)

            self.brick_array.append(rect_array)


        self.play(
            brick_wall.set_fill, {"opacity" : 0.2}
        )


        # Draw the branches

        for (n, rect_row_array) in enumerate(self.brick_array):
            for (i, rect) in enumerate(rect_row_array):
                pos = rect.get_center()
                tally = TallyStack(n - i, i)
                tally.move_to(pos)


                # from the left
                lines = VGroup()

                if i > 0:
                    for j in range(choose(n-1,i-1)):
                        start_pos = self.rect_center(n-1,i-1,j)
                        end_pos = self.rect_center(n,i,j)
                        lines.add(Line(start_pos,end_pos, stroke_color = GRADE_COLOR_2))
                    self.play(
                        LaggedStart(ShowCreation, lines))

                # from the right
                lines = VGroup()

                if i < n:
                    for j in range(choose(n-1,i)):
                        start_pos = self.rect_center(n-1,i,j)
                        if i != 0:
                            end_pos = self.rect_center(n,i,choose(n-1,i-1) + j)
                        else:
                            end_pos = self.rect_center(n,i,j)
                    
                        lines.add(Line(start_pos,end_pos, stroke_color = GRADE_COLOR_1))
                    self.play(
                        LaggedStart(ShowCreation, lines))



                #self.play(FadeIn(tally))


class DieFace(SVGMobject):
    
    def __init__(self, value, **kwargs):

        self.value = value
        self.file_name = "Dice-" + str(value)
        self.ensure_valid_file()

        paths, attributes = svg2paths(self.file_path)
        print paths, attributes
        SVGMobject.__init__(self, file_name = self.file_name)
        # for submob in self.submobject_family():
        #     if type(submob) == Rectangle:
        #         submob.set_fill(opacity = 0)
        #         submob.set_stroke(width = 7)

class RowOfDice(VGroup):
    CONFIG = {
        "values" : range(1,7)
    }

    def generate_points(self):
        for value in self.values:
            new_die = DieFace(value)
            new_die.submobjects[0].set_fill(opacity = 0)
            new_die.submobjects[0].set_stroke(width = 7)
            new_die.next_to(self, RIGHT)
            self.add(new_die)



class ShowUncertainty1(PiCreatureScene):

    def throw_a_die(self):

        eye = np.random.randint(1,7)
        face = self.row_of_dice.submobjects[eye - 1]
        self.tallies[eye - 1] += 1

        new_hist = self.hist_from_tallies()

        self.play(
            ApplyMethod(face.submobjects[0].set_fill, {"opacity": 1},
                rate_func = there_and_back,
                run_time = 0.3,
            ),
        )
        self.play(
            Transform(self.dice_histogram, new_hist,
                run_time = 0.5)
        )



    def hist_from_tallies(self):
        x_scale = self.row_of_dice.get_width() / np.size(self.tallies)
        hist = Histogram(np.ones(6), self.tallies, 
            mode = "widths", 
            x_labels = "none",
            y_scale = 0.5,
            x_scale = x_scale
        )

        hist.next_to(self.row_of_dice, UP)
        return hist

    def construct(self):

        self.row_of_dice = RowOfDice().scale(0.5).move_to(3 * DOWN)
        self.add(self.row_of_dice)

        self.tallies = np.zeros(6)
        self.dice_histogram = self.hist_from_tallies()
        
        self.add(self.dice_histogram)

        for i in range(30):
            self.throw_a_die()
            self.wait()




class ShowUncertainty2(PiCreatureScene):


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

























