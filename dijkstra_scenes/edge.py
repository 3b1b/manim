from __future__ import print_function
from constants import *
from mobject.component import Component
from dijkstra_scenes.node import Node
from mobject.geometry import Arrow
from mobject.geometry import Line
from mobject.numbers import Integer
from animation.creation import ShowCreation
from animation.transform import ReplacementTransform
from utils.space_ops import rotate_vector
from collections import OrderedDict
import copy
import ipdb
import numpy
import sys

class Edge(Component):
    def __init__(self, start_node, end_node, attrs=None, **kwargs):
        self.start_node = start_node
        self.end_node = end_node
        Component.__init__(self, start_node, end_node, attrs=attrs, **kwargs)

    def __str__(self):
        return "Edge(start=({}, {}), end=({}, {}))".format(
            *numpy.append(
                self.start_node.mobject.get_center()[:2],
                self.end_node.mobject.get_center()[:2]))
    __repr__ = __str__

    @staticmethod
    def assert_primitive(pair):
        try:
            assert type(pair) == tuple and len(pair) == 2
            Node.assert_primitive(pair[0])
            Node.assert_primitive(pair[1])
        except AssertionError:
            print("Invalid Edge primitive: {}".format(pair), file=sys.stderr)
            ipdb.set_trace(context=7)

    def make_key(self, start_node, end_node):
        return (start_node.key, end_node.key)

    def opposite(self, point):
        Node.assert_primitive(point)
        if numpy.allclose(self.start_node.key, point):
            return self.end_node.key
        elif numpy.allclose(self.end_node.key, point):
            return self.start_node.key
        else:
            raise Exception("node isn't part of line")

    def get_label_scale_factor(self, label, num_labels):
        if label.get_height() > Integer(7).get_height():
            return self.scale_factor * \
                Integer(7).get_height() / label.get_height()
        else:
            return self.mobject.scale_factor

    def set_label(self, name, label, animate=True, **kwargs):
        kwargs["animate"] = animate
        d = copy.deepcopy(self.labels)
        d[name] = label
        return self.set_labels(d, **kwargs)

    def set_labels(self, new_labels, **kwargs):
        assert(type(new_labels) == OrderedDict)
        # make sure labels are different
        for old_label in self.labels.values():
            for new_label in new_labels.values():
                assert(id(old_label) != id(new_label))

        anims = []
        # delete
        for key, val in new_labels.items():
            if val is None:
                anims.append(Uncreate(self.labels[key]))
                self.remove(self.labels[key])
                del new_labels[key]
                del self.labels[key]

        # scale
        for label in new_labels.values():
            if type(label) == Arrow: continue # TODO
            scale_factor = self.get_label_scale_factor(label, len(new_labels))
            label.scale(scale_factor)

        # move
        start, end = self.mobject.get_start_and_end()
        vec = start - end
        vec = vec / numpy.linalg.norm(vec)
        vec = rotate_vector(vec, numpy.pi/2)
        buff = MED_SMALL_BUFF if self.mobject.curved else SMALL_BUFF
        last_mobject = None
        old_label_copies = OrderedDict()
        for name, label in self.labels.items():
            if name in new_labels:
                if last_mobject:
                    new_labels[name].next_to(last_mobject, RIGHT, buff=buff)
                else:
                    new_labels[name].next_to(self.mobject.get_midpoint(), vec, buff=buff)
            else:
                if last_mobject:
                    old_label_copies[name] = label.copy().next_to(last_mobject, RIGHT, buff=buff)
                else:
                    old_label_copies[name] = label.copy().next_to(self.mobject.get_midpoint(), vec, buff=buff)
            last_mobject = label

        for name, label in new_labels.items():
            if name in self.labels:
                pass
            else:
                if last_mobject:
                    label.next_to(last_mobject, RIGHT, buff=buff)
                else:
                    label.next_to(self.mobject.get_midpoint(), vec, buff=buff)
                last_mobject = label
        for key in old_label_copies:
            if key not in new_labels:
                new_labels[key] = old_label_copies[key]

        # animate / create
        if "animate" not in kwargs or kwargs["animate"]:
            for name in new_labels.keys():
                if name in self.labels:
                    anims.extend([ReplacementTransform(self.labels[name],
                                                       new_labels[name],
                                                       parent=self)])
                else:
                    anims.extend([ShowCreation(new_labels[name])])
                    self.add(new_labels[name])
            for name in self.labels:
                if name not in new_labels:
                    anims.extend([Uncreate(self.labels[name])])
                    self.remove(self.labels[name])
        else:
            for name in new_labels.keys():
                if name not in self.labels:
                    self.add(new_labels[name])
                else:
                    self.add(new_labels[name])
                    self.remove(self.labels[name])
            for name in self.labels:
                if name not in new_labels:
                    self.remove(self.labels[name])
        self.labels = new_labels
        return anims

    def get_weight(self):
        return self.labels["weight"] if "weight" in self.labels else None

    def update(self, dic=None, animate=True):
        # empty update for when start or end node changes radius
        if dic is None:
            dic = OrderedDict()

        # set mobject parameters
        if "stroke_width" not in dic:
            if hasattr(self, "mobject"):
                dic["stroke_width"] = self.mobject.stroke_width
            else:
                print("Attempted to initialize Edge without stroke_width")
                import ipdb; ipdb.set_trace(context=7)

        if "rectangular_stem_width" not in dic:
            if hasattr(self, "mobject"):
                dic["rectangular_stem_width"] = self.mobject.rectangular_stem_width
            else:
                print("Attempted to initialize Edge without rectangular_stem_width")
                import ipdb; ipdb.set_trace(context=7)

        if "scale_factor" not in dic:
            if hasattr(self, "mobject"):
                dic["scale_factor"] = self.mobject.scale_factor
            else:
                print("Attempted to initialize Edge without scale_factor")
                import ipdb; ipdb.set_trace(context=7)

        if "color" not in dic:
            if hasattr(self, "mobject"):
                dic["color"] = self.mobject.color

        if "directed" not in dic:
            if hasattr(self, "mobject") and self.mobject.directed:
                dic["directed"] = True
            else:
                dic["directed"] = False

        if "curved" not in dic:
            if hasattr(self, "mobject") and self.mobject.curved:
                dic["curved"] = True
            else:
                dic["curved"] = False

        ret = []
        normalized_vec = self.end_node.mobject.get_center() - \
            self.start_node.mobject.get_center()
        normalized_vec = normalized_vec / numpy.linalg.norm(normalized_vec)
        normal_vec = rotate_vector(normalized_vec, numpy.pi/2)
        if dic["directed"]:
            mob = Arrow(
                self.start_node.mobject.get_center() + \
                    normalized_vec * (self.start_node.mobject.radius - 0.0),
                self.end_node.mobject.get_center() - \
                    normalized_vec * (self.end_node.mobject.radius - 0.0),
                buff=0,
                **dic
            )
        else:
            mob = Line(
                self.start_node.mobject.get_center() + \
                    normalized_vec * self.start_node.mobject.radius,
                self.end_node.mobject.get_center() - \
                    normalized_vec * self.end_node.mobject.radius,
                **dic
            )

        if dic["curved"]:
            start, end = mob.get_start_and_end()
            midpoint = (start + end) / 2
            def f(x):
                return x - 0.1 * normal_vec * (numpy.linalg.norm(start - midpoint) - numpy.linalg.norm(x - midpoint))
            mob.shift(-0.05 * normal_vec).apply_function(f)
        new_mob = mob

        if animate:
            ret.extend([ReplacementTransform(self.mobject, new_mob, parent=self)])
        else:
            if hasattr(self, "mobject"):
                self.remove(self.mobject)
            self.add(new_mob)
        self.mobject = new_mob

        # update labels
        labels = OrderedDict()
        for key in dic.keys():
            if key == "weight":
                labels["weight"] = dic["weight"]
        if not hasattr(self, "labels"):
            self.labels = OrderedDict()
        if animate:
            ret.extend(self.set_labels(labels))
        else:
            self.set_labels(labels, animate=False)

        return ret
