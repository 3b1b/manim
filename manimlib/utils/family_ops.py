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
