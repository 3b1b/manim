from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from animation.continual_animation import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from topics.objects import *
from topics.probability import *
from topics.complex_numbers import *
from scene import Scene
from scene.reconfigurable_scene import ReconfigurableScene
from scene.zoomed_scene import *
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *
from topics.graph_scene import *

class EquationSolver1d(GraphScene, ZoomedScene, ReconfigurableScene):
    CONFIG = {
    "graph_func" : lambda x : x,
    "targetX" : 0,
    "targetY" : 0,
    "initial_lower_x" : 0,
    "initial_upper_x" : 10,
    "num_iterations" : 10,
    "iteration_at_which_to_start_zoom" : None,
    "graph_label" : None,
    "show_target_line" : True
    }

    def drawGraph(self):
        self.setup_axes()
        self.graph = self.get_graph(self.graph_func)
        self.add(self.graph)

        if self.graph_label != None:
            self.add(self.get_graph_label(self.graph, self.graph_label, 
                x_val = 4, direction = RIGHT))
        
        if self.show_target_line:
            target_line_object = DashedLine(
                self.coords_to_point(self.x_min, self.targetY), 
                self.coords_to_point(self.x_max, self.targetY),
                dashed_segment_length = 0.1)
            self.add(target_line_object)

            target_line_label = TexMobject("y = " + str(self.targetY))
            target_line_label.next_to(target_line_object.get_left(), UP + RIGHT)
            self.add(target_line_label)

    def solveEquation(self):
        leftBrace, rightBrace = xBraces = TexMobject("||")
        xBraces.stretch(2, 0)

        downBrace, upBrace = yBraces = TexMobject("||")
        yBraces.stretch(2, 0)
        yBraces.rotate(np.pi/2)

        lowerX = self.initial_lower_x
        lowerY = self.graph_func(lowerX)
        upperX = self.initial_upper_x
        upperY = self.graph_func(upperX)

        leftBrace.move_to(self.coords_to_point(lowerX, 0))
        leftBraceLabel = DecimalNumber(lowerX)
        leftBraceLabel.next_to(leftBrace, DOWN + LEFT, buff = SMALL_BUFF)
        leftBraceLabelAnimation = ContinualChangingDecimal(leftBraceLabel, 
            lambda alpha : self.point_to_coords(leftBrace.get_center())[0],
            tracked_mobject = leftBrace)
        self.add(leftBraceLabelAnimation)
        
        rightBrace.move_to(self.coords_to_point(upperX, 0))
        rightBraceLabel = DecimalNumber(upperX)
        rightBraceLabel.next_to(rightBrace, DOWN + RIGHT, buff = SMALL_BUFF)
        rightBraceLabelAnimation = ContinualChangingDecimal(rightBraceLabel, 
            lambda alpha : self.point_to_coords(rightBrace.get_center())[0],
            tracked_mobject = rightBrace)
        self.add(rightBraceLabelAnimation)

        downBrace.move_to(self.coords_to_point(0, lowerY))
        downBraceLabel = DecimalNumber(lowerY)
        downBraceLabel.next_to(downBrace, LEFT + DOWN, buff = SMALL_BUFF)
        downBraceLabelAnimation = ContinualChangingDecimal(downBraceLabel, 
            lambda alpha : self.point_to_coords(downBrace.get_center())[1],
            tracked_mobject = downBrace)
        self.add(downBraceLabelAnimation)
        
        upBrace.move_to(self.coords_to_point(0, upperY))
        upBraceLabel = DecimalNumber(upperY)
        upBraceLabel.next_to(upBrace, LEFT + UP, buff = SMALL_BUFF)
        upBraceLabelAnimation = ContinualChangingDecimal(upBraceLabel, 
            lambda alpha : self.point_to_coords(upBrace.get_center())[1],
            tracked_mobject = upBrace)
        self.add(upBraceLabelAnimation)

        lowerDotPoint = self.input_to_graph_point(lowerX, self.graph)
        lowerDotXPoint = self.coords_to_point(lowerX, 0)
        lowerDotYPoint = self.coords_to_point(0, self.graph_func(lowerX))
        lowerDot = Dot(lowerDotPoint)
        upperDotPoint = self.input_to_graph_point(upperX, self.graph)
        upperDot = Dot(upperDotPoint)
        upperDotXPoint = self.coords_to_point(upperX, 0)
        upperDotYPoint = self.coords_to_point(0, self.graph_func(upperX))

        lowerXLine = Line(lowerDotXPoint, lowerDotPoint, stroke_width = 1, color = YELLOW)
        upperXLine = Line(upperDotXPoint, upperDotPoint, stroke_width = 1, color = YELLOW)
        lowerYLine = Line(lowerDotYPoint, lowerDotPoint, stroke_width = 1, color = YELLOW)
        upperYLine = Line(upperDotYPoint, upperDotPoint, stroke_width = 1, color = YELLOW)
        self.add(lowerXLine, upperXLine, lowerYLine, upperYLine)

        self.add(xBraces, yBraces, lowerDot, upperDot)

        for i in range(self.num_iterations):
            if i == self.iteration_at_which_to_start_zoom:
                self.activate_zooming()
                self.little_rectangle.move_to(
                    self.coords_to_point(self.targetX, self.targetY))
                inverseZoomFactor = 1/float(self.zoom_factor)
                self.play(
                    lowerDot.scale_in_place, inverseZoomFactor,
                    upperDot.scale_in_place, inverseZoomFactor)


            def makeUpdater(xAtStart):
                def updater(group, alpha):
                    dot, xBrace, yBrace, xLine, yLine = group
                    newX = interpolate(xAtStart, midX, alpha)
                    newY = self.graph_func(newX)
                    graphPoint = self.input_to_graph_point(newX, 
                            self.graph)
                    dot.move_to(graphPoint)
                    xAxisPoint = self.coords_to_point(newX, 0)
                    xBrace.move_to(xAxisPoint)
                    yAxisPoint = self.coords_to_point(0, newY)
                    yBrace.move_to(yAxisPoint)
                    xLine.put_start_and_end_on(xAxisPoint, graphPoint)
                    yLine.put_start_and_end_on(yAxisPoint, graphPoint)
                    return group
                return updater

            midX = (lowerX + upperX)/float(2)
            midY = self.graph_func(midX)

            midCoords = self.coords_to_point(midX, midY)
            midColor = RED
            midXPoint = Dot(self.coords_to_point(midX, 0), color = midColor)
            self.play(
                ReplacementTransform(leftBrace.copy(), midXPoint),
                ReplacementTransform(rightBrace.copy(), midXPoint))
            midXLine = Line(self.coords_to_point(midX, 0), midCoords, color = midColor)
            self.play(ShowCreation(midXLine))
            midDot = Dot(midCoords, color = midColor)
            if(self.iteration_at_which_to_start_zoom != None and 
                i >= self.iteration_at_which_to_start_zoom):
                midDot.scale_in_place(inverseZoomFactor)
            self.add(midDot)
            midYLine = Line(midCoords, self.coords_to_point(0, midY), color = midColor)
            self.play(ShowCreation(midYLine))

            if midY < self.targetY:
                movingGroup = Group(lowerDot, 
                    leftBrace, downBrace,
                    lowerXLine, lowerYLine)
                self.play(
                    UpdateFromAlphaFunc(movingGroup, makeUpdater(lowerX)))
                lowerX = midX
                lowerY = midY

            else:
                movingGroup = Group(upperDot, 
                    rightBrace, upBrace,
                    upperXLine, upperYLine)
                self.play(
                    UpdateFromAlphaFunc(movingGroup, makeUpdater(upperX)))
                upperX = midX
                upperY = midY
            self.remove(midXLine, midDot, midYLine)

        self.dither()

    def construct(self):
        self.drawGraph()
        self.solveEquation()

class FirstSqrtScene(EquationSolver1d):
    CONFIG = {
    "x_min" : 0,
    "x_max" : 2,
    "y_min" : 0,
    "y_max" : 4,
    "graph_origin" : 2*DOWN + 5 * LEFT,
    "x_axis_width" : 12,
    "zoom_factor" : 3,
    "zoomed_canvas_center" : 2.25 * UP + 1.75 * LEFT,
    "graph_func" : lambda x : x**2,
    "targetX" : np.sqrt(2),
    "targetY" : 2,
    "initial_lower_x" : 1,
    "initial_upper_x" : 2,
    "num_iterations" : 2,
    "iteration_at_which_to_start_zoom" : 1,
    "graph_label" : "y = x^2",
    "show_target_line" : True,
    }

class SecondSqrtScene(FirstSqrtScene, ReconfigurableScene):

    def setup(self):
        FirstSqrtScene.setup(self)
        ReconfigurableScene.setup(self)

    def construct(self):
        shiftVal = self.targetY

        self.drawGraph()
        newOrigin = self.coords_to_point(0, shiftVal)
        self.transition_to_alt_config(
            graph_func = lambda x : x**2 - shiftVal,
            targetY = 0,
            graph_label = "y = x^2 - " + str(shiftVal),
            y_min = self.y_min - shiftVal,
            y_max = self.y_max - shiftVal,
            show_target_line = False,
            graph_origin = newOrigin)
        self.solveEquation()

class LoopSplitScene(Scene):
    def construct(self):
        # Original loop
        tl = UP + LEFT
        tm = UP
        tr = UP + RIGHT
        mr = RIGHT
        br = DOWN + RIGHT
        bm = DOWN
        bl = DOWN + LEFT
        lm = LEFT

        loop_color = BLUE

        top_line = Line(tl, tr, color = loop_color)
        right_line = Line(tr, br, color = loop_color)
        bottom_line = Line(br, bl, color = loop_color)
        left_line = Line(bl, tl, color = loop_color)
        loop = Group(top_line, right_line, bottom_line, left_line)
        self.add(loop)
        
        # TODO: Make the following a continual animation, and on all split loops do the same
        bullet = TexMobject("*", fill_color = RED)
        bullet.move_to(tl)
        self.add(bullet)
        list_of_args = reduce(op.add, 
            [
                [ApplyMethod, bullet.move_to, point, {"rate_func" : None}] for 
                point in [tr, br, bl, tl]
            ]
            )
        succ_anim = Succession(*list_of_args)
        self.add(CycleAnimation(succ_anim))

        # Splits in middle
        split_line = DashedLine(interpolate(tl, tr, 0.5), interpolate(bl, br, 0.5))
        self.play(ShowCreation(split_line))

        self.remove(split_line)
        mid_line_left = Line(tm, bm, color = loop_color)
        mid_line_right = Line(tm, bm, color = loop_color)
        self.add(mid_line_left, mid_line_right)

        top_line_left_half = Line(tl, tm, color = loop_color)
        top_line_right_half = Line(tm, tr, color = loop_color)

        bottom_line_left_half = Line(bl, bm, color = loop_color)
        bottom_line_right_half = Line(bm, br, color = loop_color)

        self.remove(top_line)
        self.add(top_line_left_half)
        self.add(top_line_right_half)
        self.remove(bottom_line)
        self.add(bottom_line_left_half)
        self.add(bottom_line_right_half)

        left_open_loop = VGroup(top_line_left_half, left_line, bottom_line_left_half)
        left_closed_loop = VGroup(left_open_loop, mid_line_left)
        right_open_loop = VGroup(top_line_right_half, right_line, bottom_line_right_half)
        right_closed_loop = VGroup(right_open_loop, mid_line_right)

        self.play(
            ApplyMethod(left_closed_loop.shift, LEFT), 
            ApplyMethod(right_closed_loop.shift, RIGHT)
            )

        self.dither()

        self.play(
            ApplyMethod(left_open_loop.shift, LEFT), 
            ApplyMethod(right_open_loop.shift, RIGHT)
            )

        self.dither()

        mid_lines = VGroup(mid_line_left, mid_line_right)

        circle = Circle()
        circle.surround(mid_lines)
        self.play(ShowCreation(circle))

class EquationSolver2d(ZoomedScene):
    #TODO
    CONFIG = {}