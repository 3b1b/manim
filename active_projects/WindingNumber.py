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

class Test(Scene):
    def construct(self):
        firstname = TextMobject("Sridhar")
        lastname = TextMobject("Ramesh")
        texObject1 = TexMobject(r"\sum_{x = 0}^{n} \frac{1}{x^2}")
        texObject2 = TexMobject(r"\int_{x = 0}^{n} \frac{1}{x^2}")
        squareObject = Square(side_length = 2)
        squareGroup = Group(*[Square(side_length = x) for x in range(3)])
        squareGroup.arrange_submobjects(RIGHT)
        #self.play(ReplacementTransform(texObject1, texObject2), run_time = 5)
        #self.play(texObject2.shift, 2*RIGHT)
        #self.play(Write(firstname))
        #self.play(Write(squareGroup))
        polygonObject = Polygon(ORIGIN, UP + RIGHT, UP + LEFT)
        polygonObject.set_stroke(color = YELLOW, width = 3)
        polygonObject.set_fill(color = WHITE, opacity = 0.5)
        self.play(DrawBorderThenFill(polygonObject), run_time = 5)

class GraphTest(GraphScene, ZoomedScene):
    CONFIG = {
    "x_min" : 0,
    "x_max" : 6,
    "y_min" : -1,
    "y_max" : 20,
    "graph_origin" : 2*DOWN + 5 * LEFT,
    "x_axis_width" : 12,
    "zoom_factor" : 3,
    "zoomed_canvas_center" : 2 * UP + 1.5 * LEFT
    }
    def construct(self):
        
        # Convenient for skipping animations:
        # self.force_skipping()
        # self.revert_to_original_skipping_status()

        self.setup_axes()
        graphFunc = lambda x : x**2
        graph = self.get_graph(graphFunc)
        self.add(graph)

        inverseZoomFactor = 1/float(self.zoom_factor)

        graphLabel = self.get_graph_label(graph, "y = x^2", 
            x_val = 4, direction = RIGHT)
        self.add(graphLabel)

        targetY = 6
        
        targetYLine = DashedLine(
            self.coords_to_point(self.x_min, targetY), 
            self.coords_to_point(self.x_max, targetY),
            dashed_segment_length = 0.1)
        self.add(targetYLine)

        targetYLineLabel = TexMobject("y = " + str(targetY))
        targetYLineLabel.next_to(targetYLine.get_left(), UP + RIGHT)
        self.add(targetYLineLabel)

        leftBrace, rightBrace = xBraces = TexMobject("||")
        xBraces.stretch(2, 0)

        downBrace, upBrace = yBraces = TexMobject("||")
        yBraces.stretch(2, 0)
        yBraces.rotate(np.pi/2)

        lowerX = 1
        lowerY = graphFunc(lowerX)
        upperX = 5
        upperY = graphFunc(upperX)

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

        lowerDotPoint = self.input_to_graph_point(lowerX, graph)
        lowerDotXPoint = self.coords_to_point(lowerX, 0)
        lowerDotYPoint = self.coords_to_point(0, graphFunc(lowerX))
        lowerDot = Dot(lowerDotPoint)
        upperDotPoint = self.input_to_graph_point(upperX, graph)
        upperDot = Dot(upperDotPoint)
        upperDotXPoint = self.coords_to_point(upperX, 0)
        upperDotYPoint = self.coords_to_point(0, graphFunc(upperX))

        lowerXLine = Line(lowerDotXPoint, lowerDotPoint, stroke_width = 1, color = YELLOW)
        upperXLine = Line(upperDotXPoint, upperDotPoint, stroke_width = 1, color = YELLOW)
        lowerYLine = Line(lowerDotYPoint, lowerDotPoint, stroke_width = 1, color = YELLOW)
        upperYLine = Line(upperDotYPoint, upperDotPoint, stroke_width = 1, color = YELLOW)
        self.add(lowerXLine, upperXLine, lowerYLine, upperYLine)

        # TODO: Display lines at start, not just on update

        self.add(xBraces, yBraces, lowerDot, upperDot)

        zoomStage = 5
        for i in range(10):
            if i == zoomStage:
                self.activate_zooming()
                self.little_rectangle.move_to(
                    self.coords_to_point(np.sqrt(targetY), targetY))
                self.play(
                    lowerDot.scale_in_place, inverseZoomFactor,
                    upperDot.scale_in_place, inverseZoomFactor)


            def makeUpdater(xAtStart):
                def updater(group, alpha):
                    dot, xBrace, yBrace, xLine, yLine = group
                    newX = interpolate(xAtStart, midX, alpha)
                    newY = graphFunc(newX)
                    graphPoint = self.input_to_graph_point(newX, 
                            graph)
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
            midY = graphFunc(midX)

            midCoords = self.coords_to_point(midX, midY)
            midColor = RED
            midXPoint = Dot(self.coords_to_point(midX, 0), color = midColor)
            self.play(
                ReplacementTransform(leftBrace.copy(), midXPoint),
                ReplacementTransform(rightBrace.copy(), midXPoint))
            midXLine = Line(self.coords_to_point(midX, 0), midCoords, color = midColor)
            self.play(ShowCreation(midXLine))
            midDot = Dot(midCoords, color = midColor)
            if(i >= zoomStage):
                midDot.scale_in_place(inverseZoomFactor)
            self.add(midDot)
            midYLine = Line(midCoords, self.coords_to_point(0, midY), color = midColor)
            self.play(ShowCreation(midYLine))

            if midY < targetY:
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
