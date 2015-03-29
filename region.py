import numpy as np
import itertools as it
from PIL import Image
import cv2

from constants import *

class Region(object):
    def __init__(self, 
                 condition = lambda x, y : True, 
                 size = (DEFAULT_HEIGHT, DEFAULT_WIDTH)
                 ):
        """
        Condition must be a function which takes in two real
        arrays (representing x and y values of space respectively)
        and return a boolean array.  This can essentially look like
        a function from R^2 to {True, False}, but & and | must be
        used in place of "and" and "or"
        """
        self.size = (h, w) = size
        scalar = 2*SPACE_HEIGHT / h
        xs =  scalar*np.arange(-w/2, w/2)
        ys = -scalar*np.arange(-h/2, h/2)
        self.xs = np.dot(
            np.ones((h, 1)),
            xs.reshape((1, w))
        )
        self.ys = np.dot(
            ys.reshape(h, 1), 
            np.ones((1, w))
        )
        self.bool_grid = condition(self.xs, self.ys)

    def union(self, region):
        self.bool_grid |= region.bool_grid

    def intersection(self, region):
        self.bool_grid &= region.bool_grid

