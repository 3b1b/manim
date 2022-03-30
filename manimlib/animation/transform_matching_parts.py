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
from manimlib.mobject.svg.mtex_mobject import LabelledString
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
        source_mobject: LabelledString,
        target_mobject: LabelledString,
        **kwargs
    ):
        digest_config(self, kwargs)
        assert isinstance(source_mobject, LabelledString)
        assert isinstance(target_mobject, LabelledString)
        anims = []
        rest_source_indices = list(range(len(source_mobject.submobjects)))
        rest_target_indices = list(range(len(target_mobject.submobjects)))

        def add_anims_from(anim_class, func, source_args, target_args=None):
            if target_args is None:
                target_args = source_args.copy()
            for source_arg, target_arg in zip(source_args, target_args):
                source_parts = func(source_mobject, source_arg)
                target_parts = func(target_mobject, target_arg)
                source_indices_lists = source_mobject.indices_lists_of_parts(
                    source_parts
                )
                target_indices_lists = target_mobject.indices_lists_of_parts(
                    target_parts
                )
                filtered_source_indices_lists = list(filter(
                    lambda indices_list: all([
                        index in rest_source_indices
                        for index in indices_list
                    ]), source_indices_lists
                ))
                filtered_target_indices_lists = list(filter(
                    lambda indices_list: all([
                        index in rest_target_indices
                        for index in indices_list
                    ]), target_indices_lists
                ))
                if not all([
                    filtered_source_indices_lists,
                    filtered_target_indices_lists
                ]):
                    return
                anims.append(anim_class(source_parts, target_parts, **kwargs))
                for index in it.chain(*filtered_source_indices_lists):
                    rest_source_indices.remove(index)
                for index in it.chain(*filtered_target_indices_lists):
                    rest_target_indices.remove(index)

        def get_common_substrs(func):
            result = sorted(list(
                set(func(source_mobject)).intersection(func(target_mobject))
            ), key=len, reverse=True)
            if "" in result:
                result.remove("")
            return result

        def get_parts_from_keys(mobject, keys):
            if not isinstance(keys, tuple):
                keys = (keys,)
            indices = []
            for key in keys:
                if isinstance(key, int):
                    indices.append(key)
                elif isinstance(key, range):
                    indices.extend(key)
                elif isinstance(key, str):
                    all_parts = mobject.get_parts_by_string(key)
                    indices.extend(it.chain(*[
                        mobject.indices_of_part(part) for part in all_parts
                    ]))
                else:
                    raise TypeError(key)
            return VGroup(VGroup(*[
                mobject[index] for index in remove_list_redundancies(indices)
            ]))

        add_anims_from(
            ReplacementTransform, get_parts_from_keys,
            self.key_map.keys(), self.key_map.values()
        )
        add_anims_from(
            FadeTransformPieces,
            LabelledString.get_parts_by_string,
            get_common_substrs(
                lambda mobject: mobject.specified_substrings
            )
        )
        add_anims_from(
            FadeTransformPieces,
            LabelledString.get_parts_by_group_substr,
            get_common_substrs(
                lambda mobject: mobject.group_substrs
            )
        )

        fade_source = VGroup(*[
            source_mobject[index]
            for index in rest_source_indices
        ])
        fade_target = VGroup(*[
            target_mobject[index]
            for index in rest_target_indices
        ])
        if self.transform_mismatches:
            anims.append(ReplacementTransform(
                fade_source,
                fade_target,
                **kwargs
            ))
        else:
            anims.append(FadeOutToPoint(
                fade_source,
                target_mobject.get_center(),
                **kwargs
            ))
            anims.append(FadeInFromPoint(
                fade_target,
                source_mobject.get_center(),
                **kwargs
            ))

        super().__init__(*anims)
