from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import VMobject

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.number_line import *
from topics.numerals import *
from scene import Scene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *
from mobject.vectorized_mobject import *

from topics.matrix import *
from topics.vector_space_scene import *

import helpers
import math

class NiceVector(Vector):
    def __init__(self, coords, basis=np.array([[1,0],[0,1]]), dim = 2):
        self.coords = coords
        self.basis = basis
        self.dim = dim

    def change_of_basis(self, matrix):
        """ changes the basis that self is expressed in,
            using the given change of base matrix.
        """
        inverse = np.linalg.inv(matrix) #inverts the matrix
        self.coords = np.dot(inverse, self.coords) # find new coords as linear combo of new basis
        new_basis = np.zeros((self.dim, self.dim))
        for i in range(self.dim):
            for j in range(self.dim):
                new_basis[i][j] = np.dot(inverse[i][j],self.basis[j][i]) #reconstructs new basis from given matrix and old basis
        self.basis = new_basis #resets basis
        return self

    def linear_decomposition(self):
        """ returns a list of basis Vectors
            such that when the list is added up,
            we get the vector
        """
        vec_list = []
        for i in range(self.dim): #loop over dimensions
            for j in range(abs(np.floor(self.coords[i]))): #whole basis vectors
                if self.coords[i] < 0: #if coordinate is negative...
                    vec_list += -1*np.array(self.basis[i]) #switch the direction of the basis vector
                else:
                    vec_list += self.basis[i] #otherwise just use the normal one
            leftover = self.coords[i] - np.floor(self.coords[i]) #leftover, if coordinates are noninteger
            if leftover != 0: #check if nonzero leftover
                leftover_vec = []
                for k in range(self.dim):
                    leftover_vec += [leftover*np.array(self.basis[k])] #create scaled leftover vector
                    #we don't need to check its sign because
                vec_list += leftover_vec #add leftover vector to overall vector list

        vector_list = []
        for vec in vec_list:
            vector_list += [Vector([vec])] #convert vectors into Vector objects
        return vector_list

vect = NiceVector(np.array([6,2]))
vect.change_of_basis(np.array([[3,0],[0,2]]))
