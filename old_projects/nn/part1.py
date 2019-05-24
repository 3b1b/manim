import sys
import os.path
import cv2

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from manimlib.imports import *

import warnings
warnings.warn("""
    Warning: This file makes use of
    ContinualAnimation, which has since
    been deprecated
""")


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
        self.arrange_in_grid(
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
        "edge_propogation_color" : YELLOW,
        "edge_propogation_time" : 1,
        "max_shown_neurons" : 16,
        "brace_for_large_layers" : True,
        "average_shown_activation_of_large_layer" : True,
        "include_output_labels" : False,
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
        layers.arrange(RIGHT, buff = self.layer_to_layer_buff)
        self.layers = layers
        self.add(self.layers)
        if self.include_output_labels:
            self.add_output_labels()

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
        neurons.arrange(
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
            VGroup(*neurons[:len(neurons) // 2]).next_to(
                dots, UP, MED_SMALL_BUFF
            )
            VGroup(*neurons[len(neurons) // 2:]).next_to(
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
                edge = self.get_edge(n1, n2)
                edge_group.add(edge)
                n1.edges_out.add(edge)
                n2.edges_in.add(edge)
            self.edge_groups.add(edge_group)
        self.add_to_back(self.edge_groups)

    def get_edge(self, neuron1, neuron2):
        return Line(
            neuron1.get_center(),
            neuron2.get_center(),
            buff = self.neuron_radius,
            stroke_color = self.edge_color,
            stroke_width = self.edge_stroke_width,
        )

    def get_active_layer(self, layer_index, activation_vector):
        layer = self.layers[layer_index].deepcopy()
        self.activate_layer(layer, activation_vector)
        return layer

    def activate_layer(self, layer, activation_vector):
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

    def activate_layers(self, input_vector):
        activations = self.neural_network.get_activation_of_all_layers(input_vector)
        for activation, layer in zip(activations, self.layers):
            self.activate_layer(layer, activation)

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
            lag_ratio = 0.5
        )]

    def add_output_labels(self):
        self.output_labels = VGroup()
        for n, neuron in enumerate(self.layers[-1].neurons):
            label = TexMobject(str(n))
            label.set_height(0.75*neuron.get_height())
            label.move_to(neuron)
            label.shift(neuron.get_width()*RIGHT)
            self.output_labels.add(label)
        self.add(self.output_labels)

class MNistNetworkMobject(NetworkMobject):
    CONFIG = {
        "neuron_to_neuron_buff" : SMALL_BUFF,
        "layer_to_layer_buff" : 1.5,
        "edge_stroke_width" : 1,
        "include_output_labels" : True,
    }

    def __init__(self, **kwargs):
        network = get_pretrained_network()
        NetworkMobject.__init__(self, network, **kwargs)

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
    image_mob.set_color(WHITE)
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
        three_mob_copy.sort(lambda p : np.dot(p, DOWN+RIGHT))

        braces = VGroup(*[Brace(three_mob, v) for v in (LEFT, UP)])
        brace_labels = VGroup(*[
            brace.get_text("28px")
            for brace in braces
        ])

        bubble = randy.get_bubble(height = 4, width = 6)
        three_mob.generate_target()
        three_mob.target.set_height(1)
        three_mob.target.next_to(bubble[-1].get_left(), RIGHT, LARGE_BUFF)
        arrow = Arrow(LEFT, RIGHT, color = BLUE)
        arrow.next_to(three_mob.target, RIGHT)
        real_three = TexMobject("3")
        real_three.set_height(0.8)
        real_three.next_to(arrow, RIGHT)

        self.play(
            FadeIn(three_mob[0]),
            LaggedStartMap(FadeIn, three_mob[1])
        )
        self.wait()
        self.play(
            LaggedStartMap(
                DrawBorderThenFill, three_mob_copy,
                run_time = 3,
                stroke_color = WHITE,
                remover = True,
            ),
            randy.change, "sassy",
            *it.chain(
                list(map(GrowFromCenter, braces)),
                list(map(FadeIn, brace_labels))
            )
        )
        self.wait()
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
        self.wait()

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
        alt_threes.arrange(DOWN)
        alt_threes.set_height(FRAME_HEIGHT - 2)
        alt_threes.to_edge(RIGHT)

        for alt_three in alt_threes:
            self.add(alt_three)
            self.wait(0.5)
        self.play(
            randy.change, "plain",
            *list(map(FadeOut, [
                self.bubble, self.arrow, self.real_three
            ])) + [MoveToTarget(three)]
        )
        for alt_three in alt_threes[:2]:
            self.play(three.replace, alt_three)
            self.wait()
        for moving_three in three, alt_threes[1]:
            moving_three.generate_target()
            moving_three.target.next_to(alt_threes, LEFT, LARGE_BUFF)
            moving_three.target[0].set_stroke(width = 0)
            moving_three.target[1].space_out_submobjects(1.5)
            self.play(MoveToTarget(
                moving_three, lag_ratio = 0.5
            ))
            self.play(
                Animation(randy),
                moving_three.replace, randy.eyes[1],
                moving_three.scale_in_place, 0.7,
                run_time = 2,
                lag_ratio = 0.5,
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
            three.target.set_height(1)
            three.target.next_to(equals, vect)

        self.play(
            randy.change, "thinking",
            ShowCreation(self.bubble),
            MoveToTarget(left_three),
            MoveToTarget(right_three),
            Write(equals),
        )
        self.wait()

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
        self.wait()
        for mob in alt_mobs[1:]:
            self.play(Transform(three, mob))
            self.wait()

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

class BrainAndHow(Scene):
    def construct(self):
        brain = SVGMobject(file_name = "brain")
        brain.set_height(2)
        brain.set_fill(LIGHT_GREY)
        brain_outline = brain.copy()
        brain_outline.set_fill(opacity = 0)
        brain_outline.set_stroke(BLUE_B, 3)

        how = TextMobject("How?!?")
        how.scale(2)
        how.next_to(brain, UP)

        self.add(brain)
        self.play(Write(how))
        for x in range(2):
            self.play(
                ShowPassingFlash(
                    brain_outline, 
                    time_width = 0.5,
                    run_time = 2
                )
            )
        self.wait()

class WriteAProgram(Scene):
    def construct(self):
        three_array = get_organized_images()[3][0]
        im_mob = ImageMobject(layer_to_image_array(three_array))
        three = PixelsAsSquares(im_mob)
        three.sort(lambda p : np.dot(p, DOWN+RIGHT))
        three.set_height(6)
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
                num_decimal_places = 1
            )
            num.set_stroke(width = 1)
            color = rgba_to_color(1 - (rgb + 0.2)/1.2)
            num.set_color(color)
            num.set_width(0.7*square.get_width())
            num.move_to(square)
            numbers.add(num)

        arrow = Arrow(LEFT, RIGHT, color = BLUE)
        arrow.next_to(three, RIGHT)

        choices = VGroup(*[TexMobject(str(n)) for n in range(10)])
        choices.arrange(DOWN)
        choices.set_height(FRAME_HEIGHT - 1)
        choices.next_to(arrow, RIGHT)

        self.play(
            LaggedStartMap(DrawBorderThenFill, three),
            ShowCreation(three_rect)
        )
        self.play(Write(numbers))
        self.play(
            ShowCreation(arrow),
            LaggedStartMap(FadeIn, choices),
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
            self.wait(1)
        choice = choices[3]
        choices.remove(choice)
        choice.add(rect)
        self.play(
            choice.scale, 1.5, 
            choice.next_to, arrow, RIGHT,
            FadeOut(choices),
            FadeOut(q_mark),
        )
        self.wait(2)

class LayOutPlan(TeacherStudentsScene, NetworkScene):
    def setup(self):
        TeacherStudentsScene.setup(self)
        NetworkScene.setup(self)
        self.remove(self.network_mob)

    def construct(self):
        self.force_skipping()

        self.show_words()
        self.show_network()
        self.show_math()
        self.ask_about_layers()
        self.show_learning()
        self.show_videos()

    def show_words(self):
        words = VGroup(
            TextMobject("Machine", "learning").set_color(GREEN),
            TextMobject("Neural network").set_color(BLUE),
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
                lag_ratio = 0
            ),
            self.teacher.change, "plain",
            run_time = 1
        )
        self.play(ShowCreation(
            network_mob.edge_groups,
            lag_ratio = 0.5,
            run_time = 2,
            rate_func=linear,
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
        equation.set_color_by_tex_to_color_map({
            "\\textbf{a}" : GREEN,
        })
        equation.move_to(self.network_mob.get_corner(UP+RIGHT))
        equation.to_edge(UP)

        self.play(Write(equation, run_time = 2))
        self.wait()

        self.equation = equation

    def ask_about_layers(self):
        self.student_says(
            "Why the layers?",
            student_index = 2,
            bubble_kwargs = {"direction" : LEFT}
        )
        self.wait()
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
        word_group.target[0].set_color(YELLOW)
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
        self.wait()

        self.learning_word = word

    def show_videos(self):
        network_mob = self.network_mob
        learning = self.learning_word
        structure = TextMobject("Structure")
        structure.set_color(YELLOW)
        videos = VGroup(*[
            VideoIcon().set_fill(RED)
            for x in range(2)
        ])
        videos.set_height(1.5)
        videos.arrange(RIGHT, buff = LARGE_BUFF)
        videos.next_to(self.students, UP, LARGE_BUFF)

        network_mob.generate_target()
        network_mob.target.set_height(0.8*videos[0].get_height())
        network_mob.target.move_to(videos[0])
        learning.generate_target()
        learning.target.next_to(videos[1], UP)
        structure.next_to(videos[0], UP)
        structure.shift(0.5*SMALL_BUFF*UP)

        self.revert_to_original_skipping_status()
        self.play(
            MoveToTarget(network_mob),
            MoveToTarget(learning)
        )
        self.play(
            DrawBorderThenFill(videos[0]),
            FadeIn(structure),
            self.get_student_changes(*["pondering"]*3)
        )
        self.wait()
        self.play(DrawBorderThenFill(videos[1]))
        self.wait()

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
        image.shift_onto_screen()
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
        examples.set_width(FRAME_WIDTH - 1)
        examples.next_to(morty, UP).to_edge(RIGHT)

        maybe_words = TextMobject("Maybe future videos?")
        maybe_words.scale(0.8)
        maybe_words.next_to(morty, UP)
        maybe_words.to_edge(RIGHT)
        maybe_words.set_color(YELLOW)

        self.play(
            Write(examples[0], run_time = 2),
            morty.change, "raise_right_hand"
        )
        self.wait()
        self.play(
            examples[0].shift, MED_LARGE_BUFF*UP,
            FadeIn(examples[1], lag_ratio = 0.5),
        )
        self.wait()
        self.play(
            examples.shift, UP,
            FadeIn(maybe_words),
            morty.change, "maybe"
        )
        self.wait(2)

class PlainVanillaWrapper(Scene):
    def construct(self):
        title = TextMobject("Plain vanilla")
        subtitle = TextMobject("(aka ``multilayer perceptron'')")
        title.scale(1.5)
        title.to_edge(UP)
        subtitle.next_to(title, DOWN)

        self.add(title)
        self.wait(2)
        self.play(Write(subtitle, run_time = 2))
        self.wait(2)

class NotPerfectAddOn(Scene):
    def construct(self):
        words = TextMobject("Not perfect!")
        words.scale(1.5)
        arrow = Arrow(UP+RIGHT, DOWN+LEFT, color = RED)
        words.set_color(RED)
        arrow.to_corner(DOWN+LEFT)
        words.next_to(arrow, UP+RIGHT)

        self.play(
            Write(words),
            ShowCreation(arrow),
            run_time = 1
        )
        self.wait(2)

class MoreAThanI(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "More \\\\ A than I",
            target_mode = "hesitant"
        )
        self.change_student_modes("sad", "erm", "tired")
        self.wait(2)

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
        VGroup(q1, a1).set_color(BLUE)
        VGroup(q2, a2).set_color(YELLOW)

        randy = Randolph().to_corner(DOWN+LEFT)
        brain = SVGMobject(file_name = "brain")
        brain.set_fill(LIGHT_GREY, opacity = 0)
        brain.replace(randy.eyes, dim_to_match = 1)

        self.add(name)
        self.play(randy.change, "pondering")
        self.play(
            brain.set_height, 2,
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
        self.wait()
        self.play(
            Write(q1, run_time = 1),
            ShowCreation(a1),
            name[0].set_color, q1.get_color(),
        )
        self.play(
            Write(q2, run_time = 1),
            ShowCreation(a2),
            name[1].set_color, q2.get_color()
        )
        self.wait(2)

        self.play(*list(map(FadeOut, [
            name, randy, brain, 
            q2, a1, a2,
            q1[0], q1[2]
        ])))

        self.neuron_word = q1[1]

    def show_neuron(self):
        neuron_word = TextMobject("Neuron")
        arrow = TexMobject("\\rightarrow")
        arrow.shift(LEFT)
        description = TextMobject("Thing that holds a number")
        neuron_word.set_color(BLUE)
        neuron_word.next_to(arrow, LEFT)
        neuron_word.shift(0.5*SMALL_BUFF*UP)
        description.next_to(arrow, RIGHT)

        neuron = Circle(radius = 0.35, color = BLUE)
        neuron.next_to(neuron_word, UP, MED_LARGE_BUFF)
        num = TexMobject("0.2")
        num.set_width(0.7*neuron.get_width())
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
        self.wait()
        self.play(
            neuron.set_fill, None, 0.2,
            num.restore
        )
        self.wait()
        for value in 0.8, 0.4, 0.1, 0.5:
            mob = TexMobject(str(value))
            mob.replace(num)
            self.play(
                neuron.set_fill, None, value,
                Transform(num, mob)
            )
            self.wait()

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
        image_mob.set_height(4)
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

        braces = VGroup(*[Brace(neurons, vect) for vect in (LEFT, UP)])
        labels = VGroup(*[
            brace.get_tex("28", buff = SMALL_BUFF) 
            for brace in braces
        ])

        equation = TexMobject("28", "\\times", "28", "=", "784")
        equation.next_to(neurons, RIGHT, LARGE_BUFF, UP)

        self.corner_image = MNistMobject(image)
        self.corner_image.to_corner(UP+LEFT)

        self.add(image_mob, rect)
        self.wait()
        self.play(
            ReplacementTransform(image_mob, neurons),
            FadeOut(rect),
            FadeIn(braces),
            FadeIn(labels),
        )
        self.wait()
        self.play(
            ReplacementTransform(labels[0].copy(), equation[0]),
            Write(equation[1]),
            ReplacementTransform(labels[1].copy(), equation[2]),
            Write(equation[3]),
            Write(equation[4]),
        )
        self.wait()

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
            num = DecimalNumber(o, num_decimal_places = 1)
            num.set_width(0.7*neuron.get_width())
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
        example_neuron.target.set_height(1.5)
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

        self.play(LaggedStartMap(FadeIn, numbers))
        self.play(
            MoveToTarget(example_neuron),
            MoveToTarget(example_num)
        )
        self.wait()
        curr_opacity = example_neuron.get_fill_opacity()
        for num in 0.3, 0.01, 1.0, curr_opacity:
            change_activation(num)
            self.wait()

        rect = SurroundingRectangle(example_num, color = YELLOW)
        activation = TextMobject("``Activation''")
        activation.next_to(example_neuron, RIGHT)
        activation.set_color(rect.get_color())
        self.play(ShowCreation(rect))
        self.play(Write(activation, run_time = 1))
        self.wait()
        change_activation(1.0)
        self.wait()
        change_activation(0.2)
        self.wait()

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
        layer.save_state()
        layer.rotate(np.pi/2)
        layer.center()
        layer.brace_label.rotate_in_place(-np.pi/2)
        n = network_mob.max_shown_neurons/2

        rows = VGroup(*[
            VGroup(*neurons[28*i:28*(i+1)])
            for i in range(28)
        ])

        self.play(
            FadeOut(self.braces),
            FadeOut(self.brace_labels),
            FadeOut(VGroup(*self.num_pixels_equation[:-1]))
        )

        self.play(rows.space_out_submobjects, 1.2)
        self.play(
            rows.arrange, RIGHT, buff = SMALL_BUFF,
            path_arc = np.pi/2,
            run_time = 2
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
        )
        self.play(
            ReplacementTransform(
                self.num_pixels_equation[-1],
                layer.brace_label
            ),
            FadeIn(layer.brace),
        )
        self.play(layer.restore, FadeIn(self.corner_image))
        self.wait()
        for edge_group, layer in zip(network_mob.edge_groups, network_mob.layers[1:]):
            self.play(
                LaggedStartMap(FadeIn, layer, run_time = 1),
                ShowCreation(edge_group),
            )
        self.wait()

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
        self.play(LaggedStartMap(FadeIn, labels))
        self.wait()
        self.play(
            MoveToTarget(neuron),
            MoveToTarget(label),
        )
        self.play(FadeIn(activation))
        for num in 0.5, 0.38, 0.97:
            change_activation(num)
            self.wait()
        self.play(
            neuron.restore,
            neuron.set_fill, None, 1,
            label.restore,
            FadeOut(activation),
            FadeOut(rect),
        )
        self.wait()

    def show_hidden_layers(self):
        hidden_layers = VGroup(*self.network_mob.layers[1:3])
        rect = SurroundingRectangle(hidden_layers, color = YELLOW)
        name = TextMobject("``Hidden layers''")
        name.next_to(rect, UP, SMALL_BUFF)
        name.set_color(YELLOW)
        q_marks = VGroup()
        for layer in hidden_layers:
            for neuron in layer.neurons:
                q_mark = TextMobject("?")
                q_mark.set_height(0.8*neuron.get_height())
                q_mark.move_to(neuron)
                q_marks.add(q_mark)
        q_marks.set_color_by_gradient(BLUE, YELLOW)
        q_mark = TextMobject("?").scale(4)
        q_mark.move_to(hidden_layers)
        q_mark.set_color(YELLOW)
        q_marks.add(q_mark)

        self.play(
            ShowCreation(rect),
            Write(name)
        )
        self.wait()
        self.play(Write(q_marks))
        self.wait()
        self.play(
            FadeOut(q_marks),
            Animation(q_marks[-1].copy())
        )

    def show_propogation(self):
        self.revert_to_original_skipping_status()
        self.remove_random_edges(0.7)
        self.feed_forward(self.image_vect)

class DiscussChoiceForHiddenLayers(TeacherStudentsScene):
    def construct(self):
        network_mob = MNistNetworkMobject(
            layer_to_layer_buff = 2.5,
            neuron_stroke_color = WHITE,
        )
        network_mob.set_height(4)
        network_mob.to_edge(UP, buff = LARGE_BUFF)
        layers = VGroup(*network_mob.layers[1:3])
        rects = VGroup(*list(map(SurroundingRectangle, layers)))
        self.add(network_mob)

        two_words = TextMobject("2 hidden layers")
        two_words.set_color(YELLOW)
        sixteen_words = TextMobject("16 neurons each")
        sixteen_words.set_color(MAROON_B)
        for words in two_words, sixteen_words:
            words.next_to(rects, UP)

        neurons_anim = LaggedStartMap(
            Indicate, 
            VGroup(*it.chain(*[layer.neurons for layer in layers])),
            rate_func = there_and_back,
            scale_factor = 2,
            color = MAROON_B,
        )

        self.play(
            ShowCreation(rects),
            Write(two_words, run_time = 1),
            self.teacher.change, "raise_right_hand",
        )
        self.wait()
        self.play(
            FadeOut(rects),
            ReplacementTransform(two_words, sixteen_words),
            neurons_anim
        )
        self.wait()
        self.play(self.teacher.change, "shruggie")
        self.change_student_modes("erm", "confused", "sassy")
        self.wait()
        self.student_says(
            "Why 2 \\\\ layers?",
            student_index = 1,
            bubble_kwargs = {"direction" : RIGHT},
            run_time = 1,
            target_mode = "raise_left_hand",
        )
        self.play(self.teacher.change, "happy")
        self.wait()
        self.student_says(
            "Why 16?",
            student_index = 0,
            run_time = 1,
        )
        self.play(neurons_anim, run_time = 3)
        self.play(
            self.teacher.change, "shruggie",
            RemovePiCreatureBubble(self.students[0]),
        )
        self.wait()

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
            lag_ratio = 0.5,
            remover = True
        )

class AskAboutPropogationAndTraining(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "How does one layer \\\\ influence the next?",
            student_index = 0,
            run_time = 1
        )
        self.wait()
        self.student_says(
            "How does \\\\ training work?",
            student_index = 2,
            run_time = 1
        )
        self.wait(3)

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
        rects = list(map(SurroundingRectangle, neuron_groups[1:3]))

        self.play(
            Write(question, run_time = 1),
            LaggedStartMap(
                GrowFromPoint, arrows,
                lambda a : (a, a.get_start()),
                run_time = 2
            )
        )
        self.wait()
        self.play(*list(map(ShowCreation, rects)))
        self.wait()

class BreakUpMacroPatterns(IntroduceEachLayer):
    CONFIG = {
        "camera_config" : {"background_opacity" : 1},
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
                get_full_raster_image_path("handwritten_" + p),
            ))[:,:,0].flatten()/255.0
            for p in prefixes
        ]
        mobjects = list(map(MNistMobject, vects))
        for mob in mobjects:
            image = mob[1]
            self.make_transparent(image)
        for prefix, mob in zip(prefixes, mobjects):
            setattr(self, prefix, mob)

    def setup_added_patterns(self):
        image_map = get_organized_images()
        two, three, five = mobs = [
            MNistMobject(image_map[n][0])
            for n in (2, 3, 5)
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
                pattern[1].set_color(random_bright_color())
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
            mob.set_color(color)
            mob.save_state()
            mob.move_to(nine)
        right_line[1].pixel_array[:14,:,3] = 0

        self.play(FadeIn(nine))
        self.wait()
        self.play(*list(map(FadeIn, parts)))
        self.wait()
        self.play(
            Write(equation[1]),
            upper_loop[1].restore,
            FadeIn(upper_loop[0])
        )
        self.wait()
        self.play(
            Write(equation[3]),
            right_line[1].restore,
            FadeIn(right_line[0]),
        )
        self.wait()

        self.nine_equation = equation

    def show_eight(self):
        eight = self.eight
        upper_loop = self.upper_loop.deepcopy()
        lower_loop = self.lower_loop
        lower_loop[1].set_color(GREEN)

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
        self.wait()
        self.play(FadeIn(lower_loop[1]))
        self.play(
            Write(equation[3]),
            lower_loop[1].restore,
            FadeIn(lower_loop[0]),
        )
        self.wait()

        self.eight_equation = equation

    def show_four(self):
        four = self.four
        upper_left_line = self.upper_left_line
        upper_left_line[1].set_color(BLUE)
        horizontal_line = self.horizontal_line
        horizontal_line[1].set_color(MAROON_B)
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
        self.play(LaggedStartMap(
            FadeIn, VGroup(*equation[3:])
        ))
        self.wait(2)

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
                pattern[1].copy().set_color(BLACK, alpha = 1)
            )
        everything.remove(*patterns)
        network_mob = self.network_mob
        layer = network_mob.layers[-2]
        patterns.generate_target()
        for pattern, neuron in zip(patterns.target, layer.neurons):
            pattern.set_height(neuron.get_height())
            pattern.next_to(neuron, RIGHT, SMALL_BUFF)
        for pattern in patterns[5:]:
            pattern.fade(1)

        self.play(*list(map(FadeOut, everything)))
        self.play(
            FadeIn(
                network_mob,
                lag_ratio = 0.5,
                run_time = 3,
            ),
            MoveToTarget(patterns)
        )
        self.wait(2)

        self.patterns = patterns

    def show_upper_loop_activation(self):
        neuron = self.network_mob.layers[-2].neurons[0]
        words = TextMobject("Upper loop neuron...maybe...")
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
        self.play(
            ShowCreation(rect),
            Write(words)
        )
        self.add_foreground_mobject(self.patterns)
        self.feed_forward(np.random.random(784))
        self.wait(2)

    def show_what_learning_is_required(self):
        edge_group = self.network_mob.edge_groups[-1].copy()
        edge_group.set_stroke(YELLOW, 4)
        for x in range(3):
            self.play(LaggedStartMap(
                ShowCreationThenDestruction, edge_group,
                run_time = 3
            ))
            self.wait()

    ######

    def get_equation(self, *mobs):
        equation = VGroup(
            mobs[0], TexMobject("=").scale(2),
            *list(it.chain(*[
                [m, TexMobject("+").scale(2)]
                for m in mobs[1:-1]
            ])) + [mobs[-1]]
        )
        equation.arrange(RIGHT)
        return equation

    def make_transparent(self, image_mob):
        return make_transparent(image_mob)
        alpha_vect = np.array(
            image_mob.pixel_array[:,:,0],
            dtype = 'uint8'
        )
        image_mob.set_color(WHITE)
        image_mob.pixel_array[:,:,3] = alpha_vect
        return image_mob

class GenerallyLoopyPattern(Scene):
    def construct(self):
        image_map = get_organized_images()
        images = list(map(MNistMobject, it.chain(
            image_map[8], image_map[9],
        )))
        random.shuffle(images)

        for image in images:
            image.to_corner(DOWN+RIGHT)
            self.add(image)
            self.wait(0.2)
            self.remove(image)

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
        self.wait()

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
        loop[0].set_color(WHITE)
        edges = Group(*[
            getattr(self, "loop_edge%d"%d)
            for d in range(1, 6)
        ])
        colors = color_gradient([BLUE, YELLOW, RED], 5)
        for edge, color in zip(edges, colors):
            for mob in edge:
                mob.set_color(color)
        loop.generate_target()
        edges.generate_target()
        for edge in edges:
            edge[0].set_stroke(width = 0)
            edge.save_state()
            edge[1].set_opacity(0)
        equation = self.get_equation(loop.target, *edges.target)
        equation.set_width(FRAME_WIDTH - 1)
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
        self.wait()
        self.play(LaggedStartMap(
            ApplyMethod, edges,
            lambda e : (e.restore,),
            run_time = 4
        ))
        self.wait()
        self.play(
            MoveToTarget(loop, run_time = 2),
            MoveToTarget(edges, run_time = 2),
            Write(symbols),
            randy.change, "happy", equation,
        )
        self.wait()

        self.loop_equation = equation
        self.randy = randy

    def break_down_long_line(self):
        randy = self.randy
        line = self.right_line
        line[0].set_color(WHITE)
        edges = Group(*[
            getattr(self, "right_line_edge%d"%d)
            for d in range(1, 4)
        ])
        colors = Color(MAROON_B).range_to(PURPLE, 3)
        for edge, color in zip(edges, colors):
            for mob in edge:
                mob.set_color(color)
        equation = self.get_equation(line, *edges)
        equation.set_height(self.loop_equation.get_height())
        equation.next_to(
            self.loop_equation, DOWN, MED_LARGE_BUFF, LEFT
        )
        image_map = get_organized_images()
        digits = VGroup(*[
            MNistMobject(image_map[n][1])
            for n in (1, 4, 7)
        ])
        digits.arrange(RIGHT)
        digits.next_to(randy, RIGHT)

        self.revert_to_original_skipping_status()
        self.play(
            FadeIn(line),
            randy.change, "hesitant", line
        )
        self.play(Blink(randy))
        self.play(LaggedStartMap(FadeIn, digits))
        self.wait()
        self.play(
            LaggedStartMap(FadeIn, Group(*equation[1:])),
            randy.change, "pondering", equation
        )
        self.wait(3)

class SecondLayerIsLittleEdgeLayer(IntroduceEachLayer):
    CONFIG = {
        "camera_config" : {
            "background_opacity" : 1,
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
            Image.open(get_full_raster_image_path("handwritten_%s"%s))
            for s in ("nine", "upper_loop", "right_line")
        ]
        nine_array, loop_array, line_array = [
            np.array(im)[:,:,0]/255.0
            for im in images
        ]
        self.nine = MNistMobject(nine_array.flatten())
        self.nine.set_height(1.5)
        self.nine[0].set_color(WHITE)
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
        for i, j in it.product(list(range(n)), list(range(k))):
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
            for array in (loop_array, line_array)
        ]
        for mob, color in (loop, YELLOW), (line, RED):
            make_transparent(mob)
            mob.set_color(color)
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
        words.set_color(YELLOW)

        self.play(
            ShowCreation(rect),
            Write(words, run_time = 2)
        )
        self.wait()
        self.play(*list(map(FadeOut, [rect, words])))

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
        neurons.set_height(2)
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
                    lag_ratio = 0.5
                ),
                FadeIn(active_layers[i])
            )


        self.play(FadeIn(nine))
        self.play(ReplacementTransform(v_nine, neurons))
        self.play(MoveToTarget(
            neurons,
            remover = True,
            lag_ratio = 0.5,
            run_time = 2
        ))

        activate_layer(1)
        self.play(edge_colored_nine.restore)
        self.separate_parts(edge_colored_nine)
        self.wait()

        activate_layer(2)
        self.play(pattern_colored_nine.restore)
        self.separate_parts(pattern_colored_nine)

        activate_layer(3)
        self.wait(2)

    def ask_question(self):
        question = TextMobject(
            "Does the network \\\\ actually do this?"
        )
        question.to_edge(LEFT)
        later = TextMobject("We'll get back \\\\ to this")
        later.to_corner(UP+LEFT)
        later.set_color(BLUE)
        arrow = Arrow(later.get_bottom(), question.get_top())
        arrow.set_color(BLUE)

        self.play(Write(question, run_time = 2))
        self.wait()
        self.play(
            FadeIn(later),
            GrowFromPoint(arrow, arrow.get_start())
        )
        self.wait()

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
            lag_ratio = 0.5,
            run_time = 2,
        ))

class EdgeDetection(Scene):
    CONFIG = {
        "camera_config" : {"background_opacity" : 1}
    }
    def construct(self):
        lion = ImageMobject("Lion")
        edges_array = get_edges(lion.pixel_array)
        edges = ImageMobject(edges_array)
        group = Group(lion, edges)
        group.set_height(4)
        group.arrange(RIGHT)
        lion_copy = lion.copy()

        self.play(FadeIn(lion))
        self.play(lion_copy.move_to, edges)
        self.play(Transform(lion_copy, edges, run_time = 3))
        self.wait(2)

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
        word[1].set_color(BLUE)
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
        sequence.arrange(RIGHT)
        sequence.set_width(FRAME_WIDTH - 1)
        sequence.to_edge(UP)

        audio_label.next_to(audio, DOWN)
        VGroup(audio, audio_label).set_color(YELLOW)
        audio.save_state()

        self.teacher_says(
            "Many", "recognition", "tasks\\\\",
            "break down like this"
        )
        self.change_student_modes(*["pondering"]*3)
        self.wait()
        content = self.teacher.bubble.content
        pre_word = content[1]
        content.remove(pre_word)
        audio.move_to(pre_word)
        self.play(
            self.teacher.bubble.content.fade, 1,
            ShowCreation(audio),
            pre_word.shift, MED_SMALL_BUFF, DOWN
        )
        self.wait(2)
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
        self.wait()
        self.play(
            GrowFromPoint(arrows[1], arrows[1].get_start()),
            LaggedStartMap(FadeIn, syllables, run_time = 1)
        )
        self.wait()
        self.play(
            GrowFromPoint(arrows[2], arrows[2].get_start()),
            LaggedStartMap(FadeIn, word, run_time = 1)
        )
        self.wait()

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
        result.arrange(RIGHT, buff = MED_SMALL_BUFF)
        result.set_height(1)

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
        self.wait()

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
            lag_ratio = 0.5,
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
        pixels.set_height(4)
        pixels.next_to(neuron, RIGHT, LARGE_BUFF)
        rect = SurroundingRectangle(pixels, color = BLUE)

        pixels_to_detect = self.get_pixels_to_detect(pixels)

        self.play(
            FadeIn(rect),
            ShowCreation(
                pixels, 
                lag_ratio = 0.5,
                run_time = 2,
            )
        )
        self.play(
            pixels_to_detect.set_fill, WHITE, 1,
            lag_ratio = 0.5,
            run_time = 2
        )
        self.wait(2)

        self.pixels = pixels
        self.pixels_to_detect = pixels_to_detect
        self.pixels_group = VGroup(rect, pixels)

    def ask_about_parameters(self):
        pixels = self.pixels
        pixels_group = self.pixels_group
        neuron = self.neuron

        question = TextMobject("What", "parameters", "should exist?")
        parameter_word = question.get_part_by_tex("parameters")
        parameter_word.set_color(self.weights_color)
        question.move_to(neuron.edges_in.get_top(), LEFT)
        arrow = Arrow(
            parameter_word.get_bottom(),
            neuron.edges_in[0].get_center(),
            color = self.weights_color
        )

        p_labels = VGroup(*[
            TexMobject("p_%d\\!:"%(i+1)).set_color(self.weights_color)
            for i in range(8)
        ] + [TexMobject("\\vdots")])
        p_labels.arrange(DOWN, aligned_edge = LEFT)
        p_labels.next_to(parameter_word, DOWN, LARGE_BUFF)
        p_labels[-1].shift(SMALL_BUFF*RIGHT)

        def get_alpha_func(i, start = 0):
            # m = int(5*np.sin(2*np.pi*i/128.))
            m = random.randint(1, 10)
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
            pixels_group.set_height, 3,
            pixels_group.to_edge, RIGHT,
            LaggedStartMap(FadeIn, p_labels),
            LaggedStartMap(FadeIn, decimals),
        )
        self.wait()
        self.play(
            *changing_decimals + pixel_updates,
            run_time = 5,
            rate_func=linear
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
        weights_word.set_color(self.weights_color)
        weights_word.move_to(parameter_word)

        w_labels = VGroup()
        for p_label in p_labels:
            w_label = TexMobject(
                p_label.get_tex_string().replace("p", "w")
            )
            w_label.set_color(self.weights_color)
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
        self.play(LaggedStartMap(
            ApplyMethod, edges,
            lambda m : (m.rotate_in_place, np.pi/24),
            rate_func = wiggle,
            run_time = 2
        ))
        self.wait()

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
            TexMobject("w_n").set_color(self.weights_color),
            TexMobject("a_n")
        )
        weighted_sum.arrange(RIGHT, buff = SMALL_BUFF)
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
                for i in list(range(2, 12, 3)) + [-4, -3]
            ],
            run_time = 1.5
        )
        self.wait()
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
        self.wait(2)

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
                lag_ratio = 0.5,
                run_time = 3
            ),
            *[
                ReplacementTransform(decimal, pixel)
                for decimal, pixel in zip(decimals, weight_grid)
            ]
        )
        self.wait()

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
            lag_ratio = 0.5
        ))
        self.wait()
        self.play(Transform(
            pixels, digit,
            run_time = 2,
            lag_ratio = 0.5
        ))
        self.wait()
        self.play(weight_grid.move_to, pixels)
        self.wait()
        self.play(
            ReplacementTransform(
                self.pixels_to_detect.copy(),
                self.weighted_sum,
                run_time = 3,
                lag_ratio = 0.5
            ),
            Animation(weight_grid),
        )
        self.wait()

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
            for y in (6, 10)
            for x in range(14-4, 14+4)
        ])
        self.wait(2)
        self.play(weight_grid.move_to, pixels)
        self.wait(2)

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
            for n in (6, 10)
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
        weighted_sum.set_color_by_tex("w_", GREEN)
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
            for n in (-3, 3)
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
        lower_number_line.set_color(LIGHT_GREY)
        lower_number_line.numbers.set_color(WHITE)
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
        self.wait()

        self.lower_number_line = lower_number_line

    def squish_into_interval(self):
        line = self.number_line
        line.remove(*line.numbers)
        ghost_line = line.copy()
        ghost_line.fade(0.5)
        ghost_line.set_color(BLUE_E)
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
        self.wait(2)

class IntroduceSigmoid(GraphScene):
    CONFIG = {
        "x_min" : -5,
        "x_max" : 5,
        "x_axis_width" : 12,
        "y_min" : -1,
        "y_max" : 2,
        "y_axis_label" : "",
        "graph_origin" : DOWN,
        "x_labeled_nums" : list(range(-4, 5)),
        "y_labeled_nums" : list(range(-1, 3)),
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
        char = self.x_axis_label.replace("$", "")
        equation = TexMobject(
            "\\sigma(%s) = \\frac{1}{1+e^{-%s}}"%(char, char)
        )
        equation.next_to(name, DOWN)
        self.add(equation, name)

        self.equation = equation
        self.sigmoid_name = name

    def add_graph(self):
        graph = self.get_graph(
            lambda x : 1./(1+np.exp(-x)),
            color = YELLOW
        )

        self.play(ShowCreation(graph))
        self.wait()

        self.sigmoid_graph = graph

    ###

    def show_part(self, x_min, x_max, color):
        line, graph_part = [
            self.get_graph(
                func,
                x_min = x_min, 
                x_max = x_max,
                color = color,
            ).set_stroke(width = 4)
            for func in (lambda x : 0, sigmoid)
        ]

        self.play(ShowCreation(line))
        self.wait()
        self.play(Transform(line, graph_part))
        self.wait()

class IncludeBias(IntroduceWeights):
    def construct(self):
        self.force_skipping()
        self.zoom_in_on_one_neuron()
        self.setup_start()
        self.revert_to_original_skipping_status()

        self.add_sigmoid_label()
        self.words_on_activation()
        self.comment_on_need_for_bias()
        self.add_bias()
        self.summarize_weights_and_biases()

    def setup_start(self):
        self.weighted_sum = self.get_weighted_sum()
        digit = self.get_digit()
        rect = SurroundingRectangle(digit)
        d_group = VGroup(digit, rect)
        d_group.set_height(3)
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
        self.digit = digit
        self.weight_grid = weight_grid

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

        self.play(
            Write(name), 
            ShowCreation(arrow),
        )
        self.sigmoid_name = name
        self.sigmoid_arrow = arrow

    def words_on_activation(self):
        neuron = self.neuron
        weighted_sum = self.weighted_sum

        activation_word = TextMobject("Activation")
        activation_word.next_to(neuron, RIGHT)
        arrow = Arrow(neuron, weighted_sum.get_bottom())
        arrow.set_color(WHITE)
        words = TextMobject("How positive is this?")
        words.next_to(self.weighted_sum, UP, SMALL_BUFF)

        self.play(
            FadeIn(activation_word),
            neuron.set_fill, WHITE, 0.8,
        )
        self.wait()
        self.play(
            GrowArrow(arrow),
            ReplacementTransform(activation_word, words),
        )
        self.wait(2)
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
        words.set_color_by_tex("weighted", GREEN)
        words.next_to(neuron, RIGHT)

        self.play(Write(words, run_time = 2))
        self.play(ApplyMethod(
            colored_pixels.shift, MED_LARGE_BUFF*UP,
            rate_func = there_and_back,
            run_time = 2,
            lag_ratio = 0.5
        ))
        self.wait()

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
        VGroup(rect, name).set_color(BLUE)

        self.play(
            ReplacementTransform(
                self.gt_ten.copy(), bias,
                run_time = 2
            ),
            MoveToTarget(rp),
        )
        self.wait(2)
        self.play(
            ShowCreation(rect),
            Write(name)
        )
        self.wait(2)

        self.bias_name = name

    def summarize_weights_and_biases(self):
        weight_grid = self.weight_grid
        bias_name = self.bias_name

        self.play(LaggedStartMap(
            ApplyMethod, weight_grid,
            lambda p : (p.set_fill, 
                random.choice([GREEN, GREEN, RED]),
                random.random()
            ),
            rate_func = there_and_back,
            lag_ratio = 0.4,
            run_time = 4
        ))
        self.wait()
        self.play(Indicate(bias_name))
        self.wait(2)

    ###

    def get_weighted_sum(self):
        args = ["\\sigma \\big("]
        for d in range(1, 4):
            args += ["w_%d"%d, "a_%d"%d, "+"]
        args += ["\\cdots", "+", "w_n", "a_n"]
        args += ["\\big)"]
        weighted_sum = TexMobject(*args)
        weighted_sum.set_color_by_tex("w_", GREEN)
        weighted_sum.set_color_by_tex("\\big", YELLOW)
        weighted_sum.to_edge(UP, LARGE_BUFF)
        weighted_sum.shift(RIGHT)

        return weighted_sum

class BiasForInactiviyWords(Scene):
    def construct(self):
        words = TextMobject("Bias for inactivity")
        words.set_color(BLUE)
        words.set_width(FRAME_WIDTH - 1)
        words.to_edge(UP)

        self.play(Write(words))
        self.wait(3)

class ContinualEdgeUpdate(VGroup):
    CONFIG = {
        "max_stroke_width" : 3,
        "stroke_width_exp" : 7,
        "n_cycles" : 5,
        "colors" : [GREEN, GREEN, GREEN, RED],
    }
    def __init__(self, network_mob, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.internal_time = 0
        n_cycles = self.n_cycles
        edges = VGroup(*it.chain(*network_mob.edge_groups))
        self.move_to_targets = []
        for edge in edges:
            edge.colors = [
                random.choice(self.colors)
                for x in range(n_cycles)
            ]
            msw = self.max_stroke_width
            edge.widths = [
                msw*random.random()**self.stroke_width_exp
                for x in range(n_cycles)
            ]
            edge.cycle_time = 1 + random.random()

            edge.generate_target()
            edge.target.set_stroke(edge.colors[0], edge.widths[0])
            edge.become(edge.target)
            self.move_to_targets.append(edge)
        self.edges = edges
        self.add(edges)
        self.add_updater(lambda m, dt: self.update_edges(dt))

    def update_edges(self, dt):
        self.internal_time += dt
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
                ShowCreation(edges, lag_ratio = 0.5),
                FadeIn(neuron),
                *added_anims,
                run_time = 1.5
            )
            last_edges = edges
        self.play(
            LaggedStartMap(
                ShowCreation, VGroup(*[
                    n.edges_in for n in neurons[7:]
                ]),
                run_time = 3,
            ),
            LaggedStartMap(
                FadeIn, VGroup(*neurons[7:]),
                run_time = 3,
            ),
            VGroup(*last_edges[1:]).set_stroke, None, 1
        )
        self.wait()

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
            LaggedStartMap(
                GrowArrow, arrows, 
                run_time = 3,
                lag_ratio = 0.3,
            )
        )
        self.wait()

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
        self.wait()
        self.play(
            ReplacementTransform(times_16.copy(), bias_count[0]),
            FadeOut(bb1),
            ReplacementTransform(bb2, bias_count[1]),
            FadeOut(bb3),
            LaggedStartMap(FadeOut, bias_arrows)
        )
        self.wait()

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
        group.arrange(RIGHT, SMALL_BUFF)
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
            LaggedStartMap(
                ShowCreation, edges,
                run_time = 4,
                lag_ratio = 0.3,
            ),
            LaggedStartMap(
                FadeIn, neurons,
                run_time = 4,
                lag_ratio = 0.3,
            )
        )
        self.wait(2)

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
        self.wait()

        self.final_number = num_mob

    def tweak_weights(self):
        learning = TextMobject("Learning $\\rightarrow$")
        finding_words = TextMobject(
            "Finding the right \\\\ weights and biases"
        )
        group = VGroup(learning, finding_words)
        group.arrange(RIGHT)
        group.scale(0.8)
        group.next_to(self.final_number, DOWN, MED_LARGE_BUFF)

        self.add(ContinualEdgeUpdate(self.network_mob))
        self.wait(5)
        self.play(Write(group))
        self.wait(10)

    ###

    def get_edge_weight_wandering_anim(self, edges):
        for edge in edges:
            edge.generate_target()
            edge.target.set_stroke(
                color = random.choice([GREEN, GREEN, GREEN, RED]),
                width = 3*random.random()**7
            )
        self.play(
            LaggedStartMap(
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
        self.wait()
        self.play(Blink(randy))
        self.wait()
        self.play(randy.change, "horrified", network_mob)
        self.play(Blink(randy))
        self.wait(10)

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
        self.wait()
        self.play(*list(map(FadeOut, [words, box])))

    def incorrect_classification(self):
        network = self.network
        training_data, validation_data, test_data = load_data_wrapper()
        for in_vect, result in test_data[20:]:
            network_answer = np.argmax(network.feedforward(in_vect))
            if network_answer != result:
                break
        self.feed_in_image(in_vect)

        wrong = TextMobject("Wrong!")
        wrong.set_color(RED)
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
        self.wait(10)


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
        self.wait(7)

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

        weighted_sum.arrange(RIGHT)
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

        w_labels.set_color(GREEN)
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
        VGroup(name, arrow, bias).set_color(BLUE)

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
        VGroup(sigmoid_name, mob).set_color(YELLOW)

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
        ).arrange(DOWN)
        column.shift(DOWN + 3.5*RIGHT)

        pre_brackets = self.get_brackets(a_labels)
        post_bracketes = self.get_brackets(column)
        pre_brackets.set_fill(opacity = 0)

        self.play(FocusOn(self.a_labels[0]))
        self.play(LaggedStartMap(
            Indicate, self.a_labels,
            rate_func = there_and_back,
            run_time = 1
        ))
        self.play(
            MoveToTarget(a_labels),
            Transform(pre_brackets, post_bracketes),
            run_time = 2
        )
        self.wait()
        self.play(*[
            LaggedStartMap(Indicate, mob, rate_func = there_and_back)
            for mob in (a_labels, a_labels_in_sum)
        ])
        self.wait()

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
        w_labels.target.arrange(RIGHT)
        w_labels.target.next_to(a_column[0], LEFT, buff = 0.8)
        lwb.next_to(w_labels.target, LEFT, SMALL_BUFF)
        lwb.align_to(rwb, UP)

        row_1, row_k = [
            VGroup(*list(map(TexMobject, [
                "w_{%s, 0}"%i,
                "w_{%s, 1}"%i,
                "\\cdots",
                "w_{%s, n}"%i,
            ])))
            for i in ("1", "k")
        ]
        dots_row = VGroup(*list(map(TexMobject, [
            "\\vdots", "\\vdots", "\\ddots", "\\vdots"
        ])))

        lower_rows = VGroup(row_1, dots_row, row_k)
        lower_rows.scale(0.75)
        last_row = w_labels.target
        for row in lower_rows:
            for target, mover in zip(last_row, row):
                mover.move_to(target)
                if "w" in mover.get_tex_string():
                    mover.set_color(GREEN)
            row.next_to(last_row, DOWN, buff = 0.45)
            last_row = row

        self.play(
            MoveToTarget(w_labels),
            Write(w_brackets, run_time = 1)
        )
        self.play(FadeIn(
            lower_rows,
            run_time = 3,
            lag_ratio = 0.5,
        ))
        self.wait()

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
            self.play(LaggedStartMap(
                ShowCreationThenDestruction, edges,
                lag_ratio = 0.8
            ))
        self.wait()

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
                mob = TexMobject("?").scale(1.3).set_color(YELLOW)
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
        self.play(LaggedStartMap(
            FadeIn, VGroup(*result_terms[1:])
        ))
        self.wait(2)
        self.show_meaning_of_lower_rows(
            arrow, brace, top_row_rect, result_terms
        )
        self.play(*list(map(FadeOut, [
            result_terms, result_brackets, equals, column_rect
        ])))

    def show_meaning_of_lower_rows(self, arrow, brace, row_rect, result_terms):
        n1, n2, nk = neurons = VGroup(*[
            self.network_mob.layers[1].neurons[i]
            for i in (0, 1, -1)
        ])
        for n in neurons:
            n.save_state()
            n.edges_in.save_state()

        rect2 = SurroundingRectangle(result_terms[1])
        rectk = SurroundingRectangle(result_terms[-1])
        VGroup(rect2, rectk).set_color(WHITE)
        row2 = self.lower_matrix_rows[0]
        rowk = self.lower_matrix_rows[-1]

        def show_edges(neuron):
            self.play(LaggedStartMap(
                ShowCreationThenDestruction,
                neuron.edges_in.copy().set_stroke(GREEN, 5),
                lag_ratio = 0.7,
                run_time = 1,
            ))

        self.play(
            row_rect.move_to, row2,
            n1.fade,
            n1.set_fill, None, 0,
            n1.edges_in.set_stroke, None, 1,
            n2.set_stroke, WHITE, 3,
            n2.edges_in.set_stroke, None, 3,
            ReplacementTransform(arrow, rect2),
            FadeOut(brace),
        )
        show_edges(n2)
        self.play(
            row_rect.move_to, rowk,
            n2.restore,
            n2.edges_in.restore,
            nk.set_stroke, WHITE, 3,
            nk.edges_in.set_stroke, None, 3,
            ReplacementTransform(rect2, rectk),
        )
        show_edges(nk)
        self.play(
            n1.restore,
            n1.edges_in.restore,
            nk.restore,
            nk.edges_in.restore,
            FadeOut(rectk),
            FadeOut(row_rect),
        )

    def add_bias_vector(self):
        bias = self.bias
        bias_name = self.bias_name
        a_column_brackets = self.a_column_brackets
        a_column = self.a_column

        plus = TexMobject("+")
        b_brackets = a_column_brackets.copy()
        b_column = VGroup(*list(map(TexMobject, [
            "b_0", "b_1", "\\vdots", "b_n",
        ])))
        b_column.scale(0.85)
        b_column.arrange(DOWN, buff = 0.35)
        b_column.move_to(a_column)
        b_column.set_color(BLUE)
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
        self.play(LaggedStartMap(
            FadeIn, VGroup(*b_column[1:])
        ))
        self.wait()

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
        parens.set_color(YELLOW)

        self.play(
            sigma.scale, 2,
            sigma.next_to, big_lp, LEFT, SMALL_BUFF,
            Transform(slp, big_lp),
            Transform(srp, big_rp),
        )
        self.wait(2)

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
        expression.set_color_by_tex_to_color_map({
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
        neurons.add_to_back(self.network_mob.layers[1].neurons[0])

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
        self.wait()
        self.play(*neuron_anims, run_time = 2)
        self.play(
            ReplacementTransform(neurons.copy(), a1),
            FadeIn(equals)
        )
        self.wait(2)

    def fade_weighted_sum(self):
        self.play(*list(map(FadeOut, [
            self.a1_label, self.a1_equals,
            self.sigma, self.sigma_parens, 
            self.weighted_sum,
            self.bias_name,
            self.sigmoid_name,
        ])))


    ###

    def get_brackets(self, mob):
        lb, rb = both = TexMobject("\\big[\\big]")
        both.set_width(mob.get_width())
        both.stretch_to_fit_height(1.2*mob.get_height())
        lb.next_to(mob, LEFT, SMALL_BUFF)
        rb.next_to(mob, RIGHT, SMALL_BUFF)
        return both

class HorrifiedMorty(Scene):
    def construct(self):
        morty = Mortimer()
        morty.flip()
        morty.scale(2)

        for mode in "horrified", "hesitant":
            self.play(
                morty.change, mode,
                morty.look, UP,
            )
            self.play(Blink(morty))
            self.wait(2)

class SigmoidAppliedToVector(Scene):
    def construct(self):
        tex = TexMobject("""
            \\sigma \\left(
            \\left[\\begin{array}{c}
                x \\\\ y \\\\ z
            \\end{array}\\right]
            \\right) =
            \\left[\\begin{array}{c}
                \\sigma(x) \\\\ \\sigma(y) \\\\ \\sigma(z)
            \\end{array}\\right]
        """)
        tex.set_width(FRAME_WIDTH - 1)
        tex.to_edge(DOWN)
        indices = it.chain(
            [0], list(range(1, 5)), list(range(16, 16+4)),
            list(range(25, 25+2)), [25+3],
            list(range(29, 29+2)), [29+3],
            list(range(33, 33+2)), [33+3],
        )
        for i in indices:
            tex[i].set_color(YELLOW)
        self.add(tex)
        self.wait()

class EoLA3Wrapper(PiCreatureScene):
    def construct(self):
        morty = self.pi_creature
        rect = ScreenRectangle(height = 5)
        rect.next_to(morty, UP+LEFT)
        rect.to_edge(UP, buff = LARGE_BUFF)
        title = TextMobject("Essence of linear algebra")
        title.next_to(rect, UP)

        self.play(
            ShowCreation(rect),
            FadeIn(title),
            morty.change, "raise_right_hand", rect
        )
        self.wait(4)

class FeedForwardCode(ExternallyAnimatedScene):
    pass

class NeuronIsFunction(MoreHonestMNistNetworkPreview):
    CONFIG  = {
        "network_mob_config" : {
            "layer_to_layer_buff" : 2
        }
    }
    def construct(self):
        self.setup_network_mob()
        self.activate_network()
        self.write_neuron_holds_a_number()
        self.feed_in_new_image(8, 7)
        self.neuron_is_function()
        self.show_neuron_as_function()
        self.fade_network_back_in()
        self.network_is_a_function()
        self.feed_in_new_image(9, 4)
        self.wait(2)


    def setup_network_mob(self):
        self.network_mob.scale(0.7)
        self.network_mob.to_edge(DOWN)
        self.network_mob.shift(LEFT)

    def activate_network(self):
        network_mob = self.network_mob
        self.image_map = get_organized_images()
        in_vect = self.image_map[3][0]
        mnist_mob = MNistMobject(in_vect)
        mnist_mob.next_to(network_mob, LEFT, MED_LARGE_BUFF, UP)
        activations = self.network.get_activation_of_all_layers(in_vect)
        for i, activation in enumerate(activations):
            layer = self.network_mob.layers[i]
            Transform(
                layer, self.network_mob.get_active_layer(i, activation)
            ).update(1)
        self.add(mnist_mob)

        self.image_rect, self.curr_image = mnist_mob

    def write_neuron_holds_a_number(self):
        neuron_word = TextMobject("Neuron")
        arrow = Arrow(ORIGIN, DOWN, color = BLUE)
        thing_words = TextMobject("Thing that holds \\\\ a number")
        group = VGroup(neuron_word, arrow, thing_words)
        group.arrange(DOWN)
        group.to_corner(UP+RIGHT, buff = LARGE_BUFF)

        neuron = self.network_mob.layers[2].neurons[2]
        decimal = DecimalNumber(neuron.get_fill_opacity())
        decimal.set_width(0.7*neuron.get_width())
        decimal.move_to(neuron)
        neuron_group = VGroup(neuron, decimal)
        neuron_group.save_state()
        decimal.set_fill(opacity = 0)

        self.play(
            neuron_group.restore,
            neuron_group.scale, 3,
            neuron_group.next_to, neuron_word, LEFT,
            FadeIn(neuron_word),
            GrowArrow(arrow),
            FadeIn(
                thing_words, run_time = 2,
                rate_func = squish_rate_func(smooth, 0.3, 1)
            )
        )
        self.wait()
        self.play(neuron_group.restore)

        self.neuron_word = neuron_word
        self.neuron_word_arrow = arrow
        self.thing_words = thing_words
        self.neuron = neuron
        self.decimal = decimal

    def feed_in_new_image(self, digit, choice):
        in_vect = self.image_map[digit][choice]

        args = []
        for s in "answer_rect", "curr_image", "image_rect":
            if hasattr(self, s):
                args.append(getattr(self, s))
            else:
                args.append(VectorizedPoint())
        MoreHonestMNistNetworkPreview.reset_display(self, *args)
        self.feed_in_image(in_vect)

    def neuron_is_function(self):
        thing_words = self.thing_words
        cross = Cross(thing_words)
        function_word = TextMobject("Function")
        function_word.move_to(thing_words, UP)

        self.play(
            thing_words.fade,
            ShowCreation(cross)
        )
        self.play(
            FadeIn(function_word),
            VGroup(thing_words, cross).to_edge, DOWN,
        )
        self.wait()

        self.function_word = function_word

    def show_neuron_as_function(self):
        neuron = self.neuron.copy()
        edges = neuron.edges_in.copy()
        prev_layer = self.network_mob.layers[1].copy()

        arrow = Arrow(ORIGIN, RIGHT, color = BLUE)
        arrow.next_to(neuron, RIGHT, SMALL_BUFF)
        decimal = DecimalNumber(neuron.get_fill_opacity())
        decimal.next_to(arrow, RIGHT)

        self.play(
            FadeOut(self.network_mob),
            *list(map(Animation, [neuron, edges, prev_layer]))
        )
        self.play(LaggedStartMap(
            ShowCreationThenDestruction, 
            edges.copy().set_stroke(YELLOW, 4),
        ))
        self.play(
            GrowArrow(arrow),
            Transform(self.decimal, decimal)
        )
        self.wait(2)

        self.non_faded_network_parts = VGroup(
            neuron, edges, prev_layer
        )
        self.neuron_arrow = arrow

    def fade_network_back_in(self):
        anims = [
            FadeIn(
                mob, 
                run_time = 2, 
                lag_ratio = 0.5
            )
            for mob in (self.network_mob.layers, self.network_mob.edge_groups)
        ]
        anims += [
            FadeOut(self.neuron_arrow),
            FadeOut(self.decimal),
        ]
        anims.append(Animation(self.non_faded_network_parts))

        self.play(*anims)
        self.remove(self.non_faded_network_parts)

    def network_is_a_function(self):
        neuron_word = self.neuron_word
        network_word = TextMobject("Network")
        network_word.set_color(YELLOW)
        network_word.move_to(neuron_word)

        func_tex = TexMobject(
            "f(a_0, \\dots, a_{783}) = ",
            """\\left[
                \\begin{array}{c} 
                    y_0 \\\\ \\vdots \\\\ y_{9} 
                \\end{array}
            \\right]"""
        )
        func_tex.to_edge(UP)
        func_tex.shift(MED_SMALL_BUFF*LEFT)

        self.play(
            ReplacementTransform(neuron_word, network_word),
            FadeIn(func_tex)
        )

    ###

    def reset_display(self, answer_rect, image, image_rect):
        #Don't do anything, just record these args
        self.answer_rect = answer_rect
        self.curr_image = image
        self.image_rect = image_rect
        return

class ComplicationIsReassuring(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "It kind of has to \\\\ be complicated, right?",
            target_mode = "speaking",
            student_index = 0
        )
        self.play(self.teacher.change, "happy")
        self.wait(4)

class NextVideo(MoreHonestMNistNetworkPreview, PiCreatureScene):
    CONFIG = {
        "network_mob_config" : {
            "neuron_stroke_color" : WHITE,
            "layer_to_layer_buff" : 2.5,
            "brace_for_large_layers" : False,
        }
    }
    def setup(self):
        MoreHonestMNistNetworkPreview.setup(self)
        PiCreatureScene.setup(self)

    def construct(self):
        self.network_and_data()
        self.show_next_video()
        self.talk_about_subscription()
        self.show_video_neural_network()

    def network_and_data(self):
        morty = self.pi_creature
        network_mob = self.network_mob
        network_mob.to_edge(LEFT)
        for obj in network_mob, self:
            obj.remove(network_mob.output_labels)
        network_mob.scale(0.7)
        network_mob.shift(RIGHT)
        edge_update = ContinualEdgeUpdate(network_mob)

        training_data, validation_data, test_data = load_data_wrapper()
        data_mobs = VGroup()
        for vect, num in test_data[:30]:
            image = MNistMobject(vect)
            image.set_height(0.7)
            arrow = Arrow(ORIGIN, RIGHT, color = BLUE)
            num_mob = TexMobject(str(num))
            group = Group(image, arrow, num_mob)
            group.arrange(RIGHT, buff = SMALL_BUFF)
            group.next_to(ORIGIN, RIGHT)
            data_mobs.add(group)

        data_mobs.next_to(network_mob, UP)

        self.add(edge_update)
        self.play(morty.change, "confused", network_mob)
        self.wait(2)
        for data_mob in data_mobs:
            self.add(data_mob)
            self.wait(0.2)
            self.remove(data_mob)

        self.content = network_mob
        self.edge_update = edge_update

    def show_next_video(self):
        morty = self.pi_creature
        content = self.content

        video = VideoIcon()
        video.set_height(3)
        video.set_fill(RED, 0.8)
        video.next_to(morty, UP+LEFT)

        rect = SurroundingRectangle(video)
        rect.set_stroke(width = 0)
        rect.set_fill(BLACK, 0.5)

        words = TextMobject("On learning")
        words.next_to(video, UP)

        if self.edge_update.internal_time < 1:
            self.edge_update.internal_time = 2
        self.play(
            content.set_height, 0.8*video.get_height(),
            content.move_to, video,
            morty.change, "raise_right_hand",
            FadeIn(rect),
            FadeIn(video),
        )
        self.add_foreground_mobjects(rect, video)
        self.wait(2)
        self.play(Write(words))
        self.wait(2)

        self.video = Group(content, rect, video, words)

    def talk_about_subscription(self):
        morty = self.pi_creature
        morty.generate_target()
        morty.target.change("hooray")
        morty.target.rotate(
            np.pi, axis = UP, about_point = morty.get_left()
        )
        morty.target.shift(LEFT)
        video = self.video


        subscribe_word = TextMobject(
            "Subscribe", "!",
            arg_separator = ""
        )
        bang = subscribe_word[1]
        subscribe_word.to_corner(DOWN+RIGHT)
        subscribe_word.shift(3*UP)
        q_mark = TextMobject("?")
        q_mark.move_to(bang, LEFT)
        arrow = Arrow(ORIGIN, DOWN, color = RED, buff = 0)
        arrow.next_to(subscribe_word, DOWN)
        arrow.shift(MED_LARGE_BUFF * RIGHT)

        self.play(
            Write(subscribe_word),
            self.video.shift, 3*LEFT,
            MoveToTarget(morty),
        )
        self.play(GrowArrow(arrow))
        self.wait(2)
        self.play(morty.change, "maybe", arrow)
        self.play(Transform(bang, q_mark))
        self.wait(3)

    def show_video_neural_network(self):
        morty = self.pi_creature

        network_mob, rect, video, words = self.video
        network_mob.generate_target(use_deepcopy = True)
        network_mob.target.set_height(5)
        network_mob.target.to_corner(UP+LEFT)
        neurons = VGroup(*network_mob.target.layers[-1].neurons[:2])
        neurons.set_stroke(width = 0)

        video.generate_target()
        video.target.set_fill(opacity = 1)
        video.target.set_height(neurons.get_height())
        video.target.move_to(neurons, LEFT)

        self.play(
            MoveToTarget(network_mob),
            MoveToTarget(video),
            FadeOut(words),
            FadeOut(rect),
            morty.change, "raise_left_hand"
        )

        neuron_pairs = VGroup(*[
            VGroup(*network_mob.layers[-1].neurons[2*i:2*i+2])
            for i in range(1, 5)
        ])
        for pair in neuron_pairs:
            video = video.copy()
            video.move_to(pair, LEFT)
            pair.target = video

        self.play(LaggedStartMap(
            MoveToTarget, neuron_pairs,
            run_time = 3
        ))
        self.play(morty.change, "shruggie")
        self.wait(10)

    ###

class NNPatreonThanks(PatreonThanks):
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
            "Andy Nichols",
            "Harsev Singh",
            "Mads Elvheim",
            "Erik Sundell",
            "Xueqi Li",
            "David G. Stork",
            "Tianyu Ge",
            "Ted Suzman",
            "Linh Tran",
            "Andrew Busey",
            "Michael McGuffin",
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

class PiCreatureGesture(PiCreatureScene):
    def construct(self):
        self.play(self.pi_creature.change, "raise_right_hand")
        self.wait(5)
        self.play(self.pi_creature.change, "happy")
        self.wait(4)

class IntroduceReLU(IntroduceSigmoid):
    CONFIG = {
        "x_axis_label" : "$a$"
    }
    def construct(self):
        self.setup_axes()
        self.add_title()
        self.add_graph()
        self.old_school()
        self.show_ReLU()
        self.label_input_regions()

    def old_school(self):
        sigmoid_graph = self.sigmoid_graph
        sigmoid_title = VGroup(
            self.sigmoid_name,
            self.equation
        )
        cross = Cross(sigmoid_title)
        old_school = TextMobject("Old school")
        old_school.to_corner(UP+RIGHT)
        old_school.set_color(RED)
        arrow = Arrow(
            old_school.get_bottom(), 
            self.equation.get_right(),
            color = RED
        )

        self.play(ShowCreation(cross))
        self.play(
            Write(old_school, run_time = 1),
            GrowArrow(arrow)
        )
        self.wait(2)
        self.play(
            ApplyMethod(
                VGroup(cross, sigmoid_title).shift, 
                FRAME_X_RADIUS*RIGHT,
                rate_func = running_start
            ),
            FadeOut(old_school),
            FadeOut(arrow),
        )
        self.play(ShowCreation(
            self.sigmoid_graph,
            rate_func = lambda t : smooth(1-t),
            remover = True
        ))

    def show_ReLU(self):
        graph = VGroup(
            Line(
                self.coords_to_point(-7, 0),
                self.coords_to_point(0, 0),
            ),
            Line(
                self.coords_to_point(0, 0),
                self.coords_to_point(4, 4),
            ),
        )
        graph.set_color(YELLOW)
        char = self.x_axis_label.replace("$", "")
        equation = TextMobject("ReLU($%s$) = max$(0, %s)$"%(char, char))
        equation.shift(FRAME_X_RADIUS*LEFT/2)
        equation.to_edge(UP)
        equation.add_background_rectangle()
        name = TextMobject("Rectified linear unit")
        name.move_to(equation)
        name.add_background_rectangle()

        self.play(Write(equation))
        self.play(ShowCreation(graph), Animation(equation))
        self.wait(2)
        self.play(
            Write(name),
            equation.shift, DOWN
        )
        self.wait(2)

        self.ReLU_graph = graph

    def label_input_regions(self):
        l1, l2 = self.ReLU_graph
        neg_words = TextMobject("Inactive")
        neg_words.set_color(RED)
        neg_words.next_to(self.coords_to_point(-2, 0), UP)

        pos_words = TextMobject("Same as $f(a) = a$")
        pos_words.set_color(GREEN)
        pos_words.next_to(
            self.coords_to_point(1, 1),
            DOWN+RIGHT
        )

        self.revert_to_original_skipping_status()
        self.play(ShowCreation(l1.copy().set_color(RED)))
        self.play(Write(neg_words))
        self.wait()
        self.play(ShowCreation(l2.copy().set_color(GREEN)))
        self.play(Write(pos_words))
        self.wait(2)

class CompareSigmoidReLUOnDeepNetworks(PiCreatureScene):
    def construct(self):
        morty, lisha = self.morty, self.lisha
        sigmoid_graph = FunctionGraph(
            sigmoid,
            x_min = -5,
            x_max = 5,
        )
        sigmoid_graph.stretch_to_fit_width(3)
        sigmoid_graph.set_color(YELLOW)
        sigmoid_graph.next_to(lisha, UP+LEFT)
        sigmoid_graph.shift_onto_screen()
        sigmoid_name = TextMobject("Sigmoid")
        sigmoid_name.next_to(sigmoid_graph, UP)
        sigmoid_graph.add(sigmoid_name)

        slow_learner = TextMobject("Slow learner")
        slow_learner.set_color(YELLOW)
        slow_learner.to_corner(UP+LEFT)
        slow_arrow = Arrow(
            slow_learner.get_bottom(),
            sigmoid_graph.get_top(),
        )

        relu_graph = VGroup(
            Line(2*LEFT, ORIGIN),
            Line(ORIGIN, np.sqrt(2)*(RIGHT+UP)),
        )
        relu_graph.set_color(BLUE)
        relu_graph.next_to(lisha, UP+RIGHT)
        relu_name = TextMobject("ReLU")
        relu_name.move_to(relu_graph, UP)
        relu_graph.add(relu_name)

        network_mob = NetworkMobject(Network(
            sizes = [6, 4, 5, 4, 3, 5, 2]
        ))
        network_mob.scale(0.8)
        network_mob.to_edge(UP, buff = MED_SMALL_BUFF)
        network_mob.shift(RIGHT)
        edge_update = ContinualEdgeUpdate(
            network_mob, stroke_width_exp = 1,
        )

        self.play(
            FadeIn(sigmoid_name),
            ShowCreation(sigmoid_graph),
            lisha.change, "raise_left_hand",
            morty.change, "pondering"
        )
        self.play(
            Write(slow_learner, run_time = 1),
            GrowArrow(slow_arrow)
        )
        self.wait()
        self.play(
            FadeIn(relu_name),
            ShowCreation(relu_graph),
            lisha.change, "raise_right_hand",
            morty.change, "thinking"
        )
        self.play(FadeIn(network_mob))
        self.add(edge_update)
        self.wait(10)



    ###
    def create_pi_creatures(self):
        morty = Mortimer()
        morty.shift(FRAME_X_RADIUS*RIGHT/2).to_edge(DOWN)
        lisha = PiCreature(color = BLUE_C)
        lisha.shift(FRAME_X_RADIUS*LEFT/2).to_edge(DOWN)
        self.morty, self.lisha = morty, lisha
        return morty, lisha

class ShowAmplify(PiCreatureScene):
    def construct(self):
        morty = self.pi_creature
        rect = ScreenRectangle(height = 5)
        rect.to_corner(UP+LEFT)
        rect.shift(DOWN)
        email = TextMobject("3blue1brown@amplifypartners.com")
        email.next_to(rect, UP)

        self.play(
            ShowCreation(rect),
            morty.change, "raise_right_hand"
        )
        self.wait(2)
        self.play(Write(email))
        self.play(morty.change, "happy", rect)
        self.wait(10)

class Thumbnail(NetworkScene):
    CONFIG = {
        "network_mob_config" : {
            'neuron_stroke_color' : WHITE,
            'layer_to_layer_buff': 1.25,
        },
    }
    def construct(self):
        network_mob = self.network_mob
        network_mob.set_height(FRAME_HEIGHT - 1)
        for layer in network_mob.layers:
            layer.neurons.set_stroke(width = 5)

        network_mob.set_height(5)
        network_mob.to_edge(DOWN)
        network_mob.to_edge(LEFT, buff=1)

        subtitle = TextMobject(
            "From the\\\\",
            "ground up\\\\",
        )
        # subtitle.arrange(
        #     DOWN,
        #     buff=0.25,
        #     aligned_edge=LEFT,
        # )
        subtitle.set_color(YELLOW)
        subtitle.set_height(2.75)
        subtitle.next_to(network_mob, RIGHT, buff=MED_LARGE_BUFF)

        edge_update = ContinualEdgeUpdate(
            network_mob,
            max_stroke_width = 10,
            stroke_width_exp = 4,
        )
        edge_update.internal_time = 3
        edge_update.update(0)

        for mob in network_mob.family_members_with_points():
            if mob.get_stroke_width() < 2:
                mob.set_stroke(width=2)


        title = TextMobject("Neural Networks")
        title.scale(3)
        title.to_edge(UP)

        self.add(network_mob)
        self.add(subtitle)
        self.add(title)














