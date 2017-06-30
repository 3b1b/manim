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

from hashlib import sha256
import binascii

#force_skipping
#revert_to_original_skipping_status

BITCOIN_COLOR = "#f7931a"

def get_cursive_name(name):
    result = TextMobject("\\normalfont\\calligra %s"%name)
    result.set_stroke(width = 0.5)
    return result

def sha256_bit_string(message):
    hexdigest = sha256(message).hexdigest()
    return bin(int(hexdigest, 16))[2:]

def sha256_tex_mob(message, n_forced_start_zeros = 0):
    line = TexMobject("0"*32)
    pre_result = VGroup(*[
        line.copy() for row in range(8)
    ])
    pre_result.arrange_submobjects(DOWN, buff = SMALL_BUFF)
    result = VGroup(*it.chain(*pre_result))
    result.scale(0.7)

    true_bit_string = sha256_bit_string(message)
    n = n_forced_start_zeros
    bit_string = "0"*n + true_bit_string[n:]
    for i, (bit, part) in enumerate(zip(bit_string, result)):
        if bit == "1":
            one = TexMobject("1")[0]
            one.replace(part, dim_to_match = 1)
            result.submobjects[i] = one

    return result

class TenDollarBill(VGroup):
    CONFIG = {
        "color" : GREEN,
        "height" : 0.5,
        "mark_paths_closed" : False,
    }
    def __init__(self, **kwargs):
        VGroup.__init__(self, **kwargs)
        rect = Rectangle(
            height = 2.61,
            width = 6.14,
            color = self.color,
            mark_paths_closed = False,
            fill_color = BLACK,
            fill_opacity = 1,
        )
        rect.scale_to_fit_height(self.height)
        oval = Circle()
        oval.stretch_to_fit_height(0.7*self.height)
        oval.stretch_to_fit_width(0.4*self.height)
        rect.add_subpath(oval.points)

        pi = Randolph(
            mode = "pondering",
            color = GREEN_B
        )
        pi.scale_to_fit_width(oval.get_width())
        pi.move_to(oval)
        pi.shift(0.1*pi.get_height()*DOWN)

        self.add(pi, rect)
        for vect in UP+LEFT, DOWN+RIGHT:
            ten = TexMobject("\\$10")
            ten.scale_to_fit_height(0.25*self.height)
            ten.next_to(self.get_corner(vect), -vect, SMALL_BUFF)
            ten.highlight(GREEN_C)
            self.add(ten)

class Broadcast(LaggedStart):
    CONFIG = {
        "small_radius" : 0.0,
        "big_radius" : 5,
        "n_circles" : 5,
        "remover" : True,
        "lag_ratio" : 0.7,
        "run_time" : 3,
    }
    def __init__(self, focal_point, **kwargs):
        digest_config(self, kwargs)
        circles = VGroup()
        for x in range(self.n_circles):
            circle = Circle(
                radius = self.big_radius, 
                stroke_color = BLACK,
                stroke_width = 0,
            )
            circle.move_to(focal_point)
            circle.save_state()
            circle.scale_to_fit_width(self.small_radius*2)
            circle.set_stroke(WHITE, 8)
            circles.add(circle)
        LaggedStart.__init__(
            self, 
            ApplyMethod, circles, 
            lambda c : (c.restore,),
            **kwargs
        )


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
        "sign_transactions" : False,
        "enumerate_lines" : False,
        "line_number_color" : YELLOW,
    }
    def setup(self):
        PiCreatureScene.setup(self)
        self.remove(self.pi_creatures)

    def add_ledger_and_network(self):
        self.add(self.get_ledger(), self.get_network())

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

        self.ledger = VGroup(rect, title, content)
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

        items = self.ledger.content

        mob.scale_to_fit_height(self.ledger_line_height)
        if self.enumerate_lines:
            num = TexMobject(str(len(items)) + ".")
            num.scale(0.8)
            num.highlight(self.line_number_color)
            num.next_to(mob, LEFT, MED_SMALL_BUFF)
            mob.add_to_back(num)
        mob.next_to(
            items[-1], DOWN, 
            buff = MED_SMALL_BUFF, 
            aligned_edge = LEFT
        )
        if self.enumerate_lines and len(items) == 1:
            mob.shift(MED_LARGE_BUFF * LEFT)
        items.add(mob)
        return mob

    def add_payment_line_to_ledger(self, from_name, to_name, amount):
        amount_str = str(amount)
        if self.denomination == "USD":
            amount_str = "\\$" + amount_str
        else:
            amount_str += " " + self.denomination
        line_tex_parts = [
            from_name.capitalize(), 
            "pays" if from_name.lower() != "you" else "pay",
            to_name.capitalize(),
            amount_str,
        ]
        if self.sign_transactions:
            line_tex_parts.append(self.get_signature_tex())
        line = TextMobject(*line_tex_parts)
        for name in from_name, to_name:
            color = self.get_color_from_name(name)
            line.highlight_by_tex(name.capitalize(), color)
        if self.sign_transactions:
            from_part = line.get_part_by_tex(from_name.capitalize())
            line[-1].highlight(from_part.get_color())

        amount_color = {
            "USD" : GREEN,
            "BTC" : BITCOIN_COLOR,
            "LD" : YELLOW,
        }.get(self.denomination, WHITE)
        line.highlight_by_tex(amount_str, amount_color)

        return self.add_line_to_ledger(line)

    def get_color_from_name(self, name):
        if hasattr(self, name.lower()):
            creature = getattr(self, name.lower())
            color = creature.get_color()
            if np.mean(color.get_rgb()) < 0.5:
                color = average_color(color, color, WHITE)
            return color
        return WHITE

    def animate_payment_addition(self, *args, **kwargs):
        line = self.add_payment_line_to_ledger(*args, **kwargs)
        self.play(LaggedStart(
            FadeIn, 
            VGroup(*it.chain(*line)),
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
        self.network = VGroup(creatures, labels, lines)
        self.network.lines = lines
        return self.network

    def create_pi_creatures(self):
        creatures = VGroup(*[
            PiCreature(color = color, height = 1).shift(2*vect)
            for color, vect in zip(
                [BLUE_C, MAROON_D, GREY_BROWN, BLUE_E],
                [UP+LEFT, UP+RIGHT, DOWN+LEFT, DOWN+RIGHT],
            )
        ])
        creatures.to_edge(RIGHT)
        names = self.get_names()
        for name, creature in zip(names, creatures):
            setattr(self, name, creature)
            label = TextMobject(name.capitalize())
            label.scale(0.75)
            label.next_to(creature, DOWN, SMALL_BUFF)
            creature.label = label
            if (creature.get_center() - creatures.get_center())[0] > 0:
                creature.flip()
            creature.look_at(creatures.get_center())

        return creatures

    def get_names(self):
        return ["alice", "bob", "charlie", "you"]

    def get_signature_tex(self):
        if not hasattr(self, "nonce"):
            self.nonce = 0
        binary = bin(hash(str(self.nonce)))[-8:]
        self.nonce += 1
        return binary + "\\dots"

    def get_signature(self, color = BLUE_C):
        result = TexMobject(self.get_signature_tex())
        result.highlight(color)
        return result

    def add_ellipsis(self):
        last_item = self.ledger.content[-1]
        dots = TexMobject("\\vdots")
        dots.next_to(last_item.get_left(), DOWN)
        last_item.add(dots)
        self.add(last_item)

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
        
class CryptoPrefix(Scene):
    def construct(self):
        cryptocurrency = TextMobject(
            "Crypto", "currency",
            arg_separator = ""
        )
        crypto = cryptocurrency.get_part_by_tex("Crypto")
        brace = Brace(crypto, UP)
        explanation = TextMobject(
            "Built using the math \\\\ from cryptography"
        )
        explanation.next_to(brace, UP)

        self.add(cryptocurrency)
        self.play(
            crypto.highlight, YELLOW,
            GrowFromCenter(brace)
        )
        self.play(Write(explanation))
        self.dither(3)

class IntroduceLedgerSystem(LedgerScene):
    CONFIG = {
        "payments" : [
            ("Alice", "Bob", 20),
            ("Bob", "Charlie", 40),
            ("Charlie", "You", 30),
            ("You", "Alice", 10),
        ]
    }
    def construct(self):
        self.add(self.get_network())
        self.exchange_money()
        self.add_ledger()
        self.tally_it_all_up()


    def exchange_money(self):
        for from_name, to_name, num in self.payments:
            from_pi = getattr(self, from_name.lower())
            to_pi = getattr(self, to_name.lower())
            cash = TexMobject("\\$"*(num/10)).highlight(GREEN)
            cash.scale_to_fit_height(0.5)
            cash.move_to(from_pi)
            self.play(
                cash.move_to, to_pi,
                to_pi.change_mode, "hooray"
            )
            self.play(FadeOut(cash))
        self.dither()

    def add_ledger(self):
        ledger = self.get_ledger()

        self.play(
            Write(ledger),
            *[
                ApplyMethod(pi.change, "pondering", ledger)
                for pi in self.pi_creatures
            ]
        )
        for payment in self.payments:
            self.animate_payment_addition(*payment)
        self.dither(3)

    def tally_it_all_up(self):
        accounts = dict()
        names = "alice", "bob", "charlie", "you"
        for name in names:
            accounts[name] = 0
        for from_name, to_name, amount in self.payments:
            accounts[from_name.lower()] -= amount
            accounts[to_name.lower()] += amount

        results = VGroup()
        debtors = VGroup()
        creditors = VGroup()
        for name in names:
            amount = accounts[name]
            creature = getattr(self, name)
            creature.cash = TexMobject("\\$"*abs(amount/10))
            creature.cash.next_to(creature, UP+LEFT, SMALL_BUFF)
            creature.cash.highlight(GREEN)
            if amount < 0:
                verb = "Owes"
                debtors.add(creature)
            else:
                verb = "Gets"
                creditors.add(creature)
            if name == "you":
                verb = verb[:-1]
            result = TextMobject(
                verb, "\\$%d"%abs(amount)
            )
            result.highlight_by_tex("Owe", RED)
            result.highlight_by_tex("Get", GREEN)
            result.add_background_rectangle()
            result.scale(0.7)
            result.next_to(creature.label, DOWN)
            results.add(result)

        brace = Brace(VGroup(*self.ledger.content[1:]), RIGHT)
        tally_up = brace.get_text("Tally up")
        tally_up.add_background_rectangle()

        self.play(
            GrowFromCenter(brace), 
            FadeIn(tally_up)
        )
        self.play(
            LaggedStart(FadeIn, results),
            *[
                ApplyMethod(pi.change, "happy")
                for pi in creditors
            ] + [
                ApplyMethod(pi.change, "plain")
                for pi in debtors
            ]
        )
        self.dither()
        debtor_cash, creditor_cash = [
            VGroup(*it.chain(*[pi.cash for pi in group]))
            for group in debtors, creditors
        ]
        self.play(FadeIn(debtor_cash))
        self.play(
            debtor_cash.arrange_submobjects, RIGHT, SMALL_BUFF,
            debtor_cash.move_to, self.pi_creatures,
        )
        self.dither()
        self.play(ReplacementTransform(
            debtor_cash, creditor_cash
        ))
        self.dither(2)

class InitialProtocol(Scene):
    def construct(self):
        self.add_title()
        self.show_first_two_items()

    def add_title(self):
        title = TextMobject("Protocol")
        title.scale(1.5)
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT).scale(4)
        h_line.next_to(title, DOWN)
        self.h_line = h_line
        self.title = title
        self.add(title, h_line)

    def show_first_two_items(self):
        items = VGroup(*map(self.get_new_item, [
            "Anyone can add lines to the Ledger",
            "Settle up with real money each month"
        ]))

        for item in items:
            self.dither()
            self.play(LaggedStart(FadeIn, item))
        self.dither(2)

    def get_new_item(self, item_string):
        item = TextMobject("$\\cdot$ %s"%item_string)
        if not hasattr(self, "items"):
            self.items = VGroup(item)
            self.items.next_to(self.h_line, DOWN, MED_LARGE_BUFF)
        else:
            item.next_to(self.items, DOWN, MED_LARGE_BUFF, LEFT)
            self.items.add(item)
        return item


class AddFraudulentLine(LedgerScene):
    def construct(self):
        self.add_ledger_and_network()
        self.bob_adds_lines()
        self.alice_reacts()

    def bob_adds_lines(self):
        line = self.add_payment_line_to_ledger("Alice", "Bob", 100)
        line.save_state()
        line.scale(0.001)
        line.move_to(self.bob)

        self.play(self.bob.change, "conniving")
        self.play(line.restore)
        self.dither()

    def alice_reacts(self):
        bubble = SpeechBubble(
            height = 1.5, width = 2, direction = LEFT,
        )
        bubble.next_to(self.alice, UP+RIGHT, buff = 0)
        bubble.write("Hey!")
        self.play(
            Animation(self.bob.pupils),
            self.alice.change, "angry",
            FadeIn(bubble),
            Write(bubble.content, run_time = 1)
        )
        self.dither(3)
        self.play(
            FadeOut(bubble),
            FadeOut(bubble.content),
            self.alice.change_mode, "pondering"
        )

class AnnounceDigitalSignatures(TeacherStudentsScene):
    def construct(self):
        words = TextMobject("Digital \\\\ signatures!")
        words.scale(1.5)
        self.force_skipping()
        self.teacher_says(
            words,
            target_mode = "hooray",
        )
        self.revert_to_original_skipping_status()

        self.change_student_modes(*["hooray"]*3)
        self.dither(2)

class IntroduceSignatures(LedgerScene):
    CONFIG = {
        "payments" : [
            ("Alice", "Bob", 100),
            ("Charlie", "You", 20),
            ("Bob", "You", 30),
        ],
    }
    def construct(self):
        self.add_ledger_and_network()
        self.add_transactions()
        self.add_signatures()

    def add_transactions(self):
        transactions = VGroup(*[
            self.add_payment_line_to_ledger(*payment)
            for payment in self.payments
        ])
        self.play(LaggedStart(FadeIn, transactions))
        self.dither()

    def add_signatures(self):
        signatures = VGroup(*[
            get_cursive_name(payments[0].capitalize())
            for payments in self.payments
        ])
        for signature, transaction in zip(signatures, self.ledger.content[1:]):
            signature.next_to(transaction, RIGHT)
            signature.highlight(transaction[0].get_color())
            self.play(Write(signature, run_time = 2))
            transaction.add(signature)
        self.dither(2)

        rect = SurroundingRectangle(self.ledger.content[1])
        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))
        self.dither()
        self.play(Indicate(signatures[0]))
        self.dither()

class AskHowDigitalSignaturesArePossible(TeacherStudentsScene):
    def construct(self):
        signature = get_cursive_name("Alice")
        signature.scale(1.5)
        signature.highlight(BLUE_C)
        signature.to_corner(UP+LEFT)
        signature_copy = signature.copy()
        signature_copy.shift(3*RIGHT)

        bits = TexMobject("01100001")
        bits.next_to(signature, DOWN)
        bits.shift_onto_screen()
        bits_copy = bits.copy()
        bits_copy.next_to(signature_copy, DOWN)


        self.add(signature)

        self.student_says(
            "Couldn't you just \\\\ copy the signature?",
            target_mode = "confused",
            run_time = 1
        )
        self.change_student_modes("pondering", "confused", "erm")
        self.play(LaggedStart(FadeIn, bits, run_time = 1))
        self.dither()
        self.play(ReplacementTransform(
            bits.copy(), bits_copy,
            path_arc = np.pi/2
        ))
        self.play(Write(signature_copy))
        self.dither(3)

class DescribeDigitalSignatures(LedgerScene):
    CONFIG = {
        "public_color" : GREEN,
        "private_color" : RED,
        "signature_color" : BLUE_C,
    }
    def construct(self):
        self.reorganize_pi_creatures()
        self.generate_key_pairs()
        self.keep_secret_key_secret()
        self.show_handwritten_signatures()
        self.show_digital_signatures()
        self.show_signing_functions()

    def reorganize_pi_creatures(self):
        self.pi_creatures.remove(self.you)
        creature_groups = VGroup(*[
            VGroup(pi, pi.label).scale(1.7)
            for pi in self.pi_creatures
        ])
        creature_groups.arrange_submobjects(RIGHT, buff = 2)
        creature_groups.to_edge(DOWN)
        self.add(creature_groups)
        for pi in self.pi_creatures:
            if pi.is_flipped():
                pi.flip()

    def generate_key_pairs(self):
        title = TextMobject("Private", "key /", "Public", "key")
        title.to_edge(UP)
        private, public = map(title.get_part_by_tex, ["Private", "Public"])
        private.highlight(self.private_color)
        public.highlight(self.public_color)
        secret = TextMobject("Secret")
        secret.move_to(private, RIGHT)
        secret.highlight(self.private_color)

        names = self.get_names()[:-1]
        public_key_strings = [
            bin(256+ord(name[0].capitalize()))[3:]
            for name in names
        ]
        private_key_strings = [
            bin(hash(name))[2:10]
            for name in names
        ]
        public_keys, private_keys = [
            VGroup(*[
                TextMobject(key_name+":"," $%s\\dots$"%key)
                for key in keys
            ])
            for key_name, keys in [
                ("pk", public_key_strings),
                ("sk", private_key_strings)
            ]
        ]
        key_pairs = [
            VGroup(*pair).arrange_submobjects(DOWN, aligned_edge = LEFT)
            for pair in zip(public_keys, private_keys)
        ]
        for key_pair, pi in zip(key_pairs, self.pi_creatures):
            key_pair.next_to(pi, UP, MED_LARGE_BUFF)
            for key in key_pair:
                key.highlight_by_tex("sk", self.private_color)
                key.highlight_by_tex("pk", self.public_color)

        self.play(Write(title, run_time = 2))
        self.play(ReplacementTransform(
            VGroup(VGroup(public.copy())),
            public_keys
        ))
        self.play(ReplacementTransform(
            VGroup(VGroup(private.copy())),
            private_keys
        ))
        self.dither()
        self.play(private.shift, DOWN)
        self.play(FadeIn(secret))
        self.play(FadeOut(private))
        self.dither()

        title.remove(private)
        title.add(secret)
        self.title = title
        self.private_keys = private_keys
        self.public_keys = public_keys

    def keep_secret_key_secret(self):
        keys = self.private_keys
        rects = VGroup(*map(SurroundingRectangle, keys))
        rects.highlight(self.private_color)
        lock = SVGMobject(
            file_name = "lock",
            height = rects.get_height(),
            fill_color = LIGHT_GREY,
            fill_opacity = 1,
            stroke_width = 0,
        )
        locks = VGroup(*[
            lock.copy().next_to(rect, LEFT, SMALL_BUFF)
            for rect in rects
        ])

        self.play(ShowCreation(rects))
        self.play(LaggedStart(DrawBorderThenFill, locks))
        self.dither()

        self.private_key_rects = rects
        self.locks = locks

    def show_handwritten_signatures(self):
        lines = VGroup(*[Line(LEFT, RIGHT) for x in range(5)])
        lines.arrange_submobjects(DOWN)
        last_line = lines[-1]
        last_line.scale(0.7, about_point = last_line.get_left())

        signature_line = lines[0].copy()
        signature_line.set_stroke(width = 2)
        signature_line.next_to(lines, DOWN, LARGE_BUFF)
        ex = TexMobject("\\times")
        ex.scale(0.7)
        ex.next_to(signature_line, UP, SMALL_BUFF, LEFT)
        lines.add(ex, signature_line)

        rect = SurroundingRectangle(
            lines, 
            color = LIGHT_GREY, 
            buff = MED_SMALL_BUFF
        )
        document = VGroup(rect, lines)
        documents = VGroup(*[
            document.copy()
            for x in range(2)
        ])
        documents.arrange_submobjects(RIGHT, buff = MED_LARGE_BUFF)
        documents.to_corner(UP+LEFT)

        signatures = VGroup()
        for document in documents:
            signature = get_cursive_name("Alice")
            signature.highlight(self.signature_color)
            line = document[1][-1]
            signature.next_to(line, UP, SMALL_BUFF)
            signatures.add(signature)

        self.play(
            FadeOut(self.title),
            LaggedStart(FadeIn, documents, run_time = 1)
        )
        self.play(Write(signatures))
        self.dither()

        self.signatures = signatures
        self.documents = documents

    def show_digital_signatures(self):
        rect = SurroundingRectangle(VGroup(
            self.public_keys[0],
            self.private_key_rects[0],
            self.locks[0]
        ))
        digital_signatures = VGroup()
        for i, signature in enumerate(self.signatures):
            bits = bin(hash(str(i)))[-8:]
            digital_signature = TexMobject(bits + "\\dots")
            digital_signature.scale(0.7)
            digital_signature.highlight(signature.get_color())
            digital_signature.move_to(signature, DOWN)
            digital_signatures.add(digital_signature)

        arrows = VGroup(*[
            Arrow(
                rect.get_corner(UP), sig.get_bottom(),
                tip_length = 0.15,
                color = WHITE
            )
            for sig in digital_signatures
        ])

        words = VGroup(*map(
            TextMobject,
            ["Different messages", "Completely different signatures"]
        ))
        words.arrange_submobjects(DOWN, aligned_edge = LEFT)
        words.scale(1.3)
        words.next_to(self.documents, RIGHT)

        self.play(FadeIn(rect))
        self.play(*map(ShowCreation, arrows))
        self.play(Transform(self.signatures, digital_signatures))
        self.play(*[
            ApplyMethod(pi.change, "pondering", digital_signatures)
            for pi in self.pi_creatures
        ])
        for word in words:
            self.play(FadeIn(word))
        self.dither()
        self.play(FadeOut(words))

    def show_signing_functions(self):
        sign = TextMobject(
            "Sign(", "Message", ", ", "sk", ") = ", "Signature",
            arg_separator = ""
        )
        sign.to_corner(UP+RIGHT)
        verify = TextMobject(
            "Verify(", "Message", ", ", "Signature", ", ", "pk", ") = ", "T/F",
            arg_separator = ""
        )
        for mob in sign, verify:
            mob.highlight_by_tex("sk", self.private_color)
            mob.highlight_by_tex("pk", self.public_color)
            mob.highlight_by_tex(
                "Signature", self.signature_color,
            )
            for name in "Message", "sk", "Signature", "pk":
                part = mob.get_part_by_tex(name)
                if part is not None:
                    setattr(mob, name.lower(), part)
        verify.next_to(sign, DOWN, MED_LARGE_BUFF, LEFT)
        VGroup(sign, verify).to_corner(UP+RIGHT)

        private_key = self.private_key_rects[0]
        public_key = self.public_keys[0]
        message = self.documents[0]
        signature = self.signatures[0]

        self.play(*[
            FadeIn(part)
            for part in sign
            if part not in [sign.message, sign.sk, sign.signature]
        ])
        self.play(ReplacementTransform(
            message.copy(), VGroup(sign.message)
        ))
        self.dither()
        self.play(ReplacementTransform(
            private_key.copy(), sign.sk
        ))
        self.dither()
        self.play(ReplacementTransform(
            VGroup(sign.sk, sign.message).copy(),
            VGroup(sign.signature)
        ))
        self.dither()
        self.play(Indicate(sign.sk))
        self.dither()
        self.play(Indicate(sign.message))
        self.dither()
        self.play(*[
            FadeIn(part)
            for part in verify
            if part not in [
                verify.message, verify.signature, 
                verify.pk, verify[-1]
            ]
        ])
        self.dither()
        self.play(
            ReplacementTransform(
                sign.message.copy(), verify.message
            ),
            ReplacementTransform(
                sign.signature.copy(), verify.signature
            )
        )
        self.dither()
        self.play(ReplacementTransform(
            public_key.copy(), VGroup(verify.pk)
        ))
        self.dither()
        self.play(Write(verify[-1]))
        self.dither()

class TryGuessingDigitalSignature(Scene):
    def construct(self):
        verify = TextMobject(
            "Verify(", "Message", ", ", 
            "256 bit Signature", ", ", "pk", ")",
            arg_separator = ""
        )
        verify.scale(1.5)
        verify.shift(DOWN)
        signature = verify.get_part_by_tex("Signature")
        verify.highlight_by_tex("Signature", BLUE)
        verify.highlight_by_tex("pk", GREEN)
        brace = Brace(signature, UP)

        zeros_row = TexMobject("0"*32)
        zeros = VGroup(*[zeros_row.copy() for x in range(8)])
        zeros.arrange_submobjects(DOWN, buff = SMALL_BUFF)
        zeros.next_to(brace, UP)

        self.add(verify)
        self.play(
            GrowFromCenter(brace),
            FadeIn(
                zeros,
                submobject_mode = "lagged_start",
                run_time = 3
            )
        )
        self.dither()
        for n in range(2**10):
            last_row = zeros[-1]
            binary = bin(n)[2:]
            for i, bit_str in enumerate(reversed(binary)):
                curr_bit = last_row.submobjects[-i-1]
                new_bit = TexMobject(bit_str)
                new_bit.replace(curr_bit, dim_to_match = 1)
                last_row.submobjects[-i-1] = new_bit
                self.remove(curr_bit)
            self.add(last_row)
            self.dither(1./30)

class SupplementVideoWrapper(Scene):
    def construct(self):
        title = TextMobject("How secure is 256 bit security?")
        title.scale(1.5)
        title.to_edge(UP)
        rect = ScreenRectangle(height = 6)
        rect.next_to(title, DOWN)
        self.add(title)
        self.play(ShowCreation(rect))
        self.dither()

class IncludeTransactionNumber(LedgerScene):
    CONFIG = {
        "ledger_width" : 7,
    }
    def construct(self):
        self.add_ledger_and_network()
        self.add_signed_payment()
        self.copy_payment_many_times()
        self.add_ids()

    def add_signed_payment(self):
        line = self.add_payment_line_to_ledger(
            "Alice", "Bob", 100
        )
        signature = self.get_signature()
        signature.next_to(line, RIGHT)
        signature.save_state()
        signature.scale(0.1)
        signature.move_to(self.alice)

        self.play(Write(line, run_time = 1))
        self.play(
            signature.restore,
            self.alice.change, "raise_left_hand"
        )
        self.dither()
        self.play(self.alice.change, "happy")
        self.dither()

        line.add(signature)

    def copy_payment_many_times(self):
        line = self.ledger.content[-1]
        copies = VGroup(*[line.copy() for x in range(4)])
        copies.arrange_submobjects(DOWN, buff = MED_SMALL_BUFF)
        copies.next_to(line, DOWN, buff = MED_SMALL_BUFF)

        self.play(
            LaggedStart(FadeIn, copies, run_time = 3),
            self.bob.change, "conniving",
        )
        self.play(self.alice.change, "angry")
        self.dither()

        self.copies = copies

    def add_ids(self):
        top_line = self.ledger.content[-1]
        lines = VGroup(top_line, *self.copies)
        numbers = VGroup()
        old_signatures = VGroup()
        new_signatures = VGroup()
        colors = list(Color(BLUE_B).range_to(GREEN_B, len(lines)))
        for i, line in enumerate(lines):
            number = TexMobject(str(i))
            number.scale(0.7)
            number.highlight(YELLOW)
            number.next_to(line, LEFT)
            numbers.add(number)
            line.add_to_back(number)
            old_signature = line[-1]
            new_signature = self.get_signature()
            new_signature.replace(old_signature)
            new_signature.highlight(colors[i])
            old_signatures.add(old_signature)
            new_signatures.add(VGroup(new_signature))
            line.remove(old_signature)

        self.play(
            Write(numbers),
            self.alice.change, "thinking"
        )
        self.play(FadeOut(old_signatures))
        self.play(ReplacementTransform(
            lines.copy(), new_signatures,
            submobject_mode = "lagged_start",
            run_time = 2,
        ))
        self.play(self.bob.change, "erm")
        self.dither(2)

class ProtocolWithDigitalSignatures(InitialProtocol):
    def construct(self):
        self.force_skipping()
        InitialProtocol.construct(self)
        self.revert_to_original_skipping_status()

        rect = SurroundingRectangle(self.items[-1])
        rect.highlight(RED)

        new_item = self.get_new_item(
            "Only signed transactions are valid"
        )
        new_item.highlight(YELLOW)

        self.play(Write(new_item))
        self.dither()
        self.play(ShowCreation(rect))
        self.dither()

class SignedLedgerScene(LedgerScene):
    CONFIG = {
        "sign_transactions" : True,
        "enumerate_lines" : True,
        "ledger_width" : 7.5,
    }

class CharlieRacksUpDebt(SignedLedgerScene):
    CONFIG = {
        "payments" : [
            ("Charlie", "Alice", 100),
            ("Charlie", "Bob", 200),
            ("Charlie", "You", 800),
            ("Charlie", "Bob", 600),
            ("Charlie", "Alice", 900),
        ],
    }
    def construct(self):
        self.add_ledger_and_network()
        lines = VGroup(*[
            self.add_payment_line_to_ledger(*payment)
            for payment in self.payments
        ])

        self.play(LaggedStart(
            FadeIn, lines, 
            run_time = 3,
            lag_ratio = 0.25
        ))
        self.play(*[
            ApplyMethod(pi.change, "sassy", self.charlie)
            for pi in self.pi_creatures
            if pi is not self.charlie
        ])
        self.play(
            self.charlie.shift, SPACE_WIDTH*RIGHT,
            rate_func = running_start
        )
        self.play(*[
            ApplyMethod(pi.change, "angry", self.charlie)
            for pi in self.get_pi_creatures()
        ])
        self.dither()

class ThinkAboutSettlingUp(Scene):
    def construct(self):
        randy = Randolph()
        randy.to_corner(DOWN+LEFT)

        self.play(PiCreatureBubbleIntroduction(
            randy, 
            "You don't \\emph{actually} \\\\" + \
            "need to settle up $\\dots$",
            bubble_class = ThoughtBubble,
            target_mode = "thinking"
        ))
        self.play(Blink(randy))
        self.dither()

class LedgerWithInitialBuyIn(SignedLedgerScene):
    def construct(self):
        self.add_ledger_and_network()
        self.everyone_buys_in()
        self.add_initial_lines()
        self.add_charlie_payments()
        self.point_out_charlie_is_broke()
        self.running_balance()

    def everyone_buys_in(self):
        center = self.network.get_center()
        moneys = VGroup(*[
            TexMobject("\\$100")
            for pi in self.pi_creatures
        ])
        moneys.highlight(GREEN)
        for pi, money in zip(reversed(self.pi_creatures), moneys):
            vect = pi.get_center() - center
            money.next_to(center, vect, SMALL_BUFF)
            money.add_background_rectangle()
            money.save_state()
            money.scale(0.01)
            corner = pi.get_corner(UP + np.sign(vect[0])*LEFT)
            money.move_to(corner)

        self.play(
            LaggedStart(
                ApplyMethod, moneys,
                lambda m : (m.restore,)
            ),
            self.charlie.change, "raise_right_hand",
            self.you.change, "raise_right_hand",
        )
        self.network.add(moneys)

    def add_initial_lines(self):
        lines = VGroup()
        for name in self.get_names():
            new_line = TextMobject(
                name.capitalize(), 
                "get" if name == "you" else "gets",
                "\\$100"
            )
            new_line.highlight_by_tex(
                name.capitalize(),
                self.get_color_from_name(name)
            )
            new_line.highlight_by_tex("100", GREEN)
            self.add_line_to_ledger(new_line)
            lines.add(new_line)
        line = Line(LEFT, RIGHT)
        line.scale_to_fit_width(self.ledger.get_width())
        line.scale_in_place(0.9)
        line.next_to(lines[-1], DOWN, SMALL_BUFF, LEFT)
        line.set_stroke(width = 1)
        lines[-1].add(line)

        self.play(
            LaggedStart(FadeIn, lines),
            *[
                ApplyMethod(pi.change, "thinking", self.ledger)
                for pi in self.pi_creatures
            ]
        )
        self.dither()

    def add_charlie_payments(self):
        payments = [
            ("Charlie", "Alice", 50),
            ("Charlie", "Bob", 50),
            ("Charlie", "You", 20),
        ]
        new_lines = VGroup(*[
            self.add_payment_line_to_ledger(*payment)
            for payment in payments
        ])

        for line in new_lines:
            self.play(Write(line, run_time = 1))
            self.dither()

    def point_out_charlie_is_broke(self):
        charlie_lines = VGroup(*[
            VGroup(*self.ledger.content[i][1:5])
            for i in 3, 5, 6, 7
        ])
        rects = VGroup(*[
            SurroundingRectangle(line)
            for line in charlie_lines
        ])
        rects.highlight(YELLOW)
        rects.set_stroke(width = 2)
        last_rect = rects[-1]
        last_rect.set_stroke(RED, 4)
        rects.remove(last_rect)
        invalid = TextMobject("Invalid")
        invalid.highlight(RED)
        invalid.next_to(last_rect, DOWN)

        self.play(ShowCreation(rects))
        self.play(self.charlie.change_mode, "guilty")
        self.dither()
        self.play(ShowCreation(last_rect))
        self.play(*[
            ApplyMethod(pi.change, "sassy", self.charlie)
            for pi in self.pi_creatures
            if pi is not self.charlie
        ])
        self.play(Write(invalid))
        self.dither(2)
        self.play(*map(FadeOut, [rects, last_rect, invalid]))

    def running_balance(self):
        charlie_lines = VGroup(*[
            VGroup(*self.ledger.content[i][1:5])
            for i in 3, 5, 6, 7
        ])
        signatures = VGroup(*[
            self.ledger.content[i][5]
            for i in 5, 6, 7
        ])
        rect = Rectangle(color = WHITE)
        rect.set_fill(BLACK, 0.8)
        rect.stretch_to_fit_height(self.ledger.get_height() - 2*MED_SMALL_BUFF)
        title = TextMobject("Charlie's running \\\\ balance")
        rect.stretch_to_fit_width(title.get_width() + 2*MED_SMALL_BUFF)
        rect.move_to(self.ledger.get_right())
        title.next_to(rect.get_top(), DOWN)
        balance = VGroup(rect, title)

        lines = VGroup(*map(TextMobject, [
            "\\$100", "\\$50", "\\$0", "Overdrawn"
        ]))
        lines.highlight(GREEN)
        lines[-1].highlight(RED)
        arrows = VGroup()
        for line, c_line in zip(lines, charlie_lines):
            line.next_to(rect.get_left(), RIGHT, LARGE_BUFF)
            line.shift(
                (c_line.get_center() - line.get_center())[1]*UP
            )
            arrow = Arrow(c_line, line)
            arrows.add(arrow)

        self.pi_creatures.remove(self.alice, self.charlie)
        self.play(
            FadeOut(signatures),
            FadeIn(balance)
        )
        self.play(
            LaggedStart(FadeIn, lines, run_time = 3),
            LaggedStart(ShowCreation, arrows, run_time = 3),
        )
        self.dither()

class RemovedConnectionBetweenLedgerAndCash(TeacherStudentsScene):
    def construct(self):
        ledger = Rectangle(
            height = 2, width = 1.5,
            color = WHITE
        )
        ledger_name = TextMobject("Ledger")
        ledger_name.scale_to_fit_width(ledger.get_width() - MED_SMALL_BUFF)
        ledger_name.next_to(ledger.get_top(), DOWN)
        ledger.add(ledger_name)

        arrow = TexMobject("\\leftrightarrow")
        cash = TexMobject("\\$\\$\\$")
        cash.highlight(GREEN)
        arrow.next_to(ledger, RIGHT)
        cash.next_to(arrow, RIGHT)
        group = VGroup(ledger, arrow, cash)
        group.next_to(self.teacher, UP+LEFT)

        self.add(group)
        self.play(
            Animation(group),
            self.teacher.change, "raise_right_hand"
        )
        self.play(
            arrow.shift, 2*UP,
            arrow.set_fill, None, 0
        )
        self.play(
            ledger.shift, LEFT, 
            cash.shift, RIGHT
        )
        self.change_student_modes(
            *["pondering"]*3,
            look_at_arg = ledger,
            added_anims = [self.teacher.change, "happy"]
        )
        self.dither(3)

class RenameToLedgerDollars(LedgerScene):
    CONFIG = {
        "payments" : [
            ("Alice", "Bob", 20),
            ("Charlie", "You", 80),
            ("Bob", "Charlie", 60),
            ("Bob", "Alice", 30),
            ("Alice", "You", 100),
        ],
        "enumerate_lines" : True,
        "line_number_color" : WHITE,
    }
    def construct(self):
        self.add(self.get_ledger())
        self.add_bubble()
        self.jump_in_to_middle()
        self.add_payments_in_dollars()
        self.rewrite_as_ledger_dollars()

    def add_bubble(self):
        randy = self.pi_creature
        bubble = SpeechBubble(direction = RIGHT)
        bubble.write("Who needs \\\\ cash?")
        bubble.resize_to_content()
        bubble.add(bubble.content)
        bubble.pin_to(randy)
        bubble.shift(MED_LARGE_BUFF*RIGHT)
        self.bubble = bubble

        self.add(randy, bubble)
        self.add_foreground_mobject(bubble)

    def jump_in_to_middle(self):
        h_line = self.ledger.content[0]
        dots = TexMobject("\\vdots")
        dots.next_to(h_line.get_left(), DOWN)
        h_line.add(dots)
        self.add(h_line)
        point = VectorizedPoint(h_line.get_corner(DOWN+LEFT))
        point.shift(MED_SMALL_BUFF*LEFT)
        self.ledger.content.add(*[
            point.copy()
            for x in range(103)
        ])

    def add_payments_in_dollars(self):
        lines = VGroup(*[
            self.add_payment_line_to_ledger(*payment)
            for payment in self.payments
        ])

        self.play(LaggedStart(
            FadeIn, lines,
            run_time = 4,
            lag_ratio = 0.3
        ))
        self.dither()

        self.payment_lines = lines

    def rewrite_as_ledger_dollars(self):
        curr_lines = self.payment_lines
        amounts = VGroup(*[line[4] for line in curr_lines])
        amounts.target = VGroup()
        for amount in amounts:
            dollar_sign = amount[0]
            amount.remove(dollar_sign)
            amount.add(dollar_sign)
            tex_string = amount.get_tex_string()
            ld = TextMobject(tex_string[2:] + " LD")
            ld.highlight(YELLOW)
            ld.scale(0.8)
            ld.move_to(amount, LEFT)
            amounts.target.add(ld)

        ledger_dollars = TextMobject("Ledger Dollars \\\\ ``LD'' ")
        ledger_dollars.highlight(YELLOW)
        ledger_dollars.next_to(self.ledger, RIGHT)

        self.play(
            Write(ledger_dollars),
            FadeOut(self.bubble),
            self.pi_creature.change, "thinking", ledger_dollars
        )
        self.play(MoveToTarget(amounts))
        self.dither(2)


    ###

    def create_pi_creatures(self):
        LedgerScene.create_pi_creatures(self)
        randy = Randolph(mode = "shruggie").flip()
        randy.to_corner(DOWN+RIGHT)
        return VGroup(randy)

class ExchangeCashForLedgerDollars(LedgerScene):
    CONFIG = {
        "sign_transactions" : True,
        "denomination" : "LD",
        "ledger_width" : 7.5,
        "ledger_height" : 6,
    }
    def construct(self):
        self.add_ledger_and_network()
        self.add_ellipsis()
        self.add_title()
        self.give_ten_dollar_bill()
        self.add_bob_pays_alice_line()
        self.everyone_thinks()

    def add_title(self):
        self.ledger.shift(DOWN)
        title = TextMobject(
            "Exchange", "LD", "for", "\\$\\$\\$"
        )
        title.highlight_by_tex("LD", YELLOW)
        title.highlight_by_tex("\\$", GREEN)
        title.scale(1.3)
        title.to_edge(UP).shift(LEFT)

        self.play(Write(title))
        self.dither()

    def give_ten_dollar_bill(self):
        bill = TenDollarBill()
        bill.next_to(self.alice.get_corner(UP+RIGHT), UP)
        bill.generate_target()
        bill.target.next_to(self.bob.get_corner(UP+LEFT), UP)

        arrow = Arrow(bill, bill.target, color = GREEN)

        small_bill = bill.copy()
        small_bill.scale(0.01, about_point = bill.get_bottom())

        self.play(
            ReplacementTransform(small_bill, bill),
            self.alice.change, "raise_right_hand"
        )
        self.play(ShowCreation(arrow))
        self.play(MoveToTarget(bill))
        self.play(self.bob.change, "happy", bill)
        self.dither()

    def add_bob_pays_alice_line(self):
        line = self.add_payment_line_to_ledger(
            "Bob", "Alice", 10
        )
        line.save_state()
        line.scale(0.01)
        line.move_to(self.bob.get_corner(UP+LEFT))
        self.play(self.bob.change, "raise_right_hand", line)
        self.play(line.restore, run_time = 2)
        self.dither()

    def everyone_thinks(self):
        self.play(*[
            ApplyMethod(pi.change, "thinking", self.ledger)
            for pi in self.pi_creatures
        ])
        self.dither(4)

class BitcoinIsALedger(Scene):
    def construct(self):
        self.add_btc_to_ledger()
        self.add_currency_to_tx_history()

    def add_btc_to_ledger(self):
        logo = BitcoinLogo()
        ledger = self.get_ledger()
        arrow = TexMobject("\\Leftrightarrow")
        group = VGroup(logo, arrow, ledger)
        group.arrange_submobjects(RIGHT)

        self.play(DrawBorderThenFill(logo))
        self.dither()
        self.play(
            Write(arrow),
            Write(ledger)
        )
        self.dither()

        self.btc_to_ledger = group

    def add_currency_to_tx_history(self):
        equation = TextMobject(
            "Currency", "=", "Transaction history"
        )
        equation.highlight_by_tex("Currency", BITCOIN_COLOR)
        equation.shift(
            self.btc_to_ledger[1].get_center() - \
            equation[1].get_center() + 2*UP
        )

        for part in equation:
            self.play(FadeIn(part))
        self.dither()

    def get_ledger(self):
        rect = Rectangle(height = 2, width = 1.5)
        title = TextMobject("Ledger")
        title.scale_to_fit_width(0.8*rect.get_width())
        title.next_to(rect.get_top(), DOWN, SMALL_BUFF)

        lines = VGroup(*[
            Line(LEFT, RIGHT)
            for x in range(8)
        ])
        lines.arrange_submobjects(DOWN, buff = SMALL_BUFF)
        lines.stretch_to_fit_width(title.get_width())
        lines.next_to(title, DOWN)
        return VGroup(rect, title, lines)

class DistributedLedgerScene(LedgerScene):
    def get_large_network(self):
        network = self.get_network()
        network.scale_to_fit_height(2*SPACE_HEIGHT - LARGE_BUFF)
        network.center()
        for pi in self.pi_creatures:
            pi.label.scale(0.8, about_point = pi.get_bottom())
        return network

    def get_distributed_ledgers(self):
        ledger = self.get_ledger()
        title = ledger[1]
        h_line = ledger.content
        title.scale_to_fit_width(0.7*ledger.get_width())
        title.next_to(ledger.get_top(), DOWN, MED_LARGE_BUFF)
        h_line.next_to(title, DOWN)
        added_lines = VGroup(*[h_line.copy() for x in range(5)])
        added_lines.arrange_submobjects(DOWN, buff = MED_LARGE_BUFF)
        added_lines.next_to(h_line, DOWN, MED_LARGE_BUFF)
        ledger.content.add(added_lines)

        ledgers = VGroup()
        for pi in self.pi_creatures:
            pi.ledger = ledger.copy()
            pi.ledger.scale_to_fit_height(pi.get_height())
            pi.ledger[0].highlight(pi.get_color())
            vect = pi.get_center()-self.pi_creatures.get_center()
            x_vect = vect[0]*RIGHT
            pi.ledger.next_to(pi, x_vect, SMALL_BUFF)
            ledgers.add(pi.ledger)
        return ledgers

    def add_large_network_and_distributed_ledger(self):
        self.add(self.get_large_network())
        self.add(self.get_distributed_ledgers())        

class TransitionToDistributedLedger(DistributedLedgerScene):
    CONFIG = {
        "sign_transactions" : True,
        "ledger_width" : 7.5,
        "ledger_height" : 6,
        "enumerate_lines" : True,
        "denomination" : "LD",
        "line_number_color" : WHITE,
        "ledger_line_height" : 0.35,
    }
    def construct(self):
        self.add_ledger_and_network()
        self.ledger.shift(DOWN)
        self.add_ellipsis()

        self.ask_where_is_ledger()
        self.add_various_payements()
        self.ask_who_controls_ledger()
        self.distribute_ledger()
        self.broadcast_transaction()
        self.ask_about_ledger_consistency()

    def ask_where_is_ledger(self):
        question = TextMobject("Where", "is", "this?!")
        question.highlight(RED)
        question.scale(1.5)
        question.next_to(self.ledger, UP)

        self.play(Write(question))
        self.dither()

        self.question = question

    def add_various_payements(self):
        payments = VGroup(*[
            self.add_payment_line_to_ledger(*payment)
            for payment in [
                ("Alice", "Bob", 20),
                ("Charlie", "You", 100),
                ("You", "Alice", 50),
                ("Bob", "You", 30),
            ]
        ])

        for payment in payments:
            self.play(LaggedStart(FadeIn, payment, run_time = 1))
            self.dither()

    def ask_who_controls_ledger(self):
        new_question = TextMobject("Who", "controls", "this?!")
        new_question.scale(1.3)
        new_question.move_to(self.question)
        new_question.highlight(RED)

        self.play(Transform(self.question, new_question))
        self.play(*[
            ApplyMethod(pi.change, "confused", new_question)
            for pi in self.pi_creatures
        ])
        self.dither(2)

    def distribute_ledger(self):
        ledger = self.ledger
        self.ledger_width = 6
        self.ledger_height = 7
        distribute_ledgers = self.get_distributed_ledgers()
        group = VGroup(self.network, distribute_ledgers)

        self.play(FadeOut(self.question))
        self.play(ReplacementTransform(
            VGroup(ledger), distribute_ledgers
        ))
        self.play(*[
            ApplyMethod(pi.change, "pondering", pi.ledger)
            for pi in self.pi_creatures
        ])
        self.play(
            group.scale_to_fit_height, 2*SPACE_HEIGHT - 2,
            group.center
        )
        self.dither(2)

    def broadcast_transaction(self):
        payment = TextMobject(
            "Alice", "pays", "Bob", "100 LD"
        )
        payment.highlight_by_tex("Alice", self.alice.get_color())
        payment.highlight_by_tex("Bob", self.bob.get_color())
        payment.highlight_by_tex("LD", YELLOW)
        payment.scale(0.75)
        payment.add_background_rectangle()
        payment_copies = VGroup(*[
            payment.copy().next_to(pi, UP)
            for pi in self.pi_creatures
        ])
        payment = payment_copies[0]

        self.play(
            self.alice.change, "raise_right_hand", payment,
            Write(payment, run_time = 2)
        )
        self.dither()
        self.play(
            ReplacementTransform(
                VGroup(payment), payment_copies, 
                run_time = 3,
                rate_func = squish_rate_func(smooth, 0.5, 1)
            ),
            Broadcast(self.alice.get_corner(UP+RIGHT)),
            self.alice.change, "happy"
        )
        self.dither()
        pairs = zip(payment_copies, self.pi_creatures)
        Scene.play(self, *it.chain(*[
            [
                pi.look_at, pi.ledger[-1],
                line.scale, 0.2,
                line.next_to, pi.ledger[-1], DOWN, SMALL_BUFF,
            ]
            for line, pi in pairs
        ]))
        self.dither(3)

        for line, pi in pairs:
            pi.ledger.add(line)

    def ask_about_ledger_consistency(self):
        ledgers = VGroup(*[
            pi.ledger
            for pi in self.pi_creatures
        ])

        self.play(
            FadeOut(self.network),
            ledgers.scale, 2,
            ledgers.arrange_submobjects, RIGHT,
            ledgers.space_out_submobjects,
        )

        question = TextMobject("Are these the same?")
        question.scale(1.5)
        question.to_edge(UP)
        arrows = VGroup(*[
            Arrow(question.get_bottom(), ledger.get_top())
            for ledger in ledgers
        ])

        self.play(*map(ShowCreation, arrows))
        self.play(Write(question))
        self.dither()

class BobDoubtsBroadcastTransaction(DistributedLedgerScene):
    def construct(self):
        self.setup_bob_and_charlie()
        self.bob_receives_transaction()
        self.bob_tries_to_pay_charlie()

    def setup_bob_and_charlie(self):
        bob, charlie = self.bob, self.charlie
        self.pi_creatures = VGroup(bob, charlie)
        for pi in self.pi_creatures:
            pi.flip()
        self.pi_creatures.scale(2)
        self.pi_creatures.arrange_submobjects(RIGHT, buff = 5)

        for name in "bob", "charlie":
            label = TextMobject(name.capitalize())
            pi = getattr(self, name)
            label.next_to(pi, DOWN)
            pi.label = label
        bob.make_eye_contact(charlie)

        self.get_distributed_ledgers()

        self.add(bob, bob.label, bob.ledger)

    def bob_receives_transaction(self):
        bob, charlie = self.bob, self.charlie
        corner = SPACE_HEIGHT*UP + SPACE_WIDTH*LEFT

        payment = TextMobject(
            "Alice", "pays", "Bob", "10 LD"
        )
        payment.highlight_by_tex("Alice", self.alice.get_color())
        payment.highlight_by_tex("Bob", self.bob.get_color())
        payment.highlight_by_tex("LD", YELLOW)
        payment.next_to(corner, UP+LEFT)

        self.play(
            Broadcast(corner),
            ApplyMethod(
                payment.next_to, bob, UP,
                run_time = 3,
                rate_func = squish_rate_func(smooth, 0.3, 1)
            ),
        )
        self.play(bob.look_at, payment)
        self.play(
            payment.scale, 0.3,
            payment.next_to, bob.ledger[-1], DOWN, SMALL_BUFF
        )

    def bob_tries_to_pay_charlie(self):
        bob, charlie = self.bob, self.charlie
        chralie_group = VGroup(
            charlie, charlie.label, charlie.ledger
        )

        self.play(
            PiCreatureSays(
                bob, "Did you hear that?",
                target_mode = "sassy"
            ),
            FadeIn(chralie_group)
        )
        self.play(charlie.change, "maybe", bob.eyes)
        self.dither(2)

class YouListeningToBroadcasts(LedgerScene):
    CONFIG = {
        "denomination" : "LD"
    }
    def construct(self):
        ledger = self.get_ledger()
        payments = VGroup(*[
            self.add_payment_line_to_ledger(*payment)
            for payment in [
                ("Alice", "You", 20),
                ("Bob", "You", 50),
                ("Charlie", "You", 30),
            ]
        ])
        self.remove(self.ledger)
        corners = [
            SPACE_WIDTH*RIGHT*u1 + SPACE_HEIGHT*UP*u2
            for u1, u2 in (-1, 1), (1, 1), (-1, -1)
        ]
        you = self.you
        you.scale(2)
        you.center()

        self.add(you)
        for payment, corner in zip(payments, corners):
            vect = corner/np.linalg.norm(corner)
            payment.next_to(corner, vect)
            self.play(
                Broadcast(corner),
                ApplyMethod(
                    payment.next_to, you, vect,
                    run_time = 3,
                    rate_func = squish_rate_func(smooth, 0.3, 1)
                ),
                you.change_mode, "pondering"
            )
        self.dither()

class AskWhatToAddToProtocol(InitialProtocol):
    def construct(self):
        self.add_title()
        items = VGroup(*map(self.get_new_item, [
            "Broadcast transactions",
            "Only accept signed transactions",
            "No overspending",
        ] + [""]*6))
        brace = Brace(VGroup(*items[3:]), LEFT)
        question = TextMobject("What to \\\\ add here?")
        question.highlight(RED)
        question.scale(1.5)
        brace.highlight(RED)
        question.next_to(brace, LEFT)

        self.add(*items[:3])
        self.play(GrowFromCenter(brace))
        self.play(Write(question))
        self.dither()

class TrustComputationalWork(DistributedLedgerScene):
    def construct(self):
        self.add_ledger()
        self.show_work()

    def add_ledger(self):
        ledgers = self.get_distributed_ledgers()
        ledger = ledgers[0]
        ledger.scale(3)
        ledger[1].scale_in_place(2./3)
        ledger.center().to_edge(UP).shift(4*LEFT)
        plus = TexMobject("+")
        plus.next_to(ledger, RIGHT)

        self.add(ledger, plus)
        self.ledger = ledger
        self.plus = plus

    def show_work(self):
        zeros = TexMobject("0"*32)
        zeros.next_to(self.plus, RIGHT)
        brace = Brace(zeros, DOWN)
        words = brace.get_text("Computational work")
        self.add(brace, words)

        for n in range(2**12):
            binary = bin(n)[2:]
            for i, bit_str in enumerate(reversed(binary)):
                curr_bit = zeros.submobjects[-i-1]
                new_bit = TexMobject(bit_str)
                new_bit.replace(curr_bit, dim_to_match = 1)
                if bit_str == "1":
                    new_bit.highlight(YELLOW)
                zeros.submobjects[-i-1] = new_bit
                self.remove(curr_bit)
            self.add(zeros)
            self.dither(1./30)

class TrustComputationalWorkSupplement(Scene):
    def construct(self):
        words = TextMobject(
            "Main tool: ", "Cryptographic hash functions"
        )
        words[1].highlight(YELLOW)
        self.add(words[0])
        self.play(Write(words[1]))
        self.dither()

class ThisIsWellIntoTheWeeds(TeacherStudentsScene):
    def construct(self):
        idea = TextMobject("Proof of work")
        idea.move_to(self.teacher.get_corner(UP+LEFT))
        idea.shift(MED_LARGE_BUFF*UP)
        idea.save_state()
        lightbulb = Lightbulb()
        lightbulb.next_to(idea, UP)
        idea.shift(DOWN)
        idea.set_fill(opacity = 0)

        self.teacher_says(
            "We're well into \\\\ the weeds now",
            target_mode = "sassy",
            added_anims = [
                ApplyMethod(pi.change, mode)
                for pi, mode in zip(self.students, [
                    "hooray", "sad", "erm"
                ])
            ],
        )
        self.dither()
        self.play(
            idea.restore,
            RemovePiCreatureBubble(
                self.teacher, target_mode = "hooray",
                look_at_arg = lightbulb
            ),
        )
        self.change_student_modes(
            *["pondering"]*3,
            added_anims = [LaggedStart(FadeIn, lightbulb)]
        )
        self.play(LaggedStart(
            ApplyMethod, lightbulb,
            lambda b : (b.highlight, YELLOW_A),
            rate_func = there_and_back
        ))
        self.dither(2)

class IntroduceSHA256(Scene):
    def construct(self):
        self.introduce_evaluation()
        self.inverse_function_question()
        self.issue_challenge()
        self.shift_everything_down()
        self.guess_and_check()

    def introduce_evaluation(self):
        messages = [
            "3Blue1Brown",
            "3Blue1Crown",
            "Mathologer",
            "Infinite Series",
            "Numberphile",
            "Welch Labs",
            "3Blue1Brown",
        ]
        groups = VGroup()
        for message in messages:
            lhs = TextMobject(
                "SHA256", "(``", message, "'') =",
                arg_separator = ""
            )
            lhs.highlight_by_tex(message, BLUE)
            digest = sha256_tex_mob(message)
            digest.next_to(lhs, RIGHT)
            group = VGroup(lhs, digest)
            group.to_corner(UP+RIGHT)
            group.shift(MED_LARGE_BUFF*DOWN)
            groups.add(group)

        group = groups[0]
        lhs, digest = group
        sha, lp, message, lp = lhs
        sha_brace = Brace(sha, UP)
        message_brace = Brace(message, DOWN)
        digest_brace = Brace(digest, DOWN)
        sha_text = sha_brace.get_text("", "Hash function")
        sha_text.highlight(YELLOW)
        message_text = message_brace.get_text("Message/file")
        message_text.highlight(BLUE)
        digest_text = digest_brace.get_text("``Hash'' or ``Digest''")
        brace_text_pairs = [
            (sha_brace, sha_text),
            (message_brace, message_text),
            (digest_brace, digest_text),
        ]   

        self.add(group)
        for brace, text in brace_text_pairs:
            self.play(
                GrowFromCenter(brace),
                Write(text, run_time = 2)
            )
            self.dither()
        self.dither()
        for mob in digest, message:
            self.play(LaggedStart(
                ApplyMethod, mob,
                lambda m : (m.highlight, YELLOW),
                rate_func = there_and_back,
                run_time = 1
            ))
        self.dither()

        new_lhs, new_digest = groups[1]
        char = new_lhs[2][-5]
        arrow = Arrow(UP, ORIGIN, buff = 0)
        arrow.next_to(char, UP)
        arrow.highlight(RED)
        self.play(ShowCreation(arrow))
        for new_group in groups[1:]:
            new_lhs, new_digest = new_group
            new_message = new_lhs[2]
            self.play(
                Transform(lhs, new_lhs),
                message_brace.stretch_to_fit_width, new_message.get_width(),
                message_brace.next_to, new_message, DOWN,
                MaintainPositionRelativeTo(message_text, message_brace),
                MaintainPositionRelativeTo(sha_brace, lhs[0]),
                MaintainPositionRelativeTo(sha_text, sha_brace)
            )
            self.play(Transform(
                digest, new_digest,
                run_time = 2,
                submobject_mode = "lagged_start",
                path_arc = np.pi/2
            ))
            if arrow in self.get_mobjects():
                self.dither()
                self.play(FadeOut(arrow))
        self.dither()

        new_sha_text = TextMobject(
            "Cryptographic", "hash function"
        )
        new_sha_text.next_to(sha_brace, UP)
        new_sha_text.shift_onto_screen()
        new_sha_text.highlight(YELLOW)
        new_sha_text[0].highlight(GREEN)
        self.play(Transform(sha_text, new_sha_text))
        self.dither()

        self.lhs = lhs
        self.message = message
        self.digest = digest
        self.digest_text = digest_text
        self.message_text = message_text

    def inverse_function_question(self):
        arrow = Arrow(3*RIGHT, 3*LEFT, buff = 0)
        arrow.set_stroke(width = 8)
        arrow.highlight(RED)
        everything = VGroup(*self.get_mobjects())
        arrow.next_to(everything, DOWN)
        words = TextMobject("Inverse is infeasible")
        words.highlight(RED)
        words.next_to(arrow, DOWN)

        self.play(ShowCreation(arrow))
        self.play(Write(words))
        self.dither()

    def issue_challenge(self):
        desired_output_text = TextMobject("Desired output")
        desired_output_text.move_to(self.digest_text)
        desired_output_text.highlight(YELLOW)
        new_digest = sha256_tex_mob("Challenge")
        new_digest.replace(self.digest)
        q_marks = TextMobject("???")
        q_marks.move_to(self.message_text)
        q_marks.highlight(BLUE)

        self.play(
            Transform(
                self.digest, new_digest,
                run_time = 2,
                submobject_mode = "lagged_start",
                path_arc = np.pi/2
            ),
            Transform(self.digest_text, desired_output_text)
        )
        self.play(
            FadeOut(self.message),
            Transform(self.message_text, q_marks)
        )
        self.dither()

    def shift_everything_down(self):
        everything = VGroup(*self.get_top_level_mobjects())
        self.play(
            everything.scale, 0.85,
            everything.to_edge, DOWN
        )

    def guess_and_check(self):
        groups = VGroup()
        for x in range(32):
            message = "Guess \\#%d"%x
            lhs = TextMobject(
                "SHA256(``", message, "'') = ",
                arg_separator = ""
            )
            lhs.highlight_by_tex("Guess", BLUE)
            digest = sha256_tex_mob(message)
            digest.next_to(lhs, RIGHT)
            group = VGroup(lhs, digest)
            group.scale(0.85)
            group.next_to(self.digest, UP, aligned_edge = RIGHT)
            group.to_edge(UP)
            groups.add(group)

        group = groups[0]
        self.play(FadeIn(group))
        for new_group in groups[1:]:
            self.play(Transform(
                group[0], new_group[0],
                run_time = 0.5,
            ))
            self.play(Transform(
                group[1], new_group[1],
                run_time = 1,
                submobject_mode = "lagged_start"
            ))

class PonderScematic(Scene):
    def construct(self):
        randy = Randolph()
        randy.to_corner(DOWN+LEFT)
        self.play(randy.change, "confused", ORIGIN)
        for x in range(3):
            self.play(Blink(randy))
            self.dither(2)

class ViewingSLLCertificate(ExternallyAnimatedScene):
    pass

class SHA256ToProofOfWork(TeacherStudentsScene):
    def construct(self):
        sha = TextMobject("SHA256")
        proof = TextMobject("Proof of work")
        arrow = Arrow(LEFT, RIGHT)
        group = VGroup(sha, arrow, proof)
        group.arrange_submobjects(RIGHT)
        group.next_to(self.teacher, UP, buff = LARGE_BUFF)
        group.to_edge(RIGHT, buff = LARGE_BUFF)

        self.play(
            Write(sha, run_time = 1),
            self.teacher.change, "raise_right_hand"
        )
        self.play(ShowCreation(arrow))
        self.play(Write(proof, run_time = 1))
        self.dither(3)

class IntroduceNonceOnTrasactions(LedgerScene):
    CONFIG = {
        "denomination" : "LD",
        "ledger_width" : 5,
        "ledger_line_height" : 0.3,
    }
    def construct(self):
        self.add(self.get_ledger())
        self.hash_with_nonce()
        self.write_probability()
        self.guess_and_check()
        self.name_proof_of_work()
        self.change_ledger()
        self.guess_and_check()

    def hash_with_nonce(self):
        ledger = self.ledger
        self.add(*[
            self.add_payment_line_to_ledger(*payment)
            for payment in [
                ("Alice", "Bob", 20),
                ("Alice", "You", 30),
                ("Charlie", "You", 100),
            ]
        ])

        nonce = TexMobject(str(2**30 + hash("Hey there")%(2**15)))
        nonce.next_to(ledger, RIGHT, LARGE_BUFF)
        nonce.highlight(GREEN_C)
        nonce_brace = Brace(nonce, DOWN)
        special_word = nonce_brace.get_text("Special number")
        arrow = Arrow(LEFT, RIGHT, buff = 0)
        arrow.next_to(ledger, RIGHT)
        arrow.shift(MED_LARGE_BUFF*DOWN)
        sha = TextMobject("SHA256")
        sha.next_to(arrow, UP)
        digest = sha256_tex_mob(
            """Man, you're reading this deeply into
            the code behind videos?  I'm touched,
            really touched.  Keeping loving math, my
            friend. """,
            n_forced_start_zeros = 30,
        )
        digest.next_to(arrow, RIGHT)
        zeros = VGroup(*digest[:30])
        zeros_brace = Brace(zeros, UP)
        zeros_words = zeros_brace.get_text("30 zeros")

        self.play(LaggedStart(
            FadeIn, VGroup(special_word, nonce_brace, nonce)
        ))
        self.dither()
        self.play(
            nonce.next_to, ledger.content, DOWN, MED_SMALL_BUFF, LEFT,
            FadeOut(special_word),
            FadeOut(nonce_brace)
        )
        ledger.content.add(nonce)
        decomposed_ledger = VGroup(*filter(
            lambda m : not m.is_subpath,
            ledger.family_members_with_points()
        ))
        self.play(
            ShowCreation(arrow),
            FadeIn(sha)
        )
        self.play(LaggedStart(
            ApplyMethod, decomposed_ledger,
            lambda m : (m.highlight, YELLOW),
            rate_func = there_and_back
        ))
        point = VectorizedPoint(sha.get_center())
        point.set_fill(opacity = 1)
        self.play(LaggedStart(
            Transform, decomposed_ledger.copy(),
            lambda m : (m, point),
            run_time = 1
        ))
        bit_iter = iter(digest)
        self.play(LaggedStart(
            ReplacementTransform, 
            VGroup(*[point.copy() for x in range(256)]),
            lambda m : (m, bit_iter.next()),
        ))
        self.remove(*self.get_mobjects_from_last_animation())
        self.add(digest)
        self.play(
            GrowFromCenter(zeros_brace),
            Write(zeros_words, run_time = 1)
        )
        self.play(LaggedStart(
            ApplyMethod, zeros,
            lambda m : (m.highlight, YELLOW)
        ))
        self.dither(2)

        self.nonce = nonce
        self.digest = digest
        self.zeros_brace = zeros_brace
        self.zeros_words = zeros_words

    def write_probability(self):
        probability = TextMobject(
            "Probability: $\\frac{1}{2^{30}}$",
            "$\\approx \\frac{1}{1{,}000{,}000{,}000}$",
        )
        probability.next_to(self.zeros_words, UP, MED_LARGE_BUFF)

        self.play(FadeIn(probability[0]))
        self.dither()
        self.play(Write(probability[1], run_time = 2))
        self.dither(2)

    def guess_and_check(self):
        q_mark = TexMobject("?")
        q_mark.highlight(RED)
        q_mark.next_to(self.zeros_words, RIGHT, SMALL_BUFF)

        self.digest.save_state()
        self.nonce.save_state()

        self.play(FadeIn(q_mark))
        for x in range(1, 13):
            nonce = TexMobject(str(x))
            nonce.move_to(self.nonce)
            nonce.highlight(GREEN_C)
            digest = sha256_tex_mob(str(x))
            digest.replace(self.digest)

            self.play(Transform(
                self.nonce, nonce,
                run_time = 1 if x == 1 else 0.3
            ))
            self.play(Transform(
                self.digest, digest,
                run_time = 1,
                submobject_mode = "lagged_start"
            ))
        self.dither()
        self.play(self.nonce.restore)
        self.play(
            self.digest.restore, 
            submobject_mode = "lagged_start",
            run_time = 2
        )
        self.play(FadeOut(q_mark))
        self.dither()

    def name_proof_of_work(self):
        words = TextMobject("``Proof of work''")
        words.next_to(self.nonce, DOWN, LARGE_BUFF)
        words.shift(MED_LARGE_BUFF*RIGHT)
        words.highlight(GREEN)
        arrow = Arrow(
            words.get_top(), self.nonce.get_bottom(),
            color = WHITE,
            tip_length = 0.15
        )
        self.play(Write(words, run_time = 2))
        self.play(ShowCreation(arrow))
        self.dither()

    def change_ledger(self):
        amount = self.ledger.content[2][-1]
        new_amount = TextMobject("300 LD")
        new_amount.scale_to_fit_height(amount.get_height())
        new_amount.highlight(amount.get_color())
        new_amount.move_to(amount, LEFT)

        new_digest = sha256_tex_mob("Ah shucks")
        new_digest.replace(self.digest)

        dot = Dot(amount.get_center())
        dot.set_fill(opacity = 0.5)

        self.play(FocusOn(amount))
        self.play(Transform(amount, new_amount))
        self.play(
            dot.move_to, new_digest,
            dot.set_fill, None, 0
        )
        self.play(Transform(
            self.digest, new_digest,
            submobject_mode = "lagged_start",
        ))

class ShowSomeBroadcasting(DistributedLedgerScene):
    def construct(self):
        self.add_large_network_and_distributed_ledger()
        lines = self.network.lines.copy()
        lines.add(*[
            line.copy().rotate(np.pi)
            for line in lines
        ])

        point = VectorizedPoint(self.pi_creatures.get_center())
        last_pi = None
        for pi in self.pi_creatures:
            outgoing_lines = []
            for line in lines:
                vect = line.get_start() - pi.get_center()
                dist = np.linalg.norm(vect)
                if dist < 2:
                    outgoing_lines.append(line)
            dots = VGroup()
            for line in outgoing_lines:
                dot = Dot(line.get_start())
                dot.highlight(YELLOW)
                dot.generate_target()
                dot.target.move_to(line.get_end())
                for alt_pi in self.pi_creatures:
                    vect = line.get_end() - alt_pi.get_center()
                    dist = np.linalg.norm(vect)
                    if dist < 2:
                        dot.ledger = alt_pi.ledger
                dots.add(dot)
            self.play(
                Animation(point),
                Broadcast(pi),
                *[
                    Succession(
                        FadeIn(dot),
                        MoveToTarget(dot, run_time = 2),
                    )
                    for dot in dots
                ]
            )
            self.play(*it.chain(*[
                [dot.move_to, dot.ledger, dot.set_fill, None, 0]
                for dot in dots
            ]))

class IntroduceBlockChain(Scene):
    CONFIG = {
        "transaction_color" : YELLOW,
        "proof_of_work_color" : GREEN,
        "prev_hash_color" : BLUE,
        "block_width" : 3,
        "block_height" : 3.5,
        "n_transaction_lines" : 8,
        "payment_height_to_block_height" : 0.15,
    }
    def setup(self):
        ls = LedgerScene()
        self.names = [
            name.capitalize()
            for name in ls.get_names()
        ]
        self.name_colors = [
            ls.get_color_from_name(name)
            for name in self.names
        ]

    def construct(self):
        self.divide_ledger_into_blocks()
        self.show_proofs_of_work()
        self.chain_blocks_together()
        self.mess_with_early_block()
        self.propogate_hash_change()
        self.redo_proof_of_work()
        self.write_block_chain()


    def divide_ledger_into_blocks(self):
        blocks = VGroup(*[
            self.get_block() for x in range(3)
        ])
        blocks.arrange_submobjects(RIGHT, buff = 1.5)
        blocks.to_edge(UP)

        all_payments = VGroup()
        all_proofs_of_work = VGroup()
        for block in blocks:
            block.remove(block.prev_hash)
            all_payments.add(*block.payments)
            all_proofs_of_work.add(block.proof_of_work)

        blocks_word = TextMobject("Blocks")
        blocks_word.scale(1.5)
        blocks_word.shift(2*DOWN)
        arrows = VGroup(*[
            Arrow(
                blocks_word.get_top(), block.get_bottom(),
                buff = MED_LARGE_BUFF,
                color = WHITE
            )
            for block in blocks
        ])

        self.play(LaggedStart(FadeIn, blocks))
        self.play(
            Write(blocks_word),
            LaggedStart(
                ShowCreation, arrows, 
                run_time = 1,
                lag_factor = 0.6,
            )
        )
        self.dither()
        for group in all_payments, all_proofs_of_work:
            self.play(LaggedStart(
                Indicate, group,
                rate_func = there_and_back,
                scale_factor = 1.1,
            ))
        self.play(*map(FadeOut, [blocks_word, arrows]))

        self.blocks = blocks

    def show_proofs_of_work(self):
        random.seed(0)
        blocks = self.blocks

        proofs_of_work = VGroup()
        new_proofs_of_work = VGroup()
        digests = VGroup()
        arrows = VGroup()
        sha_words = VGroup()
        signatures = VGroup()

        for block in blocks:
            proofs_of_work.add(block.proof_of_work)
            num_str = str(random.randint(0, 10**12))
            number = TexMobject(num_str)
            number.highlight(self.proof_of_work_color)
            number.replace(block.proof_of_work, dim_to_match = 1)
            new_proofs_of_work.add(number)

            digest = sha256_tex_mob(num_str, 60)
            digest.scale(0.7)
            digest.move_to(block).to_edge(DOWN)
            VGroup(*digest[:60]).highlight(YELLOW)
            arrow = Arrow(block, digest)
            sha = TextMobject("SHA256")
            sha.scale(0.7)
            point = arrow.get_center()
            sha.next_to(point, UP, SMALL_BUFF)
            sha.rotate(-np.pi/2, about_point = point)
            sha.shift(SMALL_BUFF*UP)
            digests.add(digest)
            arrows.add(arrow)
            sha_words.add(sha)

            for payment in block.payments[:2]:
                signatures.add(payment[-1])

        proofs_of_work.save_state()

        self.play(Transform(
            proofs_of_work, new_proofs_of_work,
            submobject_mode = "lagged_start"
        ))
        self.play(
            ShowCreation(arrows),
            Write(sha_words),
            run_time = 2
        )
        self.play(Write(digests))
        self.dither()
        for group in signatures, proofs_of_work:
            self.play(LaggedStart(
                Indicate, group,
                run_time = 2,
                rate_func = there_and_back,
            ))
            self.dither()
        self.play(
            proofs_of_work.restore,
            FadeOut(sha_words)
        )

        self.digests = digests
        self.sha_arrows = arrows

    def chain_blocks_together(self):
        blocks = self.blocks
        digests = self.digests
        sha_arrows = self.sha_arrows
        block_spacing = blocks[1].get_center() - blocks[0].get_center()
        prev_hashes = VGroup(*[
            block.prev_hash for block in blocks
        ])

        prev_hashes.add(
            prev_hashes[-1].copy().shift(block_spacing).fade(1)
        )

        new_arrows = VGroup()
        for block in blocks:
            end = np.array([
                block.get_left()[0] + block_spacing[0],
                block.prev_hash.get_center()[1],
                0
            ])
            arrow = Arrow(end+LEFT, end, buff = SMALL_BUFF)
            arrow.points[0] = block.get_right()
            arrow.points[1] = block.get_right() + RIGHT
            arrow.points[2] = end + LEFT + SMALL_BUFF*UP
            new_arrows.add(arrow)

        for i in range(3):
            self.play(
                ReplacementTransform(digests[i], prev_hashes[i+1]),
                Transform(sha_arrows[i], new_arrows[i])
            )
        arrow = new_arrows[0].copy().shift(-block_spacing)
        sha_arrows.add_to_back(arrow)
        self.play(*map(FadeIn, [arrow, prev_hashes[0]]))
        self.dither(2)

        self.prev_hashes = prev_hashes

    def mess_with_early_block(self):
        blocks = self.blocks
        amount = blocks[0].payments[1][3]
        new_amount = TextMobject("400 LD")
        new_amount.scale_to_fit_height(amount.get_height())
        new_amount.highlight(RED)
        new_amount.move_to(amount, LEFT)

        self.play(FocusOn(amount))
        self.play(Transform(amount, new_amount))
        self.dither()
        self.play(Swap(*blocks[:2]))
        self.dither()

        blocks.submobjects[:2] = blocks.submobjects[1::-1]

    def propogate_hash_change(self):
        alt_prev_hashes = self.prev_hashes.copy()
        alt_prev_hashes.highlight(RED)

        for block, prev_hash in zip(self.blocks, alt_prev_hashes[1:]):
            rect = block.rect.copy()
            rect.set_stroke(RED, 8)
            self.play(ShowCreation(rect))
            self.play(ReplacementTransform(rect, prev_hash))
        self.alt_prev_hashes = alt_prev_hashes

    def redo_proof_of_work(self):
        proofs_of_work = VGroup(*[
            block.proof_of_work for block in self.blocks
        ])
        hashes = self.alt_prev_hashes[1:]

        self.play(FadeOut(proofs_of_work))
        for proof_of_work, prev_hash in zip(proofs_of_work, hashes):
            num_pow_group = VGroup(*[
                Integer(random.randint(10**9, 10**10))
                for x in range(50)
            ])
            num_pow_group.highlight(proof_of_work.get_color())
            num_pow_group.scale_to_fit_width(proof_of_work.get_width())
            num_pow_group.move_to(proof_of_work)
            for num_pow in num_pow_group:
                self.add(num_pow)
                self.dither(1./20)
                self.remove(num_pow)
            self.add(num_pow)
            prev_hash.highlight(BLUE)

    def write_block_chain(self):
        ledger = TextMobject("Ledger")
        ledger.next_to(self.blocks, DOWN)
        cross = Cross(ledger)
        block_chain = TextMobject("``Block Chain''")
        block_chain.next_to(ledger, DOWN)

        self.play(FadeIn(ledger))
        self.play(
            ShowCreation(cross),
            Write(block_chain)
        )
        self.dither(2)


    ######

    def get_block(self):
        block = VGroup()
        rect = Rectangle(
            color = WHITE,
            height = self.block_height,
            width = self.block_width,
        )
        h_line1, h_line2 = [
            Line(
                rect.get_left(), rect.get_right()
            ).shift(0.3*rect.get_height()*vect)
            for vect in UP, DOWN
        ]

        payments = VGroup()
        if not hasattr(self, "transaction_counter"):
            self.transaction_counter = 0
        for x in range(2):
            hashes = [
                hash("%d %d"%(seed, self.transaction_counter))
                for seed in range(3)
            ]
            payment = TextMobject(
                self.names[hashes[0]%3],
                "pays",
                self.names[hashes[1]%4],
                "%d0 LD"%(hashes[2]%9 + 1),
            )
            payment.highlight_by_tex("LD", YELLOW)
            for name, color in zip(self.names, self.name_colors):
                payment.highlight_by_tex(name, color)
            signature = TextMobject("$\\langle$ Signature $\\rangle$")
            signature.highlight(payment[0].get_color())
            signature.next_to(payment, DOWN, SMALL_BUFF)
            payment.add(signature)

            factor = self.payment_height_to_block_height
            payment.scale_to_fit_height(factor*rect.get_height())
            payments.add(payment)
            self.transaction_counter += 1
        payments.add(TexMobject("\\dots").scale(0.5))
        payments.arrange_submobjects(DOWN, buff = MED_SMALL_BUFF)
        payments.next_to(h_line1, DOWN)

        proof_of_work = TextMobject("Proof of work")
        proof_of_work.highlight(self.proof_of_work_color)
        proof_of_work.scale(0.8)
        proof_of_work.move_to(
            VGroup(h_line2, VectorizedPoint(rect.get_bottom()))
        )

        prev_hash = TextMobject("Prev hash")
        prev_hash.scale(0.8)
        prev_hash.highlight(self.prev_hash_color)
        prev_hash.move_to(
            VGroup(h_line1, VectorizedPoint(rect.get_top()))
        )

        block.rect = rect
        block.h_lines = VGroup(h_line1, h_line2)
        block.payments = payments
        block.proof_of_work = proof_of_work
        block.prev_hash = prev_hash
        block.digest_mobject_attrs()
        return block


















