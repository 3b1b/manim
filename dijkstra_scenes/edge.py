from big_ol_pile_of_manim_imports import *
from collections import OrderedDict as OrderedDict
import numpy.linalg as la
from dijkstra_scenes.node import Node as Node

class Edge(Group):
    def __init__(self, start_node, end_node, **kwargs):
        self.key = (start_node.key, end_node.key)
        self.assert_edge_primitive(self.key)
        # create mobject
        self.start_node = start_node
        self.end_node = end_node
        normal_vec = end_node.get_center() - start_node.get_center()
        normal_vec /= la.norm(normal_vec)
        self.line = Line(
            start_node.get_center() + normal_vec * start_node.mobject.radius,
            end_node.get_center() - normal_vec * end_node.mobject.radius,
            stroke_width=kwargs["stroke_width"],
        )
        # TODO: find a way to add the weight without creating bad
        # non-weighted -> weighted Transforms
        # save labels
        saved_labels = []
        if "labels" in kwargs and \
                kwargs["labels"] and \
                self.key in kwargs["labels"]:
            saved_labels.extend(kwargs["labels"][self.key])
            del kwargs["labels"]
        if "weight" in kwargs:
            saved_labels.append(("weight", kwargs["weight"]))
            del kwargs["weight"]
        # initialize and set labels
        Group.__init__(self, self.line, **kwargs)
        self.labels = OrderedDict()
        self.set_labels(*saved_labels, animate=False)

    @staticmethod
    def assert_edge_primitive(pair):
        try:
            assert type(pair) == tuple and len(pair) == 2
            Node.assert_node_primitive(pair[0])
            Node.assert_node_primitive(pair[1])
        except: import ipdb; ipdb.set_trace()

    def __str__(self):
        return "Edge(start=({}, {}), end=({}, {}))".format(
            *np.append(
                self.start_node.get_center()[:2],
                self.end_node.get_center()[:2]))
    __repr__ = __str__

    def opposite(self, point):
        Node.assert_node_primitive(point)
        if np.allclose(self.start_node.key, point):
            return self.end_node.key
        elif np.allclose(self.end_node.key, point):
            return self.start_node.key
        else:
            raise Exception("node isn't part of line")

    def set_label(self, name, label, animate=True, **kwargs):
        kwargs["animate"] = animate
        return self.set_labels((name, label), **kwargs)

    def set_labels(self, *labels, **kwargs):
        if not labels:
            return

        # copy
        new_labels = OrderedDict()
        for name in self.labels.keys():
            new_labels[name] = self.labels[name].copy()
        for name, label in labels:
            new_labels[name] = label

        # move
        if len(new_labels) != len(self.labels):
            # rearrange labels
            start, end = self.line.get_start_and_end()
            vec = end - start
            vec /= la.norm(vec)
            vec = rotate_vector(vec, np.pi / 2)
            last_mobject = None
            for label in new_labels.values():
                if last_mobject:
                    label.next_to(last_mobject, RIGHT, buff=SMALL_BUFF)
                else:
                    label.next_to(self.line.get_midpoint(), vec, buff=SMALL_BUFF)
                last_mobject = label
        else:
            assert(new_labels.keys() == self.labels.keys())
            for name in new_labels:
                new_labels[name].move_to(self.labels[name].get_center())

        # scale TODO
        for label in new_labels.values():
            label.scale(self.scale)

        # animate / create
        anims = []
        for name in new_labels.keys():
            if "animate" not in kwargs or kwargs["animate"]:
                if name in self.labels:
                    anims.extend([ReplacementTransform(self.labels[name],
                                                       new_labels[name],
                                                       parent=self)])
                else:
                    anims.extend([ShowCreation(new_labels[name])])
                    self.add(new_labels[name])
            else:
                if name not in self.labels:
                    self.add(new_labels[name])
        self.labels = new_labels
        return anims

    def get_label(self):
        return self.label

    def get_weight(self):
        return self.labels["weight"] if "weight" in self.labels else None

    def set_weight(self, weight):
        return self.set_label("weight", Integer(weight))
