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

def get_cursive_name(name):
    result = TextMobject("\\normalfont\\calligra %s"%name)
    result.set_stroke(width = 0.5)
    return result

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
            "pays" if from_name.lower() != "you" else "pay",
            to_name.capitalize(),
            amount_str
        )
        for name in from_name, to_name:
            color = self.get_color_from_name(name)
            line.highlight_by_tex(name.capitalize(), color)
        if self.denomination == "USD":
            line.highlight_by_tex(amount_str, GREEN_D)
        elif self.denomination == "BTC":
            line.highlight_by_tex(amount_str, BITCOIN_COLOR)

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
        title = TextMobject("Protocol")
        title.scale(1.5)
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT).scale(4)
        h_line.next_to(title, DOWN)

        items = VGroup(*map(TextMobject, [
            "$\\cdot$ Anyone can add lines to the Ledger",
            "$\\cdot$ Settle up with real money each month"
        ]))
        items.arrange_submobjects(
            DOWN, 
            buff = MED_LARGE_BUFF, 
            aligned_edge = LEFT
        )
        items.next_to(h_line, DOWN, MED_LARGE_BUFF)


        self.add(title, h_line)
        for item in items:
            self.dither()
            self.play(LaggedStart(FadeIn, item))
        self.dither(2)

        self.title = title
        self.items = items

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
        pass


class SupplementVideoWrapper(Scene):
    def construct(self):
        pass











