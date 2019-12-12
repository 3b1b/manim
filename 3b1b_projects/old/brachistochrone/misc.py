import numpy as np
import itertools as it

from manimlib.imports import *
from old_projects.brachistochrone.curves import Cycloid

class PhysicalIntuition(Scene):
    def construct(self):
        n_terms = 4
        def func(xxx_todo_changeme):
            (x, y, ignore) = xxx_todo_changeme
            z = complex(x, y)                                    
            if (np.abs(x%1 - 0.5)<0.01 and y < 0.01) or np.abs(z)<0.01:
                return ORIGIN
            out_z = 1./(2*np.tan(np.pi*z)*(z**2))
            return out_z.real*RIGHT - out_z.imag*UP
        arrows = Mobject(*[
            Arrow(ORIGIN, np.sqrt(2)*point)
            for point in compass_directions(4, RIGHT+UP)
        ])
        arrows.set_color(YELLOW)
        arrows.ingest_submobjects()
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
        axes.set_color(WHITE)

        for term in terms.split():
            self.play(ShimmerIn(term, run_time = 0.5))
        self.wait()
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
        centuries = list(range(1600, 2100, 100))
        timeline = NumberLine(
            numerical_radius = 300,
            number_at_center = 1800,
            unit_length_to_spatial_width = FRAME_X_RADIUS/100,
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
        self.wait()
        run_times = iter([3, 1])
        for point, event in zip(centers[1:], dated_events):
            self.play(ApplyMethod(
                timeline.shift, -point.get_center(), 
                run_time = next(run_times)
            ))
            picture = ImageMobject(event["picture"], invert = False)
            picture.set_width(2)
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
            self.wait(3)
            self.play(*list(map(FadeOut, [event_mob, date_mob, line, picture])))


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
        solution.stroke_width = 3
        solution.set_color(GREY)
        solution.set_width(5)
        solution.to_corner(UP+RIGHT)
        newton = ImageMobject("Old_Newton", invert = False)
        newton.scale(0.8)
        phil_trans = TextMobject("Philosophical Transactions")
        rect = Rectangle(height = 6, width = 4.5, color = WHITE)
        rect.to_corner(UP+RIGHT)
        rect.shift(DOWN)
        phil_trans.set_width(0.8*rect.get_width())
        phil_trans.next_to(Point(rect.get_top()), DOWN)
        new_solution = solution.copy()
        new_solution.set_width(phil_trans.get_width())
        new_solution.next_to(phil_trans, DOWN, buff = 1)
        not_newton = TextMobject("-Totally not by Newton")
        not_newton.set_width(2.5)
        not_newton.next_to(new_solution, DOWN, aligned_edge = RIGHT)
        phil_trans.add(rect)

        newton_complaint = TextMobject([
            "``I do not love to be",
            " \\emph{dunned} ",
            "and teased by foreigners''"
        ], size = "\\small")
        newton_complaint.to_edge(UP, buff = 0.2)
        dunned = newton_complaint.split()[1]
        dunned.set_color()
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
        self.wait()
        self.clear()
        self.add(newton)
        clock.ingest_submobjects()
        self.play(Transform(clock, solution))
        self.remove(clock)
        self.add(solution)
        self.wait()
        self.play(
            FadeIn(phil_trans),
            Transform(solution, new_solution)
        )
        self.wait()
        self.play(ShimmerIn(not_newton))
        phil_trans.add(solution, not_newton)
        self.wait()
        self.play(*list(map(ShimmerIn, newton_complaint.split())))
        self.wait()
        self.play(
            ShimmerIn(dunned_def),
            ShowCreation(dunned_arrow)
        )
        self.wait()
        self.remove(dunned_def, dunned_arrow)
        self.play(FadeOut(newton_complaint))
        self.remove(newton_complaint)
        self.play(
            FadeOut(newton),
            GrowFromCenter(johann)
        )
        self.remove(newton)        
        self.wait()
        self.play(ShimmerIn(johann_quote))
        self.wait()


class ThetaTGraph(Scene):
    def construct(self):
        t_axis = NumberLine()
        theta_axis = NumberLine().rotate(np.pi/2)
        theta_mob = TexMobject("\\theta(t)")
        t_mob = TexMobject("t")
        theta_mob.next_to(theta_axis, RIGHT)
        theta_mob.to_edge(UP)
        t_mob.next_to(t_axis, UP)
        t_mob.to_edge(RIGHT)
        graph = ParametricFunction(
            lambda t : 4*t*RIGHT + 2*smooth(t)*UP
        )
        line = Line(graph.points[0], graph.points[-1], color = WHITE)
        q_mark = TextMobject("?")
        q_mark.next_to(Point(graph.get_center()), LEFT)
        stars = Stars(color = BLACK)
        stars.scale(0.1).shift(q_mark.get_center())


        squiggle = ParametricFunction(
            lambda t : t*RIGHT + 0.2*t*(5-t)*(np.sin(t)**2)*UP,
            start = 0,
            end = 5
        )

        self.play(
            ShowCreation(t_axis),
            ShowCreation(theta_axis),
            ShimmerIn(theta_mob),
            ShimmerIn(t_mob)
        )
        self.play(
            ShimmerIn(q_mark),
            ShowCreation(graph)
        )
        self.wait()
        self.play(
            Transform(q_mark, stars),
            Transform(graph, line)
        )
        self.wait()
        self.play(Transform(graph, squiggle))
        self.wait()


class SolutionsToTheBrachistochrone(Scene):
    def construct(self):
        r_range = np.arange(0.5, 2, 0.25)
        cycloids = Mobject(*[
            Cycloid(radius = r, end_theta=2*np.pi)
            for r in r_range
        ])
        lower_left = 2*DOWN+6*LEFT
        lines = Mobject(*[
            Line(
                lower_left, 
                lower_left+5*r*np.cos(np.arctan(r))*RIGHT+2*r*np.sin(np.arctan(r))*UP
            )
            for r in r_range
        ])
        nl = NumberLine(numbers_with_elongated_ticks = [])
        x_axis = nl.copy().shift(3*UP)
        y_axis = nl.copy().rotate(np.pi/2).shift(6*LEFT)
        t_axis = nl.copy().shift(2*DOWN)
        x_label = TexMobject("x")
        x_label.next_to(x_axis, DOWN)
        x_label.to_edge(RIGHT)
        y_label = TexMobject("y")
        y_label.next_to(y_axis, RIGHT)
        y_label.shift(2*DOWN)
        t_label = TexMobject("t")
        t_label.next_to(t_axis, UP)
        t_label.to_edge(RIGHT)
        theta_label = TexMobject("\\theta")
        theta_label.next_to(y_axis, RIGHT)
        theta_label.to_edge(UP)
        words = TextMobject("Boundary conditions?")
        words.next_to(lines, RIGHT)
        words.shift(2*UP)

        self.play(ShowCreation(x_axis), ShimmerIn(x_label))
        self.play(ShowCreation(y_axis), ShimmerIn(y_label))
        self.play(ShowCreation(cycloids))
        self.wait()
        self.play(
            Transform(cycloids, lines),
            Transform(x_axis, t_axis),
            Transform(x_label, t_label),
            Transform(y_label, theta_label),
            run_time = 2
        )
        self.wait()
        self.play(ShimmerIn(words))
        self.wait()


class VideoLayout(Scene):
    def construct(self):
        left, right = 5*LEFT, 5*RIGHT
        top_words = TextMobject("The next 15 minutes of your life:")
        top_words.to_edge(UP)
        line = Line(left, right, color = BLUE_D)
        for a in np.arange(0, 4./3, 1./3):
            vect = interpolate(left, right, a)
            line.add_line(vect+0.2*DOWN, vect+0.2*UP)
        left_brace = Brace(
            Mobject(
                Point(left), 
                Point(interpolate(left, right, 2./3))
            ),
            DOWN
        )
        right_brace = Brace(
            Mobject(
                Point(interpolate(left, right, 2./3)),
                Point(right)
            ),
            UP
        )
        left_brace.words = list(map(TextMobject, [
            "Problem statement", 
            "History",
            "Johann Bernoulli's cleverness"
        ]))
        curr = left_brace
        right_brace.words = list(map(TextMobject, [
            "Challenge",
            "Mark Levi's cleverness",            
        ]))
        for brace in left_brace, right_brace:
            curr = brace
            direction = DOWN if brace is left_brace else UP
            for word in brace.words:
                word.next_to(curr, direction)
                curr = word
        right_brace.words.reverse()

        self.play(ShimmerIn(top_words))
        self.play(ShowCreation(line))
        for brace in left_brace, right_brace:
            self.play(GrowFromCenter(brace))
            self.wait()
            for word in brace.words:
                self.play(ShimmerIn(word))
                self.wait()




class ShortestPathProblem(Scene):
    def construct(self):
        point_a, point_b = 3*LEFT, 3*RIGHT
        dots = []
        for point, char in [(point_a, "A"), (point_b, "B")]:
            dot = Dot(point)
            letter = TexMobject(char)
            letter.next_to(dot, UP+LEFT)
            dot.add(letter)
            dots.append(dot)

        path = ParametricFunction(
            lambda t : (t/2 + np.cos(t))*RIGHT + np.sin(t)*UP,
            start = -2*np.pi,
            end = 2*np.pi
        )
        path.scale(6/(2*np.pi))
        path.shift(point_a - path.points[0])
        path.set_color(RED)
        line = Line(point_a, point_b)
        words = TextMobject("Shortest path from $A$ to $B$")
        words.to_edge(UP)

        self.play(
            ShimmerIn(words),
            *list(map(GrowFromCenter, dots))
        )
        self.play(ShowCreation(path))
        self.play(Transform(
            path, line,
            path_func = path_along_arc(np.pi)
        ))
        self.wait()


class MathBetterThanTalking(Scene):
    def construct(self):
        mathy = Mathematician()
        mathy.to_corner(DOWN+LEFT)
        bubble = ThoughtBubble()
        bubble.pin_to(mathy)
        bubble.write("Math $>$ Talking about math")

        self.add(mathy)
        self.play(ShowCreation(bubble))
        self.play(ShimmerIn(bubble.content))
        self.wait()
        self.play(ApplyMethod(
            mathy.blink, 
            rate_func = squish_rate_func(there_and_back, 0.4, 0.6)
        ))


class DetailsOfProofBox(Scene):
    def construct(self):
        rect = Rectangle(height = 4, width = 6, color = WHITE)
        words = TextMobject("Details of proof")
        words.to_edge(UP)

        self.play(
            ShowCreation(rect),
            ShimmerIn(words)
        )
        self.wait()



class TalkedAboutSnellsLaw(Scene):
    def construct(self):
        randy = Randolph()
        randy.to_corner(DOWN+LEFT)
        morty = Mortimer()
        morty.to_edge(DOWN+RIGHT)
        randy.bubble = SpeechBubble().pin_to(randy)
        morty.bubble = SpeechBubble().pin_to(morty)

        phrases = [
            "Let's talk about Snell's law",
            "I love Snell's law",
            "It's like running from \\\\ a beach into the ocean",
            "It's like two constant \\\\ tension springs",
        ]

        self.add(randy, morty)
        talkers = it.cycle([randy, morty])
        for talker, phrase in zip(talkers, phrases):
            talker.bubble.write(phrase)
            self.play(
                FadeIn(talker.bubble),
                ShimmerIn(talker.bubble.content)
            )
            self.play(ApplyMethod(
                talker.blink, 
                rate_func = squish_rate_func(there_and_back)
            ))
            self.wait()
            self.remove(talker.bubble, talker.bubble.content)


class YetAnotherMarkLevi(Scene):
    def construct(self):
        words = TextMobject("Yet another bit of Mark Levi cleverness")
        words.to_edge(UP)
        levi = ImageMobject("Mark_Levi", invert = False)
        levi.set_width(6)
        levi.show()

        self.add(levi)
        self.play(ShimmerIn(words))
        self.wait(2)
















