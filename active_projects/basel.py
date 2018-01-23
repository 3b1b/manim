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
from topics.combinatorics import *
from scene import Scene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *


from mobject.vectorized_mobject import *

## To watch one of these scenes, run the following:
## python extract_scene.py -p file_name <SceneName>

inverse_power_law = lambda maxint,cutoff,exponent: \
    (lambda r: maxint * (cutoff/(r+cutoff))**exponent)
inverse_quadratic = lambda maxint,cutoff: inverse_power_law(maxint,cutoff,2)

LIGHT_COLOR = YELLOW
INDICATOR_RADIUS = 0.7
INDICATOR_STROKE_WIDTH = 1
INDICATOR_STROKE_COLOR = WHITE
INDICATOR_TEXT_COLOR = WHITE
INDICATOR_UPDATE_TIME = 0.2
FAST_INDICATOR_UPDATE_TIME = 0.1
OPACITY_FOR_UNIT_INTENSITY = 0.2
SWITCH_ON_RUN_TIME = 2.5
FAST_SWITCH_ON_RUN_TIME = 0.1
LIGHT_CONE_NUM_SECTORS = 30
NUM_CONES = 50 # in first lighthouse scene
NUM_VISIBLE_CONES = 5 # ibidem
ARC_TIP_LENGTH = 0.2


def show_line_length(line):
    v = line.points[1] - line.points[0]
    print v[0]**2 + v[1]**2


class AngleUpdater(ContinualAnimation):
    def __init__(self, angle_arc, lc, **kwargs):
        self.angle_arc = angle_arc
        self.source_point = angle_arc.get_arc_center()
        self.lc = lc
        #self.angle_decimal = angle_decimal
        ContinualAnimation.__init__(self, self.angle_arc, **kwargs)

    def update_mobject(self, dt):
    # angle arc
        new_arc = self.angle_arc.copy().set_bound_angles(
            start = self.lc.start_angle,
            stop = self.lc.stop_angle()
         )
        new_arc.generate_points()
        new_arc.move_arc_center_to(self.source_point)
        self.angle_arc.points = new_arc.points
        self.angle_arc.add_tip(tip_length = ARC_TIP_LENGTH, at_start = True, at_end = True)




class LightScreen(VMobject):
    # A light screen is composed of a VMobject and a light cone.
    # It has knowledge of the light source point.
    # As the screen changes, it calculates the viewing angle from
    # the source and updates the light cone.

    def __init__(self, light_source = ORIGIN, screen = None, light_cone = None):
        Mobject.__init__(self)
        self.light_cone = light_cone
        self.light_source = light_source
        self.screen = screen
        self.light_cone.move_source_to(self.light_source)
        self.shadow = VMobject(fill_color = BLACK, stroke_width = 0, fill_opacity = 1.0)
        self.add(self.light_cone, self.screen, self.shadow)
        self.update_shadow(self.shadow)

    def update_light_cone(self,lc):
        lower_angle, upper_angle = self.viewing_angles()
        self.light_cone.update_opening(start_angle = lower_angle,
            stop_angle = upper_angle)
        return self

    def viewing_angle_of_point(self,point):
        distance_vector = point - self.light_source
        angle = angle_of_vector(distance_vector)
        return angle

    def viewing_angles(self):
        all_points = []

        for submob in self.family_members_with_points():
            all_points.extend(submob.get_anchors())

        viewing_angles = np.array(map(self.viewing_angle_of_point, self.screen.get_anchors()))
           
        if len(viewing_angles) == 0:
            lower_angle = upper_angle = 0
        else:
            lower_angle = np.min(viewing_angles)
            upper_angle = np.max(viewing_angles)

        return lower_angle, upper_angle

    def update_shadow(self,sh):
        self.shadow.points = self.screen.points
        ray1 = self.screen.points[0] - self.light_source
        ray2 = self.screen.points[-1] - self.light_source
        ray1 = ray1/np.linalg.norm(ray1) * 100
        ray1 = rotate_vector(ray1,-TAU/16)
        ray2 = ray2/np.linalg.norm(ray2) * 100
        ray2 = rotate_vector(ray2,TAU/16)
        outpoint1 = self.screen.points[0] + ray1
        outpoint2 = self.screen.points[-1] + ray2
        self.shadow.add_control_points([outpoint2,outpoint1,self.screen.points[0]])
        self.shadow.mark_paths_closed = True


class LightCone(VGroup):
    CONFIG = {
        "start_angle": 0,
        "angle" : TAU/8,
        "radius" : 10,
        "brightness" : 1,
        "opacity_function" : lambda r : 1./max(r, 0.01),
        "num_sectors" : 10,
        "color": LIGHT_COLOR,
    }

    def generate_points(self):
        radii = np.linspace(0, self.radius, self.num_sectors+1)
        sectors = [
            AnnularSector(
                start_angle = self.start_angle,
                angle = self.angle,
                inner_radius = r1,
                outer_radius = r2,
                stroke_width = 0,
                stroke_color = self.color,
                fill_color = self.color,
                fill_opacity = self.brightness * self.opacity_function(r1),
            )
            for r1, r2 in zip(radii, radii[1:])
        ]
        self.add(*sectors)

    def get_source_point(self):
        if len(self.submobjects) == 0:
            return None
        source = self.submobjects[0].get_arc_center()
        return source

    def move_source_to(self,point):
        if len(self.submobjects) == 0:
            return
        source = self.submobjects[0].get_arc_center()
        self.shift(point - source)
        
    def update_opening(self, start_angle, stop_angle):
        self.start_angle = start_angle
        self.angle = stop_angle - start_angle
        source_point = self.get_source_point()
        for submob in self.submobjects:
            if type(submob) == AnnularSector:

                submob.start_angle = self.start_angle
                submob.angle = self.angle
                submob.generate_points()
                submob.shift(source_point - submob.get_arc_center())

    def set_brightness(self,new_brightness):
        self.brightness = new_brightness
        radii = np.linspace(0, self.radius, self.num_sectors+1)
        for (r1,sector) in zip(radii,self.submobjects):
            sector.set_fill(opacity =  self.brightness * self.opacity_function(r1))

    def stop_angle(self):
        return self.start_angle + self.angle







class Candle(VGroup):
    CONFIG = {
        "radius" : 5,
        "brightness" : 1.0,
        "opacity_function" : lambda r : 1./max(r, 0.01),
        "num_annuli" : 10,
        "color": LIGHT_COLOR,
    }

    def generate_points(self):
        radii = np.linspace(0, self.radius, self.num_annuli+1)
        annuli = [
            Annulus(
                inner_radius = r1,
                outer_radius = r2,
                stroke_width = 0,
                stroke_color = self.color,
                fill_color = self.color,
                fill_opacity = self.brightness * self.opacity_function(r1),
            )
            for r1, r2 in zip(radii, radii[1:])
        ]
        self.add(*annuli)

    def get_source_point(self):
        if len(self.submobjects) == 0:
            return None
        source = self.submobjects[0].get_center()
        return source

    def move_source_to(self,point):
        if len(self.submobjects) == 0:
            return
        source = self.submobjects[0].get_center()
        self.shift(point - source)

    def set_brightness(self,new_brightness):
        self.brightness = new_brightness
        radii = np.linspace(0, self.radius, self.num_annuli+1)
        for (r1,annulus) in zip(radii,self.submobjects):
            annulus.set_fill(opacity =  self.brightness * self.opacity_function(r1))




class SwitchOn(LaggedStart):
    CONFIG = {
        "lag_ratio": 0.2,
        "run_time": SWITCH_ON_RUN_TIME
    }

    def __init__(self, light, **kwargs):
        if not isinstance(light,LightCone) and not isinstance(light,Candle):
            raise Exception("Only LightCones and Candles can be switched on")
        LaggedStart.__init__(self,
            FadeIn, light, **kwargs)

class LightHouse(SVGMobject):
    CONFIG = {
        "file_name" : "lighthouse",
        "height" : 0.5
    }

class LightIndicator(Mobject):
    CONFIG = {
        "radius": 0.5,
        "intensity": 0,
        "opacity_for_unit_intensity": 1
    }

    def generate_points(self):
        self.background = Circle(color=BLACK, radius = self.radius)
        self.background.set_fill(opacity=1)
        self.foreground = Circle(color=self.color, radius = self.radius)
        self.foreground.set_stroke(color=INDICATOR_STROKE_COLOR,width=INDICATOR_STROKE_WIDTH)

        self.add(self.background, self.foreground)
        self.reading = DecimalNumber(self.intensity,num_decimal_points = 3)
        self.reading.set_fill(color=INDICATOR_TEXT_COLOR)
        self.reading.move_to(self.get_center())
        self.add(self.reading)

    def set_intensity(self, new_int):
        self.intensity = new_int
        new_opacity = min(1, new_int * self.opacity_for_unit_intensity)
        self.foreground.set_fill(opacity=new_opacity)
        ChangeDecimalToValue(self.reading, new_int).update(1)
        


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


class IntroScene(PiCreatureScene):

    CONFIG = {
        "rect_height" : 0.2,
        "duration" : 1.0,
        "eq_spacing" : 3 * MED_LARGE_BUFF
    }

    def construct(self):

        randy = self.get_primary_pi_creature()
        randy.scale(0.7).to_corner(DOWN+RIGHT)

        self.force_skipping()

        self.build_up_euler_sum()
        self.build_up_sum_on_number_line()
        self.show_pi_answer()
        self.other_pi_formulas()

        self.revert_to_original_skipping_status()
        

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

        q_circle = Circle(color=WHITE,radius=0.8)
        q_mark = TexMobject("?")
        q_mark.next_to(q_circle)

        thought = Group(q_circle, q_mark)
        q_mark.height *= 2
        self.pi_creature_thinks(thought,target_mode = "confused",
            bubble_kwargs = { "height" : 1.5, "width" : 2 })

        self.wait()



class FirstLightHouseScene(PiCreatureScene):

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

        lighthouses = []
        lighthouse_pos = []
        light_cones = []


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
            lighthouse = LightHouse()
            point = self.number_line.number_to_point(i)
            light_cone = Candle(
                opacity_function = inverse_quadratic(1,1),
                num_annuli = LIGHT_CONE_NUM_SECTORS,
                radius = 12)
            
            light_cone.move_source_to(point)
            lighthouse.next_to(point,DOWN,0)
            lighthouses.append(lighthouse)
            light_cones.append(light_cone)
            lighthouse_pos.append(point)


        for lh in lighthouses:
            self.add_foreground_mobject(lh)

        light_indicator.set_intensity(0)

        intensities = np.cumsum(np.array([1./n**2 for n in range(1,NUM_CONES+1)]))
        opacities = intensities * light_indicator.opacity_for_unit_intensity

        self.remove_foreground_mobjects(light_indicator)


        # slowly switch on visible light cones and increment indicator
        for (i,lc) in zip(range(NUM_VISIBLE_CONES),light_cones[:NUM_VISIBLE_CONES]):
            indicator_start_time = 0.4 * (i+1) * SWITCH_ON_RUN_TIME/lc.radius * self.number_line.unit_size
            indicator_stop_time = indicator_start_time + INDICATOR_UPDATE_TIME
            indicator_rate_func = squish_rate_func(
                smooth,indicator_start_time,indicator_stop_time)
            self.play(
                SwitchOn(lc),
                FadeIn(euler_sum_above[2*i], run_time = SWITCH_ON_RUN_TIME,
                    rate_func = indicator_rate_func),
                FadeIn(euler_sum_above[2*i - 1], run_time = SWITCH_ON_RUN_TIME,
                    rate_func = indicator_rate_func),
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
        for (i,lc) in zip(range(NUM_VISIBLE_CONES,NUM_CONES),light_cones[NUM_VISIBLE_CONES:NUM_CONES]):
            indicator_start_time = 0.5 * (i+1) * FAST_SWITCH_ON_RUN_TIME/lc.radius * self.number_line.unit_size
            indicator_stop_time = indicator_start_time + FAST_INDICATOR_UPDATE_TIME
            indicator_rate_func = squish_rate_func(#smooth, 0.8, 0.9)
                smooth,indicator_start_time,indicator_stop_time)
            self.play(
                SwitchOn(lc, run_time = FAST_SWITCH_ON_RUN_TIME),
                ChangeDecimalToValue(light_indicator.reading,intensities[i],
                    rate_func = indicator_rate_func, run_time = FAST_SWITCH_ON_RUN_TIME),
                ApplyMethod(light_indicator.foreground.set_fill,None,opacities[i])
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

        

class SingleLightHouseScene(PiCreatureScene):

    def construct(self):

        self.create_light_source_and_creature()



    def create_light_source_and_creature(self):

        SCREEN_SIZE = 3.0
        DISTANCE_FROM_LIGHTHOUSE = 10.0
        source_point = [-DISTANCE_FROM_LIGHTHOUSE/2,0,0]
        observer_point = [DISTANCE_FROM_LIGHTHOUSE/2,0,0]

        lighthouse = LightHouse()
        candle = Candle(
            opacity_function = inverse_quadratic(1,1),
            num_annuli = LIGHT_CONE_NUM_SECTORS,
            radius = 10,
            brightness = 1,
        )
        lighthouse.scale(2).next_to(source_point, DOWN, buff = 0)
        candle.move_to(source_point)
        morty = self.get_primary_pi_creature()
        morty.scale(0.5)
        morty.move_to(observer_point)
        self.add(lighthouse)
        self.play(
            SwitchOn(candle)
        )

        light_cone = LightCone(
            opacity_function = inverse_quadratic(1,1),
            num_sectors = LIGHT_CONE_NUM_SECTORS,
            radius = 10,
            brightness = 5,
        )
        light_cone.move_source_to(source_point)
        screen = Line([0,-1,0],[0,1,0])
        show_line_length(screen)

        screen.rotate_in_place(-TAU/6)
        show_line_length(screen)

        screen.next_to(morty, LEFT, buff = 1)
        
        light_screen = LightScreen(light_source = source_point,
            screen = screen, light_cone = light_cone)
        light_screen.screen.color = WHITE
        light_screen.screen.fill_opacity = 1
        light_screen.update_light_cone(light_cone)
        self.play(
            FadeIn(light_screen, run_time = 2),
        # dim the light that misses the screen
            ApplyMethod(candle.set_brightness,0.3),
            ApplyMethod(light_screen.update_shadow,light_screen.shadow),
            FadeIn(light_cone),
        )

        lc_updater = lambda lc: light_screen.update_light_cone(lc)
        sh_updater = lambda sh: light_screen.update_shadow(sh)

        ca1 = ContinualUpdateFromFunc(light_screen.light_cone,
           lc_updater)
        ca2 = ContinualUpdateFromFunc(light_screen.shadow,
           sh_updater)

        self.add(ca1, ca2)
        self.add_foreground_mobject(morty)

        pointing_screen_at_source = ApplyMethod(screen.rotate_in_place,TAU/6)
        self.play(pointing_screen_at_source)

        arc_angle = light_cone.angle
        # draw arc arrows to show the opening angle
        angle_arc = Arc(radius = 5, start_angle = light_cone.start_angle,
            angle = light_cone.angle, tip_length = ARC_TIP_LENGTH)
        #angle_arc.add_tip(at_start = True, at_end = True)
        angle_arc.move_arc_center_to(source_point)
        
        self.add(angle_arc)

        angle_indicator = DecimalNumber(arc_angle/TAU*360,
            num_decimal_points = 0,
            unit = "^\\circ")
        angle_indicator.next_to(angle_arc,RIGHT)
        self.add_foreground_mobject(angle_indicator)

        angle_update_func = lambda x: light_cone.angle/TAU*360
        ca3 = ContinualChangingDecimal(angle_indicator,angle_update_func)
        self.add(ca3)

        #ca4 = ContinualUpdateFromFunc(angle_arc,update_angle_arc)
        ca4 = AngleUpdater(angle_arc, light_screen.light_cone)
        self.add(ca4)

        rotating_screen = ApplyMethod(light_screen.screen.rotate_in_place, TAU/6, run_time=3, rate_func = wiggle)
        self.play(rotating_screen)
        
        #rotating_screen_back = ApplyMethod(light_screen.screen.rotate_in_place, -TAU/6) #, run_time=3, rate_func = wiggle)
        #self.play(rotating_screen_back)

        self.wait()



        # morph into Earth scene

        globe = Circle(radius = 3)
        globe.move_to([2,0,0])
        sun_position = [-100,0,0]
        self.play(
            ApplyMethod(lighthouse.move_to,sun_position),
            ApplyMethod(candle.move_to,sun_position),
            ApplyMethod(light_cone.move_source_to,sun_position),
            FadeOut(angle_arc),
            FadeOut(angle_indicator),
            FadeIn(globe),
            ApplyMethod(light_screen.move_to,[0,0,0]),
            ApplyMethod(morty.move_to,[1,0,0])

        )































