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
        "neuron_fill_color" : GREEN,
        "edge_color" : LIGHT_GREY,
        "edge_stroke_width" : 2,
        "max_shown_neurons" : 16,
        "brace_for_large_layers" : True,
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
        if len(av) > n_neurons:
            av = av[av > 0][:n_neurons]
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
                self.neuron_fill_color,
                width = 1.5*self.edge_stroke_width
            )
            return map(ShowCreationThenDestruction, edge_group_copy)

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
            label.next_to(neuron, RIGHT, SMALL_BUFF)
            self.output_labels.add(label)
        self.add(self.output_labels)

class NetworkScene(Scene):
    CONFIG = {
        "layer_sizes" : [8, 6, 6, 4]
    }
    def setup(self):
        self.add_network()

    def add_network(self):
        self.network = Network(sizes = self.layer_sizes)
        self.network_mob = NetworkMobject(self.network)
        self.add(self.network_mob)

    def feed_forward(self, input_vector, false_confidence = False):
        activations = self.network.get_activation_of_all_layers(
            input_vector
        )
        if false_confidence:
            i = np.argmax(activations[-1])
            activations[-1] *= 0
            activations[-1][i] = 1.0
        for i, activation in enumerate(activations):
            self.show_activation_of_layer(i, activation)

    def show_activation_of_layer(self, layer_index, activation_vector):
        layer = self.network_mob.layers[layer_index]
        active_layer = self.network_mob.get_active_layer(
            layer_index, activation_vector
        )
        anims = [Transform(layer, active_layer)]
        if layer_index > 0:
            anims += self.network_mob.get_edge_propogation_animations(
                layer_index-1
            )
        self.play(*anims)

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
    def construct(self):
        training_data, validation_data, test_data = load_data_wrapper()
        for data in test_data[:1]:
            self.feed_in_image(data[0])

    def feed_in_image(self, in_vect):
        image = PixelsFromVect(in_vect)
        image.next_to(self.network_mob, LEFT, LARGE_BUFF, UP)
        rect = SurroundingRectangle(image, color = BLUE)

        self.play(FadeIn(image), FadeIn(rect))
        print in_vect.shape
        # self.feed_forward(in_vect)
        # self.play(FadeOut(image))





    ###

    def add_network(self):
        self.network_mob = MNistNetworkMobject()
        self.network = self.network_mob.neural_network
        self.add(self.network_mob)

















































