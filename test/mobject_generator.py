import random

import numpy

from manimlib.mobject.mobject import Mobject

class MobjectGenerator:
    def __init__(self,
            max_num_of_points = 8,
            lower_bound = -1000,
            upper_bound = 1000,
            max_depth = 4,
            max_num_of_children = 5):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.max_num_of_points = max_num_of_points
        self.max_depth = max_depth
        self.max_num_of_children = max_num_of_children
        self.r = random.Random()

    def next(self):
        obj = Mobject()
        self.__gen__(obj, self.max_depth - 1)
        return obj

    def __gen__(self, obj, depth):
        for _ in range(self.r.randint(1, self.max_num_of_points + 1)):
            obj.points = numpy.append(
                    obj.points,
                    [self.__gen_array_in_bounds__()],
                    axis=0)
        if depth <= 0 or not self.__should_make_child__(.75): return obj

        for _ in range(self.r.randint(0, self.max_num_of_children)):
            child = Mobject()
            obj.add(self.__gen__(child, depth - 1))
        return obj

    def __gen_array_in_bounds__(self):
        x = self.r.randrange(self.lower_bound, self.upper_bound)
        y = self.r.randrange(self.lower_bound, self.upper_bound)
        z = self.r.randrange(self.lower_bound, self.upper_bound)
        return numpy.array([x, y, z], dtype=numpy.float64)

    def __should_make_child__(self, chance):
        return (self.r.random() <= chance
                and self.r.random() <= chance)
