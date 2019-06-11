from manimlib.imports import *
from active_projects.eop.reusable_imports import *

class ShowUncertaintyDice(Scene):

    def throw_a_die(self, run_time = 0.3):

        eye = np.random.randint(1,7)
        face = self.row_of_dice.submobjects[eye - 1]

        self.play(
            ApplyMethod(face.submobjects[0].set_fill, {"opacity": 1},
                rate_func = there_and_back,
                run_time = run_time,
            ),
        )

    def construct(self):

        self.row_of_dice = RowOfDice(direction = DOWN).scale(0.5)
        self.add(self.row_of_dice)

        for i in range(5):
            self.throw_a_die()
            self.wait(1)

        for i in range(10):
            self.throw_a_die()
            self.wait(0.3)

        for i in range(100):
            self.throw_a_die(0.05)
            self.wait(0.0)



class IdealizedDieHistogram(Scene):

    def construct(self):

        self.probs = 1.0/6 * np.ones(6)
        x_scale = 1.3

        y_labels = ["${1\over 6}$"] * 6

        hist = Histogram(np.ones(6), self.probs, 
            mode = "widths", 
            x_labels = "none",
            y_labels = y_labels,
            y_label_position = "center",
            y_scale = 20,
            x_scale = x_scale,
        )
        hist.rotate(-TAU/4)

        for label in hist.y_labels_group:
            label.rotate(TAU/4)
        hist.remove(hist.y_labels_group)


        self.play(FadeIn(hist))
        self.play(LaggedStartMap(FadeIn, hist.y_labels_group))

