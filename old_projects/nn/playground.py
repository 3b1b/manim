#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os.path
from functools import reduce

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from constants import *

from manimlib.imports import *

from nn.network import *
from nn.part1 import *


class Test(Scene):
    def construct(self):
        network = get_pretrained_network()
        training_data, validation_data, test_data = load_data_wrapper()
        self.show_weight_rows(network, index = 0)
        # self.show_maximizing_inputs(network)
        # self.show_all_activation_images(network, test_data)

        # group = Group()
        # for k in range(10):
        #     v = np.zeros((10, 1))
        #     v[k] = 1
        #     h_group = Group()
        #     for W, b in reversed(zip(network.weights, network.biases)):
        #         h_group.add(MNistMobject(v))
        #         v = np.dot(W.T, sigmoid_inverse(v) - b)
        #         v = sigmoid(v)
        #     h_group.add(MNistMobject(v))
        #     h_group.arrange(LEFT)
        #     group.add(h_group)
        # group.arrange(DOWN)
        # group.set_height(FRAME_HEIGHT - 1)
        # self.add(group)


    def show_random_results(self):
        group = Group(*[
            Group(*[
                MNistMobject(a)
                for a in network.get_activation_of_all_layers(
                    np.random.randn(784, 1)
                )
            ]).arrange(RIGHT)
            for x in range(10)
        ]).arrange(DOWN)
        group.set_height(FRAME_HEIGHT - 1)
        self.add(group)

    def show_weight_rows(self, network, index):
        group = VGroup()
        for row in network.weights[index]:
            mob = PixelsFromVect(np.zeros(row.size))
            for n, pixel in zip(row, mob):
                color = GREEN if n > 0 else RED
                opacity = 2*(sigmoid(abs(n)) - 0.5)
                pixel.set_fill(color, opacity = opacity)
            group.add(mob)
        group.arrange_in_grid()
        group.set_height(FRAME_HEIGHT - 1)
        self.add(group)

    def show_all_activation_images(self, network, test_data):
        image_samples = Group(*[
            self.get_activation_images(digit, network, test_data)
            for digit in range(10)
        ])
        image_samples.arrange_in_grid(
            n_rows = 2, buff = LARGE_BUFF
        )
        image_samples.set_height(FRAME_HEIGHT - 1)
        self.add(image_samples)

    def get_activation_images(self, digit, network, test_data, n_examples = 8):
        input_vectors = [
            data[0] 
            for data in test_data
            if data[1] == digit
        ]
        activation_iamges = Group(*[
            Group(*[
                MNistMobject(a)
                for a in network.get_activation_of_all_layers(vect)
            ]).arrange(RIGHT)
            for vect in input_vectors[:n_examples]
        ]).arrange(DOWN)
        activation_iamges.set_height(FRAME_HEIGHT - 1)
        return activation_iamges

    def show_two_blend(self):
        training_data, validation_data, test_data = load_data_wrapper()
        vects = [
            data[0]
            for data in training_data[:30]
            if np.argmax(data[1]) == 2
        ]
        mean_vect = reduce(op.add, vects)/len(vects)
        self.add(MNistMobject(mean_vect))

    def show_maximizing_inputs(self, network):
        training_data, validation_data, test_data = load_data_wrapper()
        layer = 1
        n_neurons = DEFAULT_LAYER_SIZES[layer]
        groups = Group()
        for k in range(n_neurons):
            out = np.zeros(n_neurons)
            out[k] = 1
            in_vect = maximizing_input(network, layer, out)
            new_out = network.get_activation_of_all_layers(in_vect)[layer]
            group = Group(*list(map(MNistMobject, [in_vect, new_out])))
            group.arrange(DOWN+RIGHT, SMALL_BUFF)
            groups.add(group)
        groups.arrange_in_grid()
        groups.set_height(FRAME_HEIGHT - 1)
        self.add(groups)

    def show_test_input(self, network):
        training_data, validation_data, test_data = load_data_wrapper()
        group = Group(*[
            self.get_set(network, test)
            for test in test_data[3:20]
            if test[1] in [4, 9]
        ])
        group.arrange(DOWN, buff = MED_LARGE_BUFF)
        group.set_height(FRAME_HEIGHT - 1)
        self.play(FadeIn(group))

    def get_set(self, network, test):
        test_in, test_out = test
        activations = network.get_activation_of_all_layers(test_in)
        group = Group(*list(map(MNistMobject, activations)))
        group.arrange(RIGHT, buff = LARGE_BUFF)
        return group

    # def show_frame(self):
    #     pass


if __name__ == "__main__":
    save_pretrained_network()
    test_network()
































