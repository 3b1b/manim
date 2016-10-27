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
            line = Line(
                d1.get_center(), d2.get_center(),
                stroke_width = 6
            )
            line.start_dot = d1 
            line.end_dot = d2
            line.update_anim = UpdateFromFunc(
                line,
                lambda l : l.put_start_and_end_on(
                    l.start_dot.get_center(),
                    l.end_dot.get_center()
                )
            )
            self.connecting_lines.add(line)
        self.connecting_lines.highlight(self.connecting_lines_color)
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
        alpha_rates = 0.1 + 0.1*np.random.random(len(list(self.dots)))
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
        self.add(self.loop)

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
        pair_colors = MAROON_B, PURPLE_C
        diag_lines = [
            Line(d1.get_center(), d2.get_center(), color = c)
            for (d1, d2), c in zip(dot_pairs, pair_colors)
        ]

        for pair, line in zip(dot_pairs, diag_lines):
            self.play(
                FadeIn(line),
                pair.highlight, line.get_color(),
            )




















