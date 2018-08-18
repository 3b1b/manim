from __future__ import print_function
from __future__ import absolute_import
from mobject.component import Component
from mobject.geometry import Circle
from mobject.geometry import Arrow
from mobject.numbers import Integer
from animation.creation import ShowCreation
from animation.creation import Uncreate
from animation.transform import ReplacementTransform
from utils.space_ops import rotate_vector
from collections import OrderedDict
import constants
import copy
import numpy
import sys

LABELED_NODE_FACTOR = 7
UNLABELED_NODE_RADIUS = 0.1
LABELED_NODE_RADIUS = LABELED_NODE_FACTOR * UNLABELED_NODE_RADIUS
HEIGHT_RELATIVE_TO_NODE = [0, 0.23, 0.23, 0.23]


class Node(Component):
    def __init__(self, point, attrs=None, **kwargs):
        Component.__init__(self, point, attrs=attrs, **kwargs)

    def __str__(self):
        return "Node(center=({}, {}))".format(*self.mobject.get_center()[:2])
    __repr__ = __str__

    @staticmethod
    def assert_primitive(point):
        try:
            assert type(point) == numpy.ndarray or type(point) == tuple
            assert len(point) == 3
        except AssertionError:
            print("Invalid Node primitive: {}".format(point), file=sys.stderr)
            import ipdb; ipdb.set_trace(context=7)

    def make_key(self, point):
        return point

    def update_attrs(self, dic, animate=True):
        if dic is None:
            return
        """
        the labels dict is needed for the radius calculation later, but the
        mobject (specifically mobject.get_center()) is needed before the labels
        can be placed
        """
        labels = OrderedDict()
        for key in list(dic.keys()):
            if key == "variable":
                labels["variable"] = dic["variable"]
                del dic["variable"]
            elif key == "dist":
                labels["dist"] = dic["dist"]
                del dic["dist"]
            elif key == "parent_pointer":
                labels["parent_pointer"] = dic["parent_pointer"]
                del dic["parent_pointer"]
        if not hasattr(self, "labels"):
            self.labels = OrderedDict()

        # mobject parameters
        num_labels = len(self.labels)
        for key in labels:
            if key not in self.labels:
                num_labels += 1
            if key in self.labels and labels[key] is None:
                num_labels -= 1

        if "scale_factor" not in dic:
            if hasattr(self, "mobject"):
                dic["scale_factor"] = self.mobject.scale_factor
            else:
                print("Attempted to initialize Node without scale_factor")
                import ipdb; ipdb.set_trace(context=7)

        if "radius" in dic:
            pass
        elif num_labels > 0:
            dic["radius"] = LABELED_NODE_RADIUS * dic["scale_factor"]
        elif num_labels == 0:
            dic["radius"] = UNLABELED_NODE_RADIUS * dic["scale_factor"]
        else:
            dic["radius"] = self.mobject.radius

        if "stroke_width" not in dic:
            if hasattr(self, "mobject"):
                dic["stroke_width"] = self.mobject.stroke_width
            else:
                print("Attempted to initialize Node without stroke_width")
                import ipdb; ipdb.set_trace(context=7)

        if "color" not in dic:
            if hasattr(self, "mobject"):
                dic["color"] = self.mobject.color
            else:
                print("Attempted to initialize Node without color")
                import ipdb; ipdb.set_trace(context=7)

        mobject = dic.get("mobject", None)
        if mobject is None:
            new_mob = Circle(**dic)
        else:
            new_mob = mobject

        if not hasattr(self, "mobject"):
            new_mob.move_to(self.key)
        else:
            new_mob.move_to(self.mobject.get_center())

        ret = []
        if animate:
            ret.extend([ReplacementTransform(self.mobject,
                                             new_mob,
                                             parent=self)])
        else:
            if hasattr(self, "mobject"):
                self.remove(self.mobject)
            self.add(new_mob)
        self.mobject = new_mob

        if labels:
            if animate:
                ret.extend(self.set_labels(labels))
            else:
                self.set_labels(labels, animate=False)

        return ret

    def move_labels(self, new_labels):
        # move
        if len(set(list(self.labels.keys()) + list(new_labels.keys()))) == 1:
            if len(new_labels) == 1:
                list(new_labels.values())[0].move_to(self.mobject.get_center())
            elif len(self.labels) == 1:
                key, val = self.labels.items()[0]
                new_labels[key] = val.copy().move_to(self.mobject.get_center())
            else:
                print("This should be impossible", file=sys.stderr)
                ipdb.set_trace(context=7)
        else:
            vec = rotate_vector(constants.RIGHT, numpy.pi / 2)
            vec *= LABELED_NODE_RADIUS / 2.4 * self.mobject.scale_factor
            old_label_copies = OrderedDict()
            for name, label in self.labels.items():
                if name in new_labels:
                    new_labels[name].move_to(self.mobject.get_center() + vec)
                else:
                    old_label_copies[name] = \
                            label.copy().move_to(
                                    self.mobject.get_center() + vec)
                vec = rotate_vector(
                        vec, 2 * numpy.pi / len(set(list(self.labels.keys()) +
                                                    list(new_labels.keys()))))
            for name, label in new_labels.items():
                if name in self.labels:
                    pass
                else:
                    label.move_to(self.mobject.get_center() + vec)
                    vec = rotate_vector(
                            vec, 2 * numpy.pi / len(set(list(self.labels.keys()) +
                                                        list(new_labels.keys()))))
            ordered_labels = OrderedDict()
            for key in self.labels:
                if key in new_labels:
                    ordered_labels[key] = new_labels[key]
                else:
                    ordered_labels[key] = old_label_copies[key]
            for key in new_labels:
                if key not in self.labels:
                    ordered_labels[key] = new_labels[key]
            new_labels = ordered_labels
        return new_labels


    def get_label_scale_factor(self, label, num_labels):
        if label.get_height() > Integer(7).get_height():
            return self.mobject.scale_factor * \
                Integer(7).get_height() / label.get_height()
        else:
            return self.mobject.scale_factor

    def get_parent_edge(self):
        if hasattr(self, "parent_edge"):
            return self.parent_edge
        else:
            return None

