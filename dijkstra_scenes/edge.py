from big_ol_pile_of_manim_imports import *
import numpy.linalg as la

class Edge(Group):
    def __init__(self, start_node, end_node, **kwargs):
        self.start_node = start_node
        self.end_node = end_node
        self.labels = {}
        normal_vec = end_node.get_center() - start_node.get_center()
        normal_vec /= la.norm(normal_vec)
        self.line = Line(
            start_node.get_center() + normal_vec * start_node.mobject.radius,
            end_node.get_center() - normal_vec * end_node.mobject.radius,
            stroke_width=kwargs["stroke_width"],
        )
        # TODO: find a way to add the weight without creating bad
        # non-weighted -> weighted Transforms
        if "weight" in kwargs:
            weight = kwargs["weight"]
            start, end = self.line.get_start_and_end()
            vec = end - start
            vec /= la.norm(vec)
            vec = rotate_vector(vec, np.pi / 2)
            self.weight = weight.next_to(self.line.get_midpoint(),
                                         vec, buff=SMALL_BUFF)
            Group.__init__(self, self.line, self.weight, **kwargs)
        else:
            self.weight = None
            Group.__init__(self, self.line, **kwargs)

    def __str__(self):
        return "Edge(start=({}, {}), end=({}, {}))".format(
            *np.append(
                self.start_node.get_center()[:2],
                self.end_node.get_center()[:2]))
    __repr__ = __str__

    def opposite(self, location):
        if np.allclose(self.start_node.get_center(), location):
            return tuple(np.round(self.end_node.mobject.get_center(), 2))
        else:
            return tuple(np.round(self.start_node.mobject.get_center(), 2))

    def set_label(self, label):
        self.label = label

    def get_label(self):
        return self.label

    def get_weight(self):
        return self.weight

    def set_weight(self, weight):
        start, end = self.line.get_start_and_end()
        vec = end - start
        vec /= la.norm(vec)
        vec = rotate_vector(vec, np.pi / 2)
        self.weight = Integer(weight).next_to(self.line.get_midpoint(),
                                              vec, buff=SMALL_BUFF)
        self.add(self.weight)
        return ShowCreation(self.weight)

