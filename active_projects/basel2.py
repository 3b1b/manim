#!/usr/bin/env python

from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.continual_animation import *

from animation.playground import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.number_line import *
from topics.numerals import *
#from topics.combinatorics import *
from scene import Scene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *
from topics.three_dimensions import *

from topics.light import *

import types
import functools

LIGHT_COLOR = YELLOW
INDICATOR_RADIUS = 0.7
INDICATOR_STROKE_WIDTH = 1
INDICATOR_STROKE_COLOR = WHITE
INDICATOR_TEXT_COLOR = WHITE
INDICATOR_UPDATE_TIME = 0.2
FAST_INDICATOR_UPDATE_TIME = 0.1
OPACITY_FOR_UNIT_INTENSITY = 0.2
SWITCH_ON_RUN_TIME = 1.5
FAST_SWITCH_ON_RUN_TIME = 0.1
NUM_LEVELS = 30
NUM_CONES = 7 # in first lighthouse scene
NUM_VISIBLE_CONES = 5 # ibidem
ARC_TIP_LENGTH = 0.2
AMBIENT_FULL = 0.5
AMBIENT_DIMMED = 0.2
SPOTLIGHT_FULL = 0.9
SPOTLIGHT_DIMMED = 0.2

LIGHT_COLOR = YELLOW
DEGREES = TAU/360

inverse_power_law = lambda maxint,scale,cutoff,exponent: \
    (lambda r: maxint * (cutoff/(r/scale+cutoff))**exponent)
inverse_quadratic = lambda maxint,scale,cutoff: inverse_power_law(maxint,scale,cutoff,2)


A = np.array([5.,-3.,0.])
B = np.array([-5.,3.,0.])
C = np.array([-5.,-3.,0.])
xA = A[0]
yA = A[1]
xB = B[0]
yB = B[1]
xC = C[0]
yC = C[1]

# find the coords of the altitude point H
# as the solution of a certain LSE
prelim_matrix = np.array([[yA - yB, xB - xA], [xA - xB, yA - yB]]) # sic
prelim_vector = np.array([xB * yA - xA * yB, xC * (xA - xB) + yC * (yA - yB)])
H2 = np.linalg.solve(prelim_matrix,prelim_vector)
H = np.append(H2, 0.)




class AngleUpdater(ContinualAnimation):
    def __init__(self, angle_arc, spotlight, **kwargs):
        self.angle_arc = angle_arc

        self.spotlight = spotlight
        ContinualAnimation.__init__(self, self.angle_arc, **kwargs)

    def update_mobject(self, dt):
        new_arc = self.angle_arc.copy().set_bound_angles(
            start = self.spotlight.start_angle(),
            stop = self.spotlight.stop_angle()
        )
        new_arc.generate_points()
        new_arc.move_arc_center_to(self.spotlight.get_source_point())
        self.angle_arc.points = new_arc.points
        self.angle_arc.add_tip(
            tip_length = ARC_TIP_LENGTH,
            at_start = True, at_end = True
        )

class LightIndicator(Mobject):
    CONFIG = {
        "radius": 0.5,
        "reading_height" : 0.25,
        "intensity": 0,
        "opacity_for_unit_intensity": 1,
        "fill_color" : YELLOW,
        "precision": 3,
        "show_reading": True,
        "measurement_point": ORIGIN,
        "light_source": None
    }

    def generate_points(self):
        self.background = Circle(color=BLACK, radius = self.radius)
        self.background.set_fill(opacity = 1.0)
        self.foreground = Circle(color=self.color, radius = self.radius)
        self.foreground.set_stroke(
            color=INDICATOR_STROKE_COLOR,
            width=INDICATOR_STROKE_WIDTH
        )
        self.foreground.set_fill(color = self.fill_color)

        self.add(self.background, self.foreground)
        self.reading = DecimalNumber(self.intensity,num_decimal_points = self.precision)
        self.reading.set_fill(color=INDICATOR_TEXT_COLOR)
        self.reading.scale_to_fit_height(self.reading_height)
        self.reading.move_to(self.get_center())
        if self.show_reading:
            self.add(self.reading)

    def set_intensity(self, new_int):
        self.intensity = new_int
        new_opacity = min(1, new_int * self.opacity_for_unit_intensity)
        self.foreground.set_fill(opacity=new_opacity)
        ChangeDecimalToValue(self.reading, new_int).update(1)
        if new_int > 1.1:
            self.reading.set_fill(color = BLACK)
        else:
            self.reading.set_fill(color = WHITE)
        return self

    def get_measurement_point(self):
        if self.measurement_point != None:
            return self.measurement_point
        else:
            return self.get_center()

    def measured_intensity(self):
        distance = np.linalg.norm(
            self.get_measurement_point() - 
            self.light_source.get_source_point()
        )
        intensity = self.light_source.opacity_function(distance) / self.opacity_for_unit_intensity
        return intensity

    def continual_update(self):
        if self.light_source == None:
            print "Indicator cannot update, reason: no light source found"
        self.set_intensity(self.measured_intensity())

class UpdateLightIndicator(AnimationGroup):

    def __init__(self, indicator, intensity, **kwargs):
        if not isinstance(indicator,LightIndicator):
            raise Exception("This transform applies only to LightIndicator")
        
        target_foreground = indicator.copy().set_intensity(intensity).foreground
        change_opacity = Transform(
            indicator.foreground, target_foreground
        )
        changing_decimal = ChangeDecimalToValue(indicator.reading, intensity)

        AnimationGroup.__init__(self, changing_decimal, change_opacity, **kwargs)
        self.mobject = indicator

class ContinualLightIndicatorUpdate(ContinualAnimation):
    def update_mobject(self,dt):
        self.mobject.continual_update()

def copy_func(f):
    """Based on http://stackoverflow.com/a/6528148/190597 (Glenn Maynard)"""
    g = types.FunctionType(f.func_code, f.func_globals, name=f.func_name,
                           argdefs=f.func_defaults,
                           closure=f.func_closure)
    g = functools.update_wrapper(g, f)
    return g

class ScaleLightSources(Transform):

    def __init__(self, light_sources_mob, factor, about_point = None, **kwargs):

        if about_point == None:
            about_point = light_sources_mob.get_center()

        ls_target = light_sources_mob.copy()

        for submob in ls_target:

            if type(submob) == LightSource:

                new_sp = submob.source_point.copy() # a mob
                new_sp.scale(factor,about_point = about_point)
                submob.move_source_to(new_sp.get_location())

                #ambient_of = copy_func(submob.ambient_light.opacity_function)
                #new_of = lambda r: ambient_of(r/factor)
                #submob.ambient_light.opacity_function = new_of

                #spotlight_of = copy_func(submob.ambient_light.opacity_function)
                #new_of = lambda r: spotlight_of(r/factor)
                #submob.spotlight.change_opacity_function(new_of)

                new_r = factor * submob.radius
                submob.set_radius(new_r)

                new_r = factor * submob.ambient_light.radius
                submob.ambient_light.radius = new_r

                new_r = factor * submob.spotlight.radius
                submob.spotlight.radius = new_r

                submob.ambient_light.scale_about_point(factor, new_sp.get_center())
                submob.spotlight.scale_about_point(factor, new_sp.get_center())


        Transform.__init__(self,light_sources_mob,ls_target,**kwargs)


###

class ThinkAboutPondScene(PiCreatureScene):
    CONFIG = {
        "default_pi_creature_class" : Randolph,
    }
    def construct(self):
        randy = self.pi_creature
        randy.to_corner(DOWN+LEFT)
        bubble = ThoughtBubble(
            width = 9,
            height = 5,
        )
        circles = bubble[:3]
        angle = -15*DEGREES
        circles.rotate(angle, about_point = bubble.get_bubble_center())
        circles.shift(LARGE_BUFF*LEFT)
        for circle in circles:
            circle.rotate(-angle)
        bubble.pin_to(randy)
        bubble.shift_onto_screen()

        self.play(
            randy.change, "thinking",
            ShowCreation(bubble)
        )
        self.wait(2)
        self.play(randy.change, "happy", bubble)
        self.wait(2)
        self.play(randy.change, "hooray", bubble)
        self.wait(2)

class IntroScene(PiCreatureScene):
    CONFIG = {
        "rect_height" : 0.075,
        "duration" : 1.0,
        "eq_spacing" : 3 * MED_LARGE_BUFF,
        "n_rects_to_show" : 30,
    }

    def construct(self):
        randy = self.get_primary_pi_creature()
        randy.scale(0.7).to_corner(DOWN+RIGHT)

        self.build_up_euler_sum()
        self.show_history()
        # self.other_pi_formulas()
        # self.refocus_on_euler_sum()

    def build_up_euler_sum(self):
        morty = self.pi_creature
        euler_sum = self.euler_sum = TexMobject(
           "1", "+", 
           "{1 \\over 4}", "+",
           "{1 \\over 9}", "+",
           "{1 \\over 16}", "+",
           "{1 \\over 25}", "+",
           "\\cdots", "=",
            arg_separator = " \\, "
        )
        equals_sign = euler_sum.get_part_by_tex("=")
        plusses = euler_sum.get_parts_by_tex("+")
        term_mobjects = euler_sum.get_parts_by_tex("1")

        self.euler_sum.to_edge(UP)
        self.euler_sum.shift(2*LEFT)
       
        max_n = self.n_rects_to_show
        terms = [1./(n**2) for n in range(1, max_n + 1)]
        series_terms = list(np.cumsum(terms))
        series_terms.append(np.pi**2/6) ##Just force this up there

        partial_sum_decimal = self.partial_sum_decimal = DecimalNumber(
            series_terms[1],
            num_decimal_points = 2
        )
        partial_sum_decimal.next_to(equals_sign, RIGHT)

        ## Number line

        number_line = self.number_line = NumberLine(
            x_min = 0,
            color = WHITE,
            number_at_center = 1,
            stroke_width = 1,
            numbers_with_elongated_ticks = [0,1,2,3],
            numbers_to_show = np.arange(0,5),
            unit_size = 5,
            tick_frequency = 0.2,
            line_to_number_buff = MED_LARGE_BUFF
        )
        number_line.add_numbers()
        number_line.to_edge(LEFT)
        number_line.shift(MED_LARGE_BUFF*UP)

        # create slabs for series terms

        lines = VGroup()
        rects = self.rects = VGroup()
        rect_labels = VGroup()
        slab_colors = it.cycle([YELLOW, BLUE])
        rect_anims = []
        rect_label_anims = []

        for i, t1, t2 in zip(it.count(1), [0]+series_terms, series_terms):
            color = slab_colors.next()
            line = Line(*map(number_line.number_to_point, [t1, t2]))
            rect = Rectangle(
                stroke_width = 0,
                fill_opacity = 1,
                fill_color = color
            )
            rect.match_width(line)
            rect.stretch_to_fit_height(self.rect_height)
            rect.move_to(line)

            if i <= 5:
                if i == 1:
                    rect_label = TexMobject("1")
                else:
                    rect_label = TexMobject("\\frac{1}{%d}"%(i**2))
                    rect_label.scale(0.75)
                max_width = 0.7*rect.get_width()
                if rect_label.get_width() > max_width:
                    rect_label.scale_to_fit_width(max_width)
                rect_label.next_to(rect, UP, buff = MED_LARGE_BUFF/(i+1))

                term_mobject = term_mobjects[i-1]
                rect_anim = GrowFromPoint(rect, term_mobject.get_center())
                rect_label_anim = ReplacementTransform(
                    term_mobject.copy(), rect_label
                )
            else:
                rect_label = VectorizedPoint()
                rect_anim = GrowFromPoint(rect, rect.get_left())
                rect_label_anim = FadeIn(rect_label)

            rects.add(rect)
            rect_labels.add(rect_label)
            rect_anims.append(rect_anim)
            rect_label_anims.append(rect_label_anim)
            lines.add(line)
        dots = TexMobject("\\dots").scale(0.5)
        last_rect = rect_anims[-1].target_mobject
        dots.scale_to_fit_width(0.9*last_rect.get_width())
        dots.move_to(last_rect, UP+RIGHT)
        rects.submobjects[-1] = dots
        rect_anims[-1] = FadeIn(dots)

        self.add(number_line)
        self.play(FadeIn(euler_sum[0]))
        self.play(
            rect_anims[0],
            rect_label_anims[0]
        )
        for i in range(4):
            self.play(
                FadeIn(term_mobjects[i+1]),
                FadeIn(plusses[i]),
            )
            anims = [
                rect_anims[i+1],
                rect_label_anims[i+1],
            ]
            if i == 0:
                anims += [
                    FadeIn(equals_sign),
                    FadeIn(partial_sum_decimal)
                ]
            elif i <= 5:
                anims += [
                    ChangeDecimalToValue(
                        partial_sum_decimal,
                        series_terms[i+1], 
                        run_time = 1,
                        num_decimal_points = 6,
                        position_update_func = lambda m: m.next_to(equals_sign, RIGHT)
                    )
                ]
            self.play(*anims)

        for i in range(4, len(series_terms)-2):
            anims = [
                rect_anims[i+1],
                ChangeDecimalToValue(
                    partial_sum_decimal,
                    series_terms[i+1],
                    num_decimal_points = 6,
                ),
            ]
            if i == 5:
                anims += [
                    FadeIn(euler_sum[-3]), # +
                    FadeIn(euler_sum[-2]), # ...
                ]
            self.play(*anims, run_time = 2./i)

        brace = self.brace = Brace(partial_sum_decimal, DOWN)
        q_marks = self.q_marks = TextMobject("???")
        q_marks.next_to(brace, DOWN)
        q_marks.highlight(LIGHT_COLOR)

        self.play(
            GrowFromCenter(brace),
            Write(q_marks),
            ChangeDecimalToValue(
                partial_sum_decimal,
                series_terms[-1],
                num_decimal_points = 6,
            ),
            morty.change, "confused",
        )
        self.wait()

        self.number_line_group = VGroup(
            number_line, rects, rect_labels
        )

    def show_history(self):
        # Pietro Mengoli in 1644
        morty = self.pi_creature
        pietro = ImageMobject("Pietro_Mengoli")
        euler = ImageMobject("Euler")

        pietro_words = TextMobject("Challenge posed by \\\\ Pietro Mengoli in 1644")
        pietro_words.scale(0.75)
        pietro_words.next_to(pietro, DOWN)
        pietro.add(pietro_words)

        euler_words = TextMobject("Solved by Leonard \\\\ Euler in 1735")
        euler_words.scale(0.75)
        euler_words.next_to(euler, DOWN)
        euler.add(euler_words)

        pietro.next_to(SPACE_WIDTH*LEFT, LEFT)
        euler.next_to(SPACE_WIDTH*RIGHT, RIGHT)

        pi_answer = self.pi_answer = TexMobject("{\\pi^2 \\over 6}")
        pi_answer.highlight(YELLOW)
        pi_answer.move_to(self.partial_sum_decimal, LEFT)
        equals_sign = TexMobject("=")
        equals_sign.next_to(pi_answer, RIGHT)
        pi_answer.shift(SMALL_BUFF*UP)
        self.partial_sum_decimal.generate_target()
        self.partial_sum_decimal.target.next_to(equals_sign, RIGHT)

        pi = pi_answer[0]
        pi_rect = SurroundingRectangle(pi, color = RED)
        pi_rect.save_state()
        pi_rect.scale_to_fit_height(SPACE_HEIGHT)
        pi_rect.center()
        pi_rect.set_stroke(width = 0)
        squared = pi_answer[1]
        squared_rect = SurroundingRectangle(squared, color = BLUE)

        brace = Brace(
            VGroup(self.euler_sum, self.partial_sum_decimal.target),
            DOWN, buff = SMALL_BUFF
        )
        basel_text = brace.get_text("Basel problem", buff = SMALL_BUFF)

        self.number_line_group.save_state()
        self.play(
            pietro.next_to, ORIGIN, LEFT, LARGE_BUFF,
            self.number_line_group.next_to, SPACE_HEIGHT*DOWN, DOWN,
            morty.change, "pondering",
        )
        self.wait(2)
        self.play(euler.next_to, ORIGIN, RIGHT, LARGE_BUFF)
        self.wait(2)
        self.play(
            ReplacementTransform(self.q_marks, pi_answer),
            FadeIn(equals_sign),
            FadeOut(self.brace),
            MoveToTarget(self.partial_sum_decimal)
        )
        self.wait()
        self.play(morty.change, "surprised")
        self.play(pi_rect.restore)
        self.wait()
        self.play(Transform(pi_rect, squared_rect))
        self.play(FadeOut(pi_rect))
        self.play(morty.change, "hesitant")
        self.wait(2)
        self.play(
            GrowFromCenter(brace),
            euler.to_edge, DOWN,
            pietro.to_edge, DOWN,
            self.number_line_group.restore,
            self.number_line_group.shift, LARGE_BUFF*RIGHT,
        )
        self.play(Write(basel_text))
        self.play(morty.change, "happy")
        self.wait(4)

    def other_pi_formulas(self):

        self.play(
            FadeOut(self.rects),
            FadeOut(self.number_line)
        )

        self.leibniz_sum = TexMobject(
            "1-{1\\over 3}+{1\\over 5}-{1\\over 7}+{1\\over 9}-\\cdots",
            "=", "{\\pi \\over 4}")

        self.wallis_product = TexMobject(
            "{2\\over 1} \\cdot {2\\over 3} \\cdot {4\\over 3} \\cdot {4\\over 5}" +
             "\\cdot {6\\over 5} \\cdot {6\\over 7} \\cdots",
             "=", "{\\pi \\over 2}")

        self.leibniz_sum.next_to(self.euler_sum.get_part_by_tex("="), DOWN,
            buff = self.eq_spacing,
            submobject_to_align = self.leibniz_sum.get_part_by_tex("=")
        )

        self.wallis_product.next_to(self.leibniz_sum.get_part_by_tex("="), DOWN,
            buff = self.eq_spacing,
            submobject_to_align = self.wallis_product.get_part_by_tex("=")
        )


        self.play(
            Write(self.leibniz_sum)
        )
        self.play(
            Write(self.wallis_product)
        )

    def refocus_on_euler_sum(self):

        self.euler_sum.add(self.pi_answer)

        self.play(
            FadeOut(self.leibniz_sum),
            FadeOut(self.wallis_product),
            ApplyMethod(self.euler_sum.shift,
                ORIGIN + 2*UP - self.euler_sum.get_center())
        )

        # focus on pi squared
        pi_squared = self.euler_sum.get_part_by_tex("\\pi")[-3]
        self.play(
            ScaleInPlace(pi_squared,2,rate_func = wiggle)
        )



        # Morty thinks of a circle

        q_circle = Circle(
            stroke_color = YELLOW,
            fill_color = YELLOW,
            fill_opacity = 0.5,
            radius = 0.4, 
            stroke_width = 10.0
        )
        q_mark = TexMobject("?")
        q_mark.next_to(q_circle)

        thought = Group(q_circle, q_mark)
        q_mark.scale_to_fit_height(0.8 * q_circle.get_height())
        self.pi_creature_thinks(thought,target_mode = "confused",
            bubble_kwargs = { "height" : 2, "width" : 3 })

        self.wait()

class PiHidingWrapper(Scene):
    def construct(self):
        title = TextMobject("Pi hiding in prime regularities")
        title.to_edge(UP)
        screen = ScreenRectangle(height = 6)
        screen.next_to(title, DOWN)
        self.add(title)
        self.play(ShowCreation(screen))
        self.wait(2)

class MathematicalWebOfConnections(PiCreatureScene):
    def construct(self):
        self.complain_that_pi_is_not_about_circles()
        self.show_other_pi_formulas()
        self.question_fundamental()
        self.draw_circle()
        self.remove_all_but_basel_sum()
        self.show_web_of_connections()
        self.show_light()

    def complain_that_pi_is_not_about_circles(self):
        jerk, randy = self.pi_creatures

        words = self.words = TextMobject(
            "$\\pi$ is not",
            "fundamentally \\\\", 
            "about circles"
        )
        words.highlight_by_tex("fundamentally", YELLOW)

        self.play(PiCreatureSays(
            jerk, words,
            target_mode = "angry"
        ))
        self.play(randy.change, "guilty")
        self.wait(2)

    def show_other_pi_formulas(self):
        jerk, randy = self.pi_creatures
        words = self.words

        basel_sum = TexMobject(
            "1 + {1 \\over 4} + {1 \\over 9} + {1 \\over 16} + \\cdots", 
            "=", "{\\pi^2 \\over 6}"
        )
        leibniz_sum = TexMobject(
            "1-{1\\over 3}+{1\\over 5}-{1\\over 7}+{1\\over 9}-\\cdots",
            "=", "{\\pi \\over 4}")

        wallis_product = TexMobject(
            "{2\\over 1} \\cdot {2\\over 3} \\cdot {4\\over 3} \\cdot {4\\over 5}" +
             "\\cdot {6\\over 5} \\cdot {6\\over 7} \\cdots",
             "=", "{\\pi \\over 2}")

        basel_sum.move_to(randy)
        basel_sum.to_edge(UP)
        basel_equals = basel_sum.get_part_by_tex("=")

        formulas = VGroup(basel_sum, leibniz_sum, wallis_product)
        formulas.scale(0.75)
        formulas.arrange_submobjects(DOWN, buff = MED_LARGE_BUFF)
        for formula in formulas:
            basel_equals_x = basel_equals.get_center()[0]
            formula_equals_x = formula.get_part_by_tex("=").get_center()[0]
            formula.shift((basel_equals_x - formula_equals_x)*RIGHT)

        formulas.move_to(randy)
        formulas.to_edge(UP)
        formulas.shift_onto_screen()
        self.formulas = formulas

        self.play(
            jerk.change, "sassy",
            randy.change, "raise_right_hand",
            FadeOut(jerk.bubble),
            words.next_to, jerk, UP,
            FadeIn(basel_sum, submobject_mode = "lagged_start", run_time = 3)
        )
        for formula in formulas[1:]:
            self.play(
                FadeIn(
                    formula, 
                    submobject_mode = "lagged_start", 
                    run_time = 3
                ),
            )
        self.wait()

    def question_fundamental(self):
        jerk, randy = self.pi_creatures
        words = self.words
        fundamentally = words.get_part_by_tex("fundamentally")
        words.remove(fundamentally)

        self.play(
            fundamentally.move_to, self.pi_creatures,
            fundamentally.shift, UP,
            FadeOut(words),
            jerk.change, "pondering",
            randy.change, "pondering",
        )
        self.wait()

        question = TextMobject("Does this mean \\\\ anything?")
        question.scale(0.8)
        question.set_stroke(WHITE, 0.5)
        question.next_to(fundamentally, DOWN, LARGE_BUFF)
        arrow = Arrow(question, fundamentally)
        arrow.highlight(WHITE)

        self.play(
            FadeIn(question),
            GrowArrow(arrow)
        )
        self.wait()

        fundamentally.add(question, arrow)
        self.fundamentally = fundamentally

    def draw_circle(self):
        semi_circle = Arc(angle = np.pi, radius = 2)
        radius = Line(ORIGIN, semi_circle.points[0])
        radius.highlight(BLUE)
        semi_circle.highlight(YELLOW)

        VGroup(radius, semi_circle).move_to(
            SPACE_WIDTH*LEFT/2 + SPACE_HEIGHT*UP/2,
        )

        decimal = DecimalNumber(0)
        def decimal_position_update_func(decimal):
            decimal.move_to(semi_circle.points[-1])
            decimal.shift(0.3*radius.get_vector())

        one = TexMobject("1")
        one.next_to(radius, UP)

        self.play(ShowCreation(radius), FadeIn(one))
        self.play(
            Rotate(radius, np.pi, about_point = radius.get_start()),
            ShowCreation(semi_circle),
            ChangeDecimalToValue(
                decimal, np.pi, 
                position_update_func = decimal_position_update_func
            ),
            MaintainPositionRelativeTo(one, radius),
            run_time = 3,
        )
        self.wait(2)

        self.circle_group = VGroup(semi_circle, radius, one, decimal)

    def remove_all_but_basel_sum(self):
        to_shift_down = VGroup(
            self.circle_group, self.pi_creatures,
            self.fundamentally, self.formulas[1:],
        )
        to_shift_down.generate_target()
        for part in to_shift_down.target:
            part.move_to(2*SPACE_HEIGHT*DOWN)

        basel_sum = self.formulas[0]

        self.play(
            MoveToTarget(to_shift_down),
            basel_sum.scale, 1.5,
            basel_sum.move_to, 1.5*DOWN,
        )

        self.basel_sum = basel_sum

    def show_web_of_connections(self):
        self.remove(self.pi_creatures)
        title = TextMobject("Interconnected web of mathematics")
        title.to_edge(UP)
        basel_sum = self.basel_sum

        dots = VGroup(*[
            Dot(radius = 0.1).move_to(
                (j - 0.5*(i%2))*RIGHT + \
                (np.sqrt(3)/2.0)* i*DOWN + \
                0.5*(random.random()*RIGHT + random.random()*UP),
            )
            for i in range(4)
            for j in range(7+(i%2))
        ])
        dots.scale_to_fit_height(3)
        dots.next_to(title, DOWN, MED_LARGE_BUFF)
        edges = VGroup()
        for x in range(100):
            d1, d2 = random.sample(dots, 2)
            edge = Line(d1.get_center(), d2.get_center())
            edge.set_stroke(YELLOW, 0.5)
            edges.add(edge)

        ## Choose special path
        path_dots = VGroup(
            dots[-7],
            dots[-14],
            dots[9],
            dots[19],
            dots[14],
        )
        path_edges = VGroup(*[
            Line(
                d1.get_center(), d2.get_center(),
                color = RED
            )
            for d1, d2 in zip(path_dots, path_dots[1:])
        ])

        circle = Circle(color = YELLOW, radius = 1)
        radius = Line(circle.get_center(), circle.get_right())
        radius.highlight(BLUE)
        VGroup(circle, radius).next_to(path_dots[-1], RIGHT)

        self.play(
            Write(title),
            LaggedStart(ShowCreation, edges, run_time = 3),
            LaggedStart(GrowFromCenter, dots, run_time = 3)
        )
        self.play(path_dots[0].highlight, RED)
        for dot, edge in zip(path_dots[1:], path_edges):
            self.play(
                ShowCreation(edge),
                dot.highlight, RED
            )
        self.play(ShowCreation(radius))
        radius.set_points_as_corners(radius.get_anchors())
        self.play(
            ShowCreation(circle),
            Rotate(radius, angle = 0.999*TAU, about_point = radius.get_start()),
            run_time = 2
        )
        self.wait()

        graph = VGroup(dots, edges, path_edges, title)
        circle.add(radius)
        basel_sum.generate_target()
        basel_sum.target.to_edge(UP)

        arrow = Arrow(
            UP, DOWN, 
            rectangular_stem_width = 0.1,
            tip_length = 0.45,
            color = RED,
        )
        arrow.next_to(basel_sum.target, DOWN, buff = MED_LARGE_BUFF)

        self.play(
            MoveToTarget(basel_sum),
            graph.next_to, basel_sum.target, UP, LARGE_BUFF,
            circle.next_to, arrow, DOWN, MED_LARGE_BUFF,
        )
        self.play(GrowArrow(arrow))
        self.wait()

        self.arrow = arrow
        self.circle = circle

    def show_light(self):
        light = AmbientLight(
            num_levels = 500, radius = 13,
            opacity_function = lambda r : 1.0/(r+1),
        )
        pi = self.basel_sum[-1][0]
        pi.set_stroke(BLACK, 0.5)
        light.move_to(pi)
        self.play(
            SwitchOn(light, run_time = 3),
            Animation(self.arrow),
            Animation(self.circle),
            Animation(self.basel_sum),
        )
        self.wait()

    ###

    def create_pi_creatures(self):
        jerk = PiCreature(color = GREEN_D)
        randy = Randolph().flip()
        jerk.move_to(0.5*SPACE_WIDTH*LEFT).to_edge(DOWN)
        randy.move_to(0.5*SPACE_WIDTH*RIGHT).to_edge(DOWN)

        return VGroup(jerk, randy)

class FirstLighthouseScene(PiCreatureScene):
    CONFIG = {
        "num_levels" : 100,
        "opacity_function" : inverse_quadratic(1,2,1),
    }
    def construct(self):
        self.remove(self.pi_creature)
        self.show_lighthouses_on_number_line()
        self.describe_brightness_of_each()
        self.ask_about_rearrangements()

    def show_lighthouses_on_number_line(self):
        number_line = self.number_line = NumberLine(
            x_min = 0,
            color = WHITE,
            number_at_center = 1.6,
            stroke_width = 1,
            numbers_with_elongated_ticks = range(1,6),
            numbers_to_show = range(1,6),
            unit_size = 2,
            tick_frequency = 0.2,
            line_to_number_buff = LARGE_BUFF,
            label_direction = DOWN,
        )

        number_line.add_numbers()
        self.add(number_line)

        origin_point = number_line.number_to_point(0)

        morty = self.pi_creature
        morty.scale(0.75)
        morty.flip()
        right_pupil = morty.eyes[1]
        morty.next_to(origin_point, LEFT, buff = 0, submobject_to_align = right_pupil)


        light_sources = VGroup()
        for i in range(1,NUM_CONES+1):
            light_source = LightSource(
                opacity_function = self.opacity_function,
                num_levels = self.num_levels,
                radius = 12.0,
            )
            point = number_line.number_to_point(i)
            light_source.move_source_to(point)
            light_sources.add(light_source)

        lighthouses = self.lighthouses = VGroup(*[
            ls.lighthouse
            for ls in light_sources[:NUM_VISIBLE_CONES+1]
        ])

        morty.save_state()
        morty.scale(3)
        morty.fade(1)
        morty.center()
        self.play(morty.restore)
        self.play(
            morty.change, "pondering",
            LaggedStart(
                FadeIn, lighthouses,
                run_time = 1
            )
        )
        self.play(LaggedStart(
            SwitchOn, VGroup(*[
                ls.ambient_light
                for ls in light_sources
            ]),
            run_time = 5,
            lag_ratio = 0.1,
            rate_func = rush_into,
        ), Animation(lighthouses))
        self.wait()

        self.light_sources = light_sources

    def describe_brightness_of_each(self):
        number_line = self.number_line
        morty = self.pi_creature
        light_sources = self.light_sources
        lighthouses = self.lighthouses

        light_indicator = LightIndicator(
            radius = INDICATOR_RADIUS,
            opacity_for_unit_intensity = OPACITY_FOR_UNIT_INTENSITY,
            color = LIGHT_COLOR
        )
        light_indicator.reading.scale(0.8)
        light_indicator.set_intensity(0)
        intensities = np.cumsum(np.array([1./n**2 for n in range(1,NUM_CONES+1)]))
        opacities = intensities * light_indicator.opacity_for_unit_intensity

        bubble = ThoughtBubble(
            direction = RIGHT,
            width = 2.5, height = 3.5
        )
        bubble.pin_to(morty)
        bubble.add_content(light_indicator)

        euler_sum_above = TexMobject(
            "1", "+", 
            "{1\over 4}", "+", 
            "{1\over 9}", "+", 
            "{1\over 16}", "+", 
            "{1\over 25}", "+", 
            "{1\over 36}"
        )
        euler_sum_terms = euler_sum_above[::2]
        plusses = euler_sum_above[1::2]

        for i, term in enumerate(euler_sum_above):
            #horizontal alignment with tick marks
            term.next_to(number_line.number_to_point(0.5*i+1), UP , buff = 2)
            # vertical alignment with light indicator
            old_y = term.get_center()[1]
            new_y = light_indicator.get_center()[1]
            term.shift([0,new_y - old_y,0])

        # show limit value in light indicator and an equals sign
        limit_reading = TexMobject("{\pi^2 \over 6}")
        limit_reading.move_to(light_indicator.reading)

        equals_sign = TexMobject("=")
        equals_sign.next_to(morty, UP)
        old_y = equals_sign.get_center()[1]
        new_y = euler_sum_above.get_center()[1]
        equals_sign.shift([0,new_y - old_y,0])

        #Triangle of light to morty's eye
        ls0 = light_sources[0]
        ls0.save_state()
        eye = morty.eyes[1]
        triangle = Polygon(
            number_line.number_to_point(1),
            eye.get_top(), eye.get_bottom(),
            stroke_width = 0,
            fill_color = YELLOW,
            fill_opacity = 1,
        )
        triangle_anim = GrowFromPoint(
            triangle, triangle.get_right(), 
            point_color = YELLOW
        )

        # First lighthouse has apparent reading
        self.play(LaggedStart(FadeOut, light_sources[1:]))
        self.wait()
        self.play(
            triangle_anim,
            # Animation(eye)
        )
        for x in range(4):
            triangle_copy = triangle.copy()
            self.play(
                FadeOut(triangle.copy()),
                triangle_anim,
            )
        self.play(
            FadeOut(triangle),
            ShowCreation(bubble),
            FadeIn(light_indicator),
        )
        self.play(
            UpdateLightIndicator(light_indicator, 1),
            FadeIn(euler_sum_terms[0])
        )
        self.wait(2)

        # Second lighthouse is 1/4, third is 1/9, etc.
        for i in range(1, 5):
            self.play(
                ApplyMethod(
                    ls0.move_to, light_sources[i],
                    run_time = 3
                ),
                UpdateLightIndicator(light_indicator, 1./(i+1)**2, run_time = 3),
                FadeIn(
                    euler_sum_terms[i],
                    run_time = 3,
                    rate_func = squish_rate_func(smooth, 0.5, 1)
                ),
            )
            self.wait()
        self.play(
            ApplyMethod(ls0.restore),
            UpdateLightIndicator(light_indicator, 1)
        )

        #Switch them all on
        self.play(
            LaggedStart(FadeIn, lighthouses[1:]),
            morty.change, "hooray",
        )
        self.play(
            LaggedStart(
                SwitchOn, VGroup(*[
                    ls.ambient_light
                    for ls in light_sources[1:]
                ]),
                run_time = 5,
                rate_func = rush_into,
            ),
            Animation(lighthouses),
            Animation(euler_sum_above),
            Write(plusses),
            UpdateLightIndicator(light_indicator, np.pi**2/6, run_time = 5),
            morty.change, "happy",
        )
        self.wait()
        self.play(
            FadeOut(light_indicator.reading),
            FadeIn(limit_reading),
            morty.change, "confused",
        )
        self.play(Write(equals_sign))
        self.wait()

    def ask_about_rearrangements(self):
        light_sources = self.light_sources
        origin = self.number_line.number_to_point(0)
        morty = self.pi_creature

        self.play(
            LaggedStart(
                Rotate, light_sources,
                lambda m : (m, (2*random.random()-1)*90*DEGREES),
                about_point = origin, 
                rate_func = lambda t : wiggle(t, 4),
                run_time = 10,
                lag_ratio = 0.9,
            ), 
            morty.change, "pondering",
        )

class RearrangeWords(Scene):
    def construct(self):
        words = TextMobject("Rearrange without changing \\\\ the apparent brightness")
        self.play(Write(words))
        self.wait(5)

class ThatJustSeemsUseless(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "How would \\\\ that help?",
            target_mode = "sassy",
            student_index = 2,
            bubble_kwargs = {"direction" : LEFT},
        )
        self.play(
            self.teacher.change, "guilty",
            self.get_student_changes(*3*['sassy'])
        )
        self.wait()

class AskAboutBrightness(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "What do you mean \\\\ by ``brightness''?"
        )
        self.play(self.teacher.change, "happy")
        self.wait(3)

class IntroduceScreen(Scene):
    CONFIG = {
        "num_levels" : 100,
        "radius" : 10,
        "num_rays" : 250,
        "min_ray_angle" : 0,
        "max_ray_angle" : TAU,
    }
    def construct(self):
        self.setup_elements()
        self.setup_angle() # spotlight and angle msmt change when screen rotates
        self.rotate_screen()
        # self.morph_lighthouse_into_sun()

    def setup_elements(self):
        SCREEN_SIZE = 3.0
        source_point = self.source_point = 2.5*LEFT
        observer_point = 3.5*RIGHT
        # Light source

        light_source = self.light_source = LightSource(
            opacity_function = inverse_quadratic(1,2,1),
            num_levels = self.num_levels,
            radius = self.radius,
            max_opacity_ambient = AMBIENT_FULL,
        )

        light_source.move_source_to(source_point)

        # Screen

        screen = self.screen = Rectangle(
            width = 0.05,
            height = 2,
            mark_paths_closed = True,
            fill_color = WHITE,
            fill_opacity = 1.0,
            stroke_width = 0.0
        )

        screen.next_to(observer_point, LEFT)

        screen_label = TextMobject("Screen")
        screen_label.next_to(screen, UP+LEFT)
        screen_arrow = Arrow(
            screen_label.get_bottom(),
            screen.get_center(),
        )

        # Pi creature
        morty = Mortimer()
        morty.shift(screen.get_center() - morty.eyes.get_left())
        morty.look_at(source_point)

        # Camera
        camera = SVGMobject(file_name = "camera")
        camera.rotate(TAU/4)
        camera.scale_to_fit_height(1.5)
        camera.move_to(morty.eyes, LEFT)

        # Animations
        light_source.set_max_opacity_spotlight(0.001)
        screen_tracker = self.screen_tracker = ScreenTracker(light_source)

        self.add(light_source.lighthouse)
        self.play(SwitchOn(light_source.ambient_light))
        self.play(
            Write(screen_label),
            GrowArrow(screen_arrow),
            FadeIn(screen)
        )
        self.wait()
        self.play(*map(FadeOut, [screen_label, screen_arrow]))
        screen.save_state()
        self.play(
            FadeIn(morty),
            screen.match_height, morty.eyes,
            screen.next_to, morty.eyes, LEFT, SMALL_BUFF
        )
        self.play(Blink(morty))
        self.play(
            FadeOut(morty),
            FadeIn(camera),
            screen.scale, 2, {"about_edge" : UP},
        )
        self.wait()
        self.play(
            FadeOut(camera),
            screen.restore,
        )

        light_source.set_screen(screen)
        light_source.spotlight.opacity_function = lambda r : 0.2/(r+1)
        screen_tracker.update(0)

        ## Ask about proportion
        self.add_foreground_mobjects(light_source.shadow, screen)
        self.shoot_rays()

        ##
        self.play(SwitchOn(light_source.spotlight))

    def setup_angle(self):

        self.wait()

        # angle msmt (arc)
        arc_angle = self.light_source.spotlight.opening_angle()
        # draw arc arrows to show the opening angle
        self.angle_arc = Arc(
            radius = 3, 
            start_angle = self.light_source.spotlight.start_angle(),
            angle = self.light_source.spotlight.opening_angle(),
            tip_length = ARC_TIP_LENGTH
        )
        #angle_arc.add_tip(at_start = True, at_end = True)
        self.angle_arc.move_arc_center_to(self.light_source.get_source_point())
        

        # angle msmt (decimal number)

        self.angle_indicator = DecimalNumber(
            arc_angle / DEGREES,
            num_decimal_points = 0,
            unit = "^\\circ"
        )
        self.angle_indicator.next_to(self.angle_arc, RIGHT)

        angle_update_func = lambda x: self.light_source.spotlight.opening_angle() / DEGREES
        angle_tracker = ContinualChangingDecimal(
            self.angle_indicator, angle_update_func
        )
        self.add(angle_tracker)

        arc_tracker = AngleUpdater(
            self.angle_arc,
            self.light_source.spotlight
        )
        self.add(arc_tracker)

        self.play(
            ShowCreation(self.angle_arc),
            ShowCreation(self.angle_indicator)
        )

        self.wait()

    def rotate_screen(self):
        self.add(
            ContinualUpdateFromFunc(
                self.light_source,
                lambda m : m.update()
            ),
        )
        self.add(
            ContinualUpdateFromFunc(
                self.angle_indicator,
                lambda m : m.set_stroke(width = 0).set_fill(opacity = 1)
            )
        )
        self.remove(self.light_source.ambient_light)
        def rotate_screen(angle):
            self.play(
                Rotate(self.light_source.spotlight.screen, angle),
                Animation(self.angle_arc),
                run_time = 2,
            )
        for angle in TAU/8, -TAU/4, TAU/8, -TAU/6:
            rotate_screen(angle)
            self.wait()
        self.shoot_rays()
        rotate_screen(TAU/6)

    ##

    def shoot_rays(self, show_creation_kwargs = None):
        if show_creation_kwargs is None:
            show_creation_kwargs = {}
        source_point = self.source_point
        screen = self.screen

        # Rays 
        step_size = (self.max_ray_angle - self.min_ray_angle)/self.num_rays
        rays = VGroup(*[
            Line(ORIGIN, self.radius*rotate_vector(RIGHT, angle))
            for angle in np.arange(
                self.min_ray_angle,
                self.max_ray_angle,
                step_size
            )
        ])
        rays.shift(source_point)
        rays.set_stroke(YELLOW, 1)
        max_angle = np.max([
            angle_of_vector(point - source_point)
            for point in screen.points
        ])
        min_angle = np.min([
            angle_of_vector(point - source_point)
            for point in screen.points
        ])
        for ray in rays:
            if min_angle <= ray.get_angle() <= max_angle:
                ray.target_color = GREEN
            else:
                ray.target_color = RED

        self.play(*[
            ShowCreation(ray, run_time = 3, **show_creation_kwargs)
            for ray in rays
        ])
        self.play(*[
            ApplyMethod(ray.highlight, ray.target_color)
            for ray in rays
        ])
        self.wait()
        self.play(FadeOut(rays))

class EarthScene(IntroduceScreen):
    CONFIG = {
        "screen_height" : 0.5,
        "screen_thickness" : 0,
        "radius" : 100 + SPACE_WIDTH,
        "source_point" : 100*LEFT,
        "min_ray_angle" : -1.65*DEGREES,
        "max_ray_angle" : 1.65*DEGREES,
        "num_rays" : 100,
    }
    def construct(self):
        # Earth
        earth_radius = 3
        earth = ImageMobject("earth")
        earth_circle = Circle(radius = earth_radius)
        earth_circle.to_edge(RIGHT)
        earth.replace(earth_circle)

        black_rect = Rectangle(
            height = 2*SPACE_HEIGHT,
            width = earth_radius + LARGE_BUFF,
            stroke_width = 0,
            fill_color = BLACK,
            fill_opacity = 1
        )
        black_rect.move_to(earth.get_center(), LEFT)

        self.add_foreground_mobjects(black_rect, earth)

        # screen
        screen = self.screen = Line(
            self.screen_height*UP, ORIGIN,
            stroke_color = WHITE, 
            stroke_width = self.screen_thickness,
        )
        screen.move_to(earth.get_left())
        screen.generate_target()
        screen.target.rotate(
            -60*DEGREES, about_point = earth_circle.get_center()
        )

        equator_arrow = Vector(
            DOWN+2*RIGHT, color = WHITE,
            use_rectangular_stem = False,
        )
        equator_arrow.next_to(screen.get_center(), UP+LEFT, SMALL_BUFF)
        pole_arrow = Vector(
            UP+3*RIGHT, 
            color = WHITE,
            use_rectangular_stem = False,
            path_arc = -60*DEGREES,
        )
        pole_arrow.shift(
            screen.target.get_center()+SMALL_BUFF*LEFT - \
            pole_arrow.get_end()
        )
        for arrow in equator_arrow, pole_arrow:
            arrow.pointwise_become_partial(arrow, 0, 0.95)
        equator_words = TextMobject("Some", "unit of area")
        pole_words = TextMobject("The same\\\\", "unit of area")
        pole_words.next_to(pole_arrow.get_start(), DOWN)
        equator_words.next_to(equator_arrow.get_start(), UP)


        # Light source (far-away Sun)

        sun = sun = LightSource(
            opacity_function = lambda r : 0.5,
            max_opacity_ambient = 0,
            max_opacity_spotlight = 0.5,
            num_levels = 5,
            radius = self.radius,
            screen = screen
        )
        sun.move_source_to(self.source_point)
        sunlight = sun.spotlight
        sunlight.opacity_function = lambda r : 5./(r+1)

        screen_tracker = ScreenTracker(sun)

        # Add elements to scene

        self.add(screen)
        self.play(SwitchOn(
            sunlight, 
            rate_func = squish_rate_func(smooth, 0.7, 0.8),
        ))
        self.add(screen_tracker)
        self.play(
            Write(equator_words),
            GrowArrow(equator_arrow)
        )
        self.add_foreground_mobjects(equator_words, equator_arrow)
        self.shoot_rays(show_creation_kwargs = {
            "rate_func" : lambda t : interpolate(0.98, 1, smooth(t))
        })
        self.wait()
        # Point to patch
        self.play(
            MoveToTarget(screen),
            Transform(equator_arrow, pole_arrow),
            Transform(
                equator_words, pole_words, 
                rate_func = squish_rate_func(smooth, 0.6, 1),
            ),
            Animation(sunlight),
            run_time = 3,
        )
        self.shoot_rays(show_creation_kwargs = {
            "rate_func" : lambda t : interpolate(0.98, 1, smooth(t))
        })
        self.wait()

class InverseSquareLaw(ThreeDScene):
    CONFIG = {
        "screen_height" : 1.0,
        "source_point" : 5*LEFT,
        "unit_distance" : 4,
        "num_levels" : 100,
    }
    def construct(self):
        self.move_screen_farther_away()
        self.morph_into_3d()

    def move_screen_farther_away(self):
        source_point = self.source_point
        unit_distance = self.unit_distance

        # screen
        screen = self.screen = Line(self.screen_height*UP, ORIGIN)
        screen.get_reference_point = screen.get_center
        screen.shift(
            source_point + unit_distance*RIGHT -\
            screen.get_reference_point()
        )
        
        # light source
        light_source = self.light_source = LightSource(
            # opacity_function = inverse_quadratic(1,5,1),
            opacity_function = lambda r : 1./(r+1),
            num_levels = self.num_levels,
            radius = 10,
            max_opacity = 0.2
        )
        light_source.set_max_opacity_spotlight(0.2)

        light_source.set_screen(screen)
        light_source.move_source_to(source_point)

        # abbreviations
        ambient_light = light_source.ambient_light
        spotlight = light_source.spotlight
        lighthouse = light_source.lighthouse
        shadow = light_source.shadow

        # Morty
        morty = self.morty = Mortimer().scale(0.3)
        morty.next_to(screen, RIGHT, buff = MED_LARGE_BUFF)

        #Screen tracker
        def update_spotlight(spotlight):
            spotlight.update_sectors()

        spotlight_update = ContinualUpdateFromFunc(spotlight, update_spotlight)
        shadow_update = ContinualUpdateFromFunc(
            shadow, lambda m : light_source.update_shadow()
        )

        # Light indicator
        light_indicator = self.light_indicator = LightIndicator(
            opacity_for_unit_intensity = 0.5,
        )
        def update_light_indicator(light_indicator):
            distance = np.linalg.norm(screen.get_reference_point() - source_point)
            light_indicator.set_intensity(1.0/(distance/unit_distance)**2)
            light_indicator.next_to(morty, UP, MED_LARGE_BUFF)
        light_indicator_update = ContinualUpdateFromFunc(
            light_indicator, update_light_indicator
        )
        light_indicator_update.update(0)

        continual_updates = self.continual_updates = [
            spotlight_update, light_indicator_update, shadow_update
        ]

        # Distance indicators

        one_arrow = DoubleArrow(ORIGIN, unit_distance*RIGHT, buff = 0)
        two_arrow = DoubleArrow(ORIGIN, 2*unit_distance*RIGHT, buff = 0)
        arrows = VGroup(one_arrow, two_arrow)
        arrows.highlight(WHITE)
        one_arrow.move_to(source_point + DOWN, LEFT)
        two_arrow.move_to(source_point + 1.75*DOWN, LEFT)
        one = Integer(1).next_to(one_arrow, UP, SMALL_BUFF)
        two = Integer(2).next_to(two_arrow, DOWN, SMALL_BUFF)
        arrow_group = VGroup(one_arrow, one, two_arrow, two)

        # Animations

        self.add_foreground_mobjects(lighthouse, screen, morty)
        self.add(shadow_update)

        self.play(
            SwitchOn(ambient_light),
            morty.change, "pondering"
        )
        self.play(
            SwitchOn(spotlight),
            FadeIn(light_indicator)
        )
        # self.remove(spotlight)
        self.add(*continual_updates)
        self.wait()
        for distance in -0.5, 0.5:
            self.shift_by_distance(distance)
            self.wait()
        self.add_foreground_mobjects(one_arrow, one)
        self.play(GrowFromCenter(one_arrow), Write(one))
        self.wait()
        self.add_foreground_mobjects(two_arrow, two)
        self.shift_by_distance(1,
            GrowFromPoint(two_arrow, two_arrow.get_left()),
            Write(two, rate_func = squish_rate_func(smooth, 0.5, 1))
        )
        self.wait()

        q_marks = TextMobject("???")
        q_marks.next_to(light_indicator, UP)
        self.play(
            Write(q_marks),
            morty.change, "confused", q_marks
        )
        self.play(Blink(morty))
        self.play(FadeOut(q_marks), morty.change, "pondering")
        self.wait()
        self.shift_by_distance(-1, arrow_group.shift, DOWN)

        self.set_variables_as_attrs(
            ambient_light, spotlight, shadow, lighthouse,
            morty, arrow_group,
            *continual_updates
        )

    def morph_into_3d(self):
        # axes = ThreeDAxes()
        old_screen = self.screen
        spotlight = self.spotlight
        source_point = self.source_point
        ambient_light = self.ambient_light
        unit_distance = self.unit_distance
        light_indicator = self.light_indicator
        morty = self.morty
        dr = ambient_light.radius/ambient_light.num_levels

        new_screen = Square(
            side_length = self.screen_height,
            stroke_color = WHITE,
            stroke_width = 1,
            fill_color = WHITE,
            fill_opacity = 0.5
        )
        new_screen.rotate(TAU/4, UP)
        new_screen.move_to(old_screen, IN)
        old_screen.fade(1)
        screen_group = VGroup(old_screen, new_screen)

        cone = VGroup(*[VGroup() for x in range(4)])
        cone.set_stroke(width = 0)
        cone.set_fill(YELLOW, opacity = 0.5)
        corner_directions = [OUT+UP, OUT+DOWN, IN+DOWN, IN+UP]
        def update_cone(cone):
            corners = map(new_screen.get_corner, corner_directions)
            distance = np.linalg.norm(old_screen.get_reference_point() - self.source_point)
            n_parts = np.ceil(distance/dr)
            alphas = np.linspace(0, 1, n_parts+1)
            for face, (c1, c2) in zip(cone, adjacent_pairs(corners)):
                face.submobjects = []
                for a1, a2 in zip(alphas, alphas[1:]):
                    face.add(Polygon(
                        interpolate(source_point, c1, a1),
                        interpolate(source_point, c1, a2),
                        interpolate(source_point, c2, a2),
                        interpolate(source_point, c2, a1),
                        fill_color = YELLOW,
                        fill_opacity = ambient_light.opacity_function(a1*distance),
                        stroke_width = 0
                    ))
        cone_update_anim = ContinualUpdateFromFunc(cone, update_cone)
        cone_update_anim.update(0)

        self.remove(self.spotlight_update, self.light_indicator_update)
        self.add(
            ContinualAnimation(new_screen),
            cone_update_anim
        )
        self.remove(spotlight)
        self.move_camera(
            phi = 60*DEGREES,
            theta = -145*DEGREES,
            added_anims = [
                # ApplyMethod(
                #     old_screen.scale, 1.8, {"about_edge" : DOWN},
                #     run_time = 2,
                # ),
                ApplyFunction(
                    lambda m : m.fade(1).shift(1.5*DOWN),
                    light_indicator,
                    remover = True
                ),
                FadeOut(morty)
            ],
            run_time = 2,
        )
        self.wait()
        self.screen = screen_group
        self.shift_by_distance(1)
        self.shift_by_distance(-1)
        self.wait()

        ## Create screen copies
        screen_copy = new_screen.copy()
        four_copies = VGroup(*[new_screen.copy() for x in range(4)])
        nine_copies = VGroup(*[new_screen.copy() for x in range(9)])
        def update_four_copies(four_copies):
            for mob, corner_direction in zip(four_copies, corner_directions):
                mob.move_to(new_screen, corner_direction)
        four_copies_update_anim = UpdateFromFunc(four_copies, update_four_copies)
        edge_directions = [
            UP, UP+OUT, OUT, DOWN+OUT, DOWN, DOWN+IN, IN, UP+IN, ORIGIN
        ]
        def update_nine_copies(nine_copies):
            for mob, corner_direction in zip(nine_copies, edge_directions):
                mob.move_to(new_screen, corner_direction)
        nine_copies_update_anim = UpdateFromFunc(nine_copies, update_nine_copies)

        three_arrow = DoubleArrow(
            source_point + 4*DOWN,
            source_point + 4*DOWN + 3*unit_distance*RIGHT,
            buff = 0,
            color = WHITE
        )
        three = Integer(3)
        three.next_to(three_arrow, DOWN)

        new_screen.fade(1)
        self.add(
            ContinualAnimation(screen_copy),
            ContinualAnimation(four_copies),
        )
        self.play(
            screen_group.scale, 2, {"about_edge" : IN + DOWN},
            screen_group.shift, unit_distance*RIGHT,
            four_copies_update_anim,
            screen_copy.shift, 0.25*OUT, #WHY?
            run_time = 2,
        )
        self.wait()
        self.move_camera(
            phi = 75*DEGREES,
            theta = -155*DEGREES,
            distance = 7,
        )
        self.begin_ambient_camera_rotation(rate = -0.01)
        self.add(ContinualAnimation(nine_copies))
        self.play(
            screen_group.scale, 3./2, {"about_edge" : IN + DOWN},
            screen_group.shift, unit_distance*RIGHT,
            nine_copies_update_anim,
            UpdateFromAlphaFunc(
                nine_copies, 
                lambda nc, a : nc.set_stroke(width = a).set_fill(opacity = 0.5*a)
            ),
            GrowFromPoint(three_arrow, three_arrow.get_left()),
            Write(three, rate_func = squish_rate_func(smooth, 0.5, 1)),
            run_time = 2,
        )
        self.wait()


    ###

    def shift_by_distance(self, distance, *added_anims):
        anims = [
            self.screen.shift, self.unit_distance*distance*RIGHT,
        ]
        if self.morty in self.mobjects:
            anims.append(MaintainPositionRelativeTo(self.morty, self.screen))
        anims += added_anims
        self.play(*anims, run_time = 2)


class IndicatorScalingScene(Scene):

    def construct(self):

        unit_intensity = 0.6

        indicator1 = LightIndicator(show_reading = False, color = LIGHT_COLOR)
        indicator1.set_intensity(unit_intensity)
        reading1 = TexMobject("1")
        reading1.move_to(indicator1)
        

        indicator2 = LightIndicator(show_reading = False, color = LIGHT_COLOR)
        indicator2.shift(2*RIGHT)
        indicator2.set_intensity(unit_intensity/4)
        reading2 = TexMobject("{1\over 4}").scale(0.8)
        reading2.move_to(indicator2)

        indicator3 = LightIndicator(show_reading = False, color = LIGHT_COLOR)
        indicator3.shift(4*RIGHT)
        indicator3.set_intensity(unit_intensity/9)
        reading3 = TexMobject("{1\over 9}").scale(0.8)
        reading3.move_to(indicator3)

        
        self.play(FadeIn(indicator1))
        self.play(FadeIn(reading1))
        self.wait()
        self.play(FadeOut(reading1))
        self.play(Transform(indicator1, indicator2))
        self.play(FadeIn(reading2))
        self.wait()
        self.play(FadeOut(reading2))
        self.play(Transform(indicator1, indicator3))
        self.play(FadeIn(reading3))
        self.wait()

class BackToEulerSumScene(PiCreatureScene):

   
    def construct(self):
        self.remove(self.get_primary_pi_creature())

        NUM_CONES = 7
        NUM_VISIBLE_CONES = 6
        INDICATOR_RADIUS = 0.5
        OPACITY_FOR_UNIT_INTENSITY = 1.0

        self.number_line = NumberLine(
            x_min = 0,
            color = WHITE,
            number_at_center = 1.6,
            stroke_width = 1,
            numbers_with_elongated_ticks = range(1,5),
            numbers_to_show = range(1,5),
            unit_size = 2,
            tick_frequency = 0.2,
            line_to_number_buff = LARGE_BUFF,
            label_direction = UP,
        )

        self.number_line.label_direction = DOWN
        #self.number_line.shift(3*UP)

        self.number_line_labels = self.number_line.get_number_mobjects()
        self.add(self.number_line,self.number_line_labels)
        self.wait()

        origin_point = self.number_line.number_to_point(0)

        self.default_pi_creature_class = Randolph
        randy = self.get_primary_pi_creature()

        randy.scale(0.5)
        randy.flip()
        right_pupil = randy.pupils[1]
        randy.next_to(origin_point, LEFT, buff = 0, submobject_to_align = right_pupil)

        randy_copy = randy.copy()
        randy_copy.target = randy.copy().shift(DOWN)



        bubble = ThoughtBubble(direction = RIGHT,
                            width = 4, height = 3,
                            file_name = "Bubbles_thought.svg")
        bubble.next_to(randy,LEFT+UP)
        bubble.set_fill(color = BLACK, opacity = 1)
        
        self.play(
            randy.change, "wave_2",
            ShowCreation(bubble),
        )


        euler_sum = TexMobject("1", "+", "{1\over 4}", 
            "+", "{1\over 9}", "+", "{1\over 16}", "+", "{1\over 25}", "+", "\cdots", " ")
        # the last entry is a dummy element which makes looping easier
        # used just for putting the fractions into the light indicators
            
        intensities = np.array([1./(n+1)**2 for n in range(NUM_CONES)])
        opacities = intensities * OPACITY_FOR_UNIT_INTENSITY

        # repeat:

        # fade in lighthouse
        # switch on / fade in ambient light
        # show creation / write light indicator
        # move indicator onto origin
            # while morphing and dimming
        # move indicator into thought bubble
            # while indicators already inside shift to the back
            # and while term appears in the series below

        point = self.number_line.number_to_point(1)
        v = point - self.number_line.number_to_point(0)
        light_source = LightSource()
        light_source.move_source_to(point)
        #light_source.ambient_light.move_source_to(point)
        #light_source.lighthouse.move_to(point)

        self.play(FadeIn(light_source.lighthouse))
        self.play(SwitchOn(light_source.ambient_light))


        # create an indicator that will move along the number line
        indicator = LightIndicator(color = LIGHT_COLOR,
                radius = INDICATOR_RADIUS,
                opacity_for_unit_intensity = OPACITY_FOR_UNIT_INTENSITY,
                show_reading = False
        )
        indicator_reading = euler_sum[0]
        indicator_reading.scale_to_fit_height(0.5 * indicator.get_height())
        indicator_reading.move_to(indicator.get_center())
        indicator.add(indicator_reading)
        indicator.tex_reading = indicator_reading
        # the TeX reading is too bright at full intensity
        indicator.tex_reading.set_fill(color = BLACK)
        indicator.foreground.set_fill(None,opacities[0])


        indicator.move_to(point)
        indicator.set_intensity(intensities[0])

        self.play(FadeIn(indicator))
        self.add_foreground_mobject(indicator)
        
        collection_point = np.array([-6.,2.,0.])
        left_shift = 0.2*LEFT
        collected_indicators = Mobject()


        for i in range(2, NUM_VISIBLE_CONES + 1):

            previous_point = self.number_line.number_to_point(i - 1)
            point = self.number_line.number_to_point(i)


            v = point - previous_point
            #print v
            # Create and position the target indicator (next on number line).
            indicator_target = indicator.deepcopy()
            indicator_target.shift(v)


            # Here we make a copy that will move into the thought bubble.
            bubble_indicator = indicator.deepcopy()
            # And its target
            bubble_indicator_target = bubble_indicator.deepcopy()
            bubble_indicator_target.set_intensity(intensities[i - 2])

            # give the target the appropriate reading
            euler_sum[2*i-4].move_to(bubble_indicator_target)
            bubble_indicator_target.remove(bubble_indicator_target.tex_reading)
            bubble_indicator_target.tex_reading = euler_sum[2*i-4].copy()
            bubble_indicator_target.add(bubble_indicator_target.tex_reading)
            # center it in the indicator

            if bubble_indicator_target.tex_reading.get_tex_string() != "1":
                bubble_indicator_target.tex_reading.scale_to_fit_height(0.8*indicator.get_height())
            # the target is less bright, possibly switch to a white text color
            if bubble_indicator_target.intensity < 0.7:
                bubble_indicator.tex_reading.set_fill(color = WHITE)

            # position the target in the thought bubble
            bubble_indicator_target.move_to(collection_point)


            self.add_foreground_mobject(bubble_indicator)


            self.wait()

            self.play(
                 Transform(bubble_indicator,bubble_indicator_target),
                 collected_indicators.shift,left_shift,
            )

            collected_indicators.add(bubble_indicator)

            new_light = light_source.deepcopy()
            w = new_light.get_source_point()
            new_light.move_source_to(w + (i-2)*v)
            w2 = new_light.get_source_point()
            
            self.add(new_light.lighthouse)
            self.play(
                  Transform(indicator,indicator_target),
                  new_light.lighthouse.shift,v,
            )
            new_light.move_source_to(w + (i-1)*v)
            new_light.lighthouse.move_to(w + (i-1)*v)

            self.play(SwitchOn(new_light.ambient_light),
            )


            

        # quickly switch on off-screen light cones
        for i in range(NUM_VISIBLE_CONES,NUM_CONES):
            indicator_start_time = 0.5 * (i+1) * FAST_SWITCH_ON_RUN_TIME/light_source.ambient_light.radius * self.number_line.unit_size
            indicator_stop_time = indicator_start_time + FAST_INDICATOR_UPDATE_TIME
            indicator_rate_func = squish_rate_func(#smooth, 0.8, 0.9)
                smooth,indicator_start_time,indicator_stop_time)
            ls = LightSource()
            point = point = self.number_line.number_to_point(i)
            ls.move_source_to(point)
            self.play(
                SwitchOn(ls.ambient_light, run_time = FAST_SWITCH_ON_RUN_TIME),
            )

        # and morph indicator stack into limit value

        sum_indicator = LightIndicator(color = LIGHT_COLOR,
                radius = INDICATOR_RADIUS,
                opacity_for_unit_intensity = OPACITY_FOR_UNIT_INTENSITY,
                show_reading = False
            )
        sum_indicator.set_intensity(intensities[0] * np.pi**2/6)
        sum_indicator_reading = TexMobject("{\pi^2 \over 6}")
        sum_indicator_reading.set_fill(color = BLACK)
        sum_indicator_reading.scale_to_fit_height(0.8 * sum_indicator.get_height())
        sum_indicator.add(sum_indicator_reading)
        sum_indicator.move_to(collection_point)

        self.play(
            FadeOut(collected_indicators),
            FadeIn(sum_indicator)
        )

            

        self.wait()

class TwoLightSourcesScene(PiCreatureScene):

    def construct(self):

        MAX_OPACITY = 0.4
        INDICATOR_RADIUS = 0.6
        OPACITY_FOR_UNIT_INTENSITY = 0.5

        morty = self.get_primary_pi_creature()
        morty.scale(0.3).flip()
        right_pupil = morty.pupils[1]
        morty.next_to(C, LEFT, buff = 0, submobject_to_align = right_pupil)

        horizontal = VMobject(stroke_width = 1)
        horizontal.set_points_as_corners([C,A])
        vertical = VMobject(stroke_width = 1)
        vertical.set_points_as_corners([C,B])

        self.play(
            ShowCreation(horizontal),
            ShowCreation(vertical)
        )

        indicator = LightIndicator(color = LIGHT_COLOR,
                radius = INDICATOR_RADIUS,
                opacity_for_unit_intensity = OPACITY_FOR_UNIT_INTENSITY,
                show_reading = True,
                precision = 2
        )

        indicator.next_to(morty,LEFT)

        self.play(
            Write(indicator)
        )


        ls1 = LightSource(radius = 20, num_levels = 50)
        ls2 = ls1.deepcopy()
        ls1.move_source_to(A)
        ls2.move_source_to(B)

        self.play(
            FadeIn(ls1.lighthouse),
            FadeIn(ls2.lighthouse),
            SwitchOn(ls1.ambient_light),
            SwitchOn(ls2.ambient_light)
        )

        distance1 = np.linalg.norm(C - ls1.get_source_point())
        intensity = ls1.ambient_light.opacity_function(distance1) / indicator.opacity_for_unit_intensity
        distance2 = np.linalg.norm(C - ls2.get_source_point())
        intensity += ls2.ambient_light.opacity_function(distance2) / indicator.opacity_for_unit_intensity

        self.play(
            UpdateLightIndicator(indicator,intensity)
        )

        self.wait()

        ls3 = ls1.deepcopy()
        ls3.move_to(np.array([6,3.5,0]))

        new_indicator = indicator.copy()
        new_indicator.light_source = ls3
        new_indicator.measurement_point = C
        self.add(new_indicator)
        self.play(
            indicator.shift, 2 * UP
        )



        #intensity = intensity_for_light_source(ls3)


        self.play(
            SwitchOff(ls1.ambient_light),
            #FadeOut(ls1.lighthouse),
            SwitchOff(ls2.ambient_light),
            #FadeOut(ls2.lighthouse),
            UpdateLightIndicator(new_indicator,0.0)
        )

        # create a *continual* animation for the replacement source
        updater = ContinualLightIndicatorUpdate(new_indicator)
        self.add(updater)

        self.play(
            SwitchOn(ls3.ambient_light),
            FadeIn(ls3.lighthouse),
            
        )

        self.wait()

        # move the light source around
        # TODO: moving along a path arc

        location = np.array([-3,-2.,0.])
        self.play(ls3.move_source_to,location)
        location = np.array([6.,1.,0.])
        self.play(ls3.move_source_to,location)
        location = np.array([5.,2.,0.])
        self.play(ls3.move_source_to,location)
        closer_location = interpolate(location, C, 0.5)
        self.play(ls3.move_source_to,closer_location)
        self.play(ls3.move_source_to,location)

        # maybe move in a circle around C using a loop?



        self.play(ls3.move_source_to,H)



        # draw lines to complete the geometric picture
        # and label the lengths

        line_a = VMobject()
        line_a.set_points_as_corners([B,C])
        line_b = VMobject()
        line_b.set_points_as_corners([A,C])
        line_c = VMobject()
        line_c.set_points_as_corners([A,B])
        line_h = VMobject()
        line_h.set_points_as_corners([H,C])

        label_a = TexMobject("a")
        label_a.next_to(line_a, LEFT, buff = 0.5)
        label_b = TexMobject("b")
        label_b.next_to(line_b, DOWN, buff = 0.5)
        label_h = TexMobject("h")
        label_h.next_to(line_h.get_center(), RIGHT, buff = 0.5)

        self.play(
            ShowCreation(line_a),
            Write(label_a)
        )

        self.play(
            ShowCreation(line_b),
            Write(label_b)
        )

        self.play(
            ShowCreation(line_c),
        )

        self.play(
            ShowCreation(line_h),
            Write(label_h)
        )


        # state the IPT
        theorem_location = np.array([3.,2.,0.])
        theorem = TexMobject("{1\over a^2} + {1\over b^2} = {1\over h^2}")
        theorem_name = TextMobject("Inverse Pythagorean Theorem")
        buffer = 1.2
        theorem_box = Rectangle(width = buffer*theorem.get_width(),
            height = buffer*theorem.get_height())

        theorem.move_to(theorem_location)
        theorem_box.move_to(theorem_location)
        theorem_name.next_to(theorem_box,UP)

        self.play(
            Write(theorem),
        )

        self.play(
            ShowCreation(theorem_box),
            Write(theorem_name),
        )

class IPTScene1(PiCreatureScene):

    def construct(self):

        show_detail = True

        SCREEN_SCALE = 0.1
        SCREEN_THICKNESS = 0.2


        # use the following for the zoomed inset
        if show_detail:
            self.camera.space_shape = (0.02 * SPACE_HEIGHT, 0.02 * SPACE_WIDTH)
            self.camera.space_center = C
            SCREEN_SCALE = 0.01
            SCREEN_THICKNESS = 0.02





        morty = self.get_primary_pi_creature()
        self.remove(morty)
        morty.scale(0.3).flip()
        right_pupil = morty.pupils[1]
        morty.next_to(C, LEFT, buff = 0, submobject_to_align = right_pupil)
        
        if not show_detail:
            self.add_foreground_mobject(morty)

        stroke_width = 6
        line_a = Line(B,C,stroke_width = stroke_width)
        line_b = Line(A,C,stroke_width = stroke_width)
        line_c = Line(A,B,stroke_width = stroke_width)
        line_h = Line(C,H,stroke_width = stroke_width)

        length_a = line_a.get_length()
        length_b = line_b.get_length()
        length_c = line_c.get_length()
        length_h = line_h.get_length()

        label_a = TexMobject("a")
        label_a.next_to(line_a, LEFT, buff = 0.5)
        label_b = TexMobject("b")
        label_b.next_to(line_b, DOWN, buff = 0.5)
        label_h = TexMobject("h")
        label_h.next_to(line_h.get_center(), RIGHT, buff = 0.5)

        self.add_foreground_mobject(line_a)
        self.add_foreground_mobject(line_b)
        self.add_foreground_mobject(line_c)
        self.add_foreground_mobject(line_h)
        self.add_foreground_mobject(label_a)
        self.add_foreground_mobject(label_b)
        self.add_foreground_mobject(label_h)
        
        if not show_detail:
            self.add_foreground_mobject(morty)

        ls1 = LightSource(radius = 10)
        ls1.move_source_to(B)

        self.add(ls1.lighthouse)

        if not show_detail:
            self.play(
                SwitchOn(ls1.ambient_light)
            )

        self.wait()

        # adding the first screen

        screen_width_a = SCREEN_SCALE * length_a
        screen_width_b = SCREEN_SCALE * length_b
        screen_width_ap = screen_width_a * length_a / length_c
        screen_width_bp = screen_width_b * length_b / length_c
        screen_width_c = SCREEN_SCALE * length_c

        screen_thickness_a = SCREEN_THICKNESS
        screen_thickness_b = SCREEN_THICKNESS

        screen1 = Rectangle(width = screen_width_b,
            height = screen_thickness_b, 
            stroke_width = 0, 
            fill_opacity = 1.0)
        screen1.move_to(C + screen_width_b/2 * RIGHT + screen_thickness_b/2 * DOWN)
        
        if not show_detail:
            self.add_foreground_mobject(morty)

        self.play(
            FadeIn(screen1)
        )
        self.add_foreground_mobject(screen1)

        ls1.set_screen(screen1)
        screen_tracker = ScreenTracker(ls1)
        self.add(screen_tracker)
        #self.add(ls1.shadow)

        if not show_detail:
            self.play(
                SwitchOn(ls1.ambient_light)
            )

        self.play(
            SwitchOn(ls1.spotlight),
            SwitchOff(ls1.ambient_light)
        )



        # now move the light source to the height point
        # while shifting scaling the screen
        screen1p = screen1.deepcopy()
        screen1pp = screen1.deepcopy()
        #self.add(screen1p)
        angle = np.arccos(length_b / length_c)
        
        screen1p.stretch_to_fit_width(screen_width_bp)
        screen1p.move_to(C + (screen_width_b - screen_width_bp/2) * RIGHT + SCREEN_THICKNESS/2 * DOWN)
        screen1p.rotate(-angle, about_point = C + screen_width_b * RIGHT)
        

        self.play(
            ls1.move_source_to,H,
            Transform(screen1,screen1p)
        )

        # add and move the second light source and screen
        ls2 = ls1.deepcopy()
        ls2.move_source_to(A)
        screen2 = Rectangle(width = screen_width_a,
            height = screen_thickness_a, 
            stroke_width = 0, 
            fill_opacity = 1.0)
        screen2.rotate(-TAU/4)
        screen2.move_to(C + screen_width_a/2 * UP + screen_thickness_a/2 * LEFT)

        self.play(
            FadeIn(screen2)
        )
        self.add_foreground_mobject(screen2)

        if not show_detail:
            self.add_foreground_mobject(morty)

        # the same scene adding sequence as before
        ls2.set_screen(screen2)
        screen_tracker2 = ScreenTracker(ls2)
        self.add(screen_tracker2)

        if not show_detail:
            self.play(
                SwitchOn(ls2.ambient_light)
            )

        self.wait()

        self.play(
            SwitchOn(ls2.spotlight),
            SwitchOff(ls2.ambient_light)
        )



        # now move the light source to the height point
        # while shifting scaling the screen
        screen2p = screen2.deepcopy()
        screen2pp = screen2.deepcopy()
        angle = np.arccos(length_a / length_c)
        screen2p.stretch_to_fit_height(screen_width_ap)
        screen2p.move_to(C + (screen_width_a - screen_width_ap/2) * UP + screen_thickness_a/2 * LEFT)
        screen2p.rotate(angle, about_point = C + screen_width_a * UP)
        # we can reuse the translation vector
        # screen2p.shift(vector)

        self.play(
            ls2.move_source_to,H,
            SwitchOff(ls1.ambient_light),
            Transform(screen2,screen2p)
        )

        # now transform both screens back
        self.play(
            Transform(screen1, screen1pp),
            Transform(screen2, screen2pp),
        )

class IPTScene2(Scene):

    def construct(self):

        intensity1 = 0.3
        intensity2 = 0.2
        formula_scale = 01.2
        indy_radius = 1

        indy1 = LightIndicator(color = LIGHT_COLOR, show_reading = False, radius = indy_radius)
        indy1.set_intensity(intensity1)
        reading1 = TexMobject("{1\over a^2}").scale(formula_scale).move_to(indy1)
        indy1.add(reading1)

        indy2 = LightIndicator(color = LIGHT_COLOR, show_reading = False, radius = indy_radius)
        indy2.set_intensity(intensity2)
        reading2 = TexMobject("{1\over b^2}").scale(formula_scale).move_to(indy2)
        indy2.add(reading2)

        indy3 = LightIndicator(color = LIGHT_COLOR, show_reading = False, radius = indy_radius)
        indy3.set_intensity(intensity1 + intensity2)
        reading3 = TexMobject("{1\over h^2}").scale(formula_scale).move_to(indy3)
        indy3.add(reading3)

        plus_sign = TexMobject("+").scale(formula_scale)
        equals_sign = TexMobject("=").scale(formula_scale)

        plus_sign.next_to(indy1, RIGHT)
        indy2.next_to(plus_sign, RIGHT)
        equals_sign.next_to(indy2, RIGHT)
        indy3.next_to(equals_sign, RIGHT)
        

        formula = VGroup(
            indy1, plus_sign, indy2, equals_sign, indy3
        )

        formula.move_to(ORIGIN)

        self.play(FadeIn(indy1))
        self.play(FadeIn(plus_sign), FadeIn(indy2))
        self.play(FadeIn(equals_sign), FadeIn(indy3))

        buffer = 1.5
        box = Rectangle(width = formula.get_width() * buffer,
            height = formula.get_height() * buffer)
        box.move_to(formula)
        text = TextMobject("Inverse Pythagorean Theorem").scale(formula_scale)
        text.next_to(box,UP)
        self.play(ShowCreation(box),Write(text))

class PondScene(Scene):

    def construct(self):

        BASELINE_YPOS = -2.5
        OBSERVER_POINT = [0,BASELINE_YPOS,0]
        LAKE0_RADIUS = 1.5
        INDICATOR_RADIUS = 0.6
        TICK_SIZE = 0.5
        LIGHTHOUSE_HEIGHT = 0.2
        LAKE_COLOR = BLUE
        LAKE_OPACITY = 0.15
        LAKE_STROKE_WIDTH = 5.0
        LAKE_STROKE_COLOR = BLUE
        TEX_SCALE = 0.8
        DOT_COLOR = BLUE

        baseline = VMobject()
        baseline.set_points_as_corners([[-8,BASELINE_YPOS,0],[8,BASELINE_YPOS,0]])

        obs_dot = Dot(OBSERVER_POINT, fill_color = DOT_COLOR)
        ls0_dot = Dot(OBSERVER_POINT + 2 * LAKE0_RADIUS * UP, fill_color = WHITE)


        # lake
        lake0 = Circle(radius = LAKE0_RADIUS,
            stroke_width = 0,
            fill_color = LAKE_COLOR,
            fill_opacity = LAKE_OPACITY
        )
        lake0.move_to(OBSERVER_POINT + LAKE0_RADIUS * UP)

        # Morty and indicator
        morty = Mortimer().scale(0.3)
        morty.next_to(OBSERVER_POINT,DOWN)
        indicator = LightIndicator(precision = 2,
            radius = INDICATOR_RADIUS,
            show_reading  = False,
            color = LIGHT_COLOR
        )
        indicator.next_to(morty,LEFT)

        # first lighthouse
        ls0 = LightSource()
        ls0.move_source_to(OBSERVER_POINT + LAKE0_RADIUS * 2 * UP)

        self.add(lake0,morty,obs_dot,ls0_dot, ls0.lighthouse)

        self.wait()


        # shore arcs
        arc_left = Arc(-TAU/2,
            radius = LAKE0_RADIUS,
            start_angle = -TAU/4,
            stroke_width = LAKE_STROKE_WIDTH,
            stroke_color = LAKE_STROKE_COLOR
        )
        arc_left.move_arc_center_to(OBSERVER_POINT + LAKE0_RADIUS * UP)

        one_left = TexMobject("1", color = LAKE_COLOR).scale(TEX_SCALE)
        one_left.next_to(arc_left,LEFT)
        

        arc_right = Arc(TAU/2,
            radius = LAKE0_RADIUS,
            start_angle = -TAU/4,
            stroke_width = LAKE_STROKE_WIDTH,
            stroke_color = LAKE_STROKE_COLOR
        )
        arc_right.move_arc_center_to(OBSERVER_POINT + LAKE0_RADIUS * UP)

        one_right = TexMobject("1", color = LAKE_COLOR).scale(TEX_SCALE)
        one_right.next_to(arc_right,RIGHT)

        self.play(
            ShowCreation(arc_left),
            Write(one_left),
            ShowCreation(arc_right),
            Write(one_right),
        )


        self.play(
            SwitchOn(ls0.ambient_light),
            lake0.set_stroke,{"color": LAKE_STROKE_COLOR, "width" : LAKE_STROKE_WIDTH},
        )

        self.play(FadeIn(indicator))

        self.play(
            indicator.set_intensity,0.5
        )

        # diameter
        diameter = DoubleArrow(OBSERVER_POINT,
            ls0.get_source_point(),
            buff = 0,
            color = WHITE,
        )
        diameter_text = TexMobject("d").scale(TEX_SCALE)
        diameter_text.next_to(diameter,RIGHT)

        self.play(
            ShowCreation(diameter),
            Write(diameter_text),
            #FadeOut(obs_dot),
            FadeOut(ls0_dot)
        )

        indicator.reading = TexMobject("{1\over d^2}").scale(TEX_SCALE)
        indicator.reading.move_to(indicator)

        self.play(
            FadeIn(indicator.reading)
        )

        # replace d with its value
        new_diameter_text = TexMobject("{2\over \pi}").scale(TEX_SCALE)
        new_diameter_text.color = LAKE_COLOR
        new_diameter_text.move_to(diameter_text)
        self.play(
            Transform(diameter_text,new_diameter_text)
        )

        # insert into indicator reading
        new_reading = TexMobject("{\pi^2 \over 4}").scale(TEX_SCALE)
        new_reading.move_to(indicator)

        self.play(
            Transform(indicator.reading,new_reading)
        )

        self.play(
            FadeOut(one_left),
            FadeOut(one_right),
            FadeOut(diameter_text),
            FadeOut(arc_left),
            FadeOut(arc_right)
        )




        def indicator_wiggle():
            INDICATOR_WIGGLE_FACTOR = 1.3

            self.play(
                ScaleInPlace(indicator, INDICATOR_WIGGLE_FACTOR, rate_func = wiggle),
                ScaleInPlace(indicator.reading, INDICATOR_WIGGLE_FACTOR, rate_func = wiggle)
            )


        def angle_for_index(i,step):
            return -TAU/4 + TAU/2**step * (i + 0.5)


        def position_for_index(i, step, scaled_down = False):

            theta = angle_for_index(i,step)
            radial_vector = np.array([np.cos(theta),np.sin(theta),0])
            position = self.lake_center + self.lake_radius * radial_vector

            if scaled_down:
                return position.scale_about_point(OBSERVER_POINT,0.5)
            else:
                return position


        def split_light_source(i, step, show_steps = True, run_time = 1, ls_radius = 1):

            ls_new_loc1 = position_for_index(i,step + 1)
            ls_new_loc2 = position_for_index(i + 2**step,step + 1)

            hyp = VMobject()
            hyp1 = Line(self.lake_center,ls_new_loc1)
            hyp2 = Line(self.lake_center,ls_new_loc2)
            hyp.add(hyp2,hyp1)
            self.new_hypotenuses.append(hyp)

            if show_steps == True:
                self.play(
                    ShowCreation(hyp, run_time = run_time)
                )

            leg1 = Line(OBSERVER_POINT,ls_new_loc1)
            leg2 = Line(OBSERVER_POINT,ls_new_loc2)
            self.new_legs_1.append(leg1)
            self.new_legs_2.append(leg2)

            if show_steps == True:
                self.play(
                    ShowCreation(leg1, run_time = run_time),
                    ShowCreation(leg2, run_time = run_time),
                )

            ls1 = self.light_sources_array[i]
            ls2 = ls1.copy()
            self.add(ls2)
            self.additional_light_sources.append(ls2)

            # check if the light sources are on screen
            ls_old_loc = np.array(ls1.get_source_point())
            onscreen_old = np.all(np.abs(ls_old_loc) < 10)
            onscreen_1 = np.all(np.abs(ls_new_loc1) < 10)
            onscreen_2 = np.all(np.abs(ls_new_loc2) < 10)
            show_animation = (onscreen_old or onscreen_1 or onscreen_2)

            if show_animation:
                self.play(
                    ApplyMethod(ls1.move_source_to,ls_new_loc1, run_time = run_time),
                    ApplyMethod(ls2.move_source_to,ls_new_loc2, run_time = run_time),
                )
            else:
                ls1.move_source_to(ls_new_loc1)
                ls2.move_source_to(ls_new_loc1)





        def construction_step(n, scale_down = True, show_steps = True, run_time = 1,
            simultaneous_splitting = False, ls_radius = 1):

            # we assume that the scene contains:
            # an inner lake, self.inner_lake
            # an outer lake, self.outer_lake
            # light sources, self.light_sources
            # legs from the observer point to each light source
            # self.legs
            # altitudes from the observer point to the
            # locations of the light sources in the previous step
            # self.altitudes
            # hypotenuses connecting antipodal light sources
            # self.hypotenuses

            # these are mobjects!


            # first, fade out all of the hypotenuses and altitudes
            if show_steps == True:
                self.play(
                    FadeOut(self.hypotenuses),
                    FadeOut(self.altitudes),
                    FadeOut(self.inner_lake)
                )
            else:
                self.play(
                    FadeOut(self.inner_lake)
                )

            # create a new, outer lake

            new_outer_lake = Circle(radius = self.lake_radius,
                stroke_width = LAKE_STROKE_WIDTH,
                fill_color = LAKE_COLOR,
                fill_opacity = LAKE_OPACITY,
                stroke_color = LAKE_STROKE_COLOR
            )
            new_outer_lake.move_to(self.lake_center)

            if show_steps == True: 
                self.play(
                    FadeIn(new_outer_lake, run_time = run_time),
                    FadeIn(ls0_dot)
                )
            else:
                self.play(
                    FadeIn(new_outer_lake, run_time = run_time),
                )

            self.wait()

            self.inner_lake = self.outer_lake
            self.outer_lake = new_outer_lake
            self.altitudes = self.legs

            self.additional_light_sources = []
            self.new_legs_1 = []
            self.new_legs_2 = []
            self.new_hypotenuses = []

            for i in range(2**n):
                split_light_source(i,
                    step = n,
                    show_steps = show_steps,
                    run_time = run_time,
                    ls_radius = ls_radius
                )



            # collect the newly created mobs (in arrays)
            # into the appropriate Mobject containers

            self.legs = VMobject()
            for leg in self.new_legs_1:
                self.legs.add(leg)
            for leg in self.new_legs_2:
                self.legs.add(leg)

            self.hypotenuses = VMobject()
            for hyp in self.new_hypotenuses:
                self.hypotenuses.add(hyp)

            for ls in self.additional_light_sources:
                self.light_sources.add(ls)
                self.light_sources_array.append(ls)

            # update scene
            self.add(
                self.light_sources,
                self.inner_lake,
                self.outer_lake,
            )

            if show_steps == True:
                self.add(
                    self.legs,
                    self.hypotenuses,
                    self.altitudes,
                )


            self.wait()

            if show_steps == True:
                self.play(FadeOut(ls0_dot))

            # scale down
            if scale_down:

                indicator_wiggle()
                
                if show_steps == True:
                    self.play(
                        ScaleLightSources(self.light_sources,0.5,about_point = OBSERVER_POINT),
                        self.inner_lake.scale_about_point,0.5,OBSERVER_POINT,
                        self.outer_lake.scale_about_point,0.5,OBSERVER_POINT,
                        self.legs.scale_about_point,0.5,OBSERVER_POINT,
                        self.hypotenuses.scale_about_point,0.5,OBSERVER_POINT,
                        self.altitudes.scale_about_point,0.5,OBSERVER_POINT,
                    )
                else:
                    self.play(
                        ScaleLightSources(self.light_sources,0.5,about_point = OBSERVER_POINT),
                        self.inner_lake.scale_about_point,0.5,OBSERVER_POINT,
                        self.outer_lake.scale_about_point,0.5,OBSERVER_POINT,
                    )

                # update the radii bc they haven't done so themselves
                # bc reasons...
                for ls in self.light_sources_array:
                    r = ls.radius
                    ls.set_radius(r*0.5)

            else:
                # update the lake center and the radius
                self.lake_center = ls0_loc = self.outer_lake.get_center() + self.lake_radius * UP
                self.lake_radius *= 2








        self.lake_center = ls0_loc = ls0.get_source_point()

        self.inner_lake = VMobject()
        self.outer_lake = lake0
        self.legs = VMobject()
        self.legs.add(Line(OBSERVER_POINT,self.lake_center))
        self.altitudes = VMobject()
        self.hypotenuses = VMobject()
        self.light_sources_array = [ls0]
        self.light_sources = VMobject()
        self.light_sources.add(ls0)

        self.lake_radius = 2 * LAKE0_RADIUS # don't ask...

        self.add(self.inner_lake,
            self.outer_lake,
            self.legs,
            self.altitudes,
            self.hypotenuses
        )

        self.play(FadeOut(diameter))
        
        self.additional_light_sources = []
        self.new_legs_1 = []
        self.new_legs_2 = []
        self.new_hypotenuses = []

        ls_radius = 25.0

        for i in range(3):
            construction_step(i, scale_down = True, ls_radius = ls_radius/2**i)

        return

        self.play(
            FadeOut(self.altitudes),
            FadeOut(self.hypotenuses),
            FadeOut(self.legs)
            )

        for i in range(3,5):
            construction_step(i, scale_down = False, show_steps = False, run_time = 1.0/2**i,
                simultaneous_splitting = True, ls_radius = ls_radius/2**3)




        # Now create a straight number line and transform into it
        MAX_N = 17

        self.number_line = NumberLine(
            x_min = -MAX_N,
            x_max = MAX_N + 1,
            color = WHITE,
            number_at_center = 0,
            stroke_width = LAKE_STROKE_WIDTH,
            stroke_color = LAKE_STROKE_COLOR,
            numbers_with_elongated_ticks = range(-MAX_N,MAX_N + 1),
            numbers_to_show = range(-MAX_N,MAX_N + 1),
            unit_size = LAKE0_RADIUS * TAU/4 / 4,
            tick_frequency = 1,
            line_to_number_buff = LARGE_BUFF,
            label_direction = UP,
        ).shift(2.5 * DOWN)

        self.number_line.label_direction = DOWN

        self.number_line_labels = self.number_line.get_number_mobjects()
        self.wait()

        origin_point = self.number_line.number_to_point(0)
        nl_sources = VMobject()
        pond_sources = VMobject()

        for i in range(-MAX_N,MAX_N+1):
            anchor = self.number_line.number_to_point(2*i + 1)
            ls = self.light_sources_array[i].copy()
            ls.move_source_to(anchor)
            nl_sources.add(ls)
            pond_sources.add(self.light_sources_array[i].copy())

        self.add(pond_sources)
        self.remove(self.light_sources)

        self.outer_lake.rotate(TAU/8)

        # open sea
        open_sea = Rectangle(
            width = 20,
            height = 10,
            stroke_width = LAKE_STROKE_WIDTH,
            stroke_color = LAKE_STROKE_COLOR,
            fill_color = LAKE_COLOR,
            fill_opacity = LAKE_OPACITY,
        ).flip().next_to(origin_point,UP,buff = 0)



        self.play(
            Transform(pond_sources,nl_sources),
            Transform(self.outer_lake,open_sea),
            FadeOut(self.inner_lake)
        )
        self.play(FadeIn(self.number_line))

class LabeledArc(Arc):
    CONFIG = {
        "length" : 1
    }

    def __init__(self, angle, **kwargs):

        BUFFER = 1.3

        Arc.__init__(self,angle,**kwargs)

        label = DecimalNumber(self.length, num_decimal_points = 0)
        r = BUFFER * self.radius
        theta = self.start_angle + self.angle/2
        label_pos = r * np.array([np.cos(theta), np.sin(theta), 0])

        label.move_to(label_pos)
        self.add(label)

class ArcHighlightOverlayScene(Scene):

    def construct(self):

        BASELINE_YPOS = -2.5
        OBSERVER_POINT = [0,BASELINE_YPOS,0]
        LAKE0_RADIUS = 1.5
        INDICATOR_RADIUS = 0.6
        TICK_SIZE = 0.5
        LIGHTHOUSE_HEIGHT = 0.2
        LAKE_COLOR = BLUE
        LAKE_OPACITY = 0.15
        LAKE_STROKE_WIDTH = 5.0
        LAKE_STROKE_COLOR = BLUE
        TEX_SCALE = 0.8
        DOT_COLOR = BLUE

        FLASH_TIME = 0.25

        def flash_arcs(n):

            angle = TAU/2**n
            arcs = []
            arcs.append(LabeledArc(angle/2, start_angle = -TAU/4, radius = LAKE0_RADIUS, length = 1))

            for i in range(1,2**n):
                arcs.append(LabeledArc(angle, start_angle = -TAU/4 + (i-0.5)*angle, radius = LAKE0_RADIUS, length = 2))
        
            arcs.append(LabeledArc(angle/2, start_angle = -TAU/4 - angle/2, radius = LAKE0_RADIUS, length = 1))

            self.play(
                FadeIn(arcs[0], run_time = FLASH_TIME)
            )

            for i in range(1,2**n + 1):
                self.play(
                    FadeOut(arcs[i-1], run_time = FLASH_TIME),
                    FadeIn(arcs[i], run_time = FLASH_TIME)
                )

            self.play(
                FadeOut(arcs[2**n], run_time = FLASH_TIME),
            )


        flash_arcs(3)







































