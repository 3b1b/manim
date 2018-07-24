from __future__ import print_function
from mobject import Mobject
from collections import OrderedDict as OrderedDict
import sys
import ipdb


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
        delattr(self, "override_children")
        delattr(self, "initial_config")

        if "attrs" in kwargs:
            attrs = kwargs["attrs"]
            del kwargs["attrs"]
        else:
            attrs = OrderedDict()
        for key in kwargs:
            if key not in attrs:
                attrs[key] = kwargs[key]
        self.update(attrs, animate=False)

    @staticmethod
    def assert_primitive(self):
        # implemented by subclasses
        pass

    def make_key(self):
        # implemented by subclasses
        pass

    def update(self):
        # implemented by subclasses
        pass

    def set_labels(self):
        # implemented by subclass
        pass

    def get_label(self):
        # implemented by subclass
        pass

    def get_center(self):
        print("You called get_center() on a Component rather than its mobject",
              file=sys.stderr)
        print("This is probably not what you want", file=sys.stderr)
        ipdb.set_trace(context=7)
