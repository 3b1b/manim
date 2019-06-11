from manimlib.imports import *

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
    hexdigest = sha256(message.encode('utf-8')).hexdigest()
    return bin(int(hexdigest, 16))[2:]

def bit_string_to_mobject(bit_string):
    line = TexMobject("0"*32)
    pre_result = VGroup(*[
        line.copy() for row in range(8)
    ])
    pre_result.arrange(DOWN, buff = SMALL_BUFF)
    result = VGroup(*it.chain(*pre_result))
    result.scale(0.7)
    bit_string = (256 - len(bit_string))*"0" + bit_string

    for i, (bit, part) in enumerate(zip(bit_string, result)):
        if bit == "1":
            one = TexMobject("1")[0]
            one.replace(part, dim_to_match = 1)
            result.submobjects[i] = one

    return result

def sha256_tex_mob(message, n_forced_start_zeros = 0):
    true_bit_string = sha256_bit_string(message)
    n = n_forced_start_zeros
    bit_string = "0"*n + true_bit_string[n:]
    return bit_string_to_mobject(bit_string)

class EthereumLogo(SVGMobject):
    CONFIG = {
        "file_name" : "ethereum_logo",
        "stroke_width" : 0,
        "fill_opacity" : 1,
        "color_chars" : "8B8B48",
        "height" : 0.5,
    }
    def __init__(self, **kwargs):
        SVGMobject.__init__(self, **kwargs)
        for part, char in zip(self.submobjects, self.color_chars):
            part.set_color("#" + 6*char)

class LitecoinLogo(SVGMobject):
    CONFIG = {
        "file_name" : "litecoin_logo",
        "stroke_width" : 0,
        "fill_opacity" : 1,
        "fill_color" : LIGHT_GREY,
        "height" : 0.5,
    }

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
        rect.set_height(self.height)
        oval = Circle()
        oval.stretch_to_fit_height(0.7*self.height)
        oval.stretch_to_fit_width(0.4*self.height)
        rect.add_subpath(oval.points)

        pi = Randolph(
            mode = "pondering",
            color = GREEN_B
        )
        pi.set_width(oval.get_width())
        pi.move_to(oval)
        pi.shift(0.1*pi.get_height()*DOWN)

        self.add(pi, rect)
        for vect in UP+LEFT, DOWN+RIGHT:
            ten = TexMobject("\\$10")
            ten.set_height(0.25*self.height)
            ten.next_to(self.get_corner(vect), -vect, SMALL_BUFF)
            ten.set_color(GREEN_C)
            self.add(ten)


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
        question.set_color_by_tex("have", YELLOW)
        self.wait()
        for word, part in zip(strings, question):
            n_chars = len(word.strip())
            n_spaces = len(word) - n_chars
            self.play(
                LaggedStartMap(FadeIn, part),
                run_time = self.time_per_char * len(word),
                rate_func = squish_rate_func(smooth, 0, 0.5)
            )
            self.wait(self.time_per_char*n_spaces)
        self.wait(2)

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
            for word in ("government", "bank")
        ]
        attributes = VGroup(digital, *buildings)
        attributes.arrange(RIGHT, buff = LARGE_BUFF)
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
        self.wait()

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
        VGroup(question, arrow, rect).set_color(RED_D)

        self.play(ShowCreation(rect))
        self.play(
            Write(question),
            ShowCreation(arrow)
        )
        self.wait()

class DisectQuestion(TeacherStudentsScene):
    def construct(self):
        self.hold_up_question()
        self.list_topics()
        self.isolate_you()

    def hold_up_question(self):
        question = TextMobject(
            "What does it mean to", "have", "a", "Bitcoin?"
        )
        question.set_color_by_tex("have", YELLOW)
        question.next_to(self.teacher, UP)
        question.to_edge(RIGHT, buff = LARGE_BUFF)
        question.save_state()
        question.shift(DOWN)
        question.set_fill(opacity = 0)

        self.play(
            self.teacher.change, "raise_right_hand",
            question.restore
        )
        self.change_student_modes(*["pondering"]*3)
        self.wait()

        self.bitcoin_word = question.get_part_by_tex("Bitcoin")

    def list_topics(self):
        topics = TextMobject(
            "Digital signatures, ",
            "Proof of work, ",
            "Cryptographic hash functions, \\dots"
        )
        topics.set_width(FRAME_WIDTH - LARGE_BUFF)
        topics.to_edge(UP)
        topics.set_color_by_tex("Digital", BLUE)
        topics.set_color_by_tex("Proof", GREEN)
        topics.set_color_by_tex("hash", YELLOW)

        for word in topics:
            anims = [Write(word, run_time = 1)]
            self.change_student_modes(
                *["confused"]*3,
                added_anims = anims,
                look_at_arg = word
            )

    def isolate_you(self):
        self.pi_creatures = VGroup()
        you = self.students[1]
        rect = FullScreenFadeRectangle()
        words = TextMobject("Invent your own")
        arrow = Arrow(UP, DOWN)
        arrow.next_to(you, UP)
        words.next_to(arrow, UP)

        self.revert_to_original_skipping_status()
        self.play(FadeIn(rect), Animation(you))
        self.play(
            Write(words),
            ShowCreation(arrow),
            you.change, "erm", words
        )
        self.play(Blink(you))
        self.wait()

class CryptocurrencyEquation(Scene):
    def construct(self):
        parts = TextMobject(
            "Ledger", 
            "- Trust",
            "+ Cryptography",
            "= Cryptocurrency"
        )
        VGroup(*parts[-1][1:]).set_color(YELLOW)
        parts.set_width(FRAME_WIDTH - LARGE_BUFF)

        for part in parts:
            self.play(FadeIn(part))
            self.wait(2)

class CryptocurrencyMarketCaps(ExternallyAnimatedScene):
    pass

class ListRecentCurrencies(Scene):
    def construct(self):
        footnote = TextMobject("$^*$Listed by market cap")
        footnote.scale(0.5)
        footnote.to_corner(DOWN+RIGHT)
        self.add(footnote)

        logos = VGroup(
            BitcoinLogo(),
            EthereumLogo(),
            ImageMobject("ripple_logo"),
            LitecoinLogo(),
            EthereumLogo().set_color_by_gradient(GREEN_B, GREEN_D),
        )
        for logo in logos:
            logo.set_height(0.75)
        logos.arrange(DOWN, buff = MED_LARGE_BUFF)
        logos.shift(LEFT)
        logos.to_edge(UP)
        names = list(map(
            TextMobject, 
            [
                "Bitcoin", "Ethereum", "Ripple", 
                "Litecoin", "Ethereum Classic"
            ],
        ))
        for logo, name in zip(logos, names):
            name.next_to(logo, RIGHT)
            anims = []
            if isinstance(logo, SVGMobject):
                anims.append(DrawBorderThenFill(logo, run_time = 1))
            else:
                anims.append(FadeIn(logo))
            anims.append(Write(name, run_time = 2))
            self.play(*anims)
        dots = TexMobject("\\vdots")
        dots.next_to(logos, DOWN)
        self.play(LaggedStartMap(FadeIn, dots, run_time = 1))
        self.wait()

class Hype(TeacherStudentsScene):
    def construct(self):
        self.teacher.change_mode("guilty")
        phrases = list(map(TextMobject, [
            "I want some!",
            "I'll get rich, right?",
            "Buy them all!"
        ]))
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
        self.wait(3)

class NoCommentOnSpeculation(TeacherStudentsScene):
    def construct(self):
        axes = VGroup(
            Line(0.25*LEFT, 4*RIGHT),
            Line(0.25*DOWN, 3*UP),
        )
        times = np.arange(0, 4.25, 0.25)
        prices = [
            0.1, 0.5, 1.75, 1.5,
            2.75, 2.2, 1.3, 0.8,
            1.1, 1.3, 1.2, 1.4,
            1.5, 1.7, 1.2, 1.3,
        ]
        graph = VMobject()
        graph.set_points_as_corners([
            time*RIGHT + price*UP
            for time, price in zip(times, prices)
        ])
        graph.set_stroke(BLUE)
        group = VGroup(axes, graph)
        group.next_to(self.teacher, UP+LEFT)

        cross = Cross(group)

        mining_graphic = ImageMobject("bitcoin_mining_graphic")
        mining_graphic.set_height(2)
        mining_graphic.next_to(self.teacher, UP+LEFT)
        mining_cross = Cross(mining_graphic)
        mining_cross.set_stroke(RED, 8)

        axes.save_state()
        axes.shift(DOWN)
        axes.fade(1)
        self.play(
            self.teacher.change, "sassy",
            axes.restore,
        )
        self.play(ShowCreation(
            graph, run_time = 2,
            rate_func=linear
        ))
        self.wait()
        self.play(ShowCreation(cross))
        group.add(cross)
        self.play(
            group.shift, FRAME_WIDTH*RIGHT,
            self.teacher.change, "happy"
        )
        self.wait()

        self.student_says(
            "But...what are they?",
            student_index = 0,
            target_mode = "confused"
        )
        self.wait(2)
        self.play(
            FadeIn(mining_graphic),
            RemovePiCreatureBubble(self.students[0]),
            self.teacher.change, "sassy",
        )
        self.play(ShowCreation(mining_cross))
        self.wait()
        self.play(
            VGroup(mining_graphic, mining_cross).shift,
            FRAME_WIDTH*RIGHT
        )
        black_words = TextMobject("Random words\\\\Blah blah")
        black_words.set_color(BLACK)
        self.teacher_thinks(black_words)
        self.zoom_in_on_thought_bubble()

class MiningIsALotteryCopy(ExternallyAnimatedScene):
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

        mob.set_height(self.ledger_line_height)
        if self.enumerate_lines:
            num = TexMobject(str(len(items)) + ".")
            num.scale(0.8)
            num.set_color(self.line_number_color)
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
            line.set_color_by_tex(name.capitalize(), color)
        if self.sign_transactions:
            from_part = line.get_part_by_tex(from_name.capitalize())
            line[-1].set_color(from_part.get_color())

        amount_color = {
            "USD" : GREEN,
            "BTC" : YELLOW,
            "LD" : YELLOW,
        }.get(self.denomination, WHITE)
        line.set_color_by_tex(amount_str, amount_color)

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
        self.play(LaggedStartMap(
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
        result.set_color(color)
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
        group.arrange(RIGHT)

        self.play(
            DrawBorderThenFill(btc),
            Write(group[1], run_time = 2)
        )
        self.wait()
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

        self.play(*list(map(FadeIn, [network, ledger])))
        for payment in payments:
            new_line = self.add_payment_line_to_ledger(*payment)
            from_name, to_name, amount = payment
            from_pi = getattr(self, from_name.lower())
            to_pi = getattr(self, to_name.lower())
            cash = TexMobject("\\$"*(amount/10))
            cash.scale(0.5)
            cash.move_to(from_pi)
            cash.set_color(GREEN)

            self.play(
                cash.move_to, to_pi,
                to_pi.change_mode, "hooray"
            )
            self.play(
                FadeOut(cash),
                Write(new_line, run_time = 1)
            )
            self.wait()

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
        self.wait(2)

class UnderlyingSystemVsUserFacing(Scene):
    def construct(self):
        underlying = TextMobject("Underlying \\\\ system")
        underlying.shift(DOWN).to_edge(LEFT)
        user_facing = TextMobject("User-facing")
        user_facing.next_to(underlying, UP, LARGE_BUFF, LEFT)

        protocol = TextMobject("Bitcoin protocol")
        protocol.next_to(underlying, RIGHT, MED_LARGE_BUFF)
        protocol.set_color(BITCOIN_COLOR)
        banking = TextMobject("Banking system")
        banking.next_to(protocol, RIGHT, MED_LARGE_BUFF)
        banking.set_color(GREEN)

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
        dollar.set_height(1)
        dollar.set_color(GREEN)
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
        self.wait(2)
        self.play(
            card.restore,
            Write(dollar)
        )
        self.play(Write(banking))
        self.wait(2)
        self.play(DrawBorderThenFill(phone))
        self.wait(2)
        
class FromBankToDecentralizedSystemCopy(ExternallyAnimatedScene):
    pass

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
            cash = TexMobject("\\$"*(num/10)).set_color(GREEN)
            cash.set_height(0.5)
            cash.move_to(from_pi)
            self.play(
                cash.move_to, to_pi,
                to_pi.change_mode, "hooray"
            )
            self.play(FadeOut(cash))
        self.wait()

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
        self.wait(3)

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
            creature.cash.set_color(GREEN)
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
            result.set_color_by_tex("Owe", RED)
            result.set_color_by_tex("Get", GREEN)
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
            LaggedStartMap(FadeIn, results),
            *[
                ApplyMethod(pi.change, "happy")
                for pi in creditors
            ] + [
                ApplyMethod(pi.change, "plain")
                for pi in debtors
            ]
        )
        self.wait()
        debtor_cash, creditor_cash = [
            VGroup(*it.chain(*[pi.cash for pi in group]))
            for group in (debtors, creditors)
        ]
        self.play(FadeIn(debtor_cash))
        self.play(
            debtor_cash.arrange, RIGHT, SMALL_BUFF,
            debtor_cash.move_to, self.pi_creatures,
        )
        self.wait()
        self.play(ReplacementTransform(
            debtor_cash, creditor_cash
        ))
        self.wait(2)

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
        items = VGroup(*list(map(self.get_new_item, [
            "Anyone can add lines to the Ledger",
            "Settle up with real money each month"
        ])))

        for item in items:
            self.wait()
            self.play(LaggedStartMap(FadeIn, item))
        self.wait(2)

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
        self.anyone_can_add_a_line()
        self.bob_adds_lines()
        self.alice_reacts()

    def anyone_can_add_a_line(self):
        words = TextMobject("Anyone can add a line")
        words.to_corner(UP+RIGHT)
        words.set_color(YELLOW)
        arrow = Arrow(
            words.get_left(), 
            self.ledger.content.get_center() + DOWN,
        )

        self.play(Write(words, run_time = 1))
        self.play(ShowCreation(arrow))
        self.wait()
        self.play(
            FadeOut(words),
            FadeOut(arrow),
            FocusOn(self.bob),
        )

    def bob_adds_lines(self):
        line = self.add_payment_line_to_ledger("Alice", "Bob", 100)
        line.save_state()
        line.scale(0.001)
        line.move_to(self.bob)

        self.play(self.bob.change, "conniving")
        self.play(line.restore)
        self.wait()

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
        self.wait(3)
        self.play(
            FadeOut(bubble),
            FadeOut(bubble.content),
            self.alice.change_mode, "pondering"
        )

class AnnounceDigitalSignatures(TeacherStudentsScene):
    def construct(self):
        words = TextMobject("Digital \\\\ signatures!")
        words.scale(1.5)
        self.teacher_says(
            words,
            target_mode = "hooray",
        )
        self.change_student_modes(*["hooray"]*3)
        self.wait(2)

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
        self.play(LaggedStartMap(FadeIn, transactions))
        self.wait()

    def add_signatures(self):
        signatures = VGroup(*[
            get_cursive_name(payments[0].capitalize())
            for payments in self.payments
        ])
        for signature, transaction in zip(signatures, self.ledger.content[1:]):
            signature.next_to(transaction, RIGHT)
            signature.set_color(transaction[0].get_color())
            self.play(Write(signature, run_time = 2))
            transaction.add(signature)
        self.wait(2)

        rect = SurroundingRectangle(self.ledger.content[1])
        self.play(ShowCreation(rect))
        self.play(FadeOut(rect))
        self.wait()
        self.play(Indicate(signatures[0]))
        self.wait()

class AskHowDigitalSignaturesArePossible(TeacherStudentsScene):
    def construct(self):
        signature = get_cursive_name("Alice")
        signature.scale(1.5)
        signature.set_color(BLUE_C)
        signature.to_corner(UP+LEFT)
        signature_copy = signature.copy()
        signature_copy.shift(3*RIGHT)

        bits = TexMobject("01100001")
        bits.next_to(signature, DOWN)
        bits.shift_onto_screen()
        bits_copy = bits.copy()
        bits_copy.next_to(signature_copy, DOWN)


        self.student_says(
            "Couldn't you just \\\\ copy the signature?",
            target_mode = "confused",
            run_time = 1
        )
        self.change_student_modes("pondering", "confused", "erm")
        self.play(Write(signature))
        self.play(LaggedStartMap(FadeIn, bits, run_time = 1))
        self.wait()
        self.play(ReplacementTransform(
            bits.copy(), bits_copy,
            path_arc = np.pi/2
        ))
        self.play(Write(signature_copy))
        self.wait(3)

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
        creature_groups.arrange(RIGHT, buff = 2)
        creature_groups.to_edge(DOWN)
        self.add(creature_groups)
        for pi in self.pi_creatures:
            if pi.is_flipped():
                pi.flip()

    def generate_key_pairs(self):
        title = TextMobject("Private", "key /", "Public", "key")
        title.to_edge(UP)
        private, public = list(map(title.get_part_by_tex, ["Private", "Public"]))
        private.set_color(self.private_color)
        public.set_color(self.public_color)
        secret = TextMobject("Secret")
        secret.move_to(private, RIGHT)
        secret.set_color(self.private_color)

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
            VGroup(*pair).arrange(DOWN, aligned_edge = LEFT)
            for pair in zip(public_keys, private_keys)
        ]
        for key_pair, pi in zip(key_pairs, self.pi_creatures):
            key_pair.next_to(pi, UP, MED_LARGE_BUFF)
            for key in key_pair:
                key.set_color_by_tex("sk", self.private_color)
                key.set_color_by_tex("pk", self.public_color)

        self.play(Write(title, run_time = 2))
        self.play(ReplacementTransform(
            VGroup(VGroup(public.copy())),
            public_keys
        ))
        self.play(ReplacementTransform(
            VGroup(VGroup(private.copy())),
            private_keys
        ))
        self.wait()
        self.play(private.shift, DOWN)
        self.play(FadeIn(secret))
        self.play(FadeOut(private))
        self.wait()

        title.remove(private)
        title.add(secret)
        self.title = title
        self.private_keys = private_keys
        self.public_keys = public_keys

    def keep_secret_key_secret(self):
        keys = self.private_keys
        rects = VGroup(*list(map(SurroundingRectangle, keys)))
        rects.set_color(self.private_color)
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
        self.play(LaggedStartMap(DrawBorderThenFill, locks))
        self.wait()

        self.private_key_rects = rects
        self.locks = locks

    def show_handwritten_signatures(self):
        lines = VGroup(*[Line(LEFT, RIGHT) for x in range(5)])
        lines.arrange(DOWN)
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
        documents.arrange(RIGHT, buff = MED_LARGE_BUFF)
        documents.to_corner(UP+LEFT)

        signatures = VGroup()
        for document in documents:
            signature = get_cursive_name("Alice")
            signature.set_color(self.signature_color)
            line = document[1][-1]
            signature.next_to(line, UP, SMALL_BUFF)
            signatures.add(signature)

        self.play(
            FadeOut(self.title),
            LaggedStartMap(FadeIn, documents, run_time = 1)
        )
        self.play(Write(signatures))
        self.wait()

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
            digital_signature.set_color(signature.get_color())
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

        words = VGroup(*list(map(
            TextMobject,
            ["Different messages", "Completely different signatures"]
        )))
        words.arrange(DOWN, aligned_edge = LEFT)
        words.scale(1.3)
        words.next_to(self.documents, RIGHT)

        self.play(FadeIn(rect))
        self.play(*list(map(ShowCreation, arrows)))
        self.play(Transform(self.signatures, digital_signatures))
        self.play(*[
            ApplyMethod(pi.change, "pondering", digital_signatures)
            for pi in self.pi_creatures
        ])
        for word in words:
            self.play(FadeIn(word))
        self.wait()
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
            mob.set_color_by_tex("sk", self.private_color)
            mob.set_color_by_tex("pk", self.public_color)
            mob.set_color_by_tex(
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
        self.wait()
        self.play(ReplacementTransform(
            private_key.copy(), sign.sk
        ))
        self.wait()
        self.play(ReplacementTransform(
            VGroup(sign.sk, sign.message).copy(),
            VGroup(sign.signature)
        ))
        self.wait()
        self.play(Indicate(sign.sk))
        self.wait()
        self.play(Indicate(sign.message))
        self.wait()
        self.play(*[
            FadeIn(part)
            for part in verify
            if part not in [
                verify.message, verify.signature, 
                verify.pk, verify[-1]
            ]
        ])
        self.wait()
        self.play(
            ReplacementTransform(
                sign.message.copy(), verify.message
            ),
            ReplacementTransform(
                sign.signature.copy(), verify.signature
            )
        )
        self.wait()
        self.play(ReplacementTransform(
            public_key.copy(), VGroup(verify.pk)
        ))
        self.wait()
        self.play(Write(verify[-1]))
        self.wait()

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
        verify.set_color_by_tex("Signature", BLUE)
        verify.set_color_by_tex("pk", GREEN)
        brace = Brace(signature, UP)

        zeros_row = TexMobject("0"*32)
        zeros = VGroup(*[zeros_row.copy() for x in range(8)])
        zeros.arrange(DOWN, buff = SMALL_BUFF)
        zeros.next_to(brace, UP)

        self.add(verify)
        self.play(
            GrowFromCenter(brace),
            FadeIn(
                zeros,
                lag_ratio = 0.5,
                run_time = 3
            )
        )
        self.wait()
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
            self.wait(1./30)

class WriteTwoTo256PossibleSignatures(Scene):
    def construct(self):
        words = TextMobject(
            "$2^{256}$", "possible\\\\", "signatures"
        )
        words.scale(2)
        words.set_color_by_tex("256", BLUE)
        self.play(Write(words))
        self.wait()

class SupplementVideoWrapper(Scene):
    def construct(self):
        title = TextMobject("How secure is 256 bit security?")
        title.scale(1.5)
        title.to_edge(UP)
        rect = ScreenRectangle(height = 6)
        rect.next_to(title, DOWN)
        self.add(title)
        self.play(ShowCreation(rect))
        self.wait()

class FeelConfidentWithVerification(PiCreatureScene):
    def construct(self):
        self.show_verification()
        self.show_secret_key()

    def show_verification(self):
        verify = TextMobject(
            "Verify(", "Message", ", ", 
            "256 bit Signature", ", ", "pk", ")",
            arg_separator = ""
        )
        signature_word = verify.get_part_by_tex("Signature")
        verify.set_color_by_tex("Signature", BLUE)
        verify.set_color_by_tex("pk", GREEN)
        brace = Brace(signature_word, UP)
        signature = sha256_tex_mob("Signature")
        signature.next_to(brace, UP)
        signature.set_color(BLUE_C)

        rhs = TextMobject("=", "True")
        rhs.set_color_by_tex("True", YELLOW)
        rhs.next_to(verify, RIGHT)

        pk = verify.get_part_by_tex("pk")
        sk = TextMobject("sk")
        sk.set_color(RED)
        arrow = TexMobject("\\Updownarrow")
        arrow.next_to(pk, DOWN)
        sk.next_to(arrow, DOWN)
        sk_group = VGroup(arrow, sk)
        lock_box = SurroundingRectangle(sk_group, buff = SMALL_BUFF)
        lock_box.set_color(RED)
        lock = SVGMobject(
            file_name = "lock", 
            fill_color = LIGHT_GREY,
            height = 0.5,
        )
        lock.next_to(lock_box, LEFT, SMALL_BUFF)

        self.add(verify)
        self.play(
            GrowFromCenter(brace),
            Write(signature),
            self.pi_creature.change, "pondering"
        )
        self.play(ReplacementTransform(
            verify.copy(), rhs
        ))
        self.wait()
        self.play(self.pi_creature.change, "happy")
        self.play(Write(sk_group))
        self.play(
            ShowCreation(lock_box),
            DrawBorderThenFill(lock, run_time = 1)
        )
        self.wait(2)


    def show_secret_key(self):
        pass


    #####

    def create_pi_creature(self):
        return Randolph().to_corner(DOWN+LEFT)

class IncludeTransactionNumber(LedgerScene):
    CONFIG = {
        "ledger_width" : 7,
    }
    def construct(self):
        self.add_ledger_and_network()
        self.add_signed_payment()
        self.fail_to_sign_new_transaction()
        self.copy_payment_many_times()
        self.add_ids()

    def add_signed_payment(self):
        line = self.add_payment_line_to_ledger(
            "Alice", "Bob", 100
        )
        signature = self.get_signature()
        signature.scale(0.7)
        signature.next_to(line, RIGHT)
        signature.save_state()
        signature.scale(0.1)
        signature.move_to(self.alice)

        self.play(Write(line, run_time = 1))
        self.play(
            signature.restore,
            self.alice.change, "raise_left_hand"
        )
        self.wait()
        self.play(self.alice.change, "happy")
        self.wait()

        line.add(signature)

    def fail_to_sign_new_transaction(self):
        payment = self.add_payment_line_to_ledger("Alice", "Bob", 3000)
        q_marks = TexMobject("???")
        q_marks.next_to(payment, RIGHT)
        cross = Cross(payment)
        payment.save_state()
        payment.move_to(self.bob.get_corner(UP+LEFT))
        payment.set_fill(opacity = 0)

        self.play(
            self.bob.change, "raise_right_hand",
            payment.restore,
        )
        self.play(
            self.bob.change, "confused",
            Write(q_marks)
        )
        self.play(ShowCreation(cross))
        self.wait()
        self.play(*list(map(FadeOut, [payment, cross, q_marks])))
        self.ledger.content.remove(payment)

    def copy_payment_many_times(self):
        line = self.ledger.content[-1]
        copies = VGroup(*[line.copy() for x in range(4)])
        copies.arrange(DOWN, buff = MED_SMALL_BUFF)
        copies.next_to(line, DOWN, buff = MED_SMALL_BUFF)

        self.play(
            LaggedStartMap(FadeIn, copies, run_time = 3),
            self.bob.change, "conniving",
        )
        self.play(self.alice.change, "angry")
        self.wait()

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
            number.set_color(YELLOW)
            number.next_to(line, LEFT)
            numbers.add(number)
            line.add_to_back(number)
            old_signature = line[-1]
            new_signature = self.get_signature()
            new_signature.replace(old_signature)
            new_signature.set_color(colors[i])
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
            lag_ratio = 0.5,
            run_time = 2,
        ))
        self.play(self.bob.change, "erm")
        self.wait(2)

class ProtocolWithDigitalSignatures(InitialProtocol):
    def construct(self):
        self.force_skipping()
        InitialProtocol.construct(self)
        self.revert_to_original_skipping_status()

        rect = SurroundingRectangle(self.items[-1])
        rect.set_color(RED)

        new_item = self.get_new_item(
            "Only signed transactions are valid"
        )
        new_item.set_color(YELLOW)

        self.play(Write(new_item))
        self.wait()
        self.play(ShowCreation(rect))
        self.wait()

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

        self.play(LaggedStartMap(
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
            self.charlie.shift, FRAME_X_RADIUS*RIGHT,
            rate_func = running_start
        )
        self.play(*[
            ApplyMethod(pi.change, "angry", self.charlie)
            for pi in self.get_pi_creatures()
        ])
        self.wait()

class CharlieFeelsGuilty(Scene):
    def construct(self):
        charlie = PiCreature(color = GREY_BROWN)
        charlie.scale(2)

        self.play(FadeIn(charlie))
        self.play(charlie.change, "sad")
        for x in range(2):
            self.play(Blink(charlie))
            self.wait(2)

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
        self.wait()

class DontAllowOverdrawing(InitialProtocol):
    def construct(self):
        self.add_title()
        lines = list(map(self.get_new_item, [
            "Anyone can add lines to the Ledger \\,",
            "Only signed transactions are valid \\,",
            "No overspending"
        ]))
        lines[2].set_color(YELLOW)

        self.add(*lines[:2])
        self.wait()
        self.play(Write(lines[2]))
        self.wait()

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
        moneys.set_color(GREEN)
        for pi, money in zip(reversed(self.pi_creatures), moneys):
            vect = pi.get_center() - center
            money.next_to(center, vect, SMALL_BUFF)
            money.add_background_rectangle()
            money.save_state()
            money.scale(0.01)
            corner = pi.get_corner(UP + np.sign(vect[0])*LEFT)
            money.move_to(corner)

        self.play(
            LaggedStartMap(
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
            new_line.set_color_by_tex(
                name.capitalize(),
                self.get_color_from_name(name)
            )
            new_line.set_color_by_tex("100", GREEN)
            self.add_line_to_ledger(new_line)
            lines.add(new_line)
        line = Line(LEFT, RIGHT)
        line.set_width(self.ledger.get_width())
        line.scale_in_place(0.9)
        line.next_to(lines[-1], DOWN, SMALL_BUFF, LEFT)
        line.set_stroke(width = 1)
        lines[-1].add(line)

        self.play(
            LaggedStartMap(FadeIn, lines),
            *[
                ApplyMethod(pi.change, "thinking", self.ledger)
                for pi in self.pi_creatures
            ]
        )
        self.wait()

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
            self.wait()

    def point_out_charlie_is_broke(self):
        charlie_lines = VGroup(*[
            VGroup(*self.ledger.content[i][1:5])
            for i in (3, 5, 6, 7)
        ])
        rects = VGroup(*[
            SurroundingRectangle(line)
            for line in charlie_lines
        ])
        rects.set_color(YELLOW)
        rects.set_stroke(width = 2)
        last_rect = rects[-1]
        last_rect.set_stroke(RED, 4)
        rects.remove(last_rect)
        invalid = TextMobject("Invalid")
        invalid.set_color(RED)
        invalid.next_to(last_rect, DOWN)

        self.play(ShowCreation(rects))
        self.play(self.charlie.change_mode, "guilty")
        self.wait()
        self.play(ShowCreation(last_rect))
        self.play(*[
            ApplyMethod(pi.change, "sassy", self.charlie)
            for pi in self.pi_creatures
            if pi is not self.charlie
        ])
        self.play(Write(invalid))
        self.wait(2)
        self.play(*list(map(FadeOut, [rects, last_rect, invalid])))

    def running_balance(self):
        charlie_lines = VGroup(*[
            VGroup(*self.ledger.content[i][1:5])
            for i in (3, 5, 6, 7)
        ])
        signatures = VGroup(*[
            self.ledger.content[i][5]
            for i in (5, 6, 7)
        ])
        rect = Rectangle(color = WHITE)
        rect.set_fill(BLACK, 0.8)
        rect.stretch_to_fit_height(self.ledger.get_height() - 2*MED_SMALL_BUFF)
        title = TextMobject("Charlie's running \\\\ balance")
        rect.stretch_to_fit_width(title.get_width() + 2*MED_SMALL_BUFF)
        rect.move_to(self.ledger.get_right())
        title.next_to(rect.get_top(), DOWN)
        balance = VGroup(rect, title)

        lines = VGroup(*list(map(TextMobject, [
            "\\$100", "\\$50", "\\$0", "Overdrawn"
        ])))
        lines.set_color(GREEN)
        lines[-1].set_color(RED)
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
            LaggedStartMap(FadeIn, lines, run_time = 3),
            LaggedStartMap(ShowCreation, arrows, run_time = 3),
        )
        self.wait()

class RemovedConnectionBetweenLedgerAndCash(TeacherStudentsScene):
    def construct(self):
        ledger = Rectangle(
            height = 2, width = 1.5,
            color = WHITE
        )
        ledger_name = TextMobject("Ledger")
        ledger_name.set_width(ledger.get_width() - MED_SMALL_BUFF)
        ledger_name.next_to(ledger.get_top(), DOWN)
        ledger.add(ledger_name)

        arrow = TexMobject("\\leftrightarrow")
        cash = TexMobject("\\$\\$\\$")
        cash.set_color(GREEN)
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
        self.wait(3)

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

        self.play(LaggedStartMap(
            FadeIn, lines,
            run_time = 4,
            lag_ratio = 0.3
        ))
        self.wait()

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
            ld.set_color(YELLOW)
            ld.scale(0.8)
            ld.move_to(amount, LEFT)
            amounts.target.add(ld)

        ledger_dollars = TextMobject("Ledger Dollars \\\\ ``LD'' ")
        ledger_dollars.set_color(YELLOW)
        ledger_dollars.next_to(self.ledger, RIGHT)

        self.play(
            Write(ledger_dollars),
            FadeOut(self.bubble),
            self.pi_creature.change, "thinking", ledger_dollars
        )
        self.play(MoveToTarget(amounts))
        self.wait(2)


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
        title.set_color_by_tex("LD", YELLOW)
        title.set_color_by_tex("\\$", GREEN)
        title.scale(1.3)
        title.to_edge(UP).shift(LEFT)

        self.play(Write(title))
        self.wait()

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
        self.wait()

    def add_bob_pays_alice_line(self):
        line = self.add_payment_line_to_ledger(
            "Bob", "Alice", 10
        )
        line.save_state()
        line.scale(0.01)
        line.move_to(self.bob.get_corner(UP+LEFT))
        self.play(self.bob.change, "raise_right_hand", line)
        self.play(line.restore, run_time = 2)
        self.wait()

    def everyone_thinks(self):
        self.play(*[
            ApplyMethod(pi.change, "thinking", self.ledger)
            for pi in self.pi_creatures
        ])
        self.wait(4)

class BitcoinIsALedger(Scene):
    def construct(self):
        self.add_btc_to_ledger()
        self.add_currency_to_tx_history()

    def add_btc_to_ledger(self):
        logo = BitcoinLogo()
        ledger = self.get_ledger()
        arrow = TexMobject("\\Leftrightarrow")
        group = VGroup(logo, arrow, ledger)
        group.arrange(RIGHT)

        self.play(DrawBorderThenFill(logo))
        self.wait()
        self.play(
            Write(arrow),
            Write(ledger)
        )
        self.wait()

        self.btc_to_ledger = group

    def add_currency_to_tx_history(self):
        equation = TextMobject(
            "Currency", "=", "Transaction history"
        )
        equation.set_color_by_tex("Currency", BITCOIN_COLOR)
        equation.shift(
            self.btc_to_ledger[1].get_center() - \
            equation[1].get_center() + 2*UP
        )

        for part in reversed(equation):
            self.play(FadeIn(part))
        self.wait()

    def get_ledger(self):
        rect = Rectangle(height = 2, width = 1.5)
        title = TextMobject("Ledger")
        title.set_width(0.8*rect.get_width())
        title.next_to(rect.get_top(), DOWN, SMALL_BUFF)

        lines = VGroup(*[
            Line(LEFT, RIGHT)
            for x in range(8)
        ])
        lines.arrange(DOWN, buff = SMALL_BUFF)
        lines.stretch_to_fit_width(title.get_width())
        lines.next_to(title, DOWN)
        return VGroup(rect, title, lines)

class BigDifferenceBetweenLDAndCryptocurrencies(Scene):
    def construct(self):
        ld = TextMobject("LD").scale(1.5).set_color(YELLOW)
        btc = BitcoinLogo()
        eth = EthereumLogo()
        ltc = LitecoinLogo()
        logos = VGroup(ltc, eth, ld, btc)
        cryptos = VGroup(btc, eth, ltc)
        for logo in cryptos:
            logo.set_height(1)
        vects = compass_directions(4, DOWN+LEFT)
        for logo, vect in zip(logos, vects):
            logo.move_to(0.75*vect)

        centralized = TextMobject("Centralized")
        decentralized = TextMobject("Decentralized")
        words = VGroup(centralized, decentralized)
        words.scale(1.5)
        words.to_edge(UP)
        for word, vect in zip(words, [RIGHT, LEFT]):
            word.shift(FRAME_X_RADIUS*vect/2)

        self.add(logos)
        self.wait()
        self.play(
            cryptos.next_to, decentralized, DOWN, LARGE_BUFF,
            ld.next_to, centralized, DOWN, LARGE_BUFF,
        )
        self.play(*list(map(Write, words)))
        self.wait(2)

class DistributedLedgerScene(LedgerScene):
    def get_large_network(self):
        network = self.get_network()
        network.set_height(FRAME_HEIGHT - LARGE_BUFF)
        network.center()
        for pi in self.pi_creatures:
            pi.label.scale(0.8, about_point = pi.get_bottom())
        return network

    def get_distributed_ledgers(self):
        ledger = self.get_ledger()
        title = ledger[1]
        h_line = ledger.content
        title.set_width(0.7*ledger.get_width())
        title.next_to(ledger.get_top(), DOWN, MED_LARGE_BUFF)
        h_line.next_to(title, DOWN)
        added_lines = VGroup(*[h_line.copy() for x in range(5)])
        added_lines.arrange(DOWN, buff = MED_LARGE_BUFF)
        added_lines.next_to(h_line, DOWN, MED_LARGE_BUFF)
        ledger.content.add(added_lines)

        ledgers = VGroup()
        for pi in self.pi_creatures:
            pi.ledger = ledger.copy()
            pi.ledger.set_height(pi.get_height())
            pi.ledger[0].set_color(pi.get_color())
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
        question.set_color(RED)
        question.scale(1.5)
        question.next_to(self.ledger, UP)

        self.play(Write(question))
        self.wait()

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
            self.play(LaggedStartMap(FadeIn, payment, run_time = 1))
            self.wait()

    def ask_who_controls_ledger(self):
        new_question = TextMobject("Who", "controls", "this?!")
        new_question.scale(1.3)
        new_question.move_to(self.question)
        new_question.set_color(RED)

        self.play(Transform(self.question, new_question))
        self.play(*[
            ApplyMethod(pi.change, "confused", new_question)
            for pi in self.pi_creatures
        ])
        self.wait(2)

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
            group.set_height, FRAME_HEIGHT - 2,
            group.center
        )
        self.wait(2)

    def broadcast_transaction(self):
        payment = TextMobject(
            "Alice", "pays", "Bob", "100 LD"
        )
        payment.set_color_by_tex("Alice", self.alice.get_color())
        payment.set_color_by_tex("Bob", self.bob.get_color())
        payment.set_color_by_tex("LD", YELLOW)
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
        self.wait()
        self.play(
            ReplacementTransform(
                VGroup(payment), payment_copies, 
                run_time = 3,
                rate_func = squish_rate_func(smooth, 0.5, 1)
            ),
            Broadcast(self.alice.get_corner(UP+RIGHT)),
            self.alice.change, "happy"
        )
        self.wait()
        pairs = list(zip(payment_copies, self.pi_creatures))
        Scene.play(self, *it.chain(*[
            [
                pi.look_at, pi.ledger[-1],
                line.scale, 0.2,
                line.next_to, pi.ledger[-1], DOWN, SMALL_BUFF,
            ]
            for line, pi in pairs
        ]))
        self.wait(3)

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
            ledgers.arrange, RIGHT,
            ledgers.space_out_submobjects,
        )

        question = TextMobject("Are these the same?")
        question.scale(1.5)
        question.to_edge(UP)
        arrows = VGroup(*[
            Arrow(question.get_bottom(), ledger.get_top())
            for ledger in ledgers
        ])

        self.play(*list(map(ShowCreation, arrows)))
        self.play(Write(question))
        self.wait()

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
        self.pi_creatures.arrange(RIGHT, buff = 5)

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
        corner = FRAME_Y_RADIUS*UP + FRAME_X_RADIUS*LEFT

        payment = TextMobject(
            "Alice", "pays", "Bob", "10 LD"
        )
        payment.set_color_by_tex("Alice", self.alice.get_color())
        payment.set_color_by_tex("Bob", self.bob.get_color())
        payment.set_color_by_tex("LD", YELLOW)
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
        self.wait(2)

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
            FRAME_X_RADIUS*RIGHT*u1 + FRAME_Y_RADIUS*UP*u2
            for u1, u2 in [(-1, 1), (1, 1), (-1, -1)]
        ]
        you = self.you
        you.scale(2)
        you.center()

        self.add(you)
        for payment, corner in zip(payments, corners):
            vect = corner/get_norm(corner)
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
        self.wait()

class AskWhatToAddToProtocol(InitialProtocol):
    def construct(self):
        self.add_title()
        items = VGroup(*list(map(self.get_new_item, [
            "Broadcast transactions",
            "Only accept signed transactions",
            "No overspending",
        ] + [""]*6)))
        brace = Brace(VGroup(*items[3:]), LEFT)
        question = TextMobject("What to \\\\ add here?")
        question.set_color(RED)
        question.scale(1.5)
        brace.set_color(RED)
        question.next_to(brace, LEFT)

        self.add(*items[:3])
        self.play(GrowFromCenter(brace))
        self.play(Write(question))
        self.wait()

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
                    new_bit.set_color(YELLOW)
                zeros.submobjects[-i-1] = new_bit
                self.remove(curr_bit)
            self.add(zeros)
            self.wait(1./30)

class TrustComputationalWorkSupplement(Scene):
    def construct(self):
        words = TextMobject(
            "Main tool: ", "Cryptographic hash functions"
        )
        words[1].set_color(YELLOW)
        self.add(words[0])
        self.play(Write(words[1]))
        self.wait()

class FraudIsInfeasible(Scene):
    def construct(self):
        words = TextMobject(
            "Fraud", "$\\Leftrightarrow$",
            "Computationally infeasible"
        )
        words.set_color_by_tex("Fraud", RED)
        words.to_edge(UP)
        self.play(FadeIn(words[0]))
        self.play(FadeIn(words[2]))
        self.play(Write(words[1]))
        self.wait()

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
        self.wait()
        self.play(
            idea.restore,
            RemovePiCreatureBubble(
                self.teacher, target_mode = "hooray",
                look_at_arg = lightbulb
            ),
        )
        self.change_student_modes(
            *["pondering"]*3,
            added_anims = [LaggedStartMap(FadeIn, lightbulb)]
        )
        self.play(LaggedStartMap(
            ApplyMethod, lightbulb,
            lambda b : (b.set_color, YELLOW_A),
            rate_func = there_and_back
        ))
        self.wait(2)

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
            lhs.set_color_by_tex(message, BLUE)
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
        sha_text.set_color(YELLOW)
        message_text = message_brace.get_text("Message/file")
        message_text.set_color(BLUE)
        digest_text = digest_brace.get_text("``Hash'' or ``Digest''")
        brace_text_pairs = [
            (sha_brace, sha_text),
            (message_brace, message_text),
            (digest_brace, digest_text),
        ]

        looks_random = TextMobject("Looks random")
        looks_random.set_color(MAROON_B)
        looks_random.next_to(digest_text, DOWN)

        self.add(group)
        self.remove(digest)
        for brace, text in brace_text_pairs:
            if brace is digest_brace:
                self.play(LaggedStartMap(
                    FadeIn, digest,
                    run_time = 4,
                    lag_ratio = 0.05
                ))
                self.wait()
            self.play(
                GrowFromCenter(brace),
                Write(text, run_time = 2)
            )
            self.wait()
        self.play(Write(looks_random))
        self.wait(2)
        for mob in digest, message:
            self.play(LaggedStartMap(
                ApplyMethod, mob,
                lambda m : (m.set_color, YELLOW),
                rate_func = there_and_back,
                run_time = 1
            ))
        self.wait()
        self.play(FadeOut(looks_random))

        new_lhs, new_digest = groups[1]
        char = new_lhs[2][-5]
        arrow = Arrow(UP, ORIGIN, buff = 0)
        arrow.next_to(char, UP)
        arrow.set_color(RED)
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
                lag_ratio = 0.5,
                path_arc = np.pi/2
            ))
            if arrow in self.get_mobjects():
                self.wait()
                self.play(FadeOut(arrow))
        self.wait()

        new_sha_text = TextMobject(
            "Cryptographic", "hash function"
        )
        new_sha_text.next_to(sha_brace, UP)
        new_sha_text.shift_onto_screen()
        new_sha_text.set_color(YELLOW)
        new_sha_text[0].set_color(GREEN)
        self.play(Transform(sha_text, new_sha_text))
        self.wait()

        self.lhs = lhs
        self.message = message
        self.digest = digest
        self.digest_text = digest_text
        self.message_text = message_text

    def inverse_function_question(self):
        arrow = Arrow(3*RIGHT, 3*LEFT, buff = 0)
        arrow.set_stroke(width = 8)
        arrow.set_color(RED)
        everything = VGroup(*self.get_mobjects())
        arrow.next_to(everything, DOWN)
        words = TextMobject("Inverse is infeasible")
        words.set_color(RED)
        words.next_to(arrow, DOWN)

        self.play(ShowCreation(arrow))
        self.play(Write(words))
        self.wait()

    def issue_challenge(self):
        desired_output_text = TextMobject("Desired output")
        desired_output_text.move_to(self.digest_text)
        desired_output_text.set_color(YELLOW)
        new_digest = sha256_tex_mob("Challenge")
        new_digest.replace(self.digest)
        q_marks = TextMobject("???")
        q_marks.move_to(self.message_text)
        q_marks.set_color(BLUE)

        self.play(
            Transform(
                self.digest, new_digest,
                run_time = 2,
                lag_ratio = 0.5,
                path_arc = np.pi/2
            ),
            Transform(self.digest_text, desired_output_text)
        )
        self.play(
            FadeOut(self.message),
            Transform(self.message_text, q_marks)
        )
        self.wait()

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
            lhs.set_color_by_tex("Guess", BLUE)
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
                lag_ratio = 0.5
            ))

class PonderScematic(Scene):
    def construct(self):
        randy = Randolph()
        randy.to_corner(DOWN+LEFT)
        self.play(randy.change, "confused", ORIGIN)
        for x in range(3):
            self.play(Blink(randy))
            self.wait(2)

class ViewingSLLCertificate(ExternallyAnimatedScene):
    pass

class SHA256ToProofOfWork(TeacherStudentsScene):
    def construct(self):
        sha = TextMobject("SHA256")
        proof = TextMobject("Proof of work")
        arrow = Arrow(LEFT, RIGHT)
        group = VGroup(sha, arrow, proof)
        group.arrange(RIGHT)
        group.next_to(self.teacher, UP, buff = LARGE_BUFF)
        group.to_edge(RIGHT, buff = LARGE_BUFF)

        self.play(
            Write(sha, run_time = 1),
            self.teacher.change, "raise_right_hand"
        )
        self.play(ShowCreation(arrow))
        self.play(Write(proof, run_time = 1))
        self.wait(3)

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
        nonce.set_color(GREEN_C)
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

        self.play(LaggedStartMap(
            FadeIn, VGroup(special_word, nonce_brace, nonce)
        ))
        self.wait()
        self.play(
            nonce.next_to, ledger.content, DOWN, MED_SMALL_BUFF, LEFT,
            FadeOut(special_word),
            FadeOut(nonce_brace)
        )
        ledger.content.add(nonce)
        decomposed_ledger = VGroup(*[m for m in ledger.family_members_with_points() if not m.is_subpath])
        self.play(
            ShowCreation(arrow),
            FadeIn(sha)
        )
        self.play(LaggedStartMap(
            ApplyMethod, decomposed_ledger,
            lambda m : (m.set_color, YELLOW),
            rate_func = there_and_back
        ))
        point = VectorizedPoint(sha.get_center())
        point.set_fill(opacity = 1)
        self.play(LaggedStartMap(
            Transform, decomposed_ledger.copy(),
            lambda m : (m, point),
            run_time = 1
        ))
        bit_iter = iter(digest)
        self.play(LaggedStartMap(
            ReplacementTransform, 
            VGroup(*[point.copy() for x in range(256)]),
            lambda m : (m, next(bit_iter)),
        ))
        self.remove(*self.get_mobjects_from_last_animation())
        self.add(digest)
        self.play(
            GrowFromCenter(zeros_brace),
            Write(zeros_words, run_time = 1)
        )
        self.play(LaggedStartMap(
            ApplyMethod, zeros,
            lambda m : (m.set_color, YELLOW)
        ))
        self.wait(2)

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
        self.wait()
        self.play(Write(probability[1], run_time = 2))
        self.wait(2)

    def guess_and_check(self):
        q_mark = TexMobject("?")
        q_mark.set_color(RED)
        q_mark.next_to(self.zeros_words, RIGHT, SMALL_BUFF)

        self.digest.save_state()
        self.nonce.save_state()

        self.play(FadeIn(q_mark))
        for x in range(1, 13):
            nonce = TexMobject(str(x))
            nonce.move_to(self.nonce)
            nonce.set_color(GREEN_C)
            digest = sha256_tex_mob(str(x))
            digest.replace(self.digest)

            self.play(Transform(
                self.nonce, nonce,
                run_time = 1 if x == 1 else 0.3
            ))
            self.play(Transform(
                self.digest, digest,
                run_time = 1,
                lag_ratio = 0.5
            ))
        self.wait()
        self.play(self.nonce.restore)
        self.play(
            self.digest.restore, 
            lag_ratio = 0.5,
            run_time = 2
        )
        self.play(FadeOut(q_mark))
        self.wait()

    def name_proof_of_work(self):
        words = TextMobject("``Proof of work''")
        words.next_to(self.nonce, DOWN, LARGE_BUFF)
        words.shift(MED_LARGE_BUFF*RIGHT)
        words.set_color(GREEN)
        arrow = Arrow(
            words.get_top(), self.nonce.get_bottom(),
            color = WHITE,
            tip_length = 0.15
        )
        self.play(Write(words, run_time = 2))
        self.play(ShowCreation(arrow))
        self.wait()

    def change_ledger(self):
        amount = self.ledger.content[2][-1]
        new_amount = TextMobject("300 LD")
        new_amount.set_height(amount.get_height())
        new_amount.set_color(amount.get_color())
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
            lag_ratio = 0.5,
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
                dist = get_norm(vect)
                if dist < 2:
                    outgoing_lines.append(line)
            dots = VGroup()
            for line in outgoing_lines:
                dot = Dot(line.get_start())
                dot.set_color(YELLOW)
                dot.generate_target()
                dot.target.move_to(line.get_end())
                for alt_pi in self.pi_creatures:
                    vect = line.get_end() - alt_pi.get_center()
                    dist = get_norm(vect)
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
        self.propagate_hash_change()
        self.redo_proof_of_work()
        self.write_block_chain()


    def divide_ledger_into_blocks(self):
        blocks = VGroup(*[
            self.get_block() for x in range(3)
        ])
        blocks.arrange(RIGHT, buff = 1.5)
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

        self.play(LaggedStartMap(FadeIn, blocks))
        self.play(
            Write(blocks_word),
            LaggedStartMap(
                ShowCreation, arrows, 
                run_time = 1,
            )
        )
        self.wait()
        for group in all_payments, all_proofs_of_work:
            self.play(LaggedStartMap(
                Indicate, group,
                rate_func = there_and_back,
                scale_factor = 1.1,
            ))
        self.play(*list(map(FadeOut, [blocks_word, arrows])))

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
            number.set_color(self.proof_of_work_color)
            number.replace(block.proof_of_work, dim_to_match = 1)
            new_proofs_of_work.add(number)

            digest = sha256_tex_mob(num_str, 60)
            digest.scale(0.7)
            digest.move_to(block).to_edge(DOWN)
            VGroup(*digest[:60]).set_color(YELLOW)
            arrow = Arrow(block, digest)
            sha = TextMobject("SHA256")
            sha.scale(0.7)
            point = arrow.get_center()
            sha.next_to(point, UP, SMALL_BUFF)
            sha.rotate(-np.pi/2, about_point = point)
            sha.shift(SMALL_BUFF*(UP+RIGHT))
            digests.add(digest)
            arrows.add(arrow)
            sha_words.add(sha)

            for payment in block.payments[:2]:
                signatures.add(payment[-1])

        proofs_of_work.save_state()

        self.play(Transform(
            proofs_of_work, new_proofs_of_work,
            lag_ratio = 0.5
        ))
        self.play(
            ShowCreation(arrows),
            Write(sha_words),
            run_time = 2
        )
        self.play(Write(digests))
        self.wait()
        for group in signatures, proofs_of_work:
            self.play(LaggedStartMap(
                Indicate, group,
                run_time = 2,
                rate_func = there_and_back,
            ))
            self.wait()
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
        self.play(*list(map(FadeIn, [arrow, prev_hashes[0]])))
        self.wait(2)

        self.prev_hashes = prev_hashes

    def mess_with_early_block(self):
        blocks = self.blocks
        amount = blocks[0].payments[1][3]
        new_amount = TextMobject("400 LD")
        new_amount.set_height(amount.get_height())
        new_amount.set_color(RED)
        new_amount.move_to(amount, LEFT)

        self.play(FocusOn(amount))
        self.play(Transform(amount, new_amount))
        self.wait()
        self.play(Swap(*blocks[:2]))
        self.wait()

        blocks.submobjects[:2] = blocks.submobjects[1::-1]

    def propagate_hash_change(self):
        prev_hashes = self.prev_hashes

        for block, prev_hash in zip(self.blocks, prev_hashes[1:]):
            rect = block.rect.copy()
            rect.set_stroke(RED, 8)
            rect.target = SurroundingRectangle(prev_hash)
            rect.target.set_stroke(rect.get_color(), 0)
            self.play(ShowCreation(rect))
            self.play(
                MoveToTarget(rect),
                prev_hash.set_color, RED
            )

    def redo_proof_of_work(self):
        proofs_of_work = VGroup(*[
            block.proof_of_work for block in self.blocks
        ])
        hashes = self.prev_hashes[1:]

        self.play(FadeOut(proofs_of_work))
        for proof_of_work, prev_hash in zip(proofs_of_work, hashes):
            num_pow_group = VGroup(*[
                Integer(random.randint(10**9, 10**10))
                for x in range(50)
            ])
            num_pow_group.set_color(proof_of_work.get_color())
            num_pow_group.set_width(proof_of_work.get_width())
            num_pow_group.move_to(proof_of_work)
            for num_pow in num_pow_group:
                self.add(num_pow)
                self.wait(1./20)
                prev_hash.set_color(random_bright_color())
                self.remove(num_pow)
            self.add(num_pow)
            prev_hash.set_color(BLUE)

    def write_block_chain(self):
        ledger = TextMobject("Ledger")
        ledger.next_to(self.blocks, DOWN, LARGE_BUFF)
        cross = Cross(ledger)
        block_chain = TextMobject("``Block Chain''")
        block_chain.next_to(ledger, DOWN)

        self.play(FadeIn(ledger))
        self.play(
            ShowCreation(cross),
            Write(block_chain)
        )
        self.wait(2)


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
            for vect in (UP, DOWN)
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
            payment.set_color_by_tex("LD", YELLOW)
            for name, color in zip(self.names, self.name_colors):
                payment.set_color_by_tex(name, color)
            signature = TextMobject("$\\langle$ Signature $\\rangle$")
            signature.set_color(payment[0].get_color())
            signature.next_to(payment, DOWN, SMALL_BUFF)
            payment.add(signature)

            factor = self.payment_height_to_block_height
            payment.set_height(factor*rect.get_height())
            payments.add(payment)
            self.transaction_counter += 1
        payments.add(TexMobject("\\dots").scale(0.5))
        payments.arrange(DOWN, buff = MED_SMALL_BUFF)
        payments.next_to(h_line1, DOWN)

        proof_of_work = TextMobject("Proof of work")
        proof_of_work.set_color(self.proof_of_work_color)
        proof_of_work.scale(0.8)
        proof_of_work.move_to(
            VGroup(h_line2, VectorizedPoint(rect.get_bottom()))
        )

        prev_hash = TextMobject("Prev hash")
        prev_hash.scale(0.8)
        prev_hash.set_color(self.prev_hash_color)
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

class DistributedBlockChainScene(DistributedLedgerScene):
    CONFIG = {
        "block_height" : 0.5,
        "block_width" : 0.5,
        "n_blocks" : 3,
    }
    def get_distributed_ledgers(self):
        ledgers = VGroup()
        point = self.pi_creatures.get_center()
        for pi in self.pi_creatures:
            vect = pi.get_center() - point
            vect[0] = 0
            block_chain = self.get_block_chain()
            block_chain.next_to(
                VGroup(pi, pi.label), vect, SMALL_BUFF
            )
            pi.block_chain = pi.ledger = block_chain
            ledgers.add(block_chain)
        self.ledgers = self.block_chains = ledgers
        return ledgers

    def get_block_chain(self):
        blocks = VGroup(*[
            self.get_block() 
            for x in range(self.n_blocks)
        ])
        blocks.arrange(RIGHT, buff = MED_SMALL_BUFF)
        arrows = VGroup()

        for b1, b2 in zip(blocks, blocks[1:]):
            arrow = Arrow(
                LEFT, RIGHT,
                preserve_tip_size_when_scaling = False,
                tip_length = 0.15,
            )
            arrow.set_width(b1.get_width())
            target_point = interpolate(
                b2.get_left(), b2.get_corner(UP+LEFT), 0.8
            )
            arrow.next_to(target_point, LEFT, 0.5*SMALL_BUFF)
            arrow.points[0] = b1.get_right()
            arrow.points[1] = b2.get_left()
            arrow.points[2] = b1.get_corner(UP+RIGHT)
            arrow.points[2] += SMALL_BUFF*LEFT
            arrows.add(arrow)
        block_chain = VGroup(blocks, arrows)
        block_chain.blocks = blocks
        block_chain.arrows = arrows
        return block_chain

    def get_block(self):
        block = Rectangle(
            color = WHITE,
            height = self.block_height,
            width = self.block_width,
        )
        for vect in UP, DOWN:
            line = Line(block.get_left(), block.get_right())
            line.shift(0.3*block.get_height()*vect)
            block.add(line)
        return block

    def create_pi_creatures(self):
        creatures = DistributedLedgerScene.create_pi_creatures(self)
        VGroup(
            self.alice, self.alice.label,
            self.charlie, self.charlie.label,
        ).shift(LEFT)
        return creatures

#Out of order
class FromBankToDecentralizedSystem(DistributedBlockChainScene):
    CONFIG = {
        "n_blocks" : 5,
        "ledger_height" : 3,
    }
    def construct(self):
        self.remove_bank()
        self.show_block_chains()
        self.add_crypto_terms()
        self.set_aside_everything()

    def remove_bank(self):
        bank = SVGMobject(
            file_name = "bank_building",
            color = LIGHT_GREY,
            height = 3,
        )
        cross = Cross(bank)
        cross.set_stroke(width = 10)
        group = VGroup(bank, cross)

        self.play(LaggedStartMap(DrawBorderThenFill, bank))
        self.play(ShowCreation(cross))
        self.wait()
        self.play(
            group.next_to, FRAME_X_RADIUS*RIGHT, RIGHT,
            rate_func = running_start,
            path_arc = -np.pi/6,
        )
        self.wait()
        self.remove(group)

    def show_block_chains(self):
        creatures = self.pi_creatures
        creatures.center()
        VGroup(self.charlie, self.you).to_edge(DOWN)
        chains = self.get_distributed_ledgers()
        for pi, chain in zip(creatures, chains):
            pi.scale_in_place(1.5)
            pi.shift(0.5*pi.get_center()[0]*RIGHT)
            chain.next_to(pi, UP)
        center_chain = self.get_block_chain()
        center_chain.scale(2)
        center_chain.center()

        self.play(LaggedStartMap(FadeIn, creatures, run_time = 1))
        self.play(
            LaggedStartMap(FadeIn, center_chain.blocks, run_time = 1),
            ShowCreation(center_chain.arrows),
        )
        self.wait()
        self.play(
            ReplacementTransform(VGroup(center_chain), chains),
            *[
                ApplyMethod(pi.change, "pondering", pi.ledger)
                for pi in creatures
            ]
        )
        self.wait()

    def add_crypto_terms(self):
        terms = TextMobject(
            "Digital signatures \\\\",
            "Cryptographic hash functions",
        )
        terms.set_color_by_tex("signature", BLUE)
        terms.set_color_by_tex("hash", YELLOW)
        for term in terms:
            self.play(Write(term, run_time = 1))
            self.wait()
        self.digital_signature = terms[0]

    def set_aside_everything(self):
        digital_signature = self.digital_signature
        ledger = LedgerScene.get_ledger(self)
        LedgerScene.add_payment_line_to_ledger(self, 
            "Alice", "Bob", "40",
        )
        LedgerScene.add_payment_line_to_ledger(self,
            "Charlie", "Alice", "60",
        )
        ledger.next_to(ORIGIN, LEFT)

        self.remove(digital_signature)
        everything = VGroup(*self.get_top_level_mobjects())

        self.play(
            Animation(digital_signature),
            everything.scale, 0.1,
            everything.to_corner, DOWN+LEFT,
        )
        self.play(
            Write(ledger),
            digital_signature.next_to, ORIGIN, RIGHT
        )
        self.wait(2)

class IntroduceBlockCreator(DistributedBlockChainScene):
    CONFIG = {
        "n_block_creators" : 3,
        "n_pow_guesses" : 60,
    }
    def construct(self):
        self.add_network()
        self.add_block_creators()
        self.broadcast_transactions()
        self.collect_transactions()
        self.find_proof_of_work()
        self.add_block_reward()
        self.comment_on_block_reward()
        self.write_miners()
        self.broadcast_block()

    def add_network(self):
        network = self.get_large_network()
        network.remove(network.lines)
        network.scale(0.7)
        ledgers = self.get_distributed_ledgers()
        self.add(network, ledgers)
        VGroup(network, ledgers).to_edge(RIGHT)

    def add_block_creators(self):
        block_creators = VGroup()
        labels = VGroup()
        everything = VGroup()
        for x in range(self.n_block_creators):
            block_creator = PiCreature(color = GREY)
            block_creator.set_height(self.alice.get_height())
            label = TextMobject("Block creator %d"%(x+1))
            label.scale(0.7)
            label.next_to(block_creator, DOWN, SMALL_BUFF)
            block_creator.label = label
            block_creators.add(block_creator)
            labels.add(label)
            everything.add(VGroup(block_creator, label))
        everything.arrange(DOWN, buff = LARGE_BUFF)
        everything.to_edge(LEFT)

        self.play(LaggedStartMap(FadeIn, everything))
        self.pi_creatures.add(*block_creators)
        self.wait()

        self.block_creators = block_creators
        self.block_creator_labels = labels

    def broadcast_transactions(self):
        payment_parts = [
            ("Alice", "Bob", 20),
            ("Bob", "Charlie", 10),
            ("Charlie", "You", 50),
            ("You", "Alice", 30),
        ]
        payments = VGroup()
        payment_targets = VGroup()
        for from_name, to_name, amount in payment_parts:
            verb = "pay" if from_name == "You" else "pays"
            payment = TextMobject(
                from_name, verb, to_name, "%d LD"%amount
            )
            payment.set_color_by_tex("LD", YELLOW)
            for name in self.get_names():
                payment.set_color_by_tex(
                    name.capitalize(),
                    self.get_color_from_name(name)
                )
            payment.scale(0.7)
            payment.generate_target()
            payment_targets.add(payment.target)

            pi = getattr(self, from_name.lower())
            payment.scale(0.1)
            payment.set_fill(opacity = 0)
            payment.move_to(pi)
            payments.add(payment)
        payment_targets.arrange(DOWN, aligned_edge = LEFT)
        payment_targets.next_to(
            self.block_creator_labels, RIGHT,
            MED_LARGE_BUFF
        )
        payment_targets.shift(UP)

        anims = []
        alpha_range = np.linspace(0, 0.5, len(payments))
        for pi, payment, alpha in zip(self.pi_creatures, payments, alpha_range):
            rf1 = squish_rate_func(smooth, alpha, alpha+0.5)
            rf2 = squish_rate_func(smooth, alpha, alpha+0.5)
            anims.append(Broadcast(
                pi, rate_func = rf1,
                big_radius = 3,
            ))
            anims.append(MoveToTarget(payment, rate_func = rf2))

        self.play(*anims, run_time = 5)
        self.payments = payments

    def collect_transactions(self):
        creator = self.block_creators[0]
        block = self.get_block()
        block.stretch_to_fit_height(4)
        block.stretch_to_fit_width(3.5)
        block.next_to(creator.label, RIGHT, MED_LARGE_BUFF)
        block.to_edge(UP)

        payments = self.payments
        payments.generate_target()
        payments.target.set_height(1.5)
        payments.target.move_to(block)

        prev_hash = TextMobject("Prev hash")
        prev_hash.set_color(BLUE)
        prev_hash.set_height(0.3)
        prev_hash.next_to(block.get_top(), DOWN, MED_SMALL_BUFF)
        block.add(prev_hash)

        self.play(
            FadeIn(block),
            MoveToTarget(payments),
            creator.change, "raise_right_hand"
        )
        self.wait()
        block.add(payments)

        self.block = block

    def find_proof_of_work(self):
        block = self.block

        arrow = Arrow(UP, ORIGIN, buff = 0)
        arrow.next_to(block, DOWN)
        sha = TextMobject("SHA256")
        sha.scale(0.7)
        sha.next_to(arrow, RIGHT)
        arrow.add(sha)

        self.add(arrow)
        for x in range(self.n_pow_guesses):
            guess = Integer(random.randint(10**11, 10**12))
            guess.set_color(GREEN)
            guess.set_height(0.3)
            guess.next_to(block.get_bottom(), UP, MED_SMALL_BUFF)

            if x == self.n_pow_guesses - 1:
                digest = sha256_tex_mob(str(x), 60)
                VGroup(*digest[:60]).set_color(YELLOW)
            else:
                digest = sha256_tex_mob(str(x))
            digest.set_width(block.get_width())
            digest.next_to(arrow.get_end(), DOWN)

            self.add(guess, digest)
            self.wait(1./20)
            self.remove(guess, digest)
        proof_of_work = guess
        self.add(proof_of_work, digest)
        block.add(proof_of_work)
        self.wait()

        self.hash_group = VGroup(arrow, digest)

    def add_block_reward(self):
        payments = self.payments
        new_transaction = TextMobject(
            self.block_creator_labels[0].get_tex_string(),
            "gets", "10 LD"
        )
        new_transaction[0].set_color(LIGHT_GREY)
        new_transaction.set_color_by_tex("LD", YELLOW)
        new_transaction.set_height(payments[0].get_height())
        new_transaction.move_to(payments.get_top())
        payments.generate_target()
        payments.target.next_to(new_transaction, DOWN, SMALL_BUFF, LEFT)
        new_transaction.shift(SMALL_BUFF*UP)

        self.play(
            MoveToTarget(payments),
            Write(new_transaction)
        )
        payments.add_to_back(new_transaction)
        self.wait()

    def comment_on_block_reward(self):
        reward = self.payments[0]
        reward_rect = SurroundingRectangle(reward)
        big_rect = SurroundingRectangle(self.ledgers)
        big_rect.set_stroke(width = 0)
        big_rect.set_fill(BLACK, opacity = 1)

        comments = VGroup(*list(map(TextMobject, [
            "- ``Block reward''",
            "- No sender/signature",
            "- Adds to total money supply",
        ])))
        comments.arrange(DOWN, aligned_edge = LEFT)
        comments.move_to(big_rect, UP+LEFT)

        pi_creatures = self.pi_creatures
        self.pi_creatures = VGroup()

        self.play(ShowCreation(reward_rect))
        self.play(FadeIn(big_rect))
        for comment in comments:
            self.play(FadeIn(comment))
            self.wait(2)
        self.play(*list(map(FadeOut, [big_rect, comments, reward_rect])))

        self.pi_creatures = pi_creatures

    def write_miners(self):
        for label in self.block_creator_labels:
            tex = label.get_tex_string()
            new_label = TextMobject("Miner " + tex[-1])
            new_label.set_color(label.get_color())
            new_label.replace(label, dim_to_match = 1)
            self.play(Transform(label, new_label))
        top_payment = self.payments[0]
        new_top_payment = TextMobject("Miner 1", "gets", "10 LD")
        new_top_payment[0].set_color(LIGHT_GREY)
        new_top_payment[-1].set_color(YELLOW)
        new_top_payment.set_height(top_payment.get_height())
        new_top_payment.move_to(top_payment, LEFT)
        self.play(Transform(top_payment, new_top_payment))
        self.wait()

    def broadcast_block(self):
        old_chains = self.block_chains
        self.n_blocks = 4
        new_chains = self.get_distributed_ledgers()
        block_target_group = VGroup()
        anims = []
        arrow_creations = []
        for old_chain, new_chain  in zip(old_chains, new_chains):
            for attr in "blocks", "arrows":
                pairs = list(zip(
                    getattr(old_chain, attr), 
                    getattr(new_chain, attr), 
                ))
                for m1, m2 in pairs:
                    anims.append(Transform(m1, m2))
            arrow_creations.append(ShowCreation(new_chain.arrows[-1]))
            block_target = self.block.copy()
            block_target.replace(new_chain.blocks[-1], stretch = True)
            block_target_group.add(block_target)
        anims.append(Transform(
            VGroup(self.block),
            block_target_group
        ))
        anims.append(Broadcast(self.block, n_circles = 4))
        anims.append(FadeOut(self.hash_group))
        anims.append(ApplyMethod(
            self.block_creators[0].change, "happy"
        ))

        self.play(*anims, run_time = 2)
        self.play(*it.chain(
            arrow_creations,
            [
                ApplyMethod(
                    pi.change, "hooray", 
                    pi.block_chain.get_right()
                )
                for pi in self.pi_creatures
            ]
        ))
        self.wait(3)

class MiningIsALottery(IntroduceBlockCreator):
    CONFIG = {
        "n_miners" : 3,
        "denomination" : "LD",
        "n_guesses" : 90,
        "n_nonce_digits" : 15,
    }
    def construct(self):
        self.add_blocks()
        self.add_arrows()
        self.make_guesses()

    def create_pi_creatures(self):
        IntroduceBlockCreator.create_pi_creatures(self)
        miners = VGroup(*[
            PiCreature(color = GREY)
            for n in range(self.n_miners)
        ])
        miners.scale(0.5)
        miners.arrange(DOWN, buff = LARGE_BUFF)
        miners.to_edge(LEFT)
        for x, miner in enumerate(miners):
            label = TextMobject("Miner %d"%(x+1))
            label.scale(0.7)
            label.next_to(miner, DOWN, SMALL_BUFF)
            miner.label = label
            self.add(label)
        self.miners = miners
        return miners

    def add_blocks(self):
        self.add(self.miners)

        blocks = VGroup()
        for miner in self.miners:
            block = self.get_block()
            block.stretch_to_fit_height(2)
            block.stretch_to_fit_width(3)
            block.next_to(miner, RIGHT)

            payments = self.get_payments(miner)
            payments.set_height(1)
            payments.move_to(block)
            block.add(payments)

            prev_hash = TextMobject("Prev hash")
            prev_hash.set_color(BLUE)
            prev_hash.set_height(0.2)
            prev_hash.next_to(block.get_top(), DOWN, SMALL_BUFF)
            block.add(prev_hash)

            miner.block = block
            miner.change("pondering", block)
            blocks.add(block)

        self.blocks = blocks
        self.add(blocks)

    def add_arrows(self):
        self.arrows = VGroup()
        for block in self.blocks:
            arrow = Arrow(LEFT, RIGHT)
            arrow.next_to(block)
            label = TextMobject("SHA256")
            label.scale(0.7)
            label.next_to(arrow, UP, buff = SMALL_BUFF)
            self.add(arrow, label)
            block.arrow = arrow
            self.arrows.add(VGroup(arrow, label))

    def make_guesses(self):
        for x in range(self.n_guesses):
            e = self.n_nonce_digits
            nonces = VGroup()
            digests = VGroup()
            for block in self.blocks:
                nonce = Integer(random.randint(10**e, 10**(e+1)))
                nonce.set_height(0.2)
                nonce.next_to(block.get_bottom(), UP, SMALL_BUFF)
                nonces.add(nonce)
                digest = sha256_tex_mob(str(x) + str(block))
                digest.set_height(block.get_height())
                digest.next_to(block.arrow, RIGHT)
                digests.add(digest)
            self.add(nonces, digests)
            self.wait(1./20)
            self.remove(nonces, digests)
        self.add(nonces, digests)

        winner_index = 1
        winner = self.miners[winner_index]
        losers = VGroup(*[m for m in self.miners if m is not winner])

        nonces[winner_index].set_color(GREEN)
        new_digest = sha256_tex_mob("Winner", 60)
        VGroup(*new_digest[:60]).set_color(YELLOW)
        old_digest = digests[winner_index]
        new_digest.replace(old_digest)
        Transform(old_digest, new_digest).update(1)

        self.play(
            winner.change, "hooray",
            *[
                ApplyMethod(VGroup(
                    self.blocks[i], self.arrows[i], 
                    nonces[i], digests[i]
                ).fade, 0.7)
                for i in range(len(self.blocks))
                if i is not winner_index
            ]
        )
        self.play(*[
            ApplyMethod(loser.change, "angry", winner)
            for loser in losers
        ])
        self.wait(2)

    #####

    def get_payments(self, miner):
        if not hasattr(self, "ledger"):
            self.get_ledger() ##Unused
        self.ledger.content.remove(*self.ledger.content[1:])

        lines = VGroup()

        miner_name = miner.label.get_tex_string()
        top_line = TextMobject(miner_name, "gets", "10 LD")
        top_line.set_color_by_tex(miner_name, LIGHT_GREY)
        top_line.set_color_by_tex("LD", YELLOW)
        lines.add(top_line)
        payments = [
            ("Alice", "Bob", 20),
            ("Charlie", "You", 50),
        ]
        for payment in payments:
            lines.add(self.add_payment_line_to_ledger(*payment))
        lines.add(TexMobject("\\vdots"))
        for line in lines:
            line.set_height(0.5)
        lines.arrange(
            DOWN, buff = SMALL_BUFF, aligned_edge = LEFT
        )
        lines[-1].next_to(lines[-2], DOWN, buff = SMALL_BUFF)
        return lines

class TwoBlockChains(DistributedBlockChainScene):
    CONFIG = {
        "n_blocks" : 5,
    }
    def construct(self):
        self.listen_for_new_blocks()
        self.defer_to_longer()
        self.break_tie()

    def listen_for_new_blocks(self):
        randy = self.randy
        chain = self.get_block_chain()
        chain.scale(1.5)
        chain.next_to(randy, UP+RIGHT)
        chain.shift_onto_screen()
        randy.change("raise_right_hand", chain)

        corners = [
            u1 * FRAME_X_RADIUS*RIGHT + u2 * FRAME_Y_RADIUS*UP
            for u1, u2 in it.product(*[[-1, 1]]*2)
        ]
        moving_blocks = chain.blocks[1:]

        self.add(randy, chain.blocks[0])
        for corner, block, arrow in zip(corners, moving_blocks, chain.arrows):
            block.save_state()
            block.next_to(corner, corner)
            self.play(
                ApplyMethod(
                    block.restore,
                    rate_func = squish_rate_func(smooth, 0.3, 0.8),
                    run_time = 3,
                ),
                Broadcast(corner, run_time = 3),
                ShowCreation(
                    arrow, 
                    rate_func = squish_rate_func(smooth, 0.8, 1),
                    run_time = 3,
                ),
            )
        self.wait()

        self.block_chain = chain

    def defer_to_longer(self):
        randy = self.randy
        self.n_blocks -= 1
        block_chains = VGroup(
            self.block_chain,
            self.get_block_chain().scale(1.5)
        )
        block_chains[1].next_to(randy, UP+LEFT)
        block_chains[1].shift_onto_screen()

        conflicting = TextMobject("Conflicting")
        conflicting.to_edge(UP)
        conflicting.set_color(RED)
        arrows = VGroup(*[
            Arrow(
                conflicting.get_bottom(), block_chain.get_top(),
                color = RED,
                buff = MED_LARGE_BUFF
            )
            for block_chain in block_chains
        ])

        longer_chain_rect = SurroundingRectangle(block_chains[0])
        longer_chain_rect.set_stroke(GREEN, 8)
        checkmark = TexMobject("\\checkmark")
        checkmark.set_color(GREEN)
        checkmark.next_to(longer_chain_rect, UP)
        checkmark.shift(RIGHT)

        chain = block_chains[1]
        chain.save_state()
        corner = FRAME_X_RADIUS*LEFT + FRAME_Y_RADIUS*UP
        chain.next_to(corner, UP+LEFT)
        self.play(
            randy.change, "confused", chain,
            Broadcast(corner),
            ApplyMethod(
                chain.restore,
                rate_func = squish_rate_func(smooth, 0.3, 0.7),
                run_time = 3
            )
        )
        self.play(
            Write(conflicting),
            *list(map(ShowCreation, arrows))
        )
        self.wait()
        self.play(ShowCreation(longer_chain_rect))
        self.play(Write(checkmark, run_time = 1))
        self.play(randy.change, "thinking", checkmark)
        self.wait()

        self.to_fade = VGroup(
            conflicting, arrows, 
            longer_chain_rect, checkmark
        )
        self.block_chains = block_chains

    def break_tie(self):
        to_fade = self.to_fade
        block_chains = self.block_chains
        randy = self.randy

        arrow = block_chains[1].arrows[-1]
        block = block_chains[1].blocks[-1]
        arrow_block = VGroup(arrow, block).copy()

        block_chains.generate_target()
        block_chains.target.arrange(
            DOWN, buff = MED_LARGE_BUFF, aligned_edge = LEFT
        )
        block_chains.target.next_to(randy, UP)
        block_chains.target.to_edge(LEFT)

        self.play(
            MoveToTarget(block_chains),
            FadeOut(to_fade),
            run_time = 1
        )
        arrow_block.next_to(block_chains[1], RIGHT, buff = 0)
        block_chains[1].add(arrow_block)
        self.play(
            randy.change, "confused", block_chains,
            FadeIn(arrow_block),
        )
        self.wait()

        arrow_block = arrow_block.copy()
        arrow_block.next_to(FRAME_X_RADIUS*RIGHT, RIGHT)
        self.play(
            ApplyMethod(
                arrow_block.next_to, block_chains[0], RIGHT, 0,
                run_time = 3,
                rate_func = squish_rate_func(smooth, 0.3, 0.8)
            ),
            Broadcast(arrow_block),
        )
        block_chains[0].add(arrow_block)
        rect = SurroundingRectangle(block_chains[0])
        rect.set_stroke(GREEN, 8)
        checkmark = TexMobject("\\checkmark")
        checkmark.next_to(rect, UP)
        checkmark.set_color(GREEN)

        self.play(
            ShowCreation(rect),
            Write(checkmark),
            randy.change, "happy", arrow_block
        )
        self.wait(2)


    ####

    def create_pi_creatures(self):
        randy = Randolph()
        randy.to_edge(DOWN)
        self.randy = randy
        return VGroup(randy)

class ReplaceCentralAuthorityWithWork(Scene):
    def construct(self):
        trust, central = words = TextMobject("Trust", "central authority")
        words.scale(1.5)
        cross = Cross(central)
        work = TextMobject("computational work")
        work.scale(1.5)
        work.move_to(central, LEFT)
        work.set_color(YELLOW)

        self.play(Write(words))
        self.play(ShowCreation(cross))
        central.add(cross)
        self.play(
            central.shift, DOWN,
            Write(work)
        )
        self.wait()

class AskAboutTrustingWork(TeacherStudentsScene):
    def construct(self):
        mode = "raise_left_hand"
        self.student_says(
            "Is trusting work \\\\ really enough?",
            target_mode = mode,
        )
        self.change_student_modes("confused", mode, "erm")
        self.wait(3)
        self.teacher_says(
            "Well, let's try\\\\ fooling someone",
            target_mode = "speaking"
        )
        self.wait(2)

class DoubleSpendingAttack(DistributedBlockChainScene):
    CONFIG = {
        "fraud_block_height" : 3,
    }
    def construct(self):
        self.initialize_characters()
        self.show_fraudulent_block()
        self.send_to_bob()
        self.dont_send_to_rest_of_network()

    def initialize_characters(self):
        network = self.get_large_network()
        network.scale(0.7)
        block_chains = self.get_distributed_ledgers()
        self.add(network, block_chains)
        self.play(self.alice.change, "conniving")
        self.wait()

    def show_fraudulent_block(self):
        block = self.get_fraud_block()
        block.next_to(self.alice, LEFT, LARGE_BUFF)
        block.remove(block.content)
        self.play(
            ShowCreation(block),
            Write(block.content),
            self.alice.change, "raise_left_hand"
        )
        block.add(block.content)
        self.wait()

        self.block = block

    def send_to_bob(self):
        block = self.block.copy()
        block.generate_target()
        block.target.replace(
            self.bob.block_chain.blocks[-1],
            stretch = True
        )
        arrow = self.bob.block_chain.arrows[-1].copy()
        VGroup(arrow, block.target).next_to(
            self.bob.block_chain.blocks[-1], RIGHT, buff = 0
        )

        self.play(
            MoveToTarget(block),
            self.alice.change, "happy"
        )
        self.play(ShowCreation(arrow))
        self.wait()

    def dont_send_to_rest_of_network(self):
        bubble = ThoughtBubble()
        words = TextMobject("Alice", "never \\\\ paid", "Bob")
        for name in "Alice", "Bob":
            words.set_color_by_tex(name, self.get_color_from_name(name))
        bubble.add_content(words)
        bubble.resize_to_content()
        bubble.add(*bubble.content)
        bubble.move_to(self.you.get_corner(UP+RIGHT), DOWN+LEFT)

        self.play(
            self.charlie.change, "shruggie",
            self.you.change, "shruggie",
        )
        self.play(LaggedStartMap(FadeIn, bubble))
        self.play(self.bob.change, "confused", words)
        self.wait(2)

    ###

    def get_fraud_block(self):
        block = self.get_block()
        block.set_height(self.fraud_block_height)
        content = VGroup()

        tuples = [
            ("Prev hash", UP, BLUE), 
            ("Proof of work", DOWN, GREEN),
        ]
        for word, vect, color in tuples:
            mob = TextMobject(word)
            mob.set_color(color)
            mob.set_height(0.07*block.get_height())
            mob.next_to(
                block.get_edge_center(vect), -vect,
                buff = 0.06*block.get_height()
            )
            content.add(mob)
            attr = word.lower().replace(" ", "_")
            setattr(block, attr, mob)

        payment = TextMobject("Alice", "pays", "Bob", "100 LD")
        for name in "Alice", "Bob":
            payment.set_color_by_tex(name, self.get_color_from_name(name))
        payment.set_color_by_tex("LD", YELLOW)
        payments = VGroup(
            TexMobject("\\vdots"),
            payment,
            TexMobject("\\vdots")
        )
        payments.arrange(DOWN)
        payments.set_width(0.9*block.get_width())
        payments.move_to(block)
        content.add(payments)

        block.content = content
        block.add(content)
        return block

class AliceRacesOtherMiners(DoubleSpendingAttack):
    CONFIG = {
        "n_frames_per_pow" : 3,
        "fraud_block_height" : 2,
        "n_miners" : 3,
        "n_proof_of_work_digits" : 11,
        "proof_of_work_update_counter" : 0,
    }
    def construct(self):
        self.initialize_characters()
        self.find_proof_of_work()
        self.receive_broadcast_from_other_miners()
        self.race_between_alice_and_miners()

    def initialize_characters(self):
        alice = self.alice
        bob = self.bob
        alice_l = VGroup(alice, alice.label)
        bob_l = VGroup(bob, bob.label)
        bob_l.move_to(ORIGIN)
        alice_l.to_corner(UP+LEFT)
        alice_l.shift(DOWN)
        self.add(bob_l, alice_l)

        chain = self.get_block_chain()
        chain.next_to(bob, UP)
        self.block_chain = chain
        self.add(chain)

        fraud_block = self.get_fraud_block()
        fraud_block.next_to(alice, RIGHT)
        fraud_block.to_edge(UP)
        proof_of_work = self.get_rand_int_mob()
        proof_of_work.replace(fraud_block.proof_of_work, dim_to_match = 1)
        fraud_block.content.remove(fraud_block.proof_of_work)
        fraud_block.content.add(proof_of_work)
        fraud_block.proof_of_work = proof_of_work
        self.fraud_block = fraud_block
        self.add(fraud_block)

        miners = VGroup(*[
            PiCreature(color = GREY)
            for x in range(self.n_miners)
        ])
        miners.set_height(alice.get_height())
        miners.arrange(RIGHT, buff = LARGE_BUFF)
        miners.to_edge(DOWN+LEFT)
        miners.shift(0.5*UP)
        miners_word = TextMobject("Miners")
        miners_word.next_to(miners, DOWN)
        self.miners = miners
        self.add(miners_word, miners)

        miner_blocks = VGroup()
        self.proofs_of_work = VGroup()
        self.add_foreground_mobject(self.proofs_of_work)
        for miner in miners:
            block = self.get_block()
            block.set_width(1.5*miner.get_width())
            block.next_to(miner, UP)

            transactions = self.get_block_filler(block)
            block.add(transactions)

            proof_of_work = self.get_rand_int_mob()
            prev_hash = TextMobject("Prev hash").set_color(BLUE)
            for mob, vect in (proof_of_work, DOWN), (prev_hash, UP):
                mob.set_height(0.1*block.get_height())
                mob.next_to(
                    block.get_edge_center(vect), -vect, 
                    buff = 0.05*block.get_height()
                )
                block.add(mob)
            block.proof_of_work = proof_of_work
            block.prev_hash = prev_hash
            self.proofs_of_work.add(proof_of_work)

            miner.block = block
            miner_blocks.add(block)
        self.add(miner_blocks)

    def find_proof_of_work(self):
        fraud_block = self.fraud_block
        chain = self.block_chain

        self.proofs_of_work.add(self.fraud_block.proof_of_work)
        self.wait(3)
        self.proofs_of_work.remove(self.fraud_block.proof_of_work)
        fraud_block.proof_of_work.set_color(GREEN)
        self.play(
            Indicate(fraud_block.proof_of_work),
            self.alice.change, "hooray"
        )
        self.wait()
    
        block = fraud_block.copy()        
        block.generate_target()
        block.target.replace(chain.blocks[-1], stretch = True)
        arrow = chain.arrows[-1].copy()
        VGroup(arrow, block.target).next_to(
            chain.blocks[-1], RIGHT, buff = 0
        )
        self.remove(fraud_block)
        self.clean_fraud_block_content()
        self.fraud_fork_head = block
        self.fraud_fork_arrow = arrow

        self.play(MoveToTarget(block))
        self.play(ShowCreation(arrow))
        self.play(self.alice.change, "happy")
        self.wait()

    def receive_broadcast_from_other_miners(self):
        winner = self.miners[-1]
        proof_of_work = winner.block.proof_of_work
        self.proofs_of_work.remove(proof_of_work)
        proof_of_work.set_color(GREEN)
        self.play(
            Indicate(proof_of_work),
            winner.change, "hooray"
        )
        block = winner.block.copy()
        proof_of_work.set_color(WHITE)
        self.remove(winner.block)

        ff_head = self.fraud_fork_head
        ff_arrow = self.fraud_fork_arrow
        arrow = ff_arrow.copy()
        movers = [ff_head, ff_arrow, block, arrow]
        for mover in movers:
            mover.generate_target()
        block.target.replace(ff_head, stretch = True)

        dist = 0.5*ff_head.get_height() + MED_SMALL_BUFF
        block.target.shift(dist*DOWN)
        ff_head.target.shift(dist*UP)
        arrow.target[1].shift(dist*DOWN)
        arrow.target.points[-2:] += dist*DOWN
        ff_arrow.target[1].shift(dist*UP)
        ff_arrow.target.points[-2:] += dist*UP

        self.play(
            Broadcast(block),
            *[
                MoveToTarget(
                    mover, run_time = 3, 
                    rate_func = squish_rate_func(smooth, 0.3, 0.8)
                )
                for mover in movers
            ]
        )
        self.play(
            FadeIn(winner.block),
            winner.change_mode, "plain",
            self.alice.change, "sassy",
        )
        self.proofs_of_work.add(winner.block.proof_of_work)
        self.wait(2)
        self.play(
            self.alice.change, "pondering",
            FadeIn(self.fraud_block)
        )
        self.proofs_of_work.add(self.fraud_block.proof_of_work)

        self.valid_fork_head = block

    def race_between_alice_and_miners(self):
        last_fraud_block = self.fraud_fork_head
        last_valid_block = self.valid_fork_head
        chain = self.block_chain
        winners = [
            "Alice", "Alice",
            "Miners", "Miners", "Miners",
            "Alice", "Miners", "Miners", "Miners",
            "Alice", "Miners", "Miners"
        ]

        self.revert_to_original_skipping_status()
        for winner in winners:
            self.wait()
            if winner == "Alice":
                block = self.fraud_block
                prev_block = last_fraud_block
            else:
                block = random.choice(self.miners).block
                prev_block = last_valid_block
            block_copy = block.deepcopy()
            block_copy.proof_of_work.set_color(GREEN)
            block_copy.generate_target()
            block_copy.target.replace(chain.blocks[1], stretch = True)
            arrow = chain.arrows[0].copy()
            VGroup(arrow, block_copy.target).next_to(
                prev_block, RIGHT, buff = 0
            )
            anims = [
                MoveToTarget(block_copy, run_time = 2),
                ShowCreation(
                    arrow,
                    run_time = 2,
                    rate_func = squish_rate_func(smooth, 0.5, 1),
                ),
                FadeIn(block),
            ]
            if winner == "Alice":
                last_fraud_block = block_copy
            else:
                last_valid_block = block_copy
                anims.append(Broadcast(block, run_time = 2))
            self.proofs_of_work.remove(block.proof_of_work)
            self.play(*anims)
            self.proofs_of_work.add(block.proof_of_work)


    #####

    def wait(self, time = 1):
        self.play(
            Animation(VGroup(*self.foreground_mobjects)),
            run_time = time
        )

    def update_frame(self, *args, **kwargs):
        self.update_proofs_of_work()
        Scene.update_frame(self, *args, **kwargs)

    def update_proofs_of_work(self):
        self.proof_of_work_update_counter += 1
        if self.proof_of_work_update_counter%self.n_frames_per_pow != 0:
            return
        for proof_of_work in self.proofs_of_work:
            new_pow = self.get_rand_int_mob()
            new_pow.replace(proof_of_work, dim_to_match = 1)
            Transform(proof_of_work, new_pow).update(1)

    def get_rand_int_mob(self):
        e = self.n_proof_of_work_digits
        return Integer(random.randint(10**e, 10**(e+1)))

    def clean_fraud_block_content(self):
        content = self.fraud_block.content
        payments = content[1]
        content.remove(payments)
        transactions = self.get_block_filler(self.fraud_block)
        content.add(transactions)

    def get_block_filler(self, block):
        result = TextMobject("$\\langle$Transactions$\\rangle$")
        result.set_width(0.8*block.get_width())
        result.move_to(block)
        return result

class WhenToTrustANewBlock(DistributedBlockChainScene):
    def construct(self):
        chain = self.block_chain = self.get_block_chain()
        chain.scale(2)
        chain.to_edge(LEFT)
        self.add(chain)

        words = list(map(TextMobject, [
            "Don't trust yet",
            "Still don't trust",
            "...a little more...",
            "Maybe trust",
            "Probably safe",
            "Alright, you're good."
        ]))
        colors = [RED, RED, YELLOW, YELLOW, GREEN, GREEN]
        self.add_new_block()
        arrow = Arrow(UP, DOWN, color = RED)
        arrow.next_to(chain.blocks[-1], UP)
        for word, color in zip(words, colors):
            word.set_color(color)
            word.next_to(arrow, UP)
        word = words[0]
        self.play(
            FadeIn(word),
            ShowCreation(arrow)
        )
        for new_word in words[1:]:
            kwargs = {
                "run_time" : 3,
                "rate_func" : squish_rate_func(smooth, 0.7, 1)
            }
            self.add_new_block(
                Transform(word, new_word, **kwargs),
                ApplyMethod(
                    arrow.set_color, new_word.get_color(),
                    **kwargs
                )
            )
        self.wait(2)

    def get_block(self):
        block = DistributedBlockChainScene.get_block(self)
        tuples = [
            ("Prev hash", UP, BLUE), 
            ("Proof of work", DOWN, GREEN),
        ]
        for word, vect, color in tuples:
            mob = TextMobject(word)
            mob.set_color(color)
            mob.set_height(0.07*block.get_height())
            mob.next_to(
                block.get_edge_center(vect), -vect,
                buff = 0.06*block.get_height()
            )
            block.add(mob)
            attr = word.lower().replace(" ", "_")
            setattr(block, attr, mob)
        transactions = TextMobject("$\\langle$Transactions$\\rangle$")
        transactions.set_width(0.8*block.get_width())
        transactions.move_to(block)
        block.add(transactions)
        return block

    def add_new_block(self, *added_anims):
        blocks = self.block_chain.blocks
        arrows = self.block_chain.arrows
        block = blocks[-1].copy()
        arrow = arrows[-1].copy()
        VGroup(block, arrow).next_to(blocks[-1], RIGHT, buff = 0)
        corner = FRAME_X_RADIUS*RIGHT + FRAME_Y_RADIUS*UP
        block.save_state()
        block.next_to(corner, UP+RIGHT)

        self.play(
            Broadcast(block),
            ApplyMethod(
                block.restore,
                run_time = 3,
                rate_func = squish_rate_func(smooth, 0.3, 0.8),
            ),
            ShowCreation(
                arrow,
                run_time = 3,
                rate_func = squish_rate_func(smooth, 0.7, 1),
            ),
            *added_anims
        )
        arrows.add(arrow)
        blocks.add(block)

class MainIdeas(Scene):
    def construct(self):
        title = TextMobject("Main ideas")
        title.scale(1.5)
        h_line = Line(LEFT, RIGHT)
        h_line.set_width(FRAME_X_RADIUS)
        h_line.next_to(title, DOWN)
        VGroup(title, h_line).to_corner(UP+LEFT)

        ideas = VGroup(*[
            TextMobject("$\\cdot$ " + words)
            for words in [
                "Digital signatures",
                "The ledger is the currency",
                "Decentralize",
                "Proof of work",
                "Block chain",
            ]
        ])
        colors = BLUE, WHITE, RED, GREEN, YELLOW
        for idea, color in zip(ideas, colors):
            idea.set_color(color)
        ideas.arrange(
            DOWN,
            buff = MED_LARGE_BUFF,
            aligned_edge = LEFT
        )
        ideas.next_to(h_line, DOWN)

        self.add(title, h_line)
        for idea in ideas:
            self.play(LaggedStartMap(FadeIn, idea))
        self.wait()

class VariableProofOfWork(WhenToTrustANewBlock):
    CONFIG = {
        "block_height" : 3,
        "block_width" : 3,
        "n_guesses" : 60,
        "n_proof_of_work_digits" : 11,
        "n_miners" : 6,
    }
    def construct(self):
        self.add_miner_and_hash()
        self.change_requirement()
        self.add_more_miners()

    def add_miner_and_hash(self):
        miner = PiCreature(color = GREY)
        miner.scale(0.7)
        miner.to_edge(LEFT)

        block = self.get_block()
        block.next_to(miner, RIGHT)
        old_proof_of_work = block.proof_of_work
        proof_of_work = self.get_rand_int_mob()
        proof_of_work.replace(old_proof_of_work, dim_to_match = 1)
        block.remove(old_proof_of_work)
        block.add(proof_of_work)
        block.proof_of_work = proof_of_work

        arrow = Arrow(LEFT, RIGHT)
        arrow.next_to(block)
        sha_tex = TextMobject("SHA256")
        sha_tex.scale(0.7)
        sha_tex.next_to(arrow, UP, SMALL_BUFF)
        sha_tex.set_color(YELLOW)
        arrow.add(sha_tex)

        digest = sha256_tex_mob("Random")
        digest.next_to(arrow.get_end(), RIGHT)

        miner.change("pondering", digest)

        self.add(miner, block, arrow, digest)
        for x in range(self.n_guesses):
            new_pow = self.get_rand_int_mob()
            new_pow.replace(proof_of_work, dim_to_match = 1)
            Transform(proof_of_work, new_pow).update(1)
            if x == self.n_guesses-1:
                n_zeros = 60
            else:
                n_zeros = 0
            new_digest = sha256_tex_mob(str(x+1), n_zeros)
            new_digest.replace(digest)
            Transform(digest, new_digest).update(1)
            self.wait(1./20)
        proof_of_work.set_color(GREEN)
        VGroup(*digest[:60]).set_color(YELLOW)

        self.miner = miner
        self.block = block
        self.arrow = arrow
        self.digest = digest

    def change_requirement(self):
        digest = self.digest
        requirement = TextMobject(
            "Must start with \\\\",
            "60", "zeros"
        )
        requirement.next_to(digest, UP, MED_LARGE_BUFF)
        self.n_zeros_mob = requirement.get_part_by_tex("60")
        self.n_zeros_mob.set_color(YELLOW)

        self.play(Write(requirement, run_time = 2))
        self.wait(2)
        for n_zeros in 30, 32, 35, 37, 42:
            self.change_challenge(n_zeros)
            self.wait()

    def add_more_miners(self):
        miner = self.miner
        block = self.block
        miner_block = VGroup(miner, block)
        target = miner_block.copy()
        target[1].scale(
            0.5, about_point = miner.get_right()
        )
        copies = VGroup(*[
            target.copy() 
            for x in range(self.n_miners - 1)
        ])
        everyone = VGroup(target, *copies)
        everyone.arrange(DOWN)
        everyone.set_height(FRAME_HEIGHT - LARGE_BUFF)
        everyone.to_corner(UP+LEFT)

        self.play(Transform(miner_block, target))
        self.play(LaggedStartMap(FadeIn, copies))
        self.change_challenge(72)
        self.wait(2)

    ###
    def change_challenge(self, n_zeros):
        digest = self.digest
        proof_of_work = self.block.proof_of_work
        n_zeros_mob = self.n_zeros_mob

        new_digest = sha256_tex_mob(str(n_zeros), n_zeros)
        new_digest.move_to(digest)
        VGroup(*new_digest[:n_zeros]).set_color(YELLOW)
        new_n_zeros_mob = TexMobject(str(n_zeros))
        new_n_zeros_mob.move_to(n_zeros_mob)
        new_n_zeros_mob.set_color(n_zeros_mob.get_color())
        new_pow = self.get_rand_int_mob()
        new_pow.replace(proof_of_work, dim_to_match = 1)
        new_pow.set_color(proof_of_work.get_color())

        self.play(
            Transform(n_zeros_mob, new_n_zeros_mob),
            Transform(
                digest, new_digest,
                lag_ratio = 0.5
            ),
            Transform(proof_of_work, new_pow),
        )

    def get_rand_int_mob(self):
        e = self.n_proof_of_work_digits
        return Integer(random.randint(10**e, 10**(e+1)))

class CompareBlockTimes(Scene):
    def construct(self):
        title = TextMobject("Average block time")
        title.scale(1.5)
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT)
        h_line.set_width(FRAME_X_RADIUS)
        h_line.next_to(title, DOWN, SMALL_BUFF)

        examples = VGroup(
            TextMobject("BTC: ", "10 minutes"),
            TextMobject("ETH: ", "15 Seconds"),
            TextMobject("XRP: ", "3.5 Seconds"),
            TextMobject("LTC: ", "2.5 Minutes"),
        )
        examples.arrange(
            DOWN, 
            buff = LARGE_BUFF,
            aligned_edge = LEFT,
        )
        examples.next_to(h_line, DOWN)
        logos = VGroup(
            BitcoinLogo(),
            EthereumLogo(),
            ImageMobject("ripple_logo"),
            LitecoinLogo(),
        )
        colors = [BITCOIN_COLOR, GREEN, BLUE_B, LIGHT_GREY]
        for logo, example, color in zip(logos, examples, colors):
            logo.set_height(0.5)
            logo.next_to(example, LEFT)
            example[0].set_color(color)

        self.add(title, h_line)
        self.play(
            FadeIn(examples[0]),
            DrawBorderThenFill(logos[0])
        )
        self.wait()
        self.play(*[
            LaggedStartMap(FadeIn, VGroup(*group[1:]))
            for group in (examples, logos)
        ])
        self.wait(2)

    # def get_ethereum_logo(self):
    #     logo = SVGMobject(
    #         file_name = "ethereum_logo",
    #         height = 1,
    #     )
    #     logo.set_fill(GREEN, 1)
    #     logo.set_stroke(WHITE, 3)
    #     logo.set_color_by_gradient(GREEN_B, GREEN_D)
    #     logo.set_width(1)
    #     logo.center()
    #     self.add(SurroundingRectangle(logo))
    #     return logo

class BlockRewards(Scene):
    def construct(self):
        title = TextMobject("Block rewards")
        title.scale(1.5)
        logo = BitcoinLogo()
        logo.set_height(0.75)
        logo.next_to(title, LEFT)
        title.add(logo)
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT)
        h_line.set_width(FRAME_X_RADIUS)
        h_line.next_to(title, DOWN)
        self.add(title, logo, h_line)

        rewards = VGroup(
            TextMobject("Jan 2009 - Nov 2012:", "50", "BTC"),
            TextMobject("Nov 2012 - Jul 2016:", "25", "BTC"),
            TextMobject("Jul 2016 - Feb 2020$^*$:", "12.5", "BTC"),
            TextMobject("Feb 2020$^*$ - Sep 2023$^*$:", "6.25", "BTC"),
        )
        rewards.arrange(
            DOWN, 
            buff = MED_LARGE_BUFF,
            aligned_edge = LEFT
        )
        rewards.next_to(h_line, DOWN)
        for reward in rewards:
            reward[1].set_color(YELLOW)

        footnote = TextMobject(
            "$^*$ Extrapolating from the 25 BTC reward period"
        )
        footnote.scale(0.5)
        footnote.to_corner(DOWN+RIGHT)

        self.play(LaggedStartMap(
            FadeIn, rewards,
            run_time = 4,
            lag_ratio = 0.5
        ))
        self.play(FadeIn(footnote))
        self.wait(3)

class ShowFirstFewBlocks(ExternallyAnimatedScene):
    pass

class ShowGeometricSum(Scene):
    def construct(self):
        equation = TexMobject(
            "210{,}000", "(", 
            "50", "+", "25", "+", "12.5", "+", 
            "6.25", "+\\cdots", ")", "=", "21{,}000{,}000"
        )
        numbers = ["50", "25", "12.5", "6.25"]
        colors = color_gradient([BLUE_D, BLUE_B], 4)
        for tex, color in zip(numbers, colors):
            equation.set_color_by_tex(tex, color)
        equation[-1].set_color(YELLOW)

        self.add(*equation[:2] + equation[-3:-1])
        for i in range(2, 9, 2):
            self.play(FadeIn(VGroup(*equation[i:i+2])))
        self.wait()
        self.play(Write(equation[-1]))
        self.wait(2)

class TransactionFeeExample(PiCreatureScene):
    def construct(self):
        alice = self.pi_creature
        payment = TextMobject(
            "Alice", "pays", "Bob", "0.42 BTC",
        )
        payment.set_color_by_tex("Alice", BLUE_C)
        payment.set_color_by_tex("Bob", MAROON)
        payment.set_color_by_tex("BTC", YELLOW)
        payment.move_to(2.5*UP)

        fee = TextMobject("And leaves", "0.001 BTC", "to the miner")
        fee.set_color_by_tex("BTC", YELLOW)
        fee.next_to(payment, DOWN)

        signature = TextMobject(
            "$\\langle$Alice's digital signature$\\rangle$"
        )
        signature.set_color(BLUE_C)
        signature.next_to(fee, DOWN)

        group = VGroup(payment, fee, signature)
        rect = SurroundingRectangle(group, color = BLUE_B)

        incentive_words = TextMobject(
            "Incentivizes miner \\\\ to include"
        )
        incentive_words.next_to(rect, DOWN, buff = 1.5)
        incentive_words.shift(2*RIGHT)
        arrow = Arrow(
            incentive_words.get_top(),
            rect.get_bottom(),
            buff = MED_LARGE_BUFF
        )

        fee.save_state()
        fee.shift(DOWN)
        fee.set_fill(opacity = 0)

        self.play(Write(payment))
        self.wait()
        self.play(
            alice.change, "raise_right_hand", payment,
            fee.restore,
        )
        self.play(Write(signature))
        self.play(
            ShowCreation(rect),
            alice.change_mode, "happy"
        )
        self.wait()
        self.play(
            Write(incentive_words),
            ShowCreation(arrow),
            alice.change, "pondering"
        )
        self.wait(2)

    def create_pi_creature(self):
        alice = PiCreature(color = BLUE_C)
        alice.to_edge(DOWN)
        alice.shift(FRAME_X_RADIUS*LEFT/2)
        return alice

class ShowBitcoinBlockSize(LedgerScene):
    CONFIG = {
        "denomination" : "BTC"
    }
    def construct(self):
        block = VGroup()
        ledger = self.get_ledger()

        payments = VGroup(*[
            self.add_payment_line_to_ledger(*args)
            for args in [
                ("Alice", "Bob", "0.42"),
                ("You", "Charlie", "3.14"),
                ("Bob", "You", "2.72"),
                ("Alice", "Charlie", "4.67"),
            ]
        ])
        dots = TexMobject("\\vdots")
        dots.next_to(payments, DOWN)
        payments.add(dots)
        payments.to_edge(LEFT)
        payments.shift(DOWN+0.5*RIGHT)
        payments_rect = SurroundingRectangle(
            payments, color = WHITE, buff = MED_LARGE_BUFF
        )
        block.add(payments_rect, payments)

        tuples = [
            ("Prev hash", UP, BLUE_C), 
            ("Proof of work", DOWN, GREEN),
        ]
        for word, vect, color in tuples:
            mob = TextMobject(word)
            mob.set_color(color)
            rect = SurroundingRectangle(
                mob, color = WHITE, buff = MED_SMALL_BUFF
            )
            VGroup(mob, rect).next_to(payments_rect, vect, 0)
            rect.stretch_to_fit_width(payments_rect.get_width())
            block.add(mob, rect)

        title = VGroup(
            BitcoinLogo(height = 0.75), 
            TextMobject("Block").scale(1.5)
        )
        title.arrange(RIGHT, SMALL_BUFF)
        title.next_to(block, UP)

        brace = Brace(payments_rect, RIGHT)
        limit = brace.get_text(
            "Limited to\\\\", 
            "$\\sim 2{,}400$", "transactions"
        )
        limit.set_color_by_tex("2{,}400", RED)

        self.add(title, block)
        self.remove(payments)
        self.play(
            GrowFromCenter(brace),
            Write(limit)
        )
        self.play(LaggedStartMap(FadeIn, payments))
        self.wait()

        ####Visa

        visa_logo = SVGMobject(
            file_name = "visa_logo",
            height = 0.5,
            stroke_width = 0,
            fill_color = BLUE_D,
            fill_opacity = 1,
        )
        visa_logo[-1].set_color("#faa61a")
        visa_logo.sort()
        avg_rate = TextMobject("Avg: $1{,}700$/second")
        max_rate = TextMobject("Max: $>24{,}000$/second")
        rates = VGroup(avg_rate, max_rate)
        rates.scale(0.8)
        rates.arrange(DOWN, aligned_edge = LEFT)
        rates.next_to(visa_logo, RIGHT, buff = MED_SMALL_BUFF)
        visa = VGroup(visa_logo, rates)
        visa.to_corner(UP+RIGHT)

        self.play(LaggedStartMap(DrawBorderThenFill, visa_logo))
        self.play(LaggedStartMap(FadeIn, avg_rate))
        self.wait()
        self.play(LaggedStartMap(FadeIn, max_rate))
        self.wait(2)

class CurrentAverageFees(Scene):
    def construct(self):
        fees = TextMobject(
            "Current average fees: ",
            "$\\sim 0.0013$ BTC", 
            "$\\approx$", "\\$3.39"
        )
        fees.set_color_by_tex("BTC", YELLOW)
        fees.set_color_by_tex("\\$", GREEN)
        fees.to_edge(UP)

        self.play(Write(fees))
        self.wait()

class HighlightingAFewFees(ExternallyAnimatedScene):
    pass

class TopicsNotCovered(TeacherStudentsScene):
    def construct(self):
        title = TextMobject("Topics not covered:")
        title.to_corner(UP+LEFT)
        title.set_color(YELLOW)
        title.save_state()
        title.shift(DOWN)
        title.set_fill(opacity = 0)

        topics = VGroup(*list(map(TextMobject, [
            "Merkle trees",
            "Alternatives to proof of work",
            "Scripting",
            "$\\vdots$",
            "(See links in description)",
        ])))
        topics.arrange(DOWN, aligned_edge = LEFT)
        topics[-2].next_to(topics[-3], DOWN)
        topics.next_to(title, RIGHT)
        topics.to_edge(UP)

        self.play(
            title.restore,
            self.teacher.change_mode, "raise_right_hand"
        )
        for topic in topics:
            self.change_student_modes(
                "confused", "thinking","pondering",
                look_at_arg = topic,
                added_anims = [LaggedStartMap(FadeIn, topic)]
            )
            self.wait()

class Exchange(Animation):
    CONFIG = {
        "rate_func" : None,
    }
    def __init__(self, exchange, **kwargs):
        self.swap = Swap(
            exchange.left,
            exchange.right,
        )
        self.changed_symbols_yet = False
        Animation.__init__(self, exchange, **kwargs)

    def interpolate_mobject(self, alpha):
        exchange = self.mobject
        if alpha < 1./3:
            self.swap.update(3*alpha)
        elif alpha < 2./3:
            sub_alpha = alpha*3 - 1
            group = VGroup(exchange.left, exchange.right)
            group.set_fill(opacity = 1-smooth(sub_alpha))
        else:
            if not self.changed_symbols_yet:
                new_left = random.choice(
                    exchange.cryptocurrencies
                ).copy()
                new_left.move_to(exchange.right)
                new_right = random.choice(
                    exchange.currencies
                ).copy()
                new_right.move_to(exchange.left)
                Transform(exchange.left, new_left).update(1)
                Transform(exchange.right, new_right).update(1)
                self.changed_symbols_yet = True
            sub_alpha = 3*alpha - 2
            group = VGroup(exchange.left, exchange.right)
            group.set_fill(opacity = smooth(sub_alpha))

class ShowManyExchanges(Scene):
    CONFIG = {
        "n_rows" : 2,
        "n_cols" : 8,
        "shift_radius" : 0.5,
        "run_time" : 30,
    }
    def construct(self):
        cryptocurrencies = self.get_cryptocurrencies()
        currencies = self.get_currencies()
        for currency in it.chain(currencies, cryptocurrencies):
            currency.set_height(0.5)
            currency.align_data(EthereumLogo())
        exchange = VGroup(*[
            Arrow(
                p1, p2,
                path_arc = np.pi,
                buff = MED_LARGE_BUFF
            )
            for p1, p2 in [(LEFT, RIGHT), (RIGHT, LEFT)]
        ]).set_color(WHITE)
        exchanges = VGroup(*[
            VGroup(*[
                exchange.copy()
                for x in range(3)
            ]).arrange(RIGHT, buff = 2*LARGE_BUFF)
            for y in range(3)
        ]).arrange(DOWN, buff = MED_LARGE_BUFF)
        exchanges = VGroup(*it.chain(*exchanges))
        self.add(exchanges)
        start_times = list(np.linspace(0, 2, len(exchanges)))
        random.shuffle(start_times)
        for exchange, start_time in zip(exchanges, start_times):
            left = random.choice(cryptocurrencies).copy()
            right = random.choice(currencies).copy()
            left.move_to(exchange.get_left())
            right.move_to(exchange.get_right())

            exchange.left = left
            exchange.right = right
            exchange.start_time = start_time
            exchange.add(left, right)
            exchange.currencies = currencies
            exchange.cryptocurrencies = cryptocurrencies
            exchange.animation = Exchange(exchange)

        times = np.arange(0, self.run_time, self.frame_duration)
        from scene.scene import ProgressDisplay
        for t in ProgressDisplay(times):
            for exchange in exchanges:
                sub_t = t - exchange.start_time
                if sub_t < 0:
                    continue
                elif sub_t > 3:
                    exchange.start_time = t
                    sub_t = 0
                    exchange.animation = Exchange(exchange)
                exchange.animation.update(sub_t/3.0)
            self.update_frame(
                self.extract_mobject_family_members(exchanges)
            )
            self.add_frames(self.get_frame())

    def get_cryptocurrencies(self):
        return [
            BitcoinLogo(),
            BitcoinLogo(),
            BitcoinLogo(),
            EthereumLogo(),
            LitecoinLogo()
        ]

    def get_currencies(self):
        return [
            TexMobject("\\$").set_color(GREEN),
            TexMobject("\\$").set_color(GREEN),
            TexMobject("\\$").set_color(GREEN),
            SVGMobject(
                file_name = "euro_symbol",
                stroke_width = 0,
                fill_opacity = 1,
                fill_color = BLUE,
            ),
            SVGMobject(
                file_name = "yen_symbol",
                stroke_width = 0,
                fill_opacity = 1,
                fill_color = RED,
            )
        ]

class ShowLDAndOtherCurrencyExchanges(ShowManyExchanges):
    CONFIG = {
        "run_time" : 15,
    }
    def get_cryptocurrencies(self):
        euro = SVGMobject(
            file_name = "euro_symbol",
            stroke_width = 0,
            fill_opacity = 1,
            fill_color = BLUE,
        )
        return [
            TextMobject("LD").set_color(YELLOW),
            TextMobject("LD").set_color(YELLOW),
            euro, euro.copy(),
            SVGMobject(
                file_name = "yen_symbol",
                stroke_width = 0,
                fill_opacity = 1,
                fill_color = RED,
            ),
            BitcoinLogo(),
        ]

    def get_currencies(self):
        return [TexMobject("\\$").set_color(GREEN)]

class CryptoPatreonThanks(PatreonThanks):
    CONFIG = {
        "specific_patrons" : [
            "Ali Yahya",
            "Desmos",
            "Burt Humburg",
            "CrypticSwarm",
            "Juan Benet",
            "Samantha D. Suplee",
            "James Park",
            "Erik Sundell",
            "Yana Chernobilsky",
            "Kaustuv DeBiswas",
            "Kathryn Schmiedicke",
            "Karan Bhargava",
            "Yu Jun",
            "Dave Nicponski",
            "Damion Kistler",
            "Markus Persson",
            "Yoni Nazarathy",
            "Ed Kellett",
            "Joseph John Cox",
            "Dan Buchoff",
            "Luc Ritchie",
            "Andrew Busey",
            "Michael McGuffin",
            "John Haley",
            "Mourits de Beer",
            "Ankalagon",
            "Eric Lavault",
            "Tomohiro Furusawa",
            "Boris Veselinovich",
            "Julian Pulgarin",
            "Jeff Linse",
            "Cooper Jones",
            "Ryan Dahl",
            "Mark Govea",
            "Robert Teed",
            "Jason Hise",
            "Meshal Alshammari",
            "Bernd Sing",
            "Nils Schneider",
            "James Thornton",
            "Mustafa Mahdi",
            "Mathew Bramson",
            "Jerry Ling",
            "Vecht",
            "Shimin Kuang",
            "Rish Kundalia",
            "Achille Brighton",
            "Ripta Pasay",
        ]
    }

class ProtocolLabs(PiCreatureScene):
    def construct(self):
        morty = self.pi_creature
        logo = self.get_logo()
        logo.next_to(morty, UP)
        logo.shift_onto_screen()
        screen_rect = ScreenRectangle()
        screen_rect.set_height(5)
        screen_rect.to_edge(LEFT)

        self.play(
            DrawBorderThenFill(logo[0]),
            LaggedStartMap(FadeIn, logo[1]),
            morty.change, "raise_right_hand",
        )
        self.wait()
        self.play(
            logo.scale, 0.5,
            logo.to_corner, UP+LEFT,
            ShowCreation(screen_rect)
        )
        modes = ["pondering", "happy", "happy"]
        for mode in modes:
            for x in range(2):
                self.play(Blink(morty))
                self.wait(3)
            self.play(morty.change, mode, screen_rect)

    def get_logo(self):
        logo = SVGMobject(
            file_name = "protocol_labs_logo",
            height = 1.5,
            fill_color = WHITE,
        )
        name = SVGMobject(
            file_name = "protocol_labs_name",
            height = 0.5*logo.get_height(),
            fill_color = LIGHT_GREY,
        )
        for mob in logo, name:
            for submob in mob:
                submob.is_subpath = False
        name.next_to(logo, RIGHT)
        return VGroup(logo, name)

class Thumbnail(DistributedBlockChainScene):
    CONFIG = {
        "n_blocks" : 4,
    }
    def construct(self):
        title = TextMobject("Crypto", "currencies", arg_separator = "")
        title.scale(2.5)
        title.to_edge(UP)
        title[0].set_color(YELLOW)
        title[0].set_stroke(RED, 2)
        self.add(title)

        # logos = VGroup(
        #     BitcoinLogo(), EthereumLogo(), LitecoinLogo()
        # )
        # for logo in logos:
        #     logo.set_height(1)
        # logos.add(TexMobject("\\dots").scale(2))
        # logos.arrange(RIGHT)
        # logos.next_to(title, RIGHT, LARGE_BUFF)
        # self.add(logos)

        block_chain = self.get_block_chain()
        block_chain.arrows.set_color(RED)
        block_chain.blocks.set_color_by_gradient(BLUE, GREEN)
        block_chain.set_width(FRAME_WIDTH-1)
        block_chain.set_stroke(width = 12)
        self.add(block_chain)



























