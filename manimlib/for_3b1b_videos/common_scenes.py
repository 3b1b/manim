import random

from manimlib.animation.animation import Animation
from manimlib.animation.composition import Succession
from manimlib.animation.creation import Write
from manimlib.animation.fading import FadeIn
from manimlib.animation.transform import ApplyMethod
from manimlib.constants import *
from manimlib.for_3b1b_videos.pi_creature import Mortimer
from manimlib.for_3b1b_videos.pi_creature import Randolph
from manimlib.mobject.coordinate_systems import NumberPlane
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.geometry import DashedLine
from manimlib.mobject.geometry import Line
from manimlib.mobject.geometry import Rectangle
from manimlib.mobject.geometry import Square
from manimlib.mobject.svg.drawings import Logo
from manimlib.mobject.svg.tex_mobject import TextMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.scene.moving_camera_scene import MovingCameraScene
from manimlib.scene.scene import Scene
from manimlib.utils.rate_functions import linear


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


class PatreonEndScreen(Scene):
    CONFIG = {
        "max_patron_group_size": 20,
        "patron_scale_val": 0.8,
        "n_patron_columns": 4,
        "max_patron_width": 5,
        "randomize_order": False,
        "capitalize": True,
        "name_y_spacing": 0.6,
        "thanks_words": "Funded by viewers, visit 3b1b.co/support to learn more",
        "scroll_time": 20,
    }

    def construct(self):
        # Add title
        title = self.title = TextMobject("Clicky Stuffs")
        title.scale(1.5)
        title.to_edge(UP, buff=MED_SMALL_BUFF)

        pi_creatures = VGroup(Randolph(), Mortimer())
        for pi, vect in zip(pi_creatures, [LEFT, RIGHT]):
            pi.set_height(title.get_height())
            pi.change_mode("thinking")
            pi.look(DOWN)
            pi.next_to(title, vect, buff=MED_LARGE_BUFF)
        self.add(title, pi_creatures)

        # Set the top of the screen
        logo_box = Square(side_length=2.5)
        logo_box.to_corner(DOWN + LEFT, buff=MED_LARGE_BUFF)

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

        # Add thanks
        thanks = TextMobject(self.thanks_words)
        thanks.scale(0.9)
        thanks.next_to(black_rect.get_bottom(), UP, SMALL_BUFF)
        thanks.set_color(YELLOW)
        underline = Line(LEFT, RIGHT)
        underline.match_width(thanks)
        underline.scale(1.1)
        underline.next_to(thanks, DOWN, SMALL_BUFF)
        thanks.add(underline)

        # Build name list
        with open("manimlib/files/patrons.txt", 'r') as fp:
            names = [
                self.modify_patron_name(name.strip())
                for name in fp.readlines()
            ]

        if self.randomize_order:
            random.shuffle(names)
        else:
            names.sort()

        name_labels = VGroup(*map(TextMobject, names))
        name_labels.scale(self.patron_scale_val)
        for label in name_labels:
            if label.get_width() > self.max_patron_width:
                label.set_width(self.max_patron_width)
        columns = VGroup(*[
            VGroup(*name_labels[i::self.n_patron_columns])
            for i in range(self.n_patron_columns)
        ])
        column_x_spacing = 0.5 + max([c.get_width() for c in columns])

        for i, column in enumerate(columns):
            for n, name in enumerate(column):
                name.shift(n * self.name_y_spacing * DOWN)
                name.align_to(ORIGIN, LEFT)
            column.move_to(i * column_x_spacing * RIGHT, UL)
        columns.center()

        max_width = FRAME_WIDTH - 1
        if columns.get_width() > max_width:
            columns.set_width(max_width)
        underline.match_width(columns)
        columns.next_to(underline, DOWN, buff=3)

        # Set movement
        columns.generate_target()
        distance = columns.get_height() + 2
        wait_time = self.scroll_time
        frame = self.camera.frame
        frame_shift = ApplyMethod(
            frame.shift, distance * DOWN,
            run_time=wait_time,
            rate_func=linear,
        )
        blink_anims = []
        blank_mob = Mobject()
        for x in range(wait_time):
            if random.random() < 0.25:
                blink_anims.append(Blink(random.choice(pi_creatures)))
            else:
                blink_anims.append(Animation(blank_mob))
        blinks = Succession(*blink_anims)

        static_group = VGroup(black_rect, line, thanks, pi_creatures, title)
        static_group.fix_in_frame()
        self.add(columns, static_group)
        self.play(frame_shift, blinks)

    def modify_patron_name(self, name):
        modification_map = {
            "RedAgent14": "Brian Shepetofsky",
            "DeathByShrimp": "Henry Bresnahan",
            "akostrikov": "Aleksandr Kostrikov",
            "Jacob Baxter": "Will Fleshman",
            "Sansword Huang": "SansWord@TW",
            "Sunil Nagaraj": "Ubiquity Ventures",
            "Nitu Kitchloo": "Ish Kitchloo",
            "PedroTristão": "Tristan",
            "Nipun Ramakrishnan": "Reducible",
        }
        for n1, n2 in modification_map.items():
            name = name.replace("ā", "\\={a}")
            if name.lower() == n1.lower():
                name = n2
        if self.capitalize:
            name = " ".join(map(
                lambda s: s.capitalize(),
                name.split(" ")
            ))
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
        "message_height": 0.4,
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
        # Background
        plane = NumberPlane(x_range=(0, 14, 0.5), y_range=(0, 8, 0.5))
        plane.axes.set_stroke(BLUE, 1)
        plane.fade(0.5)
        self.add(plane)

        # Pis
        pis = self.get_pis()
        pis.set_height(self.pi_height)
        pis.arrange(RIGHT, aligned_edge=DOWN)
        pis.move_to(self.pi_bottom, DOWN)
        self.pis = pis
        self.add(pis)

        plane.move_to(pis.get_bottom() + SMALL_BUFF * DOWN)

        # Message
        if self.use_date:
            message = self.get_date_message()
        else:
            message = self.get_probabalistic_message()
        message.set_height(self.message_height)
        message.next_to(pis, DOWN)
        message.set_stroke(BLACK, 5, background=True)
        self.add(message)

        # Suppoerter note
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
            "New video every day ",
            "(with probability 0.05)",
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
