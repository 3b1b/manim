import numpy as np
import itertools as it

from helpers import *

from mobject.tex_mobject import TexMobject, TextMobject, Brace
from mobject import Mobject, Mobject1D
from mobject.image_mobject import \
    ImageMobject, MobjectFromPixelArray
from topics.three_dimensions import Stars

from animation import Animation
from animation.transform import \
    Transform, CounterclockwiseTransform, ApplyPointwiseFunction,\
    FadeIn, FadeOut, GrowFromCenter, ApplyFunction, ApplyMethod, \
    ShimmerIn
from animation.simple_animations import \
    ShowCreation, Homotopy, PhaseFlow, ApplyToCenters, DelayByOrder, \
    ShowPassingFlash
from animation.playground import TurnInsideOut, Vibrate
from topics.geometry import \
    Line, Circle, Square, Grid, Rectangle, Arrow, Dot, Point, \
    Arc, FilledRectangle
from topics.characters import Randolph, Mathematician
from topics.functions import ParametricFunction, FunctionGraph
from topics.number_line import NumberPlane
from mobject.region import  Region, region_from_polygon_vertices
from scene import Scene
from scene.zoomed_scene import ZoomedScene

from brachistochrone.curves import Cycloid

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
        result.ingest_sub_mobjects()
        tangent_vectors = result.points[1:]-result.points[:-1]
        lengths = np.apply_along_axis(
            np.linalg.norm, 1, tangent_vectors
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
        photon = self.wavify(path)
        photon.highlight(color)
        return ShowPassingFlash(photon, **kwargs)


class SimplePhoton(PhotonScene):
    def construct(self):
        text = TextMobject("Light")
        text.to_edge(UP)
        self.play(ShimmerIn(text))
        self.play(self.photon_run_along_path(
            Cycloid(), rate_func = None
        ))
        self.dither()


class MultipathPhotonScene(PhotonScene):
    CONFIG = {
        "num_paths" : 5
    }
    def run_along_paths(self, **kwargs):
        paths = self.get_paths()
        colors = Color(YELLOW).range_to(WHITE, len(paths))
        for path, color in zip(paths, colors):
            path.highlight(color)
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
        self.dither()

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
                Line(SPACE_WIDTH*LEFT + fc[1]*UP, fc),
                Line(fc, sc),
                Line(sc, focal_point),
                Line(focal_point, 6*focal_point-5*sc)
            ).ingest_sub_mobjects()
            for fc, sc in zip(first_contact, second_contact)
        ]


class PhotonOffMirror(MultipathPhotonScene):
    def construct(self):
        self.mirror = Line(*SPACE_HEIGHT*np.array([DOWN, UP]))
        self.mirror.highlight(GREY)
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
            ).ingest_sub_mobjects()
            for anchor_point, end_point in zip(anchor_points, end_points)
        ]

class PhotonsInGlass(MultipathPhotonScene):
    def construct(self):
        glass = Region(lambda x, y : y < 0)
        self.highlight_region(glass, BLUE_E)
        self.run_along_paths()

    def get_paths(self):
        x, y = -3, 3
        start_point = x*RIGHT + y*UP
        angles = np.arange(np.pi/18, np.pi/3, np.pi/18)
        midpoints = y*np.arctan(angles)
        end_points = midpoints + SPACE_HEIGHT*np.arctan(2*angles)
        return [
            Mobject(
                Line(start_point, [midpoint, 0, 0]),
                Line([midpoint, 0, 0], [end_point, -SPACE_HEIGHT, 0])
            ).ingest_sub_mobjects()
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
        curr_path_copy = curr_path.copy().ingest_sub_mobjects()
        self.play(
            self.photon_run_along_path(curr_path),
            ShowCreation(curr_path_copy, rate_func = rush_into)
        )
        self.remove(curr_path_copy)
        for path in paths[1:] + [paths[0]]:
            self.play(Transform(curr_path, path, run_time = 4))
        self.dither()

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
        lower_right, upper_right, upper_left, lower_left = map(
            self.lens.point_from_proportion, alphas
        )
        return [
            Mobject(
                Line(self.start_point, a),
                Line(a, b),
                Line(b, self.end_point)
            ).highlight(color)
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
        mirror = Line(*SPACE_HEIGHT*np.array([DOWN, UP]))
        mirror.highlight(GREY)
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
            ).highlight(color)
            for midpoint, color in zip(
                [2*UP, 2*DOWN],
                Color(YELLOW).range_to(WHITE, 2)
            )
        ]


class ShowMultiplePathsInGlass(ShowMultiplePathsScene):
    def construct(self):
        glass = Region(lambda x, y : y < 0)
        self.highlight_region(glass, BLUE_E)
        ShowMultiplePathsScene.construct(self)

    def generate_start_and_end_points(self):
        self.start_point = 3*LEFT + 2*UP
        self.end_point = 3*RIGHT + 2*DOWN

    def get_paths(self):
        return [
            Mobject(
                Line(self.start_point, midpoint),
                Line(midpoint, self.end_point)
            ).highlight(color)
            for midpoint, color in zip(
                [3*LEFT, 3*RIGHT],
                Color(YELLOW).range_to(WHITE, 2)
            )
        ]


class MultilayeredGlass(PhotonScene, ZoomedScene):
    CONFIG = {
        "num_discrete_layers" : 5,
        "num_variables" : 3,
        "top_color" : BLUE_E,
        "bottom_color" : BLUE_A,
        "zoomed_canvas_space_shape" : (5, 5),
        "square_color" : GREEN_B,
    }
    def construct(self):
        self.cycloid = Cycloid(end_theta = np.pi)
        self.cycloid.highlight(YELLOW)
        self.top = self.cycloid.get_top()[1]
        self.bottom = self.cycloid.get_bottom()[1]-1
        self.generate_layers()
        self.generate_discrete_path()
        photon_run = self.photon_run_along_path(
            self.discrete_path,
            run_time = 1,
            rate_func = rush_into
        )

        self.continuous_to_smooth()
        self.add(*self.layers)
        self.show_layer_variables()
        self.play(photon_run)
        self.play(ShowCreation(self.discrete_path))
        self.isolate_bend_points()
        self.clear()
        self.add(*self.layers)
        self.show_main_equation()
        self.ask_continuous_question()

    def continuous_to_smooth(self):
        self.add(*self.layers)
        continuous = self.get_continuous_background()
        self.add(continuous)
        self.dither()
        self.play(ShowCreation(
            continuous,
            rate_func = lambda t : smooth(1-t)
        ))
        self.remove(continuous)
        self.dither()
        
    def get_continuous_background(self):
        glass = FilledRectangle(
            height = self.top-self.bottom,
            width = 2*SPACE_WIDTH,
        )
        glass.sort_points(lambda p : -p[1])
        glass.shift((self.top-glass.get_top()[1])*UP)
        glass.gradient_highlight(self.top_color, self.bottom_color)
        return glass

    def generate_layer_info(self):
        self.layer_thickness = float(self.top-self.bottom)/self.num_discrete_layers
        self.layer_tops = np.arange(
            self.top, self.bottom, -self.layer_thickness
        )
        top_rgb, bottom_rgb = [
            np.array(Color(color).get_rgb())
            for color in self.top_color, self.bottom_color
        ]
        epsilon = 1./(self.num_discrete_layers-1)
        self.layer_colors = [
            Color(rgb = interpolate(top_rgb, bottom_rgb, alpha))
            for alpha in np.arange(0, 1+epsilon, epsilon)
        ]

    def generate_layers(self):
        self.generate_layer_info()
        def create_region(top, color):
            return Region(
                lambda x, y : (y < top) & (y > top-self.layer_thickness),
                color = color
            )
        self.layers = [
            create_region(top, color)
            for top, color in zip(self.layer_tops, self.layer_colors)
        ]


    def generate_discrete_path(self):
        points = self.cycloid.points
        tops = list(self.layer_tops)
        tops.append(tops[-1]-self.layer_thickness)
        indices = [
            np.argmin(np.abs(points[:, 1]-top))
            for top in tops
        ]
        self.bend_points = points[indices[1:-1]]
        self.path_angles = []
        self.discrete_path = Mobject1D(
            color = YELLOW,
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
            points[end], SPACE_WIDTH*RIGHT+(self.layer_tops[-1]-1)*UP
        )

    def show_layer_variables(self):
        layer_top_pairs = zip(
            self.layer_tops[:self.num_variables], 
            self.layer_tops[1:]
        )
        v_equations = []
        start_ys = []
        end_ys = []
        center_paths = []
        braces = []
        for (top1, top2), x in zip(layer_top_pairs, it.count(1)):
            eq_mob = TexMobject(
                ["v_%d"%x, "=", "\sqrt{\phantom{y_1}}"],
                size = "\\Large"
            )
            midpoint = UP*(top1+top2)/2
            eq_mob.shift(midpoint)
            v_eq = eq_mob.split()
            center_paths.append(Line(
                midpoint+SPACE_WIDTH*LEFT, 
                midpoint+SPACE_WIDTH*RIGHT
            ))            
            brace_endpoints = Mobject(
                Point(self.top*UP+x*RIGHT),
                Point(top2*UP+x*RIGHT)
            )
            brace = Brace(brace_endpoints, RIGHT)

            start_y = TexMobject("y_%d"%x, size = "\\Large")
            end_y = start_y.copy()            
            start_y.next_to(brace, RIGHT)
            end_y.shift(v_eq[-1].get_center())
            end_y.shift(0.2*RIGHT)

            v_equations.append(v_eq)
            start_ys.append(start_y)
            end_ys.append(end_y)
            braces.append(brace)

        for v_eq, path, time in zip(v_equations, center_paths, [2, 1, 0.5]):
            photon_run = self.photon_run_along_path(
                path,
                rate_func = None
            )
            self.play(
                ShimmerIn(v_eq[0]),
                photon_run,
                run_time = time
            )
        self.dither()
        for start_y, brace in zip(start_ys, braces):
            self.add(start_y)            
            self.play(GrowFromCenter(brace))
        self.dither()
        quads = zip(v_equations, start_ys, end_ys, braces)
        self.equations = []
        for v_eq, start_y, end_y, brace in quads:
            self.remove(brace)
            self.play(
                ShowCreation(v_eq[1]),
                ShowCreation(v_eq[2]),
                Transform(start_y, end_y)
            )

            v_eq.append(start_y)
            self.equations.append(Mobject(*v_eq))

    def isolate_bend_points(self):
        arc_radius = 0.1
        self.activate_zooming()
        little_square = self.get_zoomed_camera_mobject()

        for index in range(3):
            bend_point = self.bend_points[index]
            line = Line(
                bend_point+DOWN, 
                bend_point+UP,
                color = WHITE,
                density = self.zoom_factor*DEFAULT_POINT_DENSITY_1D
            )
            angle_arcs = []
            for i, rotation in [(index, np.pi/2), (index+1, -np.pi/2)]:
                arc = Arc(angle = self.path_angles[i])
                arc.scale(arc_radius)
                arc.rotate(rotation)
                arc.shift(bend_point)
                angle_arcs.append(arc)
            thetas = []
            for i in [index+1, index+2]:
                theta = TexMobject("\\theta_%d"%i)
                theta.scale(0.5/self.zoom_factor)
                vert = UP if i == index+1 else DOWN
                horiz = rotate_vector(vert, np.pi/2)
                theta.next_to(
                    Point(bend_point), 
                    horiz, 
                    buff = 0.01
                )
                theta.shift(1.5*arc_radius*vert)
                thetas.append(theta)
            figure_marks = [line] + angle_arcs + thetas                

            self.play(ApplyMethod(
                little_square.shift,
                bend_point - little_square.get_center(),
                run_time = 2
            ))
            self.play(*map(ShowCreation, figure_marks))
            self.dither()
            equation_frame = little_square.copy()
            equation_frame.scale(0.5)
            equation_frame.shift(
                little_square.get_corner(UP+RIGHT) - \
                equation_frame.get_corner(UP+RIGHT)
            )
            equation_frame.scale_in_place(0.9)
            self.show_snells(index+1, equation_frame)
            self.remove(*figure_marks)
        self.disactivate_zooming()

    def show_snells(self, index, frame):
        left_text, right_text = [
            "\\dfrac{\\sin(\\theta_%d)}{\\phantom{\\sqrt{y_1}}}"%x
            for x in index, index+1
        ]
        left, equals, right = TexMobject(
            [left_text, "=", right_text]
        ).split()
        vs = []
        sqrt_ys = []
        for x, numerator in [(index, left), (index+1, right)]:
            v, sqrt_y = [
                TexMobject(
                    text, size = "\\Large"
                ).next_to(numerator, DOWN)
                for text in "v_%d"%x, "\\sqrt{y_%d}"%x
            ]
            vs.append(v)
            sqrt_ys.append(sqrt_y)
        start, end = [
            Mobject(
                left.copy(), mobs[0], equals.copy(), right.copy(), mobs[1]
            ).replace(frame)
            for mobs in vs, sqrt_ys
        ]

        self.add(start)
        self.dither(2)
        self.play(Transform(
            start, end, 
            path_func = counterclockwise_path()
        ))
        self.dither(2)
        self.remove(start, end)

    def show_main_equation(self):
        self.equation = TexMobject("""
            \\dfrac{\\sin(\\theta)}{\\sqrt{y}} = 
            \\text{constant}
        """)
        self.equation.shift(LEFT)
        self.equation.shift(
            (self.layer_tops[0]-self.equation.get_top())*UP
        )
        self.add(self.equation)
        self.dither()

    def ask_continuous_question(self):
        continuous = self.get_continuous_background()
        line = Line(
            UP, DOWN,
            density = self.zoom_factor*DEFAULT_POINT_DENSITY_1D
        )
        theta = TexMobject("\\theta")
        theta.scale(0.5/self.zoom_factor)

        self.play(
            ShowCreation(continuous),
            Animation(self.equation)
        )
        self.remove(*self.layers)
        self.play(ShowCreation(self.cycloid))
        self.activate_zooming()
        little_square = self.get_zoomed_camera_mobject()

        self.add(line)
        indices = np.arange(
            0, self.cycloid.get_num_points()-1, 10
        )
        for index in indices:
            point = self.cycloid.points[index]
            next_point = self.cycloid.points[index+1]
            angle = angle_of_vector(point - next_point)
            for mob in little_square, line:
                mob.shift(point - mob.get_center())
            arc = Arc(angle-np.pi/2, start_angle = np.pi/2)
            arc.scale(0.1)
            arc.shift(point)
            self.add(arc)
            if angle > np.pi/2 + np.pi/6:
                vect_angle = interpolate(np.pi/2, angle, 0.5)
                vect = rotate_vector(RIGHT, vect_angle)
                theta.center()
                theta.shift(point)
                theta.shift(0.15*vect)
                self.add(theta)
            self.dither(self.frame_duration)
            self.remove(arc)


class StraightLinesFastestInConstantMedium(PhotonScene):
    def construct(self):
        kwargs = {"size" : "\\Large"}
        left = TextMobject("Speed of light is constant", **kwargs)
        arrow = TexMobject("\\Rightarrow", **kwargs)
        right = TextMobject("Staight path is fastest", **kwargs)
        left.next_to(arrow, LEFT)
        right.next_to(arrow, RIGHT)
        squaggle, line = self.get_paths()        

        self.play(*map(ShimmerIn, [left, arrow, right]))
        self.play(ShowCreation(squaggle))
        self.play(Transform(
            squaggle, line, 
            path_func = path_along_arc(np.pi)
        ))
        self.play(self.photon_run_along_path(line))
        self.dither()


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
            mob.highlight(BLUE_D)
        return result

class GlassAndAir(PhotonScene):
    def construct(self):
        pass











