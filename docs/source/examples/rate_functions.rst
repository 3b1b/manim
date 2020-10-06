Rate functions
===============

There are primarily 3 kinds of easing functions
1. Ease In - The animation has a smooth start
2. Ease Out - The animation has a smooth end
3. Ease In Out - The animation has a smooth start as well as smooth end

.. manim:: RateFunctions1Example

    class RateFunctions1Example(Scene):
        def construct(self):
            line1 = Line(3*LEFT, 3*RIGHT).shift(UP).set_color(RED)
            line2 = Line(3*LEFT, 3*RIGHT).set_color(GREEN)
            line3 = Line(3*LEFT, 3*RIGHT).shift(DOWN).set_color(BLUE)

            dot1 = Dot().move_to(line1.get_left())
            dot2 = Dot().move_to(line2.get_left())
            dot3 = Dot().move_to(line3.get_left())

            label1 = Tex("Ease In").next_to(line1, RIGHT)
            label2 = Tex("Ease out").next_to(line2, RIGHT)
            label3 = Tex("Ease In Out").next_to(line3, RIGHT)

            self.play(
                FadeIn(VGroup(line1, line2, line3), 
                FadeIn(VGroup(dot1, dot2, dot3))),
                Write(VGroup(label1, label2, label3)),
            )
            self.play(
                MoveAlongPath(dot1, line1, rate_func=ease_in_sine),
                MoveAlongPath(dot2, line2, rate_func=ease_out_sine),
                MoveAlongPath(dot3, line3, rate_func=ease_in_out_sine),
                run_time=7
            )
            self.wait()