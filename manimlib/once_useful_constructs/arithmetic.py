import numpy as np

from manimlib.animation.animation import Animation
from manimlib.constants import *
from manimlib.mobject.svg.tex_mobject import TexMobject
from manimlib.scene.scene import Scene


class RearrangeEquation(Scene):
    def construct(
        self,
        start_terms,
        end_terms,
        index_map,
        path_arc=np.pi,
        start_transform=None,
        end_transform=None,
        leave_start_terms=False,
        transform_kwargs={},
    ):
        transform_kwargs["path_func"] = path
        start_mobs, end_mobs = self.get_mobs_from_terms(
            start_terms, end_terms
        )
        if start_transform:
            start_mobs = start_transform(Mobject(*start_mobs)).split()
        if end_transform:
            end_mobs = end_transform(Mobject(*end_mobs)).split()
        unmatched_start_indices = set(range(len(start_mobs)))
        unmatched_end_indices = set(range(len(end_mobs)))
        unmatched_start_indices.difference_update(
            [n % len(start_mobs) for n in index_map]
        )
        unmatched_end_indices.difference_update(
            [n % len(end_mobs) for n in list(index_map.values())]
        )
        mobject_pairs = [
            (start_mobs[a], end_mobs[b])
            for a, b in index_map.items()
        ] + [
            (Point(end_mobs[b].get_center()), end_mobs[b])
            for b in unmatched_end_indices
        ]
        if not leave_start_terms:
            mobject_pairs += [
                (start_mobs[a], Point(start_mobs[a].get_center()))
                for a in unmatched_start_indices
            ]

        self.add(*start_mobs)
        if leave_start_terms:
            self.add(Mobject(*start_mobs))
        self.wait()
        self.play(*[
            Transform(*pair, **transform_kwargs)
            for pair in mobject_pairs
        ])
        self.wait()

    def get_mobs_from_terms(self, start_terms, end_terms):
        """
        Need to ensure that all image mobjects for a tex expression
        stemming from the same string are point-for-point copies of one
        and other.  This makes transitions much smoother, and not look
        like point-clouds.
        """
        num_start_terms = len(start_terms)
        all_mobs = np.array(
            TexMobject(start_terms).split() + TexMobject(end_terms).split())
        all_terms = np.array(start_terms + end_terms)
        for term in set(all_terms):
            matches = all_terms == term
            if sum(matches) > 1:
                base_mob = all_mobs[list(all_terms).index(term)]
                all_mobs[matches] = [
                    base_mob.copy().replace(target_mob)
                    for target_mob in all_mobs[matches]
                ]
        return all_mobs[:num_start_terms], all_mobs[num_start_terms:]


class FlipThroughSymbols(Animation):
    CONFIG = {
        "start_center": ORIGIN,
        "end_center": ORIGIN,
    }

    def __init__(self, tex_list, **kwargs):
        mobject = TexMobject(self.curr_tex).shift(start_center)
        Animation.__init__(self, mobject, **kwargs)

    def interpolate_mobject(self, alpha):
        new_tex = self.tex_list[np.ceil(alpha * len(self.tex_list)) - 1]

        if new_tex != self.curr_tex:
            self.curr_tex = new_tex
            self.mobject = TexMobject(new_tex).shift(self.start_center)
        if not all(self.start_center == self.end_center):
            self.mobject.center().shift(
                (1 - alpha) * self.start_center + alpha * self.end_center
            )
