from nn.network import *
from nn.part1 import *
from nn.part2 import *

class LayOutPlan(Scene):
    def construct(self):
        title = TextMobject("Plan")
        title.scale(1.5)
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS - 1)
        h_line.next_to(title, DOWN)

        items = BulletedList(
            "Recap",
            "Intuitive walkthrough",
            "Derivatives in \\\\ computational graphs",
        )
        items.to_edge(LEFT, buff = LARGE_BUFF)
        self.add(items)

        rect = ScreenRectangle()
        rect.set_width(FRAME_WIDTH - items.get_width() - 2)
        rect.next_to(items, RIGHT, MED_LARGE_BUFF)

        self.play(
            Write(title),
            ShowCreation(h_line),
            ShowCreation(rect),
            run_time = 2
        )
        for i in range(len(items)):
            self.play(items.fade_all_but, i)
            self.wait(2)

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
        rect.set_color(RED)
        arrow = Vector(DOWN, color = RED)
        arrow.shift(rect.get_bottom())
        cost = DecimalNumber(self.start_cost)
        cost.set_color(RED)
        cost.next_to(arrow, DOWN)

        cost_expression = TexMobject(
            "C(", "w_0, w_1, \\dots, w_{13{,}001}", ")", "="
        )
        for tex in "()":
            cost_expression.set_color_by_tex(tex, RED)
        cost_expression.next_to(cost, DOWN)
        cost_group = VGroup(cost_expression, cost)
        cost_group.arrange(RIGHT)
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
        words.set_color(YELLOW)
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
        self.wait()
        self.play(*list(map(FadeOut, [randy, words, arrow])))

    def circle_magnitudes(self):
        rects = VGroup()
        for decimal in self.grad_vect.decimals:
            rects.add(SurroundingRectangle(VGroup(*decimal[-8:])))
        rects.set_color(WHITE)

        self.play(LaggedStartMap(ShowCreation, rects))
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
        VGroup(edge1, d1).set_color(YELLOW)
        VGroup(edge2, d2).set_color(MAROON_B)
        new_vect_contents = VGroup(
            TexMobject("\\vdots"),
            d1, TexMobject("\\vdots"),
            d2, TexMobject("\\vdots"),
        )
        new_vect_contents.arrange(DOWN)
        new_vect_contents.move_to(vect_contents)

        new_w_terms = TexMobject(
            "\\dots", "w_n", "\\dots", "w_k", "\\dots"
        )
        new_w_terms.move_to(w_terms, DOWN)
        new_w_terms[1].set_color(d1.get_color())
        new_w_terms[3].set_color(d2.get_color())

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
        self.wait()
        self.play(GrowArrow(d2.arrow))
        self.play(ShowCreation(edge2))
        self.wait(2)

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
            term.dot.set_color(term.get_color())
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
                self.wait()
            self.play(*list(map(FadeOut, [
                w.dot, w.brace, w.number_line, w.words
            ])))


    ######

    def move_grad_terms_into_position(self, grad_terms, *added_anims):
        cost_expression = self.cost_expression
        w_terms = self.cost_expression[1]
        points = VGroup(*[
            VectorizedPoint()
            for term in grad_terms
        ])
        points.arrange(RIGHT)
        points.replace(w_terms, dim_to_match = 0)

        grad_terms.generate_target()
        grad_terms.target[len(grad_terms)/2].rotate(np.pi/2)
        grad_terms.target.arrange(RIGHT)
        grad_terms.target.set_width(cost_expression.get_width())
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
                lag_ratio = 0.5,
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
            LaggedStartMap(
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
            equation.set_color_by_tex_to_color_map({
                "\\delta" : YELLOW,
                "C" : RED,
                "b" : MAROON_B,
                "w" : BLUE,
                "z" : TEAL,
            })
            equation.set_color_by_tex("nabla", WHITE)
        equations.arrange(
            DOWN, buff = MED_LARGE_BUFF, aligned_edge = LEFT
        )

        circle = Circle(radius = 3*FRAME_X_RADIUS)
        circle.set_fill(WHITE, 0)
        circle.set_stroke(WHITE, 0)

        self.play(
            Write(equations),
            morty.change, "confused", equations
        )
        self.wait()
        self.play(morty.change, "pleading")
        self.wait(2)

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
            LaggedStartMap(
                MoveToTarget, movers,
                run_time = 2,
            ),
            morty.change, "pondering",
        )
        self.wait()

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
        cost_words.set_color(RED)

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
            self.wait(self.time_per_example)

        #Wiggle all edges
        edges = VGroup(*it.chain(*self.network_mob.edge_groups))
        reversed_edges = VGroup(*reversed(edges))
        self.play(LaggedStartMap(
            ApplyFunction, edges,
            lambda edge : (
                lambda m : m.rotate_in_place(np.pi/12).set_color(YELLOW),
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
        words.set_color(YELLOW)
        words.scale(0.8)
        words.to_corner(UP+LEFT)

        for x in range(self.n_adjustments):
            if x < 2:
                self.play(FadeIn(words[x]))
            for train_in, train_out in training_data[:n_examples_per_adjustment]:
                self.show_one_example(train_in, train_out)
                self.wait(self.time_per_example)
            self.play(LaggedStartMap(
                ApplyMethod, reversed_edges,
                lambda m : (m.rotate_in_place, np.pi),
                run_time = 1,
                lag_ratio = 0.2,
            ))
            if x >= 2:
                self.wait()

    ####

    def show_one_example(self, train_in, train_out):
        if hasattr(self, "curr_image"):
            self.remove(self.curr_image)
        image = MNistMobject(train_in)
        image.set_height(self.image_height)
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

class FocusOnOneExample(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("Focus on just \\\\ one example")
        self.wait(2)

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
        self.wait()

    def single_example_influencing_weights(self):
        two = self.curr_image
        two.save_state()

        edge_groups = self.network_mob.edge_groups
        def adjust_edge_group_anim(edge_group):
            return LaggedStartMap(
                ApplyFunction, edge_group,
                lambda edge : (
                    lambda m : m.rotate_in_place(np.pi/12).set_color(YELLOW),
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
        self.wait()

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
            norm = get_norm(vect)
            unit_vect = vect / norm

            edge.target.put_start_and_end_on(
                c1 + unit_vect*r1,
                c2 - unit_vect*r2
            )

        self.play(
            FadeOut(to_fade),
            *list(map(MoveToTarget, movers))
        )
        self.show_decimals(neurons)
        self.cannot_directly_affect_activations()
        self.show_desired_activation_nudges(neurons, output_labels, alt_output_labels)
        self.focus_on_one_neuron(movers)

    def show_decimals(self, neurons):
        decimals = VGroup()
        for neuron in neurons:
            activation = neuron.get_fill_opacity()
            decimal = DecimalNumber(activation, num_decimal_places = 1)
            decimal.set_width(0.7*neuron.get_width())
            decimal.move_to(neuron)
            if activation > 0.8:
                decimal.set_color(BLACK)
            decimals.add(decimal)

        self.play(Write(decimals, run_time = 2))
        self.wait()
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
            LaggedStartMap(
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
                arrow.set_color(BLUE)
                arrow.rotate_in_place(np.pi)
            arrows.add(arrow)

            rect = SurroundingRectangle(VGroup(neuron, label))
            if i == 2:
                rect.set_color(BLUE)
            else:
                rect.set_color(RED)
            rects.add(rect)

        self.play(
            output_labels.shift, SMALL_BUFF*RIGHT,
            LaggedStartMap(GrowArrow, arrows, run_time = 1)
        )
        self.wait()

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
                num_decimal_places = 1
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
        self.wait()
        self.remove(two_rect)
        self.play(ReplacementTransform(two_rect.copy(), non_two_rects))
        self.wait()
        self.play(LaggedStartMap(FadeOut, non_two_rects, run_time = 1))
        self.play(LaggedStartMap(
            ApplyFunction, arrows,
            lambda arrow : (
                lambda m : m.scale_in_place(0.5).set_color(YELLOW),
                arrow,
            ),
            rate_func = wiggle
        ))
        self.play(ShowCreation(two_rect))
        self.wait()
        self.play(ReplacementTransform(two_rect, eight_rect))
        self.wait()
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
        self.wait()
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

        w_terms.set_color(BLUE)
        b.set_color(MAROON_B)
        sigma.set_color(YELLOW)

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
        self.wait()
        self.play(ReplacementTransform(
            prev_neurons.copy(), a_terms,
            path_arc = np.pi/2
        ))
        self.wait()
        self.play(
            Write(plus_terms[-1]),
            Write(b)
        )
        self.wait()
        self.play(sigma.restore)
        self.wait()
        for mob in b, w_terms, a_terms:
            self.play(
                mob.shift, MED_SMALL_BUFF*DOWN,
                rate_func = there_and_back,
                lag_ratio = 0.5,
                run_time = 1.5
            )
        self.wait()

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
            words.set_color_by_tex_to_color_map({
                "b" : b.get_color(),
                "w_" : w_terms.get_color(),
                "a_" : a_terms.get_color(),
            })
        increase_words.arrange(
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
            self.wait()

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
        dim_neurons = VGroup()
        edges_to_bright_neurons = VGroup()
        for i in sorted_indices[:5]:
            dim_neurons.add(prev_neurons[i])
        for i in sorted_indices[-4:]:
            bright_neurons.add(prev_neurons[i])
            edges_to_bright_neurons.add(edges[i])
        bright_edges = edges_to_bright_neurons.copy()
        bright_edges.set_stroke(YELLOW, 4)

        added_words = TextMobject("in proportion to $a_i$")
        added_words.next_to(
            increase_words[1], DOWN, 
            1.5*SMALL_BUFF, LEFT
        )
        added_words.set_color(YELLOW)

        terms_rect = SurroundingRectangle(
            VGroup(w_terms[0], a_terms[0]),
            color = WHITE
        )

        self.play(LaggedStartMap(
            ApplyFunction, edges,
            lambda edge : (
                lambda m : m.rotate_in_place(np.pi/12).set_stroke(YELLOW),
                edge
            ),
            rate_func = wiggle
        ))
        self.wait()
        self.play(
            ShowCreation(bright_edges),
            ShowCreation(bright_neurons)
        )
        self.play(LaggedStartMap(
            ApplyMethod, bright_neurons,
            lambda m : (m.shift, MED_LARGE_BUFF*LEFT),
            rate_func = there_and_back
        ))
        self.wait()
        self.play(
            ReplacementTransform(bright_edges[0].copy(), w_terms[0]),
            ReplacementTransform(bright_neurons[0].copy(), a_terms[0]),
            ShowCreation(terms_rect)
        )
        self.wait()
        for x in range(2):
            self.play(LaggedStartMap(ShowCreationThenDestruction, bright_edges))
        self.play(LaggedStartMap(ShowCreation, bright_edges))
        self.play(LaggedStartMap(
            ApplyMethod, dim_neurons,
            lambda m : (m.shift, MED_LARGE_BUFF*LEFT),
            rate_func = there_and_back
        ))
        self.play(FadeOut(terms_rect))
        self.wait()
        self.play(
            self.curr_image.shift, MED_LARGE_BUFF*RIGHT,
            rate_func = wiggle
        )
        self.wait()
        self.play(Write(added_words))
        self.wait()

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
            return LaggedStartMap(
                ShowCreationThenDestruction, bright_edges,
                lag_ratio = 0.7
            )
        neuron_arrows = VGroup(*[
            Vector(MED_LARGE_BUFF*RIGHT).next_to(n, LEFT)
            for n in bright_neurons
        ])
        two_neuron_arrow = Vector(MED_LARGE_BUFF*DOWN)
        two_neuron_arrow.next_to(two_neuron, UP)
        VGroup(neuron_arrows, two_neuron_arrow).set_color(YELLOW)

        neuron_rects = VGroup(*list(map(
            SurroundingRectangle, bright_neurons
        )))
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
            LaggedStartMap(GrowArrow, neuron_arrows),
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
                num_decimal_places = 1,
            ),
            UpdateFromFunc(
                two_decimal,
                lambda m : m.set_color(WHITE if m.number < 0.8 else BLACK),
            ),
            LaggedStartMap(ShowCreation, bright_edges),
            run_time = 2,
        )
        self.wait()
        self.play(
            LaggedStartMap(ShowCreation, neuron_rects),
            Write(seeing_words, run_time = 2),
            morty.change, "thinking", seeing_words
        )
        self.wait()
        self.play(
            ShowCreation(two_neuron_rect),
            Write(thinking_words, run_time = 2),
            morty.look_at, thinking_words
        )
        self.wait()
        self.play(LaggedStartMap(FadeOut, VGroup(
            neuron_rects, two_neuron_rect,
            seeing_words, thinking_words,
            words, morty,
            neuron_arrows, two_neuron_arrow,
            bright_edges, 
        )))
        self.play(
            ApplyMethod(two_neuron.set_fill, WHITE, two_activation),
            ChangingDecimal(
                two_decimal,
                lambda a : interpolate(1, two_activation, a),
                num_decimal_places = 1,
            ),
            UpdateFromFunc(
                two_decimal,
                lambda m : m.set_color(WHITE if m.number < 0.8 else BLACK),
            ),
        )

    def show_desired_increase_to_previous_neurons(self):
        increase_words = self.increase_words
        two_neuron = self.two_neuron
        two_decimal = self.two_decimal
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
        for s_edges in positive_edges, negative_edges:
            s_edges.alt_position = VGroup(*[
                Line(LEFT, RIGHT, color = s_edge.get_color())
                for s_edge in s_edges
            ])
            s_edges.alt_position.arrange(DOWN, MED_SMALL_BUFF)
            s_edges.alt_position.to_corner(DOWN+RIGHT, LARGE_BUFF)

        added_words = TextMobject("in proportion to $w_i$")
        added_words.set_color(self.w_terms.get_color())
        added_words.next_to(
            increase_words[-1], DOWN,
            SMALL_BUFF, aligned_edge = LEFT
        )

        self.play(LaggedStartMap(
            ApplyFunction, prev_neurons,
            lambda neuron : (
                lambda m : m.scale_in_place(0.5).set_color(YELLOW),
                neuron
            ),
            rate_func = wiggle
        ))
        self.wait()
        for positive in [True, False]:
            if positive:
                arrows = positive_arrows
                s_edges = positive_edges
                neurons = positive_neurons
                color = self.positive_edge_color
            else:
                arrows = negative_arrows
                s_edges = negative_edges
                neurons = negative_neurons
                color = self.negative_edge_color
            s_edges.save_state()
            self.play(Transform(s_edges, s_edges.alt_position))
            self.wait(0.5)
            self.play(s_edges.restore)
            self.play(
                LaggedStartMap(GrowArrow, arrows),
                neurons.set_stroke, color
            )
            self.play(ApplyMethod(
                neurons.set_fill, color, 1,
                rate_func = there_and_back,
            ))
        self.wait()
        self.play(
            two_neuron.set_fill, None, 0.8,
            ChangingDecimal(
                two_decimal,
                lambda a : two_neuron.get_fill_opacity()
            ),
            run_time = 3,
            rate_func = there_and_back
        )
        self.wait()
        self.play(*[
            ApplyMethod(
                edge.set_stroke, None, 3*edge.get_stroke_width(),
                rate_func = there_and_back, 
                run_time = 2
            )
            for edge in edges
        ])
        self.wait()
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

        words1 = TextMobject("No direct influence")
        words1.next_to(rect, UP)
        words2 = TextMobject("Just keeping track")
        words2.move_to(words1)

        edges = self.network_mob.edge_groups[-2]

        self.play(ShowCreation(rect))
        self.play(Write(words1))
        self.play(LaggedStartMap(
            Indicate, prev_neurons,
            rate_func = wiggle
        ))
        self.wait()
        self.play(LaggedStartMap(
            ShowCreationThenDestruction, edges
        ))
        self.play(Transform(words1, words2))
        self.wait()
        self.play(FadeOut(VGroup(words1, rect)))

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
        quads = list(zip(neurons, self.decimals, self.arrows, output_labels))

        self.revert_to_original_skipping_status()
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
        for neuron, decimal, arrow, label in quads[:2] + quads[2:5]:
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
                LaggedStartMap(ShowCreation, neuron.edges_in),
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
            LaggedStartMap(
                FadeIn, VGroup(*it.starmap(VGroup, quads[5:])),
            ),
            LaggedStartMap(
                FadeIn, VGroup(*[n.edges_in for n in neurons[5:]])
            ),
            Write(all_dots_plus),
            run_time = 3,
        )
        self.wait(2)

        ##
        words = TextMobject("Propagate backwards")
        words.to_edge(UP)
        words.set_color(BLUE)
        target_arrows = prev_neuron_arrows.copy()
        target_arrows.next_to(prev_neurons, RIGHT, SMALL_BUFF)
        rect = SurroundingRectangle(VGroup(
            self.network_mob.layers[-1],
            self.network_mob.output_labels
        ))
        rect.set_fill(BLACK, 1)
        rect.set_stroke(BLACK, 0)
        self.play(Write(words))
        self.wait()
        self.play(
            FadeOut(self.network_mob.edge_groups[-1]),
            FadeIn(rect),
            ReplacementTransform(arrows_to_fade, VGroup(target_arrows)),
        )
        self.prev_neuron_arrows = target_arrows

    def show_recursion(self):
        network_mob = self.network_mob
        words_to_fade = VGroup(
            self.increase_words,
            self.in_proportion_to_w,
            self.in_proportion_to_a,
        )
        edges = network_mob.edge_groups[1]
        neurons = network_mob.layers[2].neurons
        prev_neurons = network_mob.layers[1].neurons
        for neuron in neurons:
            neuron.edges_in.save_state()

        self.play(
            FadeOut(words_to_fade),
            FadeIn(prev_neurons),
            LaggedStartMap(ShowCreation, edges),
        )
        self.wait()
        for neuron, arrow in zip(neurons, self.prev_neuron_arrows):
            edge_copies = neuron.edges_in.copy()
            for edge in edge_copies:
                edge.set_stroke(arrow.get_color(), 2)
                edge.rotate_in_place(np.pi)
            self.play(
                edges.set_stroke, None, 0.15,
                neuron.edges_in.restore,
            )
            self.play(ShowCreationThenDestruction(edge_copies))
            self.remove(edge_copies)


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

class WriteHebbian(Scene):
    def construct(self):
        words = TextMobject("Hebbian theory")
        words.set_width(FRAME_WIDTH - 1)
        words.to_edge(UP)
        self.play(Write(words))
        self.wait()

class NotANeuroScientist(TeacherStudentsScene):
    def construct(self):
        quote = TextMobject("``Neurons that fire together wire together''")
        quote.to_edge(UP)
        self.add(quote)
        asterisks = TextMobject("***")
        asterisks.next_to(quote.get_corner(UP+RIGHT), RIGHT, SMALL_BUFF)
        asterisks.set_color(BLUE)

        brain = SVGMobject(file_name = "brain")
        brain.set_height(1.5)
        self.add(brain)
        double_arrow = DoubleArrow(LEFT, RIGHT)
        double_arrow.next_to(brain, RIGHT)
        q_marks = TextMobject("???")
        q_marks.next_to(double_arrow, UP)

        network = NetworkMobject(Network(sizes = [6, 4, 4, 5]))
        network.set_height(1.5)
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
        no_claim_words.set_color(YELLOW)

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
        self.wait()
        self.play(brain_anim)
        self.play(FocusOn(asterisks))
        self.play(Write(asterisks, run_time = 1))
        for x in range(2):
            self.play(brain_anim)
            self.wait()

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
            Line(LEFT, RIGHT).scale(0.85*FRAME_X_RADIUS)
            for x in range(6)
        ])
        h_lines.arrange(DOWN, buff = 1)
        h_lines.set_stroke(LIGHT_GREY, 2)
        h_lines.to_edge(DOWN, buff = MED_LARGE_BUFF)
        h_lines.to_edge(LEFT, buff = 0)

        v_lines = VGroup(*[
            Line(UP, DOWN).scale(FRAME_Y_RADIUS - MED_LARGE_BUFF)
            for x in range(self.n_examples + 1)
        ])
        v_lines.arrange(RIGHT, buff = 1.4)
        v_lines.set_stroke(LIGHT_GREY, 2)
        v_lines.to_edge(LEFT, buff = 2)

        # self.add(h_lines, v_lines)
        self.h_lines = h_lines
        self.v_lines = v_lines

    def setup_weights(self):
        weights = VGroup(*list(map(TexMobject, [
            "w_0", "w_1", "w_2", "\\vdots", "w_{13{,}001}"
        ])))
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
        for i in list(range(3)) + [4]:
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
                self.wait()
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
        self.wait()

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
            for i in list(range(3)) + [4]
            for j in range(1, self.n_examples)
        ])
        for change in changes:
            change.scale_in_place(self.change_scale_val)

        self.play(
            LaggedStartMap(FadeIn, examples),
            LaggedStartMap(ShowCreation, self.h_lines),
            LaggedStartMap(ShowCreation, self.v_lines),
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
        for i in list(range(3)) + [-1]:
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
            LaggedStartMap(ShowCreation, VGroup(*rects[1:])),
            *look_at_anims(rects[1])
        )
        self.play(
            LaggedStartMap(
                ReplacementTransform, VGroup(*rects[1:]).copy(),
                lambda m : (m, m.arrow),
                lag_ratio = 0.7,
            ),
            VGroup(*rects[1:]).set_stroke, WHITE, 1,
            LaggedStartMap(
                ReplacementTransform, VGroup(*self.change_rows[1:]).copy(),
                lambda m : (m, m.target),
                lag_ratio = 0.7,
            ),
            Write(dots),
            *look_at_anims(averages[1])
        )
        self.blink(3)
        self.wait()

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
        eta.set_color(MAROON_B)

        to_fade = VGroup(*it.chain(
            self.h_lines, self.v_lines,
            self.more_h_dots, self.more_v_dots,
            self.change_rows, 
            self.first_column_dots,
            self.rects,
            self.arrows,
        ))
        arrow = self.arrow_to_averages

        self.play(LaggedStartMap(FadeOut, to_fade))
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
        self.wait()

    ####

    def get_example(self, in_vect, index):
        result = MNistMobject(in_vect)
        result.set_height(self.image_height)

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
            result.set_color(BLUE)
        else:
            result.set_color(RED)
        return result

    def get_look_at_anims(self, mob):
        return [eyes.look_at_anim(mob) for eyes in self.all_eyes]

    def blink(self, n):
        for x in range(n):
            self.play(random.choice(self.all_eyes).blink_anim())

class WatchPreviousScene(TeacherStudentsScene):
    def construct(self):
        screen = ScreenRectangle(height = 4.5)
        screen.to_corner(UP+LEFT)

        self.play(
            self.teacher.change, "raise_right_hand", screen,
            self.get_student_changes(
                *["thinking"]*3,
                look_at_arg = screen
            ),
            ShowCreation(screen)
        )
        self.wait(10)

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
        self.wait(2)
        self.play(Transform(term[0], alt_term0))
        self.wait(2)

class OrganizeDataIntoMiniBatches(Scene):
    CONFIG = {
        "n_rows" : 5,
        "n_cols" : 12,
        "example_height" : 1,
        "random_seed" : 0,
    }
    def construct(self):
        self.seed_random_libraries()
        self.add_examples()
        self.shuffle_examples()
        self.divide_into_minibatches()
        self.one_step_per_batch()

    def seed_random_libraries(self):
        random.seed(self.random_seed)
        np.random.seed(self.random_seed)

    def add_examples(self):
        examples = self.get_examples()
        self.arrange_examples_in_grid(examples)
        for example in examples:
            example.save_state()
        alt_order_examples = VGroup(*examples)
        for mob in examples, alt_order_examples:
            random.shuffle(mob.submobjects)
        self.arrange_examples_in_grid(examples)

        self.play(LaggedStartMap(
            FadeIn, alt_order_examples,
            lag_ratio = 0.2,
            run_time = 4
        ))
        self.wait()

        self.examples = examples

    def shuffle_examples(self):
        self.play(LaggedStartMap(
            ApplyMethod, self.examples,
            lambda m : (m.restore,),
            lag_ratio = 0.3,
            run_time = 3,
            path_arc = np.pi/3,
        ))
        self.wait()

    def divide_into_minibatches(self):
        examples = self.examples
        examples.sort(lambda p : -p[1])
        rows = Group(*[
            Group(*examples[i*self.n_cols:(i+1)*self.n_cols])
            for i in range(self.n_rows)
        ])

        mini_batches_words = TextMobject("``Mini-batches''")
        mini_batches_words.to_edge(UP)
        mini_batches_words.set_color(YELLOW)

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
        self.play(LaggedStartMap(
            FadeIn, rects,
            lag_ratio = 0.7,
            rate_func = there_and_back
        ))
        self.wait()

        self.set_variables_as_attrs(rows, rects, mini_batches_words)

    def one_step_per_batch(self):
        rows = self.rows
        brace = Brace(rows[0], UP, buff = SMALL_BUFF)
        text = brace.get_text(
            "Compute gradient descent step (using backprop)",
            buff = SMALL_BUFF
        )
        def indicate_row(row):
            row.sort(lambda p : p[0])
            return LaggedStartMap(
                ApplyFunction, row,
                lambda row : (
                    lambda m : m.scale_in_place(0.75).set_color(YELLOW),
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
        self.wait()


    ###

    def get_examples(self):
        n_examples = self.n_rows*self.n_cols
        height = self.example_height
        training_data, validation_data, test_data = load_data_wrapper()
        return Group(*[
            MNistMobject(
                t[0],
                rect_kwargs = {"stroke_width" : 2}
            ).set_height(height)
            for t in training_data[:n_examples]
        ])
        # return Group(*[
        #     Square(
        #         color = BLUE, 
        #         stroke_width = 2
        #     ).set_height(height)
        #     for x in range(n_examples)
        # ])

    def arrange_examples_in_grid(self, examples):
        examples.arrange_in_grid(
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
        terms.arrange(DOWN)
        terms.to_edge(UP)
        self.play(
            LaggedStartMap(FadeIn, terms),
            self.get_student_changes(*["horrified"]*3)
        )
        self.wait()
        self.play(
            terms[-1].next_to, self.teacher.get_corner(UP+LEFT), UP,
            FadeOut(VGroup(*terms[:-1])),
            self.teacher.change, "raise_right_hand",
            self.get_student_changes(*["pondering"]*3)
        )
        self.wait()

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
            self.play(morty.look, LEFT)
            self.wait(2)

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
        self.wait(2)
        self.teacher_says(
            "Let's get to the \\\\ calculus then",
            target_mode = "hooray",
            added_anims = [self.get_student_changes(*3*["plain"])],
            run_time = 1
        )
        self.wait(2)

class EOCWrapper(Scene):
    def construct(self):
        title = TextMobject("Essence of calculus")
        title.to_edge(UP)
        screen = ScreenRectangle(height = 6)
        screen.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(screen))
        self.wait()

class SimplestNetworkExample(PreviewLearning):
    CONFIG = {
        "random_seed" : 6,
        "z_color" : GREEN,
        "cost_color" : RED,
        "desired_output_color" : YELLOW,
        "derivative_scale_val" : 0.85,
    }
    def construct(self):
        self.seed_random_libraries()
        self.collapse_ordinary_network()
        self.show_weights_and_biases()
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
        self.name_chain_rule()
        self.indicate_everything_on_screen()
        self.prepare_for_derivatives()
        self.compute_derivatives()
        self.get_lost_in_formulas()
        self.fire_together_wire_together()
        self.organize_chain_rule_rhs()
        self.show_average_derivative()
        self.show_gradient()
        self.transition_to_derivative_wrt_b()
        self.show_derivative_wrt_b()
        self.show_derivative_wrt_a()
        self.show_previous_weight_and_bias()
        self.animate_long_path()

    def seed_random_libraries(self):
        np.random.seed(self.random_seed)
        random.seed(self.random_seed)

    def collapse_ordinary_network(self):
        network_mob = self.network_mob
        config = dict(self.network_mob_config)
        config.pop("include_output_labels")
        config.update({
            "edge_stroke_width" : 3,
            "edge_propogation_color" : YELLOW,
            "edge_propogation_time" : 1,
            "neuron_radius" : 0.3,
        })
        simple_network = Network(sizes = [1, 1, 1, 1])
        simple_network_mob = NetworkMobject(simple_network, **config)
        self.color_network_edges()
        s_edges = simple_network_mob.edge_groups
        for edge, weight_matrix in zip(s_edges, simple_network.weights):
            weight = weight_matrix[0][0]
            width = 2*abs(weight)
            color = BLUE if weight > 0 else RED
            edge.set_stroke(color, width)

        def edge_collapse_anims(edges, left_attachment_target):
            return [
                ApplyMethod(
                    e.put_start_and_end_on_with_projection,
                    left_attachment_target.get_right(), 
                    e.get_end()
                )
                for e in edges
            ]

        neuron = simple_network_mob.layers[0].neurons[0]
        self.play(
            ReplacementTransform(network_mob.layers[0], neuron),
            *edge_collapse_anims(network_mob.edge_groups[0], neuron)
        )
        for i, layer in enumerate(network_mob.layers[1:]):
            neuron = simple_network_mob.layers[i+1].neurons[0]
            prev_edges = network_mob.edge_groups[i]
            prev_edge_target = simple_network_mob.edge_groups[i]
            if i+1 < len(network_mob.edge_groups):
                edges = network_mob.edge_groups[i+1]
                added_anims = edge_collapse_anims(edges, neuron)
            else:
                added_anims = [FadeOut(network_mob.output_labels)]
            self.play(
                ReplacementTransform(layer, neuron),
                ReplacementTransform(prev_edges, prev_edge_target),
                *added_anims
            )
        self.remove(network_mob)
        self.add(simple_network_mob)
        self.network_mob = simple_network_mob
        self.network = self.network_mob.neural_network
        self.feed_forward(np.array([0.5]))
        self.wait()

    def show_weights_and_biases(self):
        network_mob = self.network_mob
        edges = VGroup(*[eg[0] for eg in network_mob.edge_groups])
        neurons = VGroup(*[
            layer.neurons[0] 
            for layer in network_mob.layers[1:]
        ])
        expression = TexMobject(
            "C", "(", 
            "w_1", ",", "b_1", ",",
            "w_2", ",", "b_2", ",",
            "w_3", ",", "b_3",
            ")"
        )
        expression.shift(2*UP)
        expression.set_color_by_tex("C", RED)
        w_terms = expression.get_parts_by_tex("w_")
        for w, edge in zip(w_terms, edges):
            w.set_color(edge.get_color())
        b_terms = expression.get_parts_by_tex("b_")
        variables = VGroup(*it.chain(w_terms, b_terms))
        other_terms = VGroup(*[m for m in expression if m not in variables])
        random.shuffle(variables.submobjects)

        self.play(ReplacementTransform(edges.copy(), w_terms))
        self.wait()
        self.play(ReplacementTransform(neurons.copy(), b_terms))
        self.wait()
        self.play(Write(other_terms))
        for x in range(2):
            self.play(LaggedStartMap(
                Indicate, variables,
                rate_func = wiggle,
                run_time = 4,
            ))
        self.wait()
        self.play(
            FadeOut(other_terms),
            ReplacementTransform(w_terms, edges),
            ReplacementTransform(b_terms, neurons),
        )
        self.remove(expression)

    def focus_just_on_last_two_layers(self):
        to_fade = VGroup(*it.chain(*list(zip(
            self.network_mob.layers[:2],
            self.network_mob.edge_groups[:2],
        ))))
        for mob in to_fade:
            mob.save_state()
        self.play(LaggedStartMap(
            ApplyMethod, to_fade,
            lambda m : (m.fade, 0.9)
        ))
        self.wait()

        self.prev_layers = to_fade

    def label_neurons(self):
        neurons = VGroup(*[
            self.network_mob.layers[i].neurons[0]
            for i in (-1, -2)
        ])
        decimals = VGroup()
        a_labels = VGroup()
        a_label_arrows = VGroup()
        superscripts = ["L", "L-1"]
        superscript_rects = VGroup()
        for neuron, superscript in zip(neurons, superscripts):
            decimal = self.get_neuron_activation_decimal(neuron)
            label = TexMobject("a^{(%s)}"%superscript)
            label.next_to(neuron, DOWN, buff = LARGE_BUFF)
            superscript_rect = SurroundingRectangle(VGroup(*label[1:]))
            arrow = Arrow(
                label[0].get_top(),
                neuron.get_bottom(),
                buff = SMALL_BUFF,
                color = WHITE
            )

            decimal.save_state()
            decimal.set_fill(opacity = 0)
            decimal.move_to(label)

            decimals.add(decimal)
            a_labels.add(label)
            a_label_arrows.add(arrow)
            superscript_rects.add(superscript_rect)

            self.play(
                Write(label, run_time = 1),
                GrowArrow(arrow),
            )
            self.play(decimal.restore)
            opacity = neuron.get_fill_opacity()
            self.play(
                neuron.set_fill, None, 0,
                ChangingDecimal(
                    decimal, 
                    lambda a : interpolate(opacity, 0.01, a)
                ),
                UpdateFromFunc(
                    decimal,
                    lambda d : d.set_fill(WHITE if d.number < 0.8 else BLACK)
                ),
                run_time = 2,
                rate_func = there_and_back,
            )
            self.wait()

        not_exponents = TextMobject("Not exponents")
        not_exponents.next_to(superscript_rects, DOWN, MED_LARGE_BUFF)
        not_exponents.set_color(YELLOW)

        self.play(
            LaggedStartMap(
                ShowCreation, superscript_rects,
                lag_ratio = 0.8, run_time = 1.5
            ),
            Write(not_exponents, run_time = 2)
        )
        self.wait()
        self.play(*list(map(FadeOut, [not_exponents, superscript_rects])))

        self.set_variables_as_attrs(
            a_labels, a_label_arrows, decimals,
            last_neurons = neurons
        )

    def show_desired_output(self):
        neuron = self.network_mob.layers[-1].neurons[0].copy()
        neuron.shift(2*RIGHT)
        neuron.set_fill(opacity = 1)
        decimal = self.get_neuron_activation_decimal(neuron)

        rect = SurroundingRectangle(neuron)
        words = TextMobject("Desired \\\\ output")
        words.next_to(rect, UP)

        y_label = TexMobject("y")
        y_label.next_to(neuron, DOWN, LARGE_BUFF)
        y_label.align_to(self.a_labels, DOWN)
        y_label_arrow = Arrow(
            y_label, neuron, 
            color = WHITE,
            buff = SMALL_BUFF
        )
        VGroup(words, rect, y_label).set_color(self.desired_output_color)

        self.play(*list(map(FadeIn, [neuron, decimal])))
        self.play(
            ShowCreation(rect),
            Write(words, run_time = 1)
        )
        self.wait()
        self.play(
            Write(y_label, run_time = 1),
            GrowArrow(y_label_arrow)
        )
        self.wait()

        self.set_variables_as_attrs(
            y_label, y_label_arrow,
            desired_output_neuron = neuron,
            desired_output_decimal = decimal,
            desired_output_rect = rect,
            desired_output_words = words,
        )

    def show_cost(self):
        pre_a = self.a_labels[0].copy()
        pre_y = self.y_label.copy()

        cost_equation = TexMobject(
            "C_0", "(", "\\dots", ")", "=",
            "(", "a^{(L)}", "-", "y", ")", "^2"
        )
        cost_equation.to_corner(UP+RIGHT)
        C0, a, y = [
            cost_equation.get_part_by_tex(tex)
            for tex in ("C_0", "a^{(L)}", "y")
        ]
        y.set_color(YELLOW)

        cost_word = TextMobject("Cost")
        cost_word.next_to(C0[0], LEFT, LARGE_BUFF)
        cost_arrow = Arrow(
            cost_word, C0,
            buff = SMALL_BUFF
        )
        VGroup(C0, cost_word, cost_arrow).set_color(self.cost_color)

        expression = TexMobject(
            "\\text{For example: }"
            "(", "0.00", "-", "0.00", ")", "^2"
        )
        numbers = expression.get_parts_by_tex("0.00")
        non_numbers = VGroup(*[m for m in expression if m not in numbers])
        expression.next_to(cost_equation, DOWN, aligned_edge = RIGHT)
        decimals = VGroup(
            self.decimals[0],
            self.desired_output_decimal
        ).copy()
        decimals.generate_target()
        for d, n in zip(decimals.target, numbers):
            d.replace(n, dim_to_match = 1)
            d.set_color(n.get_color())

        self.play(
            ReplacementTransform(pre_a, a),
            ReplacementTransform(pre_y, y),
        )
        self.play(LaggedStartMap(
            FadeIn, VGroup(*[m for m in cost_equation if m not in [a, y]])
        ))
        self.play(
            MoveToTarget(decimals),
            FadeIn(non_numbers)
        )
        self.wait()
        self.play(
            Write(cost_word, run_time = 1),
            GrowArrow(cost_arrow)
        )
        self.play(C0.shift, MED_SMALL_BUFF*UP, rate_func = wiggle)
        self.wait()
        self.play(*list(map(FadeOut, [decimals, non_numbers])))

        self.set_variables_as_attrs(
            cost_equation, cost_word, cost_arrow
        )

    def show_activation_formula(self):
        neuron = self.network_mob.layers[-1].neurons[0]
        edge = self.network_mob.edge_groups[-1][0]
        pre_aL, pre_aLm1 = self.a_labels.copy()

        formula = TexMobject(
            "a^{(L)}", "=", "\\sigma", "(",
            "w^{(L)}", "a^{(L-1)}", "+", "b^{(L)}", ")"
        )
        formula.next_to(neuron, UP, MED_LARGE_BUFF, RIGHT)
        aL, equals, sigma, lp, wL, aLm1, plus, bL, rp = formula
        wL.set_color(edge.get_color())
        weight_label = wL.copy()
        bL.set_color(MAROON_B)
        bias_label = bL.copy()
        sigma_group = VGroup(sigma, lp, rp)
        sigma_group.save_state()
        sigma_group.set_fill(opacity = 0)
        sigma_group.shift(DOWN)

        self.play(
            ReplacementTransform(pre_aL, aL),
            Write(equals)
        )
        self.play(ReplacementTransform(
            edge.copy(), wL
        ))
        self.wait()
        self.play(ReplacementTransform(pre_aLm1, aLm1))
        self.wait()
        self.play(Write(VGroup(plus, bL), run_time = 1))
        self.wait()
        self.play(sigma_group.restore)
        self.wait()

        weighted_sum_terms = VGroup(wL, aLm1, plus, bL)
        self.set_variables_as_attrs(
            formula, weighted_sum_terms
        )

    def introduce_z(self):
        terms = self.weighted_sum_terms
        terms.generate_target()
        terms.target.next_to(
            self.formula, UP, 
            buff = MED_LARGE_BUFF,
            aligned_edge = RIGHT
        )
        terms.target.shift(MED_LARGE_BUFF*RIGHT)
        equals = TexMobject("=")
        equals.next_to(terms.target[0][0], LEFT)

        z_label = TexMobject("z^{(L)}")
        z_label.next_to(equals, LEFT)
        z_label.align_to(terms.target, DOWN)
        z_label.set_color(self.z_color)
        z_label2 = z_label.copy()

        aL_start = VGroup(*self.formula[:4])
        aL_start.generate_target()
        aL_start.target.align_to(z_label, LEFT)
        z_label2.next_to(aL_start.target, RIGHT, SMALL_BUFF)
        z_label2.align_to(aL_start.target[0], DOWN)
        rp = self.formula[-1]
        rp.generate_target()
        rp.target.next_to(z_label2, RIGHT, SMALL_BUFF)
        rp.target.align_to(aL_start.target, DOWN)

        self.play(MoveToTarget(terms))
        self.play(Write(z_label), Write(equals))
        self.play(
            ReplacementTransform(z_label.copy(), z_label2),
            MoveToTarget(aL_start),
            MoveToTarget(rp),
        )
        self.wait()

        zL_formula = VGroup(z_label, equals, *terms)
        aL_formula = VGroup(*list(aL_start) + [z_label2, rp])
        self.set_variables_as_attrs(z_label, zL_formula, aL_formula)

    def break_into_computational_graph(self):
        network_early_layers = VGroup(*it.chain(
            self.network_mob.layers[:2],
            self.network_mob.edge_groups[:2]
        ))

        wL, aL, plus, bL = self.weighted_sum_terms
        top_terms = VGroup(wL, aL, bL).copy()
        zL = self.z_label.copy()
        aL = self.formula[0].copy()
        y = self.y_label.copy()
        C0 = self.cost_equation[0].copy()
        targets = VGroup()
        for mob in top_terms, zL, aL, C0:
            mob.generate_target()
            targets.add(mob.target)
        y.generate_target()
        top_terms.target.arrange(RIGHT, buff = MED_LARGE_BUFF)
        targets.arrange(DOWN, buff = LARGE_BUFF)
        targets.center().to_corner(DOWN+LEFT)
        y.target.next_to(aL.target, LEFT, LARGE_BUFF, DOWN)

        top_lines = VGroup(*[
            Line(
                term.get_bottom(), 
                zL.target.get_top(), 
                buff = SMALL_BUFF
            )
            for term in top_terms.target
        ])
        z_to_a_line, a_to_c_line, y_to_c_line = all_lines = [
            Line(
                m1.target.get_bottom(), 
                m2.target.get_top(), 
                buff = SMALL_BUFF
            )
            for m1, m2 in [
                (zL, aL), 
                (aL, C0), 
                (y, C0)
            ]
        ]
        for mob in [top_lines] + all_lines:
            yellow_copy = mob.copy().set_color(YELLOW)
            mob.flash = ShowCreationThenDestruction(yellow_copy)

        self.play(MoveToTarget(top_terms))
        self.wait()
        self.play(MoveToTarget(zL))
        self.play(
            ShowCreation(top_lines, lag_ratio = 0),
            top_lines.flash
        )
        self.wait()
        self.play(MoveToTarget(aL))
        self.play(
            network_early_layers.fade, 1,
            ShowCreation(z_to_a_line),
            z_to_a_line.flash
        )
        self.wait()
        self.play(MoveToTarget(y))
        self.play(MoveToTarget(C0))
        self.play(*it.chain(*[
            [ShowCreation(line), line.flash]
            for line in (a_to_c_line, y_to_c_line)
        ]))
        self.wait(2)

        comp_graph = VGroup()
        comp_graph.wL, comp_graph.aLm1, comp_graph.bL = top_terms
        comp_graph.top_lines = top_lines
        comp_graph.zL = zL
        comp_graph.z_to_a_line = z_to_a_line
        comp_graph.aL = aL
        comp_graph.y = y
        comp_graph.a_to_c_line = a_to_c_line
        comp_graph.y_to_c_line = y_to_c_line
        comp_graph.C0 = C0
        comp_graph.digest_mobject_attrs()
        self.comp_graph = comp_graph

    def show_preceding_layer_in_computational_graph(self):
        shift_vect = DOWN
        comp_graph = self.comp_graph
        comp_graph.save_state()
        comp_graph.generate_target()
        comp_graph.target.shift(shift_vect)
        rect = SurroundingRectangle(comp_graph.aLm1)

        attrs = ["wL", "aLm1", "bL", "zL"]
        new_terms = VGroup()
        for attr in attrs:
            term = getattr(comp_graph, attr)
            tex = term.get_tex_string()
            if "L-1" in tex:
                tex = tex.replace("L-1", "L-2")
            else:
                tex = tex.replace("L", "L-1")
            new_term = TexMobject(tex)
            new_term.set_color(term.get_color())
            new_term.move_to(term)
            new_terms.add(new_term)
        new_edges = VGroup(
            comp_graph.top_lines.copy(),
            comp_graph.z_to_a_line.copy(),
        )
        new_subgraph = VGroup(new_terms, new_edges)
        new_subgraph.next_to(comp_graph.target, UP, SMALL_BUFF)
        self.wLm1 = new_terms[0]
        self.zLm1 = new_terms[-1]

        prev_neuron = self.network_mob.layers[1]
        prev_neuron.restore()
        prev_edge = self.network_mob.edge_groups[1]
        prev_edge.restore()

        self.play(
            ShowCreation(rect),
            FadeIn(prev_neuron),
            ShowCreation(prev_edge)
        )
        self.play(
            ReplacementTransform(
                VGroup(prev_neuron, prev_edge).copy(),
                new_subgraph
            ),
            UpdateFromAlphaFunc(
                new_terms,
                lambda m, a : m.set_fill(opacity = a)
            ),
            MoveToTarget(comp_graph),
            rect.shift, shift_vect
        )
        self.wait(2)
        self.play(
            FadeOut(new_subgraph),
            FadeOut(prev_neuron),
            FadeOut(prev_edge),
            comp_graph.restore,
            rect.shift, -shift_vect,
            rect.set_stroke, BLACK, 0
        )
        VGroup(prev_neuron, prev_edge).fade(1)
        self.remove(rect)
        self.wait()

        self.prev_comp_subgraph = new_subgraph

    def show_number_lines(self):
        comp_graph = self.comp_graph
        wL, aLm1, bL, zL, aL, C0 = [
            getattr(comp_graph, attr)
            for attr in ["wL", "aLm1", "bL", "zL", "aL", "C0"]
        ]
        wL.val = self.network.weights[-1][0][0]
        aL.val = self.decimals[0].number
        zL.val = sigmoid_inverse(aL.val)
        C0.val = (aL.val - 1)**2

        number_line = UnitInterval(
            unit_size = 2,
            stroke_width = 2,
            tick_size = 0.075,
            color = LIGHT_GREY,
        )

        for mob in wL, zL, aL, C0:
            mob.number_line = number_line.deepcopy()
            if mob is wL:
                mob.number_line.next_to(mob, UP, MED_LARGE_BUFF, LEFT)
            else:
                mob.number_line.next_to(mob, RIGHT)
            if mob is C0:
                mob.number_line.x_max = 0.5
                for tick_mark in mob.number_line.tick_marks[1::2]:
                    mob.number_line.tick_marks.remove(tick_mark)
            mob.dot = Dot(color = mob.get_color())
            mob.dot.move_to(
                mob.number_line.number_to_point(mob.val)
            )
            if mob is wL:
                path_arc = 0
                dot_spot = mob.dot.get_bottom()
            else:
                path_arc = -0.7*np.pi
                dot_spot = mob.dot.get_top()
            if mob is C0:
                mob_spot = mob[0].get_corner(UP+RIGHT)
                tip_length = 0.15
            else:
                mob_spot = mob.get_corner(UP+RIGHT)
                tip_length = 0.2
            mob.arrow = Arrow(
                mob_spot, dot_spot,
                path_arc = path_arc,
                tip_length = tip_length,
                buff = SMALL_BUFF,
            )
            mob.arrow.set_color(mob.get_color())
            mob.arrow.set_stroke(width = 5)

            self.play(ShowCreation(
                mob.number_line, 
                lag_ratio = 0.5
            ))
            self.play(
                ShowCreation(mob.arrow),
                ReplacementTransform(
                    mob.copy(), mob.dot,
                    path_arc = path_arc
                )
            )
        self.wait()

    def ask_about_w_sensitivity(self):
        wL, aLm1, bL, zL, aL, C0 = [
            getattr(self.comp_graph, attr)
            for attr in ["wL", "aLm1", "bL", "zL", "aL", "C0"]
        ]
        aLm1_val = self.last_neurons[1].get_fill_opacity()
        bL_val = self.network.biases[-1][0]

        get_wL_val = lambda : wL.number_line.point_to_number(
            wL.dot.get_center()
        )
        get_zL_val = lambda : get_wL_val()*aLm1_val+bL_val
        get_aL_val = lambda : sigmoid(get_zL_val())
        get_C0_val = lambda : (get_aL_val() - 1)**2

        def generate_dot_update(term, val_func):
            def update_dot(dot):
                dot.move_to(term.number_line.number_to_point(val_func()))
                return dot
            return update_dot

        dot_update_anims = [
            UpdateFromFunc(term.dot, generate_dot_update(term, val_func))
            for term, val_func in [
                (zL, get_zL_val),
                (aL, get_aL_val),
                (C0, get_C0_val),
            ]
        ]

        def shake_dot(run_time = 2, rate_func = there_and_back):
            self.play(
                ApplyMethod(
                    wL.dot.shift, LEFT, 
                    rate_func = rate_func, 
                    run_time = run_time
                ),
                *dot_update_anims
            )        

        wL_line = Line(wL.dot.get_center(), wL.dot.get_center()+LEFT)
        del_wL = TexMobject("\\partial w^{(L)}")
        del_wL.scale(self.derivative_scale_val)
        del_wL.brace = Brace(wL_line, UP, buff = SMALL_BUFF)
        del_wL.set_color(wL.get_color())
        del_wL.next_to(del_wL.brace, UP, SMALL_BUFF)

        C0_line = Line(C0.dot.get_center(), C0.dot.get_center()+MED_SMALL_BUFF*RIGHT)
        del_C0 = TexMobject("\\partial C_0")
        del_C0.scale(self.derivative_scale_val)
        del_C0.brace = Brace(C0_line, UP, buff = SMALL_BUFF)
        del_C0.set_color(C0.get_color())
        del_C0.next_to(del_C0.brace, UP, SMALL_BUFF)

        for sym in del_wL, del_C0:
            self.play(
                GrowFromCenter(sym.brace),
                Write(sym, run_time = 1)
            )
            shake_dot()
        self.wait()

        self.set_variables_as_attrs(
            shake_dot, del_wL, del_C0,
        )

    def show_derivative_wrt_w(self):
        del_wL = self.del_wL
        del_C0 = self.del_C0
        cost_word = self.cost_word
        cost_arrow = self.cost_arrow
        shake_dot = self.shake_dot
        wL = self.comp_graph.wL

        dC_dw = TexMobject(
            "{\\partial C_0", "\\over", "\\partial w^{(L)} }"
        )
        dC_dw[0].set_color(del_C0.get_color())
        dC_dw[2].set_color(del_wL.get_color())
        dC_dw.scale(self.derivative_scale_val)
        dC_dw.to_edge(UP, buff = MED_SMALL_BUFF)
        dC_dw.shift(3.5*LEFT)

        full_rect = SurroundingRectangle(dC_dw)
        full_rect_copy = full_rect.copy()
        words = TextMobject("What we want")
        words.next_to(full_rect, RIGHT)
        words.set_color(YELLOW)

        denom_rect = SurroundingRectangle(dC_dw[2])
        numer_rect = SurroundingRectangle(dC_dw[0])

        self.play(
            ReplacementTransform(del_C0.copy(), dC_dw[0]),
            ReplacementTransform(del_wL.copy(), dC_dw[2]),
            Write(dC_dw[1], run_time = 1)
        )
        self.play(
            FadeOut(cost_word),
            FadeOut(cost_arrow),
            ShowCreation(full_rect),
            Write(words, run_time = 1),
        )
        self.wait(2)
        self.play(
            FadeOut(words),
            ReplacementTransform(full_rect, denom_rect)
        )
        self.play(Transform(dC_dw[2].copy(), del_wL, remover = True))
        shake_dot()
        self.play(ReplacementTransform(denom_rect, numer_rect))
        self.play(Transform(dC_dw[0].copy(), del_C0, remover = True))
        shake_dot()
        self.wait()
        self.play(ReplacementTransform(numer_rect, full_rect_copy))
        self.play(FadeOut(full_rect_copy))
        self.wait()

        self.dC_dw = dC_dw

    def show_chain_of_events(self):
        comp_graph = self.comp_graph
        wL, zL, aL, C0 = [
            getattr(comp_graph, attr)
            for attr in ["wL", "zL", "aL", "C0"]
        ]
        del_wL = self.del_wL
        del_C0 = self.del_C0

        zL_line = Line(ORIGIN, MED_LARGE_BUFF*LEFT)
        zL_line.shift(zL.dot.get_center())
        del_zL = TexMobject("\\partial z^{(L)}")
        del_zL.set_color(zL.get_color())
        del_zL.brace = Brace(zL_line, DOWN, buff = SMALL_BUFF)

        aL_line = Line(ORIGIN, MED_SMALL_BUFF*LEFT)
        aL_line.shift(aL.dot.get_center())
        del_aL = TexMobject("\\partial a^{(L)}")
        del_aL.set_color(aL.get_color())
        del_aL.brace = Brace(aL_line, DOWN, buff = SMALL_BUFF)

        for sym in del_zL, del_aL:
            sym.scale(self.derivative_scale_val)
            sym.brace.stretch_about_point(
                0.5, 1, sym.brace.get_top(),
            )
            sym.shift(
                sym.brace.get_bottom()+SMALL_BUFF*DOWN \
                -sym[0].get_corner(UP+RIGHT)
            )

        syms = [del_wL, del_zL, del_aL, del_C0]
        for s1, s2 in zip(syms, syms[1:]):
            self.play(
                ReplacementTransform(s1.copy(), s2),
                ReplacementTransform(s1.brace.copy(), s2.brace),
            )
            self.shake_dot(run_time = 1.5)
            self.wait(0.5)
        self.wait()

        self.set_variables_as_attrs(del_zL, del_aL)

    def show_chain_rule(self):
        dC_dw = self.dC_dw
        del_syms = [
            getattr(self, attr)
            for attr in ("del_wL", "del_zL", "del_aL", "del_C0")
        ]

        dz_dw = TexMobject(
            "{\\partial z^{(L)}", "\\over", "\\partial w^{(L)}}"
        )
        da_dz = TexMobject(
            "{\\partial a^{(L)}", "\\over", "\\partial z^{(L)}}"
        )
        dC_da = TexMobject(
            "{\\partial C0}", "\\over", "\\partial a^{(L)}}"
        )
        dz_dw[2].set_color(self.del_wL.get_color())
        VGroup(dz_dw[0], da_dz[2]).set_color(self.z_color)
        dC_da[0].set_color(self.cost_color)
        equals = TexMobject("=")
        group = VGroup(equals, dz_dw, da_dz, dC_da)
        group.arrange(RIGHT, SMALL_BUFF)
        group.scale(self.derivative_scale_val)
        group.next_to(dC_dw, RIGHT)
        for mob in group[1:]:
            target_y = equals.get_center()[1]
            y = mob[1].get_center()[1]
            mob.shift((target_y - y)*UP)

        self.play(Write(equals, run_time = 1))
        for frac, top_sym, bot_sym in zip(group[1:], del_syms[1:], del_syms):
            self.play(Indicate(top_sym, rate_func = wiggle))
            self.play(
                ReplacementTransform(top_sym.copy(), frac[0]),
                FadeIn(frac[1]),
            )
            self.play(Indicate(bot_sym, rate_func = wiggle))
            self.play(ReplacementTransform(
                bot_sym.copy(), frac[2]
            ))
            self.wait()
        self.shake_dot()
        self.wait()

        self.chain_rule_equation = VGroup(dC_dw, *group)

    def name_chain_rule(self):
        graph_parts = self.get_all_comp_graph_parts()
        equation = self.chain_rule_equation
        rect = SurroundingRectangle(equation)
        group = VGroup(equation, rect)
        group.generate_target()
        group.target.to_corner(UP+LEFT)
        words = TextMobject("Chain rule")
        words.set_color(YELLOW)
        words.next_to(group.target, DOWN)

        self.play(ShowCreation(rect))
        self.play(
            MoveToTarget(group),
            Write(words, run_time = 1),
            graph_parts.scale, 0.7, graph_parts.get_bottom()
        )
        self.wait(2)
        self.play(*list(map(FadeOut, [rect, words])))

    def indicate_everything_on_screen(self):
        everything = VGroup(*self.get_top_level_mobjects())
        everything = VGroup(*[m for m in everything.family_members_with_points() if not m.is_subpath])
        self.play(LaggedStartMap(
            Indicate, everything,
            rate_func = wiggle,
            lag_ratio = 0.2,
            run_time = 5
        ))
        self.wait()

    def prepare_for_derivatives(self):
        zL_formula = self.zL_formula
        aL_formula = self.aL_formula
        az_formulas = VGroup(zL_formula, aL_formula)
        cost_equation = self.cost_equation
        desired_output_words = self.desired_output_words

        az_formulas.generate_target()
        az_formulas.target.to_edge(RIGHT)

        index = 4
        cost_eq = cost_equation[index]
        z_eq = az_formulas.target[0][1]
        x_shift = (z_eq.get_center() - cost_eq.get_center())[0]*RIGHT
        cost_equation.generate_target()
        Transform(
            VGroup(*cost_equation.target[1:index]),
            VectorizedPoint(cost_eq.get_left())
        ).update(1)
        cost_equation.target[0].next_to(cost_eq, LEFT, SMALL_BUFF)
        cost_equation.target.shift(x_shift)

        self.play(
            FadeOut(self.all_comp_graph_parts),
            FadeOut(self.desired_output_words),
            MoveToTarget(az_formulas),
            MoveToTarget(cost_equation)
        )

    def compute_derivatives(self):
        cost_equation = self.cost_equation
        zL_formula = self.zL_formula
        aL_formula = self.aL_formula
        chain_rule_equation = self.chain_rule_equation.copy()
        dC_dw, equals, dz_dw, da_dz, dC_da = chain_rule_equation

        derivs = VGroup(dC_da, da_dz, dz_dw)
        deriv_targets = VGroup()
        for deriv in derivs:
            deriv.generate_target()
            deriv_targets.add(deriv.target)
        deriv_targets.arrange(DOWN, buff = MED_LARGE_BUFF)
        deriv_targets.next_to(dC_dw, DOWN, LARGE_BUFF)
        for deriv in derivs:
            deriv.equals = TexMobject("=")
            deriv.equals.next_to(deriv.target, RIGHT)


        #dC_da
        self.play(
            MoveToTarget(dC_da),
            Write(dC_da.equals)
        )
        index = 4
        cost_rhs = VGroup(*cost_equation[index+1:])       
        dC_da.rhs = cost_rhs.copy()
        two = dC_da.rhs[-1]
        two.scale(1.5)
        two.next_to(dC_da.rhs[0], LEFT, SMALL_BUFF)
        dC_da.rhs.next_to(dC_da.equals, RIGHT)
        dC_da.rhs.shift(0.7*SMALL_BUFF*UP)
        cost_equation.save_state()

        self.play(
            cost_equation.next_to, dC_da.rhs,
            DOWN, MED_LARGE_BUFF, LEFT
        )
        self.wait()
        self.play(ReplacementTransform(
            cost_rhs.copy(), dC_da.rhs,
            path_arc = np.pi/2,
        ))
        self.wait()
        self.play(cost_equation.restore)
        self.wait()

        #show_difference
        neuron = self.last_neurons[0]
        decimal = self.decimals[0]
        double_arrow = DoubleArrow(
            neuron.get_right(),
            self.desired_output_neuron.get_left(),
            buff = SMALL_BUFF,
            color = RED
        )

        moving_decimals = VGroup(
            self.decimals[0].copy(),
            self.desired_output_decimal.copy()
        )
        minus = TexMobject("-")
        minus.move_to(moving_decimals)
        minus.scale(0.7)
        minus.set_fill(opacity = 0)
        moving_decimals.submobjects.insert(1, minus)
        moving_decimals.generate_target(use_deepcopy = True)
        moving_decimals.target.arrange(RIGHT, buff = SMALL_BUFF)
        moving_decimals.target.scale(1.5)
        moving_decimals.target.next_to(
            dC_da.rhs, DOWN, 
            buff = MED_LARGE_BUFF,
            aligned_edge = RIGHT,
        )
        moving_decimals.target.set_fill(WHITE, 1)

        self.play(ReplacementTransform(
            dC_da.rhs.copy(), double_arrow
        ))
        self.wait()
        self.play(MoveToTarget(moving_decimals))
        opacity = neuron.get_fill_opacity()
        for target_o in 0, opacity:
            self.wait(2)
            self.play(
                neuron.set_fill, None, target_o,
                *[
                    ChangingDecimal(d, lambda a : neuron.get_fill_opacity())
                    for d in (decimal, moving_decimals[0])
                ]
            )
        self.play(*list(map(FadeOut, [double_arrow, moving_decimals])))

        #da_dz
        self.play(
            MoveToTarget(da_dz),
            Write(da_dz.equals)
        )
        a_rhs = VGroup(*aL_formula[2:])
        da_dz.rhs = a_rhs.copy()
        prime = TexMobject("'")
        prime.move_to(da_dz.rhs[0].get_corner(UP+RIGHT))
        da_dz.rhs[0].shift(0.5*SMALL_BUFF*LEFT)
        da_dz.rhs.add_to_back(prime)
        da_dz.rhs.next_to(da_dz.equals, RIGHT)
        da_dz.rhs.shift(0.5*SMALL_BUFF*UP)
        aL_formula.save_state()
        self.play(
            aL_formula.next_to, da_dz.rhs,
            DOWN, MED_LARGE_BUFF, LEFT
        )
        self.wait()
        self.play(ReplacementTransform(
            a_rhs.copy(), da_dz.rhs,
        ))
        self.wait()
        self.play(aL_formula.restore)
        self.wait()

        #dz_dw
        self.play(
            MoveToTarget(dz_dw),
            Write(dz_dw.equals)
        )
        z_rhs = VGroup(*zL_formula[2:])
        dz_dw.rhs = z_rhs[1].copy()
        dz_dw.rhs.next_to(dz_dw.equals, RIGHT)
        dz_dw.rhs.shift(SMALL_BUFF*UP)
        zL_formula.save_state()
        self.play(
            zL_formula.next_to, dz_dw.rhs,
                DOWN, MED_LARGE_BUFF, LEFT,
        )
        self.wait()
        rect = SurroundingRectangle(VGroup(*zL_formula[2:4]))
        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))
        self.play(ReplacementTransform(
            z_rhs[1].copy(), dz_dw.rhs,
        ))
        self.wait()
        self.play(zL_formula.restore)
        self.wait()

        self.derivative_equations = VGroup(dC_da, da_dz, dz_dw)

    def get_lost_in_formulas(self):
        randy = Randolph()
        randy.flip()
        randy.scale(0.7)
        randy.to_edge(DOWN)
        randy.shift(LEFT)

        self.play(FadeIn(randy))
        self.play(randy.change, "pleading", self.chain_rule_equation)
        self.play(Blink(randy))
        self.play(randy.change, "maybe")
        self.play(Blink(randy))
        self.play(FadeOut(randy))

    def fire_together_wire_together(self):
        dz_dw = self.derivative_equations[2]
        rhs = dz_dw.rhs
        rhs_copy = rhs.copy()
        del_wL = dz_dw[2].copy()
        rect = SurroundingRectangle(VGroup(dz_dw, dz_dw.rhs))
        edge = self.network_mob.edge_groups[-1][0]
        edge.save_state()
        neuron = self.last_neurons[1]
        decimal = self.decimals[1]

        def get_decimal_anims():
            return [
                ChangingDecimal(decimal, lambda a : neuron.get_fill_opacity()),
                UpdateFromFunc(
                    decimal, lambda m : m.set_color(
                        WHITE if neuron.get_fill_opacity() < 0.8 \
                        else BLACK
                    )
                )
            ]

        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))
        self.play(
            del_wL.next_to, edge, UP, SMALL_BUFF
        )
        self.play(
            edge.set_stroke, None, 10,
            rate_func = wiggle,
            run_time = 3,
        )
        self.wait()
        self.play(rhs.shift, MED_LARGE_BUFF*UP, rate_func = wiggle)
        self.play(
            rhs_copy.move_to, neuron,
            rhs_copy.set_fill, None, 0
        )
        self.remove(rhs_copy)
        self.play(
            neuron.set_fill, None, 0,
            *get_decimal_anims(),
            run_time = 3,
            rate_func = there_and_back
        )
        self.wait()

        #Fire together wire together
        opacity = neuron.get_fill_opacity()
        self.play(
            neuron.set_fill, None, 0.99, 
            *get_decimal_anims()
        )
        self.play(edge.set_stroke, None, 8)
        self.play(
            neuron.set_fill, None, opacity, 
            *get_decimal_anims()
        )
        self.play(edge.restore, FadeOut(del_wL))
        self.wait(3)

    def organize_chain_rule_rhs(self):
        fracs = self.derivative_equations
        equals_group = VGroup(*[frac.equals for frac in fracs])
        rhs_group = VGroup(*[frac.rhs for frac in reversed(fracs)])

        chain_rule_equation = self.chain_rule_equation
        equals = TexMobject("=")
        equals.next_to(chain_rule_equation, RIGHT)

        rhs_group.generate_target()
        rhs_group.target.arrange(RIGHT, buff = SMALL_BUFF)
        rhs_group.target.next_to(equals, RIGHT)
        rhs_group.target.shift(SMALL_BUFF*UP)

        right_group = VGroup(
            self.cost_equation, self.zL_formula, self.aL_formula,
            self.network_mob, self.decimals,
            self.a_labels, self.a_label_arrows,
            self.y_label, self.y_label_arrow,
            self.desired_output_neuron,
            self.desired_output_rect,
            self.desired_output_decimal,
        )

        self.play(
            MoveToTarget(rhs_group, path_arc = np.pi/2),
            Write(equals),
            FadeOut(fracs),
            FadeOut(equals_group),
            right_group.to_corner, DOWN+RIGHT
        )
        self.wait()

        rhs_group.add(equals)
        self.chain_rule_rhs = rhs_group

    def show_average_derivative(self):
        dC0_dw = self.chain_rule_equation[0]
        full_derivative = TexMobject(
            "{\\partial C", "\\over", "\\partial w^{(L)}}",
            "=", "\\frac{1}{n}", "\\sum_{k=0}^{n-1}",
            "{\\partial C_k", "\\over", "\\partial w^{(L)}}"
        )
        full_derivative.set_color_by_tex_to_color_map({
            "partial C" : self.cost_color,
            "partial w" : self.del_wL.get_color()
        })
        full_derivative.to_edge(LEFT)

        dCk_dw = VGroup(*full_derivative[-3:])
        lhs = VGroup(*full_derivative[:3])
        rhs = VGroup(*full_derivative[4:])
        lhs_brace = Brace(lhs, DOWN)
        lhs_text = lhs_brace.get_text("Derivative of \\\\ full cost function")
        rhs_brace = Brace(rhs, UP)
        rhs_text = rhs_brace.get_text("Average of all \\\\ training examples")
        VGroup(
            full_derivative, lhs_brace, lhs_text, rhs_brace, rhs_text
        ).to_corner(DOWN+LEFT)

        mover = dC0_dw.copy()
        self.play(Transform(mover, dCk_dw))
        self.play(Write(full_derivative, run_time = 2))
        self.remove(mover)
        for brace, text in (rhs_brace, rhs_text), (lhs_brace, lhs_text):
            self.play(
                GrowFromCenter(brace),
                Write(text, run_time = 2),
            )
            self.wait(2)
        self.cycle_through_altnernate_training_examples()
        self.play(*list(map(FadeOut, [
            VGroup(*full_derivative[3:]), 
            lhs_brace, lhs_text,
            rhs_brace, rhs_text,
        ])))

        self.dC_dw = lhs

    def cycle_through_altnernate_training_examples(self):
        neurons = VGroup(
            self.desired_output_neuron, *self.last_neurons
        )
        decimals = VGroup(
            self.desired_output_decimal, *self.decimals
        )
        group = VGroup(neurons, decimals)
        group.save_state()

        for x in range(20):
            for n, d in zip(neurons, decimals):
                o = np.random.random()
                if n is self.desired_output_neuron:
                    o = np.round(o)
                n.set_fill(opacity = o)
                Transform(
                    d, self.get_neuron_activation_decimal(n)
                ).update(1)
            self.wait(0.2)
        self.play(group.restore, run_time = 0.2)

    def show_gradient(self):
        dC_dw = self.dC_dw
        dC_dw.generate_target()
        terms = VGroup(
            TexMobject("{\\partial C", "\\over", "\\partial w^{(1)}"),
            TexMobject("{\\partial C", "\\over", "\\partial b^{(1)}"),
            TexMobject("\\vdots"),
            dC_dw.target,
            TexMobject("{\\partial C", "\\over", "\\partial b^{(L)}"),
        )
        for term in terms:
            if isinstance(term, TexMobject):
                term.set_color_by_tex_to_color_map({
                    "partial C" : RED,
                    "partial w" : BLUE,
                    "partial b" : MAROON_B,
                })
        terms.arrange(DOWN, buff = MED_LARGE_BUFF)
        lb, rb = brackets = TexMobject("[]")
        brackets.scale(3)
        brackets.stretch_to_fit_height(1.1*terms.get_height())
        lb.next_to(terms, LEFT, buff = SMALL_BUFF)
        rb.next_to(terms, RIGHT, buff = SMALL_BUFF)
        vect = VGroup(lb, terms, rb)
        vect.set_height(5)
        lhs = TexMobject("\\nabla C", "=")
        lhs[0].set_color(RED)
        lhs.next_to(vect, LEFT)
        VGroup(lhs, vect).to_corner(DOWN+LEFT, buff = LARGE_BUFF)
        terms.remove(dC_dw.target)

        self.play(
            MoveToTarget(dC_dw),
            Write(vect, run_time = 1)
        )
        terms.add(dC_dw)
        self.play(Write(lhs))
        self.wait(2)
        self.play(FadeOut(VGroup(lhs, vect)))

    def transition_to_derivative_wrt_b(self):
        all_comp_graph_parts = self.all_comp_graph_parts
        all_comp_graph_parts.scale(
            1.3, about_point = all_comp_graph_parts.get_bottom()
        )
        comp_graph = self.comp_graph
        wL, bL, zL, aL, C0 = [
            getattr(comp_graph, attr)
            for attr in ["wL", "bL", "zL", "aL", "C0"]
        ]
        path_to_C = VGroup(wL, zL, aL, C0)

        top_expression = VGroup(
            self.chain_rule_equation,
            self.chain_rule_rhs
        )
        rect = SurroundingRectangle(top_expression)

        self.play(ShowCreation(rect))
        self.play(FadeIn(comp_graph), FadeOut(rect))
        for x in range(2):
            self.play(LaggedStartMap(
                Indicate, path_to_C, 
                rate_func = there_and_back,
                run_time = 1.5,
                lag_ratio = 0.7,
            ))
        self.wait()

    def show_derivative_wrt_b(self):
        comp_graph = self.comp_graph
        dC0_dw = self.chain_rule_equation[0]
        dz_dw = self.chain_rule_equation[2]
        aLm1 = self.chain_rule_rhs[0]
        left_term_group = VGroup(dz_dw, aLm1)
        dz_dw_rect = SurroundingRectangle(dz_dw)

        del_w = dC0_dw[2]
        del_b = TexMobject("\\partial b^{(L)}")
        del_b.set_color(MAROON_B)
        del_b.replace(del_w)

        dz_db = TexMobject(
            "{\\partial z^{(L)}", "\\over", "\\partial b^{(L)}}"
        )
        dz_db.set_color_by_tex_to_color_map({
            "partial z" : self.z_color,
            "partial b" : MAROON_B
        })
        dz_db.replace(dz_dw)

        one = TexMobject("1")
        one.move_to(aLm1, RIGHT)
        arrow = Arrow(
            dz_db.get_bottom(),
            one.get_bottom(),
            path_arc = np.pi/2,
            color = WHITE,
        )
        arrow.set_stroke(width = 2)

        wL, bL, zL, aL, C0 = [
            getattr(comp_graph, attr)
            for attr in ["wL", "bL", "zL", "aL", "C0"]
        ]
        path_to_C = VGroup(bL, zL, aL, C0)
        def get_path_animation():
            return LaggedStartMap(
                Indicate, path_to_C, 
                rate_func = there_and_back,
                run_time = 1.5,
                lag_ratio = 0.7,
            )

        zL_formula = self.zL_formula
        b_in_z_formula = zL_formula[-1]
        z_formula_rect = SurroundingRectangle(zL_formula)
        b_in_z_rect = SurroundingRectangle(b_in_z_formula)

        self.play(get_path_animation())
        self.play(ShowCreation(dz_dw_rect))
        self.play(FadeOut(dz_dw_rect))
        self.play(
            left_term_group.shift, DOWN,
            left_term_group.fade, 1,
        )
        self.remove(left_term_group)
        self.chain_rule_equation.remove(dz_dw)
        self.chain_rule_rhs.remove(aLm1)
        self.play(Transform(del_w, del_b))
        self.play(FadeIn(dz_db))
        self.play(get_path_animation())
        self.wait()
        self.play(ShowCreation(z_formula_rect))
        self.wait()
        self.play(ReplacementTransform(z_formula_rect, b_in_z_rect))
        self.wait()
        self.play(
            ReplacementTransform(b_in_z_formula.copy(), one),
            FadeOut(b_in_z_rect)
        )
        self.play(
            ShowCreation(arrow),
            ReplacementTransform(
                dz_db.copy(), one,
                path_arc = arrow.path_arc
            )
        )
        self.wait(2)
        self.play(*list(map(FadeOut, [dz_db, arrow, one])))

        self.dz_db = dz_db

    def show_derivative_wrt_a(self):
        denom = self.chain_rule_equation[0][2]
        numer = VGroup(*self.chain_rule_equation[0][:2])
        del_aLm1 = TexMobject("\\partial a^{(L-1)}")
        del_aLm1.scale(0.8)
        del_aLm1.move_to(denom)
        dz_daLm1 = TexMobject(
            "{\\partial z^{(L)}", "\\over", "\\partial a^{(L-1)}}"
        )
        dz_daLm1.scale(0.8)
        dz_daLm1.next_to(self.chain_rule_equation[1], RIGHT, SMALL_BUFF)
        dz_daLm1.shift(0.7*SMALL_BUFF*UP)
        dz_daLm1[0].set_color(self.z_color)
        dz_daLm1_rect = SurroundingRectangle(dz_daLm1)
        wL = self.zL_formula[2].copy()
        wL.next_to(self.chain_rule_rhs[0], LEFT, SMALL_BUFF)

        arrow = Arrow(
            dz_daLm1.get_bottom(), wL.get_bottom(),
            path_arc = np.pi/2,
            color = WHITE,
        )

        comp_graph = self.comp_graph
        path_to_C = VGroup(*[
            getattr(comp_graph, attr)
            for attr in ["aLm1", "zL", "aL", "C0"]
        ])
        def get_path_animation():
            return LaggedStartMap(
                Indicate, path_to_C, 
                rate_func = there_and_back,
                run_time = 1.5,
                lag_ratio = 0.7,
            )

        zL_formula = self.zL_formula
        z_formula_rect = SurroundingRectangle(zL_formula)
        a_in_z_rect = SurroundingRectangle(VGroup(*zL_formula[2:4]))
        wL_in_z = zL_formula[2]

        for x in range(3):
            self.play(get_path_animation())
        self.play(
            numer.shift, SMALL_BUFF*UP,
            Transform(denom, del_aLm1)
        )
        self.play(
            FadeIn(dz_daLm1),
            VGroup(*self.chain_rule_equation[-2:]).shift, SMALL_BUFF*RIGHT,
        )
        self.wait()
        self.play(ShowCreation(dz_daLm1_rect))
        self.wait()
        self.play(ReplacementTransform(
            dz_daLm1_rect, z_formula_rect
        ))
        self.wait()
        self.play(ReplacementTransform(z_formula_rect, a_in_z_rect))
        self.play(
            ReplacementTransform(wL_in_z.copy(), wL),
            FadeOut(a_in_z_rect)
        )
        self.play(
            ShowCreation(arrow),
            ReplacementTransform(
                dz_daLm1.copy(), wL,
                path_arc = arrow.path_arc
            )
        )
        self.wait(2)

        self.chain_rule_rhs.add(wL, arrow)
        self.chain_rule_equation.add(dz_daLm1)

    def show_previous_weight_and_bias(self):
        to_fade = self.chain_rule_rhs
        comp_graph = self.comp_graph
        prev_comp_subgraph = self.prev_comp_subgraph
        prev_comp_subgraph.scale(0.8)
        prev_comp_subgraph.next_to(comp_graph, UP, SMALL_BUFF)

        prev_layer = VGroup(
            self.network_mob.layers[1],
            self.network_mob.edge_groups[1],
        )
        for mob in prev_layer:
            mob.restore()
        prev_layer.next_to(self.last_neurons, LEFT, buff = 0)
        self.remove(prev_layer)

        self.play(LaggedStartMap(FadeOut, to_fade, run_time = 1))
        self.play(
            ShowCreation(prev_comp_subgraph, run_time = 1),
            self.chain_rule_equation.to_edge, RIGHT
        )
        self.play(FadeIn(prev_layer))

        ###
        neuron = self.network_mob.layers[1].neurons[0]
        decimal = self.get_neuron_activation_decimal(neuron)
        a_label = TexMobject("a^{(L-2)}")
        a_label.replace(self.a_labels[1])
        arrow = self.a_label_arrows[1].copy()
        VGroup(a_label, arrow).shift(
            neuron.get_center() - self.last_neurons[1].get_center()
        )

        self.play(
            Write(a_label, run_time = 1),
            Write(decimal, run_time = 1),
            GrowArrow(arrow),
        )        

    def animate_long_path(self):
        comp_graph = self.comp_graph
        path_to_C = VGroup(
            self.wLm1, self.zLm1,
            *[
                getattr(comp_graph, attr)
                for attr in ["aLm1", "zL", "aL", "C0"]
            ]
        )
        for x in range(2):
            self.play(LaggedStartMap(
                Indicate, path_to_C, 
                rate_func = there_and_back,
                run_time = 1.5,
                lag_ratio = 0.4,
            ))
        self.wait(2)

    ###

    def get_neuron_activation_decimal(self, neuron):
        opacity = neuron.get_fill_opacity()
        decimal = DecimalNumber(opacity, num_decimal_places = 2)
        decimal.set_width(0.85*neuron.get_width())
        if decimal.number > 0.8:
            decimal.set_fill(BLACK)
        decimal.move_to(neuron)
        return decimal

    def get_all_comp_graph_parts(self):
        comp_graph = self.comp_graph
        result = VGroup(comp_graph)
        for attr in "wL", "zL", "aL", "C0":
            sym = getattr(comp_graph, attr)
            result.add(
                sym.arrow, sym.number_line, sym.dot
            )
            del_sym = getattr(self, "del_" + attr)
            result.add(del_sym, del_sym.brace)

        self.all_comp_graph_parts = result
        return result

class IsntThatOverSimplified(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Isn't that over-simplified?", 
            target_mode = "raise_right_hand",
            run_time = 1
        )
        self.change_student_modes(
            "pondering", "raise_right_hand", "pondering"
        )
        self.wait()
        self.teacher_says(
            "Not that much, actually!",
            run_time = 1,
            target_mode = "hooray"
        )
        self.wait(2)

class GeneralFormulas(SimplestNetworkExample):
    CONFIG = {
        "layer_sizes" : [3, 3, 2],
        "network_mob_config" : {
            "include_output_labels" : False,
            "neuron_to_neuron_buff" : LARGE_BUFF,
            "neuron_radius" : 0.3,
        },
        "edge_stroke_width" : 4,
        "stroke_width_exp" : 0.2,
        "random_seed" : 9,
    }
    def setup(self):
        self.seed_random_libraries()
        self.setup_bases()

    def construct(self):
        self.setup_network_mob()
        self.show_all_a_labels()
        self.only_show_abstract_a_labels()
        self.add_desired_output()
        self.show_cost()
        self.show_example_weight()
        self.show_values_between_weight_and_cost()
        self.show_weight_chain_rule()
        self.show_derivative_wrt_prev_activation()
        self.show_multiple_paths_from_prev_layer_neuron()
        self.show_previous_layer()

    def setup_network_mob(self):
        self.color_network_edges()
        self.network_mob.to_edge(LEFT)
        self.network_mob.shift(DOWN)
        in_vect = np.random.random(self.layer_sizes[0])
        self.network_mob.activate_layers(in_vect)
        self.remove(self.network_mob.layers[0])
        self.remove(self.network_mob.edge_groups[0])

    def show_all_a_labels(self):
        Lm1_neurons = self.network_mob.layers[-2].neurons
        L_neurons = self.network_mob.layers[-1].neurons
        all_arrows = VGroup()
        all_labels = VGroup()
        all_decimals = VGroup()
        all_subscript_rects = VGroup()
        for neurons in L_neurons, Lm1_neurons:
            is_L = neurons is L_neurons
            vect = LEFT if is_L else RIGHT
            s = "L" if is_L else "L-1"
            arrows = VGroup()
            labels = VGroup()
            decimals = VGroup()
            subscript_rects = VGroup()
            for i, neuron in enumerate(neurons):
                arrow = Arrow(ORIGIN, vect)
                arrow.next_to(neuron, -vect)
                arrow.set_fill(WHITE)
                label = TexMobject("a^{(%s)}_%d"%(s, i))
                label.next_to(arrow, -vect, SMALL_BUFF)
                rect = SurroundingRectangle(label[-1], buff = 0.5*SMALL_BUFF)
                decimal = self.get_neuron_activation_decimal(neuron)
                neuron.arrow = arrow
                neuron.label = label
                neuron.decimal = decimal
                arrows.add(arrow)
                labels.add(label)
                decimals.add(decimal)
                subscript_rects.add(rect)
            all_arrows.add(arrows)
            all_labels.add(labels)
            all_decimals.add(decimals)
            all_subscript_rects.add(subscript_rects)

        start_labels, start_arrows = [
            VGroup(*list(map(VGroup, [group[i][0] for i in (0, 1)]))).copy()
            for group in (all_labels, all_arrows)
        ]
        for label in start_labels:
            label[0][-1].set_color(BLACK)

        self.add(all_decimals)
        self.play(*it.chain(
            list(map(Write, start_labels)),
            [GrowArrow(a[0]) for a in start_arrows]
        ))
        self.wait()
        self.play(
            ReplacementTransform(start_labels, all_labels),
            ReplacementTransform(start_arrows, all_arrows),
        )
        self.play(LaggedStartMap(
            ShowCreationThenDestruction,
            VGroup(*all_subscript_rects.family_members_with_points()),
            lag_ratio = 0.7
        ))
        self.wait()

        self.set_variables_as_attrs(
            L_neurons, Lm1_neurons,
            all_arrows, all_labels,
            all_decimals, all_subscript_rects,
        )

    def only_show_abstract_a_labels(self):
        arrows_to_fade = VGroup()
        labels_to_fade = VGroup()
        labels_to_change = VGroup()
        self.chosen_neurons = VGroup()
        rects = VGroup()
        for x, layer in enumerate(self.network_mob.layers[-2:]):
            for y, neuron in enumerate(layer.neurons):
                if (x == 0 and y == 1) or (x == 1 and y == 0):
                    tex = "k" if x == 0 else "j"
                    neuron.label.generate_target()
                    self.replace_subscript(neuron.label.target, tex)
                    self.chosen_neurons.add(neuron)
                    labels_to_change.add(neuron.label)
                    rects.add(SurroundingRectangle(
                        neuron.label.target[-1], 
                        buff = 0.5*SMALL_BUFF
                    ))
                else:
                    labels_to_fade.add(neuron.label)
                    arrows_to_fade.add(neuron.arrow)

        self.play(
            LaggedStartMap(FadeOut, labels_to_fade),
            LaggedStartMap(FadeOut, arrows_to_fade),
            run_time = 1
        )
        for neuron, rect in zip(self.chosen_neurons, rects):
            self.play(
                MoveToTarget(neuron.label),
                ShowCreation(rect)
            )
            self.play(FadeOut(rect))
            self.wait()
        self.wait()

    def add_desired_output(self):
        layer = self.network_mob.layers[-1]
        desired_output = layer.deepcopy()
        desired_output.shift(3*RIGHT)
        desired_output_decimals = VGroup()
        arrows = VGroup()
        labels = VGroup()
        for i, neuron in enumerate(desired_output.neurons):
            neuron.set_fill(opacity = i)
            decimal = self.get_neuron_activation_decimal(neuron)
            neuron.decimal = decimal
            neuron.arrow = Arrow(ORIGIN, LEFT, color = WHITE)
            neuron.arrow.next_to(neuron, RIGHT)
            neuron.label = TexMobject("y_%d"%i)
            neuron.label.next_to(neuron.arrow, RIGHT)
            neuron.label.set_color(self.desired_output_color)

            desired_output_decimals.add(decimal)
            arrows.add(neuron.arrow)
            labels.add(neuron.label)
        rect = SurroundingRectangle(desired_output, buff = 0.5*SMALL_BUFF)
        words = TextMobject("Desired output")
        words.next_to(rect, DOWN)
        VGroup(words, rect).set_color(self.desired_output_color)

        self.play(
            FadeIn(rect),
            FadeIn(words),
            ReplacementTransform(layer.copy(), desired_output),
            FadeIn(labels),
            *[
                ReplacementTransform(n1.decimal.copy(), n2.decimal)
                for n1, n2 in zip(layer.neurons, desired_output.neurons)
            ] + list(map(GrowArrow, arrows))
        )
        self.wait()

        self.set_variables_as_attrs(
            desired_output,
            desired_output_decimals,
            desired_output_rect = rect,
            desired_output_words = words,
        )

    def show_cost(self):
        aj = self.chosen_neurons[1].label.copy()
        yj = self.desired_output.neurons[0].label.copy()

        cost_equation = TexMobject(
            "C_0", "=", "\\sum_{j = 0}^{n_L - 1}",
            "(", "a^{(L)}_j", "-", "y_j", ")", "^2"
        )
        cost_equation.to_corner(UP+RIGHT)
        cost_equation[0].set_color(self.cost_color)
        aj.target = cost_equation.get_part_by_tex("a^{(L)}_j")
        yj.target = cost_equation.get_part_by_tex("y_j")
        yj.target.set_color(self.desired_output_color)
        to_fade_in = VGroup(*[m for m in cost_equation if m not in [aj.target, yj.target]])
        sum_part = cost_equation.get_part_by_tex("sum")

        self.play(*[
            ReplacementTransform(mob, mob.target)
            for mob in (aj, yj)
        ])
        self.play(LaggedStartMap(FadeIn, to_fade_in))
        self.wait(2)
        self.play(LaggedStartMap(
            Indicate, sum_part,
            rate_func = wiggle,
        ))
        self.wait()
        for mob in aj.target, yj.target, cost_equation[-1]:
            self.play(Indicate(mob))
        self.wait()

        self.set_variables_as_attrs(cost_equation)

    def show_example_weight(self):
        edges = self.network_mob.edge_groups[-1]
        edge = self.chosen_neurons[1].edges_in[1]
        faded_edges = VGroup(*[e for e in edges if e is not edge])
        faded_edges.save_state()
        for faded_edge in faded_edges:
            faded_edge.save_state()

        w_label = TexMobject("w^{(L)}_{jk}")
        subscripts = VGroup(*w_label[-2:])
        w_label.scale(1.2)
        w_label.add_background_rectangle()
        w_label.next_to(ORIGIN, UP, SMALL_BUFF)
        w_label.rotate(edge.get_angle())
        w_label.shift(edge.get_center())
        w_label.set_color(BLUE)

        edges.save_state()
        edges.generate_target()
        for e in edges.target:
            e.rotate(-e.get_angle())
        edges.target.arrange(DOWN)
        edges.target.move_to(edges)
        edges.target.to_edge(UP)

        self.play(MoveToTarget(edges))
        self.play(LaggedStartMap(
            ApplyFunction, edges,
            lambda e : (
                lambda m : m.rotate_in_place(np.pi/12).set_color(YELLOW),
                e
            ),
            rate_func = wiggle
        ))
        self.play(edges.restore)
        self.play(faded_edges.fade, 0.9)
        for neuron in self.chosen_neurons:
            self.play(Indicate(neuron), Animation(neuron.decimal))
        self.play(Write(w_label))
        self.wait()
        self.play(Indicate(subscripts))
        for x in range(2):
            self.play(Swap(*subscripts))
            self.wait()

        self.set_variables_as_attrs(faded_edges, w_label)

    def show_values_between_weight_and_cost(self):
        z_formula = TexMobject(
            "z^{(L)}_j", "=", 
            "w^{(L)}_{j0}", "a^{(L-1)}_0", "+",
            "w^{(L)}_{j1}", "a^{(L-1)}_1", "+",
            "w^{(L)}_{j2}", "a^{(L-1)}_2", "+", 
            "b^{(L)}_j"
        )
        compact_z_formula = TexMobject(
            "z^{(L)}_j", "=", 
            "\\cdots", "", "+" 
            "w^{(L)}_{jk}", "a^{(L-1)}_k", "+", 
            "\\cdots", "", "", "",
        )
        for expression in z_formula, compact_z_formula:
            expression.to_corner(UP+RIGHT)
            expression.set_color_by_tex_to_color_map({
                "z^" : self.z_color,
                "w^" : self.w_label.get_color(),
                "b^" : MAROON_B,
            })
        w_part = z_formula.get_parts_by_tex("w^")[1]
        aLm1_part = z_formula.get_parts_by_tex("a^{(L-1)}")[1]

        a_formula = TexMobject(
            "a^{(L)}_j", "=", "\\sigma(", "z^{(L)}_j", ")"
        )
        a_formula.set_color_by_tex("z^", self.z_color)
        a_formula.next_to(z_formula, DOWN, MED_LARGE_BUFF)
        a_formula.align_to(self.cost_equation, LEFT)
        aL_part = a_formula[0]

        to_fade = VGroup(
            self.desired_output,
            self.desired_output_decimals,
            self.desired_output_rect,
            self.desired_output_words,
            *[
                VGroup(n.arrow, n.label)
                for n in self.desired_output.neurons
            ]
        )

        self.play(
            FadeOut(to_fade),
            self.cost_equation.next_to, a_formula, DOWN, MED_LARGE_BUFF,
            self.cost_equation.to_edge, RIGHT,
            ReplacementTransform(self.w_label[1].copy(), w_part),
            ReplacementTransform(
                self.chosen_neurons[0].label.copy(), 
                aLm1_part
            ),
        )
        self.play(Write(VGroup(*[m for m in z_formula if m not in [w_part, aLm1_part]])))
        self.wait()
        self.play(ReplacementTransform(
            self.chosen_neurons[1].label.copy(),
            aL_part
        ))
        self.play(
            Write(VGroup(*a_formula[1:3] + [a_formula[-1]])),
            ReplacementTransform(
                z_formula[0].copy(),
                a_formula.get_part_by_tex("z^")
            )
        )
        self.wait()

        self.set_variables_as_attrs(z_formula, compact_z_formula, a_formula)

    def show_weight_chain_rule(self):
        chain_rule = self.get_chain_rule(
            "{\\partial C_0", "\\over", "\\partial w^{(L)}_{jk}}",
            "=",
            "{\\partial z^{(L)}_j", "\\over", "\\partial w^{(L)}_{jk}}",
            "{\\partial a^{(L)}_j", "\\over", "\\partial z^{(L)}_j}",
            "{\\partial C_0", "\\over", "\\partial a^{(L)}_j}",
        )
        terms = VGroup(*[
            VGroup(*chain_rule[i:i+3])
            for i in range(4,len(chain_rule), 3)
        ])
        rects = VGroup(*[
            SurroundingRectangle(term, buff = 0.5*SMALL_BUFF)
            for term in terms
        ])
        rects.set_color_by_gradient(GREEN, WHITE, RED)

        self.play(Transform(
            self.z_formula, self.compact_z_formula
        ))
        self.play(Write(chain_rule))
        self.wait()
        self.play(LaggedStartMap(
            ShowCreationThenDestruction, rects,
            lag_ratio = 0.7,
            run_time = 3
        ))
        self.wait()

        self.set_variables_as_attrs(chain_rule)

    def show_derivative_wrt_prev_activation(self):
        chain_rule = self.get_chain_rule(
            "{\\partial C_0", "\\over", "\\partial a^{(L-1)}_k}",
            "=",
            "\\sum_{j=0}^{n_L - 1}", 
            "{\\partial z^{(L)}_j", "\\over", "\\partial a^{(L-1)}_k}",
            "{\\partial a^{(L)}_j", "\\over", "\\partial z^{(L)}_j}",
            "{\\partial C_0", "\\over", "\\partial a^{(L)}_j}",
        )
        formulas = VGroup(self.z_formula, self.a_formula, self.cost_equation)

        n = chain_rule.index_of_part_by_tex("sum")
        self.play(ReplacementTransform(
            self.chain_rule, VGroup(*chain_rule[:n] + chain_rule[n+1:])
        ))
        self.play(Write(chain_rule[n], run_time = 1))
        self.wait()

        self.set_variables_as_attrs(chain_rule)

    def show_multiple_paths_from_prev_layer_neuron(self):
        neurons = self.network_mob.layers[-1].neurons
        labels, arrows, decimals = [
            VGroup(*[getattr(n, attr) for n in neurons])
            for attr in ("label", "arrow", "decimal")
        ]
        edges = VGroup(*[n.edges_in[1] for n in neurons])
        labels[0].generate_target()
        self.replace_subscript(labels[0].target, "0")

        paths = [
            VGroup(
                self.chosen_neurons[0].label,
                self.chosen_neurons[0].arrow,
                self.chosen_neurons[0],
                self.chosen_neurons[0].decimal,
                edges[i],
                neurons[i],
                decimals[i],
                arrows[i],
                labels[i],
            )
            for i in range(2)
        ]
        path_lines = VGroup()
        for path in paths:
            points = [path[0].get_center()]
            for mob in path[1:]:
                if isinstance(mob, DecimalNumber):
                    continue
                points.append(mob.get_center())
            path_line = VMobject()
            path_line.set_points_as_corners(points)
            path_lines.add(path_line)
        path_lines.set_color(YELLOW)

        chain_rule = self.chain_rule
        n = chain_rule.index_of_part_by_tex("sum")
        brace = Brace(VGroup(*chain_rule[n:]), DOWN, buff = SMALL_BUFF)
        words = brace.get_text("Sum over layer L", buff = SMALL_BUFF)

        cost_aL = self.cost_equation.get_part_by_tex("a^{(L)}")

        self.play(
            MoveToTarget(labels[0]),
            FadeIn(labels[1]),
            GrowArrow(arrows[1]),
            edges[1].restore,
            FadeOut(self.w_label),
        )
        for x in range(5):
            anims = [
                ShowCreationThenDestruction(
                    path_line,
                    run_time = 1.5,
                    time_width = 0.5,
                )
                for path_line in path_lines
            ]
            if x == 2:
                anims += [
                    FadeIn(words),
                    GrowFromCenter(brace)
                ]
            self.play(*anims)
            self.wait()
        for path, path_line in zip(paths, path_lines):
            label = path[-1]
            self.play(
                LaggedStartMap(
                    Indicate, path,
                    rate_func = wiggle,
                    run_time = 1,
                ),
                ShowCreation(path_line),
                Animation(label)
            )
            self.wait()
            group = VGroup(label, cost_aL)
            self.play(
                group.shift, MED_SMALL_BUFF*UP, 
                rate_func = wiggle
            )
            self.play(FadeOut(path_line))
        self.wait()

    def show_previous_layer(self):
        mid_neurons = self.network_mob.layers[1].neurons
        layer = self.network_mob.layers[0]
        edges = self.network_mob.edge_groups[0]
        faded_edges = self.faded_edges
        to_fade = VGroup(
            self.chosen_neurons[0].label,
            self.chosen_neurons[0].arrow,
        )
        for neuron in layer.neurons:
            neuron.add(self.get_neuron_activation_decimal(neuron))

        all_edges_out = VGroup(*[
            VGroup(*[n.edges_in[i] for n in mid_neurons]).copy()
            for i in range(len(layer.neurons))
        ])
        all_edges_out.set_stroke(YELLOW, 3)

        deriv = VGroup(*self.chain_rule[:3])
        deriv_rect = SurroundingRectangle(deriv)
        mid_neuron_outlines = mid_neurons.copy()
        mid_neuron_outlines.set_fill(opacity = 0)
        mid_neuron_outlines.set_stroke(YELLOW, 5)

        def get_neurons_decimal_anims(neuron):
            return [
                ChangingDecimal(
                    neuron.decimal,
                    lambda a : neuron.get_fill_opacity(),
                ),
                UpdateFromFunc(
                    neuron.decimal,
                    lambda m : m.set_fill(
                        WHITE if neuron.get_fill_opacity() < 0.8 else BLACK
                    )
                )
            ]

        self.play(ShowCreation(deriv_rect))
        self.play(LaggedStartMap(
            ShowCreationThenDestruction, 
            mid_neuron_outlines
        ))
        self.play(*it.chain(*[
            [
                ApplyMethod(n.set_fill, None, random.random()),
            ] + get_neurons_decimal_anims(n)
            for n in mid_neurons
        ]), run_time = 4, rate_func = there_and_back)
        self.play(faded_edges.restore)
        self.play(
            LaggedStartMap(
                GrowFromCenter, layer.neurons,
                run_time = 1
            ),
            LaggedStartMap(ShowCreation, edges),
            FadeOut(to_fade)
        )
        for x in range(3):
            for edges_out in all_edges_out:
                self.play(ShowCreationThenDestruction(edges_out))
        self.wait()

    ####

    def replace_subscript(self, label, tex):
        subscript = label[-1]
        new_subscript = TexMobject(tex)[0]
        new_subscript.replace(subscript, dim_to_match = 1)
        label.remove(subscript)
        label.add(new_subscript)
        return label

    def get_chain_rule(self, *tex):
        chain_rule = TexMobject(*tex)
        chain_rule.scale(0.8)
        chain_rule.to_corner(UP+LEFT)
        chain_rule.set_color_by_tex_to_color_map({
            "C_0" : self.cost_color,
            "z^" : self.z_color,
            "w^" : self.w_label.get_color()
        })
        return chain_rule

class ThatsPrettyMuchIt(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "That's pretty \\\\ much it!",
            target_mode = "hooray",
            run_time = 1,
        )
        self.wait(2)

class PatYourselfOnTheBack(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Pat yourself on \\\\ the back!",
            target_mode = "hooray"
        )
        self.change_student_modes(*["hooray"]*3)
        self.wait(3)

class ThatsALotToThinkAbout(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "That's a lot to \\\\ think about!",
            target_mode = "surprised"
        )
        self.change_student_modes(*["thinking"]*3)
        self.wait(4)

class LayersOfComplexity(Scene):
    def construct(self):
        chain_rule_equations = self.get_chain_rule_equations()
        chain_rule_equations.to_corner(UP+RIGHT)

        brace = Brace(chain_rule_equations, LEFT)
        arrow = Vector(LEFT, color = RED)
        arrow.next_to(brace, LEFT)
        gradient = TexMobject("\\nabla C")
        gradient.scale(2)
        gradient.set_color(RED)
        gradient.next_to(arrow, LEFT)

        self.play(LaggedStartMap(FadeIn, chain_rule_equations))
        self.play(GrowFromCenter(brace))
        self.play(GrowArrow(arrow))
        self.play(Write(gradient))
        self.wait()


    def get_chain_rule_equations(self):
        w_deriv = TexMobject(
            "{\\partial C", "\\over", "\\partial w^{(l)}_{jk}}",
            "=",
            "a^{(l-1)}_k",
            "\\sigma'(z^{(l)}_j)",
            "{\\partial C", "\\over", "\\partial a^{(l)}_j}",
        )
        lil_rect = SurroundingRectangle(
            VGroup(*w_deriv[-3:]),
            buff = 0.5*SMALL_BUFF
        )
        a_deriv = TexMobject(
            "\\sum_{j = 0}^{n_{l+1} - 1}",
            "w^{(l+1)}_{jk}",
            "\\sigma'(z^{(l+1)}_j)",
            "{\\partial C", "\\over", "\\partial a^{(l+1)}_j}",
        )
        or_word = TextMobject("or")
        last_a_deriv = TexMobject("2(a^{(L)}_j - y_j)")

        a_deriv.next_to(w_deriv, DOWN, LARGE_BUFF)
        or_word.next_to(a_deriv, DOWN)
        last_a_deriv.next_to(or_word, DOWN, MED_LARGE_BUFF)

        big_rect = SurroundingRectangle(VGroup(a_deriv, last_a_deriv))
        arrow = Arrow(
            lil_rect.get_corner(DOWN+LEFT), 
            big_rect.get_top(),
        )

        result = VGroup(
            w_deriv, lil_rect, arrow,
            big_rect, a_deriv, or_word, last_a_deriv
        )
        for expression in w_deriv, a_deriv, last_a_deriv:
            expression.set_color_by_tex_to_color_map({
                "C" : RED,
                "z^" : GREEN,
                "w^" : BLUE,
                "b^" : MAROON_B,
            })
        return result

class SponsorFrame(PiCreatureScene):
    def construct(self):
        morty = self.pi_creature
        screen = ScreenRectangle(height = 5)
        screen.to_corner(UP+LEFT)
        url = TextMobject("http://3b1b.co/crowdflower")
        url.move_to(screen, UP+LEFT)
        screen.shift(LARGE_BUFF*DOWN)
        arrow = Arrow(LEFT, RIGHT, color = WHITE)
        arrow.next_to(url, RIGHT)

        t_shirt_words = TextMobject("Free T-Shirt")
        t_shirt_words.scale(1.5)
        t_shirt_words.set_color(YELLOW)
        t_shirt_words.next_to(morty, UP, aligned_edge = RIGHT)

        human_in_the_loop = TextMobject("Human-in-the-loop approach")
        human_in_the_loop.next_to(screen, DOWN)

        self.play(
            morty.change, "hooray", t_shirt_words,
            Write(t_shirt_words, run_time = 2)
        )
        self.wait()
        self.play(
            morty.change, "raise_right_hand", screen,
            ShowCreation(screen)
        )
        self.play(
            t_shirt_words.scale, 1./1.5,
            t_shirt_words.next_to, arrow, RIGHT
        )
        self.play(Write(url))
        self.play(GrowArrow(arrow))
        self.wait(2)
        self.play(morty.change, "thinking", url)
        self.wait(3)
        self.play(Write(human_in_the_loop))
        self.play(morty.change, "happy", url)
        self.play(morty.look_at, screen)
        self.wait(7)
        t_shirt_words_outline = t_shirt_words.copy()
        t_shirt_words_outline.set_fill(opacity = 0)
        t_shirt_words_outline.set_stroke(GREEN, 3)
        self.play(
            morty.change, "hooray", t_shirt_words,
            LaggedStartMap(ShowCreation, t_shirt_words_outline),
        )
        self.play(FadeOut(t_shirt_words_outline))
        self.play(LaggedStartMap(
            Indicate, url,
            rate_func = wiggle,
            color = PINK,
            run_time = 3
        ))
        self.wait(3)

class NN3PatreonThanks(PatreonThanks):
    CONFIG = {
        "specific_patrons" : [
            "Randall Hunt",
            "Burt Humburg",
            "CrypticSwarm",
            "Juan Benet",
            "David Kedmey",
            "Michael Hardwicke",
            "Nathan Weeks",
            "Marcus Schiebold",
            "Ali Yahya",
            "William",
            "Mayank M. Mehrotra",
            "Lukas Biewald",
            "Samantha D. Suplee",
            "Yana Chernobilsky",
            "Kaustuv DeBiswas",
            "Kathryn Schmiedicke",
            "Yu Jun",
            "Dave Nicponski",
            "Damion Kistler",
            "Markus Persson",
            "Yoni Nazarathy",
            "Ed Kellett",
            "Joseph John Cox",
            "Luc Ritchie",
            "1stViewMaths",
            "Jacob Magnuson",
            "Mark Govea",
            "Dagan Harrington",
            "Clark Gaebel",
            "Eric Chow",
            "Mathias Jansson",
            "Robert Teed",
            "Pedro Perez Sanchez",
            "David Clark",
            "Michael Gardner",
            "Harsev Singh",
            "Mads Elvheim",
            "Erik Sundell",
            "Xueqi Li",
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
            "Jason Hise",
            "Meshal Alshammari",
            "Bernd Sing",
            "Mustafa Mahdi",
            "Mathew Bramson",
            "Jerry Ling",
            "Vecht",
            "Shimin Kuang",
            "Rish Kundalia",
            "Achille Brighton",
            "Ripta Pasay",
        ],
        "max_patron_group_size" : 25,
        "patron_scale_val" : 0.7,
    }

class Thumbnail(PreviewLearning):
    CONFIG = {
        "layer_sizes" : [8, 6, 6, 4],
        "network_mob_config" : {
            "neuron_radius" : 0.3,
            "neuron_to_neuron_buff" : MED_SMALL_BUFF,
            "include_output_labels" : False,
        },
        "stroke_width_exp" : 1,
        "max_stroke_width" : 5,
        "title" : "Backpropagation",
        "network_scale_val" : 0.8,
    }
    def construct(self):
        self.color_network_edges()
        network_mob = self.network_mob
        network_mob.scale(
            self.network_scale_val, 
            about_point = network_mob.get_bottom()
        )
        network_mob.activate_layers(np.random.random(self.layer_sizes[0]))

        for edge in it.chain(*network_mob.edge_groups):
            arrow = Arrow(
                edge.get_end(), edge.get_start(), 
                buff = 0,
                tip_length = 0.1,
                color = edge.get_color()
            )
            network_mob.add(arrow.tip)

        arrow = Vector(
            3*LEFT, 
            tip_length = 0.75, 
            rectangular_stem_width = 0.2,
            color = BLUE,
        )
        arrow.next_to(network_mob.edge_groups[1], UP, MED_LARGE_BUFF)

        network_mob.add(arrow)
        self.add(network_mob)

        title = TextMobject(self.title)
        title.scale(2)
        title.to_edge(UP)
        self.add(title)

class SupplementThumbnail(Thumbnail):
    CONFIG = {
        "title" : "Backpropagation \\\\ calculus",
        "network_scale_val" : 0.7,
    }
    def construct(self):
        Thumbnail.construct(self)
        self.network_mob.to_edge(DOWN, buff = MED_SMALL_BUFF)

        for layer in self.network_mob.layers:
            for neuron in layer.neurons:
                partial = TexMobject("\\partial")
                partial.move_to(neuron)
                self.remove(neuron)
                self.add(partial)




















