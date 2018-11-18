

import random
import string

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
from scene.moving_camera_scene import MovingCameraScene
from for_3b1b_videos.pi_creature_animations import Blink
from for_3b1b_videos.pi_creature import Mortimer
from for_3b1b_videos.pi_creature import Randolph
from mobject.geometry import Line
from mobject.geometry import DashedLine
from mobject.geometry import Rectangle
from mobject.geometry import Square
from mobject.svg.drawings import PatreonLogo
from mobject.svg.drawings import Logo


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
        "text_size": "\\Large",
        "use_quotation_marks": True,
        "top_buff": 1.0,
        "author_buff": 1.0,
    }

    def construct(self):
        self.quote = self.get_quote()
        self.author = self.get_author(self.quote)

        self.play(FadeIn(self.quote, **self.fade_in_kwargs))
        self.wait(2)
        self.play(Write(self.author, run_time=3))
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
        quote.to_edge(UP, buff=self.top_buff)
        if quote.get_width() > max_width:
            quote.set_width(max_width)
        return quote

    def get_author(self, quote):
        author = TextMobject(self.text_size + " --" + self.author)
        author.next_to(quote, DOWN, buff=self.author_buff)
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

        patrons = list(map(TextMobject, self.specific_patrons))
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
        "max_patron_width": 3.5,
        "run_time": 20,
        "randomize_order": True,
        "capitalize": True,
        "name_y_spacing": 0.7,
    }

    def construct(self):
        if self.randomize_order:
            random.shuffle(self.specific_patrons)
        if self.capitalize:
            self.specific_patrons = [
                " ".join(map(
                    lambda s: s.capitalize(),
                    patron.split(" ")
                ))
                for patron in self.specific_patrons
            ]

        self.add_title()
        self.scroll_through_patrons()

    def add_title(self):
        title = self.title = TextMobject("Clicky Stuffs")
        title.scale(1.5)
        title.to_edge(UP, buff=MED_SMALL_BUFF)

        randy, morty = self.pi_creatures = VGroup(Randolph(), Mortimer())
        for pi, vect in (randy, LEFT), (morty, RIGHT):
            pi.set_height(title.get_height())
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
            stroke_width=3,
            stroke_color=BLACK,
            width=FRAME_WIDTH,
            height=0.6 * FRAME_HEIGHT,
        )
        black_rect.to_edge(UP, buff=0)
        line = DashedLine(FRAME_X_RADIUS * LEFT, FRAME_X_RADIUS * RIGHT)
        line.move_to(ORIGIN)

        thanks = TextMobject("Funded by the community, with special thanks to:")
        thanks.scale(0.9)
        thanks.next_to(black_rect.get_bottom(), UP, SMALL_BUFF)
        thanks.set_color(YELLOW)
        underline = Line(LEFT, RIGHT)
        underline.set_width(thanks.get_width() + MED_SMALL_BUFF)
        underline.next_to(thanks, DOWN, SMALL_BUFF)
        thanks.add(underline)

        patrons = VGroup(*list(map(TextMobject, self.specific_patrons)))
        patrons.scale(self.patron_scale_val)
        for patron in patrons:
            if patron.get_width() > self.max_patron_width:
                patron.set_width(self.max_patron_width)
        columns = VGroup(*[
            VGroup(*patrons[i::self.n_patron_columns])
            for i in range(self.n_patron_columns)
        ])
        for column in columns:
            for n, name in enumerate(column):
                name.shift(n * self.name_y_spacing * DOWN)
        columns.arrange_submobjects(
            RIGHT, buff=LARGE_BUFF,
            aligned_edge=UP,
        )
        if columns.get_width() > self.max_patron_width:
            columns.set_width(total_width - 1)

        thanks.to_edge(RIGHT)
        columns.next_to(thanks, DOWN, 3 * LARGE_BUFF)

        self.add(columns, black_rect, line, thanks)
        self.play(
            columns.move_to, 2 * DOWN, DOWN,
            columns.align_to, thanks, {"alignment_vect": RIGHT},
            rate_func=None,
            run_time=self.run_time,
        )


class LogoGenerationTemplate(MovingCameraScene):
    def setup(self):
        MovingCameraScene.setup(self)
        frame = self.camera_frame
        frame.shift(DOWN)

        self.logo = Logo()
        name = TextMobject("3Blue1Brown")
        name.scale(2.5)
        name.next_to(self.logo, DOWN, buff=MED_LARGE_BUFF)
        name.set_sheen(-0.2, DR)
        self.channel_name = name

    def construct(self):
        logo = self.logo
        name = self.channel_name

        self.play(
            Write(name, run_time=3, lag_factor=2.5),
            *self.get_logo_animations(logo)
        )
        self.wait()

    def get_logo_animations(self, logo):
        return []  # For subclasses


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
