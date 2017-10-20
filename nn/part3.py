from nn.network import *
from nn.part1 import *
from nn.part2 import *

class LayOutPlan(Scene):
    def construct(self):
        title = TextMobject("Plan")
        title.scale(1.5)
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT).scale(SPACE_WIDTH - 1)
        h_line.next_to(title, DOWN)

        items = BulletedList(
            "Recap",
            "Intuitive walkthrough",
            "Derivatives in \\\\ computational graphs",
        )
        items.to_edge(LEFT, buff = LARGE_BUFF)
        self.add(items)

        rect = ScreenRectangle()
        rect.scale_to_fit_width(2*SPACE_WIDTH - items.get_width() - 2)
        rect.next_to(items, RIGHT, MED_LARGE_BUFF)

        self.play(
            Write(title),
            ShowCreation(h_line),
            ShowCreation(rect),
            run_time = 2
        )
        for i in range(len(items)):
            self.play(items.fade_all_but, i)
            self.dither(2)

class TODOInsertFeedForwardAnimations(TODOStub):
    CONFIG = {
        "message" : "Insert Feed Forward Animations"
    }

class TODOInsertStepsDownCostSurface(TODOStub):
    CONFIG = {
        "message" : "Insert Steps Down Cost Surface"
    }

class TODOInsertDefinitionOfCostFunction(TODOStub):
    CONFIG = {
        "message" : "Insert Definition of cost function"
    }

class TODOInsertGradientNudging(TODOStub):
    CONFIG = {
        "message" : "Insert GradientNudging"
    }

class InterpretGradientComponents(GradientNudging):
    CONFIG = {
        "network_mob_config" : {
            "layer_to_layer_buff" : 3,
        },
        "stroke_width_exp" : 2,
        "n_decimals" : 6,
        "n_steps" : 3,
        "start_cost" : 3.48,
        "delta_cost" : -0.21,
    }
    def construct(self):
        self.setup_network()
        self.add_cost()
        self.add_gradient()
        self.change_weights_repeatedly()
        self.ask_about_high_dimensions()
        self.circle_magnitudes()
        self.isolate_particular_weights()
        self.shift_cost_expression()
        self.tweak_individual_weights()

    def setup_network(self):
        self.network_mob.scale(0.55)
        self.network_mob.to_corner(UP+RIGHT)
        self.color_network_edges()

    def add_cost(self):
        rect = SurroundingRectangle(self.network_mob)
        rect.highlight(RED)
        arrow = Vector(DOWN, color = RED)
        arrow.shift(rect.get_bottom())
        cost = DecimalNumber(self.start_cost)
        cost.highlight(RED)
        cost.next_to(arrow, DOWN)

        cost_expression = TexMobject(
            "C(", "w_0, w_1, \\dots, w_{13{,}001}", ")", "="
        )
        for tex in "()":
            cost_expression.highlight_by_tex(tex, RED)
        cost_expression.next_to(cost, DOWN)
        cost_group = VGroup(cost_expression, cost)
        cost_group.arrange_submobjects(RIGHT)
        cost_group.next_to(arrow, DOWN)

        self.add(rect, arrow, cost_group)

        self.set_variables_as_attrs(
            cost, cost_expression, cost_group,
            network_rect = rect
        )

    def change_weights_repeatedly(self):
        decimals = self.grad_vect.decimals
        grad_terms = self.grad_vect.contents
        edges = VGroup(*reversed(list(
            it.chain(*self.network_mob.edge_groups)
        )))
        cost = self.cost

        for x in range(self.n_steps):
            self.move_grad_terms_into_position(grad_terms.copy())
            self.play(*self.get_weight_adjustment_anims(edges, cost))
            self.play(*self.get_decimal_change_anims(decimals))

    def ask_about_high_dimensions(self):
        grad_vect = self.grad_vect

        words = TextMobject(
            "Direction in \\\\ ${13{,}002}$ dimensions?!?")
        words.highlight(YELLOW)
        words.move_to(grad_vect).to_edge(DOWN)
        arrow = Arrow(
            words.get_top(),
            grad_vect.get_bottom(),
            buff = SMALL_BUFF
        )

        randy = Randolph()
        randy.scale(0.6)
        randy.next_to(words, LEFT)
        randy.shift_onto_screen()

        self.play(
            Write(words, run_time = 2), 
            GrowArrow(arrow),
        )
        self.play(FadeIn(randy))
        self.play(randy.change, "confused", words)
        self.play(Blink(randy))
        self.dither()
        self.play(*map(FadeOut, [randy, words, arrow]))

    def circle_magnitudes(self):
        rects = VGroup()
        for decimal in self.grad_vect.decimals:
            rects.add(SurroundingRectangle(VGroup(*decimal[-4:])))
        rects.highlight(WHITE)

        self.play(LaggedStart(ShowCreation, rects))
        self.play(FadeOut(rects))

    def isolate_particular_weights(self):
        vect_contents = self.grad_vect.contents
        w_terms = self.cost_expression[1]

        edges = self.network_mob.edge_groups
        edge1 = self.network_mob.layers[1].neurons[3].edges_in[0].copy()
        edge2 = self.network_mob.layers[1].neurons[9].edges_in[15].copy()
        VGroup(edge1, edge2).set_stroke(width = 4)
        d1 = DecimalNumber(3.2)
        d2 = DecimalNumber(0.1)
        VGroup(edge1, d1).highlight(YELLOW)
        VGroup(edge2, d2).highlight(MAROON_B)
        new_vect_contents = VGroup(
            TexMobject("\\vdots"),
            d1, TexMobject("\\vdots"),
            d2, TexMobject("\\vdots"),
        )
        new_vect_contents.arrange_submobjects(DOWN)
        new_vect_contents.move_to(vect_contents)

        new_w_terms = TexMobject(
            "\\dots", "w_n", "\\dots", "w_k", "\\dots"
        )
        new_w_terms.move_to(w_terms, DOWN)
        new_w_terms[1].highlight(d1.get_color())
        new_w_terms[3].highlight(d2.get_color())

        for d, edge in (d1, edge1), (d2, edge2):
            d.arrow = Arrow(
                d.get_right(), edge.get_center(),
                color = d.get_color()
            )

        self.play(
            FadeOut(vect_contents),
            FadeIn(new_vect_contents),
            FadeOut(w_terms),
            FadeIn(new_w_terms),
            edges.set_stroke, LIGHT_GREY, 0.35,
        )
        self.play(GrowArrow(d1.arrow))
        self.play(ShowCreation(edge1))
        self.dither()
        self.play(GrowArrow(d2.arrow))
        self.play(ShowCreation(edge2))
        self.dither(2)

        self.cost_expression.remove(w_terms)
        self.cost_expression.add(new_w_terms)
        self.set_variables_as_attrs(
            edge1, edge2, new_w_terms, 
            new_decimals = VGroup(d1, d2)
        )

    def shift_cost_expression(self):
        self.play(self.cost_group.shift, DOWN+0.5*LEFT)

    def tweak_individual_weights(self):
        cost = self.cost
        cost_num = cost.number
        edges = VGroup(self.edge1, self.edge2)
        decimals = self.new_decimals
        changes = (1.0, 1./32)
        wn = self.new_w_terms[1]
        wk = self.new_w_terms[3]

        number_line_template = NumberLine(
            x_min = -1,
            x_max = 1,
            tick_frequency = 0.25,
            numbers_with_elongated_ticks = [],
            color = WHITE
        )
        for term in wn, wk, cost:
            term.number_line = number_line_template.copy()
            term.brace = Brace(term.number_line, DOWN, buff = SMALL_BUFF)
            group = VGroup(term.number_line, term.brace)
            group.next_to(term, UP)
            term.dot = Dot()
            term.dot.highlight(term.get_color())
            term.dot.move_to(term.number_line.get_center())
            term.dot.save_state()
            term.dot.move_to(term)
            term.dot.set_fill(opacity = 0)

        groups = [
            VGroup(d, d.arrow, edge, w)
            for d, edge, w in zip(decimals, edges, [wn, wk])
        ]
        for group in groups:
            group.save_state()

        for i in range(2):
            group1, group2 = groups[i], groups[1-i]
            change = changes[i]
            edge = edges[i]
            w = group1[-1]
            added_anims = []
            if i == 0:
                added_anims = [
                    GrowFromCenter(cost.brace),
                    ShowCreation(cost.number_line),
                    cost.dot.restore
                ]
            self.play(
                group1.restore,
                group2.fade, 0.7,
                GrowFromCenter(w.brace),
                ShowCreation(w.number_line),
                w.dot.restore,
                *added_anims
            )
            for x in range(2):
                func = lambda a : interpolate(
                    cost_num, cost_num-change, a
                )
                self.play(
                    ChangingDecimal(cost, func),
                    cost.dot.shift, change*RIGHT,
                    w.dot.shift, 0.25*RIGHT,
                    edge.set_stroke, None, 8,
                    rate_func = lambda t : wiggle(t, 4),
                    run_time = 2,
                )
                self.dither()
            self.play(*map(FadeOut, [w.dot, w.brace, w.number_line]))


    ######

    def move_grad_terms_into_position(self, grad_terms):
        cost_expression = self.cost_expression
        w_terms = self.cost_expression[1]
        points = VGroup(*[
            VectorizedPoint()
            for term in grad_terms
        ])
        points.arrange_submobjects(RIGHT)
        points.replace(w_terms, dim_to_match = 0)

        grad_terms.generate_target()
        grad_terms.target[len(grad_terms)/2].rotate(np.pi/2)
        grad_terms.target.arrange_submobjects(RIGHT)
        grad_terms.target.scale_to_fit_width(cost_expression.get_width())
        grad_terms.target.next_to(cost_expression, DOWN)

        words = TextMobject("Nudge weights")
        words.scale(0.8)
        words.next_to(grad_terms.target, DOWN)

        self.play(
            MoveToTarget(grad_terms),
            FadeIn(words)
        )
        self.play(
            Transform(
                grad_terms, points,
                remover = True,
                submobject_mode = "lagged_start",
                run_time = 1
            ),
            FadeOut(words)
        )

    def get_weight_adjustment_anims(self, edges, cost):
        start_cost = cost.number
        target_cost = start_cost + self.delta_cost
        w_terms = self.cost_expression[1]

        return [
            self.get_edge_change_anim(edges),
            LaggedStart(
                Indicate, w_terms,
                rate_func = there_and_back,
                run_time = 1.5,
            ),
            ChangingDecimal(
                cost, 
                lambda a : interpolate(start_cost, target_cost, a),
                run_time = 1.5
            )
        ]















































