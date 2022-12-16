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
from manimlib.mobject.svg.tex_mobject import Tex
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.mobject.svg.tex_mobject import SingleStringTex
    from manimlib.mobject.svg.tex_mobject import Tex
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
        key_map: dict = dict(),
        **kwargs
    ):
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


class TransformMatchingTex(TransformMatchingParts):
    mobject_type: type = Tex
    group_type: type = VGroup

    @staticmethod
    def get_mobject_parts(mobject: Tex) -> list[SingleStringTex]:
        return mobject.submobjects

    @staticmethod
    def get_mobject_key(mobject: Tex) -> str:
        return mobject.get_tex()


class TransformMatchingStrings(AnimationGroup):
    def __init__(self,
        source: StringMobject,
        target: StringMobject,
        key_map: dict = {},
        transform_mismatches: bool = False,
        **kwargs
    ):
        assert isinstance(source, StringMobject)
        assert isinstance(target, StringMobject)

        def get_matched_indices_lists(*part_items_list):
            part_items_list_len = len(part_items_list)
            indexed_part_items = sorted(it.chain(*[
                [
                    (substr, items_index, indices_list)
                    for substr, indices_list in part_items
                ]
                for items_index, part_items in enumerate(part_items_list)
            ]))
            grouped_part_items = [
                (substr, [
                    [indices_lists for _, _, indices_lists in grouper_2]
                    for _, grouper_2 in it.groupby(
                        grouper_1, key=lambda t: t[1]
                    )
                ])
                for substr, grouper_1 in it.groupby(
                    indexed_part_items, key=lambda t: t[0]
                )
            ]
            return [
                tuple(indices_lists_list)
                for _, indices_lists_list in sorted(filter(
                    lambda t: t[0] and len(t[1]) == part_items_list_len,
                    grouped_part_items
                ), key=lambda t: len(t[0]), reverse=True)
            ]

        def get_filtered_indices_lists(indices_lists, used_indices):
            result = []
            used = []
            for indices_list in indices_lists:
                if not all(
                    index not in used_indices and index not in used
                    for index in indices_list
                ):
                    continue
                result.append(indices_list)
                used.extend(indices_list)
            return result, used

        anim_class_items = [
            (ReplacementTransform, [
                (
                    source.get_submob_indices_lists_by_selector(k),
                    target.get_submob_indices_lists_by_selector(v)
                )
                for k, v in key_map.items()
            ]),
            (FadeTransformPieces, get_matched_indices_lists(
                source.get_specified_part_items(),
                target.get_specified_part_items()
            )),
            (FadeTransformPieces, get_matched_indices_lists(
                source.get_group_part_items(),
                target.get_group_part_items()
            ))
        ]

        anims = []
        source_used_indices = []
        target_used_indices = []
        for anim_class, pairs in anim_class_items:
            for source_indices_lists, target_indices_lists in pairs:
                source_filtered, source_used = get_filtered_indices_lists(
                    source_indices_lists, source_used_indices
                )
                target_filtered, target_used = get_filtered_indices_lists(
                    target_indices_lists, target_used_indices
                )
                if not source_filtered or not target_filtered:
                    continue
                anims.append(anim_class(
                    source.build_parts_from_indices_lists(source_filtered),
                    target.build_parts_from_indices_lists(target_filtered),
                    **kwargs
                ))
                source_used_indices.extend(source_used)
                target_used_indices.extend(target_used)

        rest_source = VGroup(*(
            submob for index, submob in enumerate(source.submobjects)
            if index not in source_used_indices
        ))
        rest_target = VGroup(*(
            submob for index, submob in enumerate(target.submobjects)
            if index not in target_used_indices
        ))
        if transform_mismatches:
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
