import numpy as np
import itertools as it

from helpers import *

from mobject.tex_mobject import TexMobject, TextMobject, Brace
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from topics.three_dimensions import Stars

from animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import TurnInsideOut, Vibrate
from topics.geometry import *
from topics.characters import *
from topics.functions import ParametricFunction, FunctionGraph
from topics.number_line import *
from mobject.region import  Region, region_from_polygon_vertices
from scene import Scene


class PhysicalIntuition(Scene):
    def construct(self):
        n_terms = 4
        def func((x, y, ignore)):
            z = complex(x, y)                                    
            if (np.abs(x%1 - 0.5)<0.01 and y < 0.01) or np.abs(z)<0.01:
                return ORIGIN
            out_z = 1./(2*np.tan(np.pi*z)*(z**2))
            return out_z.real*RIGHT - out_z.imag*UP
        arrows = Mobject(*[
            Arrow(ORIGIN, np.sqrt(2)*point)
            for point in compass_directions(4, RIGHT+UP)
        ])
        arrows.highlight(YELLOW)
        arrows.ingest_sub_mobjects()
        all_arrows = Mobject(*[
            arrows.copy().scale(0.3/(x)).shift(x*RIGHT)
            for x in range(1, n_terms+2)
        ])
        terms = TexMobject([
            "\\dfrac{1}{%d^2} + "%(x+1)
            for x in range(n_terms)
        ]+["\\cdots"])
        terms.shift(2*UP)
        plane = NumberPlane(color = BLUE_E)
        axes = Mobject(NumberLine(), NumberLine().rotate(np.pi/2))
        axes.highlight(WHITE)

        for term in terms.split():
            self.play(ShimmerIn(term, run_time = 0.5))
        self.dither()
        self.play(ShowCreation(plane), ShowCreation(axes))
        self.play(*[
            Transform(*pair)
            for pair in zip(terms.split(), all_arrows.split())
        ])
        self.play(PhaseFlow(
            func, plane,
            run_time = 5,
            virtual_time = 8
        ))



class TimeLine(Scene):
    def construct(self):
        dated_events = [
            {
                "date" : 1696, 
                "text": "Johann Bernoulli poses Brachistochrone problem",
                "picture" : "Johann_Bernoulli2"
            },
            {
                "date" : 1662, 
                "text" : "Fermat states his principle of least time",
                "picture" : "Pierre_de_Fermat"
            }
        ]
        speical_dates = [2016] + [
            obj["date"] for obj in dated_events
        ]
        centuries = range(1600, 2100, 100)
        timeline = NumberLine(
            numerical_radius = 300,
            number_at_center = 1800,
            unit_length_to_spatial_width = SPACE_WIDTH/100,
            tick_frequency = 10,
            numbers_with_elongated_ticks = centuries
        )
        timeline.add_numbers(*centuries)
        centers = [
            Point(timeline.number_to_point(year))
            for year in speical_dates
        ]
        timeline.add(*centers)
        timeline.shift(-centers[0].get_center())

        self.add(timeline)
        self.dither()
        run_times = iter([3, 1])
        for point, event in zip(centers[1:], dated_events):
            self.play(ApplyMethod(
                timeline.shift, -point.get_center(), 
                run_time = run_times.next()
            ))
            picture = ImageMobject(event["picture"], invert = False)
            picture.scale_to_fit_width(2)
            picture.to_corner(UP+RIGHT)
            event_mob = TextMobject(event["text"])
            event_mob.shift(2*LEFT+2*UP)
            date_mob = TexMobject(str(event["date"]))
            date_mob.scale(0.5)
            date_mob.shift(0.6*UP)
            line = Line(event_mob.get_bottom(), 0.2*UP)
            self.play(
                ShimmerIn(event_mob),
                ShowCreation(line),
                ShimmerIn(date_mob)
            )
            self.play(FadeIn(picture))
            self.dither(3)
            self.play(*map(FadeOut, [event_mob, date_mob, line, picture]))


class StayedUpAllNight(Scene):
    def construct(self):
        clock = Circle(radius = 2, color = WHITE)
        clock.add(Dot(ORIGIN))
        ticks = Mobject(*[
            Line(1.8*vect, 2*vect, color = GREY)
            for vect in compass_directions(12)
        ])
        clock.add(ticks)
        hour_hand = Line(ORIGIN, UP)
        minute_hand = Line(ORIGIN, 1.5*UP)
        clock.add(hour_hand, minute_hand)
        clock.to_corner(UP+RIGHT)
        hour_hand.get_center = lambda : clock.get_center()
        minute_hand.get_center = lambda : clock.get_center()
 
        solution = ImageMobject(
            "Newton_brachistochrone_solution2",
            use_cache = False
        )
        solution.point_thickness = 3
        solution.highlight(GREY)
        solution.scale_to_fit_width(5)
        solution.to_corner(UP+RIGHT)
        newton = ImageMobject("Old_Newton", invert = False)
        newton.scale(0.8)
        phil_trans = TextMobject("Philosophical Transactions")
        rect = Rectangle(height = 6, width = 4.5, color = WHITE)
        rect.to_corner(UP+RIGHT)
        rect.shift(DOWN)
        phil_trans.scale_to_fit_width(0.8*rect.get_width())
        phil_trans.next_to(Point(rect.get_top()), DOWN)
        new_solution = solution.copy()
        new_solution.scale_to_fit_width(phil_trans.get_width())
        new_solution.next_to(phil_trans, DOWN, buff = 1)
        not_newton = TextMobject("-Totally not by Newton")
        not_newton.scale_to_fit_width(2.5)
        not_newton.next_to(new_solution, DOWN, aligned_edge = RIGHT)
        phil_trans.add(rect)

        newton_complaint = TextMobject([
            "``I do not love to be",
            " \\emph{dunned} ",
            "and teased by foreigners''"
        ], size = "\\small")
        newton_complaint.to_edge(UP, buff = 0.2)
        dunned = newton_complaint.split()[1]
        dunned.highlight()
        dunned_def = TextMobject("(old timey term for making \\\\ demands on someone)")
        dunned_def.scale(0.7)
        dunned_def.next_to(phil_trans, LEFT)
        dunned_def.shift(2*UP)
        dunned_arrow = Arrow(dunned_def, dunned)

        johann = ImageMobject("Johann_Bernoulli2", invert = False)
        johann.scale(0.4)
        johann.to_edge(LEFT)
        johann.shift(DOWN)
        johann_quote = TextMobject("``I recognize the lion by his claw''")
        johann_quote.next_to(johann, UP, aligned_edge = LEFT)

        self.play(ApplyMethod(newton.to_edge, LEFT))
        self.play(ShowCreation(clock))
        kwargs = {
            "axis" : OUT,
            "rate_func" : smooth
        }
        self.play(
            Rotating(hour_hand, radians = -2*np.pi, **kwargs),
            Rotating(minute_hand, radians = -12*2*np.pi, **kwargs),
            run_time = 5
        )
        self.dither()
        self.clear()
        self.add(newton)
        clock.ingest_sub_mobjects()
        self.play(Transform(clock, solution))
        self.remove(clock)
        self.add(solution)
        self.dither()
        self.play(
            FadeIn(phil_trans),
            Transform(solution, new_solution)
        )
        self.dither()
        self.play(ShimmerIn(not_newton))
        phil_trans.add(solution, not_newton)
        self.dither()
        self.play(*map(ShimmerIn, newton_complaint.split()))
        self.dither()
        self.play(
            ShimmerIn(dunned_def),
            ShowCreation(dunned_arrow)
        )
        self.dither()
        self.remove(dunned_def, dunned_arrow)
        self.play(FadeOut(newton_complaint))
        self.remove(newton_complaint)
        self.play(
            FadeOut(newton),
            GrowFromCenter(johann)
        )
        self.remove(newton)        
        self.dither()
        self.play(ShimmerIn(johann_quote))
        self.dither()


class ThetaTSigmoidGraph(Scene):
    def construct(self):
        pass














        



