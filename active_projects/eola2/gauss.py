from big_ol_pile_of_manim_imports import *


class ShowRowReduction(Scene):
    CONFIG = {
        "matrix": [
            [2, -1, -1],
            [0, 3, -4],
            [-3, 2, 1],
        ]
    }

    def construct(self):
        pass

    def initialize_terms(self):
        # Create Integer mobjects, and arrange in appropriate grid
        pass

    def apply_row_rescaling(self, row_index, scale_factor):
        pass

    def add_row_multiple_to_row(self, row1_index, row2_index, scale_factor):
        pass
