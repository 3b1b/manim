Shapes
=================================

.. manim:: Shape1
    :quality: medium
    :save_last_frame:

    class Shape1(Scene):
        def construct(self):
            d = Dot()
            c = Circle()
            s = Square()
            t = Triangle()
            d.next_to(c, RIGHT)
            s.next_to(c, LEFT)
            t.next_to(c, DOWN)
            self.add(d, c, s, t)
            self.wait(1)
