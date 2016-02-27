import numpy as np
import itertools as it

from helpers import *

from mobject.tex_mobject import TexMobject, TextMobject, Brace
from mobject import Mobject
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

RANDY_SCALE_VAL = 0.3



class Cycloid(ParametricFunction):
    DEFAULT_CONFIG = {
        "point_a"       : 6*LEFT+3*UP,
        "radius"        : 2,
        "end_theta"     : 3*np.pi/2,
        "density"       : 5*DEFAULT_POINT_DENSITY_1D,
        "color"         : BLUE_D
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
    DEFAULT_CONFIG = {
        "color" : YELLOW_D,
        "density" : 20*DEFAULT_POINT_DENSITY_1D
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        pre_func = lambda t : [
            t**3 - 1.5*t,
            t**2 + 0.6*(t**2 - 4)*(t**2 - 1),
            0
        ]
        ParametricFunction.__init__(
            self,
            lambda t : pre_func(4*t-2),
            **kwargs
        )


class SlideWordDownCycloid(Animation):
    DEFAULT_CONFIG = { 
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

    def update_mobject(self, alpha):
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
                letter.rgbs = brightness*np.ones(letter.rgbs.shape)
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
        anim.path.gradient_highlight(WHITE, BLUE_E)
        self.play(ShowCreation(anim.path))
        self.play(anim)
        self.dither()
        self.play(
            FadeOut(anim.path),
            ApplyMethod(anim.mobject.center)
        )



class PathSlidingScene(Scene):
    DEFAULT_CONFIG = {
        "gravity" : 3,
        "delta_t" : 0.05
    }
    def slide(self, mobject, path, roll = False):
        points = path.points
        time_slices = self.get_time_slices(points)
        curr_t = 0
        last_index = 0
        curr_index = 1
        self.t_equals = TexMobject("t = ")
        self.t_equals.shift(3.5*UP+4*RIGHT)
        self.add(self.t_equals)
        while curr_index < len(points):
            self.slider = mobject.copy()
            self.adjust_mobject_to_index(
                self.slider, curr_index, points
            )
            if roll:
                distance = np.linalg.norm(
                    points[curr_index] - points[last_index]
                )
                self.roll(mobject, distance)
            self.add(self.slider)
            self.write_time(curr_t)
            self.dither(self.frame_duration)
            self.remove(self.slider)
            curr_t += self.delta_t
            last_index = curr_index
            while time_slices[curr_index] < curr_t:
                curr_index += 1
                if curr_index == len(points):
                    break
        self.add(self.slider)
        self.dither()

    def get_time_slices(self, points):
        dt_list = np.zeros(len(points))
        ds_list = np.apply_along_axis(
            np.linalg.norm,
            1,
            points[1:]-points[:-1]
        )
        delta_y_list = np.abs(points[0, 1] - points[1:,1])
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
        return mobject

    def write_time(self, time):
        if hasattr(self, "time_mob"):
            self.remove(self.time_mob)
        digits = map(TexMobject, "%.2f"%time)
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
        randy.scale(RANDY_SCALE_VAL)
        paths = self.get_paths()
        point_a = Dot(paths[0].points[0])
        point_b = Dot(paths[0].points[-1])
        A = TexMobject("A").next_to(point_a, LEFT)
        B = TexMobject("B").next_to(point_b, RIGHT)
        for point, tex in [(point_a, A), (point_b, B)]:
            self.play(ShowCreation(point))
            self.play(ShimmerIn(tex))
            self.dither()
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
            self.dither()
            self.remove(self.slider)
            self.slide(randy, curr_path)
        self.clear()
        self.add(point_a, point_b, A, B, curr_path)
        text = TextMobject("Which path is fastest?")
        text.to_edge(UP)
        self.play(ShimmerIn(text))
        for path in paths:
            self.play(Transform(
                curr_path, path,
                path_func = path_along_arc(np.pi/2),
                run_time = 3
            ))

    def get_paths(self):
        sharp_corner = Mobject(
            Line(3*UP+LEFT, LEFT),
            Arc(angle = np.pi/2, start_angle = np.pi),
            Line(DOWN, DOWN+3*RIGHT)
        ).ingest_sub_mobjects().highlight(GREEN)
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
        end = target_path.point[-1]
        for path in paths:
            path.position_endpoints_on(start, end)


class RollingRandolph(PathSlidingScene):
    def construct(self):
        randy = Randolph()
        randy.scale(RANDY_SCALE_VAL)
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
        path.gradient_highlight(RED_D, WHITE)
        radius = Line(ORIGIN, path.points[0])
        randy = Randolph()
        randy.scale(RANDY_SCALE_VAL)
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
                path.position_endpoints_on, start, end,
                path_func = path_along_arc(-angle)
            ),
            run_time = 3
        )
        self.adjust_mobject_to_index(randy_copy, 1, path.points)
        self.play(FadeIn(randy_copy))
        self.remove(randy_copy)
        self.slide(randy, path)
        self.play(ShimmerIn(words))
        self.dither()







