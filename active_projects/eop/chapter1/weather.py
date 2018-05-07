from big_ol_pile_of_manim_imports import *
from active_projects.eop.reusable_imports import *


class WeatherForecast(PiCreatureScene):

    CONFIG = {
        "default_pi_creature_kwargs": {
        "color": MAROON_E,
        "flip_at_start": False,
        },
    }

    def construct(self):

        unit_rect = Rectangle(
            height = 4, width = 4
        )

        p_rain = 0.23
        p_sun = 1 - p_rain
        opacity = 0.7

        rain_rect = unit_rect.copy().stretch(p_rain, 0)
        rain_rect.align_to(unit_rect, LEFT)
        rain_rect.set_fill(color = BLUE, opacity = opacity)
        rain_rect.set_stroke(width = 0)

        sun_rect = unit_rect.copy().stretch(p_sun, 0)
        sun_rect.next_to(rain_rect, RIGHT, buff = 0)
        sun_rect.set_fill(color = YELLOW, opacity = opacity)
        sun_rect.set_stroke(width = 0)

        self.add(unit_rect, rain_rect, sun_rect)

        rain = SVGMobject(file_name = "rain").scale(0.35)
        sun = SVGMobject(file_name = "sun").scale(0.35)

        rain.flip().move_to(rain_rect)
        sun.move_to(sun_rect)

        self.add(rain, sun)

        text_scale =  0.7

        brace_rain = Brace(rain_rect, UP)
        p_rain_label = TextMobject("$p($rain$)=$").scale(text_scale)
        p_rain_decimal = DecimalNumber(p_rain).scale(text_scale)
        p_rain_decimal.next_to(p_rain_label)
        p_rain_whole_label = VGroup(p_rain_label, p_rain_decimal)
        p_rain_whole_label.next_to(brace_rain, UP)

        brace_sun = Brace(sun_rect, DOWN)
        p_sun_label = TextMobject("$p($sun$)=$").scale(text_scale)
        p_sun_decimal = DecimalNumber(p_sun).scale(text_scale)
        p_sun_decimal.next_to(p_sun_label)
        p_sun_whole_label = VGroup(p_sun_label, p_sun_decimal)
        p_sun_whole_label.next_to(brace_sun, DOWN)

        self.add(brace_rain, p_rain_whole_label, brace_sun, p_sun_whole_label)




        new_p_rain = 0.68
        new_p_sun = 1 - new_p_rain

        new_rain_rect = unit_rect.copy().stretch(new_p_rain, 0)
        new_rain_rect.align_to(unit_rect, LEFT)
        new_rain_rect.set_fill(color = BLUE, opacity = opacity)
        new_rain_rect.set_stroke(width = 0)

        new_sun_rect = unit_rect.copy().stretch(new_p_sun, 0)
        new_sun_rect.next_to(new_rain_rect, RIGHT, buff = 0)
        new_sun_rect.set_fill(color = YELLOW, opacity = opacity)
        new_sun_rect.set_stroke(width = 0)

        new_rain = SVGMobject(file_name = "rain").scale(0.35)
        new_sun = SVGMobject(file_name = "sun").scale(0.35)

        new_rain.flip().move_to(new_rain_rect)
        new_sun.move_to(new_sun_rect)

        new_brace_rain = Brace(new_rain_rect, UP)
        new_p_rain_label = TextMobject("$p($rain$)=$").scale(text_scale)
        new_p_rain_decimal = DecimalNumber(new_p_rain).scale(text_scale)
        new_p_rain_decimal.next_to(new_p_rain_label)
        new_p_rain_whole_label = VGroup(new_p_rain_label, new_p_rain_decimal)
        new_p_rain_whole_label.next_to(new_brace_rain, UP)

        
        new_brace_sun = Brace(new_sun_rect, DOWN)
        new_p_sun_label = TextMobject("$p($sun$)=$").scale(text_scale)
        new_p_sun_decimal = DecimalNumber(new_p_sun).scale(text_scale)
        new_p_sun_decimal.next_to(new_p_sun_label)
        new_p_sun_whole_label = VGroup(new_p_sun_label, new_p_sun_decimal)
        new_p_sun_whole_label.next_to(new_brace_sun, DOWN)

        def rain_update_func(alpha):
            return alpha * new_p_rain + (1 - alpha) * p_rain

        def sun_update_func(alpha):
            return 1 - rain_update_func(alpha)

        run_time = 5

        update_p_rain = ChangingDecimal(
            p_rain_decimal, rain_update_func,
            tracked_mobject = p_rain_label,
            run_time = run_time
        )
        update_p_sun = ChangingDecimal(
            p_sun_decimal, sun_update_func,
            tracked_mobject = p_sun_label,
            run_time = run_time
        )

        self.play(
            Transform(rain_rect, new_rain_rect, run_time = run_time),
            Transform(sun_rect, new_sun_rect, run_time = run_time),
            Transform(rain, new_rain, run_time = run_time),
            Transform(sun, new_sun, run_time = run_time),
            Transform(brace_rain, new_brace_rain, run_time = run_time),
            Transform(brace_sun, new_brace_sun, run_time = run_time),
            Transform(p_rain_label, new_p_rain_label, run_time = run_time),
            Transform(p_sun_label, new_p_sun_label, run_time = run_time),
            update_p_rain,
            update_p_sun
        )











