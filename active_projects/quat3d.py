from big_ol_pile_of_manim_imports import *
from active_projects.quaternions import *

W_COLOR = YELLOW
I_COLOR = GREEN
J_COLOR = RED
K_COLOR = BLUE


class QuaternionLabel(VGroup):
    CONFIG = {
        "decimal_config": {}
    }

    def __init__(self, quat, **kwargs):
        VGroup.__init__(self, **kwargs)
        dkwargs = dict(self.decimal_config)
        self.add(DecimalNumber(quat[0], color=W_COLOR, **dkwargs))
        dkwargs["include_sign"] = True
        self.add(
            DecimalNumber(quat[1], color=I_COLOR, **dkwargs),
            TexMobject("i"),
            DecimalNumber(quat[2], color=J_COLOR, **dkwargs),
            TexMobject("j"),
            DecimalNumber(quat[3], color=K_COLOR, **dkwargs),
            TexMobject("k"),
        )
        self.arrange_submobjects(RIGHT, buff=SMALL_BUFF)


# Scenes

class Introduction(QuaternionHistory):
    CONFIG = {
        "names_and_quotes": [
            (
                "Oliver Heaviside",
                """\\Huge ``the quaternion was not only not
                required, but was a positive evil''"""
            ),
            (
                "Lord Kelvin",
                """\\Huge ``Quaternions... though beautifully \\\\ ingenious,
                have been an unmixed evil'' """
            ),
        ]
    }

    def construct(self):
        title_word = TextMobject("Quaternions:")
        title_equation = TexMobject(
            "i^2 = j^2 = k^2 = ijk = -1",
            tex_to_color_map={
                "i": I_COLOR,
                "j": J_COLOR,
                "k": K_COLOR,
            }
        )
        # label = QuaternionLabel([
        #     float(str((TAU * 10**(3 * k)) % 10)[:4])
        #     for k in range(4)
        # ])
        title = VGroup(title_word, title_equation)
        title.arrange_submobjects(RIGHT)
        title.to_edge(UP)

        images_group = self.get_dissenter_images_quotes_and_names()
        images_group.to_edge(DOWN)
        images, quotes, names = images_group
        for pair in images_group:
            pair[1].align_to(pair[0], UP)

        self.play(
            FadeInFromDown(title_word),
            Write(title_equation)
        )
        self.wait()
        self.play(
            LaggedStart(
                FadeInFrom, images,
                lambda m: (m, 3 * DOWN),
                lag_ratio=0.75
            ),
            LaggedStart(FadeInFromLarge, names, lag_ratio=0.75),
            *[
                LaggedStart(
                    FadeIn, VGroup(*it.chain(*quote)),
                    lag_ratio=0.3,
                    run_time=3
                )
                for quote in quotes
            ],
        )
        self.wait(2)
        self.play(
            title.shift, 2 * UP,
            *[
                ApplyMethod(mob.shift, FRAME_WIDTH * vect / 2)
                for pair in images_group
                for mob, vect in zip(pair, [LEFT, RIGHT])
            ],
        )


class WhoCares(TeacherStudentsScene):
    def construct(self):
        quotes = Group(*[
            ImageMobject(
                "CoderQuaternionResponse_{}".format(d),
                height=2
            )
            for d in range(4)
        ])
        logos = Group(*[
            ImageMobject(name, height=0.5)
            for name in [
                "TwitterLogo",
                "HackerNewsLogo",
                "RedditLogo",
                "YouTubeLogo",
            ]
        ])
        for quote, logo in zip(quotes, logos):
            logo.move_to(quote.get_corner(UR))
            quote.add(logo)

        quotes.arrange_submobjects_in_grid()
        quotes.set_height(4)
        quotes.to_corner(UL)

        self.student_says(
            "Um...who cares?",
            target_mode="sassy",
            added_anims=[self.teacher.change, "guilty"]
        )
        self.wait(2)
        self.play(
            RemovePiCreatureBubble(self.students[1]),
            self.teacher.change, "raise_right_hand"
        )
        self.play(
            LaggedStart(
                FadeInFromDown, quotes,
                run_time=3
            ),
            self.get_student_changes(*3 * ["pondering"], look_at_arg=quotes)
        )
        self.wait(2)

        # Show HN

        # Show Twitter
