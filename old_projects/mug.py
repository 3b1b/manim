#!/usr/bin/env python
# -*- coding: utf-8 -*-

from manimlib.imports import *
from old_projects.efvgt import ConfettiSpiril

#revert_to_original_skipping_status


class HappyHolidays(TeacherStudentsScene):
    def construct(self):
        hats = VGroup(*list(map(
            self.get_hat, self.pi_creatures
        )))
        self.add(self.get_snowflakes())
        self.change_student_modes(
            *["hooray"]*3,
            look_at_arg = FRAME_Y_RADIUS*UP,
            added_anims = [self.teacher.change, "hooray"]
        )
        self.play(LaggedStartMap(
            DrawBorderThenFill, hats
        ), Animation(self.pi_creatures))
        self.change_student_modes(
            "happy", "wave_2", "wave_1",
            look_at_arg = FRAME_Y_RADIUS*UP,
        )
        self.look_at(self.teacher.get_corner(UP+LEFT))
        self.wait(2)
        self.play(self.teacher.change, "happy")
        self.wait(2)

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
                mob, x_start = 2*random.random()*FRAME_X_RADIUS - FRAME_X_RADIUS,
                **kwargs
            )
        snowflake_spirils = LaggedStartMap(
            random_confetti_spiral, snowflakes,
            run_time = 10,
            rate_func = lambda x : x,
        )
        return turn_animation_into_updater(snowflake_spirils)

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
            house.set_height(self.object_height)
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
        circle.set_height(self.object_height)
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
        result.set_color("RED")
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
        self.play(LaggedStartMap(MoveToTarget, group, run_time = run_time))

class PauseIt(PiCreatureScene):
    def construct(self):
        morty = self.pi_creatures
        morty.center().to_edge(DOWN)
        self.pi_creature_says(
            "Pause it!", target_mode = "surprised"
        )
        self.wait(2)
        
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
            LaggedStartMap(DrawBorderThenFill, utilities, run_time = 2)
        )
        self.play(
            LaggedStartMap(
                ShowCreation, lines, 
                run_time = 3
            ),
            Animation(self.objects)
        )
        self.play(
            Write(no_crossing_words[0]),
            GrowArrow(no_crossing_words[1]),
        )
        self.wait()

        self.objects.add_to_back(lines, no_crossing_words)

    def point_to_abstractions(self):
        objects = self.objects
        objects.generate_target()
        objects.target.scale(0.5)
        objects.target.move_to(
            (FRAME_Y_RADIUS*DOWN + FRAME_X_RADIUS*LEFT)/2
        )

        eulers = TexMobject(*"V-E+F=2")
        eulers.set_color_by_tex_to_color_map({
            "V" : RED,
            "E" : GREEN,
            "F" : BLUE,
        })
        eulers.to_edge(UP, buff = 2)

        cube = Cube()
        cube.set_stroke(WHITE, 2)
        cube.set_height(0.75)
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
        always_rotate(cube, axis=UP)
        self.play(
            GrowArrow(arrow_to_eulers),
            Write(eulers),
            FadeIn(cube)
        )
        self.wait(5)
        self.play(
            GrowArrow(arrow_from_eulers),
            Write(tda)
        )
        self.wait(2)

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
            LaggedStartMap(FadeIn, self.students)
        )
        self.change_student_modes(
            *["pondering"]*3, look_at_arg = everything
        )
        self.wait(5)

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
            LaggedStartMap(DrawBorderThenFill, houses),
            LaggedStartMap(GrowFromCenter, utilities),
            try_it.set_width, house.get_width(),
            try_it.fade, 1,
            try_it.move_to, house,
            self.pi_creature.change, "happy",
        )
        self.play(LaggedStartMap(FadeIn, puzzle_words))

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
            self.play(LaggedStartMap(ShowCreation, good_lines))
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
            self.play(LaggedStartMap(FadeOut, good_lines))

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
        meta_puzzle_words.set_color(BLUE)

        self.play(
            MoveToTarget(group),
            randy.change, "pondering"
        )
        self.play(Write(meta_puzzle_words))
        self.play(randy.change, "confused")

        straight_lines = self.get_straight_lines()
        almost_solution_lines = self.get_almost_solution_lines()
        self.play(LaggedStartMap(
            ShowCreation, straight_lines,
            run_time = 2,
            lag_ratio = 0.8
        ), Blink(randy))
        self.play(Transform(
            straight_lines, almost_solution_lines,
            run_time = 3,
            lag_ratio = 0.5
        ))
        self.wait()

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
        vertices_word.set_color(YELLOW)

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

        self.play(LaggedStartMap(GrowFromCenter, pi_creatures))
        self.play(
            LaggedStartMap(ShowCreation, lines),
            LaggedStartMap(
                ApplyMethod, pi_creatures,
                lambda pi : (pi.change, "pondering", lines)
            )
        )
        self.play(Write(graph_word))
        self.play(ReplacementTransform(
            pi_creatures, dots,
            run_time = 2,
            lag_ratio = 0.5
        ))
        self.add_foreground_mobjects(dots)
        self.play(
            FadeIn(vertex_arrows),
            FadeIn(vertices_word),
        )
        self.wait()
        self.play(LaggedStartMap(
            ApplyMethod, lines,
            lambda l : (l.rotate_in_place, np.pi/12),
            rate_func = wiggle
        ))
        self.play(
            FadeIn(edge_word),
            GrowArrow(edge_arrow),
        )
        self.wait(2)
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
        self.wait()
        self.play(ReplacementTransform(graph_word, planar_graph_word))
        self.wait(2)

    ###

    def create_pi_creatures(self):
        pis = VGroup(
            PiCreature(color = BLUE_D),
            PiCreature(color = GREY_BROWN),
            PiCreature(color = BLUE_C).flip(),
            PiCreature(color = BLUE_E).flip(),
        )
        pis.scale(0.5)
        pis.arrange_in_grid(buff = 2)
        return pis

class IsK33Planar(UtilitiesPuzzleScene):
    def construct(self):
        self.setup_configuration()
        self.objects.shift(MED_LARGE_BUFF*DOWN)

        straight_lines = self.get_straight_lines()
        almost_solution_lines = self.get_almost_solution_lines()

        question = TextMobject("Is", "this graph", "planar?")
        question.set_color_by_tex("this graph", YELLOW)
        question.to_edge(UP)
        brace = Brace(question.get_part_by_tex("graph"), DOWN, buff = SMALL_BUFF)
        fancy_name = brace.get_text(
            "``Complete bipartite graph $K_{3, 3}$''",
            buff = SMALL_BUFF
        )
        fancy_name.set_color(YELLOW)

        self.add(question)
        self.convert_objects_to_dots()
        self.play(LaggedStartMap(ShowCreation, straight_lines))
        self.play(
            GrowFromCenter(brace),
            LaggedStartMap(FadeIn, fancy_name),
        )
        self.play(ReplacementTransform(
            straight_lines, almost_solution_lines,
            run_time = 3,
            lag_ratio = 0.5
        ))
        self.wait(2)

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
        eulers.set_color(GREEN)
        non_eulers = VGroup(*[m for m in words if m is not eulers])

        self.add(words)
        self.wait()
        self.play(
            pi1.shift, 2*LEFT,
            pi2.shift, 2*RIGHT,
        )

        know_eulers = TextMobject("Know about \\\\ Euler's formula")
        know_eulers.next_to(pi1, DOWN)
        know_eulers.set_color(GREEN)
        dont = TextMobject("Don't")
        dont.next_to(pi2, DOWN)
        dont.set_color(RED)

        self.play(
            FadeIn(know_eulers),
            pi1.change, "hooray",
        )
        self.play(
            FadeIn(dont),
            pi2.change, "maybe", eulers,
        )
        self.wait()
        self.pi_creature_thinks(
            pi1, "",
            bubble_kwargs = {"width" : 3, "height" : 2},
            target_mode = "thinking"
        )
        self.play(pi2.change, "confused", eulers)
        self.wait()

        ### Out of thin air
        self.play(*list(map(FadeOut, [
            non_eulers, pi1, pi2, pi1.bubble,
            know_eulers, dont
        ])))
        self.play(eulers.next_to, ORIGIN, LEFT, LARGE_BUFF)
        arrow = Arrow(eulers, objects, color = WHITE)
        self.play(
            GrowArrow(arrow),
            LaggedStartMap(DrawBorderThenFill, VGroup(*it.chain(*objects)))
        )
        self.wait()
        self.play(
            objects.move_to, eulers, RIGHT,
            eulers.move_to, objects, LEFT,
            path_arc = np.pi,
            run_time = 1.5,
        )
        self.wait(2)

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
        self.play(LaggedStartMap(
            ShowCreation, lines,
            run_time = 3,
        ))
        self.add_foreground_mobjects(lines, objects)
        self.wait()
        for region in front_regions:
            self.play(FadeIn(region))
        self.play(
            FadeIn(back_region),
            Animation(front_regions),
        )
        self.wait()
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
        self.wait()
        self.play(
            FadeOut(back_region),
            FadeOut(front_regions[0]),
            FadeOut(paint_bucket),
            *list(map(Animation, front_regions[1:]))
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

        self.wait()
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

        back_region.set_color(BLUE_E)
        front_regions.set_color_by_gradient(GREEN_E, MAROON_E)

        return flat_lines, line_groups, regions

class FromLastVideo(Scene):
    def construct(self):
        title = TextMobject("From last video")
        title.to_edge(UP)
        rect = ScreenRectangle(height = 6)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait(2)

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
        front_regions.target.arrange(RIGHT, buff = LARGE_BUFF)
        front_regions.target.to_edge(UP)

        self.add(front_regions)
        self.add_foreground_mobjects(lines, objects)
        self.wait()
        self.play(MoveToTarget(front_regions))
        self.play(LaggedStartMap(
            ApplyMethod, front_regions,
            lambda m : (m.rotate_in_place, np.pi/12),
            rate_func = wiggle,
            lag_ratio = 0.75,
            run_time = 1
        ))
        self.play(front_regions.restore)
        self.wait()

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
            anims = [ApplyMethod(region.set_color, YELLOW)]
            if last_region:
                anims.append(ApplyMethod(last_region.restore))
            anims.append(Animation(front_regions))
            self.play(*anims, run_time = 0.25)
            self.wait(0.5)
            last_region = region
        self.play(last_region.restore)
        self.wait()
        self.play(FadeOut(count))

        #Count edges per region
        fade_rect = FullScreenFadeRectangle(opacity = 0.8)
        line_group = line_groups[0].copy()
        region = front_regions[0].copy()
        self.foreground_mobjects = []
        def show_lines(line_group):
            lg_copy = line_group.copy()
            lg_copy.set_stroke(WHITE, 6)
            self.play(LaggedStartMap(
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
        self.wait()

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
        self.wait()
        self.play(ShowCreation(lines[-1]))
        self.add(region, lines, objects)
        self.wait()
        self.remove(region)
        self.play(ShowCreation(lines[-1], 
            rate_func = lambda t : smooth(1-2*t*(1-t))
        ))
        self.add(region, lines, objects)
        self.wait()
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
        self.wait(2)

class LightUpNodes(IntroduceRegions):
    CONFIG = {
        "vertices_word" : "Lit vertices",
    }
    def construct(self):
        self.setup_configuration()
        self.setup_regions()
        self.setup_counters()
        self.describe_one_as_lit()
        self.show_rule_for_lighting()

    def setup_configuration(self):
        IntroduceRegions.setup_configuration(self)
        self.convert_objects_to_dots(run_time = 0)
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
            TextMobject("\\# %s"%self.vertices_word),
            TextMobject("\\# Edges"),
            TextMobject("\\# Regions"),
        ]
        for title, vect in zip(titles, [LEFT, ORIGIN, RIGHT]):
            title.shift(FRAME_X_RADIUS*vect/2)
            title.to_edge(UP)
            underline = Line(LEFT, RIGHT)
            underline.stretch_to_fit_width(title.get_width())
            underline.next_to(title, DOWN, SMALL_BUFF)
            title.add(underline)
            self.add(title)
        self.count_titles = titles
        self.v_count, self.e_count, self.f_count = self.counts = list(map(
            Integer, [1, 0, 1]
        ))
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
            LaggedStartMap(GrowArrow, dim_arrows)
        )
        self.wait()
        self.play(*list(map(FadeOut, [
            lit_word, lit_arrow, dim_word, dim_arrows
        ])))

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
        self.wait()
        for line, vertex in (lines[1], houses[1]), (lines[4], utilities[1]):
            self.play(
                ShowCreation(line),
                *self.get_count_change_animations(0, 1, 0)
            )
            self.play(*it.chain(
                self.get_lit_vertex_animations(vertex),
                self.get_count_change_animations(1, 0, 0),
            ))
        self.wait()
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
        self.wait()

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
        self.wait()
        self.play(
            ShowCreation(lines[7]),
            *self.get_count_change_animations(0, 1, 1)
        )
        self.add_foreground_mobjects(line_groups[2])
        self.add_foreground_mobjects(objects)
        self.play(FadeIn(region))
        self.wait()

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
        plus_one.set_color(YELLOW)
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
        line.set_width(0.5*vertex.get_width())
        line.next_to(ORIGIN, buff = 0.75*vertex.get_width())
        lines = VGroup(*[
            line.copy().rotate(angle)
            for angle in np.arange(0, 2*np.pi, np.pi/4)
        ])
        lines.move_to(vertex)
        random.shuffle(lines.submobjects)
        return [
            LaggedStartMap(
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
        VGroup(new_vertex, new_region).shift(RIGHT)
        arrows = VGroup(*[
            Arrow(
                new_edge.get_right(), mob.get_left(), 
                color = WHITE,
                buff = SMALL_BUFF
            )
            for mob in (new_vertex, new_region)
        ])
        for word, arrow in zip(["Either", "or"], arrows):
            word_mob = TextMobject(word)
            word_mob.scale(0.65)
            word_mob.next_to(ORIGIN, UP, SMALL_BUFF)
            word_mob.rotate(arrow.get_angle())
            word_mob.shift(arrow.get_center())
            word_mob.set_color(GREEN)
            arrow.add(word_mob)
        new_vertex.set_color(YELLOW)
        new_edge.set_color(BLUE)
        new_region.set_color(RED)
        rule = VGroup(new_edge, arrows, new_vertex, new_region)
        rule.center().to_edge(UP)

        nine_total = TextMobject("(9 total)")
        nine_total.next_to(new_edge, DOWN)

        self.play(
            Animation(rule),
            self.teacher.change, "raise_right_hand"
        )
        self.change_student_modes(
            *["confused"]*3,
            look_at_arg = rule
        )
        self.wait(2)
        self.play(
            Write(nine_total),
            self.teacher.change, "happy",
        )
        self.change_student_modes(
            *["thinking"]*3, 
            look_at_arg = rule
        )
        self.wait(3)

class ConcludeFiveRegions(LightUpNodes):
    def construct(self):
        self.setup_configuration()
        self.setup_regions()
        self.setup_counters()

        self.describe_start_setup()
        self.show_nine_lines_to_start()
        self.show_five_to_lit_up_nodes()
        self.relate_four_lines_to_regions()
        self.conclude_about_five_regions()

    def describe_start_setup(self):
        to_dim = VGroup(*it.chain(self.houses, self.utilities[1:]))
        to_dim.set_stroke(width = 1)
        to_dim.set_fill(opacity = 0)

        full_screen_rect = FullScreenFadeRectangle(
            fill_color = LIGHT_GREY,
            fill_opacity = 0.25,
        )

        self.play(
            Indicate(self.v_count),
            *self.get_lit_vertex_animations(self.utilities[0])
        )
        self.play(
            FadeIn(
                full_screen_rect,
                rate_func = there_and_back,
                remover = True,
            ),
            Indicate(self.f_count),
            *list(map(Animation, self.mobjects))
        )
        self.wait()

    def show_nine_lines_to_start(self):
        line_sets = self.get_straight_lines()
        line_sets.target = VGroup()
        for lines in line_sets:
            lines.generate_target()
            for line in lines.target:
                line.rotate(-line.get_angle())
                line.set_width(1.5)
            lines.target.arrange(DOWN)
            line_sets.target.add(lines.target)
        line_sets.target.arrange(DOWN)
        line_sets.target.center()
        line_sets.target.to_edge(RIGHT)

        for lines in line_sets:
            self.play(LaggedStartMap(ShowCreation, lines, run_time = 1))
            self.play(MoveToTarget(lines))
        self.wait()

        ghost_lines = line_sets.copy()
        ghost_lines.fade(0.9)
        self.add(ghost_lines, line_sets)
        self.side_lines = VGroup(*it.chain(*line_sets))

    def show_five_to_lit_up_nodes(self):
        side_lines = self.side_lines
        lines = self.lines
        vertices = VGroup(*it.chain(self.houses, self.utilities))
        line_indices = [0, 1, 4, 6, 7]
        vertex_indices = [0, 1, 4, 5, 2]

        for li, vi in zip(line_indices, vertex_indices):
            side_line = side_lines[li]
            line = lines[li]
            vertex = vertices[vi]
            self.play(ReplacementTransform(side_line, line))
            self.play(*it.chain(
                self.get_count_change_animations(1, 1, 0),
                self.get_lit_vertex_animations(vertex),
            ))

    def relate_four_lines_to_regions(self):
        f_rect = SurroundingRectangle(
            VGroup(self.count_titles[-1], self.f_count)
        )
        on_screen_side_lines = VGroup(*[m for m in self.side_lines if m in self.mobjects])
        side_lines_rect = SurroundingRectangle(on_screen_side_lines)
        side_lines_rect.set_color(WHITE)

        self.play(ShowCreation(side_lines_rect))
        self.wait()
        self.play(ReplacementTransform(side_lines_rect, f_rect))
        self.play(FadeOut(f_rect))
        self.wait()

    def conclude_about_five_regions(self):
        lines = self.lines
        side_lines = self.side_lines
        regions = self.regions[1:]
        line_groups = self.line_groups
        line_indices = [3, 5, 2]
        objects = self.objects

        for region, line_group, li in zip(regions, line_groups, line_indices):
            self.play(ReplacementTransform(
                side_lines[li], lines[li]
            ))
            self.play(
                FadeIn(region), 
                Animation(line_group), 
                Animation(objects),
                *self.get_count_change_animations(0, 1, 1)
            )
        self.wait()

        #Conclude
        words = TextMobject("Last line must \\\\ introduce 5th region")
        words.scale(0.8)
        words.set_color(BLUE)
        rect = SurroundingRectangle(self.f_count)
        rect.set_color(BLUE)
        words.next_to(rect, DOWN)
        randy = Randolph().flip()
        randy.scale(0.5)
        randy.next_to(words, RIGHT, SMALL_BUFF, DOWN)
        self.play(ShowCreation(rect), Write(words))
        self.play(FadeIn(randy))
        self.play(randy.change, "pondering")
        self.play(Blink(randy))
        self.wait(2)

class WhatsWrongWithFive(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "What's wrong with \\\\ 5 regions?",
            target_mode = "maybe"
        )
        self.wait(2)

class CyclesHaveAtLeastFour(UtilitiesPuzzleScene):
    def construct(self):
        self.setup_configuration()
        houses, utilities = self.houses, self.utilities
        vertices = VGroup(
            houses[0], utilities[0],
            houses[1], utilities[1], houses[0],
        )
        lines = [
            VectorizedPoint(),
            self.get_line(0, 0),
            self.get_line(0, 1),
            self.get_line(1, 1),
            self.get_line(1, 0, self.objects.get_corner(DOWN+LEFT)),
        ]
        for line in lines[1::2]:
            line.points = line.points[::-1]
        arrows = VGroup()
        for vertex in vertices:
            vect = vertices.get_center() - vertex.get_center()
            arrow = Vector(vect, color = WHITE)
            arrow.next_to(vertex, -vect, buff = 0)
            vertex.arrow = arrow
            arrows.add(arrow)
        word_strings = [
            "Start at a house",
            "Go to a utility",
            "Go to another house",
            "Go to another utility",
            "Back to the start",
        ]
        words = VGroup()
        for word_string, arrow in zip(word_strings, arrows):
            vect = arrow.get_vector()[1]*UP
            word = TextMobject(word_string)
            word.next_to(arrow.get_start(), -vect)
            words.add(word)

        count = Integer(-1)
        count.fade(1)
        count.to_edge(UP)

        last_word = None
        last_arrow = None

        for line, word, arrow in zip(lines, words, arrows):
            anims = []
            for mob in last_word, last_arrow:
                if mob:
                    anims.append(FadeOut(mob))
            new_count = Integer(count.number + 1)
            new_count.move_to(count)
            anims += [
                FadeIn(word),
                GrowArrow(arrow),
                ShowCreation(line),
                FadeOut(count),
                FadeIn(new_count),
            ]
            self.play(*anims)
            self.wait()
            last_word = word
            last_arrow = arrow
            count = new_count
        self.wait(2)

class FiveRegionsFourEdgesEachGraph(Scene):
    CONFIG = {
        "v_color" : WHITE,
        "e_color" : YELLOW,
        "f_colors" : (BLUE, RED_E, BLUE_E),
        "n_edge_double_count_examples" : 6,
        "random_seed" : 1,
    }
    def construct(self):
        self.draw_squares()
        self.transition_to_graph()
        self.count_edges_per_region()
        self.each_edges_has_two_regions()
        self.ten_total_edges()

    def draw_squares(self):
        words = VGroup(
            TextMobject("5", "regions"),
            TextMobject("4", "edges each"),
        )
        words.arrange(DOWN)
        words.to_edge(UP)
        words[0][0].set_color(self.f_colors[0])
        words[1][0].set_color(self.e_color)

        squares = VGroup(*[Square() for x in range(5)])
        squares.scale(0.5)
        squares.set_stroke(width = 0)
        squares.set_fill(opacity = 1)
        squares.set_color_by_gradient(*self.f_colors)
        squares.arrange(RIGHT, buff = MED_LARGE_BUFF)
        squares.next_to(words, DOWN, LARGE_BUFF)
        all_edges = VGroup()
        all_vertices = VGroup()
        for square in squares:
            corners = square.get_anchors()[:4]
            square.edges = VGroup(*[
                Line(c1, c2, color = self.e_color)
                for c1, c2 in adjacent_pairs(corners)
            ])
            square.vertices = VGroup(*[
                Dot(color = self.v_color).move_to(c)
                for c in corners
            ])
            all_edges.add(*square.edges)
            all_vertices.add(*square.vertices)

        self.play(
            FadeIn(words[0]),
            LaggedStartMap(FadeIn, squares, run_time = 1.5)
        )
        self.play(
            FadeIn(words[1]),
            LaggedStartMap(ShowCreation, all_edges),
            LaggedStartMap(GrowFromCenter, all_vertices),
        )
        self.wait()

        self.add_foreground_mobjects(words)
        self.set_variables_as_attrs(words, squares)

    def transition_to_graph(self):
        squares = self.squares
        words = self.words

        points = np.array([
            UP+LEFT,
            UP+RIGHT,
            DOWN+RIGHT,
            DOWN+LEFT,
            3*(UP+RIGHT),
            3*(DOWN+LEFT),
            3*(DOWN+RIGHT),
        ])
        points *= 0.75

        regions = VGroup(*[
            Square().set_points_as_corners(points[indices])
            for indices in [
                [0, 1, 2, 3],
                [0, 4, 2, 1],
                [5, 0, 3, 2],
                [5, 2, 4, 6],
                [6, 4, 0, 5],
            ]
        ])
        regions.set_stroke(width = 0)
        regions.set_fill(opacity = 1)
        regions.set_color_by_gradient(*self.f_colors)

        all_edges = VGroup()
        all_movers = VGroup()
        for region, square in zip(regions, squares):
            corners = region.get_anchors()[:4]
            region.edges = VGroup(*[
                Line(c1, c2, color = self.e_color)
                for c1, c2 in adjacent_pairs(corners)
            ])
            all_edges.add(*region.edges)
            region.vertices = VGroup(*[
                Dot(color = self.v_color).move_to(c)
                for c in corners
            ])
            mover = VGroup(
                square, square.edges, square.vertices,
            )
            mover.target = VGroup(
                region, region.edges, region.vertices
            )
            all_movers.add(mover)

        back_region = FullScreenFadeRectangle()
        back_region.set_fill(regions[-1].get_color(), 0.5)
        regions[-1].set_fill(opacity = 0)
        back_region.add(regions[-1].copy().set_fill(BLACK, 1))
        back_region.edges = regions[-1].edges

        self.play(
            FadeIn(
                back_region,
                rate_func = squish_rate_func(smooth, 0.7, 1),
                run_time = 3,
            ),
            LaggedStartMap(
                MoveToTarget, all_movers,
                run_time = 3,
                replace_mobject_with_target_in_scene = True,
            ),
        )
        self.wait(2)

        self.set_variables_as_attrs(
            regions, all_edges, back_region,
            graph = VGroup(*[m.target for m in all_movers])
        )

    def count_edges_per_region(self):
        all_edges = self.all_edges
        back_region = self.back_region
        regions = self.regions
        graph = self.graph
        all_vertices = VGroup(*[r.vertices for r in regions])

        ghost_edges = all_edges.copy()
        ghost_edges.set_stroke(LIGHT_GREY, 1)

        count = Integer(0)
        count.scale(2)
        count.next_to(graph, RIGHT, buff = 2)
        count.set_fill(YELLOW, opacity = 0)

        last_region = VGroup(back_region, *regions[1:])
        last_region.add(all_edges)

        for region in list(regions[:-1]) + [back_region]:
            self.play(
                FadeIn(region),
                Animation(ghost_edges),
                FadeOut(last_region),
                Animation(count),
                Animation(all_vertices),
            )
            for edge in region.edges:
                new_count = Integer(count.number + 1)
                new_count.replace(count, dim_to_match = 1)
                new_count.set_color(count.get_color())
                self.play(
                    ShowCreation(edge),
                    FadeOut(count),
                    FadeIn(new_count),
                    run_time = 0.5
                )
                count = new_count
            last_region = VGroup(region, region.edges)
        self.wait()
        self.add_foreground_mobjects(count)
        self.play(
            FadeOut(last_region),
            Animation(ghost_edges),
            Animation(all_vertices),
        )

        self.set_variables_as_attrs(count, ghost_edges, all_vertices)

    def each_edges_has_two_regions(self):
        regions = list(self.regions[:-1]) + [self.back_region]
        back_region = self.back_region
        self.add_foreground_mobjects(self.ghost_edges, self.all_vertices)

        edge_region_pair_groups = []
        for r1, r2 in it.combinations(regions, 2):
            for e1 in r1.edges:
                for e2 in r2.edges:
                    diff = e1.get_center()-e2.get_center()
                    if get_norm(diff) < 0.01:
                        edge_region_pair_groups.append(VGroup(
                            e1, r1, r2
                        ))

        for x in range(self.n_edge_double_count_examples):
            edge, r1, r2 = random.choice(edge_region_pair_groups)
            if r2 is back_region:
                #Flip again, maybe you're still unlucky, maybe not
                edge, r1, r2 = random.choice(edge_region_pair_groups)
            self.play(ShowCreation(edge))
            self.add_foreground_mobjects(edge)
            self.play(FadeIn(r1), run_time = 0.5)
            self.play(FadeIn(r2), Animation(r1), run_time = 0.5)
            self.wait(0.5)
            self.play(*list(map(FadeOut, [r2, r1, edge])), run_time = 0.5)
            self.remove_foreground_mobjects(edge)

    def ten_total_edges(self):
        double_count = self.count
        brace = Brace(double_count, UP)
        words = brace.get_text("Double-counts \\\\ edges")
        regions = self.regions

        edges = VGroup(*it.chain(
            regions[0].edges,
            regions[-1].edges,
            [regions[1].edges[1]],
            [regions[2].edges[3]],
        ))

        count = Integer(0)
        count.scale(2)
        count.set_fill(WHITE, 0)
        count.next_to(self.graph, LEFT, LARGE_BUFF)

        self.play(
            GrowFromCenter(brace),
            Write(words)
        )
        self.wait()
        for edge in edges:
            new_count = Integer(count.number + 1)
            new_count.replace(count, dim_to_match = 1)
            self.play(
                ShowCreation(edge),
                FadeOut(count),
                FadeIn(new_count),
                run_time = 0.5
            )
            count = new_count
        self.wait()

class EulersFormulaForGeneralPlanarGraph(LightUpNodes, ThreeDScene):
    CONFIG = {
        "vertices_word" : "Vertices"
    }
    def construct(self):
        self.setup_counters()
        self.show_creation_of_graph()
        self.show_formula()
        self.transform_into_cube()

    def show_creation_of_graph(self):
        points = np.array([
            UP+LEFT,
            UP+RIGHT,
            DOWN+RIGHT,
            DOWN+LEFT,
            3*(UP+LEFT),
            3*(UP+RIGHT),
            3*(DOWN+RIGHT),
            3*(DOWN+LEFT),
        ])
        points *= 0.75
        points += DOWN
        vertices = VGroup(*list(map(Dot, points)))
        vertices.set_color(YELLOW)
        edges = VGroup(*[
            VGroup(*[
                Line(p1, p2, color = WHITE)
                for p2 in points
            ])
            for p1 in points
        ])
        regions = self.get_cube_faces(points)
        regions.set_stroke(width = 0)
        regions.set_fill(opacity = 1)
        regions.set_color_by_gradient(GREEN, RED, BLUE_E)
        regions[-1].set_fill(opacity = 0)

        pairs = [
            (edges[0][1], vertices[1]),
            (edges[1][2], vertices[2]),
            (edges[2][6], vertices[6]),
            (edges[6][5], vertices[5]),
            (edges[5][1], regions[2]),
            (edges[0][4], vertices[4]),
            (edges[4][5], regions[1]),
            (edges[0][3], vertices[3]),
            (edges[3][2], regions[0]),
            (edges[4][7], vertices[7]),
            (edges[7][3], regions[4]),
            (edges[7][6], regions[3]),
        ]

        self.add_foreground_mobjects(vertices[0])
        self.wait()
        for edge, obj in pairs:
            anims = [ShowCreation(edge)]
            if obj in vertices:
                obj.save_state()
                obj.move_to(edge.get_start())
                anims.append(ApplyMethod(obj.restore))
                anims += self.get_count_change_animations(1, 1, 0)
                self.add_foreground_mobjects(obj)
            else:
                anims = [FadeIn(obj)] + anims
                anims += self.get_count_change_animations(0, 1, 1)
            self.play(*anims)
            self.add_foreground_mobjects(edge)
        self.wait()

        self.set_variables_as_attrs(edges, vertices, regions)

    def show_formula(self):
        counts = VGroup(*self.counts)
        count_titles = VGroup(*self.count_titles)
        groups = [count_titles, counts]

        for group in groups:
            group.symbols = VGroup(*list(map(TexMobject, ["-", "+", "="])))
            group.generate_target()
            line = VGroup(*it.chain(*list(zip(group.target, group.symbols))))
            line.arrange(RIGHT)
            line.to_edge(UP, buff = MED_SMALL_BUFF)
        VGroup(counts.target, counts.symbols).shift(0.75*DOWN)
        for mob in count_titles.target:
            mob[-1].fade(1)
        count_titles.symbols.shift(0.5*SMALL_BUFF*UP)
        twos = VGroup(*[
            TexMobject("2").next_to(group.symbols, RIGHT)
            for group in groups
        ])
        twos.shift(0.5*SMALL_BUFF*UP)

        words = TextMobject("``Euler's characteristic formula''")
        words.next_to(counts.target, DOWN)
        words.shift(MED_LARGE_BUFF*RIGHT)
        words.set_color(YELLOW)

        for group in groups:
            self.play(
                MoveToTarget(group),
                Write(group.symbols)
            )
        self.wait()
        self.play(Write(twos))
        self.wait()
        self.play(Write(words))
        self.wait()

        self.top_formula = VGroup(count_titles, count_titles.symbols, twos[0])
        self.bottom_formula = VGroup(counts, counts.symbols, twos[1])

    def transform_into_cube(self):
        regions = self.regions
        points = np.array([
            UP+LEFT,
            UP+RIGHT,
            DOWN+RIGHT,
            DOWN+LEFT,
            UP+LEFT+2*IN,
            UP+RIGHT+2*IN,
            DOWN+RIGHT+2*IN,
            DOWN+LEFT+2*IN,
        ])
        cube = self.get_cube_faces(points)
        cube.shift(OUT)
        cube.rotate_in_place(np.pi/12, RIGHT)
        cube.rotate_in_place(np.pi/6, UP)
        cube.shift(MED_LARGE_BUFF*DOWN)
        shade_in_3d(cube)

        for face, region in zip(cube, regions):
            face.set_fill(region.get_color(), opacity = 0.8)

        self.remove(self.edges)
        regions.set_stroke(WHITE, 3)
        cube.set_stroke(WHITE, 3)

        new_formula = TexMobject("V - E + F = 2")
        new_formula.to_edge(UP, buff = MED_SMALL_BUFF)
        new_formula.align_to(self.bottom_formula, RIGHT)

        self.play(FadeOut(self.vertices))
        self.play(ReplacementTransform(regions, cube, run_time = 2))
        cube.sort(lambda p : -p[2])
        always_rotate(cube, axis=UP, about_point=ORIGIN)
        self.add(cube)
        self.wait(3)
        self.play(
            FadeOut(self.top_formula),
            FadeIn(new_formula)
        )
        self.wait(10)


    ###

    def get_cube_faces(self, eight_points):
        return VGroup(*[
            Square().set_points_as_corners(eight_points[indices])
            for indices in [
                [0, 1, 2, 3],
                [0, 4, 5, 1],
                [1, 5, 6, 2],
                [2, 6, 7, 3],
                [3, 7, 4, 0],
                [4, 5, 6, 7],
            ]
        ])

class YouGaveFriendsAnImpossiblePuzzle(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "You gave friends \\\\ an impossible puzzle?",
            target_mode = "sassy",
        )
        self.change_student_modes(
            "angry", "sassy", "angry",
            added_anims = [self.teacher.change, "happy"]
        )
        self.wait(2)

class FunnyStory(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("Funny story", target_mode = "hooray")
        self.wait()
        self.change_student_modes(
            *["happy"]*3,
            added_anims = [RemovePiCreatureBubble(
                self.teacher,
                target_mode = "raise_right_hand"
            )],
            look_at_arg = UP+2*RIGHT
        )
        self.wait(5)

class QuestionWrapper(Scene):
    def construct(self):
        question = TextMobject(
            "Where", "\\emph{specifically}", "does\\\\", 
            "this proof break down?",
        )
        question.to_edge(UP)
        question.set_color_by_tex("specifically", YELLOW)
        screen_rect = ScreenRectangle(height = 5.5)
        screen_rect.next_to(question, DOWN)

        self.play(ShowCreation(screen_rect))
        self.wait()
        for word in question:
            self.play(LaggedStartMap(
                FadeIn, word,
                run_time = 0.05*len(word)
            ))
            self.wait(0.05)
        self.wait()

class Homework(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("Consider this \\\\ homework")
        self.change_student_modes(*["pondering"]*3)
        self.wait(2)
        self.student_says(
            "$V-E+F=0$ on \\\\ a torus!",
            target_mode = "hooray"
        )
        self.wait()
        self.teacher_says("Not good enough!", target_mode = "surprised")
        self.change_student_modes(*["confused"]*3)
        self.wait(2)

class WantToLearnMore(Scene):
    def construct(self):
        text = TextMobject("Want to learn more?")
        self.play(Write(text))
        self.wait()

class PatreonThanks(PatreonEndScreen):
    CONFIG = {
        "specific_patrons" : [
            "Randall Hunt",
            "Desmos",
            "Burt Humburg",
            "CrypticSwarm",
            "Juan Benet",
            "David Kedmey",
            "Ali Yahya",
            "Mayank M. Mehrotra",
            "Lukas Biewald",
            "Yana Chernobilsky",
            "Kaustuv DeBiswas",
            "Kathryn Schmiedicke",
            "Yu Jun",
            "Dave Nicponski",
            "Damion Kistler",
            "Jordan Scales",
            "Markus Persson",
            "Egor Gumenuk",
            "Yoni Nazarathy",
            "Ryan Atallah",
            "Joseph John Cox",
            "Luc Ritchie",
            "Onuralp Soylemez",
            "John Bjorn Nelson",
            "Yaw Etse",
            "David Barbetta",
            "Julio Cesar Campo Neto",
            "Waleed Hamied",
            "Oliver Steele",
            "George Chiesa",
            "supershabam",
            "James Park",
            "Samantha D. Suplee",
            "Delton Ding",
            "Thomas Tarler",
            "Jonathan Eppele",
            "Isak Hietala",
            "1stViewMaths",
            "Jacob Magnuson",
            "Mark Govea",
            "Dagan Harrington",
            "Clark Gaebel",
            "Eric Chow",
            "Mathias Jansson",
            "David Clark",
            "Michael Gardner",
            "Mads Elvheim",
            "Erik Sundell",
            "Awoo",
            "Dr. David G. Stork",
            "Tianyu Ge",
            "Ted Suzman",
            "Linh Tran",
            "Andrew Busey",
            "John Haley",
            "Ankalagon",
            "Eric Lavault",
            "Boris Veselinovich",
            "Julian Pulgarin",
            "Jeff Linse",
            "Cooper Jones",
            "Ryan Dahl",
            "Robert Teed",
            "Jason Hise",
            "Meshal Alshammari",
            "Bernd Sing",
            "James Thornton",
            "Mustafa Mahdi",
            "Mathew Bramson",
            "Jerry Ling",
            "Shimin  Kuang",
            "Rish Kundalia",
            "Achille Brighton",
            "Ripta Pasay",
        ]
    }

































