from manimlib.imports import *


class RelationToOtherVideos(Scene):
    CONFIG = {
        "camera_config": {
            "background_color": DARK_GREY,
        },
    }

    def construct(self):
        # Show three videos
        videos = self.get_video_thumbnails()
        brace = Brace(videos, UP)
        text = TextMobject("Heat equation")
        text.scale(2)
        text.next_to(brace, UP)

        self.play(
            LaggedStartMap(
                FadeInFrom, videos,
                lambda m: (m, LEFT),
                lag_ratio=0.4,
                run_time=2,
            ),
            GrowFromCenter(brace),
            FadeInFromDown(text),
        )
        self.wait()
        group = Group(text, brace, videos)

        # Show Fourier thinking
        fourier = ImageMobject("Joseph Fourier")
        fourier.set_height(4)
        fourier.to_edge(RIGHT)
        group.generate_target()
        group.target.to_edge(DOWN)
        fourier.align_to(group.target[0], DOWN)
        bubble = ThoughtBubble(
            direction=RIGHT,
            width=3,
            height=2,
            fill_opacity=0.5,
            stroke_color=WHITE,
        )
        bubble[-1].shift(0.25 * DOWN + 0.5 * LEFT)
        bubble[:-1].rotate(20 * DEGREES)
        for mob in bubble[:-1]:
            mob.rotate(-20 * DEGREES)
        bubble.move_tip_to(
            fourier.get_corner(UL) + DOWN
        )
        bubble.to_edge(UP, buff=SMALL_BUFF)

        self.play(
            MoveToTarget(group),
            FadeInFrom(fourier, LEFT)
        )
        self.play(Write(bubble, run_time=1))
        self.wait()

        # Discount first two
        first_two = videos[:2]
        first_two.generate_target()
        first_two.target.scale(0.5)
        first_two.target.to_corner(DL)
        new_brace = Brace(first_two.target, UP)

        self.play(
            # fourier.scale, 0.8,
            fourier.match_x, new_brace,
            fourier.to_edge, UP,
            MoveToTarget(first_two),
            Transform(brace, new_brace),
            text.scale, 0.7,
            text.next_to, new_brace, UP,
            FadeOutAndShift(bubble, LEFT),
        )
        self.play(
            videos[2].scale, 1.7,
            videos[2].to_corner, UR,
        )
        self.wait()

    #
    def get_video_thumbnails(self):
        thumbnails = Group(
            ImageMobject("diffyq_part2_thumbnail"),
            ImageMobject("diffyq_part3_thumbnail"),
            ImageMobject("diffyq_part4_thumbnail"),
        )
        for thumbnail in thumbnails:
            thumbnail.set_height(4)
            thumbnail.add(SurroundingRectangle(
                thumbnail,
                color=WHITE,
                stroke_width=2,
                buff=0
            ))
        thumbnails.arrange(RIGHT, buff=LARGE_BUFF)
        thumbnails.set_width(FRAME_WIDTH - 1)
        return thumbnails


class FourierGainsImmortality(Scene):
    CONFIG = {
        "mathematicians": [
            "Pythagoras",
            "Euclid",
            "Archimedes",
            "Fermat",
            "Newton",
            "Leibniz",
            "Johann_Bernoulli2",
            "Euler",
            "Joseph Fourier",
            "Gauss",
            "Riemann",
            "Cantor",
            "Noether",
            "Ramanujan",
            "Godel",
            "Turing",
        ]
    }

    def construct(self):
        fourier = ImageMobject("Joseph Fourier")
        fourier.set_height(5)
        fourier.to_edge(LEFT)
        name = TextMobject("Joseph Fourier")
        name.next_to(fourier, DOWN)

        immortals = self.get_immortals()
        immortals.remove(immortals.fourier)
        immortals.to_edge(RIGHT)

        self.add(fourier, name)
        self.play(LaggedStartMap(
            FadeIn, immortals,
            lag_ratio=0.1,
            run_time=2,
        ))
        self.play(
            TransformFromCopy(fourier, immortals.fourier)
        )
        self.wait()

    def get_immortals(self):
        images = Group(*[
            ImageMobject(name)
            for name in self.mathematicians
        ])
        for image in images:
            image.set_height(1)
        images.arrange_in_grid(n_rows=4)

        last_row = images[-4:]
        low_center = last_row.get_center()
        last_row.arrange(RIGHT, buff=0.4, center=False)
        last_row.move_to(low_center)

        frame = SurroundingRectangle(images)
        frame.set_color(WHITE)
        title = TextMobject("Immortals of Math")
        title.match_width(frame)
        title.next_to(frame, UP)

        result = Group(title, frame, *images)
        result.set_height(FRAME_HEIGHT - 1)
        result.to_edge(RIGHT)
        for image, name in zip(images, self.mathematicians):
            setattr(
                result,
                name.split(" ")[-1].lower(),
                image,
            )
        return result


class WhichWavesAreAvailable(Scene):
    def construct(self):
        pass
