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

.. manim:: ExampleArrow
    :quality: medium
    :save_last_frame:

    class ExampleArrow(Scene):
        def construct(self):
            dot = Dot(ORIGIN)
            arrow = Arrow(ORIGIN, [2, 2, 0], buff=0)
            numberplane = NumberPlane()
            origin_text = Text('(0, 0)').next_to(dot, DOWN)
            tip_text = Text('(2, 2)').next_to(arrow.get_end(), RIGHT)
            self.add(numberplane, dot, arrow, origin_text, tip_text)

.. manim:: ExampleArrowTips
    :quality: medium
    :save_last_frame:

    from manim.mobject.geometry import ArrowTriangleTip, ArrowSquareTip, ArrowSquareFilledTip,\
                                       ArrowCircleTip, ArrowCircleFilledTip
    class ExampleArrowTips(Scene):
        def construct(self):
            a00 = Arrow(start=[-2, 3, 0], end=[2, 3, 0], color=YELLOW)
            a11 = Arrow(start=[-2, 2, 0], end=[2, 2, 0], tip_shape=ArrowTriangleTip)
            a12 = Arrow(start=[-2, 1, 0], end=[2, 1, 0])
            a21 = Arrow(start=[-2, 0, 0], end=[2, 0, 0], tip_shape=ArrowSquareTip)
            a22 = Arrow([-2, -1, 0], [2, -1, 0], tip_shape=ArrowSquareFilledTip)
            a31 = Arrow([-2, -2, 0], [2, -2, 0], tip_shape=ArrowCircleTip)
            a32 = Arrow([-2, -3, 0], [2, -3, 0], tip_shape=ArrowCircleFilledTip)
            b11 = a11.copy().scale(0.5, scale_tips=True).next_to(a11, RIGHT)
            b12 = a12.copy().scale(0.5, scale_tips=True).next_to(a12, RIGHT)
            b21 = a21.copy().scale(0.5, scale_tips=True).next_to(a21, RIGHT)
            self.add(a00, a11, a12, a21, a22, a31, a32, b11, b12, b21)
