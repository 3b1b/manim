#!/usr/bin/env python
# -*- coding: utf-8 -*-


from manimlib.imports import *
from once_useful_constructs.light import *

import warnings
warnings.warn("""
    Warning: This file makes use of
    ContinualAnimation, which has since
    been deprecated
""")


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

# A = np.array([5.,-3.,0.])
# B = np.array([-5.,3.,0.])
# C = np.array([-5.,-3.,0.])
# xA = A[0]
# yA = A[1]
# xB = B[0]
# yB = B[1]
# xC = C[0]
# yC = C[1]

# find the coords of the altitude point H
# as the solution of a certain LSE
# prelim_matrix = np.array([[yA - yB, xB - xA], [xA - xB, yA - yB]]) # sic
# prelim_vector = np.array([xB * yA - xA * yB, xC * (xA - xB) + yC * (yA - yB)])
# H2 = np.linalg.solve(prelim_matrix,prelim_vector)
# H = np.append(H2, 0.)

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
        self.reading = DecimalNumber(self.intensity,num_decimal_places = self.precision)
        self.reading.set_fill(color=INDICATOR_TEXT_COLOR)
        self.reading.set_height(self.reading_height)
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
        if self.measurement_point is not None:
            return self.measurement_point
        else:
            return self.get_center()

    def measured_intensity(self):
        distance = get_norm(
            self.get_measurement_point() - 
            self.light_source.get_source_point()
        )
        intensity = self.light_source.opacity_function(distance) / self.opacity_for_unit_intensity
        return intensity

    def update_mobjects(self):
        if self.light_source == None:
            print("Indicator cannot update, reason: no light source found")
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
        self.mobject.update_mobjects()

def copy_func(f):
    """Based on http://stackoverflow.com/a/6528148/190597 (Glenn Maynard)"""
    g = types.FunctionType(f.__code__, f.__globals__, name=f.__name__,
                           argdefs=f.__defaults__,
                           closure=f.__closure__)
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

class ThreeDSpotlight(VGroup):
    CONFIG = { 
        "fill_color" : YELLOW,
    }
    def __init__(self, screen, ambient_light, source_point_func, **kwargs):
        self.screen = screen
        self.ambient_light = ambient_light
        self.source_point_func = source_point_func
        self.dr = ambient_light.radius/ambient_light.num_levels
        VGroup.__init__(self, **kwargs)

    def update(self):
        screen = self.screen
        source_point = self.source_point_func()
        dr = self.dr
        corners = screen.get_anchors()
        self.submobjects = [VGroup() for a in screen.get_anchors()]

        distance = get_norm(
            screen.get_center() - source_point
        )
        n_parts = np.ceil(distance/dr)
        alphas = np.linspace(0, 1, n_parts+1)
        for face, (c1, c2) in zip(self, adjacent_pairs(corners)):
            face.submobjects = []
            for a1, a2 in zip(alphas, alphas[1:]):
                face.add(Polygon(
                    interpolate(source_point, c1, a1),
                    interpolate(source_point, c1, a2),
                    interpolate(source_point, c2, a2),
                    interpolate(source_point, c2, a1),
                    fill_color = self.fill_color,
                    fill_opacity = self.ambient_light.opacity_function(a1*distance),
                    stroke_width = 0
                ))

class ContinualThreeDLightConeUpdate(ContinualAnimation):
    def update(self, dt):
        self.mobject.update()

###

class ThinkAboutPondScene(PiCreatureScene):
    CONFIG = {
        "default_pi_creature_class" : Randolph,
    }
    def construct(self):
        randy = self.pi_creature
        randy.to_corner(DOWN+LEFT)
        bubble = ThoughtBubble(
            width = 11,
            height = 8,
        )
        circles = bubble[:3]
        angle = -15*DEGREES
        circles.rotate(angle, about_point = bubble.get_bubble_center())
        circles.shift(LARGE_BUFF*LEFT)
        for circle in circles:
            circle.rotate(-angle)
        bubble.pin_to(randy)
        bubble.shift(DOWN)
        bubble[:3].rotate(np.pi, axis = UP+2*RIGHT, about_edge = UP+LEFT)
        bubble[:3].scale(0.7, about_edge = DOWN+RIGHT)
        bubble[:3].shift(1.5*DOWN)
        for oval in bubble[:3]:
            oval.rotate(TAU/3)

        self.play(
            randy.change, "thinking",
            ShowCreation(bubble)
        )
        self.wait(2)
        self.play(randy.change, "happy", bubble)
        self.wait(4)
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
            num_decimal_places = 2
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
            color = next(slab_colors)
            line = Line(*list(map(number_line.number_to_point, [t1, t2])))
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
                    rect_label.set_width(max_width)
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
        dots.set_width(0.9*last_rect.get_width())
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
                        num_decimal_places = 6,
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
                    num_decimal_places = 6,
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
        q_marks.set_color(LIGHT_COLOR)

        self.play(
            GrowFromCenter(brace),
            Write(q_marks),
            ChangeDecimalToValue(
                partial_sum_decimal,
                series_terms[-1],
                num_decimal_places = 6,
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

        pietro.next_to(FRAME_X_RADIUS*LEFT, LEFT)
        euler.next_to(FRAME_X_RADIUS*RIGHT, RIGHT)

        pi_answer = self.pi_answer = TexMobject("{\\pi^2 \\over 6}")
        pi_answer.set_color(YELLOW)
        pi_answer.move_to(self.partial_sum_decimal, LEFT)
        equals_sign = TexMobject("=")
        equals_sign.next_to(pi_answer, RIGHT)
        pi_answer.shift(SMALL_BUFF*UP)
        self.partial_sum_decimal.generate_target()
        self.partial_sum_decimal.target.next_to(equals_sign, RIGHT)

        pi = pi_answer[0]
        pi_rect = SurroundingRectangle(pi, color = RED)
        pi_rect.save_state()
        pi_rect.set_height(FRAME_Y_RADIUS)
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
            self.number_line_group.next_to, FRAME_Y_RADIUS*DOWN, DOWN,
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
        q_mark.set_height(0.8 * q_circle.get_height())
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
            "I am not",
            "fundamentally \\\\", 
            "about circles"
        )
        words.set_color_by_tex("fundamentally", YELLOW)

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
        formulas.arrange(DOWN, buff = MED_LARGE_BUFF)
        for formula in formulas:
            basel_equals_x = basel_equals.get_center()[0]
            formula_equals_x = formula.get_part_by_tex("=").get_center()[0]
            formula.shift((basel_equals_x - formula_equals_x)*RIGHT)

        formulas.to_corner(UP+RIGHT)
        formulas.shift(2*LEFT)
        self.formulas = formulas

        self.play(
            jerk.change, "sassy",
            randy.change, "raise_right_hand",
            FadeOut(jerk.bubble),
            words.next_to, jerk, UP,
            FadeIn(basel_sum, lag_ratio = 0.5, run_time = 3)
        )
        for formula in formulas[1:]:
            self.play(
                FadeIn(
                    formula, 
                    lag_ratio = 0.5, 
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
        arrow.set_color(WHITE)

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
        radius.set_color(BLUE)
        semi_circle.set_color(YELLOW)

        VGroup(radius, semi_circle).move_to(
            FRAME_X_RADIUS*LEFT/2 + FRAME_Y_RADIUS*UP/2,
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
            part.move_to(FRAME_HEIGHT*DOWN)

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
        dots.set_height(3)
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
        radius.set_color(BLUE)
        VGroup(circle, radius).next_to(path_dots[-1], RIGHT)

        self.play(
            Write(title),
            LaggedStartMap(ShowCreation, edges, run_time = 3),
            LaggedStartMap(GrowFromCenter, dots, run_time = 3)
        )
        self.play(path_dots[0].set_color, RED)
        for dot, edge in zip(path_dots[1:], path_edges):
            self.play(
                ShowCreation(edge),
                dot.set_color, RED
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
        jerk.move_to(0.5*FRAME_X_RADIUS*LEFT).to_edge(DOWN)
        randy.move_to(0.5*FRAME_X_RADIUS*RIGHT).to_edge(DOWN)

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
            numbers_with_elongated_ticks = list(range(1,6)),
            numbers_to_show = list(range(1,6)),
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
            LaggedStartMap(
                FadeIn, lighthouses,
                run_time = 1
            )
        )
        self.play(LaggedStartMap(
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
        self.play(LaggedStartMap(FadeOut, light_sources[1:]))
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
            LaggedStartMap(FadeIn, lighthouses[1:]),
            morty.change, "hooray",
        )
        self.play(
            LaggedStartMap(
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
            LaggedStartMap(
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
    CONFIG = {
        "num_levels" : 200,
        "radius" : 10,
    }
    def construct(self):
        light_source = LightSource(
            num_levels = self.num_levels,
            radius = self.radius,
            opacity_function = inverse_quadratic(1,2,1),
        )
        light_source.lighthouse.scale(0.5, about_edge = UP)
        light_source.move_source_to(5*LEFT + 2*UP)

        self.add_foreground_mobjects(self.pi_creatures)
        self.student_says(
            "What do you mean \\\\ by ``brightness''?",
            added_anims = [
                SwitchOn(light_source.ambient_light),
                Animation(light_source.lighthouse)
            ]
        )
        self.play(self.teacher.change, "happy")
        self.wait(4)

class IntroduceScreen(Scene):
    CONFIG = {
        "num_levels" : 100,
        "radius" : 10,
        "num_rays" : 250,
        "min_ray_angle" : 0,
        "max_ray_angle" : TAU,
        "source_point" : 2.5*LEFT,
        "observer_point" : 3.5*RIGHT,
        "screen_height" : 2,
    }
    def construct(self):
        self.setup_elements()
        self.setup_angle() # spotlight and angle msmt change when screen rotates
        self.rotate_screen()
        # self.morph_lighthouse_into_sun()

    def setup_elements(self):
        SCREEN_SIZE = 3.0
        source_point = self.source_point
        observer_point = self.observer_point,

        # Light source
        light_source = self.light_source = self.get_light_source()

        # Screen

        screen = self.screen = Rectangle(
            width = 0.05,
            height = self.screen_height,
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
        camera.set_height(1.5)
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
        self.play(*list(map(FadeOut, [screen_label, screen_arrow])))
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
            num_decimal_places = 0,
            unit = "^\\circ"
        )
        self.angle_indicator.next_to(self.angle_arc, RIGHT)

        angle_update_func = lambda x: self.light_source.spotlight.opening_angle() / DEGREES
        self.angle_indicator.add_updater(
            lambda d: d.set_value(angle_update_func())
        )
        self.add(self.angle_indicator)

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
            Mobject.add_updater(
                self.light_source,
                lambda m : m.update()
            ),
        )
        self.add(
            Mobject.add_updater(
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

    def get_light_source(self):
        light_source = LightSource(
            opacity_function = inverse_quadratic(1,2,1),
            num_levels = self.num_levels,
            radius = self.radius,
            max_opacity_ambient = AMBIENT_FULL,
        )
        light_source.move_source_to(self.source_point)
        return light_source

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
            ApplyMethod(ray.set_color, ray.target_color)
            for ray in rays
        ])
        self.wait()
        self.play(FadeOut(rays))

class EarthScene(IntroduceScreen):
    CONFIG = {
        "screen_height" : 0.5,
        "screen_thickness" : 0,
        "radius" : 100 + FRAME_X_RADIUS,
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
            height = FRAME_HEIGHT,
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
        )
        equator_arrow.next_to(screen.get_center(), UP+LEFT, SMALL_BUFF)
        pole_arrow = Vector(
            UP+3*RIGHT, 
            color = WHITE,
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

class ShowLightInThreeDimensions(IntroduceScreen, ThreeDScene):
    CONFIG = {
        "num_levels" : 200,
    }
    def construct(self):
        light_source = self.get_light_source()
        screens = VGroup(
            Square(),
            RegularPolygon(8),
            Circle().insert_n_curves(25),
        )
        for screen in screens:
            screen.set_height(self.screen_height)
        screens.rotate(TAU/4, UP)
        screens.next_to(self.observer_point, LEFT)
        screens.set_stroke(WHITE, 2)
        screens.set_fill(WHITE, 0.5)
        screen = screens[0]

        cone = ThreeDSpotlight(
            screen, light_source.ambient_light,
            light_source.get_source_point
        )
        cone_update_anim = ContinualThreeDLightConeUpdate(cone)

        self.add(light_source, screen, cone)
        self.add(cone_update_anim)
        self.move_camera(
            phi = 60*DEGREES,
            theta = -155*DEGREES,
            run_time = 3,
        )
        self.begin_ambient_camera_rotation()
        kwargs = {"run_time" : 2}
        self.play(screen.stretch, 0.5, 1, **kwargs)
        self.play(screen.stretch, 2, 2, **kwargs)
        self.play(Rotate(
            screen, TAU/4, 
            axis = UP+OUT, 
            rate_func = there_and_back, 
            run_time = 3,
        ))
        self.play(Transform(screen, screens[1], **kwargs))
        self.play(screen.stretch, 0.5, 2, **kwargs)
        self.play(Transform(screen, screens[2], **kwargs))
        self.wait(2)
        self.play(
            screen.stretch, 0.5, 1, 
            screen.stretch, 2, 2, 
            **kwargs
        )
        self.play(
            screen.stretch, 3, 1, 
            screen.stretch, 0.7, 2, 
            **kwargs
        )
        self.wait(2)

class LightInThreeDimensionsOverlay(Scene):
    def construct(self):
        words = TextMobject("""
            ``Solid angle'' \\\\
            (measured in ``steradians'')
        """)
        self.play(Write(words))
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

        spotlight_update = Mobject.add_updater(spotlight, update_spotlight)
        shadow_update = Mobject.add_updater(
            shadow, lambda m : light_source.update_shadow()
        )

        # Light indicator
        light_indicator = self.light_indicator = LightIndicator(
            opacity_for_unit_intensity = 0.5,
        )
        def update_light_indicator(light_indicator):
            distance = get_norm(screen.get_reference_point() - source_point)
            light_indicator.set_intensity(1.0/(distance/unit_distance)**2)
            light_indicator.next_to(morty, UP, MED_LARGE_BUFF)
        light_indicator_update = Mobject.add_updater(
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
        arrows.set_color(WHITE)
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

        cone = ThreeDSpotlight(
            new_screen, ambient_light,
            source_point_func = lambda : source_point
        )
        cone_update_anim = ContinualThreeDLightConeUpdate(cone)


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

        ## Create screen copies
        def get_screen_copy_group(distance):
            n = int(distance)**2
            copies = VGroup(*[new_screen.copy() for x in range(n)])
            copies.rotate(-TAU/4, axis = UP)
            copies.arrange_in_grid(buff = 0)
            copies.rotate(TAU/4, axis = UP)
            copies.move_to(source_point, IN)
            copies.shift(distance*RIGHT*unit_distance)
            return copies
        screen_copy_groups = list(map(get_screen_copy_group, list(range(1, 8))))
        def get_screen_copy_group_anim(n):
            group = screen_copy_groups[n]
            prev_group = screen_copy_groups[n-1]
            group.save_state()
            group.fade(1)
            group.replace(prev_group, dim_to_match = 1)
            return ApplyMethod(group.restore)

        # corner_directions = [UP+OUT, DOWN+OUT, DOWN+IN, UP+IN]
        # edge_directions = [
        #     UP, UP+OUT, OUT, DOWN+OUT, DOWN, DOWN+IN, IN, UP+IN, ORIGIN
        # ]

        # four_copies = VGroup(*[new_screen.copy() for x in range(4)])
        # nine_copies = VGroup(*[new_screen.copy() for x in range(9)])
        # def update_four_copies(four_copies):
        #     for mob, corner_direction in zip(four_copies, corner_directions):
        #         mob.move_to(new_screen, corner_direction)
        # four_copies_update_anim = UpdateFromFunc(four_copies, update_four_copies)
        # def update_nine_copies(nine_copies):
        #     for mob, corner_direction in zip(nine_copies, edge_directions):
        #         mob.move_to(new_screen, corner_direction)
        # nine_copies_update_anim = UpdateFromFunc(nine_copies, update_nine_copies)

        three_arrow = DoubleArrow(
            source_point + 4*DOWN,
            source_point + 4*DOWN + 3*unit_distance*RIGHT,
            buff = 0,
            color = WHITE
        )
        three = Integer(3)
        three.next_to(three_arrow, DOWN)

        new_screen.fade(1)
        # self.add(
        #     ContinualAnimation(screen_copy),
        #     ContinualAnimation(four_copies),
        # )

        self.add(ContinualAnimation(screen_copy_groups[0]))
        self.add(ContinualAnimation(screen_copy_groups[1]))
        self.play(
            new_screen.scale, 2, {"about_edge" : IN},
            new_screen.shift, unit_distance*RIGHT,
            get_screen_copy_group_anim(1),
            run_time = 2,
        )
        self.wait()
        self.move_camera(
            phi = 75*DEGREES,
            theta = -155*DEGREES,
            distance = 7,
            run_time = 10,
        )
        self.begin_ambient_camera_rotation(rate = -0.01)
        self.add(ContinualAnimation(screen_copy_groups[2]))
        self.play(
            new_screen.scale, 3./2, {"about_edge" : IN},
            new_screen.shift, unit_distance*RIGHT,
            get_screen_copy_group_anim(2),
            GrowFromPoint(three_arrow, three_arrow.get_left()),
            Write(three, rate_func = squish_rate_func(smooth, 0.5, 1)),
            run_time = 2,
        )
        self.begin_ambient_camera_rotation(rate = -0.01)
        self.play(LaggedStartMap(
            ApplyMethod, screen_copy_groups[2],
            lambda m : (m.set_color, RED),
            run_time = 5,
            rate_func = there_and_back,
        ))
        self.wait(2)
        self.move_camera(distance = 18)
        self.play(*[
            ApplyMethod(mob.fade, 1)
            for mob in screen_copy_groups[:2]
        ])
        last_group = screen_copy_groups[2]
        for n in range(4, len(screen_copy_groups)+1):
            group = screen_copy_groups[n-1]
            self.add(ContinualAnimation(group))
            self.play(
                new_screen.scale, float(n)/(n-1), {"about_edge" : IN},
                new_screen.shift, unit_distance*RIGHT,
                get_screen_copy_group_anim(n-1),
                last_group.fade, 1,
            )
            last_group = group
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

class OtherInstanceOfInverseSquareLaw(Scene):
    def construct(self):
        title = TextMobject("Where the inverse square law shows up")
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT).scale(FRAME_X_RADIUS)
        h_line.next_to(title, DOWN)
        self.add(title, h_line)

        items = VGroup(*[
            TextMobject("- %s"%s).scale(1)
            for s in [
                "Heat", "Sound", "Radio waves", "Electric fields",
            ]
        ])
        items.arrange(DOWN, buff = MED_LARGE_BUFF, aligned_edge = LEFT)
        items.next_to(h_line, DOWN, LARGE_BUFF)
        items.to_edge(LEFT)

        dot = Dot()
        dot.move_to(4*RIGHT)
        self.add(dot)
        def get_broadcast():
            return Broadcast(dot, big_radius = 5, run_time = 5)

        self.play(
            LaggedStartMap(FadeIn, items, run_time = 4, lag_ratio = 0.7),
            Succession(*[
                get_broadcast()
                for x in range(2)
            ])
        )
        self.play(get_broadcast())
        self.wait()

class ScreensIntroWrapper(TeacherStudentsScene):
    def construct(self):
        point = VectorizedPoint(FRAME_X_RADIUS*LEFT/2 + FRAME_Y_RADIUS*UP/2)
        self.play(self.teacher.change, "raise_right_hand")
        self.change_student_modes(
            "pondering", "erm", "confused",
            look_at_arg = point,
        )
        self.play(self.teacher.look_at, point)
        self.wait(5)

class ManipulateLightsourceSetups(PiCreatureScene):
    CONFIG = {
        "num_levels" : 100,
        "radius" : 10,
        "pi_creature_point" : 2*LEFT + 2*DOWN,
    }
    def construct(self):
        unit_distance = 3

        # Morty
        morty = self.pi_creature
        observer_point = morty.eyes[1].get_center()

        bubble = ThoughtBubble(height = 3, width = 4, direction = RIGHT)
        bubble.set_fill(BLACK, 1)
        bubble.pin_to(morty)

        # Indicator
        light_indicator = LightIndicator(
            opacity_for_unit_intensity = 0.5,
            fill_color = YELLOW,
            radius = 0.4,
            reading_height = 0.2,
        )
        light_indicator.move_to(bubble.get_bubble_center())
        def update_light_indicator(light_indicator):
            distance = get_norm(light_source.get_source_point()-observer_point)
            light_indicator.set_intensity((unit_distance/distance)**2)

        #Light source
        light_source = LightSource(
            opacity_function = inverse_quadratic(1,2,1),
            num_levels = self.num_levels,
            radius = self.radius,
            max_opacity_ambient = AMBIENT_FULL,
        )
        light_source.move_to(observer_point + unit_distance*RIGHT)

        #Light source copies
        light_source_copies = VGroup(*[light_source.copy() for x in range(2)])
        for lsc, vect in zip(light_source_copies, [RIGHT, UP]):
            lsc.move_to(observer_point + np.sqrt(2)*unit_distance*vect)

        self.add(light_source)
        self.add_foreground_mobjects(morty, bubble, light_indicator)
        self.add(Mobject.add_updater(light_indicator, update_light_indicator))
        self.play(
            ApplyMethod(
                light_source.shift, 0.66*unit_distance*LEFT,
                rate_func = wiggle,
                run_time = 5,
            ),
            morty.change, "erm",
        )
        self.play(
            UpdateFromAlphaFunc(
                light_source, 
                lambda ls, a : ls.move_to(
                    observer_point + rotate_vector(
                        unit_distance*RIGHT, (1+1./8)*a*TAU
                    )
                ),
                run_time = 6,
                rate_func = bezier([0, 0, 1, 1])
            ),
            morty.change, "pondering",
            UpdateFromFunc(morty, lambda m : m.look_at(light_source))
        )
        self.wait()

        plus = TexMobject("+")
        point = light_indicator.get_center()
        plus.move_to(point)
        light_indicator_copy = light_indicator.copy()
        self.add_foreground_mobjects(plus, light_indicator_copy)
        self.play(
            ReplacementTransform(
                light_source, light_source_copies[0]
            ),
            ReplacementTransform(
                light_source.copy().fade(1), 
                light_source_copies[1]
            ),
            FadeIn(plus),
            UpdateFromFunc(
                light_indicator_copy,
                lambda li : update_light_indicator(li),
            ),
            UpdateFromAlphaFunc(
                light_indicator, lambda m, a : m.move_to(
                    point + a*0.75*RIGHT,
                )
            ),
            UpdateFromAlphaFunc(
                light_indicator_copy, lambda m, a : m.move_to(
                    point + a*0.75*LEFT,
                )
            ),
            run_time = 2
        )
        self.play(morty.change, "hooray")
        self.wait(2)

    ##

    def create_pi_creature(self):
        morty = Mortimer()
        morty.flip()
        morty.scale(0.5)
        morty.move_to(self.pi_creature_point)
        return morty

class TwoLightSourcesScene(ManipulateLightsourceSetups):
    CONFIG = {
        "num_levels" : 200,
        "radius" : 15,
        "a" : 9,
        "b" : 5,
        "origin_point" : 5*LEFT + 2.5*DOWN
    }
    def construct(self):
        MAX_OPACITY = 0.4
        INDICATOR_RADIUS = 0.6
        OPACITY_FOR_UNIT_INTENSITY = 0.5
        origin_point = self.origin_point

        #Morty
        morty = self.pi_creature
        morty.change("hooray") # From last scen
        morty.generate_target()
        morty.target.change("plain")
        morty.target.scale(0.6)
        morty.target.next_to(
            origin_point, LEFT, buff = 0, 
            submobject_to_align = morty.target.eyes[1]
        )

        #Axes
        axes = Axes(
            x_min = -1, x_max = 10.5,
            y_min = -1, y_max = 6.5,
        )
        axes.shift(origin_point)

        #Important reference points
        A = axes.coords_to_point(self.a, 0)
        B = axes.coords_to_point(0, self.b)
        C = axes.coords_to_point(0, 0)
        xA = A[0]
        yA = A[1]
        xB = B[0]
        yB = B[1]
        xC = C[0]
        yC = C[1]
        # find the coords of the altitude point H
        # as the solution of a certain LSE
        prelim_matrix = np.array([
            [yA - yB, xB - xA], 
            [xA - xB, yA - yB]
        ]) # sic
        prelim_vector = np.array(
            [xB * yA - xA * yB, xC * (xA - xB) + yC * (yA - yB)]
        )
        H2 = np.linalg.solve(prelim_matrix, prelim_vector)
        H = np.append(H2, 0.)

        #Lightsources
        lsA = LightSource(
            radius = self.radius, 
            num_levels = self.num_levels,
            opacity_function = inverse_power_law(2, 1, 1, 1.5),
        )
        lsB = lsA.deepcopy()
        lsA.move_source_to(A)
        lsB.move_source_to(B)
        lsC = lsA.deepcopy()
        lsC.move_source_to(H)

        #Lighthouse labels
        A_label = TextMobject("A")
        A_label.next_to(lsA.lighthouse, RIGHT)
        B_label = TextMobject("B")
        B_label.next_to(lsB.lighthouse, LEFT)

        #Identical lighthouse labels
        identical_lighthouses_words = TextMobject("All identical \\\\ lighthouses")
        identical_lighthouses_words.to_corner(UP+RIGHT)
        identical_lighthouses_words.shift(LEFT)
        identical_lighthouses_arrows = VGroup(*[
            Arrow(
                identical_lighthouses_words.get_corner(DOWN+LEFT),
                ls.get_source_point(), 
                buff = SMALL_BUFF,
                color = WHITE,
            )
            for ls in (lsA, lsB, lsC)
        ])

        #Lines
        line_a = Line(C, A)
        line_a.set_color(BLUE)
        line_b = Line(C, B)
        line_b.set_color(RED)
        line_c = Line(A, B)
        line_h = Line(H, C)
        line_h.set_color(GREEN)

        label_a = TexMobject("a")
        label_a.match_color(line_a)
        label_a.next_to(line_a, DOWN, buff = SMALL_BUFF)
        label_b = TexMobject("b")
        label_b.match_color(line_b)
        label_b.next_to(line_b, LEFT, buff = SMALL_BUFF)
        label_h = TexMobject("h")
        label_h.match_color(line_h)
        label_h.next_to(line_h.get_center(), RIGHT, buff = SMALL_BUFF)

        perp_mark = VMobject().set_points_as_corners([
            RIGHT, RIGHT+DOWN, DOWN
        ])
        perp_mark.scale(0.25, about_point = ORIGIN)
        perp_mark.rotate(line_c.get_angle() + TAU/4, about_point = ORIGIN)
        perp_mark.shift(H)
        # perp_mark.set_color(BLACK)

        #Indicators
        indicator = LightIndicator(
            color = LIGHT_COLOR,
            radius = INDICATOR_RADIUS,
            opacity_for_unit_intensity = OPACITY_FOR_UNIT_INTENSITY,
            show_reading = True,
            precision = 2,
        )
        indicator.next_to(origin_point, UP+LEFT)
        def update_indicator(indicator):
            intensity = 0
            for ls in lsA, lsB, lsC:
                if ls in self.mobjects:
                    distance = get_norm(ls.get_source_point() - origin_point)
                    d_indensity = fdiv(
                        3./(distance**2),
                        indicator.opacity_for_unit_intensity
                    )
                    d_indensity *= ls.ambient_light.submobjects[1].get_fill_opacity()
                    intensity += d_indensity
            indicator.set_intensity(intensity)
        indicator_update_anim = Mobject.add_updater(indicator, update_indicator)

        new_indicator = indicator.copy()
        new_indicator.light_source = lsC
        new_indicator.measurement_point = C

        #Note sure what this is...
        distance1 = get_norm(origin_point - lsA.get_source_point())
        intensity = lsA.ambient_light.opacity_function(distance1) / indicator.opacity_for_unit_intensity
        distance2 = get_norm(origin_point - lsB.get_source_point())
        intensity += lsB.ambient_light.opacity_function(distance2) / indicator.opacity_for_unit_intensity

        # IPT Theorem
        theorem = TexMobject(
            "{1 \over ", "a^2}", "+", 
            "{1 \over", "b^2}", "=", "{1 \over","h^2}"
        )
        theorem.set_color_by_tex_to_color_map({
            "a" : line_a.get_color(),
            "b" : line_b.get_color(),
            "h" : line_h.get_color(),
        })
        theorem_name = TextMobject("Inverse Pythagorean Theorem")
        theorem_name.to_corner(UP+RIGHT)
        theorem.next_to(theorem_name, DOWN, buff = MED_LARGE_BUFF)
        theorem_box = SurroundingRectangle(theorem, color = WHITE)

        #Transition from last_scene
        self.play(
            ShowCreation(axes, run_time = 2),
            MoveToTarget(morty),
            FadeIn(indicator),
        )

        #Move lsC around
        self.add(lsC)
        indicator_update_anim.update(0)
        intensity = indicator.reading.number
        self.play(
            SwitchOn(lsC.ambient_light),
            FadeIn(lsC.lighthouse),
            UpdateFromAlphaFunc(
                indicator, lambda i, a : i.set_intensity(a*intensity)
            )
        )
        self.add(indicator_update_anim)
        self.play(Animation(lsC), run_time = 0) #Why is this needed?
        for point in axes.coords_to_point(5, 2), H:
            self.play(
                lsC.move_source_to, point,
                path_arc = TAU/4,
                run_time = 1.5,
            )
        self.wait()

        # Draw line
        self.play(
            ShowCreation(line_h),
            morty.change, "pondering"
        )
        self.wait()
        self.play(
            ShowCreation(line_c),
            ShowCreation(perp_mark)
        )
        self.wait()
        self.add_foreground_mobjects(line_c, line_h)

        #Add alternate light_sources
        for ls in lsA, lsB:
            ls.save_state()
            ls.move_to(lsC)
            ls.fade(1)
            self.add(ls)
            self.play(
                ls.restore, 
                run_time = 2
            )
        self.wait()
        A_label.save_state()
        A_label.center().fade(1)
        self.play(A_label.restore)
        self.wait()
        self.play(ReplacementTransform(
            A_label.copy().fade(1), B_label
        ))
        self.wait(2)

        #Compare combined of laA + lsB with lsC
        rect = SurroundingRectangle(indicator, color = RED)
        self.play(
            FadeOut(lsA),
            FadeOut(lsB),
        )
        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))
        self.play(FadeOut(lsC))
        self.add(lsA, lsB)
        self.play(
            FadeIn(lsA),
            FadeIn(lsB),
        )
        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))
        self.wait(2)

        # All standard lighthouses
        self.add(lsC)
        self.play(FadeIn(lsC))
        self.play(
            Write(identical_lighthouses_words),
            LaggedStartMap(GrowArrow, identical_lighthouses_arrows)
        )
        self.wait()
        self.play(*list(map(FadeOut, [
            identical_lighthouses_words,
            identical_lighthouses_arrows,
        ])))

        #Show labels of lengths
        self.play(ShowCreation(line_a), Write(label_a))
        self.wait()
        self.play(ShowCreation(line_b), Write(label_b))
        self.wait()
        self.play(Write(label_h))
        self.wait()

        #Write IPT
        a_part = theorem[:2]
        b_part = theorem[2:5]
        h_part = theorem[5:]
        for part in a_part, b_part, h_part:
            part.save_state()
            part.scale(3)
            part.fade(1)
        a_part.move_to(lsA)
        b_part.move_to(lsB)
        h_part.move_to(lsC)

        self.play(*list(map(FadeOut, [lsA, lsB, lsC, indicator])))
        for ls, part in (lsA, a_part), (lsB, b_part), (lsC, h_part):
            self.add(ls)
            self.play(
                SwitchOn(ls.ambient_light, run_time = 2),
                FadeIn(ls.lighthouse),
                part.restore
            )
        self.wait()
        self.play(
            Write(theorem_name),
            ShowCreation(theorem_box)
        )
        self.play(morty.change, "confused")
        self.wait(2)

class MathologerVideoWrapper(Scene):
    def construct(self):
        title = TextMobject("""
            Mathologer's excellent video on \\\\
            the many Pythagorean theorem cousins
        """)
        # title.scale(0.7)
        title.to_edge(UP)
        logo = ImageMobject("mathologer_logo")
        logo.set_height(1)
        logo.to_corner(UP+LEFT)
        logo.shift(FRAME_WIDTH*RIGHT)
        screen = ScreenRectangle(height = 5.5)
        screen.next_to(title, DOWN)

        self.play(
            logo.shift, FRAME_WIDTH*LEFT,
            LaggedStartMap(FadeIn, title),
            run_time = 2
        )
        self.play(ShowCreation(screen))
        self.wait(5)

class SimpleIPTProof(Scene):
    def construct(self):
        A = 5*RIGHT
        B = 3*UP
        C = ORIGIN
        #Dumb and inefficient
        alphas = np.linspace(0, 1, 500)
        i = np.argmin([get_norm(interpolate(A, B, a)) for a in alphas])
        H = interpolate(A, B, alphas[i])
        triangle = VGroup(
            Line(C, A, color = BLUE),
            Line(C, B, color = RED),
            Line(A, B, color = WHITE),
            Line(C, H, color = GREEN)
        )
        for line, char in zip(triangle, ["a", "b", "c", "h"]):
            label = TexMobject(char)
            label.match_color(line)
            vect = line.get_center() - triangle.get_center()
            vect /= get_norm(vect)
            label.next_to(line.get_center(), vect)
            triangle.add(label)
            if char == "h":
                label.next_to(line.get_center(), UP+LEFT, SMALL_BUFF)

        triangle.to_corner(UP+LEFT)
        self.add(triangle)

        argument_lines = VGroup(
            TexMobject(
                "\\text{Area} = ", 
                "{1 \\over 2}", "a", "b", "=",
                "{1 \\over 2}", "c", "h"
            ),
            TexMobject("\\Downarrow"),
            TexMobject("a^2", "b^2", "=", "c^2", "h^2"),
            TexMobject("\\Downarrow"),
            TexMobject(
                "a^2", "b^2", "=", 
                "(",  "a^2", "+", "b^2", ")", "h^2"
            ),
            TexMobject("\\Downarrow"),
            TexMobject(
                "{1 \\over ", "h^2}", "=", 
                "{1 \\over ", "b^2}", "+", 
                "{1 \\over ", "a^2}",
            ),
        )
        argument_lines.arrange(DOWN)
        for line in argument_lines:
            line.set_color_by_tex_to_color_map({
                "a" : BLUE,
                "b" : RED,
                "h" : GREEN,
                "Area" : WHITE,
                "Downarrow" : WHITE,
            })
            all_equals = line.get_parts_by_tex("=")
            if all_equals:
                line.alignment_mob = all_equals[-1]
            else:
                line.alignment_mob = line[0]
            line.shift(-line.alignment_mob.get_center()[0]*RIGHT)
        argument_lines.next_to(triangle, RIGHT)
        argument_lines.to_edge(UP)

        prev_line = argument_lines[0]
        self.play(FadeIn(prev_line))
        for arrow, line in zip(argument_lines[1::2], argument_lines[2::2]):
            line.save_state()
            line.shift(
                prev_line.alignment_mob.get_center() - \
                line.alignment_mob.get_center() 
            )
            line.fade(1)
            self.play(
                line.restore,
                GrowFromPoint(arrow, arrow.get_top())
            )
            self.wait()
            prev_line = line

class WeCanHaveMoreFunThanThat(TeacherStudentsScene):
    def construct(self):
        point = VectorizedPoint(FRAME_X_RADIUS*LEFT/2 + FRAME_Y_RADIUS*UP/2)
        self.teacher_says(
            "We can have \\\\ more fun than that!",
            target_mode = "hooray"
        )
        self.change_student_modes(*3*["erm"], look_at_arg = point)
        self.wait()
        self.play(
            RemovePiCreatureBubble(
                self.teacher, 
                target_mode = "raise_right_hand",
                look_at_arg = point,
            ),
            self.get_student_changes(*3*["pondering"], look_at_arg = point)
        )
        self.wait(3)

class IPTScene(TwoLightSourcesScene, ZoomedScene):
    CONFIG = {
        "max_opacity_ambient" : 0.2,
        "num_levels" : 200,
    }
    def construct(self):
        #Copy pasting from TwoLightSourcesScene....Very bad...
        origin_point = self.origin_point
        self.remove(self.pi_creature)

        #Axes
        axes = Axes(
            x_min = -1, x_max = 10.5,
            y_min = -1, y_max = 6.5,
        )
        axes.shift(origin_point)

        #Important reference points
        A = axes.coords_to_point(self.a, 0)
        B = axes.coords_to_point(0, self.b)
        C = axes.coords_to_point(0, 0)
        xA = A[0]
        yA = A[1]
        xB = B[0]
        yB = B[1]
        xC = C[0]
        yC = C[1]
        # find the coords of the altitude point H
        # as the solution of a certain LSE
        prelim_matrix = np.array([
            [yA - yB, xB - xA], 
            [xA - xB, yA - yB]
        ]) # sic
        prelim_vector = np.array(
            [xB * yA - xA * yB, xC * (xA - xB) + yC * (yA - yB)]
        )
        H2 = np.linalg.solve(prelim_matrix, prelim_vector)
        H = np.append(H2, 0.)

        #Lightsources
        lsA = LightSource(
            radius = self.radius, 
            num_levels = self.num_levels,
            opacity_function = inverse_power_law(2, 1, 1, 1.5),
            max_opacity_ambient = self.max_opacity_ambient,
        )
        lsA.lighthouse.scale(0.5, about_edge = UP)
        lsB = lsA.deepcopy()
        lsA.move_source_to(A)
        lsB.move_source_to(B)
        lsC = lsA.deepcopy()
        lsC.move_source_to(H)

        #Lighthouse labels
        A_label = TextMobject("A")
        A_label.next_to(lsA.lighthouse, RIGHT)
        B_label = TextMobject("B")
        B_label.next_to(lsB.lighthouse, LEFT)

        #Lines
        line_a = Line(C, A)
        line_a.set_color(BLUE)
        line_b = Line(C, B)
        line_b.set_color(RED)
        line_c = Line(A, B)
        line_h = Line(H, C)
        line_h.set_color(GREEN)

        label_a = TexMobject("a")
        label_a.match_color(line_a)
        label_a.next_to(line_a, DOWN, buff = SMALL_BUFF)
        label_b = TexMobject("b")
        label_b.match_color(line_b)
        label_b.next_to(line_b, LEFT, buff = SMALL_BUFF)
        label_h = TexMobject("h")
        label_h.match_color(line_h)
        label_h.next_to(line_h.get_center(), RIGHT, buff = SMALL_BUFF)

        perp_mark = VMobject().set_points_as_corners([
            RIGHT, RIGHT+DOWN, DOWN
        ])
        perp_mark.scale(0.25, about_point = ORIGIN)
        perp_mark.rotate(line_c.get_angle() + TAU/4, about_point = ORIGIN)
        perp_mark.shift(H)

        # Mini triangle
        m_hyp_a = Line(H, A)
        m_a = line_a.copy()
        m_hyp_b = Line(H, B)
        m_b = line_b.copy()
        mini_triangle = VGroup(m_a, m_hyp_a, m_b, m_hyp_b)
        mini_triangle.set_stroke(width = 5)

        mini_triangle.generate_target()
        mini_triangle.target.scale(0.1, about_point = origin_point)
        for part, part_target in zip(mini_triangle, mini_triangle.target):
            part.target = part_target

        # Screen label
        screen_word = TextMobject("Screen")
        screen_word.next_to(mini_triangle.target, UP+RIGHT, LARGE_BUFF)
        screen_arrow = Arrow(
            screen_word.get_bottom(),
            mini_triangle.target.get_center(),
            color = WHITE,
        )

        # IPT Theorem
        theorem = TexMobject(
            "{1 \over ", "a^2}", "+", 
            "{1 \over", "b^2}", "=", "{1 \over","h^2}"
        )
        theorem.set_color_by_tex_to_color_map({
            "a" : line_a.get_color(),
            "b" : line_b.get_color(),
            "h" : line_h.get_color(),
        })
        theorem_name = TextMobject("Inverse Pythagorean Theorem")
        theorem_name.to_corner(UP+RIGHT)
        theorem.next_to(theorem_name, DOWN, buff = MED_LARGE_BUFF)
        theorem_box = SurroundingRectangle(theorem, color = WHITE)

        # Setup spotlights
        spotlight_a = VGroup()
        spotlight_a.screen = m_hyp_a
        spotlight_b = VGroup()
        spotlight_b.screen = m_hyp_b
        for spotlight in spotlight_a, spotlight_b:
            spotlight.get_source_point = lsC.get_source_point
        dr = lsC.ambient_light.radius/lsC.ambient_light.num_levels
        def update_spotlight(spotlight):
            spotlight.submobjects = []
            source_point = spotlight.get_source_point()
            c1, c2 = spotlight.screen.get_start(), spotlight.screen.get_end()
            distance = max(
                get_norm(c1 - source_point),
                get_norm(c2 - source_point),
            )
            n_parts = np.ceil(distance/dr)
            alphas = np.linspace(0, 1, n_parts+1)
            for a1, a2 in zip(alphas, alphas[1:]):
                spotlight.add(Polygon(
                    interpolate(source_point, c1, a1),
                    interpolate(source_point, c1, a2),
                    interpolate(source_point, c2, a2),
                    interpolate(source_point, c2, a1),
                    fill_color = YELLOW,
                    fill_opacity = 2*lsC.ambient_light.opacity_function(a1*distance),
                    stroke_width = 0
                ))

        def update_spotlights(spotlights):
            for spotlight in spotlights:
                update_spotlight(spotlight)

        def get_spotlight_triangle(spotlight):
            sp = spotlight.get_source_point()
            c1 = spotlight.screen.get_start()
            c2 = spotlight.screen.get_end()
            return Polygon(
                sp, c1, c2,
                stroke_width = 0,
                fill_color = YELLOW,
                fill_opacity = 0.5,
            )

        spotlights = VGroup(spotlight_a, spotlight_b)
        spotlights_update_anim = Mobject.add_updater(
            spotlights, update_spotlights
        )

        # Add components
        self.add(
            axes,
            lsA.ambient_light,
            lsB.ambient_light,
            lsC.ambient_light,
            line_c,
        )
        self.add_foreground_mobjects(
            lsA.lighthouse, A_label,
            lsB.lighthouse, B_label,
            lsC.lighthouse,  line_h,
            theorem, theorem_name, theorem_box,
        )

        # Show miniature triangle
        self.play(ShowCreation(mini_triangle, lag_ratio = 0))
        self.play(
            MoveToTarget(mini_triangle),
            run_time = 2,
        )
        self.add_foreground_mobject(mini_triangle)

        # Show beams of light
        self.play(
            Write(screen_word),
            GrowArrow(screen_arrow),
        )
        self.wait()
        spotlights_update_anim.update(0)
        self.play(
            LaggedStartMap(FadeIn, spotlight_a),
            LaggedStartMap(FadeIn, spotlight_b),
            Animation(screen_arrow),
        )
        self.add(spotlights_update_anim)
        self.play(*list(map(FadeOut, [screen_word, screen_arrow])))
        self.wait()

        # Reshape screen
        m_hyps = [m_hyp_a, m_hyp_b]
        for hyp, line in (m_hyp_a, m_a), (m_hyp_b, m_b):
            hyp.save_state()
            hyp.alt_version = line.copy()
            hyp.alt_version.set_color(WHITE)

        for x in range(2):
            self.play(*[
                Transform(m, m.alt_version)
                for m in m_hyps
            ])
            self.wait()
            self.play(*[m.restore for m in m_hyps])
            self.wait()

        # Show spotlight a key point
        def show_beaming_light(spotlight):
            triangle = get_spotlight_triangle(spotlight)
            for x in range(3):
                anims = []
                if x > 0:
                    anims.append(FadeOut(triangle.copy()))
                anims.append(GrowFromPoint(triangle, triangle.points[0]))
                self.play(*anims)
            self.play(FadeOut(triangle))
            pass

        def show_key_point(spotlight, new_point):
            screen = spotlight.screen
            update_spotlight_anim = UpdateFromFunc(spotlight, update_spotlight)
            self.play(
                Transform(screen, screen.alt_version),
                update_spotlight_anim,
            )
            show_beaming_light(spotlight)
            self.play(screen.restore, update_spotlight_anim)
            self.wait()
            self.play(
                lsC.move_source_to, new_point,
                Transform(screen, screen.alt_version),
                update_spotlight_anim,
                run_time = 2
            )
            show_beaming_light(spotlight)
            self.wait()
            self.play(
                lsC.move_source_to, H,
                screen.restore,
                update_spotlight_anim,
                run_time = 2
            )
            self.wait()

        self.remove(spotlights_update_anim)
        self.add(spotlight_b)
        self.play(*list(map(FadeOut, [
            spotlight_a, lsA.ambient_light, lsB.ambient_light
        ])))
        show_key_point(spotlight_b, A)
        self.play(
            FadeOut(spotlight_b),
            FadeIn(spotlight_a),
        )
        show_key_point(spotlight_a, B)
        self.wait()

class HomeworkWrapper(Scene):
    def construct(self):
        title = TextMobject("Homework")
        title.to_edge(UP)
        screen = ScreenRectangle(height = 6)
        screen.center()
        self.add(title)
        self.play(ShowCreation(screen))
        self.wait(5)

class HeresWhereThingsGetGood(TeacherStudentsScene):
    def construct(self):
        self.teacher_says("Now for the \\\\ good part!")
        self.change_student_modes(*["hooray"]*3)
        self.change_student_modes(*["happy"]*3)
        self.wait()

class DiameterTheorem(TeacherStudentsScene):
    def construct(self):
        circle = Circle(radius = 2, color = WHITE)
        circle.next_to(self.students[2], UP)
        self.add(circle)

        center = Dot(circle.get_center(), color = WHITE)
        self.add_foreground_mobject(center)

        diameter_word = TextMobject("Diameter")
        diameter_word.next_to(center, DOWN, SMALL_BUFF)

        point = VectorizedPoint(circle.get_top())
        triangle = Polygon(LEFT, RIGHT, UP)
        triangle.set_stroke(BLUE)
        triangle.set_fill(WHITE, 0.5)
        def update_triangle(triangle):
            triangle.set_points_as_corners([
                circle.get_left(), circle.get_right(),
                point.get_center(), circle.get_left(),
            ])
        triangle_update_anim = Mobject.add_updater(
            triangle, update_triangle
        )
        triangle_update_anim.update(0)

        perp_mark = VMobject()
        perp_mark.set_points_as_corners([LEFT, DOWN, RIGHT])
        perp_mark.shift(DOWN)
        perp_mark.scale(0.15, about_point = ORIGIN)
        perp_mark.shift(point.get_center())
        perp_mark.add(point.copy())

        self.play(
            self.teacher.change, "raise_right_hand",
            DrawBorderThenFill(triangle),
            Write(diameter_word),
        )
        self.play(
            ShowCreation(perp_mark),
            self.get_student_changes(*["pondering"]*3)
        )
        self.add_foreground_mobjects(perp_mark)
        self.add(triangle_update_anim)
        for angle in 0.2*TAU, -0.4*TAU, 0.3*TAU:
            point.generate_target()
            point.target.rotate(angle, about_point = circle.get_center())

            perp_mark.generate_target()
            perp_mark.target.rotate(angle/2)
            perp_mark.target.shift(
                point.target.get_center() - \
                perp_mark.target[1].get_center()
            )

            self.play(
                MoveToTarget(point),
                MoveToTarget(perp_mark),
                path_arc = angle,
                run_time = 3,
            )

class InscribedeAngleThreorem(TeacherStudentsScene):
    def construct(self):
        circle = Circle(radius = 2, color = WHITE)
        circle.next_to(self.students[2], UP)
        self.add(circle)

        title = TextMobject("Inscribed angle \\\\ theorem")
        title.to_corner(UP+LEFT)
        self.add(title)

        center = Dot(circle.get_center(), color = WHITE)
        self.add_foreground_mobject(center)

        point = VectorizedPoint(circle.get_left())
        shape = Polygon(UP+LEFT, ORIGIN, DOWN+LEFT, RIGHT)
        shape.set_stroke(BLUE)
        def update_shape(shape):
            shape.set_points_as_corners([
                point.get_center(),
                circle.point_from_proportion(7./8), 
                circle.get_center(),
                circle.point_from_proportion(1./8), 
                point.get_center(),
            ])
        shape_update_anim = Mobject.add_updater(
            shape, update_shape
        )
        shape_update_anim.update(0)

        angle_mark = Arc(start_angle = -TAU/8, angle = TAU/4)
        angle_mark.scale(0.3, about_point = ORIGIN)
        angle_mark.shift(circle.get_center())
        theta = TexMobject("\\theta").set_color(RED)
        theta.next_to(angle_mark, RIGHT, MED_SMALL_BUFF)
        angle_mark.match_color(theta)

        half_angle_mark = Arc(start_angle = -TAU/16, angle = TAU/8)
        half_angle_mark.scale(0.3, about_point = ORIGIN)
        half_angle_mark.shift(point.get_center())
        half_angle_mark.add(point.copy())
        theta_halves = TexMobject("\\theta/2").set_color(GREEN)
        theta_halves.scale(0.7)
        half_angle_mark.match_color(theta_halves)
        theta_halves_update = UpdateFromFunc(
            theta_halves, lambda m : m.move_to(interpolate(
                point.get_center(), 
                half_angle_mark.point_from_proportion(0.5),
                2.5,
            ))
        )
        theta_halves_update.update(0)

        self.play(
            self.teacher.change, "raise_right_hand",
            ShowCreation(shape, rate_func=linear),
        )
        self.play(*list(map(FadeIn, [angle_mark, theta])))
        self.play(
            ShowCreation(half_angle_mark),
            Write(theta_halves),
            self.get_student_changes(*["pondering"]*3)
        )
        self.add_foreground_mobjects(half_angle_mark, theta_halves)
        self.add(shape_update_anim)
        for angle in 0.25*TAU, -0.4*TAU, 0.3*TAU, -0.35*TAU:
            point.generate_target()
            point.target.rotate(angle, about_point = circle.get_center())

            half_angle_mark.generate_target()
            half_angle_mark.target.rotate(angle/2)
            half_angle_mark.target.shift(
                point.target.get_center() - \
                half_angle_mark.target[1].get_center()
            )

            self.play(
                MoveToTarget(point),
                MoveToTarget(half_angle_mark),
                theta_halves_update,
                path_arc = angle,
                run_time = 3,
            )

class PondScene(ThreeDScene):
    def construct(self):

        BASELINE_YPOS = -2.5
        OBSERVER_POINT = np.array([0,BASELINE_YPOS,0])
        LAKE0_RADIUS = 1.5
        INDICATOR_RADIUS = 0.6
        TICK_SIZE = 0.5
        LIGHTHOUSE_HEIGHT = 0.5
        LAKE_COLOR = BLUE
        LAKE_OPACITY = 0.15
        LAKE_STROKE_WIDTH = 5.0
        LAKE_STROKE_COLOR = BLUE
        TEX_SCALE = 0.8
        DOT_COLOR = BLUE

        LIGHT_MAX_INT = 1
        LIGHT_SCALE = 2.5
        LIGHT_CUTOFF = 1

        RIGHT_ANGLE_SIZE = 0.3

        self.cumulated_zoom_factor = 1

        def right_angle(pointA, pointB, pointC, size = 1):

            v1 = pointA - pointB
            v1 = size * v1/get_norm(v1)
            v2 = pointC - pointB
            v2 = size * v2/get_norm(v2)
            
            P = pointB
            Q = pointB + v1
            R = Q + v2
            S = R - v1
            angle_sign = VMobject()
            angle_sign.set_points_as_corners([P,Q,R,S,P])
            angle_sign.mark_paths_closed = True
            angle_sign.set_fill(color = WHITE, opacity = 1)
            angle_sign.set_stroke(width = 0)
            return angle_sign

        def triangle(pointA, pointB, pointC):

            mob = VMobject()
            mob.set_points_as_corners([pointA, pointB, pointC, pointA])
            mob.mark_paths_closed = True
            mob.set_fill(color = WHITE, opacity = 0.5)
            mob.set_stroke(width = 0)
            return mob

        def zoom_out_scene(factor):

            self.remove_foreground_mobject(self.ls0_dot)
            self.remove(self.ls0_dot)

            phi0 = self.camera.get_phi() # default is 0 degs
            theta0 = self.camera.get_theta() # default is -90 degs
            distance0 = self.camera.get_distance()

            distance1 = 2 * distance0
            camera_target_point = self.camera.get_spherical_coords(phi0, theta0, distance1)

            self.play(
                ApplyMethod(self.camera.rotation_mobject.move_to, camera_target_point),
                self.zoomable_mobs.shift, self.obs_dot.get_center(),
                self.unzoomable_mobs.scale,2,{"about_point" : ORIGIN},
            )

            self.cumulated_zoom_factor *= factor

            # place ls0_dot by hand
            #old_radius = self.ls0_dot.radius
            #self.ls0_dot.radius = 2 * old_radius

            #v = self.ls0_dot.get_center() - self.obs_dot.get_center()
            #self.ls0_dot.shift(v)
            #self.ls0_dot.move_to(self.outer_lake.get_center())
            self.ls0_dot.scale(2, about_point = ORIGIN)
                
            #self.add_foreground_mobject(self.ls0_dot)

        def shift_scene(v):
            self.play(
                self.zoomable_mobs.shift,v,
                self.unzoomable_mobs.shift,v
            )

        self.zoomable_mobs = VMobject()
        self.unzoomable_mobs = VMobject()

        baseline = VMobject()
        baseline.set_points_as_corners([[-8,BASELINE_YPOS,0],[8,BASELINE_YPOS,0]])
        baseline.set_stroke(width = 0) # in case it gets accidentally added to the scene
        self.zoomable_mobs.add(baseline) # prob not necessary

        obs_dot = self.obs_dot = Dot(OBSERVER_POINT, fill_color = DOT_COLOR)
        ls0_dot = self.ls0_dot = Dot(OBSERVER_POINT + 2 * LAKE0_RADIUS * UP, fill_color = WHITE)
        self.unzoomable_mobs.add(self.obs_dot)#, self.ls0_dot)

        # lake
        lake0 = Circle(radius = LAKE0_RADIUS,
            stroke_width = 0,
            fill_color = LAKE_COLOR,
            fill_opacity = LAKE_OPACITY
        )
        lake0.move_to(OBSERVER_POINT + LAKE0_RADIUS * UP)
        self.zoomable_mobs.add(lake0)

        # Morty and indicator
        morty = Mortimer().flip().scale(0.3)
        morty.next_to(OBSERVER_POINT,DOWN)
        indicator = LightIndicator(precision = 2,
            radius = INDICATOR_RADIUS,
            show_reading  = False,
            color = LIGHT_COLOR
        )
        indicator.next_to(morty,LEFT)
        self.unzoomable_mobs.add(morty, indicator)

        # first lighthouse
        original_op_func = inverse_quadratic(LIGHT_MAX_INT,LIGHT_SCALE,LIGHT_CUTOFF)
        ls0 = LightSource(opacity_function = original_op_func, radius = 15.0, num_levels = 150)
        ls0.lighthouse.set_height(LIGHTHOUSE_HEIGHT)
        ls0.lighthouse.height = LIGHTHOUSE_HEIGHT
        ls0.move_source_to(OBSERVER_POINT + LAKE0_RADIUS * 2 * UP)
        self.zoomable_mobs.add(ls0, ls0.lighthouse, ls0.ambient_light)

        # self.add(lake0, morty, obs_dot, ls0_dot, ls0.lighthouse)

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

        # New introduction
        lake0.save_state()
        morty.save_state()
        lake0.set_height(6)
        morty.to_corner(UP+LEFT)
        morty.fade(1)
        lake0.center()

        lake_word = TextMobject("Lake")
        lake_word.scale(2)
        lake_word.move_to(lake0)

        self.play(
            DrawBorderThenFill(lake0, stroke_width = 1),
            Write(lake_word)
        )
        self.play(
            lake0.restore,
            lake_word.scale, 0.5, {"about_point" : lake0.get_bottom()},
            lake_word.fade, 1
        )
        self.remove(lake_word)
        self.play(morty.restore)
        self.play(
            GrowFromCenter(obs_dot),
            GrowFromCenter(ls0_dot),
            FadeIn(ls0.lighthouse)
        )
        self.add_foreground_mobjects(ls0.lighthouse, obs_dot, ls0_dot)
        self.play(
            SwitchOn(ls0.ambient_light),
            Animation(ls0.lighthouse),
        )
        self.wait()
        self.play(
            morty.move_to, ls0.lighthouse, 
            run_time = 3,
            path_arc = TAU/2,
            rate_func = there_and_back
        )

        self.play(
            ShowCreation(arc_right),
            Write(one_right),
        )
        self.play(
            ShowCreation(arc_left),
            Write(one_left),
        )
        self.play(
            lake0.set_stroke, {
                "color": LAKE_STROKE_COLOR, 
                "width" : LAKE_STROKE_WIDTH
            },
        )
        self.wait()
        self.add_foreground_mobjects(morty)


        # Show indicator
        self.play(FadeIn(indicator))

        self.play(indicator.set_intensity, 0.5)

        diameter_start = interpolate(OBSERVER_POINT,ls0.get_source_point(),0.02)
        diameter_stop = interpolate(OBSERVER_POINT,ls0.get_source_point(),0.98)

        # diameter
        diameter = DoubleArrow(diameter_start,
            diameter_stop,
            buff = 0,
            color = WHITE,
        )
        diameter_text = TexMobject("d").scale(TEX_SCALE)
        diameter_text.next_to(diameter,RIGHT)

        self.play(
            GrowFromCenter(diameter),
            Write(diameter_text),
            #FadeOut(self.obs_dot),
            FadeOut(ls0_dot)
        )
        self.wait()

        indicator_reading = TexMobject("{1 \over d^2}").scale(TEX_SCALE)
        indicator_reading.move_to(indicator)
        self.unzoomable_mobs.add(indicator_reading)

        self.play(
            ReplacementTransform(
                diameter_text[0].copy(),
                indicator_reading[2],
            ),
            FadeIn(indicator_reading)
        )
        self.wait()

        # replace d with its value
        new_diameter_text = TexMobject("{2 \over \pi}").scale(TEX_SCALE)
        new_diameter_text.color = LAKE_COLOR
        new_diameter_text.move_to(diameter_text)
        self.play(FadeOut(diameter_text))
        self.play(FadeIn(new_diameter_text))
        self.wait(2)

        # insert into indicator reading
        new_reading = TexMobject("{\pi^2 \over 4}").scale(TEX_SCALE)
        new_reading.move_to(indicator)
        new_diameter_text_copy = new_diameter_text.copy()
        new_diameter_text_copy.submobjects.reverse()

        self.play(
            FadeOut(indicator_reading),
            ReplacementTransform(
                new_diameter_text_copy,
                new_reading,
                parth_arc = 30*DEGREES
            )
        )
        indicator_reading = new_reading

        self.wait(2)

        self.play(
            FadeOut(one_left),
            FadeOut(one_right),
            FadeOut(new_diameter_text),
            FadeOut(arc_left),
            FadeOut(arc_right)
        )
        self.add_foreground_mobjects(indicator, indicator_reading)
        self.unzoomable_mobs.add(indicator_reading)

        def indicator_wiggle():
            INDICATOR_WIGGLE_FACTOR = 1.3

            self.play(
                ScaleInPlace(indicator, INDICATOR_WIGGLE_FACTOR, rate_func = wiggle),
                ScaleInPlace(indicator_reading, INDICATOR_WIGGLE_FACTOR, rate_func = wiggle)
            )

        def angle_for_index(i,step):
            return -TAU/4 + TAU/2**step * (i + 0.5)


        def position_for_index(i, step, scaled_down = False):

            theta = angle_for_index(i,step)
            radial_vector = np.array([np.cos(theta),np.sin(theta),0])
            position = self.lake_center + self.lake_radius * radial_vector

            if scaled_down:
                return position.scale_about_point(self.obs_dot.get_center(),0.5)
            else:
                return position


        def split_light_source(i, step, show_steps = True, animate = True, run_time = 1):

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

            leg1 = Line(self.obs_dot.get_center(),ls_new_loc1)
            leg2 = Line(self.obs_dot.get_center(),ls_new_loc2)
            self.new_legs_1.append(leg1)
            self.new_legs_2.append(leg2)

            if show_steps == True:
                self.play(
                    ShowCreation(leg1, run_time = run_time),
                    ShowCreation(leg2, run_time = run_time),
                )

            ls1 = self.light_sources_array[i]


            ls2 = ls1.copy()
            if animate == True:
                self.add(ls2)

            self.additional_light_sources.append(ls2)

            # check if the light sources are on screen
            ls_old_loc = np.array(ls1.get_source_point())
            onscreen_old = np.any(np.abs(ls_old_loc) < 10)
            onscreen_1 = np.any(np.abs(ls_new_loc1) < 10)
            onscreen_2 = np.any(np.abs(ls_new_loc2) < 10)
            show_animation = (onscreen_old or onscreen_1 or onscreen_2)

            if show_animation or animate:
                ls1.generate_target()
                ls2.generate_target()
                ls1.target.move_source_to(ls_new_loc1)
                ls2.target.move_source_to(ls_new_loc2)
                ls1.fade(1)
                self.play(
                    MoveToTarget(ls1), MoveToTarget(ls2),
                    run_time = run_time
                )
            else:
                ls1.move_source_to(ls_new_loc1)
                ls2.move_source_to(ls_new_loc1)


        def construction_step(n, show_steps = True, run_time = 1,
            simultaneous_splitting = False):

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
                self.zoomable_mobs.remove(self.hypotenuses, self.altitudes, self.inner_lake)
                self.play(
                    FadeOut(self.hypotenuses),
                    FadeOut(self.altitudes),
                    FadeOut(self.inner_lake)
                )
            else:
                self.zoomable_mobs.remove(self.inner_lake)
                self.play(
                    FadeOut(self.inner_lake)
                )

            # create a new, outer lake
            self.lake_center = self.obs_dot.get_center() + self.lake_radius * UP

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
                    FadeIn(self.ls0_dot)
                )
            else:
                self.play(
                    FadeIn(new_outer_lake, run_time = run_time),
                )

            self.wait()

            self.inner_lake = self.outer_lake
            self.outer_lake = new_outer_lake
            self.altitudes = self.legs
            #self.lake_center = self.outer_lake.get_center()

            self.additional_light_sources = []
            self.new_legs_1 = []
            self.new_legs_2 = []
            self.new_hypotenuses = []

            if simultaneous_splitting == False:

                for i in range(2**n):
                    
                    split_light_source(i,
                        step = n,
                        show_steps = show_steps,
                        run_time = run_time
                    )

                    if n == 1 and i == 0:
                        # show again where the right angles are
                        A = self.light_sources[0].get_center()
                        B = self.additional_light_sources[0].get_center()
                        C = self.obs_dot.get_center()

                        triangle1 = triangle(
                            A, C, B
                        )
                        right_angle1 = right_angle(
                            A, C, B, size = 2 * RIGHT_ANGLE_SIZE
                        )

                        self.play(
                            FadeIn(triangle1),
                            FadeIn(right_angle1)
                        )

                        self.wait()

                        self.play(
                            FadeOut(triangle1),
                            FadeOut(right_angle1)
                        )

                        self.wait()

                        H = self.inner_lake.get_center() + self.lake_radius/2 * RIGHT
                        L = self.outer_lake.get_center()
                        triangle2 = triangle(
                            L, H, C
                        )

                        right_angle2 = right_angle(
                            L, H, C, size = 2 * RIGHT_ANGLE_SIZE
                        )

                        self.play(
                            FadeIn(triangle2),
                            FadeIn(right_angle2)
                        )

                        self.wait()

                        self.play(
                            FadeOut(triangle2),
                            FadeOut(right_angle2)
                        )

                        self.wait()

            else: # simultaneous splitting

                old_lake = self.outer_lake.copy()
                old_ls = self.light_sources.copy()
                old_ls2 = old_ls.copy()
                for submob in old_ls2.submobjects:
                    old_ls.add(submob)

                self.remove(self.outer_lake, self.light_sources)
                self.add(old_lake, old_ls)

                for i in range(2**n):
                    split_light_source(i,
                        step = n,
                        show_steps = show_steps,
                        run_time = run_time,
                        animate = False
                    )

                self.play(
                    ReplacementTransform(old_ls, self.light_sources, run_time = run_time),
                    ReplacementTransform(old_lake, self.outer_lake, run_time = run_time),
                )




            # collect the newly created mobs (in arrays)
            # into the appropriate Mobject containers

            self.legs = VMobject()
            for leg in self.new_legs_1:
                self.legs.add(leg)
                self.zoomable_mobs.add(leg)
            for leg in self.new_legs_2:
                self.legs.add(leg)
                self.zoomable_mobs.add(leg)

            for hyp in self.hypotenuses.submobjects:
                self.zoomable_mobs.remove(hyp)

            self.hypotenuses = VMobject()
            for hyp in self.new_hypotenuses:
                self.hypotenuses.add(hyp)
                self.zoomable_mobs.add(hyp)

            for ls in self.additional_light_sources:
                self.light_sources.add(ls)
                self.light_sources_array.append(ls)
                self.zoomable_mobs.add(ls)

            # update scene
            self.add(
                self.light_sources,
                self.inner_lake,
                self.outer_lake,
            )
            self.zoomable_mobs.add(self.light_sources, self.inner_lake, self.outer_lake)

            if show_steps == True:
                self.add(
                    self.legs,
                    self.hypotenuses,
                    self.altitudes,
                )
                self.zoomable_mobs.add(self.legs, self.hypotenuses, self.altitudes)


            self.wait()

            if show_steps == True:
                self.play(FadeOut(self.ls0_dot))

            #self.lake_center = ls0_loc = self.obs_dot.get_center() + self.lake_radius * UP
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

        self.zoomable_mobs.add(self.inner_lake, self.outer_lake, self.altitudes, self.light_sources)

        self.add(
            self.inner_lake,
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

        construction_step(0)

        my_triangle = triangle(
            self.light_sources[0].get_source_point(),
            OBSERVER_POINT,
            self.light_sources[1].get_source_point()
        )

        angle_sign1 = right_angle(
            self.light_sources[0].get_source_point(),
            OBSERVER_POINT,
            self.light_sources[1].get_source_point(),
            size = RIGHT_ANGLE_SIZE
        )

        self.play(
            FadeIn(angle_sign1),
            FadeIn(my_triangle)
        )

        angle_sign2 = right_angle(
            self.light_sources[1].get_source_point(),
            self.lake_center,
            OBSERVER_POINT,
            size = RIGHT_ANGLE_SIZE
        )

        self.play(
            FadeIn(angle_sign2)
        )

        self.wait()

        self.play(
            FadeOut(angle_sign1),
            FadeOut(angle_sign2),
            FadeOut(my_triangle)
        )

        indicator_wiggle()
        self.remove(self.ls0_dot)
        zoom_out_scene(2)

        
        construction_step(1)
        indicator_wiggle()
        #self.play(FadeOut(self.ls0_dot))
        zoom_out_scene(2)


        construction_step(2)
        indicator_wiggle()
        self.play(FadeOut(self.ls0_dot))




        self.play(
            FadeOut(self.altitudes),
            FadeOut(self.hypotenuses),
            FadeOut(self.legs)
        )

        max_it = 6
        scale = 2**(max_it - 4)
        TEX_SCALE *= scale



        # for i in range(3,max_it + 1):
        #     construction_step(i, show_steps = False, run_time = 4.0/2**i,
        #         simultaneous_splitting = True)



        # simultaneous expansion of light sources from now on
        self.play(FadeOut(self.inner_lake))

        for n in range(3,max_it + 1):

            new_lake = self.outer_lake.copy().scale(2,about_point = self.obs_dot.get_center())
            for ls in self.light_sources_array:
                lsp = ls.copy()
                self.light_sources.add(lsp)
                self.add(lsp)
                self.light_sources_array.append(lsp)

            new_lake_center = new_lake.get_center()
            new_lake_radius = 0.5 * new_lake.get_width()

            shift_list = (Transform(self.outer_lake,new_lake),)


            for i in range(2**n):
                theta = -TAU/4 + (i + 0.5) * TAU / 2**n
                v = np.array([np.cos(theta), np.sin(theta),0])
                pos1 = new_lake_center + new_lake_radius * v
                pos2 = new_lake_center - new_lake_radius * v
                shift_list += (self.light_sources.submobjects[i].move_source_to,pos1)
                shift_list += (self.light_sources.submobjects[i+2**n].move_source_to,pos2)

            self.play(*shift_list)

        #self.revert_to_original_skipping_status()

        # Now create a straight number line and transform into it
        MAX_N = 17

        origin_point = self.obs_dot.get_center()

        self.number_line = NumberLine(
            x_min = -MAX_N,
            x_max = MAX_N + 1,
            color = WHITE,
            number_at_center = 0,
            stroke_width = LAKE_STROKE_WIDTH,
            stroke_color = LAKE_STROKE_COLOR,
            #numbers_with_elongated_ticks = range(-MAX_N,MAX_N + 1),
            numbers_to_show = list(range(-MAX_N,MAX_N + 1,2)),
            unit_size = LAKE0_RADIUS * TAU/4 / 2 * scale,
            tick_frequency = 1,
            line_to_number_buff = LARGE_BUFF,
            label_direction = UP,
        ).shift(scale * 2.5 * DOWN)

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
            width = 20 * scale,
            height = 10 * scale,
            stroke_width = LAKE_STROKE_WIDTH,
            stroke_color = LAKE_STROKE_COLOR,
            fill_color = LAKE_COLOR,
            fill_opacity = LAKE_OPACITY,
        ).flip().next_to(origin_point,UP,buff = 0)

        self.play(
            ReplacementTransform(pond_sources,nl_sources),
            ReplacementTransform(self.outer_lake,open_sea),
            FadeOut(self.inner_lake)
        )
        self.play(FadeIn(self.number_line))

        self.wait()

        v = 4 * scale * UP
        self.play(
            nl_sources.shift,v,
            morty.shift,v,
            self.number_line.shift,v,
            indicator.shift,v,
            indicator_reading.shift,v,
            open_sea.shift,v,
            self.obs_dot.shift,v,
        )
        self.number_line_labels.shift(v)

        origin_point = self.number_line.number_to_point(0)
        #self.remove(self.obs_dot)
        self.play(
            indicator.move_to, origin_point + scale * UP,
            indicator_reading.move_to, origin_point + scale * UP,
            FadeOut(open_sea),
            FadeOut(morty),
            FadeIn(self.number_line_labels)
        )

        two_sided_sum = TexMobject("\dots", "+", "{1\over (-11)^2}",\
         "+", "{1\over (-9)^2}", " + ", "{1\over (-7)^2}", " + ", "{1\over (-5)^2}", " + ", \
         "{1\over (-3)^2}", " + ", "{1\over (-1)^2}", " + ", "{1\over 1^2}", " + ", \
         "{1\over 3^2}", " + ", "{1\over 5^2}", " + ", "{1\over 7^2}", " + ", \
         "{1\over 9^2}", " + ", "{1\over 11^2}", " + ", "\dots")

        nb_symbols = len(two_sided_sum.submobjects)

        two_sided_sum.scale(TEX_SCALE)
        
        for (i,submob) in zip(list(range(nb_symbols)),two_sided_sum.submobjects):
            submob.next_to(self.number_line.number_to_point(i - 13),DOWN, buff = 2*scale)
            if (i == 0 or i % 2 == 1 or i == nb_symbols - 1): # non-fractions
                submob.shift(0.3 * scale * DOWN)

        self.play(Write(two_sided_sum))

        for i in range(MAX_N - 5, MAX_N):
            self.remove(nl_sources.submobjects[i].ambient_light)
        
        for i in range(MAX_N, MAX_N + 5):
            self.add_foreground_mobject(nl_sources.submobjects[i].ambient_light)

        self.wait()        

        covering_rectangle = Rectangle(
            width = FRAME_X_RADIUS * scale,
            height = 2 * FRAME_Y_RADIUS * scale,
            stroke_width = 0,
            fill_color = BLACK,
            fill_opacity = 1,
        )
        covering_rectangle.next_to(ORIGIN,LEFT,buff = 0)
        for i in range(10):
            self.add_foreground_mobject(nl_sources.submobjects[i])

        self.add_foreground_mobject(indicator)
        self.add_foreground_mobject(indicator_reading)


        half_indicator_reading = TexMobject("{\pi^2 \over 8}").scale(TEX_SCALE)
        half_indicator_reading.move_to(indicator)

        central_plus_sign = two_sided_sum[13]

        self.play(
            FadeIn(covering_rectangle),
            Transform(indicator_reading, half_indicator_reading),
            FadeOut(central_plus_sign)
        )

        equals_sign = TexMobject("=").scale(TEX_SCALE)
        equals_sign.move_to(central_plus_sign)
        p = 2 * scale * LEFT + central_plus_sign.get_center()[1] * UP

        self.play(
            indicator.move_to,p,
            indicator_reading.move_to,p,
            FadeIn(equals_sign),
        )

        self.revert_to_original_skipping_status()

        # show Randy admiring the result
        randy = Randolph(color = MAROON_E).scale(scale).move_to(2*scale*DOWN+5*scale*LEFT)
        self.play(FadeIn(randy))
        self.play(randy.change,"happy")
        self.play(randy.change,"hooray")

class CircumferenceText(Scene):
    CONFIG = {"n" : 16}
    def construct(self):
        words = TextMobject("Circumference %d"%self.n)
        words.scale(1.25)
        words.to_corner(UP+LEFT)
        self.add(words)

class CenterOfLargerCircleOverlayText(Scene):
    def construct(self):
        words = TextMobject("Center of \\\\ larger circle")
        arrow = Vector(DOWN+LEFT, color = WHITE)
        arrow.shift(words.get_bottom() + SMALL_BUFF*DOWN - arrow.get_start())
        group = VGroup(words, arrow)
        group.set_height(FRAME_HEIGHT - 1)
        group.to_edge(UP)
        self.add(group)

class DiameterWordOverlay(Scene):
    def construct(self):
        word = TextMobject("Diameter")
        word.set_width(FRAME_X_RADIUS)
        word.rotate(-45*DEGREES)
        self.play(Write(word))
        self.wait()

class YayIPTApplies(TeacherStudentsScene):
    def construct(self):
        self.teacher_says(
            "Heyo!  The Inverse \\\\ Pythagorean Theorem \\\\ applies!",
            bubble_kwargs = {"width" : 5},
            target_mode = "surprised"
        )
        self.change_student_modes(*3*["hooray"])
        self.wait(2)

class WalkThroughOneMoreStep(TeacherStudentsScene):
    def construct(self):
        self.student_says("""
            Wait...can you walk \\\\
            through one more step?
        """)
        self.play(self.teacher.change, "happy")
        self.wait(4)

class ThinkBackToHowAmazingThisIs(ThreeDScene):
    CONFIG = {
        "x_radius" : 100,
        "max_shown_n" : 20,
    }
    def construct(self):
        self.show_sum()
        self.show_giant_circle()

    def show_sum(self):
        number_line = NumberLine(
            x_min = -self.x_radius, 
            x_max = self.x_radius,
            numbers_to_show = list(range(-self.max_shown_n, self.max_shown_n)),
        )
        number_line.add_numbers()
        number_line.shift(2*DOWN)

        positive_dots, negative_dots = [
            VGroup(*[
                Dot(number_line.number_to_point(u*x))
                for x in range(1, int(self.x_radius), 2)
            ])
            for u in (1, -1)
        ]
        dot_pairs = it.starmap(VGroup, list(zip(positive_dots, negative_dots)))

        # Decimal
        decimal = DecimalNumber(0, num_decimal_places = 6)
        decimal.to_edge(UP)
        terms = [2./(n**2) for n in range(1, 100, 2)]
        partial_sums = np.cumsum(terms)

        # pi^2/4 label
        brace = Brace(decimal, DOWN)
        pi_term = TexMobject("\pi^2 \over 4")
        pi_term.next_to(brace, DOWN)

        term_mobjects = VGroup()
        for n in range(1, self.max_shown_n, 2):
            p_term = TexMobject("\\left(\\frac{1}{%d}\\right)^2"%n)
            n_term = TexMobject("\\left(\\frac{-1}{%d}\\right)^2"%n)
            group = VGroup(p_term, n_term)
            group.scale(0.7)
            p_term.next_to(number_line.number_to_point(n), UP, LARGE_BUFF)
            n_term.next_to(number_line.number_to_point(-n), UP, LARGE_BUFF)
            term_mobjects.add(group)
        term_mobjects.set_color_by_gradient(BLUE, YELLOW)
        plusses = VGroup(*[
            VGroup(*[
                TexMobject("+").next_to(
                    number_line.number_to_point(u*n), UP, buff = 1.25,
                )
                for u in (-1, 1)
            ])
            for n in range(0, self.max_shown_n, 2)
        ])

        zoom_out = always_shift(
            self.camera.rotation_mobject,
            direction = OUT, rate = 0.4
        )
        def update_decimal(decimal):
            z = self.camera.rotation_mobject.get_center()[2]
            decimal.set_height(0.07*z)
            decimal.move_to(0.7*z*UP)
        scale_decimal = Mobject.add_updater(decimal, update_decimal)


        self.add(number_line, *dot_pairs)
        self.add(zoom_out, scale_decimal)

        tuples = list(zip(term_mobjects, plusses, partial_sums))
        run_time = 1
        for term_mobs, plus_pair, partial_sum in tuples:
            self.play(
                FadeIn(term_mobs),
                Write(plus_pair, run_time = 1),
                ChangeDecimalToValue(decimal, partial_sum),
                run_time = run_time
            )
            self.wait(run_time)
            run_time *= 0.9
        self.play(ChangeDecimalToValue(decimal, np.pi**2/4, run_time = 5))
        zoom_out.begin_wind_down()
        self.wait()
        self.remove(zoom_out, scale_decimal)
        self.play(*list(map(FadeOut, it.chain(
            term_mobjects, plusses, 
            number_line.numbers, [decimal]
        ))))

        self.number_line = number_line

    def show_giant_circle(self):
        self.number_line.insert_n_curves(10000)
        everything = VGroup(*self.mobjects)
        circle = everything.copy()
        circle.move_to(ORIGIN)
        circle.apply_function(
            lambda x_y_z : complex_to_R3(7*np.exp(complex(0, 0.0315*x_y_z[0])))
        )
        circle.rotate(-TAU/4, about_point = ORIGIN)
        circle.center()

        self.play(Transform(everything, circle, run_time = 6))

class ButWait(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "But wait!",
            target_mode = "angry",
            run_time = 1,
        )
        self.change_student_modes(
            "sassy", "angry", "sassy",
            added_anims = [self.teacher.change, "guilty"],
            run_time = 1
        )
        self.student_says(
            """
            You promised us \\\\
            $1+{1 \\over 4} + {1 \\over 9} + {1 \\over 16} + \\cdots$
            """,
            target_mode = "sassy",
        )
        self.wait(3)
        self.teacher_says("Yes, but that's \\\\ very close.")
        self.change_student_modes(*["plain"]*3)
        self.wait(2)

class FinalSumManipulationScene(PiCreatureScene):

    def construct(self):

        LAKE_COLOR = BLUE
        LAKE_OPACITY = 0.15
        LAKE_STROKE_WIDTH = 5.0
        LAKE_STROKE_COLOR = BLUE
        TEX_SCALE = 0.8

        LIGHT_COLOR2 = RED
        LIGHT_COLOR3 = BLUE

        unit_length = 1.5
        vertical_spacing = 2.5 * DOWN
        switch_on_time = 0.2

        sum_vertical_spacing = 1.5

        randy = self.get_primary_pi_creature()
        randy.set_color(MAROON_D)
        randy.color = MAROON_D
        randy.scale(0.7).flip().to_edge(DOWN + LEFT)
        self.wait()

        ls_template = LightSource(
            radius = 1,
            num_levels = 10,
            max_opacity_ambient = 0.5,
            opacity_function = inverse_quadratic(1,0.75,1)
        )


        odd_range = np.arange(1,9,2)
        even_range = np.arange(2,16,2)
        full_range = np.arange(1,8,1)

        self.number_line1 = NumberLine(
            x_min = 0,
            x_max = 11,
            color = LAKE_STROKE_COLOR,
            number_at_center = 0,
            stroke_width = LAKE_STROKE_WIDTH,
            stroke_color = LAKE_STROKE_COLOR,
            #numbers_to_show = full_range,
            number_scale_val = 0.5,
            numbers_with_elongated_ticks = [],
            unit_size = unit_length,
            tick_frequency = 1,
            line_to_number_buff = MED_SMALL_BUFF,
            include_tip = True,
            label_direction = UP,
        )

        self.number_line1.next_to(2.5 * UP + 3 * LEFT, RIGHT, buff = 0.3)
        self.number_line1.add_numbers()

        odd_lights = VMobject()
        for i in odd_range:
            pos = self.number_line1.number_to_point(i)
            ls = ls_template.copy()
            ls.move_source_to(pos)
            odd_lights.add(ls)

        self.play(
            ShowCreation(self.number_line1, run_time = 5),
        )
        self.wait()


        odd_terms = VMobject()
        for i in odd_range:
            if i == 1:
                term = TexMobject("\phantom{+\,\,\,}{1\over " + str(i) + "^2}",
                    fill_color = LIGHT_COLOR, stroke_color = LIGHT_COLOR)
            else:
                term = TexMobject("+\,\,\, {1\over " + str(i) + "^2}",
                    fill_color = LIGHT_COLOR, stroke_color = LIGHT_COLOR)

            term.next_to(self.number_line1.number_to_point(i), DOWN, buff = 1.5)
            odd_terms.add(term)


        for (ls, term) in zip(odd_lights.submobjects, odd_terms.submobjects):
            self.play(
                FadeIn(ls.lighthouse, run_time = switch_on_time),
                SwitchOn(ls.ambient_light, run_time = switch_on_time),
                Write(term, run_time = switch_on_time)
            )

        result1 = TexMobject("{\pi^2\over 8} =", fill_color = LIGHT_COLOR,
            stroke_color = LIGHT_COLOR)
        result1.next_to(self.number_line1, LEFT, buff = 0.5)
        result1.shift(0.87 * vertical_spacing)
        self.play(Write(result1))




        self.number_line2 = self.number_line1.copy()
        self.number_line2.numbers_to_show = full_range
        self.number_line2.shift(2 * vertical_spacing)
        self.number_line2.add_numbers()

        full_lights = VMobject()

        for i in full_range:
            pos = self.number_line2.number_to_point(i)
            ls = ls_template.copy()
            ls.color = LIGHT_COLOR3
            ls.move_source_to(pos)
            full_lights.add(ls)

        self.play(
            ShowCreation(self.number_line2, run_time = 5),
        )
        self.wait()


        full_lighthouses = VMobject()
        full_ambient_lights = VMobject()
        for ls in full_lights:
            full_lighthouses.add(ls.lighthouse)
            full_ambient_lights.add(ls.ambient_light)

        self.play(
            LaggedStartMap(FadeIn, full_lighthouses, lag_ratio = 0.2, run_time = 3),
        )

        self.play(
            LaggedStartMap(SwitchOn, full_ambient_lights, lag_ratio = 0.2, run_time = 3)
        )

        # for ls in full_lights.submobjects:
        #     self.play(
        #         FadeIn(ls.lighthouse, run_time = 0.1),#5 * switch_on_time),
        #         SwitchOn(ls.ambient_light, run_time = 0.1)#5 * switch_on_time),
        #     )



        even_terms = VMobject()
        for i in even_range:
            term = TexMobject("+\,\,\, {1\over " + str(i) + "^2}", fill_color = LIGHT_COLOR2, stroke_color = LIGHT_COLOR)
            term.next_to(self.number_line1.number_to_point(i), DOWN, buff = sum_vertical_spacing)
            even_terms.add(term)


        even_lights = VMobject()

        for i in even_range:
            pos = self.number_line1.number_to_point(i)
            ls = ls_template.copy()
            ls.color = LIGHT_COLOR2
            ls.move_source_to(pos)
            even_lights.add(ls)

        for (ls, term) in zip(even_lights.submobjects, even_terms.submobjects):
            self.play(
                SwitchOn(ls.ambient_light, run_time = switch_on_time),
                Write(term)
            )
        self.wait()



        # now morph the even lights into the full lights
        full_lights_copy = full_lights.copy()
        even_lights_copy = even_lights.copy()


        self.play(
            Transform(even_lights,full_lights, run_time = 2)
        )


        self.wait()

        for i in range(6):
            self.play(
                Transform(even_lights[i], even_lights_copy[i])
            )
            self.wait()

        # draw arrows
        P1 = self.number_line2.number_to_point(1)
        P2 = even_terms.submobjects[0].get_center()
        Q1 = interpolate(P1, P2, 0.2)
        Q2 = interpolate(P1, P2, 0.8)
        quarter_arrow = Arrow(Q1, Q2,
            color = LIGHT_COLOR2)
        quarter_label = TexMobject("\\times {1\over 4}", fill_color = LIGHT_COLOR2, stroke_color = LIGHT_COLOR2)
        quarter_label.scale(0.7)
        quarter_label.next_to(quarter_arrow.get_center(), RIGHT)

        self.play(
            ShowCreation(quarter_arrow),
            Write(quarter_label),
        )
        self.wait()

        P3 = odd_terms.submobjects[0].get_center()
        R1 = interpolate(P1, P3, 0.2)
        R2 = interpolate(P1, P3, 0.8)
        three_quarters_arrow = Arrow(R1, R2,
            color = LIGHT_COLOR)
        three_quarters_label = TexMobject("\\times {3\over 4}", fill_color = LIGHT_COLOR, stroke_color = LIGHT_COLOR)
        three_quarters_label.scale(0.7)
        three_quarters_label.next_to(three_quarters_arrow.get_center(), LEFT)

        self.play(
            ShowCreation(three_quarters_arrow),
            Write(three_quarters_label)
        )
        self.wait()

        four_thirds_arrow = Arrow(R2, R1, color = LIGHT_COLOR)
        four_thirds_label = TexMobject("\\times {4\over 3}", fill_color = LIGHT_COLOR, stroke_color = LIGHT_COLOR)
        four_thirds_label.scale(0.7)
        four_thirds_label.next_to(four_thirds_arrow.get_center(), LEFT)


        self.play(
            FadeOut(quarter_label),
            FadeOut(quarter_arrow),
            FadeOut(even_lights),
            FadeOut(even_terms)

        )
        self.wait()

        self.play(
            ReplacementTransform(three_quarters_arrow, four_thirds_arrow),
            ReplacementTransform(three_quarters_label, four_thirds_label)
        )
        self.wait()

        full_terms = VMobject()
        for i in range(1,8): #full_range:
            if i == 1:
                term = TexMobject("\phantom{+\,\,\,}{1\over " + str(i) + "^2}", fill_color = LIGHT_COLOR3, stroke_color = LIGHT_COLOR3)
            elif i == 7:
                term = TexMobject("+\,\,\,\dots", fill_color = LIGHT_COLOR3, stroke_color = LIGHT_COLOR3)
            else:
                term = TexMobject("+\,\,\, {1\over " + str(i) + "^2}", fill_color = LIGHT_COLOR3, stroke_color = LIGHT_COLOR3)

            term.move_to(self.number_line2.number_to_point(i))
            full_terms.add(term)

        #return

        self.play(
            FadeOut(self.number_line1),
            FadeOut(odd_lights),
            FadeOut(self.number_line2),
            FadeOut(full_lights),
            FadeIn(full_terms)
        )
        self.wait()

        v = (sum_vertical_spacing + 0.5) * UP
        self.play(
            odd_terms.shift, v,
            result1.shift, v,
            four_thirds_arrow.shift, v,
            four_thirds_label.shift, v,
            odd_terms.shift, v,
            full_terms.shift, v
        )

        arrow_copy = four_thirds_arrow.copy()
        label_copy = four_thirds_label.copy()
        arrow_copy.shift(2.5 * LEFT)
        label_copy.shift(2.5 * LEFT)

        self.play(
            FadeIn(arrow_copy),
            FadeIn(label_copy)
        )
        self.wait()

        final_result = TexMobject("{\pi^2 \over 6}=", fill_color = LIGHT_COLOR3, stroke_color = LIGHT_COLOR3)
        final_result.next_to(arrow_copy, DOWN)

        self.play(
            Write(final_result),
            randy.change_mode,"hooray"
        )
        self.wait()

        equation = VMobject()
        equation.add(final_result)
        equation.add(full_terms)


        self.play(
            FadeOut(result1),
            FadeOut(odd_terms),
            FadeOut(arrow_copy),
            FadeOut(label_copy),
            FadeOut(four_thirds_arrow),
            FadeOut(four_thirds_label),
            full_terms.shift,LEFT,
        )
        self.wait()

        self.play(equation.shift, -equation.get_center()[1] * UP + UP + 1.5 * LEFT)

        result_box = Rectangle(width = 1.1 * equation.get_width(),
            height = 2 * equation.get_height(), color = LIGHT_COLOR3)
        result_box.move_to(equation)


        self.play(
            ShowCreation(result_box)
        )
        self.wait()

class LabeledArc(Arc):
    CONFIG = {
        "length" : 1
    }

    def __init__(self, angle, **kwargs):

        BUFFER = 0.8

        Arc.__init__(self,angle,**kwargs)

        label = DecimalNumber(self.length, num_decimal_places = 0)
        r = BUFFER * self.radius
        theta = self.start_angle + self.angle/2
        label_pos = r * np.array([np.cos(theta), np.sin(theta), 0])

        label.move_to(label_pos)
        self.add(label)

class ArcHighlightOverlaySceneCircumferenceEight(Scene):
    CONFIG = {
        "n" : 2,
    }
    def construct(self):
        BASELINE_YPOS = -2.5
        OBSERVER_POINT = [0,BASELINE_YPOS,0]
        LAKE0_RADIUS = 2.5
        INDICATOR_RADIUS = 0.6
        TICK_SIZE = 0.5
        LIGHTHOUSE_HEIGHT = 0.2
        LAKE_COLOR = BLUE
        LAKE_OPACITY = 0.15
        LAKE_STROKE_WIDTH = 5.0
        LAKE_STROKE_COLOR = BLUE
        TEX_SCALE = 0.8
        DOT_COLOR = BLUE

        FLASH_TIME = 1

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

        flash_arcs(self.n)

class ArcHighlightOverlaySceneCircumferenceSixteen(ArcHighlightOverlaySceneCircumferenceEight):
    CONFIG = {
        "n" : 3,
    }

class InfiniteCircleScene(PiCreatureScene):

    def construct(self):

        morty = self.get_primary_pi_creature()
        morty.set_color(MAROON_D).flip()
        morty.color = MAROON_D
        morty.scale(0.5).move_to(ORIGIN)

        arrow = Arrow(ORIGIN, 2.4 * RIGHT)
        dot = Dot(color = BLUE).next_to(arrow)
        ellipsis = TexMobject("\dots")

        infsum = VGroup()
        infsum.add(ellipsis.copy())

        for i in range(3):
            infsum.add(arrow.copy().next_to(infsum.submobjects[-1]))
            infsum.add(dot.copy().next_to(infsum.submobjects[-1]))

        infsum.add(arrow.copy().next_to(infsum.submobjects[-1]))
        infsum.add(ellipsis.copy().next_to(infsum.submobjects[-1]))

        infsum.next_to(morty,DOWN, buff = 1)

        self.wait()
        self.play(
            LaggedStartMap(FadeIn,infsum,lag_ratio = 0.2)
        )
        self.wait()

        A = infsum.submobjects[-1].get_center() + 0.5 * RIGHT
        B = A + RIGHT + 1.3 * UP + 0.025 * LEFT
        right_arc = DashedLine(TAU/4*UP, ORIGIN, stroke_color = YELLOW,
            stroke_width = 8).apply_complex_function(np.exp)
        right_arc.rotate(-TAU/4).next_to(infsum, RIGHT).shift(0.5 * UP)
        right_tip_line = Arrow(B - UP, B, color = WHITE)
        right_tip_line.add_tip()
        right_tip = right_tip_line.get_tip()
        right_tip.set_fill(color = YELLOW)
        right_arc.add(right_tip)
        

        C = B + 3.2 * UP
        right_line = DashedLine(B + 0.2 * DOWN,C + 0.2 * UP, stroke_color = YELLOW,
            stroke_width = 8)

        ru_arc = right_arc.copy().rotate(angle = TAU/4)
        ru_arc.remove(ru_arc.submobjects[-1])
        ru_arc.to_edge(UP+RIGHT, buff = 0.15)

        D = np.array([5.85, 3.85,0])
        E = np.array([-D[0],D[1],0])
        up_line = DashedLine(D, E, stroke_color = YELLOW,
            stroke_width = 8)

        lu_arc = ru_arc.copy().flip().to_edge(LEFT + UP, buff = 0.15)
        left_line = right_line.copy().flip(axis = RIGHT).to_edge(LEFT, buff = 0.15)

        left_arc = right_arc.copy().rotate(-TAU/4)
        left_arc.next_to(infsum, LEFT).shift(0.5 * UP + 0.1 * LEFT)

        right_arc.shift(0.2 * RIGHT)
        right_line.shift(0.2 * RIGHT)

        self.play(FadeIn(right_arc))
        self.play(ShowCreation(right_line))
        self.play(FadeIn(ru_arc))
        self.play(ShowCreation(up_line))
        self.play(FadeIn(lu_arc))
        self.play(ShowCreation(left_line))
        self.play(FadeIn(left_arc))



        self.wait()

class Credits(Scene):
    def construct(self):
        credits = VGroup(*[
            VGroup(*list(map(TextMobject, pair)))
            for pair in [
                ("Primary writer and animator:", "Ben Hambrecht"),
                ("Editing, advising, narrating:", "Grant Sanderson"),
                ("Based on a paper originally by:", "Johan Wästlund"),
            ]
        ])
        for credit, color in zip(credits, [MAROON_D, BLUE_D, WHITE]):
            credit[1].set_color(color)
            credit.arrange(DOWN, buff = SMALL_BUFF)

        credits.arrange(DOWN, buff = LARGE_BUFF)

        credits.center()
        patreon_logo = PatreonLogo()
        patreon_logo.to_edge(UP)

        for credit in credits:
            self.play(LaggedStartMap(FadeIn, credit[0]))
            self.play(FadeIn(credit[1]))
        self.wait()
        self.play(
            credits.next_to, patreon_logo.get_bottom(), DOWN, MED_LARGE_BUFF,
            DrawBorderThenFill(patreon_logo)
        )
        self.wait()

class Promotion(PiCreatureScene):
    CONFIG = {
        "seconds_to_blink" : 5,
    }
    def construct(self):
        url = TextMobject("https://brilliant.org/3b1b/")
        url.to_corner(UP+LEFT)

        rect = Rectangle(height = 9, width = 16)
        rect.set_height(5.5)
        rect.next_to(url, DOWN)
        rect.to_edge(LEFT)

        self.play(
            Write(url),
            self.pi_creature.change, "raise_right_hand"
        )
        self.play(ShowCreation(rect))
        self.wait(2)
        self.change_mode("thinking")
        self.wait()
        self.look_at(url)
        self.wait(10)
        self.change_mode("happy")
        self.wait(10)
        self.change_mode("raise_right_hand")
        self.wait(10)

        self.remove(rect)
        self.play(
            url.next_to, self.pi_creature, UP+LEFT
        )
        url_rect = SurroundingRectangle(url)
        self.play(ShowCreation(url_rect))
        self.play(FadeOut(url_rect))
        self.wait(3)

class BaselPatreonThanks(PatreonEndScreen):
    CONFIG = {
        "specific_patrons" : [
            "CrypticSwarm ",
            "Ali Yahya",
            "Juan Benet",
            "Markus Persson",
            "Damion Kistler",
            "Burt Humburg",
            "Yu Jun",
            "Dave Nicponski",
            "Kaustuv DeBiswas",
            "Joseph John Cox",
            "Luc Ritchie",
            "Achille Brighton",
            "Rish Kundalia",
            "Yana Chernobilsky",
            "Shìmín Ku$\\overline{\\text{a}}$ng",
            "Mathew Bramson",
            "Jerry Ling",
            "Mustafa Mahdi",
            "Meshal Alshammari",
            "Mayank M. Mehrotra",
            "Lukas Biewald",
            "Robert Teed",
            "Samantha D. Suplee",
            "Mark Govea",
            "John Haley",
            "Julian Pulgarin",
            "Jeff Linse",
            "Cooper Jones",
            "Desmos  ",
            "Boris Veselinovich",
            "Ryan Dahl",
            "Ripta Pasay",
            "Eric Lavault",
            "Randall Hunt",
            "Andrew Busey",
            "Mads Elvheim",
            "Tianyu Ge",
            "Awoo",
            "Dr. David G. Stork",
            "Linh Tran",
            "Jason Hise",
            "Bernd Sing",
            "James H. Park",
            "Ankalagon   ",
            "Devin Scott",
            "Mathias Jansson",
            "David Clark",
            "Ted Suzman",
            "Eric Chow",
            "Michael Gardner",
            "David Kedmey",
            "Jonathan Eppele",
            "Clark Gaebel",
            "Jordan Scales",
            "Ryan Atallah",
            "supershabam ",
            "1stViewMaths ",
            "Jacob Magnuson",
            "Chloe Zhou",
            "Ross Garber",
            "Thomas Tarler",
            "Isak Hietala",
            "Egor Gumenuk",
            "Waleed Hamied",
            "Oliver Steele",
            "Yaw Etse",
            "David B",
            "Delton Ding",
            "James Thornton",
            "Felix Tripier",
            "Arthur Zey",
            "George Chiesa",
            "Norton Wang",
            "Kevin Le",
            "Alexander Feldman",
            "David MacCumber",
            "Jacob Kohl",
            "Sergei  ",
            "Frank Secilia",
            "Patrick Mézard",
            "George John",
            "Akash Kumar",
            "Britt Selvitelle",
            "Jonathan Wilson",
            "Ignacio Freiberg",
            "Zhilong Yang",
            "Karl Niu",
            "Dan Esposito",
            "Michael Kunze",
            "Giovanni Filippi",
            "Eric Younge",
            "Prasant Jagannath",
            "Andrejs Olins",
            "Cody Brocious",
        ],
    }
    def construct(self):
        next_video = TextMobject("$\\uparrow$  Next video $\\uparrow$")
        next_video.to_edge(RIGHT, buff = 1.5)
        next_video.shift(MED_SMALL_BUFF*UP)
        next_video.set_color(YELLOW)
        self.add_foreground_mobject(next_video)
        PatreonEndScreen.construct(self)

class Thumbnail(Scene):
    CONFIG = {
        "light_source_config" : {
            "num_levels" : 250,
            "radius" : 10.0, 
            "max_opacity_ambient" : 1.0,
            "opacity_function" : inverse_quadratic(1,0.25,1)
        }
    }
    def construct(self):
        equation = TexMobject(
            "1", "+", "{1\over 4}", "+", 
            "{1\over 9}","+", "{1\over 16}","+", 
            "{1\over 25}", "+", "\cdots"
        )
        equation.scale(1.8)
        equation.move_to(2*UP)
        equation.set_stroke(RED, 1)
        answer = TexMobject("= \\frac{\\pi^2}{6}", color = LIGHT_COLOR)
        answer.scale(3)
        answer.set_stroke(RED, 1)
        # answer.next_to(equation, DOWN, buff = 1)
        answer.move_to(1.25*DOWN)
        #equation.move_to(2 * UP)
        #answer = TexMobject("={\pi^2\over 6}", color = LIGHT_COLOR).scale(3)
        #answer.next_to(equation, DOWN, buff = 1)

        lake_radius = 6
        lake_center = ORIGIN

        lake = Circle(
            fill_color = BLUE, 
            fill_opacity = 0.15,
            radius = lake_radius,
            stroke_color = BLUE_D, 
            stroke_width = 3,
        )
        lake.move_to(lake_center)

        for i in range(16):
            theta = -TAU/4 + (i + 0.5) * TAU/16
            pos = lake_center + lake_radius * np.array([np.cos(theta), np.sin(theta), 0])
            ls = LightSource(**self.light_source_config)
            ls.move_source_to(pos)
            lake.add(ls.ambient_light)
            lake.add(ls.lighthouse)

        self.add(lake)
        self.add(equation, answer)
        self.wait()












