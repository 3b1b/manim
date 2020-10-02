Annotations
=================================

.. manim:: AnnotateBrace
    :save_last_frame:

    class AnnotateBrace(Scene):
        def construct(self):
            dot = Dot([0, 0, 0])
            dot2 = Dot([2, 1, 0])
            line = Line(dot.get_center(), dot2.get_center()).set_color(ORANGE)
            b1 = Brace(line)
            b1text = b1.get_text("Distance")
            b2 = Brace(line, direction=line.copy().rotate(PI / 2).get_unit_vector())
            b2text = b2.get_tex("x-x_1")
            self.add(dot, dot2, line, b1, b2, b1text, b2text)

