from big_ol_pile_of_manim_imports import *
from collections import OrderedDict as OrderedDict
import numpy.linalg as la
from dijkstra_scenes.node import Node as Node

class Edge(Component):
    def __init__(self, start_node, end_node, labels=None,
            scale_factor=1, edge_color=None, **kwargs):
        if labels is not None:
            for label in labels:
                if len(label) == 3 and "stroke_width" in label[2]:
                    kwargs["stroke_width"] = label[2]["stroke_width"]
        if edge_color is not None:
            kwargs["color"] = edge_color
        Component.__init__(self, start_node, end_node,
                labels=labels, scale_factor=scale_factor, **kwargs)
        self.start_node = start_node
        self.end_node = end_node

    @staticmethod
    def assert_primitive(pair):
        try:
            assert type(pair) == tuple and len(pair) == 2
            Node.assert_primitive(pair[0])
            Node.assert_primitive(pair[1])
        except: import ipdb; ipdb.set_trace(context=7)

    def make_key(self, start_node, end_node):
        return (start_node.key, end_node.key)

    def create_mobject(self, start_node, end_node, labels=None, **kwargs):
        normalized_vec = end_node.get_center() - start_node.get_center()
        normalized_vec /= la.norm(normalized_vec)
        return Line(
            start_node.get_center() + normalized_vec * start_node.mobject.radius,
            end_node.get_center() - normalized_vec * end_node.mobject.radius,
            **kwargs
        )

    def __str__(self):
        return "Edge(start=({}, {}), end=({}, {}))".format(
            *np.append(
                self.start_node.get_center()[:2],
                self.end_node.get_center()[:2]))
    __repr__ = __str__

    def opposite(self, point):
        Node.assert_primitive(point)
        if np.allclose(self.start_node.key, point):
            return self.end_node.key
        elif np.allclose(self.end_node.key, point):
            return self.start_node.key
        else:
            raise Exception("node isn't part of line")

    def set_labels(self, *labels, **kwargs):
        if not labels:
            return

        # copy
        new_labels = OrderedDict()
        for name in self.labels.keys():
            new_labels[name] = self.labels[name].copy()
        for label in labels:
            name, mobject = label[:2]
            new_labels[name] = mobject

        # move
        if len(new_labels) != len(self.labels):
            # rearrange labels
            start, end = self.mobject.get_start_and_end()
            vec = end - start
            vec /= la.norm(vec)
            vec = rotate_vector(vec, np.pi / 2)
            last_mobject = None
            for label in new_labels.values():
                if last_mobject:
                    label.next_to(last_mobject, RIGHT, buff=SMALL_BUFF)
                else:
                    label.next_to(self.mobject.get_midpoint(), vec, buff=SMALL_BUFF)
                last_mobject = label
        else:
            assert(new_labels.keys() == self.labels.keys())
            for name in new_labels:
                new_labels[name].move_to(self.labels[name].get_center())

        # scale TODO
        for label in new_labels.values():
            label.scale(self.scale_factor)

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

    def get_weight(self):
        return self.labels["weight"] if "weight" in self.labels else None

    def set_stroke_width(self, stroke_width, color=None):
        normalized_vec = self.end_node.get_center() - self.start_node.get_center()
        normalized_vec /= la.norm(normalized_vec)
        new_line = Line(
            self.start_node.get_center() + normalized_vec * self.start_node.mobject.radius,
            self.end_node.get_center() - normalized_vec * self.end_node.mobject.radius,
            stroke_width=stroke_width,
        ).set_color(color)
        ret = ReplacementTransform(
            self.mobject,
            new_line,
            parent=self,
        )
        self.mobject = new_line
        self.stroke_width = stroke_width
        return ret

    def update_endpoints(self, stroke_width=None, color=None):
        if stroke_width is not None:
            self.stroke_width = stroke_width
        normalized_vec = self.end_node.get_center() - self.start_node.get_center()
        normalized_vec /= la.norm(normalized_vec)
        new_line = Line(
            self.start_node.get_center() + normalized_vec * self.start_node.mobject.radius,
            self.end_node.get_center() - normalized_vec * self.end_node.mobject.radius,
            stroke_width=self.stroke_width,
        ).set_color(color)
        ret = ReplacementTransform(
            self.mobject,
            new_line,
            parent=self,
        )
        self.mobject = new_line
        return ret

    def change_color(self, color):
        new_line = self.mobject.copy().set_color(color)
        ret = ReplacementTransform(
            self.mobject,
            new_line,
            parent=self,
        )
        self.mobject = new_line
        return ret

