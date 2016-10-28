from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from scene import Scene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *


class ClosedLoopScene(Scene):
    CONFIG = {
        "loop_anchor_points" : [
            3*RIGHT,
            2*RIGHT+UP,
            3*RIGHT + 3*UP,
            UP,
            2*UP+LEFT,
            2*LEFT + 2*UP,
            3*LEFT,
            2*LEFT+DOWN,
            3*LEFT+2*DOWN,
            2*DOWN+RIGHT,
            LEFT+DOWN,
        ],
        "square_vertices" : [
            2*RIGHT+UP,
            2*UP+LEFT,
            2*LEFT+DOWN,
            2*DOWN+RIGHT
        ],
        "rect_vertices" : [
            0*RIGHT + 1*UP,
            -1*RIGHT +  2*UP,
            -3*RIGHT +  0*UP,
            -2*RIGHT + -1*UP,
        ],
        "dot_color" : YELLOW,
        "connecting_lines_color" : BLUE,
        "pair_colors" : [MAROON_B, PURPLE_B],
    }
    def setup(self):
        self.dots = VGroup()
        self.connecting_lines = VGroup()
        self.add_loop()

    def add_loop(self):
        self.loop = self.get_default_loop()
        self.add(self.loop)

    def get_default_loop(self):
        loop = VMobject()
        loop.set_points_smoothly(
            self.loop_anchor_points + [self.loop_anchor_points[0]]
        )
        return loop

    def get_square(self):
        return Polygon(*self.square_vertices)

    def get_rect_vertex_dots(self, square = False):
        if square:
            vertices = self.square_vertices
        else:
            vertices = self.rect_vertices
        dots = VGroup(*[Dot(v) for v in vertices])
        dots.highlight(self.dot_color)
        return dots

    def get_rect_alphas(self, square = False):
        #Inefficient and silly, but whatever.
        dots = self.get_rect_vertex_dots(square = square)
        return self.get_dot_alphas(dots)

    def add_dot(self, dot):
        self.add_dots(dot)

    def add_dots(self, *dots):
        self.dots.add(*dots)
        self.add(self.dots)

    def add_rect_dots(self, square = False):
        self.add_dots(*self.get_rect_vertex_dots())

    def add_dots_at_alphas(self, *alphas):
        self.add_dots(*[
            Dot(
                self.loop.point_from_proportion(alpha), 
                color = self.dot_color
            )
            for alpha in alphas
        ])

    def add_connecting_lines(self, cyclic = False):
        if cyclic:
            pairs = adjascent_pairs(self.dots)
        else:
            n_pairs = len(list(self.dots))/2
            pairs = zip(self.dots[:n_pairs], self.dots[n_pairs:])
        for d1, d2 in pairs:
            line = Line(d1.get_center(), d2.get_center())
            line.start_dot = d1 
            line.end_dot = d2
            line.update_anim = UpdateFromFunc(
                line,
                lambda l : l.put_start_and_end_on(
                    l.start_dot.get_center(),
                    l.end_dot.get_center()
                )
            )
            line.highlight(d1.get_color())
            self.connecting_lines.add(line)
        if cyclic:
            self.connecting_lines.highlight(self.connecting_lines_color)
            self.connecting_lines.set_stroke(width = 6)
        self.add(self.connecting_lines, self.dots)

    def get_line_anims(self):
        return [
            line.update_anim
            for line in self.connecting_lines
        ] + [Animation(self.dots)]

    def get_dot_alphas(self, dots = None, precision = 0.005):
        if dots == None:
            dots = self.dots
        alphas = []
        alpha_range = np.arange(0, 1, precision)
        loop_points = np.array(map(self.loop.point_from_proportion, alpha_range))
        for dot in dots:
            vects = loop_points - dot.get_center()
            norms = np.apply_along_axis(np.linalg.norm, 1, vects)
            index = np.argmin(norms)
            alphas.append(alpha_range[index])
        return alphas

    def let_dots_wonder(self, run_time = 5, random_seed = None, added_anims = []):
        if random_seed is not None:
            np.random.seed(random_seed)
        start_alphas = self.get_dot_alphas()
        alpha_rates = 0.05 + 0.1*np.random.random(len(list(self.dots)))
        def generate_rate_func(start, rate):
            return lambda t : (start + t*rate*run_time)%1
        anims = [
            MoveAlongPath(
                dot,
                self.loop,
                rate_func = generate_rate_func(start, rate)
            )
            for dot, start, rate in zip(self.dots, start_alphas, alpha_rates)
        ]
        anims += self.get_line_anims()
        anims += added_anims
        self.play(*anims, run_time = run_time)

    def move_dots_to_alphas(self, alphas, run_time = 3):
        assert(len(alphas) == len(list(self.dots)))
        start_alphas = self.get_dot_alphas()
        def generate_rate_func(start_alpha, alpha):
            return lambda t : interpolate(start_alpha, alpha, smooth(t))
        anims = [
            MoveAlongPath(
                dot, self.loop,
                rate_func = generate_rate_func(sa, a),
                run_time = run_time,
            )
            for dot, sa, a in zip(self.dots, start_alphas, alphas)
        ]
        anims += self.get_line_anims()
        self.play(*anims)

    def transform_loop(self, target_loop, **kwargs):
        alphas = self.get_dot_alphas()
        dot_anims = []
        for dot, alpha in zip(self.dots, alphas):
            dot.generate_target()
            dot.target.move_to(target_loop.point_from_proportion(alpha))
            dot_anims.append(MoveToTarget(dot))
        self.play(
            Transform(self.loop, target_loop),
            *dot_anims + self.get_line_anims(),
            **kwargs
        )
        self.remove(self.loop)
        self.loop = target_loop
        self.add(self.loop, self.dots, self.connecting_lines)

    def highlight_dots_by_pair(self):
        n_pairs = len(list(self.dots))/2
        for d1, d2, c in zip(self.dots[:n_pairs], self.dots[n_pairs:], self.pair_colors):
            VGroup(d1, d2).highlight(c)

    def find_square(self):
        alpha_quads = list(it.combinations(
            np.arange(0, 1, 0.02) , 4
        ))
        quads = np.array([
            [
                self.loop.point_from_proportion(alpha)
                for alpha in quad
            ]
            for quad in alpha_quads
        ])
        scores = self.square_scores(quads)
        index = np.argmin(scores)
        return quads[index]

    def square_scores(self, all_quads):
        midpoint_diffs = np.apply_along_axis(
            np.linalg.norm, 1,
            0.5*(all_quads[:,0] + all_quads[:,2]) - 0.5*(all_quads[:,1] + all_quads[:,3])
        )
        vects1 = all_quads[:,0] - all_quads[:,2]
        vects2 = all_quads[:,1] - all_quads[:,3]
        distances1 = np.apply_along_axis(np.linalg.norm, 1, vects1)
        distances2 = np.apply_along_axis(np.linalg.norm, 1, vects2)
        distance_diffs = np.abs(distances1 - distances2)
        midpoint_diffs /= distances1
        distance_diffs /= distances2

        buffed_d1s = np.repeat(distances1, 3).reshape(vects1.shape)
        buffed_d2s = np.repeat(distances2, 3).reshape(vects2.shape)
        unit_v1s = vects1/buffed_d1s
        unit_v2s = vects2/buffed_d2s
        dots = np.abs(unit_v1s[:,0]*unit_v2s[:,0] + unit_v1s[:,1]*unit_v2s[:,1] + unit_v1s[:,2]*unit_v2s[:,2])

        return midpoint_diffs + distance_diffs + dots



#############################

class Introduction(TeacherStudentsScene):
    def construct(self):
        self.play(self.get_teacher().change_mode, "hooray")
        self.random_blink()
        self.teacher_says("")
        for pi in self.get_students():
            pi.generate_target()
            pi.target.change_mode("happy")            
            pi.target.look_at(self.get_teacher().bubble)
        self.play(*map(MoveToTarget, self.get_students()))
        self.random_blink(3)
        self.teacher_says(
            "Here's why \\\\ I'm excited...",
            pi_creature_target_mode = "hooray"
        )
        for pi in self.get_students():
            pi.target.look_at(self.get_teacher().eyes)
        self.play(*map(MoveToTarget, self.get_students()))
        self.dither()

class WhenIWasAKid(TeacherStudentsScene):
    def construct(self):
        children = self.get_children()
        speaker = self.get_speaker()

        self.prepare_everyone(children, speaker)
        self.transition_from_previous_scene(children, speaker)
        self.students = children
        self.teacher = speaker
        self.run_class()
        self.grow_up()

    def transition_from_previous_scene(self, children, speaker):
        self.play(self.get_teacher().change_mode, "hooray", run_time = 0)
        self.change_student_modes(*["happy"]*3)

        speaker.look_at(children)
        me = children[-1]
        self.play(
            FadeOut(self.get_students()),
            Transform(self.get_teacher(), me)
        )
        self.remove(self.get_teacher())
        self.add(me)
        self.play(*map(FadeIn, children[:-1] + [speaker]))
        self.random_blink()

    def run_class(self):
        children = self.students
        speaker = self.teacher
        title = TextMobject("Topology")
        title.to_edge(UP)

        self.random_blink()
        self.play(self.teacher.change_mode, "speaking")
        self.play(Write(title))
        self.random_blink()
        pi1, pi2, pi3, me = children
        self.play(pi1.change_mode, "raise_right_hand")
        self.random_blink()
        self.play(
            pi2.change_mode, "confused",
            pi3.change_mode, "happy",
            pi2.look_at, pi3.eyes,
            pi3.look_at, pi2.eyes,
        )
        self.random_blink()
        self.play(me.change_mode, "pondering")
        self.dither()
        self.random_blink(2)
        self.play(pi1.change_mode, "raise_left_hand")
        self.dither()
        self.play(pi2.change_mode, "erm")
        self.random_blink()
        self.student_says(
            "How is this math?",
            student_index = -1,
            pi_creature_target_mode = "pleading",
            width = 5, 
            height = 3,
            direction = RIGHT
        )
        self.play(
            pi1.change_mode, "pondering",
            pi2.change_mode, "pondering",
            pi3.change_mode, "pondering",
        )
        self.play(speaker.change_mode, "pondering")
        self.random_blink()

    def grow_up(self):
        me = self.students[-1]
        self.students.remove(me)
        morty = Mortimer(mode = "pondering")
        morty.flip()
        morty.move_to(me, aligned_edge = DOWN)
        morty.to_edge(LEFT)
        morty.look(RIGHT)

        self.play(
            Transform(me, morty),
            *map(FadeOut, [
                self.students, self.teacher,
                me.bubble, me.bubble.content
            ])
        )
        self.remove(me)
        self.add(morty)
        self.play(Blink(morty))
        self.dither()
        self.play(morty.change_mode, "hooray")
        self.dither()


    def prepare_everyone(self, children, speaker):
        self.everyone = list(children) + [speaker]
        for pi in self.everyone:
            pi.bubble = None

    def get_children(self):
        colors = [MAROON_E, YELLOW_D, PINK, GREY_BROWN]
        children = VGroup(*[
            BabyPiCreature(color = color)
            for color in colors
        ])
        children.arrange_submobjects(RIGHT)
        children.to_edge(DOWN, buff = LARGE_BUFF)
        children.to_edge(LEFT)
        return children

    def get_speaker(self):
        speaker = Mathematician(mode = "happy")
        speaker.flip()
        speaker.to_edge(DOWN, buff = LARGE_BUFF)
        speaker.to_edge(RIGHT)
        return speaker

    def get_everyone(self):
        if hasattr(self, "everyone"):
            return self.everyone
        else:
            return TeacherStudentsScene.get_everyone(self)

class FormingTheMobiusStrip(Scene):
    def construct(self):
        pass

class DrawLineOnMobiusStrip(Scene):
    def construct(self):
        pass

class MugIntoTorus(Scene):
    def construct(self):
        pass

class DefineInscribedSquareProblem(ClosedLoopScene):
    def construct(self):
        self.draw_loop()
        self.cycle_through_shapes()
        self.ask_about_rectangles()

    def draw_loop(self):
        self.title = TextMobject("Inscribed", "square", "problem")
        self.title.to_edge(UP)

        #Draw loop
        self.remove(self.loop)
        self.play(Write(self.title))
        self.dither()
        self.play(ShowCreation(
            self.loop, 
            run_time = 3, 
            rate_func = None
        ))
        self.dither()
        self.add_rect_dots(square = True)
        self.play(ShowCreation(self.dots, run_time = 2))
        self.dither()
        self.add_connecting_lines(cyclic = True)
        self.play(
            ShowCreation(
                self.connecting_lines,
                submobject_mode = "all_at_once",
                run_time = 2
            ),
            Animation(self.dots)
        )
        self.dither(2)

    def cycle_through_shapes(self):
        circle = Circle(radius = 2.5, color = WHITE)
        ellipse = circle.copy()
        ellipse.stretch(1.5, 0)
        ellipse.stretch(0.7, 1)
        ellipse.rotate(-np.pi/2)
        ellipse.scale_to_fit_height(4)
        pi_loop = TexMobject("\\pi")[0]
        pi_loop.set_fill(opacity = 0)
        pi_loop.set_stroke(
            color = WHITE,
            width = DEFAULT_POINT_THICKNESS
        )
        pi_loop.scale_to_fit_height(4)
        randy = Randolph()
        randy.look(DOWN)
        randy.scale_to_fit_width(pi_loop.get_width())
        randy.move_to(pi_loop, aligned_edge = DOWN)
        randy.body.set_fill(opacity = 0)
        randy.mouth.set_stroke(width = 0)

        self.transform_loop(circle)
        self.dither()
        odd_eigths = np.linspace(1./8, 7./8, 4)
        self.move_dots_to_alphas(odd_eigths)
        self.dither()
        for nudge in 0.1, -0.1, 0:
            self.move_dots_to_alphas(odd_eigths+nudge)
        self.dither()
        self.transform_loop(ellipse)
        self.dither()
        nudge = 0.055
        self.move_dots_to_alphas(
            odd_eigths + [nudge, -nudge, nudge, -nudge]
        )
        self.dither(2)
        self.transform_loop(pi_loop)
        self.let_dots_wonder()
        randy_anims = [
            FadeIn(randy),
            Animation(randy),            
            Blink(randy),
            Animation(randy),
            Blink(randy, rate_func = smooth)
        ]
        for anim in randy_anims:
            self.let_dots_wonder(
                run_time = 1,
                random_seed = 0,
                added_anims = [anim]
            )
        self.remove(randy)
        self.transform_loop(self.get_default_loop())

    def ask_about_rectangles(self):
        morty = Mortimer()
        morty.next_to(ORIGIN, DOWN)
        morty.to_edge(RIGHT)

        new_title = TextMobject("Inscribed", "rectangle", "problem")
        new_title.highlight_by_tex("rectangle", YELLOW)
        new_title.to_edge(UP)
        rect_dots = self.get_rect_vertex_dots()
        rect_alphas = self.get_dot_alphas(rect_dots)

        self.play(FadeIn(morty))
        self.play(morty.change_mode, "speaking")
        self.play(Transform(self.title, new_title))
        self.move_dots_to_alphas(rect_alphas)
        self.dither()
        self.play(morty.change_mode, "hooray")
        self.play(Blink(morty))
        self.dither()
        self.play(FadeOut(self.connecting_lines))
        self.connecting_lines = VGroup()
        self.play(morty.change_mode, "plain")

        dot_pairs = [
            VGroup(self.dots[i], self.dots[j])
            for i, j in (0, 2), (1, 3)
        ]
        pair_colors = MAROON_B, PURPLE_B
        diag_lines = [
            Line(d1.get_center(), d2.get_center(), color = c)
            for (d1, d2), c in zip(dot_pairs, pair_colors)
        ]

        for pair, line in zip(dot_pairs, diag_lines):
            self.play(
                FadeIn(line),
                pair.highlight, line.get_color(),
            )

class RectangleProperties(Scene):
    def construct(self):
        rect = Rectangle(color = BLUE)
        vertex_dots = VGroup(*[
            Dot(anchor, color = YELLOW)
            for anchor in rect.get_anchors_and_handles()[0]
        ])
        dot_pairs = [
            VGroup(vertex_dots[i], vertex_dots[j])
            for i, j in (0, 2), (1, 3)
        ]
        colors = [MAROON_B, PURPLE_B]
        diag_lines = [
            Line(d1.get_center(), d2.get_center(), color = c)
            for (d1, d2), c in zip(dot_pairs, colors)
        ]
        braces = [Brace(rect).next_to(ORIGIN, DOWN) for x in range(2)]
        for brace, line in zip(braces, diag_lines):
            brace.stretch_to_fit_width(line.get_length())
            brace.rotate(line.get_angle())
        a, b, c, d = labels = VGroup(*[
            TexMobject(s).next_to(dot, dot.get_center(), buff = SMALL_BUFF)
            for s, dot in zip("abcd", vertex_dots)
        ])
        midpoint = Dot(ORIGIN, color = RED)


        self.play(ShowCreation(rect))
        self.dither()
        self.play(
            ShowCreation(vertex_dots),
            Write(labels)
        )
        self.dither()
        mob_lists = [
            (a, c, dot_pairs[0]),
            (b, d, dot_pairs[1]),
        ]
        for color, mob_list in zip(colors, mob_lists):
            self.play(*[
                ApplyMethod(mob.highlight, color)
                for mob in mob_list
            ])
            self.dither()
        for line, brace in zip(diag_lines, braces):
            self.play(
                ShowCreation(line),
                GrowFromCenter(brace)
            )
            self.dither()
            self.play(FadeOut(brace))
        self.play(FadeIn(midpoint))
        self.dither()

class PairOfPairBecomeRectangle(Scene):
    def construct(self):
        dots = VGroup(
            Dot(4*RIGHT+0.5*DOWN, color = MAROON_B),
            Dot(5*RIGHT+3*UP, color = MAROON_B),
            Dot(LEFT+0.1*DOWN, color = PURPLE_B),
            Dot(2*LEFT+UP, color = PURPLE_B)
        )
        labels = VGroup()
        for dot, char in zip(dots, "acbd"):
            label = TexMobject(char)
            y_coord = dot.get_center()[1]
            label.next_to(dot, np.sign(dot.get_center()[1])*UP)
            label.highlight(dot.get_color())
            labels.add(label)
        lines = [
            Line(
                dots[i].get_center(), 
                dots[j].get_center(), 
                color = dots[i].get_color()
            )
            for i, j in (0, 1), (2, 3)
        ]
        groups = [
            VGroup(dots[0], dots[1], labels[0], labels[1], lines[0]),
            VGroup(dots[2], dots[3], labels[2], labels[3], lines[1]),
        ]
        midpoint = Dot(LEFT, color = RED)

        words = VGroup(*map(TextMobject, [
            "Common midpoint",
            "Same distance apart",
            "$\\Downarrow$",
            "Rectangle",
        ]))
        words.arrange_submobjects(DOWN)
        words.to_edge(RIGHT)
        words[-1].highlight(BLUE)

        self.play(
            ShowCreation(dots),
            Write(labels)
        )
        self.play(*map(ShowCreation, lines))
        self.dither()
        self.play(*[
            ApplyMethod(
                group.shift, 
                -group[-1].get_center()+midpoint.get_center()
            )
            for group in groups
        ])
        self.play(
            ShowCreation(midpoint),
            Write(words[0])
        )
        factor = lines[0].get_length()/lines[1].get_length()        
        grower = groups[1].copy()
        new_line = grower[-1]
        new_line.scale_in_place(factor)
        grower[0].move_to(new_line.get_start())
        grower[2].next_to(grower[0], DOWN)
        grower[1].move_to(new_line.get_end())
        grower[3].next_to(grower[1], UP)

        self.play(Transform(groups[1], grower))
        self.play(Write(words[1]))
        self.dither()

        rectangle = Polygon(*[
            dots[i].get_center()
            for i in 0, 2, 1, 3
        ])
        rectangle.highlight(BLUE)
        self.play(
            ShowCreation(rectangle),
            Animation(dots)
        )
        self.play(*map(Write, words[2:]))
        self.dither()

class SearchForRectangleOnLoop(ClosedLoopScene):
    def construct(self):
        self.add_dots_at_alphas(*np.linspace(0.2, 0.8, 4))
        self.highlight_dots_by_pair()
        rect_alphas = self.get_rect_alphas()

        self.play(ShowCreation(self.dots))
        self.add_connecting_lines()
        self.play(ShowCreation(self.connecting_lines))
        self.let_dots_wonder(2)
        self.move_dots_to_alphas(rect_alphas)

        midpoint = Dot(
            center_of_mass([d.get_center() for d in self.dots]),
            color = RED
        )
        self.play(ShowCreation(midpoint))
        self.dither()
        angles = [line.get_angle() for line in self.connecting_lines]
        angle_mean = np.mean(angles)
        self.play(
            *[
                ApplyMethod(line.rotate_in_place, angle_mean-angle)
                for line, angle in zip(self.connecting_lines, angles)
            ] + [Animation(midpoint)],
            rate_func = there_and_back
        )
        self.add(self.connecting_lines.copy(), midpoint)
        self.connecting_lines = VGroup()
        self.dither()
        self.add_connecting_lines(cyclic = True)
        self.play(
            ShowCreation(self.connecting_lines), 
            Animation(self.dots)
        )
        self.dither()

class DeclareFunction(ClosedLoopScene):
    def construct(self):
        self.add_dots_at_alphas(0.2, 0.8)
        self.highlight_dots_by_pair()        
        self.add_connecting_lines()
        VGroup(
            self.loop, self.dots, self.connecting_lines
        ).scale(0.7).to_edge(LEFT).shift(DOWN)
        arrow = Arrow(LEFT, RIGHT).next_to(self.loop)
        self.add(arrow)

        self.add_tex()
        self.let_dots_wonder(10)

    def add_tex(self):
        tex = TexMobject("f", "(A, B)", "=", "(x, y, z)")
        tex.to_edge(UP)
        tex.shift(LEFT)

        ab_brace = Brace(tex[1])
        xyz_brace = Brace(tex[-1], RIGHT)
        ab_brace.add(ab_brace.get_text("Pair of points on the loop"))
        xyz_brace.add(xyz_brace.get_text("Point in 3d space"))
        ab_brace.gradient_highlight(MAROON_B, PURPLE_B)
        xyz_brace.highlight(BLUE)

        self.add(tex)
        self.play(Write(ab_brace))
        self.dither()
        self.play(Write(xyz_brace))
        self.dither()

class DefinePairTo3dFunction(Scene):
    def construct(self):
        pass

class LabelMidpoint(Scene):
    def construct(self):
        words = TextMobject("Midpoint $M$")
        words.highlight(RED)
        words.scale(2)
        self.play(Write(words, run_time = 1))
        self.dither()

class LabelDistance(Scene):
    def construct(self):
        words = TextMobject("Distance $d$")
        words.highlight(MAROON_B)
        words.scale(2)
        self.play(Write(words, run_time = 1))
        self.dither()

class DrawingOneLineOfTheSurface(Scene):
    def construct(self):
        pass

class FunctionSurface(Scene):
    def construct(self):
        pass

class PointPairApprocahingEachother3D(Scene):
    def construct(self):
        pass

class InputPairToFunction(Scene):
    def construct(self):
        tex = TexMobject("f(X, X)", "=X")
        tex.highlight_by_tex("=X", BLUE)
        tex.scale(2)
        self.play(Write(tex[0]))
        self.dither(2)
        self.play(Write(tex[1]))
        self.dither(2)

class WigglePairUnderSurface(Scene):
    def construct(self):
        pass        

class WriteContinuous(Scene):
    def construct(self):
        self.play(Write(TextMobject("Continuous").scale(2)))
        self.dither(2)

class DistinctPairCollisionOnSurface(Scene):
    def construct(self):
        pass

class PairOfRealsToPlane(Scene):
    def construct(self):
        r1, r2 = numbers = -3, 2
        colors = GREEN, RED
        dot1, dot2 = dots = VGroup(*[Dot(color = c) for c in colors])
        for dot, number in zip(dots, numbers):
            dot.move_to(number*RIGHT)
        pair_label = TexMobject("(", str(r1), ",", str(r2), ")")
        for number, color in zip(numbers, colors):
            pair_label.highlight_by_tex(str(number), color)
        pair_label.next_to(dots, UP, buff = 2)
        arrows = VGroup(*[
            Arrow(pair_label[i], dot, color = dot.get_color())
            for i, dot in zip([1, 3], dots)
        ])
        two_d_point = Dot(r1*RIGHT + r2*UP, color = YELLOW)
        pair_label.add_background_rectangle()

        x_axis = NumberLine(color = BLUE)
        y_axis = NumberLine(color = BLUE)
        plane = NumberPlane().fade()

        self.add(x_axis, y_axis, dots, pair_label)
        self.play(ShowCreation(arrows, run_time = 2))
        self.dither()
        self.play(
            pair_label.next_to, two_d_point, UP+LEFT, SMALL_BUFF,
            Rotate(y_axis, np.pi/2),
            Rotate(dot2, np.pi/2),
            FadeOut(arrows)
        )
        lines = VGroup(*[
            DashedLine(dot, two_d_point, color = dot.get_color())
            for dot in dots
        ])
        self.play(*map(ShowCreation, lines))
        self.play(ShowCreation(two_d_point))
        everything = VGroup(*self.get_mobjects())
        self.play(
            FadeIn(plane), 
            Animation(everything),
            Animation(dot2)
        )
        self.dither()

class SeekSurfaceForPairs(ClosedLoopScene):
    def construct(self):
        self.loop.to_edge(LEFT)
        self.add_dots_at_alphas(0.2, 0.3)
        self.highlight_dots_by_pair()        
        self.add_connecting_lines()

        arrow = Arrow(LEFT, RIGHT).next_to(self.loop)
        words = TextMobject("Some 2d surface")
        words.next_to(arrow, RIGHT)

        anims = [
            ShowCreation(arrow),
            Write(words)
        ]
        for anim in anims:
            self.let_dots_wonder(
                random_seed = 1,
                added_anims = [anim],
                run_time = anim.run_time
            )
        self.let_dots_wonder(random_seed = 1, run_time = 10)

class AskAbouPairType(TeacherStudentsScene):
    def construct(self):
        self.student_says("""
            Do you mean ordered
            or unordered pairs?
        """)
        self.play(*[
            ApplyMethod(self.get_students()[i].change_mode, "confused")
            for i in 0, 2
        ])
        self.random_blink(3)

class DefineOrderedPair(ClosedLoopScene):
    def construct(self):
        title = TextMobject("Ordered pairs")
        title.to_edge(UP)
        subtitle = TexMobject(
            "(", "a", ",", "b", ")", 
            "\\ne", 
            "(", "b", ",", "a", ")"
        )
        labels_start = VGroup(subtitle[1], subtitle[3])
        labels_end = VGroup(subtitle[9], subtitle[7])
        subtitle.next_to(title, DOWN)
        colors = GREEN, RED
        for char, color in zip("ab", colors):
            subtitle.highlight_by_tex(char, color)
        self.loop.next_to(subtitle, DOWN)
        self.add(title, subtitle)

        self.add_dots_at_alphas(0.5, 0.6)
        dots = self.dots
        for dot, color, char in zip(dots, colors, "ab"):
            dot.highlight(color)
            label = TexMobject(char)
            label.highlight(color)
            label.next_to(dot, LEFT, buff = SMALL_BUFF)
            dot.label = label

        self.dither()
        self.play(*[
            Transform(label.copy(), dot.label)
            for label, dot in zip(labels_start, dots)
        ])
        self.remove(*self.get_mobjects_from_last_animation())
        self.add(*[d.label for d in dots])
        self.dither()
        self.play(
            dots[0].move_to, dots[1],
            dots[1].move_to, dots[0],
            *[
                MaintainPositionRelativeTo(dot.label, dot)
                for dot in dots
            ],
            path_arc = np.pi/2
        )
        self.play(*[
            Transform(dot.label.copy(), label)
            for dot, label in zip(dots, labels_end)
        ])
        self.dither()

class DefineUnorderedPair(ClosedLoopScene):
    def construct(self):
        title = TextMobject("Ordered pairs")
        title.to_edge(UP)
        subtitle = TexMobject(
            "\\{a,b\\}",
            "=",
            "\\{b,a\\}",
        )
        subtitle.next_to(title, DOWN)
        for char in "ab":
            subtitle.highlight_by_tex(char, PURPLE_B)
        self.loop.next_to(subtitle, DOWN)
        self.add(title, subtitle)

        self.add_dots_at_alphas(0.5, 0.6)
        dots = self.dots
        dots.highlight(PURPLE_B)

        labels = VGroup(*[subtitle[i].copy() for i in 0, 2])
        for label, vect in zip(labels, [LEFT, RIGHT]):
            label.next_to(dots, vect, LARGE_BUFF)
        arrows = [
            Arrow(*pair, color = PURPLE_B)
            for pair in it.product(labels, dots)
        ]
        arrow_pairs = [VGroup(*arrows[:2]), VGroup(*arrows[2:])]

        for label, arrow_pair in zip(labels, arrow_pairs):
            self.play(*map(FadeIn, [label, arrow_pair]))
            self.dither()
        for x in range(2):
            self.play(
                dots[0].move_to, dots[1],
                dots[1].move_to, dots[0],
                path_arc = np.pi/2
            )
            self.dither()

class DeformToInterval(ClosedLoopScene):
    def construct(self):
        interval = UnitInterval(color = WHITE)
        interval.shift(2*DOWN)
        numbers = interval.get_number_mobjects(0, 1)
        line = Line(interval.get_left(), interval.get_right())
        line.insert_n_anchor_points(self.loop.get_num_anchor_points())
        line.make_smooth()
        original_line = line.copy()

        self.loop.scale(0.7)
        self.loop.to_edge(UP)
        original_loop = self.loop.copy()
        cut_loop = self.loop.copy()
        cut_loop.points[0] += 0.3*(UP+RIGHT)
        cut_loop.points[-1] += 0.3*(DOWN+RIGHT)
        original_cut_loop = cut_loop.copy()

        #Unwrap loop
        self.transform_loop(cut_loop, path_arc = np.pi)
        self.dither()
        self.transform_loop(
            line,
            run_time = 3,
            path_arc = np.pi/2
        )
        self.dither()
        self.play(ShowCreation(interval))
        self.play(Write(numbers))
        self.dither()

        #Follow points
        self.loop = original_loop.copy()
        self.play(FadeIn(self.loop))
        self.add(original_loop)
        self.add_dots_at_alphas(*np.linspace(0, 1, 20))
        self.dots.gradient_highlight(BLUE, MAROON_C, BLUE)
        self.play(Write(self.dots))
        dots_copy = self.dots.copy()        
        self.add(dots_copy)
        self.dither()
        self.transform_loop(line, run_time = 3)
        self.dither()
        self.loop = original_loop
        self.dots = dots_copy
        self.transform_loop(original_cut_loop)
        self.dither()











