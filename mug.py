#!/usr/bin/env python
# -*- coding: utf-8 -*-

from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from animation.continual_animation import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from topics.objects import *
from topics.probability import *
from topics.complex_numbers import *
from scene import Scene
from scene.reconfigurable_scene import ReconfigurableScene
from scene.zoomed_scene import *
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *
from topics.graph_scene import *

from old_projects.efvgt import ConfettiSpiril

#revert_to_original_skipping_status


class HappyHolidays(TeacherStudentsScene):
    def construct(self):
        hats = VGroup(*map(
            self.get_hat, self.pi_creatures
        ))
        self.add(self.get_snowflakes())
        self.change_student_modes(
            *["hooray"]*3,
            look_at_arg = SPACE_HEIGHT*UP,
            added_anims = [self.teacher.change, "hooray"]
        )
        self.play(LaggedStart(
            DrawBorderThenFill, hats
        ), Animation(self.pi_creatures))
        self.change_student_modes(
            "happy", "wave_2", "wave_1",
            look_at_arg = SPACE_HEIGHT*UP,
        )
        self.look_at(self.teacher.get_corner(UP+LEFT))
        self.dither(2)
        self.play(self.teacher.change, "happy")
        self.dither(2)

    def get_hat(self, pi):
        hat = SVGMobject(
            file_name = "santa_hat",
            height = 0.5*pi.get_height()
        )
        hat.rotate(-np.pi/12)
        vect = RIGHT
        if not pi.is_flipped():
            hat.flip()
            vect = LEFT
        hat.set_fill(RED_D)
        hat[0].remove(hat[0][1])
        hat[0].set_fill("#EEE")
        hat[2].set_fill(WHITE)
        hat.add(hat[0])
        hat.next_to(pi.body, UP, buff = SMALL_BUFF)
        hat.shift(SMALL_BUFF*vect)
        return hat

    def get_snowflakes(self, n_flakes = 50):
        snowflakes = VGroup(*[
            SVGMobject(
                file_name = "snowflake",
                height = 0.5,
                stroke_width = 0,
                fill_opacity = 0.75,
                fill_color = WHITE,
            ).rotate(np.pi/12, RIGHT)
            for x in range(n_flakes)
        ])
        def random_confetti_spiral(mob, **kwargs):
            return ConfettiSpiril(
                mob, x_start = 2*random.random()*SPACE_WIDTH - SPACE_WIDTH,
                **kwargs
            )
        snowflake_spirils = LaggedStart(
            random_confetti_spiral, snowflakes,
            run_time = 10,
            rate_func = lambda x : x,
        )
        return NormalAnimationAsContinualAnimation(snowflake_spirils)

class UtilitiesPuzzleScene(Scene):
    CONFIG = {
        "object_height" : 0.75,
        "h_distance" : 2,
        "v_distance" : 2,
        "line_width" : 4,
    }
    def setup_configuration(self):
        houses = VGroup()
        for x in range(3):
            house = SVGMobject(file_name = "house")
            house.scale_to_fit_height(self.object_height)
            house.set_fill(LIGHT_GREY)
            house.move_to(x*self.h_distance*RIGHT)
            houses.add(house)
        houses.move_to(self.v_distance*UP/2)

        utilities = VGroup(*[
            self.get_utility(u, c).move_to(x*self.h_distance*RIGHT)
            for x, u, c in zip(
                it.count(),
                ["fire", "electricity", "water"], 
                [RED_D, YELLOW_C, BLUE_D]
            )
        ])
        utilities.move_to(self.v_distance*DOWN/2)
        objects = VGroup(houses, utilities)
        bounding_box = SurroundingRectangle(
            objects,   
            buff = MED_LARGE_BUFF,
            stroke_width = 0
        )
        objects.add(bounding_box)
        self.add_foreground_mobjects(objects)
        self.set_variables_as_attrs(
            houses, utilities, objects, bounding_box
        )

    def get_utility(self, name, color):
        circle = Circle(
            fill_color = color,
            fill_opacity = 1,
            stroke_width = 0,
        )
        utility = SVGMobject(
            file_name = name,
            height = 0.65*circle.get_height(),
            fill_color = WHITE,
        )
        if color == YELLOW:
            utility.set_fill(DARK_GREY)
        utility.move_to(circle)
        circle.add(utility)
        circle.scale_to_fit_height(self.object_height)
        return circle

    def get_line(
        self, utility_index, house_index, 
        *midpoints,
        **kwargs
        ):
        prop = kwargs.pop("prop", 1.0)
        utility = self.utilities[utility_index]
        points = [utility.get_center()]
        points += list(midpoints)
        points += [self.houses[house_index].get_center()]
        line = Line(
            points[0], points[-1],
            color = utility[0].get_color(),
            stroke_width = self.line_width
        )
        line.set_points_smoothly(points)
        line.pointwise_become_partial(line, 0, prop)
        return line

    def get_almost_solution_lines(self):
        bb = self.bounding_box
        return VGroup(
            VGroup(
                self.get_line(0, 0),
                self.get_line(0, 1),
                self.get_line(0, 2, bb.get_top()),
            ),
            VGroup(
                self.get_line(1, 0, bb.get_corner(DOWN+LEFT)),
                self.get_line(1, 1),
                self.get_line(1, 2, bb.get_corner(DOWN+RIGHT)),
            ),
            VGroup(
                self.get_line(2, 0, bb.get_top()),
                self.get_line(2, 1),
                self.get_line(2, 2),
            ),
        )

    def get_straight_lines(self):
        return VGroup(*[
            VGroup(*[self.get_line(i, j) for j in range(3)])
            for i in range(3)
        ])

    def get_no_crossing_words(self):
        arrow = Vector(DOWN)
        arrow.next_to(self.bounding_box.get_top(), UP, SMALL_BUFF)
        words = TextMobject("No crossing!")
        words.next_to(arrow, UP, buff = SMALL_BUFF)
        result = VGroup(words, arrow)
        result.highlight("RED")
        return result

    def get_region(self, *bounding_edges):
        region = VMobject(mark_paths_closed = True)
        for i, edge in enumerate(bounding_edges):
            new_edge = edge.copy()
            if i%2 == 1:
                new_edge.points = new_edge.points[::-1]
            region.append_vectorized_mobject(new_edge)
        region.set_stroke(width = 0)
        region.set_fill(WHITE, opacity = 1)
        return region

    def convert_objects_to_dots(self, run_time = 2):
        group = VGroup(*it.chain(self.houses, self.utilities))
        for mob in group:
            mob.target = Dot(color = mob.get_color())
            mob.target.scale(2)
            mob.target.move_to(mob)
        self.play(LaggedStart(MoveToTarget, group, run_time = run_time))

class AboutToyPuzzles(UtilitiesPuzzleScene, TeacherStudentsScene, ThreeDScene):
    def construct(self):
        self.remove(self.pi_creatures)
        self.lay_out_puzzle()
        self.point_to_abstractions()
        self.show_this_video()

    def lay_out_puzzle(self):
        self.setup_configuration()
        houses, utilities = self.houses, self.utilities
        lines = VGroup(*it.chain(*self.get_almost_solution_lines()))
        no_crossing_words = self.get_no_crossing_words()

        self.remove(self.objects)
        self.play(
            ReplacementTransform(
                VGroup(houses[1], houses[1]).copy().fade(1),
                VGroup(houses[0], houses[2]),
                rate_func = squish_rate_func(smooth, 0.35, 1),
                run_time = 2,
            ),
            FadeIn(houses[1]),
            LaggedStart(DrawBorderThenFill, utilities, run_time = 2)
        )
        self.play(
            LaggedStart(
                ShowCreation, lines, 
                run_time = 3
            ),
            Animation(self.objects)
        )
        self.play(
            Write(no_crossing_words[0]),
            GrowArrow(no_crossing_words[1]),
        )
        self.dither()

        self.objects.add_to_back(lines, no_crossing_words)

    def point_to_abstractions(self):
        objects = self.objects
        objects.generate_target()
        objects.target.scale(0.5)
        objects.target.move_to(
            (SPACE_HEIGHT*DOWN + SPACE_WIDTH*LEFT)/2
        )

        eulers = TexMobject(*"V-E+F=2")
        eulers.highlight_by_tex_to_color_map({
            "V" : RED,
            "E" : GREEN,
            "F" : BLUE,
        })
        eulers.to_edge(UP, buff = 2)

        cube = Cube()
        cube.set_stroke(WHITE, 2)
        cube.scale_to_fit_height(0.75)
        cube.pose_at_angle()
        cube.next_to(eulers, UP)

        tda = TextMobject("Topological \\\\ Data Analysis")
        tda.move_to(DOWN + 4*RIGHT)

        arrow_from_eulers = Arrow(
            eulers.get_bottom(), tda.get_corner(UP+LEFT),
            color = WHITE
        )

        self.play(
            objects.scale, 0.5,
            objects.move_to, DOWN + 4*LEFT,
        )
        arrow_to_eulers = Arrow(
            self.houses[2].get_corner(UP+LEFT),
            eulers.get_bottom(),
            color = WHITE
        )
        self.add(AmbientRotation(cube, axis = UP))
        self.play(
            GrowArrow(arrow_to_eulers),
            Write(eulers),
            FadeIn(cube)
        )
        self.dither(5)
        self.play(
            GrowArrow(arrow_from_eulers),
            Write(tda)
        )
        self.dither(2)

        self.set_variables_as_attrs(
            eulers, cube, tda,
            arrows = VGroup(arrow_to_eulers, arrow_from_eulers),
        )

    def show_this_video(self):
        screen_rect = FullScreenFadeRectangle(
            stroke_color = WHITE,
            stroke_width = 2,
            fill_opacity = 0,
        )
        everything = VGroup(
            self.objects, self.arrows, self.eulers, 
            self.cube, self.tda,
            screen_rect,
        )

        self.teacher.save_state()
        self.teacher.fade(1)

        self.play(
            everything.scale, 0.5,
            everything.next_to, self.teacher, UP+LEFT,
            self.teacher.restore,
            self.teacher.change, "raise_right_hand", UP+LEFT,
            LaggedStart(FadeIn, self.students)
        )
        self.change_student_modes(
            *["pondering"]*3, look_at_arg = everything
        )
        self.dither(5)

class ThisPuzzleIsHard(UtilitiesPuzzleScene, PiCreatureScene):
    def construct(self):
        self.introduce_components()
        self.failed_attempts()
        self.ask_meta_puzzle()

    def introduce_components(self):
        randy = self.pi_creature

        try_it = TextMobject("Try it yourself!")
        try_it.to_edge(UP)

        self.setup_configuration()
        houses, utilities = self.houses, self.utilities
        self.remove(self.objects)
        house = houses[0]

        puzzle_words = TextMobject("""
            Puzzle: Connect each house to \\\\
            each utility without crossing lines.
        """)
        # puzzle_words.next_to(self.objects, UP)
        puzzle_words.to_edge(UP)

        self.add(try_it)
        self.play(Animation(try_it))
        self.play(
            LaggedStart(DrawBorderThenFill, houses),
            LaggedStart(GrowFromCenter, utilities),
            try_it.scale_to_fit_width, house.get_width(),
            try_it.fade, 1,
            try_it.move_to, house,
            self.pi_creature.change, "happy",
        )
        self.play(LaggedStart(FadeIn, puzzle_words))

        self.add_foreground_mobjects(self.objects)
        self.set_variables_as_attrs(puzzle_words)

    def failed_attempts(self):
        bb = self.bounding_box
        utilities = self.utilities
        houses = self.houses
        randy = self.pi_creature

        line_sets = [
            [
                self.get_line(0, 0),
                self.get_line(1, 1),
                self.get_line(2, 2),
                self.get_line(0, 1),
                self.get_line(2, 1),
                self.get_line(0, 2, bb.get_corner(UP+LEFT)),
                self.get_line(
                    2, 0, bb.get_corner(DOWN+LEFT),
                    prop = 0.85,
                ),
                self.get_line(
                    2, 0, bb.get_corner(UP+RIGHT), bb.get_top(),
                    prop = 0.73,
                ),
            ],
            [
                self.get_line(0, 0),
                self.get_line(1, 1),
                self.get_line(2, 2),
                self.get_line(0, 1),
                self.get_line(1, 2),
                self.get_line(
                    2, 0, 
                    bb.get_bottom(),
                    bb.get_corner(DOWN+LEFT)
                ),
                self.get_line(0, 2, bb.get_top()),
                self.get_line(
                    2, 1,
                    utilities[1].get_bottom() + MED_SMALL_BUFF*DOWN,
                    utilities[1].get_left() + MED_SMALL_BUFF*LEFT,
                ),
                self.get_line(
                    1, 0, houses[2].get_corner(UP+LEFT) + MED_LARGE_BUFF*LEFT,
                    prop = 0.49,
                ),
                self.get_line(
                    1, 2, bb.get_right(),
                    prop = 0.25,
                ),
            ],
            [
                self.get_line(0, 0),
                self.get_line(0, 1),
                self.get_line(0, 2, bb.get_top()),
                self.get_line(1, 0, bb.get_corner(DOWN+LEFT)),
                self.get_line(1, 1),
                self.get_line(1, 2, bb.get_corner(DOWN+RIGHT)),
                self.get_line(2, 1),
                self.get_line(2, 2),
                self.get_line(2, 0, bb.get_top(), prop = 0.45),
                self.get_line(2, 0, prop = 0.45),
            ],
        ]
        modes = ["confused", "sassy", "angry"]

        for line_set, mode in zip(line_sets, modes):
            good_lines = VGroup(*line_set[:-2])
            bad_lines = line_set[-2:]
            self.play(LaggedStart(ShowCreation, good_lines))
            for bl in bad_lines:
                self.play(
                    ShowCreation(
                        bl,
                        rate_func = bezier([0, 0, 0, 1, 1, 1, 1, 1, 0.3, 1, 1]),
                        run_time = 1.5
                    ),
                    randy.change, mode,
                )
                self.play(ShowCreation(
                    bl, rate_func = lambda t : smooth(1-t),
                ))
                self.remove(bl)
            self.play(LaggedStart(FadeOut, good_lines))

    def ask_meta_puzzle(self):
        randy = self.pi_creature
        group = VGroup(
            self.puzzle_words,
            self.objects,
        )
        rect = SurroundingRectangle(group, color = BLUE, buff = MED_LARGE_BUFF)
        group.add(rect)
        group.generate_target()
        group.target.scale(0.75)
        group.target.shift(DOWN)
        group[-1].set_stroke(width = 0)

        meta_puzzle_words = TextMobject("""
            Meta-puzzle: Prove that this\\\\
            is impossible.
        """)
        meta_puzzle_words.next_to(group.target, UP)
        meta_puzzle_words.highlight(BLUE)

        self.play(
            MoveToTarget(group),
            randy.change, "pondering"
        )
        self.play(Write(meta_puzzle_words))
        self.play(randy.change, "confused")

        straight_lines = self.get_straight_lines()
        almost_solution_lines = self.get_almost_solution_lines()
        self.play(LaggedStart(
            ShowCreation, straight_lines,
            run_time = 2,
            lag_ratio = 0.8
        ), Blink(randy))
        self.play(Transform(
            straight_lines, almost_solution_lines,
            run_time = 3,
            submobject_mode = "lagged_start"
        ))
        self.dither()

    ######

    def create_pi_creature(self):
        return Randolph().to_corner(DOWN+LEFT)

class IntroduceGraph(PiCreatureScene):
    def construct(self):
        pi_creatures = self.pi_creatures
        dots = VGroup(*[
            Dot(color = pi.get_color()).scale(2).move_to(pi)
            for pi in pi_creatures
        ])
        lines = VGroup(*[
            Line(pi1.get_center(), pi2.get_center())
            for pi1, pi2 in it.combinations(pi_creatures, 2)
        ])

        graph_word = TextMobject("``", "", "Graph", "''", arg_separator = "")
        graph_word.to_edge(UP)
        planar_graph_word = TextMobject("``", "Planar", " graph", "''", arg_separator = "")
        planar_graph_word.move_to(graph_word)

        vertices_word = TextMobject("Vertices")
        vertices_word.to_edge(RIGHT, buff = LARGE_BUFF)
        vertices_word.highlight(YELLOW)

        vertex_arrows = VGroup(*[
            Arrow(vertices_word.get_left(), dot)
            for dot in dots[-2:]
        ])

        edge_word = TextMobject("Edge")
        edge_word.next_to(lines, LEFT, LARGE_BUFF)
        edge_arrow = Arrow(
            edge_word, lines, buff = SMALL_BUFF,
            color = WHITE
        )

        self.play(LaggedStart(GrowFromCenter, pi_creatures))
        self.play(
            LaggedStart(ShowCreation, lines),
            LaggedStart(
                ApplyMethod, pi_creatures,
                lambda pi : (pi.change, "pondering", lines)
            )
        )
        self.play(Write(graph_word))
        self.play(ReplacementTransform(
            pi_creatures, dots,
            run_time = 2,
            submobject_mode = "lagged_start"
        ))
        self.add_foreground_mobjects(dots)
        self.play(
            FadeIn(vertex_arrows),
            FadeIn(vertices_word),
        )
        self.dither()
        self.play(LaggedStart(
            ApplyMethod, lines,
            lambda l : (l.rotate_in_place, np.pi/12),
            rate_func = wiggle
        ))
        self.play(
            FadeIn(edge_word),
            GrowArrow(edge_arrow),
        )
        self.dither(2)
        line = lines[2]
        self.play(
            line.set_points_smoothly, [
                line.get_start(),
                dots.get_left() + MED_SMALL_BUFF*LEFT,
                dots.get_corner(DOWN+LEFT) + MED_SMALL_BUFF*(DOWN+LEFT),
                dots.get_bottom() + MED_SMALL_BUFF*DOWN,
                line.get_end(),
            ],
            VGroup(edge_word, edge_arrow).shift, MED_LARGE_BUFF*LEFT,
        )
        self.dither()
        self.play(ReplacementTransform(graph_word, planar_graph_word))
        self.dither(2)

    ###

    def create_pi_creatures(self):
        pis = VGroup(
            PiCreature(color = BLUE_D),
            PiCreature(color = GREY_BROWN),
            PiCreature(color = BLUE_C).flip(),
            PiCreature(color = BLUE_E).flip(),
        )
        pis.scale(0.5)
        pis.arrange_submobjects_in_grid(buff = 2)
        return pis

class IsK33Planar(UtilitiesPuzzleScene):
    def construct(self):
        self.setup_configuration()
        self.objects.shift(MED_LARGE_BUFF*DOWN)

        straight_lines = self.get_straight_lines()
        almost_solution_lines = self.get_almost_solution_lines()

        question = TextMobject("Is", "this graph", "planar?")
        question.highlight_by_tex("this graph", YELLOW)
        question.to_edge(UP)
        brace = Brace(question.get_part_by_tex("graph"), DOWN, buff = SMALL_BUFF)
        fancy_name = brace.get_text(
            "``Complete bipartite graph $K_{3, 3}$''",
            buff = SMALL_BUFF
        )
        fancy_name.highlight(YELLOW)

        self.add(question)
        self.convert_objects_to_dots()
        self.play(LaggedStart(ShowCreation, straight_lines))
        self.play(
            GrowFromCenter(brace),
            LaggedStart(FadeIn, fancy_name),
        )
        self.play(ReplacementTransform(
            straight_lines, almost_solution_lines,
            run_time = 3,
            submobject_mode = "lagged_start"
        ))
        self.dither(2)

class TwoKindsOfViewers(PiCreatureScene, UtilitiesPuzzleScene):
    def construct(self):
        self.setup_configuration()
        objects = self.objects
        objects.remove(self.bounding_box)
        lines = self.get_straight_lines()
        objects.add_to_back(lines)
        objects.scale(0.75)
        objects.next_to(ORIGIN, RIGHT, LARGE_BUFF)
        self.remove(objects)

        pi1, pi2 = self.pi_creatures
        words = TextMobject(
            "$(V-E+F)$", "kinds of viewers"
        )
        words.to_edge(UP)
        eulers = words.get_part_by_tex("V-E+F")
        eulers.highlight(GREEN)
        non_eulers = VGroup(*filter(lambda m : m is not eulers, words))

        self.add(words)
        self.dither()
        self.play(
            pi1.shift, 2*LEFT,
            pi2.shift, 2*RIGHT,
        )

        know_eulers = TextMobject("Know about \\\\ Euler's formula")
        know_eulers.next_to(pi1, DOWN)
        know_eulers.highlight(GREEN)
        dont = TextMobject("Don't")
        dont.next_to(pi2, DOWN)
        dont.highlight(RED)

        self.play(
            FadeIn(know_eulers),
            pi1.change, "hooray",
        )
        self.play(
            FadeIn(dont),
            pi2.change, "maybe", eulers,
        )
        self.dither()
        self.pi_creature_thinks(
            pi1, "",
            bubble_kwargs = {"width" : 3, "height" : 2},
            target_mode = "thinking"
        )
        self.play(pi2.change, "confused", eulers)
        self.dither()

        ### Out of thin air
        self.play(*map(FadeOut, [
            non_eulers, pi1, pi2, pi1.bubble,
            know_eulers, dont
        ]))
        self.play(eulers.next_to, ORIGIN, LEFT, LARGE_BUFF)
        arrow = Arrow(eulers, objects, color = WHITE)
        self.play(
            GrowArrow(arrow),
            LaggedStart(DrawBorderThenFill, VGroup(*it.chain(*objects)))
        )
        self.dither()
        self.play(
            objects.move_to, eulers, RIGHT,
            eulers.move_to, objects, LEFT,
            path_arc = np.pi,
            run_time = 1.5,
        )
        self.dither(2)

    ###

    def create_pi_creatures(self):
        group = VGroup(Randolph(color = BLUE_C), Randolph())
        group.scale(0.7)
        group.shift(MED_LARGE_BUFF*DOWN)
        return group

class IntroduceRegions(UtilitiesPuzzleScene):
    def construct(self):
        self.setup_configuration()
        houses, utilities = self.houses, self.utilities
        objects = self.objects
        lines, line_groups, regions = self.get_lines_line_groups_and_regions()
        back_region = regions[0]
        front_regions = VGroup(*regions[1:])

        self.convert_objects_to_dots(run_time = 0)
        self.play(LaggedStart(
            ShowCreation, lines,
            run_time = 3,
        ))
        self.add_foreground_mobjects(lines, objects)
        self.dither()
        for region in front_regions:
            self.play(FadeIn(region))
        self.play(
            FadeIn(back_region),
            Animation(front_regions),
        )
        self.dither()
        self.play(FadeOut(regions))

        ##Paint bucket
        paint_bucket = SVGMobject(
            file_name = "paint_bucket",
            height = 0.5,
        )
        paint_bucket.flip()
        paint_bucket.move_to(8*LEFT + 5*UP)

        def click(region):
            self.play(
                UpdateFromAlphaFunc(
                    region,
                    lambda m, a : m.set_fill(opacity = int(2*a)),
                ),
                ApplyMethod(
                    paint_bucket.scale_in_place, 0.5,
                    rate_func = there_and_back,
                ),
                run_time = 0.25,
            )

        self.play(
            paint_bucket.next_to, utilities, DOWN+LEFT, SMALL_BUFF
        )
        click(regions[1])
        self.play(paint_bucket.next_to, utilities[1], UP+RIGHT, SMALL_BUFF)
        click(regions[2])
        self.play(paint_bucket.next_to, houses[1], RIGHT)
        click(regions[3])
        self.play(paint_bucket.move_to, 4*LEFT + 2*UP)
        self.add_foreground_mobjects(front_regions, lines, objects)
        click(back_region)
        self.remove_foreground_mobjects(front_regions)
        self.dither()
        self.play(
            FadeOut(back_region),
            FadeOut(front_regions[0]),
            FadeOut(paint_bucket),
            *map(Animation, front_regions[1:])
        )

        #Line tries to escape
        point_sets = [
            [
                VGroup(*houses[1:]).get_center(),
                houses[2].get_top() + MED_SMALL_BUFF*UP,
            ],
            [
                houses[1].get_top() + SMALL_BUFF*UP,
                utilities[0].get_center(),
            ],
            [VGroup(houses[1], utilities[1]).get_center()],
            [
                utilities[2].get_center() + 0.75*(DOWN+RIGHT)
            ],
        ]
        escape_lines = VGroup(*[
            Line(LEFT, RIGHT).set_points_smoothly(
                [utilities[2].get_center()] + point_set
            )
            for point_set in point_sets
        ])

        self.dither()
        for line in escape_lines:
            self.play(ShowCreation(line,
                rate_func = lambda t : 0.8*smooth(t)
            ))
            self.play(ShowCreation(line,
                rate_func = lambda t : smooth(1 - t)
            ))

    def get_lines_line_groups_and_regions(self):
        lines = self.get_almost_solution_lines()
        flat_lines = VGroup(*it.chain(*lines))
        flat_lines.remove(lines[2][0])

        line_groups = [
            VGroup(*[lines[i][j] for i, j in ij_set])
            for ij_set in [
                [(0, 0), (1, 0), (1, 1), (0, 1)],
                [(1, 1), (2, 1), (2, 2), (1, 2)],
                [(0, 2), (2, 2), (2, 1), (0, 1)],
                [(0, 0), (1, 0), (1, 2), (0, 2)],
            ]
        ]
        regions = VGroup(*[
            self.get_region(*line_group)
            for line_group in line_groups
        ])
        back_region = FullScreenFadeRectangle(fill_opacity = 1 )
        regions.submobjects.pop()
        regions.submobjects.insert(0, back_region)
        front_regions = VGroup(*regions[1:])

        back_region.highlight(BLUE_E)
        front_regions.gradient_highlight(GREEN_E, MAROON_E)

        return flat_lines, line_groups, regions

class FromLastVideo(Scene):
    def construct(self):
        title = TextMobject("From last video")
        title.to_edge(UP)
        rect = ScreenRectangle(height = 6)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.dither(2)

class AskAboutRegions(IntroduceRegions):
    def construct(self):
        self.setup_configuration()
        houses, utilities = self.houses, self.utilities
        self.convert_objects_to_dots(run_time = 0)
        objects = self.objects
        lines, line_groups, regions = self.get_lines_line_groups_and_regions()
        back_region = regions[0]
        front_regions = VGroup(*regions[1:])
        missing_lines = VGroup(
            self.get_line(2, 0, self.objects.get_top()),
            self.get_line(
                2, 0, 
                self.objects.get_bottom() + DOWN,
                self.objects.get_corner(DOWN+LEFT) + DOWN+LEFT,
            )
        )
        missing_lines.set_stroke(width = 5)

        front_regions.save_state()
        front_regions.generate_target()
        front_regions.target.scale(0.5)
        front_regions.target.arrange_submobjects(RIGHT, buff = LARGE_BUFF)
        front_regions.target.to_edge(UP)

        self.add(front_regions)
        self.add_foreground_mobjects(lines, objects)
        self.dither()
        self.play(MoveToTarget(front_regions))
        self.play(LaggedStart(
            ApplyMethod, front_regions,
            lambda m : (m.rotate_in_place, np.pi/12),
            rate_func = wiggle,
            lag_ratio = 0.75,
            run_time = 1
        ))
        self.play(front_regions.restore)
        self.dither()

        #Show missing lines
        for line in missing_lines:
            self.play(ShowCreation(
                line,
                rate_func = there_and_back,
                run_time = 2,
            ))

        #Count regions
        count = TexMobject("1")
        count.scale(1.5)
        count.to_edge(UP)
        self.play(
            FadeIn(back_region), 
            FadeIn(count),
            Animation(front_regions)
        )
        last_region = None
        for n, region in zip(it.count(2), front_regions):
            new_count = TexMobject(str(n))
            new_count.replace(count, dim_to_match = 1)
            self.remove(count)
            self.add(new_count)
            count = new_count

            region.save_state()
            anims = [ApplyMethod(region.highlight, YELLOW)]
            if last_region:
                anims.append(ApplyMethod(last_region.restore))
            anims.append(Animation(front_regions))
            self.play(*anims, run_time = 0.25)
            self.dither(0.5)
            last_region = region
        self.play(last_region.restore)
        self.dither()
        self.play(FadeOut(count))

        #Count edges per region
        fade_rect = FullScreenFadeRectangle(opacity = 0.8)
        line_group = line_groups[0].copy()
        region = front_regions[0].copy()
        self.foreground_mobjects = []
        def show_lines(line_group):
            lg_copy = line_group.copy()
            lg_copy.set_stroke(WHITE, 6)
            self.play(LaggedStart(
                FadeIn, lg_copy,
                run_time = 3,
                rate_func = there_and_back,
                lag_ratio = 0.4,
                remover = True,
            ))

        self.play(
            FadeIn(fade_rect),
            Animation(region),
            Animation(line_group),
        )
        show_lines(line_group)
        last_line_group = line_group
        last_region = region
        for i in range(1, 3):
            line_group = line_groups[i].copy()
            region = front_regions[i].copy()
            self.play(
                FadeOut(last_region),
                FadeOut(last_line_group),
                FadeIn(region),
                FadeIn(line_group),
            )
            show_lines(line_group)
            last_line_group = line_group
            last_region = region
        self.play(
            FadeOut(fade_rect),
            FadeOut(last_region),
            FadeOut(last_line_group),
        )
        self.dither()

class NewRegionClosedOnlyForNodesWithEdges(UtilitiesPuzzleScene):
    def construct(self):
        self.setup_configuration()
        self.convert_objects_to_dots(run_time = 0)
        objects = self.objects
        houses, utilities = self.houses, self.utilities

        bb = self.bounding_box
        lines = VGroup(
            self.get_line(2, 1),
            self.get_line(0, 1),
            self.get_line(0, 2,
                bb.get_corner(UP+LEFT),
                bb.get_top() + MED_LARGE_BUFF*UP,
            ),
            self.get_line(2, 2),
        )
        lit_line = lines[2].copy()
        lit_line.points = lit_line.points[::-1]
        lit_line.set_stroke(WHITE, 5)

        region = self.get_region(*lines)
        region.set_fill(MAROON_E)

        arrow = Vector(DOWN+LEFT, color = WHITE)
        arrow.next_to(houses[2], UP+RIGHT, buff = SMALL_BUFF)
        words = TextMobject("Already has \\\\ an edge")
        words.next_to(arrow.get_start(), UP, SMALL_BUFF)

        for line in lines[:-1]:
            self.play(ShowCreation(line))
        lines[-1].pointwise_become_partial(lines[-1], 0, 0.92)
        lines[-1].save_state()
        self.dither()
        self.play(ShowCreation(lines[-1]))
        self.add(region, lines, objects)
        self.dither()
        self.remove(region)
        self.play(ShowCreation(lines[-1], 
            rate_func = lambda t : smooth(1-2*t*(1-t))
        ))
        self.add(region, lines, objects)
        self.dither()
        self.remove(region)
        self.play(
            ShowCreation(lines[-1],
                rate_func = lambda t : smooth(1-0.5*t)
            ),
            FadeIn(words),
            GrowArrow(arrow),
        )
        for x in range(2):
            self.play(ShowCreationThenDestruction(lit_line))
        self.play(lines[-1].restore)
        self.add(region, lines, objects)
        self.dither(2)

class LightUpNodes(IntroduceRegions):
    def construct(self):
        self.setup_configuration()
        self.setup_regions()
        self.setup_counters()
        self.describe_one_as_lit()
        self.show_rule_for_lighting()

    def setup_configuration(self):
        IntroduceRegions.setup_configuration(self)
        self.convert_objects_to_dots(run_time = 1)
        self.objects.shift(DOWN)

    def setup_regions(self):
        lines, line_groups, regions = self.get_lines_line_groups_and_regions()
        back_region = regions[0]
        front_regions = VGroup(*regions[1:])
        self.set_variables_as_attrs(
            lines, line_groups, regions,
            back_region, front_regions,
        )

    def setup_counters(self):
        titles = [
            TextMobject("\\# Lit vertices"),
            TextMobject("\\# Edges"),
            TextMobject("\\# Regions"),
        ]
        for title, vect in zip(titles, [LEFT, ORIGIN, RIGHT]):
            title.shift(SPACE_WIDTH*vect/2)
            title.to_edge(UP)
            underline = Line(LEFT, RIGHT)
            underline.stretch_to_fit_width(title.get_width())
            underline.next_to(title, DOWN, SMALL_BUFF)
            title.add(underline)
            self.add(title)
        self.v_count, self.e_count, self.f_count = self.counts = map(
            Integer, [1, 0, 1]
        )
        for count, title in zip(self.counts, titles):
            count.next_to(title, DOWN)
            self.add(count)

    def describe_one_as_lit(self):
        houses, utilities = self.houses, self.utilities
        vertices = VGroup(*it.chain(houses, utilities))
        dim_arrows = VGroup()
        for vertex in vertices:
            arrow = Vector(0.5*(DOWN+LEFT), color = WHITE)
            arrow.next_to(vertex, UP+RIGHT, SMALL_BUFF)
            vertex.arrow = arrow
            dim_arrows.add(arrow)
        lit_vertex = utilities[0]
        lit_arrow = lit_vertex.arrow
        lit_arrow.rotate(np.pi/2, about_point = lit_vertex.get_center())
        dim_arrows.remove(lit_arrow)
        lit_word = TextMobject("Lit up")
        lit_word.next_to(lit_arrow.get_start(), UP, SMALL_BUFF)
        dim_word = TextMobject("Dim")
        dim_word.next_to(dim_arrows[1].get_start(), UP, MED_LARGE_BUFF)

        dot = Dot().move_to(self.v_count)

        self.play(
            vertices.set_fill, None, 0,
            vertices.set_stroke, None, 1,
        )
        self.play(ReplacementTransform(dot, lit_vertex))
        self.play(
            FadeIn(lit_word),
            GrowArrow(lit_arrow)
        )
        self.play(*self.get_lit_vertex_animations(lit_vertex))
        self.play(
            FadeIn(dim_word),
            LaggedStart(GrowArrow, dim_arrows)
        )
        self.dither()
        self.play(*map(FadeOut, [
            lit_word, lit_arrow, dim_word, dim_arrows
        ]))

    def show_rule_for_lighting(self):
        lines = self.lines
        regions = self.regions
        line_groups = self.line_groups
        objects = self.objects
        houses, utilities = self.houses, self.utilities

        #First region, lines 0, 1, 4, 3
        lines[4].rotate_in_place(np.pi)
        region = regions[1]

        self.play(ShowCreation(lines[0]))
        self.play(*self.get_count_change_animations(0, 1, 0))
        self.play(*it.chain(
            self.get_lit_vertex_animations(houses[0]),
            self.get_count_change_animations(1, 0, 0)
        ))
        self.dither()
        for line, vertex in (lines[1], houses[1]), (lines[4], utilities[1]):
            self.play(
                ShowCreation(line),
                *self.get_count_change_animations(0, 1, 0)
            )
            self.play(*it.chain(
                self.get_lit_vertex_animations(vertex),
                self.get_count_change_animations(1, 0, 0),
            ))
        self.dither()
        self.play(
            ShowCreation(lines[3], run_time = 2),
            *self.get_count_change_animations(0, 1, 0)
        )
        self.add_foreground_mobjects(line_groups[0])
        self.add_foreground_mobjects(objects)
        self.play(
            FadeIn(region),
            *self.get_count_change_animations(0, 0, 1)
        )
        self.dither()

        #Next region, lines 2, 7, 8
        region = regions[3]
        lines[6].rotate_in_place(np.pi)

        for line, vertex in (lines[2], houses[2]), (lines[6], utilities[2]):
            self.play(ShowCreation(line), *it.chain(
                self.get_lit_vertex_animations(
                    vertex,
                    run_time = 2, 
                    squish_range = (0.5, 1),
                ),
                self.get_count_change_animations(1, 1, 0)
            ))
        self.dither()
        self.play(
            ShowCreation(lines[7]),
            *self.get_count_change_animations(0, 1, 1)
        )
        self.add_foreground_mobjects(line_groups[2])
        self.add_foreground_mobjects(objects)
        self.play(FadeIn(region))
        self.dither()

    ####

    def get_count_change_animations(self, *changes):
        anims = []
        for change, count in zip(changes, self.counts):
            if change == 0:
                continue
            new_count = Integer(count.number + 1)
            new_count.move_to(count)
            anims.append(Transform(
                count, new_count,
                run_time = 2,
                rate_func = squish_rate_func(smooth, 0.5, 1)
            ))
            count.number += 1
            anims.append(self.get_plus_one_anim(count))

        return anims

    def get_plus_one_anim(self, count):
        plus_one = TexMobject("+1")
        plus_one.highlight(YELLOW)
        plus_one.move_to(count)
        plus_one.next_to(count, DOWN)
        plus_one.generate_target()
        plus_one.target.move_to(count)
        plus_one.target.set_fill(opacity = 0)
        move = MoveToTarget(plus_one, remover = True)
        grow = GrowFromCenter(plus_one)
        return UpdateFromAlphaFunc(
            plus_one,
            lambda m, a : (
                (grow if a < 0.5 else move).update(2*a%1)
            ),
            remover = True,
            rate_func = double_smooth,
            run_time = 2
        )

    def get_lit_vertex_animations(self, vertex, run_time = 1, squish_range = (0, 1)):
        line = Line(
            LEFT, RIGHT,
            stroke_width = 0,
            stroke_color = BLACK,
        )
        line.scale_to_fit_width(0.5*vertex.get_width())
        line.next_to(ORIGIN, buff = 0.75*vertex.get_width())
        lines = VGroup(*[
            line.copy().rotate(angle)
            for angle in np.arange(0, 2*np.pi, np.pi/4)
        ])
        lines.move_to(vertex)
        random.shuffle(lines.submobjects)
        return [
            LaggedStart(
                ApplyMethod, lines,
                lambda l : (l.set_stroke, YELLOW, 4),
                rate_func = squish_rate_func(there_and_back, *squish_range),
                lag_ratio = 0.75,
                remover = True,
                run_time = run_time
            ),
            ApplyMethod(
                vertex.set_fill, None, 1,
                run_time = run_time,
                rate_func = squish_rate_func(smooth, *squish_range)
            ),
        ]

class ShowRule(TeacherStudentsScene):
    def construct(self):
        new_edge = TextMobject("New edge")
        new_vertex = TextMobject("New (lit) vertex")
        new_vertex.next_to(new_edge, UP+RIGHT, MED_LARGE_BUFF)
        new_region = TextMobject("New region")
        new_region.next_to(new_edge, DOWN+RIGHT, MED_LARGE_BUFF)
        VGroup(new_vertex, new_region).shift(MED_LARGE_BUFF*RIGHT)
        arrows = VGroup(*[
            Arrow(
                new_edge.get_right(), mob.get_left(), 
                color = WHITE,
                buff = SMALL_BUFF
            )
            for mob in new_vertex, new_region
        ])
        new_vertex.highlight(YELLOW)
        new_edge.highlight(BLUE)
        new_region.highlight(RED)
        rule = VGroup(new_edge, arrows, new_vertex, new_region)
        rule.center().to_edge(UP)

        self.add(rule)

class ConcludeFiveRegions(LightUpNodes):
    def construct(self):
        self.setup_configuration()
        self.setup_regions()
        self.setup_counters()
        self.show_new_region_creation()
        self.show_rule()
        self.show_nine_lines_to_start()
        self.conclude_about_five_regions()






















