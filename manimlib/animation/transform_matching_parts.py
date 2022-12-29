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
    from manimlib.scene.scene import Scene


class TransformMatchingParts(AnimationGroup):
    mobject_type: type = Mobject
    group_type: type = Group

    def __init__(
        self,
        mobject: Mobject,
        target_mobject: Mobject,
        transform_mismatches: bool = False,
        fade_transform_mismatches: bool = False,
        key_map: dict | None = None,
        **kwargs
    ):
        assert(isinstance(mobject, self.mobject_type))
        assert(isinstance(target_mobject, self.mobject_type))
        source_map = self.get_shape_map(mobject)
        target_map = self.get_shape_map(target_mobject)
        key_map = key_map or dict()

        # Create two mobjects whose submobjects all match each other
        # according to whatever keys are used for source_map and
        # target_map
        transform_source = self.group_type()
        transform_target = self.group_type()
        kwargs["final_alpha_value"] = 0
        for key in set(source_map).intersection(target_map):
            transform_source.add(source_map[key])
            transform_target.add(target_map[key])
        anims = [Transform(transform_source, transform_target, **kwargs)]
        # User can manually specify when one part should transform
        # into another despite not matching by using key_map
        key_mapped_source = self.group_type()
        key_mapped_target = self.group_type()
        for key1, key2 in key_map.items():
            if key1 in source_map and key2 in target_map:
                key_mapped_source.add(source_map[key1])
                key_mapped_target.add(target_map[key2])
                source_map.pop(key1, None)
                target_map.pop(key2, None)
        if len(key_mapped_source) > 0:
            anims.append(FadeTransformPieces(
                key_mapped_source,
                key_mapped_target,
            ))

        fade_source = self.group_type()
        fade_target = self.group_type()
        for key in set(source_map).difference(target_map):
            fade_source.add(source_map[key])
        for key in set(target_map).difference(source_map):
            fade_target.add(target_map[key])

        if transform_mismatches:
            anims.append(Transform(fade_source.copy(), fade_target, **kwargs))
        if fade_transform_mismatches:
            anims.append(FadeTransformPieces(fade_source, fade_target, **kwargs))
        else:
            anims.append(FadeOutToPoint(
                fade_source, target_mobject.get_center(), **kwargs
            ))
            anims.append(FadeInFromPoint(
                fade_target.copy(), mobject.get_center(), **kwargs
            ))

        super().__init__(*anims)

        self.to_remove = mobject
        self.to_add = target_mobject

    def get_shape_map(self, mobject: Mobject) -> dict[int | str, VGroup]:
        shape_map: dict[int | str, VGroup] = {}
        for sm in self.get_mobject_parts(mobject):
            key = self.get_mobject_key(sm)
            if key not in shape_map:
                shape_map[key] = VGroup()
            shape_map[key].add(sm)
        return shape_map

    def clean_up_from_scene(self, scene: Scene) -> None:
        for anim in self.animations:
            anim.update(0)
        scene.remove(self.mobject)
        scene.remove(self.to_remove)
        scene.add(self.to_add)

    @staticmethod
    def get_mobject_parts(mobject: Mobject) -> Mobject:
        # To be implemented in subclass
        return mobject

    @staticmethod
    def get_mobject_key(mobject: Mobject) -> int:
        # To be implemented in subclass
        return hash(mobject)


class TransformMatchingShapes(TransformMatchingParts):
    mobject_type: type = VMobject
    group_type: type = VGroup

    @staticmethod
    def get_mobject_parts(mobject: VMobject) -> list[VMobject]:
        return mobject.family_members_with_points()

    @staticmethod
    def get_mobject_key(mobject: VMobject) -> int:
        mobject.save_state()
        mobject.center()
        mobject.set_height(1)
        result = hash(np.round(mobject.get_points(), 3).tobytes())
        mobject.restore()
        return result


class TransformMatchingStrings(AnimationGroup):
    def __init__(
        self,
        source: StringMobject,
        target: StringMobject,
        matched_keys: list[str] | None = None,
        key_map: dict[str, str] | None = None,
        match_animation: type = Transform,
        mismatch_animation: type = Transform,
        run_time=2,
        lag_ratio=0,
        **kwargs,
    ):
        self.source = source
        self.target = target
        matched_keys = matched_keys or list()
        key_map = key_map or dict()
        self.anim_config = dict(**kwargs)

        # We will progressively build up a list of transforms
        # from characters in source to those in target. These
        # two lists keep track of which characters are accounted
        # for so far
        self.source_chars = source.family_members_with_points()
        self.target_chars = target.family_members_with_points()
        self.anims = []

        # Start by pairing all matched keys specifically passed in
        for key in matched_keys:
            self.add_transform(
                source.select_parts(key),
                target.select_parts(key),
                match_animation
            )
        # Then pair those based on the key map
        for key, value in key_map.items():
            self.add_transform(
                source.select_parts(key),
                target.select_parts(value),
                mismatch_animation
            )
        # Now pair by substrings which were isolated in StringMobject
        # initializations
        specified_substrings = [
            *source.get_specified_substrings(),
            *target.get_specified_substrings()
        ]
        for key in specified_substrings:
            self.add_transform(
                source.select_parts(key),
                target.select_parts(key),
                match_animation
            )
        # Match any pairs with the same shape
        pairs = self.find_pairs_with_matching_shapes(self.source_chars, self.target_chars)
        for source_char, target_char in pairs:
            self.add_transform(source_char, target_char, match_animation)
        # Finally, account for mismatches
        for source_char in self.source_chars:
            self.anims.append(FadeOutToPoint(
                source_char, target.get_center(),
                **self.anim_config
            ))
        for target_char in self.target_chars:
            self.anims.append(FadeInFromPoint(
                target_char, source.get_center(),
                **self.anim_config
            ))
        super().__init__(
            *self.anims,
            run_time=run_time,
            lag_ratio=lag_ratio,
            group_type=VGroup,
        )

    def add_transform(
        self,
        source: VMobject,
        target: VMobject,
        transform_type: type = Transform,
    ):
        new_source_chars = source.family_members_with_points()
        new_target_chars = target.family_members_with_points()
        source_is_new = all(char in self.source_chars for char in new_source_chars)
        target_is_new = all(char in self.target_chars for char in new_target_chars)
        if source_is_new and target_is_new:
            self.anims.append(transform_type(
                source, target, **self.anim_config
            ))
            for char in new_source_chars:
                self.source_chars.remove(char)
            for char in new_target_chars:
                self.target_chars.remove(char)

    def find_pairs_with_matching_shapes(self, chars1, chars2) -> list[tuple[VMobject, VMobject]]:
        result = []
        for char1, char2 in it.product(chars1, chars2):
            if char1.has_same_shape_as(char2):
                result.append((char1, char2))
        return result

    def clean_up_from_scene(self, scene: Scene) -> None:
        super().clean_up_from_scene(scene)
        scene.remove(self.mobject)
        scene.add(self.target)


class TransformMatchingTex(TransformMatchingStrings):
    """Alias for TransformMatchingStrings"""
    pass
