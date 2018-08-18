import numpy as np
import itertools as it
from copy import deepcopy
import sys

from constants import *

from scene.scene import Scene
from geometry import Polygon
from mobject.region import  region_from_polygon_vertices, region_from_line_boundary

A_COLOR = BLUE
B_COLOR = MAROON_D
C_COLOR = YELLOW

TEX_MOB_SCALE_FACTOR = 0.5
POINTS = np.array([
    DOWN,
    2*UP,
    DOWN+RIGHT,
    2*DOWN,
    2*DOWN+RIGHT,
    DOWN+3*LEFT,
    2*UP+3*LEFT,
    4*RIGHT,
    3*UP+3*RIGHT,
])

class Triangle(Polygon):
    def __init__(self, **kwargs):
        kwargs["color"] = C_COLOR
        Polygon.__init__(
            self, 
            *POINTS[[0, 1, 2]],
            edge_colors = [B_COLOR, C_COLOR, A_COLOR],
            **kwargs
        )
        nudge = 0.2
        target = POINTS[0]+nudge*(UP+RIGHT)
        for direction in UP, RIGHT:
            self.add_line(POINTS[0]+nudge*direction, target, color = WHITE)


    def add_all_letters(self):
        for char in "abc":
            self.add_letter(char)
        return self

    def add_letter(self, char, nudge = 0.3):
        mob = TexMobject(char).scale(TEX_MOB_SCALE_FACTOR)
        if char == "a":
            points = self.get_vertices()[[0, 2, 1]]
        elif char == "b":
            points = self.get_vertices()[[1, 0, 2]]
        elif char == "c":
            points = self.get_vertices()[[2, 1, 0]]
        center = 0.5*sum(points[:2]) #average of first two points
        mob.shift(center) 
        normal_dir = rotate_vector(points[1] - points[0], np.pi/2, OUT)
        if np.dot(normal_dir, points[2]-center) > 0:
            normal_dir = -normal_dir
        normal_dir /= get_norm(normal_dir)
        mob.shift(nudge*normal_dir)
        self.add(mob)
        return self

    def place_hypotenuse_on(self, point1, point2):
        #self.vertices[1], self.vertices[2]
        start1, start2 = self.get_vertices()[[1, 2]]
        target_vect = np.array(point2)-np.array(point1)
        curr_vect = start2-start1
        self.scale(get_norm(target_vect)/get_norm(curr_vect))
        self.rotate(angle_of_vector(target_vect)-angle_of_vector(curr_vect))
        self.shift(point1-self.get_vertices()[1])
        return self



def a_square(**kwargs):
    return Polygon(*POINTS[[0, 2, 4, 3]], color = A_COLOR, **kwargs)

def b_square(**kwargs):
    return Polygon(*POINTS[[1, 0, 5, 6]], color = B_COLOR, **kwargs)

def c_square(**kwargs):
    return Polygon(*POINTS[[1, 2, 7, 8]], color = C_COLOR, **kwargs)


class DrawPointsReference(Scene):
    def construct(self):
        for point, count in zip(POINTS, it.count()):
            mob = TexMobject(str(count)).scale(TEX_MOB_SCALE_FACTOR)
            mob.shift(POINTS[count])
            self.add(mob)

class DrawTriangle(Scene):
    def construct(self):
        self.add(Triangle().add_all_letters())

class DrawAllThreeSquares(Scene):
    def construct(self):
        a = a_square()
        b = b_square()
        c = c_square()
        self.add(Triangle(), a, b, c)
        for letter, mob in zip("abc", [a, b, c]):
            char_mob = TexMobject(letter+"^2").scale(TEX_MOB_SCALE_FACTOR)
            char_mob.shift(mob.get_center())
            self.add(char_mob)


class AddParallelLines(DrawAllThreeSquares):
    args_list = [
        (1, False),
        (2, False),
        (3, False),
        (3, True),
    ]
    @staticmethod
    def args_to_string(num, trim):
        return str(num) + ("Trimmed" if trim else "")

    def construct(self, num, trim):
        DrawAllThreeSquares.construct(self)
        shift_pairs = [
            (4*RIGHT, 3*UP),
            (ORIGIN, DOWN),
            (3*LEFT, 2*DOWN)
        ]
        for side_shift, vert_shift in shift_pairs[:num]:
            line1 = Line(BOTTOM, TOP, color = WHITE)
            line1.shift(side_shift)
            line2 = Line(LEFT_SIDE, RIGHT_SIDE, color = WHITE)
            line2.shift(vert_shift)
            self.add(line1, line2)
        if trim:
            for mob in self.mobjects:
                mob.filter_out(lambda p : p[0] > 4)
                mob.filter_out(lambda p : p[0] < -3)
                mob.filter_out(lambda p : p[1] > 3)
                mob.filter_out(lambda p : p[1] < -2)

class HighlightEmergentTriangles(AddParallelLines):
    args_list = [(3,True)]
    def construct(self, *args):
        AddParallelLines.construct(self, *args)
        triplets = [
            [(0, 2), (0, -1), (1, -1)],
            [(1, -1), (4, -1), (4, 0)],
            [(4, 0), (4, 3), (3, 3)],
            [(3, 3), (0, 3), (0, 2)],
        ]
        for triplet in triplets:
            self.set_color_region(
                region_from_polygon_vertices(*triplet),
                color = "DARK_BLUE"
            )

class IndicateTroublePointFromParallelLines(AddParallelLines):
    args_list = [(3,True)]
    def construct(self, *args):
        AddParallelLines.construct(self, *args)
        circle = Circle(radius = 0.25)
        circle.shift(DOWN+RIGHT)
        vect = DOWN+RIGHT
        arrow = Arrow(circle.get_center()+2*vect, circle.get_boundary_point(vect))
        arrow.set_color(circle.get_color())
        self.add_mobjects_among(list(locals().values()))


class DrawAllThreeSquaresWithMoreTriangles(DrawAllThreeSquares):
    args_list = [
        (1, True),
        (2, True),
        (3, True),
        (4, True),
        (5, True),
        (6, True),
        (7, True),
        (8, True),
        (9, True),
        (10, True),
        (10, False)
    ]
    @staticmethod
    def args_to_string(num, fill):
        fill_string = "" if fill else "HollowTriangles"
        return str(num) + fill_string

    def construct(self, num, fill):
        DrawAllThreeSquares.construct(self)
        pairs = [
            ((0, 2, 0), (1, -1, 0)),
            ((-3, -1, 0), (0, -2, 0)),
            ((4, -1, 0), (1, -2, 0)),
            ((0, -2, 0), (-3, -1, 0)),
            ((1, -2, 0), (4, -1, 0)),
            ((1, -1, 0), (4, 0, 0)),
            ((4, 0, 0), (3, 3, 0)),
            ((3, 3, 0), (0, 2, 0)),
            ((-3, 3, 0), (0, 2, 0)),
            ((0, 2, 0), (-3, 3, 0))
        ]
        to_flip = [1, 3, 8, 9]
        for n in range(num):
            triangle = Triangle()
            if n in to_flip:
                triangle.rotate(np.pi, UP)
            self.add(triangle.place_hypotenuse_on(*pairs[n]))
            vertices = list(triangle.get_vertices())
            if n not in to_flip:
                vertices.reverse()
            if fill:
                self.set_color_region(
                    region_from_polygon_vertices(*vertices),
                    color = DARK_BLUE
                )

class IndicateBigRectangleTroublePoint(DrawAllThreeSquaresWithMoreTriangles):
    args_list = [(10, False)]
    def construct(self, *args):
        DrawAllThreeSquaresWithMoreTriangles.construct(self, *args)
        circle = Circle(radius = 0.25, color = WHITE)
        circle.shift(4*RIGHT)
        vect = DOWN+RIGHT
        arrow = Arrow(circle.get_center()+vect, circle.get_boundary_point(vect))
        self.add_mobjects_among(list(locals().values()))

class ShowBigRectangleDimensions(DrawAllThreeSquaresWithMoreTriangles):
    args_list = [(10, False)]
    def construct(self, num, fill):
        DrawAllThreeSquaresWithMoreTriangles.construct(self, num, fill)
        u_brace = Underbrace((-3, -2, 0), (4, -2, 0))
        side_brace = Underbrace((-3, -3, 0), (2, -3, 0))
        for brace in u_brace, side_brace:
            brace.shift(0.2*DOWN)
        side_brace.rotate(-np.pi/2)
        a_plus_2b = TexMobject("a+2b").scale(TEX_MOB_SCALE_FACTOR)
        b_plus_2a = TexMobject("b+2a").scale(TEX_MOB_SCALE_FACTOR)
        a_plus_2b.next_to(u_brace, DOWN)
        b_plus_2a.next_to(side_brace, LEFT)
        self.add_mobjects_among(list(locals().values()))

class FillInAreaOfBigRectangle(DrawAllThreeSquaresWithMoreTriangles):
    args_list = [(10, False)]
    def construct(self, *args):
        DrawAllThreeSquaresWithMoreTriangles.construct(self, *args)
        args_list = [(10, False)]
        color = Color("yellow")
        color.set_rgb(0.3*np.array(color.get_rgb()))
        self.set_color_region(
            region_from_polygon_vertices(
                (-3, 3),
                (-3, -2),
                (4, -2),
                (4, 3)
            ),
            color = color
        )

class DrawOnlyABSquares(Scene):
    def construct(self):
        a = a_square()
        b = b_square()
        for char, mob in zip("ab", [a, b]):
            symobl = TexMobject(char+"^2").scale(TEX_MOB_SCALE_FACTOR)
            symobl.shift(mob.get_center())
            self.add(symobl)
        triangle = Triangle()
        self.add_mobjects_among(list(locals().values()))

class AddTriangleCopyToABSquares(DrawOnlyABSquares):
    def construct(self):
        DrawOnlyABSquares.construct(self)
        triangle = Triangle()
        triangle.rotate(np.pi, UP)
        triangle.place_hypotenuse_on(3*LEFT+DOWN, 2*DOWN)
        self.add(triangle)
        self.set_color_triangles()

    def set_color_triangles(self):
        for mob in self.mobjects:
            if isinstance(mob, Triangle):
                vertices = list(mob.get_vertices())
                for x in range(2):
                    self.set_color_region(region_from_polygon_vertices(
                        *vertices
                    ), color = DARK_BLUE)
                    vertices.reverse()#silly hack

class AddAllTrianglesToABSquares(AddTriangleCopyToABSquares):
    def construct(self):
        AddTriangleCopyToABSquares.construct(self)
        self.add(Triangle().place_hypotenuse_on(RIGHT+DOWN, 2*UP))
        triangle = Triangle()
        triangle.rotate(np.pi, UP)
        triangle.place_hypotenuse_on(2*DOWN, 3*LEFT+DOWN)
        self.add(triangle)
        self.set_color_triangles()



class DrawNakedCSqurae(Scene):
    def construct(self):
        c = c_square().center()
        triangle = Triangle().place_hypotenuse_on(*c.get_vertices()[[0,1]])
        triangle.add_all_letters()
        self.add(triangle, c)


class DrawCSquareWithAllTraingles(Scene):
    args_list = [
        (False, False, False, False),
        (False, True, False, True),
        (True, True, False, False),
        (False, True, True, False),
    ]
    @staticmethod
    def args_to_string(*toggle_vector):
        return "".join(map(str, list(map(int, toggle_vector))))

    def construct(self, *toggle_vector):
        if len(toggle_vector) == 0:
            toggle_vector = [False]*4
        self.c_square = c_square().center()
        vertices = it.cycle(self.c_square.get_vertices())
        last_vertex = next(vertices)
        have_letters = False
        self.triangles = []
        for vertex, should_flip in zip(vertices, toggle_vector):
            triangle = Triangle()
            pair = np.array([last_vertex, vertex])
            if should_flip:
                triangle.rotate(np.pi, UP)
                pair = pair[[1, 0]]
            triangle.place_hypotenuse_on(*pair)
            if not have_letters:
                triangle.add_all_letters()
                have_letters = True
            self.triangles.append(triangle)
            self.add(triangle)
            last_vertex = vertex            
        self.add(self.c_square)

class HighlightCSquareInBigSquare(DrawCSquareWithAllTraingles):
    args_list = [tuple([False]*4)]
    def construct(self, *args):
        DrawCSquareWithAllTraingles.construct(self, *args)
        self.set_color_region(region_from_polygon_vertices(
            *c_square().center().get_vertices()
        ), color = YELLOW)

class IndicateCSquareTroublePoint(DrawCSquareWithAllTraingles):
    def construct(self, *toggle_vector):
        DrawCSquareWithAllTraingles.construct(self, *toggle_vector)
        circle = Circle(color = WHITE)
        circle.scale(0.25)
        vertex = self.c_square.get_vertices()[1]
        circle.shift(vertex)
        vect = 2*RIGHT+DOWN
        arrow = Arrow(vertex+vect, circle.get_boundary_point(vect))
        self.add(circle, arrow)


class ZoomInOnTroublePoint(Scene):
    args_list = list(it.product([True, False], [True, False]))

    @staticmethod
    def args_to_string(with_labels, rotate):
        label_string = "WithLabels" if with_labels else "WithoutLabels"
        rotate_string = "Rotated" if rotate else ""
        return label_string + rotate_string

    def construct(self, with_labels, rotate):
        zoom_factor = 10
        density = zoom_factor*DEFAULT_POINT_DENSITY_1D
        c = c_square(density = density)
        c.shift(-c.get_vertices()[1])
        c.scale(zoom_factor)
        vertices = c.get_vertices()
        for index in 0, 1:
            triangle = Triangle(density = density)
            triangle.place_hypotenuse_on(vertices[index], vertices[index+1])
            self.add(triangle)
        circle = Circle(radius = 2.5, color = WHITE)
        angle1_arc = Circle(color = WHITE)
        angle2_arc = Circle(color = WHITE).scale(0.5)
        angle1_arc.filter_out(lambda x_y_z2 : not (x_y_z2[0] > 0 and x_y_z2[1] > 0 and x_y_z2[1] < x_y_z2[0]/3))
        angle2_arc.filter_out(lambda x_y_z3 : not (x_y_z3[0] < 0 and x_y_z3[1] > 0 and x_y_z3[1] < -3*x_y_z3[0]))

        self.add_mobjects_among(list(locals().values()))
        self.add_elbow()        
        if rotate:
            for mob in self.mobjects:
                mob.rotate(np.pi/2)
        if with_labels:
            alpha = TexMobject("\\alpha").scale(TEX_MOB_SCALE_FACTOR)
            beta = TexMobject("90-\\alpha").scale(TEX_MOB_SCALE_FACTOR)
            if rotate:
                alpha.next_to(angle1_arc, UP+0.1*LEFT)
                beta.next_to(angle2_arc, DOWN+0.5*LEFT)
            else:
                alpha.next_to(angle1_arc, RIGHT)
                beta.next_to(angle2_arc, LEFT)
            self.add(alpha, beta)



    def add_elbow(self):
        c = 0.1
        p1 = c*LEFT + 3*c*UP
        p2 = 3*c*RIGHT + c*UP
        p3 = 2*c*RIGHT + 4*c*UP
        self.add(Line(p1, p3, color = WHITE))
        self.add(Line(p2, p3, color = WHITE))


class DrawTriangleWithAngles(Scene):
    def construct(self):
        triangle = Triangle(density = 2*DEFAULT_POINT_DENSITY_1D)
        triangle.scale(2).center().add_all_letters()
        vertices = triangle.get_vertices()
        kwargs = {"color" : WHITE}
        angle1_arc = Circle(radius = 0.4, **kwargs).filter_out(
            lambda x_y_z : not(x_y_z[0] > 0 and x_y_z[1] < 0 and x_y_z[1] < -3*x_y_z[0])
        ).shift(vertices[1])
        angle2_arc = Circle(radius = 0.2, **kwargs).filter_out(
            lambda x_y_z1 : not(x_y_z1[0] < 0 and x_y_z1[1] > 0 and x_y_z1[1] < -3*x_y_z1[0])
        ).shift(vertices[2])
        alpha = TexMobject("\\alpha")
        beta = TexMobject("90-\\alpha")
        alpha.shift(vertices[1]+3*RIGHT+DOWN)
        beta.shift(vertices[2]+3*RIGHT+UP)
        arrow1 = Arrow(alpha, angle1_arc)
        arrow2 = Arrow(beta, angle2_arc)

        self.add(triangle, angle1_arc, angle2_arc, alpha, beta, arrow1, arrow2)


class LabelLargeSquare(DrawCSquareWithAllTraingles):
    args_list = []
    def construct(self):
        DrawCSquareWithAllTraingles.construct(self)
        everything = Mobject(*self.mobjects)
        u_brace = Underbrace(2*(DOWN+LEFT), 2*(DOWN+RIGHT))
        u_brace.shift(0.2*DOWN)
        side_brace = deepcopy(u_brace).rotate(np.pi/2)
        upper_brace = deepcopy(u_brace).rotate(np.pi)
        a_plus_b = TexMobject("a+b").scale(TEX_MOB_SCALE_FACTOR)
        upper_brace.add(a_plus_b.next_to(upper_brace, UP))
        side_brace.add(a_plus_b.next_to(side_brace, RIGHT))
        self.add(upper_brace, side_brace)

class CompletelyFillLargeSquare(LabelLargeSquare):
    def construct(self):
        LabelLargeSquare.construct(self)
        vertices = [2*(DOWN+LEFT), 2*(DOWN+RIGHT), 2*(UP+RIGHT), 2*(UP+LEFT)]
        vertices.append(vertices[0])
        pairs = list(zip(vertices, vertices[1:]))
        self.set_color_region(region_from_line_boundary(*pairs), color = BLUE)


class FillComponentsOfLargeSquare(LabelLargeSquare):
    def construct(self):
        LabelLargeSquare.construct(self)
        points = np.array([
            2*UP+2*LEFT,
            UP+2*LEFT,
            2*DOWN+2*LEFT,
            2*DOWN+LEFT,
            2*DOWN+2*RIGHT,
            DOWN+2*RIGHT,
            2*UP+2*RIGHT,
            RIGHT+2*UP
        ])
        for triplet in [[0, 1, 7], [2, 3, 1], [4, 5, 3], [6, 7, 5]]:
            triplet.append(triplet[0])
            self.set_color_region(region_from_line_boundary(*[
                [points[i], points[j]]
                for i, j in zip(triplet, triplet[1:])
            ]), color = DARK_BLUE)
        vertices = points[[1, 3, 5, 7, 1]]
        self.set_color_region(region_from_line_boundary(*[
            [p1, p2]
            for p1, p2 in zip(vertices, vertices[1:])
        ]), color = YELLOW)

class ShowRearrangementInBigSquare(DrawCSquareWithAllTraingles):
    args_list = []
    def construct(self):
        self.add(Square(side_length = 4, color = WHITE))        
        DrawCSquareWithAllTraingles.construct(self)
        self.remove(self.c_square)
        self.triangles[1].shift(LEFT)
        for i, j in [(0, 2), (3, 1)]:
            self.triangles[i].place_hypotenuse_on(
                *self.triangles[j].get_vertices()[[2, 1]]
            )


class ShowRearrangementInBigSquareWithRegions(ShowRearrangementInBigSquare):
    def construct(self):
        ShowRearrangementInBigSquare.construct(self)
        self.set_color_region(region_from_polygon_vertices(
            2*(LEFT+UP), 2*LEFT+DOWN, RIGHT+DOWN, RIGHT+2*UP
        ), color = B_COLOR)
        self.set_color_region(region_from_polygon_vertices(
            RIGHT+DOWN, RIGHT+2*DOWN, 2*RIGHT+2*DOWN, 2*RIGHT+DOWN
        ), color = A_COLOR)
