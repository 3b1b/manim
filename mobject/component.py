from __future__ import print_function
from __future__ import absolute_import
from collections import OrderedDict as OrderedDict
from mobject.geometry import Arrow
from mobject.mobject import Mobject
from animation.creation import ShowCreation
from animation.creation import Uncreate
from animation.transform import ReplacementTransform
import copy
import sys


class Component(Mobject):
    CONFIG = {
        "scale_factor": 1
    }

    def __init__(self, *args, **kwargs):
        # typechecking
        self.key = self.make_key(*args)
        self.assert_primitive(self.key)

        # modifications to self.CONFIG will
        # persist for future mobjects
        config_copy = self.CONFIG.copy()
        config_copy.update(kwargs)
        kwargs = config_copy

        # mobject information is stored in the Mobject, not the Component
        Mobject.__init__(self)
        delattr(self, "dim")
        delattr(self, "scale_factor")
        delattr(self, "name")
        delattr(self, "color")

        if "attrs" in kwargs:
            attrs = kwargs["attrs"]
            del kwargs["attrs"]
        else:
            attrs = OrderedDict()
        for key in kwargs:
            if key not in attrs:
                attrs[key] = kwargs[key]
        self.update_attrs(attrs, animate=False)

    @staticmethod
    def assert_primitive(self):
        # implemented by subclasses
        pass

    def make_key(self):
        # implemented by subclasses
        pass

    def update_attrs(self):
        # implemented by subclasses
        pass

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
            if type(label) == Arrow:
                continue  # TODO
            scale_factor = self.get_label_scale_factor(label, len(new_labels))
            label.scale(scale_factor)

        new_labels = self.move_labels(new_labels, **kwargs)

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

    def move_labels(self, new_labels):
        # implemented by subclass
        pass

    def get_label(self, name):
        return self.labels.get(name, None)

    def get_center(self):
        print("You called get_center() on a Component rather than its mobject",
              file=sys.stderr)
        print("This is probably not what you want", file=sys.stderr)
        breakpoint(context=7)
