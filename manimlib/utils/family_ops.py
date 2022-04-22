from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable

    from manimlib.mobject.mobject import Mobject


def extract_mobject_family_members(
    mobject_list: Iterable[Mobject],
    exclude_pointless: bool = False
) -> list[Mobject]:
    return [
        sm
        for mob in mobject_list
        for sm in mob.get_family()
        if (not exclude_pointless) or sm.has_points()
    ]


def restructure_list_to_exclude_certain_family_members(
    mobject_list: list[Mobject],
    to_remove: list[Mobject]
) -> list[Mobject]:
    """
    Removes anything in to_remove from mobject_list, but in the event that one of
    the items to be removed is a member of the family of an item in mobject_list,
    the other family members are added back into the list.

    This is useful in cases where a scene contains a group, e.g. Group(m1, m2, m3),
    but one of its submobjects is removed, e.g. scene.remove(m1), it's useful
    for the list of mobject_list to be edited to contain other submobjects, but not m1.
    """
    new_list = []
    to_remove = extract_mobject_family_members(to_remove)

    def add_safe_mobjects_from_list(list_to_examine, set_to_remove):
        for mob in list_to_examine:
            if mob in set_to_remove:
                continue
            intersect = set_to_remove.intersection(mob.get_family())
            if intersect:
                add_safe_mobjects_from_list(mob.submobjects, intersect)
            else:
                new_list.append(mob)
    add_safe_mobjects_from_list(mobject_list, set(to_remove))
    return new_list
