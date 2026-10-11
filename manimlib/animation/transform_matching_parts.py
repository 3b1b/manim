from __future__ import annotations

import itertools as it
from difflib import SequenceMatcher

from manimlib.animation.composition import AnimationGroup
from manimlib.animation.fading import FadeInFromPoint
from manimlib.animation.fading import FadeOutToPoint
from manimlib.animation.transform import Transform
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.svg.string_mobject import StringMobject

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable
    from manimlib.scene.scene import Scene


class TransformMatchingParts(AnimationGroup):
    """
    TransformMatchingParts
    ======================

    An AnimationGroup that transforms the individual point-bearing components
    of one Mobject into the components of another Mobject. It attempts to
    match components by shape, allowing corresponding pieces to transform
    directly while unmatched source pieces fade out and unmatched target
    pieces fade in.

    TransformMatchingParts is useful for visualizing changes between
    mathematical expressions, diagrams, geometric constructions, and other
    compound Mobjects whose components can be animated independently.

    Unlike a single Transform applied to an entire compound object, this
    class builds a collection of animations for individual components.
    Explicit matched_pairs can specify correspondences, while remaining
    components are automatically paired when they have the same shape.

    Components that cannot be matched are handled with point-based fade
    animations: unmatched source components fade out toward the target's
    center, and unmatched target components fade in from the source's center.

    Parameters
    ----------
    source : Mobject
        The original Mobject whose components will be transformed, faded
        out, or otherwise animated.

    target : Mobject
        The destination Mobject whose components will be transformed into
        or faded in. The target is added to the scene during cleanup.

    matched_pairs : Iterable[tuple[Mobject, Mobject]], default=()
        An iterable of pairs specifying explicit source-target component
        correspondences. Each pair contains a source component and its
        intended target component.

        Explicit pairs are processed before automatic shape matching.
        Components successfully accounted for by an earlier pair are
        removed from the lists used for subsequent matching.

    match_animation : type, default=Transform
        The animation class used when a matched source component and target
        component have the same shape according to has_same_shape_as().

    mismatch_animation : type, default=Transform
        The animation class used when a component pair is explicitly
        supplied or otherwise passed to add_transform(), but the two
        components do not have the same shape.

        Despite the parameter name, the default is Transform, so mismatched
        components that are paired are still transformed directly rather
        than automatically faded out and faded in.

    run_time : float, default=2
        Total runtime passed to AnimationGroup.

    lag_ratio : float, default=0
        Lag ratio passed to AnimationGroup. Controls the relative scheduling
        of the component animations according to AnimationGroup's behavior.

    **kwargs
        Additional keyword arguments stored in anim_config and passed to
        the individual match, mismatch, FadeOutToPoint, and FadeInFromPoint
        animations.

    Attributes
    ----------
    source : Mobject
        The original compound Mobject.

    target : Mobject
        The destination compound Mobject.

    match_animation : type
        Animation class used for pairs with matching shapes.

    mismatch_animation : type
        Animation class used for pairs with different shapes.

    anim_config : dict
        Dictionary containing the extra keyword arguments forwarded to the
        component animations.

    source_pieces : list[Mobject]
        Mutable list of source family members with points that have not yet
        been successfully accounted for by add_transform().

    target_pieces : list[Mobject]
        Mutable list of target family members with points that have not yet
        been successfully accounted for by add_transform().

    anims : list[Animation]
        The component animations assembled during initialization. This list
        is passed to AnimationGroup after explicit matching, automatic shape
        matching, and unmatched-component handling.

    Implementation
    --------------
    1. Collect point-bearing family members from source and target using
       family_members_with_points().
    2. Process the explicitly supplied matched_pairs by calling
       add_transform() for each pair.
    3. Search the remaining source and target components for pairs whose
       shapes match according to has_same_shape_as().
    4. For each accepted pair, select match_animation or
       mismatch_animation and append the resulting animation to anims.
    5. Fade out any remaining source components toward target.get_center().
    6. Fade in any remaining target components from source.get_center().
    7. Initialize AnimationGroup with the assembled animations, run_time,
       and lag_ratio.
    8. During cleanup, perform the parent AnimationGroup cleanup, remove
       self.mobject from the scene, and add target to the scene.

    The add_transform() method verifies that the selected source and target
    families contain point-bearing components still present in the remaining
    piece lists. Empty families and components that have already been
    accounted for are ignored.

    Examples
    --------
    1. Transform one geometric shape into another
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    from manimlib import *

    class ShapeMatchingExample(Scene):
        def construct(self):
            source = VGroup(
                Circle(radius=0.5, color=BLUE),
                Square(side_length=1, color=YELLOW),
            ).arrange(RIGHT)

            target = VGroup(
                Circle(radius=0.8, color=GREEN),
                Triangle(color=RED),
            ).arrange(RIGHT)

            self.add(source)

            self.play(
                TransformMatchingParts(
                    source,
                    target,
                    run_time=3,
                )
            )

            self.wait()

    The class searches for components with matching shapes. Matching pieces
    use match_animation, while unmatched pieces are handled by the configured
    mismatch behavior or the point-based fade animations.

    2. Explicitly match selected components
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    from manimlib import *

    class ExplicitMatchingExample(Scene):
        def construct(self):
            source_circle = Circle(color=BLUE)
            source_square = Square(color=YELLOW)
            source = VGroup(source_circle, source_square).arrange(RIGHT)

            target_circle = Circle(radius=1.2, color=GREEN)
            target_triangle = Triangle(color=RED)
            target = VGroup(target_circle, target_triangle).arrange(RIGHT)

            self.add(source)

            self.play(
                TransformMatchingParts(
                    source,
                    target,
                    matched_pairs=[
                        (source_circle, target_circle),
                        (source_square, target_triangle),
                    ],
                    run_time=3,
                )
            )

            self.wait()

    Explicit pairs are processed first. The circle pair can use the matching
    animation, while the square-triangle pair uses mismatch_animation because
    the shapes differ. In both cases, the chosen animation class receives
    the source component and target component.

    3. Use a different animation for shape mismatches
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    from manimlib import *

    class CustomMismatchExample(Scene):
        def construct(self):
            source = VGroup(
                Square(color=BLUE),
                Circle(color=YELLOW),
            ).arrange(RIGHT)

            target = VGroup(
                Triangle(color=GREEN),
                Circle(color=RED),
            ).arrange(RIGHT)

            self.add(source)

            self.play(
                TransformMatchingParts(
                    source,
                    target,
                    matched_pairs=[(source[0], target[0])],
                    match_animation=Transform,
                    mismatch_animation=Transform,
                    run_time=3,
                )
            )

            self.wait()

    This example explicitly pairs the square with the triangle, so that
    pair is transformed using mismatch_animation. The remaining circle
    components can be automatically paired if their shapes match.

    To use a different animation for mismatches, supply another compatible
    animation class that accepts the source, target, and anim_config keyword
    arguments.

    4. Configure the timing of component animations
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    from manimlib import *

    class MatchingTimingExample(Scene):
        def construct(self):
            source = VGroup(
                Circle(),
                Square(),
                Triangle(),
            ).arrange(RIGHT)

            target = VGroup(
                Triangle(color=GREEN),
                Circle(color=BLUE),
                Square(color=RED),
            ).arrange(RIGHT)

            self.add(source)

            self.play(
                TransformMatchingParts(
                    source,
                    target,
                    run_time=4,
                    lag_ratio=0.2,
                )
            )

            self.wait()

    The lag_ratio is forwarded to AnimationGroup and affects the scheduling
    of the individual component animations. Actual timing depends on the
    number and durations of the component animations.

    Notes
    -----
    - Matching is based on has_same_shape_as(), not semantic meaning,
      textual identity, or visual proximity.
    - Explicit matched_pairs are processed before automatic matching.
      Use them when multiple components have identical shapes but represent
      different conceptual elements.
    - Automatic matching checks every pair of remaining components using
      a Cartesian product. With many components, this search can become
      computationally expensive.
    - The implementation does not stop searching after finding the first
      matching pair. It collects matching pairs from the remaining lists
      and passes them through add_transform(). Since add_transform()
      removes accounted-for components, later pairs involving already
      consumed components are rejected.
    - A component with no point-bearing family members is ignored by
      add_transform().
    - Unmatched source components use FadeOutToPoint toward the target
      center; unmatched target components use FadeInFromPoint from the
      source center.
    - mismatch_animation applies to paired components with different
      shapes. It does not control how completely unmatched components
      are handled.
    - The extra keyword arguments are forwarded to component animations,
      but run_time and lag_ratio are passed separately to AnimationGroup.
    - The default matched_pairs argument is a mutable empty list. This
      implementation does not modify that list, but callers should
      generally prefer None or an immutable empty tuple in new APIs.
    - clean_up_from_scene() removes self.mobject and adds target after
      the parent cleanup. The exact relationship between self.mobject,
      source, and the animation group's assembled objects depends on the
      AnimationGroup implementation and should not be assumed to be a
      simple replacement in every custom subclass.
    - The source and target components should be structured so their
      point-bearing family members can be animated independently without
      unintended overlap or duplication.

    See Also
    --------
    AnimationGroup
        Runs multiple animations as a coordinated group.

    Transform
        Transforms one Mobject into another.

    FadeInFromPoint
        Introduces a Mobject by fading it in from a specified point.

    FadeOutToPoint
        Removes a Mobject by fading it toward a specified point.

    Mobject.family_members_with_points
        Retrieves family members that contain points.

    Mobject.has_same_shape_as
        Tests whether two Mobjects have matching shapes.
    """

    def __init__(
        self,
        source: Mobject,
        target: Mobject,
        matched_pairs: Iterable[tuple[Mobject, Mobject]] = [],
        match_animation: type = Transform,
        mismatch_animation: type = Transform,
        run_time: float = 2,
        lag_ratio: float = 0,
        **kwargs,
    ):
        self.source = source
        self.target = target
        self.match_animation = match_animation
        self.mismatch_animation = mismatch_animation
        self.anim_config = dict(**kwargs)

        # We will progressively build up a list of transforms
        # from pieces in source to those in target. These
        # two lists keep track of which pieces are accounted
        # for so far
        self.source_pieces = source.family_members_with_points()
        self.target_pieces = target.family_members_with_points()
        self.anims = []

        for pair in matched_pairs:
            self.add_transform(*pair)

        # Match any pairs with the same shape
        for pair in self.find_pairs_with_matching_shapes(self.source_pieces, self.target_pieces):
            self.add_transform(*pair)

        # Finally, account for mismatches
        for source_piece in self.source_pieces:
            if any([source_piece in anim.mobject.get_family() for anim in self.anims]):
                continue
            self.anims.append(FadeOutToPoint(
                source_piece, target.get_center(),
                **self.anim_config
            ))
        for target_piece in self.target_pieces:
            if any([target_piece in anim.mobject.get_family() for anim in self.anims]):
                continue
            self.anims.append(FadeInFromPoint(
                target_piece, source.get_center(),
                **self.anim_config
            ))

        super().__init__(
            *self.anims,
            run_time=run_time,
            lag_ratio=lag_ratio,
        )

    def add_transform(
        self,
        source: Mobject,
        target: Mobject,
    ):
        new_source_pieces = source.family_members_with_points()
        new_target_pieces = target.family_members_with_points()
        if len(new_source_pieces) == 0 or len(new_target_pieces) == 0:
            # Don't animate null sorces or null targets
            return
        source_is_new = all(char in self.source_pieces for char in new_source_pieces)
        target_is_new = all(char in self.target_pieces for char in new_target_pieces)
        if not source_is_new or not target_is_new:
            return

        transform_type = self.mismatch_animation
        if source.has_same_shape_as(target):
            transform_type = self.match_animation

        self.anims.append(transform_type(source, target, **self.anim_config))
        for char in new_source_pieces:
            self.source_pieces.remove(char)
        for char in new_target_pieces:
            self.target_pieces.remove(char)

    def find_pairs_with_matching_shapes(
        self,
        chars1: list[Mobject],
        chars2: list[Mobject]
    ) -> list[tuple[Mobject, Mobject]]:
        result = []
        for char1, char2 in it.product(chars1, chars2):
            if char1.has_same_shape_as(char2):
                result.append((char1, char2))
        return result

    def clean_up_from_scene(self, scene: Scene) -> None:
        super().clean_up_from_scene(scene)
        scene.remove(self.mobject)
        scene.add(self.target)


class TransformMatchingShapes(TransformMatchingParts):
    """Alias for TransformMatchingParts"""
    pass


class TransformMatchingStrings(TransformMatchingParts):
    def __init__(
        self,
        source: StringMobject,
        target: StringMobject,
        matched_keys: Iterable[str] = [],
        key_map: dict[str, str] = dict(),
        matched_pairs: Iterable[tuple[VMobject, VMobject]] = [],
        **kwargs,
    ):
        matched_pairs = [
            *matched_pairs,
            *self.matching_blocks(source, target, matched_keys, key_map),
        ]

        super().__init__(
            source, target,
            matched_pairs=matched_pairs,
            **kwargs,
        )

    def matching_blocks(
        self,
        source: StringMobject,
        target: StringMobject,
        matched_keys: Iterable[str],
        key_map: dict[str, str]
    ) -> list[tuple[VMobject, VMobject]]:
        syms1 = source.get_symbol_substrings()
        syms2 = target.get_symbol_substrings()
        counts1 = list(map(source.substr_to_path_count, syms1))
        counts2 = list(map(target.substr_to_path_count, syms2))

        # Start with user specified matches
        blocks = [(source[key1], target[key2]) for key1, key2 in key_map.items()]
        blocks += [(source[key], target[key]) for key in matched_keys]

        # Nullify any intersections with those matches in the two symbol lists
        for sub_source, sub_target in blocks:
            for i in range(len(syms1)):
                if i < len(source) and source[i] in sub_source.family_members_with_points():
                    syms1[i] = "Null1"
            for j in range(len(syms2)):
                if j < len(target) and target[j] in sub_target.family_members_with_points():
                    syms2[j] = "Null2"

        # Group together longest matching substrings
        while True:
            matcher = SequenceMatcher(None, syms1, syms2)
            match = matcher.find_longest_match(0, len(syms1), 0, len(syms2))
            if match.size == 0:
                break

            i1 = sum(counts1[:match.a])
            i2 = sum(counts2[:match.b])
            size = sum(counts1[match.a:match.a + match.size])

            blocks.append((source[i1:i1 + size], target[i2:i2 + size]))

            for i in range(match.size):
                syms1[match.a + i] = "Null1"
                syms2[match.b + i] = "Null2"

        return blocks


class TransformMatchingTex(TransformMatchingStrings):
    """Alias for TransformMatchingStrings"""
    pass
