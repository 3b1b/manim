from __future__ import annotations

import numpy as np
import time

from manimlib.constants import BLACK
from manimlib.logger import log
from manimlib.mobject.numbers import Integer
from manimlib.mobject.types.vectorized_mobject import VGroup

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable

    from manimlib.mobject.mobject import Mobject


def print_family(mobject: Mobject, n_tabs: int = 0) -> None:
    """For debugging purposes"""
    log.debug("\t" * n_tabs + str(mobject) + " " + str(id(mobject)))
    for submob in mobject.submobjects:
        print_family(submob, n_tabs + 1)


def index_labels(
    mobject: Mobject | np.ndarray, 
    label_height: float = 0.15
) -> VGroup:
    labels = VGroup()
    for n, submob in enumerate(mobject):
        label = Integer(n)
        label.set_height(label_height)
        label.move_to(submob)
        label.set_stroke(BLACK, 5, background=True)
        labels.add(label)
    return labels


def get_runtime(func: Callable) -> float:
    now = time.time()
    func()
    return time.time() - now
