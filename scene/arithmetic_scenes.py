import numpy as np
import itertools as it

from scene import Scene
from graphs import *

from mobject import *
from animation import *
from region import *
from constants import *
from helpers import *

class RearrangeEquation(Scene):
    def construct(
        self, 
        start_terms, 
        end_terms, 
        index_map,
        size = None,
        path = counterclockwise_path,
        start_transform = None,
        end_transform = None,
        leave_start_terms = False,
        transform_kwargs = {},
        ):
        transform_kwargs["interpolation_function"] = path
        start_mobs, end_mobs = self.get_mobs_from_terms(
            start_terms, end_terms, size
        )
        if start_transform:
            start_mobs = start_transform(CompoundMobject(*start_mobs)).split()
        if end_transform:
            end_mobs = end_transform(CompoundMobject(*end_mobs)).split()
        unmatched_start_indices = set(range(len(start_mobs)))
        unmatched_end_indices   = set(range(len(end_mobs)))
        unmatched_start_indices.difference_update(
            [n%len(start_mobs) for n in index_map]
        )
        unmatched_end_indices.difference_update(
            [n%len(end_mobs) for n in index_map.values()]
        )
        mobject_pairs = [
            (start_mobs[a], end_mobs[b])
            for a, b in index_map.iteritems()
        ]+ [
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
            self.add(CompoundMobject(*start_mobs))
        self.dither()
        self.animate(*[
            Transform(*pair, **transform_kwargs)
            for pair in mobject_pairs
        ])
        self.dither()


    def get_mobs_from_terms(self, start_terms, end_terms, size):
        """
        Need to ensure that all image mobjects for a tex expression
        stemming from the same string are point-for-point copies of one
        and other.  This makes transitions much smoother, and not look
        like point-clouds.
        """
        num_start_terms = len(start_terms)
        all_mobs = np.array(
            tex_mobject(start_terms, size = size).split() + \
            tex_mobject(end_terms, size = size).split()
        )
        all_terms = np.array(start_terms+end_terms)
        for term in set(all_terms):
            matches = all_terms == term
            if sum(matches) > 1:
                base_mob = all_mobs[list(all_terms).index(term)]
                all_mobs[matches] = [
                    deepcopy(base_mob).replace(target_mob)
                    for target_mob in all_mobs[matches]
                ]
        return all_mobs[:num_start_terms], all_mobs[num_start_terms:]






