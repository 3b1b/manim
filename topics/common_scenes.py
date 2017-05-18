
from helpers import *

from scene.scene import Scene
from animation.simple_animations import Write, DrawBorderThenFill
from animation.transform import FadeIn, FadeOut, ApplyMethod
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
            if self.quote_arg_separator == " ":
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
        "patron_group_size" : 10,
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

        patrons = map(TextMobject, self.specific_patrons)
        num_groups = float(len(patrons)) / self.patron_group_size
        proportion_range = np.linspace(0, 1, num_groups + 1)
        indices = (len(patrons)*proportion_range).astype('int')
        patron_groups = [
            VGroup(*patrons[i:j])
            for i, j in zip(indices, indices[1:])
        ]        

        for i, group in enumerate(patron_groups):
            group.arrange_submobjects(DOWN, aligned_edge = LEFT)
            group.scale(self.patron_scale_val)
            group.to_edge(LEFT if i%2 == 0 else RIGHT)

        self.play(
            morty.change_mode, "gracious",
            DrawBorderThenFill(patreon_logo),
        )
        self.play(Write(special_thanks, run_time = 1))
        print len(patron_groups)
        for i, group in enumerate(patron_groups):
            anims = [
                FadeIn(
                    group, run_time = 2,
                    submobject_mode = "lagged_start",
                    lag_factor = 4,
                ),
                morty.look_at, group.get_top(),
            ]
            if i >= 2:
                anims.append(FadeOut(patron_groups[i-2]))
            self.play(*anims)
            self.play(morty.look_at, group.get_bottom())
            self.play(Blink(morty))



















