import numpy as np
import itertools as it

from manimlib.imports import *
from old_projects.brachistochrone.light import PhotonScene
from old_projects.brachistochrone.curves import *


class MultilayeredScene(Scene):
    CONFIG = {
        "n_layers" : 5,
        "top_color" : BLUE_E,
        "bottom_color" : BLUE_A,
        "total_glass_height" : 5,
        "top" : 3*UP,
        "RectClass" : Rectangle #FilledRectangle
    }

    def get_layers(self, n_layers = None):
        if n_layers is None:
            n_layers = self.n_layers
        width = FRAME_WIDTH
        height = float(self.total_glass_height)/n_layers
        rgb_pair = [
            np.array(Color(color).get_rgb())
            for color in (self.top_color, self.bottom_color)
        ]
        rgb_range = [
            interpolate(*rgb_pair+[x])
            for x in np.arange(0, 1, 1./n_layers)
        ]
        tops = [
            self.top + x*height*DOWN
            for x in range(n_layers)
        ]
        color = Color()
        result = []
        for top, rgb in zip(tops, rgb_range):
            color.set_rgb(rgb)
            rect = self.RectClass(
                height = height, 
                width = width, 
                color = color
            )
            rect.shift(top-rect.get_top())
            result.append(rect)
        return result

    def add_layers(self):
        self.layers = self.get_layers()
        self.add(*self.layers)
        self.freeze_background()

    def get_bottom(self):
        return self.top + self.total_glass_height*DOWN

    def get_continuous_glass(self):
        result = self.RectClass(
            width = FRAME_WIDTH,
            height = self.total_glass_height,
        )
        result.sort_points(lambda p : -p[1])
        result.set_color_by_gradient(self.top_color, self.bottom_color)
        result.shift(self.top-result.get_top())
        return result


class TwoToMany(MultilayeredScene):
    CONFIG = {
        "RectClass" : FilledRectangle
    }
    def construct(self):
        glass = self.get_glass()
        layers = self.get_layers()

        self.add(glass)
        self.wait()
        self.play(*[
            FadeIn(
                layer,
                rate_func = squish_rate_func(smooth, x, 1)
            )
            for layer, x in zip(layers[1:], it.count(0, 0.2))
        ]+[
            Transform(glass, layers[0])
        ])
        self.wait()

    def get_glass(self):
        return self.RectClass(
            height = FRAME_Y_RADIUS,
            width = FRAME_WIDTH,
            color = BLUE_E
        ).shift(FRAME_Y_RADIUS*DOWN/2)


class RaceLightInLayers(MultilayeredScene, PhotonScene):
    CONFIG = {
        "RectClass" : FilledRectangle
    }
    def construct(self):
        self.add_layers()
        line = Line(FRAME_X_RADIUS*LEFT, FRAME_X_RADIUS*RIGHT)
        lines = [
            line.copy().shift(layer.get_center())
            for layer in self.layers
        ]

        def rate_maker(x):
            return lambda t : min(x*x*t, 1)
        min_rate, max_rate = 1., 2.
        rates = np.arange(min_rate, max_rate, (max_rate-min_rate)/self.n_layers)
        self.play(*[
            self.photon_run_along_path(
                line,
                rate_func = rate_maker(rate),
                run_time = 2
            )
            for line, rate in zip(lines, rates)
        ])

class ShowDiscretePath(MultilayeredScene, PhotonScene):
    CONFIG = {
        "RectClass" : FilledRectangle
    }
    def construct(self):
        self.add_layers()
        self.cycloid = Cycloid(end_theta = np.pi)

        self.generate_discrete_path()
        self.play(ShowCreation(self.discrete_path))
        self.wait()
        self.play(self.photon_run_along_path(
            self.discrete_path,
            rate_func = rush_into,
            run_time = 3
        ))
        self.wait()


    def generate_discrete_path(self):
        points = self.cycloid.points
        tops = [mob.get_top()[1] for mob in self.layers]
        tops.append(tops[-1]-self.layers[0].get_height())
        indices = [
            np.argmin(np.abs(points[:, 1]-top))
            for top in tops
        ]
        self.bend_points = points[indices[1:-1]]
        self.path_angles = []
        self.discrete_path = Mobject1D(
            color = WHITE,
            density = 3*DEFAULT_POINT_DENSITY_1D
        )
        for start, end in zip(indices, indices[1:]):
            start_point, end_point = points[start], points[end]
            self.discrete_path.add_line(
                start_point, end_point
            )
            self.path_angles.append(
                angle_of_vector(start_point-end_point)-np.pi/2
            )
        self.discrete_path.add_line(
            points[end], FRAME_X_RADIUS*RIGHT+(tops[-1]-0.5)*UP
        )

class NLayers(MultilayeredScene):
    CONFIG = {
        "RectClass" : FilledRectangle
    }
    def construct(self):
        self.add_layers()
        brace = Brace(
            Mobject(
                Point(self.top),
                Point(self.get_bottom())
            ),
            RIGHT
        )
        n_layers = TextMobject("$n$ layers")
        n_layers.next_to(brace)

        self.wait()

        self.add(brace)
        self.show_frame()

        self.play(
            GrowFromCenter(brace),
            GrowFromCenter(n_layers)
        )
        self.wait()

class ShowLayerVariables(MultilayeredScene, PhotonScene):
    CONFIG = {
        "RectClass" : FilledRectangle
    }
    def construct(self):
        self.add_layers()
        v_equations = []
        start_ys = []
        end_ys = []
        center_paths = []
        braces = []
        for layer, x in zip(self.layers[:3], it.count(1)):
            eq_mob = TexMobject(
                ["v_%d"%x, "=", "\sqrt{\phantom{y_1}}"],
                size = "\\Large"
            )
            eq_mob.shift(layer.get_center()+2*LEFT)
            v_eq = eq_mob.split()
            v_eq[0].set_color(layer.get_color())
            path = Line(FRAME_X_RADIUS*LEFT, FRAME_X_RADIUS*RIGHT)
            path.shift(layer.get_center())
            brace_endpoints = Mobject(
                Point(self.top),
                Point(layer.get_bottom())
            )
            brace = Brace(brace_endpoints, RIGHT)
            brace.shift(x*RIGHT)

            start_y = TexMobject("y_%d"%x, size = "\\Large")
            end_y = start_y.copy()
            start_y.next_to(brace, RIGHT)
            end_y.shift(v_eq[-1].get_center())
            nudge = 0.2*RIGHT
            end_y.shift(nudge)

            v_equations.append(v_eq)
            start_ys.append(start_y)
            end_ys.append(end_y)
            center_paths.append(path)            
            braces.append(brace)

        for v_eq, path, time in zip(v_equations, center_paths, [2, 1, 0.5]):
            photon_run = self.photon_run_along_path(
                path,
                rate_func=linear
            )
            self.play(
                FadeToColor(v_eq[0], WHITE),
                photon_run,
                run_time = time
            )
        self.wait()

        starts = [0, 0.3, 0.6]
        self.play(*it.chain(*[
            [
                GrowFromCenter(
                    mob,
                    rate_func=squish_rate_func(smooth, start, 1)
                )
                for mob, start in zip(mobs, starts)
            ]
            for mobs in (start_ys, braces)
        ]))
        self.wait()

        triplets = list(zip(v_equations, start_ys, end_ys))
        anims = []
        for v_eq, start_y, end_y in triplets:
            anims += [
                ShowCreation(v_eq[1]),
                ShowCreation(v_eq[2]),
                Transform(start_y.copy(), end_y)
            ]
        self.play(*anims)
        self.wait()


class LimitingProcess(MultilayeredScene):
    CONFIG = {
        "RectClass" : FilledRectangle
    }
    def construct(self):
        num_iterations = 3
        layer_sets = [
            self.get_layers((2**x)*self.n_layers)
            for x in range(num_iterations)
        ]
        glass_sets = [
            Mobject(*[
                Mobject(
                    *layer_sets[x][(2**x)*index:(2**x)*(index+1)]
                )
                for index in range(self.n_layers)
            ]).ingest_submobjects()
            for x in range(num_iterations)
        ]
        glass_sets.append(self.get_continuous_glass())
        for glass_set in glass_sets:
            glass_set.sort_points(lambda p : p[1])
        curr_set = glass_sets[0]
        self.add(curr_set)
        for layer_set in glass_sets[1:]:
            self.wait()
            self.play(Transform(curr_set, layer_set))
        self.wait()



class ShowLightAndSlidingObject(MultilayeredScene, TryManyPaths, PhotonScene):
    CONFIG = {
        "show_time" : False,
        "wait_and_add" : False,
        "RectClass" : FilledRectangle
    }
    def construct(self):
        glass = self.get_continuous_glass()
        self.play(ApplyMethod(glass.fade, 0.8))
        self.freeze_background()

        paths = self.get_paths()
        for path in paths:
            if path.get_height() > self.total_glass_height:
                path.stretch(0.7, 1)
                path.shift(self.top - path.get_top())
            path.rgbas[:,2] = 0
        loop = paths.pop(1) ##Bad!
        randy = Randolph()
        randy.scale(RANDY_SCALE_FACTOR)
        randy.shift(-randy.get_bottom())
        photon_run = self.photon_run_along_path(
            loop, 
            rate_func = lambda t : smooth(1.2*t, 2),
            run_time = 4.1
        )
        text = self.get_text().to_edge(UP, buff = 0.2)

        self.play(ShowCreation(loop))
        self.wait()
        self.play(photon_run)
        self.remove(photon_run.mobject)
        randy = self.slide(randy, loop)
        self.add(randy)
        self.wait()
        self.remove(randy)
        self.play(ShimmerIn(text))
        for path in paths:
            self.play(Transform(
                loop, path,
                path_func = path_along_arc(np.pi/2),
                run_time = 2
            ))


class ContinuouslyObeyingSnellsLaw(MultilayeredScene):
    CONFIG = {
        "arc_radius" : 0.5,
        "RectClass" : FilledRectangle
    }
    def construct(self):
        glass = self.get_continuous_glass()
        self.add(glass)
        self.freeze_background()

        cycloid = Cycloid(end_theta = np.pi)
        cycloid.set_color(YELLOW)
        chopped_cycloid = cycloid.copy()
        n = cycloid.get_num_points()
        chopped_cycloid.filter_out(lambda p : p[1] > 1 and p[0] < 0)
        chopped_cycloid.reverse_points()


        self.play(ShowCreation(cycloid))
        ref_mob = self.snells_law_at_every_point(cycloid, chopped_cycloid)
        self.show_equation(chopped_cycloid, ref_mob)

    def snells_law_at_every_point(self, cycloid, chopped_cycloid):
        square = Square(side_length = 0.2, color = WHITE)
        words = TextMobject(["Snell's law ", "everywhere"])
        snells, rest = words.split()
        colon = TextMobject(":")
        words.next_to(square)
        words.shift(0.3*UP)
        combo = Mobject(square, words)
        combo.get_center = lambda : square.get_center()
        new_snells = snells.copy().center().to_edge(UP, buff = 1.5)
        colon.next_to(new_snells)
        colon.shift(0.05*DOWN)
            
        self.play(MoveAlongPath(
            combo, cycloid,
            run_time = 5
        ))
        self.play(MoveAlongPath(
            combo, chopped_cycloid,
            run_time = 4
        ))
        dot = Dot(combo.get_center())
        self.play(Transform(square, dot))
        self.play(
            Transform(snells, new_snells),
            Transform(rest, colon)
        )
        self.wait()
        return colon

    def get_marks(self, point1, point2):
        vert_line = Line(2*DOWN, 2*UP)
        tangent_line = vert_line.copy()
        theta = TexMobject("\\theta")
        theta.scale(0.5)
        angle = angle_of_vector(point1 - point2)
        tangent_line.rotate(
            angle - tangent_line.get_angle()
        )
        angle_from_vert = angle - np.pi/2
        for mob in vert_line, tangent_line:
            mob.shift(point1 - mob.get_center())
        arc = Arc(angle_from_vert, start_angle = np.pi/2)
        arc.scale(self.arc_radius)
        arc.shift(point1)
        vect_angle = angle_from_vert/2 + np.pi/2
        vect = rotate_vector(RIGHT, vect_angle)
        theta.center()
        theta.shift(point1)
        theta.shift(1.5*self.arc_radius*vect)
        return arc, theta, vert_line, tangent_line


    def show_equation(self, chopped_cycloid, ref_mob):
        point2, point1 = chopped_cycloid.points[-2:]
        arc, theta, vert_line, tangent_line = self.get_marks(
            point1, point2
        )
        equation = TexMobject([
            "\\sin(\\theta)",
            "\\over \\sqrt{y}",            
        ])
        sin, sqrt_y = equation.split()
        equation.next_to(ref_mob)
        const = TexMobject(" = \\text{constant}")
        const.next_to(equation)
        ceil_point = np.array(point1)
        ceil_point[1] = self.top[1]
        brace = Brace(
            Mobject(Point(point1), Point(ceil_point)),
            RIGHT
        )
        y_mob = TexMobject("y").next_to(brace)

        self.play(
            GrowFromCenter(sin),
            ShowCreation(arc), 
            GrowFromCenter(theta)
        )
        self.play(ShowCreation(vert_line))
        self.play(ShowCreation(tangent_line))
        self.wait()
        self.play(
            GrowFromCenter(sqrt_y),
            GrowFromCenter(brace),
            GrowFromCenter(y_mob)
        )
        self.wait()
        self.play(Transform(
            Point(const.get_left()), const
        ))
        self.wait()



















