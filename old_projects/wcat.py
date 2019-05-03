from manimlib.imports import *


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
        dots.set_color(self.dot_color)
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
        self.add_dots(*self.get_rect_vertex_dots(square = square))

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
            pairs = adjacent_pairs(self.dots)
        else:
            n_pairs = len(list(self.dots))/2
            pairs = list(zip(self.dots[:n_pairs], self.dots[n_pairs:]))
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
            line.set_color(d1.get_color())
            self.connecting_lines.add(line)
        if cyclic:
            self.connecting_lines.set_color(self.connecting_lines_color)
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
        loop_points = np.array(list(map(self.loop.point_from_proportion, alpha_range)))
        for dot in dots:
            vects = loop_points - dot.get_center()
            norms = np.apply_along_axis(get_norm, 1, vects)
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

    def transform_loop(self, target_loop, added_anims = [], **kwargs):
        alphas = self.get_dot_alphas()
        dot_anims = []
        for dot, alpha in zip(self.dots, alphas):
            dot.generate_target()
            dot.target.move_to(target_loop.point_from_proportion(alpha))
            dot_anims.append(MoveToTarget(dot))
        self.play(
            Transform(self.loop, target_loop),
            *dot_anims + self.get_line_anims() + added_anims,
            **kwargs
        )

    def set_color_dots_by_pair(self):
        n_pairs = len(list(self.dots))/2
        for d1, d2, c in zip(self.dots[:n_pairs], self.dots[n_pairs:], self.pair_colors):
            VGroup(d1, d2).set_color(c)

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
            get_norm, 1,
            0.5*(all_quads[:,0] + all_quads[:,2]) - 0.5*(all_quads[:,1] + all_quads[:,3])
        )
        vects1 = all_quads[:,0] - all_quads[:,2]
        vects2 = all_quads[:,1] - all_quads[:,3]
        distances1 = np.apply_along_axis(get_norm, 1, vects1)
        distances2 = np.apply_along_axis(get_norm, 1, vects2)
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
        self.play(*list(map(MoveToTarget, self.get_students())))
        self.random_blink(3)
        self.teacher_says(
            "Here's why \\\\ I'm excited...",
            target_mode = "hooray"
        )
        for pi in self.get_students():
            pi.target.look_at(self.get_teacher().eyes)
        self.play(*list(map(MoveToTarget, self.get_students())))
        self.wait()

class WhenIWasAKid(TeacherStudentsScene):
    def construct(self):
        children = self.get_children()
        speaker = self.get_speaker()

        self.prepare_everyone(children, speaker)
        self.state_excitement(children, speaker)
        self.students = children
        self.teacher = speaker
        self.run_class()
        self.grow_up()

    def state_excitement(self, children, speaker):
        self.teacher_says(
            """
            Here's why 
            I'm excited!
            """,
            target_mode = "hooray"
        )
        self.change_student_modes(*["happy"]*3)
        self.wait()

        speaker.look_at(children)
        me = children[-1]
        self.play(
            FadeOut(self.get_students()),
            FadeOut(self.get_teacher().bubble),
            FadeOut(self.get_teacher().bubble.content),
            Transform(self.get_teacher(), me)
        )
        self.remove(self.get_teacher())
        self.add(me)
        self.play(*list(map(FadeIn, children[:-1] + [speaker])))
        self.random_blink()

    def run_class(self):
        children = self.students
        speaker = self.teacher
        title = TextMobject("Topology")
        title.to_edge(UP)
        pi1, pi2, pi3, me = children

        self.random_blink()
        self.teacher_says(
            """
            Math! Excitement!
            You are the future!
            """,
            target_mode = "hooray"
        )
        self.play(
            pi1.look_at, pi2.eyes,
            pi1.change_mode, "erm",
            pi2.look_at, pi1.eyes,
            pi2.change_mode, "surprised",
        )
        self.play(
            pi3.look_at, me.eyes,
            pi3.change_mode, "sassy",
            me.look_at, pi3.eyes,
        )
        self.random_blink(2)

        self.play(
            self.teacher.change_mode, "speaking",
            FadeOut(self.teacher.bubble),
            FadeOut(self.teacher.bubble.content),
        )
        self.play(Write(title))
        self.random_blink()
        
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
        self.wait()
        self.random_blink(2)
        self.play(pi1.change_mode, "raise_left_hand")
        self.wait()
        self.play(pi2.change_mode, "erm")
        self.random_blink()
        self.student_says(
            "How is this math?",
            student_index = -1,
            target_mode = "pleading",
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
            *list(map(FadeOut, [
                self.students, self.teacher,
                me.bubble, me.bubble.content
            ]))
        )
        self.remove(me)
        self.add(morty)
        self.play(Blink(morty))
        self.wait()
        self.play(morty.change_mode, "hooray")
        self.wait()


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
        children.arrange(RIGHT)
        children.to_edge(DOWN, buff = LARGE_BUFF)
        children.to_edge(LEFT)
        return children

    def get_speaker(self):
        speaker = Mathematician(mode = "happy")
        speaker.flip()
        speaker.to_edge(DOWN, buff = LARGE_BUFF)
        speaker.to_edge(RIGHT)
        return speaker

    def get_pi_creatures(self):
        if hasattr(self, "everyone"):
            return self.everyone
        else:
            return TeacherStudentsScene.get_pi_creatures(self)

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
        self.wait()
        self.play(ShowCreation(
            self.loop, 
            run_time = 5, 
            rate_func=linear
        ))
        self.wait()
        self.add_rect_dots(square = True)
        self.play(ShowCreation(self.dots, run_time = 2))
        self.wait()
        self.add_connecting_lines(cyclic = True)
        self.play(
            ShowCreation(
                self.connecting_lines,
                lag_ratio = 0,
                run_time = 2
            ),
            Animation(self.dots)
        )
        self.wait(2)

    def cycle_through_shapes(self):
        circle = Circle(radius = 2.5, color = WHITE)
        ellipse = circle.copy()
        ellipse.stretch(1.5, 0)
        ellipse.stretch(0.7, 1)
        ellipse.rotate(-np.pi/2)
        ellipse.set_height(4)
        pi_loop = TexMobject("\\pi")[0]
        pi_loop.set_fill(opacity = 0)
        pi_loop.set_stroke(
            color = WHITE,
            width = DEFAULT_STROKE_WIDTH
        )
        pi_loop.set_height(4)
        randy = Randolph()
        randy.look(DOWN)
        randy.set_width(pi_loop.get_width())
        randy.move_to(pi_loop, aligned_edge = DOWN)
        randy.body.set_fill(opacity = 0)
        randy.mouth.set_stroke(width = 0)

        self.transform_loop(circle)
        self.remove(self.loop)
        self.loop = circle
        self.add(self.loop, self.connecting_lines, self.dots)
        self.wait()
        odd_eigths = np.linspace(1./8, 7./8, 4)
        self.move_dots_to_alphas(odd_eigths)
        self.wait()
        for nudge in 0.1, -0.1, 0:
            self.move_dots_to_alphas(odd_eigths+nudge)
        self.wait()
        self.transform_loop(ellipse)
        self.wait()
        nudge = 0.055
        self.move_dots_to_alphas(
            odd_eigths + [nudge, -nudge, nudge, -nudge]
        )
        self.wait(2)
        self.transform_loop(pi_loop)
        self.let_dots_wonder()
        randy_anims = [
            FadeIn(randy),
            Animation(randy),            
            Blink(randy),
            Animation(randy),         
            Blink(randy),
            Animation(randy),
            Blink(randy, rate_func = smooth)
        ]
        for anim in randy_anims:
            self.let_dots_wonder(
                run_time = 1.5,
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
        new_title.set_color_by_tex("rectangle", YELLOW)
        new_title.to_edge(UP)
        rect_dots = self.get_rect_vertex_dots()
        rect_alphas = self.get_dot_alphas(rect_dots)

        self.play(FadeIn(morty))
        self.play(morty.change_mode, "speaking")
        self.play(Transform(self.title, new_title))
        self.move_dots_to_alphas(rect_alphas)
        self.wait()
        self.play(morty.change_mode, "hooray")
        self.play(Blink(morty))
        self.wait()
        self.play(FadeOut(self.connecting_lines))
        self.connecting_lines = VGroup()
        self.play(morty.change_mode, "plain")

        dot_pairs = [
            VGroup(self.dots[i], self.dots[j])
            for i, j in [(0, 2), (1, 3)]
        ]
        pair_colors = MAROON_B, PURPLE_B
        diag_lines = [
            Line(d1.get_center(), d2.get_center(), color = c)
            for (d1, d2), c in zip(dot_pairs, pair_colors)
        ]

        for pair, line in zip(dot_pairs, diag_lines):
            self.play(
                FadeIn(line),
                pair.set_color, line.get_color(),
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
            for i, j in [(0, 2), (1, 3)]
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
        self.wait()
        self.play(
            ShowCreation(vertex_dots),
            Write(labels)
        )
        self.wait()
        mob_lists = [
            (a, c, dot_pairs[0]),
            (b, d, dot_pairs[1]),
        ]
        for color, mob_list in zip(colors, mob_lists):
            self.play(*[
                ApplyMethod(mob.set_color, color)
                for mob in mob_list
            ])
            self.wait()
        for line, brace in zip(diag_lines, braces):
            self.play(
                ShowCreation(line),
                GrowFromCenter(brace)
            )
            self.wait()
            self.play(FadeOut(brace))
        self.play(FadeIn(midpoint))
        self.wait()

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
            label.set_color(dot.get_color())
            labels.add(label)
        lines = [
            Line(
                dots[i].get_center(), 
                dots[j].get_center(), 
                color = dots[i].get_color()
            )
            for i, j in [(0, 1), (2, 3)]
        ]
        groups = [
            VGroup(dots[0], dots[1], labels[0], labels[1], lines[0]),
            VGroup(dots[2], dots[3], labels[2], labels[3], lines[1]),
        ]
        midpoint = Dot(LEFT, color = RED)

        words = VGroup(*list(map(TextMobject, [
            "Common midpoint",
            "Same distance apart",
            "$\\Downarrow$",
            "Rectangle",
        ])))
        words.arrange(DOWN)
        words.to_edge(RIGHT)
        words[-1].set_color(BLUE)

        self.play(
            ShowCreation(dots),
            Write(labels)
        )
        self.play(*list(map(ShowCreation, lines)))
        self.wait()
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
        self.wait()

        rectangle = Polygon(*[
            dots[i].get_center()
            for i in (0, 2, 1, 3)
        ])
        rectangle.set_color(BLUE)
        self.play(
            ShowCreation(rectangle),
            Animation(dots)
        )
        self.play(*list(map(Write, words[2:])))
        self.wait()

class SearchForRectangleOnLoop(ClosedLoopScene):
    def construct(self):
        self.add_dots_at_alphas(*np.linspace(0.2, 0.8, 4))
        self.set_color_dots_by_pair()
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
        self.wait()
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
        self.wait()
        self.add_connecting_lines(cyclic = True)
        self.play(
            ShowCreation(self.connecting_lines), 
            Animation(self.dots)
        )
        self.wait()

class DeclareFunction(ClosedLoopScene):
    def construct(self):
        self.add_dots_at_alphas(0.2, 0.8)
        self.set_color_dots_by_pair()        
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
        ab_brace.set_color_by_gradient(MAROON_B, PURPLE_B)
        xyz_brace.set_color(BLUE)

        self.add(tex)
        self.play(Write(ab_brace))
        self.wait()
        self.play(Write(xyz_brace))
        self.wait()

class DefinePairTo3dFunction(Scene):
    def construct(self):
        pass

class LabelMidpoint(Scene):
    def construct(self):
        words = TextMobject("Midpoint $M$")
        words.set_color(RED)
        words.scale(2)
        self.play(Write(words, run_time = 1))
        self.wait()

class LabelDistance(Scene):
    def construct(self):
        words = TextMobject("Distance $d$")
        words.set_color(MAROON_B)
        words.scale(2)
        self.play(Write(words, run_time = 1))
        self.wait()

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
        tex.set_color_by_tex("=X", BLUE)
        tex.scale(2)
        self.play(Write(tex[0]))
        self.wait(2)
        self.play(Write(tex[1]))
        self.wait(2)

class WigglePairUnderSurface(Scene):
    def construct(self):
        pass        

class WriteContinuous(Scene):
    def construct(self):
        self.play(Write(TextMobject("Continuous").scale(2)))
        self.wait(2)

class DistinctPairCollisionOnSurface(Scene):
    def construct(self):
        pass

class PairsOfPointsOnLoop(ClosedLoopScene):
    def construct(self):
        self.add_dots_at_alphas(0.2, 0.5)
        self.dots.set_color(MAROON_B)
        self.add_connecting_lines()
        self.let_dots_wonder(run_time = 10)

class PairOfRealsToPlane(Scene):
    def construct(self):
        r1, r2 = numbers = -3, 2
        colors = GREEN, RED
        dot1, dot2 = dots = VGroup(*[Dot(color = c) for c in colors])
        for dot, number in zip(dots, numbers):
            dot.move_to(number*RIGHT)
        pair_label = TexMobject("(", str(r1), ",", str(r2), ")")
        for number, color in zip(numbers, colors):
            pair_label.set_color_by_tex(str(number), color)
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
        self.wait()
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
        self.play(*list(map(ShowCreation, lines)))
        self.play(ShowCreation(two_d_point))
        everything = VGroup(*self.get_mobjects())
        self.play(
            FadeIn(plane), 
            Animation(everything),
            Animation(dot2)
        )
        self.wait()

class SeekSurfaceForPairs(ClosedLoopScene):
    def construct(self):
        self.loop.to_edge(LEFT)
        self.add_dots_at_alphas(0.2, 0.3)
        self.set_color_dots_by_pair()        
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
            for i in (0, 2)
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
            subtitle.set_color_by_tex(char, color)
        self.loop.next_to(subtitle, DOWN)
        self.add(title, subtitle)

        self.add_dots_at_alphas(0.5, 0.6)
        dots = self.dots
        for dot, color, char in zip(dots, colors, "ab"):
            dot.set_color(color)
            label = TexMobject(char)
            label.set_color(color)
            label.next_to(dot, RIGHT, buff = SMALL_BUFF)
            dot.label = label
        self.dots[1].label.shift(0.3*UP)
        first = TextMobject("First")
        first.next_to(self.dots[0], UP+2*LEFT, LARGE_BUFF)
        arrow = Arrow(first.get_bottom(), self.dots[0], color = GREEN)

        self.wait()
        self.play(*[
            Transform(label.copy(), dot.label)
            for label, dot in zip(labels_start, dots)
        ])
        self.remove(*self.get_mobjects_from_last_animation())
        self.add(*[d.label for d in dots])
        self.wait()
        self.play(
            Write(first),
            ShowCreation(arrow)
        )
        self.wait()

class DefineUnorderedPair(ClosedLoopScene):
    def construct(self):
        title = TextMobject("Unordered pairs")
        title.to_edge(UP)
        subtitle = TexMobject(
            "\\{a,b\\}",
            "=",
            "\\{b,a\\}",
        )
        subtitle.next_to(title, DOWN)
        for char in "ab":
            subtitle.set_color_by_tex(char, PURPLE_B)
        self.loop.next_to(subtitle, DOWN)
        self.add(title, subtitle)

        self.add_dots_at_alphas(0.5, 0.6)
        dots = self.dots
        dots.set_color(PURPLE_B)

        labels = VGroup(*[subtitle[i].copy() for i in (0, 2)])
        for label, vect in zip(labels, [LEFT, RIGHT]):
            label.next_to(dots, vect, LARGE_BUFF)
        arrows = [
            Arrow(*pair, color = PURPLE_B)
            for pair in it.product(labels, dots)
        ]
        arrow_pairs = [VGroup(*arrows[:2]), VGroup(*arrows[2:])]

        for label, arrow_pair in zip(labels, arrow_pairs):
            self.play(*list(map(FadeIn, [label, arrow_pair])))
            self.wait()
        for x in range(2):
            self.play(
                dots[0].move_to, dots[1],
                dots[1].move_to, dots[0],
                path_arc = np.pi/2
            )
            self.wait()

class BeginWithOrdered(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            One must know order
            before he can ignore it.
        """)
        self.random_blink(3)

class DeformToInterval(ClosedLoopScene):
    def construct(self):
        interval = UnitInterval(color = WHITE)
        interval.shift(2*DOWN)
        numbers = interval.get_number_mobjects(0, 1)
        line = Line(interval.get_left(), interval.get_right())
        line.insert_n_curves(self.loop.get_num_curves())
        line.make_smooth()

        self.loop.scale(0.7)
        self.loop.to_edge(UP)
        original_loop = self.loop.copy()
        cut_loop = self.loop.copy()
        cut_loop.points[0] += 0.3*(UP+RIGHT)
        cut_loop.points[-1] += 0.3*(DOWN+RIGHT)

        #Unwrap loop
        self.transform_loop(cut_loop, path_arc = np.pi)
        self.wait()
        self.transform_loop(
            line,
            run_time = 3,
            path_arc = np.pi/2
        )
        self.wait()
        self.play(ShowCreation(interval))
        self.play(Write(numbers))
        self.wait()

        #Follow points
        self.loop = original_loop.copy()
        self.play(FadeIn(self.loop))
        self.add(original_loop)
        self.add_dots_at_alphas(*np.linspace(0, 1, 20))
        self.dots.set_color_by_gradient(BLUE, MAROON_C, BLUE)
        dot_at_1 = self.dots[-1]
        dot_at_1.generate_target()
        dot_at_1.target.move_to(interval.get_right())
        dots_copy = self.dots.copy()
        fading_dots = VGroup(*list(self.dots)+list(dots_copy))
        end_dots = VGroup(
            self.dots[0], self.dots[-1],
            dots_copy[0], dots_copy[-1]
        )
        fading_dots.remove(*end_dots)

        self.play(Write(self.dots))
        self.add(dots_copy)
        self.wait()
        self.transform_loop(
            line, 
            added_anims = [MoveToTarget(dot_at_1)],
            run_time = 3
        )
        self.wait()
        self.loop = original_loop
        self.dots = dots_copy
        dot_at_1 = self.dots[-1]
        dot_at_1.target.move_to(cut_loop.points[-1])
        self.transform_loop(
            cut_loop,
            added_anims = [MoveToTarget(dot_at_1)]
        )
        self.wait()
        fading_dots.generate_target()
        fading_dots.target.set_fill(opacity = 0.3)
        self.play(MoveToTarget(fading_dots))
        self.play(
            end_dots.shift, 0.2*UP, 
            rate_func = wiggle
        )
        self.wait()

class RepresentPairInUnitSquare(ClosedLoopScene):
    def construct(self):
        interval = UnitInterval(color = WHITE)
        interval.shift(2.5*DOWN)
        interval.shift(LEFT)
        numbers = interval.get_number_mobjects(0, 1)
        line = Line(interval.get_left(), interval.get_right())
        line.insert_n_curves(self.loop.get_num_curves())
        line.make_smooth()
        vert_interval = interval.copy()
        square = Square()
        square.set_width(interval.get_width())
        square.set_stroke(width = 0)
        square.set_fill(color = BLUE, opacity = 0.3)
        square.move_to(
            interval.get_left(),
            aligned_edge = DOWN+LEFT
        )

        right_words = VGroup(*[
            TextMobject("Pair of\\\\ loop points"),
            TexMobject("\\Downarrow"),
            TextMobject("Point in \\\\ unit square")
        ])
        right_words.arrange(DOWN)
        right_words.to_edge(RIGHT)

        dot_coords = (0.3, 0.7)
        self.loop.scale(0.7)
        self.loop.to_edge(UP)
        self.add_dots_at_alphas(*dot_coords)
        self.dots.set_color_by_gradient(GREEN, RED)

        self.play(
            Write(self.dots),
            Write(right_words[0])
        )
        self.wait()
        self.transform_loop(line)
        self.play(
            ShowCreation(interval),
            Write(numbers),
            Animation(self.dots)
        )
        self.wait()
        self.play(*[
            Rotate(mob, np.pi/2, about_point = interval.get_left())
            for mob in (vert_interval, self.dots[1])
        ])

        #Find interior point
        point = self.dots[0].get_center()[0]*RIGHT
        point += self.dots[1].get_center()[1]*UP
        inner_dot = Dot(point, color = YELLOW)
        dashed_lines = VGroup(*[
            DashedLine(dot, inner_dot, color = dot.get_color())
            for dot in self.dots
        ])
        self.play(ShowCreation(dashed_lines))
        self.play(ShowCreation(inner_dot))
        self.play(
            FadeIn(square),
            Animation(self.dots),
            *list(map(Write, right_words[1:]))
        )
        self.wait()

        #Shift point in square

        movers = list(dashed_lines)+list(self.dots)+[inner_dot]
        for mob in movers:
            mob.generate_target()
        shift_vals = [
            RIGHT+DOWN, 
            LEFT+DOWN, 
            LEFT+2*UP,
            3*DOWN,
            2*RIGHT+UP,
            RIGHT+UP,
            3*LEFT+3*DOWN
        ]
        for shift_val in shift_vals:
            inner_dot.target.shift(shift_val)
            self.dots[0].target.shift(shift_val[0]*RIGHT)
            self.dots[1].target.shift(shift_val[1]*UP)
            for line, dot in zip(dashed_lines, self.dots):
                line.target.put_start_and_end_on(
                    dot.target.get_center(), 
                    inner_dot.target.get_center()
                )
            self.play(*list(map(MoveToTarget, movers)))
        self.wait()
        self.play(*list(map(FadeOut, [dashed_lines, self.dots])))

class EdgesOfSquare(Scene):
    def construct(self):
        square = self.add_square()
        x_edges, y_edges = self.get_edges(square)
        label_groups = self.get_coordinate_labels(square)
        arrow_groups = self.get_arrows(x_edges, y_edges)

        for edge in list(x_edges) + list(y_edges):
            self.play(ShowCreation(edge))
        self.wait()
        for label_group in label_groups:
            for label in label_group[:3]:
                self.play(FadeIn(label))
            self.wait()
            self.play(Write(VGroup(*label_group[3:])))
            self.wait()
        self.play(FadeOut(VGroup(*label_groups)))
        for arrows in arrow_groups:
            self.play(ShowCreation(arrows, run_time = 2))
            self.wait()
        self.play(*[
            ApplyMethod(
                n.next_to,
                square.get_corner(vect+LEFT),
                LEFT,
                MED_SMALL_BUFF,
                path_arc = np.pi/2
            )
            for n, vect in zip(self.numbers, [DOWN, UP])
        ])
        self.wait()

    def add_square(self):
        interval = UnitInterval(color = WHITE)
        interval.shift(2.5*DOWN)
        bottom_left = interval.get_left()
        for tick in interval.tick_marks:
            height = tick.get_height()
            tick.scale_in_place(0.5)
            tick.shift(height*DOWN/4.)
        self.numbers = interval.get_number_mobjects(0, 1)
        vert_interval = interval.copy()
        vert_interval.rotate(np.pi, axis = UP+RIGHT, about_point = bottom_left)
        square = Square()
        square.set_width(interval.get_width())
        square.set_stroke(width = 0)
        square.set_fill(color = BLUE, opacity = 0.3)
        square.move_to(
            bottom_left,
            aligned_edge = DOWN+LEFT
        )
        self.add(interval, self.numbers, vert_interval, square)
        return square

    def get_edges(self, square):
        y_edges = VGroup(*[
            Line(
                square.get_corner(vect+LEFT),
                square.get_corner(vect+RIGHT),
            )
            for vect in (DOWN, UP)
        ])
        y_edges.set_color(BLUE)
        x_edges = VGroup(*[
            Line(
                square.get_corner(vect+DOWN),
                square.get_corner(vect+UP),
            )
            for vect in (LEFT, RIGHT)
        ])
        x_edges.set_color(MAROON_B)
        return x_edges, y_edges

    def get_coordinate_labels(self, square):
        alpha_range = np.arange(0, 1.1, 0.1)
        dot_groups = [
            VGroup(*[
                Dot(interpolate(
                    square.get_corner(DOWN+vect),
                    square.get_corner(UP+vect),
                    alpha
                ))
                for alpha in alpha_range
            ])
            for vect in (LEFT, RIGHT)            
        ]
        for group in dot_groups:
            group.set_color_by_gradient(YELLOW, PURPLE_B)
        label_groups = [
            VGroup(*[
                TexMobject("(%s, %s)"%(a, b)).scale(0.7)
                for b in alpha_range
            ])
            for a in (0, 1)
        ]
        for dot_group, label_group in zip(dot_groups, label_groups):
            for dot, label in zip(dot_group, label_group):
                label[1].set_color(MAROON_B)
                label.next_to(dot, RIGHT*np.sign(dot.get_center()[0]))
                label.add(dot)
        return label_groups

    def get_arrows(self, x_edges, y_edges):
        alpha_range = np.linspace(0, 1, 4)
        return [
            VGroup(*[
                VGroup(*[
                    Arrow(
                        edge.point_from_proportion(a1),
                        edge.point_from_proportion(a2),
                        buff = 0
                    )
                    for a1, a2 in zip(alpha_range, alpha_range[1:])
                ])
                for edge in edges
            ]).set_color(edges.get_color())
            for edges in (x_edges, y_edges)
        ]

class EndpointsGluedTogether(ClosedLoopScene):
    def construct(self):
        interval = UnitInterval(color = WHITE)
        interval.shift(2*DOWN)
        numbers = interval.get_number_mobjects(0, 1)
        line = Line(interval.get_left(), interval.get_right())
        line.insert_n_curves(self.loop.get_num_curves())
        line.make_smooth()

        self.loop.scale(0.7)
        self.loop.to_edge(UP)
        original_loop = self.loop
        self.remove(original_loop)

        self.loop = line
        dots = VGroup(*[
            Dot(line.get_critical_point(vect))
            for vect in (LEFT, RIGHT)
        ])
        dots.set_color(BLUE)

        self.add(interval, dots)
        self.play(dots.rotate_in_place, np.pi/20, rate_func = wiggle)
        self.wait()
        self.transform_loop(
            original_loop,
            added_anims = [
                ApplyMethod(dot.move_to, original_loop.points[0])
                for dot in dots
            ],
            run_time = 3
        )
        self.wait()

class WrapUpToTorus(Scene):
    def construct(self):
        pass

class TorusPlaneAnalogy(ClosedLoopScene):
    def construct(self):
        top_arrow = DoubleArrow(LEFT, RIGHT)
        top_arrow.to_edge(UP, buff = 2*LARGE_BUFF)
        single_pointed_top_arrow = Arrow(LEFT, RIGHT)
        single_pointed_top_arrow.to_edge(UP, buff = 2*LARGE_BUFF)        
        low_arrow = DoubleArrow(LEFT, RIGHT).shift(2*DOWN)
        self.loop.scale(0.5)
        self.loop.next_to(top_arrow, RIGHT)
        self.loop.shift_onto_screen()
        self.add_dots_at_alphas(0.3, 0.5)
        self.dots.set_color_by_gradient(GREEN, RED)

        plane = NumberPlane()
        plane.scale(0.3).next_to(low_arrow, LEFT)
        number_line = NumberLine()
        number_line.scale(0.3)
        number_line.next_to(low_arrow, RIGHT)
        number_line.add(
            Dot(number_line.number_to_point(3), color = GREEN),
            Dot(number_line.number_to_point(-2), color = RED),
        )

        self.wait()
        self.play(ShowCreation(single_pointed_top_arrow))
        self.wait()
        self.play(ShowCreation(top_arrow))
        self.wait()
        self.play(ShowCreation(plane))
        self.play(ShowCreation(low_arrow))
        self.play(ShowCreation(number_line))
        self.wait()

class WigglingPairOfPoints(ClosedLoopScene):
    def construct(self):
        alpha_pairs = [
            (0.4, 0.6),
            (0.42, 0.62),
        ]
        self.add_dots_at_alphas(*alpha_pairs[-1])
        self.add_connecting_lines()
        self.dots.set_color_by_gradient(GREEN, RED)
        self.connecting_lines.set_color(YELLOW)
        for x, pair in zip(list(range(20)), it.cycle(alpha_pairs)):
            self.move_dots_to_alphas(pair, run_time = 0.3)


class WigglingTorusPoint(Scene):
        def construct(self):
            pass    

class WhatAboutUnordered(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "What about \\\\ unordered pairs?"
        )
        self.play(self.get_teacher().change_mode, "pondering")
        self.random_blink(2)

class TrivialPairCollision(ClosedLoopScene):
    def construct(self):
        self.loop.to_edge(RIGHT)
        self.add_dots_at_alphas(0.35, 0.55)
        self.dots.set_color_by_gradient(BLUE, YELLOW)
        a, b = self.dots
        a_label = TexMobject("a").next_to(a, RIGHT)
        a_label.set_color(a.get_color())
        b_label = TexMobject("b").next_to(b, LEFT)
        b_label.set_color(b.get_color())
        line = Line(
            a.get_corner(DOWN+LEFT),
            b.get_corner(UP+RIGHT),
            color = MAROON_B
        )
        midpoint = Dot(self.dots.get_center(), color = RED)
        randy = Randolph(mode = "pondering")
        randy.next_to(self.loop, LEFT, aligned_edge = DOWN)
        randy.look_at(b)
        self.add(randy)

        for label in a_label, b_label:
            self.play(
                Write(label, run_time = 1),
                randy.look_at, label
            )
        self.play(Blink(randy))
        self.wait()
        swappers = [a, b, a_label, b_label]
        for mob in swappers:
            mob.save_state()
        self.play(
            a.move_to, b,
            b.move_to, a,
            a_label.next_to, b, LEFT,
            b_label.next_to, a, RIGHT,
            randy.look_at, a,
            path_arc = np.pi
        )
        self.play(ShowCreation(midpoint))
        self.play(ShowCreation(line), Animation(midpoint))
        self.play(randy.change_mode, "erm", randy.look_at, b)
        self.play(
            randy.look_at, a,
            *[m.restore for m in swappers],
            path_arc = -np.pi
        )
        self.play(Blink(randy))
        self.wait()

class NotHelpful(Scene):
    def construct(self):
        morty = Mortimer()
        morty.next_to(ORIGIN, DOWN)
        bubble = morty.get_bubble(SpeechBubble, width = 4, height = 3)
        bubble.write("Not helpful!")

        self.add(morty)
        self.play(
            FadeIn(bubble),
            FadeIn(bubble.content),
            morty.change_mode, "angry",
            morty.look, OUT
        )
        self.play(Blink(morty))
        self.wait()

class FoldUnitSquare(EdgesOfSquare):
    def construct(self):    
        self.add_triangles()
        self.add_arrows()
        self.show_points_to_glue()
        self.perform_fold()
        self.show_singleton_pairs()
        self.ask_about_gluing()
        self.clarify_edge_gluing()

    def add_triangles(self):
        square = self.add_square()
        triangles = VGroup(*[
            Polygon(*[square.get_corner(vect) for vect in vects])
            for vects in [
                (DOWN+LEFT, UP+RIGHT, UP+LEFT),            
                (DOWN+LEFT, UP+RIGHT, DOWN+RIGHT),
            ]
        ])
        triangles.set_stroke(width = 0)
        triangles.set_fill(
            color = square.get_color(), 
            opacity = square.get_fill_opacity()
        )
        self.remove(square)
        self.square = square
        self.add(triangles)
        self.triangles = triangles

    def add_arrows(self):
        start_arrows = VGroup()
        end_arrows = VGroup()
        colors = MAROON_B, BLUE
        for a in 0, 1:        
            for color in colors:
                b_range = np.linspace(0, 1, 4)
                for b1, b2 in zip(b_range, b_range[1:]):
                    arrow = Arrow(
                        self.get_point_from_coords(a, b1),
                        self.get_point_from_coords(a, b2),
                        buff = 0,
                        color = color
                    )
                    if color is BLUE:
                        arrow.rotate(
                            -np.pi/2, 
                            about_point = self.square.get_center()
                        )
                    if (a is 0):
                        start_arrows.add(arrow)
                    else:
                        end_arrows.add(arrow)
        self.add(start_arrows, end_arrows)
        self.start_arrows = start_arrows
        self.end_arrows = VGroup(*list(end_arrows[3:])+list(end_arrows[:3])).copy()
        self.end_arrows.set_color(
            color_gradient([MAROON_B, BLUE], 3)[1]
        )

    def show_points_to_glue(self):
        colors = YELLOW, MAROON_B, PINK
        pairs = [(0.2, 0.3), (0.5, 0.7), (0.25, 0.6)]
        unit = self.square.get_width()

        start_dots = VGroup()
        end_dots = VGroup()
        for (x, y), color in zip(pairs, colors):
            old_x_line, old_y_line = None, None
            for (a, b) in (x, y), (y, x):
                point = self.get_point_from_coords(a, b)
                dot = Dot(point)
                dot.set_color(color)
                if color == colors[-1]:
                    s = "(x, y)" if a < b else "(y, x)"
                    label = TexMobject(s)
                else:
                    label = TexMobject("(%.01f, %.01f)"%(a, b))
                vect = UP+RIGHT if a < b else DOWN+RIGHT
                label.next_to(dot, vect, buff = SMALL_BUFF)

                self.play(*list(map(FadeIn, [dot, label])))
                x_line = Line(point+a*unit*LEFT, point)
                y_line = Line(point+b*unit*DOWN, point)
                x_line.set_color(GREEN)
                y_line.set_color(RED)
                if old_x_line is None:
                    self.play(ShowCreation(x_line), Animation(dot))
                    self.play(ShowCreation(y_line), Animation(dot))
                    old_x_line, old_y_line = y_line, x_line
                else:
                    self.play(Transform(old_x_line, x_line), Animation(dot))
                    self.play(Transform(old_y_line, y_line), Animation(dot))
                    self.remove(old_x_line, old_y_line)
                    self.add(x_line, y_line, dot)
                self.wait(2)
                self.play(FadeOut(label))
                if a < b:
                    start_dots.add(dot)
                else:
                    end_dots.add(dot)
            self.play(*list(map(FadeOut, [x_line, y_line])))
        self.start_dots, self.end_dots = start_dots, end_dots

    def perform_fold(self):
        diag_line = DashedLine(
            self.square.get_corner(DOWN+LEFT),
            self.square.get_corner(UP+RIGHT),
            color = RED
        )

        self.play(ShowCreation(diag_line))
        self.wait()
        self.play(
            Transform(*self.triangles),
            Transform(self.start_dots, self.end_dots),
            Transform(self.start_arrows, self.end_arrows),
        )
        self.wait()
        self.diag_line = diag_line

    def show_singleton_pairs(self):
        xs = [0.7, 0.4, 0.5]
        old_label = None
        old_dot = None
        for x in xs:
            point = self.get_point_from_coords(x, x)
            dot = Dot(point)
            if x is xs[-1]:
                label = TexMobject("(x, x)")
            else:
                label = TexMobject("(%.1f, %.1f)"%(x, x))
            label.next_to(dot, UP+LEFT, buff = SMALL_BUFF)
            VGroup(dot, label).set_color(RED)
            if old_label is None:
                self.play(
                    ShowCreation(dot),
                    Write(label)
                )
                old_label = label
                old_dot = dot
            else:
                self.play(
                    Transform(old_dot, dot),
                    Transform(old_label, label),
                )
            self.wait()
        #Some strange bug necesitating this
        self.remove(old_label)
        self.add(label)

    def ask_about_gluing(self):
        keepers = VGroup(
            self.triangles[0],
            self.start_arrows,
            self.diag_line
        ).copy()
        faders = VGroup(*self.get_mobjects())
        randy = Randolph()
        randy.next_to(ORIGIN, DOWN)
        bubble = randy.get_bubble(height = 4, width = 6)
        bubble.write("How do you \\\\ glue those arrows?")

        self.play(
            FadeOut(faders),
            Animation(keepers)
        )
        self.play(
            keepers.scale, 0.6,
            keepers.shift, 4*RIGHT + UP,
            FadeIn(randy)
        )
        self.play(
            randy.change_mode, "pondering",
            randy.look_at, keepers,
            ShowCreation(bubble),
            Write(bubble.content)
        )
        self.play(Blink(randy))
        self.wait()
        self.randy = randy

    def clarify_edge_gluing(self):
        dots = VGroup(*[
            Dot(self.get_point_from_coords(*coords), radius = 0.1)
            for coords in [
                (0.1, 0),
                (1, 0.1),
                (0.9, 0),
                (1, 0.9),
            ]
        ])
        dots.scale(0.6)
        dots.shift(4*RIGHT + UP)
        for dot in dots[:2]:
            dot.set_color(YELLOW)
            self.play(
                ShowCreation(dot),
                self.randy.look_at, dot
            )
        self.wait()
        for dot in dots[2:]:
            dot.set_color(MAROON_B)
            self.play(
                ShowCreation(dot),
                self.randy.look_at, dot
            )
        self.play(Blink(self.randy))
        self.wait()

    def get_point_from_coords(self, x, y):
        left, right, bottom, top = [
            self.triangles.get_edge_center(vect)
            for vect in (LEFT, RIGHT, DOWN, UP)
        ]
        x_point = interpolate(left, right, x)
        y_point = interpolate(bottom, top, y)
        return x_point[0]*RIGHT + y_point[1]*UP

class PrepareForMobiusStrip(Scene):
    def construct(self):
        self.add_triangles()
        self.perform_cut()
        self.rearrange_pieces()

    def add_triangles(self):
        triangles = VGroup(
            Polygon(
                DOWN+LEFT,
                DOWN+RIGHT,
                ORIGIN,
            ),
            Polygon(
                DOWN+RIGHT,
                UP+RIGHT,          
                ORIGIN,
            ),
        )
        triangles.set_fill(color = BLUE, opacity = 0.6)
        triangles.set_stroke(width = 0)
        triangles.center()
        triangles.scale(2)
        arrows_color = color_gradient([PINK, BLUE], 3)[1]
        for tri in triangles:
            anchors = tri.get_anchors_and_handles()[0]
            alpha_range = np.linspace(0, 1, 4)
            arrows = VGroup(*[
                Arrow(
                    interpolate(anchors[0], anchors[1], a),
                    interpolate(anchors[0], anchors[1], b),
                    buff = 0,
                    color = arrows_color
                )
                for a, b in zip(alpha_range, alpha_range[1:])
            ])
            tri.original_arrows = arrows
            tri.add(arrows)
            i, j, k = (0, 2, 1) if tri is triangles[0] else (1, 2, 0)
            dashed_line = DashedLine(
                anchors[i], anchors[j], 
                color = RED
            )
            tri.add(dashed_line)

            #Add but don't draw cut_arrows
            start, end = anchors[j], anchors[k]
            cut_arrows = VGroup(*[
                Arrow(
                    interpolate(start, end, a),
                    interpolate(start, end, b),
                    buff = 0,
                    color = YELLOW
                )
                for a, b in zip(alpha_range, alpha_range[1:])
            ])
            tri.cut_arrows = cut_arrows
        self.add(triangles)
        self.triangles = triangles

    def perform_cut(self):
        tri1, tri2 = self.triangles


        self.play(ShowCreation(tri1.cut_arrows))
        for tri in self.triangles:
            tri.add(tri.cut_arrows)
        self.wait()
        self.play(
            tri1.shift, (DOWN+LEFT)/2.,
            tri2.shift, (UP+RIGHT)/2.,
        )
        self.wait()

    def rearrange_pieces(self):
        tri1, tri2 = self.triangles
        self.play(
            tri1.rotate, np.pi, UP+RIGHT,
            tri1.next_to, ORIGIN, RIGHT,
            tri2.next_to, ORIGIN, LEFT,
        )
        self.wait()
        self.play(*[
            ApplyMethod(tri.shift, tri.points[0][0]*LEFT)
            for tri in self.triangles
        ])
        self.play(*[
            FadeOut(tri.original_arrows)
            for tri in self.triangles
        ])
        for tri in self.triangles:
            tri.remove(tri.original_arrows)
        self.wait()
        # self.play(*[
        #     ApplyMethod(tri.rotate, -np.pi/4)
        #     for tri in self.triangles
        # ])
        # self.wait()

class FoldToMobius(Scene):
    def construct(self):
        pass

class MobiusPlaneAnalogy(ClosedLoopScene):
    def construct(self):
        top_arrow = Arrow(LEFT, RIGHT)
        top_arrow.to_edge(UP, buff = 2*LARGE_BUFF)
        low_arrow = Arrow(LEFT, RIGHT).shift(2*DOWN)
        self.loop.scale(0.5)
        self.loop.next_to(top_arrow, RIGHT)
        self.loop.shift_onto_screen()
        self.add_dots_at_alphas(0.3, 0.5)
        self.dots.set_color(PURPLE_B)

        plane = NumberPlane()
        plane.scale(0.3).next_to(low_arrow, LEFT)
        number_line = NumberLine()
        number_line.scale(0.3)
        number_line.next_to(low_arrow, RIGHT)
        number_line.add(
            Dot(number_line.number_to_point(3), color = GREEN),
            Dot(number_line.number_to_point(-2), color = RED),
        )

        self.wait()
        self.play(ShowCreation(top_arrow))
        self.wait()
        self.play(ShowCreation(plane))
        self.play(ShowCreation(low_arrow))
        self.play(ShowCreation(number_line))
        self.wait()

class DrawRightArrow(Scene):
    CONFIG = {
        "tex" : "\\Rightarrow"
    }
    def construct(self):
        arrow = TexMobject(self.tex)
        arrow.scale(4)
        self.play(Write(arrow))
        self.wait()

class DrawLeftrightArrow(DrawRightArrow):
    CONFIG = {
        "tex" : "\\Leftrightarrow"
    }

class MobiusToPairToSurface(ClosedLoopScene):
    def construct(self):
        self.loop.scale(0.5)
        self.loop.next_to(ORIGIN, RIGHT)
        self.loop.to_edge(UP)
        self.add_dots_at_alphas(0.4, 0.6)
        self.dots.set_color(MAROON_B)
        self.add_connecting_lines()
        strip_dot = Dot().next_to(self.loop, LEFT, buff = 2*LARGE_BUFF)
        surface_dot = Dot().next_to(self.loop, DOWN, buff = 2*LARGE_BUFF)

        top_arrow = Arrow(strip_dot, self.loop)
        right_arrow = Arrow(self.loop, surface_dot)
        diag_arrow = Arrow(strip_dot, surface_dot)

        randy = self.randy = Randolph(mode = "pondering")
        randy.next_to(ORIGIN, DOWN+LEFT)

        self.look_at(strip_dot)
        self.play(
            ShowCreation(top_arrow),
            randy.look_at, self.loop
        )
        self.wait()
        self.look_at(strip_dot, surface_dot)
        self.play(ShowCreation(diag_arrow))
        self.play(Blink(randy))
        self.look_at(strip_dot, self.loop)
        self.wait()
        self.play(
            ShowCreation(right_arrow),
            randy.look_at, surface_dot
        )
        self.play(Blink(randy))
        self.play(randy.change_mode, "happy")
        self.play(Blink(randy))
        self.wait()


    def look_at(self, *things):
        for thing in things:
            self.play(self.randy.look_at, thing)

class MapMobiusStripOntoSurface(Scene):
    def construct(self):
        pass

class StripMustIntersectItself(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            """
            The strip must 
            intersect itself
            during this process
            """,
            width = 4
        )
        dot = Dot(2*UP + 4*LEFT)
        for student in self.get_students():
            student.generate_target()
            student.target.change_mode("pondering")
            student.target.look_at(dot)
        self.play(*list(map(MoveToTarget, self.get_students())))
        self.random_blink(4)

class PairOfMobiusPointsLandOnEachother(Scene):
    def construct(self):
        pass

class ThatsTheProof(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            """
            Bada boom
            bada bang!
            """,
            target_mode = "hooray",
            width = 4
        )
        self.change_student_modes(*["hooray"]*3)
        self.random_blink()
        self.change_student_modes(
            "confused", "sassy", "erm"
        )
        self.teacher_says(
            """
            If you trust
            the mobius strip 
            fact...
            """,
            target_mode = "guilty",            
            width = 4,
        )
        self.random_blink()

class TryItYourself(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            It's actually an
            edifying exercise.
        """)
        self.random_blink()
        self.change_student_modes(*["pondering"]*3)
        self.random_blink(2)

        pi = self.get_students()[1]
        bubble = pi.get_bubble(
            "thought", 
            width = 4, height = 4,
            direction = RIGHT
        )
        bubble.set_fill(BLACK, opacity = 1)
        bubble.write("Orientation seem\\\\ to matter...")
        self.play(
            FadeIn(bubble),
            Write(bubble.content)
        )
        self.random_blink(3)

class OneMoreAnimation(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("""
            One more animation,
            but first...
        """)
        self.change_student_modes(*["happy"]*3)
        self.random_blink()

class PatreonThanks(Scene):
    CONFIG = {
        "specific_patrons" : [
            "Loo Yu Jun",
            "Tom",
            "Othman Alikhan",
            "Juan Batiz-Benet",
            "Markus Persson",
            "Joseph John Cox",
            "Achille Brighton",
            "Kirk Werklund",
            "Luc Ritchie",
            "Ripta Pasay",
            "PatrickJMT  ",
            "Felipe Diniz",
        ]
    }
    def construct(self):
        morty = Mortimer()
        morty.next_to(ORIGIN, DOWN)

        n_patrons = len(self.specific_patrons)
        special_thanks = TextMobject("Special thanks to:")
        special_thanks.set_color(YELLOW)
        special_thanks.shift(2*UP)

        left_patrons = VGroup(*list(map(TextMobject, 
            self.specific_patrons[:n_patrons/2]
        )))
        right_patrons = VGroup(*list(map(TextMobject, 
            self.specific_patrons[n_patrons/2:]
        )))
        for patrons, vect in (left_patrons, LEFT), (right_patrons, RIGHT):
            patrons.arrange(DOWN, aligned_edge = LEFT)
            patrons.next_to(special_thanks, DOWN)
            patrons.to_edge(vect, buff = LARGE_BUFF)

        self.play(morty.change_mode, "gracious")
        self.play(Write(special_thanks, run_time = 1))
        self.play(
            Write(left_patrons),
            morty.look_at, left_patrons
        )
        self.play(
            Write(right_patrons),
            morty.look_at, right_patrons
        )
        self.play(Blink(morty))
        for patrons in left_patrons, right_patrons:
            for index in 0, -1:
                self.play(morty.look_at, patrons[index])
                self.wait()

class CreditTWo(Scene):
    def construct(self):
        morty = Mortimer()
        morty.next_to(ORIGIN, DOWN)
        morty.to_edge(RIGHT)

        brother = PiCreature(color = GOLD_E)
        brother.next_to(morty, LEFT)
        brother.look_at(morty.eyes)
        
        headphones = Headphones(height = 1)
        headphones.move_to(morty.eyes, aligned_edge = DOWN)
        headphones.shift(0.1*DOWN)

        url = TextMobject("www.audible.com/3b1b")
        url.to_corner(UP+RIGHT, buff = LARGE_BUFF)

        self.add(morty)
        self.play(Blink(morty))
        self.play(
            FadeIn(headphones), 
            Write(url),
            Animation(morty)
        )
        self.play(morty.change_mode, "happy")
        self.wait()
        self.play(Blink(morty))
        self.wait()
        self.play(
            FadeIn(brother),
            morty.look_at, brother.eyes
        )
        self.play(brother.change_mode, "surprised")
        self.play(Blink(brother))
        self.wait()
        self.play(
            morty.look, LEFT,
            brother.change_mode, "happy",
            brother.look, LEFT
        )
        self.play(Blink(morty))
        self.wait()

class CreditThree(Scene):
    def construct(self):
        logo_dot = Dot().to_edge(UP).shift(3*RIGHT)
        randy = Randolph()
        randy.next_to(ORIGIN, DOWN)
        randy.to_edge(LEFT)
        randy.look(RIGHT)
        self.add(randy)
        bubble = randy.get_bubble(width = 2, height = 2)

        domains = VGroup(*list(map(TextMobject, [
            "visualnumbertheory.com",
            "buymywidgets.com",
            "learnwhatilearn.com",
        ])))
        domains.arrange(DOWN, aligned_edge = LEFT)
        domains.next_to(randy, UP, buff = LARGE_BUFF)
        domains.shift_onto_screen()

        promo_code = TextMobject("Promo code: TOPOLOGY")
        promo_code.shift(3*RIGHT)
        self.add(promo_code)
        whois = TextMobject("Free WHOIS privacy")
        whois.next_to(promo_code, DOWN, buff = LARGE_BUFF)

        self.play(Blink(randy))
        self.play(
            randy.change_mode, "happy",
            randy.look_at, logo_dot
        )
        self.wait()
        self.play(
            ShowCreation(bubble),
            randy.change_mode, "pondering",
            run_time = 2
        )
        self.play(Blink(randy))
        self.play(
            Transform(bubble, VectorizedPoint(randy.get_corner(UP+LEFT))),
            randy.change_mode, "sad"
        )
        self.wait()
        self.play(
            Write(domains, run_time = 5),
            randy.look_at, domains
        )
        self.wait()
        self.play(Blink(randy))
        self.play(
            randy.change_mode, "hooray",
            randy.look_at, logo_dot,
            FadeOut(domains)
        )
        self.wait()
        self.play(
            Write(whois),
            randy.change_mode, "confused",
            randy.look_at, whois
        )
        self.wait(2)
        self.play(randy.change_mode, "sassy")
        self.wait(2)
        self.play(
            randy.change_mode, "happy",
            randy.look_at, logo_dot
        )
        self.play(Blink(randy))
        self.wait()


class ShiftingLoopPairSurface(Scene):
    def construct(self):
        pass

class ThumbnailImage(ClosedLoopScene):
    def construct(self):
        self.add_rect_dots(square = True)
        for dot in self.dots:
            dot.scale_in_place(1.5)
        self.add_connecting_lines(cyclic = True)
        self.connecting_lines.set_stroke(width = 10)
        self.loop.add(self.connecting_lines, self.dots)

        title = TextMobject("Unsolved")
        title.scale(2.5)
        title.to_edge(UP)
        title.set_color_by_gradient(YELLOW, MAROON_B)
        self.add(title)
        self.loop.next_to(title, DOWN, buff = MED_SMALL_BUFF)
        self.loop.shift(2*LEFT)









