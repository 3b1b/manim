
import sys
import os.path
import cv2

from manimlib.imports import *

from nn.network import *
from nn.part1 import *

POSITIVE_COLOR = BLUE
NEGATIVE_COLOR = RED

def get_training_image_group(train_in, train_out):
    image = MNistMobject(train_in)
    image.set_height(1)
    arrow = Vector(RIGHT, color = BLUE, buff = 0)
    output = np.argmax(train_out)
    output_tex = TexMobject(str(output)).scale(1.5)
    result = Group(image, arrow, output_tex)
    result.arrange(RIGHT)
    result.to_edge(UP)
    return result

def get_decimal_vector(nums, with_dots = True):
    decimals = VGroup()
    for num in nums:
        decimal = DecimalNumber(num)
        if num > 0:
            decimal.set_color(POSITIVE_COLOR)
        else:
            decimal.set_color(NEGATIVE_COLOR)
        decimals.add(decimal)
    contents = VGroup(*decimals)
    if with_dots:
        dots = TexMobject("\\vdots")
        contents.submobjects.insert(len(decimals)/2, dots)
    contents.arrange(DOWN)
    lb, rb = brackets = TexMobject("\\big[", "\\big]")
    brackets.scale(2)
    brackets.stretch_to_fit_height(1.2*contents.get_height())
    lb.next_to(contents, LEFT, SMALL_BUFF)
    rb.next_to(contents, RIGHT, SMALL_BUFF)

    result = VGroup(lb, contents, brackets)
    result.lb = lb
    result.rb = rb
    result.brackets = brackets
    result.decimals = decimals
    result.contents = contents
    if with_dots:
        result.dots = dots
    return result


########

class ShowLastVideo(TeacherStudentsScene):
    def construct(self):
        frame = ScreenRectangle()
        frame.set_height(4.5)
        frame.to_corner(UP+LEFT)
        title = TextMobject("But what \\emph{is} a Neural Network")
        title.move_to(frame)
        title.to_edge(UP)
        frame.next_to(title, DOWN)

        assumption_words = TextMobject(
            "I assume you've\\\\ watched this"
        )
        assumption_words.move_to(frame)
        assumption_words.to_edge(RIGHT)
        arrow = Arrow(RIGHT, LEFT, color = BLUE)
        arrow.next_to(assumption_words, LEFT)


        self.play(
            ShowCreation(frame),
            self.teacher.change, "raise_right_hand"
        )
        self.play(
            Write(title),
            self.get_student_changes(*["thinking"]*3)
        )
        self.play(
            Animation(title),
            GrowArrow(arrow),
            FadeIn(assumption_words)
        )
        self.wait(5)

class ShowPlan(Scene):
    def construct(self):
        title = TextMobject("Plan").scale(1.5)
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS)
        h_line.set_color(WHITE)
        h_line.next_to(title, DOWN)
        self.add(title, h_line)

        items = VGroup(*[
            TextMobject("$\\cdot$ %s"%s)
            for s in [
                "Recap",
                "Gradient descent",
                "Analyze this network",
                "Where to learn more",
                "Research corner",
            ]
        ])
        items.arrange(DOWN, buff = MED_LARGE_BUFF, aligned_edge = LEFT)
        items.to_edge(LEFT, buff = LARGE_BUFF)

        rect = SurroundingRectangle(VGroup(*items[1:3]))

        self.add(items)
        self.wait()
        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))
        for item in items[1:]:
            to_fade = VGroup(*[i for i in items if i is not item])
            self.play(
                to_fade.set_fill, None, 0.5,
                item.set_fill, None, 1,
            )
            self.wait()

class BeginAndEndRecap(Scene):
    def construct(self):
        recap = TexMobject(
            "\\langle", "\\text{Recap}", "\\rangle"
        )
        new_langle = TexMobject("\\langle/")
        new_langle.scale(2)
        recap.scale(2)
        new_langle.move_to(recap[0], RIGHT)

        self.add(recap)
        self.wait(2)
        self.play(Transform(recap[0], new_langle))
        self.wait(2)

class PreviewLearning(NetworkScene):
    CONFIG = {
        "layer_sizes" : DEFAULT_LAYER_SIZES,
        "network_mob_config" : {
            "neuron_to_neuron_buff" : SMALL_BUFF,
            "layer_to_layer_buff" : 2,
            "edge_stroke_width" : 1,
            "neuron_stroke_color" : WHITE,
            "neuron_stroke_width" : 2,
            "neuron_fill_color" : WHITE,
            "average_shown_activation_of_large_layer" : False,
            "edge_propogation_color" : GREEN,
            "edge_propogation_time" : 2,
            "include_output_labels" : True,
        },
        "n_examples" : 15,
        "max_stroke_width" : 3,
        "stroke_width_exp" : 3,
        "eta" : 3.0,
        "positive_edge_color" : BLUE,
        "negative_edge_color" : RED,
        "positive_change_color" : BLUE_C,
        "negative_change_color" : average_color(*2*[RED] + [YELLOW]),
        "default_activate_run_time" : 1.5,
    }
    def construct(self):
        self.initialize_network()
        self.add_training_words()
        self.show_training()

    def initialize_network(self):
        self.network_mob.scale(0.7)
        self.network_mob.to_edge(DOWN)
        self.color_network_edges()

    def add_training_words(self):
        words = TextMobject("Training in \\\\ progress$\\dots$")
        words.scale(1.5)
        words.to_corner(UP+LEFT)

        self.add(words)

    def show_training(self):
        training_data, validation_data, test_data = load_data_wrapper()
        for train_in, train_out in training_data[:self.n_examples]:
            image = get_training_image_group(train_in, train_out)
            self.activate_network(train_in, FadeIn(image))
            self.backprop_one_example(
                train_in, train_out, 
                FadeOut(image), self.network_mob.layers.restore
            )

    def activate_network(self, train_in, *added_anims, **kwargs):
        network_mob = self.network_mob
        layers = network_mob.layers
        layers.save_state()
        activations = self.network.get_activation_of_all_layers(train_in)
        active_layers = [
            self.network_mob.get_active_layer(i, vect)
            for i, vect in enumerate(activations)
        ]
        all_edges = VGroup(*it.chain(*network_mob.edge_groups))
        run_time = kwargs.get("run_time", self.default_activate_run_time)
        edge_animation = LaggedStartMap(
            ShowCreationThenDestruction, 
            all_edges.copy().set_fill(YELLOW),
            run_time = run_time,
            lag_ratio = 0.3,
            remover = True,
        )
        layer_animation = Transform(
            VGroup(*layers), VGroup(*active_layers),
            run_time = run_time,
            lag_ratio = 0.5,
            rate_func=linear,
        )

        self.play(edge_animation, layer_animation, *added_anims)

    def backprop_one_example(self, train_in, train_out, *added_outro_anims):
        network_mob = self.network_mob
        nabla_b, nabla_w = self.network.backprop(train_in, train_out)
        neuron_groups = VGroup(*[
            layer.neurons
            for layer in network_mob.layers[1:]
        ])
        delta_neuron_groups = neuron_groups.copy()
        edge_groups = network_mob.edge_groups
        delta_edge_groups = VGroup(*[
            edge_group.copy()
            for edge_group in edge_groups
        ])
        tups = list(zip(
            it.count(), nabla_b, nabla_w, 
            delta_neuron_groups, neuron_groups,
            delta_edge_groups, edge_groups
        ))
        pc_color = self.positive_change_color
        nc_color = self.negative_change_color
        for i, nb, nw, delta_neurons, neurons, delta_edges, edges in reversed(tups):
            shown_nw = self.get_adjusted_first_matrix(nw)
            if np.max(shown_nw) == 0:
                shown_nw = (2*np.random.random(shown_nw.shape)-1)**5
            max_b = np.max(np.abs(nb))
            max_w = np.max(np.abs(shown_nw))
            for neuron, b in zip(delta_neurons, nb):
                color = nc_color if b > 0 else pc_color
                # neuron.set_fill(color, abs(b)/max_b)
                neuron.set_stroke(color, 3)
            for edge, w in zip(delta_edges.split(), shown_nw.T.flatten()):
                edge.set_stroke(
                    nc_color if w > 0 else pc_color,
                    3*abs(w)/max_w
                )
                edge.rotate_in_place(np.pi)
            if i == 2:
                delta_edges.submobjects = [
                    delta_edges[j]
                    for j in np.argsort(shown_nw.T.flatten())
                ]
            network = self.network
            network.weights[i] -= self.eta*nw
            network.biases[i] -= self.eta*nb

            self.play(
                ShowCreation(
                    delta_edges, lag_ratio = 0
                ),
                FadeIn(delta_neurons),
                run_time = 0.5
            )
        edge_groups.save_state()
        self.color_network_edges()
        self.remove(edge_groups)
        self.play(*it.chain(
            [ReplacementTransform(
                edge_groups.saved_state, edge_groups,
            )],
            list(map(FadeOut, [delta_edge_groups, delta_neuron_groups])),
            added_outro_anims,
        ))

    #####

    def get_adjusted_first_matrix(self, matrix):
        n = self.network_mob.max_shown_neurons
        if matrix.shape[1] > n:
            half = matrix.shape[1]/2
            return matrix[:,half-n/2:half+n/2]
        else:
            return matrix

    def color_network_edges(self):
        layers = self.network_mob.layers
        weight_matrices = self.network.weights
        for layer, matrix in zip(layers[1:], weight_matrices):
            matrix = self.get_adjusted_first_matrix(matrix)
            matrix_max = np.max(matrix)
            for neuron, row in zip(layer.neurons, matrix):
                for edge, w in zip(neuron.edges_in, row):
                    if w > 0:
                        color = self.positive_edge_color
                    else:
                        color = self.negative_edge_color
                    msw = self.max_stroke_width
                    swe = self.stroke_width_exp
                    sw = msw*(abs(w)/matrix_max)**swe
                    sw = min(sw, msw)
                    edge.set_stroke(color, sw)

    def get_edge_animation(self):
        edges = VGroup(*it.chain(*self.network_mob.edge_groups))
        return LaggedStartMap(
            ApplyFunction, edges,
            lambda mob : (
                lambda m : m.rotate_in_place(np.pi/12).set_color(YELLOW),
                mob
            ),
            rate_func = wiggle
        )

class BackpropComingLaterWords(Scene):
    def construct(self):
        words = TextMobject("(Backpropagation be \\\\ the next video)")
        words.set_width(FRAME_WIDTH-1)
        words.to_edge(DOWN)
        self.add(words)

class TrainingVsTestData(Scene):
    CONFIG = {
        "n_examples" : 10,
        "n_new_examples_shown" : 10,
    }
    def construct(self):
        self.initialize_data()
        self.introduce_all_data()
        self.subdivide_into_training_and_testing()
        self.scroll_through_much_data()

    def initialize_data(self):
        training_data, validation_data, test_data = load_data_wrapper()
        self.data = training_data
        self.curr_index = 0

    def get_examples(self):
        ci = self.curr_index
        self.curr_index += self.n_examples
        group = Group(*it.starmap(
            get_training_image_group,
            self.data[ci:ci+self.n_examples]
        ))
        group.arrange(DOWN)
        group.scale(0.5)
        return group

    def introduce_all_data(self):
        training_examples, test_examples = [
            self.get_examples() for x in range(2)
        ]

        training_examples.next_to(ORIGIN, LEFT)
        test_examples.next_to(ORIGIN, RIGHT)
        self.play(
            LaggedStartMap(FadeIn, training_examples),
            LaggedStartMap(FadeIn, test_examples),
        )

        self.training_examples = training_examples
        self.test_examples = test_examples

    def subdivide_into_training_and_testing(self):
        training_examples = self.training_examples
        test_examples = self.test_examples
        for examples in training_examples, test_examples:
            examples.generate_target()
        training_examples.target.shift(2*LEFT)
        test_examples.target.shift(2*RIGHT)

        train_brace = Brace(training_examples.target, LEFT)
        train_words = train_brace.get_text("Train on \\\\ these")
        test_brace = Brace(test_examples.target, RIGHT)
        test_words = test_brace.get_text("Test on \\\\ these")

        bools = [True]*(len(test_examples)-1) + [False]
        random.shuffle(bools)
        marks = VGroup()
        for is_correct, test_example in zip(bools, test_examples.target):
            if is_correct:
                mark = TexMobject("\\checkmark")
                mark.set_color(GREEN)
            else:
                mark = TexMobject("\\times")
                mark.set_color(RED)
            mark.next_to(test_example, LEFT)
            marks.add(mark)

        self.play(
            MoveToTarget(training_examples),
            GrowFromCenter(train_brace),
            FadeIn(train_words)
        )
        self.wait()
        self.play(
            MoveToTarget(test_examples),
            GrowFromCenter(test_brace),
            FadeIn(test_words)
        )
        self.play(Write(marks))
        self.wait()

    def scroll_through_much_data(self):
        training_examples = self.training_examples
        colors = color_gradient([BLUE, YELLOW], self.n_new_examples_shown)
        for color in colors:
            new_examples = self.get_examples()
            new_examples.move_to(training_examples)
            for train_ex, new_ex in zip(training_examples, new_examples):
                self.remove(train_ex)
                self.add(new_ex)
                new_ex[0][0].set_color(color)
                self.wait(1./30)
            training_examples = new_examples

class MNistDescription(Scene):
    CONFIG = {
        "n_grids" : 5,
        "n_rows_per_grid" : 10,
        "n_cols_per_grid" : 8,
        "time_per_example" : 1./120,
    }
    def construct(self):
        title = TextMobject("MNIST Database")
        title.scale(1.5)
        title.set_color(BLUE)
        authors = TextMobject("LeCun, Cortes and Burges")
        authors.next_to(title, DOWN)
        link_words = TextMobject("(links in the description)")
        link_words.next_to(authors, DOWN, MED_LARGE_BUFF)
        arrows = VGroup(*[Vector(DOWN) for x in range(4)])
        arrows.arrange(RIGHT, buff = LARGE_BUFF)
        arrows.next_to(link_words, DOWN)
        arrows.set_color(BLUE)

        word_group = VGroup(title, authors, link_words, arrows)
        word_group.center()

        self.add(title, authors)
        self.play(
            Write(link_words, run_time = 2),
            LaggedStartMap(GrowArrow, arrows),
        )
        self.wait()

        training_data, validation_data, test_data = load_data_wrapper()
        epc = self.n_rows_per_grid*self.n_cols_per_grid
        training_data_groups = [
            training_data[i*epc:(i+1)*epc]
            for i in range(self.n_grids)
        ]

        for i, td_group in enumerate(training_data_groups):
            print(i)
            group = Group(*[
                self.get_digit_pair(v_in, v_out)
                for v_in, v_out in td_group
            ])
            group.arrange_in_grid(
                n_rows = self.n_rows_per_grid,
            )
            group.set_height(FRAME_HEIGHT - 1)
            if i == 0:
                self.play(
                    LaggedStartMap(FadeIn, group),
                    FadeOut(word_group),
                )
            else:
                pairs = list(zip(last_group, group))
                random.shuffle(pairs)
                time = 0
                for t1, t2 in pairs:
                    time += self.time_per_example
                    self.remove(t1)
                    self.add(t2)
                    if time > self.frame_duration:
                        self.wait(self.frame_duration)
                        time = 0
            last_group = group


    def get_digit_pair(self, v_in, v_out):
        tup = Group(*TexMobject("(", "00", ",", "0", ")"))
        tup.scale(2)
        # image = PixelsFromVect(v_in)
        # image.add(SurroundingRectangle(image, color = BLUE, buff = SMALL_BUFF))
        image = MNistMobject(v_in)
        label = TexMobject(str(np.argmax(v_out)))
        image.replace(tup[1])
        tup.submobjects[1] = image
        label.replace(tup[3], dim_to_match = 1)
        tup.submobjects[3] = label

        return tup

class NotSciFi(TeacherStudentsScene):
    def construct(self):
        students = self.students
        self.student_says(
            "Machines learning?!?",
            student_index = 0,
            target_mode = "pleading",
            run_time = 1,
        )
        bubble = students[0].bubble
        students[0].bubble = None
        self.student_says(
            "Should we \\\\ be worried?", student_index = 2,
            target_mode = "confused",
            bubble_kwargs = {"direction" : LEFT},
            run_time = 1,
        )
        self.wait()
        students[0].bubble = bubble
        self.teacher_says(
            "It's actually \\\\ just calculus.",
            run_time = 1
        )
        self.teacher.bubble = None
        self.wait()
        self.student_says(
            "Even worse!", 
            target_mode = "horrified",
            bubble_kwargs = {
                "direction" : LEFT, 
                "width" : 3,
                "height" : 2,
            },
        )
        self.wait(2)

class FunctionMinmization(GraphScene):
    CONFIG = {
        "x_labeled_nums" : list(range(-1, 10)),
    }
    def construct(self):
        self.setup_axes()
        title = TextMobject("Finding minima")
        title.to_edge(UP)
        self.add(title)

        def func(x):
            x -= 4.5
            return 0.03*(x**4 - 16*x**2) + 0.3*x + 4
        graph = self.get_graph(func)
        graph_label = self.get_graph_label(graph, "C(x)")
        self.add(graph, graph_label)

        dots = VGroup(*[
            Dot().move_to(self.input_to_graph_point(x, graph))
            for x in range(10)
        ])
        dots.set_color_by_gradient(YELLOW, RED)

        def update_dot(dot, dt):
            x = self.x_axis.point_to_number(dot.get_center())
            slope = self.slope_of_tangent(x, graph)
            x -= slope*dt
            dot.move_to(self.input_to_graph_point(x, graph))

        self.add(*[
            Mobject.add_updater(dot, update_dot)
            for dot in dots
        ])
        self.wait(10)

class ChangingDecimalWithColor(ChangingDecimal):
    def interpolate_mobject(self, alpha):
        ChangingDecimal.interpolate_mobject(self, alpha)
        num = self.number_update_func(alpha)
        self.decimal_number.set_fill(
            interpolate_color(BLACK, WHITE, 0.5+num*0.5), 
            opacity = 1
        )

class IntroduceCostFunction(PreviewLearning):
    CONFIG = {
        "max_stroke_width" : 2,
        "full_edges_exp" : 5,
        "n_training_examples" : 100,
        "bias_color" : MAROON_B
    }
    def construct(self):
        self.network_mob.shift(LEFT)
        self.isolate_one_neuron()
        self.reminder_of_weights_and_bias()
        self.bring_back_rest_of_network()
        self.feed_in_example()
        self.make_fun_of_output()
        self.need_a_cost_function()
        self.fade_all_but_last_layer()
        self.break_down_cost_function()
        self.show_small_cost_output()
        self.average_over_all_training_data()

    def isolate_one_neuron(self):
        network_mob = self.network_mob
        neurons = VGroup(*it.chain(*[
            layer.neurons
            for layer in network_mob.layers[1:]
        ]))
        edges = VGroup(*it.chain(*network_mob.edge_groups))
        neuron = network_mob.layers[1].neurons[7]
        neurons.remove(neuron)
        edges.remove(*neuron.edges_in)
        output_labels = network_mob.output_labels
        kwargs = {
            "lag_ratio" : 0.5,
            "run_time" : 2,
        }
        self.play(
            FadeOut(edges, **kwargs),
            FadeOut(neurons, **kwargs),
            FadeOut(output_labels, **kwargs),
            Animation(neuron),
            neuron.edges_in.set_stroke, None, 2,
        )

        self.neuron = neuron

    def reminder_of_weights_and_bias(self):
        neuron = self.neuron
        layer0 = self.network_mob.layers[0]
        active_layer0 = self.network_mob.get_active_layer(
            0, np.random.random(len(layer0.neurons))
        )
        prev_neurons = layer0.neurons

        weighted_edges = VGroup(*[
            self.color_edge_randomly(edge.copy(), exp = 1)
            for edge in neuron.edges_in
        ])

        formula = TexMobject(
            "=", "\\sigma(",
            "w_1", "a_1", "+",
            "w_2", "a_2", "+",
            "\\cdots", "+",
            "w_n", "a_n", "+", "b", ")"
        )
        w_labels = formula.get_parts_by_tex("w_")
        a_labels = formula.get_parts_by_tex("a_")
        b = formula.get_part_by_tex("b")
        sigma = VGroup(
            formula.get_part_by_tex("\\sigma"),
            formula.get_part_by_tex(")"),
        )
        symbols = VGroup(*[
            formula.get_parts_by_tex(tex)
            for tex in ("=", "+", "dots")
        ])

        w_labels.set_color(self.positive_edge_color)
        b.set_color(self.bias_color)
        sigma.set_color(YELLOW)
        formula.next_to(neuron, RIGHT)

        weights_word = TextMobject("Weights")
        weights_word.next_to(neuron.edges_in, RIGHT, aligned_edge = UP)
        weights_word.set_color(self.positive_edge_color)
        weights_arrow_to_edges = Arrow(
            weights_word.get_bottom(),
            neuron.edges_in[0].get_center(),
            color = self.positive_edge_color
        )

        weights_arrow_to_syms = VGroup(*[
            Arrow(
                weights_word.get_bottom(),
                w_label.get_top(),
                color = self.positive_edge_color
            )
            for w_label in w_labels
        ])

        bias_word = TextMobject("Bias")
        bias_arrow = Vector(DOWN, color = self.bias_color)
        bias_arrow.next_to(b, UP, SMALL_BUFF)
        bias_word.next_to(bias_arrow, UP, SMALL_BUFF)
        bias_word.set_color(self.bias_color)

        self.play(
            Transform(layer0, active_layer0),
            neuron.set_fill, None, 0.5,
            FadeIn(formula),
            run_time = 2,
            lag_ratio = 0.5
        )
        self.play(LaggedStartMap(
            ShowCreationThenDestruction, 
            neuron.edges_in.copy().set_stroke(YELLOW, 3),
            run_time = 1.5,
            lag_ratio = 0.7,
            remover = True
        ))
        self.play(
            Write(weights_word),
            *list(map(GrowArrow, weights_arrow_to_syms)),
            run_time = 1
        )
        self.wait()
        self.play(
            ReplacementTransform(
                w_labels.copy(), weighted_edges,
                remover = True
            ),
            Transform(neuron.edges_in, weighted_edges),
            ReplacementTransform(
                weights_arrow_to_syms,
                VGroup(weights_arrow_to_edges),
            )
        )
        self.wait()
        self.play(
            Write(bias_word),
            GrowArrow(bias_arrow),
            run_time = 1
        )
        self.wait(2)

        ## Initialize randomly
        w_random = TextMobject("Initialize randomly")
        w_random.move_to(weights_word, LEFT)
        b_random = w_random.copy()
        b_random.move_to(bias_word, RIGHT)

        self.play(
            Transform(weights_word, w_random),
            Transform(bias_word, b_random),
            *[
                ApplyFunction(self.color_edge_randomly, edge)
                for edge in neuron.edges_in
            ]
        )
        self.play(LaggedStartMap(
            ApplyMethod, neuron.edges_in,
            lambda m : (m.rotate_in_place, np.pi/12),
            rate_func = wiggle,
            run_time = 2
        ))
        self.play(*list(map(FadeOut, [
            weights_word, weights_arrow_to_edges,
            bias_word, bias_arrow,
            formula
        ])))

    def bring_back_rest_of_network(self):
        network_mob = self.network_mob
        neurons = VGroup(*network_mob.layers[1].neurons)
        neurons.remove(self.neuron)
        for layer in network_mob.layers[2:]:
            neurons.add(*layer.neurons)
        neurons.add(*network_mob.output_labels)

        edges = VGroup(*network_mob.edge_groups[0])
        edges.remove(*self.neuron.edges_in)
        for edge_group in network_mob.edge_groups[1:]:
            edges.add(*edge_group)

        for edge in edges:
            self.color_edge_randomly(edge, exp = self.full_edges_exp)

        self.play(*[
            LaggedStartMap(
                FadeIn, group,
                run_time = 3,
            )
            for group in (neurons, edges)
        ])

    def feed_in_example(self):
        vect = get_organized_images()[3][5]
        image = PixelsFromVect(vect)
        image.to_corner(UP+LEFT)
        rect = SurroundingRectangle(image, color = BLUE)
        neurons = VGroup(*[
            Circle(
                stroke_width = 1,
                stroke_color = WHITE,
                fill_opacity = pixel.fill_rgb[0],
                fill_color = WHITE,
                radius = pixel.get_height()/2
            ).move_to(pixel)
            for pixel in image
        ])
        layer0= self.network_mob.layers[0]
        n = self.network_mob.max_shown_neurons
        neurons.target = VGroup(*it.chain(
            VGroup(*layer0.neurons[:n/2]).set_fill(opacity = 0),
            [
                VectorizedPoint(layer0.dots.get_center())
                for x in range(len(neurons)-n)
            ],
            VGroup(*layer0.neurons[-n/2:]).set_fill(opacity = 0),
        ))

        self.play(
            self.network_mob.shift, 0.5*RIGHT,
            ShowCreation(rect),
            LaggedStartMap(DrawBorderThenFill, image),
            LaggedStartMap(DrawBorderThenFill, neurons),
            run_time = 1
        )
        self.play(
            MoveToTarget(
                neurons, lag_ratio = 0.5,
                remover = True
            ),
            layer0.neurons.set_fill, None, 0,
        )
        self.activate_network(vect, run_time = 2)

        self.image = image
        self.image_rect = rect

    def make_fun_of_output(self):
        last_layer = self.network_mob.layers[-1].neurons
        last_layer.add(self.network_mob.output_labels)
        rect = SurroundingRectangle(last_layer)
        words = TextMobject("Utter trash")
        words.next_to(rect, DOWN, aligned_edge = LEFT)
        VGroup(rect, words).set_color(YELLOW)

        self.play(
            ShowCreation(rect),
            Write(words, run_time = 2)
        )
        self.wait()

        self.trash_rect = rect
        self.trash_words = words

    def need_a_cost_function(self):
        vect = np.zeros(10)
        vect[3] = 1
        output_labels = self.network_mob.output_labels
        desired_layer = self.network_mob.get_active_layer(-1, vect)
        layer = self.network_mob.layers[-1]
        layer.add(output_labels)
        desired_layer.add(output_labels.copy())
        desired_layer.shift(2*RIGHT)
        layers = VGroup(layer, desired_layer)

        words = TextMobject(
            "What's the", "``cost''\\\\", "of this difference?",
        )
        words.set_color_by_tex("cost", RED)
        words.next_to(layers, UP)
        words.to_edge(UP)
        words.shift_onto_screen()
        double_arrow = DoubleArrow(
            layer.get_right(),
            desired_layer.get_left(),
            color = RED
        )

        self.play(FadeIn(words))
        self.play(ReplacementTransform(layer.copy(), desired_layer))
        self.play(GrowFromCenter(double_arrow))
        self.wait(2)

        self.desired_last_layer = desired_layer
        self.diff_arrow = double_arrow

    def fade_all_but_last_layer(self):
        network_mob = self.network_mob
        to_fade = VGroup(*it.chain(*list(zip(
            network_mob.layers[:-1],
            network_mob.edge_groups
        ))))

        self.play(LaggedStartMap(FadeOut, to_fade, run_time = 1))

    def break_down_cost_function(self):
        layer = self.network_mob.layers[-1]
        desired_layer = self.desired_last_layer
        decimal_groups = VGroup(*[
            self.num_vect_to_decimals(self.layer_to_num_vect(l))
            for l in (layer, desired_layer)
        ])

        terms = VGroup()
        symbols = VGroup()
        for d1, d2 in zip(*decimal_groups):
            term = TexMobject(
                "(", "0.00", "-", "0.00", ")^2", "+",
            )
            term.scale(d1.get_height()/term[1].get_height())
            for d, i in (d1, 1), (d2, 3):
                term.submobjects[i] = d.move_to(term[i])
            terms.add(term)
            symbols.add(*term)
            symbols.remove(d1, d2)
            last_plus = term[-1]
        for mob in terms[-1], symbols:
            mob.remove(last_plus)
        terms.arrange(
            DOWN, buff = SMALL_BUFF,
            aligned_edge = LEFT
        )
        terms.set_height(1.5*layer.get_height())
        terms.next_to(layer, LEFT, buff = 2)

        image_group = Group(self.image, self.image_rect)
        image_group.generate_target()
        image_group.target.scale(0.5)
        cost_of = TextMobject("Cost of").set_color(RED)
        cost_group = VGroup(cost_of, image_group.target)
        cost_group.arrange(RIGHT)
        brace = Brace(terms, LEFT)
        cost_group.next_to(brace, LEFT)

        self.revert_to_original_skipping_status()
        self.play(*[
            ReplacementTransform(
                VGroup(*l.neurons[:10]).copy(), dg
            )
            for l, dg in zip([layer, desired_layer], decimal_groups)
        ])
        self.play(
            FadeIn(symbols),
            MoveToTarget(image_group),
            FadeIn(cost_of),
            GrowFromCenter(brace),
        )
        self.wait()

        self.decimal_groups = decimal_groups
        self.image_group = image_group
        self.cost_group = VGroup(cost_of, image_group)
        self.brace = brace

    def show_small_cost_output(self):
        decimals, desired_decimals = self.decimal_groups
        neurons = self.network_mob.layers[-1].neurons
        brace = self.brace
        cost_group = self.cost_group

        neurons.save_state()
        cost_group.save_state()
        brace.save_state()
        brace.generate_target()

        arrows = VGroup(*[
            Arrow(ORIGIN, LEFT).next_to(d, LEFT, MED_LARGE_BUFF)
            for d in decimals
        ])
        arrows.set_color(WHITE)

        def generate_term_update_func(decimal, desired_decimal):
            return lambda a : (decimal.number - desired_decimal.number)**2

        terms = VGroup()
        term_updates = []
        for arrow, d1, d2 in zip(arrows, *self.decimal_groups):
            term = DecimalNumber(0, num_decimal_places = 4)
            term.set_height(d1.get_height())
            term.next_to(arrow, LEFT)
            term.num_update_func = generate_term_update_func(d1, d2)
            terms.add(term)
            term_updates.append(ChangingDecimalWithColor(
                term, term.num_update_func,
                num_decimal_places = 4
            ))
        brace.target.next_to(terms, LEFT)

        sum_term = DecimalNumber(0)
        sum_term.next_to(brace.target, LEFT)
        sum_term.set_color(RED)
        def sum_update(alpha):
            return sum([
                (d1.number - d2.number)**2
                for d1, d2 in zip(*self.decimal_groups)
            ])
        term_updates.append(ChangingDecimal(sum_term, sum_update))
        for update in term_updates:
            update.interpolate_mobject(0)

        target_vect = 0.1*np.random.random(10)
        target_vect[3] = 0.97

        def generate_decimal_update_func(start, target):
            return lambda a : interpolate(start, target, a)

        update_decimals = [
            ChangingDecimalWithColor(
                decimal, 
                generate_decimal_update_func(decimal.number, t)
            )
            for decimal, t in zip(decimals, target_vect)
        ]

        self.play(
            cost_group.scale, 0.5,
            cost_group.to_corner, UP+LEFT,
            MoveToTarget(brace),
            LaggedStartMap(GrowArrow, arrows),
            LaggedStartMap(FadeIn, terms),
            FadeIn(sum_term),
            Animation(decimals)
        )
        self.play(*it.chain(
            update_decimals,
            term_updates,
            [
                ApplyMethod(neuron.set_fill, None, t)
                for neuron, t in zip(neurons, target_vect)
            ]
        ))
        self.wait()
        self.play(LaggedStartMap(Indicate, decimals, rate_func = there_and_back))
        self.wait()
        for update in update_decimals:
            update.rate_func = lambda a : smooth(1-a)
        self.play(*it.chain(
            update_decimals,
            term_updates,
            [neurons.restore]
        ), run_time = 2)
        self.wait()
        self.play(
            cost_group.restore,
            brace.restore,
            FadeOut(VGroup(terms, sum_term, arrows)),
        )

    def average_over_all_training_data(self):
        image_group = self.image_group
        decimal_groups = self.decimal_groups

        random_neurons = self.network_mob.layers[-1].neurons
        desired_neurons = self.desired_last_layer.neurons

        wait_times = iter(it.chain(
            4*[0.5],
            4*[0.25],
            8*[0.125],
            it.repeat(0.1)
        ))

        words = TextMobject("Average cost of \\\\ all training data...")
        words.set_color(BLUE)
        words.to_corner(UP+LEFT)

        self.play(
            Write(words, run_time = 1),
        )

        training_data, validation_data, test_data = load_data_wrapper()
        for in_vect, out_vect in training_data[:self.n_training_examples]:
            random_v = np.random.random(10)
            new_decimal_groups = VGroup(*[
                self.num_vect_to_decimals(v)
                for v in (random_v, out_vect)
            ])
            for ds, nds in zip(decimal_groups, new_decimal_groups):
                for old_d, new_d in zip(ds, nds):
                    new_d.replace(old_d)
            self.remove(decimal_groups)
            self.add(new_decimal_groups)
            decimal_groups = new_decimal_groups
            for pair in (random_v, random_neurons), (out_vect, desired_neurons):
                for n, neuron in zip(*pair):
                    neuron.set_fill(opacity = n)
            new_image_group = MNistMobject(in_vect)
            new_image_group.replace(image_group)
            self.remove(image_group)
            self.add(new_image_group)
            image_group = new_image_group

            self.wait(next(wait_times))

    ####

    def color_edge_randomly(self, edge, exp = 1):
        r = (2*np.random.random()-1)**exp
        r *= self.max_stroke_width
        pc, nc = self.positive_edge_color, self.negative_edge_color
        edge.set_stroke(
            color = pc if r > 0 else nc,
            width = abs(r),
        )
        return edge

    def layer_to_num_vect(self, layer, n_terms = 10):
        return [
            n.get_fill_opacity()
            for n in layer.neurons
        ][:n_terms]

    def num_vect_to_decimals(self, num_vect):
        return VGroup(*[
            DecimalNumber(n).set_fill(opacity = 0.5*n + 0.5)
            for n in num_vect
        ])

    def num_vect_to_column_vector(self, num_vect, height):
        decimals = VGroup(*[
            DecimalNumber(n).set_fill(opacity = 0.5*n + 0.5)
            for n in num_vect
        ])
        decimals.arrange(DOWN)
        decimals.set_height(height)
        lb, rb = brackets = TexMobject("[]")
        brackets.scale(2)
        brackets.stretch_to_fit_height(height + SMALL_BUFF)
        lb.next_to(decimals, LEFT)
        rb.next_to(decimals, RIGHT)
        result = VGroup(brackets, decimals)
        result.brackets = brackets
        result.decimals = decimals
        return result

class YellAtNetwork(PiCreatureScene, PreviewLearning):
    def setup(self):
        PiCreatureScene.setup(self)
        PreviewLearning.setup(self)

    def construct(self):
        randy = self.randy
        network_mob, eyes = self.get_network_and_eyes()

        three_vect = get_organized_images()[3][5]
        self.activate_network(three_vect)

        image = PixelsFromVect(three_vect)
        image.add(SurroundingRectangle(image, color = BLUE))
        arrow = Arrow(LEFT, RIGHT, color = WHITE)

        layer = network_mob.layers[-1]
        layer.add(network_mob.output_labels)
        layer_copy = layer.deepcopy()
        for neuron in layer_copy.neurons:
            neuron.set_fill(WHITE, opacity = 0)
        layer_copy.neurons[3].set_fill(WHITE, 1)
        layer_copy.scale(1.5)
        desired = Group(image, arrow, layer_copy)
        desired.arrange(RIGHT)
        desired.to_edge(UP)

        q_marks = TexMobject("???").set_color(RED)
        q_marks.next_to(arrow, UP, SMALL_BUFF)

        self.play(
            PiCreatureBubbleIntroduction(
                randy, "Bad network!",
                target_mode = "angry", 
                look_at_arg = eyes,
                run_time = 1,
            ),
            eyes.look_at_anim(randy.eyes)
        )
        self.play(eyes.change_mode_anim("sad"))
        self.play(eyes.look_at_anim(3*DOWN + 3*RIGHT))
        self.play(
            FadeIn(desired),
            RemovePiCreatureBubble(
                randy, target_mode = "sassy",
                look_at_arg = desired
            ),
            eyes.look_at_anim(desired)
        )
        self.play(eyes.blink_anim())
        rect = SurroundingRectangle(
            VGroup(layer_copy.neurons[3], layer_copy[-1][3]),
        )
        self.play(ShowCreation(rect))
        layer_copy.add(rect)
        self.wait()
        self.play(
            layer.copy().replace, layer_copy, 1,
            Write(q_marks, run_time = 1),
            layer_copy.shift, 1.5*RIGHT,
            randy.change, "angry", eyes,
        )
        self.play(eyes.look_at_anim(3*RIGHT + 3*RIGHT))
        self.wait()

    ####

    def get_network_and_eyes(self):
        randy = self.randy
        network_mob = self.network_mob
        network_mob.scale(0.5)
        network_mob.next_to(randy, RIGHT, LARGE_BUFF)
        self.color_network_edges()
        eyes = Eyes(network_mob.edge_groups[1])
        return network_mob, eyes

    def create_pi_creature(self):
        randy = self.randy = Randolph()
        randy.shift(3*LEFT).to_edge(DOWN)
        return randy

class ThisIsVeryComplicated(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Very complicated!",
            target_mode = "surprised",
            run_time = 1,
        )
        self.change_student_modes(*3*["guilty"])
        self.wait(2)

class EmphasizeComplexityOfCostFunction(IntroduceCostFunction):
    CONFIG = {
        "stroke_width_exp" : 3,
        "n_examples" : 32,
    }
    def construct(self):
        self.setup_sides()
        self.show_network_as_a_function()
        self.show_cost_function()

    def setup_sides(self):
        v_line = Line(UP, DOWN).scale(FRAME_Y_RADIUS)
        network_mob = self.network_mob
        network_mob.set_width(FRAME_X_RADIUS - 1)
        network_mob.to_corner(DOWN+LEFT)

        self.add(v_line)
        self.color_network_edges()

    def show_network_as_a_function(self):
        title = TextMobject("Neural network function")
        title.shift(FRAME_X_RADIUS*RIGHT/2)
        title.to_edge(UP)
        underline = Line(LEFT, RIGHT)
        underline.stretch_to_fit_width(title.get_width())
        underline.next_to(title, DOWN, SMALL_BUFF)
        self.add(title, underline)

        words = self.get_function_description_words(
            "784 numbers (pixels)",
            "10 numbers",
            "13{,}002 weights/biases",
        )
        input_words, output_words, parameter_words = words
        for word in words:
            self.add(word[0])

        in_vect = get_organized_images()[7][8]
        activations = self.network.get_activation_of_all_layers(in_vect)
        image = MNistMobject(in_vect)
        image.set_height(1.5)
        image_label = TextMobject("Input")
        image_label.set_color(input_words[0].get_color())
        image_label.next_to(image, UP, SMALL_BUFF)

        arrow = Arrow(LEFT, RIGHT, color = WHITE)
        arrow.next_to(image, RIGHT)
        output = self.num_vect_to_column_vector(activations[-1], 2)
        output.next_to(arrow, RIGHT)

        group = Group(image, image_label, arrow, output)
        group.next_to(self.network_mob, UP, 0, RIGHT)

        dot = Dot()
        dot.move_to(input_words.get_right())
        dot.set_fill(opacity = 0.5)

        self.play(FadeIn(input_words[1], lag_ratio = 0.5))
        self.play(
            dot.move_to, image,
            dot.set_fill, None, 0,
            FadeIn(image),
            FadeIn(image_label),
        )
        self.activate_network(in_vect, 
            GrowArrow(arrow),
            FadeIn(output),
            FadeIn(output_words[1])
        )
        self.wait()
        self.play(
            FadeIn(parameter_words[1]), 
            self.get_edge_animation()
        )
        self.wait(2)

        self.to_fade = group
        self.curr_words = words
        self.title = title
        self.underline = underline

    def show_cost_function(self):
        network_mob = self.network_mob
        to_fade = self.to_fade
        input_words, output_words, parameter_words = self.curr_words

        network_mob.generate_target()
        network_mob.target.scale_in_place(0.7)
        network_mob.target.to_edge(UP, buff = LARGE_BUFF)
        rect = SurroundingRectangle(network_mob.target, color = BLUE)
        network_label = TextMobject("Input")
        network_label.set_color(input_words[0].get_color())
        network_label.next_to(rect, UP, SMALL_BUFF)

        new_output_word = TextMobject("1 number", "(the cost)")
        new_output_word[1].set_color(RED).scale(0.9)
        new_output_word.move_to(output_words[1], LEFT)
        new_output_word.shift(0.5*SMALL_BUFF*DOWN)
        new_parameter_word = TextMobject("""
            \\begin{flushleft}
            Many, many, many \\\\ training examples
            \\end{flushleft}
        """).scale(0.9)
        new_parameter_word.move_to(parameter_words[1], UP+LEFT) 

        new_title = TextMobject("Cost function")
        new_title.set_color(RED)
        new_title.move_to(self.title)

        arrow = Arrow(UP, DOWN, color = WHITE)
        arrow.next_to(rect, DOWN)
        cost = TextMobject("Cost: 5.4")
        cost.set_color(RED)
        cost.next_to(arrow, DOWN)

        training_data, validation_data, test_data = load_data_wrapper()
        training_examples = Group(*list(map(
            self.get_training_pair_mob, 
            training_data[:self.n_examples]
        )))
        training_examples.next_to(parameter_words, DOWN, buff = LARGE_BUFF)

        self.play(
            FadeOut(to_fade),
            FadeOut(input_words[1]),
            FadeOut(output_words[1]),
            MoveToTarget(network_mob),
            FadeIn(rect),
            FadeIn(network_label),
            Transform(self.title, new_title),
            self.underline.stretch_to_fit_width, new_title.get_width()
        )
        self.play(
            ApplyMethod(
                parameter_words[1].move_to, input_words[1], LEFT,
                path_arc = np.pi,
            ),
            self.get_edge_animation()
        )
        self.wait()
        self.play(
            GrowArrow(arrow),
            Write(cost, run_time = 1)
        )
        self.play(Write(new_output_word, run_time = 1))
        self.wait()
        self.play(
            FadeIn(new_parameter_word),
            FadeIn(training_examples[0])
        )
        self.wait(0.5)
        for last_ex, ex in zip(training_examples, training_examples[1:]):
            activations = self.network.get_activation_of_all_layers(
                ex.in_vect
            )
            for i, a in enumerate(activations):
                layer = self.network_mob.layers[i]
                active_layer = self.network_mob.get_active_layer(i, a)
                Transform(layer, active_layer).update(1)
            self.remove(last_ex)
            self.add(ex)
            self.wait(0.25)

    ####

    def get_function_description_words(self, w1, w2, w3):
        input_words = TextMobject("Input:", w1)
        input_words[0].set_color(BLUE)
        output_words = TextMobject("Output:", w2)
        output_words[0].set_color(YELLOW)
        parameter_words = TextMobject("Parameters:", w3)
        parameter_words[0].set_color(GREEN)
        words = VGroup(input_words, output_words, parameter_words)
        words.arrange(DOWN, aligned_edge = LEFT)
        words.scale(0.9)
        words.next_to(ORIGIN, RIGHT)
        words.shift(UP)
        return words

    def get_training_pair_mob(self, data):
        in_vect, out_vect = data
        image = MNistMobject(in_vect)
        image.set_height(1)
        comma = TextMobject(",")
        comma.next_to(image, RIGHT, SMALL_BUFF, DOWN)
        output = TexMobject(str(np.argmax(out_vect)))
        output.set_height(0.75)
        output.next_to(image, RIGHT, MED_SMALL_BUFF)
        lp, rp = parens = TextMobject("()")
        parens.scale(2)
        parens.stretch_to_fit_height(1.2*image.get_height())
        lp.next_to(image, LEFT, SMALL_BUFF)
        rp.next_to(lp, RIGHT, buff = 2)

        result = Group(lp, image, comma, output, rp)
        result.in_vect = in_vect
        return result

class NetworkGrowthMindset(YellAtNetwork):
    def construct(self):
        randy = self.pi_creature
        network_mob, eyes = self.get_network_and_eyes()
        eyes.look_at_anim(randy.eyes).update(1)
        edge_update = ContinualEdgeUpdate(
            network_mob,
            colors = [BLUE, RED]
        )

        self.play(
            PiCreatureSays(
                randy, "Awful, just awful!",
                target_mode = "angry",
                look_at_arg = eyes,
                run_time = 1,
            ),
            eyes.change_mode_anim("concerned_musician")
        )
        self.wait()
        self.add(edge_update)
        self.pi_creature_says(
            "But we can do better! \\\\ Growth mindset!",
            target_mode = "hooray"
        )
        self.play(eyes.change_mode_anim("happy"))
        self.wait(3)

class SingleVariableCostFunction(GraphScene):
    CONFIG = {
        "x_axis_label" : "$w$",
        "y_axis_label" : "",
        "x_min" : -5,
        "x_max" : 7,
        "x_axis_width" : 12,
        "graph_origin" : 2.5*DOWN + LEFT,
        "tangent_line_color" : YELLOW,
    }
    def construct(self):
        self.reduce_full_function_to_single_variable()
        self.show_graph()
        self.find_exact_solution()
        self.make_function_more_complicated()
        self.take_steps()
        self.take_steps_based_on_slope()
        self.ball_rolling_down_hill()
        self.note_step_sizes()

    def reduce_full_function_to_single_variable(self):
        name = TextMobject("Cost function")
        cf1 = TexMobject("C(", "w_1, w_2, \\dots, w_{13{,}002}", ")")
        cf2 = TexMobject("C(", "w", ")")
        for cf in cf1, cf2:
            VGroup(cf[0], cf[2]).set_color(RED)
        big_brace, lil_brace = [
            Brace(cf[1], DOWN)
            for cf in (cf1, cf2)
        ]
        big_brace_text = big_brace.get_text("Weights and biases")
        lil_brace_text = lil_brace.get_text("Single input")

        name.next_to(cf1, UP, LARGE_BUFF)
        name.set_color(RED)

        self.add(name, cf1)
        self.play(
            GrowFromCenter(big_brace),
            FadeIn(big_brace_text)
        )
        self.wait()
        self.play(
            ReplacementTransform(big_brace, lil_brace),
            ReplacementTransform(big_brace_text, lil_brace_text),
            ReplacementTransform(cf1, cf2),
        )

        # cf2.add_background_rectangle()
        lil_brace_text.add_background_rectangle()
        self.brace_group = VGroup(lil_brace, lil_brace_text)
        cf2.add(self.brace_group)
        self.function_label = cf2
        self.to_fade = name

    def show_graph(self):
        function_label = self.function_label
        self.setup_axes()
        graph = self.get_graph(
            lambda x : 0.5*(x - 3)**2 + 2,
            color = RED
        )

        self.play(
            FadeOut(self.to_fade),
            Write(self.axes),
            Animation(function_label),
            run_time = 1,
        )
        self.play(
            function_label.next_to, 
                self.input_to_graph_point(5, graph), RIGHT,
            ShowCreation(graph)
        )
        self.wait()

        self.graph = graph

    def find_exact_solution(self):
        function_label = self.function_label
        graph = self.graph

        w_min = TexMobject("w", "_{\\text{min}}", arg_separator = "")
        w_min.move_to(function_label[1], UP+LEFT)
        w_min[1].fade(1)
        x = 3
        dot = Dot(
            self.input_to_graph_point(x, graph),
            color = YELLOW
        )
        line = self.get_vertical_line_to_graph(
            x, graph, 
            line_class = DashedLine,
            color = YELLOW
        )
        formula = TexMobject("\\frac{dC}{dw}(w) = 0")
        formula.next_to(dot, UP, buff = 2)
        formula.shift(LEFT)
        arrow = Arrow(formula.get_bottom(), dot.get_center())

        self.play(
            w_min.shift, 
                line.get_bottom() - w_min[0].get_top(),
                MED_SMALL_BUFF*DOWN,
            w_min.set_fill, WHITE, 1,
        )
        self.play(ShowCreation(line))
        self.play(DrawBorderThenFill(dot, run_time = 1))
        self.wait()
        self.play(Write(formula, run_time = 2))
        self.play(GrowArrow(arrow))
        self.wait()

        self.dot = dot
        self.line = line
        self.w_min = w_min
        self.deriv_group = VGroup(formula, arrow)

    def make_function_more_complicated(self):
        dot = self.dot
        line = self.line
        w_min = self.w_min
        deriv_group = self.deriv_group
        function_label = self.function_label
        brace_group = function_label[-1]
        function_label.remove(brace_group)

        brace = Brace(deriv_group, UP)
        words = TextMobject("Sometimes \\\\ infeasible")
        words.next_to(deriv_group, UP)
        words.set_color(BLUE)
        words.next_to(brace, UP)

        graph = self.get_graph(
            lambda x : 0.05*((x+2)*(x-1)*(x-3))**2 + 2 + 0.3*(x-3),
            color = RED
        )

        self.play(
            ReplacementTransform(self.graph, graph),
            function_label.shift, 2*UP+1.9*LEFT,
            FadeOut(brace_group),
            Animation(dot)
        )
        self.graph = graph
        self.play(
            Write(words, run_time = 1),
            GrowFromCenter(brace)
        )
        self.wait(2)
        self.play(FadeOut(VGroup(words, brace, deriv_group)))

    def take_steps(self):
        dot = self.dot
        line = self.line
        w_mob, min_mob = self.w_min
        graph = self.graph

        def update_line(line):
            x = self.x_axis.point_to_number(w_mob.get_center())
            line.put_start_and_end_on_with_projection(
                self.coords_to_point(x, 0),
                self.input_to_graph_point(x, graph)
            )
            return line
        line_update_anim = UpdateFromFunc(line, update_line)

        def update_dot(dot):
            dot.move_to(line.get_end())
            return dot
        dot_update_anim = UpdateFromFunc(dot, update_dot)

        point = self.coords_to_point(2, 0)
        arrows = VGroup()
        q_marks = VGroup()
        for vect, color in (LEFT, BLUE), (RIGHT, GREEN):
            arrow = Arrow(ORIGIN, vect, buff = SMALL_BUFF)
            arrow.shift(point + SMALL_BUFF*UP)
            arrow.set_color(color)
            arrows.add(arrow)
            q_mark = TextMobject("?")
            q_mark.next_to(arrow, UP, buff = 0)
            q_mark.add_background_rectangle()
            q_marks.add(q_mark)

        self.play(
            w_mob.next_to, point, DOWN,
            FadeOut(min_mob),
            line_update_anim, 
            dot_update_anim,
        )
        self.wait()
        self.play(*it.chain(
            list(map(GrowArrow, arrows)),
            list(map(FadeIn, q_marks)),
        ))
        self.wait()

        self.arrow_group = VGroup(arrows, q_marks)
        self.line_update_anim = line_update_anim
        self.dot_update_anim = dot_update_anim
        self.w_mob = w_mob

    def take_steps_based_on_slope(self):
        arrows, q_marks = arrow_group = self.arrow_group
        line_update_anim = self.line_update_anim
        dot_update_anim = self.dot_update_anim
        dot = self.dot
        w_mob = self.w_mob
        graph = self.graph

        x = self.x_axis.point_to_number(w_mob.get_center())
        tangent_line = self.get_tangent_line(x, arrows[0].get_color())

        self.play(
            ShowCreation(tangent_line),
            Animation(dot),
        )
        self.play(VGroup(arrows[1], q_marks).set_fill, None, 0)
        self.play(
            w_mob.shift, MED_SMALL_BUFF*LEFT,
            MaintainPositionRelativeTo(arrow_group, w_mob),
            line_update_anim, dot_update_anim,
        )
        self.wait()

        new_x = 0.3
        new_point = self.coords_to_point(new_x, 0)
        new_tangent_line = self.get_tangent_line(
            new_x, arrows[1].get_color()
        )
        self.play(
            FadeOut(tangent_line),
            w_mob.next_to, new_point, DOWN,
            arrow_group.next_to, new_point, UP, SMALL_BUFF,
            arrow_group.set_fill, None, 1,
            dot_update_anim,
            line_update_anim,
        )
        self.play(
            ShowCreation(new_tangent_line),
            Animation(dot),
            Animation(arrow_group),
        )
        self.wait()
        self.play(VGroup(arrows[0], q_marks).set_fill, None, 0)
        self.play(
            w_mob.shift, MED_SMALL_BUFF*RIGHT,
            MaintainPositionRelativeTo(arrow_group, w_mob),
            line_update_anim, dot_update_anim,
        )
        self.play(
            FadeOut(VGroup(new_tangent_line, arrow_group)),
            Animation(dot),
        )
        self.wait()
        for x in 0.8, 1.1, 0.95:
            self.play(
                w_mob.next_to, self.coords_to_point(x, 0), DOWN,
                line_update_anim,
                dot_update_anim,
            )
        self.wait()

    def ball_rolling_down_hill(self):
        ball = self.dot
        graph = self.graph
        point = VectorizedPoint(self.coords_to_point(-0.5, 0))
        w_mob = self.w_mob

        def update_ball(ball):
            x = self.x_axis.point_to_number(ball.point.get_center())
            graph_point = self.input_to_graph_point(x, graph)
            vect = rotate_vector(UP, self.angle_of_tangent(x, graph))
            radius = ball.get_width()/2
            ball.move_to(graph_point + radius*vect)
            return ball

        def update_point(point, dt):
            x = self.x_axis.point_to_number(point.get_center())
            slope = self.slope_of_tangent(x, graph)
            if abs(slope) > 0.5:
                slope = 0.5 * slope / abs(slope)
            x -= slope*dt
            point.move_to(self.coords_to_point(x, 0))


        ball.generate_target()
        ball.target.scale(2)
        ball.target.set_fill(opacity = 0)
        ball.target.set_stroke(BLUE, 3)
        ball.point = point
        ball.target.point = point
        update_ball(ball.target)

        self.play(MoveToTarget(ball))
        self.play(
            point.move_to, w_mob,
            UpdateFromFunc(ball, update_ball),
            run_time = 3,
        )
        self.wait(2)

        points = [
            VectorizedPoint(self.coords_to_point(x, 0))
            for x in np.linspace(-2.7, 3.7, 11)
        ]
        balls = VGroup()
        updates = []
        for point in points:
            new_ball = ball.copy() 
            new_ball.point = point
            balls.add(new_ball)
            updates += [
                Mobject.add_updater(point, update_point),
                Mobject.add_updater(new_ball, update_ball)
            ]
        balls.set_color_by_gradient(BLUE, GREEN)

        self.play(ReplacementTransform(ball, balls))
        self.add(*updates)
        self.wait(5)
        self.remove(*updates)
        self.remove(*points)
        self.play(FadeOut(balls))

    def note_step_sizes(self):
        w_mob = self.w_mob
        line_update_anim = self.line_update_anim

        x = -0.5
        target_x = 0.94
        point = VectorizedPoint(self.coords_to_point(x, 0))
        line = self.get_tangent_line(x)
        line.scale_in_place(0.5)
        def update_line(line):
            x = self.x_axis.point_to_number(point.get_center())
            self.make_line_tangent(line, x)
            return line

        self.play(
            ShowCreation(line),
            w_mob.next_to, point, DOWN,
            line_update_anim,
        )
        for n in range(6):
            x = self.x_axis.point_to_number(point.get_center())
            new_x = interpolate(x, target_x, 0.5)
            self.play(
                point.move_to, self.coords_to_point(new_x, 0),
                MaintainPositionRelativeTo(w_mob, point),
                line_update_anim,
                UpdateFromFunc(line, update_line),
            )
            self.wait(0.5)
        self.wait()

    ###

    def get_tangent_line(self, x, color = YELLOW):
        tangent_line = Line(LEFT, RIGHT).scale(3)
        tangent_line.set_color(color)
        self.make_line_tangent(tangent_line, x)
        return tangent_line

    def make_line_tangent(self, line, x):
        graph = self.graph
        line.rotate(self.angle_of_tangent(x, graph) - line.get_angle())
        line.move_to(self.input_to_graph_point(x, graph))

class LocalVsGlobal(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            Local minimum = Doable \\\\
            Global minimum = Crazy hard
        """)
        self.change_student_modes(*["pondering"]*3)
        self.wait(2)

class TwoVariableInputSpace(Scene):
    def construct(self):
        self.add_plane()
        self.ask_about_direction()
        self.show_gradient()

    def add_plane(self):
        plane = NumberPlane(
            x_radius = FRAME_X_RADIUS/2
        )
        plane.add_coordinates()
        name = TextMobject("Input space")
        name.add_background_rectangle()
        name.next_to(plane.get_corner(UP+LEFT), DOWN+RIGHT)
        x, y = list(map(TexMobject, ["x", "y"]))
        x.next_to(plane.coords_to_point(3.25, 0), UP, SMALL_BUFF)
        y.next_to(plane.coords_to_point(0, 3.6), RIGHT, SMALL_BUFF)

        self.play(
            *list(map(Write, [plane, name, x, y])),
            run_time = 1
        )
        self.wait()

        self.plane = plane

    def ask_about_direction(self):
        point = self.plane.coords_to_point(2, 1)
        dot = Dot(point, color = YELLOW)
        dot.save_state()
        dot.move_to(FRAME_Y_RADIUS*UP + FRAME_X_RADIUS*RIGHT/2)
        dot.fade(1)
        arrows = VGroup(*[
            Arrow(ORIGIN, vect).shift(point)
            for vect in compass_directions(8)
        ])
        arrows.set_color(WHITE)
        question = TextMobject(
            "Which direction decreases \\\\",
            "$C(x, y)$", "most quickly?"
        )
        question.scale(0.7)
        question.set_color(YELLOW)
        question.set_color_by_tex("C(x, y)", RED)
        question.add_background_rectangle()
        question.next_to(arrows, LEFT)

        self.play(dot.restore)
        self.play(
            FadeIn(question),
            LaggedStartMap(GrowArrow, arrows)
        )
        self.wait()

        self.arrows = arrows
        self.dot = dot
        self.question = question

    def show_gradient(self):
        arrows = self.arrows
        dot = self.dot
        question = self.question

        arrow = arrows[3]
        new_arrow = Arrow(
            dot.get_center(), arrow.get_end(),
            buff = 0,
            color = GREEN
        )
        new_arrow.set_color(GREEN)
        arrow.save_state()

        gradient = TexMobject("\\nabla C(x, y)")
        gradient.add_background_rectangle()
        gradient.next_to(arrow.get_end(), UP, SMALL_BUFF)

        gradient_words = TextMobject(
            "``Gradient'', the direction\\\\ of",
            "steepest increase"
        )
        gradient_words.scale(0.7)
        gradient_words[-1].set_color(GREEN)
        gradient_words.next_to(gradient, UP, SMALL_BUFF)
        gradient_words.add_background_rectangle(opacity = 1)
        gradient_words.shift(LEFT)

        anti_arrow = new_arrow.copy()
        anti_arrow.rotate(np.pi, about_point = dot.get_center())
        anti_arrow.set_color(RED)

        self.play(
            Transform(arrow, new_arrow),
            Animation(dot),
            *[FadeOut(a) for a in arrows if a is not arrow]
        )
        self.play(FadeIn(gradient))
        self.play(Write(gradient_words, run_time = 2))
        self.wait(2)
        self.play(
            arrow.fade,
            ReplacementTransform(
                arrow.copy(),
                anti_arrow
            )
        )
        self.wait(2)

class CostSurface(ExternallyAnimatedScene):
    pass

class KhanAcademyMVCWrapper(PiCreatureScene):
    def construct(self):
        screen = ScreenRectangle(height = 5)
        screen.to_corner(UP+LEFT)
        morty = self.pi_creature

        self.play(
            ShowCreation(screen),
            morty.change, "raise_right_hand",
        )
        self.wait(3)
        self.play(morty.change, "happy", screen)
        self.wait(5)

class KAGradientPreview(ExternallyAnimatedScene):
    pass

class GradientDescentAlgorithm(Scene):
    def construct(self):
        words = VGroup(
            TextMobject("Compute", "$\\nabla C$"),
            TextMobject("Small step in", "$-\\nabla C$", "direction"),
            TextMobject("Repeat."),
        )
        words.arrange(DOWN, aligned_edge = LEFT)
        words.set_width(FRAME_WIDTH - 1)
        words.to_corner(DOWN+LEFT)

        for word in words[:2]:
            word[1].set_color(RED)

        for word in words:
            self.play(Write(word, run_time = 1))
            self.wait()

class GradientDescentName(Scene):
    def construct(self):
        words = TextMobject("Gradient descent")
        words.set_color(BLUE)
        words.set_width(FRAME_WIDTH - 1)
        words.to_edge(DOWN)

        self.play(Write(words, run_time = 2))
        self.wait()

class ShowFullCostFunctionGradient(PreviewLearning):
    def construct(self):
        self.organize_weights_as_column_vector()
        self.show_gradient()

    def organize_weights_as_column_vector(self):
        network_mob = self.network_mob
        edges = VGroup(*it.chain(*network_mob.edge_groups))
        layers = VGroup(*network_mob.layers)
        layers.add(network_mob.output_labels)
        self.color_network_edges()

        nums = [2.25, -1.57,  1.98, -1.16,  3.82, 1.21]
        decimals = VGroup(*[
            DecimalNumber(num).set_color(
                BLUE_D if num > 0 else RED
            )
            for num in nums
        ])
        dots = TexMobject("\\vdots")
        decimals.submobjects.insert(3, dots)
        decimals.arrange(DOWN)
        decimals.shift(2*LEFT + 0.5*DOWN)
        lb, rb = brackets = TexMobject("\\big[", "\\big]")
        brackets.scale(2)
        brackets.stretch_to_fit_height(1.2*decimals.get_height())
        lb.next_to(decimals, LEFT, SMALL_BUFF)
        rb.next_to(decimals, RIGHT, SMALL_BUFF)
        column_vect = VGroup(lb, decimals, rb)

        edges_target = VGroup(*it.chain(
            decimals[:3],
            [dots]*(len(edges) - 6),
            decimals[-3:]
        ))

        words = TextMobject("$13{,}002$ weights and biases")
        words.next_to(column_vect, UP)

        lhs = TexMobject("\\vec{\\textbf{W}}", "=")
        lhs[0].set_color(YELLOW)
        lhs.next_to(column_vect, LEFT)

        self.play(
            FadeOut(layers),
            edges.space_out_submobjects, 1.2,
        )
        self.play(
            ReplacementTransform(
                edges, edges_target,
                run_time = 2,
                lag_ratio = 0.5
            ),
            LaggedStartMap(FadeIn, words),
        )
        self.play(*list(map(Write, [lb, rb, lhs])), run_time = 1)
        self.wait()

        self.column_vect = column_vect

    def show_gradient(self):
        column_vect = self.column_vect

        lhs = TexMobject(
            "-", "\\nabla", "C(", "\\vec{\\textbf{W}}", ")", "="
        )
        lhs.shift(2*RIGHT)
        lhs.set_color_by_tex("W", YELLOW)
        old_decimals = VGroup(*[m for m in column_vect[1] if isinstance(m, DecimalNumber)])
        new_decimals = VGroup()
        new_nums = [0.18, 0.45, -0.51, 0.4, -0.32, 0.82]
        for decimal, new_num in zip(old_decimals, new_nums):
            new_decimal = DecimalNumber(new_num)
            new_decimal.set_color(BLUE if new_num > 0 else RED_B)
            new_decimal.move_to(decimal)
            new_decimals.add(new_decimal)
        rhs = VGroup(
            column_vect[0].copy(),
            new_decimals, 
            column_vect[2].copy(),
        )
        rhs.to_edge(RIGHT, buff = 1.75)
        lhs.next_to(rhs, LEFT)

        words = TextMobject("How to nudge all \\\\ weights and biases")
        words.next_to(rhs, UP)

        self.play(Write(VGroup(lhs, rhs)))
        self.play(FadeIn(words))
        for od, nd in zip(old_decimals, new_decimals):
            nd = nd.deepcopy()
            od_num = od.number
            nd_num = nd.number
            self.play(
                nd.move_to, od, 
                nd.shift, 1.5*RIGHT
            )
            self.play(
                Transform(
                    nd, VectorizedPoint(od.get_center()),
                    lag_ratio = 0.5,
                    remover = True
                ),
                ChangingDecimal(
                    od,
                    lambda a : interpolate(od_num, od_num+nd_num, a)
                )
            )
        self.wait()

class DotsInsert(Scene):
    def construct(self):
        dots = TexMobject("\\vdots")
        dots.set_height(FRAME_HEIGHT - 1)
        self.add(dots)

class HowMinimizingCostMeansBetterTrainingPerformance(IntroduceCostFunction):
    def construct(self):
        IntroduceCostFunction.construct(self)
        self.improve_last_layer()

    def improve_last_layer(self):
        decimals = self.decimal_groups[0]
        neurons = self.network_mob.layers[-1].neurons

        values = [d.number for d in decimals]
        target_values = 0.1*np.random.random(10)
        target_values[3] = 0.98

        words = TextMobject("Minimize cost $\\dots$")
        words.next_to(decimals, UP, MED_LARGE_BUFF)
        words.set_color(YELLOW)
        # words.shift(LEFT)

        def generate_update(n1, n2):
            return lambda a : interpolate(n1, n2, a)
        updates = [
            generate_update(n1, n2)
            for n1, n2 in zip(values, target_values)
        ]

        self.play(LaggedStartMap(FadeIn, words, run_time = 1))
        self.play(*[
            ChangingDecimal(d, update)
            for d, update in zip(decimals, updates)
        ] + [
            UpdateFromFunc(
                d,
                lambda mob: mob.set_fill(
                    interpolate_color(BLACK, WHITE, 0.5+0.5*mob.number),
                    opacity = 1
                )
            )
            for d in decimals
        ] + [
            ApplyMethod(neuron.set_fill, WHITE, target_value)
            for neuron, target_value in zip(neurons, target_values)
        ], run_time = 3)
        self.wait()

    ###

    def average_over_all_training_data(self):
        pass #So that IntroduceCostFunction.construct doesn't do this

class CostSurfaceSteps(ExternallyAnimatedScene):
    pass

class ConfusedAboutHighDimension(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "13{,}002-dimensional \\\\ nudge?",
            target_mode = "confused"
        )
        self.change_student_modes(*["confused"]*3)
        self.wait(2)
        self.teacher_thinks(
            "",
            bubble_kwargs = {"width" : 6, "height" : 4},
            added_anims = [self.get_student_changes(*["plain"]*3)]
        )
        self.zoom_in_on_thought_bubble()

class NonSpatialGradientIntuition(Scene):
    CONFIG = {
        "w_color" : YELLOW,
        "positive_color" : BLUE,
        "negative_color" : RED,
        "vect_height" : FRAME_Y_RADIUS - MED_LARGE_BUFF,
        "text_scale_value" : 0.7,
    }
    def construct(self):
        self.add_vector()
        self.add_gradient()
        self.show_sign_interpretation()
        self.show_magnitude_interpretation()

    def add_vector(self):
        lhs = TexMobject("\\vec{\\textbf{W}}", "=")
        lhs[0].set_color(self.w_color)
        lhs.to_edge(LEFT)

        ws = VGroup(*[
            VGroup(TexMobject(tex))
            for tex in it.chain(
                ["w_%d"%d for d in range(3)],
                ["\\vdots"],
                ["w_{13{,}00%d}"%d for d in range(3)]
            )
        ])
        ws.set_color(self.w_color)
        ws.arrange(DOWN)
        lb, rb = brackets = TexMobject("\\big[", "\\big]").scale(2)
        brackets.stretch_to_fit_height(1.2*ws.get_height())
        lb.next_to(ws, LEFT)
        rb.next_to(ws, RIGHT)
        vect = VGroup(lb, ws, rb)

        vect.set_height(self.vect_height)
        vect.to_edge(UP).shift(2*LEFT)
        lhs.next_to(vect, LEFT)

        self.add(lhs, vect)
        self.vect = vect
        self.top_lhs = lhs

    def add_gradient(self):
        lb, ws, rb = vect = self.vect
        ws = VGroup(*ws)
        dots = ws[len(ws)/2]
        ws.remove(dots)

        lhs = TexMobject(
            "-\\nabla", "C(", "\\vec{\\textbf{W}}", ")", "="
        )
        lhs.next_to(vect, RIGHT, LARGE_BUFF)
        lhs.set_color_by_tex("W", self.w_color)

        decimals = VGroup()
        nums = [0.31, 0.03, -1.25, 0.78, -0.37, 0.16]
        for num, w in zip(nums, ws):
            decimal = DecimalNumber(num)
            decimal.scale(self.text_scale_value)
            if num > 0:
                decimal.set_color(self.positive_color)
            else:
                decimal.set_color(self.negative_color)
            decimal.move_to(w)
            decimals.add(decimal)
        new_dots = dots.copy()

        grad_content = VGroup(*it.chain(
            decimals[:3], new_dots, decimals[3:]
        ))
        grad_vect = VGroup(lb.copy(), grad_content, rb.copy())
        VGroup(grad_vect[0], grad_vect[-1]).space_out_submobjects(0.8)
        grad_vect.set_height(self.vect_height)
        grad_vect.next_to(self.vect, DOWN)
        lhs.next_to(grad_vect, LEFT)

        brace = Brace(grad_vect, RIGHT)
        words = brace.get_text("Example gradient")

        self.wait()
        self.play(
            ReplacementTransform(self.top_lhs.copy(), lhs),
            ReplacementTransform(self.vect.copy(), grad_vect),
            GrowFromCenter(brace),
            FadeIn(words)
        )
        self.wait()
        self.play(FadeOut(VGroup(brace, words)))

        self.ws = ws
        self.grad_lhs = lhs
        self.grad_vect = grad_vect
        self.decimals = decimals

    def show_sign_interpretation(self):
        ws = self.ws.copy()
        decimals = self.decimals

        direction_phrases = VGroup()
        for w, decimal in zip(ws, decimals):
            if decimal.number > 0:
                verb = "increase"
                color = self.positive_color
            else:
                verb = "decrease"
                color = self.negative_color
            phrase = TextMobject("should", verb)
            phrase.scale(self.text_scale_value)
            phrase.set_color_by_tex(verb, color)
            w.generate_target()
            group = VGroup(w.target, phrase)
            group.arrange(RIGHT)
            w.target.shift(0.7*SMALL_BUFF*DOWN)
            group.move_to(decimal.get_center() + RIGHT, LEFT)
            direction_phrases.add(phrase)

        self.play(
            LaggedStartMap(MoveToTarget, ws),
            LaggedStartMap(FadeIn, direction_phrases)
        )
        self.wait(2)

        self.direction_phrases = direction_phrases
        self.ws = ws

    def show_magnitude_interpretation(self):
        direction_phrases = self.direction_phrases
        ws = self.ws
        decimals = self.decimals

        magnitude_words = VGroup()
        rects = VGroup()
        for phrase, decimal in zip(direction_phrases, decimals):
            if abs(decimal.number) < 0.2:
                adj = "a little"
                color = interpolate_color(BLACK, WHITE, 0.5)
            elif abs(decimal.number) < 0.5:
                adj = "somewhat"
                color = LIGHT_GREY
            else:
                adj = "a lot"
                color =  WHITE
            words = TextMobject(adj)
            words.scale(self.text_scale_value)
            words.set_color(color)
            words.next_to(phrase, RIGHT, SMALL_BUFF)
            magnitude_words.add(words)

            rect = SurroundingRectangle(
                VGroup(*decimal[-4:]), 
                buff = SMALL_BUFF,
                color = LIGHT_GREY
            )
            rect.target = words
            rects.add(rect)

        self.play(LaggedStartMap(ShowCreation, rects))
        self.play(LaggedStartMap(MoveToTarget, rects))
        self.wait(2)

class SomeConnectionsMatterMoreThanOthers(PreviewLearning):
    def setup(self):
        np.random.seed(1)
        PreviewLearning.setup(self)
        self.color_network_edges()

        ex_in = get_organized_images()[3][4]
        image = MNistMobject(ex_in)
        image.to_corner(UP+LEFT)
        self.add(image)
        self.ex_in = ex_in

    def construct(self):
        self.activate_network(self.ex_in)
        self.fade_edges()
        self.show_important_connection()
        self.show_unimportant_connection()

    def fade_edges(self):
        edges = VGroup(*it.chain(*self.network_mob.edge_groups))
        self.play(*[
            ApplyMethod(
                edge.set_stroke, BLACK, 0,
                rate_func = lambda a : 0.5*smooth(a)
            )
            for edge in edges
        ])

    def show_important_connection(self):
        layers = self.network_mob.layers
        edge = self.get_edge(2, 3)
        edge.set_stroke(YELLOW, 4)
        words = TextMobject("This weight \\\\ matters a lot")
        words.next_to(layers[-1], UP).to_edge(UP)
        words.set_color(YELLOW)
        arrow = Arrow(words.get_bottom(), edge.get_center())

        self.play(
            ShowCreation(edge),
            GrowArrow(arrow),
            FadeIn(words)
        )
        self.wait()

    def show_unimportant_connection(self):
        color = TEAL
        edge = self.get_edge(11, 6)
        edge.set_stroke(color, 5)
        words = TextMobject("Who even cares \\\\ about this weight?")
        words.next_to(self.network_mob.layers[-1], DOWN)
        words.to_edge(DOWN)
        words.set_color(color)
        arrow = Arrow(words.get_top(), edge.get_center(), buff = SMALL_BUFF)
        arrow.set_color(color)

        self.play(
            ShowCreation(edge),
            GrowArrow(arrow),
            FadeIn(words)
        )
        self.wait()
    ###

    def get_edge(self, i1, i2):
        layers = self.network_mob.layers
        n1 = layers[-2].neurons[i1]
        n2 = layers[-1].neurons[i2]
        return self.network_mob.get_edge(n1, n2)

class SpinningVectorWithLabel(Scene):
    def construct(self):
        plane = NumberPlane(
            x_unit_size = 2,
            y_unit_size = 2,
        )
        plane.add_coordinates()
        self.add(plane)

        vector = Vector(2*RIGHT)
        label = get_decimal_vector([-1, -1], with_dots = False)
        label.add_to_back(BackgroundRectangle(label))
        label.next_to(vector.get_end(), UP+RIGHT)
        label.decimals.set_fill(opacity = 0)
        decimals = label.decimals.copy()
        decimals.set_fill(WHITE, 1)

        cd1 = ChangingDecimal(
            decimals[0],
            lambda a : np.cos(vector.get_angle()),
            tracked_mobject = label.decimals[0],
        )
        cd2 = ChangingDecimal(
            decimals[1],
            lambda a : np.sin(vector.get_angle()),
            tracked_mobject = label.decimals[1],
        )

        self.play(
            Rotate(
                vector, 
                0.999*np.pi,
                in_place = False,
                run_time = 8,
                rate_func = there_and_back
            ),
            UpdateFromFunc(
                label,
                lambda m : m.next_to(vector.get_end(), UP+RIGHT)
            ),
            cd1, cd2,
        )
        self.wait()

class TwoGradientInterpretationsIn2D(Scene):
    def construct(self):
        self.force_skipping()

        self.setup_plane()
        self.add_function_definitions()
        self.point_out_direction()
        self.point_out_relative_importance()
        self.wiggle_in_neighborhood()

    def setup_plane(self):
        plane = NumberPlane()
        plane.add_coordinates()
        self.add(plane)
        self.plane = plane

    def add_function_definitions(self):
        func = TexMobject(
            "C(", "x, y", ")", "=", 
            "\\frac{3}{2}x^2", "+", "\\frac{1}{2}y^2",
        )
        func.shift(FRAME_X_RADIUS*LEFT/2).to_edge(UP)

        grad = TexMobject("\\nabla", "C(", "1, 1", ")", "=")
        vect = TexMobject(
            "\\left[\\begin{array}{c} 3 \\\\ 1 \\end{array}\\right]"
        )
        vect.next_to(grad, RIGHT, SMALL_BUFF)
        grad_group = VGroup(grad, vect)
        grad_group.next_to(ORIGIN, RIGHT).to_edge(UP, buff = MED_SMALL_BUFF)
        for mob in grad, vect, func:
            mob.add_background_rectangle()
            mob.background_rectangle.scale_in_place(1.1)

        self.play(Write(func, run_time = 1))
        self.play(Write(grad_group, run_time = 2))
        self.wait()

        self.func = func
        self.grad = grad
        self.vect = vect

    def point_out_direction(self):
        coords = self.grad.get_part_by_tex("1, 1").copy()
        vect = self.vect[1].copy()
        coords.set_color(YELLOW)
        vect.set_color(GREEN)

        dot = Dot(self.plane.coords_to_point(1, 1))
        dot.set_color(coords.get_color())
        arrow = Arrow(
            self.plane.coords_to_point(1, 1),
            self.plane.coords_to_point(4, 2),
            buff = 0,
            color = vect.get_color()
        )
        words = TextMobject("Direction of \\\\ steepest ascent")
        words.add_background_rectangle()
        words.next_to(ORIGIN, DOWN)
        words.rotate(arrow.get_angle())
        words.shift(arrow.get_center())

        self.play(DrawBorderThenFill(coords, run_time = 1))
        self.play(ReplacementTransform(coords.copy(), dot))
        self.play(DrawBorderThenFill(vect, run_time = 1))
        self.play(
            ReplacementTransform(vect.copy(), arrow),
            Animation(dot)
        )
        self.play(Write(words))
        self.wait()

        self.remove(vect)
        self.vect[1].set_color(vect.get_color())
        self.remove(coords)
        self.grad.get_part_by_tex("1, 1").set_color(coords.get_color())

        self.steepest_words = words
        self.dot = dot

    def point_out_relative_importance(self):
        func = self.func
        grad_group = VGroup(self.grad, self.vect)
        x_part = func.get_part_by_tex("x^2")
        y_part = func.get_part_by_tex("y^2")

        self.play(func.shift, 1.5*DOWN)

        x_rect = SurroundingRectangle(x_part, color = YELLOW)
        y_rect = SurroundingRectangle(y_part, color = TEAL)
        x_words = TextMobject("$x$ has 3 times \\\\ the impact...")
        x_words.set_color(x_rect.get_color())
        x_words.add_background_rectangle()
        x_words.next_to(x_rect, UP)
        # x_words.to_edge(LEFT)
        y_words = TextMobject("...as $y$")
        y_words.set_color(y_rect.get_color())
        y_words.add_background_rectangle()
        y_words.next_to(y_rect, DOWN)

        self.play(
            Write(x_words, run_time = 2),
            ShowCreation(x_rect)
        )
        self.wait()
        self.play(
            Write(y_words, run_time = 1),
            ShowCreation(y_rect)
        )
        self.wait(2)

    def wiggle_in_neighborhood(self):
        dot = self.dot
        steepest_words = self.steepest_words

        neighborhood = Circle(
            fill_color = BLUE,
            fill_opacity = 0.25,
            stroke_width = 0,
            radius = 0.5,
        )
        neighborhood.move_to(dot)

        self.revert_to_original_skipping_status()
        self.play(
            FadeOut(steepest_words),
            GrowFromCenter(neighborhood)
        )
        self.wait()
        for vect in RIGHT, UP, 0.3*(3*RIGHT + UP):
            self.play(
                dot.shift, 0.5*vect,
                rate_func = lambda t : wiggle(t, 4),
                run_time = 3,
            )
            self.wait()

class ParaboloidGraph(ExternallyAnimatedScene):
    pass

class TODOInsertEmphasizeComplexityOfCostFunctionCopy(TODOStub):
    CONFIG = {
        "message" : "Insert EmphasizeComplexityOfCostFunction copy"
    }

class GradientNudging(PreviewLearning):
    CONFIG = {
        "n_steps" : 10,
        "n_decimals" : 8,
    }
    def construct(self):
        self.setup_network_mob()
        self.add_gradient()
        self.change_weights_repeatedly()

    def setup_network_mob(self):
        network_mob = self.network_mob
        self.color_network_edges()
        network_mob.scale(0.7)
        network_mob.to_corner(DOWN+RIGHT)

    def add_gradient(self):
        lhs = TexMobject(
            "-", "\\nabla", "C(", "\\dots", ")", "="
        )
        brace = Brace(lhs.get_part_by_tex("dots"), DOWN)
        words = brace.get_text("All weights \\\\ and biases")
        words.scale(0.8, about_point = words.get_top())
        np.random.seed(3)
        nums = 4*(np.random.random(self.n_decimals)-0.5)
        vect = get_decimal_vector(nums)
        vect.next_to(lhs, RIGHT)
        group = VGroup(lhs, brace, words, vect)
        group.to_corner(UP+LEFT)

        self.add(*group)

        self.set_variables_as_attrs(
            grad_lhs = lhs,
            grad_vect = vect,
            grad_arg_words = words,
            grad_arg_brace = brace
        )

    def change_weights_repeatedly(self):
        network_mob = self.network_mob
        edges = VGroup(*reversed(list(
            it.chain(*network_mob.edge_groups)
        )))

        decimals = self.grad_vect.decimals

        words = TextMobject(
            "Change by some small\\\\",
            "multiple of $-\\nabla C(\\dots)$"
        )
        words.next_to(network_mob, UP).to_edge(UP)
        arrows = VGroup(*[
            Arrow(
                words.get_bottom(),
                edge_group.get_top(),
                color = WHITE
            )
            for edge_group in network_mob.edge_groups
        ])

        mover = VGroup(*decimals.family_members_with_points()).copy()
        # mover.set_fill(opacity = 0)
        mover.set_stroke(width = 0)
        target = VGroup(*self.network_mob.edge_groups.family_members_with_points()).copy()
        target.set_fill(opacity = 0)
        ApplyMethod(target.set_stroke, YELLOW, 2).update(0.3)
        self.play(
            ReplacementTransform(mover, target),
            FadeIn(words),
            LaggedStartMap(GrowArrow, arrows, run_time = 1)
        )
        self.play(FadeOut(target))
        self.play(self.get_edge_change_anim(edges))
        self.play(*self.get_decimal_change_anims(decimals))
        for x in range(self.n_steps):
            self.play(self.get_edge_change_anim(edges))
            self.play(*self.get_decimal_change_anims(decimals))
        self.wait()

    ###

    def get_edge_change_anim(self, edges):
        target_nums = 6*(np.random.random(len(edges))-0.5)
        edges.generate_target()
        for edge, target_num in zip(edges.target, target_nums):
            curr_num = edge.get_stroke_width()
            if Color(edge.get_stroke_color()) == Color(self.negative_edge_color):
                curr_num *= -1
            new_num = interpolate(curr_num, target_num, 0.2)
            if new_num > 0:
                new_color = self.positive_edge_color
            else:
                new_color = self.negative_edge_color
            edge.set_stroke(new_color, abs(new_num))
            edge.rotate_in_place(np.pi)
        return MoveToTarget(
            edges,
            lag_ratio = 0.5,
            run_time = 1.5
        )

    def get_decimal_change_anims(self, decimals):
        words = TextMobject("Recompute \\\\ gradient")
        words.next_to(decimals, DOWN, MED_LARGE_BUFF)
        def wrf(t):
            if t < 1./3:
                return smooth(3*t)
            elif t < 2./3:
                return 1
            else:
                return smooth(3 - 3*t)

        changes = 0.2*(np.random.random(len(decimals))-0.5)
        def generate_change_func(x, dx):
            return lambda a : interpolate(x, x+dx, a)
        return [
            ChangingDecimal(
                decimal, 
                generate_change_func(decimal.number, change)
            )
            for decimal, change in zip(decimals, changes)
        ] + [
            FadeIn(words, rate_func = wrf, run_time = 1.5, remover = True)
        ]

class BackPropWrapper(PiCreatureScene):
    def construct(self):
        morty = self.pi_creature
        screen = ScreenRectangle(height = 5)
        screen.to_corner(UP+LEFT)
        screen.shift(MED_LARGE_BUFF*DOWN)

        title = TextMobject("Backpropagation", "(next video)")
        title.next_to(screen, UP)

        self.play(
            morty.change, "raise_right_hand", screen,
            ShowCreation(screen)
        )
        self.play(Write(title[0], run_time = 1))
        self.wait()
        self.play(Write(title[1], run_time = 1))
        self.play(morty.change, "happy", screen)
        self.wait(5)

class TODOInsertCostSurfaceSteps(TODOStub):
    CONFIG = {
        "message" : "Insert CostSurfaceSteps"
    }

class ContinuouslyRangingNeuron(PreviewLearning):
    def construct(self):
        self.color_network_edges()
        network_mob = self.network_mob
        network_mob.scale(0.8)
        network_mob.to_edge(DOWN)
        neuron = self.network_mob.layers[2].neurons[6]
        decimal = DecimalNumber(0)
        decimal.set_width(0.8*neuron.get_width())
        decimal.move_to(neuron)

        decimal.generate_target()
        neuron.generate_target()
        group = VGroup(neuron.target, decimal.target)
        group.set_height(1)
        group.next_to(network_mob, UP)
        decimal.set_fill(opacity = 0)

        def update_decimal_color(decimal):
            if neuron.get_fill_opacity() > 0.8:
                decimal.set_color(BLACK)
            else:
                decimal.set_color(WHITE)
        decimal_color_anim = UpdateFromFunc(decimal, update_decimal_color)

        self.play(*list(map(MoveToTarget, [neuron, decimal])))
        for x in 0.7, 0.35, 0.97, 0.23, 0.54:
            curr_num = neuron.get_fill_opacity()
            self.play(
                neuron.set_fill, None, x,
                ChangingDecimal(
                    decimal, lambda a : interpolate(curr_num, x, a)
                ),
                decimal_color_anim
            )
            self.wait()

class AskHowItDoes(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "How well \\\\ does it do?",
            student_index = 0
        )
        self.wait(5)

class TestPerformance(PreviewLearning):
    CONFIG = {
        "n_examples" : 300,
        "time_per_example" : 0.1,
        "wrong_wait_time" : 0.5,
        "stroke_width_exp" : 2,
        "decimal_kwargs" : {
            "num_decimal_places" : 3,
        }
    }
    def construct(self):
        self.setup_network_mob()
        self.init_testing_data()
        self.add_title()
        self.add_fraction()
        self.run_through_examples()

    def setup_network_mob(self):
        self.network_mob.set_height(5)
        self.network_mob.to_corner(DOWN+LEFT)
        self.network_mob.to_edge(DOWN, buff = MED_SMALL_BUFF)

    def init_testing_data(self):
        training_data, validation_data, test_data = load_data_wrapper()
        self.test_data = iter(test_data[:self.n_examples])

    def add_title(self):
        title = TextMobject("Testing data")
        title.to_edge(UP, buff = MED_SMALL_BUFF)
        title.to_edge(LEFT, buff = LARGE_BUFF)
        self.add(title)
        self.title = title

    def add_fraction(self):
        self.n_correct = 0
        self.total = 0
        self.decimal = DecimalNumber(0, **self.decimal_kwargs)
        word_frac = TexMobject(
            "{\\text{Number correct}", "\\over", 
            "\\text{total}}", "=",
        )
        word_frac[0].set_color(GREEN)
        self.frac = self.get_frac()
        self.equals = TexMobject("=")
        fracs = VGroup(
            word_frac, self.frac, 
            self.equals, self.decimal
        )
        fracs.arrange(RIGHT)
        fracs.to_corner(UP+RIGHT, buff = LARGE_BUFF)
        self.add(fracs)

    def run_through_examples(self):
        title = self.title
        rects = [
            SurroundingRectangle(
                VGroup(neuron, label),
                buff = 0.5*SMALL_BUFF
            )
            for neuron, label in zip(
                self.network_mob.layers[-1].neurons,
                self.network_mob.output_labels
            )
        ]
        rect_wrong = TextMobject("Wrong!")
        rect_wrong.set_color(RED)
        num_wrong = rect_wrong.copy()

        arrow = Arrow(LEFT, RIGHT, color = WHITE)
        guess_word = TextMobject("Guess")
        self.add(arrow, guess_word)

        from tqdm import tqdm as ProgressDisplay
        for test_in, test_out in ProgressDisplay(list(self.test_data)):
            self.total += 1

            activations = self.activate_layers(test_in)
            choice = np.argmax(activations[-1])

            image = MNistMobject(test_in)
            image.set_height(1.5)
            choice_mob = TexMobject(str(choice))
            choice_mob.scale(1.5)
            group = VGroup(image, arrow, choice_mob)
            group.arrange(RIGHT)
            group.shift(
                self.title.get_bottom()+MED_SMALL_BUFF*DOWN -\
                image.get_top()
            )
            self.add(image, choice_mob)
            guess_word.next_to(arrow, UP, SMALL_BUFF)

            rect = rects[choice]
            self.add(rect)

            correct = (choice == test_out)
            if correct:
                self.n_correct += 1
            else:
                rect_wrong.next_to(rect, RIGHT)
                num_wrong.next_to(choice_mob, DOWN)
                self.add(rect_wrong, num_wrong)
            new_frac = self.get_frac()
            new_frac.shift(
                self.frac[1].get_left() - \
                new_frac[1].get_left()
            )
            self.remove(self.frac)
            self.add(new_frac)
            self.frac = new_frac
            self.equals.next_to(new_frac, RIGHT)

            new_decimal = DecimalNumber(
                float(self.n_correct)/self.total,
                **self.decimal_kwargs
            )
            new_decimal.next_to(self.equals, RIGHT)
            self.remove(self.decimal)
            self.add(new_decimal)
            self.decimal = new_decimal

            self.wait(self.time_per_example)
            if not correct:
                self.wait(self.wrong_wait_time)

            self.remove(rect, rect_wrong, num_wrong, image, choice_mob)

        self.add(rect, image, choice_mob)

    ###
    def add_network(self):
        self.network_mob = MNistNetworkMobject(**self.network_mob_config)
        self.network_mob.scale(0.8)
        self.network_mob.to_edge(DOWN)
        self.network = self.network_mob.neural_network
        self.add(self.network_mob)
        self.color_network_edges()

    def get_frac(self):
        frac = TexMobject("{%d"%self.n_correct, "\\over", "%d}"%self.total)
        frac[0].set_color(GREEN)
        return frac

    def activate_layers(self, test_in):
        activations = self.network.get_activation_of_all_layers(test_in)
        layers = self.network_mob.layers
        for layer, activation in zip(layers, activations)[1:]:
            for neuron, a in zip(layer.neurons, activation):
                neuron.set_fill(opacity = a)
        return activations

class ReactToPerformance(TeacherStudentsScene):
    def construct(self):
        title = VGroup(
            TextMobject("Play with network structure"),
            Arrow(LEFT, RIGHT, color = WHITE),
            TextMobject("98\\%", "testing accuracy")
        )
        title.arrange(RIGHT)
        title.to_edge(UP)
        title[-1][0].set_color(GREEN)
        self.play(Write(title, run_time = 2))

        last_words = TextMobject(
            "State of the art \\\\ is", 
            "99.79\\%"
        )
        last_words[-1].set_color(GREEN)

        self.teacher_says(
            "That's pretty", "good!",
            target_mode = "surprised",
            run_time = 1
        )
        self.change_student_modes(*["hooray"]*3)
        self.wait()
        self.teacher_says(last_words, target_mode = "hesitant")
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = self.teacher.bubble
        )
        self.wait()

class NoticeWhereItMessesUp(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Look where it \\\\ messes up",
            run_time = 1
        )
        self.wait(2)

class WrongExamples(TestPerformance):
    CONFIG = {
        "time_per_example" : 0
    }

class TODOBreakUpNineByPatterns(TODOStub):
    CONFIG = {
        "message" : "Insert the scene with 9 \\\\ broken up by patterns"
    }

class NotAtAll(TeacherStudentsScene, PreviewLearning):
    def setup(self):
        TeacherStudentsScene.setup(self)
        PreviewLearning.setup(self)

    def construct(self):
        words = TextMobject("Well...\\\\", "not at all!")
        words[1].set_color(BLACK)
        network_mob = self.network_mob
        network_mob.set_height(4)
        network_mob.to_corner(UP+LEFT)
        self.add(network_mob)
        self.color_network_edges()

        self.teacher_says(
            words, target_mode = "guilty",
            run_time = 1
        )
        self.change_student_modes(*["sassy"]*3)
        self.play(
            self.teacher.change, "concerned_musician",
            words[1].set_color, WHITE
        )
        self.wait(2)

class InterpretFirstWeightMatrixRows(TestPerformance):
    CONFIG = {
        "stroke_width_exp" : 1,
    }
    def construct(self):
        self.slide_network_to_side()
        self.prepare_pixel_arrays()
        self.show_all_pixel_array()

    def slide_network_to_side(self):
        network_mob = self.network_mob
        network_mob.generate_target()
        to_fade = VGroup(*it.chain(
            network_mob.edge_groups[1:],
            network_mob.layers[2:],
            network_mob.output_labels
        ))
        to_keep = VGroup(*it.chain(
            network_mob.edge_groups[0],
            network_mob.layers[:2]
        ))
        shift_val = FRAME_X_RADIUS*LEFT + MED_LARGE_BUFF*RIGHT - \
                    to_keep.get_left()
        self.play(
            to_fade.shift, shift_val,
            to_fade.fade, 1,
            to_keep.shift, shift_val
        )
        self.remove(to_fade)

    def prepare_pixel_arrays(self):
        pixel_arrays = VGroup()
        w_matrix = self.network.weights[0]
        for row in w_matrix:
            max_val = np.max(np.abs(row))
            shades = np.array(row)/max_val
            pixel_array = PixelsFromVect(np.zeros(row.size))
            for pixel, shade in zip(pixel_array, shades):
                if shade > 0:
                    color = self.positive_edge_color
                else:
                    color = self.negative_edge_color
                pixel.set_fill(color, opacity = abs(shade)**(0.3))
            pixel_arrays.add(pixel_array)
        pixel_arrays.arrange_in_grid(buff = MED_LARGE_BUFF)
        pixel_arrays.set_height(FRAME_HEIGHT - 2.5)
        pixel_arrays.to_corner(DOWN+RIGHT)

        for pixel_array in pixel_arrays:
            rect = SurroundingRectangle(pixel_array)
            rect.set_color(WHITE)
            pixel_array.rect = rect

        words = TextMobject("What second layer \\\\ neurons look for")
        words.next_to(pixel_arrays, UP).to_edge(UP)

        self.pixel_arrays = pixel_arrays
        self.words = words

    def show_all_pixel_array(self):
        edges = self.network_mob.edge_groups[0]
        neurons = self.network_mob.layers[1].neurons
        edges.remove(neurons[0].edges_in)

        self.play(
            VGroup(*neurons[1:]).set_stroke, None, 0.5,
            FadeIn(self.words),
            neurons[0].edges_in.set_stroke, None, 2,
            *[
                ApplyMethod(edge.set_stroke, None, 0.25)
                for edge in edges
                if edge not in neurons[0].edges_in
            ]
        )
        self.wait()
        last_neuron = None

        for neuron, pixel_array in zip(neurons, self.pixel_arrays):
            if last_neuron:
                self.play(
                    last_neuron.edges_in.set_stroke, None, 0.25,
                    last_neuron.set_stroke, None, 0.5,
                    neuron.set_stroke, None, 3,
                    neuron.edges_in.set_stroke, None, 2,
                )
            self.play(ReplacementTransform(
                neuron.edges_in.copy().set_fill(opacity = 0),
                pixel_array,
            ))
            self.play(ShowCreation(pixel_array.rect))
            last_neuron = neuron

class InputRandomData(TestPerformance):
    def construct(self):
        self.color_network_edges()
        self.show_random_image()
        self.show_expected_outcomes()
        self.feed_in_random_data()
        self.network_speaks()

    def show_random_image(self):
        np.random.seed(4)
        rand_vect = np.random.random(28*28)
        image = PixelsFromVect(rand_vect)
        image.to_edge(LEFT)
        image.shift(UP)
        rect = SurroundingRectangle(image)

        arrow = Arrow(
            rect.get_top(),
            self.network_mob.layers[0].neurons.get_top(),
            path_arc = -2*np.pi/3,
        )
        arrow.tip.set_stroke(width = 3)

        self.play(
            ShowCreation(rect),
            LaggedStartMap(
                DrawBorderThenFill, image, 
                stroke_width = 0.5
            )
        )
        self.play(ShowCreation(arrow))
        self.wait()

        self.image = image
        self.rand_vect = rand_vect
        self.image_rect = rect
        self.arrow = arrow

    def show_expected_outcomes(self):
        neurons = self.network_mob.layers[-1].neurons

        words = TextMobject("What might you expect?")
        words.to_corner(UP+RIGHT)
        arrow = Arrow(
            words.get_bottom(), neurons.get_top(),
            color = WHITE
        )

        self.play(
            Write(words, run_time = 1),
            GrowArrow(arrow)
        )
        vects = [np.random.random(10) for x in range(2)]
        vects += [np.zeros(10), 0.4*np.ones(10)]
        for vect in vects:
            neurons.generate_target()
            for neuron, o in zip(neurons, vect):
                neuron.generate_target()
                neuron.target.set_fill(WHITE, opacity = o)
            self.play(LaggedStartMap(
                MoveToTarget, neurons,
                run_time = 1
            ))
            self.wait()
        self.play(FadeOut(VGroup(words, arrow)))

    def feed_in_random_data(self):
        neurons = self.network_mob.layers[0].neurons
        rand_vect = self.rand_vect
        image = self.image.copy()
        output_labels = self.network_mob.output_labels

        opacities = it.chain(rand_vect[:8], rand_vect[-8:])
        target_neurons = neurons.copy()
        for n, o in zip(target_neurons, opacities):
            n.set_fill(WHITE, opacity = o)

        point = VectorizedPoint(neurons.get_center())
        image.target = VGroup(*it.chain(
            target_neurons[:len(neurons)/2],
            [point]*(len(image) - len(neurons)),
            target_neurons[-len(neurons)/2:]
        ))

        self.play(MoveToTarget(
            image, 
            run_time = 2,
            lag_ratio = 0.5
        ))
        self.activate_network(rand_vect, FadeOut(image))

        ### React ###
        neurons = self.network_mob.layers[-1].neurons
        choice = np.argmax([n.get_fill_opacity() for n in neurons])
        rect = SurroundingRectangle(VGroup(
            neurons[choice], output_labels[choice]
        ))
        word = TextMobject("What?!?")
        word.set_color(YELLOW)
        word.next_to(rect, RIGHT)

        self.play(ShowCreation(rect))
        self.play(Write(word, run_time = 1))
        self.wait()

        self.network_mob.add(rect, word)
        self.choice = choice

    def network_speaks(self):
        network_mob = self.network_mob
        network_mob.generate_target(use_deepcopy = True)
        network_mob.target.scale(0.7)
        network_mob.target.to_edge(DOWN)
        eyes = Eyes(
            network_mob.target.edge_groups[1],
            height = 0.45,
        )
        eyes.shift(0.5*SMALL_BUFF*UP)

        bubble = SpeechBubble(
            height = 3, width = 5,
            direction = LEFT
        )
        bubble.pin_to(network_mob.target.edge_groups[-1])
        bubble.write("Looks like a \\\\ %d to me!"%self.choice)

        self.play(
            MoveToTarget(network_mob),
            FadeIn(eyes)
        )
        self.play(eyes.look_at_anim(self.image))
        self.play(
            ShowCreation(bubble),
            Write(bubble.content, run_time = 1)
        )
        self.play(eyes.blink_anim())
        self.wait()

class CannotDraw(PreviewLearning):
    def construct(self):
        network_mob = self.network_mob
        self.color_network_edges()
        network_mob.scale(0.5)
        network_mob.to_corner(DOWN+RIGHT)
        eyes = Eyes(network_mob.edge_groups[1])
        eyes.shift(SMALL_BUFF*UP)
        self.add(eyes)

        bubble = SpeechBubble(
            height = 3, width = 4,
            direction = RIGHT
        )
        bubble.pin_to(network_mob.edge_groups[0])
        bubble.write("Uh...I'm really \\\\ more of a multiple \\\\ choice guy")

        randy = Randolph()
        randy.to_corner(DOWN+LEFT)
        eyes.look_at_anim(randy.eyes).update(1)

        self.play(PiCreatureSays(
            randy, "Draw a \\\\ 5 for me",
            look_at_arg = eyes,
            run_time = 1
        ))
        self.play(eyes.change_mode_anim("concerned_musician"))
        self.play(
            ShowCreation(bubble),
            Write(bubble.content),
            eyes.look_at_anim(network_mob.get_corner(DOWN+RIGHT))
        )
        self.play(eyes.blink_anim())
        self.play(Blink(randy))
        self.wait()

class TODOShowCostFunctionDef(TODOStub):
    CONFIG = {
        "message" : "Insert cost function averaging portion"
    }

class TODOBreakUpNineByPatterns2(TODOBreakUpNineByPatterns):
    pass

class SomethingToImproveUpon(PiCreatureScene, TestPerformance):
    CONFIG = {
        "n_examples" : 15,
        "time_per_example" : 0.15,
    }
    def setup(self):
        self.setup_bases()
        self.color_network_edges()
        self.network_mob.to_edge(LEFT)
        edge_update = ContinualEdgeUpdate(
            self.network_mob,
            colors = [BLUE, BLUE, RED]
        )
        edge_update.internal_time = 1
        self.add(edge_update)

    def construct(self):
        self.show_path()
        self.old_news()
        self.recognizing_digits()
        self.hidden_layers()

    def show_path(self):
        network_mob = self.network_mob
        morty = self.pi_creature

        line = Line(LEFT, RIGHT).scale(5)
        line.shift(UP)
        dots = VGroup(*[
            Dot(line.point_from_proportion(a))
            for a in np.linspace(0, 1, 5)
        ])
        dots.set_color_by_gradient(BLUE, YELLOW)
        path = VGroup(line, dots)
        words = TextMobject("This series")
        words.next_to(line, DOWN)

        self.play(
            network_mob.scale, 0.25,
            network_mob.next_to, path.get_right(), UP,
            ShowCreation(path),
            Write(words, run_time = 1),
            morty.change, "sassy", 
        )
        self.wait(2)
        self.play(
            ApplyMethod(
                network_mob.next_to, path.get_left(), UP,
                path_arc = np.pi/2,
            ),
            Rotate(path, np.pi, in_place = True),
            morty.change, "raise_right_hand"
        )
        self.wait(3)

        self.line = line
        self.path = path
        self.this_series = words

    def old_news(self):
        network_mob = self.network_mob
        morty = self.pi_creature
        line = self.line

        words = TextMobject("Old technology!")
        words.to_edge(UP)
        arrow = Arrow(words.get_left(), network_mob.get_right())

        name = TextMobject("``Multilayer perceptron''")
        name.next_to(words, DOWN)

        cnn = TextMobject("Convolutional NN")
        lstm = TextMobject("LSTM")
        cnn.next_to(line.get_center(), UP)
        lstm.next_to(line.get_right(), UP)

        modern_variants = VGroup(cnn, lstm)
        modern_variants.set_color(YELLOW)

        self.play(
            Write(words, run_time = 1),
            GrowArrow(arrow),
            morty.change_mode, "hesitant"
        )
        self.play(Write(name))
        self.wait()
        self.play(
            FadeIn(modern_variants),
            FadeOut(VGroup(words, arrow, name)),
            morty.change, "thinking"
        )
        self.wait(2)

        self.modern_variants = modern_variants

    def recognizing_digits(self):
        training_data, validation_data, test_data = load_data_wrapper()

        for v_in, choice in validation_data[:self.n_examples]:
            image = MNistMobject(v_in)
            image.set_height(1)
            choice = TexMobject(str(choice))
            choice.scale(2)
            arrow = Vector(RIGHT, color = WHITE)
            group = Group(image, arrow, choice)
            group.arrange(RIGHT)
            group.next_to(self.line, DOWN, LARGE_BUFF)
            group.to_edge(LEFT, buff = LARGE_BUFF)

            self.add(group)
            self.wait(self.time_per_example)
            self.remove(group)

    def hidden_layers(self):
        morty = self.pi_creature
        network_mob = self.network_mob

        self.play(
            network_mob.scale, 4, 
            network_mob.center, 
            network_mob.to_edge, LEFT,
            FadeOut(VGroup(self.path, self.modern_variants, self.this_series)),
            morty.change, "confused",
        )

        hidden_layers = network_mob.layers[1:3]
        rects = VGroup(*list(map(SurroundingRectangle, hidden_layers)))
        np.random.seed(0)

        self.play(ShowCreation(rects))
        self.activate_network(np.random.random(28*28))
        self.wait(3)

class ShiftingFocus(Scene):
    def construct(self):
        how, do, networks, learn = words = TextMobject(
            "How", "do", "neural networks", "learn?"
        )
        networks.set_color(BLUE)
        cross = Cross(networks)
        viewers = TextMobject("video viewers")
        viewers.move_to(networks)
        viewers.set_color(YELLOW)
        cap_do = TextMobject("Do")
        cap_do.move_to(do, DOWN+LEFT)

        self.play(Write(words, run_time = 1))
        self.wait()
        self.play(ShowCreation(cross))
        self.play(
            VGroup(networks, cross).shift, DOWN,
            Write(viewers, run_time = 1)
        )
        self.wait(2)
        self.play(
            FadeOut(how),
            Transform(do, cap_do)
        )
        self.wait(2)

class PauseAndPonder(TeacherStudentsScene):
    def construct(self):
        screen = ScreenRectangle(height = 3.5)
        screen.to_edge(UP+LEFT)

        self.teacher_says(
            "Pause and \\\\ ponder!",
            target_mode = "hooray",
            run_time = 1
        )
        self.play(
            ShowCreation(screen),
            self.get_student_changes(*["pondering"]*3),
        )
        self.wait(6)

class ConvolutionalNetworkPreview(Scene):
    def construct(self):
        vect = get_organized_images()[9][0]
        image = PixelsFromVect(vect)
        image.set_stroke(width = 1)
        image.set_height(FRAME_HEIGHT - 1)
        self.add(image)

        kernels = [
            PixelsFromVect(np.zeros(16))
            for x in range(2)
        ]
        for i, pixel in enumerate(kernels[0]):
            x = i%4
            y = i//4
            if x == y:
                pixel.set_fill(BLUE, 1)
            elif abs(x - y) == 1:
                pixel.set_fill(BLUE, 0.5)
        for i, pixel in enumerate(kernels[1]):
            x = i%4
            if x == 1:
                pixel.set_fill(BLUE, 1)
            elif x == 2:
                pixel.set_fill(RED, 1)
        for kernel in kernels:
            kernel.set_stroke(width = 1)
            kernel.scale(image[0].get_height()/kernel[0].get_height())
            kernel.add(SurroundingRectangle(
                kernel, color = YELLOW, buff = 0
            ))
            self.add(kernel)
            for i, pixel in enumerate(image):
                x = i%28
                y = i//28
                if x > 24 or y > 24:
                    continue
                kernel.move_to(pixel, UP+LEFT)
                self.wait(self.frame_duration)
            self.remove(kernel)

class RandomlyLabeledImageData(Scene):
    CONFIG = {
        "image_label_pairs" : [
            ("lion", "Lion"),
            ("Newton", "Genius"),
            ("Fork", "Fork"),
            ("Trilobite", "Trilobite"),
            ("Puppy", "Puppy"),
            ("Astrolabe", "Astrolabe"),
            ("Adele", "Songbird of \\\\ our generation"),
            ("Cow", "Cow"),
            ("Sculling", "Sculling"),
            ("Pierre_de_Fermat", "Tease"),
        ]
    }
    def construct(self):
        groups = Group()
        labels = VGroup()
        for i, (image_name, label_name) in enumerate(self.image_label_pairs):
            x = i//5
            y = i%5
            group = self.get_training_group(image_name, label_name)
            group.shift(4.5*LEFT + x*FRAME_X_RADIUS*RIGHT)
            group.shift(3*UP + 1.5*y*DOWN)
            groups.add(group)
            labels.add(group[-1])
        permutation = list(range(len(labels)))
        while any(np.arange(len(labels)) == permutation):
            random.shuffle(permutation)
        for label, i in zip(labels, permutation):
            label.generate_target()
            label.target.move_to(labels[i], LEFT)
            label.target.set_color(YELLOW)

        self.play(LaggedStartMap(
            FadeIn, groups,
            run_time = 3,
            lag_ratio = 0.3,
        ))
        self.wait()
        self.play(LaggedStartMap(
            MoveToTarget, labels, 
            run_time = 4,
            lag_ratio = 0.5,
            path_arc = np.pi/3,
        ))
        self.wait()

    def get_training_group(self, image_name, label_name):
        arrow = Vector(RIGHT, color = WHITE)
        image = ImageMobject(image_name)
        image.set_height(1.3)
        image.next_to(arrow, LEFT)
        label = TextMobject(label_name)
        label.next_to(arrow, RIGHT)
        group = Group(image, arrow, label)
        return group

class TrainOnImages(PreviewLearning, RandomlyLabeledImageData):
    CONFIG = {
        "layer_sizes" : [17, 17, 17, 17, 17, 17],
        "network_mob_config" : {
            "brace_for_large_layers" : False,
            "include_output_labels" : False,
        },
    }
    def construct(self):
        self.setup_network_mob()

        image_names, label_names = list(zip(*self.image_label_pairs))
        label_names = list(label_names)
        random.shuffle(label_names)
        groups = [
            self.get_training_group(image_name, label_name)
            for image_name, label_name in zip(image_names, label_names)
        ]


        edges = VGroup(*reversed(list(
            it.chain(*self.network_mob.edge_groups)
        )))

        for group in groups:
            for edge in edges:
                edge.generate_target()
                edge.target.rotate_in_place(np.pi)
                alt_edge = random.choice(edges)
                color = alt_edge.get_stroke_color()
                width = alt_edge.get_stroke_width()
                edge.target.set_stroke(color, width)

            group.to_edge(UP)
            self.add(group)
            self.play(LaggedStartMap(
                MoveToTarget, edges,
                lag_ratio = 0.4,
                run_time = 2,
            ))
            self.remove(group)

    def setup_network_mob(self):
        self.network_mob.set_height(5)
        self.network_mob.to_edge(DOWN)
        self.color_network_edges()

class IntroduceDeepNetwork(Scene):
    def construct(self):
        pass

class AskNetworkAboutMemorizing(YellAtNetwork):
    def construct(self):
        randy = self.pi_creature
        network_mob, eyes = self.get_network_and_eyes()
        eyes.look_at_anim(randy.eyes).update(1)
        self.add(eyes)

        self.pi_creature_says(
            "Are you just \\\\ memorizing?",
            target_mode = "sassy",
            look_at_arg = eyes,
            run_time = 2
        )
        self.wait()
        self.play(eyes.change_mode_anim("sad"))
        self.play(eyes.blink_anim())
        self.wait()

class CompareLearningCurves(GraphScene):
    CONFIG = {
        "x_min" : 0,
        "y_axis_label" : "Value of \\\\ cost function",
        "x_axis_label" : "Number of gradient \\\\ descent steps",
        "graph_origin" : 2*DOWN + 3.5*LEFT,
    }
    def construct(self):
        self.setup_axes()
        self.x_axis_label_mob.to_edge(DOWN)
        self.y_axis_label_mob.to_edge(LEFT)
        self.y_axis_label_mob.set_color(RED)

        slow_decrease = self.get_graph(
            lambda x : 9 - 0.25*x
        )
        faster_decrease = self.get_graph(
            lambda x : 4.3*sigmoid(5*(2-x)) + 3 + 0.5*ReLU(3-x)
        )
        for decrease, p in (slow_decrease, 0.2), (faster_decrease, 0.07):
            y_vals = decrease.get_anchors()[:,1]
            y_vals -= np.cumsum(p*np.random.random(len(y_vals)))
            decrease.make_jagged()
        faster_decrease.move_to(slow_decrease, UP+LEFT)

        slow_label = TextMobject("Randomly-labeled data")
        slow_label.set_color(slow_decrease.get_color())
        slow_label.to_corner(UP+RIGHT)
        slow_line = Line(ORIGIN, RIGHT)
        slow_line.set_stroke(slow_decrease.get_color(), 5)
        slow_line.next_to(slow_label, LEFT)

        fast_label = TextMobject("Properly-labeled data")
        fast_label.set_color(faster_decrease.get_color())
        fast_label.next_to(slow_label, DOWN)
        fast_line = slow_line.copy()
        fast_line.set_color(faster_decrease.get_color())
        fast_line.next_to(fast_label, LEFT)

        self.play(FadeIn(slow_label), ShowCreation(slow_line))
        self.play(ShowCreation(
            slow_decrease,
            run_time = 12,
            rate_func=linear,
        ))
        self.play(FadeIn(fast_label), ShowCreation(fast_line))
        self.play(ShowCreation(
            faster_decrease,
            run_time = 12,
            rate_func=linear,
        ))
        self.wait()

        ####

        line = Line(
            self.coords_to_point(1, 2),
            self.coords_to_point(3, 9),
        )
        rect = Rectangle()
        rect.set_fill(YELLOW, 0.3)
        rect.set_stroke(width = 0)
        rect.replace(line, stretch = True)

        words = TextMobject("Learns structured data more quickly")
        words.set_color(YELLOW)
        words.next_to(rect, DOWN)
        words.add_background_rectangle()

        self.play(DrawBorderThenFill(rect))
        self.play(Write(words))
        self.wait()

class ManyMinimaWords(Scene):
    def construct(self):
        words = TextMobject(
            "Many local minima,\\\\",
            "roughly equal quality"
        )
        words.set_width(FRAME_WIDTH - 1)
        words.to_edge(UP)
        self.play(Write(words))
        self.wait()


class NNPart2PatreonThanks(PatreonThanks):
    CONFIG = {
        "specific_patrons" : [
            "Desmos",
            "Burt Humburg",
            "CrypticSwarm",
            "Juan Benet",
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
            "Eric Chow",
            "Mathias Jansson",
            "Pedro Perez Sanchez",
            "David Clark",
            "Michael Gardner",
            "Harsev Singh",
            "Mads Elvheim",
            "Erik Sundell",
            "Xueqi Li",
            "David G. Stork",
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
            "Mark Govea",
            "Robert Teed",
            "Jason Hise",
            "Meshal Alshammari",
            "Bernd Sing",
            "James Thornton",
            "Mustafa Mahdi",
            "Mathew Bramson",
            "Jerry Ling",
            "Vecht",
            "Shimin Kuang",
            "Rish Kundalia",
            "Achille Brighton",
            "Ripta Pasay",
        ]
    }






























