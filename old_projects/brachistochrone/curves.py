from manimlib.imports import *

RANDY_SCALE_FACTOR = 0.3



class Cycloid(ParametricFunction):
    CONFIG = {
        "point_a"       : 6*LEFT+3*UP,
        "radius"        : 2,
        "end_theta"     : 3*np.pi/2,
        "density"       : 5*DEFAULT_POINT_DENSITY_1D,
        "color"         : YELLOW
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        ParametricFunction.__init__(self, self.pos_func, **kwargs)

    def pos_func(self, t):
        T = t*self.end_theta
        return self.point_a + self.radius * np.array([
            T - np.sin(T),
            np.cos(T) - 1,
            0
        ])

class LoopTheLoop(ParametricFunction):
    CONFIG = {
        "color" : YELLOW_D,
        "density" : 10*DEFAULT_POINT_DENSITY_1D
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        def func(t):
            t = (6*np.pi/2)*(t-0.5)
            return (t/2-np.sin(t))*RIGHT + \
                   (np.cos(t)+(t**2)/10)*UP
        ParametricFunction.__init__(self, func, **kwargs)


class SlideWordDownCycloid(Animation):
    CONFIG = { 
        "rate_func" : None,
        "run_time"  : 8
    }
    def __init__(self, word, **kwargs):
        self.path = Cycloid(end_theta = np.pi)        
        word_mob = TextMobject(list(word))
        end_word = word_mob.copy()
        end_word.shift(-end_word.get_bottom())
        end_word.shift(self.path.get_corner(DOWN+RIGHT))
        end_word.shift(3*RIGHT)
        self.end_letters = end_word.split()
        for letter in word_mob.split():
            letter.center()
            letter.angle = 0
        unit_interval = np.arange(0, 1, 1./len(word))
        self.start_times = 0.5*(1-(unit_interval))
        Animation.__init__(self, word_mob, **kwargs)

    def interpolate_mobject(self, alpha):
        virtual_times = 2*(alpha - self.start_times)
        cut_offs = [
            0.1,
            0.3,
            0.7,
        ]
        for letter, time, end_letter in zip(
            self.mobject.split(), virtual_times, self.end_letters
            ):
            time = max(time, 0)
            time = min(time, 1)
            if time < cut_offs[0]:
                brightness = time/cut_offs[0]
                letter.rgbas = brightness*np.ones(letter.rgbas.shape)
                position = self.path.points[0]
                angle = 0
            elif time < cut_offs[1]:
                alpha = (time-cut_offs[0])/(cut_offs[1]-cut_offs[0])
                angle = -rush_into(alpha)*np.pi/2
                position = self.path.points[0]
            elif time < cut_offs[2]:
                alpha = (time-cut_offs[1])/(cut_offs[2]-cut_offs[1])
                index = int(alpha*self.path.get_num_points())
                position = self.path.points[index]
                try:
                    angle = angle_of_vector(
                        self.path.points[index+1] - \
                        self.path.points[index]
                    )
                except:
                    angle = letter.angle
            else:
                alpha = (time-cut_offs[2])/(1-cut_offs[2])
                start = self.path.points[-1]
                end = end_letter.get_bottom()
                position = interpolate(start, end, rush_from(alpha))
                angle = 0

            letter.shift(position-letter.get_bottom())
            letter.rotate_in_place(angle-letter.angle)
            letter.angle = angle


class BrachistochroneWordSliding(Scene):
    def construct(self):
        anim = SlideWordDownCycloid("Brachistochrone")
        anim.path.set_color_by_gradient(WHITE, BLUE_E)
        self.play(ShowCreation(anim.path))
        self.play(anim)
        self.wait()
        self.play(
            FadeOut(anim.path),
            ApplyMethod(anim.mobject.center)
        )



class PathSlidingScene(Scene):
    CONFIG = {
        "gravity" : 3,
        "delta_t" : 0.05,
        "wait_and_add" : True,
        "show_time" : True,
    }
    def slide(self, mobject, path, roll = False, ceiling = None):
        points = path.points
        time_slices = self.get_time_slices(points, ceiling = ceiling)
        curr_t = 0
        last_index = 0
        curr_index = 1
        if self.show_time:
            self.t_equals = TexMobject("t = ")
            self.t_equals.shift(3.5*UP+4*RIGHT)
            self.add(self.t_equals)
        while curr_index < len(points):
            self.slider = mobject.copy()
            self.adjust_mobject_to_index(
                self.slider, curr_index, points
            )
            if roll:
                distance = get_norm(
                    points[curr_index] - points[last_index]
                )
                self.roll(mobject, distance)
            self.add(self.slider)
            if self.show_time:
                self.write_time(curr_t)
            self.wait(self.frame_duration)
            self.remove(self.slider)
            curr_t += self.delta_t
            last_index = curr_index
            while time_slices[curr_index] < curr_t:
                curr_index += 1
                if curr_index == len(points):
                    break
        if self.wait_and_add:
            self.add(self.slider)
            self.wait()
        else:
            return self.slider

    def get_time_slices(self, points, ceiling = None):
        dt_list = np.zeros(len(points))
        ds_list = np.apply_along_axis(
            get_norm,
            1,
            points[1:]-points[:-1]
        )
        if ceiling is None:
            ceiling = points[0, 1]
        delta_y_list = np.abs(ceiling - points[1:,1])
        delta_y_list += 0.001*(delta_y_list == 0)
        v_list = self.gravity*np.sqrt(delta_y_list)
        dt_list[1:] = ds_list / v_list
        return np.cumsum(dt_list)

    def adjust_mobject_to_index(self, mobject, index, points):
        point_a, point_b = points[index-1], points[index]
        while np.all(point_a == point_b):
            index += 1
            point_b = points[index]
        theta = angle_of_vector(point_b - point_a)
        mobject.rotate(theta)
        mobject.shift(points[index])
        self.midslide_action(point_a, theta)
        return mobject

    def midslide_action(self, point, angle):
        pass

    def write_time(self, time):
        if hasattr(self, "time_mob"):
            self.remove(self.time_mob)
        digits = list(map(TexMobject, "%.2f"%time))
        digits[0].next_to(self.t_equals, buff = 0.1)
        for left, right in zip(digits, digits[1:]):
            right.next_to(left, buff = 0.1, aligned_edge = DOWN)
        self.time_mob = Mobject(*digits)
        self.add(self.time_mob)

    def roll(self, mobject, arc_length):
        radius = mobject.get_width()/2
        theta = arc_length / radius
        mobject.rotate_in_place(-theta)

    def add_cycloid_end_points(self):
        cycloid = Cycloid()
        point_a = Dot(cycloid.points[0])
        point_b = Dot(cycloid.points[-1])
        A = TexMobject("A").next_to(point_a, LEFT)
        B = TexMobject("B").next_to(point_b, RIGHT)
        self.add(point_a, point_b, A, B)
        digest_locals(self)


class TryManyPaths(PathSlidingScene):
    def construct(self):
        randy = Randolph()
        randy.shift(-randy.get_bottom())
        self.slider = randy.copy()  
        randy.scale(RANDY_SCALE_FACTOR)
        paths = self.get_paths()
        point_a = Dot(paths[0].points[0])
        point_b = Dot(paths[0].points[-1])
        A = TexMobject("A").next_to(point_a, LEFT)
        B = TexMobject("B").next_to(point_b, RIGHT)
        for point, tex in [(point_a, A), (point_b, B)]:
            self.play(ShowCreation(point))
            self.play(ShimmerIn(tex))
            self.wait()
        curr_path = None        
        for path in paths:
            new_slider = self.adjust_mobject_to_index(
                randy.copy(), 1, path.points
            )
            if curr_path is None:
                curr_path = path
                self.play(ShowCreation(curr_path))
            else:
                self.play(Transform(curr_path, path))
            self.play(Transform(self.slider, new_slider))
            self.wait()
            self.remove(self.slider)
            self.slide(randy, curr_path)
        self.clear()
        self.add(point_a, point_b, A, B, curr_path)
        text = self.get_text()
        text.to_edge(UP)
        self.play(ShimmerIn(text))
        for path in paths:
            self.play(Transform(
                curr_path, path,
                path_func = path_along_arc(np.pi/2),
                run_time = 3
            ))

    def get_text(self):
        return TextMobject("Which path is fastest?")

    def get_paths(self):
        sharp_corner = Mobject(
            Line(3*UP+LEFT, LEFT),
            Arc(angle = np.pi/2, start_angle = np.pi),
            Line(DOWN, DOWN+3*RIGHT)
        ).ingest_submobjects().set_color(GREEN)
        paths = [
            Arc(
                angle = np.pi/2, 
                radius = 3, 
                start_angle = 4
            ),
            LoopTheLoop(),            
            Line(7*LEFT, 7*RIGHT, color = RED_D),
            sharp_corner,
            FunctionGraph(
                lambda x : 0.05*(x**2)+0.1*np.sin(2*x)
            ),
            FunctionGraph(
                lambda x : x**2, 
                x_min = -3, 
                x_max = 2,
                density = 3*DEFAULT_POINT_DENSITY_1D
            )
        ]
        cycloid = Cycloid()
        self.align_paths(paths, cycloid)
        return paths + [cycloid]

    def align_paths(self, paths, target_path):
        start = target_path.points[0]
        end = target_path.points[-1]
        for path in paths:
            path.put_start_and_end_on(start, end)


class RollingRandolph(PathSlidingScene):
    def construct(self):
        randy = Randolph()
        randy.scale(RANDY_SCALE_FACTOR)
        randy.shift(-randy.get_bottom())
        self.add_cycloid_end_points()        
        self.slide(randy, self.cycloid, roll = True)



class NotTheCircle(PathSlidingScene):
    def construct(self):
        self.add_cycloid_end_points()
        start = self.point_a.get_center()
        end   = self.point_b.get_center()
        angle = 2*np.pi/3
        path = Arc(angle, radius = 3)
        path.set_color_by_gradient(RED_D, WHITE)
        radius = Line(ORIGIN, path.points[0])
        randy = Randolph()
        randy.scale(RANDY_SCALE_FACTOR)
        randy.shift(-randy.get_bottom())
        randy_copy = randy.copy()
        words = TextMobject("Circular paths are good, \\\\ but still not the best")
        words.shift(UP)

        self.play(
            ShowCreation(path),
            ApplyMethod(
                radius.rotate, 
                angle,
                path_func = path_along_arc(angle)
            )
        )
        self.play(FadeOut(radius))
        self.play(
            ApplyMethod(
                path.put_start_and_end_on, start, end,
                path_func = path_along_arc(-angle)
            ),
            run_time = 3
        )
        self.adjust_mobject_to_index(randy_copy, 1, path.points)
        self.play(FadeIn(randy_copy))
        self.remove(randy_copy)
        self.slide(randy, path)
        self.play(ShimmerIn(words))
        self.wait()


class TransitionAwayFromSlide(PathSlidingScene):
    def construct(self):
        randy = Randolph()
        randy.scale(RANDY_SCALE_FACTOR)
        randy.shift(-randy.get_bottom())
        self.add_cycloid_end_points()
        arrow = Arrow(ORIGIN, 2*RIGHT)
        arrows = Mobject(*[
            arrow.copy().shift(vect)
            for vect in (3*LEFT, ORIGIN, 3*RIGHT)
        ])
        arrows.shift(FRAME_WIDTH*RIGHT)
        self.add(arrows)

        self.add(self.cycloid)
        self.slide(randy, self.cycloid)
        everything = Mobject(*self.mobjects)
        self.play(ApplyMethod(
            everything.shift, 4*FRAME_X_RADIUS*LEFT,
            run_time = 2,
            rate_func = rush_into
        ))
        

class MinimalPotentialEnergy(Scene):
    def construct(self):
        horiz_radius = 5
        vert_radius = 3

        vert_axis = NumberLine(numerical_radius = vert_radius)
        vert_axis.rotate(np.pi/2)
        vert_axis.shift(horiz_radius*LEFT)
        horiz_axis = NumberLine(
            numerical_radius = 5,
            numbers_with_elongated_ticks = []
        )
        axes = Mobject(horiz_axis, vert_axis)
        graph = FunctionGraph(
            lambda x : 0.4*(x-2)*(x+2)+3,
            x_min = -2,
            x_max = 2,
            density = 3*DEFAULT_POINT_DENSITY_1D
        )
        graph.stretch_to_fit_width(2*horiz_radius)
        graph.set_color(YELLOW)
        min_point = Dot(graph.get_bottom())
        nature_finds = TextMobject("Nature finds this point")
        nature_finds.scale(0.5)
        nature_finds.set_color(GREEN)
        nature_finds.shift(2*RIGHT+3*UP)
        arrow = Arrow(
            nature_finds.get_bottom(), min_point, 
            color = GREEN
        )

        side_words_start = TextMobject("Parameter describing")
        top_words, last_side_words = [
            list(map(TextMobject, pair))
            for pair in [
                ("Light's travel time", "Potential energy"),
                ("path", "mechanical state")
            ]
        ]
        for word in top_words + last_side_words + [side_words_start]:
            word.scale(0.7)
        side_words_start.next_to(horiz_axis, DOWN)
        side_words_start.to_edge(RIGHT)
        for words in top_words:
            words.next_to(vert_axis, UP)
            words.to_edge(LEFT)
        for words in last_side_words:
            words.next_to(side_words_start, DOWN)
        for words in top_words[1], last_side_words[1]:
            words.set_color(RED)

        self.add(
            axes, top_words[0], side_words_start, 
            last_side_words[0]
        )
        self.play(ShowCreation(graph))
        self.play(
            ShimmerIn(nature_finds),
            ShowCreation(arrow),
            ShowCreation(min_point)
        )
        self.wait()
        self.play(
            FadeOut(top_words[0]), 
            FadeOut(last_side_words[0]),
            GrowFromCenter(top_words[1]), 
            GrowFromCenter(last_side_words[1])
        )
        self.wait(3)




class WhatGovernsSpeed(PathSlidingScene):
    CONFIG = {
        "num_pieces" : 6,
        "wait_and_add" : False,
        "show_time" : False,
    }
    def construct(self):
        randy = Randolph()
        randy.scale(RANDY_SCALE_FACTOR)
        randy.shift(-randy.get_bottom())
        self.add_cycloid_end_points()
        points = self.cycloid.points
        ceiling = points[0, 1]
        n = len(points)
        broken_points = [
            points[k*n/self.num_pieces:(k+1)*n/self.num_pieces]
            for k in range(self.num_pieces)
        ]
        words = TextMobject("""
            What determines the speed\\\\
            at each point?
        """)
        words.to_edge(UP)

        self.add(self.cycloid)
        sliders, vectors = [], []
        for points in broken_points:
            path = Mobject().add_points(points)
            vect = points[-1] - points[-2]
            magnitude = np.sqrt(ceiling - points[-1, 1])
            vect = magnitude*vect/get_norm(vect)
            slider = self.slide(randy, path, ceiling = ceiling)
            vector = Vector(slider.get_center(), vect)
            self.add(slider, vector)
            sliders.append(slider)
            vectors.append(vector)
        self.wait()
        self.play(ShimmerIn(words))
        self.wait(3)
        slider = sliders.pop(1)
        vector = vectors.pop(1)
        faders = sliders+vectors+[words]
        self.play(*list(map(FadeOut, faders)))
        self.remove(*faders)
        self.show_geometry(slider, vector)

    def show_geometry(self, slider, vector):
        point_a = self.point_a.get_center()
        horiz_line = Line(point_a, point_a + 6*RIGHT)
        ceil_point = point_a
        ceil_point[0] = slider.get_center()[0]
        vert_brace = Brace(
            Mobject(Point(ceil_point), Point(slider.get_center())),
            RIGHT,
            buff = 0.5
        )
        vect_brace = Brace(slider)
        vect_brace.stretch_to_fit_width(vector.get_length())
        vect_brace.rotate(np.arctan(vector.get_slope()))
        vect_brace.center().shift(vector.get_center())
        nudge = 0.2*(DOWN+LEFT)
        vect_brace.shift(nudge)
        y_mob = TexMobject("y")
        y_mob.next_to(vert_brace)
        sqrt_y = TexMobject("k\\sqrt{y}")
        sqrt_y.scale(0.5)
        sqrt_y.shift(vect_brace.get_center())
        sqrt_y.shift(3*nudge)

        self.play(ShowCreation(horiz_line))
        self.play(
            GrowFromCenter(vert_brace),
            ShimmerIn(y_mob)
        )
        self.play(
            GrowFromCenter(vect_brace),
            ShimmerIn(sqrt_y)
        )
        self.wait(3)
        self.solve_energy()

    def solve_energy(self):
        loss_in_potential = TextMobject("Loss in potential: ")
        loss_in_potential.shift(2*UP)
        potential = TexMobject("m g y".split())
        potential.next_to(loss_in_potential)
        kinetic = TexMobject([
            "\\dfrac{1}{2}","m","v","^2","="
        ])
        kinetic.next_to(potential, LEFT)
        nudge = 0.1*UP
        kinetic.shift(nudge)
        loss_in_potential.shift(nudge)
        ms = Mobject(kinetic.split()[1], potential.split()[0])
        two = TexMobject("2")
        two.shift(ms.split()[1].get_center())
        half = kinetic.split()[0]
        sqrt = TexMobject("\\sqrt{\\phantom{2mg}}")
        sqrt.shift(potential.get_center())
        nudge = 0.2*LEFT
        sqrt.shift(nudge)
        squared = kinetic.split()[3]
        equals = kinetic.split()[-1]
        new_eq = equals.copy().next_to(kinetic.split()[2])

        self.play(
            Transform(
                Point(loss_in_potential.get_left()),
                loss_in_potential
            ),
            *list(map(GrowFromCenter, potential.split()))
        )
        self.wait(2)
        self.play(
            FadeOut(loss_in_potential),
            GrowFromCenter(kinetic)
        )
        self.wait(2)
        self.play(ApplyMethod(ms.shift, 5*UP))
        self.wait()
        self.play(Transform(
            half, two, 
            path_func = counterclockwise_path()
        ))
        self.wait()
        self.play(
            Transform(
                squared, sqrt, 
                path_func = clockwise_path()
            ),
            Transform(equals, new_eq)
        )
        self.wait(2)




class ThetaTInsteadOfXY(Scene):
    def construct(self):
        cycloid = Cycloid()
        index = cycloid.get_num_points()/3
        point = cycloid.points[index]
        vect = cycloid.points[index+1]-point
        vect /= get_norm(vect)
        vect *= 3
        vect_mob = Vector(point, vect)
        dot = Dot(point)
        xy = TexMobject("\\big( x(t), y(t) \\big)")
        xy.next_to(dot, UP+RIGHT, buff = 0.1)
        vert_line = Line(2*DOWN, 2*UP)
        vert_line.shift(point)
        angle = vect_mob.get_angle() + np.pi/2
        arc = Arc(angle, radius = 1, start_angle = -np.pi/2)
        arc.shift(point)
        theta = TexMobject("\\theta(t)")
        theta.next_to(arc, DOWN, buff = 0.1, aligned_edge = LEFT)
        theta.shift(0.2*RIGHT)

        self.play(ShowCreation(cycloid))
        self.play(ShowCreation(dot))
        self.play(ShimmerIn(xy))
        self.wait()
        self.play(
            FadeOut(xy),
            ShowCreation(vect_mob)
        )
        self.play(
            ShowCreation(arc),
            ShowCreation(vert_line),
            ShimmerIn(theta)
        )
        self.wait()


class DefineCurveWithKnob(PathSlidingScene):
    def construct(self):
        self.knob = Circle(color = BLUE_D)
        self.knob.add_line(UP, DOWN)
        self.knob.to_corner(UP+RIGHT)
        self.knob.shift(0.5*DOWN)
        self.last_angle = np.pi/2
        arrow = Vector(ORIGIN, RIGHT)
        arrow.next_to(self.knob, LEFT)
        words = TextMobject("Turn this knob over time to define the curve")
        words.next_to(arrow, LEFT)
        self.path = self.get_path()
        self.path.shift(1.5*DOWN)
        self.path.show()
        self.path.set_color(BLACK)        

        randy = Randolph()
        randy.scale(RANDY_SCALE_FACTOR)
        randy.shift(-randy.get_bottom())

        self.play(ShimmerIn(words))
        self.play(ShowCreation(arrow))
        self.play(ShowCreation(self.knob))
        self.wait()
        self.add(self.path)

        self.slide(randy, self.path)
        self.wait()


    def get_path(self):
        return Cycloid(end_theta = 2*np.pi)

    def midslide_action(self, point, angle):
        d_angle = angle-self.last_angle
        self.knob.rotate_in_place(d_angle)
        self.last_angle = angle
        self.path.set_color(BLUE_D, lambda p : p[0] < point[0])



class WonkyDefineCurveWithKnob(DefineCurveWithKnob):
    def get_path(self):
        return ParametricFunction(
            lambda t : t*RIGHT + (-0.2*t-np.sin(2*np.pi*t/6))*UP,
            start = -7, 
            end = 10
        )


class SlowDefineCurveWithKnob(DefineCurveWithKnob):
    def get_path(self):
        return ParametricFunction(
            lambda t : t*RIGHT + (np.exp(-(t+2)**2)-0.2*np.exp(t-2)),
            start = -4, 
            end = 4
        )


class BumpyDefineCurveWithKnob(DefineCurveWithKnob):
    def get_path(self):

        result = FunctionGraph(
            lambda x : 0.05*(x**2)+0.1*np.sin(2*x)
        )
        result.rotate(-np.pi/20)
        result.scale(0.7)
        result.shift(DOWN)
        return result













