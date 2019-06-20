from manimlib.imports import *
from old_projects.lost_lecture import ShowWord
from old_projects.clacks.solution2.mirror_scenes import ReflectWorldThroughMirrorNew
from old_projects.clacks.question import Thumbnail


class WrapperScene(Scene):
    CONFIG = {
        "title": "Title",
        "shade_of_grey": "#333333"
    }

    def construct(self):
        title = TextMobject(self.title)
        title.scale(1.5)
        title.to_edge(UP)
        big_rect = self.get_big_rect()
        screen_rect = self.get_screen_rect()
        screen_rect.next_to(title, DOWN)

        self.add(big_rect, screen_rect)
        self.play(
            FadeIn(big_rect),
            FadeInFrom(title, DOWN),
            FadeInFrom(screen_rect, UP),
        )
        self.wait()

    def get_big_rect(self):
        big_rect = FullScreenFadeRectangle()
        big_rect.set_fill(self.shade_of_grey, 1)
        return big_rect

    def get_screen_rect(self, height=6):
        screen_rect = ScreenRectangle(height=height)
        screen_rect.set_fill(BLACK, 1)
        return screen_rect


class ComingUpWrapper(WrapperScene):
    CONFIG = {"title": "Coming up..."}


class LastVideoWrapper(WrapperScene):
    CONFIG = {"title": "Last time..."}


class LeftEdge(Scene):
    CONFIG = {
        "text": "Left edge",
        "vect": LEFT,
    }

    def construct(self):
        words = TextMobject(self.text)
        arrow = Vector(self.vect)
        arrow.match_width(words)
        arrow.next_to(words, DOWN)

        self.play(
            FadeInFromDown(words),
            GrowArrow(arrow)
        )
        self.wait()


class RightEdge(LeftEdge):
    CONFIG = {
        "text": "Right edge",
        "vect": RIGHT,
    }


class NoteOnEnergyLostToSound(Scene):
    def construct(self):
        self.add(TextMobject(
            "Yeah yeah, the clack sound\\\\"
            "would require energy, but\\\\"
            "don't let accuracy get in the\\\\"
            "way of delight!",
            alignment="",
        ))


class DotProductVideoWrapper(WrapperScene):
    CONFIG = {"title": "Dot product"}


class Rectangle(Scene):
    def construct(self):
        rect = ScreenRectangle(height=FRAME_HEIGHT - 0.25)
        rect.set_stroke(WHITE, 6)
        self.add(rect)


class ShowRectangleCreation(Scene):
    def construct(self):
        rect = ScreenRectangle(height=2)
        rect.set_stroke(YELLOW, 6)
        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))


class ShowDotProductMeaning(Scene):
    def construct(self):
        v_vect = Vector(2 * RIGHT, color=YELLOW)
        w_vect = Vector(3 * RIGHT, color=PINK)
        dot = Dot(color=RED)
        dot.shift(DOWN)

        v_vect.angle_tracker = ValueTracker()
        w_vect.angle_tracker = ValueTracker()

        def update_vect(vect):
            target = vect.angle_tracker.get_value()
            vect.rotate(target - vect.get_angle())
            vect.shift(dot.get_center() - vect.get_start())

        v_vect.add_updater(update_vect)
        w_vect.add_updater(update_vect)

        v_label = TexMobject("\\vec{\\textbf{v}}")
        v_label.vect = v_vect
        w_label = TexMobject("\\vec{\\textbf{w}}")
        w_label.vect = w_vect
        for label in v_label, w_label:
            label.match_color(label.vect)
            label.set_stroke(BLACK, 5, background=True)

        def update_label(label):
            target = np.array(label.vect.get_end())
            target += 0.25 * normalize(label.vect.get_vector())
            label.move_to(target)

        v_label.add_updater(update_label)
        w_label.add_updater(update_label)

        title = TexMobject(
            "\\vec{\\textbf{w}}",
            "\\cdot",
            "\\vec{\\textbf{v}}",
            "=",
            "||", "\\vec{\\textbf{w}}", "||",
            "\\cdot",
            "||", "\\vec{\\textbf{v}}", "||",
            "\\cdot",
            "\\cos(\\theta)"
        )
        title.set_color_by_tex_to_color_map({
            "textbf{v}": v_vect.get_color(),
            "textbf{w}": w_vect.get_color(),
        })
        title.to_edge(UP)

        def get_w_line():
            center = dot.get_center()
            direction = w_vect.get_vector()
            return Line(
                center - 3 * direction,
                center + 3 * direction,
                stroke_color=LIGHT_GREY,
                stroke_width=1,
            )
        w_line = always_redraw(get_w_line)

        def get_proj_v():
            center = dot.get_center()
            v = v_vect.get_vector()
            w = w_vect.get_vector()
            w_unit = normalize(w)
            result = Vector(np.dot(v, w_unit) * w_unit)
            result.set_fill(v_vect.get_color(), 0.5)
            result.shift(center - result.get_start())
            return result
        proj_v = always_redraw(get_proj_v)

        def get_proj_line():
            return DashedLine(
                v_vect.get_end(),
                proj_v.get_end(),
                stroke_width=1,
                dash_length=0.025,
            )
        proj_line = always_redraw(get_proj_line)

        template_line = Line(LEFT, RIGHT)

        def get_vect_brace(vect):
            brace = Brace(template_line, UP, buff=SMALL_BUFF)
            brace.set_width(vect.get_length(), stretch=True)
            angle = vect.get_angle() % TAU
            if angle < PI:
                angle += PI
            brace.rotate(angle, about_point=ORIGIN)
            brace.shift(vect.get_center())
            return brace
        w_brace = always_redraw(
            lambda: get_vect_brace(w_vect)
        )
        proj_v_brace = always_redraw(
            lambda: get_vect_brace(proj_v)
        )

        def get_arc():
            center = dot.get_center()
            a1 = w_vect.get_angle()
            a2 = v_vect.get_angle()
            arc = Arc(
                start_angle=a1,
                angle=a2 - a1,
                radius=0.5,
                arc_center=center,
            )
            theta = TexMobject("\\theta")
            p = arc.point_from_proportion(0.5)
            theta.move_to(
                center + 1.5 * (p - center)
            )
            return VGroup(arc, theta)
        arc = always_redraw(get_arc)

        self.add(
            title[:3],
            w_vect, v_vect, dot,
            w_label, v_label,
        )
        self.play(
            v_vect.angle_tracker.set_value, 170 * DEGREES,
            w_vect.angle_tracker.set_value, 45 * DEGREES,
            run_time=2,
        )
        self.wait()
        w_brace.update()
        self.play(
            GrowFromCenter(w_brace),
            Write(title[3:7])
        )

        self.add(w_line, w_vect, w_label, dot)
        self.play(ShowCreation(w_line))
        proj_v.update()
        self.play(
            ShowCreation(proj_line),
            TransformFromCopy(v_vect, proj_v),
        )
        self.add(proj_v, proj_line, dot)
        proj_v_brace.update()
        self.play(
            GrowFromCenter(proj_v_brace),
            FadeInFromDown(title[7:])
        )
        arc.update()
        self.play(Write(arc))
        self.wait()

        for angle in [135, 225, 270, 90, 150]:
            self.play(
                v_vect.angle_tracker.set_value, angle * DEGREES,
                run_time=2
            )
            self.wait()


class FinalComment(Scene):
    def construct(self):
        self.add(TextMobject(
            "Thoughts on what ending should go here?\\\\"
            "See the Patreon post."
        ))


class FourtyFiveDegreeLine(Scene):
    CONFIG = {
        "angle": 45 * DEGREES,
        "label_config": {
            "num_decimal_places": 0,
            "unit": "^\\circ",
            "label_height": 0.3,
        },
        "degrees": True
    }

    def construct(self):
        angle = self.angle
        arc = Arc(angle, radius=1)
        label = DecimalNumber(0, **self.label_config)
        label.set_height(self.label_config["label_height"])
        label.next_to(arc, RIGHT)
        label.shift(0.5 * SMALL_BUFF * UP)
        line1 = Line(ORIGIN, 3 * RIGHT)
        line2 = line1.copy()

        if self.degrees:
            target_value = int(angle / DEGREES)
        else:
            target_value = angle

        self.add(line1, label)
        self.play(
            ChangeDecimalToValue(label, target_value),
            ShowCreation(arc),
            Rotate(line2, angle, about_point=ORIGIN)
        )
        self.wait()


class ArctanSqrtPoint1Angle(FourtyFiveDegreeLine):
    CONFIG = {
        "angle": np.arctan(np.sqrt(0.1)),
    }


class AskAboutAddingThetaToItself(Scene):
    CONFIG = {
        "theta": np.arctan(0.25),
        "wait_time": 0.25,
        "wedge_radius": 3,
        "theta_symbol_scale_val": 0.5,
        "number_height": 0.2,
    }

    def construct(self):
        theta = self.theta
        groups = self.get_groups(theta)
        horizon = self.get_horizon()
        counter = ValueTracker(0)
        dynamic_ineq = self.get_dynamic_inequality(counter)
        semicircle = self.get_semicircle()

        self.add(horizon)
        self.add(dynamic_ineq)

        for n in range(len(groups)):
            counter.set_value(n + 1)
            if n < len(groups) - 1:
                groups[n][-1].set_color(YELLOW)
                if n > 0:
                    groups[n - 1][-1].set_color(WHITE)
            self.add(groups[:n + 1])
            self.add_sound("pen_click", gain=-20)
            self.wait(self.wait_time)
        self.wait(0.5)

        counter.set_value(counter.get_value() - 1)
        self.remove(groups[-1])
        self.add_sound("pen_click", gain=-20)
        self.wait()

        self.play(ShowCreation(semicircle))
        self.play(FadeOut(semicircle))

        self.wait(3)

    def get_group(self, theta):
        # Define group
        wedge_radius = self.wedge_radius
        wedge = VGroup(
            Line(ORIGIN, wedge_radius * RIGHT),
            Line(ORIGIN, wedge_radius * RIGHT).rotate(
                theta, about_point=ORIGIN
            ),
        )
        wedge.set_stroke((WHITE, GREY), 2)
        arc = Arc(theta, radius=1)
        theta_symbol = TexMobject("\\theta")
        tssv = self.theta_symbol_scale_val
        theta_symbol.scale(tssv)
        theta_symbol.next_to(arc, RIGHT, tssv / 2)
        theta_symbol.shift(tssv * SMALL_BUFF * UP)

        return VGroup(wedge, arc, theta_symbol)

    def get_groups(self, theta):
        group = self.get_group(theta)
        angles = [k * theta for k in range(int(PI / theta) + 1)]
        groups = VGroup(*[
            group.copy().rotate(angle, about_point=ORIGIN)
            for angle in angles
        ])
        # colors = it.cycle([BLUE_D, BLUE_B, BLUE_C, GREY_BROWN])
        colors = it.cycle([BLUE_D, GREY_BROWN])
        for n, angle, group, color in zip(it.count(1), angles, groups, colors):
            wedge, arc, symbol = group
            symbol.rotate(-angle)
            arc.set_color(color)
            number = Integer(n)
            number.set_height(self.number_height)
            number.move_to(center_of_mass([
                wedge[0].get_end(),
                wedge[1].get_end(),
            ]))
            group.add(number)
        groups[-1][-1].set_color(RED)

        return groups

    def get_horizon(self):
        horizon = DashedLine(5 * LEFT, 5 * RIGHT)
        horizon.set_stroke(WHITE, 1)
        return horizon

    def get_semicircle(self):
        return Arc(
            start_angle=0,
            angle=PI,
            radius=self.wedge_radius / 2,
            color=YELLOW,
            stroke_width=4,
        )

    def get_inequality(self):
        ineq = TexMobject(
            "N", "\\cdot", "\\theta", "<",
            "\\pi", "=", "3.1415926\\dots"
        )
        N = ineq.get_part_by_tex("N")
        self.pi_symbol = ineq.get_part_by_tex("\\pi")
        N.set_color(YELLOW)
        # ineq[-3:].set_color(BLUE)

        brace = Brace(N, UP, buff=SMALL_BUFF)
        text = brace.get_text("Maximum", buff=SMALL_BUFF)
        group = VGroup(ineq, brace, text)
        group.next_to(ORIGIN, DOWN, MED_LARGE_BUFF)
        return group

    def get_dynamic_inequality(self, counter):
        multiple = Integer(0)
        dot = TexMobject("\\cdot")
        theta_tex = TexMobject("({:.2f})".format(self.theta))
        eq = TexMobject("=")
        value = DecimalNumber(0)
        ineq = TexMobject("<")
        pi = TexMobject("\\pi", "=", "3.1415926\\dots")
        # pi.set_color(BLUE)
        group = VGroup(
            multiple, dot, theta_tex,
            eq, value,
            ineq, pi
        )
        group.arrange(RIGHT, buff=0.2)
        group.next_to(ORIGIN, DOWN, buff=LARGE_BUFF)
        theta_brace = Brace(group[2], DOWN, buff=SMALL_BUFF)
        theta_symbol = theta_brace.get_tex("\\theta")
        group.add(theta_brace, theta_symbol)
        # group.align_to(self.pi_symbol, RIGHT)

        def get_count():
            return int(counter.get_value())

        def get_product():
            return get_count() * self.theta

        def is_greater_than_pi():
            return get_product() > PI

        def get_color():
            return RED if is_greater_than_pi() else YELLOW

        def get_ineq():
            result = TexMobject(
                ">" if is_greater_than_pi() else "<"
            )
            result.set_color(get_color())
            result.move_to(ineq)
            return result
        dynamic_ineq = always_redraw(get_ineq)
        group.remove(ineq)
        group.add(dynamic_ineq)

        multiple.add_updater(lambda m: m.set_value(get_count()))
        multiple.add_updater(lambda m: m.next_to(dot, LEFT, 0.2))
        multiple.add_updater(lambda m: m.set_color(get_color()))
        value.add_updater(lambda m: m.set_value(get_product()))

        return group


class AskAboutAddingThetaToItselfThetaPoint1(AskAboutAddingThetaToItself):
    CONFIG = {
        "theta": 0.1,
        "wait_time": 0.1,
        "theta_symbol_scale_val": 0.25,
        "number_height": 0.15,
    }


class AskAboutAddingThetaToItselfThetaPoint2(AskAboutAddingThetaToItself):
    CONFIG = {
        "theta": 0.2,
        "wait_time": 0.1,
    }


class FinalFormula(Scene):
    def construct(self):
        text = TextMobject("Final answer: ")
        t2c_map = {
            "\\theta": BLUE,
            "m_1": GREEN,
            "m_2": RED,
        }

        formula = TexMobject(
            "\\left\\lfloor",
            "{\\pi", "\\over", "\\theta}",
            "\\right\\rfloor"
        )
        formula.set_color_by_tex_to_color_map(t2c_map)
        group = VGroup(text, formula)
        group.arrange(RIGHT)
        group.scale(1.5)
        group.to_edge(UP)

        self.play(Write(text))
        self.play(FadeInFrom(formula))
        self.play(ShowCreationThenFadeAround(formula))
        self.wait()

        theta_eq = TexMobject(
            "\\theta", "=", "\\arctan", "\\left(",
            "\\sqrt",
            "{{m_2", "\\over", "m_1}}",
            "\\right)"
        )
        theta_eq.set_color_by_tex_to_color_map(t2c_map)
        theta_eq.scale(1.5)
        theta_eq.next_to(group, DOWN, MED_LARGE_BUFF)

        self.play(TransformFromCopy(
            formula.get_part_by_tex("\\theta"),
            theta_eq.get_part_by_tex("\\theta"),
        ))
        self.play(Write(theta_eq[1:]))
        self.wait()


class ReviewWrapper(WrapperScene):
    CONFIG = {"title": "To review:"}


class SurprisedRandy(Scene):
    def construct(self):
        randy = Randolph()
        self.play(randy.change, "surprised", 3 * UR)
        self.play(Blink(randy))
        self.play(randy.change, "confused")
        self.play(Blink(randy))
        self.wait()


class TwoSolutionsWrapper(WrapperScene):
    def construct(self):
        big_rect = self.get_big_rect()
        screen_rects = VGroup(*[
            self.get_screen_rect(height=3)
            for x in range(2)
        ])
        screen_rects.arrange(RIGHT, buff=LARGE_BUFF)
        title = TextMobject("Two solutions")
        title.scale(1.5)
        title.to_edge(UP)
        screen_rects.next_to(title, DOWN, LARGE_BUFF)

        # pi creatures
        pis = VGroup(
            Randolph(color=BLUE_D),
            Randolph(color=BLUE_E),
            Randolph(color=BLUE_B),
            Mortimer().scale(1.2)
        )
        pis.set_height(2)
        pis.arrange(RIGHT, buff=MED_LARGE_BUFF)
        pis.to_edge(DOWN, buff=SMALL_BUFF)

        self.add(big_rect, title, pis)
        self.play(
            LaggedStartMap(
                ShowCreation, screen_rects.copy().set_fill(opacity=0),
                lag_ratio=0.8
            ),
            LaggedStartMap(
                FadeIn, screen_rects,
                lag_ratio=0.8
            ),
            LaggedStartMap(
                ApplyMethod, pis,
                lambda pi: (pi.change, "pondering", screen_rects[0])
            ),
        )
        self.play(Blink(random.choice(pis)))
        self.play(LaggedStartMap(
            ApplyMethod, pis,
            lambda pi: (pi.change, "thinking", screen_rects[1])
        ))
        self.play(Blink(random.choice(pis)))
        self.wait()


class FinalQuote(Scene):
    def construct(self):
        quote_text = """
            A change of perspective\\\\
            is worth 80 IQ points.
        """
        quote_parts = [s for s in quote_text.split(" ") if s]
        quote = TextMobject(
            *quote_parts,
        )
        quote.scale(1.2)
        quote.shift(2 * RIGHT + UP)

        image = ImageMobject("AlanKay")
        image.set_height(6)
        image.to_corner(UL)
        image.shift(2 * LEFT + 0.5 * UP)
        name = TextMobject("Alan Kay")
        name.scale(1.5)
        name.next_to(image, DOWN)
        name.shift_onto_screen()

        self.play(
            FadeInFromDown(image),
            Write(name),
        )
        self.wait()

        for word in quote:
            self.play(ShowWord(word))
            self.wait(0.005 * len(word)**1.5)
        self.wait()


class EndScreen(PatreonEndScreen):
    CONFIG = {
        "specific_patrons": [
            "1stViewMaths",
            "Adam Kozak",
            "Adrian Robinson",
            "Alexis Olson",
            "Ali Yahya",
            "Andreas Benjamin Brössel",
            "Andrew Busey",
            "Ankalagon",
            "Antonio Juarez",
            "Arjun Chakroborty",
            "Art Ianuzzi",
            "Arthur Zey",
            "Awoo",
            "Bernd Sing",
            "Bob Sanderson",
            "Boris Veselinovich",
            "Brian Staroselsky",
            "Britt Selvitelle",
            "Burt Humburg",
            "Chad Hurst",
            "Charles Southerland",
            "Chris Connett",
            "Christian Kaiser",
            "Clark Gaebel",
            "Cooper Jones",
            "D. Sivakumar",
            "Danger Dai",
            "Dave B",
            "Dave Kester",
            "dave nicponski",
            "David Clark",
            "David Gow",
            "Delton Ding",
            "Devarsh Desai",
            "eaglle",
            "emptymachine",
            "Eric Younge",
            "Eryq Ouithaqueue",
            "Evan Phillips",
            "Federico Lebron",
            "Florian Chudigiewitsch",
            "Giovanni Filippi",
            "Graham",
            "Hal Hildebrand",
            "Hitoshi Yamauchi",
            "J",
            "j eduardo perez",
            "Jacob Magnuson",
            "Jameel Syed",
            "James Hughes",
            "Jan Pijpers",
            "Jason Hise",
            "Jeff Linse",
            "Jeff Straathof",
            "John Griffith",
            "John Haley",
            "John Shaughnessy",
            "John V Wertheim",
            "Jonathan Eppele",
            "Jonathan Wilson",
            "Jordan Scales",
            "Joseph John Cox",
            "Joseph Kelly",
            "Juan Benet",
            "Kai-Siang Ang",
            "Kanan Gill",
            "Kaustuv DeBiswas",
            "L0j1k",
            "Lee Redden",
            "Linh Tran",
            "Luc Ritchie",
            "Ludwig Schubert",
            "Lukas -krtek.net- Novy",
            "Lukas Biewald",
            "Magister Mugit",
            "Magnus Dahlström",
            "Magnus Lysfjord",
            "Mark B Bahu",
            "Mark Heising",
            "Mathew Bramson",
            "Mathias Jansson",
            "Matt Langford",
            "Matt Roveto",
            "Matt Russell",
            "Matthew Cocke",
            "Mauricio Collares",
            "Michael Faust",
            "Michael Hardel",
            "Mike Coleman",
            "Mustafa Mahdi",
            "Márton Vaitkus",
            "Nathan Jessurun",
            "Nero Li",
            "Omar Zrien",
            "Owen Campbell-Moore",
            "Peter Ehrnstrom",
            "Peter Mcinerney",
            "Quantopian",
            "Randy C. Will",
            "Richard Barthel",
            "Richard Burgmann",
            "Richard Comish",
            "Ripta Pasay",
            "Rish Kundalia",
            "Robert Teed",
            "Roobie",
            "Roy Larson",
            "Ryan Atallah",
            "Ryan Williams",
            "Samuel D. Judge",
            "Scott Gray",
            "Scott Walter, Ph.D.",
            "Sindre Reino Trosterud",
            "soekul",
            "Solara570",
            "Song Gao",
            "Stevie Metke",
            "Ted Suzman",
            "Tihan Seale",
            "Valeriy Skobelev",
            "Vassili Philippov",
            "Xavier Bernard",
            "Yana Chernobilsky",
            "Yaw Etse",
            "YinYangBalance.Asia",
            "Yu Jun",
            "Zach Cardwell",
        ],
    }


class ClacksSolution2Thumbnail(Scene):
    def construct(self):
        self.add_scene1()
        self.add_scene2()

        arrow = Arrow(
            self.block_word.get_top(),
            self.light_dot.get_bottom(),
            tip_length=0.75,
            rectangular_stem_width=0.2,
            color=RED,
            buff=0.5,
        )
        arrow.add_to_back(arrow.copy().set_stroke(BLACK, 20))
        self.add(arrow)
        return

        arrow = TexMobject("\\Updownarrow")
        arrow.set_height(2)
        arrow.set_color(YELLOW)
        arrow.set_stroke(Color("red"), 2, background=True)
        self.add(arrow)

    def add_scene1(self):
        scene1 = Thumbnail(
            sliding_blocks_config={
                "block1_config": {
                    "label_text": "$100^{d}$ kg",
                    "distance": 8,
                },
            }
        )
        group = Group(*scene1.mobjects)
        group.scale(0.75, about_point=ORIGIN)
        group.shift(1.5 * DOWN + 3 * LEFT)
        scene1.remove(scene1.question)
        self.add(*scene1.mobjects)

        black_rect = FullScreenFadeRectangle(fill_opacity=1)
        black_rect.shift(3.5 * UP)
        self.add(black_rect)

        word = TextMobject("Blocks")
        word.set_color(YELLOW)
        word.scale(3)
        word.to_corner(DR, buff=LARGE_BUFF)
        word.shift(0.5 * LEFT)
        self.block_word = word
        self.add(word)

    def add_scene2(self):
        scene2 = ReflectWorldThroughMirrorNew(
            skip_animations=True,
            file_writer_config={
                "write_to_movie": False,
            },
            end_at_animation_number=18,
            # center=1.5 * DOWN,
            center=ORIGIN,
        )
        worlds = VGroup(scene2.world, *scene2.reflected_worlds)
        mirrors = VGroup(*[rw[1] for rw in worlds])
        mirrors.set_stroke(width=5)
        triangles = VGroup(*[rw[0] for rw in worlds])
        trajectories = VGroup(
            scene2.trajectory,
            *scene2.reflected_trajectories
        )
        trajectories.set_stroke(YELLOW, 1)

        beams1, beams2 = [
            scene2.get_shooting_beam_anims(
                path,
                max_stroke_width=20,
                max_time_width=1,
                num_flashes=50,
            )
            for path in [
                scene2.trajectory,
                scene2.ghost_trajectory,
            ]
        ]
        beams = beams1 + beams2
        beams = beams2
        flashes = VGroup()
        for beam in beams:
            beam.update(0.5)
            flashes.add(beam.mobject)

        dot = self.light_dot = Dot(color=YELLOW, radius=0.1)
        dot.move_to(flashes[0].get_left())
        flashes.add(dot)

        self.add(triangles, mirrors)
        # self.add(randys)
        self.add(trajectories[0].set_stroke(width=2))
        self.add(flashes)

        word = TextMobject("Light beam")
        word.scale(3.5)
        word.set_color(YELLOW)
        # word.set_stroke(BLACK, 25, background=True)
        word.add_to_back(word.copy().set_stroke(
            BLACK, 25,
        ))
        word.next_to(dot, UR)
        word.shift(-word.get_center()[0] * RIGHT)
        word.shift(SMALL_BUFF * RIGHT)
        self.light_word = word
        self.add(word)
