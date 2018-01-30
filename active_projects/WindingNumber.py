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
from camera import *
from mobject.svg_mobject import *
from mobject.tex_mobject import *
from topics.graph_scene import *

# TODO/WARNING: There's a lot of refactoring and cleanup to be done in this code,
# (and it will be done, but first I'll figure out what I'm doing with all this...)
# -SR
        
class EquationSolver1d(GraphScene, ZoomedScene):
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
        yBraces.rotate(TAU/4)

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


# TODO: Perhaps have bullets (pulses) fade out and in at ends of line, instead of jarringly
# popping out and in?
#
# TODO: Perhaps have bullets change color corresponding to a function of their coordinates?
# This could involve some merging of functoinality with PiWalker
class LinePulser(ContinualAnimation):
    def __init__(self, line, bullet_template, num_bullets, pulse_time, color_func = None, **kwargs):
        self.line = line
        self.num_bullets = num_bullets
        self.pulse_time = pulse_time
        self.bullets = [bullet_template.copy() for i in range(num_bullets)]
        self.color_func = color_func
        ContinualAnimation.__init__(self, VGroup(line, VGroup(*self.bullets)), **kwargs)

    def update_mobject(self, dt):
        alpha = self.external_time % self.pulse_time
        start = self.line.get_start()
        end = self.line.get_end()
        for i in range(self.num_bullets):
            position = interpolate(start, end, 
                np.true_divide((i + alpha),(self.num_bullets)))
            self.bullets[i].move_to(position)
            if self.color_func:
                self.bullets.set_color(self.color_func(position))


def color_func(alpha):
    alpha = alpha % 1
    colors = ["#FF0000", ORANGE, YELLOW, "#00FF00", "#0000FF", "#FF00FF"]
    num_colors = len(colors)
    beta = (alpha % (1.0/num_colors)) * num_colors
    start_index = int(np.floor(num_colors * alpha)) % num_colors
    end_index = (start_index + 1) % num_colors

    return interpolate_color(colors[start_index], colors[end_index], beta)

class ArrowCircleTest(Scene):
    def construct(self):
        circle_radius = 3
        circle = Circle(radius = circle_radius, color = WHITE)
        self.add(circle)

        base_arrow = Arrow(circle_radius * 0.7 * RIGHT, circle_radius * 1.3 * RIGHT)

        def rev_rotate(x, revs):
            x.rotate(revs * TAU, about_point = ORIGIN)
            x.set_color(color_func(revs))
            return x

        num_arrows = 8 * 3
        arrows = [rev_rotate(base_arrow.copy(), (np.true_divide(i, num_arrows))) for i in range(num_arrows)]
        arrows_vgroup = VGroup(*arrows)

        self.play(ShowCreation(arrows_vgroup), run_time = 2.5, rate_func = None)

        self.wait()

class FuncRotater(Animation):
    CONFIG = {
        "rotate_func" : lambda x : x # Func from alpha to revolutions
    }

    # Perhaps abstract this out into an "Animation updating from original object" class
    def update_submobject(self, submobject, starting_submobject, alpha):
        submobject.points = np.array(starting_submobject.points)

    def update_mobject(self, alpha):
        Animation.update_mobject(self, alpha)
        angle_revs = self.rotate_func(alpha)
        # We do a clockwise rotation
        self.mobject.rotate(
            -angle_revs * TAU, 
            about_point = ORIGIN
        )
        self.mobject.set_color(color_func(angle_revs))

class TestRotater(Scene):
    def construct(self):
        test_line = Line(ORIGIN, RIGHT)
        self.play(FuncRotater(
            test_line,
            rotate_func = lambda x : x % 0.25,
            run_time = 10))

# TODO: Be careful about clockwise vs. counterclockwise convention throughout!
# Make sure this is correct everywhere in resulting video.
class OdometerScene(Scene):
    CONFIG = {
        "rotate_func" : lambda x : np.sin(x * TAU),
        "run_time" : 5,
        "dashed_line_angle" : None,
        "biased_display_start" : None
    }

    def construct(self):
        radius = 1.3
        circle = Circle(center = ORIGIN, radius = radius)
        self.add(circle)

        if self.dashed_line_angle:
            dashed_line = DashedLine(ORIGIN, radius * RIGHT)
            # Clockwise rotation
            dashed_line.rotate(-self.dashed_line_angle * TAU, about_point = ORIGIN)
            self.add(dashed_line)
        
        num_display = DecimalNumber(0)
        num_display.move_to(2 * DOWN)

        display_val_bias = 0
        if self.biased_display_start != None:
            display_val_bias = self.biased_display_start - self.rotate_func(0)
        display_func = lambda alpha : self.rotate_func(alpha) + display_val_bias

        base_arrow = Arrow(ORIGIN, RIGHT, buff = 0)

        self.play(
            FuncRotater(base_arrow, rotate_func = self.rotate_func),
            ChangingDecimal(num_display, display_func),
            run_time = self.run_time,
            rate_func = None)

def point_to_rev((x, y)):
    # Warning: np.arctan2 would happily discontinuously returns the value 0 for (0, 0), due to 
    # design choices in the underlying atan2 library call, but for our purposes, this is 
    # illegitimate, and all winding number calculations must be set up to avoid this
    if (x, y) == (0, 0):
        print "Error! Angle of (0, 0) computed!"
        return None
    return np.true_divide(np.arctan2(y, x), TAU)

# Returns the value with the same fractional component as x, closest to m
def resit_near(x, m):
    frac_diff = (x - m) % 1
    if frac_diff > 0.5:
        frac_diff -= 1
    return m + frac_diff

# TODO?: Perhaps use modulus of (uniform) continuity instead of num_checkpoints, calculating 
# latter as needed from former?
def make_alpha_winder(func, start, end, num_checkpoints):
    check_points = [None for i in range(num_checkpoints)]
    check_points[0] = func(start)
    step_size = np.true_divide(end - start, num_checkpoints)
    for i in range(num_checkpoints - 1):
        check_points[i + 1] = \
        resit_near(
            func(start + (i + 1) * step_size),
            check_points[i])
    def return_func(alpha):
        index = clamp(0, num_checkpoints - 1, int(alpha * num_checkpoints))
        x = interpolate(start, end, alpha)
        return resit_near(func(x), check_points[index])
    return return_func

def split_interval((a, b)):
    mid = (a + b)/2.0
    return ((a, mid), (mid, b))

class RectangleData():
    def __init__(self, x_interval, y_interval):
        self.rect = (x_interval, y_interval)

    def get_top_left(self):
        return np.array((self.rect[0][0], self.rect[1][1]))

    def get_top_right(self):
        return np.array((self.rect[0][1], self.rect[1][1]))

    def get_bottom_right(self):
        return np.array((self.rect[0][1], self.rect[1][0]))

    def get_bottom_left(self):
        return np.array((self.rect[0][0], self.rect[1][0]))

    def get_top(self):
        return (self.get_top_left(), self.get_top_right())

    def get_right(self):
        return (self.get_top_right(), self.get_bottom_right())

    def get_bottom(self):
        return (self.get_bottom_right(), self.get_bottom_left())

    def get_left(self):
        return (self.get_bottom_left(), self.get_top_left())

    def splits_on_dim(self, dim):
        x_interval = self.rect[0]
        y_interval = self.rect[1]

        # TODO: Can refactor the following; will do later
        if dim == 0:
            return_data = [RectangleData(new_interval, y_interval) for new_interval in split_interval(x_interval)]
        elif dim == 1:
            return_data = [RectangleData(x_interval, new_interval) for new_interval in split_interval(y_interval)]        
        else: 
            print "RectangleData.splits_on_dim passed illegitimate dimension!"

        return tuple(return_data)

    def split_line_on_dim(self, dim):
        x_interval = self.rect[0]
        y_interval = self.rect[1]

        if dim == 0:
            sides = (self.get_top(), self.get_bottom())
        elif dim == 1:
            sides = (self.get_left(), self.get_right())
        else:
            print "RectangleData.split_line_on_dim passed illegitimate dimension!"

        return tuple([mid(x, y) for (x, y) in sides])

def complex_to_pair(c):
    return (c.real, c.imag)

def plane_poly_with_roots(*points):
    def f((x, y)):
        return complex_to_pair(np.prod([complex(x, y) - complex(a,b) for (a,b) in points]))
    return f

def plane_func_from_complex_func(f):
    return lambda (x, y) : complex_to_pair(f(complex(x,y)))

def point_func_from_complex_func(f):
    return lambda (x, y, z): complex_to_R3(f(complex(x, y)))

empty_animation = Animation(Mobject())
def EmptyAnimation():
    return empty_animation

class WalkerAnimation(Animation):
    CONFIG = {
        "walk_func" : None, # Must be initialized to use
        "remover" : True,
        "rate_func" : None,
        "coords_to_point" : None
    }

    def __init__(self, walk_func, rev_func, coords_to_point, **kwargs):
        self.walk_func = walk_func
        self.rev_func = rev_func
        self.coords_to_point = coords_to_point
        self.compound_walker = VGroup()
        self.compound_walker.walker = PiCreature(color = RED)
        self.compound_walker.walker.scale(0.35)
        self.compound_walker.arrow = Arrow(ORIGIN, RIGHT) #, buff = 0)
        self.compound_walker.digest_mobject_attrs()
        Animation.__init__(self, self.compound_walker, **kwargs)

    # Perhaps abstract this out into an "Animation updating from original object" class
    def update_submobject(self, submobject, starting_submobject, alpha):
        submobject.points = np.array(starting_submobject.points)

    def update_mobject(self, alpha):
        Animation.update_mobject(self, alpha)
        cur_x, cur_y = cur_coords = self.walk_func(alpha)
        self.mobject.walker.move_to(self.coords_to_point(cur_x, cur_y))
        rev = self.rev_func(cur_coords)
        self.mobject.walker.set_color(color_func(rev))
        self.mobject.arrow.set_color(color_func(rev))
        self.mobject.arrow.rotate(
            rev * TAU, 
            about_point = ORIGIN #self.mobject.arrow.get_start()
        )

def LinearWalker(start_coords, end_coords, coords_to_point, rev_func, **kwargs):
    walk_func = lambda alpha : interpolate(start_coords, end_coords, alpha)
    return WalkerAnimation(
        walk_func = walk_func, 
        coords_to_point = coords_to_point, 
        rev_func = rev_func,
        **kwargs)

class PiWalker(Scene):
    CONFIG = {
        "func" : plane_func_from_complex_func(lambda c : c**2),
        "walk_coords" : [],
        "step_run_time" : 1
    }

    def construct(self):

        rev_func = lambda p : point_to_rev(self.func(p))

        num_plane = NumberPlane()
        num_plane.fade()
        self.add(num_plane)

        walk_coords = self.walk_coords
        for i in range(len(walk_coords)):
            start_x, start_y = start_coords = walk_coords[i]
            start_point = num_plane.coords_to_point(start_x, start_y)
            end_x, end_y = end_coords = walk_coords[(i + 1) % len(walk_coords)]
            end_point = num_plane.coords_to_point(end_x, end_y)
            self.play(
                LinearWalker(
                    start_coords = start_coords, 
                    end_coords = end_coords,
                    coords_to_point = num_plane.coords_to_point,
                    rev_func = rev_func,
                    remover = (i < len(walk_coords) - 1)
                ),
                ShowCreation(Line(start_point, end_point), rate_func = None),
                run_time = self.step_run_time)

        # TODO: Allow smooth paths instead of brekaing them up into lines, and 
        # use point_from_proportion to get points along the way
                

        self.wait()

class PiWalkerRect(PiWalker):
    CONFIG = {
        "start_x" : -1,
        "start_y" : 1,
        "walk_width" : 2,
        "walk_height" : 2,
    }

    def setup(self):
        TL = np.array((self.start_x, self.start_y))
        TR = TL + (self.walk_width, 0)
        BR = TR + (0, -self.walk_height)
        BL = BR + (-self.walk_width, 0)
        self.walk_coords = [TL, TR, BR, BL]
        PiWalker.setup(self)

class PiWalkerCircle(PiWalker):
    CONFIG = {
        "radius" : 1,
        "num_steps" : 100,
        "step_run_time" : 0.01
    }

    def setup(self):
        r = self.radius
        N = self.num_steps
        self.walk_coords = [r * np.array((np.cos(i * TAU/N), np.sin(i * TAU/N))) for i in range(N)]
        PiWalker.setup(self)

# TODO: Perhaps restructure this to avoid using AnimationGroup, and instead 
# use lists of animations or lists or other such data, to be merged and processed into parallel 
# animations later
class EquationSolver2d(Scene):
    CONFIG = {
        "func" : plane_poly_with_roots((1, 2), (-1, 3)),
        "initial_lower_x" : -5.1,
        "initial_upper_x" : 5.1,
        "initial_lower_y" : -3.1,
        "initial_upper_y" : 3.1,
        "num_iterations" : 5,
        "num_checkpoints" : 10,
        # TODO: Consider adding a "find_all_roots" flag, which could be turned off 
        # to only explore one of the two candidate subrectangles when both are viable
    }

    def construct(self):
        num_plane = NumberPlane()
        num_plane.fade()
        self.add(num_plane)

        rev_func = lambda p : point_to_rev(self.func(p))

        def Animate2dSolver(cur_depth, rect, dim_to_split):
            if cur_depth >= self.num_iterations:
                return EmptyAnimation()

            def draw_line_return_wind(start, end, start_wind):
                alpha_winder = make_alpha_winder(rev_func, start, end, self.num_checkpoints)
                a0 = alpha_winder(0)
                rebased_winder = lambda alpha: alpha_winder(alpha) - a0 + start_wind
                flashing_line = Line(num_plane.coords_to_point(*start), num_plane.coords_to_point(*end),
                    stroke_width = 5,
                    color = RED)
                thin_line = flashing_line.copy()
                thin_line.set_stroke(width = 1)
                walker_anim = LinearWalker(
                    start_coords = start, 
                    end_coords = end,
                    coords_to_point = num_plane.coords_to_point,
                    rev_func = rev_func,
                    remover = True
                )
                line_draw_anim = AnimationGroup(
                    ShowCreation(thin_line), 
                    #ShowPassingFlash(flashing_line), 
                    walker_anim,
                    rate_func = None)
                anim = line_draw_anim
                return (anim, rebased_winder(1))

            wind_so_far = 0
            anim = EmptyAnimation()
            sides = [
                rect.get_top(), 
                rect.get_right(), 
                rect.get_bottom(), 
                rect.get_left()
            ]
            for (start, end) in sides:
                (next_anim, wind_so_far) = draw_line_return_wind(start, end, wind_so_far)
                anim = Succession(anim, next_anim)

            total_wind = round(wind_so_far)

            if total_wind == 0:
                coords = [
                    rect.get_top_left(), 
                    rect.get_top_right(), 
                    rect.get_bottom_right(), 
                    rect.get_bottom_left()
                ]
                points = [num_plane.coords_to_point(x, y) for (x, y) in coords]
                # TODO: Maybe use diagonal lines or something to fill in rectangles indicating
                # their "Nothing here" status?
                fill_rect = polygonObject = Polygon(*points, fill_opacity = 0.8, color = RED)
                return Succession(anim, FadeIn(fill_rect))
            else:
                (sub_rect1, sub_rect2) = rect.splits_on_dim(dim_to_split)
                sub_rects = [sub_rect1, sub_rect2]
                sub_anims = [
                    Animate2dSolver(
                        cur_depth = cur_depth + 1,
                        rect = sub_rect,
                        dim_to_split = 1 - dim_to_split
                    )
                    for sub_rect in sub_rects
                ]
                mid_line_coords = rect.split_line_on_dim(dim_to_split)
                mid_line_points = [num_plane.coords_to_point(x, y) for (x, y) in mid_line_coords]
                mid_line = DashedLine(*mid_line_points)
                return Succession(anim, 
                    ShowCreation(mid_line), 
                    # FadeOut(mid_line), # TODO: Can change timing so this fades out at just the time it would be overdrawn
                    AnimationGroup(*sub_anims)
                )

        lower_x = self.initial_lower_x
        upper_x = self.initial_upper_x
        lower_y = self.initial_lower_y
        upper_y = self.initial_upper_y

        x_interval = (lower_x, upper_x)
        y_interval = (lower_y, upper_y)

        rect = RectangleData(x_interval, y_interval)

        anim = Animate2dSolver(
            cur_depth = 0, 
            rect = rect,
            dim_to_split = 0,
        )

        self.play(anim)

        self.wait()

#############
# Above are mostly general tools; here, we list, in order, finished or near-finished scenes

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
# TODO: Don't bother with ReconfigurableScene; just use new config from start
# (But can also use this as written, and just cut into middle in Premiere)

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

# TODO: Pi creatures intrigued

class ComplexPlaneIs2d(Scene):
    def construct(self):
        com_plane = ComplexPlane()
        self.add(com_plane)
        # TODO: Add labels to axes, specific complex points
        self.wait()

class NumberLineScene(Scene):
    def construct(self):
        num_line = NumberLine()
        self.add(num_line)
        # TODO: Add labels, arrows, specific points
        self.wait()

        border_color = PURPLE_E
        inner_color = RED
        stroke_width = 10

        left_point = num_line.number_to_point(-1)
        right_point = num_line.number_to_point(1)
        # TODO: Make this line a thin rectangle
        interval_1d = Line(left_point, right_point, 
            stroke_color = inner_color, stroke_width = stroke_width)
        rect_1d = Rectangle(stroke_width = 0, fill_opacity = 1, fill_color = inner_color)
        rect_1d.replace(interval_1d)
        rect_1d.stretch_to_fit_height(SMALL_BUFF)
        left_dot = Dot(left_point, stroke_width = stroke_width, color = border_color)
        right_dot = Dot(right_point, stroke_width = stroke_width, color = border_color)
        endpoints_1d = VGroup(left_dot, right_dot)
        full_1d = VGroup(rect_1d, endpoints_1d)
        self.play(ShowCreation(full_1d))
        self.wait()

        # TODO: Can polish the morphing above; have dots become left and right sides, and 
        # only then fill in the top and bottom

        num_plane = NumberPlane()

        random_points = [UP + LEFT, UP + RIGHT, DOWN + RIGHT, DOWN + LEFT]

        border_2d = Polygon(
            *random_points,
            stroke_color = border_color,
            stroke_width = stroke_width)

        filling_2d = Polygon(
            *random_points,
            fill_color = inner_color,
            fill_opacity = 0.8,
            stroke_width = stroke_width)
        full_2d = VGroup(filling_2d, border_2d)

        self.play(
            FadeOut(num_line), 
            FadeIn(num_plane),
            ReplacementTransform(full_1d, full_2d))

        self.wait()

initial_2d_func = point_func_from_complex_func(lambda c : np.exp(c))

class Initial2dFuncSceneMorphing(Scene):
    CONFIG = {
        "num_needed_anchor_points" : 10,
        "func" : initial_2d_func,
    }

    def setup(self):
        split_line = DashedLine(SPACE_HEIGHT * UP, SPACE_HEIGHT * DOWN)
        self.num_plane = NumberPlane(x_radius = SPACE_WIDTH/2)
        self.num_plane.to_edge(LEFT, buff = 0)
        self.num_plane.prepare_for_nonlinear_transform()
        self.add(self.num_plane, split_line)

    def squash_onto_left(self, object):
        object.shift(SPACE_WIDTH/2 * LEFT)

    def squash_onto_right(self, object):
        object.shift(SPACE_WIDTH/2 * RIGHT)

    def obj_draw(self, input_object):
        output_object = input_object.copy()
        if input_object.get_num_anchor_points() < self.num_needed_anchor_points:
            input_object.insert_n_anchor_points(self.num_needed_anchor_points)
        output_object.apply_function(self.func)
        self.squash_onto_left(input_object)
        self.squash_onto_right(output_object)
        self.play(
            ShowCreation(input_object), 
            ShowCreation(output_object)
            )

    def construct(self):
        right_plane = self.num_plane.copy()
        right_plane.center()
        right_plane.prepare_for_nonlinear_transform()
        right_plane.apply_function(self.func)
        right_plane.shift(SPACE_WIDTH/2 * RIGHT)
        self.right_plane = right_plane
        crappy_cropper = FullScreenFadeRectangle(fill_opacity = 1)
        crappy_cropper.stretch_to_fit_width(SPACE_WIDTH)
        crappy_cropper.to_edge(LEFT, buff = 0)
        self.play(
            ReplacementTransform(self.num_plane.copy(), right_plane),
            FadeIn(crappy_cropper), 
            Animation(self.num_plane),
            run_time = 3
        )

        points = [LEFT + DOWN, RIGHT + DOWN, LEFT + UP, RIGHT + UP]
        for i in range(len(points) - 1):
            line = Line(points[i], points[i + 1], color = RED)
            self.obj_draw(line)

# Alternative to the above, using MappingCameras, but no morphing animation
class Initial2dFuncSceneWithoutMorphing(Scene):

    def setup(self):
        left_camera = Camera(**self.camera_config)
        right_camera = MappingCamera(
            mapping_func = initial_2d_func,
            **self.camera_config)
        split_screen_camera = SplitScreenCamera(left_camera, right_camera, **self.camera_config)
        self.camera = split_screen_camera

    def construct(self):
        num_plane = NumberPlane()
        num_plane.prepare_for_nonlinear_transform()
        #num_plane.fade()
        self.add(num_plane)
        
        points = [LEFT + DOWN, RIGHT + DOWN, LEFT + UP, RIGHT + UP]
        for i in range(len(points) - 1):
            line = Line(points[i], points[i + 1], color = RED)
            self.play(ShowCreation(line))

# TODO: Illustrations for introducing domain coloring

# TODO: Bunch of Pi walker scenes

# TODO: An odometer scene when introducing winding numbers
# (Just set up an OdometerScene with function matching the walking of the Pi
# creature from previous scene, then place it as a simultaneous inset with Premiere)

class LoopSplitScene(Scene):

    def PulsedLine(self, start, end, bullet_template, num_bullets = 4, pulse_time = 1, **kwargs):
        line = Line(start, end, **kwargs)
        anim = LinePulser(line, bullet_template, num_bullets, pulse_time, **kwargs)
        return [VGroup(line, *anim.bullets), anim]

    def construct(self):
        num_plane = NumberPlane(color = LIGHT_GREY, stroke_width = 1)

        # We actually don't want to highlight
        num_plane.axes.set_stroke(color = WHITE, width = 2)
        num_plane.fade()
        self.add(num_plane)

        scale_factor = 2
        shift_term = 0

        # Original loop
        tl = scale_factor * (UP + LEFT) + shift_term
        tm = scale_factor * UP + shift_term
        tr = scale_factor * (UP + RIGHT) + shift_term
        mr = scale_factor * RIGHT + shift_term
        br = scale_factor * (DOWN + RIGHT) + shift_term
        bm = scale_factor * DOWN + shift_term
        bl = scale_factor * (DOWN + LEFT) + shift_term
        lm = scale_factor * LEFT + shift_term

        loop_color = BLUE

        default_bullet = PiCreature(color = RED)
        default_bullet.scale(0.15)

        modified_bullet = PiCreature(color = PINK)
        modified_bullet.scale(0.15)

        def SGroup(*args):
            return VGroup(*[arg[0] for arg in args])

        top_line = self.PulsedLine(tl, tr, default_bullet, color = BLUE)
        right_line = self.PulsedLine(tr, br, modified_bullet, color = BLUE)
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
        mid_line_right = self.PulsedLine(bm, tm, modified_bullet, color = loop_color)
        self.add(*mid_line_left)
        self.add(*mid_line_right)

        top_line_left_half = self.PulsedLine(tl, tm, default_bullet, 2, 1, color = loop_color)
        top_line_right_half = self.PulsedLine(tm, tr, modified_bullet, 2, 1, color = loop_color)

        bottom_line_left_half = self.PulsedLine(bm, bl, default_bullet, 2, 1, color = loop_color)
        bottom_line_right_half = self.PulsedLine(br, bm, modified_bullet, 2, 1, color = loop_color)

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

        # self.play(
        #     ApplyMethod(left_closed_loop.shift, LEFT), 
        #     ApplyMethod(right_closed_loop.shift, RIGHT)
        #     )

        self.wait()

        # self.play(
        #     ApplyMethod(left_open_loop.shift, LEFT), 
        #     ApplyMethod(right_open_loop.shift, RIGHT)
        #     )

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
        # self.play(
        #     ApplyMethod(left_open_loop.shift, 2 * RIGHT), 
        #     ApplyMethod(right_open_loop.shift, 2 * LEFT)
        #     )

        self.wait()

# Is there a way to abstract this into a general process to derive a new mapped scene from an old scene?
class LoopSplitSceneMapped(LoopSplitScene):

    def setup(self):
        left_camera = Camera(**self.camera_config)
        right_camera = MappingCamera(
            mapping_func = lambda (x, y, z) : complex_to_R3(((complex(x,y) + 3)**1.1) - 3), 
            **self.camera_config)
        split_screen_camera = SplitScreenCamera(left_camera, right_camera, **self.camera_config)
        self.camera = split_screen_camera

# TODO: Perhaps do extra illustration of zooming out and winding around a large circle, 
# to illustrate relation between degree and large-scale winding number
class FundThmAlg(EquationSolver2d):
    CONFIG = {
        "func" : plane_poly_with_roots((1, 2), (-1, 2.5), (-1, 2.5)),
        "num_iterations" : 1,
    }

# TODO: Borsuk-Ulam visuals
# Note: May want to do an ordinary square scene, then MappingCamera it into a circle
# class BorsukUlamScene(PiWalker):

# 3-way scene of "Good enough"-illustrating odometers; to be composed in Premiere
left_func = lambda x : x**2 - x + 1
diff_func = lambda x : np.cos(1.4 * (x - 0.1) * (np.log(x + 0.1) - 0.3) * TAU)/2.1

class LeftOdometer(OdometerScene):
    CONFIG = {
        "rotate_func" : left_func,
        "biased_display_start" : 0
    }

class RightOdometer(OdometerScene):
    CONFIG = {
        "rotate_func" : lambda x : left_func(x) + diff_func(x),
        "biased_display_start" : 0
    }

class DiffOdometer(OdometerScene):
    CONFIG = {
        "rotate_func" : diff_func,
        "dashed_line_angle" : 0.5,
        "biased_display_start" : 0
    }

# TODO: Brouwer's fixed point theorem visuals

# TODO: Pi creatures wide-eyed in amazement

#################

# TODOs, from easiest to hardest:

# Minor fiddling with little things in each animation; placements, colors, timing, text

# Initial odometer scene (simple once previous Pi walker scene is decided upon)

# Writing new Pi walker scenes by parametrizing general template

# Generalizing Pi walker stuff to make bullets on pulsing lines change colors dynamically according to 
# function traced out

# Debugging Pi walker stuff added to EquationSolver2d

# ----

# Pi creature emotion stuff

# BFT visuals

# Borsuk-Ulam visuals

# Domain coloring

# TODO: Ask about tracked mobject, which is probably very useful for our animations

# FIN
