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
    def __init__(self, coords, basis=[[1,0],[0,1]], dim = 2):
        self.coords = coords
        self.basis = basis
        self.dim = dim
        return self

    def change_of_basis(self, matrix):
        """ changes the basis that self is expressed in,
            using the given change of base matrix.
        """
        self.coords = np.dot(matrix,self.coords) #updates self.coords to new basis #(might have to transpose self.coords)
        inverse = np.linalg.inv(matrix) #inverts the matrix

        new_basis = np.array(self.dim) 
        for i in range(self.dim):
            for j in range(self.dim):
                new_basis[i][j] = inverse[i][j]*self.basis[j] #reconstructs new basis from given matrix and old basis
        self.basis = new_basis #resets basis
        
        return self
    
    def linear_decomposition(self):
        """ returns a list of basis vectors
            such that when the list is added up,
            we get the vector
        """
        vector_list = []
        for i in range(self.dim): #loop over dimensions
            for j in range(abs(np.floor(self.coords[i]))): #whole basis vectors
                vector_list += self.basis[i]
            leftover = self.coords[i] - np.floor(self.coords[i]) #leftover, if coordinates are noninteger
            if leftover != 0: #check if nonzero leftover
                leftover_vec = []
                for k in range(self.dim):
                    leftover_vec += [leftover*self.coords[k]] #create scaled leftover vector
                vector_list += leftover_vec #add leftover vector to overall vector list
        return vector_list 