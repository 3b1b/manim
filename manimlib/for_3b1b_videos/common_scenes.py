import random

from manimlib.animation.composition import LaggedStartMap
from manimlib.animation.creation import DrawBorderThenFill
from manimlib.animation.creation import Write
from manimlib.animation.fading import FadeIn
from manimlib.animation.fading import FadeOut
from manimlib.constants import *
from manimlib.for_3b1b_videos.pi_creature import Mortimer
from manimlib.for_3b1b_videos.pi_creature import Randolph
from manimlib.for_3b1b_videos.pi_creature_animations import Blink
from manimlib.for_3b1b_videos.pi_creature_scene import PiCreatureScene
from manimlib.mobject.geometry import DashedLine
from manimlib.mobject.geometry import Line
from manimlib.mobject.geometry import Rectangle
from manimlib.mobject.geometry import Square
from manimlib.mobject.svg.drawings import Logo
from manimlib.mobject.svg.drawings import PatreonLogo
from manimlib.mobject.svg.tex_mobject import TextMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.mobject_update_utils import always_shift
from manimlib.scene.moving_camera_scene import MovingCameraScene
from manimlib.scene.scene import Scene
from manimlib.utils.rate_functions import linear
from manimlib.utils.space_ops import get_norm
from manimlib.utils.space_ops import normalize


class OpeningQuote(Scene):
    CONFIG = {
        "quote": [],
        "quote_arg_separator": " ",
        "highlighted_quote_terms": {},
        "author": "",
        "fade_in_kwargs": {
            "lag_ratio": 0.5,
            "rate_func": linear,
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

        patrons = list(map(TextMobject, self.specific_patronds))
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
                subgroup.arrange(DOWN, aligned_edge=LEFT)
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
                LaggedStartMap(
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


class PatreonEndScreen(PatreonThanks, PiCreatureScene):
    CONFIG = {
        "n_patron_columns": 3,
        "max_patron_width": 3.5,
        "run_time": 20,
        "randomize_order": True,
        "capitalize": True,
        "name_y_spacing": 0.7,
        "thanks_words": "Funded by the community, with special thanks to:",
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

        # self.add_title()
        self.scroll_through_patrons()

    def create_pi_creatures(self):
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
        return self.pi_creatures

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

        thanks = TextMobject(self.thanks_words)
        thanks.scale(0.9)
        thanks.next_to(black_rect.get_bottom(), UP, SMALL_BUFF)
        thanks.set_color(YELLOW)
        underline = Line(LEFT, RIGHT)
        underline.match_width(thanks)
        underline.scale(1.1)
        underline.next_to(thanks, DOWN, SMALL_BUFF)
        thanks.add(underline)

        changed_patron_names = map(
            self.modify_patron_name,
            self.specific_patrons,
        )
        patrons = VGroup(*map(
            TextMobject,
            changed_patron_names,
        ))
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
        columns.arrange(
            RIGHT, buff=LARGE_BUFF,
            aligned_edge=UP,
        )
        if columns.get_width() > self.max_patron_width:
            columns.set_width(total_width - 1)

        thanks.to_edge(RIGHT, buff=MED_SMALL_BUFF)
        columns.next_to(underline, DOWN, buff=2)

        columns.generate_target()
        columns.target.to_edge(DOWN, buff=2)
        vect = columns.target.get_center() - columns.get_center()
        distance = get_norm(vect)
        wait_time = 20
        always_shift(
            columns,
            direction=normalize(vect),
            rate=(distance / wait_time)
        )

        self.add(columns, black_rect, line, thanks)
        self.wait(wait_time)

    def modify_patron_name(self, name):
        if name == "RedAgent14":
            return "Brian Shepetofsky"
        return name


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
            Write(name, run_time=3),
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


class Banner(Scene):
    CONFIG = {
        "camera_config": {
            "pixel_height": 1440,
            "pixel_width": 2560,
        },
        "pi_height": 1.25,
        "pi_bottom": 0.25 * DOWN,
        "use_date": False,
        "date": "Sunday, February 3rd",
        "message_scale_val": 0.9,
        "add_supporter_note": False,
        "pre_date_text": "Next video on ",
    }

    def __init__(self, **kwargs):
        # Force these dimensions
        self.camera_config = {
            "pixel_height": 1440,
            "pixel_width": 2560,
        }
        Scene.__init__(self, **kwargs)

    def construct(self):
        pis = self.get_pis()
        pis.set_height(self.pi_height)
        pis.arrange(RIGHT, aligned_edge=DOWN)
        pis.move_to(self.pi_bottom, DOWN)
        self.add(pis)

        if self.use_date:
            message = self.get_date_message()
        else:
            message = self.get_probabalistic_message()
        message.scale(self.message_scale_val)
        message.next_to(pis, DOWN)
        self.add(message)

        if self.add_supporter_note:
            note = self.get_supporter_note()
            note.scale(0.5)
            message.shift((MED_SMALL_BUFF - SMALL_BUFF) * UP)
            note.next_to(message, DOWN, SMALL_BUFF)
            self.add(note)

        yellow_parts = [sm for sm in message if sm.get_color() == YELLOW]
        for pi in pis:
            if yellow_parts:
                pi.look_at(yellow_parts[-1])
            else:
                pi.look_at(message)

    def get_pis(self):
        return VGroup(
            Randolph(color=BLUE_E, mode="pondering"),
            Randolph(color=BLUE_D, mode="hooray"),
            Randolph(color=BLUE_C, mode="sassy"),
            Mortimer(color=GREY_BROWN, mode="thinking")
        )

    def get_probabalistic_message(self):
        return TextMobject(
            "New video every", "Sunday",
            "(with probability 0.3)",
            tex_to_color_map={"Sunday": YELLOW},
        )

    def get_date_message(self):
        return TextMobject(
            self.pre_date_text,
            self.date,
            tex_to_color_map={self.date: YELLOW},
        )

    def get_supporter_note(self):
        return TextMobject(
            "(Available to supporters for review now)",
            color="#F96854",
        )
