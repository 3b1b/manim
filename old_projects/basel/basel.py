#!/usr/bin/env python


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
NUM_CONES = 7 # in first lighthouse scene
NUM_VISIBLE_CONES = 5 # ibidem
ARC_TIP_LENGTH = 0.2

NUM_LEVELS = 15
AMBIENT_FULL = 0.8
AMBIENT_DIMMED = 0.5
AMBIENT_SCALE = 2.0
AMBIENT_RADIUS = 20.0
SPOTLIGHT_FULL = 0.8
SPOTLIGHT_DIMMED = 0.2
SPOTLIGHT_SCALE = 1.0
SPOTLIGHT_RADIUS = 20.0

LIGHT_COLOR = YELLOW
DEGREES = TAU/360


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
        self.angle_arc.add_tip(tip_length = ARC_TIP_LENGTH,
            at_start = True, at_end = True)





class LightIndicator(VMobject):
    CONFIG = {
        "radius": 0.5,
        "intensity": 0,
        "opacity_for_unit_intensity": 1,
        "precision": 3,
        "show_reading": True,
        "measurement_point": ORIGIN,
        "light_source": None
    }

    def generate_points(self):
        self.background = Circle(color=BLACK, radius = self.radius)
        self.background.set_fill(opacity=1.0)
        self.foreground = Circle(color=self.color, radius = self.radius)
        self.foreground.set_stroke(color=INDICATOR_STROKE_COLOR,width=INDICATOR_STROKE_WIDTH)

        self.add(self.background, self.foreground)
        self.reading = DecimalNumber(self.intensity,num_decimal_places = self.precision)
        self.reading.set_fill(color=INDICATOR_TEXT_COLOR)
        self.reading.move_to(self.get_center())
        if self.show_reading:
            self.add(self.reading)

    def set_intensity(self, new_int):
        self.intensity = new_int
        new_opacity = min(1, new_int * self.opacity_for_unit_intensity)
        self.foreground.set_fill(opacity=new_opacity)
        ChangeDecimalToValue(self.reading, new_int).update(1)
        return self

    def get_measurement_point(self):
        if self.measurement_point != None:
            return self.measurement_point
        else:
            return self.get_center()


    def measured_intensity(self):
        distance = get_norm(self.get_measurement_point() - 
            self.light_source.get_source_point())
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

                # ambient_of = copy_func(submob.ambient_light.opacity_function)
                # new_of = lambda r: ambient_of(r / factor)
                # submob.ambient_light.change_opacity_function(new_of)

                # spotlight_of = copy_func(submob.ambient_light.opacity_function)
                # new_of = lambda r: spotlight_of(r / factor)
                # submob.spotlight.change_opacity_function(new_of)

                new_r = factor * submob.radius
                submob.set_radius(new_r)

                new_r = factor * submob.ambient_light.radius
                submob.ambient_light.radius = new_r

                new_r = factor * submob.spotlight.radius
                submob.spotlight.radius = new_r

                submob.ambient_light.scale_about_point(factor, new_sp.get_center())
                submob.spotlight.scale_about_point(factor, new_sp.get_center())


        Transform.__init__(self,light_sources_mob,ls_target,**kwargs)


















class IntroScene(PiCreatureScene):

    CONFIG = {
        "rect_height" : 0.2,
        "duration" : 0.5,
        "eq_spacing" : 6 * MED_LARGE_BUFF
    }

    def construct(self):

        randy = self.get_primary_pi_creature()
        randy.scale(0.7).to_corner(DOWN+RIGHT)

        self.build_up_euler_sum()
        self.build_up_sum_on_number_line()
        self.show_pi_answer()
        self.other_pi_formulas()
        self.refocus_on_euler_sum()





    def build_up_euler_sum(self):

        self.euler_sum = TexMobject(
           "1", "+", 
           "{1 \\over 4}", "+",
           "{1 \\over 9}", "+",
           "{1 \\over 16}", "+",
           "{1 \\over 25}", "+",
           "\\cdots", "=",
            arg_separator = " \\, "
        )

        self.euler_sum.to_edge(UP)
        self.euler_sum.shift(2*LEFT)
       
        terms = [1./n**2 for n in range(1,6)]
        partial_results_values = np.cumsum(terms)

        self.play(
               FadeIn(self.euler_sum[0], run_time = self.duration)
        )

        equals_sign = self.euler_sum.get_part_by_tex("=")

        self.partial_sum_decimal = DecimalNumber(partial_results_values[1],
                num_decimal_places = 2)
        self.partial_sum_decimal.next_to(equals_sign, RIGHT)



        for i in range(4):

            FadeIn(self.partial_sum_decimal, run_time = self.duration)

            if i == 0:

                self.play(
                    FadeIn(self.euler_sum[1], run_time = self.duration),
                    FadeIn(self.euler_sum[2], run_time = self.duration),
                    FadeIn(equals_sign, run_time = self.duration),
                    FadeIn(self.partial_sum_decimal, run_time = self.duration)
                )

            else:
                self.play(
                    FadeIn(self.euler_sum[2*i+1], run_time = self.duration),
                    FadeIn(self.euler_sum[2*i+2], run_time = self.duration),
                    ChangeDecimalToValue(
                        self.partial_sum_decimal,
                        partial_results_values[i+1], 
                        run_time = self.duration,
                        num_decimal_places = 6,
                        show_ellipsis = True,
                        position_update_func = lambda m: m.next_to(equals_sign, RIGHT)
                    )
                )
                
            self.wait()

        self.q_marks = TextMobject("???").set_color(LIGHT_COLOR)
        self.q_marks.move_to(self.partial_sum_decimal)

        self.play(
            FadeIn(self.euler_sum[-3], run_time = self.duration), # +
            FadeIn(self.euler_sum[-2], run_time = self.duration), # ...
            ReplacementTransform(self.partial_sum_decimal, self.q_marks)
        )

        self.wait()



    def build_up_sum_on_number_line(self):

        self.number_line = NumberLine(
            x_min = 0,
            color = WHITE,
            number_at_center = 1,
            stroke_width = 1,
            numbers_with_elongated_ticks = [0,1,2,3],
            numbers_to_show = np.arange(0,5),
            unit_size = 5,
            tick_frequency = 0.2,
            line_to_number_buff = MED_LARGE_BUFF
        ).shift(LEFT)

        self.number_line_labels = self.number_line.get_number_mobjects()
        self.play(
            FadeIn(self.number_line),
            FadeIn(self.number_line_labels)
        )
        self.wait()

        # create slabs for series terms

        max_n1 = 10
        max_n2 = 100

        terms = [0] + [1./(n**2) for n in range(1, max_n2 + 1)]
        series_terms = np.cumsum(terms)
        lines = VGroup()
        self.rects = VGroup()
        slab_colors = [YELLOW, BLUE] * (max_n2 / 2)

        for t1, t2, color in zip(series_terms, series_terms[1:], slab_colors):
            line = Line(*list(map(self.number_line.number_to_point, [t1, t2])))
            rect = Rectangle()
            rect.stroke_width = 0
            rect.fill_opacity = 1
            rect.set_color(color)
            rect.stretch_to_fit_height(
                self.rect_height,
            )
            rect.stretch_to_fit_width(0.5 * line.get_width())
            rect.move_to(line)

            self.rects.add(rect)
            lines.add(line)

        #self.rects.set_colors_by_radial_gradient(ORIGIN, 5, YELLOW, BLUE)
        
        self.little_euler_terms = VGroup()
        for i in range(1,7):
            if i == 1:
                term = TexMobject("1", fill_color = slab_colors[i-1])
            else:
                term = TexMobject("{1\over " + str(i**2) + "}", fill_color = slab_colors[i-1])
            term.scale(0.4)
            self.little_euler_terms.add(term)


        for i in range(5):
            self.play(
                GrowFromPoint(self.rects[i], self.euler_sum[2*i].get_center(),
                    run_time = 1)
            )
            term = self.little_euler_terms.submobjects[i]
            term.next_to(self.rects[i], UP)
            self.play(FadeIn(term))

        self.ellipsis = TexMobject("\cdots")
        self.ellipsis.scale(0.4)
        for i in range(5, max_n1):
            
            if i == 5:
                self.ellipsis.next_to(self.rects[i+3], UP)
                self.play(
                    FadeIn(self.ellipsis),
                    GrowFromPoint(self.rects[i], self.euler_sum[10].get_center(),
                    run_time = 0.5)
                )
            else:
                self.play(
                    GrowFromPoint(self.rects[i], self.euler_sum[10].get_center(),
                    run_time = 0.5)
                )
        for i in range(max_n1, max_n2):
            self.play(
                    GrowFromPoint(self.rects[i], self.euler_sum[10].get_center(),
                    run_time = 0.01)
                )

        self.wait()

        PI = TAU/2
        P = self.q_marks.get_center() + 0.5 * DOWN + 0.5 * LEFT
        Q = self.rects[-1].get_center() + 0.2 * UP
        self.arrow = CurvedArrow(P, Q,
            angle = TAU/12,
            color = YELLOW
        )

        self.play(FadeIn(self.arrow))

        self.wait()


    def show_pi_answer(self):

        self.pi_answer = TexMobject("{\\pi^2 \\over 6}").set_color(YELLOW)
        self.pi_answer.move_to(self.partial_sum_decimal)
        self.pi_answer.next_to(self.euler_sum[-1], RIGHT, buff = 1,
            submobject_to_align = self.pi_answer[-2])
        self.play(ReplacementTransform(self.q_marks, self.pi_answer))

        self.wait()


    def other_pi_formulas(self):

        self.play(
            FadeOut(self.rects),
            FadeOut(self.number_line_labels),
            FadeOut(self.number_line),
            FadeOut(self.little_euler_terms),
            FadeOut(self.ellipsis),
            FadeOut(self.arrow)
        )

        self.leibniz_sum = TexMobject(
            "1-{1\\over 3}+{1\\over 5}-{1\\over 7}+{1\\over 9}-\\cdots",
            "=", "\quad\,\,{\\pi \\over 4}", arg_separator = " \\, ")

        self.wallis_product = TexMobject(
            "{2\\over 1} \\cdot {2\\over 3} \\cdot {4\\over 3} \\cdot {4\\over 5}" +
             "\\cdot {6\\over 5} \\cdot {6\\over 7} \\cdots",
             "=", "\quad\,\, {\\pi \\over 2}", arg_separator = " \\, ")

        self.leibniz_sum.next_to(self.euler_sum.get_part_by_tex("="), DOWN,
            buff = 2,
            submobject_to_align = self.leibniz_sum.get_part_by_tex("=")
        )

        self.wallis_product.next_to(self.leibniz_sum.get_part_by_tex("="), DOWN,
            buff = 2,
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
            WiggleOutThenIn(pi_squared,
                scale_value = 4,
                angle = 0.003 * TAU,
                run_time = 2
            )
        )



        # Morty thinks of a circle

        q_circle = Circle(
            stroke_color = YELLOW,
            fill_color = YELLOW,
            fill_opacity = 0.25,
            radius = 0.5, 
            stroke_width = 3.0
        )
        q_mark = TexMobject("?")
        q_mark.next_to(q_circle)

        thought = Group(q_circle, q_mark)
        q_mark.set_height(0.6 * q_circle.get_height())

        self.look_at(pi_squared)
        self.pi_creature_thinks(thought,target_mode = "confused",
            bubble_kwargs = { "height" : 2.5, "width" : 5 })
        self.look_at(pi_squared)

        self.wait()




















class FirstLighthouseScene(PiCreatureScene):

    def construct(self):
        self.remove(self.get_primary_pi_creature())
        self.show_lighthouses_on_number_line()



    def show_lighthouses_on_number_line(self):

        self.number_line = NumberLine(
            x_min = 0,
            color = WHITE,
            number_at_center = 1.6,
            stroke_width = 1,
            numbers_with_elongated_ticks = list(range(1,5)),
            numbers_to_show = list(range(1,5)),
            unit_size = 2,
            tick_frequency = 0.2,
            line_to_number_buff = LARGE_BUFF,
            label_direction = UP,
        )

        self.number_line.label_direction = DOWN

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



        light_indicator = LightIndicator(radius = INDICATOR_RADIUS,
            opacity_for_unit_intensity = OPACITY_FOR_UNIT_INTENSITY,
            color = LIGHT_COLOR)
        light_indicator.reading.scale(0.8)

        bubble = ThoughtBubble(direction = RIGHT,
                            width = 2.5, height = 3.5)
        bubble.next_to(randy,LEFT+UP)
        bubble.add_content(light_indicator)
        self.wait()
        self.play(
            randy.change, "wave_2",
            ShowCreation(bubble),
            FadeIn(light_indicator)
        )

        light_sources = []


        euler_sum_above = TexMobject("1", "+", "{1\over 4}", 
            "+", "{1\over 9}", "+", "{1\over 16}", "+", "{1\over 25}", "+", "{1\over 36}")

        for (i,term) in zip(list(range(len(euler_sum_above))),euler_sum_above):
            #horizontal alignment with tick marks
            term.next_to(self.number_line.number_to_point(0.5*i+1),UP,buff = 2)
            # vertical alignment with light indicator
            old_y = term.get_center()[1]
            new_y = light_indicator.get_center()[1]
            term.shift([0,new_y - old_y,0])
            


        for i in range(1,NUM_CONES+1):
            light_source = LightSource(
                opacity_function = inverse_quadratic(1,AMBIENT_SCALE,1),
                num_levels = NUM_LEVELS,
                radius = AMBIENT_RADIUS,
            )
            point = self.number_line.number_to_point(i)
            light_source.move_source_to(point)
            light_sources.append(light_source)

        self.wait()
        for ls in light_sources:
            self.add_foreground_mobject(ls.lighthouse)

        light_indicator.set_intensity(0)

        intensities = np.cumsum(np.array([1./n**2 for n in range(1,NUM_CONES+1)]))
        opacities = intensities * light_indicator.opacity_for_unit_intensity

        self.remove_foreground_mobjects(light_indicator)


        # slowly switch on visible light cones and increment indicator
        for (i,light_source) in zip(list(range(NUM_VISIBLE_CONES)),light_sources[:NUM_VISIBLE_CONES]):
            indicator_start_time = 1.0 * (i+1) * SWITCH_ON_RUN_TIME/light_source.radius * self.number_line.unit_size
            indicator_stop_time = indicator_start_time + INDICATOR_UPDATE_TIME
            indicator_rate_func = squish_rate_func(
                smooth,indicator_start_time,indicator_stop_time)
            self.play(
                SwitchOn(light_source.ambient_light),
                FadeIn(euler_sum_above[2*i], run_time = SWITCH_ON_RUN_TIME,
                    rate_func = indicator_rate_func),
                FadeIn(euler_sum_above[2*i - 1], run_time = SWITCH_ON_RUN_TIME,
                    rate_func = indicator_rate_func),
                # this last line *technically* fades in the last term, but it is off-screen
                ChangeDecimalToValue(light_indicator.reading,intensities[i],
                    rate_func = indicator_rate_func, run_time = SWITCH_ON_RUN_TIME),
                ApplyMethod(light_indicator.foreground.set_fill,None,opacities[i],
                    rate_func = indicator_rate_func, run_time = SWITCH_ON_RUN_TIME)
            )

            if i == 0:
                self.wait()
                # move a copy out of the thought bubble for comparison
                light_indicator_copy = light_indicator.copy()
                old_y = light_indicator_copy.get_center()[1]
                new_y = self.number_line.get_center()[1]
                self.play(
                    light_indicator_copy.shift,[0, new_y - old_y,0]
                )

            self.wait()

        self.wait()

        # quickly switch on off-screen light cones and increment indicator
        for (i,light_source) in zip(list(range(NUM_VISIBLE_CONES,NUM_CONES)),light_sources[NUM_VISIBLE_CONES:NUM_CONES]):
            indicator_start_time = 0.5 * (i+1) * FAST_SWITCH_ON_RUN_TIME/light_source.radius * self.number_line.unit_size
            indicator_stop_time = indicator_start_time + FAST_INDICATOR_UPDATE_TIME
            indicator_rate_func = squish_rate_func(#smooth, 0.8, 0.9)
                smooth,indicator_start_time,indicator_stop_time)
            self.play(
                SwitchOn(light_source.ambient_light, run_time = FAST_SWITCH_ON_RUN_TIME),
                ChangeDecimalToValue(light_indicator.reading,intensities[i-1],
                    rate_func = indicator_rate_func, run_time = FAST_SWITCH_ON_RUN_TIME),
                ApplyMethod(light_indicator.foreground.set_fill,None,opacities[i-1])
            )


        # show limit value in light indicator and an equals sign
        limit_reading = TexMobject("{\pi^2 \over 6}")
        limit_reading.move_to(light_indicator.reading)

        equals_sign = TexMobject("=")
        equals_sign.next_to(randy, UP)
        old_y = equals_sign.get_center()[1]
        new_y = euler_sum_above.get_center()[1]
        equals_sign.shift([0,new_y - old_y,0])

        self.play(
            FadeOut(light_indicator.reading),
            FadeIn(limit_reading),
            FadeIn(equals_sign),
        )

            

        self.wait()

        





















class SingleLighthouseScene(PiCreatureScene):

    def construct(self):

        self.setup_elements()
        self.setup_angle() # spotlight and angle msmt change when screen rotates
        self.rotate_screen()
        #self.morph_lighthouse_into_sun()


    def setup_elements(self):

        self.remove(self.get_primary_pi_creature())

        SCREEN_SIZE = 3.0
        DISTANCE_FROM_LIGHTHOUSE = 10.0
        source_point = [-DISTANCE_FROM_LIGHTHOUSE/2,0,0]
        observer_point = [DISTANCE_FROM_LIGHTHOUSE/2,0,0]

        # Light source

        self.light_source = LightSource(
            opacity_function = inverse_quadratic(1,SPOTLIGHT_SCALE,1),
            num_levels = NUM_LEVELS,
            radius = 10,
            max_opacity_ambient = AMBIENT_FULL,
            max_opacity_spotlight = SPOTLIGHT_FULL,

        )

        self.light_source.move_source_to(source_point)


        # Pi Creature

        morty = self.get_primary_pi_creature()
        morty.scale(0.5)
        morty.move_to(observer_point)
        morty.shift(2*OUT)
        self.add_foreground_mobject(morty)

        self.add(self.light_source.lighthouse)

        self.play(
            SwitchOn(self.light_source.ambient_light)
        )

        # Screen

        self.screen = Rectangle(
            width = 0.06,
            height = 2,
            mark_paths_closed = True,
            fill_color = WHITE,
            fill_opacity = 1.0,
            stroke_width = 0.0
        )

        self.screen.rotate(-TAU/6)
        self.screen.next_to(morty,LEFT)

        self.light_source.set_screen(self.screen)

        # Animations

        self.play(FadeIn(self.screen))

        #self.light_source.set_max_opacity_spotlight(0.001)
        #self.play(SwitchOn(self.light_source.spotlight))


        self.wait()




        # just calling .dim_ambient via ApplyMethod does not work, why?
        dimmed_ambient_light = self.light_source.ambient_light.deepcopy()
        dimmed_ambient_light.dimming(AMBIENT_DIMMED)
        self.light_source.update_shadow()

        self.play(
            FadeIn(self.light_source.shadow),
        )
        self.add_foreground_mobject(self.light_source.shadow)
        self.add_foreground_mobject(morty)

        self.play(
            self.light_source.dim_ambient,
            #Transform(self.light_source.ambient_light,dimmed_ambient_light),
            #self.light_source.set_max_opacity_spotlight,1.0,
        )
        self.play(
            FadeIn(self.light_source.spotlight)
        )

        self.screen_tracker = ScreenTracker(self.light_source)
        self.add(self.screen_tracker)

        self.wait()




    def setup_angle(self):

        self.wait()

        
        pointing_screen_at_source = Rotate(self.screen,TAU/6)
        self.play(pointing_screen_at_source)

        # angle msmt (arc)

        arc_angle = self.light_source.spotlight.opening_angle()
        # draw arc arrows to show the opening angle
        self.angle_arc = Arc(radius = 5, start_angle = self.light_source.spotlight.start_angle(),
            angle = self.light_source.spotlight.opening_angle(), tip_length = ARC_TIP_LENGTH)
        #angle_arc.add_tip(at_start = True, at_end = True)
        self.angle_arc.move_arc_center_to(self.light_source.get_source_point())
        

        # angle msmt (decimal number)

        self.angle_indicator = DecimalNumber(arc_angle / DEGREES,
            num_decimal_places = 0,
            unit = "^\\circ",
            fill_opacity = 1.0,
            fill_color = WHITE)
        self.angle_indicator.next_to(self.angle_arc,RIGHT)

        angle_update_func = lambda x: self.light_source.spotlight.opening_angle() / DEGREES
        self.angle_indicator.add_updater(
            lambda d: d.set_value(angle_update_func())
        )
        self.add(self.angle_indicator)

        ca2 = AngleUpdater(self.angle_arc, self.light_source.spotlight)
        self.add(ca2)

        self.play(
            ShowCreation(self.angle_arc),
            ShowCreation(self.angle_indicator)
        )

        self.wait()

    def rotate_screen(self):



        self.play(Rotate(self.light_source.spotlight.screen, TAU/8))
        self.play(Rotate(self.light_source.spotlight.screen, -TAU/4))

        self.play(Rotate(self.light_source.spotlight.screen, TAU/8))

        self.wait()

        self.play(Rotate(self.light_source.spotlight.screen, -TAU/4))

        self.wait()

        self.play(Rotate(self.light_source.spotlight.screen, TAU/4))

### The following is supposed to morph the scene into the Earth scene,
### but it doesn't work


class MorphIntoSunScene(PiCreatureScene):
    def construct(self):
        self.setup_elements()
        self.morph_lighthouse_into_sun()

    def setup_elements(self):
        self.remove(self.get_primary_pi_creature())

        SCREEN_SIZE = 3.0
        DISTANCE_FROM_LIGHTHOUSE = 10.0
        source_point = [-DISTANCE_FROM_LIGHTHOUSE/2,0,0]
        observer_point = [DISTANCE_FROM_LIGHTHOUSE/2,0,0]

        # Light source

        self.light_source = LightSource(
            opacity_function = inverse_quadratic(1,SPOTLIGHT_SCALE,1),
            num_levels = NUM_LEVELS,
            radius = 10,
            max_opacity_ambient = AMBIENT_FULL,
            max_opacity_spotlight = SPOTLIGHT_FULL,

        )

        self.light_source.move_source_to(source_point)


        # Pi Creature

        morty = self.get_primary_pi_creature()
        morty.scale(0.5)
        morty.move_to(observer_point)
        morty.shift(2*OUT)
        self.add_foreground_mobject(morty)

        self.add(self.light_source.lighthouse,self.light_source.ambient_light)
        

        # Screen

        self.screen = Rectangle(
            width = 0.06,
            height = 2,
            mark_paths_closed = True,
            fill_color = WHITE,
            fill_opacity = 1.0,
            stroke_width = 0.0
        )

        self.screen.next_to(morty,LEFT)

        self.light_source.set_screen(self.screen)
        self.add(self.screen,self.light_source.shadow)
        
        self.add_foreground_mobject(self.light_source.shadow)
        self.add_foreground_mobject(morty)
        self.light_source.dim_ambient
        self.add(self.light_source.spotlight)
        self.screen_tracker = ScreenTracker(self.light_source)
        self.add(self.screen_tracker)

        self.wait()


    def morph_lighthouse_into_sun(self):

        sun_position = np.array([-100,0,0])




        # Why does none of this change the opacity function???

        self.sun = self.light_source.copy()

        self.sun.change_spotlight_opacity_function(lambda r: 0.1)
        # self.sun.spotlight.opacity_function = lambda r: 0.1
        # for submob in self.sun.spotlight.submobjects:
        #     submob.set_fill(opacity = 0.1)

        #self.sun.move_source_to(sun_position)
        #self.sun.set_radius(120)

        self.sun.spotlight.generate_points()

        self.wait()

        self.play(
             Transform(self.light_source,self.sun)
        )

        self.wait()




 














class EarthScene(Scene):

    def construct(self):

        SCREEN_THICKNESS = 10

        self.screen_height = 2.0
        self.brightness_rect_height = 1.0

        # screen
        self.screen = VMobject(stroke_color = WHITE, stroke_width = SCREEN_THICKNESS)
        self.screen.set_points_as_corners([
            [0,-self.screen_height/2,0],
            [0,self.screen_height/2,0]
        ])

        # Earth

        earth_center_x = 2
        earth_center = [earth_center_x,0,0]
        earth_radius = 3
        earth = Circle(radius = earth_radius)
        earth.add(self.screen)
        earth.move_to(earth_center)
        #self.remove(self.screen_tracker)

        theta0 = 70 * DEGREES
        dtheta = 10 * DEGREES
        theta1 = theta0 + dtheta
        theta = (theta0 + theta1)/2

        self.add_foreground_mobject(self.screen)

        # background Earth
        background_earth = SVGMobject(
            file_name = "earth",
            width = 2 * earth_radius,
            fill_color = BLUE,
        )
        background_earth.move_to(earth_center)
        # Morty

        morty = Mortimer().scale(0.5).next_to(self.screen, RIGHT, buff = 1.5)
        self.add_foreground_mobject(morty)


        # Light source (far-away Sun)

        sun_position = [-100,0,0]

        self.sun = LightSource(
            opacity_function = lambda r : 0.5,
            max_opacity_ambient = 0,
            max_opacity_spotlight = 0.5,
            num_levels = NUM_LEVELS,
            radius = 150,
            screen = self.screen
        )

        self.sun.move_source_to(sun_position)


        # Add elements to scene

        self.add(self.sun,self.screen)
        self.bring_to_back(self.sun.shadow)
        screen_tracker = ScreenTracker(self.sun)

        self.add(screen_tracker)
        
        self.wait()

        self.play(
            FadeIn(earth),
            FadeIn(background_earth)
        )
        self.add_foreground_mobject(earth)
        self.add_foreground_mobject(self.screen)


        # move screen onto Earth
        screen_on_earth = self.screen.deepcopy()
        screen_on_earth.rotate(-theta)
        screen_on_earth.scale(0.3)
        screen_on_earth.move_to(np.array([
            earth_center_x - earth_radius * np.cos(theta),
            earth_radius * np.sin(theta),
            0]))

        polar_morty = morty.copy().scale(0.5).next_to(screen_on_earth,DOWN,buff = 0.5)
        polar_morty.set_color(BLUE_C)

        self.play(
            Transform(self.screen, screen_on_earth),
            Transform(morty,polar_morty)
        )

        self.wait()


        tropical_morty = polar_morty.copy()
        tropical_morty.move_to(np.array([0,0,0]))
        tropical_morty.set_color(RED)

        morty.target = tropical_morty

        # move screen to equator

        self.play(
            Rotate(earth, theta0 + dtheta/2,run_time = 3),
            MoveToTarget(morty, path_arc = 70*DEGREES, run_time = 3),
        )

























class ScreenShapingScene(ThreeDScene):


    # TODO: Morph from Earth Scene into this scene

    def construct(self):

        #self.force_skipping()
        self.setup_elements()
        self.deform_screen()
        self.create_brightness_rect()
        self.slant_screen()
        self.unslant_screen()
        self.left_shift_screen_while_showing_light_indicator()
        self.add_distance_arrow()
        self.right_shift_screen_while_showing_light_indicator_and_distance_arrow()
        self.left_shift_again()
        #self.revert_to_original_skipping_status()
        
        self.morph_into_3d()
        self.prove_inverse_square_law()


    def setup_elements(self):

        SCREEN_THICKNESS = 10

        self.screen_height = 1.0
        self.brightness_rect_height = 1.0

        # screen
        self.screen = Line([3,-self.screen_height/2,0],[3,self.screen_height/2,0],
            path_arc = 0, num_arc_anchors = 10)
        
        # light source
        self.light_source = LightSource(
            opacity_function = inverse_quadratic(1,5,1),
            num_levels = NUM_LEVELS,
            radius = 10,
            max_opacity = 0.2
            #screen = self.screen
        )
        self.light_source.set_max_opacity_spotlight(0.2)

        self.light_source.set_screen(self.screen)
        self.light_source.move_source_to([-5,0,0])

        # abbreviations
        self.ambient_light = self.light_source.ambient_light
        self.spotlight = self.light_source.spotlight
        self.lighthouse = self.light_source.lighthouse

        
        #self.add_foreground_mobject(self.light_source.shadow)

        # Morty
        self.morty = Mortimer().scale(0.3).next_to(self.screen, RIGHT, buff = 0.5)

        # Add everything to the scene
        self.add(self.lighthouse)
        
        self.wait()
        self.play(FadeIn(self.screen))
        self.wait()

        self.add_foreground_mobject(self.screen)
        self.add_foreground_mobject(self.morty)

        self.play(SwitchOn(self.ambient_light))

        self.play(
            SwitchOn(self.spotlight),
            self.light_source.dim_ambient
        )

        screen_tracker = ScreenTracker(self.light_source)
        self.add(screen_tracker)


        self.wait()



    def deform_screen(self):

        self.wait()

        self.play(ApplyMethod(self.screen.set_path_arc, 45 * DEGREES))
        self.play(ApplyMethod(self.screen.set_path_arc, -90 * DEGREES))
        self.play(ApplyMethod(self.screen.set_path_arc, 0))




    def create_brightness_rect(self):

        # in preparation for the slanting, create a rectangle that shows the brightness

        # a rect a zero width overlaying the screen
        # so we can morph it into the brightness rect above
        brightness_rect0 = Rectangle(width = 0,
            height = self.screen_height).move_to(self.screen.get_center())
        self.add_foreground_mobject(brightness_rect0)

        self.brightness_rect = Rectangle(width = self.brightness_rect_height,
            height = self.brightness_rect_height, fill_color = YELLOW, fill_opacity = 0.5)

        self.brightness_rect.next_to(self.screen, UP, buff = 1)

        self.play(
            ReplacementTransform(brightness_rect0,self.brightness_rect)
        )

        self.unslanted_screen = self.screen.deepcopy()
        self.unslanted_brightness_rect = self.brightness_rect.copy()
        # for unslanting the screen later


    def slant_screen(self):

        SLANTING_AMOUNT = 0.1

        lower_screen_point, upper_screen_point = self.screen.get_start_and_end()

        lower_slanted_screen_point = interpolate(
            lower_screen_point, self.spotlight.get_source_point(), SLANTING_AMOUNT
        )
        upper_slanted_screen_point = interpolate(
            upper_screen_point, self.spotlight.get_source_point(), -SLANTING_AMOUNT
        )

        self.slanted_brightness_rect = self.brightness_rect.copy()
        self.slanted_brightness_rect.width *= 2
        self.slanted_brightness_rect.generate_points()
        self.slanted_brightness_rect.set_fill(opacity = 0.25)

        self.slanted_screen = Line(lower_slanted_screen_point,upper_slanted_screen_point,
            path_arc = 0, num_arc_anchors = 10)
        self.slanted_brightness_rect.move_to(self.brightness_rect.get_center())

        self.play(
             Transform(self.screen,self.slanted_screen),
             Transform(self.brightness_rect,self.slanted_brightness_rect),
        )



    def unslant_screen(self):

        self.wait()        
        self.play(
            Transform(self.screen,self.unslanted_screen),
            Transform(self.brightness_rect,self.unslanted_brightness_rect),
        )




    def left_shift_screen_while_showing_light_indicator(self):

        # Scene 5: constant screen size, changing opening angle

        OPACITY_FOR_UNIT_INTENSITY = 1

        # let's use an actual light indicator instead of just rects

        self.indicator_intensity = 0.25
        indicator_height = 1.25 * self.screen_height

        self.indicator = LightIndicator(radius = indicator_height/2,
            opacity_for_unit_intensity = OPACITY_FOR_UNIT_INTENSITY,
            color = LIGHT_COLOR,
            precision = 2)
        self.indicator.set_intensity(self.indicator_intensity)

        self.indicator.move_to(self.brightness_rect.get_center())

        self.play(
            FadeOut(self.brightness_rect),
            FadeIn(self.indicator)
        )

        # Here some digits of the indicator disappear...

        self.add_foreground_mobject(self.indicator.reading)


        self.unit_indicator_intensity = 1.0 # intensity at distance 1
                                            # (where we are about to move to)

        self.left_shift = (self.screen.get_center()[0] - self.spotlight.get_source_point()[0])/2

        self.play(
            self.screen.shift,[-self.left_shift,0,0],
            self.morty.shift,[-self.left_shift,0,0],
            self.indicator.shift,[-self.left_shift,0,0],
            self.indicator.set_intensity,self.unit_indicator_intensity,
        )
        


    def add_distance_arrow(self):

        # distance arrow (length 1)
        left_x = self.spotlight.get_source_point()[0]
        right_x = self.screen.get_center()[0]
        arrow_y = -2
        arrow1 = Arrow([left_x,arrow_y,0],[right_x,arrow_y,0])
        arrow2 = Arrow([right_x,arrow_y,0],[left_x,arrow_y,0])
        arrow1.set_fill(color = WHITE)
        arrow2.set_fill(color = WHITE)
        distance_decimal = Integer(1).next_to(arrow1,DOWN)
        self.arrow = VGroup(arrow1, arrow2,distance_decimal)
        self.add(self.arrow)


        # distance arrow (length 2)
        # will be morphed into
        self.distance_to_source = right_x - left_x
        new_right_x = left_x + 2 * self.distance_to_source
        new_arrow1 = Arrow([left_x,arrow_y,0],[new_right_x,arrow_y,0])
        new_arrow2 = Arrow([new_right_x,arrow_y,0],[left_x,arrow_y,0])
        new_arrow1.set_fill(color = WHITE)
        new_arrow2.set_fill(color = WHITE)
        new_distance_decimal = Integer(2).next_to(new_arrow1,DOWN)
        self.new_arrow = VGroup(new_arrow1, new_arrow2, new_distance_decimal)
        # don't add it yet


    def right_shift_screen_while_showing_light_indicator_and_distance_arrow(self):

        self.wait()

        self.play(
            ReplacementTransform(self.arrow,self.new_arrow),
            ApplyMethod(self.screen.shift,[self.distance_to_source,0,0]),
            ApplyMethod(self.indicator.shift,[self.left_shift,0,0]),
            
            ApplyMethod(self.indicator.set_intensity,self.indicator_intensity),
            # this should trigger ChangingDecimal, but it doesn't
            # maybe bc it's an anim within an anim?

            ApplyMethod(self.morty.shift,[self.distance_to_source,0,0]),
        )


    def left_shift_again(self):

        self.wait()

        self.play(
            ReplacementTransform(self.new_arrow,self.arrow),
            ApplyMethod(self.screen.shift,[-self.distance_to_source,0,0]),
            #ApplyMethod(self.indicator.shift,[-self.left_shift,0,0]),
            ApplyMethod(self.indicator.set_intensity,self.unit_indicator_intensity),
            ApplyMethod(self.morty.shift,[-self.distance_to_source,0,0]),
        )

    def morph_into_3d(self):


        self.play(FadeOut(self.morty))

        axes = ThreeDAxes()
        self.add(axes)

        phi0 = self.camera.get_phi() # default is 0 degs
        theta0 = self.camera.get_theta() # default is -90 degs
        distance0 = self.camera.get_distance()

        phi1 = 60 * DEGREES # angle from zenith (0 to 180)
        theta1 = -135 * DEGREES # azimuth (0 to 360)
        distance1 = distance0
        target_point = self.camera.get_spherical_coords(phi1, theta1, distance1)

        dphi = phi1 - phi0
        dtheta = theta1 - theta0

        camera_target_point = target_point # self.camera.get_spherical_coords(45 * DEGREES, -60 * DEGREES)
        projection_direction = self.camera.spherical_coords_to_point(phi1,theta1, 1)

        new_screen0 = Rectangle(height = self.screen_height,
            width = 0.1, stroke_color = RED, fill_color = RED, fill_opacity = 1)
        new_screen0.rotate(TAU/4,axis = DOWN)
        new_screen0.move_to(self.screen.get_center())
        self.add(new_screen0)
        self.remove(self.screen)
        self.light_source.set_screen(new_screen0)

        self.light_source.set_camera(self.camera)


        new_screen = Rectangle(height = self.screen_height,
            width = self.screen_height, stroke_color = RED, fill_color = RED, fill_opacity = 1)
        new_screen.rotate(TAU/4,axis = DOWN)
        new_screen.move_to(self.screen.get_center())

        self.add_foreground_mobject(self.ambient_light)
        self.add_foreground_mobject(self.spotlight)
        self.add_foreground_mobject(self.light_source.shadow)

        self.play(
             ApplyMethod(self.camera.rotation_mobject.move_to, camera_target_point),
             
        )
        self.remove(self.spotlight)

        self.play(Transform(new_screen0,new_screen))

        self.wait()

        self.unit_screen = new_screen0 # better name



    def prove_inverse_square_law(self):

        def orientate(mob):
            mob.move_to(self.unit_screen)
            mob.rotate(TAU/4, axis = LEFT)
            mob.rotate(TAU/4, axis = OUT)
            mob.rotate(TAU/2, axis = LEFT)
            return mob

        unit_screen_copy = self.unit_screen.copy()
        fourfold_screen = self.unit_screen.copy()
        fourfold_screen.scale(2,about_point = self.light_source.get_source_point())

        self.remove(self.spotlight)


        reading1 = TexMobject("1")
        orientate(reading1)

        self.play(FadeIn(reading1))
        self.wait()
        self.play(FadeOut(reading1))
        

        self.play(
            Transform(self.unit_screen, fourfold_screen)
        )

        reading21 = TexMobject("{1\over 4}").scale(0.8)
        orientate(reading21)
        reading22 = reading21.deepcopy()
        reading23 = reading21.deepcopy()
        reading24 = reading21.deepcopy()
        reading21.shift(0.5*OUT + 0.5*UP)
        reading22.shift(0.5*OUT + 0.5*DOWN)
        reading23.shift(0.5*IN + 0.5*UP)
        reading24.shift(0.5*IN + 0.5*DOWN)


        corners = fourfold_screen.get_anchors()
        midpoint1 = (corners[0] + corners[1])/2
        midpoint2 = (corners[1] + corners[2])/2
        midpoint3 = (corners[2] + corners[3])/2
        midpoint4 = (corners[3] + corners[0])/2
        midline1 = Line(midpoint1, midpoint3)
        midline2 = Line(midpoint2, midpoint4)

        self.play(
            ShowCreation(midline1),
            ShowCreation(midline2)
        )

        self.play(
            FadeIn(reading21),
            FadeIn(reading22),
            FadeIn(reading23),
            FadeIn(reading24),
        )

        self.wait()

        self.play(
            FadeOut(reading21),
            FadeOut(reading22),
            FadeOut(reading23),
            FadeOut(reading24),
            FadeOut(midline1),
            FadeOut(midline2)
        )

        ninefold_screen = unit_screen_copy.copy()
        ninefold_screen.scale(3,about_point = self.light_source.get_source_point())

        self.play(
            Transform(self.unit_screen, ninefold_screen)
        )

        reading31 = TexMobject("{1\over 9}").scale(0.8)
        orientate(reading31)
        reading32 = reading31.deepcopy()
        reading33 = reading31.deepcopy()
        reading34 = reading31.deepcopy()
        reading35 = reading31.deepcopy()
        reading36 = reading31.deepcopy()
        reading37 = reading31.deepcopy()
        reading38 = reading31.deepcopy()
        reading39 = reading31.deepcopy()
        reading31.shift(IN + UP)
        reading32.shift(IN)
        reading33.shift(IN + DOWN)
        reading34.shift(UP)
        reading35.shift(ORIGIN)
        reading36.shift(DOWN)
        reading37.shift(OUT + UP)
        reading38.shift(OUT)
        reading39.shift(OUT + DOWN)

        corners = ninefold_screen.get_anchors()
        midpoint11 = (2*corners[0] + corners[1])/3
        midpoint12 = (corners[0] + 2*corners[1])/3
        midpoint21 = (2*corners[1] + corners[2])/3
        midpoint22 = (corners[1] + 2*corners[2])/3
        midpoint31 = (2*corners[2] + corners[3])/3
        midpoint32 = (corners[2] + 2*corners[3])/3
        midpoint41 = (2*corners[3] + corners[0])/3
        midpoint42 = (corners[3] + 2*corners[0])/3
        midline11 = Line(midpoint11, midpoint32)
        midline12 = Line(midpoint12, midpoint31)
        midline21 = Line(midpoint21, midpoint42)
        midline22 = Line(midpoint22, midpoint41)

        self.play(
            ShowCreation(midline11),
            ShowCreation(midline12),
            ShowCreation(midline21),
            ShowCreation(midline22),
        )

        self.play(
            FadeIn(reading31),
            FadeIn(reading32),
            FadeIn(reading33),
            FadeIn(reading34),
            FadeIn(reading35),
            FadeIn(reading36),
            FadeIn(reading37),
            FadeIn(reading38),
            FadeIn(reading39),
        )




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
            numbers_with_elongated_ticks = list(range(1,5)),
            numbers_to_show = list(range(1,5)),
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
        indicator_reading.set_height(0.5 * indicator.get_height())
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
                bubble_indicator_target.tex_reading.set_height(0.8*indicator.get_height())
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
        sum_indicator_reading.set_height(0.8 * sum_indicator.get_height())
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

        distance1 = get_norm(C - ls1.get_source_point())
        intensity = ls1.ambient_light.opacity_function(distance1) / indicator.opacity_for_unit_intensity
        distance2 = get_norm(C - ls2.get_source_point())
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
            self.camera.frame_shape = (0.02 * FRAME_HEIGHT, 0.02 * FRAME_WIDTH)
            self.camera.frame_center = C
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








class InscribedAngleScene(ThreeDScene):




    def construct(self):

        BASELINE_YPOS = -2.5
        OBSERVER_POINT = [0,BASELINE_YPOS,0]
        LAKE0_RADIUS = 1.5
        INDICATOR_RADIUS = 0.6
        TICK_SIZE = 0.5
        LIGHTHOUSE_HEIGHT = 0.3
        LAKE_COLOR = BLUE
        LAKE_OPACITY = 0.15
        LAKE_STROKE_WIDTH = 5.0
        LAKE_STROKE_COLOR = BLUE
        TEX_SCALE = 0.8
        DOT_COLOR = BLUE

        LIGHT_MAX_INT = 1
        LIGHT_SCALE = 5
        LIGHT_CUTOFF = 1

        self.cumulated_zoom_factor = 1


        def zoom_out_scene(factor):


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


        def shift_scene(v):
            self.play(
                self.zoomable_mobs.shift,v,
                self.unzoomable_mobs.shift,v
            )

        self.force_skipping()

        self.zoomable_mobs = VMobject()
        self.unzoomable_mobs = VMobject()


        baseline = VMobject()
        baseline.set_points_as_corners([[-8,BASELINE_YPOS,0],[8,BASELINE_YPOS,0]])
        baseline.set_stroke(width = 0) # in case it gets accidentally added to the scene
        self.zoomable_mobs.add(baseline) # prob not necessary

        self.obs_dot = Dot(OBSERVER_POINT, fill_color = DOT_COLOR)
        self.ls0_dot = Dot(OBSERVER_POINT + 2 * LAKE0_RADIUS * UP, fill_color = WHITE)
        self.unzoomable_mobs.add(self.obs_dot) #, self.ls0_dot)

        # lake
        lake0 = Circle(radius = LAKE0_RADIUS,
            stroke_width = 0,
            fill_color = LAKE_COLOR,
            fill_opacity = LAKE_OPACITY
        )
        lake0.move_to(OBSERVER_POINT + LAKE0_RADIUS * UP)
        self.zoomable_mobs.add(lake0)

        # Morty and indicator
        morty = Mortimer().scale(0.3)
        morty.next_to(OBSERVER_POINT,DOWN)
        indicator = LightIndicator(precision = 2,
            radius = INDICATOR_RADIUS,
            show_reading  = False,
            color = LIGHT_COLOR
        )
        indicator.next_to(morty,LEFT)
        self.unzoomable_mobs.add(morty, indicator)

        # first lighthouse
        original_op_func = inverse_quadratic(LIGHT_MAX_INT,AMBIENT_SCALE,LIGHT_CUTOFF)
        ls0 = LightSource(opacity_function = original_op_func, num_levels = NUM_LEVELS)
        ls0.move_source_to(OBSERVER_POINT + LAKE0_RADIUS * 2 * UP)
        self.zoomable_mobs.add(ls0, ls0.lighthouse, ls0.ambient_light)

        self.add(lake0,morty,self.obs_dot,self.ls0_dot, ls0.lighthouse)

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
            #FadeOut(self.obs_dot),
            FadeOut(self.ls0_dot)
        )

        indicator_reading = TexMobject("{1\over d^2}").scale(TEX_SCALE)
        indicator_reading.move_to(indicator)
        self.unzoomable_mobs.add(indicator_reading)

        self.play(
            FadeIn(indicator_reading)
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
            Transform(indicator_reading,new_reading)
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


        def split_light_source(i, step, show_steps = True, run_time = 1):

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
            self.add(ls2)
            self.additional_light_sources.append(ls2)

            # check if the light sources are on screen
            ls_old_loc = np.array(ls1.get_source_point())
            onscreen_old = np.all(np.abs(ls_old_loc[:2]) < 10 ** 2**step)
            onscreen_1 = np.all(np.abs(ls_new_loc1[:2][:2]) < 10 ** 2**step)
            onscreen_2 = np.all(np.abs(ls_new_loc2[:2]) < 10 ** 2**step)
            show_animation = (onscreen_old or onscreen_1 or onscreen_2)

            if show_animation:
                print("animating (", i, ",", step, ")")
                self.play(
                    ApplyMethod(ls1.move_source_to,ls_new_loc1, run_time = run_time),
                    ApplyMethod(ls2.move_source_to,ls_new_loc2, run_time = run_time),
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

            for i in range(2**n):
                split_light_source(i,
                    step = n,
                    show_steps = show_steps,
                    run_time = run_time
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

        self.revert_to_original_skipping_status()

        construction_step(0)
        indicator_wiggle()
        self.play(FadeOut(self.ls0_dot))
        zoom_out_scene(2)

        return

        construction_step(1)
        indicator_wiggle()
        self.play(FadeOut(self.ls0_dot))
        zoom_out_scene(2)

        construction_step(2)
        indicator_wiggle()
        self.play(FadeOut(self.ls0_dot))



        self.revert_to_original_skipping_status()


        ANGLE_COLOR1 = BLUE_C
        ANGLE_COLOR2 = GREEN_D

        
        for mob in self.mobjects:
            mob.fade(1.0)

        for hyp in self.hypotenuses:
            hyp.set_stroke(width = 0)
        for alt in self.altitudes:
            alt.set_stroke(width = 0)
        for leg in self.legs:
            leg.set_stroke(width = 0)
        self.inner_lake.set_stroke(width = 0)
        self.outer_lake.set_stroke(width = 0)

        self.wait()

        inner_lake_center = self.inner_lake.get_center()
        inner_lake_radius = self.lake_radius * 0.25
        inner_ls = VGroup()
        for i in range(4):
            theta = -TAU/4 + (i+0.5) * TAU/4
            point = inner_lake_center + inner_lake_radius * np.array([np.cos(theta), np.sin(theta),0])
            dot = Dot(point, color = LAKE_STROKE_COLOR, radius = 0.3)
            inner_ls.add(dot)

        self.add(inner_ls)

        inner_ls1 = inner_ls.submobjects[0]
        inner_ls2 = inner_ls.submobjects[1]
        inner_ls1_center = inner_ls1.get_center()
        inner_ls2_center = inner_ls2.get_center()

        outer_lake_center = self.outer_lake.get_center()
        outer_lake_radius = self.lake_radius * 0.5
        outer_ls = VGroup()
        for i in range(8):
            theta = -TAU/4 + (i+0.5) * TAU/8
            point = outer_lake_center + outer_lake_radius * np.array([np.cos(theta), np.sin(theta),0])
            dot = Dot(point, color = LAKE_STROKE_COLOR, radius = 0.3)
            outer_ls.add(dot)

        self.add(outer_ls)

        outer_ls1 = outer_ls.submobjects[0]
        outer_ls2 = outer_ls.submobjects[1]
        outer_ls1_center = outer_ls1.get_center()
        outer_ls2_center = outer_ls2.get_center()

        self.wait()

        arc_radius = 2.0

        line1 = Line(inner_lake_center, inner_ls1_center, color = WHITE)
        line2 = Line(inner_lake_center, inner_ls2_center, color = WHITE)


        #arc_point1 = interpolate(inner_lake_center, inner_ls1_center, 0.2)
        #arc_point2 = interpolate(inner_lake_center, inner_ls2_center, 0.2)
        #inner_angle_arc = ArcBetweenPoints(arc_point1, arc_point2, angle = TAU/4)
        inner_angle_arc = Arc(angle = TAU/4, start_angle = -TAU/8, radius = arc_radius,
            stroke_color = ANGLE_COLOR1)
        inner_angle_arc.move_arc_center_to(inner_lake_center)

        inner_label = TexMobject("\\theta", fill_color = ANGLE_COLOR1).scale(3).next_to(inner_angle_arc, LEFT, buff = -0.1)

        self.play(
            ShowCreation(line1),
            ShowCreation(line2),
        )
        self.play(
            ShowCreation(inner_angle_arc),
            FadeIn(inner_label)
        )




        self.wait()



        line3 = Line(outer_lake_center, inner_ls1_center, color = WHITE)
        line4 = Line(outer_lake_center, inner_ls2_center, color = WHITE)
        outer_angle_arc = Arc(angle = TAU/8, start_angle = -3*TAU/16, radius = arc_radius,
            stroke_color = ANGLE_COLOR2)
        outer_angle_arc.move_arc_center_to(outer_lake_center)

        outer_label = TexMobject("{\\theta \over 2}", color = ANGLE_COLOR2).scale(2.5).move_to(outer_angle_arc)
        outer_label.shift([-2,-1,0])

        self.play(
            ShowCreation(line3),
            ShowCreation(line4),
        )
        self.play(
            ShowCreation(outer_angle_arc),
            FadeIn(outer_label)
        )



        self.wait()



        line5 = Line(outer_lake_center, outer_ls1_center, color = WHITE)
        line6 = Line(outer_lake_center, outer_ls2_center, color = WHITE)

        self.play(
            ShowCreation(line5),
            ShowCreation(line6)
        )


        self.wait()

        self.play(
            FadeOut(line1),
            FadeOut(line2),
            FadeOut(line3),
            FadeOut(line4),
            FadeOut(line5),
            FadeOut(line6),
            FadeOut(inner_angle_arc),
            FadeOut(outer_angle_arc),
            FadeOut(inner_label),
            FadeOut(outer_label),
        )


        self.wait()

        inner_lines = VGroup()
        inner_arcs = VGroup()

        for i in range(-2,2):

            theta = -TAU/4 + (i+0.5)*TAU/4
            ls_point = inner_lake_center + inner_lake_radius * np.array([
                np.cos(theta), np.sin(theta),0])
            line = Line(inner_lake_center, ls_point, color = WHITE)
            inner_lines.add(line)

            arc = Arc(angle = TAU/4, start_angle = theta, radius = arc_radius,
                stroke_color = ANGLE_COLOR1)
            arc.move_arc_center_to(inner_lake_center)
            inner_arcs.add(arc)

            if i == 1:
                arc.set_stroke(width = 0)

        for line in inner_lines.submobjects:
            self.play(
                ShowCreation(line),
            )
        self.add_foreground_mobject(inner_lines)
        for arc in inner_arcs.submobjects:
            self.play(
                ShowCreation(arc)
            )

        self.wait()

        outer_lines = VGroup()
        outer_arcs = VGroup()

        for i in range(-2,2):

            theta = -TAU/4 + (i+0.5)*TAU/4

            ls_point = inner_lake_center + inner_lake_radius * np.array([
                np.cos(theta), np.sin(theta),0])
            line = Line(outer_lake_center, ls_point, color = WHITE)
            outer_lines.add(line)

            theta = -TAU/4 + (i+0.5)*TAU/8
            arc = Arc(angle = TAU/8, start_angle = theta, radius = arc_radius,
                stroke_color = ANGLE_COLOR2)
            arc.move_arc_center_to(outer_lake_center)
            outer_arcs.add(arc)

            if i == 1:
                arc.set_stroke(width = 0)

        
        for line in outer_lines.submobjects:
            self.play(
                ShowCreation(line),
            )
        self.add_foreground_mobject(outer_lines)
        for arc in outer_arcs.submobjects:
            self.play(
                ShowCreation(arc)
            )

        self.wait()

        self.play(
            FadeOut(inner_lines),
            FadeOut(inner_arcs)
        )


        outer_lines2 = VGroup()

        for i in range(-2,2):

            theta = -TAU/4 + (i+0.5)*TAU/8
            ls_point = outer_lake_center + outer_lake_radius * np.array([
                np.cos(theta), np.sin(theta),0])
            line = Line(outer_lake_center, ls_point, color = WHITE)
            outer_lines2.add(line)

        self.play(
            ShowCreation(outer_lines2),
        )

        self.wait()

        outer_lines3 = outer_lines2.copy().rotate(TAU/2, about_point = outer_lake_center)
        outer_arcs3 = outer_arcs.copy().rotate(TAU/2, about_point = outer_lake_center)

        self.play(
            ShowCreation(outer_lines3),
        )
        self.add_foreground_mobject(outer_lines3)
        for arc in outer_arcs3.submobjects:
            self.play(
                ShowCreation(arc)
            )

        last_arc = outer_arcs3.submobjects[0].copy()
        last_arc.rotate(-TAU/8, about_point = outer_lake_center)
        last_arc2 = last_arc.copy()
        last_arc2.rotate(TAU/2, about_point = outer_lake_center)

        self.play(
            ShowCreation(last_arc),
            ShowCreation(last_arc2),
        )

        self.wait()

        self.play(
            FadeOut(outer_lines2),
            FadeOut(outer_lines3),
            FadeOut(outer_arcs),
            FadeOut(outer_arcs3),
            FadeOut(last_arc),
            FadeOut(last_arc2),
        )

        self.play(
            FadeOut(inner_ls),
            FadeOut(outer_ls),
        )


        self.wait()


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

        STEP_RUN_TIME = 0.5


        #self.force_skipping()


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

        self.obs_dot = Dot(OBSERVER_POINT, fill_color = DOT_COLOR)
        self.ls0_dot = Dot(OBSERVER_POINT + 2 * LAKE0_RADIUS * UP, fill_color = WHITE)
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
        morty = Randolph(color = MAROON_D).scale(0.3)
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
        ls0 = LightSource(opacity_function = original_op_func, radius = 15.0, num_levels = 15)
        ls0.lighthouse.set_height(LIGHTHOUSE_HEIGHT)
        ls0.lighthouse.height = LIGHTHOUSE_HEIGHT
        ls0.move_source_to(OBSERVER_POINT + LAKE0_RADIUS * 2 * UP)
        self.zoomable_mobs.add(ls0, ls0.lighthouse, ls0.ambient_light)

        self.add(lake0,morty,self.obs_dot,self.ls0_dot, ls0.lighthouse)
        self.add_foreground_mobject(morty)
        self.add_foreground_mobject(self.obs_dot)
        self.add_foreground_mobject(self.ls0_dot)
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
        self.add_foreground_mobject(indicator)

        self.play(
            indicator.set_intensity,0.5
        )

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
            ShowCreation(diameter),
            Write(diameter_text),
            #FadeOut(self.obs_dot),
            FadeOut(self.ls0_dot)
        )

        indicator_reading = TexMobject("{1\over d^2}").scale(TEX_SCALE)
        indicator_reading.move_to(indicator)
        self.unzoomable_mobs.add(indicator_reading)

        self.play(
            FadeIn(indicator_reading)
        )
        self.add_foreground_mobject(indicator_reading)

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
            Transform(indicator_reading,new_reading)
        )

        self.wait()

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
            onscreen_old = np.all(np.abs(ls_old_loc[:2]) < 10 * 2**3)
            onscreen_1 = np.all(np.abs(ls_new_loc1[:2]) < 10 * 2**3)
            onscreen_2 = np.all(np.abs(ls_new_loc2[:2]) < 10 * 2**3)
            show_animation = (onscreen_old or onscreen_1 or onscreen_2)

            if show_animation or animate:
                print("animating (", i, ",", step, ")")
                self.play(
                    ApplyMethod(ls1.move_source_to,ls_new_loc1, run_time = run_time),
                    ApplyMethod(ls2.move_source_to,ls_new_loc2, run_time = run_time),
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

            # WE ALWAYS USE THIS CASE BRANCH
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



            # WE DON'T USE THIS CASE BRANCH ANYMORE
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


        construction_step(0, run_time = STEP_RUN_TIME)

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

        
        construction_step(1, run_time = STEP_RUN_TIME)
        indicator_wiggle()
        #self.play(FadeOut(self.ls0_dot))
        zoom_out_scene(2)


        construction_step(2, run_time = STEP_RUN_TIME)
        indicator_wiggle()
        self.play(FadeOut(self.ls0_dot))




        self.play(
            FadeOut(self.altitudes),
            FadeOut(self.hypotenuses),
            FadeOut(self.legs)
        )

        max_it = 10
        scale = 2**(max_it - 5)
        TEX_SCALE *= scale



        # for i in range(3,max_it + 1):
        #     construction_step(i, show_steps = False, run_time = 4.0/2**i,
        #         simultaneous_splitting = True)


        #print "starting simultaneous expansion"

        # simultaneous expansion of light sources from now on
        self.play(FadeOut(self.inner_lake))

        for n in range(3,max_it + 1):
            print("working on n = ", n, "...")
            new_lake = self.outer_lake.copy().scale(2,about_point = self.obs_dot.get_center())
            for (i,ls) in enumerate(self.light_sources_array[:2**n]):
                #print i
                lsp = ls.copy()
                self.light_sources.add(lsp)
                self.add(lsp)
                self.light_sources_array.append(lsp)

            new_lake_center = new_lake.get_center()
            new_lake_radius = 0.5 * new_lake.get_width()

            self.play(Transform(self.outer_lake,new_lake))
            shift_list = []

            for i in range(2**n):
                #print "==========="
                #print i
                theta = -TAU/4 + (i + 0.5) * TAU / 2**(n+1)
                v = np.array([np.cos(theta), np.sin(theta),0])
                pos1 = new_lake_center + new_lake_radius * v
                pos2 = new_lake_center - new_lake_radius * v
                ls1 = self.light_sources.submobjects[i]
                ls2 = self.light_sources.submobjects[i+2**n]

                ls_old_loc = np.array(ls1.get_source_point())
                onscreen_old = np.all(np.abs(ls_old_loc[:2]) < 10 * 2**2)
                onscreen_1 = np.all(np.abs(pos1[:2]) < 10 * 2**2)
                onscreen_2 = np.all(np.abs(pos2[:2]) < 10 * 2**2)
                
                if onscreen_old or onscreen_1:
                    print("anim1 for step", n, "part", i)
                    print("------------------ moving from", ls_old_loc[:2], "to", pos1[:2])
                    shift_list.append(ApplyMethod(ls1.move_source_to, pos1, run_time = STEP_RUN_TIME))
                else:
                    ls1.move_source_to(pos1)
                if onscreen_old or onscreen_2:
                    print("anim2 for step", n, "part", i)
                    print("------------------ moving from", ls_old_loc[:2], "to", pos2[:2])
                    shift_list.append(ApplyMethod(ls2.move_source_to, pos2, run_time = STEP_RUN_TIME))
                else:
                    ls2.move_source_to(pos2)
                

                #print shift_list

            self.play(*shift_list)
            print("...done")


        #self.revert_to_original_skipping_status()

        # Now create a straight number line and transform into it
        MAX_N = 7

        origin_point = self.obs_dot.get_center()

        self.number_line = NumberLine(
            x_min = -MAX_N,
            x_max = MAX_N + 1,
            color = WHITE,
            number_at_center = 0,
            stroke_width = LAKE_STROKE_WIDTH,
            stroke_color = LAKE_STROKE_COLOR,
            numbers_with_elongated_ticks = [],
            numbers_to_show = list(range(-MAX_N,MAX_N + 1)),#,2),
            unit_size = LAKE0_RADIUS * TAU/4 / 2 * scale,
            tick_frequency = 1,
            tick_size = LAKE_STROKE_WIDTH,
            number_scale_val = 3,
            line_to_number_buff = LARGE_BUFF,
            label_direction = UP,
        ).shift(origin_point - self.number_line.number_to_point(0)) # .shift(scale * 2.5 * DOWN)

        print("scale ", scale)
        print("number line at", self.number_line.get_center())
        print("should be at", origin_point, "or", OBSERVER_POINT)

        self.number_line.tick_marks.fade(1)
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
        for ls in self.light_sources_array:
            self.remove(ls)

        self.outer_lake.rotate(TAU/8)

        # open sea
        open_sea = Rectangle(
            width = 200 * scale,
            height = 100 * scale,
            stroke_width = LAKE_STROKE_WIDTH,
            stroke_color = LAKE_STROKE_COLOR,
            fill_color = LAKE_COLOR,
            fill_opacity = LAKE_OPACITY,
        ).flip().next_to(self.obs_dot.get_center(),UP,buff = 0)

        self.revert_to_original_skipping_status()

        self.play(
            ReplacementTransform(pond_sources,nl_sources),
            #FadeOut(pond_sources),
            #FadeIn(nl_sources),
            ReplacementTransform(self.outer_lake,open_sea),
            #FadeOut(self.inner_lake)
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
            indicator.move_to, origin_point + scale * UP + 2 * UP,
            indicator_reading.move_to, origin_point + scale * UP + 2 * UP,
            FadeOut(open_sea),
            FadeOut(morty),
            FadeIn(self.number_line_labels),
            FadeIn(self.number_line.tick_marks),
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

        self.wait()

        for ls in nl_sources.submobjects:
            if ls.get_source_point()[0] < 0:
                self.remove_foreground_mobject(ls.ambient_light)
                self.remove(ls.ambient_light)
            else:
                self.add_foreground_mobject(ls.ambient_light)

        for label in self.number_line_labels.submobjects:
            if label.get_center()[0] <= 0:
                self.remove(label)



        covering_rectangle = Rectangle(
            width = FRAME_X_RADIUS * scale,
            height = 2 * FRAME_Y_RADIUS * scale,
            stroke_width = 0,
            fill_color = BLACK,
            fill_opacity = 1,
        )
        covering_rectangle.next_to(ORIGIN, LEFT, buff = 0)
        #for i in range(10):
        #    self.add_foreground_mobject(nl_sources.submobjects[i])

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
        randy = Randolph(color = MAROON_D).scale(scale).move_to(2*scale*DOWN+5*scale*LEFT)
        self.play(FadeIn(randy))
        self.play(randy.change,"happy")
        self.play(randy.change,"hooray")








class WaitScene(TeacherStudentsScene):

    def construct(self):


        self.teacher_says(TexMobject("{1\over 1^2}+{1\over 3^2}+{1\over 5^2}+{1\over 7^2}+\dots = {\pi^2 \over 8}!"))

        student_q = TextMobject("What about")
        full_sum = TexMobject("{1\over 1^2}+{1\over 2^2}+{1\over 3^2}+{1\over 4^2}+\dots?")
        full_sum.next_to(student_q,RIGHT)
        student_q.add(full_sum)


        self.student_says(student_q, target_mode = "angry")


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

        BUFFER = 1.3

        Arc.__init__(self,angle,**kwargs)

        label = DecimalNumber(self.length, num_decimal_places = 0)
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



class ThumbnailScene(Scene):

    def construct(self):

        equation = TexMobject("1+{1\over 4}+{1\over 9}+{1\over 16}+{1\over 25}+\dots")
        equation.scale(1.5)
        equation.move_to(1.5 * UP)
        q_mark = TexMobject("=?", color = LIGHT_COLOR).scale(5)
        q_mark.next_to(equation, DOWN, buff = 1.5)
        #equation.move_to(2 * UP)
        #q_mark = TexMobject("={\pi^2\over 6}", color = LIGHT_COLOR).scale(3)
        #q_mark.next_to(equation, DOWN, buff = 1)

        lake_radius = 6
        lake_center = ORIGIN
        op_scale = 0.4

        lake = Circle(
            fill_color = LAKE_COLOR, 
            fill_opacity = LAKE_OPACITY, 
            radius = lake_radius,
            stroke_color = LAKE_STROKE_COLOR, 
            stroke_width = LAKE_STROKE_WIDTH,
        )
        lake.move_to(lake_center)

        for i in range(16):
            theta = -TAU/4 + (i + 0.5) * TAU/16
            pos = lake_center + lake_radius * np.array([np.cos(theta), np.sin(theta), 0])
            ls = LightSource(
                radius = 15.0, 
                num_levels = 150,
                max_opacity_ambient = 1.0,
                opacity_function = inverse_quadratic(1,op_scale,1)
            )
            ls.move_source_to(pos)
            lake.add(ls.ambient_light, ls.lighthouse)

        self.add(lake)

        self.add(equation, q_mark)

        self.wait()




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




class RightAnglesOverlay(Scene):

    def construct(self):

        BASELINE_YPOS = -2.5
        OBSERVER_POINT = [0,BASELINE_YPOS,0]
        LAKE0_RADIUS = 1.5 * 2
        INDICATOR_RADIUS = 0.6
        TICK_SIZE = 0.5
        LIGHTHOUSE_HEIGHT = 0.2
        LAKE_COLOR = BLUE
        LAKE_OPACITY = 0.15
        LAKE_STROKE_WIDTH = 5.0
        LAKE_STROKE_COLOR = BLUE
        TEX_SCALE = 0.8
        DOT_COLOR = BLUE

        RIGHT_ANGLE_SIZE = 0.3


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


        lake_center = OBSERVER_POINT + LAKE0_RADIUS * UP
        points = []
        lines = VGroup()
        for i in range(4):
            theta = -TAU/4 + (i+0.5)*TAU/4
            v = np.array([np.cos(theta), np.sin(theta), 0])
            P = lake_center + LAKE0_RADIUS * v
            points.append(P)
            lines.add(Line(lake_center, P, stroke_width = 8))

        self.play(FadeIn(lines))

        self.wait()

        for i in range(4):
            sign = right_angle(points[i-1], lake_center, points[i],RIGHT_ANGLE_SIZE)
            self.play(FadeIn(sign))
            self.play(FadeOut(sign))

        self.wait()

        self.play(FadeOut(lines))

        flash_arcs(3)
