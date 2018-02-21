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
        self.angle_arc.add_tip(tip_length = ARC_TIP_LENGTH,
            at_start = True, at_end = True)





class LightIndicator(Mobject):
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
        self.reading = DecimalNumber(self.intensity,num_decimal_points = self.precision)
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
        distance = np.linalg.norm(self.get_measurement_point() - 
            self.light_source.get_source_point())
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
        "duration" : 1.0,
        "eq_spacing" : 3 * MED_LARGE_BUFF
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
                num_decimal_points = 2)
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
                        num_decimal_points = 6,
                        show_ellipsis = True,
                        position_update_func = lambda m: m.next_to(equals_sign, RIGHT)
                    )
                )
                
            self.wait()

        self.q_marks = TextMobject("???").highlight(LIGHT_COLOR)
        self.q_marks.move_to(self.partial_sum_decimal)

        self.play(
            FadeIn(self.euler_sum[-3], run_time = self.duration), # +
            FadeIn(self.euler_sum[-2], run_time = self.duration), # ...
            ReplacementTransform(self.partial_sum_decimal, self.q_marks)
        )



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
        )

        self.number_line_labels = self.number_line.get_number_mobjects()
        self.add(self.number_line,self.number_line_labels)
        self.wait()

        # create slabs for series terms

        max_n = 10

        terms = [0] + [1./(n**2) for n in range(1, max_n + 1)]
        series_terms = np.cumsum(terms)
        lines = VGroup()
        self.rects = VGroup()
        slab_colors = [YELLOW, BLUE] * (max_n / 2)

        for t1, t2, color in zip(series_terms, series_terms[1:], slab_colors):
            line = Line(*map(self.number_line.number_to_point, [t1, t2]))
            rect = Rectangle()
            rect.stroke_width = 0
            rect.fill_opacity = 1
            rect.highlight(color)
            rect.stretch_to_fit_height(
                self.rect_height,
            )
            rect.stretch_to_fit_width(line.get_width())
            rect.move_to(line)

            self.rects.add(rect)
            lines.add(line)

        #self.rects.radial_gradient_highlight(ORIGIN, 5, YELLOW, BLUE)
        
        for i in range(5):
            self.play(
                GrowFromPoint(self.rects[i], self.euler_sum[2*i].get_center(),
                    run_time = self.duration)
            )

        for i in range(5, max_n):
            self.play(
                GrowFromPoint(self.rects[i], self.euler_sum[10].get_center(),
                    run_time = self.duration)
            )


    def show_pi_answer(self):

        self.pi_answer = TexMobject("{\\pi^2 \\over 6}").highlight(YELLOW)
        self.pi_answer.move_to(self.partial_sum_decimal)
        self.pi_answer.next_to(self.euler_sum[-1], RIGHT,
            submobject_to_align = self.pi_answer[-2])
        self.play(ReplacementTransform(self.q_marks, self.pi_answer))


    def other_pi_formulas(self):

        self.play(
            FadeOut(self.rects),
            FadeOut(self.number_line_labels),
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
            numbers_with_elongated_ticks = range(1,5),
            numbers_to_show = range(1,5),
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

        self.play(
            randy.change, "wave_2",
            ShowCreation(bubble),
            FadeIn(light_indicator)
        )

        light_sources = []


        euler_sum_above = TexMobject("1", "+", "{1\over 4}", 
            "+", "{1\over 9}", "+", "{1\over 16}", "+", "{1\over 25}", "+", "{1\over 36}")

        for (i,term) in zip(range(len(euler_sum_above)),euler_sum_above):
            #horizontal alignment with tick marks
            term.next_to(self.number_line.number_to_point(0.5*i+1),UP,buff = 2)
            # vertical alignment with light indicator
            old_y = term.get_center()[1]
            new_y = light_indicator.get_center()[1]
            term.shift([0,new_y - old_y,0])
            


        for i in range(1,NUM_CONES+1):
            light_source = LightSource(
                opacity_function = inverse_quadratic(1,2,1),
                num_levels = NUM_LEVELS,
                radius = 12.0,
            )
            point = self.number_line.number_to_point(i)
            light_source.move_source_to(point)
            light_sources.append(light_source)


        for ls in light_sources:
            self.add_foreground_mobject(ls.lighthouse)

        light_indicator.set_intensity(0)

        intensities = np.cumsum(np.array([1./n**2 for n in range(1,NUM_CONES+1)]))
        opacities = intensities * light_indicator.opacity_for_unit_intensity

        self.remove_foreground_mobjects(light_indicator)


        # slowly switch on visible light cones and increment indicator
        for (i,light_source) in zip(range(NUM_VISIBLE_CONES),light_sources[:NUM_VISIBLE_CONES]):
            indicator_start_time = 0.4 * (i+1) * SWITCH_ON_RUN_TIME/light_source.radius * self.number_line.unit_size
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
                ApplyMethod(light_indicator.foreground.set_fill,None,opacities[i])
            )

            if i == 0:
                # move a copy out of the thought bubble for comparison
                light_indicator_copy = light_indicator.copy()
                old_y = light_indicator_copy.get_center()[1]
                new_y = self.number_line.get_center()[1]
                self.play(
                    light_indicator_copy.shift,[0, new_y - old_y,0]
                )

        # quickly switch on off-screen light cones and increment indicator
        for (i,light_source) in zip(range(NUM_VISIBLE_CONES,NUM_CONES),light_sources[NUM_VISIBLE_CONES:NUM_CONES]):
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
        self.morph_lighthouse_into_sun()


    def setup_elements(self):

        self.remove(self.get_primary_pi_creature())

        SCREEN_SIZE = 3.0
        DISTANCE_FROM_LIGHTHOUSE = 10.0
        source_point = [-DISTANCE_FROM_LIGHTHOUSE/2,0,0]
        observer_point = [DISTANCE_FROM_LIGHTHOUSE/2,0,0]

        # Light source

        self.light_source = LightSource(
            opacity_function = inverse_quadratic(1,2,1),
            num_levels = NUM_LEVELS,
            radius = 10,
            max_opacity_ambient = AMBIENT_FULL
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
            width = 0.1,
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

        self.light_source.set_max_opacity_spotlight(0.001)
        self.add(self.light_source.spotlight)

        self.screen_tracker = ScreenTracker(self.light_source)
        self.add(self.screen_tracker)

        self.wait()


        # just calling .dim_ambient via ApplyMethod does not work, why?
        dimmed_ambient_light = self.light_source.ambient_light.deepcopy()
        dimmed_ambient_light.dimming(AMBIENT_DIMMED)

        self.play(
            Transform(self.light_source.ambient_light,dimmed_ambient_light),
            self.light_source.set_max_opacity_spotlight,1.0,
            FadeIn(self.light_source.shadow)
        )

        self.add_foreground_mobject(morty)




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
            num_decimal_points = 0,
            unit = "^\\circ")
        self.angle_indicator.next_to(self.angle_arc,RIGHT)

        angle_update_func = lambda x: self.light_source.spotlight.opening_angle() / DEGREES
        ca1 = ContinualChangingDecimal(self.angle_indicator,angle_update_func)
        self.add(ca1)

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


    def morph_lighthouse_into_sun(self):



        sun_position = [-100,0,0]


        self.play(
            FadeOut(self.angle_arc),
            FadeOut(self.angle_indicator)
        )

        self.sun = self.light_source.deepcopy()

        #self.sun.num_levels = NUM_LEVELS,
        #self.sun.set_radius(150)
        #self.sun.set_max_opacity_ambient(AMBIENT_FULL)
        


        self.sun.spotlight.change_opacity_function(lambda r: 0.5)
        self.sun.set_radius(150)
        self.sun.move_source_to(sun_position)

 #       self.sun.update()

   #     self.add(self.sun)
        # temporarily remove the screen tracker while we move the source
        #self.remove(self.screen_tracker)

        #print self.sun.spotlight.get_source_point()

        self.play(
             #self.light_source.spotlight.move_source_to,sun_position,
             Transform(self.light_source,self.sun)
        )

        #self.add(ScreenTracker(self.sun))

        self.wait()




 














class EarthScene(Scene):

    def construct(self):

        SCREEN_THICKNESS = 10

        self.screen_height = 2.0
        self.brightness_rect_height = 1.0

        # screen
        self.screen = VMobject(stroke_color = WHITE, stroke_width = SCREEN_THICKNESS)
        self.screen.set_points_as_corners([
            [3,-self.screen_height/2,0],
            [3,self.screen_height/2,0]
        ])

        # Earth

        earth_center_x = 2
        earth_center = [earth_center_x,0,0]
        earth_radius = 3
        earth = Circle(radius = earth_radius)
        earth.move_to(earth_center)
        #self.remove(self.screen_tracker)

        theta0 = 70 * DEGREES
        dtheta = 10 * DEGREES
        theta1 = theta0 + dtheta
        theta = (theta0 + theta1)/2

        earth.add(self.screen)

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

        self.play(FadeIn(earth))
        self.bring_to_back(earth)

        # move screen onto Earth
        screen_on_earth = self.screen.deepcopy()
        screen_on_earth.rotate(-theta)
        screen_on_earth.scale(0.3)
        screen_on_earth.move_to(np.array([
            earth_center_x - earth_radius * np.cos(theta),
            earth_radius * np.sin(theta),
            0]))

        polar_morty = morty.copy().scale(0.5).next_to(screen_on_earth,DOWN,buff = 0.5)

        self.play(
            Transform(self.screen, screen_on_earth),
            Transform(morty,polar_morty)
        )

        self.wait()


        tropical_morty = polar_morty.copy()
        tropical_morty.move_to(np.array([0,0,0]))
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

        LIGHT_MAX_INT = 1
        LIGHT_SCALE = 5
        LIGHT_CUTOFF = 1

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
        original_op_func = inverse_quadratic(LIGHT_MAX_INT,LIGHT_SCALE,LIGHT_CUTOFF)
        ls0 = LightSource(opacity_function = original_op_func)
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

        indicator_reading = TexMobject("{1\over d^2}").scale(TEX_SCALE)
        indicator_reading.move_to(indicator)

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
                return position.scale_about_point(OBSERVER_POINT,0.5)
            else:
                return position


        def split_light_source(i, step, show_steps = True, run_time = 1, scale_down = True):

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

            if scale_down:
               #  print "scaling down"
               # #new_of = lambda x: original_op_func(x/0.5**step)
               # #new_of = inverse_quadratic(LIGHT_MAX_INT, LIGHT_SCALE * 10**(step+1), LIGHT_CUTOFF)
               #  print "=============="
               #  for t in np.arange(0.0,5.0,1.0):
               #      print ls1.ambient_light.opacity_function(t)

               #  print "=============="

                new_of = lambda x: np.sin(10*x)
                ls1.ambient_light.change_opacity_function(lambda x: np.sin(100*x))
                # for t in np.arange(0.0,5.0,1.0):
                #     print ls1.ambient_light.opacity_function(t)

                ls1.spotlight.change_opacity_function(new_of)

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
                    scale_down = scale_down
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
            construction_step(i, scale_down = True)



        self.play(
            FadeOut(self.altitudes),
            FadeOut(self.hypotenuses),
            FadeOut(self.legs)
            )

        for i in range(3,5):
            construction_step(i, scale_down = False, show_steps = False, run_time = 1.0/2**i,
                simultaneous_splitting = True)




        # Now create a straight number line and transform into it
        MAX_N = 17

        self.number_line = NumberLine(
            x_min = -MAX_N,
            x_max = MAX_N + 1,
            color = WHITE,
            number_at_center = 0,
            stroke_width = LAKE_STROKE_WIDTH,
            stroke_color = LAKE_STROKE_COLOR,
            #numbers_with_elongated_ticks = range(-MAX_N,MAX_N + 1),
            numbers_to_show = range(-MAX_N,MAX_N + 1,2),
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
            ReplacementTransform(pond_sources,nl_sources),
            ReplacementTransform(self.outer_lake,open_sea),
            FadeOut(self.inner_lake)
        )
        self.play(FadeIn(self.number_line))


        self.wait()

        v = 5*UP
        self.play(
            nl_sources.shift,v,
            morty.shift,v,
            self.number_line.shift,v,
            indicator.shift,v,
            indicator_reading.shift,v,
            open_sea.shift,v,
        )
        self.number_line_labels.shift(v)

        origin_point = self.number_line.number_to_point(0)
        self.remove(obs_dot)
        self.play(
            indicator.move_to, origin_point + UP,
            indicator_reading.move_to, origin_point + UP,
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

        two_sided_sum.scale(0.8)
        
        for (i,submob) in zip(range(nb_symbols),two_sided_sum.submobjects):
            submob.next_to(self.number_line.number_to_point(i - 13),DOWN, buff = 2)
            if (i == 0 or i % 2 == 1 or i == nb_symbols - 1): # non-fractions
                submob.shift(0.2 * DOWN)

        self.play(Write(two_sided_sum))

        covering_rectangle = Rectangle(
            width = SPACE_WIDTH,
            height = 2 * SPACE_HEIGHT,
            stroke_width = 0,
            fill_color = BLACK,
            fill_opacity = 1,
        )
        covering_rectangle.next_to(ORIGIN,LEFT,buff = 0)
        for i in range(10):
            self.add_foreground_mobject(self.light_sources_array[i])

        self.add_foreground_mobject(indicator)
        self.add_foreground_mobject(indicator.reading)

        half_indicator = indicator.copy()
        half_indicator.show_reading = False
        half_indicator.set_intensity(indicator.intensity / 2)
        half_indicator_reading = TexMobject("{\pi^2 \over 8}").scale(TEX_SCALE)
        half_indicator_reading.move_to(half_indicator)
        half_indicator.remove(indicator_reading)
        half_indicator.add(half_indicator_reading)

        half_indicator_copy = half_indicator.deepcopy()
        half_indicator_reading_copy = half_indicator_reading.deepcopy()

        self.play(
            FadeIn(covering_rectangle),
            FadeIn(half_indicator),
        )

        p = 2*LEFT
        self.play(
            half_indicator_copy.move_to,p,
            half_indicator_reading_copy.move_to,p
        )



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










