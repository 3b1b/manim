from __future__ import annotations

import itertools as it

import numpy as np

from manimlib.animation.composition import AnimationGroup
from manimlib.animation.fading import FadeTransformPieces
from manimlib.animation.fading import FadeInFromPoint
from manimlib.animation.fading import FadeOutToPoint
from manimlib.animation.transform import ReplacementTransform
from manimlib.animation.transform import Transform
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.mobject import Group
from manimlib.mobject.svg.labelled_string import LabelledString
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.config_ops import digest_config
from manimlib.utils.iterables import remove_list_redundancies

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.scene.scene import Scene
    from manimlib.mobject.svg.tex_mobject import Tex, SingleStringTex


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
        "key_map": dict(),
        "transform_mismatches": False,
    }

    def __init__(self,
        source: LabelledString,
        target: LabelledString,
        **kwargs
    ):
        digest_config(self, kwargs)
        assert isinstance(source, LabelledString)
        assert isinstance(target, LabelledString)
        anims = []
        source_indices = list(range(len(source.labelled_submobjects)))
        target_indices = list(range(len(target.labelled_submobjects)))

        def get_indices_lists(mobject, parts):
            return [
                [
                    mobject.labelled_submobjects.index(submob)
                    for submob in part
                ]
                for part in parts
            ]

        def add_anims_from(anim_class, func, source_args, target_args=None):
            if target_args is None:
                target_args = source_args.copy()
            for source_arg, target_arg in zip(source_args, target_args):
                source_parts = func(source, source_arg)
                target_parts = func(target, target_arg)
                source_indices_lists = list(filter(
                    lambda indices_list: all([
                        index in source_indices
                        for index in indices_list
                    ]), get_indices_lists(source, source_parts)
                ))
                target_indices_lists = list(filter(
                    lambda indices_list: all([
                        index in target_indices
                        for index in indices_list
                    ]), get_indices_lists(target, target_parts)
                ))
                if not source_indices_lists or not target_indices_lists:
                    continue
                anims.append(anim_class(source_parts, target_parts, **kwargs))
                for index in it.chain(*source_indices_lists):
                    source_indices.remove(index)
                for index in it.chain(*target_indices_lists):
                    target_indices.remove(index)

        def get_common_substrs(substrs_from_source, substrs_from_target):
            return sorted([
                substr for substr in substrs_from_source
                if substr and substr in substrs_from_target
            ], key=len, reverse=True)

        def get_parts_from_keys(mobject, keys):
            if isinstance(keys, str):
                keys = [keys]
            result = VGroup()
            for key in keys:
                if not isinstance(key, str):
                    raise TypeError(key)
                result.add(*mobject.get_parts_by_string(key))
            return result

        add_anims_from(
            ReplacementTransform, get_parts_from_keys,
            self.key_map.keys(), self.key_map.values()
        )
        add_anims_from(
            FadeTransformPieces,
            LabelledString.get_parts_by_string,
            get_common_substrs(
                source.specified_substrs,
                target.specified_substrs
            )
        )
        add_anims_from(
            FadeTransformPieces,
            LabelledString.get_parts_by_group_substr,
            get_common_substrs(
                source.group_substrs,
                target.group_substrs
            )
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
