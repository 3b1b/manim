import sys
import os.path

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
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
from scene import Scene
from scene.reconfigurable_scene import ReconfigurableScene
from scene.zoomed_scene import *
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

from nn.network import *

#force_skipping
#revert_to_original_skipping_status

class WrappedImage(Group):
    CONFIG = {
        "rect_kwargs" : {
            "color" : BLUE,
            "buff" : SMALL_BUFF,
        }
    }
    def __init__(self, image_mobject, **kwargs):
        Group.__init__(self, **kwargs)
        rect = SurroundingRectangle(
            image_mobject, **self.rect_kwargs
        )
        self.add(rect, image_mobject)

class PixelsAsSquares(VGroup):
    CONFIG = {
        "height" : 2,
    }
    def __init__(self, image_mobject, **kwargs):
        VGroup.__init__(self, **kwargs)
        for row in image_mobject.pixel_array:
            for rgba in row:
                square = Square(
                    stroke_width = 0, 
                    fill_opacity = rgba[3]/255.0,
                    fill_color = rgba_to_color(rgba/255.0),
                )
                self.add(square)
        self.arrange_submobjects_in_grid(
            *image_mobject.pixel_array.shape[:2],
            buff = 0
        )
        self.replace(image_mobject)

class PixelsFromVect(PixelsAsSquares):
    def __init__(self, vect, **kwargs):
        PixelsAsSquares.__init__(self,
            ImageMobject(layer_to_image_array(vect)),
            **kwargs
        )

class MNistMobject(WrappedImage):
    def __init__(self, vect, **kwargs):
        WrappedImage.__init__(self, 
            ImageMobject(layer_to_image_array(vect)),
            **kwargs
        )

class NetworkMobject(VGroup):
    CONFIG = {
        "neuron_radius" : 0.15,
        "neuron_to_neuron_buff" : MED_SMALL_BUFF,
        "layer_to_layer_buff" : LARGE_BUFF,
        "neuron_stroke_color" : BLUE,
        "neuron_stroke_width" : 3,
        "neuron_fill_color" : GREEN,
        "edge_color" : LIGHT_GREY,
        "edge_stroke_width" : 2,
        "edge_propogation_color" : GREEN,
        "edge_propogation_time" : 1,
        "max_shown_neurons" : 16,
        "brace_for_large_layers" : True,
        "average_shown_activation_of_large_layer" : True,
    }
    def __init__(self, neural_network, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.neural_network = neural_network
        self.layer_sizes = neural_network.sizes
        self.add_neurons()
        self.add_edges()

    def add_neurons(self):
        layers = VGroup(*[
            self.get_layer(size)
            for size in self.layer_sizes
        ])
        layers.arrange_submobjects(RIGHT, buff = self.layer_to_layer_buff)
        self.layers = layers
        self.add(self.layers)

    def get_layer(self, size):
        layer = VGroup()
        n_neurons = size
        if n_neurons > self.max_shown_neurons:
            n_neurons = self.max_shown_neurons
        neurons = VGroup(*[
            Circle(
                radius = self.neuron_radius,
                stroke_color = self.neuron_stroke_color,
                stroke_width = self.neuron_stroke_width,
            )
            for x in range(n_neurons)
        ])   
        neurons.arrange_submobjects(
            DOWN, buff = self.neuron_to_neuron_buff
        )
        for neuron in neurons:
            neuron.edges_in = VGroup()
            neuron.edges_out = VGroup()
        layer.neurons = neurons
        layer.add(neurons)

        if size > n_neurons:
            dots = TexMobject("\\vdots")
            dots.move_to(neurons)
            VGroup(*neurons[:len(neurons)/2]).next_to(
                dots, UP, MED_SMALL_BUFF
            )
            VGroup(*neurons[len(neurons)/2:]).next_to(
                dots, DOWN, MED_SMALL_BUFF
            )
            layer.dots = dots
            layer.add(dots)
            if self.brace_for_large_layers:
                brace = Brace(layer, LEFT)
                brace_label = brace.get_tex(str(size))
                layer.brace = brace
                layer.brace_label = brace_label
                layer.add(brace, brace_label)

        return layer

    def add_edges(self):
        self.edge_groups = VGroup()
        for l1, l2 in zip(self.layers[:-1], self.layers[1:]):
            edge_group = VGroup()
            for n1, n2 in it.product(l1.neurons, l2.neurons):
                edge = Line(
                    n1.get_center(),
                    n2.get_center(),
                    buff = self.neuron_radius,
                    stroke_color = self.edge_color,
                    stroke_width = self.edge_stroke_width,
                )
                edge_group.add(edge)
                n1.edges_out.add(edge)
                n2.edges_in.add(edge)
            self.edge_groups.add(edge_group)
        self.add_to_back(self.edge_groups)

    def get_active_layer(self, layer_index, activation_vector):
        layer = self.layers[layer_index].deepcopy()
        n_neurons = len(layer.neurons)
        av = activation_vector
        def arr_to_num(arr):
            return (np.sum(arr > 0.1) / float(len(arr)))**(1./3)

        if len(av) > n_neurons:
            if self.average_shown_activation_of_large_layer:
                indices = np.arange(n_neurons)
                indices *= int(len(av)/n_neurons)
                indices = list(indices)
                indices.append(len(av))
                av = np.array([
                    arr_to_num(av[i1:i2])
                    for i1, i2 in zip(indices[:-1], indices[1:])
                ])
            else:
                av = np.append(
                    av[:n_neurons/2],
                    av[-n_neurons/2:],
                )
        for activation, neuron in zip(av, layer.neurons):
            neuron.set_fill(
                color = self.neuron_fill_color,
                opacity = activation
            )
        return layer

    def deactivate_layers(self):
        all_neurons = VGroup(*it.chain(*[
            layer.neurons
            for layer in self.layers
        ]))
        all_neurons.set_fill(opacity = 0)
        return self

    def get_edge_propogation_animations(self, index):
        edge_group_copy = self.edge_groups[index].copy()
        edge_group_copy.set_stroke(
            self.edge_propogation_color,
            width = 1.5*self.edge_stroke_width
        )
        return [
            ShowCreationThenDestruction(
                mob, 
                run_time = self.edge_propogation_time
            )
            for mob in edge_group_copy
        ]

class MNistNetworkMobject(NetworkMobject):
    CONFIG = {
        "neuron_to_neuron_buff" : SMALL_BUFF,
        "layer_to_layer_buff" : 1.5,
        "edge_stroke_width" : 1,
    }

    def __init__(self, **kwargs):
        network = get_pretrained_network()
        NetworkMobject.__init__(self, network, **kwargs)
        self.add_output_labels()

    def add_output_labels(self):
        self.output_labels = VGroup()
        for n, neuron in enumerate(self.layers[-1].neurons):
            label = TexMobject(str(n))
            label.scale_to_fit_height(0.75*neuron.get_height())
            label.move_to(neuron)
            label.shift(neuron.get_width()*RIGHT)
            self.output_labels.add(label)
        self.add(self.output_labels)

class NetworkScene(Scene):
    CONFIG = {
        "layer_sizes" : [8, 6, 6, 4],
    }
    def setup(self):
        self.add_network()

    def add_network(self):
        self.network = Network(sizes = self.layer_sizes)
        self.network_mob = NetworkMobject(self.network)
        self.add(self.network_mob)

    def feed_forward(self, input_vector, false_confidence = False, added_anims = None):
        if added_anims is None:
            added_anims = []
        activations = self.network.get_activation_of_all_layers(
            input_vector
        )
        if false_confidence:
            i = np.argmax(activations[-1])
            activations[-1] *= 0
            activations[-1][i] = 1.0
        for i, activation in enumerate(activations):
            self.show_activation_of_layer(i, activation, added_anims)
            added_anims = []

    def show_activation_of_layer(self, layer_index, activation_vector, added_anims = None):
        if added_anims is None:
            added_anims = []
        layer = self.network_mob.layers[layer_index]
        active_layer = self.network_mob.get_active_layer(
            layer_index, activation_vector
        )
        anims = [Transform(layer, active_layer)]
        if layer_index > 0:
            anims += self.network_mob.get_edge_propogation_animations(
                layer_index-1
            )
        anims += added_anims
        self.play(*anims)

    def remove_random_edges(self, prop = 0.9):
        for edge_group in self.network_mob.edge_groups:
            for edge in list(edge_group):
                if np.random.random() < prop:
                    edge_group.remove(edge)

###############################

class ExampleThrees(PiCreatureScene):
    def construct(self):
        self.show_initial_three()
        self.show_alternate_threes()
        self.resolve_remaining_threes()
        self.show_alternate_digits()

    def show_initial_three(self):
        randy = self.pi_creature

        self.three_mobs = self.get_three_mobs()
        three_mob = self.three_mobs[0]
        three_mob_copy = three_mob[1].copy()
        three_mob_copy.sort_submobjects(lambda p : np.dot(p, DOWN+RIGHT))

        braces = VGroup(*[Brace(three_mob, v) for v in LEFT, UP])
        brace_labels = VGroup(*[
            brace.get_text("28px")
            for brace in braces
        ])

        bubble = randy.get_bubble(height = 4, width = 6)
        three_mob.generate_target()
        three_mob.target.scale_to_fit_height(1)
        three_mob.target.next_to(bubble[-1].get_left(), RIGHT, LARGE_BUFF)
        arrow = Arrow(LEFT, RIGHT, color = BLUE)
        arrow.next_to(three_mob.target, RIGHT)
        real_three = TexMobject("3")
        real_three.scale_to_fit_height(0.8)
        real_three.next_to(arrow, RIGHT)

        self.play(
            FadeIn(three_mob[0]),
            LaggedStart(FadeIn, three_mob[1])
        )
        self.dither()
        self.play(
            LaggedStart(
                DrawBorderThenFill, three_mob_copy,
                run_time = 3,
                stroke_color = WHITE,
                remover = True,
            ),
            randy.change, "sassy",
            *it.chain(
                map(GrowFromCenter, braces),
                map(FadeIn, brace_labels)
            )
        )
        self.dither()
        self.play(
            ShowCreation(bubble),
            MoveToTarget(three_mob),
            FadeOut(braces),
            FadeOut(brace_labels),
            randy.change, "pondering"
        )
        self.play(
            ShowCreation(arrow),
            Write(real_three)
        )
        self.dither()

        self.bubble = bubble
        self.arrow = arrow
        self.real_three = real_three

    def show_alternate_threes(self):
        randy = self.pi_creature

        three = self.three_mobs[0]
        three.generate_target()
        three.target[0].set_fill(opacity = 0, family = False)
        for square in three.target[1]:
            yellow_rgb = color_to_rgb(YELLOW)
            square_rgb = color_to_rgb(square.get_fill_color())
            square.set_fill(
                rgba_to_color(yellow_rgb*square_rgb),
                opacity = 0.5
            )

        alt_threes = VGroup(*self.three_mobs[1:])
        alt_threes.arrange_submobjects(DOWN)
        alt_threes.scale_to_fit_height(2*SPACE_HEIGHT - 2)
        alt_threes.to_edge(RIGHT)

        for alt_three in alt_threes:
            self.add(alt_three)
            self.dither(0.5)
        self.play(
            randy.change, "plain",
            *map(FadeOut, [
                self.bubble, self.arrow, self.real_three
            ]) + [MoveToTarget(three)]
        )
        for alt_three in alt_threes[:2]:
            self.play(three.replace, alt_three)
            self.dither()
        for moving_three in three, alt_threes[1]:
            moving_three.generate_target()
            moving_three.target.next_to(alt_threes, LEFT, LARGE_BUFF)
            moving_three.target[0].set_stroke(width = 0)
            moving_three.target[1].space_out_submobjects(1.5)
            self.play(MoveToTarget(
                moving_three, submobject_mode = "lagged_start"
            ))
            self.play(
                Animation(randy),
                moving_three.replace, randy.eyes[1],
                moving_three.scale_in_place, 0.7,
                run_time = 2,
                submobject_mode = "lagged_start",
            )
            self.play(
                Animation(randy),
                FadeOut(moving_three)
            )

        self.remaining_threes = [alt_threes[0], alt_threes[2]]

    def resolve_remaining_threes(self):
        randy = self.pi_creature

        left_three, right_three = self.remaining_threes
        equals = TexMobject("=")
        equals.move_to(self.arrow)
        for three, vect in (left_three, LEFT), (right_three, RIGHT):
            three.generate_target()
            three.target.scale_to_fit_height(1)
            three.target.next_to(equals, vect)

        self.play(
            randy.change, "thinking",
            ShowCreation(self.bubble),
            MoveToTarget(left_three),
            MoveToTarget(right_three),
            Write(equals),
        )
        self.dither()

        self.equals = equals

    def show_alternate_digits(self):
        randy = self.pi_creature
        cross = Cross(self.equals)
        cross.stretch_to_fit_height(0.5)
        three = self.remaining_threes[1]

        image_map = get_organized_images()
        arrays = [image_map[k][0] for k in range(8, 4, -1)]
        alt_mobs = [
            WrappedImage(
                PixelsAsSquares(ImageMobject(layer_to_image_array(arr))),
                color = LIGHT_GREY,
                buff = 0
            ).replace(three)
            for arr in arrays
        ]

        self.play(
            randy.change, "sassy",
            Transform(three, alt_mobs[0]),
            ShowCreation(cross)
        )
        self.dither()
        for mob in alt_mobs[1:]:
            self.play(Transform(three, mob))
            self.dither()

    ######

    def create_pi_creature(self):
        return Randolph().to_corner(DOWN+LEFT)

    def get_three_mobs(self):
        three_arrays = get_organized_images()[3][:4]
        three_mobs = VGroup()
        for three_array in three_arrays:
            im_mob = ImageMobject(
                layer_to_image_array(three_array),
                height = 4,
            )
            pixel_mob = PixelsAsSquares(im_mob)
            three_mob = WrappedImage(
                pixel_mob,
                color = LIGHT_GREY,
                buff = 0
            )
            three_mobs.add(three_mob)
        return three_mobs

class WriteAProgram(Scene):
    def construct(self):
        three_array = get_organized_images()[3][0]
        im_mob = ImageMobject(layer_to_image_array(three_array))
        three = PixelsAsSquares(im_mob)
        three.sort_submobjects(lambda p : np.dot(p, DOWN+RIGHT))
        three.scale_to_fit_height(6)
        three.next_to(ORIGIN, LEFT)
        three_rect = SurroundingRectangle(
            three, 
            color = BLUE,
            buff = SMALL_BUFF
        )

        numbers = VGroup()
        for square in three:
            rgb = square.fill_rgb
            num = DecimalNumber(
                square.fill_rgb[0],
                num_decimal_points = 1
            )
            num.set_stroke(width = 1)
            color = rgba_to_color(1 - (rgb + 0.2)/1.2)
            num.highlight(color)
            num.scale_to_fit_width(0.7*square.get_width())
            num.move_to(square)
            numbers.add(num)

        arrow = Arrow(LEFT, RIGHT, color = BLUE)
        arrow.next_to(three, RIGHT)

        choices = VGroup(*[TexMobject(str(n)) for n in range(10)])
        choices.arrange_submobjects(DOWN)
        choices.scale_to_fit_height(2*SPACE_HEIGHT - 1)
        choices.next_to(arrow, RIGHT)

        self.play(
            LaggedStart(DrawBorderThenFill, three),
            ShowCreation(three_rect)
        )
        self.play(Write(numbers))
        self.play(
            ShowCreation(arrow),
            LaggedStart(FadeIn, choices),
        )

        rect = SurroundingRectangle(choices[0], buff = SMALL_BUFF)
        q_mark = TexMobject("?")
        q_mark.next_to(rect, RIGHT)
        self.play(ShowCreation(rect))
        for n in 8, 1, 5, 3:
            self.play(
                rect.move_to, choices[n],
                MaintainPositionRelativeTo(q_mark, rect)
            )
            self.dither(1)
        choice = choices[3]
        choices.remove(choice)
        choice.add(rect)
        self.play(
            choice.scale, 1.5, 
            choice.next_to, arrow, RIGHT,
            FadeOut(choices),
            FadeOut(q_mark),
        )
        self.dither(2)

class LayOutPlan(TeacherStudentsScene, NetworkScene):
    def setup(self):
        TeacherStudentsScene.setup(self)
        NetworkScene.setup(self)
        self.remove(self.network_mob)

    def construct(self):
        self.show_words()
        self.show_network()
        self.show_math()
        self.ask_about_layers()
        self.show_learning()

    def show_words(self):
        words = VGroup(
            TextMobject("Machine", "learning").highlight(GREEN),
            TextMobject("Neural network").highlight(BLUE),
        )
        words.next_to(self.teacher.get_corner(UP+LEFT), UP)
        words[0].save_state()
        words[0].shift(DOWN)
        words[0].fade(1)

        self.play(
            words[0].restore,
            self.teacher.change, "raise_right_hand",
            self.get_student_changes("pondering", "erm", "sassy")
        )
        self.play(
            words[0].shift, MED_LARGE_BUFF*UP,
            FadeIn(words[1]),
        )
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = words
        )
        self.play(words.to_corner, UP+RIGHT)

        self.words = words

    def show_network(self):
        network_mob = self.network_mob
        network_mob.next_to(self.students, UP)

        self.play(
            ReplacementTransform(
                VGroup(self.words[1].copy()),
                network_mob.layers
            ),
            self.get_student_changes(
                *["confused"]*3,
                submobject_mode = "all_at_once"
            ),
            run_time = 1
        )
        self.play(ShowCreation(
            network_mob.edge_groups,
            submobject_mode = "lagged_start",
            run_time = 2,
            lag_factor = 8,
            rate_func = None,
        ))
        self.play(self.teacher.change, "plain")
        in_vect = np.random.random(self.network.sizes[0])
        self.feed_forward(in_vect)
        self.dither()

    def show_math(self):
        equation = TexMobject(
            "\\textbf{a}_{l+1}", "=",  
            "\\sigma(",
                "W_l", "\\textbf{a}_l", "+", "b_l",
            ")"
        )
        equation.highlight_by_tex_to_color_map({
            "\\textbf{a}" : GREEN,
        })
        equation.move_to(self.network_mob.get_corner(UP+RIGHT))
        equation.to_edge(UP)

        self.play(Write(equation, run_time = 2))
        self.dither()

    def ask_about_layers(self):
        self.student_says(
            "Why the layers?",
            student_index = 2,
            bubble_kwargs = {"direction" : LEFT}
        )
        self.dither()
        self.play(RemovePiCreatureBubble(self.students[2]))

    def show_learning(self):
        rect = SurroundingRectangle(self.words[0][1], color = YELLOW)
        self.network_mob.neuron_fill_color = YELLOW

        layer = self.network_mob.layers[-1]
        activation = np.zeros(len(layer))
        activation[1] = 1.0
        active_layer = self.network_mob.get_active_layer(
            -1, activation
        )

        self.play(ShowCreation(rect))
        self.play(Transform(layer, active_layer))
        for edge_group in reversed(self.network_mob.edge_groups):
            edge_group.generate_target()
            for edge in edge_group.target:
                edge.set_stroke(
                    YELLOW, 
                    width = 4*np.random.random()**2
                )
            self.play(MoveToTarget(edge_group))
        self.dither()

class PreviewMNistNetwork(NetworkScene):
    CONFIG = {
        "n_examples" : 15,
        "network_mob_config" : {},
    }
    def construct(self):
        self.remove_random_edges(0.7) #Remove?

        training_data, validation_data, test_data = load_data_wrapper()
        for data in test_data[:self.n_examples]:
            self.feed_in_image(data[0])

    def feed_in_image(self, in_vect):
        image = PixelsFromVect(in_vect)
        image.next_to(self.network_mob, LEFT, LARGE_BUFF, UP)
        big_rect = SurroundingRectangle(image, color = BLUE)
        start_neurons = self.network_mob.layers[0].neurons.copy()
        start_neurons.set_stroke(WHITE, width = 0)
        start_neurons.set_fill(WHITE, 0)

        self.play(FadeIn(image), FadeIn(big_rect))
        self.feed_forward(in_vect, added_anims = [
            self.get_image_to_layer_one_animation(image, start_neurons)
        ])
        n = np.argmax([
            neuron.get_fill_opacity()
            for neuron in self.network_mob.layers[-1].neurons
        ])
        rect = SurroundingRectangle(VGroup(
            self.network_mob.layers[-1].neurons[n],
            self.network_mob.output_labels[n],
        ))
        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))
        self.play(
            FadeOut(image),
            FadeOut(big_rect),
            self.network_mob.deactivate_layers,
        )

    def get_image_to_layer_one_animation(self, image, start_neurons):
        image_mover = VGroup(*[
            pixel.copy()
            for pixel in image
            if pixel.fill_rgb[0] > 0.1
        ])
        return Transform(
            image_mover, start_neurons, 
            remover = True,
            run_time = 1,
        )

    ###

    def add_network(self):
        self.network_mob = MNistNetworkMobject(**self.network_mob_config)
        self.network = self.network_mob.neural_network
        self.add(self.network_mob)

class AlternateNeuralNetworks(PiCreatureScene):
    def construct(self):
        morty = self.pi_creature
        examples = VGroup(
            VGroup(
                TextMobject("Convolutional neural network"),
                TextMobject("Good for image recognition"),
            ),
            VGroup(
                TextMobject("Long short-term memory network"),
                TextMobject("Good for speech recognition"),
            )
        )
        for ex in examples:
            arrow = Arrow(LEFT, RIGHT, color = BLUE)
            ex[0].next_to(arrow, LEFT)
            ex[1].next_to(arrow, RIGHT)
            ex.submobjects.insert(1, arrow)
        examples.scale_to_fit_width(2*SPACE_WIDTH - 1)
        examples.next_to(morty, UP).to_edge(RIGHT)

        maybe_words = TextMobject("Maybe future videos?")
        maybe_words.scale(0.8)
        maybe_words.next_to(morty, UP)
        maybe_words.to_edge(RIGHT)
        maybe_words.highlight(YELLOW)

        self.play(
            Write(examples[0], run_time = 2),
            morty.change, "raise_right_hand"
        )
        self.dither()
        self.play(
            examples[0].shift, MED_LARGE_BUFF*UP,
            FadeIn(examples[1], submobject_mode = "lagged_start"),
        )
        self.dither()
        self.play(
            examples.shift, UP,
            FadeIn(maybe_words),
            morty.change, "maybe"
        )
        self.dither(2)

class PlainVanillaWrapper(Scene):
    def construct(self):
        title = TextMobject("Plain vanilla")
        subtitle = TextMobject("(aka ``multilayer perceptron'')")
        title.scale(1.5)
        title.to_edge(UP)
        subtitle.next_to(title, DOWN)

        self.add(title)
        self.dither(2)
        self.play(Write(subtitle, run_time = 2))
        self.dither(2)

class NotPerfectAddOn(Scene):
    def construct(self):
        words = TextMobject("Not perfect!")
        words.scale(1.5)
        arrow = Arrow(UP+RIGHT, DOWN+LEFT, color = RED)
        words.highlight(RED)
        arrow.to_corner(DOWN+LEFT)
        words.next_to(arrow, UP+RIGHT)

        self.play(
            Write(words),
            ShowCreation(arrow),
            run_time = 1
        )
        self.dither(2)

class MoreAThanI(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "More \\\\ A than I",
            target_mode = "hesitant"
        )
        self.change_student_modes("sad", "erm", "tired")
        self.dither(2)

class BreakDownName(Scene):
    def construct(self):
        self.ask_questions()
        self.show_neuron()

    def ask_questions(self):
        name = TextMobject("Neural", "network")
        name.to_edge(UP)
        q1 = TextMobject(
            "What are \\\\ the ", "neuron", "s?",
            arg_separator = ""
        )
        q2 = TextMobject("How are \\\\ they connected?")
        q1.next_to(name[0].get_bottom(), DOWN, buff = LARGE_BUFF)
        q2.next_to(name[1].get_bottom(), DOWN+RIGHT, buff = LARGE_BUFF)
        a1 = Arrow(q1.get_top(), name[0].get_bottom())
        a2 = Arrow(q2.get_top(), name.get_corner(DOWN+RIGHT))
        VGroup(q1, a1).highlight(BLUE)
        VGroup(q2, a2).highlight(YELLOW)

        randy = Randolph().to_corner(DOWN+LEFT)
        brain = SVGMobject(file_name = "brain")
        brain.set_fill(LIGHT_GREY, opacity = 0)
        brain.replace(randy.eyes, dim_to_match = 1)

        self.add(name)
        self.play(randy.change, "pondering")
        self.play(
            brain.scale_to_fit_height, 2,
            brain.shift, 2*UP,
            brain.set_fill, None, 1,
            randy.look, UP
        )
        brain_outline = brain.copy()
        brain_outline.set_fill(opacity = 0)
        brain_outline.set_stroke(BLUE_B, 3)
        self.play(
            ShowPassingFlash(
                brain_outline, 
                time_width = 0.5,
                run_time = 2
            )
        )
        self.play(Blink(randy))
        self.dither()
        self.play(
            Write(q1, run_time = 1),
            ShowCreation(a1),
            name[0].highlight, q1.get_color(),
        )
        self.play(
            Write(q2, run_time = 1),
            ShowCreation(a2),
            name[1].highlight, q2.get_color()
        )
        self.dither(2)

        self.play(*map(FadeOut, [
            name, randy, brain, 
            q2, a1, a2,
            q1[0], q1[2]
        ]))

        self.neuron_word = q1[1]

    def show_neuron(self):
        neuron_word = TextMobject("Neuron")
        arrow = TexMobject("\\rightarrow")
        arrow.shift(LEFT)
        description = TextMobject("Thing that holds a number")
        neuron_word.highlight(BLUE)
        neuron_word.next_to(arrow, LEFT)
        neuron_word.shift(0.5*SMALL_BUFF*UP)
        description.next_to(arrow, RIGHT)

        neuron = Circle(radius = 0.35, color = BLUE)
        neuron.next_to(neuron_word, UP, MED_LARGE_BUFF)
        num = TexMobject("0.2")
        num.scale_to_fit_width(0.7*neuron.get_width())
        num.move_to(neuron)
        num.save_state()
        num.move_to(description.get_right())
        num.set_fill(opacity = 1)

        self.play(
            ReplacementTransform(self.neuron_word, neuron_word),
            ShowCreation(neuron)
        )
        self.play(
            ShowCreation(arrow),
            Write(description, run_time = 1)
        )
        self.dither()
        self.play(
            neuron.set_fill, None, 0.2,
            num.restore
        )
        self.dither()
        for value in 0.8, 0.4, 0.1, 0.5:
            mob = TexMobject(str(value))
            mob.replace(num)
            self.play(
                neuron.set_fill, None, value,
                Transform(num, mob)
            )
            self.dither()

class IntroduceEachLayer(PreviewMNistNetwork):
    CONFIG = {
        "network_mob_config" : {
            "neuron_stroke_color" : WHITE,
            "neuron_stroke_width" : 2,
            "neuron_fill_color" : WHITE,
            "average_shown_activation_of_large_layer" : False,
            "edge_propogation_color" : YELLOW,
            "edge_propogation_time" : 2,
        }
    }
    def construct(self):
        self.setup_network_mob()
        self.break_up_image_as_neurons()
        self.show_activation_of_one_neuron()
        self.transform_into_full_network()
        self.show_output_layer()
        self.show_hidden_layers()
        self.show_propogation()

    def setup_network_mob(self):
        self.remove(self.network_mob)

    def break_up_image_as_neurons(self):
        self.image_map = get_organized_images()
        image = self.image_map[9][0]
        image_mob = PixelsFromVect(image)
        image_mob.scale_to_fit_height(4)
        image_mob.next_to(ORIGIN, LEFT)
        rect = SurroundingRectangle(image_mob, color = BLUE)
        neurons = VGroup()
        for pixel in image_mob:
            pixel.set_fill(WHITE, opacity = pixel.fill_rgb[0])
            neuron = Circle(
                color = WHITE,
                stroke_width = 1,
                radius = pixel.get_width()/2
            )
            neuron.move_to(pixel)
            neuron.set_fill(WHITE, pixel.get_fill_opacity())
            neurons.add(neuron)
        neurons.scale_in_place(1.2)
        neurons.space_out_submobjects(1.3)
        neurons.to_edge(DOWN)

        braces = VGroup(*[Brace(neurons, vect) for vect in LEFT, UP])
        labels = VGroup(*[
            brace.get_tex("28", buff = SMALL_BUFF) 
            for brace in braces
        ])

        equation = TexMobject("28", "\\times", "28", "=", "784")
        equation.next_to(neurons, RIGHT, LARGE_BUFF, UP)

        self.corner_image = MNistMobject(image)
        self.corner_image.to_corner(UP+LEFT)

        self.add(image_mob, rect)
        self.dither()
        self.play(
            ReplacementTransform(image_mob, neurons),
            FadeOut(rect),
            FadeIn(braces),
            FadeIn(labels),
        )
        self.dither()
        self.play(
            ReplacementTransform(labels[0].copy(), equation[0]),
            Write(equation[1]),
            ReplacementTransform(labels[1].copy(), equation[2]),
            Write(equation[3]),
            Write(equation[4]),
        )
        self.dither()

        self.neurons = neurons
        self.braces = braces
        self.brace_labels = labels
        self.num_pixels_equation = equation
        self.image_vect = image

    def show_activation_of_one_neuron(self):
        neurons = self.neurons
        numbers = VGroup()
        example_neuron = None
        example_num = None
        for neuron in neurons:
            o = neuron.get_fill_opacity()
            num = DecimalNumber(o, num_decimal_points = 1)
            num.scale_to_fit_width(0.7*neuron.get_width())
            num.move_to(neuron)
            if o > 0.8:
                num.set_fill(BLACK)
            numbers.add(num)
            if o > 0.25 and o < 0.75 and example_neuron is None:
                example_neuron = neuron
                example_num = num
                example_neuron.save_state()
                example_num.save_state()
        example_neuron.generate_target()
        example_neuron.target.scale_to_fit_height(1.5)
        example_neuron.target.next_to(neurons, RIGHT)
        example_num.target = DecimalNumber(
            example_neuron.get_fill_opacity()
        )
        example_num.target.move_to(example_neuron.target)

        def change_activation(num):
            self.play(
                example_neuron.set_fill, None, num,
                ChangingDecimal(
                    example_num,
                    lambda a : example_neuron.get_fill_opacity(),
                ),
                UpdateFromFunc(
                    example_num,
                    lambda m : m.set_fill(
                        BLACK if example_neuron.get_fill_opacity() > 0.8 else WHITE
                    )
                )
            )

        self.play(LaggedStart(FadeIn, numbers))
        self.play(
            MoveToTarget(example_neuron),
            MoveToTarget(example_num)
        )
        self.dither()
        curr_opacity = example_neuron.get_fill_opacity()
        for num in 0.3, 0.01, 1.0, curr_opacity:
            change_activation(num)
            self.dither()

        rect = SurroundingRectangle(example_num, color = YELLOW)
        activation = TextMobject("``Activation''")
        activation.next_to(example_neuron, RIGHT)
        activation.highlight(rect.get_color())
        self.play(ShowCreation(rect))
        self.play(Write(activation, run_time = 1))
        self.dither()
        change_activation(1.0)
        self.dither()
        change_activation(0.2)
        self.dither()

        self.play(
            example_neuron.restore,
            example_num.restore,
            FadeOut(activation),
            FadeOut(rect),
        )
        self.play(FadeOut(numbers))

    def transform_into_full_network(self):
        network_mob = self.network_mob
        neurons = self.neurons
        layer = network_mob.layers[0]
        n = network_mob.max_shown_neurons/2

        self.play(
            FadeOut(self.braces),
            FadeOut(self.brace_labels),
            FadeOut(VGroup(*self.num_pixels_equation[:-1]))
        )
        self.play(
            ReplacementTransform(
                VGroup(*neurons[:n]), 
                VGroup(*layer.neurons[:n]),
            ),
            ReplacementTransform(
                VGroup(*neurons[n:-n]), 
                layer.dots,
            ),
            ReplacementTransform(
                VGroup(*neurons[-n:]), 
                VGroup(*layer.neurons[-n:]),
            ),
            FadeIn(self.corner_image)
        )
        self.play(
            ReplacementTransform(
                self.num_pixels_equation[-1],
                layer.brace_label
            ),
            FadeIn(layer.brace)
        )
        self.dither()
        for edge_group, layer in zip(network_mob.edge_groups, network_mob.layers[1:]):
            self.play(
                LaggedStart(FadeIn, layer, run_time = 1),
                ShowCreation(edge_group),
            )
        self.dither()

    def show_output_layer(self):
        layer = self.network_mob.layers[-1]
        labels = self.network_mob.output_labels
        rect = SurroundingRectangle(
            VGroup(layer, labels)
        )
        neuron = layer.neurons[-1]
        neuron.set_fill(WHITE, 0)
        label = labels[-1]
        for mob in neuron, label:
            mob.save_state()
            mob.generate_target()
        neuron.target.scale_in_place(4)
        neuron.target.shift(1.5*RIGHT)
        label.target.scale(1.5)
        label.target.next_to(neuron.target, RIGHT)

        activation = DecimalNumber(0)
        activation.move_to(neuron.target)

        def change_activation(num):
            self.play(
                neuron.set_fill, None, num,
                ChangingDecimal(
                    activation,
                    lambda a : neuron.get_fill_opacity(),
                ),
                UpdateFromFunc(
                    activation,
                    lambda m : m.set_fill(
                        BLACK if neuron.get_fill_opacity() > 0.8 else WHITE
                    )
                )
            )

        self.play(ShowCreation(rect))
        self.play(LaggedStart(FadeIn, labels))
        self.dither()
        self.play(
            MoveToTarget(neuron),
            MoveToTarget(label),
        )
        self.play(FadeIn(activation))
        for num in 0.5, 0.38, 0.97:
            change_activation(num)
            self.dither()
        self.play(
            neuron.restore,
            neuron.set_fill, None, 1,
            label.restore,
            FadeOut(activation),
            FadeOut(rect),
        )
        self.dither()

    def show_hidden_layers(self):
        hidden_layers = VGroup(*self.network_mob.layers[1:3])
        rect = SurroundingRectangle(hidden_layers, color = YELLOW)
        name = TextMobject("``Hidden layers''")
        name.next_to(rect, UP, SMALL_BUFF)
        name.highlight(YELLOW)
        q_marks = VGroup()
        for layer in hidden_layers:
            for neuron in layer.neurons:
                q_mark = TextMobject("?")
                q_mark.scale_to_fit_height(0.8*neuron.get_height())
                q_mark.move_to(neuron)
                q_marks.add(q_mark)
        q_marks.gradient_highlight(BLUE, YELLOW)
        q_mark = TextMobject("?").scale(4)
        q_mark.move_to(hidden_layers)
        q_mark.highlight(YELLOW)
        q_marks.add(q_mark)

        self.play(
            ShowCreation(rect),
            Write(name)
        )
        self.dither()
        self.play(Write(q_marks))
        self.dither()
        self.play(
            FadeOut(q_marks),
            Animation(q_marks[-1].copy())
        )

    def show_propogation(self):
        self.revert_to_original_skipping_status()
        self.remove_random_edges(0.7)
        self.feed_forward(self.image_vect)

class MoreHonestMNistNetworkPreview(IntroduceEachLayer):
    CONFIG = {
        "network_mob_config" : {
            "edge_propogation_time" : 1.5,
        }
    }
    def construct(self):
        PreviewMNistNetwork.construct(self)

    def get_image_to_layer_one_animation(self, image, start_neurons):
        neurons = VGroup()
        for pixel in image:
            neuron = Circle(
                radius = pixel.get_width()/2,
                stroke_width = 1,
                stroke_color = WHITE,
                fill_color = WHITE,
                fill_opacity = pixel.fill_rgb[0]
            )
            neuron.move_to(pixel)
            neurons.add(neuron)
        neurons.scale(1.2)
        neurons.next_to(image, DOWN)
        n = len(start_neurons)
        point = VectorizedPoint(start_neurons.get_center())
        target = VGroup(*it.chain(
            start_neurons[:n/2],
            [point.copy() for x in range(len(neurons)-n)],
            start_neurons[n/2:],
        ))
        mover = image.copy()
        self.play(Transform(mover, neurons))
        return Transform(
            mover, target, 
            run_time = 2,
            submobject_mode = "lagged_start",
            remover = True
        )

class AskAboutPropogationAndTraining(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "How does one layer \\\\ influence the next?",
            student_index = 0,
            run_time = 1
        )
        self.dither()
        self.student_says(
            "How does \\\\ training work?",
            student_index = 2,
            run_time = 1
        )
        self.dither(3)

class AskAboutLayers(PreviewMNistNetwork):
    def construct(self):
        self.play(
            self.network_mob.scale, 0.8,
            self.network_mob.to_edge, DOWN,
        )

        question = TextMobject("Why the", "layers?")
        question.to_edge(UP)
        neuron_groups = [
            layer.neurons
            for layer in self.network_mob.layers
        ]
        arrows = VGroup(*[
            Arrow(
                question[1].get_bottom(),
                group.get_top()
            )
            for group in neuron_groups
        ])
        rects = map(SurroundingRectangle, neuron_groups[1:3])

        self.play(
            Write(question, run_time = 1),
            LaggedStart(
                GrowFromPoint, arrows,
                lambda a : (a, a.get_start()),
                run_time = 2
            )
        )
        self.dither()
        self.play(*map(ShowCreation, rects))
        self.dither()

class BreakUpMacroPatterns(IntroduceEachLayer):
    CONFIG = {
        "camera_config" : {"background_alpha" : 255},
        "prefixes" : [
            "nine", "eight", "four",
            "upper_loop", "right_line",
            "lower_loop", "horizontal_line",
            "upper_left_line"
        ]
    }
    def construct(self):
        self.setup_network_mob()
        self.setup_needed_patterns()
        self.setup_added_patterns()
        self.show_nine()
        self.show_eight()
        self.show_four()
        self.show_second_to_last_layer()
        self.show_upper_loop_activation()
        self.show_what_learning_is_required()

    def setup_needed_patterns(self):
        prefixes = self.prefixes
        vects = [
            np.array(Image.open(
                get_full_image_path("handwritten_" + p),
            ))[:,:,0].flatten()/255.0
            for p in prefixes
        ]
        mobjects = map(MNistMobject, vects)
        for mob in mobjects:
            image = mob[1]
            self.make_transparent(image)
        for prefix, mob in zip(prefixes, mobjects):
            setattr(self, prefix, mob)

    def setup_added_patterns(self):
        image_map = get_organized_images()
        two, three, five = mobs = [
            MNistMobject(image_map[n][0])
            for n in 2, 3, 5
        ]
        self.added_patterns = VGroup()
        for mob in mobs:
            for i, j in it.product([0, 14], [0, 14]):
                pattern = mob.deepcopy()
                pa = pattern[1].pixel_array
                temp = np.array(pa[i:i+14,j:j+14,:], dtype = 'uint8')
                pa[:,:] = 0
                pa[i:i+14,j:j+14,:] = temp
                self.make_transparent(pattern[1])
                pattern[1].highlight(random_bright_color())
                self.added_patterns.add(pattern)
        self.image_map = image_map

    def show_nine(self):
        nine = self.nine
        upper_loop = self.upper_loop
        right_line = self.right_line
        equation = self.get_equation(nine, upper_loop, right_line)
        equation.to_edge(UP)
        equation.shift(LEFT)

        parts = [upper_loop[1], right_line[1]]
        for mob, color in zip(parts, [YELLOW, RED]):
            mob.highlight(color)
            mob.save_state()
            mob.move_to(nine)
        right_line[1].pixel_array[:14,:,3] = 0

        self.play(FadeIn(nine))
        self.dither()
        self.play(*map(FadeIn, parts))
        self.dither()
        self.play(
            Write(equation[1]),
            upper_loop[1].restore,
            FadeIn(upper_loop[0])
        )
        self.dither()
        self.play(
            Write(equation[3]),
            right_line[1].restore,
            FadeIn(right_line[0]),
        )
        self.dither()

        self.nine_equation = equation

    def show_eight(self):
        eight = self.eight
        upper_loop = self.upper_loop.deepcopy()
        lower_loop = self.lower_loop
        lower_loop[1].highlight(GREEN)

        equation = self.get_equation(eight, upper_loop, lower_loop)
        equation.next_to(self.nine_equation, DOWN)

        lower_loop[1].save_state()
        lower_loop[1].move_to(eight[1])

        self.play(
            FadeIn(eight),
            Write(equation[1]),
        )
        self.play(ReplacementTransform(
            self.upper_loop.copy(),
            upper_loop
        ))
        self.dither()
        self.play(FadeIn(lower_loop[1]))
        self.play(
            Write(equation[3]),
            lower_loop[1].restore,
            FadeIn(lower_loop[0]),
        )
        self.dither()

        self.eight_equation = equation

    def show_four(self):
        four = self.four
        upper_left_line = self.upper_left_line
        upper_left_line[1].highlight(BLUE)
        horizontal_line = self.horizontal_line
        horizontal_line[1].highlight(MAROON_B)
        right_line = self.right_line.deepcopy()
        equation = self.get_equation(four, right_line, upper_left_line, horizontal_line)
        equation.next_to(
            self.eight_equation, DOWN, aligned_edge = LEFT
        )

        self.play(
            FadeIn(four),
            Write(equation[1])
        )
        self.play(ReplacementTransform(
            self.right_line.copy(), right_line
        ))
        self.play(LaggedStart(
            FadeIn, VGroup(*equation[3:])
        ))
        self.dither(2)

        self.four_equation = equation

    def show_second_to_last_layer(self):
        everything = VGroup(*it.chain(
            self.nine_equation,
            self.eight_equation,
            self.four_equation,
        ))
        patterns = VGroup(
            self.upper_loop,
            self.lower_loop,
            self.right_line,
            self.upper_left_line,
            self.horizontal_line,
            *self.added_patterns[:11]
        )
        for pattern in patterns:
            pattern.add_to_back(
                pattern[1].copy().highlight(BLACK, alpha = 1)
            )
        everything.remove(*patterns)
        network_mob = self.network_mob
        layer = network_mob.layers[-2]
        patterns.generate_target()
        for pattern, neuron in zip(patterns.target, layer.neurons):
            pattern.scale_to_fit_height(neuron.get_height())
            pattern.next_to(neuron, RIGHT, SMALL_BUFF)
        for pattern in patterns[5:]:
            pattern.fade(1)

        self.play(*map(FadeOut, everything))
        self.play(
            FadeIn(
                network_mob,
                submobject_mode = "lagged_start",
                run_time = 3,
            ),
            MoveToTarget(patterns)
        )
        self.dither(2)

        self.patterns = patterns

    def show_upper_loop_activation(self):
        neuron = self.network_mob.layers[-2].neurons[0]
        words = TextMobject("Upper loop neuron...mabye...")
        words.scale(0.8)
        words.next_to(neuron, UP)
        words.shift(RIGHT)
        rect = SurroundingRectangle(VGroup(
            neuron, self.patterns[0]
        ))
        nine = self.nine
        upper_loop = self.upper_loop.copy()
        upper_loop.remove(upper_loop[0])
        upper_loop.replace(nine)
        nine.add(upper_loop)
        nine.to_corner(UP+LEFT)
        self.remove_random_edges(0.7)
        self.network.get_activation_of_all_layers = lambda v : [
            np.zeros(784),
            sigmoid(6*(np.random.random(16)-0.5)),
            np.array([1, 0, 1] + 13*[0]),
            np.array(9*[0] + [1])
        ]

        self.play(FadeIn(nine))
        self.add_foreground_mobject(self.patterns)
        self.play(
            ShowCreation(rect),
            Write(words)
        )
        self.feed_forward(np.random.random(784))
        self.dither(2)

    def show_what_learning_is_required(self):
        edge_group = self.network_mob.edge_groups[-1].copy()
        edge_group.set_stroke(YELLOW, 4)
        for x in range(3):
            self.play(LaggedStart(
                ShowCreationThenDestruction, edge_group,
                run_time = 3
            ))
            self.dither()

    ######

    def get_equation(self, *mobs):
        equation = VGroup(
            mobs[0], TexMobject("=").scale(2),
            *list(it.chain(*[
                [m, TexMobject("+").scale(2)]
                for m in mobs[1:-1]
            ])) + [mobs[-1]]
        )
        equation.arrange_submobjects(RIGHT)
        return equation

    def make_transparent(self, image_mob):
        alpha_vect = np.array(
            image_mob.pixel_array[:,:,0],
            dtype = 'uint8'
        )
        image_mob.highlight(WHITE)
        image_mob.pixel_array[:,:,3] = alpha_vect
        return image_mob

class HowWouldYouRecognizeSubcomponent(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "Okay, but recognizing loops \\\\",
            "is just as hard!",
            target_mode = "sassy"
        )
        self.play(
            self.teacher.change, "guilty"
        )
        self.dither()

class BreakUpMicroPatterns(BreakUpMacroPatterns):
    CONFIG = {
        "prefixes" : [
            "loop",
            "loop_edge1",
            "loop_edge2",
            "loop_edge3",
            "loop_edge4",
            "loop_edge5",
            "right_line"
        ]
    }
    def construct(self):
        self.setup_network_mob()
        self.setup_needed_patterns()
        self.break_down_loop()



























