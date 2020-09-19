Formulas
=================================

.. manim:: Formula1
    :quality: medium
    :save_last_frame:

    class Formula1(Scene):
        def construct(self):
            t = MathTex(r"\int_a^b f'(x) dx = f(b)- f(a)")
            self.add(t)
            self.wait(1)
