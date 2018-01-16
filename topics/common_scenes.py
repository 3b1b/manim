
from helpers import *

from scene.scene import Scene
from animation import Animation
from animation.simple_animations import Write, DrawBorderThenFill, LaggedStart
from animation.transform import FadeIn, FadeOut, ApplyMethod
from mobject.vectorized_mobject import VGroup
from mobject.tex_mobject import TexMobject, TextMobject
from topics.characters import Mortimer, Randolph, Blink
from topics.objects import PatreonLogo
from topics.geometry import Square, Rectangle, DashedLine


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
        self.wait(2)
        self.play(Write(self.author, run_time = 3))
        self.wait()

    def get_quote(self, max_width = 2*SPACE_WIDTH-1):
        text_mobject_kwargs = {
            "alignment" : "",
            "arg_separator" : self.quote_arg_separator,
        }
        if isinstance(self.quote, str):
            quote = TextMobject("``%s''"%self.quote.strip(), **text_mobject_kwargs)
        else:
            words = ["\\Large ``"] + list(self.quote) + ["''"]
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
        author = TextMobject("\\Large -" + self.author)
        author.next_to(quote, DOWN)
        author.highlight(YELLOW)
        return author

class PatreonThanks(Scene):
    CONFIG = {
        "specific_patrons" : [],
        "max_patron_group_size" : 20,
        "patron_scale_val" : 0.8,
    }
    def construct(self):
        morty = Mortimer()
        morty.next_to(ORIGIN, DOWN)

        patreon_logo = PatreonLogo()
        patreon_logo.to_edge(UP)

        n_patrons = len(self.specific_patrons)
        patrons = map(TextMobject, self.specific_patrons)
        num_groups = float(len(patrons)) / self.max_patron_group_size
        proportion_range = np.linspace(0, 1, num_groups + 1)
        indices = (len(patrons)*proportion_range).astype('int')
        patron_groups = [
            VGroup(*patrons[i:j])
            for i, j in zip(indices, indices[1:])
        ]        

        for i, group in enumerate(patron_groups):
            left_group = VGroup(*group[:len(group)/2])
            right_group = VGroup(*group[len(group)/2:])
            for subgroup, vect in (left_group, LEFT), (right_group, RIGHT):
                subgroup.arrange_submobjects(DOWN, aligned_edge = LEFT)
                subgroup.scale(self.patron_scale_val)
                subgroup.to_edge(vect)

        last_group = None
        for i, group in enumerate(patron_groups):
            anims = []
            if last_group is not None:
                self.play(
                    FadeOut(last_group),
                    morty.look, UP+LEFT
                )
            else:
                anims += [
                    DrawBorderThenFill(patreon_logo),
                ]
            self.play(
                LaggedStart(
                    FadeIn, group, 
                    run_time = 2,
                ),
                morty.change, "gracious", group.get_corner(UP+LEFT),
                *anims
            )
            self.play(morty.look_at, group.get_corner(DOWN+LEFT))
            self.play(morty.look_at, group.get_corner(UP+RIGHT))
            self.play(morty.look_at, group.get_corner(DOWN+RIGHT))
            self.play(Blink(morty))
            last_group = group

class PatreonEndScreen(PatreonThanks):
    CONFIG = {
        "n_patron_columns" : 3,
        "max_patron_width" : 3,
        "run_time" : 20,
    }
    def construct(self):
        self.add_title()
        self.scroll_through_patrons()

    def add_title(self):
        title = TextMobject("Clicky Stuffs")
        title.scale(1.5)
        title.to_edge(UP, buff = MED_SMALL_BUFF)

        randy, morty = Randolph(), Mortimer()
        for pi, vect in (randy, LEFT), (morty, RIGHT):
            pi.scale_to_fit_height(title.get_height())
            pi.change_mode("thinking")
            pi.look(DOWN)
            pi.next_to(title, vect, buff = MED_LARGE_BUFF)
        self.add_foreground_mobjects(title, randy, morty)


    def scroll_through_patrons(self):
        logo_box = Square(side_length = 2.5)
        logo_box.to_corner(DOWN+LEFT, buff = MED_LARGE_BUFF)
        total_width = SPACE_WIDTH - logo_box.get_right()[0]

        black_rect = Rectangle(
            fill_color = BLACK,
            fill_opacity = 1,
            stroke_width = 0,
            width = 2*SPACE_WIDTH,
            height = 1.1*SPACE_HEIGHT
        )
        black_rect.to_edge(UP, buff = 0)
        line = DashedLine(SPACE_WIDTH*LEFT, SPACE_WIDTH*RIGHT)
        line.move_to(black_rect, DOWN)
        line.shift(SMALL_BUFF*SMALL_BUFF*DOWN)
        self.add(line)

        patrons = VGroup(*map(TextMobject, self.specific_patrons))
        patrons.scale(self.patron_scale_val)
        for patron in patrons:
            if patron.get_width() > self.max_patron_width:
                patron.scale_to_fit_width(self.max_patron_width)
        columns = VGroup(*[
            VGroup(
                *patrons[i::self.n_patron_columns]
            ).arrange_submobjects(DOWN, buff = MED_SMALL_BUFF)
            for i in range(self.n_patron_columns)
        ])
        columns.arrange_submobjects(
            RIGHT, buff = LARGE_BUFF,
            aligned_edge = UP,
        )
        columns.scale_to_fit_width(total_width - 1)
        columns.next_to(black_rect, DOWN, LARGE_BUFF)
        columns.to_edge(RIGHT)

        self.play(
            columns.next_to, SPACE_HEIGHT*DOWN, UP, LARGE_BUFF,
            columns.to_edge, RIGHT, 
            Animation(black_rect),
            rate_func = None,
            run_time = self.run_time,
        )


class ExternallyAnimatedScene(Scene):
    def construct(self):
        raise Exception("Don't actually run this class.")

class TODOStub(Scene):
    CONFIG = {
        "message" : ""
    }
    def construct(self):
        self.add(TextMobject("TODO: %s"%self.message))
        self.wait()















