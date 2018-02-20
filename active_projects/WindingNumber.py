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

def rev_to_rgba(alpha):
    alpha = (0.5 - alpha) % 1 # For convenience, to go CW from red on left instead of CCW from right
    # 0 is red, 1/6 is yellow, 1/3 is green, 2/3 is blue
    hue_list = [0, 0.5/6.0, 1/6.0, 1.1/6.0, 2/6.0, 3/6.0, 4/6.0, 5/6.0]
    num_hues = len(hue_list)
    start_index = int(np.floor(num_hues * alpha)) % num_hues
    end_index = (start_index + 1) % num_hues
    beta = (alpha % (1.0/num_hues)) * num_hues

    start_hue = hue_list[start_index]
    end_hue = hue_list[end_index]
    if end_hue < start_hue:
        end_hue = end_hue + 1
    hue = interpolate(start_hue, end_hue, beta)

    return color_to_rgba(Color(hue = hue, saturation = 1, luminance = 0.5))

    # alpha = alpha % 1
    # colors = colorslist
    # num_colors = len(colors)
    # beta = (alpha % (1.0/num_colors)) * num_colors
    # start_index = int(np.floor(num_colors * alpha)) % num_colors
    # end_index = (start_index + 1) % num_colors

    # return interpolate(colors[start_index], colors[end_index], beta)

def rev_to_color(alpha):
    return rgba_to_color(rev_to_rgba(alpha))

def point_to_rev((x, y), allow_origin = False):
    # Warning: np.arctan2 would happily discontinuously returns the value 0 for (0, 0), due to 
    # design choices in the underlying atan2 library call, but for our purposes, this is 
    # illegitimate, and all winding number calculations must be set up to avoid this
    if not(allow_origin) and (x, y) == (0, 0):
        print "Error! Angle of (0, 0) computed!"
        return
    return fdiv(np.arctan2(y, x), TAU)

def point_to_rgba(point):
    rev = point_to_rev(point, allow_origin = True)
    rgba = rev_to_rgba(rev)
    base_size = np.sqrt(point[0]**2 + point[1]**2)
    rescaled_size = np.sqrt(base_size/(base_size + 1))
    return rgba * rescaled_size

positive_color = rev_to_color(0)
negative_color = rev_to_color(0.5)
neutral_color = rev_to_color(0.25)
        
class EquationSolver1d(GraphScene, ZoomedScene):
    CONFIG = {
    "camera_config" : 
        {
            "use_z_coordinate_for_display_order": True,
        },
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
            curve_label = self.get_graph_label(self.graph, self.graph_label, 
                x_val = 4, direction = LEFT)
            curve_label.shift(LEFT)
            self.add(curve_label)
        
        if self.show_target_line:
            target_line_object = DashedLine(
                self.coords_to_point(self.x_min, self.targetY), 
                self.coords_to_point(self.x_max, self.targetY),
                dashed_segment_length = 0.1)
            self.add(target_line_object)

            target_line_label = TexMobject("y = " + str(self.targetY))
            target_line_label.next_to(target_line_object.get_left(), UP + RIGHT)
            self.add(target_line_label)

            self.wait() # Give us time to appreciate the graph
            self.play(FadeOut(target_line_label)) # Reduce clutter

        print "For reference, graphOrigin: ", self.coords_to_point(0, 0)
        print "targetYPoint: ", self.coords_to_point(0, self.targetY)

    # This is a mess right now (first major animation coded), 
    # but it works; can be refactored later or never
    def solveEquation(self):
        leftBrace = TexMobject("|") # Not using [ and ] because they end up crossing over
        leftBrace.set_color(negative_color)
        rightBrace = TexMobject("|")
        rightBrace.set_color(positive_color)
        xBraces = Group(leftBrace, rightBrace)
        xBraces.stretch(2, 0)

        downBrace = TexMobject("|")
        downBrace.set_color(negative_color)
        upBrace = TexMobject("|")
        upBrace.set_color(positive_color)
        yBraces = Group(downBrace, upBrace)
        yBraces.stretch(2, 0)
        yBraces.rotate(TAU/4)

        lowerX = self.initial_lower_x
        lowerY = self.func(lowerX)
        upperX = self.initial_upper_x
        upperY = self.func(upperX)

        leftBrace.move_to(self.coords_to_point(lowerX, 0)) #, aligned_edge = RIGHT)
        leftBraceLabel = DecimalNumber(lowerX)
        leftBraceLabel.next_to(leftBrace, DOWN + LEFT, buff = SMALL_BUFF)
        leftBraceLabelAnimation = ContinualChangingDecimal(leftBraceLabel, 
            lambda alpha : self.point_to_coords(leftBrace.get_center())[0],
            tracked_mobject = leftBrace)
        self.add(leftBraceLabelAnimation)
        
        rightBrace.move_to(self.coords_to_point(upperX, 0)) #, aligned_edge = LEFT)
        rightBraceLabel = DecimalNumber(upperX)
        rightBraceLabel.next_to(rightBrace, DOWN + RIGHT, buff = SMALL_BUFF)
        rightBraceLabelAnimation = ContinualChangingDecimal(rightBraceLabel, 
            lambda alpha : self.point_to_coords(rightBrace.get_center())[0],
            tracked_mobject = rightBrace)
        self.add(rightBraceLabelAnimation)

        downBrace.move_to(self.coords_to_point(0, lowerY)) #, aligned_edge = UP)
        downBraceLabel = DecimalNumber(lowerY)
        downBraceLabel.next_to(downBrace, LEFT + DOWN, buff = SMALL_BUFF)
        downBraceLabelAnimation = ContinualChangingDecimal(downBraceLabel, 
            lambda alpha : self.point_to_coords(downBrace.get_center())[1],
            tracked_mobject = downBrace)
        self.add(downBraceLabelAnimation)
        
        upBrace.move_to(self.coords_to_point(0, upperY)) #, aligned_edge = DOWN)
        upBraceLabel = DecimalNumber(upperY)
        upBraceLabel.next_to(upBrace, LEFT + UP, buff = SMALL_BUFF)
        upBraceLabelAnimation = ContinualChangingDecimal(upBraceLabel, 
            lambda alpha : self.point_to_coords(upBrace.get_center())[1],
            tracked_mobject = upBrace)
        self.add(upBraceLabelAnimation)

        lowerDotPoint = self.input_to_graph_point(lowerX, self.graph)
        lowerDotXPoint = self.coords_to_point(lowerX, 0)
        lowerDotYPoint = self.coords_to_point(0, self.func(lowerX))
        lowerDot = Dot(lowerDotPoint + OUT, color = negative_color)
        upperDotPoint = self.input_to_graph_point(upperX, self.graph)
        upperDot = Dot(upperDotPoint + OUT, color = positive_color)
        upperDotXPoint = self.coords_to_point(upperX, 0)
        upperDotYPoint = self.coords_to_point(0, self.func(upperX))

        lowerXLine = Line(lowerDotXPoint, lowerDotPoint, color = negative_color)
        upperXLine = Line(upperDotXPoint, upperDotPoint, color = positive_color)
        lowerYLine = Line(lowerDotYPoint, lowerDotPoint, color = negative_color)
        upperYLine = Line(upperDotYPoint, upperDotPoint, color = positive_color)
        self.add(lowerXLine, upperXLine, lowerYLine, upperYLine)

        self.add(xBraces, yBraces, lowerDot, upperDot)

        x_guess_line = Line(lowerDotXPoint, upperDotXPoint, color = neutral_color)
        self.add(x_guess_line)

        lowerGroup = Group(
            lowerDot, 
            leftBrace, downBrace,
            lowerXLine, lowerYLine,
            x_guess_line
        )
        
        upperGroup = Group(
            upperDot, 
            rightBrace, upBrace,
            upperXLine, upperYLine,
            x_guess_line
        )

        initialLowerXDot = Dot(lowerDotXPoint, color = negative_color)
        initialUpperXDot = Dot(upperDotXPoint, color = positive_color)
        initialLowerYDot = Dot(lowerDotYPoint, color = negative_color)
        initialUpperYDot = Dot(upperDotYPoint, color = positive_color)
        self.add(initialLowerXDot, initialUpperXDot, initialLowerYDot, initialUpperYDot)

        for i in range(self.num_iterations):
            if i == self.iteration_at_which_to_start_zoom:
                self.activate_zooming()
                self.little_rectangle.move_to(
                    self.coords_to_point(self.targetX, self.targetY))
                inverseZoomFactor = 1/float(self.zoom_factor)
                self.play(
                    lowerDot.scale_in_place, inverseZoomFactor,
                    upperDot.scale_in_place, inverseZoomFactor)


            def makeUpdater(xAtStart, fixed_guess_x):
                def updater(group, alpha):
                    dot, xBrace, yBrace, xLine, yLine, guess_line = group
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
                    fixed_guess_point = self.coords_to_point(fixed_guess_x, 0)
                    guess_line.put_start_and_end_on(xAxisPoint, fixed_guess_point)
                    return group
                return updater

            midX = (lowerX + upperX)/float(2)
            midY = self.func(midX)
            in_negative_branch = midY < self.targetY
            sign_color = negative_color if in_negative_branch else positive_color

            midCoords = self.coords_to_point(midX, midY)
            midColor = neutral_color
            # Hm... even the z buffer isn't helping keep this above x_guess_line
            midXPoint = Dot(self.coords_to_point(midX, 0) + OUT, color = midColor)

            x_guess_label_caption = TextMobject("New guess: x = ", fill_color = midColor)
            x_guess_label_num = DecimalNumber(midX, fill_color = midColor)
            x_guess_label_num.move_to(0.9 * SPACE_HEIGHT * DOWN)
            x_guess_label_caption.next_to(x_guess_label_num, LEFT)
            x_guess_label = Group(x_guess_label_caption, x_guess_label_num)
            y_guess_label_caption = TextMobject(", y = ", fill_color = midColor)
            y_guess_label_num = DecimalNumber(midY, fill_color = sign_color)
            y_guess_label_caption.next_to(x_guess_label_num, RIGHT)
            y_guess_label_num.next_to(y_guess_label_caption, RIGHT)
            y_guess_label = Group(y_guess_label_caption, y_guess_label_num)
            guess_labels = Group(x_guess_label, y_guess_label)

            self.play(
                ReplacementTransform(leftBrace.copy(), midXPoint),
                ReplacementTransform(rightBrace.copy(), midXPoint),
                FadeIn(x_guess_label))

            midXLine = DashedLine(self.coords_to_point(midX, 0), midCoords, color = midColor)
            self.play(ShowCreation(midXLine))
            midDot = Dot(midCoords, color = sign_color)
            if(self.iteration_at_which_to_start_zoom != None and 
                i >= self.iteration_at_which_to_start_zoom):
                midDot.scale_in_place(inverseZoomFactor)
            self.add(midDot)
            midYLine = DashedLine(midCoords, self.coords_to_point(0, midY), color = sign_color)
            self.play(
                ShowCreation(midYLine), 
                FadeIn(y_guess_label),
                ApplyMethod(midXPoint.set_color, sign_color),
                ApplyMethod(midXLine.set_color, sign_color))
            midYPoint = Dot(self.coords_to_point(0, midY), color = sign_color)
            self.add(midYPoint)

            if in_negative_branch:
                self.play(
                    UpdateFromAlphaFunc(lowerGroup, 
                        makeUpdater(lowerX, 
                            fixed_guess_x = upperX
                        )
                    ),
                    FadeOut(guess_labels),
                )
                lowerX = midX
                lowerY = midY

            else:
                self.play(
                    UpdateFromAlphaFunc(upperGroup, 
                        makeUpdater(upperX, 
                            fixed_guess_x = lowerX
                        )
                    ),
                    FadeOut(guess_labels),
                )
                upperX = midX
                upperY = midY
            #mid_group = Group(midXLine, midDot, midYLine) Removing groups doesn't flatten as expected?
            self.remove(midXLine, midDot, midYLine)

        self.wait()

    def construct(self):
        self.drawGraph()
        self.solveEquation()

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
    step_size = fdiv(end - start, num_checkpoints)
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
            return_data = [RectangleData(x_interval, new_interval) for new_interval in split_interval(y_interval)[::-1]]        
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
    return np.array((c.real, c.imag))

def plane_poly_with_roots(*points):
    def f((x, y)):
        return complex_to_pair(np.prod([complex(x, y) - complex(a,b) for (a,b) in points]))
    return f

def plane_func_from_complex_func(f):
    return lambda (x, y) : complex_to_pair(f(complex(x,y)))

def point_func_from_complex_func(f):
    return lambda (x, y, z): complex_to_R3(f(complex(x, y)))

test_map_func = point_func_from_complex_func(lambda c: c**2)

empty_animation = EmptyAnimation()

class WalkerAnimation(Animation):
    CONFIG = {
        "walk_func" : None, # Must be initialized to use
        "remover" : True,
        "rate_func" : None,
        "coords_to_point" : None
    }

    def __init__(self, walk_func, rev_func, coords_to_point, show_arrows = True, **kwargs):
        self.walk_func = walk_func
        self.rev_func = rev_func
        self.coords_to_point = coords_to_point
        self.compound_walker = VGroup()
        self.show_arrows = show_arrows

        base_walker = Dot().scale(5) # PiCreature().scale(0.8) # 
        self.compound_walker.walker = base_walker.scale(0.35).set_stroke(BLACK, 1.5) #PiCreature()
        if show_arrows:
            self.compound_walker.arrow = Arrow(ORIGIN, 0.5 * RIGHT, buff = 0).set_stroke(BLACK, 1.5)
        self.compound_walker.digest_mobject_attrs()
        Animation.__init__(self, self.compound_walker, **kwargs)

    # Perhaps abstract this out into an "Animation updating from original object" class
    def update_submobject(self, submobject, starting_submobject, alpha):
        submobject.points = np.array(starting_submobject.points)

    def update_mobject(self, alpha):
        Animation.update_mobject(self, alpha)
        cur_x, cur_y = cur_coords = self.walk_func(alpha)
        cur_point = self.coords_to_point(cur_x, cur_y)
        self.mobject.shift(cur_point - self.mobject.walker.get_center())
        rev = self.rev_func(cur_coords)
        self.mobject.walker.set_fill(rev_to_color(rev))
        if self.show_arrows:
            self.mobject.arrow.set_fill(rev_to_color(rev))
            self.mobject.arrow.rotate(
                rev * TAU, 
                about_point = self.mobject.arrow.get_start()
            )

def walker_animation_with_display(
    walk_func, 
    rev_func, 
    coords_to_point, 
    number_update_func = None,
    show_arrows = True,
    **kwargs
    ):
    
    walker_anim = WalkerAnimation(
        walk_func = walk_func, 
        rev_func = rev_func, 
        coords_to_point = coords_to_point,
        show_arrows = show_arrows,
        **kwargs)
    walker = walker_anim.compound_walker.walker

    if number_update_func != None:
        display = DecimalNumber(0, 
            num_decimal_points = 1, 
            fill_color = WHITE,
            include_background_rectangle = True)
        display.background_rectangle.fill_opacity = 0.5
        display.background_rectangle.fill_color = GREY
        display.background_rectangle.scale(1.2)
        displaycement = 0.5 * DOWN # How about that pun, eh?
        display.move_to(walker.get_center() + displaycement)
        display_anim = ChangingDecimal(display, 
            number_update_func, 
            tracked_mobject = walker_anim.compound_walker.walker,
            **kwargs)
        anim_group = AnimationGroup(walker_anim, display_anim)
        return anim_group
    else:
        return walker_anim

def LinearWalker(
    start_coords, 
    end_coords, 
    coords_to_point, 
    rev_func, 
    number_update_func = None, 
    show_arrows = True,
    **kwargs
    ):
    walk_func = lambda alpha : interpolate(start_coords, end_coords, alpha)
    return walker_animation_with_display(
        walk_func = walk_func, 
        coords_to_point = coords_to_point, 
        rev_func = rev_func,
        number_update_func = number_update_func,
        show_arrows = show_arrows,
        **kwargs)

class ColorMappedByFuncScene(Scene):
    CONFIG = {
        "func" : lambda p : p,
        "num_plane" : NumberPlane(),
        "show_num_plane" : True,

        "show_output" : False, # Not currently implemented; TODO
    }

    def setup(self):
        if self.show_output:
            self.input_to_pos_func = self.func
            self.pos_to_color_func = lambda p : p
        else:
            self.input_to_pos_func = lambda p : p
            self.pos_to_color_func = self.func

        # func_hash hashes the function at some random points
        func_hash_points = [(-0.93, 1), (1, -2.7), (20, 4)]
        to_hash = tuple((self.func(p)[0], self.func(p)[1]) for p in func_hash_points)
        func_hash = hash(to_hash)
        full_hash = hash((func_hash, self.camera.pixel_shape))
        self.background_image_file = os.path.join(
            self.output_directory, "images", 
            "color_mapped_background_" + str(full_hash) + ".png"
        )
        self.in_background_pass = not os.path.exists(self.background_image_file)

        print "Background file: " + self.background_image_file
        if self.in_background_pass:
            print "The background file does not exist yet; this will be a background creation + video pass"
        else:
            print "The background file already exists; this will only be a video pass"

    def construct(self):
        if self.in_background_pass:
            self.camera.set_background_from_func(
                lambda (x, y): point_to_rgba(
                    self.pos_to_color_func(
                        # Should be self.num_plane.point_to_coords_cheap(np.array([x, y, 0])),
                        # but for cheapness, we'll go with just (x, y), having never altered
                        # any num_plane's from default settings so far
                        (x, y)
                    )
                )
            )

            self.save_image(self.background_image_file, mode = "RGBA")

        self.camera.background_image = self.background_image_file
        self.camera.init_background()

        if self.show_num_plane:
            self.num_plane.fade()
            self.add(self.num_plane)

class PureColorMap(ColorMappedByFuncScene):
    CONFIG = {
        "show_num_plane" : False
    }

class ColorMappedByFuncStill(ColorMappedByFuncScene):
    def construct(self):
        ColorMappedByFuncScene.construct(self)
        self.wait()

class PiWalker(ColorMappedByFuncScene):
    CONFIG = {
        "walk_coords" : [],
        "step_run_time" : 1,
    }

    def construct(self):
        ColorMappedByFuncScene.construct(self)
        num_plane = self.num_plane

        rev_func = lambda p : point_to_rev(self.func(p))

        walk_coords = self.walk_coords
        for i in range(len(walk_coords)):
            start_x, start_y = start_coords = walk_coords[i]
            start_point = num_plane.coords_to_point(start_x, start_y)
            end_x, end_y = end_coords = walk_coords[(i + 1) % len(walk_coords)]
            end_point = num_plane.coords_to_point(end_x, end_y)
            self.play(
                ShowCreation(Line(start_point, end_point), rate_func = None),
                LinearWalker(
                    start_coords = start_coords, 
                    end_coords = end_coords,
                    coords_to_point = num_plane.coords_to_point,
                    rev_func = rev_func,
                    remover = (i < len(walk_coords) - 1),
                    show_arrows = not self.show_output
                ),
                run_time = self.step_run_time)

        # TODO: Allow smooth paths instead of breaking them up into lines, and 
        # use point_from_proportion to get points along the way

        self.wait()

class PiWalkerRect(PiWalker):
    CONFIG = {
        "start_x" : -1,
        "start_y" : 1,
        "walk_width" : 2,
        "walk_height" : 2,
        "func" : plane_func_from_complex_func(lambda c: c**2)
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

# TODO: Give drawn lines a bit of buffer, so that the rectangle's corners are filled in
class EquationSolver2d(ColorMappedByFuncScene):
    CONFIG = {
        "camera_config" : {"use_z_coordinate_for_display_order": True},
        "initial_lower_x" : -5.1,
        "initial_upper_x" : 5.1,
        "initial_lower_y" : -3.1,
        "initial_upper_y" : 3.1,
        "num_iterations" : 1,
        "num_checkpoints" : 10,
        "display_in_parallel" : True,
        "use_fancy_lines" : True,
        # TODO: Consider adding a "find_all_roots" flag, which could be turned off 
        # to only explore one of the two candidate subrectangles when both are viable
    }

    def construct(self):
        ColorMappedByFuncScene.construct(self)
        num_plane = self.num_plane
        self.remove(num_plane)

        # Clearing background
        self.camera.background_image = None
        self.camera.init_background()

        rev_func = lambda p : point_to_rev(self.func(p))
        clockwise_rev_func = lambda p : -rev_func(p)

        def Animate2dSolver(cur_depth, rect, dim_to_split, sides_to_draw = [0, 1, 2, 3]):
            print "Solver at depth: " + str(cur_depth)

            if cur_depth >= self.num_iterations:
                return empty_animation

            def draw_line_return_wind(start, end, start_wind, should_linger = False, draw_line = True):
                alpha_winder = make_alpha_winder(clockwise_rev_func, start, end, self.num_checkpoints)
                a0 = alpha_winder(0)
                rebased_winder = lambda alpha: alpha_winder(alpha) - a0 + start_wind
                thick_line = Line(num_plane.coords_to_point(*start), num_plane.coords_to_point(*end),
                    stroke_width = 10,
                    color = RED)
                if self.use_fancy_lines:
                    colored_line = thick_line.color_using_background_image(self.background_image_file)
                else:
                    colored_line = thick_line.set_stroke(width = 4)

                walker_anim = LinearWalker(
                    start_coords = start, 
                    end_coords = end,
                    coords_to_point = num_plane.coords_to_point,
                    rev_func = rev_func,
                    number_update_func = rebased_winder,
                    remover = True
                )

                if should_linger: # Do we need an "and not self.display_in_parallel" here?
                    rate_func = lingering
                else:
                    rate_func = None

                opt_line_anim = ShowCreation(colored_line) if draw_line else empty_animation

                line_draw_anim = AnimationGroup(
                    opt_line_anim, 
                    walker_anim,
                    rate_func = rate_func)
                return (line_draw_anim, rebased_winder(1))

            wind_so_far = 0
            anim = empty_animation
            sides = [
                rect.get_top(), 
                rect.get_right(), 
                rect.get_bottom(), 
                rect.get_left()
            ]
            for (i, (start, end)) in enumerate(sides):
                (next_anim, wind_so_far) = draw_line_return_wind(start, end, wind_so_far, 
                    should_linger = i == len(sides) - 1,
                    draw_line = i in sides_to_draw)
                anim = Succession(anim, next_anim)

            total_wind = round(wind_so_far)

            if total_wind == 0:
                coords = [
                    rect.get_top_left(), 
                    rect.get_top_right(), 
                    rect.get_bottom_right(), 
                    rect.get_bottom_left()
                ]
                points = np.array([num_plane.coords_to_point(x, y) for (x, y) in coords]) + 2 * IN
                # TODO: Maybe use diagonal lines or something to fill in rectangles indicating
                # their "Nothing here" status?
                # Or draw a large X or something
                fill_rect = polygonObject = Polygon(*points, fill_opacity = 0.8, color = DARK_BROWN)
                return Succession(anim, FadeIn(fill_rect))
            else:
                (sub_rect1, sub_rect2) = rect.splits_on_dim(dim_to_split)
                if dim_to_split == 0:
                    sub_rect_and_sides = [(sub_rect1, 1), (sub_rect2, 3)]
                else:
                    sub_rect_and_sides = [(sub_rect1, 2), (sub_rect2, 0)]
                sub_anims = [
                    Animate2dSolver(
                        cur_depth = cur_depth + 1,
                        rect = sub_rect,
                        dim_to_split = 1 - dim_to_split,
                        sides_to_draw = [side_to_draw]
                    )
                    for (sub_rect, side_to_draw) in sub_rect_and_sides
                ]
                mid_line_coords = rect.split_line_on_dim(dim_to_split)
                mid_line_points = [num_plane.coords_to_point(x, y)  + IN for (x, y) in mid_line_coords]
                # TODO: Have this match rectangle line style, apart from dashes and thin-ness?
                # Though there is also informational value in seeing the dashed line separately from rectangle lines
                mid_line = DashedLine(*mid_line_points)
                if self.display_in_parallel:
                    recursive_anim = AnimationGroup(*sub_anims) 
                else:
                    recursive_anim = Succession(*sub_anims)
                return Succession(anim, 
                    ShowCreation(mid_line),
                    recursive_anim
                )

        lower_x = self.initial_lower_x
        upper_x = self.initial_upper_x
        lower_y = self.initial_lower_y
        upper_y = self.initial_upper_y

        x_interval = (lower_x, upper_x)
        y_interval = (lower_y, upper_y)

        rect = RectangleData(x_interval, y_interval)

        print "Starting to compute anim"

        anim = Animate2dSolver(
            cur_depth = 0, 
            rect = rect,
            dim_to_split = 0,
        )

        print "Done computing anim"

        self.play(anim)

        self.wait()

# TODO: Perhaps have bullets (pulses) fade out and in at ends of line, instead of jarringly
# popping out and in?
#
# TODO: Perhaps have bullets change color corresponding to a function of their coordinates?
# This could involve some merging of functoinality with PiWalker
class LinePulser(ContinualAnimation):
    def __init__(self, line, bullet_template, num_bullets, pulse_time, output_func = None, **kwargs):
        self.line = line
        self.num_bullets = num_bullets
        self.pulse_time = pulse_time
        self.bullets = [bullet_template.copy() for i in range(num_bullets)]
        self.output_func = output_func
        ContinualAnimation.__init__(self, VGroup(line, VGroup(*self.bullets)), **kwargs)

    def update_mobject(self, dt):
        alpha = self.external_time % self.pulse_time
        start = self.line.get_start()
        end = self.line.get_end()
        for i in range(self.num_bullets):
            position = interpolate(start, end, 
                fdiv((i + alpha),(self.num_bullets)))
            self.bullets[i].move_to(position)
            if self.output_func:
                position_2d = (position[0], position[1])
                rev = point_to_rev(self.output_func(position_2d))
                color = rev_to_color(rev)
                self.bullets[i].set_color(color)

class ArrowCircleTest(Scene):
    def construct(self):
        circle_radius = 3
        circle = Circle(radius = circle_radius, color = WHITE)
        self.add(circle)

        base_arrow = Arrow(circle_radius * 0.7 * RIGHT, circle_radius * 1.3 * RIGHT)

        def rev_rotate(x, revs):
            x.rotate(revs * TAU, about_point = ORIGIN)
            x.set_color(rev_to_color(revs))
            return x

        num_arrows = 8 * 3

        # 0.5 - fdiv below so as to get a clockwise rotation from left
        arrows = [rev_rotate(base_arrow.copy(), 0.5 - (fdiv(i, num_arrows))) for i in range(num_arrows)]
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
        self.mobject.set_color(rev_to_color(angle_revs))

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
        
        num_display = DecimalNumber(0, include_background_rectangle = False).set_stroke(1)
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

#############
# Above are mostly general tools; here, we list, in order, finished or near-finished scenes

class FirstSqrtScene(EquationSolver1d):
    CONFIG = {
        "x_min" : 0,
        "x_max" : 2.5,
        "y_min" : 0,
        "y_max" : 2.5**2,
        "graph_origin" : 2.5*DOWN + 5.5*LEFT,
        "x_axis_width" : 12,
        "zoom_factor" : 3,
        "zoomed_canvas_center" : 2.25 * UP + 1.75 * LEFT,
        "func" : lambda x : x**2,
        "targetX" : np.sqrt(2),
        "targetY" : 2,
        "initial_lower_x" : 1,
        "initial_upper_x" : 2,
        "num_iterations" : 3,
        "iteration_at_which_to_start_zoom" : 3,
        "graph_label" : "y = x^2",
        "show_target_line" : True,
    }

FirstSqrtSceneConfig = FirstSqrtScene.CONFIG
shiftVal = FirstSqrtSceneConfig["targetY"]

class SecondSqrtScene(FirstSqrtScene):
        CONFIG = {
            "func" : lambda x : FirstSqrtSceneConfig["func"](x) - shiftVal,
            "targetY" : 0,
            "graph_label" : FirstSqrtSceneConfig["graph_label"] + " - " + str(shiftVal),
            "y_min" : FirstSqrtSceneConfig["y_min"] - shiftVal,
            "y_max" : FirstSqrtSceneConfig["y_max"] - shiftVal,
            "show_target_line" : False,
            # 0.96 hacked in by checking calculations above
            "graph_origin" : 0.96 * shiftVal * UP + FirstSqrtSceneConfig["graph_origin"],
        }

# TODO: Pi creatures intrigued

class RewriteEquation(Scene):
    def construct(self):
        # Can maybe fitz around with smoothening the transform, so just = goes to - and new stuff
        # is added at the right end, while things re-center
        f_old = TexMobject("f(x)")
        f_new = f_old.copy()
        equals_old = TexMobject("=")
        equals_old_2 = equals_old.copy()
        equals_new = equals_old.copy()
        g_old = TexMobject("g(x)")
        g_new = g_old.copy()
        minus_new = TexMobject("-")
        zero_new = TexMobject("0")
        f_old.next_to(equals_old, LEFT)
        g_old.next_to(equals_old, RIGHT)
        minus_new.next_to(g_new, LEFT)
        f_new.next_to(minus_new, LEFT)
        equals_new.next_to(g_new, RIGHT)
        zero_new.next_to(equals_new, RIGHT)
        
        self.add(f_old, equals_old, equals_old_2, g_old)
        self.wait()
        self.play(
            ReplacementTransform(f_old, f_new),
            ReplacementTransform(equals_old, equals_new), 
            ReplacementTransform(g_old, g_new), 
            ReplacementTransform(equals_old_2, minus_new),
            ShowCreation(zero_new),
        )
        self.wait()

class SignsExplanation(Scene):
    def construct(self):
        num_line = NumberLine(stroke_width = 1)
        largest_num = 10
        num_line.add_numbers(*range(-largest_num, largest_num + 1))
        self.add(num_line)
        self.wait()

        pos_num = 3
        neg_num = -pos_num

        pos_arrow = Arrow(
                num_line.number_to_point(0), 
                num_line.number_to_point(pos_num),
                buff = 0,
                color = positive_color)
        neg_arrow = Arrow(
                num_line.number_to_point(0), 
                num_line.number_to_point(neg_num),
                buff = 0,
                color = negative_color)
        
        #num_line.add_numbers(pos_num)
        self.play(ShowCreation(pos_arrow))

        #num_line.add_numbers(neg_num)
        self.play(ShowCreation(neg_arrow))

class VectorField(Scene):
    CONFIG = {
        "func" : plane_func_from_complex_func(lambda p : p**2 + 2),
        "granularity" : 10,
        "arrow_scale_factor" : 0.1,
        "normalized_arrow_scale_factor" : 5
    }

    def construct(self):
        num_plane = NumberPlane()
        self.add(num_plane)

        x_min, y_min = num_plane.point_to_coords(SPACE_WIDTH * LEFT + SPACE_HEIGHT * UP)
        x_max, y_max = num_plane.point_to_coords(SPACE_WIDTH * RIGHT + SPACE_HEIGHT * DOWN)

        x_points = np.linspace(x_min, x_max, self.granularity)
        y_points = np.linspace(y_min, y_max, self.granularity)
        points = it.product(x_points, y_points)

        sized_arrows = Group()
        unsized_arrows = Group()
        for (x, y) in points:
            output = self.func((x, y))
            output_size = np.sqrt(sum(output**2))
            normalized_output = output * fdiv(self.normalized_arrow_scale_factor, output_size) # Assume output has nonzero size here
            arrow = Vector(output * self.arrow_scale_factor)
            normalized_arrow = Vector(normalized_output * self.arrow_scale_factor)
            arrow.move_to(num_plane.coords_to_point(x, y))
            normalized_arrow.move_to(arrow)
            sized_arrows.add(arrow)
            unsized_arrows.add(normalized_arrow)

        self.add(sized_arrows)
        self.wait()

        self.play(ReplacementTransform(sized_arrows, unsized_arrows))
        self.wait()

class HasItsLimitations(Scene):
    def construct(self):
        num_line = NumberLine()
        num_line.add_numbers()
        self.add(num_line)

        self.wait()

        num_plane = NumberPlane()
        num_plane.add_coordinates()

        self.play(FadeOut(num_line), FadeIn(num_plane))

        self.wait()

        complex_plane = ComplexPlane()
        complex_plane.add_coordinates()
        
        self.play(FadeOut(num_plane), FadeIn(complex_plane))
        

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
    CONFIG = {
        "output_func" : plane_poly_with_roots((1, 1))
    }

    def PulsedLine(self, 
        start, end, 
        bullet_template, 
        num_bullets = 4, 
        pulse_time = 1, 
        **kwargs):
        line = Line(start, end, **kwargs)
        anim = LinePulser(
            line = line, 
            bullet_template = bullet_template, 
            num_bullets = num_bullets, 
            pulse_time = pulse_time, 
            output_func = self.output_func,
            **kwargs)
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
        "func" : plane_poly_with_roots((1, 2), (-1, 1.5), (-1, 1.5)),
        "num_iterations" : 5,
        "display_in_parallel" : True,
        "use_fancy_lines" : False,
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

class CombineInterval(Scene):
    def construct(self):
        plus_sign = TexMobject("+", fill_color = positive_color)
        minus_sign = TexMobject("-", fill_color = negative_color)

        left_point = Dot(LEFT, color = positive_color)
        right_point = Dot(RIGHT, color = negative_color)
        line1 = Line(LEFT, RIGHT)
        interval1 = Group(line1, left_point, right_point)

        plus_sign.next_to(left_point, UP)
        minus_sign.next_to(right_point, UP)

        self.add(interval1, plus_sign, minus_sign)
        self.wait()
        self.play(
            CircleIndicate(plus_sign),
            CircleIndicate(minus_sign),
        )
        self.wait()

        mid_point = Dot(ORIGIN, color = GREY)

        question_mark = TexMobject("?", fill_color = GREY)
        plus_sign_copy = plus_sign.copy()
        minus_sign_copy = minus_sign.copy()
        new_signs = Group(question_mark, plus_sign_copy, minus_sign_copy)
        for sign in new_signs: sign.next_to(mid_point, UP)

        self.play(FadeIn(mid_point), FadeIn(question_mark))
        self.wait()

        self.play(
            ApplyMethod(mid_point.set_color, positive_color),
            ReplacementTransform(question_mark, plus_sign_copy),
        )
        self.play(
            CircleIndicate(plus_sign_copy),
            CircleIndicate(minus_sign),
        )

        self.wait()

        self.play(
            ApplyMethod(mid_point.set_color, negative_color),
            ReplacementTransform(plus_sign_copy, minus_sign_copy),
        )
        self.play(
            CircleIndicate(minus_sign_copy),
            CircleIndicate(plus_sign),
        )

        self.wait()

class CombineInterval2(Scene):
    def construct(self):
        plus_sign = TexMobject("+", fill_color = positive_color)

        def make_interval(a, b):
            line = Line(a, b)
            start_dot = Dot(a, color = positive_color)
            end_dot = Dot(b, color = positive_color)
            start_sign = plus_sign.copy().next_to(start_dot, UP)
            end_sign = plus_sign.copy().next_to(end_dot, UP)
            return Group(start_sign, end_sign, line, start_dot, end_dot)

        def pair_indicate(a, b):
            self.play(
                CircleIndicate(a),
                CircleIndicate(b)
            )

        left_interval = make_interval(2 * LEFT, LEFT)
        right_interval = make_interval(RIGHT, 2 * RIGHT)

        self.play(FadeIn(left_interval), FadeIn(right_interval))

        pair_indicate(left_interval[0], left_interval[1])

        pair_indicate(right_interval[0], right_interval[1])

        self.play(
            ApplyMethod(left_interval.shift, RIGHT),
            ApplyMethod(right_interval.shift, LEFT),
        )

        pair_indicate(left_interval[0], right_interval[1])

        self.wait()

# TODO: Brouwer's fixed point theorem visuals
# class BFTScene(Scene):

# TODO: Pi creatures wide-eyed in amazement

#################

# TODOs, from easiest to hardest:

# Minor fiddling with little things in each animation; placements, colors, timing, text

# Initial odometer scene (simple once previous Pi walker scene is decided upon)

# Writing new Pi walker scenes by parametrizing general template

# Domain coloring scenes by parametrizing general template

# (All the above are basically trivial tinkering at this point)

# ----

# Pi creature emotion stuff

# BFT visuals

# Borsuk-Ulam visuals

# TODO: Add to camera an option for lower-quality (faster-rendered) background than pixel_array, 
# helpful for previews

####################

# Random test scenes and test functions go here:

def rect_to_circle((x, y, z)):
    size = np.sqrt(x**2 + y**2)
    max_abs_size = max(abs(x), abs(y))
    return fdiv(np.array((x, y, z)) * max_abs_size, size)

class MapPiWalkerRect(PiWalkerRect):
    CONFIG = {
        "camera_class" : MappingCamera,
        "camera_config" : {"mapping_func" : rect_to_circle},
        "display_output_color_map" : True
    }

class ShowBack(PiWalkerRect):
    CONFIG = {
         "func" : plane_poly_with_roots((1, 2), (-1, 1.5), (-1, 1.5))
    }

class Diagnostic(Scene):
    def construct(self):
        testList = map( (lambda n : (n, rev_to_rgba(n))), [0, 0.25, 0.5, 0.9])
        print "rev_to_rgbas", testList
        self.wait()

# FIN