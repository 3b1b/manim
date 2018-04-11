from __future__ import absolute_import

import random

from constants import *

from animation.animation import Animation
from animation.composition import LaggedStart
from animation.creation import DrawBorderThenFill
from animation.creation import Write
from animation.creation import FadeIn
from animation.creation import FadeOut
from mobject.svg.tex_mobject import TextMobject
from mobject.types.vectorized_mobject import VGroup
from scene.scene import Scene
from for_3b1b_videos.pi_creature_animations import Blink
from for_3b1b_videos.pi_creature import Mortimer
from for_3b1b_videos.pi_creature import Randolph
from mobject.geometry import DashedLine
from mobject.geometry import Rectangle
from mobject.geometry import Square
from mobject.svg.drawings import PatreonLogo


class OpeningQuote(Scene):
    CONFIG = {
        "quote": [],
        "quote_arg_separator": " ",
        "highlighted_quote_terms": {},
        "author": "",
        "fade_in_kwargs": {
            "submobject_mode": "lagged_start",
            "rate_func": None,
            "lag_factor": 4,
            "run_time": 5,
        },
        "text_size" : "\\Large",
        "use_quotation_marks": True,
        "top_buff" : 1.0,
        "author_buff": 1.0,
    }

    def construct(self):
        self.quote = self.get_quote()
        self.author = self.get_author(self.quote)

        self.play(FadeIn(self.quote, **self.fade_in_kwargs))
        self.wait(2)
        self.play(Write(self.author, run_time = 3))
        self.wait()

    def get_quote(self, max_width=FRAME_WIDTH - 1):
        text_mobject_kwargs = {
            "alignment": "",
            "arg_separator": self.quote_arg_separator,
        }
        if isinstance(self.quote, str):
            if self.use_quotation_marks:
                quote = TextMobject("``%s''" %
                                self.quote.strip(), **text_mobject_kwargs)
            else:
                quote = TextMobject("%s" %
                                self.quote.strip(), **text_mobject_kwargs)
        else:
            if self.use_quotation_marks:
                words = [self.text_size + " ``"] + list(self.quote) + ["''"]
            else:
                words = [self.text_size] + list(self.quote)
            quote = TextMobject(*words, **text_mobject_kwargs)
            # TODO, make less hacky
            if self.quote_arg_separator == " ":
                quote[0].shift(0.2 * RIGHT)
                quote[-1].shift(0.2 * LEFT)
        for term, color in self.highlighted_quote_terms:
            quote.set_color_by_tex(term, color)
        quote.to_edge(UP, buff = self.top_buff)
        if quote.get_width() > max_width:
            quote.scale_to_fit_width(max_width)
        return quote

    def get_author(self, quote):
        author = TextMobject(self.text_size + " --" + self.author)
        author.next_to(quote, DOWN, buff = self.author_buff)
        author.set_color(YELLOW)
        return author


class PatreonThanks(Scene):
    CONFIG = {
        "specific_patrons": [],
        "max_patron_group_size": 20,
        "patron_scale_val": 0.8,
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
        indices = (len(patrons) * proportion_range).astype('int')
        patron_groups = [
            VGroup(*patrons[i:j])
            for i, j in zip(indices, indices[1:])
        ]

        for i, group in enumerate(patron_groups):
            left_group = VGroup(*group[:len(group) / 2])
            right_group = VGroup(*group[len(group) / 2:])
            for subgroup, vect in (left_group, LEFT), (right_group, RIGHT):
                subgroup.arrange_submobjects(DOWN, aligned_edge=LEFT)
                subgroup.scale(self.patron_scale_val)
                subgroup.to_edge(vect)

        last_group = None
        for i, group in enumerate(patron_groups):
            anims = []
            if last_group is not None:
                self.play(
                    FadeOut(last_group),
                    morty.look, UP + LEFT
                )
            else:
                anims += [
                    DrawBorderThenFill(patreon_logo),
                ]
            self.play(
                LaggedStart(
                    FadeIn, group,
                    run_time=2,
                ),
                morty.change, "gracious", group.get_corner(UP + LEFT),
                *anims
            )
            self.play(morty.look_at, group.get_corner(DOWN + LEFT))
            self.play(morty.look_at, group.get_corner(UP + RIGHT))
            self.play(morty.look_at, group.get_corner(DOWN + RIGHT))
            self.play(Blink(morty))
            last_group = group


class PatreonEndScreen(PatreonThanks):
    CONFIG = {
        "n_patron_columns": 3,
        "max_patron_width": 3,
        "run_time": 20,
        "randomize_order": True,
    }

    def construct(self):
        if self.randomize_order:
            random.shuffle(self.specific_patrons)
        self.add_title()
        self.scroll_through_patrons()

    def add_title(self):
        title = self.title = TextMobject("Clicky Stuffs")
        title.scale(1.5)
        title.to_edge(UP, buff=MED_SMALL_BUFF)

        randy, morty = self.pi_creatures = VGroup(Randolph(), Mortimer())
        for pi, vect in (randy, LEFT), (morty, RIGHT):
            pi.scale_to_fit_height(title.get_height())
            pi.change_mode("thinking")
            pi.look(DOWN)
            pi.next_to(title, vect, buff=MED_LARGE_BUFF)
        self.add_foreground_mobjects(title, randy, morty)

    def scroll_through_patrons(self):
        logo_box = Square(side_length=2.5)
        logo_box.to_corner(DOWN + LEFT, buff=MED_LARGE_BUFF)
        total_width = FRAME_X_RADIUS - logo_box.get_right()[0]

        black_rect = Rectangle(
            fill_color=BLACK,
            fill_opacity=1,
            stroke_width=0,
            width=FRAME_WIDTH,
            height=1.1 * FRAME_Y_RADIUS
        )
        black_rect.to_edge(UP, buff=0)
        line = DashedLine(FRAME_X_RADIUS * LEFT, FRAME_X_RADIUS * RIGHT)
        line.move_to(black_rect, DOWN)
        line.shift(SMALL_BUFF * SMALL_BUFF * DOWN)
        self.add(line)

        patrons = VGroup(*map(TextMobject, self.specific_patrons))
        patrons.scale(self.patron_scale_val)
        for patron in patrons:
            if patron.get_width() > self.max_patron_width:
                patron.scale_to_fit_width(self.max_patron_width)
        columns = VGroup(*[
            VGroup(
                *patrons[i::self.n_patron_columns]
            ).arrange_submobjects(DOWN, buff=MED_SMALL_BUFF)
            for i in range(self.n_patron_columns)
        ])
        columns.arrange_submobjects(
            RIGHT, buff=LARGE_BUFF,
            aligned_edge=UP,
        )
        columns.scale_to_fit_width(total_width - 1)
        columns.next_to(black_rect, DOWN, 3 * LARGE_BUFF)
        columns.to_edge(RIGHT)

        self.play(
            columns.next_to, FRAME_Y_RADIUS * DOWN, UP, LARGE_BUFF,
            columns.to_edge, RIGHT,
            Animation(black_rect),
            rate_func=None,
            run_time=self.run_time,
        )


class ExternallyAnimatedScene(Scene):
    def construct(self):
        raise Exception("Don't actually run this class.")


class TODOStub(Scene):
    CONFIG = {
        "message": ""
    }

    def construct(self):
        self.add(TextMobject("TODO: %s" % self.message))
        self.wait()
