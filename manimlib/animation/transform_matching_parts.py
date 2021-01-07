from manimlib.animation.composition import AnimationGroup
from manimlib.animation.fading import FadeTransformPieces
from manimlib.animation.fading import FadeInFromPoint
from manimlib.animation.fading import FadeOutToPoint
from manimlib.animation.transform import Transform

from manimlib.mobject.mobject import Mobject
from manimlib.mobject.mobject import Group
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.svg.tex_mobject import TexMobject
from manimlib.utils.config_ops import digest_config


class TransformMatchingParts(AnimationGroup):
    CONFIG = {
        "mobject_type": Mobject,
        "group_type": Group,
        "transform_mismatches": False,
        "fade_transform_mismatches": False,
    }

    def __init__(self, mobject, target_mobject, **kwargs):
        digest_config(self, kwargs)
        assert(isinstance(mobject, VMobject) and isinstance(target_mobject, VMobject))
        source_map = self.get_shape_map(mobject)
        target_map = self.get_shape_map(target_mobject)

        transform_source = VGroup()
        transform_target = VGroup()
        fade_source = VGroup()
        fade_target = VGroup()

        kwargs["final_alpha_value"] = 0
        for key in set(source_map).intersection(target_map):
            transform_source.add(source_map[key])
            transform_target.add(target_map[key])
        anims = [Transform(transform_source, transform_target, **kwargs)]

        for key in set(source_map).difference(target_map):
            fade_source.add(source_map[key])
        for key in set(target_map).difference(source_map):
            fade_target.add(target_map[key])

        if self.transform_mismatches:
            anims.append(Transform(fade_source, fade_target, **kwargs))
        if self.fade_transform_mismatches:
            anims.append(FadeTransformPieces(fade_source, fade_target, **kwargs))
        else:
            anims.append(FadeOutToPoint(
                fade_source, fade_target.get_center(), **kwargs
            ))
            anims.append(FadeInFromPoint(
                fade_target.copy(), fade_source.get_center(), **kwargs
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

    def get_mobject_parts(self, mobject):
        # To be implemented in subclass
        return mobject

    def get_mobject_key(self, mobject):
        # To be implemented in subclass
        return hash(mobject)


class TransformMatchingShapes(TransformMatchingParts):
    CONFIG = {
        "mobject_type": VMobject,
        "group_type": VGroup,
    }

    def get_mobject_parts(self, mobject):
        return mobject.family_members_with_points()

    def get_mobject_key(self, mobject):
        return hash(mobject.get_triangulation().tobytes())


class TransformMatchingTex(TransformMatchingParts):
    CONFIG = {
        "mobject_type": TexMobject,
        "group_type": VGroup,
    }

    def get_mobject_parts(self, mobject):
        return mobject.submobjects

    def get_mobject_key(self, mobject):
        return mobject.get_tex_string()
