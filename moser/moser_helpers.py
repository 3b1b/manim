import numpy as np
import operator as op
import itertools as it

from constants import *
from image_mobject import *

def choose(n, r):
    if n < r: return 0
    if r == 0: return 1
    denom = reduce(op.mul, xrange(1, r+1), 1)
    numer = reduce(op.mul, xrange(n, n-r, -1), 1)
    return numer//denom

def moser_function(n):
    return choose(n, 4) + choose(n, 2) + 1

def intersection(line1, line2):
    """
    A "line" should come in the form [(x0, y0), (x1, y1)] for two
    points it runs through
    """
    p0, p1, p2, p3 = map(
        lambda tup : np.array(tup[:2]),
        [line1[0], line1[1], line2[0], line2[1]]
    )
    p1, p2, p3 = map(lambda x : x - p0, [p1, p2, p3])
    transform = np.zeros((2, 2))
    transform[:,0], transform[:,1] = p1, p2
    if np.linalg.det(transform) == 0: return
    inv = np.linalg.inv(transform)
    new_p3 = np.dot(inv, p3.reshape((2, 1)))
    #Where does line connecting (0, 1) to new_p3 hit x axis
    x_intercept = new_p3[0] / (1 - new_p3[1]) 
    result = np.dot(transform, [[x_intercept], [0]])
    result = result.reshape((2,)) + p0
    return result



