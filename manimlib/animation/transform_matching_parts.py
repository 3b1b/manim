from __future__ import annotations

import itertools as it

import numpy as np

from manimlib.animation.composition import AnimationGroup
from manimlib.animation.fading import FadeInFromPoint
from manimlib.animation.fading import FadeOutToPoint
from manimlib.animation.fading import FadeTransformPieces
from manimlib.animation.transform import ReplacementTransform
from manimlib.animation.transform import Transform
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.mobject import Group
from manimlib.mobject.svg.string_mobject import StringMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.config_ops import digest_config

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.mobject.svg.tex_mobject import SingleStringTex
    from manimlib.mobject.svg.tex_mobject import Tex
    from manimlib.scene.scene import Scene


class TransformMatchingParts(AnimationGroup):
    CONFIG = {
        "mobject_type": Mobject,
        "group_type": Group,
        "transform_mismatches": False,
        "fade_transform_mismatches": False,
        "key_map": dict(),
    }

    def __init__(self, mobject: Mobject, target_mobject: Mobject, **kwargs):
        digest_config(self, kwargs)
        assert(isinstance(mobject, self.mobject_type))
        assert(isinstance(target_mobject, self.mobject_type))
        source_map = self.get_shape_map(mobject)
        target_map = self.get_shape_map(target_mobject)

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
        for key1, key2 in self.key_map.items():
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

        if self.transform_mismatches:
            anims.append(Transform(fade_source.copy(), fade_target, **kwargs))
        if self.fade_transform_mismatches:
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

    def get_shape_map(self, mobject: Mobject) -> dict[int, VGroup]:
        shape_map: dict[int, VGroup] = {}
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
    CONFIG = {
        "mobject_type": VMobject,
        "group_type": VGroup,
    }

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


class TransformMatchingTex(TransformMatchingParts):
    CONFIG = {
        "mobject_type": VMobject,
        "group_type": VGroup,
    }

    @staticmethod
    def get_mobject_parts(mobject: Tex) -> list[SingleStringTex]:
        return mobject.submobjects

    @staticmethod
    def get_mobject_key(mobject: Tex) -> str:
        return mobject.get_tex()


class TransformMatchingStrings(AnimationGroup):
    CONFIG = {
        "key_map": {},
        "transform_mismatches": False,
    }

    def __init__(self,
        source: StringMobject,
        target: StringMobject,
        **kwargs
    ):
        digest_config(self, kwargs)
        assert isinstance(source, StringMobject)
        assert isinstance(target, StringMobject)
        anims = []
        source_indices = list(range(len(source.labels)))
        target_indices = list(range(len(target.labels)))

        def get_filtered_indices_lists(indices_lists, rest_indices):
            result = []
            for indices_list in indices_lists:
                if not indices_list:
                    continue
                if not all(index in rest_indices for index in indices_list):
                    continue
                result.append(indices_list)
                for index in indices_list:
                    rest_indices.remove(index)
            return result

        def add_anims(anim_class, indices_lists_pairs):
            for source_indices_lists, target_indices_lists in indices_lists_pairs:
                source_indices_lists = get_filtered_indices_lists(
                    source_indices_lists, source_indices
                )
                target_indices_lists = get_filtered_indices_lists(
                    target_indices_lists, target_indices
                )
                if not source_indices_lists or not target_indices_lists:
                    continue
                anims.append(anim_class(
                    source.build_parts_from_indices_lists(source_indices_lists),
                    target.build_parts_from_indices_lists(target_indices_lists),
                    **kwargs
                ))

        def get_substr_to_indices_lists_map(part_items):
            result = {}
            for substr, indices_list in part_items:
                if substr not in result:
                    result[substr] = []
                result[substr].append(indices_list)
            return result

        def add_anims_from(anim_class, func):
            source_substr_map = get_substr_to_indices_lists_map(func(source))
            target_substr_map = get_substr_to_indices_lists_map(func(target))
            common_substrings = sorted([
                s for s in source_substr_map if s and s in target_substr_map
            ], key=len, reverse=True)
            add_anims(
                anim_class,
                [
                    (source_substr_map[substr], target_substr_map[substr])
                    for substr in common_substrings
                ]
            )

        add_anims(
            ReplacementTransform,
            [
                (
                    source.get_submob_indices_lists_by_selector(k),
                    target.get_submob_indices_lists_by_selector(v)
                )
                for k, v in self.key_map.items()
            ]
        )
        add_anims_from(
            FadeTransformPieces,
            StringMobject.get_specified_part_items
        )
        add_anims_from(
            FadeTransformPieces,
            StringMobject.get_group_part_items
        )

        rest_source = VGroup(*[source[index] for index in source_indices])
        rest_target = VGroup(*[target[index] for index in target_indices])
        if self.transform_mismatches:
            anims.append(
                ReplacementTransform(rest_source, rest_target, **kwargs)
            )
        else:
            anims.append(
                FadeOutToPoint(rest_source, target.get_center(), **kwargs)
            )
            anims.append(
                FadeInFromPoint(rest_target, source.get_center(), **kwargs)
            )

        super().__init__(*anims)
