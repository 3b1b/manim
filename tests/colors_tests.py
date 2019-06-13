from manimlib.imports import *

class ColorScene1(Scene):
    def construct(self):
        rectangle=Rectangle(fill_color=RED,stroke_color=RED,fill_opacity=1)
        print(RED)
        self.add(rectangle)