from big_ol_pile_of_manim_imports import *
from collections import OrderedDict as OrderedDict
import numpy.linalg as la
import copy
from dijkstra_scenes.node import Node as Node

class Edge(Component):
    CONFIG = {
        "rectangular_stem_width": 0.03,
    }
    def __init__(self, start_node, end_node, directed=False, labels=None,
            scale_factor=1, edge_color=None, curved=False, **kwargs):
        if labels is not None:
            for label in labels:
                if len(label) == 3 and "stroke_width" in label[2]:
                    kwargs["stroke_width"] = label[2]["stroke_width"]
        if edge_color is not None:
            kwargs["color"] = edge_color
        Component.__init__(self, start_node, end_node, directed=directed,
                labels=labels, scale_factor=scale_factor, curved=curved,
                **kwargs)
        self.start_node = start_node
        self.end_node = end_node
        self.is_parent = False

    @staticmethod
    def assert_primitive(pair):
        try:
            assert type(pair) == tuple and len(pair) == 2
            Node.assert_primitive(pair[0])
            Node.assert_primitive(pair[1])
        except: import ipdb; ipdb.set_trace(context=7)

    def make_key(self, start_node, end_node):
        return (start_node.key, end_node.key)

    def create_mobject(self, start_node, end_node, directed=False,
            labels=None, curved=False, **kwargs):
        normalized_vec = end_node.get_center() - start_node.get_center()
        normalized_vec = normalized_vec / la.norm(normalized_vec)
        normal_vec = rotate_vector(normalized_vec, np.pi/2)
        if directed:
            mob = Arrow(
                start_node.get_center() + normalized_vec * (start_node.mobject.radius - 0.0),
                end_node.get_center() - normalized_vec * (end_node.mobject.radius - 0.0),
                buff=0,
                **kwargs
            )
        else:
            mob = Line(
                start_node.get_center() + normalized_vec * start_node.mobject.radius,
                end_node.get_center() - normalized_vec * end_node.mobject.radius,
                **kwargs
            )

        if curved:
            start, end = mob.get_start_and_end()
            midpoint = (start + end) / 2
            def f(x):
                return x - 0.1 * normal_vec * (la.norm(start - midpoint) - la.norm(x - midpoint))
            mob.shift(-0.05 * normal_vec).apply_function(f)
        return mob

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
        if len(new_labels) != len(self.labels) or kwargs.get("rearrange", False) == True:
            start, end = self.mobject.get_start_and_end()
            vec = start - end
            vec = vec / la.norm(vec)
            vec = rotate_vector(vec, np.pi/2)
            last_mobject = None
            buff = MED_SMALL_BUFF if self.curved else SMALL_BUFF
            for label in new_labels.values():
                if last_mobject:
                    label.next_to(last_mobject, RIGHT, buff=buff)
                else:
                    label.next_to((start + end) / 2, vec, buff=buff)
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

    def set_stroke_width(self, stroke_width=2, rectangular_stem_width=0.03, color=None):
        normalized_vec = self.end_node.get_center() - self.start_node.get_center()
        normalized_vec /= la.norm(normalized_vec)
        new_line = self.create_mobject(self.start_node, self.end_node,
                directed=self.directed, curved=self.curved, color=color,
                stroke_width=stroke_width,
                rectangular_stem_width=rectangular_stem_width, scale_factor=1)
        ret = ReplacementTransform(
            self.mobject,
            new_line,
            parent=self,
        )
        self.mobject = new_line
        self.stroke_width = stroke_width
        return ret

    def update_endpoints(self, stroke_width=2, rectangular_stem_width=0.03,
            color=None, curve=False):
        if stroke_width is not None:
            self.stroke_width = stroke_width
        normalized_vec = self.end_node.get_center() - self.start_node.get_center()
        normalized_vec /= la.norm(normalized_vec)
        new_line = self.create_mobject(self.start_node, self.end_node,
                directed=self.directed, curved=curve, stroke_width=stroke_width,
                rectangular_stem_width=rectangular_stem_width, color=color)
        ret = [ReplacementTransform(
            self.mobject,
            new_line,
            parent=self,
        )]
        self.mobject = new_line
        saved_labels = copy.deepcopy(self.labels)
        label_anims = self.set_labels(*saved_labels.items(), rearrange=True, animate=True)
        if label_anims:
            ret.extend(label_anims)
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

