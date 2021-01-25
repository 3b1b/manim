"""Debugging utilities."""


__all__ = ["print_family", "index_labels", "get_submobject_index_labels"]


from .color import BLACK
from ..mobject.numbers import Integer
from ..mobject.types.vectorized_mobject import VGroup
import logging


def print_family(mobject, n_tabs=0):
    """For debugging purposes"""
    print("\t" * n_tabs, mobject, id(mobject))
    for submob in mobject.submobjects:
        print_family(submob, n_tabs + 1)


def index_labels(mobject, label_height=0.15):
    labels = VGroup()
    for n, submob in enumerate(mobject):
        label = Integer(n)
        label.set_height(label_height)
        label.move_to(submob)
        label.set_stroke(BLACK, 5, background=True)
        labels.add(label)
    return labels


def get_submobject_index_labels(mobject, label_height=0.15):
    logging.getLogger("manim").warning(
        "get_submobject_index_labels has been deprecated and has been replaced by index_labels, which does the same thing, and will thus be removed in a future release."
    )

    return index_labels(mobject, label_height)
