from __future__ import annotations

import itertools as it

import numpy as np

from manimlib.animation.composition import AnimationGroup
from manimlib.animation.fading import FadeInFromPoint
from manimlib.animation.fading import FadeOutToPoint
from manimlib.animation.fading import FadeTransformPieces
from manimlib.animation.transform import Transform
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.mobject import Group
from manimlib.mobject.svg.string_mobject import StringMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable
    from manimlib.scene.scene import Scene


class TransformMatchingParts(AnimationGroup):
    def __init__(
        self,
        source: Mobject,
        target: Mobject,
        matched_pairs: Iterable[tuple[Mobject, Mobject]] = [],
        match_animation: type = Transform,
        mismatch_animation: type = Transform,
        run_time: float = 2,
        lag_ratio: float = 0,
        **kwargs,
    ):
        self.source = source
        self.target = target
        self.match_animation = match_animation
        self.mismatch_animation = mismatch_animation
        self.anim_config = dict(**kwargs)

        # We will progressively build up a list of transforms
        # from pieces in source to those in target. These
        # two lists keep track of which pieces are accounted
        # for so far
        self.source_pieces = source.family_members_with_points()
        self.target_pieces = target.family_members_with_points()
        self.anims = []

        for pair in matched_pairs:
            self.add_transform(*pair)

        # Match any pairs with the same shape
        for pair in self.find_pairs_with_matching_shapes(self.source_pieces, self.target_pieces):
            self.add_transform(*pair)

        # Finally, account for mismatches
        for source_piece in self.source_pieces:
            if any([source_piece in anim.mobject.get_family() for anim in self.anims]):
                continue
            self.anims.append(FadeOutToPoint(
                source_piece, target.get_center(),
                **self.anim_config
            ))
        for target_piece in self.target_pieces:
            if any([target_piece in anim.mobject.get_family() for anim in self.anims]):
                continue
            self.anims.append(FadeInFromPoint(
                target_piece, source.get_center(),
                **self.anim_config
            ))

        super().__init__(
            *self.anims,
            run_time=run_time,
            lag_ratio=lag_ratio,
        )

    def add_transform(
        self,
        source: Mobject,
        target: Mobject,
    ):
        new_source_pieces = source.family_members_with_points()
        new_target_pieces = target.family_members_with_points()
        if len(new_source_pieces) == 0 or len(new_target_pieces) == 0:
            # Don't animate null sorces or null targets
            return
        source_is_new = all(char in self.source_pieces for char in new_source_pieces)
        target_is_new = all(char in self.target_pieces for char in new_target_pieces)
        if not source_is_new or not target_is_new:
            return

        transform_type = self.mismatch_animation 
        if source.has_same_shape_as(target):
            transform_type = self.match_animation

        self.anims.append(transform_type(source, target, **self.anim_config))
        for char in new_source_pieces:
            self.source_pieces.remove(char)
        for char in new_target_pieces:
            self.target_pieces.remove(char)

    def find_pairs_with_matching_shapes(
        self,
        chars1: list[Mobject],
        chars2: list[Mobject]
    ) -> list[tuple[Mobject, Mobject]]:
        result = []
        for char1, char2 in it.product(chars1, chars2):
            if char1.has_same_shape_as(char2):
                result.append((char1, char2))
        return result

    def clean_up_from_scene(self, scene: Scene) -> None:
        super().clean_up_from_scene(scene)
        scene.remove(self.mobject)
        scene.add(self.target)


class TransformMatchingShapes(TransformMatchingParts):
    """Alias for TransformMatchingParts"""
    pass


class TransformMatchingStrings(TransformMatchingParts):
    def __init__(
        self,
        source: StringMobject,
        target: StringMobject,
        matched_keys: Iterable[str] = [],
        key_map: dict[str, str] = dict(),
        **kwargs,
    ):
        matched_pairs = [
            *[(source[key], target[key]) for key in matched_keys],
            *[(source[key1], target[key2]) for key1, key2 in key_map.items()],
            *[
                (source[substr], target[substr])
                for substr in [
                    *source.get_specified_substrings(),
                    *target.get_specified_substrings(),
                    *source.get_symbol_substrings(),
                    *target.get_symbol_substrings(),
                ]
            ]
        ]
        super().__init__(
            source, target,
            matched_pairs=matched_pairs,
            **kwargs,
        )


class TransformMatchingTex(TransformMatchingStrings):
    """Alias for TransformMatchingStrings"""
    pass
