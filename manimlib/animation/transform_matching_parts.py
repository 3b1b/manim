import numpy as np

from manimlib.animation.composition import AnimationGroup
from manimlib.animation.fading import FadeTransformPieces
from manimlib.animation.fading import FadeInFromPoint
from manimlib.animation.fading import FadeOutToPoint
from manimlib.animation.transform import Transform

from manimlib.mobject.mobject import Mobject
from manimlib.mobject.mobject import Group
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.config_ops import digest_config


class TransformMatchingParts(AnimationGroup):
    CONFIG = {
        "mobject_type": Mobject,
        "group_type": Group,
        "transform_mismatches": False,
        "fade_transform_mismatches": False,
        "key_map": dict(),
    }

    def __init__(self, mobject, target_mobject, **kwargs):
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

    def get_shape_map(self, mobject):
        shape_map = {}
        for sm in self.get_mobject_parts(mobject):
            key = self.get_mobject_key(sm)
            if key not in shape_map:
                shape_map[key] = VGroup()
            shape_map[key].add(sm)
        return shape_map

    def clean_up_from_scene(self, scene):
        for anim in self.animations:
            anim.update(0)
        scene.remove(self.mobject)
        scene.remove(self.to_remove)
        scene.add(self.to_add)

    @staticmethod
    def get_mobject_parts(mobject):
        # To be implemented in subclass
        return mobject

    @staticmethod
    def get_mobject_key(mobject):
        # To be implemented in subclass
        return hash(mobject)


class TransformMatchingShapes(TransformMatchingParts):
    CONFIG = {
        "mobject_type": VMobject,
        "group_type": VGroup,
    }

    @staticmethod
    def get_mobject_parts(mobject):
        return mobject.family_members_with_points()

    @staticmethod
    def get_mobject_key(mobject):
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
    def get_mobject_parts(mobject):
        return mobject.submobjects

    @staticmethod
    def get_mobject_key(mobject):
        return mobject.get_tex()
