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
from manimlib.mobject.svg.mtex_mobject import MTex
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


class TransformMatchingMTex(AnimationGroup):
    CONFIG = {
        "key_map": dict(),
    }

    def __init__(self, source_mobject: MTex, target_mobject: MTex, **kwargs):
        digest_config(self, kwargs)
        assert isinstance(source_mobject, MTex)
        assert isinstance(target_mobject, MTex)
        anims = []
        rest_source_submobs = source_mobject.submobjects.copy()
        rest_target_submobs = target_mobject.submobjects.copy()

        def add_anim_from(anim_class, func, source_attr, target_attr=None):
            if target_attr is None:
                target_attr = source_attr
            source_parts = func(source_mobject, source_attr)
            target_parts = func(target_mobject, target_attr)
            filtered_source_parts = [
                submob_part for submob_part in source_parts
                if all([
                    submob in rest_source_submobs
                    for submob in submob_part
                ])
            ]
            filtered_target_parts = [
                submob_part for submob_part in target_parts
                if all([
                    submob in rest_target_submobs
                    for submob in submob_part
                ])
            ]
            if not (filtered_source_parts and filtered_target_parts):
                return
            anims.append(anim_class(
                VGroup(*filtered_source_parts),
                VGroup(*filtered_target_parts),
                **kwargs
            ))
            for submob in it.chain(*filtered_source_parts):
                rest_source_submobs.remove(submob)
            for submob in it.chain(*filtered_target_parts):
                rest_target_submobs.remove(submob)

        def get_submobs_from_keys(mobject, keys):
            if not isinstance(keys, tuple):
                keys = (keys,)
            indices = []
            for key in keys:
                if isinstance(key, int):
                    indices.append(key)
                elif isinstance(key, range):
                    indices.extend(key)
                elif isinstance(key, str):
                    all_parts = mobject.get_parts_by_tex(key)
                    indices.extend(it.chain(*[
                        mobject.indices_of_part(part) for part in all_parts
                    ]))
                else:
                    raise TypeError(key)
            return VGroup(VGroup(*[
                mobject[i] for i in remove_list_redundancies(indices)
            ]))

        for source_key, target_key in self.key_map.items():
            add_anim_from(
                ReplacementTransform, get_submobs_from_keys,
                source_key, target_key
            )

        common_specified_substrings = sorted(list(
            set(source_mobject.get_specified_substrings()).intersection(
                target_mobject.get_specified_substrings()
            )
        ), key=len, reverse=True)
        for part_tex_string in common_specified_substrings:
            add_anim_from(
                FadeTransformPieces, MTex.get_parts_by_tex, part_tex_string
            )

        common_submob_tex_strings = {
            source_submob.get_tex() for source_submob in source_mobject
        }.intersection({
            target_submob.get_tex() for target_submob in target_mobject
        })
        for tex_string in common_submob_tex_strings:
            add_anim_from(
                FadeTransformPieces,
                lambda mobject, attr: VGroup(*[
                    VGroup(mob) for mob in mobject
                    if mob.get_tex() == attr
                ]),
                tex_string
            )

        anims.append(FadeOutToPoint(
            VGroup(*rest_source_submobs), target_mobject.get_center(), **kwargs
        ))
        anims.append(FadeInFromPoint(
            VGroup(*rest_target_submobs), source_mobject.get_center(), **kwargs
        ))

        super().__init__(*anims)
