#!/usr/bin/env python

from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
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
INDICATOR_STROKE_COLOR = LIGHT_COLOR
INDICATOR_TEXT_COLOR = LIGHT_COLOR
OPACITY_FOR_UNIT_INTENSITY = 0.2



class LightCone(VGroup):
    CONFIG = {
        "angle" : TAU/8,
        "radius" : 5,
        "opacity_function" : lambda r : 1./max(r, 0.01),
        "num_sectors" : 10,
        "color": LIGHT_COLOR,
    }

    def generate_points(self):
        radii = np.linspace(0, self.radius, self.num_sectors+1)
        sectors = [
            AnnularSector(
                angle = self.angle,
                inner_radius = r1,
                outer_radius = r2,
                stroke_width = 0,
                stroke_color = self.color,
                fill_color = self.color,
                fill_opacity = self.opacity_function(r1),
            )
            for r1, r2 in zip(radii, radii[1:])
        ]
        self.add(*sectors)


class Candle(VGroup):
    CONFIG = {
        "radius" : 5,
        "opacity_function" : lambda r : 1./max(r, 0.01),
        "num_sectors" : 10,
        "color": LIGHT_COLOR,
    }

    def generate_points(self):
        radii = np.linspace(0, self.radius, self.num_sectors+1)
        annuli = [
            Annulus(
                inner_radius = r1,
                outer_radius = r2,
                stroke_width = 0,
                stroke_color = self.color,
                fill_color = self.color,
                fill_opacity = self.opacity_function(r1),
            )
            for r1, r2 in zip(radii, radii[1:])
        ]
        self.add(*annuli)



class SwitchOn(LaggedStart):
    CONFIG = {
        "lag_ratio": 0.2,
        "run_time": 3
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
        "intensity": 1,
        "opacity_for_unit_intensity": 1
    }

    def generate_points(self):
        self.background = Circle(color=BLACK, radius = self.radius)
        self.background.set_fill(opacity=1)
        self.foreground = Circle(color=self.color, radius = self.radius)
        self.foreground.set_stroke(color=INDICATOR_STROKE_COLOR,width=INDICATOR_STROKE_WIDTH)

        self.add(self.background, self.foreground)
        self.reading = DecimalNumber(self.intensity)
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

        morty = self.get_primary_pi_creature()
        morty.scale(0.7).to_corner(DOWN+RIGHT)

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



class FirstLightHouseScene(Scene):

    def construct(self):
        self.show_lighthouses_on_number_line()



    def show_lighthouses_on_number_line(self):

        self.number_line = NumberLine(
            x_min = 0,
            color = WHITE,
            number_at_center = 1,
            stroke_width = 1,
            numbers_with_elongated_ticks = [0,1,2,3],
            numbers_to_show = np.arange(0,5),
            unit_size = 2,
            tick_frequency = 0.2,
            line_to_number_buff = LARGE_BUFF
        )

        self.number_line_labels = self.number_line.get_number_mobjects()
        self.add(self.number_line,self.number_line_labels)
        self.wait()

        light_indicator = LightIndicator(radius = INDICATOR_RADIUS,
            opacity_for_unit_intensity = OPACITY_FOR_UNIT_INTENSITY, color = LIGHT_COLOR)

        origin_point = self.number_line.number_to_point(0)
        light_indicator.move_to(origin_point)
        self.add_foreground_mobject(light_indicator)

        lighthouses = []
        lighthouse_pos = []
        light_cones = []

        num_cones = 2

        for i in range(1,num_cones+1):
            lighthouse = LightHouse()
            point = self.number_line.number_to_point(i)
            light_cone = LightCone(angle = TAU/8,
            #light_cone = Candle(
                opacity_function = inverse_power_law(1,1,2),
                num_sectors = 10,
                radius = 10)
            light_cone.move_to(point)
            lighthouse.next_to(point,DOWN,0)
            lighthouses.append(lighthouse)
            light_cones.append(light_cone)
            lighthouse_pos.append(point)


        for lh in lighthouses:
            self.add_foreground_mobject(lh)

        light_indicator.set_intensity(0)

        intensities = np.cumsum(np.array([1./n**2 for n in range(1,num_cones+1)]))
        opacities = intensities * light_indicator.opacity_for_unit_intensity

        self.remove_foreground_mobjects(light_indicator)


        for (i,lc) in zip(range(num_cones),light_cones):
            self.play(
                SwitchOn(lc),
                #Animation(light_indicator),
                ChangeDecimalToValue(light_indicator.reading,intensities[i]),
                ApplyMethod(light_indicator.foreground.set_fill,None,opacities[i])
                #UpdateLightIndicator(light_indicator, intensities[i])
            )


            

        self.wait()

        









