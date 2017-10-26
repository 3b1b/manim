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
        self.setup_network()
        self.setup_diff_words()
        self.show_single_example()
        self.single_example_influencing_weights()
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
        neurons[2].save_state()

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

        #Show changing activations
        anims = []
        def get_decimal_update(start, end):
            return lambda a : interpolate(start, end, a)
        for i in range(10):
            target = 1.0 if i == 2 else 0.01
            anims += [neurons[i].set_fill, WHITE, target]
            decimal = self.decimals[i]
            anims.append(ChangingDecimal(
                decimal,
                get_decimal_update(decimal.number, target),
                num_decimal_points = 1
            ))
            anims.append(UpdateFromFunc(
                self.decimals[i],
                lambda m : m.set_fill(WHITE if m.number < 0.8 else BLACK)
            ))

        self.play(
            *anims,
            run_time = 3,
            rate_func = there_and_back
        )

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
                lambda m : m.rotate_in_place(np.pi/12).set_stroke(YELLOW),
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
        self.dither()
        for x in range(2):
            self.play(LaggedStart(ShowCreationThenDestruction, bright_edges))
        self.play(LaggedStart(ShowCreation, bright_edges))
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
        all_arrows = VGroup()
        positive_edges = VGroup()
        negative_edges = VGroup()
        positive_neurons = VGroup()
        negative_neurons = VGroup()
        for neuron, edge in zip(prev_neurons, edges):
            value = self.get_edge_value(edge)
            arrow = self.get_neuron_nudge_arrow(edge)
            arrow.move_to(neuron.get_left())
            arrow.shift(SMALL_BUFF*LEFT)
            all_arrows.add(arrow)
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
        self.play(prev_neurons.set_stroke, WHITE, 2)

        self.set_variables_as_attrs(
            in_proportion_to_w = added_words,
            prev_neuron_arrows = all_arrows,
        )

    def only_keeping_track_of_changes(self):
        arrows = self.prev_neuron_arrows
        prev_neurons = self.network_mob.layers[-2].neurons
        rect = SurroundingRectangle(VGroup(arrows, prev_neurons))

        words = TextMobject("No direct influence")
        words.next_to(rect, UP)

        self.play(ShowCreation(rect))
        self.play(Write(words))
        self.dither()
        self.play(FadeOut(VGroup(words, rect)))

    def show_other_output_neurons(self):
        two_neuron = self.two_neuron
        two_decimal = self.two_decimal
        two_arrow = self.two_arrow
        two_label = self.two_label
        two_edges = two_neuron.edges_in

        prev_neurons = self.network_mob.layers[-2].neurons
        neurons = self.network_mob.layers[-1].neurons
        prev_neuron_arrows = self.prev_neuron_arrows
        arrows_to_fade = VGroup(prev_neuron_arrows)

        output_labels = self.network_mob.output_labels
        quads = zip(neurons, self.decimals, self.arrows, output_labels)

        self.play(
            two_neuron.restore,
            two_decimal.scale, 0.5,
            two_decimal.move_to, two_neuron.saved_state,
            two_arrow.scale, 0.5,
            two_arrow.next_to, two_neuron.saved_state, RIGHT, 0.5*SMALL_BUFF,
            two_label.scale, 0.5,
            two_label.next_to, two_neuron.saved_state, RIGHT, 1.5*SMALL_BUFF,
            FadeOut(VGroup(self.lhs, self.rhs)),
            *[e.restore for e in two_edges]
        )
        for neuron, decimal, arrow, label in quads[:2]:
            plusses = VGroup()
            new_arrows = VGroup()
            for edge, prev_arrow in zip(neuron.edges_in, prev_neuron_arrows):
                plus = TexMobject("+").scale(0.5)
                plus.move_to(prev_arrow)
                plus.shift(2*SMALL_BUFF*LEFT)
                new_arrow = self.get_neuron_nudge_arrow(edge)
                new_arrow.move_to(plus)
                new_arrow.shift(2*SMALL_BUFF*LEFT)
                plusses.add(plus)
                new_arrows.add(new_arrow)

            self.play(
                FadeIn(VGroup(neuron, decimal, arrow, label)),
                LaggedStart(ShowCreation, neuron.edges_in),
            )
            self.play(
                ReplacementTransform(neuron.edges_in.copy(), new_arrows),
                Write(plusses, run_time = 2)
            )

            arrows_to_fade.add(new_arrows, plusses)
            prev_neuron_arrows = new_arrows

        all_dots_plus = VGroup()
        for arrow in prev_neuron_arrows:
            dots_plus = TexMobject("\\cdots +")
            dots_plus.scale(0.5)
            dots_plus.move_to(arrow.get_center(), RIGHT)
            dots_plus.shift(2*SMALL_BUFF*LEFT)
            all_dots_plus.add(dots_plus)
        arrows_to_fade.add(all_dots_plus)

        self.play(
            LaggedStart(
                FadeIn, VGroup(*it.starmap(VGroup, quads[-7:])),
            ),
            LaggedStart(
                FadeIn, VGroup(*[n.edges_in for n in neurons[-7:]])
            ),
            Write(all_dots_plus),
            run_time = 3,
        )
        self.dither(2)

        def squish(p): 
            return p[1]*UP
        self.play(
            arrows_to_fade.apply_function, squish,
            arrows_to_fade.move_to, prev_neurons,
        )

    def show_recursion(self):
        network_start = VGroup(*it.chain(
            self.network_mob.edge_groups[1],
            self.network_mob.layers[1],
            self.network_mob.edge_groups[0],
            self.network_mob.layers[0],
        ))
        words_to_fade = VGroup(
            self.increase_words,
            self.in_proportion_to_w,
            self.in_proportion_to_a,
        )

        self.play(
            FadeOut(words_to_fade),
            LaggedStart(FadeIn, network_start, run_time = 3)
        )
        self.dither()
        for i in 1, 0:
            edges = self.network_mob.edge_groups[i]
            self.play(LaggedStart(
                ApplyFunction, edges,
                lambda edge : (
                    lambda m : m.rotate_in_place(np.pi/12).highlight(YELLOW),
                    edge
                ),
                rate_func = wiggle
            ))
            self.dither()

    ####

    def get_neuron_nudge_arrow(self, edge):
        value = self.get_edge_value(edge)
        height = np.sign(value)*0.1 + 0.1*value
        arrow = Vector(height*UP, color = edge.get_color())
        return arrow

    def get_edge_value(self, edge):
        value = edge.get_stroke_width()
        if Color(edge.get_stroke_color()) == Color(self.negative_edge_color):
            value *= -1
        return value

class NotANeuroScientist(TeacherStudentsScene):
    def construct(self):
        quote = TextMobject("``Neurons that fire together wire together''")
        quote.to_edge(UP)
        self.add(quote)
        asterisks = TextMobject("***")
        asterisks.next_to(quote.get_corner(UP+RIGHT), RIGHT, SMALL_BUFF)
        asterisks.highlight(BLUE)

        brain = SVGMobject(file_name = "brain")
        brain.scale_to_fit_height(1.5)
        self.add(brain)
        double_arrow = DoubleArrow(LEFT, RIGHT)
        double_arrow.next_to(brain, RIGHT)
        q_marks = TextMobject("???")
        q_marks.next_to(double_arrow, UP)

        network = NetworkMobject(Network(sizes = [6, 4, 4, 5]))
        network.scale_to_fit_height(1.5)
        network.next_to(double_arrow, RIGHT)

        group = VGroup(brain, double_arrow, q_marks, network)
        group.next_to(self.students, UP, buff = 1.5)
        self.add(group)
        self.add(ContinualEdgeUpdate(
            network,
            stroke_width_exp = 0.5,
            color = [BLUE, RED],
        ))

        rect = SurroundingRectangle(group)
        no_claim_words = TextMobject("No claims here...")
        no_claim_words.next_to(rect, UP)
        no_claim_words.highlight(YELLOW)

        brain_outline = brain.copy()
        brain_outline.set_fill(opacity = 0)
        brain_outline.set_stroke(BLUE, 3)
        brain_anim = ShowCreationThenDestruction(brain_outline)

        words = TextMobject("Definitely not \\\\ a neuroscientist")
        words.next_to(self.teacher, UP, buff = 1.5)
        words.shift_onto_screen()
        arrow = Arrow(words.get_bottom(), self.teacher.get_top())

        self.play(
            Write(words),
            GrowArrow(arrow),
            self.teacher.change, "guilty", words,
            run_time = 1,
        )
        self.change_student_modes(*3*["sassy"])
        self.play(
            ShowCreation(rect),
            Write(no_claim_words, run_time = 1),
            brain_anim
        )
        self.dither()
        self.play(brain_anim)
        self.play(FocusOn(asterisks))
        self.play(Write(asterisks, run_time = 1))
        for x in range(2):
            self.play(brain_anim)
            self.dither()

class ConstructGradientFromAllTrainingExamples(Scene):
    CONFIG = { 
        "image_height" : 0.9,
        "eyes_height" : 0.25,
        "n_examples" : 6,
        "change_scale_val" : 0.8,
    }
    def construct(self):
        self.setup_grid()
        self.setup_weights()
        self.show_two_requesting_changes()
        self.show_all_examples_requesting_changes()
        self.average_together()
        self.collapse_into_gradient_vector()

    def setup_grid(self):
        h_lines = VGroup(*[
            Line(LEFT, RIGHT).scale(0.85*SPACE_WIDTH)
            for x in range(6)
        ])
        h_lines.arrange_submobjects(DOWN, buff = 1)
        h_lines.set_stroke(LIGHT_GREY, 2)
        h_lines.to_edge(DOWN, buff = MED_LARGE_BUFF)
        h_lines.to_edge(LEFT, buff = 0)

        v_lines = VGroup(*[
            Line(UP, DOWN).scale(SPACE_HEIGHT - MED_LARGE_BUFF)
            for x in range(self.n_examples + 1)
        ])
        v_lines.arrange_submobjects(RIGHT, buff = 1.4)
        v_lines.set_stroke(LIGHT_GREY, 2)
        v_lines.to_edge(LEFT, buff = 2)

        # self.add(h_lines, v_lines)
        self.h_lines = h_lines
        self.v_lines = v_lines

    def setup_weights(self):
        weights = VGroup(*map(TexMobject, [
            "w_0", "w_1", "w_2", "\\vdots", "w_{13{,}001}"
        ]))
        for i, weight in enumerate(weights):
            weight.move_to(self.get_grid_position(i, 0))
        weights.to_edge(LEFT, buff = MED_SMALL_BUFF)

        brace = Brace(weights, RIGHT)
        weights_words = brace.get_text("All weights and biases")

        self.add(weights, brace, weights_words)
        self.set_variables_as_attrs(
            weights, brace, weights_words,
            dots = weights[-2]
        )

    def show_two_requesting_changes(self):
        two = self.get_example(get_organized_images()[2][0], 0)
        self.two = two
        self.add(two)

        self.two_changes = VGroup()
        for i in range(3) + [4]:
            weight = self.weights[i]
            bubble, change = self.get_requested_change_bubble(two)
            weight.save_state()
            weight.generate_target()
            weight.target.next_to(two, RIGHT, aligned_edge = DOWN)

            self.play(
                MoveToTarget(weight),
                two.eyes.look_at_anim(weight.target),
                FadeIn(bubble),
                Write(change, run_time = 1),
            )
            if random.random() < 0.5:
                self.play(two.eyes.blink_anim())
            else:
                self.dither()
            if i == 0:
                added_anims = [
                    FadeOut(self.brace),
                    FadeOut(self.weights_words),
                ]
            elif i == 4:
                dots_copy = self.dots.copy()
                added_anims = [
                    dots_copy.move_to,
                    self.get_grid_position(3, 0)
                ]
                self.first_column_dots = dots_copy
            else:
                added_anims = []
            self.play(
                FadeOut(bubble),
                weight.restore,
                two.eyes.look_at_anim(weight.saved_state),
                change.restore,
                change.scale, self.change_scale_val,
                change.move_to, self.get_grid_position(i, 0),
                *added_anims
            )
            self.two_changes.add(change)
        self.dither()

    def show_all_examples_requesting_changes(self):
        training_data, validation_data, test_data = load_data_wrapper()
        data = training_data[:self.n_examples-1]
        examples = VGroup(*[
            self.get_example(t[0], j)
            for t, j in zip(data, it.count(1))
        ])
        h_dots = TexMobject("\\dots")
        h_dots.next_to(examples, RIGHT, MED_LARGE_BUFF)
        more_h_dots = VGroup(*[
            TexMobject("\\dots").move_to(
                self.get_grid_position(i, self.n_examples)
            )
            for i in range(5)
        ])
        more_h_dots.shift(MED_LARGE_BUFF*RIGHT)
        more_h_dots[-2].rotate_in_place(-np.pi/4)
        more_v_dots = VGroup(*[
            self.dots.copy().move_to(
                self.get_grid_position(3, j)
            )
            for j in range(1, self.n_examples)
        ])

        changes = VGroup(*[
            self.get_random_decimal().move_to(
                self.get_grid_position(i, j)
            )
            for i in range(3) + [4]
            for j in range(1, self.n_examples)
        ])
        for change in changes:
            change.scale_in_place(self.change_scale_val)

        self.play(
            LaggedStart(FadeIn, examples),
            LaggedStart(ShowCreation, self.h_lines),
            LaggedStart(ShowCreation, self.v_lines),
            Write(
                h_dots, 
                run_time = 2, 
                rate_func = squish_rate_func(smooth, 0.7, 1)
            )
        )
        self.play(
            Write(changes),
            Write(more_v_dots),
            Write(more_h_dots),
            *[
                example.eyes.look_at_anim(random.choice(changes))
                for example in examples
            ]
        )
        for x in range(2):
            self.play(random.choice(examples).eyes.blink_anim())

        k = self.n_examples - 1
        self.change_rows = VGroup(*[
            VGroup(two_change, *changes[k*i:k*(i+1)])
            for i, two_change in enumerate(self.two_changes)
        ])
        for i in range(3) + [-1]:
            self.change_rows[i].add(more_h_dots[i])

        self.all_eyes = VGroup(*[
            m.eyes for m in [self.two] + list(examples)
        ])

        self.set_variables_as_attrs(
            more_h_dots, more_v_dots,
            h_dots, changes,
        )

    def average_together(self):
        rects = VGroup()
        arrows = VGroup()
        averages = VGroup()
        for row in self.change_rows:
            rect = SurroundingRectangle(row)
            arrow = Arrow(ORIGIN, RIGHT)
            arrow.next_to(rect, RIGHT)
            rect.arrow = arrow
            average = self.get_colored_decimal(3*np.mean([
                m.number for m in row 
                if isinstance(m, DecimalNumber)
            ]))
            average.scale(self.change_scale_val)
            average.next_to(arrow, RIGHT)
            row.target = VGroup(average)

            rects.add(rect)
            arrows.add(arrow)
            averages.add(average)

        words = TextMobject("Average over \\\\ all training data")
        words.scale(0.8)
        words.to_corner(UP+RIGHT)
        arrow_to_averages = Arrow(
            words.get_bottom(), averages.get_top(),
            color = WHITE
        )

        dots = self.dots.copy()
        dots.move_to(VGroup(*averages[-2:]))

        look_at_anims = self.get_look_at_anims

        self.play(Write(words, run_time = 1), *look_at_anims(words))
        self.play(ShowCreation(rects[0]), *look_at_anims(rects[0]))
        self.play(
            ReplacementTransform(rects[0].copy(), arrows[0]),
            rects[0].set_stroke, WHITE, 1,
            ReplacementTransform(
                self.change_rows[0].copy(),
                self.change_rows[0].target
            ),
            *look_at_anims(averages[0])
        )
        self.play(GrowArrow(arrow_to_averages))
        self.play(
            LaggedStart(ShowCreation, VGroup(*rects[1:])),
            *look_at_anims(rects[1])
        )
        self.play(
            LaggedStart(
                ReplacementTransform, VGroup(*rects[1:]).copy(),
                lambda m : (m, m.arrow),
                lag_ratio = 0.7,
            ),
            VGroup(*rects[1:]).set_stroke, WHITE, 1,
            LaggedStart(
                ReplacementTransform, VGroup(*self.change_rows[1:]).copy(),
                lambda m : (m, m.target),
                lag_ratio = 0.7,
            ),
            Write(dots),
            *look_at_anims(averages[1])
        )
        self.blink(3)
        self.dither()

        averages.add(dots)
        self.set_variables_as_attrs(
            rects, arrows, averages,
            arrow_to_averages
        )

    def collapse_into_gradient_vector(self):
        averages = self.averages
        lb, rb = brackets = TexMobject("[]")
        brackets.scale(2)
        brackets.stretch_to_fit_height(1.2*averages.get_height())
        lb.next_to(averages, LEFT, SMALL_BUFF)
        rb.next_to(averages, RIGHT, SMALL_BUFF)
        brackets.set_fill(opacity = 0)

        shift_vect = 2*LEFT

        lhs = TexMobject(
            "-", "\\nabla", "C(",
            "w_1,", "w_2,", "\\dots", "w_{13{,}001}",
            ")", "="
        )
        lhs.next_to(lb, LEFT)
        lhs.shift(shift_vect)
        minus = lhs[0]
        w_terms = lhs.get_parts_by_tex("w_")
        dots_term = lhs.get_part_by_tex("dots")
        eta = TexMobject("\\eta")
        eta.move_to(minus, RIGHT)
        eta.highlight(MAROON_B)

        to_fade = VGroup(*it.chain(
            self.h_lines, self.v_lines,
            self.more_h_dots, self.more_v_dots,
            self.change_rows, 
            self.first_column_dots,
            self.rects,
            self.arrows,
        ))
        arrow = self.arrow_to_averages

        self.play(LaggedStart(FadeOut, to_fade))
        self.play(
            brackets.shift, shift_vect,
            brackets.set_fill, WHITE, 1,
            averages.shift, shift_vect,
            Transform(arrow, Arrow(
                arrow.get_start(),
                arrow.get_end() + shift_vect,
                buff = 0,
                color = arrow.get_color(),
            )),
            FadeIn(VGroup(*lhs[:3])),
            FadeIn(VGroup(*lhs[-2:])),
            *self.get_look_at_anims(lhs)
        )
        self.play(
            ReplacementTransform(self.weights, w_terms),
            ReplacementTransform(self.dots, dots_term),
            *self.get_look_at_anims(w_terms)
        )
        self.blink(2)
        self.play(
            GrowFromCenter(eta),
            minus.shift, MED_SMALL_BUFF*LEFT
        )
        self.dither()

    ####

    def get_example(self, in_vect, index):
        result = MNistMobject(in_vect)
        result.scale_to_fit_height(self.image_height)

        eyes = Eyes(result, height = self.eyes_height)
        result.eyes = eyes
        result.add(eyes)
        result.move_to(self.get_grid_position(0, index))
        result.to_edge(UP, buff = LARGE_BUFF)
        return result

    def get_grid_position(self, i, j):
        x = VGroup(*self.v_lines[j:j+2]).get_center()[0]
        y = VGroup(*self.h_lines[i:i+2]).get_center()[1]
        return x*RIGHT + y*UP

    def get_requested_change_bubble(self, example_mob):
        change = self.get_random_decimal()
        words = TextMobject("Change by")
        change.next_to(words, RIGHT)
        change.save_state()
        content = VGroup(words, change)

        bubble = SpeechBubble(height = 1.5, width = 3)
        bubble.add_content(content)
        group = VGroup(bubble, content)
        group.shift(
            example_mob.get_right() + SMALL_BUFF*RIGHT \
            -bubble.get_corner(DOWN+LEFT)
        )

        return VGroup(bubble, words), change

    def get_random_decimal(self):
        return self.get_colored_decimal(
            0.3*(random.random() - 0.5)
        )

    def get_colored_decimal(self, number):
        result = DecimalNumber(number)
        if result.number > 0:
            plus = TexMobject("+")
            plus.next_to(result, LEFT, SMALL_BUFF)
            result.add_to_back(plus)
            result.highlight(BLUE)
        else:
            result.highlight(RED)
        return result

    def get_look_at_anims(self, mob):
        return [eyes.look_at_anim(mob) for eyes in self.all_eyes]

    def blink(self, n):
        for x in range(n):
            self.play(random.choice(self.all_eyes).blink_anim())

class OpenCloseSGD(Scene):
    def construct(self):
        term = TexMobject(
            "\\langle", "\\text{Stochastic gradient descent}",
            "\\rangle"
        )
        alt_term0 = TexMobject("\\langle /")
        alt_term0.move_to(term[0], RIGHT)

        term.save_state()
        center = term.get_center()
        term[0].move_to(center, RIGHT)
        term[2].move_to(center, LEFT)
        term[1].scale(0.0001).move_to(center)

        self.play(term.restore)
        self.dither(2)
        self.play(Transform(term[0], alt_term0))
        self.dither(2)

class OrganizeDataIntoMiniBatches(Scene):
    CONFIG = {
        "n_rows" : 5,
        "n_cols" : 12,
        "example_height" : 1,
    }
    def construct(self):
        self.add_examples()
        self.shuffle_examples()
        self.divide_into_minibatches()
        self.one_step_per_batch()

    def add_examples(self):
        examples = self.get_examples()
        self.arrange_examples_in_grid(examples)
        for example in examples:
            example.save_state()
        alt_order_examples = VGroup(*examples)
        for mob in examples, alt_order_examples:
            random.shuffle(mob.submobjects)
        self.arrange_examples_in_grid(examples)

        self.play(LaggedStart(
            FadeIn, alt_order_examples,
            lag_ratio = 0.2,
            run_time = 4
        ))
        self.dither()

        self.examples = examples

    def shuffle_examples(self):
        self.play(LaggedStart(
            ApplyMethod, self.examples,
            lambda m : (m.restore,),
            lag_ratio = 0.3,
            run_time = 3,
            path_arc = np.pi/3,
        ))
        self.dither()

    def divide_into_minibatches(self):
        examples = self.examples
        examples.sort_submobjects(lambda p : -p[1])
        rows = Group(*[
            Group(*examples[i*self.n_cols:(i+1)*self.n_cols])
            for i in range(self.n_rows)
        ])

        mini_batches_words = TextMobject("``Mini-batches''")
        mini_batches_words.to_edge(UP)
        mini_batches_words.highlight(YELLOW)

        self.play(
            rows.space_out_submobjects, 1.5,
            rows.to_edge, UP, 1.5,
            Write(mini_batches_words, run_time = 1)
        )

        rects = VGroup(*[
            SurroundingRectangle(
                row, 
                stroke_width = 0,
                fill_color = YELLOW,
                fill_opacity = 0.25,
            )
            for row in rows
        ])
        self.play(LaggedStart(
            FadeIn, rects,
            lag_ratio = 0.7,
            rate_func = there_and_back
        ))
        self.dither()

        self.set_variables_as_attrs(rows, rects, mini_batches_words)

    def one_step_per_batch(self):
        rows = self.rows
        brace = Brace(rows[0], UP, buff = SMALL_BUFF)
        text = brace.get_text(
            "Compute gradient descent step (using backprop)",
            buff = SMALL_BUFF
        )
        def indicate_row(row):
            row.sort_submobjects(lambda p : p[0])
            return LaggedStart(
                ApplyFunction, row,
                lambda row : (
                    lambda m : m.scale_in_place(0.75).highlight(YELLOW),
                    row
                ),
                rate_func = wiggle
            )

        self.play(
            FadeOut(self.mini_batches_words),
            GrowFromCenter(brace),
            Write(text, run_time = 2),
        )
        self.play(indicate_row(rows[0]))
        brace.add(text)
        for last_row, row in zip(rows, rows[1:-1]):
            self.play(
                last_row.shift, UP,
                brace.next_to, row, UP, SMALL_BUFF
            )
            self.play(indicate_row(row))
        self.dither()


    ###

    def get_examples(self):
        n_examples = self.n_rows*self.n_cols
        height = self.example_height
        training_data, validation_data, test_data = load_data_wrapper()
        return Group(*[
            MNistMobject(
                t[0],
                rect_kwargs = {"stroke_width" : 2}
            ).scale_to_fit_height(height)
            for t in training_data[:n_examples]
        ])
        # return Group(*[
        #     Square(
        #         color = BLUE, 
        #         stroke_width = 2
        #     ).scale_to_fit_height(height)
        #     for x in range(n_examples)
        # ])

    def arrange_examples_in_grid(self, examples):
        examples.arrange_submobjects_in_grid(
            n_rows = self.n_rows,
            buff = SMALL_BUFF
        )

class SGDSteps(ExternallyAnimatedScene):
    pass

class GradientDescentSteps(ExternallyAnimatedScene):
    pass

class SwimmingInTerms(TeacherStudentsScene):
    def construct(self):
        terms = VGroup(
            TextMobject("Cost surface"),
            TextMobject("Stochastic gradient descent"),
            TextMobject("Mini-batches"),
            TextMobject("Backpropagation"),
        )
        terms.arrange_submobjects(DOWN)
        terms.to_edge(UP)
        self.play(
            LaggedStart(FadeIn, terms),
            self.get_student_changes(*["horrified"]*3)
        )
        self.dither()
        self.play(
            terms[-1].next_to, self.teacher.get_corner(UP+LEFT), UP,
            FadeOut(VGroup(*terms[:-1])),
            self.teacher.change, "raise_right_hand",
            self.get_student_changes(*["pondering"]*3)
        )
        self.dither()

class BackpropCode(ExternallyAnimatedScene):
    pass

class BackpropCodeAddOn(PiCreatureScene):
    def construct(self):
        words = TextMobject(
            "The code you'd find \\\\ in Nielsen's book"
        )
        words.to_corner(DOWN+LEFT)
        morty = self.pi_creature
        morty.next_to(words, UP)
        self.add(words)
        for mode in ["pondering", "thinking", "happy"]:
            self.play(
                morty.change, "pondering",
                morty.look, UP+LEFT
            )
            self.play(morty.look, DOWN+LEFT)
            self.dither(2)

class CannotFollowCode(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "I...er...can't follow\\\\ that code at all.",
            target_mode = "confused",
            student_index = 1
        )
        self.play(self.students[1].change, "sad")
        self.change_student_modes(
            "angry", "sad", "angry",
            look_at_arg = self.teacher.eyes
        )
        self.play(self.teacher.change, "hesitant")
        self.dither(2)
        self.teacher_says(
            "Let's get to the \\\\ calculus then",
            target_mode = "hooray",
            added_anims = [self.get_student_changes(*3*["plain"])],
            run_time = 1
        )
        self.dither(2)

class EOCWrapper(Scene):
    def construct(self):
        title = TextMobject("Essence of calculus")
        title.to_edge(UP)
        screen = ScreenRectangle(height = 6)
        screen.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(screen))
        self.dither()

class SimplestNetworkExample(Scene):
    def construct(self):
        self.collapse_ordinary_network()
        self.focus_just_on_last_two_layers()
        self.label_neurons()
        self.show_desired_output()
        self.show_cost()
        self.show_activation_formula()
        self.introduce_z()
        self.break_into_computational_graph()
        self.show_preceding_layer_in_computational_graph()
        self.show_number_lines()
        self.ask_about_w_sensitivity()
        self.show_derivative_wrt_w()
        self.show_chain_of_events()
        self.show_chain_rule()
        self.compute_derivatives()
        self.fire_together_wire_together()
        self.show_derivative_wrt_b()
        self.show_derivative_wrt_a()
        self.show_previous_weight_and_bias()

    def collapse_ordinary_network(self):
        pass
        
    def focus_just_on_last_two_layers(self):
        pass
        
    def label_neurons(self):
        pass
        
    def show_desired_output(self):
        pass
        
    def show_cost(self):
        pass
        
    def show_activation_formula(self):
        pass
        
    def introduce_z(self):
        pass
        
    def break_into_computational_graph(self):
        pass
        
    def show_preceding_layer_in_computational_graph(self):
        pass
        
    def show_number_lines(self):
        pass
        
    def ask_about_w_sensitivity(self):
        pass
        
    def show_derivative_wrt_w(self):
        pass
        
    def show_chain_of_events(self):
        pass
        
    def show_chain_rule(self):
        pass
        
    def compute_derivatives(self):
        pass
        
    def fire_together_wire_together(self):
        pass
        
    def show_derivative_wrt_b(self):
        pass
        
    def show_derivative_wrt_a(self):
        pass
        
    def show_previous_weight_and_bias(self):
        pass
        













