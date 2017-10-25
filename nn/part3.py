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
            self.move_grad_terms_into_position(
                grad_terms.copy(),
                *self.get_weight_adjustment_anims(edges, cost)
            )
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
            rects.add(SurroundingRectangle(VGroup(*decimal[-5:])))
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
            term.words = TextMobject("Nudge this weight")
            term.words.scale(0.7)
            term.words.next_to(term.number_line, UP, MED_SMALL_BUFF)

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
                Write(w.words, run_time = 1),
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
            self.play(*map(FadeOut, [
                w.dot, w.brace, w.number_line, w.words
            ]))


    ######

    def move_grad_terms_into_position(self, grad_terms, *added_anims):
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
            FadeOut(words),
            *added_anims
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

class GetLostInNotation(PiCreatureScene):
    def construct(self):
        morty = self.pi_creature
        equations = VGroup(
            TexMobject(
                "\\delta", "^L", "=", "\\nabla_a", "C", 
                "\\odot \\sigma'(", "z", "^L)"
            ),
            TexMobject(
                "\\delta", "^l = ((", "w", "^{l+1})^T", 
                "\\delta", "^{l+1}) \\odot \\sigma'(", "z", "^l)"
            ),
            TexMobject(
                "{\\partial", "C", "\\over \\partial", "b", 
                "_j^l} =", "\\delta", "_j^l"
            ),
            TexMobject(
                "{\\partial", "C", " \\over \\partial", 
                "w", "_{jk}^l} = ", "a", "_k^{l-1}", "\\delta", "_j^l"
            ),
        )
        for equation in equations:
            equation.highlight_by_tex_to_color_map({
                "\\delta" : YELLOW,
                "C" : RED,
                "b" : MAROON_B,
                "w" : BLUE,
                "z" : TEAL,
            })
            equation.highlight_by_tex("nabla", WHITE)
        equations.arrange_submobjects(
            DOWN, buff = MED_LARGE_BUFF, aligned_edge = LEFT
        )

        circle = Circle(radius = 3*SPACE_WIDTH)
        circle.set_fill(WHITE, 0)
        circle.set_stroke(WHITE, 0)

        self.play(
            Write(equations),
            morty.change, "confused", equations
        )
        self.dither()
        self.play(morty.change, "pleading")
        self.dither(2)

        ##
        movers = VGroup(*equations.family_members_with_points())
        random.shuffle(movers.submobjects)
        for mover in list(movers):
            if mover.is_subpath:
                movers.remove(mover)
                continue
            mover.set_stroke(WHITE, width = 0)
            mover.target = Circle()
            mover.target.scale(0.5)
            mover.target.set_fill(mover.get_color(), opacity = 0)
            mover.target.set_stroke(BLACK, width = 1)
            mover.target.move_to(mover)
        self.play(
            LaggedStart(
                MoveToTarget, movers,
                run_time = 2,
            ),
            morty.change, "pondering",
        )
        self.dither()

class TODOInsertPreviewLearning(TODOStub):
    CONFIG = {
        "message" : "Insert PreviewLearning"
    }

class ShowAveragingCost(PreviewLearning):
    CONFIG = {
        "network_scale_val" : 0.8,
        "stroke_width_exp" : 1,
        "start_examples_time" : 5,
        "examples_per_adjustment_time" : 2,
        "n_adjustments" : 5,
        "time_per_example" : 1./15,
        "image_height" : 1.2,
    }
    def construct(self):
        self.setup_network()
        self.setup_diff_words()
        self.show_many_examples()

    def setup_network(self):
        self.network_mob.scale(self.network_scale_val)
        self.network_mob.to_edge(DOWN)
        self.network_mob.shift(LEFT)
        self.color_network_edges()

    def setup_diff_words(self):
        last_layer_copy = self.network_mob.layers[-1].deepcopy()
        last_layer_copy.add(self.network_mob.output_labels.copy())
        last_layer_copy.shift(1.5*RIGHT)

        double_arrow = DoubleArrow(
            self.network_mob.output_labels,
            last_layer_copy,
            color = RED
        )
        brace = Brace(
            VGroup(self.network_mob.layers[-1], last_layer_copy), 
            UP
        )
        cost_words = brace.get_text("Cost of \\\\ one example")
        cost_words.highlight(RED)

        self.add(last_layer_copy, double_arrow, brace, cost_words)
        self.set_variables_as_attrs(
            last_layer_copy, double_arrow, brace, cost_words
        )
        self.last_layer_copy = last_layer_copy

    def show_many_examples(self):
        training_data, validation_data, test_data = load_data_wrapper()

        average_words = TextMobject("Average over all training examples")
        average_words.next_to(LEFT, RIGHT)
        average_words.to_edge(UP)
        self.add(average_words)

        n_start_examples = int(self.start_examples_time/self.time_per_example)
        n_examples_per_adjustment = int(self.examples_per_adjustment_time/self.time_per_example)
        for train_in, train_out in training_data[:n_start_examples]:
            self.show_one_example(train_in, train_out)
            self.dither(self.time_per_example)

        #Wiggle all edges
        edges = VGroup(*it.chain(*self.network_mob.edge_groups))
        reversed_edges = VGroup(*reversed(edges))
        self.play(LaggedStart(
            ApplyFunction, edges,
            lambda edge : (
                lambda m : m.rotate_in_place(np.pi/12).highlight(YELLOW),
                edge,
            ),
            rate_func = lambda t : wiggle(t, 4),
            run_time = 3,
        ))

        #Show all, then adjust
        words = TextMobject(
            "Each step \\\\ uses every \\\\ example\\\\",
            "$\\dots$theoretically",
            alignment = ""
        )
        words.highlight(YELLOW)
        words.scale(0.8)
        words.to_corner(UP+LEFT)

        for x in xrange(self.n_adjustments):
            if x < 2:
                self.play(FadeIn(words[x]))
            for train_in, train_out in training_data[:n_examples_per_adjustment]:
                self.show_one_example(train_in, train_out)
                self.dither(self.time_per_example)
            self.play(LaggedStart(
                ApplyMethod, reversed_edges,
                lambda m : (m.rotate_in_place, np.pi),
                run_time = 1,
                lag_ratio = 0.2,
            ))
            if x >= 2:
                self.dither()

    ####

    def show_one_example(self, train_in, train_out):
        if hasattr(self, "curr_image"):
            self.remove(self.curr_image)
        image = MNistMobject(train_in)
        image.scale_to_fit_height(self.image_height)
        image.next_to(
            self.network_mob.layers[0].neurons, UP,
            aligned_edge = LEFT
        )
        self.add(image)
        self.network_mob.activate_layers(train_in)

        index = np.argmax(train_out)
        self.last_layer_copy.neurons.set_fill(opacity = 0)
        self.last_layer_copy.neurons[index].set_fill(WHITE, opacity = 1)
        self.add(self.last_layer_copy)

        self.curr_image = image


class WalkThroughTwoExample(ShowAveragingCost):
    CONFIG = {
        "random_seed" : 0,
    }
    def setup(self):
        np.random.seed(self.random_seed)
        random.seed(self.random_seed)
        self.setup_bases()

    def construct(self):
        self.force_skipping()

        self.setup_network()
        self.setup_diff_words()
        self.show_single_example()
        # self.single_example_influencing_weights()
        self.expand_last_layer()
        self.show_activation_formula()
        self.three_ways_to_increase()
        self.note_connections_to_brightest_neurons()
        self.fire_together_wire_together()
        self.show_desired_increase_to_previous_neurons()
        self.only_keeping_track_of_changes()
        self.show_other_output_neurons()
        self.show_recursion()

    def show_single_example(self):
        two_vect = get_organized_images()[2][0]
        two_out = np.zeros(10)
        two_out[2] = 1.0
        self.show_one_example(two_vect, two_out)
        for layer in self.network_mob.layers:
            layer.neurons.set_fill(opacity = 0)

        self.activate_network(two_vect)
        self.dither()

    def single_example_influencing_weights(self):
        two = self.curr_image
        two.save_state()

        edge_groups = self.network_mob.edge_groups
        def adjust_edge_group_anim(edge_group):
            return LaggedStart(
                ApplyFunction, edge_group,
                lambda edge : (
                    lambda m : m.rotate_in_place(np.pi/12).highlight(YELLOW),
                    edge
                ),
                rate_func = wiggle,
                run_time = 1,
            )


        self.play(
            two.next_to, edge_groups[0].get_corner(DOWN+RIGHT), DOWN,
            adjust_edge_group_anim(edge_groups[0])
        )
        self.play(
            ApplyMethod(
                two.next_to, edge_groups[1].get_corner(UP+RIGHT), UP,
                path_arc = np.pi/6,
            ),
            adjust_edge_group_anim(VGroup(*reversed(edge_groups[1])))
        )
        self.play(
            ApplyMethod(
                two.next_to, edge_groups[2].get_corner(DOWN+RIGHT), DOWN,
                path_arc = -np.pi/6,
            ),
            adjust_edge_group_anim(edge_groups[2])
        )
        self.play(two.restore)
        self.dither()

    def expand_last_layer(self):
        neurons = self.network_mob.layers[-1].neurons
        alt_neurons = self.last_layer_copy.neurons
        output_labels = self.network_mob.output_labels
        alt_output_labels = self.last_layer_copy[-1]
        edges = self.network_mob.edge_groups[-1]

        movers = VGroup(
            neurons, alt_neurons, 
            output_labels, alt_output_labels, 
            *edges
        )
        to_fade = VGroup(self.brace, self.cost_words, self.double_arrow)
        for mover in movers:
            mover.save_state()
            mover.generate_target()
            mover.target.scale_in_place(2)

        neurons.target.to_edge(DOWN, MED_LARGE_BUFF)
        output_labels.target.next_to(neurons.target, RIGHT, MED_SMALL_BUFF)
        alt_neurons.target.next_to(neurons.target, RIGHT, buff = 2)
        alt_output_labels.target.next_to(alt_neurons.target, RIGHT, MED_SMALL_BUFF)

        n_pairs = it.product(
            self.network_mob.layers[-2].neurons, 
            neurons.target
        )
        for edge, (n1, n2) in zip(edges, n_pairs):
            r1 = n1.get_width()/2.0
            r2 = n2.get_width()/2.0
            c1 = n1.get_center()
            c2 = n2.get_center()
            vect = c2 - c1
            norm = np.linalg.norm(vect)
            unit_vect = vect / norm

            edge.target.put_start_and_end_on(
                c1 + unit_vect*r1,
                c2 - unit_vect*r2
            )

        self.play(
            FadeOut(to_fade),
            *map(MoveToTarget, movers)
        )
        self.show_decimals(neurons)
        self.cannot_directly_affect_activations()
        self.show_desired_activation_nudges(neurons, output_labels, alt_output_labels)
        self.focus_on_one_neuron(movers)

    def show_decimals(self, neurons):
        decimals = VGroup()
        for neuron in neurons:
            activation = neuron.get_fill_opacity()
            decimal = DecimalNumber(activation, num_decimal_points = 1)
            decimal.scale_to_fit_width(0.7*neuron.get_width())
            decimal.move_to(neuron)
            if activation > 0.8:
                decimal.highlight(BLACK)
            decimals.add(decimal)

        self.play(Write(decimals, run_time = 2))
        self.dither()
        self.decimals = decimals

    def cannot_directly_affect_activations(self):
        words = TextMobject("You can only adjust weights and biases")
        words.next_to(self.curr_image, RIGHT, MED_SMALL_BUFF, UP)

        edges = VGroup(*self.network_mob.edge_groups.family_members_with_points())
        random.shuffle(edges.submobjects)
        for edge in edges:
            edge.generate_target()
            edge.target.set_stroke(
                random.choice([BLUE, RED]),
                2*random.random()**2,
            )

        self.play(
            LaggedStart(
                Transform, edges,
                lambda e : (e, e.target),
                run_time = 4, 
                rate_func = there_and_back,
            ),
            Write(words, run_time = 2)
        )
        self.play(FadeOut(words))

    def show_desired_activation_nudges(self, neurons, output_labels, alt_output_labels):
        arrows = VGroup()
        rects = VGroup()
        for i, neuron, label in zip(it.count(), neurons, alt_output_labels):
            activation = neuron.get_fill_opacity()
            target_val = 1 if i == 2 else 0
            diff = abs(activation - target_val)
            arrow = Arrow(
                ORIGIN, diff*neuron.get_height()*DOWN,
                color = RED,
            )
            arrow.move_to(neuron.get_right())
            arrow.shift(0.175*RIGHT)
            if i == 2:
                arrow.highlight(BLUE)
                arrow.rotate_in_place(np.pi)
            arrows.add(arrow)

            rect = SurroundingRectangle(VGroup(neuron, label))
            if i == 2:
                rect.highlight(BLUE)
            else:
                rect.highlight(RED)
            rects.add(rect)

        self.play(
            output_labels.shift, SMALL_BUFF*RIGHT,
            LaggedStart(GrowArrow, arrows, run_time = 1)
        )
        self.dither()

        two_rect = rects[2]
        eight_rect = rects[8].copy()
        non_two_rects = VGroup(*[r for r in rects if r is not two_rect])
        self.play(ShowCreation(two_rect))
        self.dither()
        self.remove(two_rect)
        self.play(ReplacementTransform(two_rect.copy(), non_two_rects))
        self.dither()
        self.play(LaggedStart(FadeOut, non_two_rects, run_time = 1))
        self.play(LaggedStart(
            ApplyFunction, arrows,
            lambda arrow : (
                lambda m : m.scale_in_place(0.5).highlight(YELLOW),
                arrow,
            ),
            rate_func = wiggle
        ))
        self.play(ShowCreation(two_rect))
        self.dither()
        self.play(ReplacementTransform(two_rect, eight_rect))
        self.dither()
        self.play(FadeOut(eight_rect))

        self.arrows = arrows

    def focus_on_one_neuron(self, expanded_mobjects):
        network_mob = self.network_mob
        neurons = network_mob.layers[-1].neurons
        labels = network_mob.output_labels
        two_neuron = neurons[2]
        neurons.remove(two_neuron)
        two_label = labels[2]
        labels.remove(two_label)
        expanded_mobjects.remove(*two_neuron.edges_in)
        two_decimal = self.decimals[2]
        self.decimals.remove(two_decimal)
        two_arrow = self.arrows[2]
        self.arrows.remove(two_arrow)

        to_fade = VGroup(*it.chain(
            network_mob.layers[:2],
            network_mob.edge_groups[:2],
            expanded_mobjects,
            self.decimals,
            self.arrows
        ))

        self.play(FadeOut(to_fade))
        self.dither()
        for mob in expanded_mobjects:
            if mob in [neurons, labels]:
                mob.scale(0.5)
                mob.move_to(mob.saved_state)
            else:
                mob.restore()
        for d, a, n in zip(self.decimals, self.arrows, neurons):
            d.scale(0.5)
            d.move_to(n)
            a.scale(0.5)
            a.move_to(n.get_right())
            a.shift(SMALL_BUFF*RIGHT)
        labels.shift(SMALL_BUFF*RIGHT)

        self.set_variables_as_attrs(
            two_neuron, two_label, two_arrow, two_decimal,
        )

    def show_activation_formula(self):
        rhs = TexMobject(
            "=", "\\sigma(",
            "w_0", "a_0", "+",
            "w_1", "a_1", "+",
            "\\cdots", "+",
            "w_{n-1}", "a_{n-1}", "+",
            "b", ")"
        )
        equals = rhs[0]
        sigma = VGroup(rhs[1], rhs[-1])
        w_terms = rhs.get_parts_by_tex("w_")
        a_terms = rhs.get_parts_by_tex("a_")
        plus_terms = rhs.get_parts_by_tex("+")
        b = rhs.get_part_by_tex("b", substring = False)
        dots = rhs.get_part_by_tex("dots")

        w_terms.highlight(BLUE)
        b.highlight(MAROON_B)
        sigma.highlight(YELLOW)

        rhs.to_corner(UP+RIGHT)
        sigma.save_state()
        sigma.shift(DOWN)
        sigma.set_fill(opacity = 0)

        prev_neurons = self.network_mob.layers[-2].neurons
        edges = self.two_neuron.edges_in

        neuron_copy = VGroup(
            self.two_neuron.copy(),
            self.two_decimal.copy(),
        )

        self.play(
            neuron_copy.next_to, equals.get_left(), LEFT,
            self.curr_image.to_corner, UP+LEFT,
            Write(equals)
        )
        self.play(
            ReplacementTransform(edges.copy(), w_terms),
            Write(VGroup(*plus_terms[:-1])),
            Write(dots),
            run_time = 1.5
        )
        self.dither()
        self.play(ReplacementTransform(
            prev_neurons.copy(), a_terms,
            path_arc = np.pi/2
        ))
        self.dither()
        self.play(
            Write(plus_terms[-1]),
            Write(b)
        )
        self.dither()
        self.play(sigma.restore)
        self.dither(2)

        self.set_variables_as_attrs(
            rhs, w_terms, a_terms, b,
            lhs = neuron_copy
        )

    def three_ways_to_increase(self):
        w_terms = self.w_terms
        a_terms = self.a_terms
        b = self.b
        increase_words = VGroup(
            TextMobject("Increase", "$b$"),
            TextMobject("Increase", "$w_i$"),
            TextMobject("Change", "$a_i$"),
        )
        for words in increase_words:
            words.highlight_by_tex_to_color_map({
                "b" : b.get_color(),
                "w_" : w_terms.get_color(),
                "a_" : a_terms.get_color(),
            })
        increase_words.arrange_submobjects(
            DOWN, aligned_edge = LEFT,
            buff = LARGE_BUFF
        )
        increase_words.to_edge(LEFT)

        mobs = [b, w_terms[0], a_terms[0]]
        for words, mob in zip(increase_words, mobs):
            self.play(
                Write(words[0], run_time = 1),
                ReplacementTransform(mob.copy(), words[1])
            )
            self.dither()

        self.increase_words = increase_words

    def note_connections_to_brightest_neurons(self):
        w_terms = self.w_terms
        a_terms = self.a_terms
        increase_words = self.increase_words
        prev_neurons = self.network_mob.layers[-2].neurons
        edges = self.two_neuron.edges_in

        prev_activations = np.array([n.get_fill_opacity() for n in prev_neurons])
        sorted_indices = np.argsort(prev_activations.flatten())
        bright_neurons = VGroup()
        edges_to_bright_neurons = VGroup()
        for i in sorted_indices[-4:]:
            bright_neurons.add(prev_neurons[i].copy())
            bright_neurons.set_stroke(YELLOW, 3)
            edges_to_bright_neurons.add(edges[i])
        bright_edges = edges_to_bright_neurons.copy()
        bright_edges.set_stroke(YELLOW, 4)

        added_words = TextMobject("in proportion to $a_i$")
        added_words.next_to(
            increase_words[1], DOWN, 
            1.5*SMALL_BUFF, LEFT
        )
        added_words.highlight(YELLOW)

        terms_rect = SurroundingRectangle(
            VGroup(w_terms[0], a_terms[0]),
            color = WHITE
        )

        self.play(LaggedStart(
            ApplyFunction, edges,
            lambda edge : (
                lambda m : m.rotate_in_place(np.pi/12).highlight(YELLOW),
                edge
            ),
            rate_func = wiggle
        ))
        self.dither()
        self.play(
            ShowCreation(bright_edges),
            ShowCreation(bright_neurons)
        )
        self.dither()
        self.play(
            ReplacementTransform(bright_edges[0].copy(), w_terms[0]),
            ReplacementTransform(bright_neurons[0].copy(), a_terms[0]),
            ShowCreation(terms_rect)
        )
        self.play(FadeOut(terms_rect))
        self.dither()
        self.play(
            self.curr_image.shift, MED_LARGE_BUFF*RIGHT,
            rate_func = wiggle
        )
        self.dither()
        self.play(Write(added_words))
        self.dither()

        self.set_variables_as_attrs(
            bright_neurons, bright_edges,
            in_proportion_to_a = added_words
        )

    def fire_together_wire_together(self):
        bright_neurons = self.bright_neurons
        bright_edges = self.bright_edges
        two_neuron = self.two_neuron
        two_decimal = self.two_decimal
        two_activation = two_decimal.number

        def get_edge_animation():
            return LaggedStart(
                ShowCreationThenDestruction, bright_edges,
                lag_ratio = 0.7
            )
        neuron_arrows = VGroup(*[
            Vector(MED_LARGE_BUFF*RIGHT).next_to(n, LEFT)
            for n in bright_neurons
        ])
        two_neuron_arrow = Vector(MED_LARGE_BUFF*DOWN)
        two_neuron_arrow.next_to(two_neuron, UP)
        VGroup(neuron_arrows, two_neuron_arrow).highlight(YELLOW)

        neuron_rects = VGroup(*map(
            SurroundingRectangle, bright_neurons
        ))
        two_neuron_rect = SurroundingRectangle(two_neuron)
        seeing_words = TextMobject("Seeing a 2")
        seeing_words.scale(0.8)
        thinking_words = TextMobject("Thinking about a 2")
        thinking_words.scale(0.8)
        seeing_words.next_to(neuron_rects, UP)
        thinking_words.next_to(two_neuron_arrow, RIGHT)

        morty = Mortimer()
        morty.scale(0.8)
        morty.to_corner(DOWN+RIGHT)
        words = TextMobject("""
            ``Neurons that \\\\
            fire together \\\\
            wire together''
        """)
        words.to_edge(RIGHT)

        self.play(FadeIn(morty))
        self.play(
            Write(words),
            morty.change, "speaking", words
        )
        self.play(Blink(morty))
        self.play(
            get_edge_animation(),
            morty.change, "pondering", bright_edges
        )
        self.play(get_edge_animation())
        self.play(
            LaggedStart(GrowArrow, neuron_arrows),
            get_edge_animation(),
        )
        self.play(
            GrowArrow(two_neuron_arrow),
            morty.change, "raise_right_hand", two_neuron
        )
        self.play(
            ApplyMethod(two_neuron.set_fill, WHITE, 1),
            ChangingDecimal(
                two_decimal,
                lambda a : interpolate(two_activation, 1, a),
                num_decimal_points = 1,
            ),
            UpdateFromFunc(
                two_decimal,
                lambda m : m.highlight(WHITE if m.number < 0.8 else BLACK),
            ),
            LaggedStart(ShowCreation, bright_edges),
            run_time = 2,
        )
        self.dither()
        self.play(
            LaggedStart(ShowCreation, neuron_rects),
            Write(seeing_words, run_time = 2),
            morty.change, "thinking", seeing_words
        )
        self.dither()
        self.play(
            ShowCreation(two_neuron_rect),
            Write(thinking_words, run_time = 2),
            morty.look_at, thinking_words
        )
        self.dither()
        self.play(LaggedStart(FadeOut, VGroup(
            neuron_rects, two_neuron_rect,
            seeing_words, thinking_words,
            words, morty,
            neuron_arrows, two_neuron_arrow,
            bright_edges, bright_neurons,
        )))
        self.play(
            ApplyMethod(two_neuron.set_fill, WHITE, two_activation),
            ChangingDecimal(
                two_decimal,
                lambda a : interpolate(1, two_activation, a),
                num_decimal_points = 1,
            ),
            UpdateFromFunc(
                two_decimal,
                lambda m : m.highlight(WHITE if m.number < 0.8 else BLACK),
            ),
        )

    def show_desired_increase_to_previous_neurons(self):
        increase_words = self.increase_words
        two_neuron = self.two_neuron
        edges = two_neuron.edges_in
        prev_neurons = self.network_mob.layers[-2].neurons

        positive_arrows = VGroup()
        negative_arrows = VGroup()
        positive_edges = VGroup()
        negative_edges = VGroup()
        positive_neurons = VGroup()
        negative_neurons = VGroup()
        for neuron, edge in zip(prev_neurons, edges):
            value = edge.get_stroke_width()
            if Color(edge.get_stroke_color()) == Color(self.negative_edge_color):
                value *= -1
            arrow = Vector(0.25*value*UP, color = edge.get_color())
            arrow.stretch_to_fit_height(neuron.get_height())
            arrow.move_to(neuron.get_left())
            arrow.shift(SMALL_BUFF*LEFT)
            if value > 0:
                positive_arrows.add(arrow)
                positive_edges.add(edge)
                positive_neurons.add(neuron)
            else:
                negative_arrows.add(arrow)
                negative_edges.add(edge)
                negative_neurons.add(neuron)

        added_words = TextMobject("in proportion to $w_i$")
        added_words.highlight(self.w_terms.get_color())
        added_words.next_to(
            increase_words[-1], DOWN,
            SMALL_BUFF, aligned_edge = LEFT
        )

        self.play(LaggedStart(
            ApplyFunction, prev_neurons,
            lambda neuron : (
                lambda m : m.scale_in_place(0.5).highlight(YELLOW),
                neuron
            ),
            rate_func = wiggle
        ))
        self.dither()
        for positive in [True, False]:
            if positive:
                arrows = positive_arrows
                edges = positive_edges
                neurons = positive_neurons
                color = self.positive_edge_color
            else:
                arrows = negative_arrows
                edges = negative_edges
                neurons = negative_neurons
                color = self.negative_edge_color
            self.play(
                LaggedStart(
                    Transform, edges,
                    lambda mob : (
                        mob,
                        Dot(
                            mob.get_center(),
                            stroke_color = edges[0].get_color(), 
                            stroke_width = 1,
                            radius = 0.25*SMALL_BUFF,
                            fill_opacity = 0
                        )
                    ),
                    rate_func = there_and_back
                ),
                neurons.set_stroke, color, 3,
            )
            self.play(
                LaggedStart(GrowArrow, arrows),
                ApplyMethod(
                    neurons.set_fill, color, 1,
                    rate_func = there_and_back,
                )
            )
        self.dither()
        self.play(Write(added_words, run_time = 1))

        self.set_variables_as_attrs(
            in_proportion_to_w = added_words,
            prev_neuron_arrows = VGroup(positive_arrows, negative_arrows),
        )

    def only_keeping_track_of_changes(self):
        arrows = self.prev_neuron_arrows
        prev_neurons = self.network_mob.layers[-2].neurons
        rect = SurroundingRectangle(VGroup(arrows, prev_neurons))

        words = TextMobject("No direct influence")
        words.next_to(rect, UP)

        self.revert_to_original_skipping_status()
        self.play(ShowCreation(rect))
        self.play(Write(words))
        self.dither()
        self.play(FadeOut(VGroup(words, rect)))

    def show_other_output_neurons(self):
        two_neuron = self.two_neuron
        two_decimal = self.two_decimal
        two_edges = two_neuron.edges_in
        

    def show_recursion(self):
        pass



































