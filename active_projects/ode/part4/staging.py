from manimlib.imports import *

from active_projects.ode.part2.fourier_series import FourierOfTrebleClef


class ComplexFourierSeriesExample(FourierOfTrebleClef):
    CONFIG = {
        "file_name": "TrebleClef",
        "run_time": 10,
        # "n_vectors": 10,
        "drawing_height": 5,
        "center_point": DOWN,
        "top_row_vector_y": 3,
        "top_row_x_spacing": 1,
    }

    def construct(self):
        pass

    def get_path(self):
        path = super().get_path()
        path.set_height(self.drawing_height)
        path.to_edge(DOWN)
        return path

    def get_top_row_vector_copies(self, vectors, max_freq=3):
        pass

    def get_top_row_vector_labels(self):
        pass
