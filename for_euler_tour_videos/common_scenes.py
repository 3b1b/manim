from __future__ import absolute_import
from animation.creation import ShowCreation
from animation.update import UpdateFromAlphaFunc
from animation.composition import Succession
from animation.composition import AnimationGroup
from animation.transform import ApplyMethod
from constants import *
from continual_animation.update import ContinualUpdateFromTimeFunc
from utils.rate_functions import linear
from mobject.geometry import Circle
from mobject.geometry import Line
from mobject.mobject import Group
from scene.scene import Scene
from utils.space_ops import rotation_matrix
import itertools
import operator
import random
import time

def euler_tour(G, start_point):
    ret = [start_point]
    unvisited = set(G.submobjects)
    random.seed(time.time())
    while unvisited:
        next_edge_candidates = [
            line for line in unvisited
            if np.allclose(line.get_start(), ret[-1])
            or np.allclose(line.get_end(), ret[-1])
        ]
        if next_edge_candidates:
            next_edge = random.choice(next_edge_candidates)
            unvisited.remove(next_edge)
            ret.append(
                next_edge.get_start()
                if np.allclose(next_edge.get_end(), ret[-1])
                else next_edge.get_end()
            )
        else:
            subgraph = Group()
            for edge in unvisited:
                subgraph.add(edge)
            start_point = None
            splice_index = None
            for start_index, point in enumerate(ret):
                for edge in unvisited:
                    if np.allclose(edge.get_start(), point) or \
                            np.allclose(edge.get_end(), point):
                        start_point = point
                        splice_index = start_index
            assert(start_point is not None)
            splice = euler_tour(subgraph, start_point)
            to_remove = set()
            for i in range(len(splice) - 1):
                for edge in unvisited:
                    u,v = edge.get_start_and_end()
                    if np.allclose(u, splice[i]) and np.allclose(v, splice[i+1]) or \
                            np.allclose(u, splice[i+1]) and np.allclose(v, splice[i]):
                        to_remove.add(edge)
            for x in to_remove:
                unvisited.remove(x)
            ret = ret[:splice_index] + splice + ret[splice_index+1:]
            return ret
    return ret


class OpeningScene(Scene):
    def rotate_shape(self):
        def make_cube():
            points = [p for p in itertools.product([0, 1], repeat=3)]
            lines = [
                (p1, p2)
                for (p1, p2) in itertools.product(points, points)
                if sum(map(operator.xor, p1, p2)) == 1
                and p1 < p2
            ]
            mobs = [Line(p1, p2, stroke_width=4) for (p1, p2) in lines]
            return Group(*mobs)

        def rotate_mob(mob, theta, axis=Y_AXIS):
            mob.rotate_about_origin(theta, axis=axis)

        outer_cube = make_cube()
        inner_cube = make_cube().scale(1./3)
        hypercube = Group(*outer_cube.submobjects + inner_cube.submobjects)
        seen_edges = set()
        for inner_edge, outer_edge in \
                zip(inner_cube.submobjects, outer_cube.submobjects):
            inner_start_and_end = list(map(tuple, inner_edge.get_start_and_end()))
            outer_start_and_end = list(map(tuple, outer_edge.get_start_and_end()))

            start_pair = (inner_start_and_end[0], outer_start_and_end[0])
            if start_pair not in seen_edges:
                seen_edges.add(start_pair)
                starting_connecting_line = \
                        Line(start_pair[0], start_pair[1], stroke_width=4)
                hypercube.add(starting_connecting_line)

            end_pair = (inner_start_and_end[1], outer_start_and_end[1])
            if end_pair not in seen_edges:
                seen_edges.add(end_pair)
                ending_connecting_line = \
                        Line(end_pair[0], end_pair[1], stroke_width=4)
                hypercube.add(ending_connecting_line)
        #hypercube = Group()
        #hypercube.add(
        #    Line(np.array([1, 1, 0]), np.array([1, -1, 0])),
        #    Line(np.array([-1, 1, 0]), np.array([1, 1, 0])),
        #    Line(np.array([-1, -1, 0]), np.array([-1, 1, 0])),
        #    Line(np.array([-1, -1, 0]), np.array([1, -1, 0])),
        #)

        hypercube.scale(3)
        hypercube.rotate(-PI / 4, Y_AXIS)
        hypercube.rotate(-np.arctan(np.sqrt(2)), X_AXIS)
        hypercube.move_to(ORIGIN)
        self.add(hypercube)
        self.wait(0.1)
        self.add(ContinualUpdateFromTimeFunc(
            hypercube,
            rotate_mob,
            start_up_time=0,
            wind_down_time=1.0,
            end_time=14./12 * PI + 0.005,
        ))

        point = Circle(
            radius=0.1,
            fill_opacity=1,
            color="#FF0022"
        ).move_to(ORIGIN)
        self.bring_to_back(point)

        def move_along_line(i, start_point=None):
            def place_along_line_from_start(mob, t):
                line = hypercube.submobjects[i]
                vec = line.get_vector()
                mob.move_to(line.get_start() + vec * t)
            def place_along_line_from_end(mob, t):
                line = hypercube.submobjects[i]
                vec = -1 * line.get_vector()
                mob.move_to(line.get_end() + vec * t)

            line = hypercube.submobjects[i]
            if start_point is None:
                start_point = line.get_start()
            if np.allclose(start_point, line.get_start()):
                return place_along_line_from_start
            elif np.allclose(start_point, line.get_end()):
                return place_along_line_from_end

        path_points = euler_tour(
            hypercube,
            hypercube.submobjects[10].get_end()
        )
        print(path_points)
        cur_path_index = 1
        path_edge_indices = []
        while cur_path_index < len(path_points):
            prev_point = path_points[cur_path_index - 1]
            next_point = path_points[cur_path_index]
            for i, edge in enumerate(hypercube.submobjects):
                start, end = edge.get_start_and_end()
                if np.allclose(start, prev_point) and \
                   np.allclose(end, next_point) or \
                   np.allclose(end, prev_point) and \
                   np.allclose(start, next_point):
                    path_edge_indices.append(i)
                    cur_path_index += 1
        successions = []
        for point_index, edge_index in enumerate(path_edge_indices):
            point_anim = UpdateFromAlphaFunc(
                point,
                move_along_line(
                    edge_index,
                    start_point=path_points[point_index]
                ),
                rate_func=linear
            )
            color_anim = ApplyMethod(
                hypercube.submobjects[edge_index].set_color,
                RED,
            )
            successions.append(
                AnimationGroup(point_anim, color_anim, run_time=0.1094)
            )

        ## this works. now.
        #self.play(ApplyMethod(hypercube.submobjects[0].set_color, RED))
        #self.play(ApplyMethod(hypercube.submobjects[1].set_color, RED))
        #self.play(ApplyMethod(hypercube.submobjects[2].set_color, RED))
        #self.play(ApplyMethod(hypercube.submobjects[3].set_color, RED))

        self.play(Succession(*successions, add_finished_mobjects=False))
        self.wait(10)

    def construct(self):
        self.rotate_shape()
