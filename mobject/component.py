from mobject import Mobject
from collections import OrderedDict as OrderedDict

class Component(Mobject):
    def __init__(self, *args, **kwargs):
        # typechecking
        self.key = self.make_key(*args)
        self.assert_primitive(self.key)

        # mobject init (will overwrite instance variables)
        kwargs.update(self.CONFIG)
        Mobject.__init__(self, **kwargs)

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
            self.set_labels(*kwargs["labels"], animate=False)

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
