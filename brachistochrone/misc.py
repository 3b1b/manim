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
from topics.characters import Randolph, Mathematician
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
        for point, event in zip(centers[1:], dated_events):
            self.play(ApplyMethod(
                timeline.shift, -point.get_center(), 
                run_time = 3
            ))
            picture = ImageMobject(event["picture"], invert = False)
            picture.scale_to_fit_width(2)
            picture.to_corner(UP+RIGHT)
            event_mob = TextMobject(event["text"])
            event_mob.shift(2*LEFT+2*UP)
            arrow = Arrow(event_mob.get_bottom(), ORIGIN)
            self.play(
                ShimmerIn(event_mob),
                ShowCreation(arrow)
            )
            self.play(FadeIn(picture))
            self.dither()
            self.play(*map(FadeOut, [event_mob, arrow, picture]))









