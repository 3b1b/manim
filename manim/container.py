"""
Abstract base class for several objects used by manim.  In particular, both
:class:`~.Scene` and :class:`~.Mobject` inherit from Container.
"""


__all__ = ["Container"]


from abc import ABC, abstractmethod
from . import logger


class Container(ABC):
    """Abstract base class for several objects used by manim.  In particular, both
    :class:`~.Scene` and :class:`~.Mobject` inherit from Container.

    Parameters
    ----------
    kwargs : Any

    """

    def __init__(self, **kwargs):
        if kwargs:
            logger.debug("Container received extra kwargs: %s", kwargs)

        if hasattr(self, "CONFIG"):
            logger.error(
                "CONFIG has been removed from ManimCommunity. Please use keyword arguments instead."
            )

    @abstractmethod
    def add(self, *items):
        """Abstract method to add items to Container.

        Parameters
        ----------
        items : Any
            Objects to be added.
        """

    @abstractmethod
    def remove(self, *items):
        """Abstract method to remove items from Container.

        Parameters
        ----------
        items : Any
            Objects to be added.
        """
