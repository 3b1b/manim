from mobject import Mobject
from collections import OrderedDict as OrderedDict

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
        # will overwrite instance variables
        Mobject.__init__(self, **config_copy)

        # create mobject
        self.mobject = self.create_mobject(*args, **kwargs)
        self.add(self.mobject)

        self.labels = OrderedDict()
        self.update(kwargs.get("attrs", None), animate=False)

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
