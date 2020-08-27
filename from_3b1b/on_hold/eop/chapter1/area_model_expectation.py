
from manimlib.imports import *
from active_projects.eop.reusable_imports import *


class IllustrateAreaModelExpectation(Scene):

    def construct(self):

        formula = TexMobject("E[X] = \sum_{i=1}^N p_i x_i").move_to(3 * LEFT + UP)
        self.play(Write(formula))


        x_scale = 5.0
        y_scale = 1.0

        probabilities = np.array([1./8, 3./8, 3./8, 1./8])
        prob_strings = ["{1\over 8}","{3\over 8}","{3\over 8}","{1\over 8}"]
        cumulative_probabilities = np.cumsum(probabilities)
        cumulative_probabilities = np.insert(cumulative_probabilities, 0, 0)
        y_values = np.array([0, 1, 2, 3])

        hist = Histogram(probabilities, y_values,
            mode = "widths",
            x_scale = x_scale,
            y_scale = y_scale,
            x_labels = "none"
        )

        flat_hist = Histogram(probabilities, 0 * y_values,
            mode = "widths",
            x_scale = x_scale,
            y_scale = y_scale,
            x_labels = "none"
        )

        self.play(FadeIn(flat_hist))
        self.play(
            ReplacementTransform(flat_hist, hist)
        )

        braces = VGroup()
        p_labels = VGroup()
        # add x labels (braces)
        for (p,string,bar) in zip(probabilities, prob_strings,hist.bars):
            brace = Brace(bar, DOWN, buff = 0.1)
            p_label = TexMobject(string).next_to(brace, DOWN, buff = SMALL_BUFF).scale(0.7)
            group = VGroup(brace, p_label)
            braces.add(brace)
            p_labels.add(p_label)
            
        self.play(
            LaggedStartMap(FadeIn,braces),
            LaggedStartMap(FadeIn, p_labels)
        )



        y_average = np.mean(y_values)
        averaged_y_values = y_average * np.ones(np.shape(y_values))

        averaged_hist = flat_hist = Histogram(probabilities, averaged_y_values,
            mode = "widths",
            x_scale = x_scale,
            y_scale = y_scale,
            x_labels = "none",
            y_labels = "none"
        ).fade(0.2)

        ghost_hist = hist.copy().fade(0.8)
        self.bring_to_back(ghost_hist)

        self.play(Transform(hist, averaged_hist, run_time = 3))
        self.wait()

        average_brace = Brace(averaged_hist, RIGHT, buff = 0.1)
        average_label = TexMobject(str(y_average)).scale(0.7)
        average_label.next_to(average_brace, RIGHT, SMALL_BUFF)
        average_group = VGroup(average_brace, average_label)

        one_brace = Brace(averaged_hist, DOWN, buff = 0.1)
        one_p_label = TexMobject(str(1)).next_to(one_brace, DOWN, buff = SMALL_BUFF).scale(0.7)
        one_group = VGroup(one_brace, one_p_label)

        self.play(
            FadeIn(average_group),
            Transform(braces, one_brace),
            Transform(p_labels, one_p_label),
        )
        
        rect = SurroundingRectangle(formula, buff = 0.5 * MED_LARGE_BUFF)
        self.play(ShowCreation(rect))

