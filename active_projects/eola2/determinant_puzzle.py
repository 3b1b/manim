from big_ol_pile_of_manim_imports import *

class WorkOutNumerically(Scene):
    def construct(self):
        pass


class SuccessiveLinearTransformations(LinearTransformationScene):
    def construct(self):
        self.apply_transposed_matrix([[0, 1], [1, 0]])
        self.apply_transposed_matrix([[1, 1], [0, 1]])
        self.wait()
