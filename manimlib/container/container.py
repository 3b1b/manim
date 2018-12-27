from manimlib.utils.config_ops import digest_config

# Currently, this is only used by both Scene and Mobject.
# Still, we abstract its functionality here, albeit purely nominally.
# All actual implementation has to be handled by derived classes for now.
#
# Note that although the prototypical instances add and remove Mobjects,
# there is also the possibility to add ContinualAnimations to Scenes. Thus,
# in the Container class in general, we do not make any presumptions about
# what types of objects may be added; this is again dependent on the specific
# derived instance.

# TODO: Move the "remove" functionality of Scene to this class


class Container(object):
    def __init__(self, *submobjects, **kwargs):
        digest_config(self, kwargs)

    def add(self, *items):
        raise Exception(
            "Container.add is not implemented; it is up to derived classes to implement")

    def remove(self, *items):
        raise Exception(
            "Container.remove is not implemented; it is up to derived classes to implement")
