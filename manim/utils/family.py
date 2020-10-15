import itertools as it

from ..mobject.mobject import Mobject
from ..utils.iterables import remove_list_redundancies


def extract_mobject_family_members(
    mobjects, use_z_index=False, only_those_with_points=False
):
    """Returns a list of the types of mobjects and their family members present.
    A "family" in this context refers to a mobject, its submobjects, and their
    submobjects, recursively.

    Parameters
    ----------
    mobjects : Mobject
        The Mobjects currently in the Scene
    only_those_with_points : bool, optional
        Whether or not to only do this for
        those mobjects that have points. By default False

    Returns
    -------
    list
        list of the mobjects and family members.
    """
    if only_those_with_points:
        method = Mobject.family_members_with_points
    else:
        method = Mobject.get_family
    if use_z_index:
        mobjects = sorted(mobjects, key=lambda m: m.z_index)
    return remove_list_redundancies(list(it.chain(*[method(m) for m in mobjects])))
