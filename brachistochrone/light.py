import numpy as np
import itertools as it

from helpers import *

from mobject.tex_mobject import TexMobject, TextMobject, Brace
from mobject import Mobject, Mobject1D
from mobject.image_mobject import \
    MobjectFromRegion, ImageMobject, MobjectFromPixelArray
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
    def run_along_paths(self):
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
                )
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


class MultilayeredGlass(PhotonScene):
    CONFIG = {
        "num_discrete_layers" : 5,
        "num_variables" : 3,
        "top_color" : BLUE_E,
        "bottom_color" : BLUE_A,
    }
    def construct(self):
        self.cycloid = Cycloid(end_theta = np.pi)
        self.top = self.cycloid.get_top()[1]
        self.bottom = self.cycloid.get_bottom()[1]-1
        self.generate_layer_regions()
        self.generate_discrete_path()
        photon_run = self.photon_run_along_path(
            self.augmented_path,
            run_time = 1,
            rate_func = rush_into
        )

        # self.continuous_to_smooth()
        self.paint_layers()
        self.show_layer_variables()
        self.play(photon_run)
        self.play(ShowCreation(self.discrete_path))
        self.isolate_bend_points()
        # self.dither()

    def continuous_to_smooth(self):
        continuous = self.get_continuous_background()
        layers = Mobject(*[
            MobjectFromRegion(region, color)
            for region, color in zip(
                self.layer_regions, self.layer_colors
            )
        ])
        layers.ingest_sub_mobjects()

        self.play(FadeIn(continuous))
        self.play(Transform(continuous, layers))
        self.remove(continuous)
        self.paint_layers()
        self.dither()

    def paint_layers(self):
        # for region, color in zip(self.layer_regions, self.layer_colors):
        #     self.highlight_region(region, color)
        for top, color in zip(self.layer_tops, self.layer_colors):
            self.add(Line(
                SPACE_WIDTH*LEFT+top*UP, SPACE_WIDTH*RIGHT+top*UP, 
                color = color
            ))

    def get_continuous_background(self):
        glass = MobjectFromRegion(Region(
            lambda x, y : (y < self.top) & (y > self.bottom)
        ))
        glass.gradient_highlight(self.top_color, self.bottom_color)
        glass.scale_in_place(0.99)
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

    def generate_layer_regions(self):
        self.generate_layer_info()
        self.layer_regions =  [
            Region(lambda x, y : (y < top) & (y > top-self.layer_thickness))
            for top in self.layer_tops
        ]

    def generate_discrete_path(self):
        points = self.cycloid.points
        indices = [
            np.argmin(np.abs(points[:, 1]-top))
            for top in self.layer_tops
        ]
        self.bend_points = points[indices[1:-1]]
        self.discrete_path = Mobject1D(color = YELLOW)
        for start, end in zip(indices, indices[1:]):
            self.discrete_path.add_line(
                points[start], points[end]
            )
        self.augmented_path = self.discrete_path.copy()
        self.augmented_path.add_line(
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
            start_y.highlight(BLACK)            
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
        little_square = Square(side_length = 4, color = WHITE)
        little_square.scale(0.25)
        little_square.shift(self.bend_points[0])
        big_square = little_square.copy()
        big_square.scale(4)
        big_square.to_corner(UP+RIGHT)


        first_time = True
        for bend_point in self.bend_points:
            if first_time:
                self.play(ShowCreation(little_square))
                first_time = False
            else:
                self.remove(lines, big_square)                
                self.play(ApplyMethod(
                    little_square.shift,
                    bend_point - little_square.get_center()
                ))
            lines = self.lines_connecting_squares(little_square, big_square)
            self.play(
                ShowCreation(lines),
                ShowCreation(big_square)
            )
            self.dither(2)



    def lines_connecting_squares(self, square1, square2):
        return Mobject(*[
            Line(
                square1.get_corner(vect),
                square2.get_corner(vect),
            )
            for vect in [UP+LEFT, DOWN+LEFT]
        ]).highlight(square1.get_color())




        
class MultilayeredGlassZoomIn(Scene):
    def construct(self, layer_number):
        pass









