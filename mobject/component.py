from mobject import Mobject
from collections import OrderedDict as OrderedDict

class Component(Mobject):
    CONFIG = {
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
        # will overwrite instance variables
        Mobject.__init__(self, **config_copy)

        # initialize variables
        if "scale_factor" in kwargs:
            self.scale_factor = kwargs["scale_factor"]
        else:
            self.scale_factor = 1

        # create mobject
        self.mobject = self.create_mobject(*args, **kwargs)
        self.add(self.mobject)

        # add labels
        self.labels = OrderedDict()
        if "labels" in kwargs and kwargs["labels"] is not None:
            self.set_labels(OrderedDict(kwargs["labels"]), animate=False)

    @staticmethod
    def assert_primitive(self):
        # implemented by subclasses
        pass

    def make_key(self):
        # implemented by subclasses
        pass

    def create_mobject(self):
        # implemented by subclass
        pass

    def set_labels(self):
        # implemented by subclass
        pass

    def get_center(self):
        """
        You called get_center() on a Component rather than its mobject.
        This is probably not what you want.
        """
        import ipdb; ipdb.set_trace(context=7)
