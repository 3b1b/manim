from manimlib.imports import *
from once_useful_constructs import *

EXAMPLE_TRANFORM = [[0, 1], [-1, 1]]
TRANFORMED_VECTOR = [[1], [2]]

def matrix_multiplication():
    return TexMobject("""
        \\left[
            \\begin{array}{cc}
                a & b \\\\
                c & d
            \\end{array}
        \\right]
        \\left[
            \\begin{array}{cc}
                e & f \\\\
                g & h
            \\end{array}
        \\right]
        = 
        \\left[
            \\begin{array}{cc}
                ae + bg & af + bh \\\\
                ce + dg & cf + dh
            \\end{array}
        \\right]
    """)

class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject(
            """
            ``There is hardly any theory which is more elementary 
            than linear algebra, in spite of the fact that generations 
            of professors and textbook writers have obscured its 
            simplicity by preposterous calculations with matrices.''
            """, 
            organize_left_to_right = False
        )
        words.set_width(2*(FRAME_X_RADIUS-1))
        words.to_edge(UP)        
        for mob in words.submobjects[48:49+13]:
            mob.set_color(GREEN)
        author = TextMobject("-Jean Dieudonn\\'e")
        author.set_color(YELLOW)
        author.next_to(words, DOWN)

        self.play(FadeIn(words))
        self.wait(3)
        self.play(Write(author, run_time = 5))
        self.wait()

class VideoIcon(SVGMobject):
    def __init__(self, **kwargs):
        SVGMobject.__init__(self, "video_icon", **kwargs)
        self.center()
        self.set_width(FRAME_WIDTH/12.)
        self.set_stroke(color = WHITE, width = 0)
        self.set_fill(color = WHITE, opacity = 1)



class UpcomingSeriesOfVidoes(Scene):
    def construct(self):
        icons = [VideoIcon() for x in range(10)]
        colors = Color(BLUE_A).range_to(BLUE_D, len(icons))
        for icon, color in zip(icons, colors):
            icon.set_fill(color, opacity = 1)
        icons = VMobject(*icons)
        icons.arrange(RIGHT)
        icons.to_edge(LEFT)
        icons.shift(UP)
        icons = icons.split()

        def rate_func_creator(offset):
            return lambda a : min(max(2*(a-offset), 0), 1)
        self.play(*[
            FadeIn(
                icon, 
                run_time = 5,
                rate_func = rate_func_creator(offset)
            )
            for icon, offset in zip(icons, np.linspace(0, 0.5, len(icons)))
        ])
        self.wait()


class AboutLinearAlgebra(Scene):
    def construct(self):
        self.show_dependencies()
        self.to_thought_bubble()

    def show_dependencies(self):
        linalg = TextMobject("Linear Algebra")
        subjects = list(map(TextMobject, [
            "Computer science",
            "Physics",
            "Electrical engineering",
            "Mechanical engineering",
            "Statistics",
            "\\vdots"
        ]))
        prev = subjects[0]
        for subject in subjects[1:]:
            subject.next_to(prev, DOWN, aligned_edge = LEFT)
            prev = subject
        all_subs = VMobject(*subjects)
        linalg.to_edge(LEFT)
        all_subs.next_to(linalg, RIGHT, buff = 2)
        arrows = VMobject(*[
            Arrow(linalg, sub)
            for sub in subjects
        ])

        self.play(Write(linalg, run_time = 1))
        self.wait()
        self.play(
            ShowCreation(arrows, lag_ratio = 0.5),
            FadeIn(all_subs),
            run_time = 2
        )
        self.wait()
        self.linalg = linalg

    def to_thought_bubble(self):
        linalg = self.linalg
        all_else = list(self.mobjects)
        all_else.remove(linalg)
        randy = Randolph()
        randy.to_corner()
        bubble = randy.get_bubble(width = 10)
        new_linalg = bubble.position_mobject_inside(linalg.copy())
        q_marks = TextMobject("???").next_to(randy, UP)

        self.play(*list(map(FadeOut, all_else)))
        self.remove(*all_else)
        self.play(
            Transform(linalg, new_linalg),
            Write(bubble),
            FadeIn(randy)
        )
        self.wait()

        topics = [
            self.get_matrix_multiplication(),
            self.get_determinant(),
            self.get_cross_product(),
            self.get_eigenvalue(),
        ]
        questions = [
            self.get_matrix_multiplication_question(),
            self.get_cross_product_question(),
            self.get_eigen_question(),
        ]
        for count, topic in enumerate(topics + questions):
            bubble.position_mobject_inside(topic)            
            if count == len(topics):
                self.play(FadeOut(linalg))
                self.play(
                    ApplyMethod(randy.change_mode, "confused"),
                    Write(q_marks, run_time = 1)
                )
                linalg = VectorizedPoint(linalg.get_center())
            if count > len(topics):
                self.remove(linalg)
                self.play(FadeIn(topic))
                linalg = topic
            else:
                self.play(Transform(linalg, topic))

            if count %3 == 0:
                self.play(Blink(randy))
                self.wait()
            else:
                self.wait(2)


    def get_matrix_multiplication(self):
        return matrix_multiplication()

    def get_determinant(self):
        return TexMobject("""
            \\text{Det}\\left(
                \\begin{array}{cc}
                    a & b \\\\
                    c & d
                \\end{array}
            \\right)
            = 
            ad - bc
        """)

    def get_cross_product(self):
        return TexMobject("""
            \\vec{\\textbf{v}} \\times \\textbf{w} =
            \\text{Det}\\left(
                \\begin{array}{ccc}
                    \\hat{\imath} & \\hat{\jmath} & \\hat{k} \\\\
                    v_1 & v_2 & v_3 \\\\
                    w_1 & w_2 & w_3 \\\\
                \\end{array}
            \\right)
        """)

    def get_eigenvalue(self):
        result = TexMobject("\\text{Det}\\left(A - \\lambda I \\right) = 0")
        result.submobjects[0][-5].set_color(YELLOW)
        return result

    def get_matrix_multiplication_question(self):
        why = TextMobject("Why?").set_color(BLUE) 
        mult = self.get_matrix_multiplication()
        why.next_to(mult, UP)
        result = VMobject(why, mult)
        result.get_center = lambda : mult.get_center()
        return result

    def get_cross_product_question(self):
        cross = TexMobject("\\vec{v} \\times \\vec{w}")
        left_right_arrow = DoubleArrow(Point(LEFT), Point(RIGHT))
        det = TextMobject("Det")
        q_mark = TextMobject("?")
        left_right_arrow.next_to(cross)
        det.next_to(left_right_arrow)
        q_mark.next_to(left_right_arrow, UP)
        cross_question = VMobject(cross, left_right_arrow, q_mark, det)
        cross_question.get_center = lambda : left_right_arrow.get_center()
        return cross_question

    def get_eigen_question(self):
        result = TextMobject(
            "What the heck \\\\ does ``eigen'' mean?",

        )
        for mob in result.submobjects[-11:-6]:
            mob.set_color(YELLOW)
        return result


class NumericVsGeometric(Scene):
    def construct(self):
        self.setup()
        self.specifics_concepts()
        self.clear_way_for_geometric()
        self.list_geometric_benefits()

    def setup(self):
        numeric = TextMobject("Numeric operations")
        geometric = TextMobject("Geometric intuition")
        for mob in numeric, geometric:
            mob.to_corner(UP+LEFT)
        geometric.shift(FRAME_X_RADIUS*RIGHT)
        hline = Line(FRAME_X_RADIUS*LEFT, FRAME_X_RADIUS*RIGHT)
        hline.next_to(numeric, DOWN)
        hline.to_edge(LEFT, buff = 0)
        vline = Line(FRAME_Y_RADIUS*UP, FRAME_Y_RADIUS*DOWN)
        for mob in hline, vline:
            mob.set_color(GREEN)

        self.play(ShowCreation(VMobject(hline, vline)))
        digest_locals(self)

    def specifics_concepts(self):
        matrix_vector_product = TexMobject(" ".join([
            matrix_to_tex_string(EXAMPLE_TRANFORM),
            matrix_to_tex_string(TRANFORMED_VECTOR),
            "&=",
            matrix_to_tex_string([
                ["1 \\cdot 1 + 0 \\cdot 2"], 
                ["1 \\cdot 1 + (-1)\\cdot 2"]
            ]),
            "\\\\ &=",
            matrix_to_tex_string([[1], [-1]]),
        ]))
        matrix_vector_product.set_width(FRAME_X_RADIUS-0.5)
        matrix_vector_product.next_to(self.vline, LEFT)

        self.play(
            Write(self.numeric),
            FadeIn(matrix_vector_product),
            run_time = 2
        )
        self.wait()
        self.play(Write(self.geometric, run_time = 2))
        ### Paste in linear transformation
        self.wait()
        digest_locals(self)

    def clear_way_for_geometric(self):
        new_line = Line(FRAME_Y_RADIUS*LEFT, FRAME_Y_RADIUS*RIGHT)
        new_line.shift((FRAME_Y_RADIUS+1)*DOWN)
        self.play(
            Transform(self.vline, new_line),
            Transform(self.hline, new_line),
            ApplyMethod(self.numeric.shift, (FRAME_HEIGHT+1)*DOWN),
            ApplyMethod(
                self.matrix_vector_product.shift, 
                (FRAME_HEIGHT+1)*DOWN
            ),
            ApplyMethod(self.geometric.to_edge, LEFT)
        )

    def list_geometric_benefits(self):
        follow_words = TextMobject("is helpful for \\dots")
        follow_words.next_to(self.geometric)
        #Ugly hack
        diff = follow_words.submobjects[0].get_bottom()[1] - \
             self.geometric.submobjects[0].get_bottom()[1]
        follow_words.shift(diff*DOWN)
        randys = [
            Randolph(mode = "speaking"),
            Randolph(mode = "surprised"),
            Randolph(mode = "pondering")
        ]
        bulb = SVGMobject("light_bulb")
        bulb.set_height(1)
        bulb.set_color(YELLOW)
        thoughts = [
            matrix_to_mobject(EXAMPLE_TRANFORM),
            bulb,
            TextMobject("So therefore...").scale(0.5)
        ]

        self.play(Write(follow_words, run_time = 1.5))
        curr_randy = None
        for randy, thought in zip(randys, thoughts):
            randy.shift(DOWN)
            thought.next_to(randy, UP+RIGHT, buff = 0)
            if curr_randy:
                self.play(
                    Transform(curr_randy, randy),
                    Transform(curr_thought, thought)
                )
            else:
                self.play(
                    FadeIn(randy),
                    Write(thought, run_time = 1)
                )
                curr_randy = randy
                curr_thought = thought
            self.wait(1.5)


class ExampleTransformation(LinearTransformationScene):
    def construct(self):
        self.setup()
        self.add_vector(np.array(TRANFORMED_VECTOR).flatten())
        self.apply_matrix(EXAMPLE_TRANFORM)
        self.wait()


class NumericToComputations(Scene):
    def construct(self):
        top = TextMobject("Numeric understanding")
        arrow = Arrow(UP, DOWN)
        bottom = TextMobject("Actual computations")
        top.next_to(arrow, UP)
        bottom.next_to(arrow, DOWN)

        self.add(top)
        self.play(ShowCreation(arrow))
        self.play(FadeIn(bottom))
        self.wait()



class LinAlgPyramid(Scene):
    def construct(self):
        rects = self.get_rects()
        words = self.place_words_in_rects([
            "Geometric understanding",
            "Computations",
            "Uses"
        ], rects)
        for word, rect in zip(words, rects):
            self.play(
                Write(word),
                ShowCreation(rect),
                run_time = 1
            )
        self.wait()
        self.play(*[
            ApplyMethod(m.set_color, DARK_GREY)
            for m in (words[0], rects[0])
        ])
        self.wait()
        self.list_applications(rects[-1])

    def get_rects(self):
        height = 1
        rects = [
            Rectangle(height = height, width = width)
            for width in (8, 5, 2)
        ]
        rects[0].shift(2*DOWN)
        for i in 1, 2:
            rects[i].next_to(rects[i-1], UP, buff = 0)
        return rects

    def place_words_in_rects(self, words, rects):
        result = []
        for word, rect in zip(words, rects):
            tex_mob = TextMobject(word)
            tex_mob.shift(rect.get_center())
            result.append(tex_mob)
        return result

    def list_applications(self, top_mob):
        subjects = [
            TextMobject(word).to_corner(UP+RIGHT)
            for word in [
                "computer science", 
                "engineering", 
                "statistics", 
                "economics", 
                "pure math",
            ]
        ]
        arrow = Arrow(top_mob, subjects[0].get_bottom(), color = RED)

        self.play(ShowCreation(arrow))
        curr_subject = None
        for subject in subjects:
            if curr_subject:
                subject.shift(curr_subject.get_center()-subject.get_center())
                self.play(Transform(curr_subject, subject, run_time = 0.5))
            else:
                curr_subject = subject
                self.play(FadeIn(curr_subject, run_time = 0.5))
            self.wait()


class IntimidatingProf(Scene):
    def construct(self):
        randy = Randolph().to_corner()
        morty = Mortimer().to_corner(DOWN+RIGHT)
        morty.shift(3*LEFT)
        morty_name1 = TextMobject("Professor")
        morty_name2 = TextMobject("Coworker")
        for name in morty_name1, morty_name2:
            name.to_edge(RIGHT)
            name.shift(2*UP)
        arrow = Arrow(morty_name1.get_bottom(), morty)
        speech_bubble = SpeechBubble(height = 3).flip()
        speech_bubble.pin_to(morty)
        speech_bubble.shift(RIGHT)
        speech_bubble.write("And of course $B^{-1}AB$ will \\\\ also have positive eigenvalues...")
        thought_bubble = ThoughtBubble(width = 6, height = 5)
        thought_bubble.next_to(morty, UP)
        thought_bubble.to_edge(RIGHT, buff = -1)
        thought_bubble.make_green_screen()
        q_marks = TextMobject("???")
        q_marks.next_to(randy, UP)
        randy_bubble = randy.get_bubble()
        randy_bubble.add_content(matrix_multiplication())

        self.add(randy, morty)
        self.play(
            FadeIn(morty_name1),
            ShowCreation(arrow)
        )
        self.play(Transform(morty_name1, morty_name2))
        self.wait()
        self.play(FadeOut(morty_name1), FadeOut(arrow))
        self.play(
            FadeIn(speech_bubble),
            ApplyMethod(morty.change_mode, "speaking")
        )
        self.play(FadeIn(thought_bubble))
        self.wait()
        self.play(
            ApplyMethod(randy.change_mode, "confused"),
            Write(q_marks, run_time = 1)
        )
        self.play(FadeOut(VMobject(speech_bubble, thought_bubble)))
        self.play(FadeIn(randy_bubble))
        self.wait()


class ThoughtBubbleTransformation(LinearTransformationScene):
    def construct(self):
        self.setup()
        rotation = rotation_about_z(np.pi/3)
        self.apply_matrix(
            np.linalg.inv(rotation), 
            path_arc = -np.pi/3,
        )
        self.apply_matrix(EXAMPLE_TRANFORM)
        self.apply_matrix(
            rotation, 
            path_arc = np.pi/3,
        )
        self.wait()


class SineApproximations(Scene):
    def construct(self):
        series = self.get_series()
        one_approx = self.get_approx_series("1", 1)
        one_approx.set_color(YELLOW)
        pi_sixts_approx = self.get_approx_series("\\pi/6", np.pi/6)
        pi_sixts_approx.set_color(RED)
        words = TextMobject("(How calculators compute sine)")
        words.set_color(GREEN)

        series.to_edge(UP)
        one_approx.next_to(series, DOWN, buff = 1.5)
        pi_sixts_approx.next_to(one_approx, DOWN, buff = 1.5)

        self.play(Write(series))
        self.wait()
        self.play(FadeIn(words))
        self.wait(2)
        self.play(FadeOut(words))
        self.remove(words)
        self.wait()
        self.play(Write(one_approx))
        self.play(Write(pi_sixts_approx))
        self.wait()

    def get_series(self):
        return TexMobject("""
            \\sin(x) = x - \\dfrac{x^3}{3!} + \\dfrac{x^5}{5!}
            + \\cdots + (-1)^n \\dfrac{x^{2n+1}}{(2n+1)!} + \\cdots
        """)

    def get_approx_series(self, val_str, val):
        #Default to 3 terms
        approximation = val - (val**3)/6. + (val**5)/120.
        return TexMobject("""
            \\sin(%s) \\approx 
            %s - \\dfrac{(%s)^3}{3!} + \\dfrac{(%s)^5}{5!} \\approx
            %.04f
        """%(val_str, val_str, val_str, val_str, approximation))


class LooseConnectionToTriangles(Scene):
    def construct(self):
        sine = TexMobject("\\sin(x)")
        triangle = Polygon(ORIGIN, 2*RIGHT, 2*RIGHT+UP)
        arrow = DoubleArrow(LEFT, RIGHT)        
        sine.next_to(arrow, LEFT)
        triangle.next_to(arrow, RIGHT)

        q_mark = TextMobject("?").scale(1.5)
        q_mark.next_to(arrow, UP)

        self.add(sine)
        self.play(ShowCreation(arrow))
        self.play(ShowCreation(triangle))
        self.play(Write(q_mark))
        self.wait()


class PhysicsExample(Scene):
    def construct(self):
        title = TextMobject("Physics")
        title.to_corner(UP+LEFT)
        parabola = FunctionGraph(
            lambda x : (3-x)*(3+x)/4,
            x_min = -4, 
            x_max = 4
        )

        self.play(Write(title))
        self.projectile(parabola)
        self.velocity_vector(parabola)
        self.approximate_sine()

    def projectile(self, parabola):
        dot = Dot(radius = 0.15)
        kwargs = {
            "run_time" : 3,
            "rate_func" : None
        }
        self.play(
            MoveAlongPath(dot, parabola.copy(), **kwargs),
            ShowCreation(parabola, **kwargs)
        )
        self.wait()


    def velocity_vector(self, parabola):
        alpha = 0.7
        d_alpha = 0.01
        vector_length = 3

        p1 = parabola.point_from_proportion(alpha)
        p2 = parabola.point_from_proportion(alpha + d_alpha)
        vector = vector_length*(p2-p1)/get_norm(p2-p1)
        v_mob = Vector(vector, color = YELLOW)
        vx = Vector(vector[0]*RIGHT, color = GREEN_B)
        vy = Vector(vector[1]*UP, color = RED)
        v_mob.shift(p1)
        vx.shift(p1)
        vy.shift(vx.get_end())

        arc = Arc(
            angle_of_vector(vector), 
            radius = vector_length / 4.
        )
        arc.shift(p1)
        theta = TexMobject("\\theta").scale(0.75)
        theta.next_to(arc, RIGHT, buff = 0.1)

        v_label = TexMobject("\\vec{v}")
        v_label.shift(p1 + RIGHT*vector[0]/4 + UP*vector[1]/2)
        v_label.set_color(v_mob.get_color())
        vx_label = TexMobject("||\\vec{v}|| \\cos(\\theta)")
        vx_label.next_to(vx, UP)
        vx_label.set_color(vx.get_color())
        vy_label = TexMobject("||\\vec{v}|| \\sin(\\theta)")
        vy_label.next_to(vy, RIGHT)
        vy_label.set_color(vy.get_color())

        for v in v_mob, vx, vy:
            self.play(
                ShowCreation(v)
            )
        self.play(
            ShowCreation(arc),
            Write(theta, run_time = 1)
        )
        for label in v_label, vx_label, vy_label:
            self.play(Write(label, run_time = 1))
        self.wait()

    def approximate_sine(self):
        approx = TexMobject("\\sin(\\theta) \\approx 0.7\\text{-ish}")
        morty = Mortimer(mode = "speaking")
        morty.flip()
        morty.to_corner()
        bubble = SpeechBubble(width = 4, height = 3)
        bubble.set_fill(BLACK, opacity = 1)
        bubble.pin_to(morty)
        bubble.position_mobject_inside(approx)

        self.play(
            FadeIn(morty),
            ShowCreation(bubble),
            Write(approx),
            run_time = 2
        )
        self.wait()


class LinearAlgebraIntuitions(Scene):
    def construct(self):
        title = TextMobject("Preview of core visual intuitions")
        title.to_edge(UP)
        h_line = Line(FRAME_X_RADIUS*LEFT, FRAME_X_RADIUS*RIGHT)
        h_line.next_to(title, DOWN)
        h_line.set_color(BLUE_E)
        intuitions = [
            "Matrices transform space",
            "Matrix multiplication corresponds to applying " + 
            "one transformation after another",
            "The determinant gives the factor by which areas change",
        ]

        self.play(
            Write(title),
            ShowCreation(h_line),
            run_time = 2
        )

        for count, intuition in enumerate(intuitions, 3):
            intuition += " (details coming in chapter %d)"%count
            mob = TextMobject(intuition)
            mob.scale(0.7)
            mob.next_to(h_line, DOWN)
            self.play(FadeIn(mob))
            self.wait(4)
            self.play(FadeOut(mob))
            self.remove(mob)
        self.wait()

class MatricesAre(Scene):
    def construct(self):
        matrix = matrix_to_mobject([[1, -1], [1, 2]])
        matrix.set_height(6)
        arrow = Arrow(LEFT, RIGHT, stroke_width = 8, preserve_tip_size_when_scaling = False)
        arrow.scale(2)
        arrow.to_edge(RIGHT)
        matrix.next_to(arrow, LEFT)

        self.play(Write(matrix, run_time = 1))
        self.play(ShowCreation(arrow))
        self.wait()

class ExampleTransformationForIntuitionList(LinearTransformationScene):
    def construct(self):
        self.setup()
        self.apply_matrix([[1, -1], [1, 2]])
        self.wait()

class MatrixMultiplicationIs(Scene):
    def construct(self):
        matrix1 = matrix_to_mobject([[1, -1], [1, 2]])
        matrix1.set_color(BLUE)
        matrix2 = matrix_to_mobject([[2, 1], [1, 2]])
        matrix2.set_color(GREEN)
        for m in matrix1, matrix2:
            m.set_height(3)
        arrow = Arrow(LEFT, RIGHT, stroke_width = 6, preserve_tip_size_when_scaling = False)
        arrow.scale(2)
        arrow.to_edge(RIGHT)
        matrix1.next_to(arrow, LEFT)
        matrix2.next_to(matrix1, LEFT)
        brace1 = Brace(matrix1, UP)
        apply_first = TextMobject("Apply first").next_to(brace1, UP)
        brace2 = Brace(matrix2, DOWN)
        apply_second = TextMobject("Apply second").next_to(brace2, DOWN)

        self.play(
            Write(matrix1), 
            ShowCreation(arrow),
            GrowFromCenter(brace1),
            Write(apply_first),
            run_time = 1
        )
        self.wait()
        self.play(
            Write(matrix2),
            GrowFromCenter(brace2),
            Write(apply_second),
            run_time = 1
        )
        self.wait()

class ComposedTransformsForIntuitionList(LinearTransformationScene):
    def construct(self):
        self.setup()
        self.apply_matrix([[1, -1], [1, 2]])
        self.wait()
        self.apply_matrix([[2, 1], [1, 2]])
        self.wait()

class DeterminantsAre(Scene):
    def construct(self):
        tex_mob = TexMobject("""
            \\text{Det}\\left(\\left[
                \\begin{array}{cc}
                    1 & -1 \\\\
                    1 & 2
                \\end{array}
            \\right]\\right)
        """)
        tex_mob.set_height(4)
        arrow = Arrow(LEFT, RIGHT, stroke_width = 8, preserve_tip_size_when_scaling = False)
        arrow.scale(2)
        arrow.to_edge(RIGHT)
        tex_mob.next_to(arrow, LEFT)

        self.play(
            Write(tex_mob),
            ShowCreation(arrow),
            run_time = 1
        )

class TransformationForDeterminant(LinearTransformationScene):
    def construct(self):
        self.setup()
        square = Square(side_length = 1)
        square.shift(-square.get_corner(DOWN+LEFT))
        square.set_fill(YELLOW_A, 0.5)
        self.add_transformable_mobject(square)
        self.apply_matrix([[1, -1], [1, 2]])

class ProfessorsTry(Scene):
    def construct(self):
        morty = Mortimer()
        morty.to_corner(DOWN+RIGHT)
        morty.shift(3*LEFT)
        speech_bubble = morty.get_bubble(SpeechBubble, height = 4, width = 8)
        speech_bubble.shift(RIGHT)
        words = TextMobject(
            "It really is beautiful!  I want you to \\\\" + \
            "see it the way I do...",
        )
        speech_bubble.position_mobject_inside(words)
        thought_bubble = ThoughtBubble(width = 4, height = 3.5)
        thought_bubble.next_to(morty, UP)
        thought_bubble.to_edge(RIGHT)
        thought_bubble.make_green_screen()
        randy = Randolph()
        randy.scale(0.8)
        randy.to_corner()

        self.add(randy, morty)
        self.play(
            ApplyMethod(morty.change_mode, "speaking"),
            FadeIn(speech_bubble),
            FadeIn(words)
        )
        self.play(Blink(randy))
        self.play(FadeIn(thought_bubble))
        self.play(Blink(morty))


class ExampleMatrixMultiplication(NumericalMatrixMultiplication):
    CONFIG = {
        "left_matrix" : [[-3, 1], [2, 5]],
        "right_matrix" : [[5, 3], [7, -3]]
    }

class TableOfContents(Scene):
    def construct(self):
        title = TextMobject("Essence of Linear Algebra")
        title.set_color(BLUE)
        title.to_corner(UP+LEFT)
        h_line = Line(FRAME_X_RADIUS*LEFT, FRAME_X_RADIUS*RIGHT)
        h_line.next_to(title, DOWN)
        h_line.to_edge(LEFT, buff = 0)
        chapters = VMobject(*list(map(TextMobject, [
            "Chapter 1: Vectors, what even are they?",
            "Chapter 2: Linear combinations, span and bases",
            "Chapter 3: Matrices as linear transformations",
            "Chapter 4: Matrix multiplication as composition",
            "Chapter 5: The determinant",
            "Chapter 6: Inverse matrices, column space and null space",
            "Chapter 7: Dot products and cross products",
            "Chapter 8: Change of basis",
            "Chapter 9: Eigenvectors and eigenvalues",
            "Chapter 10: Abstract vector spaces",
        ])))
        chapters.arrange(DOWN)
        chapters.scale(0.7)
        chapters.next_to(h_line, DOWN)

        self.play(
            Write(title),
            ShowCreation(h_line)
        )
        for chapter in chapters.split():
            chapter.to_edge(LEFT, buff = 1)
            self.play(FadeIn(chapter))
        self.wait(2)

        entry3 = chapters.split()[2]
        added_words = TextMobject("(Personally, I'm most excited \\\\ to do this one)")
        added_words.scale(0.5)
        added_words.set_color(YELLOW)
        added_words.next_to(h_line, DOWN)
        added_words.to_edge(RIGHT)
        arrow = Arrow(added_words.get_bottom(), entry3)

        self.play(
            ApplyMethod(entry3.set_color, YELLOW),
            ShowCreation(arrow),
            Write(added_words),
            run_time = 1
        )
        self.wait()
        removeable = VMobject(added_words, arrow, h_line, title)
        self.play(FadeOut(removeable))
        self.remove(removeable)

        self.series_of_videos(chapters)

    def series_of_videos(self, chapters):
        icon = SVGMobject("video_icon")
        icon.center()
        icon.set_width(FRAME_WIDTH/12.)
        icon.set_stroke(color = WHITE, width = 0)
        icons = [icon.copy() for chapter in chapters.split()]
        colors = Color(BLUE_A).range_to(BLUE_D, len(icons))
        for icon, color in zip(icons, colors):
            icon.set_fill(color, opacity = 1)
        icons = VMobject(*icons)
        icons.arrange(RIGHT)
        icons.to_edge(LEFT)
        icons.shift(UP)

        randy = Randolph()
        randy.to_corner()
        bubble = randy.get_bubble()
        new_icons = icons.copy().scale(0.2)
        bubble.position_mobject_inside(new_icons)

        self.play(Transform(
            chapters, icons,
            path_arc = np.pi/2,
        ))
        self.clear()
        self.add(icons)
        self.play(FadeIn(randy))
        self.play(Blink(randy))
        self.wait()
        self.play(
            ShowCreation(bubble),
            Transform(icons, new_icons)
        )
        self.remove(icons)
        bubble.make_green_screen()
        self.wait()


class ResourceForTeachers(Scene):
    def construct(self):
        morty = Mortimer(mode = "speaking")
        morty.to_corner(DOWN + RIGHT)
        bubble = morty.get_bubble(SpeechBubble)
        bubble.write("I'm assuming you \\\\ know linear algebra\\dots")
        words = bubble.content
        bubble.clear()
        randys = VMobject(*[
            Randolph(color = c)
            for c in (BLUE_D, BLUE_C, BLUE_E)
        ])
        randys.arrange(RIGHT)
        randys.scale(0.8)
        randys.to_corner(DOWN+LEFT)

        self.add(randys, morty)
        self.play(FadeIn(bubble), Write(words), run_time = 3)
        for randy in np.array(randys.split())[[2,0,1]]:
            self.play(Blink(randy))
        self.wait()

class AboutPacing(Scene):
    def construct(self):
        words = TextMobject("About pacing...")
        dots = words.split()[-3:]
        words.remove(*dots)
        self.play(FadeIn(words))
        self.play(Write(VMobject(*dots)))
        self.wait()

class DifferingBackgrounds(Scene):
    def construct(self):
        words = list(map(TextMobject, [
            "Just brushing up",
            "Has yet to take the course",
            "Supplementing course concurrently",
        ]))
        students = VMobject(*[
            Randolph(color = c)
            for c in (BLUE_D, BLUE_C, BLUE_E)
        ])
        modes = ["pondering", "speaking_looking_left", "sassy"]
        students.arrange(RIGHT)
        students.scale(0.8)
        students.center().to_edge(DOWN)

        last_word, last_arrow = None, None
        for word, student, mode in zip(words, students.split(), modes):
            word.shift(2*UP)
            arrow = Arrow(word, student)
            if last_word:
                word_anim = Transform(last_word, word)
                arrow_anim = Transform(last_arrow, arrow)
            else:
                word_anim = Write(word, run_time = 1)
                arrow_anim = ShowCreation(arrow)
                last_word = word
                last_arrow = arrow
            self.play(
                word_anim, arrow_anim,
                ApplyMethod(student.change_mode, mode)
            )
            self.play(Blink(student))
            self.wait()
        self.wait()



class PauseAndPonder(Scene):
    def construct(self):
        pause = TexMobject("=").rotate(np.pi/2)
        pause.stretch(0.5, 1)
        pause.set_height(1.5)
        bubble = ThoughtBubble().set_height(2)
        pause.shift(LEFT)
        bubble.next_to(pause, RIGHT, buff = 1)

        self.play(FadeIn(pause))
        self.play(ShowCreation(bubble))
        self.wait()


class NextVideo(Scene):
    def construct(self):
        title = TextMobject("Next video: Vectors, what even are they?")
        title.to_edge(UP)
        rect = Rectangle(width = 16, height = 9, color = BLUE)
        rect.set_height(6)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.wait()








