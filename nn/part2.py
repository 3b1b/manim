import sys
import os.path
import cv2

from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject, Group
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
from topics.graph_scene import *
from topics.common_scenes import *
from scene import Scene
from scene.reconfigurable_scene import ReconfigurableScene
from scene.zoomed_scene import *
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

from nn.network import *
from nn.part1 import *

def get_training_image_group(train_in, train_out):
    image = MNistMobject(train_in)
    image.scale_to_fit_height(1)
    arrow = Vector(RIGHT, color = BLUE, buff = 0)
    output = np.argmax(train_out)
    output_tex = TexMobject(str(output)).scale(1.5)
    result = Group(image, arrow, output_tex)
    result.arrange_submobjects(RIGHT)
    result.to_edge(UP)
    return result

########

class ShowLastVideo(TeacherStudentsScene):
    def construct(self):
        frame = ScreenRectangle()
        frame.scale_to_fit_height(4.5)
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
        self.dither(5)

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
        "positive_change_color" : average_color(*2*[BLUE] + [YELLOW]),
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
        edge_animation = LaggedStart(
            ShowCreationThenDestruction, 
            all_edges.copy().set_fill(YELLOW),
            run_time = run_time,
            lag_ratio = 0.3,
            remover = True,
        )
        layer_animation = Transform(
            VGroup(*layers), VGroup(*active_layers),
            run_time = run_time,
            submobject_mode = "lagged_start",
            rate_func = None,
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
        tups = zip(
            it.count(), nabla_b, nabla_w, 
            delta_neuron_groups, neuron_groups,
            delta_edge_groups, edge_groups
        )
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
                    delta_edges, submobject_mode = "all_at_once"
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
            map(FadeOut, [delta_edge_groups, delta_neuron_groups]),
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
        return LaggedStart(
            ApplyFunction, edges,
            lambda mob : (
                lambda m : m.rotate_in_place(np.pi/12).highlight(YELLOW),
                mob
            ),
            rate_func = wiggle
        )

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
        group.arrange_submobjects(DOWN)
        group.scale(0.5)
        return group

    def introduce_all_data(self):
        training_examples, test_examples = [
            self.get_examples() for x in range(2)
        ]

        training_examples.next_to(ORIGIN, LEFT)
        test_examples.next_to(ORIGIN, RIGHT)
        self.play(
            LaggedStart(FadeIn, training_examples),
            LaggedStart(FadeIn, test_examples),
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
                mark.highlight(GREEN)
            else:
                mark = TexMobject("\\times")
                mark.highlight(RED)
            mark.next_to(test_example, LEFT)
            marks.add(mark)

        self.play(
            MoveToTarget(training_examples),
            GrowFromCenter(train_brace),
            FadeIn(train_words)
        )
        self.dither()
        self.play(
            MoveToTarget(test_examples),
            GrowFromCenter(test_brace),
            FadeIn(test_words)
        )
        self.play(Write(marks))
        self.dither()

    def scroll_through_much_data(self):
        training_examples = self.training_examples
        colors = color_gradient([BLUE, YELLOW], self.n_new_examples_shown)
        for color in colors:
            new_examples = self.get_examples()
            new_examples.move_to(training_examples)
            for train_ex, new_ex in zip(training_examples, new_examples):
                self.remove(train_ex)
                self.add(new_ex)
                new_ex[0][0].highlight(color)
                self.dither(1./30)
            training_examples = new_examples

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
        self.dither()
        students[0].bubble = bubble
        self.teacher_says(
            "It's actually \\\\ just calculus.",
            run_time = 1
        )
        self.teacher.bubble = None
        self.dither()
        self.student_says(
            "Even worse!", 
            target_mode = "horrified",
            bubble_kwargs = {
                "direction" : LEFT, 
                "width" : 3,
                "height" : 2,
            },
        )
        self.dither(2)

class FunctionMinmization(GraphScene):
    CONFIG = {
        "x_labeled_nums" : range(-1, 10),
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
        dots.gradient_highlight(YELLOW, RED)

        def update_dot(dot, dt):
            x = self.x_axis.point_to_number(dot.get_center())
            slope = self.slope_of_tangent(x, graph)
            x -= slope*dt
            dot.move_to(self.input_to_graph_point(x, graph))

        self.add(*[
            ContinualUpdateFromFunc(dot, update_dot)
            for dot in dots
        ])
        self.dither(10)

class IntroduceCostFunction(PreviewLearning):
    CONFIG = {
        "max_stroke_width" : 2,
        "full_edges_exp" : 5,
        "n_training_examples" : 100,
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
            "submobject_mode" : "lagged_start",
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
            for tex in "=", "+", "dots"
        ])

        w_labels.highlight(GREEN)
        b.highlight(BLUE)
        sigma.highlight(YELLOW)
        # formula.to_edge(UP)
        formula.next_to(neuron, RIGHT)

        weights_word = TextMobject("Weights")
        weights_word.next_to(neuron.edges_in, RIGHT, aligned_edge = UP)
        weights_word.highlight(GREEN)
        weights_arrow_to_edges = Arrow(
            weights_word.get_bottom(),
            neuron.edges_in[0].get_center(),
            color = GREEN
        )

        weights_arrow_to_syms = VGroup(*[
            Arrow(
                weights_word.get_bottom(),
                w_label.get_top(),
                color = GREEN
            )
            for w_label in w_labels
        ])

        bias_word = TextMobject("Bias")
        bias_arrow = Vector(DOWN, color = BLUE)
        bias_arrow.next_to(b, UP, SMALL_BUFF)
        bias_word.next_to(bias_arrow, UP, SMALL_BUFF)
        bias_word.highlight(BLUE)

        self.play(
            Transform(layer0, active_layer0),
            neuron.set_fill, None, 0.5,
            FadeIn(formula),
            run_time = 2,
            submobject_mode = "lagged_start"
        )
        self.play(LaggedStart(
            ShowCreationThenDestruction, 
            neuron.edges_in.copy().set_stroke(YELLOW, 3),
            run_time = 1.5,
            lag_ratio = 0.7,
            remover = True
        ))
        self.play(
            Write(weights_word),
            *map(GrowArrow, weights_arrow_to_syms),
            run_time = 1
        )
        self.dither()
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
        self.dither()
        self.play(
            Write(bias_word),
            GrowArrow(bias_arrow),
            run_time = 1
        )
        self.dither(2)

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
        self.play(LaggedStart(
            ApplyMethod, neuron.edges_in,
            lambda m : (m.rotate_in_place, np.pi/12),
            rate_func = wiggle,
            run_time = 2
        ))
        self.play(*map(FadeOut, [
            weights_word, weights_arrow_to_edges,
            bias_word, bias_arrow,
            formula
        ]))

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
            LaggedStart(
                FadeIn, group,
                run_time = 3,
            )
            for group in neurons, edges
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
            layer0.neurons[:n/2],
            [
                VectorizedPoint(layer0.dots.get_center())
                for x in xrange(len(neurons)-n)
            ],
            layer0.neurons[-n/2:]
        ))

        self.play(
            self.network_mob.shift, 0.5*RIGHT,
            ShowCreation(rect),
            LaggedStart(DrawBorderThenFill, image),
            LaggedStart(DrawBorderThenFill, neurons),
            run_time = 1
        )
        self.play(MoveToTarget(
            neurons, submobject_mode = "lagged_start",
            remover = True
        ))
        self.activate_network(vect, run_time = 2)

        self.image = image
        self.image_rect = rect

    def make_fun_of_output(self):
        last_layer = self.network_mob.layers[-1].neurons
        last_layer.add(self.network_mob.output_labels)
        rect = SurroundingRectangle(last_layer)
        words = TextMobject("Utter trash")
        words.next_to(rect, DOWN, aligned_edge = LEFT)
        VGroup(rect, words).highlight(YELLOW)

        self.play(
            ShowCreation(rect),
            Write(words, run_time = 2)
        )
        self.dither()

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
        words.highlight_by_tex("cost", RED)
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
        self.dither(2)

        self.desired_last_layer = desired_layer
        self.diff_arrow = double_arrow

    def fade_all_but_last_layer(self):
        network_mob = self.network_mob
        to_fade = VGroup(*it.chain(*zip(
            network_mob.layers[:-1],
            network_mob.edge_groups
        )))

        self.play(LaggedStart(FadeOut, to_fade, run_time = 1))

    def break_down_cost_function(self):
        layer = self.network_mob.layers[-1]
        desired_layer = self.desired_last_layer
        decimal_groups = VGroup(*[
            self.num_vect_to_decimals(self.layer_to_num_vect(l))
            for l in layer, desired_layer
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
        terms.arrange_submobjects(
            DOWN, buff = SMALL_BUFF,
            aligned_edge = LEFT
        )
        terms.scale_to_fit_height(1.5*layer.get_height())
        terms.next_to(layer, LEFT, buff = 2)

        image_group = Group(self.image, self.image_rect)
        image_group.generate_target()
        image_group.target.scale(0.5)
        cost_of = TextMobject("Cost of").highlight(RED)
        cost_group = VGroup(cost_of, image_group.target)
        cost_group.arrange_submobjects(RIGHT)
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
        self.dither()

        self.decimal_groups = decimal_groups
        self.image_group = image_group
        self.cost_group = VGroup(cost_of, image_group)

    def average_over_all_training_data(self):
        image_group = self.image_group
        decimal_groups = self.decimal_groups

        random_neurons = self.network_mob.layers[-1].neurons
        desired_neurons = self.desired_last_layer.neurons

        dither_times = iter(it.chain(
            4*[0.5],
            4*[0.25],
            8*[0.125],
            it.repeat(0.1)
        ))

        words = TextMobject("Average cost of \\\\ all training data...")
        words.highlight(BLUE)
        words.to_corner(UP+LEFT)

        self.play(
            Write(words, run_time = 1),
        )

        training_data, validation_data, test_data = load_data_wrapper()
        for in_vect, out_vect in training_data[:self.n_training_examples]:
            random_v = np.random.random(10)
            new_decimal_groups = VGroup(*[
                self.num_vect_to_decimals(v)
                for v in random_v, out_vect
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

            self.dither(dither_times.next())

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
        decimals.arrange_submobjects(DOWN)
        decimals.scale_to_fit_height(height)
        lb, rb = brackets = TexMobject("[]")
        brackets.scale(2)
        brackets.stretch_to_fit_height(height + SMALL_BUFF)
        lb.next_to(decimals, LEFT)
        rb.next_to(decimals, RIGHT)
        result = VGroup(brackets, decimals)
        result.brackets = brackets
        result.decimals = decimals
        return result

class ThisIsVeryComplicated(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Very complicated!",
            target_mode = "surprised",
            run_time = 1,
        )
        self.change_student_modes(*3*["guilty"])
        self.dither(2)

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
        v_line = Line(UP, DOWN).scale(SPACE_HEIGHT)
        network_mob = self.network_mob
        network_mob.scale_to_fit_width(SPACE_WIDTH - 1)
        network_mob.to_corner(DOWN+LEFT)

        self.add(v_line)
        self.color_network_edges()

    def show_network_as_a_function(self):
        title = TextMobject("Neural network function")
        title.shift(SPACE_WIDTH*RIGHT/2)
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
        image.scale_to_fit_height(1.5)
        image_label = TextMobject("Input")
        image_label.highlight(input_words[0].get_color())
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

        self.play(FadeIn(input_words[1], submobject_mode = "lagged_start"))
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
        self.dither()
        self.play(
            FadeIn(parameter_words[1]), 
            self.get_edge_animation()
        )
        self.dither(2)

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
        network_label.highlight(input_words[0].get_color())
        network_label.next_to(rect, UP, SMALL_BUFF)

        new_output_word = TextMobject("1 number", "(the cost)")
        new_output_word[1].highlight(RED).scale(0.9)
        new_output_word.move_to(output_words[1], LEFT)
        new_output_word.shift(0.5*SMALL_BUFF*DOWN)
        new_parameter_word = TextMobject("""
            \\begin{flushleft}
            Many, many, many \\\\ training examples
            \\end{flushleft}
        """).scale(0.9)
        new_parameter_word.move_to(parameter_words[1], UP+LEFT) 

        new_title = TextMobject("Cost function")
        new_title.highlight(RED)
        new_title.move_to(self.title)

        arrow = Arrow(UP, DOWN, color = WHITE)
        arrow.next_to(rect, DOWN)
        cost = TextMobject("Cost: 5.4")
        cost.highlight(RED)
        cost.next_to(arrow, DOWN)

        training_data, validation_data, test_data = load_data_wrapper()
        training_examples = Group(*map(
            self.get_training_pair_mob, 
            training_data[:self.n_examples]
        ))
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
        self.dither()
        self.play(
            GrowArrow(arrow),
            Write(cost, run_time = 1)
        )
        self.play(Write(new_output_word, run_time = 1))
        self.dither()
        self.play(
            FadeIn(new_parameter_word),
            FadeIn(training_examples[0])
        )
        self.dither(0.5)
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
            self.dither(0.25)

    ####

    def get_function_description_words(self, w1, w2, w3):
        input_words = TextMobject("Input:", w1)
        input_words[0].highlight(BLUE)
        output_words = TextMobject("Output:", w2)
        output_words[0].highlight(YELLOW)
        parameter_words = TextMobject("Parameters:", w3)
        parameter_words[0].highlight(GREEN)
        words = VGroup(input_words, output_words, parameter_words)
        words.arrange_submobjects(DOWN, aligned_edge = LEFT)
        words.scale(0.9)
        words.next_to(ORIGIN, RIGHT)
        words.shift(UP)
        return words

    def get_training_pair_mob(self, data):
        in_vect, out_vect = data
        image = MNistMobject(in_vect)
        image.scale_to_fit_height(1)
        comma = TextMobject(",")
        comma.next_to(image, RIGHT, SMALL_BUFF, DOWN)
        output = TexMobject(str(np.argmax(out_vect)))
        output.scale_to_fit_height(0.75)
        output.next_to(image, RIGHT, MED_SMALL_BUFF)
        lp, rp = parens = TextMobject("()")
        parens.scale(2)
        parens.stretch_to_fit_height(1.2*image.get_height())
        lp.next_to(image, LEFT, SMALL_BUFF)
        rp.next_to(lp, RIGHT, buff = 2)

        result = Group(lp, image, comma, output, rp)
        result.in_vect = in_vect
        return result


class YellAtNetwork(PiCreatureScene, PreviewLearning):
    def setup(self):
        PiCreatureScene.setup(self)
        PreviewLearning.setup(self)

    def construct(self):
        randy = self.randy

        network_mob = self.network_mob
        network_mob.scale(0.5)
        network_mob.next_to(randy, RIGHT, LARGE_BUFF)
        self.color_network_edges()
        eyes = Eyes(network_mob.edge_groups[1])

        self.play(
            PiCreatureBubbleIntroduction(
                randy, "Horrible!",
                target_mode = "angry", 
                look_at_arg = eyes,
                run_time = 1,
            ),
            eyes.look_at_anim(randy.eyes)
        )
        self.play(eyes.change_mode_anim("sad"))
        self.play(eyes.look_at_anim(3*DOWN + 3*RIGHT))
        self.dither()
        self.play(eyes.blink_anim())
        self.dither()

    ####

    def create_pi_creature(self):
        randy = self.randy = Randolph()
        randy.shift(3*LEFT + DOWN)
        return randy

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
            VGroup(cf[0], cf[2]).highlight(RED)
        big_brace, lil_brace = [
            Brace(cf[1], DOWN)
            for cf in cf1, cf2
        ]
        big_brace_text = big_brace.get_text("Weights and biases")
        lil_brace_text = lil_brace.get_text("Single input")

        name.next_to(cf1, UP, LARGE_BUFF)
        name.highlight(RED)

        self.add(name, cf1)
        self.play(
            GrowFromCenter(big_brace),
            FadeIn(big_brace_text)
        )
        self.dither()
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
        self.dither()

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
        self.dither()
        self.play(Write(formula, run_time = 2))
        self.play(GrowArrow(arrow))
        self.dither()

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
        words.highlight(BLUE)
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
        self.dither(2)
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
            arrow.highlight(color)
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
        self.dither()
        self.play(*it.chain(
            map(GrowArrow, arrows),
            map(FadeIn, q_marks),
        ))
        self.dither()

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
        self.dither()

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
        self.dither()
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
        self.dither()
        for x in 0.8, 1.1, 0.95:
            self.play(
                w_mob.next_to, self.coords_to_point(x, 0), DOWN,
                line_update_anim,
                dot_update_anim,
            )
        self.dither()

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
        self.dither(2)

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
                ContinualUpdateFromFunc(point, update_point),
                ContinualUpdateFromFunc(new_ball, update_ball)
            ]
        balls.gradient_highlight(BLUE, GREEN)

        self.play(ReplacementTransform(ball, balls))
        self.add(*updates)
        self.dither(5)
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
            self.dither(0.5)
        self.dither()

    ###

    def get_tangent_line(self, x, color = YELLOW):
        tangent_line = Line(LEFT, RIGHT).scale(3)
        tangent_line.highlight(color)
        self.make_line_tangent(tangent_line, x)
        return tangent_line

    def make_line_tangent(self, line, x):
        graph = self.graph
        line.rotate(self.angle_of_tangent(x, graph) - line.get_angle())
        line.move_to(self.input_to_graph_point(x, graph))





















