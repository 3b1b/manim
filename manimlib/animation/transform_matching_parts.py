from manimlib.animation.composition import AnimationGroup
from manimlib.animation.fading import FadeTransformPieces
from manimlib.animation.transform import Transform

from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject


class TransformMatchingParts(AnimationGroup):
    def __init__(self, mobject, target_mobject, **kwargs):
        assert(isinstance(mobject, VMobject) and isinstance(target_mobject, VMobject))
        source_map = self.get_shape_map(mobject)
        target_map = self.get_shape_map(target_mobject)

        transform_source = VGroup()
        transform_target = VGroup()
        fade_source = VGroup()
        fade_target = VGroup()

        for key in set(source_map).intersection(target_map):
            transform_source.add(source_map[key])
            transform_target.add(target_map[key])
        for key in set(source_map).difference(target_map):
            fade_source.add(source_map[key])
        for key in set(target_map).difference(source_map):
            fade_target.add(target_map[key])

        kwargs["final_alpha_value"] = 0
        super().__init__(
            Transform(transform_source, transform_target, **kwargs),
            FadeTransformPieces(fade_source, fade_target, **kwargs),
        )

        self.to_remove = mobject
        self.to_add = target_mobject

    def get_shape_map(self, mobject):
        shape_map = {}
        for sm in mobject.family_members_with_points():
            key = hash(sm.get_triangulation().tobytes())
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
