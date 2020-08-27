from manimlib.utils.config_ops import digest_config

# Currently, this is only used by both Scene and Mobject.
# Still, we abstract its functionality here, albeit purely nominally.
# All actual implementation has to be handled by derived classes for now.

# TODO: Move the "remove" functionality of Scene to this class


class Container(object):
    """
    Base class for Scenes and Mobjects. Generic container.
    """
    def __init__(self, **kwargs):
        digest_config(self, kwargs)

    def add(self, *items):
        """
        Generic method to add items to Container.
        Must be implemented by subclasses.
        """
        raise Exception(
            "Container.add is not implemented; it is up to derived classes to implement")

    def remove(self, *items):
        """
        Generic method to remove items from Container.
        Must be implemented by subclasses.
        """
        raise Exception(
            "Container.remove is not implemented; it is up to derived classes to implement")
