from big_ol_pile_of_manim_imports import *
from collections import OrderedDict as OrderedDict
import numpy.linalg as la

class Edge(Group):
    def __init__(self, start_node, end_node, **kwargs):
        # create mobject
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
        # save labels
        saved_labels = []
        if "labels" in kwargs and \
                kwargs["labels"] and \
                (start_node, end_node) in kwargs["labels"]:
            saved_labels.extend(kwargs["labels"][(start_node, end_node)])
            del kwargs["labels"]
        if "weight" in kwargs:
            saved_labels.append(("weight", kwargs["weight"]))
            del kwargs["weight"]
        # initialize and set labels
        Group.__init__(self, self.line, **kwargs)
        self.labels = OrderedDict()
        self.set_labels(*saved_labels, animate=False)

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
                    last_mobject = label
                else:
                    label.next_to(self.line.get_midpoint(), vec, buff=SMALL_BUFF)
        else:
            assert(new_labels.keys() == self.labels.keys())
            for name in new_labels:
                new_labels[name].move_to(self.labels[name].get_center())

        # scale TODO

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
