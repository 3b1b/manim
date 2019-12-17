from manimlib.imports import *
from active_projects.eop.reusable_imports import *

class Chapter1OpeningQuote(OpeningQuote):
    CONFIG = {
        "fade_in_kwargs": {
            "lag_ratio": 0.5,
            "rate_func": linear,
            "run_time": 10,
        },
        "text_size" : "\\normalsize",
        "use_quotation_marks": False,
        "quote" : [
            "To see a world in a grain of sand\\\\",
            "And a heaven in a wild flower,\\\\",
            "Hold infinity in the palm of your hand\\\\",
            "\phantom{r}And eternity in an hour.\\\\"
        ],
        "quote_arg_separator" : " ",
        "highlighted_quote_terms" : {},
        "author" : "William Blake: \\\\ \emph{Auguries of Innocence}",
    }

class Introduction(TeacherStudentsScene):

    CONFIG = {
        "default_pi_creature_kwargs": {
        "color": MAROON_E,
        "flip_at_start": True,
        },
    }

    def construct(self):
        
        self.wait(5)
        
        self.change_student_modes(
            "confused", "frustrated", "dejected",
            look_at_arg = UP + 2 * RIGHT
        )

        self.wait()

        self.play(
            self.get_teacher().change_mode,"raise_right_hand"
        )
        self.wait()

        self.wait(30)
        # put examples here in video editor


        # # # # # # # # # # # # # # # # # #
        # show examples of the area model #
        # # # # # # # # # # # # # # # # # #