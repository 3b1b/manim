import numpy as np
import itertools as it

from manimlib.imports import *

from old_projects.brachistochrone.curves import \
    Cycloid, PathSlidingScene, RANDY_SCALE_FACTOR, TryManyPaths


class Lens(Arc):
    CONFIG = {
        "radius" : 2,
        "angle" : np.pi/2,
        "color" : BLUE_B,
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        Arc.__init__(self, self.angle, **kwargs)

    def generate_points(self):
        Arc.generate_points(self)
        self.rotate(-np.pi/4)
        self.shift(-self.get_left())
        self.add_points(self.copy().rotate(np.pi).points)



class PhotonScene(Scene):
    def wavify(self, mobject):
        result = mobject.copy()
        result.ingest_submobjects()
        tangent_vectors = result.points[1:]-result.points[:-1]
        lengths = np.apply_along_axis(
            get_norm, 1, tangent_vectors
        )
        thick_lengths = lengths.repeat(3).reshape((len(lengths), 3))
        unit_tangent_vectors = tangent_vectors/thick_lengths
        rot_matrix = np.transpose(rotation_matrix(np.pi/2, OUT))
        normal_vectors = np.dot(unit_tangent_vectors, rot_matrix)
        # total_length = np.sum(lengths)
        times = np.cumsum(lengths)
        nudge_sizes = 0.1*np.sin(2*np.pi*times)
        thick_nudge_sizes = nudge_sizes.repeat(3).reshape((len(nudge_sizes), 3))
        nudges = thick_nudge_sizes*normal_vectors
        result.points[1:] += nudges
        return result


    def photon_run_along_path(self, path, color = YELLOW, **kwargs):
        if "rate_func" not in kwargs:
            kwargs["rate_func"] = None
        photon = self.wavify(path)
        photon.set_color(color)
        return ShowPassingFlash(photon, **kwargs)


class SimplePhoton(PhotonScene):
    def construct(self):
        text = TextMobject("Light")
        text.to_edge(UP)
        self.play(ShimmerIn(text))
        self.play(self.photon_run_along_path(
            Cycloid(), rate_func=linear
        ))
        self.wait()


class MultipathPhotonScene(PhotonScene):
    CONFIG = {
        "num_paths" : 5
    }
    def run_along_paths(self, **kwargs):
        paths = self.get_paths()
        colors = Color(YELLOW).range_to(WHITE, len(paths))
        for path, color in zip(paths, colors):
            path.set_color(color)
        photon_runs = [
            self.photon_run_along_path(path)
            for path in paths
        ]
        for photon_run, path in zip(photon_runs, paths):
            self.play(
                photon_run,
                ShowCreation(
                    path,
                    rate_func = lambda t : 0.9*smooth(t)
                ), 
                **kwargs
            )
        self.wait()

    def generate_paths(self):
        raise Exception("Not Implemented")


class PhotonThroughLens(MultipathPhotonScene):
    def construct(self):
        self.lens = Lens()
        self.add(self.lens)
        self.run_along_paths()


    def get_paths(self):
        interval_values = np.arange(self.num_paths).astype('float')
        interval_values /= (self.num_paths-1.)
        first_contact = [
            self.lens.point_from_proportion(0.4*v+0.55)
            for v in reversed(interval_values)
        ]
        second_contact = [
            self.lens.point_from_proportion(0.3*v + 0.1)
            for v in interval_values
        ]
        focal_point = 2*RIGHT
        return [
            Mobject(
                Line(FRAME_X_RADIUS*LEFT + fc[1]*UP, fc),
                Line(fc, sc),
                Line(sc, focal_point),
                Line(focal_point, 6*focal_point-5*sc)
            ).ingest_submobjects()
            for fc, sc in zip(first_contact, second_contact)
        ]

class TransitionToOptics(PhotonThroughLens):
    def construct(self):
        optics = TextMobject("Optics")
        optics.to_edge(UP)
        self.add(optics)
        self.has_started = False
        PhotonThroughLens.construct(self)

    def play(self, *args, **kwargs):
        if not self.has_started:
            self.has_started = True
            everything = Mobject(*self.mobjects)
            vect = FRAME_WIDTH*RIGHT
            everything.shift(vect)
            self.play(ApplyMethod(
                everything.shift, -vect,
                rate_func = rush_from
            ))
        Scene.play(self, *args, **kwargs)


class PhotonOffMirror(MultipathPhotonScene):
    def construct(self):
        self.mirror = Line(*FRAME_Y_RADIUS*np.array([DOWN, UP]))
        self.mirror.set_color(GREY)
        self.add(self.mirror)
        self.run_along_paths()

    def get_paths(self):
        interval_values = np.arange(self.num_paths).astype('float')
        interval_values /= (self.num_paths-1)
        anchor_points = [
            self.mirror.point_from_proportion(0.6*v+0.3)
            for v in interval_values
        ]
        start_point = 5*LEFT+3*UP
        end_points = []
        for point in anchor_points:
            vect = start_point-point
            vect[1] *= -1
            end_points.append(point+2*vect)
        return [
            Mobject(
                Line(start_point, anchor_point), 
                Line(anchor_point, end_point)
            ).ingest_submobjects()
            for anchor_point, end_point in zip(anchor_points, end_points)
        ]

class PhotonsInWater(MultipathPhotonScene):
    def construct(self):
        water = Region(lambda x, y : y < 0, color = BLUE_E)
        self.add(water)
        self.run_along_paths()

    def get_paths(self):
        x, y = -3, 3
        start_point = x*RIGHT + y*UP
        angles = np.arange(np.pi/18, np.pi/3, np.pi/18)
        midpoints = y*np.arctan(angles)
        end_points = midpoints + FRAME_Y_RADIUS*np.arctan(2*angles)
        return [
            Mobject(
                Line(start_point, [midpoint, 0, 0]),
                Line([midpoint, 0, 0], [end_point, -FRAME_Y_RADIUS, 0])
            ).ingest_submobjects()
            for midpoint, end_point in zip(midpoints, end_points)
        ]


class ShowMultiplePathsScene(PhotonScene):
    def construct(self):
        text = TextMobject("Which path minimizes travel time?")
        text.to_edge(UP)
        self.generate_start_and_end_points()
        point_a = Dot(self.start_point)
        point_b = Dot(self.end_point)
        A = TextMobject("A").next_to(point_a, UP)
        B = TextMobject("B").next_to(point_b, DOWN)
        paths = self.get_paths()

        for point, letter in [(point_a, A), (point_b, B)]:
            self.play(
                ShowCreation(point),
                ShimmerIn(letter)
            )
        self.play(ShimmerIn(text))
        curr_path = paths[0].copy()
        curr_path_copy = curr_path.copy().ingest_submobjects()
        self.play(
            self.photon_run_along_path(curr_path),
            ShowCreation(curr_path_copy, rate_func = rush_into)
        )
        self.remove(curr_path_copy)
        for path in paths[1:] + [paths[0]]:
            self.play(Transform(curr_path, path, run_time = 4))
        self.wait()
        self.path = curr_path.ingest_submobjects()

    def generate_start_and_end_points(self):
        raise Exception("Not Implemented")

    def get_paths(self):
        raise Exception("Not implemented")


class ShowMultiplePathsThroughLens(ShowMultiplePathsScene):
    def construct(self):
        self.lens = Lens()
        self.add(self.lens)
        ShowMultiplePathsScene.construct(self)

    def generate_start_and_end_points(self):
        self.start_point = 3*LEFT + UP
        self.end_point = 2*RIGHT

    def get_paths(self):
        alphas = [0.25, 0.4, 0.58, 0.75]
        lower_right, upper_right, upper_left, lower_left = list(map(
            self.lens.point_from_proportion, alphas
        ))
        return [
            Mobject(
                Line(self.start_point, a),
                Line(a, b),
                Line(b, self.end_point)
            ).set_color(color)
            for (a, b), color in zip(
                [
                    (upper_left, upper_right),
                    (upper_left, lower_right),
                    (lower_left, lower_right),
                    (lower_left, upper_right),
                ],
                Color(YELLOW).range_to(WHITE, 4)
            )
        ]


class ShowMultiplePathsOffMirror(ShowMultiplePathsScene):
    def construct(self):
        mirror = Line(*FRAME_Y_RADIUS*np.array([DOWN, UP]))
        mirror.set_color(GREY)
        self.add(mirror)
        ShowMultiplePathsScene.construct(self)

    def generate_start_and_end_points(self):
        self.start_point = 4*LEFT + 2*UP
        self.end_point = 4*LEFT + 2*DOWN

    def get_paths(self):
        return [
            Mobject(
                Line(self.start_point, midpoint),
                Line(midpoint, self.end_point)
            ).set_color(color)
            for midpoint, color in zip(
                [2*UP, 2*DOWN],
                Color(YELLOW).range_to(WHITE, 2)
            )
        ]


class ShowMultiplePathsInWater(ShowMultiplePathsScene):
    def construct(self):
        glass = Region(lambda x, y : y < 0, color = BLUE_E)
        self.generate_start_and_end_points()
        straight = Line(self.start_point, self.end_point)
        slow = TextMobject("Slow")
        slow.rotate(np.arctan(straight.get_slope()))
        slow.shift(straight.points[int(0.7*straight.get_num_points())])
        slow.shift(0.5*DOWN)
        too_long = TextMobject("Too long")
        too_long.shift(UP)
        air = TextMobject("Air").shift(2*UP)
        water = TextMobject("Water").shift(2*DOWN)

        self.add(glass)
        self.play(GrowFromCenter(air))
        self.play(GrowFromCenter(water))
        self.wait()
        self.remove(air, water)
        ShowMultiplePathsScene.construct(self)
        self.play(
            Transform(self.path, straight)
        )
        self.wait()
        self.play(GrowFromCenter(slow))
        self.wait()
        self.remove(slow)
        self.leftmost.ingest_submobjects()
        self.play(Transform(self.path, self.leftmost, run_time = 3))
        self.wait()
        self.play(ShimmerIn(too_long))
        self.wait()


    def generate_start_and_end_points(self):
        self.start_point = 3*LEFT + 2*UP
        self.end_point = 3*RIGHT + 2*DOWN

    def get_paths(self):
        self.leftmost, self.rightmost = result = [
            Mobject(
                Line(self.start_point, midpoint),
                Line(midpoint, self.end_point)
            ).set_color(color)
            for midpoint, color in zip(
                [3*LEFT, 3*RIGHT],
                Color(YELLOW).range_to(WHITE, 2)
            )
        ]
        return result


class StraightLinesFastestInConstantMedium(PhotonScene):
    def construct(self):
        kwargs = {"size" : "\\Large"}
        left = TextMobject("Speed of light is constant", **kwargs)
        arrow = TexMobject("\\Rightarrow", **kwargs)
        right = TextMobject("Staight path is fastest", **kwargs)
        left.next_to(arrow, LEFT)
        right.next_to(arrow, RIGHT)
        squaggle, line = self.get_paths()        

        self.play(*list(map(ShimmerIn, [left, arrow, right])))
        self.play(ShowCreation(squaggle))
        self.play(self.photon_run_along_path(
            squaggle, run_time = 2, rate_func=linear
        ))
        self.play(Transform(
            squaggle, line, 
            path_func = path_along_arc(np.pi)
        ))
        self.play(self.photon_run_along_path(line, rate_func=linear))
        self.wait()


    def get_paths(self):
        squaggle = ParametricFunction(
            lambda t : (0.5*t+np.cos(t))*RIGHT+np.sin(t)*UP,
            start = -np.pi,
            end = 2*np.pi
        )
        squaggle.shift(2*UP)
        start, end = squaggle.points[0], squaggle.points[-1]
        line = Line(start, end)
        result = [squaggle, line]
        for mob in result:
            mob.set_color(BLUE_D)
        return result

class PhtonBendsInWater(PhotonScene, ZoomedScene):
    def construct(self):
        glass = Region(lambda x, y : y < 0, color = BLUE_E)
        kwargs = {
            "density" : self.zoom_factor*DEFAULT_POINT_DENSITY_1D
        }
        top_line = Line(FRAME_Y_RADIUS*UP+2*LEFT, ORIGIN, **kwargs)
        extension = Line(ORIGIN, FRAME_Y_RADIUS*DOWN+2*RIGHT, **kwargs)
        bottom_line = Line(ORIGIN, FRAME_Y_RADIUS*DOWN+RIGHT, **kwargs)
        path1 = Mobject(top_line, extension)
        path2 = Mobject(top_line, bottom_line)
        for mob in path1, path2:
            mob.ingest_submobjects()
        extension.set_color(RED)
        theta1 = np.arctan(bottom_line.get_slope())
        theta2 = np.arctan(extension.get_slope())
        arc = Arc(theta2-theta1, start_angle = theta1, radius = 2)
        question_mark = TextMobject("$\\theta$?")
        question_mark.shift(arc.get_center()+0.5*DOWN+0.25*RIGHT)
        wave = self.wavify(path2)
        wave.set_color(YELLOW)
        wave.scale(0.5)

        self.add(glass)
        self.play(ShowCreation(path1))
        self.play(Transform(path1, path2))
        self.wait()
        # self.activate_zooming()
        self.wait()        
        self.play(ShowPassingFlash(
            wave, run_time = 3, rate_func=linear
        ))
        self.wait()
        self.play(ShowCreation(extension))
        self.play(
            ShowCreation(arc),
            ShimmerIn(question_mark)
        )

class LightIsFasterInAirThanWater(ShowMultiplePathsInWater):
    def construct(self):
        glass = Region(lambda x, y : y < 0, color = BLUE_E)
        equation = TexMobject("v_{\\text{air}} > v_{\\text{water}}")
        equation.to_edge(UP)
        path = Line(FRAME_X_RADIUS*LEFT, FRAME_X_RADIUS*RIGHT)
        path1 = path.copy().shift(2*UP)
        path2 = path.copy().shift(2*DOWN)

        self.add(glass)
        self.play(ShimmerIn(equation))
        self.wait()
        photon_runs = []
        photon_runs.append(self.photon_run_along_path(
            path1, rate_func = lambda t : min(1, 1.2*t)
        ))
        photon_runs.append(self.photon_run_along_path(path2))
        self.play(*photon_runs, **{"run_time" : 2})
        self.wait()


class GeometryOfGlassSituation(ShowMultiplePathsInWater):
    def construct(self):
        glass = Region(lambda x, y : y < 0, color = BLUE_E)
        self.generate_start_and_end_points()
        left = self.start_point[0]*RIGHT
        right = self.end_point[0]*RIGHT
        start_x = interpolate(left, right, 0.2)
        end_x = interpolate(left, right, 1.0)
        left_line = Line(self.start_point, left, color = RED_D)
        right_line = Line(self.end_point, right, color = RED_D)
        h_1, h_2 = list(map(TexMobject, ["h_1", "h_2"]))
        h_1.next_to(left_line, LEFT)
        h_2.next_to(right_line, RIGHT)
        point_a = Dot(self.start_point)
        point_b = Dot(self.end_point)
        A = TextMobject("A").next_to(point_a, UP)
        B = TextMobject("B").next_to(point_b, DOWN)

        x = start_x
        left_brace = Brace(Mobject(Point(left), Point(x)))
        right_brace = Brace(Mobject(Point(x), Point(right)), UP)
        x_mob = TexMobject("x")
        x_mob.next_to(left_brace, DOWN)
        w_minus_x = TexMobject("w-x")
        w_minus_x.next_to(right_brace, UP)
        top_line = Line(self.start_point, x)
        bottom_line = Line(x, self.end_point)
        top_dist = TexMobject("\\sqrt{h_1^2+x^2}")
        top_dist.scale(0.5)
        a = 0.3
        n = top_line.get_num_points()
        point = top_line.points[int(a*n)]
        top_dist.next_to(Point(point), RIGHT, buff = 0.3)
        bottom_dist = TexMobject("\\sqrt{h_2^2+(w-x)^2}")
        bottom_dist.scale(0.5)
        n = bottom_line.get_num_points()
        point = bottom_line.points[int((1-a)*n)]
        bottom_dist.next_to(Point(point), LEFT, buff = 1)

        end_top_line = Line(self.start_point, end_x)
        end_bottom_line = Line(end_x, self.end_point)
        end_brace = Brace(Mobject(Point(left), Point(end_x)))
        end_x_mob = TexMobject("x").next_to(end_brace, DOWN)

        axes = Mobject(
            NumberLine(),
            NumberLine().rotate(np.pi/2).shift(7*LEFT)
        )
        graph = FunctionGraph(
            lambda x : 0.4*(x+1)*(x-3)+4,
            x_min = -2,
            x_max = 4
        )
        graph.set_color(YELLOW)
        Mobject(axes, graph).scale(0.2).to_corner(UP+RIGHT, buff = 1)
        axes.add(TexMobject("x", size = "\\small").next_to(axes, RIGHT))
        axes.add(TextMobject("Travel time", size = "\\small").next_to(
            axes, UP
        ))
        new_graph = graph.copy()
        midpoint = new_graph.points[new_graph.get_num_points()/2]
        new_graph.filter_out(lambda p : p[0] < midpoint[0])
        new_graph.reverse_points()
        pairs_for_end_transform = [
            (mob, mob.copy())
            for mob in (top_line, bottom_line, left_brace, x_mob)
        ]

        self.add(glass, point_a, point_b, A, B)
        line = Mobject(top_line, bottom_line).ingest_submobjects()
        self.play(ShowCreation(line))
        self.wait()
        self.play(
            GrowFromCenter(left_brace), 
            GrowFromCenter(x_mob)
        )
        self.play(
            GrowFromCenter(right_brace), 
            GrowFromCenter(w_minus_x)
        )
        self.play(ShowCreation(left_line), ShimmerIn(h_1))
        self.play(ShowCreation(right_line), GrowFromCenter(h_2))
        self.play(ShimmerIn(top_dist))
        self.play(GrowFromCenter(bottom_dist))
        self.wait(3)
        self.clear()
        self.add(glass, point_a, point_b, A, B, 
                 top_line, bottom_line, left_brace, x_mob)
        self.play(ShowCreation(axes))
        kwargs = {
            "run_time" : 4,
        }
        self.play(*[
            Transform(*pair, **kwargs)
            for pair in [
                (top_line, end_top_line),
                (bottom_line, end_bottom_line),
                (left_brace, end_brace),
                (x_mob, end_x_mob)
            ]
        ]+[ShowCreation(graph, **kwargs)])
        self.wait()
        self.show_derivatives(graph)
        line = self.show_derivatives(new_graph)
        self.add(line)
        self.play(*[
            Transform(*pair, rate_func = lambda x : 0.3*smooth(x))
            for pair in pairs_for_end_transform
        ])
        self.wait()

    def show_derivatives(self, graph, run_time = 2):
        step = self.frame_duration/run_time
        for a in smooth(np.arange(0, 1-step, step)):
            index = int(a*graph.get_num_points())
            p1, p2 = graph.points[index], graph.points[index+1]
            line = Line(LEFT, RIGHT)
            line.rotate(angle_of_vector(p2-p1))
            line.shift(p1)
            self.add(line)
            self.wait(self.frame_duration)
            self.remove(line)
        return line


class Spring(Line):
    CONFIG = {
        "num_loops" : 5,
        "loop_radius" : 0.3,
        "color" : GREY
    }

    def generate_points(self):
        ## self.start, self.end
        length = get_norm(self.end-self.start)
        angle = angle_of_vector(self.end-self.start)
        micro_radius = self.loop_radius/length
        m = 2*np.pi*(self.num_loops+0.5)
        def loop(t):
            return micro_radius*(
                RIGHT + np.cos(m*t)*LEFT + np.sin(m*t)*UP
            )
        new_epsilon = self.epsilon/(m*micro_radius)/length

        self.add_points([
            t*RIGHT + loop(t)
            for t in np.arange(0, 1, new_epsilon)
        ])
        self.scale(length/(1+2*micro_radius))
        self.rotate(angle)
        self.shift(self.start)


class SpringSetup(ShowMultiplePathsInWater):
    def construct(self):
        self.ring_shift_val = 6*RIGHT
        self.slide_kwargs = {
            "rate_func" : there_and_back,
            "run_time" : 5
        }

        self.setup_background()
        rod = Region(
            lambda x, y : (abs(x) < 5) & (abs(y) < 0.05),
            color = GOLD_E
        )
        ring = Arc(
            angle = 11*np.pi/6,
            start_angle = -11*np.pi/12,
            radius = 0.2,
            color = YELLOW
        )
        ring.shift(-self.ring_shift_val/2)
        self.generate_springs(ring)                


        self.add_rod_and_ring(rod, ring)
        self.slide_ring(ring)
        self.wait()
        self.add_springs()
        self.add_force_definitions()
        self.slide_system(ring)
        self.show_horizontal_component(ring)
        self.show_angles(ring)
        self.show_equation()


    def setup_background(self):
        glass = Region(lambda x, y : y < 0, color = BLUE_E)
        self.generate_start_and_end_points()
        point_a = Dot(self.start_point)
        point_b = Dot(self.end_point)
        A = TextMobject("A").next_to(point_a, UP)
        B = TextMobject("B").next_to(point_b, DOWN)
        self.add(glass, point_a, point_b, A, B)

    def generate_springs(self, ring):
        self.start_springs, self.end_springs = [
            Mobject(
                Spring(self.start_point, r.get_top()),
                Spring(self.end_point, r.get_bottom())
            )
            for r in (ring, ring.copy().shift(self.ring_shift_val))
        ]
        
    def add_rod_and_ring(self, rod, ring):
        rod_word = TextMobject("Rod")
        rod_word.next_to(Point(), UP)
        ring_word = TextMobject("Ring")
        ring_word.next_to(ring, UP)
        self.wait()
        self.add(rod)
        self.play(ShimmerIn(rod_word))
        self.wait()
        self.remove(rod_word)
        self.play(ShowCreation(ring))
        self.play(ShimmerIn(ring_word))
        self.wait()
        self.remove(ring_word)

    def slide_ring(self, ring):
        self.play(ApplyMethod(
            ring.shift, self.ring_shift_val,
            **self.slide_kwargs
        ))

    def add_springs(self):
        colors = iter([BLACK, BLUE_E])
        for spring in self.start_springs.split():
            circle = Circle(color = next(colors))
            circle.reverse_points()
            circle.scale(spring.loop_radius)
            circle.shift(spring.points[0])

            self.play(Transform(circle, spring))
            self.remove(circle)
            self.add(spring)
            self.wait()

    def add_force_definitions(self):
        top_force = TexMobject("F_1 = \\dfrac{1}{v_{\\text{air}}}")
        bottom_force = TexMobject("F_2 = \\dfrac{1}{v_{\\text{water}}}")
        top_spring, bottom_spring = self.start_springs.split()
        top_force.next_to(top_spring)
        bottom_force.next_to(bottom_spring, DOWN, buff = -0.5)
        words = TextMobject("""
            The force in a real spring is 
            proportional to that spring's length
        """)
        words.to_corner(UP+RIGHT)
        for force in top_force, bottom_force:
            self.play(GrowFromCenter(force))
            self.wait()
        self.play(ShimmerIn(words))
        self.wait(3)
        self.remove(top_force, bottom_force, words)

    def slide_system(self, ring):
        equilibrium_slide_kwargs = dict(self.slide_kwargs)
        def jiggle_to_equilibrium(t):
            return 0.7*(1+((1-t)**2)*(-np.cos(10*np.pi*t)))
        equilibrium_slide_kwargs = {
            "rate_func" : jiggle_to_equilibrium,
            "run_time" : 3
        }
        start = Mobject(ring, self.start_springs)
        end = Mobject(
            ring.copy().shift(self.ring_shift_val),
            self.end_springs
        )
        for kwargs in self.slide_kwargs, equilibrium_slide_kwargs:
            self.play(Transform(start, end, **kwargs))
            self.wait()
    
    def show_horizontal_component(self, ring):
        v_right = Vector(ring.get_top(), RIGHT)
        v_left = Vector(ring.get_bottom(), LEFT)
        self.play(*list(map(ShowCreation, [v_right, v_left])))
        self.wait()
        self.remove(v_right, v_left)

    def show_angles(self, ring):
        ring_center = ring.get_center()
        lines, arcs, thetas = [], [], []
        counter = it.count(1)
        for point in self.start_point, self.end_point:
            line = Line(point, ring_center, color = GREY)
            angle = np.pi/2-np.abs(np.arctan(line.get_slope()))
            arc = Arc(angle, radius = 0.5).rotate(np.pi/2)
            if point is self.end_point:
                arc.rotate(np.pi)
            theta = TexMobject("\\theta_%d"%next(counter))
            theta.scale(0.5)
            theta.shift(2*arc.get_center())
            arc.shift(ring_center)
            theta.shift(ring_center)

            lines.append(line)
            arcs.append(arc)
            thetas.append(theta)
        vert_line = Line(2*UP, 2*DOWN)
        vert_line.shift(ring_center)
        top_spring, bottom_spring = self.start_springs.split()

        self.play(
            Transform(ring, Point(ring_center)),
            Transform(top_spring, lines[0]),
            Transform(bottom_spring, lines[1])
        )
        self.play(ShowCreation(vert_line))
        anims = []
        for arc, theta in zip(arcs, thetas):
            anims += [
                ShowCreation(arc),
                GrowFromCenter(theta)
            ]
        self.play(*anims)
        self.wait()

    def show_equation(self):
        equation = TexMobject([
            "\\left(\\dfrac{1}{\\phantom{v_air}}\\right)",
            "\\sin(\\theta_1)", 
            "=", 
            "\\left(\\dfrac{1}{\\phantom{v_water}}\\right)",
            "\\sin(\\theta_2)"
        ])
        equation.to_corner(UP+RIGHT)
        frac1, sin1, equals, frac2, sin2 = equation.split()
        v_air, v_water = [
            TexMobject("v_{\\text{%s}}"%s, size = "\\Large")
            for s in ("air", "water")
        ]
        v_air.next_to(Point(frac1.get_center()), DOWN)
        v_water.next_to(Point(frac2.get_center()), DOWN)
        frac1.add(v_air)
        frac2.add(v_water)
        f1, f2 = [
            TexMobject("F_%d"%d, size = "\\Large") 
            for d in (1, 2)
        ]
        f1.next_to(sin1, LEFT)
        f2.next_to(equals, RIGHT)
        sin2_start = sin2.copy().next_to(f2, RIGHT)
        bar1 = TexMobject("\\dfrac{\\qquad}{\\qquad}")
        bar2 = bar1.copy()
        bar1.next_to(sin1, DOWN)
        bar2.next_to(sin2, DOWN)        
        v_air_copy = v_air.copy().next_to(bar1, DOWN)
        v_water_copy = v_water.copy().next_to(bar2, DOWN)
        bars = Mobject(bar1, bar2)
        new_eq = equals.copy().center().shift(bars.get_center())
        snells = TextMobject("Snell's Law")
        snells.set_color(YELLOW)
        snells.shift(new_eq.get_center()[0]*RIGHT)
        snells.shift(UP)

        anims = []
        for mob in f1, sin1, equals, f2, sin2_start:
            anims.append(ShimmerIn(mob))
        self.play(*anims)
        self.wait()
        for f, frac in (f1, frac1), (f2, frac2):
            target = frac.copy().ingest_submobjects()
            also = []
            if f is f2:
                also.append(Transform(sin2_start, sin2))
                sin2 = sin2_start
            self.play(Transform(f, target), *also)
            self.remove(f)
            self.add(frac)
        self.wait()
        self.play(
            FadeOut(frac1),
            FadeOut(frac2),
            Transform(v_air, v_air_copy),
            Transform(v_water, v_water_copy),
            ShowCreation(bars),
            Transform(equals, new_eq)
        )
        self.wait()
        frac1 = Mobject(sin1, bar1, v_air)
        frac2 = Mobject(sin2, bar2, v_water)
        for frac, vect in (frac1, LEFT), (frac2, RIGHT):
            self.play(ApplyMethod(
                frac.next_to, equals, vect
            ))
        self.wait()
        self.play(ShimmerIn(snells))
        self.wait()

class WhatGovernsTheSpeedOfLight(PhotonScene, PathSlidingScene):
    def construct(self):
        randy = Randolph()
        randy.scale(RANDY_SCALE_FACTOR)
        randy.shift(-randy.get_bottom())
        self.add_cycloid_end_points()   

        self.add(self.cycloid)
        self.slide(randy, self.cycloid)
        self.play(self.photon_run_along_path(self.cycloid))

        self.wait()

class WhichPathWouldLightTake(PhotonScene, TryManyPaths):
    def construct(self):
        words = TextMobject(
            ["Which path ", "would \\emph{light} take", "?"]
        )
        words.split()[1].set_color(YELLOW)
        words.to_corner(UP+RIGHT)
        self.add_cycloid_end_points()

        anims = [
            self.photon_run_along_path(
                path, 
                rate_func = smooth
            )
            for path in  self.get_paths()
        ]
        self.play(anims[0], ShimmerIn(words))
        for anim in anims[1:]:
            self.play(anim)



class StateSnellsLaw(PhotonScene):
    def construct(self):
        point_a = 3*LEFT+3*UP
        point_b = 1.5*RIGHT+3*DOWN
        midpoint = ORIGIN

        lines, arcs, thetas = [], [], []
        counter = it.count(1)
        for point in point_a, point_b:
            line = Line(point, midpoint, color = RED_D)
            angle = np.pi/2-np.abs(np.arctan(line.get_slope()))
            arc = Arc(angle, radius = 0.5).rotate(np.pi/2)
            if point is point_b:
                arc.rotate(np.pi)
                line.reverse_points()
            theta = TexMobject("\\theta_%d"%next(counter))
            theta.scale(0.5)
            theta.shift(2*arc.get_center())
            arc.shift(midpoint)
            theta.shift(midpoint)

            lines.append(line)
            arcs.append(arc)
            thetas.append(theta)
        vert_line = Line(2*UP, 2*DOWN)
        vert_line.shift(midpoint)
        path = Mobject(*lines).ingest_submobjects()
        glass = Region(lambda x, y : y < 0, color = BLUE_E)
        self.add(glass)
        equation = TexMobject([
            "\\dfrac{\\sin(\\theta_1)}{v_{\\text{air}}}",
            "=",            
            "\\dfrac{\\sin(\\theta_2)}{v_{\\text{water}}}",
        ])
        equation.to_corner(UP+RIGHT)
        exp1, equals, exp2 = equation.split()
        snells_law = TextMobject("Snell's Law:")
        snells_law.set_color(YELLOW)
        snells_law.to_edge(UP)

        self.play(ShimmerIn(snells_law))
        self.wait()
        self.play(ShowCreation(path))
        self.play(self.photon_run_along_path(path))
        self.wait()
        self.play(ShowCreation(vert_line))
        self.play(*list(map(ShowCreation, arcs)))
        self.play(*list(map(GrowFromCenter, thetas)))
        self.wait()
        self.play(ShimmerIn(exp1))
        self.wait()
        self.play(*list(map(ShimmerIn, [equals, exp2])))
        self.wait()
        









