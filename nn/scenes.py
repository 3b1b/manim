import sys
import os.path
import cv2

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
from topics.graph_scene import *
from scene import Scene
from scene.reconfigurable_scene import ReconfigurableScene
from scene.zoomed_scene import *
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

from nn.network import *

#force_skipping
#revert_to_original_skipping_status


DEFAULT_GAUSS_BLUR_CONFIG = {
    "ksize"  : (5, 5), 
    "sigmaX" : 10, 
    "sigmaY" : 10,
}

DEFAULT_CANNY_CONFIG = {
    "threshold1" : 100,
    "threshold2" : 200,
}


def get_edges(image_array):
    blurred = cv2.GaussianBlur(
        image_array, 
        **DEFAULT_GAUSS_BLUR_CONFIG
    )
    edges = cv2.Canny(
        blurred, 
        **DEFAULT_CANNY_CONFIG
    )
    return edges

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
                fill_color = self.neuron_fill_color,
                fill_opacity = 0,
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
        return [ShowCreationThenDestruction(
            edge_group_copy, 
            run_time = self.edge_propogation_time,
            submobject_mode = "lagged_start"
        )]

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
        "network_mob_config" : {},
    }
    def setup(self):
        self.add_network()

    def add_network(self):
        self.network = Network(sizes = self.layer_sizes)
        self.network_mob = NetworkMobject(
            self.network,
            **self.network_mob_config
        )
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

def make_transparent(image_mob):
    alpha_vect = np.array(
        image_mob.pixel_array[:,:,0],
        dtype = 'uint8'
    )
    image_mob.highlight(WHITE)
    image_mob.pixel_array[:,:,3] = alpha_vect
    return image_mob

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
            self.teacher.change, "plain",
            run_time = 1
        )
        self.play(ShowCreation(
            network_mob.edge_groups,
            submobject_mode = "lagged_start",
            run_time = 2,
            lag_factor = 8,
            rate_func = None,
        ))
        in_vect = np.random.random(self.network.sizes[0])
        self.feed_forward(in_vect)

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

        self.equation = equation

    def ask_about_layers(self):
        self.student_says(
            "Why the layers?",
            student_index = 2,
            bubble_kwargs = {"direction" : LEFT}
        )
        self.dither()
        self.play(RemovePiCreatureBubble(self.students[2]))

    def show_learning(self):
        word = self.words[0][1].copy()
        rect = SurroundingRectangle(word, color = YELLOW)
        self.network_mob.neuron_fill_color = YELLOW

        layer = self.network_mob.layers[-1]
        activation = np.zeros(len(layer.neurons))
        activation[1] = 1.0
        active_layer = self.network_mob.get_active_layer(
            -1, activation
        )
        word_group = VGroup(word, rect)
        word_group.generate_target()
        word_group.target.move_to(self.equation, LEFT)
        word_group.target[0].highlight(YELLOW)
        word_group.target[1].set_stroke(width = 0)

        self.play(ShowCreation(rect))
        self.play(
            Transform(layer, active_layer),
            FadeOut(self.equation),
            MoveToTarget(word_group),
        )
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
        image_rect = SurroundingRectangle(image, color = BLUE)
        start_neurons = self.network_mob.layers[0].neurons.copy()
        start_neurons.set_stroke(WHITE, width = 0)
        start_neurons.set_fill(WHITE, 0)

        self.play(FadeIn(image), FadeIn(image_rect))
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
        self.reset_display(rect, image, image_rect)

    def reset_display(self, answer_rect, image, image_rect):
        self.play(FadeOut(answer_rect))
        self.play(
            FadeOut(image),
            FadeOut(image_rect),
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
        return make_transparent(image_mob)
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
            "right_line",
            "right_line_edge1",
            "right_line_edge2",
            "right_line_edge3",
        ]
    }
    def construct(self):
        self.setup_network_mob()
        self.setup_needed_patterns()

        self.break_down_loop()
        self.break_down_long_line()

    def break_down_loop(self):
        loop = self.loop
        loop[0].highlight(WHITE)
        edges = Group(*[
            getattr(self, "loop_edge%d"%d)
            for d in range(1, 6)
        ])
        colors = color_gradient([BLUE, YELLOW, RED], 5)
        for edge, color in zip(edges, colors):
            for mob in edge:
                mob.highlight(color)
        loop.generate_target()
        edges.generate_target()
        for edge in edges:
            edge[0].set_stroke(width = 0)
            edge.save_state()
            edge[1].set_opacity(0)
        equation = self.get_equation(loop.target, *edges.target)
        equation.scale_to_fit_width(2*SPACE_WIDTH - 1)
        equation.to_edge(UP)
        symbols = VGroup(*equation[1::2])

        randy = Randolph()
        randy.to_corner(DOWN+LEFT)

        self.add(randy)
        self.play(
            FadeIn(loop),
            randy.change, "pondering", loop
        )
        self.play(Blink(randy))
        self.dither()
        self.play(LaggedStart(
            ApplyMethod, edges,
            lambda e : (e.restore,),
            run_time = 4
        ))
        self.dither()
        self.play(
            MoveToTarget(loop, run_time = 2),
            MoveToTarget(edges, run_time = 2),
            Write(symbols),
            randy.change, "happy", equation,
        )
        self.dither()

        self.loop_equation = equation
        self.randy = randy

    def break_down_long_line(self):
        randy = self.randy
        line = self.right_line
        line[0].highlight(WHITE)
        edges = Group(*[
            getattr(self, "right_line_edge%d"%d)
            for d in range(1, 4)
        ])
        colors = Color(MAROON_B).range_to(PURPLE, 3)
        for edge, color in zip(edges, colors):
            for mob in edge:
                mob.highlight(color)
        equation = self.get_equation(line, *edges)
        equation.scale_to_fit_height(self.loop_equation.get_height())
        equation.next_to(
            self.loop_equation, DOWN, MED_LARGE_BUFF, LEFT
        )
        image_map = get_organized_images()
        digits = VGroup(*[
            MNistMobject(image_map[n][1])
            for n in 1, 4, 7
        ])
        digits.arrange_submobjects(RIGHT)
        digits.next_to(randy, RIGHT)

        self.revert_to_original_skipping_status()
        self.play(
            FadeIn(line),
            randy.change, "hesitant", line
        )
        self.play(Blink(randy))
        self.play(LaggedStart(FadeIn, digits))
        self.dither()
        self.play(
            LaggedStart(FadeIn, Group(*equation[1:])),
            randy.change, "pondering", equation
        )
        self.dither(3)

class SecondLayerIsLittleEdgeLayer(IntroduceEachLayer):
    CONFIG = {
        "camera_config" : {
            "background_alpha" : 255,
        },
        "network_mob_config" : {
            "layer_to_layer_buff" : 2,
            "edge_propogation_color" : YELLOW,
        }
    }
    def construct(self):
        self.setup_network_mob()
        self.setup_activations_and_nines()

        self.describe_second_layer()
        self.show_propogation()
        self.ask_question()

    def setup_network_mob(self):
        self.network_mob.scale(0.7)
        self.network_mob.to_edge(DOWN)
        self.remove_random_edges(0.7)

    def setup_activations_and_nines(self):
        layers = self.network_mob.layers
        nine_im, loop_im, line_im = images = [
            Image.open(get_full_image_path("handwritten_%s"%s))
            for s in "nine", "upper_loop", "right_line"
        ]
        nine_array, loop_array, line_array = [
            np.array(im)[:,:,0]/255.0
            for im in images
        ]
        self.nine = MNistMobject(nine_array.flatten())
        self.nine.scale_to_fit_height(1.5)
        self.nine[0].highlight(WHITE)
        make_transparent(self.nine[1])
        self.nine.next_to(layers[0].neurons, UP)

        self.activations = self.network.get_activation_of_all_layers(
            nine_array.flatten()
        )
        self.activations[-2] = np.array([1, 0, 1] + 13*[0])


        self.edge_colored_nine = Group()
        nine_pa = self.nine[1].pixel_array
        n, k = 6, 4
        colors = color_gradient([BLUE, YELLOW, RED, MAROON_B, GREEN], 10)
        for i, j in it.product(range(n), range(k)):
            mob = ImageMobject(np.zeros((28, 28, 4), dtype = 'uint8'))
            mob.replace(self.nine[1])
            pa = mob.pixel_array
            color = colors[(k*i + j)%(len(colors))]
            rgb = (255*color_to_rgb(color)).astype('uint8')
            pa[:,:,:3] = rgb
            i0, i1 = 1+(28/n)*i, 1+(28/n)*(i+1)
            j0, j1 = (28/k)*j, (28/k)*(j+1)
            pa[i0:i1,j0:j1,3] = nine_pa[i0:i1,j0:j1,3]
            self.edge_colored_nine.add(mob)
        self.edge_colored_nine.next_to(layers[1], UP)

        loop, line = [
            ImageMobject(layer_to_image_array(array.flatten()))
            for array in loop_array, line_array
        ]
        for mob, color in (loop, YELLOW), (line, RED):
            make_transparent(mob)
            mob.highlight(color)
            mob.replace(self.nine[1])
        line.pixel_array[:14,:,:] = 0

        self.pattern_colored_nine = Group(loop, line)
        self.pattern_colored_nine.next_to(layers[2], UP)

        for mob in self.edge_colored_nine, self.pattern_colored_nine:
            mob.align_to(self.nine[1], UP)

    def describe_second_layer(self):
        layer = self.network_mob.layers[1]
        rect = SurroundingRectangle(layer)
        words = TextMobject("``Little edge'' layer?")
        words.next_to(rect, UP, MED_LARGE_BUFF)
        words.highlight(YELLOW)

        self.play(
            ShowCreation(rect),
            Write(words, run_time = 2)
        )
        self.dither()
        self.play(*map(FadeOut, [rect, words]))

    def show_propogation(self):
        nine = self.nine
        edge_colored_nine = self.edge_colored_nine
        pattern_colored_nine = self.pattern_colored_nine
        activations = self.activations
        network_mob = self.network_mob
        layers = network_mob.layers
        edge_groups = network_mob.edge_groups.copy()
        edge_groups.set_stroke(YELLOW, 4)

        v_nine = PixelsAsSquares(nine[1])
        neurons = VGroup()
        for pixel in v_nine:
            neuron = Circle(
                radius = pixel.get_width()/2,
                stroke_color = WHITE,
                stroke_width = 1,
                fill_color = WHITE,
                fill_opacity = pixel.get_fill_opacity(),
            )
            neuron.rotate(3*np.pi/4)
            neuron.move_to(pixel)
            neurons.add(neuron)
        neurons.scale_to_fit_height(2)
        neurons.space_out_submobjects(1.2)
        neurons.next_to(network_mob, LEFT)
        self.set_neurons_target(neurons, layers[0])

        pattern_colored_nine.save_state()
        pattern_colored_nine.move_to(edge_colored_nine)
        edge_colored_nine.save_state()
        edge_colored_nine.move_to(nine[1])
        for mob in edge_colored_nine, pattern_colored_nine:
            for submob in mob:
                submob.set_opacity(0)

        active_layers = [
            network_mob.get_active_layer(i, a)
            for i, a in enumerate(activations)
        ]

        def activate_layer(i):
            self.play(
                ShowCreationThenDestruction(
                    edge_groups[i-1],
                    run_time = 2,
                    submobject_mode = "lagged_start"
                ),
                FadeIn(active_layers[i])
            )


        self.play(FadeIn(nine))
        self.play(ReplacementTransform(v_nine, neurons))
        self.play(MoveToTarget(
            neurons,
            remover = True,
            submobject_mode = "lagged_start",
            run_time = 2
        ))

        activate_layer(1)
        self.play(edge_colored_nine.restore)
        self.separate_parts(edge_colored_nine)
        self.dither()

        activate_layer(2)
        self.play(pattern_colored_nine.restore)
        self.separate_parts(pattern_colored_nine)

        activate_layer(3)
        self.dither(2)

    def ask_question(self):
        question = TextMobject(
            "Does the network \\\\ actually do this?"
        )
        question.to_edge(LEFT)
        later = TextMobject("We'll get back \\\\ to this")
        later.to_corner(UP+LEFT)
        later.highlight(BLUE)
        arrow = Arrow(later.get_bottom(), question.get_top())
        arrow.highlight(BLUE)

        self.play(Write(question, run_time = 2))
        self.dither()
        self.play(
            FadeIn(later),
            GrowFromPoint(arrow, arrow.get_start())
        )
        self.dither()

    ###

    def set_neurons_target(self, neurons, layer):
        neurons.generate_target()
        n = len(layer.neurons)/2
        Transform(
            VGroup(*neurons.target[:n]),
            VGroup(*layer.neurons[:n]),
        ).update(1)
        Transform(
            VGroup(*neurons.target[-n:]),
            VGroup(*layer.neurons[-n:]),
        ).update(1)
        Transform(
            VGroup(*neurons.target[n:-n]),
            VectorizedPoint(layer.get_center())
        ).update(1)

    def separate_parts(self, image_group):
        vects = compass_directions(len(image_group), UP)
        image_group.generate_target()
        for im, vect in zip(image_group.target, vects):
            im.shift(MED_SMALL_BUFF*vect)
        self.play(MoveToTarget(
            image_group,
            rate_func = there_and_back,
            submobject_mode = "lagged_start",
            run_time = 2,
        ))

class EdgeDetection(Scene):
    CONFIG = {
        "camera_config" : {"background_alpha" : 255}
    }
    def construct(self):
        lion = ImageMobject("Lion")
        edges_array = get_edges(lion.pixel_array)
        edges = ImageMobject(edges_array)
        group = Group(lion, edges)
        group.scale_to_fit_height(4)
        group.arrange_submobjects(RIGHT)
        lion_copy = lion.copy()

        self.play(FadeIn(lion))
        self.play(lion_copy.move_to, edges)
        self.play(Transform(lion_copy, edges, run_time = 3))
        self.dither(2)

class ManyTasksBreakDownLikeThis(TeacherStudentsScene):
    def construct(self):
        audio = self.get_wave_form()
        audio_label = TextMobject("Raw audio")
        letters = TextMobject(" ".join("recognition"))
        syllables = TextMobject("$\\cdot$".join([
            "re", "cog", "ni", "tion"
        ]))
        word = TextMobject(
            "re", "cognition",
            arg_separator = ""
        )
        word[1].highlight(BLUE)
        arrows = VGroup()
        def get_arrow():
            arrow = Arrow(ORIGIN, RIGHT, color = BLUE)
            arrows.add(arrow)
            return arrow
        sequence = VGroup(
            audio, get_arrow(),
            letters, get_arrow(),
            syllables, get_arrow(),
            word
        )
        sequence.arrange_submobjects(RIGHT)
        sequence.scale_to_fit_width(2*SPACE_WIDTH - 1)
        sequence.to_edge(UP)

        audio_label.next_to(audio, DOWN)
        VGroup(audio, audio_label).highlight(YELLOW)
        audio.save_state()

        self.teacher_says(
            "Many", "recognition", "tasks\\\\",
            "break down like this"
        )
        self.change_student_modes(*["pondering"]*3)
        self.dither()
        content = self.teacher.bubble.content
        pre_word = content[1]
        content.remove(pre_word)
        audio.move_to(pre_word)
        self.play(
            self.teacher.bubble.content.fade, 1,
            ShowCreation(audio),
            pre_word.shift, MED_SMALL_BUFF, DOWN
        )
        self.dither(2)
        self.play(
            RemovePiCreatureBubble(self.teacher),
            audio.restore,
            FadeIn(audio_label),
            *[
                ReplacementTransform(
                    m1, m2
                )
                for m1, m2 in zip(pre_word, letters)
            ]
        )
        self.play(
            GrowFromPoint(arrows[0], arrows[0].get_start()),
        )
        self.dither()
        self.play(
            GrowFromPoint(arrows[1], arrows[1].get_start()),
            LaggedStart(FadeIn, syllables, run_time = 1)
        )
        self.dither()
        self.play(
            GrowFromPoint(arrows[2], arrows[2].get_start()),
            LaggedStart(FadeIn, word, run_time = 1)
        )
        self.dither()

    def get_wave_form(self):
        func = lambda x : abs(sum([
            (1./n)*np.sin((n+3)*x)
            for n in range(1, 5)
        ]))
        result = VGroup(*[
            Line(func(x)*DOWN, func(x)*UP)
            for x in np.arange(0, 4, 0.1)
        ])
        result.set_stroke(width = 2)
        result.arrange_submobjects(RIGHT, buff = MED_SMALL_BUFF)
        result.scale_to_fit_height(1)

        return result

class AskAboutWhatEdgesAreDoing(IntroduceEachLayer):
    CONFIG = {
        "network_mob_config" : {
            "layer_to_layer_buff" : 2,
        }
    }
    def construct(self):
        self.add_question()
        self.show_propogation()

    def add_question(self):
        self.network_mob.scale(0.8)
        self.network_mob.to_edge(DOWN)
        edge_groups = self.network_mob.edge_groups
        self.remove_random_edges(0.7)

        question = TextMobject(
            "What are these connections actually doing?"
        )
        question.to_edge(UP)
        question.shift(RIGHT)
        arrows = VGroup(*[
            Arrow(
                question.get_bottom(),
                edge_group.get_top()
            )
            for edge_group in edge_groups
        ])

        self.add(question, arrows)

    def show_propogation(self):
        in_vect = get_organized_images()[6][3]
        image = MNistMobject(in_vect)
        image.next_to(self.network_mob, LEFT, MED_SMALL_BUFF, UP)

        self.add(image)
        self.feed_forward(in_vect)
        self.dither()

class IntroduceWeights(IntroduceEachLayer):
    CONFIG = {
        "weights_color" : GREEN,
        "negative_weights_color" : RED,
    }
    def construct(self):
        self.zoom_in_on_one_neuron()
        self.show_desired_pixel_region()
        self.ask_about_parameters()
        self.show_weights()
        self.show_weighted_sum()
        self.organize_weights_as_grid()
        self.make_most_weights_0()
        self.add_negative_weights_around_the_edge()

    def zoom_in_on_one_neuron(self):
        self.network_mob.to_edge(LEFT)
        layers = self.network_mob.layers
        edge_groups = self.network_mob.edge_groups

        neuron = layers[1].neurons[7].deepcopy()

        self.play(
            FadeOut(edge_groups),
            FadeOut(VGroup(*layers[1:])),
            FadeOut(self.network_mob.output_labels),
            Animation(neuron),
            neuron.edges_in.set_stroke, None, 2,
            submobject_mode = "lagged_start",
            run_time = 2
        )

        self.neuron = neuron

    def show_desired_pixel_region(self):
        neuron = self.neuron
        d = 28

        pixels = PixelsAsSquares(ImageMobject(
            np.zeros((d, d, 4))
        ))
        pixels.set_stroke(width = 0.5)
        pixels.set_fill(WHITE, 0)
        pixels.scale_to_fit_height(4)
        pixels.next_to(neuron, RIGHT, LARGE_BUFF)
        rect = SurroundingRectangle(pixels, color = BLUE)

        pixels_to_detect = self.get_pixels_to_detect()

        self.play(
            FadeIn(rect),
            ShowCreation(
                pixels, 
                submobject_mode = "lagged_start",
                run_time = 2,
            )
        )
        self.play(
            pixels_to_detect.set_fill, WHITE, 1,
            submobject_mode = "lagged_start",
            run_time = 2
        )
        self.dither(2)

        self.pixels = pixels
        self.pixels_to_detect = pixels_to_detect
        self.pixels_group = VGroup(rect, pixels)

    def ask_about_parameters(self):
        pixels = self.pixels
        pixels_group = self.pixels_group
        neuron = self.neuron

        question = TextMobject("What", "parameters", "should exist?")
        parameter_word = question.get_part_by_tex("parameters")
        parameter_word.highlight(self.weights_color)
        question.move_to(neuron.edges_in.get_top(), LEFT)
        arrow = Arrow(
            parameter_word.get_bottom(),
            neuron.edges_in[0].get_center(),
            color = self.weights_color
        )

        p_labels = VGroup(*[
            TexMobject("p_%d\\!:"%(i+1)).highlight(self.weights_color)
            for i in range(8)
        ] + [TexMobject("\\vdots")])
        p_labels.arrange_submobjects(DOWN, aligned_edge = LEFT)
        p_labels.next_to(parameter_word, DOWN, LARGE_BUFF)
        p_labels[-1].shift(SMALL_BUFF*RIGHT)

        def get_alpha_func(i, start = 0):
            m = int(5*np.sin(2*np.pi*i/128.))
            return lambda a : start + (1-2*start)*np.sin(np.pi*a*m)**2

        decimals = VGroup()
        changing_decimals = []
        for i, p_label in enumerate(p_labels[:-1]):
            decimal = DecimalNumber(0)
            decimal.next_to(p_label, RIGHT, MED_SMALL_BUFF)
            decimals.add(decimal)
            changing_decimals.append(ChangingDecimal(
                decimal, get_alpha_func(i + 5)
            ))
        for i, pixel in enumerate(pixels):
            pixel.func = get_alpha_func(i, pixel.get_fill_opacity())
        pixel_updates = [
            UpdateFromAlphaFunc(
                pixel,
                lambda p, a : p.set_fill(opacity = p.func(a))
            )
            for pixel in pixels
        ]

        self.play(
            Write(question, run_time = 2),
            GrowFromPoint(arrow, arrow.get_start()),
            pixels_group.scale_to_fit_height, 3,
            pixels_group.to_edge, RIGHT,
            LaggedStart(FadeIn, p_labels),
            LaggedStart(FadeIn, decimals),
        )
        self.dither()
        self.play(
            *changing_decimals + pixel_updates,
            run_time = 5,
            rate_func = None
        )

        self.question = question
        self.weight_arrow = arrow
        self.p_labels = p_labels
        self.decimals = decimals

    def show_weights(self):
        p_labels = self.p_labels
        decimals = self.decimals
        arrow = self.weight_arrow
        question = self.question
        neuron = self.neuron
        edges = neuron.edges_in

        parameter_word = question.get_part_by_tex("parameters")
        question.remove(parameter_word)
        weights_word = TextMobject("Weights", "")[0]
        weights_word.highlight(self.weights_color)
        weights_word.move_to(parameter_word)

        w_labels = VGroup()
        for p_label in p_labels:
            w_label = TexMobject(
                p_label.get_tex_string().replace("p", "w")
            )
            w_label.highlight(self.weights_color)
            w_label.move_to(p_label)
            w_labels.add(w_label)

        edges.generate_target()
        random_numbers = 1.5*np.random.random(len(edges))-0.5
        self.make_edges_weighted(edges.target, random_numbers)
        def get_alpha_func(r):
            return lambda a : (4*r)*a

        self.play(
            FadeOut(question),
            ReplacementTransform(parameter_word, weights_word),
            ReplacementTransform(p_labels, w_labels)
        )
        self.play(
            MoveToTarget(edges),
            *[
                ChangingDecimal(
                    decimal,
                    get_alpha_func(r)
                )
                for decimal, r in zip(decimals, random_numbers)
            ]
        )
        self.play(LaggedStart(
            ApplyMethod, edges,
            lambda m : (m.rotate_in_place, np.pi/24),
            rate_func = wiggle,
            run_time = 2
        ))
        self.dither()

        self.w_labels = w_labels
        self.weights_word = weights_word
        self.random_numbers = random_numbers

    def show_weighted_sum(self):
        weights_word = self.weights_word
        weight_arrow = self.weight_arrow
        w_labels = VGroup(*[
            VGroup(*label[:-1]).copy()
            for label in self.w_labels
        ])
        layer = self.network_mob.layers[0]

        a_vect = np.random.random(16)
        active_layer = self.network_mob.get_active_layer(0, a_vect)

        a_labels = VGroup(*[
            TexMobject("a_%d"%d)
            for d in range(1, 5)
        ])

        weighted_sum = VGroup(*it.chain(*[
            [w, a, TexMobject("+")]
            for w, a in zip(w_labels, a_labels)
        ]))
        weighted_sum.add(
            TexMobject("\\cdots"),
            TexMobject("+"),
            TexMobject("w_n").highlight(self.weights_color),
            TexMobject("a_n")
        )
        weighted_sum.arrange_submobjects(RIGHT, buff = SMALL_BUFF)
        weighted_sum.to_edge(UP)

        self.play(Transform(layer, active_layer))
        self.play(
            FadeOut(weights_word),
            FadeOut(weight_arrow),
            *[
                ReplacementTransform(n.copy(), a)
                for n, a in zip(layer.neurons, a_labels)
            ] + [
                ReplacementTransform(n.copy(), weighted_sum[-4])
                for n in layer.neurons[4:-1]
            ] + [
                ReplacementTransform(
                    layer.neurons[-1].copy(), 
                    weighted_sum[-1]
                )
            ] + [
                Write(weighted_sum[i])
                for i in range(2, 12, 3) + [-4, -3]
            ],
            run_time = 1.5
        )
        self.dither()
        self.play(*[
            ReplacementTransform(w1.copy(), w2)
            for w1, w2 in zip(self.w_labels, w_labels)[:4]
        ]+[
            ReplacementTransform(w.copy(), weighted_sum[-4])
            for w in self.w_labels[4:-1]
        ]+[
            ReplacementTransform(
                self.w_labels[-1].copy(), weighted_sum[-2]
            )
        ], run_time = 2)
        self.dither(2)

        self.weighted_sum = weighted_sum

    def organize_weights_as_grid(self):
        pixels = self.pixels
        w_labels = self.w_labels
        decimals = self.decimals

        weights = 2*np.sqrt(np.random.random(784))-1
        weights[:8] = self.random_numbers[:8]
        weights[-8:] = self.random_numbers[-8:]

        weight_grid = PixelsFromVect(np.abs(weights))
        weight_grid.replace(pixels)
        weight_grid.next_to(pixels, LEFT)
        for weight, pixel in zip(weights, weight_grid):
            if weight >= 0:
                color = self.weights_color
            else:
                color = self.negative_weights_color
            pixel.set_fill(color, opacity = abs(weight))

        self.play(FadeOut(w_labels))
        self.play(
            FadeIn(
                VGroup(*weight_grid[len(decimals):]),
                submobject_mode = "lagged_start",
                run_time = 3
            ),
            *[
                ReplacementTransform(decimal, pixel)
                for decimal, pixel in zip(decimals, weight_grid)
            ]
        )
        self.dither()

        self.weight_grid = weight_grid

    def make_most_weights_0(self):
        weight_grid = self.weight_grid
        pixels = self.pixels
        pixels_group = self.pixels_group

        weight_grid.generate_target()
        for w, p in zip(weight_grid.target, pixels):
            if p.get_fill_opacity() > 0.1:
                w.set_fill(GREEN, 0.5)
            else:
                w.set_fill(BLACK, 0.5)
            w.set_stroke(WHITE, 0.5)

        digit = self.get_digit()
        digit.replace(pixels)

        self.play(MoveToTarget(
            weight_grid,
            run_time = 2,
            submobject_mode = "lagged_start"
        ))
        self.dither()
        self.play(Transform(
            pixels, digit,
            run_time = 2,
            submobject_mode = "lagged_start"
        ))
        self.dither()
        self.play(weight_grid.move_to, pixels)
        self.dither()
        self.play(
            ReplacementTransform(
                self.pixels_to_detect.copy(),
                self.weighted_sum,
                run_time = 3,
                submobject_mode = "lagged_start"
            ),
            Animation(weight_grid),
        )
        self.dither()

    def add_negative_weights_around_the_edge(self):
        weight_grid = self.weight_grid
        pixels = self.pixels

        self.play(weight_grid.next_to, pixels, LEFT)
        self.play(*[
            ApplyMethod(
                weight_grid[28*y + x].set_fill, 
                self.negative_weights_color,
                0.5
            )
            for y in 6, 10
            for x in range(14-4, 14+4)
        ])
        self.dither(2)
        self.play(weight_grid.move_to, pixels)
        self.dither(2)

    ####

    def get_digit(self):
        digit_vect = get_organized_images()[7][4]
        digit = PixelsFromVect(digit_vect)
        digit.set_stroke(width = 0.5)
        return digit

    def get_pixels_to_detect(self, pixels):
        d = int(np.sqrt(len(pixels)))
        return VGroup(*it.chain(*[
            pixels[d*n + d/2 - 4 : d*n + d/2 + 4]
            for n in range(7, 10)
        ]))

    def get_surrounding_pixels_for_edge(self, pixels):
        d = int(np.sqrt(len(pixels)))
        return VGroup(*it.chain(*[
            pixels[d*n + d/2 - 4 : d*n + d/2 + 4]
            for n in 6, 10
        ]))

    def make_edges_weighted(self, edges, weights):
        for edge, r in zip(edges, weights):
            if r > 0:
                color = self.weights_color 
            else:
                color = self.negative_weights_color
            edge.set_stroke(color, 6*abs(r))

class MotivateSquishing(Scene):
    def construct(self):
        self.add_weighted_sum()
        self.show_real_number_line()
        self.show_interval()
        self.squish_into_interval()

    def add_weighted_sum(self):
        weighted_sum = TexMobject(*it.chain(*[
            ["w_%d"%d, "a_%d"%d, "+"]
            for d in range(1, 5)
        ] + [
            ["\\cdots", "+", "w_n", "a_n"]
        ]))
        weighted_sum.highlight_by_tex("w_", GREEN)
        weighted_sum.to_edge(UP)
        self.add(weighted_sum)
        self.weighted_sum = weighted_sum

    def show_real_number_line(self):
        weighted_sum = self.weighted_sum
        number_line = NumberLine(unit_size = 1.5)
        number_line.add_numbers()
        number_line.shift(UP)
        arrow1, arrow2 = [
            Arrow(
                weighted_sum.get_bottom(),
                number_line.number_to_point(n),
            )
            for n in -3, 3
        ]

        self.play(Write(number_line))
        self.play(GrowFromPoint(arrow1, arrow1.get_start()))
        self.play(Transform(
            arrow1, arrow2,
            run_time = 5,
            rate_func = there_and_back
        ))
        self.play(FadeOut(arrow1))

        self.number_line = number_line

    def show_interval(self):
        lower_number_line = self.number_line.copy()
        lower_number_line.shift(2*DOWN)
        lower_number_line.highlight(LIGHT_GREY)
        lower_number_line.numbers.highlight(WHITE)
        interval = Line(
            lower_number_line.number_to_point(0),
            lower_number_line.number_to_point(1),
            color = YELLOW,
            stroke_width = 5
        )
        brace = Brace(interval, DOWN, buff = 0.7)
        words = TextMobject("Activations should be in this range")
        words.next_to(brace, DOWN, SMALL_BUFF)

        self.play(ReplacementTransform(
            self.number_line.copy(), lower_number_line
        ))
        self.play(
            GrowFromCenter(brace),
            GrowFromCenter(interval),
        )
        self.play(Write(words, run_time = 2))
        self.dither()

        self.lower_number_line = lower_number_line

    def squish_into_interval(self):
        line = self.number_line
        line.remove(*line.numbers)
        ghost_line = line.copy()
        ghost_line.fade(0.5)
        ghost_line.highlight(BLUE_E)
        self.add(ghost_line, line)
        lower_line = self.lower_number_line

        line.generate_target()
        u = line.unit_size
        line.target.apply_function(
            lambda p : np.array([u*sigmoid(p[0])]+list(p[1:]))
        )
        line.target.move_to(lower_line.number_to_point(0.5))

        arrow = Arrow(
            line.numbers.get_bottom(),
            line.target.get_top(),
            color = YELLOW
        )

        self.play(
            MoveToTarget(line),
            GrowFromPoint(arrow, arrow.get_start())
        )
        self.dither(2)

class IntroduceSigmoid(GraphScene):
    CONFIG = {
        "x_min" : -5,
        "x_max" : 5,
        "x_axis_width" : 12,
        "y_min" : -1,
        "y_max" : 2,
        "y_axis_label" : "",
        "graph_origin" : DOWN,
        "x_labeled_nums" : range(-4, 5),
        "y_labeled_nums" : range(-1, 3),
    }
    def construct(self):
        self.setup_axes()
        self.add_title()
        self.add_graph()
        self.show_part(-5, -2, RED)
        self.show_part(2, 5, GREEN)
        self.show_part(-2, 2, BLUE)

    def add_title(self):
        name = TextMobject("Sigmoid")
        name.next_to(ORIGIN, RIGHT, LARGE_BUFF)
        name.to_edge(UP)
        equation = TexMobject(
            "\\sigma(x) = \\frac{1}{1+e^{-x}}"
        )
        equation.next_to(name, DOWN)
        self.add(equation, name)

    def add_graph(self):
        graph = self.get_graph(
            lambda x : 1./(1+np.exp(-x)),
            color = YELLOW
        )

        self.play(ShowCreation(graph))
        self.dither()

    ###

    def show_part(self, x_min, x_max, color):
        line, graph_part = [
            self.get_graph(
                func,
                x_min = x_min, 
                x_max = x_max,
                color = color,
            ).set_stroke(width = 4)
            for func in lambda x : 0, sigmoid
        ]

        self.play(ShowCreation(line))
        self.dither()
        self.play(Transform(line, graph_part))
        self.dither()

class IncludeBias(IntroduceWeights):
    def construct(self):
        self.force_skipping()
        self.zoom_in_on_one_neuron()
        self.setup_start()
        self.revert_to_original_skipping_status()

        self.words_on_activation()
        self.comment_on_need_for_bias()
        self.add_bias()
        self.summarize_weights_and_biases()

    def setup_start(self):
        self.weighted_sum = self.get_weighted_sum()
        digit = self.get_digit()
        rect = SurroundingRectangle(digit)
        d_group = VGroup(digit, rect)
        d_group.scale_to_fit_height(3)
        d_group.to_edge(RIGHT)
        weight_grid = digit.copy()
        weight_grid.set_fill(BLACK, 0.5)
        self.get_pixels_to_detect(weight_grid).set_fill(
            GREEN, 0.5
        )
        self.get_surrounding_pixels_for_edge(weight_grid).set_fill(
            RED, 0.5
        )
        weight_grid.move_to(digit)

        edges = self.neuron.edges_in
        self.make_edges_weighted(
            edges, 1.5*np.random.random(len(edges)) - 0.5
        )

        Transform(
            self.network_mob.layers[0],
            self.network_mob.get_active_layer(0, np.random.random(16))
        ).update(1)

        self.add(self.weighted_sum, digit, weight_grid)
        self.add_sigmoid_label()
        self.digit = digit
        self.weight_grid = weight_grid

    def words_on_activation(self):
        neuron = self.neuron
        weighted_sum = self.weighted_sum

        activation_word = TextMobject("Activation")
        activation_word.next_to(neuron, RIGHT)
        arrow = Arrow(neuron, weighted_sum.get_bottom())
        arrow.highlight(WHITE)
        words = TextMobject("How positive is this?")
        words.next_to(self.weighted_sum, UP, SMALL_BUFF)

        self.play(
            FadeIn(activation_word),
            neuron.set_fill, WHITE, 0.8,
        )
        self.dither()
        self.play(
            GrowArrow(arrow),
            ReplacementTransform(activation_word, words),
        )
        self.dither(2)
        self.play(FadeOut(arrow))

        self.how_positive_words = words

    def comment_on_need_for_bias(self):
        neuron = self.neuron
        weight_grid = self.weight_grid
        colored_pixels = VGroup(
            self.get_pixels_to_detect(weight_grid),
            self.get_surrounding_pixels_for_edge(weight_grid),
        )

        words = TextMobject(
            "Only activate meaningfully \\\\ when",
            "weighted sum", "$> 10$"
        )
        words.highlight_by_tex("weighted", GREEN)
        words.next_to(neuron, RIGHT)

        self.play(Write(words, run_time = 2))
        self.play(LaggedStart(
            ApplyMethod, colored_pixels,
            lambda p : (p.shift, MED_LARGE_BUFF*UP),
            rate_func = there_and_back,
            run_time = 2
        ))
        self.dither()

        self.gt_ten = words[-1]

    def add_bias(self):
        bias = TexMobject("-10")
        wn, rp = self.weighted_sum[-2:]
        bias.next_to(wn, RIGHT, SMALL_BUFF)
        bias.shift(0.02*UP)
        rp.generate_target()
        rp.target.next_to(bias, RIGHT, SMALL_BUFF)

        rect = SurroundingRectangle(bias, buff = 0.5*SMALL_BUFF)
        name = TextMobject("``bias''")
        name.next_to(rect, DOWN)
        VGroup(rect, name).highlight(BLUE)

        self.play(
            ReplacementTransform(
                self.gt_ten.copy(), bias,
                run_time = 2
            ),
            MoveToTarget(rp),
        )
        self.dither(2)
        self.play(
            ShowCreation(rect),
            Write(name)
        )
        self.dither(2)

        self.bias_name = name

    def summarize_weights_and_biases(self):
        weight_grid = self.weight_grid
        bias_name = self.bias_name

        self.play(LaggedStart(
            ApplyMethod, weight_grid,
            lambda p : (p.set_fill, 
                random.choice([GREEN, GREEN, RED]),
                random.random()
            ),
            rate_func = there_and_back,
            lag_ratio = 0.4,
            run_time = 4
        ))
        self.dither()
        self.play(Indicate(bias_name))
        self.dither(2)

    ###

    def get_weighted_sum(self):
        args = ["\\sigma \\big("]
        for d in range(1, 4):
            args += ["w_%d"%d, "a_%d"%d, "+"]
        args += ["\\cdots", "+", "w_n", "a_n"]
        args += ["\\big)"]
        weighted_sum = TexMobject(*args)
        weighted_sum.highlight_by_tex("w_", GREEN)
        weighted_sum.highlight_by_tex("\\big", YELLOW)
        weighted_sum.to_edge(UP, LARGE_BUFF)
        weighted_sum.shift(RIGHT)

        return weighted_sum

    def add_sigmoid_label(self):
        name = TextMobject("Sigmoid")
        sigma = self.weighted_sum[0][0]
        name.next_to(sigma, UP)
        name.to_edge(UP, SMALL_BUFF)

        arrow = Arrow(
            name.get_bottom(), sigma.get_top(), 
            buff = SMALL_BUFF,
            use_rectangular_stem = False,
            max_tip_length_to_length_ratio = 0.3
        )

        self.add(name, arrow)
        self.sigmoid_name = name
        self.sigmoid_arrow = arrow

class ContinualEdgeUpdate(ContinualAnimation):
    def __init__(self, network_mob, **kwargs):
        n_cycles = 5
        edges = VGroup(*it.chain(*network_mob.edge_groups))
        self.move_to_targets = []
        for edge in edges:
            edge.colors = [
                random.choice([GREEN, GREEN, GREEN, RED])
                for x in range(n_cycles)
            ]
            edge.widths = [
                3*random.random()**7
                for x in range(n_cycles)
            ]
            edge.cycle_time = 1 + random.random()

            edge.generate_target()
            edge.target.set_stroke(edge.colors[0], edge.widths[0])
            self.move_to_targets.append(MoveToTarget(edge))
        self.edges = edges
        ContinualAnimation.__init__(self, edges, **kwargs)

    def update_mobject(self, dt):
        if self.internal_time < 1:
            alpha = smooth(self.internal_time)
            for move_to_target in self.move_to_targets:
                move_to_target.update(alpha)
            return
        for edge in self.edges:
            t = (self.internal_time-1)/edge.cycle_time
            alpha = ((self.internal_time-1)%edge.cycle_time)/edge.cycle_time
            low_n = int(t)%len(edge.colors)
            high_n = int(t+1)%len(edge.colors)
            color = interpolate_color(edge.colors[low_n], edge.colors[high_n], alpha)
            width = interpolate(edge.widths[low_n], edge.widths[high_n], alpha)
            edge.set_stroke(color, width)

class ShowRemainingNetwork(IntroduceWeights):
    def construct(self):
        self.force_skipping()
        self.zoom_in_on_one_neuron()
        self.revert_to_original_skipping_status()

        self.show_all_of_second_layer()
        self.count_in_biases()
        self.compute_layer_two_of_weights_and_biases_count()
        self.show_remaining_layers()
        self.show_final_number()
        self.tweak_weights()

    def show_all_of_second_layer(self):
        example_neuron = self.neuron
        layer = self.network_mob.layers[1]

        neurons = VGroup(*layer.neurons)
        neurons.remove(example_neuron)

        words = TextMobject("784", "weights", "per neuron")
        words.next_to(layer.neurons[0], RIGHT)
        words.to_edge(UP)

        self.play(FadeIn(words))
        last_edges = None
        for neuron in neurons[:7]:
            edges = neuron.edges_in
            added_anims = []
            if last_edges is not None:
                added_anims += [
                    last_edges.set_stroke, None, 1
                ]
            edges.set_stroke(width = 2)
            self.play(
                ShowCreation(edges, submobject_mode = "lagged_start"),
                FadeIn(neuron),
                *added_anims,
                run_time = 1.5
            )
            last_edges = edges
        self.play(
            LaggedStart(
                ShowCreation, VGroup(*[
                    n.edges_in for n in neurons[7:]
                ]),
                run_time = 3,
            ),
            LaggedStart(
                FadeIn, VGroup(*neurons[7:]),
                run_time = 3,
            ),
            VGroup(*last_edges[1:]).set_stroke, None, 1
        )
        self.dither()

        self.weights_words = words

    def count_in_biases(self):
        neurons = self.network_mob.layers[1].neurons
        words = TextMobject("One", "bias","for each")
        words.next_to(neurons, RIGHT, buff = 2)
        arrows = VGroup(*[
            Arrow(
                words.get_left(),
                neuron.get_center(),
                color = BLUE
            )
            for neuron in neurons
        ])

        self.play(
            FadeIn(words),
            LaggedStart(
                GrowArrow, arrows, 
                run_time = 3,
                lag_ratio = 0.3,
            )
        )
        self.dither()

        self.bias_words = words
        self.bias_arrows = arrows

    def compute_layer_two_of_weights_and_biases_count(self):
        ww1, ww2, ww3 = weights_words = self.weights_words
        bb1, bb2, bb3 = bias_words = self.bias_words
        bias_arrows = self.bias_arrows

        times_16 = TexMobject("\\times 16")
        times_16.next_to(ww1, RIGHT, SMALL_BUFF)
        ww2.generate_target()
        ww2.target.next_to(times_16, RIGHT)

        bias_count = TextMobject("16", "biases")
        bias_count.next_to(ww2.target, RIGHT, LARGE_BUFF)

        self.play(
            Write(times_16),
            MoveToTarget(ww2),
            FadeOut(ww3)
        )
        self.dither()
        self.play(
            ReplacementTransform(times_16.copy(), bias_count[0]),
            FadeOut(bb1),
            ReplacementTransform(bb2, bias_count[1]),
            FadeOut(bb3),
            LaggedStart(FadeOut, bias_arrows)
        )
        self.dither()

        self.weights_count = VGroup(ww1, times_16, ww2)
        self.bias_count = bias_count

    def show_remaining_layers(self):
        weights_count = self.weights_count
        bias_count = self.bias_count
        for count in weights_count, bias_count:
            count.generate_target()
            count.prefix = VGroup(*count.target[:-1])

        added_weights = TexMobject(
            "+16\\!\\times\\! 16 + 16 \\!\\times\\! 10"
        )
        added_weights.to_corner(UP+RIGHT)
        weights_count.prefix.next_to(added_weights, LEFT, SMALL_BUFF)
        weights_count.target[-1].next_to(
            VGroup(weights_count.prefix, added_weights),
            DOWN
        )

        added_biases = TexMobject("+ 16 + 10")
        group = VGroup(bias_count.prefix, added_biases)
        group.arrange_submobjects(RIGHT, SMALL_BUFF)
        group.next_to(weights_count.target[-1], DOWN, LARGE_BUFF)
        bias_count.target[-1].next_to(group, DOWN)

        network_mob = self.network_mob
        edges = VGroup(*it.chain(*network_mob.edge_groups[1:]))
        neurons = VGroup(*it.chain(*[
            layer.neurons for layer in network_mob.layers[2:]
        ]))

        self.play(
            MoveToTarget(weights_count),
            MoveToTarget(bias_count),
            Write(added_weights, run_time = 1),
            Write(added_biases, run_time = 1),
            LaggedStart(
                ShowCreation, edges,
                run_time = 4,
                lag_ratio = 0.3,
            ),
            LaggedStart(
                FadeIn, neurons,
                run_time = 4,
                lag_ratio = 0.3,
            )
        )
        self.dither(2)

        weights_count.add(added_weights)
        bias_count.add(added_biases)

    def show_final_number(self):
        group = VGroup(
            self.weights_count,
            self.bias_count,
        )
        group.generate_target()
        group.target.scale_in_place(0.8)
        rect = SurroundingRectangle(group.target, buff = MED_SMALL_BUFF)
        num_mob = TexMobject("13{,}002")
        num_mob.scale(1.5)
        num_mob.next_to(rect, DOWN)

        self.play(
            ShowCreation(rect),
            MoveToTarget(group),
        )
        self.play(Write(num_mob))
        self.dither()

        self.final_number = num_mob

    def tweak_weights(self):
        learning = TextMobject("Learning $\\rightarrow$")
        finding_words = TextMobject(
            "Finding the right \\\\ weights and biases"
        )
        group = VGroup(learning, finding_words)
        group.arrange_submobjects(RIGHT)
        group.scale(0.8)
        group.next_to(self.final_number, DOWN, MED_LARGE_BUFF)

        self.add(ContinualEdgeUpdate(self.network_mob))
        self.dither(5)
        self.play(Write(group))
        self.dither(10)

    ###

    def get_edge_weight_wandering_anim(self, edges):
        for edge in edges:
            edge.generate_target()
            edge.target.set_stroke(
                color = random.choice([GREEN, GREEN, GREEN, RED]),
                width = 3*random.random()**7
            )
        self.play(
            LaggedStart(
                MoveToTarget, edges,
                lag_ratio = 0.6,
                run_time = 2,
            ),
            *added_anims
        )

class ImagineSettingByHand(Scene):
    def construct(self):
        randy = Randolph()
        randy.scale(0.7)
        randy.to_corner(DOWN+LEFT)

        bubble = randy.get_bubble()
        network_mob = NetworkMobject(
            Network(sizes = [8, 6, 6, 4]),
            neuron_stroke_color = WHITE
        )
        network_mob.scale(0.7)
        network_mob.move_to(bubble.get_bubble_center())
        network_mob.shift(MED_SMALL_BUFF*RIGHT + SMALL_BUFF*(UP+RIGHT))

        self.add(randy, bubble, network_mob)
        self.add(ContinualEdgeUpdate(network_mob))
        self.play(randy.change, "pondering")
        self.dither()
        self.play(Blink(randy))
        self.dither()
        self.play(randy.change, "horrified", network_mob)
        self.play(Blink(randy))
        self.dither(10)

class WhenTheNetworkFails(MoreHonestMNistNetworkPreview):
    CONFIG = {
        "network_mob_config" : {"layer_to_layer_buff" : 2}
    }
    def construct(self):
        self.setup_network_mob()
        self.black_box()
        self.incorrect_classification()
        self.ask_about_weights()

    def setup_network_mob(self):
        self.network_mob.scale(0.8)
        self.network_mob.to_edge(DOWN)

    def black_box(self):
        network_mob = self.network_mob
        layers = VGroup(*network_mob.layers[1:3])
        box = SurroundingRectangle(
            layers,
            stroke_color = WHITE,
            fill_color = BLACK,
            fill_opacity = 0.8,
        )
        words = TextMobject("...rather than treating this as a black box")
        words.next_to(box, UP, LARGE_BUFF)

        self.play(
            Write(words, run_time = 2),
            DrawBorderThenFill(box)
        )
        self.dither()
        self.play(*map(FadeOut, [words, box]))

    def incorrect_classification(self):
        network = self.network
        training_data, validation_data, test_data = load_data_wrapper()
        for in_vect, result in test_data[20:]:
            network_answer = np.argmax(network.feedforward(in_vect))
            if network_answer != result:
                break
        self.feed_in_image(in_vect)

        wrong = TextMobject("Wrong!")
        wrong.highlight(RED)
        wrong.next_to(self.network_mob.layers[-1], UP+RIGHT)
        self.play(Write(wrong, run_time = 1))

    def ask_about_weights(self):
        question = TextMobject(
            "What weights are used here?\\\\",
            "What are they doing?"
        )
        question.next_to(self.network_mob, UP)

        self.add(ContinualEdgeUpdate(self.network_mob))
        self.play(Write(question))
        self.dither(10)


    ###

    def reset_display(self, *args):
        pass

class EvenWhenItWorks(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Even when it works,\\\\",
            "dig into why."
        )
        self.change_student_modes(*["pondering"]*3)
        self.dither(7)

class IntroduceWeightMatrix(NetworkScene):
    CONFIG = {
        "network_mob_config" : {
            "neuron_stroke_color" : WHITE,
            "neuron_fill_color" : WHITE,
            "neuron_radius" : 0.35,
            "layer_to_layer_buff" : 2,
        },
        "layer_sizes" : [8, 6],
    }
    def construct(self):
        self.setup_network_mob()
        self.show_weighted_sum()
        self.organize_activations_into_column()
        self.organize_weights_as_matrix()
        self.show_meaning_of_matrix_row()
        self.connect_weighted_sum_to_matrix_multiplication()
        self.add_bias_vector()
        self.apply_sigmoid()
        self.write_clean_final_expression()

    def setup_network_mob(self):
        self.network_mob.to_edge(LEFT, buff = LARGE_BUFF)
        self.network_mob.layers[1].neurons.shift(0.02*RIGHT)

    def show_weighted_sum(self):
        self.fade_many_neurons()
        self.activate_first_layer()
        self.show_first_neuron_weighted_sum()
        self.add_bias()
        self.add_sigmoid()
        self.dither()
    ##

    def fade_many_neurons(self):
        anims = []
        neurons = self.network_mob.layers[1].neurons
        for neuron in neurons[1:]:
            neuron.save_state()
            neuron.edges_in.save_state()
            anims += [
                neuron.fade, 0.8,
                neuron.set_fill, None, 0,
                neuron.edges_in.fade, 0.8,
            ]
        anims += [
            Animation(neurons[0]),
            Animation(neurons[0].edges_in),
        ]
        self.play(*anims)

    def activate_first_layer(self):
        layer = self.network_mob.layers[0]
        activations = 0.7*np.random.random(len(layer.neurons))
        active_layer = self.network_mob.get_active_layer(0, activations)
        a_labels = VGroup(*[
            TexMobject("a^{(0)}_%d"%d)
            for d in range(len(layer.neurons))
        ])
        for label, neuron in zip(a_labels, layer.neurons):
            label.scale(0.75)
            label.move_to(neuron)

        self.play(
            Transform(layer, active_layer),
            Write(a_labels, run_time = 2)
        )

        self.a_labels = a_labels

    def show_first_neuron_weighted_sum(self):
        neuron = self.network_mob.layers[1].neurons[0]
        a_labels = VGroup(*self.a_labels[:2]).copy()
        a_labels.generate_target()
        w_labels = VGroup(*[
            TexMobject("w_{0, %d}"%d)
            for d in range(len(a_labels))
        ])
        weighted_sum = VGroup()
        symbols = VGroup()
        for a_label, w_label in zip(a_labels.target, w_labels):
            a_label.scale(1./0.75)
            plus =  TexMobject("+")
            weighted_sum.add(w_label, a_label, plus)
            symbols.add(plus)
        weighted_sum.add(
            TexMobject("\\cdots"),
            TexMobject("+"),
            TexMobject("w_{0, n}"),
            TexMobject("a^{(0)}_n"),
        )

        weighted_sum.arrange_submobjects(RIGHT)
        a1_label = TexMobject("a^{(1)}_0")
        a1_label.next_to(neuron, RIGHT)
        equals = TexMobject("=").next_to(a1_label, RIGHT)
        weighted_sum.next_to(equals, RIGHT)

        symbols.add(*weighted_sum[-4:-2])
        w_labels.add(weighted_sum[-2])
        a_labels.add(self.a_labels[-1].copy())
        a_labels.target.add(weighted_sum[-1])
        a_labels.add(VGroup(*self.a_labels[2:-1]).copy())
        a_labels.target.add(VectorizedPoint(weighted_sum[-4].get_center()))

        VGroup(a1_label, equals, weighted_sum).scale(
            0.75, about_point = a1_label.get_left()
        )

        w_labels.highlight(GREEN)
        w_labels.shift(0.6*SMALL_BUFF*DOWN)
        a_labels.target.shift(0.5*SMALL_BUFF*UP)

        self.play(
            Write(a1_label), 
            Write(equals),
            neuron.set_fill, None, 0.3,
            run_time = 1
        )
        self.play(MoveToTarget(a_labels, run_time = 1.5))
        self.play(
            Write(w_labels),
            Write(symbols),
        )

        self.a1_label = a1_label
        self.a1_equals = equals
        self.w_labels = w_labels
        self.a_labels_in_sum = a_labels
        self.symbols = symbols
        self.weighted_sum = VGroup(w_labels, a_labels, symbols)

    def add_bias(self):
        weighted_sum = self.weighted_sum
        bias = TexMobject("+\\,", "b_0")
        bias.scale(0.75)
        bias.next_to(weighted_sum, RIGHT, SMALL_BUFF)
        bias.shift(0.5*SMALL_BUFF*DOWN)
        name = TextMobject("Bias")
        name.scale(0.75)
        name.next_to(bias, DOWN, MED_LARGE_BUFF)
        arrow = Arrow(name, bias, buff = SMALL_BUFF)
        VGroup(name, arrow, bias).highlight(BLUE)

        self.play(
            FadeIn(name),
            FadeIn(bias),
            GrowArrow(arrow),
        )

        self.weighted_sum.add(bias)

        self.bias = bias
        self.bias_name = VGroup(name, arrow)

    def add_sigmoid(self):
        weighted_sum = self.weighted_sum
        weighted_sum.generate_target()
        sigma, lp, rp = mob = TexMobject("\\sigma\\big(\\big)")
        # mob.scale(0.75)
        sigma.move_to(weighted_sum.get_left())
        sigma.shift(0.5*SMALL_BUFF*(DOWN+RIGHT))
        lp.next_to(sigma, RIGHT, SMALL_BUFF)
        weighted_sum.target.next_to(lp, RIGHT, SMALL_BUFF)
        rp.next_to(weighted_sum.target, RIGHT, SMALL_BUFF)

        name = TextMobject("Sigmoid")
        name.next_to(sigma, UP, MED_LARGE_BUFF)
        arrow = Arrow(name, sigma, buff = SMALL_BUFF)
        sigmoid_name = VGroup(name, arrow)
        VGroup(sigmoid_name, mob).highlight(YELLOW)

        self.play(
            FadeIn(mob),
            MoveToTarget(weighted_sum),
            MaintainPositionRelativeTo(self.bias_name, self.bias),
        )
        self.play(FadeIn(sigmoid_name))

        self.sigma = sigma
        self.sigma_parens = VGroup(lp, rp)
        self.sigmoid_name = sigmoid_name

    ##

    def organize_activations_into_column(self):
        a_labels = self.a_labels.copy()
        a_labels.generate_target()
        column = a_labels.target
        a_labels_in_sum = self.a_labels_in_sum

        dots = TexMobject("\\vdots")
        mid_as = VGroup(*column[2:-1])
        Transform(mid_as, dots).update(1)
        last_a = column[-1]
        new_last_a = TexMobject(
            last_a.get_tex_string().replace("7", "n")
        )
        new_last_a.replace(last_a)
        Transform(last_a, new_last_a).update(1)

        VGroup(
            *column[:2] + [mid_as] + [column[-1]]
        ).arrange_submobjects(DOWN)
        column.shift(DOWN + 3.5*RIGHT)

        pre_brackets = self.get_brackets(a_labels)
        post_bracketes = self.get_brackets(column)
        pre_brackets.set_fill(opacity = 0)

        self.play(LaggedStart(
            Indicate, self.a_labels,
            rate_func = there_and_back
        ))
        self.play(
            MoveToTarget(a_labels),
            Transform(pre_brackets, post_bracketes),
            run_time = 2
        )
        self.dither()
        self.play(*[
            LaggedStart(Indicate, mob, rate_func = there_and_back)
            for mob in a_labels, a_labels_in_sum
        ])
        self.dither()

        self.a_column = a_labels
        self.a_column_brackets = pre_brackets

    def organize_weights_as_matrix(self):
        a_column = self.a_column
        a_column_brackets = self.a_column_brackets
        w_brackets = a_column_brackets.copy()
        w_brackets.next_to(a_column_brackets, LEFT, SMALL_BUFF)
        lwb, rwb = w_brackets

        w_labels = self.w_labels.copy()
        w_labels.submobjects.insert(
            2, self.symbols[-2].copy()
        )
        w_labels.generate_target()
        w_labels.target.arrange_submobjects(RIGHT)
        w_labels.target.next_to(a_column[0], LEFT, buff = 0.8)
        lwb.next_to(w_labels.target, LEFT, SMALL_BUFF)
        lwb.align_to(rwb, UP)

        row_1, row_k = [
            VGroup(*map(TexMobject, [
                "w_{%s, 0}"%i,
                "w_{%s, 1}"%i,
                "\\cdots",
                "w_{%s, k}"%i,
            ]))
            for i in "1", "n"
        ]
        dots_row = VGroup(*map(TexMobject, [
            "\\vdots", "\\vdots", "\\ddots", "\\vdots"
        ]))

        lower_rows = VGroup(row_1, dots_row, row_k)
        lower_rows.scale(0.75)
        last_row = w_labels.target
        for row in lower_rows:
            for target, mover in zip(last_row, row):
                mover.move_to(target)
                if "w" in mover.get_tex_string():
                    mover.highlight(GREEN)
            row.next_to(last_row, DOWN, buff = 0.45)
            last_row = row

        self.play(
            MoveToTarget(w_labels),
            Write(w_brackets, run_time = 1)
        )
        self.play(FadeIn(
            lower_rows,
            run_time = 3,
            submobject_mode = "lagged_start",
        ))
        self.dither()

        self.top_matrix_row = w_labels
        self.lower_matrix_rows = lower_rows
        self.matrix_brackets = w_brackets

    def show_meaning_of_matrix_row(self):
        row = self.top_matrix_row
        edges = self.network_mob.layers[1].neurons[0].edges_in.copy()
        edges.set_stroke(GREEN, 5)
        rect = SurroundingRectangle(row, color = GREEN_B)

        self.play(ShowCreation(rect))
        for x in range(2):
            self.play(LaggedStart(
                ShowCreationThenDestruction, edges,
                lag_ratio = 0.8
            ))
        self.dither()

        self.top_row_rect = rect

    def connect_weighted_sum_to_matrix_multiplication(self):
        a_column = self.a_column
        a_brackets = self.a_column_brackets
        top_row_rect = self.top_row_rect

        column_rect = SurroundingRectangle(a_column)

        equals = TexMobject("=")
        equals.next_to(a_brackets, RIGHT)
        result_brackets = a_brackets.copy()
        result_terms = VGroup()
        for i in 0, 1, 4, -1:
            a = a_column[i]
            if i == 4:
                mob = TexMobject("\\vdots")
            else:
                # mob = Circle(radius = 0.2, color = YELLOW)
                mob = TexMobject("?").scale(1.3).highlight(YELLOW)
            result_terms.add(mob.move_to(a))
        VGroup(result_brackets, result_terms).next_to(equals, RIGHT)

        brace = Brace(
            VGroup(self.w_labels, self.a_labels_in_sum), DOWN
        )
        arrow = Arrow(
            brace.get_bottom(),
            result_terms[0].get_top(), 
            buff = SMALL_BUFF 
        )

        self.play(
            GrowArrow(arrow),
            GrowFromCenter(brace),
        )
        self.play(
            Write(equals),
            FadeIn(result_brackets),
        )
        self.play(ShowCreation(column_rect))
        self.play(ReplacementTransform(
            VGroup(top_row_rect, column_rect).copy(),
            result_terms[0]
        ))
        self.play(LaggedStart(
            FadeIn, VGroup(*result_terms[1:])
        ))
        self.dither(2)
        self.play(*map(FadeOut, [
            result_terms, result_brackets, equals,
            arrow, brace,
            top_row_rect, column_rect
        ]))

    def add_bias_vector(self):
        bias = self.bias
        bias_name = self.bias_name
        a_column_brackets = self.a_column_brackets
        a_column = self.a_column

        plus = TexMobject("+")
        b_brackets = a_column_brackets.copy()
        b_column = VGroup(*map(TexMobject, [
            "b_0", "b_1", "\\vdots", "b_n",
        ]))
        b_column.scale(0.85)
        b_column.arrange_submobjects(DOWN, buff = 0.35)
        b_column.move_to(a_column)
        b_column.highlight(BLUE)
        plus.next_to(a_column_brackets, RIGHT)
        VGroup(b_brackets, b_column).next_to(plus, RIGHT)

        bias_rect = SurroundingRectangle(bias)

        self.play(ShowCreation(bias_rect))
        self.play(FadeOut(bias_rect))
        self.play(
            Write(plus),
            Write(b_brackets),
            Transform(self.bias[1].copy(), b_column[0]),
            run_time = 1
        )
        self.play(LaggedStart(
            FadeIn, VGroup(*b_column[1:])
        ))
        self.dither()

        self.bias_plus = plus
        self.b_brackets = b_brackets
        self.b_column = b_column

    def apply_sigmoid(self):
        expression_bounds = VGroup(
            self.matrix_brackets[0], self.b_brackets[1]
        )
        sigma = self.sigma.copy()
        slp, srp = self.sigma_parens.copy()

        big_lp, big_rp = parens = TexMobject("()")
        parens.scale(3)
        parens.stretch_to_fit_height(expression_bounds.get_height())
        big_lp.next_to(expression_bounds, LEFT, SMALL_BUFF)
        big_rp.next_to(expression_bounds, RIGHT, SMALL_BUFF)
        parens.highlight(YELLOW)

        self.play(
            sigma.scale, 2,
            sigma.next_to, big_lp, LEFT, SMALL_BUFF,
            Transform(slp, big_lp),
            Transform(srp, big_rp),
        )
        self.dither(2)

        self.big_sigma_group = VGroup(VGroup(sigma), slp, srp)

    def write_clean_final_expression(self):
        self.fade_weighted_sum()
        expression = TexMobject(
            "\\textbf{a}^{(1)}", 
            "=",
            "\\sigma", 
            "\\big(", 
            "\\textbf{W}", 
            "\\textbf{a}^{(0)}",
            "+", 
            "\\textbf{b}", 
            "\\big)",
        )
        expression.highlight_by_tex_to_color_map({
            "sigma" : YELLOW,
            "big" : YELLOW,
            "W" : GREEN,
            "\\textbf{b}" : BLUE
        })
        expression.next_to(self.big_sigma_group, UP, LARGE_BUFF)
        a1, equals, sigma, lp, W, a0, plus, b, rp = expression

        neuron_anims = []
        neurons = VGroup(*self.network_mob.layers[1].neurons[1:])
        for neuron in neurons:
            neuron_anims += [
                neuron.restore,
                neuron.set_fill, None, random.random()
            ]
            neuron_anims += [
                neuron.edges_in.restore
            ]

        self.play(ReplacementTransform(
            VGroup(
                self.top_matrix_row, self.lower_matrix_rows,
                self.matrix_brackets
            ).copy(),
            VGroup(W), 
        ))
        self.play(ReplacementTransform(
            VGroup(self.a_column, self.a_column_brackets).copy(),
            VGroup(VGroup(a0)),
        ))
        self.play(
            ReplacementTransform(
                VGroup(self.b_column, self.b_brackets).copy(),
                VGroup(VGroup(b))
            ),
            ReplacementTransform(
                self.bias_plus.copy(), plus
            )
        )
        self.play(ReplacementTransform(
            self.big_sigma_group.copy(),
            VGroup(sigma, lp, rp)
        ))
        self.dither()
        self.play(*neuron_anims, run_time = 2)
        self.play(
            ReplacementTransform(neurons.copy(), a1),
            FadeIn(equals)
        )
        self.dither(2)

    def fade_weighted_sum(self):
        self.play(*map(FadeOut, [
            self.a1_label, self.a1_equals,
            self.sigma, self.sigma_parens, 
            self.weighted_sum,
            self.bias_name,
            self.sigmoid_name,
        ]))


    ###

    def get_brackets(self, mob):
        lb, rb = both = TexMobject("\\big[\\big]")
        both.scale_to_fit_width(mob.get_width())
        both.stretch_to_fit_height(1.2*mob.get_height())
        lb.next_to(mob, LEFT, SMALL_BUFF)
        rb.next_to(mob, RIGHT, SMALL_BUFF)
        return both



class EoLA3Wrapper(Scene):
    def construct(self):
        pass






























