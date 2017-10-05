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
        "positive_change_color" : average_color(*2*[GREEN] + [YELLOW]),
        "negative_change_color" : average_color(*2*[RED] + [YELLOW]),
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

    def activate_network(self, train_in, *added_anims):
        network_mob = self.network_mob
        layers = network_mob.layers
        layers.save_state()
        activations = self.network.get_activation_of_all_layers(train_in)
        active_layers = [
            self.network_mob.get_active_layer(i, vect)
            for i, vect in enumerate(activations)
        ]
        all_edges = VGroup(*it.chain(*network_mob.edge_groups))
        edge_animation = LaggedStart(
            ShowCreationThenDestruction, 
            all_edges.copy().set_fill(YELLOW),
            run_time = 1.5,
            lag_ratio = 0.3,
            remover = True,
        )
        layer_animation = Transform(
            VGroup(*layers), VGroup(*active_layers),
            run_time = 1.5,
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
                    color = GREEN if w > 0 else RED
                    msw = self.max_stroke_width
                    swe = self.stroke_width_exp
                    sw = msw*(abs(w)/matrix_max)**swe
                    sw = min(sw, msw)
                    edge.set_stroke(color, sw)

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
    def construct(self):
        self.force_skipping()

        self.isolate_one_neuron()
        self.reminder_of_weights_and_bias()
        self.initialize_randomly()
        self.feed_in_example()
        self.make_fun_of_output()
        self.need_a_cost_function()
        self.show_cost_function()

    def isolate_one_neuron(self):
        network_mob = self.network_mob
        network_mob.shift(LEFT)
        neuron_groups = VGroup(*[
            layer.neurons
            for layer in network_mob.layers[1:]
        ])
        edge_groups = network_mob.edge_groups
        neuron = neuron_groups[0][7].deepcopy()
        output_labels = network_mob.output_labels
        kwargs = {
            "submobject_mode" : "lagged_start",
            "run_time" : 2,
        }
        self.play(
            FadeOut(edge_groups, **kwargs),
            FadeOut(neuron_groups, **kwargs),
            FadeOut(output_labels, **kwargs),
            Animation(neuron),
            neuron.edges_in.set_stroke, None, 2,
        )
        self.dither()

        self.neuron = neuron

    def reminder_of_weights_and_bias(self):
        neuron = self.neuron
        layer0 = self.network_mob.layers[0]
        active_layer0 = self.network_mob.get_active_layer(
            0, np.random.random(len(layer0.neurons))
        )
        prev_neurons = layer0.neurons

        weights = 4*(np.random.random(len(neuron.edges_in))-0.5)
        weighted_edges = VGroup(*[
            edge.copy().set_stroke(
                color = GREEN if w > 0 else RED,
                width = abs(w)
            )
            for w, edge in zip(weights, neuron.edges_in)
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
        weights_arrow = Arrow(
            weights_word.get_bottom(),
            neuron.edges_in[0].get_center(),
            color = GREEN
        )

        alt_weights_arrows = VGroup(*[
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

        self.revert_to_original_skipping_status()
        self.play(
            Transform(layer0, active_layer0),
            FadeIn(a_labels),
            FadeIn(symbols),
            run_time = 2,
            submobject_mode = "lagged_start"
        )
        self.play(
            Write(weights_word),
            GrowArrow(weights_arrow),
            Transform(neuron.edges_in, weighted_edges),
            run_time = 1,
        )
        self.dither()
        self.play(
            ReplacementTransform(
                weighted_edges.copy(), w_labels,
            ),
            ReplacementTransform(
                VGroup(weights_arrow),
                alt_weights_arrows
            )
        )
        self.dither()
        self.play(
            Write(b),
            Write(bias_word),
            GrowArrow(bias_arrow),
            run_time = 1
        )
        self.play(Write(sigma))
        self.dither(2)

    def initialize_randomly(self):
        pass

    def feed_in_example(self):
        pass

    def make_fun_of_output(self):
        pass

    def need_a_cost_function(self):
        pass

    def show_cost_function(self):
        pass


    ####

    def activate_network(self, train_in, *added_anims):
        ##TODO
        PreviewLearning.activate_network(self, train_in, *added_anims)





































