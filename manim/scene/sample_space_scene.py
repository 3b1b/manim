"""A scene suitable for usage with :class:`.SampleSpace`."""

__all__ = ["SampleSpaceScene"]


from ..animation.animation import Animation
from ..animation.transform import MoveToTarget
from ..animation.transform import Transform
from ..animation.update import UpdateFromFunc
from ..constants import *
from ..scene.scene import Scene
from ..mobject.probability import SampleSpace
from ..mobject.types.vectorized_mobject import VGroup


class SampleSpaceScene(Scene):
    def get_sample_space(self, **config):
        self.sample_space = SampleSpace(**config)
        return self.sample_space

    def add_sample_space(self, **config):
        self.add(self.get_sample_space(**config))

    def get_division_change_animations(
        self, sample_space, parts, p_list, dimension=1, new_label_kwargs=None, **kwargs
    ):
        if new_label_kwargs is None:
            new_label_kwargs = {}
        anims = []
        p_list = sample_space.complete_p_list(p_list)
        space_copy = sample_space.copy()

        vect = DOWN if dimension == 1 else RIGHT
        parts.generate_target()
        for part, p in zip(parts.target, p_list):
            part.replace(space_copy, stretch=True)
            part.stretch(p, dimension)
        parts.target.arrange(vect, buff=0)
        parts.target.move_to(space_copy)
        anims.append(MoveToTarget(parts))
        if hasattr(parts, "labels") and parts.labels is not None:
            label_kwargs = parts.label_kwargs
            label_kwargs.update(new_label_kwargs)
            new_braces, new_labels = sample_space.get_subdivision_braces_and_labels(
                parts.target, **label_kwargs
            )
            anims += [
                Transform(parts.braces, new_braces),
                Transform(parts.labels, new_labels),
            ]
        return anims

    def get_horizontal_division_change_animations(self, p_list, **kwargs):
        assert hasattr(self.sample_space, "horizontal_parts")
        return self.get_division_change_animations(
            self.sample_space,
            self.sample_space.horizontal_parts,
            p_list,
            dimension=1,
            **kwargs,
        )

    def get_vertical_division_change_animations(self, p_list, **kwargs):
        assert hasattr(self.sample_space, "vertical_parts")
        return self.get_division_change_animations(
            self.sample_space,
            self.sample_space.vertical_parts,
            p_list,
            dimension=0,
            **kwargs,
        )

    def get_conditional_change_anims(
        self, sub_sample_space_index, value, post_rects=None, **kwargs
    ):
        parts = self.sample_space.horizontal_parts
        sub_sample_space = parts[sub_sample_space_index]
        anims = self.get_division_change_animations(
            sub_sample_space,
            sub_sample_space.vertical_parts,
            value,
            dimension=0,
            **kwargs,
        )
        if post_rects is not None:
            anims += self.get_posterior_rectangle_change_anims(post_rects)
        return anims

    def get_top_conditional_change_anims(self, *args, **kwargs):
        return self.get_conditional_change_anims(0, *args, **kwargs)

    def get_bottom_conditional_change_anims(self, *args, **kwargs):
        return self.get_conditional_change_anims(1, *args, **kwargs)

    def get_prior_rectangles(self):
        return VGroup(
            *[self.sample_space.horizontal_parts[i].vertical_parts[0] for i in range(2)]
        )

    def get_posterior_rectangles(self, buff=MED_LARGE_BUFF):
        prior_rects = self.get_prior_rectangles()
        areas = [rect.get_width() * rect.get_height() for rect in prior_rects]
        total_area = sum(areas)
        total_height = prior_rects.get_height()

        post_rects = prior_rects.copy()
        for rect, area in zip(post_rects, areas):
            rect.stretch_to_fit_height(total_height * area / total_area)
            rect.stretch_to_fit_width(area / rect.get_height())
        post_rects.arrange(DOWN, buff=0)
        post_rects.next_to(self.sample_space, RIGHT, buff)
        return post_rects

    def get_posterior_rectangle_braces_and_labels(
        self, post_rects, labels, direction=RIGHT, **kwargs
    ):
        return self.sample_space.get_subdivision_braces_and_labels(
            post_rects, labels, direction, **kwargs
        )

    def update_posterior_braces(self, post_rects):
        braces = post_rects.braces
        labels = post_rects.labels
        for rect, brace, label in zip(post_rects, braces, labels):
            brace.stretch_to_fit_height(rect.get_height())
            brace.next_to(rect, RIGHT, SMALL_BUFF)
            label.next_to(brace, RIGHT, SMALL_BUFF)

    def get_posterior_rectangle_change_anims(self, post_rects):
        def update_rects(rects):
            new_rects = self.get_posterior_rectangles()
            Transform(rects, new_rects).update(1)
            if hasattr(rects, "braces"):
                self.update_posterior_braces(rects)
            return rects

        anims = [UpdateFromFunc(post_rects, update_rects)]
        if hasattr(post_rects, "braces"):
            anims += list(map(Animation, [post_rects.labels, post_rects.braces]))
        return anims
