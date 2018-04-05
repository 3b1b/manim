from big_ol_pile_of_manim_imports import *
from eop.pascal import *


WIDTH = 6
HEIGHT = 0.25
COLOR_HEADS = YELLOW
COLOR_TAILS = BLUE
NB_ROWS = 28


class AreaSplittingScene(Scene):

    def create_rect_row(self,n):
        rects_group = VGroup()
        for k in range(n+1):
            proportion = float(choose(n,k)) / 2**n
            new_rect = Rectangle(
                width = proportion * WIDTH, 
                height = HEIGHT,
                fill_color = graded_color(n,k),
                fill_opacity = 1
            )
            new_rect.next_to(rects_group,RIGHT,buff = 0)
            rects_group.add(new_rect)
        return rects_group

    def split_rect_row(self,rect_row):

        split_row = VGroup()
        for rect in rect_row.submobjects:
            half = rect.copy().stretch_in_place(0.5,0)
            left_half = half.next_to(rect.get_center(),LEFT,buff = 0)
            right_half = half.copy().next_to(rect.get_center(),RIGHT,buff = 0)
            split_row.add(left_half, right_half)
        return split_row

    def construct(self):

        rect_row = self.create_rect_row(0)
        rect_row.move_to(3.5*UP + 0*HEIGHT*DOWN)
        self.add(rect_row)
        for n in range(NB_ROWS):
            # copy and shift
            new_rect_row = rect_row.copy()
            self.add(new_rect_row)
            self.play(new_rect_row.shift,HEIGHT * DOWN)
            self.wait()

            #split
            split_row = self.split_rect_row(new_rect_row)
            self.play(FadeIn(split_row))
            self.wait()

            # merge
            rect_row = self.create_rect_row(n+1)
            rect_row.move_to(3.5*UP + (n+1)*HEIGHT*DOWN)
            self.play(FadeIn(rect_row))
            self.wait()






