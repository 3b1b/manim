from manimlib.imports import *
from old_projects.brachistochrone.curves import *

class RollAlongVector(Animation):
    CONFIG = {
        "rotation_vector" : OUT,
    }
    def __init__(self, mobject, vector, **kwargs):
        radius = mobject.get_width()/2
        radians = get_norm(vector)/radius
        last_alpha = 0
        digest_config(self, kwargs, locals())
        Animation.__init__(self, mobject, **kwargs)

    def interpolate_mobject(self, alpha):
        d_alpha = alpha - self.last_alpha
        self.last_alpha = alpha
        self.mobject.rotate_in_place(
            d_alpha*self.radians, 
            self.rotation_vector
        )
        self.mobject.shift(d_alpha*self.vector)


class CycloidScene(Scene):
    CONFIG = {
        "point_a"   : 6*LEFT+3*UP,
        "radius"    : 2,
        "end_theta" : 2*np.pi
    }
    def construct(self):
        self.generate_cycloid()
        self.generate_circle()
        self.generate_ceiling()

    def grow_parts(self):
        self.play(*[
            ShowCreation(mob)
            for mob in (self.circle, self.ceiling)
        ])

    def generate_cycloid(self):
        self.cycloid = Cycloid(
            point_a = self.point_a,
            radius = self.radius,
            end_theta = self.end_theta
        )

    def generate_circle(self, **kwargs):
        self.circle = Circle(radius = self.radius, **kwargs)
        self.circle.shift(self.point_a - self.circle.get_top())
        radial_line = Line(
            self.circle.get_center(), self.point_a
        )
        self.circle.add(radial_line)

    def generate_ceiling(self):
        self.ceiling = Line(FRAME_X_RADIUS*LEFT, FRAME_X_RADIUS*RIGHT)
        self.ceiling.shift(self.cycloid.get_top()[1]*UP)

    def draw_cycloid(self, run_time = 3, *anims, **kwargs):
        kwargs["run_time"] = run_time
        self.play(
            RollAlongVector(
                self.circle,
                self.cycloid.points[-1]-self.cycloid.points[0],
                **kwargs
            ),
            ShowCreation(self.cycloid, **kwargs),
            *anims
        )

    def roll_back(self, run_time = 3, *anims, **kwargs):
        kwargs["run_time"] = run_time
        self.play(
            RollAlongVector(
                self.circle,
                self.cycloid.points[0]-self.cycloid.points[- 1],
                rotation_vector = IN,
                **kwargs
            ),
            ShowCreation(
                self.cycloid, 
                rate_func = lambda t : smooth(1-t),
                **kwargs
            ),
            *anims
        )
        self.generate_cycloid()


class IntroduceCycloid(CycloidScene):
    def construct(self):
        CycloidScene.construct(self)

        equation = TexMobject([
            "\\dfrac{\\sin(\\theta)}{\\sqrt{y}}",
            "= \\text{constant}"
        ])
        sin_sqrt, const = equation.split()
        new_eq = equation.copy()
        new_eq.to_edge(UP, buff = 1.3)
        cycloid_word = TextMobject("Cycloid")
        arrow = Arrow(2*UP, cycloid_word)
        arrow.reverse_points()
        q_mark = TextMobject("?")

        self.play(*list(map(ShimmerIn, equation.split())))
        self.wait()
        self.play(
            ApplyMethod(equation.shift, 2.2*UP),
            ShowCreation(arrow)
        )
        q_mark.next_to(sin_sqrt)
        self.play(ShimmerIn(cycloid_word))
        self.wait()
        self.grow_parts()
        self.draw_cycloid()
        self.wait()
        extra_terms = [const, arrow, cycloid_word]
        self.play(*[
            Transform(mob, q_mark)
            for mob in extra_terms
        ])
        self.remove(*extra_terms)
        self.roll_back()
        q_marks, arrows = self.get_q_marks_and_arrows(sin_sqrt)
        self.draw_cycloid(3, 
            ShowCreation(q_marks),
            ShowCreation(arrows)
        )
        self.wait()

    def get_q_marks_and_arrows(self, mob, n_marks = 10):
        circle = Circle().replace(mob)
        q_marks, arrows = result = [Mobject(), Mobject()]
        for x in range(n_marks):
            index = (x+0.5)*self.cycloid.get_num_points()/n_marks
            q_point = self.cycloid.points[index]
            vect = q_point-mob.get_center()
            start_point = circle.get_boundary_point(vect)
            arrow = Arrow(
                start_point, q_point,
                color = BLUE_E
            )

            q_marks.add(TextMobject("?").shift(q_point))
            arrows.add(arrow)
        for mob in result:
            mob.ingest_submobjects()
        return result


class LeviSolution(CycloidScene):
    CONFIG = {
        "cycloid_fraction" : 0.25,
    }
    def construct(self):
        CycloidScene.construct(self)
        self.add(self.ceiling)
        self.generate_points()
        methods = [
            self.draw_cycloid,
            self.roll_into_position,
            self.draw_p_and_c,
            self.show_pendulum,
            self.show_diameter,
            self.show_theta,
            self.show_similar_triangles,
            self.show_sin_thetas,
            self.show_y,
            self.rearrange,
        ]
        for method in methods:
            method()
            self.wait()


    def generate_points(self):
        index = int(self.cycloid_fraction*self.cycloid.get_num_points())
        p_point = self.cycloid.points[index]
        p_dot = Dot(p_point)
        p_label = TexMobject("P")
        p_label.next_to(p_dot, DOWN+LEFT)
        c_point = self.point_a + self.cycloid_fraction*self.radius*2*np.pi*RIGHT
        c_dot = Dot(c_point)
        c_label = TexMobject("C")
        c_label.next_to(c_dot, UP)

        digest_locals(self)

    def roll_into_position(self):
        self.play(RollAlongVector(
            self.circle,
            (1-self.cycloid_fraction)*self.radius*2*np.pi*LEFT,
            rotation_vector = IN,
            run_time = 2
        ))

    def draw_p_and_c(self):
        radial_line = self.circle.submobjects[0] ##Hacky
        self.play(Transform(radial_line, self.p_dot))
        self.remove(radial_line)
        self.add(self.p_dot)
        self.play(ShimmerIn(self.p_label))
        self.wait()
        self.play(Transform(self.ceiling.copy(), self.c_dot))
        self.play(ShimmerIn(self.c_label))

    def show_pendulum(self, arc_angle = np.pi, arc_color = GREEN):
        words = TextMobject(": Instantaneous center of rotation")
        words.next_to(self.c_label)
        line = Line(self.p_point, self.c_point)
        line_angle = line.get_angle()+np.pi
        line_length = line.get_length()
        line.add(self.p_dot.copy())
        line.get_center = lambda : self.c_point
        tangent_line = Line(3*LEFT, 3*RIGHT)
        tangent_line.rotate(line_angle-np.pi/2)
        tangent_line.shift(self.p_point)
        tangent_line.set_color(arc_color)
        right_angle_symbol = Mobject(
            Line(UP, UP+RIGHT),
            Line(UP+RIGHT, RIGHT)
        )
        right_angle_symbol.scale(0.3)
        right_angle_symbol.rotate(tangent_line.get_angle()+np.pi)
        right_angle_symbol.shift(self.p_point)

        self.play(ShowCreation(line))
        self.play(ShimmerIn(words))
        self.wait()
        pairs = [    
            (line_angle, arc_angle/2),
            (line_angle+arc_angle/2, -arc_angle),
            (line_angle-arc_angle/2, arc_angle/2),
        ]
        arcs = []
        for start, angle in pairs:
            arc = Arc(
                angle = angle,
                radius = line_length,
                start_angle = start,
                color = GREEN
            )
            arc.shift(self.c_point)
            self.play(
                ShowCreation(arc),
                ApplyMethod(
                    line.rotate_in_place, 
                    angle,
                    path_func = path_along_arc(angle)
                ),
                run_time = 2
            )
            arcs.append(arc)
        self.wait()
        self.play(Transform(arcs[1], tangent_line))
        self.add(tangent_line)
        self.play(ShowCreation(right_angle_symbol))
        self.wait()

        self.tangent_line = tangent_line
        self.right_angle_symbol = right_angle_symbol
        self.pc_line = line
        self.remove(words, *arcs)

    def show_diameter(self):
        exceptions = [
            self.circle, 
            self.tangent_line,
            self.pc_line,
            self.right_angle_symbol
        ]
        everything = set(self.mobjects).difference(exceptions)
        everything_copy = Mobject(*everything).copy()
        light_everything = everything_copy.copy()
        dark_everything = everything_copy.copy()
        dark_everything.fade(0.8)
        bottom_point = np.array(self.c_point)
        bottom_point += 2*self.radius*DOWN
        diameter = Line(bottom_point, self.c_point)
        brace = Brace(diameter, RIGHT)
        diameter_word = TextMobject("Diameter")
        d_mob = TexMobject("D")
        diameter_word.next_to(brace)
        d_mob.next_to(diameter)

        self.remove(*everything)
        self.play(Transform(everything_copy, dark_everything))
        self.wait()
        self.play(ShowCreation(diameter))
        self.play(GrowFromCenter(brace))
        self.play(ShimmerIn(diameter_word))
        self.wait()
        self.play(*[
            Transform(mob, d_mob)
            for mob in (brace, diameter_word)
        ])
        self.remove(brace, diameter_word)
        self.add(d_mob)
        self.play(Transform(everything_copy, light_everything))
        self.remove(everything_copy)
        self.add(*everything)

        self.d_mob = d_mob
        self.bottom_point = bottom_point        

    def show_theta(self, radius = 1):
        arc = Arc(
            angle = self.tangent_line.get_angle()-np.pi/2,
            radius = radius,
            start_angle = np.pi/2
        )

        theta = TexMobject("\\theta")
        theta.shift(1.5*arc.get_center())
        Mobject(arc, theta).shift(self.bottom_point)

        self.play(
            ShowCreation(arc),
            ShimmerIn(theta)
        )
        self.arc = arc 
        self.theta = theta

    def show_similar_triangles(self):
        y_point = np.array(self.p_point)
        y_point[1] = self.point_a[1]
        new_arc = Arc(
            angle = self.tangent_line.get_angle()-np.pi/2,
            radius = 0.5,
            start_angle = np.pi
        )
        new_arc.shift(self.c_point)
        new_theta = self.theta.copy()
        new_theta.next_to(new_arc, LEFT)
        new_theta.shift(0.1*DOWN)
        kwargs = {
            "stroke_width" : 2*DEFAULT_STROKE_WIDTH,
        }
        triangle1 = Polygon(
            self.p_point, self.c_point, self.bottom_point,
            color = MAROON,
            **kwargs
        )
        triangle2 = Polygon(
            y_point, self.p_point, self.c_point,
            color = WHITE,
            **kwargs
        )
        y_line = Line(self.p_point, y_point)

        self.play(
            Transform(self.arc.copy(), new_arc),
            Transform(self.theta.copy(), new_theta),
            run_time = 3
        )
        self.wait()
        self.play(FadeIn(triangle1))
        self.wait()
        self.play(Transform(triangle1, triangle2))
        self.play(ApplyMethod(triangle1.set_color, MAROON))
        self.wait()
        self.remove(triangle1)
        self.add(y_line)

        self.y_line = y_line

    def show_sin_thetas(self):
        pc = Line(self.p_point, self.c_point)
        mob = Mobject(self.theta, self.d_mob).copy()
        mob.ingest_submobjects()
        triplets = [
            (pc, "D\\sin(\\theta)", 0.5),
            (self.y_line, "D\\sin^2(\\theta)", 0.7),
        ]
        for line, tex, scale in triplets:
            trig_mob = TexMobject(tex)
            trig_mob.set_width(
                scale*line.get_length()
            )
            trig_mob.shift(-1.2*trig_mob.get_top())
            trig_mob.rotate(line.get_angle())
            trig_mob.shift(line.get_center())
            if line is self.y_line:
                trig_mob.shift(0.1*UP) 

            self.play(Transform(mob, trig_mob))
            self.add(trig_mob)
            self.wait()

        self.remove(mob)
        self.d_sin_squared_theta = trig_mob


    def show_y(self):
        y_equals = TexMobject(["y", "="])
        y_equals.shift(2*UP)
        y_expression = TexMobject([
            "D ", "\\sin", "^2", "(\\theta)"
        ])
        y_expression.next_to(y_equals)
        y_expression.shift(0.05*UP+0.1*RIGHT)
        temp_expr = self.d_sin_squared_theta.copy()
        temp_expr.rotate(-np.pi/2)
        temp_expr.replace(y_expression)
        y_mob = TexMobject("y")
        y_mob.next_to(self.y_line, RIGHT)
        y_mob.shift(0.2*UP)

        self.play(
            Transform(self.d_sin_squared_theta, temp_expr),
            ShimmerIn(y_mob),
            ShowCreation(y_equals)
        )
        self.remove(self.d_sin_squared_theta)
        self.add(y_expression)

        self.y_equals = y_equals
        self.y_expression = y_expression

    def rearrange(self):
        sqrt_nudge = 0.2*LEFT        
        y, equals = self.y_equals.split()
        d, sin, squared, theta = self.y_expression.split()
        y_sqrt = TexMobject("\\sqrt{\\phantom{y}}")
        d_sqrt = y_sqrt.copy()
        y_sqrt.shift(y.get_center()+sqrt_nudge)
        d_sqrt.shift(d.get_center()+sqrt_nudge)

        self.play(
            ShimmerIn(y_sqrt),
            ShimmerIn(d_sqrt),
            ApplyMethod(squared.shift, 4*UP),
            ApplyMethod(theta.shift, 1.5* squared.get_width()*LEFT)
        )
        self.wait()
        y_sqrt.add(y)
        d_sqrt.add(d)
        sin.add(theta)

        sin_over = TexMobject("\\dfrac{\\phantom{\\sin(\\theta)}}{\\quad}")
        sin_over.next_to(sin, DOWN, 0.15)
        new_eq = equals.copy()
        new_eq.next_to(sin_over, LEFT)
        one_over = TexMobject("\\dfrac{1}{\\quad}")
        one_over.next_to(new_eq, LEFT)
        one_over.shift(
            (sin_over.get_bottom()[1]-one_over.get_bottom()[1])*UP
        )

        self.play(
            Transform(equals, new_eq),
            ShimmerIn(sin_over),
            ShimmerIn(one_over),
            ApplyMethod(
                d_sqrt.next_to, one_over, DOWN,
                path_func = path_along_arc(-np.pi)
            ),
            ApplyMethod(
                y_sqrt.next_to, sin_over, DOWN,
                path_func = path_along_arc(-np.pi)
            ),
            run_time = 2
        )
        self.wait()

        brace = Brace(d_sqrt, DOWN)
        constant = TextMobject("Constant")
        constant.next_to(brace, DOWN)

        self.play(
            GrowFromCenter(brace),
            ShimmerIn(constant)
        )




class EquationsForCycloid(CycloidScene):
    def construct(self):
        CycloidScene.construct(self)
        equations = TexMobject([
            "x(t) = Rt - R\\sin(t)",
            "y(t) = -R + R\\cos(t)"
        ])
        top, bottom = equations.split()
        bottom.next_to(top, DOWN)
        equations.center()
        equations.to_edge(UP, buff = 1.3)

        self.play(ShimmerIn(equations))
        self.grow_parts()
        self.draw_cycloid(rate_func=linear, run_time = 5)
        self.wait()

class SlidingObject(CycloidScene, PathSlidingScene):
    CONFIG = {
        "show_time" : False,
        "wait_and_add" : False
    }

    args_list = [(True,), (False,)]

    @staticmethod
    def args_to_string(with_words):
        return "WithWords" if with_words else "WithoutWords"
        
    @staticmethod
    def string_to_args(string):
        return string == "WithWords"

    def construct(self, with_words):
        CycloidScene.construct(self)

        randy = Randolph()
        randy.scale(RANDY_SCALE_FACTOR)
        randy.shift(-randy.get_bottom())
        central_randy = randy.copy()
        start_randy = self.adjust_mobject_to_index(
            randy.copy(), 1, self.cycloid.points
        )

        if with_words:
            words1 = TextMobject("Trajectory due to gravity")
            arrow = TexMobject("\\leftrightarrow")
            words2 = TextMobject("Trajectory due \\emph{constantly} rotating wheel")
            words1.next_to(arrow, LEFT)
            words2.next_to(arrow, RIGHT)
            words = Mobject(words1, arrow, words2)
            words.set_width(FRAME_WIDTH-1)
            words.to_edge(UP, buff = 0.2)
            words.to_edge(LEFT)

        self.play(ShowCreation(self.cycloid.copy()))
        self.slide(randy, self.cycloid)
        self.add(self.slider)
        self.wait()
        self.grow_parts()
        self.draw_cycloid()
        self.wait()
        self.play(Transform(self.slider, start_randy))
        self.wait()
        self.roll_back()
        self.wait()
        if with_words:
            self.play(*list(map(ShimmerIn, [words1, arrow, words2])))
        self.wait()
        self.remove(self.circle)
        start_time = len(self.frames)*self.frame_duration
        self.remove(self.slider)        
        self.slide(central_randy, self.cycloid)
        end_time = len(self.frames)*self.frame_duration
        self.play_over_time_range(
            start_time,
            end_time,
            RollAlongVector(
                self.circle, 
                self.cycloid.points[-1]-self.cycloid.points[0],
                run_time = end_time-start_time,
                rate_func=linear
            )
        )
        self.add(self.circle, self.slider)
        self.wait()



class RotateWheel(CycloidScene):
    def construct(self):
        CycloidScene.construct(self)
        self.circle.center()

        self.play(Rotating(
            self.circle,
            axis = OUT,
            run_time = 5,
            rate_func = smooth
        ))










