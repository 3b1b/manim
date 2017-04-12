
from helpers import *

from scene.scene import Scene
from animation.simple_animations import Write, DrawBorderThenFill
from animation.transform import FadeIn, ApplyMethod
from mobject.vectorized_mobject import VGroup
from mobject.tex_mobject import TexMobject, TextMobject
from topics.characters import Mortimer, Blink
from topics.objects import PatreonLogo


class OpeningQuote(Scene):
    CONFIG = {
        "quote" : [],
        "quote_arg_separator" : " ",
        "highlighted_quote_terms" : {},
        "author" : "",
        "fade_in_kwargs" : {
            "submobject_mode" : "lagged_start",
            "rate_func" : None,
            "lag_factor" : 4,
            "run_time" : 5,
        },
    }
    def construct(self):
        self.quote = self.get_quote()
        self.author = self.get_author(self.quote)

        self.play(FadeIn(self.quote, **self.fade_in_kwargs))
        self.dither(2)
        self.play(Write(self.author, run_time = 3))
        self.dither()

    def get_quote(self, max_width = 2*SPACE_WIDTH-1):
        text_mobject_kwargs = {
            "alignment" : "",
            "arg_separator" : self.quote_arg_separator,
        }
        if isinstance(self.quote, str):
            quote = TextMobject("``%s''"%self.quote.strip(), **text_mobject_kwargs)
        else:
            words = ["``"] + list(self.quote) + ["''"]
            quote = TextMobject(*words, **text_mobject_kwargs)
            ##TODO, make less hacky
            quote[0].shift(0.2*RIGHT)
            quote[-1].shift(0.2*LEFT)
        for term, color in self.highlighted_quote_terms.items():
            quote.highlight_by_tex(term, color)
        quote.to_edge(UP)
        if quote.get_width() > max_width:
            quote.scale_to_fit_width(max_width)
        return quote

    def get_author(self, quote):
        author = TextMobject("-" + self.author)
        author.next_to(quote, DOWN)
        author.highlight(YELLOW)
        return author

class PatreonThanks(Scene):
    CONFIG = {
        "specific_patrons" : [
            "Ali Yahya",
            "Meshal  Alshammari",
            "CrypticSwarm    ",
            "Justin Helps",
            "Ankit Agarwal",
            "Yu  Jun",
            "Shelby  Doolittle",
            "Dave    Nicponski",
            "Damion  Kistler",
            "Juan    Benet",
            "Othman  Alikhan",
            "Markus  Persson",
            "Dan Buchoff",
            "Derek Dai",
            "Joseph  John Cox",
            "Luc Ritchie",
            "Nils Schneider",
            "Mathew Bramson",
            "Guido   Gambardella",
            "Jerry   Ling",
            "Mark    Govea",
            "Vecht",
            "Shimin Kuang",
            "Rish    Kundalia",
            "Achille Brighton",
            "Kirk    Werklund",
            "Ripta   Pasay",
            "Felipe  Diniz",
        ],
        "max_patrons_height" : 2*SPACE_HEIGHT - 1,
        "patron_scale_val" : 0.7,
    }
    def construct(self):
        morty = Mortimer()
        morty.next_to(ORIGIN, DOWN)

        n_patrons = len(self.specific_patrons)
        special_thanks = TextMobject("Special thanks")
        special_thanks.highlight(YELLOW)
        special_thanks.to_edge(UP)

        patreon_logo = PatreonLogo()
        patreon_logo.next_to(morty, UP, buff = MED_LARGE_BUFF)

        left_patrons = VGroup(*map(TextMobject, 
            self.specific_patrons[:n_patrons/2]
        ))
        right_patrons = VGroup(*map(TextMobject, 
            self.specific_patrons[n_patrons/2:]
        ))
        for patrons in left_patrons, right_patrons:
            patrons.arrange_submobjects(
                DOWN, aligned_edge = LEFT,
                buff = 1.5*MED_SMALL_BUFF
            )

        all_patrons = VGroup(left_patrons, right_patrons)
        all_patrons.scale(self.patron_scale_val)
        for patrons, vect in (left_patrons, LEFT), (right_patrons, RIGHT):
            patrons.to_edge(vect, buff = MED_SMALL_BUFF)
            if patrons.get_height() > 2*SPACE_HEIGHT - LARGE_BUFF:
                patrons.to_edge(UP, buff = MED_SMALL_BUFF)

        shift_distance = max(
            0, (all_patrons.get_height() - 2*SPACE_HEIGHT)
        )
        if shift_distance > 0:
            shift_distance += 1
        velocity = shift_distance/9.0
        def get_shift_anim():
            return ApplyMethod(
                all_patrons.shift, velocity*UP,
                rate_func = None
            )

        self.play(
            morty.change_mode, "gracious",
            DrawBorderThenFill(patreon_logo),
        )
        self.play(Write(special_thanks, run_time = 1))
        self.play(
            Write(left_patrons),
            morty.look_at, left_patrons
        )
        self.play(
            Write(right_patrons),
            morty.look_at, right_patrons
        )
        self.play(Blink(morty), get_shift_anim())
        for patrons in left_patrons, right_patrons:
            for index in 0, -1:
                self.play(
                    morty.look_at, patrons[index],
                    get_shift_anim()
                )
                self.play(get_shift_anim())




















