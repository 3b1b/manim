"""
Abstract base class for several objects used by manim.  In particular, both
:class:`~.Scene` and :class:`~.Mobject` inherit from Container.
"""


__all__ = ["Container"]


from abc import ABC, abstractmethod
from .utils.config_ops import digest_config


class Container(ABC):
    """Abstract base class for several objects used by manim.  In particular, both
    :class:`~.Scene` and :class:`~.Mobject` inherit from Container.

    Parameters
    ----------
    kwargs : Any
        Arguments to be passed to :func:`~.digest_config`

    """

    def __init__(self, **kwargs):
        digest_config(self, kwargs)

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
