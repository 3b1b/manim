"""
network.py
~~~~~~~~~~

A module to implement the stochastic gradient descent learning
algorithm for a feedforward neural network.  Gradients are calculated
using backpropagation.  Note that I have focused on making the code
simple, easily readable, and easily modifiable.  It is not optimized,
and omits many desirable features.
"""


#### Libraries
# Standard library
import os
import pickle
import random

# Third-party libraries
import numpy as np
from PIL import Image
from nn.mnist_loader import load_data_wrapper
# from utils.space_ops import get_norm

NN_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
# PRETRAINED_DATA_FILE = os.path.join(NN_DIRECTORY, "pretrained_weights_and_biases_80")
# PRETRAINED_DATA_FILE = os.path.join(NN_DIRECTORY, "pretrained_weights_and_biases_ReLU")
PRETRAINED_DATA_FILE = os.path.join(NN_DIRECTORY, "pretrained_weights_and_biases")
IMAGE_MAP_DATA_FILE = os.path.join(NN_DIRECTORY, "image_map")
# PRETRAINED_DATA_FILE = "/Users/grant/cs/manim/nn/pretrained_weights_and_biases_on_zero"
# DEFAULT_LAYER_SIZES = [28**2, 80, 10]
DEFAULT_LAYER_SIZES = [28**2, 16, 16, 10]

try:
    xrange          # Python 2
except NameError:
    xrange = range  # Python 3


class Network(object):
    def __init__(self, sizes, non_linearity = "sigmoid"):
        """The list ``sizes`` contains the number of neurons in the
        respective layers of the network.  For example, if the list
        was [2, 3, 1] then it would be a three-layer network, with the
        first layer containing 2 neurons, the second layer 3 neurons,
        and the third layer 1 neuron.  The biases and weights for the
        network are initialized randomly, using a Gaussian
        distribution with mean 0, and variance 1.  Note that the first
        layer is assumed to be an input layer, and by convention we
        won't set any biases for those neurons, since biases are only
        ever used in computing the outputs from later layers."""
        self.num_layers = len(sizes)
        self.sizes = sizes
        self.biases = [np.random.randn(y, 1) for y in sizes[1:]]
        self.weights = [np.random.randn(y, x)
                        for x, y in zip(sizes[:-1], sizes[1:])]
        if non_linearity == "sigmoid":
            self.non_linearity = sigmoid
            self.d_non_linearity = sigmoid_prime
        elif non_linearity == "ReLU":
            self.non_linearity = ReLU
            self.d_non_linearity = ReLU_prime
        else:
            raise Exception("Invalid non_linearity")

    def feedforward(self, a):
        """Return the output of the network if ``a`` is input."""
        for b, w in zip(self.biases, self.weights):
            a = self.non_linearity(np.dot(w, a)+b)
        return a

    def get_activation_of_all_layers(self, input_a, n_layers = None):
        if n_layers is None:
            n_layers = self.num_layers
        activations = [input_a.reshape((input_a.size, 1))]
        for bias, weight in zip(self.biases, self.weights)[:n_layers]:
            last_a = activations[-1]
            new_a = self.non_linearity(np.dot(weight, last_a) + bias)
            new_a = new_a.reshape((new_a.size, 1))
            activations.append(new_a)
        return activations

    def SGD(self, training_data, epochs, mini_batch_size, eta,
            test_data=None):
        """Train the neural network using mini-batch stochastic
        gradient descent.  The ``training_data`` is a list of tuples
        ``(x, y)`` representing the training inputs and the desired
        outputs.  The other non-optional parameters are
        self-explanatory.  If ``test_data`` is provided then the
        network will be evaluated against the test data after each
        epoch, and partial progress printed out.  This is useful for
        tracking progress, but slows things down substantially."""
        if test_data: n_test = len(test_data)
        n = len(training_data)
        for j in range(epochs):
            random.shuffle(training_data)
            mini_batches = [
                training_data[k:k+mini_batch_size]
                for k in range(0, n, mini_batch_size)]
            for mini_batch in mini_batches:
                self.update_mini_batch(mini_batch, eta)
            if test_data:
                print("Epoch {0}: {1} / {2}".format(
                    j, self.evaluate(test_data), n_test))
            else:
                print("Epoch {0} complete".format(j))

    def update_mini_batch(self, mini_batch, eta):
        """Update the network's weights and biases by applying
        gradient descent using backpropagation to a single mini batch.
        The ``mini_batch`` is a list of tuples ``(x, y)``, and ``eta``
        is the learning rate."""
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        for x, y in mini_batch:
            delta_nabla_b, delta_nabla_w = self.backprop(x, y)
            nabla_b = [nb+dnb for nb, dnb in zip(nabla_b, delta_nabla_b)]
            nabla_w = [nw+dnw for nw, dnw in zip(nabla_w, delta_nabla_w)]
        self.weights = [w-(eta/len(mini_batch))*nw
                        for w, nw in zip(self.weights, nabla_w)]
        self.biases = [b-(eta/len(mini_batch))*nb
                       for b, nb in zip(self.biases, nabla_b)]

    def backprop(self, x, y):
        """Return a tuple ``(nabla_b, nabla_w)`` representing the
        gradient for the cost function C_x.  ``nabla_b`` and
        ``nabla_w`` are layer-by-layer lists of numpy arrays, similar
        to ``self.biases`` and ``self.weights``."""
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        # feedforward
        activation = x
        activations = [x] # list to store all the activations, layer by layer
        zs = [] # list to store all the z vectors, layer by layer
        for b, w in zip(self.biases, self.weights):
            z = np.dot(w, activation)+b
            zs.append(z)
            activation = self.non_linearity(z)
            activations.append(activation)
        # backward pass
        delta = self.cost_derivative(activations[-1], y) * \
            self.d_non_linearity(zs[-1])
        nabla_b[-1] = delta
        nabla_w[-1] = np.dot(delta, activations[-2].transpose())
        # Note that the variable l in the loop below is used a little
        # differently to the notation in Chapter 2 of the book.  Here,
        # l = 1 means the last layer of neurons, l = 2 is the
        # second-last layer, and so on.  It's a renumbering of the
        # scheme in the book, used here to take advantage of the fact
        # that Python can use negative indices in lists.
        for l in range(2, self.num_layers):
            z = zs[-l]
            sp = self.d_non_linearity(z)
            delta = np.dot(self.weights[-l+1].transpose(), delta) * sp
            nabla_b[-l] = delta
            nabla_w[-l] = np.dot(delta, activations[-l-1].transpose())
        return (nabla_b, nabla_w)

    def evaluate(self, test_data):
        """Return the number of test inputs for which the neural
        network outputs the correct result. Note that the neural
        network's output is assumed to be the index of whichever
        neuron in the final layer has the highest activation."""
        test_results = [(np.argmax(self.feedforward(x)), y)
                        for (x, y) in test_data]
        return sum(int(x == y) for (x, y) in test_results)

    def cost_derivative(self, output_activations, y):
        """Return the vector of partial derivatives \\partial C_x /
        \\partial a for the output activations."""
        return (output_activations-y)

#### Miscellaneous functions
def sigmoid(z):
    """The sigmoid function."""
    return 1.0/(1.0+np.exp(-z))

def sigmoid_prime(z):
    """Derivative of the sigmoid function."""
    return sigmoid(z)*(1-sigmoid(z))

def sigmoid_inverse(z):
    # z = 0.998*z + 0.001
    assert(np.max(z) <= 1.0 and np.min(z) >= 0.0)
    z = 0.998*z + 0.001
    return np.log(np.true_divide(
        1.0, (np.true_divide(1.0, z) - 1)
    ))

def ReLU(z):
    result = np.array(z)
    result[result < 0] = 0
    return result

def ReLU_prime(z):
    return (np.array(z) > 0).astype('int')

def get_pretrained_network():
    data_file = open(PRETRAINED_DATA_FILE, 'rb')
    weights, biases = pickle.load(data_file, encoding='latin1')
    sizes = [w.shape[1] for w in weights]
    sizes.append(weights[-1].shape[0])
    network = Network(sizes)
    network.weights = weights
    network.biases = biases
    return network

def save_pretrained_network(epochs = 30, mini_batch_size = 10, eta = 3.0):
    network = Network(sizes = DEFAULT_LAYER_SIZES)
    training_data, validation_data, test_data = load_data_wrapper()
    network.SGD(training_data, epochs, mini_batch_size, eta)
    weights_and_biases = (network.weights, network.biases)
    data_file = open(PRETRAINED_DATA_FILE, mode = 'w')
    pickle.dump(weights_and_biases, data_file)
    data_file.close()

def test_network():
    network = get_pretrained_network()
    training_data, validation_data, test_data = load_data_wrapper()
    n_right, n_wrong = 0, 0
    for test_in, test_out in test_data:
        if np.argmax(network.feedforward(test_in)) == test_out:
            n_right += 1
        else:
            n_wrong += 1
    print((n_right, n_wrong, float(n_right)/(n_right + n_wrong)))

def layer_to_image_array(layer):
    w = int(np.ceil(np.sqrt(len(layer))))
    if len(layer) < w**2:
        layer = np.append(layer, np.zeros(w**2 - len(layer)))
    layer = layer.reshape((w, w))
    # return Image.fromarray((255*layer).astype('uint8'))
    return (255*layer).astype('int')

def maximizing_input(network, layer_index, layer_vect, n_steps = 100, seed_guess = None):
    pre_sig_layer_vect = sigmoid_inverse(layer_vect)
    weights, biases = network.weights, network.biases
    # guess = np.random.random(weights[0].shape[1])
    if seed_guess is not None:
        pre_sig_guess = sigmoid_inverse(seed_guess.flatten())
    else:
        pre_sig_guess = np.random.randn(weights[0].shape[1])
    norms = []
    for step in range(n_steps):
        activations = network.get_activation_of_all_layers(
            sigmoid(pre_sig_guess), layer_index
        )
        jacobian = np.diag(sigmoid_prime(pre_sig_guess).flatten())
        for W, a, b in zip(weights, activations, biases):
            jacobian = np.dot(W, jacobian)
            a = a.reshape((a.size, 1))
            sp = sigmoid_prime(np.dot(W, a) + b)
            jacobian = np.dot(np.diag(sp.flatten()), jacobian)
        gradient = np.dot(
            np.array(layer_vect).reshape((1, len(layer_vect))),
            jacobian
        ).flatten()
        norm = get_norm(gradient)
        if norm == 0:
            break
        norms.append(norm)
        old_pre_sig_guess = np.array(pre_sig_guess)
        pre_sig_guess += 0.1*gradient
        print(get_norm(old_pre_sig_guess - pre_sig_guess))
    print("")
    return sigmoid(pre_sig_guess)

def save_organized_images(n_images_per_number = 10):
    training_data, validation_data, test_data = load_data_wrapper()
    image_map = dict([(k, []) for k in range(10)])
    for im, output_arr in training_data:
        if min(list(map(len, list(image_map.values())))) >= n_images_per_number:
            break
        value = int(np.argmax(output_arr))
        if len(image_map[value]) >= n_images_per_number:
            continue
        image_map[value].append(im)
    data_file = open(IMAGE_MAP_DATA_FILE, mode = 'wb')
    pickle.dump(image_map, data_file)
    data_file.close()

def get_organized_images():
    data_file = open(IMAGE_MAP_DATA_FILE, mode = 'r')
    image_map = pickle.load(data_file, encoding='latin1')
    data_file.close()
    return image_map

# def maximizing_input(network, layer_index, layer_vect):
#     if layer_index == 0:
#         return layer_vect
#     W = network.weights[layer_index-1]
#     n = max(W.shape)
#     W_square = np.identity(n)
#     W_square[:W.shape[0], :W.shape[1]] = W
#     zeros = np.zeros((n - len(layer_vect), 1))
#     vect = layer_vect.reshape((layer_vect.shape[0], 1))
#     vect = np.append(vect, zeros, axis = 0)
#     b = np.append(network.biases[layer_index-1], zeros, axis = 0)
#     prev_vect = np.dot(
#         np.linalg.inv(W_square),
#         (sigmoid_inverse(vect) - b)
#     )
#     # print layer_vect, sigmoid(np.dot(W, prev_vect)+b)
#     print W.shape
#     prev_vect = prev_vect[:W.shape[1]]
#     prev_vect /= np.max(np.abs(prev_vect))
#     # prev_vect /= 1.1
#     return maximizing_input(network, layer_index - 1, prev_vect)
