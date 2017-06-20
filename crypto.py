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
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from topics.objects import *
from topics.probability import *
from topics.complex_numbers import *
from topics.common_scenes import *
from scene import Scene
from scene.reconfigurable_scene import ReconfigurableScene
from scene.zoomed_scene import *
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

#force_skipping
#revert_to_original_skipping_status

BITCOIN_COLOR = "#f7931a"

##################

class AskQuestion(Scene):
    CONFIG = {
        "time_per_char" : 0.06,
    }
    def construct(self):
        strings = [
            "What", "does", "it", "mean   ", "to", 
            "have    ", "a", "Bitcoin?"
        ]
        question = TextMobject(*strings)
        question.highlight_by_tex("have", YELLOW)
        self.dither()
        for word, part in zip(strings, question):
            n_chars = len(word.strip())
            n_spaces = len(word) - n_chars
            self.play(
                LaggedStart(FadeIn, part),
                run_time = self.time_per_char * len(word),
                rate_func = squish_rate_func(smooth, 0, 0.5)
            )
            self.dither(self.time_per_char*n_spaces)
        self.dither(2)

class BitcoinPaperHighlightTitle(ExternallyAnimatedScene):
    pass

class TimeBitcoinCover(ExternallyAnimatedScene):
    pass

class ListOfAttributes(Scene):
    def construct(self):
        logo = BitcoinLogo()

        digital = TextMobject("Digital")
        government, bank = buildings = [
            SVGMobject(
                file_name = "%s_building"%word,
                height = 2,
                fill_color = LIGHT_GREY,
                fill_opacity = 1,
                stroke_width = 0,
            )
            for word in "government", "bank"
        ]
        attributes = VGroup(digital, *buildings)
        attributes.arrange_submobjects(RIGHT, buff = LARGE_BUFF)
        for building in buildings:
            building.cross = Cross(building)
            building.cross.set_stroke(width = 12)

        self.play(DrawBorderThenFill(logo))
        self.play(
            logo.to_corner, UP+LEFT,
            Write(digital, run_time = 2)
        )
        for building in buildings:
            self.play(FadeIn(building))
            self.play(ShowCreation(building.cross))
        self.dither()

class UnknownAuthor(Scene):
    CONFIG = {
        "camera_config" : {
            "background_image" : "bitcoin_paper"
        }
    }
    def construct(self):
        rect = Rectangle(height = 0.4, width = 2.5)
        rect.shift(2.45*UP)
        question = TextMobject("Who is this?")
        question.next_to(rect, RIGHT, buff = 1.5)
        arrow = Arrow(question, rect, buff = SMALL_BUFF)
        VGroup(question, arrow, rect).highlight(RED_D)

        self.play(ShowCreation(rect))
        self.play(
            Write(question),
            ShowCreation(arrow)
        )
        self.dither()

class NameCryptoCurrencies(TeacherStudentsScene):
    def construct(self):
        words = TextMobject("It's called a", "``cryptocurrency''")
        words.highlight_by_tex("cryptocurrency", YELLOW)
        self.teacher_says(words)
        self.change_student_modes(*["pondering"]*3)
        self.dither()

class CryptocurrencyMarketCaps(ExternallyAnimatedScene):
    pass

class Hype(TeacherStudentsScene):
    def construct(self):
        self.teacher.change_mode("guilty")
        phrases = map(TextMobject, [
            "I want some!",
            "I'll get rich, right?",
            "Buy them all!"
        ])
        modes = ["hooray", "conniving", "surprised"]
        for student, phrase, mode in zip(self.students, phrases, modes):
            bubble = SpeechBubble()
            bubble.set_fill(BLACK, 1)
            bubble.add_content(phrase)
            bubble.resize_to_content()
            bubble.pin_to(student)
            bubble.add(phrase)
            self.play(
                student.change_mode, mode,
                FadeIn(bubble),
            )
        self.dither(3)

class AskQuestionCopy(AskQuestion):
    pass

class LedgerScene(PiCreatureScene):
    CONFIG = {
        "ledger_width" : 6,
        "ledger_height" : 7,
        "denomination" : "USD",
        "ledger_line_height" : 0.4,
    }
    def setup(self):
        PiCreatureScene.setup(self)
        self.remove(self.pi_creatures)

    def get_ledger(self):
        title = TextMobject("Ledger")
        rect = Rectangle(
            width = self.ledger_width, 
            height = self.ledger_height
        )
        title.next_to(rect.get_top(), DOWN)
        h_line = Line(rect.get_left(), rect.get_right())
        h_line.scale(0.8)
        h_line.set_stroke(width = 2)
        h_line.next_to(title, DOWN)
        content = VGroup(h_line)

        self.ledger = VGroup(rect, title, h_line, content)
        self.ledger.content = content
        self.ledger.to_corner(UP+LEFT)
        return self.ledger

    def add_line_to_ledger(self, string_or_mob):
        if isinstance(string_or_mob, str):
            mob = TextMobject(string_or_mob)
        elif isinstance(string_or_mob, Mobject):
            mob = string_or_mob
        else:
            raise Exception("Invalid input")

        mob.scale_to_fit_height(self.ledger_line_height)
        mob.next_to(
            self.ledger.content[-1], DOWN, 
            buff = MED_SMALL_BUFF, 
            aligned_edge = LEFT
        )
        self.ledger.content.add(mob)
        return mob

    def add_payment_line_to_ledger(self, from_name, to_name, amount):
        amount_str = str(amount)
        if self.denomination == "USD":
            amount_str = "\\$" + amount_str
        else:
            amount_str += " " + self.denomination
        line = TextMobject(
            from_name.capitalize(), 
            "pays" if from_name.lower() is not "you" else "pay",
            to_name.capitalize(),
            amount_str
        )
        for name in from_name, to_name:
            if hasattr(self, name.lower()):
                creature = getattr(self, name.lower())
                color = creature.get_color()
                line.highlight_by_tex(name.capitalize(), color)
        if self.denomination == "USD":
            line.highlight_by_tex(amount_str, GREEN_D)
        elif self.denomination == "BTC":
            line.highlight_by_tex(amount_str, BITCOIN_COLOR)

        return self.add_line_to_ledger(line)

    def animate_payment_addition(self, *args, **kwargs):
        line = self.add_payment_line_to_ledger(*args, **kwargs)
        self.play(LaggedStart(
            FadeIn, 
            VGroup(*line.family_members_with_points()),
            run_time = 1
        ))

    def get_network(self):
        creatures = self.pi_creatures
        lines = VGroup(*[
            Line(
                VGroup(pi1, pi1.label), VGroup(pi2, pi2.label),
                buff = MED_SMALL_BUFF,
                stroke_width = 2,
            )
            for pi1, pi2 in it.combinations(creatures, 2)
        ])
        labels = VGroup(*[pi.label for pi in creatures])

        return VGroup(creatures, labels, lines)

    def create_pi_creatures(self):
        creatures = VGroup(*[
            PiCreature(color = color, height = 1).shift(2*vect)
            for color, vect in zip(
                [BLUE_B, MAROON_D, GREY_BROWN, BLUE_E],
                [UP+LEFT, UP+RIGHT, DOWN+LEFT, DOWN+RIGHT],
            )
        ])
        creatures.to_edge(RIGHT)
        names = ["alice", "bob", "charlie", "you"]
        for name, creature in zip(names, creatures):
            setattr(self, name, creature)
            label = TextMobject(name.capitalize())
            label.scale(0.5)
            label.next_to(creature, DOWN)
            creature.label = label
            if (creature.get_center() - creatures.get_center())[0] > 0:
                creature.flip()
            creature.look_at(creatures.get_center())

        return creatures


class LayOutPlan(LedgerScene):
    def construct(self):
        self.ask_question()
        self.show_ledger()
        self.become_skeptical()

    def ask_question(self):
        btc = BitcoinLogo()
        group = VGroup(btc, TexMobject("= ???"))
        group.arrange_submobjects(RIGHT)

        self.play(
            DrawBorderThenFill(btc),
            Write(group[1], run_time = 2)
        )
        self.dither()
        self.play(
            group.scale, 0.7,
            group.next_to, ORIGIN, RIGHT,
            group.to_edge, UP
        )

    def show_ledger(self):
        network = self.get_network()
        ledger = self.get_ledger()
        payments = [
            ("Alice", "Bob", 20),
            ("Bob", "Charlie", 40),
            ("Alice", "You", 50),
        ]

        self.play(*map(FadeIn, [network, ledger]))
        for payment in payments:
            new_line = self.add_payment_line_to_ledger(*payment)
            from_name, to_name, amount = payment
            from_pi = getattr(self, from_name.lower())
            to_pi = getattr(self, to_name.lower())
            cash = TexMobject("\\$"*(amount/10))
            cash.scale(0.5)
            cash.move_to(from_pi)
            cash.highlight(GREEN)

            self.play(
                cash.move_to, to_pi,
                to_pi.change_mode, "hooray"
            )
            self.play(
                FadeOut(cash),
                Write(new_line, run_time = 1)
            )
            self.dither()

    def become_skeptical(self):
        creatures = self.pi_creatures

        self.play(*[
            ApplyMethod(pi.change_mode, "sassy")
            for pi in creatures
        ])
        for k in range(3):
            self.play(*[
                ApplyMethod(
                    creatures[i].look_at,
                    creatures[k*(i+1)%4]
                )
                for i in range(4)
            ])
        self.dither(2)

class UnderlyingSystemVsUserFacing(Scene):
    def construct(self):
        underlying = TextMobject("Underlying \\\\ system")
        underlying.shift(DOWN).to_edge(LEFT)
        user_facing = TextMobject("User-facing")
        user_facing.next_to(underlying, UP, LARGE_BUFF, LEFT)

        protocol = TextMobject("Bitcoin protocol")
        protocol.next_to(underlying, RIGHT, MED_LARGE_BUFF)
        protocol.highlight(BITCOIN_COLOR)
        banking = TextMobject("Banking system")
        banking.next_to(protocol, RIGHT, MED_LARGE_BUFF)
        banking.highlight(GREEN)

        phone = SVGMobject(
            file_name = "phone",
            fill_color = WHITE,
            fill_opacity = 1,
            height = 1,
            stroke_width = 0,
        )
        phone.next_to(protocol, UP, LARGE_BUFF)
        card = SVGMobject(
            file_name = "credit_card",
            fill_color = LIGHT_GREY,
            fill_opacity = 1,
            stroke_width = 0,
            height = 1
        )
        card.next_to(banking, UP, LARGE_BUFF)

        btc = BitcoinLogo()
        btc.next_to(phone, UP, MED_LARGE_BUFF)
        dollar = TexMobject("\\$")
        dollar.scale_to_fit_height(1)
        dollar.highlight(GREEN)
        dollar.next_to(card, UP, MED_LARGE_BUFF)
        card.save_state()
        card.shift(2*RIGHT)
        card.set_fill(opacity = 0)


        h_line = Line(underlying.get_left(), banking.get_right())
        h_line.next_to(underlying, DOWN, MED_SMALL_BUFF, LEFT)
        h_line2 = h_line.copy()
        h_line2.next_to(user_facing, DOWN, MED_LARGE_BUFF, LEFT)
        h_line3 = h_line.copy()
        h_line3.next_to(user_facing, UP, MED_LARGE_BUFF, LEFT)
        v_line = Line(5*UP, ORIGIN)
        v_line.next_to(underlying, RIGHT, MED_SMALL_BUFF)
        v_line.shift(1.7*UP)
        v_line2 = v_line.copy()
        v_line2.next_to(protocol, RIGHT, MED_SMALL_BUFF)
        v_line2.shift(1.7*UP)

        self.add(h_line, h_line2, h_line3, v_line, v_line2)
        self.add(underlying, user_facing, btc)
        self.play(Write(protocol))
        self.dither(2)
        self.play(
            card.restore,
            Write(dollar)
        )
        self.play(Write(banking))
        self.dither(2)
        self.play(DrawBorderThenFill(phone))
        self.dither(2)
        






























