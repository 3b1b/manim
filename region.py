import numpy as np
import itertools as it
from PIL import Image
import cv2
from copy import deepcopy

from constants import *
import displayer as disp

class Region(object):
    def __init__(self, 
                 condition = None, 
                 shape = None,
                 ):
        """
        Condition must be a function which takes in two real
        arrays (representing x and y values of space respectively)
        and return a boolean array.  This can essentially look like
        a function from R^2 to {True, False}, but & and | must be
        used in place of "and" and "or"
        """
        if shape == None:
            self.shape = (DEFAULT_HEIGHT, DEFAULT_WIDTH)
        else:
            self.shape = shape
        # self.condition = condition
        (h, w) = self.shape
        scalar = 2*SPACE_HEIGHT / h
        xs =  scalar*np.arange(-w/2, w/2)
        ys = -scalar*np.arange(-h/2, h/2)
        #TODO, do xs and ys really need to be saved in self?
        self.xs = np.dot(
            np.ones((h, 1)),
            xs.reshape((1, w))
        )
        self.ys = np.dot(
            ys.reshape(h, 1), 
            np.ones((1, w))
        )
        if condition:
            self.bool_grid = condition(self.xs, self.ys)
        else:
            self.bool_grid = np.ones(self.shape, dtype = 'bool')

    def show(self, color = None):
        Image.fromarray(disp.paint_region(self, color = color)).show()

    def _combine(self, region, op):
        assert region.shape == self.shape
        self.bool_grid = op(self.bool_grid, region.bool_grid)

    def union(self, region):
        self._combine(region, lambda bg1, bg2 : bg1 | bg2)
        return self

    def intersect(self, region):
        self._combine(region, lambda bg1, bg2 : bg1 & bg2)
        return self

    def complement(self):
        self.bool_grid = ~self.bool_grid
        return self

class HalfPlane(Region):
    def __init__(self, point_pair, upper_left = True, *args, **kwargs):
        """
        point_pair of the form [(x_0, y_0,...), (x_1, y_1,...)]

        Pf upper_left is True, the side of the region will be
        everything on the upper left side of the line through
        the point pair
        """
        if not upper_left:
            point_pair = list(point_pair)
            point_pair.reverse()
        (x0, y0), (x1, y1) = point_pair[0][:2], point_pair[1][:2]
        def condition(x, y):
            return (x1 - x0)*(y - y0) > (y1 - y0)*(x - x0)
        Region.__init__(self, condition, *args, **kwargs)

def region_from_line_boundary(*lines, **kwargs):
    reg = Region(**kwargs)
    for line in lines:
        reg.intersect(HalfPlane(line, **kwargs))
    return reg

def region_from_polygon_vertices(*vertices, **kwargs):
    points = list(vertices)
    points.append(points[0])
    return region_from_line_boundary(*zip(points, points[1:]), **kwargs)


def plane_partition(*lines, **kwargs):
    """
    A 'line' is a pair of points [(x0, y0,...), (x1, y1,...)]

    Returns the list of regions of the plane cut out by
    these lines
    """
    result = []
    half_planes = [HalfPlane(line, **kwargs) for line in lines]
    complements = [deepcopy(hp).complement() for hp in half_planes]
    num_lines = len(lines)
    for bool_list in it.product(*[[True, False]]*num_lines):
        reg = Region(**kwargs)
        for i in range(num_lines):
            if bool_list[i]:
                reg.intersect(half_planes[i])
            else:
                reg.intersect(complements[i])
        if reg.bool_grid.any():
            result.append(reg)
    return result

def plane_partition_from_points(*points, **kwargs):
    """
    Returns list of regions cut out by the complete graph
    with points from the argument as vertices.  

    Each point comes in the form (x, y)
    """
    lines = [[p1, p2] for (p1, p2) in it.combinations(points, 2)]
    return plane_partition(*lines, **kwargs)






