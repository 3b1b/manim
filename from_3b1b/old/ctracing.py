from manimlib.imports import *
from from_3b1b.old.sir import *


class LastFewMonths(Scene):
    def construct(self):
        words = TextMobject("Last ", "few\\\\", "months:")
        words.set_height(4)
        underlines = VGroup()
        for word in words:
            underline = Line(LEFT, RIGHT)
            underline.match_width(word)
            underline.next_to(word, DOWN, SMALL_BUFF)
            underlines.add(underline)
        underlines[0].stretch(1.4, 0, about_edge=LEFT)
        underlines.set_color(BLUE)

        # self.play(ShowCreation(underlines))
        self.play(ShowIncreasingSubsets(words, run_time=0.75, rate_func=linear))
        self.wait()


class UnemploymentTitle(Scene):
    def construct(self):
        words = TextMobject("Unemployment claims\\\\per week in the US")[0]
        words.set_width(FRAME_WIDTH - 1)
        words.to_edge(UP)
        arrow = Arrow(
            words.get_bottom(),
            words.get_bottom() + 3 * RIGHT + 3 * DOWN,
            stroke_width=10,
            tip_length=0.5,
        )
        arrow.set_color(BLUE_E)
        words.set_color(BLACK)
        self.play(
            ShowIncreasingSubsets(words),
            ShowCreation(arrow),
        )
        self.wait()


class ExplainTracing(Scene):
    def construct(self):
        # Words
        words = VGroup(
            TextMobject("Testing, ", "Testing, ", "Testing!"),
            TextMobject("Contact Tracing"),
        )
        words[0].set_color(GREEN)
        words[1].set_color(BLUE_B)
        words.set_width(FRAME_WIDTH - 2)
        words.arrange(DOWN, buff=1)

        self.play(ShowIncreasingSubsets(words[0], rate_func=linear))
        self.wait()
        self.play(Write(words[1], run_time=1))
        self.wait()

        self.play(
            words[1].to_edge, UP,
            FadeOut(words[0], 6 * UP)
        )

        ct_word = words[1][0]

        # Groups
        clusters = VGroup()
        for x in range(4):
            cluster = VGroup()
            for y in range(4):
                cluster.add(Randolph())
            cluster.arrange_in_grid(buff=LARGE_BUFF)
            clusters.add(cluster)
        clusters.scale(0.5)
        clusters.arrange_in_grid(buff=2)
        clusters.set_height(4)

        self.play(FadeIn(clusters))

        pis = VGroup()
        boxes = VGroup()
        for cluster in clusters:
            for pi in cluster:
                pis.add(pi)
                box = SurroundingRectangle(pi, buff=0.05)
                boxes.add(box)
                pi.box = box

        boxes.set_stroke(WHITE, 1)

        sicky = clusters[0][2]
        covid_words = TextMobject("COVID-19\\\\Positive!")
        covid_words.set_color(RED)
        arrow = Vector(RIGHT, color=RED)
        arrow.next_to(sicky, LEFT)
        covid_words.next_to(arrow, LEFT, SMALL_BUFF)

        self.play(
            sicky.change, "sick",
            sicky.set_color, "#9BBD37",
            FadeIn(covid_words, RIGHT),
            GrowArrow(arrow),
        )
        self.play(ShowCreation(sicky.box))
        self.wait(2)
        anims = []
        for pi in clusters[0]:
            if pi is not sicky:
                anims.append(ApplyMethod(pi.change, "tired"))
                anims.append(ShowCreation(pi.box))
        self.play(*anims)
        self.wait()

        self.play(VFadeIn(
            boxes[4:],
            run_time=2,
            rate_func=there_and_back_with_pause,
        ))
        self.wait()

        self.play(FadeOut(
            VGroup(
                covid_words,
                arrow,
                *boxes[:4],
                *pis,
            ),
            lag_ratio=0.1,
            run_time=3,
        ))
        self.play(ct_word.move_to, 2 * UP)

        # Underlines
        implies = TexMobject("\\Downarrow")
        implies.scale(2)
        implies.next_to(ct_word, DOWN, MED_LARGE_BUFF)
        loc_tracking = TextMobject("Location Tracking")
        loc_tracking.set_color(GREY_BROWN)
        loc_tracking.match_height(ct_word)
        loc_tracking.next_to(implies, DOWN, MED_LARGE_BUFF)

        q_marks = TexMobject("???")
        q_marks.scale(2)
        q_marks.next_to(implies, RIGHT)

        cross = Cross(implies)
        cross.set_stroke(RED, 7)

        self.play(
            Write(implies),
            FadeIn(loc_tracking, UP)
        )
        self.play(FadeIn(q_marks, lag_ratio=0.1))
        self.wait()

        parts = VGroup(ct_word[:7], ct_word[7:])
        lines = VGroup()
        for part in parts:
            line = Line(part.get_left(), part.get_right())
            line.align_to(part[0], DOWN)
            line.shift(0.1 * DOWN)
            lines.add(line)
        
        ct_word.set_stroke(BLACK, 2, background=True)
        self.add(lines[1], ct_word)
        self.play(ShowCreation(lines[1]))
        self.wait()
        self.play(ShowCreation(lines[0]))
        self.wait()

        self.play(
            ShowCreation(cross),
            FadeOut(q_marks, RIGHT),
            FadeOut(lines),
        )
        self.wait()

        dp_3t = TextMobject("DP-3T")
        dp_3t.match_height(ct_word)
        dp_3t.move_to(loc_tracking)
        dp_3t_long = TextMobject("Decentralized Privacy-Preserving Proximity Tracing")
        dp_3t_long.next_to(dp_3t, DOWN, LARGE_BUFF)

        arrow = Vector(UP)
        arrow.set_stroke(width=8)
        arrow.move_to(implies)

        self.play(
            FadeInFromDown(dp_3t),
            FadeOut(loc_tracking),
            FadeOut(implies),
            FadeOut(cross),
            ShowCreation(arrow)
        )
        self.play(Write(dp_3t_long))
        self.wait()


class ContactTracingMisnomer(Scene):
    def construct(self):
        # Word play
        words = TextMobject("Contact ", "Tracing")
        words.scale(2)
        rects = VGroup(*[
            SurroundingRectangle(word, buff=0.2)
            for word in words
        ])
        expl1 = TextMobject("Doesn't ``trace'' you...")
        expl2 = TextMobject("...or your contacts")
        expls = VGroup(expl1, expl2)
        colors = [RED, BLUE]

        self.add(words)
        for vect, rect, expl, color in zip([UP, DOWN], reversed(rects), expls, colors):
            arrow = Vector(-vect)
            arrow.next_to(rect, vect, SMALL_BUFF)
            expl.next_to(arrow, vect, SMALL_BUFF)
            rect.set_color(color)
            arrow.set_color(color)
            expl.set_color(color)

            self.play(
                FadeIn(expl, -vect),
                GrowArrow(arrow),
                ShowCreation(rect),
            )
            self.wait()

        self.play(Write(
            VGroup(*self.mobjects),
            rate_func=lambda t: smooth(1 - t),
            run_time=3,
        ))


class ContactTracingWords(Scene):
    def construct(self):
        words = TextMobject("Contact\\\\", "Tracing")
        words.set_height(4)
        for word in words:
            self.add(word)
            self.wait()
        self.wait()
        return
        self.play(ShowIncreasingSubsets(words))
        self.wait()
        self.play(
            words.set_height, 1,
            words.to_corner, UL,
        )
        self.wait()


class WanderingDotsWithLines(Scene):
    def construct(self):
        sim = SIRSimulation(
            city_population=20,
            person_type=DotPerson,
            person_config={
                "color_map": {
                    "S": GREY,
                    "I": GREY,
                    "R": GREY,
                },
                "infection_ring_style": {
                    "stroke_color": YELLOW,
                },
                "max_speed": 0.5,
            },
            infection_time=100,
        )

        for person in sim.people:
            person.set_status("S")
            person.infection_start_time += random.random()

        lines = VGroup()

        max_dist = 1.25

        def update_lines(lines):
            lines.remove(*lines.submobjects)
            for p1 in sim.people:
                for p2 in sim.people:
                    if p1 is p2:
                        continue
                    dist = get_norm(p1.get_center() - p2.get_center())
                    if dist < max_dist:
                        line = Line(p1.get_center(), p2.get_center())
                        alpha = (max_dist - dist) / max_dist
                        line.set_stroke(
                            interpolate_color(WHITE, RED, alpha),
                            width=4 * alpha
                        )
                        lines.add(line)

        lines.add_updater(update_lines)

        self.add(lines)
        self.add(sim)
        self.wait(10)
        for person in sim.people:
            person.set_status("I")
            person.infection_start_time += random.random()
        self.wait(50)


class WhatAboutPeopleWithoutPhones(TeacherStudentsScene):
    def construct(self):
        self.student_says(
            "What about people\\\\without phones?",
            target_mode="sassy",
            added_anims=[self.teacher.change, "guilty"]
        )
        self.change_student_modes("angry", "angry", "sassy")
        self.wait()
        self.play(self.teacher.change, "tease")
        self.wait()

        words = VectorizedPoint()
        words.scale(1.5)
        words.to_corner(UL)

        self.play(
            FadeInFromDown(words),
            RemovePiCreatureBubble(self.students[2]),
            *[
                ApplyMethod(pi.change, "pondering", words)
                for pi in self.pi_creatures
            ]
        )
        self.wait(5)


class PiGesture1(Scene):
    def construct(self):
        randy = Randolph(mode="raise_right_hand", height=2)
        bubble = randy.get_bubble(
            bubble_class=SpeechBubble,
            height=2, width=3,
        )
        bubble.write("This one's\\\\great")
        bubble.content.scale(0.8)
        bubble.content.set_color(BLACK)
        bubble.set_color(BLACK)
        bubble.set_fill(opacity=0)
        randy.set_stroke(BLACK, 5, background=True)
        self.add(randy, bubble, bubble.content)


class PiGesture2(Scene):
    def construct(self):
        randy = Randolph(mode="raise_left_hand", height=2)
        randy.look(UL)
        # randy.flip()
        randy.set_color(GREY_BROWN)
        bubble = randy.get_bubble(
            bubble_class=SpeechBubble,
            height=2, width=3,
            direction=LEFT,
        )
        bubble.write("So is\\\\this one")
        bubble.content.scale(0.8)
        bubble.content.set_color(BLACK)
        bubble.set_color(BLACK)
        bubble.set_fill(opacity=0)
        randy.set_stroke(BLACK, 5, background=True)
        self.add(randy, bubble, bubble.content)


class PiGesture3(Scene):
    def construct(self):
        randy = Randolph(mode="hooray", height=2)
        randy.flip()
        bubble = randy.get_bubble(
            bubble_class=SpeechBubble,
            height=2, width=3,
            direction=LEFT,
        )
        bubble.write("And this\\\\one")
        bubble.content.scale(0.8)
        bubble.content.set_color(BLACK)
        bubble.set_color(BLACK)
        bubble.set_fill(opacity=0)
        randy.set_stroke(BLACK, 5, background=True)
        self.add(randy, bubble, bubble.content)


class AppleGoogleCoop(Scene):
    def construct(self):
        logos = Group(
            self.get_apple_logo(),
            self.get_google_logo(),
        )
        for logo in logos:
            logo.set_height(2)
        apple, google = logos

        logos.arrange(RIGHT, buff=3)

        arrows = VGroup()
        for vect, u in zip([UP, DOWN], [0, 1]):
            m1, m2 = logos[u], logos[1 - u]
            arrows.add(Arrow(
                m1.get_edge_center(vect),
                m2.get_edge_center(vect),
                path_arc=-90 * DEGREES,
                buff=MED_LARGE_BUFF,
                stroke_width=10,
            ))

        self.play(LaggedStart(
            Write(apple),
            FadeIn(google),
            lag_ratio=0.7,
        ))
        self.wait()
        self.play(ShowCreation(arrows, run_time=2))
        self.wait()

    def get_apple_logo(self):
        result = SVGMobject("apple_logo")
        result.set_color("#b3b3b3")
        return result

    def get_google_logo(self):
        result = ImageMobject("google_logo_black")
        return result


class LocationTracking(Scene):
    def construct(self):
        question = TextMobject(
            "Would you like this company to track\\\\",
            "and occasionally sell your location?"
        )
        question.to_edge(UP, buff=LARGE_BUFF)

        slider = Rectangle(width=1.25, height=0.5)
        slider.round_corners(radius=0.25)
        slider.set_fill(GREEN, 1)
        slider.next_to(question, DOWN, buff=MED_LARGE_BUFF)

        dot = Dot(radius=0.25)
        dot.set_fill(GREY_C, 1)
        dot.set_stroke(WHITE, 3)
        dot.move_to(slider, RIGHT)

        morty = Mortimer()
        morty.next_to(slider, RIGHT)
        morty.to_edge(DOWN)

        bubble = morty.get_bubble(
            height=2,
            width=3,
            direction=LEFT,
        )

        answer = TextMobject("Um...", "no.")
        answer.set_height(0.4)
        answer.set_color(YELLOW)
        bubble.add_content(answer)

        self.add(morty)

        self.play(
            FadeInFromDown(question),
            Write(slider),
            FadeIn(dot),
        )
        self.play(morty.change, "confused", slider)
        self.play(Blink(morty))
        self.play(
            FadeIn(bubble),
            Write(answer[0]),
        )
        self.wait()
        self.play(
            dot.move_to, slider, LEFT,
            slider.set_fill, {"opacity": 0},
            FadeIn(answer[1]),
            morty.change, "sassy"
        )
        self.play(Blink(morty))
        self.wait(2)
        self.play(Blink(morty))
        self.wait(2)


class MoreLinks(Scene):
    def construct(self):
        words = TextMobject("See more links\\\\in the description.")
        words.scale(2)
        words.to_edge(UP, buff=2)
        arrows = VGroup(*[
            Vector(1.5 * DOWN, stroke_width=10)
            for x in range(4)
        ])
        arrows.arrange(RIGHT, buff=0.75)
        arrows.next_to(words, DOWN, buff=0.5)
        for arrow, color in zip(arrows, [BLUE_D, BLUE_C, BLUE_E, GREY_BROWN]):
            arrow.set_color(color)
        self.play(Write(words))
        self.play(LaggedStartMap(ShowCreation, arrows))
        self.wait()


class LDMEndScreen(PatreonEndScreen):
    CONFIG = {
        "scroll_time": 20,
        "specific_patrons": [
            "1stViewMaths",
            "Aaron",
            "Adam Dřínek",
            "Adam Margulies",
            "Aidan Shenkman",
            "Alan Stein",
            "Albin Egasse",
            "Alex Mijalis",
            "Alexander Mai",
            "Alexis Olson",
            "Ali Yahya",
            "Andreas Snekloth Kongsgaard",
            "Andrew Busey",
            "Andrew Cary",
            "Andrew R. Whalley",
            "Aravind C V",
            "Arjun Chakroborty",
            "Arthur Zey",
            "Ashwin Siddarth",
            "Augustine Lim",
            "Austin Goodman",
            "Avi Finkel",
            "Awoo",
            "Axel Ericsson",
            "Ayan Doss",
            "AZsorcerer",
            "Barry Fam",
            "Bartosz Burclaf",
            "Ben Delo",
            "Benjamin Bailey",
            "Bernd Sing",
            "Bill Gatliff",
            "Boris Veselinovich",
            "Bradley Pirtle",
            "Brandon Huang",
            "Brendan Shah",
            "Brian Cloutier",
            "Brian Staroselsky",
            "Britt Selvitelle",
            "Britton Finley",
            "Burt Humburg",
            "Calvin Lin",
            "Carl-Johan R. Nordangård",
            "Charles Southerland",
            "Charlie N",
            "Chris Connett",
            "Chris Druta",
            "Christian Kaiser",
            "cinterloper",
            "Clark Gaebel",
            "Colwyn Fritze-Moor",
            "Corey Ogburn",
            "D. Sivakumar",
            "Dan Herbatschek",
            "Daniel Brown",
            "Daniel Herrera C",
            "Darrell Thomas",
            "Dave B",
            "Dave Cole",
            "Dave Kester",
            "dave nicponski",
            "David B. Hill",
            "David Clark",
            "David Gow",
            "Delton Ding",
            "Dominik Wagner",
            "Eduardo Rodriguez",
            "Emilio Mendoza",
            "emptymachine",
            "Eric Younge",
            "Eryq Ouithaqueue",
            "Federico Lebron",
            "Fernando Via Canel",
            "Frank R. Brown, Jr.",
            "gary",
            "Giovanni Filippi",
            "Goodwine",
            "Hal Hildebrand",
            "Heptonion",
            "Hitoshi Yamauchi",
            "Isaac Gubernick",
            "Ivan Sorokin",
            "Jacob Baxter",
            "Jacob Harmon",
            "Jacob Hartmann",
            "Jacob Magnuson",
            "Jalex Stark",
            "Jameel Syed",
            "James Beall",
            "Jason Hise",
            "Jayne Gabriele",
            "Jean-Manuel Izaret",
            "Jeff Dodds",
            "Jeff Linse",
            "Jeff Straathof",
            "Jeffrey Wolberg",
            "Jimmy Yang",
            "Joe Pregracke",
            "Johan Auster",
            "John C. Vesey",
            "John Camp",
            "John Haley",
            "John Le",
            "John Luttig",
            "John Rizzo",
            "John V Wertheim",
            "jonas.app",
            "Jonathan Heckerman",
            "Jonathan Wilson",
            "Joseph John Cox",
            "Joseph Kelly",
            "Josh Kinnear",
            "Joshua Claeys",
            "Joshua Ouellette",
            "Juan Benet",
            "Julien Dubois",
            "Kai-Siang Ang",
            "Kanan Gill",
            "Karl Niu",
            "Kartik Cating-Subramanian",
            "Kaustuv DeBiswas",
            "Killian McGuinness",
            "kkm",
            "Klaas Moerman",
            "Kristoffer Börebäck",
            "Kros Dai",
            "L0j1k",
            "Lael S Costa",
            "LAI Oscar",
            "Lambda GPU Workstations",
            "Laura Gast",
            "Lee Redden",
            "Linh Tran",
            "Luc Ritchie",
            "Ludwig Schubert",
            "Lukas Biewald",
            "Lukas Zenick",
            "Magister Mugit",
            "Magnus Dahlström",
            "Magnus Hiie",
            "Manoj Rewatkar - RITEK SOLUTIONS",
            "Mark B Bahu",
            "Mark Heising",
            "Mark Hopkins",
            "Mark Mann",
            "Martin Price",
            "Mathias Jansson",
            "Matt Godbolt",
            "Matt Langford",
            "Matt Roveto",
            "Matt Russell",
            "Matteo Delabre",
            "Matthew Bouchard",
            "Matthew Cocke",
            "Maxim Nitsche",
            "Michael Bos",
            "Michael Hardel",
            "Michael W White",
            "Mirik Gogri",
            "Molly Mackinlay",
            "Mustafa Mahdi",
            "Márton Vaitkus",
            "Nero Li",
            "Nicholas Cahill",
            "Nikita Lesnikov",
            "Nitu Kitchloo",
            "Oleg Leonov",
            "Oliver Steele",
            "Omar Zrien",
            "Omer Tuchfeld",
            "Patrick Gibson",
            "Patrick Lucas",
            "Pavel Dubov",
            "Pesho Ivanov",
            "Petar Veličković",
            "Peter Ehrnstrom",
            "Peter Francis",
            "Peter Mcinerney",
            "Pierre Lancien",
            "Pradeep Gollakota",
            "Rafael Bove Barrios",
            "Raghavendra Kotikalapudi",
            "Randy C. Will",
            "rehmi post",
            "Rex Godby",
            "Ripta Pasay",
            "Rish Kundalia",
            "Roman Sergeychik",
            "Roobie",
            "Ryan Atallah",
            "Samuel Judge",
            "SansWord Huang",
            "Scott Gray",
            "Scott Walter, Ph.D.",
            "soekul",
            "Solara570",
            "Spyridon Michalakis",
            "Stephen Shanahan",
            "Steve Huynh",
            "Steve Muench",
            "Steve Sperandeo",
            "Steven Siddals",
            "Stevie Metke",
            "Sundar Subbarayan",
            "supershabam",
            "Suteerth Vishnu",
            "Suthen Thomas",
            "Tal Einav",
            "Taras Bobrovytsky",
            "Tauba Auerbach",
            "Ted Suzman",
            "Terry Hayes",
            "THIS IS THE point OF NO RE tUUurRrhghgGHhhnnn",
            "Thomas J Sargent",
            "Thomas Tarler",
            "Tianyu Ge",
            "Tihan Seale",
            "Tim Erbes",
            "Tim Kazik",
            "Tomasz Legutko",
            "Tyler Herrmann",
            "Tyler Parcell",
            "Tyler VanValkenburg",
            "Tyler Veness",
            "Ubiquity Ventures",
            "Vassili Philippov",
            "Vasu Dubey",
            "Veritasium",
            "Vignesh Ganapathi Subramanian",
            "Vinicius Reis",
            "Vladimir Solomatin",
            "Wooyong Ee",
            "Xuanji Li",
            "Yana Chernobilsky",
            "Yavor Ivanov",
            "Yetinother",
            "YinYangBalance.Asia",
            "Yu Jun",
            "Yurii Monastyrshyn",
            "Zachariah Rosenberg",
        ],
    }
