from big_ol_pile_of_manim_imports import *


class NumberlineTransformationScene(Scene):
    CONFIG = {

    }

    def setup(self):
        pass


class ExampleNumberlineTransformationScene(NumberlineTransformationScene):
    def construct(self):
        pass

# Scenes


class WriteOpeningWords(Scene):
    def construct(self):
        raw_string1 = "Dear calculus student,"
        raw_string2 = "You're about to go through your first course. Like " + \
                      "any new topic, it will take some hard work to understand,"
        words1, words2 = [
            TextMobject("\\Large", *rs.split(" "))
            for rs in raw_string1, raw_string2
        ]
        words1.next_to(words2, UP, aligned_edge=LEFT, buff=LARGE_BUFF)
        words = VGroup(*it.chain(words1, words2))
        words.scale_to_fit_width(FRAME_WIDTH - 2 * LARGE_BUFF)
        words.to_edge(UP)

        letter_wait = 0.05
        word_wait = 2 * letter_wait
        comma_wait = 5 * letter_wait
        for word in words:
            self.play(LaggedStart(
                FadeIn, word,
                run_time=len(word) * letter_wait,
                lag_ratio=1.5 / len(word)
            ))
            self.wait(word_wait)
            if word.get_tex_string()[-1] == ",":
                self.wait(comma_wait)


class StartingCalc101(PiCreatureScene):
    CONFIG = {
        # "default_pi_creature_kwargs": {
        #     "color": BLUE,
        #     "flip_at_start": False,
        # },
    }

    def construct(self):
        randy = self.pi_creature
        deriv_string = "\\frac{df}{dx}(x) = \\lim(\\delta x \\to \\infty)" + \
                       "{f(x + \\delta x) - f(x) \\over \\delta x}"
        equations = VGroup(
            TexMobject(*break_up_string_by_terms(deriv_string, "\\delta x"))
        )
        title = TextMobject("Calculus 101")
        title.to_edge(UP)
        h_line = Line(LEFT, RIGHT)
        h_line.scale_to_fit_width(FRAME_WIDTH - LARGE_BUFF)
        h_line.next_to(title, DOWN)

        self.add(title, h_line)
        self.play(randy.change, "erm", title)
        self.wait()


