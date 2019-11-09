import random
from manimlib.imports import *
from manimlib.mobject.three_dimensions import Cube, Prism
from manimlib.mobject.types.vectorized_mobject import VMobject
from math import sqrt
import math

class Multiplication_of_2(Scene):
    def construct(self):
        items = VGroup(
            # TextMobject("How the ellipse will arise"),
            # TextMobject("Kepler's 2nd law"),
            # TextMobject("The shape of velocities"),
            TextMobject("$$1\\times1=1$$"),
            TextMobject("$$1\\times2=2$$"),
            TextMobject("$$1\\times3=3$$"),
            TextMobject("$$1\\times4=4$$"),
            TextMobject("$$1\\times5=5$$"),
            TextMobject("$$1\\times6=6$$"),
            TextMobject("$$1\\times7=7$$"),
            TextMobject("$$1\\times8=8$$"),
            TextMobject("$$1\\times9=9$$"),
            TextMobject("$$1\\times10=10$$"),
        )
        items.arrange(
            DOWN*0.3z, buff=LARGE_BUFF, aligned_edge=LEFT
        )
        items.to_edge(LEFT, buff=1.5)
        for item in items:
            item.add(Dot().next_to(item, LEFT))
            item.generate_target()
            item.target.set_fill(GREY, opacity=0.5)

        title = Title("Multiplication of 1")
        scale_factor = 1.2

        self.add(title)
        self.play(LaggedStartMap(
            FadeIn, items,
            run_time=1,
            lag_ratio=0.7,
        ))
        self.wait()
        
        for item in items:
            other_items = VGroup(*[m for m in items if m is not item])
            new_item = item.copy()
            new_item.scale(scale_factor, about_edge=LEFT)
            new_item.set_fill(WHITE, 1)
            self.play(
                Transform(item, new_item),
                *list(map(MoveToTarget, other_items))
            )
            self.wait()
