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

class DualScene(Scene):
    CONFIG = {
    "num_needed_anchor_points" : 10
    }

    def setup(self):
        split_line = DashedLine(SPACE_HEIGHT * UP, SPACE_HEIGHT * DOWN)
        self.num_plane = NumberPlane(x_radius = SPACE_WIDTH/2)
        self.num_plane.to_edge(LEFT, buff = 0)
        self.num_plane.prepare_for_nonlinear_transform()
        self.add(self.num_plane, split_line)

    def apply_function(self, func, run_time = 3):
        self.func = func
        right_plane = self.num_plane.copy()
        right_plane.center()
        right_plane.prepare_for_nonlinear_transform()
        right_plane.apply_function(func)
        right_plane.shift(SPACE_WIDTH/2 * RIGHT)
        self.right_plane = right_plane
        crappy_cropper = FullScreenFadeRectangle(fill_opacity = 1)
        crappy_cropper.stretch_to_fit_width(SPACE_WIDTH)
        crappy_cropper.to_edge(LEFT, buff = 0)
        self.play(
            ReplacementTransform(self.num_plane.copy(), right_plane),
            FadeIn(crappy_cropper), 
            Animation(self.num_plane),
            run_time = run_time
        )

    def squash_onto_left(self, object):
        object.shift(SPACE_WIDTH/2 * LEFT)

    def squash_onto_right(self, object):
        object.shift(SPACE_WIDTH/2 * RIGHT)

    def path_draw(self, input_object, run_time = 3):
        output_object = input_object.copy()
        if input_object.get_num_anchor_points() < self.num_needed_anchor_points:
            input_object.insert_n_anchor_points(self.num_needed_anchor_points)
        output_object.apply_function(self.func)
        self.squash_onto_left(input_object)
        self.squash_onto_right(output_object)
        self.play(
            ShowCreation(input_object), 
            ShowCreation(output_object),
            run_time = run_time
            )

class TestDual(DualScene):
    def construct(self):
        self.force_skipping()
        self.apply_function(lambda (x, y, z) : complex_to_R3(complex(x,y)**2))
        self.revert_to_original_skipping_status()
        self.path_draw(Line(LEFT + DOWN, RIGHT + DOWN))
        
class EquationSolver1d(GraphScene, ZoomedScene, ReconfigurableScene):
    CONFIG = {
    "func" : lambda x : x,
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
        self.graph = self.get_graph(self.func)
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
        lowerY = self.func(lowerX)
        upperX = self.initial_upper_x
        upperY = self.func(upperX)

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
        lowerDotYPoint = self.coords_to_point(0, self.func(lowerX))
        lowerDot = Dot(lowerDotPoint)
        upperDotPoint = self.input_to_graph_point(upperX, self.graph)
        upperDot = Dot(upperDotPoint)
        upperDotXPoint = self.coords_to_point(upperX, 0)
        upperDotYPoint = self.coords_to_point(0, self.func(upperX))

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
                    newY = self.func(newX)
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
            midY = self.func(midX)

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

        self.wait()

    def construct(self):
        self.drawGraph()
        self.solveEquation()

class FirstSqrtScene(EquationSolver1d):
    CONFIG = {
    "x_min" : 0,
    "x_max" : 2.5,
    "y_min" : 0,
    "y_max" : 2.5**2,
    "graph_origin" : 2*DOWN + 5 * LEFT,
    "x_axis_width" : 12,
    "zoom_factor" : 3,
    "zoomed_canvas_center" : 2.25 * UP + 1.75 * LEFT,
    "func" : lambda x : x**2,
    "targetX" : np.sqrt(2),
    "targetY" : 2,
    "initial_lower_x" : 1,
    "initial_upper_x" : 2,
    "num_iterations" : 10,
    "iteration_at_which_to_start_zoom" : 3,
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
            func = lambda x : x**2 - shiftVal,
            targetY = 0,
            graph_label = "y = x^2 - " + str(shiftVal),
            y_min = self.y_min - shiftVal,
            y_max = self.y_max - shiftVal,
            show_target_line = False,
            graph_origin = newOrigin)
        self.solveEquation()

# TODO: Perhaps have pulses fade out and in at ends of line, instead of jarringly
# popping out and in?
class LinePulser(ContinualAnimation):
    def __init__(self, line, bullet_template, num_bullets, pulse_time, **kwargs):
        self.line = line
        self.num_bullets = num_bullets
        self.pulse_time = pulse_time
        self.bullets = [bullet_template.copy() for i in range(num_bullets)]
        ContinualAnimation.__init__(self, VGroup(line, VGroup(*self.bullets)), **kwargs)

    def update_mobject(self, dt):
        alpha = self.external_time % self.pulse_time
        start = self.line.get_start()
        end = self.line.get_end()
        for i in range(self.num_bullets):
            self.bullets[i].move_to(interpolate(start, end, 
                np.true_divide((i + alpha),(self.num_bullets))))
            self.bullets[i].shift((0, 0, 1)) # Temporary hack for z-buffer fidgetiness

class LoopSplitScene(Scene):

    def PulsedLine(self, start, end, bullet_template, num_bullets = 4, pulse_time = 1, **kwargs):
        line = Line(start, end, **kwargs)
        anim = LinePulser(line, bullet_template, num_bullets, pulse_time, **kwargs)
        return [VGroup(line, *anim.bullets), anim]

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

        default_bullet = PiCreature(color = RED)
        default_bullet.scale(0.15)

        def SGroup(*args):
            return VGroup(*[arg[0] for arg in args])

        top_line = self.PulsedLine(tl, tr, default_bullet, color = BLUE)
        right_line = self.PulsedLine(tr, br, default_bullet, color = BLUE)
        bottom_line = self.PulsedLine(br, bl, default_bullet, color = BLUE)
        left_line = self.PulsedLine(bl, tl, default_bullet, color = BLUE)
        line_list = [top_line, right_line, bottom_line, left_line]
        loop = SGroup(*line_list)
        for line in line_list:
            self.add(*line)
        self.wait()

        # Splits in middle
        split_line = DashedLine(interpolate(tl, tr, 0.5), interpolate(bl, br, 0.5))
        self.play(ShowCreation(split_line))

        self.remove(*split_line)
        mid_line_left = self.PulsedLine(tm, bm, default_bullet, color = loop_color)
        mid_line_right = self.PulsedLine(bm, tm, default_bullet, color = loop_color)
        self.add(*mid_line_left)
        self.add(*mid_line_right)

        top_line_left_half = self.PulsedLine(tl, tm, default_bullet, 2, 1, color = loop_color)
        top_line_right_half = self.PulsedLine(tm, tr, default_bullet, 2, 1, color = loop_color)

        bottom_line_left_half = self.PulsedLine(bm, bl, default_bullet, 2, 1, color = loop_color)
        bottom_line_right_half = self.PulsedLine(br, bm, default_bullet, 2, 1, color = loop_color)

        self.remove(*top_line)
        self.add(*top_line_left_half)
        self.add(*top_line_right_half)
        self.remove(*bottom_line)
        self.add(*bottom_line_left_half)
        self.add(*bottom_line_right_half)

        left_open_loop = SGroup(top_line_left_half, left_line, bottom_line_left_half)
        left_closed_loop = VGroup(left_open_loop, mid_line_left[0])
        right_open_loop = SGroup(top_line_right_half, right_line, bottom_line_right_half)
        right_closed_loop = VGroup(right_open_loop, mid_line_right[0])

        self.play(
            ApplyMethod(left_closed_loop.shift, LEFT), 
            ApplyMethod(right_closed_loop.shift, RIGHT)
            )

        self.wait()

        self.play(
            ApplyMethod(left_open_loop.shift, LEFT), 
            ApplyMethod(right_open_loop.shift, RIGHT)
            )

        self.wait()

        mid_lines = SGroup(mid_line_left, mid_line_right)

        highlight_circle = Circle(color = YELLOW_E) # Perhaps make this a dashed circle?
        highlight_circle.surround(mid_lines)
        self.play(Indicate(mid_lines), ShowCreation(highlight_circle, run_time = 0.5))
        
        self.wait()

        self.play(FadeOut(highlight_circle), FadeOut(mid_lines))
        # Because FadeOut didn't remove the continual pulsers, we remove them manually
        self.remove(mid_line_left[1], mid_line_right[1])

        # Brings loop back together; keep in sync with motions which bring loop apart above
        self.play(
            ApplyMethod(left_open_loop.shift, 2 * RIGHT), 
            ApplyMethod(right_open_loop.shift, 2 * LEFT)
            )

        self.wait()

class NumberLineScene(Scene):
    def construct(self):
        num_line = NumberLine()
        self.add(num_line)
        self.wait()

        interval_1d = Line(num_line.number_to_point(-1), num_line.number_to_point(1), 
            stroke_color = RED, stroke_width = 10)
        self.play(ShowCreation(interval_1d))
        self.wait()

        num_plane = NumberPlane()

        random_points = [UP + LEFT, 2 * UP, RIGHT, DOWN, DOWN + RIGHT, LEFT]

        interval_2d = Polygon(
            *random_points,
            stroke_color = RED,
            stroke_width = 10)
        # TODO: Turn this into a more complicated, curvy loop?
        # TODO: Illustrate borders and filled interiors with a particular color
        # on both 1d and 2d region?

        self.play(
            FadeOut(num_line), 
            FadeIn(num_plane),
            ReplacementTransform(interval_1d, interval_2d))

        self.wait()        

class ArrowCircleTest(Scene):
    def construct(self):
        circle_radius = 3
        circle = Circle(radius = circle_radius)
        self.add(circle)

        base_arrow = Arrow(circle_radius * 0.7 * RIGHT, circle_radius * 1.3 * RIGHT)

        def rev_rotate(x, revs):
            return x.rotate(revs * 2 * np.pi)

        num_arrows = 8 * 3
        arrows = [rev_rotate(base_arrow.copy(), (np.true_divide(i, num_arrows))) for i in range(num_arrows)]
        arrows_vgroup = VGroup(*arrows)

        self.play(ShowCreation(arrows_vgroup), run_time = 2.5, rate_func = None)

        self.wait()

class FuncRotater(Animation):
    CONFIG = {
        "rotate_func" : lambda x : x # Func from alpha to revolutions
    }

    # Perhaps abstract this out into an "Animation from base object" class
    def update_submobject(self, submobject, starting_submobject, alpha):
        submobject.points = np.array(starting_submobject.points)

    def update_mobject(self, alpha):
        Animation.update_mobject(self, alpha)
        self.mobject.rotate(
            self.rotate_func(alpha) * 2 * np.pi, 
        )
        # Will want to have arrow colors change to match direction as well

class TestRotater(Scene):
    def construct(self):
        test_line = Line(ORIGIN, RIGHT)
        self.play(FuncRotater(
            test_line,
            rotate_func = lambda x : x % 0.25,
            run_time = 10))

class OdometerScene(Scene):
    CONFIG = {
        "rotate_func" : lambda x : np.sin(x * 2 * np.pi),
        "run_time" : 5
    }

    def construct(self):
        base_arrow = Arrow(ORIGIN, RIGHT)
        circle = Circle(center = ORIGIN, radius = 1.3)
        self.add(circle)
        num_display = DecimalNumber(0)
        num_display.move_to(2 * DOWN)
        self.play(
            FuncRotater(base_arrow, rotate_func = self.rotate_func),
            ChangingDecimal(num_display, self.rotate_func),
            run_time = self.run_time,
            rate_func = None)

def Vect2dToRevAngle(x, y):
    return np.true_divide(np.arctan2(y, x), 2 * np.pi)

# Returns the value with the same fractional component as x, closest to m
def resit_near(x, m):
    frac_diff = (x - m) % 1
    if frac_diff > 0.5:
        frac_diff -= 1
    return m + frac_diff

# Perhaps use modulus of (uniform) continuity instead of num_check_points, calculating 
# latter as needed from former?
def winding_func(func, start, end, num_check_points):
    check_points = [None for i in range(num_check_points)]
    check_points[0] = func(0)
    step_size = np.true_divide(end - start, num_check_points)
    for i in range(num_check_points - 1):
        check_points[i + 1] = \
        resit_near(
            func(start + (i + 1) * step_size),
            check_points[i])
    return lambda x : resit_near(func(x), check_points[int((x - start)/step_size)])

class EquationSolver2d(ZoomedScene):
    #TODO
    CONFIG = {
    "func" : lambda p : p,
    "target_input" : (0, 0),
    "target_output" : (0, 0),
    "initial_top_left_point" : (0, 0),
    "initial_guess_dimensions" : (0, 0),
    "num_iterations" : 10,
    "iteration_at_which_to_start_zoom" : None
    }